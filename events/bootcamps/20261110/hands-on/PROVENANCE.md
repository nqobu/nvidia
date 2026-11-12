# 教材來源與公開副本差異

本包整理自 2026-11-10 課堂教材。來源的科學分析流程與輔助程式保留；只在公開副本作環境移植，沒有修改教室裡正在使用的檔案或服務。

## 內容與來源

- BioNeMo：課堂講師教材、`support/workshop.py`、公開結構／配體資料、EGFR MSA、固定參考及配對完整的 prepared 範例。代表性圖檔屬教材範例，並非學員執行紀錄。官方 toolkit 的固定 commit 見 `environment.json`，由使用者另行下載。
- VISTA2D：課堂 notebook、提示卡、API brief、輸出 writer、任務檢查器及小型真實顯微影像。VISTA 原始碼與兩個權重由 `environment/configure.py` 依 `assets.json` 取得；沒有附三個任務的完成解答。
- Single-cell：NVIDIA [single-cell-analysis-blueprint](https://github.com/NVIDIA-AI-Blueprints/single-cell-analysis-blueprint)的課堂使用副本，保留 scverse／作者署名；上游下載日期與原始 notebook 雜湊見 `environment.json`。
- Genomics：NVIDIA [genomics-analysis](https://github.com/NVIDIA-AI-Blueprints/genomics-analysis)的課堂使用副本。`codonfm_helpers.py`、`extract_cds.py`、`gtf_processing.py` 保留原始分析程式；CodonFM 保留課堂 source snapshot 與原始 LICENSE，不另猜測 upstream commit。

## 移植調整

| 檔案 | 本次公開副本調整 |
| --- | --- |
| 全部五份 notebook | 清除 outputs、execution_count 與執行介面的暫存 metadata；保留作者與教材內容。 |
| BioNeMo notebook | code cell 2、4、6、36、38（從 0 起算）的教室資源 CLI 改為條件執行；自建環境顯示 README 指引。其餘 code cell 保留。 |
| BioNeMo support | 三個預設 NIM hostname 改為主機 `127.0.0.1`；原有環境變數覆寫、API payload、快取與單候選提交限制保留。 |
| BioNeMo 設定 | 新增課後專用 Compose、requirements、`.env.example` 與 agent 設定說明；沒有搬入教室登入／proxy／systemd 設定。 |
| VISTA2D | `classroom.json` 先用 `.venv/bin/python` 作可攜提示；執行環境設定後改成該次 Python 的絕對路徑。科學與學習 code cell 均保留。 |
| Genomics notebook | code cell 6 將固定 `/data` 改為可覆寫的本機可寫目錄；cell 20 由 NCHC broker 換成主機 `run_parabricks.sh`。Parabricks 映像、ref、paired FASTQ、VCF、BAM 參數保留。 |
| Agent 指引 | 補充「新環境建置」與「上課分析」階段的區別，並允許使用學員自己的模型供應者。 |

Single-cell 的科學 code cell 沒有改動；Genomics 保留既有課堂修正：安全下載器，以及 Polars join 前的 ID dtype 對齊。教材中的「Workshop VM Only」資源管理段落是歷史課堂說明；課後環境依各課 README 操作。

`classroom-copy-manifest.json` 記錄複製前的來源檔案 SHA256；`SHA256SUMS` 記錄這次完整公開副本。兩者有差異的項目依上表解讀。

## 驗證範圍

發布包檢查涵蓋：五份 notebook 結構及空白輸出、科學 code cell 的來源比對、輔助檔案、Python／shell 語法、Compose 設定、相對連結、檔案雜湊及敏感資料掃描。教材來源曾用於課堂環境；**本次沒有在新的國網／自有主機／Brev 各自重新下載大型資產、build 映像或全程執行五份 notebook**。各平台完成建置後仍需驗證實際 GPU、套件、模型、資料與 notebook 儲存，不能把靜態檢查當成完整重現。

## 授權與出處

保留 notebook 作者、上游版權聲明與 `licenses/` 內的 Blueprint 原始 LICENSE；CodonFM 的 LICENSE 留在其目錄。新增整理說明不替講師教材、影像、模型或資料另行指定授權。顯微影像來源與使用條件見 `vista2d/data/microscopy/README.md`；模型／資料使用各自來源的條件，不因放在同一教材目錄而改變。
