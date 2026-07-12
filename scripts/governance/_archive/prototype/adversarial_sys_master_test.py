# [BLUEPRINT] MOD-INF-005 | scripts/governance/adversarial_sys_master_test.py | §
# [MODULE] scripts.governance.adversarial_sys_master_test
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.sys_master_compliance
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
Red/Blue Team Adversarial Test v3: SYS-MASTER-001 + MOD-MASTER_BLUEPRINT Integration Hardening

Red Team: 模拟攻击——破坏 frontmatter / registry / cold start / crosscheck
Blue Team: 系统防御——SYS-MASTER-CMP gate + crosscheck_sys_master_deps.py

exit 0 = 所有攻击被防御系统检测到（预期行为）
exit 1 = 至少一个攻击未被检测到（漏洞）
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from _shared.constants import REPO_ROOT

PROJECT_ROOT = REPO_ROOT
GATE = [sys.executable, str(PROJECT_ROOT / "src" / "zephyr" / "gates" / "sys_master_compliance.py"), "--json"]


def run_gate() -> list[dict]:
    """run_gate implementation - call check functions directly to avoid subprocess/argv issues."""
    from zephyr.gov_enforcement.rule_enforcement.sys_master_compliance import (
        check_ai_rules_count,
        check_blueprint_existence,
        check_cold_start_integration,
        check_construction_progress_consistency,
        check_crosscheck_script,
        check_depends_on_integrity,
        check_gate_registry_entry,
        check_sli_data_sources,
        check_version_consistency,
    )

    all_checks = []
    all_checks.extend(check_blueprint_existence())
    all_checks.extend(check_cold_start_integration())
    all_checks.extend(check_depends_on_integrity())
    all_checks.extend(check_construction_progress_consistency())
    all_checks.extend(check_version_consistency())
    all_checks.extend(check_ai_rules_count())
    all_checks.extend(check_gate_registry_entry())
    all_checks.extend(check_sli_data_sources())
    all_checks.extend(check_crosscheck_script())
    return all_checks


class Attack:
    def __init__(self, name: str):
        """__init__ implementation."""
        self.name = name
        self.detected = False
        self.detail = ""

    def execute(self, attack_fn, restore_fn, check_label):
        """Execute attack with proper restore sequence."""
        backup = attack_fn()
        try:
            post_attack = run_gate()
        finally:
            restore_fn(backup)
        found = [f for f in post_attack if check_label in f.get("label", "")]
        if found:
            self.detected = found[0]["status"] == "FAIL"
            self.detail = found[0].get("detail", "")
        else:
            self.detail = f"check_label '{check_label}' not found in gate output"


def extract_fm_boundaries(text: str) -> tuple[str, str]:
    """Use same regex as extract_frontmatter to find YAML frontmatter boundaries."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        raise RuntimeError("Cannot find frontmatter boundaries")
    fm_end = m.end()
    return text[:fm_end], text[fm_end:]


# ============================================================
# Attack 1: MOD-MASTER_BLUEPRINT frontmatter construction_progress corruption
# ============================================================


def attack_01_frontmatter() -> Attack:
    """attack_01_frontmatter implementation."""
    a = Attack("M01-frontmatter_corruption")
    bp = PROJECT_ROOT / "docs" / "03_modules" / "_master-blueprint" / "blueprint.md"

    def attack_fn():
        """attack_fn implementation."""
        original = bp.read_text(encoding="utf-8")
        corrupted = re.sub(
            r"construction_progress: \S+",
            "construction_progress: phase_9_broken",
            original,
            count=1,
        )
        bp.write_text(corrupted, encoding="utf-8")
        return original

    def restore(backup):
        """restore implementation."""
        bp.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "MOD-MASTER_BLUEPRINT construction_progress_consistency")
    return a


# ============================================================
# Attack 2: blueprint_registry.yaml drift for SYS-MASTER-001
# ============================================================


def attack_02_registry() -> Attack:
    """attack_02_registry implementation."""
    a = Attack("M02-registry_drift")
    reg = PROJECT_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"

    def attack_fn():
        """attack_fn implementation."""
        original = reg.read_text(encoding="utf-8")
        lines = original.splitlines(True)
        in_sys = False
        for i, line in enumerate(lines):
            if "module_id: SYS-MASTER-001" in line:
                in_sys = True
            if in_sys and "construction_progress: completed" in line:
                lines[i] = line.replace("completed", "DRIFTED_not_started")
                break
        reg.write_text("".join(lines), encoding="utf-8")
        return original

    def restore(backup):
        """restore implementation."""
        reg.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "SYS-MASTER-001 construction_progress_consistency")
    return a


# ============================================================
# Attack 3: SYS-MASTER-001 depends_on MOD-MASTER_BLUEPRINT broken
# Attack：将 depends_on 中 MOD-MASTER_BLUEPRINT 的 target 改为不存在值
# Gate防御：check_depends_on_integrity() YAML解析 depends_on，检查 target=="MOD-MASTER_BLUEPRINT"
# ============================================================


def attack_03_depends_on() -> Attack:
    """attack_03_depends_on implementation."""
    a = Attack("M03-depends_on_broken")
    bp = PROJECT_ROOT / "docs" / "03_modules" / "_system_master" / "blueprint.md"

    def attack_fn():
        """attack_fn implementation."""
        original = bp.read_text(encoding="utf-8")
        fm_part, body = extract_fm_boundaries(original)
        broken_fm = fm_part.replace('{target: "MOD-MASTER_BLUEPRINT"', '{target: "ATTACK_DELETED_999"')
        bp.write_text(broken_fm + body, encoding="utf-8")
        return original

    def restore(backup):
        """restore implementation."""
        bp.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "depends_on_integrity")
    return a


# ============================================================
# Attack 4: project_rules.md cold start reference to SYS-MASTER-001 removed
# Attack：删除 project_rules.md 冷启动序列中对 SYS-MASTER-001 的引用
# Gate防御：check_cold_start_integration() 搜索 STEP 1..STEP 5 区间内的 SYS-MASTER 或 _system_master
# ============================================================


def attack_04_cold_start() -> Attack:
    """attack_04_cold_start implementation."""
    a = Attack("M04-cold_start_removal")
    rules = PROJECT_ROOT / ".trae" / "rules" / "project_rules.md"

    def attack_fn():
        """attack_fn implementation."""
        original = rules.read_text(encoding="utf-8")
        removed = original.replace("_system_master", "_ATTACK_REMOVED_REF")
        removed = removed.replace("SYS-MASTER-001", "ATTACK_DELETED_MASTER")
        rules.write_text(removed, encoding="utf-8")
        return original

    def restore(backup):
        """restore implementation."""
        rules.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "cold_start_integration")
    return a


# ============================================================
# Attack 5: crosscheck_sys_master_deps.py broken (syntax error injected)
# Attack：在脚本中注入 raise SystemExit(1) 导致 subprocess 返回非零
# Gate防御：check_crosscheck_script() subprocess.run 检查 exit code
# ============================================================


def attack_05_crosscheck() -> Attack:
    """attack_05_crosscheck implementation."""
    a = Attack("M05-crosscheck_broken")
    script = PROJECT_ROOT / "scripts" / "governance" / "crosscheck_sys_master_deps.py"

    def attack_fn():
        """attack_fn implementation."""
        original = script.read_text(encoding="utf-8")
        broken = original.replace("def main() -> int:", "def main() -> int:\n    raise SystemExit(99)")
        script.write_text(broken, encoding="utf-8")
        return original

    def restore(backup):
        """restore implementation."""
        script.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "crosscheck_script_pass")
    return a


# ============================================================
# Attack 6: MOD-MASTER_BLUEPRINT blueprint deleted
# Attack：物理删除 MOD-MASTER_BLUEPRINT 蓝图文件
# Gate防御：check_blueprint_existence() 检查文件存在
# ============================================================


def attack_06_missing() -> Attack:
    """attack_06_missing implementation."""
    a = Attack("M06-missing_blueprint")
    bp = PROJECT_ROOT / "docs" / "03_modules" / "_master-blueprint" / "blueprint.md"

    def attack_fn():
        """attack_fn implementation."""
        original = bp.read_text(encoding="utf-8")
        bp.unlink()
        return original

    def restore(backup):
        """restore implementation."""
        bp.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "MOD-MASTER_BLUEPRINT blueprint_exists")
    return a


# ============================================================
# Attack 7: SYS-MASTER-001 AI rules count reduced below 76
# Attack：替换编号为 (!) (@) 减少规则计数
# Gate防御：check_ai_rules_count() re.findall 计数 >= 76
# ============================================================


def attack_07_rules() -> Attack:
    """attack_07_rules implementation."""
    a = Attack("M07-ai_rules_regression")
    bp = PROJECT_ROOT / "docs" / "03_modules" / "_system_master" / "blueprint.md"

    def attack_fn():
        """attack_fn implementation."""
        original = bp.read_text(encoding="utf-8")
        fm_part, body = extract_fm_boundaries(original)
        reduced_fm = fm_part.replace("(1)", "(!)").replace("(2)", "(@)")
        bp.write_text(reduced_fm + body, encoding="utf-8")
        return original

    def restore(backup):
        """restore implementation."""
        bp.write_text(backup, encoding="utf-8")

    a.execute(attack_fn, restore, "ai_rules_count")
    return a


# ============================================================
# Main
# ============================================================


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    banner = "=" * 60
    print(f"\n{banner}")
    print("  Red/Blue Team Adversarial Test v3: SYS-MASTER-001 + MOD-MASTER_BLUEPRINT")
    print(banner)

    attacks = [
        attack_01_frontmatter,
        attack_02_registry,
        attack_03_depends_on,
        attack_04_cold_start,
        attack_05_crosscheck,
        attack_06_missing,
        attack_07_rules,
    ]

    results = []
    for i, fn in enumerate(attacks, 1):
        print(f"\n[M{i}] {fn.__name__}")
        try:
            a = fn()
        except Exception as e:
            a = Attack(f"M{i}-CRASH")
            a.detail = f"Exception: {e}"
            results.append(a)
            print(f"  CRASH {e}")
            continue
        icon = "PASS" if a.detected else "MISS"
        print(f"  [{icon}] detected={a.detected}  {a.detail}")
        results.append(a)

    detected = sum(1 for r in results if r.detected)
    missed = sum(1 for r in results if not r.detected)
    print(f"\n{banner}")
    print(f"  TOTAL: {len(results)} attacks, {detected} DETECTED, {missed} MISSED")
    print(banner)

    report = {
        "test_type": "adversarial",
        "version": 3,
        "target": ["SYS-MASTER-001", "MOD-MASTER_BLUEPRINT"],
        "defense_gate": "SYS-MASTER-CMP",
        "date": "2026-05-07",
        "executor": "session-20260507-999",
        "summary": {
            "total_attacks": len(results),
            "detected": detected,
            "missed": missed,
            "detection_rate": f"{detected}/{len(results)}",
        },
        "attacks": [{"name": r.name, "detected": r.detected, "detail": r.detail} for r in results],
    }

    report_path = PROJECT_ROOT / "docs" / "_working" / "audit" / "adversarial_test_sys_master_20260507.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReport: {report_path.relative_to(PROJECT_ROOT)}")

    post_gate = run_gate()
    post_fails = [c for c in post_gate if c["status"] == "FAIL"]
    if post_fails:
        print("\n[POST-TEST INTEGRITY CHECK] WARNING: gate still has failures after restore:")
        for f in post_fails:
            print(f"  - {f['label']}: {f.get('detail', '')}")
        print("  This may indicate incomplete teardown from a crashed attack.")
    else:
        print("\n[POST-TEST INTEGRITY CHECK] All gate checks PASS after restore.")

    return 0 if missed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
