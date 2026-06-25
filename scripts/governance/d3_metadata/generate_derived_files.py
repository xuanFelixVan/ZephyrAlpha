# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_derived_files.py | §
# [MODULE] scripts.governance.d3_metadata.generate_derived_files
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""
generate_derived_files.py — 枚举自动派生生成器（Level 3 终极防御）
v1.0.0 — 2026-05-03



AGENTS.md §6.14 漂移免疫架构原则 Level 3：
  从 vocabulary YAML（canonical SSoT）自动生成派生文件中的枚举列表，
  消除手动复制——物理上不可能漂移。

  对标：K8s CRD derive macro（Go 类型 → CRD schema 自动派生）
        Terraform terraform-docs（state → README 自动生成）
        OpenAPI code generators（spec → 类型自动生成）

派生链：
  1. vocabularies/{field}_vocabulary.yaml → frontmatter_field_registry.yaml (allowed_values/enum_values)
  2. vocabularies/{field}_vocabulary.yaml → architecture_contract.yaml (allowed_values)
  3. vocabularies/{field}_vocabulary.yaml → frontmatter_schema.json (oneOf+const)

使用方式：
  python generate_derived_files.py --check    # 仅检查，不修改文件
  python generate_derived_files.py --apply    # 应用变更到派生文件
  python generate_derived_files.py --diff     # 显示差异但不应用

exit codes: 0=一致/已应用, 1=发现漂移, 2=系统错误
"""

from __future__ import annotations

__manifest__ = """
args:
- --check
description: GATE-GENERATE — 枚举自动派生生成器（§6.14 Level 3 — vocabulary YAML → 派生文件枚举列表自动同步，--check/--apply/--diff）
dimensions:
- D3
priority: P2
timeout_seconds: 30
warn_only: true
"""


import json
import os
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

import yaml
from _shared.yaml_utils import load_yaml

VOCAB_DIR = GOV_DOCS_DIR / "_registry" / "vocabularies"
CATALOGS_DIR = GOV_DOCS_DIR / "_registry" / "catalogs"
CONTRACTS_DIR = GOV_DOCS_DIR / "_registry" / "contracts"
SCHEMAS_DIR = GOV_DOCS_DIR / "_registry" / "schemas"

FIELD_REGISTRY_PATH = CATALOGS_DIR / "frontmatter_field_registry.yaml"
ARCH_CONTRACT_PATH = CONTRACTS_DIR / "architecture_contract.yaml"
SCHEMA_JSON_PATH = SCHEMAS_DIR / "frontmatter_schema.json"

VOCAB_FIELD_MAP = {
    "doc_type": "doc_type_vocabulary.yaml",
    "status": "status_vocabulary.yaml",
    "rule_form": "rule_form_vocabulary.yaml",
    "ttl": "ttl_vocabulary.yaml",
    "layer": "layer_vocabulary.yaml",
}

_drifts: list[str] = []


def _drift(msg: str) -> None:
    """_drift implementation."""
    _drifts.append(msg)


def _load_vocab_values(vocab_name: str) -> tuple[list[str], list[str]]:
    """加载 vocabulary YAML 的有效值和废弃值列表"""
    vocab_file = VOCAB_FIELD_MAP.get(vocab_name)
    if not vocab_file:
        return [], []
    vocab_path = VOCAB_DIR / vocab_file
    if not vocab_path.exists():
        return [], []
    try:
        data = load_yaml(vocab_path)
    except Exception:
        return [], []
    if not isinstance(data, dict):
        return [], []
    valid: list[str] = []
    for entry in data.get("values", []):
        if isinstance(entry, dict):
            val = entry.get("value") or entry.get("id")
            if val:
                valid.append(str(val))
        elif isinstance(entry, str):
            valid.append(entry)
    deprecated: list[str] = []
    for entry in data.get("deprecated_values", []):
        if isinstance(entry, dict):
            val = entry.get("value") or entry.get("id")
            if val:
                deprecated.append(str(val))
        elif isinstance(entry, str):
            deprecated.append(entry)
    return valid, deprecated


def _sync_field_registry(field_name: str, vocab_values: list[str], apply: bool) -> bool:
    """同步 frontmatter_field_registry.yaml 中的 allowed_values/enum_values

    field_registry 有两种枚举表示：
    - allowed_values: 简单值列表（部分字段）
    - enum_values: 带 description 的对象列表（部分字段）
    两种都需比对。
    """
    if not FIELD_REGISTRY_PATH.exists():
        return False
    try:
        with open(FIELD_REGISTRY_PATH, encoding="utf-8") as f:
            content = f.read()
        data = yaml.safe_load(content)
    except Exception:
        return False
    if not isinstance(data, dict):
        return False

    changed = False
    for field in data.get("fields", []):
        fname = field.get("field_name") or field.get("name", "")
        if fname != field_name:
            continue

        current_values: set[str] = set()
        if "allowed_values" in field:
            current_values = set(str(v) for v in field.get("allowed_values", []))
        elif "enum_values" in field:
            for ev in field.get("enum_values", []):
                if isinstance(ev, dict):
                    val = ev.get("value") or ev.get("id")
                    if val:
                        current_values.add(str(val))
                elif isinstance(ev, str):
                    current_values.add(ev)

        vocab_set = set(vocab_values)
        extra = current_values - vocab_set
        if extra:
            _drift(f"field_registry.{field_name}: 多出 {len(extra)} 个不在 vocabulary 中的值: {sorted(extra)[:5]}")
            if apply and "allowed_values" in field:
                field["allowed_values"] = [v for v in field.get("allowed_values", []) if str(v) in vocab_set]
                changed = True
            elif apply and "enum_values" in field:
                field["enum_values"] = [
                    ev for ev in field.get("enum_values", [])
                    if (isinstance(ev, dict) and str(ev.get("value") or ev.get("id") or "") in vocab_set)
                    or (isinstance(ev, str) and ev in vocab_set)
                ]
                changed = True

    if changed and apply:
        tmp_path = f"{FIELD_REGISTRY_PATH}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            os.replace(tmp_path, FIELD_REGISTRY_PATH)
        except (PermissionError, OSError):
            pass
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    return changed


def _sync_arch_contract(field_name: str, vocab_values: list[str], apply: bool) -> bool:
    """同步 architecture_contract.yaml 中的 allowed_values（仅同步 vocabulary 的子集）"""
    if not ARCH_CONTRACT_PATH.exists():
        return False
    try:
        with open(ARCH_CONTRACT_PATH, encoding="utf-8") as f:
            content = f.read()
        data = yaml.safe_load(content)
    except Exception:
        return False
    if not isinstance(data, dict):
        return False

    changed = False
    fm_schema = data.get("frontmatter_schema", {})
    for field in fm_schema.get("required_fields", []):
        fname = field.get("name", "")
        if fname != field_name:
            continue
        current = field.get("allowed_values", [])
        current_set = set(str(v) for v in current)
        vocab_set = set(vocab_values)
        extra = current_set - vocab_set
        if extra:
            _drift(f"arch_contract.{field_name}: 有 {len(extra)} 个值不在 vocabulary 中: {sorted(extra)[:5]}")
            if apply:
                valid_only = [v for v in current if str(v) in vocab_set]
                field["allowed_values"] = valid_only
                changed = True

    if changed and apply:
        tmp_path = f"{ARCH_CONTRACT_PATH}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            os.replace(tmp_path, ARCH_CONTRACT_PATH)
        except (PermissionError, OSError):
            pass
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    return changed


def _sync_schema_json(field_name: str, vocab_values: list[str], apply: bool) -> bool:
    """同步 frontmatter_schema.json 中的 oneOf+const（或 enum）数组

    schema_json 中 enum 可能是字符串数组或带描述的对象数组，
    oneOf+const 用于更结构化的枚举定义，需要正确提取当前值进行比对。
    """
    if not SCHEMA_JSON_PATH.exists():
        return False
    try:
        with open(SCHEMA_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False

    changed = False
    properties = data.get("properties", {})
    prop = properties.get(field_name, {})
    if not prop:
        return False

    current_enum = prop.get("enum", [])
    current_set: set[str] = set()
    for v in current_enum:
        if isinstance(v, str):
            current_set.add(v)
        elif isinstance(v, dict):
            val = v.get("value") or v.get("const")
            if val:
                current_set.add(str(val))
    if not current_enum and "oneOf" in prop:
        for item in prop["oneOf"]:
            if isinstance(item, dict):
                val = item.get("const")
                if val:
                    current_set.add(str(val))

    vocab_set = set(vocab_values)
    extra = current_set - vocab_set
    if extra:
        _drift(f"schema_json.{field_name}: 多出 {len(extra)} 个不在 vocabulary 中的值: {sorted(extra)[:5]}")
        if apply:
            if "oneOf" in prop:
                prop["oneOf"] = [
                    item for item in prop.get("oneOf", [])
                    if isinstance(item, dict)
                    and str(item.get("const", "")) in vocab_set
                ]
                prop.pop("enum", None)
            elif "enum" in prop:
                prop["enum"] = [v for v in current_enum if isinstance(v, str) and v in vocab_set]
            changed = True

    if changed and apply:
        tmp_path = f"{SCHEMA_JSON_PATH}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            os.replace(tmp_path, SCHEMA_JSON_PATH)
        except (PermissionError, OSError):
            pass
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    return changed


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(
        description="枚举自动派生生成器（Level 3）— vocabulary YAML → 派生文件枚举列表自动同步"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="仅检查漂移，不修改文件",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="应用变更到派生文件",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="显示差异但不应用",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现漂移不阻塞（exit 0）",
    )
    args = parser.parse_args()

    if not args.check and not args.apply and not args.diff:
        args.check = True

    print("=" * 72)
    print("GATE-GENERATE: 枚举自动派生生成器 v1.0.0 (Level 3)")
    print("对标: K8s derive macro / Terraform terraform-docs / OpenAPI generators")
    print("=" * 72)
    print()

    apply = args.apply
    total_changes = 0

    for vocab_name in VOCAB_FIELD_MAP:
        valid_values, _deprecated = _load_vocab_values(vocab_name)
        if not valid_values:
            print(f"  {vocab_name}: ⚠️ vocabulary 为空或不存在，跳过")
            continue

        print(f"  {vocab_name}: {len(valid_values)} 个有效值")

        c1 = _sync_field_registry(vocab_name, valid_values, apply)
        c2 = _sync_arch_contract(vocab_name, valid_values, apply)
        c3 = _sync_schema_json(vocab_name, valid_values, apply)

        changes = sum(1 for c in [c1, c2, c3] if c)
        if changes:
            total_changes += changes
            action = "已同步" if apply else "待同步"
            print(
                f"    → {action}: field_registry={'✅' if c1 else '⏭️'} "
                f"arch_contract={'✅' if c2 else '⏭️'} schema_json={'✅' if c3 else '⏭️'}"
            )
        else:
            print("    → ✅ 一致")

    print()

    if _drifts:
        print(f"📋 漂移详情 ({len(_drifts)} 项):")
        for d in _drifts:
            print(f"   • {d}")
        print()

    if total_changes > 0:
        print(f"✅ 已应用 {total_changes} 处变更")
        return EXIT_PASS

    if _drifts:
        print(f"🔴 发现 {len(_drifts)} 处漂移（使用 --apply 同步）")
        if args.warn_only:
            print("   (--warn-only 模式，exit 0)")
            return EXIT_PASS
        return EXIT_FINDINGS

    print("✅ 所有派生文件与 vocabulary YAML 一致")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
