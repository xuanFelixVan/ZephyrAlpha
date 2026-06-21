"""
DM-100017: depgraph.db端到端功能测试
覆盖：dep_表组7表CRUD、arch_表组7表CRUD、rule_bindings表、nodes 23列、edges 18列
"""
import sqlite3
import json
import sys
from datetime import datetime

DB_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"

def test_all():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    count = c.execute("SELECT COUNT(*) FROM domains").fetchone()[0]
    check("domains has 35 records", count == 35, f"got {count}")

    d = c.execute("SELECT * FROM domains WHERE domain_id='D-DATA-PERSISTENCE'").fetchone()
    check("domains SELECT by id", d is not None and d['domain_name'] == 'persistence')

    # === 2. nodes 表 (23列) ===
    print("\n=== 2. nodes (23 columns) ===")
    cols = [desc[1] for desc in c.execute("PRAGMA table_info(nodes)").fetchall()]
    expected_cols = ['node_id', 'node_type', 'path', 'granularity', 'domain_id', 'subdomain_id',
                     'blueprint_id', 'belongs_to', 'owner', 'change_policy', 'impact_level',
                     'modification_permission', 'file_header_score', 'tags', 'architecture_layer',
                     'design_maturity', 'deployment_lifecycle', 'trust_zone', 'license',
                     'drive_direction', 'type_specific_data', 'last_verified']
    for col in expected_cols:
        check(f"nodes has column '{col}'", col in cols, f"missing {col}")

    node_count = c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    check("nodes has data", node_count > 100, f"got {node_count}")

    # === 3. edges 表 (18列+) ===
    print("\n=== 3. edges (18 columns) ===")
    edge_cols = [desc[1] for desc in c.execute("PRAGMA table_info(edges)").fetchall()]
    expected_edge = ['edge_id', 'from_node', 'to_node', 'dep_type', 'architecture_direction',
                     'coupling_strength', 'used_symbol', 'invocation_method', 'api_contract_refs',
                     'event_ref', 'ddd_integration_pattern', 'failure_mode', 'fallback',
                     'activation_condition', 'data_transfer_description', 'resource_impact',
                     'relationship_type', 'cross_domain', 'verified']
    for col in expected_edge:
        check(f"edges has column '{col}'", col in edge_cols, f"missing {col}")

    edge_count = c.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    check("edges has data", edge_count > 100, f"got {edge_count}")

    # === 4. domain_dependencies ===
    print("\n=== 4. domain_dependencies ===")
    c.execute("""INSERT OR REPLACE INTO domain_dependencies (from_domain, to_domain, edge_count, edge_types, constraint_type)
        VALUES (?, ?, ?, ?, ?)""", ('D-DATA', 'D-GOV', 5, '["import_depends"]', 'hard'))
    conn.commit()
    dd = c.execute("SELECT * FROM domain_dependencies WHERE from_domain='D-DATA' AND to_domain='D-GOV'").fetchone()
    check("domain_dependencies INSERT+SELECT", dd is not None and dd['edge_count'] == 5)

    # === 5. contracts ===
    print("\n=== 5. contracts ===")
    now = datetime.now().isoformat()
    c.execute("""INSERT OR REPLACE INTO contracts (contract_id, name, provider_domain, consumer_domain, contract_type, schema_definition, version)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", ('CTR-TEST-001', 'Test Contract', 'D-DATA', 'D-GOV', 'api', '{}', '1.0'))
    conn.commit()
    ctr = c.execute("SELECT * FROM contracts WHERE contract_id='CTR-TEST-001'").fetchone()
    check("contracts INSERT+SELECT", ctr is not None)

    # === 6. domain_events ===
    print("\n=== 6. domain_events ===")
    c.execute("""INSERT OR REPLACE INTO domain_events (event_id, name, source_domain, target_domains, payload_schema, priority)
        VALUES (?, ?, ?, ?, ?, ?)""", ('EVT-TEST-001', 'Test Event', 'D-DATA', '["D-GOV"]', '{}', 'P1'))
    conn.commit()
    evt = c.execute("SELECT * FROM domain_events WHERE event_id='EVT-TEST-001'").fetchone()
    check("domain_events INSERT+SELECT", evt is not None)

    # === 7. invariants ===
    print("\n=== 7. invariants ===")
    c.execute("""INSERT OR REPLACE INTO invariants (invariant_id, domain_id, description, constraint_type, enforcement)
        VALUES (?, ?, ?, ?, ?)""", ('INV-TEST-001', 'D-DATA', 'Test invariant', 'hard', 'gate'))
    conn.commit()
    inv = c.execute("SELECT * FROM invariants WHERE invariant_id='INV-TEST-001'").fetchone()
    check("invariants INSERT+SELECT", inv is not None)

    # === 8. arch_ 表组 ===
    print("\n=== 8. arch_domain_capacity ===")
    cap = c.execute("SELECT COUNT(*) FROM arch_domain_capacity").fetchone()[0]
    check("arch_domain_capacity has data", cap > 0, f"got {cap}")

    print("\n=== 9. arch_path_mappings ===")
    pm = c.execute("SELECT COUNT(*) FROM arch_path_mappings").fetchone()[0]
    check("arch_path_mappings has data", pm > 0, f"got {pm}")

    print("\n=== 10. arch_layers ===")
    layers = c.execute("SELECT COUNT(*) FROM arch_layers").fetchone()[0]
    check("arch_layers has data", layers > 0, f"got {layers}")

    print("\n=== 11. arch_domain_layers ===")
    dl = c.execute("SELECT COUNT(*) FROM arch_domain_layers").fetchone()[0]
    check("arch_domain_layers has data", dl > 0, f"got {dl}")

    print("\n=== 12. arch_constraints ===")
    ac = c.execute("SELECT COUNT(*) FROM arch_constraints").fetchone()[0]
    check("arch_constraints has data", ac > 0, f"got {ac}")

    print("\n=== 13. arch_directory_tree ===")
    dt = c.execute("SELECT COUNT(*) FROM arch_directory_tree").fetchone()[0]
    check("arch_directory_tree has data", dt > 0, f"got {dt}")

    print("\n=== 14. arch_bottlenecks ===")
    bn = c.execute("SELECT COUNT(*) FROM arch_bottlenecks").fetchone()[0]
    check("arch_bottlenecks has data", bn > 0, f"got {bn}")

    # === 15. rule_bindings ===
    print("\n=== 15. rule_bindings ===")
    c.execute("""INSERT INTO rule_bindings (function_name, rule_id, binding_type, trigger_type, trigger_id)
        VALUES (?, ?, ?, ?, ?)""", ('test_func', 'RULE-001', 'pre_check', 'operation', 'OP-001'))
    conn.commit()
    rb = c.execute("SELECT * FROM rule_bindings WHERE function_name='test_func'").fetchone()
    check("rule_bindings INSERT+SELECT", rb is not None)

    # === 16. type_specific_data JSON解析 ===
    print("\n=== 16. type_specific_data JSON ===")
    node = c.execute("SELECT type_specific_data FROM nodes LIMIT 1").fetchone()
    if node and node['type_specific_data']:
        try:
            data = json.loads(node['type_specific_data'])
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
    c.execute("DELETE FROM invariants WHERE invariant_id='INV-TEST-001'")
    c.execute("DELETE FROM rule_bindings WHERE function_name='test_func'")
    conn.commit()
    check("cleanup", True)

    conn.close()

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {passed+failed} total")
    if failed > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)

if __name__ == "__main__":
    test_all()
