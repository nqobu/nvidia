# NCHC LLM 工作坊 2026 — NVIDIA NeMo Agent Toolkit 教學

本工作坊帶你使用 **NVIDIA NeMo Agent Toolkit** 建立 AI agent，
語言模型採用透過 NIM 提供服務的 `nemotron-3-nano-30b-a3b`。

## 什麼是 NeMo Agent Toolkit？

NeMo Agent Toolkit（套件名：`nvidia-nat`，CLI 名：`nat`）是 NVIDIA 開源的
AI agent workflow 建構工具。

| 概念 | 說明 |
|---|---|
| **Function / Tool** | agent 可以呼叫的 Python 函式（如網路搜尋、計算機、自訂邏輯） |
| **LLM** | 做決策的語言模型（這裡用 `nemotron-3-nano-30b-a3b` 透過 NIM 提供） |
| **Workflow / Agent** | 把 LLM 與 tools 串在一起回答問題 |
| **Config YAML** | 描述整個 workflow 的宣告式設定檔 |

---

## 環境設定

### 前置需求

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — 安裝指令：
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Python 3.11 或 3.12（如果系統沒有，uv 會自動下載）

### 1 — 建立環境並安裝套件

```bash
uv sync
```

這一行會讀取 `pyproject.toml`、建立 `.venv/` 並把所有相依套件裝好。

### 2 — 設定 API key

```bash
export NVIDIA_API_KEY=nvapi-xxx   # 換成講師提供的 key
```

把這行加進你的 shell 設定（`~/.bashrc` 或 `~/.zshrc`）就不必每次重打。
或者每個 notebook 的第一個 code cell 也會引導你互動式輸入。

### 3 — 啟動 Jupyter

```bash
uv run jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
```

`uv run` 會在專案的 virtual environment 內執行指令——不必手動切換 kernel。
從 Jupyter 檔案瀏覽器打開教學 notebook 即可。

---

## 教學

| # | Notebook | 涵蓋概念 |
|---|---|---|
| 01 | [tutorial_01_hello_world.ipynb](tutorial_01_hello_world.ipynb) | 最基本的 workflow — LLM + 內建 datetime tool |
| 02 | [tutorial_02_code_agent.ipynb](tutorial_02_code_agent.ipynb) | ReAct pattern — agent 自己寫 Python + sandbox 執行 |
| 03 | [tutorial_03_custom_tool.ipynb](tutorial_03_custom_tool.ipynb) | 用 Python 寫自己的 tool |

請依順序執行——每一個 tutorial 都以前一個為基礎。

---

## 疑難排解

**`nat: command not found`** — 再跑一次 `uv sync`，並用 `uv run jupyter lab` 啟動。

**`NVIDIA_API_KEY` 未設定** — 每個 notebook 第一個 code cell 都會警告你。

**`code_execution` tool 連不上 sandbox** —
Tutorial 02 的 sandbox server 跑在 `http://127.0.0.1:6000`，由 notebook 的 Step 1
自動拉起來。如果連不上：
- 重跑 Step 1 cell（會自動偵測現有 server，沒有才啟動）
- 看 `/tmp/sandbox.log` 找 Flask 的錯誤訊息
- 手動啟動：`python .venv/lib/python3.12/site-packages/nat/tool/code_execution/local_sandbox/local_sandbox_server.py &`

**第一次執行很慢** — Nemotron 模型權重在 NIM 端 cold start 可能耗時；後續執行會快很多。

**datetime tool 顯示錯誤時間** — `local_datetime` tool 會自動處理時區；不需要手動設 `TZ`。
