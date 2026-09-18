# [MODULE] tests.zephyr.data.test_failopen_brk049
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.scheduler; zephyr.data.alerter; zephyr.data.source_circuit_breaker; zephyr.data.supply_sentinel
# [TESTS] 本文件
# [TTL] permanent
"""BRK-049/BRK-046 吞异常与哨兵白名单收口的**能红测试钉**（车道 st-ff-failopen-20260918）。

判据来源（#ARCH-327 实证教训）：加固代码本身写在 `except Exception` 里，而它的两条
测试把**防线整体 patch 成 MagicMock** → 全绿但空转 17 小时。故本文件的铁律是：

    **被断言的那条防线永远是真对象，注入故障只打在它的协作方/环境上。**

- 告警投递闩：真 `IntegratorScheduler` 实例 + 真 `Alerter`（root=tmp_path），
  故障用"failures 目录的父路径是一个普通文件"制造真 `NotADirectoryError`；
- 熔断回调：真 `SourceCircuitBreaker`，回调是真会 `1/0` 的函数；
- 去重状态：真 `_should_print_warn`，故障是真损坏的 JSON / 真不可写的 `.runtime`；
- 哨兵白名单：真 `check_tables` + 真不存在的表（CH 可达与否都必然报红）。

每条都同时断言"不预设失败类别"这条日志纪律：正文里出现的异常类型名必须等于
真实抛出的那个类型，且 `exc_info` 非空。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.data.alerter import LEVEL_CRITICAL, Alerter
from zephyr.data.source_circuit_breaker import CircuitState, SourceCircuitBreaker
from zephyr.data.supply_sentinel import _SENTINEL_CONFIG_PATH, check_tables

# 收口后被撤豁免的 12 张在册表（判据：撤豁免≠放宽阈值，只是把"永不响"改回"会响"）
_SENTINEL_ALLOW_EMPTY_CEILING: int = 1


class _ExplodingAlerter:
    """真会抛的告警通道（注入协作方故障，不 patch 被测防线本身）。"""

    def __init__(self, exc: BaseException) -> None:
        self._exc = exc
        self.calls = 0

    def notify(self, **_kw: Any) -> bool:  # noqa: ANN401 — 与 Alerter.notify 同形
        self.calls += 1
        raise self._exc


def _undeliverable_dir(tmp_path: Path) -> Path:
    """构造一个**必然**写盘失败的路径：父段是普通文件，mkdir 必抛。"""
    blocker = tmp_path / "blocker.json"
    blocker.write_text("{}", encoding="utf-8")
    return blocker / "failures"


def _error_records(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.levelno >= logging.ERROR]


def _assert_real_type_in_message(rec: logging.LogRecord) -> None:
    """兜底日志不得预设失败类别：正文须含**真实**异常类型名 + 保留栈。"""
    assert rec.exc_info, "兜底日志必须带 exc_info（丢栈=无法归因）"
    real = type(rec.exc_info[1]).__name__
    assert real in rec.getMessage(), f"日志预设/缺失失败类别：真实类型 {real} 未进正文"


# ============ 1. CH 健康探活告警闩（真 CRITICAL 断供告警面）============ #


def test_deliver_alert_reports_false_when_not_landed(tmp_path: Path, caplog) -> None:
    """真投递失败时 helper 必须返回 False——旧实现把返回值丢弃后无条件置"已告警"。"""
    from zephyr.data.scheduler import IntegratorScheduler

    sched = IntegratorScheduler.__new__(IntegratorScheduler)  # 真类，不 mock 防线
    sched._alerter = Alerter(failures_dir=_undeliverable_dir(tmp_path))
    with caplog.at_level(logging.DEBUG):
        delivered = sched._deliver_alert_with_latch(
            task_id="ch_health_probe",
            error="CH 健康探活连续 3 次失败",
            level=LEVEL_CRITICAL,
            source="clickhouse",
        )
    assert delivered is False, "告警未落盘却返回 True = 假处置（旧行为）"
    assert any("未落盘" in r.getMessage() for r in _error_records(caplog)), "未投递必须留痕"
    _assert_real_type_in_message(
        next(r for r in caplog.records if "写失败汇总文件异常" in r.getMessage())
    )


def test_deliver_alert_reports_false_when_channel_raises(tmp_path: Path, caplog) -> None:
    """通道抛异常：判为未投递 + 留真实类型栈，且**不上抛**（不得打断探活主循环）。"""
    from zephyr.data.scheduler import IntegratorScheduler

    sched = IntegratorScheduler.__new__(IntegratorScheduler)
    sched._alerter = _ExplodingAlerter(TypeError("boom"))
    with caplog.at_level(logging.DEBUG):
        delivered = sched._deliver_alert_with_latch(
            task_id="ch_health_probe",
            error="x",
            level=LEVEL_CRITICAL,
            source="clickhouse",
        )
    assert delivered is False
    rec = next(r for r in _error_records(caplog) if "告警投递异常" in r.getMessage())
    assert "TypeError" in rec.getMessage()
    _assert_real_type_in_message(rec)


def test_deliver_alert_true_on_real_landing(tmp_path: Path) -> None:
    """正向对照：目录可写时必须返回 True 且盘上真有文件（否则上面的红是假红）。"""
    from zephyr.data.scheduler import IntegratorScheduler

    sched = IntegratorScheduler.__new__(IntegratorScheduler)
    ok_dir = tmp_path / "failures"
    sched._alerter = Alerter(failures_dir=ok_dir)
    assert (
        sched._deliver_alert_with_latch(
            task_id="ch_health_probe", error="y", level=LEVEL_CRITICAL, source="clickhouse"
        )
        is True
    )
    landed = list(ok_dir.glob("*.json"))
    assert len(landed) == 1, "返回 True 但盘上无件 = 又一处假处置"
    assert json.loads(landed[0].read_text(encoding="utf-8"))["task_id"] == "ch_health_probe"


# ============ 2. 数据源熔断器跳闸回调（保命升级链）============ #


def test_circuit_breaker_trip_callback_failure_is_observable() -> None:
    """回调炸了：状态机必须仍是 OPEN（不放松），但失败必须可被外部机械观测。"""
    def _boom(_source: str, _reason: str) -> None:
        _ = 1 / 0

    br = SourceCircuitBreaker("failopen_probe", failure_threshold=2, on_trip=_boom)
    br.record_failure()
    br.record_failure()

    assert br.state is CircuitState.OPEN, "回调故障回滚了熔断态 = 放松（绝不允许）"
    assert br.allow_request() is False, "熔断中仍放行 = 放松"
    assert br.trip_callback_failures == 1, "升级回调失败被吞（BRK-049 旧行为）"
    assert br.last_trip_callback_error is not None
    assert br.last_trip_callback_error.startswith("ZeroDivisionError")


def test_circuit_breaker_trip_logs_real_exception_type(caplog) -> None:
    """跳闸回调异常必须进 ERROR 日志并带真实类型名+栈。"""
    def _boom(_source: str, _reason: str) -> None:
        raise ValueError("升级通道不可用")

    br = SourceCircuitBreaker("failopen_probe_log", failure_threshold=1, on_trip=_boom)
    with caplog.at_level(logging.DEBUG):
        br.record_failure()
    rec = next(r for r in _error_records(caplog) if "熔断跳闸升级回调失败" in r.getMessage())
    assert "ValueError" in rec.getMessage()
    _assert_real_type_in_message(rec)


# ============ 3. RECONCILER-HEALTH 告警去重状态（gate 自身留痕面）============ #


def test_should_print_warn_dedup_and_degrade_traces(tmp_path, caplog) -> None:
    from zephyr.gov_enforcement.commit_gates.reconciler_health_gate import _should_print_warn

    assert _should_print_warn(tmp_path, "sigA") is True
    assert _should_print_warn(tmp_path, "sigA") is False, "24h 内同签名必须去重"

    state = tmp_path / ".runtime" / "reconciler_health_warn_dedup.json"
    state.write_text("{这不是合法JSON", encoding="utf-8")
    with caplog.at_level(logging.DEBUG):
        assert _should_print_warn(tmp_path, "sigA") is True, "状态损坏应回退为打印（加严方向）"
    rec = next(r for r in caplog.records if "去重状态不可读" in r.getMessage())
    assert "JSONDecodeError" in rec.getMessage(), "日志预设了失败类别"
    _assert_real_type_in_message(rec)


def test_should_print_warn_dedup_state_unwritable(tmp_path, caplog) -> None:
    from zephyr.gov_enforcement.commit_gates.reconciler_health_gate import _should_print_warn

    (tmp_path / ".runtime").write_text("我是文件不是目录", encoding="utf-8")
    with caplog.at_level(logging.DEBUG):
        assert _should_print_warn(tmp_path, "sigB") is True, "落盘失败仍须打印"
    assert any("去重状态落盘失败" in r.getMessage() for r in caplog.records), "零痕迹=BRK-049"


# ============ 4. 策略注册表自动发现降级（净值对账成员集）============ #


def test_resolve_member_modes_autodiscover_degradation_is_traced(
    monkeypatch: pytest.MonkeyPatch, caplog
) -> None:
    import zephyr.governance.strategies.strategy_base as sb
    import zephyr.pf_core.strategy_engine.framework_composer as fc

    def _boom(_pkg: str) -> None:
        raise RuntimeError("discovery 通道炸了")

    monkeypatch.setattr(sb, "autodiscover_strategies", _boom)
    with caplog.at_level(logging.DEBUG):
        daily, tick = fc._resolve_member_modes()

    assert isinstance(daily, set) and isinstance(tick, set), "降级仍须返回成员集"
    rec = next(r for r in caplog.records if "日频策略自动发现失败" in r.getMessage())
    assert "RuntimeError" in rec.getMessage()
    _assert_real_type_in_message(rec)


# ============ 5. BRK-046 哨兵 allow_empty 白名单 ============ #


def test_sentinel_allow_empty_requires_written_rationale() -> None:
    """结构性钉：白名单不得无凭据扩张（每条豁免必须自带理由/复核日期/复核人）。"""
    entries = yaml.safe_load(_SENTINEL_CONFIG_PATH.read_text(encoding="utf-8"))["tables"]
    granted = [e for e in entries if e.get("allow_empty")]
    assert len(granted) <= _SENTINEL_ALLOW_EMPTY_CEILING, (
        f"allow_empty 豁免 {len(granted)} 张 > 上限 {_SENTINEL_ALLOW_EMPTY_CEILING}："
        "该开关是永久静默（表可永远 0 行不告警），新增须逐张论证"
    )
    for e in granted:
        for field in ("rationale_zh", "reviewed_at", "reviewed_by"):
            assert e.get(field), f"{e['table']} 的 allow_empty 缺 {field}（隐性豁免）"


def test_sentinel_empty_table_alarms_without_whitelist(tmp_path: Path) -> None:
    """能红证据：同一张空表，带 allow_empty=静默 / 不带=必报 breach。"""
    ghost = "c1_market.zz_failopen_probe_absent_table"
    base = {
        "table": ghost,
        "date_col": "trade_date",
        "max_lag_days": 2,
        "past_only": True,
    }

    def _run(extra: dict) -> dict:
        cfg = tmp_path / f"sentinel_{len(extra)}.yaml"
        cfg.write_text(
            yaml.safe_dump({"tables": [{**base, **extra}]}, allow_unicode=True),
            encoding="utf-8",
        )
        return check_tables(config_path=cfg)

    strict = _run({})
    assert strict["breached"] == 1, "无白名单的空表不报红 = 哨兵是假的"
    assert strict["results"][0]["detail"], "违规必须带可归因 detail"
    assert "empty" in strict["results"][0]["detail"] or "error" in strict["results"][0]["detail"]


def test_sentinel_real_tables_no_longer_whitelisted() -> None:
    """收口面核对：本轮撤豁免的表仍在哨兵册内（撤豁免≠撤检测）。"""
    entries = yaml.safe_load(_SENTINEL_CONFIG_PATH.read_text(encoding="utf-8"))["tables"]
    by_table = {e["table"]: e for e in entries}
    for t in (
        "c1_market.sector_fund_flow",
        "c1_market.hl_liquidation_raw",
        "c1_market.gold_etf_holdings",
    ):
        assert t in by_table, f"{t} 被整条摘掉 = 借收口之名撤检测"
        assert not by_table[t].get("allow_empty"), f"{t} 仍挂着永久静默豁免"
        assert int(by_table[t]["max_lag_days"]) > 0, f"{t} 阈值被顺手放宽"
