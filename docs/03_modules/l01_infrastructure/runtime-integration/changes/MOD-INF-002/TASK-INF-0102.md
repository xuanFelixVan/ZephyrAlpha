---
task_id: "TASK-INF-0102"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2 Cross-Layer 缺口清单 RL-001~RL-048 + §5.5 填补方案表 + §4 输入"
title: "Phase 1a 底座上线缺口填补——RL-002/003/004/008/013/024/036/038/044/048"
description: |
  填补 Phase 1a 涉及的 Cross-Layer 缺口。
  RL-002 模块管理→ModuleLifecycle 拓扑排序启动（≤50ms/500模块）+
  RL-003 配置分层→ConfigCenter YAML+env+热重载（<3s）+
  RL-013/024 依赖注入→MOD-INF-016 di_container.py 构造注入+接口绑定+循环检测+
  RL-036 结构化并发→asyncio.TaskGroup 管理1500+模块+
  RL-038 优雅关闭→drain→等待→超时→ForceKill→持久化+
  RL-044 预热期→warmup→内部HC→READY+
  RL-048 Crash-Only→每次停止=crash，恢复走重启。
  同步验证 §4 输入：Owner架构提问、Wave 0 跨层审计、MOD-INF-016 v0.14.0 现有实现。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-lifecycle-standard.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\errors.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\shutdown.py"
    description: "优雅关闭协议——§5.3 GracefulShutdown 代码骨架实现"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\warmup.py"
    description: "预热期机制——warmup→internal HC→READY"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\di_container.py"
    description: "DI 容器——构造注入+ABC接口绑定+循环检测(BFS)"
  - path: "D:\\ZephyrAlpha\\tests\\shared\\test_shutdown.py"
    description: "优雅关闭协议单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\shared\\test_warmup.py"
    description: "预热期机制单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\shared\\test_di_container.py"
    description: "DI 容器单元测试——含循环依赖检测验证"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\shutdown.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\warmup.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\di_container.py"
  - "D:\\ZephyrAlpha\\tests\\shared\\test_shutdown.py"
  - "D:\\ZephyrAlpha\\tests\\shared\\test_warmup.py"
  - "D:\\ZephyrAlpha\\tests\\shared\\test_di_container.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\errors.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建——产出物必须符合目录结构标准"
  - module_id: "MOD-INF-002"
    section: "§5.2"
    reason: "设计原则：Crash-Only + StructuredConcurrency + Fail-Closed"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "本蓝图——§2 RL缺口定义、§5.3 代码骨架(GracefulShutdown/Warmup)、§5.2 设计原则"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\shared-core\\blueprint.md"
    reason: "MOD-INF-016 承载基座——验证现有 shared/lifecycle/hooks.py 并扩展"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-lifecycle-standard.md"
    reason: "任务生命周期标准——确保产出物状态机对齐"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 60
acceptance_criteria:
  - "shared/lifecycle/shutdown.py: GracefulShutdown 类——drain(30s)→force_kill(5s)→状态持久化"
  - "shared/lifecycle/warmup.py: WarmupManager 类——缓存预热+内部HealthCheck全PASS→READY信号"
  - "shared/production/di_container.py: 构造注入+ABC接口绑定+启动时BFS循环检测阻断"
  - "500 模块拓扑排序 ≤ 50ms（RL-002）"
  - "配置热重载延迟 < 3s（RL-003）"
  - "0 孤儿协程——asyncio.TaskGroup 验证（RL-036）"
  - "关闭 0 数据丢失——SIGTERM→drain→持久化（RL-038）"
  - "启动 0 假熔断——warmup→READY（RL-044）"
rollback_instructions: |
  1. 删除新增文件：D:\ZephyrAlpha\src\zephyr\shared\lifecycle\shutdown.py / warmup.py
  2. 删除新增文件：D:\ZephyrAlpha\src\zephyr\shared\production\di_container.py
  3. 删除新增测试文件：D:\ZephyrAlpha\tests\shared\test_shutdown.py / test_warmup.py / test_di_container.py
  4. 如 shared/lifecycle/hooks.py 或 shared/config/__init__.py 被意外修改→git checkout 还原
depends_on:
  - "TASK-INF-0101"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
  - "MOD-INF-016"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
