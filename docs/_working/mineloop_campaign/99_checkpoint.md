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

## 13. 日班 T1 反向复审车道首账（统筹晨令整合版 04:0x 接令，04:3x 首件收口）

接令后动作序：冷启动复核（`lock_files.py cleanup` 清了 1 枚他域死锁：
tests/gov/governance/redblue_wave73/test_v7_pid_reuse.py；reaper --status 正常，commit_pct=70.09 未进告警区）。

三件已落（全部正门，dev 现字节为基）：
1. **事件开关判官落进执行核族内**（无第二真源）：`pillars_route` 第三支 'event'、`_event_metrics`
   （事件日 vs 非事件日次日收益差 bp＋Welch t，IS/OOS/regime 分段各自出数，对齐沿用 shift(-1)）、
   `judge_event` 五柱（方向≤0／t≤-2／事件日 n≥200 族内下限卡面往松不采／OOS 同号／两段同号，
   未知键 fail-closed 与两族同款）；反向命题用**上界键** `event_gap_max_bp`/`event_t_stat_max`，
   不把 `*_min` 的键义反过来重定义（专测双向钉）；本轮单向收紧一处＝n≥200 同时套在"被用来确认的那一窗"。
   绑定位 `op_event_flag_rolling_pctile`：分位一律**历史滚动**（含当日、暖机无读数），
   反未来函数专测＝改 t 之后的取值，t 及之前标记一字不变。
2. **31 行分诊册 20_**：A 类规则写死（硬闸 IS/OOS 同号；候选池只取 ic<0；同命题去重＝五元组指标全等），
   A=4／B=12／C=12，A 占已考卡 14.3%，17 张 IS-OOS 反号卡列 unstable 清单**不立案**（立案＝在多重比较上再赌一次）。
   四闸全过的负向卡实测只有 2 张，第 3、4 张取自三闸池且放松的都是 regime 同一闸（反号逐张写进
   failed_gates/known_weakness 不藏）；严格四闸口径 A=2 的数一并留档，禁只引一套。
3. **四张新版本卡（四换齐）＋结果账 22_**：晋级率头号卡（含 walk-forward 条款预注册）、涨停溢价、
   连板高度＝三张已考；催化剂密度卡 status=blocked_on_impl（基序列算子不在册，禁以近似密度冒代）。
   **三张全 fail**：IS 窗 t=-0.99/-0.01/+0.17 全不显著，且 OOS 三张**全部反号**（+9.5/+23.1/+5.5bp，
   且 OOS 窗事件日仅 79-104 个，不足族内 200 下限）。读法两面都写清：
   不否定母卡在册的**时序相关**负号（审的是单调共动），否定的是更强的可交易形式
   "负效应集中在高分位过热日" ⇒ 按各卡面"一轮为限"，族 reverse_triage_T1_20261011 归档，禁改阈再考。
   分数册 41→44 行 only-add（lost=0、shared 逐字段零差），试次照计 3 次，母卡零改动零重判。

队列机制新观察（登记不追责，供维护班）：同会话两袋（scripts 2 件＋docs 11 件）在后袋入队时**被并入同一 qid**
（q-…-0044 files=11，message 取前袋文本，后袋 qid 记 supersedes）⇒"一次一袋"在队列侧会被同会话合并，
归属与拆域意图丢失。本轮先观察后果再定是否入维护班病根清单；如落地侧因跨域而 red，按 dead_reason 拆袋复投。

检查点衔接：06:00 备份样本窗与补跑夜循环窗期间本班 CH 重载降档（今日剩余动作以纸面与只读为主）；
~12:00 收 T8 补跑验收数（数据车道域，只收数不代跑）；晨报对账项 tilib 补跑夜循环=**未跑**
（实测 LastRun=10-10 02:30:01、NextRun=10-12 02:30:00，10-11 02:30 无对象，与统筹"已完成/已改期"口径一致）。

下一棒入口：T2 板块族余量已收口（17_，8/8 处置）→ 转 W-A 试点 5 张；T3 WO-A1 前置只读探针（在册 simulate
参数注入面＋在飞归属）；T7 接线工单＝walk-forward 触发面（数据落地事件触发，禁 cron）＋20 行早期不可复跑行；
T6 情绪先锋候 Gate 0。

## 14. 探索车道改令闭合＋两处自更正＋主区 index 陈旧快照险情（06:0x 记，14 节结构自证）

令面对象＝统筹 2026-10-11 探索车道改令（取代"三阶段立即发车"）①先吃仓 ②聚合决定是否续扫 ③GPU 采样器复活。

| 令 | 状态 | 凭据 |
|---|---|---|
| ① 吃仓聚合 | 已交（已落 dev） | `23_exploration_digest.yaml` 机生：27,423 格＝t1 2,462＋p2 24,961，45 格 negatives 排除，窗 2020-01-01..2023-12-31；commit 5e303042e2 |
| ① 假设池→新卡 | 已交 | `TDM-E-L1__comparison__04_换手惩罚三档两两对照` ＋ `05_沪深300池宽top100与top50对照`，双双 blocked_on_impl（同一缺口＝执行器只落聚合指标、缺逐日敞口/净值序列），考试窗 2024+ 与扫描窗完全不相交 |
| ② 是否续扫 | 已决且**改口两次** | 先判"定向补扫 648+216 格"（`24_`），落地后继续核价核闸再改口：价格错约 20 倍＋续扫被两道结构闸挡住 ⇒ 全账在 `25_exploration_price_correction_and_blockers.yaml`（commit 5052559681） |
| ③ GPU 采样器 | 已在岗 | pid 22656（pythonw，600s×240 档），设备曲线续写 `.runtime/nightmine/gpu_util_long.log`，字段逐字沿用改前口径（utilization.gpu｜memory.used｜memory.total｜temperature.gpu），归因另开 `gpu_proc_long.log`（NVML 逐进程，理由＝桌面图形污染 util%，单尺不可归因）；该曲线＝st-gpux 的"改前"基线 |

自更正一（数字，方向＝我把自己吓住了）：`24_` 写"648+216 格 ≈ 13-14.4 小时 CPU 单线程"，
实测三支心跳末行 4,167 格/2,719.5 秒＝0.652 秒/格、4,167/2,416.8＝0.580、617/621.6＝0.993（含一次数据装载暖机）
⇒ 864 格 ≈ 9-10 分钟。我把 GPU 化班账袋里的一次性口径当成了网格速率，且错向"更贵"（偏保守所以当时没拦下车）。
口径如实标注：三值均系 engine=auto（心跳里 gpu_util 11-13%、显存 5.7GB ⇒ 确有部分面上卡），
**纯 CPU 路径速率未测**——全仓 15 支 grid_ 批次的 batch_meta 无一支 engine=cpu，无历史读数可引，发跑前须先 8 格 smoke 量 CPU 真速。

自更正二（计数，方向＝我把设计折叠算成遗漏）：`24_` finding_1 的"7 维皆钉死"里有 2 维属设计——
`I_cost_tier`（schema 注释原文"不进乘法网格，恒折叠；执行器对幸存者单独重跑"，预注册册 cost_gate.tiers_bp=[0,5,10,20,40]
由 exam_cost_gate.run_cost_tier_scan 在考试面消费，且该册明写"成本档禁作搜索轴"）、
`F_merge_policy`（active_if 要求 strategy_pool 长度>1，单池跑批下恒 single 是设计）⇒ 真未开＝J/X_stop/X_breaker/X_sector/K 共 5 维。
另另一半证据面同样未开：本班 10 批 27,423 格尚无幸存者进五档梯（`f06_survivors.csv` 在册仅 1 支且 birth_batch=grid_20260916-123551 属老批）。

结构闸一（冻结面）：`config/search_space_prereg.yaml` 头部原文＝"改空间=作废重开预注册（禁跑中改）"，
frozen_by=裁定#413；现生效卡 f06_grid_v2 frozen_by=夜矿续战令三连裁③（Owner 通道，frozen_at 2026-10-10T12:10）。
该册自述分工＝网格轴机器真源在 `config/position_recipe_grid_schema.yaml`（GridCompiler 消费），本册＝冻结/预算/防线真源
（`factory_grid_executor._apply_prereg_budget` 钳制+fail-closed）⇒ 新 λ 档与新池宽档属"改空间"不属"跑新组合"，
本班不自行改 schema、不自行改预注册册；`24_` 里"本班可自决定向补扫"作废。

结构闸二（执行器次序）：phase=1 空间实测 362,880 格（与 GridCompiler 返回 n_raw 逐位相符）；
phase=3+ramp=True 乘积 52,254,720 格（144 倍＝J2×X_stop3×X_breaker2×X_sector3×K4），
直调 compile 实测 **MemoryError**，栈在 `src/zephyr/position/core/position_recipe_compiler.py:269` 的 combos 全展开行；
且 subspace 过滤发生在 expand **之后**（`factory_grid_executor.py:1951 compile → 1954 if subspace → 1956 才过滤 recipes_all`）
⇒ `--context-json` 与 `--subspace-json` 无法组合成窄扫（先炸后筛）。需工单 **WO-A4**＝把冻结移到展开前（或新增 --freeze-dims-json）。

附带核出：该册 f06_grid_v2.duration_basis 的"实测 44.8s/格→1000 格≈12.4h；L2 提速落地 3.5s/格后可经裁定通道升点"已过期
（auto 实测 0.58-0.99 秒/格优于自设前置 3.5-6 倍）；升点按该册文字须经裁定通道，本班不自改 n_samples。

险情登记（非本班起因，本班已就地止血）：主区（＝/d/ZephyrAlpha，非车道）的 index 与工作区里躺着本班四本**已落地账册的陈旧旧快照**——
`02_binding_book.yaml` IDX/WT=131 行（HEAD=279）、`14_calibration_failclosed_restatement.yaml` IDX=90（HEAD=115）、
`99_checkpoint.md` IDX=81/WT=175（HEAD=292），另 `23_/24_` 两本被记成 D（删除）。
他袋此刻提交整池即会把我本班已落地台账**回退掉**＝在册"运行码落后 HEAD"的文档侧同型。
处置：逐本按行判 IDX/WT 是否 HEAD 的纯子集（02_/14_/99_ 工作区面 unique 行=0 ⇒ 无他人新内容可损；99_ index 面有 9 行旧版残留⇒先归档）
→ 陈旧 index blob 归档 `.runtime/tmp/st-mineloop-20261010/index_stale_blobs_20261011/` → `git checkout HEAD -- 三本` 复原，
现 IDX==WT==HEAD（279/115/292），`23_/24_` 同步复原并 sha1 逐位复核；`16_pillar_vocab_census.yaml` 的 IDX=2386>HEAD=2303 属机生再生长非回退⇒**未动**，待其所有者/下次再生物自洽。
根因呈维护班：主区 index 是多会话自动暂存混合池，失败袋/落袋残留会把旧快照长期滞留在池里，
而正门合并器只判"袋内字节 vs dev"漂移，**不判"池内旧快照 vs HEAD 的回退方向"**——建议加一支"池内条目若为其 HEAD 版真子集则告警/拒纳"巡检（本班不代修他人池）。

下一步入口：①Owner 三选一（见 `25_` decisions_needed_owner），推荐 option_1 池宽 top150/top200
（纯 schema 两值；执行器 topN 转整数处 line 1135 已核实为通用解析 ⇒ 零代码，老批读数零动）；
②WO-A4 落地后才谈得上风控 5 维窄扫（核心区 144 倍×12 核点≈1,728 格）；③窗主起跑后读其 manifest＋heartbeat 复核新速率（CPU/GPU 分口径）。

## 15. CH 压缩窗内账（10:5x 接令＝约 4.5 小时禁一切取数；v3 池宽扫描与 hfq WO-004 顺延窗毕）

窗令解读：CH 面全停＝本班窗内零 CH 查询、零发跑；文档/卡片/git/队列照常 ⇒ 只做不动库的事。GPU 采样器只读 NVML、零 CH ⇒ 照跑。

一、§14 首投死信复盘（q-20261011-st-mineloop-20261010-0051 死于"非注册表族件双侧皆改真冲突（整文件三方）"）：
根因**不是他人改了我的册**，而是我车道里的基线本身就是旧字节——`git merge-base --is-ancestor 8bc2237b48 7f8bb84fe5` 返 False，
即 §11/§12/§13 三节只活在 dev、车道 HEAD 从没吃过；"旧基线＋我的追加"对 dev 现值就成双侧皆改。
工法入册（补上我"袋前数删除行"那条的另半边）：凡此前已落 dev 的同名件再投，MUST 先 `git checkout dev -- <件>` 取正基线再追加，
`--base-head` 取 `git rev-parse dev`，投前自证"只增不减"＝`git diff --numstat dev -- <件>` 删除列必须 0、节数=旧+N。

二、窗纪再核，把 §14 里"今日 08:00 起跑"这句**证伪了一半**：
计划任务 ZephyrAlpha_F06Grid 实测（GBK 解码后读数）下次运行时间=N/A、上次运行时间=2026-10-10 21:00、上次结果=0；
且 11:0x 时点 `data/strategy_intake` 最新目录仍是 10-10 23:37 的六分片，10-11 全天零新目录（按 batch_meta 的 ts 前缀过滤＝空集）。
⇒ 红线"08:00 考试窗归窗主"**当前无对象**，与 10-10 那次"到点自己跑"被更正为"立即跑"同形态（"窗口须验对象"第三次应验）。
诚实边界（不把推断当结论）：N/A＋零目录只证"这个注册名今天没有待跑的一次性触发"，不证"无人在跑"；
窗主若换自起进程或改名任务，本班从任务表查不到——要坐实须窗主自报或读进程表（读进程表不违 CH 令）。

三、本班窗内明确不发：v3 池宽窄批（既属改空间＝待 Owner 批重开预注册，又要 CH）继续等窗毕；
采样器截至 10:54:44 共 133 档（他班 97 档基线一字未动），归因册同步在写。

## 16. WO-A4 与 route B 落地账＋新工法两条入册＋一处他车道存量红（15:0x 记）

裁定①（选 route B）＋③（WO-A4 排产）同批施工完，袋 497955b139 四件同笼（本体＋它读的册＋它的测试＋账册，在册"门禁代码+它读的册+本体同袋"处方）：
执行器对 dev 现字节 +80/−1（唯一删除行＝被我替换掉的 `compiler = GridCompiler.from_yaml(SCHEMA_PATH)` 原句，袋前逐行核过），
测试件 +93/−0（5 支新增），探针册与 29_ 各新建纯加。基线取法＝先 `git checkout dev -- <件>`（我车道旧副本 2550 行落后 dev 3122 行）。

改的四下：①`_resolve_grid_schema(schema_path, freeze_dims)`＝把钉值移到 compile **之前**，钉不在册的值即 SystemExit（冻结只准收窄，禁静默扩空间），缺省双空逐字节走原路；
②run_batch 两 keyword-only 参＋main 两旗 `--schema-path`/`--freeze-dims-json`；③batch_meta 与 summary 同记生效面 {schema_path, schema_sha256, freeze_dims}
（否则日后分不清"同空间不同抽样"与"不同空间同抽样"）；④TYPE_CHECKING 守卫（运行面零新导入，ruff F821/UP037 双清）。共享册与 t3a/t3b 两册一字未动。

验收六段实测（零 CH，`woa4_acceptance_probe.py`）：P1 缺省 362,880 逐位不变（sha16 b5faa1299cddf3d3）｜P1b 钉 B_top_n=[top50]⇒72,576（/5，证钉值在展开前生效）｜
P2 phase=3+ramp=True 只钉已探九维⇒144 格且可编译（旧结构此处 MemoryError；144＝J2×X_stop3×X_breaker2×X_sector3×K4）｜
P3 共享册钉 top150 被拦"冻结只能收窄"｜P4 探针册窄批＝72 格与 26_ 逐位相符、全钉单核点＝1 格｜P5b 共享册旧两档同钉法＝36 格（＝裁定②内部对照批，零改即可发）。
测试面：新增 5 支全绿；整文件 40 passed/2 failed，那 2 支在未改动 main 基座同码复跑同败（9.54 秒）⇒ 存量非本班引入。

新工法一（Owner 裁定④入册）：**任何 grid 发跑前"三件定窗"**＝任务现值（Get-ScheduledTask 的 State/NextRunTime/LastTaskResult，非预注册册纸面注记）
＋进程表（Name=python* 且 cmdline 含执行器，且**先减掉自家观测命令的关键词自匹配**——我今天第一次探测就报了 4 个自己的 PID）
＋产物目录 mtime。三条齐了才算窗况，单条不作判据。
新工法二（我自爆后入册）：**引在飞件须"符号名＋行号"双写**。25_/26_/28_ 引的 1951/1954/1956、1135、731 写下时对当时 dev 现值逐条 grep 命中，
但 st-gpux 06:39 e869fd1e0d、07:01 dda797cca9 两袋使文件增长，现值＝compile 2117／subspace 2120→2122／topN 解析 1301／_LAMBDA_PEN 749。单写行号＝定时炸弹。

他车道存量红一处（不代修，呈报）：`tests/trade/position/test_position_recipe_compiler.py::test_charter_v2_schema_nominal_counts` 现红——
它断言 phase=1 折叠集为 {F,I,J,K,X_stop,X_breaker}，而 X_sector 于 10-08 14:16 由 278f283636c（st-mx07-W5）加进 schema 后该测试未随更（该测试文件末改 10-07 09:57 5cdda376364）
⇒ 实测报 "Extra items in the left set: 'X_sector'"，红龄约 3 日，与本班袋无关（本班未碰共享册/编译器/该测试）。一行可修（把 X_sector 补进期望折叠集），等点名再动。

窗毕待发三批（三件定窗＋E0 闸自然放行，全程 cpu 双旗、--exploration-ledger 分册不占考试 N 账本）：
step0 8 格 smoke 量**纯 CPU 首速**并按在册 F5 三元组（measured_at/run_id/commit）回填；
batch_2＝36 格内部对照（裁定②，共享册零改件即可发，钉值面 `.runtime/tmp/st-mineloop-20261010/freeze_breadth_control36.json`）；
batch_1＝72 格探针册续曲（裁定①，`freeze_breadth_probe72.json` ＋ `--schema-path config/position_recipe_grid_schema_v3_breadth_probe.yaml`）。

## 17. 等窗期三件（复联扣发证据／WO-A1 探针结论／L2-09 立场分定义面解冻，16:3x 记）

账在 `30_chwindow_hold_and_unfreeze.yaml`（落地面 5a6e115808，+104/−0 ＋ sector_lane_spec +20/−1，唯一删除行＝被我替换掉的 rating_score_map: __TBD_BY_OWNER__ 那句）。

一、三批按 Owner 批令①的判据**扣发**（不是漏发）：Get-VM 实测 zephyr-ch State=Off Uptime=0；两次仅 SELECT 1 存活探针（15:51/15:52）均 10060 超时；
15:02/15:11/15:52 三支 journal 全是 `WARN Another backup is running (holder PID 27300 alive...)` + `LOCK_HELD skip_record`，**journal 至今无 Start-VM 行**；
`.runtime/backup.lock` mtime 停在 13:48（2.1 小时未刷新），持锁者 CPU 累计 8.83 秒／子进程只有 conhost／无 robocopy·vboxmanage·clickhouse 在跑。
硬发后果＝864 格全死在 `RuntimeError: kline_daily_hfq 数据缺失`，零读数而 negatives.csv 与探索分册被伪阴性灌满 ⇒ 守"断供面禁硬考"。
按批令②：不碰 27300、不清锁、不开机；Start-VM 后留 30 分钟 I/O 缓释窗，仍三面冻结才走五因子闸（归追凶三班）。
补一条我自己不要滑过去的边界：持锁脚本在 serializer worktree 影子根，但那份与主区 sha1 逐字节相同（e1cecf852b1c）⇒ **不能拿"影子根"当解释**；
真正缺的是证据——它 13:48 起跑早于今天 T1 的 journal/transcript 落地（14:54 aafb398927），所以这班一行 journal 都没有，恰是 T1 要治的形态落在 T1 之前起跑的那一班身上。

二、WO-A1 只读探针结论（这句最值钱）：**缺口 100% 在绑定层，不在判官**。
判官侧现值逐条 grep 命中＝run_card:632 已带 signal_b 形参、_comparison_metrics:309 双臂面齐、_arm_nav_metrics:217 且 :236 原文 `ret = df["e"].shift(0) * df["r"].shift(-1)`；
而 card_binding.py 全文 grep `signal_b`＝零命中（run_binding_book:591、run_one:624 只回一条 Series）。
⇒ 适配器只需在 card_binding 加逐臂参数注入＋signal_b 通道，**不动判官、不动卡面阈值**；13 支 blocked_on_impl 卡共用这一个洞。
另登记一处假分雷：_arm_nav_metrics 把臂序列当**敞口**，卡面若写"池组合收益回放"而适配器把收益直接喂进 e 位，会得到"收益×次日收益"的量纲错——**它不报错，只出假分**。

三、L2-09/03 立场分定义面解冻（批令④）：口径按 Owner 裁 B 进绑定 op 规格，写法是**符号引用**不是抄数字——
`rating_score_map: import:zephyr.nlp.research_rating.RATING_SCORE`（B 案真源 src/zephyr/nlp/research_rating.py:38-48，自称唯一真源、未知评级不猜值），
A 案（consensus_daily_compute.py:70-78 的华泰二口径）随弃案注销。复制数字＝造第二真源，两处 map 一旦漂移，本卡与共识日线就各按各的序出分。
覆盖复核对本班 00:16 已入册实测集（七词＋空串，146,940 行）：B 案七词全覆盖，空串/未知＝None 剔除，与该 op 既有"剔 NaN"同一条规则。
残留并列对如实登记：A 案两对注销；**B 案自身还剩 卖出=回避=-1.0**（同分类转移不计数），按实测量级更小（全窗 卖出 30／回避 2，IS 窗 5／2）⇒ 记为已知边界，不上调成缺陷也不偷偷并词。
定义面已解；op 代码实现与出分仍是 CH 面，复联后第一梯队。

四、三批就绪态：探针册已落地（497955b139，n_raw=508,032 只活在探针册里）；两份"其余维全钉"的单因子广度面已生成，格数与 §16 的 P4/P5b 实测逐位相符
（`freeze_breadth_control36.json`=36 格＝批令②内部对照；`freeze_breadth_probe72.json`=72 格＝批令①续曲）。journal 一出 Start-VM＋probe=1 行，我叠三件定窗连发。

## 18. 三批点火读数＋第四次自纠＋N 账本分账闸落地（20:0x-21:2x 记，落地面取数）

一、三批已发完（统筹 18:35 点火令，触发面 17:31:24 journal Start-VM+probe=1；本班自证复联＝三批
8/36/72 格全 out=pos 且 net_returns.parquet 各 970 交易日，价格面真读到才算跑通）。

| 批 | run_id | 格 | 用时 | 秒/格 | 口径 |
|---|---|---|---|---|---|
| step0 纯 CPU 首测 | grid_20261011-183549 | 8 | 55.443s | 6.93 | 冷启动（含一次取数＋combine 未命中） |
| 36 格内部对照 | grid_20261011-200358 | 36 | 23.9s | 0.664 | 共享册 sha16 b5faa1299cddf3d3，16 维全钉 |
| 72 格探针续曲 | grid_20261011-200438 | 72 | 25.279s | 0.351 | 探针册 sha16 2e8e24cc08cebdaa，B 档加 top150/200 |

跨批对拍：共有 recipe=36、sharpe 逐位不等=0、36⊂72=True、72 批净新增 36 格 ⇒ route B 承诺（只加邻域档不动旧格）机械证实。
三批 n_trials_effective（summary 面）＝2／2／11。step0 探索分册文件盘上不存在**不是丢件**：
`if not smoke and _EXPLORATION_LEDGER:`（run_batch 收尾段）——smoke 按设计两册都不进，先读码定性再报。

二、第四次自纠（用自己的跑批证伪自己写下的前提）：26_/29_ 的"池宽未见顶 ⇒ 该续扫 top150/200"依据的是
23_ 的**边际均值**（joint_GxTopN：top50 0.2835→top100 0.3393，+0.0558）。同窄面**条件曲线**是
top50 0.4961 → top100 0.4271 → top150 0.4209 → top200 0.4226，相邻差 −0.0690/−0.0062/+0.0017，单调递增核 **0/18**
⇒ 曲线在 top50 已见顶。误跑批 grid_20261011-190142 反成了教材：200 格里 top10/top20/top30 占 114 格，
不平衡构成能把下降斜率抹成上升。工法入册：判"未见顶"必须用同窄面条件曲线，任何"该续扫"先问它是按哪一列取的均值。
后果：卡 `TDM-E-L1__comparison__05` 的 `sharpe_delta_min=0.03`（卡面自述取自 23_ 边际差一半）口径不成立
⇒ 只能另起 06_ 版本卡（G4-5 禁原地改），口径选择属 Owner 门位，本班不自裁、不催（该卡现 status=blocked_on_impl）。
误跑批 grid_20261011-190142 保留不删、登记**作废读用**（它走探索分册 scan_ledger_breadthcontrol_s0.jsonl，考试账本未进）。

三、WO-A5 N 账本分账闸已落地（三批 a0e27b1ac3 码／b942162936 测试／12bebcfdf4 账册）。
缺陷本体：写"最新批次 N_eff 披露位"原先只看 smoke 不看 --exploration-ledger ⇒ 探索窄批按代码会覆盖考试侧。
今天没出事是**撞上的**：N 账本 CAS 写被 registry_mass_edit_guard 拒（实测 pid=53780 十条 event=refused，
deleted_lines=4 > threshold=2；同册自 09-22 累计 1690 次拒写、10-11 全天 written=0，披露位停在 10-07 的 value=16）。
本班只修自己那半（判据 _should_write_neff_slot／写点 _write_neff_slot 单点化，+25/−7，删的 7 行＝被替换的旧 if 块＋旧注释）；
护栏标定（threshold=max(1,ceil(总行×0.005)) 对中等册＝2 行预算，覆盖中段多行标量块必然替换 ≥4 行 ⇒ 合法写常驻失败；
建议判据改"净删除行数"）转维护二班，file_utils 在他班在飞域，不代修不放宽。
落地面验收（统筹令"复跑探针显示 slot 不被探索批覆写"）：
`python .runtime/tmp/st-mineloop-20261010/neff_gate_probe.py` → ①探索批不写②烟测不写③正常批写（闸不是死闸）④写后再来探索批仍不抢值，
末行 GATE PROBE PASS；真源册全程零写（自证 value=16），靶面是整档副本且不在 `_registry/catalogs/` 路径判定内
⇒ 本探针验的是新闸三态，不验护栏，两件事不混。测试面 5 支新增（真值表四态＋AST 结构守卫），
红证打在 dev 未修字节上三条全红（woa5_red_proof.py）。落地面合跑 130 passed／2 failed
（那 2 支 TestNetReturnsArchive parquet 存量红，已在未改动基座多次复跑同败，非本班引入）。

四、WO-A1 出分最后一格（15_ 册 scope_must 第 1 条口径）：装置已点名——
`evaluate_recipe`（executor:1199）产 weights → `_c4_engine.run_backtest_full`（translated/_c4_engine.py:800）产 net，
e 位=weights 逐行和、r 位=net.pct_change()；禁新造第二台撮合引擎（同真源可派生→必并）。
诚实预期照 Owner③ 口径＝3 支非 13 支，但逐支重读分诊表后**内部再分档**：
①`TDM-X-R1-01/comparison/02` 臂参数已赋数 ⇒ 接线即出分；
②`ablation/03` pending_numeric_params 三项卡面无相邻数值 ⇒ 禁替卡拍数，需赋数或新版本卡；
③`shadow/02` family_not_routed:shadow ⇒ 卡在族路由不在数据面。
另有第二道洞（登记不遮掩）：双臂分支 r 位现硬编 `index_next_day_return()`＝**CSI300** 日收益（card_binding.py:212-218 读到 return 行），
而卡面引句讲的是池组合/基线净值；现校验只查卡面文本与量纲帽，查不出"注入序列并非引句所讲那条"⇒ 会安静出错面分。
修法与接线同批：底座来源自报身份标签，build_arm_pair 里与 r 引句域做同一性断言＋一颗"喂错底座必红"的红证。


## 19. 通宵执行与晨间裁定包（派工令 01:15 起；本班无 00_ledger.md，晨间包按"自家真源"落本册尾节，该映射在此声明）

### 一、执行了什么（逐项＋红绿证锚点）

1. 甲案第 1-3 步（返回面）已投袋 q-20261012-st-mineloop-20261010-0080：exit_simulator.py +14/−0 纯插入，
   st 追加 exposure_daily/weights_daily，不改 arity。四护栏自证：①纯追加；②同输入两码面输入指纹
   ed32c667c8920ac3 相等、nav 逐位等值最大差 0.0、既有 12 支 st 键零变；③头部 [RETURN-FACE-EXTENSION] 声明块随件；④未触发。
   锚点=.runtime/tmp/st-mineloop-20261010/zero_drift_st_probe.py（末行 ZERO DRIFT PASS）。
2. 甲案第 4-5 步"结构面"已投袋 q-...-0081：arm_protocol_binding +86/−2、card_binding +62/−4，六支删除行逐条点名入袋文。
   内容＝ArmBase（e/r/命名序列槽/face_id）＋`series:<名>` 按名注入＋缺名 ArmParamUnfrozen
   ＋FACE_ID_KEYWORDS/require_target_identity（r 位身份闸跑在量帽之前）。
   实测＝三件合跑 84 passed 零 error（与改动前同计数）、ruff format/check 双清。注册动作刻意留下半袋（净绿才投）。
3. ERROR 归因（预签一款）已做基座复跑，结论与预签两支都不同：dev 基座单跑 1 passed；本班码面单跑 1 passed；
   本班码面三件合跑 84 passed 零 error ⇒ 那条 #ARCH-084 tracked-write ERROR 与"册面是否已脏/投影刷新是否真发生写"相关，
   非码面相关，归维护三班在册测试隔离簇（令内同型三例）。手法存证：换面前后 sha 双向校验，未用裸 checkout。
4. 全库 arms 卡普查（新增事实）：30 支带 arms 面的 comparison/ablation 卡经在册 triage_card 分类
   ＝ needs_matching_engine 30／feasible_now 0。

### 二、自裁了什么（逐条＋证据＋依据）

1. 袋形拆 A（结构面，注册留空）＋下半袋（注册＋空册桩重写）——依据＝授权矩阵"域内施工序自裁"＋在册"净绿才投"。
2. series 留空、不自造级别序列——依据＝15_ 册 scope_must_not 第 3 条＋06 卡面"禁在考卷里重写判定逻辑"；
   证据＝MOD-RK-049 实测（evaluate 事件步进；position_cap 为在册固定表 1.0/0.8/0.5/0.3/0.0＋RECOVERY 阶梯 0.25×(n+1)）。
3. ERROR 定性为测试面相关——依据＝授权矩阵"他基座复跑定性存量红，照册登记不代修"。
4. 晨间包落点用本册 §19 而非新造 00_ledger.md——依据＝最保守可回退＋全资产净零；偏离如实记此。
5. 一次 `git show dev:<相对路径>` 在 cwd 漂到车道时返回**空串**，被"长度>5000 才继续"的断言拦下——
   在册教训（dev:全路径取空）今夜第三次自证；写法改为 cwd=仓根＋returncode＋长度双检。

### 三、等裁什么（编号菜单＋证据＋建议默认）

1. 首张双臂分的真闸门＝**卡面级别映射未冻结**：02/06 卡写 L1 100%/L2 100%禁新开/L3 梯度 80/60/40%/L4 0%，
   而在册状态机是 NORMAL/WARN/DANGER/CRISIS/KILL＋RECOVERY 阶梯，其 position_cap＝1.0/0.8/0.5/0.3/0.0——
   **两侧不同数**，L3 的 80/60/40 梯度在状态机里没有对应三档。本班不自愈这个差（补它＝替卡拍数或改卡面语义，均属 Owner 门位）。
   建议默认＝甲：Owner 在卡面补一行"级别↔状态"映射（含 L3 梯度落哪几态）；乙：裁"以在册 position_cap 为准"并走新版本卡更新语义。
   未裁前 06 卡保持 blocked_on_impl，零假分。
2. 中间臂（解除即回满）的无迟滞参数未冻结（hysteresis_ratio 该取何值卡面没写；在册默认 0.5＝卡面"修复当日跌幅 50%"）。
   建议默认＝中间臂暂不开考，只跑开臂 vs 关臂两臂对并随件披露（禁砍臂降级——乙案否决理由已在册）。
3. 关臂"单一阈值全清"阈值取点：卡面只有 L4 的 25%。建议默认＝以 25% 为单一阈值、factor=0.0（两数均在卡面）并披露该读法。
4. 30 支 arms 卡全为 needs_matching_engine：全项目"首张 PASS 卡"候选面比 W-A 册旧口径（含 06 共 3 支）窄得多。
   建议默认＝先按 1-3 打通 06 两臂对，再决定是否为其余 29 支立项撮合引擎；本班今夜不扩面。
5. 0080/0081 若仍未落：只续租不抢；死锁报统筹→维护三班（队列治理权在其域）。

零面声明：判据数值零动｜卡面阈值零动｜N 账本字节零写｜GPU 面零碰｜CH 实跑零次（首张分未出的原因＝上面 1-3，非偷懒）｜
在飞件 claim 续租中｜三袋死信留 dead/ 不删。
