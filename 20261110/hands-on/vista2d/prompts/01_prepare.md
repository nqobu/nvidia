# Mission 1 Write the model preparation script 任務一撰寫模型準備程式

Copy only one language section into your agent.
請只選擇一種語言的段落貼給代理。

## English

Read WORKSHOP.md, docs/VISTA2D_API.md, and the checkpoints entries in assets.json.
Create prepare_model.py implementing that brief using Python's standard library.
It must download missing checkpoints, verify MD5, reuse valid cached files, preserve
mismatching existing files, support --check-only, and write preparation.json after success.
Do not call a finished workshop helper or copy instructor code. Do not install packages.
Run a syntax check and --help, then stop so I can inspect the code and run it in the notebook.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.

Implement the missing-file download path, but do not download or execute preparation yourself. The notebook will use `prepare_model.py --check-only` to verify the pre-cached weights. Stop after syntax checking and `--help`.
## 繁體中文

請閱讀 WORKSHOP.md、docs/VISTA2D_API.md，以及 assets.json 中的 checkpoints。
依照介面說明，以 Python 標準函式庫建立 prepare_model.py。
程式必須下載缺少的權重、驗證 MD5、沿用有效快取、保留並回報校驗不符的既有檔案，
支援 --check-only，並且只在全部成功後寫入 preparation.json。
不要呼叫已完成的 workshop 工具，不要複製講師解答，也不要安裝套件。
請執行語法檢查與 --help，然後停止，讓我在筆記本檢視新程式並親自執行。
請以繁體中文說明你完成的工作。

請在教材根目錄工作，沿用已建立的 uv 虛擬環境，以 `.venv/bin/python` 執行語法檢查
與 `--help`；模型子程序使用 `classroom.json` 已設定的絕對 Python 路徑。
不要建立新環境、執行 `uv venv`、安裝或升級套件，也不要更動 GPU 驅動。
這個 VM 映像已在 `models/` 預放官方權重，請驗證後沿用，不要刪除或強制重新下載有效快取。

請實作缺漏檔案的下載流程，但不要自行下載或執行模型準備。筆記本會以 `prepare_model.py --check-only` 驗證預放權重。完成語法檢查與 `--help` 後即停止。