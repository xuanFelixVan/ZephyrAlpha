# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] scripts.governance.d7_code.check_module_id_consistency
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.module_id_consistency_gate (gate logic reference)
# [CONSUMERS] GitCommitGateway; session_worktree_commit; CI/CD audit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] --scan-existing scans ALL .py files for pre-existing module_id conflicts; default mode checks staged files only
# [MODIFY-GUARD] module_id_consistency_gate.py (gate logic source of truth)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=pass; exit 1=conflicts found; exit 2=usage error
# [TESTS] tests/governance/commit_gates/test_module_id_consistency_gate.py
# [TTL] permanent
# [A_module] module_id=MOD-GATE_ENGINE_audit_module_id | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
"""check_module_id_consistency.py — module_id 全仓一致性扫描（--scan-existing 模式）.

用法:
  # 扫描全仓所有 .py 文件的 module_id 冲突（含存量基线）
  python scripts/governance/d7_code/check_module_id_consistency.py --scan-existing

  # 只扫描 src/zephyr/ 下的文件
  python scripts/governance/d7_code/check_module_id_consistency.py --scan-existing --src-only

  # JSON 格式输出（供 CI 消费）
  python scripts/governance/d7_code/check_module_id_consistency.py --scan-existing --json

退出码:
  0 — 无冲突
  1 — 发现冲突
  2 — 参数错误

冲突分类:
  Type A — __init__.py 复制（子包 __init__.py 复制父包 module_id）
  Type B — 跨域副本（不同域的文件声明相同 module_id）
  Type C — bridges 副本（bridges/ 文件复制父目录文件 module_id）
  Type D — 其他（多副本/测试文件等）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# === 正则定义（与 module_id_consistency_gate.py 保持一致）===

# 匹配 [A_module] module_id=XXX 或 [A_module] module_id: XXX 头部声明
_RE_HEADER_MODULE_ID = re.compile(
    r"^#\s*\[A_\w+\]\s*module_id[:=]\s*(\S+)", re.MULTILINE
)

# 匹配游离的 module_id: 声明行（非 [A_module] 头部，YAML 风格）
_RE_STRAY_MODULE_ID = re.compile(
    r"^module_id:\s*([A-Z]+(?:-[A-Z]+)*-\w+)\s*(?:\([^)]*\))?\s*$", re.MULTILINE
)

# 排除模式：Python 代码中的 module_id 用法（非声明）
_EXCLUDE_PATTERNS = [
    re.compile(r'def\s+\w+\(.*module_id'),
    re.compile(r'module_id\s*=\s*"'),
    re.compile(r'module_id"\s*:\s*"'),
    re.compile(r'module_id:\s*str\b'),
    re.compile(r'module_id:\s*Optional'),
    re.compile(r'self\._?module_id'),
    re.compile(r'module_id\s*=\s*["\']'),
]


def _extract_module_id(content: str) -> str | None:
    """从文件内容提取 [A_module] 头部的 module_id 声明.

    只匹配注释行中的声明（# [A_module] module_id=XXX），
    排除 Python 代码中的 module_id 用法（赋值/类型注解/字典 key）。
    """
    for line in content.splitlines()[:30]:
        is_comment = line.strip().startswith("#")
        if not is_comment:
            # 非注释行——检查是否是 YAML 风格的 module_id: XXX
            if any(pat.search(line) for pat in _EXCLUDE_PATTERNS):
                continue
            # 只接受大写前缀的 module_id 值
            m = re.search(r"module_id:\s*(\S+)", line)
            if m:
                mid = m.group(1).strip()
                if mid.startswith(("MOD-", "SH-", "CFG-", "PS-", "TRAE-")):
                    if not (mid.startswith('"') or mid.startswith("'")):
                        return mid
            continue

        # 注释行——正常匹配
        m = _RE_HEADER_MODULE_ID.search(line)
        if m:
            mid = m.group(1).strip()
            if not (mid.startswith('"') or mid.startswith("'")):
                return mid
    return None


def _has_stray_module_id(content: str) -> list[str]:
    """检测文件体内是否有游离的 module_id: 声明行（非头部 [A_module] 声明）.

    返回游离行的 module_id 值列表。
    """
    strays = []
    for match in _RE_STRAY_MODULE_ID.finditer(content):
        line_start = content.rfind("\n", 0, match.start()) + 1
        line = content[line_start:match.end()]
        # 排除注释行（# 开头的 [A_module] 声明不算游离）
        if line.strip().startswith("#"):
            continue
        strays.append(match.group(1))
    return strays


def scan_existing(root: Path, src_only: bool = False) -> dict:
    """扫描全仓所有 .py 文件的 module_id 冲突.

    Args:
        root: 项目根目录
        src_only: 只扫描 src/ 目录

    Returns:
        {
            "total_ids": int,
            "conflict_groups": int,
            "conflict_files": int,
            "conflicts": {module_id: [file_paths]},
            "stray_lines": {file_path: [module_ids]},
            "by_type": {"A": [...], "B": [...], "C": [...], "D": [...]},
        }
    """
    id_to_files: dict[str, list[str]] = defaultdict(list)
    stray_lines: dict[str, list[str]] = {}

    scan_dirs = [root / "src"]
    if not src_only:
        tests_dir = root / "tests"
        if tests_dir.exists():
            scan_dirs.append(tests_dir)

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py in scan_dir.rglob("*.py"):
            try:
                content = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            mid = _extract_module_id(content)
            if mid:
                rel = str(py.relative_to(root)).replace("\\", "/")
                id_to_files[mid].append(rel)

            # 检查游离行
            strays = _has_stray_module_id(content)
            if strays:
                rel = str(py.relative_to(root)).replace("\\", "/")
                stray_lines[rel] = strays

    # 找冲突
    conflicts = {mid: files for mid, files in id_to_files.items() if len(files) > 1}

    # 分类
    type_a = []  # __init__.py 复制
    type_b = []  # 跨域副本
    type_c = []  # bridges 副本
    type_d = []  # 其他

    for mid, files in sorted(conflicts.items()):
        all_init = all(Path(f).name == "__init__.py" for f in files)
        has_bridge = any("bridge" in f.lower() for f in files)

        if all_init:
            type_a.append((mid, files))
        elif has_bridge:
            type_c.append((mid, files))
        elif len(files) == 2:
            type_b.append((mid, files))
        else:
            type_d.append((mid, files))

    return {
        "total_ids": len(id_to_files),
        "conflict_groups": len(conflicts),
        "conflict_files": sum(len(f) for f in conflicts.values()),
        "conflicts": conflicts,
        "stray_lines": stray_lines,
        "by_type": {
            "A": type_a,
            "B": type_b,
            "C": type_c,
            "D": type_d,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="module_id 全仓一致性扫描（--scan-existing 模式）"
    )
    parser.add_argument(
        "--scan-existing",
        action="store_true",
        help="扫描全仓所有 .py 文件的 module_id 冲突（含存量基线）",
    )
    parser.add_argument(
        "--src-only",
        action="store_true",
        help="只扫描 src/ 目录（不扫描 tests/）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 格式输出（供 CI 消费）",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="项目根目录（默认自动检测）",
    )
    args = parser.parse_args()

    if not args.scan_existing:
        parser.print_help()
        return 2

    root = Path(args.root) if args.root else Path(__file__).resolve().parents[3]
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    result = scan_existing(root, src_only=args.src_only)

    if args.json:
        # JSON 输出—— conflicts 转为可序列化格式
        out = {
            "total_ids": result["total_ids"],
            "conflict_groups": result["conflict_groups"],
            "conflict_files": result["conflict_files"],
            "conflicts": result["conflicts"],
            "stray_lines": result["stray_lines"],
            "by_type": {
                k: [{"module_id": mid, "files": files} for mid, files in v]
                for k, v in result["by_type"].items()
            },
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        # 人类可读输出
        print(f"=== Module ID 冲突扫描结果（--scan-existing） ===")
        print(f"项目根: {root}")
        print(f"总 module_id 数: {result['total_ids']}")
        print(f"冲突组数: {result['conflict_groups']}")
        print(f"冲突文件总数: {result['conflict_files']}")

        for type_name, type_label in [("A", "__init__.py 复制"), ("B", "跨域副本"), ("C", "bridges 副本"), ("D", "其他")]:
            groups = result["by_type"][type_name]
            print(f"\n--- Type {type_name}: {type_label} ({len(groups)} 组) ---")
            for mid, files in groups[:20]:
                print(f"  {mid}:")
                for f in files:
                    print(f"    {f}")
            if len(groups) > 20:
                print(f"  ... 还有 {len(groups) - 20} 组")

        if result["stray_lines"]:
            print(f"\n--- 游离 module_id 声明行 ({len(result['stray_lines'])} 文件) ---")
            for f, mids in list(result["stray_lines"].items())[:20]:
                print(f"  {f}: {mids}")
            if len(result["stray_lines"]) > 20:
                print(f"  ... 还有 {len(result['stray_lines']) - 20} 文件")

    return 1 if result["conflict_groups"] > 0 or result["stray_lines"] else 0


if __name__ == "__main__":
    sys.exit(main())
