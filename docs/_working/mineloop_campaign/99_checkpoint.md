---
ttl: task_bound
title: 99_checkpoint——矿考循环班第一轮交接卡（滚动更新）
created: "2026-10-10"
sid: st-mineloop-20261010
family_id: MINELOOP-CAMPAIGN
---

# 接班先读这页（第一轮 20:50–00:1x 收口态）

工棚=`D:/ZephyrAlpha/.aidrafts/st-mineloop-20261010`（基=会话分支 session/st-mineloop-20261010，
创建时取自 dev@d8284e8ab6，**已落后 dev**，见 §3 死闸）。逻辑会话 pid=0/logical=True 在册（W-29 豁免），
reaper keep 已登记子串 `st-mineloop-20261010`。
保全副本=`D:/ZephyrAlpha/.runtime/tmp/st-mineloop-20261010/safety_r1/`（55 件＋manifest.sha256.json）。

## 1. 已落 dev（可逐笔对账）

| 件 | 落地笔 | 复核命令 |
|---|---|---|
| creation_token 投影净增 40 条 | `e9d6c0f72f` | `git show dev:docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml \| grep -c st-mineloop-20261010` =40 |
| exam_scores_v1 18→25 行（7 行全 fail）＋7 张已考卡 examined 指针 | `c1f633124e` | `git show dev:docs/03_modules/_domain_backtest/exam_scores_v1.yaml \| grep -c '^- card_id'` =25 |

**⚠ P0 不同源缺口（接班第一优先）**：dev 上已有我 7 行成绩，但产生它们的绑定层
`scripts/backtest/fexam/card_binding.py` 与 `02_binding_book.yaml` **未落 dev**（被 §2 两道闸挡在入队口）。
读数的人现在无法从在册代码复算这 7 行——须在下一轮先把模块袋落地，或在分数册追加更正行声明出处工棚路径。

## 2. 两道拦路闸（实测复现条件，非猜测）

1. **TABLE-NAME-REGISTRY（我件的真缺陷，可修）**：`card_binding.py` 内 `_REGISTERED_TABLES`
   写了表名字面量（`c1_market.kline_index` 等），门禁 #ARCH-CH-024 Phase 5 拦。
   修法（≤10 行）：代码内零表名字面量——表面全部由绑定册 args（数据面）携带，
   代码只经 `zephyr.data.table_registry.get_registry()` 解析与校验
   （在册键实测可用：`market_index_valuation_daily`／`market_news_sentiment_window`／`macro_credit_money`；
   `all_tables()` 返回 221 条**表名**而非 category_id，故 kline_index/sector_880/margin_trading 的
   category_id 仍须先查 catalog 真源再落键，勿凭记忆写）。
2. **CREATE-GUARD 对新卡 .yaml 判"无 token"（结构性死闸，非本班可解）**：
   token 三径实测＝PG 账本在册 ✅／`git show dev:<册>` 命中 40 ✅／工棚 `git show :<册>` 命中 40 ✅，
   而 31 张卡的入队预检仍拒。同一袋里 `.py` 件却过 CREATE-GUARD（死于 §1）⇒
   拒判只对 `docs/03_modules/_domain_backtest/exam_cards/**` 生效，与前役在册案
   「PG 账本/投影/门禁读取面三口径不一致」同族（`new-asset-landing-blocked-on-pg-backed-registry-20261010`）。
   本班按纪律**三次试投均在入队口快败、未新增死信**（队列 dead 计数未因本班增长），停止烧队列。
   接班动作＝找册主车道（`reconcile` + `registry_projection_generator --render`）核 exam_card 族
   在门禁侧的 token 读取路径，或给该族登记 di_seam 类豁免；勿改门禁判据。

## 3. 工棚基底落后 dev

`git merge --ff-only dev` 被拒（本地已 add 的 10 个跟踪件与 dev 同内容但 git 仍要求先提交/暂存）。
本班**未做** `checkout -B`/`restore` 等破坏性对齐（禁野路子）。接班若要续投新卡袋，先按正门把
基底对齐（建议：`git commit` 让会话分支自吸或直接弃工棚从 dev 重放保全副本 safety_r1/）。

## 4. 第一轮账（实测，勿沿用账面）

- 卡册：456 件＝骨架 186＋名卡 270；prereg 174→**205**（本班新 31 张其中 14 prereg／9 blocked_on_data／8 blocked_on_impl，
  另 7 张已考出分转 examined）
- 出分：18→25 行（**7 行全 fail**，FAIL 率 100%）；试次 7 条入 `trial_ledger_registry`（`batch_id: examcard:*:2026-10-10`，
  零 ledger_warning）
- 复挖：9 个前役"封矿"节点送验，**8 推翻**（L2-01/L2-04/L2-07/L2-07-1/L2-09/L2-09-2/P-FLOW/P1-01/P2-04 系）
- 绑定普查（193 prereg）：C 121（engine_replay 63／panel_stock 22／other 27／sector_series 3／probability_hit 3）
  ／U 31／B 17／A? 15／**A+D＝0** ⇒ "现成能考"面已被前役吃光，剩下的每张都要写算子
- 数据面：`emotion_index` pre_open **仅 27 行**（令卡与 L15 立卡前提被证伪，该卡已改判 blocked_on_data，
  判据四键零动）／close_final 止于 2026-09-30／`news_sentiment_score` 2025 密度断崖但逐日覆盖未断（OOS 601 日）

## 5. 呈批面（不自拍）

P1 3 张新卡门柱键在 `_COMPARISON_KNOWN_KEYS` 词表外（执行器无机判面）→ 扩词表须立法
P2 `apply_depgraph.py --add-design-node --dry-run` **实际写 PG**（node_id=16575808 先于实跑存在）→ 工具病根
P3 MOD-BT-248 blueprint 面缺位（depgraph 报 `docs/03_modules/MOD-BT-248/blueprint.md` 不存在并标 missing）
P4 试次册内见 `batch_id: examcard:TDM-E-TEST/*`（测试卡 id 形态）→ 疑似单元跑写生产册，**写入者我未钉死**，须复核
P5 ≥15 张/轮 的结构性不可达（见 §4），要达标须二选一：投板块族算子车道（9 张同一底座）或立重放引擎工单（63 张的门）
P6 业务资产判死/花钱/实盘/出域＝零项

## 6. 四件执行令进度（总统统筹 2026-10-11 00:0x，本班实测回执）

| 令 | 实测状态 | 凭据/下一动作 |
|---|---|---|
| ③ 31 卡袋＋T1 详录袋复投 | **两件均已在 dev**（本班 00:4x 复核实测） | `git ls-tree dev -- …/exam_cards`=487（456＋31）；`git ls-tree dev -- …/T1_quarantine_claim_20261010.md` 命中；维护一班 T4 的 PG 第三源在 dev 码上（`_pg_confirmed_token_files` 命中 3）——我 23:5x 那次复投能过，正是主区投影追齐＋该第三源双力合一 |
| ② 板块族 9 张专道 | 底座＋**3 张已出分**（虹吸集中度／调整周期进度／接棒撤离榜），分数册 dev=26 行 | 专道 agent 正在逐张定案余下候选；两级分桶卡（如 L2-01-3 多周期动量主导度 buckets=categorical_then_quantile）执行器不支持＝已判拒考并入实现面缺口清单，禁硬喂市场均值 |
| ① W-A 重放引擎工单 | **分箱已完成并入库**（`W-A_arm_pilot_spec.yaml` 已落 dev；测试 10 passed） | 实测 19 支双臂卡（键面 arm_protocol 17＋散文声明 2）：现器可考 **3**（进配对分支 2）／需"按臂参数化调用在册装置＋逐臂日收益"适配器 **16**（其中分钟族 5 支另需 5min 切片器）／unfrozen 0（数字缺口单列 pending_numeric_params：X-R1-01/03 体制门降幅 3 处，未替卡拍数）。⇒ **W-B 放量的前置是适配器工单，不是配方**；另 18 支门柱键在 `_COMPARISON_KNOWN_KEYS` 七键之外＝须立法（本班未自扩）。本体件 `arm_protocol_binding.py` 因大白话投影未兑现暂不入册（见 §7.3） |
| ④ GPU 深挖＋情绪先锋 | GPU 零触碰（他班 4 分片）；情绪面**门槛被实测翻案** | `emotion_index` close_final 已续至 **2026-10-09（8,620 行）**＝本班 00:13 实测还是 8,617/止于 09-30 ⇒ 断供面正在回补（探针期间表仍在写）。情绪族 33 张逐张判定：现可考 **5**／等 close_final 1／须数值重建分段 8／他腿阻塞 11／已考 8。⚠ 最大假绿：历史 close_final 实为 **C3+C4 两腿代理**、live 段 3-5 腿 ⇒ 同序列跨 IS/OOS 换定义，`oos_same_sign` 可能考的是"腿数变化"；六段切点查无真源（卡面"在册六段口径"=悬空引用）。首批 N=1 不凑数：`TDM-E-L1-S3/calibration/06_promotion_rate_derived` |

### 本班这一轮新学的三条落地硬知识（接班直接引用）

1. **`--base-head dev` 是落地三方合并的开关**：袋默认 base=工棚 HEAD（我停在昨夜 d8284e8ab6），
   于是"册被他人改过＋我有本地增行"被判 `双侧皆改真冲突` 连死两袋；
   投袋时显式带当轮 dev sha ⇒ `q-...-0008 DRAIN done=1` 一次过。**热件必带**。
2. **TRANSLATION-COVERAGE 已从观察期转硬拦**（新建 .py 缺 plain_zh 直接拒），
   且它读**落地面投影册**：账本在册≠能过门。正解＝先投"翻译册投影先行同步袋"（严格超集，删 0 增 2，
   把他道那条点名写进 message），再投本体袋。
3. **"册只增"门与"别带他人未落地条目"纪律相冲时的解法**＝用键集合差证明盘面是 dev 的**严格超集**
   （缺 0 条），按"投影先行同步"通道过，并点名代带的他人条目——
   这是 maint1 与四连批①同日两笔已用过的同型通道，非本班发明。

## 7. 下一轮入口（2026-10-11 00:5x 重写：原 1/2 两项已完成）

1. ~~修表面字面量→投模块＋翻译册袋~~ **已完成**：表名字面量由 66d02fca0e 版消除（SQL_* 常量＋
   TableRegistry 品类派生）；本班在其上追加算子后按"翻译册先行→本体→测试"三袋落地
2. ~~解考试卡族闸后投 31 卡~~ **已完成**：dev 卡数 487
3. **01:00–04:00 CH 让路**（`02:30 夜跑让路`同在）——窗内只做代码与文档，04:00 后再跑批
4. 板块族续绑优先序（专道 agent 定案后为准）：L2-01-2／L2-02-2／L2-04-1／L2/ablation-02／
   L2-09/03（research_report）；**L2-01-3 判两级分桶拒考**、L2-02/03 的"前 5 日"口径已钉死不得回改
5. W-A 试点 5 张：按 `W-A_arm_pilot_spec.yaml` 的分箱跑 comparison 双臂出分（敞口变换形＝现器可考）
6. 情绪先锋：待数据车道 Gate 0 补 close_final（现 max=2026-09-30），复元判据与首批清单见
   `emotion_lane_status.yaml`
7. **04:00 后必跑（CH 让路解除，`date` 实测后再动）**：
   ① 五分位三卡 `--force` 正确口径重跑（虹吸集中度／调整周期进度／接棒撤离榜，旧行保留、试次照计，
      对照说明见 `09_caliber_deviation_note.yaml`）；② 板块族可考 2 张（L2-01-2／L2-02-2，
      args 与拒因见 `sector_lane_spec.yaml.bind_args`；09-03 因评级序两套互斥留 __TBD_BY_OWNER__ 不跑）；
   ③ 情绪族首批 5 张中先跑不依赖 close_final 的单臂卡；W-A 试点 P1（X-R1-01/comparison/02）
      需状态机 cap 适配器就绪才跑，未就绪就如实不跑
8. **阻断件（唯一一条）**：`scripts/backtest/fexam/card_binding.py`（追加算子 sector_relay_retreat_net_ratio）
   与 `scripts/backtest/fexam/arm_protocol_binding.py`（W-A 本体）均因 TRANSLATION-COVERAGE 读
   **落地面文件投影**（无 PG 第三源，区别于 CREATE-GUARD 今日已获）被硬拦。本班已把两条 plain_zh
   经意图 API 落 PG 真源（`REG-MODULE-TRANSLATION-001`/entries，status=active）并 publish_snapshot
   （v16→v17，entry_count 8861）；**须册主车道 render 兑现投影**（纪律＝禁原属主代打共享热册），
   兑现后两本体＋其配对测试（19 测版）一并投，测试袋已按配对关系退回 17 测版保持 dev 全绿
9. 缺陷呈批（新增两条，均本班实测可复现）：
   ① `add_module_translation.py` 无账本通道、只 safe_write 直写投影 ⇒ 任何一次 render 即抹掉登记，
      而该门现已硬拦＝后来者会被假拦（本班级改用 api.register＋publish_snapshot）；
   ② `commit_queue enqueue` 无 `--allow-multi-domain`（跨域须按域拆袋），且袋默认 base=工棚 HEAD，
      基底落后即"双侧皆改真冲突"死信——热件投袋务必显式 `--base-head <dev sha>`

## 8. 04:00 跑批单（现成命令，机器钟到点即跑；跑前一律先 `date`）

```
cd D:/ZephyrAlpha/.aidrafts/st-mineloop-20261010
# ① 五分位三卡正确口径重跑（旧行保留，only-add 追加，试次照计；对照 09 号偏差申报）
python scripts/backtest/fexam/card_binding.py --mode run \
  --binding-book docs/_working/mineloop_campaign/02_binding_book.yaml \
  --approve-list D:/ZephyrAlpha/.runtime/tmp/st-mineloop-20261010/approve_recast.txt \
  --scores docs/03_modules/_domain_backtest/exam_scores_v1.yaml \
  --out docs/_working/mineloop_campaign/10_exam_recast_quintile.yaml --tag recast --force \
  --override-ch-window-with-reason "04:00 让路窗已解除（夜跑主体 tilib 01:16 实测 Disabled）"
```
- ② 情绪/板块余卡：**候 `11_prebind_review.yaml` 车道判定**（逐字复核闸已前置，
  含"卡面是否给了阈值/分桶协议现器能否判/信号面有无未来收益"三筛）后才写 args 跑；
  已判拒的一张（02-2）在绑定册里 status=rejected，禁改回 approved
- ③ 重跑后必做：分数册袋（only-add 行＋被翻卡面的卡件）随 `--base-head <dev sha>` 投，
  绑定册/复核册同批；dev 与工棚差异若只到行尾（CRLF/LF）则**不需重投**（本班已用归一化 diff 验过）

## 9. 定时看门狗（统筹令③，非本体会话执行）

qoder_cron 一次性本地任务 `a4e738c8-c802-48a0-bc22-cc6536c797b1`，
名"矿考班·02:25 夜跑看门狗照查"，2026-10-11 02:25+08:00 触发、跑完自删（deleteAfterRun）、
模型继承=qfmodel、权限档=auto。零 CH、零 git 写，产物双份：
`.runtime/tmp/st-mineloop-20261010/watchdog_0225.txt` ＋ 本卡追加一节（结构自证：追加后 `^## ` 应为 8）。
本机 01:16 预查已得：**`tilib_indicator_backfill_nightly` state=Disabled（next 仍写 02:30 但不点火）、
`ZephyrAlpha-CH-OptimizeMerge-Weekly` Disabled**；另 `ZephyrAlpha_QMTWatchdog` last rc=4294770688（非 0，
情绪面解锁哨兵本身可疑）——晨报请一并核对这三条。

## 10. 02:25 看门狗照查（一次性自动化轮，非总包本体会话）

- 实测 date=2026-10-11 02:25:08 +0800（本轮所有读数取于该分钟）
- 夜跑主体 tilib=**Disabled**，原文行
  `tilib_indicator_backfill_nightly | state=Disabled | next=2026-10-11 2:30:00 | last=2026-10-10 2:30:01 | rc=0`
  ⇒ next 字段仍印 02:30 但 Disabled 态不点火；最后一次真跑是 10-10 02:30:01（rc=0）
- CH 周优化合并=**Disabled**，原文行
  `ZephyrAlpha-CH-OptimizeMerge-Weekly | state=Disabled | next=2026-10-11 3:30:00 | last=2026-10-4 3:30:00 | rc=0`
- QMTWatchdog rc=**0**（原文行 `ZephyrAlpha_QMTWatchdog | state=Ready | next=2026-10-11 8:45:00 |
  last=2026-10-11 1:33:31 | rc=0`）⇒ §9 记的 01:16 非 0 读数已被 01:33:31 那次更晚运行覆盖，
  该项在晨报可判"已消解"，两次读数都留档不删
- 夜跑日志面（只读 `ls -t .runtime/logs | head -15`，未全树遍历）：最新 mtime=2026-10-10 23:05:04
  （reconcile_worker_247a…log），02:2x 前后零更新 ⇒ **未见**夜跑主体起跑痕迹（故无 tail 对象）
- 队列=counts `{"pending":0,"processing":0,"done":716,"dead":1418}` total=2134，
  lease present=false，daemon online=true。本班 done 27 袋（0001-0005、0008-0017、0019、0021-0031），
  §9/任务书点名的 0017/0021 相符；**0020 实测 dead**（非 done），dead_reason 原文前 160 字：
  `cascade_stale: 基底重校验不适用 ['scripts/backtest/fexam/card_binding.py']（stale_by=q-20261011-st-mineloop-20261010-0019）`
  ——即被同班 0019 落地后判基底陈旧，属超越非回退。另本班 dead 三条在档：0006/0007
  （exam_scores_v1.yaml 非注册表族件双侧皆改真冲突，死信回退人工）、0018
  （rule_catalog_registry.yaml 入账本册但 PG 现读不可用：FileNotFoundError: PG 连接配置文件不存在；
  其处方文字写"退 pending 重试"而此刻 counts.pending=0 ⇒ 实测停在 dead 未回 pending，晨报核对项）。
  本轮未 requeue、未重投、未碰 blobs/dead。
- 结论：02:30 让路面是否仍成立=**成立**（tilib＋CH 周优化合并两枚 02:25 均实测 Disabled，
  日志面 10-11 凌晨零更新佐证确未起跑）。本轮零生产路径写盘、零 git 写、零 CH 查询，未破 01:00–04:00 窗。
  同内容纯文本副本=`.runtime/tmp/st-mineloop-20261010/watchdog_0225.txt`。
  结构自证：追加前 `grep -c '^## '`=9，追加后=10，本节号=10（§9 末句"应为 8"是当时 8 节基线的旧话，已过时）。

## 11. 第二轮收账（总统统筹 01:35 四件合并批复①②③④全部闭合，本班 02:5x 记）

工法一条（统筹令①要求入档）：**窗口须验对象**。让路窗（01:00–04:00／21:00–22:30）成立与否不取决于钟面，
而取决于窗内是否真有让路对象。本班三次实测留痕：01:33／01:38／02:09 均得
`tilib_indicator_backfill_nightly=Disabled`＋`ZephyrAlpha-CH-OptimizeMerge-Weekly=Disabled`＋
`ZephyrAlpha_F06Grid=Disabled`＋`clickhouse-server 进程数=0` ⇒ 04:00 等待取消（今晚第三次溶解），
跑批一律带 `--override-ch-window-with-reason` 把"无对象"读数写进命令面，禁引用上一轮读数当本轮证据。

四件闭合（全部走正门入 dev，逐袋 `--base-head <dev sha>`＋对 dev 现字节为基）：

| 批复 | 落地袋 | dev 面实测 |
|---|---|---|
| ①§8 五分位三卡重跑 | q-…-0026（1122bdc810） | 分数册 26→29 行，三卡全 fail，`n_buckets_used: 5` 命中 3 |
| ③G-CAL-1 消解＋05/06 开考 | q-…-0027/0028/0029（83a7ce0c3a） | 册 29→31 行；绑定册 9→11 格；12_/13_ 两件入册 |
| ②步骤①未判柱清单（纯观测） | q-…-0030/0031（bd1453ff0b） | `run_card` 每行新增 `unjudged` 三面；试件 20 passed |
| ②步骤②calibration 未知键 fail-closed | q-…-0032/0033/0034（ac7565169f） | `judge()` 起始处早退判 fail 并点名键；在册 31 行全 fail、零 pass 需重述（如实记空集） |
| ④三工单立项＋WO-V 开工件 | 本袋（§11 同批） | 15_ 立项书／16_ 词表普查（`--mode vocab-census` 机生） |

⚑ **本班自犯蒸发一条（如实报，不遮掩）**：本班 00:38 袋 39363f2627（执行器分桶口径修复）以**车道旧快照整档**
覆盖了 st-nightmine2-20261010 已落 dev 的 ba7c1891f7「判官按 pillars_numeric 键集分派」修复
（6 行码＋30 行两支红蓝测试），`git log -S"_cal_shaped"` 双向定位＝ba7c1891f7 加(0→1)、39363f2627 删(1→0)。
01:51/01:53 两袋（903c0de7fb＋31c3cc24a7）以 `git apply -3` 把原 diff 重放回 dev 现字节，两支测试并存回收
（16→23 支全绿）。**工法改正（后续每袋执行）**：共享件动手前先 `git checkout dev -- <件>` 取现字节为基，
袋前跑 `git diff dev --stat` 自证净增形态（本夜各袋均为 +N/-0 或点名 -1），禁拿车道旧快照整档投袋。

普查新显形（此前无人报过，两条）：
1. **混形卡**＝19 张卡路由=双臂判官却仍带校准侧键（mono/ic/regime）＋47 张路由=校准判官却带 NAV/事件研究侧键；
   两侧判官各看自家词表，混形卡的另一侧柱＝结构性未判面。词表面普查件=16_（487 张卡、
   无机制判面 186 张、含越表键 119 张、去重越表键名 181 个）。
2. **shadow 族路由现状**＝35 张 shadow 卡按 family 一律走校准判官（三连裁③v2 的键集分派只覆盖
   comparison/ablation），带 NAV 键者现被未知键 fail-closed 拦下不出假绿。**扩面与否＝判据路由面改动，本班不自决**，
   已随 15_ 的 `owner_decision_needed` 呈批（含爆面实测数）。

车道根配置面诊断（解释在册死信 q-20261011-…-0018 与 §10 留疑问）：从 worktree 根跑治理件时
配置按 `__file__` 派生根解析 ⇒ 实测报 `CH 配置文件不存在: <车道根>/config/.env.clickhouse`（02:41 亲见），
q-0018 的 `PG 连接配置文件不存在: FileNotFoundError` 属同族形态。**不是数据面坏了，是根解析错了**。
处方：治理/连库类命令一律从主区根发起（或显式带主区 `--queue-root`/`--worktree-root`），
在车道根跑出的"连不上"读数不得当作生产面事实入册。

下一轮入口（按解锁价值排序）：
1. WO-A1 逐臂适配器：先读在册 simulate 族的参数注入面（属重放引擎工单本尊，跨会话在飞域，须先探在飞归属再动）；
2. WO-A2 5 分钟切片器：先落 TableRegistry 个股分钟面存在性核查（ETF 5/15/30min 已在册，个股面未证）＝数据解锁申请面；
3. 情绪先锋四态卡：QMTWatchdog 01:33:31 rc=0（§10 实测，01:16 非 0 读数已被更晚一次覆盖），
   情绪面 close_final 到 2026-10-09；开考前须先实测 2026-09 腿数断点（辅轴仍禁消费）；
4. 板块族余卡：05/06 已出分后，sector 线仅剩 02-2（拒绑，走卡面修订新版本）与 09-03（未冻序数表，呈 Owner）；
5. `arm_protocol_binding.py` 本体袋仍未落（MOD-BT-249 码件在车道/主区 index 里 staged，dev 无该件）＝残件清零项。

## 12. 第二轮成绩与红面清点（滚动报告面，03:0x 从 dev 实测取数，非记忆）

分数册与卡池面（`git show dev:` 逐件解析计数）：
- exam_scores_v1.yaml 行数=31，verdict 分布 `fail:31 / pass:0`（本轮新增 5 行＝recast 3＋lu 2）；
- 卡池 487 张状态分布：preregistered 177／empty 186／blocked_on_impl 34／blocked_on_data 62／examined 28；
  本轮新转 examined=2 张（卡 05/06），另 3 张是已考卡的正门重跑（分数册 only-add 追加，旧行保留）；
- 试次照计：`run_card` 的 n_trial_ledger 钩子未动，本轮 5 次开考各计 1 次（T5 纪律面无绕过）。

本轮出分成绩（如实，全负）：涨停溢价 05 ic=-0.0515／mono=-0.212／oos=-0.0025（n=1619），
晋级率 06 ic=-0.0636／mono=-0.479／oos=-0.0700（n=1619），五分位重跑三卡 ic/mono 见 §11 表。
**方向性结论**：昨涨停溢价与晋级率越高，次日沪深300 越弱（样本内与 OOS 同号），
与"打板赚钱→次日接力"的母卡先验反向——这是预注册制该产出的那种负结果，不是事故。

红面清点（非本班域，不代修，交晨报）：`tests/backtest` 在本车道跑出 8 红
（test_factory_wiring_night.py 7 支＋test_sim_daily_runner.py 1 支），290 绿。
非因果证明＝这两支文件对 `calibration_exam`／`card_binding`／`fexam` **零 import**（grep 无命中）；
症状面＝跨域符号缺失（`hypothesis_translator.TASK_ROUTE`、`f06_e4_wfa_exam_wiring.append_screen_ledger`）
＋车道根连库解析（CH :8123 refused）。dev 现册该两文件与主区无差（`git status --porcelain` 空）。
本班未从主区跑该两支（避免 F06 落库类测试触生产写面），故只报"车道面观察＋非因果"，不申报 dev 结论。

情绪先锋线收口：emotion_lane_status.yaml 的 exam_now 5 张已全部处置＝05/06 本轮出分（已转 examined），
余 3 张（TDM-E-L0-02/calibration/03、TDM-E-L1-S5/calibration/03、TDM-X-S1-04/calibration/02）被 22e481951e 绑定前复核判 reject（未冻合成式／宇宙分母／未来函数），
按 G4-5 只能走新版本卡，不在本班自决面内。**情绪族首批 N=1 的名额已兑现**（06 卡），
QMT 解锁面（close_final 到 2026-10-09）不再构成阻塞，但"六段/四态重建规则未冻结"仍是硬门。

待 Owner／正式通道三件（本班不自决）：
1. shadow 族与混形卡的**判官路由扩面**（实测爆面 19＋47 张）——15_ 的 `owner_decision_needed`；
2. 09-03 评级序双口径证据链（本班已出对照面，未拍）；
3. 分段/宇宙口径**新版本卡**五支的立项（card_id 逐支可 grep，禁简称）：TDM-E-L0-02/calibration/03_偏离幅度分位响应曲线、TDM-E-L1-S5/calibration/03_derived_signal_shock_panel、TDM-X-S1-04/calibration/02_突破失败连续次数前瞻收益、TDM-E-L2-02-2/calibration/02_板块见顶预警三信号（绑定册 status=rejected）、TDM-E-L2-09/calibration/03_评级上调聚集。

下一轮入口与优先级：板块族余卡（sector_lane_spec.yaml 已排产）＞WO-A1 逐臂适配器只读探在飞归属＞
T2 复挖第二轮（186 张 empty 卡是矿面）。本班 bag 面：本轮 14 袋（q-…-0024..0037）全 done、dead 0。
