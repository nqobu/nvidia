# 任務二：撰寫 VISTA2D 執行程式

請閱讀 docs/VISTA2D_API.md 與 vendor/VISTA/vista2d/configs/inference.json。
依照介面說明，建立支援 --sample、--output、--dry-run 的 run_vista.py。
程式需產生衍生的 MONAI 設定，保留原本的前處理、網路、推論器及實例解碼。
只使用已提供的 support.save_mask.SaveInstanceMask 來儲存整數遮罩。
透過 subprocess 執行 classroom.json 指定的模型 Python，保留 inference.log，
而且只在真正推論成功後寫入 run.json。
不要訓練模型、更動上游原始碼、匯入 workshop 包裝程式，或製造假遮罩。
請檢查語法並執行 --help，然後停止，不要啟動 GPU 推論。
我會在筆記本檢視程式，再執行只產生設定的 --dry-run 與真正推論。
請以繁體中文回覆。

請在教材根目錄工作，沿用已建立的 uv 虛擬環境，以 `.venv/bin/python` 執行語法檢查
與 `--help`；模型子程序使用 `classroom.json` 已設定的絕對 Python 路徑。
不要建立新環境、執行 `uv venv`、安裝或升級套件，也不要更動 GPU 驅動。
這個 VM 映像已在 `models/` 預放官方權重，請驗證後沿用，不要刪除或強制重新下載有效快取。

請勿自行執行 `--dry-run` 或真正推論，也不要建立試跑輸出目錄。只檢查語法及 `--help`，由我在筆記本執行 dry-run 與推論。
