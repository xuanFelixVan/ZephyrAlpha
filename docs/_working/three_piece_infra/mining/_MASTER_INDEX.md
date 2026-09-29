---
ttl: task_bound
completes_when: 每个可开工（⬜/🔨）中类都有叶簿且三扫收敛（无新增 W-xx）；本表无 NOT-MINED 行
---

# 挖矿叶子层 · W-xx 总索引（族 → 叶簿 → 头号实测结论）

> **本表是什么**：`00_master_skeleton.md` §二是**中类层**（W-xx），其 §四"长尾②"自认「六图/波2 案卷内 ⬜ 细目逐条二次分诊（各族子文档）」**未挖**。本层=那件未挖的事：一个 W-xx 一份叶簿，回答"谁写/谁读/何时触发/现在为什么不算完成"（协调册 §四 判据）。
> **口径真源**：`docs/_working/total_command_closeout/02_field_corrections_and_new_cases.md`（X 册）**优先于** `00_master_skeleton.md`（骨架册）。冲突处叶簿显式记两说，不静默择一（本任务 RULES 条 2）。
> **不在本层范围内（已由他会话建成，只引不挖）**：业务链**环节**叶层 `docs/_working/decision_map_campaign_20260924/links/L01_regime/` … `L09_review/`（每环节 SKEL.md + _INDEX.md + `sNN_*/MINE.md`，约 97 份叶簿）。本层做的是**W-xx 族叶层**（施工分诊面），与 L0x 是正交两轴：L0x 答"这个业务环节怎么通的"，本层答"这条待办谁负责、缺哪一手、什么算完"。**两轴已互为引用**（例：`family11_endgame_capability/W-116.md` §4-D 指向 `links/L06_exam_alloc/SKEL.md:164` 项 L06-C02）。
> **状态图例**：继承骨架册 §二 标记（✅/🔨/⬜/🌑/【快】），X 册有改判者在"态（校正后）"列注明。
> **叶簿路径约定**：`mining/families/<familyNN_slug>/<W-xx>.md`。文件名以 `-` 而非 `_` 连数字（R5-DIGIT-SUFFIX 实测判定式 `r"_\d+$"`，X-04）。
> **本表最后更新轮**：本会话终轮（叶簿 **30** 份在册，覆盖率与未挖清单见 §十六；跨族收敛建议见 §十七）。

## 〇、本索引自身的实测改判（先声明，免得叶簿被当成照抄骨架）

| # | 骨架册/任务书声称 | 本会话现读（HEAD 面） | 影响 |
|---|---|---|---|
| IDX-1 | 任务书：骨架册声明"**14 families** / 140 openable W-xx + 12 gated" | 骨架册 §二 标题写 **"12 族 / 58 个可开工中类"**；§五-4 封顶声明写 **"13 族 / 122 个可开工中类 + 12 待门位"**。全文 `grep -c "族 14\|族14"` = **0** | "14 族/140"在 HEAD 骨架册里**不存在**；本索引按盘面实族数（族 0–13）建表，族 14 见 IDX-2 |
| IDX-2 | 任务书："family 13 + family 14 (red-team and external-review backfill, **W-140..W-180**)" | `grep -rhoE "W-1[6-8][0-9]" docs/_working/total_command_closeout/` 只回 **W-160 / W-161 / W-162**；W-163..W-180 **全目录零命中**。红队回流=W-140..W-162（X-64/X-65），外部审查回流落在 `review_ext_*.md` + 骨架册 §六 前言（波 1A 可信层），**未编 W 号** | **不虚构 W-163..W-180**。外部审查回流按真实载体登记为 §十五"未编号外部审查项"；W-181..W-186 是协调册 §六 **将**新增的族 15，尚未落 HEAD |
| IDX-3 | 骨架册 §一：裁定册"HEAD 面 entries=231 条，最大号=裁定#413" | 复核**成立**：`… \| grep -cE "^- ruling_id:"` = **231**；`… \| grep -oE "ruling_id: .裁定#[0-9]+" \| sort -n \| tail -1` = **413**（条目行 5701） | 全战役引用裁定号的上限锚点确认=413；更高位一律记"悬空自赋号"（W-56）。**新事实（W-56 叶簿）**：HEAD 文档面被引用的最大号也=413 ⇒ **HEAD 引用面当前无悬空号**，残留只在车道 |
| IDX-4 | X 册 §二/§五 用"归位"列新立 `W-35b / W-40b / W-31b` 三个号 | 骨架册族 12 已把**同一事实**编号为 **W-127（X-21）/ W-128（X-22）/ W-129（X-23）** | **三对同号两立** ⇒ 同一件事在两处各排一次产。详表与裁决建议见 `family03_data_business_chain/W-31.md` §8；本表把 `b` 号行标为"与 W-12x 同号两立" |
| IDX-5 | 骨架册 §二 W-13 行标 🔨（"成品存在但未进 HEAD"） | 本窗：`src/zephyr/data/ch_parts_monitor.py`、`src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py`（470 行）、`tests/governance/commit_gates/test_ch_final_gate_no_final_reads.py` **全在 HEAD**，且名册 `in_process_gate_registry.yaml:327 enabled: true` | 该项**不属抢救面**；真缺口是"三态"未实现（叶簿 M4：`grep -icE "三态\|degraded\|unknown\|stale"` = **0**）⇒ 见 `family01_finished_goods_rescue/W-13.md`。**本战役对 🔨 的默认信任被反向证伪一次** |
| IDX-6 | X-31 记 `REG-STATE-VOCAB-001` "实册 63" | 本窗：`grep -v '^[[:space:]]*#' state_vocabulary_registry.yaml \| grep -c 'vocabulary_id:'` = **29**（与 ROOR 标量 29 **自洽**）；差在**散文 28**（四轴 10+12+5+1）与第四套口径 `34+4+1`（该册 `:498`） | 按 63 排产会把"差 1 的量纲注记"做成 34 条大活 ⇒ 见 `family05_governance_registries/W-52.md` |
| IDX-7 | X-13 记热册蒸发"已被本班修复（盘缺 HEAD 16→0）" | 本窗主区三态复跑：该册状态 **`MM`**、`- file:` 条数 **HEAD 11427 / 盘 11419**、键集差 **HEAD-only 10 / DISK-only 2**、删行 **index 层 2 + 工作区层 16** | **病仍活着且形态升级**（9 条连实体都不在盘上）⇒ 本案是全表**成本最低、时效最高**的一颗，见 `family12_field_discovered_new_cases/W-121.md` |

## 一、族 0 · 编排与验真（`family00_orchestration_and_verification/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-01 | 🔨 | `NOT-MINED` | 11 令归并四态表：产物即骨架册本体，"未落地"判据与 W-02 重叠，待与族 0 一并定夺是否属"文档已交付即完成" |
| W-02 | 🔨 | `NOT-MINED` | 已裁检索：真源=ruling_registry + issue registry 两册；W-56/W-81 是本项的执法面 |
| W-03 | ⬜ | `NOT-MINED` | 归属与禁碰清单：**已由本窗协调册 `three_piece_infra/00_plan_and_ownership.md` §一 部分实现**（八车道归属表）→ 内收对价候选 |

## 二、族 1 · 存量成品抢救落地（`family01_finished_goods_rescue/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-10 | 🔨 | `mining/families/family01_finished_goods_rescue/W-10.md` | 六图役：车道 `.aidrafts/st-mapbuild-20260924` 本窗实测 dirty=**272（238 ` M` + 34 `??`，与 X 册 §七 守卫版真值逐位吻合）**、HEAD=`cb6b4bfc0e`（**早于**主区 `3eeb935743`）⇒ 零自有 commit；"94 件"与 272 **对象不同不可互推** |
| W-11 | 🔨 | `mining/families/family01_finished_goods_rescue/W-11.md` | AI 层 169 件本窗复算=**87 `A ` + 80 ` M` + 2 `MM`**，其中 **86 件在 `docs/_working`**（案卷非代码）⇒ 真实现面约 79 件；87 件 `A ` 是**最脆弱档**（在车道 index、不在任何 commit）；X-02 的 priority 雷必逐 hunk 剔（车道基底正是 outage 原状 `f3cac8b95c`） |
| W-12 | 🔨 | `NOT-MINED` | 全流通三批成品：`lane_ff_*` 共 10 个目录（X-60 驳回"不存在"的红队假 P0）；对账件已存在＝`scripts/automation/flowthrough_verifier.py`（本窗 W-32 取证时命中） |
| W-13 | 🔨→**建议改 ⬜** | `mining/families/family01_finished_goods_rescue/W-13.md` | **IDX-5**：三件成品都在 HEAD、门已 `enabled: true`；缺的是"三态"——`_default_query -> str` 与 W-25 的 `load_flags_from_yaml -> int` **同构压态**；且该门 `[ERROR_CONTRACT]` 与 `[INVARIANTS]` **自相矛盾**（一边"出声不静默放行"一边"异常降级 fail-open passed=True"）⇒ 先裁契约再动码 |
| W-14 | 🔨 | `NOT-MINED` | 审计修复账簿 §11–§13：`.aidrafts/st-audit-fix-20260924` dirty=27/ahead=0（X 册 §七 守卫版） |
| W-15 | ⬜ | `NOT-MINED` | 队列 blobs 内"从未 add/已被回退"字节反查：受 W-27 约束；**本窗新证据方向**＝W-11 M1 的 87 件 `A ` 提示"历史固化脚本是否覆盖 `git diff --cached` 面"须先验（不留则这 87 件的暂存语义已丢） |
| W-16 | ✅待复验 | `NOT-MINED` | 22 件回退哨兵：哨兵实体与 W-121 的常设尺是同一颗（`W-28b`）；本窗 IDX-7 证明它**未落地** ⇒ 22 件仍无回退保护 |

## 三、族 2 · 提交链解锁与治本（`family02_commit_chain_detox/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-20 | ⬜ | `mining/families/family02_commit_chain_detox/W-20.md` | 双条**仍在 HEAD**（行 7707 / 20231，计数 2）；册头 `unique_key: [id]`（行 55-56）⇒ 同键异容必死于 `commit_queue_landing.py:666`；**Z-05 的"并入"处方有破坏性**：两条是**不相干的两件事**（P1 已晋升的 commit queue 扩展 vs P1 测试身份泄漏新案），并条=静默注销安全案 |
| W-20b | ⬜→判"执法洞"**作废** | `mining/families/family02_commit_chain_detox/W-20b.md` | X-12 算术**独立复算成立**：`enabled: false` 字面 5 次但行 22 是用法注释 ⇒ 真禁用 **4 台**，`103−4=99`；四台注释**全部**自述"Owner 批准 B 方案"，而 `grep -c "B方案" ruling_registry` = **0** ⇒ 声称的授权在正式通道查无（详见 W-120 M3） |
| W-21 | ⬜ | `NOT-MINED` | 门禁 priority：真源=GateSpec；X-02 判该役改动作废；本层实测两门在名册的行位（`DOC-HEADER-SUITE`/`BLUEPRINT-FORMAT`）未取，施工前必自跑 |
| W-22 | 🌑观察 | `NOT-MINED` | own-scope 治本：X-01 撤案（13 类死因，"外来 staged"仅 2 封） |
| W-23 | ⬜ | `mining/families/family02_commit_chain_detox/W-23.md` | 名册**支持** `files_trigger`（29 处已用）而 CREATE-GUARD 条目（`:109-115`）**没写**；`:527` 的 `git grep` 实测在 class 循环内 ⇒ **批量化降系数、触发面降次数，缺一即半只鞋** |
| W-24 | 🔨 | `NOT-MINED` | 派生标量恒取 ours：`heal_derived_scalars` **已在 HEAD**（`src/zephyr/shared/io/yaml_utils.py:729`，读者=`validators/validate_static_manifest_drift.py:178`）；骨架册点的 `script_manifest.yaml` **不在 `_registry/catalogs/`**（本窗 `ls` 报无此档）⇒ 锚路径待重定位 |
| W-25 | ⬜ | `mining/families/family02_commit_chain_detox/W-25.md` | 病在**签名**：`load_flags_from_yaml() -> int`，`:339-341` 把"路径解析失败"与"文件不存在"并成 `warning + return 0` ⇒ 一律 OFF；`except Exception: return None` 同形**两处副本**（`:316-323`、`:213-222`）⇒ Z-10 三态在现签名下**无法表达** |
| W-26 | ⬜ | `mining/families/family02_commit_chain_detox/W-26.md` | `run_enqueue_preflight` 全仓**只有 1 个调用点**（`commit_queue.py:2811-2813`），而"形成队列项"另有 `:859 enqueue_item` / `:1889 requeue_dead_item` ⇒ 预检写在**命令入口**不在**数据入口**；且预检自述"永不上抛…degraded fail-open"（`enqueue_preflight.py:13`） |
| W-27 | 🌑部分 | `NOT-MINED` | 死信终局处置：本窗旁证 `ls .runtime/commit_queue/dead/ \| wc -l`=**701**、`grep -rl "同侧身份键"`=**35**（带取数时刻；含归档子目录口径见骨架册 W-27 行） |
| W-28 | ⬜ | `NOT-MINED` | "自述绿 vs HEAD 在册"常设尺：X-29 定性形态＝整批未落地+工棚自证绿；**本层抓到的第二必红样本**＝`batched_auto_committer.py` 注释自述"GATE-ASSET-INDEX 写→buffer 合成 OK→workspace_hygiene `git restore`→NOTHING_TO_COMMIT，但 reconciler 已记 auto_committed"＝**"日志说已重生实际未重生"** |
| W-29 | ⬜ | `mining/families/family02_commit_chain_detox/W-29.md` | **活性判据是"PID 活着"不是"在干活"**（`worktree_drift_watchdog.py:746-750` 加固①，注释"宁可漏扫不可误扫"）⇒ X-19 的 keeper **按设计工作**；看门狗自带 `# noqa: m10-time-trigger`（`:17`）**无机读豁免号**，而该管它的门 `PERMANENT-SYSTEM-TRIGGER` 恰关着 ⇒ 两案互为因果 |

## 四、族 3 · 数据与业务链路治本（`family03_data_business_chain/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-30 | ⬜ | `mining/families/family03_data_business_chain/W-30.md` | `'str > date'`＝**边界契约违约**非"缺归一"：`provider_base.py:71-73` 注 `FetchPayload.start/end: datetime.date`，`internal_compute_provider.py:710` 直递给 `financial_derived_compute.run_compute(start: str\|None)`，fdd:397/399 比 fdd:261 的 `isoformat()` 串。X-40 行号全中但"无归一"对 consensus **不成立**（`:146-147/154-157` 已 str↔str，`infer_incremental_start()->str` 在 `:288`）⇒ consensus 只兜 `start`，`end` 仍 date＝**同款潜伏** |
| W-31 | ⬜ | `mining/families/family03_data_business_chain/W-31.md` | 病根＝**回执与真值之间没有第二次读数**：`progress_store.py:217` 只记 RUNNING、`:232` `rows_written` **默认 0** ⇒ "0 行+SUCCESS"结构可达；全仓仅 `auto_backfiller.py:186` 用 `>0` 当判据；**开工前置＝读数通道定档**（X-26/X-27） |
| W-31b | ⬜（X-23 新立） | **与 W-129 同号两立，见 W-31.md §8** | `cohort_ledger_daily` 真重复（`:3437`/`:3816`，本层未复跑）+ 三分母 271/270/266；**须先于主尺**（同名两条⇒二义=新假绿产地） |
| W-32 | ⬜ | `mining/families/family03_data_business_chain/W-32.md` | 宿主**已在册且真被读**：`data_supply_sentinel.yaml` 头注"唯一真源；模块=`zephyr.data.supply_sentinel`"，读者含 `flowthrough_verifier.py`/`calendar_coverage_checker.py` ⇒ **禁新起第二件**；缺的是 intake/dedup/reject 三列守恒⇒**判据一步不成立** |
| W-33 | 🔨待实判 | `NOT-MINED` | Fill 单一写者：Z-22 要求以实测裁决、禁按交接书施工；本层**未挖**（`auto_backfiller.py` 是否即宿主未定） |
| W-34 | ⬜ | `mining/families/family03_data_business_chain/W-34.md` | 张数三套全废（X-25）根因＝**"什么叫空壳表"无机读定义**；登记册 `known_data_gaps.yaml` 实测 **63 条** 且**≥10 个真读侧**⇒改登记有执法效果；X-53 已撤"请 Owner 新批"；最深缺口＝#328 的"逐件三层调查"**没有承载字段**⇒条件批文不可机械验收 |
| W-35 | 🌑 | `NOT-MINED` | hfq `lineage_version`：X-39 面积改为"族内 11 张含 8 张迁移残留"；X-58 判读写侧已部分在场（`redblue_metaq_suite.py:95/96/305/319`、`wo004/recalc_hfq.py:167-176`）。**本层未挖** |
| W-36 | ⬜ | `mining/families/family03_data_business_chain/W-36.md` | `reconciliation_differences` 是**一名三处**（CH `c1_market` 由 `recon_runner` 写 / `governance.db` 日志表 / DDL 面自带"legacy 坏 DDL 毒化"+ReplacingMergeTree 需 `FINAL`）；**零判定路径消费**，只有 `api_server.py:1484` 名字映射 ⇒ "两库皆空"当前被读成"今天对账干净"。consensus/score 两支**未挖** |
| W-37 | 🔨被回退 | `NOT-MINED` | miniQMT 口径四件文案：Z-19 已判"改回+当场落库+哨兵"；本层**未量哨兵实体** |
| W-38 | ⬜ | `NOT-MINED` | 35 个常红尺：X-10 判清单锚文件不存在⇒拆两段（先重跑出真清单） |
| W-39 | ⬜ | `NOT-MINED` | 四类假绿：X-15/X-20 已给"夹具污染审计账本"治形；**本层为④"裸 http.client 绕 DatabaseService"补了实测面**（`git grep -c "http.client"`：`ch_writer.py` 9 / `rolling_archive_reconciler.py` 4 / `archiver.py` 3 / `waste_table_scanner.py` 2 / `akshare_provider.py` 2）⇒ 该类**不是测试面独有**，`scripts/ch/waste_table_scanner.py` 同时是 W-34 的普查件（一案两职=连坐风险） |
| W-40 | 🔨 | `mining/families/family03_data_business_chain/W-40.md` | 62 条链路三态表**无任何 `.py` 生成器**（`git grep -ln business_pipeline_skeleton` 6 命中全是文档/名册）⇒ X-22 的 29/25/8≠30/23/9 与 `#43` 幽灵行是**必然产物**；两条尺今天跑必红（最便宜的红证）；M5 另证"122 vs 62 不同对象"仍被裸引 |
| W-40b | ⬜（X-22 新立） | **与 W-128 同号两立** | "以生成器重出三态表"＝W-40 的尺 3，**不独立成件** |
| W-35b | ⬜（X-21 新立） | **与 W-127 同号两立，叶簿见 `family12…/W-127.md`** | 见 IDX-4 |

## 五、族 4 · 灾备与冷存（`family04_dr_cold_storage/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-41 | ⬜ | `mining/families/family04_dr_cold_storage/W-41.md` | **X-08 的处方在 HEAD 逐字成立**：`_reap_incubated_expired:982` 的判定段（`:1004-1013`）只有 `pid not in live_pids`，**14 行内 `create_time` 出现 0 次**，而全文件该字段出现 **13 次**（对照腿 `kill_ghost_windows:708` 已在用）⇒ 不是缺数据是**没搬判据**；另补一条 X-08 未点出的顺序缺陷：白名单在"存在性+时间窗"**之后**才判，PID 被复用成 `svchost` 时白名单天然护不住 |
| W-42 | ⬜ | `NOT-MINED` | 06:00 轮复制根因（X-09：`.worktrees` 占 92.42%；336678 是 Mode B 增量 diff 计数） |
| W-43 | ⬜ | `NOT-MINED` | vault 旧副本只读位（`0o100444`）一票否决整轮（X-17 第二病） |
| W-44 | ⬜ | `NOT-MINED` | 演练库 `LC_COLLATE 'C' TEMPLATE template0` |
| W-45 | 🔨 | `NOT-MINED` | 备份可恢复性零实证：X-07 判真键名 `last_backup_status`/`last_backup_log_verified`/`last_run_outcome`，现值 `ok`/`False`/`lock_skipped`（非"failed"） |
| W-46 | ⬜ | `NOT-MINED` | keep 免死名单卫生（与 W-41 **同函数**，须同窗施工） |
| W-47 | 🌑 | `NOT-MINED` | keep 判据收紧＝改保命面→⚑-3（Z-29 拆半） |
| W-48 | 🌑 | `NOT-MINED` | `.worktrees` 入排除清单→⚑-3 |
| W-49 | 🌑 | `NOT-MINED` | PT4H 硬时限 vs 3.9h/9.1h/2.2h |
| W-50 | 🌑 | `NOT-MINED` | `g_mirror` 反向复活可删 G 侧唯一 `data.vhdx` ⇒ 本层最高危 |
| W-51 | 🌑 | `NOT-MINED` | ch_vm 重做写 F 盘（X-46：F 亦 92%） |

## 六、族 5 · 治理册与净零（`family05_governance_registries/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-52 | ⬜ | `mining/families/family05_governance_registries/W-52.md` | **IDX-6**：标量 29 == 实册 29（**自洽**），真缺口是①该条 `maintenance: manual` 却带 `counting_rule`（="派生标量却手工维护"，今天必红且不依赖数值）②散文 28 的"1 合并条"无字段解释③第四套口径 `34+4+1` 写在**被登记对象正文**里。正解＝并入既有 `heal_derived_scalars` 作用域，**非新写第二器** |
| W-53 | ⬜ | `NOT-MINED` | `functional_domain_registry`（本窗实测该册 HEAD 1918 行、`ssot_path` 散布各域）的 ssot_path↔covers 错配；X-31 判"同 path 实 2 条"非 3 条。锚行 `:343-356` 本窗读到的内容是 `D_INFRA_RUNTIME` 条 ⇒ **锚位可能已漂**，施工前必重定位 |
| W-54 | 🌑 | `NOT-MINED` | 翻译册 wo001_003：X-43 判"grep -c 输出 0=已办结"错（HEAD 与盘各 3 条悬挂）；净删属注册表门位 |
| W-55 | 🔨 | `mining/families/family05_governance_registries/W-55.md` | 取号器 HEAD **无**、主区盘 **无**，**在两条车道各一份**（656 行/29 个 def-class-O_EXCL 命中）⇒ 先 diff 两版再落地；**对 Z-38 的实质异议**："在途占号感知"这条断言**无数据源**（仓内无占号登记面），须二选一（占号入队列元数据 / 显式退役该断言）；号段口径须写死"max+1，禁回填空洞"（Z-59 在册，本窗实测条目 231 vs 最大号 413=182 洞，骨架册记 193 **不可引**） |
| W-56 | ⬜→**HEAD 面已完成** | `mining/families/family05_governance_registries/W-56.md` | **IDX-3 补**：HEAD 文档引用上界=413=在册最大 ⇒ 当前**零悬空号**；真实残留改两处：①**迁号无闭包**（`#404→#407` 在册，旧号引用无台管）②**号在册而事未办**（X-49 的 #410"授权空转"）⇒ 判据焦点应从"扫悬空"改向这两条；车道面须由有 claim 权者扫（本层禁扫他道） |
| W-57 | ⬜ | `NOT-MINED` | 宪法 L0 漂移：X-52 判 `#ARCH-AGENTS-SSOT-DRIFT-001` 已在册（行 22528）⇒ 引用号可用 |
| W-58 | ⬜ | `NOT-MINED` | 议题册 severity 变体归一 |
| W-59 | 🌑 | `NOT-MINED` | `10_d_data.md` 19,037 行未跟踪（X-52；〔SW15 2026-09-29 复测 19,364，活文件现值以 wc -l 为准〕） |

## 七、族 6 · 考试与搜索链（`family06_exam_and_search_chain/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-60 | 🌑 | `NOT-MINED` | 成本门抽查口径（X-36 可呈，注 `source: replay`） |
| W-61 | 🌑 | `NOT-MINED` | T1 定稿：X-34/X-35 判 verdict 无 `VERDICT:` 字段、"零方差"不可直读、缺同窗对拍件 |
| W-62 | 🔨 | `NOT-MINED` | t1_t2_handover 哨兵被自家复杂度门存量债挡（Z-40） |
| W-63 | 🌑→**撤案** | `NOT-MINED` | `cmd_successor_20260925/`：X-04 撤待入库案、X-54 判 H 册口径错（`ls\|wc -l` 把子目录当文件） |
| W-64 | ⬜ | `NOT-MINED` | T2 前置：晋级池基落主区 |
| W-65 | 🌑 | `NOT-MINED` | 方案①prereg 重签＝冻结判据件（注：本窗实测 `config/search_space_prereg.yaml` 头注称"原#404 迁号留痕见裁定#408"⇒ 重签动作与 W-56 迁号闭包同根） |
| W-66 | ⬜ | `NOT-MINED` | 17 号文六线垃圾判据检查 |

## 八、族 7 · 元问题与 QMine 收尾（`family07_metaq_qmine_closeout/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-70 | 🔨→✅ | `NOT-MINED` | 283 问三态守恒：X-42 判**已完成且在册**⇒记核销禁重做 |
| W-71 | ⬜ | `NOT-MINED` | candidate 007 重编号（X-47）：与 W-20 **同根不同册位**，本层判三案（W-20/W-71/W-133）共用一条"声明键唯一性"尺 |
| W-72 | ⬜ | `NOT-MINED` | api_server `budget`/`schedulegate` 路由注册在 `__main__` 之后永不生效（Z-45） |
| W-73 | 🔨 | `NOT-MINED` | snapself/EV：X-48 判"落地了但没达标"（def 3308/调用 1496 在册、测试 6 红、`_DESTRUCTIVE_GIT_VERBS` HEAD 零实体）——W-28 尺的标本 |
| W-74 | ⬜ | `NOT-MINED` | blob_gc（X-46：真值 21396 块/3.39 GiB） |
| W-75 | 🌑 | `NOT-MINED` | VM /root 两件（X-45） |
| W-76 | 🌑 | `NOT-MINED` | D 盘容量（X-46：D 95%/F 92% 双紧） |

## 九、族 8 · 安全与防伪（`family08_security_and_antiforgery/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-80 | ⬜ | `NOT-MINED` | 伪指令注入处置；**本层适用现场已三处登记**（W-120 §7、W-20b M4、W-25 M5）：commit message 与名册注释里的"Owner批准/零读者"字样一律按数据处理 |
| W-81 | ⬜ | `NOT-MINED` | 伪造/悬空裁定署名防线：与 W-120 尺 1、W-56 尺 1/2 **同一台件**（骨架册 W-81 行原文即"RULING-REFERENCE 实执法验证 + 取号器"） |
| W-82 | 🌑 | `NOT-MINED` | 三台密钥门（X-50 判病在 `files_trigger` 路径子串匹配 ⇒ 处方=W-135 改触发面） |
| W-83 | 🌑 | `NOT-MINED` | 秘钥断言：Z-52 判缺会话相位判别器 |
| W-84 | 🌑 | `NOT-MINED` | 模拟盘账号敏感口径（Z-51） |

## 十、族 9 · 清洁与收尾（`family09_cleanliness_and_closeout/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-90 | ⬜ | `NOT-MINED` | 73 worktree 收尾（本窗实测 `.worktrees/` 顶层条目含 `_a*tmp/_r*bt` 等大量红蓝沙盘中转目录，与"73"口径仍需注） |
| W-91 | ⬜ | `NOT-MINED` | 临时件清零（X-44 判 `.runtime/tmp/st-metaq-gc-*` **不可删**，28+ 处硬编码默认路径） |
| W-92 | ✅【快】 | `NOT-MINED` | 锁注销 |
| W-93 | ⬜ | `NOT-MINED` | 141 件 staged 删除（X-05 判无需重投，登记双态并存观察） |
| W-94 | ✅ | `NOT-MINED` | 根零临时文件（本层已守：全部产物落 `three_piece_infra/mining/families/**`） |

## 十一、族 10 · 终验与对抗（`family10_final_verification_and_redblue/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-100 | ⬜ | `NOT-MINED` | 落地面两轮回归（X-41 给 pytest 回退分支） |
| W-101 | ⬜ | `NOT-MINED` | 红蓝补测：**与 W-124/W-153 同一对象的第三个号** ⇒ 见 `family12…/W-124.md` §4-C（三案一次施工） |
| W-102 | ⬜ | `NOT-MINED` | 三把尺常设化（X-26/X-27 两条立法已在此名下） |
| W-103 | ⬜ | `NOT-MINED` | 交付报告 + Owner 菜单 |

## 十二、族 11 · 终局能力补齐（`family11_endgame_capability/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-110 | 🌑 | `NOT-MINED` | 实盘合规门 12 闸＝门位面；**事实面已另建叶簿 W-140**（本窗实测 4/12 闸运行时非自身引用数**全为 0**） |
| W-111 | 🌑 | `NOT-MINED` | AI 进化点火三缺（B11 判"插座≠护栏"；`tests/shared` 20 skip=覆盖洞不是绿） |
| W-112 | 🌑 | `NOT-MINED` | 实盘双编排二选一 |
| W-113 | 🌑 | `NOT-MINED` | `immutable_tree` 翻转：本窗复核 `config/flags.yaml:52` = **false**（与骨架册 §一 一致） |
| W-114 | 🌑 | `NOT-MINED` | 四台禁用门逐台归因＝W-20b 的实体；本层已给四台的在册理由原文与"B 方案无号"事实 |
| W-115 | 🌑 | `NOT-MINED` | 退役/净删批复：X-53 已缩小本单（空壳表走 #311/#328）；**本层补一条**："退役"缺机读事件/schema 是 W-118/W-119/W-127 三案共同缺口 |
| W-116 | ⬜→建议**🌑** | `mining/families/family11_endgame_capability/W-116.md` | `state_matrix` **槽位/词表/R41 执法全在 HEAD**（`trading_decision_map.yaml:5556` 起，封闭词表含 `pending-owner-adoption`）；**双探测推翻本层初判**：确有生产读者（`daily_decision_orchestrator.py:360` 按格查表），真缺口＝`:354` 读不到只 `log.warning` ＋"包集=空→安全态"是**设计行为**（表现为一切正常）；填格工作**已在业务链叶层立案**＝`links/L06_exam_alloc/SKEL.md:164` 项 **L06-C02**（P0，Owner 资金分配门位）⇒ 只引不挖 |
| W-117 | ⬜ | `mining/families/family11_endgame_capability/W-117.md` | "图形技术库全缺"**错两档**：`chart_pattern_registry.yaml`（`REG-PAT-001`）在册形态条目本窗实跑 **287** 行（schema 已到 v2.2），且**锚点校验台 + 指纹扫描器都在 HEAD**（`check_registry_code_anchor.py` / `pattern_code_fingerprint.py`）⇒ 缺的不是库而是**三字段全 null 占位**（`code_symbol`/`code_fingerprint`/`evidence`，册内注释自述"禁止视为已填写内容"）；"支撑阻力/RANSAC"才是**真缺**（HEAD 零实现件，只命中册不命中码）；"61 形态"在 HEAD **查无锚 ⇒ E4 禁用作工作量**；该子项**判据未就绪**（写不出变异体，须先出口径页） |
| W-118 | ⬜ | `mining/families/family11_endgame_capability/W-118.md` | 普查面被协调册包 13.3 **取代**（本层不另建件）；实测三数并存（active 24／zero 114／机账 138 条 vs 名册 143，CHIPS 5 条未入账）；根因＝**三套"有没有人用"口径互斥** + 机账**零读者** + 死亡证明无登记格式；尺"在 `docs/` 提一句不该让指标出零"是**最小最硬的红证** |
| W-119 | ⬜ | `mining/families/family11_endgame_capability/W-119.md` | 冻结件 `config/search_space_prereg.yaml` **真读者已接**（`factory_grid_executor._apply_prereg_budget` 钳制+fail-closed，头注自述）且引用 #306/#407/#408/#413 **全部可引**；322/159 有案卷锚（`05_t0_and_strategy_library.md:33`）；缺的是**把退役集并入 prereg（作废重开）**与"退役事件"（`strategy_archive/` 已建**零触发**）；**硬前置＝⚑-2 定稿**，未定稿前禁重考 |

## 十三、族 12 · 实测挖出的新案（`family12_field_discovered_new_cases/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-120 | ⬜ | `mining/families/family12_field_discovered_new_cases/W-120.md` | **两值并存**：消息自称 **678 件**，`git show --stat` 实报 **528 files changed / 109893+ / 2320−**（骨架册照抄了 678）；且"Owner批准B方案"在裁定册 **0 命中**；该 commit 时间 `2026-09-26 01:15:39 +0800`；四台禁用门注释同引"B方案"⇒ 同窗同事件；尺=授权对号 + 件数对账 + `disabled_at` 前置 |
| W-121 | 🔨 | `mining/families/family12_field_discovered_new_cases/W-121.md` | **IDX-7：病仍活着**——该册 `MM` 态、`- file:` HEAD **11427** / 盘 **11419**、键集差 **10/2**、删行 index **2** + 工作区 **16**；且 10 条里抽样 1 条（`final_review_chartlib/ext_00_final_review_report.md`）**实体在盘上也没了**（HEAD YES / 盘 NO）⇒ 不能一律按"补 token"处置；正解＝W-28b 三态键集差尺（今天跑即自带红证）＋**禁 `git checkout HEAD -- 热册`** |
| W-122 | ⬜ | `mining/families/family12_field_discovered_new_cases/W-122.md` | 比 X-14 更广：`fullflow_closure_wave2` 的 token 在该册 **2 条**（含 `__init__.py`），而 `git ls-tree HEAD \| grep -c "scripts/governance/fullflow/"` = **0**，且 `git log --all --diff-filter=A` 该件 = **空** ⇒ **从未入库**；根因＝**token 记录的是"准建"意图，无任何件在落地后回收/核销** ⇒ `capability_lookup` 会返回假可用 |
| W-123 | ⬜ | `NOT-MINED` | 审计账本夹具污染（X-15/X-20 三段式） |
| W-124 | ⬜ | `mining/families/family12_field_discovered_new_cases/W-124.md` | X-16 的 W5 修正**两条都被本窗证实**：①`dead_triage.yaml`/`_r2.yaml`/`_report.md`/`deep_dive_r1.md` **都在 HEAD**（且真名**小写**）；②`test_redblue_governance.py`/`test_redblue_robust.py` **HEAD 无 + 全分支零 A** ⇒ 不是"没落地"是"从未入库且盘上也无" ⇒ **须重写不可捞回**；本案与 W-101/W-153 是**同一洞的三个号** |
| W-125 | ⬜ | `NOT-MINED` | `hardlinked` 恒 0 + 一票否决（X-17） |
| W-126 | ⬜ | `NOT-MINED` | T1 备份护甲落后 5 小时（X-18，E3） |
| W-127 | ⬜ | `mining/families/family12_field_discovered_new_cases/W-127.md` | **定性需改**：该腿排班是 `monthly_static` + `incremental: false`（`tasks.yaml:2388-2394`）⇒ "滞后 21 天"**可能在契约内**；真缺口＝**新鲜度契约单侧**（消费方≥5 处读点但无处声明"最多能多旧"），且 `known_data_gaps.yaml` 无 `staleness` 型 `gap_type` 可登记；**若按 X-21 改日更＝未定档即改生产输入**（量级×20~30） |
| W-128 | ⬜ | **与 W-40b 同号两立，叶簿见 `family03…/W-40.md`** | 三态表生成器重出 |
| W-129 | ⬜ | **与 W-31b 同号两立，叶簿见 `family03…/W-31.md` §7** | `cohort_ledger_daily` 重复 |
| W-130 | ⬜ | `NOT-MINED` | 跨库 `system.tables LIKE` 静默空 + `ch_writer.query` 返 `""` ⇒ 判据污染面立法；**本层把它的处方（读数通道定档）当作 W-31/W-32/W-34/W-45 的公共前置引用**，建议升为横切案 |
| W-131 | ⬜ | `mining/families/family12_field_discovered_new_cases/W-131.md` | **五数并存**：本窗实测 TDM `module_ref:` **182 行 / 空 23 / 非空 159**，而 X-28 与协调册记 121/61 ⇒ 或 HEAD 已前进或"行数≠节点数"；另实测 `fail_open_register.yaml` 内 `algo_note_sync_gate.py` **同一路径 2 条**（行 2354/5997）＝W-20 型同键双条在**豁免册**的现场；"半执法"机制本层定位＝**门只在已有声明处执法，缺口恰在无声明处**（X-28 自测 B 的结构性不触发即此）⇒ 必须复用 `NO_DECLARED_EDGE` 第三态 |
| W-132 | ⬜ | `NOT-MINED` | 号文 01~08、12 双向皆无（X-38） |
| W-133 | ⬜（X-47） | `NOT-MINED` | 007 与 5 处引用件同袋序（与 W-20 同根） |
| W-134 | ⬜（X-48） | `NOT-MINED` | snapself/EV 两组红测转绿 |
| W-135 | ⬜（X-50） | `NOT-MINED` | 密钥门触发面改型（替换 Z-49 机制）；**与 W-23 同一名册字段（`files_trigger`）动作**，本层判应同袋施工 |
| W-136 | ⬜（X-52） | `NOT-MINED` | `dead_archive` 89 件在盘 HEAD 不跟踪的定策 |

## 十四、族 13 · 红队回流补编目（`family13_redteam_backfill/`）

| W | 态 | 叶簿 | 一句话头号结论 |
|---|---|---|---|
| W-140 | ⬜ | `mining/families/family13_redteam_backfill/W-140.md` | 本窗逐闸实测（4/12）：`programmatic_trading_guard`、`regulatory_report_generator` 在 `src/**`+`scripts/**` **只命中自身文件**；`manipulation_realtime_monitor` 仅 `order_manager.py:80-81` 的 **`if TYPE_CHECKING:`** 导入；`compliance_rule_engine` 的"1 个引用"经核对是 `compliance_policy_engine.py:33` 的**注释** ⇒ **X-61 把注释和类型期都算成了接线，真运行时接线数=0**；另抓到 `order_manager.py:4/:5` **同文件两行治理头注自相矛盾**（一行标 TYPE_CHECKING、一行宣称 fill 回调消费）⇒ 逐闸表必须"运行时/仅类型/文本命中"三列分计 |
| W-141 | ⬜ | `NOT-MINED` | 盘后任务 ACTION 原文取数（X-62 vs X-32 两说并存） |
| W-142..W-151 | ⬜ | `NOT-MINED` | 波2 役 12 项逐件映射（X-29：31 件 dev 全无；本窗 W-11 复算=86 案卷+约 79 实现件 ⇒ 映射表的分母须重出） |
| W-152 | ⬜ | `NOT-MINED` | HMAC 归属载体立项文档 |
| W-153 | ⬜ | `NOT-MINED` | 场景⑦跨道连坐补跑＝**与 W-124/W-101 同号三立** |
| W-154 | ⬜ | `NOT-MINED` | 机生 L↔F↔TDM 四向对账表＝协调册**包 13.4**（同一对象）；本层另判 W-116 尺 3、W-131 尺 1、W-118 主尺都**要消费这张表**⇒ 它是族 11/12/13 的公共前置 |
| W-155 | ⬜ | `NOT-MINED` | 负结果台账与死矿登记内收到既有宿主（Z-57） |
| W-156 | ⬜ | `NOT-MINED` | 孤儿件三态定策＝包 13.3 孤岛册（与 W-118/W-140 同读侧件） |
| W-157 | ⬜ | `NOT-MINED` | `st-metaq-gc-*` 28 处硬编码改道（X-44） |
| W-158 | ⬜ | `NOT-MINED` | 13 条 AI 代裁追认单；**本层已备 6 条现成"被推翻"样本**（X 册 §六 自我更正表 + 本层 W-116 自证推翻一格 + W-131 五数分歧） |
| W-159/W-160 | ⬜ | `NOT-MINED` | 15 门 P4 合并家族标注／T14 own_scope 十七条；注：本窗在 `/tmp/ipg.yaml:40` 读到 `total_gates: 103` 的注释自述"114→99 P4 七簇合并"，**其中点名 `PERMANENT-SYSTEM-TRIGGER` 在合并七簇之列而它同时 `enabled:false`**（W-20b）⇒ 该条值得 W-159 优先核 |
| W-161 | ⬜ | `NOT-MINED` | 同名册/异路径册读侧错配清理；**W-52 的"实册 63"若来自另一本册，正是本案对象**（本层已把两案绑在一起） |
| W-162 | ⬜ | `NOT-MINED` | arbiter ④⑥ 收尾（金哈希规程＋候选册报告器） |

## 十五、未编号的"外部审查回流"面（任务书所称 family 14，盘面**不存在该族**）

> 骨架册 §六 前言＝`review_ext_verdict.md` 改判的落地（新增波 1A 可信层）。这些项**有实责无 W 号**，本索引不为其编号（编号权在骨架册）；列此以免被当成漏挖。

| 项 | 载体 | 状态 |
|---|---|---|
| 交付状态迁回机读真源 `governance.db.tasks`（73 列/2546 行/14 态含 `VERIFIED`） | 骨架册 §六 前言 | 波 1A 在途（`st-final-build-20260926`） |
| 完成判据 `COMPLETED`→`VERIFIED` | 同上 | 波 1A；**本层提示**：W-25 未修前 flag 可"读不到=OFF"，W-13 未修前 CH 探测可"读空=OK" ⇒ VERIFIED 的判定本身仍有静默旁路 |
| 门禁"名册声明/进程内实载/触发面命中"一张对账表 | 同上 | 与 W-20b/W-23/W-114 **同根，未并册**（本层建议：这张表就是它们的唯一宿主） |
| W-181..W-186（波 13 三件机械基建） | 协调册 §六 并回位点 | 尚未落 HEAD（族 15 待建） |

## 十六、覆盖率与诚实声明

- 本索引列出 **135** 行 W-xx（含 X 册新立的 3 个 `b` 号、4 个 `W-13x` 与 1 处区间行）。与骨架册 §五-4 自述"122 个可开工中类 + 12 待门位 = 134"**差 1**，与任务书"140"**差 5** ⇒ 属**分母口径未定档**（骨架册 §三 同族病），本层登记不擅改。
- **已建叶簿 30 份**（本会话），覆盖分布：族 1 = 3/7｜族 2 = 6/11｜族 3 = 6/14（含 `b` 号行）｜族 4 = 1/11｜族 5 = 3/8｜族 11 = 4/10（本项优先的 W-116..119 全数）｜族 12 = 6/17｜族 13 = 1/13（区间行计一）｜**族 0 / 6 / 7 / 8 / 9 / 10 = 0（未挖，如实标注）**。
- `NOT-MINED` 是真态，不是占位。每轮增长只改对应行的路径与结论；**禁止**把未实测的 W-xx 写成已有叶簿。
- **本层自证被推翻过一次并留痕**（W-116 §4-C：初判"`state_matrix` 可能零生产读者"，双探测后推翻，改判为"有读者但读不到只 warning"）⇒ 本索引所有结论按同一规矩对待：**能复跑的命令 + 两说并存**。
- 封矿判据（挖矿 SOP §6 三扫，本层适配）：①每号有叶簿；②每叶簿六向无空向；③相邻两批"叶内可拆枝"趋零。当前**未封矿**。

## 十七、跨族收敛建议（本层给总筹的内收清单，非施工指令）

| # | 收敛对象 | 本层依据 | 建议动作 |
|---|---|---|---|
| CV-1 | **W-20 + W-20b + W-71 + W-131 + W-133 + W-161** | "同键双条 / 声明键与业务身份不符 / 同名册" 在候选册、豁免册、ROOR、TDM 四处独立命中（W-20 M1、W-131 M4、W-52 M1-M5） | 一条"声明键唯一性 + 册自洽"尺，**参数化册名**；禁六处各建 |
| CV-2 | **W-25 + W-13 + W-29 + W-31 + W-130** | "读不到→静默→当作无事"同构：`flags.py:339-341 return 0`、`ch_parts_monitor._default_query->str`、watchdog 三处 `return summary`、`progress_store rows_written 默认 0`、`ch_writer.query 异常返 ""` | 立**一条横切要求**："读数返回类型必带错误通道 + 探测失败必报红"，逐案引用不逐案重述 |
| CV-3 | **W-31 + W-32 + W-34 + W-40b + W-118 + W-127 + W-140 + W-154 + W-156** | 都在回答"被声明 vs 被使用 vs 有多新"，各自要建扫描件 | 收敛为**丁道包 13.3 普查引擎的视图集**（§3.4 单一 scope），一次施工多案消费 |
| CV-4 | **W-124 + W-153 + W-101** | 同一红蓝覆盖洞的三个号 | 一次"场景×图×测试"差集工程；主尺未就绪（缺矩阵，即 W-154） |
| CV-5 | **W-55 + W-56 + W-81 + W-120** | 号段发号/悬空引用/伪造署名/绕门声称，四条同一根：**编号无中央面 + 引用的批文无机检面** | 共用一个号段解析器 + 一条"引用必在册"尺；W-120 提供今天必红的样本 |
| CV-6 | **W-115 + W-118 + W-119 + W-127** | "退役"缺机读事件与 schema，致四案各卡一半 | 先定"退役/死亡证明"登记格式（建议宿主=`wiring_registry.yaml`），再谈四案 |
| CV-7 | **W-121（独立，最高时效）** | 本窗实测病仍在流血（10/2 键差、16+2 删行） | **优先落 W-28b 三态键集差尺**；它是全表成本最低、收益最高的一颗 |
| CV-8 | **W-11 + W-12 + W-10 + W-14 + W-16** | 五案的"车道成品对账/回退哨兵"是同一件 | 一台参数化"名册/案卷声称 vs git 实况"对账件（与 W-122、W-124 副尺 1 同件） |
