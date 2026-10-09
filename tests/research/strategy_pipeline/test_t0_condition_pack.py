# [BLUEPRINT] MOD-BT-226 | docs/03_modules/_domain_backtest/blueprint.md | §做T条件包日链
# [MODULE] tests.strategy_pipeline.test_t0_condition_pack
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; zephyr.strategy_pipeline.t0_condition_pack; zephyr.strategy_pipeline.pipeline_events
# [CONSUMERS] F43 做T统一调度接线质量守卫（t0_condition_pack_due 执行体）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试禁写生产路径——子进程/marker/alert 全 monkeypatch（零真实脚本执行/零库/
#   零 .runtime 触碰）；STEPS 步序契约（anchored_state→six_phase→condition_pack）钉死
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-BT-226-tests | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""做T条件包日件执行体单元测试（全 mock，零真库/零子进程实跑）。

覆盖：happy path 三步串行+marker、同日幂等跳过、force 逃生、步失败即停不触 marker、
payload 业务日覆盖与 resolver 回退、单步超时收敛 rc=-1、契约签名钉死。
铁律：不连真实 QMT/任何业务数据库、不写 data/ 生产路径。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.strategy_pipeline import pipeline_events  # noqa: E402
from zephyr.strategy_pipeline import t0_condition_pack as tcp  # noqa: E402


@pytest.fixture()
def wired(monkeypatch):
    """marker/alert/pipeline_events 侧全替身；_run_step 由各测试覆写。"""
    calls: dict = {"markers": [], "alerts": []}
    monkeypatch.setattr(pipeline_events, "_marker_seen", lambda name: False)
    monkeypatch.setattr(pipeline_events, "_touch_marker", lambda name: calls["markers"].append(name))
    monkeypatch.setattr(pipeline_events, "alert", lambda msg, level="WARN": calls["alerts"].append((level, msg)))
    return calls


def test_contract_signature_pinned():
    """run_optional_due 派发契约钉死：def run_t0_condition_pack_due(event: dict) -> dict。"""
    import inspect

    sig = inspect.signature(tcp.run_t0_condition_pack_due)
    assert list(sig.parameters) == ["event"]
    assert pipeline_events.OPTIONAL_DUE_KINDS["t0_condition_pack_due"] == (
        "zephyr.strategy_pipeline.t0_condition_pack",
        "run_t0_condition_pack_due",
    )


def test_happy_path_three_steps_serial_and_marker(wired, monkeypatch):
    ran: list[str] = []

    def fake_run(script_rel, extra, timeout_s):
        ran.append(script_rel)
        assert timeout_s == tcp.DEFAULT_STEP_TIMEOUT_S
        return 0, ""

    monkeypatch.setattr(tcp, "_run_step", fake_run)
    out = tcp.run_t0_condition_pack_due({"payload": {"trade_date": "2026-09-28"}})
    assert out == {"rc": 0, "day": "2026-09-28", "steps": [s[0] for s in tcp.STEPS]}
    assert ran == [s[1] for s in tcp.STEPS]  # 步序=anchored_state→six_phase→condition_pack
    assert wired["markers"] == ["t0_condition_pack_due:2026-09-28"]  # 全步成功才落 trade_date marker
    assert any("已落地" in msg for _, msg in wired["alerts"])


def test_step_failure_stops_no_marker(wired, monkeypatch):
    ran: list[str] = []

    def fake_run(script_rel, extra, timeout_s):
        ran.append(script_rel)
        return (1, "boom") if len(ran) == 1 else (0, "")

    monkeypatch.setattr(tcp, "_run_step", fake_run)
    out = tcp.run_t0_condition_pack_due({"payload": {"trade_date": "2026-09-28"}})
    assert out == {"rc": 1, "day": "2026-09-28", "step": "anchored_state"}
    assert len(ran) == 1  # 失败即停，不续跑后续步
    assert wired["markers"] == []  # 失败不触 marker=跨唤醒重试
    assert any(level == "ERROR" for level, _ in wired["alerts"])


def test_same_day_marker_skip_and_force_escape(wired, monkeypatch):
    monkeypatch.setattr(pipeline_events, "_marker_seen", lambda name: True)
    ran: list[str] = []
    monkeypatch.setattr(tcp, "_run_step", lambda s, e, t: ran.append(s) or (0, ""))
    out = tcp.run_t0_condition_pack_due({"payload": {"trade_date": "2026-09-28"}})
    assert out == {"skipped": "already_persisted", "day": "2026-09-28"}
    assert ran == []  # 幂等：同业务日已成功=零副作用
    out2 = tcp.run_t0_condition_pack_due({"payload": {"trade_date": "2026-09-28", "force": True}})
    assert out2["rc"] == 0 and len(ran) == 3  # force=人工重跑逃生


def test_day_fallback_to_data_driven_resolver(wired, monkeypatch):
    monkeypatch.setattr(pipeline_events, "resolve_pf_alloc_trade_date", lambda: "2026-09-25")
    monkeypatch.setattr(tcp, "_run_step", lambda s, e, t: (0, ""))
    out = tcp.run_t0_condition_pack_due({"payload": {}})
    assert out["day"] == "2026-09-25"  # 禁墙钟猜日：回退=行情业务日真源


def test_payload_day_overrides_resolver(wired, monkeypatch):
    monkeypatch.setattr(
        pipeline_events,
        "resolve_pf_alloc_trade_date",
        lambda: (_ for _ in ()).throw(RuntimeError("禁猜日——resolver 不该被调")),
    )
    monkeypatch.setattr(tcp, "_run_step", lambda s, e, t: (0, ""))
    out = tcp.run_t0_condition_pack_due({"payload": {"biz_date": "2026-09-24"}})
    assert out["day"] == "2026-09-24"  # 显式覆盖优先（人工重跑口）


def test_run_step_timeout_converges_to_rc_minus1(monkeypatch):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="x", timeout=600)

    monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", boom)
    rc, err = tcp._run_step("scripts/ch/build_anchored_state_history.py", (), 600)
    assert rc == -1 and "timeout" in err  # 超时=有界硬边界，收敛为失败不挂死


def test_steps_are_explicit_paths_no_glob():
    """§D 处方：显式常量路径（禁 glob）；头部空洞步=anchored_state 在链首。"""
    assert tcp.STEPS[0][0] == "anchored_state" and tcp.STEPS[0][1].endswith("build_anchored_state_history.py")
    assert all(not any(ch in s[1] for ch in "*?") for s in tcp.STEPS)
