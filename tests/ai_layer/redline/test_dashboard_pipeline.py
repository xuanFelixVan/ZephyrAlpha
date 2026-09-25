# [A_test] module_id: zephyr.ai_layer.redline.dashboard_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_dual_metric_dashboard
# [MODULE] tests.ai_layer.redline.test_dashboard_pipeline
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.dashboard_pipeline; schemas.categories.ai_cost_daily
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_dashboard_pipeline.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：S5 看板=双指标日更且数据源可追溯
#              （行供给注入+阈值真源注入 tmp_path，零连库零生产路径写）；
#              热加载用 os.utime 显式推 mtime（Windows mtime 精度规避）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_dashboard_pipeline.py — S5 双指标看板数据链单测（阈值/回撤/降档/恢复/DDL 形状）。"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from schemas.categories.ai_cost_daily import DDL, TABLE_NAME
from zephyr.ai_layer.redline.dashboard_pipeline import (
    DegradationConfig,
    DegradationConfigError,
    Thresholds,
    dashboard_snapshot,
    degrade_event_payload,
    estimate_daily_cost,
    evaluate_degradation,
    parse_thresholds,
    portfolio_drawdown,
    recovery_allowed,
)
from zephyr.shared.io.paths import REPO_ROOT

CONFIG_TEXT = (
    "cost_daily:\n"
    "  currency: CNY\n"
    "  soft_yuan: 200.0\n"
    "  hard_yuan: 500.0\n"
    "drawdown_pct:\n"
    "  attention_pct: 5.0\n"
    "  degrade_pct: 10.0\n"
    "recovery:\n"
    "  consecutive_days: 3\n"
    "hysteresis:\n"
    "  confirmation_count: 2\n"
    "  cooldown_seconds: 60.0\n"
    "  oscillation_threshold_per_hour: 3\n"
)


def _write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "obj_s_degradation.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _thresholds() -> Thresholds:
    return Thresholds(200.0, 500.0, 5.0, 10.0)


def test_parse_thresholds_and_missing_keys_fail_closed(tmp_path: Path):
    thresholds = parse_thresholds(
        {
            "cost_daily": {"soft_yuan": 1.0, "hard_yuan": 2.0},
            "drawdown_pct": {"attention_pct": 3.0, "degrade_pct": 4.0},
        }
    )
    assert (thresholds.cost_soft_yuan, thresholds.cost_hard_yuan) == (1.0, 2.0)
    assert thresholds.confirmation_count == 2, "缺省滞回值=先例原值兜底"
    with pytest.raises(DegradationConfigError):
        parse_thresholds({"cost_daily": {"soft_yuan": 1.0}})


def test_production_config_loads():
    """生产阈值真源可加载（只读验证初值预注册面完整）。"""
    config = DegradationConfig(REPO_ROOT / "config" / "obj_s_degradation.yaml")
    assert config.thresholds.cost_hard_yuan > config.thresholds.cost_soft_yuan
    assert config.thresholds.drawdown_degrade_pct > config.thresholds.drawdown_attention_pct


def test_hot_reload_mtime_change(tmp_path: Path):
    path = _write_config(tmp_path, CONFIG_TEXT)
    config = DegradationConfig(path)
    assert config.thresholds.cost_hard_yuan == 500.0
    updated = CONFIG_TEXT.replace("hard_yuan: 500.0", "hard_yuan: 900.0")
    path.write_text(updated, encoding="utf-8")
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns + 2_000_000, stat.st_mtime_ns + 2_000_000))
    assert config.reload_if_changed() is True
    assert config.thresholds.cost_hard_yuan == 900.0
    assert config.reload_if_changed() is False, "mtime 未变不重载"


def test_hot_reload_bad_file_keeps_last_good(tmp_path: Path):
    path = _write_config(tmp_path, CONFIG_TEXT)
    config = DegradationConfig(path)
    assert config.thresholds.cost_hard_yuan == 500.0, "先强制首载（惰性加载的好配置基线）"
    path.write_text("cost_daily: [broken\n", encoding="utf-8")
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns + 2_000_000, stat.st_mtime_ns + 2_000_000))
    assert config.reload_if_changed() is False, "坏重载保留上一份好配置"
    assert config.thresholds.cost_hard_yuan == 500.0


def test_portfolio_drawdown_known_values():
    rows = [
        {"trade_date": "2026-09-01", "strategy_id": "S1", "equity": 100.0},
        {"trade_date": "2026-09-01", "strategy_id": "S2", "equity": 50.0},
        {"trade_date": "2026-09-02", "strategy_id": "S1", "equity": 90.0},
        {"trade_date": "2026-09-02", "strategy_id": "S2", "equity": 50.0},
        {"trade_date": "2026-09-03", "strategy_id": "S1", "equity": 120.0},
        {"trade_date": "2026-09-03", "strategy_id": "S2", "equity": 30.0},
    ]
    report = portfolio_drawdown(rows)
    assert report.days_evaluated == 3
    assert report.high_water_mark == pytest.approx(150.0)  # 09-03: 120+30
    assert report.portfolio_equity_latest == pytest.approx(150.0)
    # 09-02 组合 140 vs HWM 150 → 回撤 6.67%（max）
    assert report.max_drawdown_pct == pytest.approx(100.0 * 10 / 150)
    assert report.current_drawdown_pct == pytest.approx(0.0)


def test_portfolio_drawdown_skips_bad_rows_and_empty():
    report = portfolio_drawdown(
        [
            {"trade_date": "bad-date", "strategy_id": "S1", "equity": 1.0},
            {"trade_date": "2026-09-01", "strategy_id": "S1", "equity": "oops"},
            {"trade_date": "2026-09-01", "strategy_id": "S2", "equity": 100.0},
        ]
    )
    assert report.skipped_rows == 2
    assert report.portfolio_equity_latest == pytest.approx(100.0)
    empty = portfolio_drawdown([])
    assert empty.days_evaluated == 0 and empty.current_drawdown_pct == 0.0


def test_evaluate_degradation_three_tiers():
    t = _thresholds()
    normal = evaluate_degradation(100.0, 1.0, t)
    assert normal.tier == "normal" and normal.actions == ()
    attention = evaluate_degradation(300.0, 1.0, t)
    assert attention.tier == "attention" and attention.actions == ("alert_yellow",)
    degrade = evaluate_degradation(100.0, 12.0, t)
    assert degrade.tier == "degrade"
    assert degrade.actions == ("heavy_pause", "cheap_model_fallback", "mining_pause"), (
        "降档动作按序生效（DESIGN §4 联动表）"
    )
    both = evaluate_degradation(600.0, 12.0, t)
    assert len(both.triggered_by) == 2


def test_recovery_allowed_hysteresis_three_pieces():
    t = _thresholds()
    assert recovery_allowed(3, 120.0, 1, t) is True
    assert recovery_allowed(2, 120.0, 1, t) is False, "回线天数不足（max(N, confirmation_count)）"
    assert recovery_allowed(3, 30.0, 1, t) is False, "cooldown 未过"
    assert recovery_allowed(3, 120.0, 3, t) is False, "每小时振荡已达上限 3 次"
    assert recovery_allowed(3, 120.0, 2, t) is True


def test_degrade_event_payload_shape():
    verdict = evaluate_degradation(600.0, 1.0, _thresholds())
    payload = degrade_event_payload(verdict)
    assert payload["event"] == "degrade_model_tier"
    assert payload["target_route"] == "flash_fallback"
    assert payload["issued_at"], "时间戳经 now_utc（禁 datetime.now）"


def test_dashboard_snapshot_shape():
    report = portfolio_drawdown([{"trade_date": "2026-09-01", "strategy_id": "S1", "equity": 100.0}])
    snapshot = dashboard_snapshot(300.0, report, _thresholds())
    assert snapshot["tier"] == "attention"
    assert snapshot["thresholds"]["cost_hard_yuan"] == 500.0
    assert snapshot["snapshot_at"]


def test_estimate_daily_cost_fallback():
    total, unknown = estimate_daily_cost(
        {"DEEPSEEK": (1_000_000, 0), "GLM": (0, 500_000), "MYSTERY": (10, 10)},
        {"DEEPSEEK": (0.002, 0.008), "GLM": (0.004, 0.012)},
    )
    assert total == pytest.approx(2.0 + 6.0)
    assert unknown == ["MYSTERY"], "无价渠道跳过并列出（不虚构单价）"


def test_cost_daily_ddl_shape():
    """DDL 真源形状钉扎：库表名/ReplacingMergeTree/ORDER BY/显式时区（RULE-SCHEMA-TZ）。"""
    assert TABLE_NAME == "c1_backtest.ai_cost_daily"
    assert "CREATE TABLE IF NOT EXISTS c1_backtest.ai_cost_daily" in DDL
    assert "ReplacingMergeTree" in DDL
    assert "ORDER BY (cost_date, channel, cost_source)" in DDL
    assert "DateTime64(3, 'UTC')" in DDL
    assert "cost_source" in DDL, "口径来源字段（bill_api/telemetry_est 可追溯）"
