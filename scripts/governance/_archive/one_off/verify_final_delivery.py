# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.verify_final_delivery
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/verify_final_delivery.py | §11最终交付验证
[MODULE] 无（独立脚本）
[INVARIANTS] 设计态节点数>=1128; 规则表各表>0
[MODIFY-GUARD] 本脚本由autopilot执行
[CONSUMERS] autopilot session-20260618-001
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 验证失败→exit 1; 验证通过→exit 0
[TESTS] 无

§11最终交付验证
- 设计态节点数 >= 1128
- 规则表数据：gates/field_vocabularies/registries/hard_boundaries/business_streams/blueprint_links 各表 > 0
"""

import os
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import DB_PATH, get_depgraph_pg_connection  # noqa: E402


def main():
    print("=" * 60)
    print("§11 最终交付验证")
    print("=" * 60)

    all_pass = True

    # 1. 设计态节点数验证
    print("\n[1] 设计态节点数验证（>= 1128）")
    conn = get_depgraph_pg_connection(autocommit=True)
    r = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE design_maturity='design'").fetchone()
    design_count = r["cnt"]
    if design_count >= 1128:
        print(f"  ✅ PASS: 设计态节点数 {design_count} >= 1128")
    else:
        print(f"  ❌ FAIL: 设计态节点数 {design_count} < 1128")
        print("     原因：MIG-5补缺步骤未执行，1012个缺失项未补入")
        print("     修复：执行MIG-5 M5-2补缺步骤（--add-design-node）")
        all_pass = False
    conn.close()

    # 2. 规则表数据验证（各表 > 0）- 规则表在depgraph中
    print("\n[2] 规则表数据验证（各表 > 0）")
    conn = get_depgraph_pg_connection(autocommit=True)
    tables = ["gates", "field_vocabularies", "registries", "hard_boundaries", "business_streams", "blueprint_links"]
    for table in tables:
        try:
            # 检查表是否存在（P2迁移后改用 information_schema）
            r = conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
                (table,),
            ).fetchone()
            if r is None:
                print(f"  ❌ FAIL: 表 {table} 不存在")
                all_pass = False
                continue
            r = conn.execute(f"SELECT COUNT(*) AS cnt FROM {table}").fetchone()
            count = r["cnt"]
            if count > 0:
                print(f"  ✅ PASS: {table} = {count}")
            else:
                print(f"  ❌ FAIL: {table} = 0")
                all_pass = False
        except Exception as e:
            print(f"  ❌ FAIL: {table} 查询失败: {e}")
            all_pass = False
    conn.close()

    # 3. depgraph基本验证
    print("\n[3] depgraph基本验证")
    conn = get_depgraph_pg_connection(autocommit=True)
    r = conn.execute("SELECT COUNT(*) AS cnt FROM nodes").fetchone()
    print(f"  总节点数: {r['cnt']}")
    r = conn.execute("SELECT COUNT(*) AS cnt FROM edges").fetchone()
    print(f"  总边数: {r['cnt']}")
    r = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE design_maturity='design'").fetchone()
    print(f"  设计态节点: {r['cnt']}")
    r = conn.execute("SELECT COUNT(*) AS cnt FROM edges WHERE dep_maturity='design'").fetchone()
    print(f"  设计态边: {r['cnt']}")
    r = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE design_maturity!='design' OR design_maturity IS NULL").fetchone()
    print(f"  运营态节点: {r['cnt']}")
    r = conn.execute("SELECT COUNT(*) AS cnt FROM edges WHERE dep_maturity!='design' OR dep_maturity IS NULL").fetchone()
    print(f"  运营态边: {r['cnt']}")

    # 4. edges完整性验证
    print("\n[4] edges完整性验证")
    r = conn.execute("""
        SELECT COUNT(*) AS cnt FROM edges e
        WHERE NOT EXISTS (SELECT 1 FROM nodes n WHERE n.node_id = e.from_node_id)
           OR NOT EXISTS (SELECT 1 FROM nodes n WHERE n.node_id = e.to_node_id)
    """).fetchone()
    print(f"  悬空边: {r['cnt']}")
    if r["cnt"] > 0:
        print(f"  ❌ FAIL: 存在{r['cnt']}条悬空边")
        all_pass = False
    else:
        print("  ✅ PASS: 无悬空边")

    conn.close()

    # 5. 交付物验证
    print("\n[5] 交付物验证")
    # depgraph 已迁移至 PostgreSQL，验证 PG 连接可用性
    try:
        _pg_conn = get_depgraph_pg_connection(autocommit=True)
        _pg_conn.execute("SELECT 1").fetchone()
        _pg_conn.close()
        print("  ✅ PASS: depgraph (PostgreSQL) 连接可用")
    except Exception as e:
        print(f"  ❌ FAIL: depgraph (PostgreSQL) 连接失败: {e}")
        all_pass = False
    # governance.db 仍为 SQLite，验证文件存在
    if DB_PATH.exists():
        _gov_size = os.path.getsize(DB_PATH)
        print(f"  ✅ PASS: governance.db ({_gov_size} bytes)")
    else:
        print(f"  ❌ FAIL: governance.db 不存在")
        all_pass = False

    # 总结
    print("\n" + "=" * 60)
    if all_pass:
        print("✅ §11 最终交付验证通过")
        exit(0)
    else:
        print("❌ §11 最终交付验证失败")
        exit(1)


if __name__ == "__main__":
    main()
