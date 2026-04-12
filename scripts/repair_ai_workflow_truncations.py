#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
修复 AI_WORKFLOW 文档中因历史替换字符/清理导致的常见截断片段：
- `核心价` -> `核心价值`
- `可追*`/`可评*`/`可复*` 等 -> 对应完整词
- `提供数据支` -> `提供数据支持`
- `避免重复造轮` -> `避免重复造轮子`
- 少量列表项缺失 `**` 的补齐（保守）

用法：
  python scripts/repair_ai_workflow_truncations.py docs/10_AI_WORKFLOW
"""

from __future__ import annotations

import argparse
import pathlib
import re


RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"核心价\b"), "核心价值"),
    (re.compile(r"提供数据支\b"), "提供数据支持"),
    (re.compile(r"清晰可\b"), "清晰可查"),
    (re.compile(r"避免重复造轮\b"), "避免重复造轮子"),
    # 可追/可评/可复：按常见语义补齐
    (re.compile(r"AI工作可追\*"), "AI工作可追溯"),
    (re.compile(r"AI效果可评\*"), "AI效果可评估"),
    (re.compile(r"AI知识可复\*"), "AI知识可复用"),
    (re.compile(r"数据可追\*"), "数据可追溯"),
    (re.compile(r"实验可复\*"), "实验可复现"),
    (re.compile(r"完整复\b"), "完整复现"),
    # 处理列表项中缺失加粗闭合：`**数据持久化: ...` -> `**数据持久化**: ...`
    (re.compile(r"\*\*(数据持久化):\s*"), r"**\1**: "),
    (re.compile(r"\*\*(开源集成):\s*"), r"**\1**: "),
    (re.compile(r"集成成熟开源项\b"), "集成成熟开源项目"),
]


def repair(text: str) -> str:
    for pat, repl in RULES:
        text = pat.sub(repl, text)
    return text


def iter_targets(path: pathlib.Path) -> list[pathlib.Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.path)
    targets = iter_targets(root)
    changed = 0

    for fp in targets:
        text = fp.read_text(encoding="utf-8", errors="replace")
        new_text = repair(text)
        if new_text == text:
            continue
        changed += 1
        if not args.dry_run:
            fp.write_text(new_text, encoding="utf-8", newline="\n")
        print("[OK]", fp.name)

    print("ChangedFiles=", changed, "DryRun=", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

