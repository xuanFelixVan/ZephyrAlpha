#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
按“文档治理”口径做结构性修复（保守）：
- 仅修复 docs/ 下 Markdown 的结构破坏：未闭合的 fenced code block、mermaid 前缀残片等
- 默认跳过归档/审计产物（避免篡改历史证据类文档）：
  - docs/06_ARCHIVE/**
  - docs/**/audit_state/**

注意：
- `汉字?` 属于内容断裂，不在本脚本范围（应输出待补全清单）。
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("docs")
STATE = ROOT / "09_AUDIT" / "STATE"
INPUT_JSON = STATE / "encoding_artifact_after_bulk.json"


def should_skip(p: str) -> bool:
    return (
        p.startswith("docs/06_ARCHIVE/")
        or "/audit_state/" in p.replace("\\", "/")
        or p.endswith(".bak.md")
    )


def fix_mermaid_yen_artifacts(text: str) -> str:
    # 仅处理 fenced mermaid 区块开头紧邻的残片（历史 `¥"` 这类），避免误伤正常金额符号
    lines = text.split("\n")
    out: list[str] = []
    in_mermaid = False
    for line in lines:
        if line.strip().startswith("```mermaid"):
            in_mermaid = True
            out.append(line)
            continue
        if in_mermaid and line.strip() == "```":
            in_mermaid = False
            out.append(line)
            continue
        if in_mermaid:
            s = line.strip()
            if s in {"¥", "¥\"", "¥?", "¥?\"", "¥\"\"\""}:
                continue
            if s.startswith("¥\""):
                out.append(line.replace("¥\"", "", 1))
                continue
            if s.startswith("¥"):
                out.append(line.replace("¥", "", 1))
                continue
        out.append(line)
    return "\n".join(out)


def close_unbalanced_fences(text: str) -> str:
    # 如果 fenced 数量为奇数，追加一个收尾 fence。
    # 这是结构层修复：用于避免渲染/解析被“吞掉”后续内容。
    if text.count("```") % 2 == 1:
        if not text.endswith("\n"):
            text += "\n"
        text += "```\n"
    return text


def main() -> int:
    if not INPUT_JSON.exists():
        raise SystemExit(f"[ERR] missing baseline: {INPUT_JSON.as_posix()}")

    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    issues = data.get("issues", [])

    targets: list[Path] = []
    for it in issues:
        if not it.get("strict", True):
            continue
        if it.get("odd_fences", 0) != 1:
            continue
        f = it.get("file")
        if not isinstance(f, str):
            continue
        f = f.replace("\\", "/")
        if should_skip(f):
            continue
        targets.append(Path(f))

    changed = 0
    for fp in targets:
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
        orig = text
        text = fix_mermaid_yen_artifacts(text)
        text = close_unbalanced_fences(text)
        if text != orig:
            fp.write_bytes(text.encode("utf-8-sig"))
            changed += 1

    print("FixedOddFenceFiles=", changed, "Targets=", len(targets))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

