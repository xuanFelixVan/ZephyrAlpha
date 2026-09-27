---
ttl: task_bound
completes_when: 1.3/1.6/1.7/1.7b/1.7c 五包代码就位、五把红证 canary 跑红、既有队列用例 before/after 计数在册且无退化
---

# 波 1B · 提交链解毒施工案卷（chain_detox_report）

turn_budget: 计划 34 次工具调用；**实测超支至 ~80**（超支主因：1.7b 后继重建被 B5 队首让位语义反噬的排障 6 次、
before/after 计量用「临时回退 HEAD 再复原」法跑了两轮、一次后台任务与前台改码竞态导致 1 次文件回滚复原）。
如实登记：超支未换来额外范围，五包范围与本包授权一致，未扩面。

verified（E1 直读，命令可复跑）：
- Python 3.12.8（`python --version`，非 TRAE 注入的 3.10）。
- priority 真源：`gate_auto_registrar.py:54-55` 明写「priority 从 GateSpec 读取，YAML 的 priority 仅 informational」
  ⇒ 波 1B 1.3 行「两册条目根本无 priority 字段（真源=GateSpec）」**复算成立**。
- 实载层聚合台↔吸收台同号 6 簇（逐台 `_cyclomatic_complexity` 无关，逐台读 GateSpec 现值）：
  DOC-HEADER-SUITE=77↔BLUEPRINT-FORMAT=130（X-02 判定他道已修，本包未碰）、
  REFERENCE-INTEGRITY=70↔DANGLING-REFERENCE=70、COMPLEXITY-GUARD=92↔NO-HIGH-COMPLEXITY=92、
  PERMANENT-SYSTEM-TRIGGER=82↔PERM-TRIGGER=82、GATE-VOCAB=80↔VOCAB-HARDCODE=80、
  DEPGRAPH-ENFORCEMENT=113↔DEPGRAPH-PRE-REGISTRATION=113、MAP-ALIGNMENT=141↔GATE-PANORAMA-ALIGNMENT=830（不同号）。
- 五把红证 canary：`29 passed`（命令原文见下文 evidence_ref.cmd §五）。
- 既有队列/网关用例 before/after 逐文件计数：**零退化**（§六全表）。
- 新函数复杂度：本包全部新函数 cc≤13、参数≤5（用门禁自家 `high_complexity_gate._cyclomatic_complexity` 复算）；
  被改的既有函数 cc 增量为 `requeue_dead_item 39→42`、`enqueue_item 25→25`、`drain_queue 29→28`、
  `_cmd_enqueue 23→21`、gateway 三读点 `5→2 / 2→2 / 2→2`（**未调任何阈值**）。
- 盘上零触碰禁改件：`config/flags.yaml`、`config/search_space_prereg.yaml`、`exam_scale_cost_prereg*`、
  `exam_scale_cost_gate.yaml` 均**未被本包写入**（`git diff --stat` 只列本包四件既有件，见 §一）。

assumed（转述/未独立复算，禁当实证引用）：
- 「实测 pending=0 / dead≈700」——X-55 已判定该读数会漂且要求带取数时刻；本包**未读生产队列**（硬约束禁拿生产队列演），
  1.7b 现状「整链停摆」的量化只引用 A 册/10 册口径，不由本包复证。
- 「CREATE-GUARD 缺 token 类实测 8 封死于该因」——引 10_wave_plan.md:68（波 2.1 行）与 X-01，本包未逐封复核。
- 「requeue 是 envelope 唯一丢失点」等 M1.3 描述——引 commit_queue.py 内既有注释，未独立复算。
- 1.6 中「`gate_precommit_run_enabled` 实际不在 flags.yaml 册面」为**本包实测**（见 §三 缺口 G-1），
  但其后果（该门在网关通道是否真在跑）未复算，只登记不定性。

input_set_disjoint_with: 本包输入集=波 1B 表 1.3/1.6/1.7/1.7b/1.7c 五行 + X 册（唯一口径）+ A 册 +
  `review_ext_ci_and_mergequeue.md`（1-1/1-2/1-7/3-1/D-08）+ 四件代码真源。
  与 1.1（四台禁用定性）/1.2（同 id 双条册）/1.4（锚点漂移）/1.5（CREATE-GUARD 触发面）/1.8（未入库件捞回）
  五行**不交**，未触碰；与波 1A（tasks 表迁移）、波 2（存量抢救）不交。

evidence_ref.cmd: 见本文 §五（逐包红证命令原文 + 实测读数）、§六（before/after 全表）。

---

## §一 逐件清单（本包写盘的全部文件，均在车道内真实路径）

既有件修改（4）：
1. `scripts/commit_queue.py` — 1.7（预检唯一漏斗 `_enqueue_preflight_scan_needed`/`_apply_enqueue_preflight`
   + `EnqueueOptions.preflight_root/enqueue_preflight` 两字段）+ 1.7b（`_successor_affected_by`/
   `_rebuild_successors_after_eviction`/`_seal_dead_letter` 接两处死信出口）+ 1.7c
   （`dead_signature`/`_iter_signature_recurrences`/`_ticket_merge_priors`/`_write_root_cause_ticket`/
   `_seal_dead_letter_attribution`/`_fuse_dead_letter_recurrence`/`_assert_recurrence_not_fused`）。+318 行。
2. `scripts/git_commit.py` — 交互正门 `--enqueue` 直调补 `preflight_root=str(wt)`（第三条旁路）。+3 行。
3. `scripts/governance/commit_queue_landing.py` — reroute 通道显式 `enqueue_preflight="skip"`（上方已自跑预检，
   skip 位的**唯一**合法使用者）。+3 行。
4. `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py` — 三处旗标读取唯一点改走三态尺
   （`_immutable_tree_enabled`/`_commit_queue_serializer_enabled`/`_precommit_run_enabled`）。±58 行。

新建件（2 源件 + 5 测试件 + 2 案卷）：
- `src/zephyr/gov_enforcement/rule_bridge/union_priority_ruler.py`（1.3 断言尺 + 设计内同值白名单）
- `src/zephyr/shared/foundation/flag_read_state.py`（1.6 三态读尺 + 读红台账）
- `tests/gov_enforcement/test_union_priority_canary.py`
- `tests/gov_enforcement/test_flag_tri_state_canary.py`
- `tests/governance/test_enqueue_preflight_bypass_canary.py`
- `tests/governance/test_dead_letter_eviction_canary.py`
- `tests/governance/test_dead_letter_ownership_canary.py`
- `docs/_working/total_command_closeout/wave1b/chain_detox_report.md`（本件）
- `docs/_working/total_command_closeout/wave1b/registration_needs.yaml`（机生登记需求册，交总包）
- ⚠ `tests/governance/test_enqueue_preflight_bypass_canary.py.tmp`：一次被中断的 Write 留下的**占位注释文件**
  （无代码、无消费者；施工队按「禁任何删除动作」未删，已登记 registration_needs.yaml 的 stray_artifacts 节）。

---

## §二 包 1.3 · priority 撞号断言尺（聚合台↔吸收台同号禁令）

改了什么：新建 `union_priority_ruler.py`——`AGGREGATE_ABSORBS_SOURCES`（6 对设计内同值白名单，**只记身份不记号数**）
+ `find_loaded_union_collisions` / `assert_no_union_priority_collisions`（尺）+ `undeclared_code_layer_equalities`
（漂移反查：新聚合台与留档源台同号但未登记 ⇒ 点名）。
为什么：波 1B 1.3 实测口径=实载层 0 簇、代码层 6 簇全是「源台+聚合台 `_union_check`」同值对（2 簇靠
`enabled:false` 才不并存，即 X-12 点名的 GATE-VOCAB / PERMANENT-SYSTEM-TRIGGER）。故**不动任何数值**，
只补尺 + 把 6 对显式注因（逐条行内注因，含 X-02 判定「BLUEPRINT-FORMAT 77↔130 互换作废、以 HEAD 为准」）。
白名单不记号数的理由：记了就成第二真源（RULE-SSOT），号数一律由测试现场从 `GateSpec` 工厂读出。
红证命令原文+读数：
```
python -m pytest tests/gov_enforcement/test_union_priority_canary.py -q --no-header
→ 6 passed
```
（`test_canary_human_forced_same_priority_must_turn_ruler_red` 人为让 REFERENCE-INTEGRITY 与
DANGLING-REFERENCE 实载同号 70 ⇒ 尺红且消息点名两台与号数；`test_canary_every_pair_turns_red_when_both_loaded`
逐对复算 6/6 全红；`test_real_loaded_layer_has_zero_union_collision` 证明今日实载 0 簇＝正向路径不误伤。）
before/after：该目录 before=51 passed（本包新建件未落盘时）→ after=66 passed（+6 尺件，0 退化）。
缺口：见 §七 G-2、G-3。

## §三 包 1.6 · flag 三态读（Z-10）

改了什么：新建 `flag_read_state.py`：`FlagReadOutcome{ON/OFF/UNREADABLE}` + `read_flag_state`（区分
「册/设施坏」与「册可读但无此键」两种读不到，各自返回调用点**改前既有**的缺省值）+ `report_flag_red`
（ERROR 点名旗标名 + 落 `.runtime/gate_audit/flag_read_red.jsonl` 台账，写失败仅 warning 绝不堵链）
+ `read_commit_chain_flag`。网关三读点的 `try/except: return False` 两态降级被本件**吸收**（内收声明见文件头）。
为什么：Z-10=读到 ON/读到 OFF/读不到被压成两态，读失败当 OFF 静默降级；对标册 D-08 指出我方只到「报红点名」
未到 safe-halt（本包按授权只做点名报红，**未**新增停机——停机策略属另一裁）。
关键约束遵守：**未改 config/flags.yaml 一字**（`git diff --stat` 无该件）；三态只补可见性，
每点返回值逐位保持改前（含 `_precommit_run_enabled` 的 `missing_key_value=True`，即改前 `default=True` 语义）。
施工中发现并修掉的自造坑（同一包内，不另计范围）：`_lookup` 首版用真值判断，会把合法值 `false` 误判成
「读不到」——已改哨兵 `_MISS/_FOUND`（`immutable_tree: false` 现读为 OFF 非 UNREADABLE，红证覆盖）。
红证命令原文+读数：
```
python -m pytest tests/gov_enforcement/test_flag_tri_state_canary.py -q --no-header
→ 9 passed
```
（三个坏册形态 bad_yaml / root_not_mapping / missing_flags_section 全部判 UNREADABLE、caplog 点名旗标、
台账可查、返回值仍为缺省；`test_real_flag_book_reads_without_red` 用真源册自证正向不误红。）
缺口：§七 G-1（**新病，未动手**：`_PRECOMMIT_RUN_FLAG = "gate_precommit_run_enabled"` 而册面顶层键是
`gate_precommit_run`（flags.yaml:109），注册表按顶层键注册 ⇒ 该旗标**永不命中**，改前被 `default=True` 静默
兜成 ON；本包三态尺现在每读必报红点名，但**未改常量名也未翻值**（改名=动门禁执行面，属另一裁）。

## §四 包 1.7 · 入队预检旁路封堵

改了什么：预检执行点从裸 CLI `_cmd_enqueue` **下沉到唯一漏斗 `enqueue_item`**（一处实现，三处受益）；
`EnqueueOptions` 新增 `preflight_root`（预检根）与 `enqueue_preflight`（"auto"/"skip"）。
`requeue_dead_item`（点名旁路①，同时保留其既有冲突标记扫）与 `git_commit.py --enqueue` 交互正门（旁路②）
都交根进闸；`commit_queue_landing` reroute 通道显式 `skip`（上方已自跑 `run_preflight`，避免同袋二次全门扫描）。
不扫的两种情形写死：未声明根、或根非 git 工作区（⇒ tmp 隔离测试与纯 API 直调**零行为变更、零额外耗时**）。
为什么：三条入队通道同一道预检，杜绝「注定死信的单子入袋白烧锁内窗口」（X-01：六图役 8 封死于 CREATE-GUARD）。
红证命令原文+读数：
```
python -m pytest tests/governance/test_enqueue_preflight_bypass_canary.py -q --no-header
→ 4 passed
```
（直调 `enqueue_item` 投缺 creation_token 新文件 ⇒ `QueueReject` 且 pending 零落袋；`requeue_dead_item` 直调
重投同件 ⇒ 同一道闸拦下且 pending 零新增；`skip` 位必须显式声明才放行；未声明根/非 git 根不扫＝正向路径自证。
本包用替身 `commit_preflight.run_preflight` 做确定性红证——CREATE-GUARD 真门是全树 git grep 分钟级且写审计，
禁在沙盘外真跑，替身只替权威判定、不替挂线本身。）

## §五 包 1.7b · 失败摘除 + 后继袋重建（与 B5 合并）/ 1.7c · 死信属主制 + 复发熔断

1.7b 改了什么：`_rebuild_successors_after_eviction`——袋进 dead 后，对**排在其后**且「叠在死者上」的 pending 袋
写既有矿③ stale 影子指令（`_write_stale_shadow`），令其拾取时经既有 `_revalidate_stale_base` 按**不含失败者的新组合**
重跑：仍适用→清标放行照常落地，不适用→具名死因 `cascade_stale`。受影响判据保守取二：
`meta.depends_on` 含死者 qid，或与死者共享文件路径（我方 Merge-Train「叠在它上面」的实形）。
**两处死信出口共用同一个 `_seal_dead_letter`**：`result.ok==False` 死信分支 + B5 attempts 耗尽摘除分支
（`_ATTEMPTS_DEAD_THRESHOLD=5`、`_REQUEUE_CIRCUIT_LIMIT=3` **一字未改**）。drain 新增可观测计数
`stats["successors_rebuilt"]`。
为什么：对标册 1-2（GitLab Merge Trains「某一节失败即摘掉，其后各节流水线重跑以反映新组合」）、
1-7（Zuul gate「失败者摘除，其后叠在它上面做过投机测试的变更重新入队、按不含失败者的新组合重建」）、
1-1（GitHub Merge Queue「移出队列，其余 PR 末态通过即继续落地」）三家同构；我方现状是「失败者归档 +
后继袋仍拿旧累积快照」。内收：不新造机制，全部复用影子通道/重校验/处方表，**合并进 B5 同一出口**。

1.7c 改了什么：`_seal_dead_letter_attribution` 每封死信落 `owner_session` + `first_dead_at` +
`dead_signature`（=`classify_dead_reason(reason)` + 首个门禁/异常 token）+ `dead_letter_family`；
`first_dead_at` 经 `meta.requeue_lineage.first_dead_at_prev` 跨重投链继承（不回退到重投时刻）；
同签名 ≥3 次 ⇒ `_fuse_dead_letter_recurrence` 置 `recurrence_fused` 并写**根因工序单**
`<queue_root>/dead_recurrence/<签名>.json`（含属主集合/首死时/复发链 qid/处方），
`requeue_dead_item` 对熔断裂直接拒投（`--force` 仍留痕越过）。
为什么：对标 3-1（Build Cop「keeping all the tests passing…regardless of who breaks them」=死信是当天必须有人
中断工作去修的活信号）；我方 R-3 曾把「需属主」态主动废成「代投」，代投把「谁弄坏的」只留在 message 里，
复发无人被叫醒；且既有 `owner_session` 只在 landing-failure 分支手写、attempts 耗尽分支**缺**（本包合并补齐）。

红证命令原文+读数：
```
python -m pytest tests/governance/test_dead_letter_eviction_canary.py -q --no-header   → 4 passed
python -m pytest tests/governance/test_dead_letter_ownership_canary.py -q --no-header  → 6 passed
```
1.7b 读数细节（重要，防后人重踩）：`_pick_head` 的 B5 让位会给毒药件加**未来时刻偏移**，故真实 drain 里
毒药件总是最后被拾取——它身后**已无袋**，`successors_rebuilt=0` 是**正确读数**（链未停摆、毒药件未再消耗 landing）。
因此该测分两段取证：①drain 面证明「不再白耗 landing + 后继袋照常落地」；②封袋出口面直接调
`_seal_dead_letter` 证明「身后有袋时必须重建」（`test_poison_eviction_shares_the_same_exit`）。
主红证 `test_chain_survives_a_dying_bag_and_successors_rebuild`：一袋必死 → `dead=1 / done=2 / successors_rebuilt=1`，
且同路径后继袋 done 项带 `meta.stale_cleared_at`（走过一次按新组合重校验），无关系袋零牵连。
人为改错→尺必红：`test_canary_mutation_disabling_rebuild_turns_ruler_red`（摘掉重建出口 ⇒ 计数归零、
痕迹消失，尺当场失配即红）；`test_predecessors_are_never_marked`（不得扩大动作面）。
1.7c 人为改错→尺必红：`test_canary_mutation_disabling_attribution_turns_ruler_red`（不封袋 ⇒ 三字段当场查无）；
`test_fused_bag_rejects_blind_requeue`（熔断裂直调 requeue 必拒且 pending 零偷渡）；
`test_signature_distinguishes_different_root_causes`（异签名不得顶数，防误伤无辜袋）。
全部在 tmp_path 沙盘演，生产队列根 `.runtime/commit_queue` 零写入。

## §六 既有队列/网关用例 before/after 全表（逐文件跑，禁一次全量收集）

before=同盘临时回退四件既有件到 HEAD（新件保留、新 canary 排除）实测；after=本包改后。

| 用例文件 | before | after | 判定 |
|---|---|---|---|
| tests/governance/test_commit_queue.py | 85 passed | 85 passed | 无退化 |
| tests/governance/test_commit_queue_b5_backoff.py | 14 passed | 14 passed | 无退化（B5 合并后阈值语义不变） |
| tests/governance/test_commit_queue_base_head.py | 23 passed | 23 passed | 无退化 |
| tests/governance/test_commit_queue_c1_debounce.py | 21 passed | 21 passed | 无退化（preflight_root 与 worktree_root 分离，C1 判据键未被牵动） |
| tests/governance/test_commit_queue_ghost_pending.py | 15 passed | 15 passed | 无退化 |
| tests/governance/test_commit_queue_integration.py | Timeout | Timeout | **两态同形=既有环境病**（车道缺 governance.db/真 worktree 设施），非本包引入 |
| tests/governance/test_commit_queue_landing.py | 1 failed, 69 passed | 1 failed, 69 passed | 同一条既有红点，计数等值 |
| tests/governance/test_commit_queue_landing_nightfix.py | 9 passed | 9 passed | 无退化 |
| tests/governance/test_commit_queue_landing_qcure_m5.py | 14 passed | 14 passed | 无退化 |
| tests/governance/test_commit_queue_landing_qmine_a1.py | 20 passed | 20 passed | 无退化 |
| tests/governance/test_commit_queue_pool.py | 15 passed | 15 passed | 无退化 |
| tests/governance/test_commit_queue_snapshot_selfconsistency.py | 7 passed | 7 passed | 无退化 |
| tests/governance/test_enqueue_preflight.py | 1 failed, 38 passed | 1 failed, 38 passed | 同一条既有红点（`TestCmdEnqueueWiring::test_blocking_exit2_no_bag_written`，`assert 0 == 2`），两态等值 |
| tests/gov_enforcement/（整目录一次跑） | 66 passed（含本包新 2 件共 15 条）⇒ 既有 51 | 66 passed（同口径）⇒ 既有 51 | 无退化（既有部分两态等值） |
| **合计（可判定的 12 个队列件）** | **321 passed / 2 failed** | **321 passed / 2 failed** | **零退化** |
| 本包新五件 canary | — | 29 passed | 新增 |

统一复跑命令（逐目录/逐文件，禁全量收集；两旗成对，遇 INTERNALERROR 按 X-41 去 `-p no:cacheprovider`）：
```
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
export PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src
python -m pytest tests/gov_enforcement/test_union_priority_canary.py \
  tests/gov_enforcement/test_flag_tri_state_canary.py \
  tests/governance/test_enqueue_preflight_bypass_canary.py \
  tests/governance/test_dead_letter_eviction_canary.py \
  tests/governance/test_dead_letter_ownership_canary.py -q --no-header
# 合计 29 passed
```
五包各自的单把红证命令原文见对应小节（§二～§五，每节一条可复跑命令）。

## §七 【缺口】节（只登记，不动手，交总包）

- **G-1（1.6，成立）** `git_commit_gateway.py:381` `_PRECOMMIT_RUN_FLAG = "gate_precommit_run_enabled"`
  与 `config/flags.yaml:109` 的顶层键 `gate_precommit_run` **不同名**；`load_flags_from_yaml` 只注册顶层键
  ⇒ 该旗标永不命中注册表，改前被 `default=True` 静默兜成 ON。本包三态尺现每读必报红点名，
  **未改常量名/未翻值**（改名＝动裁定#341 门的执行面，属 Owner 门位或另裁）。
  副作用登记：本包落地后，每次走网关提交会多一条 `[flag-tri-state]` ERROR + 一行读红台账（这是尺该红的红）。
- **G-2（1.6，同类病）** `_immutable_tree_enabled` 改前用 `Path(__file__).parents[3]` 求仓根 =
  `<repo>/src` ⇒ 它读的其实是 `src/config/flags.yaml`（不存在）⇒ 一直走 `except` 静默 OFF。
  本包改走三态尺后读的是真册（值仍 false=OFF，返回值零变更）。旧形态属「读不到当 OFF」的实锤个案，留案取证。
- **G-3（1.3）** `gate_registry.yaml`（全目录册 181 台）与 `in_process_gate_registry.yaml`（进程内 103 台）
  两册条目确无 priority 字段（X-51 三口径同族），故「聚合台↔吸收台」关系目前**只能由代码内白名单承载**；
  若将来要在册面表达吸收关系，须先解决 X-51 的三本数对象不同问题，否则会造第二真源。
- **G-4（1.7b）** `LandingEnvironmentError`（环境失败）分支按既有语义**整轮终止且不死信**，本包未接后继重建
  （环境性失败非「失败者摘除」，接上去会让 700 封级联标脏）。此边界与既有 B5/2026-09-10 死信事故治本一致，
  但**意味着 R-L 的「后继重建」只覆盖 item 性死亡 + attempts 摘除两出口**，呈报口径须按此收窄。
- **G-5（1.7b/1.7c）** 后继重建与复发计数都只在**单写者 lease 内**读 pending/dead；pool 车道（
  `test_commit_queue_pool.py`）的死亡出口是否全部经本封袋面，本包未逐出口核（观察项，未改）。
- **G-6（计量法）** before/after 的 before 态是用「临时 `git show HEAD:<f>` 覆盘再复原」测得，
  期间一次后台任务与前台改码竞态导致 `commit_queue.py` 一度被旧备份覆盖（已按 sha256 比对发现并复原，
  随后 29 把 canary 复跑通过）。教训：**同类计量禁并发跑**，建议总包把该计量固化为一次性前台脚本。
- **G-7（新发现，未动）** `test_commit_queue_integration.py` 在本车道两态同形 Timeout（>200s）——
  车道缺 `data/databases/governance.db` 等被 ignore 的库，波 1B「出口判据」若依赖该件需先声明车道可用性。

## §八 内收与净零自查（宪法 §4）

- 新增源件 2、吸收既有实现面 3（网关三处两态降级读法）+ 手写封袋字段 2 处（收敛进 `_seal_dead_letter`）。
- 未造第二真源：priority 仍只在 GateSpec；旗标值仍只在 flags.yaml；死因分类/处方仍用既有函数；
  后继重建仍用既有影子通道与既有重校验函数，未新增状态目录语义（`dead_recurrence/` 与 `.stale/` 同为
  点前缀/非四态旁路目录，不进 glob("q-*.json") 视野）。
- 阈值零改动：`_ATTEMPTS_DEAD_THRESHOLD=5`、`_REQUEUE_CIRCUIT_LIMIT=3`、COMPLEXITY>15、
  死信爆发阈值、`config/flags.yaml` 全部一字未动。
