# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.known_unknown_registry
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Known-Unknown Registry — v0.16.0 R229

Blindspot: FLE unconscious of its own blindspots; "unknown unknowns" accumulate silently.
Risk: R229 — FLE overconfident in domains it has never been validated against.

Mitigation: "I know what I don't know" registry—explicit blindspot catalog with confidence calibration.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: known_unknown_registry.py
# 层: 算法
# - id: A1
#   name_zh: ① KnownUnknownRegistry
#   name_en: KnownUnknownRegistry
#   intro: class KnownUnknownRegistry 源码 L76-L88
#   desc: 公共方法（定义序）: register, open_count, by_domain；源码 L76-L88
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: KnownUnknownRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class KnownUnknownState(str, Enum):
    OPEN = "OPEN"
    MITIGATED = "MITIGATED"
    ACCEPTED = "ACCEPTED"


@dataclass
class KnownUnknown:
    id: str
    domain: str
    description: str
    state: KnownUnknownState = KnownUnknownState.OPEN
    last_reviewed: str = ""


@dataclass
class KnownUnknownRegistry:
    items: list[KnownUnknown] = field(default_factory=list)

    def register(self, item_id: str, domain: str, description: str) -> KnownUnknown:
        item = KnownUnknown(id=item_id, domain=domain, description=description)
        self.items.append(item)
        return item

    def open_count(self) -> int:
        return sum(1 for i in self.items if i.state is KnownUnknownState.OPEN)

    def by_domain(self, domain: str) -> list[KnownUnknown]:
        return [i for i in self.items if i.domain == domain]
