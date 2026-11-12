#!/usr/bin/env bash
# 啟動 NCHC LLM 工作坊環境：以 nemo-automodel:26.04 container 跑 JupyterLab
# 用法：./start_jupyter.sh
# 可選環境變數：
#   PORT      JupyterLab 對外 port（預設 8888）

set -euo pipefail

IMAGE="nvcr.io/nvidia/nemo-automodel:26.04"
CONTAINER="nchc-llm-workshop"
PORT="${PORT:-8888}"
WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


# 移除先前殘留的同名 container
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}\$"; then
    echo "▶ 移除舊 container ${CONTAINER}"
    docker rm -f "$CONTAINER" >/dev/null
fi

echo "▶ 啟動 ${CONTAINER}（mount: ${WORKSPACE} → /workspace, port: ${PORT}）"
docker run -d \
    --name "$CONTAINER" \
    --gpus all --ipc=host \
    --ulimit memlock=-1 --ulimit stack=67108864 \
    -v "$WORKSPACE":/workspace -w /workspace \
    -v "/home/ubuntu/nvidia:/workspace/nvidia" \
    -p "${PORT}:8888" \
    -e HF_HOME=/workspace/.hf_cache \
    "$IMAGE" \
    bash -c '
        set -e
        # 把預設 python3 kernel 改成指向 /opt/venv/bin/python（裡面才有 editable-install 的 nemo_automodel）
        # 這樣 notebook 預設選的 kernel 就直接能 import nemo_automodel，不必手動切換
        cat > /usr/local/share/jupyter/kernels/python3/kernel.json <<JSON
{
 "argv": ["/opt/venv/bin/python", "-Xfrozen_modules=off", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
 "display_name": "Python 3 (ipykernel)",
 "language": "python",
 "metadata": {"debugger": true}
}
JSON
        mkdir -p /workspace/.hf_cache
        exec jupyter lab \
            --ip=0.0.0.0 --port=8888 \
            --no-browser --allow-root \
            --ServerApp.token="" --ServerApp.password="" \
            --ServerApp.root_dir=/workspace
    ' >/dev/null

# 偵測對外可達的 IP（給遠端開瀏覽器用），抓不到時退回 localhost
VM_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
[[ -z "$VM_IP" ]] && VM_IP="localhost"

echo -n "▶ 等待 JupyterLab 起來"
for _ in $(seq 1 60); do
    if curl -fs "http://localhost:${PORT}/lab" >/dev/null 2>&1; then
        echo
        echo "✅ JupyterLab 已就緒：http://<Floating IP>:${PORT}"
        echo
        echo "   停止環境並釋放磁碟：./stop_jupyter.sh"
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo
echo "❌ 等待逾時。請看 logs：docker logs $CONTAINER" >&2
exit 1
