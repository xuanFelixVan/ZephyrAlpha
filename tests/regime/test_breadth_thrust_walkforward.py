# [A_test] module_id: MOD-TEST-BREADTH-WF | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | 14 号 §4.5 / OVB-4
# [MODULE] tests.regime.test_breadth_thrust_walkforward
# [DOMAIN] D_REGIME
# [DEPENDENCIES] scripts.regime_breadth_thrust_walkforward; zephyr.regime.features.overlay_features;
#   zephyr.regime.validation.overfitting_guard; zephyr.data.table_registry; pandas; numpy; pytest
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR-CONTRACT] AssertionError->fail
# [TESTS] tests/regime/test_breadth_thrust_walkforward.py
# [TTL] permanent
# [ARCH-REF] #MOD-REGIME-002 #10_regime_detector_spec §4.12 #14_regime_s2_diagnosis §4.5 #OVB-4
# 覆盖：scripts/regime_breadth_thrust_walkforward.py（台账 s2_breadth_thrust 清偿证据链）离线口径
"""test_breadth_thrust_walkforward.py — S2 breadth_thrust 重校管线单元测试（OVB-4 清偿件）。

分组：
  1. 引擎真源零漂移（score_for_config == 生产 s2_breadth_thrust_score；漂移必炸）
  2. 进料口纪律（表名经 TableRegistry 解析；只读 role；产物只落临时区）
  3. 统计口径（percentile_of / 事件窗裁剪 / 预热与死日剔除 / 折划分）
  4. 反未来函数（段指标与选值对 end 之后的数据零感知）
  5. 预注册机械判据（passes_acceptance 双边界 + 缺值即不过；注册表 hash 锁）
  6. 与台账的闭环（harness 在位、无裸客户端、ALERT 计数不回升）

禁网禁库：全部合成序列 + tmp_path（不触 ClickHouse、不写 data/）。
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from scripts import regime_breadth_thrust_walkforward as wf
from zephyr.regime.features.overlay_features import s2_breadth_thrust_score
from zephyr.regime.validation.overfitting_guard import PreRegistrationRegistry

_HARNESS_PATH = Path(__file__).resolve().parents[2] / "scripts" / "regime_breadth_thrust_walkforward.py"

# ---------------------------------------------------------------------------
# 合成广度序列：确定性 45 日周期（quiet → washout → thrust），无随机源可重放
# ---------------------------------------------------------------------------
_LEG = 15
_CYCLE = _LEG * 3
#: 三段瞬时 adv/(adv+dec)：washout 腿极低、thrust 腿极高 → EMA10 必双侧穿越 0.40 / 0.615
_RATIO_BY_PHASE: dict[int, float] = {0: 0.50, 1: 0.08, 2: 0.96}
_TOTAL_ISSUES = 1000.0


def _synthetic_frame(n_days: int = 45 * 24, *, start: str = "2015-01-05") -> pd.DataFrame:
    """index=交易日，列 adv/dec/close/live——与 load_breadth 输出同构的注入假数据。"""
    idx = pd.bdate_range(start=start, periods=n_days)
    phase = (np.arange(n_days) % _CYCLE) // _LEG
    ratio = np.array([_RATIO_BY_PHASE[int(p)] for p in phase], dtype=float)
    i = np.arange(n_days, dtype=float)
    close = 100.0 * (1.0 + 0.0004) ** i * (1.0 + 0.01 * np.sin(i / 9.0))
    return pd.DataFrame(
        {
            "adv": ratio * _TOTAL_ISSUES,
            "dec": (1.0 - ratio) * _TOTAL_ISSUES,
            "close": close,
            "live": np.ones(n_days, dtype=bool),
        },
        index=idx,
    )


def _flat_frame(n_days: int = 900) -> pd.DataFrame:
    """adv=dec 恒等 → EMA 恒 0.5：任何 thrust 候选在线率都是 0（"无点通过"路径）。"""
    frame = _synthetic_frame(n_days)
    frame["adv"] = 500.0
    frame["dec"] = 500.0
    return frame


#: run_walkforward 会逐段算 PREREG_REPORT_WINDOWS（2005/2014/2019）→ 母体须横跨全窗，
#: 否则撞 [ERROR_CONTRACT]「段窗口无数据->ValueError」（正是禁出"半张报告"的 fail-closed 设计）。
def _wf_frame() -> pd.DataFrame:
    return _synthetic_frame(5200, start=wf.PREREG_SERIES_START)


# ---------------------------------------------------------------------------
# 1. 引擎真源零漂移
# ---------------------------------------------------------------------------
class TestMirrorDiscipline:
    """诊断版与生产版漂移=报告作废，故等值性必须是断言而非注释。"""

    def test_score_for_config_equals_production_on_current_params(self):
        frame = _synthetic_frame()
        mine = wf.score_for_config(frame["adv"], frame["dec"])
        prod = s2_breadth_thrust_score(frame["adv"], frame["dec"])
        pd.testing.assert_series_equal(mine, prod, check_names=False)

    def test_mirror_covers_the_full_four_level_ladder(self):
        """合成母体必须真跑到 0/30/60/80 四级（缺一级的分布不代表生产工况，自检失效）。"""
        score = wf.score_for_config(_synthetic_frame()["adv"], _synthetic_frame()["dec"], wf.ThrustConfig())
        assert set(score.round(1).unique()) == {0.0, 30.0, 60.0, 80.0}
        assert int((score >= 80).sum()) > 0, "合成序列从未出现完整 thrust → 母体不具代表性"

    def test_verify_mirror_returns_day_count(self):
        frame = _synthetic_frame()
        assert wf.verify_mirror(frame["adv"], frame["dec"]) == int(len(frame))

    def test_verify_mirror_raises_when_production_diverges(self, monkeypatch):
        """生产函数被改（或本文件常量忘同步）→ 必炸，禁出"看起来对"的报告。"""
        frame = _synthetic_frame()
        monkeypatch.setattr(
            wf,
            "s2_breadth_thrust_score",
            lambda a, d, ema_window=10: s2_breadth_thrust_score(a, d) + 1.0,
        )
        with pytest.raises(ValueError, match="禁双实现"):
            wf.verify_mirror(frame["adv"], frame["dec"])

    def test_mirror_constants_are_still_read_back_from_production_source(self):
        """镜像常量（EMA 窗/两阈值）须仍出现在生产签名与函数体内——防"改产阈值忘改校准器"。"""
        src = inspect.getsource(s2_breadth_thrust_score)
        assert f"ema_window: int = {wf.PROD_EMA_WINDOW}" in src
        assert f"> {wf.PROD_IMPROVE_FLOOR}" in src
        for level, literal in ((wf.CURRENT_THRUST, "0.615"), (wf.CURRENT_WASHOUT, "0.40")):
            assert literal in src, f"生产函数体已不含 {literal}，但 harness 仍镜像它"
            assert float(literal) == level


# ---------------------------------------------------------------------------
# 2. 进料口纪律（CH 只读 + TableRegistry 真源，禁裸客户端/禁写 data/）
# ---------------------------------------------------------------------------
class _FakeCH:
    """最小 ClickHouse 替身：只实现 load_breadth 用到的 execute(sql, params, with_column_types=True)。"""

    def __init__(self, tables: dict[str, pd.DataFrame]):
        self._tables = tables
        self.queries: list[str] = []

    def execute(self, sql: str, params: Any = None, with_column_types: bool = False):  # noqa: ANN001
        self.queries.append(sql)
        for marker, frame in self._tables.items():
            if marker in sql:
                cols = [("trade_date", "Date")] + [(c, "Float64") for c in frame.columns]
                rows = [[d, *row] for d, row in zip(frame.index, frame.to_numpy(), strict=True)]
                return (rows, cols) if with_column_types else rows
        raise AssertionError(f"未预期查询（符号/表未在注入清单内）: {sql[:90]}")


def _kline_index_tables() -> dict[str, pd.DataFrame]:
    dates = pd.bdate_range(start="2019-01-02", periods=10)
    proxy = pd.DataFrame({"close": np.linspace(3000.0, 3100.0, 10)}, index=dates)
    breadth = pd.DataFrame(
        {"advance_count": [100.0] * 8 + [0.0, 0.0], "decline_count": [50.0] * 8 + [0.0, 0.0]},
        index=dates,
    )
    # EQW_ALLA 覆盖 399106 的两个死日——镜像生产 _load_breadth 的补洞分支
    eqw = pd.DataFrame({"advance_count": [70.0, 80.0], "decline_count": [20.0, 10.0]}, index=dates[8:])
    return {"'000300'": proxy, "'399106'": breadth, "'EQW_ALLA'": eqw}


class _Reg:
    """TableRegistry 替身：记录被解析的逻辑表名（表名真源纪律的可查证面）。"""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def table(self, name: str) -> str:
        self.seen.append(name)
        return f"c1_market.tbl_{name}"


class TestLoaderDiscipline:
    def test_table_names_come_from_registry_not_literals(self, monkeypatch):
        reg = _Reg()
        monkeypatch.setattr("zephyr.data.table_registry.get_registry", lambda: reg)
        conn = _FakeCH(_kline_index_tables())
        out = wf.load_breadth(conn=conn)  # type: ignore[arg-type]

        assert reg.seen == ["market_index_kline", "market_kline_index_calc"], "表名解析键漂移 → 须同步 registry"
        assert all("c1_market.tbl_" in q for q in conn.queries), "SQL 出现硬编码表名"
        assert int(out["live"].sum()) == 10, "EQW_ALLA 补位未生效（死日仍冒充无数据）"

    def test_default_connection_is_reader_role(self, monkeypatch):
        """conn=None 时必须经 DatabaseService(role='reader')，禁 writer/禁裸客户端。"""
        calls: list[str] = []

        class _Svc:
            def get_clickhouse_conn(self, role: str | None = None):
                calls.append(str(role))
                return _FakeCH(_kline_index_tables())

        monkeypatch.setattr("zephyr.data.table_registry.get_registry", _Reg)
        monkeypatch.setattr("zephyr.infrastructure.database_service.DatabaseService", _Svc)
        out = wf.load_breadth()
        assert calls == ["reader"], f"校准管线用了非只读连接: {calls}"
        assert len(out) == 10

    def test_dead_days_flagged_not_silently_dropped(self, monkeypatch):
        """补位后仍死的日必须留 live=False 痕（母体剔除数可查证，不静默改日历）。"""
        monkeypatch.setattr("zephyr.data.table_registry.get_registry", _Reg)
        tables = _kline_index_tables()
        tables["'EQW_ALLA'"] = tables["'EQW_ALLA'"].iloc[:0]
        out = wf.load_breadth(conn=_FakeCH(tables))  # type: ignore[arg-type]
        assert int(out["live"].sum()) == 8
        assert list(out.index[8:]) == list(out[~out["live"]].index)
        assert bool((out.loc[out["live"], "adv"] > 0).all())

    def test_products_never_land_in_production_data_dir(self):
        """INVARIANTS：缓存/结果只落临时区（防校准跑批污染生产数据目录）。"""
        cache = str(wf._default_cache_path()).replace("\\", "/")
        assert cache.startswith(".runtime/tmp/"), f"默认缓存路径越界生产区: {cache}"
        text = _HARNESS_PATH.read_text(encoding="utf-8")
        for bad in ('"data/', "'data/", 'Path("data', "Path('data"):
            assert bad not in text, f"harness 出现生产数据目录写入嫌疑 {bad}"


# ---------------------------------------------------------------------------
# 3. 统计口径
# ---------------------------------------------------------------------------
class TestStatistics:
    def test_percentile_of_is_the_share_at_or_below(self):
        """分位口径=「≤level 的占比」（现行值是第几百分位），且是 0-100 量纲（台账按此回填）。"""
        s = pd.Series(np.arange(1.0, 101.0))
        assert wf.percentile_of(s, 50.0) == 50.0
        assert wf.percentile_of(s, 100.0) == 100.0
        assert wf.percentile_of(s, 0.5) == 0.0

    def test_percentile_of_ignores_nan_and_rejects_empty(self):
        s = pd.Series([1.0, 2.0, np.nan, 3.0])
        assert wf.percentile_of(s, 2.0) == pytest.approx(200.0 / 3.0)
        with pytest.raises(ValueError, match="空样本"):
            wf.percentile_of(pd.Series([np.nan, np.nan]), 0.5)

    def test_folds_are_expanding_and_test_segments_are_adjacent(self):
        idx = pd.bdate_range(start="2008-01-02", periods=252 * 14)
        folds = wf.make_folds(idx, first_test_start="2012-01-01", test_years=3, n_folds=4)
        assert [f.fold_id for f in folds] == ["F1", "F2", "F3", "F4"]
        for k, f in enumerate(folds):
            assert f.train_start == idx.min(), "训练段须锚定序列起点（expanding，非滑动窗）"
            assert f.train_end < f.test_start, "训练段越界进入评估段"
            assert f.test_start < f.test_end
            if k:
                assert f.train_end >= folds[k - 1].test_end, "训练段未吸收上一折的样本外"
                assert f.test_start > folds[k - 1].test_end, "评估段重叠 = 同一段被跑多次"

    def test_folds_stop_where_data_ends(self):
        idx = pd.bdate_range(start="2014-01-02", periods=252 * 4)
        folds = wf.make_folds(idx, first_test_start="2015-01-01", test_years=3, n_folds=9)
        assert [f.fold_id for f in folds] == ["F1"], "空 test 段不得进统计（次折起点已在数据末端之后）"
        assert folds[-1].test_end <= idx.max()

    def test_event_windows_are_clipped_to_the_population(self):
        """上穿事件的前向窗不得伸出母体尾（否则训练段吃到段外价格）。"""
        frame = _synthetic_frame()
        score = wf.score_for_config(frame["adv"], frame["dec"], wf.ThrustConfig())
        all_onsets = wf.onset_dates(score, 60.0)
        kept = wf._onsets_within(score, frame.index, 60.0, max_horizon=max(wf.HORIZONS))
        assert len(all_onsets) > len(kept), "合成序列本就该含尾部事件，否则本测试无判别力"
        assert kept.max() <= frame.index[-max(wf.HORIZONS) - 1]

    def test_onset_dates_use_onset_semantics_not_level_semantics(self):
        """持续在线只算一次事件（防"永远在线"被当成连续新信号虚增事件数）。"""
        score = pd.Series([0.0, 60.0, 80.0, 60.0, 0.0, 60.0], index=pd.bdate_range("2020-01-01", periods=6))
        assert list(wf.onset_dates(score, 60.0)) == [score.index[1], score.index[5]]

    def test_dead_days_are_excluded_and_counted(self):
        frame = _synthetic_frame()
        start = frame.index[50]  # 早于死日块（100:110）→ 二者都落在报告窗口内
        frame.iloc[100:110, frame.columns.get_loc("live")] = False
        m = wf.segment_metrics(frame, wf.ThrustConfig(), start)
        assert m["excluded_dead_days_in_window"] == 10
        in_window = int((frame.index >= start).sum())
        assert m["n_days"] == in_window - 10, "死日仍留在统计母体里"

    def test_warmup_days_are_excluded_at_the_series_head(self):
        """首段须砍掉 EMA/rolling 预热日（预热伪影会虚高分位）。"""
        frame = _synthetic_frame()
        m = wf.segment_metrics(frame, wf.ThrustConfig())
        assert m["start"] == str(frame.index[wf.WARMUP_TRADE_DAYS].date())
        assert m["n_days"] == int(len(frame)) - wf.WARMUP_TRADE_DAYS

    def test_segment_metrics_rejects_empty_population(self):
        frame = _synthetic_frame(200)
        frame["live"] = False
        with pytest.raises(ValueError, match="无有效样本"):
            wf.segment_metrics(frame, wf.ThrustConfig())

    def test_segment_metrics_rejects_a_window_beyond_the_data(self):
        with pytest.raises(ValueError, match="无有效样本"):
            wf.segment_metrics(_synthetic_frame(200), wf.ThrustConfig(), "2090-01-01")

    def test_metrics_report_every_quantity_the_ledger_now_claims(self):
        """台账证据段的量纲（EMA 分位 + 稀有度占比 + 事件超额）必须由本管线产出，缺一即无法回填。"""
        m = wf.segment_metrics(_synthetic_frame(), wf.ThrustConfig())
        for key in (
            "n_days",
            "percentile_of_thrust",
            "percentile_of_washout",
            "on_share",
            "washout_share",
            "full_thrust_days",
            "full_thrust_share",
            "onset_events",
            "event_excess_20d_bps",
            "acceptance_pass",
        ):
            assert key in m, f"裁定所需指标 {key} 已从 segment_metrics 消失 → 台账 claims 失去真源"
        assert 0.0 <= m["percentile_of_washout"] < m["percentile_of_thrust"] <= 100.0
        assert m["on_share"] > m["full_thrust_share"]
        assert m["score_ge60_days"] >= m["onset_events"]


# ---------------------------------------------------------------------------
# 4. 反未来函数
# ---------------------------------------------------------------------------
class TestNoFutureFunction:
    def test_segment_metrics_are_blind_to_data_after_end(self):
        """同一窗口：喂"截至该日的短帧"与"其后还有多年数据的长帧"须逐字段相等。"""
        cfg = wf.ThrustConfig()
        short = _synthetic_frame(45 * 14)
        long = _synthetic_frame(45 * 24)
        pd.testing.assert_frame_equal(short, long.loc[: short.index.max()])  # 生成器确定性前提
        cut = short.index.max()
        assert wf.segment_metrics(short, cfg, end=cut) == wf.segment_metrics(long, cfg, end=cut), (
            "段指标对窗口之外的数据可感知 → 样本外污染训练段"
        )

    def test_select_in_train_is_deterministic_on_the_same_segment(self):
        frame = _synthetic_frame(45 * 14)
        assert wf.select_in_train(frame) == wf.select_in_train(frame.copy())

    def test_select_in_train_refuses_when_no_grid_point_passes(self):
        """恒 0.5 的广度：任何 thrust 候选在线率=0 → 必须拒绝选值，禁"挑个最不离谱的"。"""
        out = wf.select_in_train(_flat_frame())
        assert out["picked"] is None
        assert out["reason"], "拒绝选值必须给出理由（报告读者须知道是没通过而不是漏跑）"

    def test_select_in_train_picks_the_passing_point_nearest_the_rarity_target(self, monkeypatch):
        """选值规则：先过验收带，再取 on_share 离 5% 带心最近者（目标=头部少数事件）。"""
        passing = {
            (0.58, 0.40): 0.12,  # 误爆（> 上界 0.10）→ 须被淘汰
            (0.60, 0.40): 0.011,
            (0.615, 0.40): 0.049,  # 离 0.05 最近 → 应选中
            (0.63, 0.40): 0.02,
        }

        def _fake(frame: pd.DataFrame, cfg: wf.ThrustConfig, *_a: Any, **_k: Any) -> dict[str, Any]:
            shared = {"washout_share": 0.10, "full_thrust_share": 0.01, "event_excess_20d_bps": 12.0}
            share = passing.get((cfg.thrust, cfg.washout))
            return wf_passing(share, **shared)

        monkeypatch.setattr(wf, "segment_metrics", _fake)
        out = wf.select_in_train(_synthetic_frame(100))
        assert out["picked"] == {"thrust": 0.615, "washout": 0.4}

    def test_run_walkforward_never_feeds_test_rows_into_selection(self, monkeypatch):
        """结构性保证：select_in_train 实际收到的帧末日必须早于该折 test_start。"""
        seen: list[pd.Timestamp] = []
        real = wf.select_in_train

        def spy(frame: pd.DataFrame) -> dict[str, Any]:
            seen.append(frame.index.max())
            return real(frame)

        monkeypatch.setattr(wf, "select_in_train", spy)
        frame = _wf_frame()
        folds = wf.make_folds(frame.index, first_test_start="2014-01-01", test_years=3, n_folds=3)
        wf.run_walkforward(frame, folds)
        assert len(seen) == len(folds) == 3
        for hi, fold in zip(seen, folds, strict=True):
            assert hi < fold.test_start, f"{fold.fold_id} 训练段含样本外日期 {hi} ≥ {fold.test_start}"


def wf_passing(share: float | None, **extra: Any) -> dict[str, Any]:
    """构造一份"除 on_share 外全部落在验收带内"的段指标（只喂选值规则，不重复实现判据）。"""
    out: dict[str, Any] = {"on_share": share, "acceptance_pass": False}
    out.update(extra)
    out["acceptance_pass"] = wf.passes_acceptance(out)
    return out


# ---------------------------------------------------------------------------
# 5. 预注册机械判据
# ---------------------------------------------------------------------------
def _metrics(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "on_share": 0.05,
        "washout_share": 0.10,
        "full_thrust_share": 0.01,
        "event_excess_20d_bps": 10.0,
    }
    base.update(overrides)
    return base


class TestAcceptanceAndPrereg:
    @pytest.mark.parametrize(
        ("key", "value", "should_pass"),
        [
            ("on_share", 0.05, True),
            ("on_share", 0.30, False),  # 天天在线 = 噪声污染 S2 confirm 析取腿
            ("on_share", 0.001, False),  # 稀有到不出现 = 维度不存在
            ("on_share", None, False),  # 缺值不得当成通过
            ("washout_share", 0.90, False),
            ("full_thrust_share", 0.50, False),
            ("event_excess_20d_bps", -999.0, False),  # 稀有但反向 = 噪声
            ("event_excess_20d_bps", None, False),
        ],
    )
    def test_acceptance_band_edges(self, key: str, value: Any, should_pass: bool):
        assert wf.passes_acceptance(_metrics(**{key: value})) is should_pass

    def test_acceptance_boundaries_are_the_pre_registered_ones(self):
        acc = wf.PREREG_ACCEPTANCE
        assert acc["on_share"] == [0.01, 0.10]
        assert acc["full_thrust_share"] == [0.002, 0.05]
        assert wf.passes_acceptance(_metrics(on_share=0.10)) is True
        assert wf.passes_acceptance(_metrics(on_share=0.1001)) is False

    def test_grid_and_windows_are_pre_registered_before_data(self):
        """网格须包住台账现值（事后扩网格=事后聪明，故端点写死后禁动）。"""
        assert wf.CURRENT_THRUST in wf.PREREG_GRID["thrust"]
        assert wf.CURRENT_WASHOUT in wf.PREREG_GRID["washout"]
        assert min(wf.PREREG_GRID["thrust"]) < wf.CURRENT_THRUST < max(wf.PREREG_GRID["thrust"])
        assert set(wf.PREREG_REPORT_WINDOWS) == {"full", "post_2014", "post_2019"}
        assert wf.PREREG_SERIES_START in set(wf.PREREG_REPORT_WINDOWS.values())
        assert len(wf.grid_points()) == len(wf.PREREG_GRID["thrust"]) * len(wf.PREREG_GRID["washout"])

    def test_prereg_registry_hash_locks_the_payload(self, tmp_path):
        path = tmp_path / "prereg.json"
        payload = {"grid": wf.PREREG_GRID, "acceptance": wf.PREREG_ACCEPTANCE}
        reg = PreRegistrationRegistry(path)
        reg.register("x", payload, note="t")
        assert reg.verify("x", payload) is True
        tampered = dict(payload, grid={"thrust": [0.615], "washout": [0.40]})
        assert reg.verify("x", tampered) is False, "改网格未换预注册名却仍能过 → hash 锁失效"
        with pytest.raises(RuntimeError):
            PreRegistrationRegistry(path).register("x", payload)
        assert json.loads(path.read_text(encoding="utf-8")), "预注册文件必须落盘可审计"

    def test_run_walkforward_is_idempotent_against_the_registry(self, tmp_path):
        """同名重跑只在 payload 未变时放行；产物结构齐备（报告真源）。"""
        frame = _wf_frame()
        folds = wf.make_folds(frame.index, first_test_start="2014-01-01", test_years=3, n_folds=3)
        reg = PreRegistrationRegistry(tmp_path / "p.json")
        first = wf.run_walkforward(frame, folds, prereg=reg)
        second = wf.run_walkforward(frame, folds, prereg=reg)
        assert json.dumps(first, sort_keys=True, default=str) == json.dumps(second, sort_keys=True, default=str)
        assert set(first) >= {
            "folds",
            "current_in_full_windows",
            "cross_fold_on_share",
            "cross_fold_stability_ratio",
            "stability_limit",
        }
        assert len(first["folds"]) == len(folds)
        assert set(first["current_in_full_windows"]) == set(wf.PREREG_REPORT_WINDOWS)
        for rec in first["folds"]:
            assert set(rec) >= {"fold", "train_days", "test_days", "current_in_train", "current_in_test", "train_pick"}
            assert rec["current_in_test"]["start"] > rec["current_in_train"]["end"], "train/test 段重叠"
            if rec["train_pick"]["picked"] is None:
                assert "picked_in_test" not in rec, "未选值却给出样本外结果 = 凭空造数"

    def test_summary_projection_keeps_only_decision_keys(self):
        frame = _wf_frame()
        folds = wf.make_folds(frame.index, first_test_start="2014-01-01", test_years=3, n_folds=1)
        summary = wf._summary_for_print(wf.run_walkforward(frame, folds))
        assert set(summary["windows"]) == set(wf.PREREG_REPORT_WINDOWS)
        assert set(summary["windows"]["full"]) <= set(wf._SUMMARY_KEYS)
        assert {"cross_fold_stability_ratio", "stability_limit", "per_fold_current_on_share"} <= set(summary)


# ---------------------------------------------------------------------------
# 6. 与台账的闭环
# ---------------------------------------------------------------------------
class TestHarnessStaysHonest:
    def test_harness_is_in_place_and_declares_this_test_file(self):
        assert _HARNESS_PATH.exists(), "台账清偿证据点名的 harness 已消失"
        assert "tests/regime/test_breadth_thrust_walkforward.py" in _HARNESS_PATH.read_text(encoding="utf-8")

    def test_harness_does_not_import_a_raw_client(self):
        text = _HARNESS_PATH.read_text(encoding="utf-8")
        for raw in ("clickhouse_driver", "clickhouse_connect", "get_clickhouse_client", "from clickhouse"):
            assert raw not in text, f"harness 直连原始客户端 {raw} → 违反只读服务层口径"
        assert 'get_clickhouse_conn(role="reader")' in text

    def test_ledger_alert_projection_count_does_not_backslide(self):
        """闭环哨兵：复推跑完后 ALERT 集合钉死，且本项**必须仍是 ALERT**。

        原期望「本项已 RESOLVED」是跑数前的设想，实测把它否掉了：现值在预注册验收带
        全样本不过（on_share 超上界）、跨折稳定性不过，训练段选值样本外只过 2/4 折
        ⇒ 按「不炸才用」闸门不采纳新值，欠账因此从「从未复推」改判为「复推过、缺陷
        定位为跨时代稳定性」——状态词不变，告警不能撤（撤了=把已知偏松的尺子静默转正）。
        台账里记的是实测数字与处置，不是设想；改这条期望必须连同台账与报告一起改。
        """
        from zephyr.regime.features.overlay_features import (
            ALERT_UNCALIBRATED_THRESHOLDS,
            THRESHOLD_CALIBRATION_LEDGER,
        )

        assert sorted(ALERT_UNCALIBRATED_THRESHOLDS) == [
            "s2_breadth_thrust",
            "t3_mainline",
            "t3_money_effect",
        ]
        entry = THRESHOLD_CALIBRATION_LEDGER["s2_breadth_thrust"]
        # 台账须指向本次闭环的真源（预注册名 + harness），否则"已复推"无从核验
        assert "s2_breadth_thrust_walkforward_v1" in entry, "台账丢了预注册名 → 复推证据链断裂"
        assert "regime_breadth_thrust_walkforward" in entry, "台账丢了 harness 指针"
        assert "不采纳" in entry, "台账未记录样本外不采纳结论 → ALERT 语义会退回「从未复推」"

