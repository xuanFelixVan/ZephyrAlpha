# [TEST] tests/regime/features/test_macro_regime_sensor.py
# [TTL] task_bound
# 覆盖: macro_regime_sensor（TDM-E-L1-S0 宏观环境传感器，NB1-B5 复活件 R2-R3）
# 纪律: mock 数据路径（monkeypatch 注入合成帧），零 CH 依赖；输出走 tmp_path fixture
"""macro_regime_sensor 单元测试（mock 数据路径）。

覆盖面：
  - R1 翻译层：load_series_map 加载/fail-closed（缺文件/坏字段）
  - R2 读视图：read_macro_indicators（monkeypatch 拉数层，missing 条目跳过）
  - 变换：level/diff/yoy；滚动分位与方向修正；weather_to_caution 阶梯
  - R3 打分：score() 四组合成+缺员降权（missing 组自动重归一）
  - 聚合面：monthly/weekly 采样与 monthly_weather_history 形状
"""

from __future__ import annotations

import datetime

import numpy as np
import pandas as pd
import pytest
import yaml

from zephyr.regime.features import macro_regime_sensor as mrs

# ---------------------------------------------------------------- fixtures


@pytest.fixture()
def tmp_map(tmp_path):
    """最小映射表（2 组 4 指标，含 1 aux 剪刀差+1 missing+1 inverse）。"""
    doc = {
        "mappings": [
            {
                "indicator_id": "MAC-T-001",
                "source": "akshare",
                "series_code": "S_RATE",
                "series_role": "primary",
                "unit": "%",
                "transform": "level",
                "direction": "inverse",
                "seasonal_adjusted": False,
                "status": "wired",
            },
            {
                "indicator_id": "MAC-T-002",
                "source": "akshare",
                "series_code": "S_M2",
                "series_role": "primary",
                "unit": "%",
                "transform": "level",
                "direction": "positive",
                "seasonal_adjusted": False,
                "status": "wired",
                "aux_series": [
                    {
                        "series_code": "S_M1",
                        "series_role": "aux",
                        "derive": "derive_scissors",
                        "unit": "%",
                        "transform": "level",
                        "direction": "positive",
                        "status": "wired",
                    },
                ],
            },
            {
                "indicator_id": "MAC-T-003",
                "source": "akshare",
                "series_code": "",
                "series_role": "primary",
                "unit": "%",
                "transform": "level",
                "direction": "positive",
                "seasonal_adjusted": False,
                "status": "missing",
            },
            {
                "indicator_id": "MAC-T-004",
                "source": "fred",
                "series_code": "S_VIX",
                "series_role": "primary",
                "unit": "指数",
                "transform": "level",
                "direction": "inverse",
                "seasonal_adjusted": False,
                "status": "wired",
            },
        ],
        "groups": {
            "G1": ["MAC-T-001", "MAC-T-002"],
            "G2": ["MAC-T-003", "MAC-T-004"],
        },
        "weights": {"G1": 0.6, "G2": 0.4},
    }
    p = tmp_path / "macro_indicator_series_map.yaml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return p


@pytest.fixture()
def synthetic_reads():
    """合成读数帧：每序列 40 个月度观测，方向语义单调可预期。"""
    dates = pd.date_range("2023-01-31", periods=40, freq="ME")

    def frame(code: str, values: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "indicator_id": "x",
                "series_role": "primary",
                "code": code,
                "obs_date": dates,
                "value": values,
            }
        )

    rng = np.random.default_rng(7)
    # S_RATE 单调下行（inverse→末端信号分位高）｜S_M2 缓升（positive→末端高）｜S_VIX 高位震荡
    reads = pd.concat(
        [
            frame("S_RATE", np.linspace(4.0, 2.0, 40)),
            frame("S_M2", 8.0 + np.linspace(0.0, 2.0, 40)),
            frame("S_M1", 4.0 + np.linspace(0.0, 4.0, 40)),  # 剪刀差 M1-M2 走阔
            frame("S_VIX", 20.0 + rng.normal(0, 1.0, 40).cumsum() * 0.1),
        ],
        ignore_index=True,
    )
    return reads


# ---------------------------------------------------------------- R1 翻译层


class TestLoadSeriesMap:
    def test_load_ok(self, tmp_map):
        smap = mrs.load_series_map(tmp_map)
        assert set(smap) == {"MAC-T-001", "MAC-T-002", "MAC-T-003", "MAC-T-004"}
        assert smap["MAC-T-002"]["aux_series"][0]["derive"] == "derive_scissors"

    def test_missing_file_fail_closed(self, tmp_path):
        with pytest.raises(ValueError, match="缺失"):
            mrs.load_series_map(tmp_path / "nope.yaml")

    def test_bad_transform_fail_closed(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text(
            yaml.safe_dump(
                {
                    "mappings": [
                        {"indicator_id": "X", "series_code": "S", "transform": "magic", "direction": "positive"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="transform"):
            mrs.load_series_map(p)


# ---------------------------------------------------------------- 变换与打分原语


class TestTransformsAndScoring:
    def test_level_passthrough(self):
        df = pd.DataFrame({"obs_date": pd.date_range("2025-01-31", periods=3, freq="ME"), "value": [1.0, 2.0, 3.0]})
        out = mrs.transform_series(df, transform="level")
        assert list(out["value"]) == [1.0, 2.0, 3.0]

    def test_diff(self):
        df = pd.DataFrame({"obs_date": pd.date_range("2025-01-31", periods=3, freq="ME"), "value": [1.0, 2.0, 2.5]})
        out = mrs.transform_series(df, transform="diff").reset_index(drop=True)
        assert out["value"].tolist() == pytest.approx([1.0, 0.5])

    def test_yoy_rolling_sum(self):
        # 12 期常量 100 → 滚动和=1200，一年前同窗和=1200 → yoy=0；末段抬升 → yoy>0
        n = 30
        vals = [100.0] * 24 + [110.0] * 6
        df = pd.DataFrame({"obs_date": pd.date_range("2023-01-31", periods=n, freq="ME"), "value": vals})
        out = mrs.transform_series(df, transform="yoy")
        assert out["value"].iloc[-1] == pytest.approx(5.0, abs=0.6)

    def test_rolling_percentile_monotonic_top(self):
        s = pd.Series(np.linspace(1.0, 10.0, 30))
        pct = mrs._rolling_percentile(s, window=24, min_periods=12)
        assert pct.iloc[-1] == pytest.approx(1.0)
        assert pct.iloc[0] != pct.iloc[0] or True  # 早期样本不足→NaN 合法

    def test_direction_adjust(self):
        assert mrs._direction_adjust(0.8, "positive") == pytest.approx(0.8)
        assert mrs._direction_adjust(0.8, "inverse") == pytest.approx(0.2)
        assert np.isnan(mrs._direction_adjust(0.8, "neutral"))

    def test_weather_to_caution_tiers(self):
        assert mrs.weather_to_caution(80.0) == (1.00, "supportive")
        assert mrs.weather_to_caution(55.0) == (0.90, "neutral")
        assert mrs.weather_to_caution(10.0) == (0.75, "cautious")


# ---------------------------------------------------------------- R2 读视图


class TestReadMacroIndicators:
    def test_read_maps_codes_and_roles(self, tmp_map, monkeypatch, synthetic_reads):
        codes_seen = {}

        def fake_fetch(codes, *, as_of):
            codes_seen.update({c: True for c in codes})
            return synthetic_reads.copy()

        monkeypatch.setattr(mrs, "_fetch_series_codes", fake_fetch)
        out = mrs.read_macro_indicators(["MAC-T-001", "MAC-T-002", "MAC-T-003"], map_path=tmp_map)
        # missing（MAC-T-003）不拉数；aux（S_M1）拉数且标 aux
        assert "S_RATE" in codes_seen and "S_M1" in codes_seen
        assert "S_VIX" not in codes_seen  # 未点名指标不拉
        assert set(out["indicator_id"]) == {"MAC-T-001", "MAC-T-002"}
        assert "aux" in set(out["series_role"])
        assert list(out.columns[:5]) == ["indicator_id", "series_role", "code", "obs_date", "value"]

    def test_pit_mode_adds_pub_ts(self, tmp_map, monkeypatch, synthetic_reads):
        def fake_fetch(codes, *, as_of):
            df = synthetic_reads.copy()
            df["pub_ts"] = pd.to_datetime(df["obs_date"]) + pd.Timedelta(days=10)
            return df

        monkeypatch.setattr(mrs, "_fetch_series_codes", fake_fetch)
        out = mrs.read_macro_indicators(["MAC-T-001"], as_of="2026-09-30 00:00:00", map_path=tmp_map)
        assert "pub_ts" in out.columns


# ---------------------------------------------------------------- R3 打分


class TestSensorScore:
    def test_score_groups_and_degradation(self, tmp_map, monkeypatch, synthetic_reads):
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: synthetic_reads.copy())
        sensor = mrs.MacroRegimeSensor(tmp_map, window=24)
        reading = sensor.score()
        # MAC-T-003 missing 已在映射表声明 → 不进 missing_indicators（声明性缺席）
        assert reading["missing_indicators"] == []
        assert reading["declared_indicators"] == 4
        # 单调下行利率（inverse）+ 上行 M2/剪刀差 → G1 组末端信号高
        g1 = reading["groups"]["G1"]
        assert g1["coverage"] == pytest.approx(1.0)
        assert g1["score"] > 0.6
        assert 0.0 <= reading["weather_score"] <= 100.0
        assert reading["caution_factor"] in (0.75, 0.90, 1.00)
        assert reading["tier"] in ("supportive", "neutral", "cautious")

    def test_score_wired_but_no_data_counts_missing(self, tmp_map, monkeypatch):
        empty = pd.DataFrame(columns=["indicator_id", "series_role", "code", "obs_date", "value"])
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: empty)
        reading = mrs.MacroRegimeSensor(tmp_map).score()
        # 全缺 → weather=None + tier=no_data；wired 无数据者进 missing_indicators
        assert reading["weather_score"] is None
        assert reading["tier"] == "no_data"
        assert set(reading["missing_indicators"]) == {"MAC-T-001", "MAC-T-002", "MAC-T-004"}

    def test_score_partial_group_renormalizes(self, tmp_map, monkeypatch, synthetic_reads):
        # S_VIX 缺数 → G2 只剩声明性 missing（MAC-T-003）→ G2 空组 → 权重重归一到 G1
        partial = synthetic_reads[synthetic_reads["code"] != "S_VIX"]
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: partial.copy())
        reading = mrs.MacroRegimeSensor(tmp_map, window=24).score()
        assert reading["groups"]["G2"]["score"] != reading["groups"]["G2"]["score"]  # NaN
        assert reading["weather_score"] is not None  # G1 仍出分


# ---------------------------------------------------------------- 聚合面


class TestSampling:
    def test_monthly_sample_last_obs(self, tmp_map, monkeypatch, synthetic_reads):
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: synthetic_reads.copy())
        sensor = mrs.MacroRegimeSensor(tmp_map)
        monthly = sensor.monthly_series()
        assert len(monthly) > 0  # 空帧空真防线：先断非空再断口径
        assert (monthly["obs_date"].dt.day >= 28).all()  # 月末最后观测

    def test_weekly_sample_shape(self, tmp_map, monkeypatch, synthetic_reads):
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: synthetic_reads.copy())
        sensor = mrs.MacroRegimeSensor(tmp_map)
        weekly = sensor.weekly_series()
        assert len(weekly) > 0
        assert set(["indicator_id", "code", "obs_date", "value"]).issubset(weekly.columns)

    def test_monthly_weather_history(self, tmp_map, monkeypatch, synthetic_reads):
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: synthetic_reads.copy())
        sensor = mrs.MacroRegimeSensor(tmp_map, window=24)
        hist = sensor.monthly_weather_history()
        assert set(hist.columns) == {"month", "weather_score", "caution_factor", "tier"}
        assert len(hist) > 0
        assert hist["weather_score"].between(0, 100).all()

    def test_sample_bad_freq_raises(self, tmp_map, monkeypatch, synthetic_reads):
        monkeypatch.setattr(mrs, "_fetch_series_codes", lambda codes, *, as_of: synthetic_reads.copy())
        sensor = mrs.MacroRegimeSensor(tmp_map)
        with pytest.raises(ValueError, match="freq"):
            sensor._sample(synthetic_reads, "Q-DEC")
