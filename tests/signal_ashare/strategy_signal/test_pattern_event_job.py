# [BLUEPRINT] MOD-SIG-145 | docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md
# [MODULE] tests.signal_ashare.strategy_signal.test_pattern_event_job
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_event_job; zephyr.data.provider_base.FetchResult
# [CONSUMERS] pytest（JOB-108 接线适配层单元测试）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 全程打桩 subprocess（不触库不出网）；断言焦点=退出码透传/UTF-8 解码假设/记账 rows_fetched 语义/解析降级不炸
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] self
# [A_module] module_id=MOD-SIG-145 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pattern_event_job 薄适配单元测试（MOD-SIG-145 W4b，JOB-108）。

适配层契约：subprocess 退出码→FetchResult.error；stdout JSON/行数解析→
rows_fetched 记账；解析失败降级 0 不炸。扫描器真身在 scripts/data，此处
全部打桩（SimpleNamespace 模拟 CompletedProcess），零库零网络。
"""

from __future__ import annotations

import json
import types

import pytest

from zephyr.signal_ashare.strategy_signal import pattern_event_job as pej


def _fake_run(returncode: int, stdout: str):
    def _run(cmd, **kwargs):
        assert kwargs.get("encoding") == "utf-8", "子进程 stdout 必须显式 UTF-8（Windows GBK 坑）"
        return types.SimpleNamespace(returncode=returncode, stdout=stdout)
    return _run


@pytest.fixture()
def stub_subprocess(monkeypatch):
    """打桩 pattern_event_job 命名空间内的 subprocess.run，记录调用参数。"""
    calls: list[dict] = []

    def _install(returncode: int, stdout: str):
        def _run(cmd, **kwargs):
            calls.append({"cmd": cmd, "kwargs": kwargs})
            return types.SimpleNamespace(returncode=returncode, stdout=stdout)
        monkeypatch.setattr(pej.subprocess, "run", _run)
        return calls

    return _install


class TestRunIncremental:
    def test_success_yields_accounting_result(self, stub_subprocess):
        summary = json.dumps({"events": 42, "errors": 0}, ensure_ascii=False)
        calls = stub_subprocess(0, f"INFO 进度日志行\n{summary}\n")

        results = list(pej.run_incremental())
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert r.rows == []
        assert r.rows_fetched == 42, "记账=扫描器实产事件数（0 行 WARN 抑制依赖此值）"
        assert r.last_key  # 游标推进需要非空 last_key
        assert r.table == "c1_market.market_pattern_event"

        cmd = calls[0]["cmd"]
        assert any(a.endswith("pattern_event_backfill.py") for a in cmd)
        assert "--data-source" in cmd and cmd[cmd.index("--data-source") + 1] == "pattern_event_incremental"
        # 产出窗口起点与上下文起点都存在且为 ISO 日期
        emit_from = cmd[cmd.index("--emit-from") + 1]
        start = cmd[cmd.index("--start") + 1]
        assert len(emit_from) == 10 and len(start) == 10
        assert start < emit_from, "上下文窗必须早于产出窗"

    def test_zero_events_keeps_zero_accounting(self, stub_subprocess):
        summary = json.dumps({"events": 0}, ensure_ascii=False)
        stub_subprocess(0, f"{summary}\n")
        (r,) = list(pej.run_incremental())
        assert r.rows_fetched == 0
        assert r.error is None

    def test_failure_propagates_exit_code_as_error(self, stub_subprocess):
        stub_subprocess(3, "")
        (r,) = list(pej.run_incremental())
        assert r.error is not None
        assert "3" in r.error
        assert r.rows == []


class TestRunWinRateMaterialize:
    def test_success_parses_ok_line(self, stub_subprocess):
        stub_subprocess(0, "INFO 窗口 1 物化 1000 行\nOK: 物化 4309 行 -> c1_market.market_pattern_win_rate\n")
        results = list(pej.run_win_rate_materialize())
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert r.rows_fetched == 4309
        assert r.table == "c1_market.market_pattern_win_rate"

    def test_failure_propagates_exit_code(self, stub_subprocess):
        stub_subprocess(1, "")
        (r,) = list(pej.run_win_rate_materialize())
        assert r.error is not None and "1" in r.error


class TestParsers:
    def test_summary_events_normal(self):
        line = json.dumps({"events": 7}, ensure_ascii=False)
        assert pej._parse_summary_events(line) == 7

    def test_summary_events_degrades_to_zero(self):
        assert pej._parse_summary_events("not json at all") == 0
        assert pej._parse_summary_events('{"events": null}') == 0
        assert pej._parse_summary_events("") == 0

    def test_materialized_rows_normal(self):
        assert pej._parse_materialized_rows("OK: 物化 123 行 -> t") == 123

    def test_materialized_rows_degrades_to_zero(self):
        assert pej._parse_materialized_rows("garbage") == 0
        assert pej._parse_materialized_rows("") == 0


class TestFetchResultAccounting:
    def test_explicit_rows_fetched_survives_post_init(self):
        r = pej.FetchResult(
            table="t", columns=[], rows=[], last_key="2026-09-14",
            elapsed_sec=0.0, rows_fetched=99,
        )
        assert r.rows_fetched == 99, "post_init 不得覆盖显式记账值"


# ── 消费班 W-C3：run_weight_sync（物化完成→调权钩子） ────────────────────────


def test_run_weight_sync_ok(monkeypatch):
    """退出码 0：解析尾行 JSON summary 的 adjusted 记账，error=None。"""
    monkeypatch.setattr(
        pej.subprocess, "run",
        _fake_run(0, '{"patterns": 5, "adjusted": 3, "weights": {"双顶": 0.8}}'),
    )
    results = list(pej.run_weight_sync())
    assert len(results) == 1
    r = results[0]
    assert r.error is None
    assert r.rows_fetched == 3
    assert r.table == pej._WIN_RATE_TABLE


def test_run_weight_sync_failure_passthrough(monkeypatch):
    """退出码非 0：error 透传（scheduler 记 FAILED），rows_fetched=0。"""
    monkeypatch.setattr(pej.subprocess, "run", _fake_run(2, ""))
    results = list(pej.run_weight_sync())
    assert len(results) == 1
    r = results[0]
    assert r.error is not None and "退出码 2" in r.error
    assert r.rows_fetched == 0


def test_run_weight_sync_parse_degrade(monkeypatch):
    """stdout 无 JSON summary：记账降级 0 不炸（结果以状态文件为准）。"""
    monkeypatch.setattr(pej.subprocess, "run", _fake_run(0, "no-json-here"))
    results = list(pej.run_weight_sync())
    assert results[0].rows_fetched == 0
    assert results[0].error is None


# ── 消费班 W-CB：run_evidence_certify（物化→认证钩子） ───────────────────────


def test_run_evidence_certify_ok(monkeypatch):
    """退出码 0：解析尾行 JSON summary 的 total 记账，error=None。"""
    monkeypatch.setattr(
        pej.subprocess, "run",
        _fake_run(0, '{"family": "day/向上/10d", "total": 400, "written": 400, "counts": {"certified": 12}}'),
    )
    results = list(pej.run_evidence_certify())
    assert len(results) == 1
    r = results[0]
    assert r.error is None
    assert r.rows_fetched == 400
    assert r.table == pej._CERT_TABLE


def test_run_evidence_certify_failure_passthrough(monkeypatch):
    monkeypatch.setattr(pej.subprocess, "run", _fake_run(3, ""))
    results = list(pej.run_evidence_certify())
    assert results[0].error is not None and "退出码 3" in results[0].error
