#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-

"""
移除 Markdown 文本中的 C1 控制字符（U+0080..U+009F）。

这些字符通常来源于历史编码损坏（例如某些 “mojibake” 片段里混入的控制字节），会导致显示异常/不可搜索。
本脚本只做删除，不做语义猜测。
"""

from __future__ import annotations

import argparse
import pathlib
import re


C1_RE = re.compile(r"[\u0080-\u009f]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--encoding", default="utf-8-sig", help="keep BOM by default")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    fp = pathlib.Path(args.file)
    text = fp.read_text(encoding=args.encoding, errors="strict")
    before = len(C1_RE.findall(text))
    if before == 0:
        print("Removed=0")
        return 0
    fixed = C1_RE.sub("", text)
    after = len(C1_RE.findall(fixed))
    if not args.dry_run:
        fp.write_text(fixed, encoding=args.encoding, newline="\n")
    print(f"Removed={before-after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

