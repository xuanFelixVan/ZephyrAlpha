# [BLUEPRINT] MOD-EX-049 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-EXE-daban_instant_circuit_breaker_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_core.test_daban_instant_circuit_breaker
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""打板专用瞬时风控单元测试（24_daban_strategy_detail §3.13 缺失#2）。

覆盖：
  - 触发器①封单崩塌（<70% 剩余即熔断，含恰 70% 边界不触发）
  - 触发器②梯队断层（FRACTURE/LONE_DRAGON/COLLAPSE 三态）
  - 触发器③量化席位 hard（>70% 触发，含恰 70% 边界不触发）
  - 触发器优先级（封单崩塌先于梯队/量化席位）
  - 正常态 MONITOR / 退化输入（initial_seal=0 或缺失）

依据：24_daban_strategy_detail.md v1.9.2 §3.13 缺失#2
"""

from __future__ import annotations

from zephyr.ex_core.daban_instant_circuit_breaker import DabanInstantCircuitBreaker


class TestSealCollapseTrigger:
    def test_seal_collapse_triggers(self):
        """封单剩余 60%（崩塌 40%≥30%）→瞬时熔断。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 6000, "initial_seal": 10000}, "PERFECT", 0.3)
        assert out["trigger"] == "SEAL_COLLAPSE"
        assert out["action"] == "INSTANT_SELL"
        assert out["qty_ratio"] == 1.0

    def test_seal_collapse_boundary_exactly_70pct_remaining_not_trigger(self):
        """边界：封单剩余恰好 70%（崩塌恰 30%）→seal_ratio<0.7 不成立→不触发①。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 7000, "initial_seal": 10000}, "PERFECT", 0.3)
        assert out["trigger"] is None
        assert out["action"] == "MONITOR"

    def test_seal_fully_gone_triggers(self):
        """封单归零→崩塌 100%→触发。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 0, "initial_seal": 10000}, "PERFECT", 0.0)
        assert out["trigger"] == "SEAL_COLLAPSE"


class TestEchelonFractureTrigger:
    def test_fracture_triggers(self):
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "FRACTURE", 0.3)
        assert out["trigger"] == "ECHELON_FRACTURE"
        assert out["action"] == "INSTANT_SELL"

    def test_lone_dragon_triggers(self):
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "LONE_DRAGON", 0.3)
        assert out["trigger"] == "ECHELON_FRACTURE"

    def test_collapse_triggers(self):
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "COLLAPSE", 0.3)
        assert out["trigger"] == "ECHELON_FRACTURE"

    def test_perfect_not_trigger(self):
        """PERFECT 梯队→触发器②不命中。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "PERFECT", 0.3)
        assert out["trigger"] is None


class TestQuantSeatTrigger:
    def test_quant_seat_hard_triggers(self):
        """量化席位 75%>70%→hard 熔断。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "PERFECT", 0.75)
        assert out["trigger"] == "QUANT_SEAT_HARD"
        assert out["action"] == "INSTANT_SELL"

    def test_quant_seat_boundary_exactly_70pct_not_trigger(self):
        """边界：恰好 70%→>70% 不成立→不触发。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "PERFECT", 0.70)
        assert out["trigger"] is None
        assert out["action"] == "MONITOR"


class TestPriorityAndDegenerate:
    def test_seal_collapse_priority_over_others(self):
        """三触发器同时满足→封单崩塌优先（spec 判定顺序）。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 0, "initial_seal": 10000}, "COLLAPSE", 0.9)
        assert out["trigger"] == "SEAL_COLLAPSE"

    def test_echelon_priority_over_quant_seat(self):
        """梯队+量化同时满足→梯队优先。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 9000, "initial_seal": 10000}, "FRACTURE", 0.9)
        assert out["trigger"] == "ECHELON_FRACTURE"

    def test_degenerate_initial_seal_zero(self):
        """退化：initial_seal=0→max(,1) 兜底不除零；current=0→崩塌触发。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {"current_seal": 0, "initial_seal": 0}, "PERFECT", 0.3)
        assert out["trigger"] == "SEAL_COLLAPSE"

    def test_degenerate_missing_live_data_keys(self):
        """退化：live_data 缺键→按 current=0/initial=1→崩塌触发（Fail-Closed）。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({}, {}, "PERFECT", 0.3)
        assert out["trigger"] == "SEAL_COLLAPSE"

    def test_normal_monitor(self):
        """正常持仓：封单 90%+PERFECT+量化 30%→MONITOR。"""
        cb = DabanInstantCircuitBreaker()
        out = cb.check_instant_break({"qty": 1000}, {"current_seal": 9000, "initial_seal": 10000}, "PERFECT", 0.3)
        assert out == {"trigger": None, "action": "MONITOR"}
