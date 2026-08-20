# [BLUEPRINT] MOD-EX-049 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-EXE-daban_pit_safety_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_pit_safety
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板 PIT 安全族单元测试（§3.13 缺失#5 get_dragon_tiger_pit / §3.14 缺失#10 DabanPITBacktestFramework）。

覆盖：
  - get_dragon_tiger_pit：查询边界 latest=T-1 / 逐行 PIT 断言（违规→AssertionError）/
    空结果 / dict 化输出
  - assert_pit：dragon_tiger T 日数据用于 T 日决策→违规；T-1→放行 /
    next_day_auction 未来数据→违规；当日→放行 / 未知数据源不断言
  - run_backtest（注入式骨架）：全链路（pre_validate 门控→决策→次日出场）/
    pre_val 否决跳过 / 退潮 CONDITIONAL 不放行 / 未注入依赖→RuntimeError

依据：24_daban_strategy_detail.md v1.9.2 §3.13 缺失#5 / v1.9.3 §3.14 缺失#10
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from zephyr.ex_core.daban_pit_safety import (
    DabanPITBacktestFramework,
    get_dragon_tiger_pit,
)

# ---------------------------------------------------------------------
# get_dragon_tiger_pit（§3.13#5）—— 鸭子类型 fake db_session
# ---------------------------------------------------------------------


class _FakeRow:
    def __init__(self, symbol, trade_date, seats=None):
        self.symbol = symbol
        self.trade_date = trade_date
        self.seats = seats or []

    def keys(self):
        return ("symbol", "trade_date", "seats")

    def __getitem__(self, k):
        return getattr(self, k)


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows


class _FakeSession:
    """记录查询参数并按 latest 过滤的鸭子类型 session（模拟 SQL 边界语义）。"""

    def __init__(self, rows):
        self._rows = rows
        self.last_params = None

    def execute(self, sql, params):
        self.last_params = params
        # 模拟 WHERE trade_date <= :latest
        filtered = [r for r in self._rows if r.trade_date <= params["latest"]]
        return _FakeResult(filtered)


class TestGetDragonTigerPit:
    def test_query_boundary_latest_is_t_minus_1(self):
        """查询边界：latest = as_of_date - 1 天（T 日盘中只用 T-1 及之前）。"""
        session = _FakeSession([])
        get_dragon_tiger_pit("000001", date(2026, 8, 19), session)
        assert session.last_params["latest"] == date(2026, 8, 18)
        assert session.last_params["symbol"] == "000001"

    def test_t_day_row_filtered_out_by_sql(self):
        """T 日龙虎榜被 SQL 边界过滤→返回仅 T-1 及之前，断言通过。"""
        rows = [
            _FakeRow("000001", date(2026, 8, 18)),
            _FakeRow("000001", date(2026, 8, 17)),
        ]
        session = _FakeSession(rows)
        out = get_dragon_tiger_pit("000001", date(2026, 8, 19), session)
        assert len(out) == 2
        assert all(isinstance(r, dict) for r in out)

    def test_pit_violation_raises(self):
        """fake session 不过滤（模拟脏数据/错误 SQL）→T 日行触发 PIT 断言 AssertionError。"""
        rows = [_FakeRow("000001", date(2026, 8, 19))]  # T 日数据
        session = _FakeSession(rows)
        session.execute = lambda sql, params: _FakeResult(rows)  # 不过滤，直返脏数据
        with pytest.raises(AssertionError, match="PIT VIOLATION"):
            get_dragon_tiger_pit("000001", date(2026, 8, 19), session)

    def test_empty_result(self):
        """退化：无龙虎榜记录→空列表不崩。"""
        session = _FakeSession([])
        assert get_dragon_tiger_pit("000001", date(2026, 8, 19), session) == []


# ---------------------------------------------------------------------
# DabanPITBacktestFramework.assert_pit（§3.14#10）
# ---------------------------------------------------------------------


class TestAssertPit:
    def test_dragon_tiger_same_day_violation(self):
        with pytest.raises(AssertionError, match="PIT VIOLATION"):
            DabanPITBacktestFramework.assert_pit("dragon_tiger", date(2026, 8, 19), date(2026, 8, 19))

    def test_dragon_tiger_t_minus_1_ok(self):
        DabanPITBacktestFramework.assert_pit("dragon_tiger", date(2026, 8, 18), date(2026, 8, 19))

    def test_next_day_auction_future_violation(self):
        with pytest.raises(AssertionError, match="PIT VIOLATION"):
            DabanPITBacktestFramework.assert_pit("next_day_auction", date(2026, 8, 21), date(2026, 8, 20))

    def test_next_day_auction_same_day_ok(self):
        DabanPITBacktestFramework.assert_pit("next_day_auction", date(2026, 8, 20), date(2026, 8, 20))

    def test_unknown_source_no_assert(self):
        """未登记规则的数据源→不断言（实时数据源 T 日盘中可用）。"""
        DabanPITBacktestFramework.assert_pit("emotion_cycle_score", date(2026, 8, 19), date(2026, 8, 19))
        DabanPITBacktestFramework.assert_pit("totally_unknown", date(2026, 8, 19), date(2026, 8, 19))

    def test_pit_rules_cover_six_sources(self):
        assert set(DabanPITBacktestFramework.PIT_RULES) == {
            "dragon_tiger",
            "emotion_cycle_score",
            "echelon_data",
            "seal_data",
            "next_day_auction",
            "news_sentiment",
        }


# ---------------------------------------------------------------------
# DabanPITBacktestFramework.run_backtest（注入式骨架）
# ---------------------------------------------------------------------


def _make_framework(
    echelon_health="PERFECT", emotion_phase="主升", emotion_score=50.0, tech_score=70.0, auction_open=11.0
):
    t0 = date(2026, 8, 18)
    t1 = date(2026, 8, 19)
    t2 = date(2026, 8, 20)

    def data_loader(source, d):
        if source == "dragon_tiger":
            return {"date": d - timedelta(days=1)}  # 永远 T-1，PIT 合规
        if source == "emotion_cycle_score":
            return {"date": d, "phase": emotion_phase, "score": emotion_score, "divergence": 0.0}
        if source == "echelon_data":
            return {
                "date": d,
                "health": echelon_health,
                "height": 2,
                "sector_resonance": 0.8,
                "follow_count": 5,
                "tech_score": tech_score,
                "price": 10.0,
            }
        if source == "next_day_auction":
            return {"date": d, "open_price": auction_open}
        raise KeyError(source)

    return DabanPITBacktestFramework(
        data_loader=data_loader,
        trading_days=lambda s, e: [t0, t1],
        next_trading_day=lambda d: t2,
    )


class TestRunBacktest:
    def test_full_chain_board_then_exit(self):
        """PERFECT 梯队+主升+双分达标→BOARD→次日高开 10% 全卖，2 个交易日均成交。"""
        fw = _make_framework()
        out = fw.run_backtest({}, date(2026, 8, 18), date(2026, 8, 19))
        assert out["total"] == 2
        assert out["by_decision"] == {"BOARD": 2}
        assert all(t["exit"]["action"] == "SELL_ALL" for t in out["trades"])

    def test_pre_validate_reject_skips_day(self):
        """LONE_DRAGON 孤板+1板+无共振无跟风=17 分→pre_validate 否决→当日跳过。"""
        fw = _make_framework(echelon_health="LONE_DRAGON")
        fw.data_loader = self._patch_echelon(fw.data_loader, height=1, resonance=0.1, follow=0)
        out = fw.run_backtest({}, date(2026, 8, 18), date(2026, 8, 19))
        assert out["total"] == 0

    def test_retreat_phase_conditional_not_pass(self):
        """退潮期 CONDITIONAL 梯队（FRACTURE 3板 58 分）不放行→跳过。"""
        fw = _make_framework(echelon_health="FRACTURE", emotion_phase="退潮")
        fw.data_loader = self._patch_echelon(fw.data_loader, height=3, resonance=0.8, follow=3)
        out = fw.run_backtest({}, date(2026, 8, 18), date(2026, 8, 19))
        assert out["total"] == 0

    @staticmethod
    def _patch_echelon(loader, height, resonance, follow):
        def patched(source, d):
            data = loader(source, d)
            if source == "echelon_data":
                data = {**data, "height": height, "sector_resonance": resonance, "follow_count": follow}
            return data

        return patched

    def test_decision_not_board_continue_skips(self):
        """决策非 BOARD/CONTINUE（低分→REJECT）→跳过。"""
        fw = _make_framework(emotion_score=25.0, tech_score=30.0)
        out = fw.run_backtest({}, date(2026, 8, 18), date(2026, 8, 19))
        assert out["total"] == 0

    def test_missing_injection_runtime_error(self):
        """退化：未注入依赖→RuntimeError（骨架未接线显式报错）。"""
        fw = DabanPITBacktestFramework()
        with pytest.raises(RuntimeError, match="未注入"):
            fw.run_backtest({}, date(2026, 8, 18), date(2026, 8, 19))

    def test_pit_violation_inside_backtest_raises(self):
        """回测内龙虎榜数据 T 日（违规）→AssertionError 中断（Fail-Closed）。"""
        fw = _make_framework()
        orig = fw.data_loader
        fw.data_loader = lambda s, d: {"date": d} if s == "dragon_tiger" else orig(s, d)
        with pytest.raises(AssertionError, match="PIT VIOLATION"):
            fw.run_backtest({}, date(2026, 8, 18), date(2026, 8, 19))
