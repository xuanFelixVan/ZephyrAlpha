#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
蓝图专用治理修复：在 01_BLUEPRINTS 中对“汉字 + ?”的常见结构性断裂做更强规则化回填。

约束：
- 跳过 fenced code block
- 跳过链接行（含 http/]( /](#）
- 仅在“中文 + ? + 分隔符/行尾”场景替换，避免误伤
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
STATE = Path("docs/09_AUDIT/STATE")

FENCE_RE = re.compile(r"^```")
LINKY_RE = re.compile(r"(https?://|\]\(|\]\(#)")
SEP = r"(?=$|[\s，。；：:、)\]】}＞>\"'`|])"


def compile_rules() -> list[tuple[re.Pattern[str], str]]:
    # 常见蓝图章节/表格/术语断裂
    pairs = [
        ("架构设?", "架构设计"),
        ("系统架构设?", "系统架构设计"),
        ("数据流设?", "数据流设计"),
        ("接口设?", "接口设计"),
        ("实现方案", "实现方案"),
        ("实施步?", "实施步骤"),
        ("关键技?", "关键技术"),
        ("设计目?", "设计目标"),
        ("质量目?", "质量目标"),
        ("功能清?", "功能清单"),
        ("功能特?", "功能特性"),
        ("核心组件架构", "核心组件架构"),
        ("架构概览?", "架构概览"),
        ("模块分层架构", "模块分层架构"),
        ("集成方?", "集成方案"),
        ("配置示?", "配置示例"),
        ("配置说明", "配置说明"),
        ("命令行接口示?", "命令行接口示例"),
        ("示?", "示例"),
        ("输出?", "输出"),
        ("输入?", "输入"),
        ("优化问?", "优化问题"),
        ("约束条件处?", "约束条件处理"),
        ("流动性约?", "流动性约束"),
        ("风险评估与应?", "风险评估与应对"),
        ("风险控制措?", "风险控制措施"),
        ("监控告?", "监控告警"),
        ("可视?", "可视化"),
        ("报?", "报告"),
        ("图?", "图表"),
        ("模?", "模块"),
        ("系?", "系统"),
        ("验?", "验证"),
        ("检?", "检查"),
        ("清?", "清单"),
        ("范?", "范围"),
        ("更?", "更新"),
        ("状?", "状态"),
    ]

    rules: list[tuple[re.Pattern[str], str]] = []
    for a, b in pairs:
        # 只对 a 中包含 '?' 的项做“中文? + 分隔符”限定；否则跳过
        if "?" in a:
            # 将 a 里的 ? 替换为字面问号匹配
            a_re = re.escape(a).replace("\\?", "\\?")
            rules.append((re.compile(a_re + SEP), b))
        else:
            # 允许少量无 ? 的修补（例如把破碎标题统一），这里不启用
            pass

    # 更通用但仍高置信度的模式（多用于标题/表格）
    rules.extend(
        [
            # 时?* / 扩?* / 维?* / 体?* 这类在蓝图里高度重复
            (re.compile(rf"时\?\*{SEP}"), "时间"),
            (re.compile(rf"扩\?\*{SEP}"), "扩展性"),
            (re.compile(rf"维\?\*{SEP}"), "维护性"),
            (re.compile(rf"体\?\*{SEP}"), "体系"),
            # 子系? / 介? / 方? 常见断裂
            (re.compile(rf"子系\?{SEP}"), "子系统"),
            (re.compile(rf"介\?{SEP}"), "接口"),
            (re.compile(rf"方\?{SEP}"), "方案"),
            # 标题末尾孤立问号：多为断裂残留，直接去掉
            (re.compile(r"(#+\\s*[^\\n\\r]*?)\\?\\s*$"), r"\\1"),
        ]
    )
    return rules


RULES = compile_rules()


def fix_line(line: str) -> tuple[str, int]:
    if "?" not in line:
        return line, 0
    if LINKY_RE.search(line):
        return line, 0
    if not re.search(r"[\u4e00-\u9fff]\?", line):
        return line, 0
    out = line
    n = 0
    for pat, rep in RULES:
        out2, k = pat.subn(rep, out)
        if k:
            out = out2
            n += k
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
    if out != orig:
        fp.write_bytes(out.encode("utf-8-sig"))
        return True, total
    return False, 0


def write_todo_snapshot() -> None:
    pat = re.compile(r"[\u4e00-\u9fff]\?")
    items = []
    for fp in sorted(ROOT.glob("*.md")):
        t = fp.read_text(encoding="utf-8-sig", errors="strict")
        hits = []
        for i, line in enumerate(t.splitlines(), 1):
            if pat.search(line):
                hits.append({"line": i, "text": line.strip()[:200]})
        if hits:
            items.append({"file": fp.as_posix(), "count": len(hits), "samples": hits[:10]})
    items.sort(key=lambda x: -x["count"])
    out = {"dir": ROOT.as_posix(), "total_files": len(items), "total_hits": sum(x["count"] for x in items), "items": items}
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "cjk_question_mark_todo_blueprints.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    changed_files = 0
    tokens = 0
    for fp in sorted(ROOT.glob("*.md")):
        changed, n = process_file(fp)
        if changed:
            changed_files += 1
            tokens += n
    write_todo_snapshot()
    print("ChangedFiles=", changed_files, "RepairedTokens=", tokens)
    print("WROTE", (STATE / "cjk_question_mark_todo_blueprints.json").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

