# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §7 写入 API 契约 + 13_exam_backfill_loop_design.md §1.5（状态机）
# [MODULE] zephyr.governance.meta_question.exam_ops
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc); zephyr.shared.io.yaml_utils (load_vocabulary_values，五份词表 yaml 同源动态加载)
# [CONSUMERS] zephyr.governance.meta_question.meta_question_registry（MetaQuestionRegistry 继承本 Mixin 获得考试生命周期方法，并回 import 本模块异常/词表常量/审计事件对象/SQL；第三方 import 自 registry 经其 re-export 兼容）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本模块=NO-GOD-CLASS 拆分件（st-metaq-20260923）：承载 registry.py 原考试生命周期簇 10 方法（transition/_is_legal_edge/_transition_event/claim/release_claim/record_exam_result/_write_audit/_append_jsonl/_load_row/_check_claim）+ 其专属常量 + meta_question 族异常；
#              方法体逐字节原样迁移：SQL 字符串、审计 JSONL 键序、双 now_utc() 调用序、LEGAL_TRANSITIONS 边表内容全部未动；
#              审计 what 全部取自 20§2.1 四族 SSOT 词表（AUDIT_WHAT_VOCAB），禁另立枚举；
#              时间一律 now_utc()（UTC aware timestamptz 口径），禁裸 datetime.now()；
#              PG 行写一律乐观锁 UPDATE...WHERE version=:expected，零行命中=VersionConflictError（禁 SELECT 后裸 UPDATE）；
#              认领鉴权：活跃租约内须 claimed_by==actor，Max/Owner 可越过（BYPASS_ACTORS）
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md §7 + 13_exam_backfill_loop_design.md §1.5 + 20_management_policy.md §2/§3（改契约先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验失败=QuestionValidationError(subcode, details)（subcode 机读 snake_case，对齐 10§7.2 错误码表）；
#                  乐观锁零行命中=VersionConflictError(q_id, expected_version)（调用方重读重放，20§3.2）；
#                  连接失败/SQL 错误=原样上抛（fail-closed，禁降级直写）；
#                  audit what 不在 SSOT 词表=ValueError（写入前硬拦，防词表漂移）
# [TESTS] tests/governance/meta_question/test_registry.py（经 MetaQuestionRegistry 继承链路行使，零改动）
# [TTL] permanent
"""exam_ops — MetaQuestionRegistry 考试生命周期簇 Mixin（状态流转/认领/考试记账 + 审计双轨）。

NO-GOD-CLASS 拆分件：原 ``registry.py`` 的考试生命周期簇方法整体迁入本 Mixin（方法体
逐字节未动），``MetaQuestionRegistry`` 改为继承本类获得同名方法，公共 API 零变化。
异常（QuestionValidationError/VersionConflictError）、审计事件参数对象与考试簇专属
常量/SQL 定义于本模块，由 ``registry.py`` 回 import（第三方 ``from ...registry import``
兼容面不变）。

宿主约定（Mixin 无 ``__init__``，依赖承载类提供）::

    self.schema             # 目标 schema（{{s}} 占位）
    self._conn(*, read_only)  # 连接获取
    self.audit_jsonl_path   # 审计 JSONL 双轨路径（None=只写 PG 审计表）
# #
# # 边:
# # I1 -.->|断点| F1
# # I2 -.->|断点| F1
# # I3 -.->|断点| F1
# # I4 -.->|断点| F1
# # F1 --> A1
# # A1 --> O1
# [/ALGO_FLOW]
# target: src/zephyr/governance/meta_question/exam_ops.py (docstring 1597 字, 14 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/exam_ops.yaml
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Final

from zephyr.shared.io.yaml_utils import load_vocabulary_values
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "AUDIT_WHAT_VOCAB",
    "BYPASS_ACTORS",
    "LEGAL_TRANSITIONS",
    "MetaQuestionAuditEvent",
    "MetaQuestionExamMixin",
    "QuestionValidationError",
    "TERMINAL_STATUSES",
    "VALID_OUTCOMES",
    "VALID_STATUSES",
    "VersionConflictError",
    "WILDCARD_TARGETS",
]

# ---------------------------------------------------------------------------
# 词表与枚举（SSOT：20_management_policy.md §2.1 / 10_intake_gate_design.md §3；
# 与 registry.py 各自同源动态加载同一 yaml，值恒等）
# ---------------------------------------------------------------------------

#: 审计 what 全族 SSOT 词表（登记/intake/blind/exam 四族，禁另立枚举）
AUDIT_WHAT_VOCAB: Final[frozenset[str]] = frozenset(
    {
        # 登记族
        "register",
        "update",
        "merge",
        "retire",
        "reexam",
        "suspend",
        "template_add",
        "template_update",
        "template_retire",
        "board_config",
        "read",
        # intake 族
        "intake_submit",
        "intake_reject",
        "intake_rate_limited",
        "intake_override",
        "dedup_hit",
        "degraded_check",
        # blind 族
        "intake_blind_park",
        "blind_promote",
        "blind_retire",
        # exam 族
        "exam_writeback",
        "exam_contradiction_case",
        "exam_arbitrate",
    }
)

VALID_STATUSES: Final[tuple[str, ...]] = tuple(load_vocabulary_values("meta_question_statuses_vocabulary.yaml"))
VALID_OUTCOMES: Final[tuple[str, ...]] = tuple(load_vocabulary_values("meta_question_outcomes_vocabulary.yaml"))

#: 状态机合法边（硬编码自 13§1.5 九流转 + 10§7.4 前半段两流转 + 10§6.3 盲册晋级边）
LEGAL_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "draft": frozenset({"registered"}),  # 入库（20§1 行 2）
    "registered": frozenset({"mining"}),  # 开工（10§7.4）
    "mining": frozenset({"in_exam"}),  # 开考（10§7.4）
    "in_exam": frozenset({"answered", "reexam", "suspended"}),  # 13§1.5
    "answered": frozenset({"reexam", "suspended"}),  # 13§1.5（复考逾期/连败挂起）
    "reexam": frozenset({"answered", "suspended"}),  # 13§2.2 三取二转 answered/复考失败挂起
    "suspended": frozenset({"registered", "reexam"}),  # 13§1.5 唤醒边/挂起原因消除
    "blinded": frozenset({"registered"}),  # 10§6.3 盲册晋级（blind_promote）
    "merged": frozenset(),  # 终态（墓碑不复用）
    "retired": frozenset(),  # 终态（墓碑不复用）
}
#: 通配边（13§1.5 任意→合并/任意→退役；终态除外）
TERMINAL_STATUSES: Final[frozenset[str]] = frozenset(s for s, ts in LEGAL_TRANSITIONS.items() if not ts)
WILDCARD_TARGETS: Final[frozenset[str]] = (
    TERMINAL_STATUSES  # 通配边目标=终态集（13§1.5 任意→合并/退役，动态派生禁字面量）
)

#: 流转目标态 → 审计 what（20§2.1 SSOT 词表内映射；mining/in_exam 无专名词，取登记族 update）
_STATUS_TO_AUDIT_EVENT: Final[dict[str, str]] = {
    "registered": "register",
    "mining": "update",
    "in_exam": "update",
    "answered": "exam_writeback",
    "reexam": "reexam",
    "suspended": "suspend",
    "merged": "merge",
    "retired": "retire",
}

#: record_exam_result 的 outcome → 允许的起始状态（13§1.5/§2.2 机械触发）
OUTCOME_FROM_STATUSES: Final[dict[str, frozenset[str]]] = {
    "answered": frozenset({"in_exam", "reexam"}),
    "reexam": frozenset({"in_exam", "answered"}),
    "suspended": frozenset({"in_exam", "answered"}),
}

#: 可越过认领鉴权的角色（10§7.4① Max/Owner 可越过）
BYPASS_ACTORS: Final[frozenset[str]] = frozenset({"Max", "Owner"})


class QuestionValidationError(Exception):
    """入库/操作校验失败（subcode 机读 snake_case，对齐 10§7.2 错误码风格）。"""

    def __init__(self, subcode: str, details: dict[str, Any] | None = None) -> None:
        self.subcode = subcode
        self.details = dict(details or {})
        super().__init__(f"{subcode}: {self.details}" if self.details else subcode)


class VersionConflictError(Exception):
    """乐观锁冲突（20§3.2：零行命中=冲突，调用方重读重放）。"""

    def __init__(self, q_id: str, expected_version: int) -> None:
        self.q_id = q_id
        self.expected_version = expected_version
        super().__init__(f"version_conflict: q_id={q_id} expected_version={expected_version}")


@dataclass
class MetaQuestionAuditEvent:
    """审计事件参数对象（20§2.1/§2.2 单条审计载荷）。

    COMPLEXITY 内收：``_write_audit`` 参数对象化（原 cur 外 8 参>7 上限），
    字段语义与原关键字参数一一对应（evidence 默认空串/diff 默认 None 不变）。
    """

    q_id: str
    actor: str
    what: str
    before: dict[str, Any] | None
    after: dict[str, Any] | None
    evidence: str = ""
    diff: list[dict[str, Any]] | None = None


def _as_json(value: Any) -> Any:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    """dict/list → JSON 字符串（PG jsonb 隐式 cast / SQLite TEXT 通吃）；其余原样。"""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _as_datetime(value: Any) -> datetime | None:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
    """DB 取回的时间统一转 aware datetime（PG 返回 datetime / SQLite 适配器返回 str）。"""
    if value is None or isinstance(value, datetime):
        return value
    parsed = datetime.fromisoformat(str(value))
    if parsed.tzinfo is None:
        raise ValueError(f"naive datetime from db: {value!r}（RULE-SCHEMA-TZ：禁无时区时间）")
    return parsed


# ---------------------------------------------------------------------------
# SQL（%s 占位符 psycopg2 口径；测试侧 SQLite wrapper 做 %s→? 翻译）
# ---------------------------------------------------------------------------

_MAIN_COLUMNS: Final[tuple[str, ...]] = (
    "q_id",
    "title",
    "layer",
    "line_ref",
    "graph_ref",
    "data_sources",
    "exam_plan",
    "consumers",
    "frequency",
    "pit_proof",
    "status",
    "parent_id",
    "merged_into",
    "provenance",
    "net_zero_note",
    "chain_refs",
    "evidence_refs",
    "last_exam",
    "priority_score",
    "priority_updated_at",
    "claimed_by",
    "claimed_until",
    "version",
    "created_at",
    "updated_at",
)

_SQL_LOAD_ROW = "SELECT {cols} FROM {{s}}.meta_question WHERE q_id = %s".format(cols=", ".join(_MAIN_COLUMNS))
_SQL_TRANSITION = (
    "UPDATE {s}.meta_question SET status = %s, updated_at = %s, version = version + 1 WHERE q_id = %s AND version = %s"
)
_SQL_EXAM_WRITEBACK = (
    "UPDATE {s}.meta_question SET status = %s, last_exam = %s, updated_at = %s, version = version + 1 "
    "WHERE q_id = %s AND version = %s"
)
_SQL_CLAIM = (
    "UPDATE {s}.meta_question SET claimed_by = %s, claimed_until = %s, updated_at = %s "
    "WHERE q_id = %s AND (claimed_by IS NULL OR claimed_until < %s)"
)
_SQL_RELEASE_CLAIM = (
    "UPDATE {s}.meta_question SET claimed_by = NULL, claimed_until = NULL, updated_at = %s "
    "WHERE q_id = %s AND claimed_by IS NOT NULL"
)
_SQL_INSERT_EXAM_RESULT = (
    "INSERT INTO {s}.meta_question_exam_result "
    "(q_id, exam_ref, conclusion, confidence, data_window, pit_assertion, outcome, recorded_by, created_at) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
)
_SQL_INSERT_AUDIT = (
    # before/after 加双引号：SQLite 侧是触发器关键字，PG 侧引号内小写与 DDL 列名等价
    'INSERT INTO {s}.meta_question_audit (q_id, actor, what, "before", "after", evidence, created_at) '
    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
)


class MetaQuestionExamMixin:
    """考试生命周期簇 Mixin：状态流转/认领/考试记账 + 审计双轨 + 行读取。

    方法体自 ``registry.py`` 逐字节迁移（NO-GOD-CLASS 拆分，st-metaq-20260923）；
    宿主 :class:`MetaQuestionRegistry` 提供.schema/_conn/audit_jsonl_path 承载。
    """

    # -- 状态流转（10§7.4 / 13§1.5 / 20§3.2）--------------------------------

    def transition(self, q_id: str, to_status: str, actor: str, evidence: str = "") -> dict[str, Any]:
        """状态流转端点：认领鉴权→目标态合法（合法边表）→乐观锁 UPDATE→审计落账。

        非法边抛 ``illegal_transition``；乐观锁零行命中抛 :class:`VersionConflictError`
        （调用方重读重放，禁 SELECT 后裸 UPDATE）。
        """
        if to_status not in VALID_STATUSES:
            raise QuestionValidationError("status_invalid", {"to_status": to_status})
        conn = self._conn(read_only=False)
        try:
            cur = conn.cursor()
            row = self._load_row(cur, q_id)
            if row is None:
                raise QuestionValidationError("qid_not_found", {"q_id": q_id})
            self._check_claim(row, actor, action="transition")
            old_status = str(row["status"])
            expected_version = int(row["version"])
            if not self._is_legal_edge(old_status, to_status):
                raise QuestionValidationError("illegal_transition", {"from_status": old_status, "to_status": to_status})
            now = now_utc()
            cur.execute(
                _SQL_TRANSITION.format(s=self.schema),
                (to_status, now, q_id, expected_version),
            )
            if cur.rowcount != 1:
                raise VersionConflictError(q_id, expected_version)
            what = self._transition_event(old_status, to_status)
            diff = [{"field": "status", "old": old_status, "new": to_status}]
            self._write_audit(
                cur,
                MetaQuestionAuditEvent(
                    q_id=q_id,
                    actor=actor,
                    what=what,
                    before={"status": old_status},
                    after={"status": to_status},
                    evidence=evidence,
                    diff=diff,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return {"q_id": q_id, "from_status": old_status, "to_status": to_status}

    @staticmethod
    def _is_legal_edge(from_status: str, to_status: str) -> bool:
        if to_status in LEGAL_TRANSITIONS.get(from_status, frozenset()):
            return True
        return to_status in WILDCARD_TARGETS and from_status not in TERMINAL_STATUSES

    @staticmethod
    def _transition_event(from_status: str, to_status: str) -> str:
        if to_status == "registered" and from_status == "blinded":
            return "blind_promote"  # 10§6.3 盲册晋级
        event = _STATUS_TO_AUDIT_EVENT.get(to_status)
        if not event:
            raise ValueError(f"audit_what_not_in_ssot_vocab:transition->{to_status}")
        return event

    # -- 认领（12§2.1 认领协议 / 20§3 乐观锁外租约闸）------------------------

    def claim(self, q_id: str, actor: str, lease_hours: int = 24) -> dict[str, Any]:
        """认领：仅当 ``claimed_by IS NULL OR claimed_until < now()`` 可认领（互斥租约）。"""
        conn = self._conn(read_only=False)
        try:
            cur = conn.cursor()
            row = self._load_row(cur, q_id)
            if row is None:
                raise QuestionValidationError("qid_not_found", {"q_id": q_id})
            now = now_utc()
            until = now + timedelta(hours=lease_hours)
            cur.execute(_SQL_CLAIM.format(s=self.schema), (actor, until, now, q_id, now))
            if cur.rowcount != 1:
                raise QuestionValidationError(
                    "claim_conflict",
                    {"q_id": q_id, "claimed_by": row.get("claimed_by")},
                )
            diff = [
                {"field": "claimed_by", "old": row.get("claimed_by"), "new": actor},
                {"field": "claimed_until", "old": None, "new": until.isoformat()},
            ]
            self._write_audit(
                cur,
                MetaQuestionAuditEvent(
                    q_id=q_id,
                    actor=actor,
                    what="update",
                    before={"claimed_by": row.get("claimed_by")},
                    after={"claimed_by": actor},
                    evidence=f"lease_hours={lease_hours}",
                    diff=diff,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return {"q_id": q_id, "claimed_by": actor, "claimed_until": until.isoformat()}

    def release_claim(self, q_id: str, actor: str) -> dict[str, Any]:
        """释放认领：仅当前认领人（或 Max/Owner）可释放。"""
        conn = self._conn(read_only=False)
        try:
            cur = conn.cursor()
            row = self._load_row(cur, q_id)
            if row is None:
                raise QuestionValidationError("qid_not_found", {"q_id": q_id})
            holder = row.get("claimed_by")
            if not holder:
                raise QuestionValidationError("claim_not_held", {"q_id": q_id})
            if actor != holder and actor not in BYPASS_ACTORS:
                raise QuestionValidationError("release_not_claimant", {"q_id": q_id, "claimed_by": holder})
            cur.execute(_SQL_RELEASE_CLAIM.format(s=self.schema), (now_utc(), q_id))
            if cur.rowcount != 1:
                raise VersionConflictError(q_id, int(row["version"]))
            diff = [{"field": "claimed_by", "old": holder, "new": None}]
            self._write_audit(
                cur,
                MetaQuestionAuditEvent(
                    q_id=q_id,
                    actor=actor,
                    what="update",
                    before={"claimed_by": holder},
                    after={"claimed_by": None},
                    evidence="release_claim",
                    diff=diff,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return {"q_id": q_id, "released_by": actor}

    # -- 考试记账（13§1 回写契约；R3 独立表）---------------------------------

    def record_exam_result(self, q_id: str, result: dict[str, Any], actor: str) -> dict[str, Any]:
        """考试回填：写 exam_result 独立表 + 按 outcome 流转主表 + 刷 last_exam + 审计。

        回写鉴权=该问当前认领人（13§1；Max/Owner 可越过，无认领/不匹配拒收）。
        outcome→状态联动：answered/reexam/suspended（13§1.5 机械触发）。
        """
        outcome = (result or {}).get("outcome")
        if outcome not in VALID_OUTCOMES:
            raise QuestionValidationError("status_invalid", {"outcome": outcome})
        conn = self._conn(read_only=False)
        try:
            cur = conn.cursor()
            row = self._load_row(cur, q_id)
            if row is None:
                raise QuestionValidationError("qid_not_found", {"q_id": q_id})
            self._check_claim(row, actor, action="exam_writeback")
            old_status = str(row["status"])
            expected_version = int(row["version"])
            if old_status not in OUTCOME_FROM_STATUSES[outcome]:
                raise QuestionValidationError(
                    "status_invalid",
                    {"from_status": old_status, "outcome": outcome},
                )
            now = now_utc()
            cur.execute(
                _SQL_INSERT_EXAM_RESULT.format(s=self.schema),
                (
                    q_id,
                    result.get("exam_ref"),
                    _as_json(result.get("conclusion")),
                    _as_json(result.get("confidence")),
                    _as_json(result.get("data_window")),
                    result.get("pit_assertion"),
                    outcome,
                    actor,
                    now,
                ),
            )
            cur.execute(
                _SQL_EXAM_WRITEBACK.format(s=self.schema),
                (outcome, now, now, q_id, expected_version),
            )
            if cur.rowcount != 1:
                raise VersionConflictError(q_id, expected_version)
            diff = [
                {"field": "status", "old": old_status, "new": outcome},
                {"field": "last_exam", "old": None, "new": now.isoformat()},
            ]
            self._write_audit(
                cur,
                MetaQuestionAuditEvent(
                    q_id=q_id,
                    actor=actor,
                    what="exam_writeback",
                    before={"status": old_status},
                    after={"status": outcome},
                    evidence=str(result.get("exam_ref") or ""),
                    diff=diff,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return {"q_id": q_id, "status": outcome, "last_exam": now.isoformat()}

    # -- 审计双轨（20§2.1/§2.2）----------------------------------------------

    def _write_audit(self, cur: Any, event: MetaQuestionAuditEvent) -> None:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
        """PG 审计行 + JSONL 追加双轨（同事务先账后实由调用方编排顺序保证）。

        COMPLEXITY 内收：载荷经 :class:`MetaQuestionAuditEvent` 参数对象传入（原 8 参>7 上限）。
        """
        if event.what not in AUDIT_WHAT_VOCAB:
            raise ValueError(f"audit_what_not_in_ssot_vocab:{event.what}")
        cur.execute(
            _SQL_INSERT_AUDIT.format(s=self.schema),
            (
                event.q_id,
                event.actor,
                event.what,
                _as_json(event.before),
                _as_json(event.after),
                event.evidence,
                now_utc(),
            ),
        )
        self._append_jsonl(
            {
                "who": event.actor,
                "when": now_utc().isoformat(),
                "what": event.what,
                "object": event.q_id,
                "diff": list(event.diff or []),
                "evidence": event.evidence,
            }
        )

    def _append_jsonl(self, event: dict[str, Any]) -> None:
        """JSONL 追加账（20§2.2：进程外留痕防 PG 单点；照 intake journal append 先例）。"""
        if self.audit_jsonl_path is None:
            return
        path = self.audit_jsonl_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    # -- 行读取 --------------------------------------------------------------

    def _load_row(self, cur: Any, q_id: str) -> dict[str, Any] | None:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
        cur.execute(_SQL_LOAD_ROW.format(s=self.schema), (q_id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row, strict=True))

    @staticmethod
    def _check_claim(row: dict[str, Any], actor: str, *, action: str) -> None:
        """认领鉴权（10§7.4①）：活跃租约内须 claimed_by==actor，Max/Owner 可越过。
        # #
        # # 边:
        # # I1 -.->|断点| F1
        # # I2 -.->|断点| F1
        # # I3 -.->|断点| F1
        # # I4 -.->|断点| F1
        # # F1 --> A1
        # # A1 --> O1
        # [/ALGO_FLOW]
        """
        holder = row.get("claimed_by")
        if not holder:
            return  # 无认领=不拦（认领协议对流转的约束以活跃租约为准）
        until = _as_datetime(row.get("claimed_until"))
        if until is not None and until <= now_utc():
            return  # 租约过期=惰性回收（12§2.1），视同无活跃认领
        if actor == holder or actor in BYPASS_ACTORS:
            return
        raise QuestionValidationError(
            "claim_mismatch", {"q_id": row.get("q_id"), "claimed_by": holder, "action": action}
        )
