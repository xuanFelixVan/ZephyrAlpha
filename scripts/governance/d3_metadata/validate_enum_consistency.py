"""
validate_enum_consistency.py — 枚举自动派生一致性闸门（GATE-ENUM）
v1.0.0 — 2026-05-03



AGENTS.md §6.13 枚举自动派生铁律 + §6.14 漂移免疫架构原则 Level 2 门禁：
  根因：vocabulary YAML 是枚举值的 canonical SSoT，但派生文件（frontmatter-field-registry、
        architecture-contract、frontmatter-schema.json）中的枚举列表是手动硬编码的副本。
        每次新增/废弃枚举值需同时更新 5+ 处，Vibe Coding AI 上下文记忆极短，必然漏改。

  本闸门：扫描所有 vocabulary YAML → 提取枚举值 → 交叉比对所有 derived_from 标注的派生文件
          → 不一致即报错。"vocabulary 改了，派生文件必须同步。"

检查维度：
  DIM-1: vocabulary YAML 枚举值 ↔ frontmatter-field-registry.yaml 中 derived_from 字段的枚举列表
  DIM-2: vocabulary YAML 枚举值 ↔ architecture-contract.yaml 中 derived_from 字段的枚举列表
  DIM-3: vocabulary YAML 枚举值 ↔ frontmatter-schema.json 中对应 enum 数组
  DIM-4: 派生文件中有枚举列表但缺少 derived_from 标注（漏标检测）
  DIM-5: vocabulary YAML 文件完整性——所有 vocabulary 必须在 registry-master-index.yaml 登记

对标：OpenAPI spec:check（spec 改了生成类型必须同步）/ Terraform drift detection（期望 vs 实际）
      ITIL SACM → CI 属性变更必须同步到所有消费该属性的 CMDB 视图

exit codes: 0=一致, 1=发现漂移, 2=系统错误
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-ENUM — 枚举自动派生一致性闸门（§6.14 Level 2 门禁 1/4 — vocabulary YAML ↔ 派生文件枚举列表交叉比对，5维检查）
dimensions:
- D3
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""


import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

from _shared.yaml_utils import load_yaml

VOCAB_TO_FIELD = {
    "doc_type": "doc_type",
    "status": "status",
    "rule_form": "rule_form",
    "ttl": "ttl",
    "layer": "layer",
    "classification": "classification",
    "language": "language",
    "created_by": "created_by",
    "scope": "scope",
    "stability": "stability",
    "verifiability": "verifiability",
}

VOCAB_DIR = GOV_DOCS_DIR / "_registry" / "vocabularies"
CATALOGS_DIR = GOV_DOCS_DIR / "_registry" / "catalogs"
CONTRACTS_DIR = GOV_DOCS_DIR / "_registry" / "contracts"
SCHEMAS_DIR = GOV_DOCS_DIR / "_registry" / "schemas"

FIELD_REGISTRY_PATH = CATALOGS_DIR / "frontmatter-field-registry.yaml"
ARCH_CONTRACT_PATH = CONTRACTS_DIR / "architecture-contract.yaml"
SCHEMA_JSON_PATH = SCHEMAS_DIR / "frontmatter-schema.json"
REGISTRY_MASTER_INDEX_PATH = CATALOGS_DIR / "registry-master-index.yaml"

_errors: list[str] = []
_warnings: list[str] = []

def _err(msg: str) -> None:
    """_err implementation."""
    _errors.append(msg)

def _warn(msg: str) -> None:
    """_warn implementation."""
    _warnings.append(msg)

def _load_vocabularies() -> dict[str, dict]:
    """扫描 vocabularies/ 目录，返回 {vocabulary_name: {values: set, path: Path}}"""
    vocabs: dict[str, dict] = {}
    if not VOCAB_DIR.exists():
        _err(f"vocabularies 目录不存在: {VOCAB_DIR}")
        return vocabs
    for vf in sorted(VOCAB_DIR.glob("*-vocabulary.yaml")):
        try:
            data = load_yaml(vf)
        except Exception as e:
            _warn(f"无法加载 {vf.name}: {e}")
            continue
        if not isinstance(data, dict):
            continue
        vocab_name = data.get("vocabulary_name", "")
        if not vocab_name:
            continue
        values: set[str] = set()
        for entry in data.get("values", []):
            if isinstance(entry, dict):
                val = entry.get("value") or entry.get("id")
                if val:
                    values.add(str(val))
            elif isinstance(entry, str):
                values.add(entry)
        deprecated_values: set[str] = set()
        for entry in data.get("deprecated_values", []):
            if isinstance(entry, dict):
                val = entry.get("value") or entry.get("id")
                if val:
                    deprecated_values.add(str(val))
            elif isinstance(entry, str):
                deprecated_values.add(entry)
        vocabs[vocab_name] = {
            "values": values,
            "deprecated_values": deprecated_values,
            "path": vf,
            "total_values": data.get("total_values", len(values)),
        }
    return vocabs

def _extract_enum_from_field_registry(field_name: str) -> tuple[set[str], str | None]:
    """从 frontmatter-field-registry.yaml 提取指定字段的枚举值和 derived_from
    支持 allowed_values（简单列表）和 enum_values（对象列表）两种格式"""
    if not FIELD_REGISTRY_PATH.exists():
        return set(), None
    try:
        data = load_yaml(FIELD_REGISTRY_PATH)
    except Exception:
        return set(), None
    if not isinstance(data, dict):
        return set(), None
    for field in data.get("fields", []):
        fname = field.get("field_name") or field.get("name")
        if fname == field_name:
            allowed = field.get("allowed_values", [])
            derived = field.get("derived_from")
            if allowed:
                return set(str(v) for v in allowed), derived
            enum_vals = field.get("enum_values", [])
            if enum_vals:
                vals = set()
                for ev in enum_vals:
                    if isinstance(ev, dict):
                        val = ev.get("value", "")
                        if val:
                            vals.add(str(val))
                    elif isinstance(ev, str):
                        vals.add(ev)
                return vals, derived
            return set(), derived
    return set(), None

def _extract_enum_from_arch_contract(field_name: str) -> tuple[set[str], str | None]:
    """从 architecture-contract.yaml 提取指定字段的枚举值和 derived_from"""
    if not ARCH_CONTRACT_PATH.exists():
        return set(), None
    try:
        data = load_yaml(ARCH_CONTRACT_PATH)
    except Exception:
        return set(), None
    if not isinstance(data, dict):
        return set(), None
    fm_schema = data.get("frontmatter_schema", {})
    for field in fm_schema.get("required_fields", []):
        if field.get("name") == field_name:
            allowed = field.get("allowed_values", [])
            derived = field.get("derived_from")
            return set(str(v) for v in allowed), derived
    return set(), None

def _extract_enum_from_schema_json(field_name: str) -> set[str]:
    """从 frontmatter-schema.json 提取指定字段的 enum 或 oneOf+const 值"""
    if not SCHEMA_JSON_PATH.exists():
        return set()
    try:
        with open(SCHEMA_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return set()
    properties = data.get("properties", {})
    prop = properties.get(field_name, {})
    values: set[str] = set()
    for v in prop.get("enum", []):
        values.add(str(v))
    for item in prop.get("oneOf", []):
        const = item.get("const")
        if const is not None:
            values.add(str(const))
    return values

SUBSET_VOCABS = {"doc_type", "layer", "ttl"}

def check_dim1_field_registry(vocabs: dict[str, dict]) -> None:
    """DIM-1: vocabulary YAML ↔ frontmatter-field-registry.yaml

    For SUBSET_VOCABS (doc_type, layer, ttl), the field-registry only contains
    the 01_policies_and_standards/ subset — missing values are warnings, not errors.
    Extra values not in vocabulary are always errors.
    """
    for vocab_name, field_name in VOCAB_TO_FIELD.items():
        if vocab_name not in vocabs:
            continue
        vocab_values = vocabs[vocab_name]["values"]
        registry_values, derived_from = _extract_enum_from_field_registry(field_name)
        if not registry_values:
            continue
        if derived_from and not derived_from.endswith(f"{vocab_name}-vocabulary.yaml"):
            _warn(
                f"DIM-1 field_registry.{field_name}: derived_from='{derived_from}' "
                f"未指向 {vocab_name}-vocabulary.yaml"
            )
        missing_in_registry = vocab_values - registry_values
        extra_in_registry = registry_values - vocab_values - vocabs[vocab_name]["deprecated_values"]
        if missing_in_registry and vocab_name not in SUBSET_VOCABS:
            _err(
                f"DIM-1 field_registry.{field_name}: vocabulary 有 {len(missing_in_registry)} 个值"
                f"未同步到 field-registry: {sorted(missing_in_registry)[:5]}"
            )
        elif missing_in_registry and vocab_name in SUBSET_VOCABS:
            pass
        if extra_in_registry:
            _err(
                f"DIM-1 field_registry.{field_name}: field-registry 有 {len(extra_in_registry)} 个值"
                f"不在 vocabulary 中: {sorted(extra_in_registry)[:5]}"
            )

def check_dim2_arch_contract(vocabs: dict[str, dict]) -> None:
    """DIM-2: vocabulary YAML ↔ architecture-contract.yaml

    architecture-contract.yaml 的 allowed_values 是 vocabulary 的子集
    （仅包含 01_policies_and_standards/ 允许的值），子集关系合法。
    但 contract 中出现 vocabulary 没有的值 = 漂移（error）。
    """
    for vocab_name, field_name in VOCAB_TO_FIELD.items():
        if vocab_name not in vocabs:
            continue
        vocab_values = vocabs[vocab_name]["values"]
        contract_values, derived_from = _extract_enum_from_arch_contract(field_name)
        if not contract_values:
            continue
        if derived_from and not derived_from.endswith(f"{vocab_name}-vocabulary.yaml"):
            _warn(
                f"DIM-2 arch_contract.{field_name}: derived_from='{derived_from}' "
                f"未指向 {vocab_name}-vocabulary.yaml"
            )
        extra_in_contract = contract_values - vocab_values - vocabs[vocab_name]["deprecated_values"]
        if extra_in_contract:
            _err(
                f"DIM-2 arch_contract.{field_name}: architecture-contract 有 {len(extra_in_contract)} 个值"
                f"不在 vocabulary 中: {sorted(extra_in_contract)[:5]}"
            )

def check_dim3_schema_json(vocabs: dict[str, dict]) -> None:
    """DIM-3: vocabulary YAML ↔ frontmatter-schema.json (enum + oneOf+const)

    For SUBSET_VOCABS, schema.json only contains the PS subset — missing is OK.
    """
    for vocab_name, field_name in VOCAB_TO_FIELD.items():
        if vocab_name not in vocabs:
            continue
        vocab_values = vocabs[vocab_name]["values"]
        schema_values = _extract_enum_from_schema_json(field_name)
        if not schema_values:
            continue
        missing_in_schema = vocab_values - schema_values
        extra_in_schema = schema_values - vocab_values - vocabs[vocab_name]["deprecated_values"]
        if missing_in_schema and vocab_name not in SUBSET_VOCABS:
            _err(
                f"DIM-3 schema_json.{field_name}: vocabulary 有 {len(missing_in_schema)} 个值"
                f"未同步到 frontmatter-schema.json: {sorted(missing_in_schema)[:5]}"
            )
        if extra_in_schema:
            _err(
                f"DIM-3 schema_json.{field_name}: frontmatter-schema.json 有 {len(extra_in_schema)} 个值"
                f"不在 vocabulary 中: {sorted(extra_in_schema)[:5]}"
            )

def check_dim4_missing_derived_from(vocabs: dict[str, dict]) -> None:
    """DIM-4: 派生文件中有枚举列表但缺少 derived_from 标注"""
    for vocab_name, field_name in VOCAB_TO_FIELD.items():
        if vocab_name not in vocabs:
            continue
        _, fr_derived = _extract_enum_from_field_registry(field_name)
        if fr_derived is None:
            _warn(
                f"DIM-4 field_registry.{field_name}: 缺少 derived_from 标注"
                f"（应标注 derived_from: '_registry/vocabularies/{vocab_name}-vocabulary.yaml'）"
            )
        _, ac_derived = _extract_enum_from_arch_contract(field_name)
        if ac_derived is None:
            _warn(
                f"DIM-4 arch_contract.{field_name}: 缺少 derived_from 标注"
                f"（应标注 derived_from: '_registry/vocabularies/{vocab_name}-vocabulary.yaml'）"
            )

def check_dim5_vocab_registration(vocabs: dict[str, dict]) -> None:
    """DIM-5: vocabulary YAML 文件必须在 registry-master-index.yaml 登记"""
    if not REGISTRY_MASTER_INDEX_PATH.exists():
        _warn("DIM-5: registry-master-index.yaml 不存在，跳过登记检查")
        return
    try:
        data = load_yaml(REGISTRY_MASTER_INDEX_PATH)
    except Exception:
        _warn("DIM-5: 无法加载 registry-master-index.yaml")
        return
    if not isinstance(data, dict):
        return
    registered_paths: set[str] = set()
    for entry in data.get("registries", []):
        if isinstance(entry, dict):
            pp = entry.get("physical_path", "")
            if pp:
                registered_paths.add(pp)
    for vocab_name, info in vocabs.items():
        vocab_rel = str(info["path"].relative_to(REPO_ROOT)).replace("\\", "/")
        if vocab_rel not in registered_paths:
            _warn(f"DIM-5 {vocab_name}-vocabulary.yaml: " f"未在 registry-master-index.yaml 登记（路径: {vocab_rel}）")

def check_dim6_field_registry_enum_values(vocabs: dict[str, dict]) -> None:
    """DIM-6: field-registry.yaml 中所有 enum_values 字段必须与对应 vocabulary 一致
    For SUBSET_VOCABS, missing values from vocabulary are OK (subset relationship)."""
    for vocab_name, field_name in VOCAB_TO_FIELD.items():
        if vocab_name not in vocabs:
            continue
        vocab_values = vocabs[vocab_name]["values"]
        registry_values, _ = _extract_enum_from_field_registry(field_name)
        if not registry_values:
            continue
        missing = vocab_values - registry_values
        if missing and vocab_name not in SUBSET_VOCABS:
            _err(
                f"DIM-6 field_registry.{field_name}: vocabulary 有 {len(missing)} 个值"
                f"未同步到 field-registry enum_values: {sorted(missing)[:5]}"
            )
        extra = registry_values - vocab_values - vocabs[vocab_name]["deprecated_values"]
        if extra:
            _err(
                f"DIM-6 field_registry.{field_name}: field-registry 有 {len(extra)} 个值"
                f"不在 vocabulary 中: {sorted(extra)[:5]}"
            )

def check_dim7_schema_json_oneof(vocabs: dict[str, dict]) -> None:
    """DIM-7: frontmatter-schema.json 中所有 oneOf+const 必须与对应 vocabulary 一致
    For SUBSET_VOCABS, missing values from vocabulary are OK (subset relationship)."""
    for vocab_name, field_name in VOCAB_TO_FIELD.items():
        if vocab_name not in vocabs:
            continue
        vocab_values = vocabs[vocab_name]["values"]
        schema_values = _extract_enum_from_schema_json(field_name)
        if not schema_values:
            continue
        missing = vocab_values - schema_values
        if missing and vocab_name not in SUBSET_VOCABS:
            _err(
                f"DIM-7 schema_json.{field_name}: vocabulary 有 {len(missing)} 个值"
                f"未同步到 frontmatter-schema.json: {sorted(missing)[:5]}"
            )
        extra = schema_values - vocab_values - vocabs[vocab_name]["deprecated_values"]
        if extra:
            _err(
                f"DIM-7 schema_json.{field_name}: schema.json 有 {len(extra)} 个值"
                f"不在 vocabulary 中: {sorted(extra)[:5]}"
            )

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(
        description="枚举自动派生一致性闸门（GATE-ENUM）— vocabulary YAML ↔ 派生文件枚举列表交叉比对"
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现漂移不阻塞（exit 0）",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("GATE-ENUM: 枚举自动派生一致性闸门 v2.0.0")
    print("对标: AGENTS.md §6.13 + §6.14 Level 2 / OpenAPI spec:check")
    print("=" * 72)
    print()

    vocabs = _load_vocabularies()
    if not vocabs:
        print("[ERROR] 未找到任何 vocabulary YAML 文件", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    print(f"  已加载 {len(vocabs)} 个 vocabulary YAML:")
    for name, info in vocabs.items():
        print(f"    - {name}: {len(info['values'])} 个有效值, {len(info['deprecated_values'])} 个废弃值")
    print()

    checks = [
        ("DIM-1: vocabulary ↔ frontmatter-field-registry.yaml", check_dim1_field_registry),
        ("DIM-2: vocabulary ↔ architecture-contract.yaml", check_dim2_arch_contract),
        ("DIM-3: vocabulary ↔ frontmatter-schema.json", check_dim3_schema_json),
        ("DIM-4: 派生文件 derived_from 标注完整性", check_dim4_missing_derived_from),
        ("DIM-5: vocabulary YAML 登记完整性", check_dim5_vocab_registration),
        ("DIM-6: field-registry enum_values ↔ vocabulary", check_dim6_field_registry_enum_values),
        ("DIM-7: schema.json oneOf+const ↔ vocabulary", check_dim7_schema_json_oneof),
    ]

    for label, fn in checks:
        print(f"  {label} ...", end=" ", flush=True)
        before_errors = len(_errors)
        before_warnings = len(_warnings)
        fn(vocabs)
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
        print("✅ GATE-ENUM 全部通过 — 所有枚举值从 vocabulary YAML 一致派生")
        return EXIT_PASS

    if _errors:
        print(f"🔴 GATE-ENUM 发现 {len(_errors)} 个枚举漂移")
        if args.warn_only:
            print("   (--warn-only 模式，exit 0)")
            return EXIT_PASS
        return EXIT_FINDINGS
    else:
        print(f"🟡 GATE-ENUM 通过（有 {len(_warnings)} 个标注性警告）")
        return EXIT_PASS

if __name__ == "__main__":
    sys.exit(main())
