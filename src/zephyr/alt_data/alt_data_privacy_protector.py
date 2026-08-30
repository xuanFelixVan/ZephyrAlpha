# [BLUEPRINT] MOD-ALT-012 | docs/03_modules/_domain_alt_data/alt_data_privacy_protector/blueprint.md
# [MODULE] zephyr.alt_data.alt_data_privacy_protector
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（判定核心纯内存；时钟/审计回调全注入，复用 gov_audit/privacy 语义不 import）
# [CONSUMERS] 运行时装配批（另类数据入库前脱敏管道挂 connector 落库路径 / 访问审计接 alert·gov_audit 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 判定核心纯内存无IO；PII词表=默认正则（手机号/身份证/姓名）+注入扩展并集；脱敏幂等（同文本同输出）；入库前白名单最小化留存（非白名单字段必丢弃）；TTL裁决严格（stored_at晚于时钟即Fail-Closed）；访问审计先记日志后回调；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/alt_data_privacy_protector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AltPrivacyError(占位 ZA-ALT-UNREGISTERED-ALT-PRIVACY)——pii_type空白/正则不可编译/TTL非正/重复TTL登记/未知数据集TTL裁决/stored_at晚于时钟/白名单空/非映射记录/访问要素空白时抛
# [TESTS] tests/alt_data/test_alt_data_privacy_protector.py
# [A_module] module_id=MOD-ALT-012 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



AltDataPrivacyProtector — 另类数据隐私保护器（MOD-ALT-012）。

B14-04665（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-021，A9
D-ALT-DATA-17）：另类数据 **PII 识别**（手机号/身份证/姓名默认正则 +
注入扩展正则兜底）+ 入库前**脱敏管道**（文本掩码 + 记录字段清洗）+
**最小化留存策略**（字段白名单 + TTL 裁决）+ **访问审计回调**，
复用 gov_audit/privacy 语义（纯内存委托，不 import 其实现）。

查重分工（蓝图 §0）：gov_audit/privacy=治理域隐私台账（本件=另类数据
入库路径上的识别/脱敏/留存执行面，只输出清洗产物与审计事件）；本件不做
采集与落库（在 connector 族），仅在管道内做字段级裁决。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: extra_patterns 参数
#   fields: 参数 extra_patterns（无注解）
#   code: alt_data_privacy_protector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: alt_data_privacy_protector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: alt_data_privacy_protector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AltDataPrivacyProtector
#   name_en: AltDataPrivacyProtector
#   intro: 另类数据隐私保护器（PII 识别 + 脱敏管道 + 最小化留存 + 访问审计）。
#   desc: 另类数据隐私保护器（PII 识别 + 脱敏管道 + 最小化留存 + 访问审计）。；公共方法（定义序）: detect_pii, sanitize_text, sanitize_record, register_ttl,…
#   inputs: extra_patterns clock audit_sink
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: AltDataPrivacyProtector
#   downstream: 运行时装配批（另类数据入库前脱敏管道挂 connector 落库路径 / 访问审计接 alert·gov_audit 路由）
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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_PII_PATTERNS",
    "AccessAudit",
    "AltDataPrivacyProtector",
    "AltPrivacyError",
    "PiiFinding",
    "PiiPattern",
]


class AltPrivacyError(Exception):
    """隐私保护输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-ALT-PRIVACY。
    """


@dataclass(frozen=True)
class PiiPattern:
    """PII 识别模式（pii_type 词表可扩展，mask 为整体替换文本）。"""

    pii_type: str
    pattern: str
    mask: str


@dataclass(frozen=True)
class PiiFinding:
    """单处 PII 命中（位置 + 原文 + 类型）。"""

    pii_type: str
    matched: str
    start: int
    end: int


@dataclass(frozen=True)
class AccessAudit:
    """数据访问审计事件（frozen，先记日志后回调）。"""

    accessor: str
    dataset_id: str
    purpose: str
    accessed_at: datetime.datetime


#: 默认 PII 识别词表（身份证/手机号/姓名，长模式优先避免子串抢配；注入 extra_patterns 可扩展）
DEFAULT_PII_PATTERNS: Final[tuple[PiiPattern, ...]] = (
    PiiPattern(pii_type="id_card", pattern=r"\d{17}[\dXx]", mask="[IDCARD]"),
    PiiPattern(pii_type="mobile_phone", pattern=r"1[3-9]\d{9}", mask="[PHONE]"),
    PiiPattern(pii_type="person_name", pattern=r"(?:姓名|联系人)[:：][一-龥]{2,4}", mask="[NAME]"),
)


class AltDataPrivacyProtector:
    """另类数据隐私保护器（PII 识别 + 脱敏管道 + 最小化留存 + 访问审计）。"""

    def __init__(
        self,
        *,
        extra_patterns: Sequence[PiiPattern] = (),
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[AccessAudit], None] | None = None,
    ) -> None:
        patterns = list(DEFAULT_PII_PATTERNS) + list(extra_patterns)
        seen_types: set[str] = set()
        compiled: list[tuple[PiiPattern, re.Pattern]] = []
        for p in patterns:
            if not p.pii_type or not p.pii_type.strip():
                raise AltPrivacyError("pii_type 空白")
            if p.pii_type in seen_types:
                raise AltPrivacyError(f"pii_type 重复: {p.pii_type!r}")
            if not p.mask:
                raise AltPrivacyError(f"mask 空白: {p.pii_type!r}")
            try:
                rx = re.compile(p.pattern)
            except re.error as exc:
                raise AltPrivacyError(f"正则不可编译: {p.pii_type!r} {p.pattern!r} ({exc})") from exc
            seen_types.add(p.pii_type)
            compiled.append((p, rx))
        self._patterns: tuple[tuple[PiiPattern, re.Pattern], ...] = tuple(compiled)
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._ttl_days: dict[str, int] = {}
        self._access_log: list[AccessAudit] = []

    # ── PII 识别 ──────────────────────────────────────────────────────────

    def detect_pii(self, text: str) -> list[PiiFinding]:
        """识别文本中的 PII（按 (start, pii_type) 确定性排序）。"""
        if not isinstance(text, str):
            raise AltPrivacyError(f"text 非字符串: {type(text)!r}")
        findings: list[PiiFinding] = []
        for p, rx in self._patterns:
            for m in rx.finditer(text):
                findings.append(PiiFinding(pii_type=p.pii_type, matched=m.group(0), start=m.start(), end=m.end()))
        findings.sort(key=lambda f: (f.start, f.pii_type))
        return findings

    # ── 脱敏管道 ──────────────────────────────────────────────────────────

    def sanitize_text(self, text: str) -> str:
        """文本脱敏（按词表顺序整体替换，幂等确定性）。"""
        if not isinstance(text, str):
            raise AltPrivacyError(f"text 非字符串: {type(text)!r}")
        out = text
        for p, rx in self._patterns:
            out = rx.sub(p.mask, out)
        return out

    def sanitize_record(
        self,
        record: Mapping[str, object],
        whitelist: Sequence[str],
    ) -> dict[str, object]:
        """入库前记录清洗：白名单最小化留存（非白名单字段丢弃）+ 字符串字段脱敏。"""
        if not isinstance(record, Mapping):
            raise AltPrivacyError(f"record 非映射: {type(record)!r}")
        if not whitelist:
            raise AltPrivacyError("whitelist 为空（最小化留存须显式声明字段）")
        allowed = set(whitelist)
        for field in allowed:
            if not field or not str(field).strip():
                raise AltPrivacyError("whitelist 含空白字段名")
        out: dict[str, object] = {}
        for key, value in record.items():
            if key not in allowed:
                continue  # 非白名单字段必丢弃
            out[key] = self.sanitize_text(value) if isinstance(value, str) else value
        return out

    # ── TTL 裁决（最小化留存） ─────────────────────────────────────────────

    def register_ttl(self, dataset_id: str, ttl_days: int) -> None:
        """登记数据集留存期限（天，须为正）。"""
        if not dataset_id or not dataset_id.strip():
            raise AltPrivacyError("dataset_id 空白")
        if dataset_id in self._ttl_days:
            raise AltPrivacyError(f"dataset_id TTL 重复登记: {dataset_id!r}")
        if ttl_days <= 0:
            raise AltPrivacyError(f"ttl_days 非正: {ttl_days!r}")
        self._ttl_days[dataset_id] = int(ttl_days)

    def should_retain(self, dataset_id: str, stored_at: datetime.datetime) -> bool:
        """TTL 裁决：now - stored_at <= ttl 则留存；未登记/未来时间 → Fail-Closed。"""
        ttl = self._ttl_days.get(dataset_id)
        if ttl is None:
            raise AltPrivacyError(f"未知数据集 TTL: {dataset_id!r}（未登记留存策略）")
        now = self._clock()
        if stored_at > now:
            raise AltPrivacyError(f"stored_at 晚于当前时钟（未来数据）: {stored_at!r}")
        return (now - stored_at).days <= ttl

    # ── 访问审计 ──────────────────────────────────────────────────────────

    def record_access(self, accessor: str, dataset_id: str, purpose: str) -> AccessAudit:
        """访问审计：要素非空校验 → 记内存日志 → 注入回调（回调异常不阻断）。"""
        for name, val in (("accessor", accessor), ("dataset_id", dataset_id), ("purpose", purpose)):
            if not val or not val.strip():
                raise AltPrivacyError(f"{name} 空白")
        audit = AccessAudit(accessor=accessor, dataset_id=dataset_id, purpose=purpose, accessed_at=self._clock())
        _log.info("另类数据访问审计: %s 访问 %s（%s）", accessor, dataset_id, purpose)
        self._access_log.append(audit)
        if self._audit_sink is not None:
            try:
                self._audit_sink(audit)
            except Exception:  # noqa: BLE001 — 审计回调不阻断（蓝图 §1）
                _log.exception("audit_sink 回调失败")
        return audit

    def access_log(self) -> tuple[AccessAudit, ...]:
        """访问审计留痕（按发生顺序）。"""
        return tuple(self._access_log)
