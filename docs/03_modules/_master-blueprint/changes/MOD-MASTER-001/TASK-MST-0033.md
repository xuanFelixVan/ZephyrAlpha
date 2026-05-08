---
task_id: "TASK-MST-0033"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 变更记录/版本历史（v0.1.0~v0.9.1 全版本） + 代码文件路径索引（§1.1 源码/§1.5 使用指南）"

title: "实现模块全版本管理与文件路径索引——MOD-MASTER-001 v0.1.0→v0.9.1 完整生命周期追踪"
description: |
  管理 MOD-MASTER-001 从 v0.1.0 到 v0.9.1 的完整版本记录和代码文件路径索引。

  **第一处变更记录（蓝图行1654-1667，v0.1.0~v0.6.0）**：
  - v0.1.0: 初始骨架——任务系统+脚本系统+知识库+Gate Engine 核心集成契约
  - v0.2.0: Phase D扩展——新增 Pipeline+CE+FLE 三系统
  - v0.3.0: 四章新增——§一~§四（拓扑/契约表/Schema/状态传播链）+ 共享Schema定义
  - v0.4.0: 大幅扩展——35 盲点审计 + §五~§九（容量预算/Phase/Anti-Patterns/施工指南/DD）
  - v0.5.0: 全维度评审后系统补全——frontmatter升级+§三嵌入CTR-VER-001+12条CT-*追加ai_prompt+§十四HealthCheck+§十五CBAC+§十六CDC/DLQ/Reconcile
  - v0.6.0: Round 2补盲——12处内部一致性修复+§十七SLO+§十八Bulkhead/Watchdog/Backup+§十九Config/FeatureFlag/Secrets/KISS+§二十DataLifecycle/MultiEnv/Chaos/Codegen/BreakingChange

  **第二处变更记录（蓝图行3598-3639，v0.7.0~v0.9.0）**：
  - v0.7.0→v0.8.0 (Round 4): 终极补全达成99/100世界级标准——新增§二十五~§三十六共12条CT-*（CT-BENCH-001/DEPLOY-001/SCHEMA-MIGRATE-001/DEGRADE-CASCADE-001/AUTONOMY-001/AGENT-QUALITY-001/PROMPT-VERSION-001/SESSION-CONFLICT-001/LEAN-001/BLUEPRINT-HEALTH-001/TRANSFER-001/KE-QUALITY-001）。总CT-*: 42+12=54条。
  - v0.8.0→v0.9.0 (Round 5): 深度交叉审计——7大维度35新盲点全注入（B-MOD-301~B-MOD-335）+ §37.10 1人+AI生存三法则。蓝图总盲点: ~300(历史)+35(Round 5)=~335。总行数: ~3,457→~3,800。

  **当前版本 v0.9.1**（frontmatter version=0.9.1）：基于 v0.9.0 的微调修正版，标题含"35+32新盲点全注入"。

  **代码文件路径索引（§1.1 源码文件 + §1.5 路径索引使用指南）**：
  - 扫描 D:\ZephyrAlpha\src\zephyr\ 全树 → 建立路径→所属系统→对应 task_id 的完整映射表
  - §1.5 使用指南：A/B/C三层引用——代码(import)/Blueprint(CT-*)/TaskCard(task_id)——三态一致性验证

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\module_version.py"
    description: "模块全版本管理器——v0.1.0→v0.9.1全版本读取+frontmatter version=0.9.1自动提取+changelog双向同步(蓝图↔module_versions表)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\file_path_index.py"
    description: "文件路径索引器——§1.1源码路径扫描+路径→系统→task_id映射+三态一致性验证(import/CT-*/task_id)"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_module_version.py"
    description: "模块版本管理单元测试——v0.1.0→v0.9.1全版本链完整性验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\module_version.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\file_path_index.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_module_version.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "蓝图 frontmatter v0.9.1 + 第一处变更记录(行1654-1667) + 第二处变更记录(行3598-3639) + §1.1源码文件索引 + §1.5路径索引使用指南"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M2"
estimated_tokens: 8000
timeout_minutes: 45

acceptance_criteria:
  - "module_version.py 读取 blueprint.md frontmatter 的 version=0.9.1 字段并写入 module_versions 表"
  - "完整解析两处变更记录——第一处(v0.1.0~v0.6.0) + 第二处(v0.7.0~v0.9.0)——版本链不间断"
  - "每次蓝图版本变更 → 自动生成 changelog entry(version/date/author/changes/sections_affected/ct_star_added/blindspots_added)"
  - "file_path_index.py 扫描 src/zephyr/ 全树 → 建立 路径→所属12系统→对应task_id 的三态映射"
  - "路径索引三态一致性验证——import路径 / CT-*契约路径 / task_id路径——不一致→CI FAIL"
  - "依赖验证: 15个 depends_on 模块的 status 一致性检查 → 不一致→CI WARN"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\module_version.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\file_path_index.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_module_version.py

depends_on: []
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
