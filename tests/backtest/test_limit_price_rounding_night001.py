# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 昨收价+板块幅度+最新价
#   fields: prev_close / limit_pct / price
#   code: MatchingEngine._is_limit_up / _is_limit_down; limit_board_queue.limit_up_price / limit_down_price
# 层: 算法
# - id: A1
#   name_zh: 涨跌停价取整
#   name_en: limit_price_rounding
#   intro: 昨收×(1±幅度) 按交易所口径 ROUND_HALF_UP 到分（钉住 x.xx5 边界）
#   code: quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
# 层: 输出
# - id: O1
#   name_zh: 涨跌停判定/板态
#   en: limit_state
# [/ALGO_FLOW]
# [A_test] module_id: MOD-TEST-BT-LIMITROUND-NIGHT001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 / MOD-SIM-025
# [MODULE] tests.backtest.test_limit_price_rounding_night001
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_limit_price_rounding_night001.py
# [TTL] permanent
"""AI-NIGHT-001 包3.2 登记项#3 — 涨跌停价交易所口径 ROUND_HALF_UP 边界测试。

A 股涨跌停价 = 昨收×(1±幅度) 四舍五入到 0.01 元（交易所口径 ROUND_HALF_UP）。
原实现用 Decimal 默认 ROUND_HALF_EVEN（matching_engine）/ float 银行家舍入
（limit_board_queue），在恰 x.xx5 边界差 1 分（如 10.15×1.1=11.165 → 交易所
11.17，银行家 11.16）。

基准口径：stk_limit 表生成（akshare_provider DS-082）已是 Decimal+ROUND_HALF_UP。

数学注记（边界可达性）：昨收为分位整数 p/100，
  ±10%: 11p/1000 尾 5 ⟺ p≡5 (mod 10)（如 10.15/10.35 可达）
  ±20%: 12p/1000 永为偶数尾 → 科创/创业板块无 x.xx5 边界（无需用例）
  ±30%: 13p/1000 尾 5 ⟺ p≡5 (mod 10)（如北交所 10.25×1.3=13.325 可达）
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_engine import MatchingEngine
from zephyr.simulation.limit_board_queue import (
    BoardState,
    detect_board_state,
    limit_down_price,
    limit_up_price,
)

D = Decimal


class TestMatchingEngineRoundingHalfUp:
    """matching_engine 涨跌停判定：恰 x.xx5 边界按交易所口径翻转"""

    def test_main_board_limit_up_10165(self):
        """主板 prev=10.15：×1.1=11.165 → 交易所 11.17（银行家 11.16）"""
        engine = MatchingEngine()
        # 11.16 < 11.17 → 未涨停，买单可成（旧口径误判涨停拒买）
        assert engine._is_limit_up("600000", D("11.16"), D("10.15")) is False
        # 11.17 = 涨停价 → 拒买
        assert engine._is_limit_up("600000", D("11.17"), D("10.15")) is True

    def test_main_board_limit_up_10385(self):
        """主板 prev=10.35：×1.1=11.385 → 交易所 11.39（银行家 11.38）"""
        engine = MatchingEngine()
        assert engine._is_limit_up("600000", D("11.38"), D("10.35")) is False
        assert engine._is_limit_up("600000", D("11.39"), D("10.35")) is True

    def test_main_board_limit_down_7605(self):
        """主板 prev=8.45：×0.9=7.605 → 交易所 7.61（银行家 7.60）"""
        engine = MatchingEngine()
        # 7.61 = 跌停价 → 拒卖（旧口径 7.61>7.60 放行——1 分边界差）
        assert engine._is_limit_down("600000", D("7.61"), D("8.45")) is True
        assert engine._is_limit_down("600000", D("7.60"), D("8.45")) is True
        # 7.62 > 7.61 → 未跌停，卖单可成
        assert engine._is_limit_down("600000", D("7.62"), D("8.45")) is False

    def test_bse_30pct_limit_up_13325(self):
        """北交所 prev=10.25：×1.3=13.325 → 交易所 13.33（银行家 13.32）"""
        engine = MatchingEngine()
        assert engine._is_limit_up("830799", D("13.32"), D("10.25")) is False
        assert engine._is_limit_up("830799", D("13.33"), D("10.25")) is True

    def test_exact_boundary_unaffected(self):
        """非 x.xx5 精确边界：两种舍入一致（零回归）"""
        engine = MatchingEngine()
        # 10.00×1.1=11.00 精确：触板拒买
        assert engine._is_limit_up("600000", D("11.00"), D("10.00")) is True
        assert engine._is_limit_up("600000", D("10.99"), D("10.00")) is False
        # 10.00×0.9=9.00 精确：触板拒卖
        assert engine._is_limit_down("600000", D("9.00"), D("10.00")) is True
        assert engine._is_limit_down("600000", D("9.01"), D("10.00")) is False


class TestLimitBoardQueueRoundingHalfUp:
    """limit_board_queue 涨跌停价函数：Decimal 精确乘 + ROUND_HALF_UP"""

    def test_limit_up_price_11385(self):
        """10.35×1.1=11.385 → 11.39（float 银行家得 11.38，防回归）"""
        assert limit_up_price(10.35, 0.10) == pytest.approx(11.39)

    def test_limit_up_price_11165(self):
        """10.15×1.1=11.165 → 11.17"""
        assert limit_up_price(10.15, 0.10) == pytest.approx(11.17)

    def test_limit_down_price_7605(self):
        """8.45×0.9=7.605 → 7.61（float 银行家得 7.60，防回归）"""
        assert limit_down_price(8.45, 0.10) == pytest.approx(7.61)

    def test_existing_tick_rounding_unchanged(self):
        """既有口径 10.05×1.1=11.055 → 11.06 保持一致（HALF_UP 同向）"""
        assert limit_up_price(10.05, 0.10) == pytest.approx(11.06)
        assert limit_down_price(10.05, 0.10) == pytest.approx(9.05)

    def test_detect_board_state_boundary(self):
        """板态判定在 1 分边界翻转"""
        # 涨停价 11.39：11.38 正常，11.39 涨停
        assert detect_board_state(11.38, 10.35, 0.10) is BoardState.NORMAL
        assert detect_board_state(11.39, 10.35, 0.10) is BoardState.LIMIT_UP
        # 跌停价 7.61：7.61 跌停，7.62 正常
        assert detect_board_state(7.61, 8.45, 0.10) is BoardState.LIMIT_DOWN
        assert detect_board_state(7.62, 8.45, 0.10) is BoardState.NORMAL
