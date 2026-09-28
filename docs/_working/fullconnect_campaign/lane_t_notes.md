---
ttl: task_bound
title: 全流通战役 T 线施工日志（交易面三件接线）
session: zc-lane-t-20260927
creation_token: lane-t-notes-fc-20260927
---

# T 线施工日志（zc-lane-t-20260927，2026-09-27）

> 硬约束遵守记录：只接 paper/模拟面（逐件影响面判定见下）；零实盘资金路径触达 → 99_skipped_for_owner.md 本轮无追加行。scripts/ 零新增文件（仅改 scripts/ch/apply_market_tables_ddl.py 既有件）。锁=lock_files.py acquire/release 全程；提交走 git_commit.py。

## T1 F39 L2 板块门接线 —— 判完结（他线已落地，本袋验证）

- 处方=L03-C02 两步（水位桥方案甲+batch2 五行）。核 HEAD 实态：**两步均已落地**——
  `_DOMINANT_TO_TEMP` :190（红队修正版 r1~r12 七态桥）、`_collect_l2` :231（water_temp_response 查表+load_l2_admission 三原料注入+gate_level 三态）、编排器注记 daily_decision_orchestrator :602-605。
- 落地批次=d27e0f0df3（l02c03+l09c02 状态轴合并批）；水位桥 WIP 容器疑虑（secbuild 分支 f44c1bfd742）解除：主区已含同款+测试，无双落。
- 测试读数：tests/strategy_pipeline/test_daily_gate_snapshot_l2.py **13 passed**。
- 本袋零代码改动（净零：已有接线不重立）。

## T2 F40 L3 个股：L04-C01 池持久化 + L04-C02 通电 —— 本袋施工

- **孤儿件回收**：L04-C01 三件（DDL/producer/测试，creation token 20260925 前袋预制）为未跟踪在野件，而 HEAD 侧带 `_collect_candidate_pool`（30505c93f6）已 import producer——HEAD 自洽性缺口，本袋 claim 后落地并收尾：
  - `schemas/categories/market/market_stock_candidate_pool.py`：c1_market.stock_candidate_pool DDL 真源（ReplacingMergeTree，DateTime64(3,'Asia/Shanghai') RULE-SCHEMA-TZ 合规，19 列）。
  - `src/zephyr/signal_ashare/core/candidate_pool_snapshot.py`：日批 producer（三来源注册制，空池 fail-visible）+ 本袋新增 `load_pool_snapshot`（exact=回放当日/pit=决策日 shift(1)，JSON 四列反序列化，C01 验收"回放任一历史日可取当日池快照"）。
  - **建表实证**：apply_market_tables_ddl.py 注册（_ALL_DDL 88 表+_EXPECTED_ENGINES）后实跑 apply，CH 26.6.1 进程外核实 engine=ReplacingMergeTree 19 列（首跳 HTTP 语法误报经降级链自愈，mini repro 同式通过）。
- **L04-C02 通电**：
  - 盘后腿：daily_gate_snapshot 侧带已在 HEAD（他线），本袋验证 collect_gate_snapshot pool 附加键契约不变。
  - 盘前腿：tradability_preflight.py 新增 `run_premarket_pool_preflight`（读池 PIT→逐票五查→JSON 裁决，快照/池行双注入位，fail-open）→ premarket_workflow.py default_stages 新增 `tradability_preflight` 工序（段3 09:10-09:12，mandatory=False，capability_id 直指执行体）。**调用方 0→≥1 达成**。
  - 三来源 sleeve 生产者全链串接=前袋明示"另案"（collect_bundles 无源=空池如实缺省），本袋不代立。
- 测试读数：test_candidate_pool_snapshot **15 passed**（含读回回环 4 新测）；test_tradability_preflight **19 passed**（runner 4 新测）；test_premarket_workflow **18 passed**（工序接线 1 新测）；tests/signal_ashare 全套 **2850 passed**。

## T3 F41 L4 执行反馈环：G41-1 最后一米 + G41-2 九态映射桥 —— 本袋施工

- **G41-1（L4-14 断链）**：
  - selector 侧（ex_sor/core/algo_execution_selector.py）：新增 `QualityPriorProvider` 协议+构造注入位+`FEEDBACK_GAIN=0.20`；`_score_algo` 总分调制 total×(1+gain×(2q−1))（q=0.5 恒等，越界夹边留痕）；breakdown 增 quality_prior/raw_total 两审计字段；reason 附反馈段。
  - scorer 侧（ex_sor/services/execution_quality_scorer.py）：新增 `ScorerBackedQualityPrior`——评分历史经 order_id→算法归因回调 join 出每算法 overall_score 均值；样本不足→None 中性（禁拍假先验）。**选择器消费评分器 0→≥1 达成，反馈环最后一米贯通**。
- **G41-2（九态判据-码面差异）**：order_enums.py 新增 `BrokerOrderState` 九态封闭词表（NEW/ACCEPTED/SUSPENDED/PENDING_CANCEL 为补态）+`BROKER_STATE_TO_ORDER_STATUS` 映射真源+`map_broker_state_to_order_status`（未知态 fail-closed；SUSPENDED/PENDING_CANCEL→SUBMITTED 存活态策略显式）。F53 交界件就位；b) 节点注对齐=S4 D 裁定场景未动。实盘券商适配器（miniqmt/qmt_file_bridge 私有映射）**零触碰**（实盘资金路径避让）。
- 测试读数：tests/ex_sor 全套 **616 passed**（selector 46 含反馈 3 新测/scorer 53 含适配器 5 新测）；九态桥 tests/shared/test_order_enums_nine_state_bridge.py **5 passed**（双态全格+fail-closed）。

## 相关域回归与既有债（非本袋）

- tests/plan_engine + tests/strategy_pipeline：**963 passed / 2 failed**——失败 2 件（TestCalendarDormancy::test_d4_data_proven_degraded_open / test_ambiguous_no_row）经干净 HEAD worktree 对照**复现=既有债**；另有他袋未跟踪件 test_daily_gate_snapshot_l5.py 引用未落地符号致 collection error（在飞 WIP，本袋不代修）。tests/signal_fundamental **160 passed**。

## 遗留与移交

- L04-C02 三来源候选生产者接线（dual_pool/strategy_chain/veto）——按 SKEL"另案"待立工单。
- G41-2b 节点注对齐九态词表——S4 D 裁定场景。
- G41-1 编排层组合点（engine 构造 selector 时接 ScorerBackedQualityPrior）——随 F53/L07-C03 收编裁定落地。
