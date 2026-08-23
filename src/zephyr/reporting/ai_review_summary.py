# [BLUEPRINT] MOD-RPT-009 | docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md | 待统筹登记（缺口总账 GAP-F-40 行）
# [MODULE] zephyr.reporting.ai_review_summary
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.review_template_registry(MOD-RPT-032 模板注册位,模板单一真源); 无硬 LLM 依赖（LLM 经模型网关抽象 llm_gateway 注入位调用，本模块不 import 具体网关实现；测试全 mock）
# [CONSUMERS] （候选：盘后复盘页"一键生成战报"，GAP-F-40 消费位；渲染产物由调用方经 ReportPublisher 归档——归档唯一出口 D-RPT-D05）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] LLM 走模型网关抽象（prompt→text 注入位，本模块零真实 LLM/网络调用）；网关未注入/异常/空输出 → 模板兜底降级（fail-open 留痕不抛，source=template_fallback）；LLM 输出 strip+空白折叠+max_chars 截断；模板经 MOD-RPT-032 注册位供给（战报五段结构固定=注册位默认 v1，版本可切换+默认模板回退），空段降级"（无）"；只渲染不归档（D-RPT-D05，同 review_template_engine 口径）；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-40 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（trade_date/market_overview/max_chars 非法，fail-closed）；网关异常→模板兜底不抛
# [TESTS] tests/reporting/test_ai_review_summary.py
# [A_module] module_id=MOD-RPT-009_summary | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""AI 复盘结语生成器（GAP-F-40，MOD-RPT-009 复盘族扩展）。

缺口总账 GAP-F-40（盘后复盘页"一键生成战报"）：LLM 总结今日行情+操作建议
结语，注入战报模板。LLM 调用走模型网关抽象（``llm_gateway: prompt -> text``
注入位，生产侧接 infrastructure.pipeline.llm_gateway / 模型路由，测试 mock）——
本模块零真实 LLM/网络调用铁律（同 trading_debate 口径）。

降级链（复盘页不因为 LLM 挂掉而空白）：
    网关未注入 / 抛异常 / 空输出 → 参数化中文模板兜底结语
    （source=template_fallback + notes 留痕，fail-open 不抛）。

战报模板（五段固定，注入式渲染）：市场回顾/板块亮点/预案执行/风险事件/AI 结语。
模板经 MOD-RPT-032 模板注册位供给（config/review_templates.yaml，版本可切换+
默认模板回退；默认 v1=迁移前代码常量原文）——本模块不再持有模板文本常量。
本模块只渲染不归档（归档唯一出口 ReportPublisher，D-RPT-D05，同
review_template_engine 口径）。

依据: 缺口总账 GAP-F-40；MOD-RPT-009 复盘族
SSoT: depgraph node 10505569（blueprint MOD-RPT-009）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: ReviewContext（日期/市场概述/板块亮点/预案执行/风险事件）+ llm_gateway 注入位
# 算法: prompt 参数化构建 → 网关调用（异常/空降级模板）→ 输出归一（strip/折叠/截断）→ 战报模板注入渲染
# 输出: ReviewSummary（source=llm|template_fallback）+ render_war_report markdown
"""

from __future__ import annotations

import datetime as _dt
import logging
import re as _re
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final

from zephyr.reporting.review_template_registry import (
    TEMPLATE_FALLBACK_SUMMARY,
    TEMPLATE_PROMPT_SUMMARY,
    TEMPLATE_WAR_REPORT,
    ReviewTemplateRegistry,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "ReviewContext",
    "ReviewSummary",
    "SummaryConfig",
    "generate_review_summary",
    "render_war_report",
]

#: 模型网关抽象签名：prompt → 文本（生产接模型网关，测试 mock）
LLMSummaryGateway = Callable[[str], str]

_DATE_RE: Final = _re.compile(r"\d{4}-\d{2}-\d{2}")
_WS_RE: Final = _re.compile(r"\s+")

_EMPTY_FALLBACK: Final = "（无）"

#: 打包默认模板注册表（懒加载单例；未显式注入注册位时的零配置路径）
_DEFAULT_REGISTRY: "ReviewTemplateRegistry | None" = None


def _default_registry() -> ReviewTemplateRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = ReviewTemplateRegistry.embedded_default()
    return _DEFAULT_REGISTRY


@dataclass(frozen=True, slots=True)
class SummaryConfig:
    """结语生成配置。"""

    max_chars: int = 200

    def __post_init__(self) -> None:
        if int(self.max_chars) < 10:
            raise ValueError(f"max_chars 非法（须 ≥10）: {self.max_chars!r}")


@dataclass(frozen=True, slots=True)
class ReviewContext:
    """复盘语境（上游装配注入，全部字符串/字符串序列）。"""

    trade_date: str
    market_overview: str
    sector_highlights: tuple[str, ...] = ()
    plan_outcomes: tuple[str, ...] = ()
    risk_events: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, str) or not _DATE_RE.fullmatch(self.trade_date):
            raise ValueError(f"trade_date 非法（须 YYYY-MM-DD）: {self.trade_date!r}")
        try:
            _dt.date.fromisoformat(self.trade_date)
        except ValueError as exc:
            raise ValueError(f"trade_date 非真实日期: {self.trade_date!r}") from exc
        if not isinstance(self.market_overview, str) or not self.market_overview.strip():
            raise ValueError(f"market_overview 非法（强制非空）: {self.market_overview!r}")
        object.__setattr__(self, "market_overview", self.market_overview.strip())
        for name in ("sector_highlights", "plan_outcomes", "risk_events"):
            items = tuple(str(x).strip() for x in getattr(self, name) if str(x).strip())
            object.__setattr__(self, name, items)


@dataclass(frozen=True, slots=True)
class ReviewSummary:
    """复盘结语产出（source=llm/template_fallback 可审计，JSON 可序列化）。"""

    trade_date: str
    summary_text: str
    source: str  # "llm" | "template_fallback"
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _join(items: tuple[str, ...]) -> str:
    return "；".join(items) if items else _EMPTY_FALLBACK


def _normalize(text: str, max_chars: int) -> str:
    return _WS_RE.sub(" ", text).strip()[:max_chars]


def _fallback_summary(ctx: ReviewContext, registry: ReviewTemplateRegistry) -> str:
    return registry.get(TEMPLATE_FALLBACK_SUMMARY).body.format(
        trade_date=ctx.trade_date,
        market_overview=ctx.market_overview,
        sector_highlights=_join(ctx.sector_highlights),
        plan_outcomes=_join(ctx.plan_outcomes),
        risk_events=_join(ctx.risk_events),
    )


def generate_review_summary(
    context: ReviewContext,
    *,
    llm_gateway: LLMSummaryGateway | None = None,
    config: SummaryConfig | None = None,
    template_registry: ReviewTemplateRegistry | None = None,
) -> ReviewSummary:
    """复盘结语生成主入口（LLM 走模型网关抽象，降级链 fail-open）。

    Args:
        context: 复盘语境（fail-closed 校验见 ReviewContext）。
        llm_gateway: 模型网关注入位（prompt→text）；None=模板兜底。
        config: 生成配置（None=默认 200 字封顶）。
        template_registry: MOD-RPT-032 模板注册位（None=打包默认注册表 v1）。

    Returns:
        ReviewSummary（source 标定 llm/template_fallback，notes 留痕降级原因）。
    """
    cfg = config or SummaryConfig()
    registry = template_registry or _default_registry()
    notes: list[str] = []

    if llm_gateway is None:
        notes.append("LLM 网关未注入（模板兜底）")
        return ReviewSummary(
            trade_date=context.trade_date,
            summary_text=_fallback_summary(context, registry),
            source="template_fallback",
            notes=tuple(notes),
        )

    prompt = registry.get(TEMPLATE_PROMPT_SUMMARY).body.format(
        trade_date=context.trade_date,
        market_overview=context.market_overview,
        sector_highlights=_join(context.sector_highlights),
        plan_outcomes=_join(context.plan_outcomes),
        risk_events=_join(context.risk_events),
        max_chars=cfg.max_chars,
    )
    try:
        raw = llm_gateway(prompt)
    except Exception as exc:  # noqa: BLE001 — 网关异常降级，复盘页不因 LLM 挂而空白
        logger.warning("LLM 网关异常降级模板兜底: %s: %s", type(exc).__name__, exc)
        notes.append(f"LLM 网关异常降级（{type(exc).__name__}）")
        return ReviewSummary(
            trade_date=context.trade_date,
            summary_text=_fallback_summary(context, registry),
            source="template_fallback",
            notes=tuple(notes),
        )

    text = _normalize(str(raw or ""), cfg.max_chars)
    if not text:
        notes.append("LLM 输出为空（模板兜底）")
        return ReviewSummary(
            trade_date=context.trade_date,
            summary_text=_fallback_summary(context, registry),
            source="template_fallback",
            notes=tuple(notes),
        )
    return ReviewSummary(
        trade_date=context.trade_date,
        summary_text=text,
        source="llm",
        notes=tuple(notes),
    )


def render_war_report(
    context: ReviewContext,
    summary: ReviewSummary,
    *,
    template_registry: ReviewTemplateRegistry | None = None,
    template_version: str | None = None,
) -> str:
    """战报模板注入渲染（五段固定；只渲染不归档——归档经 ReportPublisher）。

    Args:
        context: 复盘语境。
        summary: generate_review_summary 产出（结语注入第 5 段）。
        template_registry: MOD-RPT-032 模板注册位（None=打包默认注册表）。
        template_version: 模板版本（None=注册表默认版本；未注册版本回退默认）。

    Returns:
        战报 markdown 字符串。
    """
    registry = template_registry or _default_registry()
    return registry.get(TEMPLATE_WAR_REPORT, template_version).body.format(
        trade_date=context.trade_date,
        market_overview=context.market_overview,
        sector_highlights=_join(context.sector_highlights),
        plan_outcomes=_join(context.plan_outcomes),
        risk_events=_join(context.risk_events),
        summary=summary.summary_text,
    )
