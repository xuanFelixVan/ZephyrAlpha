---
ttl: task_bound
title: 考试班 st-examrun-20261012 班台账（令 B·CPU 通道）
created: "2026-10-12"
sid: st-examrun-20261012
family_id: EXAMRUN-CAMPAIGN-20261012
---

# 〇、头条（Owner 醒来先读这七行）

1. 本班今晚**开考 0 张**。不是没干活：在册通道上的"可考存量"实测＝**0**（三证齐，§2）。
2. Owner 令卡的北极星"N 千题"在本仓**没有对应题池**：卡册总数 495，其中未考 177、已考 31、
   骨架无题面 186、缺实现 39、缺数据 62；另一套在册题池（原问题 283 问）已 100% 有考果行。
   **今晚可达上限＝个位数**，且必须先补绑定层（算子），不是补机器、不是补时间。
3. 首张 PASS：**没有**（分数册 44 行全 fail，pass=0）。不放水造一张，理由见 §6。
4. 本班挖到并当班修掉两处会让"每题入账"变假绿的洞（§4）：执行器把试次册路径焊死在生产真源
   ⇒ 测试跑把 2 条 `TDM-E-TEST` 假试次写进生产 N 账本（10-12 00:58 实测）；修＝注入位＋两颗防回归钉。
5. 存量 N 账本正在少记：分数册 44 行去重得 38 个 (卡,日) 键，dev 面试次册只有 **18** 条
   ⇒ **少记 20 条＝53%**（主区工作区面 34 条＝16 条从未落地；10-11 全天出分在 dev 上零入账）。
   DSR/PBO 分母因此虚低一半——这是在册病根（09-27 少记 17.4%、10-08 复犯）的**第三次、更狠的一次**。
6. GPU 通道**未解锁**（§3：03 件重判表未出品，其自家报告写"对 B1 无判别力、须等归因落地才有资格判"）；
   本班全程 CPU，且 01:00–04:00 零 CH 让路窗**对象真实存在**（tilib 夜跑今晚=Ready，next=02:30）。
7. 待 Owner 点的三件（§5）：要不要给"目标面通道"立项（解 118 张＝未考面的 67%）、
   要不要授权本班补账 16 条（代投他班试次）、六段切点 8 张卡拍不拍。

工棚=`D:/ZephyrAlpha/.worktrees/st-examrun-20261012`（分支 `ai/st-examrun-20261012/task-examrun-overnight-b`，
建车基线 dev@20fa9c43bb）；SessionRegistry 逻辑会话在册（pid=0）＋心跳 daemon PID 36620；
reaper keep 已 CAS 追加本 sid 三条（追加后他会话条目零损，`st-mineloop2-20261012` 命中数改前改后皆 3）。

# 一、判据铁律（P0）——已核到代码 return 行，非纪律口号

铁律声明：**存量卡一律按其卡面注册判据考；不得用新阈值/通缩校正重判历史卡；新卡按挖矿班 SOP 新阈值考。**

本班逐条亲读的四道机械闸（全部 fail-closed，写口而非审计层）：

| # | 点位 | 判据本体（读到 return 行） | 性质 |
|---|------|--------------------------|------|
| 1 | `scripts/backtest/fexam/card_binding.py:818-830` | `spec=OPS.get(op)`；`if spec is None: raise ValueError("op_not_in_ops_book:...")`；`if q.replace(" ","") not in blob.replace(" ",""): raise ValueError("prose_quote_not_found_on_card:...")` | 算子必须在册＋引句必须是卡面原文子串，防自创口径 |
| 2 | `card_binding.py:968-970` | 出分后 `_judgment_snapshot` 与出分前逐键比，`if before != after: raise BindingIntegrityError("出分后卡面判据集被改…本卡中止须人工复核")` | 挪门柱即中止＝"存量卡判据零改动"由代码守 |
| 3 | `scripts/backtest/fexam/calibration_exam.py:482-495` | `unknown = set(p) - set(_CALIBRATION_JUDGED_KEYS)`；`if unknown: return "fail", ["未支持判据键（机判面待扩，fail-closed）: …"]` | 未知冻结键=判败不=跳过；执行器零裁量 |
| 4 | `calibration_exam.py:644-654` | `if status != "preregistered" and not force: raise`；`if signal is None or target is None: raise RuntimeError("缺省 CH 取数面未接…")` | 骨架卡（empty）禁考；无注入不出分，不静默缺省取数 |

本班零动面（逐项申报）：判据数值 0／卡面阈值 0／窗与分桶 0／判官词表 0／路由分派 0／
绑定册既有格 0（既未新增亦未把 rejected 改回 approved）／GPU 面 0 碰。

一处 fail-open（**本班不代修、不放宽**，点名给归属）：
`card_binding.py:955` `tgt = index_next_day_return()` —— 无条件注入沪深300 次日收益，
`run_one` 全程没有"注入序列是否就是卡面引句所讲那条"的同一性断言（:944-958 读完无此行）。
后果＝卡面 target 非"指数次日收益"的卡一旦被绑定开考，会**答错题而不报错**、出可读的假分。
同型在册申报＝矿考循环班 99_checkpoint §18"第二道洞"；修法（ArmBase＋`require_target_identity`，
r 位闸跑在量纲帽之前）在矿考二班在飞袋 `q-20261012-st-mineloop-20261010-0080/0081`。
⇒ 本班按红线⑥避让在飞件，不抢改；本班因此**不开任何 target 面不同形的卡**（普查见 §2）。

一处归属缺陷（本班新钉，同样不代修）：`card_binding.py:964` `recorded_by="st-mineloop-20261010"` 硬编码
⇒ 别班经此执行器开考的所有试次，N 账本 `recorded_by` 一律记成矿考循环班。
若 Owner 令本班代跑批量，须先把该位做成入参（一行改动，落点在矿考二班在飞件，等其落地）。

# 二、P1 存量题池＝实测分母与解锁地图（全部本机取数，非记忆）

dev 面（`20fa9c43bb`）实测，取数件=`.runtime/tmp/st-examrun-20261012/inventory_cards.py`（只读，零 CH）：

| 面 | 实测 |
|---|---|
| 卡册文件数 | 495（令卡写 494，差 1＝本班按 git ls-tree 实数报，不四舍五入） |
| status 分布 | preregistered 177／empty 186／examined 31／blocked_on_impl 39／blocked_on_data 62 |
| family 分布 | comparison 197／calibration 188／ablation 75／shadow 35 |
| 分数册 | 44 行／31 张卡／verdict `fail:44 pass:0` |
| 绑定册（dev 面 `02_binding_book.yaml`） | 14 格＝13 approved＋1 rejected；**13 格全部已出分** |

**可考面＝0 的三证**（三条独立尺，同向）：

1. 在册普查器（它自己声明"零 CH"）：`card_binding.py --mode classify` 跑 177 张 preregistered
   ⇒ `A 0／A? 11／B 17／C 121／D 0／U 28`。A/D 才是"现器可考"，两者皆 0。
   （普查件=`.runtime/tmp/st-examrun-20261012/classify_census_20261012.yaml`）
2. 绑定格穷举：OPS 共 11 个算子（dev `card_binding.py:770-815`），**11 个已被在册 13 格全部占用**；
   六份前役规格件（`sector_lane_spec/emotion_lane_status/11_prebind_review/27_five_card_freeze_protocol/
   12_gcal1_reconciliation/W-A_arm_pilot_spec`）里点名 card_id 且给 op/args 的条目，逐条过四问
   （op 在不在 OPS／绑定册有没有格／卡 dev 面是不是 preregistered／有没有被判死或须走新版本卡）
   ⇒ **READY_TO_BIND＝空集**。三张"卡面齐只缺算子"（`sector_amount_share_top_decile_spread`／
   `sector_top_warning_density`／`rating_upgrade_cluster_share`）中前两支已被 `17_:17,45` 判须新版本卡，
   第三支 `TDM-E-L2-09/calibration/03` 在 `27_:57` 五支新版本卡族册内（`can_freeze_in_window: 否` :62）。
3. 复考面穷读卡面纪律（31 张逐件）：28 张卡面 discipline 逐字同文
   「冻结后开考；事后挪门柱=作废（G4-5）；试次全入 n_trial_ledger」＝**对复考未声明**；
   明文禁止 4 张（`L1-S2/16`／`L1-S3/07`／`L1-S3/08` 卡面 `one_round_limit`＋
   `X-S1-02/comparison/02` 卡面:39「口径版本不重审」）；
   唯一有在册复考依据的 3 张（五分位三卡，凭 `09_caliber_deviation_note.yaml:43-45` 口径修复声明）
   **已重跑过**（分数册内 `mineloop-recast-*` 与 `mineloop-route-audit-*` 两批在册，各 3 行）⇒ 复考面也已耗尽。
   按红线"未声明不得推定许可"，本班未对任何已考卡动一手。

未考面 177 张按"解它要什么"切分（这就是解锁地图，逐类给成本与地盘）：

| 类 | 张数 | 缺的东西 | 谁的地盘 | 本班动作 |
|---|---|---|---|---|
| C·target_face 不同形 | **118** | 执行器逐卡 target 面解析＋同一性断言（`card_binding.py:955` 的洞） | 矿考二班在飞（袋 0080/0081） | 只做普查与报价（§6.2），不开考 |
| C·needs_replay_engine | 2 | 撮合引擎逐臂适配器 WO-A1（双臂） | 矿考班 16 支双臂卡＝红线⑤零接触 | 不碰 |
| C·horizon 不匹配 | 1 | next_5d 型 horizon 面 | 同上执行器面 | 不碰 |
| B·panel_deferred | 17 | 面板去重/撮合口径须逐表面核（CH 实测）＋面板算子 | 考试班可做，但要 CH 且 8 张卡在 `11_/27_` 判死册内 | 04:00 后按表面核口径，未判死者才绑 |
| A?·表未登配方册 | 11 | `_REGISTERED_TABLES`（dev 面仅 3 表）登记＋对应算子 | 本班可做（须粒度实证，禁猜 SQL） | 逐张过三闸：4 张已判死（§1），7 张在板块族收口册内 |
| U·无 data_binding 节 | 13 | 卡面本身没写数据绑定＝**题面未冻结** | 挖矿班（卡面是判据立法面） | 不代拍，列供题需求 |
| U·多表须复合配方 | 15 | 复合配方册（一格一序列装不下） | 挖矿班＋执行器双面 | 同上 |
| blocked_on_data 62 张的最大簇 | 9 张＝`c1_market.sector_constituent` | 板块成分 PIT 深史（在册：该表是三处采集宇宙唯一读取源，裸扩即造回归） | 数据车道 | 呈数据解锁申请，不硬考 |
| 情绪族 close_final 回补的真实解锁 | **1 张候选，且未解锁** | `L9-G4/ablation/02` 卡面:96-101 解锁条件是"概念成分按日落版≥8 版本且 breadth≥250 日"，不是 close_final | 数据车道 | 纠正前役"close_final 续上即解锁"的推测面 |

# 三、GPU 通道解锁判定＝未成立（预签条款逐字对表）

- 条款（统预先签）：`GPU 化班 03 件重判表出品` **且** `§二·丙 口径按其预签生效` ⇒ 解锁；解锁前一律 CPU。
- 实测（盘面，`docs/_working/gpufeed_campaign/03_gpux_final_report.md`）：
  - `:453-457`「§二·丙 的三档双比例检验（1e-8／1e-6／1e-4）在**本跑批形态下对 B1 无判别力**」；
  - `:465`「**须等 §八 那针归因落地**（同进程双跑判据已在册）后才有资格判。本班不据此改任何线」；
  - `:39` 级 3 的 p₁/p₀ 读数（GPU 超 1e-8 者 26 格 2.48% vs 纯 CPU 自对照底 17 格 1.62%）
    系列序修复（袋 `q-20261012-st-gpux2-20261011-0006`）**之前**的跨进程量，已被在册定性为污染读数；
    修后 n=60 试点 p₀=0，n=1050 终判未跑。
- ⇒ 两条件皆未成立，**本班全程 CPU 通道**（参考实测吞吐：36 格 23.9s／72 格 25.3s，够）。
- 解锁后的登记口（预研，未动）：互斥组真源=`config/resource_profile_registry.yaml` 的 `gpu_default` 组，
  但**该册是生成器件**（头一行"禁手工增删条目"，`counting_rule: entities 数组条目数`）⇒ 挂条目须走
  生成器四源（`generate_resource_profile_registry.py`），且在册已证：该册 HEAD 面若存任一
  `sched_mem_ceiling` block，改动它的袋**必被 RESOURCE-SCHEDULE 拦**（预算类判据全量无豁免旗）
  ⇒ 本班用 GPU 前先量存量 block，量出非 0 就停下呈批，不硬闯。

# 四、当班自挖两洞（已修，随袋）

1. **试次册写入路径无注入位＝测试跑污染生产 N 账本**。
   本体：`calibration_exam.py:736` `TrialLedger().record_run(...)` 用缺省路径
   （`src/zephyr/backtest/core/n_trial_ledger.py:72` `LEDGER_REGISTRY_PATH=REPO_ROOT/docs/…/trial_ledger_registry.yaml`），
   而 `run_card` 签名（:632-642）**没有** ledger 路径入参 ⇒ 任何调用方（含单测）都直写生产册。
   实测后果（主区工作区面 trial registry，`recorded_at=2026-10-11T16:58:56+00:00`＝本地 10-12 00:58）：
   `examcard:TDM-E-TEST/calibration/02` 与 `examcard:TDM-E-TEST/comparison/02` 两条 n=1 假试次，
   `recorded_by=calibration_exam`。写入者钉死＝`tests/backtest/test_calibration_exam.py:22,127`
   的 `card_id="TDM-E-TEST/calibration/02"`／`"TDM-E-TEST/comparison/02"`（与在册 §5-P4 那条"疑似单元跑写生产册"
   同一桩，本班把它钉到底）。
   该测试件第 3 行自称「测试隔离：卡/分数册全在 tmp_path」＝**半截隔离**（分数册隔离了，试次册没隔离）。
   修法（零行为变更给生产路径，只开注入位）：`run_card(..., ledger_registry_path=None)` →
   `TrialLedger(registry_path=ledger_registry_path)`；两颗钉＝
   ①注入位真被传给 TrialLedger 构造（改前必红：改前该 kwarg 不存在＝TypeError/被忽略）；
   ②跑完整支测试文件后生产册 sha256 一字不变（改前必红：现状就变）。
   污染清面：那 2 条**只在主区工作区面、不在 dev**，故本班不"删生产数据"，而是把"落地时须剔出"
   写进 §5 的补账判据（判据＝批次卡号必须能在卡册找到同名件；`TDM-E-TEST` 在卡册零同名＝排除）。
2. **`--mode classify` 的 `--cards-dir` 不接相对路径**（相对路径时 `p.relative_to(RUN_ROOT)` 抛 ValueError 崩整普查）。
   本班绕法＝传绝对路径（已在 §2 命令面留痕）。属普查器可用性缺陷，一行可修，非本班件、未代修。

（自纠一条，方向＝本班把自己吓住了）本班 01:4x 探 ClickHouse 探的是 `127.0.0.1:8123` 得 CLOSED，
据此差点上报"CH 断供"。真源在 `config/.env.clickhouse`：`CLICKHOUSE_HOST=172.24.30.100`。
复测 `172.24.30.100:8123/9000/22` 三向皆 OPEN，VM `zephyr-ch` State=Running（uptime 8h11m）。
⇒ **数据面在位**，本班全程未开 CH 只因为窗纪律（01:00–04:00），不是因为连不上。

# 五、呈批与移交（不自拍）

| # | 件 | 事实与证据 | 建议默认（不代拍） |
|---|---|---|---|
| P-1 | N 账本少记 53% | 分数册 44 行去重 38 个 (卡,日) 键；dev 试次册 examcard 记录仅 18 条；主区面 34 条；`dev⊂主区` 严格超集（`dev−main=0`）⇒ 16 条未落地、另 10 条三面皆无 | 让车道自落（红线：代投在途字节会变成回退弹）；若 Owner 要本班补账，本班只投"dev 字节＋16 条逐字记录"的只增袋，并剔除 2 条 `TDM-E-TEST` |
| P-2 | 目标面通道＝118 张的门 | §1 的 `card_binding.py:955` fail-open＋§2 表第一行 | 等矿考二班 0080/0081 落地后由本班逐张开绑定；本班可先交 target_source 去重普查（§6.2） |
| P-3 | 六段切点/四态重建未冻 | `emotion_lane_status.yaml:350-358`：8 张需数值重建，卡面已冻 0 张、partial 1 张；`L2-05-1/02:21,58` 等点名"在册六段口径"查无真源 | Owner 拍切点真源；拍前本班不替卡填数 |
| P-4 | 词表外键（`resid_ic_min` 等） | 在册普查 `16_pillar_vocab_census.yaml:1768-1769`；`calibration_exam.py:487-493` 现 fail-closed 判败 | 扩词表＝判官机判面立法，须另裁；本班未扩 |
| P-5 | 题池天花板 | §0 第 2 行＋§2 | 要"N 千题"须先扩题面（186 骨架卡是矿面），不是扩算力 |
| P-6 | 资金/实盘/出域/法律 | 零项 | — |
| P-7 | 相邻册 78 张 pass 认不认 | 判据面实测见 §11（绝对值线／direction 78/78 未声明／不看 icir／线自述"初拟待Owner校"） | 认＝补 direction 注解后另起新版本卡重考（禁原地重判）；不认＝维持卡册为唯一 PASS 面。本班两不代拍 |
| P-8 | 面板形绑定通道要不要本班建 | 一条通道解最多 39 张（§10.2 表首行）；成本＝2 个新算子形（面板信号＋面板目标）＋须与 §9.3-B 的 ICIR 面同批（否则每台面板卡发假 PASS）；前置＝CH 粒度实证（断供面禁硬考） | **今夜不建**：OPS 注册表与 `run_binding_book` 都在 `card_binding.py`，而该件 10-12 01:1x 起在矿考二班（`st-mineloop2-20261012`，keep 已登记）在飞——按红线⑤⑥与宪法 §3.4 避让，不抢共享件；本班已把两处结构缺陷的**修法与钉**写清（§9.3），谁先 claim 谁建 |

# 六、执行序与时间账（供周审计）

- 01:39 进场；01:40 冷启动两闸（`python=3.12.8`、`setup_dev_env --check`、`lock_files cleanup`、
  reaper `--status source=live`，`ZephyrAlpha_ProcessReaper state=Ready last=01:37:23 rc=0` ⇒ 写操作前提成立）
- 01:5x 开工作树＋SessionRegistry(pid=0)＋心跳 daemon PID 36620＋reaper keep CAS 追加
- 02:0x–02:4x 分母普查/在册 classify/四张最近门/情绪族/复考纪律/绑定穷举/判据闸亲读
- 02:5x–03:2x 自挖两洞定性＋修复与两颗钉
- 04:0x 起（窗毕且 `date` 实测后）：见下"跑批单"
- 让路窗对象核验（在册工法"窗口须验对象"）：本班 01:4x 实测
  `tilib_indicator_backfill_nightly state=Ready next=10/12 02:30`（与 10-11 那夜的 Disabled **不同**）
  ＋`ZephyrAlpha_GateFullTreeAudit Ready 03:30`＋`LibraryLedgerBackup Ready 03:30`＋`MetaqAuditReconcile Ready 03:50`
  ＋`DailyBackup Ready 06:00` ⇒ **今晚 01:00–04:00 窗有对象，本班零 CH 查询照守，不用 override 旗**。
- 系统面（影响本班并发上限）：01:40 reaper 报 `commit_pct=87.68 / cpu_pct=88.0 / breached=['ALERT-SYS-001']`
  ＋`worktree_changes=835>50` ⇒ 本班不自造并发批（在册事故形态：并发崩在 git add，0xC0000142），
  长批一律串行＋单袋走正门。

### 6.1 04:00 跑批单（现成命令；到点先 `date` 实测，再按闸自然放行）

```
# ① 复测 dev 面（挖矿/矿考两班可能已落新卡与新绑定；本班分母只认 dev 现字节）
python .runtime/tmp/st-examrun-20261012/inventory_cards.py
python scripts/backtest/fexam/card_binding.py --mode classify \
  --cards-dir D:/ZephyrAlpha/docs/03_modules/_domain_backtest/exam_cards \
  --out .runtime/tmp/st-examrun-20261012/classify_census_after0400.yaml
# ② 仅当 A/D 或 READY_TO_BIND 非空才开考（CPU 通道，窗闸自然放行，本班不加 override 旗）
python scripts/backtest/fexam/card_binding.py --mode run \
  --binding-book docs/_working/mineloop_campaign/02_binding_book.yaml \
  --approve-list .runtime/tmp/st-examrun-20261012/approve_examrun.txt \
  --scores docs/03_modules/_domain_backtest/exam_scores_v1.yaml \
  --out .runtime/tmp/st-examrun-20261012/exam_run_r1.yaml --tag examrun --dry-run
# ③ 每题入账核验（在册教训：目录存在≠已入账；跑后立即对账）
python .runtime/tmp/st-examrun-20261012/reconcile_ledger_vs_scores.py
```

### 6.2 本班窗内交付的第二件（04:00 后只读，零 CH）

`target_source 去重普查`：把 118 张"target_face 不同形"卡的 `data_binding.target_source` 原文
逐字抽出→归一成"需要几条目标序列"的清单。这是给 Owner 的 P-2 报价面：解一条序列＝解 N 张卡。

# 七、首张 PASS 看守（P3）

在册 44 行全 fail，pass=0。本班纪律：任何卡出 pass ⇒ 立即单独上报并晨间包置顶，
随件给五样（门柱逐柱读数、n/OOS/regime 三面、绑定引句原文与卡面行号、试次入账凭据、该卡纪律面是否允下一轮）。
**不缩任何阈、不把 fail-closed 的未知键当已判、不给未声明复考的卡加试次**——
PASS 的全部价值在于它是真的；一张造出来的 PASS 会把后面所有 DSR/PBO 读数一起带歪（§4 P-1 的 53% 少记就是前车）。

# 八、晨间包

（滚动更新段，收官时填终数；§〇 是它的头条摘要）

## 8.1 已考总数 / 通过数 / FAIL 分布

- 本班开考：**0 张**（判据与可考面见 §2 三证＋§9.6 第四次独立确认；未硬考＝非漏考）。
- 在册累计：44 行／31 卡，`fail:44 pass:0`（04:02 复测同值）。
- 本班新增分数行 0／卡面 status 改动 0／绑定册新增格 0／CH 实跑 0 次。
- 相邻册读数（非本班题池，见 §11）：指标尺 143 条中 pass 78／rework 55／retire 10，其 pass 线自述"初拟待 Owner 校"。

## 8.2 GPU 解锁时刻与切换记录

- **未解锁，未切换**（判定与 04:02 更新的读数见 §10.5：重判表已在 GPU 二班车道出品 03:21，
  但未落 dev，且其自身结论＝9 格 >1e-4"判未过待裁"）。本班全程 CPU，GPU 面零碰、互斥组零挂号。

## 8.3 阻塞清单（按解锁价值排序）

1. 绑定层算子＝唯一吞吐瓶颈（OPS 11 个全被占用；READY_TO_BIND 空集，四把尺同向）。
2. **面板形绑定通道**＝最多 39 张的门（实测绑定层交不出宽表；落点件在矿考二班在飞域）＝§5 P-8。
3. 逐卡目标面闸（`card_binding.py:955` 无条件注 CSI300 且无同一性断言）＝118 张的门，矿考二班在飞。
4. 撮合引擎逐臂适配器（WO-A1）＝30 张双臂卡的门，红线⑤零接触。
5. 卡面供题＝186 张骨架＋13 张无 data_binding＋附录那 8 条 ablation 卡（§15，判据须先呈统筹批）。
6. 六段切点未冻＝8 张（Owner 门位 P-3；挖矿道呈批稿已在主区工作区待落，见 §15）。
7. 词表外键（`resid_ic_min` 等，实测 84 张）＝扩面须立法（P-4）。
8. **机器面**：04:02 `commit_pct=99.94 / degraded=True`＋队列 pending 56 ⇒ 落地链随时可能崩，
   本班交付是否落 dev 需按 §16 的命令复核，不靠通知。

## 8.4 本班交付清单与复核命令

| 交付 | 位置 | 复核命令 |
|---|---|---|
| 判据铁律四闸证据＋一处 fail-open 一处归属缺陷 | 本件 §1 | `git show dev:scripts/backtest/fexam/card_binding.py \| sed -n '818,830p;955p;964p;968,970p'` |
| 实测分母与解锁地图 | 本件 §2 | `python .runtime/tmp/st-examrun-20261012/inventory_cards.py`（零 CH） |
| GPU 未解锁判定 | 本件 §3 | `sed -n '453,465p' docs/_working/gpufeed_campaign/03_gpux_final_report.md` |
| N 账本少记 53% | 本件 §4-1/§5 P-1 | `python .runtime/tmp/st-examrun-20261012/reconcile_ledger_vs_scores.py` |
| 试次册注入位修复＋两颗钉 | `calibration_exam.py`＋`tests/backtest/test_calibration_exam.py` | `pytest tests/backtest/test_calibration_exam.py -q`＋生产册 sha256 前后比对 |

# 九、02:5x 追加账（用尺不用手算；旧案卷 §0/§4/§5 原样留存，本节是更正与新增）

## 9.1 N 账本少记——改用机械尺后的准确数（旧 §0 第 5 行"53%"是被本节取代的口径）

尺=`.runtime/tmp/st-examrun-20261012/reconcile_ledger_vs_scores.py`（判据逐字写在件头：
对分数册每行令 `key=examcard:<card_id>:<date>`，该 key 必须出现在账本 `batch_records` 的 batch_id 集合里＝
`record_run` 的幂等键本身）；输出=`.runtime/tmp/st-examrun-20261012/reconcile.json`。实测：

| 读数 | 值 |
|---|---|
| 分数册行 / 去重后期望试次键 | 44 / **38** |
| 账本记录数 dev／主区工作区／矿考循环班车道 | 29／49／44 |
| **dev 少记** | **21/38＝55.3%** |
| 主区工作区仍少记（三面皆无＝从未入账） | 10 键 |
| 未落地记录（主区有 dev 无） | **20 条**＝examcard 形 16＋grid 形 4 |
| 其中测试泄漏形（`TDM-E-TEST/*`） | 5 条 ⇒ **不得补**（可补＝15 条） |
| dev ⊂ 主区 严格超集（回退集为空） | **成立**（`regression_ids=[]`）⇒ 补账机械安全 |

更正两条方向：①本班 §0 曾手算"少记 20 条＝53%"，用尺后＝**21 条＝55.3%**（手算漏了 dev 账本里那条
`examcard:TDM-E-TEST/calibration/02:2026-10-10` 已是污染在册）；②dev 账本**已有 1 条**、主区已积到 **6 条**
测试泄漏形（10-10／10-11／10-12 各两条）⇒ §4-1 那个洞不是"00:58 一次事故"而是**每晚测试跑都在漏**，
本班已随袋封住写口（注入位＋autouse 夹具）。
补账不代投：15 条可补记录的 recorded_by 属他班（矿考循环班 10／calibration_exam 缺省 5 等），
且矿考二班此刻仍在飞该册；按在册处方"车道自己后落地则代投袋会变回退弹"⇒ 本班只交尺与清单，
授权面见 §5 P-1。

## 9.2 供题面地图（177 张零 CH 普查，件=`target_face_census.yaml`）

| 闸 | 过闸数 | 不过闸＝解锁物 |
|---|---|---|
| 卡面 target＝指数次日收益（现器唯一目标面） | 49 | 128 张需"逐卡目标面解析＋同一性断言"（§1 的 fail-open 就是这道闸缺的件） |
| pillars_numeric 全在判官五键词表内 | 93 | 84 张带词表外键 ⇒ `judge():487-493` fail-closed（考了也只能得假 fail） |
| 分桶型现器有面（quintile/decile/tercile/quantile_4） | 47 | 130 张的分桶形现器无面 |
| 未被六份在册判定件点名（保守尺） | 136 | 41 张在前役判定面内（多数已判死或已考） |
| 五闸全过＝本班候选 | **11** | 逐张 cls：U 5／B 4／A? 2（见下表） |

11 张候选逐张与阻塞因（本班尺偏松处已标注）：

| card_id | cls | 缺什么 |
|---|---|---|
| L1-S0-1/calibration/03_market_scope_sentiment_series | U | signal_column 是"sentiment_index（主）/ avg_polarity、positive_share…"多列形 ⇒ 卡面未冻结单列 |
| L1-S0/calibration/03_流动性卡 | U | 卡面无 `data_binding` 节＝取数面未冻结（挖矿班域） |
| L1-S2/calibration/07_连板家数分布 | U | 同上 |
| L1-S3/calibration/02_昨日涨停溢价 | U | 同上 |
| L2-07-1/calibration/02_回踩四因子合成分 | B | **面板形＝现绑定层交不出**（§9.3-A）；另卡面 :73/:75-76 自陈码内三维与节点文字四维互斥 |
| L2-07-1/calibration/03_死常量两腿_结构破坏与超窗横盘 | B | 同上（分档与权重已冻在卡面 :72-79，缺的是面板通道） |
| L2-09/calibration/04_业绩预增催化剂腿 | U | 三表复合配方（earnings_forecast＋express_report＋research_report） |
| L9-A01/calibration/02_日线动量截面 | B | 面板形；且 target_source :58 明写"面板 target 宽表（个股 t+1 收益）"≠现器注入的指数次日收益 |
| L9-A03/calibration/02_880板块相对强弱持续性 | B | 面板形；target :56 为 next_day_sector_return（板块面） |
| L9-A10/calibration/02_全球风险因子隔夜传导 | A? | 前役闸：PIT vintage（卡面 :32-33 判 macro_data 现值回算＝前视污染）＋五因子禁合成（一格一序列装不下） |
| L9-A15/calibration/03_币圈镜像资金费率对BTC | A? | **本班尺误纳入**：卡面 target :61-62 是 `crypto_kline_daily BTCUSDT`，被宽正则误判成"指数次日收益"；前役尺同型误判见 `01_binding_census.yaml:1057-1065` |

⇒ 结论不变且更硬：**这 11 张里没有一张是"本班今晨可绑可考"的**；解锁 8 张的公共闸＝面板形绑定通道（§9.3-A），
解锁 128 张的公共闸＝逐卡目标面。二者的落点件（`card_binding.py`/`arm_protocol_binding.py`）在矿考二班在飞域。

## 9.3 面板形两处结构缺陷（本班实测钉死，非读码推断；已修＋三钉）

A. **绑定层交不出面板**：OPS 11 格 fn 签名一律 `-> tuple[pd.Series, dict]`（dev `card_binding.py:770-815`），
   而 panel 支路 `_panel_metrics(signal: pd.DataFrame, target: pd.DataFrame)`（dev `calibration_exam.py:191-193`）
   要两张宽表并走 `fast_rank_ic` 的 `.columns` 交集（`ic_exam.py:73`）。
   实测（`.runtime/tmp/st-examrun-20261012/panel_face_probe.py`）：
   `A RESULT: AttributeError: 'Series' object has no attribute 'columns'`
   ⇒ 普查 B 类 **17 张**卡不是"缺算子"，是**缺形**——结构不可考，且现器不报错只在取数处抛。
B. **面板路的 ICIR 柱从未被评估且不披露**（假绿，两处字节错位）：
   - `ic_exam.ic_stats` 回键 `"icir"`（:42），`_panel_metrics:208` 读 `"ic_ir"` ⇒ 面板路 `ic_ir` 恒 NaN
     （实测：同面 ic_stats 得 icir=1.6714，而 `_panel_metrics` 回 nan）；
   - `judge`/`_judge_calibration_face` 对 NaN 的处置＝跳过加败（:457 只在不为 None/NaN 时比较）；
   - `_unjudged_pillars:292` 判据是 `m.get("ic_ir") is None` ⇒ NaN 情形**不进未判柱清单**。
   实测合成果：`verdict=pass fails=[]`，而 unjudged 面只列 mono_spearman_min 与 regime_same_sign，
   **ic_ir_min 消失**＝一张五柱全冻的卡可以只被评 3 柱就发 PASS。
   现网未爆因＝面板卡一张也没考过（A 挡住了）；**一旦面板通道落地，这条就是每台面板卡的假绿源**。
   本班修法（两处同向，只增 fail 不增 pass）：`ic_ir` 读回真键 `icir`；未判柱判据改 `is None or != !=`（NaN 也披露）。
   三钉＝`test_panel_route_ic_ir_is_actually_computed`／`test_panel_route_high_icir_floor_now_fails_instead_of_passing`／
   `test_unjudged_discloses_nan_ic_ir_face`；双向实测闭合：dev 字节 3 failed／修后 41 passed，
   换面 sha256 前后各核一次（`RESTORE sha_equal=True`）。

## 9.4 本班队列账与一处要交维护班的机制观察

入队四件、实际两袋：`q-20261012-st-examrun-20261012-0001`（files=3：calibration_exam.py＋本班 00_ledger.md＋
测试件最新字节）与 `-0002`（测试件**旧**字节，系前一袋遗留）。两次入队各打出
`[compaction] 共享注册表路径不可信合并——拒绝压缩，两袋保留`，随后 C1 短窗合批把新袋并进 0001。
⇒ 风险面＝若 0001 先落地、0002 后落地，测试件会被旧字节回退。
处置＝**让 0002 死，不 requeue**（在册处方：在途字节因车道自己后落地会变回退弹）；
晨间终态判据（唯一可信）：`git show dev:tests/backtest/test_calibration_exam.py | grep -c test_panel_route_ic_ir_is_actually_computed` = 1。
本班投前已按在册工法跑预检（`WORKTREE-REQUIRED` 与 `COMMIT-SCOPE` 各一次被预检在锁外拦下、零死信，
改形后过：车道 cwd＋主区脚本＝同一台队列根，禁影子根）。
合跑证据（车道内，`PYTHONNOUSERSITE=1`＋车道 src 前置，实测 `ce.__file__` 落车道防导主区包）：
`tests/backtest/test_card_binding.py + test_arm_protocol_binding.py + tests/backtest/fexam + test_calibration_exam.py`
＝**171 passed in 15.42s**（零连带红）。

袋内字节 vs 车道现字节逐袋核（03:5x 实测，尺＝`pending/<qid>.json` 的 `files[].blob_sha256`
比 `sha256(车道文件字节)`；注：字段名是 `blob_sha256`，拿 `sha256`/`content_sha256` 去取会取到空串＝又一把假红尺）：

| 袋 | 件 | 袋内 sha | 车道 sha | 判定 |
|---|---|---|---|---|
| q-0001（吸收 0003/0004/0005） | `calibration_exam.py` | `f54bb4e24d3d` | `f54bb4e24d3d` | 同＝落地即终态 |
| q-0001 | `tests/backtest/test_calibration_exam.py` | `7d81d903652e` | `7d81d903652e` | 同 |
| q-0001 | `examrun_campaign_20261012/00_ledger.md` | `90f7d584591e` | `9d69d3ea17c1` | **袋内是旧版**（§9–§14 尚未随袋）⇒ 本班以最后一袋收口，落地判据只认 `git show dev:` |
| q-0002（depends_on q-0001） | `tests/backtest/test_calibration_exam.py` | `5dd04be0b085` | `7d81d903652e` | **袋内是补钉前的旧字节**＝若它后于 q-0001 落地会把测试件回退 |

q-0002 处置＝**不动它、不 requeue、不手删队列项**（在册处方：在途旧字节袋会因自车道后落地变回退弹，
让它按判据自然死；删队列项属不可逆面，本班不自作）。防线＝晨间用 `morning_watch.py` 的
`my_landing_dev_bytes.panel_route_pin` 核 dev 现字节里有没有 `test_panel_route_ic_ir_is_actually_computed`，
一旦为 false＝本班立即用新车道字节重投一袋（这是可逆补救，不是掩盖）。



## 9.5 本班尺的三次自纠（全部留旧读数不删，方向写明）

1. **少记口径**：§0/§4 手算"20 条＝53%"→ 用尺后 **21 条＝55.3%**（见 §9.1）。
   手算漏了 dev 在册那条测试泄漏形；尺的判据逐字写在件头，可复算。
2. **目标面严正则＝坏尺**：本班另跑一把 `次日(指数|沪深300|000300)收益` 强正则，得"0 候选"。
   正对照一跑就露：13 张**确已按指数次日收益出分**的在册卡，强正则命中 **0/13**
   （卡面真形是 `kline_index symbol='000300' close → next_day_return`／`next_day_index_return（CSI300 次日收益）`）。
   ⇒ 那个 0 是**假红**（尺失效），不得当结论；本班随即弃用自造尺，改回在册分类器的面
   （`card_binding --mode classify` 的 `target_face_not_index_next_day` 判定）当唯一尺。
   教训升级入册：**任何"0 命中"的尺，先拿已知可命中件跑正对照**，与"恒绿尺"同罪。
3. **路径形错位**：普查件里 `path` 字段是 Windows 反斜杠相对路径（`docs\03_modules\…`），
   直接喂 `git show dev:` 返回非零 ⇒ 那一列 route/bucket 全空是**读数失败**不是"卡没分桶"。
   该列未被用于任何结论；结论只建立在三处：classify 普查（在册尺）、绑定册穷举＋六判定件逐条行号、
   以及本班亲读的 4 张最近门卡面原文（§1/§2 的行号引用）。

## 9.6 最近门 11 张的在册判定面（用判定件字符串命中，逐条可 grep）

| card_id | 是否被判死册点名 | 点名件 |
|---|---|---|
| L2-01-2/calibration/02 板块成交额占比活跃度 | 是 | `17_:16-17,27-28`（reject_pending_new_version，须新版本卡） |
| L2-01-3/calibration/02 多周期动量主导度 | 是 | `17_:30-32`（两级分桶现器无面） |
| L2-01/comparison/02 等权与IC加权双臂 | 是 | `17_:69-73`（needs_engine→WO-A1；红线⑤双臂面本班不碰） |
| L2-01/comparison/03 缺路处置律重归一与剔除双臂 | 是 | 同上 |
| L2-02-2/calibration/02 板块见顶预警三信号 | 是 | `17_:35-36`＋绑定册 `:151 status: rejected`（禁改回 approved）＋`27_:48` |
| L2-04-1/calibration/02 轮动五态调节分 | 是 | `17_:39`（9 格 5 态名，态生成规则未冻＝进名单即替卡拍数） |
| L2-09/calibration/03 评级上调聚集 | 是 | `11_:210 reject`＋`17_:44-45`＋`27_:57`（五支新版本卡族，`can_freeze_in_window: 否` :62）＋`30_:70` |
| L2/ablation/02 板块候选池整体边际 | 是 | `17_:74+`（needs_engine→WO-A1） |
| L9-A10/calibration/02 全球风险因子隔夜传导 | 判定件未点名，本班读卡面判死 | 卡面 `:32-33` PIT vintage 门柱 vs 绑定面只有 macro_data 现值＝口径互斥（闸一）；`:8` 五因子各单跑 vs 一格一序列（闸二） |
| L9-A15/calibration/02 资金费率拥挤跨市场预警 | 同上 | 卡面 `:56` `resid_ic_min` 在 series 路词表外 ⇒ `judge():487-493` fail-closed（闸二，考了只得假 fail） |
| L9-A15/calibration/03 币圈镜像资金费率对BTC | 同上 | 卡面 `:61-62` target=`crypto_kline_daily BTCUSDT`；执行器 `:955` 无条件注 CSI300＝答错题（闸一，且 §1 的 fail-open 正在此爆） |

⇒ **11 张最近门 11 张全有在册或卡面级拒因，无一可绑可考**；§2 的"现器可考＝0"由第四把独立尺再次确认。

# 十、04:00 后追记（窗毕实测＋终态数，随填）

- 04:0x 复测 dev 面：见 §10.1（挖矿/矿考两班是否落新卡与新绑定；本班分母只认 dev 现字节）。
- 04:0x 让路面复核：`tilib_indicator_backfill_nightly` 02:5x 实测仍 `state=Running`（267009＝运行中），
  与 10-11 那夜"Disabled 无对象"不同 ⇒ **今晚窗有真对象，本班 01:00–04:00 零 CH 照守，未用 override 旗**。
- 开考与入账：见 §10.4。
- GPU 解锁复核：见 §10.5。

## 10.1 03:0x 机器水位报警（影响全班夜间施工，非本班起因）

`python -m zephyr.trading.process_reaper --status` 03:0x 实测原文：
`degraded=True`、`commit_pct=94.89`（开班 01:40 为 70.09→87.68，一路恶化）、`ram_used_pct=73.3`、
`cpu_pct=87.9`、`breached=['ALERT-SYS-001','ALERT-SYS-003']`、`worktree_changes=845>50`。
在册事故形态：提交内存耗尽时崩在 `git add`（0xC0000142）。
⇒ 本班处置＝**不加新袋、不造并发、不开自造并行批**（已入队四件合批成两袋，等 daemon 自举）；
本班晨间复核会把该读数再取一次。若 Owner 见此数，优先处置面在维护班而非考试班。

## 10.2 解锁地图→工单报价（给 Owner 的决策面，尺全部在册）

未考 177 张按"解它要什么"归成三条通道（前役尺=`01_binding_census.yaml:4-11` 的 tally 与
`target_face_kind` 分布；本班尺=§2 的 classify 复跑，两次相隔一日、卡数 184→177 的差＝已考与改判）：

| 通道 | 现器缺什么 | 解开的卡数 | 谁的地盘 | 本班判读 |
|---|---|---|---|---|
| **面板形绑定通道** | OPS 11 格全回 `tuple[pd.Series, dict]`，而 `_panel_metrics` 要两张宽表（§9.3-A 实测 AttributeError） | **最多 39**＝`panel_stock 22`（目标面=个股面板）＋`signal_kind=panel` 的 B 类 17 | 绑定层（考试班/矿考班共域，现无人claim） | **性价比最高的一条**：不碰撮合引擎、不碰判官，只加"面板取数＋面板目标"两种形；且必须与 §9.3-B 的 ICIR 面同批修，否则每台面板卡发假 PASS |
| 逐卡目标面通道 | `card_binding.py:955` 无条件注 CSI300，缺"引句所讲那条序列"的同一性断言 | `engine_replay 63`＋`other 27`＋`sector_series 3`＋`probability_hit 3`＝118（其中 engine_replay 与双臂重叠 30 支归 WO-A1） | 矿考二班在飞（袋 0080/0081 的 ArmBase/require_target_identity 正是此闸） | 等其落地后本班逐张开绑；本班不抢改共享件 |
| 卡面供给（题面本身） | 186 张 empty＝骨架无题面；28 张 U 无 `data_binding` 节；15 张 U 需复合配方 | 上限＝新供题数（186 骨架是矿面） | 挖矿班（卡面＝判据立法面，红线禁本班代拍） | 本班按 P2 只读接考；03:0x 实测矿考二班车道与 dev 卡册/绑定册**零差异**＝暂无新供题在途 |

另两条硬闸（不解锁就只能出假分，任何放量前必看）：词表外键 84 张（§9.2，`judge():487-493` fail-closed）
与分桶无面 130 张（`_n_buckets_from_card` 只认 quintile/decile/tercile/quantile_4）。

## 10.3 本班对"N 千题"北极星的诚实答复（实测分母，非态度）

- 卡册全量 495，未考 177，其中现器可考 0；
- 另一套在册题池（原问题 283 问）`exam_result` 已有 340 行＝无未考 backlog，且其试次不进 N 账本；
- 因子/策略/指标全量考池（175＋161＋143＋5）前役已跑：175 与 161 **全部 rework**（册面无量化 outputs，
  凭据=`docs/_working/matrix_campaign/90_execution_log.md:43-44`），不是可考面。
⇒ 今晚的题池上限就是"未考卡数"，而它被三条通道闸住（§10.2）。要"千题"须先要"千张卡"＝挖矿班供题面，
或先落"面板形绑定通道"（一条通道解 39 张）。本班今夜不靠降阈、不靠重判、不靠假绑来凑数。

## 10.4 开考与入账（04:02 实测）

- **开考＝0 张；分数行新增＝0；绑定格新增＝0；试次入账＝0**（不是漏考，是 §2/§9.6 的可考面实测为空）。
- dev 面 04:02 复测与 01:4x 首测**逐项相同**（`morning_watch.py` 读数）：卡 495／prereg 177／examined 31／
  blocked_impl 39／blocked_data 62／empty 186；绑定册 13 approved＋1 rejected；分数册 44 行／31 卡／pass 0。
  ⇒ 本班期间挖矿与矿考两班**未向 dev 落任何新卡或新绑定格**（附录那 8 条 ablation 卡亦未起草，见 §15）。
- 入账核验尺同批复跑：`ledger_reconcile`＝expected 38／dev 记录 29／missing 21（55.3%）／unlanded 20／
  主区含 6 条测试泄漏形——本班零开考故零新增，缺口面未被本班扩大，也未被本班修补（补账属 §5 P-1 待裁）。

## 10.5 GPU 解锁复核（04:02 再取，读数**较 §3 有更新**）

- 新事实：GPU 化二班车道件 `.worktrees/st-gpux2-20261011/docs/_working/gpufeed_campaign/03_gpux_final_report.md`
  已出现 **§十一·B 呈批四数（n=1,050 实抽 1,049 格，03:21 完成，据 `b2_bt_floor_n1050.json`）**：
  (a) 修列序后同进程 CPU 两跑 **1,049/1,049 逐位等，三档越线各 0 ⇒ p₀≡0**；
  (b) 设备面 A↔B：1e-8 档 11 格／1e-6 档 10 格／**1e-4 档 9 格（0.858%）**，对 p₀=0 的 z=3.33/3.17/3.01，
  双侧 p＝8.8e-4/1.5e-3/2.6e-3；差幅直方 `==0:489`、`(0,1e-16]:544`、`(1e-4,∞]:9`；
  (d) 三批入参逐字相同、`d_inputs_identical=True`。
- **但解锁两条件仍判不成立**，理由两条实测：
  ①**未出品到在册面**——dev 与主区的 03 件里查无 §十一·B（04:02 grep 零命中），条款说的是"03 件重判表出品"；
  ②**§二·丙 口径未"生效"**——该重判自己的结论是"判未过待裁"（9 格 >1e-4 离散放大未过等价线），
  且 p₀≡0 使"对自噪底做双比例检验"退化，要改的句子是"自噪底=0，容差只量设备侧合法分歧"——
  这在册上属**预登记倾向而非正式裁定**。
- ⇒ 本班**继续全程 CPU**，不开 GPU 通道、不在互斥组挂号、不动 `config/resource_profile_registry.yaml`
  （该册是生成器件且改它要先量存量 `sched_mem_ceiling` block，见 §3 末段）。
- 切换触发器（留给接班/晨间）：dev 面 03 件出现 §十一·B **且** 统筹/Owner 对那 9 格给出"过/不过"裁定 ⇒
  本班先量存量 block、再挂 `gpu_default` 互斥组、再切；两步缺一不切。


# 十一、"首张 PASS 在哪"的实测答复（03:4x，晨间包 P3 项）

**494 卡册＝0 张 PASS**（dev 面 44 行全 fail，`morning_watch.py` 的 `scores_dev.pass=0` 复核）。
但相邻那本在册考尺里已经有 PASS，本班替 Owner 把它的判据面读了一遍再报（**本班未据以改判一手**）：

`docs/_working/fexam/indicator_exam_scores_v1.yaml`（`generated_at_utc=2026-10-05 20:01:42Z`）
counts：total 143／**pass 78**／rework 55／retire_candidate 10。逐条复算这 78 张 pass：

| 判据面实测 | 读数 |
|---|---|
| pass 线原文（`prereg_v1.indicator_pass_line`） | `{abs_ic_5d_min: 0.02, regime_check: report_only, note: IC及格线同因子；regime_valid声明核对只报告不判死}` |
| 同册因子线自述 | `factor_pass_line.note = 初拟待Owner校（施工单§2口径）` |
| pass 行里 holdout `ic_5d` **为负**的 | **75/78**（判据取 \|IC\|，负 IC 同样算过线） |
| pass 行里 `direction` 未声明（None/空） | **78/78** |
| pass 行里 \|icir\|<0.3 或无值 | 47/78（该册 indicator 线未含 icir 闸；因子线才有 0.3） |

⇒ 答复＝**在册另一本尺已发 78 张"pass"，但它的线是"初拟待 Owner 校"的绝对值线，不看方向、不看 ICIR、
regime 只报告不判死**；按 Owner 令卡 P3 的"PASS 的价值在于它是真的"，本班不把这 78 张当首张 PASS 上报，
也不重判它们（重判历史＝改判据，§0 铁律）。要不要认这本的线、要不要补 direction 注解后另起新卡重考，
属 Owner 门位——本班列为 §5 P-7（新增）。同族在册线索：`docs/_working/fexam/codesym_factor_exam_v1.md:62`
（MOM-029 因 registry 未声明 direction 判 rework，"若登记 direction=short 则 ICIR=+0.31 恰过线"）。


另：挖矿班 03:2x 落 dev 的元方法调研（`6578afb599`，件=`docs/_working/2026-10-12-exam-card-mining-meta-method-research.md`）
通篇是轴清单与三本账，**未含新的 pass 线数值**；dev 面带数值的缺省线仍只有 roster 册那句"初拟待Owner校"
（`scripts/backtest/fexam/roster.py` PREREG_V1）。⇒ 令卡 P0 所说"新卡按挖矿班 SOP 新阈值考"，
本班实测到的落地形态只有一种是机判可执行的＝**逐卡读该卡 `pillars_numeric`（卡面即阈值）**；
若 Owner 所指是另一套统一新阈值，请点名件与数值，本班不猜（猜＝替卡拍数）。

# 十二、首张 PASS 上报时必须随件的一句（P3 看守细则，本班实测）

现器两条路都**没有 IC_IR 面**，所以任何卡出 pass 只代表 4/5 柱：

| 路 | ic_ir 现值 | 是否披露 | 证据 |
|---|---|---|---|
| series（现网 44 行全走这条） | 恒 `None`（`_series_metrics:182` 硬置，现器无 IC_IR 面） | **披露**：`_unjudged_pillars:292-293` 的 None 支覆盖它，进 `numeric_keys_no_machine_face` | 实测 dev 分数册 21/44 行带 `unjudged` 面（10-11 批复②步骤①后落），其中 4 行点名 `ic_ir_min` |
| panel | 因键位错恒 `NaN`（§9.3-B） | **改前不披露**（只查 `is None`）⇒ 本班已修＋已钉 | 实测 `verdict=pass fails=[]` 而 unjudged 面无 ic_ir_min |

⇒ 晨间包若出现 PASS，必附"该卡冻了哪几柱、实评几柱、ic_ir 是否在册无面"；
`ic_ir_min` 在卡面冻着而未评＝**在册声明的机判面缺口**（词表立法工单对象，§5 P-4），不是本班可补的数。
另注：10-11 之前的 23 行分数无 `unjudged` 字段（观测面当晚才上线），引用那些行时须同时说明这一层。

# 十三、三条"可能有增量考面"的猜想全部实测关闭（供接班勿重复挖）

| 猜想 | 实测尺 | 读数 | 判定 |
|---|---|---|---|
| 卡册外另有一批 preregistered 卡可考 | `git grep -l "^status: preregistered" dev -- "docs/**/*.yaml"` 去 exam_cards | **0 件** | 关闭：未考面全在 495 件册内（§2 的分母即全集） |
| 已出分行里还有"卡面五分位而实算十桶"的未补正卡（同 09 号在册依据可合法重跑） | 逐行比 `metrics.n_buckets_used` vs 卡面 `buckets.type` | 44 行中 **15 行带该字段，值分布 {5,10}，与卡面冻结型全对＝0 处不符**；余 **29 行无该字段（不可核，不得称"已对齐"）** | 关闭：无可合法重跑的存量错位行；29 旧行要补核＝复考＝重判（§0 铁律禁） |
| 39 张 blocked_on_impl 里有"阻塞因已被 10-11 落地解决"的 | 逐卡读 blocked 因文本＋比现器路由/算子册（含新落的 event 路与五分位修复） | 其中 **2 张**形制接近可用（`L2-09/calibration/06_catalyst_density_high_event_v2`＝缺"行业×日研报发布量"基序列算子；`L9-E2/ablation/02`＝需逐日产物面）；两张的算子落点都在 `card_binding.py`（矿考二班在飞件） | 关闭（今夜）：非"因已解"，是"解它的刀在别人手上"；本班不抢改共享件（红线⑤⑥、宪法 §3.4） |

# 十四、"测试写生产册"是同族病不是孤例（并档证据，供统筹判是否立通用闸）

本班 §4-1 抓到的是 `tests/backtest/test_calibration_exam.py` 经 `run_card` 缺省路径写生产 N 账本；
同一夜另一道班（在册记忆 `pg-ledger-rows-need-retire-on-path-abandon-20261012`，10-12）实测抓到
**同族两处**：跑 `tests/gov/governance/test_commit_queue_landing.py` 与 `test_derived_books_parity.py`
也会写生产册（#ARCH-084 守护**只在 teardown warn**，`ZEPHYR_TEST_STRICT=1` 才硬失败），
并且 PG 账本里已积 7 条 active 幽灵行（created_by 全是 CLI 缺省归因名 `add_module_translation`＝测试经真 CLI 落的生产账本）。
⇒ 三处同族形态都是**"测试的写口没有被机械禁止，只在事后 warn"**；
本班的修法是"给写口开注入位＋autouse 夹具改指 tmp＋两颗能红的钉"，与前役 §5-L06 的
"契约类缺陷要问这条约束在哪一层被强制，在审计层的等于没有；修法是写口 fail-closed"完全同型。
是否升成一道通用门（staged/运行期检测测试进程写生产册即硬失败）＝治理资产净增面，
须按 §4 全资产净零声明替代对象，本班不自建，列此供统筹判。

# 十五、令 B 附录收令（注册册 ablation 执行＝普查⑤）——03:2x 落位实测

- 令据＝Owner 03:1x 附录：挖矿班起草的 **8 条注册策略 ablation 分解卡**到位即接考（逐腿拆：恐慌反弹腿／质量门等）；
  **卡面判据数值须先呈统筹批**，批后才开考；CH 面按窗纪律。
- 锚位实测：普查⑤原文＝`docs/_working/2026-10-12-exam-card-mining-meta-method-research.md:197`
  「注册册 8 策略 ablation 分解卡（哪条腿在贡献——ablation 卡型现成）」；
  同件 :172 把「注册册 8 条」与「引擎层 8 个 strategy_id」**分列**（两个不同的 8，接考时勿混）。
- **卡的落位状态＝尚未起草**（03:2x 实测三路）：`git ls-tree dev -- …/exam_cards` 零新增 ablation 卡；
  全盘近 3 小时新件里无该族卡文件；挖矿道今晚在盘的只两件＝
  `2026-10-12-exam-card-mining-meta-method-research.md`（已落 dev，`6578afb599`）＋
  `2026-10-12-d-family-qualification-freeze-draft.md`（`st-minedig-20261012` 的呈批稿，
  工作区状态 `A`、**未落 dev**，status: draft_for_ruling＝只起草呈批不开考，与本附录同纪律）。
- 本班预备（零 CH，接到卡即可跑的三件事已就位）：
  1. 取数与判据面预检尺＝`morning_watch.py`（一条命令给卡册/绑定册/分数册/GPU/窗况/账本六面）；
  2. 入账核验尺＝`reconcile_ledger_vs_scores.py`（判据＝`examcard:<card>:<date>` 必须在账本，§9.1）；
  3. ablation 族的现器可用性预判（据本班 §9.3 实测）：**ablation 卡若是"逐腿拆＋比臂间差"形，
     就走双臂/面板形**——绑定层现器只能交单序列（实测 `AttributeError: 'Series' object has no attribute 'columns'`），
     而逐腿对照需要每腿一条序列；**且 ICIR 柱在 panel 路曾因键位错恒 NaN**（本班已修，落地后生效）。
     ⇒ 请挖矿班在卡面 data_binding 里把每条腿写成**可单序列取数**的形（或等面板通道落地），
     否则 8 张卡到手仍一张也考不出（这不是本班能绕的，绕＝假分）。
- 策略侧腿的可考性预告（供挖矿班起草时避坑，本班只报实测面）：
  `strategy_registry.yaml` 里 `STR-E-TIMING-001 恐慌反弹分布预测` 等 active 条目的腿面字段只有
  `alpha_sources` 一列可机读；"质量门/风控门"这类腿若指向**逐日产物未落库**的面，
  则按本班 §13 同型结论＝出生即 `blocked_on_impl`（先立卡冻判据、算子后补），
  与 10-11 那批"高事件 v2 卡"的在册处置一致。
- 本班不自拍判据：卡面数值到手后**先呈统筹批**（附录原文），批文到位前零开考、零绑定。

# 十六、04:02 窗况与落地链读数（两条"到点不等于可干"的实测）

1. **让路窗到点，但对象仍在跑**：`tilib_indicator_backfill_nightly` 04:02 实测
   `LastRunTime=2026/10/12 2:30:01`、`LastTaskResult=267009`（在册口径 267009＝运行中）＝已跑 92 分钟未结束。
   ⇒ 本班处置＝**继续零 CH**，不用 `--override-ch-window-with-reason` 硬闯（那条旗的合法用法是"窗内无对象"，
   现在是"窗内有对象且跨窗"，正好相反）。这是在册工法"窗口须验对象"的**反向半边**：
   窗未到点而有对象也应让（前役已立），窗到点而对象未撤同样要让——判据是对象，不是钟面。
   本班全程 CH 实跑 0 次；`172.24.30.100:8123/9000` 仅 TCP 连通性探过（非查询）。
2. **机器提交内存近满，落地链随时可能崩**：04:02 reaper 自报
   `commit_pct=99.94`（开班 01:40 为 87.68，一路恶化）、`degraded=True`、`breached=['ALERT-SYS-003']`、
   `worktree_changes=834>50`；队列 04:02 现值 `pending 56 / processing 1 / done 750 / dead 1460`，
   本班两袋（`q-…-0001` 三件合批／`q-…-0002` 旧测试字节）**均在 pending、无一进 dead**。
   ⇒ 本班据此**不加并发、不追投多袋**（在册事故形态：提交内存耗尽崩在 `git add`，0xC0000142）；
   收口只投一袋（本件终态），并把"本班交付是否已落 dev"的判据写成可复核命令而非等待通知：
   `git show dev:docs/_working/examrun_campaign_20261012/00_ledger.md`（空＝未落，按 §9.4 补救路径重投一袋）。

# 十七、04:07–06:50 值守时间线与两起本班险情（如实报，含本班自犯）

值守器＝`.runtime/tmp/st-examrun-20261012/intake_watch.py`（每 20 分钟一轮，只读，零 CH；
启用前先跑正对照＝基线四项与 §2 首测逐字相同才可信）。逐轮实测：

| 时刻 | dev 供题面四项 | 本班三袋是否落 dev | tilib | 队列 |
|---|---|---|---|---|
| 04:06 基线 | 卡 495／prereg 177／绑定 approved 13／分数 44 行 pass 0 | 未落 | Running | pending 63 |
| 04:26→06:50 共 8 轮 | **delta 全空**（四项一字未变） | 三袋全 false | **全程 Running**（rc=267009） | pending 58–63／done 751→766 |

⇒ 三条结论：①挖矿/矿考两班 04:07–06:50 **未向 dev 落任何新卡或新绑定格**，附录点名的 8 条 ablation 卡
亦未起草 ⇒ 本班"接考"整夜无对象，不是值守不力；②让路对象（tilib 指标回填）**跨窗跑到 4 小时 20 分仍未收**
⇒ 本班全程零 CH 被持续验证（若按钟面 04:00 放量，正好撞在 bulk 写窗上）；③队列在他班侧持续消化
（15 笔落地），**本班三袋全程 pending、零 dead**＝不是死信而是"不被处理"。

**险情一＝本班袋不被消化（现象实测，归因在他域，本班不越）**
- 现值：`q-…-0001`（02:39，三件）／`q-…-0002`（02:39，旧测试字节，depends_on 0001）／`q-…-0006`（04:05，班账终态）；
  meta 面 priority=0、branch=dev、base_head 齐、worktree_root 正确，`dead/` 零命中 ⇒ 无 dead_reason 可依，
  `requeue` 不适用（它治 dead 项）。
- 本班自查到的**相关性**（明说不是结论）：06:52 实测心跳守护 PID 36620＝`HB_DEAD`，
  且 `list_active()` 18 个活动会话里**无本班**；在册形态＝活性锚失效（idle>1800s 自退）会使队列侧把件
  判成 ghost/held。时间线吻合：本班最后工位段在 03:0x，daemon 约 03:3x 自退，04:05 投的 0006 同样未消化。
- 本班已做（均可逆，未碰队列内部）：①重注册 `SessionRegistry.register(sid, pid=0)`＋重启心跳 daemon
  （新 PID 57752，实测在 active、心跳新鲜）；②**保全三件＋patch**
  ＝`.runtime/tmp/st-examrun-20261012/safety_r1/`：manifest 记 `f54bb4e24d3d…`（执行器）／
  `7d81d903652e…`（测试件）／`6ecee75f077b…`（本账）＋`lane_staged_vs_dev.patch` 63,593 字节。
  06:5x 复核：车道本文件 563 行、sha 与 manifest **逐字一致**＝即便车道被 sweep 或袋被 purge，成果另有自存面。
- 队列治理权在维护班域（宪法 §2.6）：本班不动 serializer、不删他项、不 force 落地。
  交接复核命令＝`git show dev:docs/_working/examrun_campaign_20261012/00_ledger.md`
  ＋`git show dev:tests/backtest/test_calibration_exam.py | grep -c test_panel_route_ic_ir_is_actually_computed`
  （应得 1）；取空则按 safety_r1 逐件重投（袋前自证已写：净增、删除行为零）。

**险情二＝本班自犯：claim 传相对路径＝幻影 claim**
- 02:0x 本班在主区根执行 `lock_files.py acquire scripts/backtest/fexam/calibration_exam.py <sid>`，
  而施工在车道——两侧归一根不同 ⇒ claim 实际零生效且**无告警**（在册新记形态
  `lane-claim-relative-path-silently-zero`）；本班看 `lock_files.py list` 有条目就误判已 claim。
- 今夜未酿撞车的**实测依据**（非运气）：`git log dev --since="2026-10-11 20:00" -- <两件>` 零命中
  ＋动手前 `git diff dev --stat -- <两件>` 为空 ⇒ dev 现字节无人碰；本班又按 `git show dev:` 取基线、
  袋前逐行点名删除行（6 行全是自替换），故未覆写他人面。
- 工法入册：**车道内 claim 一律传车道绝对路径**，并当场核对 `list` 里持有者名下路径根＝车道；
  与"三件定窗""0 命中尺要先跑正对照"并列为本班三条工法。

## 17·补 07:23 活性锚对照＝假说被证伪；真实现象是全池停摆（旧 §17 留文不删）

对照实验（会话重注册为 active 之后，25 分钟内每 5 分钟一测）：`session_active=True` 六次全真，
而本班四袋 `mine_pending=4 / mine_dead=0` 一字未变，同期队列 `done 767→770`（他班 3 笔落地）。
⇒ **"活性锚失效"不是本班袋不被处理的充分因**；§17 里"时间线吻合"那条相关性到此降级为
"未成立的相关性"（原文保留不删，供周审计看我怎么错）。

整池读数（07:2x 逐件解析 `pending/q-*.json`）：
- pending **59 笔**，分属≥10 会话：maint3 12／deadcure3b 11／gpuwo 10／gpux2 7／**examrun 4**／
  cband 4／minedig 3／fclean3 3／backfix3 3／mineloop2 1。
- **最旧一笔 01:56:40（st-gpux2）＝已滞留 5h26m**；本班 02:39 两笔排第 11、12 位
  ⇒ "老的排队、新到的先落"是全池共性，不是本班独有病。
- 消化速率实测：25 分钟 3 笔 ≈ **7.2 笔/小时** ⇒ 清完现池约需 8 小时，而入队与落地近乎相抵
  （20 分钟内 pending 在 59↔63 摆动）。
- 最可能的束缚条件（本机读数，**不作归因定论**）：04:02 reaper 自报 `commit_pct=99.94 / degraded=True`
  ＋`worktree_changes≈834`；serializer 每袋要跑 git 三路合并，页面文件近满时 git 侧整体变慢
  （在册事故形态＝崩在 `git add`，0xC0000142）。
  ⇒ 该面属落地链/机器面，治理权在维护班域：**本班不动 serializer、不 force 落地、不删他项**，
  只交读数与复核命令；若 Owner 要本班"代为催一件事"，正门是 `commit_queue.py health`＋向维护三班会知，
  不是自己抢落地。

本班交付的存活面（三处，任一被抹另有两处在）：①队列 blob（4 袋，`blob_sha256` 已逐件核＝车道字节）；
②车道工作树＋index（已 `git add`）；③`safety_r1/` 三件＋`manifest.sha256.json`
＋`lane_staged_vs_dev.patch`（63,593B）＋`lane_ledger_vs_dev.patch`（52,877B）。
复核仍只认 dev 字节（§17 末两条命令）。

# 十八、统筹晨裁 ⑤ 收令与执行边界（考试班＝消费侧）

- ① 面板形绑定通道＝排产矿考域（与 CW-MINELOOP-001 横截面回放面同一件工程，一次建两面用）；**本班＝消费侧**。
  "ICIR 假 pass 修复合批"约束照持（本体袋 q-…-0011 未落地，见 §20）⇒ 矿考域若先把面板通道落地，
  面板卡的 `ic_ir_min` 会**恒 NaN 且改前不披露**＝每台发假绿。本班已备好两面：
  修体（读回 `ic_stats` 真键 `icir`）＋披露闸（None 或 NaN 都进未判柱清单）＋三支能红钉。
- ② N 账本补账 15 条＝批，但前置两修（`mass_edit_guard` 预算→维护三班；`exploration/record_run` 的 elif 互斥→矿考域执行器）；
  修好后剔 5 条测试泄漏形再按正集纪律补。本班尺＝`reconcile_ledger_vs_scores.py` 可直接复算 38/29/21/20/5 这套数。
  本班不代补、不代投他班未落地条目（红线②＋在册归属篡改处方）。
- ③ 相邻指标册 78 张＝**不认 pass**，按"未裁读数"作反向分诊候选族处理；挖矿道已机生分诊
  （`docs/_working/fexam/batch3_reverse_triage_v1.yaml`：A20／cap溢55／正方向3）＋立 20 张卡。
- 本班照实记录：**零开考、零绑定**；池排空前不开新考批，只做读数与接考准备。

# 十九、接考预备读数（读队列 blob 预判，零 CH，不改他班任何件）

挖矿道 q-…-0002 袋内 20 张反向卡（`TDM-E-L1-S2/calibration/17..36_*_high_event`）本班逐张过在册尺：
**20/20 现为 `status: blocked_on_impl`、`signal_kind: series`、路由=event、`buckets.type=event_flag_two_state_contrast`、
`classify_card` 判 U（表列零命中＝卡面无 data_binding 取数面）、20/20 带"一轮为限"**。
⇒ **本班今天即使拿到这 20 张，可考数仍是 0**：缺的不是运行时间，是"指标列→事件开关基序列"这条绑定算子
（现器 `event_flag_rolling_pctile` 需 base_op/base_csv 二选一，而指标列→日频基序列无在册算子）。
尺与清单＝`.runtime/tmp/st-examrun-20261012/preassess_minedig_q0002.json`（`preassess_queued_cards.py` 生成，
先跑正对照：基线四项与 dev 面一致才启用）。

# 二十、dev 考尺红约 9 小时（本班致因链与唯一堵点，升级处置）

**现象（实测，非推断）**：`dev:tests/backtest/test_calibration_exam.py` 要求 `run_card` 有注入位，
而 `dev:.../calibration_exam.py` 里 `ledger_registry_path` 命中数＝0 ⇒ 用 dev 面两文件在 tmp 合跑得
**1 failed, 37 passed**：`TypeError: run_card() got an unexpected keyword argument 'ledger_registry_path'`
（复现：把 dev 两件取到 tmp 后 pytest，命令＝`.runtime/tmp/st-examrun-20261012/devface_check/`）。

**致因链（三层，全在本班）**：
1. 本班把"本体＋测试＋班账"三件放进同一袋（省袋心切），而班账放在
   `docs/_working/examrun_campaign_20261012/`＝**数字后缀目录**，触 R5-DIGIT-SUFFIX（在册明令"_working 禁数字后缀"）
   ⇒ 袋 0001 死，**本体件被连坐带死**；
2. 配套测试件袋 0002 是独立袋，10:36 **自己落了 dev** ⇒ 本末倒置落地（试件先行、本体缺位）；
   本班当时给 0002 挂了 `depends_on 0001`，但**队列的依赖序没有挡住它落地**＝顺序保证不能只写在旗上；
3. 随后两次机器死机把本班会话判死（pid 亡），复员时又踩 TAKEOVER-PENDING 死循环：
   本班自己那条 open 接管条目未销账 ⇒ 0009/0010 连死；已按处方 `--resolve` 销账（held 释放＋心跳重启）。

**当前唯一堵点（不属本班域，须统筹/维护班处置）**：0011 袋死于
`TAKEOVER-PENDING：命中 open 接管条目——死会话 sid=st-mineloop-20261010（idle 31045s > 7200s）`，
命中文件正是 `scripts/backtest/fexam/calibration_exam.py`；该死会话车道
`.aidrafts/st-mineloop-20261010` **dirty=107 且这两件均为 `MM`（有未提交在途编辑）**。
⇒ 本班**不代处置他班车道、不 resolve 他班接管账**（那是把别人 107 件工作草率判为可弃，属 Owner/统筹门位）。

**请授权的一条命令**（任一即可解本班堵点）：
- 统筹/矿考班认领并处置该车道（merge 或 abort 后）：`python scripts/governance/session_takeover_ledger.py --resolve st-mineloop-20261010 --by <接管者> --note <处置结论>`
- 或授权本班按"只读比对后弃车道"处理：先出 dirty=107 的分件清单与对 dev 的净差账（本班可在 20 分钟内交），再凭该账 resolve。

**堵点解除后本班立即做**（已备好，一条命令）：重投本体袋 `scripts/backtest/fexam/calibration_exam.py`
（对 dev 现字节为基、删除 6 行逐条点名、落地前实测"dev 测试件＋本体＝38 passed"已做完），
随后补投含三支面板钉的测试件（41 passed 版）与班账终态袋（新路径 `docs/_working/examrun_campaign/`）。

**零面声明（本班全程）**：判据数值零动｜卡面阈值零动｜分数册零写｜卡面 status 零改｜GPU 面零碰｜
CH 查询 0 次（含死机后复员，全程零取数）｜N 账本真源零写｜他班件零改（只读其队列 blob 与车道 status）。

# 廿一、复员执行账（20:5x，统筹授权后的落地链，含两处根因留痕）

- **班账已落 dev**：commit `c74b75add8`（20:51，`[GW:]` 归属＝本班，单件 `docs/_working/examrun_campaign/00_ledger.md`，679 行）。
  落地判据只认 `git show dev:` ＋ `git log -1 --name-only` 核归属（在册两条工法，未靠任何通知）。
- **ghost_session 连死的真根因（不是"我还活着被误判"，是我的守护根本没在写心跳）**：
  `heartbeat.jsonl` 留痕原文＝`{"ts":"2026-10-12T11:02:16+00:00","pid":11852,"status":"started"}`
  紧跟 `{"...","status":"exited","reason":"session not in registry"}`——
  即在册记忆 `session-register-pid0-for-heartbeat-daemon` 那条形态的**我本班复现版**：
  我先 spawn 守护、后 register（顺序颠倒），守护启动即退，此后三次投袋全被存活闸判 ghost。
  修法＝先 `register(pid=0)` 再 spawn，并**以心跳日志新增 alive 行为验收**（不是"我以为起来了"）：
  新守护 pid 3488，40 秒后实测末行 `{"pid":3488,"status":"alive"}` ⇒ 之后 0017 一次落地。
- **TAKEOVER 自锁循环（转维护三班第 2 例同族）**：本班按统筹授权 resolve 掉 `st-mineloop-20261010`
  那条 open 条目后，`session_takeover_ledger --scan` 又以 `reason=orphan_resources`（车道在盘而注册表无此会话）
  **重开同一条**，命中面一字未变 ⇒ 只要该车道未被接棒人处置，任何班提交 `calibration_exam.py` 都会被拦一次。
  本班第二次 resolve 已在 note 里写明"同授权二次执行"，并登记：`resolve→scan 重开` 是机制病，
  处方应在扫描侧（已 resolved 且命中面未变者不重开，或重开需带新证据），归维护三班活性族簇。
- **本班 12 袋账**：done 2（0002 测试件 v1＝造成本末倒置的元凶、0017 班账）；
  dead 10（0001/0006/0007/0008 死因 R5 数字后缀路径，内容已迁合规路径；
  0009/0010/0011/0015 死因 TAKEOVER/自锁；0012/0016 死因 ghost_session）；
  0018＝本体袋在队；死袋一律不 requeue（R5 类改路径重投，TAKEOVER/ghost 类修因后重投），
  与复发熔断同向：本班**未用 --force 越闸**。
- 教训一条（写给我自己）：`gate_dry_run` 的"命中面自检"我第一版用 `hasattr(...)` 兜底，
  函数名不对即静默返回空集 ⇒ 判成"零拦截"，实际门里有 1 条。凡"自检尺"必须先证明它能红：
  本次改判据为"用门导出的 `entry_match_surface` 实算＋打印 blocking entries 数"，才看到真阻塞。
