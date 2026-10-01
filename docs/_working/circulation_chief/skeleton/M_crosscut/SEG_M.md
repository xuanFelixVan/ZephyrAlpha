---
ttl: task_bound
title: M 段·全局横切段挖矿档（W3-3）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# M 段·全局横切段（F116-F122，6 环节）

> 方法同 SEG_I。本轮要点：**F121 三域+研究域实件 37 py 且获回测主链消费实证**（骨架"design 挂起"口径部分过时）；F119 真源落位临时区的治理矛盾注记。

## 六向台账

| 环节id | 名称 | 上游 | 下游 | 生产者路径:行 | 消费者 | 自动化态 | 运行态 | 三态复核(骨架→本轮) |
|--------|------|------|------|--------------|--------|----------|--------|--------------------|
| M-01(F116) | SOP 方法论族 | — | 全链方法论 | docs/01_policies_and_standards/sop/ **11 目录**实测（automation_sop/backtest_system_sop/construction_sop/data_audit_sop/data_ops_sop/governance_sop/library_sop/mining_sop/ops_sop/review_sop/trading_decision_map_sop）+README+index+audit_prompts_20_ai.md | 全链 AI（宪法 §6 检索序） | 静态 | 在用 | 挖干→挖干（族数口径 9/11/12 漂移已在骨架 §4-7 登记，本轮实测 11 目录） |
| M-02(F117) | 文档资产体系 | — | 治理面 | docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml；data/asset_index/unified-asset-index.yaml（头 12 行实测：generated_by scripts/governance/generate_asset_index.py，total_assets **33249**，generated_at 2026-09-11） | 治理/发现 | 机生 | 索引 09-11 后未见再生成注记 | 挖干→挖干（机生；再生成时效注记） |
| M-03(F118) | 四盘存储地图 | — | F08/F09 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md:3/:15（INFRA-STORE-003 永久手册，D=生产/F=冷储/G=备份总仓/offsite=Owner 月度离场） | F08 冷库/F09 备份 | 静态 | 在用（宪法 §7 引用） | 挖干→挖干 |
| M-04(F119) | 双引擎自动化总计划 | F83 | 排班 | docs/_working/cmd_ledger/automation_master_plan.md:10（双引擎·调度唯一真源）、:34-40（L0-L6 角色表） | I-08 班底/排班 | 静态 | 在用 | 挖干→挖干+**治理矛盾注记：'L0-L6 唯一真源'落位 _working（临时区，TTL 语义）与永久手册定位冲突**（宪法 §9.4 永久区禁引临时区）——升版应迁 docs/01_policies_and_standards 或 _registry |
| M-05(F120) | 业务层四轴+底板骨架 | — | F72-F75 | docs/_working/automation/20260917_fullauto_skeleton_v1.md:41-43（§4 施工优先级序列·工单队列） | H 段转正链设计 | **无**（design） | 纸面+工单队列 | 存疑(design)→存疑(design)——详见 F120.md |
| M-06(F121) | 研究性三域+研究域 | — | 待裁 | src/zephyr/digital_twin(8py)/cross_asset(7py)/execution_simulation(8py)/research(14py)=**37 py 实测**；外部消费实证：src/zephyr/backtest/core/matching_engine.py:804 lazy import execution_simulation.almgren_chriss_impact_model（P0-2 冲击成本）+implementations/vectorized_engine.py:4 | **G-02 回测引擎族已实际消费 execution_simulation** | **无**（Owner 门 M0 待裁挂起） | 部分实件已在主链运行（lazy import） | 存疑(design Owner 门)→**实件+主链消费实证（Owner 门仍挂）**——详见 F121.md |
| M-07(F122) | 管线路由 M1-M11 | — | Agent 编排 | config/blueprint_routing.yaml（**route_id 30 条**实测，:16 权限 Human-Gated）；src/zephyr/integration/pipeline_orchestrator.py:4（依赖 26 件：ModelRouter/circuit_breaker/dead_letter_queue/rollback.contract/LLM 网关等） | governance/ops_governance/phase_check_registry.py、infrastructure/pipeline 族（grep -l 实测） | 事件 | 编排库在，任务级流量未见 | 存疑(M4/M5 边界)→存疑——详见 F122.md |

## 段内小结

- 环节 6：挖干 4（F116/F117/F118/F119，其中 F119 带落位矛盾注记）+ design 2（F120/F121——F121 有实证升级）+ partial 1（F122，与 F121 计重叠边界）。
- **三态变迁 1 笔**：F121 design→实件+主链消费实证（Owner 门未动，仍待裁）。
- M-04 落位矛盾与 F130 空壳、F87 零消费并列为本轮"登记面诚实性"三注记。
