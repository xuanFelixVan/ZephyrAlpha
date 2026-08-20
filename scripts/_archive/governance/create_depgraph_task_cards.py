#!/usr/bin/env python
"""
depgraph_issue_registry 任务卡批量建卡脚本（直接DB插入版）
创建12张任务卡：5项待修复 + 7项需重新校验
"""

import json
import sqlite3
from datetime import UTC, datetime

DB_PATH = "data/databases/governance.db"
NOW = datetime.now(UTC).isoformat()

POST_SYNC = json.dumps(
    [
        "python D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py --output-db D:/ZephyrAlpha/data/databases/depgraph.db",
        "python D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write",
        "python D:/ZephyrAlpha/scripts/governance/audit_registration.py",
    ],
    ensure_ascii=False,
)

ACCEPTANCE_STD = json.dumps(
    [
        "无temp_*/backup/*-v2残留文件",
        "所有产出文件在deliverables指定路径下",
        "task_completion_gate.py扫描通过（0个ORPHAN/STALE/DUPLICATE/LEGACY）",
    ],
    ensure_ascii=False,
)

RULES_BASE = json.dumps(
    [
        {"module_id": "TRAE-011", "section": "§1", "reason": "域归属铁律"},
        {"module_id": "TRAE-034", "section": "§task_001", "reason": "任务卡标准"},
        {"module_id": "TRAE-034", "section": "§task_001_granularity", "reason": "粒度门约束R1-R6"},
    ],
    ensure_ascii=False,
)

REGISTRY = "D:/ZephyrAlpha/docs/02_enterprise_architecture/depgraph_issue_registry.md"
DB = "D:/ZephyrAlpha/data/databases/depgraph.db"


def make_desc(root_cause, fix, construction, verify):
    return (
        f"根因：{root_cause}\n"
        f"治根：{fix}\n"
        f"施工步骤：\n"
        f"  1. 搜索审计：Grep搜索项目已有同类脚本/模块，审计决策三选一（复用/扩展/新建）\n"
        f"  2. 前置检查：验证files_in_scope路径存在，确认depgraph.db可读写\n"
        f"  3. 施工：{construction}\n"
        f"  4. 疏通：如遇导入错误或SQL异常，创建修复卡\n"
        f"  5. 循环验证：执行acceptance命令，连续2轮exit=0\n"
        f"  6. 更新清单：更新depgraph_issue_registry.md对应问题状态\n"
        f"  7. 四方对齐：depgraph+path_tree+audit_registration三方一致\n"
        f"  8. 端到端测试：验证生成器→全景图→依赖图整条管线\n"
        f"验收标准：{verify}"
    )


CARDS = [
    # ===== 5项待修复 =====
    {
        "task_id": "DM-100242",
        "namespace": "DM",
        "seq": 100242,
        "title": "G5: 生成器域名双源统一——移除硬编码域名字典改为从DB读取",
        "priority": "P1",
        "phase": 4,
        "safety_level": "M",
        "directive": "G5",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§九 G5",
        "files_in_scope": json.dumps(
            [
                "D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py",
                REGISTRY,
            ],
            ensure_ascii=False,
        ),
        "deliverables": json.dumps(
            [
                "D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py",
            ],
            ensure_ascii=False,
        ),
        "allowed_touch": json.dumps(
            [
                "D:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py",
            ],
            ensure_ascii=False,
        ),
        "description": make_desc(
            "generate_project_depgraph.py中硬编码了域名字典，与depgraph.db的domains表形成双源。生成器重跑时硬编码字典覆盖DB修改，导致域名数据丢失。",
            "移除生成器中的硬编码域名字典，改为从depgraph.db的domains表读取域名列表，实现SSoT。",
            "Grep搜索generate_project_depgraph.py中的DOMAIN_DICT或类似硬编码字典定义，删除硬编码字典，改为DB查询SELECT domain_id,ssot_path FROM domains，确保生成器从DB读取域名。",
            "生成器重跑后domains表数据不变，Grep搜索generate_project_depgraph.py无硬编码域名残留，python generate_project_depgraph.py exit=0",
        ),
        "rollback": "git checkout -- scripts/governance/generate_project_depgraph.py",
    },
    {
        "task_id": "SRC-100295",
        "namespace": "SRC",
        "seq": 100295,
        "title": "B2: 安全敏感文件[AI_AUTONOMY]标记——认证/加密/回滚文件标human_gated",
        "priority": "P1",
        "phase": 4,
        "safety_level": "H",
        "directive": "B2",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§五 B2",
        "files_in_scope": json.dumps(
            [
                REGISTRY,
                "D:/ZephyrAlpha/src/zephyr/security/llm_security_01/gateway.py",
            ],
            ensure_ascii=False,
        ),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps(
            [
                "D:/ZephyrAlpha/src/zephyr/security/llm_security_01/gateway.py",
                "D:/ZephyrAlpha/src/zephyr/security/llm_security_02/gateway.py",
                "D:/ZephyrAlpha/scripts/rollback.py",
                "D:/ZephyrAlpha/src/zephyr/governance/kill_switch.py",
            ],
            ensure_ascii=False,
        ),
        "description": make_desc(
            "96.9%代码文件[AI_AUTONOMY]标记为ai_modifiable，安全敏感文件（认证gateway、加密模块、回滚脚本、kill_switch）未标human_gated，AI可自由修改这些文件，存在安全风险。",
            "扫描所有安全敏感文件，将[AI_AUTONOMY]标记从ai_modifiable改为human_gated，产出审计报告记录修改清单。",
            "Grep搜索src/zephyr/security/和scripts/rollback.py和kill_switch.py中的[AI_AUTONOMY]字段，将ai_modifiable改为human_gated，产出审计报告记录所有修改文件和行号。",
            "Grep搜索安全敏感文件[AI_AUTONOMY]字段无ai_modifiable残留，审计报告存在且包含修改清单",
        ),
        "rollback": "git checkout -- src/zephyr/security/ scripts/rollback.py src/zephyr/governance/kill_switch.py",
    },
    {
        "task_id": "DM-100243",
        "namespace": "DM",
        "seq": 100243,
        "title": "E1: arch_layers表10条旧层名记录清理——4标准层已覆盖100%",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "E1",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§七 E1",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([DB], ensure_ascii=False),
        "allowed_touch": json.dumps([DB], ensure_ascii=False),
        "description": make_desc(
            "arch_layers表有13条记录：4条标准层（L0-L3）+9条旧层名（shared/contracts/meta/infrastructure/data/signal/domain/intelligence/simulation/governance）。4标准层已覆盖100%节点，旧层名无引用但仍残留在表中。",
            "删除arch_layers表中9条旧层名记录，仅保留4条标准层记录。",
            "执行DELETE FROM arch_layers WHERE layer_id NOT IN ('L0','L1','L2','L3')，验证删除后表仅剩4条标准层记录。",
            "SELECT COUNT(*) FROM arch_layers WHERE layer_id NOT IN ('L0','L1','L2','L3')返回0，SELECT COUNT(*) FROM arch_layers返回4",
        ),
        "rollback": "从git历史恢复arch_layers表数据，或从备份DB恢复",
    },
    {
        "task_id": "OPS-2026061804",
        "namespace": "OPS",
        "seq": 2026061804,
        "title": "C3: 门禁增量扫描——仅扫描变更文件而非全量扫描",
        "priority": "P2",
        "phase": 4,
        "safety_level": "M",
        "directive": "C3",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§六 C3",
        "files_in_scope": json.dumps(
            [
                "D:/ZephyrAlpha/scripts/governance/audit_registration.py",
                REGISTRY,
            ],
            ensure_ascii=False,
        ),
        "deliverables": json.dumps(
            [
                "D:/ZephyrAlpha/scripts/governance/audit_registration.py",
            ],
            ensure_ascii=False,
        ),
        "allowed_touch": json.dumps(
            [
                "D:/ZephyrAlpha/scripts/governance/audit_registration.py",
            ],
            ensure_ascii=False,
        ),
        "description": make_desc(
            "audit_registration.py每次运行扫描全部文件，即使只改了1个文件。扩展到1500模块后全量扫描会越来越慢，影响开发效率。",
            "为audit_registration.py添加--incremental参数，通过git diff获取变更文件列表，仅扫描变更文件而非全量扫描。",
            "读取audit_registration.py当前扫描逻辑，添加--incremental参数解析，使用git diff --name-only获取变更文件列表，仅对变更文件执行扫描逻辑，保留--full参数用于全量扫描。",
            "python audit_registration.py --incremental exit=0，python audit_registration.py --full exit=0，增量扫描仅扫描变更文件",
        ),
        "rollback": "git checkout -- scripts/governance/audit_registration.py",
    },
    {
        "task_id": "DM-100244",
        "namespace": "DM",
        "seq": 100244,
        "title": "K1: 3项待定架构决策文档——T6事件类型/T7三级配置/T17模块DOMAIN字段",
        "priority": "P3",
        "phase": 4,
        "safety_level": "L",
        "directive": "K1",
        "source_blueprint": "MOD-ARCH-002",
        "source_section": "§十一 K1",
        "files_in_scope": json.dumps(
            [
                REGISTRY,
                "D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md",
            ],
            ensure_ascii=False,
        ),
        "deliverables": json.dumps(
            [
                "D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_decisions_pending.md",
            ],
            ensure_ascii=False,
        ),
        "allowed_touch": json.dumps(
            [
                "D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_decisions_pending.md",
            ],
            ensure_ascii=False,
        ),
        "description": make_desc(
            "3项架构决策未拍板：T6事件类型体系（系统事件分类标准未定义）、T7三级配置结构（配置文件分层规则未确定）、T17模块级DOMAIN字段（模块文件头是否声明域归属未裁定）。这些决策不定，相关功能无法实现。",
            "创建architecture_decisions_pending.md文档，列出3项决策的背景、选项、利弊分析、推荐方案，提交Owner审批。",
            "读取architecture_upgrade_discussion.md中T6/T7/T17的讨论内容，为每项决策编写背景描述+2-3个选项+利弊分析+推荐方案，产出architecture_decisions_pending.md。",
            "architecture_decisions_pending.md存在且包含3项决策的完整分析，每项决策有推荐方案",
        ),
        "rollback": "删除architecture_decisions_pending.md即可，无副作用",
    },
    # ===== 7项需重新校验 =====
    {
        "task_id": "DM-100245",
        "namespace": "DM",
        "seq": 100245,
        "title": "I5-RECHECK: belongs_to校验逻辑修正——存模块ID非node_id需用正确字段校验",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "I5",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§四 I5",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "belongs_to字段存的是模块ID（如MOD-INF-008）而非node_id（INTEGER）。原校验SQL用belongs_to NOT IN (SELECT CAST(node_id AS TEXT) FROM nodes)是错误的——拿模块ID匹配数字node_id当然匹配不上，导致5588个虚假断裂。",
            "确认nodes表有无module_id字段。如有，用belongs_to NOT IN (SELECT module_id FROM nodes)重新校验。如无，belongs_to引用蓝图模块编号，需和蓝图注册表匹配。产出校验报告。",
            "PRAGMA table_info(nodes)检查有无module_id字段，用正确字段重新执行校验SQL，统计真实斷裂数量，产出校验报告含校验SQL+结果+结论。",
            "校验报告存在且含校验SQL和结果，真实斷裂数量明确（可能远少于5588）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
    {
        "task_id": "DM-100246",
        "namespace": "DM",
        "seq": 100246,
        "title": "I8-RECHECK: build_status消费者确认——生成器默认填draft是否有消费者",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "I8",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§四 I8",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "production 802个全标draft、prototype 5833个全标draft——生成器扫描代码时默认填draft。但如果AI不依赖build_status字段做决策，标draft影响不大。需确认有无消费者。",
            "Grep搜索项目代码中所有引用build_status的位置，确认是否有代码/AI依赖该字段做决策。产出消费者清单和结论。",
            "Grep搜索src/zephyr/和scripts/中build_status引用，列出所有消费者文件和行号，分析每个消费者如何使用该字段，产出校验报告含消费者清单+结论。",
            "校验报告存在且含消费者清单，结论明确（有消费者需修复/无消费者可忽略）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
    {
        "task_id": "DM-100247",
        "namespace": "DM",
        "seq": 100247,
        "title": "I13-RECHECK: 孤儿节点过滤——需过滤出node_type=module的production代码文件",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "I13",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§四 I13",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "production孤儿157个，样本全是config/registry/yaml文件（如config/capacity/*.yaml）。配置文件和注册表文件没有代码import依赖是正常的——它们被运行时读取。需过滤出node_type=module的production孤儿才是真问题。",
            "用WHERE node_type=module AND design_maturity=production过滤孤儿节点，统计真实代码孤儿数量，产出校验报告。",
            "执行SELECT path,node_type,domain_id FROM nodes WHERE node_id NOT IN (SELECT from_node_id FROM edges) AND node_id NOT IN (SELECT to_node_id FROM edges) AND design_maturity=production AND node_type=module，产出校验报告含真实孤儿清单+结论。",
            "校验报告存在且含真实代码孤儿清单，结论明确（真实孤儿数量可能远少于157）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
    {
        "task_id": "DM-100248",
        "namespace": "DM",
        "seq": 100248,
        "title": "I15-RECHECK: tags字段消费者确认——88.8%为空是否影响AI决策",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "I15",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§四 I15",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "tags字段88.8%为空（7775/8759）。设计态tags空洞1138个可接受（规划中模块还没打标签）。运营态tags空洞6637个需关注——但如果AI不需要按tags筛选节点，空着影响不大。需确认有无消费者。",
            "Grep搜索项目代码中所有引用tags字段的位置，确认是否有代码/AI依赖该字段做筛选。产出消费者清单和结论。",
            "Grep搜索src/zephyr/和scripts/中tags字段引用（注意排除HTML tags和git tags），列出所有消费者文件和行号，产出校验报告含消费者清单+结论。",
            "校验报告存在且含消费者清单，结论明确（有消费者需回填/无消费者可忽略）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
    {
        "task_id": "DM-100249",
        "namespace": "DM",
        "seq": 100249,
        "title": "E5-RECHECK: last_verified消费者确认——与I15合并处理",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "E5",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§七 E5",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "last_verified字段大量为空，AI无法判断数据新鲜度。但在数据刚生成的阶段所有数据都是新鲜的。需确认last_verified字段有无消费者，与I15合并处理。",
            "Grep搜索项目代码中所有引用last_verified的位置，确认是否有代码/AI依赖该字段判断数据新鲜度。产出消费者清单和结论。",
            "Grep搜索src/zephyr/和scripts/中last_verified引用，列出所有消费者文件和行号，产出校验报告含消费者清单+结论。与I15校验报告交叉引用。",
            "校验报告存在且含消费者清单，结论明确（有消费者需回填/无消费者可忽略）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
    {
        "task_id": "DM-100250",
        "namespace": "DM",
        "seq": 100250,
        "title": "A4-RECHECK: 循环依赖过滤——需排除同域内循环确认有无跨域循环",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "A4",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§三 A4",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "dep_cycles视图8行大部分是同域内循环（模块导入__init__.py，__init__.py又导入模块），这是Python包结构的正常现象。只有跨域循环才是架构问题。需过滤出跨域循环。",
            "查询dep_cycles视图，对每条循环记录检查from_node和to_node的domain_id是否不同，仅保留跨域循环。产出校验报告。",
            "执行SELECT * FROM dep_cycles，对每条记录JOIN nodes表获取from_node_id和to_node_id的domain_id，过滤出domain_id不同的记录，产出校验报告含跨域循环清单+结论。",
            "校验报告存在且含跨域循环清单，结论明确（跨域循环数量可能为0或极少）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
    {
        "task_id": "DM-100251",
        "namespace": "DM",
        "seq": 100251,
        "title": "C1-RECHECK: 3个索引查询频率确认——coupling_strength仅7个不同值索引效果有限",
        "priority": "P2",
        "phase": 4,
        "safety_level": "L",
        "directive": "C1",
        "source_blueprint": "MOD-GOV-DEPGRAPH",
        "source_section": "§六 C1",
        "files_in_scope": json.dumps([DB, REGISTRY], ensure_ascii=False),
        "deliverables": json.dumps([], ensure_ascii=False),
        "allowed_touch": json.dumps([], ensure_ascii=False),
        "description": make_desc(
            "3个缺失索引：nodes.last_verified（290个不同值）、edges.coupling_strength（仅7个不同值，基数太低索引效果有限）、domain_dependencies.constraint_type。需确认这些字段是否常被查询，不常查询则不需要加索引。",
            "Grep搜索项目代码中引用这3个字段的位置，统计查询频率，评估索引收益。产出校验报告。",
            "Grep搜索src/zephyr/和scripts/中last_verified/coupling_strength/constraint_type引用，统计每个字段的查询次数，评估索引收益（coupling_strength基数低可能不需要索引），产出校验报告含查询频率统计+索引建议。",
            "校验报告存在且含查询频率统计和索引建议，结论明确（哪些索引需要创建/哪些不需要）",
        ),
        "rollback": "无文件需删除，无副作用",
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    created = []
    failed = []

    for c in CARDS:
        try:
            cur.execute(
                """
                INSERT INTO tasks (
                    task_id, namespace, seq, title, description, status, priority,
                    phase, execution_model, safety_level, directive, classification,
                    source_blueprint, source_section, files_in_scope, deliverables,
                    allowed_touch, applicable_rules, rollback_instructions,
                    post_sync_standard, acceptance, ai_autonomy_level,
                    created_at, updated_at, is_deleted, construction_status,
                    verification_status, schema_version, dependency_type,
                    assigned_pipeline, estimated_tokens,
                    timeout_minutes, block_sessions_count, approval_required,
                    requires_rb_check
                ) VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?, 'deepseek', ?, ?, 'internal',
                          ?, ?, ?, ?, ?, ?, ?, ?, ?, 'supervised',
                          ?, ?, 0, 'pending', 'unverified', '5.0', 'hard',
                          'A', 8000, 30, 0, 0, 0)
            """,
                (
                    c["task_id"],
                    c["namespace"],
                    c["seq"],
                    c["title"],
                    c["description"],
                    c["priority"],
                    c["phase"],
                    c["safety_level"],
                    c["directive"],
                    c["source_blueprint"],
                    c["source_section"],
                    c["files_in_scope"],
                    c["deliverables"],
                    c["allowed_touch"],
                    RULES_BASE,
                    c["rollback"],
                    POST_SYNC,
                    ACCEPTANCE_STD,
                    NOW,
                    NOW,
                ),
            )
            created.append(c["task_id"])
            print(f"  OK: {c['task_id']} | {c['title'][:60]}")
        except Exception as e:
            failed.append((c["task_id"], str(e)))
            print(f"  FAIL: {c['task_id']} | {str(e)[:200]}")

    conn.commit()
    conn.close()
    print(f"\n=== 结果: {len(created)} created, {len(failed)} failed ===")
    if failed:
        for tid, err in failed:
            print(f"  {tid}: {err[:200]}")


if __name__ == "__main__":
    import sys

    sys.exit("DEPRECATED: 此脚本已归档，depgraph.db 已迁移至 PostgreSQL 16")
    main()
