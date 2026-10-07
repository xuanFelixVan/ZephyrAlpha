---
ttl: task_bound
completes_when: P2 五件全部落地或 Owner 另有裁定
card: C268
session: st-mastertc-l2
date: 2026-10-07
---

# C268 P2 五件结构性补强——设计稿（各件落点与验收）

> 真源=《未完成任务施工清单》P2 五件（`docs/_working/final_delivery_campaign/recovered_final_reconciliation_checklist_2026_09_28.md` §P2 条目 24-28）。
> 本夜（2026-10-07 总包夜战）做两件半：①本文设计稿全量；②三层对账日报查勘（§三）；③季度审计注册查勘（§五）。
> 剩余施工件（防假绿三件套两 gate、晋升阈值裁定落册、独立验证器、日报生成器）按 §六 排队移交。

## 一、晋升门阈值预登记（条目 25）

**结论先行**：ruling_registry 已有裁定#488（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` L4242），
但其口径="总包夜战 2026-10-06 全量⏳处置"，**不是**晋升门阈值登记通道——阈值预登记须独立成节、走独立裁定号。

**落点**（三件套，缺一不闭环）：
1. 阈值数据册 `config/promotion_gate_thresholds.yaml`（新建，CREATE-GUARD token 先行）：
   - 四族判据（清单条目 25 原文口径）：`backtest_sim_return_deviation`（回测-模拟收益偏差）、
     `slippage`（滑点）、`fill_rate_cancel_rate`（成交率/撤单率）、`volatility_decay`（波动衰减）；
   - 每族 `threshold`（数值）+`stage_from/stage_to`（backtest→paper→live_micro 三级）+
     `source: paper_outpost_2w_backfill`（paper_outpost 阈值按 2 周实测回填后纳入——首版可
     `status: placeholder` 挂 TODO，不装真数）；
   - 对齐锚：MLflow 晋升阶段（stage transition）+ RTS 6 年度自评条目引用字段。
2. 裁定登记：阈值册+裁定同 commit 原子（RULE-RULING）；**取号器归 L10 裁定台**
   （`--claim --session st-mastertc-l10` + ruling_registry safe_write_text）——本车道不越权取号。
3. 消费侧接线：`src/zephyr/strategy_pipeline/paper_outpost.py` 晋升判定点改读阈值册
   （禁硬编码——现有内联阈值迁入册，保留回退默认=现行值，行为零变更）。

**验收**：阈值册存在且 schema 校验过；裁定号在册且 related_arch 指向册路径；
paper_outpost 判定点单测证明"改册阈值→判定跟随"。

## 二、防假绿三件套（条目 24）

**落点**：
1. ①tests/ 写权限分离：改 `gate_registry.yaml` 或 in_process 名册对 tests/ 触碰的既有门
   （TEST-ISOLATION 族）加"AI 车道改断言→warn+审计，Owner 车道白名单除外"判据；
   真源先行=parallel_session_coordination_policy 增补条款（文档随批）。
2. ②断言 diff 强制复审门：新 gate `ASSERTION_DIFF_REVIEW`（src/zephyr/gov_enforcement/commit_gates/），
   判据=own-diff 中 `assert_*`/期望值字面量变更行数>0 且提交人=AI 车道 → 阻断+处方
   （独立复审 sid 复核后放行）。own-scope 化（`_build_own_scope` 同族，C338 先例）。
3. ③held-out 第二测试集：波 7.3 红蓝集（tests/governance/redblue_*）扩容为 held-out 目录 +
   `scripts/run_held_out.py`（代理成功宣告后由总包通道调用，结果 append 进车道 workbook）。

**验收**：三件各有 gate/脚本落仓+单测；本夜不施工（涉 tests 域写权限分离=纪律移交，见 §六）。

## 三、三层对账日报（条目 27）——本夜查勘件

**查勘结论**（grep `对账日报|daily_recon` scripts/ src/，2026-10-07）：
- **已有**：交易侧日终对账=`src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation`
  （柜台/内部/持仓三账核对），schedule.yaml L250/L259 有 15:40 槽声明；
- **缺口 A（现状断链）**：d5 供应链图生成器在案判定——"15:40 槽在 schedule.yaml 挂着但
  scheduler 无该槽分派分支、tasks.yaml 无同名任务、run_daily_reconciliation 零生产调用方"；
- **缺口 B（P2 本件）**：清单口径的三层=回测↔模拟↔实盘**偏差日报**（LEAN Reconciliation
  章节同构），与交易三账核对是不同对象——HEAD 无任何实现（`grep backtest.*paper.*live` 族零命中）。

**落点（处方）**：
1. 生成器 `scripts/governance/generators/generate_reconciliation_daily.py`：三层指标
   （收益/滑点/成交率/回撤）逐层取数→两两偏差表+阈值越界标记（阈值=§一册同源）；
   产物 `data/reports/reconciliation_daily_<date>.md`（append-only，禁覆盖）；
2. 触发：挂 schedule.yaml 既有日终槽（事件触发语义，禁新增 cron/Timer——宪法 §9.3）；
   顺路修复缺口 A 的 15:40 槽分派断链（scheduler 分派分支+tasks.yaml 同名任务）；
3. 消费：作为 §一晋升门的持续证据源（晋升裁定引用最近 N 日日报 hash）。

**验收**：生成器单测（tmp 隔离假数）；连续两日产物存在且偏差表数值可复算。

## 四、独立验证通道（条目 26）

**落点**：`src/zephyr/governance/validator/` 新子域（与策略开发链路代码隔离——不得 import
ex_sor/signal_* 生产实现）；验证器只读 point-in-time 数据快照重算关键指标；AI 生成因子/策略
双检（概念稳健性+样本外结果分析）两报告 schema 固化进册。

**验收**：隔离性由 import 门（新 gate 或既有 DEPGRAPH 判据）强制；双报告样例+重算数值与
生产链路交叉核对≤容差。

## 五、季度审计机制注册（条目 28）——本夜查勘件

**查勘结论**：两处候选登记面均 `ai_autonomy: human_gated`——
`risk_tier_registry.yaml`（REG-RISK-TIER-001）与 `event_calendar_registry.yaml`
（REG-EVT-001，且其为**市场事件**日历非治理审计日历）。按卡面纪律"registry 改动风险高则
只登记处方"——**本夜只登记处方，不动册**。

**落点（处方）**：治理审计日历条目（quarterly cadence），范围四项（清单条目 28 原文）：
ANY-ABUSE 7 处、noqa_exempt_registry 全量、CloneGuard acknowledged 白名单、flag 全量；
一表季检（SOC2 access review 同构）。登记动作=Owner 窗口二选一：
a) `event_calendar_registry.yaml` 增治理子段；b) 新 `governance_audit_calendar.yaml`（ROOR 登记）。
create_guard.py INVARIANTS 在案的"merge_evaluation warn-only 由季度审计评估升级"（裁定#375）
应并入同一季检表——首季必查项。

**验收**：册内 quarterly 条目存在且四项范围齐；季检表模板落 docs/_working/。

## 六、本夜执行面与移交

| 件 | 本夜状态 | 移交 |
|---|---|---|
| 晋升门阈值预登记 | 设计稿+#488 查勘（非通道） | 阈值册+裁定（L10 取号）+paper_outpost 接线 |
| 防假绿三件套 | 设计稿 | gate 施工×2+held-out 集（tests 域写权限分离=纪律移交总包） |
| 三层对账日报 | 查勘完成（缺口 A/B 双证） | 生成器+调度接线（缺口 A 顺路修） |
| 独立验证通道 | 设计稿 | validator 子域施工 |
| 季度审计注册 | 查勘完成（双面 human_gated） | Owner 窗口择面登记（§五处方） |
