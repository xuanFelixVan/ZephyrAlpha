# [BLUEPRINT] MOD-PA-034 | docs/03_modules/_domain_portfolio_alloc/portfolio_netting/blueprint.md（被测件挂靠）
# [MODULE] tests.research.pf_alloc.test_portfolio_v0
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] pytest; pandas; numpy; src.zephyr.pf_alloc.core.portfolio_netting
# [CONSUMERS] portfolio_netting 质量守卫（MODIFY-GUARD）；L-4 里程碑一验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 全合成数据零 DB/网络依赖; 轧平代数正确性(同票反向等量→净零); 预算切分比例精确; NaN 缺供诚实传播不掩盖; 校验 fail-closed(负预算/未知策略名/空输入抛 ValueError)
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [A_module] module_id=MOD-PA-034 | layer=tests | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_portfolio_v0.py — L-4 里程碑一验收测试（净额轧平 + 预算切分，纯合成数据）。

被测件：src/zephyr/pf_alloc/core/portfolio_netting.py（MOD-PA-034）。
覆盖：轧平代数正确性 / 预算切分比例精确性 / NaN 缺供不掩盖 / fail-closed 校验 /
输出形状契约（列序字典序/日期并集/单策略恒等）与 fail-closed 扩展九类（C-9 补齐）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.zephyr.pf_alloc.core.portfolio_netting import net_positions, split_capital

# ──────────────────────────────────────────────────────────────────────────────
# 合成权重面 fixtures
# ──────────────────────────────────────────────────────────────────────────────


def _face(
    values: dict[str, list[float]],
    dates: int = 3,
) -> pd.DataFrame:
    """构造 date×symbol 权重面（index=交易日, columns=标的）。"""
    idx = pd.date_range("2026-01-05", periods=dates, freq="B")
    cols = list(values.keys())
    data = np.array([values[c] for c in cols], dtype="float64").T
    return pd.DataFrame(data, index=idx[: len(data)], columns=cols)


@pytest.fixture()
def face_long() -> pd.DataFrame:
    """策略 A：600000.SH 多 0.5，000001.SZ 多 0.2。"""
    return _face({"600000.SH": [0.5, 0.5, 0.5], "000001.SZ": [0.2, 0.2, 0.2]})


@pytest.fixture()
def face_short() -> pd.DataFrame:
    """策略 B：600000.SH 空 0.5（与 A 反向等量），300750.SZ 空 0.3。"""
    return _face({"600000.SH": [-0.5, -0.5, -0.5], "300750.SZ": [-0.3, -0.3, -0.3]})


# ──────────────────────────────────────────────────────────────────────────────
# ① 轧平代数正确性
# ──────────────────────────────────────────────────────────────────────────────


class TestNetPositionsAlgebra:
    """轧平代数：同票代数和、反向净零、符号保留。"""

    def test_opposite_equal_weights_net_to_zero(self, face_long: pd.DataFrame, face_short: pd.DataFrame) -> None:
        """两策略同票反向等量权重 → 净零（对冲净额，intent netting 本体）。"""
        net = net_positions({"stratA": face_long, "stratB": face_short})
        assert "600000.SH" in net.columns
        # 净零：浮点容差内恒为 0（三行全对冲）
        assert net["600000.SH"].to_numpy() == pytest.approx([0.0, 0.0, 0.0], abs=1e-12)

    def test_algebraic_sum_preserves_sign(self, face_long: pd.DataFrame, face_short: pd.DataFrame) -> None:
        """代数和逐格正确且符号保留：同向叠加/反向部分对冲/净空头自然表达。"""
        a = _face({"600000.SH": [0.4, 0.4, 0.4], "000001.SZ": [0.2, 0.2, 0.2]})
        b = _face({"600000.SH": [-0.1, -0.1, -0.1], "300750.SZ": [-0.3, -0.3, -0.3]})
        net = net_positions({"a": a, "b": b})
        # 同票代数和：0.4 + (-0.1) = 0.3
        assert net["600000.SH"].to_numpy() == pytest.approx([0.3, 0.3, 0.3])
        # 单策略独有标的 = 其自身权重（无观点策略贡献 0）
        assert net["000001.SZ"].to_numpy() == pytest.approx([0.2, 0.2, 0.2])
        assert net["300750.SZ"].to_numpy() == pytest.approx([-0.3, -0.3, -0.3])
        # 符号保留：负净权重 = 组合净空头
        assert (net["300750.SZ"] < 0).all()

    def test_three_strategy_netting(self) -> None:
        """三策略同票代数和顺序无关（加法交换律）。"""
        idx = pd.date_range("2026-01-05", periods=2, freq="B")
        f1 = pd.DataFrame({"X": [0.3, 0.3]}, index=idx)
        f2 = pd.DataFrame({"X": [-0.5, -0.5]}, index=idx)
        f3 = pd.DataFrame({"X": [0.45, 0.45]}, index=idx)
        net_ab = net_positions({"f1": f1, "f2": f2, "f3": f3})
        net_ba = net_positions({"f3": f3, "f2": f2, "f1": f1})
        assert net_ab["X"].to_numpy() == pytest.approx([0.25, 0.25])
        assert net_ba["X"].to_numpy() == pytest.approx(net_ab["X"].to_numpy())

    def test_date_union_alignment(self) -> None:
        """日期并集对齐：错位交易日逐格代数，缺供日诚实 NaN。"""
        idx1 = pd.date_range("2026-01-05", periods=2, freq="B")
        idx2 = pd.date_range("2026-01-06", periods=2, freq="B")
        f1 = pd.DataFrame({"X": [0.2, 0.2]}, index=idx1)
        f2 = pd.DataFrame({"X": [-0.2, -0.2]}, index=idx2)
        net = net_positions({"f1": f1, "f2": f2})
        assert len(net) == 3  # 01-05/01-06/01-07 并集
        # 01-05：f2 面无该行=缺供 → 净 NaN（不默认 0 掩盖）
        assert net.loc[idx1[0], "X"] != net.loc[idx1[0], "X"]
        # 01-06：两方都供 → 0.2 + (-0.2) = 净零
        assert net.loc[idx2[0], "X"] == pytest.approx(0.0, abs=1e-12)
        # 01-07：仅 f2 供 → 净 = f2（f1 面无该行=缺供 → NaN）
        assert net.loc[idx2[1], "X"] != net.loc[idx2[1], "X"]


# ──────────────────────────────────────────────────────────────────────────────
# ② 预算切分比例精确性
# ──────────────────────────────────────────────────────────────────────────────


class TestSplitCapital:
    """预算切分：逐策略缩放精确、再轧平正确。"""

    def _combined_face(self) -> pd.DataFrame:
        idx = pd.date_range("2026-01-05", periods=2, freq="B")
        cols = pd.MultiIndex.from_tuples(
            [("sA", "600000.SH"), ("sA", "000001.SZ"), ("sB", "600000.SH"), ("sB", "300750.SZ")],
            names=["strategy", "symbol"],
        )
        data = np.array(
            [
                [0.5, 0.2, -0.4, -0.3],
                [0.5, 0.2, -0.4, -0.3],
            ],
            dtype="float64",
        )
        return pd.DataFrame(data, index=idx, columns=cols)

    def test_budget_scaling_exact_ratio(self) -> None:
        """预算切分比例精确：每策略面整体 × 预算比（sleeve 账本独立互不挪用）。"""
        combined = self._combined_face()
        net = split_capital(combined, {"sA": 0.6, "sB": 0.4})
        # sA 预算 0.6：600000.SH 贡献 0.5×0.6=0.30；sB 预算 0.4：贡献 -0.4×0.4=-0.16
        assert net["600000.SH"].to_numpy() == pytest.approx([0.14, 0.14])
        assert net["000001.SZ"].to_numpy() == pytest.approx([0.12, 0.12])
        assert net["300750.SZ"].to_numpy() == pytest.approx([-0.12, -0.12])

    def test_split_then_net_equivalence(self) -> None:
        """split_capital ≡ 逐策略手动缩放后 net_positions（两入口一条代数）。"""
        combined = self._combined_face()
        budget = {"sA": 0.7, "sB": 0.3}
        via_split = split_capital(combined, budget)
        via_manual = net_positions(
            {
                "sA": combined["sA"].mul(budget["sA"]),
                "sB": combined["sB"].mul(budget["sB"]),
            }
        )
        pd.testing.assert_frame_equal(via_split, via_manual)

    def test_zero_budget_silences_strategy(self) -> None:
        """预算 0 = 该 sleeve 本轮零仓位（合法，非缺供）。"""
        combined = self._combined_face()
        net = split_capital(combined, {"sA": 1.0, "sB": 0.0})
        assert net["300750.SZ"].to_numpy() == pytest.approx([0.0, 0.0], abs=1e-15)
        assert net["600000.SH"].to_numpy() == pytest.approx([0.5, 0.5])


# ──────────────────────────────────────────────────────────────────────────────
# ③ NaN 缺供诚实传播（不掩盖）
# ──────────────────────────────────────────────────────────────────────────────


class TestNanHonesty:
    """NaN=诚实缺供：不 fillna、不默认 0 掩盖。"""

    def test_nan_cell_propagates_to_net(self, face_long: pd.DataFrame) -> None:
        """某策略某格 NaN（缺供）→ 净面该格 NaN（其余格正常代数）。"""
        a = face_long.copy()
        b = _face({"600000.SH": [-0.2, -0.2, -0.2]})
        a.iloc[1, a.columns.get_loc("600000.SH")] = np.nan  # 策略 A 01-06 缺供
        net = net_positions({"a": a, "b": b})
        col = net["600000.SH"]
        assert col.iloc[1] != col.iloc[1]  # NaN（缺供传播）
        assert col.iloc[0] == pytest.approx(0.3)
        assert col.iloc[2] == pytest.approx(0.3)

    def test_all_nan_column_fully_blocked(self) -> None:
        """整列缺供 → 净面该列全 NaN（禁止带病面流出）。"""
        a = _face({"X": [np.nan, np.nan, np.nan]})
        b = _face({"X": [0.3, 0.3, 0.3]})
        net = net_positions({"a": a, "b": b})
        assert net["X"].isna().all()

    def test_split_capital_nan_propagates(self) -> None:
        """预算切分同样诚实：缩放不修复 NaN（×预算≠补数）。"""
        idx = pd.date_range("2026-01-05", periods=2, freq="B")
        cols = pd.MultiIndex.from_tuples([("sA", "X"), ("sB", "X")], names=["strategy", "symbol"])
        combined = pd.DataFrame([[0.5, -0.2], [np.nan, -0.2]], index=idx, columns=cols)
        net = split_capital(combined, {"sA": 0.5, "sB": 0.5})
        assert net["X"].iloc[1] != net["X"].iloc[1]  # 缺供格 NaN
        assert net["X"].iloc[0] == pytest.approx(0.15)


# ──────────────────────────────────────────────────────────────────────────────
# ④ fail-closed 校验
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    """输入校验 fail-closed：非法输入一律 ValueError。"""

    def test_negative_budget_raises(self) -> None:
        combined = pd.DataFrame(
            [[0.1, 0.2]],
            index=pd.date_range("2026-01-05", periods=1),
            columns=pd.MultiIndex.from_tuples([("sA", "X"), ("sB", "Y")], names=["strategy", "symbol"]),
        )
        with pytest.raises(ValueError, match="负预算"):
            split_capital(combined, {"sA": 0.5, "sB": -0.1})

    def test_unknown_strategy_in_budget_raises(self) -> None:
        """未知策略名（budget 含 weights 没有的策略）→ ValueError。"""
        combined = pd.DataFrame(
            [[0.1]],
            index=pd.date_range("2026-01-05", periods=1),
            columns=pd.MultiIndex.from_tuples([("sA", "X")], names=["strategy", "symbol"]),
        )
        with pytest.raises(ValueError, match="未知策略名"):
            split_capital(combined, {"sA": 0.5, "ghost": 0.5})

    def test_missing_strategy_budget_raises(self) -> None:
        """weights 有策略但 budget 未供 → 缺供 fail-closed ValueError。"""
        combined = pd.DataFrame(
            [[0.1, 0.1], [0.2, 0.2]],
            index=pd.date_range("2026-01-05", periods=2),
            columns=pd.MultiIndex.from_tuples([("sA", "X"), ("sB", "X")], names=["strategy", "symbol"]),
        )
        with pytest.raises(ValueError, match="未供预算"):
            split_capital(combined, {"sA": 1.0})

    def test_empty_strategies_raises(self) -> None:
        with pytest.raises(ValueError, match="为空"):
            net_positions({})

    def test_non_dataframe_raises(self) -> None:
        with pytest.raises(ValueError, match="DataFrame"):
            net_positions({"bad": "not a dataframe"})

    def test_duplicate_index_raises(self) -> None:
        idx = pd.DatetimeIndex(["2026-01-05", "2026-01-05"])
        dup = pd.DataFrame({"X": [0.1, 0.2]}, index=idx)
        with pytest.raises(ValueError, match="重复日期"):
            net_positions({"dup": dup})

    def test_non_finite_budget_raises(self) -> None:
        combined = pd.DataFrame(
            [[0.1]],
            index=pd.date_range("2026-01-05", periods=1),
            columns=pd.MultiIndex.from_tuples([("sA", "X")], names=["strategy", "symbol"]),
        )
        with pytest.raises(ValueError, match="非有限"):
            split_capital(combined, {"sA": float("inf")})


# ──────────────────────────────────────────────────────────────────────────────
# ⑤ 输出形状契约（C-9 里程碑一补齐）
# ──────────────────────────────────────────────────────────────────────────────


def _mi_single(strategy: str = "sA", symbol: str = "X", value: float = 0.1) -> pd.DataFrame:
    """构造单格 MultiIndex 权重面（level0=策略名, 末层=标的）。"""
    idx = pd.date_range("2026-01-05", periods=1, freq="B")
    cols = pd.MultiIndex.from_tuples([(strategy, symbol)], names=["strategy", "symbol"])
    return pd.DataFrame([[value]], index=idx, columns=cols)


class TestOutputShapeContract:
    """输出形状：列序字典序确定性、日期并集、单策略恒等、预算和自由。"""

    def test_column_order_is_sorted(self) -> None:
        """净面列序=标的字典序（groupby 确定性输出，与输入面列序无关）。"""
        a = _face({"ZZZ": [0.1, 0.1], "AAA": [0.2, 0.2]})
        b = _face({"MMM": [-0.3, -0.3]})
        net = net_positions({"a": a, "b": b})
        assert list(net.columns) == ["AAA", "MMM", "ZZZ"]

    def test_single_strategy_identity(self) -> None:
        """单策略输入=恒等（列重排为字典序，数值逐格不变；列轴名钉死 'symbol'）。"""
        face = _face({"BBB": [0.3, 0.3], "AAA": [0.1, 0.1]})
        net = net_positions({"solo": face})
        assert list(net.columns) == ["AAA", "BBB"]
        assert net.columns.name == "symbol"  # concat keys 命名传导的确定性契约
        expected = face[["AAA", "BBB"]].rename_axis(columns="symbol")
        pd.testing.assert_frame_equal(net, expected)

    def test_index_is_date_union_monotonic(self) -> None:
        """输出索引=各面日期并集且单调递增（确定性，供下游对齐）。"""
        idx1 = pd.date_range("2026-01-05", periods=2, freq="B")
        idx2 = pd.date_range("2026-01-06", periods=2, freq="B")
        f1 = pd.DataFrame({"X": [0.1, 0.1]}, index=idx1)
        f2 = pd.DataFrame({"X": [0.1, 0.1]}, index=idx2)
        net = net_positions({"f1": f1, "f2": f2})
        assert net.index.is_monotonic_increasing
        assert list(net.index) == list(sorted(idx1.union(idx2)))

    def test_budget_sum_not_constrained_to_one(self) -> None:
        """契约只约束 >=0 有限值——和≠1 合法，逐 sleeve 精确缩放互不挪用。"""
        cols = pd.MultiIndex.from_tuples([("sA", "X"), ("sB", "X")], names=["strategy", "symbol"])
        idx = pd.date_range("2026-01-05", periods=1, freq="B")
        combined = pd.DataFrame([[0.2, 0.1]], index=idx, columns=cols)
        net = split_capital(combined, {"sA": 1.5, "sB": 0.5})
        assert net["X"].iloc[0] == pytest.approx(1.5 * 0.2 + 0.5 * 0.1)


# ──────────────────────────────────────────────────────────────────────────────
# ⑥ fail-closed 扩展面（C-9 里程碑一补齐）
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosedExtended:
    """契约声明但首版未覆盖的非法输入：strategies/weights/budget 三入口穷举。"""

    def test_non_dict_strategies_raises(self) -> None:
        with pytest.raises(ValueError, match="dict"):
            net_positions([_face({"X": [0.1]})])  # type: ignore[arg-type]

    def test_non_string_strategy_name_raises(self) -> None:
        with pytest.raises(ValueError, match="非空字符串"):
            net_positions({1: _face({"X": [0.1]})})  # type: ignore[dict-item]

    def test_empty_string_strategy_name_raises(self) -> None:
        with pytest.raises(ValueError, match="非空字符串"):
            net_positions({"": _face({"X": [0.1]})})

    def test_empty_face_raises(self) -> None:
        with pytest.raises(ValueError, match="为空"):
            net_positions({"a": pd.DataFrame()})

    def test_nan_in_index_raises(self) -> None:
        idx = pd.DatetimeIndex([pd.Timestamp("2026-01-05"), pd.NaT])
        bad = pd.DataFrame({"X": [0.1, 0.2]}, index=idx)
        with pytest.raises(ValueError, match="NaN"):
            net_positions({"a": bad})

    def test_duplicate_columns_raises(self) -> None:
        dup = pd.DataFrame(
            [[0.1, 0.2]],
            index=pd.date_range("2026-01-05", periods=1, freq="B"),
            columns=["X", "X"],
        )
        with pytest.raises(ValueError, match="重复标的"):
            net_positions({"a": dup})

    def test_empty_weights_raises(self) -> None:
        with pytest.raises(ValueError, match="为空"):
            split_capital(pd.DataFrame(), {"sA": 1.0})

    def test_non_multiindex_columns_raises(self) -> None:
        plain = pd.DataFrame([[0.1]], index=pd.date_range("2026-01-05", periods=1, freq="B"), columns=["X"])
        with pytest.raises(ValueError, match="MultiIndex"):
            split_capital(plain, {"sA": 1.0})

    def test_budget_not_dict_raises(self) -> None:
        with pytest.raises(ValueError, match="dict"):
            split_capital(_mi_single(), [("sA", 1.0)])  # type: ignore[arg-type]

    def test_empty_budget_raises(self) -> None:
        with pytest.raises(ValueError, match="为空"):
            split_capital(_mi_single(), {})

    def test_bool_budget_rejected(self) -> None:
        """bool 是 int 子类——显式拒绝（True/False 不是合法资金比例）。"""
        with pytest.raises(ValueError, match="有限数值"):
            split_capital(_mi_single(), {"sA": True})
