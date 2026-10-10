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

## 6. 下一轮入口（照做即可续）

1. 修 §2.1 表面字面量 → `pytest tests/backtest/test_card_binding.py`（17 绿）→ 投"模块＋翻译册"袋（域已拆好：
   `bag2b1.txt`／`bag2b2.txt` 在 `.runtime/tmp/st-mineloop-20261010/`）
2. 找册主车道解 §2.2 后投 `bag3.txt`（31 张新卡，token 已在 dev）
3. 绑定层续绑优先序：板块族底座复用 8 张（L2-01-2/L2-01-3/L2-01×2/L2-02/L2-02-2/L2-04-1/L2）
   → `c3_fundamental.research_report` 评级聚集 1 张 → macro_data 全球因子 1 张（须先定"日变化率或 z-score"择一，卡面未冻结＝禁考）
4. T4 监听：`SELECT stage,count() FROM c1_market.emotion_index GROUP BY stage` 到 close_final 复元即开情绪先锋四态卡首批
5. CH 纪律：W1 v2 提前窗已 PASS 收卷、任务 Disabled（周六常规窗恢复＝考后事项，examchief 在册）；
   01:00–04:00 让路不变，`--override-ch-window-with-reason` 留痕形已在册可抄
