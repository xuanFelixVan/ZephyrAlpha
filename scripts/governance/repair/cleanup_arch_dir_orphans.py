# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §depgraph
# [MODULE] zephyr.governance.repair.cleanup_arch_dir_orphans
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DB_cleanup_arch_dir | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
5.18.9 治本：arch_directory_tree 683 孤儿 domain_id 清理 + 补 FK
=================================================================
执行前提：已 git commit 备份（约束#7）

清理策略：
  1. D_GOV_SCRIPTS-META (498行) → D_GOV_SCRIPTS（已存在于 domains 表）
  2. D_GOV_SCRIPTS-ARCH (82行)  → D_GOV_SCRIPTS
  3. '' 空串 (103行)            → NULL（语义规范化）
  4. 补 FK: arch_directory_tree.domain_id REFERENCES domains(domain_id)

用法：
    python scripts/governance/repair/cleanup_arch_dir_orphans.py
    python scripts/governance/repair/cleanup_arch_dir_orphans.py --dry-run  # 只查不写
"""

from __future__ import annotations

import sys

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection


def main(dry_run: bool = False) -> int:
    print("=" * 70)
    print("5.18.9 治本：arch_directory_tree 孤儿清理 + 补 FK")
    print("=" * 70)

    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            # === 步骤 0：清理前审计 ===
            cur.execute("""
                SELECT t.domain_id, COUNT(*) as cnt
                FROM arch_directory_tree t
                WHERE t.domain_id IS NOT NULL
                AND t.domain_id NOT IN (SELECT domain_id FROM domains)
                GROUP BY t.domain_id ORDER BY cnt DESC
            """)
            orphans_before = cur.fetchall()
            total_orphans = sum(r[1] for r in orphans_before)
            print(f"\n[步骤0] 清理前审计：{total_orphans} 孤儿")
            for row in orphans_before:
                domain_id = row[0] if row[0] else "''(空串)"
                print(f"  domain_id={domain_id}: {row[1]} 行")

            if total_orphans == 0:
                print("\n✓ 无孤儿，跳过清理")

            # === 步骤 1：修正 D_GOV_SCRIPTS-META/D_GOV_SCRIPTS-ARCH → D_GOV_SCRIPTS ===
            if total_orphans > 0 and not dry_run:
                cur.execute("""
                    UPDATE arch_directory_tree
                    SET domain_id = 'D_GOV_SCRIPTS'
                    WHERE domain_id IN ('D_GOV_SCRIPTS-META', 'D_GOV_SCRIPTS-ARCH')
                """)
                fixed_scripts = cur.rowcount
                print(f"\n[步骤1] D_GOV_SCRIPTS-META/ARCH → D_GOV_SCRIPTS: {fixed_scripts} 行已修正")

                # === 步骤 2：空串 → NULL ===
                cur.execute("""
                    UPDATE arch_directory_tree
                    SET domain_id = NULL
                    WHERE domain_id = ''
                """)
                fixed_empty = cur.rowcount
                print(f"[步骤2] 空串 → NULL: {fixed_empty} 行已修正")
            elif dry_run and total_orphans > 0:
                print("\n[dry-run] 跳过 UPDATE 操作")

            # === 步骤 3：验证孤儿已清除 ===
            if not dry_run:
                cur.execute("""
                    SELECT COUNT(*) FROM arch_directory_tree t
                    WHERE t.domain_id IS NOT NULL
                    AND t.domain_id NOT IN (SELECT domain_id FROM domains)
                """)
                remaining = cur.fetchone()[0]
                print(f"\n[步骤3] 验证：剩余孤儿 {remaining}")
                if remaining > 0:
                    print("✗ 清理失败，仍有孤儿残留")
                    conn.rollback()
                    return 1

                # === 步骤 4：补 FK ===
                # 先检查 FK 是否已存在
                cur.execute("""
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_arch_dir_domain'
                    AND table_name = 'arch_directory_tree'
                """)
                if cur.fetchone():
                    print("[步骤4] FK fk_arch_dir_domain 已存在，跳过")
                else:
                    cur.execute("""
                        ALTER TABLE arch_directory_tree
                        ADD CONSTRAINT fk_arch_dir_domain
                        FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
                    """)
                    print("[步骤4] FK fk_arch_dir_domain 已添加")

                conn.commit()
                print("\n✓ 5.18.9 治本完成：孤儿已清理 + FK 已补齐")

            if dry_run:
                print("\n[dry-run] 未执行任何修改")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ 错误: {e}")
        return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry))
