# [A_test] module_id: MOD-GOV_test_strategy_family_attribution | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_strategy_family_attribution
# [TESTS] docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml
# [TTL] task_bound
"""90 号 Phase2 项（#1 策略类型）：新增策略强制族归属声明（治理流程，即时生效）。

裁定真源：90_methodology_open_questions.md 施工优先级表 #1——
  零新增施工：新增策略强制族归属声明（治理流程，即时生效）。
  本测试将治理规则固化为可执行门禁：每条策略 MUST 声明已知 strategy_class（族），
  且 strategy_id 的 CLASS 段与 strategy_class 一致（防"换名复活"式族漂移）。
"""

from __future__ import annotations

import re

import yaml

from zephyr.shared.io.paths import REPO_ROOT

_REGISTRY = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "strategy_registry.yaml"

#: 已知策略族（schema 注释枚举真源：daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）
_KNOWN_CLASSES = frozenset(
    {"daban", "multifactor", "event_driven", "value_reversal", "momentum_trend", "sector_rotation"}
)

#: strategy_id CLASS 段 → strategy_class 映射（族归属一致性）
_ID_PREFIX_TO_CLASS = {
    "DABAN": "daban",
    "MULTIFACTOR": "multifactor",
    "EVENT": "event_driven",
    "VREV": "value_reversal",
    "MOMTREND": "momentum_trend",
    "SECTOR": "sector_rotation",
    "SECTORROT": "sector_rotation",
}

_ID_RE = re.compile(r"^STR-([A-Z]+)-\d+$")


def _entries() -> list[dict]:
    with open(_REGISTRY, encoding="utf-8") as fh:
        return yaml.safe_load(fh)["strategies"]


class TestFamilyAttribution:
    def test_every_strategy_declares_known_family(self):
        """族归属强制声明：每条策略 strategy_class 非空且属已知族枚举。"""
        entries = _entries()
        assert entries, "strategy_registry 为空（门禁空转）"
        for e in entries:
            assert e.get("strategy_class") in _KNOWN_CLASSES, (
                f"{e.get('strategy_id')} strategy_class 缺失/非法: {e.get('strategy_class')!r}"
            )

    def test_id_prefix_consistent_with_family(self):
        """strategy_id 的 CLASS 段必须与 strategy_class 一致。"""
        for e in _entries():
            sid = e["strategy_id"]
            m = _ID_RE.match(sid)
            assert m, f"strategy_id 命名非法（须 STR-{{CLASS}}-{{NNN}}）: {sid}"
            prefix = m.group(1)
            assert prefix in _ID_PREFIX_TO_CLASS, f"{sid} 未知 CLASS 段: {prefix}"
            assert _ID_PREFIX_TO_CLASS[prefix] == e["strategy_class"], (
                f"{sid} 族不一致: id段={prefix}→{_ID_PREFIX_TO_CLASS[prefix]} vs strategy_class={e['strategy_class']}"
            )
