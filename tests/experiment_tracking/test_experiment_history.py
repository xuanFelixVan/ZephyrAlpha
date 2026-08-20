# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] tests.experiment_tracking.test_experiment_history
# [DOMAIN] D_FRONTEND
# [A_module] module_id=MOD-TEST-L08-EXPHIST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
"""「实验历史」Tab 单元测试（51 号工作流 B4）。

覆盖:
  - P0-1 NAV 归一化（不变/缩放/空）
  - P0-2 时间轴对齐（一致/差 1 交集+warning/完全错位降级）
  - P1-6 verdict 后缀剥离（max_dd 不切错）
  - P1-7 分级降级（NAV CSV 损坏）
  - fetch_experiment_history 列表（2 run / 51 run 截断 50）
  - fetch_c1_comparison 双曲线 + 4 verdict + summary
  - render_experiment_history pn=None 纯 dict
  - _render_c1_comparison plotly figure 2 trace
"""

from __future__ import annotations

import pytest

import zephyr.experiment_tracking.query as query
from zephyr.experiment_tracking.config import ExperimentTrackingConfig
from zephyr.experiment_tracking.fallback_tracker import FallbackBackend
from zephyr.frontend.dashboard.components import experiment_history as eh

_COMPONENT = "c1-validation"

_METRICS = {
    "passed": 1.0,
    "baseline_sharpe": 1.5,
    "experiment_sharpe": 1.8,
    "baseline_maxdd": -0.10,
    "experiment_maxdd": -0.08,
    "baseline_calmar": 2.0,
    "experiment_calmar": 2.4,
    "baseline_turnover": 1.1,
    "experiment_turnover": 1.0,
    "sharpe_baseline": 1.5,
    "sharpe_experiment": 1.8,
    "sharpe_passed": 1.0,
    "max_dd_baseline": -0.10,
    "max_dd_experiment": -0.08,
    "max_dd_passed": 1.0,
    "calmar_baseline": 2.0,
    "calmar_experiment": 2.4,
    "calmar_passed": 1.0,
    "turnover_baseline": 1.1,
    "turnover_experiment": 1.0,
    "turnover_passed": 0.0,
}
_CSV_B = b"date,nav\n2026-01-01,1.0\n2026-01-02,1.1\n2026-01-03,1.21\n"
_CSV_E = b"date,nav\n2026-01-01,100\n2026-01-02,112\n2026-01-03,125\n"


def _write_run(fb_dir, run_name="run_x", metrics=None, with_artifacts=True):
    """用 FallbackBackend 写一个 mock C1 run，返回 run_id。"""
    backend = FallbackBackend(fb_dir)
    run_id = backend.start_run(_COMPONENT, run_name, {"mode": "mock", "passed": "True"})
    backend.log_metrics(metrics or dict(_METRICS), step=None)
    if with_artifacts:
        backend.log_artifact_bytes(_CSV_B, "nav_curve_baseline.csv", artifact_path="nav")
        backend.log_artifact_bytes(_CSV_E, "nav_curve_experiment.csv", artifact_path="nav")
        backend.log_artifact_bytes(b"# C1 Report\nok", "c1_summary.md", artifact_path="report")
    backend.end_run("FINISHED")
    return run_id


@pytest.fixture()
def fb_env(monkeypatch, tmp_path):
    """patch query.load_config 指向 tmp_path fallback_dir + 清缓存。"""
    cfg = ExperimentTrackingConfig(enable_tracking=True, fallback_dir=tmp_path / "fb")
    monkeypatch.setattr(query, "load_config", lambda: cfg)
    eh.reset_experiment_history_cache()
    yield cfg
    eh.reset_experiment_history_cache()


# ── P0-1 归一化 ─────────────────────────────────────────────────


class TestNormalizeNav:
    def test_already_normalized(self):
        assert eh._normalize_nav([1.0, 1.1, 1.21]) == [1.0, 1.1, 1.21]

    def test_rescaled(self):
        assert eh._normalize_nav([100, 110, 121]) == [1.0, 1.1, 1.21]

    def test_empty_and_zero_head(self):
        assert eh._normalize_nav([]) == []
        assert eh._normalize_nav([0, 1, 2]) == [0, 1, 2]


# ── P0-2 时间轴对齐 ─────────────────────────────────────────────


class TestAlignment:
    def test_aligned_no_warning(self, fb_env):
        run_id = _write_run(fb_env.fallback_dir)
        view = eh.fetch_c1_comparison(run_id)
        assert view is not None
        assert view.alignment_warning is None
        assert view.nav_baseline == [1.0, 1.1, 1.21]
        assert view.nav_experiment == [1.0, 1.12, 1.25]  # 100 起点归一化

    def test_misaligned_intersection(self, fb_env):
        run_id = _write_run(fb_env.fallback_dir, with_artifacts=False)
        backend = FallbackBackend(fb_env.fallback_dir)
        rid = backend.start_run(_COMPONENT, "x2", None)
        backend.log_metrics(dict(_METRICS), step=None)
        backend.log_artifact_bytes(_CSV_B, "nav_curve_baseline.csv", artifact_path="nav")
        # experiment 少一个点且日期错位一天
        backend.log_artifact_bytes(
            b"date,nav\n2026-01-02,100\n2026-01-04,110\n",
            "nav_curve_experiment.csv",
            artifact_path="nav",
        )
        backend.end_run("FINISHED")
        view = eh.fetch_c1_comparison(rid)
        assert view is not None
        assert view.alignment_warning is not None
        assert view.timestamps_baseline == ["2026-01-02"]  # 交集

    def test_totally_misaligned_degraded(self, fb_env):
        backend = FallbackBackend(fb_env.fallback_dir)
        rid = backend.start_run(_COMPONENT, "x3", None)
        backend.log_metrics(dict(_METRICS), step=None)
        backend.log_artifact_bytes(_CSV_B, "nav_curve_baseline.csv", artifact_path="nav")
        backend.log_artifact_bytes(
            b"date,nav\n2027-01-01,100\n",
            "nav_curve_experiment.csv",
            artifact_path="nav",
        )
        backend.end_run("FINISHED")
        view = eh.fetch_c1_comparison(rid)
        assert view is not None
        assert view.degraded_reason == "NAV 时间轴完全错位"
        assert view.nav_baseline == [] and view.nav_experiment == []


# ── P1-6 verdict 解析 ───────────────────────────────────────────


class TestParseVerdicts:
    def test_suffix_strip_not_split(self):
        verdicts = eh._parse_verdicts(
            {
                "max_dd_baseline": -0.1,
                "max_dd_experiment": -0.08,
                "max_dd_passed": 1.0,
                "sharpe_baseline": 1.5,
                "sharpe_experiment": 1.8,
                "sharpe_passed": 1.0,
                "orphan_passed": 1.0,  # 缺 baseline/experiment → 跳过
            }
        )
        names = sorted(v.name for v in verdicts)
        assert names == ["max_dd", "sharpe"]  # max_dd 不切错为 max


# ── P1-7 分级降级 ───────────────────────────────────────────────


class TestDegraded:
    def test_broken_csv(self, fb_env):
        backend = FallbackBackend(fb_env.fallback_dir)
        rid = backend.start_run(_COMPONENT, "broken", None)
        backend.log_metrics(dict(_METRICS), step=None)
        backend.log_artifact_bytes(b"not,a,csv\n1,2", "nav_curve_baseline.csv", artifact_path="nav")
        backend.log_artifact_bytes(_CSV_E, "nav_curve_experiment.csv", artifact_path="nav")
        backend.end_run("FINISHED")
        view = eh.fetch_c1_comparison(rid)
        assert view is not None
        assert view.degraded_reason == "baseline NAV 缺失"
        assert view.nav_experiment  # experiment 仍可用

    def test_both_missing(self, fb_env):
        rid = _write_run(fb_env.fallback_dir, with_artifacts=False)
        view = eh.fetch_c1_comparison(rid)
        assert view is not None
        assert view.degraded_reason == "NAV 数据缺失"

    def test_run_not_exist(self, fb_env):
        assert eh.fetch_c1_comparison("no-such-run") is None


# ── fetch 列表 ──────────────────────────────────────────────────


class TestFetchHistory:
    def test_two_runs_listed(self, fb_env):
        _write_run(fb_env.fallback_dir, "r1")
        _write_run(fb_env.fallback_dir, "r2")
        data = eh.fetch_experiment_history()
        assert len(data.runs) == 2
        assert data.truncated is False
        assert all(r.passed is True for r in data.runs)  # passed 解析（TypeError 修复回归）

    def test_51_runs_truncated_to_50(self, fb_env):
        for i in range(51):
            _write_run(fb_env.fallback_dir, f"r{i:02d}")
        data = eh.fetch_experiment_history()
        assert len(data.runs) == 50
        assert data.truncated is True


# ── fetch 单 run 对比视图 ───────────────────────────────────────


class TestFetchComparison:
    def test_full_view(self, fb_env):
        run_id = _write_run(fb_env.fallback_dir)
        view = eh.fetch_c1_comparison(run_id)
        assert view is not None
        assert len(view.verdicts) == 4
        assert view.nav_baseline == [1.0, 1.1, 1.21]
        assert view.nav_experiment == [1.0, 1.12, 1.25]
        assert view.summary_md.startswith("# C1 Report")
        # P1-5 diff 方向：sharpe Δ=+0.3 好；turnover Δ=-0.1 好（负向指标）
        assert view.metrics_diff["sharpe"]["good"] is True
        assert view.metrics_diff["turnover"]["good"] is True


# ── render 层 ───────────────────────────────────────────────────


class TestRender:
    def test_render_dict_payload(self, fb_env):
        _write_run(fb_env.fallback_dir)
        data = eh.fetch_experiment_history()
        payload = eh.render_experiment_history(data)
        assert isinstance(payload, dict)
        assert payload["empty"] is False
        assert len(payload["runs"]) == 1

    def test_render_empty_state(self, fb_env):
        payload = eh.render_experiment_history(eh.ExperimentHistoryData(runs=[], component=_COMPONENT))
        assert payload["empty"] is True

    def test_nav_figure_two_traces(self):
        view = eh.C1ComparisonView(
            run_id="x",
            run_name="x",
            start_time="",
            passed=True,
            nav_baseline=[1.0, 1.1],
            nav_experiment=[1.0, 1.2],
            timestamps_baseline=["2026-01-01", "2026-01-02"],
            timestamps_experiment=["2026-01-01", "2026-01-02"],
        )
        fig = eh._nav_figure(view)
        assert len(fig.data) == 2  # baseline + experiment

    def test_widget_selection_flow(self, fb_env):
        """回归（2026-08-16 浏览器实测 bug）：MultiSelect.options 的 value 必须是 run_id
        （str 可哈希）——param.value 返回 value 列表，若放 RunSummary 对象，回调再索引
        options 会 TypeError unhashable。锚定契约防回退。"""
        if eh.pn is None:
            pytest.skip("panel 未装")
        rid = _write_run(fb_env.fallback_dir)
        data = eh.fetch_experiment_history()
        payload = eh.render_experiment_history(data)
        layout = payload["_layout"]
        selector = layout[0][0]
        # 契约 1：options 的 value 全为 run_id（str）
        assert set(selector.options.values()) == {r.run_id for r in data.runs}
        assert all(isinstance(v, str) for v in selector.options.values())
        # 契约 2：param.value 接受 run_id 选择（浏览器端回传同形）
        selector.value = [rid]
        assert selector.value == [rid]
        # 契约 3：by_id 解析路径不炸（回调核心逻辑）
        by_id = {r.run_id: r for r in data.runs}
        picked = [by_id[x] for x in selector.value]
        view = eh.fetch_c1_comparison(picked[0].run_id)
        assert view is not None and len(view.verdicts) == 4
