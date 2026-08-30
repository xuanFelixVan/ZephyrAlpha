# [BLUEPRINT] MOD-INT-MKT-INTERPRETER | docs/03_modules/_domain_intelligence/llm_market_interpreter/blueprint.md
# [MODULE] zephyr.intelligence.llm_market_interpreter
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；local_llm/api_llm/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（local_llm 接本地池 qwen3:8b / api_llm 接 API 池·gateway / mode_selector 接交易时段真源 / audit_sink 接审计链）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 三路全空 Fail-Closed；LLM 输出须为合法 JSON 四字段且值域合规否则 InterpretationError；sources_used 留痕非空输入路；仅信号输入无下单语义；零密钥字段
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/llm_market_interpreter/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 三路全空/未知mode/callable缺失→ValueError；LLM输出结构非法→InterpretationError；audit_sink异常→sink_errors留痕
# [TESTS] tests/intelligence/test_llm_market_interpreter.py
# [A_module] module_id=MOD-INT-MKT-INTERPRETER | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
LlmMarketInterpreter — LLM 市场解读引擎（MOD-INT-MKT-INTERPRETER）

B1-00118（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-ALT-11）：三路输入
（新闻/研报摘要/社媒）统一市场解读——本地 LLM 盘后 + API 盘中双模，
输出结构化结论（主题/情感/影响标的/置信度）；**仅作信号输入不直接
下单**，结论经注入 audit_sink 入审计链。

查重裁定：不复制 news_sentiment_analyzer（MOD-INT-AISA，单路新闻情感
打分+窗口聚合）、api_llm_pool（MOD-INT-API-LLM-POOL，provider 池化
治理）、llm_gateway（MOD-INF-009，真实调用面）、llm_premarket_analysis
（MOD-PLAN-007，盘前复盘单点）；本模块为三路统一解读引擎，LLM 能力经
注入 callable 消费，零密钥零直连。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: local_llm 参数
#   fields: 参数 local_llm（无注解）
#   code: llm_market_interpreter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: api_llm 参数
#   fields: 参数 api_llm（无注解）
#   code: llm_market_interpreter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: mode_selector 参数
#   fields: 参数 mode_selector（无注解）
#   code: llm_market_interpreter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: llm_market_interpreter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LlmMarketInterpreter
#   name_en: LlmMarketInterpreter
#   intro: 三路统一市场解读引擎（判定核心纯内存，LLM/审计全注入式）。
#   desc: 三路统一市场解读引擎（判定核心纯内存，LLM/审计全注入式）。；公共方法（定义序）: sink_errors, interpret；源码 L137-L225
#   inputs: local_llm api_llm mode_selector audit_sink
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: LlmMarketInterpreter
#   downstream: 运行时装配批（local_llm 接本地池 qwen3:8b / api_llm 接 API 池·gateway / mode_selector 接交易时段真…
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
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Callable, Final, Optional

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__: Final = [
    "AuditRecord",
    "InterpretationError",
    "LlmMarketInterpreter",
    "MarketInputBundle",
    "MarketInterpretation",
]

MODES: Final = ("local", "api")
CHANNELS: Final = ("news", "research", "social")
REQUIRED_FIELDS: Final = ("theme", "sentiment", "affected_symbols", "confidence")


class InterpretationError(ZephyrBaseError):
    """LLM 输出结构非法（Fail-Closed，不放行伪结构）。"""


@dataclass(frozen=True)
class MarketInputBundle:
    """三路输入包。"""

    news: tuple = ()
    research: tuple = ()
    social: tuple = ()
    as_of: datetime.datetime | None = None


@dataclass(frozen=True)
class MarketInterpretation:
    """结构化解读结论（仅信号输入，无任何下单/仓位语义）。"""

    theme: str
    sentiment: float
    affected_symbols: tuple
    confidence: float
    mode: str
    sources_used: tuple


@dataclass(frozen=True)
class AuditRecord:
    """审计记录：每次解读外发审计链。"""

    mode: str
    sources_used: tuple
    interpretation: MarketInterpretation
    raw_digest: str
    occurred_at: datetime.datetime


class LlmMarketInterpreter:
    """三路统一市场解读引擎（判定核心纯内存，LLM/审计全注入式）。"""

    def __init__(
        self,
        local_llm: Callable[[str], str] | None = None,
        api_llm: Callable[[str], str] | None = None,
        mode_selector: Callable[[datetime.datetime | None], str] | None = None,
        audit_sink: Callable[[AuditRecord], None] | None = None,
    ) -> None:
        self._local_llm = local_llm
        self._api_llm = api_llm
        self._mode_selector = mode_selector
        self._audit_sink = audit_sink
        self._sink_errors: list[str] = []

    @property
    def sink_errors(self) -> tuple[str, ...]:
        return tuple(self._sink_errors)

    # ── 解析 ──

    @staticmethod
    def _parse_output(raw: str) -> dict:
        try:
            obj = json.loads(raw)
        except (TypeError, json.JSONDecodeError) as exc:
            raise InterpretationError(f"LLM 输出非合法 JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise InterpretationError("LLM 输出非 JSON 对象")
        missing = [f for f in REQUIRED_FIELDS if f not in obj]
        if missing:
            raise InterpretationError(f"LLM 输出缺字段: {missing}")
        sentiment = obj["sentiment"]
        confidence = obj["confidence"]
        if not isinstance(sentiment, (int, float)) or not -1.0 <= float(sentiment) <= 1.0:
            raise InterpretationError(f"sentiment 越界 [-1,1]: {sentiment!r}")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise InterpretationError(f"confidence 越界 [0,1]: {confidence!r}")
        symbols = obj["affected_symbols"]
        if not isinstance(symbols, (list, tuple)):
            raise InterpretationError("affected_symbols 须为列表")
        return obj

    # ── 主接口 ──

    def interpret(self, bundle: MarketInputBundle, mode: str | None = None) -> MarketInterpretation:
        sources = tuple(c for c in CHANNELS if getattr(bundle, c))
        if not sources:
            raise ValueError("三路输入全空（news/research/social 至少一路非空）")
        if mode is None:
            if self._mode_selector is None:
                raise ValueError("mode 未显式给定且 mode_selector 未注入")
            mode = self._mode_selector(bundle.as_of)
        if mode not in MODES:
            raise ValueError(f"未知 mode: {mode!r}（合法: {MODES}）")
        llm = self._local_llm if mode == "local" else self._api_llm
        if llm is None:
            raise ValueError(f"{mode} 模式 LLM callable 未注入")

        prompt_parts = []
        for channel in sources:
            prompt_parts.append(f"[{channel}] " + " | ".join(str(t) for t in getattr(bundle, channel)))
        prompt = "\n".join(prompt_parts)
        raw = llm(prompt)
        obj = self._parse_output(raw)

        out = MarketInterpretation(
            theme=str(obj["theme"]),
            sentiment=float(obj["sentiment"]),
            affected_symbols=tuple(str(s) for s in obj["affected_symbols"]),
            confidence=float(obj["confidence"]),
            mode=mode,
            sources_used=sources,
        )
        if self._audit_sink is not None:
            record = AuditRecord(
                mode=mode,
                sources_used=sources,
                interpretation=out,
                raw_digest=hashlib.md5(raw.encode("utf-8")).hexdigest(),
                occurred_at=datetime.datetime.now(datetime.timezone.utc),
            )
            try:
                self._audit_sink(record)
            except Exception as exc:  # noqa: BLE001 — sink 异常不阻断结论
                log.warning("audit_sink 异常: %s", exc)
                self._sink_errors.append(f"audit_sink: {exc}")
        return out
