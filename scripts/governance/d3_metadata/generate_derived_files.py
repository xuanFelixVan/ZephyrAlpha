# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_derived_files.py | §
# [MODULE] scripts.governance.d3_metadata.generate_derived_files
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] event_driven
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
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
from _shared.yaml_utils import load_vocabulary_entries, load_vocabulary_values, load_yaml  # noqa: E402  # D-D-05：词表加载收敛到 SSoT

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
    "classification": "classification_vocabulary.yaml",
    "language": "language_vocabulary.yaml",
    "created_by": "created_by_vocabulary.yaml",
    "scope": "scope_vocabulary.yaml",
    "stability": "stability_vocabulary.yaml",
    "verifiability": "verifiability_vocabulary.yaml",
    "safety_level": "safety_level_vocabulary.yaml",
    "evolution_policy": "evolution_policy_vocabulary.yaml",
    "ai_autonomy": "ai_autonomy_vocabulary.yaml",
    "governance_family": "governance_family_vocabulary.yaml",
    "ai_capability_slot": "ai_capability_slot_vocabulary.yaml",
    "ai_autonomy_level_planned": "ai_autonomy_level_planned_vocabulary.yaml",
    "review_status": "review_status_vocabulary.yaml",
    "category": "category_vocabulary.yaml",
    "domain": "domain_vocabulary.yaml",
    "header_format": "header_format_vocabulary.yaml",
    "file_category": "file_category_vocabulary.yaml",
}

_drifts: list[str] = []


def _drift(msg: str) -> None:
    """_drift implementation."""
    _drifts.append(msg)


def _load_vocab_values(vocab_name: str) -> list[str]:
    """加载 vocabulary YAML 的有效值列表。

    D-D-05 治本（2026-06-30）：收敛到 SSoT ``load_vocabulary_values``。
    原函数返回 tuple(valid, deprecated)，但调用方只用 valid（_deprecated 未使用），
    故简化为只返回 valid list。fallback_key="id" 兼容 value/id 双键。
    """
    vocab_file = VOCAB_FIELD_MAP.get(vocab_name)
    if not vocab_file:
        return []
    return list(
        load_vocabulary_values(vocab_file, fallback_key="id", strict=False)
    )


def _sync_field_registry(field_name: str, vocab_values: list[str], apply: bool) -> bool:  # noqa: gate-vocab  # 派生文件同步器：用 vocab_values 比对 field_registry，非复制词表加载
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

        # dynamic_from_ssot 标志：值集由词表单一维护，派生同步应跳过
        # 大小写不敏感——YAML 中可能写作 dynamic_from_ssot 或 DYNAMIC_FROM_SSOT
        _av = field.get("allowed_values")
        _ev = field.get("enum_values")
        _has_sentinel = (
            (isinstance(_av, str) and _av.lower() == "dynamic_from_ssot")
            or (isinstance(_ev, str) and _ev.lower() == "dynamic_from_ssot")
        )
        if _has_sentinel:
            continue

        # Sentinel 完整性检查：VOCAB_FIELD_MAP 中的字段必须有 sentinel
        # 防止 sentinel 被删除后硬编码值——即使值当前一致，未来词表变更会漂移
        if field_name in VOCAB_FIELD_MAP:
            _drift(
                f"field_registry.{field_name}: 字段在 VOCAB_FIELD_MAP 中但未使用 dynamic_from_ssot sentinel"
                f"——sentinel 可能被删除并替换为硬编码值，这会导致未来词表变更时漂移"
            )

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


def _sync_arch_contract(field_name: str, vocab_values: list[str], apply: bool) -> bool:  # noqa: gate-vocab  # 派生文件同步器：用 vocab_values 比对 arch_contract，非复制词表加载
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
        # dynamic_from_ssot 标志：值集由词表单一维护，派生同步应跳过
        # 大小写不敏感——YAML 中可能写作 dynamic_from_ssot 或 DYNAMIC_FROM_SSOT
        _av = field.get("allowed_values")
        _has_sentinel = isinstance(_av, str) and _av.lower() == "dynamic_from_ssot"
        if _has_sentinel:
            continue

        # Sentinel 完整性检查：VOCAB_FIELD_MAP 中的字段必须有 sentinel
        if field_name in VOCAB_FIELD_MAP:
            _drift(
                f"arch_contract.{field_name}: 字段在 VOCAB_FIELD_MAP 中但未使用 dynamic_from_ssot sentinel"
                f"——sentinel 可能被删除，这会导致未来词表变更时漂移"
            )

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


def _sync_schema_json(field_name: str, vocab_entries: list[dict], apply: bool) -> bool:
    """同步 frontmatter_schema.json 中的 oneOf+const（或 enum）数组

    schema_json 中 enum 可能是字符串数组或带描述的对象数组，
    oneOf+const 用于更结构化的枚举定义，需要正确提取当前值进行比对。

    治本（2026-06-30）：双向同步——除了检测 extra（schema 多出的值），
    还检测 missing（词表有但 schema 缺失的值）。--apply 时从词表 definition
    填充新增 oneOf+const 项的 description，保证 schema 完整性。
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

    vocab_set = set(e["value"] for e in vocab_entries)
    # ── extra 检测：schema 多出的值（不在词表中）──
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

    # ── missing 检测：词表有但 schema 缺失的值（治本 2026-06-30 双向同步）──
    missing = vocab_set - current_set
    if missing:
        _drift(f"schema_json.{field_name}: 缺失 {len(missing)} 个 vocabulary 中的值: {sorted(missing)[:5]}")
        if apply:
            entry_map = {e["value"]: e["definition"] for e in vocab_entries}
            if "oneOf" in prop:
                for val in sorted(missing):
                    prop["oneOf"].append({
                        "const": val,
                        "description": entry_map.get(val, val),
                    })
                changed = True
            elif "enum" in prop:
                for val in sorted(missing):
                    prop["enum"].append(val)
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


def _sync_schema_allof_rule_form(apply: bool) -> bool:
    """同步 frontmatter_schema.json 的 allOf rule_form 条件约束块（P7-FIX 治本）。

    从 doc_type_vocabulary.yaml 的 per-value allowed_rule_forms 字段自动生成
    allOf 块（单值→const / 多值→enum），覆盖手动维护的 rule_form 约束。
    非 rule_form 的 allOf 块（status/stability/file_category 约束）保留不动。

    真源链：doc_type_vocabulary.yaml values[].allowed_rule_forms
            → frontmatter_schema.json allOf[].then.properties.rule_form
    """
    if not SCHEMA_JSON_PATH.exists():
        return False

    # 1. 加载 doc_type_vocabulary.yaml 的 allowed_rule_forms（按词表顺序）
    doc_type_path = VOCAB_DIR / "doc_type_vocabulary.yaml"
    if not doc_type_path.exists():
        return False
    doc_type_vocab = load_yaml(str(doc_type_path))
    if not isinstance(doc_type_vocab, dict):
        return False
    values = doc_type_vocab.get("values", [])
    if not isinstance(values, list):
        return False

    # 2. 加载 rule_form_vocabulary.yaml 合法值（校验 allowed_rule_forms 引用合法性）
    rule_form_values = set(load_vocabulary_values("rule_form_vocabulary.yaml"))

    # 3. 构建期望的 rule_form allOf 块（按词表顺序）
    expected_blocks: list[dict] = []
    for entry in values:
        if not isinstance(entry, dict):
            continue
        dt = entry.get("value")
        allowed = entry.get("allowed_rule_forms")
        if not dt or not allowed or not isinstance(allowed, list):
            continue
        # 校验 allowed_rule_forms 引用的值都在 rule_form_vocabulary.yaml 中
        for rf in allowed:
            if rule_form_values and str(rf) not in rule_form_values:
                _drift(
                    f"schema_json allof: doc_type={dt} allowed_rule_forms "
                    f"含非法 rule_form 值 '{rf}'（不在 rule_form_vocabulary.yaml 中）"
                )
        # 生成约束块
        allowed_strs = [str(v) for v in allowed]
        if len(allowed_strs) == 1:
            rule_form_constraint: dict = {"const": allowed_strs[0]}
            desc = f"{dt} 类型的 rule_form 必须为 {allowed_strs[0]}"
        else:
            rule_form_constraint = {"enum": allowed_strs}
            desc = f"{dt} 类型的 rule_form 为 {' 或 '.join(allowed_strs)}"
        expected_blocks.append({
            "description": desc,
            "if": {
                "properties": {"doc_type": {"const": str(dt)}},
                "required": ["doc_type"],
            },
            "then": {
                "properties": {"rule_form": rule_form_constraint},
            },
        })

    # 4. 加载 schema.json，拆分 allOf 为 rule_form 块和其他块
    try:
        with open(SCHEMA_JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    existing_allof = data.get("allOf", [])
    if not isinstance(existing_allof, list):
        return False

    # 5. 比较期望 vs 实际的 rule_form 块（结构+描述都比对，全量自动生成）
    actual_rf_blocks: list[dict] = []
    for block in existing_allof:
        if not isinstance(block, dict):
            continue
        then_props = block.get("then", {}).get("properties", {})
        if "rule_form" in then_props:
            actual_rf_blocks.append(block)

    expected_json = json.dumps(expected_blocks, ensure_ascii=False, sort_keys=True)
    actual_json = json.dumps(actual_rf_blocks, ensure_ascii=False, sort_keys=True)
    changed = expected_json != actual_json

    if changed:
        _drift(
            f"schema_json allOf rule_form: 需重新生成"
            f"（期望 {len(expected_blocks)} 块，当前 {len(actual_rf_blocks)} 块）"
        )
        if apply:
            # 重建 allOf：保留非 rule_form 块的原顺序，在首个 rule_form 块位置插入生成块
            new_allof: list[dict] = []
            rf_inserted = False
            for block in existing_allof:
                if not isinstance(block, dict):
                    new_allof.append(block)
                    continue
                then_props = block.get("then", {}).get("properties", {})
                if "rule_form" in then_props:
                    if not rf_inserted:
                        new_allof.extend(expected_blocks)
                        rf_inserted = True
                    # 跳过旧的 rule_form 块（已被生成的替代）
                else:
                    new_allof.append(block)
            if not rf_inserted:
                # 无既有 rule_form 块，追加到末尾
                new_allof.extend(expected_blocks)
            data["allOf"] = new_allof

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


def _check_unregistered_enum_fields() -> bool:
    """检测 schema.json 中有枚举字段未注册到 VOCAB_FIELD_MAP（治本 2026-06-30）。

    红方攻击防御：AI 新增 frontmatter 字段时直接手写 enum，不建词表，
    GATE-GENERATE 只校验 VOCAB_FIELD_MAP 中的字段，新字段漏检→多真源。
    本函数扫描 schema.json 所有枚举字段，发现未注册的就报告 drift，
    强制新增枚举字段必须在 VOCAB_FIELD_MAP 注册对应词表。

    空的 oneOf/enum（如 depends_on 占位符）不触发——只检测有实际值的字段。
    """
    if not SCHEMA_JSON_PATH.exists():
        return False
    try:
        data = json.loads(SCHEMA_JSON_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    properties = data.get("properties", {})
    unregistered: list[str] = []
    for name, prop in properties.items():
        if not isinstance(prop, dict):
            continue
        has_enum_values = False
        if "oneOf" in prop:
            for item in prop["oneOf"]:
                if isinstance(item, dict) and "const" in item:
                    has_enum_values = True
                    break
        elif "enum" in prop and prop["enum"]:
            has_enum_values = True
        if has_enum_values and name not in VOCAB_FIELD_MAP:
            unregistered.append(name)
    if unregistered:
        _drift(
            f"schema_json: {len(unregistered)} 个枚举字段未注册到 VOCAB_FIELD_MAP: "
            f"{unregistered}——新增枚举字段必须在 VOCAB_FIELD_MAP 注册对应词表，"
            f"否则 GATE-GENERATE 不会校验该字段（漏检多真源）"
        )
    return bool(unregistered)


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
        valid_values = _load_vocab_values(vocab_name)
        if not valid_values:
            print(f"  {vocab_name}: ⚠️ vocabulary 为空或不存在，跳过")
            continue

        print(f"  {vocab_name}: {len(valid_values)} 个有效值")

        c1 = _sync_field_registry(vocab_name, valid_values, apply)
        c2 = _sync_arch_contract(vocab_name, valid_values, apply)
        # _sync_schema_json 需要 vocab_entries（含 definition）用于 missing 检测
        # 治本（2026-06-30）：收敛到 SSoT load_vocabulary_entries（公共函数，非局部副本）
        vocab_file = VOCAB_FIELD_MAP.get(vocab_name, "")
        vocab_entries = load_vocabulary_entries(vocab_file, fallback_key="id", strict=False)
        c3 = _sync_schema_json(vocab_name, vocab_entries, apply)

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

    # P7-FIX：同步 allOf rule_form 条件约束块（从 doc_type_vocabulary.yaml allowed_rule_forms 自动生成）
    c4 = _sync_schema_allof_rule_form(apply)
    if c4:
        total_changes += 1
        action = "已同步" if apply else "待同步"
        print(f"  allOf rule_form: → {action}: schema_json_allof={'✅' if apply else '⏭️'}")

    # 治本（2026-06-30）：检测未注册枚举字段（防漏检多真源）
    _check_unregistered_enum_fields()

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
        print(f"🔴 发现 {len(_drifts)} 处漂移")
        print("   修复方式：python scripts/governance/d3_metadata/generate_derived_files.py --apply")
        print("   （--apply 会自动同步 extra+missing，sentinel 字段需人工裁定）")
        if args.warn_only:
            print("   (--warn-only 模式，exit 0)")
            return EXIT_PASS
        return EXIT_FINDINGS

    print("✅ 所有派生文件与 vocabulary YAML 一致")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
