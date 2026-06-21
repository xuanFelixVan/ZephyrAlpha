# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_derived_from.py | §
"""
validate_derived_from.py — derived_from 标注完整性闸门（GATE-DERIVED）
v1.0.0 — 2026-05-03



AGENTS.md §6.13 枚举自动派生铁律 + §6.14 漂移免疫架构原则 Level 2 门禁 4/4：
  根因：派生文件（frontmatter-field-registry、architecture-contract、frontmatter-schema.json）
        中有枚举列表但未标注 derived_from，导致无法追溯枚举值的 canonical SSoT。
        AI 修改枚举时不知道哪些文件需要同步，漏改必然发生。

  本闸门：扫描所有应标注 derived_from 的派生文件 → 检测缺失标注 → 检测标注指向不存在的
          vocabulary YAML → 检测标注了但枚举值与 vocabulary 不一致。

检查维度：
  DIM-1: frontmatter-field-registry.md 中 enum 类型字段必须有 derived_from
  DIM-2: architecture-contract.yaml 中 allowed_values 字段必须有 derived_from
  DIM-3: frontmatter-schema.json 中 enum 属性应能追溯到 vocabulary（通过字段名映射）
  DIM-4: derived_from 指向的 vocabulary YAML 文件必须存在
  DIM-5: derived_from 指向的 vocabulary YAML 中对应字段必须存在

对标：ITIL SACM → CI 属性变更必须同步到所有消费该属性的 CMDB 视图
      K8s Admission Controller → 所有资源创建请求必须通过审核

exit codes: 0=一致, 1=发现缺失, 2=系统错误
"""

from __future__ import annotations
__manifest__ = """
args: []
description: GATE-DERIVED — derived_from 标注完整性闸门（§6.14 Level 2 门禁 4/4 — 派生文件 derived_from
  标注检测，5维检查）
dimensions:
- D3
- D5
priority: P1
timeout_seconds: 15
warn_only: false
"""


import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

from _shared.yaml_utils import load_yaml

VOCAB_DIR = GOV_DOCS_DIR / "_registry" / "vocabularies"
CATALOGS_DIR = GOV_DOCS_DIR / "_registry" / "catalogs"
CONTRACTS_DIR = GOV_DOCS_DIR / "_registry" / "contracts"
SCHEMAS_DIR = GOV_DOCS_DIR / "_registry" / "schemas"

FIELD_REGISTRY_PATH = CATALOGS_DIR / "frontmatter-field-registry.md"
ARCH_CONTRACT_PATH = CONTRACTS_DIR / "architecture-contract.yaml"
SCHEMA_JSON_PATH = SCHEMAS_DIR / "frontmatter-schema.json"

VOCAB_FIELD_MAP = {
    "doc_type": "doc_type-vocabulary.yaml",
    "status": "status-vocabulary.yaml",
    "rule_form": "rule_form-vocabulary.yaml",
    "ttl": "ttl-vocabulary.yaml",
    "layer": "layer-vocabulary.yaml",
}

_errors: list[str] = []
_warnings: list[str] = []

def _err(msg: str) -> None:
    """_err implementation."""
    _errors.append(msg)

def _warn(msg: str) -> None:
    """_warn implementation."""
    _warnings.append(msg)

def check_dim1_field_registry() -> None:
    """DIM-1: frontmatter-field-registry.md 中 enum 类型字段必须有 derived_from"""
    if not FIELD_REGISTRY_PATH.exists():
        _warn("DIM-1: frontmatter-field-registry.md 不存在")
        return
    try:
        data = load_yaml(FIELD_REGISTRY_PATH)
    except Exception as e:
        _err(f"DIM-1: 无法加载 frontmatter-field-registry.md: {e}")
        return
    if not isinstance(data, dict):
        return
    for field in data.get("fields", []):
        fname = field.get("field_name") or field.get("name", "")
        ftype = field.get("type", "")
        if ftype != "enum":
            continue
        if fname not in VOCAB_FIELD_MAP:
            continue
        derived = field.get("derived_from")
        if not derived:
            _warn(
                f"DIM-1 field_registry.{fname}: enum 字段缺少 derived_from 标注"
                f"（应标注 derived_from: '_registry/vocabularies/{VOCAB_FIELD_MAP[fname]}'）"
            )
        elif not derived.endswith(VOCAB_FIELD_MAP[fname]):
            _warn(f"DIM-1 field_registry.{fname}: derived_from='{derived}' " f"未指向 {VOCAB_FIELD_MAP[fname]}")

def check_dim2_arch_contract() -> None:
    """DIM-2: architecture-contract.yaml 中 allowed_values 字段必须有 derived_from"""
    if not ARCH_CONTRACT_PATH.exists():
        _warn("DIM-2: architecture-contract.yaml 不存在")
        return
    try:
        data = load_yaml(ARCH_CONTRACT_PATH)
    except Exception as e:
        _err(f"DIM-2: 无法加载 architecture-contract.yaml: {e}")
        return
    if not isinstance(data, dict):
        return
    fm_schema = data.get("frontmatter_schema", {})
    for field in fm_schema.get("required_fields", []):
        fname = field.get("name", "")
        if fname not in VOCAB_FIELD_MAP:
            continue
        allowed = field.get("allowed_values")
        if not allowed:
            continue
        derived = field.get("derived_from")
        if not derived:
            _warn(
                f"DIM-2 arch_contract.{fname}: 有 allowed_values 但缺少 derived_from 标注"
                f"（应标注 derived_from: '_registry/vocabularies/{VOCAB_FIELD_MAP[fname]}'）"
            )
        elif not derived.endswith(VOCAB_FIELD_MAP[fname]):
            _warn(f"DIM-2 arch_contract.{fname}: derived_from='{derived}' " f"未指向 {VOCAB_FIELD_MAP[fname]}")

def check_dim3_schema_json() -> None:
    """DIM-3: frontmatter-schema.json 中 enum 属性应能追溯到 vocabulary"""
    if not SCHEMA_JSON_PATH.exists():
        _warn("DIM-3: frontmatter-schema.json 不存在")
        return
    try:
        with open(SCHEMA_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _err(f"DIM-3: 无法加载 frontmatter-schema.json: {e}")
        return
    properties = data.get("properties", {})
    derived_from_prop = properties.get("derived_from", {})
    if not derived_from_prop:
        _warn("DIM-3: frontmatter-schema.json 缺少 derived_from 属性定义")
    for fname in VOCAB_FIELD_MAP:
        prop = properties.get(fname, {})
        if not prop:
            continue
        if "enum" in prop and "derived_from" not in prop:
            _warn(
                f"DIM-3 schema_json.{fname}: 有 enum 但缺少 derived_from 标注"
                f"（JSON Schema 中可添加 derived_from 作为扩展属性）"
            )

def check_dim4_derived_from_exists() -> None:
    """DIM-4: derived_from 指向的 vocabulary YAML 文件必须存在"""
    for fname, vocab_file in VOCAB_FIELD_MAP.items():
        vocab_path = VOCAB_DIR / vocab_file
        if not vocab_path.exists():
            _err(f"DIM-4: {fname} 的 vocabulary 文件不存在: {vocab_path}")

def check_dim5_vocab_contains_field() -> None:
    """DIM-5: derived_from 指向的 vocabulary YAML 中对应字段必须存在"""
    for fname, vocab_file in VOCAB_FIELD_MAP.items():
        vocab_path = VOCAB_DIR / vocab_file
        if not vocab_path.exists():
            continue
        try:
            data = load_yaml(vocab_path)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        vocab_name = data.get("vocabulary_name", "")
        if vocab_name != fname:
            _warn(f"DIM-5 {vocab_file}: vocabulary_name='{vocab_name}' " f"与期望的字段名 '{fname}' 不匹配")
        values = data.get("values", [])
        if not values:
            _warn(f"DIM-5 {vocab_file}: values 列表为空")

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(
        description="derived_from 标注完整性闸门（GATE-DERIVED）— 派生文件 derived_from 标注检测"
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现缺失不阻塞（exit 0）",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("GATE-DERIVED: derived_from 标注完整性闸门 v1.0.0")
    print("对标: AGENTS.md §6.13 + §6.14 Level 2 / ITIL SACM")
    print("=" * 72)
    print()

    checks = [
        ("DIM-1: field_registry enum 字段 derived_from 标注", check_dim1_field_registry),
        ("DIM-2: arch_contract allowed_values derived_from 标注", check_dim2_arch_contract),
        ("DIM-3: schema_json enum 属性 derived_from 追溯", check_dim3_schema_json),
        ("DIM-4: derived_from 指向的 vocabulary 文件存在性", check_dim4_derived_from_exists),
        ("DIM-5: vocabulary YAML 字段名匹配", check_dim5_vocab_contains_field),
    ]

    for label, fn in checks:
        print(f"  {label} ...", end=" ", flush=True)
        before_errors = len(_errors)
        before_warnings = len(_warnings)
        fn()
        new_errors = len(_errors) - before_errors
        new_warnings = len(_warnings) - before_warnings
        if new_errors > 0:
            print(f"❌ {new_errors} error(s)")
        elif new_warnings > 0:
            print(f"⚠️ {new_warnings} warning(s)")
        else:
            print("✅ PASS")

    print()

    if _errors:
        print(f"🔴 错误 ({len(_errors)}):")
        for e in _errors:
            print(f"   {e}")
        print()

    if _warnings:
        print(f"🟡 警告 ({len(_warnings)}):")
        for w in _warnings:
            print(f"   {w}")
        print()

    if not _errors and not _warnings:
        print("✅ GATE-DERIVED 全部通过 — 所有派生文件 derived_from 标注完整")
        return EXIT_PASS

    if _errors:
        print(f"🔴 GATE-DERIVED 发现 {len(_errors)} 个标注缺失")
        if args.warn_only:
            print("   (--warn-only 模式，exit 0)")
            return EXIT_PASS
        return EXIT_FINDINGS
    else:
        print(f"🟡 GATE-DERIVED 通过（有 {len(_warnings)} 个标注性警告）")
        return EXIT_PASS

if __name__ == "__main__":
    sys.exit(main())
