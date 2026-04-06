#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI_WORKFLOW 文档 U+FFFD（�）内容级修复器（高置信度替换 + 结构化清理）

目标：
- 优先修复 YAML 元数据、标题、目录锚点、列表符号位中的 `�`
- 仅做“可从上下文明确推断”的替换；无法推断的保留给后续人工逐点处理

用法：
  python scripts/repair_ai_workflow_ufffd.py docs/10_AI_WORKFLOW --dry-run
  python scripts/repair_ai_workflow_ufffd.py docs/10_AI_WORKFLOW
  python scripts/repair_ai_workflow_ufffd.py docs/10_AI_WORKFLOW/INDEX.md
"""

from __future__ import annotations

import argparse
import pathlib
import re

REP = "\ufffd"  # '�'


def repair_text(text: str) -> str:
    # 1) 高置信度：owner/standard_type 常见字段
    text = re.sub(r"(?m)^owner:\s*首席架构\ufffd\?\s*$", "owner: 首席架构师", text)
    text = re.sub(r"(?m)^standard_type:\s*专业机构级蓝\ufffd\?\s*$", "standard_type: 专业机构级蓝图", text)
    text = re.sub(r"(?m)^standard_type:\s*专业机构级索\ufffd\?\s*$", "standard_type: 专业机构级索引", text)

    # 2) 列表符号：`- �?**xxx**` -> `- ✅ **xxx**`
    text = re.sub(r"(?m)^(\s*[-*]\s*)\ufffd\?\s*(\*\*)", r"\1✅ \2", text)
    # 行内：`�?**` -> `✅ **`
    text = text.replace("\ufffd?**", "✅ **")

    # 3) 常见短语（局部片段修复）
    phrase_map = [
        ("模块总索\ufffd?", "模块总索引"),
        ("快速导\ufffd?", "快速导览"),
        ("模块概\ufffd?", "模块概述"),
        ("模块架\ufffd?", "模块架构"),
        ("实施路\ufffd?", "实施路径"),
        ("文档治\ufffd?", "文档治理"),
        ("质量保\ufffd?", "质量保障"),
        ("相关文\ufffd?", "相关文档"),
        ("专业机构级蓝\ufffd?", "专业机构级蓝图"),
        ("专业机构级索\ufffd?", "专业机构级索引"),
        ("首席架构\ufffd?", "首席架构师"),
        ("AI工作记录与优\ufffd?", "AI工作记录与优化"),
        ("AI工作汇报与交\ufffd?", "AI工作汇报与交付"),
        ("开源模块选型与推\ufffd?", "开源模块选型与推荐"),
        ("适用范围", "适用范围"),
    ]
    for a, b in phrase_map:
        text = text.replace(a, b)

    # 4) 通用清理：大量场景表现为 `�?`（替换字符+问号残渣）
    #    这里将其移除，避免残留破坏可读性/锚点。
    text = text.replace("\ufffd?", "")

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

    changed_files = 0
    total_removed = 0

    for fp in targets:
        text = fp.read_text(encoding="utf-8", errors="replace")
        if REP not in text:
            continue
        before = text.count(REP)
        new_text = repair_text(text)
        after = new_text.count(REP)
        removed = before - after
        if removed <= 0:
            continue
        changed_files += 1
        total_removed += removed
        if not args.dry_run:
            fp.write_text(new_text, encoding="utf-8", newline="\n")
        print(f"[OK] {fp.name} removed={removed} remaining={after}")

    print(f"ChangedFiles={changed_files} RemovedTotal={total_removed} DryRun={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

