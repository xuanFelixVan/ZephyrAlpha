---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 考试政策 exam_policy——E4 正考准入·执行口径·成本双口径·复权降级·负结果台账
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-19
topic: backtest_system_sop
scope: 07_trading_decision_architecture
related_issues:
  - "裁定#365"
---

# 考试政策（exam_policy）——考试段判据真源

> **一句话**：凡是"升考试"（E4 正考/窄测，factor 或 strategy 对象皆同此册）：**何时允许点火一次考试、按什么口径考、结论怎么分级、负结果去哪里**，判据真源全在本册；禁凭战役令临时条款考试，禁车道间口径漂移。
> **定位与互挂**：[sop_b_node_loop.md](sop_b_node_loop.md) ⑥=考试在七步循环中的**执行位次**（真源不复制）；[factor_mining_sop_policy.md](../mining_sop/factor_mining_sop_policy.md) S5=因子生产线中的**流程位次**（其 §2 regime 条件化=必报项真源，本册只引用）；本册=**判据语义**（准入/口径/降级/台账），编排语义冲突时不归本册管。禁第二套门控：本册不重造 V1-V6/OverfittingDetector/DSR 机制（README §6 既有资产表），只钉调用纪律。
> **诞生**：2026-09-19 裁定#365——strategy_sop_gap_report **G3（E4 正考未 SOP 化）+G5（复权链断供结论分级）+G6（成本双口径声明）+G8（负结果台账）** 四条缺口合并为一本（净零原则下唯一新立候选，对价=四条缺口登记销项）；此前口径散在 f06 脚本+战役令 §2+sop_b ⑥三处（G3 现状证据）。

## 1. 考试准入（何时允许点火一次考试；=G3 销项）

不满足任一条=禁点火，跑了也白跑（结论作废）：

1. **prereg 卡 frozen**：考窗（IS/OOS）/通过阈值/桶边界在跑数前写死并冻结（模板=factor_mining_sop §4）；事后挪门柱=本批作废。
2. **封闭族声明（N_eff）**：本批考试含哪些条目（含失败者）封闭在案；中途加条目=重开预注册。
3. **沙箱三关过关单**：同源预检/族内去重/数据面复核三关各留痕（factor_mining_sop S4）；数据面以考试时点实查为准，禁抄 prereview 声称值。
4. **试验台账行已开**：本批试验次数从第一轮跑数起全量留痕（§5）——Deflated Sharpe 的原料，后补=造假。

## 2. 考试执行口径（=G3 销项）

1. **执行器**：`scripts/backtest/f06_e4_wfa_exam.py`（只可运行不可改）；完整成本五项（佣金+印花税+滑点+市场冲击+做T额外成本），费率读实际账户配置**禁硬编码**。
2. **门控**：WFA/OOS 门控 + 按对象类型映射验证层（factor→V1，sop_b §2 映射表）+ OverfittingDetector 三阶段 + Deflated Sharpe（**喂全部留痕试验次数**，禁只喂幸存配置）。
3. **regime 条件化必报**：每因子/策略 MUST 附分状态桶指标与"什么状态下有效"结论（条款真源=factor_mining_sop §2，本册互挂不复制）；**无状态分解的正考报告按"无条件证据档"降级收录**。
4. **结论可比性**：同批结论必须同口径；跨批引用结论必须连口径一起引（§3-§4 双声明纪律）。

## 3. 成本双口径声明（=G6 销项）

1. **双口径事实**：引擎现行五项成本（`matching_logic.py` 成本段）与 Owner-001 滑点档（`cost_model_calibration.py` 校准段）**并存**，谁也没退役。
2. **声明纪律**：每份考试报告 MUST 写明本次用哪个口径；双口径并行跑时两套结果分开列，禁混排。
3. **引用纪律**：引用任何回测/考试结论必须同时声明成本口径与区间（IS/OOS）——对齐 [README.md](README.md) §7 护栏 5；无口径标注的结论=无效引用。

## 4. 复权链断供结论分级（=G5 销项）

1. **现状事实**：`kline_daily.adj_factor` 实查恒 1（复权链断供）→ **一切日线结论=暂定档**（复权修复前有效）。
2. **标签纪律**：暂定档结论在报告、factor_registry/strategy_registry 回写、组队备料件中 MUST 带"暂定（复权链断供）"标签；禁把暂定档当最终档引用或升级。
3. **复验义务**：复权链修复后，受影响结论须复验方可升档；分钟级结论不受 adj_factor 直接影响，但其日线聚合衍生结论继承暂定档。

## 5. 负结果台账（=G8 销项）

1. **全量入册**：每批考试正/负/零结果同权留痕（另类挖矿 0/5 前科=没有正式台账的血泪）；"没找到"必须写清排除了什么、排除理由。
2. **判死归档配额**：判死单须带"≥3 个已排除候选与排除理由"（sop_b ⑦）；落选/跳过条目进 results 全量 CSV 与报告偏离/落选登记。
3. **试验次数留痕**：台账记录因子×前瞻×桶总组数与全部跑数轮次——**这是 Deflated Sharpe 校正的原料**（§2.2），缺原料=结论降级。
4. **死矿登记**：判死矿脉/因子族登记在案，防同一死矿被反复挖（重复试错成本）；复挖须带新机制假设或新数据面，否则禁复挖。
5. **落点**：战役台账行 + lane 目录全量 results 件（`docs/_working/<campaign>/<lane>/`）；注册表回写走 GitCommitGateway。

## 6. 三态出口（与 sop_b ⑦对齐）

| 出口 | 判据 | 后续动作 |
|------|------|---------|
| 达标 | 预注册阈值全过+DSR 校正后仍显著 | factor 回写 registry ic/ir/decay；strategy 走 sop_c C5-C6；结论按 §3-§4 带口径与暂定标签 |
| 不达标有假设 | 阈值未过但机制假设可修 | 回 S0-S3（factor_mining_sop）带假设登记，禁止原地调参重跑凑数 |
| 判死归档 | 机制证伪/数据面不可修/全状态不稳 | 判死单+§5 负结果台账行+死矿登记 |

## 7. 诞生与净零记录

- 裁定#365（2026-09-19）：本册=G3+G5+G6+G8 合并新立（净零原则下唯一新立候选）；对价=四条缺口在 `docs/_working/archive/2026-09/bizmine_night/factor_sop_screen/strategy_sop_gap_report.md` 登记销项（resolved）；同批 factor_mining_sop 转正（G4/G2/G10 载体）。
- 修订纪律：本册为判据真源，车道临时条款与之旅中冲突时**就严者为准**；修本册走裁定登记（RULE-RULING）。
