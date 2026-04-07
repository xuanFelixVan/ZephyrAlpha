#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量修复 docs/ 下 Markdown 编码，统一保存为 UTF-8 with BOM（utf-8-sig）。

特点：
- 智能尝试解码：utf-8 / utf-8-sig / gb18030 / gbk / cp1252 / latin-1
- 典型 mojibake 反转：对“é¦–å¸­...” 这类文本尝试 latin1->utf8 反转
- 控制字符修复：对混入 U+0080..U+009F 的行做按字节反转尝试
"""

from __future__ import annotations

import argparse
import pathlib
import re
from dataclasses import dataclass


MOJI_RE = re.compile(r"(?:Ã.|Â.|â.|å.|ä.|é.|è.|ç.|æ.)")
CTRL_RE = re.compile(r"[\u0080-\u009f]")


@dataclass(frozen=True)
class DecodeResult:
    encoding: str
    text: str


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def moji_count(s: str) -> int:
    return len(MOJI_RE.findall(s))


def has_ctrl(s: str) -> bool:
    return bool(CTRL_RE.search(s))


def reverse_latin1_utf8(s: str) -> str | None:
    # 若包含 >255 的字符，说明不是“字节当字符”的 mojibake
    if any(ord(ch) > 255 for ch in s):
        return None
    raw = bytes(ord(ch) for ch in s)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def linewise_fix_ctrl(text: str) -> str:
    out = []
    changed = False
    for line in text.splitlines(keepends=False):
        if has_ctrl(line) and cjk_count(line) == 0:
            cand = reverse_latin1_utf8(line)
            if cand is not None and (moji_count(cand) < moji_count(line) or cjk_count(cand) > 0):
                out.append(cand)
                changed = True
                continue
        out.append(line)
    fixed = "\n".join(out)
    if text.endswith("\n"):
        fixed += "\n"
    return fixed if changed else text


def decode_bytes(b: bytes) -> DecodeResult:
    # 1) UTF-8 strict
    try:
        return DecodeResult("utf-8", b.decode("utf-8"))
    except UnicodeDecodeError:
        pass

    # 2) UTF-8 with BOM
    try:
        return DecodeResult("utf-8-sig", b.decode("utf-8-sig"))
    except UnicodeDecodeError:
        pass

    # 3) GB18030 (superset of GBK/GB2312)
    for enc in ("gb18030", "gbk"):
        try:
            return DecodeResult(enc, b.decode(enc))
        except UnicodeDecodeError:
            continue

    # 4) cp1252 then latin-1 (always decodes)
    try:
        return DecodeResult("cp1252", b.decode("cp1252"))
    except UnicodeDecodeError:
        return DecodeResult("latin-1", b.decode("latin-1"))


def normalize_text(text: str) -> str:
    # 典型 mojibake：moji 多 + 中文少
    if moji_count(text) >= 50 and cjk_count(text) < 200:
        cand = reverse_latin1_utf8(text)
        if cand is not None and cjk_count(cand) > cjk_count(text):
            text = cand

    # 行级控制字符修复（针对混入控制字符的一类）
    text = linewise_fix_ctrl(text)
    return text


def iter_md_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(root.rglob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs", help="root directory to scan")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="process only a single relative path under root")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    if args.only:
        files = [root / args.only]
    else:
        files = iter_md_files(root)

    changed = 0
    for fp in files:
        if not fp.exists():
            continue
        b = fp.read_bytes()
        dec = decode_bytes(b)
        text = normalize_text(dec.text)

        out = text.encode("utf-8-sig")  # UTF-8 with BOM
        if out != b:
            changed += 1
            if not args.dry_run:
                fp.write_bytes(out)
            print(f"[OK] {fp.as_posix()} ({dec.encoding} -> utf-8-sig)")

    print("ChangedFiles=", changed, "DryRun=", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

