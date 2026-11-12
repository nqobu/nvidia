# NVIDIA NIM 部署 Nemotron-3-Nano 完整教學

本教學將帶你一步步使用 **NVIDIA NIM (NVIDIA Inference Microservices)** 在本機部署 `nemotron-3-nano` 大型語言模型，並透過 OpenAI 相容 API 進行推論，最後以 **AIPerf** 進行效能基準測試。

---

## 目錄

1. [環境前置需求](#1-環境前置需求)
2. [啟動 NIM LLM 服務](#2-啟動-nim-llm-服務)
3. [呼叫 API 進行推論](#3-呼叫-api-進行推論)
4. [啟用 Reasoning（推理）模式](#4-啟用-reasoning推理模式)
5. [Model Profiles 設定](#5-model-profiles-設定)
6. [離線部署](#6-離線部署)
7. [使用 AIPerf 進行效能基準測試](#7-使用-aiperf-進行效能基準測試)

---

## 1. 環境前置需求

- 已安裝 **Docker** 並可使用 NVIDIA GPU（需安裝 NVIDIA Container Toolkit）。
- 擁有有效的 **NGC API Key**（可至 [NVIDIA NGC](https://ngc.nvidia.com/) 申請）。
- 至少一張可用的 NVIDIA GPU（依模型 Profile 而定，建議 ≥ 34GB 或 ≥ 63GB VRAM）。

設定 NGC API Key（建議寫入 `~/.bashrc` 以便重複使用）：

```bash
export NGC_API_KEY=<your-ngc-api-key>
```

選擇模型快取目錄（避免每次重啟容器都重新下載權重）：

```bash
# 選擇一個本機路徑，用來快取下載後的模型權重
export LOCAL_NIM_CACHE=~/.cache/nim
mkdir -p "$LOCAL_NIM_CACHE"
```

---

## 2. 啟動 NIM LLM 服務

使用 `docker run` 啟動 NIM 容器，並指定 GPU、共用記憶體、API Key、快取路徑、對外連接埠及模型映像檔。

```bash
docker run -it --rm \
    --gpus device=0 \
    --shm-size=16GB \
    -e NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -p 8000:8000 \
    nvcr.io/nim/nvidia/nemotron-3-nano:latest \
    nim-serve \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder \
    --reasoning-parser nemotron_v3
```

### 參數說明

| 參數 | 說明 |
|------|------|
| `--gpus device=0` | 指定使用第 0 張 GPU |
| `--shm-size=16GB` | 配置 16GB 共用記憶體（避免 OOM） |
| `-e NGC_API_KEY` | 傳入 NGC API Key 環境變數 |
| `-v "$LOCAL_NIM_CACHE:/opt/nim/.cache"` | 將本機快取目錄掛載到容器內 |
| `-p 8000:8000` | 將容器內 8000 埠對應至主機 8000 埠 |
| `--enable-auto-tool-choice` | 啟用自動 Tool Calling 選擇 |
| `--tool-call-parser qwen3_coder` | 指定 Tool Calling 解析器 |
| `--reasoning-parser nemotron_v3` | 指定 Nemotron 推理解析器 |

> 第一次啟動時，NIM 會自動從 NGC 下載模型權重，視網路速度可能需要數分鐘到數十分鐘。看到 `Uvicorn running on http://0.0.0.0:8000` 即代表啟動成功。

---

## 3. 呼叫 API 進行推論

NIM 提供與 **OpenAI 相容** 的 RESTful API，可使用 `curl` 或任何 OpenAI SDK 進行呼叫。

### 3.1 取得模型資訊

```bash
curl -X GET 'http://0.0.0.0:8000/v1/models'
```

回應將列出目前 NIM 載入的模型 ID 與基本資訊。

### 3.2 Completion API（文字接龍）

```bash
curl -X 'POST' \
    'http://0.0.0.0:8000/v1/completions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "model": "nvidia/nemotron-3-nano",
      "prompt": "Once upon a time",
      "max_tokens": 64
    }'
```

### 3.3 Chat Completion API（對話模式）

```bash
curl -X 'POST' \
    'http://0.0.0.0:8000/v1/chat/completions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "model": "nvidia/nemotron-3-nano",
        "messages": [{"role":"user", "content":"Which number is larger, 9.11 or 9.8?"}],
        "max_tokens": 256
    }'
```

---

## 4. 啟用 Reasoning（推理）模式

Nemotron-3-Nano 支援 **思考鏈（Chain-of-Thought）** 推理模式，可在請求中加入 `chat_template_kwargs.enable_thinking` 參數開啟。

```bash
curl -X 'POST' \
    'http://0.0.0.0:8000/v1/chat/completions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "model": "nvidia/nemotron-3-nano",
        "messages": [{"role":"user", "content":"Which number is larger, 9.11 or 9.8?"}],
        "max_tokens": 256,
        "chat_template_kwargs": {
            "enable_thinking": true
        }
    }'
```

啟用後模型會先輸出推理過程（`<think>...</think>`），再給出最終答案，對於數學、邏輯類問題有更佳的表現。

---

## 5. Model Profiles 設定

NIM 會自動偵測硬體並選擇最佳設定，但在以下情境中你可能需要手動選擇 Profile：

- 多 GPU 配置（Tensor Parallel / Pipeline Parallel）
- 特定精度需求（FP8 / BF16 / NVFP4）
- 是否啟用 LoRA 支援

### 5.1 列出所有可用的 Profiles

```bash
docker run --rm \
    --gpus device=0 \
    nvcr.io/nim/nvidia/nemotron-3-nano:latest \
    list-model-profiles
```

### 5.2 預期輸出

```
SYSTEM INFO
- Free GPUs:
  -  [26b5:10de] (0) NVIDIA L40 [current utilization: 1%]
MODEL PROFILES
- Compatible with system and runnable:
  - 8c91cce84b9b032ff4af489cb1a20395e223af35623010df9155390ab2284b7a (vllm-fp8-tp1-pp1-34.0) [requires >=34 GB/gpu]
  - 352d88f8021d0ce396a61d10e929d1d4b45f75038b593595d0d92f80a398a032 (vllm-bf16-tp1-pp1-63.0) [requires >=63 GB/gpu]
  - With LoRA support:
    - c760c1e7b61228a776af1a3c872e61839ac4de1d671c904d304db6d86fd4e754 (vllm-fp8-tp1-pp1-feat_lora-34.0) [requires >=34 GB/gpu]
    - 75ff6ef7a8d2468fe7217ec6c359836f5c8616dadb17850d3a94c324529386b2 (vllm-bf16-tp1-pp1-feat_lora-63.0) [requires >=63 GB/gpu]
- Compatible with system but low memory: <None>
- Compilable to TRT-LLM using just-in-time compilation of HF models to TRTLLM engines: <None>
- Incompatible with system:
    - 65c92a9795f322676e4e02fd12ee5c7298647d10895b135beb412187371a8626 (vllm-fp8-tp8-pp1-8.0) [requires >=8 GB/gpu]
    - 9412ea9de9fdffb496984fc03b83a95f10e8d23cd019253f60283a7beeaf6a15 (vllm-fp8-tp4-pp1-12.0) [requires >=12 GB/gpu]
    ...
```

### Profile 命名規則解析

以 `vllm-bf16-tp1-pp1-63.0` 為例：

| 區段 | 含義 |
|------|------|
| `vllm` | 使用的推論後端 |
| `bf16` | 模型精度（FP8 / BF16 / NVFP4） |
| `tp1` | Tensor Parallel = 1 |
| `pp1` | Pipeline Parallel = 1 |
| `63.0` | 每張 GPU 至少需要的 VRAM（GB） |
| `feat_lora` | 額外支援 LoRA |

### 5.3 指定特定 Profile 啟動

透過 `NIM_MODEL_PROFILE` 環境變數指定 Profile ID：

```bash
docker run -it --rm \
    --gpus device=0 \
    --shm-size=16GB \
    -e NGC_API_KEY \
    -e NIM_MODEL_PROFILE="352d88f8021d0ce396a61d10e929d1d4b45f75038b593595d0d92f80a398a032" \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -p 8000:8000 \
    nvcr.io/nim/nvidia/nemotron-3-nano:latest
```

---

## 6. 離線部署

若目標機器無法連網，可採用「先在有網路機器下載、再複製到離線機器」的方式部署。

### Step 1：在有網路的機器下載模型與映像檔

```bash
# 設定 NGC API Key
export NGC_API_KEY=<your-api-key>

# 設定快取目錄
export NIM_CACHE_PATH=~/.cache/nim
mkdir -p "$NIM_CACHE_PATH"

# 執行下載指令（指定要下載的 Profile）
docker run -it --rm \
    -e NGC_API_KEY \
    -v "$NIM_CACHE_PATH:/opt/nim/.cache" \
    nvcr.io/nim/nvidia/nemotron-3-nano:latest \
    download-to-cache --profile 352d88f8021d0ce396a61d10e929d1d4b45f75038b593595d0d92f80a398a032
```

完成後，將以下兩項打包並轉移至離線機器：

1. 快取目錄：`~/.cache/nim`
2. Docker 映像檔（可用 `docker save -o nemotron-nim.tar nvcr.io/nim/nvidia/nemotron-3-nano:latest` 匯出）

在離線機器使用 `docker load -i nemotron-nim.tar` 匯入映像檔。

### Step 2：在離線機器啟動 NIM

```bash
docker run -it --rm \
    --gpus device=0 \
    --shm-size=16GB \
    -e NIM_MODEL_PROFILE="352d88f8021d0ce396a61d10e929d1d4b45f75038b593595d0d92f80a398a032" \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -p 8000:8000 \
    nvcr.io/nim/nvidia/nemotron-3-nano:latest
```

> 注意：離線啟動不再需要 `NGC_API_KEY`，但 `NIM_MODEL_PROFILE` 必須與下載時一致。

---

## 7. 使用 AIPerf 進行效能基準測試

**AIPerf** 是 NVIDIA 推出的 LLM 推論效能測試工具，能自動產生大量請求並測量延遲（latency）、吞吐量（throughput）、TTFT（Time To First Token）等指標。

### 7.1 安裝 AIPerf

使用 `uv` 管理 Python 環境（速度比 `pip` 快非常多）：

```bash
# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

# 安裝 Python 3.12
uv python install 3.12

# 建立虛擬環境
uv venv aiperf --python 3.12

# 啟動虛擬環境
source aiperf/bin/activate

# 安裝 aiperf
uv pip install aiperf
```

### 7.2 執行效能測試

```bash
aiperf profile \
    --model nvidia/nemotron-3-nano \
    --tokenizer nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
    --url http://0.0.0.0:8000 \
    --endpoint-type chat \
    --concurrency 128 \
    --request-count 384 \
    --streaming \
    --isl 128 \
    --isl-stddev 0 \
    --osl 512 \
    --osl-stddev 0 \
    --extra-inputs "ignore_eos:true" \
    --extra-inputs "min_tokens:512" \
    --random-seed 42 \
    --artifact-dir "/artifacts"
```

### 7.3 重要參數說明

| 參數 | 說明 |
|------|------|
| `--model` | 要測試的模型名稱（需與 NIM 中的模型 ID 一致） |
| `--tokenizer` | 用於計算 token 數的 tokenizer |
| `--url` | NIM 服務的 URL |
| `--endpoint-type chat` | 測試 `/v1/chat/completions` 端點 |
| `--concurrency 128` | 同時併發 128 個請求 |
| `--request-count 384` | 總共送出 384 個請求 |
| `--streaming` | 啟用串流回應，可量測 TTFT |
| `--isl 128` | Input Sequence Length（輸入 token 數）= 128 |
| `--osl 512` | Output Sequence Length（輸出 token 數）= 512 |
| `--isl-stddev / --osl-stddev` | 輸入/輸出長度的標準差（0 表示固定長度） |
| `--extra-inputs "ignore_eos:true"` | 忽略 EOS token，強迫模型輸出滿 `osl` 長度 |
| `--extra-inputs "min_tokens:512"` | 最少輸出 512 個 token |
| `--random-seed 42` | 固定隨機種子，方便重現結果 |
| `--artifact-dir` | 測試報告輸出目錄 |

### 7.4 主要產出指標

- **Throughput（吞吐量）**：每秒處理的請求數 / token 數
- **TTFT（Time To First Token）**：從送出請求到收到第一個 token 的延遲
- **ITL（Inter-Token Latency）**：相鄰 token 之間的延遲
- **Request Latency**：完整請求的端到端延遲

測試完成後，可在 `--artifact-dir` 指定路徑下找到完整的 JSON / CSV 報告。

---

## 附錄：常見問題排查

| 問題 | 可能原因與解法 |
|------|---------------|
| `docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]]` | 未安裝 NVIDIA Container Toolkit |
| `Unauthorized` 或 `403 Forbidden` | `NGC_API_KEY` 未設定或無效 |
| OOM / GPU 記憶體不足 | 改選擇較小 VRAM 需求的 Profile（如 FP8 版本） |
| 第一次啟動非常慢 | 正在下載模型權重，請耐心等候並確認 `LOCAL_NIM_CACHE` 有正確掛載 |
| Reasoning 模式沒有 `<think>` 區塊 | 確認啟動時有加入 `--reasoning-parser nemotron_v3` |

---

## 參考資源

- [NVIDIA NIM 官方文件](https://docs.nvidia.com/nim/)
- [NVIDIA NGC Catalog](https://catalog.ngc.nvidia.com/)
- [AIPerf GitHub](https://github.com/ai-dynamo/aiperf)
