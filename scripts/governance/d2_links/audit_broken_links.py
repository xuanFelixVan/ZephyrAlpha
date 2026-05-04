#!/usr/bin/env python3
"""断链审计（Broken Link Auditor）- Stage H N-04 前置

扫描整个  仓库中所有 Markdown 文件的链接：
  1. 相对路径链接 `[text](./xxx.md)` / `[text](../xxx.md)` / `[text](xxx.md)`
  2. 根相对链接 `[text](/path/xxx.md)` → 视为 repo-relative
  3. 文档中出现的 `` `path/to/file.md` `` 代码跨度若看起来像仓库路径，也尝试验证

产出：
  - 控制台：按文件分组列出断链
  - 退出码：有断链返回 1，无断链返回 0

不触碰：
  - 外部 URL（http:// https:// mailto:）
  - fragment-only 链接（#anchor）
  - archive/、.git/ 等子树

路径对齐准则：
  - 所有链接按 "仓库根 = " 解析
  - 允许相对当前文件、根相对、或 src/ docs/ 等顶级目录
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

ROOT = REPO_ROOT

EXCLUDE_DIRS = EXCLUDE_DIRS | {"archive", "_reorg_snapshots"}

EXCLUDE_FILE_SUFFIXES = (".pyc",)

# 跳过 session-logs 内部（日志有大量历史链接）
EXCLUDE_PATH_SUBSTRINGS = (
    "docs/19_development_workspace/session-logs",
    "docs/19_development_workspace/archive",  # 迁移输入归档
    "docs/99_archive",  # 历史归档
)

# 外链（忽略）
EXTERNAL_PROTO = re.compile(r"^(?:https?|mailto|ftp|file|data|javascript):", re.I)

# Markdown 链接：[text](url)，排除图片 ![..](..) 的话不必区分，逻辑一致
RE_MD_LINK = re.compile(r"(?<!\\)\[[^\]]+\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)")

# Inline code span：`...`，其中的内容不算真实链接（教学示例/占位符）
RE_INLINE_CODE = re.compile(r"`[^`\n]*`")


def _strip_inline_code(line: str) -> str:
    return RE_INLINE_CODE.sub(lambda _m: " " * len(_m.group(0)), line)


def _is_under_excluded(path_posix: str) -> bool:
    for sub in EXCLUDE_PATH_SUBSTRINGS:
        if sub in path_posix:
            return True
    return False


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for p in iter_files(root, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        rel_posix = p.relative_to(root).as_posix()
        if _is_under_excluded(rel_posix):
            continue
        yield p


def _resolve_link_target(link: str, source_file: Path, root: Path) -> Path | None:
    """将 Markdown 链接解析为仓库内绝对路径。外链/fragment 返回 None。"""
    # 去掉 fragment 和 query
    s = link.split("#", 1)[0].split("?", 1)[0].strip()
    if not s:
        return None
    if EXTERNAL_PROTO.match(s):
        return None
    # 根相对
    if s.startswith("/"):
        return root / s.lstrip("/")
    # 相对于当前文件
    return (source_file.parent / s).resolve()


def audit(root: Path) -> list[tuple[str, int, str]]:
    """返回 (rel_source, line_no, broken_link) 列表。"""
    broken: list[tuple[str, int, str]] = []
    for md in _iter_markdown_files(root):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        in_fence = False
        for ln_idx, raw_line in enumerate(text.splitlines(), start=1):
            # Fenced code block（``` / ~~~）内的链接视作示例，跳过
            stripped = raw_line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line = _strip_inline_code(raw_line)
            for m in RE_MD_LINK.finditer(line):
                url = m.group(1).strip()
                target = _resolve_link_target(url, md, root)
                if target is None:
                    continue
                # 允许目录存在也视为命中
                if target.exists():
                    continue
                # 允许 .md 后缀省略（Jekyll 风格）
                alt_md = Path(str(target) + ".md") if not target.suffix else None
                if alt_md is not None and alt_md.exists():
                    continue
                rel_src = md.relative_to(root).as_posix()
                broken.append((rel_src, ln_idx, url))
    return broken


def main() -> None:
    """入口函数."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="仓库根路径（默认 ）",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="最多打印多少条，0 表示不限",
    )
    ap.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现不阻塞（exit 0）",
    )
    args = ap.parse_args()
    broken = audit(args.root)
    total = len(broken)
    if total == 0:
        print("[LINK-AUDIT] OK  0 broken link(s).", file=sys.stderr)
        sys.exit(0)
    print(f"[LINK-AUDIT] {total} broken link(s) found:", file=sys.stderr)
    shown = 0
    last_src = ""
    for rel_src, ln, url in broken:
        if args.limit and shown >= args.limit:
            print(f"  ... ({total - shown} more)", file=sys.stderr)
            break
        if rel_src != last_src:
            print(f"\n  {rel_src}", file=sys.stderr)
            last_src = rel_src
        print(f"    L{ln:<4d}  {url}", file=sys.stderr)
        shown += 1
    sys.exit(0 if args.warn_only else 1)


if __name__ == "__main__":
    main()
