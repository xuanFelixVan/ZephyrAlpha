# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | 07号文 §4-P1
# [MODULE] zephyr.autonomy_core.context.local_llm_summarizer
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.context.integrity_check; zephyr.integration.llm_runtime_gateway（懒加载，函数体内 import）
# [CONSUMERS] zephyr.autonomy_core.context.context_assembler（opt-in 注入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 摘要不过 integrity 校验不替换原文（verify_summary_integrity False -> 返回空串，由 DocCompressor 降级 rule_based）; 任一 slot 摘要失败整体降级（防漏段静默丢信息）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 网关缺省/异常/infer 非 ok -> 返回空串（降级不炸，绝不抛给调用方）
# [TESTS] tests/autonomy/test_local_llm_summarizer.py
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""
LocalLLMSummarizer — 本地 Qwen 分 slot 摘要器（07 号文 §4 Phase 1 P1-2）
=========================================================================
llm_summary 压缩档的生产实现：经 llm_runtime_gateway（MOD-INF-051）本地通道
做摘要——调用 infer 时固定 complexity="simple"（ECONOMY/MINIMAL tier，
网关路由本地优先）；可选 channel 显式钉死（如 "ollama"）强制仅本地。

分 slot 摘要逻辑
---------------
1. 原文按 slot_chars 切段（行边界对齐，防切坏 Markdown 结构）；
2. 逐段经网关摘要（prompt 要求保留标题行与 frontmatter）；
3. 合并各段摘要；合并稿仍超 slot_chars 时递归再压缩一轮（最多 max_passes 轮）；
4. 合并摘要过 verify_summary_integrity 交叉校验（约束六）——不过则返回空串，
   由 DocCompressor 三档降级链自动降 rule_based，绝不替换原文。

降级纪律
--------
网关缺省（构造失败）/ infer 异常 / status != "ok" / 任一 slot 失败 /
integrity 校验不过 —— 一律返回空串（降级不炸），由调用方走 rule_based 兜底。

裁定回填（07 号文 §4 P1-3）：维持 sync 主用，async wrapper 待真实需求再建。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: original 参数
#   fields: 参数 original，类型注解 str
#   code: local_llm_summarizer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: summary 参数
#   fields: 参数 summary，类型注解 str
#   code: local_llm_summarizer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: checker 参数
#   fields: 参数 checker（无注解）
#   code: local_llm_summarizer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: min_ratio 参数
#   fields: 参数 min_ratio（无注解）
#   code: local_llm_summarizer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① verify_summary_integrity
#   name_en: verify_summary_integrity
#   intro: 摘要完整性交叉校验（07 号文 §4 P1-2：校验通过方可替换原文）。
#   desc: 摘要完整性交叉校验（07 号文 §4 P1-2：校验通过方可替换原文）。 校验规则（任一条不过即 False）： 1. 摘要非空且确为压缩（len(summary) < len(…；源码 L144-L184
#   inputs: original summary checker min_ratio
#   outputs: bool
# - id: A2
#   name_zh: ② LocalLLMSummarizer
#   name_en: LocalLLMSummarizer
#   intro: 本地 Qwen 分 slot 摘要器（DocCompressor llm_summary 档的生产注入实现）。
#   desc: 本地 Qwen 分 slot 摘要器（DocCompressor llm_summary 档的生产注入实现）。 Parameters ---------- gateway : _…；公共方法（定义序）: summari…
#   inputs: gateway slot_chars max_passes complexity channel integrity_checker
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.autonomy_core.context.context_assembler（opt-in 注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any, Final, Protocol, runtime_checkable

from zephyr.autonomy_core.context.integrity_check import IntegrityCheck

__all__ = [
    "LocalLLMSummarizer",
    "verify_summary_integrity",
]

_log = logging.getLogger(__name__)

_DEFAULT_SLOT_CHARS: Final[int] = 3000
_DEFAULT_MAX_PASSES: Final[int] = 2
_SUMMARY_MIN_RATIO: Final[float] = 0.05
_SUMMARY_MIN_CHARS: Final[int] = 32
_FRONTMATTER_RE: Final = re.compile(r"^(---\n.*?\n---\n?)", re.DOTALL)
_HEADER_RE: Final = re.compile(r"^#{1,6}\s+\S")
_TASK_TYPE: Final[str] = "doc_summary_slot"


@runtime_checkable
class _InferGatewayProtocol(Protocol):
    """摘要器依赖的网关协议（对齐 llm_runtime_gateway.LLMRuntimeGateway.infer）。"""

    def infer(self, task_type: str, prompt: str, **kw: Any) -> Any: ...


def _build_default_gateway() -> _InferGatewayProtocol | None:
    """懒加载默认 LLMRuntimeGateway（跨域 D_INTEGRATION 仅在此函数体内 import）。

    构造失败（本地通道不可用/依赖缺失）降级返回 None，由调用方走空串降级路径。
    """
    try:
        from zephyr.integration.llm_runtime_gateway import LLMRuntimeGateway

        return LLMRuntimeGateway()
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None


def _extract_frontmatter(text: str) -> str:
    m = _FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def _extract_headers(text: str) -> list[str]:
    return [line.strip() for line in text.split("\n") if _HEADER_RE.match(line)]


def verify_summary_integrity(
    original: str,
    summary: str,
    *,
    checker: IntegrityCheck | None = None,
    min_ratio: float = _SUMMARY_MIN_RATIO,
) -> bool:
    """摘要完整性交叉校验（07 号文 §4 P1-2：校验通过方可替换原文）。

    校验规则（任一条不过即 False）：
      1. 摘要非空且确为压缩（len(summary) < len(original)）；
      2. 未塌缩（len(summary) >= max(32, len(original) * min_ratio)）；
      3. frontmatter 完整性——原文含 frontmatter 时，摘要中的 frontmatter 块
         经 IntegrityCheck.verify 做 hash 比对须一致（hashes_match=True）；
      4. 标题保留——原文全部 Markdown 标题行须出现在摘要中。

    checker 可注入（测试 fake）；缺省用 IntegrityCheck 实例。
    """
    if not summary or not summary.strip():
        return False
    if len(summary) >= len(original):
        return False
    if len(summary) < max(_SUMMARY_MIN_CHARS, int(len(original) * min_ratio)):
        return False

    check = checker if checker is not None else IntegrityCheck()

    original_fm = _extract_frontmatter(original)
    if original_fm:
        summary_fm = _extract_frontmatter(summary)
        before_hash = hashlib.sha256(original_fm.encode("utf-8")).hexdigest()
        after_hash = hashlib.sha256(summary_fm.encode("utf-8")).hexdigest()
        report = check.verify(layer="llm_summary", before_hash=before_hash, after_hash=after_hash)
        if not report.hashes_match:
            return False

    summary_headers = set(_extract_headers(summary))
    for header in _extract_headers(original):
        if header not in summary_headers:
            return False
    return True


class LocalLLMSummarizer:
    """本地 Qwen 分 slot 摘要器（DocCompressor llm_summary 档的生产注入实现）。

    Parameters
    ----------
    gateway : _InferGatewayProtocol | None
        LLM 推理网关（协议注入，测试 fake）；None 时首次摘要懒加载默认
        LLMRuntimeGateway，构造失败降级为 summarize() 恒返回空串。
    slot_chars : int
        单 slot 字符上限（默认 3000）；原文不超长时单 slot 直摘。
    max_passes : int
        合并稿仍超长时的递归压缩轮数上限（默认 2，防死循环）。
    complexity : str
        透传 gateway.infer 的复杂度（默认 "simple" -> ECONOMY/MINIMAL tier
        本地优先路由）。
    channel : str | None
        显式钉死通道（如 "ollama" 强制仅本地）；None 时按 complexity 路由。
    integrity_checker : IntegrityCheck | None
        完整性校验器注入位（测试 fake）；缺省 IntegrityCheck()。
    """

    def __init__(
        self,
        gateway: _InferGatewayProtocol | None = None,
        *,
        slot_chars: int = _DEFAULT_SLOT_CHARS,
        max_passes: int = _DEFAULT_MAX_PASSES,
        complexity: str = "simple",
        channel: str | None = None,
        integrity_checker: IntegrityCheck | None = None,
    ) -> None:
        self._gateway = gateway
        self._gateway_resolved = gateway is not None
        self._slot_chars = slot_chars
        self._max_passes = max(1, max_passes)
        self._complexity = complexity
        self._channel = channel
        self._integrity_checker = integrity_checker

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------
    def summarize(self, text: str) -> str:
        """分 slot 摘要入口；任何失败/校验不过返回空串（调用方降级 rule_based）。"""
        if not text or not text.strip():
            return ""
        gateway = self._resolve_gateway()
        if gateway is None:
            return ""
        summary = self._summarize_pass(gateway, text, pass_no=1)
        if not summary:
            return ""
        if not verify_summary_integrity(text, summary, checker=self._integrity_checker):
            _log.warning("llm_summary 摘要未过 integrity 校验，返回空串触发降级")
            return ""
        return summary

    def __call__(self, text: str) -> str:
        """对齐 DocCompressor llm_summarizer 注入位签名 Callable[[str], str]。"""
        return self.summarize(text)

    # ------------------------------------------------------------------
    # 内部：网关解析与 slot 摘要
    # ------------------------------------------------------------------
    def _resolve_gateway(self) -> _InferGatewayProtocol | None:
        if self._gateway is not None:
            return self._gateway
        if not self._gateway_resolved:
            self._gateway = _build_default_gateway()
            self._gateway_resolved = True
        return self._gateway

    def _split_slots(self, text: str) -> list[str]:
        """按 slot_chars 切段（行边界对齐）；单段原文原样返回。"""
        if len(text) <= self._slot_chars:
            return [text]
        slots: list[str] = []
        current: list[str] = []
        current_len = 0
        for line in text.split("\n"):
            line_len = len(line) + 1
            if current and current_len + line_len > self._slot_chars:
                slots.append("\n".join(current))
                current = []
                current_len = 0
            current.append(line)
            current_len += line_len
        if current:
            slots.append("\n".join(current))
        return [s for s in slots if s.strip()]

    def _summarize_slot(self, gateway: _InferGatewayProtocol, slot_text: str, index: int, total: int) -> str:
        """单 slot 摘要；infer 异常/非 ok/空文本一律返回空串。"""
        prompt = (
            f"[文档摘要 slot {index}/{total}] 请将以下文档片段压缩为精炼中文摘要，"
            "要求：完整保留全部 Markdown 标题行（# 开头）与 frontmatter 块"
            "（--- 包围，如有），保留关键事实/规则/路径，删除冗余表述：\n\n"
            f"{slot_text}"
        )
        kw: dict[str, Any] = {"complexity": self._complexity}
        if self._channel is not None:
            kw["channel"] = self._channel
        try:
            result = gateway.infer(_TASK_TYPE, prompt, **kw)
        except Exception as exc:  # noqa: BLE001 — 降级纪律：网关异常不抛给调用方
            _log.warning("llm_summary slot %d/%d infer 异常: %s", index, total, exc)
            return ""
        if getattr(result, "status", "") != "ok":
            _log.warning("llm_summary slot %d/%d status=%s", index, total, getattr(result, "status", ""))
            return ""
        return str(getattr(result, "text", "") or "").strip()

    def _summarize_pass(self, gateway: _InferGatewayProtocol, text: str, *, pass_no: int) -> str:
        """单轮分 slot 摘要；任一 slot 失败整体返回空串（防漏段丢信息）。"""
        slots = self._split_slots(text)
        if len(slots) == 1:
            return self._summarize_slot(gateway, slots[0], 1, 1)
        partials: list[str] = []
        for i, slot in enumerate(slots, 1):
            part = self._summarize_slot(gateway, slot, i, len(slots))
            if not part:
                return ""
            partials.append(part)
        merged = "\n\n".join(partials)
        if len(merged) > self._slot_chars and pass_no < self._max_passes:
            return self._summarize_pass(gateway, merged, pass_no=pass_no + 1)
        return merged
