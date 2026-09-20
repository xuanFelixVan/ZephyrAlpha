---
ttl: task_bound
title: E5 G07×state_label 关联核查作业簿——台账标准 §七待查项关账
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E5 G07×state_label 关联核查作业簿（只读核查，已关账）

## 六向台账

- **目标**：交接令任务 4——G07 情绪周期模块（五阶段候选，挂起中）与 judgment_intraday_market_state.state_label 的映射关系；G07 能否作为 L1 判定的证据维度（台账标准 §七登记的待查项）。
- **证据**（核查代理 2026-09-18 实挖，file:line 全带）：
  - G07 真身=src/zephyr/signal_ashare/sentiment/sentiment_cycle.py（MOD-SIG-140，MATURITY=new）；五阶段枚举 FREEZING冰点/STARTING反核/FERMENTING主升/CONSENSUS疯狂/EBING退潮（:52-63）；输出 5 维灰度概率+dominant_phase+confidence（:379-390）；输入十项日级盘后指标（:362-376）；**零生产接线**（唯一真实消费=similar_day_inference.py:67）；挂起三重因=TDM-E-L2-05 红节点 pending_gate（TDM:946,950,965）+2026-09-12 裁定 COMBINATION_INVALID（docs/_working/2026-09-11-g07-sentiment-validation.md:32,89）+MATURITY=new。
  - state_label 系 payload JSON 内字段（无独立 DDL 列），五态值域低迷/防御/震荡/进攻/亢奋锁死于 src/zephyr/plan_engine/judgment_ledger.py:134-135 且 fail-closed 校验（:223-226）；写入方=intraday_l1_tracker.py（MOD-PLAN-028，60min bar 事件触发）；evidence 为自由 dict 且发射器不校验其内部（:223-240），组装点 TRACKER:397-415。
  - 历史裁定范围澄清：COMBINATION_INVALID 判的是 A 股三策略组合分层去相关失败（ρ 0.667→0.768，5713 只全市场代理收益口径，验证报告 :32,63,85）——**非币圈侧、非打标能力禁令**；报告 §4.2 反而主动建议定位器增"回放/打标模式"输出（:78）。
  - 定位器真实缺陷（接线前必修）：回放锁死（链式先验自我强化，4 年仅 EBING/FREEZING 两态）；兜底分支把 evidence 最高相（2024-09-30 CONSENSUS 0.644）强改收缩态 FREEZING（:77-78）；FREEZING 样本 n=1 未过验证（:80）。
- **块**：B1 定位/B2 值域与写入方/B3 可行性/B4 结论落档——全部完成。
- **依赖**：无（纯只读，零代码变更）。
- **三态**：挖干（封矿）。
- **下一步**：接线属新施工（改 tracker+修定位器），本环节不开工；登记为方向备案（下节）。

## 核查结论（落档正文）

**一行结论：有条件赞成接线——G07 以 payload.evidence.sentiment_phase 附注形态作 L1 判定证据维度（零 DDL 变更、零值域冲突），但禁止进入 state_label 主判链路，且接线前置条件是先修定位器"打标模式"语义。**

1. **表契约天然兼容**：evidence 自由 dict、发射器不校验内部（judgment_ledger.py:223-240）；tracker 已有组装点与"特征缺席=键缺席+degraded 标注"惯例（:397-415,:240-242）；台账标准 §七本就预登记"G07 情绪阶段可作 L1 证据维度之一"（2026-09-16-judgment-ledger-standard.md:91-93）——Owner 方向已预留。
2. **裁定不禁此用途**：COMBINATION_INVALID 限策略组合层三处置（TDM-E-L2-05 不转蓝/G13 情绪暴露硬上限/CONSENSUS 期多策略扩张冻结），不含判定台账链。
3. **两轴互斥不可直映射**：G07 阶段名不在 _INTRADAY_STATES 值域，直接当 state_label 会被 fail-closed 拒收（judgment_ledger.py:225-226）；且生命周期环≠盘中温度轴（G07 有对 regime 12 态软映射先例 SENTIMENT_TO_REGIME_MAP :669-675，无对 L1 五态映射）。
4. **缓行理由（数据说话）**：输入共线（G07 核心输入涨跌停/炸板/连板与 L1 现有 breadth/attack_sector 同源，增量信息存疑）；定位器兜底是仓位收缩语义非判定语义，不修即注入会污染证据链；MATURITY=new+FREEZING 零验证。

## 方向备案（供未来立项，本战役不施工）

排期建议：①修定位器打标模式（回放先验隔离+兜底语义分离）→②30 天双跑对照（evidence 附注与主判隔离评估）→③再议升级主判特征。届时走新预注册，不在本环节范围。

## 长尾登记

- scenario_classifier.py 在 plan_engine 下不存在（实为 scenario_planner.py/scenario_probability_model.py）——交接令笔误勘误；三重共振条件引擎若复用白名单 AST 求值器，真源在 daily_plan.py 侧（orchp3 合并后核实）。
