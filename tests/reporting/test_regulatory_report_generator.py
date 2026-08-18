# [BLUEPRINT] MOD-RPT-006 | docs/03_modules/_domain_reporting/regulatory_report_generator/blueprint.md
# [MODULE] tests.reporting.test_regulatory_report_generator
# [DOMAIN] D_REPORTING
# [INVARIANTS] 4类报告(程序化交易/异常交易/持仓/绩效); data_hash=SHA-256(canonical_json(content)); 必填字段缺失拒绝; RegulatoryReport frozen不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRegulatoryReportError(ZA-RPT-0006)
# [TESTS] self
# [A_module] module_id=MOD-RPT-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-006 Regulatory Report Generator 单元测试.

覆盖（blueprint §9）:
  - 4类报告生成: programmatic_trading / abnormal_trading / position / performance
  - 完整性校验: validate_report 重算 data_hash 比对
  - 必填字段缺失: strategies/risk_rules/events/holdings/metrics 为空/缺失 → InvalidRegulatoryReportError
  - 数据篡改检测: 改 content → validate_report 返回 False
  - data_hash 计算: SHA-256(canonical_json(content)), 确定性
  - RegulatoryReport frozen 不可变
  - 边界值: 空 period/portfolio_id / 绩效必填指标缺失 / 持仓集中度计算 / 行业分布
  - report_id 格式: REG-<TYPE前缀>-<hex10>
  - schema_version / report_type 枚举
  - 同输入→相同 data_hash (确定性)
  - 不同输入→不同 data_hash
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import pytest

from zephyr.reporting.regulatory_report_generator import (
    InvalidRegulatoryReportError,
    RegulatoryReport,
    RegulatoryReportGenerator,
    ReportType,
    _canonical_json,
    _compute_data_hash,
)

# ── 程序化交易报告测试 ──


class TestProgrammaticTradingReport:
    def test_generate_basic(self) -> None:
        """生成程序化交易报告——基本字段正确。"""
        gen = RegulatoryReportGenerator()
        strategies = [
            {"name": "momentum", "parameters": {"lookback": 20}, "status": "active"},
            {"name": "mean_reversion", "parameters": {"window": 10}, "status": "testing"},
        ]
        risk_rules = [
            {"name": "max_position", "threshold": 0.1, "action": "reject"},
        ]
        report = gen.generate_programmatic_trading(
            portfolio_id="PF-001",
            reporting_period="2026-Q3",
            strategies=strategies,
            risk_rules=risk_rules,
        )
        assert report.report_type == ReportType.PROGRAMMATIC_TRADING
        assert report.portfolio_id == "PF-001"
        assert report.reporting_period == "2026-Q3"
        assert report.content["report_category"] == "programmatic_trading"
        assert report.content["strategy_count"] == 2
        assert report.content["risk_rule_count"] == 1
        assert report.content["strategies"] == strategies
        assert report.content["risk_rules"] == risk_rules
        assert report.schema_version == "1.0"
        assert report.report_id.startswith("REG-PRO-")

    def test_generate_data_hash_matches_content(self) -> None:
        """data_hash = SHA-256(canonical_json(content))。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_programmatic_trading(
            "PF-001", "2026",
            strategies=[{"name": "s1", "parameters": {}, "status": "active"}],
            risk_rules=[{"name": "r1", "threshold": 0.1, "action": "warn"}],
        )
        expected = hashlib.sha256(
            _canonical_json(report.content).encode("utf-8")
        ).hexdigest()
        assert report.data_hash == expected

    def test_missing_strategies_raises(self) -> None:
        """strategies 为空列表 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError) as exc:
            gen.generate_programmatic_trading(
                "PF-001", "2026",
                strategies=[],
                risk_rules=[{"name": "r1", "threshold": 0.1, "action": "warn"}],
            )
        assert "strategies" in str(exc.value)

    def test_missing_risk_rules_raises(self) -> None:
        """risk_rules 为空列表 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError) as exc:
            gen.generate_programmatic_trading(
                "PF-001", "2026",
                strategies=[{"name": "s1", "parameters": {}, "status": "active"}],
                risk_rules=[],
            )
        assert "risk_rules" in str(exc.value)

    def test_empty_portfolio_id_raises(self) -> None:
        """portfolio_id 为空 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_programmatic_trading(
                "  ", "2026",
                strategies=[{"name": "s1"}],
                risk_rules=[{"name": "r1"}],
            )


# ── 异常交易自报测试 ──


class TestAbnormalTradingReport:
    def test_generate_basic(self) -> None:
        """生成异常交易自报——基本字段正确。"""
        gen = RegulatoryReportGenerator()
        events = [
            {
                "event_type": "price_spike",
                "trigger": "price +10% in 1min",
                "action": "paused",
                "timestamp": "2026-08-01T10:30:00Z",
            },
            {
                "event_type": "volume_anomaly",
                "trigger": "volume > 5x avg",
                "action": "alerted",
                "timestamp": "2026-08-01T14:00:00Z",
            },
        ]
        report = gen.generate_abnormal_trading(
            portfolio_id="PF-002",
            reporting_period="2026-08",
            events=events,
        )
        assert report.report_type == ReportType.ABNORMAL_TRADING
        assert report.content["report_category"] == "abnormal_trading"
        assert report.content["event_count"] == 2
        assert set(report.content["event_types"]) == {"price_spike", "volume_anomaly"}

    def test_dedup_event_types(self) -> None:
        """event_types 去重。"""
        gen = RegulatoryReportGenerator()
        events = [
            {"event_type": "price_spike", "trigger": "t1", "action": "a1"},
            {"event_type": "price_spike", "trigger": "t2", "action": "a2"},
            {"event_type": "volume_anomaly", "trigger": "t3", "action": "a3"},
        ]
        report = gen.generate_abnormal_trading("PF-001", "2026-08", events)
        assert sorted(report.content["event_types"]) == ["price_spike", "volume_anomaly"]

    def test_missing_events_raises(self) -> None:
        """events 为空 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_abnormal_trading("PF-001", "2026-08", events=[])

    def test_event_type_unknown_when_missing(self) -> None:
        """event 缺 event_type → 归为 'unknown'。"""
        gen = RegulatoryReportGenerator()
        events = [{"trigger": "t1", "action": "a1"}]
        report = gen.generate_abnormal_trading("PF-001", "2026-08", events)
        assert "unknown" in report.content["event_types"]


# ── 持仓报告测试 ──


class TestPositionReport:
    def test_generate_basic(self) -> None:
        """生成持仓报告——集中度+行业分布计算正确。"""
        gen = RegulatoryReportGenerator()
        holdings = [
            {"symbol": "600519", "quantity": 100, "market_value": 200000, "sector": "consumer"},
            {"symbol": "000858", "quantity": 200, "market_value": 100000, "sector": "consumer"},
            {"symbol": "601318", "quantity": 300, "market_value": 150000, "sector": "finance"},
        ]
        report = gen.generate_position(
            portfolio_id="PF-001",
            reporting_period="2026-08",
            holdings=holdings,
        )
        assert report.report_type == ReportType.POSITION
        assert report.content["holding_count"] == 3
        assert report.content["total_market_value"] == 450000
        # 最大持仓占比 = 200000 / 450000
        assert report.content["top_position_concentration"] == pytest.approx(200000 / 450000)
        # 行业集中度: consumer = 300000/450000, finance = 150000/450000
        sectors = report.content["sector_concentrations"]
        assert sectors["consumer"] == pytest.approx(300000 / 450000)
        assert sectors["finance"] == pytest.approx(150000 / 450000)

    def test_concentration_single_holding(self) -> None:
        """单一持仓——集中度=1.0。"""
        gen = RegulatoryReportGenerator()
        holdings = [{"symbol": "600519", "quantity": 100, "market_value": 500000, "sector": "consumer"}]
        report = gen.generate_position("PF-001", "2026-08", holdings)
        assert report.content["top_position_concentration"] == 1.0
        assert report.content["sector_concentrations"]["consumer"] == 1.0

    def test_missing_holdings_raises(self) -> None:
        """holdings 为空 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_position("PF-001", "2026-08", holdings=[])

    def test_missing_sector_defaults_unknown(self) -> None:
        """holdings 缺 sector → 归为 'unknown'。"""
        gen = RegulatoryReportGenerator()
        holdings = [{"symbol": "600519", "quantity": 100, "market_value": 100000}]
        report = gen.generate_position("PF-001", "2026-08", holdings)
        assert "unknown" in report.content["sector_concentrations"]

    def test_zero_market_value_safe(self) -> None:
        """所有持仓 market_value=0 → 集中度=0, 不除零。"""
        gen = RegulatoryReportGenerator()
        holdings = [
            {"symbol": "A", "quantity": 0, "market_value": 0, "sector": "x"},
            {"symbol": "B", "quantity": 0, "market_value": 0, "sector": "y"},
        ]
        report = gen.generate_position("PF-001", "2026-08", holdings)
        assert report.content["total_market_value"] == 0
        assert report.content["top_position_concentration"] == 0.0
        assert report.content["sector_concentrations"] == {}


# ── 绩效报告测试 ──


class TestPerformanceReport:
    def test_generate_basic(self) -> None:
        """生成绩效报告——必填指标 + 归因摘要。"""
        gen = RegulatoryReportGenerator()
        metrics = {
            "return_pct": 12.5,
            "max_drawdown": -8.3,
            "sharpe_ratio": 1.8,
            "sortino_ratio": 2.1,
            "attribution_summary": {"stock_selection": 5.0, "timing": 7.5},
        }
        report = gen.generate_performance(
            portfolio_id="PF-001",
            reporting_period="2026-Q3",
            metrics=metrics,
        )
        assert report.report_type == ReportType.PERFORMANCE
        assert report.content["return_pct"] == 12.5
        assert report.content["max_drawdown"] == -8.3
        assert report.content["sharpe_ratio"] == 1.8
        assert report.content["metrics"] == metrics

    def test_missing_return_pct_raises(self) -> None:
        """缺 return_pct → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError) as exc:
            gen.generate_performance(
                "PF-001", "2026-Q3",
                metrics={"max_drawdown": -5.0, "sharpe_ratio": 1.5},
            )
        assert "return_pct" in str(exc.value)

    def test_missing_max_drawdown_raises(self) -> None:
        """缺 max_drawdown → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_performance(
                "PF-001", "2026-Q3",
                metrics={"return_pct": 10.0, "sharpe_ratio": 1.5},
            )

    def test_missing_sharpe_ratio_raises(self) -> None:
        """缺 sharpe_ratio → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_performance(
                "PF-001", "2026-Q3",
                metrics={"return_pct": 10.0, "max_drawdown": -5.0},
            )

    def test_empty_metrics_raises(self) -> None:
        """metrics 为空 dict → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_performance("PF-001", "2026-Q3", metrics={})


# ── 完整性校验测试 ──


class TestValidateReport:
    def test_valid_report_passes(self) -> None:
        """未篡改的报告 → validate_report 返回 True。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "600519", "quantity": 100, "market_value": 200000, "sector": "consumer"}],
        )
        assert gen.validate_report(report) is True

    def test_tampered_content_fails(self) -> None:
        """篡改 content → validate_report 返回 False。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "600519", "quantity": 100, "market_value": 200000, "sector": "consumer"}],
        )
        # 用 dataclasses.replace 构造篡改版本（frozen 不可直接改）
        tampered = dataclasses.replace(
            report,
            content={**report.content, "total_market_value": 999999},
        )
        assert gen.validate_report(tampered) is False

    def test_all_report_types_validate(self) -> None:
        """4类报告都通过完整性校验。"""
        gen = RegulatoryReportGenerator()
        r1 = gen.generate_programmatic_trading(
            "PF-001", "2026",
            strategies=[{"name": "s1"}],
            risk_rules=[{"name": "r1"}],
        )
        r2 = gen.generate_abnormal_trading(
            "PF-001", "2026",
            events=[{"event_type": "x", "trigger": "t", "action": "a"}],
        )
        r3 = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
        )
        r4 = gen.generate_performance(
            "PF-001", "2026",
            metrics={"return_pct": 1.0, "max_drawdown": -1.0, "sharpe_ratio": 1.0},
        )
        for r in (r1, r2, r3, r4):
            assert gen.validate_report(r) is True


# ── data_hash 确定性测试 ──


class TestDataHashDeterminism:
    def test_same_input_same_hash(self) -> None:
        """同输入 → 相同 data_hash（确定性）。"""
        gen = RegulatoryReportGenerator()
        kwargs = dict(
            portfolio_id="PF-001",
            reporting_period="2026",
            strategies=[{"name": "s1", "parameters": {"a": 1}, "status": "active"}],
            risk_rules=[{"name": "r1", "threshold": 0.1, "action": "warn"}],
        )
        r1 = gen.generate_programmatic_trading(**kwargs)
        r2 = gen.generate_programmatic_trading(**kwargs)
        # report_id 不同（UUID），但 data_hash 相同
        assert r1.data_hash == r2.data_hash
        assert r1.report_id != r2.report_id

    def test_different_input_different_hash(self) -> None:
        """不同输入 → 不同 data_hash。"""
        gen = RegulatoryReportGenerator()
        r1 = gen.generate_performance(
            "PF-001", "2026",
            metrics={"return_pct": 10.0, "max_drawdown": -5.0, "sharpe_ratio": 1.5},
        )
        r2 = gen.generate_performance(
            "PF-001", "2026",
            metrics={"return_pct": 11.0, "max_drawdown": -5.0, "sharpe_ratio": 1.5},
        )
        assert r1.data_hash != r2.data_hash

    def test_canonical_json_sort_keys(self) -> None:
        """canonical_json 用 sort_keys 确保确定性。"""
        # 键顺序不同但内容相同 → 相同 hash
        c1 = {"b": 2, "a": 1}
        c2 = {"a": 1, "b": 2}
        assert _compute_data_hash(c1) == _compute_data_hash(c2)

    def test_data_hash_is_sha256_hex(self) -> None:
        """data_hash 是 64 位 hex 字符串（SHA-256）。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_performance(
            "PF-001", "2026",
            metrics={"return_pct": 1.0, "max_drawdown": -1.0, "sharpe_ratio": 1.0},
        )
        assert len(report.data_hash) == 64
        int(report.data_hash, 16)  # 合法 hex


# ── 不可变性测试 ──


class TestImmutability:
    def test_regulatory_report_is_frozen(self) -> None:
        """RegulatoryReport frozen——不可修改字段赋值。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
        )
        # frozen dataclass 阻止字段重新赋值
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.portfolio_id = "PF-999"  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.data_hash = "fake"  # type: ignore[misc]

    def test_report_type_enum_values(self) -> None:
        """ReportType 4个枚举值正确。"""
        assert ReportType.PROGRAMMATIC_TRADING.value == "programmatic_trading"
        assert ReportType.ABNORMAL_TRADING.value == "abnormal_trading"
        assert ReportType.POSITION.value == "position"
        assert ReportType.PERFORMANCE.value == "performance"


# ── report_id / 元数据测试 ──


class TestReportIdAndMetadata:
    def test_report_id_format(self) -> None:
        """report_id 格式: REG-<TYPE前缀>-<hex10>。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
        )
        # REG-POS-<10 hex chars>
        assert report.report_id.startswith("REG-POS-")
        hex_part = report.report_id.split("REG-POS-")[1]
        assert len(hex_part) == 10
        int(hex_part, 16)  # 合法 hex

    def test_report_id_prefixes_per_type(self) -> None:
        """4类报告的 report_id 前缀正确。"""
        gen = RegulatoryReportGenerator()
        r1 = gen.generate_programmatic_trading(
            "PF-001", "2026",
            strategies=[{"name": "s1"}],
            risk_rules=[{"name": "r1"}],
        )
        r2 = gen.generate_abnormal_trading(
            "PF-001", "2026",
            events=[{"event_type": "x"}],
        )
        r3 = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
        )
        r4 = gen.generate_performance(
            "PF-001", "2026",
            metrics={"return_pct": 1.0, "max_drawdown": -1.0, "sharpe_ratio": 1.0},
        )
        assert r1.report_id.startswith("REG-PRO-")
        assert r2.report_id.startswith("REG-ABN-")
        assert r3.report_id.startswith("REG-POS-")
        assert r4.report_id.startswith("REG-PER-")

    def test_generated_at_is_utc(self) -> None:
        """generated_at 为 UTC 时间。"""
        gen = RegulatoryReportGenerator()
        before = datetime.now(UTC)
        report = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
        )
        after = datetime.now(UTC)
        assert report.generated_at.tzinfo is not None
        assert before <= report.generated_at <= after

    def test_schema_version(self) -> None:
        """schema_version = "1.0"。"""
        gen = RegulatoryReportGenerator()
        report = gen.generate_position(
            "PF-001", "2026-08",
            holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
        )
        assert report.schema_version == "1.0"


# ── 边界值 / 错误契约测试 ──


class TestEdgeCases:
    def test_empty_reporting_period_raises(self) -> None:
        """reporting_period 为空 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_position(
                "PF-001", "  ",
                holdings=[{"symbol": "A", "quantity": 1, "market_value": 100, "sector": "x"}],
            )

    def test_empty_portfolio_id_raises_abnormal(self) -> None:
        """abnormal 报告 portfolio_id 为空 → 拒绝。"""
        gen = RegulatoryReportGenerator()
        with pytest.raises(InvalidRegulatoryReportError):
            gen.generate_abnormal_trading(
                "", "2026",
                events=[{"event_type": "x"}],
            )

    def test_error_code_is_za_rpt_0006(self) -> None:
        """InvalidRegulatoryReportError.error_code = ZA-RPT-0006。"""
        assert InvalidRegulatoryReportError.error_code == "ZA-RPT-0006"

    def test_generator_has_no_external_state(self) -> None:
        """RegulatoryReportGenerator 无外部状态——多次实例化互不影响。"""
        gen1 = RegulatoryReportGenerator()
        gen2 = RegulatoryReportGenerator()
        kwargs = dict(
            portfolio_id="PF-001",
            reporting_period="2026",
            strategies=[{"name": "s1"}],
            risk_rules=[{"name": "r1"}],
        )
        r1 = gen1.generate_programmatic_trading(**kwargs)
        r2 = gen2.generate_programmatic_trading(**kwargs)
        assert r1.data_hash == r2.data_hash

    def test_content_copied_not_referenced(self) -> None:
        """content 顶层是 dict 副本——外部修改原 metrics 后, data_hash 检测到篡改。"""
        gen = RegulatoryReportGenerator()
        metrics = {"return_pct": 10.0, "max_drawdown": -5.0, "sharpe_ratio": 1.5}
        report = gen.generate_performance("PF-001", "2026", metrics=metrics)
        # 顶层值字段是值拷贝, 不受原 dict 修改影响
        assert report.content["return_pct"] == 10.0
        # 嵌套 metrics 是浅拷贝引用——修改原 dict 会传播到 report.content["metrics"]
        # 但 data_hash 在生成时已固定, 因此 validate_report 会检测到篡改
        metrics["return_pct"] = 999.0
        assert report.content["metrics"]["return_pct"] == 999.0  # 浅拷贝传播
        assert gen.validate_report(report) is False  # 篡改被检测
