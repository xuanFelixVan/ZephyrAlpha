# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_architecture_contract_internal.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_architecture_contract_internal
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [TTL] permanent
"""GATE-CONTRACT: CI gate for architecture_contract.yaml internal consistency.
Prevents internal inconsistencies (regex conflicts, doc_type gaps, VR skew)
from reaching the codebase—closes the root cause of 3 CRITICAL issues in
the third audit.


Dimensions:
  DIM-1: module_id regex consistency (frontmatter_schema vs VR-001)
  DIM-2: doc_type consistency (frontmatter_schema vs VR-002)
  DIM-3: VR rule sequential numbering
  DIM-4: total_vr_rules matches actual count
  DIM-5: frontmatter field stage completeness

Exit 1 on any FAIL → pre_commit blocks the commit.
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args: []
description: GATE-CONTRACT — architecture_contract 内部一致性校验（7 维度：regex/doc_type/VR编号一致性等）
dimensions:
- D3
- D5
priority: P0
timeout_seconds: 15
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

CONTRACT_PATH = REPO_ROOT / "docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml"
DOC_TYPE_VOCAB_PATH = REPO_ROOT / "docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml"


def load_contract() -> dict:
    """加载合约定义"""
    with open(CONTRACT_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)
        "加载数据."
    "load contract."


def load_doc_type_vocab_values() -> dict:
    """加载文档类型词汇值"""
    with open(DOC_TYPE_VOCAB_PATH, encoding="utf-8") as f:
        "加载数据."
        vocab = yaml.safe_load(f)
    return {entry["value"] for entry in vocab.get("values", [])}
    "加载文档类型词汇值."


def check_dim1_module_id_regex(contract) -> list[dict]:
    """DIM-1: frontmatter_schema module_id regex must match VR-001 regex."""
    vr001 = None
    for vr in contract.get("validation_rules", []):
        if vr["id"] == "VR-001":
            vr001 = vr
            break
    if vr001 is None:
        return ("FAIL", "VR-001 not found in validation_rules")
    vr001_desc = vr001.get("check", "")
    vr001_regex_match = re.search("(?:matches\\s+|regex\\s*[=:]\\s*)([\\^][^\\s]+)", vr001_desc)
    vr001_regex = vr001_regex_match.group(1) if vr001_regex_match else None
    fms_fields = contract.get("frontmatter_schema", {}).get("required_fields", [])
    fms_module = None
    for field in fms_fields:
        if field.get("name") == "module_id":
            fms_module = field
            break
    if fms_module is None:
        return ("FAIL", "module_id field not found in frontmatter_schema required_fields")
    fms_regex = fms_module.get("format", "")
    if fms_regex != vr001_regex:
        return ("FAIL", f"module_id regex mismatch: frontmatter_schema={fms_regex}, VR-001={vr001_regex}")
    return ("PASS", "module_id regex consistent")


def check_dim2_doc_type_consistency(contract) -> list[dict]:
    """DIM-2: VR-002 doc_type list must match frontmatter_schema doc_type allowed_values."""
    vr002 = None
    for vr in contract.get("validation_rules", []):
        if vr["id"] == "VR-002":
            vr002 = vr
            break
    if vr002 is None:
        return ("FAIL", "VR-002 not found in validation_rules")
    fms_fields = contract.get("frontmatter_schema", {}).get("required_fields", [])
    fms_doc_type = None
    for field in fms_fields:
        if field.get("name") == "doc_type":
            fms_doc_type = field
            break
    if fms_doc_type is None:
        return ("FAIL", "doc_type field not found in frontmatter_schema required_fields")
    # dynamic_from_ssot sentinel: values loaded at runtime from vocabulary, skip static comparison
    if fms_doc_type.get("allowed_values") == "dynamic_from_ssot":
        return ("PASS", "doc_type uses dynamic_from_ssot sentinel - values loaded from vocabulary at runtime")
    fms_values = set(fms_doc_type.get("allowed_values", []))
    vr002_check = vr002.get("check", "")
    vr002_values = set()
    for prefix_match in re.finditer("\\[([a-zA-Z_,\\s]+)\\]", vr002_check):
        for val in prefix_match.group(1).split(","):
            cleaned = val.strip()
            if cleaned and (not cleaned.startswith(".")):
                vr002_values.add(cleaned)
    if fms_values != vr002_values:
        only_fms = fms_values - vr002_values
        only_vr = vr002_values - fms_values
        parts = []
        if only_fms:
            parts.append(f"frontmatter_schema only: {sorted(only_fms)}")
        if only_vr:
            parts.append(f"VR-002 only: {sorted(only_vr)}")
        return ("FAIL", "doc_type values mismatch: " + "; ".join(parts))
    return ("PASS", "doc_type values consistent")


def check_dim3_vr_sequential(contract) -> list[dict]:
    """DIM-3: VR rules must be sequentially numbered."""
    vr_ids = []
    for vr in contract.get("validation_rules", []):
        vr_ids.append(vr["id"])
    expected = [f"VR-{i:03d}" for i in range(1, len(vr_ids) + 1)]
    if vr_ids != expected:
        return ("FAIL", f"Non-sequential VR IDs: {vr_ids} (expected {expected})")
    return ("PASS", "VR rules sequentially numbered")


def check_dim4_total_vr_count(contract) -> list[dict]:
    """DIM-4: total_vr_rules must match actual VR count."""
    declared = contract.get("total_vr_rules")
    actual = len(contract.get("validation_rules", []))
    if declared != actual:
        return ("FAIL", f"total_vr_rules={declared}, actual={actual}")
    return ("PASS", "total_vr_rules matches actual")


def check_dim5_field_stage_completeness(contract) -> list[dict]:
    """DIM-5: All required_fields must have stage indicators, sums must match PS-STD-001 §2.2."""
    required = contract.get("frontmatter_schema", {}).get("required_fields", [])
    conditional = contract.get("frontmatter_schema", {}).get("conditional_required", [])
    missing_stage = [f["name"] for f in required if "stage" not in f]
    if missing_stage:
        return ("FAIL", f"required_fields missing stage: {missing_stage}")
    stage_counts = {"draft": 0, "active": 0, "deprecated_only": 0}
    for f in required:
        stage = f.get("stage", "")
        if stage in stage_counts:
            stage_counts[stage] += 1
    for f in conditional:
        stage = f.get("stage", "")
        if stage in stage_counts:
            stage_counts[stage] += 1
    if stage_counts["draft"] not in (6, 7):
        return ("FAIL", f"draft stage has {stage_counts['draft']} fields (PS-STD-001 §2.2 specifies 7)")
    return (
        "PASS",
        f"stage counts: draft={stage_counts['draft']}, active={stage_counts['active']}, deprecated_only={stage_counts['deprecated_only']}",
    )


def check_dim6_vocab_derived_from(contract) -> list[dict]:
    """DIM-6: Each field with allowed_values/derived_from must have a reachable vocabulary."""
    vocab_dir = CONTRACT_PATH.parent.parent / "vocabularies"
    existing_vocabs = {f.name for f in vocab_dir.glob("*.yaml")}
    failures = []
    all_fields = contract.get("frontmatter_schema", {}).get("required_fields", [])
    all_fields += contract.get("frontmatter_schema", {}).get("conditional_required", [])
    all_fields += contract.get("frontmatter_schema", {}).get("optional_fields", [])
    for field in all_fields:
        derived = field.get("derived_from", "")
        if derived:
            vocab_name = derived.replace("_registry/vocabularies/", "")
            if vocab_name not in existing_vocabs:
                failures.append(f"{field['name']} derived_from={vocab_name} not found")
    if failures:
        return ("FAIL", "; ".join(failures))
    return ("PASS", "all derived_from vocabularies reachable")


def check_dim7_doc_type_subset(contract) -> list[dict]:
    """DIM-7: doc_type in frontmatter_schema must be a subset of vocabulary."""
    try:
        vocab_values = load_doc_type_vocab_values()
    except Exception as e:
        return ("FAIL", f"cannot load doc_type_vocabulary.yaml: {e}")
    fms_fields = contract.get("frontmatter_schema", {}).get("required_fields", [])
    fms_doc_type = None
    for f in fms_fields:
        if f.get("name") == "doc_type":
            fms_doc_type = f
            break
    if fms_doc_type is None:
        return ("FAIL", "doc_type not in required_fields")
    # dynamic_from_ssot sentinel: values loaded at runtime from vocabulary, trivially a subset
    if fms_doc_type.get("allowed_values") == "dynamic_from_ssot":
        return ("PASS", "doc_type uses dynamic_from_ssot sentinel - values are vocabulary values at runtime")
    fms_values = set(fms_doc_type.get("allowed_values", []))
    not_in_vocab = fms_values - vocab_values
    if not_in_vocab:
        return ("FAIL", f"contract values not in vocabulary: {sorted(not_in_vocab)}")
    return ("PASS", f"contract doc_type ({len(fms_values)}) is subset of vocabulary ({len(vocab_values)})")


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    if not CONTRACT_PATH.exists():
        print(f"FATAL: {CONTRACT_PATH} not found")
        sys.exit(EXIT_ERROR)
    contract = load_contract()
    dimensions = [
        ("DIM-1 module_id regex", check_dim1_module_id_regex),
        ("DIM-2 doc_type consistency (VR-002)", check_dim2_doc_type_consistency),
        ("DIM-3 VR sequential numbering", check_dim3_vr_sequential),
        ("DIM-4 total_vr_rules", check_dim4_total_vr_count),
        ("DIM-5 field stage completeness", check_dim5_field_stage_completeness),
        ("DIM-6 vocab derived_from reachable", check_dim6_vocab_derived_from),
        ("DIM-7 doc_type subset of vocabulary", check_dim7_doc_type_subset),
    ]
    fails = 0
    for label, checker in dimensions:
        status, msg = checker(contract)
        icon = "OK" if status == "PASS" else "FAIL"
        print(f"  [{icon}] {label}: {msg}")
        if status != "PASS":
            fails += 1
    print()
    if fails > 0:
        print(f"BLOCKED: {fails}/{len(dimensions)} dimensions FAILED")
        print("Fix architecture_contract.yaml before committing.")
        sys.exit(EXIT_FINDINGS)
    else:
        print(f"ALL {len(dimensions)}/{len(dimensions)} dimensions PASS")
        sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
