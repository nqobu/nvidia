# Genomics：Parabricks ＋ CodonFM

[00_variant_effect_prediction.ipynb](notebooks/00_variant_effect_prediction.ipynb)從公開 FASTQ 範例開始，經 Parabricks 變異檢測、GENCODE 註釋，再使用 CodonFM 預測變異效應。

## 最短建置路徑：GPU VM 主機

此版本的 Jupyter kernel 執行在 **VM 主機的獨立 Python 環境**；Parabricks 由主機 Docker 啟動。請勿直接把 notebook 放進沒有 Docker 的一般容器後執行。需 [uv](https://docs.astral.sh/uv/getting-started/installation/)、可用的 GPU Docker、`bcftools`、`tabix`／`bgzip`、`samtools`、`wget`；OS 工具由自己的 VM 管理員安裝，例如 Ubuntu 的 `apt install bcftools tabix samtools wget`。

在此 `genomics/` 目錄執行：

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python torch==2.5.1 torchvision==0.20.1 xformers==0.0.28.post3 --index-url https://download.pytorch.org/whl/cu124
uv pip install --python .venv/bin/python -r environment/requirements.txt 'jupyterlab>=4.4,<5'
.venv/bin/python -m ipykernel install --sys-prefix --name genomics --display-name 'Genomics (CodonFM)'
docker pull nvcr.io/nvidia/clara/clara-parabricks:4.6.0-1@sha256:d0761eb4b9921bc046c53520287316d545eb79feaeb8f22387e9bb5734650447
.venv/bin/python -c 'import torch, transformers, polars; assert torch.cuda.is_available(); print(torch.__version__, transformers.__version__)'
.venv/bin/jupyter lab --ip=127.0.0.1 --port=8888
```

選擇 **Genomics (CodonFM)** kernel，從 `notebooks/` 開啟教材。`DATA_DIR` 預設為此課程的 `data/`；如需叢集 scratch，可在啟動 Jupyter 前 `export DATA_DIR=/your/writable/path`。

| 項目 | 版本／來源 |
| --- | --- |
| 推論環境 | Python 3.12、PyTorch 2.5.1／CUDA 12.4、xformers 0.0.28.post3、transformers 4.54.1 |
| Parabricks | `nvcr.io/nvidia/clara/clara-parabricks:4.6.0-1`，固定映像 digest |
| CodonFM 原始碼 | `CodonFM/`：課堂實際使用的 source snapshot，含原始 LICENSE；無模型權重 |
| FASTQ／參考 | `scripts/download_vep_safe.sh`：NVIDIA 公開 Parabricks sample archive |
| 註釋 | notebook 下載 GENCODE Human Release 47 basic annotation |
| 模型 | notebook 從 Hugging Face 的 `nvidia/NV-CodonFM-Encodon-Cdwt-1B-v1` 下載權重與設定 |

資料、映像、模型及 BAM 等輸出會占用大量磁碟；此課堂配置使用約 500 GB 磁碟。開始前確認足夠可用空間。模型若要求接受授權或登入，使用自己的帳號依官方頁面處理。

本副本把教室後台 broker 的單一 cell 改成呼叫 [run_parabricks.sh](scripts/run_parabricks.sh)，執行相同映像與科學參數；完整舊輸出存在時會停止並要求另選輸出路徑，避免誤認新執行。這不是在 notebook 內掛載 Docker socket。

**國網叢集：** 先取得計算節點與 GPU 配置，再請 agent／管理員依站點容器 runtime 改寫上述固定 Parabricks 工作。將 `DATA_DIR` 掛到容器 `/workdir`，保留 `deepvariant_germline` 的 ref、paired FASTQ、VCF、BAM 參數；Python 端保持獨立 Genomics 環境。GPU 裝置須對應排程分配，不能假定主機 GPU 0 可用。Brev 使用 VM Mode 可沿用主機流程。

課堂共用 VM 的 `bootcamp-resources` 不適用自建環境；依平台方式儲存並關閉 kernel。[上游 blueprint](https://github.com/NVIDIA-AI-Blueprints/genomics-analysis)、[Parabricks 文件](https://docs.nvidia.com/clara/parabricks/latest/index.html)、[CodonFM](https://github.com/NVIDIA-Digital-Bio/CodonFM)。
