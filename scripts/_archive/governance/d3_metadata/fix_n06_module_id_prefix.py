# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/fix_n06_module_id_prefix.py | §
# [MODULE] scripts.governance.d3_metadata.fix_n06_module_id_prefix
# [INVARIANTS] scope prefix mapping is append-only; number assignment must be unique per scope
# [MODIFY-GUARD] SCOPE_PREFIX_RULES changes require Owner approval
# [CONSUMERS] check_naming_convention.py N-06; validate_module_id.py DIM-3
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=clean/no violations; exit 1=violations found (dry-run); exit 2=error
# [TESTS] tests/unit/test_fix_n06_module_id_prefix.py
"""fix_n06_module_id_prefix.py — 修复 N-06 module_id scope 前缀违规。

对标：check_naming_convention.py N-06（module_id 缺少 scope 前缀检测）

功能：
  1. 扫描项目中所有含 module_id 字段的文件
  2. 检测 module_id 是否匹配 ^(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW)-\\d+
  3. 对违规 module_id，根据文件类型/位置推导正确的 scope 前缀
  4. 分配该 scope 内唯一递增编号
  5. 原子写入更新文件

用法：
  python fix_n06_module_id_prefix.py              # dry-run（默认）
  python fix_n06_module_id_prefix.py --apply      # 实际修改
  python fix_n06_module_id_prefix.py --max-workers 8
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

VALID_SCOPE_PREFIX_RE = re.compile(r"^(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW)-[A-Z0-9-]*\d+$")

BLUEPRINT_HEADER_RE = re.compile(
    r"^(\s*#\s*\[BLUEPRINT\]\s+)(\S+)(\s*\|.*)",
    re.MULTILINE,
)

YAML_MODULE_ID_RE = re.compile(
    r"^(module_id:\s*)[\"']?(\S+?)[\"']?\s*$",
    re.MULTILINE,
)

DOC_TYPE_RE = re.compile(r"^doc_type:\s*(\S+)", re.MULTILINE)

EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".ruff_cache",
        ".mypy_cache",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        ".tox",
        ".eggs",
        ".idea",
        ".vscode",
        ".trae",
        ".ailocks",
        ".aidrafts",
        "_reorg_snapshots",
        "archive",
    }
)

SCAN_EXTENSIONS: frozenset[str] = frozenset({".py", ".md", ".yaml", ".yml", ".json"})

SCOPE_PREFIX_RULES: list[tuple[str, str]] = [
    ("ke-", "KE"),
    ("adr-", "ADR"),
    ("b_", "MOD"),
]


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    filepath: Path
    current_id: str
    suggested_id: str
    scope: str
    file_type: str


# ---------------------------------------------------------------------------
# scope 前缀推导
# ---------------------------------------------------------------------------


def determine_scope_prefix(filepath: Path, content: str) -> str:
    """根据文件路径和内容推导 module_id 的 scope 前缀。"""
    rel = str(filepath).replace("\\", "/").lower()
    name = filepath.name.lower()

    for prefix_pattern, scope in SCOPE_PREFIX_RULES:
        if name.startswith(prefix_pattern):
            return scope

    if "docs/01_policies_and_standards/" in rel:
        dt_match = DOC_TYPE_RE.search(content)
        doc_type = dt_match.group(1).lower() if dt_match else ""
        if "standard" in doc_type:
            return "STD"
        if "policy" in doc_type:
            return "PSP"
        if "register" in doc_type or "registry" in doc_type:
            return "GOV"
        if "operational" in doc_type or "runbook" in doc_type or "playbook" in doc_type:
            return "OPS"
        return "GOV"

    if "docs/03_modules/" in rel:
        return "MOD"

    if "src/zephyr/" in rel:
        return "SRC"

    if "tests/" in rel:
        return "SRC"

    if "data/" in rel and filepath.suffix in (".yaml", ".yml", ".json"):
        return "ARCH"

    return "GOV"


# ---------------------------------------------------------------------------
# module_id 提取
# ---------------------------------------------------------------------------


def extract_module_id_from_py(content: str) -> str | None:
    """从 Python 文件 [BLUEPRINT] 头部提取 module_id。"""
    m = BLUEPRINT_HEADER_RE.search(content)
    if m:
        return m.group(2).strip()
    return None


def extract_module_id_from_yaml_md(content: str) -> str | None:
    """从 YAML/MD 文件 frontmatter 提取 module_id。

    仅提取 --- 之间的 frontmatter 区域内的 module_id，
    避免匹配文件正文中嵌入的 module_id 数据条目。
    """
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    frontmatter = content[3:end]
    m = YAML_MODULE_ID_RE.search(frontmatter)
    if m:
        val = m.group(2).strip().strip("\"'")
        if val.lower() in ("null", "none", "~", ""):
            return None
        return val
    return None


def extract_module_id_from_json(content: str) -> str | None:
    """从 JSON 文件提取 module_id。"""
    import json

    try:
        data = json.loads(content)
        mid = data.get("module_id")
        if mid and isinstance(mid, str):
            return mid.strip()
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def extract_module_id(filepath: Path, content: str) -> str | None:
    """根据文件类型提取 module_id。"""
    if filepath.suffix == ".py":
        return extract_module_id_from_py(content)
    if filepath.suffix == ".json":
        return extract_module_id_from_json(content)
    return extract_module_id_from_yaml_md(content)


# ---------------------------------------------------------------------------
# 编号分配
# ---------------------------------------------------------------------------


def collect_existing_numbers(module_ids: dict[str, list[Path]]) -> dict[str, int]:
    """收集每个 scope 前缀下已有的最大编号。"""
    max_nums: dict[str, int] = {}
    for mid in module_ids:
        m = re.match(r"^([A-Z]+(?:-[A-Z]+)*)-(\d+)", mid)
        if m:
            prefix = m.group(1)
            num = int(m.group(2))
            if prefix not in max_nums or num > max_nums[prefix]:
                max_nums[prefix] = num
    return max_nums


def assign_next_number(scope: str, max_nums: dict[str, int], counter: dict[str, int]) -> str:
    """分配 scope 内下一个唯一编号。线程安全：counter 由主线程串行分配。"""
    base = max_nums.get(scope, 0)
    offset = counter.get(scope, 0) + 1
    counter[scope] = offset
    return f"{scope}-{base + offset:03d}"


# ---------------------------------------------------------------------------
# 文件扫描
# ---------------------------------------------------------------------------


def scan_files() -> list[Path]:
    """扫描项目中所有可能含 module_id 的文件。"""
    files: list[Path] = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = Path(root) / fn
            if p.suffix in SCAN_EXTENSIONS:
                files.append(p)
    return files


def read_file_safe(filepath: Path) -> str | None:
    """安全读取文件内容。"""
    try:
        return filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# ---------------------------------------------------------------------------
# 违规检测（线程安全，只读）
# ---------------------------------------------------------------------------


def detect_violation(filepath: Path) -> Violation | None:
    """检测单个文件的 N-06 违规。返回 Violation 或 None。"""
    content = read_file_safe(filepath)
    if content is None:
        return None

    mid = extract_module_id(filepath, content)
    if mid is None:
        return None

    if VALID_SCOPE_PREFIX_RE.match(mid):
        return None

    scope = determine_scope_prefix(filepath, content)
    rel = filepath.relative_to(REPO_ROOT)
    file_type = "py" if filepath.suffix == ".py" else filepath.suffix.lstrip(".")

    return Violation(
        filepath=filepath,
        current_id=mid,
        suggested_id="",
        scope=scope,
        file_type=file_type,
    )


# ---------------------------------------------------------------------------
# 原子写入
# ---------------------------------------------------------------------------


def atomic_write(filepath: Path, content: str) -> bool:
    """原子写入文件（RULE-ONE）。"""
    tmp_path = f"{filepath}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, filepath)
        return True
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False
    except OSError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False


# ---------------------------------------------------------------------------
# module_id 替换
# ---------------------------------------------------------------------------


def replace_module_id_py(content: str, old_id: str, new_id: str) -> str:
    """替换 Python 文件 [BLUEPRINT] 头部的 module_id。"""
    return BLUEPRINT_HEADER_RE.sub(
        lambda m: f"{m.group(1)}{new_id}{m.group(3)}",
        content,
        count=1,
    )


def replace_module_id_yaml_md(content: str, old_id: str, new_id: str) -> str:
    """替换 YAML/MD 文件 frontmatter 中的 module_id。

    仅在 --- 之间的 frontmatter 区域内替换，避免误改正文中的数据条目。
    """
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    if end == -1:
        return content
    frontmatter = content[3:end]
    body = content[end + 3 :]

    def _replacer(m: re.Match) -> str:
        prefix = m.group(1)
        had_quote = old_id in m.group(0) and ('"' in m.group(0) or "'" in m.group(0))
        if had_quote:
            return f'{prefix}"{new_id}"'
        return f"{prefix}{new_id}"

    new_frontmatter = YAML_MODULE_ID_RE.sub(_replacer, frontmatter, count=1)
    return f"---{new_frontmatter}---{body}"


def replace_module_id_json(content: str, old_id: str, new_id: str) -> str:
    """替换 JSON 文件中的 module_id。"""
    import json

    try:
        data = json.loads(content)
        if data.get("module_id") == old_id:
            data["module_id"] = new_id
            return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    except (json.JSONDecodeError, TypeError):
        pass
    return content


def replace_module_id(filepath: Path, content: str, old_id: str, new_id: str) -> str:
    """根据文件类型替换 module_id。"""
    if filepath.suffix == ".py":
        return replace_module_id_py(content, old_id, new_id)
    if filepath.suffix == ".json":
        return replace_module_id_json(content, old_id, new_id)
    return replace_module_id_yaml_md(content, old_id, new_id)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="修复 N-06 module_id scope 前缀违规")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际修改文件（默认 dry-run 仅显示变更计划）",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="ThreadPoolExecutor 并行度（默认 8）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="有违规时仍 exit 0",
    )
    args = parser.parse_args()

    dry_run = not args.apply
    mode_label = "DRY-RUN" if dry_run else "APPLY"
    print(f"[N-06-FIX] mode={mode_label} max_workers={args.max_workers}")

    # STEP 1: 扫描文件
    all_files = scan_files()
    print(f"[N-06-FIX] scanned {len(all_files)} files")

    # STEP 2: 并行检测违规
    violations: list[Violation] = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(detect_violation, f): f for f in all_files}
        for fut in as_completed(futures):
            try:
                result = fut.result()
                if result is not None:
                    violations.append(result)
            except Exception as exc:
                fp = futures[fut]
                print(f"[N-06-FIX] ERROR scanning {fp}: {exc}", file=sys.stderr)

    if not violations:
        print("[N-06-FIX] ALL PASS — no N-06 violations found")
        return EXIT_PASS

    print(f"[N-06-FIX] found {len(violations)} N-06 violations")

    # STEP 3: 收集全局已有 module_id 以分配唯一编号
    all_module_ids: dict[str, list[Path]] = defaultdict(list)
    for f in all_files:
        content = read_file_safe(f)
        if content is None:
            continue
        mid = extract_module_id(f, content)
        if mid:
            all_module_ids[mid].append(f)

    max_nums = collect_existing_numbers(all_module_ids)
    number_counter: dict[str, int] = {}

    # STEP 4: 为每个违规分配新 module_id
    for v in sorted(violations, key=lambda x: str(x.filepath)):
        v.suggested_id = assign_next_number(v.scope, max_nums, number_counter)

    # STEP 5: 输出变更计划 / 执行变更
    by_scope: dict[str, list[Violation]] = defaultdict(list)
    for v in violations:
        by_scope[v.scope].append(v)

    print(f"\n{'=' * 70}")
    print(f"N-06 FIX PLAN ({mode_label})")
    print(f"{'=' * 70}")
    print(f"Total violations: {len(violations)}\n")

    for scope, items in sorted(by_scope.items()):
        print(f"  Scope [{scope}] — {len(items)} violation(s):")
        for v in items:
            rel = v.filepath.relative_to(REPO_ROOT)
            print(f"    {rel}")
            print(f"      {v.current_id} → {v.suggested_id}")
        print()

    if dry_run:
        print(f"[N-06-FIX] DRY-RUN complete — {len(violations)} violations would be fixed")
        print("[N-06-FIX] Use --apply to make actual changes")
        return EXIT_FINDINGS if not args.warn_only else EXIT_PASS

    # STEP 6: 实际修改（串行写入，避免并发写入冲突）
    success_count = 0
    fail_count = 0
    for v in sorted(violations, key=lambda x: str(x.filepath)):
        content = read_file_safe(v.filepath)
        if content is None:
            print(f"[N-06-FIX] SKIP (read error): {v.filepath}", file=sys.stderr)
            fail_count += 1
            continue

        new_content = replace_module_id(v.filepath, content, v.current_id, v.suggested_id)
        if new_content == content:
            print(f"[N-06-FIX] SKIP (no replacement made): {v.filepath}", file=sys.stderr)
            fail_count += 1
            continue

        ok = atomic_write(v.filepath, new_content)
        if ok:
            rel = v.filepath.relative_to(REPO_ROOT)
            print(f"[N-06-FIX] FIXED: {rel}  {v.current_id} → {v.suggested_id}")
            success_count += 1
        else:
            print(f"[N-06-FIX] FAIL (write error): {v.filepath}", file=sys.stderr)
            fail_count += 1

    # STEP 7: 汇总
    print(f"\n{'=' * 70}")
    print("N-06 FIX SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total violations:  {len(violations)}")
    print(f"Successfully fixed: {success_count}")
    print(f"Failed:            {fail_count}")
    print(f"Skipped (no-op):   {len(violations) - success_count - fail_count}")

    if fail_count > 0:
        return EXIT_FINDINGS
    return EXIT_PASS if not args.warn_only or success_count == 0 else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
