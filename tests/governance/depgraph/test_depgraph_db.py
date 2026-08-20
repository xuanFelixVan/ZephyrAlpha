"""
DM-100017: depgraph端到端功能测试（P2迁移后：PostgreSQL）
覆盖：dep_表组7表CRUD、arch_表组7表CRUD、rule_bindings表、nodes 23列、edges 18列

5.34.4 治本（2026-07-18）：原实现经 get_depgraph_pg_connection() 直连生产
depgraph (PostgreSQL)，INSERT/DELETE 直接修改生产数据。现增加防护——
pytest 运行（PYTEST_CURRENT_TEST）时连接目标强制切到 PG 测试库
（ZEPHYR_TEST_PG_* 环境变量或 config/.env.postgres.test），未配置或不可用
时 pytest.skip，禁止测试写生产表；手工脚本执行（__main__）优先使用测试库
配置，未配置时回退生产库并输出 stderr 提醒（操作员显式选择）。
"""

import json
import os
import sys
from datetime import datetime

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT


def _in_pytest() -> bool:
    """是否处于 pytest 测试调用上下文。

    PYTEST_CURRENT_TEST 仅在测试调用期由 pytest 设置——不能用
    ``"pytest" in sys.modules`` 判定（本文件自身 import pytest，恒为 True）。
    """
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _resolve_test_pg_config() -> dict[str, str] | None:
    """解析 PG 测试库连接参数（5.34.4 治本）。

    优先级：``config/.env.postgres.test``（KEY=VALUE，若存在）>
    ``ZEPHYR_TEST_PG_*`` 环境变量。与 tests/conftest.py 的
    ``_load_test_pg_config()`` 同规（本文件需支持 __main__ 独立执行，
    不依赖 conftest 加载，故自含一份）。未配置 host/db 时返回 None。

    禁止回退到 ``config/.env.postgres``（生产库真源）——测试连接目标必须
    显式声明，防测试误写生产表。
    """
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
    """5.34.4 治本：连接目标选择——pytest 下强制测试库，禁止写生产表。

    - pytest 运行：连接 PG 测试库（ZEPHYR_TEST_PG_* / config/.env.postgres.test），
      未配置或不可用时 pytest.skip；绝不回退生产库。
    - __main__ 手工执行：优先测试库配置；未配置时回退 get_depgraph_pg_connection()
      （生产库）并输出 stderr 提醒——操作员显式选择的人工验证路径。
    """
    test_cfg = _resolve_test_pg_config()
    if _in_pytest():
        if test_cfg is None:
            pytest.skip(
                "PG 测试库未配置（ZEPHYR_TEST_PG_HOST/ZEPHYR_TEST_PG_DB 或 "
                "config/.env.postgres.test），跳过以防测试写生产表（5.34.4）"
            )
        try:
            conn = psycopg2.connect(cursor_factory=RealDictCursor, **test_cfg)
        except psycopg2.OperationalError as exc:
            pytest.skip(f"PG 测试库不可用，跳过: {exc}")
        # 与 get_depgraph_pg_connection() 默认 autocommit=True 行为对齐——
        # 本测试含"表已删除"容错查询（psycopg2.Error 后继续执行），
        # 非 autocommit 下事务会进入 aborted 状态导致后续查询全部失败。
        conn.autocommit = True
        return conn
    if test_cfg is not None:
        conn = psycopg2.connect(cursor_factory=RealDictCursor, **test_cfg)
        conn.autocommit = True
        print(f"[5.34.4] 使用 PG 测试库: {test_cfg['host']}:{test_cfg['port']}/{test_cfg['dbname']}")
        return conn
    print(
        "[5.34.4] WARNING: 未配置 PG 测试库（ZEPHYR_TEST_PG_* / "
        "config/.env.postgres.test），回退连接生产 depgraph (PostgreSQL)——"
        "INSERT/DELETE 将修改生产数据，请确认这是有意的人工验证。",
        file=sys.stderr,
    )
    return get_depgraph_pg_connection()


def test_all():
    conn = _make_connection()
    conn.cursor_factory = RealDictCursor
    c = conn.cursor()
    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} - {detail}")

    # === 1. domains 表 ===
    print("\n=== 1. domains ===")
    c.execute("SELECT COUNT(*) AS cnt FROM domains")
    count = c.fetchone()["cnt"]
    # 治本（2026-07-19）：35 → 63（裁定#199/#200/#204 补 25 个手工域后 DB 共 63 个域）
    check("domains has 63 records", count == 63, f"got {count}")

    # 治本（2026-07-19）：D-DATA-PERSISTENCE 是旧 D-XXX 格式（裁定#204 已统一为 D_XXX），
    # 改用 D_INFRA_RUNTIME（YAML domain_name_zh=运行时集成，sync 后 DB domain_name 同步）。
    c.execute("SELECT * FROM domains WHERE domain_id='D_INFRA_RUNTIME'")
    d = c.fetchone()
    check(
        "domains SELECT by id",
        d is not None and d["domain_name"] == "运行时集成",
        f"got domain_name={d['domain_name'] if d else None}",
    )

    # === 2. nodes 表 (23列) ===
    print("\n=== 2. nodes (23 columns) ===")
    c.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema='public' AND table_name='nodes'
    """)
    cols = [row["column_name"] for row in c.fetchall()]
    expected_cols = [
        "node_id",
        "node_type",
        "path",
        "granularity",
        "domain_id",
        "subdomain_id",
        "blueprint_id",
        "belongs_to",
        "owner",
        "change_policy",
        "impact_level",
        "modification_permission",
        "file_header_score",
        "tags",
        "architecture_layer",
        "design_maturity",
        "deployment_lifecycle",
        "trust_zone",
        "license",
        "drive_direction",
        "type_specific_data",
        "last_verified",
    ]
    for col in expected_cols:
        check(f"nodes has column '{col}'", col in cols, f"missing {col}")

    c.execute("SELECT COUNT(*) AS cnt FROM nodes")
    node_count = c.fetchone()["cnt"]
    check("nodes has data", node_count > 100, f"got {node_count}")

    # === 3. edges 表 (18列+) ===
    print("\n=== 3. edges (18 columns) ===")
    c.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema='public' AND table_name='edges'
    """)
    edge_cols = [row["column_name"] for row in c.fetchall()]
    expected_edge = [
        "edge_id",
        "from_node",
        "to_node",
        "dep_type",
        "architecture_direction",
        "coupling_strength",
        "used_symbol",
        "invocation_method",
        "api_contract_refs",
        "event_ref",
        "ddd_integration_pattern",
        "failure_mode",
        "fallback",
        "activation_condition",
        "data_transfer_description",
        "resource_impact",
        "relationship_type",
        "cross_domain",
        "verified",
    ]
    for col in expected_edge:
        check(f"edges has column '{col}'", col in edge_cols, f"missing {col}")

    c.execute("SELECT COUNT(*) AS cnt FROM edges")
    edge_count = c.fetchone()["cnt"]
    check("edges has data", edge_count > 100, f"got {edge_count}")

    # === 4. domain_dependencies ===
    print("\n=== 4. domain_dependencies ===")
    c.execute(
        """INSERT INTO domain_dependencies (from_domain, to_domain, edge_count, edge_types, constraint_type)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (from_domain, to_domain) DO UPDATE SET
            edge_count=EXCLUDED.edge_count,
            edge_types=EXCLUDED.edge_types,
            constraint_type=EXCLUDED.constraint_type""",
        ("D-DATA", "D-GOV", 5, '["import_depends"]', "hard"),
    )
    conn.commit()
    c.execute("SELECT * FROM domain_dependencies WHERE from_domain='D-DATA' AND to_domain='D-GOV'")
    dd = c.fetchone()
    check("domain_dependencies INSERT+SELECT", dd is not None and dd["edge_count"] == 5)

    # === 5. contracts ===
    print("\n=== 5. contracts ===")
    now = datetime.now().isoformat()
    c.execute(
        """INSERT INTO contracts (contract_id, name, provider_domain, consumer_domain, contract_type, schema_definition, version)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (contract_id) DO UPDATE SET
            name=EXCLUDED.name,
            provider_domain=EXCLUDED.provider_domain,
            consumer_domain=EXCLUDED.consumer_domain,
            contract_type=EXCLUDED.contract_type,
            schema_definition=EXCLUDED.schema_definition,
            version=EXCLUDED.version""",
        ("CTR-TEST-001", "Test Contract", "D-DATA", "D-GOV", "api", "{}", "1.0"),
    )
    conn.commit()
    c.execute("SELECT * FROM contracts WHERE contract_id='CTR-TEST-001'")
    ctr = c.fetchone()
    check("contracts INSERT+SELECT", ctr is not None)

    # === 6. domain_events ===
    print("\n=== 6. domain_events ===")
    c.execute(
        """INSERT INTO domain_events (event_id, name, source_domain, target_domains, payload_schema, priority)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO UPDATE SET
            name=EXCLUDED.name,
            source_domain=EXCLUDED.source_domain,
            target_domains=EXCLUDED.target_domains,
            payload_schema=EXCLUDED.payload_schema,
            priority=EXCLUDED.priority""",
        ("EVT-TEST-001", "Test Event", "D-DATA", '["D-GOV"]', "{}", "P1"),
    )
    conn.commit()
    c.execute("SELECT * FROM domain_events WHERE event_id='EVT-TEST-001'")
    evt = c.fetchone()
    check("domain_events INSERT+SELECT", evt is not None)

    # === 8. arch_ 表组 ===
    # 注意：arch_domain_capacity 和 arch_domain_layers 已在 v6/v14 删除/合并入 domains 表
    print("\n=== 8. arch_domain_capacity ===")
    try:
        c.execute("SELECT COUNT(*) AS cnt FROM arch_domain_capacity")
        cap = c.fetchone()["cnt"]
        check("arch_domain_capacity has data", cap > 0, f"got {cap}")
    except psycopg2.Error:
        check("arch_domain_capacity has data", False, "table deleted (v6/v14 merged into domains)")

    print("\n=== 9. arch_path_mappings ===")
    c.execute("SELECT COUNT(*) AS cnt FROM arch_path_mappings")
    pm = c.fetchone()["cnt"]
    check("arch_path_mappings has data", pm > 0, f"got {pm}")

    print("\n=== 11. arch_domain_layers ===")
    try:
        c.execute("SELECT COUNT(*) AS cnt FROM arch_domain_layers")
        dl = c.fetchone()["cnt"]
        check("arch_domain_layers has data", dl > 0, f"got {dl}")
    except psycopg2.Error:
        check("arch_domain_layers has data", False, "table deleted (v6/v14 merged into domains)")

    print("\n=== 12. arch_constraints ===")
    c.execute("SELECT COUNT(*) AS cnt FROM arch_constraints")
    ac = c.fetchone()["cnt"]
    check("arch_constraints has data", ac > 0, f"got {ac}")

    print("\n=== 13. arch_directory_tree ===")
    c.execute("SELECT COUNT(*) AS cnt FROM arch_directory_tree")
    dt = c.fetchone()["cnt"]
    check("arch_directory_tree has data", dt > 0, f"got {dt}")

    # === 15. rule_bindings ===
    print("\n=== 15. rule_bindings ===")
    c.execute(
        """INSERT INTO rule_bindings (function_name, rule_id, binding_type, trigger_type, trigger_id)
        VALUES (%s, %s, %s, %s, %s)""",
        ("test_func", "RULE-001", "pre_check", "operation", "OP-001"),
    )
    conn.commit()
    c.execute("SELECT * FROM rule_bindings WHERE function_name='test_func'")
    rb = c.fetchone()
    check("rule_bindings INSERT+SELECT", rb is not None)

    # === 16. type_specific_data JSON解析 ===
    print("\n=== 16. type_specific_data JSON ===")
    c.execute("SELECT type_specific_data FROM nodes LIMIT 1")
    node = c.fetchone()
    if node and node["type_specific_data"]:
        try:
            data = json.loads(node["type_specific_data"])
            check("type_specific_data is valid JSON", isinstance(data, dict))
        except json.JSONDecodeError:
            check("type_specific_data is valid JSON", False, "JSON decode error")
    else:
        check("type_specific_data exists", True, "empty but OK")

    # === Cleanup ===
    print("\n=== Cleanup ===")
    c.execute("DELETE FROM domain_dependencies WHERE from_domain='D-DATA' AND to_domain='D-GOV'")
    c.execute("DELETE FROM contracts WHERE contract_id='CTR-TEST-001'")
    c.execute("DELETE FROM domain_events WHERE event_id='EVT-TEST-001'")
    c.execute("DELETE FROM rule_bindings WHERE function_name='test_func'")
    conn.commit()
    check("cleanup", True)

    conn.close()

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed > 0:
        # 5.34.4 治本：pytest 下用断言失败代替 sys.exit（SystemExit 在 pytest
        # 下会被记为 error 而非正常失败）；__main__ 脚本保持原退出码语义。
        if _in_pytest():
            raise AssertionError(f"depgraph DB checks failed: {failed}/{passed + failed}")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        if not _in_pytest():
            sys.exit(0)


def test_get_status_and_gate_map():
    """测试 DepgraphReader.get_status_and_gate_map 批量查询 build_status + gate_reason。

    治本（2026-08-02，模板对齐）：get_status_and_gate_map 是 battle_map 生成器
    渲染 ⛔ 受限原因行的数据来源（visualization_view_template §4.3 要素⑤），
    必须返回 build_status + gate_reason 两个字段，供生成器同时取回避免二次 DB 往返。
    """
    from zephyr.governance.persistence.depgraph_reader import DepgraphReader
    from zephyr.governance.persistence.pg_wrapper import _PgConnExecuteWrapper

    conn = _make_connection()
    try:
        # 显式用 RealDictCursor——_make_connection 回退生产库时默认 cursor 是 tuple
        c = conn.cursor(cursor_factory=RealDictCursor)
        # 取 5 个有 path 的现有节点作为测试样本
        c.execute("SELECT path, blueprint_id, build_status, gate_reason FROM nodes WHERE path IS NOT NULL LIMIT 5")
        existing = c.fetchall()
        if not existing:
            if _in_pytest():
                pytest.skip("test DB has no nodes with path")
            print("SKIP: no nodes with path found")
            return

        # 构造 DepgraphReader 并注入测试连接（绕过 get_depgraph_pg_connection）
        reader = DepgraphReader()
        reader._tls.conn = _PgConnExecuteWrapper(conn)

        # 收集测试 ID（path + blueprint_id 都测）
        test_ids: list[str] = []
        expected: dict[str, dict[str, str]] = {}
        for row in existing:
            bs = row["build_status"] or "planned"
            gr = row["gate_reason"] or ""
            entry = {"build_status": bs, "gate_reason": gr}
            for k in ("path", "blueprint_id"):
                v = row[k]
                if v:
                    test_ids.append(v)
                    expected[v] = entry

        # ① 正常查询：返回 dict 含正确 build_status + gate_reason
        result = reader.get_status_and_gate_map(test_ids)
        assert len(result) > 0, f"expected results for {test_ids}, got empty"
        for tid, exp in expected.items():
            assert tid in result, f"{tid} not in result"
            assert result[tid]["build_status"] == exp["build_status"], (
                f"{tid} build_status: got {result[tid]['build_status']}, expected {exp['build_status']}"
            )
            assert result[tid]["gate_reason"] == exp["gate_reason"], (
                f"{tid} gate_reason: got {result[tid]['gate_reason']!r}, expected {exp['gate_reason']!r}"
            )
            # 必须含 build_status + gate_reason 两个核心 key；
            # 允许返回结果新增元数据字段（如 acquisition_method/acquisition_source），
            # 故用 issuperset 而非严格相等，避免新增字段时测试误判失败（P0 修复 2026-08-05）
            assert set(result[tid].keys()).issuperset({"build_status", "gate_reason"})

        # ② 空输入 → 空 dict
        assert reader.get_status_and_gate_map([]) == {}
        assert reader.get_status_and_gate_map([""]) == {}

        # ③ 不存在的 ID → 不在返回 dict 中
        result_missing = reader.get_status_and_gate_map(["NONEXISTENT_PATH_xyz_123"])
        assert "NONEXISTENT_PATH_xyz_123" not in result_missing

        # 不调用 reader.close()——会关闭测试连接，由 finally 统一关闭
        print("PASS: test_get_status_and_gate_map")
    finally:
        conn.close()


if __name__ == "__main__":
    test_all()
    test_get_status_and_gate_map()
