# Tutorial 02：寫程式 + 執行的 Code Agent

**目標：** 用 **ReAct** pattern 建立一個 agent，它會自己寫 Python、丟到 sandbox 執行、再看結果決定下一步。

> **環境設定：** 開始之前請先完成上一層 [README](../README.md) 的環境設定。

---

## 為什麼是 code_execution，不是搜尋？

ReAct 真正的強項是「**看到 Observation 之後再決定下一步**」。code execution 比 web search 更適合教學：

| | wiki / web search | **code_execution** |
|---|---|---|
| 多跳推理 | 看似有但常常一回合就答完 | 算式錯了→看 stderr→修正；每一步都看得到 |
| 自我修正 | 看到不滿意的搜尋結果換 query | **更直接**：看到 traceback 直接修 bug |
| 外部依賴 | Wikipedia API、API key、UA 限制 | 只要本機跑得起 Python 就 OK |
| 教學可重現性 | 受網路、限速、被擋影響 | 結果穩定、可離線 |
| 學員自由度 | 出題受限於 wiki 條目品質 | 數學、字串、資料分析皆可 |

---

## `code_execution` 怎麼運作

```
LLM 寫出一段 Python
   │
   ▼
┌──────────────────────────────────────────┐
│            code_execution tool           │
│                                          │
│  POST http://127.0.0.1:6000/execute     │
│  body: {                                 │
│    "generated_code": "<python source>", │
│    "timeout": 15,                        │
│    "language": "python"                  │
│  }                                       │
└──────────────────────────────────────────┘
   │
   ▼
sandbox 在子程序 exec()，回傳 stdout / stderr / status
   │
   ▼
LLM 看到結果 → Thought: 「對嗎？要不要再算一次？」
```

> Sandbox 是 `nvidia-nat` 內附的 Flask 程序（`local_sandbox_server.py`），
> 我們不用 docker、直接以 Python 子程序拉起來；notebook 的 Step 1 會自動處理。

---

## ReAct 在這個情境長怎樣

以「**找 x 使 x = cos(x) 收斂**」為例：

```
Thought: 用 fixed-point iteration，從 x=1 開始迭代到 |Δ|<1e-10
Action: py
Action Input: {"generated_code": "import math\nx=1.0\nfor i in range(200):\n    nx=math.cos(x)\n    if abs(nx-x)<1e-10:\n        print(f'iter={i}, x={nx}'); break\n    x=nx\n"}
Observation: iter=85, x=0.7390851332151607
Thought: 收斂值 ≈ 0.7391；驗證 cos(0.7391) 是不是約等於它本身
Action: py
Action Input: {"generated_code": "import math; print(math.cos(0.7390851332151607))"}
Observation: 0.7390851332151607
Thought: 完美吻合
Final Answer: 收斂值約為 0.7390851332，迭代 86 次。
```

第二次 Action 的存在，**完全取決於第一次的 Observation**——這正是 ReAct 比 `tool_calling_agent` 強的地方。

---

## 執行

```bash
# 單跳：寫程式算大數
nat run --config_file tutorial_02_code_agent/configs/config.yml \
        --input "Compute 2^100 and tell me how many digits it has."

# 多步 pipeline
nat run --config_file tutorial_02_code_agent/configs/config.yml \
        --input "Generate the first 20 Fibonacci numbers, then find which are prime, and report how many there are."

# 自我修正 + 數值驗證
nat run --config_file tutorial_02_code_agent/configs/config.yml \
        --input "Solve x^2 - 5*x + 6 = 0 symbolically with sympy, then verify by substituting each root back into the equation."
```

---

## 比較 Agent 類型

| Agent 類型 | 決策方式 | 適用 |
|---|---|---|
| `tool_calling_agent` | LLM 原生 tool-calling API（一次決定要呼叫什麼） | 快速、可預測的任務 |
| `react_agent` | 顯式 Thought / Action / Observation 迴圈（看到結果再決定下一步） | 多步推理、寫程式 + 驗證、可見的思考過程 |

**下一個：** [Tutorial 03 — 自訂 tool agent](../tutorial_03_custom_tool/README.md)
