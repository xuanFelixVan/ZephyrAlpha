#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
治理式修复：将文档中“汉字 + ?”的高置信度断裂做保守回填。

策略（保守，避免误伤）：
- 仅在“非 fenced code block”内处理
- 尽量不修改包含链接的行（含 http/]( /](# 等）
- 采用有限的常见断裂词尾规则（如 设?→设计、功?→功能、模?→模块、报?→报告、系?→系统、监?→监控、约?→约束…）
- 仅当 `?` 位于中文之后，且后面是分隔符/行尾时替换（避免改动数学/代码/路径）

输出：
- 修复文件数、修复次数
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path("docs")


def in_governed_scope(p: str) -> bool:
    p = p.replace("\\", "/")
    return not (p.startswith("docs/06_ARCHIVE/") or "/audit_state/" in p)


FENCE_RE = re.compile(r"^```")
LINKY_RE = re.compile(r"(https?://|\]\(|\]\(#)")

# 仅在 “中文 + ? + 分隔符/行尾” 生效
SEP = r"(?=$|[\s，。；：:、)\]】}＞>\"'`|])"

RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(rf"设\?{SEP}"), "设计"),
    (re.compile(rf"设\?\*{SEP}"), "设计"),
    (re.compile(rf"计\?{SEP}"), "计划"),
    (re.compile(rf"功\?{SEP}"), "功能"),
    (re.compile(rf"模\?{SEP}"), "模块"),
    (re.compile(rf"报\?{SEP}"), "报告"),
    (re.compile(rf"监\?{SEP}"), "监控"),
    (re.compile(rf"约\?{SEP}"), "约束"),
    (re.compile(rf"验\?{SEP}"), "验证"),
    (re.compile(rf"检\?{SEP}"), "检查"),
    (re.compile(rf"更\?{SEP}"), "更新"),
    (re.compile(rf"状\?{SEP}"), "状态"),
    (re.compile(rf"范\?{SEP}"), "范围"),
    (re.compile(rf"清\?{SEP}"), "清单"),
    (re.compile(rf"规\?{SEP}"), "规范"),
    (re.compile(rf"对\?{SEP}"), "对接"),
    (re.compile(rf"集\?{SEP}"), "集成"),
    (re.compile(rf"解\?{SEP}"), "解释"),
    (re.compile(rf"结\?{SEP}"), "结束"),
    (re.compile(rf"周\?{SEP}"), "周期"),
    (re.compile(rf"开\?{SEP}"), "开发"),
    (re.compile(rf"缓\?{SEP}"), "缓存"),
    (re.compile(rf"图\?{SEP}"), "图表"),
    (re.compile(rf"节\?{SEP}"), "节奏"),
    (re.compile(rf"库\?{SEP}"), "库"),
    (re.compile(rf"顶\?{SEP}"), "顶层"),
    (re.compile(rf"档\?{SEP}"), "档案"),
    (re.compile(rf"迁\?{SEP}"), "迁移"),
    # 常见“系统/接口/指标/流程”类断裂（单字系?易误伤，放最后且仅在“中文+系?”）
    (re.compile(rf"系\?{SEP}"), "系统"),
    (re.compile(rf"接\?{SEP}"), "接口"),
    (re.compile(rf"标\?{SEP}"), "指标"),
    (re.compile(rf"程\?{SEP}"), "流程"),
]


def fix_line(line: str) -> tuple[str, int]:
    if "?" not in line:
        return line, 0
    if LINKY_RE.search(line):
        return line, 0
    # 仅在中文前缀下考虑（减少误伤英文问号）
    if not re.search(r"[\u4e00-\u9fff]\?", line):
        return line, 0
    n = 0
    out = line
    for pat, rep in RULES:
        out2, k = pat.subn(rep, out)
        if k:
            n += k
            out = out2
    return out, n


def process_file(fp: Path) -> tuple[bool, int]:
    text = fp.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    orig = text
    in_fence = False
    total = 0
    out_lines: list[str] = []
    for line in text.split("\n"):
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        fixed, n = fix_line(line)
        total += n
        out_lines.append(fixed)
    out = "\n".join(out_lines)
    if not out.endswith("\n"):
        out += "\n"
    changed = (out != orig)
    if changed:
        fp.write_bytes(out.encode("utf-8-sig"))
    return changed, total


def main() -> int:
    changed_files = 0
    changed_hits = 0
    for fp in ROOT.rglob("*.md"):
        s = fp.as_posix()
        if not in_governed_scope(s):
            continue
        changed, hits = process_file(fp)
        if changed:
            changed_files += 1
            changed_hits += hits
    print("ChangedFiles=", changed_files, "RepairedTokens=", changed_hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

