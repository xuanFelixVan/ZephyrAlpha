# [BLUEPRINT] MOD-BT-T0V3 | docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md | §4 材料资格判据契约
# [MODULE] tests/audit/test_t0_conditional_e4_v3_exam.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/t0_conditional_e4_v3_exam.py; scripts/audit/t0_conditional_e4_v2_exam.py
# [CONSUMERS] pre-commit 自家测试批；红蓝复算
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部离线（零 CH、零生产路径写入，材料一律 tmp_path）；每条断言必须能红（判据件不许自我证明为真）
# [MODIFY-GUARD] 禁为让测试过而放宽资格判据
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红，禁 skip 掩盖
# [TESTS] 本件即测试
# [TTL] task_bound
"""T0-CONDITIONAL-V3 材料资格判据契约测试（治 F-1/F-2/F-3 三污染，见卡 §0.2）"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "audit"))

import t0_conditional_e4_v2_exam as v2  # noqa: E402
import t0_conditional_e4_v3_exam as v3  # noqa: E402


def _fill(day, symbol, side, price, qty, ts="09:35:00", run="r1"):
    return {
        "timestamp": f"{day} {ts}",
        "symbol": symbol,
        "side": side,
        "price": price,
        "quantity": qty,
        "commission": 5.0,
        "run_id": run,
        "trade_date": day,
    }


class TestM2RoundTripWithinOneRun:
    def test_cross_run_buy_and_sell_must_not_form_a_pair(self) -> None:
        """F-1 主案：A 组合只买、B 组合只卖，同 symbol 同日 ⇒ 会计上不存在往返，必 0 配对。

        若本测试变绿的方式是"pool 之后再配对"，即证明修复不承重——此断言就是那条红线。
        """
        runs = {
            "runA": [_fill("2026-07-01", "600000", "buy", 10.0, 1000, run="runA")],
            "runB": [_fill("2026-07-01", "600000", "sell", 10.5, 1000, run="runB")],
        }
        pairs, tally = v3.pair_within_runs(runs)
        assert pairs == []
        assert tally["pairs_gross"] == 0

    def test_same_run_both_sides_forms_exactly_one_pair(self) -> None:
        runs = {
            "runA": [
                _fill("2026-07-01", "600000", "buy", 10.0, 1000, ts="09:35:00"),
                _fill("2026-07-01", "600000", "sell", 10.05, 1000, ts="14:30:00"),
            ]
        }
        pairs, tally = v3.pair_within_runs(runs)
        assert len(pairs) == 1
        assert pairs[0]["run_id"] == "runA"
        assert abs(pairs[0]["gross_bp"] - 50.0) < 1.0
        assert tally["pairs_rejected_m4_price_limit"] == 0


class TestM4PriceLimitFeasibility:
    @pytest.mark.parametrize(
        "symbol,expected_board",
        [
            ("600000", "main"),
            ("000001", "main"),
            ("300908", "gem_star"),
            ("301162", "gem_star"),
            ("688697", "gem_star"),
            ("830799", "bse"),
        ],
    )
    def test_board_classification(self, symbol, expected_board) -> None:
        assert v3.board_of(symbol) == expected_board

    def test_impossible_intraday_spread_is_rejected(self) -> None:
        """300908 同日 18.78→28.68（+52.7%）＝两套执行模型分歧，超创业板 ±20% 单日极限 ⇒ 必剔。"""
        runs = {
            "runA": [
                _fill("2026-04-22", "300908", "buy", 18.7793, 100),
                _fill("2026-04-22", "300908", "sell", 28.6771, 100),
            ]
        }
        pairs, tally = v3.pair_within_runs(runs)
        assert pairs == []
        assert tally["pairs_rejected_m4_price_limit"] == 1

    def test_main_board_cap_is_between_2200_and_2230_bp(self) -> None:
        cap = v3.max_feasible_gross_bp("600000")
        assert 2200 < cap < 2230  # (1.10/0.90-1)*1e4

    def test_gem_star_cap_is_5000_bp(self) -> None:
        assert 4990 < v3.max_feasible_gross_bp("300908") < 5010


class TestM3TradeLogDedup:
    def test_fingerprint_stable_across_dict_order(self) -> None:
        a = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        b = [{"y": 2, "x": 1}, {"x": 3, "y": 4}]
        assert v3.log_fingerprint(a) == v3.log_fingerprint(b)

    def test_fingerprint_changes_when_price_changes(self) -> None:
        a = [{"x": 1, "y": 2}]
        b = [{"x": 1, "y": 3}]
        assert v3.log_fingerprint(a) != v3.log_fingerprint(b)

    def test_identical_log_under_two_run_ids_counted_once(self, tmp_path) -> None:
        """F-3 主案：同一 trade_log 换 run_id 逐字节重放（实测 60 件仅 32 指纹）⇒ 只取首个代表件。"""
        log = [_fill("2026-07-01", "600000", "buy", 10.0, 100), _fill("2026-07-01", "600000", "sell", 10.02, 100)]
        plain = [{k: v for k, v in t.items() if k not in ("run_id", "trade_date")} for t in log]
        for name, rid in (("bt-aaaa.json", "bt-aaaa"), ("bt-bbbb.json", "bt-bbbb")):
            (tmp_path / name).write_text(
                yaml.safe_dump({"run_id": rid, "strategy_id": "s", "trade_log": plain}), encoding="utf-8"
            )
        _kept, mat = v3.load_material(tmp_path)
        assert mat["files_total"] == 2
        assert mat["files_deduped_away"] == 1
        assert mat["fills_total"] == 2  # 只数代表件的 2 笔，重放件的 2 笔不进气泡计数


class TestGateSetSeparation:
    """卡 §2.3：不路由日=副考，禁并入主考；宏观禁做=对照。"""

    def _pairs(self):
        return [{"symbol": "600000", "trade_date": "2026-07-06", "gross_bp": 40.0, "net_bp": 8.8}]

    def test_unrouted_emotion_goes_to_secondary_not_primary(self) -> None:
        regime = {date(2026, 7, 3): ("r3", 0.9)}
        phases = {"2026-07-03": ""}  # routed=0
        p, s, c, tally = v2.split_gates(self._pairs(), regime, phases)
        assert p == [] and len(s) == 1 and c == []
        assert tally["emotion_unevaluable_day"] == 1

    def test_emotion_deny_never_enters_primary(self) -> None:
        regime = {date(2026, 7, 3): ("r3", 0.9)}
        phases = {"2026-07-03": "capitulation"}
        p, s, c, _t = v2.split_gates(self._pairs(), regime, phases)
        assert p == [] and s == [] and len(c) == 1

    def test_both_gates_allow_enters_primary(self) -> None:
        regime = {date(2026, 7, 3): ("r3", 0.9)}
        phases = {"2026-07-03": "expansion"}
        p, s, c, _t = v2.split_gates(self._pairs(), regime, phases)
        assert len(p) == 1 and s == [] and c == []

    def test_emotion_allow_but_macro_deny_goes_to_control(self) -> None:
        """考窗实测态：六段=expansion 而 vol_pct 仅 0.5 ⇒ 双门互斥的具体形态。"""
        regime = {date(2026, 7, 3): ("r2", 0.504)}
        phases = {"2026-07-03": "expansion"}
        p, s, c, _t = v2.split_gates(self._pairs(), regime, phases)
        assert p == [] and s == [] and len(c) == 1
