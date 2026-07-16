# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/false_negative_cases/__init__.py | §
# [TTL] permanent
"""
False Negative Cases — Golden Test Case 库
==========================================
职责：为脚本系统的审计脚本提供标准化的假阴性检测用例，
确保每个维度的脚本都能正确检测出已知问题模式。
对应脚本系统蓝图盲点 B73 + 行动项 A1。

目录结构：
  false_negative_cases/
  ├── __init__.py          # 本文件
  ├── security_cases.yaml  # 安全维度用例
  ├── architecture_cases.yaml  # 架构维度用例
  ├── data_quality_cases.yaml  # 数据质量维度用例
  └── governance_cases.yaml    # 治理维度用例

每个 YAML 文件格式：
  cases:
    - case_id: "FN-XXX"
      description: "用例描述"
      expected_detection: "security|architecture|..."
      severity: "critical|high|medium|low"
      input_file: "test_fixtures/fn_XXX.py"
      expected_finding_count: 1
      false_negative_if: "脚本未检出此问题"
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["FalseNegativeCase", "load_cases"]


@dataclass
class FalseNegativeCase:
    case_id: str
    description: str
    expected_detection: str
    severity: str = "medium"
    input_file: str = ""
    expected_finding_count: int = 1
    false_negative_if: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


def load_cases(directory: str) -> list[FalseNegativeCase]:
    from pathlib import Path

    import yaml

    cases: list[FalseNegativeCase] = []
    dpath = Path(directory)

    for yaml_file in sorted(dpath.glob("*_cases.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for c in data.get("cases", []):
            cases.append(FalseNegativeCase(**c))

    return cases
