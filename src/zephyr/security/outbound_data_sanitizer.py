# [BLUEPRINT] MOD-SEC-024 | docs/03_modules/_domain_security/outbound_data_sanitizer/blueprint.md
# [MODULE] zephyr.security.outbound_data_sanitizer
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] 无（纯内存；字段白名单/掩码正则词表/时钟全注入，正则仅标准库 re）
# [CONSUMERS] 运行时装配批（外发 API 出口统一装配本拦截闸：持仓/策略/因子 payload）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 白名单外字段一律剥离(持仓/策略/因子三类闭合); PII/凭证命中正则词表一律掩码(递归作用于嵌套 dict/list 字符串); 未过检(剥离后空载)不放行 Fail-Closed; 报告字段确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_security/outbound_data_sanitizer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OutboundSanitizeError(占位 ZA-SEC-UNREGISTERED-OUTBOUND-SANITIZER)——未知类别/空白名单/空payload/剥离后无白名单字段/非法正则时抛
# [TESTS] tests/security/test_outbound_data_sanitizer.py
# [A_module] module_id=MOD-SEC-024 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""OutboundDataSanitizer — 外发数据脱敏拦截器（MOD-SEC-024）。

B1-00372（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SEC-005，C2）：外发 API
payload **字段级过滤**（持仓/策略/因子三类白名单，白名单外字段一律剥离）
+ **PII/凭证掩码**（正则词表，递归作用于嵌套字符串）+ **统一出口拦截**
（未过检不放行 Fail-Closed）。

查重分工（蓝图 §0）：MOD-DATSEC-002=存储/访问侧脱敏引擎（本件不复用其引
擎）；output_guard=输出内容守卫语义（本件=外发出口拦截闸，仅作出口统一
装配点，不重建内容审查）。
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_MASK_PATTERNS",
    "MASK_REPLACEMENT",
    "OutboundSanitizeError",
    "OutboundDataSanitizer",
    "PayloadCategory",
    "SanitizeReport",
]


class OutboundSanitizeError(Exception):
    """外发脱敏拦截输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SEC-UNREGISTERED-OUTBOUND-SANITIZER。
    """


class PayloadCategory(str, Enum):
    """外发 payload 类别（词表闭合）。"""

    POSITIONS = "positions"
    STRATEGY = "strategy"
    FACTORS = "factors"


#: 默认 PII/凭证掩码正则词表（注入词表可覆盖/扩展）
DEFAULT_MASK_PATTERNS: Final[dict[str, str]] = {
    "phone": r"1[3-9]\d{9}",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "id_card": r"\b\d{17}[\dXx]\b",
    "credential": r"(?i)(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*[^\s,;]+",
}

#: 掩码替换串
MASK_REPLACEMENT: Final[str] = "***"


@dataclass(frozen=True)
class SanitizeReport:
    """脱敏报告（确定性排序，frozen）。"""

    category: PayloadCategory
    kept_fields: tuple[str, ...]
    stripped_fields: tuple[str, ...]
    masked_fields: tuple[str, ...]
    sanitized: dict
    checked_at: datetime.datetime


class OutboundDataSanitizer:
    """外发出口拦截闸（白名单过滤 + PII/凭证掩码 + 未过检不放行）。"""

    def __init__(
        self,
        *,
        field_whitelists: Mapping[PayloadCategory, Iterable[str]],
        mask_patterns: Mapping[str, str] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not field_whitelists:
            raise OutboundSanitizeError("field_whitelists 为空（无白名单声明）")
        whitelists: dict[PayloadCategory, frozenset[str]] = {}
        for category, fields in field_whitelists.items():
            if not isinstance(category, PayloadCategory):
                raise OutboundSanitizeError(f"非法 payload 类别: {category!r}")
            field_set = frozenset(fields)
            if not field_set:
                raise OutboundSanitizeError(f"类别 {category.value} 白名单为空")
            if any(not f for f in field_set):
                raise OutboundSanitizeError(f"类别 {category.value} 白名单含空字段名")
            whitelists[category] = field_set
        self._whitelists = whitelists

        patterns = dict(DEFAULT_MASK_PATTERNS)
        if mask_patterns is not None:
            for name, pattern in mask_patterns.items():
                if not name:
                    raise OutboundSanitizeError("掩码规则名为空")
                patterns[name] = pattern
        compiled: dict[str, re.Pattern[str]] = {}
        for name, pattern in patterns.items():
            try:
                compiled[name] = re.compile(pattern)
            except re.error as exc:
                raise OutboundSanitizeError(f"非法掩码正则 {name!r}: {exc}") from exc
        self._mask_patterns: Final = compiled
        self._clock = clock or datetime.datetime.now

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _mask_value(self, value: object) -> tuple[object, bool]:
        """递归掩码字符串值；返回 (新值, 是否发生掩码)。"""
        if isinstance(value, str):
            masked = value
            for pattern in self._mask_patterns.values():
                masked = pattern.sub(MASK_REPLACEMENT, masked)
            return masked, masked != value
        if isinstance(value, Mapping):
            out: dict = {}
            changed = False
            for key, sub in value.items():
                new_sub, sub_changed = self._mask_value(sub)
                out[key] = new_sub
                changed = changed or sub_changed
            return out, changed
        if isinstance(value, (list, tuple)):
            items = []
            changed = False
            for sub in value:
                new_sub, sub_changed = self._mask_value(sub)
                items.append(new_sub)
                changed = changed or sub_changed
            return type(value)(items), changed
        return value, False

    # ── 出口拦截 ─────────────────────────────────────────────────────────

    def sanitize(
        self, category: PayloadCategory, payload: Mapping[str, object]
    ) -> SanitizeReport:
        """出口拦截：白名单剥离 → 递归掩码 → 未过检（空载）Fail-Closed 不放行。"""
        if not isinstance(category, PayloadCategory):
            raise OutboundSanitizeError(f"非法 payload 类别: {category!r}")
        whitelist = self._whitelists.get(category)
        if whitelist is None:
            raise OutboundSanitizeError(f"类别 {category.value} 未注册白名单（Fail-Closed）")
        if not isinstance(payload, Mapping) or not payload:
            raise OutboundSanitizeError("payload 为空或非 Mapping（Fail-Closed 不放行）")

        sanitized: dict[str, object] = {}
        stripped: list[str] = []
        masked: list[str] = []
        for field, value in payload.items():
            if field not in whitelist:
                stripped.append(field)
                continue
            new_value, was_masked = self._mask_value(value)
            sanitized[field] = new_value
            if was_masked:
                masked.append(field)

        if not sanitized:
            _log.warning("外发拦截: 类别 %s 剥离后空载，不放行", category.value)
            raise OutboundSanitizeError(
                f"未过检不放行: 类别 {category.value} 白名单内无字段（全量剥离）"
            )
        if stripped:
            _log.info("外发脱敏: 类别 %s 剥离字段 %s", category.value, sorted(stripped))
        if masked:
            _log.info("外发脱敏: 类别 %s 掩码字段 %s", category.value, sorted(masked))

        return SanitizeReport(
            category=category,
            kept_fields=tuple(sorted(sanitized)),
            stripped_fields=tuple(sorted(stripped)),
            masked_fields=tuple(sorted(masked)),
            sanitized=sanitized,
            checked_at=self._clock(),
        )
