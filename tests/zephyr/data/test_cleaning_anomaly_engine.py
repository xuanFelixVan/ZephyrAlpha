# [BLUEPRINT] MOD-DATA_ENG | (pending)
# [MODULE] tests.zephyr.data.test_cleaning_anomaly_engine
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] zephyr.data_eng.cleaning_anomaly_engine
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存DataFrame测试，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=清洗/修复逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""CleaningAnomalyEngine 单元测试（CAND-DATENG-001 / B1-00606 min_build_spec）。

覆盖：
- 清洗规则库五类检出：价格跳变/复权断点/重复bar/量能异常/缺失模式
- 自动修复策略：跨源仲裁 / 前值填充≤3根 / 超限剔除并标 quality_flag
- 修复审计日志闭环 + 人工审核队列
- 告警路由回调触发
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.data_eng.cleaning_anomaly_engine import (
    AnomalyRule,
    CleaningAnomalyEngine,
    RepairStrategy,
)


def _bars(closes, volumes=None, adj=None, freq="D") -> pd.DataFrame:
    idx = pd.date_range("2026-01-05", periods=len(closes), freq=freq)
    df = pd.DataFrame(
        {
            "open": closes,
            "high": [c * 1.01 for c in closes],
            "low": [c * 0.99 for c in closes],
            "close": closes,
            "volume": volumes if volumes is not None else [1000.0] * len(closes),
        },
        index=idx,
    )
    if adj is not None:
        df["adj_factor"] = adj
    return df


class TestDetectRules:
    """五类清洗规则检出。"""

    def test_clean_frame_no_findings(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.15, 10.3, 10.25])
        findings = eng.detect(df, symbol="600519.SH")
        assert findings == []

    def test_price_jump_detected(self) -> None:
        eng = CleaningAnomalyEngine()
        closes = [10.0, 10.1, 10.05, 10.1, 10.0, 10.05, 10.1, 10.0, 10.05, 10.1, 58.0, 10.05]
        findings = eng.detect(_bars(closes), symbol="600519.SH")
        rules = {f.rule for f in findings}
        assert AnomalyRule.PRICE_JUMP in rules

    def test_adj_break_detected(self) -> None:
        eng = CleaningAnomalyEngine()
        closes = [10.0, 10.1, 10.2, 10.1, 10.2, 10.1]
        adj = [1.0, 1.0, 1.0, 3.5, 3.5, 3.5]  # 复权因子突变 >2x
        findings = eng.detect(_bars(closes, adj=adj), symbol="600519.SH")
        assert any(f.rule == AnomalyRule.ADJ_BREAK for f in findings)

    def test_duplicate_bar_detected(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1])
        dup = df.iloc[[2]]
        df2 = pd.concat([df, dup]).sort_index()
        findings = eng.detect(df2, symbol="600519.SH")
        assert any(f.rule == AnomalyRule.DUPLICATE_BAR for f in findings)

    def test_volume_spike_detected(self) -> None:
        eng = CleaningAnomalyEngine()
        closes = [10.0] * 12
        volumes = [1000.0] * 11 + [9_000_000.0]
        findings = eng.detect(_bars(closes, volumes=volumes), symbol="600519.SH")
        assert any(f.rule == AnomalyRule.VOLUME_SPIKE for f in findings)

    def test_missing_pattern_detected(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1, 10.0, 10.1])
        df.loc[df.index[2], "close"] = None
        findings = eng.detect(df, symbol="600519.SH")
        assert any(f.rule == AnomalyRule.MISSING_PATTERN for f in findings)


class TestRepair:
    """自动修复三策略 + 审计 + 审核队列。"""

    def test_forward_fill_within_3_bars(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1, 10.0, 10.1, 10.2, 10.1])
        df.loc[df.index[3], "close"] = None
        df.loc[df.index[4], "close"] = None  # 连续2根缺失 ≤3
        result = eng.repair(df, symbol="600519.SH")
        assert result.data["close"].isna().sum() == 0
        filled = result.data.loc[df.index[3], "close"]
        assert filled == pytest.approx(10.2)  # 前值填充
        assert result.data.loc[df.index[3], "quality_flag"] == "filled"
        assert any(r.strategy == RepairStrategy.FORWARD_FILL for r in result.audit_log)
        assert result.review_queue == []

    def test_drop_and_flag_beyond_3_bars(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1, 10.0, 10.1, 10.2, 10.1, 10.0, 10.1])
        for i in range(3, 8):  # 连续5根缺失 >3
            df.loc[df.index[i], "close"] = None
        result = eng.repair(df, symbol="600519.SH")
        assert len(result.data) == 5  # 10 - 5 根被剔除
        assert any(r.strategy == RepairStrategy.DROP_AND_FLAG for r in result.audit_log)
        assert len(result.review_queue) == 5  # 剔除进人工审核队列

    def test_cross_source_arbitration(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1])
        df.loc[df.index[1], "close"] = None
        alt = _bars([10.0, 10.15, 10.2, 10.1])  # 备用源有值
        result = eng.repair(df, alt_source=alt, symbol="600519.SH")
        assert result.data.loc[df.index[1], "close"] == pytest.approx(10.15)
        assert result.data.loc[df.index[1], "quality_flag"] == "arbitrated"
        assert any(r.strategy == RepairStrategy.CROSS_SOURCE_ARBITRATE for r in result.audit_log)

    def test_audit_log_records_every_action(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1])
        df.loc[df.index[2], "close"] = None
        result = eng.repair(df, symbol="600519.SH")
        assert len(result.audit_log) == 1
        rec = result.audit_log[0]
        assert rec.symbol == "600519.SH"
        assert rec.strategy == RepairStrategy.FORWARD_FILL
        assert rec.timestamp == str(df.index[2])

    def test_alert_route_invoked_on_drop(self) -> None:
        calls: list[tuple[str, str, str]] = []
        eng = CleaningAnomalyEngine(alert_sink=lambda level, title, msg: calls.append((level, title, msg)))
        df = _bars([10.0, 10.1, 10.2, 10.1, 10.0, 10.1, 10.2, 10.1, 10.0, 10.1])
        for i in range(2, 7):  # 连续5根缺失 → 剔除
            df.loc[df.index[i], "close"] = None
        eng.repair(df, symbol="600519.SH")
        assert calls, "剔除动作应触发告警路由"
        assert any("600519.SH" in c[2] for c in calls)


class TestBoundaries:
    """边界与防御。"""

    def test_empty_frame(self) -> None:
        eng = CleaningAnomalyEngine()
        df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        assert eng.detect(df, symbol="X") == []
        result = eng.repair(df, symbol="X")
        assert result.data.empty
        assert result.audit_log == []

    def test_exactly_3_bars_fill_allowed(self) -> None:
        eng = CleaningAnomalyEngine()
        df = _bars([10.0, 10.1, 10.2, 10.1, 10.0, 10.1, 10.2, 10.1])
        for i in range(2, 5):  # 连续3根缺失 = 上限
            df.loc[df.index[i], "close"] = None
        result = eng.repair(df, symbol="600519.SH")
        assert len(result.data) == 8  # 不剔除
        assert result.data["close"].isna().sum() == 0
