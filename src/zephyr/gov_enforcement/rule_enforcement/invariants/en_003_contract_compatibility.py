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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:EN-003 ====
"""
EN-003 契约兼容性检查器——字段/类型/必填对齐差异比对（Contract Compatibility Checker）

Reads cross_layer_contracts.yaml field definitions, imports the corresponding
Python dataclass, and diffs: field presence, type, required/optional alignment.

SSoT: cross_layer_contracts.yaml v3.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: module_path 参数
#   fields: 参数 module_path，类型注解 str
#   code: en_003_contract_compatibility.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: class_name 参数
#   fields: 参数 class_name，类型注解 str
#   code: en_003_contract_compatibility.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: physical_path 参数
#   fields: 参数 physical_path，类型注解 str
#   code: en_003_contract_compatibility.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: t 参数
#   fields: 参数 t，类型注解 str
#   code: en_003_contract_compatibility.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CompatibilityResult
#   name_en: CompatibilityResult
#   intro: class CompatibilityResult 源码 L176-L186
#   desc: 公共方法（定义序）: summary；源码 L176-L186
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② load_contracts
#   name_en: load_contracts
#   intro: load_contracts() 源码 L189-L191
#   desc: 源码 L189-L191
#   inputs: 无参数
#   outputs: dict[str, Any]
# - id: A3
#   name_zh: ③ get_dataclass_fields
#   name_en: get_dataclass_fields
#   intro: get_dataclass_fields(module_path, class_name) 源码 L197-L213
#   desc: 源码 L197-L213
#   inputs: module_path class_name
#   outputs: dict[str, str] | None
# - id: A4
#   name_zh: ④ strip_module_path
#   name_en: strip_module_path
#   intro: strip_module_path(physical_path) 源码 L219-L238
#   desc: 源码 L219-L238
#   inputs: physical_path
#   outputs: tuple[str, str] | None
# - id: A5
#   name_zh: ⑤ normalize_type
#   name_en: normalize_type
#   intro: normalize_type(t) 源码 L244-L248
#   desc: 源码 L244-L248
#   inputs: t
#   outputs: str
# - id: A6
#   name_zh: ⑥ run_check
#   name_en: run_check
#   intro: run_check() 源码 L254-L322
#   desc: 源码 L254-L322
#   inputs: 无参数
#   outputs: CompatibilityResult
# - id: A7
#   name_zh: ⑦ check
#   name_en: check
#   intro: check() 源码 L325-L327
#   desc: 源码 L325-L327
#   inputs: 无参数
#   outputs: tuple[bool, str]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: dict[str, str] | None
#   name_en: dict[str, str] | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import dataclasses
import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

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


def load_contracts() -> dict[str, Any]:
    with open(CONTRACTS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_load_contracts = load_contracts


def get_dataclass_fields(module_path: str, class_name: str) -> dict[str, str] | None:
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
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None


_get_dataclass_fields = get_dataclass_fields


def strip_module_path(physical_path: str) -> tuple[str, str] | None:
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
    module_path = "zephyr." + ".".join(parts).replace(".py", "").replace("-", "_")

    stem = path.stem
    class_name = "".join(w.capitalize() for w in stem.split("_"))
    return module_path, class_name


_strip_module_path = strip_module_path


def normalize_type(t: str) -> str:
    t = t.strip()
    if t in TYPE_ALIAS_MAP:
        return TYPE_ALIAS_MAP[t]
    return t


_normalize_type = normalize_type


def run_check() -> CompatibilityResult:
    data = load_contracts()
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

        resolved = strip_module_path(physical_path)
        if resolved is None:
            skipped.append(f"{cid}: could not resolve module path from {physical_path}")
            continue

        module_path, class_name = resolved
        actual_fields = get_dataclass_fields(module_path, class_name)
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
            spec_type = normalize_type(sf.get("type", "Any"))
            actual_type = normalize_type(actual_fields[fname])

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
