#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.sync_yaml_to_depgraph
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# 真源说明：本脚本同步的是【规则数据】（trae_*.yaml/契约/门禁/词汇表）YAML→DB。
# 【架构数据】（nodes/edges）不通过本脚本同步，其真源在 DB，用 apply_depgraph.py 写入。
# 详见 AGENTS.md §真源分类（11.0.2）。
"""
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/sync_yaml_to_depgraph.py | §22.10
[MODULE] 无（独立脚本）
[INVARIANTS] YAML→DB单向同步; 27项同步; try/finally恢复触发器
[MODIFY-GUARD] 本脚本由autopilot执行
[CONSUMERS] autopilot session-20260618-001
[STABILITY] stable
[SAFETY] H
[AI_AUTONOMY] human_gated
[ERROR_CONTRACT] 同步失败→回滚+恢复触发器→exit 1; 触发器恢复失败→FATAL raise（DB无保护）; 成功→exit 0
[TESTS] 无

P0-7 YAML→DB 同步脚本：将规则/契约/门禁/词汇表从 YAML 同步到 depgraph
- 同步方向：YAML → DB 单向（禁止反向）
- 27项同步：cross_module_dependencies/architecture_contract/contract_mapping/gate_registry/
  functional_domain/vocabularies/architecture_rules/declarative_contract/frontmatter_field/
  registry_of_registries/directory_registry/rule_catalog/infrastructure/model_capability/
  hard_boundaries/business_streams/blueprint_links
  + ARCH-051 dataflow_registry + ARCH-052 aggregate_nodes + ARCH-053 interface_contracts/database_nodes
  + data_source_apis（#179）
  + data_source_assets（#180）+ service_assets（#181）+ config_assets（#182）
  + cross_layer_contracts（#154b）跨层(跨域)契约→contracts 表
- 通行证机制：临时DROP只读触发器→同步→finally恢复触发器
"""

__manifest__ = """
args: []
description: P0-7 YAML→DB 同步脚本：将规则/契约/门禁/词汇表从 YAML 同步到 depgraph
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import os
import sys
from datetime import UTC
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装，请运行: pip install pyyaml")
    sys.exit(EXIT_FINDINGS)

# _shared.constants 统一路径引用（裁定#206 / Bug H 修复——禁止硬编码绝对路径）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# P2 PG 迁移：删除 lock_files 文件锁（PG 用 MVCC）；导入 PG 连接入口
import psycopg2  # noqa: E402
from _shared.constants import EXIT_FINDINGS, REPO_ROOT, get_depgraph_pg_connection  # noqa: E402

# 治本（2026-06-27）：删除 DB_PATH = str(DEPGRAPH_DB_PATH)（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()，无文件路径概念。
RULES_DIR = str(REPO_ROOT / "docs" / "01_policies_and_standards")

# V5.1 裁定（2026-07-02）：8 张表保护。blueprint_links 移除——它是 nodes 派生物化视图，非 YAML 真源，apply_depgraph.py 可直接写入。
READONLY_TABLES = [
    "gates",
    "field_vocabularies",
    "registries",
    "cross_registry_rules",
    "hard_boundaries",
    "business_streams",
    "infrastructure_components",
    "model_capabilities",
    "data_source_apis",
    "data_source_assets",
    "service_assets",
    "rule_ai_perception",
]


def load_yaml(rel_path: str) -> dict:
    """加载 YAML 文件（使用绝对路径）"""
    full_path = os.path.join(RULES_DIR, rel_path)
    if not os.path.exists(full_path):
        print(f"  警告: {full_path} 不存在，跳过")
        return {}
    with open(full_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ========== 契约 domain_id 归一化映射（防止FK违规）==========
# YAML 中的 layer名/domain_key/文件路径 → 有效 domain_id
# 映射真源：cross_layer_contracts.yaml + contract_mapping_table.yaml + domains表

# contract_mapping_table.yaml layer_contracts 的 layer 字段 → domain_id
_LAYER_NAME_TO_DOMAIN = {
    "data": "D_MKT_DATA",
    # ARCH-045: signal 层不映射到单一 domain（signal 层包含 3 个平级子域）
    # 设为 None 后 sync_contract_mapping_table 跳过 signal 层契约写入
    "signal": None,
    "pf_core": "D_PF_CORE",
    "ex_core": "D_EX_CORE",
    "reporting": "D_REPORTING",
    "ml_train": "D_ML_TRAIN",
    "compliance": "D_GOV_ENFORCEMENT",  # 裁定#ARCH-target_layer_v1.0.0: D_COMPLIANCE已merge到D_GOV_ENFORCEMENT
    "simulation": "D_SIMULATION",
    "frontend": "D_FRONTEND",
}

# contract_mapping_table.yaml domain_contracts 的 YAML key → domain_id
# v1.1.0: alpha_signal_domain 拆分为 factor_domain + signal_domain（域平级无父子）
# 新增 domain_key 须在此字典登记映射，否则 sync_contract_mapping_table 会阻断并提示
_DOMAIN_KEY_TO_DOMAIN_ID = {
    "alpha_signal_domain": "D_ASHARE_SIGNAL",  # 旧key保留向后兼容
    "factor_domain": "D_FACTOR",
    # ARCH-045: signal_domain 含3子域(D_FUNDAMENTAL_SIGNAL/D_ASHARE_SIGNAL/D_SIGQC)，
    # 聚合 key 映射到主代表 D_ASHARE_SIGNAL，待后续架构裁定是否拆分
    "signal_domain": "D_ASHARE_SIGNAL",
    "ml_experiment_domain": "D_ML_TRAIN",
}

# AS-CT-*/ME-CT-* 域契约的 consumer_domain 映射（基于 direction 字段语义）
_DOMAIN_CONTRACT_CONSUMER = {
    "AS-CT-DATA-001": "D_FACTOR",
    # ARCH-045: AS-CT-FACTOR-001 的 consumer 原 D_SIGLEGACY 已删除，设为 None 跳过
    "AS-CT-FACTOR-001": None,
    "AS-CT-FACTOR-002": "D_FACTOR",
    "AS-CT-SIGNAL-001": "D_RISK",
    "AS-CT-VMS-001": "D_KNOWLEDGE",
    "ME-CT-FEATURE-001": "D_KNOWLEDGE",
    "ME-CT-TRAIN-001": "D_ML_TRAIN",
    "ME-CT-CHECKPOINT-001": "D_INTELLIGENCE",
    "ME-CT-AB-001": "D_INTELLIGENCE",
    "ME-CT-BACKTEST-001": "D_INTELLIGENCE",
    "ME-CT-SHADOW-001": "D_INTELLIGENCE",
}

# CTR-* 层契约 domain_mapping 为 null 时的 consumer_domain 回退
_CTR_CONSUMER_FALLBACK = {
    "CTR-001": "D_FACTOR",
    "CTR-TRACE-001": "D_FACTOR",
    "CTR-004": "D_EX_CORE",
    "CTR-005": "D_TRADING",
    "CTR-006": "D_RISK",
    "CTR-008": "D_RISK",
    "CTR-009": "D_INTELLIGENCE",
    "CTR-010": "D_INTELLIGENCE",
    "CTR-011": "D_ML_TRAIN",
    "CTR-012": "D_SHARED",
    "CTR-ERR-003": "D_RISK",
    # ARCH-045: CTR-P1-004/005 的 consumer 原 D_SIGLEGACY 已删除，设为 None 跳过
    "CTR-P1-003": "D_PF_CORE",
    "CTR-P1-004": None,
    "CTR-P1-005": None,
    "CTR-P1-006": "D_TRADING",
    "CTR-P1-009": "D_FRONTEND",
    "CTR-P1-012": "D_RISK",
    "CTR-P1-014": "D_SIMULATION",
    "CTR-P1-015": "D_RISK",
    "EXT-DASHBOARD-FLE-001": "D_SHARED",
}


def _normalize_provider(contract_id, raw_provider):
    """归一化 provider_domain：layer名/domain_key → 有效 domain_id"""
    if not raw_provider:
        return "D_SHARED"
    if raw_provider in _DOMAIN_KEY_TO_DOMAIN_ID:
        return _DOMAIN_KEY_TO_DOMAIN_ID[raw_provider]
    if raw_provider in _LAYER_NAME_TO_DOMAIN:
        return _LAYER_NAME_TO_DOMAIN[raw_provider]
    return raw_provider  # 已是有效 domain_id 或旧 layer_id（由 cleanup 处理）


def _normalize_consumer(contract_id, raw_consumer):
    """归一化 consumer_domain：contract_id引用/direction/null → 有效 domain_id"""
    # AS-CT-*/ME-CT-* 域契约：direction 字段不是 domain_id，用 contract_id 查映射
    if contract_id in _DOMAIN_CONTRACT_CONSUMER:
        return _DOMAIN_CONTRACT_CONSUMER[contract_id]
    if not raw_consumer:
        # layer_contracts 的 domain_mapping 为 null 时，用 CTR 回退映射
        if contract_id in _CTR_CONSUMER_FALLBACK:
            return _CTR_CONSUMER_FALLBACK[contract_id]
        return "D_SHARED"
    # domain_mapping 是另一个 contract_id（如 AS-CT-DATA-001）
    if raw_consumer in _DOMAIN_CONTRACT_CONSUMER:
        return _DOMAIN_CONTRACT_CONSUMER[raw_consumer]
    return raw_consumer  # 已是有效 domain_id（由 cleanup 处理无效值）


def _path_to_domain(path_str):
    """文件路径 → 归属 domain_id（declarative contract CT-* 专用）"""
    if not path_str:
        return "D_SHARED"
    if path_str.startswith("config/"):
        return "D_DATA_SEC"
    if "MOD-INF-005" in path_str:
        return "D_GOV_SCRIPTS"
    if "orchestrator" in path_str or "context-engine" in path_str:
        return "D_INTELLIGENCE"
    if "kb/" in path_str:
        return "D_KNOWLEDGE"
    if "scripts/governance" in path_str:
        return "D_GOV_SCRIPTS"
    if "infra_ops" in path_str:
        return "D_INFRA_OPS"
    if "capability.py" in path_str:
        return "D_DATA_SEC"
    return "D_SHARED"


def disable_readonly_triggers(cur):
    """临时禁用只读触发器（sync 脚本的通行证）

    P2 PG 迁移修正：PG 模式下 READONLY_TABLES 仍有 readonly_{table}_{insert/update/delete}
    触发器（SQLite→PG 迁移遗留）。使用 ALTER TABLE DISABLE TRIGGER USER 禁用用户定义触发器，
    保留 FK 约束触发器（session_replication_role 需 superuser，zephyr 非超权故用此法）。
    """
    for table in READONLY_TABLES:
        cur.execute(f"ALTER TABLE {table} DISABLE TRIGGER USER")
    print(f"  [PG] 已禁用 {len(READONLY_TABLES)} 张只读表的用户触发器（FK 约束保留）")


def restore_readonly_triggers(cur):
    """恢复只读触发器（无论同步成功/失败都必须恢复，否则DB无保护）

    S1.5 硬告警：best-effort 恢复所有表，收集失败项，任一失败则 raise。
    原实现遇首个失败即中断，剩余表保持触发器禁用=无保护。改为逐表尝试。
    """
    failed = []
    for table in READONLY_TABLES:
        try:
            cur.execute(f"ALTER TABLE {table} ENABLE TRIGGER USER")
        except Exception as e:
            failed.append(f"{table}: {e}")
    if failed:
        raise RuntimeError(f"触发器恢复失败 ({len(failed)}/{len(READONLY_TABLES)} 表): " + "; ".join(failed))
    print(f"  [PG] 已恢复 {len(READONLY_TABLES)} 张只读表的用户触发器")


def _resolve_module_to_single_node(cur, module_id, fallback_name):
    """把模块级依赖端解析为单一节点。返回 (node_id, status)。

    status: 'single' 唯一节点；'multi' 多节点（应跳过物化）；'none' 无法解析。

    治本(2026-07-23, depgraph 尺度错配)：cross_module_dependency_registry 的 source/target
    是模块级 module_id（如 MOD-L02-001），被多个节点共享。模块级关系无法唯一投影为节点级边——
    COUNT>1 时返回 'multi' 让调用方跳过，避免 LIMIT 1 取任意节点（实测返回 min node_id）导致
    边端点语义错误。模块级关系应留在 domain_dependencies/contracts 表，节点级真实依赖由
    production import 边覆盖。
    """
    if module_id:
        cur.execute("SELECT COUNT(*) AS n FROM nodes WHERE blueprint_id = %s", (module_id,))
        cnt = cur.fetchone()["n"]
        if cnt > 1:
            return (None, "multi")
        if cnt == 1:
            cur.execute("SELECT node_id FROM nodes WHERE blueprint_id = %s", (module_id,))
            return (cur.fetchone()["node_id"], "single")
    # COUNT==0 或无 module_id：回退到 path LIKE fallback_name（保持现行单节点兼容行为）
    if fallback_name:
        cur.execute("SELECT node_id FROM nodes WHERE path LIKE %s LIMIT 1", (f"%{fallback_name}%",))
        row = cur.fetchone()
        if row:
            return (row["node_id"], "single")
    return (None, "none")


# ========== P0 优先级同步 ==========


def sync_cross_module_dependencies(cur):
    """#152: 跨模块依赖注册表 → edges 表"""
    print("同步 #152: 跨模块依赖注册表 → edges...")
    data = load_yaml("_registry/catalogs/cross_module_dependency_registry.yaml")
    if not data:
        return

    # S1.3: edges 表三写分区硬约束
    # 只删除 YAML 同步的 design edge（valid_since IS NOT NULL）
    # 保留 apply_depgraph.py --add-design-edge 写入的（valid_since IS NULL）——DB 触发器 trg_edges_protect_apply_depgraph 硬保护
    # 禁止将 WHERE 条件扩大为 dep_maturity='design'（会误删 apply_depgraph edges，触发器会 ABORT）
    cur.execute("DELETE FROM edges WHERE dep_maturity = 'design' AND valid_since IS NOT NULL")

    deps = data.get("dependencies", [])
    synced = 0
    skipped_multi = 0
    for dep in deps:
        # YAML source/target 是模块级 module_id（如 MOD-INF-002），用 blueprint_id 匹配
        source = dep.get("source", "")
        source_name = dep.get("source_name", "")
        target = dep.get("target", "")
        target_name = dep.get("target_name", "")
        dep_id = dep.get("dep_id", "")

        from_nid, from_status = _resolve_module_to_single_node(cur, source, source_name)
        to_nid, to_status = _resolve_module_to_single_node(cur, target, target_name)

        # 治本(2026-07-23, depgraph 尺度错配)：模块级依赖映射到多节点时无法唯一投影为节点级边，跳过
        # 模块级关系留在 domain_dependencies/contracts 表，节点级真实依赖由 production import 边覆盖
        if from_status == "multi" or to_status == "multi":
            skipped_multi += 1
            print(
                f"  跳过 {dep_id}: source={source}({from_status}) target={target}({to_status}) "
                f"映射到多节点模块，无法唯一投影为节点级边"
            )
            continue

        if from_nid is not None and to_nid is not None:
            is_legal = 1 if dep.get("is_legal_cycle", False) else 0
            cur.execute(
                """
            INSERT INTO edges
            (from_node_id, to_node_id, dep_type, coupling_strength,
             architecture_direction, api_contract_refs, data_transfer_description,
             dep_maturity, valid_since, is_legal_cycle)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'design', %s, %s)
            """,
                (
                    from_nid,
                    to_nid,
                    dep.get("type", "import"),
                    dep.get("strength", "medium"),
                    dep.get("direction", "downstream"),
                    dep.get("contract_anchor", ""),
                    dep.get("description", ""),
                    dep.get("valid_since", ""),
                    is_legal,
                ),
            )
            synced += 1

    print(f"  同步 {synced}/{len(deps)} 条依赖（dep_maturity='design'，跳过 {skipped_multi} 条多节点模块）")


def sync_architecture_contract(cur):
    """#153: 架构契约 VR 规则 → arch_constraints 表"""
    print("同步 #153: 架构契约 VR 规则 → arch_constraints...")
    data = load_yaml("_registry/contracts/architecture_contract.yaml")
    if not data:
        return

    rules = data.get("validation_rules", [])
    synced = 0
    for rule in rules:
        rule_id = rule.get("rule_id", "")
        # name 是 NOT NULL，用 rule_id 或 description 作为 name
        name = rule.get("name", rule_id)
        cur.execute(
            """
        INSERT INTO arch_constraints
        (constraint_id, name, constraint_type, rule_definition, severity, enforcement)
        VALUES (%s, %s, 'architecture_contract', %s, %s, 'code')
        ON CONFLICT(constraint_id) DO UPDATE SET
            name=excluded.name,
            constraint_type=excluded.constraint_type,
            rule_definition=excluded.rule_definition,
            severity=excluded.severity,
            enforcement=excluded.enforcement
        """,
            (rule_id, name, str(rule.get("conditions", [])), rule.get("severity", "error")),
        )
        synced += 1

    print(f"  同步 {synced}/{len(rules)} 条 VR 规则")


def sync_contract_mapping_table(cur):
    """#154: 契约映射表 → contracts 表"""
    print("同步 #154: 契约映射表 → contracts...")
    data = load_yaml("_registry/contracts/contract_mapping_table.yaml")
    if not data:
        return

    synced = 0
    # 域契约（UPSERT 只更新基础字段）
    # YAML 结构：domain_contracts[domain_key] = {domain_id, blueprint, contracts: [...]}
    # FIX: domain_key/direction 不是 domain_id，必须归一化防止FK违规
    # 校验：domain_key 必须在 _DOMAIN_KEY_TO_DOMAIN_ID 中有映射，提前阻断防止 FK 违规
    domain_keys = [k for k, v in data.get("domain_contracts", {}).items() if isinstance(v, dict)]
    unregistered = [k for k in domain_keys if k not in _DOMAIN_KEY_TO_DOMAIN_ID]
    if unregistered:
        raise ValueError(
            f"contract_mapping_table.yaml 的 domain_contracts 含未登记 domain_key {unregistered}。"
            f"新增 domain_key 须同步在 _DOMAIN_KEY_TO_DOMAIN_ID 字典添加映射"
            f"（有效 domain_id 见 functional_domain_registry.yaml，D_ 前缀）。"
        )
    for domain_key, domain_data in data.get("domain_contracts", {}).items():
        if not isinstance(domain_data, dict):
            continue
        contracts = domain_data.get("contracts", [])
        for contract in contracts:
            if not isinstance(contract, dict):
                continue
            contract_id = contract.get("domain_contract_id", contract.get("contract_id", ""))
            if not contract_id:
                continue
            raw_consumer = contract.get("domain_mapping", contract.get("direction", ""))
            provider_domain = _normalize_provider(contract_id, domain_key)
            consumer_domain = _normalize_consumer(contract_id, raw_consumer)
            # ARCH-045: domain 为 None 时跳过（signal 层契约待重新分配到子域）
            if provider_domain is None or consumer_domain is None:
                continue
            cur.execute(
                """
            INSERT INTO contracts
            (contract_id, name, provider_domain, consumer_domain, contract_type)
            VALUES (%s, %s, %s, %s, 'domain_contract')
            ON CONFLICT(contract_id) DO UPDATE SET
                name=excluded.name,
                provider_domain=excluded.provider_domain,
                consumer_domain=excluded.consumer_domain,
                contract_type=excluded.contract_type
            """,
                (
                    contract_id,
                    contract.get("description", ""),
                    provider_domain,
                    consumer_domain,
                ),
            )
            synced += 1

    # 层契约
    # FIX: layer/domain_mapping 不是 domain_id，必须归一化防止FK违规
    for contract in data.get("layer_contracts", []):
        if not isinstance(contract, dict):
            continue
        contract_id = contract.get("contract_id", "")
        if not contract_id:
            continue
        raw_layer = contract.get("layer", "")
        raw_mapping = contract.get("domain_mapping", "") or ""
        provider_domain = _normalize_provider(contract_id, raw_layer)
        consumer_domain = _normalize_consumer(contract_id, raw_mapping)
        # ARCH-045: domain 为 None 时跳过（signal 层契约待重新分配到子域）
        if provider_domain is None or consumer_domain is None:
            continue
        cur.execute(
            """
        INSERT INTO contracts
        (contract_id, name, provider_domain, consumer_domain, contract_type)
        VALUES (%s, %s, %s, %s, 'layer_contract')
        ON CONFLICT(contract_id) DO UPDATE SET
            name=excluded.name,
            provider_domain=excluded.provider_domain,
            consumer_domain=excluded.consumer_domain,
            contract_type=excluded.contract_type
        """,
            (
                contract_id,
                contract.get("description", ""),
                provider_domain,
                consumer_domain,
            ),
        )
        synced += 1

    print(f"  同步 {synced} 条契约")


def sync_cross_layer_contracts(cur):
    """#154b: 跨层(跨域)契约 → contracts 表

    SSoT: architecture_model/contracts/cross_layer_contracts.yaml
    将 39 条跨域契约(CTR-*/OCP-*/EXT-*/AI-GOV-*/CT-TEL-*)从 YAML 同步到 contracts 表。
    与 sync_contract_mapping_table 互补：后者同步域契约(domain_contract)和层契约(layer_contract)，
    本函数同步跨域契约(cross_layer)。
    派生关系：YAML → DB → generate_contract_catalog.py → contract_catalog.md。

    FK 防护：target_domains 中可能含已删除的 domain_id（如 D_SIGLEGACY，ARCH-045），
    先查 domains 表获取有效集合，过滤无效值。
    """
    import json

    print("同步 #154b: 跨层(跨域)契约 → contracts...")
    yaml_path = REPO_ROOT / "architecture_model" / "contracts" / "cross_layer_contracts.yaml"
    if not yaml_path.exists():
        print(f"  跳过: {yaml_path} 不存在")
        return
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    contracts = data.get("contracts", [])
    if not contracts:
        print("  跳过: YAML 中无 contracts 条目")
        return

    # 查询有效 domain_id 集合（FK 约束防护）
    cur.execute("SELECT domain_id FROM domains")
    valid_domains = {row["domain_id"] for row in cur.fetchall()}

    # 删除旧的跨域契约（幂等：多次运行安全，不影响域契约/层契约）
    cur.execute("DELETE FROM contracts WHERE contract_type = 'cross_layer'")

    synced = 0
    skipped = 0
    for c in contracts:
        contract_id = c.get("id", "")
        if not contract_id:
            continue
        name = c.get("name", "")
        source_domain = c.get("source_domain", "")
        target_domains = c.get("target_domains", [])
        if isinstance(target_domains, str):
            target_domains = [target_domains]

        # FK 防护：source_domain 无效则跳过
        if source_domain and source_domain not in valid_domains:
            print(f"  跳过 {contract_id}: source_domain={source_domain} 不在 domains 表")
            skipped += 1
            continue
        if not source_domain:
            source_domain = "D_SHARED"

        # FK 防护：过滤 target_domains，只保留有效 domain_id
        valid_targets = [d for d in target_domains if d in valid_domains]
        if not valid_targets:
            # 无有效消费者，用 D_SHARED 兜底
            valid_targets = ["D_SHARED"]

        # consumer_domain 取第一个（主要消费者），完整列表存 schema_definition
        consumer_domain = valid_targets[0]

        # schema_definition 存完整信息（target_domains + physical_path + fields）
        schema_info = {
            "target_domains": valid_targets,
            "physical_path": c.get("physical_path", ""),
            "flow": c.get("flow", ""),
            "priority": c.get("priority", ""),
            "frozen": c.get("frozen", False),
            "stability": c.get("stability", ""),
            "fields": c.get("fields", []),
            "sla": c.get("sla", {}),
            "description": c.get("description", ""),
        }
        schema_definition = json.dumps(schema_info, ensure_ascii=False)
        version = c.get("schema_version", "")
        promise = c.get("flow", "")

        cur.execute(
            """
        INSERT INTO contracts
        (contract_id, name, provider_domain, consumer_domain, contract_type,
         schema_definition, version, promise)
        VALUES (%s, %s, %s, %s, 'cross_layer', %s, %s, %s)
        ON CONFLICT(contract_id) DO UPDATE SET
            name=excluded.name,
            provider_domain=excluded.provider_domain,
            consumer_domain=excluded.consumer_domain,
            contract_type=excluded.contract_type,
            schema_definition=excluded.schema_definition,
            version=excluded.version,
            promise=excluded.promise
        """,
            (contract_id, name, source_domain, consumer_domain, schema_definition, version, promise),
        )
        synced += 1

    print(f"  同步 {synced} 条跨域契约（跳过 {skipped} 条 FK 违规）")


# ========== P1 优先级同步 ==========


def sync_gate_registry(cur):
    """#155: 门禁注册表 → gates 表"""
    print("同步 #155: 门禁注册表 → gates...")
    data = load_yaml("_registry/catalogs/gate_registry.yaml")
    if not data:
        return

    gates = data.get("gates", [])
    # 顶层 source 字段（默认 .pre-commit-config.yaml，ARCH-009）
    registry_source = data.get("source", ".pre-commit-config.yaml")
    synced = 0
    for gate in gates:
        cur.execute(
            """
        INSERT INTO gates
        (gate_id, name, entry, description, files_trigger, always_run, category, status,
         source, event_driven, auto_start)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(gate_id) DO UPDATE SET
            name=excluded.name,
            entry=excluded.entry,
            description=excluded.description,
            files_trigger=excluded.files_trigger,
            always_run=excluded.always_run,
            category=excluded.category,
            status=excluded.status,
            source=excluded.source,
            event_driven=excluded.event_driven,
            auto_start=excluded.auto_start
        """,
            (
                gate.get("gate_id", ""),
                gate.get("name", ""),
                gate.get("entry", ""),
                gate.get("description", ""),
                gate.get("files_trigger", ""),
                1 if gate.get("always_run", False) else 0,
                gate.get("category", ""),
                gate.get("status", "active"),
                gate.get("source", registry_source),
                gate.get("event_driven", ""),
                1 if gate.get("auto_start", True) else 0,
            ),
        )
        synced += 1

    print(f"  同步 {synced}/{len(gates)} 个门禁")


def normalize_domain_id(domain_id: str) -> str:
    """归一化域ID: D-XXX → D_XXX (裁定#204 命名规范使用 D_ 下划线前缀)

    D-AUTONOMY-CORE → D_AUTONOMY_CORE
    D-INFRA-OPS    → D_INFRA_OPS
    D_AUTONOMY_CORE → D_AUTONOMY_CORE (无变化)
    """
    if not domain_id.startswith("D-"):
        return domain_id
    return "D_" + domain_id[2:].replace("-", "_")


def validate_domain_id_consistency(cur, entries):
    """校验 YAML 域ID与 DB 现有域ID的归一化一致性,防止连字符/下划线重复。

    检查: YAML 中的 domain_id 归一化后是否与 DB 现有 domain_id 不同但归一化相同。
    如果 YAML 用 D-AUTONOMY-CORE 而 DB 已有 D_AUTONOMY_CORE,会报警并跳过。
    """
    cur.execute("SELECT domain_id FROM domains")
    existing_ids = {row["domain_id"] for row in cur.fetchall()}

    issues = []
    for d in entries:
        yaml_id = d.get("domain", "")
        if not yaml_id.startswith("D-"):
            continue
        normalized = normalize_domain_id(yaml_id)
        # YAML 用连字符但 DB 已有下划线版本 → 会产生重复
        if normalized != yaml_id and normalized in existing_ids:
            issues.append((yaml_id, normalized))
        # DB 已有连字符版本但 YAML 改为下划线 → 需要清理 DB 旧连字符行
        # 仅当 yaml_id 中间有下划线时才检查(单词域如 D_GOVERNANCE 无连字符变体)
        if normalized == yaml_id and "_" in yaml_id[2:]:
            hyphen_variant = "D-" + yaml_id[2:].replace("_", "-")
            if hyphen_variant != yaml_id and hyphen_variant in existing_ids:
                issues.append((hyphen_variant, yaml_id))

    if issues:
        print("  [WARNING] 发现域ID归一化冲突,可能导致重复:")
        for yaml_id, db_id in issues:
            print(f"    YAML={yaml_id} vs DB={db_id} (归一化后相同)")
        print("  [ACTION] 跳过这些域的同步,请先清理 DB 中的冲突域")
        return issues
    return []


def sync_functional_domain_registry(cur):
    """#156: 功能域注册表 → domains + arch_path_mappings 表"""
    print("同步 #156: 功能域注册表 → domains + arch_path_mappings...")
    data = load_yaml("_registry/catalogs/functional_domain_registry.yaml")
    if not data:
        return

    entries = data.get("entries", [])

    # 校验: 检查 YAML 域ID与 DB 现有域ID的归一化一致性
    conflict_domains = validate_domain_id_consistency(cur, entries)
    conflict_set = {yaml_id for yaml_id, _ in conflict_domains}

    synced = 0
    deduped = 0
    seen_domains = set()
    from datetime import datetime

    now = datetime.now(UTC).isoformat()
    skipped = 0
    for d in entries:
        domain_id = d.get("domain", "")
        # 跳过有归一化冲突的域(防止产生重复)
        if domain_id in conflict_set:
            print(f"  SKIP: 跳过冲突域 '{domain_id}'——归一化后与 DB 现有域冲突,请先清理")
            skipped += 1
            continue
        # DM-100252: 跳过非规范域ID（既非 D_ 也非 D-），防止脏数据写入 domains 表
        # 裁定#204: 域命名规范为 D_XXX（下划线前缀）；历史 D-XXX 由 normalize_domain_id 归一化
        if not (domain_id.startswith("D_") or domain_id.startswith("D-")):
            print(f"  SKIP: 跳过非规范域ID '{domain_id}' (subdomain={d.get('subdomain', '')})——非 D_XXX 格式")
            skipped += 1
            continue
        # 治本（#ARCH-SSOT-GLOSSARY-MERGE-001）：跳过遗留图示用名域（stability=deprecated），
        # 防止废弃域污染 depgraph domains 表。遗留域中文名经 domain_name_mapping YAML fallback 查到。
        if d.get("stability") == "deprecated":
            print(f"  SKIP: 跳过遗留域 '{domain_id}' (stability=deprecated)——不 sync 到 depgraph")
            skipped += 1
            continue
        # DM-100252: domains 表去重——YAML 同一 domain_id 有多 subdomain entry，
        # domains 表以 domain_id 为主键，重复 INSERT 会 ON CONFLICT 覆盖（折叠为最后一条）。
        # 每个 domain_id 只 INSERT 首次出现的 entry；arch_path_mappings 仍同步所有 entry 的 ssot_path。
        if domain_id not in seen_domains:
            seen_domains.add(domain_id)
            ai_autonomy = d.get("ai_autonomy", "ai_modifiable")
            covers = d.get("covers", [])
            description = covers[0] if covers else ""
            # domain_group NOT NULL：YAML 无此字段，用 tier 或 'governance' 作为默认值
            domain_group = d.get("tier", "governance")
            if isinstance(domain_group, str) and domain_group.startswith("tier_"):
                domain_group = domain_group.replace("tier_", "").replace("_governance", "").replace("_", "")

            ssot_path = d.get("ssot_path", "")
            # 治本（2026-07-19）：domain_name 优先用 YAML 的 domain_name_zh（中文显示名），
            # 缺失时 fallback 到 subdomain（向后兼容旧 YAML）。
            # 历史问题：原用 subdomain 写入 domains.domain_name 导致 38 域为英文（如 "rule_enforcement"），
            # 与 25 个手工插入的中文域（如 "反馈检测器"）混合，导致 domain_index 显示不一致。
            # 修复后：YAML 的 domain_name_zh 升级为真源，DB 统一为中文。
            domain_name = d.get("domain_name_zh", "") or d.get("subdomain", "")
            cur.execute(
                """
        INSERT INTO domains (domain_id, domain_name, domain_group, description, ssot_path,
                             modification_permission, build_status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'planned', %s, %s)
        ON CONFLICT(domain_id) DO UPDATE SET
            domain_name=excluded.domain_name,
            description=excluded.description,
            ssot_path=excluded.ssot_path,
            modification_permission=excluded.modification_permission,
            updated_at=excluded.updated_at
        """,
                (domain_id, domain_name, domain_group, description, ssot_path or None, ai_autonomy, now, now),
            )
            synced += 1
        else:
            deduped += 1

        if ssot_path:
            # arch_path_mappings 需要 path_type NOT NULL 和 state NOT NULL
            cur.execute(
                """
            INSERT INTO arch_path_mappings
            (path_pattern, domain_id, path_type, state)
            VALUES (%s, %s, 'ssot', 'active')
            ON CONFLICT DO NOTHING
            """,
                (ssot_path, domain_id),
            )

    print(
        f"  同步 {synced} 个功能域（含 modification_permission 字段映射），跳过 {skipped} 个非规范域ID，去重 {deduped} 个重复域"
    )


def sync_vocabularies(cur):
    """#157: 词汇表 → field_vocabularies 表"""
    print("同步 #157: 词汇表 → field_vocabularies...")
    vocab_dir = os.path.join(RULES_DIR, "_registry/vocabularies")
    if not os.path.exists(vocab_dir):
        return

    synced = 0
    for yaml_file in Path(vocab_dir).glob("*.yaml"):
        data = load_yaml(f"_registry/vocabularies/{yaml_file.name}")
        field_name = data.get("vocabulary_name") or yaml_file.stem.removesuffix("_vocabulary")
        values = data.get("values", [])

        for value in values:
            if isinstance(value, dict):
                v = value.get("value", "")
                definition = value.get("definition", "")
            else:
                v = value
                definition = ""

            cur.execute(
                """
            INSERT INTO field_vocabularies
            (field_name, value, definition, source_yaml)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT(field_name, value) DO UPDATE SET
                definition=excluded.definition,
                source_yaml=excluded.source_yaml
            """,
                (field_name, v, definition, yaml_file.name),
            )
            synced += 1

    print(f"  同步 {synced} 个词汇值")


def sync_architecture_rules(cur):
    """#158: 架构规则 TRAE-013~017/036~038 → arch_constraints 表"""
    print("同步 #158: 架构规则 → arch_constraints...")
    rule_files = [
        "rules/trae_013_arch_cross_package_dep.yaml",
        "rules/trae_014_arch_blueprint_alignment.yaml",
        "rules/trae_015_arch_path_registration.yaml",
        "rules/trae_016_arch_drift_detection.yaml",
        "rules/trae_017_arch_governance_order.yaml",
        "rules/trae_036_arch_gate_transition.yaml",
        "rules/trae_037_arch_qualification_versioning.yaml",
        "rules/trae_038_arch_ctr_injection.yaml",
    ]

    synced = 0
    for rule_file in rule_files:
        data = load_yaml(rule_file)
        rules = data.get("rules", [])

        for rule in rules:
            rule_id = rule.get("rule_id", "")
            aliases = rule.get("aliases", [])
            name = aliases[0] if aliases else rule_id
            conditions = rule.get("conditions", [])

            cur.execute(
                """
            INSERT INTO arch_constraints
            (constraint_id, name, constraint_type, rule_definition, severity, enforcement)
            VALUES (%s, %s, 'architecture_rule', %s, %s, 'code')
            ON CONFLICT(constraint_id) DO UPDATE SET
                name=excluded.name,
                constraint_type=excluded.constraint_type,
                rule_definition=excluded.rule_definition,
                severity=excluded.severity,
                enforcement=excluded.enforcement
            """,
                (rule_id, name, name + ": " + str(conditions), rule.get("severity", "error")),
            )
            synced += 1

    print(f"  同步 {synced} 条架构规则")


# ========== P2 优先级同步 ==========


def sync_declarative_contract_tracker(cur):
    """#159: 声明式契约追踪 → contracts 表扩展"""
    print("同步 #159: 声明式契约追踪 → contracts...")
    data = load_yaml("_registry/catalogs/declarative_contract_tracker_registry.yaml")
    if not data:
        return

    contracts = data.get("contracts", [])
    synced = 0
    for contract in contracts:
        # FIX: source/actual_consumer 是文件路径，不是 domain_id，必须归一化防止FK违规
        contract_id = contract.get("contract_id", "")
        source = contract.get("source", "")
        actual_consumer = contract.get("actual_consumer", "")
        provider_domain = _path_to_domain(source)
        consumer_domain = _path_to_domain(actual_consumer)
        cur.execute(
            """
        INSERT INTO contracts
        (contract_id, name, provider_domain, consumer_domain, contract_type,
         promise, actual_consumer, fulfillment_status, gap, target_phase, last_reviewed)
        VALUES (%s, %s, %s, %s, 'declarative', %s, %s, %s, %s, %s, %s)
        ON CONFLICT(contract_id) DO UPDATE SET
            name=excluded.name,
            provider_domain=excluded.provider_domain,
            consumer_domain=excluded.consumer_domain,
            promise=excluded.promise,
            actual_consumer=excluded.actual_consumer,
            fulfillment_status=excluded.fulfillment_status,
            gap=excluded.gap,
            target_phase=excluded.target_phase,
            last_reviewed=excluded.last_reviewed
        """,
            (
                contract_id,
                source,
                provider_domain,
                consumer_domain,
                contract.get("promise", ""),
                actual_consumer,
                contract.get("status", "unresolved"),
                contract.get("gap", ""),
                contract.get("target_phase", ""),
                contract.get("last_reviewed", ""),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 条声明式契约")


def sync_frontmatter_field_registry(cur):
    """#160: Frontmatter 字段注册表 → field_vocabularies 表"""
    print("同步 #160: Frontmatter 字段注册表 → field_vocabularies...")
    data = load_yaml("_registry/catalogs/frontmatter_field_registry.yaml")
    if not data:
        return

    fields = data.get("fields", [])
    synced = 0
    for field in fields:
        field_name = field.get("field_name", "")
        enum_values = field.get("enum_values", [])

        # dynamic_from_ssot 标志：值集由词表单一维护，不写入 DB
        if isinstance(enum_values, str):
            continue

        for value in enum_values:
            # enum_values 元素可能是 dict {value: ..., description: ...} 或 str
            if isinstance(value, dict):
                v = value.get("value", "")
                definition = value.get("description", "")
            else:
                v = value
                definition = field.get("description", "")

            if not v:
                continue
            cur.execute(
                """
            INSERT INTO field_vocabularies
            (field_name, value, definition, source_yaml)
            VALUES (%s, %s, %s, 'frontmatter_field_registry.yaml')
            ON CONFLICT(field_name, value) DO UPDATE SET
                definition=excluded.definition,
                source_yaml=excluded.source_yaml
            """,
                (field_name, v, definition),
            )
            synced += 1

    print(f"  同步 {synced} 个字段枚举值")


def sync_registry_of_registries(cur):
    """#161: 注册表之注册表 → registries + cross_registry_rules 表"""
    print("同步 #161: 注册表之注册表 → registries + cross_registry_rules...")
    data = load_yaml("_registry/catalogs/registry_consistency_contract.yaml")
    if not data:
        return

    registries = data.get("registries", [])
    synced = 0
    for reg in registries:
        cur.execute(
            """
        INSERT INTO registries
        (registry_id, name, title, path, version, description, ssot_for)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(registry_id) DO UPDATE SET
            name=excluded.name,
            title=excluded.title,
            path=excluded.path,
            version=excluded.version,
            description=excluded.description,
            ssot_for=excluded.ssot_for
        """,
            (
                reg.get("id", ""),
                reg.get("name", ""),
                reg.get("title", ""),
                reg.get("path", ""),
                reg.get("version", ""),
                reg.get("description", ""),
                str(reg.get("ssot_for", [])),
            ),
        )
        synced += 1

    rules = data.get("cross_registry_rules", [])
    rules_synced = 0
    for rule in rules:
        cur.execute(
            """
        INSERT INTO cross_registry_rules
        (rule_id, title, fields, ssot, consistency, violation_action)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT(rule_id) DO UPDATE SET
            title=excluded.title,
            fields=excluded.fields,
            ssot=excluded.ssot,
            consistency=excluded.consistency,
            violation_action=excluded.violation_action
        """,
            (
                rule.get("rule_id", ""),
                rule.get("title", ""),
                str(rule.get("fields", [])),
                rule.get("ssot", ""),
                rule.get("consistency", "exact"),
                rule.get("violation_action", "warn"),
            ),
        )
        rules_synced += 1

    print(f"  同步 {synced} 个注册表 + {rules_synced} 条跨表规则")


def sync_directory_registry(cur):
    """#162: 目录注册表 → arch_directory_tree 表"""
    print("同步 #162: 目录注册表 → arch_directory_tree...")
    data = load_yaml("_registry/catalogs/directory_registry.yaml")
    if not data:
        return

    dirs = data.get("directories", [])
    synced = 0
    for d in dirs:
        cur.execute(
            """
        INSERT INTO arch_directory_tree
        (path, parent_path, path_type, domain_id, blueprint_id, design_maturity)
        VALUES (%s, %s, 'directory', %s, %s, 'design')
        ON CONFLICT(path) DO UPDATE SET
            parent_path=excluded.parent_path,
            domain_id=excluded.domain_id,
            blueprint_id=excluded.blueprint_id,
            design_maturity='design'
        WHERE arch_directory_tree.design_maturity = 'design'
        """,
            # 裁定#ARCH-target_layer_v1.0.0 v17修复：domain_id为空时用None（NULL），
            # 避免空字符串""触发fk_arch_dir_domain外键违规（NULL不被FK检查，空字符串被检查）
            # YAML用parent字段（非parent_path），一并兼容
            (
                d.get("path", ""),
                d.get("parent", d.get("parent_path", "")),
                d.get("domain_id") or None,
                d.get("module_id", ""),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 个目录（design_maturity='design'）")


def sync_rule_catalog_registry(cur):
    """#163: 规则路径目录 → arch_directory_tree 表（文档节点归属位置表）"""
    print("同步 #163: 规则路径目录 → arch_directory_tree（文档节点位置）...")
    data = load_yaml("_registry/catalogs/rule_catalog_registry.yaml")
    if not data:
        return

    rules = data.get("files", [])  # #ARCH-024 修复：catalog 顶层键是 files，不是 rules
    synced = 0
    for rule in rules:
        path = rule.get("path", "")
        if not path:
            continue

        cur.execute(
            """
        INSERT INTO arch_directory_tree
        (path, parent_path, path_type, domain_id, blueprint_id, design_maturity)
        VALUES (%s, %s, 'file', 'D_GOV_DOCS', %s, 'design')
        ON CONFLICT(path) DO UPDATE SET
            parent_path=excluded.parent_path,
            domain_id=excluded.domain_id,
            blueprint_id=excluded.blueprint_id,
            design_maturity='design'
        WHERE arch_directory_tree.design_maturity = 'design'
        """,
            (path, rule.get("parent_path", ""), rule.get("module_id", "")),
        )
        synced += 1

    print(f"  同步 {synced} 个文档节点到 arch_directory_tree（design_maturity='design'）")


# ========== P3 优先级同步 ==========


def sync_infrastructure_registry(cur):
    """#164: 基础设施注册表 → infrastructure_components 表"""
    print("同步 #164: 基础设施注册表 → infrastructure_components...")
    data = load_yaml("_registry/catalogs/infrastructure_registry.yaml")
    if not data:
        return

    # YAML 用 'infrastructure' 列表（不是 'components'）
    components = data.get("infrastructure", [])
    if not components:
        components = data.get("components", [])
    synced = 0
    for comp in components:
        if not isinstance(comp, dict):
            continue
        cur.execute(
            """
        INSERT INTO infrastructure_components
        (component_id, component_type, address, health_check, dependencies, sla, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(component_id) DO UPDATE SET
            component_type=excluded.component_type,
            address=excluded.address,
            health_check=excluded.health_check,
            dependencies=excluded.dependencies,
            sla=excluded.sla,
            status=excluded.status
        """,
            (
                comp.get("infra_id", comp.get("component_id", comp.get("type", ""))),
                comp.get("type", ""),
                comp.get("host", comp.get("address", "")) or "",
                comp.get("health_check", ""),
                str(comp.get("dependency_of", comp.get("dependencies", []))),
                comp.get("sla", ""),
                comp.get("status", "active"),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 个基础设施组件")


def sync_model_capability_contract(cur):
    """#164: 模型能力契约 → model_capabilities 表"""
    print("同步 #164: 模型能力契约 → model_capabilities...")
    data = load_yaml("_registry/contracts/model_capability_contract.yaml")
    if not data:
        return

    models = data.get("models", [])
    synced = 0
    for model in models:
        cur.execute(
            """
        INSERT INTO model_capabilities
        (model_name, tier, max_files_per_session, allowed_paths,
         forbidden_paths, recommended_tasks, forbidden_tasks)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(model_name) DO UPDATE SET
            tier=excluded.tier,
            max_files_per_session=excluded.max_files_per_session,
            allowed_paths=excluded.allowed_paths,
            forbidden_paths=excluded.forbidden_paths,
            recommended_tasks=excluded.recommended_tasks,
            forbidden_tasks=excluded.forbidden_tasks
        """,
            (
                model.get("name", ""),
                model.get("tier", "standard"),
                model.get("max_files_per_session", 0),
                str(model.get("allowed_paths", [])),
                str(model.get("forbidden_paths", [])),
                str(model.get("recommended_tasks", [])),
                str(model.get("forbidden_tasks", [])),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 个 AI 模型")


# ========== P4 优先级同步（V4.2 新增表） ==========


def sync_hard_boundaries(cur):
    """#170: 硬边界 → hard_boundaries 表"""
    print("同步 #170: 硬边界 → hard_boundaries...")
    data = load_yaml("_registry/catalogs/hard_boundaries_registry.yaml")
    if not data:
        print("  警告: hard_boundaries_registry.yaml 不存在，跳过（待创建 YAML 源）")
        return

    cur.execute("DELETE FROM hard_boundaries")

    boundaries = data.get("boundaries", [])
    synced = 0
    for b in boundaries:
        cur.execute(
            """
        INSERT INTO hard_boundaries
        (boundary_id, category, constraint_def, parameters, impact)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(boundary_id) DO UPDATE SET
            category=excluded.category,
            constraint_def=excluded.constraint_def,
            parameters=excluded.parameters,
            impact=excluded.impact
        """,
            (
                b.get("id", ""),
                b.get("category", ""),
                b.get("constraint", ""),
                str(b.get("parameters", {})),
                b.get("impact", ""),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 条硬边界")


def sync_business_streams(cur):
    """#171: 业务流定义 → business_streams 表"""
    print("同步 #171: 业务流定义 → business_streams...")
    data = load_yaml("_registry/catalogs/business_streams_registry.yaml")
    if not data:
        print("  警告: business_streams_registry.yaml 不存在，跳过（待创建 YAML 源）")
        return

    cur.execute("DELETE FROM business_streams")

    streams = data.get("streams", [])
    synced = 0
    for s in streams:
        cur.execute(
            """
        INSERT INTO business_streams
        (stream_id, name, goal, input, output, runtime_plane)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT(stream_id) DO UPDATE SET
            name=excluded.name,
            goal=excluded.goal,
            input=excluded.input,
            output=excluded.output,
            runtime_plane=excluded.runtime_plane
        """,
            (
                s.get("id", ""),
                s.get("name", ""),
                s.get("goal", ""),
                str(s.get("input", [])),
                str(s.get("output", [])),
                s.get("runtime_plane", "data_plane"),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 个业务流")


def sync_blueprint_links(cur):
    """#172: 蓝图→文件映射 → blueprint_links 表（从 nodes 表派生）"""
    print("同步 #172: 蓝图→文件映射 → blueprint_links...")
    cur.execute("DELETE FROM blueprint_links")

    # blueprint_path 字段可能为空，用 path 作为 blueprint_path 的回退
    cur.execute("""
    INSERT INTO blueprint_links (blueprint_id, blueprint_path, alignment_verified)
    SELECT blueprint_id, MIN(COALESCE(NULLIF(blueprint_path, ''), path)), 0
    FROM nodes
    WHERE blueprint_id IS NOT NULL AND blueprint_id != ''
    GROUP BY blueprint_id
    """)
    synced = cur.rowcount

    print(f"  同步 {synced} 条蓝图→文件映射")


def sync_domain_naming_rules(cur):
    """#173: 域命名规则 → domain_naming_rules 表（裁定#204 / OPS-2026062610 预防根因）

    SSoT: docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml
    建表 + 同步 5 条规则，apply_depgraph.py --insert-domain 建域时强制校验。
    """
    print("同步 #173: 域命名规则 → domain_naming_rules...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS domain_naming_rules (
        rule_id      TEXT PRIMARY KEY,
        rule_name    TEXT NOT NULL,
        rule_text    TEXT NOT NULL,
        applies_to   TEXT NOT NULL DEFAULT 'create',
        severity     TEXT NOT NULL DEFAULT 'error',
        example_bad  TEXT,
        example_good TEXT,
        created_at   TEXT NOT NULL,
        source_doc   TEXT
    )
    """)

    data = load_yaml("_registry/catalogs/domain_naming_rules.yaml")
    entries = data.get("entries", [])
    if not entries:
        print("  警告: domain_naming_rules.yaml 无 entries，跳过")
        return

    from datetime import datetime

    now = datetime.now(UTC).isoformat()
    synced = 0
    for e in entries:
        cur.execute(
            """
        INSERT INTO domain_naming_rules
            (rule_id, rule_name, rule_text, applies_to, severity,
             example_bad, example_good, created_at, source_doc)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(rule_id) DO UPDATE SET
            rule_name=excluded.rule_name,
            rule_text=excluded.rule_text,
            applies_to=excluded.applies_to,
            severity=excluded.severity,
            example_bad=excluded.example_bad,
            example_good=excluded.example_good,
            source_doc=excluded.source_doc
        """,
            (
                e["rule_id"],
                e["rule_name"],
                e["rule_text"],
                e.get("applies_to", "create"),
                e.get("severity", "error"),
                e.get("example_bad", ""),
                e.get("example_good", ""),
                now,
                e.get("source_doc", ""),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 条域命名规则（NR-001~NR-005）")


def sync_derived_identifier_registry(cur):
    """#174: 派生标识符关系 → derived_identifier_registry 表（裁定#206 B-5/B-6 + 裁定#207 R3-4）

    SSoT: docs/01_policies_and_standards/_registry/catalogs/derived_identifier_registry.yaml
    建表 + 同步派生标识符关系，apply_depgraph.py --propagate-rename 改名传播时依据本表。
    """
    print("同步 #174: 派生标识符关系 → derived_identifier_registry...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS derived_identifier_registry (
        derived_type        TEXT NOT NULL,
        source_field        TEXT NOT NULL,
        derived_field       TEXT NOT NULL,
        derivation_rule     TEXT NOT NULL,
        propagation_method  TEXT NOT NULL DEFAULT 'exact_value_map',
        source_doc          TEXT,
        PRIMARY KEY (derived_type, derived_field)
    )
    """)

    data = load_yaml("_registry/catalogs/derived_identifier_registry.yaml")
    entries = data.get("entries", [])
    if not entries:
        print("  警告: derived_identifier_registry.yaml 无 entries，跳过")
        return

    synced = 0
    for e in entries:
        cur.execute(
            """
        INSERT INTO derived_identifier_registry
            (derived_type, source_field, derived_field,
             derivation_rule, propagation_method, source_doc)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT(derived_type, derived_field) DO UPDATE SET
            source_field=excluded.source_field,
            derivation_rule=excluded.derivation_rule,
            propagation_method=excluded.propagation_method,
            source_doc=excluded.source_doc
        """,
            (
                e["derived_type"],
                e["source_field"],
                e["derived_field"],
                e["derivation_rule"],
                e.get("propagation_method", "exact_value_map"),
                e.get("source_doc", ""),
            ),
        )
        synced += 1

    print(f"  同步 {synced} 条派生标识符关系")


# ========== 历史遗留清理 ==========


def cleanup_legacy_fk_violations(cur):
    """清理 sync 后仍残留的 FK 违规 contracts 记录。

    这些记录不在任何 YAML 真源中（手动录入的 C-* 规则描述、旧 CTR-TRD-* 变体等），
    consumer_domain 为旧 '-CONTRACTS' 后缀变体（D_TRADING-CONTRACTS / D_SHARED-CONTRACTS），
    从未是有效 domain_id。sync 无法触及（不在 YAML 中），需一次性清理。
    """
    print("清理: 历史遗留 FK 违规 contracts 记录...")
    # 先统计
    cur.execute(
        """SELECT count(*) AS cnt FROM contracts
           WHERE consumer_domain LIKE %s
              OR consumer_domain LIKE %s""",
        ("%-CONTRACTS", "%-contracts"),
    )
    pre_count = cur.fetchone()["cnt"]
    if pre_count == 0:
        print("  无残留违规记录，跳过")
        return
    # 删除 consumer_domain 为旧 -CONTRACTS 后缀变体的孤立记录
    cur.execute(
        "DELETE FROM contracts WHERE consumer_domain LIKE %s",
        ("%-CONTRACTS",),
    )
    deleted = cur.rowcount
    print(f"  删除 {deleted} 条 '-CONTRACTS' 后缀孤立记录")


def verify_readonly_table_comments(cur):
    """S1.2: 验证 8 张 readonly 表 COMMENT 存在性 + 四要素完整性（HB-001 table_comment_required）。

    四要素（HB-001 table_comment_rule）：
    1. 表性质：包含 "YAML 真源只读缓存"
    2. 禁止操作：包含 "readonly 触发器"
    3. 真源路径：包含 "真源："
    4. 同步入口：包含 "同步入口"

    COMMENT 缺失或要素不全不影响数据正确性，只影响 AI 可发现性，因此仅告警不阻断。
    依据：hard_boundaries_registry.yaml HB-001 table_comment_required=true。
    AI 在 SQL 上下文中通过 \\d+ tablename 或 pg_description 视图发现表性质。
    """
    REQUIRED_ELEMENTS = [
        ("表性质", "YAML 真源只读缓存"),
        ("禁止操作", "readonly 触发器"),
        ("真源路径", "真源："),
        ("同步入口", "同步入口"),
    ]

    cur.execute(
        """
        SELECT c.relname, obj_description(c.oid) as comment
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = 'public' AND c.relkind = 'r'
        AND c.relname = ANY(%s)
    """,
        (READONLY_TABLES,),
    )
    rows = {row["relname"]: row["comment"] for row in cur.fetchall()}

    missing_comment = []
    incomplete = []

    for table in READONLY_TABLES:
        comment = rows.get(table)
        if not comment:
            missing_comment.append(table)
            continue
        missing_elements = [name for name, keyword in REQUIRED_ELEMENTS if keyword not in comment]
        if missing_elements:
            incomplete.append((table, missing_elements))

    if missing_comment:
        print("\n[WARN] S1.2 HB-001 以下 readonly 表缺少 COMMENT（AI 可发现性受损）：")
        for t in missing_comment:
            print(f"  - {t}（需执行 COMMENT ON TABLE {t} IS '...'，见 02_create_pg_schema.sql 末尾）")

    if incomplete:
        print("\n[WARN] S1.2 HB-001 以下 readonly 表 COMMENT 缺少四要素：")
        for table, missing in incomplete:
            print(f"  - {table} 缺少：{', '.join(missing)}")

    if not missing_comment and not incomplete:
        print(f"\n[OK] S1.2 HB-001: {len(READONLY_TABLES)} 张 readonly 表 COMMENT 齐全且四要素完整")


# ========== dataflowgraph 同步（ARCH-051） ==========


def sync_dataflow_registry(cur):
    """#175: dataflowgraph 数据流图注册表 → dataflow_datasets/jobs/edges 表（ARCH-051）

    SSoT: docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml
    ARCH-051 裁定建立，治本"跨层数据流无中央真源"的病根。
    与 depgraph 同库不同表（表名前缀 dataflow_*），共享连接配置。

    同步内容：
    - jobs → dataflow_jobs（13个核心数据变换作业）
    - datasets → dataflow_datasets（14个核心数据集）
    - edges → dataflow_edges（由 produced_by_job/consumed_by_jobs 派生：push/pull）
    """
    # 显式 import dataflowgraph_schema（声明依赖关系，满足 ORPHAN-MODULE 门禁）
    from zephyr.governance.persistence.dataflowgraph_schema import _DATAFLOW_CORE_TABLES  # noqa: F401

    print("同步 #175: dataflowgraph 数据流图 → dataflow_datasets/jobs/edges...")
    data = load_yaml("_registry/catalogs/dataflow_graph_registry.yaml")
    if not data:
        print("  跳过: dataflow_graph_registry.yaml 不存在或为空")
        return

    from datetime import UTC, datetime

    now_iso = datetime.now(UTC).isoformat(timespec="seconds")

    # --- 清空运营态数据（DELETE + UPSERT 模式，保护设计态）---
    # ARCH-052: 与 generate_project_depgraph.py 对齐——保护 design_maturity='design' 的设计态数据
    # apply_dataflowgraph.py --add-design-* 写入的数据（design_maturity='design', build_status='planned'）
    # 不得被常规 sync 清空。NULL != 'design' 为 NULL（非 TRUE），需显式处理。
    # 先 edges（FK 逻辑依赖），再 datasets/jobs
    #
    # Ruling:100PCT-AI-GOVERNANCE P0-5 (2026-07-19) 治本：
    # 原 DELETE 谓词 `design_maturity != 'design'` 会误删非 design 占位记录。
    # 治本：谓词从"排除 design"改为"只删 production"，保护 design。
    # ARCH-MM-002：design_maturity 由 3 态（design/prototype/production）收敛为 2 态
    # （design/production），prototype 已移除；此谓词天然保护 design。
    # 配套 P0-4：protect_dataflow_design_maturity 触发器双重防御（谓词层 + 触发器层），
    # 即使谓词漏判，触发器仍阻断。
    #
    # TRAE-082 数据流设计态治本（2026-07-31）：
    # jobs/datasets 改用 UPSERT（ON CONFLICT DO UPDATE）——design 记录不被 DELETE，
    # 但通过 UPSERT 幂等更新（YAML 是 SSoT，design 记录同时存在于 YAML 和 DB）。
    # edges 无唯一约束且受 ARCH-053 触发器保护（禁止 DELETE design 态），
    # 故只 DELETE production edges，INSERT 时用 WHERE NOT EXISTS 避免重复。
    cur.execute("DELETE FROM dataflow_edges WHERE design_maturity IS NULL OR design_maturity = 'production'")  # noqa: bare-sql  治理DBA脚本存量清理语句，format重排伪新增（§5.160.2集中化专项另列）
    cur.execute("DELETE FROM dataflow_datasets WHERE design_maturity IS NULL OR design_maturity = 'production'")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
    cur.execute("DELETE FROM dataflow_jobs WHERE design_maturity IS NULL OR design_maturity = 'production'")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）

    # --- 同步 jobs（先 jobs，因为 datasets 的 produced_by_job 引用 job_name）---
    jobs = data.get("jobs", [])
    job_name_to_id: dict[str, int] = {}  # job_name -> PG job_id（保留）
    job_yaml_id_to_pg_id: dict[str, int] = {}  # YAML job_id(JOB-NNN) -> PG job_id（用于派生 edges）
    job_yaml_id_to_design: dict[str, str] = {}  # YAML job_id -> design_maturity（用于派生 edges）
    synced_jobs = 0
    for j in jobs:
        job_name = j.get("job_name", "")
        if not job_name:
            continue
        j_design = j.get("design_maturity", "production")
        j_build = "planned" if j_design == "design" else "generated"
        cur.execute(
            """
            INSERT INTO dataflow_jobs
                (job_name, entity_type, scope, source_code_ref, trigger_type,
                 run_context, pit_relevance, description, design_maturity,
                 build_status, module_id, last_updated)
            VALUES (%s, 'job', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_name) DO UPDATE SET
                scope = EXCLUDED.scope,
                source_code_ref = EXCLUDED.source_code_ref,
                trigger_type = EXCLUDED.trigger_type,
                run_context = EXCLUDED.run_context,
                pit_relevance = EXCLUDED.pit_relevance,
                description = EXCLUDED.description,
                design_maturity = EXCLUDED.design_maturity,
                build_status = EXCLUDED.build_status,
                module_id = EXCLUDED.module_id,
                last_updated = EXCLUDED.last_updated
            RETURNING job_id
        """,
            (
                job_name,
                j.get("scope", "production"),
                j.get("source_code_ref"),
                j.get("trigger_type"),
                j.get("run_context"),
                j.get("pit_relevance", "strict"),
                j.get("description"),
                j_design,
                j_build,
                j.get("module_id") or None,
                now_iso,
            ),
        )
        job_id = cur.fetchone()["job_id"]
        job_name_to_id[job_name] = job_id
        job_yaml_id_to_pg_id[j.get("job_id", "")] = job_id
        job_yaml_id_to_design[j.get("job_id", "")] = j_design
        synced_jobs += 1

    # --- 同步 datasets ---
    datasets = data.get("datasets", [])
    dataset_name_to_id: dict[str, int] = {}  # entity_name -> dataset_id（用于派生 edges）
    dataset_name_to_design: dict[str, str] = {}  # entity_name -> design_maturity（用于派生 edges）
    synced_datasets = 0
    for d in datasets:
        entity_name = d.get("entity_name", "")
        if not entity_name:
            continue
        d_design = d.get("design_maturity", "production")
        d_build = "planned" if d_design == "design" else "generated"
        cur.execute(
            """
            INSERT INTO dataflow_datasets
                (entity_name, entity_type, scope, contract_ref, physical_type,
                 produced_by_job, domain_id, design_maturity, build_status,
                 pit_policy, format_summary, valid_since, module_id, last_updated)
            VALUES (%s, 'dataset', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (entity_name) DO UPDATE SET
                scope = EXCLUDED.scope,
                contract_ref = EXCLUDED.contract_ref,
                physical_type = EXCLUDED.physical_type,
                produced_by_job = EXCLUDED.produced_by_job,
                domain_id = EXCLUDED.domain_id,
                design_maturity = EXCLUDED.design_maturity,
                build_status = EXCLUDED.build_status,
                pit_policy = EXCLUDED.pit_policy,
                format_summary = EXCLUDED.format_summary,
                valid_since = EXCLUDED.valid_since,
                module_id = EXCLUDED.module_id,
                last_updated = EXCLUDED.last_updated
            RETURNING dataset_id
        """,
            (
                entity_name,
                d.get("scope", "production"),
                d.get("contract_ref"),
                d.get("physical_type"),
                d.get("produced_by_job"),
                d.get("domain_id"),
                d_design,
                d_build,
                d.get("pit_policy", "strict"),
                d.get("format_summary"),
                d.get("valid_since"),
                d.get("module_id") or None,
                now_iso,
            ),
        )
        dataset_id = cur.fetchone()["dataset_id"]
        dataset_name_to_id[entity_name] = dataset_id
        dataset_name_to_design[entity_name] = d_design
        synced_datasets += 1

    # --- 派生 edges ---
    # YAML 的 produced_by_job / consumed_by_jobs 字段使用 JOB-NNN 格式（YAML job_id），
    # 不是 job_name（如 ingest.minqmt_kline），故用 job_yaml_id_to_pg_id 映射查 PG job_id。
    # 1. Job→Dataset 产出（produced_by_job）→ edge_type=push
    synced_edges = 0
    for d in datasets:
        entity_name = d.get("entity_name", "")
        produced_by = d.get("produced_by_job")
        if entity_name in dataset_name_to_id and produced_by in job_yaml_id_to_pg_id:
            edge_design = job_yaml_id_to_design.get(produced_by, "production")
            cur.execute(
                """
                INSERT INTO dataflow_edges
                    (from_entity_id, to_entity_id, from_entity_type, to_entity_type, edge_type, design_maturity, last_updated)
                SELECT %s, %s, 'job', 'dataset', 'push', %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM dataflow_edges
                    WHERE from_entity_id = %s AND to_entity_id = %s AND edge_type = 'push'
                )
            """,
                (
                    job_yaml_id_to_pg_id[produced_by],
                    dataset_name_to_id[entity_name],
                    edge_design,
                    now_iso,
                    job_yaml_id_to_pg_id[produced_by],
                    dataset_name_to_id[entity_name],
                ),
            )
            synced_edges += 1

    # 2. Dataset→Job 消费（consumed_by_jobs）→ edge_type=pull
    for d in datasets:
        entity_name = d.get("entity_name", "")
        consumed_by = d.get("consumed_by_jobs", []) or []
        if entity_name in dataset_name_to_id:
            edge_design = dataset_name_to_design.get(entity_name, "production")
            for consumed_job_yaml_id in consumed_by:
                if consumed_job_yaml_id in job_yaml_id_to_pg_id:
                    cur.execute(
                        """
                        INSERT INTO dataflow_edges
                            (from_entity_id, to_entity_id, from_entity_type, to_entity_type, edge_type, design_maturity, last_updated)
                        SELECT %s, %s, 'dataset', 'job', 'pull', %s, %s
                        WHERE NOT EXISTS (
                            SELECT 1 FROM dataflow_edges
                            WHERE from_entity_id = %s AND to_entity_id = %s AND edge_type = 'pull'
                        )
                    """,
                        (
                            dataset_name_to_id[entity_name],
                            job_yaml_id_to_pg_id[consumed_job_yaml_id],
                            edge_design,
                            now_iso,
                            dataset_name_to_id[entity_name],
                            job_yaml_id_to_pg_id[consumed_job_yaml_id],
                        ),
                    )
                    synced_edges += 1

    print(f"  同步 {synced_jobs} 个 Job, {synced_datasets} 个 Dataset, {synced_edges} 条 edges")


# ========== 聚合节点同步（ARCH-052） ==========


# ARCH-052: owner_module → domain_id 映射
# 聚合节点的 registry.yaml 用 owner_module 字段标识归属蓝图，
# 但 nodes 表需要 domain_id（FK 到 domains 表），此处显式映射。
_AGGREGATE_OWNER_TO_DOMAIN = {
    "MOD-GATE_ENGINE": "D_GOV_ENFORCEMENT",
    "MOD-GOV_SCRIPTS": "D_GOV_SCRIPTS",
    "MOD-AUDIT-TEST": "D_AUDITTEST",
    "MOD-GOVERNANCE": "D_GOVERNANCE",
}

# ARCH-052: 聚合节点 registry.yaml 列表（SSoT 真源）
# 每个文件描述一类配置对象集（门禁/脚本/测试/规则），用 1 个聚合节点代表。
# 路径相对于 RULES_DIR（docs/01_policies_and_standards/）。
_AGGREGATE_REGISTRY_FILES = [
    "_registry/catalogs/rule_enforcement_registry.yaml",
    "_registry/catalogs/scripts_registry.yaml",
    "_registry/catalogs/test_suite_registry.yaml",
    "_registry/catalogs/rule_registry_collection.yaml",
]


def sync_aggregate_nodes(cur):
    """#176 ARCH-052: 聚合节点 registry.yaml → nodes 表

    SSoT: 4 个 registry.yaml 文件（_AGGREGATE_REGISTRY_FILES）
    ARCH-052 裁定：门禁/脚本/测试/规则文件不再作为独立 depgraph 节点，
    用 1 个聚合节点代表一组配置对象。本函数将这 4 个聚合节点 UPSERT 到 nodes 表。

    为什么需要本函数：
      - generate_project_depgraph.py 重建时已排除聚合节点类型（不被 DELETE）
      - 但若 DB 被意外清空（如人工操作/并发会话误删），需要从 YAML 恢复
      - 本函数提供"YAML→DB 单向恢复"通道，与 sync_gate_registry 等保持一致模式

    幂等性：
      - nodes 表无 blueprint_id 唯一约束，使用 SELECT-then-UPDATE/INSERT 模式
      - 已存在的聚合节点（按 blueprint_id+node_type 匹配）UPDATE，否则 INSERT
      - 不用 DELETE+INSERT 模式，避免破坏 edges 表中指向聚合节点的边
    """
    print("同步 #176 ARCH-052: 聚合节点 registry.yaml → nodes...")
    synced = 0
    skipped = 0
    for rel_path in _AGGREGATE_REGISTRY_FILES:
        data = load_yaml(rel_path)
        if not data:
            print(f"  跳过: {rel_path} 不存在或为空")
            skipped += 1
            continue

        module_id = data.get("module_id", "")
        node_type = data.get("node_type", "")
        collection_name = data.get("collection_name", "")
        owner_module = data.get("owner_module", "")
        total_registered = data.get("total_registered", 0)

        if not module_id or not node_type:
            print(f"  跳过: {rel_path} 缺少 module_id 或 node_type")
            skipped += 1
            continue

        domain_id = _AGGREGATE_OWNER_TO_DOMAIN.get(owner_module)
        if not domain_id:
            print(f"  跳过: {rel_path} 的 owner_module={owner_module} 未在 _AGGREGATE_OWNER_TO_DOMAIN 登记映射")
            skipped += 1
            continue

        # path 指向 registry.yaml（SSoT 指针），用 repo-relative 路径
        # RULES_DIR = docs/01_policies_and_standards/，rel_path 相对它
        node_path = f"docs/01_policies_and_standards/{rel_path}"
        # node_name 对齐域文档渲染格式："<中文名> — ARCH-052 聚合节点 production"
        node_name = f"{collection_name} — ARCH-052 聚合节点 production"

        # 查询是否已存在（按 blueprint_id + node_type 匹配，避免误伤同名节点）
        cur.execute(
            "SELECT node_id FROM nodes WHERE blueprint_id = %s AND node_type = %s LIMIT 1",
            (module_id, node_type),
        )
        existing = cur.fetchone()

        if existing:
            # UPDATE 已有聚合节点
            # 2026-08-28 B-007 治本：机械通道不降级人工 lifecycle 态（承 P0 STATUS-PRESERVE 不变量）
            # ——UPDATE 剔除 build_status 回写（保留现值），INSERT 仍落 'stable'
            cur.execute(
                """
                UPDATE nodes SET
                    path = %s,
                    node_name = %s,
                    domain_id = %s,
                    design_maturity = 'production',
                    architecture_layer = 'L1_foundation',
                    granularity = 'aggregated',
                    tags = 'ARCH-052,aggregate_node',
                    blueprint_id_invalid = 1
                WHERE node_id = %s
                """,
                (node_path, node_name, domain_id, existing["node_id"]),
            )
        else:
            # INSERT 新聚合节点（node_id 自增）
            # blueprint_id_invalid=1: CFG-* 前缀不符合裁定#208 三轨制（MOD-/D-/SH-），
            # 但 CFG- 是聚合节点 registry 的语义前缀（Configuration），用此 escape hatch
            cur.execute(
                """
                INSERT INTO nodes (
                    blueprint_id, node_type, path, node_name, domain_id,
                    design_maturity, build_status, architecture_layer,
                    granularity, tags, blueprint_id_invalid
                ) VALUES (%s, %s, %s, %s, %s, 'production', 'stable',
                          'L1_foundation', 'aggregated', 'ARCH-052,aggregate_node', 1)
                """,
                (module_id, node_type, node_path, node_name, domain_id),
            )
        synced += 1
        print(f"  UPSERT 聚合节点: {module_id} ({node_type}) → {domain_id}, items={total_registered}")

    print(f"  同步 {synced} 个聚合节点，跳过 {skipped} 个")


# ========== 接口契约同步（ARCH-053） ==========


def sync_interface_contracts(cur):
    """#177 ARCH-053: 接口契约注册表 → interface_contracts 表

    SSoT: docs/01_policies_and_standards/_registry/catalogs/interface_contract_registry.yaml
    ARCH-053 裁定：补齐 API 契约层，对标 Backstage API kind。
    与 cross_module_dependency 互补：本表回答"怎么依赖"，后者回答"是否依赖"。

    同步内容：
    - interfaces → interface_contracts 表（接口集级粒度，一个模块一组接口）
    """
    print("同步 #177 ARCH-053: 接口契约注册表 → interface_contracts...")
    data = load_yaml("_registry/catalogs/interface_contract_registry.yaml")
    if not data:
        print("  跳过: interface_contract_registry.yaml 不存在或为空")
        return

    from datetime import UTC, datetime

    now_iso = datetime.now(UTC).isoformat(timespec="seconds")

    # 建表（幂等，与 sync_dataflow_registry 模式一致）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interface_contracts (
            interface_id   TEXT PRIMARY KEY,
            module_id      TEXT NOT NULL,
            api_name       TEXT,
            api_type       TEXT,
            description    TEXT,
            exposed_interfaces TEXT,
            consumed_by_modules TEXT,
            contract_version TEXT,
            stability      TEXT,
            last_updated   TEXT
        )
    """)
    # P6 修复：加 COMMENT（HB-001 四要素：表名+用途+真源+同步方向）
    cur.execute(
        "COMMENT ON TABLE interface_contracts IS 'ARCH-053 接口契约表 | 用途: 模块API契约(接口集级) | 真源: interface_contract_registry.yaml | 同步: YAML→DB单向'"
    )

    interfaces = data.get("interfaces", [])
    synced = 0
    for iface in interfaces:
        interface_id = iface.get("interface_id", "")
        if not interface_id:
            continue
        cur.execute(
            """
            INSERT INTO interface_contracts
                (interface_id, module_id, api_name, api_type, description,
                 exposed_interfaces, consumed_by_modules, contract_version,
                 stability, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT(interface_id) DO UPDATE SET
                module_id=excluded.module_id,
                api_name=excluded.api_name,
                api_type=excluded.api_type,
                description=excluded.description,
                exposed_interfaces=excluded.exposed_interfaces,
                consumed_by_modules=excluded.consumed_by_modules,
                contract_version=excluded.contract_version,
                stability=excluded.stability,
                last_updated=excluded.last_updated
        """,
            (
                interface_id,
                iface.get("module_id", ""),
                iface.get("api_name", ""),
                iface.get("api_type", ""),
                iface.get("description", ""),
                str(iface.get("exposed_interfaces", [])),
                str(iface.get("consumed_by_modules", [])),
                iface.get("contract_version", ""),
                iface.get("stability", "evolving"),
                now_iso,
            ),
        )
        synced += 1

    print(f"  同步 {synced} 个接口契约")


# ========== Database 节点同步（ARCH-053） ==========


# ARCH-053: infrastructure_registry 中 type 含数据库的条目 → nodes 表
_DATABASE_INFRA_TYPES = {"relational_db", "vector_db"}


def sync_database_nodes(cur):
    """#178 ARCH-053: infrastructure_registry 的数据库条目 → nodes 表（node_type='database'）

    SSoT: docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml
    ARCH-053 裁定：补齐 database 节点到 depgraph，使模块→数据库依赖在依赖图中可视化。

    根因：sync_infrastructure_registry 只写到 infrastructure_components 表，
    未写到 nodes 表。generate_project_depgraph.py 的 DELETE 已排除 node_type='database'，
    但无人创建——这是设计遗漏。本函数补齐。

    真源：infrastructure_registry.yaml（不新建 database_registry.yaml，避免第二真源）
    """
    print("同步 #178 ARCH-053: infrastructure_registry 数据库条目 → nodes...")
    data = load_yaml("_registry/catalogs/infrastructure_registry.yaml")
    if not data:
        print("  跳过: infrastructure_registry.yaml 不存在或为空")
        return

    infra_list = data.get("infrastructure", [])
    synced = 0
    for comp in infra_list:
        if not isinstance(comp, dict):
            continue
        comp_type = comp.get("type", "")
        if comp_type not in _DATABASE_INFRA_TYPES:
            continue

        infra_id = comp.get("infra_id", "")
        name = comp.get("name", "")
        if not infra_id or not name:
            continue

        # 构造 nodes 表字段
        # 治本（2026-08-03）：blueprint_id 不再用 infra_id——infra_id 是基础设施资源目录 ID
        # （INFRA-{TYPE}-{NNN}），不是 module_id（裁定#208 仅接受 MOD-/SH- 前缀）。
        # 旧代码误将 infra_id 存为 blueprint_id 并标 blueprint_id_invalid=1，导致合规扫描
        # 持续报 4 个 BAD。现在 blueprint_id 设 NULL（path 是稳定 PK，裁定#209 Stage 2，
        # 足以唯一标识节点），infra_id 仅保留在 YAML 真源 + path 锚点中。
        # path 指向 infrastructure_registry.yaml（SSoT 指针）
        # 每个 database 节点加 #infra_id 锚点区分，避免 idx_nodes_path 唯一约束冲突
        # （infrastructure_registry.yaml 含多个 database 条目，共用同一 path 会违反唯一约束）
        node_path = f"docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#{infra_id}"
        node_name = f"{name} — database 节点 (ARCH-053)"

        # domain_id 用 D_INFRA_RUNTIME（运行时基础设施域，与 registry_adapter.py 一致）
        # 修复 ARCH-053 FK 违反：D_INFRA 不存在于 domains 表，nodes_domain_id_fkey 阻断
        domain_id = "D_INFRA_RUNTIME"

        # 查询是否已存在（按 path + node_type='database' 匹配，path 是稳定 PK 裁定#209）
        cur.execute(
            "SELECT node_id FROM nodes WHERE path = %s AND node_type = 'database' LIMIT 1",
            (node_path,),
        )
        existing = cur.fetchone()

        if existing:
            # 2026-08-28 B-007 治本：机械通道不降级人工 lifecycle 态（承 P0 STATUS-PRESERVE 不变量）
            # ——UPDATE 剔除 build_status 回写（保留现值），INSERT 仍落 'stable'
            cur.execute(
                """
                UPDATE nodes SET
                    blueprint_id = NULL,
                    path = %s,
                    node_name = %s,
                    domain_id = %s,
                    design_maturity = 'production',
                    architecture_layer = 'L1_foundation',
                    granularity = 'aggregated',
                    tags = 'ARCH-053,database_node',
                    blueprint_id_invalid = 0
                WHERE node_id = %s
                """,
                (node_path, node_name, domain_id, existing["node_id"]),
            )
        else:
            cur.execute(
                """
                INSERT INTO nodes (
                    blueprint_id, node_type, path, node_name, domain_id,
                    design_maturity, build_status, architecture_layer,
                    granularity, tags, blueprint_id_invalid
                ) VALUES (NULL, 'database', %s, %s, %s, 'production', 'stable',
                          'L1_foundation', 'aggregated', 'ARCH-053,database_node', 0)
                """,
                (node_path, node_name, domain_id),
            )
        synced += 1
        print(f"  UPSERT database 节点: {infra_id} ({comp_type}) — {name}")

    print(f"  同步 {synced} 个 database 节点")


def sync_data_source_apis(cur):
    """#179: 数据源 API 结构化清单 → data_source_apis 表

    SSoT: architecture_model/data/data_source_apis_registry.yaml
    将 124 个数据源 API 从 YAML 同步到 depgraph.data_source_apis 表。
    data_source_operation_manual.md 的 API 总览表格已替换为指针，派生关系：
    YAML → DB → generate_asset_catalog.py → asset_catalog.md §7。
    """
    print("同步 #179: 数据源 API 清单 → data_source_apis...")
    yaml_path = REPO_ROOT / "architecture_model" / "data" / "data_source_apis_registry.yaml"
    if not yaml_path.exists():
        print(f"  跳过: {yaml_path} 不存在")
        return
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    apis = data.get("apis", [])
    if not apis:
        print("  跳过: YAML 中无 apis 条目")
        return
    cur.execute("DELETE FROM data_source_apis")
    synced = 0
    for a in apis:
        cur.execute(
            """
            INSERT INTO data_source_apis
                (api_id, source_id, category, api_name, short_name,
                 function_desc, params, returns_format, frequency_codes,
                 data_scope, test_status, test_result, section_ref, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                a.get("api_id", ""),
                a.get("source_id", ""),
                a.get("category", ""),
                a.get("api_name", ""),
                a.get("short_name", ""),
                a.get("function_desc", ""),
                a.get("params", ""),
                a.get("returns_format", ""),
                a.get("frequency_codes", ""),
                a.get("data_scope", ""),
                a.get("test_status", "untested"),
                a.get("test_result", ""),
                a.get("section_ref", ""),
                a.get("notes", ""),
            ),
        )
        synced += 1
    print(f"  同步 {synced} 个数据源 API")


def sync_data_source_assets(cur):
    """#180: 外部数据源资产清单 → data_source_assets 表

    SSoT: architecture_model/data/data_sources_registry.yaml
    将外部数据源资产（v2.1.0 起 12 个；account_type + policy 字段同步到 DB）
    从 YAML 同步到 depgraph.data_source_assets 表。
    派生关系：YAML → DB → generate_asset_catalog.py → asset_catalog.md。
    v2.1.0: 新增 account_type + policy(JSONB) 同步，AI 可直接查 DB 获取配额/策略。
    """
    print("同步 #180: 外部数据源资产 → data_source_assets...")
    yaml_path = REPO_ROOT / "architecture_model" / "data" / "data_sources_registry.yaml"
    if not yaml_path.exists():
        print(f"  跳过: {yaml_path} 不存在")
        return
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    sources = data.get("data_sources", [])
    if not sources:
        print("  跳过: YAML 中无 data_sources 条目")
        return
    cur.execute("DELETE FROM data_source_assets")
    synced = 0
    for s in sources:
        cur.execute(
            """
            INSERT INTO data_source_assets
                (source_id, name, name_en, type, account_type, category, vendor,
                 interface_types, api_count, auth_required, auth_method,
                 rate_limit, status, coverage, limitations, owner, operation_manual, policy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        """,
            (
                s.get("id", ""),
                s.get("name", ""),
                s.get("name_en", ""),
                s.get("type", ""),
                s.get("account_type", ""),
                s.get("category", ""),
                s.get("vendor", ""),
                ", ".join(s.get("interface_types", []))
                if isinstance(s.get("interface_types"), list)
                else s.get("interface_types", ""),
                s.get("api_count", 0),
                s.get("auth_required", False),
                s.get("auth_method", ""),
                s.get("rate_limit", ""),
                s.get("status", ""),
                s.get("coverage", ""),
                s.get("limitations", ""),
                s.get("owner", ""),
                s.get("operation_manual", ""),
                json.dumps(s.get("policy", {}), ensure_ascii=False),
            ),
        )
        synced += 1
    print(f"  同步 {synced} 个外部数据源资产")


def sync_service_assets(cur):
    """#181: 服务资产清单 → service_assets 表

    SSoT: architecture_model/runtime/service_registry.yaml
    将服务资产从 YAML 同步到 depgraph.service_assets 表。
    派生关系：YAML → DB → generate_asset_catalog.py → asset_catalog.md。
    """
    print("同步 #181: 服务资产 → service_assets...")
    yaml_path = REPO_ROOT / "architecture_model" / "runtime" / "service_registry.yaml"
    if not yaml_path.exists():
        print(f"  跳过: {yaml_path} 不存在")
        return
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    services = data.get("services", [])
    if not services:
        print("  跳过: YAML 中无 services 条目")
        return
    cur.execute("DELETE FROM service_assets")
    synced = 0
    for s in services:
        cur.execute(
            """
            INSERT INTO service_assets
                (service_id, name, type, component_ref, domain,
                 port, host, protocol, status, description, owner)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                s.get("id", ""),
                s.get("name", ""),
                s.get("type", ""),
                s.get("component_ref"),
                s.get("domain", ""),
                s.get("port"),
                s.get("host", ""),
                s.get("protocol", ""),
                s.get("status", ""),
                s.get("description", ""),
                s.get("owner", ""),
            ),
        )
        synced += 1
    print(f"  同步 {synced} 个服务资产")


def sync_config_assets(cur):
    """#182: 配置项资产 → config_assets 表（文件系统扫描派生）

    真源：config/*.yaml 文件本身（文件系统，非单一 YAML）
    扫描 config/ 目录下所有 .yaml 文件，写入 file_path/file_name/size_bytes/last_modified。
    非 readonly 表（文件系统扫描派生，需定期重扫）。
    """
    print("同步 #182: 配置项资产 → config_assets（文件系统扫描）...")
    config_dir = REPO_ROOT / "config"
    if not config_dir.exists():
        print(f"  跳过: {config_dir} 不存在")
        return
    yaml_files = sorted(config_dir.glob("*.yaml"))
    if not yaml_files:
        print("  跳过: config/ 下无 .yaml 文件")
        return
    cur.execute("DELETE FROM config_assets")
    synced = 0
    for f in yaml_files:
        stat = f.stat()
        rel_path = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
        cur.execute(
            """
            INSERT INTO config_assets
                (file_path, file_name, category, size_bytes, owner, last_modified)
            VALUES (%s, %s, %s, %s, %s, to_timestamp(%s))
        """,
            (
                rel_path,
                f.name,
                "config",
                stat.st_size,
                "ZephyrAlpha-Owner",
                stat.st_mtime,
            ),
        )
        synced += 1
    print(f"  同步 {synced} 个配置文件")


def sync_rule_ai_perception_index(cur):
    """#183: 规则AI感知索引 → rule_ai_perception 表（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）

    真源：_registry/catalogs/rule_ai_perception_index.yaml（由 generate_rule_ai_perception_index.py 生成）
    消费方：discover_applicable_rules MCP 工具（Phase 3.2b）、M17 指标。
    """
    print("同步 #183: 规则AI感知索引 → rule_ai_perception...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rule_ai_perception (
        rule_id         TEXT PRIMARY KEY,
        title           TEXT NOT NULL DEFAULT '',
        module_id       TEXT NOT NULL DEFAULT '',
        scope           TEXT NOT NULL DEFAULT '',
        domain          TEXT NOT NULL DEFAULT '',
        severity        TEXT NOT NULL DEFAULT '',
        stability       TEXT NOT NULL DEFAULT '',
        ai_autonomy     TEXT NOT NULL DEFAULT '',
        safety_level    TEXT NOT NULL DEFAULT '',
        operations      TEXT[] NOT NULL DEFAULT '{}',
        gate_ids        TEXT[] NOT NULL DEFAULT '{}',
        tags            TEXT[] NOT NULL DEFAULT '{}',
        aliases         TEXT[] NOT NULL DEFAULT '{}',
        paired_gate_id  TEXT,
        rule_file       TEXT NOT NULL DEFAULT ''
    )
    """)
    cur.execute(
        "COMMENT ON TABLE rule_ai_perception IS '规则AI感知索引（#183，#ARCH-GOV-CONVERGENCE-META Phase 3.2a）— 表性质: YAML 真源只读缓存 | 禁止操作: readonly 触发器保护，禁止直接 INSERT/UPDATE/DELETE | 真源：docs/01_policies_and_standards/_registry/catalogs/rule_ai_perception_index.yaml | 同步入口: scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py sync_rule_ai_perception_index()'"
    )

    data = load_yaml("_registry/catalogs/rule_ai_perception_index.yaml")
    rules = data.get("rules", [])
    if not rules:
        print("  警告: rule_ai_perception_index.yaml 无 rules，跳过")
        return

    synced = 0
    for rule in rules:
        cur.execute(
            """
        INSERT INTO rule_ai_perception
            (rule_id, title, module_id, scope, domain, severity, stability,
             ai_autonomy, safety_level, operations, gate_ids, tags, aliases,
             paired_gate_id, rule_file)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(rule_id) DO UPDATE SET
            title=excluded.title,
            module_id=excluded.module_id,
            scope=excluded.scope,
            domain=excluded.domain,
            severity=excluded.severity,
            stability=excluded.stability,
            ai_autonomy=excluded.ai_autonomy,
            safety_level=excluded.safety_level,
            operations=excluded.operations,
            gate_ids=excluded.gate_ids,
            tags=excluded.tags,
            aliases=excluded.aliases,
            paired_gate_id=excluded.paired_gate_id,
            rule_file=excluded.rule_file
        """,
            (
                rule.get("rule_id", ""),
                rule.get("title", ""),
                rule.get("module_id", ""),
                rule.get("scope", ""),
                rule.get("domain", ""),
                rule.get("severity", ""),
                rule.get("stability", ""),
                rule.get("ai_autonomy", ""),
                rule.get("safety_level", ""),
                rule.get("operations", []) or [],
                rule.get("gate_ids", []) or [],
                rule.get("tags", []) or [],
                rule.get("aliases", []) or [],
                rule.get("paired_gate_id"),
                rule.get("rule_file", ""),
            ),
        )
        synced += 1

    print(f"  同步 {synced}/{len(rules)} 条规则感知索引")


# ========== sync_all 级联失败隔离辅助（裁定 B / P1 / #ARCH-GUC-TRIGGER-FIX-001）==========
# 治本目标：30 项 sync 单点失败不再拖垮全部，每项独立 SAVEPOINT 隔离
# 失败项记录到 sync_failures_log 表，由 reconciler 跟踪修复（裁定 C / P2 填充 error_class）


def _ensure_sync_failures_log_table(cur):
    """幂等创建 sync_failures_log 表（失败项日志，供 reconciler 跟踪）。

    表结构：
    - function_name: 失败的 sync 函数名
    - phase / arch_ref: 优先级阶段 + 架构 issue 编号
    - error_message / error_type: 异常详情
    - error_class: 错误分类（裁定 C / P2 填充：deterministic/transient/unknown）
    - failed_at: 失败时间戳
    - resolved / resolved_at: 解决状态（reconciler 标记）
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_failures_log (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            function_name TEXT NOT NULL,
            phase TEXT,
            arch_ref TEXT,
            error_message TEXT NOT NULL,
            error_type TEXT,
            error_class TEXT,
            failed_at TIMESTAMP NOT NULL DEFAULT NOW(),
            resolved BOOLEAN DEFAULT FALSE,
            resolved_at TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_sync_failures_log_unresolved
        ON sync_failures_log(failed_at) WHERE NOT resolved
    """)


def _log_sync_failures(cur, failures):
    """Best-effort 写入失败项到 sync_failures_log（写入失败不阻断 sync）。

    用独立 SAVEPOINT 隔离：若 sync_failures_log 表创建/写入失败，
    ROLLBACK TO SAVEPOINT 保证主事务不被污染，sync 主流程继续 commit。

    Args:
        cur: DB cursor
        failures: list of dict, 每项含 phase/function/arch_ref/error/error_type
    """
    try:
        cur.execute("SAVEPOINT sp_log_failures")
        _ensure_sync_failures_log_table(cur)
        for f in failures:
            cur.execute(
                """
                INSERT INTO sync_failures_log (function_name, phase, arch_ref, error_message, error_type, error_class)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    f["function"],
                    f["phase"],
                    f["arch_ref"],
                    f["error"],
                    f["error_type"],
                    f.get("error_class", "unknown"),
                ),
            )
        cur.execute("RELEASE SAVEPOINT sp_log_failures")
    except Exception as e:
        # Best-effort: 写日志失败不能阻断 sync 主流程
        try:
            cur.execute("ROLLBACK TO SAVEPOINT sp_log_failures")
        except Exception:  # noqa: BLE001 — SAVEPOINT 可能未建立（best-effort 回滚，忽略失败不阻断主流程）
            pass  # SAVEPOINT 本身可能未建立
        print(f"[WARN] sync_failures_log 写入失败（不阻断）: {e}")


def _run_sync_with_savepoint(cur, phase, arch_ref, func, failures):
    """单项 sync 用 SAVEPOINT 隔离执行；失败记录到 failures 列表。

    治本（裁定 B / P1 / #ARCH-GUC-TRIGGER-FIX-001）：每项 sync 失败只
    ROLLBACK TO SAVEPOINT，不影响其他 sync。失败项追加到 failures 供
    _log_sync_failures 写入 sync_failures_log 表。

    Args:
        cur: DB cursor
        phase: 优先级阶段（如 "P0"）
        arch_ref: 架构 issue 编号（如 "#152"）
        func: sync 函数（签名: func(cur) -> None）
        failures: 可变列表，失败时追加 dict
    """
    sp_name = f"sp_{func.__name__}"[:60]  # PG 标识符长度限制 63
    try:
        cur.execute(f"SAVEPOINT {sp_name}")
        func(cur)
        cur.execute(f"RELEASE SAVEPOINT {sp_name}")
    except Exception as e:
        try:
            cur.execute(f"ROLLBACK TO SAVEPOINT {sp_name}")
        except Exception as rollback_err:
            # SAVEPOINT 本身可能未建立（极端情况），记录但继续
            print(f"[WARN] ROLLBACK TO {sp_name} 失败: {rollback_err}")
        err_msg = str(e)[:2000]  # 截断防日志膨胀
        err_type = type(e).__name__
        err_class = _classify_error(err_type, err_msg)  # 裁定 C / P2
        failures.append(
            {
                "phase": phase,
                "function": func.__name__,
                "arch_ref": arch_ref,
                "error": err_msg,
                "error_type": err_type,
                "error_class": err_class,
            }
        )
        print(f"[SYNC ISOLATED FAIL] {phase} {func.__name__} ({arch_ref}): {err_type} [{err_class}]: {err_msg[:200]}")


# ========== 错误分类（裁定 C / P2 / #ARCH-GUC-TRIGGER-FIX-001）==========
# 分类 sync 函数抛出的 Python 异常，填充 sync_failures_log.error_class 列。
# reconciler 侧另有 _classify_sync_failure 解析 subprocess 文本做重试决策——
# 两者分类标准一致，但本函数基于异常类型/消息，reconciler 侧基于 stderr 文本。

_DETERMINISTIC_EXC_TYPES = frozenset(
    {
        "undefinedobject",
        "undefinedcolumn",
        "undefinedtable",
        "undefinedfunction",
        "syntaxerror",
        "duplicatetable",
        "duplicatecolumn",
        "permissiondenied",
        "notnullviolation",
        "foreignkeyviolation",
        "uniqueviolation",
        "checkviolation",
        "invalidtextrepresentation",
        "invalidparametervalue",
        "undefinedparameter",
        "duplicateobject",
        "duplicatealias",
        "invalidcolumnreference",
        "groupingerror",
        "wrongobjecttype",
    }
)

_TRANSIENT_EXC_TYPES = frozenset(
    {
        "operationalerror",
        "deadlockdetected",
        "serializationfailure",
        "internalerror",
    }
)

_DETERMINISTIC_MSG_PATTERNS = (
    "unrecognized configuration parameter",
    "does not exist",
    "already exists",
    "syntax error",
    "permission denied",
    "not-null constraint",
    "foreign key constraint",
    "unique constraint",
    "check constraint",
    "invalid input syntax",
)

_TRANSIENT_MSG_PATTERNS = (
    "deadlock detected",
    "could not serialize access",
    "connection refused",
    "connection timeout",
    "could not connect",
    "server closed the connection unexpectedly",
    "terminating connection due to",
)


def _classify_error(error_type: str, error_message: str) -> str:
    """分类 sync 函数抛出的异常，决定 error_class（裁定 C / P2 / #ARCH-GUC-TRIGGER-FIX-001）。

    Args:
        error_type: 异常类名（如 "UndefinedObject", "OperationalError"）
        error_message: 异常消息文本

    Returns:
        "deterministic" - 确定性错误（schema bug），重试必然失败
        "transient" - 瞬态错误（连接/死锁），重试可能成功
        "unknown" - 未知错误，保守重试

    优先级：deterministic > transient（避免 OperationalError 包装的 GUC 错误被误判为 transient）
    """
    et = (error_type or "").lower()
    msg = (error_message or "").lower()

    # 1. deterministic 类型/消息优先（psycopg2 可能用 OperationalError 包装 UndefinedObject）
    if et in _DETERMINISTIC_EXC_TYPES:
        return "deterministic"
    for pat in _DETERMINISTIC_MSG_PATTERNS:
        if pat in msg:
            return "deterministic"
    # 2. transient 类型/消息次之
    if et in _TRANSIENT_EXC_TYPES:
        return "transient"
    for pat in _TRANSIENT_MSG_PATTERNS:
        if pat in msg:
            return "transient"
    return "unknown"


# ========== 主同步函数 ==========


def sync_all() -> bool:
    """主同步函数：按优先级同步所有 YAML 源。

    返回 True=全部同步成功，False=部分或全部失败（已隔离，查看 sync_failures_log）。
    严重故障（连接断、触发器恢复失败）抛异常。

    P2 PG 迁移：删除 lock_files 跨进程文件锁（PG 用 MVCC，无需文件锁）。
    事务管理保留：autocommit=False + 显式 commit/rollback。

    裁定 B / P1（#ARCH-GUC-TRIGGER-FIX-001）：每项 sync 用 SAVEPOINT 隔离，
    单点失败只 ROLLBACK TO SAVEPOINT，不影响其他 sync。失败项记录到
    sync_failures_log 表，由 reconciler 跟踪修复（裁定 C / P2 填充 error_class）。
    """
    # P2 PG 迁移：删除 os.path.exists(DB_PATH) 检查（PG 无文件路径概念）
    # P2 PG 迁移：删除 lock_files 跨进程文件锁（PG 用 MVCC）
    try:
        conn = get_depgraph_pg_connection(autocommit=False, superuser=True)  # 需 DDL: DISABLE TRIGGER + CREATE TABLE
    except psycopg2.Error as e:
        print(f"[ERROR] 无法连接 PostgreSQL: {e}")
        return False
    cur = conn.cursor()

    print("=" * 60)
    print("=== YAML→DB 同步开始 ===")
    # 裁定 #ARCH-CH-024 Phase 3: 删除硬编码 localhost:5432/depgraph（连接真源是 config/.env.postgresql）
    # 实际连接由上方 get_depgraph_pg_connection() 读取，此处仅打印通用标识避免漂移
    print("DB: PostgreSQL (depgraph) — 连接配置见 config/.env.postgresql")
    print(f"RULES_DIR: {RULES_DIR}")
    print("=" * 60)

    # sync 函数清单（按优先级阶段 + 架构 issue 编号）
    # 顺序依赖：sync_data_source_assets 必须在 sync_data_source_apis 之前
    # （FK ON DELETE CASCADE——若 assets 后执行，其 DELETE 会级联清空 apis）
    sync_functions = [
        ("P0", "#152", sync_cross_module_dependencies),
        ("P0", "#153", sync_architecture_contract),
        ("P0", "#154", sync_contract_mapping_table),
        ("P0", "#154b", sync_cross_layer_contracts),
        ("P1", "#155", sync_gate_registry),
        ("P1", "#156", sync_functional_domain_registry),
        ("P1", "#157", sync_vocabularies),
        ("P1", "#158", sync_architecture_rules),
        ("P2", "#159", sync_declarative_contract_tracker),
        ("P2", "#160", sync_frontmatter_field_registry),
        ("P2", "#161", sync_registry_of_registries),
        ("P2", "#162", sync_directory_registry),
        ("P2", "#163", sync_rule_catalog_registry),
        ("P3", "#164", sync_infrastructure_registry),
        ("P3", "#164", sync_model_capability_contract),
        ("P4", "#170", sync_hard_boundaries),
        ("P4", "#171", sync_business_streams),
        ("P4", "#172", sync_blueprint_links),
        ("P5", "#173", sync_domain_naming_rules),
        ("P5", "#174", sync_derived_identifier_registry),
        ("P6", "#175", sync_dataflow_registry),
        ("P7", "#176", sync_aggregate_nodes),
        ("P8", "#177", sync_interface_contracts),
        ("P8", "#178", sync_database_nodes),
        # 顺序依赖：assets 必须在 apis 之前（FK ON DELETE CASCADE）
        ("P9", "#180", sync_data_source_assets),
        ("P9", "#179", sync_data_source_apis),
        ("P9", "#181", sync_service_assets),
        ("P9", "#182", sync_config_assets),
        ("P10", "#183", sync_rule_ai_perception_index),
        ("cleanup", "—", cleanup_legacy_fk_violations),
    ]

    failures: list[dict] = []
    try:
        # 临时禁用只读触发器（PG 模式下为 no-op，权限管理替代）
        disable_readonly_triggers(cur)

        # 裁定 B / P1：每项 sync 用 SAVEPOINT 隔离，单点失败不扩散
        for phase, arch_ref, func in sync_functions:
            _run_sync_with_savepoint(cur, phase, arch_ref, func, failures)

        # 失败项写入 sync_failures_log（best-effort，不阻断 sync 主流程）
        if failures:
            _log_sync_failures(cur, failures)

        conn.commit()  # 提交所有成功的 sync（失败项已 ROLLBACK TO SAVEPOINT）

        # 打印汇总
        total = len(sync_functions)
        failed = len(failures)
        succeeded = total - failed
        if failures:
            print(f"\n[PARTIAL] {succeeded}/{total} 项同步成功，{failed} 项失败（已隔离）")
            for f in failures:
                print(f"  - {f['phase']} {f['function']} ({f['arch_ref']}): {f['error_type']}: {f['error'][:150]}")
        else:
            print(f"\n[PASS] {total} 项 YAML→DB 同步完成")

        # DM-90974 Phase 2: 落 depgraph_dirty.flag 触发域文档重生（治本运行时 DB 写入盲区）
        try:
            from _shared.constants import mark_depgraph_dirty

            mark_depgraph_dirty()
        except Exception as _e:  # noqa: BLE001 — flag 写入失败不阻断同步主流程
            print(f"[DIRTY-FLAG] WARNING: depgraph_dirty.flag 写入失败（不阻断）: {_e}", file=sys.stderr)

        # S1.2: 验证 readonly 表 COMMENT（HB-001 table_comment_required）
        verify_readonly_table_comments(cur)

        return len(failures) == 0

    except Exception as e:
        # 严重故障（SAVEPOINT 异常累积、连接断等）：回滚整个事务
        conn.rollback()
        print(f"\n[SYNC FATAL] 严重故障，已回滚: {e}")
        import traceback

        traceback.print_exc()
        raise  # DM-3010: 用raise替代sys.exit(EXIT_FINDINGS)，让调用方可捕获

    finally:
        # 恢复只读触发器（无论同步成功/失败都必须恢复，否则DB无保护）
        try:
            restore_readonly_triggers(cur)
            conn.commit()
        except Exception as e:
            # S1.5 硬告警：触发器恢复失败=DB处于无保护状态，必须阻断（原仅WARNING=静默放行）
            print(f"[FATAL] 触发器恢复失败，DB 只读保护已失效: {e}")
            print("[FATAL] readonly 表此刻可被直接写入——请手动 ALTER TABLE <table> ENABLE TRIGGER USER 恢复")
            raise RuntimeError(f"触发器恢复失败，DB 无保护: {e}") from e
        finally:
            conn.close()
            print("=== YAML→DB 同步完成 ===")


def main():
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="P0-7 YAML→DB 同步脚本：将规则/契约/门禁/词汇表从 YAML 同步到 depgraph"
    )
    parser.add_argument(
        "--list-readonly-tables",
        action="store_true",
        help="列出由 YAML 同步的只读表（手写会被覆盖），不执行同步",
    )
    args = parser.parse_args()
    if args.list_readonly_tables:
        print("# 以下表由 sync_yaml_to_depgraph.py 从 YAML 同步，禁止手写（DB 触发器会 ABORT）：")
        for t in READONLY_TABLES:
            print(f"  {t}")
        return
    ok = sync_all()
    if not ok:
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def ensure_sync_failures_log_table(cur):
    """公共接口：ensure_sync_failures_log_table（Stage 4 公共化）。"""
    return _ensure_sync_failures_log_table(cur)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def resolve_module_to_single_node(cur, module_id, fallback_name):
    """公共接口：resolve_module_to_single_node（Stage 4 公共化）。"""
    return _resolve_module_to_single_node(cur, module_id, fallback_name)
