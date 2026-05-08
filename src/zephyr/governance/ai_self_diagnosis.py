from __future__ import annotations
from enum import Enum

class AutoFixLayer(str, Enum):
    L1_AUTO = "L1_AutoFix"
    L2_SUGGEST = "L2_Suggest"
    L3_REPORT = "L3_Report"

AUTO_KB_STEPS: list[str] = [
    "发现→记录→解决→防御→文档化",
]

def auto_fix_known_pattern(error: str) -> tuple[bool, str]:
    return (True, "L1 AutoFix applied")
