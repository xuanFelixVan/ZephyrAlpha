# [BLUEPRINT] MOD-PLAN-013 | 待统筹登记（缺口总账 GAP-F-03 + 45号作战手册 §4 W4）
# [MODULE] zephyr.plan_engine.trading_debate
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.governance.intelligence_governance.agent_debate（AgentDebate/DebateVerdict 复用，已 production）
# [CONSUMERS] 作战室 W4 多空辩论台（预案质量门）; （候选：GAP-F-44 五角色 Analyst Agent 扩展基座）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 四角色链顺序固定（牛/熊研究员→交易员→风控）；牛/熊各 1~3 条核心论点（45号 W4）；风控 veto 恒优先于交易员结论（veto→SIT_OUT+red_flag）；D3 fake_ratio>0.6 且进攻方案→自动否决（45号 W4 硬规则，>0.6 严格大于对齐 44号 §9.11）；本模块零 LLM/DB 调用（角色论点/综合/风控结论全部注入，LLM 网关接线=上游职责）；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-03 行
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（context/role/trader_fn 返回值非法 fail-closed）；辩论引擎异常→debate_verdict="ENGINE_ERROR" 降级留痕不抛（质量门不阻塞预案主流程）
# [TESTS] tests/plan_engine/test_trading_debate.py
# [A_module] module_id=MOD-PLAN-013 | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""TradingDebate — 交易域多空辩论四角色链编排 (MOD-PLAN-013)

缺口总账 GAP-F-03（=前端设计文档缺口⑧）落码：作战室 W4 多空辩论台（预案质量门）。
复用 agent_debate（DebateVerdict，治理域双模型辩论已 production）作辩论裁决引擎，
本模块=交易域四角色实例化+编排入口（TradingAgents 四段式骨架：多空辩论→交易员
综合→风控 veto，45号 §3.4 对标血统）。

四角色链（45号 §4 W4 契约）：
    ① 多头研究员 vs 空头研究员：各 1~3 条核心论点（输入=技术/新闻/情绪/基本面
       四路分析文本，由上游 LLM/分析模块产出后经 RoleArgument 注入）；
       辩论裁决复用 AgentDebate.debate()（content_hash 一致→AGREE 共识，
       不一致→OVERRIDE 需人工/规则裁决）。
    ② 交易员综合：trader_fn 注入位（LLM 交易员接线点）；默认规则交易员——
       辩论共识 AGREE → EXECUTE ×1.0；分歧 → DOWNSIZE 降半档 ×0.8
       （44号 §9.6 半档=-20% 口径）。
    ③ 风控官：risk_fn 注入位；默认规则风控——D3 fake_ratio>0.6 且进攻方案
       → 自动 VETO（45号 W4："D3>0.6 自动否决全部进攻方案"，虚假申报诱多/诱空
       红色警示）；veto → 该情景方案 SIT_OUT + red_flag（W4 红色标注契约）。

不做什么：不调 LLM（角色内容全部注入，模型网关接线属上游编排）/不下单/
         不改 ScenarioPlan（输出=质量门结论，消费方负责降仓/禁用应用）/
         不做方向点预测（90号 §7 只画栏杆不算命）。

依据: 缺口总账 GAP-F-03；45_warroom_playbook §4 W4；44号 §9.6/§9.11
SSoT: depgraph MOD-PLAN-013（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: DebateContext(交易日/情景/档位/进攻标记/D3 fake_ratio/四路分析) + 牛/熊 RoleArgument + trader_fn/risk_fn 注入位
# 特征: 辩论裁决 verdict / 交易员 decision+scale / 风控 verdict+reasons
# 算法: 牛熊辩论(agent_debate) → 交易员综合(默认规则或可注入) → 风控裁决(D3>0.6 进攻自动否决) → 终局合成(veto 优先)
# 输出: TradingDebateResult（纯 frozen dataclass，JSON 可序列化，供 W4 展示+预案降仓联动）
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Final

from zephyr.governance.intelligence_governance.agent_debate import AgentDebate

log = logging.getLogger(__name__)

__all__: Final = [
    "DECISION_DOWNSIZE",
    "DECISION_EXECUTE",
    "DECISION_SIT_OUT",
    "VERDICT_PASS",
    "VERDICT_VETO",
    "DebateContext",
    "RiskVerdict",
    "RoleArgument",
    "TraderSynthesis",
    "TradingDebateConfig",
    "TradingDebateResult",
    "run_trading_debate",
]

# ── 角色与结论枚举（字符串常量，冻结词表）──

ROLE_BULL: Final = "BULL_RESEARCHER"  # 多头研究员
ROLE_BEAR: Final = "BEAR_RESEARCHER"  # 空头研究员

DECISION_EXECUTE: Final = "EXECUTE"  # 交易员：按预案执行
DECISION_DOWNSIZE: Final = "DOWNSIZE"  # 交易员：降半档执行
DECISION_SIT_OUT: Final = "SIT_OUT"  # 终局：放弃该情景方案（禁做）

VERDICT_PASS: Final = "PASS"  # 风控通过
VERDICT_VETO: Final = "VETO"  # 风控否决

_TRADER_DECISIONS: Final = frozenset({DECISION_EXECUTE, DECISION_DOWNSIZE, DECISION_SIT_OUT})
_ROLES: Final = frozenset({ROLE_BULL, ROLE_BEAR})

FAKE_RATIO_VETO: Final = 0.6  # D3 虚假申报否决阈值（44号 §9.11，>0.6 严格大于）
HALF_NOTCH_SCALE: Final = 0.8  # 降半档=-20%（44号 §9.6）


# ── 输入契约 ──


@dataclass(frozen=True, slots=True)
class DebateContext:
    """辩论语境（四路分析+竞价三细节语境，上游装配注入）。

    Attributes:
        trade_date: 交易日 YYYY-MM-DD
        scenario: 被质询的情景方案（SCENARIO_LIST 语义，如 FLAT_OPEN_REAL_UP）
        stance: 档位名（CONSERVATIVE/DEFENSIVE/NORMAL/OFFENSIVE/AGGRESSIVE）
        is_offensive: 该情景方案是否进攻属性（D3 自动否决只打进攻方案）
        fake_ratio: D3 撤单比（9:25 竞价验证产出；None=未执行/缺数据不触发自动否决）
        channels: 四路分析文本 {technical/news/sentiment/fundamental: str}（可缺省）
    """

    trade_date: str
    scenario: str
    stance: str = "NORMAL"
    is_offensive: bool = True
    fake_ratio: float | None = None
    channels: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        import datetime as _dt
        import re as _re

        if not isinstance(self.trade_date, str) or not _re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.trade_date):
            raise ValueError(f"trade_date 非法（须 YYYY-MM-DD）: {self.trade_date!r}")
        try:
            _dt.date.fromisoformat(self.trade_date)
        except ValueError as exc:
            raise ValueError(f"trade_date 非真实日期: {self.trade_date!r}") from exc
        if not isinstance(self.scenario, str) or not self.scenario.strip():
            raise ValueError(f"scenario 非法（须非空字符串）: {self.scenario!r}")
        if self.fake_ratio is not None and not (0.0 <= float(self.fake_ratio) <= 1.0):
            raise ValueError(f"fake_ratio 非法（须 ∈ [0,1]）: {self.fake_ratio!r}")


@dataclass(frozen=True, slots=True)
class RoleArgument:
    """研究员论点（牛/熊各 1~3 条核心论点，45号 W4 契约）。

    论点文本由上游 LLM/分析模块产出（技术/新闻/情绪/基本面四路综合），
    本模块只编排不生成（零 LLM 调用铁律）。
    """

    role: str  # ROLE_BULL / ROLE_BEAR
    points: tuple[str, ...]  # 1~3 条核心论点
    confidence: float | None = None  # 研究员自评置信度 [0,1]（留痕，不参与裁决）

    def __post_init__(self) -> None:
        if self.role not in _ROLES:
            raise ValueError(f"role 非法（合法={sorted(_ROLES)}）: {self.role!r}")
        pts = tuple(str(p).strip() for p in self.points if str(p).strip())
        if not 1 <= len(pts) <= 3:
            raise ValueError(f"points 非法（须 1~3 条核心论点）: {len(self.points)} 条")
        object.__setattr__(self, "points", pts)
        if self.confidence is not None and not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError(f"confidence 非法（须 ∈ [0,1]）: {self.confidence!r}")


# ── 角色产出契约 ──


@dataclass(frozen=True, slots=True)
class TraderSynthesis:
    """交易员综合结论（可降半档，45号 W4）。"""

    decision: str  # EXECUTE / DOWNSIZE / SIT_OUT
    scale: float  # 仓位缩放（DOWNSIZE 默认 0.8 半档）
    rationale: str  # 综合理由（中文可审计）


@dataclass(frozen=True, slots=True)
class RiskVerdict:
    """风控官裁决（通过/否决；veto 时该情景方案降仓或禁用，红色标注）。"""

    verdict: str  # PASS / VETO
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TradingDebateConfig:
    """辩论编排配置（默认值=44/45号设计口径）。"""

    fake_ratio_veto: float = FAKE_RATIO_VETO  # D3 自动否决阈值（严格大于）
    half_notch_scale: float = HALF_NOTCH_SCALE  # 交易员降半档缩放

    def __post_init__(self) -> None:
        if not (0.0 < float(self.fake_ratio_veto) < 1.0):
            raise ValueError(f"fake_ratio_veto 非法（须 ∈ (0,1)）: {self.fake_ratio_veto!r}")
        if not (0.0 < float(self.half_notch_scale) <= 1.0):
            raise ValueError(f"half_notch_scale 非法（须 ∈ (0,1]）: {self.half_notch_scale!r}")


@dataclass(frozen=True, slots=True)
class TradingDebateResult:
    """四角色链总产出（W4 展示+预案降仓联动契约，JSON 可序列化）。"""

    trade_date: str
    scenario: str
    debate_verdict: str  # DebateVerdict 值（AGREE/OVERRIDE/...）或 ENGINE_ERROR 降级
    bull: RoleArgument
    bear: RoleArgument
    trader: TraderSynthesis
    risk: RiskVerdict
    final_outcome: str  # 终局（veto 优先于交易员）
    final_scale: float  # 终局仓位缩放（SIT_OUT=0.0）
    red_flag: bool  # 风控 veto 红色标注（W4 契约）
    annotations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        from dataclasses import asdict

        return asdict(self)


# ── 默认规则交易员/风控（注入位的缺省实现，规则可审计非 LLM）──


def _default_trader(
    ctx: DebateContext,
    bull: RoleArgument,
    bear: RoleArgument,
    verdict: str,
    config: TradingDebateConfig,
) -> TraderSynthesis:
    """默认规则交易员：辩论共识 → EXECUTE；分歧 → DOWNSIZE 降半档。"""
    if verdict == "AGREE":
        return TraderSynthesis(
            decision=DECISION_EXECUTE,
            scale=1.0,
            rationale="多空辩论共识（论点一致），按预案执行",
        )
    return TraderSynthesis(
        decision=DECISION_DOWNSIZE,
        scale=config.half_notch_scale,
        rationale=f"多空分歧（{verdict}），降半档×{config.half_notch_scale} 执行（留人工裁决空间）",
    )


def _default_risk(ctx: DebateContext, trader: TraderSynthesis, config: TradingDebateConfig) -> RiskVerdict:
    """默认规则风控：D3 fake_ratio>阈值 且进攻方案 → 自动否决（45号 W4 硬规则）。"""
    if ctx.fake_ratio is not None and ctx.fake_ratio > config.fake_ratio_veto and ctx.is_offensive:
        return RiskVerdict(
            verdict=VERDICT_VETO,
            reasons=[
                f"D3 撤单比 fake_ratio={ctx.fake_ratio:.2f}>{config.fake_ratio_veto}（虚假申报，"
                "主力诱多/诱空），自动否决全部进攻方案（45号 W4 硬规则）"
            ],
        )
    return RiskVerdict(verdict=VERDICT_PASS, reasons=[])


# ── 编排入口 ──


def run_trading_debate(
    context: DebateContext,
    bull: RoleArgument,
    bear: RoleArgument,
    *,
    trader_fn: Callable[[DebateContext, RoleArgument, RoleArgument, str], TraderSynthesis] | None = None,
    risk_fn: Callable[[DebateContext, TraderSynthesis], RiskVerdict] | None = None,
    debate_engine: Any | None = None,
    config: TradingDebateConfig | None = None,
) -> TradingDebateResult:
    """四角色链编排主入口（牛/熊→交易员→风控）。

    Args:
        context: 辩论语境（fail-closed 校验见 DebateContext）。
        bull: 多头研究员论点（1~3 条）。
        bear: 空头研究员论点（1~3 条）。
        trader_fn: 交易员注入位（LLM 交易员接线点）；None=默认规则交易员。
        risk_fn: 风控官注入位；None=默认规则风控（D3 自动否决）。
        debate_engine: 辩论引擎注入位（测试 mock）；None=新建 AgentDebate。
        config: 编排配置（None=设计默认值）。

    Returns:
        TradingDebateResult（风控 veto 恒优先：final_outcome=SIT_OUT+red_flag）。

    Raises:
        ValueError: bull/bear 角色错位、trader_fn 返回非法 decision（fail-closed）。
    """
    cfg = config or TradingDebateConfig()
    if bull.role != ROLE_BULL:
        raise ValueError(f"bull 参数角色错位（须 {ROLE_BULL}）: {bull.role!r}")
    if bear.role != ROLE_BEAR:
        raise ValueError(f"bear 参数角色错位（须 {ROLE_BEAR}）: {bear.role!r}")

    notes: list[str] = []
    annotations: list[str] = []

    # ① 牛熊辩论（复用 agent_debate 已 production 框架）
    engine = debate_engine if debate_engine is not None else AgentDebate()
    bull_text = "\n".join(bull.points)
    bear_text = "\n".join(bear.points)
    try:
        verdict = engine.debate(ROLE_BULL, bull_text, ROLE_BEAR, bear_text)
        verdict_str = str(getattr(verdict, "value", verdict))
    except Exception as exc:  # noqa: BLE001 — 辩论引擎异常降级，质量门不阻塞预案主流程
        log.warning("辩论引擎异常降级: %s: %s", type(exc).__name__, exc)
        verdict_str = "ENGINE_ERROR"
        notes.append(f"辩论引擎异常降级（按分歧处理）: {type(exc).__name__}")

    # ② 交易员综合
    if trader_fn is not None:
        trader = trader_fn(context, bull, bear, verdict_str)
    else:
        trader = _default_trader(context, bull, bear, verdict_str, cfg)
    if not isinstance(trader, TraderSynthesis) or trader.decision not in _TRADER_DECISIONS:
        raise ValueError(f"trader_fn 返回非法（decision 须 ∈ {sorted(_TRADER_DECISIONS)}）: {trader!r}")
    if not (0.0 <= float(trader.scale) <= 1.0):
        raise ValueError(f"trader scale 非法（须 ∈ [0,1]）: {trader.scale!r}")

    # ③ 风控官裁决
    risk = risk_fn(context, trader) if risk_fn is not None else _default_risk(context, trader, cfg)
    if not isinstance(risk, RiskVerdict) or risk.verdict not in {VERDICT_PASS, VERDICT_VETO}:
        raise ValueError(f"risk_fn 返回非法（verdict 须 PASS/VETO）: {risk!r}")

    # ④ 终局合成（风控 veto 恒优先，45号 W4：veto 时该情景方案降仓或禁用）
    if risk.verdict == VERDICT_VETO:
        final_outcome = DECISION_SIT_OUT
        final_scale = 0.0
        red_flag = True
        annotations.append("风控否决：该情景方案禁用（红色标注，W0 归因记执行不一致若强行执行）")
    else:
        final_outcome = trader.decision
        final_scale = 0.0 if trader.decision == DECISION_SIT_OUT else float(trader.scale)
        red_flag = False

    return TradingDebateResult(
        trade_date=context.trade_date,
        scenario=context.scenario,
        debate_verdict=verdict_str,
        bull=bull,
        bear=bear,
        trader=trader,
        risk=risk,
        final_outcome=final_outcome,
        final_scale=final_scale,
        red_flag=red_flag,
        annotations=annotations,
        notes=notes,
    )
