# [BLUEPRINT] MOD-DATA_ENG | (pending)
# [MODULE] tests.zephyr.data.test_expectation_governance
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] zephyr.data_eng.expectation_governance
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存DataFrame+tmp_path存档，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=期望验证/门控逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""ExpectationGovernance 单元测试（CAND-DATENG-002 / B1-00607 min_build_spec）。

覆盖：
- 期望套件 YAML 加载（schema/非空/值域/分布/时效）
- 三档门控裁定：阻断(BLOCK)/降级(DEGRADE)/告警(WARN)/放行(OK)
- 验证报告存档 JSONL 可追溯
- CTR-001 NormalizedMarketData 契约字段联动
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from zephyr.data_eng.expectation_governance import (
    Expectation,
    ExpectationGovernance,
    GateVerdict,
)


def _market_df() -> pd.DataFrame:
    idx = pd.date_range("2026-08-20", periods=5, freq="D")
    return pd.DataFrame(
        {
            "symbol": ["600519.SH"] * 5,
            "open": [1700.0, 1701.0, 1702.0, 1703.0, 1704.0],
            "high": [1710.0] * 5,
            "low": [1690.0] * 5,
            "close": [1705.0, 1706.0, 1707.0, 1708.0, 1709.0],
            "volume": [1000.0] * 5,
            "timestamp": idx,
        },
        index=idx,
    )


class TestSuiteYaml:
    """期望套件 YAML 加载。"""

    def test_load_suite_yaml(self, tmp_path) -> None:
        suite_yaml = tmp_path / "suite.yaml"
        suite_yaml.write_text(
            "suite: market_data_daily\n"
            "expectations:\n"
            "  - type: schema\n"
            "    column: close\n"
            "    severity: block\n"
            "  - type: not_null\n"
            "    column: close\n"
            "    severity: block\n"
            "  - type: range\n"
            "    column: close\n"
            "    params: {min: 0}\n"
            "    severity: degrade\n"
            "  - type: distribution\n"
            "    column: volume\n"
            "    params: {mean_max: 100000}\n"
            "  - type: freshness\n"
            "    column: timestamp\n"
            "    params: {max_age_hours: 7200}\n",
            encoding="utf-8",
        )
        exps = ExpectationGovernance.load_suite(suite_yaml)
        assert len(exps) == 5
        assert exps[0].type == "schema"
        assert exps[0].severity == "block"
        assert exps[2].params["min"] == 0
        assert exps[4].type == "freshness"

    def test_load_suite_missing_expectations_key(self, tmp_path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("suite: x\n", encoding="utf-8")
        with pytest.raises(ValueError, match="expectations"):
            ExpectationGovernance.load_suite(bad)


class TestThreeTierGate:
    """阻断/降级/告警三档裁定。"""

    def test_all_pass_ok(self) -> None:
        gov = ExpectationGovernance()
        exps = [
            Expectation(type="schema", column="close"),
            Expectation(type="not_null", column="close"),
            Expectation(type="range", column="close", params={"min": 0}, severity="block"),
        ]
        report = gov.validate(_market_df(), exps, suite_name="s1")
        assert report.verdict == GateVerdict.OK
        assert all(r.passed for r in report.results)

    def test_block_severity_failure_blocks(self) -> None:
        gov = ExpectationGovernance()
        exps = [Expectation(type="schema", column="nonexistent_col", severity="block")]
        report = gov.validate(_market_df(), exps, suite_name="s1")
        assert report.verdict == GateVerdict.BLOCK

    def test_degrade_severity_failure_degrades(self) -> None:
        gov = ExpectationGovernance()
        exps = [Expectation(type="range", column="close", params={"min": 99999}, severity="degrade")]
        report = gov.validate(_market_df(), exps, suite_name="s1")
        assert report.verdict == GateVerdict.DEGRADE

    def test_warn_severity_failure_warns(self) -> None:
        gov = ExpectationGovernance()
        exps = [Expectation(type="distribution", column="volume", params={"mean_max": 1.0}, severity="warn")]
        report = gov.validate(_market_df(), exps, suite_name="s1")
        assert report.verdict == GateVerdict.WARN

    def test_block_dominates_degrade(self) -> None:
        gov = ExpectationGovernance()
        exps = [
            Expectation(type="schema", column="missing_a", severity="degrade"),
            Expectation(type="schema", column="missing_b", severity="block"),
        ]
        report = gov.validate(_market_df(), exps, suite_name="s1")
        assert report.verdict == GateVerdict.BLOCK

    def test_freshness_expectation(self) -> None:
        gov = ExpectationGovernance()
        stale = _market_df()
        exps = [Expectation(type="freshness", column="timestamp", params={"max_age_hours": 1}, severity="degrade")]
        report = gov.validate(stale, exps, suite_name="s1")
        assert report.verdict == GateVerdict.DEGRADE

    def test_not_null_failure(self) -> None:
        gov = ExpectationGovernance()
        df = _market_df()
        df.loc[df.index[0], "close"] = None
        exps = [Expectation(type="not_null", column="close", severity="block")]
        report = gov.validate(df, exps, suite_name="s1")
        assert report.verdict == GateVerdict.BLOCK
        assert report.results[0].passed is False


class TestReportArchive:
    """验证报告存档可追溯。"""

    def test_archive_jsonl(self, tmp_path) -> None:
        archive = tmp_path / "reports.jsonl"
        gov = ExpectationGovernance(archive_path=archive)
        exps = [Expectation(type="schema", column="close")]
        gov.validate(_market_df(), exps, suite_name="s1")
        gov.validate(_market_df(), exps, suite_name="s1")
        lines = archive.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        rec = json.loads(lines[0])
        assert rec["suite_name"] == "s1"
        assert rec["verdict"] == "ok"
        assert rec["row_count"] == 5
        assert "validated_at" in rec


class TestCtr001Linkage:
    """CTR-001 NormalizedMarketData 契约字段联动。"""

    def test_suite_from_ctr001_covers_required_fields(self) -> None:
        exps = ExpectationGovernance.suite_from_ctr001()
        cols = {e.column for e in exps if e.type == "schema"}
        # CTR-001 必填字段（无默认值）：close/data_source/high/low/open/symbol/timestamp/volume/idempotency_key
        for required in ("close", "open", "high", "low", "symbol", "timestamp", "volume"):
            assert required in cols
        # schema 期望应为 block 级（契约承重墙）
        assert all(e.severity == "block" for e in exps if e.type == "schema")

    def test_ctr001_suite_runs_on_market_df(self) -> None:
        gov = ExpectationGovernance()
        df = _market_df()  # 缺 data_source/idempotency_key → 契约 schema 失败
        report = gov.validate(df, ExpectationGovernance.suite_from_ctr001(), suite_name="ctr001")
        assert report.verdict == GateVerdict.BLOCK

    def test_unknown_expectation_type_rejected(self) -> None:
        gov = ExpectationGovernance()
        exps = [Expectation(type="magic_type", column="close")]
        with pytest.raises(ValueError, match="magic_type"):
            gov.validate(_market_df(), exps, suite_name="s1")
