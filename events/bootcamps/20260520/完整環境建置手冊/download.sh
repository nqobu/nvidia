#!/usr/bin/env bash
set -euo pipefail

exec > >(tee -a /var/log/nvbootcamp-init-2.log) 2>&1

BASTION_IP="10.1.1.81"
BASTION_USER="nvbootcamp"
BASTION_PASS="nvbootcamp2026"
REGISTRY="${BASTION_IP}:5000"


DEFAULT_USER="ubuntu"
DEFAULT_HOME="/home/ubuntu"
DATA_MOUNT="/data"
CACHE_DIR="${DATA_MOUNT}/.cache"
NIM_CACHE_DIR="${CACHE_DIR}/nim"

NIM_INTERNAL_IMAGE="${REGISTRY}/nvcr.io/nim/nvidia/nemotron-3-nano:latest"
NIM_CLEAN_IMAGE=nvcr.io/nim/nvidia/nemotron-3-nano:latest

echo "[1/3] Rsync nim cache from bastion to ${NIM_CACHE_DIR}"

mkdir -p "${NIM_CACHE_DIR}"

sshpass -p "${BASTION_PASS}" rsync -avz \
  -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
  "${BASTION_USER}@${BASTION_IP}:/home/nvbootcamp/.cache/nim/" \
  "${NIM_CACHE_DIR}/"

chown -R "${DEFAULT_USER}:${DEFAULT_USER}" "${CACHE_DIR}"

echo "[2/3] Create ~/.cache symlinks to data disk"
rm -rf "${DEFAULT_HOME}/.cache"
ln -s "${CACHE_DIR}" "${DEFAULT_HOME}/.cache"
chown -h "${DEFAULT_USER}:${DEFAULT_USER}" "${DEFAULT_HOME}/.cache"


echo "[3/3] Pull NIM images from internal registry and retag clean names"

docker pull "${NIM_INTERNAL_IMAGE}"
docker tag "${NIM_INTERNAL_IMAGE}" "${NIM_CLEAN_IMAGE}"
docker rmi "${NIM_INTERNAL_IMAGE}" || true