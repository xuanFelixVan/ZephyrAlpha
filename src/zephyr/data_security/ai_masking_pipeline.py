# [BLUEPRINT] MOD-DATSEC-001 | docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md
# [MODULE] zephyr.data_security.ai_masking_pipeline
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] 无（管道核心纯内存；clock/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（LLM 外发前统一脱敏装配点 / 审计接 gov_audit 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 级别词表闭合(L1|L2|L3|L4); L4 禁发原文仅统计摘要; L3 金额分桶泛化+标的泛化; L2 禁发原值序列仅因子定义+统计; L1 原样放行; 每次调用写脱敏前后对比审计; 标的映射按首现序确定分配; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AiMaskingError(占位 ZA-DSEC-UNREGISTERED-AI-MASKING)——空策略表/未知用途/空文本/非法级别/非法分桶阈值时抛
# [TESTS] tests/data_security/test_ai_masking_pipeline.py
# [A_module] module_id=MOD-DATSEC-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AiMaskingPipeline — AI 分级脱敏管道（MOD-DATSEC-001）。

B13-04183（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATSEC-001，A3数据架构）：
L1-L4 **分级脱敏管道**——L4 禁发原文仅统计摘要 / L3 金额分桶泛化（大额/
中额/小额）+ 标的泛化（标的A/标的B…）/ L2 保留因子定义与统计、禁发原值
序列 / L1 无要求原样放行；**策略表驱动**（用途→MaskingPolicy 注册表，与
MOD-DATSEC-003 共用策略表 schema 语义：Mapping 键查表、未注册 Fail-Closed）；
每次 LLM 调用记录**脱敏前后对比**入审计回调。Presidio 分级思想单机化。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: policies 参数
#   fields: 参数 policies（无注解）
#   code: ai_masking_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: ai_masking_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: ai_masking_pipeline.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AiMaskingPipeline
#   name_en: AiMaskingPipeline
#   intro: L1-L4 分级脱敏管道（策略表驱动 + 审计留痕）。
#   desc: L1-L4 分级脱敏管道（策略表驱动 + 审计留痕）。；公共方法（定义序）: level_of, mask_for_llm；源码 L136-L248
#   inputs: policies clock audit_sink
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: AiMaskingPipeline
#   downstream: 运行时装配批（LLM 外发前统一脱敏装配点 / 审计接 gov_audit 路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AiMaskingError",
    "AiMaskingPipeline",
    "MaskingAuditRecord",
    "MaskingLevel",
    "MaskingPolicy",
]

#: A 股样式标的代码（600519.SH / 000001.SZ / 430047.BJ）
#: 注：不用 \b —— CJK 字符在 Unicode \w 内会吞掉边界，改显式 ASCII 环视
_TICKER_RE: Final = re.compile(r"(?<![0-9A-Za-z.])\d{6}\.(?:SH|SZ|BJ)(?![0-9A-Za-z])")
#: 数值 token（支持千分位逗号与小数；负向环视防越界吞字）
_AMOUNT_RE: Final = re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![\d.])")
#: 原值序列：≥3 个数值以逗号/顿号/斜杠分隔（{2,} = 首个之后至少再跟 2 个）
_SEQ_RE: Final = re.compile(r"\d+(?:\.\d+)?(?:\s*[,，、/]\s*\d+(?:\.\d+)?){2,}")
_SEQ_SPLIT_RE: Final = re.compile(r"[,，、/]")


class AiMaskingError(Exception):
    """脱敏管道输入/策略非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DSEC-UNREGISTERED-AI-MASKING。
    """


class MaskingLevel(str, Enum):
    """脱敏级别（词表闭合，数字越大越严格）。"""

    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


@dataclass(frozen=True)
class MaskingPolicy:
    """单用途脱敏策略（策略表行，frozen）。

    large_amount / medium_amount 为 L3 金额分桶阈值（≥large→大额，
    ≥medium→中额，否则小额）；sequence_min_len 为 L2 原值序列最小长度。
    """

    level: MaskingLevel
    large_amount: float = 1_000_000.0
    medium_amount: float = 100_000.0
    sequence_min_len: int = 3


@dataclass(frozen=True)
class MaskingAuditRecord:
    """单次 LLM 调用脱敏前后对比（审计载荷，frozen）。"""

    purpose: str
    level: MaskingLevel
    before: str
    after: str
    masked_at: datetime.datetime
    note: str


class AiMaskingPipeline:
    """L1-L4 分级脱敏管道（策略表驱动 + 审计留痕）。"""

    def __init__(
        self,
        *,
        policies: Mapping[str, MaskingPolicy],
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[MaskingAuditRecord], None] | None = None,
    ) -> None:
        if not policies:
            raise AiMaskingError("policies 为空（无用途策略声明）")
        for purpose, policy in policies.items():
            if not purpose:
                raise AiMaskingError("purpose 为空")
            if not isinstance(policy, MaskingPolicy):
                raise AiMaskingError(f"非法策略: {purpose!r}")
            if not isinstance(policy.level, MaskingLevel):
                raise AiMaskingError(f"非法级别: {policy.level!r}")
            if policy.medium_amount < 0 or policy.large_amount < policy.medium_amount:
                raise AiMaskingError(f"非法分桶阈值: large={policy.large_amount} medium={policy.medium_amount}")
            if policy.sequence_min_len < 2:
                raise AiMaskingError(f"非法 sequence_min_len: {policy.sequence_min_len}")
        self._policies: dict[str, MaskingPolicy] = dict(policies)
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _policy_of(self, purpose: str) -> MaskingPolicy:
        policy = self._policies.get(purpose)
        if policy is None:
            raise AiMaskingError(f"未知用途: {purpose!r}（未在策略表中注册）")
        return policy

    def _audit(self, purpose: str, level: MaskingLevel, before: str, after: str, note: str) -> None:
        record = MaskingAuditRecord(
            purpose=purpose,
            level=level,
            before=before,
            after=after,
            masked_at=self._clock(),
            note=note,
        )
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — 审计失败不阻断主流程
                _log.exception("audit_sink 审计失败: %s", purpose)

    @staticmethod
    def _bucket(amount: float, policy: MaskingPolicy) -> str:
        if amount >= policy.large_amount:
            return "大额"
        if amount >= policy.medium_amount:
            return "中额"
        return "小额"

    # ── 级别处理 ──────────────────────────────────────────────────────────

    def _mask_l3(self, text: str, policy: MaskingPolicy) -> str:
        """L3：标的泛化（首现序 标的A/标的B…）+ 金额分桶泛化。"""
        tickers = sorted(set(_TICKER_RE.findall(text)), key=text.index)
        mapping = {t: f"标的{chr(ord('A') + i) if i < 26 else i}" for i, t in enumerate(tickers)}
        masked = _TICKER_RE.sub(lambda m: mapping[m.group(0)], text)

        def _amount_sub(m: re.Match[str]) -> str:
            return self._bucket(float(m.group(0).replace(",", "")), policy)

        return _AMOUNT_RE.sub(_amount_sub, masked)

    @staticmethod
    def _mask_l2(text: str, policy: MaskingPolicy) -> str:
        """L2：禁发原值序列——≥sequence_min_len 的数值序列替换为统计摘要。"""

        def _seq_sub(m: re.Match[str]) -> str:
            values = [float(x) for x in _SEQ_SPLIT_RE.split(m.group(0))]
            if len(values) < policy.sequence_min_len:
                return m.group(0)
            mean = sum(values) / len(values)
            return f"[原值序列已脱敏:共{len(values)}个值 均值={mean:.4f} 最小={min(values):.4f} 最大={max(values):.4f}]"

        return _SEQ_RE.sub(_seq_sub, text)

    @staticmethod
    def _mask_l4(text: str) -> str:
        """L4：禁发原文——仅输出确定性统计摘要。"""
        digits = sum(1 for ch in text if ch.isdigit())
        tickers = len(_TICKER_RE.findall(text))
        amounts = len(_AMOUNT_RE.findall(text))
        return f"[L4统计摘要] 字符数={len(text)} 数字字符数={digits} 标的出现数={tickers} 数值token数={amounts}"

    # ── 对外 ─────────────────────────────────────────────────────────────

    def level_of(self, purpose: str) -> MaskingLevel:
        """用途级别查询（未知用途 → Fail-Closed）。"""
        return self._policy_of(purpose).level

    def mask_for_llm(self, purpose: str, text: str) -> str:
        """按用途策略脱敏；每次调用记录脱敏前后对比入审计回调。"""
        policy = self._policy_of(purpose)
        if not isinstance(text, str) or not text:
            raise AiMaskingError("text 为空（无可脱敏载荷）")
        if policy.level is MaskingLevel.L1:
            masked, note = text, "L1 原样放行"
        elif policy.level is MaskingLevel.L2:
            masked, note = self._mask_l2(text, policy), "L2 禁发原值序列"
        elif policy.level is MaskingLevel.L3:
            masked, note = self._mask_l3(text, policy), "L3 金额标的泛化"
        else:
            masked, note = self._mask_l4(text), "L4 禁发仅统计摘要"
        self._audit(purpose, policy.level, text, masked, note)
        return masked
