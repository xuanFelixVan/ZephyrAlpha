---
module_id: KE-2758
status: active
title: In-Scope
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# In-Scope

In-Scope
- 创建 `src/zephyr/context-engine/` 目录及 `__init__.py`，声明 `bounded_context=true`
- 按 §4 文件组成创建以下 9 个 .py 源文件骨架（含模块级 docstring）：
  - `context_assembler.py` — Build 阶段——从 VMS 拉取原始上下文
  - `context_budget_tracker.py` — Compress 阶段——Token 预算管理
  - `doc_compressor.py` — Compress 阶段——三级压缩回退（已有 563 行完整实现，更新 docstring）
  - `context_injector.py` — Inject 阶段——格式化+注入 session
  - `intent_parser.py` — 解析任务意图→决定检索策略
  - `intent_keyword_mapper.py` — 意图→关键词映射表
  - `pattern_library.py` — Validate 阶段——已知危险模式库
  - `prompt_registry.py` — Validate 阶段——注入模板注册
  - `system_snapshot.py` — 系统状态快照——供上下文参考
- 创建配置目录与占位文件：
  - `config/context-rules.yaml` (已存在，验证)
  - `config/compression/policy.yaml` (已存在，验证)
- 创建 `architecture-context.json` 空结构
- 更新 `blueprint_registry.yaml` 登记 MOD-CONTEXT_ENGINE
- 更新蓝图 `construction_progress` → `phase_1_partial`（已完成部分）
