---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
completes_when: 本案卷读数被总包在 dev 侧复核，且其中点名的在册缺陷被属主车道承接
generated_by: 本班只读车道（弱模型出案卷不出裁定），落地面由 st-fclean4-20261012 复核
session: st-fclean4-20261012
lane: wave4-lane_face_readers
role: 只读调研案卷（零删除、零 git 写、零改判据）
---
# 终清波四·车道案卷：`.aidrafts` 面级读者盘点与产物跟踪性核验（退场前判据）

> 原稿面＝`.runtime/tmp/st-fclean4-20261012/lanes/lane_face_readers.md`（TTL 临时区），本件为其入册副本；
> 数值口径以该案卷自带的时刻与参照点声明为准。
# 终清波四·车道案卷：`.aidrafts` 面级读者与"同窗复跑"约束（只读，零删除）

## 0. 口径与红线（先声明）

- 零删除、零 `git add`/commit/`git worktree`/`git branch`/`git stash`、未改任何在册跟踪文件；唯一写出＝本文件。
- 未对任何在册工具执行 `--help` 或裸跑（波二事故在案）；未调用 `SessionRegistry.list_active()`（写调用）。
- **尺子校准（两次自纠，先记防后人重踩）**：
  1. 首版 `.git/worktrees/*/gitdir` 存活判定用 `cygpath -f "$p"` 把路径吞成空串 ⇒ **37/37 全判 STALE（假红）**。
     改正后＝直接 `test -e "$p"`，**正对照**：`test -e "D:/ZephyrAlpha/.aidrafts/st-regsolo-20261010/.git"` ⇒ CONTROL-OK。
     改正后实测 **36 ALIVE / 1 STALE**（见 §5）。
  2. 波三 §5 的尺是 `grep -rl "\.aidrafts/st-"`（**字面量前缀** grep），它数到的"12 支"里混有 `.pyc` 与生成器**散文里的路径字面量**，
     与"真做目录遍历的读者"不是同一个集合。本案卷两把尺都跑（§1 双计数）。

## 1. 任务1：`.aidrafts` 代码侧读者枚举与分类

**尺 A（字面 `.aidrafts`，`*.py`，ripgrep 默认尊重 .gitignore ⇒ 排除 `.pyc`）**：

| 根 | 命中行 | 文件数 |
|---|---|---|
| `src/` | 83 | 19 |
| `scripts/` | 115 | 51 |
| `tests/` | 102 | 21 |
| **合计** | **300** | **91** |

正对照＝同尺在 `src/zephyr/shared/io/paths.py` 命中 8 行（已知存在）；尺失效时表现为整根 0。

**分类计数（本案卷判据，逐档给 file:line）**：

| 类 | 定义 | 文件数 | 命中行 |
|---|---|---|---|
| (a) | **面级读者**：真做 `.aidrafts` 子目录遍历，或以 `git worktree list` 为面枚举 | **10 支模块 / 12 个枚举点** | 见 §2 逐支 |
| (b) | 硬编码**具体** `<sid>` 路径字面量 | 6 支（`wave2/lane_inventory.py`、`wave1b/dead_letter_prescriptions.py`、`wave1b/claim_gate_repro.py`、`wave11/w178_universe_facts_gen.py`、`d5_architecture/generators/generate_dev_delivery_map.py`、`scripts/git_guard.py:955`） | ~14 |
| (c) | 测试夹具（`tmp_path/.aidrafts/...` 自造沙盒） | 21 支（tests/） | 102 |
| (d) | 文档串/注释/案卷正文 | 散布 | ~40 |
| (e) | **排除/跳过清单**（扫描器把 `.aidrafts` 列为不进入，非读者） | 其余 ≈55 支 | ≈130 |

(e) 的关键判据作用：**它对"少一棵树"零反应**——目录本来就被跳过，面变形状不改变输出。
样本（各 1 行即足证形态）：`scripts/ops_guard.py:110`、`scripts/governance/next_ruling_id.py:89`、
`scripts/governance/d1_structure/detect_orphan_py.py:98`、`src/zephyr/library/collectors/fs_collector.py:38`、
`scripts/governance/d5_architecture/validators/validate_*_map.py:201/209/295`、`src/zephyr/security/access_control/orphan_judge/{judge,duplicate_detector,cascade_analyzer}.py:423/136/193`。

**与波三"12 支面级读者"的差解释**：
- 波三的 12＝字面 grep `\.aidrafts/st-` 的**文件数**（含同名 `.pyc`，其原话"等＋同名 .pyc"）。
- 本案卷按"是否真枚举面"重尺：**真面级读者 10 支模块 / 12 个枚举点**（数字撞巧相同，集合不同）。
- 波三点名的 5 支里：**只有 `wave2/lane_inventory.py` 与 `wave1b/dead_letter_prescriptions.py` 确实含 `.aidrafts/st-` 字面量，
  且都是 (b) 硬编码具体 2026-09 sid（`st-final-build-20260926`/`st-mapbuild-20260924`），不是通配面遍历**；
  `wave11/w178_universe_facts_gen.py:27` 与 `wave1b/claim_gate_repro.py:36` 是**用法文档串**（类 d）；
  `generate_dev_delivery_map.py` 的 4 处是**散文字面量**（类 b/d，见 §2.6）。
⇒ 波三"改面形状会落到这些生成器输出上"的前提**在机械层不成立**（详见 §2 结论）。

## 2. 任务2：面级读者逐支四问（枚举对象／输出去处／是否 git 跟踪／少一棵树是否变）

| # | 枚举点 file:line | 枚举对象 | 输出去处 | git 跟踪? | 少一棵 `.aidrafts/<sid>` 会变? |
|---|---|---|---|---|---|
| 1 | `src/zephyr/gov_enforcement/rule_bridge/coordination_state_board.py:108`(`_CANDIDATE_MARKERS`) + `:302-313`（`registered` ∪ `base.iterdir()`，逐目录 `rev-parse --show-toplevel` 自证） | `git worktree list` **∪** `.aidrafts`/`.worktrees`/`.qoder/worktrees` **目录遍历** | `:84-85` → `docs/_working/three_piece_infra/visibility_board/board.yaml` + `BOARD.md`（写入点 `:942-948`） | **否**（`git ls-files --error-unmatch` 双双 NOT-TRACKED；`git check-ignore` 无输出＝非被忽略，纯未跟踪） | **会变**（`worktrees.lanes` 少一行）——但产物不进 git ⇒ 无 `git diff --exit-code` 型门咬它 |
| 2 | `scripts/governance/session_takeover_ledger.py:868-870`（`aidrafts.iterdir()`，跳 `lane_`/`ff_` 前缀）+ `:100,197-203`（`_WORKTREE_ROOTS` 按 sid 探 `<root>/.aidrafts/<sid>`） | **目录遍历**（孤儿补漏：注册表无名字但树还在） | `.runtime/takeover/` 台账 JSON（文件头 `[INVARIANTS]`：只读写 `.runtime` 运行态） | **否**（运行态面） | **会变但方向相反**：删树＝被扫到的孤儿目录少 ⇒ 台账少一条 `orphan_resources` 条目；`git worktree remove` 正规退役＝面与注册表同步收敛，不留孤儿 ⇒ 无条目 |
| 3 | `src/zephyr/governance/audit/reuse_scan.py:148-167`（`_scan_worktrees`：`drafts.iterdir()`，仅当主区无同名件时报） | **目录遍历**（写前"别人在干同一件事"反查） | 返回值进调用方（REUSE-SCAN 写前告警/审计），非落盘册 | **否** | **可能少几条告警**（若某候选树里存着主区没有的同路径件，即波三 §6.2 的 25 件非缓存 C2_orphan）⇒ 属**取证面收窄**，非注册表失效；呈 Owner 门位的抢救前置因此仍成立 |
| 4 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:2181-2215`（`_sweep_stale_worktrees`：`drafts.iterdir()` **但 `:2215` 只收 `d.name.startswith("sess-")`**） | 目录遍历（自动清理侧） | 无落盘产物（返回 `{swept,skipped,warnings}` 进 reconciler 结果） | **否** | **不变**——`st-*` 命名不在其射程；⚑ 反向结论重要：**自动 sweep 永远不会替波四退役这批树，波四也永远不会被 sweep 抢跑**（`git_performance_monitor_reconciler.count_stale_worktrees:145-152` 同样只数 `sess-` ⇒ 其计数零变化） |
| 5 | `src/zephyr/gov_enforcement/rule_bridge/worktree_manager.py:75`(`_AIDRAFTS_DIR`) + `:275,292-304`（`_parse_worktree_list` ← `git worktree list --porcelain`） | **`git worktree list`**（非目录遍历） | 内存返回值（create/remove/exists 判定面） | 不适用 | **会变**：`git worktree remove` 后该树从注册面消失（这正是预期）；仅 `git branch -d` 不消注册面 |
| 6 | `src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py:106`(`_POOL_DIR_NAME=".aidrafts_pool"`) + `:196`（idle 池扫描）+ `:212-217`（`git worktree list --porcelain` 判在册） | `.aidrafts_pool/` 目录遍历 ∪ worktree list | 池 lease 决策（`git worktree move .aidrafts_pool/<pool-id> .aidrafts/<sid>`，`:37/:282`） | 不适用 | **不变**（候选集是 `.aidrafts/` 而非池；池仅 1 棵 `pool-20260919202729-c433`，见 §5 STALE 项） |
| 7 | `scripts/governance/commit_queue_landing.py:1800`（`worktree list --porcelain`） | `git worktree list` | 落地器内部快照（无静态产物） | 不适用 | **会变但无害**：落地树是 `.runtime/commit_queue/worktree(s)`，与 `.aidrafts` 无交集（`:3706-3707` 明示刻意不落 `.aidrafts_pool`，因 `_sweep_stale_worktrees` 会扫 `.aidrafts` 直接子目录） |
| 8 | `scripts/session_worktree.py:773-774`（注释即判据：**"解析 git worktree list --porcelain 为注册表（唯一真源，不做目录遍历）"**）+ `:152-154` + `:1157,1173`（archive 目标必须命中注册面） | `git worktree list` | CLI  stdout/归档面 | 否 | **会变**：`--porcelain` 少一条 ⇒ `session_worktree.py archive <sid>` 对已 remove 的 sid 报"未命中注册表"（`:1173`）⇒ **退役顺序必须 archive 在 remove 之前** |
| 9 | `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py:231-233`（`if rel.startswith(".aidrafts/")` 剥 `<sid>` 前缀；`:218-220` 注明补此道正源于 st-regsolo 实测） | 路径形态判定（非枚举） | 门判定输入 | 不适用 | **会变（运行时行为）**：树被 remove 后**该 sid 的会话**不可能再从树内提交 ⇒ 剥前缀分支不再被命中；对**其它**在飞会话零影响（sid 单段假设 `:233`） |
| 10 | `scripts/governance/wave2/lane_inventory.py:40-59` | **硬编码 SITES 清单**（14 条 2026-09 sid，无通配遍历） | `:41` `OUT_YAML=<LANE_ROOT>/lane_inventory.yaml`，`LANE_ROOT=.aidrafts/st-final-build-20260926/docs/_working/total_command_closeout/wave2`（**该目录已不在盘**） | 产物主仓副本 `docs/_working/total_command_closeout/wave2/lane_inventory.yaml` **TRACKED** | **不变**：SITES 不含 15 候选 sid 任何一枚；且写入点在已消失的 2026-09 车道目录内 ⇒ 现跑只会新建目录后落车道本地件，主仓跟踪件不可能与之齐平（**"复跑同批"对它是伪任务**） |

**§2 总结论（推翻波三前置）**：面级读者里**没有任何一支**产出"内容随 `.aidrafts` 成员集合变化且**被 git 跟踪**"的产物。
两个真面遍历产物（`board.yaml`/`BOARD.md`、takeover 台账）都**未跟踪**；
四个 TRACKED 的 wave 产物（`docs/_working/total_command_closeout/{wave1b/dead_letter_census.yaml,wave1b/dead_letter_prescription_matrix.{md,yaml},wave11/w178_universe_facts.yaml,wave2/lane_inventory.yaml}` + `config/dev_delivery_map.yaml`）
的内容来源分别是：门死信处方硬编码表（`:1274-1275` 只是路径字符串）、ClickHouse 双探测读数（`w178_universe_facts_gen.py:56-57,507`）、SITES 静态清单、交付图散文常量（`generate_dev_delivery_map.py:264,268,276,873`）——**均不随候选树消失而变**。

## 3. 任务3：门与齐平面

`gate_registry.yaml`（`total_gates: 191`，`:10`）中与"生成物齐平/工作树"相关的条目（行号=该册）：

| gate_id | file:line | 比什么 | 削树会红? |
|---|---|---|---|
| GATE-WORKTREE-REQUIRED | `gate_registry.yaml:24-35`（描述 `:27`：commit 是否在 session worktree 内，主区 warn+计数，累计 ≥5 升阻断） | 提交点 cwd 是否在注册工作树内 | **会咬波四自身**：退役批若在主区直提，累计计数走的就是这扇门（与削哪些树无关，属本班工法约束） |
| GATE-CODEGEN-IDEMPOTENT | `:498-511`（`entry: .../check_contracts_codegen_idempotent.py --ci`，描述 `:503` "重跑产物与磁盘零 diff"） | 契约生成器幂等 | **不红**：`files_trigger` 只锁 `architecture_model/contracts/cross_layer_contracts.yaml` 与 `generate_contracts.py`（`:504-505`），与 wave 产物/`.aidrafts` 无交集 |
| GATE-CANONICAL-YAML-DRIFT | `:512-524` | 5 本 canonical YAML vs markdown | **不红**：trigger（`:518`）只含 technology/contracts/runtime_planes/governance_systems_registry/pyproject/chart_factory |
| DEPGRAPH-FRESHNESS | `:965-977` | src/、scripts/ 变更后 depgraph 是否重建 | **不红**：削的是 gitignored 的 `.aidrafts` 树，不改 `src/`、`scripts/` 字节 ⇒ 不触发（若同批改脚本则另论） |
| MAP-ALIGNMENT（GATE-PANORAMA-ALIGNMENT 已 `deprecated`+`redirect_to`，`:2188-2199`） | `:1579-1593` | 三图 schema/generator/registry vs 磁盘 | **不红**：trigger 列的是 depgraph/dataflow/decisiongraph schema 与 `align_panoramas.py`、`docs/03_modules/*.md`；且 `validate_dev_delivery_map.py:201`、`validate_construction_steps.py:202`、`validate_strategy_card_lifecycle_map.py:209`、`validate_data_supply_chain_map.py:295` **把 `.aidrafts` 写进 `_DISK_EXEMPT_PREFIXES`**——面被显式豁免，削树不进门 |
| SNAPSHOT-DRIFT | `:1919-1929`（`own_scope: true`） | own-diff 快照方向 | **不红**：own-scope 只看本袋改动文件 |
| HOT-FILE-BASE-FRESHNESS / GATE-TRIPLE-ALIGN / GATE-BATTLE-MAP-ALIGNMENT / RULE-FOUR-WAY-ALIGN | `:1282 / :143 / :727 / :1824` | 热文件基线/三处齐平/作战图/四路对齐 | **不红**（无一以 `.aidrafts` 为输入；正对照＝这些 id 在同册可 grep 到） |
| GATE:SESSION-REQUIRED / PROTECTED-PATHS 前缀归一 | 处方真源 `scripts/governance/wave1b/dead_letter_prescriptions.py:700-703`、`src/zephyr/gov_enforcement/commit_gates/approval_resolver.py:203-233` | 会话在册／路径剥前缀 | 见 §2 表第 9 行：只对**被退役 sid 自身**的提交路径有影响 |

自动侧唯一"会因面形状变而变"的常驻件＝**GATE-WORKTREE-LIFECYCLE**（`src/zephyr/governance/audit/reconciliation_registry.py:9260-9345`，post-commit、`_trigger` 对任何非空 commit 都真）：它调 `session_worktree_sweep(max_age_minutes=30)`，
但其枚举受 `session_worktree.py:2215` 的 `sess-` 前缀闸约束 ⇒ **`st-*` 面不在射程**（§2 第 4 行）。

**注册表册里以"会话 id/工作树路径"为条目的册**（`.aidrafts` 面 grep，catalogs 目录）：
`architecture_issue_registry.yaml:8526,9816,10052,10084,10155`、`ruling_registry.yaml:2296,2982,3510,3617,3787,4367`
——**全部是散文正文里的历史叙述**（非键值条目）；`docs/registry_of_registries.yaml` 对 `aidrafts|worktree` **0 命中**
（正对照＝同尺 `grep -c 'registry' docs/registry_of_registries.yaml` = **193**，尺未坏；`grep -c -e aidrafts -e worktree` = **0**）
⇒ ROOR 不含本面路径，**无册需要随退役改条目**。

## 4. 任务4：15 候选 sid 的悬空引用逐件表

尺：`grep -rn --include=*.yaml|--include=*.md docs/01_policies_and_standards`；`grep -rn --include=*.py src scripts tests`。
正对照＝同尺对 `st-maint3-20261011` 得 py=10（逐条见下），尺未坏。

| sid | docs/01 yaml | docs/01 md | 代码 py | 机读命中性质 |
|---|---|---|---|---|
| st-backfix-patrol-20261011 | 0 | 0 | 0 | 无 |
| st-backfix3-20261011 | 0 | 0 | 0 | 无 |
| st-cband-20261012 | 11 | 0 | 0 | 全为 `capability_canonical_file_registry.yaml` 的 `created_by:` 归属值 |
| st-deadcure3-20261010 | 5 | 0 | 0 | 同上 |
| st-deadcure3b-chief-20261011 | 249 | 0 | 0 | 同上（`created_by:`） |
| st-dexp-20261009 | 12 | 0 | 0 | `created_by:`（含 `:3756 created_by: st-dexp-20261009`） |
| st-final4-20261010 | 2 | 0 | 0 | `created_by:` |
| st-finalclean2-20261010 | 3 | 2 | 2 | 代码＝注释/测试文首：`scripts/commit_queue.py:3008`、`tests/gov/governance/test_requeue_snapshot_replay_guard.py:10` |
| st-fullflow2-20261008 | 9 | 0 | 2 | 代码＝测试 docstring：`tests/signal_ashare/source_line/test_capital_flow_direction_criterion.py:3`、`.../test_news_sentiment_criterion.py:3`；册面＝`architecture_issue_registry.yaml:9913`（owner 正文）、`ruling_registry.yaml:4249,4266`（summary 正文） |
| st-maint3-20261011 | 6 | 0 | 10 | **全部注释/测试夹具**：`src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py:8,456`、`src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py:105`、`scripts/governance/generators/generate_resource_profile_registry.py:1950`、`tests/gov/governance/{test_worktree_drift_watchdog.py:1097,test_commit_queue_landing.py:2378,2389,test_enqueue_preflight.py:434,test_pool_regression_direction_gate.py:98,test_resource_schedule_regen_check.py:189}` |
| st-minedig-20261012 | 25 | 2 | 0 | `created_by:` + md 正文 |
| st-nightmine-20261010 | 274 | 0 | 0 | `created_by:`（`capability_canonical_file_registry.yaml:7453,7463,7483,…`，值形如 `st-nightmine-20261010-L3b/L3c`）+ `trial_ledger_registry.yaml:174 recorded_by: st-nightmine-20261010` |
| st-nightmine-20261010b | 0 | 0 | 0 | 无 |
| st-nightmine2-20261010 | 3 | 1 | 0 | `trial_ledger_registry.yaml:30 recorded_by:`、`:25` note 正文 |
| st-regsolo-20261010 | 8 | 0 | 18 | 代码**全为注释/[MODIFY-GUARD] 署名**：`approval_resolver.py:218`、`registry_yaml_parse_gate.py:100`、`commit_belt_daemon.py:911`、`commit_queue_landing.py:1428,2378`、`batch_creation_tokens.py:15,24`、`register_asset.py:147` + 12 支 tests 的 `[MODIFY-GUARD]` 行；册面＝`ruling_registry.yaml:4441,4484,4527`（adjudicator 正文） |

**判读（关键区分）**：
1. **机读字段命中确实存在，但语义是"归属署名"不是"路径指针"**——`created_by:`/`recorded_by:`/`adjudicator=` 只记"谁产的"，
   不指向 `.aidrafts/<sid>` 任何字节 ⇒ 削树**不产生悬空路径**，也不违反 `REFERENCE-INTEGRITY` 类"引用须可解析"判据（这些值不是路径形态，无 `/.aidrafts/` 前缀）。
2. `capability_canonical_file_registry.yaml` 的 597 枚命中里**没有一个**以路径形态书写 sid；该册是 PG 账本的机生投影（`ruling_registry.yaml:4441` 正文自证"手改必被覆盖"），
   ⇒ **禁止为退役去手改这些 `created_by` 值**（改了也会被 render 冲掉，且属"人写正文逐字不动"红线，见 `generate_resource_profile_registry.py:1950-1953` 撤章纪律）。
3. **散文里的"去这里取件"型指针**：波三 §6.2 已记 `st-regsolo-20261010` 的 5 件 `docs/_working/regsolo_campaign/{99_delivery.md,lanes/t1..t4.md}` **仅存活于该车道**。
   本案卷补一条同型面：`tests/infra/infrastructure/test_resource_schedule_regen_check.py:189` 指向
   `.runtime/sessions/st-maint3-20261011/archive/plan_20261011T162521Z/orig/`（取证指针，属 `.runtime` 面不在 `.aidrafts` 面）；
   `scripts/governance/wave11/w178_universe_facts_gen.py:27`、`wave1b/claim_gate_repro.py:36`、`wave1b/dead_letter_prescriptions.py:1274-1275`
   的"照此命令复跑"指针指向 `.aidrafts/st-final-build-20260926`——**该目录已在盘上不存在**（ls §5），
   ⇒ 这三处已是**存量断指**，与波四候选无关，但证明"车道目录被清后复跑命令即失效"是**已发生的先例**，须在呈批里如实写。

## 5. 任务5：`.git/worktrees` 管理面（未跑 prune/repair，只报所见）

`ls .git/worktrees/` ＝ **37 枚**管理目录；`git worktree list --porcelain` ＝ **38** 条注册（含主区）；`ls .aidrafts/` ＝ **18 棵**。
（对照波三：面已从 16 变 18——新增 `st-cband-20261012`/`st-fclean4-20261012`(本班)/`st-gpux3-20261012`/`st-minedig-20261012`，
 移除 `st-deadcure2-20261009`/`st-fclean3-20261012`（二者 `ls -d` 实测 No such file，且 `.git/worktrees/` 已无其管理目录＝**已由他班走 `git worktree remove` 正规退役**）；⇒ **波三 §5 的 12 支计数是在一个已变形的面上量的**。）

**STALE（注册路径不在盘）＝1 枚**：
- `pool-20260919202729-c433` → `D:/ZephyrAlpha/.aidrafts_pool/pool-20260919202729-c433/.git`（**池树**，且 `git worktree list` 显示 `0000000000 (detached HEAD) locked`）
  ⇒ 面**已经不一致**：一棵"锁定的、HEAD 全零、物理目录消失"的池注册仍在册。它是 `worktree_pool` 的 lease 面，**不属波四候选**（见 §6），
     呈统筹单独立项；`git worktree prune` 会连 `locked` 语义一起处置，本班未跑。
其余 36 枚 ALIVE。**注意 3 枚"同名双注册"**（git 去重后缀 `1`）：
`st-finalclean2-20261010`(→`.worktrees/…`) 与 `st-finalclean2-202610101`(→`.aidrafts/st-finalclean2-20261010`)；
`st-gpux3-20261012`(→`.worktrees/…`) 与 `st-gpux3-202610121`(→`.aidrafts/st-gpux3-20261012`)；
`st-mineloop2-20261012` 与 `st-mineloop2-202610121`（后者指向 `.worktrees/st-mineloop2-20261012/.aidrafts/st-mineloop2-20261012`＝**树中套树**）。
⇒ 同一 sid 在 `.aidrafts` 与 `.worktrees` 两侧**各占一枚独立管理目录**；波三 §7 的"影子树"在管理面同样成立。

`du -sk`（仅管理目录，apparent KB）：候选与在飞 `st-*` 各 **≈2,352–2,752 KB（2.3–2.7 MiB）**；
池/序列化面则大一个数量级：`worktree`=84,425｜`w0`=27,656｜`w1`=20,000｜`w2`=15,812｜`w3`=10,400｜`pool-…`=3｜`AI-PROBE-001`=2,697。
⇒ 每退役一棵 `.aidrafts` 树，磁盘回收≈297 MiB（树）＋≈2.7 MiB（管理目录），管理面占比 <1%（波三 §9"管理面体量未量"在此补齐）。

## 6. 任务6：序列化/池基础设施树（排除集，逐条给创建者代码）

| 注册路径 | 分支 | 管理目录 | 创建/管理者 file:line |
|---|---|---|---|
| `D:/ZephyrAlpha/.runtime/commit_queue/worktree` | `serializer/commit-queue`（**locked**） | `worktree` | `scripts/governance/commit_queue_landing.py:121`（`_WORKTREE_DIR_NAME="worktree"`）+ `:1718`（默认 `queue_root/"worktree"`）；前缀归一消费方 `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py:205` |
| `.runtime/commit_queue/worktrees/w0..w3` | `serializer/commit-queue-w0..w3` | `w0..w3` | `commit_queue_landing.py:3932 def drain_queue_pool`（通道池）；`approval_resolver.py:206`（`_WT_PREFIX_PLURAL`）/`:217`（"serializer 复数通道池"）；测试复刻 `tests/gov/governance/resilience/test_evaporation_cure_lane_ev.py:116-118` |
| `.aidrafts_pool/pool-20260919202729-c433` | detached（locked，HEAD 全零，目录已不在盘） | 同名 | `src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py:106`(`_POOL_DIR_NAME`)、`:196`（idle 扫描）、`:281-282`（`git worktree move .aidrafts_pool/{pool_id} .aidrafts/{sid}`）、`:389`（prefetch n 棵） |
| `.runtime/commit_queue/worktree/.worktrees/st-map9-f6-20261005` | `ai/st-map9-f6-20261005/task-…` | `st-map9-f6-20261005` | 落地快照**内部的嵌套树**（serializer 面） |
| `.worktrees/st-maint2-20261011/.aidrafts/{AI-PROBE-001,st-cli-1}` | `session/AI-PROBE-001`、`session/st-cli-1` | 同名 | `src/zephyr/gov_enforcement/rule_bridge/worktree_manager.py:75` + `session_worktree` 创建链（宿主树本身在 `.worktrees`） |
| `.worktrees/st-mineloop2-20261012/.aidrafts/st-mineloop2-20261012` | `session/st-mineloop2-20261012` | `st-mineloop2-202610121` | 同上 |

⇒ **排除集（波四禁碰）**＝`worktree`、`w0..w3`、`pool-20260919202729-c433`、以及**任何 `.runtime/commit_queue/**` 与 `.worktrees/**` 路径下的注册项**。
另外 `scripts/session_worktree.py:735` `_ARCHIVE_ALL_EXCLUDED_MARKERS = (".aidrafts_pool", ".qoder", "commit_queue")`
给出在册"archive-all 不碰"的同一族标记 ⇒ 与本案卷排除集**逐字互证**。

**波四候选 15 sid 的落位核对**（对照 §5 的 ALIVE 清单）：15 枚全部在 `.aidrafts/` 下且各占一枚独立管理目录，
**无一**落在 `.runtime/commit_queue/**` 或 `pool-*` 或 `w0..w3`；但 `st-finalclean2-20261010` 与 `st-gpux3-20261012`
在 `.worktrees` 侧**另有同名树**（不同分支/不同 HEAD，波三 §7 已证非双存）⇒ 退 `.aidrafts` 侧时
`.worktrees` 侧同名树**不在本批**，且必须确认 remove 命中的是 `…101`/`…121` 那枚管理目录（git 按路径匹配，勿误伤同名注册）。

## 7. 残余未覆盖面（强制，如实报）

| 项 | 状态 |
|---|---|
| 尺 A 的口径边界 | 只 `--include=*.py`、ripgrep 尊重 `.gitignore` ⇒ **`.pyc`/`__pycache__` 未计**（波三 12 支含 `.pyc`）；`.ps1`/`.toml`/CI yaml 中的 `.aidrafts` 引用**未查** |
| 非 py 语言的读者 | `.ps1`（`register_resource_view_publish_task.ps1` 等在册真源）、`.json` 运行态分片、`.yml` workflow 的 `.aidrafts` 引用**未枚举** |
| `board.yaml` 的新鲜度契约 | 已证**未跟踪**，但**未证**"是否有门/巡检拿 board 的 lanes 计数当阈值断言"（只 grep 到 `commit_queue.py:3563-3565` 把它当 dead_archive/retired_dirs 消费者）。⇒ 若统筹要"同窗复跑"，此项 E1 |
| `coordination_state_board` 全量输出字段 | 只读到 `lanes` 枚举与写盘点（`:302-313/:942-948`），**未逐字段核**其余分节（queue/claims/registry_dead_dirs）是否含 `.aidrafts` 派生计数 |
| reuse_scan 的落盘面 | 只证返回值是写前告警；**未证** REUSE-SCAN 是否有历史审计 jsonl 落盘并被门读取（`reuse_scan.py:155` 之外的输出面未读） |
| `.git/worktrees` 嵌套树 | `st-mineloop2-…121`/`AI-PROBE-001`/`st-cli-1` 三枚"树中树"仅证存在与存活，**未查**其内部是否再嵌 `.aidrafts` 面（`coordination_state_board._CANDIDATE_MARKERS` 只扫主根三层，嵌套面可能不被它看见） |
| prune 语义 | 未跑（红线）；`pool-20260919202729-c433` 的 `locked` 原因、由谁 lock（`git worktree lock` 写 `locked` 文件）未追 |
| 15 候选 sid 的 `docs/_working/**` 台账指针 | **未逐枚读**"取件指针"语义（本案卷只覆盖任务4要求的 docs/01+代码两面；波三 §5 的台账计数是上一班口径，已在变形面上过时） |
| 面漂移 | 本卷所有计数钉在 2026-10-12 现读（`ls .aidrafts`=18 / `git worktree list`=38）；在飞班随时增删树 ⇒ 复算先重取三数 |
| 本班写动作 | **零**（唯一写出＝本文件 + `out/` 无机读表：所有表以本文内联，避免生成器/清单漂移，根宪法 §9.5） |
