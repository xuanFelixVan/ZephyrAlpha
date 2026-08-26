# [BLUEPRINT] MOD-KNW-011 | docs/03_modules/_domain_knowledge/research_project_aggregate/blueprint.md
# [MODULE] zephyr.knowledge.research_project_aggregate
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（聚合核心纯内存；SQLite 连接/时钟/联动适配器 全注入）
# [CONSUMERS] 运行时装配批（研究项目建模 / hypothesis_registry 等联动注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态机四态闭合(draft→active→review→archived; review→active 退回返修; archived 终态); 子实体四类闭合(hypothesis|evidence|experiment|factor); 同 (project,kind,ref_id) 重挂版本严格+1; 项目每次变更 version 递增; archived 禁止挂载; SQLite 持久化经注入连接; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/research_project_aggregate/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResearchProjectError(占位 ZA-KNW-UNREGISTERED-RESEARCH-PROJECT)——连接缺失/未知项目/非法状态迁移/非法子实体/重复项目时抛
# [TESTS] tests/knowledge/test_research_project_aggregate.py
# [A_module] module_id=MOD-KNW-011 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ResearchProjectAggregate — 研究项目聚合根（MOD-KNW-011）。

B6-08533（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-014，B6）：
ResearchProject **聚合根**——project_id + 状态机（draft→active→review→
archived 四态闭合，review→active 退回返修）+ 关联**假设/证据/实验/因子产
出**四类子实体挂载（版本不变量：同引用重挂版本严格 +1）+ SQLite 持久化
（注入连接）+ 与 hypothesis_registry / evidence_chain /
experiment_tracking / 因子库**联动接口**（注入适配器，挂载即回调）。

查重分工（蓝图 §0）：hypothesis_registry=假设自身登记与生命周期（本件只
挂引用不重建登记）；evidence_chain=证据链不可变追加（本件只挂引用）；
experiment_tracking=实验运行记录（本件只挂引用）；knowledge_artifact_store
=6 类产出不可变工件（本件=项目维度聚合视图）。纯内存/DI，不触网不起子进程。
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChildKind",
    "ChildRef",
    "ProjectStatus",
    "ProjectView",
    "ResearchProjectAggregate",
    "ResearchProjectError",
]


class ResearchProjectError(Exception):
    """研究项目聚合输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-RESEARCH-PROJECT。
    """


class ProjectStatus(str, Enum):
    """项目状态机（四态闭合）。"""

    DRAFT = "draft"
    ACTIVE = "active"
    REVIEW = "review"
    ARCHIVED = "archived"


#: 合法迁移表：draft→active→review→archived；review→active 退回返修；archived 终态
_ALLOWED_TRANSITIONS: Final[dict[ProjectStatus, frozenset[ProjectStatus]]] = {
    ProjectStatus.DRAFT: frozenset({ProjectStatus.ACTIVE}),
    ProjectStatus.ACTIVE: frozenset({ProjectStatus.REVIEW}),
    ProjectStatus.REVIEW: frozenset({ProjectStatus.ARCHIVED, ProjectStatus.ACTIVE}),
    ProjectStatus.ARCHIVED: frozenset(),
}


class ChildKind(str, Enum):
    """子实体类型（四类闭合）。"""

    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    EXPERIMENT = "experiment"
    FACTOR = "factor"


@dataclass(frozen=True)
class ChildRef:
    """子实体挂载引用（frozen；version 随重挂递增）。"""

    kind: ChildKind
    ref_id: str
    version: int
    note: str
    attached_at: datetime.datetime


@dataclass(frozen=True)
class ProjectView:
    """项目视图（frozen）。"""

    project_id: str
    name: str
    status: ProjectStatus
    version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


#: 联动适配器签名：adapter(project_id, child_ref) -> None（异常仅告警不阻断）
LinkageAdapter = Callable[[str, ChildRef], None]

_SCHEMA: Final = """
CREATE TABLE IF NOT EXISTS research_projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_project_children (
    project_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    ref_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    note TEXT NOT NULL,
    attached_at TEXT NOT NULL,
    PRIMARY KEY (project_id, kind, ref_id)
);
"""

_TS_FMT: Final = "%Y-%m-%dT%H:%M:%S.%f"


def _ts(dt: datetime.datetime) -> str:
    return dt.strftime(_TS_FMT)


def _parse(ts: str) -> datetime.datetime:
    return datetime.datetime.strptime(ts, _TS_FMT)


class ResearchProjectAggregate:
    """研究项目聚合根（状态机 + 子实体挂载 + SQLite 持久化 + 联动）。"""

    def __init__(
        self,
        *,
        conn: sqlite3.Connection | None,
        clock: Callable[[], datetime.datetime] | None = None,
        hypothesis_registry: LinkageAdapter | None = None,
        evidence_chain: LinkageAdapter | None = None,
        experiment_tracker: LinkageAdapter | None = None,
        factor_sink: LinkageAdapter | None = None,
    ) -> None:
        if conn is None:
            raise ResearchProjectError("sqlite 连接未注入（聚合根持久化强制经注入连接）")
        self._conn = conn
        self._clock = clock or datetime.datetime.now
        self._linkage: dict[ChildKind, LinkageAdapter | None] = {
            ChildKind.HYPOTHESIS: hypothesis_registry,
            ChildKind.EVIDENCE: evidence_chain,
            ChildKind.EXPERIMENT: experiment_tracker,
            ChildKind.FACTOR: factor_sink,
        }
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _row(self, project_id: str) -> sqlite3.Row | tuple:
        if not project_id:
            raise ResearchProjectError("project_id 为空")
        row = self._conn.execute(
            "SELECT project_id, name, status, version, created_at, updated_at "
            "FROM research_projects WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            raise ResearchProjectError(f"未知研究项目: {project_id!r}")
        return row

    @staticmethod
    def _view(row) -> ProjectView:
        return ProjectView(
            project_id=row[0], name=row[1], status=ProjectStatus(row[2]),
            version=int(row[3]), created_at=_parse(row[4]), updated_at=_parse(row[5]),
        )

    def _bump(self, project_id: str, now: datetime.datetime) -> None:
        self._conn.execute(
            "UPDATE research_projects SET version = version + 1, updated_at = ? "
            "WHERE project_id = ?",
            (_ts(now), project_id),
        )

    # ── 项目生命周期 ───────────────────────────────────────────────────────

    def create_project(self, project_id: str, name: str, *, description: str = "") -> ProjectView:
        """建项：draft/v1；重复 project_id → Fail-Closed。"""
        if not project_id:
            raise ResearchProjectError("project_id 为空")
        if not name:
            raise ResearchProjectError("项目名称为空")
        exists = self._conn.execute(
            "SELECT 1 FROM research_projects WHERE project_id = ?", (project_id,)
        ).fetchone()
        if exists is not None:
            raise ResearchProjectError(f"project_id 重复: {project_id!r}")
        now = self._clock()
        self._conn.execute(
            "INSERT INTO research_projects "
            "(project_id, name, status, version, created_at, updated_at) "
            "VALUES (?, ?, ?, 1, ?, ?)",
            (project_id, name, ProjectStatus.DRAFT.value, _ts(now), _ts(now)),
        )
        self._conn.commit()
        _log.info("研究项目建档: %s (%s)", project_id, name)
        return self.get_project(project_id)

    def get_project(self, project_id: str) -> ProjectView:
        """项目查询（未知 → Fail-Closed）。"""
        return self._view(self._row(project_id))

    def list_projects(self, *, status: ProjectStatus | None = None) -> tuple[ProjectView, ...]:
        """项目列表（按 project_id 确定性排序；可按状态过滤）。"""
        if status is not None and not isinstance(status, ProjectStatus):
            raise ResearchProjectError(f"非法项目状态: {status!r}")
        if status is None:
            rows = self._conn.execute(
                "SELECT project_id, name, status, version, created_at, updated_at "
                "FROM research_projects ORDER BY project_id"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT project_id, name, status, version, created_at, updated_at "
                "FROM research_projects WHERE status = ? ORDER BY project_id",
                (status.value,),
            ).fetchall()
        return tuple(self._view(r) for r in rows)

    def transition(self, project_id: str, to_status: ProjectStatus) -> ProjectView:
        """状态迁移：非法迁移/同态迁移 → Fail-Closed。"""
        if not isinstance(to_status, ProjectStatus):
            raise ResearchProjectError(f"非法项目状态: {to_status!r}")
        view = self._view(self._row(project_id))
        if to_status not in _ALLOWED_TRANSITIONS[view.status]:
            raise ResearchProjectError(
                f"非法状态迁移: {project_id!r} {view.status.value} -> {to_status.value}"
                "（合法: draft→active→review→archived；review→active 返修）"
            )
        now = self._clock()
        self._conn.execute(
            "UPDATE research_projects SET status = ?, version = version + 1, updated_at = ? "
            "WHERE project_id = ?",
            (to_status.value, _ts(now), project_id),
        )
        self._conn.commit()
        _log.info("项目状态迁移: %s %s -> %s", project_id, view.status.value, to_status.value)
        return self.get_project(project_id)

    # ── 子实体挂载（版本不变量） ────────────────────────────────────────────

    def attach_child(
        self,
        project_id: str,
        kind: ChildKind,
        ref_id: str,
        *,
        note: str = "",
    ) -> ChildRef:
        """挂载子实体：archived 禁挂；同引用重挂版本严格 +1；联动回调。"""
        if not isinstance(kind, ChildKind):
            raise ResearchProjectError(f"非法子实体类型: {kind!r}（四类闭合）")
        if not ref_id:
            raise ResearchProjectError("ref_id 为空")
        view = self._view(self._row(project_id))
        if view.status is ProjectStatus.ARCHIVED:
            raise ResearchProjectError(f"项目已归档，禁止挂载子实体: {project_id!r}")
        prev = self._conn.execute(
            "SELECT version FROM research_project_children "
            "WHERE project_id = ? AND kind = ? AND ref_id = ?",
            (project_id, kind.value, ref_id),
        ).fetchone()
        version = 1 if prev is None else int(prev[0]) + 1
        now = self._clock()
        self._conn.execute(
            "INSERT OR REPLACE INTO research_project_children "
            "(project_id, kind, ref_id, version, note, attached_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, kind.value, ref_id, version, note, _ts(now)),
        )
        self._bump(project_id, now)
        self._conn.commit()
        child = ChildRef(kind=kind, ref_id=ref_id, version=version, note=note, attached_at=now)
        adapter = self._linkage.get(kind)
        if adapter is not None:
            try:
                adapter(project_id, child)
            except Exception:  # noqa: BLE001 — 联动异常仅告警不阻断（蓝图 §1）
                _log.exception("联动适配器失败: %s -> %s/%s", project_id, kind.value, ref_id)
        return child

    def children_of(
        self,
        project_id: str,
        *,
        kind: ChildKind | None = None,
    ) -> tuple[ChildRef, ...]:
        """子实体视图（按 (kind, ref_id) 确定性排序）。"""
        if kind is not None and not isinstance(kind, ChildKind):
            raise ResearchProjectError(f"非法子实体类型: {kind!r}")
        self._row(project_id)
        if kind is None:
            rows = self._conn.execute(
                "SELECT kind, ref_id, version, note, attached_at "
                "FROM research_project_children WHERE project_id = ? "
                "ORDER BY kind, ref_id",
                (project_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT kind, ref_id, version, note, attached_at "
                "FROM research_project_children WHERE project_id = ? AND kind = ? "
                "ORDER BY kind, ref_id",
                (project_id, kind.value),
            ).fetchall()
        return tuple(
            ChildRef(
                kind=ChildKind(r[0]), ref_id=r[1], version=int(r[2]),
                note=r[3], attached_at=_parse(r[4]),
            )
            for r in rows
        )

    def child_version(self, project_id: str, kind: ChildKind, ref_id: str) -> int:
        """单引用当前挂载版本（未挂载 → Fail-Closed）。"""
        if not isinstance(kind, ChildKind):
            raise ResearchProjectError(f"非法子实体类型: {kind!r}")
        self._row(project_id)
        row = self._conn.execute(
            "SELECT version FROM research_project_children "
            "WHERE project_id = ? AND kind = ? AND ref_id = ?",
            (project_id, kind.value, ref_id),
        ).fetchone()
        if row is None:
            raise ResearchProjectError(
                f"子实体未挂载: {project_id!r} {kind.value}/{ref_id!r}"
            )
        return int(row[0])
