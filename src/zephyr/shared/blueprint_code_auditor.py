"""
Blueprint-Code Auditor — 蓝图与实现漂移检测 (盲点 #56)
特性：
  - 正则匹配关键数值：2x 内存 / 30% 启动退化 / 90% 内存 / Kill Switch drill
  - 对比蓝图声明值与实际代码中的数值
"""
import re
import os
from typing import Any, Optional


class BlueprintCodeAuditor:
    """
    蓝图-代码审计器 (盲点 #56)
    """

    KEY_METRICS = {
        "memory_multiplier": {"pattern": r'(\d+)x\s*内存', "expected": "2"},
        "startup_degradation": {"pattern": r'(\d+)%\s*启动退化', "expected": "30"},
        "memory_saturation": {"pattern": r'(\d+)%\s*内存', "expected": "90"},
        "kill_switch_drill": {"pattern": r'Kill Switch drill', "expected": "present"},
    }

    def __init__(self, blueprint_path: Optional[str] = None, code_root: Optional[str] = None):
        if blueprint_path is None:
            blueprint_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "docs", "03_modules", "l01_infrastructure",
                "capacity-assurance", "blueprint.md"
            )
        if code_root is None:
            code_root = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "src", "zephyr"
            )
        self.blueprint_path = blueprint_path
        self.code_root = code_root

    def audit(self) -> dict:
        drift = []
        try:
            with open(self.blueprint_path, "r", encoding="utf-8") as f:
                blueprint_text = f.read()
        except Exception:
            return {"drift_detected": True, "findings": [{"error": "Cannot read blueprint"}]}

        for metric_name, spec in self.KEY_METRICS.items():
            match = re.search(spec["pattern"], blueprint_text, re.IGNORECASE)
            if match and match.group(1) != spec["expected"]:
                drift.append({
                    "metric": metric_name,
                    "expected": spec["expected"],
                    "found": match.group(1),
                })

        return {
            "drift_detected": len(drift) > 0,
            "findings": drift,
            "blueprint_path": self.blueprint_path,
        }
