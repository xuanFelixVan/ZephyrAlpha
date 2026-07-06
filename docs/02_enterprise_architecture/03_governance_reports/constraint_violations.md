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
| V-ORPHAN-1059178 | 孤儿节点: 1059178 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059178 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1059179 | 孤儿节点: 1059179 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059179 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1059180 | 孤儿节点: 1059180 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059180 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1059181 | 孤儿节点: 1059181 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059181 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-1059182 | 孤儿节点: 1059182 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059182 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-1059183 | 孤儿节点: 1059183 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059183 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-1059185 | 孤儿节点: 1059185 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 1059185 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-1059187 | 孤儿节点: 1059187 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1059187 路径 src/zephyr/autonomy_core/file_autoregister.py ... |
| V-ORPHAN-1059195 | 孤儿节点: 1059195 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1059195 路径 src/zephyr/autonomy_core/vibe_coding_quality_g... |
| V-ORPHAN-1059238 | 孤儿节点: 1059238 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1059238 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-1059297 | 孤儿节点: 1059297 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059297 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-1059298 | 孤儿节点: 1059298 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 1059298 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-1059300 | 孤儿节点: 1059300 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059300 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-1059301 | 孤儿节点: 1059301 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059301 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-1059302 | 孤儿节点: 1059302 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059302 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-1059303 | 孤儿节点: 1059303 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059303 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-1059304 | 孤儿节点: 1059304 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059304 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-1059305 | 孤儿节点: 1059305 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059305 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-1059306 | 孤儿节点: 1059306 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059306 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1059307 | 孤儿节点: 1059307 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059307 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-1059308 | 孤儿节点: 1059308 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059308 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-1059309 | 孤儿节点: 1059309 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059309 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-1059310 | 孤儿节点: 1059310 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059310 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-1059311 | 孤儿节点: 1059311 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059311 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-1059312 | 孤儿节点: 1059312 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 1059312 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-1059313 | 孤儿节点: 1059313 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059313 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-1059314 | 孤儿节点: 1059314 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059314 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1059315 | 孤儿节点: 1059315 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059315 路径 src/zephyr/backtest/core/data_handler.py 未注册到目... |
| V-ORPHAN-1059316 | 孤儿节点: 1059316 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059316 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-1059318 | 孤儿节点: 1059318 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059318 路径 src/zephyr/backtest/core/matching_engine.py 未注... |
| V-ORPHAN-1059319 | 孤儿节点: 1059319 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059319 路径 src/zephyr/backtest/core/matching_logic.py 未注册... |
| V-ORPHAN-1059320 | 孤儿节点: 1059320 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059320 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-1059321 | 孤儿节点: 1059321 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059321 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-1059322 | 孤儿节点: 1059322 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059322 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-1059323 | 孤儿节点: 1059323 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059323 路径 src/zephyr/backtest/core/portfolio.py 未注册到目录树 |
| V-ORPHAN-1059324 | 孤儿节点: 1059324 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059324 路径 src/zephyr/backtest/core/tick_replay.py 未注册到目录... |
| V-ORPHAN-1059325 | 孤儿节点: 1059325 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059325 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-1059326 | 孤儿节点: 1059326 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059326 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1059329 | 孤儿节点: 1059329 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059329 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-1059331 | 孤儿节点: 1059331 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059331 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-1059332 | 孤儿节点: 1059332 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059332 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-1059334 | 孤儿节点: 1059334 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059334 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-1059335 | 孤儿节点: 1059335 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059335 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-1059336 | 孤儿节点: 1059336 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059336 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1059337 | 孤儿节点: 1059337 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 1059337 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-1059338 | 孤儿节点: 1059338 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059338 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-1059339 | 孤儿节点: 1059339 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059339 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-1059340 | 孤儿节点: 1059340 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059340 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-1059341 | 孤儿节点: 1059341 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059341 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-1059342 | 孤儿节点: 1059342 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059342 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-1059343 | 孤儿节点: 1059343 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059343 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-1059344 | 孤儿节点: 1059344 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059344 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-1059345 | 孤儿节点: 1059345 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059345 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-1059346 | 孤儿节点: 1059346 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059346 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-1059347 | 孤儿节点: 1059347 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059347 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-1059348 | 孤儿节点: 1059348 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059348 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-1059349 | 孤儿节点: 1059349 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059349 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-1059350 | 孤儿节点: 1059350 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059350 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1059351 | 孤儿节点: 1059351 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059351 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-1059352 | 孤儿节点: 1059352 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059352 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-1059353 | 孤儿节点: 1059353 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059353 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-1059354 | 孤儿节点: 1059354 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059354 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-1059355 | 孤儿节点: 1059355 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059355 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-1059356 | 孤儿节点: 1059356 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059356 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-1059357 | 孤儿节点: 1059357 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059357 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-1059358 | 孤儿节点: 1059358 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059358 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1059359 | 孤儿节点: 1059359 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059359 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-1059360 | 孤儿节点: 1059360 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059360 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-1059361 | 孤儿节点: 1059361 | orphan_node | D_GOV_ENFORCEMENT |  | warn | advisory | 节点 1059361 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-1059363 | 孤儿节点: 1059363 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1059363 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-1059364 | 孤儿节点: 1059364 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1059364 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-1059365 | 孤儿节点: 1059365 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1059365 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1059366 | 孤儿节点: 1059366 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1059366 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-1059367 | 孤儿节点: 1059367 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1059367 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-1059368 | 孤儿节点: 1059368 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 1059368 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-1059369 | 孤儿节点: 1059369 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059369 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-1059370 | 孤儿节点: 1059370 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059370 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-1059372 | 孤儿节点: 1059372 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059372 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-1059374 | 孤儿节点: 1059374 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059374 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-1059375 | 孤儿节点: 1059375 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059375 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-1059376 | 孤儿节点: 1059376 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059376 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-1059379 | 孤儿节点: 1059379 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059379 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-1059380 | 孤儿节点: 1059380 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059380 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-1059381 | 孤儿节点: 1059381 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059381 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-1059382 | 孤儿节点: 1059382 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059382 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-1059383 | 孤儿节点: 1059383 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059383 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-1059384 | 孤儿节点: 1059384 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059384 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-1059385 | 孤儿节点: 1059385 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059385 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-1059386 | 孤儿节点: 1059386 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059386 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-1059387 | 孤儿节点: 1059387 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059387 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-1059388 | 孤儿节点: 1059388 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059388 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-1059389 | 孤儿节点: 1059389 | orphan_node | D_GOVERNANCE |  | warn | advisory | 节点 1059389 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-1059390 | 孤儿节点: 1059390 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059390 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-1059391 | 孤儿节点: 1059391 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059391 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-1059392 | 孤儿节点: 1059392 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059392 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-1059393 | 孤儿节点: 1059393 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059393 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-1059394 | 孤儿节点: 1059394 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059394 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-1059395 | 孤儿节点: 1059395 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1059395 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-1059396 | 孤儿节点: 1059396 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 1059396 路径 src/zephyr/data_governance/api/__init__.py 未注册... |
| V-ORPHAN-1059397 | 孤儿节点: 1059397 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 1059397 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(registry_management) production 节点 479 超过上限 1... |
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
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(registry_management) production 节点 479 超过硬上限 ... |
| V-HARD150-D_TRADING | 硬上限违规: D_TRADING | hard_limit_exceeded | D_TRADING |  | error | gate | 域 D_TRADING(交易运营) production 节点 280 超过硬上限 150 (ARCH-CAP-002 ... |
| V-LAYER-D_AUTONOMY_CORE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOVERNANCE | error | gate | 层级违规: 1059288 -> 1059516 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1059259 -> 1060015 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 1059209 -> 1060514 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 1059465 -> 1059921 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 1059478 -> 1061579 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_A2A | D_GOVERNANCE | error | gate | 层级违规: 1060225 -> 1059795 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_A2A-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_A2A | D_SHARED | error | gate | 层级违规: 1060234 -> 1061063 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOVERNANCE | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOVERNANCE | error | gate | 层级违规: 1060247 -> 1059569 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 1060144 -> 1060476 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 1060257 -> 1060990 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 1059177 -> 1061463 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 1059811 -> 1059780 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 1059681 -> 1059960 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-1059178 | 孤儿节点: 1059178 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059179 | 孤儿节点: 1059179 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059180 | 孤儿节点: 1059180 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059181 | 孤儿节点: 1059181 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059182 | 孤儿节点: 1059182 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059183 | 孤儿节点: 1059183 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059185 | 孤儿节点: 1059185 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-1059187 | 孤儿节点: 1059187 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1059195 | 孤儿节点: 1059195 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1059238 | 孤儿节点: 1059238 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1059297 | 孤儿节点: 1059297 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059298 | 孤儿节点: 1059298 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-1059300 | 孤儿节点: 1059300 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059301 | 孤儿节点: 1059301 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059302 | 孤儿节点: 1059302 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059303 | 孤儿节点: 1059303 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059304 | 孤儿节点: 1059304 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059305 | 孤儿节点: 1059305 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059306 | 孤儿节点: 1059306 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059307 | 孤儿节点: 1059307 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059308 | 孤儿节点: 1059308 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059309 | 孤儿节点: 1059309 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059310 | 孤儿节点: 1059310 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059311 | 孤儿节点: 1059311 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059312 | 孤儿节点: 1059312 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-1059313 | 孤儿节点: 1059313 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059314 | 孤儿节点: 1059314 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059315 | 孤儿节点: 1059315 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059316 | 孤儿节点: 1059316 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059318 | 孤儿节点: 1059318 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059319 | 孤儿节点: 1059319 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059320 | 孤儿节点: 1059320 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059321 | 孤儿节点: 1059321 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059322 | 孤儿节点: 1059322 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059323 | 孤儿节点: 1059323 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059324 | 孤儿节点: 1059324 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059325 | 孤儿节点: 1059325 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059326 | 孤儿节点: 1059326 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059329 | 孤儿节点: 1059329 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059331 | 孤儿节点: 1059331 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059332 | 孤儿节点: 1059332 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059334 | 孤儿节点: 1059334 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059335 | 孤儿节点: 1059335 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059336 | 孤儿节点: 1059336 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059337 | 孤儿节点: 1059337 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-1059338 | 孤儿节点: 1059338 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059339 | 孤儿节点: 1059339 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059340 | 孤儿节点: 1059340 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059341 | 孤儿节点: 1059341 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059342 | 孤儿节点: 1059342 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059343 | 孤儿节点: 1059343 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059344 | 孤儿节点: 1059344 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059345 | 孤儿节点: 1059345 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059346 | 孤儿节点: 1059346 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059347 | 孤儿节点: 1059347 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059348 | 孤儿节点: 1059348 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059349 | 孤儿节点: 1059349 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059350 | 孤儿节点: 1059350 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059351 | 孤儿节点: 1059351 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059352 | 孤儿节点: 1059352 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059353 | 孤儿节点: 1059353 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059354 | 孤儿节点: 1059354 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059355 | 孤儿节点: 1059355 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059356 | 孤儿节点: 1059356 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059357 | 孤儿节点: 1059357 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059358 | 孤儿节点: 1059358 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059359 | 孤儿节点: 1059359 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059360 | 孤儿节点: 1059360 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059361 | 孤儿节点: 1059361 | orphan_node | D_GOV_ENFORCEMENT |  | warn | open |
| V-ORPHAN-1059363 | 孤儿节点: 1059363 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1059364 | 孤儿节点: 1059364 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1059365 | 孤儿节点: 1059365 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1059366 | 孤儿节点: 1059366 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1059367 | 孤儿节点: 1059367 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1059368 | 孤儿节点: 1059368 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-1059369 | 孤儿节点: 1059369 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059370 | 孤儿节点: 1059370 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059372 | 孤儿节点: 1059372 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059374 | 孤儿节点: 1059374 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059375 | 孤儿节点: 1059375 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059376 | 孤儿节点: 1059376 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059379 | 孤儿节点: 1059379 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059380 | 孤儿节点: 1059380 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059381 | 孤儿节点: 1059381 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059382 | 孤儿节点: 1059382 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059383 | 孤儿节点: 1059383 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059384 | 孤儿节点: 1059384 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059385 | 孤儿节点: 1059385 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059386 | 孤儿节点: 1059386 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059387 | 孤儿节点: 1059387 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059388 | 孤儿节点: 1059388 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1059389 | 孤儿节点: 1059389 | orphan_node | D_GOVERNANCE |  | warn | open |
| V-ORPHAN-1059390 | 孤儿节点: 1059390 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1059391 | 孤儿节点: 1059391 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1059392 | 孤儿节点: 1059392 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1059393 | 孤儿节点: 1059393 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1059394 | 孤儿节点: 1059394 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-1059395 | 孤儿节点: 1059395 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1059396 | 孤儿节点: 1059396 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-1059397 | 孤儿节点: 1059397 | orphan_node | D_DATA_ENG |  | warn | open |
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
