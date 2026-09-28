# [BLUEPRINT] MOD-PA-044 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] tests.zephyr.data.test_pf_alloc_rebalance_check_wiring
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; zephyr.data.scheduler; zephyr.pf_alloc.rebalance_check_runner
# [CONSUMERS] FAC-E8 再平衡调度接线守卫（scheduler pf_alloc_rebalance_check 槽 ↔ rebalance_check_runner）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] monkeypatch 断言被调——runner 全替身，零真 CH/零网络；schedule.yaml 断言只读；
#   总闸文件存在=槽停用（lane_g 总闸惯例）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-PA-044-WIR | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E8 再平衡调度接线测试：pf_alloc_rebalance_check 槽确实调用 rebalance_check_runner。"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.data import scheduler as sched  # noqa: E402


class _FakeScheduler:
    def __init__(self):
        self._alerter = MagicMock()


@pytest.fixture()
def runner_calls(monkeypatch):
    calls: list[dict] = []
    holder: dict = {"result": {"ok": True}}

    def _fake_run(**kwargs):
        calls.append(kwargs)
        return holder["result"]

    monkeypatch.setattr("zephyr.pf_alloc.rebalance_check_runner.run_rebalance_check", _fake_run)
    return calls, holder


def test_slot_invokes_runner_with_alerter(runner_calls):
    calls, holder = runner_calls
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "pf_alloc_rebalance_check")
    assert out == {"pf_alloc_rebalance_check": True}
    assert len(calls) == 1
    assert calls[0]["alerter"] is fake._alerter


def test_runner_not_ok_returns_false(runner_calls):
    calls, holder = runner_calls
    holder["result"] = {"ok": False, "error": "blind_scan: budgets/pockets 缺证"}
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "pf_alloc_rebalance_check")
    assert out == {"pf_alloc_rebalance_check": False}


def test_exception_degrades_to_alerter(monkeypatch):
    def _boom(**kwargs):
        raise RuntimeError("ch down")

    monkeypatch.setattr("zephyr.pf_alloc.rebalance_check_runner.run_rebalance_check", _boom)
    fake = _FakeScheduler()
    out = sched._run_special_schedule(fake, "pf_alloc_rebalance_check")
    assert out == {"pf_alloc_rebalance_check": False}
    fake._alerter.notify.assert_called_once()
    assert fake._alerter.notify.call_args.kwargs["level"] == "ERROR"


def test_slot_registered_in_schedule_yaml():
    doc = yaml.safe_load((sched._DEFAULT_CONFIG_DIR / "schedule.yaml").read_text(encoding="utf-8"))
    slot = doc["schedules"]["pf_alloc_rebalance_check"]
    assert slot["cron"] == "45 5 * * 0-4"  # catchup_guard(05:30) 之后、pre_market(08:34) 之前
    assert slot["executor"] in ("default", "heavy", "realtime", "intraday_minute", "intraday_sector")


def test_slot_is_trading_day_guarded():
    from zephyr.data.trading_calendar import TRADING_DAY_GUARDED_SCHEDULES

    assert "pf_alloc_rebalance_check" in TRADING_DAY_GUARDED_SCHEDULES
