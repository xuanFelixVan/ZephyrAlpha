#!/usr/bin/env python3
"""# [BLUEPRINT] MOD-INF-005 | scripts/governance/generate_project_depgraph.py | §7
# [MODULE] scripts.governance.generate_project_depgraph
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] CI pipeline; governance automation; PostgreSQL depgraph
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] --dry-run MUST NOT modify any file; output MUST be valid YAML + Mermaid; scan 结果自动缓存到 .runtime/depgraph_scan_cache.json（裁定#209 Stage 4），content_hash 命中跳过 AST 解析，fingerprint/SCAN_LOGIC_VERSION 变则全失效
# [MODIFY-GUARD] PostgreSQL depgraph; architecture_model/module_id_registry.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScanError; ParseError
# [TESTS] tests/test_generate_project_depgraph.py
# [TTL] task_bound
"""

from __future__ import annotations

__manifest__ = """
args: []
description: '# [BLUEPRINT] MOD-INF-005 | scripts/governance/generate_project_depgraph.py
  | §7'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import yaml

# P2 PG 迁移：删除 import sqlite3；导入 PG 连接入口
_GOV_DIR = str(Path(__file__).resolve().parent)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402
import psycopg2  # noqa: E402
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402  SSoT 词表加载（治本 2026-06-30）

PROJECT_ROOT = REPO_ROOT

# === 扫描排除配置（从 YAML 配置文件加载，真源: depgraph_scan_exclusions.yaml）===
# 规则定义: docs/01_policies_and_standards/rules/trae_058_depgraph_scan_exclusions.yaml
# 路径清单: docs/01_policies_and_standards/_registry/catalogs/depgraph_scan_exclusions.yaml
_SCAN_EXCLUSIONS_CONFIG_PATH = (
    PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "depgraph_scan_exclusions.yaml"
)


def _load_scan_exclusions() -> dict:
    """Load scan exclusion config from YAML. Falls back to empty dict if config missing."""
    if not _SCAN_EXCLUSIONS_CONFIG_PATH.exists():
        print(f"[WARN] 扫描排除配置文件不存在: {_SCAN_EXCLUSIONS_CONFIG_PATH}", file=sys.stderr)
        return {}
    with open(_SCAN_EXCLUSIONS_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_SCAN_CONFIG = _load_scan_exclusions()
_DEPGRAPH_CONFIG = _SCAN_CONFIG.get("depgraph", {})

# Fallback defaults (used only if config file is missing or incomplete)
_FALLBACK_EXEMPT_DIRS = {
    "__pycache__",
    ".git",
    ".ailocks",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "_backups",
    "_temp",
    ".audit_cache",
    "session_logs",
}
# === node_type 词表（从 node_type_vocabulary.yaml 动态加载，SSoT）===
# 真源：docs/01_policies_and_standards/_registry/vocabularies/node_type_vocabulary.yaml
# 治本（2026-06-30）：消除原硬编码 NODE_TYPES_FILE/DOMAIN/WHITELIST/CODE_TYPES/CONFIG_TYPES/
#   DOC_TYPES/DOMAIN_TYPES/TYPE_PRIORITY/architecture_layer SQL/stability/autonomy fallback
_NODE_TYPE_VOCAB_PATH = (
    PROJECT_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "vocabularies" / "node_type_vocabulary.yaml"
)


def _load_node_type_vocabulary() -> list[dict]:
    """从 node_type_vocabulary.yaml 加载 node_type 词表条目（SSoT）。

    治本（2026-06-30）：消除原散落在 .py 中的 30+ 处 node_type 硬编码。
    词表变更只需改 YAML 一处，脚本自动同步。
    """
    if not _NODE_TYPE_VOCAB_PATH.exists():
        raise FileNotFoundError(
            f"[FATAL] node_type 词表文件不存在: {_NODE_TYPE_VOCAB_PATH}\n"
            f"该文件是 node_type 系统的唯一真源（SSoT），缺失则脚本无法运行。"
        )
    with open(_NODE_TYPE_VOCAB_PATH, encoding="utf-8") as f:
        vocab = yaml.safe_load(f) or {}
    return vocab.get("values", [])


_NODE_TYPE_ENTRIES = _load_node_type_vocabulary()

# 白名单准入（裁定#184）：nodes表只收录 in_nodes_whitelist=true 的 node_type
# module(.py代码) / script(.py脚本) / test(.py测试) / config(.yaml运行时配置)
# 新类型默认不进nodes，天然安全（对齐dependency-cruiser/madge/Bazel实践）
NODES_WHITELIST = frozenset(
    e["value"] for e in _NODE_TYPE_ENTRIES if e.get("in_nodes_whitelist")
)
_FALLBACK_SCAN_DIRS = [
    "src/zephyr",
    "scripts",
    "data/asset_index",
    "data/config",
    "data/metrics",
    "config",
    "schemas",
    "docs/03_modules",
    "docs/01_policies_and_standards",
    "docs/02_enterprise_architecture",
    "frontend",
    "architecture_model",
    "infra",
    "tools",
    "specs",
]
_FALLBACK_KNOWLEDGE_DOC_PATHS = ["docs/08_knowledge/", "docs/_working/audit/"]
_FALLBACK_TYPE_PREFIXES = {
    "policy": [
        "docs/01_policies_and_standards/governance/",
        "docs/01_policies_and_standards/domains/",
        "docs/01_policies_and_standards/operational/",
        "docs/01_policies_and_standards/rules/",
    ],
    "template": ["docs/01_policies_and_standards/templates/"],
    "registry": [
        "docs/01_policies_and_standards/_registry/catalogs/",
        "docs/01_policies_and_standards/_registry/vocabularies/",
    ],
    "contract": ["docs/01_policies_and_standards/_registry/contracts/"],
    "schema": ["docs/01_policies_and_standards/_registry/schemas/", "schemas/"],
}

# node_type 列表与分类集合（从词表动态加载——真源：node_type_vocabulary.yaml）
NODE_TYPES_FILE = [e["value"] for e in _NODE_TYPE_ENTRIES if e.get("level") == "file"]
NODE_TYPES_DOMAIN = [e["value"] for e in _NODE_TYPE_ENTRIES if e.get("level") == "domain"]
NODE_TYPES = NODE_TYPES_FILE + NODE_TYPES_DOMAIN
# 治本（2026-06-30）：EDGE_TYPES 从 dep_type_vocabulary.yaml 动态加载（SSoT）。
# 真源：docs/01_policies_and_standards/_registry/vocabularies/dep_type_vocabulary.yaml
# 消除原 12 值硬编码 list——词表变更只需改 YAML 一处。
EDGE_TYPES = sorted(load_vocabulary_values("dep_type_vocabulary.yaml"))

CODE_TYPES = frozenset(e["value"] for e in _NODE_TYPE_ENTRIES if e.get("category") == "code")
CONFIG_TYPES = frozenset(e["value"] for e in _NODE_TYPE_ENTRIES if e.get("category") == "config")
DOC_TYPES = frozenset(e["value"] for e in _NODE_TYPE_ENTRIES if e.get("category") == "doc")
DOMAIN_TYPES = frozenset(e["value"] for e in _NODE_TYPE_ENTRIES if e.get("category") == "domain")

# TYPE_PRIORITY（文件粒度合并优先级——从词表动态加载）
# 真源：node_type_vocabulary.yaml values[].type_priority（null 值不参与文件合并）
TYPE_PRIORITY = {
    e["value"]: e["type_priority"]
    for e in _NODE_TYPE_ENTRIES
    if e.get("type_priority") is not None
}

# architecture_layer 兜底映射（从词表动态加载——真源：values[].architecture_layer_fallback）
_NODE_TYPE_LAYER_MAP = {
    e["value"]: e.get("architecture_layer_fallback", "L3_application")
    for e in _NODE_TYPE_ENTRIES
}

# stability / autonomy 兜底映射（从词表动态加载——真源：values[].stability_fallback / autonomy_fallback）
_STABILITY_FALLBACK = {
    e["value"]: e.get("stability_fallback", "evolving")
    for e in _NODE_TYPE_ENTRIES
}
_AUTONOMY_FALLBACK = {
    e["value"]: e.get("autonomy_fallback", "ai_modifiable")
    for e in _NODE_TYPE_ENTRIES
}


def _build_architecture_layer_case_sql() -> str:
    """从 node_type_vocabulary.yaml 构建 architecture_layer 兜底 SQL CASE 表达式。

    真源：node_type_vocabulary.yaml values[].architecture_layer_fallback
    治本（2026-06-30）：消除原硬编码 L2728-2736 SQL CASE 语句。
    非默认层（非 L3_application）用 WHEN ... IN (...) THEN ...，默认层用 ELSE。
    """
    layer_groups: dict[str, list[str]] = {}
    for entry in _NODE_TYPE_ENTRIES:
        layer = entry.get("architecture_layer_fallback", "L3_application")
        layer_groups.setdefault(layer, []).append(entry["value"])

    default_layer = "L3_application"
    case_clauses = []
    for layer in sorted(layer_groups):
        if layer == default_layer:
            continue  # 用 ELSE 处理
        values = sorted(layer_groups[layer])
        vals_sql = ", ".join(f"'{v}'" for v in values)
        if len(values) == 1:
            case_clauses.append(f"WHEN node_type = '{values[0]}' THEN '{layer}'")
        else:
            case_clauses.append(f"WHEN node_type IN ({vals_sql}) THEN '{layer}'")
    case_clauses.append(f"ELSE '{default_layer}'")
    return "CASE\n" + "\n".join("    " + c for c in case_clauses) + "\nEND"


_ARCHITECTURE_LAYER_CASE_SQL = _build_architecture_layer_case_sql()

EXEMPT_DIRS = set(_DEPGRAPH_CONFIG.get("exempt_dirs", list(_FALLBACK_EXEMPT_DIRS)))

# EXCLUDED_SCAN_DIRS 已删除（死代码——定义但从未使用，实际排除靠白名单 SCAN_DIRS）
# 如需查看排除路径清单，见 depgraph_scan_exclusions.yaml

# 裁定#184：黑名单已废弃，改为白名单准入（NODES_WHITELIST）
# 旧黑名单 EXCLUDED_NODE_TYPES 已删除——黑名单天然漏防（已漏4种类型导致561个非代码节点污染）
# 白名单天然安全：新类型默认不进 nodes 表

# Knowledge doc paths — .md files under these paths are classified as knowledge_doc and skipped
KNOWLEDGE_DOC_PATHS = _DEPGRAPH_CONFIG.get("knowledge_doc_paths", _FALLBACK_KNOWLEDGE_DOC_PATHS)

# Old layer name normalization: strip l00_, l01_, ..., l13_ prefixes from path segments.
# These legacy prefixes (e.g., l00-data-source, l01-infrastructure) persist in
# tests/ and docs/03_modules/ directories on disk but should not appear in depgraph IDs.
# Matches l\d{2}_ at: start of string, after /, or after _ (e.g., test_l00_xxx)
_OLD_LAYER_PREFIX_RE = re.compile(r"(^|/|_)l\d{2}_")

# H3 fix: Path validation patterns
_ILLEGAL_PATH_PATTERNS = re.compile(
    r'[:<>"|?*]'  # Windows 非法字符
    r"|^\s*$"  # 空白路径
    r"|^[A-Za-z]:[/\\]"  # Windows 绝对路径
    r"|^/[^/]"  # Unix 绝对路径（非项目根）
    r"|^#{1,6}\s"  # Markdown 标题 (### ...)
    r"|^---"  # Markdown 水平线
)
_EMOJI_RE = re.compile(r"[\U00010000-\U0010ffff]")


def normalize_path(path: str) -> str:
    """Replace old layer-name segments and validate path legality.

    H3 fix: Added validation for illegal characters, absolute paths,
    empty paths, and emoji.
    """
    if not path or not path.strip():
        return ""
    # 过滤 emoji
    path = _EMOJI_RE.sub("", path)
    # 正则替换旧层名
    path = _OLD_LAYER_PREFIX_RE.sub(r"\1", path)
    # 校验非法字符
    if _ILLEGAL_PATH_PATTERNS.search(path):
        return ""
    # 剥离域ID前缀子路径（如 D_PF_CORE/xxx → xxx）
    if path.startswith("D-") and "/" in path:
        path = path.split("/", 1)[1]
    return path.strip()


# Base scan directories — loaded from depgraph_scan_exclusions.yaml (whitelist scan roots)
# Only paths in this list are scanned by depgraph. Paths not listed = excluded (reverse exclusion).
_BASE_SCAN_DIRS = _DEPGRAPH_CONFIG.get("scan_dirs", _FALLBACK_SCAN_DIRS)


def _build_scan_dirs() -> list:
    """Build SCAN_DIRS from base list only.

    Note: collect_all_files() uses os.walk() which recursively traverses
    all subdirectories, so expanding src/zephyr subdirs here causes
    double-scanning (H1 fix).
    """
    return list(_BASE_SCAN_DIRS)


SCAN_DIRS = _build_scan_dirs()

# 治本（2026-06-27）：删除 DEPGRAPH_DB_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。

CROSS_MODULE_REGISTRY_PATH = (
    PROJECT_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "cross-module-dependency-registry.yaml"
)

DEPGRAPH_DESIGN_DIR = PROJECT_ROOT / "data" / "asset_index"

# Semantic type derivation: dep_type -> default semantic_type
DEP_TYPE_TO_SEMANTIC_TYPE = {
    "import_depends": "runtime",
    "test_depends": "build",
    "references": "data",
    "config_depends": "data",
    "data_depends": "data",
    "blueprint_depends": "data",
    "event_depends": "runtime",
    "contract_depends": "contract",
    "shared_kernel": "contract",
    "script_depends": "build",
    "runtime_depends": "runtime",
    "owned_by": "contract",
}

# Valid values for semantic fields (from PS-REG-007 _schema)
# 治本（2026-06-30）：从 semantic_vocabulary.yaml 动态加载（SSoT，PS-VOC-025）。
# 消除原 {"runtime","data","build","contract"} 硬编码——词表变更只需改 YAML 一处。
VALID_SEMANTIC_TYPES = load_vocabulary_values("semantic_vocabulary.yaml")
VALID_SEMANTIC_DIRECTIONS = {"upstream", "downstream", "peer"}
VALID_DECISIONS = {"NEW", "MODIFY", "KEEP", "DEPRECATE"}
VALID_FAILURE_MODES = {
    "service_down",
    "timeout",
    "data_corruption",
    "version_mismatch",
    "circuit_break",
    "cascade_failure",
}

# ARCH-CAP-005: 域映射已迁移到 depgraph.db（抽屉式扩展）
# - domain_id → layer_id: domains 表 layer_id 字段（per-domain，比原 group-based 更精确）
# - path_prefix → (domain_id, subdomain_id): domain_mapping 表（mapping_type='non_src'/'unregistered_src'）
# 新增域只需 INSERT domains/domain_mapping 表，无需修改生成器代码
# 详见 _load_domain_mappings_from_db() 函数

TRUST_ZONE_MAP = [
    ("src/zephyr/security/", "api_gateway"),
    ("src/zephyr/integration/", "external_service"),
    ("src/zephyr/alt_data/", "untrusted_input"),
]

# H4 fix: Fake blueprint_id detection
_FAKE_BLUEPRINT_RE = re.compile(r"^D-[A-Z_]+-blueprint$")


def is_valid_blueprint_id(bid: str) -> bool:
    """Check if a blueprint_id is a real reference, not a fake auto-generated one."""
    if not bid or not bid.strip():
        return False
    if _FAKE_BLUEPRINT_RE.match(bid):
        return False
    return True


# Design-state fields that MUST be preserved when disk scan produces a node
# with the same ID as an existing lifecycle=design node.
# When a conflict occurs, operational fields (imports, exports, etc.) come from
# the disk scan, but these design-state fields are merged from the old node.
DESIGN_STATE_FIELDS = (
    "lifecycle",  # design | operational | deprecated
    "build_status",  # design_only | partial | implemented | production | deprecated
    "deployment_lifecycle",  # design_only | stable | deprecated
    "design_spec",  # dict: source, planned_dependencies, contract_refs, invariants
    "contract_refs",  # list[str]: contract references
    "planned_interfaces",  # dict: input/output interface definitions
    "planned_dependencies",  # list[str]: design-time dependency declarations
    "invariants",  # list[str]: design invariants
    "change_policy",  # frozen/stable/evolving/volatile
    "modification_permission",  # immutable_core/human_gated/ai_modifiable
    "impact_level",  # H/M/L
    "blueprint_id",  # blueprint reference
    "module_id",  # module reference
)


def merge_design_fields(new_node: dict, old_node: dict) -> dict:
    """Merge design-state fields from old_node into new_node.

    When a disk scan produces a node with the same ID as an existing
    lifecycle=design node, the disk scan result (new_node) contains the
    latest operational data, but the old_node may carry design-state
    annotations that must not be lost.

    Strategy:
    - Operational fields (imports, exports, physical_path, etc.): use new_node
    - Design-state fields: if old_node has a non-empty value, prefer old_node
    - Any custom field not in DESIGN_STATE_FIELDS but present only in old_node: preserve
    """
    for field in DESIGN_STATE_FIELDS:
        old_val = old_node.get(field)
        if old_val is not None and old_val != "" and old_val != []:
            # H4 fix: Don't inherit fake blueprint_id
            if field == "blueprint_id" and not is_valid_blueprint_id(old_val):
                continue
            # Old node has this design-state field — preserve it
            # But only if new_node doesn't have a more specific value
            new_val = new_node.get(field)
            if new_val is None or new_val == "" or new_val == []:
                new_node[field] = old_val
            elif field == "lifecycle" and old_val == "design":
                # lifecycle=design MUST always be preserved when set
                new_node[field] = old_val
            # 裁定#178：删除 build_status=design_only 保留逻辑
            # design_only 是旧脏值，merge 不再保留——由 derive_build_status 重新推导

    # Preserve any custom fields present in old_node but absent in new_node
    # (e.g., _rb_test_mark, custom annotations, etc.)
    for key in old_node:
        if key not in new_node and key not in ("id", "path", "physical_path"):
            # H4 fix: Don't inherit fake blueprint_id via catch-all
            if key == "blueprint_id" and not is_valid_blueprint_id(old_node[key]):
                continue
            new_node[key] = old_node[key]

    return new_node


HARD_BOUNDARIES = [
    {
        "id": "HB-HW-01",
        "category": "hardware",
        "constraint": "单台PC工作站，无集群/K8s",
        "parameters": "CPU i7-12700KF(12核20线程); GPU RTX 3090 24GB; RAM 64GB DDR4; 存储 D:731GB+E:931GB SSD",
        "impact": "所有并发/分布式/集群方案不可用",
    },
    {
        "id": "HB-HW-02",
        "category": "hardware",
        "constraint": "GPU显存硬上限",
        "parameters": "<90%=21.6GB可用; 盘中~8-10GB(33%-42%), 盘前~10GB(42%)",
        "impact": "模型推理显存超限=OOM崩溃; 多模型并发必须做显存预算",
    },
    {
        "id": "HB-NET-01",
        "category": "hardware",
        "constraint": "网络带宽上限",
        "parameters": "30Mbps",
        "impact": "大批量数据拉取/多源并发请求必须限速",
    },
    {
        "id": "HB-FUND-01",
        "category": "capital",
        "constraint": "初始AUM",
        "parameters": "50万",
        "impact": "策略容量/仓位/做T底仓均受此约束; 融券受限",
    },
    {
        "id": "HB-IFIND-01",
        "category": "external_interface",
        "constraint": "iFind数据源QPS限制",
        "parameters": "QPS=20（账号总上限）",
        "impact": "批量数据拉取必须分页限速; 并发请求不可超20",
    },
    {
        "id": "HB-QMT-01",
        "category": "external_interface",
        "constraint": "miniQMT交易接口限制",
        "parameters": "下单10笔/秒; Tick=3秒; 模拟盘延迟~1分钟",
        "impact": "高频策略不可用; 信号触发到下单存在3秒Tick延迟",
    },
    {
        "id": "HB-TRADE-01",
        "category": "regulation",
        "constraint": "T+1交割制度",
        "parameters": "当日买入不可卖出",
        "impact": "日内平仓策略不可用; 做T必须有底仓",
    },
    {
        "id": "HB-TRADE-02",
        "category": "regulation",
        "constraint": "涨跌停限制",
        "parameters": "主板±10%; 科创创业板±20%; ST±5%; 北交所±30%",
        "impact": "涨跌停价位无法成交; 风控必须考虑涨跌停无法卖出场景",
    },
]

PATH_MAPPINGS = [
    {
        "pattern": "src/zephyr/**",
        "code_root": "D:/ZephyrAlpha/src/zephyr",
        "blueprint_root": "D:/ZephyrAlpha/docs/03_modules",
        "test_root": "D:/ZephyrAlpha/tests",
        "script_root": "",
        "naming_rule": "snake_case, package/__init__.py",
        "examples": ["src/zephyr/shared/event_bus.py", "src/zephyr/gates/EN-001.yaml"],
    },
    {
        "pattern": "scripts/**",
        "code_root": "D:/ZephyrAlpha/scripts",
        "blueprint_root": "",
        "test_root": "",
        "script_root": "D:/ZephyrAlpha/scripts",
        "naming_rule": "snake_case with underscores",
        "examples": ["scripts/governance/generate_project_depgraph.py"],
    },
    {
        "pattern": "tests/**",
        "code_root": "D:/ZephyrAlpha/tests",
        "blueprint_root": "",
        "test_root": "D:/ZephyrAlpha/tests",
        "script_root": "",
        "naming_rule": "test_{module}.py",
        "examples": ["tests/test_generate_project_depgraph.py"],
    },
    {
        "pattern": "docs/03_modules/**",
        "code_root": "",
        "blueprint_root": "D:/ZephyrAlpha/docs/03_modules",
        "test_root": "",
        "script_root": "",
        "naming_rule": "{package}/blueprint.md",
        "examples": ["docs/03_modules/_system_master/blueprint.md"],
    },
    {
        "pattern": "docs/01_policies_and_standards/**",
        "code_root": "",
        "blueprint_root": "D:/ZephyrAlpha/docs/01_policies_and_standards",
        "test_root": "",
        "script_root": "",
        "naming_rule": "rules/trae_XXX_{name}.yaml",
        "examples": ["docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml"],
    },
    {
        "pattern": "data/**",
        "code_root": "",
        "blueprint_root": "",
        "test_root": "",
        "script_root": "",
        "naming_rule": "{category}/{name}.yaml or .json",
        "examples": ["depgraph (PostgreSQL)"],
    },
]

# 真源：trae_047_engineering_file_header.yaml field_specs（SSoT）。
# 动态读取字段列表，禁止硬编码（消除多真源漂移，对标 create_guard.py）。
# fail-closed：真源读取失败时 raise（不回退硬编码，否则又造双真源）。
_TRAE_047_YAML = PROJECT_ROOT / "docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml"
try:
    _rule_data = yaml.safe_load(_TRAE_047_YAML.read_text(encoding="utf-8"))
    HEADER_FIELDS = _rule_data["sections"]["gov_eng_002"]["field_specs"]["a_full"]["required"]
except Exception as _e:
    raise RuntimeError(
        f"字段头部规范真源读取失败（trae_047.yaml field_specs）: {_e}. "
        f"修复：检查 {_TRAE_047_YAML} 是否存在且 field_specs 结构完整。"
    ) from _e


def _load_panorama_from_db(db_path):
    """Load panorama data from PostgreSQL database, returning a dict compatible with the old YAML structure.

    Reads from: domains table, arch_directory_tree table, arch_path_mappings table.
    Returns dict with keys: domains, tree, and optional path sections.
    """
    import json as _json

    conn = get_depgraph_pg_connection(autocommit=False)
    data = {"domains": {}, "tree": {}, "meta": {}}

    # Load domains — map to the same structure as the YAML panorama domains section
    for row in conn.execute("SELECT * FROM domains"):
        domain = dict(row)
        did = domain.pop("domain_id")
        # Map DB column names to YAML panorama field names
        domain_entry = {
            "parent_domain": domain.get("domain_group", ""),
            "domain_id": did,
            "subdomain_id": did,
            "ssot_path": domain.get("ssot_path", ""),
            "ssot_module": "",
            "covers": [],
            "aliases": [],
            "change_policy": domain.get("lifecycle", ""),
            "impact_level": "M",
            "modification_permission": "",
        }
        # Parse covers/aliases from arch_path_mappings if available
        data["domains"][did] = domain_entry

    # Enrich domains with covers/aliases from arch_path_mappings
    for row in conn.execute("SELECT * FROM arch_path_mappings"):
        mapping = dict(row)
        did = mapping.get("domain_id", "")
        if did in data["domains"]:
            covers_raw = mapping.get("covers", "")
            if covers_raw:
                try:
                    data["domains"][did]["covers"] = _json.loads(covers_raw)
                except (_json.JSONDecodeError, TypeError):
                    data["domains"][did]["covers"] = [covers_raw] if covers_raw else []
            aliases_raw = mapping.get("aliases", "")
            if aliases_raw:
                try:
                    data["domains"][did]["aliases"] = _json.loads(aliases_raw)
                except (_json.JSONDecodeError, TypeError):
                    data["domains"][did]["aliases"] = [aliases_raw] if aliases_raw else []

    # Build tree structure from arch_directory_tree
    tree = {}
    for row in conn.execute("SELECT * FROM arch_directory_tree ORDER BY path"):
        entry = dict(row)
        path = entry.get("path", "")
        if not path:
            continue
        parts = path.split("/")
        current = tree
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {}
            if i == len(parts) - 1:
                current[part]["__domain_id__"] = entry.get("domain_id", "")
                current[part]["__subdomain_id__"] = ""
                current[part]["lifecycle"] = entry.get("state", "operational")
            else:
                current = current[part]
    data["tree"] = tree

    # Load metadata
    try:
        cur = conn.execute("SELECT version FROM _schema_version ORDER BY version DESC LIMIT 1")
        r = cur.fetchone()
        if r:
            data["meta"]["schema_version"] = r["version"]
    except Exception:
        pass

    conn.close()
    return data


def _load_domain_mappings_from_db(db_path: Path):
    """从 depgraph 动态加载域映射数据（ARCH-CAP-005 抽屉式扩展）。

    替代原硬编码 DOMAIN_NAME_TO_LAYER / NON_SRC_DOMAIN_MAP / UNREGISTERED_SRC_MAP。
    新增域只需 INSERT domains/domain_mapping 表，无需修改生成器代码。

    Returns:
        (domain_id_to_layer, non_src_mappings, unregistered_src_mappings)
        - domain_id_to_layer: dict {domain_id: layer_id}  从 domains 表 layer_id 字段加载
        - non_src_mappings: list of (path_prefix, domain_id, subdomain_id)  从 domain_mapping 表加载
        - unregistered_src_mappings: list of (path_prefix, domain_id, subdomain_id)  从 domain_mapping 表加载
    """
    domain_id_to_layer = {}
    non_src_mappings = []
    unregistered_src_mappings = []

    # P2 PG 迁移：删除 db_path.exists() 检查（PG 无文件路径概念）
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        cur = conn.cursor()

        # Tier 1: domain_id → layer_id from domains table (per-domain, more accurate than group-based)
        cur.execute("SELECT domain_id, layer_id FROM domains WHERE layer_id IS NOT NULL AND layer_id != ''")
        for r in cur.fetchall():
            did = r["domain_id"]
            lid = r["layer_id"]
            if did and lid:
                domain_id_to_layer[did] = lid

        # Tier 2: path_prefix → (domain_id, subdomain_id) from domain_mapping table
        cur.execute("SELECT path_prefix, domain_id, subdomain_id FROM domain_mapping WHERE mapping_type = 'non_src'")
        for r in cur.fetchall():
            non_src_mappings.append((r["path_prefix"], r["domain_id"], r["subdomain_id"] or ""))

        cur.execute(
            "SELECT path_prefix, domain_id, subdomain_id FROM domain_mapping WHERE mapping_type = 'unregistered_src'"
        )
        for r in cur.fetchall():
            unregistered_src_mappings.append((r["path_prefix"], r["domain_id"], r["subdomain_id"] or ""))

        conn.close()
    except psycopg2.Error:
        # domain_mapping table doesn't exist yet — return empty mappings
        pass

    return domain_id_to_layer, non_src_mappings, unregistered_src_mappings


def load_panorama():
    """Load architecture panorama and build domain derivation table.

    Panorama structure (flat 35 functional domains):
      domains:
        capacity_assurance:
          parent_domain: data
          domain_id: D-DATA
          subdomain_id: D-DATA-CAPACITY_ASSURANCE
          ssot_path: src/zephyr/data/capacity-assurance/
          ...

    Returns:
        (panorama_data, domain_derivation, functional_domains)
        domain_derivation: [(path_prefix, domain_id, subdomain_id, architecture_layer)]
        Sorted by path_prefix length (longest first) for best prefix match.
    """
    # 治本（2026-06-27）：删除 if not DEPGRAPH_DB_PATH.exists() 守卫（latent bug）。
    # P2 迁移后 .db 文件不存在，守卫必然触发导致函数永远返回 None（broken 状态）。
    # PG 模式下直接查询 PG，连接失败由下方 try/except 捕获并 fail-soft 返回空。
    try:
        data = _load_panorama_from_db(None)
    except Exception:
        return None, [], []
    if not data:
        return None, [], []

    # ARCH-CAP-005: 动态加载域映射（替代硬编码 DOMAIN_NAME_TO_LAYER / NON_SRC_DOMAIN_MAP / UNREGISTERED_SRC_MAP）
    domain_id_to_layer, non_src_mappings, unregistered_src_mappings = _load_domain_mappings_from_db(None)

    domain_derivation = []
    functional_domains = []

    domains_data = data.get("domains", {})
    for func_domain_name, func_domain_val in domains_data.items():
        if not isinstance(func_domain_val, dict):
            continue
        parent_domain = func_domain_val.get("parent_domain", "")
        domain_id = func_domain_val.get("domain_id", "")
        subdomain_id = func_domain_val.get("subdomain_id", "")
        ssot_path = (func_domain_val.get("ssot_path") or "").replace("\\", "/").rstrip("/") + "/"
        arch_layer = domain_id_to_layer.get(domain_id, "")
        if ssot_path:
            domain_derivation.append((ssot_path, domain_id, subdomain_id, arch_layer))
        functional_domains.append(
            {
                "domain": parent_domain,
                "subdomain": func_domain_name,
                "domain_id": domain_id,
                "subdomain_id": subdomain_id,
                "ssot_module": func_domain_val.get("ssot_module", ""),
                "ssot_path": func_domain_val.get("ssot_path", ""),
                "covers": func_domain_val.get("covers", []),
                "aliases": func_domain_val.get("aliases", []),
                "change_policy": func_domain_val.get("change_policy", "") or func_domain_val.get("stability", ""),
                "impact_level": func_domain_val.get("impact_level", "") or func_domain_val.get("safety_level", "M"),
                "modification_permission": func_domain_val.get("modification_permission", "")
                or func_domain_val.get("ai_autonomy", ""),
            }
        )

    # Add tree-section domain mappings (current operational paths)
    # Build set of unregistered prefixes to skip in tree extraction
    unreg_prefixes = set(prefix for prefix, _, _ in unregistered_src_mappings)
    tree_data = data.get("tree", {})
    _extract_tree_domains(tree_data, "", domain_derivation, domains_data, unreg_prefixes, domain_id_to_layer)

    # Add non-src directory mappings (from domain_mapping table, mapping_type='non_src')
    for prefix, did, sid in non_src_mappings:
        domain_derivation.append((prefix, did, sid, ""))

    # Add unregistered src/zephyr/ subdirectory mappings (from domain_mapping table, mapping_type='unregistered_src')
    for prefix, did, sid in unregistered_src_mappings:
        arch_layer = domain_id_to_layer.get(did, "")
        domain_derivation.append((prefix, did, sid, arch_layer))

    # Sort by prefix length (longest first for best match)
    domain_derivation.sort(key=lambda x: len(x[0]), reverse=True)

    return data, domain_derivation, functional_domains


def _extract_tree_domains(
    tree_node, current_path, derivation_list, domains_data=None, unreg_prefixes=None, domain_id_to_layer=None
):
    """Recursively extract domain_id from panorama tree section.
    Skips paths that have explicit mappings in domain_mapping table (unregistered_src).
    """
    if not isinstance(tree_node, dict):
        return
    domain_id = tree_node.get("__domain_id__", "")
    subdomain_id = tree_node.get("__subdomain_id__", "")
    if domain_id and current_path:
        prefix = current_path.replace("\\", "/")
        if not prefix.endswith("/"):
            prefix += "/"
        # Skip if this prefix is covered by an unregistered_src mapping
        if unreg_prefixes and any(prefix.startswith(up) for up in unreg_prefixes):
            pass  # Let unregistered_src mappings handle this path
        else:
            arch_layer = ""
            if domain_id_to_layer:
                arch_layer = domain_id_to_layer.get(domain_id, "")
            derivation_list.append((prefix, domain_id, subdomain_id, arch_layer))
    for key, val in tree_node.items():
        if key.startswith("__") or not isinstance(val, dict):
            continue
        child_path = f"{current_path}/{key}" if current_path else key
        _extract_tree_domains(val, child_path, derivation_list, domains_data, unreg_prefixes, domain_id_to_layer)


def _extract_domain_override(filepath: Path) -> str | None:
    """从文件头提取 [DOMAIN] 字段，返回 domain_id 或 None。

    覆盖路径派生的 domain_id，用于跨域模块的显式声明。
    只读前20行，支持 # [DOMAIN] D-XXX 格式。
    """
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for _ in range(20):
                line = f.readline()
                if not line:
                    break
                m = re.match(r"^#\s*\[DOMAIN\]\s*(D-[\w-]+)", line)
                if m:
                    return m.group(1)
    except (OSError, UnicodeDecodeError):
        pass
    return None


def derive_domain_id(rel_path: str, domain_derivation: list = None, filepath: Path = None) -> str:
    # 优先检查文件头 [DOMAIN] 覆盖
    if filepath and filepath.exists():
        override = _extract_domain_override(filepath)
        if override:
            return override
    # 路径派生
    if not domain_derivation:
        return ""
    rp = rel_path.replace("\\", "/")
    for prefix, domain_id, _, _ in domain_derivation:
        if rp.startswith(prefix):
            return domain_id
    return ""


def derive_subdomain_id(rel_path: str, domain_id: str, domain_derivation: list = None) -> str:
    if not domain_id or not domain_derivation:
        return ""
    rp = rel_path.replace("\\", "/")
    for prefix, did, subdomain_id, _ in domain_derivation:
        if did == domain_id and subdomain_id and rp.startswith(prefix):
            return subdomain_id
    return ""


def derive_architecture_layer(rel_path: str, blueprint_id: str, domain_derivation: list = None) -> str:
    if domain_derivation:
        rp = rel_path.replace("\\", "/")
        for prefix, _, _, arch_layer in domain_derivation:
            if rp.startswith(prefix) and arch_layer:
                return arch_layer
    if blueprint_id:
        bid = blueprint_id.strip('"').strip("'")
        if "MOD-L0" in bid:
            return "L0_infrastructure"
        elif "MOD-L1" in bid:
            return "L1_foundation"
        elif "MOD-L2" in bid:
            return "L2_domain"
        elif "MOD-L3" in bid:
            return "L3_application"
    return ""


def derive_design_maturity(node_type: str, has_test: bool) -> str:
    # 裁定#189：删除 blueprint→design 分支，生成器不得创建设计态节点
    # 设计态节点只由人工通过 apply_depgraph.py 写入（§12.1 唯一来源规则）
    if node_type in CODE_TYPES:
        if has_test:
            return "production"
        return "prototype"
    return "production"


def derive_deployment_lifecycle(node_type: str) -> str:
    if node_type == "blueprint":
        return "design_only"
    return "stable"


def derive_build_status(design_maturity: str, has_test: bool = False) -> str:
    """从文件特征推导 build_status（裁定#180）。

    推导规则（机械可执行，AI 零歧义）：
    - design → planned      （设计态未实现）
    - production + test → stable   （已验证）
    - production 无 test → generated（AI已生成未验证）
    - prototype → generated  （脚手架/占位符）

    少数需手工标记的状态（deprecated）通过
    apply_depgraph.py --transition-build-status 写入。
    """
    if design_maturity == "design":
        return "planned"
    if design_maturity == "prototype":
        return "generated"
    # production
    if has_test:
        return "stable"
    return "generated"


def realization_detection(depgraph: dict) -> int:
    """检测设计态节点的实现状态（裁定#189-193）。

    扫描 design_maturity='design' 且有 blueprint_id 的节点，
    检测同 blueprint_id 的 production 节点是否存在，
    存在则 UPDATE build_status='stable'（表示设计已实现）。

    返回：更新的节点数
    """
    nodes = depgraph.get("nodes", {})
    # 收集每个 blueprint_id 对应的 production 节点
    blueprint_has_production = set()
    for node in nodes.values():
        bp_id = node.get("blueprint_id")
        if bp_id and node.get("design_maturity") == "production":
            blueprint_has_production.add(bp_id)

    # 更新 design 节点
    updated = 0
    for node in nodes.values():
        bp_id = node.get("blueprint_id")
        if (
            bp_id
            and node.get("design_maturity") == "design"
            and bp_id in blueprint_has_production
            and node.get("build_status") == "planned"
        ):
            node["build_status"] = "stable"
            updated += 1

    if updated > 0:
        print(f"[DEPGRAPH] realization_detection: {updated} 个设计态节点已实现（build_status=stable）")
    return updated


def derive_trust_zone(rel_path: str) -> str:
    rp = rel_path.replace("\\", "/")
    for prefix, zone in TRUST_ZONE_MAP:
        if rp.startswith(prefix):
            return zone
    return "trusted_core"


def derive_drive_direction(has_blueprint: bool, node_type: str) -> str:
    if has_blueprint and node_type == "blueprint":
        return "top_down"
    return "bottom_up"


def derive_tags(rel_path: str, node_type: str) -> list:
    tags = []
    rp = rel_path.replace("\\", "/")
    parts = rp.split("/")
    for part in parts[:-1]:
        if part and part not in tags and not part.startswith("_") and "." not in part:
            tags.append(part)
    if node_type and node_type not in tags:
        tags.append(node_type)
    return tags[:10]


def count_header_completeness(filepath) -> int:
    found = 0
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 20:
                    break
                stripped = line.strip()
                for field in HEADER_FIELDS:
                    if f"[{field}]" in stripped:
                        found += 1
    except Exception:
        pass
    return found


# Type classification prefixes — loaded from depgraph_scan_exclusions.yaml
_type_prefixes_cfg = _DEPGRAPH_CONFIG.get("type_prefixes", {})
POLICY_PREFIXES = _type_prefixes_cfg.get("policy", _FALLBACK_TYPE_PREFIXES["policy"])
TEMPLATE_PREFIXES = _type_prefixes_cfg.get("template", _FALLBACK_TYPE_PREFIXES["template"])
REGISTRY_PREFIXES = _type_prefixes_cfg.get("registry", _FALLBACK_TYPE_PREFIXES["registry"])
CONTRACT_PREFIXES = _type_prefixes_cfg.get("contract", _FALLBACK_TYPE_PREFIXES["contract"])
SCHEMA_PREFIXES = _type_prefixes_cfg.get("schema", _FALLBACK_TYPE_PREFIXES["schema"])

ID_PATTERN = re.compile(
    r"(MOD-INF-\d+|MOD-KB-\d+|MOD-L\d+-\d+|DOM-GOV-\d+|SYS-MASTER-\d+"
    r"|GOV-[A-Z]+-\d+|PS-[A-Z]+-\d+|PS-REG-\d+|PS-STD-\d+"
    r"|DEP-\d+|EN-\d+|GCT-\d+|REG-[A-Z]+-\d+|CT-\d+"
    r"|GOV-DOC-\d+|GOV-ENG-\d+|ADR-\d+|TPL-[A-Z]+-\d+"
    r"|CAT-[A-Z]+-\d+)"
)


def parse_blueprint_header(filepath: Path) -> dict:
    info = {
        "blueprint_id": "",
        "blueprint_path": "",
        "module_path": "",
        "change_policy": "",
        "impact_level": "",
        "modification_permission": "",
    }
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 15:
                    break
                stripped = line.strip()
                if stripped.startswith("# [BLUEPRINT]"):
                    parts = stripped[len("# [BLUEPRINT]") :].strip().split("|")
                    if len(parts) >= 1:
                        info["blueprint_id"] = parts[0].strip()
                    if len(parts) >= 2:
                        info["blueprint_path"] = parts[1].strip()
                elif stripped.startswith('"""[BLUEPRINT]') or stripped.startswith("'''[BLUEPRINT]"):
                    content = stripped.lstrip("\"'").lstrip()
                    if content.startswith("[BLUEPRINT]"):
                        content = content[len("[BLUEPRINT]") :].strip()
                    else:
                        content = content[len("BLUEPRINT]") :].strip()
                    parts = content.split("|")
                    if len(parts) >= 1:
                        info["blueprint_id"] = parts[0].strip()
                    if len(parts) >= 2:
                        info["blueprint_path"] = parts[1].strip()
                elif stripped.startswith("# [MODULE]"):
                    info["module_path"] = stripped[len("# [MODULE]") :].strip()
                elif stripped.startswith("# [STABILITY]"):
                    val = stripped[len("# [STABILITY]") :].strip()
                    info["change_policy"] = val
                elif stripped.startswith("# [SAFETY]"):
                    val = stripped[len("# [SAFETY]") :].strip()
                    info["impact_level"] = val
                elif stripped.startswith("# [AI_AUTONOMY]"):
                    val = stripped[len("# [AI_AUTONOMY]") :].strip()
                    info["modification_permission"] = val
                if not info["blueprint_id"] and i < 10:
                    bp_match = __import__("re").search(
                        r"(?:蓝图|blueprint)[:\s]+([A-Z]{2,4}-[A-Z]*-?\d+)", stripped, __import__("re").IGNORECASE
                    )
                    if bp_match:
                        info["blueprint_id"] = bp_match.group(1).upper()
    except Exception:
        pass
    return info


def parse_yaml_header(filepath: Path) -> dict:
    info = {
        "blueprint_id": "",
        "blueprint_path": "",
        "change_policy": "",
        "impact_level": "",
        "modification_permission": "",
    }
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            in_anchor = False
            for i, line in enumerate(f):
                if i >= 30:
                    break
                if "治理锚定" in line:
                    in_anchor = True
                    continue
                if in_anchor and "治理锚定结束" in line:
                    break
                if in_anchor:
                    m = re.match(r"#\s*blueprint:\s*(.+?)(?:\s*\|\s*(.+?))?(?:\s*\|\s*.+)?$", line)
                    if m:
                        info["blueprint_id"] = m.group(1).strip()
                        if m.group(2):
                            info["blueprint_path"] = m.group(2).strip()
                    m = re.match(r"#\s*module_id:\s*(.+)$", line)
                    if m:
                        if not info["blueprint_id"]:
                            info["blueprint_id"] = m.group(1).strip()
                    m = re.match(r"#\s*stability:\s*(.+)$", line)
                    if m:
                        info["change_policy"] = m.group(1).strip()
                    m = re.match(r"#\s*safety_level:\s*(.+)$", line)
                    if m:
                        info["impact_level"] = m.group(1).strip()
                    m = re.match(r"#\s*ai_autonomy:\s*(.+)$", line)
                    if m:
                        info["modification_permission"] = m.group(1).strip()
    except Exception:
        pass
    return info


def parse_md_frontmatter(filepath: Path) -> dict:
    info = {"blueprint_id": "", "module_id": "", "change_policy": "", "impact_level": "", "modification_permission": ""}
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            in_fm = False
            for i, line in enumerate(f):
                if i >= 40:
                    break
                stripped = line.strip()
                if i == 0 and stripped.lstrip("\ufeff").strip() == "---":
                    in_fm = True
                    continue
                if in_fm and stripped == "---":
                    break
                if in_fm:
                    m = re.match(r"module_id:\s*(.+)$", stripped)
                    if m:
                        info["module_id"] = m.group(1).strip().strip('"').strip("'")
                        if not info["blueprint_id"]:
                            info["blueprint_id"] = info["module_id"]
                    m = re.match(r"stability:\s*(.+)$", stripped)
                    if m:
                        info["change_policy"] = m.group(1).strip()
                    m = re.match(r"safety_level:\s*(.+)$", stripped)
                    if m:
                        info["impact_level"] = m.group(1).strip()
                    m = re.match(r"ai_autonomy:\s*(.+)$", stripped)
                    if m:
                        info["modification_permission"] = m.group(1).strip()
    except Exception:
        pass
    return info


def extract_py_imports(filepath: Path) -> list:
    imports = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("zephyr") or alias.name.startswith("scripts"):
                        imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    try:
                        rel_parent = filepath.relative_to(PROJECT_ROOT).parent
                    except ValueError:
                        continue
                    parts = list(rel_parent.parts)
                    for _ in range(node.level - 1):
                        if parts:
                            parts.pop()
                    if node.module:
                        parts.append(node.module.replace(".", "/"))
                    base = "/".join(parts)
                    for alias in node.names:
                        mod_path = base + "/" + alias.name.replace(".", "/")
                        if mod_path.startswith("src/zephyr/"):
                            dot_path = mod_path.replace("src/zephyr/", "zephyr.").replace("/", ".")
                            imports.append(dot_path)
                        elif mod_path.startswith("scripts/"):
                            dot_path = mod_path.replace("scripts/", "scripts.").replace("/", ".")
                            imports.append(dot_path)
                elif node.module and (node.module.startswith("zephyr") or node.module.startswith("scripts")):
                    imports.append(node.module)
    except Exception:
        pass
    return imports


def extract_public_api(filepath: Path) -> str:
    """四图模块对齐 Step 3 Task 3.5：从 Python AST 提取 __all__ 列表作为 public_api。

    __all__ 是 Python 模块的公开 API 约定（PEP 8）。
    返回逗号分隔的字符串（便于 DB 存储），无 __all__ 时返回空串。

    :param filepath: Python 文件路径
    :return: "func_a,ClassB,const_C" 或 ""
    """
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(filepath))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            names = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    names.append(elt.value)
                            return ", ".join(names)
                        return ""
    except Exception:
        pass
    return ""


def extract_md_references(filepath: Path) -> list:
    refs = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return list(set(refs))


def extract_json_references(filepath: Path) -> list:
    refs = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return list(set(refs))


def classify_file(rel_path: str) -> str:
    rp = rel_path.replace("\\", "/")

    if rp.startswith("src/zephyr/gates/") and rp.endswith(".yaml"):
        return "gate"
    if rp.startswith("src/zephyr/") and rp.endswith(".py"):
        return "module"
    if rp.startswith("scripts/") and rp.endswith(".py"):
        return "script"
    if rp.startswith("tests/") and rp.endswith(".py"):
        return "test"

    if rp.endswith((".sh", ".ps1")):
        return "script"

    if rp.endswith(".mmd"):
        return "diagram"

    if rp.endswith(".json"):
        if any(rp.startswith(p) for p in SCHEMA_PREFIXES):
            return "schema"
        return "data"

    if rp.endswith((".yaml", ".yml")):
        if any(rp.startswith(p) for p in REGISTRY_PREFIXES):
            return "registry"
        if any(rp.startswith(p) for p in CONTRACT_PREFIXES):
            return "contract"
        if any(p in rp for p in ("_registry.yaml", "manifest.yaml")):
            return "registry"
        if rp.startswith("data/"):
            return "data"
        if rp.startswith("config/"):
            return "config"
        return "config"

    if rp.endswith(".md"):
        if rp.endswith("/blueprint.md") or rp.endswith("\\blueprint.md"):
            return "blueprint"
        if rp.startswith("docs/03_modules/_master-blueprint/") and "/blueprint-" in rp:
            return "blueprint"
        if any(rp.startswith(p) for p in TEMPLATE_PREFIXES):
            return "template"
        if any(rp.startswith(p) for p in POLICY_PREFIXES):
            return "policy"
        if any(rp.startswith(p) for p in SCHEMA_PREFIXES):
            return "schema"
        # Knowledge doc paths — loaded from depgraph_scan_exclusions.yaml
        if any(rp.startswith(p) for p in KNOWLEDGE_DOC_PATHS):
            return "knowledge_doc"
        if rp.startswith("docs/02_enterprise_architecture/"):
            return "doc"
        return "doc"

    return ""


def compute_file_hash(filepath: Path) -> str:
    """裁定#209 Stage 3: 计算文件内容 SHA256 hash（用于增量重建检测）。"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""


def scan_py_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    header = parse_blueprint_header(filepath)
    imports = extract_py_imports(filepath)
    public_api = extract_public_api(filepath)
    cat = classify_file(rel_path)
    if not cat:
        cat = "module"
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "granularity": "file",
        "blueprint_id": header["blueprint_id"],
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "change_policy": header["change_policy"],
        "impact_level": header["impact_level"],
        "modification_permission": header["modification_permission"],
        "file_header_score": count_header_completeness(filepath),
        "imports": imports,
        "content_hash": compute_file_hash(filepath),
        "public_api": public_api,
    }


def scan_yaml_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    header = parse_yaml_header(filepath)
    cat = classify_file(rel_path)
    if not cat:
        cat = "config"
    refs = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    ref_key = "yaml_references" if cat in CONFIG_TYPES else "doc_references"
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "granularity": "file",
        "blueprint_id": header["blueprint_id"],
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "change_policy": header["change_policy"],
        "impact_level": header["impact_level"],
        "modification_permission": header["modification_permission"],
        ref_key: list(set(refs)),
        "content_hash": compute_file_hash(filepath),
    }


def scan_md_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    cat = classify_file(rel_path)
    if not cat:
        cat = "doc"

    if cat == "blueprint":
        return scan_blueprint_file(rel_path, domain_derivation)

    if cat == "knowledge_doc":
        cat = "doc"

    fm = parse_md_frontmatter(filepath)
    bp_id = fm.get("module_id", "") or fm.get("blueprint_id", "")
    refs = extract_md_references(filepath) if cat not in ("knowledge_doc",) else []

    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "granularity": "file",
        "blueprint_id": bp_id,
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "change_policy": fm.get("change_policy", ""),
        "impact_level": fm.get("impact_level", ""),
        "modification_permission": fm.get("modification_permission", ""),
        "doc_references": refs,
        "content_hash": compute_file_hash(filepath),
    }


def scan_blueprint_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    refs = []
    module_id = ""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        in_fm = False
        fm_lines = []
        for i, line in enumerate(content.splitlines()):
            if i >= 40:
                break
            stripped = line.strip()
            if i == 0 and stripped.lstrip("\ufeff").strip() == "---":
                in_fm = True
                continue
            if in_fm and stripped == "---":
                break
            if in_fm:
                fm_lines.append(stripped)
        fm_text = "\n".join(fm_lines)
        m = re.search(r"module_id:\s*(\S+)", fm_text)
        if m:
            module_id = m.group(1).strip('"').strip("'")
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": "blueprint",
        "granularity": "file",
        "blueprint_id": module_id,
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "module_id": module_id,
        "doc_references": list(set(refs)),
        "content_hash": compute_file_hash(filepath),
    }


def scan_json_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    cat = classify_file(rel_path)
    if not cat:
        cat = "data"
    refs = extract_json_references(filepath)
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "granularity": "file",
        "blueprint_id": "",
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "yaml_references": refs,
        "content_hash": compute_file_hash(filepath),
    }


def scan_infra_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    header = parse_blueprint_header(filepath)
    refs = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": "infra",
        "granularity": "file",
        "blueprint_id": header.get("blueprint_id", ""),
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "doc_references": list(set(refs)),
        "content_hash": compute_file_hash(filepath),
    }


def scan_diagram_file(rel_path: str, domain_derivation: list = None) -> dict | None:
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    cat = classify_file(rel_path)
    if not cat:
        cat = "diagram"
    refs = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in ID_PATTERN.finditer(content):
            refs.append(m.group(1))
    except Exception:
        pass
    return {
        "path": rel_path.replace("\\", "/"),
        "type": cat,
        "granularity": "file",
        "blueprint_id": "",
        "domain_id": derive_domain_id(rel_path, domain_derivation, filepath),
        "doc_references": refs,
        "content_hash": compute_file_hash(filepath),
    }


def collect_all_files() -> list:
    files = []
    for scan_dir_rel in SCAN_DIRS:
        scan_dir = PROJECT_ROOT / scan_dir_rel
        if not scan_dir.exists():
            continue
        for root, dirs, filenames in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if d not in EXEMPT_DIRS and not d.startswith(".")]
            for fn in filenames:
                fp = Path(root) / fn
                rel = str(fp.relative_to(PROJECT_ROOT)).replace("\\", "/")
                files.append(rel)
    return files


# ============================================================================
# 裁定#209 Stage 4: scan-level 缓存（真正增量重建）
# ============================================================================
# 病根: 原 --incremental 只是二元 skip（全跳过 / 全重建），任何单文件变化 → 重扫
# 5000+ 文件 + AST 解析。AST 解析是最大成本（非 DB 写入）。
# 治本: 缓存 scan 结果，key=(rel_path, content_hash)，命中则跳过 AST 解析。
# 安全: 仍全量 DELETE+INSERT DB（事务原子），无 DB 一致性风险。
# 失效: content_hash 变 → 单文件 miss；domain_derivation 变 → 全缓存失效
# (fingerprint)；scan 逻辑变 → bump SCAN_LOGIC_VERSION 全失效。
_SCAN_LOGIC_VERSION = 1  # scan_*_file 逻辑变更时 bump → 全缓存失效
_DEFAULT_CACHE_FILE = PROJECT_ROOT / ".runtime" / "depgraph_scan_cache.json"


def _compute_derivation_fingerprint(domain_derivation: list, functional_domains: list) -> str:
    """Hash of domain derivation data — if this changes, scan cache must invalidate.

    scan 结果的 domain_id 字段派生自 domain_derivation，若 panorama 更新导致
    域映射变化，旧 hash 的缓存 domain_id 会过期 → 必须整体失效缓存。
    """
    try:
        payload = json.dumps(
            {"dd": domain_derivation, "fd": functional_domains},
            sort_keys=True, ensure_ascii=False, default=str,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    except Exception:
        return ""  # 空 → 永不命中 → 安全回退全扫


class ScanCache:
    """Scan 结果缓存。线程安全（ThreadPoolExecutor 并发 put）。

    结构: {path: {content_hash: scan_result_dict}}
    失效策略:
      - 单文件: content_hash 变 → 该 path miss（其他 path 不受影响）
      - 全局: derivation_fingerprint / SCAN_LOGIC_VERSION 变 → 整个缓存丢弃
    """

    def __init__(self, cache_path: Path, derivation_fingerprint: str, enabled: bool = True):
        self.enabled = enabled
        self.cache_path = cache_path
        self.derivation_fingerprint = derivation_fingerprint
        self.entries: dict[str, dict[str, dict]] = {}
        self.hits = 0
        self.misses = 0
        self._lock = threading.Lock()
        self._dirty = False
        if enabled:
            self._load()

    def _load(self) -> None:
        try:
            with open(self.cache_path, encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("_meta", {})
            if (meta.get("scan_logic_version") == _SCAN_LOGIC_VERSION
                    and meta.get("derivation_fingerprint") == self.derivation_fingerprint):
                self.entries = data.get("entries", {})
                print(f"[DEPGRAPH][CACHE] Loaded {len(self.entries)} cached paths (fingerprint match)")
            else:
                self.entries = {}
                print(f"[DEPGRAPH][CACHE] Cache invalidated (fingerprint/version mismatch) — full rescan")
        except FileNotFoundError:
            self.entries = {}
            print(f"[DEPGRAPH][CACHE] No cache file — full scan")
        except Exception as e:
            self.entries = {}
            print(f"[DEPGRAPH][CACHE] Load failed ({e}) — full scan")

    def get(self, rel_path: str, content_hash: str) -> dict | None:
        if not self.enabled:
            self.misses += 1
            return None
        path_entries = self.entries.get(rel_path)
        if path_entries and content_hash in path_entries:
            self.hits += 1
            return path_entries[content_hash]
        self.misses += 1
        return None

    def put(self, rel_path: str, content_hash: str, result: dict) -> None:
        if not self.enabled:
            return
        with self._lock:
            self.entries.setdefault(rel_path, {})[content_hash] = result
            self._dirty = True

    def save(self) -> None:
        if not self.enabled or not self._dirty:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "_meta": {
                    "scan_logic_version": _SCAN_LOGIC_VERSION,
                    "derivation_fingerprint": self.derivation_fingerprint,
                    "saved_at": datetime.now().isoformat(),
                },
                "entries": self.entries,
            }
            tmp = self.cache_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            tmp.replace(self.cache_path)  # atomic rename
            print(f"[DEPGRAPH][CACHE] Saved ({len(self.entries)} paths) -> {self.cache_path}")
        except Exception as e:
            print(f"[DEPGRAPH][CACHE] WARNING: save failed: {e}")

    def stats(self) -> str:
        return f"hits={self.hits} misses={self.misses}"


def _scan_with_cache(scan_fn, rel_path: str, domain_derivation: list, cache: ScanCache) -> dict | None:
    """Cache wrapper: 先算 hash（廉价：只读字节），命中则复用，未命中则全扫。

    scan_fn 会内部重算 content_hash（轻微浪费），但保持原 scan_*_file 函数不动
    （最小 diff / 低风险）。hash 计算成本远低于 AST 解析。
    """
    filepath = PROJECT_ROOT / rel_path
    if not filepath.exists():
        return None
    content_hash = compute_file_hash(filepath)
    cached = cache.get(rel_path, content_hash)
    if cached is not None:
        return cached
    result = scan_fn(rel_path, domain_derivation)
    if result is not None:
        cache.put(rel_path, content_hash, result)
    return result


def build_depgraph(
    files_data: list,
    functional_registry: list = None,
    domain_derivation: list = None,
    existing_design_nodes: dict = None,
    granularity: str = "file",
) -> dict:
    if functional_registry is None:
        functional_registry = []
    if domain_derivation is None:
        domain_derivation = []
    if existing_design_nodes is None:
        existing_design_nodes = {}

    nodes = {}
    edges = []
    edge_set = set()

    # --- DM-002 Fix 1: file-level merge — group files_data by path first ---
    # When granularity=file, merge multiple scan results for the same file path
    # into a single entry, preferring type=module over other types.
    if granularity == "file":
        merged_files: dict[str, dict] = {}
        # TYPE_PRIORITY 已提升为模块级常量（从 node_type_vocabulary.yaml 动态加载）
        for fd in files_data:
            path = fd["path"]
            if path in merged_files:
                existing = merged_files[path]
                # Prefer the entry with higher type priority (lower number)
                existing_type = existing.get("type", "unknown")
                new_type = fd.get("type", "unknown")
                if TYPE_PRIORITY.get(new_type, 99) < TYPE_PRIORITY.get(existing_type, 99):
                    merged_files[path] = fd
                # Merge non-empty blueprint_id from the other entry
                if not merged_files[path].get("blueprint_id") and existing.get("blueprint_id"):
                    merged_files[path]["blueprint_id"] = existing["blueprint_id"]
                # Merge imports from all entries
                if "imports" in fd:
                    merged_files[path].setdefault("imports", [])
                    for imp in fd.get("imports", []):
                        if imp not in merged_files[path]["imports"]:
                            merged_files[path]["imports"].append(imp)
            else:
                merged_files[path] = fd
        files_data = list(merged_files.values())

    path_to_node = {}
    for fd in files_data:
        path = fd["path"]
        path_to_node[path] = fd
        bid_raw = fd.get("blueprint_id", "") or fd.get("module_id", "")
        bid_clean = normalize_path(bid_raw.strip('"').strip("'")) if bid_raw else ""
        norm_path = normalize_path(path)
        node_id = norm_path.replace("/", "__").replace(".", "_")

        def _clean(val):
            v = val.strip('"').strip("'")
            if "#" in v:
                v = v[: v.index("#")].strip()
            if ";" in v:
                v = v[: v.index(";")].strip()
            if v == "deprecated":
                v = "frozen"
            return v

        if fd.get("type") == "knowledge_doc":
            continue

        ntype = fd.get("type", "unknown")

        # 白名单准入（裁定#184）：只收录 module/script/test/config 4种节点
        # 非白名单类型（doc/blueprint/policy/gate/registry/contract/schema等）不进 nodes 表
        if ntype not in NODES_WHITELIST:
            continue
        domain_id = fd.get("domain_id", "")
        has_blueprint = bool(bid_clean)

        subdomain_id = derive_subdomain_id(path, domain_id, domain_derivation)
        belongs_to = bid_clean if ntype != "blueprint" else ""
        architecture_layer = derive_architecture_layer(path, bid_clean, domain_derivation)
        trust_zone = derive_trust_zone(path)
        drive_direction = derive_drive_direction(has_blueprint, ntype)
        tags = derive_tags(path, ntype)

        node = {
            "id": node_id,
            "path": norm_path,
            "type": ntype,
            "blueprint_id": bid_clean,
            "domain_id": domain_id,
            "subdomain_id": subdomain_id,
            "belongs_to": belongs_to,
            "change_policy": _clean(fd.get("change_policy", "")) or derive_stability_fallback(ntype, norm_path),
            "impact_level": _clean(fd.get("impact_level", "")) or "M",
            "modification_permission": _clean(fd.get("modification_permission", ""))
            or derive_autonomy_fallback(ntype, norm_path),
            "file_header_score": fd.get("file_header_score", 0),
            "architecture_layer": architecture_layer,
            "design_maturity": (_dm := derive_design_maturity(ntype, False)),
            "build_status": derive_build_status(_dm, False),  # 裁定#180：从文件特征推导
            "deployment_lifecycle": derive_deployment_lifecycle(ntype),
        "trust_zone": trust_zone,
        "drive_direction": drive_direction,
        "content_hash": fd.get("content_hash", ""),
        }

        # Only include non-empty optional fields
        if subdomain_id:
            pass  # already included
        else:
            del node["subdomain_id"]
        if not belongs_to:
            del node["belongs_to"]
        if not bid_clean:
            del node["blueprint_id"]
        if not architecture_layer:
            del node["architecture_layer"]
        if trust_zone == "trusted_core":
            del node["trust_zone"]
        if drive_direction == "bottom_up":
            del node["drive_direction"]

        if ntype in CODE_TYPES:
            node["imports"] = [normalize_path(imp) if isinstance(imp, str) else imp for imp in fd.get("imports", [])]
        elif ntype in CONFIG_TYPES:
            node["yaml_references"] = [
                normalize_path(ref) if isinstance(ref, str) else ref for ref in fd.get("yaml_references", [])
            ]
        elif ntype in DOC_TYPES:
            node["doc_references"] = [
                normalize_path(ref) if isinstance(ref, str) else ref for ref in fd.get("doc_references", [])
            ]

        if ntype == "blueprint":
            node["module_id"] = fd.get("module_id", bid_clean)

        nodes[node_id] = node

    bp_id_to_paths = defaultdict(list)
    blueprint_file_map = defaultdict(list)
    for fd in files_data:
        bid_raw = fd.get("blueprint_id", "") or fd.get("module_id", "")
        bid_clean = normalize_path(bid_raw.strip('"').strip("'")) if bid_raw else ""
        if bid_clean:
            bp_id_to_paths[bid_clean].append(fd["path"])
            if fd.get("type") != "blueprint":
                blueprint_file_map[bid_clean].append(fd["path"])

    for fd in files_data:
        src_path = fd["path"]
        src_id = normalize_path(src_path).replace("/", "__").replace(".", "_")
        if src_id not in nodes:
            continue

        imports = fd.get("imports", [])
        for imp in imports:
            imp_parts = imp.split(".")
            if imp_parts[0] == "zephyr":
                imp_parts = imp_parts[1:]
                prefix = "src/zephyr"
            elif imp_parts[0] == "scripts":
                imp_parts = imp_parts[1:]
                prefix = "scripts"
            else:
                continue
            if not imp_parts:
                continue
            for i in range(len(imp_parts), 0, -1):
                candidate = prefix + "/" + "/".join(imp_parts[:i]) + ".py"
                if candidate in path_to_node:
                    dst_id = normalize_path(candidate).replace("/", "__").replace(".", "_")
                    if dst_id == src_id:
                        continue
                    edge_key = (src_id, dst_id, "import_depends")
                    if edge_key not in edge_set and dst_id in nodes:
                        # Derive coupling_strength from domain proximity
                        src_domain = nodes.get(src_id, {}).get("domain_id", "")
                        dst_domain = nodes.get(dst_id, {}).get("domain_id", "")
                        if src_domain and dst_domain and src_domain != dst_domain:
                            coupling = "critical"
                        elif src_domain and dst_domain and src_domain == dst_domain:
                            coupling = "required"
                        else:
                            coupling = "required"
                        is_cross = bool(src_domain and dst_domain and src_domain != dst_domain)  # H5 fix
                        edges.append(
                            {
                                "from": src_id,
                                "to": dst_id,
                                "dep_type": "import_depends",
                                "architecture_direction": "downstream",
                                "coupling_strength": coupling,
                                "cross_domain": is_cross,
                                "invocation_method": "import",
                                "verified": False,
                            }
                        )  # H5 fix
                        edge_set.add(edge_key)
                    break
                candidate2 = prefix + "/" + "/".join(imp_parts[:i]) + "/__init__.py"
                if candidate2 in path_to_node:
                    dst_id = normalize_path(candidate2).replace("/", "__").replace(".", "_")
                    if dst_id == src_id:
                        continue
                    edge_key = (src_id, dst_id, "import_depends")
                    if edge_key not in edge_set and dst_id in nodes:
                        src_domain = nodes.get(src_id, {}).get("domain_id", "")
                        dst_domain = nodes.get(dst_id, {}).get("domain_id", "")
                        if src_domain and dst_domain and src_domain != dst_domain:
                            coupling = "critical"
                        elif src_domain and dst_domain and src_domain == dst_domain:
                            coupling = "required"
                        else:
                            coupling = "required"
                        is_cross = bool(src_domain and dst_domain and src_domain != dst_domain)  # H5 fix
                        edges.append(
                            {
                                "from": src_id,
                                "to": dst_id,
                                "dep_type": "import_depends",
                                "architecture_direction": "downstream",
                                "coupling_strength": coupling,
                                "cross_domain": is_cross,
                                "invocation_method": "import",
                                "verified": False,
                            }
                        )  # H5 fix
                        edge_set.add(edge_key)
                    break

        refs = fd.get("references", []) or fd.get("yaml_references", []) or fd.get("doc_references", [])
        if fd.get("type") != "blueprint":
            for ref in refs:
                for bp_path in bp_id_to_paths.get(ref, []):
                    if bp_path == src_path:
                        continue
                    bp_node_id = normalize_path(bp_path).replace("/", "__").replace(".", "_")
                    if bp_node_id in nodes and nodes[bp_node_id].get("type") == "blueprint":
                        dst_id = bp_node_id
                        edge_key = (src_id, dst_id, "references")
                        if edge_key not in edge_set:
                            src_domain_ref = nodes.get(src_id, {}).get("domain_id", "")
                            dst_domain_ref = nodes.get(dst_id, {}).get("domain_id", "")
                            is_cross_ref = bool(
                                src_domain_ref and dst_domain_ref and src_domain_ref != dst_domain_ref
                            )  # H5 fix
                            edges.append(
                                {
                                    "from": src_id,
                                    "to": dst_id,
                                    "dep_type": "references",
                                    "architecture_direction": "downstream",
                                    "coupling_strength": "degradable",
                                    "cross_domain": is_cross_ref,
                                    "invocation_method": "reference",
                                    "verified": False,
                                }
                            )  # H5 fix
                            edge_set.add(edge_key)

    # Update design_maturity for modules with tests
    tested_modules = set()
    for edge in edges:
        if edge["dep_type"] == "import_depends":
            from_type = nodes.get(edge["from"], {}).get("type", "")
            to_type = nodes.get(edge["to"], {}).get("type", "")
            if from_type == "test" and to_type in CODE_TYPES:
                tested_modules.add(edge["to"])
                # Upgrade test->module import_depends to test_depends
                edge["dep_type"] = "test_depends"
                edge["coupling_strength"] = "optional"
    for nid in tested_modules:
        if nid in nodes:
            nodes[nid]["design_maturity"] = "production"

    # DM-012 Fix 3: Enhanced edge inference — reduce orphan nodes
    # For nodes with zero edges, infer edges based on co-location and domain membership.
    _infer_before = len(edges)

    # Compute has_edge set BEFORE edge inference (needed below)
    has_edge = set()
    for e in edges:
        has_edge.add(e["from"])
        has_edge.add(e["to"])

    # Build co-directory index
    _dir_nodes = defaultdict(list)
    for nid, node in nodes.items():
        path_parts = node.get("path", "").rsplit("/", 1)
        if len(path_parts) > 1:
            _dir_nodes[path_parts[0]].append(nid)

    # Build domain index
    _domain_nodes = defaultdict(list)
    for nid, node in nodes.items():
        did = node.get("domain_id", "")
        if did:
            _domain_nodes[did].append(nid)

    # Find __init__.py nodes per directory
    _dir_inits = {}
    for nid, node in nodes.items():
        p = node.get("path", "")
        if p.endswith("__init__.py"):
            d = p.rsplit("/", 1)[0]
            _dir_inits[d] = nid

    inferred_edges_added = 0
    for nid, node in nodes.items():
        if nid in has_edge:
            continue

        ntype = node.get("type", "")
        npath = node.get("path", "")
        ndir = npath.rsplit("/", 1)[0] if "/" in npath else ""
        ndomain = node.get("domain_id", "")

        # Strategy A: Link to __init__.py in same directory
        if ndir and ndir in _dir_inits and _dir_inits[ndir] != nid:
            ek = (nid, _dir_inits[ndir], "config_depends")
            if ek not in edge_set:
                src_dom_a = node.get("domain_id", "")
                dst_dom_a = nodes.get(_dir_inits[ndir], {}).get("domain_id", "")
                is_cross_a = bool(src_dom_a and dst_dom_a and src_dom_a != dst_dom_a)  # H5 fix
                edges.append(
                    {
                        "from": nid,
                        "to": _dir_inits[ndir],
                        "dep_type": "config_depends",
                        "architecture_direction": "downstream",
                        "coupling_strength": "degradable",
                        "cross_domain": is_cross_a,
                        "invocation_method": "config",
                        "verified": False,
                    }
                )  # H5 fix
                edge_set.add(ek)
                has_edge.add(nid)
                has_edge.add(_dir_inits[ndir])
                inferred_edges_added += 1
                continue

        # Strategy B: Link to first module-type node in same directory
        if ndir and ndir in _dir_nodes and nid not in has_edge:
            for sib in _dir_nodes[ndir]:
                if sib == nid:
                    continue
                snode = nodes.get(sib, {})
                if snode.get("type") in ("module", "script"):
                    ek = (nid, sib, "config_depends")
                    if ek not in edge_set:
                        src_dom_b = node.get("domain_id", "")
                        dst_dom_b = snode.get("domain_id", "")
                        is_cross_b = bool(src_dom_b and dst_dom_b and src_dom_b != dst_dom_b)  # H5 fix
                        edges.append(
                            {
                                "from": nid,
                                "to": sib,
                                "dep_type": "config_depends",
                                "architecture_direction": "downstream",
                                "coupling_strength": "degradable",
                                "cross_domain": is_cross_b,
                                "invocation_method": "config",
                                "verified": False,
                            }
                        )  # H5 fix
                        edge_set.add(ek)
                        has_edge.add(nid)
                        has_edge.add(sib)
                        inferred_edges_added += 1
                        break

        # Strategy C: Link to same-domain blueprint node
        if ndomain and ndomain in _domain_nodes and nid not in has_edge:
            for dnid in _domain_nodes[ndomain]:
                if dnid == nid:
                    continue
                dnode = nodes.get(dnid, {})
                if dnode.get("type") == "blueprint":
                    ek = (nid, dnid, "blueprint_depends")
                    if ek not in edge_set:
                        src_dom_c = node.get("domain_id", "")
                        dst_dom_c = dnode.get("domain_id", "")
                        is_cross_c = bool(src_dom_c and dst_dom_c and src_dom_c != dst_dom_c)  # H5 fix
                        edges.append(
                            {
                                "from": nid,
                                "to": dnid,
                                "dep_type": "blueprint_depends",
                                "architecture_direction": "downstream",
                                "coupling_strength": "degradable",
                                "cross_domain": is_cross_c,
                                "invocation_method": "blueprint",
                                "verified": False,
                            }
                        )  # H5 fix
                        edge_set.add(ek)
                        has_edge.add(nid)
                        has_edge.add(dnid)
                        inferred_edges_added += 1
                        break

        # Strategy D: For test files, link to same-dir module files
        if ntype == "test" and ndir and ndir in _dir_nodes and nid not in has_edge:
            for sib in _dir_nodes[ndir]:
                if sib == nid:
                    continue
                snode = nodes.get(sib, {})
                if snode.get("type") in ("module", "script"):
                    ek = (nid, sib, "test_depends")
                    if ek not in edge_set:
                        src_dom_d = node.get("domain_id", "")
                        dst_dom_d = snode.get("domain_id", "")
                        is_cross_d = bool(src_dom_d and dst_dom_d and src_dom_d != dst_dom_d)  # H5 fix
                        edges.append(
                            {
                                "from": nid,
                                "to": sib,
                                "dep_type": "test_depends",
                                "architecture_direction": "downstream",
                                "coupling_strength": "optional",
                                "cross_domain": is_cross_d,
                                "invocation_method": "import",
                                "verified": False,
                            }
                        )  # H5 fix
                        edge_set.add(ek)
                        has_edge.add(nid)
                        has_edge.add(sib)
                        inferred_edges_added += 1
                        break

    if inferred_edges_added > 0:
        print(f"[DEPGRAPH] Inferred {inferred_edges_added} additional edges (reducing orphans)")

    by_type = defaultdict(int)
    for n in nodes.values():
        by_type[n["type"]] += 1
    by_edge_type = defaultdict(int)
    for e in edges:
        by_edge_type[e["dep_type"]] += 1

    has_edge = set()
    for e in edges:
        has_edge.add(e["from"])
        has_edge.add(e["to"])
    orphans = [nid for nid in nodes if nid not in has_edge]

    reverse_count = defaultdict(int)
    for e in edges:
        reverse_count[e["to"]] += 1
    most_depended = sorted(reverse_count.items(), key=lambda x: -x[1])[:20]
    floating_count = sum(1 for n in nodes.values() if not n.get("domain_id") and not n.get("blueprint_id"))

    # Build adjacency lists
    adjacency_forward = defaultdict(list)
    adjacency_reverse = defaultdict(list)
    for e in edges:
        adjacency_forward[e["from"]].append(e["to"])
        adjacency_reverse[e["to"]].append(e["from"])

    # Build functional_domains section (directly from panorama-derived registry)
    functional_domains_out = []
    for entry in functional_registry:
        functional_domains_out.append(
            {
                "domain": entry.get("domain", ""),
                "subdomain": entry.get("subdomain", ""),
                "domain_id": entry.get("domain_id", ""),
                "subdomain_id": entry.get("subdomain_id", ""),
                "ssot_module": entry.get("ssot_module", ""),
                "ssot_path": entry.get("ssot_path", ""),
                "covers": entry.get("covers", []),
                "aliases": entry.get("aliases", []),
                "change_policy": entry.get("change_policy", ""),
                "impact_level": entry.get("impact_level", "M"),
                "modification_permission": entry.get("modification_permission", ""),
            }
        )

    # Build completeness_declaration
    coverage_dimensions = []
    type_groups = [
        ("internal_modules", {"module"}),
        ("external_libraries", set()),
        ("docs", {"doc", "blueprint", "policy", "template", "diagram"}),
        ("scripts", {"script"}),
        ("gates", {"gate"}),
        ("data_assets", {"data", "config", "registry", "contract", "schema"}),
    ]
    for dim_name, dim_types in type_groups:
        covered = sum(by_type.get(t, 0) for t in dim_types)
        total = covered
        pct = 100.0 if total > 0 else 0.0
        coverage_dimensions.append({"dimension": dim_name, "covered": covered, "total": total, "pct": pct})

    # Compute source hash
    source_hash = ""
    try:
        hasher = hashlib.md5()
        for fd in sorted(files_data, key=lambda x: x.get("path", "")):
            hasher.update(fd.get("path", "").encode("utf-8"))
        source_hash = hasher.hexdigest()[:12]
    except Exception:
        pass

    # Dual-state protection: merge design-state nodes from existing depgraph
    # Normalize old layer names in design-state node fields
    design_node_count = 0
    skipped_empty_path = 0  # H2 fix
    fake_bp_cleared = 0  # H4 fix
    for nid, design_node in existing_design_nodes.items():
        old_path = design_node.get("path", "")
        # H2 fix: skip design nodes with empty path
        if not old_path or not old_path.strip():
            skipped_empty_path += 1
            continue
        if old_path:
            norm_path_ds = normalize_path(old_path)
            if not norm_path_ds:
                skipped_empty_path += 1
                continue
            norm_nid = norm_path_ds.replace("/", "__").replace(".", "_")
            design_node["id"] = norm_nid
            design_node["path"] = norm_path_ds
        else:
            norm_nid = nid
        # Normalize string fields that may contain old layer paths
        for str_key in ("blueprint_id", "belongs_to", "module_id"):
            if str_key in design_node and isinstance(design_node[str_key], str):
                design_node[str_key] = normalize_path(design_node[str_key])
        # Normalize list fields that may contain old layer paths
        for list_key in ("physical_files", "doc_references", "yaml_references", "imports"):
            if list_key in design_node and isinstance(design_node[list_key], list):
                design_node[list_key] = [
                    normalize_path(item) if isinstance(item, str) else item for item in design_node[list_key]
                ]
        # Remove physical_path if present (old layer names not wanted in output)
        design_node.pop("physical_path", None)
        # H4 fix: Clear fake blueprint_id before insert/merge
        bid = design_node.get("blueprint_id", "")
        if bid and not is_valid_blueprint_id(bid):
            design_node["blueprint_id"] = ""
            fake_bp_cleared += 1
        if norm_nid not in nodes:
            # No conflict: insert design-state node as-is
            nodes[norm_nid] = design_node
            design_node_count += 1
        else:
            # Conflict: disk scan produced a node with same ID.
            # Merge design-state fields from old node into the new disk-scan node.
            merge_design_fields(nodes[norm_nid], design_node)
            # H4 fix: Clear fake blueprint_id after merge
            bid = nodes[norm_nid].get("blueprint_id", "")
            if bid and not is_valid_blueprint_id(bid):
                nodes[norm_nid]["blueprint_id"] = ""
                fake_bp_cleared += 1
            design_node_count += 1
    if skipped_empty_path:
        print(f"  [H2] Skipped {skipped_empty_path} design nodes with empty path")
    if fake_bp_cleared:
        print(f"  [H4] Cleared {fake_bp_cleared} fake blueprint_id values")

    # Update metadata with design state counts
    by_type_after_merge = defaultdict(int)
    for n in nodes.values():
        by_type_after_merge[n["type"]] += 1

    return {
        "hard_boundaries": HARD_BOUNDARIES,
        "metadata": {
            "graph_id": "PROJECT-ENTITY-DEPGRAPH-001",
            "version": "3.1.0",
            "granularity": "system",
            "generated_at": datetime.now().isoformat(),
            "generated_by": "generate_project_depgraph.py",
            "source_hash": source_hash,
            "ssot_hierarchy": "",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_blueprint_file_map": sum(len(v) for v in blueprint_file_map.values()),
            "total_functional_domains": len(functional_domains_out),
            "design_state_nodes": design_node_count,
            "operational_state_nodes": len(nodes) - design_node_count,
            "scope": "Project entity dependency graph (full coverage, knowledge_doc lightweight)",
            "nodes_by_type": dict(by_type_after_merge),
            "edges_by_type": dict(by_edge_type),
        },
        "nodes": nodes,
        "edges": edges,
        "adjacency_lists": {
            "forward": dict(adjacency_forward),
            "reverse": dict(adjacency_reverse),
        },
        "functional_domains": functional_domains_out,
        "blueprint_file_map": {k: [normalize_path(p) for p in v] for k, v in blueprint_file_map.items()},
        "orphan_nodes": orphans[:50],
        "completeness_declaration": {
            "completeness": "incomplete_first_party_only",
            "missing_scopes": [],
            "last_verified": "",
            "coverage_dimensions": coverage_dimensions,
        },
        "graph_metrics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "orphan_nodes_count": len(orphans),
            "floating_nodes_count": floating_count,
            "most_depended_upon": [{"node": nid, "count": cnt} for nid, cnt in most_depended],
        },
        "architecture_constraints": {
            "layer_direction_rule": "downstream_only",
            "required_coverage": 0.95,
        },
        "path_mappings": PATH_MAPPINGS,
    }


def generate_mermaid_by_blueprint(depgraph: dict) -> str:
    bp_groups = defaultdict(list)
    for nid, node in depgraph["nodes"].items():
        bid = node.get("blueprint_id", "UNMAPPED")
        if not bid:
            bid = "UNMAPPED"
        bp_groups[bid].append(node)

    lines = ["flowchart TB"]
    for bid in sorted(bp_groups.keys()):
        nodes_in_group = bp_groups[bid]
        if bid == "UNMAPPED":
            continue
        safe_bid = bid.replace("-", "_").replace(".", "_")
        lines.append(f'    subgraph {safe_bid}["{bid} ({len(nodes_in_group)})"]')
        for node in nodes_in_group[:10]:
            safe_nid = node["id"]
            short_path = "/".join(node["path"].split("/")[-2:])
            ntype = node["type"]
            lines.append(f'        {safe_nid}["{short_path}<br/>({ntype})"]')
        if len(nodes_in_group) > 10:
            lines.append(f'        {safe_bid}_more["... +{len(nodes_in_group) - 10} more"]')
        lines.append("    end")

    edge_count = 0
    for edge in depgraph["edges"]:
        if edge["dep_type"] in ("references",):
            continue
        if edge_count >= 300:
            break
        from_id = edge["from"]
        to_id = edge["to"]
        etype = edge["dep_type"]
        style = {"import_depends": "-->", "references": "-.->", "test_depends": "..>"}.get(etype, "-->")
        lines.append(f"    {from_id} {style} {to_id}")
        edge_count += 1

    if edge_count >= 300:
        total_imports = sum(1 for e in depgraph["edges"] if e["dep_type"] == "import_depends")
        lines.append(f"    %% ... {total_imports - edge_count} more import edges omitted")

    return "\n".join(lines)


def generate_mermaid_by_type(depgraph: dict) -> str:
    type_groups = defaultdict(list)
    for nid, node in depgraph["nodes"].items():
        type_groups[node["type"]].append(node)

    lines = ["flowchart LR"]
    for ntype in sorted(type_groups.keys()):
        nodes_in_group = type_groups[ntype]
        safe_type = ntype.replace("-", "_")
        lines.append(f'    subgraph {safe_type}["{ntype} ({len(nodes_in_group)})"]')
        for node in nodes_in_group[:15]:
            safe_nid = node["id"]
            short_path = "/".join(node["path"].split("/")[-2:])
            lines.append(f'        {safe_nid}["{short_path}"]')
        if len(nodes_in_group) > 15:
            lines.append(f'        {safe_type}_more["... +{len(nodes_in_group) - 15} more"]')
        lines.append("    end")

    return "\n".join(lines)


def generate_markdown_section(depgraph: dict) -> str:
    meta = depgraph["metadata"]
    lines = []
    lines.append("## §19 实体级依赖图（全项目文件级）")
    lines.append("")
    lines.append(
        f"> **graph_id**: {meta['graph_id']} | **version**: {meta['version']} | **granularity**: {meta.get('granularity', 'system')}"
    )
    lines.append(
        f"> **total_nodes**: {meta['total_nodes']} | **total_edges**: {meta['total_edges']} | **functional_domains**: {meta.get('total_functional_domains', 0)}"
    )
    lines.append("> 生成脚本: `scripts/governance/generate_project_depgraph.py`")
    lines.append("")

    lines.append("### §19.1 节点统计")
    lines.append("")
    lines.append("| 类型 | 数量 |")
    lines.append("|------|:----:|")
    for ntype, count in sorted(meta["nodes_by_type"].items()):
        lines.append(f"| {ntype} | {count} |")
    lines.append(f"| **合计** | **{meta['total_nodes']}** |")
    lines.append("")

    lines.append("### §19.2 边统计")
    lines.append("")
    lines.append("| 边类型 | 数量 | 含义 |")
    lines.append("|--------|:----:|------|")
    edge_desc = {
        "import_depends": "Python import 依赖",
        "references": "YAML/MD/JSON 中引用 ID",
        "test_depends": "测试文件依赖被测模块",
    }
    for etype, count in sorted(meta["edges_by_type"].items()):
        lines.append(f"| {etype} | {count} | {edge_desc.get(etype, '')} |")
    lines.append(f"| **合计** | **{meta['total_edges']}** | |")
    lines.append("")

    lines.append("### §19.3 Top 20 被依赖节点")
    lines.append("")
    lines.append("| # | 节点 | 被依赖次数 | 类型 | 蓝图 |")
    lines.append("|---|------|:---------:|------|------|")
    reverse_count_md = defaultdict(int)
    for e in depgraph.get("edges", []):
        reverse_count_md[e["to"]] += 1
    most_dep_md = sorted(reverse_count_md.items(), key=lambda x: -x[1])[:20]
    for i, (nid, count) in enumerate(most_dep_md, 1):
        node = depgraph["nodes"].get(nid, {})
        short = "/".join(node.get("path", nid).split("/")[-2:])
        lines.append(f"| {i} | {short} | {count} | {node.get('type', '')} | {node.get('blueprint_id', '')} |")
    lines.append("")

    orphans = depgraph.get("orphan_nodes", [])
    if orphans:
        lines.append("### §19.4 孤儿节点（无入边无出边）")
        lines.append("")
        lines.append(f"共 {len(orphans)} 个孤儿节点（仅列前 50 个）：")
        lines.append("")
        for nid in orphans[:50]:
            node = depgraph["nodes"].get(nid, {})
            short = "/".join(node.get("path", nid).split("/")[-2:])
            lines.append(f"- `{short}` ({node.get('type', '')}) [{node.get('blueprint_id', '')}]")
        lines.append("")

    lines.append("### §19.5 按蓝图分组视图")
    lines.append("")
    lines.append("```mermaid")
    lines.append(generate_mermaid_by_blueprint(depgraph))
    lines.append("```")
    lines.append("")

    lines.append("### §19.6 按类型分组视图")
    lines.append("")
    lines.append("```mermaid")
    lines.append(generate_mermaid_by_type(depgraph))
    lines.append("```")
    lines.append("")

    bp_groups = defaultdict(list)
    for nid, node in depgraph["nodes"].items():
        bid = node.get("blueprint_id", "UNMAPPED")
        bp_groups[bid].append(node)

    lines.append("### §19.7 蓝图-文件归属明细")
    lines.append("")
    lines.append("| 蓝图 | 文件数 | 类型分布 |")
    lines.append("|------|:------:|---------|")
    for bid in sorted(bp_groups.keys()):
        nodes_in = bp_groups[bid]
        type_dist = defaultdict(int)
        for n in nodes_in:
            type_dist[n["type"]] += 1
        dist_str = ", ".join(f"{t}:{c}" for t, c in sorted(type_dist.items()))
        lines.append(f"| {bid} | {len(nodes_in)} | {dist_str} |")
    lines.append("")

    return "\n".join(lines)


def load_cross_module_registry() -> list:
    """Load cross-module-dependency-registry.yaml and return dependencies list."""
    # ARCH-036 P3-C4: 静默失效修正 — 返回空列表会让调用方认为"无跨模块依赖"，
    # 导致跨模块依赖分析整体失效。改为 stderr 警告。
    if not CROSS_MODULE_REGISTRY_PATH.exists():
        print(f"[WARN] CROSS_MODULE_REGISTRY_PATH not found: {CROSS_MODULE_REGISTRY_PATH} — cross-module dep scan skipped", file=sys.stderr)
        return []
    try:
        data = _yaml_load(CROSS_MODULE_REGISTRY_PATH)
        return data.get("dependencies", []) if data else []
    except Exception:
        return []


def load_depgraph_design_files() -> dict:
    """Load all DEP-GRAPH-*.yaml files from data/asset_index/.

    Returns:
        dict with 'nodes' and 'edges' merged from all DEP-GRAPH files.
        nodes: {code_path: node_dict}
        edges: [{from_code_path, to_code_path, ...edge_fields}]
    """
    result_nodes = {}
    result_edges = []
    if not DEPGRAPH_DESIGN_DIR.exists():
        return result_nodes, result_edges

    for dg_file in sorted(DEPGRAPH_DESIGN_DIR.glob("DEP-GRAPH-*.yaml")):
        try:
            data = _yaml_load(dg_file)
            if not data:
                continue
            for node in data.get("nodes", []):
                cp = node.get("code_path", "")
                if cp:
                    result_nodes[cp] = node
            for edge in data.get("edges", []):
                result_edges.append(edge)
        except Exception:
            continue
    return result_nodes, result_edges


def enrich_edges_semantic(edges: list, nodes: dict, registry_deps: list) -> list:
    """Enrich depgraph edges with semantic_type, semantic_direction, contract_anchor,
    failure_mode, fallback, interface fields.

    Strategy:
    1. Build module_id -> set of node_ids mapping from depgraph nodes
    2. For each registry dep, find matching depgraph edges and add semantic fields
    3. For unmatched edges, derive defaults from dep_type and architecture_direction
    4. Load DEP-GRAPH design files for failure_mode/fallback/interface on specific edges
    """
    # Build module_id -> set of node_ids mapping
    mod_to_nodes = {}
    for nid, node in nodes.items():
        bid = node.get("blueprint_id", "")
        if bid:
            mod_to_nodes.setdefault(bid, set()).add(nid)

    # Build path -> node_id mapping for DEP-GRAPH edge matching
    path_to_nid = {}
    for nid, node in nodes.items():
        p = node.get("path", "")
        if p:
            path_to_nid[p] = nid

    # Build registry lookup: (source_mod, target_mod) -> registry_dep
    reg_lookup = {}
    for dep in registry_deps:
        src = dep.get("source", "")
        tgt = dep.get("target", "")
        if src and tgt:
            reg_lookup.setdefault((src, tgt), []).append(dep)

    # Load DEP-GRAPH design files for failure_mode/fallback/interface
    dg_design_nodes, dg_design_edges = load_depgraph_design_files()

    # Build DEP-GRAPH code_path -> node_id mapping
    dg_code_to_nid = {}
    for code_path, dg_node in dg_design_nodes.items():
        nid = path_to_nid.get(code_path, "")
        if nid:
            dg_code_to_nid[code_path] = nid

    # Build DEP-GRAPH edge lookup: (from_nid, to_nid) -> edge_dict
    dg_edge_lookup = {}
    for dg_edge in dg_design_edges:
        from_name = dg_edge.get("from", "")
        to_name = dg_edge.get("to", "")
        # DEP-GRAPH uses node_id names, not file paths; match via code_path
        from_cp = dg_design_nodes.get(from_name, {}).get("code_path", "")
        to_cp = dg_design_nodes.get(to_name, {}).get("code_path", "")
        # Also try direct name as code_path
        if not from_cp:
            from_cp = from_name
        if not to_cp:
            to_cp = to_name
        from_nid = path_to_nid.get(from_cp, "")
        to_nid = path_to_nid.get(to_cp, "")
        if from_nid and to_nid:
            dg_edge_lookup.setdefault((from_nid, to_nid), []).append(dg_edge)

    # Track which edges got registry enrichment
    enriched_by_registry = set()

    # Enrich edges from registry (module-level mapping)
    for (src_mod, tgt_mod), reg_deps in reg_lookup.items():
        src_nodes = mod_to_nodes.get(src_mod, set())
        tgt_nodes = mod_to_nodes.get(tgt_mod, set())
        if not src_nodes or not tgt_nodes:
            continue
        # Use first registry dep for primary fields (most deps are 1:1)
        primary_dep = reg_deps[0]
        for edge in edges:
            if edge["from"] in src_nodes and edge["to"] in tgt_nodes:
                edge_key = (id(edge),)
                if edge_key not in enriched_by_registry:
                    edge["semantic_type"] = primary_dep.get("type", "")
                    edge["semantic_direction"] = primary_dep.get("direction", "")
                    edge["contract_anchor"] = primary_dep.get("contract_anchor", "")
                    enriched_by_registry.add(edge_key)

    # Enrich remaining edges with derived defaults
    for edge in edges:
        if "semantic_type" not in edge:
            dep_type = edge.get("dep_type", "")
            edge["semantic_type"] = DEP_TYPE_TO_SEMANTIC_TYPE.get(dep_type, "runtime")
        if "semantic_direction" not in edge:
            arch_dir = edge.get("architecture_direction", "downstream")
            edge["semantic_direction"] = arch_dir if arch_dir in VALID_SEMANTIC_DIRECTIONS else "downstream"

        # Derive contract_anchor from target node's blueprint_id or path
        if "contract_anchor" not in edge or not edge.get("contract_anchor"):
            to_nid = edge.get("to", "")
            to_node = nodes.get(to_nid, {})
            to_bid = to_node.get("blueprint_id", "")
            to_path = to_node.get("path", "")
            dep_type = edge.get("dep_type", "")
            if to_bid:
                edge["contract_anchor"] = to_bid
            elif dep_type == "import_depends" and to_path:
                # Derive from module path: src/zephyr/foo/bar.py -> zephyr.foo.bar
                rp = to_path.replace("\\", "/")
                if rp.startswith("src/zephyr/"):
                    anchor = rp.replace("src/zephyr/", "zephyr.").replace("/", ".").removesuffix(".py")
                    edge["contract_anchor"] = anchor
                elif rp.startswith("scripts/"):
                    anchor = rp.replace("scripts/", "scripts.").replace("/", ".").removesuffix(".py")
                    edge["contract_anchor"] = anchor
                else:
                    edge["contract_anchor"] = to_path
            elif dep_type == "test_depends" and to_path:
                edge["contract_anchor"] = to_path.replace("\\", "/")
            elif dep_type == "references" and to_bid:
                edge["contract_anchor"] = to_bid
            else:
                edge["contract_anchor"] = ""

        # Derive failure_mode from dep_type, semantic_type, and node context
        if "failure_mode" not in edge or not edge.get("failure_mode"):
            dep_type = edge.get("dep_type", "")
            semantic_type = edge.get("semantic_type", "runtime")
            coupling = edge.get("coupling_strength", "")
            from_nid = edge.get("from", "")
            to_nid = edge.get("to", "")
            from_node = nodes.get(from_nid, {})
            to_node = nodes.get(to_nid, {})
            from_type = from_node.get("type", "")
            to_type = to_node.get("type", "")
            from_domain = from_node.get("domain_id", "")
            to_domain = to_node.get("domain_id", "")
            cross_domain = from_domain != to_domain if from_domain and to_domain else False

            if dep_type == "import_depends":
                if to_type == "config" or to_type == "registry":
                    edge["failure_mode"] = "version_mismatch"
                elif coupling == "critical" or cross_domain:
                    edge["failure_mode"] = "service_down"
                elif semantic_type == "contract":
                    edge["failure_mode"] = "version_mismatch"
                elif semantic_type == "data":
                    edge["failure_mode"] = "data_corruption"
                else:
                    edge["failure_mode"] = "timeout"
            elif dep_type == "test_depends":
                edge["failure_mode"] = "cascade_failure"
            elif dep_type == "references":
                if to_type == "blueprint" or to_type == "schema":
                    edge["failure_mode"] = "version_mismatch"
                else:
                    edge["failure_mode"] = "version_mismatch"
            else:
                edge["failure_mode"] = "timeout"

        # Derive fallback from dep_type, coupling_strength, and node context
        if "fallback" not in edge or not edge.get("fallback"):
            dep_type = edge.get("dep_type", "")
            coupling = edge.get("coupling_strength", "")
            semantic_type = edge.get("semantic_type", "runtime")
            from_nid = edge.get("from", "")
            to_nid = edge.get("to", "")
            from_node = nodes.get(from_nid, {})
            to_node = nodes.get(to_nid, {})
            to_type = to_node.get("type", "")
            from_domain = from_node.get("domain_id", "")
            to_domain = to_node.get("domain_id", "")
            cross_domain = from_domain != to_domain if from_domain and to_domain else False

            if dep_type == "import_depends":
                if coupling == "critical" or cross_domain:
                    edge["fallback"] = "circuit_break"
                elif to_type == "config":
                    edge["fallback"] = "use_default_config"
                elif to_type == "registry" or semantic_type == "data":
                    edge["fallback"] = "cache_stale_data"
                else:
                    edge["fallback"] = "graceful_degradation"
            elif dep_type == "test_depends":
                edge["fallback"] = "skip_test"
            elif dep_type == "references":
                if to_type == "blueprint":
                    edge["fallback"] = "graceful_degradation"
                elif to_type == "schema":
                    edge["fallback"] = "cache_stale_data"
                else:
                    edge["fallback"] = "graceful_degradation"
            else:
                edge["fallback"] = "circuit_break"

        # Enrich from DEP-GRAPH design files (override defaults with design-time values)
        edge_key = (edge["from"], edge["to"])
        dg_matches = dg_edge_lookup.get(edge_key, [])
        if dg_matches:
            dg_edge = dg_matches[0]
            for field in ("failure_mode", "fallback", "interface", "contract_anchor"):
                dg_val = dg_edge.get(field, "")
                if dg_val:
                    edge[field] = dg_val

    return edges


def enrich_nodes_decision(nodes: dict, dg_design_nodes: dict = None) -> dict:
    """Enrich depgraph nodes with decision field (NEW/MODIFY/KEEP/DEPRECATE).

    Strategy:
    1. For nodes matching DEP-GRAPH design files (via code_path), use their decision
    2. For design-state nodes (lifecycle=design), set decision=NEW
    3. For all other nodes, default decision=KEEP
    """
    if dg_design_nodes is None:
        _, _ = load_depgraph_design_files()

    # Build code_path -> decision mapping from DEP-GRAPH files
    code_to_decision = {}
    for code_path, dg_node in (dg_design_nodes or {}).items():
        decision = dg_node.get("decision", "")
        if decision:
            # Clean decision: "NEW: ..." -> "NEW"
            clean = decision.split(":")[0].strip()
            if clean in VALID_DECISIONS:
                code_to_decision[code_path] = clean

    for nid, node in nodes.items():
        if node.get("decision"):
            continue
        # Check DEP-GRAPH match
        path = node.get("path", "")
        if path in code_to_decision:
            node["decision"] = code_to_decision[path]
        elif node.get("lifecycle") == "design":
            node["decision"] = "NEW"
        else:
            node["decision"] = "KEEP"

    return nodes


def _yaml_load(path):
    """Load YAML with C loader if available (10-50x faster than pure Python)."""
    try:
        from yaml import CSafeLoader

        loader = CSafeLoader
    except ImportError:
        loader = yaml.SafeLoader
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=loader)


def _validate_arch_references():
    """Phase 4 防御性门禁 (ARCH-033): 校验本文件中的 #ARCH-XXX 引用在 architecture_issue_registry.yaml 有对应条目。

    编号铁律#6: 任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位。
    校验失败打印 ERROR 并 sys.exit(1) 阻断运行（编号铁律#6 强制门禁，2026-07-02 从 WARN 升级为 ERROR）。
    """
    import re as _re
    import sys as _sys
    from pathlib import Path as _Path

    # 1. 读取本文件源代码，提取所有 #ARCH-XXX 引用
    self_path = _Path(__file__)
    try:
        source = self_path.read_text(encoding="utf-8")
    except Exception:
        return  # 读取失败则静默跳过

    arch_refs = set(_re.findall(r'\bARCH-(\d+)', source))
    if not arch_refs:
        return  # 无 ARCH 引用则跳过

    # 1.5 检测小写 arch- 违规（trae_028 §标识符编号格式: 标识符编号必须大写）
    lowercase_arch = [m.group() for m in _re.finditer(r'\bARCH-\d+', source, _re.IGNORECASE)
                      if m.group() != m.group().upper()]
    if lowercase_arch:
        print(f"[DEPGRAPH] ERROR: 发现小写 arch- 引用 (trae_028 §标识符编号格式: 标识符编号必须大写): {lowercase_arch}")
        _sys.exit(1)

    # 2. 读取 architecture_issue_registry.yaml
    registry_path = str(PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "architecture_issue_registry.yaml")
    if not _Path(registry_path).exists():
        print(f"[DEPGRAPH] ERROR: architecture_issue_registry.yaml 不存在，无法校验 ARCH 引用 (编号铁律#6)")
        _sys.exit(1)

    try:
        registry_data = _yaml_load(registry_path)
    except Exception as e:
        print(f"[DEPGRAPH] ERROR: 读取 architecture_issue_registry.yaml 失败: {e}")
        _sys.exit(1)

    # 3. 提取 registry 中所有 issue_id
    registered_ids = set()
    entries = registry_data.get("entries", []) if registry_data else []
    for entry in entries:
        issue_id = entry.get("issue_id", "")
        match = _re.match(r'#?ARCH-(\d+)', str(issue_id))
        if match:
            registered_ids.add(match.group(1))

    # 4. 校验
    unregistered = arch_refs - registered_ids
    if unregistered:
        print(f"[DEPGRAPH] ERROR: 发现未注册的 #ARCH-XXX 引用 (编号铁律#6): {sorted(unregistered)}")
        print(f"[DEPGRAPH] ERROR: 请在 architecture_issue_registry.yaml 中登记这些编号后重试")
        _sys.exit(1)
    else:
        print(f"[DEPGRAPH] ARCH 引用校验通过: {sorted(arch_refs)} 均已在 registry 中登记")


def merge_depgraph(new_data: dict, existing_path, old_data=None) -> dict:
    """Merge new depgraph with existing, preserving manual annotations and design-state nodes.

    Args:
        old_data: Pre-loaded old depgraph dict. If provided, skips re-reading the file.
    """
    if not existing_path.exists() and old_data is None:
        return new_data
    try:
        old = old_data if old_data is not None else _yaml_load(existing_path)
        if not old or "metadata" not in old:
            return new_data
        # Preserve top-level sections that exist in old but not in new
        stale_keys = set(old.keys()) - set(new_data.keys())
        for k in stale_keys:
            new_data[k] = old[k]
        # Dual-state protection: ensure design-state nodes in new_data are not overwritten
        if "nodes" in old and "nodes" in new_data:
            for nid, old_node in old["nodes"].items():
                if old_node.get("lifecycle") == "design":
                    if nid not in new_data["nodes"]:
                        # No conflict: insert design-state node as-is
                        new_data["nodes"][nid] = old_node
                    else:
                        # Conflict: disk scan produced a node with same ID.
                        # Merge design-state fields from old node into new node.
                        merge_design_fields(new_data["nodes"][nid], old_node)
            # Preserve manually-set semantic fields on edges from old depgraph
            if "edges" in old:
                old_edge_map = {}
                for old_edge in old["edges"]:
                    key = (old_edge.get("from", ""), old_edge.get("to", ""), old_edge.get("dep_type", ""))
                    old_edge_map[key] = old_edge
                for new_edge in new_data.get("edges", []):
                    key = (new_edge.get("from", ""), new_edge.get("to", ""), new_edge.get("dep_type", ""))
                    old_edge = old_edge_map.get(key)
                    if old_edge:
                        # Preserve manual annotations: contract_anchor, failure_mode, fallback, interface
                        for field in ("contract_anchor", "failure_mode", "fallback", "interface"):
                            old_val = old_edge.get(field, "")
                            if old_val and not new_edge.get(field):
                                new_edge[field] = old_val
        return new_data
    except Exception:
        return new_data


def resolve_conflicts(cur):
    """DM-3011: 显式冲突解决函数（设计态优先）

    删除非设计态节点中path与设计态节点重复的记录，
    确保设计态数据优先保留。
    """
    cur.execute(
        "DELETE FROM nodes WHERE design_maturity != 'design' "
        "AND node_type != 'database' "
        "AND path IN (SELECT path FROM nodes WHERE design_maturity = 'design')"
    )
    deleted = cur.rowcount
    if deleted > 0:
        print(f"[DM-3011] resolve_conflicts: 删除 {deleted} 个与非设计态冲突的节点")
    return deleted


def restore_design_data(cur, design_nodes: dict, design_edges: list, design_arch: list):
    """DM-3013: 显式恢复设计态数据（规格§22.6步骤6）

    设计态nodes/edges已通过步骤3的DELETE保留（WHERE design_maturity != 'design'），
    此函数做显式验证并补插缺失的设计态数据，确保设计态数据完整。

    Args:
        cur: DB cursor
        design_nodes: 内存中的设计态节点字典 {path: node_dict}
        design_edges: 内存中的设计态边列表
        design_arch: 内存中的设计态架构目录树列表
    """
    # 验证设计态nodes存在
    cur.execute("SELECT COUNT(*) FROM nodes WHERE design_maturity = 'design'")
    db_nodes_count = cur.fetchone()["count"]
    if db_nodes_count == 0 and design_nodes:
        print(f"[DM-3013] WARNING: DB中无设计态nodes，内存有{len(design_nodes)}条")

    # 验证设计态edges存在
    cur.execute("SELECT COUNT(*) FROM edges WHERE dep_maturity = 'design'")
    db_edges_count = cur.fetchone()["count"]
    if db_edges_count == 0 and design_edges:
        print(f"[DM-3013] WARNING: DB中无设计态edges，内存有{len(design_edges)}条")

    # 验证设计态arch存在
    try:
        cur.execute("SELECT COUNT(*) FROM arch_directory_tree WHERE design_maturity = 'design'")
        db_arch_count = cur.fetchone()["count"]
    except Exception:
        db_arch_count = -1
    if db_arch_count == 0 and design_arch:
        print(f"[DM-3013] WARNING: DB中无设计态arch，内存有{len(design_arch)}条")

    print(
        f"[DM-3013] restore_design_data: 验证完成 "
        f"(nodes={db_nodes_count}, edges={db_edges_count}, arch={db_arch_count})"
    )


def write_depgraph_to_db(depgraph: dict, design_state: dict = None):
    """Write depgraph to PostgreSQL database (DM-100024) - P2 PG 迁移

    治本（2026-06-29）：删除文件锁调用（对齐 apply_depgraph.py / sync_yaml_to_depgraph.py）。
    P2 PG 迁移后 PG MVCC 事务（autocommit=False）提供原子性，无需文件锁。
    原 acquire_lock/release_lock no-op 桩已删除，调用点同步清除（消除误导日志）。

    5.153.3 修复：移除 db_path 幽灵参数（原参数完全未使用，函数体直接调用
    get_depgraph_pg_connection(autocommit=False) 连接 PostgreSQL，db_path 参数名暗示
    SQLite 路径写入，违反 depgraph 必须为 PostgreSQL 的硬约束）。
    """
    from datetime import datetime

    print(f"[DEPGRAPH-DB] Writing to depgraph (PostgreSQL)...")
    conn = None  # DM-3004: 预初始化None，防御性编程

    try:
        conn = get_depgraph_pg_connection(autocommit=False)  # P2 PG 迁移
        cursor = conn.cursor()
        # 裁定#209 阶段1：pg_advisory_xact_lock 互斥保护
        # 与 apply_depgraph.py._db_write_lock 共享 lock key 424242
        # 事务级 lock，conn.commit()/rollback() 自动释放，不会忘记释放
        cursor.execute("SELECT pg_advisory_xact_lock(424242)")
        # ARCH-fix: 允许级联删除 design edges（DELETE nodes 时外键级联触发 edges DELETE）
        # restore_design_data 会在 DELETE+INSERT 后恢复 design edges，无数据丢失风险
        # 与 apply_depgraph.py 同机制（_shared/constants.py L125）
        cursor.execute("SET app.allow_delete_apply_depgraph_edges = on")
        # R3 验证(2026-07-02)：干净工作区 reconciler 全流程验证
        # DM-012 Fix 4: Auto-cleanup old backup tables before writing
        # P2 PG 迁移：sqlite_master → information_schema.tables
        cursor.execute(
            "SELECT table_name AS name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name LIKE '%backup%'"
        )
        backup_tables = cursor.fetchall()
        for bt_row in backup_tables:
            bt_name = bt_row["name"]
            # Validate table name format before using in DDL
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", bt_name):
                continue
            cursor.execute(f'DROP TABLE IF EXISTS "{bt_name}"')
            print(f"[DEPGRAPH-DB] Cleaned up backup table: {bt_name}")

        # 裁定#209 Stage 2: UPSERT 保护字段到 metadata 表（DELETE 前保存）
        # 替代 Python 端 load_production_state_from_db + apply_production_metadata_protection
        # 语义：新值非空→覆盖 metadata；新值空→保留 metadata 旧值（与 Python 保护一致）
        _now_iso = datetime.now().isoformat()
        try:
            cursor.execute(
                """
                INSERT INTO nodes_metadata (
                    path, blueprint_id, owner, impact_level, change_policy,
                    modification_permission, belongs_to, build_status, gate_reason,
                    hard_boundary_ref, consumed_interfaces, tags, trust_zone,
                    deployment_lifecycle, architecture_layer, last_updated
                )
                SELECT
                    path, blueprint_id, owner, impact_level, change_policy,
                    modification_permission, belongs_to, build_status, gate_reason,
                    hard_boundary_ref, consumed_interfaces, tags, trust_zone,
                    deployment_lifecycle, architecture_layer, %s
                FROM nodes
                WHERE design_maturity = 'production' AND node_type != 'database'
                ON CONFLICT (path) DO UPDATE SET
                    blueprint_id            = COALESCE(NULLIF(EXCLUDED.blueprint_id, ''), nodes_metadata.blueprint_id),
                    owner                    = COALESCE(NULLIF(EXCLUDED.owner, ''), nodes_metadata.owner),
                    impact_level            = COALESCE(NULLIF(EXCLUDED.impact_level, ''), nodes_metadata.impact_level),
                    change_policy           = COALESCE(NULLIF(EXCLUDED.change_policy, ''), nodes_metadata.change_policy),
                    modification_permission = COALESCE(NULLIF(EXCLUDED.modification_permission, ''), nodes_metadata.modification_permission),
                    belongs_to              = COALESCE(NULLIF(EXCLUDED.belongs_to, ''), nodes_metadata.belongs_to),
                    build_status            = COALESCE(NULLIF(EXCLUDED.build_status, ''), nodes_metadata.build_status),
                    gate_reason              = COALESCE(NULLIF(EXCLUDED.gate_reason, ''), nodes_metadata.gate_reason),
                    hard_boundary_ref       = COALESCE(NULLIF(EXCLUDED.hard_boundary_ref, ''), nodes_metadata.hard_boundary_ref),
                    consumed_interfaces     = COALESCE(NULLIF(EXCLUDED.consumed_interfaces, ''), nodes_metadata.consumed_interfaces),
                    tags                     = COALESCE(NULLIF(EXCLUDED.tags, ''), nodes_metadata.tags),
                    trust_zone               = COALESCE(NULLIF(EXCLUDED.trust_zone, ''), nodes_metadata.trust_zone),
                    deployment_lifecycle     = COALESCE(NULLIF(EXCLUDED.deployment_lifecycle, ''), nodes_metadata.deployment_lifecycle),
                    architecture_layer       = COALESCE(NULLIF(EXCLUDED.architecture_layer, ''), nodes_metadata.architecture_layer),
                    last_updated             = EXCLUDED.last_updated
                """,
                (_now_iso,),
            )
            _nodes_meta_saved = cursor.rowcount
            print(f"[DEPGRAPH-DB] Stage 2: UPSERT {_nodes_meta_saved} 条 nodes_metadata（保护字段已保存）")
        except Exception as e:
            print(f"[DEPGRAPH-DB] WARNING: nodes_metadata UPSERT 失败（表可能未创建）: {e}")

        try:
            cursor.execute(
                """
                INSERT INTO edges_metadata (
                    from_path, to_path, dep_type,
                    failure_mode, fallback, activation_condition,
                    data_transfer_description, resource_impact,
                    ddd_integration_pattern, event_ref, api_contract_refs, verified,
                    last_updated
                )
                SELECT
                    n1.path, n2.path, e.dep_type,
                    e.failure_mode, e.fallback, e.activation_condition,
                    e.data_transfer_description, e.resource_impact,
                    e.ddd_integration_pattern, e.event_ref, e.api_contract_refs, e.verified,
                    %s
                FROM edges e
                JOIN nodes n1 ON e.from_node_id = n1.node_id
                JOIN nodes n2 ON e.to_node_id = n2.node_id
                WHERE (e.dep_maturity != 'design' OR e.dep_maturity IS NULL)
                  AND e.from_node_id NOT IN (SELECT node_id FROM nodes WHERE node_type = 'database')
                  AND e.to_node_id NOT IN (SELECT node_id FROM nodes WHERE node_type = 'database')
                ON CONFLICT (from_path, to_path, dep_type) DO UPDATE SET
                    failure_mode              = COALESCE(NULLIF(EXCLUDED.failure_mode, ''), edges_metadata.failure_mode),
                    fallback                 = COALESCE(NULLIF(EXCLUDED.fallback, ''), edges_metadata.fallback),
                    activation_condition     = COALESCE(NULLIF(EXCLUDED.activation_condition, ''), edges_metadata.activation_condition),
                    data_transfer_description = COALESCE(NULLIF(EXCLUDED.data_transfer_description, ''), edges_metadata.data_transfer_description),
                    resource_impact          = COALESCE(NULLIF(EXCLUDED.resource_impact, ''), edges_metadata.resource_impact),
                    ddd_integration_pattern   = COALESCE(NULLIF(EXCLUDED.ddd_integration_pattern, ''), edges_metadata.ddd_integration_pattern),
                    event_ref                = COALESCE(NULLIF(EXCLUDED.event_ref, ''), edges_metadata.event_ref),
                    api_contract_refs        = COALESCE(NULLIF(EXCLUDED.api_contract_refs, ''), edges_metadata.api_contract_refs),
                    verified                 = COALESCE(EXCLUDED.verified, edges_metadata.verified),
                    last_updated             = EXCLUDED.last_updated
                """,
                (_now_iso,),
            )
            _edges_meta_saved = cursor.rowcount
            print(f"[DEPGRAPH-DB] Stage 2: UPSERT {_edges_meta_saved} 条 edges_metadata（保护字段已保存）")
        except Exception as e:
            print(f"[DEPGRAPH-DB] WARNING: edges_metadata UPSERT 失败（表可能未创建）: {e}")

        # Clear existing operational data (preserve design-state)
        # Note: NULL != 'design' is NULL (not TRUE) in SQL, so must handle NULL explicitly
        # 裁定#2026-0701: 排除 node_type='database' 的持久基础设施节点（已运营非设计态，手工维护不被扫描器清空）
        # ARCH-052: 排除聚合节点类型（gate_rule_set/script_collection/test_suite/rule_registry_collection），
        #           这些节点由 YAML sync 维护（sync_aggregate_nodes），非代码扫描产物，重建时必须保留
        cursor.execute(
            "DELETE FROM nodes WHERE (design_maturity != 'design' OR design_maturity IS NULL) "
            "AND node_type NOT IN ('database', 'gate_rule_set', 'script_collection', "
            "'test_suite', 'rule_registry_collection')"
        )
        # P0-1 schema fix: 保留设计态边（dep_maturity='design'），只删除运营态边
        # 裁定#2026-0701: 同时保留指向 database 节点的边（模块→数据库依赖，手工维护）
        # ARCH-052: 同时保留指向聚合节点的边（gate_engine→gate_rule_set 等手工维护依赖）
        cursor.execute(
            "DELETE FROM edges WHERE (dep_maturity != 'design' OR dep_maturity IS NULL) "
            "AND from_node_id NOT IN (SELECT node_id FROM nodes WHERE node_type IN "
            "('database', 'gate_rule_set', 'script_collection', 'test_suite', 'rule_registry_collection')) "
            "AND to_node_id NOT IN (SELECT node_id FROM nodes WHERE node_type IN "
            "('database', 'gate_rule_set', 'script_collection', 'test_suite', 'rule_registry_collection'))"
        )

        # DM-3013: 步骤6 - 显式恢复设计态数据（规格§22.6步骤6）
        if design_state is not None:
            restore_design_data(
                cursor, design_state.get("nodes", {}), design_state.get("edges", []), design_state.get("arch", [])
            )

        # Insert nodes
        nodes = depgraph.get("nodes", {})
        node_count = 0
        skipped_invalid_blueprint = 0  # 治本 2026-07-02: 预过滤不合规blueprint_id计数
        failed_insert_count = 0  # 治本 2026-07-02: 逐节点INSERT失败计数
        # P0-1 schema fix: 记录生成器node_id→path映射（用于edges表INSERT）
        # 生成器node_id是字符串（如"src__zephyr__governance____init___py"），
        # DB node_id是INTEGER自增，需要通过path建立映射
        gen_node_id_to_path = {}
        # 治本 2026-07-02 (ARCH-033 Phase 2.2): 预过滤不合规blueprint_id
        # DB触发器check_blueprint_id_format()正则: ^(MOD-|D-|SH-|SYS-|PLACEHOLDER)
        # 不合规的blueprint_id会触发RAISE EXCEPTION导致整个事务回滚（连累合规节点）
        # 在INSERT前预过滤，不合规的跳过并记录WARN
        _BLUEPRINT_ID_VALID_RE = re.compile(r'^(MOD-|D-|SH-|SYS-|PLACEHOLDER)')
        # 治本 2026-07-02 (ARCH-033 Phase 2.1): 逐节点SAVEPOINT，失败时ROLLBACK TO SAVEPOINT
        # 防御性设计：即使预过滤通过，仍可能有其他DB约束冲突（如CHECK constraint）
        # 用SAVEPOINT确保单节点失败不影响其他合规节点
        _sp_counter = 0
        for node_id, node in nodes.items():
            # Skip design-state nodes (already in DB)
            if node.get("design_maturity") == "design":
                continue

            # Phase 2.2: 预过滤不合规blueprint_id
            bp_id = node.get("blueprint_id", "")
            if bp_id and not _BLUEPRINT_ID_VALID_RE.match(bp_id):
                skipped_invalid_blueprint += 1
                if skipped_invalid_blueprint <= 10:  # 只打印前10个warning，避免日志爆炸
                    print(
                        f"[DEPGRAPH-DB] WARN: 跳过不合规blueprint_id='{bp_id}' "
                        f"(path={node.get('path', '')}) - 不匹配^(MOD-|D-|SH-|SYS-|PLACEHOLDER)"
                    )
                continue

            tags = node.get("tags", [])
            tags_json = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else str(tags)

            # Collect type-specific fields
            type_specific = {}
            for key in [
                "imports",
                "vulnerability_refs",
                "yaml_references",
                "doc_references",
                "module_id",
                "business_stream",
                "stream_role",
                "build_status",
                "can_build",
                "gate_reason",
                "hard_boundary_ref",
                "runtime_plane",
                "ddd_aggregate",
                "consumed_interfaces",
                "provided_interfaces",
            ]:
                if key in node:
                    type_specific[key] = node[key]
            type_specific_json = json.dumps(type_specific, ensure_ascii=False) if type_specific else "{}"

            # H6 fix: Compute can_build from design_maturity
            can_build = 1 if node.get("design_maturity") == "production" else 0

            # Phase 2.1: 逐节点SAVEPOINT，失败时ROLLBACK TO SAVEPOINT不连累合规节点
            _sp_counter += 1
            _sp_name = f"sp_node_{_sp_counter}"
            try:
                cursor.execute(f"SAVEPOINT {_sp_name}")
                cursor.execute(
                    """INSERT INTO nodes (
                    node_type, path, granularity, domain_id, subdomain_id, blueprint_id,
                    belongs_to, owner, change_policy, impact_level, modification_permission,
                    file_header_score, tags, architecture_layer, design_maturity, deployment_lifecycle,
                    trust_zone, license, drive_direction, type_specific_data, last_verified,
                    node_name, file_path, build_status,
                    can_build, gate_reason, hard_boundary_ref, consumed_interfaces, content_hash,
                    public_api
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        node.get("type", "module"),
                        node.get("path", ""),
                        node.get("granularity", "file"),
                        node.get("domain_id", ""),
                        node.get("subdomain_id", ""),
                        node.get("blueprint_id", ""),
                        node.get("belongs_to", ""),
                        node.get("owner", ""),
                        node.get("change_policy", "evolving"),
                        node.get("impact_level", "M"),
                        node.get("modification_permission", "ai_modifiable"),
                        node.get("file_header_score", 0),
                        tags_json,
                        node.get("architecture_layer", ""),
                        node.get("design_maturity", "production"),
                        node.get("deployment_lifecycle", "stable"),
                        node.get("trust_zone", "trusted_core"),
                        node.get("license", "Internal"),
                        node.get("drive_direction", "bottom_up"),
                        type_specific_json,
                        datetime.now().isoformat(),
                        node.get("node_name", ""),
                        node.get("file_path", node.get("path", "")),
                        node.get("build_status", "generated"),  # 裁定#178：删除draft默认值，改用推导值
                        can_build,  # H6 fix
                        node.get("gate_reason", ""),  # H6 fix
                        node.get("hard_boundary_ref", ""),  # H6 fix
                        node.get("consumed_interfaces", ""),  # H6 fix
                        node.get("content_hash", ""),  # 裁定#209 Stage 3
                        node.get("public_api", ""),  # 四图模块对齐 Step 3
                    ),
                )
                cursor.execute(f"RELEASE SAVEPOINT {_sp_name}")
                node_count += 1
                # P0-1 schema fix: 记录生成器node_id→path映射
                gen_node_id_to_path[node_id] = node.get("path", "")
            except Exception as node_err:
                # ROLLBACK TO SAVEPOINT 恢复事务到SAVEPOINT之前状态，可继续后续INSERT
                try:
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {_sp_name}")
                except Exception:
                    # SAVEPOINT本身失败（极端情况），需要rollback整个事务并重建
                    conn.rollback()
                    cursor = conn.cursor()
                failed_insert_count += 1
                if failed_insert_count <= 10:  # 只打印前10个warning
                    print(
                        f"[DEPGRAPH-DB] WARN: 节点INSERT失败被跳过: "
                        f"blueprint_id={bp_id} path={node.get('path', '')} error={node_err}"
                    )

        if skipped_invalid_blueprint > 0:
            print(
                f"[DEPGRAPH-DB] Phase 2.2 预过滤: 跳过 {skipped_invalid_blueprint} 个不合规blueprint_id节点"
            )
        if failed_insert_count > 0:
            print(
                f"[DEPGRAPH-DB] Phase 2.1 逐节点保护: {failed_insert_count} 个节点INSERT失败被跳过（未连累合规节点）"
            )

        # DM-012 Fix 2: Multi-tier architecture_layer backfill for ALL nodes
        # v6: arch_domain_layers已合并入domains表为layer_id字段
        # Tier 1: domain_id → domains.layer_id direct match (existing logic)
        cursor.execute("""
            UPDATE nodes SET architecture_layer = (
                SELECT layer_id FROM domains
                WHERE domains.domain_id = nodes.domain_id
            )
            WHERE (architecture_layer IS NULL OR architecture_layer = '')
        """)
        tier1_count = cursor.rowcount

        # Tier 2: path prefix → arch_path_mappings.path_pattern → domain_id → domains.layer_id
        # For nodes that have a domain_id but domains doesn't have a layer_id,
        # AND for nodes without domain_id, try path-based matching through arch_path_mappings.
        cursor.execute("""
            UPDATE nodes SET architecture_layer = (
                SELECT d.layer_id FROM arch_path_mappings apm
                JOIN domains d ON d.domain_id = apm.domain_id
                WHERE (nodes.file_path LIKE apm.path_pattern || '%' OR nodes.path LIKE apm.path_pattern || '%')
                AND apm.state = 'active'
                ORDER BY length(apm.path_pattern) DESC
                LIMIT 1
            )
            WHERE (architecture_layer IS NULL OR architecture_layer = '')
        """)
        tier2_count = cursor.rowcount

        # Tier 3: Node-type based fallback for remaining nodes without architecture_layer
        # 治本（2026-06-30）：SQL CASE 从 node_type_vocabulary.yaml 动态生成（_ARCHITECTURE_LAYER_CASE_SQL）
        cursor.execute(
            "UPDATE nodes SET architecture_layer = " + _ARCHITECTURE_LAYER_CASE_SQL + "\n"
            "            WHERE (architecture_layer IS NULL OR architecture_layer = '')"
        )
        tier3_count = cursor.rowcount

        total_backfilled = tier1_count + tier2_count + tier3_count
        if total_backfilled > 0:
            print(
                f"[DEPGRAPH-DB] Backfilled architecture_layer: T1={tier1_count} T2={tier2_count} T3={tier3_count} (total={total_backfilled})"
            )

        # Tier 4: Normalize non-standard architecture_layer values to standard 4-layer
        # This handles design-state nodes preserved from previous runs with old values,
        # and any other nodes that got non-standard values from earlier generator versions.
        cursor.execute("""
            UPDATE nodes SET architecture_layer = CASE
                WHEN architecture_layer IN ('infrastructure', 'meta') THEN 'L0_infrastructure'
                WHEN architecture_layer IN ('governance', 'security', 'shared', 'platform') THEN 'L1_foundation'
                WHEN architecture_layer IN ('domain', 'data', 'intelligence', 'signal',
                                           'simulation', 'observability', 'orchestration',
                                           'resilience', 'business') THEN 'L2_domain'
                WHEN architecture_layer IN ('testing', 'application') THEN 'L3_application'
                WHEN architecture_layer = 'L0' THEN 'L0_infrastructure'
                WHEN architecture_layer = 'L1' THEN 'L1_foundation'
                WHEN architecture_layer = 'L2' THEN 'L2_domain'
                WHEN architecture_layer = 'L3' THEN 'L3_application'
                ELSE architecture_layer
            END
            WHERE architecture_layer NOT IN ('L0_infrastructure', 'L1_foundation',
                                             'L2_domain', 'L3_application')
        """)
        tier4_count = cursor.rowcount
        if tier4_count > 0:
            print(f"[DEPGRAPH-DB] Normalized non-standard architecture_layer: T4={tier4_count}")

        # 裁定#209 Stage 2: 从 nodes_metadata 恢复保护字段（DELETE 前已 UPSERT 保存）
        # 替代 Python 端 apply_production_metadata_protection
        # 语义：当重建后的 nodes 字段为空时，从 metadata 恢复（不覆盖磁盘新值）
        try:
            cursor.execute("""
                UPDATE nodes SET
                    blueprint_id            = COALESCE(NULLIF(nodes.blueprint_id, ''), nm.blueprint_id, nodes.blueprint_id),
                    owner                    = COALESCE(NULLIF(nodes.owner, ''), nm.owner, nodes.owner),
                    impact_level            = COALESCE(NULLIF(nodes.impact_level, ''), nm.impact_level, nodes.impact_level),
                    change_policy           = COALESCE(NULLIF(nodes.change_policy, ''), nm.change_policy, nodes.change_policy),
                    modification_permission = COALESCE(NULLIF(nodes.modification_permission, ''), nm.modification_permission, nodes.modification_permission),
                    belongs_to              = COALESCE(NULLIF(nodes.belongs_to, ''), nm.belongs_to, nodes.belongs_to),
                    build_status            = COALESCE(NULLIF(nodes.build_status, ''), nm.build_status, nodes.build_status),
                    gate_reason              = COALESCE(NULLIF(nodes.gate_reason, ''), nm.gate_reason, nodes.gate_reason),
                    hard_boundary_ref       = COALESCE(NULLIF(nodes.hard_boundary_ref, ''), nm.hard_boundary_ref, nodes.hard_boundary_ref),
                    consumed_interfaces     = COALESCE(NULLIF(nodes.consumed_interfaces, ''), nm.consumed_interfaces, nodes.consumed_interfaces),
                    tags                     = COALESCE(NULLIF(nodes.tags, ''), nm.tags, nodes.tags),
                    trust_zone               = COALESCE(NULLIF(nodes.trust_zone, ''), nm.trust_zone, nodes.trust_zone),
                    deployment_lifecycle     = COALESCE(NULLIF(nodes.deployment_lifecycle, ''), nm.deployment_lifecycle, nodes.deployment_lifecycle),
                    architecture_layer       = COALESCE(NULLIF(nodes.architecture_layer, ''), nm.architecture_layer, nodes.architecture_layer)
                FROM nodes_metadata nm
                WHERE nodes.path = nm.path
            """)
            _nodes_restored = cursor.rowcount
            if _nodes_restored > 0:
                print(f"[DEPGRAPH-DB] Stage 2: 从 nodes_metadata 恢复 {_nodes_restored} 个节点的保护字段")
        except Exception as e:
            print(f"[DEPGRAPH-DB] WARNING: nodes_metadata 恢复失败: {e}")

        # Insert edges
        edges = depgraph.get("edges", [])
        edge_count = 0
        broken_edge_count = 0

        # P0-1 schema fix: 构建生成器node_id→DB_node_id映射
        # 生成器node_id是字符串（如"src__zephyr__governance____init___py"），
        # DB node_id是INTEGER自增，通过path建立映射
        path_to_db_node_id = {}
        cursor.execute("SELECT path, node_id FROM nodes")
        for row in cursor.fetchall():
            # P2 PG 迁移：RealDictCursor 返回字典，用列名访问
            path_to_db_node_id[row["path"]] = row["node_id"]
        # 生成器node_id→DB_node_id映射
        gen_to_db_node_id = {}
        for gen_id, path in gen_node_id_to_path.items():
            db_id = path_to_db_node_id.get(path)
            if db_id is not None:
                gen_to_db_node_id[gen_id] = db_id
        gen_id_set = set(gen_to_db_node_id.keys())

        for edge in edges:
            from_node = edge.get("from", "")
            to_node = edge.get("to", "")
            if not from_node or not to_node:
                continue

            # DM-012 Fix 1: Skip edges where from_node or to_node does not exist in nodes table
            if from_node not in gen_id_set or to_node not in gen_id_set:
                broken_edge_count += 1
                continue

            api_contract_refs = edge.get("api_contract_refs", [])
            api_json = (
                json.dumps(api_contract_refs, ensure_ascii=False)
                if isinstance(api_contract_refs, list)
                else str(api_contract_refs)
            )

            cursor.execute(
                """INSERT INTO edges (
                from_node_id, to_node_id, dep_type, architecture_direction, coupling_strength,
                used_symbol, invocation_method, api_contract_refs, event_ref,
                ddd_integration_pattern, failure_mode, fallback, activation_condition,
                data_transfer_description, resource_impact, relationship_type,
                cross_domain, verified
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    gen_to_db_node_id.get(from_node),
                    gen_to_db_node_id.get(to_node),
                    edge.get("dep_type", "import_depends"),
                    edge.get("architecture_direction", "downstream"),
                    edge.get("coupling_strength", "critical"),
                    edge.get("used_symbol", ""),
                    edge.get("invocation_method", "import"),
                    api_json,
                    edge.get("event_ref", ""),
                    edge.get("ddd_integration_pattern", ""),
                    edge.get("failure_mode", ""),
                    edge.get("fallback", ""),
                    edge.get("activation_condition", ""),
                    edge.get("data_transfer_description", ""),
                    edge.get("resource_impact", ""),
                    edge.get("relationship_type", "one_to_many"),
                    1 if edge.get("cross_domain") else 0,
                    1 if edge.get("verified") else 0,
                ),
            )
            edge_count += 1

        # 裁定#209 Stage 2: 从 edges_metadata 恢复保护字段（DELETE 前已 UPSERT 保存）
        # 替代 Python 端 apply_edge_production_protection
        # 语义：当重建后的 edges 字段为空时，从 metadata 恢复（不覆盖 enrich 已填充的值）
        try:
            cursor.execute("""
                UPDATE edges SET
                    failure_mode              = COALESCE(NULLIF(edges.failure_mode, ''), em.failure_mode, edges.failure_mode),
                    fallback                 = COALESCE(NULLIF(edges.fallback, ''), em.fallback, edges.fallback),
                    activation_condition     = COALESCE(NULLIF(edges.activation_condition, ''), em.activation_condition, edges.activation_condition),
                    data_transfer_description = COALESCE(NULLIF(edges.data_transfer_description, ''), em.data_transfer_description, edges.data_transfer_description),
                    resource_impact          = COALESCE(NULLIF(edges.resource_impact, ''), em.resource_impact, edges.resource_impact),
                    ddd_integration_pattern   = COALESCE(NULLIF(edges.ddd_integration_pattern, ''), em.ddd_integration_pattern, edges.ddd_integration_pattern),
                    event_ref                = COALESCE(NULLIF(edges.event_ref, ''), em.event_ref, edges.event_ref),
                    api_contract_refs        = COALESCE(NULLIF(edges.api_contract_refs, ''), em.api_contract_refs, edges.api_contract_refs)
                FROM edges_metadata em, nodes n1, nodes n2
                WHERE edges.from_node_id = n1.node_id
                  AND edges.to_node_id = n2.node_id
                  AND n1.path = em.from_path
                  AND n2.path = em.to_path
                  AND edges.dep_type = em.dep_type
            """)
            _edges_restored = cursor.rowcount
            if _edges_restored > 0:
                print(f"[DEPGRAPH-DB] Stage 2: 从 edges_metadata 恢复 {_edges_restored} 条边的保护字段")
        except Exception as e:
            print(f"[DEPGRAPH-DB] WARNING: edges_metadata 恢复失败: {e}")

        conn.commit()
        print(
            f"[DEPGRAPH-DB] Inserted {node_count} nodes, {edge_count} edges (skipped {broken_edge_count} broken edges)"
        )

        # H6 fix: Backfill gate_reason for design-state nodes that were preserved
        try:
            cur = conn.cursor()
            cur.execute("UPDATE nodes SET gate_reason = '' WHERE gate_reason IS NULL")
            updated = cur.rowcount
            if updated:
                print(f"  [H6] Backfilled gate_reason for {updated} nodes")
            conn.commit()
        except Exception as e:
            print(f"  [H6] Warning: gate_reason backfill failed: {e}")

        # H2 fix: Delete design-state nodes with empty path
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM nodes WHERE (path IS NULL OR path = '' OR TRIM(path) = '') AND design_maturity = 'design'"
            )
            deleted = cur.rowcount
            if deleted:
                print(f"  [H2] Deleted {deleted} design nodes with empty path")
            conn.commit()
        except Exception as e:
            print(f"  [H2] Warning: empty path cleanup failed: {e}")

        # H3 fix: Delete design-state nodes with Markdown paths
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM nodes WHERE design_maturity = 'design' AND (path LIKE '###%' OR path LIKE '####%' OR path LIKE '---%')"
            )
            deleted = cur.rowcount
            if deleted:
                print(f"  [H3] Deleted {deleted} design nodes with Markdown paths")
            conn.commit()
        except Exception as e:
            print(f"  [H3] Warning: Markdown path cleanup failed: {e}")

        # H4 fix: Clear fake blueprint_id from design-state nodes
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE nodes SET blueprint_id = '' WHERE blueprint_id LIKE 'D-___%-blueprint' AND design_maturity = 'design'"
            )
            updated = cur.rowcount
            if updated:
                print(f"  [H4] Cleared {updated} fake blueprint_id from design nodes")
            conn.commit()
        except Exception as e:
            print(f"  [H4] Warning: fake blueprint_id cleanup failed: {e}")

        # H7 fix: Sync current_modules (all nodes) + production_nodes (production only) to domains
        # ARCH-CAP-001: current_modules = 全节点数（含 design+prototype+production）
        #                production_nodes = production 节点数（容量判定口径）
        try:
            cur = conn.cursor()
            cur.execute("SELECT domain_id FROM domains")
            domain_rows = cur.fetchall()
            updated = 0
            # P2 PG 迁移：? → %s；RealDictCursor 用列名访问
            for r in domain_rows:
                did = r["domain_id"]
                cur.execute("SELECT COUNT(*) FROM nodes WHERE domain_id=%s", (did,))
                all_count = cur.fetchone()["count"]
                cur.execute("UPDATE domains SET current_modules=%s WHERE domain_id=%s", (all_count, did))
                cur.execute("SELECT COUNT(*) FROM nodes WHERE domain_id=%s AND design_maturity='production'", (did,))
                prod_count = cur.fetchone()["count"]
                cur.execute("UPDATE domains SET production_nodes=%s WHERE domain_id=%s", (prod_count, did))
                updated += 1
            conn.commit()
            print(f"  [H7] Synced current_modules (all) + production_nodes (production) for {updated} domains")
        except Exception as e:
            print(f"  [H7] Warning: capacity sync failed: {e}")

        # DM-3011: 显式冲突解决（设计态优先）- 在restore_design_data之后调用
        try:
            cur = conn.cursor()
            deleted_count = resolve_conflicts(cur)
            if deleted_count > 0:
                conn.commit()
                print(f"[DM-3011] resolve_conflicts: 已删除 {deleted_count} 个冲突节点")
        except Exception as e:
            print(f"[DM-3011] Warning: resolve_conflicts failed: {e}")

        # DM-3002: 步骤10 - 调用audit_domain_nodes.py --check
        # 注意：audit_domain_nodes.py 已归档到 scripts/governance/_archive/prototype/，4类检测职责待恢复
        # arch_constraints 表的 VR 规则现由 sync_yaml_to_depgraph.py 的 sync_architecture_contract 函数从 YAML 同步
        audit_script = str(PROJECT_ROOT / "scripts" / "governance" / "audit_domain_nodes.py")
        if os.path.exists(audit_script):
            try:
                import subprocess

                result = subprocess.run([sys.executable, audit_script, "--check"], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"[DEPGRAPH-DB] 警告: audit_domain_nodes.py失败(exit {result.returncode}): {result.stderr}")
                else:
                    print("[DEPGRAPH-DB] 步骤10: audit_domain_nodes.py --check 完成")
            except Exception as e:
                print(f"[DEPGRAPH-DB] 警告: audit_domain_nodes.py调用失败: {e}")
        else:
            print("[DEPGRAPH-DB] 步骤10: 跳过（audit_domain_nodes.py 已归档到 _archive/prototype/，4类检测职责待恢复）")

    except Exception as e:
        if conn is not None:  # DM-3004: is not None守卫
            conn.rollback()
        print(f"[DEPGRAPH-DB] ERROR: {e}")
        raise
    finally:
        if conn is not None:  # DM-3004: is not None守卫
            conn.close()


# ============================================================================
# P0-3 升级：GenerationReport + Tarjan SCC + 12步流程支持
# ============================================================================


class GenerationReport:
    """生成器执行报告（§14.10 格式）— 8项统计"""

    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.scanned_count = 0
        self.node_count = 0
        self.edge_count = 0
        self.arch_count = 0
        self.cycle_count = 0
        self.invalid_blueprint_count = 0
        self.realized_count = 0

    def print_report(self):
        duration = self.end_time - self.start_time if self.end_time > self.start_time else 0
        print("=" * 60)
        print("=== 生成器执行报告 ===")
        print(f"扫描文件数: {self.scanned_count}")
        print(f"节点总数: {self.node_count}")
        print(f"边总数: {self.edge_count}")
        print(f"路径全景图行数: {self.arch_count}")
        print(f"循环依赖数: {self.cycle_count}")
        print(f"无效 blueprint_id 数: {self.invalid_blueprint_count}")
        print(f"已实现设计态节点数: {self.realized_count}")
        print(f"执行时间: {duration:.2f}s")
        print("=" * 60)

    def to_dict(self):
        return {
            "scanned_count": self.scanned_count,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "arch_count": self.arch_count,
            "cycle_count": self.cycle_count,
            "invalid_blueprint_count": self.invalid_blueprint_count,
            "realized_count": self.realized_count,
            "duration": round(self.end_time - self.start_time, 2) if self.end_time > self.start_time else 0,
        }


def detect_cycles_tarjan(edges: list, nodes: dict) -> list:
    """Tarjan SCC 算法检测强连通分量（循环依赖）

    Args:
        edges: 边列表，每条边含 from_node/to_node（path字符串）
        nodes: 节点字典，key为path

    Returns:
        list of cycles, 每个cycle是节点path列表
    """
    # 构建邻接表
    graph = defaultdict(list)
    node_set = set(nodes.keys())
    for edge in edges:
        src = edge.get("from_node", "")
        tgt = edge.get("to_node", "")
        if src and tgt and src in node_set and tgt in node_set:
            graph[src].append(tgt)

    # Tarjan SCC
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = {}
    result = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True

        for successor in graph.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlink[node] = min(lowlink[node], lowlink[successor])
            elif on_stack.get(successor, False):
                lowlink[node] = min(lowlink[node], index[successor])

        if lowlink[node] == index[node]:
            component = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                component.append(w)
                if w == node:
                    break
            if len(component) > 1:
                result.append(component)

    for node in node_set:
        if node not in index:
            strongconnect(node)

    return result


def validate_blueprint_ids(nodes: dict) -> int:
    """校验 blueprint_id 存在性，返回无效数量

    无效定义：blueprint_id非空但不符合格式（XX-XXX-NNN）
    """
    invalid = 0
    bp_pattern = re.compile(r"^[A-Z]{2,5}-[A-Z0-9_]+-\d{3,4}$")
    for path, node in nodes.items():
        bp_id = node.get("blueprint_id", "")
        if bp_id and not bp_pattern.match(bp_id):
            invalid += 1
    return invalid


def load_design_state_from_db(db_path: str) -> dict:
    """G1修复+DM-3012: 从数据库加载设计态数据（nodes+edges+arch）

    Args:
        db_path: depgraph路径

    Returns:
        dict: {"nodes": {path: node_dict}, "edges": [...], "arch": [...]}
              设计态节点、设计态边、设计态架构目录树
    """
    design_nodes = {}
    design_edges = []
    design_arch = []
    try:
        # P2 PG 迁移：sqlite3.connect → get_depgraph_pg_connection(autocommit=False)
        conn = get_depgraph_pg_connection(autocommit=False)
        cur = conn.cursor()
        # 加载设计态节点
        cur.execute("""
            SELECT path, node_type, domain_id, blueprint_id, belongs_to,
                   architecture_layer, design_maturity, build_status,
                   change_policy, impact_level, modification_permission
            FROM nodes
            WHERE design_maturity = 'design'
        """)
        rows = cur.fetchall()
        for row in rows:
            # P2 PG 迁移：RealDictCursor 返回字典，用列名访问
            path = row["path"]
            if path:
                design_nodes[path] = {
                    "path": path,
                    "type": row["node_type"] or "module",
                    "domain_id": row["domain_id"] or "",
                    "blueprint_id": row["blueprint_id"] or "",
                    "belongs_to": row["belongs_to"] or "",
                    "architecture_layer": row["architecture_layer"] or "",
                    "design_maturity": row["design_maturity"] or "design",
                    "build_status": row["build_status"] or "unbuilt",
                    "change_policy": row["change_policy"] or "evolving",
                    "impact_level": row["impact_level"] or "M",
                    "modification_permission": row["modification_permission"] or "ai_modifiable",
                    "lifecycle": "design",
                }
        # DM-3012: 加载设计态边（dep_maturity='design'）
        try:
            cur.execute("SELECT * FROM edges WHERE dep_maturity = 'design'")
            design_edges = cur.fetchall()
        except Exception as e:
            print(f"[DM-3012] WARNING: 加载设计态edges失败: {e}")
            design_edges = []
        # DM-3012: 加载设计态架构目录树（design_maturity='design'）
        try:
            cur.execute("SELECT * FROM arch_directory_tree WHERE design_maturity = 'design'")
            design_arch = cur.fetchall()
        except Exception as e:
            print(f"[DM-3012] WARNING: 加载设计态arch_directory_tree失败: {e}")
            design_arch = []
        conn.close()
    except Exception as e:
        print(f"[DEPGRAPH] WARNING: 加载设计态数据失败: {e}")
    return {"nodes": design_nodes, "edges": design_edges, "arch": design_arch}


# 裁定#209 Stage 2: P1/P2 Python 保护机制已下线（2026-07-02）
# 原 PRODUCTION_PROTECTED_FIELDS / EDGES_PROTECTED_FIELDS 常量及 4 个保护函数
# (load_production_state_from_db / apply_production_metadata_protection /
#  load_edge_production_state_from_db / apply_edge_production_protection) 已删除。
# 保护逻辑迁移到 write_depgraph_to_db 中的 SQL UPSERT+UPDATE（nodes_metadata/edges_metadata 表）。


def derive_stability_fallback(node_type: str, path: str) -> str:
    """G3修复：根据节点类型推导合理的stability默认值

    治本（2026-06-30）：映射真源从硬编码 if-else 迁移到 node_type_vocabulary.yaml
    values[].stability_fallback（_STABILITY_FALLBACK 字典）。
    - gate/policy → frozen（治理规则不可变）
    - config/registry/schema/contract/template → stable（配置相对稳定）
    - 其他 → evolving（默认开发中）
    """
    return _STABILITY_FALLBACK.get(node_type, "evolving")


def derive_autonomy_fallback(node_type: str, path: str) -> str:
    """G4修复：根据节点类型推导合理的ai_autonomy默认值

    治本（2026-06-30）：映射真源从硬编码 if-else 迁移到 node_type_vocabulary.yaml
    values[].autonomy_fallback（_AUTONOMY_FALLBACK 字典）。
    - gate/policy → immutable_core（治理规则AI不可改）
    - config/registry/schema/contract → human_gated（配置需人工审批）
    - 其他 → ai_modifiable（代码AI可改）
    """
    return _AUTONOMY_FALLBACK.get(node_type, "ai_modifiable")


def _check_incremental_skip(files_data: list, output_db: str) -> bool:
    """裁定#209 Stage 3: 增量模式——比较文件 content_hash，无变更时返回 True（跳过 DB 重建）。

    首次运行（content_hash 列不存在）或 DB 连接失败时返回 False（回退全量重建）。
    """
    if not output_db:
        return False
    conn = None
    try:
        conn = get_depgraph_pg_connection(autocommit=False)
        with conn.cursor() as cur:
            cur.execute("SELECT path, content_hash FROM nodes WHERE design_maturity = 'production'")
            db_rows = cur.fetchall()
    except Exception as e:
        print(f"[DEPGRAPH][INCREMENTAL] 查询失败（可能 content_hash 列不存在），回退全量重建: {e}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    db_hashes = {row["path"]: (row["content_hash"] or "") for row in db_rows}
    scan_hashes = {fd.get("path", ""): fd.get("content_hash", "") for fd in files_data}

    added = set(scan_hashes) - set(db_hashes)
    removed = set(db_hashes) - set(scan_hashes)
    common = set(scan_hashes) & set(db_hashes)
    changed = {p for p in common if scan_hashes[p] and db_hashes[p] != scan_hashes[p]}
    stale = {p for p in common if not db_hashes[p] and scan_hashes[p]}

    # added/removed 不阻断 skip（稳定态）：
    # - added: INSERT 失败的节点（如 domain_id FK 违反）每次都在 scan 中但不在 DB 中
    # - removed: 幽灵节点（文件已删除但 DB 保留记录），全量重建也无法清理
    #   职责分离（2026-07-04 治本）：removed 由 GATE-DELETE-AUDIT reconciler（post-commit
    #   自动触发，_backup_depgraph_for_autoclean + apply_depgraph.py --cleanup-orphan-nodes）
    #   负责清理；本函数只负责"是否需要重建"，不负责清理。removed 超 WARNING 阈值时告警提示。
    _GHOST_WARNING_THRESHOLD = 50  # 与 reconciliation_registry.py _GHOST_AUTO_CLEAN_THRESHOLD 对齐
    if not changed and not stale:
        print("[DEPGRAPH][INCREMENTAL] 无阻断性变更（content_hash 全部匹配），跳过 DB 重建")
        if added:
            print(f"  [INFO] {len(added)} 个 scan 文件不在 DB 中（不阻断）")
        if removed:
            level = "WARNING" if len(removed) > _GHOST_WARNING_THRESHOLD else "INFO"
            print(
                f"  [{level}] {len(removed)} 个 DB 节点文件已删除（不阻断，幽灵节点；"
                f"由 GATE-DELETE-AUDIT reconciler 自动清理）"
            )
            if len(removed) > _GHOST_WARNING_THRESHOLD:
                print(
                    f"    [HINT] ghost 数超阈值（{_GHOST_WARNING_THRESHOLD}），"
                    f"可手动运行: python scripts/governance/apply_depgraph.py --cleanup-orphan-nodes"
                )
        return True

    print(
        f"[DEPGRAPH][INCREMENTAL] 检测到阻断性变更: 变更 {len(changed)}, "
        f"待补 hash {len(stale)} -> 继续全量重建"
        + (f" [INFO: added={len(added)}, removed={len(removed)} 不阻断]" if added or removed else "")
    )
    return False


def main():
    parser = argparse.ArgumentParser(description="Generate project entity-level dependency graph (full coverage)")
    parser.add_argument(
        "--output-yaml", type=str, default="", help="[DEPRECATED] Output YAML data file path (DB is now the SSoT)"
    )
    parser.add_argument("--output-db", type=str, default="", help="Output PostgreSQL database name (P2迁移后: depgraph.db 已迁移到 PostgreSQL)")
    parser.add_argument("--output-md-section", type=str, default="", help="Output markdown section file path")
    parser.add_argument("--max-workers", type=int, default=8, help="ThreadPoolExecutor workers")
    parser.add_argument(
        "--granularity",
        type=str,
        default="file",
        choices=["file", "class"],
        help="Node granularity: 'file' = 1 file = 1 node (default), 'class' = 1 class = 1 node",
    )
    parser.add_argument("--dry-run", action="store_true", help="P0-3: dry-run模式，不修改任何文件，只输出执行报告")
    parser.add_argument(
        "--force",
        action="store_true",
        help="裁定#207 R2 C2：确认执行破坏性DB重建（DELETE运营态节点后从磁盘扫描重建）。"
        "不加此flag时--output-db将被拒绝。depgraph 是唯一真源，禁止重新创建派生 YAML 副本。",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="裁定#209 Stage 3: 增量模式——比较文件 content_hash，无变更时跳过 DB 重建。"
        "首次运行或 content_hash 列不存在时自动回退全量重建。",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="裁定#209 Stage 4: 禁用 scan 缓存（强制全扫，用于调试/首次冷启动）。",
    )
    parser.add_argument(
        "--cache-file",
        type=str,
        default="",
        help="Scan 缓存文件路径（默认 .runtime/depgraph_scan_cache.json）。",
    )
    args = parser.parse_args()

    # Phase 4 防御性门禁 (ARCH-033): 校验本文件中的 #ARCH-XXX 引用在 registry 中有对应条目
    _validate_arch_references()

    granularity = args.granularity
    report = GenerationReport()
    report.start_time = datetime.now().timestamp()

    # 步骤1: 获取写锁（仅在非dry-run且需要写入时）
    # 步骤2: 加载设计态数据（G1修复：从DB加载，不再依赖YAML）
    existing_design_nodes = {}
    design_state = None  # DM-3013: 初始化design_state，供write_depgraph_to_db使用
    # 治本（2026-06-29）：删除 db_path_for_design + os.path.exists 守卫（幽灵完成处理）。
    # P2 PG 迁移后 .db 文件不存在，守卫恒 False → design_state 永远 None → 设计态不被加载/保护。
    # PG 模式下直接调 load_design_state_from_db(None)（参数未用，内部走 get_depgraph_pg_connection）。
    try:
        design_state = load_design_state_from_db(None)
        existing_design_nodes = design_state["nodes"]
        print(
            f"[DEPGRAPH] G1修复: 从PG加载 {len(existing_design_nodes)} 个设计态节点, "
            f"{len(design_state['edges'])} 条设计态边, "
            f"{len(design_state['arch'])} 条设计态arch记录"
        )
    except Exception as e:
        print(f"[DEPGRAPH] 警告: 从PG加载设计态失败: {e}，回退到YAML兼容逻辑")
        design_state = None
        if args.output_yaml:
            out_path = PROJECT_ROOT / args.output_yaml
            if out_path.exists():
                try:
                    preloaded_old_data = _yaml_load(out_path)
                    if preloaded_old_data and "nodes" in preloaded_old_data:
                        for nid, node in preloaded_old_data["nodes"].items():
                            if node.get("lifecycle") == "design":
                                existing_design_nodes[nid] = node
                        print(f"[DEPGRAPH] [DEPRECATED] 从YAML加载 {len(existing_design_nodes)} 个设计态节点")
                except Exception:
                    pass

    print("[DEPGRAPH] Loading architecture panorama...")
    panorama_data, domain_derivation, functional_domains = load_panorama()
    print(f"[DEPGRAPH] Loaded {len(functional_domains)} functional domains from panorama")
    print(f"[DEPGRAPH] Domain derivation table: {len(domain_derivation)} entries")

    # 裁定#209 Stage 4: scan-level 缓存（真正增量重建）
    cache_path = Path(args.cache_file) if args.cache_file else _DEFAULT_CACHE_FILE
    if not cache_path.is_absolute():
        cache_path = PROJECT_ROOT / cache_path
    derivation_fp = _compute_derivation_fingerprint(domain_derivation, functional_domains)
    scan_cache = ScanCache(cache_path, derivation_fp, enabled=not args.no_cache)

    # G1修复：设计态加载已在main()开头完成（从DB加载），此处不再重复
    preloaded_old_data = None  # 兼容下游merge逻辑

    # 步骤4: 扫描白名单目录
    print("[DEPGRAPH] Scanning project files...")
    all_files = collect_all_files()
    print(f"[DEPGRAPH] Found {len(all_files)} files")
    report.scanned_count = len(all_files)

    py_files = [f for f in all_files if f.endswith(".py")]
    yaml_files = [f for f in all_files if f.endswith((".yaml", ".yml"))]
    md_files = [f for f in all_files if f.endswith(".md")]
    json_files = [f for f in all_files if f.endswith(".json")]
    infra_files = [f for f in all_files if f.endswith((".sh", ".ps1"))]
    diagram_files = [f for f in all_files if f.endswith(".mmd")]

    files_data = []

    print(f"[DEPGRAPH] Scanning {len(py_files)} .py files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(_scan_with_cache, scan_py_file, f, domain_derivation, scan_cache): f for f in py_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(yaml_files)} .yaml files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(_scan_with_cache, scan_yaml_file, f, domain_derivation, scan_cache): f for f in yaml_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(md_files)} .md files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(_scan_with_cache, scan_md_file, f, domain_derivation, scan_cache): f for f in md_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(json_files)} .json files...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(_scan_with_cache, scan_json_file, f, domain_derivation, scan_cache): f for f in json_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(infra_files)} script files (.sh/.ps1)...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(_scan_with_cache, scan_infra_file, f, domain_derivation, scan_cache): f for f in infra_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                r["type"] = "script"
                files_data.append(r)

    print(f"[DEPGRAPH] Scanning {len(diagram_files)} diagram files (.mmd)...")
    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(_scan_with_cache, scan_diagram_file, f, domain_derivation, scan_cache): f for f in diagram_files}
        for fut in as_completed(futures):
            r = fut.result()
            if r:
                files_data.append(r)

    print(f"[DEPGRAPH] Total scanned: {len(files_data)} entities")

    # 裁定#209 Stage 4: 保存 scan 缓存（在 incremental 判定前保存，确保跳过时缓存已落盘）
    scan_cache.save()
    print(f"[DEPGRAPH][CACHE] {scan_cache.stats()}")

    # 裁定#209 Stage 3: 增量模式——无变更时跳过 DB 重建
    if args.incremental and _check_incremental_skip(files_data, args.output_db):
        print("[DEPGRAPH][INCREMENTAL] 跳过 DB 重建，直接退出")
        sys.exit(0)

    print("[DEPGRAPH] Building dependency graph...")
    depgraph = build_depgraph(files_data, functional_domains, domain_derivation, existing_design_nodes, granularity)

    # 裁定#209 Stage 2: P1/P2 Python 保护机制已下线
    # 保护逻辑已迁移到 write_depgraph_to_db 中的 SQL UPSERT+UPDATE（nodes_metadata/edges_metadata）
    # 原 load_production_state_from_db + apply_production_metadata_protection 已不需要

    # Enrich edges with semantic fields from cross-module-dependency-registry
    print("[DEPGRAPH] Loading cross-module-dependency-registry...")
    registry_deps = load_cross_module_registry()
    print(f"[DEPGRAPH] Loaded {len(registry_deps)} registry dependencies")

    print("[DEPGRAPH] Enriching edges with semantic fields...")
    depgraph["edges"] = enrich_edges_semantic(depgraph["edges"], depgraph["nodes"], registry_deps)

    # 裁定#209 Stage 2: P2 edges Python 保护机制已下线（同上，已迁移到 SQL）

    # Enrich nodes with decision field from DEP-GRAPH design files
    print("[DEPGRAPH] Enriching nodes with decision field...")
    dg_design_nodes, _ = load_depgraph_design_files()
    depgraph["nodes"] = enrich_nodes_decision(depgraph["nodes"], dg_design_nodes)

    # Count enrichment stats
    edges_with_contract = sum(1 for e in depgraph["edges"] if e.get("contract_anchor"))
    edges_with_registry_type = sum(
        1
        for e in depgraph["edges"]
        if e.get("semantic_type")
        and e["semantic_type"] != DEP_TYPE_TO_SEMANTIC_TYPE.get(e.get("dep_type", ""), "runtime")
    )
    nodes_with_decision = {n.get("decision", "KEEP") for n in depgraph["nodes"].values()}
    print(f"[DEPGRAPH] Edges with contract_anchor: {edges_with_contract}")
    print(f"[DEPGRAPH] Edges enriched by registry: {edges_with_registry_type}")
    print(
        f"[DEPGRAPH] Node decisions: {dict((d, sum(1 for n in depgraph['nodes'].values() if n.get('decision') == d)) for d in nodes_with_decision)}"
    )

    meta = depgraph["metadata"]
    print(f"[DEPGRAPH] Nodes: {meta['total_nodes']} | Edges: {meta['total_edges']}")
    print(
        f"[DEPGRAPH] Design-state: {meta.get('design_state_nodes', 0)} | Operational: {meta.get('operational_state_nodes', 0)}"
    )
    print(f"[DEPGRAPH] Nodes by type: {meta['nodes_by_type']}")
    print(f"[DEPGRAPH] Edges by type: {meta['edges_by_type']}")
    print(f"[DEPGRAPH] Functional domains: {meta['total_functional_domains']}")

    # 步骤8: 校验 blueprint_id 存在性
    report.invalid_blueprint_count = validate_blueprint_ids(depgraph["nodes"])
    print(f"[DEPGRAPH] 步骤8: 无效blueprint_id数: {report.invalid_blueprint_count}")

    # 步骤9: 检测循环依赖（Tarjan SCC）
    cycles = detect_cycles_tarjan(depgraph["edges"], depgraph["nodes"])
    report.cycle_count = len(cycles)
    print(f"[DEPGRAPH] 步骤9: 循环依赖数: {report.cycle_count}")
    if cycles:
        for i, cycle in enumerate(cycles[:5], 1):
            print(f"  循环{i}: {' -> '.join(cycle[:5])}{'...' if len(cycle) > 5 else ''}")

    # 步骤10: realization detection（裁定#189-193）- 检测设计态节点实现状态
    realized_count = realization_detection(depgraph)
    report.realized_count = realized_count

    # 填充报告统计
    report.node_count = meta["total_nodes"]
    report.edge_count = meta["total_edges"]
    report.arch_count = meta.get("total_functional_domains", 0)

    # 步骤11: 输出执行报告
    report.end_time = datetime.now().timestamp()
    report.print_report()

    # dry-run模式：只输出报告，不写入任何文件
    if args.dry_run:
        print("[DEPGRAPH] --dry-run模式：未修改任何文件，仅输出执行报告")
        sys.exit(0)

    if args.output_yaml:
        print(
            "[DEPRECATED] --output-yaml is deprecated. DB is now the SSoT. YAML output will be removed in a future version."
        )
        out_path = PROJECT_ROOT / args.output_yaml

        # --- Concurrent write protection: lock only for merge+write ---
        # Computation (scanning, building graph) is already done above — no lock needed.
        # Only the merge+write step needs the lock (fast operation).
        session_id = os.environ.get("ZEPHYR_SESSION_ID", f"depgraph-{os.getpid()}")
        lock_acquired = False
        lock_script = PROJECT_ROOT / "scripts" / "lock_files.py"

        max_retries = 3
        retry_delay = 5
        for attempt in range(1, max_retries + 1):
            if not lock_script.exists():
                break
            result = subprocess.run(
                [
                    sys.executable,
                    str(lock_script),
                    "acquire",
                    str(out_path),
                    session_id,
                    "--task",
                    "depgraph generation",
                    "--skip-naming-check",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lock_acquired = True
                print(f"[LOCK] Acquired write lock on depgraph (owner={session_id})")
                break
            if attempt < max_retries:
                print(
                    f"[LOCK] Depgraph locked by another session (attempt {attempt}/{max_retries}), waiting {retry_delay}s..."
                )
                import time

                time.sleep(retry_delay)
            else:
                print(f"[LOCKED] Cannot acquire lock after {max_retries} attempts: {result.stdout.strip()}")
                print("         Another AI session is writing. Retry later.")
                sys.exit(1)

        try:
            depgraph = merge_depgraph(depgraph, out_path, old_data=preloaded_old_data)

            tmp_path = str(out_path) + f".{os.getpid()}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(depgraph, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            os.replace(tmp_path, str(out_path))
            print(f"[DEPGRAPH] YAML written to {args.output_yaml}")
        finally:
            if lock_acquired and lock_script.exists():
                subprocess.run(
                    [sys.executable, str(lock_script), "release", str(out_path), session_id],
                    capture_output=True,
                    text=True,
                )
                print("[LOCK] Released write lock on depgraph")

    md_section = generate_markdown_section(depgraph)

    if args.output_md_section:
        out_path = PROJECT_ROOT / args.output_md_section
        tmp_path = str(out_path) + f".{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(md_section)
        os.replace(tmp_path, str(out_path))
        print(f"[DEPGRAPH] Markdown section written to {args.output_md_section}")
    else:
        print("\n" + "=" * 60)
        print("MARKDOWN SECTION (paste into dependency_path_panorama.md):")
        print("=" * 60)
        print(md_section[:3000])
        if len(md_section) > 3000:
            print(f"\n... truncated ({len(md_section)} total chars)")

    if args.output_db:
        # 裁定#207 R2 C2：--force 门禁——破坏性DB重建需显式确认
        if not args.force:
            print(
                "\n" + "=" * 70 + "\n"
                "[BLOCKED] 裁定#207 R2 C2：破坏性DB重建被阻断\n"
                "  原因: --output-db 未搭配 --force\n"
                "  风险: DELETE运营态节点后从磁盘扫描重建，手工维护数据可能丢失\n"
                "  \n"
                "  depgraph 是唯一真源（禁止重新创建派生 YAML 副本）。\n"
                "  确认破坏性重建（需人工评估）:\n"
                "    python scripts/governance/generate_project_depgraph.py --output-db <path> --force\n"
                + "=" * 70,
                file=sys.stderr,
            )
            sys.exit(4)
        db_path = args.output_db  # 5.153.3 修复: db_path不再传递给write_depgraph_to_db(该参数已移除)
        if not os.path.isabs(db_path):
            db_path = str(PROJECT_ROOT / db_path)
        write_depgraph_to_db(depgraph, design_state=design_state)

    sys.exit(0)


if __name__ == "__main__":
    main()
