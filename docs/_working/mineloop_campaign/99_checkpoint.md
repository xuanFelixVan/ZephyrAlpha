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
| ① W-A 重放引擎工单 | 关键判据已定：**不必新造引擎** | 执行核 comparison 分支的 `signal/signal_b` 就是两臂**敞口序列**，`_arm_nav_metrics` 内部自行做 t 敞口×t+1 目标 的 NAV 与配对差 ⇒ 凡 arm_protocol 把两臂定义为同底座上的敞口变换（置常数/开关 cap/取子集/改 exec_caliber/权重形式）即可现考；真需要新建的只有逐标的持仓路径重放那一类。车道 agent 正按此对 17 张 arm_protocol 卡分箱＋出 5 张试点 |
| ④ GPU 深挖＋情绪先锋 | GPU＝他班 4 分片，本班零触碰；情绪面**门槛已量化** | `emotion_index` 实测：close_final 8,617 行止于 2026-09-30、pre_open 仅 27 行、auction 17 行 ⇒ pre_open 腿撑不起 IS/OOS（那张卡本班已改判 blocked_on_data，判据四键零动）；车道 agent 正出首批开考清单与 Gate 0 需求 |

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
