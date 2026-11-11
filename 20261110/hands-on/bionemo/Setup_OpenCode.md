# Agent 設定（課後自建）

可以沿用自己的 agent。使用 OpenCode 時，依[官方文件](https://opencode.ai/docs/)安裝，選擇自己有權使用的語言模型；國網 Taiwan AI RAP 的帳號與模型存取請從 [iService](https://iservice.nchc.org.tw/)確認。憑證只設定在自己的私有設定檔或環境中。

課堂測試的 BioNeMo Agent Toolkit 版本如下。在新的環境下載並安裝四個官方 skill，以下指令在 `bionemo/` 執行：

```bash
git clone https://github.com/NVIDIA-BioNeMo/bionemo-agent-toolkit .toolkit
git -C .toolkit checkout f9bb5bb3aacc881c89eb15e93fd119e91915eea8
mkdir -p "$HOME/.config/opencode/skills"
for skill in drug-discovery-pipeline genmol-nim diffdock-nim boltz2-nim; do
  test ! -e "$HOME/.config/opencode/skills/$skill" || { printf 'Already installed: %s\n' "$skill"; continue; }
  cp -R ".toolkit/skills/bionemo-agent-toolkit/skills/$skill" "$HOME/.config/opencode/skills/"
done
```

若同名 skill 已存在，先比較版本再更新。其他 agent 請依其官方 skill 目錄規則安裝同一份來源。重新啟動 agent，確認四個 skill 能讀取，再讀 `AGENTS.md`、`support/agent/deployment_endpoints.md` 與教材提示詞。

讓 agent 使用此課程 `.venv/bin/python` 及 `support.workshop.ENDPOINTS`。需要截取互動 HTML 圖時才另外安裝 Playwright 與 Chromium；觀看 notebook 的 3D 圖不需要這個選用工具。
