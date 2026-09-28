# [MODULE] tests.backtest.test_chart_condition_consumer
# [DEPENDENCIES] pytest; pandas; numpy; zephyr.backtest.regime_validation.chart_condition_consumer; scripts.backtest.condition_attribution
# [CONSUMERS] CI（MODIFY-GUARD 契约钉：src/zephyr/backtest/regime_validation/chart_condition_consumer.py）
# [STARTUP] collected-by-pytest
# [TTL] permanent
"""图形条件轴消费适配器契约钉（st-zcloseout 接线袋出口判据）。

覆盖判据：
  ① 稳定供给面契约：axis_id 冻结、axis_frame 七列逐列对齐判读端消费面；
  ② 地板透传：30 日地板不达 ⇒ cell_id=None 下沉 conditional-free（无统计不是 0）；
  ③ fail-closed 原样上抛（适配层禁吞）：空事件/缺列/多族未定族；
  ④ stratify_key_join：分层键挂接 + 零重叠日炸；
  ⑤ 工件消费红证：save_axis_pack 落盘 ⇒ condition_attribution.attribute_run（生产判读端，
     零改动）直接归因图形胞——接线袋的核心验收（包不再是孤岛）；
  ⑥ 零通道纯度：适配器源码禁 CH/写库通道。
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.condition_attribution import attribute_run
from zephyr.backtest.regime_validation.chart_condition_consumer import (
    AXIS_ID,
    ChartConditionAxisProvider,
    provider_from_events,
    provider_from_pack_dir,
    save_axis_pack,
    stratify_key_join,
)
from zephyr.backtest.regime_validation.condition_package import build_condition_pack

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATES = ("risk_on", "neutral", "risk_off")


def _mk_base_pack(days: int = 600):
    """合成两轴基准包（与 test_chart_condition_package 同构：情绪五档×三态轮转，每胞过地板）。"""
    dates = pd.bdate_range("2021-01-04", periods=days)
    values = [0.1 + 0.18 * (i % 5) for i in range(days)]
    rows = pd.DataFrame(
        {
            "date": dates,
            "value": values,
            "state": [_STATES[i % 3] for i in range(days)],
        }
    )
    return build_condition_pack(rows, start="2021-01-04", end=str(dates[-1].date()), floor_days=30)


def _mk_events(dates: pd.DatetimeIndex, pattern_class: str = "K线", direction: str = "向上") -> pd.DataFrame:
    """合成图形事件：逐日 5 标的同向（breadth 全档饱和 → chart_state 稳定）。"""
    rows = []
    for d in dates:
        for i in range(5):
            rows.append(
                {
                    "anchor_trade_date": d.date(),
                    "direction": direction,
                    "pattern_id": "CDLHAMMER" if pattern_class == "K线" else "PAT-CLL-007",
                    "pattern_class": pattern_class,
                    "symbol": f"60000{i}",
                    "name": "锤子线",
                    "timeframe": "day",
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture()
def provider() -> ChartConditionAxisProvider:
    base = _mk_base_pack()
    events = _mk_events(base.frame["date"])
    return provider_from_events(events, base)


class TestProviderInterface:
    def test_axis_id_is_frozen(self, provider):
        assert provider.axis_id == AXIS_ID == "chart_condition"

    def test_axis_frame_columns_match_judge_consumption_surface(self, provider):
        frame = provider.axis_frame()
        assert list(frame.columns) == [
            "date",
            "family",
            "chart_state",
            "grey_band",
            "state",
            "cell_id",
            "cell_eligible",
        ]
        assert (frame["family"] == "candle").all()
        assert (frame["chart_state"] == "chart_bull").all()
        assert frame["cell_id"].dropna().str.startswith("c").all()  # 胞名 c 前缀命名空间
        assert frame["date"].is_unique

    def test_cells_and_provenance_passthrough(self, provider):
        cells = provider.cells()
        assert {"cell_id", "days", "eligible"} <= set(cells.columns)
        eligible = provider.eligible_cells()
        assert eligible and set(eligible) <= set(cells["cell_id"])
        prov = provider.provenance()
        assert len(prov["closed_book_window"]) == 2
        assert prov["cell_floor_days"] == 30


class TestFloorPassthrough:
    def test_floor_not_reached_sinks_conditional_free(self):
        base = _mk_base_pack()
        events = _mk_events(base.frame["date"])
        provider = provider_from_events(events, base, floor_days=10_000)
        frame = provider.axis_frame()
        assert frame["cell_eligible"].sum() == 0
        assert frame["cell_id"].isna().all()  # 无统计=None 不是 0
        assert provider.eligible_cells() == []


class TestFailClosedPassthrough:
    def test_empty_events_raise(self):
        with pytest.raises(RuntimeError, match="事件框为空"):
            provider_from_events(
                pd.DataFrame(columns=["anchor_trade_date", "direction", "pattern_id", "pattern_class", "symbol"]),
                _mk_base_pack(),
            )

    def test_missing_column_raises(self):
        ev = _mk_events(pd.bdate_range("2021-01-04", periods=5)).drop(columns=["direction"])
        with pytest.raises(KeyError, match="缺列"):
            provider_from_events(ev, _mk_base_pack())

    def test_multi_family_without_family_raises(self):
        base = _mk_base_pack()
        dates = base.frame["date"]
        events = pd.concat([_mk_events(dates), _mk_events(dates.iloc[:60], pattern_class="缠论")])
        provider = provider_from_events(events, base)
        panel = pd.DataFrame({"ret": 0.001}, index=pd.DatetimeIndex(dates))
        with pytest.raises(ValueError, match="禁跨族混算"):
            stratify_key_join(panel, provider)

    def test_unknown_family_raises(self, provider):
        panel = pd.DataFrame({"ret": 0.001}, index=pd.DatetimeIndex(provider.axis_frame()["date"].iloc[:5]))
        with pytest.raises(RuntimeError, match="零行"):
            stratify_key_join(panel, provider, family="chanlun")


class TestStratifyKeyJoin:
    def test_join_attaches_stratification_keys(self, provider):
        dates = pd.DatetimeIndex(provider.axis_frame()["date"])
        panel = pd.DataFrame({"ret": np.sin(np.arange(len(dates)) / 7) * 0.001}, index=dates)
        joined = stratify_key_join(panel, provider)
        assert {"cell_id", "cell_eligible"} <= set(joined.columns)
        assert len(joined) == len(panel)  # inner join 零补行
        assert joined["cell_eligible"].all()
        assert joined["cell_id"].notna().all()

    def test_zero_overlap_raises(self, provider):
        panel = pd.DataFrame({"ret": 0.001}, index=pd.bdate_range("2030-01-01", periods=10))
        with pytest.raises(RuntimeError, match="零重叠日"):
            stratify_key_join(panel, provider)

    def test_missing_date_column_raises(self, provider):
        with pytest.raises(KeyError, match="date"):
            stratify_key_join(pd.DataFrame({"ret": [0.001]}), provider)


class TestArtifactConsumerRoundtrip:
    """核心验收：落盘 ⇒ 生产判读端（condition_attribution，零改动）直接归因图形胞。"""

    def test_attribute_run_consumes_chart_axis_pack(self, provider, tmp_path):
        pack_dir = tmp_path / "chart_pack"
        save_axis_pack(provider, pack_dir)

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        dates = pd.DatetimeIndex(provider.axis_frame()["date"])
        nr = pd.DataFrame(
            {"recipeA": np.sin(np.arange(len(dates)) / 7) * 0.002},
            index=dates,
        )
        nr.index.name = "trade_date"
        nr.to_csv(run_dir / "net_returns.csv")
        nr_file = (run_dir / "net_returns.csv").resolve()
        (run_dir / "summary.json").write_text(json.dumps({"net_returns_file": str(nr_file)}), encoding="utf-8")

        table = attribute_run(run_dir, pack_dir)
        assert not table.empty
        # 归因到的胞是图形三轴命名空间（c<chart_state>|g<band>|s<state>|f<family>）
        assert table["cell_id"].str.startswith("cchart_bull|").all()
        assert table["cell_id"].str.contains("|fcandle", regex=False).all()
        assert (table["days"] >= 30).all()

    def test_offline_readback_roundtrip(self, provider, tmp_path):
        pack_dir = tmp_path / "chart_pack"
        save_axis_pack(provider, pack_dir)
        reborn = provider_from_pack_dir(pack_dir)
        assert reborn.axis_id == AXIS_ID
        pd.testing.assert_frame_equal(reborn.axis_frame(), provider.axis_frame())


class TestZeroChannelPurity:
    def test_adapter_imports_no_ch_or_write_channel(self):
        """AST 红证：适配器 import 面= pandas + 包内委托，禁 CH/写库/内建时钟通道。"""
        import ast

        source = (_REPO_ROOT / "src/zephyr/backtest/regime_validation/chart_condition_consumer.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        banned = {"duckdb", "requests", "urllib", "sqlite3", "sqlalchemy", "clickhouse_connect"}
        assert not roots & banned, f"适配器禁通道 import: {roots & banned}"
        assert roots <= {"__future__", "dataclasses", "pathlib", "typing", "pandas", "zephyr"}, (
            f"适配器依赖面越界: {sorted(roots)}（纯适配=标准库+pandas+zephyr 包内委托）"
        )
