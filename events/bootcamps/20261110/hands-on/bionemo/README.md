# BioNeMo：GenMol → DiffDock → Boltz-2

主要教材：[BioNeMo_with_Agent.md](BioNeMo_with_Agent.md)；程式參考：[BioNeMo_Workflow.ipynb](BioNeMo_Workflow.ipynb)。先完成下列課後環境，再開始提示詞或 notebook。

## 最短建置路徑：GPU VM

在此 `bionemo/` 目錄執行。需要 [uv](https://docs.astral.sh/uv/getting-started/installation/)、Docker、NVIDIA Container Toolkit，以及具有映像與模型存取權的個人 NGC key。國網叢集請由 agent 依排程與站點容器規則轉換此範例。

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
test -f .env || cp .env.example .env
chmod 600 .env
# 在自己的編輯器填入 .env 的 NGC_API_KEY；不要把憑證交給公開對話或 Git。
```

另以 `docker login nvcr.io --username '$oauthtoken'` 登入，在密碼提示私下輸入自己的 NGC key。再執行：

```bash
docker compose up -d
docker compose ps
curl --fail http://127.0.0.1:8001/v1/health/ready
curl --fail http://127.0.0.1:8002/v1/health/ready
curl --fail http://127.0.0.1:8003/v1/health/ready
.venv/bin/jupyter lab --ip=127.0.0.1 --port=8888
```

首次啟動會下載／準備模型，三個 readiness 都成功後才開始。Compose 使用課堂相同的版本與映像 digest，模型快取保存在 volumes；**三模型同時運作的容量以 H200 課堂配置為參考**。較小 GPU 可依工作階段逐一啟停服務，或將請求送往自己有權使用的遠端 NIM。

若 VM 的對外網卡 MTU 小於 1500，請在 `.env` 的 `NIM_NETWORK_MTU` 填入實際值。課堂 VM 是 1442；其他平台先盤點，不要直接套用課堂數值。

| 模型 | 版本 | 預設完整推論 URL |
| --- | --- | --- |
| GenMol | 2.0.0 | `http://127.0.0.1:8001/generate` |
| DiffDock | 2.3.0 | `http://127.0.0.1:8002/molecular-docking/diffdock/generate` |
| Boltz-2 | 1.10.0 | `http://127.0.0.1:8003/biology/mit/boltz2/predict` |

遠端服務請在**啟動 Jupyter／agent 前**設定 `GENMOL_URL`、`DIFFDOCK_URL`、`BOLTZ2_URL`，使用上表格式的完整推論 URL。`support.workshop.ENDPOINTS` 會讀取這些環境變數。此請求範例用於自建、無額外驗證的 NIM；其他 API gateway 的認證與路徑需依其文件調整，不能只替換 hostname。

## Agent 與資料

沿用自己已配置的 agent；[OpenCode 設定與官方 skills](Setup_OpenCode.md)說明課堂使用方式。語言模型服務可使用自己有權存取的國網 Taiwan AI RAP 或其他供應者；與 NIM 的 NGC key 是不同用途。

`data/` 包含公開 PDB／配體、匹配的 EGFR MSA 與固定參考；[data/sources.json](data/sources.json)及 notebook 記錄來源。`prepared/` 是配對完整的教學範例，只有自己選擇 `USE_PREPARED = True` 時才使用。不要將其中分數當成新生成分子的分數。

完成後先儲存及關閉 kernel，再在本目錄用 `docker compose stop` 釋放三模型 GPU。它只針對這份課後 Compose 專案；課堂 VM 的 `bootcamp-resources` 不需要安裝到新環境。

官方：[GenMol](https://docs.nvidia.com/nim/bionemo/genmol/2.0.0/getting-started)、[DiffDock](https://docs.nvidia.com/nim/bionemo/diffdock/2.3.0/getting-started)、[Boltz-2](https://docs.nvidia.com/nim/bionemo/boltz2/1.10.0/getting-started)。
