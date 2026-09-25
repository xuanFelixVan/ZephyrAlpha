# [MODULE] zephyr.governance.registry_ledger.api
# [DOMAIN] D_GOVERNANCE
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [DEPENDENCIES] zephyr.governance.registry_ledger.identity (entry_composite_key); schema (SCHEMA_NAME); depgraph_schema (连接池); psycopg2
# [CONSUMERS] scripts/governance/registry_migration/wave0_phase0_gate.py; 后续落地方 hook/registry 工具改道（W-M1 波次接线）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按条目声明写禁整文件接口（§3.1 负面清单）；CAS 409 拒绝必记事件行；retire 强制 authority_ref；force 需 owner_approval_ref（D-5）
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildA-20260923（W-M1 车道A·波0②）；2026-09-24 wave0 补全头字段+noqa
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 返回码契约 Result.code（§3.2 六码+四码）；编程错误（连接断/坏参数）raise 由调用方兜
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_ledger 意图 API——register/update/retire 按条目声明（W-M1 车道A·波0②）。

接口面负面清单（设计 §3.1）：不提供 write_whole_registry/set_entries 等任何接受
"整册内容"的写接口；退役必须点名条目并附 authority_ref，缺失机械拒绝；系统不存在
"把册里少掉的条目解释为删除"的路径。

结果契约（设计 §3.2，错误码机械可判）：OK/OK_NOOP/CONFLICT_VERSION(409)/
CONFLICT_DUPLICATE(409)/AUTHORITY_REQUIRED/SCHEMA_INVALID/NOT_FOUND/
INVALID_ARGUMENT/FORBIDDEN_FORCE/LEASE_HELD。并发双写败者 CAS 拒绝且拒绝本身记
事件行（detail.conflict=true，设计 §2.3）；force=显式参数+takeover 事件审计，
且需 Owner 批文标记 owner_approval_ref（D-5，high 域门位）。


# [ALGO_FLOW]
层: 输入 → 校验 → 事务 → 输出
- 输入: registry_id/family_key/payload/expected_version/reason/session_id
- 校验: actor_kind 枚举、reason≥10 字、payload 非空 dict、身份键可解析
- 事务: 单连接 insert/update+事件行（register 幂等命中 OK_NOOP；CAS 失败 409 且拒绝记事件）
- 输出: Result(code, entry, event_id, detail)"""

from __future__ import annotations

import contextlib
import hashlib
import json
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Final

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extensions import cursor as PgCursor
from psycopg2.extras import Json

from zephyr.governance.registry_ledger.ledger_identity import entry_composite_key
from zephyr.governance.registry_ledger.registry_ledger_ddl import SCHEMA_NAME

OK = "OK"
OK_NOOP = "OK_NOOP"
CONFLICT_VERSION = "CONFLICT_VERSION"
CONFLICT_DUPLICATE = "CONFLICT_DUPLICATE"
AUTHORITY_REQUIRED = "AUTHORITY_REQUIRED"
SCHEMA_INVALID = "SCHEMA_INVALID"
NOT_FOUND = "NOT_FOUND"
INVALID_ARGUMENT = "INVALID_ARGUMENT"
FORBIDDEN_FORCE = "FORBIDDEN_FORCE"
LEASE_HELD = "LEASE_HELD"

# 共享 SQL 常量（高频复用语句集中化；entry/cols 占位调用侧注入）
_SQL_ENTRY_LAST_EVENT = "UPDATE {entry} SET last_event_id=%s WHERE entry_pk=%s"
_SQL_ENTRY_BY_PK = "SELECT {cols} FROM {entry} WHERE entry_pk=%s"


def _pg_json_dumps(obj: object) -> str:
    """PG jsonb 统一序列化（YAML date/datetime 等标量归一 str，与 payload_sha256 同形态）。"""
    return json.dumps(obj, default=str, ensure_ascii=False)


_HTTP_STATUS: Final = {
    OK: 200,
    OK_NOOP: 200,
    CONFLICT_VERSION: 409,
    CONFLICT_DUPLICATE: 409,
    AUTHORITY_REQUIRED: 403,
    SCHEMA_INVALID: 422,
    NOT_FOUND: 404,
    INVALID_ARGUMENT: 400,
    FORBIDDEN_FORCE: 403,
    LEASE_HELD: 423,
}

ACTOR_KINDS = ("agent", "human", "generator", "system")
LEASE_TTL = timedelta(minutes=30)
MIN_REASON_LEN = 10

_ENTRY_COLS = (
    "entry_pk",
    "registry_id",
    "family_key",
    "entry_key",
    "payload",
    "payload_sha256",
    "version",
    "status",
    "held_by_session",
    "held_at",
    "lease_expires_at",
    "created_by",
    "created_at",
    "updated_by",
    "updated_at",
    "last_event_id",
)


@dataclass
class Result:
    code: str
    entry: dict | None = None
    event_id: int | None = None
    detail: dict = field(default_factory=dict)

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS[self.code]

    @property
    def ok(self) -> bool:
        return self.code in (OK, OK_NOOP)


def canonical_payload_sha256(payload: dict) -> str:
    """规范形内容指纹（sorted keys 紧凑 JSON，幂等判重/死亡证明 final_fingerprint）。"""
    blob = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str
    )  # YAML date/datetime 归一 str，sha 与存储 payload 同形态
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _entry_dict(row: tuple) -> dict:
    return dict(zip(_ENTRY_COLS, row, strict=True))


def _t(name: str, schema: str = SCHEMA_NAME) -> str:
    return f'"{schema}".{name}'


@dataclass
class _Conn:
    conn: PgConnection
    owned: bool


def _conn_ctx(conn: PgConnection) -> _Conn:
    """conn 为空时自管连接（depgraph writer 路径）；传入则共用并统一 commit/rollback。"""
    if conn is not None:
        return _Conn(conn, owned=False)
    return _Conn(_open_default_conn(), owned=True)


def _open_default_conn() -> PgConnection:
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection(read_only=False)


def _release_conn(c: _Conn) -> None:
    if not c.owned:
        return
    # release 兜底：失败降级直接 close；close 再失败静默（清理路径无可恢复动作）
    with contextlib.suppress(Exception):
        from zephyr.governance.depgraph_schema import release_depgraph_pg_connection

        release_depgraph_pg_connection(c.conn)
    with contextlib.suppress(Exception):
        c.conn.close()


def _validate_actor(actor_kind: str) -> None:
    if actor_kind not in ACTOR_KINDS:
        raise ValueError(f"actor_kind must be one of {ACTOR_KINDS}, got {actor_kind!r}")


def _require_reason(reason: str | None, action: str) -> None:
    if not isinstance(reason, str) or len(reason.strip()) < MIN_REASON_LEN:
        raise ValueError(f"{action} requires reason >= {MIN_REASON_LEN} chars (design §2.3), got {reason!r}")


def _record_event(  # noqa: long-param-list  02号文§3.1 意图API签名契约绑定（调用方关键字形态固定）
    cur: PgCursor,
    *,
    registry_id: str,
    family_key: str,
    entry_key: str,
    action: str,
    actor_session: str,
    actor_kind: str,
    after_version: int,
    payload_after: dict,
    base_version: int | None = None,
    before_sha256: str | None = None,
    reason: str | None = None,
    authority_ref: str | None = None,
    detail: dict | None = None,
    schema: str = SCHEMA_NAME,
) -> int:
    cur.execute(
        f"INSERT INTO {_t('registry_event', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
        "(registry_id, family_key, entry_key, action, actor_session, actor_kind, "
        " base_version, after_version, payload_after, before_sha256, reason, "
        " authority_ref, detail) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING event_id",
        (
            registry_id,
            family_key,
            entry_key,
            action,
            actor_session,
            actor_kind,
            base_version,
            after_version,
            Json(payload_after, dumps=_pg_json_dumps),
            before_sha256,
            reason,
            authority_ref,
            Json(detail, dumps=_pg_json_dumps) if detail else None,
        ),
    )
    return int(cur.fetchone()[0])


def register(  # noqa: long-param-list  02号文§3.1 意图API签名契约绑定（调用方关键字形态固定）
    registry_id: str,
    family_key: str,
    payload: dict,
    *,
    reason: str | None = None,
    session_id: str,
    actor_kind: str = "agent",
    conn: PgConnection = None,
    schema: str = SCHEMA_NAME,
) -> Result:
    """登记新条目。同键同指纹=OK_NOOP；同键异指纹=CONFLICT_DUPLICATE(409)+拒绝事件。"""
    _validate_actor(actor_kind)
    if not isinstance(payload, dict) or not payload:
        return Result(SCHEMA_INVALID, detail={"cause": "payload must be a non-empty dict"})
    entry_key = entry_composite_key(payload)
    if entry_key is None:
        return Result(SCHEMA_INVALID, detail={"cause": "identity key unresolvable (non-scalar first field)"})
    sha = canonical_payload_sha256(payload)
    c = _conn_ctx(conn)

    def _t(name: str, _s: str = schema) -> str:
        return f'"{_s}".{name}'

    try:
        with c.conn.cursor() as cur:
            try:
                cur.execute(
                    f"INSERT INTO {_t('registry_entry')} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                    "(registry_id, family_key, entry_key, payload, payload_sha256, "
                    " version, created_by, updated_by) "
                    "VALUES (%s,%s,%s,%s,%s,1,%s,%s) RETURNING entry_pk",
                    (
                        registry_id,
                        family_key,
                        entry_key,
                        Json(payload, dumps=_pg_json_dumps),
                        sha,
                        session_id,
                        session_id,
                    ),
                )
                entry_pk = int(cur.fetchone()[0])
                event_id = _record_event(
                    cur,
                    registry_id=registry_id,
                    schema=schema,
                    family_key=family_key,
                    entry_key=entry_key,
                    action="register",
                    actor_session=session_id,
                    actor_kind=actor_kind,
                    after_version=1,
                    payload_after=payload,
                    reason=reason,
                )
                cur.execute(
                    _SQL_ENTRY_LAST_EVENT.format(entry=_t("registry_entry", schema)),
                    (event_id, entry_pk),
                )
            except psycopg2.errors.ForeignKeyViolation:
                c.conn.rollback()
                return Result(NOT_FOUND, detail={"cause": "registry_catalog row missing"})
            except psycopg2.errors.UniqueViolation:
                c.conn.rollback()
                cur2 = c.conn.cursor()
                try:
                    cur2.execute(
                        f"SELECT payload_sha256, status, version FROM {_t('registry_entry')} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                        "WHERE registry_id=%s AND family_key=%s AND entry_key=%s",
                        (registry_id, family_key, entry_key),
                    )
                    row = cur2.fetchone()
                    if row is None:
                        raise
                    cur_sha, status, version = row
                    if cur_sha == sha and status == "active":
                        c.conn.commit()
                        return Result(OK_NOOP, detail={"entry_key": entry_key, "version": version})
                    event_id = _record_event(
                        cur2,
                        registry_id=registry_id,
                        schema=schema,
                        family_key=family_key,
                        entry_key=entry_key,
                        action="register",
                        actor_session=session_id,
                        actor_kind=actor_kind,
                        base_version=None,
                        after_version=version,
                        payload_after=payload,
                        reason=reason,
                        detail={"conflict": True, "existing_status": status},
                    )
                    c.conn.commit()
                    return Result(
                        CONFLICT_DUPLICATE,
                        detail={
                            "entry_key": entry_key,
                            "existing_status": status,
                            "existing_version": version,
                            "conflict_event_id": event_id,
                        },
                    )
                finally:
                    cur2.close()
            cur.execute(
                _SQL_ENTRY_BY_PK.format(cols=", ".join(_ENTRY_COLS), entry=_t("registry_entry", schema)),
                (entry_pk,),
            )
            row = cur.fetchone()
        c.conn.commit()
        return Result(OK, entry=_entry_dict(row), event_id=event_id)
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.conn.rollback()
        raise
    finally:
        _release_conn(c)


def update(  # noqa: long-param-list  02号文§3.1 意图API签名契约绑定（调用方关键字形态固定）
    registry_id: str,
    family_key: str,
    entry_key: str,
    expected_version: int,
    payload: dict,
    *,
    reason: str,
    session_id: str,
    actor_kind: str = "agent",
    conn: PgConnection = None,
    schema: str = SCHEMA_NAME,
) -> Result:
    """CAS 更新（expected_version 基线不匹配=CONFLICT_VERSION 409，拒绝记事件行）。"""
    _validate_actor(actor_kind)
    _require_reason(reason, "update")
    if not isinstance(expected_version, int) or expected_version < 1:
        raise ValueError(f"expected_version must be int >= 1, got {expected_version!r}")
    if not isinstance(payload, dict) or not payload:
        return Result(SCHEMA_INVALID, detail={"cause": "payload must be a non-empty dict"})
    if entry_composite_key(payload) != entry_key:
        return Result(INVALID_ARGUMENT, detail={"cause": "payload identity mismatch with entry_key"})
    sha = canonical_payload_sha256(payload)
    c = _conn_ctx(conn)

    def _t(name: str, _s: str = schema) -> str:
        return f'"{_s}".{name}'

    try:
        with c.conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_pk, payload_sha256, status, version "
                f"FROM {_t('registry_entry')} "
                "WHERE registry_id=%s AND family_key=%s AND entry_key=%s FOR UPDATE",
                (registry_id, family_key, entry_key),
            )
            row = cur.fetchone()
            if row is None:
                c.conn.commit()
                return Result(NOT_FOUND, detail={"entry_key": entry_key})
            entry_pk, old_sha, status, cur_ver = row
            if status != "active" or int(cur_ver) != expected_version:
                event_id = _record_event(
                    cur,
                    registry_id=registry_id,
                    schema=schema,
                    family_key=family_key,
                    entry_key=entry_key,
                    action="update",
                    actor_session=session_id,
                    actor_kind=actor_kind,
                    base_version=expected_version,
                    after_version=int(cur_ver),
                    payload_after=payload,
                    reason=reason,
                    detail={"conflict": True, "current_status": status, "current_version": int(cur_ver)},
                )
                c.conn.commit()
                return Result(
                    CONFLICT_VERSION,
                    entry={
                        "registry_id": registry_id,
                        "family_key": family_key,
                        "entry_key": entry_key,
                        "payload_sha256": old_sha,
                        "version": int(cur_ver),
                        "status": status,
                    },
                    detail={
                        "entry_key": entry_key,
                        "current_status": status,
                        "current_version": int(cur_ver),
                        "conflict_event_id": event_id,
                    },
                )
            cur.execute(
                f"UPDATE {_t('registry_entry')} "
                "SET payload=%s, payload_sha256=%s, version=version+1, "
                "updated_by=%s, updated_at=now() "
                "WHERE entry_pk=%s AND version=%s RETURNING version",
                (Json(payload, dumps=_pg_json_dumps), sha, session_id, entry_pk, expected_version),
            )
            new_version = int(cur.fetchone()[0])
            event_id = _record_event(
                cur,
                registry_id=registry_id,
                schema=schema,
                family_key=family_key,
                entry_key=entry_key,
                action="update",
                actor_session=session_id,
                actor_kind=actor_kind,
                base_version=expected_version,
                after_version=new_version,
                payload_after=payload,
                before_sha256=old_sha,
                reason=reason,
            )
            cur.execute(
                _SQL_ENTRY_LAST_EVENT.format(entry=_t("registry_entry", schema)),
                (event_id, entry_pk),
            )
            cur.execute(
                _SQL_ENTRY_BY_PK.format(cols=", ".join(_ENTRY_COLS), entry=_t("registry_entry", schema)),
                (entry_pk,),
            )
            entry_row = cur.fetchone()
        c.conn.commit()
        return Result(OK, entry=_entry_dict(entry_row), event_id=event_id)
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.conn.rollback()
        raise
    finally:
        _release_conn(c)


def retire(  # noqa: long-param-list  02号文§3.1 意图API签名契约绑定（调用方关键字形态固定）
    registry_id: str,
    family_key: str,
    entry_key: str,
    *,
    authority_ref: str,
    reason: str,
    evidence: str | None = None,
    session_id: str,
    actor_kind: str = "agent",
    conn: PgConnection = None,
    schema: str = SCHEMA_NAME,
) -> Result:
    """退役=tombstone（行保留永不物理删）；authority_ref 缺失机械拒绝（死亡证明字段6）。"""
    _validate_actor(actor_kind)
    if not authority_ref or not str(authority_ref).strip():
        return Result(AUTHORITY_REQUIRED, detail={"cause": "retire requires authority_ref (ruling/批件号)"})
    _require_reason(reason, "retire")
    c = _conn_ctx(conn)

    def _t(name: str, _s: str = schema) -> str:
        return f'"{_s}".{name}'

    try:
        with c.conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_pk, version, payload, payload_sha256, status "
                f"FROM {_t('registry_entry')} "
                "WHERE registry_id=%s AND family_key=%s AND entry_key=%s FOR UPDATE",
                (registry_id, family_key, entry_key),
            )
            row = cur.fetchone()
            if row is None:
                c.conn.commit()
                return Result(NOT_FOUND, detail={"entry_key": entry_key})
            entry_pk, version, payload, sha, status = row
            if status != "active":
                c.conn.commit()
                return Result(OK_NOOP, detail={"entry_key": entry_key, "already_retired": True})
            new_version = int(version) + 1
            cur.execute(
                f"UPDATE {_t('registry_entry')} "
                "SET status='retired', version=%s, updated_by=%s, updated_at=now() "
                "WHERE entry_pk=%s",
                (new_version, session_id, entry_pk),
            )
            event_id = _record_event(
                cur,
                registry_id=registry_id,
                schema=schema,
                family_key=family_key,
                entry_key=entry_key,
                action="retire",
                actor_session=session_id,
                actor_kind=actor_kind,
                base_version=int(version),
                after_version=new_version,
                payload_after=payload,
                before_sha256=sha,
                reason=reason,
                authority_ref=authority_ref,
                detail={"evidence": evidence} if evidence else None,
            )
            cur.execute(
                _SQL_ENTRY_LAST_EVENT.format(entry=_t("registry_entry", schema)),
                (event_id, entry_pk),
            )
            cur.execute(
                _SQL_ENTRY_BY_PK.format(cols=", ".join(_ENTRY_COLS), entry=_t("registry_entry", schema)),
                (entry_pk,),
            )
            entry_row = cur.fetchone()
        c.conn.commit()
        return Result(OK, entry=_entry_dict(entry_row), event_id=event_id)
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.conn.rollback()
        raise
    finally:
        _release_conn(c)


def takeover(  # noqa: long-param-list  02号文§3.1 意图API签名契约绑定（调用方关键字形态固定）
    registry_id: str,
    family_key: str,
    entry_key: str,
    *,
    force: bool = False,
    owner_approval_ref: str | None = None,
    reason: str,
    session_id: str,
    actor_kind: str = "agent",
    conn: PgConnection = None,
    schema: str = SCHEMA_NAME,
) -> Result:
    """强制接管条目租约。force=True 需 Owner 批文标记 owner_approval_ref（D-5，high 域）；
    活租约未过期且未 force=LEASE_HELD。接管必记 action=takeover 事件（含被顶会话）。"""
    _validate_actor(actor_kind)
    _require_reason(reason, "takeover")
    if force and not (owner_approval_ref and str(owner_approval_ref).strip()):
        return Result(FORBIDDEN_FORCE, detail={"cause": "force takeover requires owner_approval_ref (D-5)"})
    c = _conn_ctx(conn)

    def _t(name: str, _s: str = schema) -> str:
        return f'"{_s}".{name}'

    try:
        with c.conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_pk, held_by_session, lease_expires_at "
                f"FROM {_t('registry_entry')} "
                "WHERE registry_id=%s AND family_key=%s AND entry_key=%s FOR UPDATE",
                (registry_id, family_key, entry_key),
            )
            row = cur.fetchone()
            if row is None:
                c.conn.commit()
                return Result(NOT_FOUND, detail={"entry_key": entry_key})
            entry_pk, held_by, lease_exp = row
            if held_by and held_by != session_id and lease_exp is not None and not force:
                cur.execute("SELECT now()")
                now = cur.fetchone()[0]
                if lease_exp > now:
                    c.conn.commit()
                    return Result(
                        LEASE_HELD,
                        detail={"held_by_session": held_by, "lease_expires_at": str(lease_exp)},
                    )
            cur.execute(
                f"UPDATE {_t('registry_entry')} "
                "SET held_by_session=%s, held_at=now(), "
                "lease_expires_at=now() + %s::interval WHERE entry_pk=%s",
                (session_id, f"{int(LEASE_TTL.total_seconds())} seconds", entry_pk),
            )
            event_id = _record_event(
                cur,
                registry_id=registry_id,
                schema=schema,
                family_key=family_key,
                entry_key=entry_key,
                action="takeover",
                actor_session=session_id,
                actor_kind=actor_kind,
                base_version=None,
                after_version=0,
                payload_after={},
                reason=reason,
                detail={
                    "displaced_session": held_by,
                    "force": bool(force),
                    "owner_approval_ref": owner_approval_ref,
                },
            )
        c.conn.commit()
        return Result(OK, event_id=event_id, detail={"displaced_session": held_by})
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.conn.rollback()
        raise
    finally:
        _release_conn(c)


def fetch_entry(
    registry_id: str,
    family_key: str,
    entry_key: str,
    *,
    conn: PgConnection = None,
    schema: str = SCHEMA_NAME,
) -> dict | None:
    """只读点查条目当前行（消费方/门禁用；读路径不产生事件）。"""
    owned = conn is None
    c = _conn_ctx(conn)

    def _t(name: str, _s: str = schema) -> str:
        return f'"{_s}".{name}'

    try:
        with c.conn.cursor() as cur:
            cur.execute(
                f"SELECT {', '.join(_ENTRY_COLS)} FROM {_t('registry_entry')} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                "WHERE registry_id=%s AND family_key=%s AND entry_key=%s",
                (registry_id, family_key, entry_key),
            )
            row = cur.fetchone()
        return _entry_dict(row) if row else None
    finally:
        _release_conn(c)
