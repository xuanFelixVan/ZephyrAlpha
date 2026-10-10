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
