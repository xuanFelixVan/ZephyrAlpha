# [MODULE] tests.backtest.test_chart_condition_package
# [DEPENDENCIES] pytest; pandas; numpy; zephyr.backtest.regime_validation.chart_condition_package
# [CONSUMERS] CI（MODIFY-GUARD 契约钉：src/zephyr/backtest/regime_validation/chart_condition_package.py）
# [STARTUP] collected-by-pytest
# [TTL] permanent
"""图形条件轴接线包的红证测试（波 10 · G-A/G-C.1 出口判据）。

覆盖判据（10_wave_plan 波 10 段 + ext_02 §G-A/§G-C 出口）：
  ① 胞数可复算、30 日地板不达判 INSUFFICIENT（不算绿）；
  ② 喂错状态标签必红；
  ③ 无统计返回 None 而非 0，baseline 行必在；
  ④ 前视注入红证：改未来 bar 不得改过去信号（且对拍证明该尺真的会红）；
  ⑤ 读数失败≠无数据（空框/零重叠必抛不静默）；
  ⑥ 零点火面：本包源码不得含写库/账本/内建时钟。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.regime_validation import chart_condition_package as ccp
from zephyr.backtest.regime_validation.condition_package import build_condition_pack

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATES = ("risk_on", "neutral", "risk_off")


def _mk_base_pack(days: int = 600):
    """合成两轴基准包（工作日上情绪值 0.05 步长轮转×三态轮转——保证每胞过地板）。"""
    dates = pd.bdate_range("2021-01-04", periods=days)
    values = [0.1 + 0.18 * (i % 5) for i in range(days)]  # 0.10/0.28/0.46/0.64/0.82 → 四档
    rows = pd.DataFrame(
        {
            "date": dates,
            "value": values,
            "state": [_STATES[i % 3] for i in range(days)],
        }
    )
    return build_condition_pack(rows, start="2021-01-04", end=str(dates[-1].date()), floor_days=30)


def _mk_events(dates: list[pd.Timestamp], family: str = "K线", direction: str = "向上", n_sym: int = 5) -> pd.DataFrame:
    rows = []
    for d in dates:
        for i in range(n_sym):
            rows.append(
                {
                    "anchor_trade_date": d.date(),
                    "direction": direction,
                    "pattern_id": "CDLHAMMER" if family == "K线" else f"PAT-X-{i}",
                    "pattern_class": family,
                    "symbol": f"60000{i}",
                    "name": "锤子线" if family == "K线" else "假突破反转",
                    "timeframe": "day",
                }
            )
    return pd.DataFrame(rows)


class TestChartStateFromBreadth:
    def test_boundaries_are_frozen_and_labelled(self):
        assert ccp.chart_state_from_breadth(6, 1) == "chart_bull"  # ratio=+0.71
        assert ccp.chart_state_from_breadth(1, 6) == "chart_bear"  # ratio=-0.71
        assert ccp.chart_state_from_breadth(3, 2) == "chart_bull"  # ratio=+0.2 边界含入多头
        assert ccp.chart_state_from_breadth(2, 3) == "chart_bear"  # ratio=-0.2 边界含入空头
        assert ccp.chart_state_from_breadth(3, 4) == "chart_mixed"  # ratio=-0.14
        assert ccp.chart_state_from_breadth(0, 0) == "chart_none"

    @pytest.mark.parametrize("u,d", [(-1, 3), (3, -1)])
    def test_negative_counts_must_go_red(self, u, d):
        with pytest.raises(ValueError, match="事件计数为负"):
            ccp.chart_state_from_breadth(u, d)


class TestFamilyClassification:
    @pytest.mark.parametrize(
        ("pid", "name", "cls", "want"),
        [
            ("CDLHAMMER", "锤子线", "K线", "candle"),
            ("PAT-CLL-007", "缠论一类买点", "缠论", "chanlun"),
            ("PAT-CHART-060", "2B 假突破反转", "反转", "false_breakout"),
            ("busted_double_top", "Busted 双顶", "反转", "false_breakout"),
            ("WYCKOFF_SPRING", "威科夫弹簧/吸筹", "结构", "manipulator"),
            ("WHATEVER", "无名形态", "趋势", "other"),
        ],
    )
    def test_four_named_families_resolve(self, pid, name, cls, want):
        assert ccp.classify_chart_family(pid, name, cls) == want

    def test_family_labels_are_closed_set(self):
        for cls in ("K线", "反转", "持续", "支撑阻力", "缠论", "波浪", "趋势", "结构", ""):
            assert ccp.classify_chart_family("x", "y", cls) in ccp.CHART_AXIS_FAMILIES


class TestBuildChartDailyState:
    def test_breadth_uses_distinct_symbols_and_ignores_neutral(self):
        up = _mk_events([pd.Timestamp("2024-01-02")], direction="向上", n_sym=4)
        down = _mk_events([pd.Timestamp("2024-01-02")], direction="向下", n_sym=1)
        down["symbol"] = ["600100"]
        out = ccp.build_chart_daily_state(pd.concat([up, down], ignore_index=True))
        assert out.iloc[0]["n_up"] == 4 and out.iloc[0]["n_down"] == 1
        assert out.iloc[0]["chart_state"] == "chart_bull"

    def test_missing_column_is_fatal_not_zero(self):
        with pytest.raises(KeyError, match="缺列"):
            ccp.build_chart_daily_state(pd.DataFrame({"date": ["2024-01-02"]}))

    def test_empty_read_must_go_red_not_empty_pack(self):
        with pytest.raises(RuntimeError, match="禁从空读数"):
            ccp.build_chart_daily_state(pd.DataFrame(columns=list(ccp._REQUIRED_EVENT_COLUMNS)))


class TestChartConditionPack:
    def _pack(self):
        base = _mk_base_pack()
        dates = list(base.frame["date"])
        events = pd.concat(
            [
                _mk_events(dates, "K线", "向上", n_sym=9),
                _mk_events(dates, "K线", "向下", n_sym=1),
            ],
            ignore_index=True,
        )
        return base, ccp.build_chart_daily_state(events)

    def test_cell_count_is_recomputable_and_floor_applied(self):
        base, daily = self._pack()
        pack = ccp.build_chart_condition_pack(daily, base, floor_days=30)
        counts = pack.frame.groupby(["chart_state", "grey_band", "state"]).size()
        assert len(pack.cells) == len(counts)
        for row in pack.cells.itertuples(index=False):
            n = int(counts[(row.chart_state, row.grey_band, row.state)])
            assert int(row.days) == n
            assert bool(row.eligible) == (n >= 30)
        assert pack.eligible_cells()

    def test_below_floor_sinks_to_conditional_free(self):
        base, daily = self._pack()
        pack = ccp.build_chart_condition_pack(daily, base, floor_days=10_000)
        assert pack.eligible_cells() == []
        assert pack.frame["cell_id"].isna().all()
        assert not pack.frame["cell_eligible"].any()

    def test_wrong_state_label_must_go_red(self):
        base, daily = self._pack()
        bad = base.frame.copy()
        bad["grey_band"] = "冰点"  # 中文标签不是轴字面量（真源 condition_package._BAND_LABELS）
        with pytest.raises(ValueError, match="未知灰度档"):
            ccp.build_chart_condition_pack(
                daily,
                ccp.ConditionPack(
                    frame=bad,
                    cells=base.cells,
                    closed_book_window=base.closed_book_window,
                    dropped_bands=base.dropped_bands,
                    states=base.states,
                    provenance=base.provenance,
                ),
                floor_days=30,
            )

        d2 = daily.copy()
        d2["chart_state"] = "bullish_hope"
        with pytest.raises(ValueError, match="未知图形档"):
            ccp.build_chart_condition_pack(d2, base, floor_days=30)

    def test_zero_overlap_window_is_fatal(self):
        base, daily = self._pack()
        shifted = daily.copy()
        shifted["date"] = shifted["date"] + pd.Timedelta(days=3650)
        with pytest.raises(RuntimeError, match="零重叠日"):
            ccp.build_chart_condition_pack(shifted, base, floor_days=30)

    def test_all_none_states_cannot_build_two_axis_pack(self):
        base, daily = self._pack()
        neutral = daily.copy()
        neutral["chart_state"] = "chart_none"
        with pytest.raises(RuntimeError, match="chart_none"):
            ccp.build_chart_condition_pack(neutral, base, floor_days=30)

    def test_family_filter_rejects_empty_domain(self):
        base, daily = self._pack()
        with pytest.raises(RuntimeError, match="无图形事件日"):
            ccp.build_chart_condition_pack(daily, base, floor_days=30, keep_families=["manipulator"])


# ── ④ 前视红证（G-C.1 出口判据）────────────────────────────────
class TestLookAheadRedProof:
    @staticmethod
    def _frames():
        # 15M 高周期 bar 收盘时刻：10:15/10:30；1M 低周期行：10:14..10:31
        low = pd.DataFrame(
            {
                "bar_close_ts": pd.to_datetime(
                    [
                        "2024-03-01 10:14",
                        "2024-03-01 10:15",
                        "2024-03-01 10:16",
                        "2024-03-01 10:29",
                        "2024-03-01 10:30",
                        "2024-03-01 10:31",
                    ]
                )
            }
        )
        high = pd.DataFrame(
            {
                "bar_close_ts": pd.to_datetime(["2024-03-01 10:15", "2024-03-01 10:30"]),
                "htf_signal": [1.0, 2.0],
            }
        )
        return low, high

    def test_high_tf_value_visible_only_after_its_close(self):
        low, high = self._frames()
        out = ccp.align_backward(low, high)
        got = out["htf_signal"].to_numpy()
        expected = np.array([np.nan, np.nan, 1.0, 1.0, 1.0, 2.0])
        assert np.array_equal(got, expected, equal_nan=True)  # 10:15 行看不到 10:15 收盘值

    def test_injecting_future_knowledge_does_not_change_past_signal(self):
        low, high = self._frames()
        past = ccp.align_backward(low, high)["htf_signal"].head(3).to_numpy()
        poisoned = high.copy()
        poisoned.loc[poisoned["bar_close_ts"] == pd.Timestamp("2024-03-01 10:30"), "htf_signal"] = 999.0
        after = ccp.align_backward(low, poisoned)["htf_signal"].head(3).to_numpy()
        assert np.array_equal(past, after, equal_nan=True)  # 改未来 bar ⇒ 过去三行信号逐位不变

        poisoned_far = high.copy()
        poisoned_far["htf_signal"] = [-7.0, -8.0]
        both = ccp.align_backward(low, poisoned_far)["htf_signal"].head(3).to_numpy()
        assert not np.array_equal(both, past, equal_nan=True)  # 尺会红：改过去 bar 必被抓（防"永不出红"的死尺）

    def test_naive_forward_join_would_leak(self):
        low, high = self._frames()
        naive = pd.merge_asof(low.sort_values("bar_close_ts"), high, on="bar_close_ts", direction="forward")
        safe = ccp.align_backward(low, high)
        assert not np.array_equal(naive["htf_signal"].to_numpy(), safe["htf_signal"].to_numpy())

    def test_missing_time_column_is_fatal(self):
        low, high = self._frames()
        with pytest.raises(KeyError):
            ccp.align_backward(low.drop(columns=["bar_close_ts"]), high)


# ── ③ 胜率接线桥（G-A.3 出口判据）──────────────────────────────
class TestCellWinRateBridge:
    @staticmethod
    def _events(n: int, direction: str = "向上"):
        dates = pd.bdate_range("2024-01-01", periods=n)
        return pd.DataFrame(
            {
                "family": ["candle"] * n,
                "cell_id": ["cchart_bull|gmild|srisk_on|fcandle"] * n,
                "direction": [direction] * n,
                "fwd_ret_key": [ccp.make_fwd_key("600000", d) for d in dates],
            }
        )

    @staticmethod
    def _returns(n: int, value: float):
        dates = pd.bdate_range("2024-01-01", periods=n)
        return pd.Series({ccp.make_fwd_key("600000", d): value for d in dates})

    def test_baseline_row_present_and_cell_rows_present(self):
        out = ccp.cell_win_rate(self._events(40), {5: self._returns(40, 0.01)})
        base = out[out["family"] == ccp._BASELINE_ID]
        assert len(base) == 1 and base.iloc[0]["n_events"] == 40
        assert len(out[out["family"] == "candle"]) == 1
        assert float(out[out["family"] == "candle"].iloc[0]["hit_rate"]) == 1.0

    def test_downward_direction_hit_definition_is_mirror(self):
        out = ccp.cell_win_rate(self._events(40, "向下"), {5: self._returns(40, 0.01)})
        assert float(out[out["family"] == "candle"].iloc[0]["hit_rate"]) == 0.0

    def test_insufficient_sample_is_none_not_zero(self):
        out = ccp.cell_win_rate(self._events(3), {5: self._returns(3, 0.02)})
        cell = out[out["family"] == "candle"].iloc[0]
        assert cell["hit_rate"] is None or (isinstance(cell["hit_rate"], float) and np.isnan(cell["hit_rate"]))
        assert bool(cell["low_sample"]) is True

    def test_unmatured_events_are_dropped_not_zero_filled(self):
        out = ccp.cell_win_rate(self._events(40), {5: self._returns(10, 0.01)})
        assert int(out[out["family"] == "candle"].iloc[0]["n_events"]) == 10

    def test_no_matured_rows_raises_instead_of_green_zero(self):
        with pytest.raises((RuntimeError, KeyError)):
            ccp.cell_win_rate(self._events(40), {5: self._returns(40, np.nan)})

    def test_unknown_fwd_window_rejected(self):
        with pytest.raises(ValueError, match="不在册"):
            ccp.cell_win_rate(self._events(40), {7: self._returns(40, 0.01)})

    def test_missing_join_key_column_fatal(self):
        with pytest.raises(KeyError, match="缺列"):
            ccp.cell_win_rate(pd.DataFrame({"family": ["candle"]}), {5: self._returns(3, 0.1)})


# ── 落盘契约（既有判读端零改动消费）───────────────────────────
class TestPersistenceContract:
    def test_roundtrip_matches_attribution_column_contract(self, tmp_path):
        base = _mk_base_pack()
        daily = ccp.build_chart_daily_state(
            pd.concat(
                [
                    _mk_events(list(base.frame["date"]), "K线", "向上", n_sym=9),
                    _mk_events(list(base.frame["date"]), "K线", "向下", n_sym=1),
                ],
                ignore_index=True,
            )
        )
        pack = ccp.build_chart_condition_pack(daily, base, floor_days=30)
        fp = ccp.save_pack(pack, tmp_path)
        assert fp.exists()
        # 判读端（condition_attribution.attribute_run）按此二列归因——列名与语义必须保真
        back = ccp.load_pack(tmp_path)
        assert {"cell_id", "cell_eligible"} <= set(back.frame.columns)
        # 真消费面：判读端 scripts/backtest/condition_attribution.py import 的是基准包的 load_pack，
        # 用它读本包产物——键名/列名契约不合即红（本道实测炸过一次 KeyError: closed_book_window）
        from zephyr.backtest.regime_validation.condition_package import load_pack as base_load_pack

        cross = base_load_pack(tmp_path)
        assert {"cell_id", "cell_eligible"} <= set(cross.frame.columns)
        assert sorted(cross.frame["cell_id"].dropna().unique()) == sorted(pack.frame["cell_id"].dropna().unique())
        assert back.eligible_cells() == pack.eligible_cells()
        assert tuple(back.provenance["axis_families"]) == ("candle",)


# ── ⑥ 零点火/零写库面（红线机械自证）──────────────────────────
class TestNoIgnitionSurface:
    FORBIDDEN = ("n_trial_ledger", "INSERT INTO", "ch_writer", "datetime.now(", "time.time(", "execute(")

    def test_source_carries_no_write_or_clock_surface(self):
        src = (_REPO_ROOT / "src/zephyr/backtest/regime_validation/chart_condition_package.py").read_text(
            encoding="utf-8"
        )
        body = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
        for tok in self.FORBIDDEN:
            if tok == "execute(":
                assert "c.execute(sql)" in body  # 只读通道允许 execute(sql)，写路径必须没有
                assert "insert" not in body.lower()
                continue
            assert tok not in body, f"接线件出现点火/写库面 token={tok}"

    def test_builtin_clock_is_guarded(self):
        with pytest.raises(NotImplementedError):
            ccp.today_safe()


# ── ⑦ 同源实现/表名真源（FUNCTION-DUP + TABLE-NAME-REGISTRY 红证）────
class _FakeConn:
    """假读数通道：只记账 SQL 并回放预置行（零真连、零写库）。"""

    def __init__(self, rows):
        self._rows = rows
        self.sql: str | None = None

    def execute(self, sql):
        self.sql = sql
        return self._rows


def _pack_rows(dates):
    """事件明细 DataFrame → conn.execute 元组流（列序=SELECT 列序，同源纪律）。"""
    ev = _mk_events(list(dates), "K线", "向上", n_sym=4)
    return [tuple(r) for r in ev.itertuples(index=False)], ev


class TestSingleImplementationAndTableTruthSource:
    def test_save_pack_is_reused_not_recopied(self):
        """落盘只有一份实现：本件必须复用 condition_package.save_pack（净零法）。"""
        from zephyr.backtest.regime_validation import condition_package as cp

        assert ccp.save_pack is cp.save_pack

    def test_save_pack_not_redefined_here(self):
        """红证：本件源码若再出现 save_pack 的 def（复制粘贴回潮），必判红。"""
        import ast

        src = (_REPO_ROOT / "src/zephyr/backtest/regime_validation/chart_condition_package.py").read_text(
            encoding="utf-8"
        )
        defs = {n.name for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}
        assert "save_pack" not in defs, "save_pack 被二次实现（FUNCTION-DUP 回潮）"

    def test_no_registered_table_name_literal_in_source(self):
        """表名只能经 TableRegistry 解析：源码里不得出现任何在册库表字面量。"""
        import ast

        from zephyr.data.table_registry import TableRegistry

        tables = set(TableRegistry().all_tables())
        rel = "src/zephyr/backtest/regime_validation/chart_condition_package.py"
        tree = ast.parse((_REPO_ROOT / rel).read_text(encoding="utf-8"))
        hits = [
            (node.lineno, node.value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and any(tb in node.value for tb in tables)
        ]
        assert hits == [], f"{rel} 出现硬编码表名字面量: {hits}"

    def test_sql_table_name_follows_registry(self):
        """变异红证：把注册表换成哨兵表名，SQL 必随注册表变（证明没有硬编码兜底）。"""

        class _SentinelRegistry:
            @staticmethod
            def table(category_id):
                assert category_id == ccp._EVENT_CATEGORY
                return "sentinel_db.sentinel_table"

        original = ccp.get_registry
        ccp.get_registry = lambda: _SentinelRegistry
        try:
            conn = _FakeConn([])
            with pytest.raises(RuntimeError):  # 空读数必抛，不静默出空包
                ccp.load_market_pattern_events("2024-01-01", "2024-03-01", conn=conn)
        finally:
            ccp.get_registry = original
        assert "sentinel_db.sentinel_table" in (conn.sql or "")
        assert ccp._EVENT_CATEGORY not in (conn.sql or "")

    def test_registry_resolves_the_undocumented_shape_event_table(self):
        """品类名在册且解析出的表名与本波形态事件表一致（禁凭记忆编品类）。"""
        from zephyr.data.table_registry import TableRegistry

        resolved = TableRegistry().table(ccp._EVENT_CATEGORY)
        assert resolved == ccp.event_table()
        assert resolved.endswith(".market_pattern_event")
        assert "{table}" in ccp._SQL_EVENTS  # 模板自身不含表名

    def test_request_object_end_to_end_pack(self):
        """8 参收敫为 ChartPackRequest 后，端到端装配面仍被真跑（含 provenance 双键）。"""
        base = _mk_base_pack(600)
        rows, ev = _pack_rows(base.frame["date"])
        conn = _FakeConn(rows)
        req = ccp.ChartPackRequest(
            start="2021-01-04",
            end=str(base.frame["date"].max().date()),
            base_pack=base,
        )
        pack = ccp.load_chart_condition_pack(req, conn=conn)
        assert {"cell_id", "cell_eligible"} <= set(pack.frame.columns)
        assert pack.provenance["event_rows_read"] == len(ev)
        assert pack.provenance["event_sample_prefix"] == "FULL_UNIVERSE"
        assert pack.provenance["event_table"] == ccp._EVENT_CATEGORY
        assert pack.eligible_cells()

    def test_request_object_defaults_are_the_frozen_calibration(self):
        """入参对象默认值=冻结口径（地板 30 日、有界读数上界），禁随手改默认。"""
        req = ccp.ChartPackRequest(start="2024-01-01", end="2024-03-01")
        assert req.floor_days == ccp._CELL_FLOOR_DAYS == 30
        assert req.event_limit == 2_000_000
        assert (req.keep_families, req.symbol_prefix, req.base_pack) == (None, None, None)
