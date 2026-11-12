# 課後實作教材

三套課程與 Genomics 延伸教材，共五份 Jupyter notebook，以及 BioNeMo 的 agent 提示詞教材。請下載完整 `hands-on/`，保留資料夾結構，才能載入相鄰的輔助程式與圖片。Notebook 已清除執行輸出；`prepared/` 與代表性圖片是明確標示的講師範例，不是本次執行結果。

| 課程 | 教材 | 環境建置 |
| --- | --- | --- |
| BioNeMo 藥物探索 | [Agent 教材](bionemo/BioNeMo_with_Agent.md)、[Notebook](bionemo/BioNeMo_Workflow.ipynb) | [BioNeMo](bionemo/README.md) |
| MONAI／VISTA2D 細胞影像 | [Notebook](vista2d/notebooks/01_cellular_image_analysis.ipynb) | [VISTA2D](vista2d/README.md) |
| Single-cell | [01 前處理](singlecell/notebooks/01_scRNA_analysis_preprocessing.ipynb)、[02 延伸分析](singlecell/notebooks/02_scRNA_analysis_extended.ipynb) | [Single-cell](singlecell/README.md) |
| Genomics | [00 變異效應預測](genomics/notebooks/00_variant_effect_prediction.ipynb) | [Genomics](genomics/README.md) |

## 選擇計算環境

**建議優先使用國網中心 GPU 資源延續課堂實驗。** 從 [iService 計算資源服務網](https://iservice.nchc.org.tw/)申請或確認可用服務，再依該平台的操作手冊取得 GPU 配額、儲存空間與連線方式。把本資料夾交給自己的 agent，即可依各課程 README 與版本資訊協助建置。

| 環境 | 如何使用這份教材 |
| --- | --- |
| 國網 GPU VM／雲端資源 | 取得 GPU 主機後依各課程 README 建置；需確認容器、儲存及對外下載權限。 |
| 國網計算叢集 | 先取得 GPU 作業配置，再在計算節點執行。依站點規定使用容器及 Jupyter 連線；若採 Apptainer／Singularity，請 agent 轉換 Docker 範例與資料掛載。不要在登入節點執行 GPU 工作。 |
| 自有 GPU 主機 | 使用 Linux x86_64、可用的 NVIDIA 驅動；容器課程另需 Docker 與 NVIDIA Container Toolkit。各課分開建環境。 |
| [Brev](https://brev.nvidia.com/) | 選擇符合課程需求的 GPU **VM Mode**，連線後採相同建置流程；這也讓 Genomics 的主機 Docker 指令可正常工作。[官方環境說明](https://docs.nvidia.com/brev/concepts/environments)。 |

課堂基準是 Ubuntu 22.04、H200、約 500 GB 磁碟；這是已使用的配置，不是所有課程的最低需求。[版本快照](environment.json)記錄各 Python 環境、模型映像與來源。Boltz-2 的官方要求包含至少 48 GB GPU 記憶體；三個 NIM 同時常駐還需要額外容量，不能把單一模型的最低值當成整套需求。[硬體支援表](https://docs.nvidia.com/nim/bionemo/boltz2/1.10.0/support-matrix)。模型、資料與暫存合計可能達數百 GB，請先規劃空間。

GPU 驅動及可用機型以所選映像的官方支援條件為準。課堂觀測版本不代表新平台的安裝要求；在共用叢集由平台管理員提供驅動。

容器若遇到 GitHub／HTTPS 下載逾時，請 agent 比對主機與容器的連線及 MTU；課堂對外 MTU 為 1442。各 Compose 提供 MTU 設定，請依自己平台填入實際值。

遠端 VM 上的 Jupyter 預設只綁定 loopback。依平台文件建立連線；一般 SSH 範例是在筆電執行 `ssh -L 8888:127.0.0.1:8888 USER@GPU_HOST`，再開啟 `http://127.0.0.1:8888` 並使用自己的 Jupyter token。若使用跳板、排程節點或 Brev，採該平台的 tunnel 方式。

## 交給 agent 的建置提示詞

```text
請協助建置此 hands-on 教材的環境。先讀 AGENTS.md、目標課程 README.md
及 environment.json，盤點目前 GPU、磁碟、Python、容器 runtime 與權限。
只建立我選擇的課程，使用獨立環境與教材記錄的版本。
若在國網叢集，沿用站點的 GPU 排程及容器規則，不假定能用 Docker 或 sudo。
依文件下載公開資料及權重；需要個人憑證時讓我在本機私下輸入。
完成套件、CUDA、路徑、權重與 Jupyter 儲存檢查後，列出啟動指令及仍缺的項目。
建置階段先停在可執行教材的狀態，不自動執行整份 notebook 或提交模型推論。
```

先建立一套環境，確認能儲存 notebook，再開始分析。Single-cell 依 **01 → 02** 執行；00 Genomics 使用不同環境。VISTA2D 保留三個腳本生成任務，沒有附講師解答。完成一課後儲存並關閉 kernel，再使用下一課的 GPU 工作。

這份公開包不依賴當日 VM 的 IP、登入 token、NCHC 後台 broker 或私人映像。大型資料、模型權重、API key 與 agent 對話不包含在包內；各課提供取得方式。[來源、移植差異與驗證範圍](PROVENANCE.md)。
