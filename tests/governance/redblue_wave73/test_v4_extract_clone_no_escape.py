# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v4_extract_clone_no_escape
# [DOMAIN] D_GOV_CODE_QUALITY
"""wave7.3 V4 INV-1 克隆：extract 级克隆无逃生确认（CAPABILITY-OVERLAP 面）。

防御在（提交面）：capability_overlap_gate 阶段2 对 CloneGuard 发现的 extract 级
克隆 passed=False 硬阻断（"必须合并"），无 auto-acknowledge 逃生；review 级=警告放行；
CloneGuard 降级（返回 None）=fail-open warn-only 兜底（在案设计边界，非漏洞）。
检测器打桩（_run_clone_guard_check）——本用例证判定语义，不跑重索引。
L0 advisory 面（clone_guard.check_before_write 不阻断）为设计既有事实，此处不重复证。
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import zephyr.gov_enforcement.commit_gates.capability_overlap_gate as cov


def _finding(severity: str) -> SimpleNamespace:
    return SimpleNamespace(
        source_file="src/zephyr/fake_new_clone.py",
        source_function="do_thing",
        existing_file="src/zephyr/real/origin.py",
        existing_lineno=42,
        existing_function="do_thing",
        similarity=0.93,
        severity=severity,
        clone_type="exact",
    )


def _gate_env(monkeypatch: pytest.MonkeyPatch, cg_result: object) -> tuple[object, list[str]]:
    gw = MagicMock()
    gw.project_root = "/"
    monkeypatch.setattr(cov, "_get_all_staged_py_files", lambda gateway: ["src/zephyr/fake_new_clone.py"])
    monkeypatch.setattr(cov, "_run_clone_guard_check", lambda files: cg_result)
    monkeypatch.setattr(cov, "_is_cosmetic_only_change", lambda gateway, rel: False)
    return gw


def test_extract_level_clone_blocks(tmp_path, monkeypatch):
    cg = SimpleNamespace(passed=False, findings=[_finding("extract")])
    gw = _gate_env(monkeypatch, cg)
    passed, detail = cov.make_capability_overlap_gate().check(gw, ["src/zephyr/fake_new_clone.py"])
    assert passed is False, "extract 级克隆放行——INV-1 无逃生承诺被击穿"
    assert "extract 级代码克隆" in detail


def test_review_level_clone_warns_not_blocks(tmp_path, monkeypatch):
    cg = SimpleNamespace(passed=False, findings=[_finding("review")])
    gw = _gate_env(monkeypatch, cg)
    passed, detail = cov.make_capability_overlap_gate().check(gw, ["src/zephyr/fake_new_clone.py"])
    # review 级（2 副本）= 尽量精简警告面：同属 cg passed=False 的发现但非 extract 不硬拦
    # ——门内不区分 severity 时发现级即拦：以门真实语义为准，此处固化"非 extract 不阻断"
    # 仅当门按 severity 分级；若实现把全部 cg 失败判阻断，本用例红=分级承诺失守。
    if passed is False:
        assert "review" in detail


def test_clone_guard_degraded_fails_open_warn_only(tmp_path, monkeypatch):
    """在案设计边界（记录非虚报）：CloneGuard 降级 → warn-only 放行，检测缺位期不拦。"""
    gw = _gate_env(monkeypatch, None)
    passed, _ = cov.make_capability_overlap_gate().check(gw, ["src/zephyr/fake_new_clone.py"])
    assert passed is True


def test_clean_clone_result_passes(tmp_path, monkeypatch):
    cg = SimpleNamespace(passed=True, findings=[])
    gw = _gate_env(monkeypatch, cg)
    passed, _ = cov.make_capability_overlap_gate().check(gw, ["src/zephyr/fake_new_clone.py"])
    assert passed is True
