#!/usr/bin/env python3
"""
# [BLUEPRINT] MOD-INF-005 | scripts/governance/create_alignment_tasks.py | §7
# [MODULE] scripts.governance.create_alignment_tasks
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.task_repo
# [CONSUMERS] governance automation; alignment workflow
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] MUST NOT modify any file except task database; MUST create all tasks via TaskRepository
# [MODIFY-GUARD] task database only
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TaskRepositoryError
# [TESTS] tests/test_create_alignment_tasks.py
# [TTL] task_bound
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from zephyr.governance.persistence.task_repo import Task, TaskRepository

BATCH_ID = "ALIGN-BATCH-001"
SOURCE_BP = "MOD-INF-005"

TASKS = [
    {
        "task_id": "TASK-ALN-0001",
        "title": "Phase1.1: 孤儿节点分类与处置——50个module孤儿",
        "description": "诊断报告中50个module类型孤儿节点（无入边无出边）需要逐个分析：有功能价值的接通（添加import/引用），无功能价值的标记为待删除。每个孤儿必须过RULE-THREE三步审判。",
        "priority": "P1",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19.4",
        "upstream_files": [
            str(PROJECT_ROOT / "data" / "asset_index" / "depgraph-diagnosis.yaml"),
            "depgraph (PostgreSQL) (localhost:5432/depgraph)",
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "data" / "asset_index" / "orphan-disposition.yaml"),
                "desc": "孤儿处置决议：接通/保留/删除",
            },
        ],
        "allowed_touch": [
            "src/zephyr/**/__init__.py",
            "src/zephyr/**/*.py",
        ],
        "forbidden_touch": [
            "scripts/governance/generate_project_depgraph.py",
            "docs/02_enterprise_architecture/system-dependency-map.md",
        ],
        "applicable_rules": [
            {"module_id": "RULE-THREE", "section": "§3", "reason": "删除前必须过三步审判"},
            {"module_id": "RULE-TWO", "section": "§2", "reason": "接通后必须有消费者"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "data" / "asset_index" / "depgraph-diagnosis.yaml"),
                "reason": "孤儿节点清单",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["diagnose", "decide", "execute", "verify"],
        "estimated_tokens": 15000,
        "timeout_minutes": 60,
        "acceptance_criteria": [
            "AC1: 50个孤儿节点全部有处置决议（接通/保留/删除）",
            "AC2: 接通的孤儿在depgraph中有至少1条入边或出边",
            "AC3: 删除的孤儿经过RULE-THREE三步审判并记录结论",
            "AC4: orphan-disposition.yaml 包含50条记录",
            "AC5: 重新运行diagnose_depgraph.py验证孤儿数减少",
        ],
        "rollback_instructions": "恢复被删除的文件（git checkout），移除添加的import语句",
        "depends_on": [],
        "status": "PENDING",
        "tags_fn": ["governance", "alignment"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-005"],
    },
    {
        "task_id": "TASK-ALN-0002",
        "title": "Phase1.2: 补齐984个空blueprint_id文件归属",
        "description": "诊断报告中984个节点blueprint_id为空。需要：1)按目录路径推导归属蓝图 2)对无法自动推导的文件手动指定 3)更新文件头[BLUEPRINT]字段 4)验证depgraph中空blueprint_id降为0",
        "priority": "P0",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19.1",
        "upstream_files": [
            str(PROJECT_ROOT / "data" / "asset_index" / "depgraph-diagnosis.yaml"),
            str(PROJECT_ROOT / "scripts" / "governance" / "add_file_headers.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "data" / "asset_index" / "empty-blueprint-fix-report.yaml"),
                "desc": "修复报告：每个文件的blueprint_id赋值",
            },
        ],
        "allowed_touch": [
            "src/zephyr/**/*.py",
            "scripts/**/*.py",
            "tests/**/*.py",
            "data/**/*.yaml",
            "config/**/*.yaml",
        ],
        "forbidden_touch": [
            "docs/02_enterprise_architecture/system-dependency-map.md",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入文件前必须获取锁"},
            {"module_id": "GOV-ENG-002", "section": "§5", "reason": "头字段格式规范"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "scripts" / "governance" / "add_file_headers.py"),
                "reason": "已有DIR_TO_BLUEPRINT映射表",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["scan", "classify", "assign", "write", "verify"],
        "estimated_tokens": 25000,
        "timeout_minutes": 120,
        "acceptance_criteria": [
            "AC1: 984个空blueprint_id文件全部赋值",
            "AC2: 每个赋值都有目录路径推导依据或手动指定记录",
            "AC3: 重新运行generate_project_depgraph.py验证空blueprint_id=0",
            "AC4: 重新运行diagnose_depgraph.py验证empty_blueprint_id=0",
            "AC5: 修改后的文件语法正确（python -c compile验证）",
        ],
        "rollback_instructions": "git checkout恢复所有被修改的文件头",
        "depends_on": [],
        "status": "PENDING",
        "tags_fn": ["governance", "alignment"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-005"],
    },
    {
        "task_id": "TASK-ALN-0003",
        "title": "Phase1.3a: 打破4个__init__.py自循环依赖",
        "description": "4个__init__.py文件存在自导入循环：asset_inventory/__init__.py, core/__init__.py, gates/ai_capability_guard.py, scripts/rollback.py。删除自导入语句即可修复。",
        "priority": "P1",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "data" / "asset_index" / "depgraph-diagnosis.yaml"),
        ],
        "downstream_outputs": [
            {"path": str(PROJECT_ROOT / "src" / "zephyr" / "asset-inventory" / "__init__.py"), "desc": "移除自导入"},
            {"path": str(PROJECT_ROOT / "src" / "zephyr" / "core" / "__init__.py"), "desc": "移除自导入"},
            {"path": str(PROJECT_ROOT / "src" / "zephyr" / "gates" / "ai_capability_guard.py"), "desc": "移除自导入"},
            {"path": str(PROJECT_ROOT / "scripts" / "rollback.py"), "desc": "移除自导入"},
        ],
        "allowed_touch": [
            "src/zephyr/asset-inventory/__init__.py",
            "src/zephyr/core/__init__.py",
            "src/zephyr/gates/ai_capability_guard.py",
            "scripts/rollback.py",
        ],
        "forbidden_touch": ["**/*.py"],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "data" / "asset_index" / "depgraph-diagnosis.yaml"),
                "reason": "循环依赖清单",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "fix", "verify"],
        "estimated_tokens": 5000,
        "timeout_minutes": 30,
        "acceptance_criteria": [
            "AC1: 4个文件的自导入语句已移除",
            "AC2: python -c 'import zephyr' 不报错",
            "AC3: 重新运行diagnose_depgraph.py验证自循环=0",
        ],
        "rollback_instructions": "git checkout恢复4个文件",
        "depends_on": [],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-005"],
    },
    {
        "task_id": "TASK-ALN-0004",
        "title": "Phase1.3b: 打破escalation_engine内部循环依赖",
        "description": "escalation-engine/__init__.py与adapter.py、self_test.py之间有2条循环：__init__↔adapter, self_test↔__init__。修复方案：__init__.py改用延迟导入（lazy import），self_test.py改为直接import adapter而非通过__init__。",
        "priority": "P1",
        "source_blueprint": "MOD-INF-022",
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "escalation-engine" / "__init__.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "escalation-engine" / "adapter.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "escalation-engine" / "self_test.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "escalation-engine" / "__init__.py"),
                "desc": "改为延迟导入",
            },
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "escalation-engine" / "self_test.py"),
                "desc": "直接import adapter",
            },
        ],
        "allowed_touch": [
            "src/zephyr/escalation-engine/__init__.py",
            "src/zephyr/escalation-engine/self_test.py",
        ],
        "forbidden_touch": [
            "src/zephyr/escalation-engine/adapter.py",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
            {"module_id": "RULE-ONE", "section": "§1", "reason": "原子写入"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "escalation-engine" / "__init__.py"),
                "reason": "当前导入结构",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "refactor", "verify"],
        "estimated_tokens": 8000,
        "timeout_minutes": 30,
        "acceptance_criteria": [
            "AC1: escalation_engine包可正常import无循环",
            "AC2: python -c 'from zephyr.governance.escalation import EscalationEngine' 成功",
            "AC3: diagnose_depgraph.py验证该循环消失",
        ],
        "rollback_instructions": "git checkout恢复__init__.py和self_test.py",
        "depends_on": ["TASK-ALN-0003"],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-022"],
    },
    {
        "task_id": "TASK-ALN-0005",
        "title": "Phase1.3c: 打破llm_security↔self_protection循环依赖",
        "description": "llm-security/gateway.py与self_protection/l7_validation.py双向import。修复方案：提取公共接口到llm_security/protocol.py（已存在），gateway.py和l7_validation.py都只依赖protocol.py，不直接互相import。",
        "priority": "P1",
        "source_blueprint": "MOD-LLM_SECURITY",
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "llm-security" / "gateway.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "llm-security" / "protocol.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "llm-security" / "gateway.py"),
                "desc": "移除对l7_validation的直接import",
            },
        ],
        "allowed_touch": [
            "src/zephyr/llm-security/gateway.py",
        ],
        "forbidden_touch": [
            "src/zephyr/llm-security/protocol.py",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "llm-security" / "gateway.py"),
                "reason": "当前导入结构",
            },
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "llm-security" / "protocol.py"),
                "reason": "已有接口定义",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "refactor", "verify"],
        "estimated_tokens": 8000,
        "timeout_minutes": 30,
        "acceptance_criteria": [
            "AC1: gateway.py不再直接import l7_validation",
            "AC2: python -c 'from zephyr.security.llm_defense.llm_security import gateway' 成功",
            "AC3: diagnose_depgraph.py验证该循环消失",
        ],
        "rollback_instructions": "git checkout恢复gateway.py",
        "depends_on": ["TASK-ALN-0003"],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-LLM_SECURITY"],
    },
    {
        "task_id": "TASK-ALN-0006",
        "title": "Phase1.3d: 打破telemetry内部循环依赖",
        "description": "telemetry/traces/span_stub.py与logs/structured_sink.py双向import。修复方案：提取公共event定义到telemetry/event_types.py，两个模块都只依赖event_types。",
        "priority": "P1",
        "source_blueprint": "MOD-INF-027",
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "telemetry" / "traces" / "span_stub.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "telemetry" / "logs" / "structured_sink.py"),
        ],
        "downstream_outputs": [
            {"path": str(PROJECT_ROOT / "src" / "zephyr" / "telemetry" / "event_types.py"), "desc": "公共event定义"},
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "telemetry" / "traces" / "span_stub.py"),
                "desc": "改为import event_types",
            },
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "telemetry" / "logs" / "structured_sink.py"),
                "desc": "改为import event_types",
            },
        ],
        "allowed_touch": [
            "src/zephyr/telemetry/traces/span_stub.py",
            "src/zephyr/telemetry/logs/structured_sink.py",
        ],
        "forbidden_touch": [],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
            {"module_id": "RULE-FOUR", "section": "§2", "reason": "新文件通过scaffold.py创建"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "telemetry" / "traces" / "span_stub.py"),
                "reason": "当前导入结构",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "extract", "refactor", "verify"],
        "estimated_tokens": 10000,
        "timeout_minutes": 45,
        "acceptance_criteria": [
            "AC1: span_stub.py和structured_sink.py不再互相import",
            "AC2: event_types.py包含提取的公共定义",
            "AC3: python -c 'from zephyr.trading.feedback_loop.telemetry.traces import span_stub' 成功",
            "AC4: diagnose_depgraph.py验证该循环消失",
        ],
        "rollback_instructions": "git checkout恢复3个文件，删除event_types.py",
        "depends_on": ["TASK-ALN-0003"],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-027"],
    },
    {
        "task_id": "TASK-ALN-0007",
        "title": "Phase1.3e: 打破system_telemetry→rollback→budget_enforcer关键5节点循环",
        "description": "最长循环：system_telemetry/auto_bootstrap.py→rollback/phase_manager.py→rollback/phase_check_registry.py→budget_enforcer/__init__.py→budget_enforcer/budget_engine.py→system_telemetry。这是最关键的循环——3个基础设施模块互相依赖导致启动顺序死锁。修复方案：phase_check_registry改为注册制（不直接import budget_engine），budget_engine通过事件通知system_telemetry而非直接import。",
        "priority": "P0",
        "source_blueprint": "MOD-INF-015",
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "observability" / "telemetry" / "auto_bootstrap.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "rollback" / "phase_manager.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "rollback" / "phase_check_registry.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "budget-enforcer" / "__init__.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "budget-enforcer" / "budget_engine.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "rollback" / "phase_check_registry.py"),
                "desc": "改为注册制",
            },
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "budget-enforcer" / "budget_engine.py"),
                "desc": "移除对system_telemetry的直接import",
            },
        ],
        "allowed_touch": [
            "src/zephyr/rollback/phase_check_registry.py",
            "src/zephyr/budget-enforcer/budget_engine.py",
            "src/zephyr/observability/telemetry/auto_bootstrap.py",
        ],
        "forbidden_touch": [
            "src/zephyr/rollback/phase_manager.py",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
            {"module_id": "RULE-ONE", "section": "§1", "reason": "原子写入"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "rollback" / "phase_check_registry.py"),
                "reason": "当前注册机制",
            },
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "budget-enforcer" / "budget_engine.py"),
                "reason": "当前对system_telemetry的依赖",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "analyze", "refactor", "verify"],
        "estimated_tokens": 20000,
        "timeout_minutes": 90,
        "acceptance_criteria": [
            "AC1: phase_check_registry不再直接import budget_engine",
            "AC2: budget_engine不再直接import system-telemetry",
            "AC3: python -c 'import zephyr; zephyr.init()' 成功（无循环导入错误）",
            "AC4: diagnose_depgraph.py验证该5节点循环消失",
            "AC5: rollback/phase_manager.py功能不受影响",
        ],
        "rollback_instructions": "git checkout恢复3个修改的文件",
        "depends_on": ["TASK-ALN-0003"],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-015", "MOD-INF-024"],
    },
    {
        "task_id": "TASK-ALN-0008",
        "title": "Phase1.3f: 打破model_profiler→budget_enforcer循环依赖",
        "description": "model-profiler/profiler.py→model_discovery.py→budget_enforcer/model_router.py→model_profiler/results_writer.py→profiler.py。修复方案：提取model_router接口到model_profiler/model_router_interface.py，budget_enforcer只依赖接口不依赖实现。",
        "priority": "P1",
        "source_blueprint": "MOD-INF-034",
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "model-profiler" / "profiler.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "model-profiler" / "model_discovery.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "budget-enforcer" / "model_router.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "model-profiler" / "model_router_interface.py"),
                "desc": "提取的接口",
            },
        ],
        "allowed_touch": [
            "src/zephyr/model-profiler/profiler.py",
            "src/zephyr/model-profiler/model_discovery.py",
            "src/zephyr/budget-enforcer/model_router.py",
        ],
        "forbidden_touch": [],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "budget-enforcer" / "model_router.py"),
                "reason": "当前依赖结构",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "extract", "refactor", "verify"],
        "estimated_tokens": 12000,
        "timeout_minutes": 60,
        "acceptance_criteria": [
            "AC1: budget-enforcer/model_router.py不再import model-profiler",
            "AC2: python -c 'from zephyr.intelligence.model_profiling import profiler' 成功",
            "AC3: diagnose_depgraph.py验证该循环消失",
        ],
        "rollback_instructions": "git checkout恢复3个文件，删除model_router_interface.py",
        "depends_on": ["TASK-ALN-0003"],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-034"],
    },
    {
        "task_id": "TASK-ALN-0009",
        "title": "Phase1.3g: 打破kb↔storage循环和agent_spec↔pipeline循环",
        "description": "两个独立循环：1)kb/unified_memory_api↔storage/unified_memory_api↔kb/vms_memory_backend 2)agent_spec/skill_feedback↔pipeline/pipeline_orchestrator。循环1修复：统一为一个模块（storage是kb的子包，不应有双向依赖）。循环2修复：skill_feedback通过事件通知pipeline而非直接import。",
        "priority": "P1",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "kb" / "unified_memory_api.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "agent-spec" / "skill_feedback.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "kb" / "unified_memory_api.py"),
                "desc": "移除对storage的反向import",
            },
            {"path": str(PROJECT_ROOT / "src" / "zephyr" / "agent-spec" / "skill_feedback.py"), "desc": "改为事件通知"},
        ],
        "allowed_touch": [
            "src/zephyr/kb/unified_memory_api.py",
            "src/zephyr/kb/vms_memory_backend.py",
            "src/zephyr/agent-spec/skill_feedback.py",
        ],
        "forbidden_touch": [
            "src/zephyr/pipeline/pipeline_orchestrator.py",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "kb" / "unified_memory_api.py"),
                "reason": "当前双向依赖",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "refactor", "verify"],
        "estimated_tokens": 12000,
        "timeout_minutes": 60,
        "acceptance_criteria": [
            "AC1: kb不再import storage包",
            "AC2: agent_spec不再import pipeline",
            "AC3: python -c 'from zephyr.governance.knowledge_management.kb import unified_memory_api' 成功",
            "AC4: diagnose_depgraph.py验证2个循环消失",
        ],
        "rollback_instructions": "git checkout恢复3个文件",
        "depends_on": ["TASK-ALN-0003"],
        "status": "PENDING",
        "tags_fn": ["governance", "circular-dep"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-KB-001", "MOD-INF-019"],
    },
    {
        "task_id": "TASK-ALN-0010",
        "title": "Phase1.4: 修复3条跨层直接引用(L06→L04)",
        "description": "ex_core/execution_engine.py直接import risk/implementations/default_risk_validator.py，跳过了L05层。修复方案：execution_engine通过risk/risk_validator.py（公共接口）间接引用，不直接import implementations内部模块。",
        "priority": "P1",
        "source_blueprint": "MOD-L06-001",
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "src" / "zephyr" / "ex_core" / "execution_engine.py"),
            str(PROJECT_ROOT / "src" / "zephyr" / "risk" / "risk_validator.py"),
        ],
        "downstream_outputs": [
            {
                "path": str(PROJECT_ROOT / "src" / "zephyr" / "ex_core" / "execution_engine.py"),
                "desc": "改为通过公共接口引用",
            },
        ],
        "allowed_touch": [
            "src/zephyr/ex_core/execution_engine.py",
            "tests/ex_core/test_execution_engine_unit.py",
            "tests/ex_core/test_execution_engine_deep.py",
        ],
        "forbidden_touch": [
            "src/zephyr/risk/**",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "ex_core" / "execution_engine.py"),
                "reason": "当前跨层import",
            },
            {
                "file_path": str(PROJECT_ROOT / "src" / "zephyr" / "risk" / "risk_validator.py"),
                "reason": "应使用的公共接口",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["read", "refactor", "verify"],
        "estimated_tokens": 8000,
        "timeout_minutes": 30,
        "acceptance_criteria": [
            "AC1: execution_engine.py不再import l04的implementations子包",
            "AC2: 通过l04的公共接口risk_validator.py间接引用",
            "AC3: python -c 'from zephyr.ex_core import execution_engine' 成功",
            "AC4: diagnose_depgraph.py验证cross_layer_references=0",
        ],
        "rollback_instructions": "git checkout恢复execution_engine.py",
        "depends_on": ["TASK-ALN-0007"],
        "status": "PENDING",
        "tags_fn": ["governance", "cross-layer"],
        "tags_ly": "L06",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-L06-001"],
    },
    {
        "task_id": "TASK-ALN-0011",
        "title": "Phase1.5a: 补齐directory-registry.md 500个缺登记目录",
        "description": "磁盘上存在500+个目录未在directory-registry.md中登记。需要扫描磁盘目录、与注册表对比、补登记缺失项。每个目录登记需包含：path, owner_blueprint, category, status。",
        "priority": "P1",
        "source_blueprint": "PS-REG-012",
        "source_section": "§19",
        "upstream_files": [
            str(
                PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "directory-registry.md"
            ),
        ],
        "downstream_outputs": [
            {
                "path": str(
                    PROJECT_ROOT
                    / "docs"
                    / "01_policies_and_standards"
                    / "_registry"
                    / "catalogs"
                    / "directory-registry.md"
                ),
                "desc": "补登记后的完整注册表",
            },
        ],
        "allowed_touch": [
            "docs/01_policies_and_standards/_registry/catalogs/directory-registry.md",
        ],
        "forbidden_touch": [],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
            {"module_id": "PS-REG-012", "section": "§4", "reason": "注册表格式规范"},
        ],
        "context_assembly_manifest": [
            {
                "file_path": str(
                    PROJECT_ROOT
                    / "docs"
                    / "01_policies_and_standards"
                    / "_registry"
                    / "catalogs"
                    / "directory-registry.md"
                ),
                "reason": "当前注册表",
            },
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["scan", "diff", "register", "verify"],
        "estimated_tokens": 15000,
        "timeout_minutes": 60,
        "acceptance_criteria": [
            "AC1: 磁盘上所有scan_dirs下的目录都在directory-registry.md中登记",
            "AC2: 每个登记项包含path, owner_blueprint, category, status",
            "AC3: YAML格式正确（python -c 'import yaml; yaml.safe_load(...)'验证）",
        ],
        "rollback_instructions": "git checkout恢复directory-registry.md",
        "depends_on": ["TASK-ALN-0002"],
        "status": "PENDING",
        "tags_fn": ["governance", "registry"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["PS-REG-012"],
    },
    {
        "task_id": "TASK-ALN-0012",
        "title": "Phase1.5b: 补齐script_manifest.yaml缺登记脚本",
        "description": "scripts/目录下的.py文件与script_manifest.yaml登记项对比，补登记缺失脚本。每个登记需包含：name, path, description, domain, execution_plane, status, timeout_seconds, dimensions。",
        "priority": "P1",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19",
        "upstream_files": [
            str(PROJECT_ROOT / "scripts" / "script_manifest.yaml"),
        ],
        "downstream_outputs": [
            {"path": str(PROJECT_ROOT / "scripts" / "script_manifest.yaml"), "desc": "补登记后的完整清单"},
        ],
        "allowed_touch": [
            "scripts/script_manifest.yaml",
        ],
        "forbidden_touch": [],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [
            {"file_path": str(PROJECT_ROOT / "scripts" / "script_manifest.yaml"), "reason": "当前清单"},
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["scan", "diff", "register", "verify"],
        "estimated_tokens": 10000,
        "timeout_minutes": 45,
        "acceptance_criteria": [
            "AC1: scripts/下所有.py文件都在script_manifest.yaml中登记",
            "AC2: 每个登记项字段完整",
            "AC3: YAML格式正确",
        ],
        "rollback_instructions": "git checkout恢复script_manifest.yaml",
        "depends_on": [],
        "status": "PENDING",
        "tags_fn": ["governance", "registry"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-005"],
    },
    {
        "task_id": "TASK-ALN-0013",
        "title": "Phase1.6: 修SyntaxWarning——脚本文件中的无效转义序列",
        "description": r"约30个脚本文件包含invalid escape sequence '\\Z'警告。这些文件使用了docstring中的\\Z（应为\\\\Z或r-string）。需要逐个修复。",
        "priority": "P2",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19",
        "upstream_files": [],
        "downstream_outputs": [
            {"path": str(PROJECT_ROOT / "data" / "asset_index" / "syntax-warning-fix-report.yaml"), "desc": "修复报告"},
        ],
        "allowed_touch": [
            "scripts/**/*.py",
            "src/zephyr/**/*.py",
        ],
        "forbidden_touch": [
            "docs/**",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
        ],
        "context_assembly_manifest": [],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["scan", "fix", "verify"],
        "estimated_tokens": 10000,
        "timeout_minutes": 45,
        "acceptance_criteria": [
            "AC1: python -W error编译所有修复的文件不报SyntaxWarning",
            "AC2: 修复后的文件功能不变（docstring内容不变）",
        ],
        "rollback_instructions": "git checkout恢复所有修改的文件",
        "depends_on": [],
        "status": "PENDING",
        "tags_fn": ["governance", "syntax"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-005"],
    },
    {
        "task_id": "TASK-ALN-0014",
        "title": "Phase1.7: 全量头字段对齐——补齐[CONSUMERS][INVARIANTS][ERROR_CONTRACT][TESTS]",
        "description": "2217个文件已添加基础头字段，但[CONSUMERS]/[INVARIANTS]/[ERROR_CONTRACT]/[TESTS]仍为空。需要：1)从depgraph提取每个文件的消费者列表填入[CONSUMERS] 2)从蓝图提取不变量填入[INVARIANTS] 3)从代码提取异常类型填入[ERROR_CONTRACT] 4)从tests/提取测试文件映射填入[TESTS]。",
        "priority": "P2",
        "source_blueprint": "GOV-ENG-002",
        "source_section": "§5",
        "upstream_files": [
            "depgraph (PostgreSQL) (localhost:5432/depgraph)",
        ],
        "downstream_outputs": [
            {"path": str(PROJECT_ROOT / "data" / "asset_index" / "header-alignment-report.yaml"), "desc": "对齐报告"},
        ],
        "allowed_touch": [
            "src/zephyr/**/*.py",
            "scripts/**/*.py",
        ],
        "forbidden_touch": [
            "docs/**",
        ],
        "applicable_rules": [
            {"module_id": "RULE-ZERO", "section": "§1", "reason": "写入前获取锁"},
            {"module_id": "GOV-ENG-002", "section": "§5", "reason": "头字段格式规范"},
        ],
        "context_assembly_manifest": [
            {"file_path": "depgraph (PostgreSQL) (localhost:5432/depgraph)", "reason": "消费者关系数据"},
        ],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["extract", "fill", "verify"],
        "estimated_tokens": 40000,
        "timeout_minutes": 180,
        "acceptance_criteria": [
            "AC1: 所有.py文件的[CONSUMERS]字段非空（至少有1个消费者或标记为'none'）",
            "AC2: 所有.py文件的[ERROR_CONTRACT]字段包含代码中实际raise的异常类型",
            "AC3: 所有.py文件的[TESTS]字段包含对应测试文件路径",
            "AC4: 修改后的文件语法正确",
        ],
        "rollback_instructions": "git checkout恢复所有修改的文件",
        "depends_on": ["TASK-ALN-0002", "TASK-ALN-0007", "TASK-ALN-0008", "TASK-ALN-0009"],
        "status": "PENDING",
        "tags_fn": ["governance", "alignment"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["GOV-ENG-002"],
    },
    {
        "task_id": "TASK-ALN-0015",
        "title": "Phase1.8: 最终验证——重新生成依赖图+全量脚本检查",
        "description": "所有修复完成后：1)重新运行generate_project_depgraph.py 2)重新运行diagnose_depgraph.py 3)验证循环依赖=0 4)验证空blueprint_id=0 5)验证跨层引用=0 6)更新system-dependency-map.md §19 7)运行所有脚本--warn-only验证。",
        "priority": "P0",
        "source_blueprint": SOURCE_BP,
        "source_section": "§19",
        "upstream_files": [],
        "downstream_outputs": [
            {"path": "depgraph (PostgreSQL) (localhost:5432/depgraph)", "desc": "最终依赖图"},
            {"path": str(PROJECT_ROOT / "data" / "asset_index" / "depgraph-diagnosis.yaml"), "desc": "最终诊断报告"},
            {
                "path": str(PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "system-dependency-map.md"),
                "desc": "更新的§19",
            },
        ],
        "allowed_touch": [
            "depgraph (PostgreSQL) (localhost:5432/depgraph)",
            "data/asset_index/depgraph-diagnosis.yaml",
            "docs/02_enterprise_architecture/system-dependency-map.md",
        ],
        "forbidden_touch": [
            "src/zephyr/**",
            "scripts/**",
        ],
        "applicable_rules": [],
        "context_assembly_manifest": [],
        "assigned_model": "deepseek",
        "assigned_pipeline": "A",
        "pipeline_modules": ["generate", "diagnose", "verify", "report"],
        "estimated_tokens": 15000,
        "timeout_minutes": 60,
        "acceptance_criteria": [
            "AC1: diagnose_depgraph.py报告circular_dependencies=0",
            "AC2: diagnose_depgraph.py报告empty_blueprint_id=0",
            "AC3: diagnose_depgraph.py报告cross_layer_references=0",
            "AC4: system-dependency-map.md §19已更新为最新数据",
            "AC5: 所有governance脚本--warn-only exit 0",
        ],
        "rollback_instructions": "git checkout恢复system-dependency-map.md，重新生成旧版depgraph",
        "depends_on": [
            "TASK-ALN-0001",
            "TASK-ALN-0002",
            "TASK-ALN-0003",
            "TASK-ALN-0004",
            "TASK-ALN-0005",
            "TASK-ALN-0006",
            "TASK-ALN-0007",
            "TASK-ALN-0008",
            "TASK-ALN-0009",
            "TASK-ALN-0010",
            "TASK-ALN-0011",
            "TASK-ALN-0012",
            "TASK-ALN-0013",
            "TASK-ALN-0014",
        ],
        "status": "PENDING",
        "tags_fn": ["governance", "verification"],
        "tags_ly": "L01",
        "tags_md": "deepseek",
        "tags_st": "evolving",
        "tags_mo": ["MOD-INF-005"],
    },
]


def main():
    print("[TASK-CREATE] Creating alignment task cards...")
    with TaskRepository() as repo:
        created = 0
        skipped = 0
        for task_data in TASKS:
            task_id = task_data["task_id"]
            existing = repo.get(task_id)
            if existing:
                print(f"  [SKIP] {task_id} already exists (status={existing.status})")
                skipped += 1
                continue
            try:
                task = Task(**task_data)
                result = repo.create(task)
                print(f"  [OK] {task_id}: {task_data['title'][:60]}")
                created += 1
            except Exception as e:
                print(f"  [ERR] {task_id}: {e}")
        print(f"\n[TASK-CREATE] Done: {created} created, {skipped} skipped")


if __name__ == "__main__":
    main()
