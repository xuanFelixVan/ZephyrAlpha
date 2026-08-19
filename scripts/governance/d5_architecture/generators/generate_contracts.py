# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/generators/generate_contracts.py | §
# [MODULE] scripts.governance.d5_architecture.generators.generate_contracts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
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
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# 治本（#ARCH-REGEN-NONIDEMPOTENT-001）：generators 目录加入 sys.path，
# in-process 加载（reconciler/tests）时 _common 可解析（正典先例：generate_data_acquisition_flow.py）
_GEN_DIR = str(_SCRIPT_DIR.parent)
if _GEN_DIR not in sys.path:
    sys.path.insert(0, _GEN_DIR)

from _common import idempotent_date  # noqa: E402  幂等日期源（消除实时时间源非确定性）
from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # exit codes（scripts/ 侧）
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

ensure_utf8_stdout()

import argparse
import re

import yaml

CONTRACTS_YAML = REPO_ROOT / ("architecture_model/contracts/cross_layer_contracts.yaml")

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
    "RiskLimits": "from zephyr.shared.contracts.risk_limits import RiskLimits",
}

DT_FACTORY_NEEDED = False


def _split_top_level(s: str) -> list[str]:
    """按顶层逗号切分泛型参数串（嵌套 [] 内的逗号不切）。"""
    parts: list[str] = []
    depth = 0
    cur = ""
    for ch in s:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def _modernize_type(type_str: str) -> str:
    """YAML 类型串 → py312 现代化形态（dict/list/X | None），与 ruff UP006/UP045 输出一致。

    治本（#ARCH-130 P0-A，2026-08-19）：生成器直出现代化类型，使 B 管线 UP006/UP045
    零动作——若直出旧形态（Dict[str, X]），ruff fix 改注解时会连带清理 typing import
    行（符号 unused 判定），而 HEAD 基准含 typing 残留行（F401 全局 ignore 不删），
    产物与基准 diff 非零=幂等破坏。typing import 行照常收集渲染（unused 无害，
    与 HEAD 基准形态对齐）。
    """
    s = type_str.strip()
    m = re.fullmatch(r"Optional\[(.+)\]", s)
    if m:
        return f"{_modernize_type(m.group(1))} | None"
    m = re.fullmatch(r"(Dict|List)\[(.+)\]", s)
    if m:
        kind, inner = m.group(1), m.group(2)
        modern_inner = ", ".join(_modernize_type(p.strip()) for p in _split_top_level(inner))
        return f"{'dict' if kind == 'Dict' else 'list'}[{modern_inner}]"
    # array[{...}] → list[dict[str, Any]]（YAML 描述性对象数组，CTR-P1-017 实证：
    # 直出 `array[{...}]`=非法 Python 类型，required=false 时默认值推导矛盾=
    # TypeError: non-default argument follows default argument）
    m = re.fullmatch(r"array\[(.+)\]", s, re.DOTALL)
    if m:
        inner = m.group(1).strip()
        if inner.startswith("{"):
            return "list[dict[str, Any]]"
        return f"list[{_modernize_type(inner)}]"
    if s in ("Dict", "List"):
        return s.lower()
    if s == "array":
        return "list"
    return s


def _parse_import_map(text: str) -> dict[str, set[str]]:
    """把文本中的 import 行解析为 {module: {symbol, ...}} 语义映射。

    治本（#ARCH-130 P0-A，2026-08-19）：替代整行字符串比对。ruff I001 会把
    `from typing import Dict` + `from typing import Optional` 合并为一行，
    整行比对必误判 missing（position.py 等 43 文件实证）；语义级对行形态免疫。
    - 多行 import（from x import (\\n A,\\n)）重组为逻辑行再解析
    - as 别名取原名（from x import y as z → symbol=y）
    - 裸 import x → 空符号集占位（渲染时输出 import x）
    """
    logical: list[str] = []
    buf = ""
    depth = 0
    for raw in text.splitlines():
        s = raw.strip()
        if buf:
            buf += " " + s
            depth += s.count("(") - s.count(")")
            if depth <= 0:
                logical.append(buf)
                buf = ""
            continue
        if s.startswith(("from ", "import ")):
            depth = s.count("(") - s.count(")")
            if depth > 0:
                buf = s
            else:
                logical.append(s)
    if buf:
        logical.append(buf)

    result: dict[str, set[str]] = {}
    for line in logical:
        if line.startswith("import "):
            result.setdefault(line[7:].strip(), set())
            continue
        m = re.match(r"from\s+(\S+)\s+import\s+(.+)", line)
        if not m:
            continue
        module, syms_raw = m.group(1), m.group(2).replace("(", " ").replace(")", " ")
        syms = {p.strip().split(" as ")[0].strip() for p in syms_raw.split(",") if p.strip()}
        result.setdefault(module, set()).update(syms)
    return result


def _render_import_block(import_map: dict[str, set[str]]) -> list[str]:
    """{module: symbols} → ruff I001 兼容形态：stdlib 组 + first-party 组，组间空行；
    组内模块字母序，同模块符号合并单行（sorted）——与 ruff 安全修复批输出形态对齐。"""
    stdlib: list[str] = []
    first_party: list[str] = []
    for module in sorted(import_map):
        syms = import_map[module]
        line = f"import {module}" if not syms else f"from {module} import {', '.join(sorted(syms))}"
        top = module.split(".")[0]
        (stdlib if top in sys.stdlib_module_names else first_party).append(line)
    lines: list[str] = list(stdlib)
    if stdlib and first_party:
        lines.append("")
    lines.extend(first_party)
    return lines


def _union_import_map(base: dict[str, set[str]], extra_text: str) -> dict[str, set[str]]:
    """把 extra_text 中的 import 语义并入 base（符号级并集，宁多勿缺）。

    治本（#ARCH-130 P0-A）：手写区（before/after）额外符号需求（Any/ClassVar/asdict 等）
    超出 YAML 字段类型推导覆盖，生成区 imports 整体替换后断供=NameError（engine_base.py /
    result_repository.py 实证）。语义级并集防断供且对 ruff 行形态免疫。
    """
    extra = _parse_import_map(extra_text)
    extra.pop("__future__", None)  # __future__ 只能居文件首部，不并入生成区
    merged = {m: set(s) for m, s in base.items()}
    for mod, syms in extra.items():
        if syms:
            merged.setdefault(mod, set()).update(syms)
        else:
            merged.setdefault(mod, set())
    return merged


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
        "# [TTL] permanent",
    ]
    return "\n".join(lines) + "\n"


def _extract_type_tokens(type_str: str) -> list[str]:
    """_extract_type_tokens implementation."""
    tokens: list[str] = []
    for token in type_str.replace("[", " ").replace("]", " ").replace(",", " ").split():
        token = token.strip()
        if token and token not in ("str", "int", "float", "bool"):
            tokens.append(token)
    return tokens


def _collect_import_map(fields: list[dict], physical_path: str = "") -> dict[str, set[str]]:
    """YAML 字段类型 → {module: {symbol}} import 语义映射（含 dataclasses 基础项）。

    治本（#ARCH-130 P0-A，2026-08-19）：返回语义映射而非行列表——同模块符号由
    _render_import_block 合并单行（与 ruff I001 输出同形态），消除整行比对误判源。
    typing 旧符号（Dict/List/Optional）照常收集：字段注解经 _modernize_type 现代化后
    这些 import 属 unused，但 HEAD 基准含残留行（F401 全局 ignore），保留=diff 零。
    """
    global DT_FACTORY_NEEDED
    DT_FACTORY_NEEDED = False

    output_module = _path_to_module(physical_path)

    import_map: dict[str, set[str]] = {"dataclasses": {"dataclass", "field"}}
    for f in fields:
        raw_type = f.get("type", "")
        # 原始串 + 现代化串双程提取：array[{...}]→list[dict[str, Any]] 的 Any
        # 仅存在于现代化串，单程提取会漏 import=NameError（CTR-P1-017 实证）
        for token in _extract_type_tokens(raw_type) + _extract_type_tokens(_modernize_type(raw_type)):
            if token in _TYPE_IMPORTS:
                m = re.match(r"from\s+(\S+)\s+import\s+(.+)", _TYPE_IMPORTS[token])
                if m and m.group(1) != output_module:
                    import_map.setdefault(m.group(1), set()).add(m.group(2).strip())

        ftype = f.get("type", "")
        if f.get("default") is not None and ftype == "datetime":
            DT_FACTORY_NEEDED = True
        if f.get("required") is True and ftype == "datetime":
            DT_FACTORY_NEEDED = True
        if ftype.startswith("Optional[") and "datetime" in ftype:
            DT_FACTORY_NEEDED = True

    if DT_FACTORY_NEEDED and "datetime" in import_map:
        import_map["datetime"].add("timezone")

    return import_map


def _resolve_base_type(type_str: str) -> str:
    """解析基础类型名（兼容现代化 `X | None` 与旧 `Optional[X]` 双形态）。"""
    base = type_str.split("|")[0].strip()  # 现代化形态:TraceContext | None → TraceContext
    base = base.replace("Optional[", "").replace("]", "").split(",")[0].strip()
    if "[" in base:
        base = base.split("[")[0].strip()
    return base


_STANDARD_TYPES = {"str", "int", "float", "bool", "datetime", "Decimal", "UUID", "Any"}


def _is_optional_like(type_str: str) -> bool:
    """Optional 双形态判定：旧 `Optional[X]` / 现代化 `X | None`。"""
    return type_str.startswith("Optional[") or "| None" in type_str


def _is_list_like(type_str: str) -> bool:
    """List 双形态判定：旧 `List[X]` / 现代化 `list[X]`。"""
    return "List" in type_str or "list" in type_str


def _is_dict_like(type_str: str) -> bool:
    """Dict 双形态判定：旧 `Dict[K,V]` / 现代化 `dict[K,V]`。"""
    return "Dict" in type_str or "dict" in type_str


def _format_default(field: dict) -> str:
    """_format_default implementation（统一基于 _modernize_type 现代化类型串判定——
    原串 `array[{...}]` 不命中 list/dict 判定致 required=false 字段无默认值=
    TypeError: non-default argument follows default argument，CTR-P1-017 实证）。"""
    default = field.get("default")
    type_str = _modernize_type(field.get("type", ""))
    base_type = _resolve_base_type(type_str)
    is_required = field.get("required", True)

    if default is None:
        if _is_optional_like(type_str):
            return " = None"
        if _is_list_like(type_str):
            return " = field(default_factory=list)"
        if _is_dict_like(type_str):
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
    elif base_type in ("List", "Dict", "list", "dict"):
        return " = field(default_factory=list)" if _is_list_like(type_str) else " = field(default_factory=dict)"
    elif base_type == "datetime":
        return " = field(default_factory=lambda: datetime.now(timezone.utc))"
    elif base_type not in _STANDARD_TYPES:
        if isinstance(default, str):
            return f" = {base_type}.{default}"
        return f" = {default}"
    else:
        return f" = {default}"


def _has_effective_default(field: dict) -> bool:
    """_has_effective_default implementation（与 _format_default 同基准=现代化类型串，
    否则排序分组与默认值产出分裂：array[...] 原串判无默认排前组、现代化串判 list
    给 default_factory=TypeError，CTR-P1-017 实证）。"""
    if "default" in field:
        return True
    if not field.get("required", True):
        return True
    type_str = _modernize_type(field.get("type", ""))
    if _is_list_like(type_str):
        return True
    if _is_dict_like(type_str):
        return True
    if _is_optional_like(type_str):
        return True
    return False


def _format_ai_prompt(ai_prompt: str, indent: int = 4) -> str:
    """_format_ai_prompt implementation.

    2026-08-19 治本：空行不填缩进前缀（原 `f"{prefix}{line.strip()}"` 把空行渲染为
    纯空白行=W293，docstring 内 ruff --fix 不可修，生成即残留 17 处实证）。
    """
    prefix = " " * indent
    lines = ai_prompt.strip().split("\n")
    return "\n".join(f"{prefix}{line.strip()}" if line.strip() else "" for line in lines)


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
        f'# created: "{idempotent_date(_SCRIPT_DIR)}"',
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
        # 治本（#ARCH-130 P0-A）：直出 UP006/UP045 现代化类型，B 管线 ruff fix 零动作
        # （否则 fix 连带清理 typing import 行 → 与含残留行的 HEAD 基准 diff 非零）
        ftype = _modernize_type(f["type"])

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
    result = _render_contract_content(ctr)
    if result is None:
        return None
    physical, final_content = result

    output_path = REPO_ROOT / physical
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not dry_run:
        atomic_write_safe(output_path, final_content)
        print(f"  ✅ {physical}")

    return str(output_path)


def _render_contract_content(ctr: dict) -> tuple[str, str] | None:
    """渲染契约文件完整内容（纯函数，零磁盘写入）。

    C 门禁接口（#ARCH-130 P0-A，2026-08-19）：返回 (physical_path, final_content)，
    供 check_contracts_codegen_idempotent.py 直接比对磁盘文件=幂等性验证。
    与 generate_contract_file 共享全部渲染逻辑，确保门禁比对=真实生成产物。
    """
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

    import_map = _collect_import_map(fields, physical)

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
    begin_marker = CODGEN_BEGIN.format(contract_id=contract_id)
    end_marker = CODGEN_END.format(contract_id=contract_id)

    output_path = REPO_ROOT / physical

    # 既有文件探测先行：import 语义并集需先拿到旧生成区/手写区 import 全集
    existing = ""
    before = ""
    after = ""
    pre_existing = ""
    has_markers = False
    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        if begin_marker in existing and end_marker in existing:
            has_markers = True
            before = existing[: existing.index(begin_marker)]
            # 治本（#ARCH-REGEN-NONIDEMPOTENT-001）：lstrip("\n") 消除 end_marker 后累积空行——
            # wrapped_content 末尾已有 {end_marker}\n，若 after 保留原尾部 \n 则每次运行 +1 空行（非幂等）。
            after = existing[existing.index(end_marker) + len(end_marker) :].lstrip("\n")
            # A3 治本重写（2026-08-19）：语义级并集替代整行比对——ruff I001 合并行
            # （from typing import Dict, Optional）与推导分开行整行不等→误判 missing→
            # 注入 docstring 前=段外 import→与 HEAD 布局 diff 非零（43 文件实证）。
            old_zone = existing[existing.index(begin_marker) : existing.index(end_marker)]
            import_map = _union_import_map(import_map, old_zone)
        else:
            # 治本(2026-07-02): 传入class_name, 跳过旧codegen的同名class定义
            raw_name = contract_name.split(" / ")[0].strip()
            _class_match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", raw_name)
            _contract_class_name = _class_match.group(0) if _class_match else ""
            pre_existing, hand_imports = _extract_hand_maintained(existing, begin_marker, _contract_class_name)
            # 手写区 import 语义级并集回注（防 NameError——Any/asdict/replace 实证）
            if hand_imports:
                import_map = _union_import_map(import_map, "\n".join(hand_imports))

    import_lines = _render_import_block(import_map)
    # 布局对齐 HEAD（ruff 安全修复批形态）：import 块与 `# ---` 头注间空一行
    generated_block = field_header + "\n".join(import_lines) + "\n\n" + header + dataclass_code + "\n"
    wrapped_content = f"{begin_marker}\n{generated_block}\n{end_marker}\n"

    if has_markers:
        # A2 幂等（2026-08-19）：created=创建日期语义，再生成不漂移——既有文件含
        # created 行时沿用旧值（idempotent_date 随生成器脚本 commit 漂移，致重跑
        # 必产生假 diff，C 门禁比对噪音）。
        m_new = re.search(r'# created: "([^"]+)"', wrapped_content)
        m_old = re.search(r'# created: "([^"]+)"', existing)
        if m_new and m_old and m_new.group(1) != m_old.group(1):
            wrapped_content = wrapped_content.replace(
                f'# created: "{m_new.group(1)}"', f'# created: "{m_old.group(1)}"'
            )
        final_content = before + wrapped_content + after
    elif existing:
        final_content = pre_existing + "\n" + wrapped_content
    else:
        final_content = wrapped_content

    return physical, final_content


def _extract_hand_maintained(source: str, begin_marker: str, contract_class_name: str = "") -> str:
    """提取手写维护的代码（BEGIN CODGEN标记之前），跳过旧codegen的同名class定义。

    治本(2026-07-02): 移除@dataclass的过早break（原逻辑遇到任何@dataclass就停止提取，
    导致手写的FactorDiscovery/BacktestEngineBase等被丢弃）。改为跳过与当前contract
    同名的class定义块（旧codegen产物），保留其他所有手写代码。
    修复engine_base.py案例：codegen覆盖手写BacktestEngineBase+FactorDiscovery的问题。
    """
    lines = source.rstrip().split("\n")
    result: list[str] = []
    skipped_imports: list[str] = []  # 被跳过规则的 import 行（else 分支并集回注用，
    # 2026-08-19 治本：手写区符号断供——result_repository.py 手写区用 Any/asdict/replace
    # 而 import 行被吞=NameError；编译期 py_compile 查不出，必须并集回注）
    skipping_old_class = False  # 正在跳过旧codegen的同名class body
    in_docstring = False  # 多行 docstring 状态机（2026-08-19 治本：原逐行跳过逻辑把
    # docstring 内容行当手写代码保留、首行 """ 行丢弃——切碎致裸中文文本 syntax error，
    # result_repository.py 实证；手工模块被 YAML 纳管场景必须整块保留 docstring）
    in_import_buf = ""  # 多行 import 重组 buffer（2026-08-19 治本 Bug1）
    in_import_depth = 0

    for line in lines:
        stripped = line.strip()
        if begin_marker in stripped:
            break

        # 2026-08-19 治本 Bug2：skipping_old_class 最高优先级——吞掉旧 codegen class 的
        # 一切（含 docstring）。原 docstring 状态机优先级更高，致 class 定义被吞但其
        # docstring 被保留=孤立 docstring 语法残骸（result_repository.py 实证）。
        if skipping_old_class:
            # 跳过class body（缩进行/空行/注释），遇到下一个顶层定义时停止
            if stripped and not line[0].isspace() and not stripped.startswith("#"):
                skipping_old_class = False
                # 不continue，继续处理当前行
            else:
                continue

        # 2026-08-19 治本 Bug1：多行 import 括号状态机——续行并入 buffer，闭合后
        # 单行化收集（原逻辑只收首行 `from x import (`，续行 `A,` 落手写区保留
        #  = IndentationError，result_repository.py 实证）。
        if in_import_buf:
            in_import_buf += " " + stripped
            in_import_depth += stripped.count("(") - stripped.count(")")
            if in_import_depth <= 0:
                skipped_imports.append(in_import_buf)
                in_import_buf = ""
            continue

        # docstring 状态机：整块保留（含首末 """ 行）
        if in_docstring:
            result.append(line)
            if '"""' in stripped:
                in_docstring = False
            continue
        if stripped.startswith('"""'):
            result.append(line)
            if stripped.count('"""') < 2:  # 单行 docstring（"""text"""）不进状态
                in_docstring = True
            continue

        # 跳过与当前contract同名的class定义（旧codegen产物）
        if contract_class_name and stripped.startswith(f"class {contract_class_name}"):
            skipping_old_class = True
            # 移除前面已添加的装饰器（@dataclass等）
            while result and result[-1].strip().startswith("@"):
                result.pop()
            continue

        # 头注区（# [...]）整块保留——手工模块的 S4 注入头注是真源元数据，
        # 丢弃会致 [DOMAIN]/[MODULE] 等治理锚点丢失（result_repository.py 实证）
        if stripped.startswith("# ["):
            result.append(line)
            continue

        # __future__ 必须文件首部（注释/docstring 后）——原位保留不回注
        # （回注到生成块中部=SyntaxError）
        if stripped.startswith("from __future__"):
            result.append(line)
            continue
        # import 行：收集不丢弃（生成区重带 YAML 推导的，手写区额外需求并集回注）
        if stripped.startswith(("from ", "import ")):
            in_import_depth = stripped.count("(") - stripped.count(")")
            if in_import_depth > 0:
                in_import_buf = stripped  # 多行 import 首行，续行进状态机重组
            else:
                skipped_imports.append(stripped)
            continue
        if stripped.startswith("# ---"):
            continue
        if (
            stripped.startswith("# layer:")
            or stripped.startswith("# category:")
            or stripped.startswith("# status:")
            or stripped.startswith("# created:")
            or stripped.startswith("# generated_by:")
        ):
            continue
        if stripped.startswith("ZephyrAlpha"):
            continue
        result.append(line)

    while result and not result[-1].strip():
        result.pop()

    return "\n".join(result).rstrip() + "\n", skipped_imports


def _extract_public_symbols(file_path: Path) -> list[str]:
    """从 Python 文件中提取公开符号（class/def/常量），用于生成显式导入。

    5.93.6: 替代 ``from .xxx import *``，消除命名空间污染。
    优先解析 ``__all__``；无 ``__all__`` 时提取不以 ``_`` 开头的 class/def/常量。
    """
    if not file_path.exists():
        return []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001  文件读取降级
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


def _extract_preserved_annotations(content: str) -> tuple[str, str]:
    """提取既有 __init__.py 中需跨生成保留的注入区（S4 头注 + ALGO_FLOW 段）。

    2026-08-19 治本（#ARCH-130 P0-A 拦截的结构冲突）：generate_directory_init 原全量
    覆写吞掉 S4 reconciler 注入的 [BLUEPRINT]/[TTL] 头注与 [ALGO_FLOW] 段——重跑
    生成器即回退后处理批修复（ruff 六码批实证 43 文件）。提取两区在生成后重新注入：
    ①文件头连续 ``# [`` 开头行（S4 头注块）；②``# [ALGO_FLOW]`` 至 ``# [/ALGO_FLOW]``
    段（可在 docstring 外）。无这两区时返回空串（=现状零行为变更）。
    """
    header_lines: list[str] = []
    for line in content.splitlines():
        if line.startswith("# ["):
            header_lines.append(line)
        elif line.strip() == "" or line.startswith("#"):
            continue  # 头注区内允许空行/普通注释
        else:
            break  # 首个非注释行=头注区结束
    header_block = "\n".join(header_lines).strip("\n")

    algo_block = ""
    m = re.search(r"^# \[ALGO_FLOW\].*?^# \[/ALGO_FLOW\]", content, re.MULTILINE | re.DOTALL)
    if m:
        algo_block = m.group(0)
    return header_block, algo_block


def generate_directory_init(directory: Path, module_names: list[str], dry_run: bool = False) -> str | None:
    """生成子目录 __init__.py（显式导入聚合）。返回写入路径（skip/未写时 None）。

    2026-08-19 治本（#ARCH-130 P0-A）双机制：
    ① S4 深度接管态（ALGO_FLOW 注入 docstring 内+边段+isort 折叠）生成器单跑无法
       复刻三方叠加形态，重跑必丢导出（io/__init__.py 丢 backtest_result_sink 实证）
       → 跳过，包导出由 S4 reconciler 维护（新契约导出需人工/S4 补登=遗留项）；
    ② 单契约模式（--contract）module_names 仅含当次模块，全量重建丢兄弟模块
       → 既有导出模块并集（只增；减靠 CODEGEN-GUARD 或人工）。
    """
    init_file = directory / "__init__.py"
    preserved_header = ""
    preserved_algo = ""
    if init_file.exists():
        existing = init_file.read_text(encoding="utf-8")
        if "CODEGEN-GUARD: CTR-declarations-manual" in existing:
            print(f"  [Codegen] SKIP {init_file} (CODEGEN-GUARD active)")
            return None
        if "# [ALGO_FLOW]" in existing:
            print(f"  [Codegen] SKIP {init_file} (S4-managed: ALGO_FLOW present)")
            return None
        preserved_header, preserved_algo = _extract_preserved_annotations(existing)
        existing_mods = re.findall(r"^from \.(\w+) import", existing, re.MULTILINE)
        module_names = sorted(set(module_names) | set(existing_mods))
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

    if preserved_algo:
        init_lines.extend(["", preserved_algo])
    content = "\n".join(init_lines) + "\n"
    if preserved_header:
        content = preserved_header + "\n" + content
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
    generated_files: list[str] = []

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
            generated_files.append(output_path)
            parent = Path(output_path).parent
            if parent != REPO_ROOT / "src/zephyr/shared/contracts":
                subdir_key = str(parent)
                mod_name = Path(output_path).stem
                subdir_modules.setdefault(subdir_key, []).append(mod_name)

    for subdir, modules in subdir_modules.items():
        generate_directory_init(Path(subdir), modules, dry_run=args.dry_run)

    print(f"\n[Codegen] 完成 — 生成 {generated_count} 个文件, 跳过 {skipped_count} (无 physical_path)")

    # B 路径（2026-08-19 治本，#ARCH-130 P0-A 拦截的结构冲突）：生成后自动 ruff 格式化，
    # 使产物即合规（I001/UP006/UP045/W292/W293 六码），消除"ruff 批修产物 vs 模板旧形态"
    # 的结构性回退通道。fail-open：ruff 不可用/失败仅告警不阻断生成（产物仍可用）。
    # 覆盖面=逐生成文件（2026-08-19 修正：原按父目录去重对整个目录 --fix，会越界触碰
    # 手写文件——engine_base.py/io/__init__.py CRLF 抖动实证；生成器只对自己的产物负责）。
    if not args.dry_run and generated_files:
        import subprocess

        for target in generated_files:
            # --select 限定六码（与 ruff 安全修复批同口径）——全量 --fix 会越界清
            # F401 等六码外规则，产物 diff 超出"回退防除"范围引入新风险
            cmd = ["ruff", "check", "--fix", "--quiet", "--select", "I001,UP006,UP045,W292,W293,F541", target]
            try:
                proc = subprocess.run(  # noqa: bare-subprocess  CLI 工具调用（ruff 管道）
                    cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60
                )
                if proc.returncode != 0:
                    print(f"  [WARN] ruff --fix {target} 异常（rc={proc.returncode}）：{proc.stderr.strip()[:200]}")
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                print(f"  [WARN] ruff 自动格式化跳过（{e}）——产物未格式化，请手工跑 ruff")
                break
            # format（2026-08-19 扩展：C 门禁需比对 format 后形态，B/C 口径一致）
            try:
                subprocess.run(  # noqa: bare-subprocess  CLI 工具调用（ruff 管道）
                    ["ruff", "format", "--quiet", target],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

    if not args.dry_run:
        print("\n[Codegen] 下一步:")
        print("  1. python scripts/context/generate_architecture_context.py  # 重生成上下文")
        print("  2. python -m pytest tests/architecture/ -v                   # 验证一致性")

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
