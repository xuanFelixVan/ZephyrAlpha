# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] tests.git.test_w5_gate_chain_parallel
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [CONSUMERS] —
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] W5 袋内并行等价性契约（st-bt-fast-w5-20261006 第 2 步红蓝判据钉死）：①同注册表 width=1 vs width=4 逐门 (passed, detail) 完全一致且顺序=priority 序（红蓝判据）；②门抛异常=fail-closed passed=False 与串行一致；③SERIAL_EXECUTION_GATES 命中门恒串行；④宽度=1 或独立门<2 回退串行现行为；⑤总闸 ZEPHYR_W5_GATE_SPEEDUP=0 回串行；⑥结果重装与触发跳过记录保 priority 序
# [MODIFY-GUARD] —
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯内存假 gateway，零 git/盘面依赖；断言失败即测试失败
# [TESTS] tests/git/test_w5_gate_chain_parallel.py（自）
# [A_module] module_id=MOD-GOV_COMMIT_GATE_REGISTRY | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_all 袋内并行等价性测试（纯内存，假 gateway）。

W5 第 2 步红蓝判据：改前后同袋判定结论逐门一致——本册用确定性假门（含 sleep
交错与异常门）把该判据钉成常驻回归。
"""

from __future__ import annotations

import time

import pytest

from zephyr.gov_enforcement.rule_bridge import commit_gate_registry as cgr
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateSpec,
)


class _FakeGateway:
    """最小假 gateway：无 git，只承载 project_root 属性与审计空转。"""

    project_root = "."


@pytest.fixture(autouse=True)
def _no_flush(monkeypatch):
    """记账落盘改空转（观测设施不参与断言）。"""
    monkeypatch.setattr(cgr, "_stat_flush", lambda gateway: None)
    monkeypatch.delenv("ZEPHYR_W5_GATE_SPEEDUP", raising=False)


def _build_registry(n: int = 12, fail_at: int | None = None) -> CommitGateRegistry:
    reg = CommitGateRegistry()
    for i in range(n):

        def _make(i: int):
            def _check(gateway, files, **kwargs):
                time.sleep(0.01 * (i % 3))  # 交错耗时诱发并行重排
                if fail_at is not None and i == fail_at:
                    raise RuntimeError(f"boom-{i}")
                return (i % 2 == 0), f"detail-{i}"

            return _check

        reg.register(GateSpec(gate_id=f"G{i:02d}", check=_make(i), priority=100 + i))
    return reg


def _digest(results):
    return [(r.gate_id, r.passed, r.detail) for r in results]


def test_parallel_equals_serial(monkeypatch):
    gw = _FakeGateway()
    reg = _build_registry(n=12)
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 1)
    serial = reg.check_all(gw, ["a.py"], session_id="t")
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 4)
    par = reg.check_all(gw, ["a.py"], session_id="t")
    assert _digest(serial) == _digest(par)
    assert [r.gate_id for r in par] == sorted(r.gate_id for r in par)  # priority 序确定性


def test_exception_fail_closed_same_as_serial(monkeypatch):
    gw = _FakeGateway()
    reg = _build_registry(n=8, fail_at=3)
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 1)
    serial = reg.check_all(gw, ["a.py"], session_id="t")
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 4)
    par = reg.check_all(gw, ["a.py"], session_id="t")
    assert _digest(serial) == _digest(par)
    bad = [r for r in par if r.gate_id == "G03"][0]
    assert bad.passed is False and "fail-closed" in bad.detail


def test_serial_exclusion_set(monkeypatch):
    gw = _FakeGateway()
    reg = _build_registry(n=6)
    orig = cgr.SERIAL_EXECUTION_GATES
    monkeypatch.setattr(cgr, "SERIAL_EXECUTION_GATES", frozenset({"G02"}))
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 4)

    # 钉住：G02 在宽 4 下结果与串行一致（排除集只影响执行位置，不影响判定）
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 1)
    serial = reg.check_all(gw, ["a.py"], session_id="t")
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 4)
    par = reg.check_all(gw, ["a.py"], session_id="t")
    assert _digest(serial) == _digest(par)
    assert orig == frozenset()  # 生产缺省恒空（显式依赖序逃生口默认不启用）


def test_width_one_single_gate_falls_back_serial(monkeypatch):
    gw = _FakeGateway()
    reg = CommitGateRegistry()
    reg.register(GateSpec(gate_id="ONLY", check=lambda gw_, f, **k: (True, "ok"), priority=100))
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 4)
    res = reg.check_all(gw, ["a.py"], session_id="t")  # 独立门<2 → 串行分支
    assert _digest(res) == [("ONLY", True, "ok")]


def test_kill_switch_forces_serial(monkeypatch):
    gw = _FakeGateway()
    reg = _build_registry(n=8)
    monkeypatch.setenv("ZEPHYR_W5_GATE_SPEEDUP", "0")
    monkeypatch.setattr(cgr, "_resolve_parallel_width", lambda: 1)  # 总闸关=宽 1
    res = reg.check_all(gw, ["a.py"], session_id="t")
    assert len(res) == 8
