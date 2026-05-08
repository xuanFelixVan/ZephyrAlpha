---
task_id: "TASK-INF-0108"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2.1-B~E 盲点审计：部署自动化+数据管理+测试深度+氛围编程"
title: "盲点关闭——B.部署自动化 B4-B01~B08 + C.数据管理 B4-C01~C06 + D.测试深度 B4-D01~D08 + E.氛围编程 B4-E01~E12"
description: |
  关闭四类盲点共 34 项。
  B.部署自动化（B4-B01~B08）：CI/CD Pipeline（§5.6 六门流水线）+
  Canary Deployment（1%→100%）+ IaC（Docker Compose→Terraform）+ Blue-Green（零停机）+
  Secret Zero Problem（密钥引导）+ Immutable Infrastructure（Phase 5设计）+
  Container Escape Prevention（gVisor/Firecracker对标）+ Artifact Registry & Provenance（Sigstore/SLSA）。
  C.数据管理（B4-C01~C06）：Schema Migration（expand-contract零停机）+
  PITR（WAL增量备份）+ Data Retention Policy（自动过期/归档）+
  DB Connection Pooling（1500模块并发）+ SQLite Write Contention（busy_timeout缓解）+
  Data Locality for Multi-Region。
  D.测试深度（B4-D01~D08）：Contract Testing（Pact验证模块间契约）+
  Property-Based Testing（Hypothesis）+ Auto Test Gen from Diff（AI施工自动生成测试）+
  Mutation Testing（Mutmut衡量测试质量）+ Fuzz Testing（EventBus/ConfigCenter边界）+
  Golden File Testing（关键输出哈希锁定）+ Cross-Module Integration Test（1500模块矩阵管理）+
  Flake Detection & Quarantine。
  E.氛围编程（B4-E01~E12）：Prompt Caching（§5.3 PromptCacheManager代码骨架）+
  Context Window Budget（Token预算）+ Semantic Code Search（Code Embedding）+
  Code Gen Template System（§5.3 ModuleTemplate 骨架）+
  AI Code Review（四眼原则）+ Self-Healing Quality Gate（修复不引入新盲点）+
  AI Decision Log（ADR自动追加）+ Diff-Level Undo（精细回滚）+
  Model Fallback Chain（§5.7 ModelFallbackChain代码骨架）+
  AI Context Persistence across Sessions+ Prompt Version Control & A/B Testing+
  Token Optimization Pipeline（自动压缩上下文）。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cache.py"
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\feedback_loop\collectors\schema_migration.py"
    description: "Schema Migration——expand-contract online migration 策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\prompt_cache_manager.py"
    description: "PromptCacheManager——§5.3 代码骨架实现：缓存检查+上下文压缩+Token预算告警"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\model_fallback_chain.py"
    description: "ModelFallbackChain——§5.7 代码骨架实现：3供应商降级链"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\ai_context_persistence.py"
    description: "AI Context Persistence——跨session上下文保存/恢复/过期"
  - path: "D:\\ZephyrAlpha\\.github\\workflows\\ci.yml"
    description: "CI/CD 六门流水线——静态分析→测试→DryRun→审批→Canary→生产验证"
  - path: "D:\\ZephyrAlpha\\config\\test_orchestration.yaml"
    description: "Cross-Module Integration Test 编排策略+Flake检测配置"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\schema_migration.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\prompt_cache_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\model_fallback_chain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\ai_context_persistence.py"
  - "D:\\ZephyrAlpha\\.github\\workflows\\ci.yml"
  - "D:\\ZephyrAlpha\\config\\test_orchestration.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cache.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 PromptCacheManager 代码骨架"
    reason: "三阶段：缓存检查→上下文压缩→Token预算告警"
  - module_id: "MOD-INF-002"
    section: "§5.7 ModelFallbackChain 代码骨架"
    reason: "deepseek-chat(90%)→deepseek-reasoner(70%)→qwen-max(60%)→升级Owner"
  - module_id: "MOD-INF-002"
    section: "§5.6 CI/CD 流水线"
    reason: "六门设计：静态分析→测试→DryRun→审批→Canary→生产验证"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§2.1-B~E 四类盲点 + §5.3/§5.6/§5.7 代码骨架和流水线设计"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 35000
timeout_minutes: 90
acceptance_criteria:
  - "B. 部署自动化: CI/CD 六门流水线 YAML 配置完整——静态分析→Canary 六阶段"
  - "C. 数据管理: Schema Migration expand-contract 策略——0 停机 ALTER TABLE"
  - "C. SQLite Write Contention: busy_timeout 配置缓解多模块写入排队（B4-C05）"
  - "D. Contract Testing: Pact 验证模块间契约不被破坏（B4-D01）"
  - "D. Property-Based Testing: Hypothesis 参数化测试覆盖边界（B4-D02）"
  - "E. PromptCacheManager: 缓存命中直接返回——SHA-256 去重（B4-E01）"
  - "E. ModelFallbackChain: 3供应商降级链——AIBackendExhaustedError 终极捕获（B4-E09）"
  - "E. AI Context Persistence: 跨session上下文保存+TTL过期策略（B4-E10）"
rollback_instructions: |
  1. 删除新增 production 文件：schema_migration.py / prompt_cache_manager.py / model_fallback_chain.py / ai_context_persistence.py
  2. 删除 .github/workflows/ci.yml
  3. 删除 config/test_orchestration.yaml
  4. 如 .github/workflows/ 目录变为空→删除目录
depends_on: []
blocked_by: []
status: "done"
tags_fn:
  - "infra"
  - "security"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
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
