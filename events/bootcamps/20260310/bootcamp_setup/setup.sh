#!/bin/bash
# ============================================================
# PhysicsNeMo Bootcamp — VM 環境一鍵設置腳本
#
# 使用方式（SSH 登入 VM 後執行）：
#   cd ~
#   git clone https://github.com/kevin5826536/physicsnemo_bootcamp_setup.git
#   cd ~/physicsnemo_bootcamp_setup
#   bash setup.sh
#
# 注意事項：
#   - 此 script 為冪等設計，可安全重複執行
#   - 若 NVIDIA Driver 尚未安裝，script 會自動安裝後提示重開機
#     → 重開機後重新 SSH 登入，再次執行 script 即可繼續
# ============================================================

set -euo pipefail

# ── 顏色輸出 ────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
err()   { echo -e "${RED}[✗]${NC} $*"; exit 1; }
step()  { echo -e "\n${CYAN}══ $* ══${NC}"; }

# ── 步驟 1：確認 GPU 可見 ────────────────────────────────────
step "步驟 1：確認 GPU 可見"
lspci | grep -qi nvidia \
    && info "GPU 偵測成功：$(lspci | grep -i nvidia | head -1)" \
    || err  "未偵測到 NVIDIA GPU，請確認 VM 已正確配置 GPU passthrough"

# ── 步驟 2：安裝 NVIDIA Driver（若尚未安裝）────────────────────
step "步驟 2：NVIDIA Driver"
if nvidia-smi &>/dev/null; then
    info "Driver 已安裝：版本 $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
else
    warn "未偵測到 Driver，開始安裝 nvidia-driver-570..."
    sudo apt-get update -y
    sudo apt-get install -y \
        build-essential curl wget git \
        software-properties-common \
        "linux-headers-$(uname -r)"
    sudo apt-get install -y nvidia-driver-570
    echo ""
    warn "Driver 安裝完成，需要重開機！"
    warn "請執行：  sudo reboot"
    warn "重開機並重新 SSH 登入後，再次執行此 script 繼續後續步驟。"
    exit 0
fi

# ── 步驟 3：安裝 Docker Engine ──────────────────────────────
step "步驟 3：Docker Engine"
if command -v docker &>/dev/null; then
    info "Docker 已安裝：$(docker --version)"
else
    warn "安裝 Docker Engine..."
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    sudo apt-get install -y ca-certificates gnupg lsb-release
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
        "deb [arch=$(dpkg --print-architecture) \
        signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker "$USER"
    info "Docker 安裝完成"
fi

# ── 步驟 4：安裝 NVIDIA Container Toolkit ──────────────────
step "步驟 4：NVIDIA Container Toolkit"
if command -v nvidia-ctk &>/dev/null; then
    info "NVIDIA Container Toolkit 已安裝：$(nvidia-ctk --version)"
else
    warn "安裝 NVIDIA Container Toolkit..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
        | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
        | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
        | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    info "NVIDIA Container Toolkit 安裝完成"
fi

# ── 步驟 5：設定 Docker daemon 支援 GPU ────────────────────
step "步驟 5：Docker daemon GPU 設定"
if grep -q '"default-runtime": "nvidia"' /etc/docker/daemon.json 2>/dev/null; then
    info "daemon.json 已設定"
else
    warn "寫入 /etc/docker/daemon.json..."
    sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "/usr/bin/nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF
    sudo systemctl restart docker
    info "Docker daemon 設定完成並重啟"
fi

# ── 步驟 6：建立工作目錄 ────────────────────────────────────
step "步驟 6：工作目錄"
mkdir -p ~/physicsnemo-workshop
info "~/physicsnemo-workshop 已就緒"

# ── 步驟 7：Clone bootcamp 教材 ─────────────────────────────
step "步驟 7：Clone bootcamp 教材"
if [ -d ~/AI-Powered-Physics-Bootcamp ]; then
    info "教材已存在（~/AI-Powered-Physics-Bootcamp），略過 clone"
else
    git clone https://github.com/openhackathons-org/AI-Powered-Physics-Bootcamp.git \
        ~/AI-Powered-Physics-Bootcamp
    info "教材 clone 完成"
fi

# ── 步驟 8：建立 Dockerfile ─────────────────────────────────
step "步驟 8：Dockerfile"
DOCKERFILE=~/physicsnemo-workshop/Dockerfile
if [ -f "$DOCKERFILE" ]; then
    info "Dockerfile 已存在，略過"
else
    warn "建立 Dockerfile..."
    cat > "$DOCKERFILE" << 'DOCKERFILE_EOF'
# ============================================================
# PhysicsNeMo AI-Powered Physics Bootcamp
# Base: nvcr.io/nvidia/physicsnemo/physicsnemo:25.06
#   → NGC 公開 Catalog，docker pull 無需 API Key
#   → 已內含 PhysicsNeMo、PhysicsNeMo-Sym（PINNs）、CUDA 完整環境
# JupyterLab on port 8888
# ============================================================

ARG PHYSICSNEMO_VERSION=25.06
FROM nvcr.io/nvidia/physicsnemo/physicsnemo:${PHYSICSNEMO_VERSION}

# ── 額外系統工具 ──────────────────────────────────────────────
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        wget \
        curl \
        vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Bootcamp 額外 Python 依賴 ─────────────────────────────────
RUN pip install --no-cache-dir \
        gdown \
        ipympl \
        cdsapi \
        jupyterlab>=4.0 \
        ipywidgets \
    && pip install --no-cache-dir --upgrade nbconvert

# ── JupyterLab 設定 ───────────────────────────────────────────
RUN mkdir -p /root/.jupyter && \
    cat > /root/.jupyter/jupyter_lab_config.py << 'EOF'
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.IdentityProvider.token = ''
c.ServerApp.password = ''
c.ServerApp.root_dir = '/workspace/AI-Powered-Physics-Bootcamp'
c.ServerApp.allow_origin = '*'
EOF

# ── Expose ports ─────────────────────────────────────────────
EXPOSE 8888 8889

WORKDIR /workspace

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
DOCKERFILE_EOF
    info "Dockerfile 建立完成"
fi

# ── 步驟 9：建置 Docker Image ───────────────────────────────
step "步驟 9：建置 Docker Image"
if sudo docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "physicsnemo-bootcamp:25.06"; then
    info "Image physicsnemo-bootcamp:25.06 已存在，略過 build"
else
    warn "開始建置（約 10–15 分鐘，主要等待 base image 下載）..."
    sudo docker build -t physicsnemo-bootcamp:25.06 ~/physicsnemo-workshop/
    info "Image 建置完成"
fi

# ── 步驟 10：啟動 JupyterLab ────────────────────────────────
step "步驟 10：啟動 JupyterLab"
if sudo docker ps --format '{{.Names}}' | grep -q "^physicsnemo-bootcamp$"; then
    info "容器已在運行中"
elif sudo docker ps -a --format '{{.Names}}' | grep -q "^physicsnemo-bootcamp$"; then
    warn "重新啟動已存在的容器..."
    sudo docker start physicsnemo-bootcamp
    info "容器已啟動"
else
    warn "啟動容器..."
    sudo docker run -d \
        --name physicsnemo-bootcamp \
        --gpus all \
        --ipc=host \
        --ulimit memlock=-1 \
        --ulimit stack=67108864 \
        -p 8888:8888 \
        -p 8889:8889 \
        -e NVIDIA_VISIBLE_DEVICES=all \
        -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
        -v ~/AI-Powered-Physics-Bootcamp:/workspace/AI-Powered-Physics-Bootcamp \
        physicsnemo-bootcamp:25.06
    info "容器已啟動"
fi

# ── 完成 ────────────────────────────────────────────────────
VM_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          環境設置完成！                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo "  在本機另開一個 Terminal，建立 SSH tunnel："
echo -e "  ${CYAN}ssh -L 8888:localhost:8888 ubuntu@<VM_IP>${NC}"
echo ""
echo "  然後在瀏覽器開啟："
echo -e "  ${CYAN}http://localhost:8888${NC}"
echo ""
