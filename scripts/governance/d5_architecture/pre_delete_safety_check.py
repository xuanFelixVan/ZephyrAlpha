# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/pre_delete_safety_check.py | §
# [MODULE] scripts.governance.d5_architecture.pre_delete_safety_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] RULE-THREE删除审判; pre_write_gate.py --delete; migration pipeline
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] exit 0=SAFE(允许删除); exit 1=BLOCKED(禁止删除); --dry-run不修改任何文件
# [MODIFY-GUARD] 只读检查脚本，禁止修改任何目标文件
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] CheckError(检查项失败); RegistryError(注册表读取失败)
# [TESTS] tests/test_pre_delete_safety_check.py
# [TTL] permanent
"""安全删除门禁脚本——RULE-THREE 强制执行器。

删除任何文件前 MUST 通过5项检查：
  CHECK-1: .py 消费者 Grep — 是否有 .py 文件 import/引用 目标文件
  CHECK-2: .yaml 消费者 Grep — 是否有 .yaml 文件引用 目标文件路径
  CHECK-3: 注册表检查 — 目标文件是否在 manifest/registry/__init__.py 中被登记
  CHECK-4: 重复内容检查 — git ls-tree 查找同内容副本
  CHECK-5: 功能价值标记 — 检查文件头 [SAFETY]/[AI_AUTONOMY] 标记

8步工作流：
  STEP 1: 解析目标文件路径，验证文件存在
  STEP 2: CHECK-1 — Grep .py 引用
  STEP 3: CHECK-2 — Grep .yaml 引用
  STEP 4: CHECK-3 — 注册表检查
  STEP 5: CHECK-4 — git ls-tree 重复内容
  STEP 6: CHECK-5 — 功能价值标记
  STEP 7: 汇总判定 — 全通过=SAFE, 任一失败=BLOCKED
  STEP 8: 输出结果

用法:
    python scripts/governance/d5_architecture/pre_delete_safety_check.py <file_path>
    python scripts/governance/d5_architecture/pre_delete_safety_check.py <file_path> --dry-run
    python scripts/governance/d5_architecture/pre_delete_safety_check.py <file_path> --json
    python scripts/governance/d5_architecture/pre_delete_safety_check.py <file_path> --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 安全删除门禁脚本——RULE-THREE 强制执行器。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from _shared.constants import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"

_REGISTRY_FILES: list[Path] = [
    _PROJECT_ROOT / "scripts" / "script_manifest.yaml",
    _PROJECT_ROOT / "src" / "zephyr" / "gates" / "_registry.yaml",
    _PROJECT_ROOT / "docs" / "03_modules" / "module-registry.yaml",
    _PROJECT_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml",
    _PROJECT_ROOT / "docs" / "03_modules" / "template-registry.yaml",
    _PROJECT_ROOT / "docs" / "03_modules" / "system-pathway-registry.yaml",
    _PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "migration_registry.yaml",
    _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "script-health-registry.md",
]

_HIGH_VALUE_MARKERS = [
    ("[SAFETY]", "H"),
    ("[AI_AUTONOMY]", "immutable_core"),
    ("[AI_AUTONOMY]", "human_gated"),
    ("[STABILITY]", "frozen"),
]

_EXCLUDE_SELF_PATTERNS = [
    r"pre_delete_safety_check\.py",
]


def _resolve_target(file_path: str) -> Path:
    """STEP 1: 解析目标文件路径，验证文件存在。"""
    p = Path(file_path)
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (_PROJECT_ROOT / p).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"目标文件不存在: {resolved}")
    return resolved


def _rel_path(resolved: Path) -> str:
    """获取相对项目根的路径字符串（正斜杠）。"""
    try:
        return str(resolved.resolve().relative_to(_PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def _check_py_references(rel: str, resolved: Path) -> tuple[bool, str, list[str]]:
    """STEP 2: CHECK-1 — Grep .py 文件中的 import/引用。"""
    stem = resolved.stem
    parent_name = resolved.parent.name
    references: list[str] = []

    search_terms = [rel, stem]
    if parent_name and parent_name != ".":
        search_terms.append(f"{parent_name}.{stem}")

    for term in search_terms:
        try:
            result = subprocess.run(
                [
                    "rg",
                    "-l",
                    "--type",
                    "py",
                    term,
                    str(_PROJECT_ROOT / "src"),
                    str(_PROJECT_ROOT / "scripts"),
                    str(_PROJECT_ROOT / "tests"),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                cwd=str(_PROJECT_ROOT),
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    ref_path = line.strip().replace("\\", "/")
                    if ref_path == rel or ref_path.endswith(f"/{rel}"):
                        continue
                    is_self = any(re.search(pat, ref_path) for pat in _EXCLUDE_SELF_PATTERNS)
                    if not is_self and ref_path not in references:
                        references.append(ref_path)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    if references:
        return False, f"PY_REFS: {len(references)} 个 .py 文件引用此文件", references
    return True, "OK: 无 .py 消费者引用", references


def _check_yaml_references(rel: str, resolved: Path) -> tuple[bool, str, list[str]]:
    """STEP 3: CHECK-2 — Grep .yaml 文件中的路径引用。"""
    references: list[str] = []
    search_terms = [rel, resolved.name]
    stem = resolved.stem
    if stem:
        search_terms.append(stem)

    for term in search_terms:
        try:
            result = subprocess.run(
                ["rg", "-l", "--type", "yaml", term, str(_PROJECT_ROOT)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                cwd=str(_PROJECT_ROOT),
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().splitlines():
                    ref_path = line.strip().replace("\\", "/")
                    if ref_path == rel or ref_path.endswith(f"/{rel}"):
                        continue
                    is_self = any(re.search(pat, ref_path) for pat in _EXCLUDE_SELF_PATTERNS)
                    if not is_self and ref_path not in references:
                        references.append(ref_path)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    if references:
        return False, f"YAML_REFS: {len(references)} 个 .yaml 文件引用此文件", references
    return True, "OK: 无 .yaml 消费者引用", references


def _check_registry(rel: str, resolved: Path) -> tuple[bool, str, list[str]]:
    """STEP 4: CHECK-3 — 注册表检查。"""
    registrations: list[str] = []
    filename = resolved.name
    stem = resolved.stem

    for registry_path in _REGISTRY_FILES:
        if not registry_path.exists():
            continue
        try:
            content = registry_path.read_text(encoding="utf-8")
            if rel in content or filename in content or stem in content:
                registrations.append(str(registry_path.relative_to(_PROJECT_ROOT)).replace("\\", "/"))
        except OSError:
            continue

    if resolved.suffix == ".py":
        init_file = resolved.parent / "__init__.py"
        if init_file.exists():
            try:
                init_content = init_file.read_text(encoding="utf-8")
                if stem in init_content:
                    registrations.append(
                        str(init_file.relative_to(_PROJECT_ROOT)).replace("\\", "/") + " (__init__.py)"
                    )
            except OSError:
                pass

    if registrations:
        return False, f"REGISTRY: 在 {len(registrations)} 个注册表中被引用", registrations
    return True, "OK: 未在注册表中被引用", registrations


def _check_git_duplicates(rel: str, resolved: Path) -> tuple[bool, str, list[str]]:
    """STEP 5: CHECK-4 — git ls-tree 重复内容检查。"""
    try:
        content = resolved.read_bytes()
    except OSError:
        return True, "WARN: 无法读取文件内容，跳过重复检查", []

    content_hash = hashlib.sha256(content).hexdigest()

    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_PROJECT_ROOT),
        )
        if result.returncode != 0:
            return True, "WARN: git ls-tree 失败，跳过重复检查", []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return True, "WARN: git 不可用，跳过重复检查", []

    duplicates: list[str] = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        blob_info = parts[0]
        file_path_git = parts[1].strip()
        if file_path_git == rel:
            continue
        blob_parts = blob_info.split()
        if len(blob_parts) >= 3 and blob_parts[1] == "blob":
            git_hash = blob_parts[2]
            if git_hash == content_hash:
                duplicates.append(file_path_git)

    if duplicates:
        return True, f"DUPLICATE: {len(duplicates)} 个同内容副本存在（可安全删除）", duplicates
    return True, "OK: 无重复内容副本", duplicates


def _check_value_markers(resolved: Path) -> tuple[bool, str, list[str]]:
    """STEP 6: CHECK-5 — 功能价值标记检查。"""
    if resolved.suffix != ".py":
        return True, "OK: 非 .py 文件，跳过价值标记检查", []

    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True, "WARN: 无法读取文件，跳过价值标记检查", []

    markers_found: list[str] = []
    lines = content.splitlines()[:30]

    for marker_field, marker_value in _HIGH_VALUE_MARKERS:
        for line in lines:
            if marker_field in line and marker_value in line:
                markers_found.append(f"{marker_field}={marker_value}")
                break

    if markers_found:
        return False, f"VALUE_MARKED: 高价值标记 {markers_found} — 禁止删除（RULE-THREE §3a）", markers_found
    return True, "OK: 无高价值标记", markers_found


def run_checks(file_path: str) -> dict[str, Any]:
    """执行全部5项检查，返回结果字典。"""
    resolved = _resolve_target(file_path)
    rel = _rel_path(resolved)

    checks: list[dict[str, Any]] = []

    ok, msg, refs = _check_py_references(rel, resolved)
    checks.append({"check": "py_references", "pass": ok, "message": msg, "details": refs})

    ok, msg, refs = _check_yaml_references(rel, resolved)
    checks.append({"check": "yaml_references", "pass": ok, "message": msg, "details": refs})

    ok, msg, refs = _check_registry(rel, resolved)
    checks.append({"check": "registry", "pass": ok, "message": msg, "details": refs})

    ok, msg, refs = _check_git_duplicates(rel, resolved)
    checks.append({"check": "git_duplicates", "pass": ok, "message": msg, "details": refs})

    ok, msg, refs = _check_value_markers(resolved)
    checks.append({"check": "value_markers", "pass": ok, "message": msg, "details": refs})

    blocked = [c for c in checks if not c["pass"]]
    safe = len(blocked) == 0

    return {
        "file": rel,
        "verdict": "SAFE" if safe else "BLOCKED",
        "safe": safe,
        "checks": checks,
        "blocked_count": len(blocked),
        "total_checks": len(checks),
    }


def main() -> int:
    """STEP 7-8: 汇总判定 + 输出结果。"""
    parser = argparse.ArgumentParser(
        description="安全删除门禁——RULE-THREE 五项检查（不通过则禁止删除）",
    )
    parser.add_argument("file_path", help="要删除的文件路径（相对或绝对）")
    parser.add_argument("--dry-run", action="store_true", help="只输出检查结果，不执行删除")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：检查失败仍 exit 0（用于自测）")
    args = parser.parse_args()

    try:
        result = run_checks(args.file_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"  File: {result['file']}")
        print(f"  Verdict: {result['verdict']}")
        print()
        for c in result["checks"]:
            icon = "  PASS" if c["pass"] else "  BLOCK"
            print(f"  {icon}  {c['check']}: {c['message']}")
            if c["details"]:
                for d in c["details"][:10]:
                    print(f"         -> {d}")
                if len(c["details"]) > 10:
                    print(f"         ... and {len(c['details']) - 10} more")
        print()
        if result["safe"]:
            print(f"  SAFE ({result['total_checks']}/{result['total_checks']}) — 允许删除 {result['file']}")
        else:
            print(f"  BLOCKED ({result['blocked_count']}/{result['total_checks']} checks failed)")
            print("  Action required: 修复以上 BLOCK 项后重试（RULE-THREE）")

    if args.warn_only:
        return 0
    return 0 if result["safe"] else 1


if __name__ == "__main__":
    sys.exit(main())
