---
ttl: task_bound
title: S06 回测批考挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S06 回测批考（策略工厂 E4 考试咽喉段）

## 1 现状盘点（自动化状态+file:line 证据）

**结论先行：考卷执行与落库的机械化部分已全自动（周六 14:00 计划任务就绪、幂等落库 fail-closed、下游事件钩子已接）；但 E4 目前"只记录不裁决"——DSR 记录不判生死、overfitting_adjudicator 未接线、及格线实际在 S07 bothwin；且 OOS 复测批无任何自动化，这是全链 S06→S07 的第一断点。**

### 1.1 考试执行体（MOD-BT-076）
- `scripts/backtest/c4_batch_screen.py`：`discover()` L88-89 全收 translated/c4_*.py（现 **84 件**）；契约校验（STRATEGY_ID/WINDOW_KIND/build）L75-85；**单件失败不阻断** L120-122（failures 列表进 summary）；IS 冻结窗 2020-01-01..2023-12-31（ETF 族 2021-04 起，`_c4_engine.window_for` L318-320）；OOS 模式=`--start/--end` 给出才启用（L199-202，verdict=oos_tested，自动带 IS 参照算 oos_years_decay L277-299）。
- 判定书现状：verdict=done"**无通过线（C5 差异化再甄别）**" L256-262——E4 本身不设及格线。
- DSR 批内折减：L131-137 委托官方件（SSOT `zephyr.backtest.regime_validation.c4_deflated_sharpe_runner`，经 `_c4_engine.batch_deflated_sharpe` L286-316）；**不可用/出错返回 None 并留 warning，不阻断落库**（注释自认"2026-09-13 OOS 批全 None 教训"）。
- S3 知识生效日哨兵：L206-214（声明制，drift 只打印+档案留证，不阻断）。
- 落库 fail-closed：run 档案 create/write/finalize L240-263；strategy_screen 四键幂等（batch,strategy_id,verdict,source_file）L269-291；**write_tsv 未确认即 RuntimeError** L322-324。
- 下游钩子：`_emit_pipeline_hook` L165-174 落账成功→`emit_c4_batch_completed`（任何异常不反噬批测进程）。
- 算力省法：`--auto-only` L154-162/187-198 只考未入冻结批台账的新件，零新件即退。

### 1.2 触发与首跑状态（实测）
- 计划任务 `ZephyrAlpha_C4Exam`：**Ready，周六 14:00**（register_c4_exam_task.ps1:30），8h 时限、IgnoreNew、StartWhenAvailable。
- **首跑从未发生**：Get-ScheduledTaskInfo 实测 LastRunTime=1999/11/30、LastTaskResult=267011（0x41303 未运行）、NextRunTime=**2026-09-19（周六）14:00**；`.runtime/logs/c4_exam.log` 不存在。
- 历史批次均为手动：data/backtest_artifacts/runs/ 有 **22 个 SCR-C4-*** 档案（20260913-20260914），如 SCR-C4-20260914-051102 verdict.md"批测完成 4 行"。
- `run_c4_exam.ps1:28` 只执行 `python scripts\backtest\c4_batch_screen.py`——**纯 IS 窗，无 OOS 批，未用 --auto-only（全量 84 件重跑）**。

### 1.3 过拟合护栏栈的接线现状
- `src/zephyr/backtest/core/overfitting_adjudicator.py`（MOD-BT-001）：三检验器（walk-forward 衰减 L343-409 / DSR L232-306 / 参数扰动 L465-557）+ `OverfitGateHook` Protocol L584-594；头注自述"上线评审流程（挂钩点预留，**未接真门禁**）"L5；`gate_hook=None` 默认不触达任何门禁 L601。**grep 证实 c4_batch_screen/_c4_engine 零引用——既不拦也不记。**
- `c4_deflated_sharpe_runner.py`（MOD-BT-001 家族）：头注 L31"不执行真实数据跑批（真实跑批待排期）"已**部分过时**——其数学本体经 `_c4_engine.batch_deflated_sharpe` 被周考实跑（单窗批内折减口径）；"待排期"指的是 memo §10.5 的多变体赛马场景。
- `distribution_forecast_eval.py`（MOD-BT-194）：PIT 校准+锐度+pinball 双标准考尺，纯函数零 IO；消费方=车道 E/Kronos 评估，**未挂周考**（现考卷件无分布预测产物）。
- CPCV/purged CV：tests/backtest/test_cpcv.py 在库（蓝图 E4"L262 护栏栈 WFO/purged CV+embargo/CPCV（测试在库）"），**未挂考试管线**。

### 1.4 事件路径（c4_batch_due 重事件）
- 轻/重分级：`pipeline_events.py:60-61`（LIGHT=c4_batch_completed 等，HEAVY={c4_batch_due}）；重 kind 只经显式 `drain --all`（L154-155 → `run_c4_batch_due` L224-235 = 子进程跑 `c4_batch_screen.py --auto-only`，默认 3600s 超时）。
- 发现器：`scan_translated_backlog` L333-355——调度器唤醒点扫"translated 有而 IS 批台账无"的件→`record("c4_batch_due")`+告警，只发现不执行。
- **实证（2026-09-15）**：`.runtime/strategy_pipeline/pending_events.jsonl` 存 1 条 `c4_batch_due`（33 个未考件，attempts=0，recorded_at 04:13:21）；`last_receipt.json` pending_left=1——**重事件滞留中，无人 drain**。schedule 侧 `drain(allow_heavy=False)`（L326）永远跳过它。

## 2 六向挖矿日志表

| 轮 | 方向 | 矿脉 | 判定 | 关键产出 |
|----|------|------|------|---------|
| 1 | ①上游 | 待考供料（构造件积压） | signal | 84 件在库、33 件未考（journal 事件 payload 全清单）；周六 10:00 FactoryLaneC 上午刚构造的件下午 14:00 即入考（ps1 注释 L12-13 设计意图） |
| 2 | ②下游 | 考完→入库事件链 | signal | `_emit_pipeline_hook`→`emit_c4_batch_completed`（同进程 drain 轻 kind）→`run_intake_auto`（pipeline_events.py:140-145）——同进程直消费已接线；失败留 journal 跨唤醒重放 |
| 3 | ③机制 | CPCV/PBO/WFA 业界惯例（全网） | signal | PBO 原论文 davidhbailey.com/dhbpapers/backtest-prob.pdf（Bailey, Borwein, López de Prado, Zhu，2015，CSCV 定义 PBO）；CPCV 实证对照 sciencedirect.com/science/article/abs/pii/S0950705124011110（Arian, Norouzi, Seco，Knowledge-Based Systems 2024：CPCV 的 PBO 低于 walk-forward/K-fold）；RiskLab 三法对比 risklab.ai/research/backtesting/backtesting_cross_validation；DSR ResearchGate 286121118（Bailey & López de Prado 2014）。结论：业界惯例=考试出口必须带多重检验签核（PBO/DSR），单窗 IS 成绩直通入库被视为伪迹源 |
| 4 | ④后端 | DSR/adjudicator/runnner 接线真相 | signal | DSR=已实跑但 None 非阻断且无阈值消费（deflated_sharpe 列只记录）；overfitting_adjudicator=零引用未接线；runner 头注"待排期"过时；知识漂移哨兵=声明制 |
| 5 | ④后端 | 计划任务/首跑核验 | signal | C4Exam Ready 但 LastRunTime=1999（未跑过）；run_c4_exam.ps1 无 OOS 批、无 --auto-only；22 个 SCR-C4 档案全手动 |
| 6 | ⑤前端 | 考批呈现 | noise | 无考试漏斗/成绩面板；run 档案 04_wide+verdict.md 即报告形态，登记不施工 |
| 7 | ⑥数据字段 | bothwin 前置字段 | signal | S07 及格集要求每策略有 `oos_tested` 行（screen_source.py:124-134 `if not segments: continue`）；全仓**无任何自动 OOS 批**（grep ps1/config/pipeline_events 零命中 --start 自动化）；IS 批标签 `C4-translated-20260912` 硬编码于 c4_batch_screen.py:49 与 screen_source.py:38 两处（耦合风险） |

**计数：signal 6 / noise 1 / 受阻 0**（全网搜索 1 次命中，无 429）。

## 3 业界与开源对照（含必答方向）

- **CPCV/purged k-fold（López de Prado）**：《Advances in Financial ML》(Wiley 2018) 提出 purged K-fold+embargo 与 CPCV；本项目测试在库（tests/backtest/test_cpcv.py）未挂管线。实证文献（Arian et al. 2024，KBS）表明 CPCV 在控制 PBO 上优于 walk-forward 与普通 K-fold——蓝图 E4 把它列为护栏栈是正确方向，欠的是接线。
- **walk-forward 惯例**：业界（QuantConnect pipeline quantconnect.com；Aeromir strategy pipeline futures.aeromir.com）把 WFA 作为从回测到实盘的标准折；本项目 overfitting_adjudicator 检验器①即 WFA 衰减比（阈值 0.70 SSoT），缺的是逐折数据供给。
- **PBO**：Bailey et al. 2015 的 CSCV/PBO 是"考试有没有选拔偏差"的标准问——本项目多考卷同批竞争（84 件选优），恰是 PBO 适用场景；现仅 DSR 批内折减部分覆盖（DSR 折减试验数膨胀，PBO 折减选择规则过拟合）。
- **DSR**：Bailey & López de Prado 2014——已接（记录级），业界用法是**签核阈值**（≥0.95 才算显著）而非仅记录。
- **结论**：本仓 E4 机械化（批量执行/幂等落库/档案）达到业界流水线水准；判定权（裁决层）落后于自家蓝图与业界惯例——蓝图 L246-254 写明"IS 冻结→DSR 折减→OOS 双窗及格线"，现实只完成第一二步的记录、第三步缺自动化。

## 4 堵点与欠账清单（含必答关键问题作答）

**必答问题 1：门序列里有没有会被"当前不可用件"卡死的门？**
- DSR **不是** fail-closed 门：`batch_deflated_sharpe` 出错/序列不可用→None，行照落、verdict 照写——不卡门（但也意味着 DSR 无裁决力）。
- overfitting_adjudicator 未接真门禁=**既不拦也不记**（gate_hook=None 且零调用方）——不卡门，但"考试"实际无裁决。
- 知识漂移哨兵=声明制不阻断。S3 不卡门。
- 真正 fail-closed 的门在 E4 内部只有两个：`批测零结果 RuntimeError`（L219，全件加载失败才触发）与 `落库未确认 RuntimeError`（L322-324，CH 写通道故障）——卡死场景=CH 不可用，此时 ps1 记 exit 1、下周 StartWhenAvailable+IgnoreNew 幂等重试，**等人一周但可自愈**。

**必答问题 2：overfitting_adjudicator 未接真门禁=不拦还是拦？**
- 答：**不拦**。三检验器与 OverfitGateHook 无任何生产调用方（grep 证实）；E4 判定书自认"无通过线"。及格裁决实际后移到 S07 bothwin（IS>0 ∧ 各 OOS 段>0 ∧ decay<0.5）+BH-FDR q≤0.10——裁决存在但不在考试咽喉，违背蓝图"运动员不兼任裁判，考试权只在 E4 咽喉"的层位设计（裁决权事实上在 C6 intake）。

**必答问题 3：c4_batch_due 重事件无人 drain 会不会导致考完不入库？**
- 答：**不会**。周六 C4Exam 直接跑全量 `c4_batch_screen.py`（非事件路径），落库不依赖 c4_batch_due 事件；该事件只是另一个触发器，滞留无害但永占 journal（scan 幂等按文件集判重，考完后文件集变化会再入队新事件，旧事件成 stale，只能 CLI `drain --all` 消化——未来某次 drain 时它触发一次 `--auto-only` 空跑，幂等无害）。
- 真风险在**下游**：c4_batch_completed→`run_intake_auto` 若因 KillSwitch 非 normal 或 EVIDENCE 缺失抛错，事件 attempts+1，**3 次即毒丸留档停摆**（pipeline_events.py:196-199）——这是需要人介入的单点。

**链路视角结论（周六 14:00 首跑后策略能否无人值守走到 S07 入库？）**：
- **能走完的**：E4 IS 批考（84 件）→ run 档案 → strategy_screen IS 台账（幂等）→ emit c4_batch_completed → 同进程 intake 尝试。首跑日本身无人值守成立（除非 CH 挂）。
- **断点①（主断，结构性）**：`run_intake_auto` 及格集来自 `fetch_bothwin`（screen_source.py:118-144），要求每策略有 `oos_tested` 行；**周考只产 IS 行、全仓无自动 OOS 批** → 新考策略在及格集为空 → **无人库**。链断在"第二窗复测无自动化"。当前 2 条 sim（c4_e3da6fa71af1_panic_rebound、lane_e_quantile_baseline）都是人工 OOS/人工认证时代的产物。
- **断点②（条件单点）**：intake 写路径双钥匙 fail-closed——KillSwitch 探针（intake.py:264-265，探针失败也停）+EVIDENCE 文件（intake.py:328-329，现存✅）——任一不满足连续 3 次→事件毒丸→停摆等人。
- **断点③（自愈型，不算断）**：挂图失败只告警不回滚（intake.py:418-421，only-add 下批重放自愈）。
- 附带：ps1 全量重跑 84 件在 8h 时限内属算力浪费（--auto-only 已备而未用）。
- **一句话**：周六首跑后，成绩能入库、事件能发、intake 能被唤醒；但**新策略走不进 S07**——除非补上 OOS 复测自动化（S06-G1）。

## 5 施工项建议（具体到文件/函数/验收标准）

| 项 | 内容 | 验收标准 |
|----|------|---------|
| S06-G1 | **OOS 复测自动化（本环节最高优先）**：run_c4_exam.ps1 在 IS 批后追加 `python scripts\backtest\c4_batch_screen.py --start 2024-01-01 --end <上周末> --auto-only`（--auto-only 与 OOS 组合需小改：`_auto_only_names` 现只认 IS 批台账，改为"IS 批有 translated_c4 行且无对应 oos_tested 行"） | 首跑后 48h 内，新 translated_c4 件各有一条 oos_tested 行且 oos_years_decay 非空；再下一周六 intake 能消费到非空及格集 |
| S06-G2 | ps1 IS 批换 `--auto-only`：只考增量件，省全量重跑 | 连续两个周六，第二次批测 results 数=新构造件数（非 84） |
| S06-G3 | E4 出口裁决列：c4_batch_screen 落库时按阈值（bothwin 预判+DSR≥0.95）写 `eligible_for_intake` 布尔/理由到 notes 或新列，判定书从"无通过线"改为门禁结论 | 判定书含逐件门禁结论；S07 可选直读该列复核 |
| S06-G4 | c4_batch_due 消费接线：run_c4_exam.ps1 开头加 `python -m zephyr.strategy_pipeline.pipeline_events drain --all`（考试窗本身就是合法重活执行点），或直接删除事件改纯任务驱动 | journal 中 c4_batch_due 滞留 <7 天；无 stale 事件积累 |
| S06-G5 | 毒丸告警升级：pipeline_events 毒丸时 alert level=ERROR 已有（L198），补 Alerter→推送渠道接线依赖 S12；先在 c4_exam.log 尾部打印 journal 状态 | 首跑日志可见 pending/毒丸状态行 |
| S06-G6 | （挂起排期）CPCV/PBO 签核入 E4：CPCV 在库未挂；解锁条件=G1/G3 落地后按蓝图开放决策点 7 评估 E4a/E4b 拆分 | —— |
| S06-G7 | （挂起排期）WFO/参数扰动检验器接线：依赖考卷件参数化（现模板零自由度，扰动无对象）；与 S05-G3 horizon 参数化联动 | —— |

## 6 封矿结论

- **矿脉封矿**：7 轮 6 signal 后，剩余矿脉（E4a 免回测快筛、multi-model 交叉考试）全部有归属（蓝图开放决策点 7/挂起项），封批登记。
- **方案封矿**：无。E4 考试咽喉是全图唯一判定权所在，终局核心有位。
- **终局视角**：机械化已完成大半，欠的是"裁决自动化"（OOS 批+出口门禁）——恰是消灭"Owner 看成绩单人工圈合格者"这段人工的关键；S06-G1 不做，S07 及之后所有环节对新增策略等于不存在。
