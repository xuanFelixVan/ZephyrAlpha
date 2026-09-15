---
ttl: task_bound
title: S09 模拟盘运行挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---

# S09 模拟盘运行（账本日跑/健康日刊/盘中会话自动排班）

> 骨架定位：S08 开完钱包后，**模拟盘四件套（账本日跑+平台日刊+盘中会话+月度评估入口）自动跑**。
> 当前状态=❌ 断：全部 manual CLI，调度零接线。本环节=C2 施工主地基（与 S10 共用排班方案）。
> **【施工班 2026-09-15 回填】C2 已落地：`sim_ledger_daily`→`sim_journal_daily` 挂 daily_kline 唤醒（SIM_DAILY_WAKE_TASKS 子串匹配），date-marker 日幂等；盘中会话仍 Disabled（Owner 门）不变。**

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 账本日跑（sim_daily）——manual CLI

- `scripts/backtest/sim_paper_ledger.py:151`：`--mode {replay_demo, sim_daily}` 必选；
  `[STARTUP] manual`（L6）、CONSUMERS 注明"每日自动化（接线另批）"（L5）。
- 已有运维加固：sim_daily 档对 CH 维护窗撞车（19:30 档 VHDX/备份优雅停机 10-25 分钟，
  2026-09-14 实证丢当日快照）做了有界重试=10 次×120s（`sim_paper_ledger.py:161-180`）——
  说明**该任务曾被人肉排过 19:30 档**，但当前无任何调度体在跑（见 1.4）。
- 输出落库：`c1_backtest.sim_pocket_daily`（日账）+ `c1_backtest.sim_trade_log`（事件流水），
  write_tsv fail-closed（L205-212）。

### 1.2 平台日刊+健康三检——manual CLI，告警已接

- `scripts/backtest/sim_platform_journal.py`（MOD-BT-090）：
  - 三健康检=行情新鲜度/账本心跳/越界持仓（L60-74；预警线 110 万=L34）；
  - 异常经 `AlertManager.raise_alert(severity=WARNING)`（`alert_if_degraded` L86-97）；
  - 日刊落 `c1_backtest.sim_platform_journal`（L120，fail-closed）；
  - `[STARTUP] manual`（L6）、"每日自动化（接线另批）"（L5）。
- 注意：账本心跳检（L66-69）在"0 钱包=平台未跑"时告警——若 S08 不修，本检会天天报异常。

### 1.3 盘中 QMT 模拟会话——CLI 已落，计划任务注册为 Disabled 且实机缺席

- `scripts/start_paper_session.py`（57 号文 GAP-2）：
  - 只连 QMT 模拟账户（`config/.env.qmt` QMT_SIM_*，实盘键永不触碰，L104-109/L180-203）；
  - 默认纯保活不下单（`_KeepAliveStrategy` 返回空权重，L117-132）；15:05 有界收场（L498-514）；
  - `--service`=LiveStrategyAdapter 常驻监督模式（异常隔离+退避重启熔断+biz 心跳
    `tmp/live_strategy_biz.heartbeat`，L338-365）；
  - **真信号源未施工**：`--strategy topn-momentum` 只是 mock 信号彩排口径（L307-309，
    "construction_backlog B4 待施工"原文登记）——盘中会话与策略注册表/钱包体系零耦合。
- `scripts/register_paper_session_task.ps1`：注册任务 `ZephyrAlpha_PaperSession`
  （每日 09:25+StartWhenAvailable PT5M+ExecutionTimeLimit=0），但**注册后立即 Disable**（L100-103，
  "enable=Owner 窗口"裁定）；wrapper=`scripts/start_paper_session_daily.ps1`
  （is_trading_day 守卫+xtMiniQmt 进程探活，缺 QMT exit 0 SKIP）。
- **实机核验（2026-09-15）**：`schtasks //query` 全量 30 个 ZephyrAlpha_* 任务中无
  ZephyrAlpha_PaperSession——注册脚本在本机未执行过或任务已删。模拟盘盘中会话当前完全不在跑。

### 1.4 调度面全景——sim 四件套零排班（实机+配置双证）

- `src/zephyr/data/config/schedule.yaml`：21 个调度槽（L23-183，pre_market 到 auction_highfreq），
  全部为数据层任务，**无任何 sim/paper 任务**。
- 计划任务清单（schtasks 实测 30 个 ZephyrAlpha_*）：DataScheduler/CHHealthProbe/DeadmanSwitch/
  C4Exam/FactoryLaneC/NightlySentiment 等——**无 paper/sim 相关任务**。
- grep `sim_paper_ledger|sim_platform_journal|sim_deviation_report|sim_governance` 于
  scripts/*.ps1 与 config/*.yaml 零命中（唯一登记=scripts/script-manifest.yaml:833-858 清单条目）。

### 1.5 相邻事实（影响 C2 方案选型）

- DataScheduler 是活的（ZephyrAlpha_DataScheduler 正在运行），且已挂策略管线唤醒钩子
  （`src/zephyr/data/scheduler.py:628-633` → wire_data_scheduler）——**"数据落地即唤醒"的
  事件通道现成**，这是 C2 的合规挂点（宪法 §9.3 事件触发优先，禁自走时钟）。
- 计划任务先例也活着：ZephyrAlpha_C4Exam（周六批考）、run_post_settlement_daily.ps1
  （--if-trading-day 守卫）——ps1 计划任务是次选挂点。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ④后端：账本日跑契约 | sim_paper_ledger L151-180（mode 参数+CH 撞窗重试加固）；落库 fail-closed | **signal** |
| R2 | ④后端：平台日刊三检 | sim_platform_journal L60-74 三检+L86-97 AlertManager；L34 预警线；manual 标记 | **signal** |
| R3 | ②下游：调度面反查 | schedule.yaml 21 槽零 sim；schtasks 30 任务零 paper/sim；ps1 grep 零命中 | **signal**（断点实锤） |
| R4 | ①上游：盘中会话链 | start_paper_session.py 全文（mock 信号/保活边界/--service）；register_paper_session_task.ps1 L100-103 Disabled 裁定；实机任务缺席核验 | **signal** |
| R5 | ⑥数据字段：唤醒通道盘点 | scheduler.py:628-633 钩子已挂；C4Exam/post_settlement 计划任务先例；pipeline_events 月度档 marker 机制 | **signal** |
| R6 | ③机制（外部）：paper 平台调度惯例 | QuantifiedStrategies paper 3-6 月+月度漂移复核（https://www.quantifiedstrategies.com/algorithmic-trading-strategies/ ，访问 2026-09）；Concretum 生产系统教训清单（https://concretumgroup.com/building-reliable-trading-systems-algorithmic-trading-automation/ ，访问 2026-09，陈旧数据/执行失败须自动处置） | **signal** |

轮次判定：6 signal / 0 noise。C2 方案成形即封批。

## 3 业界与开源对照

- **paper 阶段频次惯例**：业界 paper trading=每交易日收盘后自动对账+晨检告警（QuantConnect
  paper 环境与 live 同引擎同调度；URL 见 S08 文档 R5）。本项目四件套分离（账本/日刊/盘中/
  评估）粒度更细，排班后强度对齐惯例。
- **健康检自动化惯例**：Concretum 生产十课（URL 见 R6）：陈旧数据与 broker 断连必须自动探测
  +自动降级，不能靠人肉发现——本项目 sim_platform_journal 三检即此形态，只欠"自动跑"。
- **盘中会话定位差异**：业界 paper 盘中会话=策略真信号驱动；本项目盘中会话当前是 mock 彩排
  骨架（57 号文 GAP-2 明示 B4 未施工）。**C2 排班对象应先定账本/日刊两件**（真钱包链路），
  盘中会话转正属 S14 实盘桥范畴，不应混入 C2 验收。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | 账本日跑无调度体 | schedule.yaml/schtasks/ps1 三处零命中；19:30 重试加固反证曾有手工档 | 钱包日账断更，S10 月度判定无输入 |
| 2 | 平台日刊无调度体 | 同上；[STARTUP] manual | 三检形同虚设，异常无人知（AlertManager 已接但无触发源） |
| 3 | 盘中会话任务缺席+Disabled 裁定 | register_paper_session_task.ps1 L100-103；实机无此任务 | QMT 模拟户盘中完全不运行（当前亦无真信号可跑，欠账登记而非硬伤） |
| 4 | 盘中会话与钱包/注册表零耦合 | mock 信号彩排口径（start_paper_session.py L307-309） | S11 整装毕业后的实盘模拟仍无载体（S14 范畴） |
| 5 | 心跳检与 S08 联动缺位 | journal L66-69 "0 钱包=异常" | S08 修复前，日刊自动跑会天天告警（施工顺序：C1 先于 C2） |

## 5 施工项建议（C2 四件套排班方案雏形——S09 部分）

**挂点裁定：DataScheduler 事件唤醒优先，计划任务兜底。**

1. **账本日跑接线（事件式，首选）**：`pipeline_events` 新增 kind `sim_ledger_daily`，
   在 `wire_data_scheduler._on_task_completed` 判定"daily_kline 任务当日 SUCCESS 完成"时
   入队（数据落地=自然唤醒，合规于宪法 §9.3）；handler 子进程隔离调
   `sim_paper_ledger.py --mode sim_daily --strategy <注册表全部 sim 条目>`（多策略循环，
   依赖 C1 参数化）。幂等=sim_daily 同日替换写天然幂等。
   - 兜底方案：仿 `register_paper_session_task.ps1` 模式写 `register_sim_paper_tasks.ps1`
     注册 17:10 计划任务（daily_kline 16:30 之后+is_trading_day 守卫）——仅当调度器钩子
     方案验收不过时启用。
   - 验收标准：模拟交易日收盘后 30 分钟内 sim_pocket_daily 出现当日全部 sim 钱包行；
     非交易日零动作；CH 断连时重试后成功或告警。
2. **平台日刊接线**：同通道 `sim_journal_daily` kind，账本 handler 成功返回后串行触发
   `sim_platform_journal.py`（顺序依赖：日刊体检要看到当日钱包行）；告警路径已存在
   （AlertManager），验收=人为制造心跳缺失→告警落地。
3. **盘中会话（登记欠账，不在 C2 验收）**：B4 真信号源施工后，Owner 窗口执行
   `Enable-ScheduledTask ZephyrAlpha_PaperSession` 转正；当前维持 Disabled 裁定不动。
4. **排班真源登记**：新增的 kind/时点写进本环节文档+capability card，禁只散落代码。

## 6 封矿结论

- 矿脉层面：调度面/CLI 契约/盘中会话/外部惯例四向闭环，6 signal 零 noise，封批转 C2。
- 方案层面：四件套自动跑直接消灭"每个交易日人肉跑四个 CLI"的人工位，终局必经件，**施工**
  裁定；盘中会话真信号化为 S14 依赖欠账，挂起排期（解锁条件=B4 真信号源施工）。

## 7 施工班状态回填（2026-09-15）

- C2 落地（pipeline_events.py）：`sim_ledger_daily`→`sim_journal_daily` 日件链挂 daily_kline/kline_daily/kline_index 唤醒（SIM_DAILY_WAKE_TASKS，task_id 子串匹配），FIFO 串行保证日刊看到当日钱包行；幂等双闸=当日 UTC date-marker（消费成功才落）∨ 非 poison 同 kind 在队；DAG 并行竞态由 journal 失败重试兜底（行情未齐→账本 RuntimeError→留队，下个数据任务完成唤醒重试）。
- 月度档：`sim_deviation_monthly` 见 S10；`sim_memo_monthly` 从未轮转的病根修复（毒丸不算已入队，C2/X2）。
- §4 堵点状态：1/2/5 已解（调度体=事件唤醒）；3/4 维持（盘中会话 Disabled=Owner 门、真信号源 B4 未施工）。
