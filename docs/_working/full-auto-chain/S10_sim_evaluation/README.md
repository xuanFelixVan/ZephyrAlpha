---
ttl: task_bound
title: S10 模拟盘成绩评估挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---

# S10 模拟盘成绩评估（月度偏离/连续 pass-breach 判定/流转建议自动跑）

> 骨架定位：S09 四件套跑起来后，**月度自动评估 sim 成绩并产出流转建议**，喂给 S11 整装回测
> 与 S12 转正建议。当前状态=❌ 断（两件 manual CLI+一件半自动+词表分裂）。本环节=C2 的
> S10 部分+FSM 词表统一欠账。
> **【施工班 2026-09-15 回填】C2 的 S10 部分已落地：`sim_deviation_monthly` 月度档（30 天 marker）+成功后串行触发治理建议器；sim_governance 收尾三件齐（Alerter ERROR 推送+run 档案+串行时序）。FSM 词表统一（paper 态）仍挂起；判定史仍 0 期，首期月判由月度档自动产出。**

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 月度偏离报告（判定器）——manual CLI，功能完备

- `scripts/backtest/sim_deviation_report.py`（MOD-BT-092）：
  - **自动发现注册表 sim/paper 条目**（L101-122：读 strategy_registry.yaml 过滤
    lifecycle_status ∈ (sim,paper)，动态加载 code_path 翻译件，要求 `STRATEGY_ID`+`build`
    契约，缺契约者 warn 跳过）；
  - 四项对照指标纯函数（L51-76：信号一致率/漏单率/收益偏差含时机拆分）+阈值提案值
    AGREE_MIN=0.90/MISS_MAX=0.10/GAP_MAX=0.30（L39）；
  - 连续两月 breach→`decay_proposal` 提案（L201-208，查上月 strategy_screen 判定史
    `prev_month_breach` L125-133），lifecycle 终裁=Owner（L8 不变量）；
  - 产物走 SCREEN run 档案（create_run/write_step/finalize_run L214-231）+
    `c1_backtest.strategy_screen` 台账回执（`_land` L249-279，verdict=sim_deviation，
    screen_batch=SIM-DEV-YYYY-MM）；
  - 回测腿冷启动处理已想到：自模拟盘首日起跑防月初仓位错位（L160-165）。
  - `[STARTUP] manual`（L6）。**纯 CLI，无事件接线**——pipeline_events 无对应 kind。

### 1.2 治理建议器——manual CLI，且存在文档-代码漂移

- `scripts/backtest/sim_governance.py`（MOD-BT-094/140）：
  - 规则：连续 2 月 monthly_pass→建议 `promote_paper`；连续 2 月 breach/出连续提案→
    `demote_decayed`（`recommend` L68-77）；只产建议不改册（L8 不变量）。
  - **输出只有 print/JSON**（L93-98）：无 AlertManager、**无 run 档案**——而 docstring L23
    写"输出=建议报告 JSON（只读），落 run 档案"——**文档代码漂移实锤**（main 全文无
    create_run 调用）。
- `scripts/backtest/strategy_lifecycle_advisor.py`（MOD-BT-187）：decay_watch 台账扫描件
  （decay≥0.5→decay_watch 冻结晋级资格；双窗皆负→reject），只读建议，manual（L5-6）。

### 1.3 半自动已存在的一件：sim_promotion_memo（月度建议书）

- `scripts/backtest/sim_promotion_memo.py`（MOD-BT-193）："Owner sim→production 签字前最后一眼"
  的机器备料，产出 `docs/_working/pipeline-research/sim-memos/sim-memo-<YYYYMM>.md`；
- **事件接线已通**：`pipeline_events.py` LIGHT_KINDS 含 `sim_memo_monthly`（L60），
  `maybe_emit_monthly()`（L283-299）挂月度 marker（30 天线，L56 MONTHLY_DAYS）评估到期入队，
  经 DataScheduler task_completed 唤醒 drain 消费（L315-330）→ `run_sim_memo`（L251-256）。
- **实机状态**：`.runtime/strategy_pipeline/last_audit.json` 只有 `mount_audit` 键
  （2026-09-15），**无 sim_memo 键**——该月度档从未触发过（管线活但此档未到 30 天或从未跑过）。
- 语义注意：sim_promotion_memo 只对"全 sim 台账"出月报，**不消费 sim_deviation 的月度判定史**
  （它走 screen_source/strategy_screen 的 IS/OOS 视角）——与 sim_governance 的判定史消费
  是两条平行线，未合流。

### 1.4 词表分裂（本环节最深的结构欠账）

- FSM 五态：candidate/sim/production/shelved/retired（`lifecycle_fsm.py:48-52`）——**无 paper 态，
  无 decayed 态**；sim 的出边只有 sim→production（Owner 门）与 sim→shelved（L100）。
- 注册表枚举八态：candidate/backtest/sim/paper/live/monitoring/decayed/retired
  （strategy_registry.yaml:58）。
- 后果：sim_governance 建议的 `promote_paper` **无 FSM 边承接**（建议无合法落点）；`demote_decayed`
  在 FSM 里最近似的是 sim→shelved 但词不同。注册表里的 lifecycle 值实际由各写入方自由产生，
  FSM 与注册表从强校验变成口头约定。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ④后端：判定器解剖 | sim_deviation_report L101-122/L39/L125-133/L201-208/L249-279；run 档案契约 | **signal** |
| R2 | ④后端：治理器+漂移 | sim_governance recommend L68-77；L93-98 仅 print；docstring L23 vs main 无 run 档案 | **signal**（漂移实锤） |
| R3 | ②下游：建议→FSM→注册表承接 | lifecycle_fsm L48-52/L95-101 无 paper/decayed 态；注册表枚举 L58 八态分裂 | **signal** |
| R4 | ①上游：事件总线半自动盘点 | pipeline_events L60/L150-151/L251-256/L283-299 sim_memo_monthly 全链；last_audit.json 实机无 sim_memo 键 | **signal** |
| R5 | ⑥数据字段：判定史台账 | strategy_screen verdict=sim_deviation/screen_batch=SIM-DEV-* 为 governance 消费真源；当前存量=0 期（从未跑过月判） | **signal** |
| R6 | ③机制（外部）：晋升 gate 惯例 | 业界 sequential gates（backtest→paper→small live→scale）+3-6 月 paper 期（quantifiedstrategies.com，访问 2026-09；quantpedia.com how-to-paper-trade，访问 2026-09） | **signal** |

轮次判定：6 signal / 0 noise。封批转施工。

## 3 业界与开源对照

- **晋升门惯例**：QuantConnect 晋升管线与 Quantpedia paper 验证（URL 见 R6）均要求
  "固定观察窗+量化门+人工最终批"三段——本项目"连续 2 月月度判定→建议→Owner 终裁"结构
  与之一致；差距只在月度判定自身没自动跑。
- **shadow/paper 双跑口径**：LuxAlgo/Lime（访问 2026-09，见 S09 文档引）强调 paper 阶段
  度量 implementation shortfall——本项目偏离报告的成交价偏差/时机拆分（L63-76 timing_component）
  已是该口径，领先同类开源模板。
- **机构 sleeve attribution 对照**：framework_composer.verify_weight_panel_identity 注释自证
  "机构 sleeve attribution 同款"（见 S11 文档）——S10 的月度判定将来可复用整装归因做
  "策略对组合的边际贡献"评估，登记为远期矿脉（本班不挖）。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | 月度偏离报告无自动触发 | pipeline_events 无 kind；[STARTUP] manual | 连续两月判定永远凑不齐，promote/demote 建议无从产生 |
| 2 | sim_governance 输出不上传不告警不落档 | main L93-98 仅 print | 建议无人看见；docstring L23 漂移 |
| 3 | 判定史存量为零 | strategy_screen 无 SIM-DEV-* 批次（从未跑） | 治理链路冷启动需先攒 2 个月数据 |
| 4 | FSM 无 paper/decayed 态，词表二分裂 | lifecycle_fsm.py:48-52 vs strategy_registry.yaml:58 | promote_paper 建议无 FSM 边；注册表值无强校验 |
| 5 | sim_memo_monthly 从未触发 | last_audit.json 仅 mount_audit 键 | 半自动件也停在纸面 |
| 6 | 偏离报告对"缺 build 契约"条目静默跳过 | sim_deviation_report.py L110-121 | 非翻译件口径的 sim 条目永久游离于治理外（当前 2 条 sim 均有契约，暂无实害） |

## 5 施工项建议（C2 的 S10 部分+词表统一）

1. **月度偏离报告接线**：pipeline_events 新增 kind `sim_deviation_monthly`，挂
   `maybe_emit_monthly()` 的月度 marker 机制（现成：L283-299 加一个
   `("sim_deviation", "sim_deviation_monthly")` 元组即可，30 天线复用）；handler 子进程调
   `sim_deviation_report.py --month <上一自然月>`（重 kind 语义：串行、超时 3600s、失败告警，
   仿 run_c4_batch_due L224-235）。触发时点=每月 1 日后首个 task_completed 唤醒。
   - 验收标准：月度 marker 到期→journal 入队→drain 后 strategy_screen 出现 SIM-DEV-YYYY-MM
     批次行+run 档案落档；重放幂等。
2. **sim_governance 收尾三件**：①输出接 AlertManager（有 promote/demote 建议时 WARNING 级）；
   ②补 run 档案（create_run/write_step，消灭 docstring 漂移）；③在偏离报告 handler 之后
   串行触发（判定史先落、建议后出）。验收=有建议时告警落地+run 档案可检索。
3. **FSM 词表统一（小改大治）**：lifecycle_fsm.py 增加 `PAPER = "paper"` 态与
   sim→paper（guard=连续 2 月偏离通过，机器可验证）、paper→production（OwnerTokenGuard 保留）、
   sim→decayed/shelved 映射裁定；或反向收敛——注册表枚举删 paper/decayed。
   **两方案取其一，裁定留痕**（推荐前者：Owner 口述流程里"整装回测完毕才转正"，paper 作为
   sim 与 production 之间的整装观察态有真实语义位）。验收=FSM 单测覆盖新边+注册表写入方
   全部经 FSM 或 registry_writer 校验。
4. **冷启动首跑**：C2 落地后手动首跑 `--month 2026-09` 建立 1 期判定史，连续两月门槛自
   2026-10 起可满足。
5. **顺带修复**：sim_memo_monthly 与 sim_deviation_monthly 的产物在 S12 合流为统一建议包
   （本班只登记边界，归 S12 施工）。

## 6 封矿结论

- 矿脉层面：判定器/治理器/FSM 承接/事件总线/台账字段五向闭环，6 signal 零 noise，封批转施工。
- 方案层面：月度判定自动化消灭"每月人肉跑评估+人肉汇总"人工位，**施工**；FSM 词表统一是
  结构欠账必还（否则 S12/S13 的拍板链挂在无校验词表上），**施工**；sleeve 边际贡献评估
  为远期矿脉**挂起排期**（解锁条件=整装回测日常化后）。

## 7 施工班状态回填（2026-09-15）

- 月度偏离报告接线✅：`sim_deviation_monthly` 归轻 kind（无人值守自动消费的显式裁定，pipeline_events.py:15/72-76），30 天 marker 月度档，成功后串行触发治理建议器。
- sim_governance 收尾三件✅：①Alerter 推送（level=ERROR——Alerter 仅 ERROR+ 落本地 failure 文件，webhook 未配置=降级本地告警文件不抛，sim_governance.py:88-102）；②run 档案补齐（create_run/write_step/finalize，docstring 漂移消灭）；③串行时序=判定史先落、建议后出。
- FSM 词表统一未做（施工 3 挂起维持）：注册表八态 vs FSM 五态分裂仍在，S13 转正页按注册表现值显示。
- 冷启动首跑：不再需要人工首跑——月度档到期自动产出首期判定史，连续两月门槛自首期+1 月起算。
