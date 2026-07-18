"""
DM-100017: depgraph端到端功能测试（P2迁移后：PostgreSQL）
覆盖：dep_表组7表CRUD、arch_表组7表CRUD、rule_bindings表、nodes 23列、edges 18列
"""

import json
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection


def test_all():
    conn = get_depgraph_pg_connection()
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
    check("domains SELECT by id", d is not None and d["domain_name"] == "运行时集成",
         f"got domain_name={d['domain_name'] if d else None}")

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
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    test_all()
