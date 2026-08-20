# [BLUEPRINT] MOD-RPT-009 | docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md
# [MODULE] zephyr.reporting.review_template_engine
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.review_orchestrator(WEEKLY_REVIEW_SECTIONS 单一真源); zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RPT-009(ReviewOrchestrator.run_weekly 装配可选升级); 调用方(周复盘事件驱动)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 四段结构固定不可增删(55号§3.6决策五, 段标题单一真源=review_orchestrator.WEEKLY_REVIEW_SECTIONS); 空段降级"（本期无）"不留空洞; 纯函数零副作用(渲染不归档, 归档归 ReportPublisher); 输入必须字符串/字符串序列
# [MODIFY-GUARD] 55_monitoring_review.md §3.6/§6
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTemplateInputError(ZA-RPT-0031)
# [TESTS] tests/reporting/test_review_template_engine.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: period(复盘周期) + 四段内容(pnl_attribution/deviation_events/threshold_changes 字符串, action_items 字符串序列) + risk_overview(可选风险概览行)
# F1: render_weekly_review()——按 weekly_review_template.md 结构渲染四段式周报 markdown
# F2: 空段降级——空字符串/空序列段渲染"（本期无）"(结构完整不留空洞)
# A1: 段标题渲染顺序=WEEKLY_REVIEW_SECTIONS 常量序(四段固定)
# O1: markdown 字符串(调用方经 ReportPublisher TRADING_REVIEW 源归档)
# [/ALGO_FLOW]
"""D_REPORTING — 周复盘模板引擎（55 号 §6 暂缓项固化，函数级 MVP）。

55 号 §6："复盘模板内容固化进代码（模板引擎）——先人工维护模板，跑 3 个月
稳定后再固化"。本模块把 weekly_review_template.md 的四段结构固化为纯函数
渲染器（段标题单一真源=review_orchestrator.WEEKLY_REVIEW_SECTIONS，不复制
常量）；渲染产物由调用方经 ReportPublisher（TRADING_REVIEW 源）归档——
本引擎只渲染不归档（归档唯一出口铁律 D-RPT-D05）。
"""

from __future__ import annotations

from typing import Final, Sequence

from zephyr.reporting.review_orchestrator import WEEKLY_REVIEW_SECTIONS
from zephyr.shared.foundation.errors import ZephyrBaseError

_EMPTY_SECTION_FALLBACK: Final[str] = "（本期无）"


class InvalidTemplateInputError(ZephyrBaseError):
    """模板引擎输入非法——空 period / 段内容类型错误等。"""

    error_code = "ZA-RPT-0031"


def _require_text(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise InvalidTemplateInputError(
            f"{name} 必须为字符串",
            details={"field": name, "type": type(value).__name__},
        )
    return value


def _section_body(text: str) -> str:
    body = text.strip()
    return body if body else _EMPTY_SECTION_FALLBACK


def render_weekly_review(
    period: str,
    pnl_attribution: str,
    deviation_events: str,
    threshold_changes: str,
    action_items: Sequence[str],
    risk_overview: str | None = None,
) -> str:
    """渲染四段式周复盘 markdown（结构固定，空段降级）。

    Args:
        period: 复盘周期标识（如 "2026-W34"）。
        pnl_attribution: 第①段 本周盈亏与归因（54 号对账归因链路供给）。
        deviation_events: 第②段 偏离与告警事件（MOD-RK-23 快照 + 告警清单）。
        threshold_changes: 第③段 阈值与参数变更（注册表变更清单）。
        action_items: 第④段 下周 action items（逐条字符串，渲染为 checkbox）。
        risk_overview: 可选风险概览行（日均评分/最大回撤/告警数/趋势）。

    Returns:
        四段式周报 markdown（段序 = WEEKLY_REVIEW_SECTIONS 固定）。

    Raises:
        InvalidTemplateInputError: period 空 / 段内容非字符串 / action_items
            含非字符串项。
    """
    if not isinstance(period, str) or not period.strip():
        raise InvalidTemplateInputError("period 不能为空", details={"period": repr(period)})
    s1 = _section_body(_require_text("pnl_attribution", pnl_attribution))
    s2 = _section_body(_require_text("deviation_events", deviation_events))
    s3 = _section_body(_require_text("threshold_changes", threshold_changes))
    if action_items is None:
        raise InvalidTemplateInputError("action_items 不能为 None", details={})
    items: list[str] = []
    for item in action_items:
        items.append(_require_text("action_item", item))

    sec1, sec2, sec3, sec4 = WEEKLY_REVIEW_SECTIONS
    lines: list[str] = [f"# 周复盘 {period.strip()}", ""]
    if risk_overview and risk_overview.strip():
        lines += [f"> 风险概览：{risk_overview.strip()}", ""]
    lines += [f"## 1. {sec1}", "", s1, ""]
    lines += [f"## 2. {sec2}", "", s2, ""]
    lines += [f"## 3. {sec3}", "", s3, ""]
    lines += [f"## 4. {sec4}", ""]
    if items:
        lines += [f"- [ ] {item.strip()}" for item in items]
    else:
        lines.append(_EMPTY_SECTION_FALLBACK)
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "InvalidTemplateInputError",
    "render_weekly_review",
]
