"""
创建 D-SIGNAL* 4 域改名执行任务卡（10 张主卡 + 10 张元审查卡）。
依据：d_signal_rename_plan.md（v2，已通过 5 轮循环审查，连续 2 次零问题）
遵循 TRAE-034 任务卡标准，通过 TaskRepository.create() 写入 SQLite governance.db。

任务卡结构：
  主卡 OPS-2026062601~2610：对应方案文档 8 个执行阶段 + 预防机制
  元卡 OPS-2026062611~2620：每张配对审查并修复对应主卡（循环验收 2 轮 0 问题）
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path("D:/ZephyrAlpha")
_SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
_SRC_DIR = REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from zephyr.governance.sqlite_schema import DB_PATH, init_db
from zephyr.governance.task_repo import TaskRepository
from zephyr.governance.rule_enforcement.task_types import (
    ExecutionModel,
    Task,
    TaskNamespace,
    TaskStatus,
)
from zephyr.integration.shared.schema.base_config import Classification, EvolutionPolicy
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel

NOW = datetime.now(UTC)

# 方案文档（任务卡施工内容的唯一真源）
PLAN_DOC = "D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/d_signal_rename_plan.md"

# 公共 applicable_rules
COMMON_RULES = [
    {"module_id": "TRAE-011", "section": "§域归属铁律", "reason": "所有文件路径必须归属正确域"},
    {"module_id": "TRAE-034", "section": "§task_001", "reason": "任务卡标准与生命周期"},
    {"module_id": "TRAE-054", "section": "§全景图访问协议", "reason": "depgraph.db修改必须通过apply_depgraph.py"},
]

# 公共 post_sync_standard
COMMON_POST_SYNC = [
    "python scripts/governance/apply_depgraph.py --diagnose",
]

# 改名映射（裁定#204）
RENAME_MAP = [
    ("D-SIGNAL_ASHARE", "D-ASHARE_SIGNAL", "A股特色信号"),
    ("D-SIGNAL_FUNDAMENTAL", "D-FUNDAMENTAL_SIGNAL", "基本面信号"),
    ("D-SIGNAL_QUALITY", "D-SIGQC", "信号质量控制"),
    ("D-SIGNAL", "D-SIGLEGACY", "信号遗留设计态"),
]


# =====================================================================
# 主卡 1：阶段0 备份
# =====================================================================
def _build_main_01_backup() -> Task:
    description = (
        "根因：裁定#204推翻#ARCH-002/#ARCH-004，将对depgraph.db执行4域改名（488行UPDATE覆盖11表），"
        "改名前必须备份depgraph.db以防数据损坏后无法回滚（trae_054 STEP0硬约束：改depgraph.db前必须git commit备份）。\n"
        "治根：通过GitCommitGateway提交当前depgraph.db到git（创建回滚点），再用apply_depgraph.py --backup"
        "创建物理备份（pre-rename-signal标签），双备份确保可回滚。\n"
        "施工步骤：\n"
        "【GitCommitGateway备份】执行 python scripts/git_commit.py --session rename-signal-backup "
        "--files data/databases/depgraph.db --message \"backup: depgraph before D-SIGNAL* rename (#204)\"，"
        "确认commit成功并记录commit hash。\n"
        "【物理备份】执行 python scripts/governance/apply_depgraph.py --backup \"pre-rename-signal\"，"
        "确认物理备份文件生成。\n"
        "【验证备份】git log确认最新commit包含depgraph.db，apply_depgraph.py备份目录存在。\n"
        "验收标准：git commit成功（含depgraph.db）+物理备份文件存在，两个回滚点均已就绪。"
    )
    return Task(
        task_id="OPS-2026062601",
        namespace=TaskNamespace.OPS,
        seq=2026062601,
        title="阶段0：GitCommitGateway+apply_depgraph.py双备份depgraph.db（#204改名前置）",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=0,
        execution_model=ExecutionModel.glm,
        model_rationale="备份操作，GLM稳定低幻觉",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=0.2,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/data/databases/depgraph.db（git commit + 物理双备份完成）"],
        acceptance=["git log确认含depgraph.db的commit存在 + apply_depgraph.py备份目录存在"],
        depends_on=[],
        tags=["d-signal-rename", "backup", "#204", "phase-0"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§4.1",
        description=description,
        allowed_touch=["D:/ZephyrAlpha/data/databases/depgraph.db"],
        applicable_rules=COMMON_RULES,
        rollback_instructions="无需回滚（本卡为备份操作，失败则不继续后续改名）",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/data/databases/depgraph.db", "description": "git+物理双备份完成"}],
        estimated_tokens=4000,
        timeout_minutes=15,
        ai_autonomy_level="supervised",
        autonomy_checklist=["git commit成功", "物理备份文件存在"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 2：阶段1a apply_depgraph.py 新增 cmd_rename_domain 命令
# =====================================================================
def _build_main_02_add_rename_cmd() -> Task:
    description = (
        "根因：depgraph.db含12表有domain相关列（11表需UPDATE+edges.cross_domain为boolean不需改），"
        "手动UPDATE易遗漏表/列（v1曾遗漏nodes.belongs_to 181行），需在apply_depgraph.py中新增"
        "cmd_rename_domain(old_id, new_id, dry_run)命令实现17步UPDATE覆盖10表，确保无遗漏。\n"
        "治根：在apply_depgraph.py中新增cmd_rename_domain命令，实现17步UPDATE逻辑："
        "domains.domain_id / nodes.domain_id / nodes.subdomain_id / nodes.belongs_to(v1遗漏已修正) / "
        "domain_dependencies.from_domain / domain_dependencies.to_domain / domain_events.source_domain / "
        "domain_events.target_domains(用REPLACE因JSON/TEXT) / contracts.provider_domain / "
        "contracts.consumer_domain / arch_constraints.from_domain / "
        "arch_constraints.to_domain(0行但保留) / arch_directory_tree.domain_id / "
        "arch_path_mappings.domain_id / domain_mapping.domain_id / domain_mapping.subdomain_id"
        "(用REPLACE+LIKE因值含-FACTOR后缀D-SIGNAL_FUNDAMENTAL-FACTOR精确匹配会漏行) / "
        "rule_bindings.domain_id。同时新增--update-domain-name命令更新domains.domain_name。\n"
        "施工步骤：\n"
        "【读取现有】读取apply_depgraph.py，了解现有命令注册机制和参数解析方式。\n"
        "【实现cmd_rename_domain】新增函数实现17步UPDATE，每步打印影响行数，dry_run模式只打印不执行。\n"
        "【实现--update-domain-name】新增命令更新domains.domain_name列。\n"
        "【注册命令】在argparse中注册--rename-domain和--update-domain-name参数。\n"
        "【dry-run测试】对4个改名各执行一次dry_run，确认17步UPDATE覆盖488行"
        "(D-SIGNAL=235/ASHARE=84/FUND=105/QUAL=64)。\n"
        "验收标准：cmd_rename_domain实现17步UPDATE覆盖10表488行，dry_run输出行数与方案§3.2统计表一致。"
    )
    return Task(
        task_id="OPS-2026062602",
        namespace=TaskNamespace.OPS,
        seq=2026062602,
        title="阶段1a：apply_depgraph.py新增cmd_rename_domain命令（17步UPDATE覆盖10表488行）",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=1,
        execution_model=ExecutionModel.glm,
        model_rationale="工具开发需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.H,
        directive="313+325+999",
        idempotent=True,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=2.0,
        files_in_scope=[PLAN_DOC, "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py"],
        deliverables=["D:/ZephyrAlpha/scripts/governance/apply_depgraph.py（新增cmd_rename_domain+--update-domain-name）"],
        acceptance=["dry_run输出17步UPDATE覆盖488行，行数与方案§3.2统计表一致(235+84+105+64=488)"],
        depends_on=["OPS-2026062601"],
        tags=["d-signal-rename", "apply_depgraph", "#204", "phase-1a", "cmd_rename_domain"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§4.2",
        description=description,
        allowed_touch=["D:/ZephyrAlpha/scripts/governance/apply_depgraph.py"],
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout -- scripts/governance/apply_depgraph.py",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC, "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py"],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py", "description": "新增cmd_rename_domain命令"}],
        estimated_tokens=10000,
        timeout_minutes=60,
        ai_autonomy_level="human_gated",
        autonomy_checklist=["17步UPDATE无遗漏表", "step4 belongs_to已纳入", "step8/17用REPLACE", "dry_run行数=488"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 3：阶段1b 执行4域DB改名
# =====================================================================
def _build_main_03_execute_rename() -> Task:
    description = (
        "根因：4个旧域名(D-SIGNAL_ASHARE/D-SIGNAL_FUNDAMENTAL/D-SIGNAL_QUALITY/D-SIGNAL)的D-前缀"
        "暗示父子关系违反所有域平级硬约束，需通过cmd_rename_domain执行4域改名到新ID"
        "(D-ASHARE_SIGNAL/D-FUNDAMENTAL_SIGNAL/D-SIGQC/D-SIGLEGACY)，同时更新domain_name。\n"
        "治根：执行4次--rename-domain命令（顺序无依赖）+4次--update-domain-name命令更新中文名。\n"
        "施工步骤：\n"
        "【dry_run先行】对4个改名各执行一次dry_run，确认影响行数=488（D-SIGNAL=235/ASHARE=84/FUND=105/QUAL=64）。\n"
        "【执行改名1】python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_ASHARE D-ASHARE_SIGNAL。\n"
        "【执行改名2】python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_FUNDAMENTAL D-FUNDAMENTAL_SIGNAL。\n"
        "【执行改名3】python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_QUALITY D-SIGQC。\n"
        "【执行改名4】python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL D-SIGLEGACY。\n"
        "【更新中文名】执行4次--update-domain-name更新D-ASHARE_SIGNAL=A股特色信号/"
        "D-FUNDAMENTAL_SIGNAL=基本面信号/D-SIGQC=信号质量控制/D-SIGLEGACY=信号遗留设计态。\n"
        "【验证无残留】查询11表确认无旧domain_id残留，4个新domain_id均存在。\n"
        "验收标准：4域改名成功，11表无旧domain_id残留，4个新domain_id均存在且domain_name已更新。"
    )
    return Task(
        task_id="OPS-2026062603",
        namespace=TaskNamespace.OPS,
        seq=2026062603,
        title="阶段1b：执行4域DB改名（4×--rename-domain+4×--update-domain-name，488行UPDATE）",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=1,
        execution_model=ExecutionModel.glm,
        model_rationale="DB操作需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.H,
        directive="313+325+999",
        idempotent=False,
        classification=Classification.CONFIDENTIAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.0,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/data/databases/depgraph.db（4域改名完成，488行UPDATE）"],
        acceptance=["11表无旧domain_id残留 + 4个新domain_id存在且domain_name正确"],
        depends_on=["OPS-2026062602"],
        tags=["d-signal-rename", "db-rename", "#204", "phase-1b", "488-rows"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§4.2+§3.2",
        description=description,
        allowed_touch=["D:/ZephyrAlpha/data/databases/depgraph.db"],
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout HEAD~1 -- data/databases/depgraph.db（恢复备份）",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC, "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py"],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/data/databases/depgraph.db", "description": "4域改名488行UPDATE完成"}],
        estimated_tokens=8000,
        timeout_minutes=30,
        ai_autonomy_level="human_gated",
        autonomy_checklist=["dry_run行数=488", "11表无旧ID残留", "4个新ID存在", "domain_name已更新"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 4：阶段2 代码[DOMAIN]头部修改（10文件）
# =====================================================================
def _build_main_04_code_headers() -> Task:
    code_files = [
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/pipeline.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/synth/signal_synthesizer.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/strategy/implementations/default_capital_allocator.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/strategy/capital_allocator.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/gen/implementations/default_signal_aggregator.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/gen/aggregator_base.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/combiner/synthesized_signal.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/capital/default_capital_allocator.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/capital/capital_allocator.py",
        "D:/ZephyrAlpha/src/zephyr/signal_fundamental/capital/capital_allocation_result.py",
    ]
    description = (
        "根因：10个代码文件L3的[DOMAIN]头部标注旧域名（D-SIGNAL或D-SIGNAL_FUNDAMENTAL），"
        "DB改名后代码头部必须同步更新为新域名D-FUNDAMENTAL_SIGNAL，否则代码头部与全景图不一致导致漂移。"
        "其中pipeline.py L3误标为D-SIGNAL（应为D-SIGNAL_FUNDAMENTAL，文件在fundamental/目录下），是预存bug需一并修复。\n"
        "治根：逐个修改10个文件L3的[DOMAIN]头部，D-SIGNAL_FUNDAMENTAL→D-FUNDAMENTAL_SIGNAL（9个文件），"
        "D-SIGNAL→D-FUNDAMENTAL_SIGNAL（pipeline.py，预存bug修复）。\n"
        "施工步骤：\n"
        "【读取确认】逐个读取10个文件L3确认当前[DOMAIN]值，与方案§3.3表格对照。\n"
        "【修改pipeline.py】L3: # [DOMAIN] D-SIGNAL → # [DOMAIN] D-FUNDAMENTAL_SIGNAL（预存bug修复）。\n"
        "【修改9个文件】L3: # [DOMAIN] D-SIGNAL_FUNDAMENTAL → # [DOMAIN] D-FUNDAMENTAL_SIGNAL"
        "（signal_synthesizer.py/default_capital_allocator.py/capital_allocator.py/"
        "default_signal_aggregator.py/aggregator_base.py/synthesized_signal.py/"
        "capital/default_capital_allocator.py/capital/capital_allocator.py/capital_allocation_result.py）。\n"
        "【验证】grep搜索src/zephyr/signal_fundamental/下无D-SIGNAL_FUNDAMENTAL和D-SIGNAL残留（L4依赖引用除外）。\n"
        "【确认不需改】alpha_signal_pipeline.py [DOMAIN]=D-FACTOR不需改，D-SIGNAL_ASHARE/D-SIGNAL_QUALITY在src下0匹配。\n"
        "验收标准：10个文件L3[DOMAIN]头部已更新为D-FUNDAMENTAL_SIGNAL，grep确认无旧域名残留。"
    )
    return Task(
        task_id="OPS-2026062604",
        namespace=TaskNamespace.OPS,
        seq=2026062604,
        title="阶段2：代码[DOMAIN]头部修改（10文件，D-SIGNAL_FUNDAMENTAL→D-FUNDAMENTAL_SIGNAL）",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=2,
        execution_model=ExecutionModel.glm,
        model_rationale="批量文本替换需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.0,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/src/zephyr/signal_fundamental/（10文件[DOMAIN]头部已更新）"],
        acceptance=["10个文件L3[DOMAIN]头部已更新为D-FUNDAMENTAL_SIGNAL，grep无旧域名残留"],
        depends_on=["OPS-2026062603"],
        tags=["d-signal-rename", "code-header", "#204", "phase-2", "10-files"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§3.3+§4.3",
        description=description,
        allowed_touch=code_files,
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout -- src/zephyr/signal_fundamental/",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/src/zephyr/signal_fundamental/", "description": "10文件[DOMAIN]头部更新"}],
        estimated_tokens=8000,
        timeout_minutes=30,
        ai_autonomy_level="supervised",
        autonomy_checklist=["10个文件L3已改", "pipeline.py预存bug已修复", "grep无残留"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 5：阶段3 YAML registry修改
# =====================================================================
def _build_main_05_yaml_registry() -> Task:
    yaml_file = "D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
    description = (
        "根因：functional_domain_registry.yaml是域注册表（YAML真源），"
        "当前L939/L953/L971标注旧域名D-SIGNAL_ASHARE/D-SIGNAL_FUNDAMENTAL/D-SIGNAL_QUALITY，"
        "L11注释引用裁定#201，DB改名后YAML真源必须同步更新为新域名，否则违反YAML是唯一真源硬约束。\n"
        "治根：修改functional_domain_registry.yaml 4行+新增1条：L11注释#裁定#201→#裁定#204（推翻#ARCH-002/#ARCH-004），"
        "L939 D-SIGNAL_ASHARE→D-ASHARE_SIGNAL，L953 D-SIGNAL_FUNDAMENTAL→D-FUNDAMENTAL_SIGNAL，"
        "L971 D-SIGNAL_QUALITY→D-SIGQC，新增D-SIGLEGACY条目（ssot_path留空，covers含45个设计态规划节点）。\n"
        "施工步骤：\n"
        "【读取确认】读取functional_domain_registry.yaml L939/L953/L971确认当前domain值。\n"
        "【修改L11注释】#裁定#201 → #裁定#204（推翻#ARCH-002/#ARCH-004）。\n"
        "【修改L939】- domain: D-SIGNAL_ASHARE → - domain: D-ASHARE_SIGNAL。\n"
        "【修改L953】- domain: D-SIGNAL_FUNDAMENTAL → - domain: D-FUNDAMENTAL_SIGNAL。\n"
        "【修改L971】- domain: D-SIGNAL_QUALITY → - domain: D-SIGQC。\n"
        "【新增D-SIGLEGACY】新增条目，ssot_path留空，covers含\"45个设计态规划节点\"。\n"
        "【验证】grep确认无旧域名残留，4个新域名+1个新增条目存在。\n"
        "验收标准：YAML 4行改名+1条新增完成，grep无旧域名残留，裁定注释已更新为#204。"
    )
    return Task(
        task_id="OPS-2026062605",
        namespace=TaskNamespace.OPS,
        seq=2026062605,
        title="阶段3：YAML registry修改（functional_domain_registry.yaml 4行改+1条新增）",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=3,
        execution_model=ExecutionModel.glm,
        model_rationale="YAML编辑需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=0.5,
        files_in_scope=[PLAN_DOC, yaml_file],
        deliverables=[yaml_file + "（4行改+1条新增）"],
        acceptance=["YAML 4行改名+1条新增完成，grep无旧域名残留，裁定注释已更新为#204"],
        depends_on=["OPS-2026062604"],
        tags=["d-signal-rename", "yaml-registry", "#204", "phase-3"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§3.4+§4.4",
        description=description,
        allowed_touch=[yaml_file],
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout -- docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC, yaml_file],
        downstream_outputs=[{"path": yaml_file, "description": "4行改名+1条新增"}],
        estimated_tokens=5000,
        timeout_minutes=20,
        ai_autonomy_level="supervised",
        autonomy_checklist=["4行改名正确", "D-SIGLEGACY新增条目", "裁定注释#204"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 6：阶段4 生成器脚本修改（6文件~23处硬编码）
# =====================================================================
def _build_main_06_generators() -> Task:
    gen_files = [
        "D:/ZephyrAlpha/scripts/governance/d5_architecture/generators/domain_name_mapping.py",
        "D:/ZephyrAlpha/scripts/governance/d5_architecture/dm200912_rewrite_views.py",
        "D:/ZephyrAlpha/scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py",
        "D:/ZephyrAlpha/scripts/governance/d5_architecture/dm200916_write_direct.py",
        "D:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_capability_heatmap.py",
        "D:/ZephyrAlpha/scripts/governance/audit_domain_nodes.py",
    ]
    description = (
        "根因：6个生成器脚本含~23处硬编码旧域名（D-SIGNAL/D-SIGNAL_FUNDAMENTAL/"
        "D-SIGNAL_ASHARE/D-SIGNAL_QUALITY），DB改名后若不更新硬编码，重新生成的制品将包含旧域名导致不一致。"
        "所有引用均为静态字面量（无动态拼接domain_id），可安全批量替换。\n"
        "治根：逐个修改6个生成器脚本中的硬编码domain_id为新域名，优先改domain_name_mapping.py（域名映射中心）。\n"
        "施工步骤：\n"
        "【优先改domain_name_mapping.py】L44-47字典映射4个旧域名→4个新域名"
        "（D-SIGNAL→D-SIGLEGACY信号遗留设计态/D-SIGNAL_ASHARE→D-ASHARE_SIGNAL/"
        "D-SIGNAL_FUNDAMENTAL→D-FUNDAMENTAL_SIGNAL/D-SIGNAL_QUALITY→D-SIGQC信号质量控制）。\n"
        "【改dm200912】L819域列表(逗号串)4个旧域名→4个新域名。\n"
        "【改dm200913】L508域列表(list)+L78/107/108/156/157/190/199/294/295/464/585/615/828共13处展示型文本批量替换。\n"
        "【改dm200916】L314-317 YAML primary_domains 4行+L425 name D-SIGNAL×C2→D-SIGLEGACY×C2+L426 domain D-SIGNAL→D-SIGLEGACY。\n"
        "【改generate_capability_heatmap】L59域列表4个旧域名→4个新域名。\n"
        "【改audit_domain_nodes】L316 domains_13 D-SIGNAL→D-SIGLEGACY+L363 print标签+L364 SQL迭代。\n"
        "【验证】grep搜索6个脚本无旧域名残留，确认无动态拼接domain_id。\n"
        "验收标准：6个生成器脚本~23处硬编码已更新，grep无旧域名残留。"
    )
    return Task(
        task_id="OPS-2026062606",
        namespace=TaskNamespace.OPS,
        seq=2026062606,
        title="阶段4：生成器脚本修改（6文件~23处硬编码domain_id批量替换）",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=4,
        execution_model=ExecutionModel.glm,
        model_rationale="批量硬编码替换需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.5,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/scripts/governance/d5_architecture/（6个生成器脚本硬编码已更新）"],
        acceptance=["6个生成器脚本~23处硬编码已更新，grep无旧域名残留"],
        depends_on=["OPS-2026062605"],
        tags=["d-signal-rename", "generators", "#204", "phase-4", "23-hardcodes"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§3.5+§4.5",
        description=description,
        allowed_touch=gen_files,
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout -- scripts/governance/d5_architecture/ scripts/governance/audit_domain_nodes.py",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/scripts/governance/d5_architecture/", "description": "6个生成器脚本硬编码更新"}],
        estimated_tokens=10000,
        timeout_minutes=45,
        ai_autonomy_level="supervised",
        autonomy_checklist=["6个脚本已改", "~23处硬编码无遗漏", "无动态拼接确认"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 7：阶段5a 活文档修改（22文件）
# =====================================================================
def _build_main_07_active_docs() -> Task:
    active_docs = [
        "D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/index.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/contracts/cross_layer_contracts.yaml",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/contracts/consumer_registry.yaml",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/cross_cutting/runtime_planes.yaml",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/architecture_model/cross_cutting/capability_heatmap.yaml",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/application_architecture.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/capability_heatmap.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/technology_architecture.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/c4_l2_containers.mmd",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/dataflow_terminal.mmd",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/capability_heatmap_visual.mmd",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/c4_l3_l11_ml_platform.mmd",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/data_flow.mmd",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/integration_topology.mmd",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/target_architecture/diagrams/runtime_topology.mmd",
        "D:/ZephyrAlpha/docs/03_modules/index.md",
        "D:/ZephyrAlpha/docs/03_modules/_domain_signal/index.md",
        "D:/ZephyrAlpha/docs/03_modules/_alpha_signal_domain/index.md",
        "D:/ZephyrAlpha/docs/03_modules/content_layering_task_cards.md",
        "D:/ZephyrAlpha/docs/01_policies_and_standards/templates/dependency_graph_template.md",
    ]
    description = (
        "根因：22个活文档（当前有效配置）含旧域名D-SIGNAL_ASHARE/D-SIGNAL_FUNDAMENTAL/D-SIGNAL_QUALITY/D-SIGNAL，"
        "DB改名后活文档必须直接替换为新域名，否则文档与DB不一致导致AI读取文档时产生幻觉。"
        "活文档与历史记录文档区分：活文档直接替换域名（~82行），历史记录文档追加推翻说明（见主卡8）。\n"
        "治根：逐个修改22个活文档，将4个旧域名直接替换为4个新域名"
        "（D-SIGNAL_ASHARE→D-ASHARE_SIGNAL/D-SIGNAL_FUNDAMENTAL→D-FUNDAMENTAL_SIGNAL/"
        "D-SIGNAL_QUALITY→D-SIGQC/D-SIGNAL→D-SIGLEGACY）。\n"
        "施工步骤：\n"
        "【读取确认】逐个读取22个活文档，确认含旧域名的行号和上下文。\n"
        "【批量替换】对每个文件执行4个旧域名→4个新域名的替换（注意D-SIGNAL最后替换避免误伤D-SIGNAL_ASHARE等）。\n"
        "【顺序注意】先替换D-SIGNAL_ASHARE→D-ASHARE_SIGNAL/D-SIGNAL_FUNDAMENTAL→D-FUNDAMENTAL_SIGNAL/"
        "D-SIGNAL_QUALITY→D-SIGQC，最后替换D-SIGNAL→D-SIGLEGACY（避免短串误匹配长串）。\n"
        "【验证】grep搜索22个活文档无旧域名残留，确认新域名已写入。\n"
        "【确认生成制品】确认7个生成制品（cross_domain_matrix.md等）不在活文档列表中（它们在阶段6重新生成）。\n"
        "验收标准：22个活文档旧域名已替换为新域名，grep无旧域名残留（排除生成制品和历史记录文档）。"
    )
    return Task(
        task_id="OPS-2026062607",
        namespace=TaskNamespace.OPS,
        seq=2026062607,
        title="阶段5a：活文档修改（22文件，直接替换4个旧域名→4个新域名，~82行）",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=5,
        execution_model=ExecutionModel.glm,
        model_rationale="批量文档替换需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=2.0,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/docs/02_enterprise_architecture/（22个活文档域名已替换，~82行）"],
        acceptance=["22个活文档旧域名已替换，grep无旧域名残留（排除生成制品和历史记录文档）"],
        depends_on=["OPS-2026062606"],
        tags=["d-signal-rename", "active-docs", "#204", "phase-5a", "22-files"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§3.6.1+§4.6",
        description=description,
        allowed_touch=active_docs,
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout -- docs/02_enterprise_architecture/ docs/03_modules/ docs/01_policies_and_standards/templates/",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/docs/02_enterprise_architecture/", "description": "22个活文档域名替换"}],
        estimated_tokens=12000,
        timeout_minutes=60,
        ai_autonomy_level="supervised",
        autonomy_checklist=["22个文件已改", "替换顺序正确(短串最后)", "grep无残留"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 8：阶段5b 历史记录文档修改（7文件）
# =====================================================================
def _build_main_08_history_docs() -> Task:
    history_docs = [
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/dependency_architecture_panorama.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/preexisting_db_issues_investigation_report.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md",
        "D:/ZephyrAlpha/docs/_working/domain_split_plan_4_oversized_domains.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/t18_implementation_plan.md",
        "D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/d_signal_rename_plan.md",
        "D:/ZephyrAlpha/data/pending_manual_completion_list.md",
    ]
    description = (
        "根因：7个历史记录文档记录了#ARCH-002/#ARCH-004等旧裁定和D-SIGNAL旧名上下文，"
        "不能直接替换域名（会破坏历史记录的完整性），需追加裁定#204推翻说明并保留旧名上下文，"
        "让后续AI能理解裁定演变历史（为什么改名）。\n"
        "治根：对7个历史记录文档追加#204推翻说明，在旧裁定记录处标注\"已被#204推翻\"，保留旧名上下文不删除。\n"
        "施工步骤：\n"
        "【panorama.md】追加裁定#204（推翻#ARCH-002/#ARCH-004）+在#201记录处标注\"已被#204推翻\"（~9行）。\n"
        "【preexisting_db_issues.md】在#ARCH-002/#ARCH-003/#ARCH-004议题处标注\"已被#204推翻\"+追加#204执行记录（~45行）。\n"
        "【architecture_upgrade_discussion.md】追加\"注：#204已推翻#ARCH-002/#ARCH-004，4域改名\"（~12行）。\n"
        "【domain_split_plan.md】追加推翻说明（1行）。\n"
        "【t18_implementation_plan.md】追加推翻说明（1行）。\n"
        "【d_signal_rename_plan.md】本方案文档自身，执行后更新为\"已执行\"状态（~45行）。\n"
        "【pending_manual_completion_list.md】更新待完成清单（3行）。\n"
        "【验证】确认7个文档已追加推翻说明，旧名上下文保留未删除。\n"
        "验收标准：7个历史记录文档已追加#204推翻说明，旧名上下文保留完整。"
    )
    return Task(
        task_id="OPS-2026062608",
        namespace=TaskNamespace.OPS,
        seq=2026062608,
        title="阶段5b：历史记录文档修改（7文件追加#204推翻说明，保留旧名上下文）",
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=5,
        execution_model=ExecutionModel.glm,
        model_rationale="历史文档编辑需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.5,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/docs/02_enterprise_architecture/（7个历史记录文档已追加#204推翻说明）"],
        acceptance=["7个历史记录文档已追加#204推翻说明，旧名上下文保留完整"],
        depends_on=["OPS-2026062607"],
        tags=["d-signal-rename", "history-docs", "#204", "phase-5b", "7-files"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§3.6.2+§4.6",
        description=description,
        allowed_touch=history_docs,
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout -- docs/02_enterprise_architecture/ data/pending_manual_completion_list.md",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/docs/02_enterprise_architecture/", "description": "7个历史记录文档追加推翻说明"}],
        estimated_tokens=10000,
        timeout_minutes=45,
        ai_autonomy_level="supervised",
        autonomy_checklist=["7个文档已追加说明", "旧名上下文保留", "#204裁定记录完整"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 9：阶段6+7 重新生成制品+验证
# =====================================================================
def _build_main_09_regenerate_verify() -> Task:
    description = (
        "根因：13个生成制品（domain_index.md/01-43_*.md/*_architecture.md/*.mmd/"
        "cross_domain_matrix.md/runtime_plane_mapping.md/integration_topology.md/"
        "capability_heatmap.md/design_vs_production.md/constraint_violations.md/"
        "capacity_report.md/project_entity_depgraph.yaml/target_path_tree.yaml）"
        "由生成器从depgraph.db自动生成，DB改名后必须重新生成否则制品含旧域名。"
        "同时需执行3项验证确保改名无残留。\n"
        "治根：执行11个生成器命令重新生成13个制品，执行3项验证（DB无残留/新ID存在/grep无旧域名）。\n"
        "施工步骤：\n"
        "【资产索引】python scripts/governance/generate_project_depgraph.py。\n"
        "【域架构文档】generate_domain_index.py + generate_domain_doc.py --all + generate_domain_architecture_diagram.py --all。\n"
        "【治理报告】generate_capacity_report.py + generate_design_vs_production.py + generate_constraint_violations.py。\n"
        "【全局架构图】generate_cross_domain_matrix.py + generate_runtime_plane_mapping.py + "
        "generate_capability_heatmap.py + dm200912_rewrite_views.py + dm200913_rewrite_diagrams.py + dm200916_write_direct.py。\n"
        "【验证1-DB无残留】查询11表确认无旧domain_id残留（D-SIGNAL_ASHARE/D-SIGNAL_FUNDAMENTAL/D-SIGNAL_QUALITY/D-SIGNAL）。\n"
        "【验证2-新ID存在】确认4个新domain_id在domains表存在。\n"
        "【验证3-grep全局】grep搜索全项目旧域名（排除生成制品和历史记录文档中的旧名上下文）。\n"
        "验收标准：13个生成制品重新生成成功+3项验证全部通过（DB无残留/新ID存在/grep无旧域名）。"
    )
    return Task(
        task_id="OPS-2026062609",
        namespace=TaskNamespace.OPS,
        seq=2026062609,
        title="阶段6+7：重新生成13个制品+3项验证（DB无残留/新ID存在/grep无旧域名）",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=6,
        execution_model=ExecutionModel.glm,
        model_rationale="生成器执行+验证需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325+999",
        idempotent=True,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=1.5,
        files_in_scope=[PLAN_DOC],
        deliverables=["D:/ZephyrAlpha/docs/02_enterprise_architecture/（13个生成制品已重新生成）"],
        acceptance=["13个生成制品重新生成成功+3项验证全部通过"],
        depends_on=["OPS-2026062608"],
        tags=["d-signal-rename", "regenerate", "verify", "#204", "phase-6-7"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§4.7+§4.8+§3.7",
        description=description,
        allowed_touch=[
            "D:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs/",
            "D:/ZephyrAlpha/docs/02_enterprise_architecture/generated/",
            "D:/ZephyrAlpha/docs/02_enterprise_architecture/01_global_architecture_diagram/",
            "D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md",
            "D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md",
            "D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/capacity_report.md",
            "D:/ZephyrAlpha/data/asset_index/project_entity_depgraph.yaml",
            "D:/ZephyrAlpha/data/asset_index/target_path_tree.yaml",
        ],
        applicable_rules=COMMON_RULES,
        rollback_instructions="DB回滚后重新运行生成器即可（制品可重新生成）",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/docs/02_enterprise_architecture/", "description": "13个生成制品重新生成"}],
        estimated_tokens=10000,
        timeout_minutes=60,
        ai_autonomy_level="supervised",
        autonomy_checklist=["11个生成器成功", "13个制品更新", "3项验证通过"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主卡 10：阶段8 git commit + 预防机制
# =====================================================================
def _build_main_10_commit_prevention() -> Task:
    description = (
        "根因：改名完成后需分批git commit记录变更，且漂移根因是命名规则仅在Markdown文档中"
        "（AI建域/生成代码时不主动查阅），需新增domain_naming_rules表把规则写入DB让AI可见，"
        "并新增建域门禁在--insert-domain时强制校验命名规则，防止再产生D-XXX_YYY形式域名。\n"
        "治根：按6批分批git commit+新增domain_naming_rules表5条规则+新增domain_naming_rules.yaml+"
        "sync同步逻辑+apply_depgraph.py建域门禁校验。\n"
        "施工步骤：\n"
        "【分批commit】按6批提交：1.apply_depgraph.py+depgraph.db 2.代码[DOMAIN]头部 3.YAML registry "
        "4.生成器脚本 5.手动维护文档 6.重新生成的制品，每批通过GitCommitGateway提交。\n"
        "【新增domain_naming_rules表】在depgraph.db新增表（rule_id/rule_name/rule_text/applies_to/"
        "severity/example_bad/example_good/created_at/source_doc），通过apply_depgraph.py建表。\n"
        "【新增5条规则】NR-001无父子前缀(error)/NR-002 snake_case命名(error)/NR-003语义独立性(error)/"
        "NR-004设计态标识(warning)/NR-005中文名一致(warning)。\n"
        "【新增domain_naming_rules.yaml】在docs/01_policies_and_standards/_registry/catalogs/新建YAML真源文件。\n"
        "【sync同步】sync_yaml_to_depgraph.py新增domain_naming_rules表同步逻辑。\n"
        "【建域门禁】apply_depgraph.py --insert-domain新增命名规则校验：查询applies_to=create的规则，"
        "severity=error违反则阻断建域(exit 3)，warning则打印警告。\n"
        "【验证门禁】测试D-SIGNAL_NEWSUB建域被NR-001阻断(exit 3)。\n"
        "验收标准：6批git commit完成+domain_naming_rules表5条规则+建域门禁阻断违反NR-001的域名。"
    )
    return Task(
        task_id="OPS-2026062610",
        namespace=TaskNamespace.OPS,
        seq=2026062610,
        title="阶段8+预防：6批git commit+domain_naming_rules表+建域门禁（防再产生D-XXX_YYY域名）",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=8,
        execution_model=ExecutionModel.glm,
        model_rationale="预防机制开发需低幻觉，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.H,
        directive="313+325+999",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=3.0,
        files_in_scope=[PLAN_DOC, "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py"],
        deliverables=["D:/ZephyrAlpha/data/databases/depgraph.db（6批commit+domain_naming_rules表+建域门禁）"],
        acceptance=["6批git commit完成+domain_naming_rules表5条规则+建域门禁阻断违反NR-001的域名"],
        depends_on=["OPS-2026062609"],
        tags=["d-signal-rename", "commit", "prevention", "#204", "phase-8", "naming-rules"],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section="§4.9+§8",
        description=description,
        allowed_touch=[
            "D:/ZephyrAlpha/data/databases/depgraph.db",
            "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py",
            "D:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py",
            "D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml",
        ],
        applicable_rules=COMMON_RULES,
        rollback_instructions="git checkout HEAD~6 -- data/databases/depgraph.db scripts/governance/ docs/01_policies_and_standards/_registry/",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC, "D:/ZephyrAlpha/scripts/governance/apply_depgraph.py"],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/data/databases/depgraph.db", "description": "domain_naming_rules表+建域门禁"}],
        estimated_tokens=15000,
        timeout_minutes=90,
        ai_autonomy_level="human_gated",
        autonomy_checklist=["6批commit完成", "5条规则入库", "门禁阻断测试通过"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 元审查卡 11~20：每张配对审查并修复对应主卡
# =====================================================================

_META_REVIEW_SECTIONS = {
    11: ("OPS-2026062601", "§4.1", "阶段0备份", "GitCommitGateway备份+apply_depgraph.py物理备份"),
    12: ("OPS-2026062602", "§4.2", "阶段1a cmd_rename_domain命令", "17步UPDATE覆盖10表488行"),
    13: ("OPS-2026062603", "§4.2+§3.2", "阶段1b 4域DB改名", "4×--rename-domain+4×--update-domain-name"),
    14: ("OPS-2026062604", "§3.3+§4.3", "阶段2 代码[DOMAIN]头部", "10文件L3修改"),
    15: ("OPS-2026062605", "§3.4+§4.4", "阶段3 YAML registry", "4行改+1条新增"),
    16: ("OPS-2026062606", "§3.5+§4.5", "阶段4 生成器脚本", "6文件~23处硬编码"),
    17: ("OPS-2026062607", "§3.6.1+§4.6", "阶段5a 活文档", "22文件直接替换域名"),
    18: ("OPS-2026062608", "§3.6.2+§4.6", "阶段5b 历史记录文档", "7文件追加推翻说明"),
    19: ("OPS-2026062609", "§4.7+§4.8+§3.7", "阶段6+7 重新生成+验证", "13制品+3项验证"),
    20: ("OPS-2026062610", "§4.9+§8", "阶段8+预防机制", "6批commit+domain_naming_rules表+门禁"),
}


def _build_meta_card(meta_seq: int) -> Task:
    """构建元审查卡：审查并修复对应主卡。"""
    meta_id = f"OPS-20260626{meta_seq:02d}"
    main_id, section, phase_name, summary = _META_REVIEW_SECTIONS[meta_seq]
    description = (
        f"根因：主卡{main_id}（{phase_name}）的施工内容需对照方案文档{section}节逐项审查，"
        f"防止遗漏/幻觉/漂移——施工内容不够详细会导致AI执行时产生幻觉（如遗漏文件、行号错误、内容不一致）。\n"
        f"治根：对照方案文档{section}节逐项核对主卡{main_id}的施工步骤/文件列表/行号/内容/验收标准，"
        f"修复所有不一致，循环审查至连续2轮0问题。\n"
        "施工步骤：\n"
        f"【读取主卡】从governance.db读取主卡{main_id}的description/allowed_touch/files_in_scope/acceptance。\n"
        f"【对照方案】读取方案文档{section}节，逐项核对主卡施工步骤是否完整覆盖方案文档所有内容。\n"
        "【核对文件清单】核对主卡allowed_touch是否完整列出方案文档中所有需修改的文件（无遗漏无多余）。\n"
        "【核对行号内容】核对主卡description中引用的行号/原内容/新内容是否与方案文档完全一致（无幻觉）。\n"
        "【核对验收标准】核对主卡acceptance是否与方案文档验收标准一致（无漂移）。\n"
        "【核对依赖关系】核对主卡depends_on是否正确（前序阶段已完成）。\n"
        "【修复不一致】发现遗漏/幻觉/漂移时，通过TaskRepository.update()修复主卡{main_id}的对应字段。\n"
        "【循环验收】重复审查至连续2轮0问题（CIRCULAR_ACCEPTANCE_ROUNDS=2）。\n"
        f"验收标准：主卡{main_id}施工内容与方案文档{section}节完全一致，连续2轮审查0问题。"
    )
    return Task(
        task_id=meta_id,
        namespace=TaskNamespace.OPS,
        seq=int(f"20260626{meta_seq:02d}"),
        title=f"元审查：审查并修复主卡{main_id}（{phase_name}）——对照方案{section}循环验收2轮0问题",
        status=TaskStatus.PENDING,
        priority=Priority.P1,
        phase=9,
        execution_model=ExecutionModel.glm,
        model_rationale="审查校验需低幻觉高精度，GLM稳定",
        fallback_model="",
        safety_level=SafetyLevel.M,
        directive="313+325+999",
        idempotent=False,
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=0.5,
        files_in_scope=[PLAN_DOC],
        deliverables=[f"主卡{main_id}审查报告（连续2轮0问题通过）"],
        acceptance=[f"主卡{main_id}施工内容与方案文档{section}节完全一致，连续2轮审查0问题"],
        depends_on=[main_id],
        tags=["d-signal-rename", "meta-review", "#204", main_id],
        source_blueprint="D-SIGNAL-RENAME-001",
        source_section=f"§元审查-{section}",
        description=description,
        allowed_touch=["D:/ZephyrAlpha/data/databases/governance.db"],
        applicable_rules=COMMON_RULES + [
            {"module_id": "TRAE-034", "section": "§task_001_batch_review_protocol", "reason": "7维度循环审查协议"},
            {"module_id": "TRAE-024", "section": "mth_006", "reason": "根源分析原则——审查发现问题时需根因分析"},
        ],
        rollback_instructions="审查操作不修改生产文件，无需回滚（仅修改governance.db中主卡字段）",
        post_sync_standard=COMMON_POST_SYNC,
        upstream_files=[PLAN_DOC],
        downstream_outputs=[{"path": "D:/ZephyrAlpha/data/databases/governance.db", "description": f"主卡{main_id}审查修复完成"}],
        estimated_tokens=8000,
        timeout_minutes=30,
        ai_autonomy_level="supervised",
        autonomy_checklist=[f"主卡{main_id}文件清单完整", "行号内容无幻觉", "验收标准无漂移", "连续2轮0问题"],
        construction_status="pending",
        verification_status="unverified",
        created_at=NOW,
        updated_at=NOW,
    )


# =====================================================================
# 主函数
# =====================================================================
def main() -> int:
    """创建 10 张主卡 + 10 张元审查卡，共 20 张。"""
    init_db(DB_PATH)

    cards: list[Task] = [
        # 主卡 1~10
        _build_main_01_backup(),
        _build_main_02_add_rename_cmd(),
        _build_main_03_execute_rename(),
        _build_main_04_code_headers(),
        _build_main_05_yaml_registry(),
        _build_main_06_generators(),
        _build_main_07_active_docs(),
        _build_main_08_history_docs(),
        _build_main_09_regenerate_verify(),
        _build_main_10_commit_prevention(),
        # 元审查卡 11~20
        _build_meta_card(11),
        _build_meta_card(12),
        _build_meta_card(13),
        _build_meta_card(14),
        _build_meta_card(15),
        _build_meta_card(16),
        _build_meta_card(17),
        _build_meta_card(18),
        _build_meta_card(19),
        _build_meta_card(20),
    ]

    created_ids: list[str] = []
    with TaskRepository(db_path=DB_PATH, auto_init=False, enable_gate=False) as repo:
        for card in cards:
            try:
                tc = repo.create(card, allow_direct_create=True)
                created_ids.append(tc.task_id)
                print(f"  [OK] {tc.task_id}: {tc.title}", file=sys.stderr)
            except Exception as e:
                print(f"  [FAIL] {card.task_id}: {e}", file=sys.stderr)
                return 1

    print(f"\n创建完成: {len(created_ids)}张任务卡", file=sys.stderr)
    for tid in created_ids:
        print(f"  - {tid}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
