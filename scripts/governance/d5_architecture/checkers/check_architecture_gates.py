# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_architecture_gates.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_architecture_gates
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
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
#!/usr/bin/env python3
"""v2.4.0 — 2026-05-03

用途：验证架构终局完成度，作为进入 beta 施工阶段的门禁。
来源：ARCHITECTURE-AS-CODE-PLAN-v2.0.md §1.3 + GATE-A 代码↔YAML 对齐 + 2026-05-03 审计反漂移升级
"""

from __future__ import annotations

__manifest__ = """
args:
  - --warn-only
  - --jsonl
description: Architecture GATE checker (GATE-01~08 + GATE-A + GATE-SC + EXTRA-01~04)
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.thresholds import get as get_threshold

ensure_utf8_stdout()

ARCH_MODEL = REPO_ROOT / "architecture_model"
ADR_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "adr"

import subprocess

from _shared.yaml_utils import load_yaml

_D5_DIR = str(Path(__file__).resolve().parent.parent)
if _D5_DIR not in sys.path:
    sys.path.insert(0, _D5_DIR)
from validators.validate_blind_spot_status import run_gate_bs


def _call_validate_yaml_summaries() -> tuple[bool, list[str]]:
    """GATE-SUM 通过 subprocess 调用 validate_yaml_summaries.py"""
    script_path = Path(__file__).resolve().parent / "validate_yaml_summaries.py"
    result = subprocess.run(
        [sys.executable, str(script_path), "--warn-only"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        return False, [f"GATE-SUM 执行失败 (exit={result.returncode}): {result.stderr.strip()[:500]}"]
    if "所有 YAML summary 字段与实际数据完全一致" in output:
        return True, []
    errors = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and "]" in stripped:
            errors.append(stripped)
    return len(errors) == 0, errors


def gate_01_index_reachable() -> tuple[bool, list[str]]:
    """GATE-01: _index.yaml 存在且所有分区文件可达"""
    errors = []
    index_path = ARCH_MODEL / "index.yaml"

    if not index_path.exists():
        errors.append(f"index.yaml 不存在: {index_path}")
        return False, errors

    data = load_yaml(index_path)
    if not data:
        errors.append("index.yaml 为空或无法解析")
        return False, errors

    partitions = data.get("partitions", [])
    if isinstance(partitions, list):
        for item in partitions:
            if isinstance(item, dict) and "path" in item:
                p = ARCH_MODEL / item["path"]
                if not p.exists():
                    errors.append(f"分区文件不可达: {item['path']}（id={item.get('id', '?')}）")
    elif isinstance(partitions, dict):
        for category, items in partitions.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and "path" in item:
                        p = ARCH_MODEL / item["path"]
                        if not p.exists():
                            errors.append(f"分区文件不可达: {item['path']}")

    return len(errors) == 0, errors


def _collect_layer_ids() -> set[str]:
    """收集所有 layer YAML 分区的 partition.id（如 l00, l01, ..., shared）。"""
    ids: set[str] = set()
    layers_dir = ARCH_MODEL / "layers"
    if not layers_dir.exists():
        return ids
    for yaml_file in sorted(layers_dir.glob("*.yaml")):
        data = load_yaml(yaml_file)
        if not data:
            continue
        partition = data.get("partition", {})
        if isinstance(partition, dict):
            pid = partition.get("id", "")
            if pid:
                ids.add(pid)
    # 也收集 frontend 和 scripts 分区 ID
    for extra_dir in ["frontend", "scripts"]:
        extra_path = ARCH_MODEL / extra_dir
        if not extra_path.exists():
            continue
        for yaml_file in sorted(extra_path.glob("*.yaml")):
            data = load_yaml(yaml_file)
            if not data:
                continue
            partition = data.get("partition", {})
            if isinstance(partition, dict):
                pid = partition.get("id", "")
                if pid:
                    ids.add(pid)
    return ids


def _collect_contract_ids() -> set[str]:
    """收集 cross_layer_contracts.yaml 中所有 contract / ocp / external 的 id。"""
    ids: set[str] = set()
    contracts_path = ARCH_MODEL / "contracts" / "cross_layer_contracts.yaml"
    if not contracts_path.exists():
        return ids
    data = load_yaml(contracts_path)
    if not data:
        return ids
    # 数据契约 (CTR-*)
    contracts = data.get("contracts", [])
    if isinstance(contracts, list):
        for c in contracts:
            if isinstance(c, dict) and "id" in c:
                ids.add(c["id"])
    # OCP 扩展点 (OCP-*)
    ocp = data.get("ocp_extension_points", [])
    if isinstance(ocp, list):
        for c in ocp:
            if isinstance(c, dict) and "id" in c:
                ids.add(c["id"])
    # 外部契约 (EXT-*)
    ext = data.get("external_contracts", [])
    if isinstance(ext, list):
        for c in ext:
            if isinstance(c, dict) and "id" in c:
                ids.add(c["id"])
    return ids


def gate_02_p0_interfaces() -> tuple[bool, list[str]]:
    """GATE-02: 所有 P0 模块的 interface_contract 非空 + contract_id 在 contracts YAML 中存在"""
    errors = []
    layers_dir = ARCH_MODEL / "layers"

    if not layers_dir.exists():
        errors.append(f"layers/ 目录不存在: {layers_dir}")
        return False, errors

    # 收集合法 contract_id
    valid_contract_ids = _collect_contract_ids()

    for yaml_file in sorted(layers_dir.glob("*.yaml")):
        data = load_yaml(yaml_file)
        if not data:
            continue
        modules = data.get("modules", [])
        if not isinstance(modules, list):
            continue
        for mod in modules:
            if not isinstance(mod, dict):
                continue
            priority = mod.get("priority", "")
            mod_id = mod.get("id", "unknown")
            if priority == "P0":
                interfaces = mod.get("interfaces", [])
                contract = mod.get("interface_contract") or interfaces
                if not contract:
                    errors.append(f"{yaml_file.name}: P0 模块 {mod_id} 缺少 interface_contract")
                # 验证 interfaces 中引用的 contract_id 在 contracts YAML 中存在
                if isinstance(interfaces, list):
                    for iface in interfaces:
                        if not isinstance(iface, dict):
                            continue
                        cid = iface.get("contract_id", "")
                        if cid and valid_contract_ids and cid not in valid_contract_ids:
                            errors.append(
                                f"{yaml_file.name}: P0 模块 {mod_id} 引用 contract_id={cid} "
                                f"在 cross_layer_contracts.yaml 中不存在"
                            )

    return len(errors) == 0, errors


def gate_03_invariants_owner() -> tuple[bool, list[str]]:
    """GATE-03: invariants.yaml 每条不变量有 owner"""
    errors = []
    inv_path = ARCH_MODEL / "cross-cutting" / "invariants.yaml"

    if not inv_path.exists():
        errors.append(f"invariants.yaml 不存在: {inv_path}")
        return False, errors

    data = load_yaml(inv_path)
    if not data:
        errors.append("invariants.yaml 为空或无法解析")
        return False, errors

    invariants = data.get("invariants", [])
    for inv in invariants:
        if not isinstance(inv, dict):
            continue
        inv_id = inv.get("id", "unknown")
        owner = inv.get("owner", "")
        if not owner:
            errors.append(f"不变量 {inv_id} 缺少 owner")

    return len(errors) == 0, errors


def gate_05_adr_accepted() -> tuple[bool, list[str]]:
    """GATE-05: ADR 体系完整性检查。
    2026-05-05 (session-012): 33 条 ADR 全部迁入 KB:decisions namespace，
    物理 adr/ 目录已删除。检查 architecture-rationale-log.md 存在性。"""
    errors = []
    rationale_log = REPO_ROOT / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"
    if not rationale_log.exists():
        errors.append(f"ADR 权威真源不存在: {rationale_log}")
        return False, errors
    return True, errors


def extra_01_no_duplicate_ids() -> tuple[bool, list[str]]:
    """EXTRA-01: YAML 模型 module_id 无重复"""
    errors = []
    all_ids: dict[str, str] = {}  # id -> source file

    for yaml_dir in [ARCH_MODEL / "layers", ARCH_MODEL / "frontend", ARCH_MODEL / "scripts"]:
        if not yaml_dir.exists():
            continue
        for yaml_file in sorted(yaml_dir.glob("*.yaml")):
            data = load_yaml(yaml_file)
            if not data:
                continue
            modules = data.get("modules", [])
            if not isinstance(modules, list):
                continue
            for mod in modules:
                if not isinstance(mod, dict):
                    continue
                mod_id = mod.get("id", "")
                if not mod_id:
                    continue
                if mod_id in all_ids:
                    errors.append(f"重复 module_id: {mod_id} 出现在 {all_ids[mod_id]} 和 {yaml_file.name}")
                else:
                    all_ids[mod_id] = yaml_file.name

    return len(errors) == 0, errors


def extra_02_interface_refs_exist() -> tuple[bool, list[str]]:
    """EXTRA-02: interfaces 的 source/target 引用存在"""
    errors = []

    # 收集所有 module_id
    all_ids: set[str] = set()
    all_yamls = []
    for yaml_dir in [ARCH_MODEL / "layers", ARCH_MODEL / "frontend", ARCH_MODEL / "scripts"]:
        if not yaml_dir.exists():
            continue
        for yaml_file in sorted(yaml_dir.glob("*.yaml")):
            data = load_yaml(yaml_file)
            if not data:
                continue
            all_yamls.append((yaml_file, data))
            modules = data.get("modules", [])
            if not isinstance(modules, list):
                continue
            for mod in modules:
                if isinstance(mod, dict) and "id" in mod:
                    all_ids.add(mod["id"])

    # 检查 interfaces
    for yaml_file, data in all_yamls:
        modules = data.get("modules", [])
        if not isinstance(modules, list):
            continue
        for mod in modules:
            if not isinstance(mod, dict):
                continue
            mod_id = mod.get("id", "unknown")
            interfaces = mod.get("interfaces", [])
            if not isinstance(interfaces, list):
                continue
            for iface in interfaces:
                if not isinstance(iface, dict):
                    continue
                for ref_key in ("source", "target", "peer"):
                    ref = iface.get(ref_key, "")
                    if ref and ref not in all_ids and not ref.startswith("external:"):
                        errors.append(f"{yaml_file.name}: {mod_id}.interfaces[].{ref_key}={ref} 引用不存在")

    return len(errors) == 0, errors


def gate_06_event_publisher_exists() -> tuple[bool, list[str]]:
    """GATE-06: domain_events.yaml 每个事件的 publisher 层 ID 在 layer YAML 分区中存在"""
    errors = []
    events_path = ARCH_MODEL / "events" / "domain_events.yaml"

    if not events_path.exists():
        errors.append(f"domain_events.yaml 不存在: {events_path}")
        return False, errors

    data = load_yaml(events_path)
    if not data:
        errors.append("domain_events.yaml 为空或无法解析")
        return False, errors

    valid_layer_ids = _collect_layer_ids()
    if not valid_layer_ids:
        errors.append("无法收集 layer IDs（layers/ 目录为空或不存在）")
        return False, errors

    # 检查所有域的事件
    for domain_key in (
        "research_domain",
        "signal_domain",
        "portfolio_domain",
        "execution_domain",
        "risk_domain",
        "ops_domain",
        "quantitative_red_lines",
    ):
        domain_events = data.get(domain_key, [])
        if not isinstance(domain_events, list):
            continue
        for event in domain_events:
            if not isinstance(event, dict):
                continue
            event_id = event.get("id", "unknown")
            publisher = event.get("publisher", "")
            if publisher and publisher not in valid_layer_ids:
                errors.append(
                    f"事件 {event_id}: publisher={publisher} 不在 layer 分区中（合法值: {sorted(valid_layer_ids)}）"
                )

    return len(errors) == 0, errors


def gate_07_aggregate_layer_exists() -> tuple[bool, list[str]]:
    """GATE-07: ddd_model.yaml 每个 aggregate 的 layer 在 layer YAML 分区中存在"""
    errors = []
    ddd_path = ARCH_MODEL / "domain" / "ddd_model.yaml"

    if not ddd_path.exists():
        errors.append(f"ddd_model.yaml 不存在: {ddd_path}")
        return False, errors

    data = load_yaml(ddd_path)
    if not data:
        errors.append("ddd_model.yaml 为空或无法解析")
        return False, errors

    valid_layer_ids = _collect_layer_ids()
    if not valid_layer_ids:
        errors.append("无法收集 layer IDs（layers/ 目录为空或不存在）")
        return False, errors

    aggregate_roots = data.get("aggregate_roots", [])
    if not isinstance(aggregate_roots, list):
        errors.append("ddd_model.yaml 缺少 aggregate_roots 列表")
        return False, errors

    for agg in aggregate_roots:
        if not isinstance(agg, dict):
            continue
        agg_id = agg.get("id", "unknown")
        layer = agg.get("layer", "")
        if layer and layer not in valid_layer_ids:
            errors.append(f"Aggregate {agg_id}: layer={layer} 不在 layer 分区中（合法值: {sorted(valid_layer_ids)}）")

    return len(errors) == 0, errors


def gate_08_technology_quadrant_valid() -> tuple[bool, list[str]]:
    """GATE-08: technology_landscape.yaml 每个条目的 quadrant 值合法"""
    errors = []
    tech_path = ARCH_MODEL / "technology" / "technology_landscape.yaml"

    if not tech_path.exists():
        errors.append(f"technology_landscape.yaml 不存在: {tech_path}")
        return False, errors

    data = load_yaml(tech_path)
    if not data:
        errors.append("technology_landscape.yaml 为空或无法解析")
        return False, errors

    valid_quadrants = {"adopt", "trial", "assess", "hold", "build"}

    technologies = data.get("technologies", [])
    if not isinstance(technologies, list):
        errors.append("technology_landscape.yaml 缺少 technologies 列表")
        return False, errors

    for tech in technologies:
        if not isinstance(tech, dict):
            continue
        tech_id = tech.get("id", "unknown")
        quadrant = tech.get("quadrant", "")
        if quadrant and quadrant not in valid_quadrants:
            errors.append(f"技术条目 {tech_id}: quadrant={quadrant} 不合法（合法值: {sorted(valid_quadrants)}）")
        elif not quadrant:
            errors.append(f"技术条目 {tech_id}: 缺少 quadrant 字段")

    return len(errors) == 0, errors


def _extract_schema_enums(schema_data: dict) -> dict[str, set[str]]:
    """从 _schema.yaml operational_schema 中提取所有 type=enum 字段的合法值集合。
    返回: {"status": {planned, deferred, ...}, "interfaces.role": {producer, consumer, both}, ...}
    """
    enums: dict[str, set[str]] = {}
    op_schema = schema_data.get("operational_schema", {})
    if not isinstance(op_schema, dict):
        return enums

    for field_name, field_def in op_schema.items():
        if not isinstance(field_def, dict):
            continue
        if field_def.get("type") == "enum":
            enums[field_name] = set(field_def.get("values", []))
        if field_def.get("type") == "object" and "properties" in field_def:
            for sub_name, sub_def in field_def["properties"].items():
                if isinstance(sub_def, dict) and sub_def.get("type") == "enum":
                    enums[f"{field_name}.{sub_name}"] = set(sub_def.get("values", []))
        if field_def.get("type") == "array" and "items" in field_def:
            items = field_def["items"]
            if isinstance(items, dict):
                for sub_name, sub_def in items.items():
                    if isinstance(sub_def, dict) and sub_def.get("type") == "enum":
                        enums[f"{field_name}.{sub_name}"] = set(sub_def.get("values", []))

    return enums


def gate_sc_schema_compliance() -> tuple[bool, list[str]]:
    """GATE-SC: 模块所有枚举字段值在 _schema.yaml 合法值列表内（v3.1.0+ 全字段校验）"""
    errors = []
    schema_path = ARCH_MODEL / "layers" / "_schema.yaml"

    if not schema_path.exists():
        errors.append(f"_schema.yaml 不存在: {schema_path}")
        return False, errors

    schema_data = load_yaml(schema_path)
    if not schema_data:
        errors.append("_schema.yaml 为空或无法解析")
        return False, errors

    schema_enums = _extract_schema_enums(schema_data)

    if not schema_enums:
        errors.append("_schema.yaml 中未找到任何 enum 字段定义")
        return False, errors

    scan_dirs = ["layers", "frontend", "scripts", "infra"]

    for dir_name in scan_dirs:
        scan_path = ARCH_MODEL / dir_name
        if not scan_path.exists():
            continue
        for yaml_file in sorted(scan_path.glob("*.yaml")):
            if yaml_file.name == "_schema.yaml":
                continue
            data = load_yaml(yaml_file)
            if not data:
                continue
            modules = data.get("modules", [])
            if not isinstance(modules, list):
                continue
            for mod in modules:
                if not isinstance(mod, dict):
                    continue
                mod_id = mod.get("id", "unknown")

                for field_path, valid_set in schema_enums.items():
                    if field_path == "status":
                        val = mod.get("status", "")
                        if val and val not in valid_set:
                            errors.append(
                                f"{dir_name}/{yaml_file.name}: 模块 {mod_id} status={val} "
                                f"不合法（合法值: {sorted(valid_set)}）"
                            )
                        elif not val:
                            errors.append(f"{dir_name}/{yaml_file.name}: 模块 {mod_id} 缺少 status 字段")
                    elif field_path == "priority":
                        val = mod.get("priority", "")
                        if val and val not in valid_set:
                            errors.append(
                                f"{dir_name}/{yaml_file.name}: 模块 {mod_id} priority={val} "
                                f"不合法（合法值: {sorted(valid_set)}）"
                            )
                    elif field_path == "runtime_plane":
                        val = mod.get("runtime_plane", "")
                        if val and val not in valid_set:
                            errors.append(
                                f"{dir_name}/{yaml_file.name}: 模块 {mod_id} runtime_plane={val} "
                                f"不合法（合法值: {sorted(valid_set)}）"
                            )
                    elif field_path == "interfaces.role":
                        for iface in mod.get("interfaces", []):
                            if not isinstance(iface, dict):
                                continue
                            role = iface.get("role", "")
                            if role and role not in valid_set:
                                errors.append(
                                    f"{dir_name}/{yaml_file.name}: 模块 {mod_id} interfaces.role={role} "
                                    f"不合法（合法值: {sorted(valid_set)}）"
                                )

    return len(errors) == 0, errors


def extra_03_summary_total_consistent() -> tuple[bool, list[str]]:
    """EXTRA-03: 每个 layer YAML 的 summary.total 与实际 modules 列表长度一致"""
    errors = []

    for yaml_dir in [ARCH_MODEL / "layers", ARCH_MODEL / "frontend", ARCH_MODEL / "scripts"]:
        if not yaml_dir.exists():
            continue
        for yaml_file in sorted(yaml_dir.glob("*.yaml")):
            data = load_yaml(yaml_file)
            if not data:
                continue
            modules = data.get("modules", [])
            summary = data.get("summary", {})
            if not isinstance(summary, dict):
                continue
            declared_total = summary.get("total")
            if declared_total is None:
                continue  # 没有 summary.total 字段则跳过
            actual_count = len(modules) if isinstance(modules, list) else 0
            if declared_total != actual_count:
                errors.append(f"{yaml_file.name}: summary.total={declared_total} 但实际 modules 数量={actual_count}")

    return len(errors) == 0, errors


def gate_a_code_yaml_alignment() -> tuple[bool, list[str]]:
    """GATE-A: src/zephyr/ ↔ architecture_model/ 代码与YAML双层对账

    GATE-A — 实际代码 ↔ YAML SSoT
    - CRITICAL: src/zephyr/lNN_* 目录存在但 _index.yaml 无对应分区（硬阻断）
    - CRITICAL: 分区有 implemented/active 模块但 src/zephyr/ 下无对应目录（硬阻断）
    - WARNING: src/zephyr/ 根层级目录未在 infra/ YAML 中登记
    """
    errors = []
    src_zephyr = REPO_ROOT / "src" / "zephyr"

    if not src_zephyr.exists():
        errors.append(f"src/zephyr/ 目录不存在: {src_zephyr}")
        return False, errors

    index_data = load_yaml(ARCH_MODEL / "index.yaml")
    if not index_data:
        errors.append("index.yaml 为空或无法解析")
        return False, errors

    partitions = index_data.get("partitions", [])
    part_map: dict[str, dict] = {}
    for p in partitions:
        if isinstance(p, dict) and "id" in p:
            part_map[p["id"]] = p

    actual_dirs: dict[str, list[str]] = {}
    root_dirs: set[str] = set()

    for entry in sorted(src_zephyr.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("__") or entry.name.startswith("."):
            continue
        files = [f.name for f in entry.rglob("*.py") if f.name != "__init__.py"]
        actual_dirs[entry.name] = files
        root_dirs.add(entry.name)

    for infra_id in ["core-services", "shared-infra"]:
        if infra_id not in part_map:
            continue
        infra_yaml_path = ARCH_MODEL / part_map[infra_id].get("path", "")
        if not infra_yaml_path.exists():
            continue
        infra_data = load_yaml(infra_yaml_path)
        if not infra_data:
            continue

        infra_modules = infra_data.get("modules") or infra_data.get("services") or []

        for mod in infra_modules:
            if not isinstance(mod, dict):
                continue
            sub_path = (mod.get("submodule_path") or "").replace("\\", "/").strip("/")
            parts = [p for p in sub_path.split("/") if p]
            dir_name = parts[-1] if len(parts) >= 2 else ""
            mod_status = mod.get("status", "")
            mod_id = mod.get("id", "?")

            if mod_status in ("implemented", "active"):
                if dir_name not in actual_dirs:
                    errors.append(
                        f"CRITICAL: {infra_id}/{mod_id} status={mod_status} 但 src/zephyr/{dir_name}/ 目录不存在"
                    )
                elif not actual_dirs.get(dir_name):
                    has_init = (src_zephyr / dir_name / "__init__.py").exists()
                    if not has_init:
                        errors.append(
                            f"CRITICAL: {infra_id}/{mod_id} status={mod_status} 但 "
                            f"src/zephyr/{dir_name}/ 下无 Python 文件且缺 __init__.py"
                        )

    known_root_dirs = {"shared"}
    for infra_id in ["core-services", "shared-infra"]:
        if infra_id not in part_map:
            continue
        infra_yaml_path = ARCH_MODEL / part_map[infra_id].get("path", "")
        if not infra_yaml_path.exists():
            continue
        infra_data = load_yaml(infra_yaml_path)
        if not infra_data:
            continue
        infra_modules = infra_data.get("modules") or infra_data.get("services") or []
        for mod in infra_modules:
            sp = (mod.get("submodule_path") or "").replace("\\", "/").strip("/")
            splitted = [p for p in sp.split("/") if p]
            if len(splitted) >= 3:
                known_root_dirs.add(splitted[2])

    for dir_name in sorted(root_dirs):
        if dir_name not in known_root_dirs:
            errors.append(f"WARNING: src/zephyr/{dir_name}/ 未在任何 YAML 分区中登记")

    has_critical = any(e.startswith("CRITICAL:") for e in errors)
    return not has_critical, errors


def gate_d_doc_directory_index_required() -> tuple[bool, list[str]]:
    """GATE-D: docs/ 下每个活跃子目录必须有 index.md 入口文件

    对标 Google OWNERS / Terraform Module Registry / ITIL CMDB ──
    所有活跃目录必须有一个声明其责任范围与结构的 index.md 入口文件。

    检查维度：
    1. docs/ 下的所有编号子目录（01_*, 02_*, etc.）必须有 index.md
    2. docs/index.md 中声明的"抽屉"路径必须真实存在
    3. 实际存在但未在 docs/index.md 中声明的目录 → 警告
    """
    errors = []
    warnings = []
    DOCS_ROOT = REPO_ROOT / "docs"

    doc_index = DOCS_ROOT / "index.md"
    index_data = None
    if doc_index.exists():
        try:
            with open(doc_index, encoding="utf-8") as f:
                index_data = f.read()
        except Exception:
            pass

    # 从 docs/index.md 中解析"抽屉"声明的目录路径
    declared_dirs: dict[str, str] = {}  # number -> path
    if index_data:
        in_table = False
        for line in index_data.splitlines():
            stripped = line.strip()
            if "子目录（抽屉）一览" in stripped:
                in_table = True
                continue
            if in_table and stripped.startswith("|"):
                parts = [p.strip() for p in stripped.split("|")]
                if len(parts) >= 4:
                    num_part = parts[1].strip() if len(parts) > 1 else ""
                    path_part = parts[2].strip() if len(parts) > 2 else ""
                    if num_part and path_part and num_part[0].isdigit():
                        clean_path = path_part.strip("`").strip()
                        declared_dirs[num_part] = clean_path

    # 收集 docs/ 下的实际编号子目录
    actual_numbered_dirs: dict[str, Path] = {}
    skipped_patterns = {"__pycache__", ".git", "_DO_NOT_USE", "_temp", "node_modules"}

    for entry in sorted(DOCS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if any(entry.name.startswith(p) or entry.name == p for p in skipped_patterns):
            continue
        match = re.match(r"^(\d{2})_", entry.name)
        if match:
            actual_numbered_dirs[match.group(1)] = entry

    # 检查 1: 活跃目录必须有 index.md
    has_kms_content = False
    for num, dir_path in sorted(actual_numbered_dirs.items()):
        index_md = dir_path / "index.md"
        if not index_md.exists():
            # 检查是否有实质内容（非空目录）
            contents = list(dir_path.glob("*"))
            meaningful = [c for c in contents if c.name != "index.md"]
            if meaningful:
                errors.append(
                    f"CRITICAL: docs/{dir_path.name}/ 有内容但缺少 index.md "
                    f"（对标 Google OWNERS——活跃目录必须有入口文件声明责任）"
                )
            else:
                warnings.append(f"WARNING: docs/{dir_path.name}/ 为空目录且无 index.md")

    # 检查 2: docs/index.md 声明的路径必须存在
    for num, declared_path in sorted(declared_dirs.items()):
        # declared_path 可能是相对路径如 "03_modules/"
        if declared_path.endswith("/"):
            declared_path = declared_path[:-1]
        resolved = DOCS_ROOT / declared_path
        if not resolved.exists():
            errors.append(f"CRITICAL: docs/index.md 声明抽屉 {num} = {declared_path} 但路径不存在")
        elif not (resolved / "index.md").exists():
            errors.append(f"CRITICAL: docs/index.md 声明抽屉 {num} = {declared_path} 路径存在 但缺少 index.md")

    # 检查 3: 实际存在但未在 docs/index.md 声明的目录
    for num, dir_path in sorted(actual_numbered_dirs.items()):
        if num not in declared_dirs:
            warnings.append(f"WARNING: docs/{dir_path.name}/ 实际存在但未在 docs/index.md 抽屉一览表中声明")

    # 检查 4: 声明的嵌套/特殊路径也必须有 index.md
    extra_check_dirs = [
        "03_modules/infrastructure_runtime_integration",
    ]
    for rel_path in extra_check_dirs:
        check_path = DOCS_ROOT / rel_path
        if check_path.exists() and not (check_path / "index.md").exists():
            errors.append(f"CRITICAL: {rel_path}/ 是活跃模块目录但缺少 index.md （对标 ITIL CMDB——每层目录必须有索引）")

    if not errors and not warnings:
        print(f"  ✅ 全部 {len(actual_numbered_dirs)} 个编号抽屉 index.md 完整")

    for w in warnings:
        print(f"  ⚠ {w}")

    return len(errors) == 0, errors


def gate_e_session_log_alignment() -> tuple[bool, list[str]]:
    """GATE-E: Session Log 变更对齐自检——决策→受影响文件同步验证

    对标 Google LSC（Large-Scale Changes）——决策不应仅改变一个文件，
    所有受影响的下游文件必须在同一 session 内同步更新。

    逻辑：读取最近 3 个 session log 的"变更的文件"表 →
    检测每类变更是否完成了跨文件联动同步：
    1. 蓝图编辑 → module-registry.yaml 版本号应同步
    2. YAML SSoT 变更 → 对应 MD 视图应同步
    3. 新建代码目录 → architecture_model YAML 应登记
    """
    errors = []
    logs_dir = REPO_ROOT / "session_logs"
    DOCS_ROOT = REPO_ROOT / "docs"

    if not logs_dir.exists():
        errors.append("session_logs/ 目录不存在")
        return False, errors

    log_files = sorted(logs_dir.rglob("session-*.yaml"), reverse=True)
    if not log_files:
        log_files = sorted(logs_dir.glob("session-*.md"), reverse=True)
    recent = log_files[:3]

    if not recent:
        errors.append("session_logs/ 存在但未找到任何 session log 文件")
        return False, errors

    for log_path in recent:
        try:
            content = log_path.read_text(encoding="utf-8")
        except Exception:
            continue

        # 解析变更文件表
        in_changes_table = False
        changed_blueprints: list[str] = []
        changed_yamls: list[str] = []
        new_dirs: list[str] = []
        session_has_alignment_section = "变更对齐检查" in content or "Alignment Verification" in content

        for line in content.splitlines():
            stripped = line.strip()
            if "变更的文件" in stripped:
                in_changes_table = True
                continue
            if in_changes_table:
                if stripped.startswith("|") and "blueprint.md" in stripped:
                    changed_blueprints.append(stripped)
                elif stripped.startswith("|") and ".yaml" in stripped:
                    changed_yamls.append(stripped)
                elif stripped == "" and len(changed_blueprints) + len(changed_yamls) > 0:
                    in_changes_table = False

        # 同样解析"新增文件"表
        in_new_table = False
        for line in content.splitlines():
            stripped = line.strip()
            if "新增文件" in stripped:
                in_new_table = True
                continue
            if in_new_table:
                if stripped.startswith("|") and "src/zephyr/" in stripped and "**新建**" in stripped:
                    new_dirs.append(stripped)
                elif stripped == "" and len(new_dirs) > 0:
                    in_new_table = False

        log_name = log_path.stem

        # 检查 1: 蓝图编辑 → module-registry.yaml 版本号是否同步
        if changed_blueprints and not session_has_alignment_section:
            errors.append(
                f"WARNING: {log_name} 修改了蓝图文件但未包含'变更对齐检查'节 "
                f"（比对 Google LSC——蓝图版本号变更应同步更新 module-registry.yaml）"
            )

        # 检查 2: YAML SSoT 变更 → MD 视图
        if changed_yamls:
            arch_model_yamls = [y for y in changed_yamls if "architecture_model" in y.lower()]
            if arch_model_yamls and not session_has_alignment_section:
                errors.append(
                    f"WARNING: {log_name} 修改了 architecture_model YAML "
                    f"但未包含'变更对齐检查'节 "
                    f"（YAML SSoT 变更应同步更新 MD 视图）"
                )

        # 检查 3: 新建代码目录 → architecture_model 登记
        if new_dirs and not session_has_alignment_section:
            errors.append(
                f"WARNING: {log_name} 新建了 src/zephyr/ 目录 "
                f"但未包含'变更对齐检查'节 "
                f"（比对 GATE-A——新建代码目录应同步更新 architecture_model YAML）"
            )

        # 检查 4: 文件变更 → path-tree 刷新
        has_path_tree_refresh = (
            "generate_project_path_tree" in content or "path-tree" in content.lower() or "path_tree" in content.lower()
        )
        if (changed_blueprints or changed_yamls or new_dirs) and not has_path_tree_refresh:
            errors.append(
                f"WARNING: {log_name} 有文件变更 "
                f"但未执行 generate_project_path_tree.py --write "
                f"（G6_PT——文件增删移后必须刷新物理路径树快照）"
            )

    if not errors:
        print(f"  ✅ 最近 {len(recent)} 个 session log 变更对齐检查通过")

    return len(errors) == 0, errors


def extra_04_ssot_issue_trend() -> tuple[bool, list[str]]:
    """EXTRA-04: SSoT 问题追踪——跨文件不一致问题数量趋势

    对标 ITIL Problem Management——已知问题必须记录到已知错误数据库（KEDB）
    并追踪其修复进度。读取 ssot-issue-tracking.yaml 中最近的扫描记录，
    检测问题数量是否在下降（修复中）还是在上升（失控）。
    """
    errors = []
    import yaml

    tracking_path = REPO_ROOT / "docs" / "_working" / "audit" / "STATE" / "ssot-issue-tracking.yaml"

    if not tracking_path.exists():
        errors.append("EXTRA-04 SKIP: ssot-issue-tracking.yaml 不存在（对标 ITIL KEDB——需要先创建问题追踪登记表）")
        return True, errors  # 不存在不阻塞，仅提醒

    try:
        with open(tracking_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        errors.append(f"EXTRA-04 FAIL: 无法解析 ssot-issue-tracking.yaml: {e}")
        return False, errors

    entries = data.get("entries", [])
    if not entries:
        print("  ✅ ssot-issue-tracking.yaml 存在但无扫描记录")
        return True, []

    entries_sorted = sorted(entries, key=lambda e: e.get("scan_date", ""), reverse=True)
    latest = entries_sorted[0]

    total_issues = latest.get("issue_totals", {}).get("total", 0)
    critical = latest.get("issue_totals", {}).get("critical_issues", 0)
    warnings = latest.get("issue_totals", {}).get("warning_issues", 0)
    fixed_in_scope = latest.get("fixed_in_scope", False)
    fix_note = latest.get("fix_scope_note", "")

    if total_issues == 0:
        print("  ✅ SSoT 问题追踪：当前 0 个已知问题——全清！")
    elif fixed_in_scope:
        print(f"  ✅ SSoT 问题追踪：{total_issues} 个问题（{critical} P0 + {warnings} P1）——本次审计范围已修复")
        if fix_note:
            print(f"     {fix_note[:100]}...")
    else:
        errors.append(
            f"EXTRA-04 WARNING: {total_issues} 个 SSoT 已知问题（{critical} P0 + {warnings} P1）"
            f"——末次扫描 {latest.get('scan_date', '?')}，修复未闭环"
        )
        # 趋势检查
        if len(entries_sorted) >= 2:
            prev = entries_sorted[1]
            prev_total = prev.get("issue_totals", {}).get("total", 0)
            delta = total_issues - prev_total
            if delta > 0:
                errors.append(
                    f"EXTRA-04 WARNING: 问题数增长 +{delta}（{prev_total} → {total_issues}）— 需触发 Owner 决策"
                )
            elif delta < 0:
                print(f"  ✅ 趋势向好：-{abs(delta)} （{prev_total} → {total_issues}）")
            else:
                print(f"  ⚠ 趋势持平：{total_issues} 未变化")

    return len(errors) == 0, errors


def main() -> int:
    """运行所有 GATE 检查，返回失败数。"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Architecture-as-Code GATE v2.4.0")
    parser.add_argument("--warn-only", action="store_true", help="有 FAIL 亦 exit 0")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON 摘要")
    parser.add_argument("--gate", type=str, default=None, help="只运行指定 GATE（如 01/02/03/06/07）")
    args = parser.parse_args()

    print("=" * 60)
    print("Architecture-as-Code GATE 检查 v2.4.0")
    print("=" * 60)

    gates = [
        ("GATE-01", "index.yaml 存在且分区可达", gate_01_index_reachable),
        ("GATE-02", "P0 模块 interface_contract 非空 + contract_id 存在", gate_02_p0_interfaces),
        ("GATE-03", "invariants.yaml 每条有 owner", gate_03_invariants_owner),
        ("GATE-05", "ADR 状态为 accepted", gate_05_adr_accepted),
        ("GATE-06", "事件 publisher 层 ID 存在", gate_06_event_publisher_exists),
        ("GATE-07", "aggregate layer 存在", gate_07_aggregate_layer_exists),
        ("GATE-08", "technology quadrant 合法", gate_08_technology_quadrant_valid),
        ("GATE-A", "src/zephyr/ ↔ YAML SSoT 代码对齐", gate_a_code_yaml_alignment),
        ("GATE-D", "docs/ 活跃子目录 index.md 强制存在（对标 Google OWNERS）", gate_d_doc_directory_index_required),
        ("GATE-E", "Session Log 变更对齐自检（对标 Google LSC）", gate_e_session_log_alignment),
        ("GATE-SC", "模块 status 在 _schema.yaml 合法值内", gate_sc_schema_compliance),
        ("GATE-SUM", "YAML Summary 自动对账", _call_validate_yaml_summaries),
        ("GATE-BS", "盲点现实对账——open 盲点 vs 代码实际状态", run_gate_bs),
        ("EXTRA-01", "module_id 无重复", extra_01_no_duplicate_ids),
        ("EXTRA-02", "interfaces source/target 存在", extra_02_interface_refs_exist),
        ("EXTRA-03", "summary.total 与 modules 数量一致", extra_03_summary_total_consistent),
        ("EXTRA-04", "SSoT 问题追踪趋势（对标 ITIL KEDB）", extra_04_ssot_issue_trend),
    ]

    total_pass = 0
    total_fail = 0

    gate_filter = f"GATE-{args.gate}" if args.gate else None

    for gate_id, desc, check_fn in gates:
        if gate_filter and gate_id != gate_filter:
            continue
        print(f"\n{'─' * 40}")
        print(f"[{gate_id}] {desc}")
        passed, errors = check_fn()
        if passed:
            print("  ✅ PASS")
            total_pass += 1
        else:
            print(f"  ❌ FAIL ({len(errors)} 项)")
            for e in errors[:10]:
                print(f"     • {e}")
            if len(errors) > 10:
                print(f"     ... 还有 {len(errors) - 10} 条")
            total_fail += 1

    print(f"\n{'=' * 60}")
    print(
        f"结果：{total_pass} PASS / {total_fail} FAIL / 2 Phase B 待办（GATE-09/10）—— 含 GATE-A/B/D/E/SUM 五层闸门 + EXTRA-01~04"
    )
    print(f"{'=' * 60}")

    if total_fail > 0:
        print("\n⛔ 存在未通过的 GATE，不满足进入 beta 的条件。")
    else:
        print("\n✅ 所有自动 GATE 通过！GATE-09/10 为 Phase B 待办项（需性能/发布基础设施就位后自动化）。")

    if args.jsonl:
        print(
            json.dumps(
                {
                    "severity": "HIGH" if total_fail else "INFO",
                    "check_id": "ARCH-GATES",
                    "total_fail": total_fail,
                    "total_pass": total_pass,
                },
                ensure_ascii=False,
            )
        )
    if args.warn_only:
        return EXIT_PASS
    return total_fail


if __name__ == "__main__":
    sys.exit(main())
