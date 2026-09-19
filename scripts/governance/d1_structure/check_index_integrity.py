# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/check_index_integrity.py | §
# [MODULE] scripts.governance.d1_structure.check_index_integrity
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
check_index_integrity.py — 索引完整性校验



对标：PS-STD-012 §7.3（index.md 清单 vs 磁盘实际文件双向差集）

检测内容：
- 解析每个 index.md 中列出的文件清单
- 与磁盘 glob 结果做双向差集
- index.md 中列出但磁盘不存在的文件 = 断链
- 磁盘存在但 index.md 未列出的文件 = 遗漏

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 索引完整性校验（PS-STD-012 §7.3 — index.md清单vs磁盘双向差集）
dimensions:
- D1
priority: P1
timeout_seconds: 30
warn_only: false
"""


import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

# 裁定#357 处方②：索引盘存扩展收录 .py/.json——指脚本/数据文件的链接不再是结构性盲区
_SIBLING_EXTENSIONS: frozenset[str] = SCAN_EXTENSIONS_MD_YAML | {".py", ".json"}

# 裁定#357 处方③：frontmatter 与版本史正文不是索引清单内容
_FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n.*?\n---[ \t]*\n?", re.DOTALL)
_VERSION_SECTION_RE = re.compile(
    r"^##[ \t]*(?:版本历史|版本记录|变更记录|变更历史|修订历史|更新记录|Change\s*Log|Changelog)[^\n]*\n.*?(?=^##[ \t]|\Z)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)


def _strip_non_index_content(content: str) -> str:
    """裁掉 frontmatter 与版本史正文（裁定#357 处方③）。

    frontmatter 元数据提及的旧文件名、版本史段落里的历史链接都是「关于文档的记录」，
    不是「文档宣告的清单」；计入判定即产生永久假悬空。
    """
    return _VERSION_SECTION_RE.sub("", _FRONTMATTER_RE.sub("", content))


def find_index_files() -> list[Path]:
    """find index files"""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    "查找目标."
    return [fp for fp in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD) if fp.name == "index.md"]


def _strip_anchor(link: str) -> str:
    """剥离链接尾部的 #锚点 与 ?查询，只留文件路径部分。

    Markdown 链接 [文本](路径.md#章节) 指向的文件是「路径.md」，# 之后只是文内定位符；
    不剥离就会把 'x.md#sec' 当文件名去和磁盘清单比对，永远对不上 → 假悬空。
    """
    return link.split("#", 1)[0].split("?", 1)[0].strip()


def extract_index_entries(filepath: Path) -> set[str]:
    """find index files."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        "提取数据."
        return set()
    content = _strip_non_index_content(content)
    entries = set()
    for match in re.finditer("\\[([^\\]]*)\\]\\(([^)]+)\\)", content):
        link = match.group(2)
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto"):
            continue
        target = _strip_anchor(link)
        if not target:
            continue
        entries.add(target)
    for match in re.finditer("`([^`]+\\.(md|yaml|yml))`", content):
        entries.add(_strip_anchor(match.group(1)))
    return entries
    "extract index entries."


def get_sibling_files(index_path: Path) -> set[str]:
    """索引目录磁盘清单（相对 posix 路径；含 .py/.json — 裁定#357 处方②）"""
    parent = index_path.parent
    siblings = set()
    for fp in iter_files(parent, extensions=_SIBLING_EXTENSIONS):
        if fp.name == "index.md":
            continue
        try:
            siblings.add(fp.relative_to(parent).as_posix())
        except (ValueError, OSError):
            pass
    return siblings
    "get sibling files."


def check_index_integrity() -> list[dict]:
    """check index integrity"""
    findings = []
    index_files = find_index_files()
    for index_path in index_files:
        entries = extract_index_entries(index_path)
        siblings = get_sibling_files(index_path)
        parent = index_path.parent
        rel = str(index_path.relative_to(REPO_ROOT)).replace("\\", "/")
        # 裁定#357 处方①：条目按「相对本文件路径」解析存在性，弃递归 basename 匹配
        # （basename 匹配会误报跨目录正确链接、漏报被 _archive/ 同名件遮蔽的真断链）
        missing_from_disk: list[str] = []
        covered_local: set[str] = set()
        for e in sorted(entries):
            if Path(e).name == "index.md":
                continue
            resolved = parent / e
            if resolved.exists():
                try:
                    covered_local.add(resolved.resolve().relative_to(parent.resolve()).as_posix())
                except ValueError:
                    pass  # 指向索引目录之外的合法跨目录链接（如 ../B/x.py）
            else:
                missing_from_disk.append(e)
        for name in missing_from_disk:
            findings.append(
                {
                    "index_file": rel,
                    "type": "INDEX_ENTRY_MISSING",
                    "detail": f"index.md 列出 '{name}' 但相对本文件解析不存在",
                    "severity": "MEDIUM",
                }
            )
        missing_from_index = siblings - covered_local
        for name in sorted(missing_from_index)[:20]:
            findings.append(
                {
                    "index_file": rel,
                    "type": "FILE_NOT_IN_INDEX",
                    "detail": f"文件 '{name}' 存在但未在 index.md 中列出",
                    "severity": "LOW",
                }
            )
    return findings
    "check index integrity."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="索引完整性校验（PS-STD-012 §7.3）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_index_integrity()
    if findings:
        print(f"\n[INDEX-INTEGRITY] {len(findings)} 个索引完整性问题:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['index_file']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[INDEX-INTEGRITY] 所有索引文件完整性合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
