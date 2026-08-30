# [BLUEPRINT] MOD-XS-015 | docs/03_modules/_domain_ex_sor/sor_agent/blueprint.md
# [MODULE] zephyr.ex_sor.core.sor_agent
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] 标准库; zephyr.ex_core.order_splitter(惰性, 默认拆单委托可注入替代)
# [CONSUMERS] 运行时装配批（MOD-XS-001 路由算法委托 / EX-CORE Pre-Trade 风控链 / broker_api_connector 券商通道执行 / D_FEEDBACK_LOOP 滑点反馈回路）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Level 0纯规则(禁LLM写入门控); decide 判定核心无IO无下单语义; SOR不做风控判断(§6.1归EX-CORE); weights和=1.0 Fail-Closed; 低流动性通道先行剔除; 拆单委托不重建算法; 滑点实际vs预估回写配对留痕; 全部决策可回放(replay_id单调)
# [MODIFY-GUARD] docs/03_modules/_domain_ex_sor/sor_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SorAgentError(占位 ZA-XS-UNREGISTERED-SOR-AGENT)——LLM回调注入/weights非法/无候选/请求非法/拆单失败/未知replay_id时抛
# [TESTS] tests/ex_sor/test_sor_agent.py
# [A_module] module_id=MOD-XS-015 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""
SorAgent — 路由Agent（SOR）（MOD-XS-015）。

B11-02491（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-SOR-001，A7-Agent架构
§1.4）：SOR Agent 实体（族卡模式，与 MOD-AU-011 T0TraderAgent 同族）。
**Level 0 纯规则**（禁 LLM 调用写入门控）承载两技能——智能路由（通道
选择 / 盘口流动性评估）+ 拆单策略（复用 order_splitter：冰山 / TWAP /
量比拆单）；滑点实际 vs 预估回写反馈循环；所有决策可回放。

查重分工（蓝图 §0 铁律⑤）：optimal_order_router=路由算法件（本件=Agent
实体：族卡+技能编排+回放+反馈循环）；order_splitter=拆单纯函数（委托不
重建）；llm_agent_router=LLM 模型路由（零交集）；smart_order_router 全仓
不存在。与 C-026/C-046 对齐：本 Agent 无下单语义，执行委托券商通道装配批。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: weights 参数
#   fields: 参数 weights（无注解）
#   code: sor_agent.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: min_liquidity 参数
#   fields: 参数 min_liquidity（无注解）
#   code: sor_agent.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: splitter_fn 参数
#   fields: 参数 splitter_fn（无注解）
#   code: sor_agent.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: feedback_sink 参数
#   fields: 参数 feedback_sink（无注解）
#   code: sor_agent.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SorAgent
#   name_en: SorAgent
#   intro: 路由Agent（SOR，MOD-XS-015）——Level 0 纯规则。
#   desc: 路由Agent（SOR，MOD-XS-015）——Level 0 纯规则。 用法： agent = SorAgent(splitter_fn=my_splitter, feedb…；公共方法（定义序）: decide,…
#   inputs: weights min_liquidity splitter_fn feedback_sink replay_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: SorAgent
#   downstream: 运行时装配批（MOD-XS-001 路由算法委托 / EX-CORE Pre-Trade 风控链 / broker_api_connector 券商通道执行…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import itertools
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AGENT_CARD",
    "BrokerCandidate",
    "SlippageFeedback",
    "SorAgent",
    "SorAgentError",
    "SorDecision",
    "SorRequest",
    "SorRouteWeights",
]

ROLE: Final[str] = "sor"

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "autonomyLevel": "L0_rule_only",
    "capabilities": [
        {
            "id": "smart_routing",
            "name": "智能路由（通道选择 / 盘口流动性评估，四维加权评分）",
            "inputs": "SorRequest + BrokerCandidate 列表（装配注入券商指标）",
            "outputs": "SorDecision（broker_id + score + rationale）",
            "autonomyLevel": "L0_rule_only",
        },
        {
            "id": "order_splitting",
            "name": "拆单策略（冰山/TWAP/量比，委托 MOD-EX-014 order_splitter）",
            "inputs": "SorRequest.split_algo + slice_count + volume_profile",
            "outputs": "SorDecision.split_plan（Σ片量=总量守恒由委托件保证）",
            "autonomyLevel": "L0_rule_only",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": ["裁决理由文本", "评分口径说明"],
        "human_gated": ["灰度上线路径（策略发布归 MOD-INF-072）"],
        "immutable": [
            "禁 LLM 调用（Level 0 纯规则红线，构造期门控断言）",
            "SOR 不做风控判断（D-EX-SOR §6.1，风控归 EX-CORE Pre-Trade）",
            "本 Agent 无下单语义（执行委托券商通道 broker_api_connector 装配批）",
            "拆单算法本体（MOD-EX-014 order_splitter，委托不重建）",
        ],
    },
    "healthCheck": {"heartbeat": "on_demand_decide"},
    "metadata": {"no_llm": "true", "replayable": "true"},
}


class SorAgentError(Exception):
    """SOR Agent 操作非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-XS-UNREGISTERED-SOR-AGENT。
    """


@dataclass(frozen=True)
class BrokerCandidate:
    """券商通道候选（指标由装配批注入）。"""

    broker_id: str
    latency_ms: float  # 通道延迟（越低越好）
    fill_rate: float  # 成交率 ∈[0,1]（越高越好）
    cost_bps: float  # 费用 bps（越低越好）
    liquidity_score: float  # 盘口流动性评分 ∈[0,1]（越高越好）

    def __post_init__(self) -> None:
        if not self.broker_id:
            raise SorAgentError("broker_id 不能为空")
        if self.latency_ms < 0 or self.cost_bps < 0:
            raise SorAgentError("latency_ms/cost_bps 须非负")
        if not (0.0 <= self.fill_rate <= 1.0) or not (0.0 <= self.liquidity_score <= 1.0):
            raise SorAgentError("fill_rate/liquidity_score 须落在 [0,1]")


@dataclass(frozen=True)
class SorRouteWeights:
    """路由四维评分权重（和=1.0 Fail-Closed）。"""

    w_latency: float = 0.25
    w_fill_rate: float = 0.35
    w_cost: float = 0.20
    w_liquidity: float = 0.20

    def __post_init__(self) -> None:
        ws = (self.w_latency, self.w_fill_rate, self.w_cost, self.w_liquidity)
        if any(w < 0 for w in ws):
            raise SorAgentError(f"权重须非负: {ws}")
        if abs(sum(ws) - 1.0) > 1e-6:
            raise SorAgentError(f"权重和须=1.0（实得 {sum(ws)}）")


@dataclass(frozen=True)
class SorRequest:
    """SOR 路由+拆单请求。"""

    symbol: str
    side: str  # BUY/SELL
    quantity: int  # 订单总量（股，正数）
    price: float  # 参考价（正数）
    split_algo: str = "twap"  # iceberg/twap/volume_ratio
    slice_count: int = 1
    volume_profile: tuple[float, ...] | None = None  # 量比曲线（volume_ratio 用）
    expected_slippage_bps: float = 0.0  # 预估滑点（回写配对用）


@dataclass(frozen=True)
class SorDecision:
    """SOR 决策（可回放）。"""

    replay_id: str
    broker_id: str
    score: float
    split_plan: Any  # 委托件产出（SplitPlan 或注入件同形态）
    estimated_cost_bps: float
    rationale: str
    decided_at: datetime


@dataclass(frozen=True)
class SlippageFeedback:
    """滑点实际 vs 预估回写记录。"""

    replay_id: str
    broker_id: str
    expected_bps: float
    actual_bps: float
    bias_bps: float  # actual - expected（正=实际劣于预估）


# 拆单算法映射（门禁降级口径对齐 MOD-EX-014：冰山→TWAP 等量少片；量比→VWAP 量能权重）
_SPLIT_ALGO_MAP: Final[dict[str, str]] = {
    "iceberg": "twap",
    "twap": "twap",
    "volume_ratio": "vwap",
}

# 禁 LLM 门控：注入回调模块路径段黑名单（Level 0 纯规则红线）
_FORBIDDEN_MODULE_SEGMENTS: Final[frozenset[str]] = frozenset({"llm", "intelligence"})


def _default_splitter(
    symbol: str,
    side: str,
    total_quantity: int,
    slice_count: int,
    algo: str,
    volume_profile: tuple[float, ...] | None,
) -> Any:
    """默认拆单委托：惰性调 zephyr.ex_core.order_splitter.split_order。"""
    from decimal import Decimal

    from zephyr.ex_core.order_splitter import SplitAlgo, SplitRequest, split_order
    from zephyr.shared.contracts.enums.order_enums import OrderSide

    request = SplitRequest(
        symbol=symbol,
        side=OrderSide(side),
        total_quantity=Decimal(total_quantity),
        slice_count=slice_count,
        volume_profile=(tuple(Decimal(str(w)) for w in volume_profile) if volume_profile else None),
    )
    return split_order(request, algo=SplitAlgo(algo))


def _assert_rule_only(name: str, fn: Callable | None) -> None:
    """禁 LLM 门控：注入回调模块路径含 llm/intelligence 段 → Fail-Closed。"""
    if fn is None:
        return
    module = getattr(fn, "__module__", "") or ""
    segments = {seg.lower() for seg in module.replace("/", ".").split(".")}
    if segments & _FORBIDDEN_MODULE_SEGMENTS:
        raise SorAgentError(f"Level 0 纯规则红线：{name} 来自禁域模块 {module}（禁 LLM 调用）")


class SorAgent:
    """路由Agent（SOR，MOD-XS-015）——Level 0 纯规则。

    用法：
        agent = SorAgent(splitter_fn=my_splitter, feedback_sink=my_sink)
        dec = agent.decide(request, candidates, now_utc)
        fb = agent.record_fill_feedback(dec.replay_id, actual_slippage_bps=8.5)
    """

    def __init__(
        self,
        weights: SorRouteWeights | None = None,
        min_liquidity: float = 0.3,
        splitter_fn: Callable[..., Any] | None = None,
        feedback_sink: Callable[[SlippageFeedback], Any] | None = None,
        replay_sink: Callable[[SorDecision], Any] | None = None,
    ) -> None:
        if not (0.0 <= min_liquidity <= 1.0):
            raise SorAgentError("min_liquidity 须落在 [0,1]")
        # 禁 LLM 门控（构造期断言，纯规则红线写入门控）
        _assert_rule_only("splitter_fn", splitter_fn)
        _assert_rule_only("feedback_sink", feedback_sink)
        _assert_rule_only("replay_sink", replay_sink)
        self._weights = weights if weights is not None else SorRouteWeights()
        self._min_liquidity = min_liquidity
        self._splitter = splitter_fn if splitter_fn is not None else _default_splitter
        self._feedback_sink = feedback_sink
        self._replay_sink = replay_sink
        self._seq = itertools.count(1)
        self._replay: list[SorDecision] = []
        self._decision_index: dict[str, tuple[str, float]] = {}  # replay_id → (broker_id, expected_bps)
        self._bias_samples: dict[str, list[float]] = {}  # broker_id → [bias_bps]

    # ── 技能①：智能路由（通道选择 + 流动性评估）──

    def _score(self, c: BrokerCandidate) -> float:
        """四维加权评分（确定性闭式；延迟/费用越低分越高）。"""
        latency_score = 1.0 / (1.0 + c.latency_ms / 100.0)
        cost_score = 1.0 / (1.0 + c.cost_bps / 10.0)
        w = self._weights
        return (
            w.w_latency * latency_score
            + w.w_fill_rate * c.fill_rate
            + w.w_cost * cost_score
            + w.w_liquidity * c.liquidity_score
        )

    # ── 决策（路由 + 拆单 + 回放）──

    def decide(
        self,
        request: SorRequest,
        candidates: list[BrokerCandidate] | tuple[BrokerCandidate, ...],
        now_utc: datetime | None = None,
    ) -> SorDecision:
        """智能路由 + 拆单 → 决策（可回放，无下单语义）。"""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)
        self._validate_request(request)
        if request.split_algo not in _SPLIT_ALGO_MAP:
            raise SorAgentError(f"未知拆单算法: {request.split_algo!r}（支持 {sorted(_SPLIT_ALGO_MAP)}）")
        # 流动性评估：低于门槛的通道先行剔除
        liquid = [c for c in candidates if c.liquidity_score >= self._min_liquidity]
        if not liquid:
            raise SorAgentError(f"无满足流动性门槛 {self._min_liquidity} 的通道候选（Fail-Closed）")
        scored = sorted(liquid, key=self._score, reverse=True)
        best = scored[0]
        best_score = self._score(best)
        # 拆单技能（委托，算法映射降级口径）
        try:
            split_plan = self._splitter(
                request.symbol,
                request.side,
                request.quantity,
                request.slice_count,
                _SPLIT_ALGO_MAP[request.split_algo],
                request.volume_profile,
            )
        except SorAgentError:
            raise
        except Exception as exc:  # noqa: BLE001 — 拆单委托失败统一包装 Fail-Closed
            raise SorAgentError(f"拆单委托失败: {exc}") from exc
        replay_id = f"SOR-{next(self._seq):06d}"
        estimated_cost = best.cost_bps + request.expected_slippage_bps
        rationale = (
            f"选中 {best.broker_id}：四维加权 {best_score:.4f}（候选 {len(candidates)}→"
            f"流动性过滤后 {len(liquid)}）；latency={best.latency_ms}ms "
            f"fill={best.fill_rate} cost={best.cost_bps}bps liq={best.liquidity_score}；"
            f"拆单 {request.split_algo}→{_SPLIT_ALGO_MAP[request.split_algo]}×{request.slice_count}"
        )
        decision = SorDecision(
            replay_id=replay_id,
            broker_id=best.broker_id,
            score=best_score,
            split_plan=split_plan,
            estimated_cost_bps=estimated_cost,
            rationale=rationale,
            decided_at=now_utc,
        )
        self._replay.append(decision)
        self._decision_index[replay_id] = (best.broker_id, request.expected_slippage_bps)
        if self._replay_sink is not None:
            try:
                self._replay_sink(decision)
            except Exception as exc:  # noqa: BLE001 — 回放外发失败不阻断判定
                _log.error("replay_sink 异常（已吞掉）: %s", exc)
        return decision

    @staticmethod
    def _validate_request(request: SorRequest) -> None:
        if not isinstance(request, SorRequest):
            raise SorAgentError("request 须为 SorRequest")
        if not request.symbol:
            raise SorAgentError("symbol 不能为空")
        if request.side not in ("BUY", "SELL"):
            raise SorAgentError(f"side 须为 BUY/SELL（实得 {request.side!r}）")
        if request.quantity <= 0:
            raise SorAgentError("quantity 须为正")
        if request.price <= 0:
            raise SorAgentError("price 须为正")
        if request.slice_count < 1:
            raise SorAgentError("slice_count 须 ≥ 1")

    # ── 滑点回写反馈循环 ──

    def record_fill_feedback(self, replay_id: str, actual_slippage_bps: float) -> SlippageFeedback:
        """成交回报 → 滑点实际 vs 预估配对 + per-broker 偏差校准统计。"""
        pair = self._decision_index.get(replay_id)
        if pair is None:
            raise SorAgentError(f"未知 replay_id: {replay_id}（Fail-Closed）")
        broker_id, expected = pair
        bias = float(actual_slippage_bps) - expected
        fb = SlippageFeedback(
            replay_id=replay_id,
            broker_id=broker_id,
            expected_bps=expected,
            actual_bps=float(actual_slippage_bps),
            bias_bps=bias,
        )
        self._bias_samples.setdefault(broker_id, []).append(bias)
        if self._feedback_sink is not None:
            try:
                self._feedback_sink(fb)
            except Exception as exc:  # noqa: BLE001 — 反馈外发失败不阻断闭环
                _log.error("feedback_sink 异常（已吞掉）: %s", exc)
        return fb

    def broker_bias(self, broker_id: str) -> float:
        """per-broker 滑点偏差均值（实际−预估；无样本=0.0）。"""
        samples = self._bias_samples.get(broker_id, [])
        return sum(samples) / len(samples) if samples else 0.0

    # ── 回放 ──

    def replay_log(self) -> tuple[SorDecision, ...]:
        """全部决策只读导出（replay_id 单调）。"""
        return tuple(self._replay)
