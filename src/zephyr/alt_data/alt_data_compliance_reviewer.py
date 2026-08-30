# [BLUEPRINT] MOD-ALT-015 | docs/03_modules/_domain_alt_data/alt_data_compliance_reviewer/blueprint.md
# [MODULE] zephyr.alt_data.alt_data_compliance_reviewer
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（协议核心纯内存；时钟全注入，复用 compliance_log 语义不 import）
# [CONSUMERS] 运行时装配批（数据源上线前接 alt_data_connector 准入 / 白名单输出接健康度管理器准入 / 审查记录接 compliance_log 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 协议核心纯内存无IO；四要素均须非空；审查清单项数闭合（注册时固定，审查须逐项判定并附证据）；整体通过=所有项通过；已批准态需复核（过期距 today-review_interval>0 则退过期态）；白名单=已批准且未过期；禁用清单=BANNED态；审查记录不可修改仅追加；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/alt_data_compliance_reviewer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AltComplianceError(占位 ZA-ALT-UNREGISTERED-ALT-COMPLIANCE)——四要素空白/source_id空白/重复登记/清单空白/未知source/审查项不齐/证据空白/禁用未知源/interval非正/状态冲突时抛
# [TESTS] tests/alt_data/test_alt_data_compliance_reviewer.py
# [A_module] module_id=MOD-ALT-015 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AltDataComplianceReviewer — 另类数据合规审查器（MOD-ALT-015）。

B13-04283（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-016，A3
D-ALT-DATA-14）：数据源合规台账——**四要素登记**（采集方式/ToS 条款/许可
范围/隐私影响）+ 上线前**审查清单逐项判定**（每项含证据字段）+ **定期复核
提醒**（注入时钟）+ 合规**白名单**与**禁用源清单**输出 + **审查记录留痕**。
canonical 承接 TESTA-020 归并。

查重分工（蓝图 §0）：compliance/compliance_log=合规审计日志持久化（本件=
审查判定核心与名单输出，不 import 不重建日志实现，仅产生审查事件可注入
回调）；本件不做采集（在 connector 族），仅做数据源准入前合规判定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: checklist 参数
#   fields: 参数 checklist（无注解）
#   code: alt_data_compliance_reviewer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: review_interval_days 参数
#   fields: 参数 review_interval_days（无注解）
#   code: alt_data_compliance_reviewer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: alt_data_compliance_reviewer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AltDataComplianceReviewer
#   name_en: AltDataComplianceReviewer
#   intro: 另类数据合规审查器（四要素 + 清单审查 + 复核 + 白名单/禁用清单）。
#   desc: 另类数据合规审查器（四要素 + 清单审查 + 复核 + 白名单/禁用清单）。；公共方法（定义序）: register, review, ban, pending_reviews, whitelist, blacklis…
#   inputs: checklist review_interval_days clock
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: AltDataComplianceReviewer
#   downstream: 运行时装配批（数据源上线前接 alt_data_connector 准入 / 白名单输出接健康度管理器准入 / 审查记录接 compliance_log 路由）
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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AltComplianceError",
    "AltDataComplianceReviewer",
    "ComplianceRecord",
    "ReviewRecord",
    "SourceStatus",
]


class AltComplianceError(Exception):
    """合规审查输入/配置/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-ALT-COMPLIANCE。
    """


class SourceStatus(str, Enum):
    """数据源合规状态（生命周期）。"""

    PENDING = "pending"  # 已登记四要素，待审查
    APPROVED = "approved"  # 清单全部通过
    BANNED = "banned"  # 禁用（不论清单结果）
    EXPIRED = "expired"  # 审查过期（需定期复核）


@dataclass(frozen=True)
class ComplianceRecord:
    """四要素台账登记（frozen）。"""

    source_id: str
    collection_method: str
    tos_terms: str
    license_scope: str
    privacy_impact: str
    registered_at: datetime.datetime


@dataclass(frozen=True)
class ReviewRecord:
    """单次审查留痕（frozen）。"""

    source_id: str
    results: tuple[tuple[str, bool, str], ...]  # (item_id, passed, evidence)
    overall_passed: bool
    reviewed_at: datetime.datetime


class AltDataComplianceReviewer:
    """另类数据合规审查器（四要素 + 清单审查 + 复核 + 白名单/禁用清单）。"""

    def __init__(
        self,
        *,
        checklist: Sequence[str],
        review_interval_days: int = 90,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not checklist:
            raise AltComplianceError("审查清单为空（上线前须逐项判定）")
        seen: set[str] = set()
        for item in checklist:
            if not item or not str(item).strip():
                raise AltComplianceError("审查清单含空白项")
            if item in seen:
                raise AltComplianceError(f"审查清单项重复: {item!r}")
            seen.add(item)
        if review_interval_days <= 0:
            raise AltComplianceError(f"review_interval_days 非正: {review_interval_days!r}")
        self._checklist: tuple[str, ...] = tuple(seen)
        self._interval = int(review_interval_days)
        self._clock = clock or datetime.datetime.now
        self._records: dict[str, ComplianceRecord] = {}
        self._status: dict[str, SourceStatus] = {}
        self._reviews: dict[str, list[ReviewRecord]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _known(self, source_id: str) -> None:
        if source_id not in self._records:
            raise AltComplianceError(f"未知数据源: {source_id!r}（未登记四要素）")

    def _ensure_not_banned(self, source_id: str) -> None:
        if self._status.get(source_id) is SourceStatus.BANNED:
            raise AltComplianceError(f"数据源 {source_id!r} 已禁用，禁止再次审查")

    def _status_effective(self, source_id: str) -> SourceStatus:
        """当前有效状态（过期自动降级 EXPIRED）。"""
        st = self._status[source_id]
        if st is not SourceStatus.APPROVED:
            return st
        reviews = self._reviews.get(source_id)
        if not reviews:
            return SourceStatus.PENDING
        latest = reviews[-1].reviewed_at
        if (self._clock() - latest).days > self._interval:
            return SourceStatus.EXPIRED
        return SourceStatus.APPROVED

    # ── 四要素登记 ────────────────────────────────────────────────────────

    def register(
        self,
        source_id: str,
        *,
        collection_method: str,
        tos_terms: str,
        license_scope: str,
        privacy_impact: str,
    ) -> ComplianceRecord:
        """登记四要素台账（source_id 唯一；四要素非空）。"""
        if not source_id or not source_id.strip():
            raise AltComplianceError("source_id 空白")
        if source_id in self._records:
            raise AltComplianceError(f"source_id 重复: {source_id!r}")
        for name, val in (
            ("collection_method", collection_method),
            ("tos_terms", tos_terms),
            ("license_scope", license_scope),
            ("privacy_impact", privacy_impact),
        ):
            if not val or not str(val).strip():
                raise AltComplianceError(f"{name} 空白: {source_id!r}")
        rec = ComplianceRecord(
            source_id=source_id,
            collection_method=collection_method,
            tos_terms=tos_terms,
            license_scope=license_scope,
            privacy_impact=privacy_impact,
            registered_at=self._clock(),
        )
        self._records[source_id] = rec
        self._status[source_id] = SourceStatus.PENDING
        self._reviews[source_id] = []
        return rec

    # ── 审查清单逐项判定 ──────────────────────────────────────────────────

    def review(
        self,
        source_id: str,
        *,
        results: Mapping[str, tuple[bool, str]],
    ) -> ReviewRecord:
        """上线前审查：清单逐项判定 + 证据（须完全闭合）。"""
        self._known(source_id)
        self._ensure_not_banned(source_id)
        if not isinstance(results, Mapping):
            raise AltComplianceError(f"results 非映射: {type(results)!r}")
        if set(results) != set(self._checklist):
            missing = set(self._checklist) - set(results)
            extra = set(results) - set(self._checklist)
            raise AltComplianceError(f"审查项不齐: 缺 {missing!r} 多 {extra!r}")
        clean: list[tuple[str, bool, str]] = []
        for item in self._checklist:
            passed, evidence = results[item]
            if not isinstance(evidence, str) or not evidence.strip():
                raise AltComplianceError(f"审查项 {item!r} 证据空白: {source_id!r}")
            clean.append((item, bool(passed), evidence.strip()))
        overall = all(p for _, p, _ in clean)
        record = ReviewRecord(
            source_id=source_id,
            results=tuple(clean),
            overall_passed=overall,
            reviewed_at=self._clock(),
        )
        self._reviews[source_id].append(record)
        new_status = SourceStatus.APPROVED if overall else SourceStatus.PENDING
        self._status[source_id] = new_status
        _log.info("合规审查: %s -> %s（overall=%s）", source_id, new_status.value, overall)
        return record

    # ── 禁用 / 定期复核提醒 ───────────────────────────────────────────────

    def ban(self, source_id: str) -> None:
        """强制禁用数据源（禁用态不审查、不列入白名单）。"""
        self._known(source_id)
        self._status[source_id] = SourceStatus.BANNED
        _log.warning("数据源被禁用: %s", source_id)

    def pending_reviews(self) -> tuple[str, ...]:
        """需复核的数据源清单（当前时钟下 APPROVED 但已过 interval 者）。"""
        out: list[str] = []
        for sid, st in self._status.items():
            if st is not SourceStatus.APPROVED:
                continue
            reviews = self._reviews.get(sid, ())
            if not reviews:
                continue
            latest = reviews[-1].reviewed_at
            if (self._clock() - latest).days > self._interval:
                out.append(sid)
        return tuple(sorted(out))

    # ── 白名单 / 禁用清单输出 ──────────────────────────────────────────────

    def whitelist(self) -> tuple[str, ...]:
        """合规白名单（已批准且审查未过期）。"""
        out = [sid for sid in self._records if self._status_effective(sid) is SourceStatus.APPROVED]
        return tuple(sorted(out))

    def blacklist(self) -> tuple[str, ...]:
        """禁用源清单。"""
        return tuple(sorted(sid for sid, st in self._status.items() if st is SourceStatus.BANNED))

    # ── 查询 ─────────────────────────────────────────────────────────────

    def status_of(self, source_id: str) -> SourceStatus:
        """当前有效状态（含过期自动降级）。"""
        self._known(source_id)
        return self._status_effective(source_id)

    def record_of(self, source_id: str) -> ComplianceRecord:
        """四要素台账（未知 → Fail-Closed）。"""
        self._known(source_id)
        return self._records[source_id]

    def review_history(self, source_id: str) -> tuple[ReviewRecord, ...]:
        """审查记录留痕（按时间顺序）。"""
        self._known(source_id)
        return tuple(self._reviews[source_id])

    def sources(self) -> tuple[str, ...]:
        """全部已登记数据源（确定性排序）。"""
        return tuple(sorted(self._records))
