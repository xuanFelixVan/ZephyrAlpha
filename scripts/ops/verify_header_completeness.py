# [BLUEPRINT] MOD-INF-005 | scripts/ops/verify_header_completeness.py | §
# [MODULE] scripts.ops.verify_header_completeness
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.frontmatter; zephyr.shared.io.paths
# [CONSUMERS] trae_047 verification flow; manual audit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 按扩展名路由到 SSoT 解析器（.py/.sh/.ps1/.mmd→parse_py_header, .yaml→parse_byaml_anchor, .json→parse_json_meta）；按格式区分 REQUIRED_FIELDS；无头部的文件跳过（不强制要求头部，仅校验有头部文件的字段完整性）
# [MODIFY-GUARD] trae_047_engineering_file_header.yaml; scripts/governance/_shared/frontmatter.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=全部完整或无文件; exit 1=有缺失
# [TESTS] 手动验证：全量扫描 + 格式路由
# [TTL] permanent
"""文件头部完整性校验（6 格式统一入口）

对标 trae_047 GOV-ENG-002：按扩展名路由到 SSoT 解析器，校验每种格式的必填字段。

格式路由（真源：scripts/governance/_shared/frontmatter.py）：
  .py（src/scripts）  → parse_py_header → A_full 15字段（12必填）
  .py（tests）        → parse_py_header → A_test 7字段（5必填）
  .sh/.ps1/.mmd       → parse_py_header → E_shell 5字段（5必填）
  .yaml               → parse_byaml_anchor → B_yaml 6字段（6必填）
  .json               → parse_json_meta → C_json 6字段（6必填）

无头部的文件（解析器返回 None）跳过——仅校验有头部文件的字段完整性。
"""
import sys
from collections import defaultdict
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# ── _shared 模块 import bootstrap（向内收：复用 SSoT 解析器）──
_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.frontmatter import (  # noqa: E402
    PY_HEADER_PATTERN,
    parse_byaml_anchor_from_file,
    parse_json_meta_from_file,
    parse_py_header_from_file,
)

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

# ── 各格式必填字段集（小写键名，与解析器返回一致）──
# A_full：.py code/script（src/scripts 下非 tests）
A_FULL_REQUIRED = [  # noqa: gate-vocab  # frontmatter 字段名（非 node_type 词表值；"blueprint"/"module"/"domain" 碰巧与 node_type 同名，语义无关）
    "blueprint", "module", "domain", "dependencies",
    "consumers", "startup", "maturity",
    "invariants", "modify-guard",
    "stability", "safety", "ai_autonomy",
    "error_contract", "tests", "ttl",  # v2.0.0: 补齐 15 字段全硬校验
]
# A_test：.py test（tests/ 下）
A_TEST_REQUIRED = ["blueprint", "module", "stability", "safety", "ai_autonomy"]
# E_shell：.sh/.ps1/.mmd
ESHELL_REQUIRED = ["blueprint", "stability", "safety", "ai_autonomy", "ttl"]
# B_yaml：.yaml（parse_byaml_anchor 返回 blueprint_id）
BYAML_REQUIRED = ["blueprint_id", "module_id", "stability", "safety_level", "ai_autonomy", "ttl"]
# C_json：.json（parse_json_meta 返回 blueprint）
CJSON_REQUIRED = ["blueprint", "module_id", "stability", "safety_level", "ai_autonomy", "ttl"]

ALL_FIELD_SETS = {
    "A_full": A_FULL_REQUIRED,
    "A_test": A_TEST_REQUIRED,
    "E_shell": ESHELL_REQUIRED,
    "B_yaml": BYAML_REQUIRED,
    "C_json": CJSON_REQUIRED,
}

# 排除目录（不扫描）
EXEMPT_DIRS = {
    "__pycache__", ".git", ".ailocks", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "_backups", "_archive", ".aidrafts", ".runtime",
    "data",  # data/ 下 .json/.yaml 是数据文件，非治理对象
    "models",  # ML 模型文件
}

# 统计
files_scanned = 0
files_complete = 0
files_missing_req = 0
files_no_header = 0
missing_stats: dict[str, int] = defaultdict(int)
missing_files: dict[str, list] = defaultdict(list)
format_counts: dict[str, int] = defaultdict(int)


def _is_exempt(path: Path) -> bool:
    """检查路径是否在排除目录下。"""
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        return True
    for part in rel.parts:
        if part in EXEMPT_DIRS:
            return True
    return False


def _get_format_and_fields(filepath: Path) -> tuple[str, list[str]] | None:
    """根据文件路径判定格式和必填字段集。

    Returns:
        (format_name, required_fields) 或 None（不校验的扩展名）。
    """
    suffix = filepath.suffix.lower()
    if suffix == ".py":
        # tests/ 下的 .py 用 A_test，其他用 A_full
        try:
            rel = filepath.relative_to(REPO_ROOT)
            if "tests" in rel.parts:
                return ("A_test", A_TEST_REQUIRED)
        except ValueError:
            pass
        return ("A_full", A_FULL_REQUIRED)
    if suffix in (".sh", ".ps1", ".mmd"):
        return ("E_shell", ESHELL_REQUIRED)
    if suffix == ".yaml":
        return ("B_yaml", BYAML_REQUIRED)
    if suffix == ".json":
        return ("C_json", CJSON_REQUIRED)
    return None


def _parse_header(filepath: Path, fmt: str) -> dict | None:
    """按格式路由到 SSoT 解析器。"""
    if fmt in ("A_full", "A_test", "E_shell"):
        return parse_py_header_from_file(filepath)
    if fmt == "B_yaml":
        return parse_byaml_anchor_from_file(filepath)
    if fmt == "C_json":
        return parse_json_meta_from_file(filepath)
    return None


def scan_file(filepath: Path) -> None:
    """校验单个文件的头部字段完整性。"""
    global files_scanned
    files_scanned += 1

    fmt_info = _get_format_and_fields(filepath)
    if not fmt_info:
        return
    fmt, required = fmt_info
    format_counts[fmt] += 1

    try:
        header = _parse_header(filepath, fmt)
    except (OSError, UnicodeDecodeError):
        return

    if not header:
        global files_no_header
        files_no_header += 1
        return

    # 字段名统一小写比较
    header_keys = {k.lower() for k in header}
    missing = [f for f in required if f not in header_keys]

    if not missing:
        global files_complete
        files_complete += 1
    else:
        global files_missing_req
        files_missing_req += 1
        for f in missing:
            missing_stats[f] += 1
            try:
                rel = str(filepath.relative_to(REPO_ROOT))
            except ValueError:
                rel = str(filepath)
            missing_files[f].append(rel)


def _collect_files() -> list[Path]:
    """收集所有需校验的文件（.py/.sh/.ps1/.mmd/.yaml/.json）。"""
    suffixes = {".py", ".sh", ".ps1", ".mmd", ".yaml", ".json"}
    scan_roots = [REPO_ROOT / "src", REPO_ROOT / "scripts", REPO_ROOT / "tests", REPO_ROOT / "docs"]
    files: list[Path] = []
    for root in scan_roots:
        if not root.exists():
            continue
        for fp in root.rglob("*"):
            if fp.is_file() and fp.suffix.lower() in suffixes and not _is_exempt(fp):
                files.append(fp)
    return sorted(files)


def main() -> int:
    files = _collect_files()

    for fp in files:
        if fp.name == "__init__.py":
            continue
        scan_file(fp)

    print("=" * 70)
    print("HEADER COMPLETENESS VERIFICATION (6 formats: A_full/A_test/E_shell/B_yaml/C_json)")
    print("=" * 70)
    print(f"Files scanned:           {files_scanned}")
    print(f"  By format:             {dict(format_counts)}")
    print(f"Files complete (all req): {files_complete}")
    print(f"Files missing required:   {files_missing_req}")
    print(f"Files no header (skip):   {files_no_header}")
    print()
    print("MISSING FIELD STATISTICS:")
    print(f"  {'Field':<20} {'Missing':>8}")
    print(f"  {'-' * 20} {'-' * 8}")
    all_fields = set()
    for fields in ALL_FIELD_SETS.values():
        all_fields.update(fields)
    for f in sorted(all_fields):
        if missing_stats.get(f, 0) > 0:
            print(f"  {f:<20} {missing_stats[f]:>8}")

    if files_missing_req > 0:
        print("\nFiles missing required fields:")
        for f in sorted(missing_files.keys()):
            if missing_files[f]:
                print(f"\n  [{f}] missing in {len(missing_files[f])} files:")
                for fn in missing_files[f][:5]:
                    print(f"    - {fn}")
                if len(missing_files[f]) > 5:
                    print(f"    ... and {len(missing_files[f]) - 5} more")

    print("\n" + "=" * 70)
    if files_missing_req == 0:
        print("RESULT: ALL FILES HAVE COMPLETE REQUIRED HEADERS ✓")
        return 0
    else:
        print(f"RESULT: {files_missing_req} FILES STILL MISSING REQUIRED FIELDS ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
