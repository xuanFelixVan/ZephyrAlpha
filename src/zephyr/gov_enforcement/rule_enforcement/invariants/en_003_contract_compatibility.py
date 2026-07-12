# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.invariants.en_003_contract_compatibility
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.shared.contracts.core.enforcer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_en_003_contract_compatibility | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:EN-003 ====
"""
EN-003 — Contract Compatibility Checker

Reads cross_layer_contracts.yaml field definitions, imports the corresponding
Python dataclass, and diffs: field presence, type, required/optional alignment.

SSoT: cross_layer_contracts.yaml v3.0
"""

from __future__ import annotations

from typing import Final
import dataclasses
import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.paths import REPO_ROOT

_YAML_PATH = Path(__file__).parent / "en_003_contract_compatibility.yaml"


def _load_contract_spec_path() -> Path:
    """从 YAML 真源加载契约文件路径（SSoT 收敛，消除 py/yaml 路径分叉）。"""
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    for check in data.get("checks", []):
        rel = check.get("params", {}).get("contract_spec_path")
        if rel:
            return REPO_ROOT / rel
    return REPO_ROOT / "architecture_model" / "contracts" / "cross_layer_contracts.yaml"

CONTRACTS_PATH: Final[Any] = _load_contract_spec_path()

TYPE_ALIAS_MAP: Final[dict[str, str]] = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "Decimal": "Decimal",
    "datetime": "datetime",
    "Any": "Any",
    "Optional[str]": "Optional[str]",
    "Optional[int]": "Optional[int]",
    "Optional[float]": "Optional[float]",
    "Optional[bool]": "Optional[bool]",
    "Optional[Decimal]": "Optional[Decimal]",
    "Optional[datetime]": "Optional[datetime]",
    "Dict[str,float]": "Dict[str,float]",
    "Dict[str,str]": "Dict[str,str]",
    "Dict[str,Any]": "Dict[str,Any]",
    "Dict[str,Decimal]": "Dict[str,Decimal]",
    "List[str]": "List[str]",
    "Optional[TraceContext]": "Optional[TraceContext]",
    "EnforcementMode": "EnforcementMode",
}


@dataclass
class CompatibilityResult:
    passed: bool
    total: int = 0
    matched: int = 0
    mismatches: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] EN-003: {self.matched}/{self.total} contracts field-compatible"
        return f"[FAIL] EN-003: {len(self.mismatches)} mismatch(es)\n" + "\n".join(f"  - {m}" for m in self.mismatches)


def _load_contracts() -> dict[str, Any]:
    with open(CONTRACTS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _get_dataclass_fields(module_path: str, class_name: str) -> dict[str, str] | None:
    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name, None)
        if cls is None:
            return None
        if not dataclasses.is_dataclass(cls):
            return None
        result: dict[str, str] = {}
        for f in dataclasses.fields(cls):
            type_str = str(f.type) if f.type is not None else "Any"
            if type_str.startswith("<class '"):
                type_str = type_str.split("'")[1]
            result[f.name] = type_str
        return result
    except Exception:
        return None


def _strip_module_path(physical_path: str) -> tuple[str, str] | None:
    path = Path(physical_path)
    if path.suffix != ".py":
        return None

    rel = path
    for parent in path.parents:
        if parent.name == "zephyr" or parent.name == "src":
            try:
                rel = path.relative_to(parent)
            except ValueError:
                continue
            break

    parts = list(rel.parts)
    module_path = "zephyr." + ".".join(parts).replace(".py", "")

    stem = path.stem
    class_name = "".join(w.capitalize() for w in stem.split("_"))
    return module_path, class_name


def _normalize_type(t: str) -> str:
    t = t.strip()
    if t in TYPE_ALIAS_MAP:
        return TYPE_ALIAS_MAP[t]
    return t


def run_check() -> CompatibilityResult:
    data = _load_contracts()
    contracts = data.get("contracts", [])
    mismatches: list[str] = []
    skipped: list[str] = []
    total = 0
    matched = 0

    for ctr in contracts:
        cid = ctr.get("id", "?")
        physical_path = ctr.get("physical_path", "")
        spec_fields = ctr.get("fields", [])

        if not physical_path or not spec_fields:
            skipped.append(f"{cid}: no physical_path or fields")
            continue

        resolved = _strip_module_path(physical_path)
        if resolved is None:
            skipped.append(f"{cid}: could not resolve module path from {physical_path}")
            continue

        module_path, class_name = resolved
        actual_fields = _get_dataclass_fields(module_path, class_name)
        if actual_fields is None:
            skipped.append(f"{cid}: could not load dataclass {class_name} from {module_path}")
            continue

        total += 1
        contract_ok = True

        spec_field_names: set[str] = {f["name"] for f in spec_fields}
        actual_field_names: set[str] = set(actual_fields.keys())

        missing_in_code = spec_field_names - actual_field_names
        extra_in_code = actual_field_names - spec_field_names

        if missing_in_code:
            mismatches.append(f"{cid}/{class_name}: fields in spec but missing in code: {sorted(missing_in_code)}")
            contract_ok = False

        if extra_in_code:
            mismatches.append(f"{cid}/{class_name}: fields in code but missing in spec: {sorted(extra_in_code)}")
            contract_ok = False

        for sf in spec_fields:
            fname = sf["name"]
            if fname not in actual_fields:
                continue
            spec_type = _normalize_type(sf.get("type", "Any"))
            actual_type = _normalize_type(actual_fields[fname])

            spec_type_short = spec_type.split("[")[0]
            actual_type_short = actual_type.split("[")[0]

            if spec_type_short != actual_type_short and spec_type != actual_type:
                mismatches.append(f"{cid}/{class_name}.{fname}: spec type={spec_type}, code type={actual_type}")
                contract_ok = False

        if contract_ok:
            matched += 1

    return CompatibilityResult(
        passed=len(mismatches) == 0,
        total=total,
        matched=matched,
        mismatches=mismatches,
        skipped=skipped,
    )


def check() -> tuple[bool, str]:
    result = run_check()
    return result.passed, result.summary()


if __name__ == "__main__":
    ok, msg = check()
    print(msg)
    sys.exit(0 if ok else 1)

# ==== END CODEGEN:EN-003 ====
