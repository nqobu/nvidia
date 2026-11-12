# Tutorial 01：Hello World

**目標：** 跑一個最簡單的 NeMo Agent Toolkit workflow — 一個 LLM、一個 tool、一個問題。

> **環境設定：** 開始之前請先完成上一層 [README](../README.md) 的環境設定。

---

## 本教學的概念

```
你的問題
     │
     ▼
┌─────────────────────────────────┐
│       tool_calling_agent        │
│                                 │
│  1. LLM 讀取你的問題             │
│  2. LLM 決定呼叫某個 tool        │
│  3. Tool 執行、傳回結果          │
│  4. LLM 寫出最終答案             │
└─────────────────────────────────┘
     │
     ▼
   答案
```

**`tool_calling_agent`** — agent 透過 LLM 內建的 tool-calling 能力決定**何時**與**如何**呼叫 tool。

**`current_datetime`** — 內建 tool，傳回當前日期與時間。

---

## 執行

從 `nchc_llm_workshop_2026/` 目錄執行：

```bash
nat run --config_file tutorial_01_hello_world/configs/config.yml \
        --input "What time is it right now? And say hello to the NCHC workshop!"
```

也試試其他問題：
```bash
nat run --config_file tutorial_01_hello_world/configs/config.yml \
        --input "What day of the week is it today?"

nat run --config_file tutorial_01_hello_world/configs/config.yml \
        --input "How many hours until midnight?"
```

---

## 預期輸出

```
Invoking tool: get_time(...)
Tool result: The current time of day is 2026-04-30 10:30:00

Workflow Result:
['Hello NCHC Workshop! The current time is 10:30 AM on April 30, 2026.']
```

**下一個：** [Tutorial 02 — 維基百科研究 agent](../tutorial_02_wiki_agent/README.md)
