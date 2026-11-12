# Tutorial 03：自訂 tool agent

**目標：** 用 Python 寫自己的 tool 並接到 NeMo Agent Toolkit workflow 裡。

> **環境設定：** 開始之前請先完成上一層 [README](../README.md) 的環境設定。

---

## 你會做出什麼

| Tool | 用途 |
|---|---|
| `temperature_converter` | 攝氏 ↔ 華氏 ↔ 克氏溫度 |
| `distance_converter` | km、m、miles、feet、inches、… |
| `simple_math` | 算術表達式 |

---

## 自訂 Tool 的結構

每個 tool 都遵循這 4 個部分：

```python
# 1. Config 類別 — 設定 YAML 內會用到的 _type 名稱
class MyToolConfig(FunctionBaseConfig, name="my_tool"):
    pass

# 2. Decorator — 把 tool 註冊到 nat
@register_function(config_type=MyToolConfig)
async def my_tool_builder(config: MyToolConfig, builder: Builder):

    # 3. 內部 async 函式 — agent 真正會呼叫的邏輯
    async def _my_tool(text: str) -> str:
        return "result"

    # 4. FunctionInfo — 包裝函式並附上給 LLM 看的描述
    yield FunctionInfo.from_fn(_my_tool, description="這個 tool 做什麼。範例：'10 km to miles'")
```

---

## Tool 怎麼被發現

`pyproject.toml` 宣告了 entry point：

```toml
[project.entry-points.'aiq.components']
nchc_unit_converter = "nchc_unit_converter.register"
```

當你安裝這個 package，Python 會註冊這個 entry point。
`nat` 啟動時會 import 每個已註冊的模組，觸發 `@register_function`，
讓 YAML 設定檔可以用到對應的 `_type` 名稱。

---

## 安裝自訂 tool 套件

寫完程式碼後（在 notebook 內進行），把套件裝進目前的環境：

```bash
uv pip install -e tutorial_03_custom_tool/
```

或在 Jupyter cell 內：
```python
%pip install -e tutorial_03_custom_tool/
```

驗證註冊有沒有成功：
```bash
nat info components | grep -E "temperature|distance|simple_math"
```

---

## 執行

```bash
nat run --config_file tutorial_03_custom_tool/configs/config.yml \
        --input "Convert 100 Celsius to Fahrenheit."

nat run --config_file tutorial_03_custom_tool/configs/config.yml \
        --input "How many miles is a marathon (42.195 km)?"

nat run --config_file tutorial_03_custom_tool/configs/config.yml \
        --input "What is 2 to the power of 10, divided by 8?"
```

---

## 練習：加入你自己的 tool

加一個**重量轉換器**（kg、lb、oz、g）：
1. 在 `register.py` 加上 `WeightConverterConfig` 與 `@register_function`
2. 在 `config.yml` 的 `tool_names` 內加上 `weight_converter`
3. 重新安裝：`uv pip install -e tutorial_03_custom_tool/`
4. 執行：`nat run ... --input "Convert 70 kg to pounds"`
