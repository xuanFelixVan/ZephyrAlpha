"""
validate_architecture.py - Validate rule files against architecture-contract.yaml

Reads architecture-contract.yaml and validates all .md/.yaml files under
01_policies_and_standards/ for compliance with directory, frontmatter,
and consistency rules.

Usage:
    python validate_architecture.py [--contract FILE] [--scan-dir DIR] [--verbose]

    Exit codes:
    1 = one or more errors found
    2 = script error (missing dependencies, bad contract file, etc.)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXCLUDE_DIRS, REPO_ROOT, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter, parse_yaml_header
from _shared.walk import iter_files

ensure_utf8_stdout()
DEFAULT_CONTRACT = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "architecture-contract.yaml"
)
DEFAULT_SCAN_DIR = REPO_ROOT / "docs" / "01_policies_and_standards"

def load_contract(contract_path: str) -> dict[str, Any]:
    """加载合约定义"""
    with open(contract_path, encoding="utf-8") as f:
        return yaml.safe_load(f)

class ValidationResult:
    def __init__(self):
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def add_error(self, rule_id: str, file_path: str, message: str) -> None:
        """add error"""
        self.errors.append({"rule": rule_id, "file": file_path, "message": message})

    def add_warning(self, rule_id: str, file_path: str, message: str) -> None:
        """add warning"""
        self.warnings.append({"rule": rule_id, "file": file_path, "message": message})

    @property
    def has_errors(self) -> bool:
        """has errors"""
        return len(self.errors) > 0

    def summary(self) -> str:
        """生成摘要"""
        lines = [f"Validation Results: {len(self.errors)} errors, {len(self.warnings)} warnings"]
        if self.errors:
            lines.append("\nERRORS:")
            for e in self.errors:
                lines.append(f'  [{e['rule']}] {e['file']}: {e['message']}')
        if self.warnings:
            lines.append("\nWARNINGS:")
            for w in self.warnings:
                lines.append(f'  [{w['rule']}] {w['file']}: {w['message']}')
        if not self.errors and (not self.warnings):
            lines.append("\n✅ All checks passed!")
        return "\n".join(lines)

def get_required_fields_for_doc_type(doc_type: str) -> set[str]:
    """get required fields for doc type"""
    common = {"module_id", "title", "doc_type", "status", "version"}
    rule_doc_fields = common | {
        "layer",
        "owner",
        "classification",
        "language",
        "created_by",
        "date",
        "ttl",
        "summary",
        "tags",
        "rule_form",
        "scope",
        "stability",
        "verifiability",
    }
    mapping = {
        "policy": rule_doc_fields,
        "standard": rule_doc_fields,
        "operational_rule": rule_doc_fields,
        "protocol": rule_doc_fields,
        "register": common,
        "index": {"title", "doc_type", "status", "version"},
        "template": common,
        "terminology": common,
        "vocabulary": {"title", "doc_type", "status"},
        "contract": common,
    }
    return mapping.get(doc_type, common)

def validate_frontmatter(fm: dict, file_path: str, contract: dict, result: ValidationResult):
    """validate frontmatter"""
    fm_schema = contract.get("frontmatter_schema", {})
    doc_type = str(fm.get("doc_type", "")).lower()
    required_fields = get_required_fields_for_doc_type(doc_type)
    for field_name in required_fields:
        val = fm.get(field_name)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            result.add_error("VR-005", file_path, f"Missing required field: {field_name}")
    for field_def in fm_schema.get("required_fields", []):
        name = field_def.get("name", "")
        if not name:
            continue
        val = fm.get(name)
        if val is None:
            continue
        val_str = str(val).lower() if isinstance(val, str) else str(val)
        allowed = [v.lower() for v in field_def.get("allowed_values", [])]
        if val_str not in allowed:
            result.add_error(
                "VR-002" if name == "doc_type" else "VR-005",
                file_path,
                f"Field '{name}' value '{val}' not in allowed values: {field_def['allowed_values']}",
            )
        if "format" in field_def:
            pattern = field_def["format"]
            if not re.match(pattern, str(val)):
                rule = "VR-001" if name == "module_id" else "VR-005"
                result.add_error(rule, file_path, f"Field '{name}' value '{val}' does not match format: {pattern}")
    if fm.get("status", "").lower() == "deprecated":
        if not fm.get("superseded_by"):
            result.add_error("VR-006", file_path, "Deprecated file missing 'superseded_by' field")

def load_rule_form_vocabulary(scan_dir: str) -> dict[str, Any] | None:
    """load rule form vocabulary"""
    vocab_path = Path(scan_dir) / "_registry" / "vocabularies" / "rule_form-vocabulary.yaml"
    if not vocab_path.exists():
        return None
    data = yaml.safe_load(vocab_path.read_text(encoding="utf-8", errors="replace"))
    return data if isinstance(data, dict) else None

def build_doc_type_rule_form_mapping(vocab: dict | None) -> dict[str, str]:
    """build doc type rule form mapping"""
    if not vocab:
        return {}
    mapping: dict[str, str] = {}
    for entry in vocab.get("values", []):
        if not isinstance(entry, dict):
            continue
        rule_form = entry.get("value", "")
        for dt in entry.get("doc_types", []):
            mapping[dt] = rule_form
    return mapping

def validate_doc_type_rule_form_consistency(
    fm: dict, file_path: str, result: ValidationResult, rule_form_mapping: dict[str, str]
):
    """validate doc type rule form consistency"""
    doc_type = str(fm.get("doc_type", "")).lower()
    rule_form = str(fm.get("rule_form", "")).lower()
    if not doc_type or not rule_form:
        return
    if not rule_form_mapping:
        return
    expected = rule_form_mapping.get(doc_type, "")
    if expected and rule_form != expected:
        result.add_error(
            "VR-004", file_path, f"doc_type='{doc_type}' should have rule_form='{expected}', got '{rule_form}'"
        )

def validate_directory_placement(file_rel_path: str, fm: dict, contract: dict, result: ValidationResult):
    """validate directory placement"""
    dir_schema = contract.get("directory_schema", {})
    doc_type = str(fm.get("doc_type", "")).lower()
    parts = Path(file_rel_path).parts
    if len(parts) < 2:
        return
    top_dir = parts[0] if len(parts) > 0 else ""
    if top_dir == "governance":
        if doc_type == "operational_rule":
            result.add_error("VR-008", file_rel_path, "operational_rule file found under governance/ directory")
    elif top_dir == "operational":
        if doc_type != "operational_rule":
            result.add_error("VR-009", file_rel_path, f"{doc_type} file found under operational/ directory")

def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="Validate architecture compliance")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Path to architecture-contract.yaml")
    parser.add_argument("--scan-dir", default=str(DEFAULT_SCAN_DIR), help="Directory to scan")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：发现不阻塞（exit 0）")
    args = parser.parse_args()
    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"ERROR: Contract file not found: {contract_path}", file=sys.stderr)
        sys.exit(2)
    contract = load_contract(str(contract_path))
    if not contract:
        print("ERROR: Failed to load contract file", file=sys.stderr)
        sys.exit(2)
    scan_dir = Path(args.scan_dir)
    if not scan_dir.exists():
        print(f"ERROR: Scan directory not found: {scan_dir}", file=sys.stderr)
        sys.exit(2)
    result = ValidationResult()
    file_count = 0
    rule_form_vocab = load_rule_form_vocabulary(str(scan_dir))
    rule_form_mapping = build_doc_type_rule_form_mapping(rule_form_vocab)
    if args.verbose and rule_form_vocab:
        print(f"  Loaded rule_form vocabulary: {len(rule_form_mapping)} doc_type mappings", file=sys.stderr)
    if args.verbose:
        print(file=sys.stderr)
    for fpath in iter_files(scan_dir, extensions=SCAN_EXTENSIONS_MD_YAML, exclude_dirs=EXCLUDE_DIRS | {".audit_cache"}):
        fname = fpath.name
        rel_path = str(fpath.relative_to(scan_dir)).replace("\\", "/")
        try:
            raw = fpath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError) as e:
            result.add_warning("VR-000", rel_path, f"Cannot read file: {e}")
            continue
        file_count += 1
        if fname.endswith(".md"):
            fm = parse_frontmatter(raw)
        else:
            fm = parse_yaml_header(raw)
        if fm is None:
            if args.verbose:
                print(f"  SKIP (no frontmatter): {rel_path}", file=sys.stderr)
            continue
        if "templates/" in rel_path:
            if args.verbose:
                print(f"  SKIP (template): {rel_path}", file=sys.stderr)
            continue
        if "generated_at" in fm or "auto_generated" in fm:
            if args.verbose:
                print(f"  SKIP (generated): {rel_path}", file=sys.stderr)
            continue
        if rel_path.startswith("domains/") and rel_path.endswith("/index.md"):
            if args.verbose:
                print(f"  SKIP (domain index): {rel_path}", file=sys.stderr)
            continue
        validate_frontmatter(fm, rel_path, contract, result)
        validate_doc_type_rule_form_consistency(fm, rel_path, result, rule_form_mapping)
        validate_directory_placement(rel_path, fm, contract, result)
    print(f"\nScanned {file_count} files in {scan_dir}", file=sys.stderr)
    print(result.summary(), file=sys.stderr)
    if result.has_errors:
        if args.warn_only:
            print(f"\n[RESULT] 发现 {len(result.errors)} 个错误，warn-only 模式继续（exit 0）", file=sys.stderr)
            sys.exit(0)
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
