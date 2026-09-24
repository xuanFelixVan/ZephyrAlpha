# [BLUEPRINT] MOD-BT-CEIL | docs/_working/t0_matrix/t0_ceiling_prereg_card.md | §0 单向判读 + §2 判据契约
# [MODULE] tests/audit/test_t0_ceiling_capacity_exam.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/t0_ceiling_capacity_exam.py; scripts/audit/cost_trio_exam.py
# [CONSUMERS] pre-commit 自家测试批；红蓝复算
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部离线零 CH；每条断言须能红；禁写生产路径
# [MODIFY-GUARD] 禁为过测试而放宽判读方向
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红，禁 skip
# [TESTS] 本件即测试
# [TTL] task_bound
"""T0-CEILING 容量考试契约测试（单向判读 / 判线继承 / PIT / 除零回归）"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "audit"))

import cost_trio_exam as ct  # noqa: E402
import t0_ceiling_capacity_exam as ceil  # noqa: E402

SRC = (REPO / "scripts" / "audit" / "t0_ceiling_capacity_exam.py").read_text(encoding="utf-8")


class TestOneDirectionalReading:
    """本件的全部诚实性在于：只会杀，不会夸。"""

    def test_no_verdict_string_ever_claims_pass(self) -> None:
        for n in (0, 10, 30, 1000):
            for ge in (0, n // 4, n // 2, n):
                v = ceil.judge(n, ge)
                assert v in {"INSUFFICIENT", "DEAD_BY_CEILING", "MARGINAL", "CEILING_OK_NOT_A_PROOF"}
                assert "PASS" not in v

    def test_source_contains_no_pass_emitting_branch(self) -> None:
        code = "\n".join(ln for ln in SRC.splitlines() if not ln.lstrip().startswith("#"))
        assert not re.search(r'return\s+"PASS', code)
        assert '"CEILING_OK_NOT_A_PROOF"' in code  # 通过态必须自带"不构成证明"字样

    def test_dead_requires_share_below_five_percent(self) -> None:
        assert ceil.judge(1000, 49) == "DEAD_BY_CEILING"
        assert ceil.judge(1000, 50) == "MARGINAL"
        assert ceil.judge(1000, 199) == "MARGINAL"
        assert ceil.judge(1000, 200) == "CEILING_OK_NOT_A_PROOF"

    def test_sample_floor_defers_judgment(self) -> None:
        assert ceil.judge(29, 29) == "INSUFFICIENT"
        assert ceil.judge(30, 0) == "DEAD_BY_CEILING"
        assert ceil.GROUP_MIN_SYMBOL_DAYS == ct.PAIR_GATE  # 门槛承考试族，非本件自定


class TestCostLinesAreInherited:
    def test_L1_equals_CST_T0_001_rt(self) -> None:
        assert ceil.L1_BP == ct.RT_COST_BP == 31.2

    def test_L2_equals_rt_plus_precondition(self) -> None:
        assert ceil.L2_BP == round(ct.RT_COST_BP + ct.EDGE_PRECONDITION_BP, 6) == 61.2

    def test_no_hardcoded_cost_number_in_source(self) -> None:
        code = "\n".join(ln for ln in SRC.splitlines() if not ln.lstrip().startswith("#") and "注释" not in ln)
        # 判线只能来自 ct.*_BP 引用，禁出现裸 31.2 / 61.2 常数
        assert not re.search(r"(L1_BP|L2_BP)\s*=\s*\d", code)


class TestPitLookAlike:
    def test_same_day_is_never_used(self) -> None:
        series = {"2026-03-02": "x"}
        assert ceil.t1(series, "2026-03-02") is None  # 同日不算 T-1

    def test_previous_trading_day_used(self) -> None:
        series = {"2026-03-02": "x", "2026-03-04": "y"}
        assert ceil.t1(series, "2026-03-05") == "y"

    def test_beyond_asof_tolerance_is_unevaluable_not_stale(self) -> None:
        # 只有 1/2 的读数，问 3/5 ⇒ 超 7 自然日容差，必须判"不可评"(None) 而不是拿旧值凑
        assert ceil.t1({"2026-01-02": "x"}, "2026-03-05") is None

    def test_tolerance_constant_matches_exam_family(self) -> None:
        import t0_conditional_e4_exam as v1

        assert v1.ASOF_TOLERANCE_DAYS == 7


class TestDivisionByZeroRegression:
    """首跑被 CH Code 153（kline_1min 存在 min(low)=0 的股票-日）拦下，本类防回归。"""

    def test_division_only_inside_guard(self) -> None:
        sql = SRC[SRC.index("_SQL_DAILY_CEILING") : SRC.index("def load_daily")]
        # 只看真代码行：SQL 注释（-- 开头）里讲解这个坑时必然提到 hi/lo，不算违规
        code_ln = [l for l in sql.splitlines() if not l.strip().startswith("--")]
        for ln in [l for l in code_ln if "/" in l and "lo" in l]:
            assert "if(lo > 0" in ln or "if(lo>0" in ln, f"未兜住零价的除法：{ln.strip()}"

    def test_zero_price_rows_are_instrumented_not_silently_dropped(self) -> None:
        assert "zero_lo" in SRC and "zero_lo_sd" in SRC

    def test_bar_count_uses_uniq_exact_not_count(self) -> None:
        """ReplacingMergeTree 未 FINAL 时同分钟多版，count() 会虚增 bar_n 误判可交易。"""
        sql = SRC[SRC.index("_SQL_DAILY_CEILING") : SRC.index("def load_daily")]
        assert "uniqExact(trade_time)" in sql
        assert not re.search(r"\bcount\(\)\s+AS\s+bar_n", sql)


class TestWindowFloorIsCensusDerived:
    def test_start_matches_minute_leg_floor(self) -> None:
        assert ceil.CEILING_START == "2021-09-01"  # 分钟腿起点（普查实测），禁前推

    def test_min_bars_is_documented_proxy(self) -> None:
        assert ceil.MIN_BARS == 200
        assert "可交易代理" in SRC or "bar_n" in SRC


class TestPackSideCrossCheckIsNotProse:
    """两件套互证必须可判红：包侧数与本件数不等时 cross_check_ok=False（原实现只留一个指针字符串）。"""

    def _rows(self):
        return [
            {"trade_date": "2022-01-04", "t1_macro_allow": 1, "t1_emotion_allow": 1},
            {"trade_date": "2022-01-05", "t1_macro_allow": 1, "t1_emotion_allow": 0},
            {"trade_date": "2024-12-31", "t1_macro_allow": 1, "t1_emotion_allow": 1},
        ]

    def test_agreement_and_disagreement_both_represented(self, monkeypatch):
        n = sum(1 for r in self._rows() if r["t1_macro_allow"] and r["t1_emotion_allow"])
        monkeypatch.setattr(ceil, "pack_dual_allow_same_window", lambda days: n)
        assert ceil.closed_book_subset(self._rows())["cross_check_ok"] is True
        monkeypatch.setattr(ceil, "pack_dual_allow_same_window", lambda days: n + 1)
        bad = ceil.closed_book_subset(self._rows())
        assert bad["cross_check_ok"] is False and bad["dual_allow_days_pack_side_same_day_set"] == n + 1
        assert bad["dual_allow_days_in_window"] == n

    def test_absent_pack_is_disclosed_not_silently_equal(self, monkeypatch):
        monkeypatch.setattr(ceil, "pack_dual_allow_same_window", lambda days: None)
        got = ceil.closed_book_subset(self._rows())
        assert got["dual_allow_days_pack_side_same_day_set"] is None and got["cross_check_ok"] is True
        assert "同一日集合" in got["cross_check"]
