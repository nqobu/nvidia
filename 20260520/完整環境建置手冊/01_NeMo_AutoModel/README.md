# NCHC LLM 工作坊 2026
## 使用 NeMo Automodel + Nemotron-3-Nano-4B 進行預訓練（Pretraining）、SFT 與 LoRA PEFT

---

## 簡介

本工作坊用 NVIDIA NeMo Automodel 這個高階訓練框架，帶你在 **30 分鐘內**走完一個語言模型的完整 fine-tuning pipeline：

1. **接續預訓練（Continued Pretraining）** — 在新領域語料上繼續訓練 base model
2. **監督式微調（Supervised Fine-Tuning, SFT）** — 用問答對教模型遵循特定格式
3. **參數高效微調（LoRA PEFT）** — 凍結 base model、只訓練少量 adapter 權重

兩個 lab 都只跑 **10 個 training step**，目的是讓學員快速理解流程與設定檔，並驗證環境能正確跑起來。實際生產訓練要把 `max_steps` 改大、`local_batch_size` 視 GPU 記憶體調整。

### 學習目標

- 看懂 NeMo Automodel 的 **YAML 設定檔**（dataset / model / optimizer / distributed / loss）
- 能用 **Megatron 二進位前處理**把 raw JSONL 轉成訓練可吃的格式
- 對比 **SFT vs LoRA PEFT** 在更新參數量、checkpoint 大小、記憶體用量上的差異
- 掌握 `nemo-automodel:26.04` 容器在 NVIDIA H100 / H200 上的執行流程

---

## 工作坊概覽

| 實驗 | 任務 | 資料集 | 訓練步數 |
|-----|------|---------|-------|
| Lab 1 | 接續預訓練（Continued Pretraining） | WikiText-103 | 10 |
| Lab 2 | SFT + LoRA PEFT | SQuAD v1.1 | 各 10 |

**模型：** `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16`（4B dense，純文字 LLM）
**框架：** [NeMo Automodel](https://github.com/NVIDIA/nemo-automodel)（版本 0.4.0）
**容器：** `nvcr.io/nvidia/nemo-automodel:26.04`

> Nemotron-3 在 HF Hub 上提供自訂的 `modeling_nemotron_h.py` 與 `configuration_nemotron_h.py`，
> 因此 YAML 與 `from_pretrained` 都需要設定 `trust_remote_code: true`。

---

## 快速開始

工作坊的環境由兩個 script 管理。**全部操作都從 `01_NeMo_AutoModel/` 這個目錄出發**：

```bash
cd 1-Automodel

# 1. 啟動：拉取 image（首次）、啟動 container、開 JupyterLab
./start_jupyter.sh

# 2. 瀏覽器開 script 印出的網址（VM 上會顯示偵測到的 IP；遠端連線時改用對應的浮動/公開 IP）
#    例：http://localhost:8888

# 3. 依序執行 Lab 1、Lab 2

# 4. 跑完後關掉環境（同時釋放磁碟）
./stop_jupyter.sh             # 只移除 container，保留 image 供下次快速啟動
./stop_jupyter.sh --purge     # 連 image 一併移除（釋放約 41 GB）
```

> Nemotron-3-Nano-4B-BF16 是**公開模型**，全程不需要 HuggingFace token。

### `start_jupyter.sh` 做的事

- 拉取 `nvcr.io/nvidia/nemo-automodel:26.04`（如果還沒有）
- 啟動 container：mount 本目錄至 `/workspace`、開 port 8888、設定 `HF_HOME=/workspace/.hf_cache`
- 把預設 `Python 3 (ipykernel)` kernel 改成指向 `/opt/venv/bin/python`，這樣 notebook 預設就能 import `nemo_automodel`
- 啟動 JupyterLab（無密碼、`--ip=0.0.0.0`）
- 偵測 VM IP 並印出連線網址

### `stop_jupyter.sh` 做的事

- 移除 container `nchc-llm-workshop`
- 加上 `--purge` 才會移除 docker image（首次拉取要 20–30 分鐘）

---


## 疑難排解

| 問題 | 解法 |
|---|---|
| `ModuleNotFoundError: No module named 'nemo_automodel'` | 用了非 `start_jupyter.sh` 啟動的環境，或開了舊 container。重跑 `./stop_jupyter.sh && ./start_jupyter.sh` 即可（script 會把預設 kernel 指向 venv python） |
| HuggingFace 匿名速率限制 | 偶發；稍候重跑即可。若仍頻繁，可設定 `HF_TOKEN` 環境變數（非必要） |
| `CUDA out of memory` | 把 YAML 設定檔中的 `local_batch_size` 調降為 `1` |
| `.bin` 檔出現 `FileNotFoundError` | 重新執行 Lab 1 Megatron 前處理那一格 cell |
| `KeyError: '-'` from `configuration_nemotron_h.py` | YAML 缺 `trust_remote_code: true`；Lab 1 預處理 cell 須先跑 sed-patch（notebook 已內建） |
| 第一次執行很慢 | 模型（約 8 GB）會在第一次使用時下載，之後就快了 |
| 想徹底清空磁碟 | Lab 2 最後一個 cell 清 checkpoint 與 HF cache；`./stop_jupyter.sh --purge` 連 image 一起移除 |

---

## 參考資源

- [NeMo Automodel GitHub](https://github.com/NVIDIA/nemo-automodel)
- [NeMo Automodel 官方文件](https://docs.nvidia.com/nemo-automodel)
- [Nemotron-3-Nano-4B-BF16 on HuggingFace](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16)
- [Nemotron 技術報告](https://arxiv.org/abs/2402.16819)（Nemotron 系列模型介紹）
- [LoRA 原始論文](https://arxiv.org/abs/2106.09685)
- [WikiText-103 資料集](https://huggingface.co/datasets/wikitext)
- [SQuAD 資料集](https://huggingface.co/datasets/rajpurkar/squad)

---
