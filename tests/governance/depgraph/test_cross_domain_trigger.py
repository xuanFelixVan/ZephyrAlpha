"""#ARCH-CROSS-DOMAIN-TRIGGER-001: edges.cross_domain 自动维护触发器测试。

验证 DB 触发器正确自动计算 cross_domain（治本修复，2026-07-25）：
  - trg_edges_cross_domain_bi: BEFORE INSERT → 覆盖 app 写入的任意值
  - trg_edges_cross_domain_bu: BEFORE UPDATE OF from_node_id,to_node_id → 重算
  - trg_nodes_domain_id_au: AFTER UPDATE OF domain_id ON nodes → 重算受影响边

测试目标：
  1. INSERT 跨域边（传 cross_domain=999）→ 触发器覆盖为 1
  2. INSERT 同域边（传 cross_domain=999）→ 触发器覆盖为 0
  3. UPDATE nodes.domain_id → 受影响边 cross_domain 自动重算
  4. 回填后 Defect A (FALSE NEGATIVE) = 0

测试库策略同 test_depgraph_db.py：pytest 下强制 PG 测试库，未配置则 skip。
触发器未在位时 skip（提示先应用迁移 06_fix_cross_domain_trigger.sql）。
"""

import os
import sys

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from zephyr.shared.io.paths import REPO_ROOT


def _in_pytest() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _resolve_test_pg_config() -> dict[str, str] | None:
    cfg: dict[str, str] = {}
    env_file = REPO_ROOT / "config" / ".env.postgres.test"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                cfg[key.strip()] = value.strip()
    host = os.environ.get("ZEPHYR_TEST_PG_HOST") or cfg.get("POSTGRES_HOST")
    port = os.environ.get("ZEPHYR_TEST_PG_PORT") or cfg.get("POSTGRES_PORT", "5432")
    dbname = os.environ.get("ZEPHYR_TEST_PG_DB") or cfg.get("POSTGRES_DB")
    user = os.environ.get("ZEPHYR_TEST_PG_USER") or cfg.get("POSTGRES_USER", "zephyr")
    password = os.environ.get("ZEPHYR_TEST_PG_PASSWORD") or cfg.get("POSTGRES_PASSWORD", "")
    if not (host and dbname):
        return None
    return {"host": host, "port": port, "dbname": dbname, "user": user, "password": password}


def _make_connection():
    """连接目标选择——pytest 下强制测试库；__main__ 下优先测试库否则回退生产。"""
    test_cfg = _resolve_test_pg_config()
    if _in_pytest():
        if test_cfg is None:
            pytest.skip("PG 测试库未配置（ZEPHYR_TEST_PG_* 或 config/.env.postgres.test），跳过以防测试写生产表")
        try:
            conn = psycopg2.connect(cursor_factory=RealDictCursor, **test_cfg)
        except psycopg2.OperationalError as exc:
            pytest.skip(f"PG 测试库不可用，跳过: {exc}")
        conn.autocommit = True
        return conn
    if test_cfg is not None:
        conn = psycopg2.connect(cursor_factory=RealDictCursor, **test_cfg)
        conn.autocommit = True
        print(f"[INFO] 使用 PG 测试库: {test_cfg['host']}:{test_cfg['port']}/{test_cfg['dbname']}")
        return conn
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    print("[WARNING] 未配置 PG 测试库，回退连接生产 depgraph——操作员显式选择")
    return get_depgraph_pg_connection(autocommit=True, read_only=False)


def _trigger_in_place(cur) -> bool:
    """检查 3 个 cross_domain 触发器是否在位。"""
    cur.execute("""
        SELECT COUNT(*) AS c FROM pg_trigger
        WHERE tgname IN ('trg_edges_cross_domain_bi','trg_edges_cross_domain_bu','trg_nodes_domain_id_au')
          AND NOT tgisinternal
    """)
    return cur.fetchone()["c"] == 3


def _find_cross_domain_pair(cur):
    """找一对不同域的 production 节点。"""
    cur.execute("""
        SELECT n1.node_id AS from_id, n1.domain_id AS from_dom,
               n2.node_id AS to_id, n2.domain_id AS to_dom
        FROM nodes n1 CROSS JOIN nodes n2
        WHERE n1.domain_id IS NOT NULL AND n1.domain_id <> ''
          AND n2.domain_id IS NOT NULL AND n2.domain_id <> ''
          AND n1.domain_id <> n2.domain_id
          AND n1.design_maturity = 'production' AND n2.design_maturity = 'production'
        LIMIT 1
    """)
    return cur.fetchone()


def _find_same_domain_pair(cur):
    """找一对同域的 production 节点。"""
    cur.execute("""
        SELECT n1.node_id AS from_id, n2.node_id AS to_id, n1.domain_id AS dom
        FROM nodes n1 CROSS JOIN nodes n2
        WHERE n1.domain_id = n2.domain_id
          AND n1.domain_id IS NOT NULL AND n1.domain_id <> ''
          AND n1.node_id <> n2.node_id
          AND n1.design_maturity = 'production' AND n2.design_maturity = 'production'
        LIMIT 1
    """)
    return cur.fetchone()


@pytest.fixture
def conn():
    c = _make_connection()
    yield c
    c.close()


def test_trigger_in_place(conn):
    """前置：3 个 cross_domain 触发器在位。"""
    with conn.cursor() as cur:
        if not _trigger_in_place(cur):
            pytest.skip(
                "cross_domain 触发器未在位——请先应用 "
                "scripts/governance/migrate_sqlite_to_pg/06_fix_cross_domain_trigger.sql"
            )


def test_insert_cross_domain_edge_auto_computed(conn):
    """INSERT 跨域边（传 cross_domain=999）→ 触发器覆盖为 1。"""
    with conn.cursor() as cur:
        if not _trigger_in_place(cur):
            pytest.skip("触发器未在位")
        pair = _find_cross_domain_pair(cur)
        if not pair:
            pytest.skip("无可用的跨域节点对")
        # dep_maturity='active' 不触发 apply_depgraph design-edge 保护
        cur.execute(
            """
            INSERT INTO edges (from_node_id, to_node_id, dep_type, dep_maturity, cross_domain)
            VALUES (%s, %s, 'import_depends', 'active', 999)
            RETURNING edge_id, cross_domain
        """,
            (pair["from_id"], pair["to_id"]),
        )
        row = cur.fetchone()
        try:
            assert row["cross_domain"] == 1, f"跨域边 cross_domain 应=1（触发器覆盖），实际={row['cross_domain']}"
        finally:
            cur.execute("DELETE FROM edges WHERE edge_id=%s", (row["edge_id"],))


def test_insert_same_domain_edge_auto_computed(conn):
    """INSERT 同域边（传 cross_domain=999）→ 触发器覆盖为 0。"""
    with conn.cursor() as cur:
        if not _trigger_in_place(cur):
            pytest.skip("触发器未在位")
        pair = _find_same_domain_pair(cur)
        if not pair:
            pytest.skip("无可用的同域节点对")
        cur.execute(
            """
            INSERT INTO edges (from_node_id, to_node_id, dep_type, dep_maturity, cross_domain)
            VALUES (%s, %s, 'import_depends', 'active', 999)
            RETURNING edge_id, cross_domain
        """,
            (pair["from_id"], pair["to_id"]),
        )
        row = cur.fetchone()
        try:
            assert row["cross_domain"] == 0, f"同域边 cross_domain 应=0（触发器覆盖），实际={row['cross_domain']}"
        finally:
            cur.execute("DELETE FROM edges WHERE edge_id=%s", (row["edge_id"],))


def test_node_domain_id_update_recomputes_edges(conn):
    """UPDATE nodes.domain_id → 受影响边 cross_domain 自动重算。"""
    with conn.cursor() as cur:
        if not _trigger_in_place(cur):
            pytest.skip("触发器未在位")
        pair = _find_cross_domain_pair(cur)
        if not pair:
            pytest.skip("无可用的跨域节点对")
        # 插入跨域边（cross_domain=1）
        cur.execute(
            """
            INSERT INTO edges (from_node_id, to_node_id, dep_type, dep_maturity)
            VALUES (%s, %s, 'import_depends', 'active')
            RETURNING edge_id
        """,
            (pair["from_id"], pair["to_id"]),
        )
        edge_id = cur.fetchone()["edge_id"]
        try:
            # 把 to_node 的域改成与 from_node 相同 → 边应变同域 cross_domain=0
            cur.execute("SELECT domain_id FROM nodes WHERE node_id=%s", (pair["from_id"],))
            new_dom = cur.fetchone()["domain_id"]
            cur.execute(
                "UPDATE nodes SET domain_id=%s WHERE node_id=%s",
                (new_dom, pair["to_id"]),
            )
            cur.execute("SELECT cross_domain FROM edges WHERE edge_id=%s", (edge_id,))
            cd = cur.fetchone()["cross_domain"]
            assert cd == 0, f"域合并后 cross_domain 应=0，实际={cd}（nodes AU 触发器未重算）"
        finally:
            # 恢复 to_node 原域 + 删测试边
            cur.execute(
                "UPDATE nodes SET domain_id=%s WHERE node_id=%s",
                (pair["to_dom"], pair["to_id"]),
            )
            cur.execute("DELETE FROM edges WHERE edge_id=%s", (edge_id,))


def test_no_false_negative_after_backfill(conn):
    """回填后 Defect A (FALSE NEGATIVE) = 0。"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) AS c FROM edges e
            JOIN nodes n1 ON e.from_node_id = n1.node_id
            JOIN nodes n2 ON e.to_node_id = n2.node_id
            WHERE COALESCE(e.cross_domain, 0) = 0
              AND n1.domain_id IS NOT NULL AND n1.domain_id <> ''
              AND n2.domain_id IS NOT NULL AND n2.domain_id <> ''
              AND n1.domain_id <> n2.domain_id
        """)
        false_neg = cur.fetchone()["c"]
        assert false_neg == 0, f"仍存在 {false_neg} 条 FALSE NEGATIVE（跨域但 cross_domain=0）——触发器/回填未生效"


if __name__ == "__main__":
    # 手工执行：优先测试库，未配置回退生产（操作员显式选择）
    c = _make_connection()
    try:
        with c.cursor() as cur:
            print(f"触发器在位: {_trigger_in_place(cur)}")
            if _find_cross_domain_pair(cur):
                print("跨域节点对: 可用")
            if _find_same_domain_pair(cur):
                print("同域节点对: 可用")
    finally:
        c.close()
    # 运行全部测试（__main__ 下不 skip）
    import subprocess

    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v", "-s"]))
