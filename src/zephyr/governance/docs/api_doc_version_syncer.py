# [BLUEPRINT] MOD-GOV-054 | docs/03_modules/_domain_governance/api_doc_version_syncer/blueprint.md
# [MODULE] zephyr.governance.docs.api_doc_version_syncer
# [DOMAIN] D_GOV_DOCS
# [DEPENDENCIES] 无（同步核心纯内存；api_scanner/doc_writer/trading_hours/human_confirmer/时钟全注入）
# [CONSUMERS] 运行时装配批（非交易时段同步批：API 扫描器 + 文档写入器 + 时段判定 + 人工确认回调统一注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 变更词表闭合(added|removed|modified); 仅非交易时段可同步(时段判定未注入/交易时段 Fail-Closed); dry-run 先行不写文档; 差异数超阈值须人工确认回调放行; 写入成功后才推进 baseline; 扫描/变更/更新计划全确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_governance/api_doc_version_syncer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ApiDocSyncError(占位 ZA-GOVD-UNREGISTERED-API-DOC-SYNC)——scanner/writer/时段判定未注入/交易时段/非法签名/重复api_id/超阈值未获人工确认/scanner或writer异常/非法阈值时抛
# [TESTS] tests/governance/docs/test_api_doc_version_syncer.py
# [A_module] module_id=MOD-GOV-054 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ApiDocVersionSyncer — API 文档版本同步器（MOD-GOV-054）。

B14-04654（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-REGSYNC-002，A9
XS-15）：扫描 API 版本号与接口签名变更（注入 api_scanner）→ 自动更
新接口文档与 changelog（注入 doc_writer，dry-run 先行）→ 差异超阈
值提醒人工确认 + 非交易时段运行（注入时段判定）。

查重分工（蓝图 §0）：api_index=API 索引真源（本件经注入 scanner 读
取其快照，不重建索引）；changelog_manager=审计 changelog 落证（本件
只经注入 writer 产出更新载荷，不写盘）；doc_drift 检测族=文档漂移
告警（本件=版本/签名驱动的主动同步，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: api_scanner 参数
#   fields: 参数 api_scanner（无注解）
#   code: api_doc_version_syncer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: doc_writer 参数
#   fields: 参数 doc_writer（无注解）
#   code: api_doc_version_syncer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: trading_hours 参数
#   fields: 参数 trading_hours（无注解）
#   code: api_doc_version_syncer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: human_confirmer 参数
#   fields: 参数 human_confirmer（无注解）
#   code: api_doc_version_syncer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ApiDocVersionSyncer
#   name_en: ApiDocVersionSyncer
#   intro: API 文档版本同步器（扫描 → diff → dry-run 计划 → 写文档/changelog）。
#   desc: API 文档版本同步器（扫描 → diff → dry-run 计划 → 写文档/changelog）。；公共方法（定义序）: scan_changes, sync；源码 L159-L335
#   inputs: api_scanner doc_writer trading_hours human_confirmer diff_threshold c…
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: ApiDocVersionSyncer
#   downstream: 运行时装配批（非交易时段同步批：API 扫描器 + 文档写入器 + 时段判定 + 人工确认回调统一注入）
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
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ApiChange",
    "ApiDocSyncError",
    "ApiDocVersionSyncer",
    "ApiSignature",
    "ChangeKind",
    "DocTarget",
    "DocUpdate",
    "SyncResult",
]


class ApiDocSyncError(Exception):
    """API 文档同步输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOVD-UNREGISTERED-API-DOC-SYNC。
    """


class ChangeKind(str, Enum):
    """API 变更类型（词表闭合）。"""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


class DocTarget(str, Enum):
    """文档更新目标（词表闭合）。"""

    DOC = "doc"
    CHANGELOG = "changelog"


@dataclass(frozen=True)
class ApiSignature:
    """API 版本与签名快照（frozen；scanner 产出单元）。"""

    api_id: str
    version: str
    signature: str


@dataclass(frozen=True)
class ApiChange:
    """单条 API 变更（frozen）。"""

    kind: ChangeKind
    api_id: str
    old_version: str
    new_version: str


@dataclass(frozen=True)
class DocUpdate:
    """单条文档更新载荷（frozen；doc_writer 消费单元）。"""

    target: DocTarget
    path: str
    content: str


@dataclass(frozen=True)
class SyncResult:
    """同步结果（frozen）。

    dry_run=True 时 updates 为计划预览且 applied=False；
    dry_run=False 且 applied=True 时 updates 已经 doc_writer 落写。
    """

    dry_run: bool
    changes: tuple[ApiChange, ...]
    updates: tuple[DocUpdate, ...]
    applied: bool


class ApiDocVersionSyncer:
    """API 文档版本同步器（扫描 → diff → dry-run 计划 → 写文档/changelog）。"""

    def __init__(
        self,
        *,
        api_scanner: Callable[[], Iterable[ApiSignature]] | None = None,
        doc_writer: Callable[[DocUpdate], None] | None = None,
        trading_hours: Callable[[], bool] | None = None,
        human_confirmer: Callable[[tuple[ApiChange, ...]], bool] | None = None,
        diff_threshold: int = 5,
        changelog_path: str = "CHANGELOG.md",
        baseline: Mapping[str, ApiSignature] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not isinstance(diff_threshold, int) or diff_threshold < 0:
            raise ApiDocSyncError(f"非法差异阈值: {diff_threshold!r}")
        if not changelog_path:
            raise ApiDocSyncError("changelog_path 为空")
        self._scanner = api_scanner
        self._writer = doc_writer
        self._trading_hours = trading_hours
        self._confirmer = human_confirmer
        self._threshold = diff_threshold
        self._changelog_path = changelog_path
        self._clock = clock or datetime.datetime.now
        self._baseline: dict[str, ApiSignature] = dict(baseline or {})

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _scan(self) -> dict[str, ApiSignature]:
        """扫描当前 API 快照（scanner 未注入/异常/非法条目 Fail-Closed）。"""
        if self._scanner is None:
            raise ApiDocSyncError("api_scanner 未注入（无法扫描 API 变更）")
        try:
            raw = list(self._scanner())
        except ApiDocSyncError:
            raise
        except Exception as exc:  # noqa: BLE001 — scanner 异常统一 Fail-Closed
            raise ApiDocSyncError(f"api_scanner 扫描失败: {exc}") from exc
        snapshot: dict[str, ApiSignature] = {}
        for item in raw:
            if not isinstance(item, ApiSignature):
                raise ApiDocSyncError(f"非法扫描条目: {item!r}")
            if not item.api_id or not item.version or not item.signature:
                raise ApiDocSyncError(f"非法 API 签名（空字段）: {item!r}")
            if item.api_id in snapshot:
                raise ApiDocSyncError(f"重复 api_id: {item.api_id!r}")
            snapshot[item.api_id] = item
        return snapshot

    def _build_updates(
        self,
        changes: tuple[ApiChange, ...],
        snapshot: Mapping[str, ApiSignature],
    ) -> tuple[DocUpdate, ...]:
        """由变更清单构建文档 + changelog 更新计划（确定性排序）。"""
        updates: list[DocUpdate] = []
        for change in changes:
            if change.kind is ChangeKind.REMOVED:
                content = f"# {change.api_id}\n\nstatus: removed\n\nlast_version: {change.old_version}\n"
            else:
                version = change.new_version
                signature = snapshot[change.api_id].signature
                content = f"# {change.api_id}\n\nversion: {version}\n\nsignature: `{signature}`\n"
            updates.append(
                DocUpdate(
                    target=DocTarget.DOC,
                    path=f"docs/api/{change.api_id}.md",
                    content=content,
                )
            )
        if changes:
            lines = [f"- {c.api_id}: {c.kind.value} {c.old_version or '-'} -> {c.new_version or '-'}" for c in changes]
            updates.append(
                DocUpdate(
                    target=DocTarget.CHANGELOG,
                    path=self._changelog_path,
                    content=(f"## API 同步 {self._clock().isoformat()}\n\n" + "\n".join(lines) + "\n"),
                )
            )
        return tuple(updates)

    # ── 扫描 diff ─────────────────────────────────────────────────────────

    def _diff(self, snapshot: Mapping[str, ApiSignature]) -> tuple[ApiChange, ...]:
        """快照与 baseline diff（按 api_id 确定性排序）。"""
        changes: list[ApiChange] = []
        for api_id in sorted(set(snapshot) | set(self._baseline)):
            new = snapshot.get(api_id)
            old = self._baseline.get(api_id)
            if old is None and new is not None:
                changes.append(
                    ApiChange(
                        kind=ChangeKind.ADDED,
                        api_id=api_id,
                        old_version="",
                        new_version=new.version,
                    )
                )
            elif new is None and old is not None:
                changes.append(
                    ApiChange(
                        kind=ChangeKind.REMOVED,
                        api_id=api_id,
                        old_version=old.version,
                        new_version="",
                    )
                )
            elif old is not None and new is not None and (old.version, old.signature) != (new.version, new.signature):
                changes.append(
                    ApiChange(
                        kind=ChangeKind.MODIFIED,
                        api_id=api_id,
                        old_version=old.version,
                        new_version=new.version,
                    )
                )
        return tuple(changes)

    def scan_changes(self) -> tuple[ApiChange, ...]:
        """扫描并与 baseline diff（不写文档；按 api_id 确定性排序）。"""
        return self._diff(self._scan())

    # ── 同步 ─────────────────────────────────────────────────────────────

    def sync(self, *, dry_run: bool = True) -> SyncResult:
        """同步：非交易时段门禁 → diff → 超阈值人工确认 → dry-run/落写。"""
        if self._trading_hours is None:
            raise ApiDocSyncError("trading_hours 未注入（无法判定非交易时段）")
        try:
            in_trading = bool(self._trading_hours())
        except Exception as exc:  # noqa: BLE001 — 时段判定异常统一 Fail-Closed
            raise ApiDocSyncError(f"trading_hours 判定失败: {exc}") from exc
        if in_trading:
            raise ApiDocSyncError("交易时段禁止同步（仅非交易时段运行）")

        snapshot = self._scan()
        changes = self._diff(snapshot)
        updates = self._build_updates(changes, snapshot)

        if len(changes) > self._threshold:
            if self._confirmer is None:
                raise ApiDocSyncError(
                    f"差异数 {len(changes)} 超阈值 {self._threshold}，human_confirmer 未注入（须人工确认）"
                )
            try:
                confirmed = bool(self._confirmer(changes))
            except Exception as exc:  # noqa: BLE001 — 确认回调异常按拒绝处理
                raise ApiDocSyncError(f"human_confirmer 确认失败: {exc}") from exc
            if not confirmed:
                raise ApiDocSyncError(f"差异数 {len(changes)} 超阈值 {self._threshold}，人工确认拒绝")

        if dry_run:
            _log.info("API 文档同步 dry-run: %d 变更 / %d 更新", len(changes), len(updates))
            return SyncResult(
                dry_run=True,
                changes=changes,
                updates=updates,
                applied=False,
            )

        if self._writer is None:
            raise ApiDocSyncError("doc_writer 未注入（禁止旁路直写文档）")
        for update in updates:
            try:
                self._writer(update)
            except Exception as exc:  # noqa: BLE001 — writer 异常统一 Fail-Closed
                raise ApiDocSyncError(f"doc_writer 写入失败: {update.path!r}: {exc}") from exc
        self._baseline = snapshot  # 写入成功后才推进 baseline
        _log.info("API 文档同步完成: %d 变更已落写", len(changes))
        return SyncResult(
            dry_run=False,
            changes=changes,
            updates=updates,
            applied=True,
        )
