# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.verify_sync_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] YAML→DB sync完整性校验; 4维检查; exit 0=pass/1=fail
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验失败→exit 1+详细报告; 成功→exit 0+摘要
# [TESTS]
# [TTL] permanent
"""
sync 完整性校验脚本：验证 YAML→DB 同步的一致性。

4维校验：
1. YAML→DB 完整性：functional_domain_registry.yaml 的每个 domain 在 domains 表中存在
2. ssot_path 非空检查：YAML 有 ssot_path 的域，DB 中 ssot_path 不为 NULL
3. arch_path_mappings 同步：YAML 有 ssot_path 的域，arch_path_mappings 表有对应条目
4. 域计数一致性：YAML unique domain_id 数量与 DB domains 表数量匹配（允许 DB 有额外系统域）

用法：
    python scripts/governance/verify_sync_integrity.py
    python scripts/governance/verify_sync_integrity.py --verbose

退出码：
    0 = 全部通过
    1 = 有校验失败项
"""
import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装，请运行: pip install pyyaml")
    sys.exit(1)

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402

RULES_DIR = str(REPO_ROOT / "docs" / "01_policies_and_standards")
YAML_PATH = os.path.join(RULES_DIR, "_registry", "catalogs", "functional_domain_registry.yaml")

# SQL 集中化（§5.160.2）
_SQL_SELECT_DOMAINS = "SELECT domain_id, ssot_path FROM domains"
_SQL_SELECT_ARCH_PATHS = "SELECT DISTINCT domain_id FROM arch_path_mappings WHERE path_type = 'ssot'"


def load_yaml_entries():
    """加载 functional_domain_registry.yaml"""
    if not os.path.exists(YAML_PATH):
        print(f"[ERROR] YAML 文件不存在: {YAML_PATH}")
        sys.exit(1)
    with open(YAML_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _build_yaml_domain_map(entries):
    """从 YAML entries 构建 domain_id → ssot_path 映射"""
    yaml_domains = {}
    for d in entries:
        did = d.get("domain", "")
        if not did or not (did.startswith("D_") or did.startswith("D-")):
            continue
        if did not in yaml_domains:
            yaml_domains[did] = d.get("ssot_path", "")
    return yaml_domains


def _load_db_domains(cur):
    """从 DB 加载 domain_id → ssot_path 映射"""
    cur.execute(_SQL_SELECT_DOMAINS)
    return {row["domain_id"]: row["ssot_path"] for row in cur.fetchall()}


def _load_arch_path_domains(cur):
    """从 arch_path_mappings 加载有 ssot 条目的 domain_id 集合"""
    cur.execute(_SQL_SELECT_ARCH_PATHS)
    return {row["domain_id"] for row in cur.fetchall()}


def _check_completeness(yaml_domains, db_domains, verbose):
    """维度1: YAML→DB 完整性"""
    missing = [(did, sp) for did, sp in yaml_domains.items() if did not in db_domains]
    if missing and verbose:
        for did, sp in missing:
            print(f"  MISSING: {did} (ssot_path={sp})")
    return missing


def _check_ssot_path(yaml_domains, db_domains, verbose):
    """维度2: ssot_path 非空检查"""
    null_ssot = [
        (did, yaml_sp)
        for did, yaml_sp in yaml_domains.items()
        if yaml_sp and did in db_domains and db_domains[did] is None
    ]
    if null_ssot and verbose:
        for did, yaml_sp in null_ssot:
            print(f"  NULL ssot_path: {did} (YAML ssot_path={yaml_sp})")
    return null_ssot


def _check_arch_paths(yaml_domains, arch_path_domains, verbose):
    """维度3: arch_path_mappings 同步"""
    missing_arch = [
        (did, yaml_sp)
        for did, yaml_sp in yaml_domains.items()
        if yaml_sp and did not in arch_path_domains
    ]
    if missing_arch and verbose:
        for did, yaml_sp in missing_arch:
            print(f"  MISSING arch_path: {did} (ssot_path={yaml_sp})")
    return missing_arch


def verify_sync_integrity(verbose=False):
    """执行4维校验，返回 (passed, failures, yaml_count, db_count)"""
    data = load_yaml_entries()
    yaml_domains = _build_yaml_domain_map(data.get("entries", []))

    conn = get_depgraph_pg_connection(autocommit=True)
    cur = conn.cursor()
    db_domains = _load_db_domains(cur)
    arch_path_domains = _load_arch_path_domains(cur)
    conn.close()

    failures = []

    missing_in_db = _check_completeness(yaml_domains, db_domains, verbose)
    if missing_in_db:
        failures.append(("YAML→DB 完整性", f"{len(missing_in_db)} 个域在 YAML 中存在但 DB 缺失"))

    null_ssot = _check_ssot_path(yaml_domains, db_domains, verbose)
    if null_ssot:
        failures.append(("ssot_path 非空", f"{len(null_ssot)} 个域 YAML 有 ssot_path 但 DB 为 NULL"))

    missing_arch = _check_arch_paths(yaml_domains, arch_path_domains, verbose)
    if missing_arch:
        failures.append(("arch_path_mappings 同步", f"{len(missing_arch)} 个域有 ssot_path 但 arch_path_mappings 缺失"))

    if missing_in_db:
        failures.append(("域计数一致性", f"YAML={len(yaml_domains)}, DB={len(db_domains)}, 缺失={len(missing_in_db)}"))

    return (len(failures) == 0), failures, len(yaml_domains), len(db_domains)


def main():
    parser = argparse.ArgumentParser(description="YAML→DB sync 完整性校验")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    args = parser.parse_args()

    print("=" * 60)
    print("YAML→DB Sync 完整性校验")
    print("=" * 60)

    passed, failures, yaml_count, db_count = verify_sync_integrity(verbose=args.verbose)

    print(f"\nYAML 域数: {yaml_count}")
    print(f"DB 域数: {db_count}")

    if passed:
        print("\n[PASS] 全部4维校验通过")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {len(failures)} 维校验失败:")
        for check, msg in failures:
            print(f"  - {check}: {msg}")
        print("\n建议: 重新运行 sync_yaml_to_depgraph.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
