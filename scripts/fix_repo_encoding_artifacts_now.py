#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
立刻修复仓库内的编码伪影（高确定性）：

- 将若干“非 UTF-8”临时文件（strict decode failures）统一转为 utf-8-sig
  - 仅按 BOM/常见编码尝试解码，不做内容级猜测
- 对指定 JSON 审计产物移除 C1 控制字符（U+0080..U+009F）与 U+FFFD（\\ufffd）
  - 这些字符对 JSON 语义通常无益，且会污染后续扫描

注意：
- 这不是“汉字? 断裂补全”，只处理可确定的编码控制字符/替换字符与统一编码。
"""

from __future__ import annotations

from pathlib import Path


REPO = Path(".")


STRICT_DECODE_FAILURES = [
    Path("audit_layer11_report.txt"),
    Path("temp_alternative.md"),
    Path("temp_alternative_data.md"),
    Path("temp_analysis.md"),
    Path("temp_gap.md"),
    Path("temp_head_blueprint.md"),
    Path("temp_open_source.md"),
    Path("temp_opensource.md"),
    Path("temp_stress_test_spec.md"),
]


AUDIT_STATE_JSONS = [
    Path("docs/09_AUDIT/STATE/layer4_deep_audit_20260407_030741.json"),
    Path("docs/09_AUDIT/STATE/layer4_deep_audit_v2_20260407_031623.json"),
    Path("docs/09_AUDIT/STATE/layer4_deep_audit_v3_20260407_113301.json"),
]


def decode_best_effort(b: bytes) -> str:
    # BOM 优先
    if b.startswith(b"\xff\xfe") or b.startswith(b"\xfe\xff"):
        try:
            return b.decode("utf-16")
        except UnicodeDecodeError:
            pass
    if b.startswith(b"\xef\xbb\xbf"):
        return b.decode("utf-8-sig", errors="strict")
    # 常见候选
    for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk", "cp1252", "latin-1"):
        try:
            return b.decode(enc, errors="strict")
        except UnicodeDecodeError:
            continue
    # 最后兜底（不应走到）
    return b.decode("latin-1", errors="replace")


def strip_c1_and_fffd(text: str) -> tuple[str, int, int]:
    before_fffd = text.count("\ufffd")
    before_c1 = sum(1 for ch in text if 0x80 <= ord(ch) <= 0x9F)
    if before_fffd == 0 and before_c1 == 0:
        return text, 0, 0
    out = "".join(ch for ch in text if not (0x80 <= ord(ch) <= 0x9F))
    out = out.replace("\ufffd", "")
    removed_fffd = before_fffd
    removed_c1 = before_c1
    return out, removed_fffd, removed_c1


def convert_to_utf8sig(fp: Path) -> bool:
    if not fp.exists() or not fp.is_file():
        return False
    b = fp.read_bytes()
    text = decode_best_effort(b)
    out = text.replace("\r\n", "\n").replace("\r", "\n")
    if not out.endswith("\n"):
        out += "\n"
    new_b = out.encode("utf-8-sig")
    if new_b == b:
        return False
    fp.write_bytes(new_b)
    return True


def sanitize_json(fp: Path) -> tuple[bool, int, int]:
    if not fp.exists() or not fp.is_file():
        return False, 0, 0
    text = fp.read_text(encoding="utf-8", errors="replace")
    fixed, r_fffd, r_c1 = strip_c1_and_fffd(text)
    if fixed == text:
        return False, 0, 0
    fp.write_text(fixed, encoding="utf-8", newline="\n")
    return True, r_fffd, r_c1


def main() -> int:
    changed = 0

    # 1) 统一临时文件编码
    conv = 0
    for fp in STRICT_DECODE_FAILURES:
        if convert_to_utf8sig(fp):
            conv += 1
    if conv:
        print("ConvertedToUtf8Sig=", conv)
        changed += conv

    # 2) 清理审计 JSON 控制字符/替换字符
    json_changed = 0
    total_fffd = 0
    total_c1 = 0
    for fp in AUDIT_STATE_JSONS:
        ok, r_fffd, r_c1 = sanitize_json(fp)
        if ok:
            json_changed += 1
            total_fffd += r_fffd
            total_c1 += r_c1
    if json_changed:
        print("SanitizedJsonFiles=", json_changed, "RemovedFFFD=", total_fffd, "RemovedC1=", total_c1)
        changed += json_changed

    print("ChangedFiles=", changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

