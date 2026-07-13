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
| 约束总数 | 164 |
| Open（未解决） | 164 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 64 |
| warn | 100 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| cross_domain_violation | 41 |
| layer_violation | 22 |
| orphan_node | 100 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-ORPHAN-2263184 | 孤儿节点: 2263184 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263184 路径 src/zephyr/alt_data/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2263185 | 孤儿节点: 2263185 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263185 路径 src/zephyr/alt_data/__init__.py 未注册到目录树 |
| V-ORPHAN-2263186 | 孤儿节点: 2263186 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263186 路径 src/zephyr/alt_data/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2263187 | 孤儿节点: 2263187 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263187 路径 src/zephyr/alt_data/infrastructure/__init__.py... |
| V-ORPHAN-2263188 | 孤儿节点: 2263188 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263188 路径 src/zephyr/alt_data/services/__init__.py 未注册到目... |
| V-ORPHAN-2263189 | 孤儿节点: 2263189 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263189 路径 src/zephyr/alt_data/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2263190 | 孤儿节点: 2263190 | orphan_node | D_ALT_DATA |  | warn | advisory | 节点 2263190 路径 src/zephyr/alt_data/_extensions/__init__.py 未注... |
| V-ORPHAN-2263243 | 孤儿节点: 2263243 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2263243 路径 src/zephyr/autonomy_core/integration/__init__.... |
| V-ORPHAN-2263304 | 孤儿节点: 2263304 | orphan_node | D_AUTONOMY_CORE |  | warn | advisory | 节点 2263304 路径 src/zephyr/autonomy_core/skills/__init__.py 未注... |
| V-ORPHAN-2263305 | 孤儿节点: 2263305 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263305 路径 src/zephyr/autonomy_perm/__init__.py 未注册到目录树 |
| V-ORPHAN-2263306 | 孤儿节点: 2263306 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263306 路径 src/zephyr/autonomy_perm/api/__init__.py 未注册到目... |
| V-ORPHAN-2263307 | 孤儿节点: 2263307 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263307 路径 src/zephyr/autonomy_perm/infrastructure/__init... |
| V-ORPHAN-2263308 | 孤儿节点: 2263308 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263308 路径 src/zephyr/autonomy_perm/core/__init__.py 未注册到... |
| V-ORPHAN-2263309 | 孤儿节点: 2263309 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263309 路径 src/zephyr/autonomy_perm/red_blue_validator/by... |
| V-ORPHAN-2263310 | 孤儿节点: 2263310 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263310 路径 src/zephyr/autonomy_perm/models/__init__.py 未注... |
| V-ORPHAN-2263311 | 孤儿节点: 2263311 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263311 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2263312 | 孤儿节点: 2263312 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263312 路径 src/zephyr/autonomy_perm/red_blue_validator/at... |
| V-ORPHAN-2263313 | 孤儿节点: 2263313 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263313 路径 src/zephyr/autonomy_perm/red_blue_validator/co... |
| V-ORPHAN-2263314 | 孤儿节点: 2263314 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263314 路径 src/zephyr/autonomy_perm/red_blue_validator/de... |
| V-ORPHAN-2263315 | 孤儿节点: 2263315 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263315 路径 src/zephyr/autonomy_perm/_extensions/__init__.... |
| V-ORPHAN-2263316 | 孤儿节点: 2263316 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263316 路径 src/zephyr/autonomy_perm/red_blue_validator/__... |
| V-ORPHAN-2263317 | 孤儿节点: 2263317 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263317 路径 src/zephyr/autonomy_perm/services/__init__.py ... |
| V-ORPHAN-2263318 | 孤儿节点: 2263318 | orphan_node | D_AUTONOMY_PERM |  | warn | advisory | 节点 2263318 路径 src/zephyr/autonomy_perm/red_blue_validator/ga... |
| V-ORPHAN-2263319 | 孤儿节点: 2263319 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263319 路径 src/zephyr/backtest/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2263320 | 孤儿节点: 2263320 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263320 路径 src/zephyr/backtest/__init__.py 未注册到目录树 |
| V-ORPHAN-2263321 | 孤儿节点: 2263321 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263321 路径 src/zephyr/backtest/core/decision_gate.py 未注册到... |
| V-ORPHAN-2263322 | 孤儿节点: 2263322 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263322 路径 src/zephyr/backtest/core/data_handler.py 未注册到目... |
| V-ORPHAN-2263326 | 孤儿节点: 2263326 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263326 路径 src/zephyr/backtest/core/pit_manager.py 未注册到目录... |
| V-ORPHAN-2263327 | 孤儿节点: 2263327 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263327 路径 src/zephyr/backtest/core/overfitting_detector.... |
| V-ORPHAN-2263328 | 孤儿节点: 2263328 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263328 路径 src/zephyr/backtest/core/metrics.py 未注册到目录树 |
| V-ORPHAN-2263331 | 孤儿节点: 2263331 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263331 路径 src/zephyr/backtest/core/walk_forward.py 未注册到目... |
| V-ORPHAN-2263332 | 孤儿节点: 2263332 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263332 路径 src/zephyr/backtest/infrastructure/__init__.py... |
| V-ORPHAN-2263333 | 孤儿节点: 2263333 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263333 路径 src/zephyr/backtest/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2263338 | 孤儿节点: 2263338 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263338 路径 src/zephyr/backtest/io/backtest_result_sink.py... |
| V-ORPHAN-2263339 | 孤儿节点: 2263339 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263339 路径 src/zephyr/backtest/io/result_repository.py 未注... |
| V-ORPHAN-2263340 | 孤儿节点: 2263340 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263340 路径 src/zephyr/backtest/_extensions/__init__.py 未注... |
| V-ORPHAN-2263341 | 孤儿节点: 2263341 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263341 路径 src/zephyr/backtest/io/__init__.py 未注册到目录树 |
| V-ORPHAN-2263342 | 孤儿节点: 2263342 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263342 路径 src/zephyr/backtest/services/__init__.py 未注册到目... |
| V-ORPHAN-2263343 | 孤儿节点: 2263343 | orphan_node | D_BACKTEST |  | warn | advisory | 节点 2263343 路径 src/zephyr/backtest/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2263344 | 孤儿节点: 2263344 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263344 路径 src/zephyr/compliance/compliance_manager.py 未注... |
| V-ORPHAN-2263345 | 孤儿节点: 2263345 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263345 路径 src/zephyr/compliance/aisg_sandbox.py 未注册到目录树 |
| V-ORPHAN-2263346 | 孤儿节点: 2263346 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263346 路径 src/zephyr/compliance/artifact_scanner.py 未注册到... |
| V-ORPHAN-2263347 | 孤儿节点: 2263347 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263347 路径 src/zephyr/compliance/default_security_gateway... |
| V-ORPHAN-2263348 | 孤儿节点: 2263348 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263348 路径 src/zephyr/compliance/evidence_pack.py 未注册到目录树 |
| V-ORPHAN-2263349 | 孤儿节点: 2263349 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263349 路径 src/zephyr/compliance/financial_compliance.py ... |
| V-ORPHAN-2263350 | 孤儿节点: 2263350 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263350 路径 src/zephyr/compliance/integrity.py 未注册到目录树 |
| V-ORPHAN-2263351 | 孤儿节点: 2263351 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263351 路径 src/zephyr/compliance/merkle_hourly.py 未注册到目录树 |
| V-ORPHAN-2263352 | 孤儿节点: 2263352 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263352 路径 src/zephyr/compliance/security_gateway_base.py... |
| V-ORPHAN-2263353 | 孤儿节点: 2263353 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263353 路径 src/zephyr/compliance/__init__.py 未注册到目录树 |
| V-ORPHAN-2263354 | 孤儿节点: 2263354 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263354 路径 src/zephyr/compliance/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2263355 | 孤儿节点: 2263355 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263355 路径 src/zephyr/compliance/audit_trail/__init__.py ... |
| V-ORPHAN-2263356 | 孤儿节点: 2263356 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263356 路径 src/zephyr/compliance/audit_orchestrator/__ini... |
| V-ORPHAN-2263357 | 孤儿节点: 2263357 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263357 路径 src/zephyr/compliance/audit_trail/bridges/__in... |
| V-ORPHAN-2263358 | 孤儿节点: 2263358 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263358 路径 src/zephyr/compliance/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2263359 | 孤儿节点: 2263359 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263359 路径 src/zephyr/compliance/behavioral_admission/__i... |
| V-ORPHAN-2263360 | 孤儿节点: 2263360 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263360 路径 src/zephyr/compliance/compliance_gate_a6/__ini... |
| V-ORPHAN-2263361 | 孤儿节点: 2263361 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263361 路径 src/zephyr/compliance/behavioral_auditor/__ini... |
| V-ORPHAN-2263362 | 孤儿节点: 2263362 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263362 路径 src/zephyr/compliance/models/__init__.py 未注册到目... |
| V-ORPHAN-2263363 | 孤儿节点: 2263363 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263363 路径 src/zephyr/compliance/implementations/__init__... |
| V-ORPHAN-2263364 | 孤儿节点: 2263364 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263364 路径 src/zephyr/compliance/infrastructure/__init__.... |
| V-ORPHAN-2263365 | 孤儿节点: 2263365 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263365 路径 src/zephyr/compliance/zero_knowledge_audit_stu... |
| V-ORPHAN-2263366 | 孤儿节点: 2263366 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263366 路径 src/zephyr/compliance/services/__init__.py 未注册... |
| V-ORPHAN-2263368 | 孤儿节点: 2263368 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2263368 路径 src/zephyr/cross_asset/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2263369 | 孤儿节点: 2263369 | orphan_node | D_COMPLIANCE |  | warn | advisory | 节点 2263369 路径 src/zephyr/compliance/_extensions/__init__.py ... |
| V-ORPHAN-2263370 | 孤儿节点: 2263370 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2263370 路径 src/zephyr/cross_asset/core/__init__.py 未注册到目录... |
| V-ORPHAN-2263371 | 孤儿节点: 2263371 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2263371 路径 src/zephyr/cross_asset/infrastructure/__init__... |
| V-ORPHAN-2263372 | 孤儿节点: 2263372 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2263372 路径 src/zephyr/cross_asset/models/__init__.py 未注册到... |
| V-ORPHAN-2263373 | 孤儿节点: 2263373 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2263373 路径 src/zephyr/cross_asset/services/__init__.py 未注... |
| V-ORPHAN-2263374 | 孤儿节点: 2263374 | orphan_node | D_CROSS_ASSET |  | warn | advisory | 节点 2263374 路径 src/zephyr/cross_asset/_extensions/__init__.py... |
| V-ORPHAN-2263375 | 孤儿节点: 2263375 | orphan_node | D_DATA |  | warn | advisory | 节点 2263375 路径 src/zephyr/data/buffered_writer.py 未注册到目录树 |
| V-ORPHAN-2263376 | 孤儿节点: 2263376 | orphan_node | D_DATA |  | warn | advisory | 节点 2263376 路径 src/zephyr/data/alerter.py 未注册到目录树 |
| V-ORPHAN-2263377 | 孤儿节点: 2263377 | orphan_node | D_DATA |  | warn | advisory | 节点 2263377 路径 src/zephyr/data/ch_writer.py 未注册到目录树 |
| V-ORPHAN-2263378 | 孤儿节点: 2263378 | orphan_node | D_DATA |  | warn | advisory | 节点 2263378 路径 src/zephyr/data/news_dedup.py 未注册到目录树 |
| V-ORPHAN-2263380 | 孤儿节点: 2263380 | orphan_node | D_DATA |  | warn | advisory | 节点 2263380 路径 src/zephyr/data/metrics.py 未注册到目录树 |
| V-ORPHAN-2263382 | 孤儿节点: 2263382 | orphan_node | D_DATA |  | warn | advisory | 节点 2263382 路径 src/zephyr/data/progress_store.py 未注册到目录树 |
| V-ORPHAN-2263383 | 孤儿节点: 2263383 | orphan_node | D_DATA |  | warn | advisory | 节点 2263383 路径 src/zephyr/data/speed_tester.py 未注册到目录树 |
| V-ORPHAN-2263384 | 孤儿节点: 2263384 | orphan_node | D_DATA |  | warn | advisory | 节点 2263384 路径 src/zephyr/data/provider_base.py 未注册到目录树 |
| V-ORPHAN-2263385 | 孤儿节点: 2263385 | orphan_node | D_DATA |  | warn | advisory | 节点 2263385 路径 src/zephyr/data/scheduler.py 未注册到目录树 |
| V-ORPHAN-2263386 | 孤儿节点: 2263386 | orphan_node | D_DATA |  | warn | advisory | 节点 2263386 路径 src/zephyr/data/task_queue.py 未注册到目录树 |
| V-ORPHAN-2263389 | 孤儿节点: 2263389 | orphan_node | D_DATA |  | warn | advisory | 节点 2263389 路径 src/zephyr/data/implementations/cls_provider.p... |
| V-ORPHAN-2263390 | 孤儿节点: 2263390 | orphan_node | D_DATA |  | warn | advisory | 节点 2263390 路径 src/zephyr/data/__main__.py 未注册到目录树 |
| V-ORPHAN-2263391 | 孤儿节点: 2263391 | orphan_node | D_DATA |  | warn | advisory | 节点 2263391 路径 src/zephyr/data/implementations/akshare_provid... |
| V-ORPHAN-2263392 | 孤儿节点: 2263392 | orphan_node | D_DATA |  | warn | advisory | 节点 2263392 路径 src/zephyr/data/implementations/baostock_provi... |
| V-ORPHAN-2263393 | 孤儿节点: 2263393 | orphan_node | D_DATA |  | warn | advisory | 节点 2263393 路径 src/zephyr/data/implementations/eastmoney_news... |
| V-ORPHAN-2263394 | 孤儿节点: 2263394 | orphan_node | D_DATA |  | warn | advisory | 节点 2263394 路径 src/zephyr/data/implementations/miniqmt_provid... |
| V-ORPHAN-2263395 | 孤儿节点: 2263395 | orphan_node | D_DATA |  | warn | advisory | 节点 2263395 路径 src/zephyr/data/implementations/ifind_provider... |
| V-ORPHAN-2263396 | 孤儿节点: 2263396 | orphan_node | D_DATA |  | warn | advisory | 节点 2263396 路径 src/zephyr/data/implementations/rss_provider.p... |
| V-ORPHAN-2263397 | 孤儿节点: 2263397 | orphan_node | D_DATA |  | warn | advisory | 节点 2263397 路径 src/zephyr/data/implementations/tickflow_provi... |
| V-ORPHAN-2263398 | 孤儿节点: 2263398 | orphan_node | D_DATA |  | warn | advisory | 节点 2263398 路径 src/zephyr/data/implementations/tdx_provider.p... |
| V-ORPHAN-2263399 | 孤儿节点: 2263399 | orphan_node | D_DATA |  | warn | advisory | 节点 2263399 路径 src/zephyr/data/implementations/__init__.py 未注... |
| V-ORPHAN-2263400 | 孤儿节点: 2263400 | orphan_node | D_DATA |  | warn | advisory | 节点 2263400 路径 src/zephyr/data/implementations/tushare_provid... |
| V-ORPHAN-2263401 | 孤儿节点: 2263401 | orphan_node | D_DATA |  | warn | advisory | 节点 2263401 路径 src/zephyr/data/satellite_geospatial_engine/__... |
| V-ORPHAN-2263402 | 孤儿节点: 2263402 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263402 路径 src/zephyr/data_eng/__init__.py 未注册到目录树 |
| V-ORPHAN-2263403 | 孤儿节点: 2263403 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263403 路径 src/zephyr/data_eng/api/__init__.py 未注册到目录树 |
| V-ORPHAN-2263404 | 孤儿节点: 2263404 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263404 路径 src/zephyr/data_eng/core/__init__.py 未注册到目录树 |
| V-ORPHAN-2263405 | 孤儿节点: 2263405 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263405 路径 src/zephyr/data_eng/_extensions/__init__.py 未注... |
| V-ORPHAN-2263406 | 孤儿节点: 2263406 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263406 路径 src/zephyr/data_eng/models/__init__.py 未注册到目录树 |
| V-ORPHAN-2263407 | 孤儿节点: 2263407 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263407 路径 src/zephyr/data_eng/infrastructure/__init__.py... |
| V-ORPHAN-2263408 | 孤儿节点: 2263408 | orphan_node | D_DATA_GOV |  | warn | advisory | 节点 2263408 路径 src/zephyr/data_governance/__init__.py 未注册到目录树 |
| V-ORPHAN-2263409 | 孤儿节点: 2263409 | orphan_node | D_DATA_ENG |  | warn | advisory | 节点 2263409 路径 src/zephyr/data_eng/services/__init__.py 未注册到目... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_AUDIT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_AUDIT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_AUDIT |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_KB | 跨域违规: D_AUTONOMY_CORE -> D_GOV_KB | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_KB | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_KB |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_RULE | 跨域违规: D_AUTONOMY_CORE -> D_GOV_RULE | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_GOV_RULE |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INFRA_RUNTIME |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTEGRATION |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_INTELLIGENCE |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SECURITY |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SHARED |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_PERM -> D_SECURITY |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_BACKTEST -> D_GOVERNANCE |
| V-CROSS-D_COMPLIANCE-D_GOVERNANCE | 跨域违规: D_COMPLIANCE -> D_GOVERNANCE | cross_domain_violation | D_COMPLIANCE | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOVERNANCE |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_AUDIT |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_DRIFT |
| V-CROSS-D_COMPLIANCE-D_GOV_ENFORCEMENT | 跨域违规: D_COMPLIANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_COMPLIANCE | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_ENFORCEMENT |
| V-CROSS-D_COMPLIANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_COMPLIANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_COMPLIANCE-D_INFRA_RUNTIME | 跨域违规: D_COMPLIANCE -> D_INFRA_RUNTIME | cross_domain_violation | D_COMPLIANCE | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_INFRA_RUNTIME |
| V-CROSS-D_COMPLIANCE-D_SECURITY | 跨域违规: D_COMPLIANCE -> D_SECURITY | cross_domain_violation | D_COMPLIANCE | D_SECURITY | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_SECURITY |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | gate | 跨域依赖未声明: D_DATA -> D_GOV_ENFORCEMENT |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | gate | 跨域依赖未声明: D_DATA -> D_SHARED |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | gate | 跨域依赖未声明: D_EX_CORE -> D_BACKTEST |
| V-CROSS-D_EX_CORE-D_INFRASTRUCTURE | 跨域违规: D_EX_CORE -> D_INFRASTRUCTURE | cross_domain_violation | D_EX_CORE | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_EX_CORE -> D_INFRASTRUCTURE |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | gate | 跨域依赖未声明: D_EX_CORE -> D_TRADING |
| V-CROSS-D_FACTOR-D_SIGLEGACY | 跨域违规: D_FACTOR -> D_SIGLEGACY | cross_domain_violation | D_FACTOR | D_SIGLEGACY | error | gate | 跨域依赖未声明: D_FACTOR -> D_SIGLEGACY |
| V-CROSS-D_FBL_DETECTORS-D_FEEDBACK_LOOP | 跨域违规: D_FBL_DETECTORS -> D_FEEDBACK_LOOP | cross_domain_violation | D_FBL_DETECTORS | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_FBL_DETECTORS -> D_FEEDBACK_LOOP |
| V-CROSS-D_FBL_DIAGNOSERS-D_SHARED | 跨域违规: D_FBL_DIAGNOSERS -> D_SHARED | cross_domain_violation | D_FBL_DIAGNOSERS | D_SHARED | error | gate | 跨域依赖未声明: D_FBL_DIAGNOSERS -> D_SHARED |
| V-CROSS-D_FBL_VERIFICATION-D_GOV_AUDIT | 跨域违规: D_FBL_VERIFICATION -> D_GOV_AUDIT | cross_domain_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_FBL_VERIFICATION -> D_GOV_AUDIT |
| V-CROSS-D_FBL_VERIFICATION-D_SECURITY | 跨域违规: D_FBL_VERIFICATION -> D_SECURITY | cross_domain_violation | D_FBL_VERIFICATION | D_SECURITY | error | gate | 跨域依赖未声明: D_FBL_VERIFICATION -> D_SECURITY |
| V-CROSS-D_FEEDBACK_LOOP-D_AUTONOMY_CORE | 跨域违规: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE | cross_domain_violation | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DETECTORS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOVERNANCE |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_DRIFT |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_OPS_RESILIENCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RECOVERY | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RECOVERY | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RECOVERY |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_INTEGRATION |
| V-CROSS-D_FEEDBACK_LOOP-D_ORCHESTRATOR | 跨域违规: D_FEEDBACK_LOOP -> D_ORCHESTRATOR | cross_domain_violation | D_FEEDBACK_LOOP | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_ORCHESTRATOR |
| V-CROSS-D_FEEDBACK_LOOP-D_SECURITY | 跨域违规: D_FEEDBACK_LOOP -> D_SECURITY | cross_domain_violation | D_FEEDBACK_LOOP | D_SECURITY | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SECURITY |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SHARED |
| V-CROSS-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 跨域违规: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP | cross_domain_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | gate | 层级违规: 2263294 -> 2264084 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_KB | error | gate | 层级违规: 2263215 -> 2264402 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | gate | 层级违规: 2263264 -> 2264381 (L1_foundation -> L2_domain) |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | gate | 层级违规: 2263215 -> 2264823 (L1_foundation -> L2_domain) |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | gate | 层级违规: 2263757 -> 2264084 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | gate | 层级违规: 2263486 -> 2263980 (L1_foundation -> L2_domain) |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | gate | 层级违规: 2263488 -> 2264239 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | gate | 层级违规: 2263813 -> 2263984 (L1_foundation -> L2_domain) |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | gate | 层级违规: 2263826 -> 2265550 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | gate | 层级违规: 2264302 -> 2263835 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | gate | 层级违规: 2264309 -> 2264338 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | gate | 层级违规: 2264011 -> 2263917 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | gate | 层级违规: 2264021 -> 2264137 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | error | gate | 层级违规: 2264020 -> 2264356 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | gate | 层级违规: 2263904 -> 2264411 (L1_foundation -> L2_domain) |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_RULE | error | gate | 层级违规: 2263904 -> 2264362 (L1_foundation -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | gate | 层级违规: 2263183 -> 2263779 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | gate | 层级违规: 2263183 -> 2265372 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_OPS-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOVERNANCE | error | gate | 层级违规: 2263945 -> 2264044 (L1_foundation -> L2_domain) |
| V-LAYER-D_OPS-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOV_DRIFT | error | gate | 层级违规: 2263943 -> 2264264 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | gate | 层级违规: 2264228 -> 2263980 (L1_foundation -> L2_domain) |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | gate | 层级违规: 2264278 -> 2264270 (L1_foundation -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-ORPHAN-2263184 | 孤儿节点: 2263184 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263185 | 孤儿节点: 2263185 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263186 | 孤儿节点: 2263186 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263187 | 孤儿节点: 2263187 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263188 | 孤儿节点: 2263188 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263189 | 孤儿节点: 2263189 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263190 | 孤儿节点: 2263190 | orphan_node | D_ALT_DATA |  | warn | open |
| V-ORPHAN-2263243 | 孤儿节点: 2263243 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2263304 | 孤儿节点: 2263304 | orphan_node | D_AUTONOMY_CORE |  | warn | open |
| V-ORPHAN-2263305 | 孤儿节点: 2263305 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263306 | 孤儿节点: 2263306 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263307 | 孤儿节点: 2263307 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263308 | 孤儿节点: 2263308 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263309 | 孤儿节点: 2263309 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263310 | 孤儿节点: 2263310 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263311 | 孤儿节点: 2263311 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263312 | 孤儿节点: 2263312 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263313 | 孤儿节点: 2263313 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263314 | 孤儿节点: 2263314 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263315 | 孤儿节点: 2263315 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263316 | 孤儿节点: 2263316 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263317 | 孤儿节点: 2263317 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263318 | 孤儿节点: 2263318 | orphan_node | D_AUTONOMY_PERM |  | warn | open |
| V-ORPHAN-2263319 | 孤儿节点: 2263319 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263320 | 孤儿节点: 2263320 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263321 | 孤儿节点: 2263321 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263322 | 孤儿节点: 2263322 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263326 | 孤儿节点: 2263326 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263327 | 孤儿节点: 2263327 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263328 | 孤儿节点: 2263328 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263331 | 孤儿节点: 2263331 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263332 | 孤儿节点: 2263332 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263333 | 孤儿节点: 2263333 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263338 | 孤儿节点: 2263338 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263339 | 孤儿节点: 2263339 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263340 | 孤儿节点: 2263340 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263341 | 孤儿节点: 2263341 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263342 | 孤儿节点: 2263342 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263343 | 孤儿节点: 2263343 | orphan_node | D_BACKTEST |  | warn | open |
| V-ORPHAN-2263344 | 孤儿节点: 2263344 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263345 | 孤儿节点: 2263345 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263346 | 孤儿节点: 2263346 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263347 | 孤儿节点: 2263347 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263348 | 孤儿节点: 2263348 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263349 | 孤儿节点: 2263349 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263350 | 孤儿节点: 2263350 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263351 | 孤儿节点: 2263351 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263352 | 孤儿节点: 2263352 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263353 | 孤儿节点: 2263353 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263354 | 孤儿节点: 2263354 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263355 | 孤儿节点: 2263355 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263356 | 孤儿节点: 2263356 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263357 | 孤儿节点: 2263357 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263358 | 孤儿节点: 2263358 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263359 | 孤儿节点: 2263359 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263360 | 孤儿节点: 2263360 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263361 | 孤儿节点: 2263361 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263362 | 孤儿节点: 2263362 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263363 | 孤儿节点: 2263363 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263364 | 孤儿节点: 2263364 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263365 | 孤儿节点: 2263365 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263366 | 孤儿节点: 2263366 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263368 | 孤儿节点: 2263368 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2263369 | 孤儿节点: 2263369 | orphan_node | D_COMPLIANCE |  | warn | open |
| V-ORPHAN-2263370 | 孤儿节点: 2263370 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2263371 | 孤儿节点: 2263371 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2263372 | 孤儿节点: 2263372 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2263373 | 孤儿节点: 2263373 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2263374 | 孤儿节点: 2263374 | orphan_node | D_CROSS_ASSET |  | warn | open |
| V-ORPHAN-2263375 | 孤儿节点: 2263375 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263376 | 孤儿节点: 2263376 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263377 | 孤儿节点: 2263377 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263378 | 孤儿节点: 2263378 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263380 | 孤儿节点: 2263380 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263382 | 孤儿节点: 2263382 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263383 | 孤儿节点: 2263383 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263384 | 孤儿节点: 2263384 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263385 | 孤儿节点: 2263385 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263386 | 孤儿节点: 2263386 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263389 | 孤儿节点: 2263389 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263390 | 孤儿节点: 2263390 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263391 | 孤儿节点: 2263391 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263392 | 孤儿节点: 2263392 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263393 | 孤儿节点: 2263393 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263394 | 孤儿节点: 2263394 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263395 | 孤儿节点: 2263395 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263396 | 孤儿节点: 2263396 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263397 | 孤儿节点: 2263397 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263398 | 孤儿节点: 2263398 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263399 | 孤儿节点: 2263399 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263400 | 孤儿节点: 2263400 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263401 | 孤儿节点: 2263401 | orphan_node | D_DATA |  | warn | open |
| V-ORPHAN-2263402 | 孤儿节点: 2263402 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2263403 | 孤儿节点: 2263403 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2263404 | 孤儿节点: 2263404 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2263405 | 孤儿节点: 2263405 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2263406 | 孤儿节点: 2263406 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2263407 | 孤儿节点: 2263407 | orphan_node | D_DATA_ENG |  | warn | open |
| V-ORPHAN-2263408 | 孤儿节点: 2263408 | orphan_node | D_DATA_GOV |  | warn | open |
| V-ORPHAN-2263409 | 孤儿节点: 2263409 | orphan_node | D_DATA_ENG |  | warn | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_AUDIT | 跨域违规: D_AUTONOMY_CORE -> D_GOV_AUDIT | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_KB | 跨域违规: D_AUTONOMY_CORE -> D_GOV_KB | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_KB | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_GOV_RULE | 跨域违规: D_AUTONOMY_CORE -> D_GOV_RULE | cross_domain_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INFRA_RUNTIME | 跨域违规: D_AUTONOMY_CORE -> D_INFRA_RUNTIME | cross_domain_violation | D_AUTONOMY_CORE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTEGRATION | 跨域违规: D_AUTONOMY_CORE -> D_INTEGRATION | cross_domain_violation | D_AUTONOMY_CORE | D_INTEGRATION | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_INTELLIGENCE | 跨域违规: D_AUTONOMY_CORE -> D_INTELLIGENCE | cross_domain_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SHARED | 跨域违规: D_AUTONOMY_CORE -> D_SHARED | cross_domain_violation | D_AUTONOMY_CORE | D_SHARED | error | open |
| V-CROSS-D_AUTONOMY_PERM-D_SECURITY | 跨域违规: D_AUTONOMY_PERM -> D_SECURITY | cross_domain_violation | D_AUTONOMY_PERM | D_SECURITY | error | open |
| V-CROSS-D_BACKTEST-D_GOVERNANCE | 跨域违规: D_BACKTEST -> D_GOVERNANCE | cross_domain_violation | D_BACKTEST | D_GOVERNANCE | error | open |
| V-CROSS-D_COMPLIANCE-D_GOVERNANCE | 跨域违规: D_COMPLIANCE -> D_GOVERNANCE | cross_domain_violation | D_COMPLIANCE | D_GOVERNANCE | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_AUDIT | 跨域违规: D_COMPLIANCE -> D_GOV_AUDIT | cross_domain_violation | D_COMPLIANCE | D_GOV_AUDIT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_DRIFT | 跨域违规: D_COMPLIANCE -> D_GOV_DRIFT | cross_domain_violation | D_COMPLIANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_ENFORCEMENT | 跨域违规: D_COMPLIANCE -> D_GOV_ENFORCEMENT | cross_domain_violation | D_COMPLIANCE | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_COMPLIANCE-D_GOV_OPS_RESILIENCE | 跨域违规: D_COMPLIANCE -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_COMPLIANCE | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_COMPLIANCE-D_INFRA_RUNTIME | 跨域违规: D_COMPLIANCE -> D_INFRA_RUNTIME | cross_domain_violation | D_COMPLIANCE | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_COMPLIANCE-D_SECURITY | 跨域违规: D_COMPLIANCE -> D_SECURITY | cross_domain_violation | D_COMPLIANCE | D_SECURITY | error | open |
| V-CROSS-D_DATA-D_GOV_ENFORCEMENT | 跨域违规: D_DATA -> D_GOV_ENFORCEMENT | cross_domain_violation | D_DATA | D_GOV_ENFORCEMENT | error | open |
| V-CROSS-D_DATA-D_SHARED | 跨域违规: D_DATA -> D_SHARED | cross_domain_violation | D_DATA | D_SHARED | error | open |
| V-CROSS-D_EX_CORE-D_BACKTEST | 跨域违规: D_EX_CORE -> D_BACKTEST | cross_domain_violation | D_EX_CORE | D_BACKTEST | error | open |
| V-CROSS-D_EX_CORE-D_INFRASTRUCTURE | 跨域违规: D_EX_CORE -> D_INFRASTRUCTURE | cross_domain_violation | D_EX_CORE | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_EX_CORE-D_TRADING | 跨域违规: D_EX_CORE -> D_TRADING | cross_domain_violation | D_EX_CORE | D_TRADING | error | open |
| V-CROSS-D_FACTOR-D_SIGLEGACY | 跨域违规: D_FACTOR -> D_SIGLEGACY | cross_domain_violation | D_FACTOR | D_SIGLEGACY | error | open |
| V-CROSS-D_FBL_DETECTORS-D_FEEDBACK_LOOP | 跨域违规: D_FBL_DETECTORS -> D_FEEDBACK_LOOP | cross_domain_violation | D_FBL_DETECTORS | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_FBL_DIAGNOSERS-D_SHARED | 跨域违规: D_FBL_DIAGNOSERS -> D_SHARED | cross_domain_violation | D_FBL_DIAGNOSERS | D_SHARED | error | open |
| V-CROSS-D_FBL_VERIFICATION-D_GOV_AUDIT | 跨域违规: D_FBL_VERIFICATION -> D_GOV_AUDIT | cross_domain_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-CROSS-D_FBL_VERIFICATION-D_SECURITY | 跨域违规: D_FBL_VERIFICATION -> D_SECURITY | cross_domain_violation | D_FBL_VERIFICATION | D_SECURITY | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_AUTONOMY_CORE | 跨域违规: D_FEEDBACK_LOOP -> D_AUTONOMY_CORE | cross_domain_violation | D_FEEDBACK_LOOP | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DETECTORS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DETECTORS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DETECTORS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_DIAGNOSERS | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_DIAGNOSERS | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_DIAGNOSERS | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_FBL_VERIFICATION | 跨域违规: D_FEEDBACK_LOOP -> D_FBL_VERIFICATION | cross_domain_violation | D_FEEDBACK_LOOP | D_FBL_VERIFICATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOVERNANCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOVERNANCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_DRIFT | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_DRIFT | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_GOV_OPS_RESILIENCE | 跨域违规: D_FEEDBACK_LOOP -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_FEEDBACK_LOOP | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RECOVERY | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RECOVERY | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INFRA_RUNTIME | 跨域违规: D_FEEDBACK_LOOP -> D_INFRA_RUNTIME | cross_domain_violation | D_FEEDBACK_LOOP | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_INTEGRATION | 跨域违规: D_FEEDBACK_LOOP -> D_INTEGRATION | cross_domain_violation | D_FEEDBACK_LOOP | D_INTEGRATION | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_ORCHESTRATOR | 跨域违规: D_FEEDBACK_LOOP -> D_ORCHESTRATOR | cross_domain_violation | D_FEEDBACK_LOOP | D_ORCHESTRATOR | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SECURITY | 跨域违规: D_FEEDBACK_LOOP -> D_SECURITY | cross_domain_violation | D_FEEDBACK_LOOP | D_SECURITY | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SHARED | 跨域违规: D_FEEDBACK_LOOP -> D_SHARED | cross_domain_violation | D_FEEDBACK_LOOP | D_SHARED | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 跨域违规: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP | cross_domain_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_AUDIT | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_KB | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_GOV_RULE | error | open |
| V-LAYER-D_AUTONOMY_CORE-D_INTELLIGENCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_AUTONOMY_CORE | D_INTELLIGENCE | error | open |
| V-LAYER-D_FBL_VERIFICATION-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FBL_VERIFICATION | D_GOV_AUDIT | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOVERNANCE | error | open |
| V-LAYER-D_FEEDBACK_LOOP-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FEEDBACK_LOOP | D_GOV_DRIFT | error | open |
| V-LAYER-D_FRONTEND-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_GOVERNANCE | error | open |
| V-LAYER-D_FRONTEND-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_FRONTEND | D_TRADING | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_CODE_QUALITY-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_CODE_QUALITY | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOVERNANCE | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_AUDIT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_AUDIT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_ENFORCEMENT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_ENFORCEMENT | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_KB | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_KB | error | open |
| V-LAYER-D_GOV_OPS_RESILIENCE-D_GOV_RULE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_GOV_OPS_RESILIENCE | D_GOV_RULE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_SHARED | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_SHARED | error | open |
| V-LAYER-D_OPS-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOVERNANCE | error | open |
| V-LAYER-D_OPS-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_OPS | D_GOV_DRIFT | error | open |
| V-LAYER-D_SECURITY-D_GOVERNANCE | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOVERNANCE | error | open |
| V-LAYER-D_SECURITY-D_GOV_DRIFT | 层级违规: L1_foundation -> L2_domain | layer_violation | D_SECURITY | D_GOV_DRIFT | error | open |
