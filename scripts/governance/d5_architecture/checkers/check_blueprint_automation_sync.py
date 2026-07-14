# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_blueprint_automation_sync.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_automation_sync
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
r"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_automation_sync
[INVARIANTS] 蓝图§5.5自动化触发机制状态列必须与代码实际实现一致; ⚠️待实现但代码已实现=DRIFT; ✅已实现但代码不存在=DRIFT
[MODIFY-GUARD] script_manifest.yaml; blueprint-construction-template.md §0.2
[CONSUMERS] CI pipeline; AI session 冷启动; Phase Gate; audit_registration.py
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=CLEAN, exit 1=DRIFT, exit 2=ERROR
[TESTS] tests/governance/test_check_blueprint_automation_sync.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import re

from _shared.constants import BLUEPRINTS_DIR, EXIT_FINDINGS, REPO_ROOT
from _shared.walk import iter_files

__manifest__ = """
args: [--warn-only, --json, --blueprint]
description: 蓝图§5.5自动化触发机制状态列↔代码实际实现同步校验
dimensions:
- D5
- D8
priority: P1
timeout_seconds: 60
warn_only: false
"""

SRC_DIR = REPO_ROOT / "src" / "zephyr"

AUTOMATION_TABLE_RE = re.compile(
    r"\|\s*([^|]+)\s*\|\s*(auto_boot|auto_scheduled|auto_event|on_demand)\s*\|\s*([^|]+)\s*\|\s*(✅已实现|⚠️待实现|⚠️部分实现|⚠️未实现|❌未实现)\s*\|"
)

MODULE_ID_RE = re.compile(r'module_id:\s*["\']?(\S+?)["\']?\s*$')
DISK_PATH_RE = re.compile(r'actual_disk_path:\s*["\']?([^"\']+)["\']?\s*$')

CODE_IMPLEMENTATION_PROBES: dict[str, dict] = {
    "MOD-INF-011": {
        "package": "vector-memory",
        "probes": {
            "VMS启动": {
                "file": "runtime/auto_runtime_core.py",
                "pattern": r"_vms\s*=\s*InProcessVectorMemory|VMS\.start\(\)",
            },
            "TTL过期清理": {
                "file": "vector-memory/in_process_vector_memory.py",
                "pattern": r"_maintenance_loop.*purge_expired|purge_expired",
            },
            "定时健康检查": {
                "file": "vector-memory/in_process_vector_memory.py",
                "pattern": r"_maintenance_loop.*check_all|check_all",
            },
            "自动修复": {
                "file": "vector-memory/in_process_vector_memory.py",
                "pattern": r"_maintenance_loop.*auto_repair|auto_repair",
            },
            "检索缓存": {"file": "vector-memory/in_process_vector_memory.py", "pattern": r"_cache_layer|CacheLayer"},
            "检索反馈收集": {
                "file": "vector-memory/in_process_vector_memory.py",
                "pattern": r"_retrieval_feedback|RetrievalFeedback",
            },
            "语义检索": {"file": "vector-memory/hybrid_retriever.py", "pattern": r"class HybridRetriever"},
            "写入": {"file": "vector-memory/in_process_vector_memory.py", "pattern": r"def write\("},
            "8 Collection初始化": {"file": "vector-memory/collection_manager.py", "pattern": r"init_all_collections"},
            "嵌入模型warmup": {"file": "vector-memory/embedding_router.py", "pattern": "def warmup"},
            "启动时健康检查": {"file": "vector-memory/in_process_vector_memory.py", "pattern": r"check_all"},
            "启动时漂移检测": {"file": "vector-memory/index_health_monitor.py", "pattern": r"detect_drift"},
            "模型版本变更清缓存": {
                "file": "vector-memory/cache_layer.py",
                "pattern": r"invalidate_all_on_model_change",
            },
            "完整性校验": {"file": "vector-memory/index_health_monitor.py", "pattern": r"integrity_check"},
            "定时漂移检测": {"file": "vector-memory/index_health_monitor.py", "pattern": r"detect_drift"},
        },
    },
}


def find_blueprint_files() -> list[Path]:
    return iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md")


def parse_frontmatter(content: str) -> dict[str, str]:
    fm: dict[str, str] = {}
    if not content.startswith("---"):
        return fm
    end = content.find("---", 3)
    if end < 0:
        return fm
    fm_text = content[3:end]
    for line in fm_text.splitlines():
        m = MODULE_ID_RE.match(line.strip())
        if m:
            fm["module_id"] = m.group(1).strip('"').strip("'")
        m2 = DISK_PATH_RE.match(line.strip())
        if m2:
            fm["actual_disk_path"] = m2.group(1).strip().strip('"').strip("'").rstrip("/")
    return fm


def extract_automation_table(content: str) -> list[dict]:
    rows: list[dict] = []
    for match in AUTOMATION_TABLE_RE.finditer(content):
        operation = match.group(1).strip()
        trigger = match.group(2).strip()
        strategy = match.group(3).strip()
        status = match.group(4).strip()
        rows.append(
            {
                "operation": operation,
                "trigger": trigger,
                "strategy": strategy,
                "status": status,
            }
        )
    return rows


def probe_code_implementation(module_id: str, operation: str) -> bool | None:
    config = CODE_IMPLEMENTATION_PROBES.get(module_id)
    if not config:
        return None
    probe = config["probes"].get(operation)
    if not probe:
        for key, p in config["probes"].items():
            if key in operation or operation in key:
                probe = p
                break
    if not probe:
        return None
    file_path = SRC_DIR / probe["file"]
    if not file_path.exists():
        return False
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(re.search(probe["pattern"], content))


def check_automation_sync(blueprint_path: Path | None = None) -> list[dict]:
    findings: list[dict] = []
    bp_files = [blueprint_path] if blueprint_path else find_blueprint_files()

    for bp_file in bp_files:
        if not bp_file.exists():
            continue
        try:
            content = bp_file.read_text(encoding="utf-8")
        except OSError:
            continue

        fm = parse_frontmatter(content)
        module_id = fm.get("module_id", "")
        if not module_id:
            continue

        if "§5.5" not in content:
            continue

        rows = extract_automation_table(content)
        if not rows:
            continue

        for row in rows:
            operation = row["operation"]
            bp_status = row["status"]

            code_impl = probe_code_implementation(module_id, operation)
            if code_impl is None:
                continue

            if bp_status in ("⚠️待实现", "⚠️未实现") and code_impl is True:
                findings.append(
                    {
                        "type": "AUTOMATION_DRIFT_IMPLEMENTED",
                        "severity": "HIGH",
                        "blueprint": str(bp_file.relative_to(REPO_ROOT)),
                        "module_id": module_id,
                        "detail": f"§5.5 '{operation}' 标注'{bp_status}'但代码已实现",
                        "fix": f"更新蓝图§5.5 '{operation}' 状态为 ✅已实现",
                    }
                )

            elif bp_status == "✅已实现" and code_impl is False:
                findings.append(
                    {
                        "type": "AUTOMATION_DRIFT_MISSING",
                        "severity": "HIGH",
                        "blueprint": str(bp_file.relative_to(REPO_ROOT)),
                        "module_id": module_id,
                        "detail": f"§5.5 '{operation}' 标注'✅已实现'但代码中未找到实现",
                        "fix": f"实现代码或更新蓝图§5.5 '{operation}' 状态为 ⚠️待实现",
                    }
                )

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="蓝图§5.5自动化触发机制↔代码实现同步校验")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--blueprint", type=str, help="指定蓝图路径")
    args = parser.parse_args()

    bp_path = Path(args.blueprint).resolve() if args.blueprint else None
    findings = check_automation_sync(bp_path)

    high_count = sum(1 for f in findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "total_findings": len(findings),
                    "high": high_count,
                    "medium": medium_count,
                    "findings": findings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("=" * 60)
        print("蓝图§5.5自动化触发机制↔代码实现同步校验")
        print("=" * 60)
        print()

        if not findings:
            print("✅ 全部对齐，§5.5状态列与代码实现一致！")
        else:
            by_type: dict[str, list[dict]] = {}
            for f in findings:
                by_type.setdefault(f["type"], []).append(f)

            for ftype, items in by_type.items():
                print(f"{'─' * 60}")
                print(f"  {ftype} ({len(items)} 条)")
                print(f"{'─' * 60}")
                for item in items:
                    icon = "❌" if item["severity"] == "HIGH" else "⚠️"
                    print(f"  {icon} [{item['module_id']}] {item['detail']}")
                    print(f"     修复: {item['fix']}")

        print()
        print(f"{'=' * 60}")
        print(f"  总结: {len(findings)} 条漂移 (HIGH:{high_count} MEDIUM:{medium_count})")
        print(f"{'=' * 60}")

    has_high = high_count > 0
    if has_high and not args.warn_only:
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
