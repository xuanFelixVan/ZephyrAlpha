# [MODULE] tests.governance.test_registry_ledger
# [DOMAIN] D_GOVERNANCE
# [TTL] task_bound
"""W-M1 车道A·波0③ 红蓝测试：registry_ledger DDL 部署器 + 意图 API。

判据（施工令③）：
1. 同条目双写必 409（串行陈旧 CAS + 真并发竞跑，恰好一胜一败）
2. 事件表物理不可改（触发器 RAISE + reader 角色权限拒绝）
3. 幂等部署器重复跑零漂移（schema_fingerprint 相等）
4. 复合键身份与 batch_creation_tokens B22 (file,token) 同构断言
测试全部落在临时 schema（registry_ledger_rb_*），收尾 CASCADE 删除，零生产路径写入。
"""

from __future__ import annotations

import importlib.util
import json
import threading
from pathlib import Path

import psycopg2
import pytest

from zephyr.governance.registry_ledger.api import (
    AUTHORITY_REQUIRED,
    CONFLICT_DUPLICATE,
    CONFLICT_VERSION,
    FORBIDDEN_FORCE,
    INVALID_ARGUMENT,
    NOT_FOUND,
    OK,
    OK_NOOP,
    SCHEMA_INVALID,
    register,
    retire,
    takeover,
    update,
)
from zephyr.governance.registry_ledger.deploy import (
    deploy_registry_ledger,
    schema_fingerprint,
)
from zephyr.governance.registry_ledger.ledger_identity import (
    entry_composite_key,
    entry_identity_key,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REASON = "wm1 lane A red-blue test write"
REASON2 = "wm1 lane A red-blue second write"
LONG_REASON = "takeover reason must be at least ten chars"

pytestmark = pytest.mark.skipif(
    not (REPO_ROOT / "config" / ".env.postgres").exists(),
    reason="config/.env.postgres missing",
)


def _pg_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (REPO_ROOT / "config" / ".env.postgres").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def _connect(env: dict[str, str], user_key: str = "POSTGRES_USER", password_key: str = "POSTGRES_PASSWORD"):
    return psycopg2.connect(
        host=env["POSTGRES_HOST"],
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user=env[user_key],
        password=env[password_key],
    )


@pytest.fixture(scope="module")
def pg_env():
    env = _pg_env()
    try:
        conn = _connect(env)
    except psycopg2.OperationalError as exc:
        pytest.skip(f"PG unavailable: {exc}")
    conn.close()
    return env


@pytest.fixture()
def ledger(pg_env):
    """临时 schema 部署器 + 连接工厂；收尾 CASCADE 删除。"""
    import uuid

    env = pg_env
    schema = f"registry_ledger_rb_{uuid.uuid4().hex[:8]}"
    conn = _connect(env)
    report = deploy_registry_ledger(conn, schema=schema)
    assert report["objects_after"] >= report["objects_before"]

    cur = conn.cursor()
    cur.execute(
        f'INSERT INTO "{schema}".registry_catalog '
        "(registry_id, physical_path, family_key, identity_mode, maintenance) "
        "VALUES ('REG-TEST-001', 'test/x.yaml', 'entries', 'first_scalar', 'manual')"
    )
    conn.commit()
    cur.close()

    yield {"conn": conn, "schema": schema, "env": env}
    conn.rollback()
    drop = _connect(env)
    with drop.cursor() as c:
        c.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
    drop.commit()
    drop.close()
    conn.close()


def _entry_payload(path: str = "src/zephyr/demo.py", token: str = "tok-a", note: str = "v1") -> dict:
    return {"file": path, "token": token, "note": note}


def _count_events(ledger, action: str | None = None) -> int:
    cur = ledger["conn"].cursor()
    if action:
        cur.execute(
            f'SELECT count(*) FROM "{ledger["schema"]}".registry_event WHERE action=%s',
            (action,),
        )
    else:
        cur.execute(f'SELECT count(*) FROM "{ledger["schema"]}".registry_event')
    n = int(cur.fetchone()[0])
    cur.close()
    return n


def _event_details(ledger) -> list[dict]:
    cur = ledger["conn"].cursor()
    cur.execute(
        f'SELECT action, base_version, after_version, detail FROM "{ledger["schema"]}".registry_event ORDER BY event_id'
    )
    rows = cur.fetchall()
    cur.close()
    return [{"action": r[0], "base_version": r[1], "after_version": r[2], "detail": r[3]} for r in rows]


# ---------- 判据③：幂等部署器重复跑零漂移 ----------


def test_deploy_idempotent_zero_drift(pg_env):
    import uuid

    env = pg_env
    schema = f"registry_ledger_rb_{uuid.uuid4().hex[:8]}"
    conn = _connect(env)
    try:
        deploy_registry_ledger(conn, schema=schema)
        fp1 = schema_fingerprint(conn, schema=schema)
        report2 = deploy_registry_ledger(conn, schema=schema)
        fp2 = schema_fingerprint(conn, schema=schema)
        assert fp1 == fp2, "redeploy must be zero-drift"
        cur = conn.cursor()
        cur.execute(f'SELECT count(*) FROM "{schema}"._schema_version')
        assert int(cur.fetchone()[0]) == 1
        cur.execute(
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname=%s AND c.relname IN ('registry_entry','registry_event',"
            "'registry_snapshot','registry_catalog')",
            (schema,),
        )
        assert int(cur.fetchone()[0]) == 4
        cur.close()
    finally:
        with conn.cursor() as c:
            c.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        conn.commit()
        conn.close()


def test_deploy_creates_append_only_triggers(ledger):
    cur = ledger["conn"].cursor()
    cur.execute(
        "SELECT tgname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid "
        "JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname=%s AND NOT t.tgisinternal",
        (ledger["schema"],),
    )
    names = {r[0] for r in cur.fetchall()}
    cur.close()
    assert "trg_registry_event_no_mutation" in names
    assert "trg_registry_snapshot_no_mutation" in names


# ---------- 判据①：同条目双写必 409 ----------


def test_register_then_stale_cas_update_409(ledger):
    r1 = register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="st-wm1-buildA-20260923",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r1.code == OK and r1.entry["version"] == 1

    r2 = update(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        1,
        _entry_payload(note="v2"),
        reason=REASON,
        session_id="st-wm1-buildA-20260923",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r2.code == OK and r2.entry["version"] == 2

    r3 = update(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        1,
        _entry_payload(note="v3-stale"),
        reason=REASON,
        session_id="st-wm1-buildA-20260923",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r3.code == CONFLICT_VERSION
    assert r3.http_status == 409
    assert r3.entry is not None and r3.entry["version"] == 2

    conflicts = [e for e in _event_details(ledger) if e["detail"] and e["detail"].get("conflict")]
    assert len(conflicts) == 1, "rejection itself must be recorded as an event row"
    assert conflicts[0]["base_version"] == 1
    assert conflicts[0]["after_version"] == 2


def test_register_duplicate_idempotent_and_conflict(ledger):
    r1 = register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r1.code == OK

    r2 = register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s2",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r2.code == OK_NOOP

    r3 = register(
        "REG-TEST-001",
        "entries",
        _entry_payload(note="different"),
        reason=REASON,
        session_id="s3",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r3.code == CONFLICT_DUPLICATE
    assert r3.http_status == 409
    assert r3.detail["conflict_event_id"] is not None


def test_concurrent_double_write_exactly_one_wins(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="seeder",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    entry_key = "file=src/zephyr/demo.py|token=tok-a"
    results: list[tuple[str, int]] = []
    barrier = threading.Barrier(2)

    def worker(name: str, note: str):
        env = ledger["env"]
        conn = _connect(env)
        barrier.wait()
        try:
            res = update(
                "REG-TEST-001",
                "entries",
                entry_key,
                1,
                _entry_payload(note=note),
                reason=REASON,
                session_id=name,
                conn=conn,
                schema=ledger["schema"],
            )
            results.append((res.code, name))
        finally:
            conn.close()

    t1 = threading.Thread(target=worker, args=("w1", "from-w1"))
    t2 = threading.Thread(target=worker, args=("w2", "from-w2"))
    t1.start()
    t2.start()
    t1.join(timeout=30)
    t2.join(timeout=30)

    codes = sorted(code for code, _ in results)
    assert codes == ["CONFLICT_VERSION", "OK"], f"exactly one winner: {results}"
    conflict_events = [e for e in _event_details(ledger) if e["detail"] and e["detail"].get("conflict")]
    assert len(conflict_events) == 1
    ok_updates = [
        e for e in _event_details(ledger) if e["action"] == "update" and not (e["detail"] or {}).get("conflict")
    ]
    assert len(ok_updates) == 1


# ---------- 判据②：事件表物理不可改 ----------


def test_event_table_physically_immutable(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    schema = ledger["schema"]
    with pytest.raises(psycopg2.Error) as exc_info:
        with ledger["conn"].cursor() as cur:
            cur.execute(f'UPDATE "{schema}".registry_event SET reason=%s', ("tampered",))
    assert "append-only" in str(exc_info.value)

    ledger["conn"].rollback()
    with pytest.raises(psycopg2.Error) as exc_info2:
        with ledger["conn"].cursor() as cur:
            cur.execute(f'DELETE FROM "{schema}".registry_event')
    assert "append-only" in str(exc_info2.value)
    ledger["conn"].rollback()
    assert _count_events(ledger) >= 1, "events survived tamper attempts"


def test_event_table_reader_role_cannot_mutate(ledger):
    env = ledger["env"]
    if "POSTGRES_READER_USER" not in env:
        pytest.skip("POSTGRES_READER_USER not configured")
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    try:
        reader = _connect(env, "POSTGRES_READER_USER", "POSTGRES_READER_PASSWORD")
    except psycopg2.OperationalError as exc:
        pytest.skip(f"reader role unreachable: {exc}")
    try:
        with reader.cursor() as cur:
            cur.execute(f'SELECT count(*) FROM "{ledger["schema"]}".registry_event')
            assert int(cur.fetchone()[0]) >= 1
            with pytest.raises(psycopg2.Error) as exc_info:
                cur.execute(f'UPDATE "{ledger["schema"]}".registry_event SET reason=%s', ("hacked",))
            assert "权限不够" in str(exc_info.value) or "permission denied" in str(exc_info.value)
    finally:
        reader.rollback()
        reader.close()


# ---------- retire：authority_ref 强制 + tombstone 永不物理删 ----------


def test_retire_requires_authority_ref(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    r = retire(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        authority_ref="",
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r.code == AUTHORITY_REQUIRED
    cur = ledger["conn"].cursor()
    cur.execute(f'SELECT status FROM "{ledger["schema"]}".registry_entry')
    assert cur.fetchone()[0] == "active"
    cur.close()
    assert _count_events(ledger, "retire") == 0


def test_retire_tombstone_keeps_row_and_records_death(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    r = retire(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        authority_ref="裁定#999",
        reason=REASON,
        evidence="docs/evidence/x.md",
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r.code == OK
    assert r.entry["status"] == "retired"
    assert r.entry["version"] == 2

    cur = ledger["conn"].cursor()
    cur.execute(f"SELECT count(*) FROM \"{ledger['schema']}\".registry_entry WHERE registry_id='REG-TEST-001'")
    assert int(cur.fetchone()[0]) == 1, "tombstone row must be kept, never physically deleted"
    cur.execute(
        f'SELECT authority_ref, before_sha256, payload_after FROM "{ledger["schema"]}".registry_event WHERE action=%s',
        ("retire",),
    )
    row = cur.fetchone()
    cur.close()
    assert row is not None
    assert row[0] == "裁定#999"
    assert len(row[1]) == 64

    r2 = register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s2",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r2.code == CONFLICT_DUPLICATE, "tombstone keeps the UNIQUE seat"


def test_update_missing_entry_404(ledger):
    r = update(
        "REG-TEST-001",
        "entries",
        "file=src/none.py",
        1,
        {"file": "src/none.py"},
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r.code == NOT_FOUND


def test_update_identity_mismatch_rejected(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    r = update(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        1,
        {"file": "src/other.py", "token": "tok-a"},
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r.code == INVALID_ARGUMENT


def test_register_unidentifiable_payload_rejected(ledger):
    r = register(
        "REG-TEST-001",
        "entries",
        {"nested": {"a": 1}},
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r.code == SCHEMA_INVALID


def test_short_reason_rejected(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    with pytest.raises(ValueError):
        update(
            "REG-TEST-001",
            "entries",
            "file=src/zephyr/demo.py|token=tok-a",
            1,
            _entry_payload(note="v2"),
            reason="short",
            session_id="s1",
            conn=ledger["conn"],
            schema=ledger["schema"],
        )


# ---------- takeover：force 显式参数 + Owner 批文标记（D-5） ----------


def test_takeover_force_requires_owner_approval(ledger):
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    r = takeover(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        force=True,
        reason=LONG_REASON,
        session_id="s2",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r.code == FORBIDDEN_FORCE

    r2 = takeover(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        force=True,
        owner_approval_ref="裁定#1001",
        reason=LONG_REASON,
        session_id="s2",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    assert r2.code == OK
    events = [e for e in _event_details(ledger) if e["action"] == "takeover"]
    assert len(events) == 1
    assert events[0]["detail"]["owner_approval_ref"] == "裁定#1001"
    assert events[0]["detail"]["force"] is True


# ---------- 判据④：复合键身份与 B22 (file,token) 同构 ----------


def _load_landing_module():
    import sys

    path = REPO_ROOT / "scripts" / "governance" / "commit_queue_landing.py"
    spec = importlib.util.spec_from_file_location("wm1_commit_queue_landing_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def test_composite_key_matches_gate_single_key():
    tokenless = {"ruling_id": 402, "title": "x"}
    assert entry_composite_key(tokenless) == "ruling_id=402"
    assert entry_composite_key(tokenless) == entry_identity_key(tokenless)
    assert entry_composite_key({"nested": {"a": 1}}) is None


def test_composite_key_matches_merger_identity():
    landing = _load_landing_module()
    corpus = [
        {"file": "src/a.py", "token": "t1", "created": "2026-09-23"},
        {"file": "src/b.py", "token": 123},
        {"ruling_id": 402, "title": "no token field"},
        {"file": "src/c.py"},
        {"path": "x/y", "token": "t2"},
    ]
    if landing._merge_entry_identity({"ruling_id": 402}) is None:
        pytest.skip("registry_family 重组位未落地（merger fail-closed 全 None），等值断言待其落地后生效")
    for payload in corpus:
        assert entry_composite_key(payload) == landing._merge_entry_identity(payload), (
            f"identity divergence for {payload}"
        )


def test_composite_key_b22_file_token_isomorphism():
    """B22 立法身份=(file,token) 二元组；复合键 `file=<path>|token=<t>` 与其一一对应。"""
    corpus = [
        {"file": "src/a.py", "token": "t1"},
        {"file": "src/b.py", "token": "t2", "note": "extra fields ignored"},
        {"file": "src/c.py", "token": 123},
    ]
    for payload in corpus:
        key = entry_composite_key(payload)
        file_value, token_value = str(payload["file"]), str(payload["token"])
        b22_tuple = (file_value, token_value)
        assert key == f"file={file_value}|token={token_value}"
        assert key.split("|") == [f"file={b22_tuple[0]}", f"token={b22_tuple[1]}"]
        # 逆映射：复合键可无损还原 B22 二元组
        left, right = key.split("|")
        assert (left.split("=", 1)[1], right.split("=", 1)[1]) == b22_tuple


def test_canonical_sha_stable_across_key_order():
    from zephyr.governance.registry_ledger.api import canonical_payload_sha256

    a = canonical_payload_sha256({"file": "x.py", "token": "t", "note": "n"})
    b = canonical_payload_sha256({"note": "n", "token": "t", "file": "x.py"})
    assert a == b
    assert len(a) == 64


def test_event_replay_yields_entry_state(ledger):
    """I2/I3 抽样：事件链（register→update）回放终点与条目状态一致。"""
    register(
        "REG-TEST-001",
        "entries",
        _entry_payload(),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    update(
        "REG-TEST-001",
        "entries",
        "file=src/zephyr/demo.py|token=tok-a",
        1,
        _entry_payload(note="v2"),
        reason=REASON,
        session_id="s1",
        conn=ledger["conn"],
        schema=ledger["schema"],
    )
    cur = ledger["conn"].cursor()
    cur.execute(
        f'SELECT payload_after FROM "{ledger["schema"]}".registry_event '
        "WHERE action='update' AND (detail IS NULL OR detail::text NOT LIKE '%conflict%') "
        "ORDER BY event_id"
    )
    last_payload = cur.fetchone()[0]
    cur.execute(f'SELECT payload, version FROM "{ledger["schema"]}".registry_entry')
    entry_payload, version = cur.fetchone()
    cur.close()
    assert json.loads(json.dumps(last_payload)) == entry_payload
    assert version == 2
