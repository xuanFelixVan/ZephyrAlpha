#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终收尾清理：消灭 docs/ Markdown 中的编码伪影

目标（面向“中文乱码”体验）：
- 移除所有 U+FFFD（�）替换字符（这些字符代表已不可逆丢失的字节）
- 尽可能反转 mojibake 文本回中文（latin1->utf8）

注意：
- 对于 U+FFFD：无法无损恢复，只能删除或替换占位。本脚本选择“删除”，以避免显示为乱码。
- 对 mojibake：仅在“中文显著增加且不引入 U+FFFD”时替换。
"""

from __future__ import annotations

import argparse
import pathlib
import re


REP = "\ufffd"
MOJI_RE = re.compile(r"(?:Ã.|Â.|â.|å.|ä.|é.|è.|ç.|æ.)")
HIGHBYTE_RE = re.compile(r"[\u00a0-\u00ff]")


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def moji_count(s: str) -> int:
    return len(MOJI_RE.findall(s))


def can_be_bytes(s: str) -> bool:
    return all(ord(ch) <= 255 for ch in s)


def reverse_bytes_to_utf8(s: str) -> str | None:
    if not can_be_bytes(s):
        return None
    raw = bytes(ord(ch) for ch in s)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def reverse_utf8_latin1_roundtrip(s: str) -> str | None:
    """
    处理“Unicode 形态的 mojibake”（如 è´è´£）：
    - 将字符串按 UTF-8 编码得到字节
    - 将这些字节按 latin-1 解码成 0..255 的“字节文本”
    - 再做 bytes->utf8 反转
    """
    b = s.encode("utf-8")
    as_latin1 = b.decode("latin-1")
    return reverse_bytes_to_utf8(as_latin1)


def accept(before: str, after: str) -> bool:
    if after is None:
        return False
    if REP in after:
        return False
    return cjk_count(after) > cjk_count(before)


def fix_line(line: str) -> str:
    if not (MOJI_RE.search(line) or HIGHBYTE_RE.search(line)):
        return line

    # Path A: direct bytes-like reverse
    cand = reverse_bytes_to_utf8(line)
    if cand and accept(line, cand):
        return cand

    # Path B: unicode-mojibake roundtrip
    cand2 = reverse_utf8_latin1_roundtrip(line)
    if cand2 and accept(line, cand2):
        return cand2

    return line


def fix_text(text: str) -> tuple[str, int, int]:
    before_rep = text.count(REP)
    # 先逐行修 mojibake（避免先删 REP 影响判定）
    lines = text.splitlines(keepends=False)
    out = [fix_line(line) for line in lines]
    fixed = "\n".join(out)
    if text.endswith("\n"):
        fixed += "\n"

    # 再移除 U+FFFD
    fixed = fixed.replace(REP, "")
    after_rep = fixed.count(REP)
    return fixed, before_rep, after_rep


def iter_md_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(root.rglob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    files = iter_md_files(root)

    changed_files = 0
    removed_rep_total = 0
    for fp in files:
        b = fp.read_bytes()
        text = b.decode("utf-8-sig", errors="replace")
        new_text, before_rep, after_rep = fix_text(text)
        if new_text != text:
            changed_files += 1
            removed_rep_total += (before_rep - after_rep)
            if not args.dry_run:
                fp.write_bytes(new_text.encode("utf-8-sig"))
    print("ChangedFiles=", changed_files, "RemovedU+FFFD=", removed_rep_total, "DryRun=", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

