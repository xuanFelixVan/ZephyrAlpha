# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l5_resource_protection
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l5_resource_protection
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 永不可降级项 L1A/L3B/L4/L5成本熔断 MUST 不出现在任何降级计划
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: l5_resource_protection.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: max_tokens 参数
#   fields: 参数 max_tokens（无注解）
#   code: l5_resource_protection.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_cost_cents 参数
#   fields: 参数 max_cost_cents（无注解）
#   code: l5_resource_protection.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: rate_max 参数
#   fields: 参数 rate_max（无注解）
#   code: l5_resource_protection.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ResourceProtectionLayer
#   name_en: ResourceProtectionLayer
#   intro: L5 资源保护层：token/cost/rate 限额 + 成本不对称检测。
#   desc: L5 资源保护层：token/cost/rate 限额 + 成本不对称检测。；公共方法（定义序）: check_token_budget, check_rate_limit, check_cost_budget, ev…
#   inputs: config max_tokens max_cost_cents rate_max rate_window_seconds
#   outputs: 返回值
# - id: A2
#   name_zh: ② AIRecursionGuard
#   name_en: AIRecursionGuard
#   intro: 防止 AI 递归攻击的递归深度守卫。
#   desc: 防止 AI 递归攻击的递归深度守卫。；公共方法（定义序）: current_depth, enter, reset, check_recursion；源码 L211-L234
#   inputs: config max_recursion_depth
#   outputs: 返回值
# - id: A3
#   name_zh: ③ AgentExecutionProtector
#   name_en: AgentExecutionProtector
#   intro: 保护 agent 执行免受资源滥用。
#   desc: 保护 agent 执行免受资源滥用。；公共方法（定义序）: record_step, check_execution_limits；源码 L237-L252
#   inputs: config max_steps
#   outputs: 返回值
# - id: A4
#   name_zh: ④ LLMCostCircuitBreaker
#   name_en: LLMCostCircuitBreaker
#   intro: LLM 成本断路器。
#   desc: LLM 成本断路器。；公共方法（定义序）: state, record_failure, allow_request, reset, trip, check；源码 L263-L304
#   inputs: config failure_threshold recovery_timeout_seconds
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ CostAsymmetryDefender
#   name_en: CostAsymmetryDefender
#   intro: 检测成本不对称攻击（少量输入榨取大量情报）。
#   desc: 检测成本不对称攻击（少量输入榨取大量情报）。；公共方法（定义序）: scan, detect_asymmetry, calculate_cost_ratio；源码 L307-L339
#   inputs: config
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ LSGPerformanceBudget
#   name_en: LSGPerformanceBudget
#   intro: LSG 性能预算追踪器（分位数统计 + SLO 判定）。
#   desc: LSG 性能预算追踪器（分位数统计 + SLO 判定）。；公共方法（定义序）: record, stats, check_budget；源码 L399-L430
#   inputs: max_tokens max_time_ms
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ DegradationPlan
#   name_en: DegradationPlan
#   intro: 降级计划（蓝图 §40.4 enact_degradation 产物）。
#   desc: 降级计划（蓝图 §40.4 enact_degradation 产物）。；公共方法（定义序）: degraded_layers；源码 L452-L461
#   inputs: 无参数
#   outputs: 返回值
# - id: A8
#   name_zh: ⑧ LSGPerformanceGuard
#   name_en: LSGPerformanceGuard
#   intro: LSG 性能预算管理（蓝图 §40.4）——安全不能以不可接受的延迟为代价。
#   desc: LSG 性能预算管理（蓝图 §40.4）——安全不能以不可接受的延迟为代价。 - track_latency：每层延迟埋点（滚动窗口，有界）。 - check_budget：聚合…；公共方法（定义序）: track_l…
#   inputs: p95_budget_ms p99_budget_ms approaching_ratio min_samples window_size
#   outputs: 返回值
# - id: A9
#   name_zh: ⑨ ModelExtractionDefender
#   name_en: ModelExtractionDefender
#   intro: 检测模型提取攻击（高熵查询模式）。
#   desc: 检测模型提取攻击（高熵查询模式）。；公共方法（定义序）: entropy_check, detect_extraction, check_query_similarity；源码 L570-L597
#   inputs: config entropy_threshold
#   outputs: 返回值
# - id: A10
#   name_zh: ⑩ SemanticCacheCollisionDefender
#   name_en: SemanticCacheCollisionDefender
#   intro: 检测语义缓存碰撞攻击（HMAC 签名验证）。
#   desc: 检测语义缓存碰撞攻击（HMAC 签名验证）。；公共方法（定义序）: salt_key, sign_value, verify_integrity, detect_collision, validate_cache_en…
#   inputs: config salt
#   outputs: 返回值
#   （注：A10 之后另有 5 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（15 定义）
#   name_en: public defs
#   intro: ResourceProtectionLayer, AIRecursionGuard, AgentExecutionProtector, LLMCostCirc…
#   downstream: zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l5_re…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

import hashlib
import hmac
import math
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final


class ResourceProtectionLayer:
    """L5 资源保护层：token/cost/rate 限额 + 成本不对称检测。"""

    def __init__(
        self,
        config=None,
        max_tokens: int = 100000,
        max_cost_cents: float = 500.0,
        rate_max: int = 100,
        rate_window_seconds: int = 60,
    ):
        self.config = config or {}
        self._max_tokens = max_tokens
        self._max_cost_cents = max_cost_cents
        self._token_usage: dict[str, int] = defaultdict(int)
        self._cost_usage: dict[str, float] = defaultdict(float)
        self._rate_limiter = SlidingWindowRateLimiter(max_requests=rate_max, window_seconds=rate_window_seconds)
        self._cost_asymmetry = CostAsymmetryDefender()

    def check_token_budget(self, session_id: str, tokens: int) -> tuple[bool, str]:
        if self._token_usage[session_id] + tokens > self._max_tokens:
            return False, f"token budget exhausted for {session_id}"
        self._token_usage[session_id] += tokens
        return True, "ok"

    def check_rate_limit(self, key: str) -> tuple[bool, str]:
        if self._rate_limiter.allow(key):
            return True, "ok"
        return False, "rate limit exceeded"

    def check_cost_budget(self, session_id: str, cost_cents: float) -> tuple[bool, str]:
        if self._cost_usage[session_id] + cost_cents > self._max_cost_cents:
            return False, "cost budget exhausted"
        self._cost_usage[session_id] += cost_cents
        return True, "ok"

    async def evaluate(self, ctx: object) -> object:
        """评估资源保护：检测成本不对称攻击。"""
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        raw = getattr(ctx, "raw_input", "") or ""
        result = self._cost_asymmetry.scan(raw)
        if result.get("blocked"):
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason="cost asymmetry attack detected",
                layer_name="l5_resource_protection",
                score=0.0,
                details=result,
            )
        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="resource budget ok",
            layer_name="l5_resource_protection",
            score=1.0,
        )


class ResourceGuard:
    def __init__(self, resource_id="", quota=0, current_usage=0):
        self.resource_id = resource_id
        self.quota = quota
        self.current_usage = current_usage


class AIRecursionGuard:
    """防止 AI 递归攻击的递归深度守卫。"""

    def __init__(self, config: dict[str, Any] | None = None, max_recursion_depth: int = 10):
        self.config = config or {}
        self._max_depth = max_recursion_depth
        self._stack: list[str] = []

    @property
    def current_depth(self) -> int:
        return len(self._stack)

    def enter(self, agent_id: str) -> bool:
        if len(self._stack) >= self._max_depth:
            return False
        self._stack.append(agent_id)
        return True

    def reset(self) -> None:
        self._stack.clear()

    # 兼容旧接口
    def check_recursion(self, call_stack: list[Any]) -> bool:
        return len(call_stack) < self._max_depth


class AgentExecutionProtector:
    """保护 agent 执行免受资源滥用。"""

    def __init__(self, config: dict[str, Any] | None = None, max_steps: int = 100):
        self.config = config or {}
        self._max_steps = max_steps
        self._steps = 0

    def record_step(self) -> dict[str, Any]:
        self._steps += 1
        exceeded = self._steps > self._max_steps
        return {"allowed": not exceeded, "steps_exceeded": exceeded, "steps": self._steps}

    # 兼容旧接口
    def check_execution_limits(self, agent_id: str) -> bool:
        return self._steps <= self._max_steps


class CircuitState(Enum):
    """断路器状态。"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class LLMCostCircuitBreaker:
    """LLM 成本断路器。"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
    ):
        self.config = config or {}
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout_seconds
        self._failures = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float = 0.0

    @property
    def state(self) -> CircuitState:
        if self._state is CircuitState.OPEN:
            if time.time() - self._opened_at > self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.time()

    def allow_request(self) -> bool:
        return self.state is not CircuitState.OPEN

    def reset(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED

    def trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.time()

    def check(self) -> CircuitState:
        return self.state


class CostAsymmetryDefender:
    """检测成本不对称攻击（少量输入榨取大量情报）。"""

    _FREE_INTELLIGENCE_PATTERNS = [
        "analyze this codebase",
        "review all files",
        "audit the entire",
        "review all",
        "analyze the entire",
        "enumerate all",
        "list every",
    ]

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def scan(self, text: str) -> dict[str, Any]:
        lowered = (text or "").lower()
        flagged = any(p in lowered for p in self._FREE_INTELLIGENCE_PATTERNS)
        return {
            "blocked": flagged,
            "free_intelligence_flagged": flagged,
            "reason": "free intelligence extraction" if flagged else "ok",
        }

    # 兼容旧接口
    def detect_asymmetry(self, request: object, response: object) -> bool:
        return self.scan(str(request))["blocked"]

    def calculate_cost_ratio(self, input_tokens: int, output_tokens: int) -> float:
        if input_tokens == 0:
            return float(output_tokens)
        return output_tokens / input_tokens


class _L5CostBudget:
    """内部成本预算追踪器。"""

    def __init__(
        self,
        max_cost: float = 100.0,
        current_cost: float = 0.0,
        *,
        session_id: str = "",
        max_cost_cents: float | None = None,
        current_cost_cents: float | None = None,
    ):
        self.session_id = session_id
        self.max_cost_cents = max_cost_cents if max_cost_cents is not None else max_cost
        self.current_cost_cents = current_cost_cents if current_cost_cents is not None else current_cost

    def exhausted(self) -> bool:
        return self.current_cost_cents >= self.max_cost_cents

    def remaining_cost_cents(self) -> float:
        return max(0.0, self.max_cost_cents - self.current_cost_cents)

    def can_spend(self, amount: float) -> bool:
        return self.current_cost_cents + amount <= self.max_cost_cents

    def spend(self, amount: float) -> None:
        self.current_cost_cents += amount


class _L5TokenBudget:
    """内部 token 预算追踪器。"""

    def __init__(
        self,
        max_tokens: int = 100000,
        current_tokens: int = 0,
        *,
        session_id: str = "",
        current_usage: int | None = None,
    ):
        self.session_id = session_id
        self.max_tokens = max_tokens
        self.current_usage = current_usage if current_usage is not None else current_tokens

    def exhausted(self) -> bool:
        return self.current_usage >= self.max_tokens

    def remaining(self) -> int:
        return max(0, self.max_tokens - self.current_usage)

    def can_consume(self, tokens: int) -> bool:
        return self.current_usage + tokens <= self.max_tokens

    def consume(self, tokens: int) -> None:
        self.current_usage += tokens


class LSGPerformanceBudget:
    """LSG 性能预算追踪器（分位数统计 + SLO 判定）。"""

    def __init__(self, max_tokens: int = 4096, max_time_ms: int = 30000):
        self.max_tokens = max_tokens
        self.max_time_ms = max_time_ms
        self._records: dict[str, list[float]] = defaultdict(list)

    def record(self, layer: str, latency_ms: float) -> None:
        self._records[layer].append(latency_ms)

    def stats(self, layer: str) -> dict[str, Any]:
        recs = self._records.get(layer, [])
        if not recs:
            return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "meets_slo": True}
        srt = sorted(recs)

        def _pct(p: float) -> float:
            idx = min(len(srt) - 1, max(0, int(len(srt) * p)))
            return srt[idx]

        p50, p95, p99 = _pct(0.50), _pct(0.95), _pct(0.99)
        return {
            "count": len(recs),
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "meets_slo": p95 < 50.0 and p99 < 100.0,
        }

    def check_budget(self, tokens_used: int, elapsed_ms: int) -> bool:
        return tokens_used <= self.max_tokens and elapsed_ms <= self.max_time_ms


class BudgetStatus(str, Enum):
    """性能预算状态（蓝图 §40.4）。"""

    WITHIN_BUDGET = "within_budget"
    APPROACHING = "approaching"
    EXCEEDED = "exceeded"


@dataclass(frozen=True)
class DegradationStep:
    """单步降级动作：某防御子层从 from_mode 降到 to_mode。"""

    layer: str
    from_mode: str
    to_mode: str
    reason: str = "latency budget exceeded"


@dataclass(frozen=True)
class DegradationPlan:
    """降级计划（蓝图 §40.4 enact_degradation 产物）。"""

    status: BudgetStatus
    steps: tuple[DegradationStep, ...] = ()
    alert: bool = False

    @property
    def degraded_layers(self) -> tuple[str, ...]:
        return tuple(step.layer for step in self.steps)


class LSGPerformanceGuard:
    """LSG 性能预算管理（蓝图 §40.4）——安全不能以不可接受的延迟为代价。

    - track_latency：每层延迟埋点（滚动窗口，有界）。
    - check_budget：聚合延迟分位数判定 WITHIN/APPROACHING/EXCEEDED。
    - enact_degradation：EXCEEDED 时按 §40.4 既定顺序产出降级计划；
      永不可降级项（L1A/L3B/L4/L5 成本熔断）绝不进入计划（不变量，
      构造期校验 + is_degradable 查询）。
    """

    # §40.4 降级顺序（按安全影响从小到大）——唯一合法降级清单
    DEGRADATION_ORDER: Final[tuple[tuple[str, str, str], ...]] = (
        ("L1C", "越狱LLM辅助检测", "纯pattern match"),
        ("L3D", "幻觉LLM辅助检测", "纯启发式"),
        ("L6", "详细审计日志", "摘要日志"),
        ("L8", "Agent间行为分析", "纯身份验证"),
        ("L7", "实时验证", "定期批量验证"),
    )
    # §40.4 永不可降级（必须保留）：L1A 核心注入检测 / L3B 沙箱执行 /
    # L4 工具调用权限检查 / L5 成本熔断
    NEVER_DEGRADABLE: Final[frozenset[str]] = frozenset({"L1A", "L3B", "L4", "L5_COST_BREAKER"})

    def __init__(
        self,
        p95_budget_ms: float = 50.0,
        p99_budget_ms: float = 100.0,
        *,
        approaching_ratio: float = 0.8,
        min_samples: int = 5,
        window_size: int = 1000,
    ) -> None:
        if any(layer in self.NEVER_DEGRADABLE for layer, _, _ in self.DEGRADATION_ORDER):
            raise ValueError("DEGRADATION_ORDER 含永不可降级层——违反蓝图 §40.4 不变量")
        self._p95_budget = p95_budget_ms
        self._p99_budget = p99_budget_ms
        self._approaching_ratio = approaching_ratio
        self._min_samples = max(1, min_samples)
        self._records: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=window_size))

    def track_latency(self, layer: str, latency_ms: float) -> None:
        """记录每个防御层的延迟消耗。"""
        self._records[layer].append(float(latency_ms))

    def _all_latencies(self) -> list[float]:
        return [v for recs in self._records.values() for v in recs]

    @staticmethod
    def _percentile(sorted_vals: list[float], p: float) -> float:
        idx = min(len(sorted_vals) - 1, max(0, int(len(sorted_vals) * p)))
        return sorted_vals[idx]

    def check_budget(self) -> BudgetStatus:
        """检查当前延迟是否超出预算。

        WITHIN_BUDGET → 正常运行；APPROACHING → 记录告警，准备降级；
        EXCEEDED → 触发降级策略。样本不足一律 WITHIN_BUDGET（不误降）。
        """
        vals = sorted(self._all_latencies())
        if len(vals) < self._min_samples:
            return BudgetStatus.WITHIN_BUDGET
        p95 = self._percentile(vals, 0.95)
        p99 = self._percentile(vals, 0.99)
        if p95 >= self._p95_budget or p99 >= self._p99_budget:
            return BudgetStatus.EXCEEDED
        if p95 >= self._p95_budget * self._approaching_ratio or p99 >= self._p99_budget * self._approaching_ratio:
            return BudgetStatus.APPROACHING
        return BudgetStatus.WITHIN_BUDGET

    def enact_degradation(self, status: BudgetStatus) -> DegradationPlan:
        """延迟超预算时的自动安全降级策略（§40.4 既定顺序）。

        EXCEEDED → 全量五步降级计划；APPROACHING → 空计划 + 告警；
        WITHIN_BUDGET → 空计划。永不可降级项绝不出现于计划。
        """
        if status is BudgetStatus.EXCEEDED:
            steps = tuple(
                DegradationStep(layer=layer, from_mode=from_mode, to_mode=to_mode)
                for layer, from_mode, to_mode in self.DEGRADATION_ORDER
            )
            plan = DegradationPlan(status=status, steps=steps, alert=True)
        elif status is BudgetStatus.APPROACHING:
            plan = DegradationPlan(status=status, steps=(), alert=True)
        else:
            plan = DegradationPlan(status=status, steps=(), alert=False)
        assert not (set(plan.degraded_layers) & self.NEVER_DEGRADABLE), "不变量：永不可降级项进入降级计划"
        return plan

    @classmethod
    def is_degradable(cls, layer: str) -> bool:
        """查询某层是否可降级——永不可降级项恒 False。"""
        return layer not in cls.NEVER_DEGRADABLE

    def stats(self) -> dict[str, Any]:
        """分位数快照（观测用）。"""
        vals = sorted(self._all_latencies())
        if not vals:
            return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "status": BudgetStatus.WITHIN_BUDGET.value}
        return {
            "count": len(vals),
            "p50": self._percentile(vals, 0.50),
            "p95": self._percentile(vals, 0.95),
            "p99": self._percentile(vals, 0.99),
            "status": self.check_budget().value,
        }


class ModelExtractionDefender:
    """检测模型提取攻击（高熵查询模式）。"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        entropy_threshold: float = 4.5,
    ):
        self.config = config or {}
        self._threshold = entropy_threshold

    def entropy_check(self, text: str) -> dict[str, Any]:
        if not text:
            return {"suspicious": False, "entropy": 0.0}
        counts = Counter(text)
        length = len(text)
        entropy = -sum((c / length) * math.log2(c / length) for c in counts.values())
        return {"suspicious": entropy > self._threshold, "entropy": round(entropy, 4)}

    # 兼容旧接口
    def detect_extraction(self, query_pattern: list[Any]) -> bool:
        joined = "".join(str(q) for q in query_pattern)
        return self.entropy_check(joined)["suspicious"]

    def check_query_similarity(self, queries: list[str]) -> float:
        if len(queries) < 2:
            return 0.0
        return 1.0 - _jaccard(set(queries[0].split()), set(queries[-1].split()))


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(len(a | b), 1)


class SemanticCacheCollisionDefender:
    """检测语义缓存碰撞攻击（HMAC 签名验证）。"""

    def __init__(self, config: dict[str, Any] | None = None, salt: str = "l5-cache-salt"):
        self.config = config or {}
        self._salt = salt

    def salt_key(self, key: str) -> str:
        return hmac.new(self._salt.encode(), key.encode(), hashlib.sha256).hexdigest()

    def sign_value(self, salted_key: str, value: str) -> str:
        return f"{value}::sig={hmac.new(salted_key.encode(), value.encode(), hashlib.sha256).hexdigest()}"

    def verify_integrity(self, salted_key: str, signed_value: str) -> tuple[bool, str]:
        if "::sig=" not in signed_value:
            return False, ""
        value, _, sig = signed_value.partition("::sig=")
        expected = hmac.new(salted_key.encode(), value.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected), value

    # 兼容旧接口
    def detect_collision(self, cache_key: str, cached_value: object, new_value: object) -> bool:
        return cached_value != new_value

    def validate_cache_entry(self, key: str, value: object) -> bool:
        return True


class SlidingWindowRateLimiter:
    """滑动窗口限流器（per-key 计数）。"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str = "default") -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        bucket = [t for t in self._buckets[key] if t >= cutoff]
        self._buckets[key] = bucket
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True

    def current_count(self, key: str = "default") -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        return sum(1 for t in self._buckets[key] if t >= cutoff)

    # 兼容旧接口
    def allow_request(self) -> bool:
        return self.allow("default")

    def record_request(self, timestamp: float) -> None:
        self._buckets["default"].append(timestamp)
