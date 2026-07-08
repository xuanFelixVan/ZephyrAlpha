# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §4.7
# [MODULE] zephyr.autonomy_core.context.context_rule_registry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] MOD-INF-017; MOD-INF-018; MOD-INF-023; MOD-INF-033
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] rule_id 全局唯一; HOT 级别 ≤400 tokens; 注册后立即可 lookup
# [MODIFY-GUARD] context_assembler.py; context_pipeline.py; __init__.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] register: rule_id 冲突->覆盖; lookup: 无匹配->空列表; load_yaml: 文件不存在->FileNotFoundError
# [TESTS] tests/test_context_rule_registry.py
# [A_module] module_id=MOD-ORC_context_rule_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

__all__ = [
    "ContextRule",
    "ContextRuleRegistry",
]

_VALID_LEVELS = {"HOT", "DOMAIN", "COLD"}
_HOT_MAX_TOKENS = 400


@dataclass
class ContextRule:
    rule_id: str
    trigger_conditions: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    priority: int = 50
    injection_level: str = "DOMAIN"
    max_tokens: int = 500
    source_module: str = ""

    def __post_init__(self) -> None:
        if self.injection_level not in _VALID_LEVELS:
            raise ValueError(f"injection_level must be one of {_VALID_LEVELS}, got {self.injection_level!r}")
        if self.injection_level == "HOT" and self.max_tokens > _HOT_MAX_TOKENS:
            raise ValueError(f"HOT level max_tokens must be ≤{_HOT_MAX_TOKENS}, got {self.max_tokens}")


class ContextRuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, ContextRule] = {}

    def register(self, rule: ContextRule) -> None:
        self._rules[rule.rule_id] = rule

    def lookup(
        self,
        task_type: str = "",
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> list[ContextRule]:
        tags = tags or []
        input_text: str = kwargs.get("input_text", "")
        matched: list[ContextRule] = []

        for rule in self._rules.values():
            if self._matches(rule, task_type, tags, input_text, kwargs):
                matched.append(rule)

        matched.sort(key=lambda r: r.priority, reverse=True)
        return matched

    def unregister(self, rule_id: str) -> None:
        self._rules.pop(rule_id, None)

    def load_yaml(self, path: str) -> int:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError("YAML rules file not found")

        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "rules" not in data:
            return 0

        count = 0
        for item in data["rules"]:
            rule = ContextRule(
                rule_id=item["rule_id"],
                trigger_conditions=item.get("trigger_conditions", {}),
                content=item.get("content", ""),
                priority=item.get("priority", 50),
                injection_level=item.get("injection_level", "DOMAIN"),
                max_tokens=item.get("max_tokens", 500),
                source_module=item.get("source_module", ""),
            )
            self._rules[rule.rule_id] = rule
            count += 1

        return count

    def list_rules(self) -> list[ContextRule]:
        return sorted(self._rules.values(), key=lambda r: r.priority, reverse=True)

    def save_yaml(self, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        rules_data = []
        for rule in self.list_rules():
            rules_data.append(
                {
                    "rule_id": rule.rule_id,
                    "trigger_conditions": rule.trigger_conditions,
                    "content": rule.content,
                    "priority": rule.priority,
                    "injection_level": rule.injection_level,
                    "max_tokens": rule.max_tokens,
                    "source_module": rule.source_module,
                }
            )

        content = yaml.dump({"rules": rules_data}, allow_unicode=True, default_flow_style=False)
        tmp_path = f"{path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

    @staticmethod
    def _matches(
        rule: ContextRule,
        task_type: str,
        tags: list[str],
        input_text: str,
        kwargs: dict[str, Any],
    ) -> bool:
        conditions = rule.trigger_conditions

        if not conditions:
            return True

        if rule.injection_level == "HOT":
            return True

        cond_task_type = conditions.get("task_type", "")
        if cond_task_type and task_type:
            if cond_task_type == task_type:
                return True

        cond_tags = conditions.get("tags", [])
        if cond_tags and tags:
            if set(cond_tags) & set(tags):
                return True

        cond_keywords = conditions.get("keywords", [])
        if cond_keywords and input_text:
            input_lower = input_text.lower()
            for kw in cond_keywords:
                if kw.lower() in input_lower:
                    return True

        on_demand = conditions.get("on_demand", False)
        if on_demand:
            demand_requested = kwargs.get("include_cold", False)
            if demand_requested:
                return True

        if not cond_task_type and not cond_tags and not cond_keywords and not on_demand:
            return True

        return False
