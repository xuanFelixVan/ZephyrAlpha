# [BLUEPRINT] MOD-INF-005 | scripts/governance/d2_links/audit_broken_links.py | §
# [MODULE] scripts.governance.d2_links.audit_broken_links
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d2_links.__init__
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
"""检测文档/数据文件中的断链与幽灵引用。

治本背景（2026-06-29）：
    调研发现 AI 在 .md/.csv/.yaml 中编造虚假文件引用（如 dom_gov_001 虚假审计闭环：
    index.md 列 22 张不存在的任务卡，move_plan.csv 引用 4 个不存在的文件）。
    现有 audit_broken_links.py 仅检测 .md 的 markdown 链接语法，漏检：
      - .csv/.yaml/.json 中的纯文本路径引用
      - frontmatter 中的 blueprint_id 引用
      - 跨目录的虚假文件引用闭环
    本扩展治本：从仅 .md markdown 链接扩展到多文件类型 + 多引用语法。

支持模式：
    python audit_broken_links.py <文件>          # 检测单个文件
    python audit_broken_links.py <目录>          # 递归检测目录
    python audit_broken_links.py <文件> --ci      # 硬阻断模式（exit 1）
    python audit_broken_links.py <文件> --warn-only  # 只警告（exit 0）

检测的引用类型：
    1. Markdown 链接 [text](target)        —— .md 文件
    2. 纯文本文件路径（含 / + 扩展名）      —— .md/.csv/.yaml/.yml/.json
    3. CSV 列值中的文件路径               —— .csv 文件
    4. YAML 值中的文件路径               —— .yaml/.yml 文件

跳过的引用：
    - http://, https://, ftp://, mailto: URL
    - 锚点引用 (#anchor)
    - 不支持的文件扩展名
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import csv
import re

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

# Markdown 链接语法：[text](target)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# 纯文本文件路径：匹配 path/to/file.ext 格式（要求含 / 分隔符 + 有扩展名）
# 注意：不要求以 docs/ 开头，因为相对路径也可能是 ./file.md 或 subdir/file.yaml
# 中文前缀防误捕（与 reconciliation_registry.py 一致）：
#   lookbehind 用 [a-zA-Z0-9/] 而非 \w（中文是 \w，会阻挡中文后的路径起点，
#   导致"删除architecture_model/foo.yaml"中"删除"被吞入匹配）；
#   首字符限 [a-zA-Z]（路径必以 ASCII 字母起，杜绝中文前缀被捕获）。
TEXT_PATH_RE = re.compile(
    r"(?<![a-zA-Z0-9/])([a-zA-Z][\w\-./]*?/[\w\-]+\.(?:md|yaml|yml|json|py|ps1|sh|toml|txt|csv))\b"
)

# YAML 值中的文件路径：value: path/to/file.ext
# 同样用 [a-zA-Z] 首字符防中文前缀误捕
YAML_PATH_RE = re.compile(
    r":\s*[\"']?([a-zA-Z][\w\-./]*?/[\w\-]+\.(?:md|yaml|yml|json|py|ps1|sh|toml|txt|csv))[\"']?\s*$",
    re.MULTILINE,
)

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = frozenset({".md", ".csv", ".yaml", ".yml", ".json"})

# 跳过的 URL 前缀
URL_PREFIXES = ("http://", "https://", "ftp://", "mailto:", "#", "data:")

# basename 全局搜索缓存（lazy 初始化，策略3 兜底用）
# 作用：markdown 链接 [text](blueprint.md) 常用裸文件名，策略1/2 解析失败但文件实际
# 存在于项目其他目录。构建全项目 basename→路径集合，O(1) 查找消除大量误报。
_BASENAME_CACHE: set[str] | None = None


def _is_url(target: str) -> bool:
    """判断是否为 URL 或锚点（应跳过）。"""
    return any(target.startswith(p) for p in URL_PREFIXES)


def _get_basename_cache() -> set[str]:
    """获取（lazy 构建）全项目 basename 集合。

    扫描 REPO_ROOT 下所有文件（排除 .git/__pycache__/.runtime/.venv/node_modules），
    收集 basename 到 set 中。一次构建多次复用（模块级缓存）。
    """
    global _BASENAME_CACHE
    if _BASENAME_CACHE is not None:
        return _BASENAME_CACHE
    _BASENAME_CACHE = set()
    _skip_dirs = frozenset({".git", "__pycache__", ".runtime", ".venv", "node_modules", ".pytest_cache"})
    for p in REPO_ROOT.rglob("*"):
        if p.is_file() and not any(part in _skip_dirs for part in p.parts):
            _BASENAME_CACHE.add(p.name)
    return _BASENAME_CACHE


def _resolve_and_check(ref: str, source: Path) -> str | None:
    """解析引用路径并检查文件是否存在。

    路径解析策略（三重尝试，治本 GAP-1 + 裸文件名兜底）：
      1. 先相对于 source.parent 解析（markdown 链接习惯）
      2. 如果不存在，尝试相对于 REPO_ROOT 解析（CSV/YAML 项目根相对路径）
      3. 如果仍不存在，检查 basename 是否在全项目中存在（裸文件名兜底）

    :param ref: 引用路径（相对或绝对）
    :param source: 引用所在文件
    :return: 断链描述字符串（如果断链），None 如果通过
    """
    if _is_url(ref):
        return None

    # 去掉锚点
    ref = ref.split("#")[0].strip()
    if not ref:
        return None

    # 策略1：相对于文件所在目录解析（markdown 链接风格）
    try:
        target_path = (source.parent / ref).resolve()
        if target_path.exists():
            return None
    except (OSError, ValueError):
        pass

    # 策略2：相对于项目根解析（CSV/YAML 项目根相对路径风格）
    try:
        target_path = (REPO_ROOT / ref).resolve()
        if target_path.exists():
            return None
    except (OSError, ValueError):
        pass

    # 策略3：basename 全局搜索兜底（裸文件名如 blueprint.md 在项目其他目录存在）
    basename = ref.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if basename in _get_basename_cache():
        return None

    return f"断链: {ref} ← {source.name}"


def _extract_md_links(content: str) -> list[str]:
    """提取 Markdown 链接中的目标路径。"""
    refs = []
    for match in MD_LINK_RE.finditer(content):
        target = match.group(2).split("#")[0].strip()
        if target:
            refs.append(target)
    return refs


def _extract_text_paths(content: str) -> list[str]:
    """提取纯文本中的文件路径引用。"""
    refs = []
    for match in TEXT_PATH_RE.finditer(content):
        path_str = match.group(1)
        if not _is_url(path_str):
            refs.append(path_str)
    return refs


def _extract_csv_paths(content: str) -> list[str]:
    """提取 CSV 文件中的文件路径列值。"""
    refs = []
    try:
        reader = csv.reader(content.splitlines())
        for row in reader:
            for cell in row:
                cell = cell.strip().strip('"').strip("'")
                # CSV 中的路径引用：含 / 且有文件扩展名
                if "/" in cell and "." in cell:
                    # 验证是否以已知扩展名结尾
                    if any(cell.endswith(ext) for ext in (".md", ".yaml", ".yml", ".json", ".py", ".ps1", ".sh", ".toml", ".txt", ".csv")):
                        if not _is_url(cell):
                            refs.append(cell)
    except Exception:
        pass  # CSV 解析失败则跳过
    return refs


def _extract_yaml_paths(content: str) -> list[str]:
    """提取 YAML 文件值中的文件路径。"""
    refs = []
    for match in YAML_PATH_RE.finditer(content):
        path_str = match.group(1)
        if not _is_url(path_str):
            refs.append(path_str)
    return refs


def audit_file(file_path: str | Path) -> tuple[bool, list[str]]:
    """审计单个文件的断链与幽灵引用。

    :param file_path: 文件路径
    :return: (是否通过, 断链列表)
    """
    p = Path(file_path)
    if not p.exists():
        return False, [f"文件不存在: {file_path}"]
    if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return True, []  # 不支持的扩展名跳过

    try:
        content = p.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError) as exc:
        return False, [f"读取失败: {p} ({exc})"]

    broken: list[str] = []

    # 根据扩展名选择提取器
    refs: list[str] = []
    ext = p.suffix.lower()
    if ext == ".md":
        refs.extend(_extract_md_links(content))
        refs.extend(_extract_text_paths(content))
    elif ext == ".csv":
        refs.extend(_extract_csv_paths(content))
    elif ext in (".yaml", ".yml"):
        refs.extend(_extract_yaml_paths(content))
        refs.extend(_extract_text_paths(content))
    elif ext == ".json":
        refs.extend(_extract_text_paths(content))

    # 去重并检查
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        result = _resolve_and_check(ref, p)
        if result:
            broken.append(result)

    return len(broken) == 0, broken


def audit_directory(dir_path: str | Path) -> tuple[bool, list[str]]:
    """递归审计目录下所有支持文件的断链。"""
    p = Path(dir_path)
    if not p.exists():
        return False, [f"目录不存在: {dir_path}"]

    all_broken: list[str] = []
    for ext in SUPPORTED_EXTENSIONS:
        for file_path in p.rglob(f"*{ext}"):
            # 跳过 .git, node_modules, __pycache__ 等
            if any(part in (".git", "node_modules", "__pycache__", ".runtime", ".venv") for part in file_path.parts):
                continue
            ok, broken = audit_file(file_path)
            if not ok:
                all_broken.extend(broken)

    return len(all_broken) == 0, all_broken


def main() -> int:
    """Entry point: parse args, run audit, return exit code."""
    parser = argparse.ArgumentParser(
        description="检测文档/数据文件中的断链与幽灵引用"
    )
    parser.add_argument(
        "path",
        nargs="+",
        help="要检测的文件或目录路径（支持多个）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 硬阻断模式：发现断链时 exit 1（用于 pre-commit 钩子）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="只警告模式：发现断链时仅打印，exit 0（用于过渡期巡检）",
    )
    args = parser.parse_args()

    all_broken: list[str] = []
    for path_str in args.path:
        p = Path(path_str)
        if p.is_dir():
            ok, broken = audit_directory(p)
        else:
            ok, broken = audit_file(p)
        all_broken.extend(broken)

    if not all_broken:
        print("✅ 无断链")
        return EXIT_PASS

    print(f"❌ 发现 {len(all_broken)} 条断链:")
    for b in all_broken:
        print(f"  → {b}")

    if args.warn_only:
        return EXIT_PASS
    if args.ci:
        return EXIT_FINDINGS
    # 默认：打印断链但 exit 0（兼容旧行为）
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
