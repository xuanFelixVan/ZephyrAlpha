---
ttl: task_bound
title: 原问题挖矿战役宪章（PQ-0284+ 持续入题）· st-pqmine-20260927
created: 2026-09-27
sid: st-pqmine-20260927
status: 挖矿中
---

# 原问题挖矿战役宪章

**使命**：继续挖掘原问题——挖矿本项目所有数据源、因子、策略与全链路环节，举一反三生成新考题（PQ-0284+），全网搜索（含外网）量化专业实践补充出题面，经去重与质量闸后注册进 meta_question 库，使 283 题验收账本持续生长。

**避让声明**：本役与 fms-chief-20260927 的 FMS 战役（docs/_working/fms_overhaul/，文件管理平面）不同平面零冲突；作业区 = docs/_working/question_mining_campaign/（他队勿入）。

## 一、出题来源（五路并发）

| 路 | 矿区 | 产出目录 |
|----|------|----------|
| S1 数据源 | CH 各库表覆盖率/PIT/质量/新鲜度 | 01_sources/ |
| S2 因子 | factor_registry.yaml 175 因子（有效性/衰减/容量/换手/相关簇/冗余/子集） | 02_factors/ |
| S3 策略 | strategy_registry.yaml + 组合层（成本敏感性/regime 适应/仓位约束/风控闸） | 03_strategies/ |
| S4 链路环节 | fullflow 骨架 122 环节（F 编号）逐环节验收问题 | 04_chain_links/ |
| S5 全网外部 | 量化社区/专业机构数据质量与因子检验范式（WebSearch） | 05_web_external/ |

## 二、出题格式（对标既有 283 题五要素）

每题必含：layer(层级)/status(状态枚举)/frequency(频率枚举)/origin(出处)/outcome(期望结论) + 题面 + 可机解 threshold + min_confidence。样例读 docs/_working/meta_question_answers/results/results_all.yaml。

## 三、去重与禁翻案（硬闸）

1. 新题题面必须对照既有 283 题（results_all.yaml）与退役 30 题（gaps/RETIREMENT_REGISTER.md）做语义去重——同义题禁出（30 问退役禁翻案是宪法级铁律）。
2. 出处必须 file:line 或 URL 可回查。
3. 判据必须可机解（能写 SQL/代码断言），"不可机解"须显式声明判为 insufficient 类。

## 四、流程

挖矿（五路并发）→ 汇总去重（90_consolidated/new_questions.yaml）→ 质量闸（五要素齐+阈值可机解+出处可查）→ 注册进 meta_question（registry.py 正门 intake，只写 meta_question schema）→ 注册日志 91_intake_log/ → （可选）exam_loop 复考。

## 五、挖干判据

六向台账（真源/写者/消费者/漂移史/冲突面/净零方案）+ 自审闸三态（挖干/未干/受阻）。封矿后才能进注册批。
