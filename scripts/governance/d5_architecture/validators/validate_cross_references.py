# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_cross_references.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_cross_references
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
# [TTL] task_bound
#!/usr/bin/env python3
"""validate_cross_references.py — 架构模型 YAML + 治理文档跨引用完整性闸门（GATE-XREF）
v2.0.0 — 2026-05-03


GATE-A 代码↔YAML 对齐 + 漂移免疫架构原则 Level 2 门禁 3/4：
  根因：架构模型由 20+ YAML 文件组成，治理文档由 50+ 文件组成，
        引用链（contract_id / invariant_id / kb_ref / owner / source_layer /
        events_published / 文件路径 / depends_on）均为手动维护，
        无自动化交叉校验。引用漂移在每个 AI session 累积而不被察觉。

  本闸门：扫描所有 YAML/MD 文件，验证每条引用链的目标是否存在，
          废弃文件是否仍被引用，路径引用是否断裂。

检查维度：
  DIM-1: contract_id 引用链 —— layers/interfaces.contract_id → contracts/ 合同清单
  DIM-2: invariant_id 引用链 —— layers/invariants.id → cross-cutting/invariants.yaml
  DIM-3: kb_ref 引用链    —— 所有 YAML 中的 kb_ref → KB decisions 实际条目
  DIM-4: invariant.owner 归属 —— invariants.owner → _index.yaml partitions
  DIM-5: contract.source_layer 归属 —— contracts.source_layer → _index.yaml partitions
  DIM-6: 聚合根 events_published → events/ 事件清单
  DIM-7: 反向扫描 —— contracts/ 合同中未被任何 layer 引用的孤儿合同
  DIM-8: module_id 注册链 —— layers 模块 id → module_id_registry.yaml 登记
  DIM-9: 废弃文件引用检测 —— 所有 .md/.yaml 中引用已废弃文件（status: deprecated）
  DIM-10: 断裂路径引用检测 —— 所有 .md/.yaml 中的文件路径引用 → 目标文件存在性

对标：ITIL SACM → CMDB 跨配置项依赖关系必须显式登记
     AWS Config → 持续评估资源间引用关系的合规性
     K8s Admission Controller → 不允许引用不存在的资源
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-XREF — 架构模型 YAML 跨引用完整性闸门（8 维检查：contract_id/invariant_id/kb_ref/owner/source_layer/events_published/孤儿合同/module_id
  注册链，根治引用漂移）
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files
from _shared.yaml_utils import load_yaml

ensure_utf8_stdout()

ARCH_MODEL = REPO_ROOT / "architecture_model"
ADR_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "adr"

_errors: list[str] = []
_warnings: list[str] = []


def _err(msg: str) -> None:
    """_err implementation."""
    _errors.append(msg)


def _warn(msg: str) -> None:
    """_warn implementation."""
    _warnings.append(msg)


# =============================================================================
# 数据采集层
# =============================================================================


def _load_all_layer_yamls() -> list[tuple[str, dict]]:
    """扫描 layers/ infra/ scripts/ frontend/ 下所有模块 YAML，返回 (文件名, 数据) 列表"""
    results: list[tuple[str, dict]] = []
    scan_dirs = [
        ARCH_MODEL / "layers",
        ARCH_MODEL / "infra",
        ARCH_MODEL / "scripts",
        ARCH_MODEL / "frontend",
    ]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for yf in sorted(scan_dir.glob("*.yaml")):
            try:
                data = load_yaml(yf)
                if isinstance(data, dict):
                    results.append((yf.name, data))
            except Exception as e:
                _warn(f"无法加载 {yf.name}: {e}")
    return results


def _get_modules(data: dict) -> list[dict]:
    """从层 YAML 数据中提取模块列表（兼容 modules / services 字段名）"""
    return data.get("modules", data.get("services", []))


def _get_invariants(data: dict) -> list[dict]:
    """_get_invariants implementation."""
    return data.get("invariants", [])


# =============================================================================
# DIM-1: contract_id 引用链
# =============================================================================


def _build_contract_registry() -> set[str]:
    """从 cross_layer_contracts.yaml 构建合同 ID 集合"""
    contract_ids: set[str] = set()
    contracts_path = ARCH_MODEL / "contracts" / "cross_layer_contracts.yaml"
    if not contracts_path.exists():
        _err(f"DIM-1 合同源文件不存在: {contracts_path}")
        return contract_ids
    data = load_yaml(contracts_path)
    for section in data.get("contracts", []):
        if isinstance(section, dict) and "id" in section:
            contract_ids.add(section["id"])
    for section in data.get("ocp_extension_points", []):
        if isinstance(section, dict) and "id" in section:
            contract_ids.add(section["id"])
    for section in data.get("external_contracts", []):
        if isinstance(section, dict) and "id" in section:
            contract_ids.add(section["id"])
    for section in data.get("ai_governance_interfaces", []):
        if isinstance(section, dict) and "id" in section:
            contract_ids.add(section["id"])
    return contract_ids


def check_dim1_contract_refs() -> None:
    """DIM-1: 所有 layers/interfaces.contract_id → 存在合同定义"""
    contract_ids = _build_contract_registry()
    if not contract_ids:
        return

    for fname, data in _load_all_layer_yamls():
        modules = _get_modules(data)
        for mod in modules:
            module_id = mod.get("id", "?")
            for iface in mod.get("interfaces", []):
                cid = iface.get("contract_id", "")
                if not cid:
                    continue
                if cid not in contract_ids:
                    _err(
                        f"DIM-1 [{fname}] 模块 {module_id} 引用的 contract_id='{cid}' 在 cross_layer_contracts.yaml 中不存在"
                    )


# =============================================================================
# DIM-2: invariant_id 引用链
# =============================================================================


def _build_invariant_registry() -> set[str]:
    """_build_invariant_registry implementation."""
    iv_path = ARCH_MODEL / "cross-cutting" / "invariants.yaml"
    if not iv_path.exists():
        _err(f"DIM-2 不变量源文件不存在: {iv_path}")
        return set()
    data = load_yaml(iv_path)
    return {iv["id"] for iv in data.get("invariants", [])}


def check_dim2_invariant_refs() -> None:
    """DIM-2: 所有 layers/invariants.id → 存在不变量定义"""
    invariant_ids = _build_invariant_registry()
    if not invariant_ids:
        return

    for fname, data in _load_all_layer_yamls():
        for iv in _get_invariants(data):
            iid = iv.get("id", "")
            if not iid:
                continue
            if iid not in invariant_ids:
                _err(f"DIM-2 [{fname}] 引用的 invariant_id='{iid}' 在 invariants.yaml 中不存在")


# =============================================================================
# DIM-3: kb_ref 引用链
# =============================================================================


def _build_adr_registry() -> set[str]:
    """_build_adr_registry implementation — 从 KB SQLite 读取 ADR 条目。"""
    adr_ids: set[str] = set()
    db_path = REPO_ROOT / "data" / "zalpha_metadata.db"
    if db_path.exists():
        try:
            import sqlite3

            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.execute("SELECT ke_id FROM knowledge WHERE category = 'architecture_decision'")
                for row in cur:
                    adr_ids.add(row[0])
            finally:
                conn.close()
        except Exception:
            _warn(f"KB 数据库读取失败: {db_path}")
    else:
        _warn(f"KB 数据库不存在: {db_path}")
    if not ADR_DIR.exists():
        _warn(f"ADR 目录不存在: {ADR_DIR}")
        return adr_ids
    for f in ADR_DIR.glob("adr-*.md"):
        m = __import__("re").match(r"adr-(\d{4})", f.stem)
        if m:
            adr_ids.add(f"ADR-{m.group(1)}")
    return adr_ids


def _collect_all_adr_refs() -> list[tuple[str, str, str]]:
    """扫描所有架构 YAML 中的 kb_ref/adr_ref 引用 → [(文件名, 模块id, adr值)]"""
    refs: list[tuple[str, str, str]] = []

    for fname, data in _load_all_layer_yamls():
        modules = _get_modules(data)
        for mod in modules:
            module_id = mod.get("id", "?")
            kb_ref = mod.get("kb_ref") or mod.get("adr_ref", [])
            if isinstance(kb_ref, list):
                for a in kb_ref:
                    refs.append((fname, module_id, a))
            elif isinstance(kb_ref, str) and kb_ref:
                refs.append((fname, module_id, kb_ref))

    # Also check invariants.yaml
    iv_path = ARCH_MODEL / "cross-cutting" / "invariants.yaml"
    if iv_path.exists():
        data = load_yaml(iv_path)
        for iv in data.get("invariants", []):
            adr = iv.get("kb_ref") or iv.get("adr_ref", "")
            if adr:
                refs.append(("invariants.yaml", iv.get("id", "?"), adr))

    # contracts
    ct_path = ARCH_MODEL / "contracts" / "cross_layer_contracts.yaml"
    if ct_path.exists():
        data = load_yaml(ct_path)
        for section in data.get("contracts", []):
            if isinstance(section, dict):
                adrs = section.get("related_adrs", [])
                for a in adrs:
                    refs.append(("cross_layer_contracts.yaml", section.get("id", "?"), a))

    return refs


def check_dim3_adr_refs() -> None:
    """DIM-3: 所有 kb_ref/adr_ref → 存在 KB 决策记录条目"""
    adr_ids = _build_adr_registry()
    if not adr_ids:
        return

    for fname, mid, adr in _collect_all_adr_refs():
        if adr not in adr_ids:
            _err(f"DIM-3 [{fname}] 模块 {mid} 引用的 kb_ref/adr_ref='{adr}' 在 KB decisions 中无对应条目")


# =============================================================================
# DIM-4: invariant.owner → _index.yaml partition
# =============================================================================


def _build_partition_registry() -> set[str]:
    """_build_partition_registry implementation."""
    idx_path = ARCH_MODEL / "index.yaml"
    if not idx_path.exists():
        _err(f"DIM-4 index.yaml 不存在: {idx_path}")
        return set()
    data = load_yaml(idx_path)
    pids: set[str] = set()
    for p in data.get("partitions", []):
        pid = p.get("id", "")
        if pid:
            pids.add(pid)
    return pids


def check_dim4_invariant_owner() -> None:
    """DIM-4: 每个 invariant.owner → 对应 _index.yaml 中的 partition id"""
    partition_ids = _build_partition_registry()
    if not partition_ids:
        return

    iv_path = ARCH_MODEL / "cross-cutting" / "invariants.yaml"
    if not iv_path.exists():
        return
    data = load_yaml(iv_path)
    for iv in data.get("invariants", []):
        owner = iv.get("owner", "")
        iid = iv.get("id", "?")
        if not owner:
            continue
        # owner like "l04-risk-management" → partition id "l04"
        # owner like "shared-contracts" → partition id "shared"
        base = owner.split("-")[0]
        if base not in partition_ids:
            _err(f"DIM-4 [{iid}] invariant owner='{owner}' 的根分区 '{base}' 不在 _index.yaml partitions 中")


# =============================================================================
# DIM-5: contract.source_layer → _index.yaml partition
# =============================================================================


def check_dim5_contract_source_layer() -> None:
    """DIM-5: 每个 contract.source_layer → 对应 _index.yaml 中的 partition id"""
    partition_ids = _build_partition_registry()
    if not partition_ids:
        return

    ct_path = ARCH_MODEL / "contracts" / "cross_layer_contracts.yaml"
    if not ct_path.exists():
        return
    data = load_yaml(ct_path)
    for section in data.get("contracts", []):
        if not isinstance(section, dict):
            continue
        sl = section.get("source_layer", "")
        cid = section.get("id", "?")
        if not sl:
            continue
        if sl not in partition_ids:
            _err(f"DIM-5 [{cid}] source_layer='{sl}' 不在 _index.yaml partitions 中")


# =============================================================================
# DIM-6: 聚合根 events_published → domain_events.yaml
# =============================================================================


def _build_event_registry() -> set[str]:
    """_build_event_registry implementation."""
    ev_path = ARCH_MODEL / "events" / "domain_events.yaml"
    if not ev_path.exists():
        _warn(f"DIM-6 事件源文件不存在: {ev_path}")
        return set()
    data = load_yaml(ev_path)
    return {e["id"] for e in data.get("events", [])}


def check_dim6_aggregate_events() -> None:
    """DIM-6: 聚合根 events_published → domain_events.yaml 中的事件 ID"""
    event_ids = _build_event_registry()
    if not event_ids:
        return

    ddd_path = ARCH_MODEL / "domain" / "ddd_model.yaml"
    if not ddd_path.exists():
        return
    data = load_yaml(ddd_path)
    for agg in data.get("aggregate_roots", []):
        agg_id = agg.get("id", "?")
        for ep in agg.get("events_published", []):
            if ep not in event_ids:
                _err(f"DIM-6 [{agg_id}] events_published='{ep}' 不在 domain_events.yaml 中")


# =============================================================================
# DIM-7: 反向扫描 — 合同孤儿检测
# =============================================================================


def _collect_all_referenced_contract_ids() -> set[str]:
    """从所有层 YAML 的 interfaces.contract_id 收集已引用的合同 ID"""
    refs: set[str] = set()
    for _fname, data in _load_all_layer_yamls():
        modules = _get_modules(data)
        for mod in modules:
            for iface in mod.get("interfaces", []):
                cid = iface.get("contract_id", "")
                if cid:
                    refs.add(cid)
    return refs


def check_dim7_orphan_contracts() -> None:
    """DIM-7: cross_layer_contracts.yaml 中未被任何层引用的合同（P1 级别警告，P0 报错）"""
    contract_ids = _build_contract_registry()
    referenced = _collect_all_referenced_contract_ids()
    if not contract_ids:
        return

    for cid in sorted(contract_ids):
        if cid not in referenced:
            if cid.startswith(("CTR-P1-", "EXT-", "AI-GOV-")):
                _warn(f"DIM-7 合同 '{cid}' 未被任何层 YAML 引用（可能是设计缺口或外部合同）")
            else:
                _err(f"DIM-7 合同 '{cid}' 未被任何层 YAML 引用（P0 核心合同必须分配层归属）")


# =============================================================================
# DIM-8: module_id 注册链
# =============================================================================


def _build_module_id_registry() -> set[str]:
    """_build_module_id_registry implementation."""
    reg_path = ARCH_MODEL / "module_id_registry.yaml"
    if not reg_path.exists():
        _warn(f"DIM-8 module_id_registry.yaml 不存在: {reg_path}")
        return set()
    data = load_yaml(reg_path)
    return {entry["module_id"] for entry in data.get("registered_ids", [])}


def check_dim8_module_id_registry() -> None:
    """DIM-8: layers 模块 id 是否在 module_id_registry.yaml 中登记（P1 警告）"""
    registered = _build_module_id_registry()
    if not registered:
        return

    for fname, data in _load_all_layer_yamls():
        modules = _get_modules(data)
        for mod in modules:
            mid = mod.get("id", "")
            if not mid:
                continue
            if mid.startswith(("MOD-", "infra-", "core-", "l", "fe-", "shared-", "scripts-")):
                continue
            if mid not in registered:
                _warn(f"DIM-8 [{fname}] 模块 id='{mid}' 未在 module_id_registry.yaml 登记（可能是新模块待注册）")


# =============================================================================
# DIM-9: 废弃文件引用检测
# =============================================================================

_DEPRECATED_FILE_NAMES = [
    "master-document-inventory-registry.md",
    "governance-rules-master-registry.yaml",
]

_DEPRECATED_FILE_PATTERNS = [
    re.compile(r"master-document-inventory\.yaml"),
    re.compile(r"governance-rules-master-registry\.yaml"),
]


def _build_deprecated_file_set() -> dict[str, Path]:
    """扫描 01_policies_and_standards/ 下所有 status: deprecated 的文件，
    返回 {文件名: Path} 映射（用于按文件名匹配引用）"""
    deprecated: dict[str, Path] = {}
    if not GOV_DOCS_DIR.exists():
        return deprecated
    for f in iter_files(GOV_DOCS_DIR, {".md", ".yaml", ".yml"}, EXCLUDE_DIRS):
        fm_raw = parse_frontmatter_from_file(f)
        fm = fm_raw[0] if isinstance(fm_raw, tuple) else fm_raw
        if fm and fm.get("status") == "deprecated":
            deprecated[f.name] = f
    for name in _DEPRECATED_FILE_NAMES:
        for parent in [GOV_DOCS_DIR / "_registry" / "catalogs", GOV_DOCS_DIR / "governance", GOV_DOCS_DIR / "meta"]:
            candidate = parent / name
            if candidate.exists():
                deprecated[name] = candidate
    return deprecated


def check_dim9_deprecated_refs() -> None:
    """DIM-9: 所有 .md/.yaml 中引用已废弃文件（status: deprecated）

    检测逻辑：
    1. 扫描 01_policies_and_standards/ 下所有 .md/.yaml 文件
    2. 在文件内容中搜索废弃文件名
    3. 排除自身引用（废弃文件引用自己）和桩文件的重定向提示
    4. 排除 rule_catalog_registry.yaml（auto-generated，含历史路径记录）
    5. 每个源文件+废弃文件对只报告一次
    """
    deprecated = _build_deprecated_file_set()
    if not deprecated:
        return

    deprecated_names = set(deprecated.keys())

    scan_files = iter_files(GOV_DOCS_DIR, {".md", ".yaml", ".yml"}, EXCLUDE_DIRS)

    for f in scan_files:
        if f.name in ("rule_catalog_registry.yaml",):
            continue

        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        fm_raw = parse_frontmatter_from_file(f)
        fm = fm_raw[0] if isinstance(fm_raw, tuple) else fm_raw
        if fm and fm.get("status") == "deprecated":
            continue

        rel = f.relative_to(GOV_DOCS_DIR)
        found_in_file: set[str] = set()

        for dep_name in sorted(deprecated_names):
            if dep_name in f.name:
                continue
            if dep_name in found_in_file:
                continue
            if dep_name not in content:
                continue

            in_redirect = False
            for pattern in _DEPRECATED_FILE_PATTERNS:
                for m in pattern.finditer(content):
                    start = max(0, m.start() - 60)
                    end = min(len(content), m.end() + 60)
                    context = content[start:end].replace("\n", " ").strip()
                    if any(
                        kw in context
                        for kw in (
                            "superseded_by",
                            "已迁移",
                            "本桩文件",
                            "已废弃",
                            "取代旧的",
                            "deprecated",
                            "原 governance-rules",
                        )
                    ):
                        in_redirect = True
                        break
                if in_redirect:
                    break

            if not in_redirect:
                found_in_file.add(dep_name)

        if found_in_file:
            _warn(f"DIM-9 [{rel}] 引用已废弃文件: {', '.join(sorted(found_in_file))}")


# =============================================================================
# DIM-10: 断裂路径引用检测
# =============================================================================

_PATH_REF_PATTERN = re.compile(
    r"(?:docs/01_policies_and_standards/|_registry/|governance/|meta/|operational/|domains/|templates/)"
    r"[\w/\-\.]+\.(?:md|yaml|yml|json)",
)

_ANCHOR_PATTERN = re.compile(
    r"\[([^\]]*)\]\(([^)]+)\)",
)


def _resolve_ref(ref_path: str, source_file: Path) -> Path | None:
    """将引用路径解析为绝对路径

    支持的路径格式：
    - 绝对仓库路径: docs/01_policies_and_standards/...
    - 相对路径: ../_registry/catalogs/xxx.yaml
    - file:/// 绝对 URL: 提取路径部分
    """
    if ref_path.startswith("file:///"):
        ref_path = ref_path[7:].lstrip("/")
        if len(ref_path) > 1 and ref_path[1] == ":":
            return Path(ref_path)
    if ref_path.startswith("docs/"):
        return REPO_ROOT / ref_path
    if ref_path.startswith("/"):
        return REPO_ROOT / ref_path.lstrip("/")
    return source_file.parent / ref_path


def check_dim10_broken_path_refs() -> None:
    """DIM-10: 所有 .md 中的文件路径引用 → 目标文件存在性

    检测逻辑：
    1. 扫描 01_policies_and_standards/ 下所有 .md 文件
    2. 提取 Markdown 链接
    3. 解析路径并验证目标文件存在
    4. 排除 URL（http/https）、锚点链接、图片链接
    5. 排除 file:/// 链接（VS Code 风格，已由 DIM-9 覆盖废弃检测）
    """
    scan_files = iter_files(GOV_DOCS_DIR, {".md"}, EXCLUDE_DIRS)

    seen: set[tuple[str, str]] = set()

    for f in scan_files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        fm_raw = parse_frontmatter_from_file(f)
        fm = fm_raw[0] if isinstance(fm_raw, tuple) else fm_raw
        if fm and fm.get("status") == "deprecated":
            continue

        for m in _ANCHOR_PATTERN.finditer(content):
            link_text = m.group(1)
            link_target = m.group(2).split("#")[0].split("?")[0]
            if not link_target:
                continue
            if link_target.startswith(("http://", "https://", "mailto:", "#", "file:///")):
                continue
            if link_target.startswith("/"):
                continue
            if not any(link_target.endswith(ext) for ext in (".md", ".yaml", ".yml", ".json")):
                continue

            dedup_key = (str(f.relative_to(GOV_DOCS_DIR)), link_target)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            resolved = _resolve_ref(link_target, f)
            if not resolved or not resolved.exists():
                rel = f.relative_to(GOV_DOCS_DIR)
                _warn(f"DIM-10 [{rel}] Markdown 链接断裂: [{link_text}]({link_target})")


# =============================================================================
# 主入口
# =============================================================================


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="架构模型 YAML 跨引用完整性闸门（GATE-XREF）")
    parser.add_argument("--warn-only", action="store_true", help="即使发现错误也返回 exit 0（CI 审计模式，不阻塞）")
    args = parser.parse_args()

    print("=" * 72)
    print("GATE-XREF: 架构模型 + 治理文档跨引用完整性闸门 v2.0.0")
    print("=" * 72)
    print()

    checks = [
        ("DIM-1: contract_id → 合同定义存在性", check_dim1_contract_refs),
        ("DIM-2: invariant_id → 不变量定义存在性", check_dim2_invariant_refs),
        ("DIM-3: kb_ref/adr_ref → KB 决策记录存在性", check_dim3_adr_refs),
        ("DIM-4: invariant.owner → _index.yaml partition", check_dim4_invariant_owner),
        ("DIM-5: contract.source_layer → _index.yaml partition", check_dim5_contract_source_layer),
        ("DIM-6: 聚合根 events_published → 事件定义", check_dim6_aggregate_events),
        ("DIM-7: 反向扫描 — 孤儿合同检测", check_dim7_orphan_contracts),
        ("DIM-8: 模块 id → module-id-registry 登记", check_dim8_module_id_registry),
        ("DIM-9: 废弃文件引用检测", check_dim9_deprecated_refs),
        ("DIM-10: 断裂路径引用检测", check_dim10_broken_path_refs),
    ]

    for label, fn in checks:
        print(f"  {label} ...", end=" ", flush=True)
        before_errors = len(_errors)
        before_warnings = len(_warnings)
        fn()
        new_errors = len(_errors) - before_errors
        new_warnings = len(_warnings) - before_warnings
        if new_errors > 0:
            print(f"❌ {new_errors} error(s)")
        elif new_warnings > 0:
            print(f"⚠️ {new_warnings} warning(s)")
        else:
            print("✅ PASS")

    print()

    if _errors:
        print(f"🔴 错误 ({len(_errors)}):")
        for e in _errors:
            print(f"   {e}")
        print()

    if _warnings:
        print(f"🟡 警告 ({len(_warnings)}):")
        for w in _warnings:
            print(f"   {w}")
        print()

    if not _errors and not _warnings:
        print("✅ GATE-XREF 全部通过 — 所有跨引用链完整无断裂")
        return EXIT_PASS
    if _errors:
        print(f"🔴 GATE-XREF 发现 {len(_errors)} 个引用断裂")
        if args.warn_only:
            print("   (--warn-only 模式，exit 0)")
            return EXIT_PASS
        return EXIT_FINDINGS
    else:
        print(f"🟡 GATE-XREF 通过（有 {len(_warnings)} 个设计性警告）")
        return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
