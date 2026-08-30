# [BLUEPRINT] MOD-MLS-003 | docs/03_modules/_domain_ml_serve/codegen_model_adapter/blueprint.md
# [MODULE] zephyr.ml_serve.codegen_model_adapter
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES] 无（适配核心纯内存；client/profile_registrar/budget_alert_sink/clock 全注入，不真发请求）
# [CONSUMERS] 运行时装配批（model_router DeepSeek-V4-Pro profile 装配 / 代码生成调用适配 / token 成本预算门禁）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 能力词表闭合(code_generation|code_repair|test_synthesis|refactor|code_explain); profile不可变且model_id唯一; 请求schema规范化(temperature=0.0/stream=False); client未注入Fail-Closed不真发; 响应token须非负且不越上下文窗; 成本按单价确定性累计; 预算预警/越限告警留痕且越限后调用Fail-Closed; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_ml_serve/codegen_model_adapter/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CodegenAdapterError(占位 ZA-MLS-UNREGISTERED-CODEGEN-ADAPTER)——未注册model/能力越词表/上下文窗越限/空请求字段/响应schema缺漏/预算耗尽/client异常时抛
# [TESTS] tests/ml_serve/test_codegen_model_adapter.py
# [A_module] module_id=MOD-MLS-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
CodegenModelAdapter — 代码生成模型适配器（MOD-MLS-003）。

B10-02296（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLS-003，A1 D-ML-46）：
model_router 注册 **DeepSeek-V4-Pro** 代码生成 profile（能力声明/上下文
窗/成本单价）+ **token 成本计量**（按 token 计费累计 + 预算告警）+
**调用适配**（请求/响应 schema 规范化，client 注入不真发）。

查重分工（蓝图 §0）：model_registry（MOD-INF-039）=LLM 模型静态注册表
（本件经 profile_registrar 挂钩装配，不重建注册表）；deep_review_model_
adapter（MOD-MLS-004）=GLM-5.1 深度审查适配（零交集，本件=代码生成）；
model_compression_accelerator（MOD-MLS-002）=压缩编排（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: client 参数
#   fields: 参数 client（无注解）
#   code: codegen_model_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: profile_registrar 参数
#   fields: 参数 profile_registrar（无注解）
#   code: codegen_model_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: budget_alert_sink 参数
#   fields: 参数 budget_alert_sink（无注解）
#   code: codegen_model_adapter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: budget_limit 参数
#   fields: 参数 budget_limit（无注解）
#   code: codegen_model_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CodegenModelAdapter
#   name_en: CodegenModelAdapter
#   intro: DeepSeek-V4-Pro 代码生成适配（profile 注册 + 成本计量 + schema 规范化）。
#   desc: DeepSeek-V4-Pro 代码生成适配（profile 注册 + 成本计量 + schema 规范化）。；公共方法（定义序）: register_profile, normalize_request, invok…
#   inputs: client profile_registrar budget_alert_sink budget_limit warn_ratio cl…
#   outputs: 返回值
#   （注：A1 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: CodegenModelAdapter
#   downstream: 运行时装配批（model_router DeepSeek-V4-Pro profile 装配 / 代码生成调用适配 / token 成本预算门禁）
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

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "BudgetAlert",
    "BudgetAlertKind",
    "CodegenAdapterError",
    "CodegenCapability",
    "CodegenModelAdapter",
    "CodegenProfile",
    "CodegenRequest",
    "CodegenResponse",
    "UsageRecord",
]

#: DeepSeek-V4-Pro 默认上下文窗（token，A1 D-ML-46 口径）
_DEFAULT_CONTEXT_WINDOW: Final[int] = 131072
#: 默认成本单价（元/1K token，占位口径，装配批可另行注册覆盖）
_DEFAULT_INPUT_PRICE: Final[float] = 0.002
_DEFAULT_OUTPUT_PRICE: Final[float] = 0.008
#: 预算预警默认触发比例（占 budget_limit）
_DEFAULT_WARN_RATIO: Final[float] = 0.8


class CodegenAdapterError(Exception):
    """代码生成适配输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLS-UNREGISTERED-CODEGEN-ADAPTER。
    """


class CodegenCapability(str, Enum):
    """代码生成能力词表（闭合）。"""

    CODE_GENERATION = "code_generation"
    CODE_REPAIR = "code_repair"
    TEST_SYNTHESIS = "test_synthesis"
    REFACTOR = "refactor"
    CODE_EXPLAIN = "code_explain"


class BudgetAlertKind(str, Enum):
    """预算告警类别。"""

    WARNING = "warning"
    EXCEEDED = "exceeded"


@dataclass(frozen=True)
class CodegenProfile:
    """代码生成模型 profile（能力声明/上下文窗/成本单价，frozen）。"""

    model_id: str
    provider: str
    capabilities: frozenset[CodegenCapability]
    context_window: int
    input_price_per_1k: float
    output_price_per_1k: float

    def __post_init__(self) -> None:
        if not self.model_id:
            raise CodegenAdapterError("model_id 为空")
        if not self.provider:
            raise CodegenAdapterError("provider 为空")
        if not self.capabilities:
            raise CodegenAdapterError("capabilities 为空（能力声明须非空）")
        for cap in self.capabilities:
            if not isinstance(cap, CodegenCapability):
                raise CodegenAdapterError(f"非法能力: {cap!r}")
        if isinstance(self.context_window, bool) or self.context_window <= 0:
            raise CodegenAdapterError("context_window 须为正整数")
        for name, price in (
            ("input_price_per_1k", self.input_price_per_1k),
            ("output_price_per_1k", self.output_price_per_1k),
        ):
            if not math.isfinite(price) or price < 0:
                raise CodegenAdapterError(f"{name} 须为非负有限值: {price!r}")


@dataclass(frozen=True)
class CodegenRequest:
    """规范化代码生成请求（frozen）。"""

    request_id: str
    model_id: str
    capability: CodegenCapability
    prompt: str
    max_tokens: int
    submitted_at: datetime.datetime


@dataclass(frozen=True)
class CodegenResponse:
    """规范化代码生成响应（frozen，cost 按 profile 单价确定性计算）。"""

    request_id: str
    model_id: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    finished_at: datetime.datetime


@dataclass(frozen=True)
class BudgetAlert:
    """预算告警载荷（budget_alert_sink 外发）。"""

    model_id: str
    kind: BudgetAlertKind
    total_cost: float
    budget_limit: float
    raised_at: datetime.datetime


@dataclass(frozen=True)
class UsageRecord:
    """单模型 token/成本累计视图（确定性）。"""

    model_id: str
    calls: int
    prompt_tokens: int
    completion_tokens: int
    total_cost: float


class CodegenModelAdapter:
    """DeepSeek-V4-Pro 代码生成适配（profile 注册 + 成本计量 + schema 规范化）。"""

    #: DeepSeek-V4-Pro 默认 profile（构造即注册；装配批可注册额外 profile）
    DEFAULT_PROFILE: Final[CodegenProfile] = CodegenProfile(
        model_id="deepseek-v4-pro",
        provider="deepseek",
        capabilities=frozenset(CodegenCapability),
        context_window=_DEFAULT_CONTEXT_WINDOW,
        input_price_per_1k=_DEFAULT_INPUT_PRICE,
        output_price_per_1k=_DEFAULT_OUTPUT_PRICE,
    )

    def __init__(
        self,
        *,
        client: Callable[[Mapping[str, object]], Mapping[str, object]] | None = None,
        profile_registrar: Callable[[CodegenProfile], None] | None = None,
        budget_alert_sink: Callable[[BudgetAlert], None] | None = None,
        budget_limit: float | None = None,
        warn_ratio: float = _DEFAULT_WARN_RATIO,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if budget_limit is not None and (not math.isfinite(budget_limit) or budget_limit <= 0):
            raise CodegenAdapterError("budget_limit 须为正有限值")
        if not math.isfinite(warn_ratio) or not 0.0 < warn_ratio <= 1.0:
            raise CodegenAdapterError("warn_ratio 须在 (0, 1] 区间")
        self._client = client
        self._registrar = profile_registrar
        self._alert_sink = budget_alert_sink
        self._budget_limit = budget_limit
        self._warn_ratio = warn_ratio
        self._clock = clock or datetime.datetime.now
        self._profiles: dict[str, CodegenProfile] = {}
        self._usage: dict[str, list[int]] = {}  # model_id -> [calls, prompt_tokens, completion_tokens]
        self._cost: dict[str, float] = {}
        self._warned: set[str] = set()
        self._exceeded_alarmed: set[str] = set()
        self.register_profile(self.DEFAULT_PROFILE)

    # ── profile 注册 ─────────────────────────────────────────────────────

    def register_profile(self, profile: CodegenProfile) -> None:
        """注册代码生成 profile（model_id 唯一；registrar 挂钩失败 Fail-Closed）。"""
        if not isinstance(profile, CodegenProfile):
            raise CodegenAdapterError("profile 非法（须 CodegenProfile）")
        if profile.model_id in self._profiles:
            raise CodegenAdapterError(f"profile 重复注册: {profile.model_id!r}")
        if self._registrar is not None:
            try:
                self._registrar(profile)
            except Exception as exc:  # noqa: BLE001 — model_router 挂钩失败 Fail-Closed
                raise CodegenAdapterError(f"profile_registrar 注册失败: {profile.model_id!r}") from exc
        self._profiles[profile.model_id] = profile
        self._usage[profile.model_id] = [0, 0, 0]
        self._cost[profile.model_id] = 0.0
        _log.info("代码生成 profile 注册: %s (%s)", profile.model_id, profile.provider)

    # ── 请求/响应 schema 规范化 ───────────────────────────────────────────

    def normalize_request(self, request: CodegenRequest) -> dict[str, object]:
        """请求 schema 规范化（校验 + 固定键 canonical dict）。"""
        if not isinstance(request, CodegenRequest):
            raise CodegenAdapterError("request 非法（须 CodegenRequest）")
        if not request.request_id:
            raise CodegenAdapterError("request_id 为空")
        profile = self.profile_of(request.model_id)
        if not isinstance(request.capability, CodegenCapability):
            raise CodegenAdapterError(f"非法能力: {request.capability!r}")
        if request.capability not in profile.capabilities:
            raise CodegenAdapterError(f"能力越界: {request.capability.value} 未在 {profile.model_id} 能力声明中")
        if not request.prompt:
            raise CodegenAdapterError("prompt 为空")
        if isinstance(request.max_tokens, bool) or not isinstance(request.max_tokens, int):
            raise CodegenAdapterError("max_tokens 须为整数")
        if request.max_tokens <= 0:
            raise CodegenAdapterError("max_tokens 须为正")
        if request.max_tokens > profile.context_window:
            raise CodegenAdapterError(f"max_tokens 越上下文窗: {request.max_tokens} > {profile.context_window}")
        return {
            "model": profile.model_id,
            "capability": request.capability.value,
            "prompt": request.prompt,
            "max_tokens": request.max_tokens,
            "temperature": 0.0,
            "stream": False,
        }

    def _normalize_response(self, request: CodegenRequest, profile: CodegenProfile, raw: object) -> CodegenResponse:
        """响应 schema 规范化（缺键/负 token/越窗 Fail-Closed）。"""
        if not isinstance(raw, Mapping):
            raise CodegenAdapterError("响应 schema 非法（须映射）")
        text = raw.get("text")
        if not isinstance(text, str):
            raise CodegenAdapterError("响应缺 text 或类型非法")
        prompt_tokens = raw.get("prompt_tokens")
        completion_tokens = raw.get("completion_tokens")
        for name, value in (
            ("prompt_tokens", prompt_tokens),
            ("completion_tokens", completion_tokens),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise CodegenAdapterError(f"响应 {name} 缺失或类型非法: {value!r}")
            if value < 0:
                raise CodegenAdapterError(f"响应 {name} 为负: {value}")
        if prompt_tokens + completion_tokens > profile.context_window:
            raise CodegenAdapterError(
                f"响应 token 越上下文窗: {prompt_tokens + completion_tokens} > {profile.context_window}"
            )
        cost = (
            prompt_tokens / 1000.0 * profile.input_price_per_1k
            + completion_tokens / 1000.0 * profile.output_price_per_1k
        )
        return CodegenResponse(
            request_id=request.request_id,
            model_id=profile.model_id,
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            finished_at=self._clock(),
        )

    # ── 调用适配（client 注入不真发） ─────────────────────────────────────

    def invoke(self, request: CodegenRequest) -> CodegenResponse:
        """调用适配：schema 校验 → 预算门禁 → client → 响应校验 → 成本计量。"""
        payload = self.normalize_request(request)
        profile = self.profile_of(request.model_id)
        if self._budget_limit is not None and self._cost[profile.model_id] >= self._budget_limit:
            raise CodegenAdapterError(
                f"预算耗尽: {profile.model_id!r} 累计成本 {self._cost[profile.model_id]} "
                f"≥ 预算 {self._budget_limit}（Fail-Closed 不真发）"
            )
        if self._client is None:
            raise CodegenAdapterError("client 未注入（Fail-Closed 不真发）")
        try:
            raw = self._client(payload)
        except Exception as exc:  # noqa: BLE001 — client 异常包装 Fail-Closed
            raise CodegenAdapterError(f"client 调用异常: {profile.model_id!r}") from exc
        response = self._normalize_response(request, profile, raw)
        self._settle(profile.model_id, response)
        return response

    def _settle(self, model_id: str, response: CodegenResponse) -> None:
        """成本计量累计 + 预算预警/越限告警（告警不阻断）。"""
        usage = self._usage[model_id]
        usage[0] += 1
        usage[1] += response.prompt_tokens
        usage[2] += response.completion_tokens
        prev = self._cost[model_id]
        total = prev + response.cost
        self._cost[model_id] = total
        if self._budget_limit is None:
            return
        if model_id not in self._warned and prev < self._warn_ratio * self._budget_limit <= total:
            self._warned.add(model_id)
            self._alert(model_id, BudgetAlertKind.WARNING, total)
        if model_id not in self._exceeded_alarmed and prev < self._budget_limit <= total:
            self._exceeded_alarmed.add(model_id)
            self._alert(model_id, BudgetAlertKind.EXCEEDED, total)

    def _alert(self, model_id: str, kind: BudgetAlertKind, total: float) -> None:
        alert = BudgetAlert(
            model_id=model_id,
            kind=kind,
            total_cost=total,
            budget_limit=self._budget_limit,
            raised_at=self._clock(),
        )
        _log.warning(
            "代码生成预算告警: %s %s 累计 %s / 预算 %s",
            model_id,
            kind.value,
            total,
            self._budget_limit,
        )
        if self._alert_sink is not None:
            try:
                self._alert_sink(alert)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("budget_alert_sink 告警失败")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def profile_of(self, model_id: str) -> CodegenProfile:
        """单模型 profile（未注册 → Fail-Closed）。"""
        profile = self._profiles.get(model_id)
        if profile is None:
            raise CodegenAdapterError(f"未注册 model: {model_id!r}")
        return profile

    def usage_of(self, model_id: str) -> UsageRecord:
        """token/成本累计视图（未注册 → Fail-Closed）。"""
        if model_id not in self._profiles:
            raise CodegenAdapterError(f"未注册 model: {model_id!r}")
        calls, prompt_tokens, completion_tokens = self._usage[model_id]
        return UsageRecord(
            model_id=model_id,
            calls=calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost=self._cost[model_id],
        )

    def registered_models(self) -> tuple[str, ...]:
        """已注册模型视图（确定性排序）。"""
        return tuple(sorted(self._profiles))
