#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
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
    # 更高频的蓝图/规范类断裂（优先放前面）
    (re.compile(rf"蓝\?{SEP}"), "蓝图"),
    (re.compile(rf"概\?{SEP}"), "概述"),
    (re.compile(rf"策\?{SEP}"), "策略"),
    (re.compile(rf"优\?{SEP}"), "优化"),
    (re.compile(rf"测\?{SEP}"), "测试"),
    (re.compile(rf"迭\?{SEP}"), "迭代"),
    (re.compile(rf"流\?{SEP}"), "流程"),
    (re.compile(rf"路\?{SEP}"), "路径"),
    (re.compile(rf"径\?{SEP}"), "路径"),
    (re.compile(rf"盘\?{SEP}"), "盘"),
    (re.compile(rf"档\?{SEP}"), "文档"),
    (re.compile(rf"实\?{SEP}"), "实现"),
    (re.compile(rf"数\?{SEP}"), "数据"),
    (re.compile(rf"图\?{SEP}"), "图表"),
    # 更具体的高置信度短语（放在通用规则之前）
    (re.compile(rf"数据引\?{SEP}"), "数据引擎"),
    (re.compile(rf"数据湖架\?{SEP}"), "数据湖架构"),
    (re.compile(rf"技术架\?{SEP}"), "技术架构"),
    (re.compile(rf"系统架\?{SEP}"), "系统架构"),
    (re.compile(rf"值\?{SEP}"), "值"),
    (re.compile(rf"度\?{SEP}"), "度"),

    # 业务/文档常见高频断裂（相对高置信度）
    (re.compile(rf"能\?{SEP}"), "能力"),
    (re.compile(rf"类\?{SEP}"), "类别"),
    (re.compile(rf"体\?{SEP}"), "体系"),
    (re.compile(rf"价\?{SEP}"), "价值"),
    (re.compile(rf"完\?{SEP}"), "完整"),
    (re.compile(rf"缺\?{SEP}"), "缺失"),
    (re.compile(rf"稳\?{SEP}"), "稳定"),
    (re.compile(rf"运\?{SEP}"), "运行"),
    (re.compile(rf"权\?{SEP}"), "权限"),
    (re.compile(rf"审\?{SEP}"), "审计"),
    (re.compile(rf"协\?{SEP}"), "协作"),
    # 短语级兜底
    (re.compile(rf"合规审\?{SEP}"), "合规审计"),

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
    # 注意：单字“档?”在语料里既可能是“文档”，也可能是“档案”。
    # 前面已优先将其映射为“文档”，这里不再重复二次映射，避免同一行被来回替换。
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

