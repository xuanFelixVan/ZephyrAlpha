# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/generators/generate_contracts.py | §
# [MODULE] scripts.governance.d5_architecture.generators.generate_contracts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.__init__
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
"""
generate_contracts.py -- SSoT to Codegen pipeline

Auto-generate Python dataclass files from cross_layer_contracts.yaml.
"""

from __future__ import annotations

import os

# Manifest metadata for governance scripts
__manifest__ = {
    "args": [],
    "description": "generate_contracts.py -- SSoT to Codegen pipeline",
    "dimensions": ["D5"],
    "priority": "P2",
    "timeout_seconds": 60,
    "warn_only": False,
}

import sys
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # exit codes（scripts/ 侧）
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

import argparse
import re

import yaml

CONTRACTS_YAML = REPO_ROOT / (
    "architecture_model/contracts/cross_layer_contracts.yaml"
)

_TYPE_IMPORTS: dict[str, str] = {
    "datetime": "from datetime import datetime",
    "Decimal": "from decimal import Decimal",
    "UUID": "from uuid import UUID",
    "Optional": "from typing import Optional",
    "List": "from typing import List",
    "Dict": "from typing import Dict",
    "Any": "from typing import Any",
    "TraceContext": "from zephyr.shared.contracts.core.trace_context import TraceContext",
    "OrderSide": "from zephyr.shared.contracts.enums.order_enums import OrderSide",
    "OrderType": "from zephyr.shared.contracts.enums.order_enums import OrderType",
    "OrderStatus": "from zephyr.shared.contracts.enums.order_enums import OrderStatus",
}

_STANDARD_IMPORTS = [
    "from __future__ import annotations",
    "",
    "from dataclasses import dataclass, field",
]

DT_FACTORY_NEEDED = False


def _path_to_module(physical_path: str) -> str:
    """_path_to_module implementation."""
    if not physical_path or not physical_path.endswith(".py"):
        return ""
    rel = physical_path.replace("\\", "/").replace(".py", "")
    if rel.startswith("src/"):
        rel = rel[4:]
    return rel.replace("/", ".")


def _generate_14field_header(physical_path: str) -> str:
    """生成 14 字段规范头部（TRAE-047 v1.1.0），使 codegen 文件天然合规。

    维护项5：模板内置 14 字段头部，避免 upgrade_headers 脚本误判。
    字段值依据 contracts 域约定（cross-layer infrastructure data contracts）。
    """
    module_path = _path_to_module(physical_path)
    lines = [
        "# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md",
        f"# [MODULE] {module_path}",
        "# [DOMAIN] D_INFRASTRUCTURE",
        "# [DEPENDENCIES]",
        "# [CONSUMERS]",
        "# [STARTUP] imported",
        "# [MATURITY] production",
        "# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)",
        "# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py",
        "# [STABILITY] evolving",
        "# [SAFETY] L",
        "# [AI_AUTONOMY] ai_modifiable",
        "# [ERROR_CONTRACT]",
        "# [TESTS]",
    ]
    return "\n".join(lines) + "\n"


def _import_to_module(import_line: str) -> str:
    """_import_to_module implementation."""
    if not import_line.startswith("from "):
        return ""
    after_from = import_line[5:]
    module = after_from.split(" import ")[0].strip()
    return module


def _extract_type_tokens(type_str: str) -> list[str]:
    """_extract_type_tokens implementation."""
    tokens: list[str] = []
    for token in type_str.replace("[", " ").replace("]", " ").replace(",", " ").split():
        token = token.strip()
        if token and token not in ("str", "int", "float", "bool"):
            tokens.append(token)
    return tokens


def _collect_imports(fields: list[dict], physical_path: str = "") -> list[str]:
    """_collect_imports implementation."""
    global DT_FACTORY_NEEDED
    DT_FACTORY_NEEDED = False

    output_module = _path_to_module(physical_path)

    types_needed: set[str] = set()
    for f in fields:
        for token in _extract_type_tokens(f.get("type", "")):
            if token in _TYPE_IMPORTS:
                import_line = _TYPE_IMPORTS[token]
                _import_module = _import_to_module(import_line)
                if _import_module != output_module:
                    types_needed.add(import_line)

        default = f.get("default")
        if default is not None and f.get("type", "") == "datetime":
            DT_FACTORY_NEEDED = True
        if f.get("required") is True and f.get("type", "") == "datetime":
            DT_FACTORY_NEEDED = True
        if f.get("type", "").startswith("Optional[") and "datetime" in f.get("type", ""):
            DT_FACTORY_NEEDED = True

    base_types = {
        t for t in types_needed if "typing" not in t and "decimal" not in t and "datetime" not in t and "uuid" not in t
    }
    stdlib_types = {t for t in types_needed if "typing" in t or "decimal" in t or "datetime" in t or "uuid" in t}

    imports = list(_STANDARD_IMPORTS)
    if stdlib_types:
        imports.append("")
        for t in sorted(stdlib_types):
            imports.append(t)
    if DT_FACTORY_NEEDED and "from datetime import datetime" in stdlib_types:
        idx = imports.index("from datetime import datetime")
        imports[idx] = "from datetime import datetime, timezone"
        if "from datetime import timezone" in imports:
            imports.remove("from datetime import timezone")
    elif DT_FACTORY_NEEDED:
        imports.append("from datetime import datetime, timezone")
    if base_types:
        imports.append("")
        for t in sorted(base_types):
            imports.append(t)

    return imports


def _resolve_base_type(type_str: str) -> str:
    """_resolve_base_type implementation."""
    base = type_str.replace("Optional[", "").replace("]", "").split(",")[0].strip()
    if "[" in base:
        base = base.split("[")[0].strip()
    return base


_STANDARD_TYPES = {"str", "int", "float", "bool", "datetime", "Decimal", "UUID", "Any"}


def _format_default(field: dict) -> str:
    """_format_default implementation."""
    default = field.get("default")
    type_str = field.get("type", "")
    base_type = _resolve_base_type(type_str)
    is_required = field.get("required", True)

    if default is None:
        if type_str.startswith("Optional["):
            return " = None"
        if "List" in type_str or type_str == "List":
            return " = field(default_factory=list)"
        if "Dict" in type_str or type_str == "Dict":
            return " = field(default_factory=dict)"
        if not is_required:
            if base_type == "str":
                return ' = ""'
            elif base_type in ("int", "float"):
                return " = 0"
            elif base_type == "bool":
                return " = False"
        return ""

    if base_type == "Decimal":
        return f' = Decimal("{default}")'
    elif base_type in ("int", "float"):
        return f" = {default}"
    elif base_type == "bool":
        if isinstance(default, bool):
            return f" = {default}"
        return f" = {str(default).capitalize()}"
    elif base_type == "str":
        if default in ("True", "False", "None"):
            return f' = "{default}"'
        return f' = "{default}"'
    elif base_type in ("List", "Dict") or base_type.startswith("List[") or base_type.startswith("Dict["):
        return " = field(default_factory=list)" if "List" in base_type else " = field(default_factory=dict)"
    elif base_type == "datetime":
        return " = field(default_factory=lambda: datetime.now(timezone.utc))"
    elif base_type not in _STANDARD_TYPES:
        if isinstance(default, str):
            return f" = {base_type}.{default}"
        return f" = {default}"
    else:
        return f" = {default}"


def _has_effective_default(field: dict) -> bool:
    """_has_effective_default implementation."""
    if "default" in field:
        return True
    if not field.get("required", True):
        return True
    type_str = field.get("type", "")
    if "List" in type_str or type_str.strip() == "List":
        return True
    if "Dict" in type_str or type_str.strip() == "Dict":
        return True
    if type_str.startswith("Optional["):
        return True
    return False


def _format_ai_prompt(ai_prompt: str, indent: int = 4) -> str:
    """_format_ai_prompt implementation."""
    prefix = " " * indent
    lines = ai_prompt.strip().split("\n")
    return "\n".join(f"{prefix}{line.strip()}" for line in lines)


def _generate_file_header(
    contract_id: str,
    contract_name: str,
    description: str,
    schema_version: str,
    ai_prompt: str,
    physical_path: str,
) -> str:
    """_generate_file_header implementation."""
    filename = Path(physical_path).name

    header = [
        "# ---",
        "# layer: cross_cutting",
        "# category: data_contract",
        "# status: auto_generated",
        f'# created: "{datetime.now(UTC).strftime("%Y-%m-%d")}"',
        "# generated_by: codegen from cross_layer_contracts.yaml",
        "# ---",
        '"""',
        f"ZephyrAlpha — shared/contracts/{filename}",
        "",
        f"{contract_id}: {contract_name}",
        "",
        description,
        "",
        f"SSoT: cross_layer_contracts.yaml -> {contract_id}",
        f"Version: {schema_version}",
        "Status: AUTO-GENERATED -- DO NOT EDIT BY HAND",
        "       Any manual changes will be overwritten by codegen.",
        "",
        "AI Prompt",
        "---------",
    ]

    for line in _format_ai_prompt(ai_prompt).split("\n"):
        header.append(line)

    header.append('"""')
    return "\n".join(header)


def _generate_dataclass(
    contract_id: str,
    contract_name: str,
    is_frozen: bool,
    fields: list[dict],
) -> str:
    """_generate_dataclass implementation."""
    raw_name = contract_name.split(" / ")[0].strip()
    # 安全提取第一个有效 Python 类名（处理 "StrategyBase + StrategyRegistry" 等）
    match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", raw_name)
    class_name = match.group(0) if match else "UnknownContract"
    frozen_str = "frozen=True" if is_frozen else ""

    lines = [
        "",
        "",
        f"@dataclass({frozen_str})" if frozen_str else "@dataclass",
        f"class {class_name}:",
    ]

    if not fields:
        lines.append("    pass")
        return "\n".join(lines)

    indent = " " * 4
    for f in fields:
        fname = f["name"]
        ftype = f["type"]

        if fname == "schema_version":
            version = f.get("default", "1.0")
            lines.append(f'{indent}{fname}: str = "{version}"')
            continue

        default_str = _format_default(f)
        if default_str:
            lines.append(f"{indent}{fname}: {ftype}{default_str}")
        else:
            lines.append(f"{indent}{fname}: {ftype}")

    return "\n".join(lines)


CODGEN_BEGIN = "# ==== BEGIN CODGEN:{contract_id} ===="
CODGEN_END = "# ==== END CODGEN:{contract_id} ===="


def generate_contract_file(ctr: dict, dry_run: bool = False) -> str | None:
    """Generate output from input data."""
    physical = ctr.get("physical_path", "")
    if not physical:
        return None

    contract_id = ctr.get("id", "")

    # 跳过 OCP 扩展点——它们包含多类 + Registry 模式，无法自动生成
    if contract_id.startswith("OCP-"):
        return None
    contract_name = ctr.get("name", "")
    description = ctr.get("description", "")
    schema_version = ctr.get("schema_version", "1.0")
    ai_prompt = ctr.get("ai_prompt", "")
    is_frozen = ctr.get("frozen", True)
    fields = ctr.get("fields", [])

    fields = sorted(fields, key=lambda f: (0 if not _has_effective_default(f) else 1, f.get("name", "")))

    imports = _collect_imports(fields, physical)

    header = _generate_file_header(
        contract_id,
        contract_name,
        description,
        schema_version,
        ai_prompt,
        physical,
    )

    dataclass_code = _generate_dataclass(
        contract_id,
        contract_name,
        is_frozen,
        fields,
    )

    field_header = _generate_14field_header(physical)
    generated_block = field_header + "\n".join(imports[2:]) + "\n" + header + dataclass_code + "\n"
    begin_marker = CODGEN_BEGIN.format(contract_id=contract_id)
    end_marker = CODGEN_END.format(contract_id=contract_id)
    wrapped_content = f"{begin_marker}\n{generated_block}\n{end_marker}\n"

    output_path = REPO_ROOT / physical

    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        if begin_marker in existing and end_marker in existing:
            before = existing[: existing.index(begin_marker)]
            after = existing[existing.index(end_marker) + len(end_marker) :]
            final_content = before + wrapped_content + after
        else:
            # 治本(2026-07-02): 传入class_name, 跳过旧codegen的同名class定义
            raw_name = contract_name.split(" / ")[0].strip()
            _class_match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", raw_name)
            _contract_class_name = _class_match.group(0) if _class_match else ""
            pre_existing = _extract_hand_maintained(existing, begin_marker, _contract_class_name)
            final_content = pre_existing + "\n" + wrapped_content
    else:
        final_content = wrapped_content

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not dry_run:
        atomic_write_safe(output_path, final_content)
        print(f"  ✅ {physical}")

    return str(output_path)


def _extract_hand_maintained(source: str, begin_marker: str, contract_class_name: str = "") -> str:
    """提取手写维护的代码（BEGIN CODGEN标记之前），跳过旧codegen的同名class定义。

    治本(2026-07-02): 移除@dataclass的过早break（原逻辑遇到任何@dataclass就停止提取，
    导致手写的FactorDiscovery/BacktestEngineBase等被丢弃）。改为跳过与当前contract
    同名的class定义块（旧codegen产物），保留其他所有手写代码。
    修复engine_base.py案例：codegen覆盖手写BacktestEngineBase+FactorDiscovery的问题。
    """
    lines = source.rstrip().split("\n")
    result: list[str] = []
    skipping_old_class = False  # 正在跳过旧codegen的同名class body

    for line in lines:
        stripped = line.strip()
        if begin_marker in stripped:
            break

        if skipping_old_class:
            # 跳过class body（缩进行/空行/注释），遇到下一个顶层定义时停止
            if stripped and not line[0].isspace() and not stripped.startswith("#"):
                skipping_old_class = False
                # 不continue，继续处理当前行
            else:
                continue

        # 跳过与当前contract同名的class定义（旧codegen产物）
        if contract_class_name and stripped.startswith(f"class {contract_class_name}"):
            skipping_old_class = True
            # 移除前面已添加的装饰器（@dataclass等）
            while result and result[-1].strip().startswith("@"):
                result.pop()
            continue

        # 原有跳过逻辑（import、注释等）
        if stripped.startswith("from __future__"):
            continue
        if stripped.startswith("from dataclasses import"):
            continue
        if stripped.startswith("from datetime import"):
            continue
        if stripped.startswith("from decimal import"):
            continue
        if stripped.startswith("from typing import"):
            continue
        if stripped.startswith("from enum import"):
            result.append(line)
            continue
        if stripped.startswith("from zephyr.shared.contracts"):
            continue
        if stripped.startswith("# ---"):
            continue
        if stripped.startswith("# ["):
            continue
        if (
            stripped.startswith("# layer:")
            or stripped.startswith("# category:")
            or stripped.startswith("# status:")
            or stripped.startswith("# created:")
            or stripped.startswith("# generated_by:")
        ):
            continue
        if stripped.startswith('"""') or stripped.startswith("ZephyrAlpha"):
            continue
        result.append(line)

    while result and not result[-1].strip():
        result.pop()

    return "\n".join(result).rstrip() + "\n"


def _extract_public_symbols(file_path: Path) -> list[str]:
    """从 Python 文件中提取公开符号（class/def/常量），用于生成显式导入。

    5.93.6: 替代 ``from .xxx import *``，消除命名空间污染。
    优先解析 ``__all__``；无 ``__all__`` 时提取不以 ``_`` 开头的 class/def/常量。
    """
    if not file_path.exists():
        return []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return []
    # 优先解析 __all__
    all_match = re.search(r"^__all__\s*=\s*\[(.*?)\]", content, re.MULTILINE | re.DOTALL)
    if all_match:
        names = re.findall(r'"(\w+)"', all_match.group(1))
        return [n for n in names if not n.startswith("_")]
    # 无 __all__：提取公开 class/def/常量
    symbols: list[str] = []
    for line in content.splitlines():
        m = re.match(r"^class (\w+)", line)
        if m:
            symbols.append(m.group(1))
            continue
        m = re.match(r"^def (\w+)", line)
        if m and not m.group(1).startswith("_"):
            symbols.append(m.group(1))
            continue
        m = re.match(r"^([A-Z][A-Za-z0-9_]*)\s*=", line)
        if m:
            symbols.append(m.group(1))
    return symbols


def generate_directory_init(directory: Path, module_names: list[str], dry_run: bool = False) -> None:
    """Generate output from input data."""
    init_file = directory / "__init__.py"
    if init_file.exists():
        existing = init_file.read_text(encoding="utf-8")
        if "CODEGEN-GUARD: CTR-declarations-manual" in existing:
            print(f"  [Codegen] SKIP {init_file} (CODEGEN-GUARD active)")
            return
    init_lines = [
        '"""',
        f"Auto-generated contracts package — {directory.name}",
        "",
        "Generated by: scripts/governance/d5_architecture/generate_contracts.py",
        '"""',
        "",
    ]
    for name in sorted(module_names):
        # 5.93.6: 显式导入替代 import *（消除命名空间污染）
        symbols = _extract_public_symbols(directory / f"{name}.py")
        if symbols:
            symbols_str = ", ".join(symbols)
            init_lines.append(f"from .{name} import {symbols_str}")
        else:
            # fallback: 无法提取符号时保留 import *
            init_lines.append(f"from .{name} import *  # noqa: F403")

    # DM-367: 显式 __all__ 用模块名（snake_case），满足 audit_registration 的
    # `module_name in registered[pkg]` 检查（PascalCase 推导在 system-telemetry 等命名不匹配场景会失败）
    init_lines.append("")
    init_lines.append("__all__ = [")
    for name in sorted(module_names):
        init_lines.append(f'    "{name}",')
    init_lines.append("]")

    content = "\n".join(init_lines) + "\n"
    if not dry_run:
        atomic_write_safe(init_file, content)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="SSoT-to-Codegen: YAML -> Python dataclass auto-generator")
    parser.add_argument("--contract", type=str, help="仅生成指定契约（如 CTR-001）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入磁盘")
    parser.add_argument("--force", action="store_true", help="强制覆盖（跳过冻结检查）")
    args = parser.parse_args()

    if not args.force:
        init_py = REPO_ROOT / "src" / "zephyr" / "shared" / "contracts" / "__init__.py"
        if init_py.exists():
            first_line = init_py.read_text(encoding="utf-8").split("\n")[0]
            if "CODEGEN-GUARD" in first_line:
                print("[Codegen] SKIPPED — CODEGEN-GUARD active in shared/contracts/__init__.py")
                print("  Phase D codegen freeze is active. Use --force to override.")
                sys.exit(EXIT_PASS)

    if args.dry_run:
        print("[Codegen] DRY-RUN 模式 — 不会写入任何文件\n")

    if not CONTRACTS_YAML.exists():
        print(f"[Codegen] ERROR: {CONTRACTS_YAML} 不存在", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    data = yaml.safe_load(CONTRACTS_YAML.read_text(encoding="utf-8"))
    contracts = data.get("contracts", [])

    generated_count = 0
    skipped_count = 0

    subdir_modules: dict[str, list[str]] = {}

    for ctr in contracts:
        cid = ctr.get("id", "")
        if args.contract and cid != args.contract:
            continue

        physical = ctr.get("physical_path", "")
        if not physical:
            skipped_count += 1
            continue

        print(f"[Codegen] {cid} — {ctr.get('name', '')}")

        output_path = generate_contract_file(ctr, dry_run=args.dry_run)
        if output_path:
            generated_count += 1
            parent = Path(output_path).parent
            if parent != REPO_ROOT / "src/zephyr/shared/contracts":
                subdir_key = str(parent)
                mod_name = Path(output_path).stem
                subdir_modules.setdefault(subdir_key, []).append(mod_name)

    for subdir, modules in subdir_modules.items():
        generate_directory_init(Path(subdir), modules, dry_run=args.dry_run)

    print(f"\n[Codegen] 完成 — 生成 {generated_count} 个文件, 跳过 {skipped_count} (无 physical_path)")

    if not args.dry_run:
        print("\n[Codegen] 下一步:")
        print("  1. python scripts/context/generate_architecture_context.py  # 重生成上下文")
        print("  2. python -m pytest tests/architecture/ -v                   # 验证一致性")

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
