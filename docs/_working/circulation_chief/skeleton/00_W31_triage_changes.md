---
ttl: task_bound
title: S3 W3-1 三态变迁清单（A/B/C/D 四段，132 环节中 58 环节）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
creation_token: w31-triage-changes-20261001
---

# W3-1 三态变迁清单（复核判 vs skeleton 原判）

## 一、判级变迁（8）

| # | 环节 | 原判 | 复核判 | 关键证据（详各 F/SEG 档） |
|---|------|------|--------|--------------------------|
| 1 | A-02(F02) | 断链（§3#6 工段串接空地） | **存疑** | onboarding_wizard.py 十环编排壳已建成（experimental 零运行痕）；断链级降为"建成未投运" |
| 2 | A-14(F125) | 盲区（未挖） | **存疑** | data_governance 21 py+data_service.py:4 消费 lineage_tracker |
| 3 | A-16(F127) | 盲区（未挖） | **存疑** | data_eng 15 py+cleaning_engines/quality 消费方 |
| 4 | B-12(F24) | 挖干 | **存疑（降级）** | MOD-BT-086 synergy_dedup 全仓零生产调用方（仅 tests）；FAC-E5=built 虚标；E4 侧另立 _translated_dedup_key |
| 5 | B-15(F27) | 存疑(P0 断链 §3#7) | **挖干（翻绿）** | MOD-PA-030 装配体+pf_alloc_daily 事件链+scheduler.py:281 再平衡槽（运行痕 json）+MOD-PA-032 三表写侧+allocation_inputs.py:192/216 TDM 只读对接；黄点=09-29 一次失败留痕 |
| 6 | B-18(F129) | 盲区 | **存疑** | ml_train 43 py+process_supervisor/intelligence 3 处外部引用 |
| 7 | C-02(F31) | 盲区（无消费） | **存疑** | alt_data 29 py 已接 tasks.yaml:2761 消费端首批+scheduler.py:1622；TDM null=登记面欠账非无消费 |
| 8 | C-08(F131) | 盲区 | **存疑** | nlp 7 py+4 外部消费方（news_taxonomy/news_llm_scorer/news_sentiment_analyzer/sentiment_sft_trainer） |

## 二、判级不变·断链判词过期/性质变化（4）

| # | 环节 | 原判 | 复核注记 |
|---|------|------|----------|
| 9 | A-04(F04) | 存疑(P0 §3#1"三引擎零接线") | 判词**半过期**：cross_validation 槽 09-27 已接线翻绿（scheduler.py:239+trading_calendar.py:161）；真断点收窄为三 data_eng 引擎 C1 Owner 门+DSL 写侧 |
| 10 | B-16(F28) | 存疑(P0) | 子项判词过期：影子组合已建成（shadow_portfolio.py 09-27 治本第一段）；IS 分解 FIELD-GAP 在 pf_core 零命中；真断点=M7→ExecutionReportSource 供数口 |
| 11 | B-06(F18) | 存疑("LLM 增补未建") | 措辞勘误：three_high_screen 头注 :12/:278 双处自证"零 LLM 依赖"=设计边界非缺口 |
| 12 | B-08(F20) | 挖干(翻绿) | 翻绿维持+新注记：运行流量薄（lane_g_candidates.csv 1 行、intel inbox 仅 2 件） |

## 三、新发现断链/错位（不在 §3 清单）

| # | 对象 | 发现 | 档 |
|---|------|------|----|
| N1 | E5 协同去重链 | 考试→去重→入库的 E5 位空转：synergy_dedup 零生产调用方+FAC-E5 built 虚标 | B_strategy_factory/F24.md |
| N2 | F123 册锚错位 | migration_registry.yaml 实为 ARCH-031 模块迁移映射册（deprecated/frozen），非"DB schema 迁移通道"；DB schema 受控迁移通道在代码面不存在 | A_data_supply/F123.md |

## 四、计数/路径漂移登记（不裁，供 S2 回写）

- resource_profile entities 101（实跑）vs skeleton 96；data_eng 15 vs 16；alt_data 29 vs 28；normalized 592 txt vs 597 条。
- 路径漂移 6 处（D 段）：selection_funnel/negative_veto→signal_fundamental/；t_trade_coordinator/sell_execution_planner→sell_decision/core/；sell_session_router→ex_sor/core/；firm_risk_aggregator/correlation_regime_monitor→position/core/；lifecycle_state_machine→factor/governance/。
- A 段 TI 派生链锚 ti_minute_recalc.py 未寻获，实锚=tasks.yaml:2287-2315。
