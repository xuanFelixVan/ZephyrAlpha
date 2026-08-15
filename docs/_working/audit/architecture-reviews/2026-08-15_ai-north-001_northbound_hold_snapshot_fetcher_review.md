---
ttl: task_bound
title: 北向资金季度持仓快照 fetcher 新增模块架构评审记录
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-15
topic: northbound_hold_snapshot_fetcher_review
session: AI-NORTH-001
---

# 北向资金季度持仓快照 fetcher 新增模块架构评审记录

> Step 1.8 架构评审门控（新增模块触发）。变更分级：L2 局部变更（D_DATA 域内同层新增，无跨层接口变更）。
> Owner 书面委托：用户任务书（AI-NORTH-001，task-19-northbound-snapshot）明确"按 19 号 memo 施工计划落地 fetcher"。
> 设计真源：[19_northbound_hold_snapshot.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/19_northbound_hold_snapshot.md) v0.2.1（方案选型/表结构/调度/验证/不做清单均已裁定）。

## 1. 变更概述

| 项 | 内容 |
|---|---|
| 新增模块 | src/zephyr/data/implementations/northbound_hold_fetcher.py（fetcher 独立文件，函数式 API） |
| 新增表 | c1_market.northbound_hold_snapshot（DDL-as-Code：schemas/categories/market_northbound_hold_snapshot.py） |
| 既有文件改动 | tushare_provider.py 增加 1 条 capability 路由（3 行叠加型）；tasks.yaml 增加 1 个任务；4 个注册表补登 |
| 数据源 | 复用 tushare 源（token/限流/熔断既有），不新建数据源 |

## 2. 六项清单

| # | 检查项 | 结论 | 证据 |
|---|---|---|---|
| 1 | KB 决策冲突 | PASS | memo §4.2 已裁定方案 C（tushare hk_hold）；与 DEAD_DATA_SOURCES（check_algo_quality.py 四个死数据源）无冲突——本 fetcher 不碰日频净流入；情绪周期/regime 分工边界不涉及 |
| 2 | 跨层循环依赖 | PASS | fetcher 仅依赖 provider_base（FetchPayload/FetchResult）+ table_registry，与 tushare_provider 同层单向委托（provider→fetcher 模块函数），无回边 |
| 3 | 可观测性 | PASS | 复用 scheduler 既有链路（fetch_perf 落 c0_meta、progress_store、alerter）；fetcher 内 log 每季度行数 |
| 4 | 数据一致性 | PASS | ReplacingMergeTree ORDER BY (ts_code, trade_date) 幂等去重；全量覆盖写入（memo §5.1）；PIT 守卫=季度末+20 自然日才采集（官方第 5 股通交易日发布留足缓冲），不采未发布季度 |
| 5 | 回滚方案 | PASS | tasks.yaml 任务删条目即停用；DROP TABLE c1_market.northbound_hold_snapshot 回滚数据；注册表条目删行即回滚；全叠加型改动无破坏性编辑 |
| 6 | 性能退化 | PASS | 每季度 2 次 API 调用（SH/SZ 拆分，单侧 <2100 行，远离 4200 上限——memo §9 分页风险构造性消除）；全量 8 季度 ≈ 16 次调用 ~3 万行，秒级完成 |

## 3. 文档更新清单（Step 7 闭环）

- 19 号 memo：状态 draft→active、§9 分页风险结论回填、修订记录 +1
- data_asset_registry.yaml：DS-103 + JOB-083 补登
- business_data_categories.yaml：market_northbound_hold_snapshot 品类
- field_dictionary.yaml：FLD-POS-008/009（hold_share/hold_ratio）
- known_data_gaps.yaml：三条 akshare 失效接口补登记（memo §5.4 施工项）
- capability_canonical_file_registry.yaml / module_translation_registry.yaml：双登记
- architecture_issue_registry.yaml：#ARCH-DATA-019 新模块登记

## 4. 评审结论

6 项全 PASS，无否决条件命中。进入 Step 2（depgraph 设计态登记）。
