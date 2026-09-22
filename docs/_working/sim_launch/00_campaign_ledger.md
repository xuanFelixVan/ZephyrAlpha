---
ttl: task_bound
completes_when: 提交落地+Owner 阅毕交付报告后随战役归档
---

# 模拟盘三步启动战役台账（st-sim-launch-20260922）

> 令源：通宵执行令 2026-09-22｜落盘：docs/_working/sim_launch/｜终态=模拟盘恢复每日运转+排班链接电+日报出格+币圈快线结论
> 红线：交易面四禁（仅 env=sim）；丁域只读；乙域不碰；策略集=E4 观察档

## §1 考古结论（真源读序完成）

### 平台资产四件验活
| 件 | 模块 | 状态 |
|---|---|---|
| 事件流水 sim_trade_log | MOD-BT-085/086/087 | 23 行，含 09-21；仅 VREV 两笔真实成交（replay_demo）+三策略每日 open 空事件 |
| 平台日刊 sim_platform_journal | MOD-BT-088~091 | 10 行至 09-21；09-15 起 data_freshness_ok=0 |
| 月度偏离 sim_deviation_report | MOD-BT-092 | 在册 sim_deviation 判定 43 行（历史月已跑过） |
| 归因/治理 sim_attribution/sim_governance/sim_promotion_memo | WO-1/WO-2 | 件在，crisis_gate_log 0 行（无 crisis 日触发，正常） |

### 停摆根因五病灶（"停摆于 09-17"的实底）
- **R1 空壳运转**：自动化链其实已通（DataScheduler task_completed → wire_data_scheduler → alloc→sim_ledger_daily→sim_journal_daily FIFO→drain），但三策略钱包全是"C1 自动开户"空壳（'open' 零成交，note=策略引擎未接线）——**接电缺口=注册表 sim 条目的翻译件重放从未实现**。
- **R2 QMT 模拟账户腿断**：ZephyrAlpha_PaperSession 计划任务 09-17/18 SKIP（XtMiniQmt 未运行=Owner 晨间 ritual 未做）；09-21 QMT 在跑但 python --service exit 1（真因被 ps1 吞：$ErrorActionPreference=Stop + `*>>` 在 PS5.1 下 stderr 触发 terminating error，日志无输出佐证）。
- **R3 日刊探针时点矛盾**：sim_platform_journal 健检1 要求 kline_index max ≥ 体检日 T，但事件链在 T 早间跑（00:42 UTC=08:42 北京），当日数据必未落 → freshness 恒 false、degraded 恒 1。行情实际新鲜（000300 到 09-21）。
- **R4 分配链时序错位**：alloc_budget_daily 有 09-15..09-21 每日快照（VREV 698K/E-TIMING 390K@09-21），但早间手工/事件开户跑在分配落地前 → 钱包额度回退 flat 1M（note 已留痕）。链内 FIFO 序设计正确，错位来自链外手工跑。
- **R5 孤儿钱包**：STR-AUTO-001/STR-MULTIFACTOR-001 不在注册表（lifecycle=sim 仅 E-TIMING/VREV 两条）、不在分配 universe（09-16 起分配仅 2 策略），却被每日续开户（run_id 每日 sim-open-*，来源=intake sim 流转钩子事件面）——注册表 SSOT 之外的幽灵账户，污染钱包数与总权益。

### 丁线接电面（只读消费）
- 日计划产物=c1_market.judgment_daily_plan（MOD-PLAN-030，subject=index:000300.SH，payload=scenarios 三场景树：S1_attack/S2_defense/S3_oscillation，action=姿态标签**无订单映射**）。
- 盘中归类=c1_market.judgment_intraday_market_state（丁线 scenario_classifier 产出）。
- 结论：接电=防御姿态（stand_aside_defense）可机械执行为空仓；其余姿态无订单语义，如实记 unexecutable 待 Owner 映射，不伪造信号。

### E4 观察档面
- strategy_screen verdict='oos_tested' 51 个 candidate；scripts/backtest/translated/ 有按 candidate 哈希命名的 c4_*.py 翻译件（build(start,end) 标准接口）。
- E4 观察档接电=c4_* 翻译件重放出模拟单（mode=sim_observe 观察档平面，与注册表 sim_daily 平面分离）。

## §2 施工清单
- FIX-1 日刊探针交易日历感知（sim_platform_journal.py）
- FIX-2 ensure_wallet 注册表 SSOT 卫兵（sim_paper_ledger.py；止血 R5）
- FIX-3 ps1 stderr 吞噬修复（start_paper_session_daily.ps1，纯 ASCII）
- NEW-A scripts/backtest/sim_daily_runner.py（MOD-BT-210）：plan 桥+E4 观察档 replay+日报判定/结算
- NEW-B schemas/categories/sim_daily_report.py（MOD-BT-211）+ scripts/ch/apply_sim_daily_report_ddl.py
- NEW-C 币圈 7×24 快线三步评估报告
- 红蓝：模拟下单链路注入测试+断供注入验证哨兵真响

## §3 自裁登记（原自裁留痕）
- A1 plan 桥不建钱包不下单（动作无订单语义，不伪造）：只落判定台账行+姿态留痕——依据"禁伪造信号"平台铁律。
- A2 E4 观察档观察平面 mode=sim_observe 与注册表平面分离，SSOT 卫兵只管 sim_daily 平面——避免门禁误杀观察档。
- A3 观察档首批 N=5 candidate（按 translated 件存在+候选哈希匹配取样），跑通即扩全量留待批——首夜控运行风险。
- A4 日刊 09-21 行修正=幂等重写一行（argMax FINAL 读取取新），零 DELETE。

## §4 进度
- [x] 冷启动+worktree+claim 三文件
- [x] 考古（本文件 §1）
- [x] depgraph 设计节点 MOD-BT-210/211 + 大白话翻译
- [x] 分包1 三修（FIX-1/2/3，含 QMT dry-run 实证+ps1 ASCII/语法双校验）
- [x] 分包2 接电（表建+runner 三平面+17 测全绿+首跑 09-21 落台账 7 行+结算清零）
- [x] 分包3 日报样张+币圈三步评估（不通，差距呈报）
- [x] 红蓝一轮（红①历史注入回补/红②非交易日缺陷当日修+疤行诚实结算/红③断供探针真响）
- [x] 两轮 76 passed（剔除 HEAD 既有红 test_rebuild_matches_pocket，stash 对照实证非本班引入）
- [x] 交付报告 delivery_report.md + 呈 Owner 七项
- [x] 提交：网关 22 次尝试过八道门（表名SSoT/noqa密度/克隆hash/复杂度/参数表/撞号/格式化/翻译册），最终 ENQUEUED q-20260922-st-sim-launch-20260922-0001（13 文件快照袋，零丢失）；串行器活体消化中，落地归属以 git log -1 --name-only 复核为准

## §5b 提交链学费（本次新增配方，已写入会话记忆）
- TABLE-NAME-REGISTRY 新 .py added 行零表名字面量：schema TABLE_NAME 常量+TableRegistry+复用他件查询函数；模块级 SQL 常量中占位符段绝不能进 f-string（eager NameError）。
- NOQA 密度≤10：bare-sql noqa 不能滥，正道=SQL 模块级常量化。
- FUNCTION-DUP hash 克隆：TSV 转义正典=ch_writer.tsv_escape。
- 复杂度≤15/参数≤7：纯函数抽取+dataclass 参数对象。
- MODULE-ID 选号必须全文件扫（含 tests/ 与 docs/03_modules），212/217 双撞实证。
- CREATE-GUARD/TTL/翻译册/depgraph 登记 cwd 必须在 worktree（git ls-files 随 cwd 扫）。
- worktree 内 enqueue 落 worktree 本地 pending（串行器只排主区）——快照袋 json 需挪主区 pending/。

## §6 白日追加修复批（2026-09-22 午后，Owner"全部调查修复"令）
- **夜间批次死信复活**：死因=挪袋未挪 blob（json 指主区 blob 库，内容在 worktree blob 库）→ 13 blob 校验 sha256 后补齐主区 → `requeue --from-bag` 死信原快照回队（落地自动）。
- **FIX-3 v2（关键）**：晨间 09:25 python 从未启动——实测证明 PS5.1 `*>>` 下 EAP=Continue 也拦不住首条 stderr 的终结性 NativeCommandError（pkg_resources 警告即死）；釜底抽薪=cmd /c 原生重定向（三证：stderr 落日志/PS 存活/退出码透传），午后会话已用独立进程先行恢复（PID 3304，keepalive 槽，启动恢复 holdings=2 today_fills=0）。今晨 1652 撤单刷屏=commitchain E2E 测试单（已撤 0 成交）的客户端重试噪音，非保活会话所发。
- **①孤儿钱包**：卫兵拦三调用点（谜源驱动方今夜若再开必撞卫兵=天然验证）；日刊聚合排除在册外钱包（显式 anomaly 点名隔离，存量零删除）；09-21 日刊行已重写（7 钱包 6,999,262.61）。
- **⑦HEAD 既有红修复**：test_rebuild_matches_pocket 对照查询漏 mode 过滤——另一平面（sim_daily）的 09-14/09-21 行被混入 replay_demo 基线（52+2=54>53 炸长度断言）；补 `AND mode='replay_demo'` 后 13 passed 全绿。
- **④日刊排程语义**：run_post_settlement.py（15:30 收盘结算链，Owner 2026-08-22 批准挂调度）尾部挂 `_run_sim_journal_step`——早间档=盘前预览，收盘档幂等覆盖定稿；步失败永不改结算链退出码。
- **③E4 扩量 5→46**：48 可重放候选全跑，46 成功（16 持仓/30 空仓，43.99M）；2 例如实留错（68cc 基本面列缺失/93aa 成分股窗口缺失=数据面缺口）；新增 NaN 价格卫兵（翻译件尾行 NaN 污染实证两钱包，重放自愈清零）。
- **台账终态**：51 行（48 e4_replay+1 platform+2 plan_bridge），未结算 0，unresolvable 1（09-19 疤行）。
- **②映射提案**：plan_order_mapping_proposal.md 落盘呈批（未接线，零伪造）。

## §5 补充自裁（施工中新增）
- A5 E4 重放逐候选隔离，单败不连坐，**全败才 fail-closed**（夜批健壮性优先，偏离 open_wallets 全败即抛先例，理由=51 候选质量参差，一坏件不该灭全夜账）。
- A6 重放重跑会把已结算行的结算列复位（同键覆盖），由 settle 累积扫描次日补齐——运行序契约=先判定后结算，已写入 runner docstring 与交付报告。
- A7 红②误落行（09-19 非交易日 plan 桥行）按丁线"中毒行留疤零 DELETE"纪律诚实结算 unresolvable，不物理删除。
