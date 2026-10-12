---
ttl: task_bound
title: 挖矿二班·D 族（D1 情绪六段）资格验收一轮执行记录（四件判据逐件实测）
created: '2026-10-13'
session: st-minedig2-20261012
family_id: MINEDIG-CAMPAIGN
subject_of_acceptance: docs/_working/2026-10-12-d-family-qualification-freeze-draft.md §5
status: acceptance_executed
---

# 10 D 族资格验收一轮（跑数后只执行不改判据版）

> **令据**：挖矿二班题库收尾令 §二.2「按冻结稿 §5 四件判据跑一轮（重放幂等＝同码本两次重放 dominant 逐日一致
> ＋落台逐日可读核查）；照 regime_recal §0 纪律」。
> **判据真源**：`docs/_working/2026-10-12-d-family-qualification-freeze-draft.md` §5 四条（本件**不新增、不改动
> 任何判据或阈值**，只登记"执行了什么动作、读到什么数"）。
> **纪律件真源**：`docs/_working/archive/2026-09/regime_recal/regime_recal_protocol_2026_09_17.md`
> §0（跑数前判据经网关 commit，跑数后只允许执行判据）＋§5（重放幂等判据原文"同一码本两次重放 dominant 序列逐日一致"）。

## 0. §0 纪律的时序自证（可复核，非自述）

| 事件 | 时刻（本地） | 取证命令 |
|---|---|---|
| 判据件（冻结稿）落 dev | 2026-10-12 **15:31:48** | `git log -1 --format="%h %cI" b648983280` |
| 本班车道起建＋会话登记 | 2026-10-12 23:38 | `git -C .worktrees/st-minedig2-20261012 log -1` |
| 本班第一次跑数（重放①） | 2026-10-13 **00:05:03–00:05:09** | `.runtime/tmp/st-minedig2-20261012/replay/r1.log` |
| 本班最后一次跑数（前缀探针） | 2026-10-13 00:14 前 | `replay/` 目录 mtime |
| CH 让路窗起点 | 2026-10-13 01:00 | 全部 CH 腿在窗外完成，窗内零查询 |

⇒ 判据件先于跑数 8.5 小时经网关在册；跑数后本班**只执行**（本件即跑数后所写，含"读到的数"，不含"新门槛"）。

⚑ **一条前提冲突如实上报（本班不代签）**：收尾令称冻结稿"五未冻点裁定 A×5 已入册"。本班实测
`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 内 **`2026-10-12` 零命中**，
最新裁定日为 2026-10-10（该册盘面 mtime 10-10 13:05）；`情绪六段／D 族／资格冻结／MINEDIG` 在该册亦零命中。
同尺正对照＝`ruling_id: 裁定#229/#304/#325/#501/#502` 五条各命中 1（尺子在岗，非 0 命中假红）。
⇒ 本班按冻结稿 §3 的**建议默认 A×5**（即草案自拟默认，非本班择定）执行，因为 A×5 之下 §5 四件的判据文字与
本班动作一字不改；裁定入册动作归统筹/册主，本班不写 ruling_registry、不自代 Owner 署名。

## 1. 判据①：段定义冻结（词表＋R2SIX＋PREEMPT＋微观阈值以 sixphase-v1 整体引用）

| 要件 | 本班实读位点与读数 | 判定 |
|---|---|---|
| 段数与段名 | `src/zephyr/shared/vocab/market_state.py:66` `class EmotionCycleSixVocab`，6 名＝投降(冰点)/蓄势/点火/主升/亢奋/退潮(派发)；docstring 记出处 `trading_decision_map.yaml:4474`（v1.2 定稿，Owner 裁定"机构命名＋修复期独立成段"） | ✅ 六段在册且零改动 |
| 宏观腿映射 | `scripts/backtest/auto_mount.py:135` `R2SIX = {"r10":"capitulation","r4":"accumulation","r11":"accumulation","r3":"expansion","r12":"ignition"}`（r1/r2 无对应＝不路由，与裁定 §3.1 默认 A 同形） | ✅ 符号引用真源，卡面零抄值 |
| 优先级 | `auto_mount.py:101` `PHASE_PREEMPT = frozenset({"r10","r11"})`；`resolve_six_phase`（:270-281）明文"宏观极端态 > 退潮 > 亢奋 > 基础映射" | ✅ |
| 微观腿阈值 | `auto_mount.py:93-100`：PHASE_PCT_WINDOW 250／EUPH_BIAS_PCT 0.90／EUPH_BR20_PCT 0.85／EUPH_RET_WINDOW 60／DIST_MEMORY 60／BR20_WINDOW 20／DIST_MA_WINDOW 20／DIST_BR20_FLOOR 0.50 | ✅ 全为 trailing 窗常数，零拟合 |
| 版本整体引用 | `scripts/audit/t0_six_phase_materialize.py:50` `PHASE_VERSION="sixphase-v1"`，且**逐行**落 `phase_version` 列（本班产物 CSV 每行尾列实测 `sixphase-v1`）；同件头 `[MODIFY-GUARD]` 明文"改动＝考试情绪轴变更，须先改预注册卡并作废重开"、`build_panel` 拒重复日/零行 | ✅ 升版义务与行级版本标记都在 |
| 漂移守卫能红 | `tests/research/research/backtest/test_auto_mount_sle3.py` 含 `test_r2six_drift_guard_vs_framework_composer`；本班实跑＝**12 passed in 1.57s**（零 CH） | ✅ 有在册守卫测试且真跑通 |

**判据①＝绿。**

## 2. 判据②：重建幂等（同码本两次重放 dominant 逐日一致）

执行面＝官方物化通道 `python scripts/audit/t0_six_phase_materialize.py`，产物一律写本班 tmp
（`--out-dir .runtime/tmp/st-minedig2-20261012/replay/*`），**未触碰他班在飞的 `docs/_working/t0_matrix/` 件**。

| 测次 | 动作 | 读数 |
|---|---|---|
| 重放① | 独立进程，全量重建 | 1,824 行，span 2019-04-01..2026-10-09；分布 expansion 394／distribution 221／accumulation 203／capitulation 202／euphoria 40／ignition 2，unrouted 762；5.7s |
| 重放② | **另一独立进程**，同参数重建 | 与重放① **`diff -q` 逐字节相同**；逐日键集合相等（1,824 日）；`dominant` 逐日不一致数＝**0**；`six_phase` 逐日不一致数＝**0** |
| 跨时/跨班对照 | 重放① vs 盘面在飞件（17:04 由 st-t0-matrix 生成） | 序列**逐行全等**（byte-sequence equal＝True，rows 1824 对 1824） |
| vs dev 已落地件 | 重放① vs `git show HEAD:` 那份（rows 1816，止 2026-09-21） | 重叠 1,816 日**标签零不一致**；新增 8 个尾日（2026-09-22..2026-10-09）＝**只追加不改史**；故冻结稿引的"1,816 日"与现值"1,824 日"之差是尾窗演进，不是判据漂移 |
| 正对照（能红证明） | `--start 2021-01-01` 再跑一次 | 行数变 1,395（≠1,824）⇒ 证伪"读缓存冒充重放"；重叠 1,395 日 dominant 零不一致 ⇒ 起点变更不回改历史标签 |

**码本面（同码本何指）实测**：`c1_backtest.regime_snapshot_history` 引擎＝plain MergeTree；表 3,636 行／1,825 唯一日；
run_id 普查 9 条＝两条全史 `VAL-P0-20260912-154118`(1,809 日)＋`VAL-P0-20260916-230726`(1,812 日，即 recal 协议 §2 钉法先例，本班实测该 run_id 确在表内)＋7 条尾部增量；
dominant 取值集＝r1/r2/r3/r4/r10/r11/r12（7 态，与普查 D2 描述一致）。
**多 run 并写面**：1,811 日存在 ≥2 行，而"同日 dominant 分歧"日数＝**0**（SQL `HAVING uniqExact(dominant)>1` 实跑）。

⚑ **结构性风险（不改判据，只登记）**：`auto_mount.load_phase_panel` **不钉 run_id**（该函数原文自述"本函数不钉 run_id"，
:302-303），其幂等目前依赖两条防线：①全表 dominant 零分歧（今日实测 0）；②一旦分歧即 `RuntimeError` 拒出相位
（:304-311，fail-closed 方向正确）。⇒ 若未来新 run 与旧 run 在同日给出不同 dominant，**重建会整体罢工而非随机选版**，
这是合格行为但不是"钉死码本"。按 §3.4 默认 A（补重放幂等验收入资格面）本件已达成；
按 recal 协议 §2 把 run_id 写进装载口仍是**未做的另一件事**，归统筹定序。

**判据②＝绿。**

## 3. 判据③：PIT 无前视（trailing 窗＋CLOSED_BOOK_CUTOFF＋PIT_TAIL_LAG 三件在册且被物化件执行）

| 要件 | 在册证据 | 被执行的实测证据（本班跑数） |
|---|---|---|
| trailing 窗 | `auto_mount.py:241-243` `_rolling_pct`＝`rolling(250, min_periods=125).rank(pct=True)`；`phase_overlay`（:246-267）全腿用 MA20/60 日收益/20 日广度，皆 tail 窗 | 前缀截断探针（下三行）——若有任何全样本归一，截断必然改写历史标签 |
| PIT_TAIL_LAG=1 | `auto_mount.py:83` | 表内最大 trade_date＝**2026-10-12**（SQL 实测），表内唯一日 1,825 个；面板行数 1,824＝逐日去重后 `snap.iloc[:len-1]` 恰切掉 2026-10-12 这一行 ⇒ 面板末日 **2026-10-09**（2026-10-10/11 为周末，表内本无该行，非被切） |
| CLOSED_BOOK_CUTOFF=2025-09-09 | `t0_six_phase_materialize.py:48` | 产物逐行带 `closed_book_ok`；meta 记 `rows_in_window 1566／rows_routed_in_window 886／emotion_gate_allow_days_in_window 359`（本班重放读数与之同值） |
| 双写 fail-closed | 物化件 `build_panel` 遇重复 trade_date 即 SystemExit；`load_phase_panel` 遇同日分歧 dominant 即 RuntimeError | 本班两次重建均未触发（即当日数据面一致），且正对照触发过行数变化（管道非静默） |

**前缀截断探针（判据③的主证据，本班自跑）**：

| 装载窗口 | 行数 | 末日 | 与全窗口重叠日数 | dominant 标签差 | six_phase 标签差 |
|---|---|---|---|---|---|
| start=2019-01-01，end=None（全窗） | 1,824 | 2026-10-09 | — | — | — |
| end=2023-12-31 | 1,155 | 2023-12-28 | 1,155 | **0** | **0** |
| end=2024-12-31 | 1,397 | 2024-12-30 | 1,397 | **0** | **0** |
| end=2025-09-09 | 1,565 | 2025-09-08 | 1,565 | **0** | **0** |

⇒ 把未来数据拿走，历史标签一字不变＝无前视的**机械**证据（非代码注释背书）。

**判据③＝绿。**

## 4. 判据④：逐日落台可读

- **落台件在册**：`docs/_working/t0_matrix/six_phase_history_v1.csv`，10 列逐日
  （trade_date/dominant/six_phase/routed/leg_macro/leg_euphoria/leg_distribution/preempt/closed_book_ok/phase_version），
  盘面版 1,824 行（2019-04-01..2026-10-09），HEAD 版 1,816 行（止 2026-09-21）；
  同目录 `six_phase_history_v1.meta.yaml` 载 provenance／coverage／discipline 三段。
- **可读性＝有真实读者**（本班 grep 实测，非自称可查）：至少 5 条考卷路径把它当六段真源读取——
  `scripts/audit/t0_ceiling_capacity_exam.py:40`、`t0_conditional_e4_exam.py:83`、
  `t0_conditional_e4_v2_exam.py:45`、`t0_conditional_e4_v3_exam.py`（头 [DEPENDENCIES] 明列）、
  `t0_gpu_condition_pack.py:40`。⇒ "落台"不是只写给人看的散文，是考试的输入面。
- **unrouted 是合法态不是缺格**：762 日（41.9%）无六段标签，meta `unrouted_reason` 明文"r1/r2 在 R2SIX 无对应且当日无微观相位→不路由（宁漏勿误），禁硬塞最近邻"；
  与 §3.1 默认 A（保持不路由，卡面 bucket 单列）一致 ⇒ 逐日可读性按"有行即有判、无段即空串"面成立。

⚑ **判据④不能替他人卡背书（本班实测，禁改卡面）**：
`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1__ablation__02_状态矩阵空档段路由代价.yaml`
的 `blocked_reason` 列 **三面**：(1) 六段段态逐日落台未证实；(2) 逐 sleeve 日频权重帧历史未在册；(3) 消融侧 activation 注入器缺件。
本班这轮只把 (1) 的"段态可得＋列名＋逐日跨度"测清（且是 CSV 面，非该卡原建议命令所指的 `c1_market` %phase% CH 表面），
(2)(3) 本班零触碰 ⇒ **该卡保持 `blocked_on_data`，本班不转它、不改它**。解锁需三面齐，非一面。

⚑ **durability 隐患（超四件范围，留呈）**：被 5 条 production 考卷消费的六段落台件住在
`docs/_working/`（frontmatter `ttl: task_bound` 工作区），而根宪法 §9.4 要求"永久区禁引临时区、成果须 promote 才算交付"。
本班不擅搬他人件（搬＝改他班交付面＋动 production 消费路径），只登记隐患归统筹/Owner 定策。

**判据④＝绿**（就 §5 原文"六段序列以逐日快照表可查"而言；其括号内"解锁 ablation 卡"的**更宽**目标＝**未达成**，已如实分面登记）。

## 5. 终判与入册动作

**四件全绿 ⇒ 按收尾令 §二.2 判据，D 族（D1 情绪六段）考试资格成立。**
D2 宏观 regime＝半冻（其判据即本班 §3.4 已入资格面的重放幂等，本轮实测同日零分歧＋fail-closed 在岗）；
D3/D6 资格已齐、D5 已考在册、D4/D7/D8 按冻结稿 §4 留原状（本班不代建、不代判）。

入册面（三处，全部**纯追加**，零删他人字节）：
1. 本件（`docs/_working/minedig2_campaign/10_dfamily_qualification_acceptance.md`）＝验收记录本体；
2. 冻结稿追加 §8 回执节（指针回本件，原文 §1-§7 字节不动）；
3. 普查件追加节（`docs/_working/2026-10-12-exam-card-mining-meta-method-research.md` §9 那条
   "六段规则未冻结＝无考试资格"行**原样保留**，另起 dated 节记本轮反证与指针）。

不自代签面（三条，全部归统筹/册主）：五未冻点裁定入册（§0 已报查无）；
`load_phase_panel` 的 run_id 钉版改动（属代码面，且 §3.4 未要求）；
落台件的永久区安置（§9.4 隐患）；ablation 卡转态。

## 6. 零面声明

零 CH 窗内查询（全部 CH 腿在 00:05–00:14 完成，让路窗 01:00 前收工）｜零新判据、零阈值改动（§0 时序表可复核）｜
零写生产路径（物化件只写本班 tmp；`docs/_working/t0_matrix/` 盘面在飞件未被本班触碰）｜
零改他人卡面与他人册｜N 账本零写（本轮非考试，是资格验收，无 exam_card 试次）｜
判定权留 E2/E4（资格≠分数）。
