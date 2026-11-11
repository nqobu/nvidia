# Optional Reuse your new scripts 選做沿用新寫的程式

Copy only one language section into your agent.
請只選擇一種語言的段落貼給代理。

## English

Using the scripts you created, tell me the notebook commands for a second run with
--sample cellpose_demo and --output outputs/cellpose-demo, followed by visualization.
Do not retrain or rewrite the model. After that, optionally use the nuclei sample and
ask whether our intended target is a nucleus or a whole cell. Do not launch these runs
until I execute the notebook cell. Do not judge accuracy without labeled comparisons.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.
## 繁體中文

請使用你剛建立的程式，告訴我在筆記本執行第二張影像推論及後續視覺化的命令。
推論使用 --sample cellpose_demo 與 --output outputs/cellpose-demo。
不要重新訓練或改寫模型。之後可以選做 nuclei，請提醒我思考預期分割的是細胞核還是完整細胞。
請等我執行筆記本儲存格後才啟動這些步驟，不要自行執行，也不要在缺少標註比較時判定準確率。
請以繁體中文回覆。

請在教材根目錄工作，沿用已建立的 uv 虛擬環境，以 `.venv/bin/python` 執行語法檢查
與 `--help`；模型子程序使用 `classroom.json` 已設定的絕對 Python 路徑。
不要建立新環境、執行 `uv venv`、安裝或升級套件，也不要更動 GPU 驅動。
這個 VM 映像已在 `models/` 預放官方權重，請驗證後沿用，不要刪除或強制重新下載有效快取。