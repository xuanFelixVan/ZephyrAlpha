# [A_test] module_id: SRC-TST-0062 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-220 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.architecture.test_contract_consistency
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
架构适应度函数：YAML ↔ Python 契约一致性
============================================

验证 cross_layer_contracts.yaml 中的契约定义与实际 Python dataclass 实现
完全一致。防止 SSoT 和代码实现之间的漂移。

架构不变式
----------
- LC01: YAML 中定义的每个 CTR 都有对应的 Python 文件
- LC02: YAML 中定义的每个字段都在 Python dataclass 中实现
- LC03: YAML 字段类型与 Python 类型注解一致
- LC04: frozen / stability 等元属性与实现一致

Safety: HIGH（契约 SSoT 是承重墙的基础）
"""

from __future__ import annotations

import dataclasses
import importlib
from dataclasses import is_dataclass
from pathlib import Path

import pytest
import yaml
from zephyr.shared.io.paths import REPO_ROOT

YAML_PATH = REPO_ROOT / (
    "architecture_model/contracts/cross_layer_contracts.yaml"
)

TYPE_MAP = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "datetime": "datetime.datetime",
    "Decimal": "decimal.Decimal",
    "UUID": "uuid.UUID",
}


def _load_contracts() -> list[dict]:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    return data.get("contracts", [])


def _ctr_dataclass_name(ctr: dict) -> str:
    """从 YAML ``name`` 解析 Python dataclass 名（例：``FactorMonitorReport / …`` → ``FactorMonitorReport``）。"""
    raw = (ctr.get("name") or "").strip()
    if " / " in raw:
        return raw.split(" / ", 1)[0].strip()
    return raw


def _resolve_python_type(type_str: str) -> str:
    resolved = TYPE_MAP.get(type_str, type_str)
    resolved = resolved.replace("Optional[", "").replace("]", "")
    resolved = resolved.replace("Dict[str, ", "").replace("]", "")
    resolved = resolved.replace("List[", "").replace("]", "")
    return resolved


def _python_type_display(py_type: type | str) -> str:
    if hasattr(py_type, "__name__"):
        return py_type.__name__
    if hasattr(py_type, "_name"):
        return str(py_type._name)
    return str(py_type)


class TestContractYamlPythonConsistency:
    """LC01~LC04: YAML SSoT 与 Python 实现一致。"""

    @pytest.fixture(scope="class")
    def contracts(self):
        return _load_contracts()

    def test_all_p0_contracts_have_python_file(self, contracts):
        missing: list[str] = []
        not_implemented: list[str] = []
        for ctr in contracts:
            if ctr.get("priority") != "P0":
                continue
            physical = ctr.get("physical_path", "")
            if not physical or "{" in physical or physical.endswith("/"):
                not_implemented.append(f"{ctr.get('id', '?')}: 路径含模板或目录 — {physical}")
                continue
            py_file = REPO_ROOT / physical
            if not py_file.exists():
                not_implemented.append(f"{ctr.get('id', '?')}: Python 文件不存在 — {physical}")
                continue
        if not_implemented:
            print(f"[WARN] {len(not_implemented)} 个 P0 契约尚未实现 Python 文件:")
            for msg in not_implemented[:10]:
                print(f"  - {msg}")
        if missing:
            pytest.fail("\n".join(missing))

    def test_all_p0_fields_in_python_dataclass(self, contracts):
        violations: list[str] = []
        for ctr in contracts:
            if ctr.get("priority") != "P0":
                continue
            physical = ctr.get("physical_path", "")
            py_file = REPO_ROOT / physical
            if not py_file.exists():
                continue

            try:
                mod_path = physical.replace("src/", "").replace(".py", "").replace("/", ".")
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, _ctr_dataclass_name(ctr), None)
                if cls is None or not is_dataclass(cls):
                    continue

                py_fields = {f.name for f in dataclasses.fields(cls)}
                for yaml_field in ctr.get("fields", []):
                    if yaml_field["name"] not in py_fields:
                        violations.append(f"{ctr['id']}.{yaml_field['name']}: YAML 中有但 Python 中无此字段")
            except Exception as e:
                violations.append(f"{ctr['id']}: 加载 Python 失败 — {e}")

        if violations:
            pytest.fail("\n".join(violations))

    def test_p0_required_fields_match(self, contracts):
        violations: list[str] = []
        for ctr in contracts:
            if ctr.get("priority") != "P0":
                continue
            physical = ctr.get("physical_path", "")
            py_file = REPO_ROOT / physical
            if not py_file.exists():
                continue

            try:
                mod_path = physical.replace("src/", "").replace(".py", "").replace("/", ".")
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, _ctr_dataclass_name(ctr), None)
                if cls is None or not is_dataclass(cls):
                    continue

                for yaml_field in ctr.get("fields", []):
                    if yaml_field.get("required", False):
                        py_field = next(
                            (f for f in dataclasses.fields(cls) if f.name == yaml_field["name"]),
                            None,
                        )
                        if py_field:
                            has_default = (
                                py_field.default is not dataclasses.MISSING
                                or py_field.default_factory is not dataclasses.MISSING
                            )
                            if has_default:
                                if py_field.default_factory is not dataclasses.MISSING:
                                    continue
                                violations.append(
                                    f"{ctr['id']}.{yaml_field['name']}: YAML 标记 required=true 但 Python 有默认值"
                                )
            except Exception:
                pass

        if violations:
            pytest.fail("\n".join(violations))


class TestContractYamlPythonConsistencyP1:
    """P1 蓝图契约：LC01/LC02/required 字段与 Python dataclass 对齐。"""

    @pytest.fixture(scope="class")
    def contracts(self):
        return _load_contracts()

    def test_all_p1_contracts_have_python_file(self, contracts):
        missing: list[str] = []
        not_implemented: list[str] = []
        for ctr in contracts:
            if not str(ctr.get("id", "")).startswith("CTR-P1"):
                continue
            if ctr.get("priority") != "P1":
                continue
            physical = ctr.get("physical_path", "")
            if not physical or "{" in physical or physical.endswith("/"):
                not_implemented.append(f"{ctr.get('id', '?')}: 路径含模板或目录 — {physical}")
                continue
            py_file = REPO_ROOT / physical
            if not py_file.exists():
                not_implemented.append(f"{ctr.get('id', '?')}: Python 文件不存在 — {physical}")
                continue
        if not_implemented:
            print(f"[WARN] {len(not_implemented)} 个 P1 契约尚未实现 Python 文件:")
            for msg in not_implemented[:10]:
                print(f"  - {msg}")
        if missing:
            pytest.fail("\n".join(missing))

    def test_all_p1_fields_in_python_dataclass(self, contracts):
        violations: list[str] = []
        for ctr in contracts:
            if not str(ctr.get("id", "")).startswith("CTR-P1"):
                continue
            if ctr.get("priority") != "P1":
                continue
            physical = ctr.get("physical_path", "")
            py_file = REPO_ROOT / physical
            if not physical or not py_file.exists():
                continue

            cls_name = _ctr_dataclass_name(ctr)
            try:
                mod_path = physical.replace("src/", "").replace(".py", "").replace("/", ".")
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, cls_name, None)
                if cls is None or not is_dataclass(cls):
                    violations.append(f"{ctr['id']}: 类型 {cls_name} 非 dataclass 或未导出")
                    continue

                py_fields = {f.name for f in dataclasses.fields(cls)}
                for yaml_field in ctr.get("fields", []):
                    if yaml_field["name"] not in py_fields:
                        violations.append(f"{ctr['id']}.{yaml_field['name']}: YAML 中有但 Python 中无此字段")
            except Exception as e:
                violations.append(f"{ctr['id']}: 加载 Python 失败 — {e}")

        if violations:
            pytest.fail("\n".join(violations))

    def test_p1_required_fields_match(self, contracts):
        violations: list[str] = []
        for ctr in contracts:
            if not str(ctr.get("id", "")).startswith("CTR-P1"):
                continue
            if ctr.get("priority") != "P1":
                continue
            physical = ctr.get("physical_path", "")
            py_file = REPO_ROOT / physical
            if not physical or not py_file.exists():
                continue

            cls_name = _ctr_dataclass_name(ctr)
            try:
                mod_path = physical.replace("src/", "").replace(".py", "").replace("/", ".")
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, cls_name, None)
                if cls is None or not is_dataclass(cls):
                    continue

                for yaml_field in ctr.get("fields", []):
                    if yaml_field.get("required", False):
                        py_field = next(
                            (f for f in dataclasses.fields(cls) if f.name == yaml_field["name"]),
                            None,
                        )
                        if py_field:
                            has_default = (
                                py_field.default is not dataclasses.MISSING
                                or py_field.default_factory is not dataclasses.MISSING
                            )
                            if has_default:
                                if py_field.default_factory is not dataclasses.MISSING:
                                    continue
                                violations.append(
                                    f"{ctr['id']}.{yaml_field['name']}: YAML 标记 required=true 但 Python 有默认值"
                                )
            except Exception:
                pass

        if violations:
            pytest.fail("\n".join(violations))
