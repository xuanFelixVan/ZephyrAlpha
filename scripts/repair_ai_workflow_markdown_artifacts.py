#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复上一轮 U+FFFD 清理后遗留的 Markdown 伪影（如 `价*`、`索*`、`系统*核心基础设施**` 等）。

说明：
- 这些伪影来源于原文本中 `�` 落在词中间或 Markdown 强调符附近。
- 本脚本只做“高置信度、可推断”的补全与排版修复，避免大范围改写。
"""

from __future__ import annotations

import argparse
import pathlib
import re


def fix_common_tokens(text: str) -> str:
    # 1) 常见词尾被截断：`价*` `索*` `概*` 等
    replacements = [
        ("总索*", "总索引"),
        ("导*", "导览"),
        ("概*", "概述"),
        ("价*", "价值"),
        ("优*", "优化"),
        ("集*", "集成"),
        ("持久*", "持久化"),
        ("架*", "架构"),
        ("文*", "文档"),
        ("治*", "治理"),
        ("保*", "保障"),
        ("索*", "索引"),
    ]
    for a, b in replacements:
        text = text.replace(a, b)

    # 2) 修复 `系统*核心基础设施**` 这类断裂的强调
    text = text.replace("系统*核心基础设施**", "系统的**核心基础设施**")

    # 3) 修复部分列表被拼接（仅处理明显模式）
    text = text.replace("完整过- ✅", "完整过程\n- ✅")
    text = text.replace("全流程数- ✅", "全流程数据\n- ✅")

    # 4) 清理一些落单的反引号/星号组合造成的异常（保守处理）
    #    - 例如表格中出现 `索|` 这种情况已由上面词尾修复覆盖
    #    - 把连续多个 `**` 中间为空的情况去掉
    text = re.sub(r"\*\*\s*\*\*", "**", text)

    return text


def iter_targets(path: pathlib.Path) -> list[pathlib.Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="docs/10_AI_WORKFLOW 或单个 .md 文件")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.path)
    targets = iter_targets(root)
    if not targets:
        print("[ERROR] no targets found")
        return 2

    changed = 0
    for fp in targets:
        text = fp.read_text(encoding="utf-8", errors="replace")
        new_text = fix_common_tokens(text)
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

