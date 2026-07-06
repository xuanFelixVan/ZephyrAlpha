---
doc_type: audit_report
title: 架构约束违规报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 架构约束违规报告

> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。

> 本文档由 generate_constraint_violations.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) arch_constraints表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 约束总数 | 152 |
| Open（未解决） | 152 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 50 |
| hard | 2 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 2 |
| cross_domain_violation | 34 |
| hard_limit_exceeded | 2 |
| layer_violation | 13 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-1218103 | 孤儿节点: 1218103 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218103 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1218105 | 孤儿节点: 1218105 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218105 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-1218106 | 孤儿节点: 1218106 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218106 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1218107 | 孤儿节点: 1218107 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218107 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1218108 | 孤儿节点: 1218108 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218108 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-1218109 | 孤儿节点: 1218109 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218109 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-1218111 | 孤儿节点: 1218111 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1218111 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-1218112 | 孤儿节点: 1218112 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1218112 路径 src/zephyr/autonomy_core/file_autoregister.py ... |
| V-ORPHAN-1218166 | 孤儿节点: 1218166 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1218166 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-1218186 | 孤儿节点: 1218186 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1218186 路径 src/zephyr/autonomy_core/skills/skill_factory.... |
| V-ORPHAN-1218224 | 孤儿节点: 1218224 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218224 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-1218225 | 孤儿节点: 1218225 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218225 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-1218226 | 孤儿节点: 1218226 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218226 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-1218227 | 孤儿节点: 1218227 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1218227 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-1218228 | 孤儿节点: 1218228 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218228 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-1218229 | 孤儿节点: 1218229 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218229 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-1218230 | 孤儿节点: 1218230 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218230 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-1218231 | 孤儿节点: 1218231 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218231 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1218232 | 孤儿节点: 1218232 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218232 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-1218233 | 孤儿节点: 1218233 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218233 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1218234 | 孤儿节点: 1218234 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218234 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-1218235 | 孤儿节点: 1218235 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218235 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-1218236 | 孤儿节点: 1218236 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218236 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-1218237 | 孤儿节点: 1218237 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218237 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-1218239 | 孤儿节点: 1218239 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1218239 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-1218240 | 孤儿节点: 1218240 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218240 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-1218241 | 孤儿节点: 1218241 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218241 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1218244 | 孤儿节点: 1218244 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218244 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-1218246 | 孤儿节点: 1218246 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218246 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-1218247 | 孤儿节点: 1218247 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218247 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-1218250 | 孤儿节点: 1218250 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218250 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-1218251 | 孤儿节点: 1218251 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218251 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1218252 | 孤儿节点: 1218252 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218252 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-1218255 | 孤儿节点: 1218255 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218255 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-1218256 | 孤儿节点: 1218256 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218256 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-1218259 | 孤儿节点: 1218259 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218259 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-1218260 | 孤儿节点: 1218260 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218260 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-1218261 | 孤儿节点: 1218261 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218261 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1218262 | 孤儿节点: 1218262 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218262 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-1218263 | 孤儿节点: 1218263 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218263 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-1218264 | 孤儿节点: 1218264 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218264 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-1218265 | 孤儿节点: 1218265 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218265 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-1218266 | 孤儿节点: 1218266 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218266 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-1218267 | 孤儿节点: 1218267 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218267 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-1218268 | 孤儿节点: 1218268 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1218268 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-1218269 | 孤儿节点: 1218269 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218269 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-1218270 | 孤儿节点: 1218270 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218270 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-1218271 | 孤儿节点: 1218271 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218271 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-1218272 | 孤儿节点: 1218272 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218272 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-1218273 | 孤儿节点: 1218273 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218273 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-1218274 | 孤儿节点: 1218274 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218274 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1218275 | 孤儿节点: 1218275 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218275 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-1218276 | 孤儿节点: 1218276 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218276 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-1218277 | 孤儿节点: 1218277 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218277 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-1218278 | 孤儿节点: 1218278 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218278 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-1218279 | 孤儿节点: 1218279 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218279 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-1218280 | 孤儿节点: 1218280 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218280 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-1218281 | 孤儿节点: 1218281 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218281 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-1218282 | 孤儿节点: 1218282 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218282 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1218283 | 孤儿节点: 1218283 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218283 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-1218284 | 孤儿节点: 1218284 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218284 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-1218286 | 孤儿节点: 1218286 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218286 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-1218287 | 孤儿节点: 1218287 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218287 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-1218288 | 孤儿节点: 1218288 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1218288 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-1218289 | 孤儿节点: 1218289 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1218289 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1218290 | 孤儿节点: 1218290 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1218290 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-1218291 | 孤儿节点: 1218291 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1218291 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-1218292 | 孤儿节点: 1218292 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1218292 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-1218293 | 孤儿节点: 1218293 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1218293 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-1218294 | 孤儿节点: 1218294 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1218294 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-1218295 | 孤儿节点: 1218295 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218295 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-1218296 | 孤儿节点: 1218296 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218296 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-1218297 | 孤儿节点: 1218297 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218297 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-1218300 | 孤儿节点: 1218300 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218300 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-1218301 | 孤儿节点: 1218301 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218301 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-1218302 | 孤儿节点: 1218302 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218302 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-1218303 | 孤儿节点: 1218303 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218303 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-1218304 | 孤儿节点: 1218304 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218304 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-1218306 | 孤儿节点: 1218306 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218306 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-1218307 | 孤儿节点: 1218307 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218307 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-1218308 | 孤儿节点: 1218308 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218308 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-1218309 | 孤儿节点: 1218309 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218309 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-1218310 | 孤儿节点: 1218310 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218310 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-1218311 | 孤儿节点: 1218311 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218311 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-1218312 | 孤儿节点: 1218312 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218312 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-1218313 | 孤儿节点: 1218313 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218313 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-1218314 | 孤儿节点: 1218314 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218314 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-1218315 | 孤儿节点: 1218315 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1218315 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-1218316 | 孤儿节点: 1218316 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218316 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1218317 | 孤儿节点: 1218317 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218317 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1218318 | 孤儿节点: 1218318 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218318 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-1218319 | 孤儿节点: 1218319 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218319 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1218320 | 孤儿节点: 1218320 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218320 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-ORPHAN-1218321 | 孤儿节点: 1218321 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1218321 路径 src/zephyr/data_governance/api/__init__.py 未注册... |
| V-ORPHAN-1218322 | 孤儿节点: 1218322 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1218322 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-1218323 | 孤儿节点: 1218323 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1218323 路径 src/zephyr/data_governance/core/__init__.py 未注... |
| V-ORPHAN-1218324 | 孤儿节点: 1218324 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1218324 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-1218325 | 孤儿节点: 1218325 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1218325 路径 src/zephyr/data_governance/infrastructure/__in... |
| V-ORPHAN-1218326 | 孤儿节点: 1218326 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1218326 路径 src/zephyr/data_governance/models/__init__.py ... |
| V-ORPHAN-1218327 | 孤儿节点: 1218327 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1218327 路径 src/zephyr/data_governance/_extensions/__init_... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 480 超过上限 1... |
| V-CAP-D_TRADING | 容量超限: D_TRADING | capacity_exceeded | D_TRADING |  | hard | gate | 域 D_TRADING(交易运营) production 节点 280 超过上限 150，需拆分或提升上限 (ARCH-... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_GOVERNANCE | 跨域违规: D_AUTONOMY_CORE -> D_GOVERNANCE | cross_domain_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOVERNANCE |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTELLIGENCE |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY_LLM | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY_LLM | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY_LLM | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SECURITY_LLM |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_PERM -> D_SECURITY |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_BACKTEST -> D_GOVERNANCE |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | gate | 跨域依赖未声明: D_EX_CORE -> D_BACKTEST |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_EX_CORE -> D_TRADING |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_FACTOR -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_FRONTEND-D_GOVERNANCE | 跨域违规: D_FRONTEND -> D_GOVERNANCE | cross_domain_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_FRONTEND -> D_GOVERNANCE |
| V-CROSS-D_FRONTEND-D_TRADING | 跨域违规: D_FRONTEND -> D_TRADING | cross_domain_violation | D_FRONTEND | D_TRADING | error | gate | 跨域依赖未声明: D_FRONTEND -> D_TRADING |
| V-CROSS-D_GOVERNANCE-D_FACTOR | 跨域违规: D_GOVERNANCE -> D_FACTOR | cross_domain_violation | D_GOVERNANCE | D_FACTOR | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_FACTOR |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_A2A |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INTELLIGENCE |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_OPS |
| V-CROSS-D_GOVERNANCE-D_PF_CORE | 跨域违规: D_GOVERNANCE -> D_PF_CORE | cross_domain_violation | D_GOVERNANCE | D_PF_CORE | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_PF_CORE |
| V-CROSS-D_GOVERNANCE-D_REPORTING | 跨域违规: D_GOVERNANCE -> D_REPORTING | cross_domain_violation | D_GOVERNANCE | D_REPORTING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_REPORTING |
| V-CROSS-D_GOVERNANCE-D_SECURITY | 跨域违规: D_GOVERNANCE -> D_SECURITY | cross_domain_violation | D_GOVERNANCE | D_SECURITY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_SECURITY |
| V-CROSS-D_GOVERNANCE-D_SECURITY_LLM | 跨域违规: D_GOVERNANCE -> D_SECURITY_LLM | cross_domain_violation | D_GOVERNANCE | D_SECURITY_LLM | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_SECURITY_LLM |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_TRADING |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOVERNANCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOVERNANCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOVERNANCE |
| V-CROSS-D_GOV_ENFORCEMENT-D_INFRA_RECOVERY | 跨域违规: D_GOV_ENFORCEMENT -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_ENFORCEMENT | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_INFRA_RECOVERY |
| V-CROSS-D_GOV_ENFORCEMENT-D_INTEGRATION | 跨域违规: D_GOV_ENFORCEMENT -> D_INTEGRATION | cross_domain_violation | D_GOV_ENFORCEMENT | D_INTEGRATION | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_INTEGRATION |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_SECURITY |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOVERNANCE |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_TELEMETRY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_TRADING |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOVERNANCE |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_SECURITY -> D_GOV_ENFORCEMENT |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 480 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 1218212 -> 1218441 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1218183 -> 1218943 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 1218135 -> 1219438 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1218390 -> 1218847 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 1218406 -> 1220506 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 1219151 -> 1218718 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1219158 -> 1219988 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1219170 -> 1218496 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1219072 -> 1219397 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1219180 -> 1219918 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 1218104 -> 1220393 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1218739 -> 1218971 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1218611 -> 1218884 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1218103 | 孤儿节点: 1218103 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218105 | 孤儿节点: 1218105 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218106 | 孤儿节点: 1218106 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218107 | 孤儿节点: 1218107 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218108 | 孤儿节点: 1218108 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218109 | 孤儿节点: 1218109 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218111 | 孤儿节点: 1218111 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1218112 | 孤儿节点: 1218112 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1218166 | 孤儿节点: 1218166 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1218186 | 孤儿节点: 1218186 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1218224 | 孤儿节点: 1218224 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218225 | 孤儿节点: 1218225 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218226 | 孤儿节点: 1218226 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218227 | 孤儿节点: 1218227 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1218228 | 孤儿节点: 1218228 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218229 | 孤儿节点: 1218229 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218230 | 孤儿节点: 1218230 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218231 | 孤儿节点: 1218231 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218232 | 孤儿节点: 1218232 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218233 | 孤儿节点: 1218233 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218234 | 孤儿节点: 1218234 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218235 | 孤儿节点: 1218235 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218236 | 孤儿节点: 1218236 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218237 | 孤儿节点: 1218237 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218239 | 孤儿节点: 1218239 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1218240 | 孤儿节点: 1218240 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218241 | 孤儿节点: 1218241 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218244 | 孤儿节点: 1218244 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218246 | 孤儿节点: 1218246 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218247 | 孤儿节点: 1218247 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218250 | 孤儿节点: 1218250 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218251 | 孤儿节点: 1218251 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218252 | 孤儿节点: 1218252 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218255 | 孤儿节点: 1218255 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218256 | 孤儿节点: 1218256 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218259 | 孤儿节点: 1218259 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218260 | 孤儿节点: 1218260 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218261 | 孤儿节点: 1218261 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218262 | 孤儿节点: 1218262 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218263 | 孤儿节点: 1218263 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218264 | 孤儿节点: 1218264 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218265 | 孤儿节点: 1218265 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218266 | 孤儿节点: 1218266 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218267 | 孤儿节点: 1218267 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218268 | 孤儿节点: 1218268 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1218269 | 孤儿节点: 1218269 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218270 | 孤儿节点: 1218270 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218271 | 孤儿节点: 1218271 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218272 | 孤儿节点: 1218272 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218273 | 孤儿节点: 1218273 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218274 | 孤儿节点: 1218274 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218275 | 孤儿节点: 1218275 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218276 | 孤儿节点: 1218276 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218277 | 孤儿节点: 1218277 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218278 | 孤儿节点: 1218278 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218279 | 孤儿节点: 1218279 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218280 | 孤儿节点: 1218280 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218281 | 孤儿节点: 1218281 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218282 | 孤儿节点: 1218282 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218283 | 孤儿节点: 1218283 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218284 | 孤儿节点: 1218284 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218286 | 孤儿节点: 1218286 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218287 | 孤儿节点: 1218287 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218288 | 孤儿节点: 1218288 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1218289 | 孤儿节点: 1218289 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1218290 | 孤儿节点: 1218290 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1218291 | 孤儿节点: 1218291 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1218292 | 孤儿节点: 1218292 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1218293 | 孤儿节点: 1218293 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1218294 | 孤儿节点: 1218294 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1218295 | 孤儿节点: 1218295 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218296 | 孤儿节点: 1218296 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218297 | 孤儿节点: 1218297 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218300 | 孤儿节点: 1218300 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218301 | 孤儿节点: 1218301 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218302 | 孤儿节点: 1218302 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218303 | 孤儿节点: 1218303 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218304 | 孤儿节点: 1218304 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218306 | 孤儿节点: 1218306 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218307 | 孤儿节点: 1218307 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218308 | 孤儿节点: 1218308 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218309 | 孤儿节点: 1218309 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218310 | 孤儿节点: 1218310 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218311 | 孤儿节点: 1218311 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218312 | 孤儿节点: 1218312 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218313 | 孤儿节点: 1218313 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218314 | 孤儿节点: 1218314 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218315 | 孤儿节点: 1218315 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1218316 | 孤儿节点: 1218316 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218317 | 孤儿节点: 1218317 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218318 | 孤儿节点: 1218318 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218319 | 孤儿节点: 1218319 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218320 | 孤儿节点: 1218320 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218321 | 孤儿节点: 1218321 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1218322 | 孤儿节点: 1218322 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1218323 | 孤儿节点: 1218323 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1218324 | 孤儿节点: 1218324 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1218325 | 孤儿节点: 1218325 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1218326 | 孤儿节点: 1218326 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1218327 | 孤儿节点: 1218327 | orphan_node | D_DATA_GOV |  | warn | open |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | open |
| V-CAP-D_TRADING | 容量超限: D_TRADING | capacity_exceeded | D_TRADING |  | hard | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOVERNANCE | 跨域违规: D_AUTONOMY_CORE -> D_GOVERNANCE | cross_domain_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY_LLM | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY_LLM | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY_LLM | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | open |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | open |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | open |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | open |
| V-CROSS-D_FACTOR-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_FACTOR -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_FACTOR | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_FRONTEND-D_GOVERNANCE | 跨域违规: D_FRONTEND -> D_GOVERNANCE | cross_domain_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-CROSS-D_FRONTEND-D_TRADING | 跨域违规: D_FRONTEND -> D_TRADING | cross_domain_violation | D_FRONTEND | D_TRADING | error | open |
| V-CROSS-D_GOVERNANCE-D_FACTOR | 跨域违规: D_GOVERNANCE -> D_FACTOR | cross_domain_violation | D_GOVERNANCE | D_FACTOR | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_ENFORCEMENT | 跨域违规: D_GOVERNANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_GOVERNANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOVERNANCE-D_INTELLIGENCE | 跨域违规: D_GOVERNANCE -> D_INTELLIGENCE | cross_domain_violation | D_GOVERNANCE | D_INTELLIGENCE | error | open |
| V-CROSS-D_GOVERNANCE-D_OPS | 跨域违规: D_GOVERNANCE -> D_OPS | cross_domain_violation | D_GOVERNANCE | D_OPS | error | open |
| V-CROSS-D_GOVERNANCE-D_PF_CORE | 跨域违规: D_GOVERNANCE -> D_PF_CORE | cross_domain_violation | D_GOVERNANCE | D_PF_CORE | error | open |
| V-CROSS-D_GOVERNANCE-D_REPORTING | 跨域违规: D_GOVERNANCE -> D_REPORTING | cross_domain_violation | D_GOVERNANCE | D_REPORTING | error | open |
| V-CROSS-D_GOVERNANCE-D_SECURITY | 跨域违规: D_GOVERNANCE -> D_SECURITY | cross_domain_violation | D_GOVERNANCE | D_SECURITY | error | open |
| V-CROSS-D_GOVERNANCE-D_SECURITY_LLM | 跨域违规: D_GOVERNANCE -> D_SECURITY_LLM | cross_domain_violation | D_GOVERNANCE | D_SECURITY_LLM | error | open |
| V-CROSS-D_GOVERNANCE-D_TRADING | 跨域违规: D_GOVERNANCE -> D_TRADING | cross_domain_violation | D_GOVERNANCE | D_TRADING | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOVERNANCE | 跨域违规: D_GOV_ENFORCEMENT -> D_GOVERNANCE | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOVERNANCE | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_INFRA_RECOVERY | 跨域违规: D_GOV_ENFORCEMENT -> D_INFRA_RECOVERY | cross_domain_violation | D_GOV_ENFORCEMENT | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_INTEGRATION | 跨域违规: D_GOV_ENFORCEMENT -> D_INTEGRATION | cross_domain_violation | D_GOV_ENFORCEMENT | D_INTEGRATION | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_SECURITY | 跨域违规: D_GOV_ENFORCEMENT -> D_SECURITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_SECURITY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOVERNANCE | 跨域违规: D_INFRA_RUNTIME -> D_GOVERNANCE | cross_domain_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_TELEMETRY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_TELEMETRY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_TELEMETRY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-CROSS-D_SECURITY-D_GOVERNANCE | 跨域违规: D_SECURITY -> D_GOVERNANCE | cross_domain_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-CROSS-D_SECURITY-D_GOV_ENFORCEMENT | 跨域违规: D_SECURITY -> D_GOV_ENFORCEMENT | cross_domain_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | open |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | open |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | open |
