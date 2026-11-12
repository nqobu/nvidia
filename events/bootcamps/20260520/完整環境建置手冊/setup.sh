#!/usr/bin/env bash
set -euo pipefail

exec > >(tee -a /var/log/nvbootcamp-init.log) 2>&1

BASTION_IP="10.1.1.81"
BASTION_USER="nvbootcamp"
BASTION_PASS="nvbootcamp2026"
REGISTRY="${BASTION_IP}:5000"

VLLM_INTERNAL_IMAGE="${REGISTRY}/vllm/vllm-openai:v0.21.0-ubuntu2404"
VLLM_CLEAN_IMAGE="vllm/vllm-openai:v0.21.0-ubuntu2404"

NEMO_AUTOMODEL_INTERNAL_IMAGE="${REGISTRY}/nvcr.io/nvidia/nemo-automodel:26.04"
NEMO_AUTOMODEL_CLEAN_IMAGE="nvcr.io/nvidia/nemo-automodel:26.04"

NEMOTRON_NIM_INTERNAL_IMAGE="${REGISTRY}/nvcr.io/nim/nvidia/nemotron-3-nano:latest"
NEMOTRON_NIM_CLEAN_IMAGE="nvcr.io/nim/nvidia/nemotron-3-nano:latest"

DATA_MOUNT="/data"
DOCKER_DATA_ROOT="${DATA_MOUNT}/docker"
CONTAINERD_DATA_ROOT="${DATA_MOUNT}/containerd"

MODEL_DIR="${DATA_MOUNT}/models"
CACHE_DIR="${DATA_MOUNT}/.cache"
NIM_CACHE_DIR="${CACHE_DIR}/nim"

MODEL_30B="NVIDIA-Nemotron-3-Nano-30B-A3B-FP8"
MODEL_4B="NVIDIA-Nemotron-3-Nano-4B-BF16"

JITTER_MIN_SECONDS=10
JITTER_MAX_SECONDS=40

RSYNC_BWLIMIT_KB=500000

DEFAULT_USER="$(getent passwd 1000 | cut -d: -f1 || true)"
DEFAULT_HOME="$(getent passwd 1000 | cut -d: -f6 || true)"

if [ -z "${DEFAULT_USER}" ]; then
  DEFAULT_USER="ubuntu"
  DEFAULT_HOME="/home/ubuntu"
fi

export DEBIAN_FRONTEND=noninteractive

echo "[INFO] DEFAULT_USER=${DEFAULT_USER}"
echo "[INFO] DEFAULT_HOME=${DEFAULT_HOME}"

retry() {
  local max_attempts="$1"
  local delay_seconds="$2"
  shift 2

  local attempt=1
  until "$@"; do
    if [ "${attempt}" -ge "${max_attempts}" ]; then
      echo "[ERROR] Command failed after ${attempt} attempts: $*"
      return 1
    fi

    echo "[WARN] Command failed. Retry ${attempt}/${max_attempts} after ${delay_seconds}s: $*"
    sleep "${delay_seconds}"
    attempt=$((attempt + 1))
  done
}

echo "[1/11] Install basic packages"
apt update
apt install -y ca-certificates curl gnupg lsb-release wget rsync sshpass e2fsprogs

echo "[2/11] Detect and mount data disk"

if findmnt -n "${DATA_MOUNT}" >/dev/null 2>&1; then
  echo "[INFO] ${DATA_MOUNT} is already mounted. Skip disk formatting."
else
  ROOT_SRC="$(findmnt -n -o SOURCE / || true)"
  ROOT_PARENT="$(lsblk -no PKNAME "${ROOT_SRC}" 2>/dev/null | head -n1 || true)"

  if [ -n "${ROOT_PARENT}" ]; then
    ROOT_DISK="/dev/${ROOT_PARENT}"
  else
    ROOT_DISK="$(readlink -f "${ROOT_SRC}" || true)"
  fi

  DATA_DISK=""

  while read -r DISK TYPE; do
    if [ "${TYPE}" != "disk" ]; then
      continue
    fi

    if [ "$(readlink -f "${DISK}")" = "$(readlink -f "${ROOT_DISK}")" ]; then
      continue
    fi

    CHILD_COUNT="$(lsblk -nr "${DISK}" | tail -n +2 | wc -l)"
    if [ "${CHILD_COUNT}" -ne 0 ]; then
      echo "[INFO] Skip ${DISK}: has partitions or children"
      continue
    fi

    if blkid "${DISK}" >/dev/null 2>&1; then
      echo "[INFO] Skip ${DISK}: filesystem exists"
      continue
    fi

    if lsblk -nr -o MOUNTPOINT "${DISK}" | grep -q '/'; then
      echo "[INFO] Skip ${DISK}: already mounted"
      continue
    fi

    DATA_DISK="${DISK}"
    break
  done < <(lsblk -dpn -o NAME,TYPE)

  if [ -z "${DATA_DISK}" ]; then
    echo "[ERROR] Cannot find empty data disk. Stop to avoid formatting wrong disk."
    lsblk -f
    exit 1
  fi

  echo "[INFO] DATA_DISK=${DATA_DISK}"
  echo "[INFO] Formatting ${DATA_DISK} as ext4"
  mkfs.ext4 -F "${DATA_DISK}"

  DATA_UUID="$(blkid -s UUID -o value "${DATA_DISK}")"

  mkdir -p "${DATA_MOUNT}"

  if ! grep -q "${DATA_UUID}" /etc/fstab; then
    echo "UUID=${DATA_UUID} ${DATA_MOUNT} ext4 defaults,nofail 0 2" >> /etc/fstab
  fi

  mount -a
fi

mkdir -p "${DOCKER_DATA_ROOT}" "${CONTAINERD_DATA_ROOT}" "${MODEL_DIR}" "${NIM_CACHE_DIR}"
chown -R "${DEFAULT_USER}:${DEFAULT_USER}" "${DATA_MOUNT}"

echo "[INFO] Data disk usage:"
df -h "${DATA_MOUNT}"

echo "[3/11] Install Docker"

install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc

chmod a+r /etc/apt/keyrings/docker.asc

tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now containerd
systemctl enable --now docker

echo "[4/11] Configure Docker data-root and insecure registry"

mkdir -p /etc/docker

tee /etc/docker/daemon.json <<EOF
{
  "data-root": "${DOCKER_DATA_ROOT}",
  "insecure-registries": ["${REGISTRY}"],
  "max-concurrent-downloads": 2
}
EOF

systemctl restart docker

echo "[INFO] Docker root dir:"
docker info | grep "Docker Root Dir" || true

echo "[5/11] Move containerd root to data disk"

systemctl stop docker.socket docker.service containerd.service || true

mkdir -p "${CONTAINERD_DATA_ROOT}"

if mountpoint -q /var/lib/containerd; then
  echo "[INFO] /var/lib/containerd is already a mountpoint."
else
  if [ -d /var/lib/containerd ]; then
    echo "[INFO] Sync existing /var/lib/containerd to ${CONTAINERD_DATA_ROOT}"
    rsync -aHAXS --numeric-ids /var/lib/containerd/ "${CONTAINERD_DATA_ROOT}/" || true

    BACKUP_DIR="/var/lib/containerd.bak.$(date +%F-%H%M%S)"
    echo "[INFO] Move old /var/lib/containerd to ${BACKUP_DIR}"
    mv /var/lib/containerd "${BACKUP_DIR}"
  fi

  mkdir -p /var/lib/containerd
fi

if ! grep -qE "^[^#]+[[:space:]]+/var/lib/containerd[[:space:]]+" /etc/fstab; then
  echo "${CONTAINERD_DATA_ROOT} /var/lib/containerd none bind 0 0" >> /etc/fstab
fi

mount /var/lib/containerd || mount -a

systemctl start containerd
systemctl start docker

echo "[INFO] containerd mount check:"
findmnt /var/lib/containerd || true
df -h /var/lib/containerd || true

echo "[INFO] Docker info after moving containerd:"
docker info | grep -E "Docker Root Dir|Storage Driver|containerd|Image Store" || true

if docker info >/dev/null 2>&1; then
  echo "[INFO] Docker is healthy. Remove old containerd backup from root disk."
  rm -rf /var/lib/containerd.bak.* || true
else
  echo "[WARN] Docker info failed. Keep old containerd backup for safety."
fi

usermod -aG docker "${DEFAULT_USER}" || true

echo "[6/11] Install NVIDIA driver / nvidia-smi"

apt update
apt install -y "linux-headers-$(uname -r)" || apt install -y linux-headers-generic

DISTRO=$(. /etc/os-release; echo ubuntu${VERSION_ID/./})

wget -O /tmp/cuda-keyring_1.1-1_all.deb \
  https://developer.download.nvidia.com/compute/cuda/repos/${DISTRO}/x86_64/cuda-keyring_1.1-1_all.deb

dpkg -i /tmp/cuda-keyring_1.1-1_all.deb
apt update
apt install -y cuda-drivers

echo "[7/11] Install NVIDIA Container Toolkit"

apt-get update
apt-get install -y ca-certificates curl gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

apt-get update
apt-get install -y nvidia-container-toolkit

nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

echo "[INFO] Docker daemon.json after NVIDIA runtime configure:"
cat /etc/docker/daemon.json || true

echo "[INFO] Random sleep before heavy rsync/docker pull"
JITTER_RANGE=$(( JITTER_MAX_SECONDS - JITTER_MIN_SECONDS + 1 ))
SLEEP_SECONDS=$(( JITTER_MIN_SECONDS + RANDOM % JITTER_RANGE ))
echo "[INFO] Sleep ${SLEEP_SECONDS}s to reduce bastion burst traffic"
sleep "${SLEEP_SECONDS}"

echo "[8/11] Rsync models from bastion /data/models to ${MODEL_DIR}"

mkdir -p "${MODEL_DIR}/${MODEL_30B}" "${MODEL_DIR}/${MODEL_4B}"

retry 3 10 sshpass -p "${BASTION_PASS}" rsync -av --delete --bwlimit="${RSYNC_BWLIMIT_KB}" \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  "${BASTION_USER}@${BASTION_IP}:/data/models/${MODEL_30B}/" \
  "${MODEL_DIR}/${MODEL_30B}/"

retry 3 10 sshpass -p "${BASTION_PASS}" rsync -av --delete --bwlimit="${RSYNC_BWLIMIT_KB}" \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  "${BASTION_USER}@${BASTION_IP}:/data/models/${MODEL_4B}/" \
  "${MODEL_DIR}/${MODEL_4B}/"

chown -R "${DEFAULT_USER}:${DEFAULT_USER}" "${MODEL_DIR}"

echo "[9/11] Rsync nim cache from bastion to ${NIM_CACHE_DIR}"

mkdir -p "${NIM_CACHE_DIR}"

retry 3 10 sshpass -p "${BASTION_PASS}" rsync -av --delete --bwlimit="${RSYNC_BWLIMIT_KB}" \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  "${BASTION_USER}@${BASTION_IP}:/home/nvbootcamp/.cache/nim/" \
  "${NIM_CACHE_DIR}/"

chown -R "${DEFAULT_USER}:${DEFAULT_USER}" "${CACHE_DIR}"

echo "[10/11] Create ~/nvidia and ~/.cache symlinks to data disk"

rm -rf "${DEFAULT_HOME}/nvidia"
ln -s "${MODEL_DIR}" "${DEFAULT_HOME}/nvidia"
chown -h "${DEFAULT_USER}:${DEFAULT_USER}" "${DEFAULT_HOME}/nvidia"

rm -rf "${DEFAULT_HOME}/.cache"
ln -s "${CACHE_DIR}" "${DEFAULT_HOME}/.cache"
chown -h "${DEFAULT_USER}:${DEFAULT_USER}" "${DEFAULT_HOME}/.cache"

echo "[11/11] Pull images from internal registry and retag clean names"

echo "[INFO] Pull ${VLLM_INTERNAL_IMAGE}"
retry 3 20 docker pull "${VLLM_INTERNAL_IMAGE}"
docker tag "${VLLM_INTERNAL_IMAGE}" "${VLLM_CLEAN_IMAGE}"
docker rmi "${VLLM_INTERNAL_IMAGE}" || true

echo "[INFO] Pull ${NEMO_AUTOMODEL_INTERNAL_IMAGE}"
retry 3 20 docker pull "${NEMO_AUTOMODEL_INTERNAL_IMAGE}"
docker tag "${NEMO_AUTOMODEL_INTERNAL_IMAGE}" "${NEMO_AUTOMODEL_CLEAN_IMAGE}"
docker rmi "${NEMO_AUTOMODEL_INTERNAL_IMAGE}" || true

echo "[INFO] Pull ${NEMOTRON_NIM_INTERNAL_IMAGE}"
retry 3 20 docker pull "${NEMOTRON_NIM_INTERNAL_IMAGE}"
docker tag "${NEMOTRON_NIM_INTERNAL_IMAGE}" "${NEMOTRON_NIM_CLEAN_IMAGE}"
docker rmi "${NEMOTRON_NIM_INTERNAL_IMAGE}" || true

echo "[INFO] Clean apt cache"
apt-get clean || true
rm -rf /var/lib/apt/lists/* || true

echo "[INFO] Docker images:"
docker image ls || true

echo "[INFO] Disk usage:"
df -h || true
du -sh "${DOCKER_DATA_ROOT}" || true
du -sh "${CONTAINERD_DATA_ROOT}" || true
du -sh /var/lib/containerd || true
du -sh "${MODEL_DIR}" || true
du -sh "${MODEL_DIR}/${MODEL_30B}" || true
du -sh "${MODEL_DIR}/${MODEL_4B}" || true
du -sh "${CACHE_DIR}" || true
du -sh "${NIM_CACHE_DIR}" || true

echo "[INFO] Symlink check:"
ls -la "${DEFAULT_HOME}" | grep -E "nvidia|.cache" || true
ls -la "${DEFAULT_HOME}/nvidia" || true
ls -la "${DEFAULT_HOME}/.cache" || true
ls -la "${DEFAULT_HOME}/.cache/nim" || true

echo "[INFO] Final Docker storage check:"
docker info | grep -E "Docker Root Dir|Storage Driver|containerd|Image Store" || true
findmnt /var/lib/containerd || true
df -h / /data /var/lib/containerd || true

echo "[DONE] Init finished. Rebooting for NVIDIA driver to take effect."
reboot