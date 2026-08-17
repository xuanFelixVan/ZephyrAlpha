# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.experiment_history
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] panel ; plotly ; pandas ; zephyr.experiment_tracking.query ; zephyr.frontend.dashboard.components.backtest_performance(调色板常量)
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pn=None 时返回纯 dict（可测）；query 调用失败→空状态不抛；nav 归一化后对比（P0-1）；时间轴交集对齐（P0-2）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch/render 失败→空状态 payload（alert 文案），不抛
# [TESTS] tests/frontend/dashboard/components/test_experiment_history.py
# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
"""D_FRONTEND — Panel「实验历史」Tab（C1 回测历史列表 + 多选横向对比 + 双净值对比视图）。

数据流: FallbackBackend JSON（logs/experiment_tracking_fallback/{component}/{run_id}/）
  → query.list_runs/get_run/download_artifact → fetch_* dataclass → render_* payload（含 _layout）。

G0.5 过渡层定位（51 号 §四.9）：开发工具/回测眼睛，非 G1 正式前端；
fetch_* dataclass 为数据契约（G1 升级时复用），render 层将来重写。

依据: 51_panel_experiment_history_mlflow_retirement.md 工作流 B + §七 P0×3/P1×4/P2×3
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 实验历史数据请求
#   fields: component 名 / run_id / 多选 run_id 列表
#   code: fetch_experiment_history / fetch_c1_comparison / render_experiment_history
# 层: 算法
# - id: A1
#   name_zh: 后端查询 + fallback
#   name_en: backend_query_fallback
#   intro: query.list_runs/get_run 拉取；失败→空状态 payload 不抛（ERROR_CONTRACT）
#   code: fetch_* 系列
# - id: A2
#   name_zh: 双净值归一化对比
#   name_en: nav_normalized_compare
#   intro: baseline/experiment nav 归一化 + 时间轴交集对齐（P0-1/P0-2）
#   code: _nav_figure
# - id: A3
#   name_zh: 视图渲染
#   name_en: view_render
#   intro: pn 可用→Panel 布局；pn=None→纯 dict（可测）
#   code: _render_c1_comparison / _render_multi_run_comparison / _detail
# 层: 输出
# - id: O1
#   name_zh: Tab payload
#   name_en: tab_payload
#   intro: 含 _layout 的 dict 供 app_panel 挂载
#   downstream: zephyr.frontend.dashboard.app_panel
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> A3 ; A3 --> O1
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Final, Optional

import pandas as pd
import plotly.graph_objects as go

from zephyr.experiment_tracking.config import ExperimentTrackingConfig
from zephyr.experiment_tracking.models import RunSummary
from zephyr.experiment_tracking.query import (
    download_artifact,
    download_artifact_text,
    get_run,
    list_runs,
)
from zephyr.frontend.dashboard.components.backtest_performance import (
    _BG,
    _BLUE,
    _GREEN,
    _ORANGE,
    _RED,
    _TEXT,
)

try:  # pragma: no cover - 环境依赖
    import panel as pn
except ImportError:  # pragma: no cover
    pn = None  # type: ignore[assignment]

_logger = logging.getLogger(__name__)

__all__: Final = [
    "C1ComparisonView",
    "C1VerdictRow",
    "ExperimentHistoryData",
    "fetch_c1_comparison",
    "fetch_experiment_history",
    "render_experiment_history",
    "reset_experiment_history_cache",
]

_COMPONENT_DEFAULT = "c1-validation"
_MAX_RUNS = 50  # P2-8：首页前 50 条兜底

# P1-5：指标正负向（higher better=True → Δ>0 绿）
_METRIC_POLARITY: Final = {
    "sharpe": True,
    "maxdd": False,
    "calmar": True,
    "turnover": False,
}


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ExperimentHistoryData:
    """实验历史列表数据。"""

    runs: list[RunSummary]
    component: str
    truncated: bool = False  # P2-8：超过前 50 条截断标记


@dataclass
class C1VerdictRow:
    """单条 verdict 对比行（从 metrics 三元组解析，P1-6 后缀剥离）。"""

    name: str
    baseline: float
    experiment: float
    passed: bool
    detail: str = ""


@dataclass
class C1ComparisonView:
    """C1 开/关对比视图数据（nav 已归一化 P0-1，时间轴已对齐 P0-2）。"""

    run_id: str
    run_name: str
    start_time: str
    passed: bool | None
    verdicts: list[C1VerdictRow] = field(default_factory=list)
    nav_baseline: list[float] = field(default_factory=list)
    nav_experiment: list[float] = field(default_factory=list)
    timestamps_baseline: list[str] = field(default_factory=list)
    timestamps_experiment: list[str] = field(default_factory=list)
    alignment_warning: str | None = None
    degraded_reason: str | None = None  # P1-7 分级降级
    metrics_diff: dict[str, dict[str, float]] = field(default_factory=dict)
    summary_md: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# 内部算法（P0-1/P0-2/P1-5/P1-6）
# ──────────────────────────────────────────────────────────────────────────────


def _normalize_nav(nav: list[float]) -> list[float]:
    """P0-1：归一到起点 1.0，消除初始净值差异（空/首点 0 原样返回）。"""
    if not nav or nav[0] == 0:
        return nav
    base = nav[0]
    return [v / base for v in nav]


def _parse_nav_csv(data: bytes | None) -> tuple[list[str], list[float]] | None:
    """解析 nav CSV（index 列 + nav 列）。损坏/缺 nav 列返回 None（P1-7 触发源）。"""
    if not data:
        return None
    try:
        df = pd.read_csv(io.BytesIO(data), index_col=0)
        if "nav" not in df.columns:
            return None
        s = df["nav"]
        return [str(i) for i in s.index], [float(v) for v in s.values]
    except Exception:  # noqa: BLE001
        return None


def _parse_verdicts(metrics: dict[str, float]) -> list[C1VerdictRow]:
    """P1-6：verdict 三元组解析（后缀剥离，不用 split——max_dd 含下划线不切错）。"""
    verdicts: list[C1VerdictRow] = []
    for key in metrics:
        if not key.endswith("_passed"):
            continue
        name = key[: -len("_passed")]
        b = metrics.get(f"{name}_baseline")
        e = metrics.get(f"{name}_experiment")
        if b is None or e is None:
            continue  # 不完整三元组跳过
        verdicts.append(
            C1VerdictRow(
                name=name,
                baseline=b,
                experiment=e,
                passed=bool(metrics[key]),
            )
        )
    return verdicts


def _metric_diffs(metrics: dict[str, float]) -> dict[str, dict[str, float]]:
    """P1-5：四项顶层指标 diff（Δ=experiment-baseline + polarity 好坏判定）。"""
    diffs: dict[str, dict[str, float]] = {}
    for name, higher_better in _METRIC_POLARITY.items():
        b = metrics.get(f"baseline_{name}")
        e = metrics.get(f"experiment_{name}")
        if b is None or e is None:
            continue
        delta = e - b
        good = (delta > 0) if higher_better else (delta < 0)
        diffs[name] = {"baseline": b, "experiment": e, "delta": delta, "good": good}
    return diffs


# ──────────────────────────────────────────────────────────────────────────────
# fetch 层
# ──────────────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def _list_runs_cached(component: str) -> tuple[RunSummary, ...]:
    """P2-8：按 component 缓存（新 run 后调 reset_experiment_history_cache 失效）。"""
    return tuple(list_runs(component))


def reset_experiment_history_cache() -> None:
    """实验历史缓存失效（C1 新 run 后调用）。"""
    _list_runs_cached.cache_clear()


def fetch_experiment_history(
    component: str = _COMPONENT_DEFAULT,
    config: ExperimentTrackingConfig | None = None,
) -> ExperimentHistoryData:
    """拉取实验历史列表（start_time 倒序，前 50 条兜底）。

    query 失败/无 run → 空 runs（不抛，Tab 显示空状态）。
    """
    try:
        runs = list(_list_runs_cached(component))
    except Exception as exc:  # noqa: BLE001
        _logger.warning("fetch_experiment_history 失败(返回空): %s", exc)
        return ExperimentHistoryData(runs=[], component=component)

    # 排序 key 统一为 timestamp 数值——防御 naive（旧版 fallback 本地时区）vs aware（UTC）混比 TypeError
    def _sort_key(r: RunSummary) -> tuple[int, float]:
        if r.start_time is None:
            return (0, 0.0)
        try:
            return (1, r.start_time.timestamp())
        except Exception:  # noqa: BLE001
            return (0, 0.0)

    runs.sort(key=_sort_key, reverse=True)
    truncated = len(runs) > _MAX_RUNS
    return ExperimentHistoryData(runs=runs[:_MAX_RUNS], component=component, truncated=truncated)


def fetch_c1_comparison(
    run_id: str,
    config: ExperimentTrackingConfig | None = None,
) -> C1ComparisonView | None:
    """拉取单 run 的 C1 对比视图（run 不存在→None；artifact 缺失→分级降级 P1-7）。

    施工顺序（51 号 §三.B2）：读 CSV → P0-1 归一化 → P0-2 对齐校验 → P1-6 解析 verdict → P1-7 降级。
    """
    try:
        detail = get_run(run_id, component=_COMPONENT_DEFAULT, config=config)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("fetch_c1_comparison get_run 失败(返回 None): %s", exc)
        return None
    if detail is None:
        return None

    view = C1ComparisonView(
        run_id=detail.run_id,
        run_name=detail.run_name,
        start_time=detail.start_time.isoformat() if detail.start_time else "",
        passed=detail.passed,
        verdicts=_parse_verdicts(detail.metrics),
        metrics_diff=_metric_diffs(detail.metrics),
    )

    # nav CSV 双读 + P1-7 分级降级
    nav_b = _parse_nav_csv(download_artifact(run_id, _COMPONENT_DEFAULT, "nav", "nav_curve_baseline.csv", config))
    nav_e = _parse_nav_csv(download_artifact(run_id, _COMPONENT_DEFAULT, "nav", "nav_curve_experiment.csv", config))
    if nav_b is None and nav_e is None:
        view.degraded_reason = "NAV 数据缺失"
    elif nav_b is None:
        view.degraded_reason = "baseline NAV 缺失"
    elif nav_e is None:
        view.degraded_reason = "experiment NAV 缺失"

    if nav_b is not None:
        view.timestamps_baseline, raw_b = nav_b
        view.nav_baseline = _normalize_nav(raw_b)  # P0-1
    if nav_e is not None:
        view.timestamps_experiment, raw_e = nav_e
        view.nav_experiment = _normalize_nav(raw_e)  # P0-1

    # P0-2：时间轴对齐校验
    if nav_b is not None and nav_e is not None:
        if view.timestamps_baseline == view.timestamps_experiment:
            pass  # 正常路径，无 warning
        else:
            common = sorted(set(view.timestamps_baseline) & set(view.timestamps_experiment))
            if not common:
                view.degraded_reason = "NAV 时间轴完全错位"
                view.nav_baseline, view.nav_experiment = [], []
            else:
                bidx = {t: i for i, t in enumerate(view.timestamps_baseline)}
                eidx = {t: i for i, t in enumerate(view.timestamps_experiment)}
                view.nav_baseline = [view.nav_baseline[bidx[t]] for t in common]
                view.nav_experiment = [view.nav_experiment[eidx[t]] for t in common]
                view.timestamps_baseline = common
                view.timestamps_experiment = common
                view.alignment_warning = "baseline/experiment 时间轴不一致，已取交集对齐"

    summary = download_artifact_text(run_id, _COMPONENT_DEFAULT, "report", "c1_summary.md", config)
    view.summary_md = summary or ""
    return view


# ──────────────────────────────────────────────────────────────────────────────
# render 层
# ──────────────────────────────────────────────────────────────────────────────


def _dark_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    """复用掘金 5-Tab 暗色调色板（import 常量，不重定义）。"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font={"color": _TEXT},
        height=height,
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
    )
    return fig


def _nav_figure(view: C1ComparisonView) -> go.Figure:
    """双净值曲线叠加图（baseline 蓝 / experiment 橙；长跨度 >3 年对数 y 轴）。"""
    fig = go.Figure()
    if view.nav_baseline:
        fig.add_trace(
            go.Scatter(
                x=view.timestamps_baseline,
                y=view.nav_baseline,
                mode="lines",
                name="baseline",
                line={"color": _BLUE, "width": 1.5},
            )
        )
    if view.nav_experiment:
        fig.add_trace(
            go.Scatter(
                x=view.timestamps_experiment,
                y=view.nav_experiment,
                mode="lines",
                name="experiment",
                line={"color": _ORANGE, "width": 1.5},
            )
        )
    span_years = len(view.timestamps_baseline) / 252 if view.timestamps_baseline else 0
    if span_years > 3:
        fig.update_yaxes(type="log")  # 长跨度：equal vertical = equal percentage
    fig.update_yaxes(title_text="净值（归一化）")
    _dark_layout(fig)
    return fig


def _diff_cards_md(view: C1ComparisonView) -> str:
    """指标 diff 卡片（Markdown 渲染，红绿色编码语义见 _METRIC_POLARITY）。"""
    if not view.metrics_diff:
        return ""
    parts = []
    for name, d in view.metrics_diff.items():
        mark = "🟢" if d["good"] else ("🔴" if d["delta"] != 0 else "⚪")
        parts.append(f"**{name}** {d['baseline']:.3f} → {d['experiment']:.3f}（Δ {d['delta']:+.3f} {mark}）")
    return "　|　".join(parts)


def _verdicts_md(view: C1ComparisonView) -> str:
    """verdict 对比表（Markdown 表格）。"""
    if not view.verdicts:
        return ""
    lines = ["| 指标 | baseline | experiment | 判定 |", "|---|---|---|---|"]
    for v in view.verdicts:
        lines.append(f"| {v.name} | {v.baseline:.4f} | {v.experiment:.4f} | {'✅' if v.passed else '❌'} |")
    return "\n".join(lines)


def _render_c1_comparison(view: C1ComparisonView) -> pn.Column | dict[str, Any]:
    """C1 对比视图布局（Alert → 双曲线 → verdict 表 → diff 卡片 → summary 折叠）。

    P0-3「看详情」按钮已砍（51 号允许：5-Tab 强依赖持仓/交易数据，nav CSV 无法重建）。
    """
    if pn is None:  # 测试路径：返回纯 dict
        return {
            "run_id": view.run_id,
            "degraded_reason": view.degraded_reason,
            "alignment_warning": view.alignment_warning,
            "nav_figure": _nav_figure(view),
            "verdicts_md": _verdicts_md(view),
            "diff_md": _diff_cards_md(view),
            "summary_md": view.summary_md,
        }
    children: list[Any] = []
    if view.degraded_reason:
        children.append(pn.pane.Alert(f"⚠️ {view.degraded_reason}", alert_type="warning"))
    if view.alignment_warning:
        children.append(pn.pane.Alert(view.alignment_warning, alert_type="info"))
    head = f"**{view.run_name}**（{view.start_time[:19]}）"
    if view.passed is not None:
        head += f"　verdict: {'✅ 通过' if view.passed else '❌ 未通过'}"
    children.append(pn.pane.Markdown(head))
    if view.nav_baseline or view.nav_experiment:
        children.append(pn.pane.Plotly(_nav_figure(view)))
    diff_md = _diff_cards_md(view)
    if diff_md:
        children.append(pn.pane.Markdown(diff_md))
    verdicts_md = _verdicts_md(view)
    if verdicts_md:
        children.append(pn.pane.Markdown(verdicts_md))
    if view.summary_md:
        children.append(pn.pane.Markdown(view.summary_md, name="C1 报告"))
    return pn.Column(*children, sizing_mode="stretch_width")


def _render_multi_run_comparison(runs: list[RunSummary]) -> pn.pane.Plotly | dict[str, Any]:
    """P1-4：多 run 横向对比（行=run，列=sharpe/maxdd/calmar/turnover/passed/时间）。

    用 plotly Table 而非 pn.widgets.Tabulator——Tabulator 前端库走 CDN，单机离线
    渲染失败（2026-08-16 浏览器实测 ReferenceError: Tabulator is not defined）；
    plotly 已是项目核心依赖，离线零新增（51 号 B2 文档备选方案）。
    """
    cols = ["run_name", "start_time", "passed", "sharpe", "maxdd", "calmar", "turnover"]
    rows: list[dict[str, Any]] = []
    for r in runs:
        rows.append(
            {
                "run_name": r.run_name,
                "start_time": r.start_time.isoformat()[:19] if r.start_time else "",
                "passed": ("✅" if r.passed else "❌") if r.passed is not None else "-",
                "sharpe": r.metrics.get("experiment_sharpe", r.metrics.get("baseline_sharpe")),
                "maxdd": r.metrics.get("experiment_maxdd", r.metrics.get("baseline_maxdd")),
                "calmar": r.metrics.get("experiment_calmar", r.metrics.get("baseline_calmar")),
                "turnover": r.metrics.get("experiment_turnover", r.metrics.get("baseline_turnover")),
            }
        )
    if pn is None:
        return {"columns": cols, "rows": rows}
    fig = go.Figure(
        data=[
            go.Table(
                header={
                    "values": [f"<b>{c}</b>" for c in cols],
                    "fill_color": _BG,
                    "font": {"color": _TEXT, "size": 13},
                    "align": "left",
                },
                cells={
                    "values": [[row[c] for row in rows] for c in cols],
                    "fill_color": "#3b3b3b",
                    "font": {"color": _TEXT, "size": 12},
                    "align": "left",
                    "format": [None, None, None, ".3f", ".3f", ".3f", ".3f"],
                    "height": 26,
                },
            )
        ]
    )
    _dark_layout(fig, height=90 + 30 * len(rows))
    fig.update_layout(title=f"{len(rows)} 个 run 横向指标对比")
    return pn.pane.Plotly(fig)


def render_experiment_history(data: ExperimentHistoryData) -> dict:
    """渲染实验历史 Tab。

    pn 可用 → payload 含 _layout（左侧多选列表 + 右侧详情 pn.bind 动态区）；
    pn=None → 纯 dict（测试断言用）。
    """
    base: dict[str, Any] = {
        "component": data.component,
        "runs": data.runs,
        "truncated": data.truncated,
        "empty": not data.runs,
    }
    if pn is None:
        return base
    if not data.runs:
        base["_layout"] = pn.pane.Alert(
            "暂无 C1 实验记录。跑一次 C1（track=True）后会在此显示。",
            alert_type="info",
        )
        return base

    # options value 用 run_id（panel 实证：MultiSelect.param.value 返回 options 的 value 列表，
    # 若 value 放 RunSummary 对象则回调里再索引 options 会 TypeError unhashable——2026-08-16 浏览器实测）
    options = {f"{r.run_name}｜{r.start_time:%m-%d %H:%M}" if r.start_time else r.run_name: r.run_id for r in data.runs}
    by_id = {r.run_id: r for r in data.runs}
    selector = pn.widgets.MultiSelect(
        name="实验 run（单选看双净值对比，多选横向指标对比）",
        options=options,
        size=14,
        sizing_mode="stretch_width",
    )

    def _detail(selection: list[str]) -> pn.viewable.Viewable:
        if not selection:
            return pn.pane.Alert("← 选择 run 查看详情（单选=双净值对比，多选=横向指标表）", alert_type="info")
        picked = [by_id[rid] for rid in selection]
        if len(picked) == 1:
            view = fetch_c1_comparison(picked[0].run_id)
            if view is None:
                return pn.pane.Alert("run 不存在或已清理", alert_type="warning")
            return _render_c1_comparison(view)
        return _render_multi_run_comparison(picked)

    # P1-4 节流偏差说明（2026-08-16 实证）：当前 panel 版本 MultiSelect 无 value_throttled 参数
    # （value_throttled 仅文本输入类 widget 有）；MultiSelect 为离散选择事件（每次点击才触发一次
    # change），天然无文本输入式刷屏风险，退用 value 绑定（Panel 标准用法）。
    detail = pn.bind(_detail, selector.param.value)
    notice = pn.pane.Markdown("*仅显示最近 50 条*") if data.truncated else None
    left = pn.Column(selector, *([notice] if notice else []), max_width=420)
    base["_layout"] = pn.Row(left, detail, sizing_mode="stretch_width")
    return base
