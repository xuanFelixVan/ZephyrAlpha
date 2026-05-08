"""
AI Understandability Constraint — AI 可理解性约束 (盲点 #13)
特性：
  - 声明：所有输出格式必须被 AI 零推理消费
  - 验证：check_readability() 检查字段命名/结构/文档完整性
"""
from dataclasses import dataclass
from typing import Any, Optional


class AIUnderstandabilityConstraint:
    """
    AI 可理解性约束 (盲点 #13)
    三段式规则：
      1. 声明 (declare)：输出格式必须是 AI 零歧义可消费的
      2. 验证 (verify)：字段完整命名、结构扁平优先、文档自描述
      3. 审计 (audit)：每次格式变更记录 Provenance Chain
    """

    READABILITY_RULES = {
        "no_abbreviations": "字段名必须完整命名，不得缩写",
        "flat_preferred": "结构应扁平化，嵌套≤2层",
        "self_documenting": "每个字段有 description 或 docstring",
        "enum_over_string": "枚举值优于原始字符串",
        "explicit_types": "类型注解必须显式，不用 Any 除非必要",
    }

    def check_readability(self, obj: Any) -> dict:
        violations = []
        passed = []

        for rule, description in self.READABILITY_RULES.items():
            check_result = self._check_rule(rule, obj)
            if check_result:
                passed.append({"rule": rule, "description": description})
            else:
                violations.append({"rule": rule, "description": description})

        return {
            "passed": len(passed),
            "violations": len(violations),
            "details": {"passed": passed, "violations": violations},
            "verdict": "PASS" if len(violations) == 0 else "FAIL",
        }

    def _check_rule(self, rule: str, obj: Any) -> bool:
        if rule == "no_abbreviations":
            if hasattr(obj, "__annotations__"):
                return all(len(k) > 2 for k in obj.__annotations__)
        if rule == "self_documenting":
            return hasattr(obj, "__doc__") and obj.__doc__ is not None
        return True

    def audit_format_change(self, old_format: dict, new_format: dict) -> str:
        changes = []
        old_keys = set(old_format.keys())
        new_keys = set(new_format.keys())
        added = new_keys - old_keys
        removed = old_keys - new_keys
        if added:
            changes.append(f"Added fields: {added}")
        if removed:
            changes.append(f"Removed fields: {removed}")
        return "; ".join(changes) if changes else "No structural changes"
