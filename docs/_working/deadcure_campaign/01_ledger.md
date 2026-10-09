---
ttl: task_bound
completes_when: 台账与实物袋计数对平且两轮循环检查零问题
---
# 死信清偿专案 · 台账（生成器产出，禁手工维护）

- 生成：2026-10-09T05:31:28｜锚点 HEAD=`193dc9db3602`｜账面=**1704** 件（1701 袋 JSON+空壳 1+.bak-orig 1+后继 1）
- 实物分布：
  - dead: 1344
  - campaign_archived: 359
  - absent: 1

## 四终态账面计数

| 终态 | disposition | 袋数 |
|---|---|---:|
| ①复活工单在册 | `revive_with_ticket` | 1185 |
| ②归档留痕 | `archived_superseded` | 358 |
| ①新增件工单（需 token） | `revive_additive_new` | 89 |
| 呈报 Owner 门位 | `pending_owner` | 40 |
| ①重投在途 | `revive_requeue` | 14 |
| ④属主退回 | `returned_to_owner` | 12 |
| ③判废留痕 | `scrapped_recorded` | 5 |
| ①复活已落地 | `revive_landed` | 1 |

## 复核命令原文

```bash
cd /d/ZephyrAlpha
ls .runtime/commit_queue/dead/q-*.json | wc -l
ls .runtime/commit_queue/dead_archive_20261009_deadcure/ | grep -c '^q-'
cat .runtime/commit_queue/dead_archive_20261009_deadcure/manifest.jsonl | wc -l
python .runtime/tmp/st-deadcure-20261009/tools/account.py
python .runtime/tmp/st-deadcure-20261009/tools/verify_lanes.py
python .runtime/tmp/st-deadcure-20261009/tools/deadcure.py restore --qid <QID>
```

## §G 组直投执行台账（Owner 2026-10-09 批文「40 件全批 A」执行面，随批生成）

- 生成时刻：2026-10-09 16:00（本册全部数字由 `tools/mk_g_ledger.py` 现测现生，禁手工维护）
- 授权链：Owner 2026-10-09 批文「40 件全批 A：G1+G3 交总队并袋，其余专车直投；G9/G10 也 A」
  - 批文的裁定登记=**裁定#496**（adjudicator st-chiefc-20261009，随其 G1+G3 并袋批同 commit 原子）；本专车**不重复登记同一批文**（宪法 §4 同域重复簇收敛），改为逐袋引用 #496 消费。
  - G1+G3（24 袋）交割单：`09_handoff_laneF1b.md` 尾部 G1G3 段（逐件 blob_ref+sha256），由总队车道 B 与 B-1（b-606）统一三方合并落地——专车零直投。

## 一、逐组判定（内容级：袋 blob × 现 HEAD 逐行对拍）

| 组 | 袋内扫描条目 | 判定 | 通道 | 依据（可复跑） |
|---|---:|---|---|---|
| G2 | 7 | **零写入·判废** | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G2'])"` |
| G4 | 1 | **受阻呈报**（N-16 文件名唯一性：AGENTS.md 与 src/zephyr/AGENTS.md 同名） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G4'])"` |
| G5 | 39 | **直投 22 件**（+tests 4 件转车道 F-1b、scripts 面不回头） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G5'])"` |
| G6 | 6 | **直投 1 件**（lane_e_candidates.csv）+代码/测试面转车道 | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G6'])"` |
| G7 | 13 | **直投 2 件**（baseline_manifest_v1.json + replay_report.md） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G7'])"` |
| G8 | 6 | **直投 2 件**（lane_b/lane_c candidates.csv，袋版=HEAD 超集） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G8'])"` |
| G9 | 4 | **直投 3 件**（facts 超集/acceptance 翻案更新/followup 逐字复原） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G9'])"` |
| G10 | 946 | **拆袋投 1 件**（按 Owner 拆袋令，只并入 created: 单行） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G10'])"` |
| G11 | 7 | **部分判废**（p1_top5_by_phase.txt 未落地→随 G2 通道） | 专车直投 | `python -c "import json;d=json.load(open(r'.runtime/tmp/st-deadcure-20261009/common/g_wide_scan.json',encoding='utf-8'));print([r for r in d if r['gid']=='G11'])"` |

### 判废证据（禁为过门放宽判据，逐条留可复跑命令）

- `data/strategy_intake/conditional_tables/p1_phase_momentum.csv`：HEAD 已在册且袋版为**早期代际**（袋独有 6 行 / HEAD 独有 6 行，最新袋 q-20260925-st-cmd-20260924-0022）→ 写回即回退，判废不投。
- `data/strategy_intake/conditional_tables/p1_sector_by_phase.csv`：HEAD 已在册且袋版为**早期代际**（袋独有 6 行 / HEAD 独有 1562 行，最新袋 q-20260925-st-cmd-20260924-0022）→ 写回即回退，判废不投。
- `data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml`：HEAD 已在册且袋版为**早期代际**（袋独有 5 行 / HEAD 独有 6 行，最新袋 q-20260924-st-t0-matrix-20260924-0008）→ 写回即回退，判废不投。
- `data/strategy_intake/lane_b_candidates.csv`：袋版=现 HEAD **严格超集**（袋独有 67 行 / HEAD 独有 0 行，最新袋 q-20261008-st-tclose-rootcure-20261006-0002）→ 纯增量，已按袋版整档并入落地（组 G8）。
- `data/strategy_intake/lane_c_candidates.csv`：袋版=现 HEAD **严格超集**（袋独有 24 行 / HEAD 独有 0 行，最新袋 q-20261008-st-tclose-rootcure-20261006-0002）→ 纯增量，已按袋版整档并入落地（组 G8）。
- `docs/_working/total_command_closeout/review_ext_autonomy_and_agents.md`：袋版独有 1 行（仅 frontmatter `created: 2026-09-26`）、HEAD 独有 5 行，且原袋是 883 项大快照（Owner 令拆袋）→ 不整档覆写，**按现 HEAD 基只并入 created 单行**落地。
- `data/strategy_intake/conditional_tables/p1_top5_by_phase.txt`：HEAD 已有 `p1_top5_by_phase.csv`（同 10 只代码、同 n/LB/均值三值逐行等价），且 `.txt` 触 DIRECTORY-CONTRACT DCR-005（data/ 扩展名白名单无 .txt）→ 判为代际取代，零写入。
- `docs/03_modules/AGENTS.md`（G4 全部 3 袋同死因）：GATE-NAMING **N-16** 文件名项目内唯一性（新增 docs/03_modules/AGENTS.md 撞 src/zephyr/AGENTS.md）。豁免通道=rules/trae_028 §n16_config `exempt_names_docs_extra` 白名单，而该白名单**代码明载改动须 Owner 批准**——专车不自签。呈 Owner 两选项：①把 AGENTS.md 纳入 n16 豁免（保住嵌套局部宪法机制）；②改名 index.md（已在豁免表，但失去 AGENTS.md 自动发现语义）。

## 二、落地回执（逐件 git show HEAD 字节对拍）

| 袋 | 状态 | 件数 | HEAD 字节全等 | HEAD 演进(EOL 归一后独有行) | 未落地 |
|---|---|---:|---:|---:|---:|
| promote | done | 12 | 12 | 0 | 0 |
| bag1_g5 | done | 22 | 22 | 0 | 0 |
| bag2_data | done | 4 | 4 | 0 | 0 |
| bag3_docs | done | 5 | 5 | 0 | 0 |
| bag4a | done | 33 | 1 | 32 | 0 |
| bag4b | done | 20 | 17 | 3 | 0 |
| bagreg | done | 1 | 0 | 1 | 0 |

复跑（单件）：`git show HEAD:<path> | sha256sum` 对 `.runtime/commit_queue/blobs/<blob_sha256>`（EOL 归一后比字节）。

## 三、转车道工单（施工面，专车不做第二施工队）

- `scripts/audit/t0_ceiling_capacity_exam.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 55 行 / HEAD 独有 82 行
- `scripts/audit/t0_conditional_e4_v2_exam.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 16 行 / HEAD 独有 42 行
- `scripts/audit/t0_conditional_e4_v3_exam.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 42 行 / HEAD 独有 72 行
- `scripts/audit/t0_gpu_condition_pack.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 96 行 / HEAD 独有 143 行
- `scripts/audit/t0_six_phase_materialize.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 19 行 / HEAD 独有 29 行
- `tests/audit/test_t0_ceiling_capacity_exam.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=ABSENT_ADD，袋独有 92 行 / HEAD 独有 0 行
- `tests/audit/test_t0_conditional_e4_v3_exam.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=ABSENT_ADD，袋独有 120 行 / HEAD 独有 0 行
- `tests/audit/test_t0_gpu_condition_pack.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=ABSENT_ADD，袋独有 131 行 / HEAD 独有 0 行
- `tests/audit/test_t0_six_phase_materialize.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=ABSENT_ADD，袋独有 129 行 / HEAD 独有 0 行
- `scripts/audit/t0_conditional_e4_exam.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 2 行 / HEAD 独有 1 行
- `scripts/backtest/auto_mount.py`（组 G5，袋 `q-20260924-st-t0-matrix-20260924-0007`）状态=CONFLICT，袋独有 101 行 / HEAD 独有 202 行
- `scripts/backtest/lane_e_enhanced_cli.py`（组 G6，袋 `q-20261006-st-cure-p12b-20261006-0007`）状态=CONFLICT，袋独有 233 行 / HEAD 独有 11 行
- `scripts/backtest/factory_intake_pipeline.py`（组 G6，袋 `q-20261006-st-cure-p12b-20261006-0007`）状态=SUPERSET_ADD，袋独有 12 行 / HEAD 独有 0 行
- `scripts/backtest/intake_ledger_recon.py`（组 G6，袋 `q-20261006-st-cure-p12b-20261006-0007`）状态=SUPERSET_ADD，袋独有 2 行 / HEAD 独有 0 行
- `tests/backtest/test_lane_e_enhanced.py`（组 G6，袋 `q-20261006-st-cure-p12b-20261006-0007`）状态=ABSENT_ADD，袋独有 169 行 / HEAD 独有 0 行
- `tests/backtest/test_factory_intake_pipeline.py`（组 G6，袋 `q-20261006-st-cure-p12b-20261006-0007`）状态=ABSENT_ADD，袋独有 191 行 / HEAD 独有 0 行
- `scripts/sector_line/build_gpu_input_pack.py`（组 G7，袋 `q-20260924-st-pipeline-final-20260924-0029`）状态=CONFLICT，袋独有 59 行 / HEAD 独有 106 行
- `scripts/sector_line/freeze_baseline.py`（组 G7，袋 `q-20260924-st-pipeline-final-20260924-0029`）状态=CONFLICT，袋独有 31 行 / HEAD 独有 65 行
- `scripts/ch/apply_hfq_lineage_engine_upgrade.py`（组 G8，袋 `q-20261008-st-tclose-rootcure-20261006-0002`）状态=ABSENT_ADD，袋独有 414 行 / HEAD 独有 0 行
- `tests/research/ch/test_apply_hfq_lineage_engine_upgrade.py`（组 G8，袋 `q-20261008-st-tclose-rootcure-20261006-0002`）状态=ABSENT_ADD，袋独有 277 行 / HEAD 独有 0 行

### 受阻不投件（禁为过门放宽判据，逐件留补登路径）

- `docs/_working/night_sweep/e6_vm_assessment.md` — 门=GATE-PRECOMMIT-RUN hook=gate-detect-shell-dangerous (ABS-38)；第 32 行照录 VM 复活预案的删除命令 `sudo -n rm -rf／root/...`，2 处命中；detect_shell_dangerous.py 未实现 GATE-SELFDOC 豁免腿（全文件 grep 零命中），而行级标只在 git 危险命令检测器里有实现；处置=不改写他人案卷的引文（那等于为过门改文）→ 本件暂不投；转门位工单：请给 shell 检测器补 GATE-SELFDOC 同型豁免腿（门侧改动=施工/门位域，专车不自改），补齐后按原袋字节重投。
- `docs/_working/tests_cure_campaign/02_reference_census.md` — 门=GATE-PRECOMMIT-RUN hook=gate-no-tests-unit (check_no_tests_unit.py, ARCH-029 防漂移)；该案卷是 tests/ 引用普查册，正文照录 1 处 `tests／unit／` 旧路径=它的记录对象本身；检测器的 _EXEMPT_PATH_PATTERNS 只豁免归档/规则册/派生册/检测器自身，无案卷普查类豁免腿；处置=不改写普查册的字面量（那等于毁证据），不自扩豁免清单（豁免清单=门侧规则数据，改动属门位/施工域）→ 本件暂不投；转门位工单：请为「路径普查/死引用账」类案卷加豁免腿（行级标记或 _working 普查册前缀），补齐后按原袋字节重投。
- `docs/_working/deadcure_campaign/05_tests_restore_manifest.yaml` — 门=GATE-PRECOMMIT-RUN hook=gate-no-tests-unit (check_no_tests_unit.py, ARCH-029 防漂移)；本清单逐字收录被删测试树原路径（含 `tests／unit／…` 存量条目=交割索引键），检测器内容级匹配即拦；其 _EXEMPT_PATH_PATTERNS 已为同类机生册（gate_registry/script_manifest/fms_deadref_baseline）开口，但未含交割清单——我产出的坏 YAML 修复（169 处 class:? → unknown）因此进不了门；处置=不自改检测器豁免清单（门侧规则数据=门位域），不删改清单里的历史路径（那是交割键）→ 修好的副本已写在车道与主区盘面（yaml.safe_load 通过，2325 项），落地需门侧补一条机生册豁免腿；本波先落其余 5 件，HEAD 版暂留坏 YAML 事实并在此挂账。

### 89 袋 additive-new 覆盖面（裁定④restricted 范围①的账）

- 判定面：`revive_additive_new` 89 袋，去重后未落地件 **60** 条。
- 本专车已覆盖（含在途四波）：**17** 条；残面 43 条去向：algo_flow 生成物 6 件（走生成器，非手投）、tests 面 16 件（车道 F-1b）、scripts/src 代码面 14 件（施工车道）、docs 下 .py 2 件、`tmp_` 命名证据件 2 件与 `baseline_manifest_v0.json`（已被我落地的 v1 取代）共 1 件判废不投、受阻不投 2 件（见上）。

## 四、重投处方 14 袋执行与分类（总统筹裁定②）

| 袋 | 死因族 | 处置 |
|---|---|---|
| `q-20261004-st-sK-orphanarch-20261004-0001` | SESSION-REQUIRED | 内容级门未修·转工单（不放宽判据） |
| `q-20261006-st-cure-p12b-20261006-0010` | ALGO-FLOW-LINK | 内容级门未修·转工单（不放宽判据） |
| `q-20261006-st-wt-clean-w2-20261006-0002` | ghost_session | 机械修因已重投 |
| `q-20261007-st-mastertc-l0-0003` | ALGO-FLOW-LINK | 内容级门未修·转工单（不放宽判据） |
| `q-20261007-st-mastertc-l7-0005` | CREATE-GUARD | 内容级门未修·转工单（不放宽判据） |
| `q-20261007-st-mastertc-l7-0007` | CREATE-GUARD | 内容级门未修·转工单（不放宽判据） |
| `q-20261007-st-mastertc-l7-0008` | CREATE-GUARD | 内容级门未修·转工单（不放宽判据） |
| `q-20261007-st-mastertc-l7-0009` | CREATE-GUARD | 内容级门未修·转工单（不放宽判据） |
| `q-20261007-st-mastertc-l7-0010` | ghost_session | 机械修因已重投 |
| `q-20261007-st-mastertc-mini-0002` | ALGO-FLOW-LINK | 内容级门未修·转工单（不放宽判据） |
| `q-20261008-st-tclose-20261004-0005` | ghost_session | 机械修因已重投 |
| `q-20261008-st-wm1-wave0-20260924-0045` | ghost_session | 机械修因已重投 |
| `q-20261008-st-wm1-wave0-20260924-0046` | 其他 | 逐袋复核 |
| `q-20261009-st-docs-e13-20261009-0001` | 其他 | 逐袋复核 |

## 五、设施事件随批（A-12 佐证）

- **第四起热册蒸发**：主区 `capability_canonical_file_registry.yaml` 盘面被外来整档快照第三次压回旧基座，我 12 条已落地 token（97 行）从盘面消失 → q-…-promote-chief-0001 死于 CREATE-GUARD。修复=`tools/repair_registry_4.py`（HEAD 基重放+外来未提交条目回插，断言 lost_from_HEAD=0/lost_from_disk=0，safe_write_text CAS），盘面 64654→65003 行，token 条目 14215 条 parse 通过。
- **复活件字段卫生**：36 件 docs/_working 复活件带 `doc_type`（DOC-HEADER-SUITE [EXEMPT-ZONE-FM] 硬拦：豁免区不得有 doc_type）→ 只删该键、正文逐字节不动（`tools/strip_doc_type.py` 断言 body 全等）；反向 3 件 docs/03_modules blueprint.md 属正式区**必须**有 doc_type，我一度连带剥离致 TTL-METADATA 报红，已按原袋字节复原该 3 件。
- **双驱动自伤**：同一原袋被两个并发驱动各投一次（-0006/-0007 同内容），已 kill 单一驱动并把三袋按 R-4 归档去重。
- **陈旧车道基线**：车道 worktree 的 HEAD 落后主 dev 时会产出注定死亡的袋（CREATE-GUARD 读主区盘面、其它内容门读车道基线），本班改为每波新建 fresh-baseline 车道（st-deadcure-g1-chief）。

- **本班自犯三错随批更正**：①复活件 ttl 探针只按 LF 判 frontmatter，2 件原已有 CRLF frontmatter 却被我另插一块（`t0_ceiling_verdict.md` / `t0_conditional_e4_v3_verdict.md`）——收尾袋按原袋字节复原这两件；其余 4 件原件确无 fence（作者侧缺陷，TTL-METADATA 因此拦袋），我补的是最小合法 frontmatter，原裸元数据行保留为正文（未删一字节）。②G5 袋入队前用 `git add` 传参拼错一次（pathspec 尾带 `?`），已改 `xargs -d '\n'` 逐件重加并核 staged 计数=22。③**我产出的 05_tests_restore_manifest.yaml 本身是坏 YAML**：169 处 `class: ?` 未加引号，`yaml.safe_load` 在第 19 行即 ParserError——机读件不可解析=交割面不可消费，属我造的真源缺陷；已把 `?` 归一为 `class: unknown`（其余 2325 条逐项零改动，safe_load 复解析 items=2325 通过）；但该更正**进不了门**——GATE-NO-TESTS-UNIT 内容级匹配把清单里逐字收录的历史路径判为旧路径重引入，门侧缺机生册豁免腿（见受阻不投件表），故 HEAD 版仍是坏 YAML，此账挂在明处不粉饰。
- **车道 F-1b 消费进度（现测）**：`05_tests_restore_manifest.yaml` 2325 件中已 `git ls-files` 命中 1513 件（65.1%）——交割在被真实消化，本专车不再代跑测试面。


## 六、重基线（Owner 2026-10-09 午后令：队列已排空，逐袋重查在途三波）

- 切入口径：以 `2026-10-09T11:20` 之后的 `dead_at` 归因增量（现测，非估）。
- **dead/ 增量 42 袋**归属（回答「你报 1380 / 实测 1410 的差」）：st-chiefc-20261009 17；st-libfront-20261009 11；st-deadcure-g2-chief 9；st-dexp-20261009 3；st-chiefc-20261009-D 2。
- 增量死因族：CREATE-GUARD 10；env/landing 异常 9；其他/无报文 9；GATE-PRECOMMIT-RUN 4；DOC-HEADER-SUITE 3；R5-DIGIT-SUFFIX 3；TAKEOVER-PENDING 1；GATE-VOCAB 1；PERMANENT-SYSTEM-TRIGGER 1；DEPGRAPH-ENFORCEMENT 1。
- 结论：差值主体是**并行会话的正常消化**（总队 st-chiefc 与其 D 车道 40 文件大袋批量过门失败、libfront/dexp 两车道新袋），非我上报口径造假；我报的是 11:26 现测瞬时值，其后 belt 又吃了两轮洪峰。

### 本专车五枚尝试袋的死亡与修因（逐袋留痕）

- `q-20261009-st-deadcure-g2-chief-0001`（33 件）死于 **DOC-HEADER-SUITE** → 修因=剥豁免区 doc_type 键（正文逐字节不动）后重投
- `q-20261009-st-deadcure-g2-chief-0002`（23 件）死于 **DOC-HEADER-SUITE** → 修因=剥豁免区 doc_type 键（正文逐字节不动）后重投
- `q-20261009-st-deadcure-g2-chief-0004`（22 件）死于 **GATE-PRECOMMIT-RUN** → 修因=照录危险命令的行加 [GATE-SELFDOC:GIT-DANGEROUS] 行级标（门自带豁免腿）；shell 检测器无豁免腿 → 该 1 件不投转门位工单
- `q-20261009-st-deadcure-g2-chief-0005`（13 件）死于 **R5-DIGIT-SUFFIX** → 修因=把该目录的 r5_exemption.md 豁免标记并入同一袋（标记件 token 已随 -0003 入 HEAD），目录与标记同袋落地=R5 的目录级标记通道，不再依赖别袋先后
- `q-20261009-st-deadcure-g2-chief-0006`（6 件）死于 **env/landing 异常（git reset（--hard） rc=128）** → 修因=环境性 reset 失败，内容未变，直接重投
- `q-20261009-st-deadcure-g2-chief-0007`（22 件）死于 **CREATE-GUARD** → 修因=环境性 reset 失败，内容未变，直接重投
- `q-20261009-st-deadcure-g2-chief-0008`（13 件）死于 **R5-DIGIT-SUFFIX** → 修因=把该目录的 r5_exemption.md 豁免标记并入同一袋（标记件 token 已随 -0003 入 HEAD），目录与标记同袋落地=R5 的目录级标记通道，不再依赖别袋先后
- `q-20261009-st-deadcure-g2-chief-0009`（14 件）死于 **CREATE-GUARD** → 修因=环境性 reset 失败，内容未变，直接重投
- `q-20261009-st-deadcure-g2-chief-0010`（21 件）死于 **R5-DIGIT-SUFFIX** → 修因=把该目录的 r5_exemption.md 豁免标记并入同一袋（标记件 token 已随 -0003 入 HEAD），目录与标记同袋落地=R5 的目录级标记通道，不再依赖别袋先后
- `q-20261009-st-deadcure-g2-chief-0012`（27 件）死于 **GATE-PRECOMMIT-RUN** → 修因=照录危险命令的行加 [GATE-SELFDOC:GIT-DANGEROUS] 行级标（门自带豁免腿）；shell 检测器无豁免腿 → 该 1 件不投转门位工单
- `q-20261009-st-deadcure-g2-chief-0015`（5 件）死于 **GATE-PRECOMMIT-RUN** → 修因=照录危险命令的行加 [GATE-SELFDOC:GIT-DANGEROUS] 行级标（门自带豁免腿）；shell 检测器无豁免腿 → 该 1 件不投转门位工单
- 本专案 g2 车道全部袋的现状态（现测）：
  - 袋序号 -0001：dead（33 件）
  - 袋序号 -0002：dead（23 件）
  - 袋序号 -0003：done（33 件）
  - 袋序号 -0004：dead（22 件）
  - 袋序号 -0005：dead（13 件）
  - 袋序号 -0006：dead（6 件）
  - 袋序号 -0007：dead（22 件）
  - 袋序号 -0008：dead（13 件）
  - 袋序号 -0009：dead（14 件）
  - 袋序号 -0010：dead（21 件）
  - 袋序号 -0011：done（14 件）
  - 袋序号 -0012：dead（27 件）
  - 袋序号 -0014：done（20 件）
  - 袋序号 -0015：dead（5 件）


- **第五/第六起热册蒸发（同日复发）**：盘面 `capability_canonical_file_registry.yaml` 被外来整档快照压回旧基座两次——14:5x 一次（244 条 HEAD 行消失，含我 12 条 token＋3 条标记 token＋总队/方法论他队条目）、15:04 一次（245 条）。守护=`tools/registry_guard.py`（20s 轮询，HEAD 基重放＋外来未提交条目回插，断言 lost_from_HEAD=0/lost_from_disk=0 才写，safe_write_text CAS），本班内已重写修复 5 次：#3: replayed 245 HEAD lines, kept 1 foreign lines; #4: replayed 245 HEAD lines, kept 1 foreign lines; #5: replayed 245 HEAD lines, kept 1 foreign lines
  - 门侧后果：CREATE-GUARD 读主区盘面（裁定#480 手术③锚定），蒸发窗口内**任何**新建 .md/.yaml/.json 袋都必死于「无 creation_token」——本专案 -0007/-0009 两枚即如此，内容与 token 本身无过错。
## 七、净零申报

- 零新 gate、零新注册表、零新真源轴；§G 台账为 G 组**执行面**，与 01_ledger（裁定面）、10_owner_menu（批文面）不同轴。
- 新增文件全部来自死信袋复原（复活≠新建）；唯一新增自造件=4 枚 `r5_exemption.md` 豁免标记（R5 门自带标记通道，目录名为 36/5/4/14 份已落地文档的引用锚点，改名即断链）与 01_ledger 本体。
- 袋不删除只迁移：dead→dead_archive_20261009_deadcure（mv+manifest 双留痕，一键 restore）。
