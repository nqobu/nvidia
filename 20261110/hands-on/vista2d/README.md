# MONAI／VISTA2D 細胞影像

[教材 notebook](notebooks/01_cellular_image_analysis.ipynb)讓 agent 逐步建立模型準備、推論與視覺化腳本。需 NVIDIA GPU；課堂使用 H200。套件、模型來源與檢查碼均已提供，學習任務的三個腳本刻意不包含在包內。

## 最短建置路徑：GPU VM

使用 [uv](https://docs.astral.sh/uv/getting-started/installation/)，在此 `vista2d/` 目錄執行：

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu124
uv pip install --python .venv/bin/python -r environment/requirements.txt
.venv/bin/python environment/configure.py
.venv/bin/python -c 'import torch, monai; print(monai.__version__); assert torch.cuda.is_available(); print(torch.cuda.get_device_name())'
.venv/bin/jupyter lab --ip=127.0.0.1 --port=8888
```

`configure.py` 只處理環境：取得固定版本 VISTA source、下載及驗證兩個官方權重，再把 `classroom.json` 的模型 Python 設為此次 `.venv` 的絕對路徑。它不執行推論，也不產生三個學習任務的解答。既有正確權重會沿用；既有檔案雜湊不符時會停止並保留原檔。

開啟 notebook 後沿用自己的 agent，依 [WORKSHOP.md](WORKSHOP.md)、[提示卡](prompts/zh-TW/00_ready.md)與 [VISTA2D_API.md](docs/VISTA2D_API.md)完成課程。此時環境已備妥，教材中的「不要重新安裝」與 `--check-only` 規則就適用。

| 項目 | 固定來源／版本 |
| --- | --- |
| 模型程式 | [Project-MONAI/VISTA](https://github.com/Project-MONAI/VISTA)，commit `d4a8fe0dbf5cb4b76c531fccca8e29c1e6f6ee45` |
| 推論環境 | Python 3.11、PyTorch 2.4.0／CUDA 12.4、MONAI 1.4.0、NumPy 1.24.4 |
| 權重與影像 | [assets.json](assets.json)；小型範例影像已附，大型權重由建置時下載 |
| 上游教學 | [MONAI VISTA2D tutorial](https://github.com/Project-MONAI/tutorials/tree/main/vista_2d) |

課堂開頭與結尾提到的 `bootcamp-resources` 僅用於當日共用 VM；課後環境用 `nvidia-smi` 檢查自己的工作，完成後儲存並關閉 kernel。國網叢集先取得 GPU 配置，再依平台規則啟動此環境及 Jupyter；Brev 可選 VM Mode 採相同指令。
