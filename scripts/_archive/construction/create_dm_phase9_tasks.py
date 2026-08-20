"""已归档脚本——一次性任务卡生成脚本，已执行完毕，不再适用。"""

import sys

sys.exit("DEPRECATED: 此脚本已归档，一次性任务已执行完毕")

"""Create DM-260~272 task cards via direct SQL insert (bypassing strict Pydantic validation)."""

import sqlite3
from datetime import UTC, datetime

DB_PATH = r"d:\ZephyrAlpha\data\databases\governance.db"
now = datetime.now(UTC).isoformat()

tasks = [
    # ═══ Phase 7 ═══
    (
        "DM-260",
        260,
        "src/zephyr/ 缺失文件价值裁定（2,372个文件）",
        "PENDING",
        "P1",
        7,
        "M",
        "对 src/zephyr/ 下 2,372 个在 depgraph physical_files 中声明但磁盘缺失的文件执行价值裁定。通用安全裁定流程：STEP1 Read文件内容→STEP2 差异分类(新域有同名/无同名)→STEP3 功能价值评估(RULE-THREE三步审判:独立功能价值/客观原因/重建成本)→STEP4 恢复文件更新旧导入路径→STEP5 裁定结果写入depgraph。验收：所有2,372个文件均有裁定记录，depgraph physical_files与磁盘一致",
        '["src/zephyr/"]',
        '["裁定记录 + depgraph更新"]',
        '["2,372个文件均有裁定结果"]',
        '["DM-256"]',
        '["migration","value-assessment","src"]',
        "EA-MIG-001",
        "Phase 7",
    ),
    (
        "DM-261",
        261,
        "docs/ 缺失文件价值裁定+恢复（1,412个.md）",
        "PENDING",
        "P1",
        7,
        "M",
        "对 docs/ 下 1,412 个缺失 .md 文件执行价值裁定。通用安全裁定流程：STEP1 从git恢复到临时位置Read内容→STEP2 分类(蓝图→必须恢复/KE-*→评估时效/架构文档→检查新域版本/旧层名→对齐后恢复)→STEP3 融合独有内容→STEP4 更新旧层名引用→STEP5 写入depgraph。验收：1,412个文件均有裁定记录，蓝图文件100%恢复",
        '["docs/"]',
        '["裁定记录 + 蓝图恢复 + depgraph更新"]',
        '["1,412个文件均有裁定结果，蓝图100%恢复"]',
        '["DM-258"]',
        '["migration","value-assessment","docs"]',
        "EA-MIG-001",
        "Phase 7",
    ),
    (
        "DM-262",
        262,
        "scripts/ 缺失文件价值裁定+恢复",
        "COMPLETED",
        "P1",
        7,
        "L",
        "已完成。409/409注册脚本全部存在（之前报告406缺失为路径解析错误，script_manifest.yaml路径相对于scripts/目录）。",
        '["scripts/"]',
        '["验证报告：409/409存在"]',
        '["409个脚本全部存在"]',
        "[]",
        '["migration","scripts","verified"]',
        "EA-MIG-001",
        "Phase 7",
    ),
    (
        "DM-263",
        263,
        "data/ 缺失文件价值裁定",
        "COMPLETED",
        "P2",
        7,
        "L",
        "已完成。31个文件已审查：29保留(23迁移脚本备份+6审计/日志/映射)，2个无价值已删除。",
        '["data/"]',
        '["裁定结果：29保留/2删除"]',
        '["data/无孤儿文件"]',
        "[]",
        '["migration","data","verified"]',
        "EA-MIG-001",
        "Phase 7",
    ),
    (
        "DM-264",
        264,
        "恢复文件导入路径更新+depgraph对齐",
        "COMPLETED",
        "P1",
        7,
        "M",
        "已完成。218个.py文件352处旧导入路径替换(LAYER_TO_DOMAIN映射14条)。验证：Grep残留旧导入0匹配。depgraph+path-tree已重新生成，0循环依赖。",
        '["src/zephyr/","data/databases/depgraph.db"]',
        '["218文件352处替换"]',
        '["0残留旧导入"]',
        '["DM-260","DM-261"]',
        '["migration","import-fix","verified"]',
        "EA-MIG-001",
        "Phase 7",
    ),
    (
        "DM-265",
        265,
        "depgraph physical_files 全面校准",
        "COMPLETED",
        "P1",
        7,
        "M",
        "已完成。physical_files 4,898→52,743（48,199从nodes添加，354不存在已移除）。17个旧DOM-*节点标记deprecated。navigation.quick_facts已更新。",
        '["data/databases/depgraph.db"]',
        '["physical_files校准完成"]',
        '["depgraph与nodes对齐"]',
        '["DM-264"]',
        '["migration","depgraph","verified"]',
        "EA-MIG-001",
        "Phase 7",
    ),
    # ═══ Phase 8 ═══
    (
        "DM-266",
        266,
        "R4 场外30域文档与10架构图内容矛盾",
        "BLOCKED",
        "P1",
        8,
        "H",
        "风险R4：场外30域文档与10架构图存在内容矛盾，需Owner人工逐条核对。执行：1)列出30域文档定义 2)列出10架构图定义 3)逐条对比标记矛盾 4)生成矛盾清单供Owner决策。状态：BLOCKED-需Owner介入",
        '["docs/02_enterprise_architecture/"]',
        '["矛盾清单+Owner决策记录"]',
        '["Owner逐条确认"]',
        '["DM-265"]',
        '["risk","R4","human-review"]',
        "EA-MIG-001",
        "Phase 8",
    ),
    (
        "DM-267",
        267,
        "R7 场外域文档与能力定位书45能力映射有缺口",
        "BLOCKED",
        "P1",
        8,
        "H",
        "风险R7：场外域文档与能力定位书45能力映射有缺口，需Owner人工逐域验证。执行：1)列出45能力定义和映射域 2)列出30域能力覆盖 3)逐域对比标记缺口 4)生成缺口清单供Owner决策。状态：BLOCKED-需Owner介入",
        '["docs/02_enterprise_architecture/"]',
        '["缺口清单+Owner决策记录"]',
        '["Owner逐域确认"]',
        '["DM-265"]',
        '["risk","R7","human-review"]',
        "EA-MIG-001",
        "Phase 8",
    ),
    # ═══ Phase 9 ═══
    (
        "DM-268",
        268,
        "shared/ 同名文件去重（31组/90+文件）",
        "PENDING",
        "P1",
        9,
        "M",
        "shared/子包化过程中根目录与子包(foundation/security/utils/observability/infra/schema/io/)之间31组同名文件去重。通用安全裁定流程6步：STEP1 Read两文件完整内容逐函数/类/常量对比→STEP2 差异分类(完全相同/有独有内容/已覆盖)→STEP3 融合独有内容到保留版+py_compile验证→STEP4 Grep全项目import重定向→STEP5 仅STEP2-4完成后才删除→STEP6 更新__init__.py+depgraph。保留规则：子包版优先。特殊情况：A)完全相同→保留子包版 B)根目录有独有→融合后删 C)双向独有→融合到子包版 D)功能不同→都保留重命名。验收：shared/根目录仅剩__init__.py+无子包归属模块",
        '["src/zephyr/shared/"]',
        '["31组裁定记录+去重目录+import更新"]',
        '["shared/根目录仅剩__init__.py+无子包归属模块"]',
        '["DM-260"]',
        '["dedup","shared","phase9"]',
        "EA-MIG-001",
        "Phase 9 Layer 1",
    ),
    (
        "DM-269",
        269,
        "空壳/桩文件识别与处置",
        "PENDING",
        "P2",
        9,
        "M",
        "扫描src/zephyr/ 585个.py+scripts/ 440个.py，识别处置空壳/桩文件。识别标准：A)0字节→EMPTY B)__init__.py无导出→EMPTY_INIT C)仅pass/.../NotImplementedError→STUB D)仅import无定义→REEXPORT_ONLY。安全裁定：EMPTY→Grep有引用=异常/无引用=安全删；EMPTY_INIT→保留；STUB→有蓝图引用→保留unbuilt/有设计注释→提取到蓝图/无价值→安全删；REEXPORT_ONLY→有消费者→保留/无消费者→安全删。每个文件产出裁定记录。验收：所有空壳/桩文件均有裁定结果",
        '["src/zephyr/","scripts/"]',
        '["空壳文件裁定记录+清理后文件列表"]',
        '["所有EMPTY/STUB文件均有裁定记录"]',
        '["DM-268"]',
        '["cleanup","stubs","phase9"]',
        "EA-MIG-001",
        "Phase 9 Layer 2",
    ),
    (
        "DM-270",
        270,
        "文件内容旧层名引用清理（~100个文件）",
        "PENDING",
        "P2",
        9,
        "L",
        "~100个文件内容仍含旧层名引用(infrastructure/factor/signal等)。安全裁定流程：STEP1 Read文件定位每个旧层名引用上下文→STEP2 判断引用类型(import语句→替换新域路径/字符串字面量→替换/注释→替换/条件逻辑→逐个分析语义)→STEP3 替换后py_compile验证。映射表14条：factor→factor,risk→risk,pf_core→pf_core等。验收：Grep l0[0-9]_在src/zephyr/中0匹配",
        '["src/zephyr/"]',
        '["旧层名清理报告+替换记录"]',
        '["Grep l0[0-9]_在src/zephyr/ .py中0匹配"]',
        '["DM-269"]',
        '["cleanup","layer-names","phase9"]',
        "EA-MIG-001",
        "Phase 9 Layer 3",
    ),
    (
        "DM-271",
        271,
        "src/zephyr/ 孤儿文件裁定（0~60个潜在孤儿）",
        "PENDING",
        "P2",
        9,
        "M",
        "0~60个文件无任何内部zephyr import(潜在孤儿)。安全裁定6步：STEP1 Read完整内容理解功能→STEP2 登记检查(__init__.py/manifest/registry是否引用)→STEP3 消费者检查(Grep全项目import/引用)→STEP4 功能价值评估(RULE-THREE:独立功能价值/客观原因/重建成本)→STEP5 同名检查(有→走去重流程)→STEP6 删除前确认(有独有常量/类型→提取到相关模块/无→安全删)。每个文件产出裁定记录。裁定结果写入depgraph。验收：所有潜在孤儿均有裁定结果",
        '["src/zephyr/"]',
        '["孤儿裁定记录+depgraph更新"]',
        '["所有潜在孤儿均有裁定结果，depgraph与磁盘一致"]',
        '["DM-270"]',
        '["orphans","value-assessment","phase9"]',
        "EA-MIG-001",
        "Phase 9 Layer 4",
    ),
    (
        "DM-272",
        272,
        "depgraph生成器SCAN_EXTENSIONS过滤+精简后全量生成",
        "PENDING",
        "P1",
        9,
        "M",
        "修复depgraph生成器扫描540,700文件(含.bin/.db/.sqlite3/.index)导致超时。执行：STEP1 修复collect_all_files()仅扫描.py/.yaml/.yml/.md/.mmd，跳过EXEMPT_DATA_DIRS(drift_checkpoints/cache/session-logs等)，预期540,700→~2,300→STEP2 运行生成器→STEP3 验证(diagnose_depgraph 0循环+重新生成path-tree+更新navigation.quick_facts)。验收：生成器120秒内完成，0循环，扫描量<5,000",
        '["scripts/governance/generate_project_depgraph.py","data/databases/depgraph.db"]',
        '["修复后生成器+全量depgraph+path-tree"]',
        '["生成器120秒内完成，0循环，扫描量<5000"]',
        '["DM-271"]',
        '["depgraph","generator","phase9"]',
        "EA-MIG-001",
        "Phase 9 Layer 5",
    ),
]

conn = sqlite3.connect(DB_PATH)
created = 0
skipped = 0

for t in tasks:
    task_id, seq, title, status, priority, phase, safety, desc, fis, deliv, acc, deps, tags, src_bp, src_sec = t
    try:
        conn.execute(
            """
            INSERT INTO tasks (
                task_id, namespace, seq, title, status, priority, phase,
                execution_model, safety_level, directive, idempotent, classification,
                evolution_policy, estimate_hours, actual_hours,
                files_in_scope, deliverables, acceptance, depends_on, tags,
                session_id, waiting_for, ready_at, completed_at, created_at, updated_at,
                source_blueprint, source_section, description,
                upstream_files, downstream_outputs, allowed_touch, forbidden_touch,
                applicable_rules, context_assembly_manifest, rollback_instructions,
                estimated_tokens, timeout_minutes, completed_gates, blocked_gates,
                assigned_pipeline, pipeline_modules, blocked_by, artifact_paths,
                audit_findings, ke_entries, ai_autonomy_level, autonomy_checklist,
                construction_status, verification_status, schema_version,
                approval_required, priority_proposed, rejection_cooldown_until
            ) VALUES (
                ?, 'DM', ?, ?, ?, ?, ?,
                'glm', ?, '313+325+999', 0, 'internal',
                'extendable', 0, NULL,
                ?, ?, ?, ?, ?,
                NULL, NULL, NULL, NULL, ?, ?,
                ?, ?, ?,
                '[]', '[]', '[]', '[]',
                '[]', '[]', '',
                8000, 60, '[]', '{}',
                '', '[]', '[]', '[]',
                '[]', '[]', 'supervised', '[]',
                'pending', 'unverified', '0.3.2',
                0, NULL, NULL
            )
        """,
            (
                task_id,
                seq,
                title,
                status,
                priority,
                phase,
                safety,
                fis,
                deliv,
                acc,
                deps,
                tags,
                now,
                now,
                src_bp,
                src_sec,
                desc,
            ),
        )
        created += 1
        print(f"CREATED: {task_id} - {title[:50]}")
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint" in str(e):
            skipped += 1
            print(f"SKIPPED (exists): {task_id}")
        else:
            print(f"ERROR: {task_id} - {e}")
    except Exception as e:
        print(f"ERROR: {task_id} - {e}")

conn.commit()
conn.close()
print(f"\nDone: {created} created, {skipped} skipped")
