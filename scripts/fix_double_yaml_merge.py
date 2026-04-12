#!/usr/bin/env python3
"""修复双 YAML frontmatter：合并两个 frontmatter 块为一个

问题根因：backfill_metadata_fields.py 为已有 frontmatter 的文件
又添加了一个新的 frontmatter 块，导致真正的双 YAML。

修复策略：
  - 新 frontmatter（backfill 生成的）作为基础，包含标准化的
    module_id / layer / version / status / responsibility
  - 原 frontmatter 中的额外字段（created_date, owner, standard_type 等）
    合并进来（不覆盖新 frontmatter 已有的字段）
  - 删除第二个 frontmatter 块，保留正文内容不变
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

# ── Windows 控制台 UTF-8 ──────────────────────────────────────
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

# 匹配文件开头的 frontmatter 块
FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    """简易 YAML 解析（仅支持单层键值对 + 简单列表）"""
    result: dict[str, str] = {}
    current_key = None
    current_list: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 列表项
        if stripped.startswith("- ") and current_key is not None:
            current_list.append(stripped[2:].strip())
            continue

        # 保存上一个 key 的列表
        if current_key is not None and current_list:
            result[current_key] = current_list
            current_list = []
            current_key = None

        # 键值对
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)", stripped)
        if m:
            # 保存上一个 key
            if current_key is not None:
                if current_key not in result:
                    result[current_key] = ""
                current_key = None

            key, value = m.group(1), m.group(2).strip()
            if value:
                # 去掉引号
                if (value.startswith("'") and value.endswith("'")) or \
                   (value.startswith('"') and value.endswith('"')):
                    value = value[1:-1]
                result[key] = value
            else:
                current_key = key
                current_list = []

    # 保存最后一个列表
    if current_key is not None and current_list:
        result[current_key] = current_list

    return result


def format_frontmatter(fm: dict) -> str:
    """将 dict 格式化为 YAML frontmatter 文本"""
    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            # 如果值包含特殊字符，加引号
            if value and (":" in value or "#" in value or value.startswith("'") or value.startswith('"')):
                if not (value.startswith("'") or value.startswith('"')):
                    value = f"'{value}'"
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def fix_file(file_path: Path) -> bool:
    """修复单个文件的双 YAML frontmatter，返回是否修改"""
    try:
        raw = file_path.read_bytes()
    except OSError:
        return False

    # 处理 BOM
    has_bom = raw[:3] == b"\xef\xbb\xbf"
    text = raw.decode("utf-8-sig")

    # 匹配第一个 frontmatter
    first_fm = FM_PATTERN.match(text)
    if not first_fm:
        return False

    # 在第一个 frontmatter 之后，检查是否有第二个
    after_first = text[first_fm.end():]
    after_first_stripped = after_first.lstrip("\n")

    second_fm = FM_PATTERN.match(after_first_stripped)
    if not second_fm:
        return False

    # 验证第二个块包含 YAML 键值对
    second_yaml_str = second_fm.group(1).strip()
    if not second_yaml_str:
        return False

    yaml_kv_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\s*:", re.MULTILINE)
    if not yaml_kv_pattern.search(second_yaml_str):
        return False

    # 解析两个 frontmatter
    new_fm = parse_frontmatter(first_fm.group(1))  # backfill 生成的新 frontmatter
    old_fm = parse_frontmatter(second_yaml_str)     # 原有的 frontmatter

    # 合并策略：新 frontmatter 为基础，补充旧 frontmatter 中的额外字段
    merged = dict(new_fm)  # 以新 frontmatter 为基础
    for key, value in old_fm.items():
        if key not in merged:
            merged[key] = value

    # 正文内容 = 第二个 frontmatter 之后的所有内容
    body = after_first_stripped[second_fm.end():]
    # 确保正文前有一个空行
    if body and not body.startswith("\n"):
        body = "\n" + body

    # 组装新文件
    new_content = format_frontmatter(merged) + body

    # 写入（保持 BOM）
    out_bytes = new_content.encode("utf-8")
    if has_bom:
        out_bytes = b"\xef\xbb\xbf" + out_bytes

    file_path.write_bytes(out_bytes)
    return True


def main():
    fixed = 0
    errors = 0

    md_files = sorted(DOCS_ROOT.rglob("*.md"))
    print(f"扫描 {len(md_files)} 个 .md 文件...")

    for f in md_files:
        try:
            if fix_file(f):
                fixed += 1
                rel = f.relative_to(DOCS_ROOT.parent)
                print(f"  ✅ 合并: {rel}")
        except Exception as e:
            errors += 1
            print(f"  ❌ 错误: {f.relative_to(DOCS_ROOT.parent)}: {e}")

    print(f"\n完成: 修复 {fixed} 个文件, 错误 {errors} 个")


if __name__ == "__main__":
    main()
