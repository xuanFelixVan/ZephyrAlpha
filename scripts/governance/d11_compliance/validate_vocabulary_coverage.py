# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_vocabulary_coverage.py | §
# [MODULE] scripts.governance.d11_compliance.validate_vocabulary_coverage
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

#!/usr/bin/env python3
"""验证 frontmatter_schema.json 中的枚举字段是否在 vocabularies/ 目录有对应词汇表。

扫描 frontmatter_schema.json 中的所有 oneOf+const 模式枚举字段，
检查每个枚举字段是否在 vocabularies/ 目录存在对应的 *-vocabulary.yaml 文件。

CLI::

    python validate_vocabulary_coverage.py [--schema PATH] [--vocab-dir PATH]

Exit codes:
    0 — 全部枚举字段都有对应词汇表
    1 — 存在缺失词汇表（打印缺失列表）
"""

# Governance script manifest


import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path


def extract_enum_fields(schema_path: Path) -> dict[str, list[str]]:
    """从 JSON Schema 中提取所有 oneOf+const 模式的枚举字段。"""
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    enums: dict[str, list[str]] = {}
    properties = schema.get("properties", {})

    for field_name, field_def in properties.items():
        values = _extract_const_values(field_def)
        if values:
            enums[field_name] = values

    # 递归检查嵌套对象（如 provenance.audit_chain.verdict）
    def _walk(obj: dict, prefix: str = "") -> None:
        """_walk implementation."""
        if not isinstance(obj, dict):
            return
        props = obj.get("properties") or obj.get("items", {}).get("properties", {})
        for k, v in props.items():
            full_key = f"{prefix}.{k}" if prefix else k
            vals = _extract_const_values(v)
            if vals:
                enums[full_key] = vals
            _walk(v, full_key)

    for field_name, field_def in properties.items():
        _walk(field_def, field_name)

    return enums


def _extract_const_values(field_def: dict) -> list[str] | None:
    """提取 oneOf/anyOf + const 模式中的枚举值。"""
    if not isinstance(field_def, dict):
        return None

    for key in ("oneOf", "anyOf"):
        variants = field_def.get(key)
        if not variants:
            continue
        values = []
        for variant in variants:
            if isinstance(variant, dict) and "const" in variant:
                values.append(variant["const"])
        if values:
            return values

    # 检查 items.oneOf（数组元素的枚举）
    items = field_def.get("items")
    if isinstance(items, dict):
        return _extract_const_values(items)

    return None


def find_vocabularies(vocab_dir: Path) -> set[str]:
    """扫描 vocabularies/ 目录，返回已存在的词汇表字段名集合。

    返回的字段名使用连字符形式（如 ai-autonomy、blueprint-refs-status），
    与 schema 字段名（下划线/点号形式）通过统一替换规则匹配。
    """


__manifest__ = """
args: []
description: >
  验证 frontmatter_schema.json 枚举字段与 vocabularies/ 目录的覆盖度。
  确保每个枚举字段都有独立词汇表文件（SSoT 原则）。
dimensions:
  - D11
priority: P2
timeout_seconds: 30
warn_only: false
"""
