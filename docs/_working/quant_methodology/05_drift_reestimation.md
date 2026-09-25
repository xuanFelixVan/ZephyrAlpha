---
ttl: task_bound
title: 分册05 漂移监控与重估循环——定期重估节奏/漂移降权/衔接对账文化
topic: drift_monitoring_reestimation
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 分册05：漂移监控与重估循环

> **大白话开场**：市场会变（regime 漂移）、数据会变（分布漂移）、策略表现会变（alpha 衰减）。**条件概率表不是刻在石头上的**——今天 65% 的胜率，一年后可能只剩 50%。本册立法"多久重算一次、漂了怎么降权、跟现有监控怎么接线"。

## 1. 漂移的三张脸（先分清对象再谈节奏）

| 漂移对象 | 大白话 | 本仓现行监测件 |
|----------|--------|---------------|
| 数据分布漂移（P(x)） | 输入变了：成交量分布、波动率分位、资金流形态变了 | `src/zephyr/feedback_loop/detectors/drift/distribution_drift_monitor.py`；concept_drift.py；ensemble_drift.py；THD-DRIFT 族 PSI 语义（挂图登记，见 D49 注记）；`data/drift_baselines/`、`data/drift_audit/` 基线与审计 |
| 概念漂移（P(y|x)） | 关系变了：同样的形态，胜率变了（散户结构变化/监管变化） | `src/zephyr/factor/analysis/decay_monitor.py`（因子衰减）；`src/zephyr/backtest/services/decay_monitor.py`；factor 生命周期状态机 `src/zephyr/factor/governance/lifecycle_state_machine.py`（retired 终态，MOD-L02-013） |
| 实盘-回测偏离 | 执行变了：滑点比假设大、成交率比假设差 | `src/zephyr/backtest/core/decision_gate.py` `monitor_backtest_live_deviation`（偏离 >30% 告警 / >50% 退役评估）；THD-DEVIATION-003 日收益相关下限 0.5（pending_adjudication 占位待校准，memo55 §3.4） |

**区分的意义**：数据漂移→重估特征/阈值；概念漂移→重估条件概率表；执行偏离→修执行假设（成本口径），三者处置不同，禁混报。

## 2. 定期重估节奏（分频立法）

| 频率 | 动作 | 触发机制 | 现行挂点 |
|------|------|---------|---------|
| 日频 | 实盘 vs 回测偏离度量；数据面新鲜度哨兵 | 事件触发（收盘后管道） | decision_gate 偏离度量（memo55 §3.4 落码）；breadth_freshness_alerts.py |
| 周频 | PSI/分布漂移扫描 vs 基线 | 事件触发 | distribution_drift_monitor + drift_baselines |
| 月频 | MonthlyRiskGovernance + 退役判据扫描 + 条件概率表**滚动重估**（重算各格 raw/n/Wilson LB，出"格间变化榜"） | 月度复盘编排 | memo55 §3.6（月复盘=轻量治理汇总，不新开分析） |
| 季度 | 合并审计窗（同真源可派生必并/零触发退役）+ 漂移基线换基裁定 | 季度审计 | 宪法 §4.2 内收判据；drift_audit 季度对表 |
| 半年/年 | 条件概率表**全量重估+重考**：重估=新预注册（考窗/判据重封），历史格按 PIT 复核 | 裁定通道 | exam_policy §1（重估也是考试，禁免检） |

**事件触发铁律**：一切重估与对账**必须事件触发**（禁 cron/Timer/sleep-loop——永久系统四要素，宪法 §9.3）。上表"频率"是**编排窗口**（事件到达后的处理节奏），不是定时器。

**重估纪律**：重估=一次新考试，走 exam_policy §1 全套准入（预注册重封、N_eff 声明、台账重开）；**禁原地调参重跑凑数**（exam_policy §6 不达标有假设出口：回 S0-S3 带假设登记）。死矿/死格登记防复挖（exam_policy §5.4）。

## 3. 漂移降权规则（漂了先降权，再谈退役）

**梯度**：正常 → 降权 → 停新开仓 → 退役评审。对应本仓已有个零件：
1. **连续收缩节流（RSC-2）**：`framework_composer.py` INARIANTS——引擎边界节流（ShrinkageBacktestEngine 在归一化后乘当日 Shrinkage，剩余质量一律落现金禁再归一化回填——裁定#270）；Shrinkage 供给链 `src/zephyr/backtest/regime_validation/shrinkage_provider.py`（Const/Schedule/Mock/RegimeDetector 四种 provider）。**漂移降权的挂点=把漂移信号映射为当日 Shrinkage 序列**（Schedule provider 已支持按日期查表+PIT as-of join）。
2. **强制中性**：downside 样本 <15 强制中性（regime_meta_allocator.py DOWNSIDE_MIN_OBSERVATIONS）——样本劣化即降权的先例。
3. **阈值注册表统编**：`docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml`（REG-ATH-001，33 条 active）——所有降权触发线必须入阈值注册表，禁散落硬编码（memo55 阈值统编裁定）。
4. **退役是评审不是扳机**：五判据触发 → 评估报告 → 裁定（strategy_retirement_evaluator + retirement_workflow；评审制铁律见 memo55 §3.5——误触发成本=一份报告 ≪ 漏触发成本=僵尸策略）。

## 4. 衔接对账文化（本仓的方法论底座）

- **对账台账是一等公民**：TDM P 流 P1 首枝=对账台账→分级频率→逻辑存活→风险否决→组合体检→结论动作清单（WealthBee 五步同构；commit 842a428c54 D39-D49 落图）。条件概率表重估的对账位=月复盘的固定枝。
- **对账文化三原则**（从既有实践提炼）：①一切结论带口径与区间（成本口径/IS-OOS 声明，exam_policy §3）；②一切修改留痕可回放（台账只增不改；判死单带 ≥3 排除候选）；③一切对账发现闭环到动作清单（P1 末枝"结论动作清单"）。
- **负结果也是对账产出**：negatives.csv / 负结果台账（exam_policy §5）——重估发现"格子胜率塌了"同样入册，防"选择性记忆"。

## 5. 一段话版

**日频盯执行偏离、周频盯分布漂移、月频滚动重估条件概率表、季度换基、年度重考；重估必走事件触发与预注册；漂了先降权（Shrinkage/强制中性/阈值注册表统编），降权不够停新开仓，退役走评审；一切发现进对账台账与负结果台账，只增不改。**
