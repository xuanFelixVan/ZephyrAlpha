# [BLUEPRINT] MOD-FACTORY-001 | docs/03_modules/_domain_autonomy_core/knowledge_classifier/blueprint.md | §
# [MODULE] zephyr.autonomy_core.module_factory.knowledge_classifier
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.llm_runtime_gateway（仅消费既有 infer 签名，不改其源文件）；pydantic v2（输出 schema 强校验）
# [CONSUMERS] 模块工厂流水线人工编排（Phase 1 手动触发；module_mapper 消费其 ClassificationResult）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 产出=建议草稿，100% human_gated；不直写注册表 YAML；LLM 输出 schema 校验失败即 fail-closed；受控词表外分类一律拒绝；tags 只归并不静默造词（新词进 tags_pending_registration）
# [MODIFY-GUARD] 变更须同步 13号文 §3.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 构造期配置非法（空词表/权重非正/阈值越界）-> KnowledgeClassifierError；LLM 网关 status!=ok / JSON 解析失败 / schema 校验失败 -> ClassificationResult(verdict="error") 不抛（fail-closed 不产半成品分类）
# [TESTS] tests/autonomy/test_knowledge_classifier.py
# [A_module] module_id=MOD-FACTORY-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""knowledge_classifier — MOD-FACTORY-001 知识分类器（13号文 §3.2，Phase 1）
========================================================================================

模块工厂六环节之"知识分类"：把采集到的知识片段分类到已定稿的注册表受控词表，
并产出 v2.0 多维适用性标注草稿。产出物 100% 为建议草稿（human_gated），
不写任何注册表 YAML。

职责
----
1. 信息价值四维评分门禁（13号文 §3.1）：相关性/时效性/信息量/可靠性，
   综合（加权平均）< 0.3 -> verdict="rejected"，不进入分类。
2. 主分类（§3.2）：factor 10 类 / strategy 6 类 / 其他分流
   （risk_rule/execution_algo/data_asset/technical_indicator/tool/knowledge_only）。
3. v2.0 多维标注输出：primary_timeframe/applicable_timeframes/regime_valid/
   regime_invalid/direction/entry_role/applies_to/tags。
4. 标签归并纪律：tags 先归并既有 v2.0 词表（同义词映射），词表外新词标记
   待登记（tags_pending_registration），不静默造词。

LLM 调用纪律（#ARCH-286 裁定）
------------------------------
LLM 调用必经 MOD-INF-051 llm_runtime_gateway 的既有 ``infer(task_type, prompt, ...)``
签名；网关经构造注入（LLMInferProtocol），测试注入 fake，禁真 LLM/禁网络。
缺省懒构造真实网关（仅在未注入且真实调用时）。

fail-closed 纪律
----------------
LLM 返回 status!=ok / JSON 不可解析 / pydantic schema 校验不过（含词表外枚举、
factor/strategy 交叉字段矛盾）-> verdict="error"，不产出任何分类字段。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from zephyr.integration.llm_runtime_gateway import LLMRuntimeGateway

__all__: Final = [
    "CLASSIFIER_TASK_TYPE",
    "DEFAULT_QUALITY_GATE",
    "DEFAULT_TAG_SYNONYMS",
    "DEFAULT_TAG_VOCAB",
    "FACTOR_CLASSES",
    "STRATEGY_CLASSES",
    "ClassificationPayload",
    "ClassificationResult",
    "KnowledgeClassifier",
    "KnowledgeClassifierError",
    "KnowledgeItem",
    "LLMInferProtocol",
    "QualityGateConfig",
    "QualityScores",
]

_log = logging.getLogger(__name__)

CLASSIFIER_TASK_TYPE: Final[str] = "module_factory_classify"

# ── 受控词表（62号文 S2/S3 裁定 + catalogs 落盘 registry 头部注释为真源，本模块为运行时镜像）──
FACTOR_CLASSES: Final[tuple[str, ...]] = (
    "value", "quality", "momentum", "volatility", "size",
    "liquidity", "event", "intraday", "technical", "sentiment",
)
STRATEGY_CLASSES: Final[tuple[str, ...]] = (
    "daban", "multifactor", "event_driven", "value_reversal",
    "momentum_trend", "sector_rotation",
)
OTHER_SUBTYPES: Final[tuple[str, ...]] = (
    "risk_rule", "execution_algo", "data_asset",
    "technical_indicator", "tool", "knowledge_only",
)
TIMEFRAMES: Final[tuple[str, ...]] = (
    "1min", "5min", "15min", "30min", "60min", "120min",
    "daily", "weekly", "monthly",
)
REGIMES: Final[tuple[str, ...]] = (
    "trend_up", "trend_down", "ranging", "panic", "euphoria", "high_vol", "low_vol",
)
DIRECTIONS: Final[tuple[str, ...]] = ("long", "short", "both", "neutral")
ENTRY_ROLES: Final[tuple[str, ...]] = (
    "trigger", "state", "filter", "ranking", "rule", "reference",
)
APPLIES_TO: Final[tuple[str, ...]] = (
    "stock", "etf", "index", "futures", "sector", "market",
)

# v2.0 标签词表运行时镜像（真源=factor_registry.yaml/strategy_registry.yaml 头部注释，
# 两库并集；变更以注册表为准，本镜像随 13号文 §3.2 同步维护）
DEFAULT_TAG_VOCAB: Final[frozenset[str]] = frozenset(
    {
        # 两库共有
        "k线", "事件", "仓位", "信号", "出货", "分时", "动量", "压力", "反转", "吸筹",
        "周期", "因子", "均值回归", "均线", "基准", "宏观", "尾盘", "形态", "成交", "成本",
        "打板", "执行", "持续", "指数", "支撑", "放量", "数据", "早盘", "止损", "波动",
        "流动性", "盘口", "突破", "组合", "绩效", "缠论", "缩量", "缺口", "股票池", "背离",
        "行业", "规则", "订单", "财报", "质量", "资金", "趋势", "量价", "量化", "震荡",
        "风控", "龙头",
        # factor_registry 独有
        "利率", "回撤", "威科夫", "情绪", "指标", "散户", "斐波那契", "期货", "杠杆",
        "超买", "超跌", "隔夜", "集中度", "高频", "龙虎榜",
        # strategy_registry 独有
        "估值", "多因子", "成长", "行情",
    }
)

# 同义词归并映射（注册表头部注释：翻转→反转、破位/跌破→突破、阻力→压力、
# 派发→出货、横盘/盘整→震荡、超买超卖→均值回归族）
DEFAULT_TAG_SYNONYMS: Final[dict[str, str]] = {
    "翻转": "反转",
    "破位": "突破",
    "跌破": "突破",
    "阻力": "压力",
    "派发": "出货",
    "横盘": "震荡",
    "盘整": "震荡",
    "超买超卖": "均值回归",
}


class KnowledgeClassifierError(Exception):
    """构造期配置非法（占位 ZA-FACTORY-UNREGISTERED-001）。"""


# ── LLM 网关注入协议（MOD-INF-051 既有 infer 签名，只消费不修改）──
@runtime_checkable
class LLMInferProtocol(Protocol):
    """LLM 推理门面注入契约——对齐 llm_runtime_gateway.LLMRuntimeGateway.infer 签名。

    返回对象 duck-type 要求：``.status``（"ok"/"error"/"blocked"）与 ``.text``。
    测试注入 fake，禁真 LLM。
    """

    def infer(
        self,
        task_type: str,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        channel: str | None = None,
        critical: bool = False,
        **kw: Any,
    ) -> Any: ...


# ── LLM 输出 schema（pydantic v2 严格校验，extra=forbid）──
class QualityScores(BaseModel):
    """信息价值四维评分（13号文 §3.1）：各维 0~1。"""

    model_config = ConfigDict(extra="forbid")

    relevance: float = Field(ge=0.0, le=1.0)
    timeliness: float = Field(ge=0.0, le=1.0)
    information: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(ge=0.0, le=1.0)


class ClassificationPayload(BaseModel):
    """LLM 分类输出受控 schema——词表外枚举/交叉字段矛盾一律 ValidationError。"""

    model_config = ConfigDict(extra="forbid")

    quality: QualityScores
    target_kind: Literal["factor", "strategy", "other"]
    factor_class: Literal[
        "value", "quality", "momentum", "volatility", "size",
        "liquidity", "event", "intraday", "technical", "sentiment",
    ] | None = None
    strategy_class: Literal[
        "daban", "multifactor", "event_driven", "value_reversal",
        "momentum_trend", "sector_rotation",
    ] | None = None
    other_subtype: Literal[
        "risk_rule", "execution_algo", "data_asset",
        "technical_indicator", "tool", "knowledge_only",
    ] | None = None
    primary_timeframe: Literal[
        "1min", "5min", "15min", "30min", "60min", "120min",
        "daily", "weekly", "monthly",
    ] | None = None
    applicable_timeframes: list[
        Literal[
            "1min", "5min", "15min", "30min", "60min", "120min",
            "daily", "weekly", "monthly",
        ]
    ] = Field(default_factory=list)
    regime_valid: list[
        Literal[
            "trend_up", "trend_down", "ranging", "panic",
            "euphoria", "high_vol", "low_vol",
        ]
    ] = Field(default_factory=list)
    regime_invalid: list[
        Literal[
            "trend_up", "trend_down", "ranging", "panic",
            "euphoria", "high_vol", "low_vol",
        ]
    ] = Field(default_factory=list)
    direction: Literal["long", "short", "both", "neutral"] = "neutral"
    entry_role: Literal[
        "trigger", "state", "filter", "ranking", "rule", "reference",
    ] = "ranking"
    applies_to: list[
        Literal["stock", "etf", "index", "futures", "sector", "market"]
    ] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    rationale: str = ""

    @model_validator(mode="after")
    def _cross_field_discipline(self) -> ClassificationPayload:
        if self.target_kind == "factor":
            if self.factor_class is None:
                raise ValueError("target_kind=factor 时 factor_class MUST 非空")
            if self.strategy_class is not None or self.other_subtype is not None:
                raise ValueError("target_kind=factor 时 strategy_class/other_subtype MUST 为空")
        elif self.target_kind == "strategy":
            if self.strategy_class is None:
                raise ValueError("target_kind=strategy 时 strategy_class MUST 非空")
            if self.factor_class is not None or self.other_subtype is not None:
                raise ValueError("target_kind=strategy 时 factor_class/other_subtype MUST 为空")
        else:  # other
            if self.other_subtype is None:
                raise ValueError("target_kind=other 时 other_subtype MUST 非空")
            if self.factor_class is not None or self.strategy_class is not None:
                raise ValueError("target_kind=other 时 factor_class/strategy_class MUST 为空")
        if self.primary_timeframe is not None and self.applicable_timeframes:
            if self.primary_timeframe not in self.applicable_timeframes:
                raise ValueError("primary_timeframe 必须含于 applicable_timeframes（或 applicable_timeframes 为空）")
        overlap = set(self.regime_valid) & set(self.regime_invalid)
        if overlap:
            raise ValueError(f"regime_valid 与 regime_invalid 交集非空: {sorted(overlap)}")
        return self


@dataclass(frozen=True)
class QualityGateConfig:
    """信息价值门禁配置：综合分=加权平均，< threshold -> REJECT（13号文 §3.1，默认 0.3）。"""

    threshold: float = 0.3
    weight_relevance: float = 0.25
    weight_timeliness: float = 0.25
    weight_information: float = 0.25
    weight_reliability: float = 0.25

    def composite(self, scores: QualityScores) -> float:
        return (
            self.weight_relevance * scores.relevance
            + self.weight_timeliness * scores.timeliness
            + self.weight_information * scores.information
            + self.weight_reliability * scores.reliability
        )


DEFAULT_QUALITY_GATE: Final = QualityGateConfig()


@dataclass(frozen=True)
class KnowledgeItem:
    """待分类知识片段（采集环节输入）。"""

    knowledge_id: str
    title: str
    content: str
    source_ref: str = ""


@dataclass(frozen=True)
class ClassificationResult:
    """分类产出（建议草稿，human_gated）。

    verdict: classified=分类完成 / rejected=质量门禁拦截（不进分类） / error=fail-closed。
    verdict!=classified 时 classification 恒为 None（不产半成品）。
    """

    verdict: Literal["classified", "rejected", "error"]
    knowledge_id: str
    classification: ClassificationPayload | None = None
    quality: QualityScores | None = None
    quality_score: float | None = None
    tags_pending_registration: tuple[str, ...] = ()
    rationale: str = ""
    error: str | None = None
    raw_text: str = ""

    @property
    def human_gate_required(self) -> bool:
        """产出 100% human_gated——恒 True（B-007）。"""
        return True


# ── Prompt（受控词表约束；模板常量化防散改）──
_SYSTEM_PROMPT: Final[str] = (
    "你是量化交易知识分类器。你只能从给定受控词表中取值，禁止发明词表外类别。"
    "你只输出一个 JSON 对象，不输出任何其他文字、解释或 markdown 围栏之外的字符。"
)

_PROMPT_TEMPLATE: Final[str] = """对以下知识片段做分类与多维适用性标注。严格输出 JSON（不要任何额外文字）。

【信息价值四维评分】（各 0~1 浮点）
- relevance 相关性（与 A 股量化交易的相关程度）
- timeliness 时效性（有效时间窗口，越长久越高分）
- information 信息量（相对既有量化常识的新增量）
- reliability 可靠性（来源可信度+逻辑自洽性）

【主分类】target_kind 三选一：
- "factor"：alpha 因子 -> factor_class 必填，词表：{factor_classes}
- "strategy"：完整交易策略（含入场/出场/仓位）-> strategy_class 必填，词表：{strategy_classes}
- "other"：其他 -> other_subtype 必填，词表：{other_subtypes}
  （risk_rule=风控规则 / execution_algo=执行算法 / data_asset=数据资产 /
   technical_indicator=技术指标 / tool=工具 / knowledge_only=纯方法论知识）

【v2.0 多维标注】
- primary_timeframe 主时间级别（词表：{timeframes}；无时间语义为 null）
- applicable_timeframes 可泛化时间级别列表（同词表；含 primary；无则空表）
- regime_valid 有效市场环境列表（词表：{regimes}；空=未标注）
- regime_invalid 失效市场环境列表（同词表；与 regime_valid 不得有交集）
- direction 信号方向（词表：{directions}；无方向语义用 "neutral"）
- entry_role 条目角色（词表：{entry_roles}；因子主消费方式=ranking，策略=trigger）
- applies_to 适用标的列表（词表：{applies_to}）
- tags 中文检索标签列表（优先从既有词表取值：{tag_vocab}；确需新词也可给出，将被标记待登记）

【输出 JSON 结构】（键名严格一致，不得多键少键）
{{
  "quality": {{"relevance": 0.0, "timeliness": 0.0, "information": 0.0, "reliability": 0.0}},
  "target_kind": "factor|strategy|other",
  "factor_class": null, "strategy_class": null, "other_subtype": null,
  "primary_timeframe": null, "applicable_timeframes": [],
  "regime_valid": [], "regime_invalid": [],
  "direction": "neutral", "entry_role": "ranking",
  "applies_to": [], "tags": [],
  "confidence": 0.0, "rationale": "一句话裁决理由"
}}

【知识片段】
标题：{title}
来源：{source_ref}
正文：
{content}
"""

_JSON_FENCE_RE: Final = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


def _extract_json(text: str) -> dict[str, Any]:
    """从 LLM 输出抽取 JSON 对象（裸 JSON / markdown 围栏 / 首尾花括号截取，逐候选尝试）。

    任何失败抛 ValueError -> 调用方 fail-closed。
    """
    stripped = text.strip()
    if not stripped:
        raise ValueError("LLM 输出为空")
    candidates = [stripped]
    fence = _JSON_FENCE_RE.search(stripped)
    if fence:
        candidates.append(fence.group(1))
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        candidates.append(stripped[start : end + 1])
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    raise ValueError("LLM 输出中未找到可解析的 JSON 对象")


class KnowledgeClassifier:
    """知识分类器（LLM 受控词表分类 + 四维质量门禁 + 标签归并）。

    llm 注入实现 LLMInferProtocol 的网关（生产=LLMRuntimeGateway，测试=fake）；
    None 时懒构造真实网关（仅真实调用路径触发，测试永不触发）。
    """

    def __init__(
        self,
        *,
        llm: LLMInferProtocol | None = None,
        quality_gate: QualityGateConfig = DEFAULT_QUALITY_GATE,
        known_tags: frozenset[str] | set[str] | None = None,
        tag_synonyms: dict[str, str] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> None:
        weights = (
            quality_gate.weight_relevance,
            quality_gate.weight_timeliness,
            quality_gate.weight_information,
            quality_gate.weight_reliability,
        )
        if any(w <= 0 for w in weights):
            raise KnowledgeClassifierError(f"质量门禁权重必须全为正: {weights}")
        if not (0.0 < quality_gate.threshold < 1.0):
            raise KnowledgeClassifierError(f"质量门禁阈值越界（0,1）: {quality_gate.threshold}")
        vocab = frozenset(known_tags) if known_tags is not None else DEFAULT_TAG_VOCAB
        if not vocab:
            raise KnowledgeClassifierError("标签词表为空（标签归并失去基准）")
        if max_tokens <= 0:
            raise KnowledgeClassifierError(f"max_tokens 必须为正: {max_tokens}")
        self._llm = llm
        self._gate = quality_gate
        self._known_tags = vocab
        self._synonyms = dict(tag_synonyms) if tag_synonyms is not None else dict(DEFAULT_TAG_SYNONYMS)
        self._max_tokens = max_tokens
        self._temperature = temperature

    def _resolve_llm(self) -> LLMInferProtocol:
        if self._llm is None:
            from zephyr.integration.llm_runtime_gateway import LLMRuntimeGateway

            self._llm = LLMRuntimeGateway()
        return self._llm

    def _merge_tags(self, raw_tags: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """标签归并：同义词映射 -> 词表内保留；词表外新词标记待登记（不静默造词）。"""
        merged: list[str] = []
        pending: list[str] = []
        for raw in raw_tags:
            tag = str(raw).strip()
            if not tag:
                continue
            tag = self._synonyms.get(tag, tag)
            if tag in self._known_tags:
                if tag not in merged:
                    merged.append(tag)
            else:
                if tag not in pending:
                    pending.append(tag)
        return tuple(merged), tuple(pending)

    def classify(self, item: KnowledgeItem) -> ClassificationResult:
        """分类一条知识片段。LLM/解析/schema 失败 -> verdict="error"（fail-closed）。"""
        prompt = _PROMPT_TEMPLATE.format(
            factor_classes="/".join(FACTOR_CLASSES),
            strategy_classes="/".join(STRATEGY_CLASSES),
            other_subtypes="/".join(OTHER_SUBTYPES),
            timeframes="/".join(TIMEFRAMES),
            regimes="/".join(REGIMES),
            directions="/".join(DIRECTIONS),
            entry_roles="/".join(ENTRY_ROLES),
            applies_to="/".join(APPLIES_TO),
            tag_vocab="、".join(sorted(self._known_tags)),
            title=item.title,
            source_ref=item.source_ref or "未标注",
            content=item.content,
        )
        try:
            response = self._resolve_llm().infer(
                CLASSIFIER_TASK_TYPE,
                prompt,
                system=_SYSTEM_PROMPT,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
            )
        except Exception as exc:  # noqa: BLE001 — LLM 网关调用失败 fail-closed
            _log.warning("knowledge_classifier LLM 调用异常: %s", exc)
            return ClassificationResult(
                verdict="error",
                knowledge_id=item.knowledge_id,
                error=f"llm_call_failed: {type(exc).__name__}: {exc}",
            )
        status = getattr(response, "status", None)
        raw_text = getattr(response, "text", "") or ""
        if status != "ok":
            return ClassificationResult(
                verdict="error",
                knowledge_id=item.knowledge_id,
                error=f"llm_status={status!r}（网关未返回可用文本）",
                raw_text=raw_text,
            )
        try:
            payload = ClassificationPayload.model_validate(_extract_json(raw_text))
        except Exception as exc:  # noqa: BLE001 — 解析/schema 失败 fail-closed（含词表外枚举）
            _log.warning("knowledge_classifier 输出校验失败: %s", exc)
            return ClassificationResult(
                verdict="error",
                knowledge_id=item.knowledge_id,
                error=f"schema_validation_failed: {type(exc).__name__}: {exc}",
                raw_text=raw_text,
            )

        composite = round(self._gate.composite(payload.quality), 6)
        if composite < self._gate.threshold:
            return ClassificationResult(
                verdict="rejected",
                knowledge_id=item.knowledge_id,
                quality=payload.quality,
                quality_score=composite,
                rationale=payload.rationale,
                error=(
                    f"quality_gate_reject: 综合信息价值 {composite} < "
                    f"{self._gate.threshold}（13号文 §3.1 门禁，不进分类）"
                ),
                raw_text=raw_text,
            )

        merged_tags, pending_tags = self._merge_tags(payload.tags)
        normalized = payload.model_copy(update={"tags": list(merged_tags)})
        return ClassificationResult(
            verdict="classified",
            knowledge_id=item.knowledge_id,
            classification=normalized,
            quality=payload.quality,
            quality_score=composite,
            tags_pending_registration=pending_tags,
            rationale=payload.rationale,
            raw_text=raw_text,
        )
