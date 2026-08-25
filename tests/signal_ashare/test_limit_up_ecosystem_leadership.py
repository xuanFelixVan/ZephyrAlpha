# [A_test] module_id: MOD-SIG-097 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-097 | docs/03_modules/_domain_signal/limit_up_ecosystem_leadership/blueprint.md
# [MODULE] tests.signal_ashare.test_limit_up_ecosystem_leadership
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""动量领导因子与涨停板生态模型（MOD-SIG-097，B10-01366）施工验证测试。

覆盖：
- 梯队生态：连板高度/分布（cap 归并）/断层检测/断层严重度/封板时间统计/
  早盘封板占比/晋级成功率（相邻日符号对齐）/断层预警；
- 降级路径：空梯队、无封板时间、无相邻日快照；
- Granger 领导-跟随：构造性领先-滞后显著、独立序列不显著、反向不显著、
  样本不足 checked=False 降级、系数阈值门槛；
- fail-closed：非法连板高度/封板分钟/不等长/非有限值/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB。
"""

from __future__ import annotations

import dataclasses
import json
import math

import pytest

from zephyr.signal_ashare.limit_up_ecosystem_leadership import (
    LadderEcosystemConfig,
    LimitUpEcosystemLeadership,
    LimitUpStock,
)


def _engine() -> LimitUpEcosystemLeadership:
    return LimitUpEcosystemLeadership(LadderEcosystemConfig())


def _stock(symbol: str, consec: int, seal: float | None = 30.0) -> LimitUpStock:
    return LimitUpStock(symbol=symbol, consec_limit=consec, first_seal_minute=seal)


def _lcg_noise(n: int, seed: int = 42, scale: float = 0.002) -> list[float]:
    """确定性 LCG 伪噪声（±scale），避免随机夹具抖动。"""
    x = seed
    out: list[float] = []
    for _ in range(n):
        x = (1103515245 * x + 12345) % (2**31)
        out.append(((x / 2**31) - 0.5) * 2 * scale)
    return out


class TestConfigValidation:
    def test_default_config_ok(self) -> None:
        LadderEcosystemConfig()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("height_cap", 1),
            ("seal_early_minute", 0.0),
            ("promotion_warn_threshold", 0.0),
            ("promotion_warn_threshold", 1.0),
            ("promotion_min_base", 0),
            ("granger_threshold", 0.0),
            ("granger_significance", 0.0),
            ("granger_significance", 1.0),
            ("granger_max_lag", 0),
            ("granger_min_samples", 10),
        ],
    )
    def test_invalid_config_raises(self, field: str, value: float) -> None:
        with pytest.raises(ValueError):
            LadderEcosystemConfig(**{field: value})


class TestEcosystemSnapshot:
    def test_empty_ladder_degraded(self) -> None:
        snap = _engine().ecosystem_snapshot([], trade_date="2026-08-25")
        assert snap.stock_count == 0
        assert snap.max_height == 0
        assert snap.degraded is True
        assert snap.fault_levels == ()
        assert snap.fault_severity is None

    def test_height_and_distribution_with_cap_merge(self) -> None:
        stocks = (
            [_stock(f"s1_{i}", 1) for i in range(8)]
            + [_stock(f"s2_{i}", 2) for i in range(4)]
            + [_stock(f"s3_{i}", 3) for i in range(2)]
            + [_stock("top", 7)]  # ≥cap=5 归并
        )
        snap = _engine().ecosystem_snapshot(stocks)
        assert snap.max_height == 7
        assert snap.height_distribution == {1: 8, 2: 4, 3: 2, 4: 0, 5: 1}
        # 第 4 层为 0 而其上（归并层）仍有更高层 → 断层
        assert snap.fault_levels == (4,)
        assert snap.fault_severity == pytest.approx(1 / 4)

    def test_no_fault_when_ladder_continuous(self) -> None:
        stocks = [_stock("a", 1), _stock("b", 2), _stock("c", 3)]
        snap = _engine().ecosystem_snapshot(stocks)
        assert snap.fault_levels == ()
        assert snap.fault_severity == 0.0

    def test_single_level_no_severity(self) -> None:
        snap = _engine().ecosystem_snapshot([_stock("a", 1), _stock("b", 1)])
        assert snap.max_height == 1
        assert snap.fault_severity is None

    def test_seal_time_stats_and_early_ratio(self) -> None:
        stocks = [
            _stock("a", 1, seal=5.0),
            _stock("b", 2, seal=30.0),
            _stock("c", 1, seal=150.0),
            _stock("d", 1, seal=None),  # 缺封板时间不参与统计
        ]
        snap = _engine().ecosystem_snapshot(stocks)
        assert snap.seal_time_mean == pytest.approx((5.0 + 30.0 + 150.0) / 3)
        assert snap.seal_time_median == pytest.approx(30.0)
        # 默认早盘界 60 分钟：5/30 命中，150 不命中 → 2/3
        assert snap.early_seal_ratio == pytest.approx(2 / 3)

    def test_all_seal_missing_degrades_leg(self) -> None:
        stocks = [_stock("a", 1, seal=None), _stock("b", 2, seal=None)]
        snap = _engine().ecosystem_snapshot(stocks)
        assert snap.seal_time_mean is None
        assert snap.seal_time_median is None
        assert snap.early_seal_ratio is None
        assert any("封板时间" in n for n in snap.notes)

    def test_promotion_rates_and_warning(self) -> None:
        prev = [_stock(f"p{i}", 2, seal=None) for i in range(4)]
        # 4 只 2 板中仅 1 只今日晋级 3 板 → 2进3=25%<30% 预警
        curr = [_stock("p0", 3)] + [_stock("n1", 1), _stock("n2", 1)]
        snap = _engine().ecosystem_snapshot(curr, prev_stocks=prev)
        assert snap.promotion_rates is not None
        assert snap.promotion_rates[2] == pytest.approx(0.25)
        assert any("2进3" in w for w in snap.promotion_warnings)

    def test_promotion_rates_none_without_prev(self) -> None:
        snap = _engine().ecosystem_snapshot([_stock("a", 2)])
        assert snap.promotion_rates is None
        assert snap.promotion_warnings == ()

    def test_promotion_base_too_small_no_warning(self) -> None:
        prev = [_stock("p0", 2)]  # 基数 1 < 默认 3
        curr = [_stock("x", 1)]
        snap = _engine().ecosystem_snapshot(curr, prev_stocks=prev)
        assert snap.promotion_rates is not None
        assert snap.promotion_rates[2] == pytest.approx(0.0)
        assert snap.promotion_warnings == ()

    def test_invalid_consec_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().ecosystem_snapshot([_stock("a", 0)])

    def test_invalid_seal_minute_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().ecosystem_snapshot([_stock("a", 1, seal=-1.0)])


class TestLeadership:
    def test_constructed_leader_significant(self) -> None:
        n = 120
        noise = _lcg_noise(n, seed=7)
        leader = [math.sin(i / 5.0) * 0.02 + noise[i] for i in range(n)]
        noise_f = _lcg_noise(n, seed=99)
        # follower_t = 0.8 × leader_{t-1} + 微噪声 → 滞后 1 显著领导
        follower = [0.0] + [0.8 * leader[i - 1] + noise_f[i] for i in range(1, n)]
        res = _engine().leadership(leader, follower)
        assert res.checked is True
        assert res.p_value is not None and res.p_value < 0.05
        assert res.leadership is not None and res.leadership > 0.3
        assert res.is_leader is True
        assert res.direction == "leader"
        assert res.best_lag == 1

    def test_independent_series_not_significant(self) -> None:
        n = 120
        leader = [math.sin(i / 5.0) * 0.02 for i in range(n)]
        follower = [math.cos(i / 3.0) * 0.02 for i in range(n)]
        res = _engine().leadership(leader, follower)
        assert res.checked is True
        assert res.is_leader is False
        assert res.direction == "none"

    def test_reverse_direction_not_leader(self) -> None:
        n = 120
        leader = [math.sin(i / 5.0) * 0.02 + n_ for i, n_ in enumerate(_lcg_noise(n, seed=7))]
        follower = [0.0] + [0.8 * leader[i - 1] for i in range(1, n)]
        # 反向：follower 是否领导 leader → 不应显著成立领导关系
        res = _engine().leadership(follower, leader)
        assert res.checked is True
        assert res.is_leader is False

    def test_insufficient_samples_degrades(self) -> None:
        res = _engine().leadership([0.01] * 20, [0.01] * 20)
        assert res.checked is False
        assert res.is_leader is False
        assert res.f_stat is None
        assert res.p_value is None

    def test_unequal_length_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().leadership([0.01] * 40, [0.01] * 41)

    def test_non_finite_raises(self) -> None:
        bad = [0.01] * 39 + [float("nan")]
        with pytest.raises(ValueError):
            _engine().leadership(bad, [0.01] * 40)

    def test_invalid_lag_raises(self) -> None:
        with pytest.raises(ValueError):
            _engine().leadership([0.01] * 40, [0.01] * 40, max_lag=0)


class TestContract:
    def test_frozen_and_json_serializable(self) -> None:
        stocks = [_stock("a", 2), _stock("b", 1)]
        snap = _engine().ecosystem_snapshot(stocks, trade_date="2026-08-25")
        with pytest.raises(dataclasses.FrozenInstanceError):
            snap.max_height = 9  # type: ignore[misc]
        json.dumps(snap.to_dict())
        n = 120
        leader = [math.sin(i / 5.0) * 0.02 for i in range(n)]
        res = _engine().leadership(leader, leader)
        json.dumps(res.to_dict())
