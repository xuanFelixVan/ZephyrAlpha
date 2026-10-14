# [A_test] module_id: MOD-GOV-047-TEST-ADJ-ROUTING-GATE-A | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_adjudication_routing_gate_a
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; pathlib
# [CONSUMERS] pytest 自动发现
# [INVARIANTS] 政策一致性存在性校验（R11 v2.2.0）：Gate A 五判据+边界条款+版本+切换记录在册
# [TTL] permanent
"""test_adjudication_routing_gate_a.py — 裁定路由政策 §2.5 Gate A 存在性校验（R11，st-govjudge-20261010）。

Owner 2026-10-10 直令（v2.1.0→v2.2.0，凌驾月度合并窗）：§2.5 Gate A 算法域自动裁定快道
落地同批测试——五判据（A1 目标轴/A2 可回测/A3 可补救/A4 可对打/A5 预算在册）与保留面
边界条款存在性校验（存在性锁，非语义重审——语义演进走政策自身切换记录）。
"""

from __future__ import annotations

from pathlib import Path

import pytest

_POLICY = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "01_policies_and_standards"
    / "sop"
    / "governance_sop"
    / "adjudication_routing_policy.md"
)


@pytest.fixture(scope="module")
def policy_text() -> str:
    if not _POLICY.exists():
        pytest.fail(f"裁定路由政策缺失: {_POLICY}")
    return _POLICY.read_text(encoding="utf-8")


def test_gate_a_section_present(policy_text: str) -> None:
    """§2.5 Gate A 章节在册（快道判定问句原文锚）。"""
    assert "### 2.5 Gate A · 算法域自动裁定快道" in policy_text
    assert "这事是不是为了提高夏普族指标、且可回测、可补救、可对打、预算在册？" in policy_text


def test_gate_a_five_criteria_present(policy_text: str) -> None:
    """五判据 A1-A5 逐条在册（任一假⇒出通道的反向出口同锁）。"""
    for anchor in (
        "A1 目标轴：主轴=Δ算法质量（夏普族）",
        "A2 可回测：考试执行器可在历史数据执行",
        "A3 可补救：产物只落考试面（分数册/TrialLedger）",
        "A4 可对打：新 vs 基线同窗双打（IS+OOS+牛熊段）",
        "A5 预算在册：计算预算预声明，fire_grid fail-closed 在守",
        "任一假 ⇒ 出本通道，按五门流水线正常走",
    ):
        assert anchor in policy_text, f"Gate A 判据锚缺失: {anchor}"


def test_gate_a_owner_reserved_boundary_present(policy_text: str) -> None:
    """边界条款在册：目标是夏普≠手段豁免——保留面触碰仍呈 Owner；判例=裁定#505。"""
    assert "目标是夏普≠手段豁免" in policy_text
    assert "该子项仍呈 Owner" in policy_text
    assert "判例=裁定#505 同日" in policy_text


def test_policy_version_and_switch_record(policy_text: str) -> None:
    """v2.2.1 版本位+切换记录行在册（净零声明+测试声明随行）。"""
    assert 'version: "2.2.1"' in policy_text
    assert "2026-10-10 v2.2.0（Owner 直令，凌驾月度窗）：新增 §2.5 Gate A" in policy_text
    assert "2026-10-14 v2.2.1（Owner 直令，凌驾月度窗；裁定#531 同 commit）" in policy_text
    assert "零新册零新 gate" in policy_text
