# [BLUEPRINT] MOD-PLAN-013 | 待统筹登记（缺口总账 GAP-F-44 行；GAP-F-03 四角色链扩展基座上生长）
# [MODULE] zephyr.plan_engine.trading_analyst_agents
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.trading_debate（四角色链编排复用，GAP-F-03 已建）
# [CONSUMERS] 作战室多空辩论扩展（W4 五策略型 Analyst Agent 席）；（候选：GAP-F-42 证据链结构化为论点供给上游）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 五角色封闭 {trend_follower, mean_reverter, fundamental, sentiment_hunter, risk_defender}，齐备且不重复（fail-closed）；stance 三态封闭 {bullish, bearish, neutral}；多/空方论点按角色 stance 归边（NEUTRAL 两侧不入），按 confidence 降序截取 ≤3 条（45号 W4 论点 1~3 条契约）；一侧无论点→占位论点+notes 留痕（链可运行）；risk_defender stance=bearish 且 conviction≥阈值→VETO 恒优先；D3 fake_ratio>0.6 进攻方案硬否决规则在风控防守员中性时仍生效；本模块零 LLM/DB 调用（论点全注入）；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-44 行
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（角色/立场/置信度/论点数/齐备性非法，fail-closed）
# [TESTS] tests/plan_engine/test_trading_analyst_agents.py
# [A_module] module_id=MOD-PLAN-013_agents | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""交易域多 Analyst Agent 五角色实例化（GAP-F-44，MOD-PLAN-013 扩展）。

缺口总账 GAP-F-44（作战室多空辩论扩展，GAP-F-03 同族）：在牛/熊研究员四角色
链之上扩展五个策略型 Analyst Agent——

| 角色 | 立场语义 |
|---|---|
| trend_follower 趋势跟随 | 趋势/均线/动量维度给多空 |
| mean_reverter 均值回归 | 偏离度/反转维度给多空 |
| fundamental 基本面 | 业绩/估值/催化维度给多空 |
| sentiment_hunter 情绪猎手 | 舆情/情绪周期维度给多空 |
| risk_defender 风控防守 | 尾部/流动性风险维度，高置信看空有一票否决权 |

编排：五角色立场归边聚合（bullish 点归多方、bearish 归空方、neutral 两侧不入，
按 confidence 降序截取 ≤3 条）→ 复用 trading_debate 四角色链（辩论裁决→交易员
综合→风控裁决）；risk_defender 映射风控侧——stance=bearish 且 conviction≥
risk_veto_conviction（默认 0.7）→ 直接 VETO；否则 D3 撤单比硬规则兜底
（trading_debate.FAKE_RATIO_VETO 口径）。

不做什么：不调 LLM（五角色论点由上游 LLM/分析模块产出后注入）/不下单/
不改 ScenarioPlan（输出=质量门结论）。

依据: 缺口总账 GAP-F-44；45_warroom_playbook §4 W4；MOD-PLAN-013
SSoT: depgraph node 10505572（MOD-PLAN-013）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: DebateContext + 五 AnalystOpinion + debate_engine/trader_fn 注入位
# 特征: 立场归边（多方/空方论点集，置信度降序）
# 算法: 聚合 → trading_debate 四角色链（风控=risk_defender 否决 ∪ D3 硬规则）
# 输出: AnalystCouncilResult（debate_result + 归边明细 + notes）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final, Sequence

from zephyr.plan_engine.trading_debate import (
    DECISION_EXECUTE,
    FAKE_RATIO_VETO,
    ROLE_BEAR,
    ROLE_BULL,
    VERDICT_VETO,
    DebateContext,
    RiskVerdict,
    RoleArgument,
    TraderSynthesis,
    TradingDebateResult,
    run_trading_debate,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "ANALYST_ROLES",
    "ROLE_FUNDAMENTAL",
    "ROLE_MEAN_REVERTER",
    "ROLE_RISK_DEFENDER",
    "ROLE_SENTIMENT_HUNTER",
    "ROLE_TREND_FOLLOWER",
    "STANCE_BEARISH",
    "STANCE_BULLISH",
    "STANCE_NEUTRAL",
    "AnalystCouncilConfig",
    "AnalystCouncilResult",
    "AnalystOpinion",
    "run_analyst_council",
]

# ── 五角色与立场枚举（字符串常量，冻结词表）──

ROLE_TREND_FOLLOWER: Final = "trend_follower"  # 趋势跟随
ROLE_MEAN_REVERTER: Final = "mean_reverter"  # 均值回归
ROLE_FUNDAMENTAL: Final = "fundamental"  # 基本面
ROLE_SENTIMENT_HUNTER: Final = "sentiment_hunter"  # 情绪猎手
ROLE_RISK_DEFENDER: Final = "risk_defender"  # 风控防守

ANALYST_ROLES: Final = (
    ROLE_TREND_FOLLOWER,
    ROLE_MEAN_REVERTER,
    ROLE_FUNDAMENTAL,
    ROLE_SENTIMENT_HUNTER,
    ROLE_RISK_DEFENDER,
)
_ROLE_SET: Final = frozenset(ANALYST_ROLES)

STANCE_BULLISH: Final = "bullish"
STANCE_BEARISH: Final = "bearish"
STANCE_NEUTRAL: Final = "neutral"
_STANCES: Final = frozenset({STANCE_BULLISH, STANCE_BEARISH, STANCE_NEUTRAL})

_MAX_DEBATE_POINTS: Final = 3  # 45号 W4：研究员各 1~3 条核心论点


@dataclass(frozen=True, slots=True)
class AnalystOpinion:
    """单角色分析意见（上游 LLM/分析模块产出注入，本模块零 LLM 调用）。

    Attributes:
        role: 五角色之一。
        stance: bullish/bearish/neutral 三态。
        conviction: 自评置信度 [0,1]（归边截取排序依据；risk_defender 否决阈值判定）。
        points: 1~3 条核心论点（中文字符串可审计）。
    """

    role: str
    stance: str
    conviction: float
    points: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.role not in _ROLE_SET:
            raise ValueError(f"role 非法（合法={sorted(_ROLE_SET)}）: {self.role!r}")
        if self.stance not in _STANCES:
            raise ValueError(f"stance 非法（合法={sorted(_STANCES)}）: {self.stance!r}")
        if not (0.0 <= float(self.conviction) <= 1.0):
            raise ValueError(f"conviction 非法（须 ∈ [0,1]）: {self.conviction!r}")
        pts = tuple(str(p).strip() for p in self.points if str(p).strip())
        if not 1 <= len(pts) <= _MAX_DEBATE_POINTS:
            raise ValueError(f"points 非法（须 1~{_MAX_DEBATE_POINTS} 条）: {len(self.points)} 条")
        object.__setattr__(self, "points", pts)


@dataclass(frozen=True, slots=True)
class AnalystCouncilConfig:
    """五角色议事配置。"""

    risk_veto_conviction: float = 0.7  # risk_defender 高置信看空否决阈值

    def __post_init__(self) -> None:
        if not (0.0 < float(self.risk_veto_conviction) <= 1.0):
            raise ValueError(f"risk_veto_conviction 非法（须 ∈ (0,1]）: {self.risk_veto_conviction!r}")


@dataclass(frozen=True, slots=True)
class AnalystCouncilResult:
    """五角色议事总产出（JSON 可序列化）。"""

    debate_result: TradingDebateResult
    opinions: tuple[AnalystOpinion, ...]
    bull_side: tuple[str, ...]  # 多方论点贡献角色（confidence 降序）
    bear_side: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _aggregate_side(opinions: Sequence[AnalystOpinion], stance: str) -> tuple[tuple[str, ...], list[str]]:
    """立场归边：按 confidence 降序截取 ≤3 条论点，返回 (角色序, 论点序)。"""
    side = sorted(
        (o for o in opinions if o.stance == stance and o.role != ROLE_RISK_DEFENDER),
        key=lambda o: -o.conviction,
    )
    points: list[str] = []
    for op in side:
        for p in op.points:
            if len(points) >= _MAX_DEBATE_POINTS:
                break
            points.append(p)
        if len(points) >= _MAX_DEBATE_POINTS:
            break
    return tuple(o.role for o in side), points


def _council_risk(
    ctx: DebateContext,
    trader: TraderSynthesis,
    risk_opinion: AnalystOpinion,
    cfg: AnalystCouncilConfig,
) -> RiskVerdict:
    """风控侧合成：risk_defender 高置信看空否决 ∪ D3 撤单比硬规则兜底。"""
    if (
        risk_opinion.stance == STANCE_BEARISH
        and float(risk_opinion.conviction) >= cfg.risk_veto_conviction
    ):
        return RiskVerdict(
            verdict=VERDICT_VETO,
            reasons=[
                f"风控防守员否决（stance=bearish，conviction={risk_opinion.conviction:.2f}≥"
                f"{cfg.risk_veto_conviction}）：" + "；".join(risk_opinion.points)
            ],
        )
    # D3 硬规则兜底（trading_debate 默认风控同口径，>0.6 严格大于）
    if ctx.fake_ratio is not None and ctx.fake_ratio > FAKE_RATIO_VETO and ctx.is_offensive:
        return RiskVerdict(
            verdict=VERDICT_VETO,
            reasons=[
                f"D3 撤单比 fake_ratio={ctx.fake_ratio:.2f}>{FAKE_RATIO_VETO}（虚假申报，"
                "主力诱多/诱空），自动否决全部进攻方案（45号 W4 硬规则）"
            ],
        )
    return RiskVerdict(verdict="PASS", reasons=[])


def run_analyst_council(
    context: DebateContext,
    opinions: Sequence[AnalystOpinion],
    *,
    trader_fn: Callable[[DebateContext, RoleArgument, RoleArgument, str], TraderSynthesis] | None = None,
    debate_engine: Any | None = None,
    config: AnalystCouncilConfig | None = None,
) -> AnalystCouncilResult:
    """五角色议事编排主入口（聚合 → trading_debate 四角色链）。

    Args:
        context: 辩论语境（复用 trading_debate.DebateContext，fail-closed）。
        opinions: 五角色意见（五角色齐备且不重复，fail-closed）。
        trader_fn: 交易员注入位（LLM 交易员接线点）；None=默认规则交易员。
        debate_engine: 辩论引擎注入位（测试 mock）；None=新建 AgentDebate。
        config: 议事配置（None=默认否决阈值 0.7）。

    Returns:
        AnalystCouncilResult（含 trading_debate 全量结果与归边明细）。

    Raises:
        ValueError: 角色缺失/重复/非法（fail-closed）。
    """
    cfg = config or AnalystCouncilConfig()
    ops = tuple(opinions)
    roles = [o.role for o in ops]
    missing = [r for r in ANALYST_ROLES if r not in roles]
    if missing:
        raise ValueError(f"五角色不齐备（缺 {missing}）")
    if len(set(roles)) != len(roles):
        raise ValueError(f"角色重复（五角色各一席）: {roles}")

    notes: list[str] = []
    bull_roles, bull_points = _aggregate_side(ops, STANCE_BULLISH)
    bear_roles, bear_points = _aggregate_side(ops, STANCE_BEARISH)
    if not bull_points:
        bull_points = ["（五角色无看多论点，占位保链可运行）"]
        notes.append("多方无论点（占位论点注入，辩论参考性下降）")
    if not bear_points:
        bear_points = ["（五角色无看空论点，占位保链可运行）"]
        notes.append("空方无论点（占位论点注入，辩论参考性下降）")

    bull = RoleArgument(
        role=ROLE_BULL,
        points=tuple(bull_points),
        confidence=max((o.conviction for o in ops if o.stance == STANCE_BULLISH), default=None),
    )
    bear = RoleArgument(
        role=ROLE_BEAR,
        points=tuple(bear_points),
        confidence=max((o.conviction for o in ops if o.stance == STANCE_BEARISH), default=None),
    )
    risk_opinion = next(o for o in ops if o.role == ROLE_RISK_DEFENDER)

    debate_result = run_trading_debate(
        context,
        bull,
        bear,
        trader_fn=trader_fn,
        risk_fn=lambda ctx, trader: _council_risk(ctx, trader, risk_opinion, cfg),
        debate_engine=debate_engine,
    )
    if debate_result.final_outcome == DECISION_EXECUTE:
        log.debug("五角色议事通过: %s %s", context.trade_date, context.scenario)

    return AnalystCouncilResult(
        debate_result=debate_result,
        opinions=ops,
        bull_side=bull_roles,
        bear_side=bear_roles,
        notes=tuple(notes),
    )
