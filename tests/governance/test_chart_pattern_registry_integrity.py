# [BLUEPRINT] REG-PAT-001 | docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml | §schema v2.2
# [MODULE] tests.governance.test_chart_pattern_registry_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml
# [CONSUMERS] REG-PAT-001 结构完整性常设守卫（真源蓝测，pytest 全量必跑）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读测试（真源蓝测基线，禁写注册表）；entry_count 对账归 CR-007 不在此重复
# [MODIFY-GUARD] 与 chart_pattern_registry schema v2.2 refinements 语义同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=REG-PAT-001 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""chart_pattern_registry（REG-PAT-001）结构完整性常设守卫。

2026-09-15 落地（v2.2 refinements 常设校验器销项，原"挂待施工"批注 8b4ccc3d23）：
- refinements 双向闭环：父条目 refinements[].registered_as 必须指向存在条目，
  且该子条目 variant_of 回指父 pattern_id（已立卡分支闭环判别式）；
- refinements 条目形状：name/name_zh/source 必填（未立卡细化 null+来源语义）；
- pattern_id 全表唯一。
entry_count 对账由 check_registry_consistency CR-007 承载（REG-PAT-001 已登记口径），不在此重复。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
_REGISTRY = _REPO / "docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml"


@pytest.fixture(scope="module")
def entries() -> list[dict]:
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    return data["chart_patterns"]


def _by_id(entries: list[dict]) -> dict[str, dict]:
    return {e["pattern_id"]: e for e in entries}


def test_pattern_id_unique(entries):
    ids = [e["pattern_id"] for e in entries]
    assert len(ids) == len(set(ids)), "pattern_id 重复（SSoT 身份唯一性破坏）"


def test_refinements_bidirectional_closure(entries):
    """已立卡分支闭环：父 refinements.registered_as → 子存在且 variant_of 回指父。

    破坏形态回归：registered_as 指向不存在/拼错的 id（登记悬空）；子条目
    variant_of 漏填/指向第三方（父子闭环断裂）——两者都会让未来生成器/映射器
    沿 refinements 或 variant_of 单向遍历时丢分支。
    """
    by_id = _by_id(entries)
    problems: list[str] = []
    for e in entries:
        for r in e.get("refinements") or []:
            ra = r.get("registered_as")
            if not ra:
                continue
            child = by_id.get(ra)
            if child is None:
                problems.append(f"{e['pattern_id']}: registered_as '{ra}' 不存在（登记悬空）")
            elif child.get("variant_of") != e["pattern_id"]:
                problems.append(
                    f"{e['pattern_id']}→{ra}: 子条目 variant_of={child.get('variant_of')!r} 不回指父（闭环断裂）"
                )
    assert not problems, "refinements 双向闭环破坏:\n" + "\n".join(f"  - {p}" for p in problems)


def test_refinements_item_shape(entries):
    """refinements 条目形状：name/name_zh/source 必填（v2.2 裁定：未立卡细化=null+来源）。"""
    problems: list[str] = []
    for e in entries:
        for r in e.get("refinements") or []:
            missing = [k for k in ("name", "name_zh", "source") if not r.get(k)]
            if missing:
                problems.append(f"{e['pattern_id']}: refinement {r.get('name', '?')} 缺字段 {missing}")
    assert not problems, "refinements 形状违规:\n" + "\n".join(f"  - {p}" for p in problems)
