---
ttl: task_bound
title: B 段·策略工厂 18 环节六向挖矿档（S3 W3-1）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
creation_token: seg-b-strategy-factory-w31-20261001
---

# SEG_B · 策略供给链＝策略工厂（B-01..B-18，18 环节）代码级核验

> 基线：FAC 图 build_status 实跑=built 5（E1A/E4/E5/E6/E7）+partial 11（E0/E1/E1B/E1C/E1D/E1E/E1G/E2/E3/E8/E9），与 skeleton §1 吻合。**注意：FAC-E5=built 与代码实况冲突（见 B-12）。**

## 六向台账

| 环节 | 上游 | 下游 | 生产者代码(路径:行) | 消费者代码 | 自动化态 | 运行态 | 三态复核 |
|------|------|------|---------------------|------------|----------|--------|----------|
| B-01(F13) E0 算力闸 | 日历/资源 | 全工厂重任务 | scripts/backtest/compute_window_gate.py（MOD-BT-151，pull gate，INVARIANTS"重算力唯一问闸面"+W12 点火面前置 batch_window_preflight） | **4 生产消费点**：factory_intake_pipeline.py、hypothesis_translator.py、factory_grid_executor.py、lane_c2_agentic_miner.py | 事件（任务到点来问，无常驻） | 黄（闸在+问闸面 4 件，FAC=partial：未全量重任务接入） | **维持存疑** |
| B-02(F14) E1 进货编排 | F15-F20 | F21 | scripts/backtest/factory_intake_pipeline.py:52 `_LANE_SPECS`（B/C/G/I 车道）+:108 preflight_compute_gate+:117"未施工车道跳过" | strategy_intake 台账族+出生证 | 事件（六车道并发，E0 前置） | 黄（E1C 三轨 gplearn/c2agentic/MCTS 代码在；**lane_c3_candidates.csv 不存在**=MCTS 轨零产出） | **维持存疑** |
| B-03(F15) 车道A·社区 | 社区源 | F14 | scripts/backtest/intake_load_screen_c2.py（MOD-BT-035，全量灌入 candidate+excluded 都留档） | c1_backtest.strategy_screen + C5 | 定时（爬取批次） | 绿（data/strategy_intake/normalized/ 6 目录 **592 txt** 实跑；skeleton 597=-5 漂移登记） | **维持挖干** |
| B-04(F16) 车道B·AI 生成 | 本地/LLM | F14 | scripts/backtest/lane_b_idea_generator.py（CONSUMERS=FAC-E1B+E2） | factory_intake_pipeline.py:154-156 with_lane_b 分支 | 手动/LLM 批 | 黄（lane_b_candidates.csv **16 行**有产出） | **维持存疑** |
| B-05(F17) 车道C·公式机 | F21 种子 | F14 | lane_c_formula_miner(MOD-BT-155)+lane_c2_agentic_miner(MOD-BT-158)+mcts_expression_search.py；config/factor_mining_whitelist.yaml | factory_intake_pipeline C/C2 分支 | 事件+手动（双轨分期裁定） | 黄（lane_c 17 行+c2 9 行；**c3=0**） | **维持存疑**（C3 零产出详 F17.md） |
| B-06(F18) 车道D·产业链三高 | F12 | F14 | scripts/backtest/three_high_screen.py（MOD-BT-090；头注 :12"零 LLM 依赖"=:278 argparse 描述同） | factory_intake_pipeline I 车道（lane_chain_candidates.csv） | 事件（图谱驱动） | 绿（three_high_candidates.csv **41 行**） | **维持存疑**——但"LLM 增补未建"是**设计边界非缺口**（本件声明零 LLM） |
| B-07(F19) 车道E·模型基线 | 行情库 | F14/F22 | distribution_forecast_eval.py(MOD-BT-084/194)+kronos_adapter.py(MOD-BT-195) | factory_intake_pipeline | 定时 | 黄 | **维持存疑** |
| B-08(F20) 车道G·全网进货 | F96 胃 | F14 | scripts/backtest/lane_g_stomach_intake.py | scheduler.py:537-544（事件沿，st-chief4x-gut-20260927 锚实跑确认） | 事件（翻绿确认） | 黄绿（翻绿维持；**运行流量薄**：lane_g_candidates.csv 仅 1 行，docs/_working/automation/inbox/ 仅 2 件=index+intel-20260916） | **维持挖干(翻绿)**，流量薄注记 |
| B-09(F21) E2 预审门 | F14/F28/F50 | F22 | scripts/backtest/hypothesis_precheck.py（MOD-BT-091）+scripts/ch/apply_hypothesis_precheck_ddl.py | hypothesis_translator(E3 只消费 precheck_passed)+factory_intake_pipeline+intake_ledger_recon+feedback_prior（4 消费方） | 事件 | 黄（DDL 已部署+4 消费方；FAC=partial 待流量核） | **维持存疑** |
| B-10(F22) E3 构造翻译 | F21 | F23 | scripts/backtest/hypothesis_translator.py（消费 compute_window_gate+precheck） | f06_e4_wfa_exam/strategy_screen_c2 | 事件 | 黄（translated_manifest.csv 在册） | **维持存疑** |
| B-11(F23) E4 考试咽喉 | F22 | F24 | scripts/backtest/strategy_screen_c2.py+f06_e4_wfa_exam.py:650（schemas backtest_strategy_screen）+strategy_screen_query.py | forward_post.py:107+strategy_lifecycle_advisor.py:64（_q 查询消费） | 事件 | 绿 | **维持挖干** |
| B-12(F24) E5 协同去重 | F23 | F25 | src/zephyr/pf_alloc/core/synergy_dedup.py:27（MOD-BT-086，纯函数贪心聚类） | **零生产调用方**：全仓 grep 仅 tests/backtest/test_synergy_dedup.py；头注声明消费者"E5 考试→去重→入库/C5 差异化"不存在；E4 考试侧另立 `_translated_dedup_key`（f06_e4_wfa_exam.py:645） | 断（built-not-wired） | 红（FAC-E5=built 与代码冲突） | **挖干→存疑（变迁，新发现断链）**（详 F24.md） |
| B-13(F25) E6 入库监控 | F24 | F26/F14 反馈 | MOD-BT-078（api_server 引用）+data/backtest_artifacts/runs/ | 台账只增+判死行；F14 反馈 | 事件+定时监控 | 绿（runs/ **191 个 run 目录**实跑） | **维持挖干** |
| B-14(F26) E7 模拟盘前哨 | F25 | F27/F72 | src/zephyr/strategy_pipeline/paper_outpost.py（MOD-BT-225，"只输建议禁写注册表"） | pipeline_events.py:206 `"paper_outpost_due"→run_paper_outpost_due` 映射+:399 marker 触指；config/resource_profile_registry.yaml:1893 sch_paper_session | 事件（pipeline_events 唤醒；STARTUP manual=设计内） | 绿（翻绿维持，触发链闭合实证） | **维持挖干(翻绿)** |
| B-15(F27) E8 组装与资金分配 | F26 | F74/F48 | src/zephyr/pf_alloc/allocation_orchestrator.py（**MOD-PA-030 G15→G14 装配体**，头注"挖矿 PFA-1 判'链从未被组装'的治本件"）+allocation_persistence.py（MOD-PA-032 三表写侧） | pipeline_events.py:186 `PF_ALLOC_MODULE` 子进程执行+pf_alloc_daily 事件（:33 唯一自动产出者 maybe_emit_pf_alloc_daily） | 事件（daily_kline SUCCESS 唤醒） | 绿（**三缺全补**：sleeve 落库=三表写侧/再平衡调度=scheduler.py:281 pf_alloc_rebalance_check 槽+data/runtime/pf_alloc_rebalance_check.json 运行痕/TDM 对接=allocation_inputs.py:192,216 只读 portfolio_plan；黄点=data/failures/20260929_pf_alloc_rebalance_check_214510.json 一次失败留痕） | **存疑(P0)→挖干（变迁，翻绿）**（详 F27.md） |
| B-16(F28) E9 实盘归因 | 实盘账本 | F50/F21 | src/zephyr/pf_core/core/performance_attribution_engine.py（MOD-PF-007，Brinson-Fachler :27）+**shadow_portfolio.py**（MOD-PF-030，09-27"FAC-E9 差件治本第一段"，纯只读对照） | risk/core/factor_exposure_manager.py+performance_attribution_degradation.py+ai_layer/perceive/translator.py:41 e9_attribution vein | 定时 | 黄（影子组合已建成但供数口"M7 接线后经 ExecutionReportSource"未接；FIELD-GAP 字样 pf_core **零命中**=原 FIELD-GAP 判词无痕；data/ 面零 shadow 产物） | **维持存疑，两子项判词过期**（详 F28.md） |
| B-17(F29) 进货台账与出生证 | F14-F22 | 全工厂 | data/strategy_intake/{raw,translated,constructed}_manifest.csv | scripts/backtest/intake_ledger_recon.py（对账） | 事件 | 黄（三段 manifest 在册，recon 在） | **维持存疑**（出生证终态=纸面 manifest，无独立出生证实体） |
| B-18(F129) ml_train 训练线 | B/J 交界 | F19 | src/zephyr/ml_train/ **43 py** 实跑吻合 | infrastructure/process_supervisor.py、intelligence/model_evaluation/{inference_base,implementations/default_inference_engine}.py、ml_train/implementations/sentiment_sft_trainer.py（被 nlp 链消费） | 静态库+被动调用 | 黄 | **盲区→存疑（变迁）**（详 F129.md） |

## 本段三态变迁

| 环节 | 原判 | 复核判 | 关键证据 |
|------|------|--------|----------|
| B-12(F24) | 挖干 | **存疑（降级）** | synergy_dedup 零生产调用方；FAC-E5 built 虚标 |
| B-15(F27) | 存疑(P0 断链) | **挖干（翻绿）** | MOD-PA-030 装配体+调度槽+运行痕+TDM 只读对接 |
| B-18(F129) | 盲区 | **存疑** | 43 py+3 外部引用 |
| B-16(F28) | 存疑(P0) | 存疑维持，子项判词过期（影子组合已建/FIELD-GAP 无痕） | shadow_portfolio.py:1-30+grep 零命中 |
