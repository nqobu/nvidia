# Single-cell：01 前處理 → 02 轉錄調控活性

使用相同的 RAPIDS 環境，先執行 [01](notebooks/01_scRNA_analysis_preprocessing.ipynb)，再執行 [02](notebooks/02_scRNA_analysis_extended.ipynb)。01 產生的 `notebooks/h5/dli_decoupler.h5ad` 是 02 的輸入；兩份 notebook 請分別開 kernel，一次執行一個。

## 最短建置路徑：GPU VM 容器

在此 `singlecell/` 目錄執行。主機需要支援該 RAPIDS 映像的 NVIDIA 驅動、Docker 與 NVIDIA Container Toolkit。

```bash
docker compose up --build
```

從啟動日誌取得**新產生的個人 Jupyter token**，以 SSH tunnel 或平台提供的安全連線開啟。使用容器的 Python 3 kernel。可在自己的容器 Terminal 驗證：

```bash
python -c 'import cupy, rapids_singlecell, scanpy; print(rapids_singlecell.__version__); print(cupy.cuda.runtime.getDeviceCount())'
```

結束後在主機本目錄執行 `docker compose stop`。若平台的對外 MTU 小於 1500，可設定 `COURSE_NETWORK_MTU` 再建立網路，例如已確認為 1442 的環境使用 `COURSE_NETWORK_MTU=1442 docker compose up --build`。

| 項目 | 課堂版本 |
| --- | --- |
| 基礎映像 | `nvcr.io/nvidia/rapidsai/base:26.02-cuda12-py3.12` |
| Python | 3.12 |
| 科學套件 | rapids_singlecell 0.14.1、scanpy 1.12、decoupler 2.1.4、anndata 0.12.10、NumPy 2.2.6 |
| 資料 | 01 內的 `https://exampledata.scverse.org/rapids-singlecell/dli_census.h5ad`；由 notebook 下載、篩選與存檔 |

此資料的載入及分析需要較多 RAM／GPU 記憶體與磁碟；課堂使用 H200。[官方 blueprint](https://build.nvidia.com/nvidia/single-cell-analysis)提供機型容量建議，請依目前資料量選擇；遇到記憶體不足，先確認其他 kernel 已關閉，再請 agent 評估容量，不要偷偷換小資料冒充原分析。`h5/` 不包含在公開包。

國網叢集請 agent 使用同樣 RAPIDS／CUDA 組合，改用站點允許的容器方式並掛載可寫目錄。自有主機及 Brev VM Mode 可使用上述流程。不要把此環境與 Genomics 的 PyTorch 環境合併。

課堂的 `bootcamp-resources` 僅用於當日 VM，課後用自己的 GPU／kernel 管理方式。[上游 notebook](https://github.com/NVIDIA-AI-Blueprints/single-cell-analysis-blueprint)、[RAPIDS-singlecell 安裝文件](https://rapids-singlecell.scverse.org/en/latest/installation.html)。
