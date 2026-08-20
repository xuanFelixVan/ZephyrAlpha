# [BLUEPRINT] MOD-NLP-INFERENCE-001 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md | §Phase 2
# [MODULE] zephyr.nlp.nlp_inference
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.integration.local_model.ollama_chat; zephyr.integration.local_model.deepseek_chat; zephyr.integration.local_model.cache_layer
# [CONSUMERS] scripts/ml/eval_sentiment.py; P1-E3 NLP 管道 Phase 2/3
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 单一推理源——复用 Ollama/DeepSeek local_model 层；零 torch 依赖；CacheLayer 缓存去重；推理失败降级 neutral 不抛异常
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NLPInferenceError(ZA-NLP-0001)——仅 chat 为 None 时抛；推理/解析失败降级 neutral
# [TESTS] tests/nlp/test_nlp_inference.py
# [A_module] module_id=MOD-NLP-INFERENCE-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-NLP-PIPELINE-001 Phase 2

"""

MOD-NLP-INFERENCE-001 NLPImply — 新闻情感推理（零样本基线）。

复用 local_model 层（OllamaChat / DeepSeekChat），实现新闻情感分类：

- prompt 模板（SYSTEM/USER，A 股新闻情感专家）
- ``parse_sentiment()``（正则提 JSON，容忍 ``<think>`` / markdown 围栏 / 前后噪声）
- ``sentiment_to_score()``（归一化 [-1, 1] 有向极性）
- ``CacheLayer`` 缓存避免重复推理（模型版本入键，换模型自动失效）

单一推理源原则（§1.4）：推理轨复用 Ollama local_model 层，零 torch 依赖。
训练轨（SFT/RLSP）产物转 GGUF 回灌 Ollama，保持推理路径统一。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md Phase 2
SSoT: #ARCH-NLP-PIPELINE-001
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 新闻标题与内容 str
#   fields: title（必填）/ content（可选，截断 max_content_chars=300）/ news_id（追踪，可选）
#   code: nlp_inference.py L239-247 infer_sentiment(title, content, news_id)
# - id: I2
#   name: 推理后端 ChatBackend
#   fields: OllamaChat / DeepSeekChat，协议方法 ask(prompt, system, temperature)
#   code: nlp_inference.py L78-81 ChatBackend Protocol
# - id: I3
#   name: 查询缓存 CacheLayer（可选）
#   fields: get_query_result / put_query_result，collection=news_sentiment
#   code: nlp_inference.py L224 _CACHE_COLLECTION
# - id: I4
#   name: 推理配置 InferConfig
#   fields: model_version（入缓存键）/ temperature=0.0 / max_content_chars=300
#   code: nlp_inference.py L227-236 InferConfig
# 层: 算法
# - id: A1
#   name_zh: ① 缓存命中判定
#   name_en: infer_sentiment 缓存段
#   intro: 模型版本+标题+内容截断拼键查缓存，命中直接返回不跑模型
#   desc: L277-295 cache_key_text=f"[{model_version}]{title}\n{snippet}"；命中→SentimentResult(cached=True)；换模型版本缓存自动失效
#   inputs: I1 I3 I4
#   outputs: 命中 SentimentResult / 未命中转 A2
# - id: A2
#   name_zh: ② LLM 零样本情感推理
#   name_en: chat.ask + SYSTEM_PROMPT/USER_TEMPLATE
#   intro: 用 A 股情感专家 prompt 调本地大模型，要求只回 JSON
#   desc: L56-70 prompt 模板（利好/利空/中性词表+JSON 输出契约）；L298-310 组 USER→chat.ask；后端异常降级 neutral(0.5) 不抛
#   inputs: I1 I2 I4
#   outputs: 模型原始文本 raw
# - id: A3
#   name_zh: ③ 输出解析 parse_sentiment
#   name_en: parse_sentiment
#   intro: 三级兜底从带噪文本里抠出 sentiment/score
#   desc: L119-173 去<think>思考块/markdown围栏→json.loads→{...}对象正则→字段级正则（容忍缺"{"）；全失败降级 (neutral, 0.5)；score 裁剪 [0,1]
#   inputs: A2
#   outputs: (sentiment, score)
# - id: A4
#   name_zh: ④ 有向极性归一化
#   name_en: sentiment_to_score
#   intro: 把离散情感标签映射成 [-1,1] 连续极性分值
#   desc: L202-219 positive→+score / negative→-score / neutral→0
#   inputs: A3
#   outputs: polarity ∈[-1,1]
# - id: A5
#   name_zh: ⑤ 批量推理 infer_batch
#   name_en: infer_batch
#   intro: 对新闻列表逐条顺序推理，结果与输入等长同序
#   desc: L332-364 for item in news_items → infer_sentiment；单条失败降级不阻断整体
#   inputs: I1 I2 I3 I4
#   outputs: list[SentimentResult]
# 层: 输出
# - id: O1
#   name_zh: 情感推理结果 SentimentResult
#   name_en: SentimentResult
#   intro: 七字段冻结 dataclass：sentiment/score/polarity/news_id/raw(截断500)/cached/error
#   invariant: 推理/解析失败降级 neutral+0.5 不抛异常；polarity∈[-1,1]
#   downstream: scripts/ml/eval_sentiment.py; P1-E3 NLP 管道 Phase 2/3（[CONSUMERS] 头）
# - id: O2
#   name_zh: 情感结果缓存写入
#   name_en: cache.put_query_result(news_sentiment)
#   intro: 推理结果按含模型版本的文本键写入查询缓存，避免重复推理
#   downstream: CacheLayer（zephyr.integration.local_model.cache_layer），供后续 infer_sentiment 命中复用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
# A1 --> A2
# I1 --> A2
# I2 --> A2
# I4 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
# A4 --> O2
# I1 --> A5
# I2 --> A5
# A5 --> O1
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, Protocol, runtime_checkable

if TYPE_CHECKING:
    from zephyr.integration.local_model.cache_layer import CacheLayer

_log = logging.getLogger(__name__)

# ── 情感标签 ──
POSITIVE = "positive"
NEGATIVE = "negative"
NEUTRAL = "neutral"
_VALID_SENTIMENTS = frozenset({POSITIVE, NEGATIVE, NEUTRAL})

# ── prompt 模板（A 股新闻情感专家）──
SYSTEM_PROMPT = """你是 A 股金融新闻情感分析专家。对给定新闻标题和内容进行情感分类。

分类标准:
- positive: 利好消息（降准/降息/利好/增长/盈利/回购/增持/重组/并购/改革/刺激/回暖/企稳/反弹等）
- negative: 利空消息（跌停/暴跌/下跌/利空/亏损/减持/违规/处罚/退市/爆雷/违约/风险/警告/监管/解禁/熔断/崩盘/恐慌等）
- neutral: 中性消息（常规公告/人事变动/数据发布/行业分析等无明显方向性）

输出 JSON: {"sentiment": "positive|negative|neutral", "score": 0.0-1.0}
score 表示情感强度（1.0=极强正向/负向，0.5=温和，0.0=完全中性）。
只输出 JSON，不要输出其他内容。"""

USER_TEMPLATE = """新闻标题: {title}
新闻内容: {content}

请分析这条新闻的情感倾向，输出 JSON。"""


class NLPInferenceError(Exception):
    """NLP 推理编程错误（ZA-NLP-0001）——仅 chat 为 None 等契约违反时抛。"""

    error_code = "ZA-NLP-0001"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@runtime_checkable
class ChatBackend(Protocol):
    """推理后端协议——OllamaChat / DeepSeekChat 均满足。"""

    def ask(self, prompt: str, *, system: str = ..., temperature: float | None = ...) -> str: ...


@dataclass(frozen=True)
class SentimentResult:
    """单条新闻情感推理结果。

    Attributes
    ----------
    sentiment : positive / negative / neutral
    score : 情感强度 [0, 1]
    polarity : 有向极性 [-1, 1]（positive→+, negative→-, neutral→0）
    news_id : 新闻 ID（追踪用，可选）
    raw : 模型原始输出（调试用，截断 500 字符）
    cached : 是否命中 CacheLayer
    error : 推理错误信息（非空表示降级，此时 sentiment=neutral）
    """

    sentiment: str
    score: float
    polarity: float
    news_id: str = ""
    raw: str = ""
    cached: bool = False
    error: str = ""


# ── 解析 ──────────────────────────────────────────────────────────────

_THINK_RE = re.compile(r"<think>[\s\S]*?</think>", re.IGNORECASE)
# 匹配第一个扁平 JSON 对象（情感输出无嵌套花括号）
_JSON_OBJ_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)
# 宽松兜底：decoder-only 生成切片瑕疵（开头 "{" 被切掉）或模型未充分收敛时，
# 仍能从残缺输出中提取 sentiment/score 字段，避免一律降级 neutral。
_SENTIMENT_FIELD_RE = re.compile(r'"sentiment"\s*:\s*"(positive|negative|neutral)"', re.IGNORECASE)
_SCORE_FIELD_RE = re.compile(r'"score"\s*:\s*([0-9]*\.?[0-9]+)', re.IGNORECASE)


def parse_sentiment(raw: str) -> tuple[str, float]:
    """从模型原始输出解析 ``(sentiment, score)``。

    容忍：``<think>`` 思考块、markdown 围栏、前后噪声文本。
    解析失败 → ``("neutral", 0.5)`` 降级（不抛异常）。

    Parameters
    ----------
    raw : 模型原始文本输出。

    Returns
    -------
    (sentiment, score) — sentiment ∈ {positive, negative, neutral}，score ∈ [0, 1]。
    """
    if not raw or not raw.strip():
        return NEUTRAL, 0.5

    text = _THINK_RE.sub("", raw).strip()

    # 去 markdown 围栏（```json ... ``` 或 ``` ... ```）
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].strip()

    # 尝试直接解析
    sentiment, score = _try_parse_json(text)
    if sentiment is not None:
        return sentiment, score

    # 回退：正则提取第一个 JSON 对象
    m = _JSON_OBJ_RE.search(text)
    if m:
        sentiment, score = _try_parse_json(m.group(0))
        if sentiment is not None:
            return sentiment, score

    # 终极兜底：字段级正则——不依赖花括号配对，容忍开头 "{" 丢失 / 前缀噪声。
    # SFT 早期或 batch generate 切片边界瑕疵时，JSON 主体仍完整但缺 "{"，
    # 此时 _JSON_OBJ_RE 匹配不到，用字段正则直接提取 sentiment/score。
    sm = _SENTIMENT_FIELD_RE.search(text)
    if sm:
        sentiment = sm.group(1).lower()
        score = 0.5
        scm = _SCORE_FIELD_RE.search(text)
        if scm:
            try:
                score = max(0.0, min(1.0, float(scm.group(1))))
            except ValueError:
                pass
        return sentiment, score

    _log.warning("parse_sentiment: 解析失败，降级 neutral; raw=%s", raw[:200])
    return NEUTRAL, 0.5


def _try_parse_json(text: str) -> tuple[str | None, float]:
    """尝试解析 JSON 文本为 (sentiment, score)；失败返回 (None, 0.0)。"""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None, 0.0
    if not isinstance(obj, dict):
        return None, 0.0
    return _extract_sentiment(obj), _extract_score(obj)


def _extract_sentiment(obj: dict[str, Any]) -> str:
    """从 dict 提取并校验 sentiment。"""
    sentiment = str(obj.get("sentiment", NEUTRAL)).strip().lower()
    return sentiment if sentiment in _VALID_SENTIMENTS else NEUTRAL


def _extract_score(obj: dict[str, Any]) -> float:
    """从 dict 提取并裁剪 score 到 [0, 1]。"""
    try:
        score = float(obj.get("score", 0.5))
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, score))


def sentiment_to_score(sentiment: str, score: float) -> float:
    """归一化到 [-1, 1] 有向极性。

    - positive → +score（0 到 1）
    - negative → -score（0 到 -1）
    - neutral  → 0

    Parameters
    ----------
    sentiment : positive / negative / neutral
    score : 情感强度 [0, 1]
    """
    clamped = max(0.0, min(1.0, score))
    if sentiment == POSITIVE:
        return clamped
    if sentiment == NEGATIVE:
        return -clamped
    return 0.0


# ── 推理 ──────────────────────────────────────────────────────────────

_CACHE_COLLECTION = "news_sentiment"


@dataclass(frozen=True)
class InferConfig:
    """推理配置——封装 model_version / temperature / max_content_chars。

    用 dataclass 打包避免 ``infer_sentiment`` 参数列表 >7（§5.150 Long Parameter List）。
    """

    model_version: str = ""
    temperature: float = 0.0
    max_content_chars: int = 300


def infer_sentiment(
    title: str,
    content: str = "",
    *,
    chat: ChatBackend,
    news_id: str = "",
    cache: CacheLayer | None = None,
    config: InferConfig | None = None,
) -> SentimentResult:
    """对单条新闻推理情感——复用 local_model 层，CacheLayer 去重。

    推理后端异常或解析失败时降级为 ``neutral`` (score=0.5)，不抛异常
    （批量推理容错：单条失败不阻断整体）。

    Parameters
    ----------
    title : 新闻标题。
    content : 新闻内容（截断到 ``config.max_content_chars`` 控制 token 成本）。
    chat : 推理后端（OllamaChat / DeepSeekChat）。
    news_id : 新闻 ID（追踪用）。
    cache : CacheLayer 实例；传入则按文本哈希缓存，避免重复推理。
    config : 推理配置（model_version / temperature / max_content_chars）；
        ``None`` 时用 ``InferConfig()`` 默认值。

    Returns
    -------
    SentimentResult

    Raises
    ------
    NLPInferenceError
        chat 为 None（契约违反）。
    """
    if chat is None:
        raise NLPInferenceError("chat 推理后端不能为 None")

    cfg = config or InferConfig()
    content_snippet = (content or "")[: cfg.max_content_chars]
    # model_version 入键：换模型时缓存自动失效（避免读到旧模型结果）
    cache_key_text = f"[{cfg.model_version}]{title}\n{content_snippet}"

    # 缓存命中
    if cache is not None:
        cached = cache.get_query_result(cache_key_text, _CACHE_COLLECTION)
        if cached:
            item = cached[0]
            sentiment = item.get("sentiment", NEUTRAL)
            score_val = float(item.get("score", 0.5))
            _log.debug("infer_sentiment: 缓存命中 news_id=%s", news_id)
            return SentimentResult(
                sentiment=sentiment,
                score=score_val,
                polarity=sentiment_to_score(sentiment, score_val),
                news_id=news_id,
                raw="(cached)",
                cached=True,
            )

    # 推理
    prompt = USER_TEMPLATE.format(title=title, content=content_snippet)
    try:
        raw = chat.ask(prompt, system=SYSTEM_PROMPT, temperature=cfg.temperature)
    except Exception as exc:  # noqa: BLE001 — 推理后端异常降级，不阻断批量
        _log.warning("infer_sentiment: 推理失败 news_id=%s: %s", news_id, exc)
        return SentimentResult(
            sentiment=NEUTRAL,
            score=0.5,
            polarity=0.0,
            news_id=news_id,
            raw="",
            error=str(exc)[:200],
        )

    sentiment, score_val = parse_sentiment(raw)
    polarity = sentiment_to_score(sentiment, score_val)

    # 写缓存
    if cache is not None:
        cache.put_query_result(
            cache_key_text,
            _CACHE_COLLECTION,
            [{"sentiment": sentiment, "score": score_val}],
        )

    return SentimentResult(
        sentiment=sentiment,
        score=score_val,
        polarity=polarity,
        news_id=news_id,
        raw=raw[:500],
    )


def infer_batch(
    news_items: list[dict[str, Any]],
    *,
    chat: ChatBackend,
    cache: CacheLayer | None = None,
    config: InferConfig | None = None,
) -> list[SentimentResult]:
    """批量推理——对 news_items 列表逐条推理（顺序，Ollama 单线程）。

    Parameters
    ----------
    news_items : 新闻 dict 列表，元素需含 ``title``（必填）、``content``（可选）、
        ``news_id``（可选）。

    其余参数同 :func:`infer_sentiment`。

    Returns
    -------
    list[SentimentResult] —— 与 news_items 等长、同序。
    """
    results: list[SentimentResult] = []
    for item in news_items:
        results.append(
            infer_sentiment(
                title=item.get("title", ""),
                content=item.get("content", ""),
                chat=chat,
                news_id=item.get("news_id", ""),
                cache=cache,
                config=config,
            )
        )
    return results


__all__: Final = [
    "POSITIVE",
    "NEGATIVE",
    "NEUTRAL",
    "SYSTEM_PROMPT",
    "USER_TEMPLATE",
    "ChatBackend",
    "SentimentResult",
    "InferConfig",
    "NLPInferenceError",
    "parse_sentiment",
    "sentiment_to_score",
    "infer_sentiment",
    "infer_batch",
]
