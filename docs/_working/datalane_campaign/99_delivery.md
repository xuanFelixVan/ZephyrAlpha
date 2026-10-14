---
ttl: task_bound
title: 数据车道班 99_delivery（T1-T6 逐件交付与验收尺，sid=st-datalane-20261010）
session: st-datalane-20261010
completes_when: T2/T3/T4 收官回执被二号/后续班签收 + T1 次夜写入量对账完成
---

# 数据车道班 99_delivery（sid=st-datalane-20261010，2026-10-10）

> 开班令=总统统筹 2026-10-10；台账=00_ledger.md（全程滚动）；本件=收官账。
> 逐件哈希+复核命令见 §四；草稿期数字以台账最新段为准。

## 一、T1 退役指标停算（裁定#489①+#494②）——已落地+闭环补全

- **bebba60c**：`_fetch_single_period` 写链按 REG-IND-001 status 过滤（仅 active 进写链；
  位置勘误与红证 A/B 见台账 §一）。红证：摘消费点过滤⇒wiring 测试红；HEAD 未修码⇒4 例全红。
- **24fec802**：T1 闭环面——P1 值级比对排除退役列集。复盘发现的交互缺陷（不补则 P1 永不
  跳过、夜跑全史重灌不停、T2 被 nightly NULL 版本掩埋）与红证见台账 §一。
- 主区对平×2（验收窗=当日 02:30 夜跑读主区码；final4 先例）：provider 与 backfill 两文件
  对平后主区实测 30 passed。主区 provider 文件现携带 B2/B4-M2 在途 hunks+本班 hunks，
  归属吸收按 489777c60e 在案口径。
- 验收（次晨跑）：夜跑 state 存活+finished_at=当日+TI_VALUE_SKIP 面 skipped>0（P1 复效）；
  写入量对比基线=单趟 3.5-4M 行——**注：本值依赖比对基读可得（241 熔断在案），读不到
  基的窗口宁多写不少写（行为不变）**。

## 二、T2 squeeze/wad 定点重算——执行+冷档双证（回执待二号）

- 处方盘面更新（探针法证，台账 §二）：修复 1a9ab332f58（10-10 05:11）晚于 02:30 夜跑起跑
  ⇒ 窗内最新版=旧码×hfq×截断基（四象限对表差值恒 −748.5 实锤）；在飞多腿产物出处不可
  干净归属 ⇒ 按开班令本义走自算定点重写稳健路线。
- 冷库双证：F:/zephyr_cold/50_archive/by_project/zephyralpha/datalane_t2_premutation/
  （2,643,381 键×6 窄列，parquet 38.7MB+tsv.gz 48MB，sha256 双件入 manifest.json；
  parquet=057b54ff…，tsv.gz=2d442318…）。
- 定点重写（recalc_t2_squeeze_wad.py --apply）：窗 2024-10-08..2026-09-30 daily，
  **24 个月全 OK，月写入≈7.6万-12.7万行，重算键 2,643,220（与冷档差 161=0.006% 源缺键
  保原值）**；公式=HEAD 1.1.0、源=kline_daily_hfq、wad 基=源表首 bar（基约定申报变更，
  D7 §一.3）；覆盖表 c1_market.tmp_t2_override（Memory，跑完即 DROP 零残留）。
  首写后 4 键探针 2/4（两键被在飞夜跑旧码腿重写掩埋=预判机制实证）→ **15:45 夜跑 runner
  52 片收官后终态刷新重放 24 月全 OK → 终验探针 5/5 全对**（最新版=本地 HEAD 修复码重算
  值逐位≤1e-6，t2_refresh.log）。明晨 02:30 起 T1 闭环码守值（P1 跳过），T6 OPTIMIZE 后
  读数即收敛口径。
- 稳定性声明：写入后不可变性依赖 T1 闭环面（P1 跳过）在读得到比对基的窗口生效；若熔断
  窗口内夜跑仍全量插（ retired 列=NULL 版本），重跑本脚本即恢复（幂等 append）。
- 通知二号（R2-C 重考，归它不归本班）：读径=优先 T6 OPTIMIZE 后读宽表；PIT 稳定读=
  冷档 parquet。考试窗 UNION 2024-10-08..2026-09-30 冻结不变。

## 三、T3/T4/T6——脚本与方案就绪，执行排程如实申报

- **T3**：limit_up_down 2019-01-04..2026-07-19 推导回补脚本就绪
  （.runtime/tmp/st-datalane-20261010/backfill_limit_up_down_derived.py，口径=在册
  derived_stk_limit 先例+广度尺同源原语；验收=7 条广度序列×1622 交易日对拍
  02_breadth_derivation_report.yaml）。执行被在飞 bcure 全史重算链（.runtime/tmp/bcure/
  ti_shard_selfheal_driver，10-08 起月粒度爬坡）压住——禁双开红线让位，属主手工重查询
  亦 500 实证。**依赖申报：bcure 链收官后 dry-run→apply→对拍**。
- **T4**：断供链定位（hfq=根，TI=下游投影，周月=miniQMT 悬空旧基座）+五门小批验门方案
  =03_t4_cascade_gate_plan.md。执行同样排在 bcure 收官后（其 2026-10 月腿亦将重写
  当月 TI，T4 门 3 可被其覆盖性完成，届时只跑对拍）。
- **T6**：触发器监测——(a) CH 空闲窗窄窗读复测：**全天无空闲窗**（bcure 链+夜跑腿压着
  RSS 3.6~6.2GiB，窄 FINAL 读 241 两次实证、无 FINAL 窄读可通）；(b) T1 落地 ✅；
  (c) 比对基低内存通道=架构面呈报。⇒ 本班**未排 OPTIMIZE**（dexp 顺序铁律：bcure 重灌
  链在跑时收敛=白占 IO；且 23:00 W1 让位二号）。触发器(a)复测命令留档：
  `SELECT symbol,trade_date,wad FROM technical_indicator FINAL WHERE symbol='000001'
  AND trade_date='2025-06-06'`（安静窗 <60s 通过即触发）。

## 四、逐件哈希与复核命令

| 件 | 哈希/commit | 复核命令 |
|---|---|---|
| T1 计算腿停算 | bebba60c | `git show bebba60c --stat`；`PYTHONNOUSERSITE=1 python -m pytest tests/legacy_zephyr/data/test_internal_compute_provider.py -q` |
| T1 闭环面（P1 比对排除） | 24fec802 | `git show 24fec802 --stat`；`PYTHONNOUSERSITE=1 python -m pytest tests/data/data/data/test_ti_backfill_value_skip_and_shard_windows.py -q` |
| 战役文档三件 | 602edf00 | `git show 602edf00 --name-only` |
| T2 冷档 | manifest.json@F:/zephyr_cold/.../datalane_t2_premutation/ | `sha256sum F:/zephyr_cold/50_archive/by_project/zephyralpha/datalane_t2_premutation/*.parquet`（对照 manifest.parquet_sha256） |
| T2 重算脚本 | .runtime/tmp/st-datalane-20261010/recalc_t2_squeeze_wad.py | `python <脚本> --compute-only`（只读重演） |
| T5 快照器 day1 | data/emotion_index_snapshots/emotion_index_20261010T041044Z.jsonl.gz | sha256=8fbad68dc33c975ecd8a1230395c7068ab5f94b9b44f27d2658bea006731a240（manifest 对账） |
| keep 登记 | data/runtime/process_reaper_keep.txt 末段 | `grep -A1 st-datalane data/runtime/process_reaper_keep.txt` |

## 五、呈报（Owner/总统筹）

1. **bcure 全史重算链**（10-08 起，月粒度，2.2 天 5/93 月，内存闸 2.5GiB）：T3/T4/T6(a)
   全部被压。其属主车道与预期工期请统筹核——若判定其使命已被夜跑链+T1 闭环面取代，
   建议属主收官；若保留，本班 T3/T4 执行窗顺延至其收官。
2. **T1×P1 交互缺陷**（24fec802 治本）：呈报作为"计算腿过滤"类改动的通用教训——停算列
   必须同步退出值级比对面，否则跳过判据被 NULL 差异毒化。
3. **T5 钉任务**：day2/3 连跑由值守自动化执行（12:35），满 3 天自动钉
   ZephyrAlpha_EmotionIndexSnapshot+回执写台账；自动化人工撤除点=钉任务成功后。
4. **主区对平降级直改×2**：原因与范围见台账 §一/§七（GW 计数为准）。

---

## 六、本班终账（sid=st-datalane2-20261012，2026-10-12 22:0x → 10-13 23:3x）

> 本班＝数据合并回填工单三件＋统筹五裁/四裁/四令/收口令的执行班。全程滚动账在 `00_ledger.md` §十九~四十；本节只记**可复核的终态读数**与未闭面。

**一、交付与验收读数（全部 CH/PG/git 实测，非账面）**

| 件 | 终态读数 | 尺 |
|---|---|---|
| ① tilib 断点续跑 | 58 片/5,792 票按在册分片配方跑完，收工口径＝C 族邻域班复算触发条件达成 | 六车道 state 面按 (shard, symbols_sha256) 键对账（曾两次假绿，见 §廿七/册三） |
| ② 段一 basic 2019-2020 | **1,831,872 行 / 4,352 票** | `uniqExact((trade_date,symbol))`，非 count() |
| ③ 段二 basic 2017-2018 | **1,561,578 行 / 3,616 票**，rows==keys，487 交易日，全标 `tushare` | 同上 |
| ③ 段二 kline 2017-2018 | **1,657,332 行 / 3,580 票**；C1 覆盖 **3,580/3,592=0.9967 ≥0.95**；`rows≠keys` 日期 **0** | 分母＝stock_list 曾在市（含 1970-01-01 在市哨兵）；首算误得 254 已自纠 |
| 590 只零行票补齐 | 08:05 一次性任务：探针 3/3 通 → 放量 **ok=568 fail=0 zero=0**（13′36″）→ 复核仍未覆盖 0 | 三道机械闸＋已知正对照；任务已注销 |
| 市值表改标（裁③） | 存量：akshare 10-12 23:53 改标；增量存量再清：21:30 `ALTER_RUN` **11,122→0** | 逐行来源判据（四列全实＋日志 `integrator.tushare … 5561 行`） |
| 写侧四处随形改（Owner 亲裁） | dev 面 7 列 + 行末 `'tushare'`；主区 **132 passed** 复跑绿；重启后新子 9548 起于 21:32:47（晚于落地笔 16.2h） | 判据②（首笔新写显 tushare）**留明日 16:3x 那笔**，未签收 |
| 收版（已批第三步） | 202610 分区每键版本 2→**1**×5,561；四项业务列校验和与 max ingest_ts **逐项全等前像**；非 FINAL 与 FINAL 一致 | 三步验证照 RULE-DATA-OPS，顺序铁律（改标→回执→收版）未倒 |
| REG-IND-001 修尺（裁④） | 审计脚本停算面改读在册真源＋册不可读回 rc=3；4 钉测试含**反向对照**（打回空集合必 rc=2） | 假门桩按真门 NULL 字面 `"None"` 形状（非 `\N`） |
| 夹具 6 行退役（路一①） | 账本 active 8,118→8,112／retired 640→646（**净零行**）；投影差集 13→**7 零垃圾** | `api.retire` 单口，authority_ref＝统筹原话，事件面内容级读回 |

**二、未闭面（都有主、有时刻，不塞本班）**

1. 判据②：明日 10-14 16:3x 那笔 basic 新写的 `data_source` 应为 `tushare`（统筹侧复核）；若仍 akshare ⇒ 另找第二写者，按台账 §卅九 三读对质法，不改判据。
2. 六件套在册化：袋 `0020` 在飞（前一道死袋 `0019` 死于落地时读到共享 index 的半写册面瞬时态——该 hazard 已连同据链交清队列/维护线）。落地后**归档车道**（`session_worktree.py archive --execute`，含会话壳与影子指令面）。
3. `scripts/script-manifest.yaml` 未随袋：车道面与 dev 面差 **+299/-3**（旧渲染），带它＝整档改写；清单归位＝由 `generate_manifest.py` 生成（根宪法 §9.5 禁手工维护静态清单）。
4. 2016 及更早 basic 仍缺；2017-2018 周线/月线/后复权表族是否跟，由源件落地时定。
5. tilib 跑器两条根治：`--only-shard` 越界静默空转须红退出；跨午夜窗新鲜度（指纹陷阱）根治未落。

**三、复核命令（只读）**

```
python -c "import sys;sys.path.insert(0,'scripts/backtest/fexam');from ch_data import ch_query as q;print(q(\"SELECT count(), uniqExact((trade_date,symbol)) FROM c1_market.stock_daily_basic WHERE trade_date='2026-10-12'\"))"
cat .runtime/tmp/st-datalane2-20261012/seg2/step4_receipt.json
cat .runtime/tmp/st-datalane2-20261012/seg2/retry_marker.json
python -c "import sys;sys.path.insert(0,'scripts/governance');from _shared.module_translation_loader import get_module_translation as g;print(g('scripts/data/backfill_kline_daily_history.py'))"
python scripts/commit_queue.py status --session st-datalane2-20261012
```
## 七、收口回执（统筹全线收口令 2026-10-14 午，sid=st-datalane2-20261012）

按序回执：**①无可推进项**——唯一在手前提"甲"（PERMANENT-SYSTEM-TRIGGER 的 m10 声明解析对称化）
12:1x 实测未落地（门件 dev 末笔 `ec33643ea93`／2026-10-03；声明解析函数 grep=0；
维护七班三袋 0010/0015/0018 全 pending；本班探针磁盘=HEAD 同面 `a598e78d2588`、三形态全拦、退出码 1）。
不硬投、不加零收益声明，转 ③ 交接卡＝`00_ledger.md` §四十二（含触发通知的唯一有效形态、
未落地两件的逐字 blob 存证与已实测抽回命令、甲落地后五步动作序、两处本班自纠）。

**②收班序列实测量**：队列本班四态 pending 0／running 0／done 8／dead 3；dev 面账本 679 行／42 节、
交付册本节前列数 6→7；`.runtime/locks` 137 条含本班 sid 0 条（无 claim 待 release）；
命令行匹配 `datalane2` 的 python 进程 0 个（无守护待按 PID 停）；
注册表 `get_session('st-datalane2-20261012')` 返回假（会话已在册外）。
剩两步在本袋落地后执行：车道归档（撞保护区即停手留命令，禁硬闯）＋撤 reaper keep 本班两行
（按 sid 谓词删、不按行号删；该件未跟踪 `.gitignore:344`，故属本地动作）。

**本班交付面（一句话可核）**：段二价量 1,657,332 行／3,580 只（C1=0.9967）、
basic 2019-2020 与 2017-2018 两批（1,831,872／1,561,578 行，rows==keys，全标 tushare）、
写侧 `data_source` 四处随形改已落（`3422a5c2d6`，落地面 132 passed＋ruff 净）、
④纠源 ALTER（akshare 错标 11,122→0）、10 月分区收版（2→1 版本、逐列校验和不变）、
运行面重启（子 9548@21:32:47 晚于修复落地）、REG-IND-001 尺与立法对齐、
PG 夹具 6 行经正道撤账留墓碑。

**待他班/待 Owner（非本班可签）**：判据②＝今日 16:3x 首笔新写入 `data_source` 是否显 `tushare`（统筹代跑）；
六件套在册化（等甲）；投影物化链与门解析器本体（门主车道）；2016 及更早 basic、周月线/后复权表族（另立工单）。
全线交接真源＝各班班账＋队列 blobs，本对话记忆不作依据。

**收口袋的第一次投递死了，死因与本册 §四十二/§四十三 同源，记档防重复**：袋
`q-20261014-st-datalane2-20261012-0023` @12:24 入队（`git_commit.py --enqueue`，无 `--base-head` 旗）、
12:37 落 dead，dead_reason＝`[landing] 非注册表族件双侧皆改真冲突（整文件三方）: 00_ledger.md`，
`base_head` 记的是**车道 HEAD** `7599a6aff2d`（车道 HEAD 是 dev 祖先＝旧基底），而袋面按 dev 现值重建——
基底与被比对象错开，于是"纯追加"被读成"双侧皆改"。修法不是弱化仲裁：改用
`commit_queue.py enqueue --base-head <dev sha> --worktree-root <车道>` 把基底写回真值
（本班已证袋面第 1..679 行与 dev 现值逐字等，是真前缀非事后拼贴）。
上表的 claim=0／进程=0 是建袋前（12:1x）读数，本袋投递自身开了会话＋守护（pid 16140）＋claim 两件，
落地后按 release→按 PID 停守护→unregister→归档车道 的序关掉（archive 的死判对活跃会话硬拒）。
