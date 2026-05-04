"""
frontmatter.py — 统一 frontmatter 解析

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
6+ 个脚本各自复制了 parse_frontmatter()，统一到此模块。

提供两种解析方式：
- parse_frontmatter(): Markdown 文件的 YAML frontmatter（--- ... ---）
- parse_yaml_header(): YAML 文件的注释头 + 顶层字段提取
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

def parse_frontmatter(content: str) -> dict | None:
    """从 Markdown 文本中解析 YAML frontmatter。

    Args:
        content: 文件全文内容。

    Returns:
        解析后的字典，无 frontmatter 或解析失败时返回 None。
    """
    if not content.startswith("---"):
        return None
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    try:
        result = yaml.safe_load(match.group(1))
        return result if isinstance(result, dict) else None
    except yaml.YAMLError:
        return None

def parse_frontmatter_from_file(filepath: Path) -> dict | None:
    """从文件路径读取并解析 YAML frontmatter。

    Args:
        filepath: 文件路径。

    Returns:
        解析后的字典，文件不存在或无 frontmatter 时返回 None。
    """
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None
    return parse_frontmatter(content)

def parse_frontmatter_raw_from_file(filepath: Path) -> tuple[dict | None, str | None]:
    """从文件路径读取并解析 YAML frontmatter，同时返回原始全文。

    用于 --fix 模式等需要原始内容的场景。

    Args:
        filepath: 文件路径。

    Returns:
        (解析后的字典, 文件全文内容)，失败时返回 (None, None)。
    """
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None, None
    fm = parse_frontmatter(content)
    return fm, content

def parse_yaml_header(content: str) -> dict | None:
    """从 YAML 文件内容中提取头部字段（注释行 + 顶层字段）。

    优先从注释行提取，再从 YAML 正文补充缺失字段。
    schema_version 自动映射为 version（对标 AGENTS.md §6.6.3）。

    Args:
        content: YAML 文件全文内容。

    Returns:
        提取的字段字典，无有效内容时返回 None。
    """
    fields: dict = {}
    for line in content.split("\n"):
        if not line.startswith("#") and line.strip() != "":
            break
        if line.startswith("#"):
            m = re.match(r"#\s*(\w+)[：:]\s*(.+)", line)
            if m:
                fields[m.group(1)] = m.group(2).strip()

    try:
        full_yaml = yaml.safe_load(content)
    except yaml.YAMLError:
        return fields if fields else None

    if isinstance(full_yaml, dict):
        for k in (
            "module_id",
            "doc_type",
            "status",
            "version",
            "title",
            "rule_form",
            "scope",
            "stability",
            "layer",
            "owner",
            "ttl",
            "superseded_by",
            "classification",
            "language",
            "created_by",
            "date",
            "summary",
            "tags",
            "verifiability",
            "generated_at",
        ):
            if k in full_yaml and k not in fields:
                fields[k] = full_yaml[k]
        if "schema_version" in full_yaml and "version" not in fields:
            fields["version"] = str(full_yaml["schema_version"])

    return fields if fields else None
