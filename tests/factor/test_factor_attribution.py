# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""D-FACTOR-ANA-09 因子归因测试——纯函数模块（无 IO 依赖）。

覆盖：
- attribute_by_time: 空输入 / 按月聚合正确 / 按季聚合
- attribute_by_sector: 空输入 / 行业归因分组 / 缺失行业映射="未知" / 单行业
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

factor_attribution = pytest.importorskip("zephyr.factor.analysis.factor_attribution")

attribute_by_time = factor_attribution.attribute_by_time
attribute_by_sector = factor_attribution.attribute_by_sector


class TestAttributeByTime:
    def test_empty_input(self):
        result = attribute_by_time(pd.Series([], dtype=float))
        assert result.empty

    def test_monthly_aggregation(self):
        dates = pd.to_datetime(["2026-01-10", "2026-01-20", "2026-02-15", "2026-03-10"])
        ic = pd.Series([0.1, 0.2, 0.3, 0.4], index=dates)
        # 使用非弃用的 "ME"（month end）别名，避免 pandas 2.x FutureWarning
        result = attribute_by_time(ic, freq="ME")
        # 3 个月：1月均值(0.1,0.2)=0.15, 2月=0.3, 3月=0.4
        assert len(result) == 3
        jan_val = result.loc[pd.Timestamp("2026-01-31")]
        assert abs(jan_val - 0.15) < 1e-10
        assert abs(result.loc[pd.Timestamp("2026-02-28")] - 0.3) < 1e-10
        assert abs(result.loc[pd.Timestamp("2026-03-31")] - 0.4) < 1e-10

    def test_quarterly_aggregation(self):
        dates = pd.to_datetime(["2026-01-10", "2026-04-10", "2026-07-10"])
        ic = pd.Series([0.1, 0.3, 0.5], index=dates)
        # 使用非弃用的 "QE"（quarter end）别名
        result = attribute_by_time(ic, freq="QE")
        # 3 个季度各 1 个值
        assert len(result) == 3

    def test_string_index_converted_to_datetime(self):
        # 字符串日期 index 也能正确聚合
        ic = pd.Series(
            [0.1, 0.2, 0.3],
            index=["2026-01-10", "2026-01-20", "2026-02-15"],
        )
        result = attribute_by_time(ic, freq="ME")
        assert len(result) == 2
        assert abs(result.iloc[0] - 0.15) < 1e-10

    @pytest.mark.filterwarnings("ignore::FutureWarning")
    def test_default_freq_from_config(self):
        # 默认 freq="M"（来自 _config.yaml，pandas 2.x 弃用 'M' 但配置未更新）
        # 此处测试 freq=None 时走配置读取路径，忽略 pandas 弃用告警
        dates = pd.to_datetime(["2026-01-10", "2026-02-15"])
        ic = pd.Series([0.1, 0.3], index=dates)
        result = attribute_by_time(ic)
        assert len(result) == 2


class TestAttributeBySector:
    def test_empty_input(self):
        result = attribute_by_sector(
            pd.Series([], dtype=float),
            pd.Series([], dtype=float),
            {},
        )
        assert result.empty

    def test_sector_grouping(self):
        fv = pd.Series([1.0, 2.0, 3.0, 4.0], index=list("ABCD"))
        fr = pd.Series([10.0, 20.0, 30.0, 40.0], index=list("ABCD"))
        sector_map = {"A": "科技", "B": "科技", "C": "金融", "D": "消费"}
        result = attribute_by_sector(fv, fr, sector_map)
        assert set(result.index) == {"科技", "金融", "消费"}
        assert list(result.columns) == ["avg_factor", "avg_return", "count"]
        # 科技: 2 个标的
        assert result.loc["科技", "count"] == 2
        assert abs(result.loc["科技", "avg_factor"] - 1.5) < 1e-10
        assert abs(result.loc["科技", "avg_return"] - 15.0) < 1e-10
        # 金融: 1 个标的
        assert result.loc["金融", "count"] == 1
        assert abs(result.loc["金融", "avg_factor"] - 3.0) < 1e-10

    def test_missing_sector_mapped_to_unknown(self):
        fv = pd.Series([1.0, 2.0, 3.0], index=list("AXY"))
        fr = pd.Series([10.0, 20.0, 30.0], index=list("AXY"))
        sector_map = {"A": "科技"}  # X, Y 无映射
        result = attribute_by_sector(fv, fr, sector_map)
        assert "未知" in result.index
        assert result.loc["未知", "count"] == 2
        assert "科技" in result.index
        assert result.loc["科技", "count"] == 1

    def test_single_sector(self):
        fv = pd.Series([1.0, 2.0, 3.0], index=list("ABC"))
        fr = pd.Series([10.0, 20.0, 30.0], index=list("ABC"))
        sector_map = {"A": "科技", "B": "科技", "C": "科技"}
        result = attribute_by_sector(fv, fr, sector_map)
        assert len(result) == 1
        assert result.index[0] == "科技"
        assert result.loc["科技", "count"] == 3
        assert abs(result.loc["科技", "avg_factor"] - 2.0) < 1e-10
        assert abs(result.loc["科技", "avg_return"] - 20.0) < 1e-10

    def test_nan_dropped(self):
        fv = pd.Series([1.0, float("nan"), 3.0], index=list("ABC"))
        fr = pd.Series([10.0, 20.0, 30.0], index=list("ABC"))
        sector_map = {"A": "科技", "B": "科技", "C": "金融"}
        result = attribute_by_sector(fv, fr, sector_map)
        # B 的因子值为 NaN → 被剔除，只剩 A, C
        assert result.loc["科技", "count"] == 1
        assert result.loc["金融", "count"] == 1

    def test_no_common_index(self):
        fv = pd.Series([1.0, 2.0], index=["A", "B"])
        fr = pd.Series([10.0, 20.0], index=["C", "D"])
        result = attribute_by_sector(fv, fr, {"A": "科技", "B": "科技"})
        assert result.empty
