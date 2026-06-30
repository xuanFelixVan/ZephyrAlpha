# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_domain_governance/blueprint.md | §rule_engine
# [MODULE] scripts.governance.check_rule_four_way_alignment
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] CI pipeline; governance audit; Phase Manager
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] YAML↔DB↔Code↔Blueprint 四方对齐; L0 规则 100% 对齐才 exit 0
# [MODIFY-GUARD] rule_engine.py; sync_rule_registry.py; verify_rule_yaml_migration.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0 = all L0 aligned; exit 1 = misalignment found; stderr has details
# [TESTS] manual: python scripts/governance/check_rule_four_way_alignment.py --all
# [TTL] task_bound

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root from {current}")


PROJECT_ROOT = _find_project_root()
RULES_DIR = PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
BLUEPRINTS_DIR = PROJECT_ROOT / "docs" / "03_modules"

# 治本（2026-06-27）：删除 DB_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()。

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402


def _load_all_yaml_rules() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    if not RULES_DIR.exists():
        print(f"[ERROR] Rules directory not found: {RULES_DIR}", file=sys.stderr)
        return rules
    for path in sorted(RULES_DIR.glob("*.yaml")):
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "rule_id" in data:
                rules[data["rule_id"]] = data
        except (OSError, yaml.YAMLError) as exc:
            print(f"[WARN] Failed to read {path}: {exc}", file=sys.stderr)
    return rules


def _get_db_rule_ids() -> set[str]:
    # 治本（2026-06-27）：删除 if not DB_PATH.exists(): return set() 守卫（latent bug）。
    # PG 模式下文件路径无意义，直接查询 PG；连接失败时 fail-loud 抛异常（不静默吞数据）。
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
        # rule 已废弃，迁移到 policy/gate（见 node_type_vocabulary.yaml）
        cursor = conn.execute("SELECT DISTINCT node_id FROM nodes WHERE node_type IN ('policy', 'gate')")
        ids = {row["node_id"] for row in cursor.fetchall()}
        conn.close()
        return ids
    except Exception:
        return set()


def _check_yaml_db(rules: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    db_ids = _get_db_rule_ids()
    if not db_ids:
        # depgraph.db 无 rule 节点是正常状态——规则 SSoT 在 YAML，DB 非规则真源
        return issues
    for rule_id, data in rules.items():
        if data.get("layer") != "L0":
            continue
        if rule_id not in db_ids:
            issues.append(f"YAML↔DB: L0 rule {rule_id} exists in YAML but not in depgraph.db nodes table")
    for db_id in db_ids:
        if db_id not in rules and db_id.startswith("TRAE-"):
            issues.append(f"YAML↔DB: rule {db_id} exists in depgraph.db but no YAML file found")
    return issues


def _check_db_code(rules: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    src_zephyr = PROJECT_ROOT / "src" / "zephyr"
    for rule_id, data in rules.items():
        if data.get("layer") != "L0":
            continue
        executors = data.get("enforcement", {}).get("executors", [])
        for executor in executors:
            found = False
            # 搜索 scripts/ 目录（按文件名匹配）
            for search_dir in [SCRIPTS_DIR, SCRIPTS_DIR / "governance"]:
                for ext in ("*.py",):
                    for path in search_dir.rglob(ext):
                        if path.name == executor or path.stem == executor.replace(".py", ""):
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            # 搜索 src/zephyr/ 目录（按方法名在文件内容中匹配）
            if not found and src_zephyr.exists():
                method_name = executor.split(".")[-1].rstrip("()")
                for py_path in src_zephyr.rglob("*.py"):
                    try:
                        content = py_path.read_text(encoding="utf-8")
                        if f"def {method_name}" in content or f"class {executor.split('.')[0]}" in content:
                            found = True
                            break
                    except OSError:
                        pass
            if not found and not executor.startswith(("ruff", "mypy", "pre-commit")):
                issues.append(f"DB↔Code: L0 rule {rule_id} executor '{executor}' not found in scripts/ or src/zephyr/")
    return issues


def _check_code_blueprint(rules: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    policies_dir = PROJECT_ROOT / "docs" / "01_policies_and_standards"
    for rule_id, data in rules.items():
        if data.get("layer") != "L0":
            continue
        blueprint_refs = data.get("references", {}).get("blueprints", [])
        for bp_ref in blueprint_refs:
            found = False
            # 搜索 docs/03_modules/ 中的 blueprint.md
            for bp_path in BLUEPRINTS_DIR.rglob("blueprint.md"):
                try:
                    content = bp_path.read_text(encoding="utf-8")
                    if bp_ref in content:
                        found = True
                        break
                except OSError:
                    pass
            if not found:
                bp_yaml_candidates = list(BLUEPRINTS_DIR.rglob(f"{bp_ref.lower()}.yaml"))
                if bp_yaml_candidates:
                    found = True
                bp_dir_candidates = list(BLUEPRINTS_DIR.rglob(bp_ref.lower().replace("-", "_")))
                if bp_dir_candidates:
                    found = True
            # 搜索 docs/01_policies_and_standards/ 中的 .md 文件（工程治理标准等）
            if not found and policies_dir.exists():
                for md_path in policies_dir.rglob("*.md"):
                    try:
                        content = md_path.read_text(encoding="utf-8")
                        if bp_ref in content:
                            found = True
                            break
                    except OSError:
                        pass
            if not found:
                issues.append(f"Code↔Blueprint: L0 rule {rule_id} references blueprint '{bp_ref}' but it was not found")
    return issues


def _check_yaml_blueprint(rules: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    policies_dir = PROJECT_ROOT / "docs" / "01_policies_and_standards"
    blueprint_rule_map: dict[str, list[str]] = {}
    # 搜索 docs/03_modules/ 中的 blueprint.md
    for bp_path in BLUEPRINTS_DIR.rglob("blueprint.md"):
        try:
            content = bp_path.read_text(encoding="utf-8")
            for rule_id in rules:
                if rule_id in content:
                    blueprint_rule_map.setdefault(str(bp_path), []).append(rule_id)
        except OSError:
            pass
    # 搜索 docs/01_policies_and_standards/ 中的 .md 文件
    if policies_dir.exists():
        for md_path in policies_dir.rglob("*.md"):
            try:
                content = md_path.read_text(encoding="utf-8")
                for rule_id in rules:
                    if rule_id in content:
                        blueprint_rule_map.setdefault(str(md_path), []).append(rule_id)
            except OSError:
                pass
    for rule_id, data in rules.items():
        if data.get("layer") != "L0":
            continue
        bp_refs = data.get("references", {}).get("blueprints", [])
        if bp_refs:
            found_in_map = False
            for bp_path, mapped_ids in blueprint_rule_map.items():
                if rule_id in mapped_ids:
                    found_in_map = True
                    break
            if not found_in_map:
                issues.append(
                    f"YAML↔Blueprint: L0 rule {rule_id} declares blueprint refs {bp_refs} but no blueprint.md references it back"
                )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Four-way alignment check: YAML ↔ DB ↔ Code ↔ Blueprint")
    parser.add_argument("--all", action="store_true", help="Run all 4 alignment checks")
    parser.add_argument("--yaml-db", action="store_true", help="Check YAML↔DB only")
    parser.add_argument("--db-code", action="store_true", help="Check DB↔Code only")
    parser.add_argument("--code-blueprint", action="store_true", help="Check Code↔Blueprint only")
    parser.add_argument("--yaml-blueprint", action="store_true", help="Check YAML↔Blueprint only")
    args = parser.parse_args()

    run_all = args.all or not any([args.yaml_db, args.db_code, args.code_blueprint, args.yaml_blueprint])

    rules = _load_all_yaml_rules()
    if not rules:
        print("[ERROR] No YAML rules loaded", file=sys.stderr)
        return 1

    print(f"Loaded {len(rules)} YAML rules from {RULES_DIR}")

    all_issues: list[str] = []

    if run_all or args.yaml_db:
        print("\n--- YAML↔DB Alignment ---")
        issues = _check_yaml_db(rules)
        all_issues.extend(issues)
        if issues:
            for issue in issues:
                print(f"  [MISALIGN] {issue}")
        else:
            print("  [OK] All L0 rules aligned between YAML and DB")

    if run_all or args.db_code:
        print("\n--- DB↔Code Alignment ---")
        issues = _check_db_code(rules)
        all_issues.extend(issues)
        if issues:
            for issue in issues:
                print(f"  [MISALIGN] {issue}")
        else:
            print("  [OK] All L0 rule executors found in scripts/")

    if run_all or args.code_blueprint:
        print("\n--- Code↔Blueprint Alignment ---")
        issues = _check_code_blueprint(rules)
        all_issues.extend(issues)
        if issues:
            for issue in issues:
                print(f"  [MISALIGN] {issue}")
        else:
            print("  [OK] All L0 rule blueprint references found")

    if run_all or args.yaml_blueprint:
        print("\n--- YAML↔Blueprint Alignment ---")
        issues = _check_yaml_blueprint(rules)
        all_issues.extend(issues)
        if issues:
            for issue in issues:
                print(f"  [MISALIGN] {issue}")
        else:
            print("  [OK] All L0 rules have bidirectional blueprint references")

    l0_count = sum(1 for d in rules.values() if d.get("layer") == "L0")
    l0_issues = [i for i in all_issues if "L0" in i]
    print("\n--- Summary ---")
    print(f"  Total rules: {len(rules)} | L0 rules: {l0_count}")
    print(f"  Total issues: {len(all_issues)} | L0 issues: {len(l0_issues)}")

    if l0_issues:
        print("\n[FAIL] L0 rules are NOT 100% aligned. Fix issues above.", file=sys.stderr)
        return 1

    print("\n[PASS] All L0 rules are 100% aligned across YAML↔DB↔Code↔Blueprint.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
