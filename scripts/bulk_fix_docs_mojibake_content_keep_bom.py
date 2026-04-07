#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
在保持 UTF-8 with BOM（utf-8-sig）不变的前提下，批量修复 docs/ 下 Markdown 内容中的 mojibake。

适用场景：
- 文件编码已经是 UTF-8/UTF-8-SIG，但正文出现 `é¦–å¸­...`、`ä¸€...`、`âœ...`、`æ...` 等乱码
  （通常是“UTF-8 字节被当成 latin-1/cp1252 文本写入”的结果）。

策略（逐行保守修复）：
- 对每一行，如果：
  - 含明显 mojibake token（Ã/Â/â/å/ä/é/è/ç/æ），或含控制字符 U+0080..U+009F
  - 且该行可被视为 0..255 的“字节文本”（即每个字符 ord<=255）
  则尝试 bytes(line) -> utf-8 解码（等价于 latin1->utf8 反转）。
- 仅当“中文增加 / mojibake token 减少 / 控制字符减少”时才接受替换。
"""

from __future__ import annotations

import argparse
import pathlib
import re


MOJI_RE = re.compile(r"(?:Ã.|Â.|â.|å.|ä.|é.|è.|ç.|æ.)")
CTRL_RE = re.compile(r"[\u0080-\u009f]")


def cjk_count(s: str) -> int:
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def moji_count(s: str) -> int:
    return len(MOJI_RE.findall(s))


def ctrl_count(s: str) -> int:
    return len(CTRL_RE.findall(s))


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


def should_attempt(line: str) -> bool:
    return moji_count(line) >= 2 or ctrl_count(line) >= 1


def accept(before: str, after: str) -> bool:
    # 必须有改善：中文增多或 mojibake/控制字符减少
    b_cjk, a_cjk = cjk_count(before), cjk_count(after)
    b_moji, a_moji = moji_count(before), moji_count(after)
    b_ctl, a_ctl = ctrl_count(before), ctrl_count(after)

    improved = False
    if a_cjk > b_cjk:
        improved = True
    if a_moji < b_moji:
        improved = True
    if a_ctl < b_ctl:
        improved = True

    # 防守：不允许替换后出现 U+FFFD
    if "\ufffd" in after:
        return False

    return improved


def fix_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=False)
    out: list[str] = []
    changed = 0

    for line in lines:
        if not should_attempt(line):
            out.append(line)
            continue

        # Path A: classic bytes-like mojibake (all chars <=255)
        cand = reverse_bytes_to_utf8(line)
        if cand is not None and accept(line, cand):
            out.append(cand)
            changed += 1
            continue

        # Path B: mojibake already stored as Unicode text (e.g. "è´è´£")
        # This can often be reversed by latin1->utf8 on the UTF-8 bytes of the string.
        try:
            b = line.encode("utf-8")
            cand2 = b.decode("latin-1")
            cand3 = reverse_bytes_to_utf8(cand2)
        except Exception:
            cand3 = None

        if cand3 is not None and accept(line, cand3):
            out.append(cand3)
            changed += 1
            continue

        out.append(line)

    fixed = "\n".join(out)
    if text.endswith("\n"):
        fixed += "\n"
    return fixed, changed


def iter_md_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(root.rglob("*.md"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="process only a single relative path under root")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    files = [root / args.only] if args.only else iter_md_files(root)

    changed_files = 0
    total_lines = 0

    for fp in files:
        if not fp.exists():
            continue
        b = fp.read_bytes()
        # 保持 BOM：用 utf-8-sig 读写
        text = b.decode("utf-8-sig", errors="strict")
        fixed, changed = fix_text(text)
        if changed <= 0:
            continue
        changed_files += 1
        total_lines += changed
        if not args.dry_run:
            fp.write_bytes(fixed.encode("utf-8-sig"))
        print(f"[OK] {fp.as_posix()} changed_lines={changed}")

    print("ChangedFiles=", changed_files, "TotalChangedLines=", total_lines, "DryRun=", args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

