#!/usr/bin/env python3
# [A_module] module_id=MOD-migrate_sqlite_to_pg | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable

# [BLUEPRINT] MOD-migrate_sqlite_to_pg | docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md | §seed_from_yaml
# [MODULE] scripts.governance.migrate_sqlite_to_pg.seed_from_yaml
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d8_doc_sync.sync_yaml_to_depgraph (sync_all); scripts.governance._shared.constants (EXIT codes)
# [CONSUMERS] manual（迁移运维流程，README 执行顺序节）; scripts.governance.migrate_sqlite_to_pg.migrate_data（姊妹脚本）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 种子表真源在 YAML（trae_062 规则数据），DB 是只读缓存;本脚本不实现同步逻辑，仅委托 sync_yaml_to_depgraph.sync_all()（向内收，复用唯一真源）
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=种子同步成功; exit 1=同步失败/DB 连接失败
# [TESTS] tests/governance/test_migrate_sqlite_to_pg.py（SEED_TABLES 一致性测试）
# [TTL] task_bound
"""
seed_from_yaml.py — 从 YAML 真源灌种子表（5.32.10 治本：种子与迁移拆分）
========================================================================
将 YAML 真源种子表（domains/gates/registries/field_vocabularies 等规则数据）
灌入 PostgreSQL。与 migrate_data.py（运营数据迁移）职责分离：

    * 本脚本：规则数据——真源在 YAML 文件（trae_062 真源分类铁律），
      DB 是只读缓存。从 SQLite 旧缓存搬这些数据 = 搬漂移。
    * migrate_data.py：架构/运营数据（nodes/edges/governance_audit_logs 等）——
      真源在 DB，从 SQLite 一次性迁移。

使用方式:
    python scripts/governance/migrate_sqlite_to_pg/seed_from_yaml.py

执行顺序（详见同目录 README.md）:
    01_create_extensions.sql → 02_create_pg_schema.sql
    → seed_from_yaml.py（本脚本，先灌种子表——nodes 等表 FK 引用 domains）
    → migrate_data.py（运营数据迁移）

实现说明:
    同步逻辑唯一真源是 scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py
    （27 项 YAML→DB 单向同步，含只读触发器通行证机制）。本脚本仅做薄封装：
    打印种子表清单 + 调用 sync_all() + 映射退出码。禁止在此复制同步逻辑。
"""

__manifest__ = """
args: []
description: 从 YAML 真源灌种子表（5.32.10 种子与迁移拆分，委托 sync_yaml_to_depgraph）
dimensions:
- D1
priority: P2
timeout_seconds: 120
warn_only: false
"""


import sys
from pathlib import Path

# Bootstrap: 基于 .git marker 定位仓库根 + scripts/governance 入 sys.path
# （d8_doc_sync 是 scripts/governance 下的包，对齐 apply_depgraph.py 的
# `from d8_doc_sync.audit_rename_completeness import scan_residual` 导入模式）
_PROJECT_ROOT = Path(__file__).resolve()
while not (_PROJECT_ROOT / ".git").exists() and _PROJECT_ROOT.parent != _PROJECT_ROOT:
    _PROJECT_ROOT = _PROJECT_ROOT.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# === 种子表清单（与 migrate_data.SEED_TABLES 一致，单一声明点在此） ===
# 这些表由 sync_yaml_to_depgraph.py 从 YAML 真源同步，不在 migrate_data.py 迁移。
SEED_TABLES = (
    "domains",
    "arch_constraints",
    "arch_directory_tree",
    "arch_path_mappings",
    "blueprint_links",
    "business_streams",
    "contracts",
    "cross_registry_rules",
    "derived_identifier_registry",
    "domain_naming_rules",
    "field_vocabularies",
    "gates",
    "hard_boundaries",
    "infrastructure_components",
    "model_capabilities",
    "registries",
)


def seed_from_yaml() -> bool:
    """从 YAML 真源同步全部种子表到 depgraph (PostgreSQL)。

    委托 sync_yaml_to_depgraph.sync_all()（同步逻辑唯一真源，向内收）。
    返回 True=同步成功，False=失败。
    """
    from d8_doc_sync.sync_yaml_to_depgraph import sync_all

    return sync_all()


def main():
    """Entry point: parse args, run logic, return exit code."""
    print("=== 种子表灌入（YAML 真源 → depgraph PostgreSQL） ===")
    print(f"种子表（{len(SEED_TABLES)} 张，真源在 YAML，trae_062 规则数据）:")
    for tbl in SEED_TABLES:
        print(f"  - {tbl}")
    print("\n委托 sync_yaml_to_depgraph.sync_all() 执行同步...\n")

    ok = seed_from_yaml()
    if ok:
        print("\n[OK] 种子表同步完成。下一步: python scripts/governance/migrate_sqlite_to_pg/migrate_data.py")
        sys.exit(EXIT_PASS)
    print("\n[ERROR] 种子表同步失败（详见上方 sync_yaml_to_depgraph 输出）")
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
