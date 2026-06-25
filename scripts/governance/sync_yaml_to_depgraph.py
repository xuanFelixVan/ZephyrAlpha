#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.sync_yaml_to_depgraph
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
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
"""
[BLUEPRINT] MOD-ARCH-002 | scripts/governance/sync_yaml_to_depgraph.py | §22.10
[MODULE] 无（独立脚本）
[INVARIANTS] YAML→DB单向同步; 17项同步; try/finally恢复触发器
[MODIFY-GUARD] 本脚本由autopilot执行
[CONSUMERS] autopilot session-20260618-001
[STABILITY] stable
[SAFETY] H
[AI_AUTONOMY] human_gated
[ERROR_CONTRACT] 同步失败→回滚+恢复触发器→exit 1; 成功→exit 0
[TESTS] 无

P0-7 YAML→DB 同步脚本：将规则/契约/门禁/词汇表从 YAML 同步到 depgraph.db
- 同步方向：YAML → DB 单向（禁止反向）
- 17项同步：cross_module_dependencies/architecture_contract/contract_mapping/gate_registry/
  functional_domain/vocabularies/architecture_rules/declarative_contract/frontmatter_field/
  registry_of_registries/directory_registry/rule_catalog/infrastructure/model_capability/
  hard_boundaries/business_streams/blueprint_links
- 通行证机制：临时DROP只读触发器→同步→finally恢复触发器
"""

import argparse
import os
import sqlite3
import sys
from datetime import UTC
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装，请运行: pip install pyyaml")
    sys.exit(1)

# 绝对路径（RULE-EIGHT）
DB_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"
RULES_DIR = r"D:\ZephyrAlpha\docs\01_policies_and_standards"

# V5.0 裁定：9 张表全部保护（与 P0-6 创建触发器列表一致）
READONLY_TABLES = [
    "gates",
    "field_vocabularies",
    "registries",
    "cross_registry_rules",
    "hard_boundaries",
    "business_streams",
    "infrastructure_components",
    "model_capabilities",
    "blueprint_links",
]


def load_yaml(rel_path: str) -> dict:
    """加载 YAML 文件（使用绝对路径）"""
    full_path = os.path.join(RULES_DIR, rel_path)
    if not os.path.exists(full_path):
        print(f"  警告: {full_path} 不存在，跳过")
        return {}
    with open(full_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def disable_readonly_triggers(cur):
    """临时禁用只读触发器（sync 脚本的通行证）"""
    for table in READONLY_TABLES:
        cur.execute(f"DROP TRIGGER IF EXISTS readonly_{table}_insert")
        cur.execute(f"DROP TRIGGER IF EXISTS readonly_{table}_update")
        cur.execute(f"DROP TRIGGER IF EXISTS readonly_{table}_delete")
    print("  只读触发器已临时禁用（sync 通行证）")


def restore_readonly_triggers(cur):
    """恢复只读触发器（无论成功失败必须恢复）"""
    for table in READONLY_TABLES:
        cur.execute(f"""
        CREATE TRIGGER IF NOT EXISTS readonly_{table}_insert
        BEFORE INSERT ON {table}
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ABORT, '{table} 表只读（唯一真源是 YAML），请修改 YAML 后运行 sync_yaml_to_depgraph.py');
        END;
        """)
        cur.execute(f"""
        CREATE TRIGGER IF NOT EXISTS readonly_{table}_update
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ABORT, '{table} 表只读（唯一真源是 YAML），请修改 YAML 后运行 sync_yaml_to_depgraph.py');
        END;
        """)
        cur.execute(f"""
        CREATE TRIGGER IF NOT EXISTS readonly_{table}_delete
        BEFORE DELETE ON {table}
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ABORT, '{table} 表只读（唯一真源是 YAML），请修改 YAML 后运行 sync_yaml_to_depgraph.py');
        END;
        """)
    print("  只读触发器已恢复（唯一真源保护激活）")


# ========== P0 优先级同步 ==========


def sync_cross_module_dependencies(cur):
    """#152: 跨模块依赖注册表 → edges 表"""
    print("同步 #152: 跨模块依赖注册表 → edges...")
    data = load_yaml("_registry/catalogs/cross_module_dependency_registry.yaml")
    if not data:
        return

    # 先删除旧的 YAML 同步的 design edge（valid_since IS NOT NULL）
    # 保留 apply_depgraph.py --add-design-edge 写入的（valid_since IS NULL）
    cur.execute("DELETE FROM edges WHERE dep_maturity = 'design' AND valid_since IS NOT NULL")

    deps = data.get("dependencies", [])
    synced = 0
    for dep in deps:
        # YAML source/target 是 module_id（如 MOD-INF-002），用 blueprint_id 匹配
        source = dep.get("source", "")
        source_name = dep.get("source_name", "")
        target = dep.get("target", "")
        target_name = dep.get("target_name", "")

        # 优先用 blueprint_id 匹配，其次用 path LIKE source_name
        cur.execute("SELECT node_id FROM nodes WHERE blueprint_id = ? LIMIT 1", (source,))
        from_row = cur.fetchone()
        if not from_row and source_name:
            cur.execute("SELECT node_id FROM nodes WHERE path LIKE ? LIMIT 1", (f"%{source_name}%",))
            from_row = cur.fetchone()

        cur.execute("SELECT node_id FROM nodes WHERE blueprint_id = ? LIMIT 1", (target,))
        to_row = cur.fetchone()
        if not to_row and target_name:
            cur.execute("SELECT node_id FROM nodes WHERE path LIKE ? LIMIT 1", (f"%{target_name}%",))
            to_row = cur.fetchone()

        if from_row and to_row:
            is_legal = 1 if dep.get("is_legal_cycle", False) else 0
            cur.execute(
                """
            INSERT INTO edges
            (from_node_id, to_node_id, dep_type, coupling_strength,
             architecture_direction, api_contract_refs, data_transfer_description,
             dep_maturity, valid_since, is_legal_cycle)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'design', ?, ?)
            """,
                (
                    from_row[0],
                    to_row[0],
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

    print(f"  同步 {synced}/{len(deps)} 条依赖（dep_maturity='design'）")


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
        INSERT OR REPLACE INTO arch_constraints
        (constraint_id, name, constraint_type, rule_definition, severity, enforcement)
        VALUES (?, ?, 'architecture_contract', ?, ?, 'code')
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
    for domain_key, domain_data in data.get("domain_contracts", {}).items():
        if not isinstance(domain_data, dict):
            continue
        contracts = domain_data.get("contracts", [])
        for contract in contracts:
            if not isinstance(contract, dict):
                continue
            # YAML 用 domain_contract_id，DB 用 contract_id
            contract_id = contract.get("domain_contract_id", contract.get("contract_id", ""))
            if not contract_id:
                continue
            cur.execute(
                """
            INSERT INTO contracts
            (contract_id, name, provider_domain, consumer_domain, contract_type)
            VALUES (?, ?, ?, ?, 'domain_contract')
            ON CONFLICT(contract_id) DO UPDATE SET
                name=excluded.name,
                provider_domain=excluded.provider_domain,
                consumer_domain=excluded.consumer_domain,
                contract_type=excluded.contract_type
            """,
                (
                    contract_id,
                    contract.get("description", ""),
                    domain_key,
                    contract.get("domain_mapping", contract.get("direction", "")),
                ),
            )
            synced += 1

    # 层契约
    for contract in data.get("layer_contracts", []):
        if not isinstance(contract, dict):
            continue
        contract_id = contract.get("contract_id", "")
        if not contract_id:
            continue
        cur.execute(
            """
        INSERT INTO contracts
        (contract_id, name, provider_domain, consumer_domain, contract_type)
        VALUES (?, ?, ?, ?, 'layer_contract')
        ON CONFLICT(contract_id) DO UPDATE SET
            name=excluded.name,
            provider_domain=excluded.provider_domain,
            consumer_domain=excluded.consumer_domain,
            contract_type=excluded.contract_type
        """,
            (
                contract_id,
                contract.get("description", ""),
                contract.get("layer", ""),
                contract.get("domain_mapping", "") or "",
            ),
        )
        synced += 1

    print(f"  同步 {synced} 条契约")


# ========== P1 优先级同步 ==========


def sync_gate_registry(cur):
    """#155: 门禁注册表 → gates 表"""
    print("同步 #155: 门禁注册表 → gates...")
    data = load_yaml("_registry/catalogs/gate_registry.yaml")
    if not data:
        return

    gates = data.get("gates", [])
    synced = 0
    for gate in gates:
        cur.execute(
            """
        INSERT OR REPLACE INTO gates
        (gate_id, name, entry, description, files_trigger, always_run, category, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
            ),
        )
        synced += 1

    print(f"  同步 {synced}/{len(gates)} 个门禁")


def normalize_domain_id(domain_id: str) -> str:
    """归一化域ID: 保留 D- 前缀,将其余连字符替换为下划线。

    D-AUTONOMY-CORE → D-AUTONOMY_CORE
    D-INFRA-OPS    → D-INFRA_OPS
    D-AUTONOMY_CORE → D-AUTONOMY_CORE (无变化)
    """
    if not domain_id.startswith("D-"):
        return domain_id
    return "D-" + domain_id[2:].replace("-", "_")


def validate_domain_id_consistency(cur, entries):
    """校验 YAML 域ID与 DB 现有域ID的归一化一致性,防止连字符/下划线重复。

    检查: YAML 中的 domain_id 归一化后是否与 DB 现有 domain_id 不同但归一化相同。
    如果 YAML 用 D-AUTONOMY-CORE 而 DB 已有 D-AUTONOMY_CORE,会报警并跳过。
    """
    cur.execute("SELECT domain_id FROM domains")
    existing_ids = {row[0] for row in cur.fetchall()}

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
        # 仅当 yaml_id 中间有下划线时才检查(单词域如 D-GOVERNANCE 无连字符变体)
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
    from datetime import datetime

    now = datetime.now(UTC).isoformat()
    skipped = 0
    for d in entries:
        domain_id = d.get("domain", "")
        # 跳过有归一化冲突的域(防止产生重复)
        if domain_id in conflict_set:
            print(
                f"  SKIP: 跳过冲突域 '{domain_id}'——归一化后与 DB 现有域冲突,请先清理"
            )
            skipped += 1
            continue
        # DM-100252: 跳过小写类别域（非 D-XXX 格式），防止 UPSERT 折叠产生脏数据
        # YAML 将在 DM-100256 重构为 D-XXX 子域描述表
        if not domain_id.startswith("D-"):
            print(
                f"  SKIP: 跳过小写类别域 '{domain_id}' (subdomain={d.get('subdomain', '')})——待 DM-100256 重构为 D-XXX 格式"
            )
            skipped += 1
            continue
        ai_autonomy = d.get("ai_autonomy", "ai_modifiable")
        covers = d.get("covers", [])
        description = covers[0] if covers else ""
        # domain_group NOT NULL：YAML 无此字段，用 tier 或 'governance' 作为默认值
        domain_group = d.get("tier", "governance")
        if isinstance(domain_group, str) and domain_group.startswith("tier_"):
            domain_group = domain_group.replace("tier_", "").replace("_governance", "").replace("_", "")

        cur.execute(
            """
        INSERT INTO domains (domain_id, domain_name, domain_group, description,
                             modification_permission, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(domain_id) DO UPDATE SET
            domain_name=excluded.domain_name,
            description=excluded.description,
            modification_permission=excluded.modification_permission,
            updated_at=excluded.updated_at
        """,
            (domain_id, d.get("subdomain", ""), domain_group, description, ai_autonomy, now, now),
        )
        synced += 1

        ssot_path = d.get("ssot_path", "")
        if ssot_path:
            # arch_path_mappings 需要 path_type NOT NULL 和 state NOT NULL
            cur.execute(
                """
            INSERT OR REPLACE INTO arch_path_mappings
            (path_pattern, domain_id, path_type, state)
            VALUES (?, ?, 'ssot', 'active')
            """,
                (ssot_path, domain_id),
            )

    print(f"  同步 {synced} 个功能域（含 modification_permission 字段映射），跳过 {skipped} 个小写类别域")


def sync_vocabularies(cur):
    """#157: 词汇表 → field_vocabularies 表"""
    print("同步 #157: 词汇表 → field_vocabularies...")
    vocab_dir = os.path.join(RULES_DIR, "_registry/vocabularies")
    if not os.path.exists(vocab_dir):
        return

    synced = 0
    for yaml_file in Path(vocab_dir).glob("*.yaml"):
        data = load_yaml(f"_registry/vocabularies/{yaml_file.name}")
        field_name = data.get("field_name", yaml_file.stem)
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
            INSERT OR REPLACE INTO field_vocabularies
            (field_name, value, definition, source_yaml)
            VALUES (?, ?, ?, ?)
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
            INSERT OR REPLACE INTO arch_constraints
            (constraint_id, name, constraint_type, rule_definition, severity, enforcement)
            VALUES (?, ?, 'architecture_rule', ?, ?, 'code')
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
        # provider_domain/consumer_domain 是 NOT NULL，declarative 契约用 source 作为 provider_domain
        cur.execute(
            """
        INSERT INTO contracts
        (contract_id, name, provider_domain, consumer_domain, contract_type,
         promise, actual_consumer, fulfillment_status, gap, target_phase, last_reviewed)
        VALUES (?, ?, ?, ?, 'declarative', ?, ?, ?, ?, ?, ?)
        ON CONFLICT(contract_id) DO UPDATE SET
            promise=excluded.promise,
            actual_consumer=excluded.actual_consumer,
            fulfillment_status=excluded.fulfillment_status,
            gap=excluded.gap,
            target_phase=excluded.target_phase,
            last_reviewed=excluded.last_reviewed
        """,
            (
                contract.get("contract_id", ""),
                contract.get("source", ""),
                contract.get("source", "declarative"),
                contract.get("actual_consumer", "declarative"),
                contract.get("promise", ""),
                contract.get("actual_consumer", ""),
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
            INSERT OR REPLACE INTO field_vocabularies
            (field_name, value, definition, source_yaml)
            VALUES (?, ?, ?, 'frontmatter_field_registry.yaml')
            """,
                (field_name, v, definition),
            )
            synced += 1

    print(f"  同步 {synced} 个字段枚举值")


def sync_registry_of_registries(cur):
    """#161: 注册表之注册表 → registries + cross_registry_rules 表"""
    print("同步 #161: 注册表之注册表 → registries + cross_registry_rules...")
    data = load_yaml("_registry/catalogs/registry_of_registries.yaml")
    if not data:
        return

    registries = data.get("registries", [])
    synced = 0
    for reg in registries:
        cur.execute(
            """
        INSERT OR REPLACE INTO registries
        (registry_id, name, title, path, version, description, ssot_for)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
        INSERT OR REPLACE INTO cross_registry_rules
        (rule_id, title, fields, ssot, consistency, violation_action)
        VALUES (?, ?, ?, ?, ?, ?)
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
        VALUES (?, ?, 'directory', ?, ?, 'design')
        ON CONFLICT(path) DO UPDATE SET
            parent_path=excluded.parent_path,
            domain_id=excluded.domain_id,
            blueprint_id=excluded.blueprint_id,
            design_maturity='design'
        WHERE arch_directory_tree.design_maturity = 'design'
        """,
            (d.get("path", ""), d.get("parent_path", ""), d.get("domain_id", ""), d.get("module_id", "")),
        )
        synced += 1

    print(f"  同步 {synced} 个目录（design_maturity='design'）")


def sync_rule_catalog_registry(cur):
    """#163: 规则路径目录 → arch_directory_tree 表（文档节点归属位置表）"""
    print("同步 #163: 规则路径目录 → arch_directory_tree（文档节点位置）...")
    data = load_yaml("_registry/catalogs/rule_catalog_registry.yaml")
    if not data:
        return

    rules = data.get("rules", [])
    synced = 0
    for rule in rules:
        path = rule.get("path", "")
        if not path:
            continue

        cur.execute(
            """
        INSERT INTO arch_directory_tree
        (path, parent_path, path_type, domain_id, blueprint_id, design_maturity)
        VALUES (?, ?, 'file', 'D-GOV-DOCS', ?, 'design')
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
        INSERT OR REPLACE INTO infrastructure_components
        (component_id, component_type, address, health_check, dependencies, sla, status)
        VALUES (?, ?, ?, ?, ?, ?, 'active')
        """,
            (
                comp.get("infra_id", comp.get("component_id", comp.get("type", ""))),
                comp.get("type", ""),
                comp.get("host", comp.get("address", "")) or "",
                comp.get("health_check", ""),
                str(comp.get("dependency_of", comp.get("dependencies", []))),
                comp.get("sla", ""),
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
        INSERT OR REPLACE INTO model_capabilities
        (model_name, tier, max_files_per_session, allowed_paths,
         forbidden_paths, recommended_tasks, forbidden_tasks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
    data = load_yaml("_registry/catalogs/hard_boundaries.yaml")
    if not data:
        print("  警告: hard_boundaries.yaml 不存在，跳过（待创建 YAML 源）")
        return

    cur.execute("DELETE FROM hard_boundaries")

    boundaries = data.get("boundaries", [])
    synced = 0
    for b in boundaries:
        cur.execute(
            """
        INSERT OR REPLACE INTO hard_boundaries
        (boundary_id, category, constraint_def, parameters, impact)
        VALUES (?, ?, ?, ?, ?)
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
    data = load_yaml("_registry/catalogs/business_streams.yaml")
    if not data:
        print("  警告: business_streams.yaml 不存在，跳过（待创建 YAML 源）")
        return

    cur.execute("DELETE FROM business_streams")

    streams = data.get("streams", [])
    synced = 0
    for s in streams:
        cur.execute(
            """
        INSERT OR REPLACE INTO business_streams
        (stream_id, name, goal, input, output, runtime_plane)
        VALUES (?, ?, ?, ?, ?, ?)
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(rule_id) DO UPDATE SET
            rule_name=excluded.rule_name,
            rule_text=excluded.rule_text,
            applies_to=excluded.applies_to,
            severity=excluded.severity,
            example_bad=excluded.example_bad,
            example_good=excluded.example_good,
            source_doc=excluded.source_doc
        """,
            (e["rule_id"], e["rule_name"], e["rule_text"],
             e.get("applies_to", "create"), e.get("severity", "error"),
             e.get("example_bad", ""), e.get("example_good", ""),
             now, e.get("source_doc", "")),
        )
        synced += 1

    print(f"  同步 {synced} 条域命名规则（NR-001~NR-005）")


# ========== 主同步函数 ==========


def sync_all():
    """主同步函数：按优先级同步所有 YAML 源"""
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] {DB_PATH} not found")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 60)
    print("=== YAML→DB 同步开始 ===")
    print(f"DB: {DB_PATH}")
    print(f"RULES_DIR: {RULES_DIR}")
    print("=" * 60)

    try:
        # 临时禁用只读触发器
        disable_readonly_triggers(cur)
        conn.commit()

        # P0 优先级同步
        sync_cross_module_dependencies(cur)  # #152
        sync_architecture_contract(cur)  # #153
        sync_contract_mapping_table(cur)  # #154

        # P1 优先级同步
        sync_gate_registry(cur)  # #155
        sync_functional_domain_registry(cur)  # #156
        sync_vocabularies(cur)  # #157
        sync_architecture_rules(cur)  # #158

        # P2 优先级同步
        sync_declarative_contract_tracker(cur)  # #159
        sync_frontmatter_field_registry(cur)  # #160
        sync_registry_of_registries(cur)  # #161
        sync_directory_registry(cur)  # #162
        sync_rule_catalog_registry(cur)  # #163

        # P3 优先级同步
        sync_infrastructure_registry(cur)  # #164
        sync_model_capability_contract(cur)  # #164

        # P4 优先级同步（V4.2 新增表）
        sync_hard_boundaries(cur)  # #170
        sync_business_streams(cur)  # #171
        sync_blueprint_links(cur)  # #172

        # P5 优先级同步（裁定#204 预防根因）
        sync_domain_naming_rules(cur)  # #173

        conn.commit()
        print("\n[PASS] 18 项 YAML→DB 同步完成")

    except Exception as e:
        conn.rollback()
        print(f"\n[SYNC ERROR] 同步失败，已回滚: {e}")
        import traceback

        traceback.print_exc()
        raise  # DM-3010: 用raise替代sys.exit(1)，让调用方可捕获

    finally:
        # 恢复只读触发器（无论成功失败必须恢复）
        try:
            restore_readonly_triggers(cur)
            conn.commit()
        except Exception as e:
            print(f"[WARNING] 触发器恢复失败: {e}")
        finally:
            conn.close()
            print("=== YAML→DB 同步完成 ===")


def main():
    parser = argparse.ArgumentParser(
        description="P0-7 YAML→DB 同步脚本：将规则/契约/门禁/词汇表从 YAML 同步到 depgraph.db"
    )
    parser.parse_args()
    sync_all()


if __name__ == "__main__":
    main()
