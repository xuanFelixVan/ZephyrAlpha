---
ttl: task_bound
---

# BUILD_trd_a10_du11 — LANE-BUILD2 验收案卷（TRD-A10 桥两缺陷 + DU-11 daily_valuation）

> 车道：LANE-BUILD2（施工验收车道）；总筹：st-qmine-20260925。
> 本卷性质：**验收与案卷**，非实现卷。实现由前任车道完成（撞 150 轮上限身亡、未及写卷），本卷只做复跑、判据打分、两项硬功夫补测与结论陈词。
> 判据真源：`docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` §四 TRD-A10 / §五 DU-11（**阈值一字未改**）。

## 一、改了什么（盘上实证，归属由总筹逐件核过）

### 甲、TRD-A10 桥客户端两缺陷（ex_core 执行域）

缺陷本质（内核文件头原话，非本卷新立论断）：本项目下单不直连券商，而是往 `orders_{env}.csv`
写指令行，QMT 沙箱里的哑执行器读行去真下单并按行首盖章（`#SENDING→#DONE/#FAIL`）。

- **缺陷① 隔夜单静默丢弃**：盘外调 `passorder` 不抛异常，执行器就给自己盖 `#DONE`＋ack(SENT)，
  而柜台从未收录该委托 → 本地订单永停在 `SUBMITTED`（09-23 实测：04:45 落单→08:53 拾取→
  09:30 开盘后柜台零收录）。
- **缺陷② submit→cancel<5s 竞态**：主线程持周期入口快照、后台线程另起读写，周期末**整文件旧快照
  回写**抹掉刚落的 `#DONE`，该行退回裸行被再次下发（09-22 实测同 remark 36 张合同）。

盘上六件（本卷逐件对拍 diff）：

| 件 | 体量 | 干了什么 |
|---|---|---|
| `src/zephyr/ex_core/bridge_instruction_kernel.py` | 新 409 行 | 把"盖章规则"抽成一份真源：`run_executor_cycle`（读-合并-替换＋终态单调 `_MARK_RANK`＋单周期单次下发＋重试预算）、`unconfirmed_claims`（幽灵单判定，柜台导出停摆期禁判）、`duplicate_remark_violations`、`should_hold_cancel`、`is_counter_confirmed`；时钟一律注入（`now_ms`），零 socket/线程/柜台 API |
| `.../adapters/qmt_file_bridge_broker.py` | +250 | 脑侧兜底：`_note_client_claims` 登记"声称已发"、`_reconcile_phantom_claims` 超判定期转**显式 REJECTED**＋error 留痕＋落 execution_report；`_scan_instruction_states` 改为"#DONE 只是声称、不再直接推终态"；撤单竞态窗口 `should_hold_cancel`；`bridge_protocol_stats()` 观察面 |
| `.../adapters/qmt_file_bridge_integration.py` | +18 | 只读装配点 `configure_read_only()`（R-H5E-1 探针降噪）＋`execution_report` 格式化——**非 TRD-A10**，见 §三乙 |
| `src/zephyr/ex_core/order_manager.py` | +9 | 撤单改传本地 `order_id`（原传 `broker_order_id`＝柜台 sysid；文件桥配对缓存按本地 id 建键→MISS 后退化成拿 sysid 当 remark 撤单→柜台配不上→`#SENDING` 卡死）＝②的撤单腿 |
| `src/zephyr/ex_core/trading_session.py` | +60 | 五级熔断磁盘影子重臂（MOD-INF-016/L08-C02）——**非 TRD-A10**，见 §三乙 |
| `tests/ex_core/test_bridge_instruction_kernel_trd_a10.py` | 新 412 行（本卷加至 ~470） | 证尺：隔夜单不自盖 #DONE 必走 #FAIL、陈旧快照不得抹终态、裸行复现不重下发、`TestCancelRaceStress100` 两腿各 100 轮、协议纯函数表 |

### 乙、DU-11 daily_valuation 部分写入（data 域，一件）

`src/zephyr/data/implementations/akshare_provider.py`（+47）：

- **病根**：续跑预查被门禁 `resume_wide_window or not payload.incremental` 挡在**日常增量**之外
  （窗口 ≥15 天才算"重采"语义），于是 `daily_valuation_incremental` 每个任务日都从标的列表头部
  从零重拉 5,560 只；单只 12s×4 worker 一整天跑不完 → 进程在排班窗口/回收器边界被杀＝
  当日只落到随机子集，同日两次重跑还互相重复覆盖。覆盖率塌陷轨迹（作者注记的实测数，
  本卷未复采）：09-18 5,570 → 09-21 5,002 → 09-22 5,003 → 09-23 2,504 → 09-24 1,500 只。
- **改法**：`if _VALUATION_RESUME_SKIP_DONE:` 让续跑预查对**所有**路径生效（进度单调累积，
  被杀不前功尽弃，缺口下一轮续补，不需要补数脚本——full_refresh 任务本身就是补数器）；
  新增 `_dedup_symbols_by_code()` 按 6 位代码归一去重（`"600000"` 与 `"600000.SH"` 两写法
  会各提交一次同一标的＝同 (symbol, trade_date) 重复版本，09-24 实测 2,000 行只覆盖 1,500 只）。
- 旧常量 `_VALUATION_RESUME_MIN_WINDOW_DAYS` 随该门禁退役（作者核过：零其它消费方）。
- 尺：`tests/zephyr/data/test_akshare_daily_valuation_resume.py` 6 条（窄窗增量必预查／宽窗刷新
  保续跑语义／预查空仍拉缺／去重保序／无重复时不动／空表容错）。

## 二、为什么这样切（内收声明）

1. **为什么抽 kernel**：盖章规则原先在沙箱哑执行器（`ZEPHYR_EXEC`，QMT 侧不在本仓）与脑侧 broker
   各写一份，两份＝第二真源，①②两个缺陷都是"两边不一致"造出来的。新 kernel 的 [CONSUMERS]
   头已声明两侧共同消费，`DEFAULT_PROTOCOL` 是唯一时限真源（调时限只调内核，
   脑侧 `configure_bridge_protocol()` 注入同一份）。
2. **内收账（净零口径）**：本卷未发现 kernel 替代掉的独立旧模块；broker 侧被内收的**旧语义**
   有两处，写清防后人走回头路：
   - `_scan_instruction_states` 旧"见 #DONE 即把本地订单推终态"→ 改为"只登记声称，终态交
     `_reconcile_phantom_claims` 判"，旧推终态分支就地删除、未另立新函数；
   - `order_manager` 旧"拿 broker_order_id 当 remark 撤单"路径改为传本地 id，未新增重试器。
   DU-11 侧＝**净删一条门禁常量** ＋ 新增一个纯函数 `_dedup_symbols_by_code`（一增一删，资产数不涨）。
3. **本车道新增（§五乙）**：内核加 `protocol_alarms()` 一张告警表（纯函数）＋ broker 一个累计计数
   `_phantom_rejected_total` 与健康面降级接线＋补一个漏导入——**未新建模块、未新建告警通道**，
   复用既有 `check_broker_health → assembly.health_check() → QMT 桥健康面板` 消费链。

## 三、双证复跑结果（本卷实测，2026-09-26 本车道显式路径复跑）

| 命令（均带显式路径，禁空参数） | 结果 | 修复前对照红证 |
|---|---|---|
| `python -m pytest tests/ex_core/test_bridge_instruction_kernel_trd_a10.py -q` | **13 passed** in ~5s | — （新尺，无"修复前"版本） |
| `python -m pytest tests/ex_core/adapters/test_qmt_file_bridge_broker.py -q` | **25 passed** in ~7s | `.runtime/tmp/trd_a10_red_before_fix.log`＝7 failed/24 passed；`.runtime/tmp/trd_a10_broker_red_before_fix.log`＝4 failed/21 passed（红均在 TRD-A10 专项类，先红后绿成立） |
| `python -m pytest tests/zephyr/data/test_akshare_daily_valuation_resume.py -q` | **6 passed** in ~3s | `.runtime/tmp/du11_red_before_fix.log`＝1 failed/5 passed（红的是窄窗增量不预查那条，正是病根本体） |
| `python -m pytest ...::TestCancelRaceStress100 -q` ×5 连跑 | 5/5 次 **3 passed**，用时 4.3–6.0s 无抖动 | 见 §五甲 |

**结论：双证全绿，修复成立。**

补注（时序，防误读）：上表是**接手时**（本车道未动一行代码之前）的原始复跑计数；§五乙补口后
同一批尺扩到 kernel 16 条＋broker 32 条＋DU-11 6 条＝**54 passed**，
`tests/ex_core` 全域 **1341 passed, 1 xfailed**（补口前 1340）。

环境坑实录（勿误判为假绿）：`python -m pytest <file> -q -p no:cacheprovider` 在本仓报
`INTERNALERROR> pytest.PytestConfigWarning: Unknown config option: cache_dir` → "no tests ran"。
这是 pytest 参数与 `pyproject.toml` 的 `cache_dir` 冲突，**不是测试没跑也不是通过**；
去掉 `-p no:cacheprovider` 即 13 passed，`--collect-only` 亦 13 collected 复核一致。

## 三乙、归属复核副产物：本袋夹带非 TRD-A10 改动（报 LANE-LAND2 与总筹）

按文件逐件 `git diff` 复核，`landing/lane_build.yaml` 认领的 5 件实现件中**有 2 件实改内容不属 TRD-A10 两缺陷**：

- `src/zephyr/ex_core/trading_session.py`（+60）：五级熔断**磁盘影子重臂**（`kill_switch_state_path` 配置项 +
  `_rearm_kill_switches_from_disk()` 启动序列第 1 步，接线点标 MOD-INF-016 / L08-C02）——属 **TRD-A12 熔断面**，不属本卷判据。
- `src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py`（+18）：`configure_read_only()` 只读装配点
  （R-H5E-1 探针告警降噪，标 st-sim-launch-20260923）＋ `execution_report` 一行格式化——属**只读探针面**。
  broker 侧同类夹带：只读构造点显式拒单（`QmtFileBridgeError("read_only Broker 不接受订单…")`）。
- 确属 TRD-A10 的：`bridge_instruction_kernel.py`（新，409 行）＋ `qmt_file_bridge_broker.py`（+250，两缺陷脑侧对账＋撤单窗口）
  ＋ `order_manager.py`（`broker.cancel_order(order.order_id)` 改传本地 id，撤单配对 MISS 致 `#SENDING` 卡死＝②的撤单腿）。

本车道不改他人清单条目（纪律：只追加自己那一条），仅如实记录：**落地袋是混合袋，
写 commit message 时须按 `--allow-multi-domain` 口径留痕，且 TRD-A12 判据不得因本袋落地而勾销**。

## 三丙、旁证红灯归属（本车道实测，勿连坐）

顺手跑的邻域回归：`python -m pytest tests/zephyr/data -q -k "valuation or akshare"`
→ **4 failed, 177 passed**（4 条全在 `tests/zephyr/data/test_akshare_index_valuation.py` 的
`index_valuation_daily` 路径与 `test_akshare_provider.py::TestFinancialIndicatorFetch` 的
`financial_indicator` 路径）。

判归"非本车道"的依据（不是"看着不像"，是路径不相交）：

- DU-11 的实改只落在 `_fetch_daily_valuation`（1715 起）与新助手 `_dedup_symbols_by_code`（11121）
  ／既有 `_load_valuation_complete_symbols`（11143），**这两条被红用例碰都不碰**；
- 主区 `src/zephyr/data/` 同时挂着多车道在途改动（`ch_writer.py`、`config/tasks.yaml`、
  `tqcenter_provider.py`、`integrity_checker.py`、`macro_vintage.py`=LANE-CNS 认领件…），
  `git status` 呈 `MM/M ` 混合态＝这批红极可能是他会话在途或 HEAD 既有，与本袋无关。

处置：按宪法 §3 条 1/4，**不代修、不认领**；报 LANE-LAND2——落地时这 4 条若仍红，
须以 own-diff 作用域判定，别让 DU-11 袋替邻域红灯连坐；同时提醒：这 4 条不在
`landing/lane_build.yaml` 的 files 清单里，也不该被吸收进本袋。

## 四、17 号文§四/§五判据逐条打分（阈值原样抄录，一字未改）

> 打分档位只有三种：**已满足** ／ **本夜不可满足（时间累积，附到期日）** ／ **缺手段**。
> 落地日记 **T0 = LANE-LAND2 真落地当日**（本车道不落地，故 T0 未知）；到期日为工作日粗算，
> 已扣 2026 国庆长假（10-01~10-07），**最终以交易日历真源核为准，勿拿本数销项**。

### 甲、TRD-A10 桥两缺陷 —— 原判据：「复现用例入库＋修复后连续 30 个交易日零静默丢弃＋撤单竞态压测 100 次 0 漏单」

| 子条 | 打分 | 依据（实测/口径） | 到期日/缺口 |
|---|---|---|---|
| ①复现用例入库 | **已满足** | 尺已在盘且入库清单在册：kernel 尺 16 条＋broker 尺 32 条（§三复跑 48 passed）；先红后绿有 2 份修复前实录（§三表）；本卷另补 3＋1 条（§五乙） | — |
| ②修复后连续 30 交易日零静默丢弃 | **本夜不可满足（时间累积）** | 修复**已落**＝机制上"丢弃"已被换成显式 `#FAIL`/`REJECTED`＋计数＋亮灯（§五乙），但"连续 30 日"要 30 个真实交易日从落地日往后数，本夜（T0 之前）零天可计。**判据未过，不得勾销** | 到期 ≈ **T0＋30 交易日**（若 T0=09-28 → ≈2026-11-13） |
| ③撤单竞态压测 100 次 0 漏单 | **协议层已满足／真柜台层不可满足** | `TestCancelRaceStress100` 两腿各 100 轮（正常受理腿＝恰好一次下发＋两行落终态；零收录腿＝零 #DONE＋每轮 #FAIL＋合同数 0），5 次连跑结果恒定（§五甲）。口径必须钉死：这是**假时钟＋假文件＋假柜台**的协议级压测，禁实盘四禁下本车道不得触达真下单通道，故"真柜台 100 次 0 漏单"未做、也不能由本卷宣称 | 真柜台腿待 T1 演练窗（禁与本卷混判）；累积窗同 ② |

**"零静默丢弃"的度量口径（本卷立，供 30 日窗验收时用）**：一次违例＝
客户端声称已发（ack SENT 或指令行被盖 #DONE）而柜台零收录、**且未被 `phantom_grace_ms`(180s)
兜住**的事件。两条真源：拦到的看 `bridge_protocol_stats()["phantom_rejected_total"]`
（进程内累计，重启归零）；持久账看 execution_report 的 REJECTED 行（reason 含
`counter_no_record`）。**"修复有效"= 违例 0；"拦到 N 次"不是违例但 N>0 当日必须亮灯**——
这正是 §五乙补的那条接线，否则数躺在 dict 里等于没数。

### 乙、DU-11 daily_valuation —— 原判据：「恢复 5,560 行/日 ±5% 连续 10 日」

| 打分 | 依据 | 到期日/缺口 |
|---|---|---|
| **本夜不可满足（时间累积）＋一条缺手段** | 病根修复**已落**（续跑预查对日常增量生效＋标的按 6 位码去重），尺 6 条全绿且有修复前红证（§三表）。但"连续 10 日 5,560 行±5%"要 10 个真实任务日的**生产数据**才能量出来，本夜一条数据都还没有（改动未落地，落地前的每一天仍按旧码跑） | 到期 ≈ **T0＋10 交易日**（若 T0=09-28 → ≈2026-10-19）。**缺手段**：判据只给了线、没给度量脚本——"行/日"必须写明口径（同 (symbol,trade_date) 多版本要先取 FINAL 再去重，否则 09-24 那种 2,000 行/1,500 只会被读成"接近达标"=假绿）。本车道**未建**该读数器（建它要写生产读路径外的新产物，且属数据面 LANE 的活），列为落地后第 1 日的验收前置件，指给 LANE-LAND2 之后的值班巡检 |

### 丙、判据之外的两条如实话

1. 本卷**不判**"TRD-A10 结案"：三条子判据里只有①已满足，②③含不可满足的时间累积与真柜台窗口，
   销项须等 T0 后由累积窗验收方（总筹/Owner）落笔。
2. 本袋混装（§三乙）意味着 **TRD-A12 熔断面**（`trading_session.py`）与**只读探针面**
   （`qmt_file_bridge_integration.py`）也随本袋落地，但它们的判据（17 号文§四 TRD-A12 行）
   本卷一条未测，**不得因本袋落地而被视为已过**。

## 五、两项硬功夫实测（任务书第 3 项，全部实测判定，未假设）

### 甲、竞态压测 100 次是不是"可重复的测试"？—— 是（且不是 1 次性用例）

实测方式：把 `TestCancelRaceStress100` 连续单跑 5 次（`.runtime/tmp` 无留痕，命令见 §三表）。

- 5/5 次 **3 passed**，用时 4.33 / 5.47 / 5.99 / 5.18 / 5.73 s，无一次抖动；
- 可重复性来源是**结构性**的，不是运气：三轮全部输入被固定（`BridgeProtocolConfig` 常量
  ＋`now_ms` 注入假时钟＋`tmp_path` 隔离假文件＋假柜台 `FakeCounter`），轮次号决定 oid/文件名
  （`STRESS-{n:03d}`/`orders_r{n}.csv`），全程无 `random`、无 `datetime.now()`、无网络与线程；
  每轮断言"恰好一次下发（零重复合同）＋两行都落终态（零漏单）"，第二轮起换 `counter_accepts=False`
  的零收录腿，加第三条 `test_every_dropped_round_leaves_fail_ack` 锁"每轮拒单必须落 ack"。
- 单次跑 = 300 轮压测（100＋100＋100），5 次连跑 = 1,500 轮零失败。
- 结论：**前任已做成可重复压测尺**，本车道无需补。唯一要说清的是它的边界＝协议层仿真，
  真柜台 100 次压测属实盘四禁禁区，本卷不代它打勾（见 §四甲③）。

### 乙、隔夜单丢弃路径有没有"埋点/告警消费"？—— 判"半成品"，本车道已补三处（含一处承重缺陷）

**实测发现（不是推测）**：

1. **承重缺陷（本车道新发现并修复）**：`_scan_instruction_states` 里用了 `MARK_FAIL`，
   而 broker 的 import 块**没导它** → `ruff F821` 直接扫出。后果链：执行器一落 `#FAIL` 行，
   脑侧扫到即 `NameError`，而 `NameError` 被 `_sync_loop` 的 fail-soft 兜成一条 warning，
   **连带整轮同步（柜台镜像刷新＋幽灵单对账）静默跳过**＝"治静默丢弃的代码自己制造新静默"。
   红证＝`.runtime/tmp/build2_fail_mark_red_before_fix.log`（`NameError: name 'MARK_FAIL' is not defined`，
   真消费腿 `_sync_local_channel` 上炸），修复＝import 补一名（1 行），修复后新用例
   `test_fail_mark_on_orders_file_is_consumed_not_crash` 绿。
2. **埋点在、消费不在（原状）**：`check_broker_health()` 已把 `duplicate_remarks` /
   `unconfirmed_claims` 两个数塞进 `counter` dict，但**等级判定完全不看它们**——09-22 那种
   36 张同 remark 事故在监控面上仍是绿灯；且装配聚合 `health_check() → QMT 桥健康面板`
   这条既有消费链只认 `level`，数躺在 dict 里没人判＝装饰性埋点。
3. **丢弃被拦后无累计账（原状）**：幽灵单转 REJECTED 只有一条 `_logger.error`，
   日志滚完就没了，健康面看不出"今天拦过几次"。

**本车道补的三处（小补丁，改实现保守）**：

- 内核新增纯函数 `protocol_alarms(*, duplicate_remarks, phantom_rejected_total)` ＋两个告警常量
  （`ALARM_DUPLICATE_REMARKS` / `ALARM_PHANTOM_REJECTED`），把"什么算既成事故"这张表放真源侧；
- broker 加累计计数 `_phantom_rejected_total`（在幽灵单转 REJECTED 处 +1），
  `bridge_protocol_stats()` 与 `check_broker_health()` 同时输出 `phantom_rejected_total`/`alarms`，
  并且**alarms 非空即把 `ok/level` 打成 `degraded`**（不改既有阈值判定、只降不升），
  让既有面板横幅与 `health_check()` 聚合等级真的动起来；
- 明确不误报红线：**判定期内的在途声称（`unconfirmed_count`）不进告警表**——每笔正常下单都会
  短暂出现，接进去＝天天狼来了，两周后这条告警作废，等于换个地方继续静默。

**新尺与红证**：kernel 侧 `TestSilentDropAlarmSurface` 6 条（清洁态不亮／36 张亮／拦到 1 笔亮／
单张合同不亮／两类同时亮／在途声称不亮）；broker 侧 4 条（在途不误报、丢弃后降级、重复合同降级、
`#FAIL` 消费不炸）。红证采**缝隙扰动**（直写 `src/` 被本环境拦为 `OSError[Errno 22]`——
疑似文件守护钩子，改前须 `lock_files.py acquire`，故不摘盘上代码）：
`PYTHONPATH=.runtime/tmp BUILD2_PROBE=P1 python -m pytest <3 条> -p build2_red_plugin`
→ **2 failed, 1 passed**（把 `protocol_alarms` 打成恒空＝修复前语义，降级用例必红）；
`BUILD2_PROBE=P2`（只认重复申报、忽略幽灵计数）→ **1 failed, 2 passed**（证明计数是承重的）；
`P0` 基线 → 3 passed。实录：`.runtime/tmp/build2_red_probe_seam.log`，扰动插件
`.runtime/tmp/build2_red_plugin.py`（临时件，TTL 区）。

**回归面**：`python -m pytest tests/ex_core -q` → **1341 passed, 1 xfailed**（补口前为 1340，
＋1 即本卷新用例）；`ruff check` 4 个受影响文件全过；`ruff format` 已把两个测试文件统一到
仓库基线（本仓 src 侧本就 ruff-format 干净）。

## 六、给 Owner 的一句话

TRD-A10 与 DU-11 的**修复已落且双证全绿**（含本车道补出的一处承重缺陷：`MARK_FAIL` 漏导入会让
新加的 `#FAIL` 消费腿炸掉整轮同步，等于治静默的代码自造新静默），但**判据一条都没过**——
"连续 30 交易日零静默丢弃""连续 10 日 5,560 行"都是要落地日 T0 往后数的时间累积窗
（≈T0+30 交易日／≈T0+10 交易日，见 §四），且 DU-11 还缺一把"行/日"的度量尺
（不先按 FINAL 去重就会把 09-24 的 2,000 行/1,500 只读成接近达标＝假绿）；
本袋又是混装袋（夹带 TRD-A12 熔断与只读探针面），请 LANE-LAND2 按跨域留痕落地，
落地日一到就把 §四的两条窗表挂进值班巡检，别让"已修"两个字在 30 天里被当成"已过"。

落款：LANE-BUILD2 施工验收车道（执行人＝继任子代理，非 Owner 署名）；总筹 st-qmine-20260925 派单。
本卷只出案卷不出裁定，判据销项权在 Owner/总筹。
