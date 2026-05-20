# NemoClaw 快速上手 Tutorial

> 一份給新手的 NemoClaw demo 指南：從安裝、建立第一個 sandbox agent，到簡單的操作與整合練習。
>
> 官方文件：<https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html>

---

## 1. 什麼是 NemoClaw？

NemoClaw 是 NVIDIA 推出的 CLI 工具（目前為 alpha 階段），用來在 **sandboxed 環境**中部署、管理一個或多個 AI agent。它建立在三層架構之上：

```
┌─────────────────────────┐
│  NemoClaw CLI           │  ← 你在這裡下指令（部署、管理、監控）
│  (Deploy & Manage)      │
├─────────────────────────┤
│  OpenShell              │  ← 建立 sandbox、強制安全策略、路由 inference
│  (Sandbox Runtime)      │
├─────────────────────────┤
│  OpenClaw               │  ← agent 本體（personality、skills、memory、channels）
│  (Inside the Sandbox)   │
└─────────────────────────┘
```

簡單來說：**NemoClaw = OpenClaw agent + OpenShell sandbox + 一條 CLI 把它們串起來**。

---

## 2. 環境需求 (Prerequisites)

| 項目 | 最低需求 | 建議 |
|------|----------|------|
| OS | Linux (Ubuntu 22.04+) / macOS (Apple Silicon) / Windows WSL2 / DGX Spark | Linux |
| CPU | 4 vCPU | 4+ vCPU |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB | 40 GB |
| Node.js | 22.16+ | 22.x LTS |
| npm | 10+ | latest |
| Docker | Engine / Desktop / Colima | Engine 24+ |

**檢查環境**：

```bash
node --version    # 應 >= v22.16
npm --version     # 應 >= 10
docker --version  # 應 >= 24.0
docker ps         # 確認 daemon 在跑
```

---

## 3. 安裝 NemoClaw

一行指令完成安裝（會啟動互動式 onboarding wizard）：

```bash
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash
```

如果要做自動化部署（CI / 不需互動）：

```bash
curl -fsSL https://www.nvidia.com/nemoclaw.sh \
  | NEMOCLAW_NON_INTERACTIVE=1 \
    NEMOCLAW_ACCEPT_THIRD_PARTY_SOFTWARE=1 \
    bash
```

安裝完成後驗證：

```bash
nemoclaw --version
nemoclaw --help
```

---

## 4. 第一次 Onboarding：建立你的 Sandbox Agent

執行 wizard：

```bash
nemoclaw onboard
```

過程中你會被問到：

### 4.1 選擇 Inference Provider

| 選項 | 適合情境 |
|------|----------|
| NVIDIA Endpoints | 用 NVIDIA hosted model（需要 API key） |
| OpenAI | OpenAI 官方 API |
| OpenAI-compatible | 自架 vLLM / LM Studio 等 |
| Anthropic | Claude API |
| Google Gemini | Gemini API |
| Local Ollama | 本機跑 Ollama（DGX Spark 推薦） |
| Model Router | 多 provider 自動路由 |

### 4.2 為 Sandbox 命名

例如：`my-assistant`

### 4.3 選擇額外功能

- **Web search**：讓 agent 可以上網查資料
- **Messaging channels**：Telegram / Discord / Slack
- **Network policy tier**：選擇預設安全等級（strict / moderate / open）

完成後 NemoClaw 會在 sandbox 內建立一個新鮮的 OpenClaw 實例。

---

## 5. 與你的 Agent 互動

### 5.１ 透過 Terminal

連進 sandbox：

```bash
nemoclaw my-assistant connect
```

進去後啟動 OpenClaw 的 TUI 對話介面：

```bash
openclaw tui
```

在 TUI 內直接打字即可。離開：先 `/exit` 離開 chat，再 `exit` 回到 host shell。

> ⚠️ **不要用 `openclaw agent --local`** — 這個 flag 會繞過 sandbox 的 secret scanning / network policy / inference auth，NemoClaw 已經明確阻擋。Sandbox 內一律用 `openclaw tui`（互動）或從 host 端透過 dashboard。

---

## 6. 常用功能 Demo

以下是新手最快可以「玩起來」的幾個功能：

### Demo 1 — 查看 sandbox 狀態

```bash
nemoclaw my-assistant status        # agent 狀態 / uptime / inference provider
```

### Demo 2 — 看 sandbox 內部的檔案

OpenClaw 把它的狀態全部寫成本地檔案，可以直接 `ls` 進去看：

```bash
nemoclaw my-assistant connect
# 進去 sandbox 後：
ls ~/.openclaw/
```

預期看到的主要項目：

| 項目 | 內容 |
|------|------|
| `openclaw.json` | agent 主設定（provider、model、tools 開關等） |
| `agents/` | 已建立的 agent 定義 |
| `skills/` | agent 可用的 skill |
| `memory/` | agent 對話累積出的記憶（**剛建好是空的**，要跟 agent 聊過才會有內容） |
| `logs/` | 歷次對話 / tool call 的紀錄 |
| `credentials/` | 加密儲存的 provider API key |
| `flows/`、`extensions/`、`canvas/` | 進階功能 |

兩個最值得看的：

```bash
# 看 agent 現在連哪個 provider、用哪個 model
cat ~/.openclaw/openclaw.json | head -40

# 看最近一次對話的 log（跟 agent 聊過再來看）
ls ~/.openclaw/logs/
```

### Demo 3 — 看 logs

```bash
nemoclaw my-assistant logs --tail 50
```

### Demo 4 — 清掉 sandbox

```bash
nemoclaw my-assistant destroy
```

---

## 6.5 Mini-demo：用 NemoClaw 做「只能看 public 帳本」的記帳助手

這個 demo 展示 NemoClaw / OpenShell 最重要的安全特性：**sandbox 預設與 host 完全隔離**。我們在 host 上建兩份 CSV（public + private），只把 public 帶進 sandbox，然後從 sandbox 內驗證 private 那份**根本看不到**，最後請 agent 對 public 做分析。

### Step 1 — 在 host 上建兩份假 CSV

```bash
# host shell（不是 sandbox 內）
mkdir -p ~/budget-demo/public ~/budget-demo/private

# Public：可以給 agent 看的日常消費
cat > ~/budget-demo/public/transactions.csv <<'EOF'
date,amount,merchant,category
2026-05-02,-3200,房東,居住
2026-05-03,-185,全聯,生活
2026-05-05,-95,星巴克,餐飲
2026-05-07,-1250,台電,居住
2026-05-09,-420,Uber Eats,餐飲
2026-05-11,-680,家樂福,生活
2026-05-13,-95,星巴克,餐飲
2026-05-15,-260,Spotify,訂閱
2026-05-18,-1480,誠品,購物
2026-05-21,-560,7-11,生活
2026-05-25,-95,星巴克,餐飲
2026-05-28,-340,計程車,通勤
EOF

# Private：薪資、投資、敏感金額 — 不希望 agent 看到
cat > ~/budget-demo/private/salary_and_investments.csv <<'EOF'
date,amount,source,note
2026-05-10,85000,公司薪轉,月薪
2026-05-10,-15000,XX證券,定期定額 0050
2026-05-15,42000,XX銀行,股利
2026-05-20,-200000,XX建設,房屋頭期款匯款
EOF
```

### Step 2 — 進 sandbox，先確認 host isolation 有生效

NemoClaw sandbox 預設不會看到 host 任何路徑 — 連我們剛建的 `~/budget-demo/` 都看不到。先驗證一下：

```bash
nemoclaw my-assistant connect
```

進到 sandbox 後（prompt 變 `sandbox@...$`）：

```bash
# Sandbox 看不到 host 任何路徑 ✅
ls ~/budget-demo/ 2>&1            #  → No such file or directory
ls /host/ 2>&1                     #  → No such file or directory
ls /home/ubuntu/budget-demo 2>&1   #  → No such file or directory
```

這就是 OpenShell 的 filesystem isolation — 不用設 policy，sandbox 本來就看不到 host。

### Step 3 — 把 public CSV 帶進 sandbox（但不帶 private）

最穩的做法：直接在 sandbox 內用 heredoc 重建 public CSV。不需要 mount、不會踩到路徑 probe 的雷。

```bash
# 還在 sandbox 內
mkdir -p ~/budget && cd ~/budget

cat > transactions.csv <<'EOF'
date,amount,merchant,category
2026-05-02,-3200,房東,居住
2026-05-03,-185,全聯,生活
2026-05-05,-95,星巴克,餐飲
2026-05-07,-1250,台電,居住
2026-05-09,-420,Uber Eats,餐飲
2026-05-11,-680,家樂福,生活
2026-05-13,-95,星巴克,餐飲
2026-05-15,-260,Spotify,訂閱
2026-05-18,-1480,誠品,購物
2026-05-21,-560,7-11,生活
2026-05-25,-95,星巴克,餐飲
2026-05-28,-340,計程車,通勤
EOF
```

驗證：

```bash
ls ~/budget/                              # → transactions.csv
ls ~/budget-demo/private 2>&1             # → No such file or directory
```

`private` 那份依然只在 host，sandbox 物理上接觸不到。

### Step 4 — 用 OpenClaw TUI 請 agent 做分析

```bash
# 還在 sandbox 內
openclaw tui
```

在 TUI 內輸入：

```
請讀 ~/budget/transactions.csv：
1. 把 category 分組，算出 5 月每組的總金額
2. 算每組佔總支出的百分比
3. 把報表寫到 ~/budget/reports/2026-05.md
```

OpenClaw 會用 sandbox 內建的 Python 跑分析、寫出 markdown 報表。

接著測一下 agent 真的看不到敏感資料 — 在 TUI 同一個對話內問：

```
我這個月薪資多少？股利收入多少？
```

預期：agent 回覆**找不到這些資料** — 因為從它的視角，這些檔案物理上不存在。這不是 prompt engineering 約束，是 sandbox 隔離。

離開 TUI：`/exit`。

### Step 5 — 看 agent 跑出的報表

在 sandbox 內直接 `cat` 看：

```bash
# 還在 sandbox 內（先 /exit 離開 TUI）
cat ~/budget/reports/2026-05.md
```

完成後退出 sandbox：

```bash
exit
```

✅ 完成 — agent 能對 public 做完整分析、寫報表、給建議，但 **物理上無法接觸 private 那份**（因為從未進 sandbox）。


---

## 7. 進階學習資源

| 主題 | 路徑 / 連結 |
|------|-------------|
| NemoClaw 官方 quickstart | <https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html> |
| NemoClaw CLI 指令參考 | <https://docs.nvidia.com/nemoclaw/latest/reference/commands.html> |
| OpenClaw（agent 框架） | <https://docs.openclaw.ai/> |
| OpenShell（sandbox runtime） | <https://docs.nvidia.com/openshell/> |
| 內部完整訓練教材 | `./claw-training-assets-main/` （7 modules、46 notebooks） |

如果想要更系統化的訓練，本 repo 內的 `claw-training-assets-main/tracks/` 已經有完整 7 個模組，從 architecture 一路到 production operations。

---

## 8. 完整安裝順序（NCHC Ubuntu VM 實戰紀錄）

這是在 NCHC GPU VM（Ubuntu + NVIDIA H200）上實際走過一次的順序，把碰到的錯誤跟需要安裝的東西整理在一起。其他 Ubuntu 環境流程大同小異。

### 8.1 安裝項目（依順序）

| # | 項目 | 用途 | 指令 |
|---|------|------|------|
| 1 | Docker Engine | OpenShell sandbox 的 runtime | NemoClaw installer 會自動裝 |
| 2 | 把使用者加進 `docker` group | 讓 docker 不用 sudo | installer 會做，但要 `newgrp docker` 才生效 |
| 3 | Node.js 22.x + npm 10+ | NemoClaw CLI runtime | installer 透過 `nvm` 自動裝 |
| 4 | NemoClaw CLI 本體 | 主程式 | `curl -fsSL https://www.nvidia.com/nemoclaw.sh \| bash` |
| 5 | NVIDIA Container Toolkit | 提供 `nvidia-ctk`、產 CDI spec、讓 sandbox 看到 GPU | 見 9.2（GPU 機才需要） |
| 6 | CDI device spec (`/etc/cdi/nvidia.yaml`) | 讓 Docker 把 `nvidia.com/gpu` 解析成實體裝置 | `sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml` |

> Driver / CUDA 不在 NemoClaw 的安裝範圍內 — NCHC VM 預設已經有 driver 580.142 / CUDA 13.0，`nvidia-smi` 能跑就算 OK。

### 8.2 錯誤總表（依出現順序）

| 階段 | 錯誤訊息 | 原因 | 修法 | 詳見 |
|------|----------|------|------|------|
| Docker 安裝後 | `Your user 'ubuntu' is not in the docker group` | group membership 還沒在當前 shell 生效 | `newgrp docker`，然後重跑 installer | — |
| `[2/3] NemoClaw CLI` | `npm error code ECONNRESET` / `npm error network aborted` | npm 出去到 `registry.npmjs.org` 中斷（亞洲常見） | 拉高 timeout + 換 mirror | 9.1 |
| `[1/8] Preflight checks` | `unresolvable CDI devices nvidia.com/gpu=all` | Docker 開了 CDI 但缺 `nvidia-container-toolkit` | 裝 toolkit + 產 CDI spec，或 `nemoclaw onboard --no-gpu` | 9.2 |

### 8.3 一鍵 setup 腳本（給之後重做的人）

```bash
#!/usr/bin/env bash
set -euo pipefail

# 0. 先設好 npm 環境變數，避免 NemoClaw installer 中途死在 ECONNRESET
mkdir -p ~/.npm
cat > ~/.npmrc <<EOF
fetch-retries=5
fetch-retry-mintimeout=20000
fetch-retry-maxtimeout=120000
fetch-timeout=600000
registry=https://registry.npmmirror.com/
EOF

# 1. 跑 NemoClaw installer
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash

# 2. 若 docker group 還沒生效，新開 shell 或 newgrp
#    newgrp docker

# 3. GPU 機器才需要：裝 NVIDIA Container Toolkit + CDI spec
if command -v nvidia-smi >/dev/null && ! command -v nvidia-ctk >/dev/null; then
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  sudo apt-get update
  sudo apt-get install -y nvidia-container-toolkit
  sudo mkdir -p /etc/cdi
  sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
fi

# 4. Onboarding
nemoclaw onboard
```

---

## 9. 常見問題 (Troubleshooting)

| 問題 | 解法 |
|------|------|
| `docker: command not found` | 安裝 Docker Engine 或 Docker Desktop，並確認 user 在 `docker` group |
| `docker group not active in shell` | 跑 `newgrp docker` 或登出再登入，讓 group 生效 |
| sandbox OOM / 卡死 | 機器 RAM < 8GB 時加上 8GB swap，或升級記憶體 |
| Dashboard 連不上 | 檢查 port 18789 是否被佔用：`lsof -i :18789` |
| Inference provider 連線失敗 | `nemoclaw my-assistant inference test` 看詳細錯誤；通常是 API key 沒設好 |
| 在 Ubuntu 上 Ollama 解壓失敗 | 安裝 `zstd`：`sudo apt install zstd` |
| `npm error code ECONNRESET` 安裝時斷線 | 見 9.1 — 調 npm timeout / 換 mirror |
| `unresolvable CDI devices nvidia.com/gpu=all` | 見 9.2 — 安裝 NVIDIA Container Toolkit |
| `Docker GPU patch failed: AMD CDI spec not found` | NemoClaw GPU patch 會找 AMD CDI，沒有就失敗。先 `openshell sandbox delete <name>`，再 `export NEMOCLAW_DOCKER_GPU_PATCH=0` 跳過 patch，重跑 `nemoclaw onboard`。NVIDIA GPU 還是會透過 CDI 正常 passthrough |
| `'openclaw agent --local' is not supported inside NemoClaw sandboxes` | `--local` 會繞過 gateway 安全機制，預期會被擋。在 sandbox 內改用 `openclaw tui`（互動）或從 host 端用 dashboard / `nemoclaw <name> connect` |

### 9.1 npm `ECONNRESET` — 安裝 NemoClaw dependencies 時連線中斷

症狀（安裝 log 出現）：

```
✗  Installing NemoClaw dependencies
npm error code ECONNRESET
npm error network aborted
```

通常是出去到 `registry.npmjs.org` 不穩（NCHC / 台灣 VM 常見）。修法：

```bash
# 1. 拉長 timeout、加 retry
npm config set fetch-retries 5
npm config set fetch-retry-mintimeout 20000
npm config set fetch-retry-maxtimeout 120000
npm config set fetch-timeout 600000

# 2. 清 cache（避免半下載的 tarball 干擾）
npm cache clean --force

# 3. 換 Asia mirror（亞洲速度比官方快很多）
npm config set registry https://registry.npmmirror.com/

# 4. 重跑安裝
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash
```

`npmmirror.com` 不通的話，備用 mirror：

```bash
npm config set registry https://registry.yarnpkg.com/
```

裝完想切回官方：

```bash
npm config set registry https://registry.npmjs.org/
```

**診斷網路**（判斷是 registry 還是 VM 出去整體有問題）：

```bash
curl -v https://registry.npmjs.org/npm 2>&1 | tail -20            # 小檔
curl -v -o /dev/null https://registry.npmjs.org/npm/-/npm-10.9.8.tgz 2>&1 | tail -10  # 大檔
```

### 9.2 `unresolvable CDI devices nvidia.com/gpu=all` — Docker 沒裝 NVIDIA Container Toolkit

症狀（preflight 紅字）：

```
Docker is configured for CDI device injection (CDISpecDirs is set), but no
nvidia.com/gpu CDI spec was found on the host. OpenShell's gateway start will
fail with `unresolvable CDI devices nvidia.com/gpu=all`.
```

原因：Docker daemon 開了 CDI device injection，但缺 `nvidia-container-toolkit`（提供 `nvidia-ctk`）。

#### 方案 A — 跳過 GPU（最快，適合 remote inference demo）

```bash
nemoclaw onboard --no-gpu
```

Wizard 內 provider 選 NVIDIA Endpoints / OpenAI / Anthropic（**不要選 Local Ollama**）。

#### 方案 B — 安裝 NVIDIA Container Toolkit（需要 local GPU inference）

先確認真有 GPU：

```bash
nvidia-smi    # 應該看到 GPU 型號與 driver version
```

接著安裝 + 產 CDI spec：

```bash
# 1. 加 repo
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. 安裝
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 3. 產 CDI spec
sudo mkdir -p /etc/cdi
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# 4. 驗證：應看到 nvidia.com/gpu=0 和 nvidia.com/gpu=all
nvidia-ctk cdi list

# 5. 重跑 onboarding
nemoclaw onboard
```

---

完成這份 tutorial 後，你應該已經能：

- 安裝並 onboard 一個 NemoClaw sandbox
- 用 Dashboard 和 Terminal 兩種方式和 agent 對話
- 切換 inference provider、加 skill、接 messaging channel
- 做 backup / restore，並控管 network policy

Happy clawing! 🦞
