"""数据库大更新后全项目对齐任务卡创建脚本

基于 architecture_upgrade_discussion.md §19 数据库架构，创建细粒度任务卡。
每个卡遵循 RULE-SIX 粒度门禁：deliverables<=1, files_in_scope<=3, acceptance<=1

任务卡分组：
  A组：DDL对齐（3卡）
  B组：路径引用修复（3卡）
  C组：生成器更新+红蓝测试（4卡）
  D组：文档更新（2卡）
  E组：四方对齐+集成检查（3卡）
  F组：极端测试方案（3卡）
"""

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(r"D:\ZephyrAlpha\data\databases\governance.db")
NOW = datetime.now(UTC).isoformat()


def create_task(
    conn,
    task_id,
    title,
    description,
    files_in_scope,
    deliverables,
    acceptance,
    depends_on=None,
    priority="P1",
    allowed_touch=None,
    applicable_rules=None,
    rollback_instructions="",
    post_sync_standard=None,
):
    """直接 SQL INSERT 创建任务卡（适配实际19列 tasks 表结构）"""
    existing = conn.execute("SELECT task_id FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    if existing:
        print(f"  [SKIP] {task_id} 已存在")
        return

    conn.execute(
        """
        INSERT INTO tasks (
            task_id, domain_id, title, description, status, priority,
            created_at, updated_at, blueprint_id, acceptance,
            files_in_scope, deliverables, applicable_rules, allowed_touch,
            rollback_instructions, post_sync_standard, construction_targets
        ) VALUES (?, ?, ?, ?, 'PENDING', ?,
                  ?, ?, 'DB-ALIGN-001', ?,
                  ?, ?, ?, ?,
                  ?, ?, ?)
    """,
        (
            task_id,
            "DM",
            title,
            description,
            priority,
            NOW,
            NOW,
            json.dumps(acceptance),
            json.dumps(files_in_scope),
            json.dumps(deliverables),
            json.dumps(applicable_rules or []),
            json.dumps(allowed_touch or files_in_scope),
            rollback_instructions,
            json.dumps(post_sync_standard or []),
            json.dumps(depends_on or []),
        ),
    )
    print(f"  [CREATED] {task_id}: {title}")


def main():
    conn = sqlite3.connect(str(DB_PATH))

    # ============================================================
    # A组：DDL对齐（3卡）—— 数据库表结构与架构方案§19对齐
    # ============================================================
    print("\n=== A组：DDL对齐 ===")

    create_task(
        conn,
        task_id="DM-100100",
        title="DDL对齐：governance.db 删除多余的 domains 表",
        description=(
            "根因：governance.db 中存在 domains 表（0行），但架构方案§19.4 D50/D52裁定 domains 表只属于 depgraph.db。"
            "governance.db 的 domains 表是迁移残留，违反唯一真源原则——两个库都有 domains 表会导致AI混淆数据归属。"
            "治根：删除 governance.db 中的 domains 表。depgraph.db 的 domains 表（35行）是唯一真源。"
            "施工步骤："
            "1. 确认 governance.db domains 表行数=0（无数据丢失风险）"
            "2. 确认 depgraph.db domains 表有35行数据（真源完整）"
            "3. 执行 DROP TABLE domains ON governance.db"
            "4. 更新 sqlite_schema.py 中 governance.db 的 schema 版本号"
            "5. 验证：governance.db 无 domains 表，depgraph.db domains 表完整"
            "验收标准：governance.db 表列表中无 domains 表，depgraph.db domains 表35行不变"
        ),
        files_in_scope=["data/databases/governance.db", "src/zephyr/data/persistence/sqlite_schema.py"],
        deliverables=["governance.db 无 domains 表"],
        acceptance=["governance.db 无 domains 表且 depgraph.db domains 35行不变"],
        rollback_instructions="从备份恢复 governance.db 的 domains 表",
    )

    create_task(
        conn,
        task_id="DM-100101",
        title="DDL对齐：depgraph.db nodes 表补齐7个缺失字段",
        description=(
            "根因：架构方案§19.8.4 裁定 nodes 表应有29列（含 node_name/file_path/stability/safety_level/ai_autonomy/design_state/runtime_state），"
            "但实际 nodes 表只有22列，缺少7列：node_name, file_path, stability, safety_level, ai_autonomy, design_state, runtime_state。"
            "这些字段是代码头部十字段对齐的核心字段，缺失导致无法存储模块的设计态属性和自治级别。"
            "治根：ALTER TABLE nodes ADD COLUMN 补齐7个缺失字段。"
            "施工步骤："
            "1. 对 depgraph.db 执行7条 ALTER TABLE nodes ADD COLUMN 语句"
            "2. 从现有 type_specific_data JSON 字段中提取已有值回填"
            "3. 更新 generate_project_depgraph.py 的 write_depgraph_to_db() 函数写入新字段"
            "4. 更新 depgraph_reader.py 的查询方法支持新字段"
            "5. 验证：PRAGMA table_info(nodes) 显示29列"
            "验收标准：nodes 表包含§19.8.4定义的全部字段，现有6140行数据无丢失"
        ),
        files_in_scope=["data/databases/depgraph.db", "scripts/governance/generate_project_depgraph.py"],
        deliverables=["depgraph.db nodes 表29列完整"],
        acceptance=[
            "PRAGMA table_info(nodes) 包含 node_name/file_path/stability/safety_level/ai_autonomy/design_state/runtime_state"
        ],
        depends_on=[],
        rollback_instructions="ALTER TABLE 无法回滚，需从备份恢复 depgraph.db",
    )

    create_task(
        conn,
        task_id="DM-100102",
        title="DDL对齐：depgraph.db 创建 init_db() 幂等初始化函数",
        description=(
            "根因：governance.db 有 sqlite_schema.py 提供27版本迁移框架，但 depgraph.db 没有独立的 schema 迁移脚本。"
            "当前 depgraph.db 的表是手动创建的，没有 CREATE TABLE IF NOT EXISTS 的幂等初始化函数。"
            "这意味着：新环境部署时无法自动建表；DDL变更（如DM-100101补字段）没有版本化追踪。"
            "治根：创建 depgraph_schema.py，提供 init_db() + 版本化迁移框架，与 sqlite_schema.py 同模式。"
            "施工步骤："
            "1. 创建 src/zephyr/data/persistence/depgraph_schema.py"
            "2. 实现 init_db(db_path) 函数，包含§19.5+§19.6+§19.8 全部15表的 CREATE TABLE IF NOT EXISTS"
            "3. 实现 _schema_version 表和版本化迁移框架"
            "4. 将 DM-100101 的 ALTER TABLE 作为 v1→v2 迁移"
            "5. 在 database_service.py 中调用 depgraph_schema.init_db()"
            "6. 验证：对空库调用 init_db() 两次均无报错"
            "验收标准：init_db() 幂等执行无报错，15表+索引全部创建"
        ),
        files_in_scope=["src/zephyr/data/persistence/depgraph_schema.py", "src/zephyr/data/database_service.py"],
        deliverables=["depgraph_schema.py init_db() 幂等建表"],
        acceptance=["对空库调用 init_db() 两次均 exit 0"],
        depends_on=["DM-100101"],
        rollback_instructions="删除 depgraph_schema.py，恢复 database_service.py",
    )

    # ============================================================
    # B组：路径引用修复（3卡）—— 全项目数据库路径统一
    # ============================================================
    print("\n=== B组：路径引用修复 ===")

    create_task(
        conn,
        task_id="DM-100110",
        title="路径修复：源码中6处 governance.db 错误路径修正",
        description=(
            "根因：6处源码文件中 governance.db 路径缺少 databases/ 子目录或指向旧目录："
            "1. sqlite_schema.py:81 — data/governance.db → data/databases/governance.db（核心路径定义！）"
            "2. drift_engine.py(2处) — data/drift/governance.db → data/databases/governance.db"
            "3. correlation_engine.py — data/drift_audit/governance.db → data/databases/governance.db"
            "4. gate_persistence.py(3处) — os.path.join(_audit_dir, 'governance.db') → data/databases/governance.db"
            "5. trend_analyzer.py — os.path.join(_db_dir, 'governance.db') → 确认并修正"
            "6. rollback_verifier.py + rollback_drill.py — data/governance.db → data/databases/governance.db"
            "治根：逐文件修正路径，统一使用 data/databases/governance.db。"
            "施工步骤："
            "1. 修改 sqlite_schema.py DB_PATH 为 data/databases/governance.db（影响所有导入者）"
            "2. 修改 drift_engine.py 两处路径"
            "3. 修改 correlation_engine.py 路径"
            "4. 修改 gate_persistence.py 三处路径构造逻辑"
            "5. 修改 rollback_verifier.py 和 rollback_drill.py 路径"
            "6. 验证：Grep 全项目确认无 data/governance.db 或 data/drift/governance.db 残留"
            "验收标准：Grep 'data/governance.db|data/drift/governance|data/drift_audit/governance' 结果=0"
        ),
        files_in_scope=[
            "src/zephyr/data/persistence/sqlite_schema.py",
            "src/zephyr/governance/behavioral_auditor/drift_engine.py",
            "src/zephyr/governance/behavioral_auditor/gate_persistence.py",
        ],
        deliverables=["6处源码路径全部指向 data/databases/governance.db"],
        acceptance=["Grep 错误路径结果=0"],
        rollback_instructions="git revert 逐文件回滚",
    )

    create_task(
        conn,
        task_id="DM-100111",
        title="路径修复：脚本中3处 governance.db 错误路径修正",
        description=(
            "根因：3处治理脚本中 governance.db 路径缺少 databases/ 子目录："
            "1. scripts/governance/run_all.py:1191 — data/governance.db → data/databases/governance.db"
            "2. scripts/governance/d5_architecture/validators/validate_cross_references.py:210 — data/governance.db → data/databases/governance.db"
            "3. scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py:50 — data/governance.db → data/databases/governance.db"
            "治根：逐文件修正路径。"
            "施工步骤："
            "1. 修改 run_all.py 第1191行路径"
            "2. 修改 validate_cross_references.py 第210行路径"
            "3. 修改 detect_deprecated_adr_references.py 第50行路径"
            "4. 验证：Grep scripts/ 确认无 data/governance.db 残留（排除 _shared/constants.py 已正确的引用）"
            "验收标准：Grep scripts/ 'data/governance.db' 结果仅含 _shared/constants.py 的正确引用"
        ),
        files_in_scope=[
            "scripts/governance/run_all.py",
            "scripts/governance/d5_architecture/validators/validate_cross_references.py",
            "scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py",
        ],
        deliverables=["3处脚本路径全部指向 data/databases/governance.db"],
        acceptance=["Grep scripts/ 错误路径结果=0"],
        depends_on=[],
        rollback_instructions="git revert 逐文件回滚",
    )

    create_task(
        conn,
        task_id="DM-100112",
        title="路径修复：测试文件+文档中旧数据库路径更新",
        description=(
            "根因：测试文件和文档中残留旧数据库路径引用："
            "1. tests/test_interrupt_guard.py:37 — 断言 data/auto_fix/auto_fix.db（源码已改为 governance.db，测试断言需同步）"
            "2. tests/test_fix_health_check.py:37 — 同上"
            "3. tests/test_boot_hooks_unlock.py:17 — data/governance.db → data/databases/governance.db"
            "4. tests/test_mcp_task_claim.py:13 — data/governance.db → data/databases/governance.db"
            "5. docs/03_modules/_domain_governance/drift_detector/blueprint.md — 引用 drift_events.db 旧路径"
            "6. database_manager.py(2处) — 备份文件名仍用 zalpha_metadata_ 前缀"
            "7. sqlite_dumper.py:442 — SQL 查询引用 zalpha_metadata 表名"
            "治根：逐文件更新路径和名称。"
            "施工步骤："
            "1. 更新测试断言中的路径"
            "2. 更新文档中的旧路径引用"
            "3. 更新 database_manager.py 备份命名从 zalpha_metadata_ 改为 governance_"
            "4. 更新 sqlite_dumper.py SQL 查询中的表名"
            "5. 验证：Grep 全项目确认无旧路径残留"
            "验收标准：Grep 'auto_fix.db|zalpha_metadata|data/drift/drift_events' 结果=0（排除架构讨论文档中的历史描述）"
        ),
        files_in_scope=[
            "tests/test_interrupt_guard.py",
            "src/zephyr/data/persistence/database_manager.py",
            "src/zephyr/infrastructure/runtime_integration/rollback/sqlite_dumper.py",
        ],
        deliverables=["测试+文档+备份命名全部更新"],
        acceptance=["Grep 旧路径残留=0"],
        depends_on=["DM-100110"],
        rollback_instructions="git revert 逐文件回滚",
    )

    # ============================================================
    # C组：生成器更新+红蓝测试（4卡）
    # ============================================================
    print("\n=== C组：生成器更新+红蓝测试 ===")

    create_task(
        conn,
        task_id="DM-100120",
        title="生成器更新：depgraph 生成器适配 nodes 表新字段",
        description=(
            "根因：DM-100101 为 nodes 表补齐7字段后，generate_project_depgraph.py 的 write_depgraph_to_db() 函数"
            "需要同步更新 INSERT 语句以写入新字段。当前函数只写入22列，新字段值为 NULL。"
            "治根：更新生成器，从文件头部十字段和 type_specific_data JSON 中提取新字段值写入。"
            "施工步骤："
            "1. 更新 write_depgraph_to_db() 的 INSERT 语句包含29列"
            "2. 更新 build_depgraph() 的节点构建逻辑，从文件头部提取 stability/safety_level/ai_autonomy"
            "3. 更新 merge_design_fields() 的 DESIGN_STATE_FIELDS 包含 design_state/runtime_state"
            "4. 运行生成器 --output-db 验证写入"
            "5. 验证：SELECT node_name, stability, safety_level FROM nodes LIMIT 10 有非NULL值"
            "验收标准：生成器运行后 nodes 表新字段有值（非全NULL）"
        ),
        files_in_scope=["scripts/governance/generate_project_depgraph.py"],
        deliverables=["depgraph 生成器写入29列 nodes 表"],
        acceptance=["生成器运行后 nodes 表新字段有非NULL值"],
        depends_on=["DM-100101"],
        rollback_instructions="git revert generate_project_depgraph.py",
    )

    create_task(
        conn,
        task_id="DM-100121",
        title="生成器更新：panorama 生成器适配 arch_ 表新字段",
        description=(
            "根因：generate_project_path_tree.py 的 cmd_write_db() 写入 arch_directory_tree 表，"
            "需要确认写入逻辑与§19.6 DDL对齐，特别是 stability/ai_autonomy 字段。"
            "同时需要更新生成器使用 depgraph_schema.py 的 init_db() 确保表结构正确。"
            "治根：更新生成器调用 init_db()，确认写入字段完整。"
            "施工步骤："
            "1. 更新 cmd_write_db() 调用 depgraph_schema.init_db() 确保表存在"
            "2. 确认 INSERT 语句包含 stability/ai_autonomy/blueprint_id 字段"
            "3. 运行生成器 --output-db 验证写入"
            "4. 验证：SELECT stability, ai_autonomy FROM arch_directory_tree LIMIT 5 有值"
            "验收标准：panorama 生成器运行后 arch_directory_tree 表字段完整"
        ),
        files_in_scope=["scripts/governance/generate_project_path_tree.py"],
        deliverables=["panorama 生成器写入完整 arch_directory_tree"],
        acceptance=["生成器运行后 arch_directory_tree stability/ai_autonomy 有值"],
        depends_on=["DM-100102"],
        rollback_instructions="git revert generate_project_path_tree.py",
    )

    create_task(
        conn,
        task_id="DM-100122",
        title="红蓝对抗：depgraph 生成器设计态覆盖测试",
        description=(
            "根因：生成器运行时可能覆盖 depgraph.db 中的设计态数据。虽然代码有 merge_design_fields() 保护，"
            "但需要极端测试验证保护机制在所有边界条件下有效。"
            "治根：设计并执行红蓝对抗测试，验证设计态数据不被覆盖。"
            "施工步骤："
            "1. 蓝方准备：在 depgraph.db nodes 表中插入 design_maturity='design' 的测试节点，"
            "   设置 type_specific_data 包含手动注解的 failure_mode/fallback/interface 字段"
            "2. 红方攻击：运行 generate_project_depgraph.py --output-db，尝试覆盖设计态数据"
            "3. 验证：SELECT 检查设计态节点的手动注解字段是否被保留"
            "4. 极端场景A：设计态节点在磁盘上对应的文件被删除——生成器应保留设计态节点"
            "5. 极端场景B：设计态节点的 domain_id 被手动修改——生成器不应覆盖 domain_id"
            "6. 极端场景C：同时运行两个生成器实例（并发写入）——文件锁应阻止冲突"
            "7. 清理测试数据"
            "验收标准：所有极端场景下设计态数据零丢失"
        ),
        files_in_scope=["scripts/governance/generate_project_depgraph.py", "data/databases/depgraph.db"],
        deliverables=["depgraph 生成器设计态保护红蓝测试报告"],
        acceptance=["设计态数据在所有极端场景下零丢失"],
        depends_on=["DM-100120"],
        rollback_instructions="从备份恢复 depgraph.db",
    )

    create_task(
        conn,
        task_id="DM-100123",
        title="红蓝对抗：panorama 生成器设计态覆盖测试",
        description=(
            "根因：panorama 生成器运行时可能覆盖 arch_directory_tree 中的设计态数据。"
            "虽然代码有 merge_with_design_nodes() 保护，需极端测试验证。"
            "治根：设计并执行红蓝对抗测试。"
            "施工步骤："
            "1. 蓝方准备：在 arch_directory_tree 中插入 state='design' 的测试路径节点"
            "2. 红方攻击：运行 generate_project_path_tree.py --output-db"
            "3. 验证：设计态节点 state/Blueprint_id/stability 不被覆盖"
            "4. 极端场景A：设计态路径在磁盘上不存在——生成器应保留设计态节点"
            "5. 极端场景B：设计态节点的 domain_id 被手动修改——不应覆盖"
            "6. 极端场景C：lifecycle='pending_deletion' 节点——生成器应保留"
            "7. 清理测试数据"
            "验收标准：所有极端场景下设计态数据零丢失"
        ),
        files_in_scope=["scripts/governance/generate_project_path_tree.py", "data/databases/depgraph.db"],
        deliverables=["panorama 生成器设计态保护红蓝测试报告"],
        acceptance=["设计态数据在所有极端场景下零丢失"],
        depends_on=["DM-100121"],
        rollback_instructions="从备份恢复 depgraph.db",
    )

    # ============================================================
    # D组：文档更新（2卡）
    # ============================================================
    print("\n=== D组：文档更新 ===")

    create_task(
        conn,
        task_id="DM-100130",
        title="文档更新：architecture_upgrade_discussion.md 数据库现状说明",
        description=(
            "根因：数据库已完成大更新（9个旧库合并为3个），但架构讨论文档中的数据库章节"
            "仍描述合并前的状态（§19.3 SQLite合并计划列出的旧库名称和大小）。"
            "需要更新文档反映当前实际状态，消除AI读取文档时的幻觉源。"
            "治根：更新文档§19.3和§二十，标注合并已完成，更新实际表数/行数/大小。"
            "施工步骤："
            "1. 更新§19.3 SQLite合并计划：标注'已完成'，更新实际结果"
            "2. 更新§十九数据库架构：governance.db 27表→26表（删除domains后）/depgraph.db 17表→15表（对齐§19.8.7后）"
            "3. 更新§二十讨论进度：添加本次数据库大更新的完成记录"
            "4. 更新D51裁定：标注'已完成，8个空库已删除，42备份已清理'"
            "5. 验证：文档中数字与实际数据库一致"
            "验收标准：文档中 governance.db/depgraph.db 表数/行数与实际一致"
        ),
        files_in_scope=["docs/02_enterprise_architecture/architecture_upgrade_discussion.md"],
        deliverables=["架构文档数据库章节更新为当前实际状态"],
        acceptance=["文档中表数/行数与实际数据库查询结果一致"],
        depends_on=["DM-100100", "DM-100101"],
        rollback_instructions="git revert 文档",
    )

    create_task(
        conn,
        task_id="DM-100131",
        title="文档更新：AI冷启动说明+规则文件数据库路径更新",
        description=(
            "根因：AI冷启动序列（onboarding_detail.md §五）和规则文件中可能引用旧数据库路径。"
            "AI新session进入项目时读取这些文件，如果路径过时会导致AI找不到数据库。"
            "治根：更新所有AI入口文档和规则文件中的数据库路径引用。"
            "施工步骤："
            "1. 检查 .trae/rules/project_rules.md 中的数据库路径引用"
            "2. 检查 .trae/rules/onboarding_detail.md 中的数据库路径引用"
            "3. 检查 AGENTS.md 中的数据库路径引用"
            "4. 更新所有发现的旧路径为 data/databases/governance.db 等正确路径"
            "5. 验证：Grep .trae/rules/ 和 AGENTS.md 确认无旧路径"
            "验收标准：AI入口文档中所有数据库路径指向正确位置"
        ),
        files_in_scope=[".trae/rules/project_rules.md", ".trae/rules/onboarding_detail.md"],
        deliverables=["AI入口文档数据库路径更新"],
        acceptance=["Grep AI入口文档旧路径结果=0"],
        depends_on=["DM-100110"],
        rollback_instructions="git revert 文档",
    )

    # ============================================================
    # E组：四方对齐+集成检查（3卡）
    # ============================================================
    print("\n=== E组：四方对齐+集成检查 ===")

    create_task(
        conn,
        task_id="DM-100140",
        title="四方对齐检查：代码头部[BLUEPRINT]→蓝图→depgraph.db→实际文件",
        description=(
            "根因：架构方案要求四方对齐：代码文件头部[BLUEPRINT]字段 → 蓝图文档 → depgraph.db nodes 表 → 磁盘实际文件。"
            "数据库大更新后，depgraph.db nodes 表可能已重新生成，需要验证四方一致性。"
            "治根：编写并执行四方对齐检查脚本。"
            "施工步骤："
            "1. 扫描 src/zephyr/ 下所有 .py 文件头部 [BLUEPRINT] 字段"
            "2. 对每个 [BLUEPRINT] 检查：蓝图文件是否存在、depgraph.db nodes 表是否有对应记录、磁盘文件路径是否匹配"
            "3. 输出不一致清单：缺失蓝图/orphan节点/路径不匹配"
            "4. 修复可自动修复的不一致（更新 depgraph.db 路径）"
            "5. 验证：四方对齐率 > 95%"
            "验收标准：四方对齐检查脚本 exit 0，不一致项 < 5%"
        ),
        files_in_scope=["data/databases/depgraph.db", "scripts/governance/generate_project_depgraph.py"],
        deliverables=["四方对齐检查脚本+检查报告"],
        acceptance=["四方对齐率 > 95%"],
        depends_on=["DM-100120"],
        rollback_instructions="删除检查脚本",
    )

    create_task(
        conn,
        task_id="DM-100141",
        title="系统集成检查：DatabaseService 事件驱动自动启动验证",
        description=(
            "根因：架构方案D64裁定 DatabaseService 应集成到事件驱动系统（自动启动/自动运行），"
            "任务卡 DM-100050 已创建但状态 PENDING。需要验证当前 DatabaseService 是否能正确连接三个数据库。"
            "治根：编写并执行 DatabaseService 集成测试。"
            "施工步骤："
            "1. 测试 DatabaseService 连接 governance.db：SELECT COUNT(*) FROM tasks"
            "2. 测试 DatabaseService 连接 depgraph.db：SELECT COUNT(*) FROM nodes"
            "3. 测试 DatabaseService 连接 market.duckdb：SELECT COUNT(*) FROM tick_data"
            "4. 测试 DatabaseService 健康检查方法"
            "5. 测试 DatabaseService 在 IDE 启动时自动初始化（ide_health_service.py 集成）"
            "6. 验证：三个数据库均可连接且有数据"
            "验收标准：DatabaseService 三库连接测试全部通过"
        ),
        files_in_scope=["src/zephyr/data/database_service.py", "scripts/ide_health_service.py"],
        deliverables=["DatabaseService 三库连接集成测试报告"],
        acceptance=["三库连接测试全部通过"],
        depends_on=["DM-100102"],
        rollback_instructions="无文件变更，仅测试",
    )

    create_task(
        conn,
        task_id="DM-100142",
        title="系统集成检查：门禁脚本+治理脚本数据库路径统一验证",
        description=(
            "根因：B组修复了路径引用，但需要端到端验证所有门禁和治理脚本能否正确连接数据库。"
            "治根：逐个运行关键门禁脚本验证数据库连接。"
            "施工步骤："
            "1. 运行 python scripts/governance/audit_registration.py --warn-only 验证"
            "2. 运行 python scripts/governance/d5_architecture/validators/validate_cross_references.py --warn-only"
            "3. 运行 python scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py --warn-only"
            "4. 运行 python scripts/governance/run_all.py --dry-run 验证路径"
            "5. 运行 python scripts/governance/phase_a_backup.py --dry-run 验证备份路径"
            "6. 验证：所有脚本 exit 0 或 --warn-only 无数据库连接错误"
            "验收标准：5个关键门禁/治理脚本全部无数据库连接错误"
        ),
        files_in_scope=[
            "scripts/governance/audit_registration.py",
            "scripts/governance/d5_architecture/validators/validate_cross_references.py",
        ],
        deliverables=["门禁脚本数据库连接验证报告"],
        acceptance=["5个关键脚本全部无数据库连接错误"],
        depends_on=["DM-100110", "DM-100111"],
        rollback_instructions="无文件变更，仅测试",
    )

    # ============================================================
    # F组：极端测试方案（3卡）
    # ============================================================
    print("\n=== F组：极端测试方案 ===")

    create_task(
        conn,
        task_id="DM-100150",
        title="极端测试：数据库并发写入+崩溃恢复测试",
        description=(
            "根因：多AI session可能同时写入同一数据库，需要验证文件锁和WAL模式在极端条件下的正确性。"
            "治根：设计并执行并发写入+崩溃恢复极端测试。"
            "施工步骤："
            "1. 并发写入测试：2个进程同时 INSERT 到 governance.db tasks 表，验证无数据丢失"
            "2. WAL模式测试：1个写入进程+1个读取进程同时操作，验证读取不阻塞"
            "3. 崩溃恢复测试：写入过程中 kill 进程，验证数据库不损坏（PRAGMA integrity_check）"
            "4. 锁竞争测试：2个进程同时运行 generate_project_depgraph.py --output-db，验证文件锁互斥"
            "5. 磁盘满模拟：写入大量数据直到接近磁盘限制，验证优雅降级"
            "6. 验证：所有测试场景无数据丢失/损坏"
            "验收标准：并发写入零数据丢失，崩溃恢复后 PRAGMA integrity_check 通过"
        ),
        files_in_scope=["data/databases/governance.db", "data/databases/depgraph.db"],
        deliverables=["并发写入+崩溃恢复极端测试报告"],
        acceptance=["并发零丢失，崩溃恢复 integrity_check 通过"],
        depends_on=["DM-100102"],
        rollback_instructions="从备份恢复数据库",
    )

    create_task(
        conn,
        task_id="DM-100151",
        title="极端测试：depgraph.db 数据完整性边界测试",
        description=(
            "根因：depgraph.db 包含6140 nodes + 7580 edges，需要验证在大规模数据下的查询性能和数据完整性。"
            "治根：设计并执行数据完整性边界测试。"
            "施工步骤："
            "1. 孤儿边检测：SELECT edges 中 from_node/to_node 不在 nodes 表中的记录数"
            "2. 循环依赖检测：BFS/DFS 检测 edges 中的循环路径"
            "3. 域归属一致性：nodes.domain_id 在 domains 表中存在的比例"
            "4. 自引用检测：edges 中 from_node=to_node 的记录"
            "5. 大规模查询性能：SELECT with JOIN nodes+edges+domains 在 6000+ 行上的响应时间 < 1s"
            "6. 外键约束验证：PRAGMA foreign_keys=ON 后 INSERT 违反外键的记录应失败"
            "7. 验证：孤儿边=0，循环依赖可检测，查询性能达标"
            "验收标准：孤儿边=0，域归属一致性>99%，JOIN查询<1s"
        ),
        files_in_scope=["data/databases/depgraph.db"],
        deliverables=["depgraph.db 数据完整性边界测试报告"],
        acceptance=["孤儿边=0，域归属>99%，JOIN<1s"],
        depends_on=["DM-100101"],
        rollback_instructions="无文件变更，仅测试",
    )

    create_task(
        conn,
        task_id="DM-100152",
        title="极端测试：market.duckdb Schema验证+写入管道压力测试",
        description=(
            "根因：market.duckdb 是业务数据库，Schema已建但无数据。需要验证Schema正确性和未来写入管道的承载能力。"
            "治根：验证Schema与§19.7 DDL对齐，执行写入压力测试。"
            "施工步骤："
            "1. Schema对齐检查：对比 market.duckdb 实际表/列与§19.7 DDL定义"
            "2. kline_3s 验证：当前是表还是视图？§19.7 裁定为视图"
            "3. 写入压力测试：INSERT 100万行 tick_data 模拟数据，测量写入吞吐量"
            "4. 分区裁剪测试：SELECT WHERE symbol='000001' AND timestamp>='2026-01-01' 验证分区裁剪生效"
            "5. 并发读写测试：1个写入+1个查询同时操作，验证DuckDB WAL模式"
            "6. 验证：Schema对齐，写入吞吐>2000 rows/sec，分区裁剪生效"
            "验收标准：Schema与§19.7对齐，写入吞吐>2000 rows/sec"
        ),
        files_in_scope=["data/databases/market.duckdb"],
        deliverables=["market.duckdb Schema验证+压力测试报告"],
        acceptance=["Schema对齐，写入>2000 rows/sec"],
        depends_on=[],
        rollback_instructions="DELETE 测试数据或重建 market.duckdb",
    )

    conn.commit()
    conn.close()
    print("\n=== 任务卡创建完成 ===")


if __name__ == "__main__":
    import sys

    sys.exit("DEPRECATED: 此脚本已归档，depgraph.db 已迁移至 PostgreSQL 16")
    main()
