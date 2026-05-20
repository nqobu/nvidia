"""
NCHC LLM 工作坊用的自訂 tool。

每個 tool 都遵循同樣的 4 個部分：
  1. Config 類別      — 宣告 YAML 內使用的 _type 名稱
  2. @register_function — 把 builder 接到 nat 的 registry
  3. 內部 async 函式   — agent 實際呼叫的邏輯
  4. FunctionInfo.from_fn — 把函式包起來、附上給 LLM 閱讀的描述
"""

import logging

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1：Temperature Converter（溫度轉換器）
# 在攝氏、華氏、克氏溫度之間轉換。
# ─────────────────────────────────────────────────────────────────────────────

class TemperatureConverterConfig(FunctionBaseConfig, name="temperature_converter"):
    pass


@register_function(config_type=TemperatureConverterConfig)
async def temperature_converter(config: TemperatureConverterConfig, builder: Builder):

    async def _convert_temperature(text: str) -> str:
        import re

        text_lower = text.lower()

        match = re.search(r"[-+]?\d+\.?\d*", text)
        if not match:
            return "Could not find a number. Example: '100 celsius to fahrenheit'."
        value = float(match.group())

        if any(kw in text_lower for kw in ["celsius", " c ", "°c", "centigrade"]):
            source = "C"
        elif any(kw in text_lower for kw in ["fahrenheit", " f ", "°f"]):
            source = "F"
        elif any(kw in text_lower for kw in ["kelvin", " k "]):
            source = "K"
        else:
            return "Could not detect the source unit. Use 'celsius', 'fahrenheit', or 'kelvin'."

        if "fahrenheit" in text_lower or ("to f" in text_lower and source != "F"):
            target = "F"
        elif "kelvin" in text_lower or ("to k" in text_lower and source != "K"):
            target = "K"
        elif "celsius" in text_lower or ("to c" in text_lower and source != "C"):
            target = "C"
        else:
            return "Could not detect the target unit. Use 'celsius', 'fahrenheit', or 'kelvin'."

        if source == target:
            return f"{value} {source} = {value} {target} (same unit)"

        if source == "C" and target == "F":
            result = value * 9 / 5 + 32
        elif source == "C" and target == "K":
            result = value + 273.15
        elif source == "F" and target == "C":
            result = (value - 32) * 5 / 9
        elif source == "F" and target == "K":
            result = (value - 32) * 5 / 9 + 273.15
        elif source == "K" and target == "C":
            result = value - 273.15
        elif source == "K" and target == "F":
            result = (value - 273.15) * 9 / 5 + 32
        else:
            return "Unsupported conversion."

        return f"{value} {source} = {result:.2f} {target}"

    yield FunctionInfo.from_fn(
        _convert_temperature,
        description=(
            "Converts temperature values between Celsius (C), Fahrenheit (F), and Kelvin (K). "
            "Example: '100 celsius to fahrenheit', '32 F to C', '300 K to celsius'."
        ),
    )
