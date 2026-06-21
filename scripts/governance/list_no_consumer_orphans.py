"""从 orphan_analysis.json 中提取 NO_CONSUMER_HAS_VALUE 模块清单。"""

__manifest__ = {
    "args": [],
    "description": "从 orphan_analysis.json 提取无消费者孤儿模块清单",
    "dimensions": ["D1"],
    "priority": "P2",
    "timeout_seconds": 30,
    "warn_only": False,
}

import json
from pathlib import Path

data = json.loads(Path("d:/ZephyrAlpha/orphan_analysis.json").read_text(encoding="utf-8"))
no_consumer = [r for r in data["results"] if r["category"] == "NO_CONSUMER_HAS_VALUE"]
print(f"NO_CONSUMER_HAS_VALUE 模块清单 ({len(no_consumer)} 个):")
print("=" * 80)
for r in no_consumer:
    print(f"  {r['relative']:<55} size={r['size']:>6}  blueprint={r['has_blueprint']}  class_def={r['has_class_or_def']}")
print("=" * 80)
print(f"TOTAL: {len(no_consumer)}")
