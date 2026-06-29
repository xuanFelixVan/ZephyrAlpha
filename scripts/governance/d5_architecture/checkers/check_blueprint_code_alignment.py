# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
# [DOMAIN] D_GOVERNANCE
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
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
[INVARIANTS] 代码[BLUEPRINT]头部module_id必须与蓝图注册表一致; 蓝图§4已实现文件必须在磁盘存在
[MODIFY-GUARD] script_manifest.yaml; blueprint_registry.yaml
[CONSUMERS] CI pipeline; AI session 冷启动; Phase Gate
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=CLEAN, exit 1=DRIFT, exit 2=ERROR
[TESTS] tests/governance/test_check_blueprint_code_alignment.py
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
from concurrent.futures import ThreadPoolExecutor, as_completed

from _shared.constants import EXIT_FINDINGS, REPO_ROOT

__manifest__ = """
args: [--warn-only, --json, --package]
description: 蓝图↔代码双向对齐检测——代码[BLUEPRINT]头部module_id与蓝图注册表一致性+蓝图§4文件落地验证
dimensions:
- D5
- D1
priority: P1
timeout_seconds: 60
warn_only: false
"""

BLUEPRINTS_DIR = REPO_ROOT / "docs" / "03_modules"
SRC_DIR = REPO_ROOT / "src" / "zephyr"
BLUEPRINT_REGISTRY = BLUEPRINTS_DIR / "blueprint_registry.yaml"
MODULE_REGISTRY = BLUEPRINTS_DIR / "module-registry.yaml"

BLUEPRINT_HEADER_RE = re.compile(r"\[BLUEPRINT\]\s+(\S+)")
MODULE_ID_RE = re.compile(r'(?:-\s*)?module_id:\s*["\']?(\S+?)["\']?\s*$')


def load_blueprint_registry() -> dict[str, dict]:
    registry: dict[str, dict] = {}
    if not BLUEPRINT_REGISTRY.exists():
        return registry
    content = BLUEPRINT_REGISTRY.read_text(encoding="utf-8")
    current_id = None
    current_entry: dict = {}
    for line in content.splitlines():
        m = MODULE_ID_RE.match(line.strip())
        if m:
            if current_id:
                registry[current_id] = current_entry
            current_id = m.group(1).strip('"').strip("'")
            current_entry = {}
            continue
        if current_id and ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            current_entry[key.strip()] = val.strip()
    if current_id:
        registry[current_id] = current_entry
    return registry


def load_module_registry() -> dict[str, str]:
    pkg_to_modid: dict[str, str] = {}
    if not MODULE_REGISTRY.exists():
        return pkg_to_modid
    content = MODULE_REGISTRY.read_text(encoding="utf-8")
    current_id = None
    for line in content.splitlines():
        m = MODULE_ID_RE.match(line.strip())
        if m:
            current_id = m.group(1).strip('"').strip("'")
            continue
        if current_id and "actual_disk_path:" in line:
            _, _, val = line.partition(":")
            path_val = val.strip().strip('"').strip("'").rstrip("/")
            pkg_name = path_val.split("/")[-1] if "/" in path_val else path_val
            if pkg_name and current_id:
                pkg_to_modid[pkg_name] = current_id
    return pkg_to_modid


def scan_code_blueprint_headers(package_filter: str | None = None) -> list[dict]:
    findings: list[dict] = []
    packages = sorted(p for p in SRC_DIR.iterdir() if p.is_dir() and not p.name.startswith("_"))
    if package_filter:
        packages = [p for p in packages if p.name == package_filter]

    def scan_file(py_file: Path, pkg_name: str) -> dict | None:
        try:
            content = py_file.read_text(encoding="utf-8")
        except OSError:
            return None
        m = BLUEPRINT_HEADER_RE.search(content)
        if not m:
            return None
        header_modid = m.group(1)
        return {"file": str(py_file.relative_to(REPO_ROOT)), "package": pkg_name, "header_modid": header_modid}

    for pkg in packages:
        py_files = list(pkg.rglob("*.py"))
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(scan_file, f, pkg.name): f for f in py_files}
            for fut in as_completed(futures):
                result = fut.result()
                if result:
                    findings.append(result)

    return findings


def check_header_vs_registry(
    code_headers: list[dict],
    blueprint_registry: dict[str, dict],
    pkg_to_modid: dict[str, str],
) -> list[dict]:
    drifts: list[dict] = []
    for entry in code_headers:
        header_modid = entry["header_modid"]
        pkg_name = entry["package"]
        expected_modid = pkg_to_modid.get(pkg_name)

        if header_modid not in blueprint_registry:
            drifts.append(
                {
                    "type": "ORPHAN_MODULE_ID",
                    "severity": "HIGH",
                    "file": entry["file"],
                    "detail": f"[BLUEPRINT] 引用 {header_modid} 不在 blueprint_registry.yaml 中",
                }
            )

        if expected_modid and header_modid != expected_modid:
            drifts.append(
                {
                    "type": "MODULE_ID_DRIFT",
                    "severity": "HIGH",
                    "file": entry["file"],
                    "detail": f"包 {pkg_name} 应属 {expected_modid}，但 [BLUEPRINT] 标注 {header_modid}",
                }
            )

    return drifts


def check_blueprint_file_list(
    blueprint_registry: dict[str, dict],
) -> list[dict]:
    drifts: list[dict] = []
    for bp_file in BLUEPRINTS_DIR.rglob("blueprint.md"):
        try:
            content = bp_file.read_text(encoding="utf-8")
        except OSError:
            continue

        fm_modid = None
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                fm_text = content[3:end]
                for line in fm_text.splitlines():
                    m = MODULE_ID_RE.match(line.strip())
                    if m:
                        fm_modid = m.group(1).strip('"').strip("'")
                        break

        actual_disk_path = None
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                fm_text = content[3:end]
                for line in fm_text.splitlines():
                    if "actual_disk_path:" in line:
                        _, _, val = line.partition(":")
                        actual_disk_path = val.strip().strip('"').strip("'").rstrip("/")
                        break

        if not actual_disk_path:
            continue

        src_base = REPO_ROOT / actual_disk_path
        if not src_base.exists():
            continue

        file_table_re = re.compile(r"\|\s*`([^`]+\.py)`\s*\|[^|]*\|[^|]*\|[^|]*\|\s*已实现\s*\|")
        for match in file_table_re.finditer(content):
            filename = match.group(1)
            full_path = src_base / filename
            if not full_path.exists():
                drifts.append(
                    {
                        "type": "BLUEPRINT_FILE_MISSING",
                        "severity": "MEDIUM",
                        "file": str(full_path.relative_to(REPO_ROOT)),
                        "detail": f"蓝图 {fm_modid} §4 声明已实现，但磁盘不存在: {filename}",
                    }
                )

    return drifts


def check_code_not_in_blueprint(
    code_headers: list[dict],
    blueprint_registry: dict[str, dict],
) -> list[dict]:
    drifts: list[dict] = []
    pkg_files: dict[str, list[str]] = {}
    for entry in code_headers:
        pkg_files.setdefault(entry["package"], []).append(entry["file"])

    for bp_file in BLUEPRINTS_DIR.rglob("blueprint.md"):
        try:
            content = bp_file.read_text(encoding="utf-8")
        except OSError:
            continue

        actual_disk_path = None
        fm_modid = None
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                fm_text = content[3:end]
                for line in fm_text.splitlines():
                    if "actual_disk_path:" in line:
                        _, _, val = line.partition(":")
                        actual_disk_path = val.strip().strip('"').strip("'").rstrip("/")
                    m = MODULE_ID_RE.match(line.strip())
                    if m:
                        fm_modid = m.group(1).strip('"').strip("'")

        if not actual_disk_path:
            continue

        pkg_name = actual_disk_path.split("/")[-1] if "/" in actual_disk_path else actual_disk_path
        src_base = REPO_ROOT / actual_disk_path
        if not src_base.exists():
            continue

        listed_files: set[str] = set()
        file_table_re = re.compile(r"\|\s*`([^`]+\.py)`\s*\|")
        for match in file_table_re.finditer(content):
            listed_files.add(match.group(1))

        for py_file in src_base.glob("*.py"):
            if py_file.name == "__pycache__":
                continue
            if py_file.name not in listed_files and py_file.name != "__init__.py":
                has_header = False
                try:
                    fc = py_file.read_text(encoding="utf-8")
                    has_header = bool(BLUEPRINT_HEADER_RE.search(fc))
                except OSError:
                    pass
                if has_header:
                    drifts.append(
                        {
                            "type": "CODE_NOT_IN_BLUEPRINT",
                            "severity": "LOW",
                            "file": str(py_file.relative_to(REPO_ROOT)),
                            "detail": f"代码文件有[BLUEPRINT]头部但不在蓝图 {fm_modid} §4 文件清单中",
                        }
                    )

    return drifts


def main() -> None:
    parser = argparse.ArgumentParser(description="蓝图↔代码双向对齐检测")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--package", type=str, help="限定扫描单个包")
    args = parser.parse_args()

    blueprint_registry = load_blueprint_registry()
    pkg_to_modid = load_module_registry()

    code_headers = scan_code_blueprint_headers(package_filter=args.package)

    drift_findings = check_header_vs_registry(code_headers, blueprint_registry, pkg_to_modid)
    file_missing_findings = check_blueprint_file_list(blueprint_registry)
    code_not_in_bp_findings = check_code_not_in_blueprint(code_headers, blueprint_registry)

    all_findings = drift_findings + file_missing_findings + code_not_in_bp_findings

    high_count = sum(1 for f in all_findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in all_findings if f["severity"] == "MEDIUM")
    low_count = sum(1 for f in all_findings if f["severity"] == "LOW")

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "total_findings": len(all_findings),
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count,
                    "findings": all_findings,
                    "code_headers_scanned": len(code_headers),
                    "blueprints_in_registry": len(blueprint_registry),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("=" * 60)
        print("蓝图↔代码双向对齐检测")
        print("=" * 60)
        print(f"扫描: {len(code_headers)} 个代码文件有[BLUEPRINT]头部")
        print(f"蓝图注册表: {len(blueprint_registry)} 个 module_id")
        print()

        if not all_findings:
            print("✅ 全部对齐，无漂移！")
        else:
            by_type: dict[str, list[dict]] = {}
            for f in all_findings:
                by_type.setdefault(f["type"], []).append(f)

            for ftype, items in by_type.items():
                print(f"{'─' * 60}")
                print(f"  {ftype} ({len(items)} 条)")
                print(f"{'─' * 60}")
                for item in items[:20]:
                    icon = "❌" if item["severity"] == "HIGH" else ("⚠️" if item["severity"] == "MEDIUM" else "ℹ️")
                    print(f"  {icon} {item['file']}")
                    print(f"     {item['detail']}")
                if len(items) > 20:
                    print(f"  ... 还有 {len(items) - 20} 条")

        print()
        print(f"{'=' * 60}")
        print(f"  总结: {len(all_findings)} 条漂移 (HIGH:{high_count} MEDIUM:{medium_count} LOW:{low_count})")
        print(f"{'=' * 60}")

    has_high = high_count > 0
    if has_high and not args.warn_only:
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
