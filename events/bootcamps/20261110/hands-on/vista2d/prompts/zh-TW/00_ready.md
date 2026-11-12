# 環境確認

請閱讀 WORKSHOP.md，回報 classroom.json 裡設定的模型 Python 路徑，
以及已部署的上游推論設定檔是否存在。不要讀取 instructor/checkpoints/ 或已完成的
workshop 包裝程式，不要安裝套件。GPU 檢查由我在筆記本執行。請以繁體中文回覆。

請在教材根目錄工作，沿用已建立的 uv 虛擬環境，以 `.venv/bin/python` 執行語法檢查
與 `--help`；模型子程序使用 `classroom.json` 已設定的絕對 Python 路徑。
不要建立新環境、執行 `uv venv`、安裝或升級套件，也不要更動 GPU 驅動。
這個 VM 映像已在 `models/` 預放官方權重，請驗證後沿用，不要刪除或強制重新下載有效快取。
