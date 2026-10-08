---
ttl: task_bound
title: S8 并发与冲突面挖矿簿 · 多队协调协议与今夜全部仪式知识
created: 2026-09-27
sid: st-fms-chief-20260927
status: MINE 完成（挖干）
---

# S8 · 并发与冲突面（总筹自留线）

**① 职责一句话**：登记本夜多队并发格局、冲突避让图、gateway 仪式链实证与协调协议，使后续任何会话拿到本簿即可安全进场施工。

## ② 现状实测

- worktree 生态 ~90 个：.aidrafts（23）/ .worktrees（45+）/ .qoder（9）/ .runtime/commit_queue（5）/ .runtime/tmp（8）。主区 HEAD=6813b000d6（dev），主区脏 511 件。
- 相邻车道：st-p15-phantom（docs/_working/decision_map_campaign_20260924/links/** + three_piece_infra/phantom_cure/）；st-p1b-libr（library_regen_reconciler.py、reconciliation_registry.py、library_new_module_reconciler.py、project_handbook 族、capability_canonical/module_translation 两册）。
- 主区在途热文件（禁 claim）：candidate_module_registry / capability_canonical_file_registry / module_translation_registry / rule_catalog_registry / trial_ledger_registry / project_handbook 族 / architecture_model/index.yaml / config/governance_operations_map.yaml / config/resource_profile_registry.yaml / data 三件 / docs/library/INDEX.md。

## ③ 六向台账

- **真源**：避让图=本簿§④；作业区宣示=docs/_working/fms_overhaul/（本目录）。
- **写者**：本会话 st-fms-chief-20260927（总筹）+ 六路施工代理（文件所有权互斥，见各簿）。
- **消费者**：后续接波会话；Owner 晨报。
- **漂移史**：capability_canonical_file_registry.yaml 曾被陈旧快照压盘（暂存区 -45 行跨会话删条，REGISTRY-MASS-DELETION 门 warn 在案，2026-09-27 02:0x 由本会话按 batch_creation_tokens 工具 CAS 处方增量补回 5 条并随 q-0001 批落账修复净 +45）。
- **冲突面**：见 §④。
- **净零方案**：本簿为唯一冲突面真源，后续波次改本簿不改散页。

## ④ 冲突避让图（后续波次铁律）

1. 本战役区 docs/_working/fms_overhaul/ 归 st-fms-chief-20260927；他队勿写。
2. st-p1b-libr 三件 library reconciler 文件：本战役 B3/B4/B10 全部绕行（B3 检查器独立新件、B4 不碰 regen reconciler、B10 只读引用）。
3. st-p15-phantom 的 decision_map links 区：B2 死引用清偿批单批 ≤20 文件绕开其面（S1 处方）。
4. .pre-commit-config.yaml 单写者=总筹；B1/B4/B10 的门注册由总筹统一一批落。
5. 宪法 AGENTS.md 单写者=B56 代理（等长替换）→ 总筹复核；期间他队禁写。
6. models/（15G）删除属 Owner 门位，本战役不动。

## ⑤ 今夜实证的仪式链知识（后续会话直接抄）

1. 提交正门实际形态：`git_commit.py --session <sid> --files <逗号清单> --message-file <utf8文件> --allow-non-worktree --allow-overlap`；锁忙自动改道入队（ENQUueued 即零丢失，无需轮询，`commit_queue.py status --session <sid>` 核销）。
2. 预检四门实测拦点：R5-DIGIT-SUFFIX（目录禁数字后缀→战役区曾由 fms_overhaul_20260927 迁址 fms_overhaul）；DIRECTORY-CONTRACT（docs/_working 只许 .csv/.html/.md/.yaml，.txt/.tsv 一律转 .csv）；CREATE-GUARD（gate 读暂存区/HEAD 态 token 册——token 与文件同批合法，token 册必须 git add）；REFERENCE-INTEGRITY（引用宪法须写"根宪法 §N"且 N 真实存在，§6.2 这类小节写法会被拦）。
3. token 工具 CAS 写前自检会拦"盘面比 HEAD 缺条"（陈旧快照压盘）——正解=按工具提示增量补回缺失条目，禁整片 checkout。
4. .ailocks 锁与一次性进程 PID 绑定会自动清理：对短命 shell 会话只有建议价值；提交时保护靠 gateway 自身 claim 体系。
5. 并发上限教训：9 挖矿+6 施工并发会撞账户速率限制（1302 阵亡 1 路）——后续波次施工并发 ≤3 路为宜，挖矿与施工错峰。
6. 队列落单判据：`git show HEAD:<file>` 只认 HEAD；"ENQUEUED≠已落地"，收尾必须 status 核销。

## ⑤+ 夜战终局追加配方（03:00-05:00 实证）

7. **入队面等价判定**：直接提交的预检按"落地仿真态"判 CREATE-GUARD/TRANSLATION-COVERAGE——册子不在本批文件清单里=按 HEAD 旧册判=必死。正解：册子随批同落（token 册/翻译册与内容同批合法）。
8. **claim 是易腐品**（TTL 300s 兜底）：claim-only 后必须立即入队；隔一条命令就过期。
9. **allow_overlap 24h 配额 5 次熔断**（TRAE-079）：超配额转 --enqueue 纯队列道，照样落地。
10. **死信循环配方**：status 读 dead_reason → 修代码/补 claim → requeue（新 qid 取当前盘面快照）→ 排队。q-0006/0008/0009 三轮循环全按此走通。
11. **门禁拦自家货是好事**：FMS 棘轮把总筹自己的 B10 脚本未入库引用也点名（(D) 类=tracked-set 探针正确工作）。
12. **注册表手术原子律**：append 条目必须同批校验 declared 计数（total_gates 103/104 撕裂卡 gateway init 一次，G2 批原子修）。
13. **生成物蒸发零损失实证**：llms.txt 被队列 stash 隔离窗口吞掉，generate_front_door.py 一条命令再生——"生成闭环"支柱的现场活证。
14. **untracked-phantom 区**：docs/02_enterprise_architecture/02_domain_architecture_docs/ 等 76+ 大文件从未入 git（连历史都没有），is_clean 对它们返回空=假干净。判 tracked 必须用 `git ls-files --error-unmatch`。本战役 B2 误伤 138 件已两轮精准逆推修复（101+236 处），322 处存疑保守保留。

## ⑥ 自审闸三态

**挖干**。后续波次拿本簿 §④§⑤ 可直接进场。


## ⑦ S1 宿主空间急救登记（批号 S1｜st-fms-tc-20260927｜2026-09-27 夜）

**触发**：D 盘宿主 free 今夜 16:4x 实测 11.92 GiB（今早 18.8，约 −0.9 GiB/h）。Owner 通宵令 2026-09-27 批准本件（含净删/迁移）。
**硬禁遵守**：未碰 Hyper-V/VM/`D:\HyperV\VMs\zephyr-ch\data.vhdx`；`.runtime/commit_queue/blobs`（dead 袋=部分未落地件唯一存活处）一字节未删；
未用 `rm -rf`/`git worktree remove --force` 硬闯任何车道；未删 `.git/**/index.lock`；搬运导出全部落 F（未经 D、未用 `D:\tmp` 中转）。

### ⑦.1 空间三列账（本批净回收 = 16.70 GiB 动作量；D free 11.92 → 26.57 GiB）

| # | 删前 D free | 动作 | 删后 D free | 净增 |
|---|-----------|------|-----------|------|
| L1 | 11.92 | A：13 条 `.aidrafts` 死车道走正门退役（2.49 GiB 车道字节） | 14.84 | +2.92 |
| — | 14.84 | （外因非本批：他道写盘蚕食 ~2.4 GiB，19:3x-19:5x） | 12.38 | −2.46 |
| L2 | 12.38 | B：`models/qwen25-7b-base` 冷库双证齐后删 D 原件（15,242,808,818 B = 14.19 GiB） | 26.57 | +14.20 |
| L3 | 26.57 | B：`models/qwen25-7b-sft-v1` 冷备（**不删 D 原件**，有活引用） | 26.57 | 0 |
| L4 | 26.57 | C：`retire_tmp_artifacts.py --apply` 354 件 logs/tmp TTL 件（1.5 MB） | 26.57 | +0.001 |

### ⑦.2 A 车道清账结果（正门 = `session_worktree_abort`，四证语义逐道复核）

- **清理 13 条 / 2.49 GiB**（全部 `.aidrafts`；判据=无未提交变更 且 无未合并提交 且 off-branch 孤儿提交=0 且 会话不在 `SessionRegistry.list_active`）：
  `ff_j_control`, `st-chief4x-know-20260927`, `st-ec1-equity`, `st-fms-chief-20260927`, `zc-lane-k-20260927`, `zc-lane-v-20260927`, `zc-lane-g-20260927`, `st-wm1-wave0-20260924`, `st-qcure-20260925`, `st-cleanup-final-20260924`, `st-sim-launch-20260923`, `st-commitsys-20260924`, `st-gaudit2-20260923`
- **零损失实证**：12 条有分支车道的 branch tip 全部 `git merge-base --is-ancestor tip dev = True` 且 `dev..tip = 0`（tip SHA 见
  `.runtime/tmp/s1_abort_log.json`）；`ff_j_control` 为 detached 且 off-branch 提交=0。正门自身另落 `.runtime/worktree_ops_log.jsonl`
  （op=worktree_delete/source=abort）与 CAND-WORKTREE-001 Z1 退役存证链路（脏文件>0 才产 patch，本 13 条均 0 脏）。
- **跳过 118 条 / 34.63 GiB 及原因**：
  - `.worktrees` 70 条 = **全部 dirty>0**（1~333 件未提交）→ 正门 S2 证 2 必拒，按铁律跳过不绕过；其中 29 条带 `campaign total_command_closeout`
    的 `unlanded bytes dirty=N own=M` 显式 `git worktree lock`（锁=在途未落地标记，20 条 own=0，其余 own=1~4）。计 21.56 GiB。
  - `.aidrafts` 余 27 条 = 全部 dirty>0（20 条带 closeout 锁）。计 8.66 GiB。
  - `.qoder/worktrees` 21 条 = 全部 dirty>0，且属 IDE 子代理自管、非派发单声明范围 → 不动，登记待决。计 4.41 GiB。
- **`.aidrafts` 无主判定（A.4）**：grep `config/dev_delivery_map.yaml`（`.aidrafts/` + `.aidrafts_pool/` 被声明为战役工作家，
  并点名 `st-mapbuild-20260924` 为活体）+ 在册 worktree 对账 → 现存 28 目录**全部在册**（0 无主孤儿），
  **已执行 `retired_lanes` 迁移（A.4 处方）**：把车道根里 **git 不认（=无主）** 的 25 个目录**移动**（非删除，同盘可回退）到
  `.runtime/retired_lanes/20260927/`，并落逐目录字节/件数清单 `manifest.yaml`（合计 312,482,917 B = 0.2910 GiB / 25 目录，
  含 `.worktrees` 24 个 + `.aidrafts` 1 个空壳 `st-t0-matrix-20260924`；同盘移动 → 零 D 空间收益，但车道根自此等于"在册真源"）。
  在册 worktree 一律不动（会断 git 元数据且属 S2 证 2 领域）。移动后 `.worktrees` 目录数 94→70、`.aidrafts` 28→27，
  与 `git worktree list` 在册数完全对齐（133 条在册记录零扰动）。
  孤儿目录只出现在 `.worktrees`：94 目录中 24 个未被 git 认（0.291 GiB：`AI-GOVA-001`/`AI-TD2-GOV-001`/`AI-TD2-SEC-001`/`AI-VCFIX-001`/
  `st-auditdoc-v4-20260918` 五件**已在 F 冷库 `50_archive/by_project/zephyralpha/worktree_remnants_20260921` 有 tar.gz+SHA256SUMS 存证**，
  另 19 个 `_a*bt/_a*tmp/_rbt/_fullbt` 类红蓝跑批壳）→ 登记待决（下批可凭冷库对账直删 D 壳）。

### ⑦.3 A.3 有未合并提交车道（不删分支、不动文件，留吸收班判断）

| 车道 | GiB | 分支 | ahead(dev) | off-branch 孤儿提交 | dirty | 锁态 | tip SHA |
|------|-----|------|-----------|-----------------|-------|------|---------|
| `.worktrees/st-zmaster2-20260926` | 0.509 | ai/st-zmaster2-20260926/three-piece-infra | 1 | 0 | 110 | 未锁（—） | dd60ae13bdea |
| `.worktrees/st-ailayer-sx-20260927` | 0.401 | ai/st-ailayer-sx-20260927/task-ai-12items | 6 | 0 | 33 | 锁（protect-unlanded-6-commits-by-st-a） | 790ae9341ca1 |
| `.worktrees/st-t0-matrix-20260924` | 0.24 | ai/st-t0-matrix-20260924/t0-matrix-reexam | 4 | 0 | 254 | 锁（unlanded bytes dirty=243 own=4 cam） | b3c52ff68ca2 |
| `.worktrees/st-commitspeed-tbl-20260924` | 0.235 | ai/st-commitspeed-tbl-20260924/task-commit-chain-instrumentation | 1 | 0 | 54 | 锁（unlanded bytes dirty=53 own=1 camp） | 3bec1e5244c6 |
| `.worktrees/st-chief4-20260927` | 0.229 | ai/st-chief4-20260927/gate-and-landing | 1 | 0 | 180 | 未锁（—） | 55b46e74f0f9 |
| `.worktrees/st-gpu-final-20260924` | 0.228 | ai/st-gpu-final-20260924/gpu-final-campaign | 1 | 0 | 45 | 锁（unlanded bytes dirty=43 own=1 camp） | c4b0e1dbfd9c |
| `.worktrees/st-secbuild-20260923` | 0.225 | ai/st-secbuild-20260923/sector-line-construction | 2 | 0 | 51 | 锁（unlanded bytes dirty=46 own=2 camp） | c14ac74c7e73 |
| `.worktrees/st-e2e-20260924` | 0.222 | ai/st-e2e-20260924/e2e-integration | 2 | 0 | 28 | 锁（unlanded bytes dirty=17 own=2 camp） | 26c2b83c1356 |
| `.worktrees/csx-s1` | 0.203 | (detached) | 0 | 1 | 29 | 锁（unlanded bytes dirty=10 own=1 camp） | 90f7a215b5e1 |
| `.aidrafts/st-t0-revival-20260922` | 0.194 | session/st-t0-revival-20260922 | 3 | 0 | 181 | 锁（unlanded bytes dirty=180 own=3 cam） | b2a3c8bc7a37 |

合计 **10 条 / 2.69 GiB / 21 个 ahead 提交 + 1 个 off-branch 孤儿提交**。
⚠ 特别点名 `.worktrees/csx-s1`：detached HEAD，`90f7a215b5e1` 不在任何分支/标签上（唯一存活处=对象库+该车道 HEAD），
车道被 closeout 锁保护（own=1）——分支删除即失联，吸收班务必先 `git branch rescue/csx-s1 90f7a215b5e1` 再处置。
其余车道 tip 已在 tip SHA 登记，可按 `git merge` / `git cherry-pick` 常规吸收。

### ⑦.4 B models/ 14.29 GiB（base 14.19 + sft 0.09）引用取证与处置

- 取证面（全 grep，含未跟踪件）：`qwen25-7b-base` 在 `src/ scripts/ config/ tests/ specs/ infra/ demos/` **0 命中**；
  仅文档与 `.runtime/commit_queue/blobs`（死信袋）提及。`config/asset_inventory.yaml:160` 的 HF 缓存条目 junction 实测
  `C:\Users\fanzi\.cache\huggingface → E:\ai_cache\huggingface`（非 D）→ 运行时权重下载不落本目录。
  只读进程查：无 python/ollama 进程、11434 无监听 → **活引用=0**。
- 处置=**移冷库后删 D 原件**：`robocopy /E /COPY:DAT /MT:16` → `F:\zephyr_cold\50_archive\by_project\zephyralpha\models_qwen25_7b_base_20260927`；
  对账=件数 29/29、字节 15,242,808,818 全等、**sha256 全 29 件比对（超出 20 件抽样要求）全 match**；
  冷库内落 `SHA256SUMS.txt`（sha256=1bea0c5e0958…）+ `file_manifest.jsonl` + `verification_report.json`（all_equal=True）；
  `F:\zephyr_cold\00_manifest\drawers.jsonl` 已登记（date=2026-09-27，drawer=50_archive/by_project）。双证齐后才 `safe_rmtree` 删 D 原件。
- `models/qwen25-7b-sft-v1`（自训 LoRA adapter，不可再生，0.09 GiB）：**活引用 4 处**
  （`scripts/ml/run_sft_train.py:54` OUTPUT_DIR、`scripts/ml/convert_gguf_ollama.py:55` DEFAULT_ADAPTER_DIR、
  `scripts/ml/accept_nlp_pipeline.py:284` --adapter-dir、`src/zephyr/ml_train/implementations/sentiment_sft_trainer.py:76` _DEFAULT_OUTPUT_DIR）
  → **D 原件原位保留、不改指向**（改 4 处默认路径+跑 ml 引用面测试属 ml 线施工范畴，非急救批），
  另做灾备冷抽 `…/models_qwen25_7b_sft_v1_20260927`（40/40 件、99,155,442 B、全件 sha256 match，已登记 drawers.jsonl）。
- 注：本节推翻 §④.6"models/ 删除属 Owner 门位，本战役不动"——门位已由 Owner 通宵令 2026-09-27 批准解除（仅 base；sft 因活引用仍留）。

### ⑦.5 C .runtime 可安全回收项

- `python scripts/governance/d6_security/retire_tmp_artifacts.py` dry-run（354 件 / 1.5 MB，logs 顶层 + tmp 根层）→ `--apply` 已执行 354/354。
- `.runtime/sessions/*/staging` 超 24h TTL 实测：4 个 staging 目录目录级 mtime>1 天，但 **0 个超期文件**（`-mtime +1` 文件计数=0），
  `.runtime/sessions` 总 1.5 MB → 无需动作；既有正门已存在（`make_session_staging_lifecycle_reconciler`，priority=802，24h TTL）。
- 硬禁项零接触：`.runtime/commit_queue/*`（blobs 3.76 GiB/22412 件、worktrees 1.73 GiB、worktree 1.63 GiB）一字节未删。

### ⑦.6 待决登记（证据不齐 / 非本批授权，不动）

| 对象 | 占用 | 为何不动 | 下批处方 |
|------|------|---------|---------|
| `.worktrees` 70 条脏车道 | 21.56 GiB | 全部有未提交变更（S2 证 2 阻断），29 条带 closeout 未落地锁 | 逐道 `_generate_retire_patch_evidence` 三分类（派生/幻影/实质），实质件吸收后走 abort |
| `.aidrafts` 27 条脏车道 | 8.66 GiB | 同上（20 条带锁） | 同上；`st-final-build-20260926` 内 `.runtime` 2.7 GiB 属车道暂存，先判 TTL |
| `.qoder/worktrees` 21 条 | 4.41 GiB | 非派发声明范围 + IDE 子代理自管 | 由 IDE 侧车道属主批处置 |
| `.runtime/tmp` 大袋（见下表） | 14.00 GiB | 派发 C 只授权 retire_tmp_artifacts + staging TTL；此袋未列 | 逐袋定属主后按 `.runtime/tmp` 临时区政策清（`csx_pkg8` 7.6G/age 1.7d、`pytest_40916` 2.6G/age 0d=**当日活体禁动**、`sweep_tail` 806M/3.7d 等） |
| `.worktrees` 24 个未在册壳目录 | 0.291 GiB | 5 件虽有 F 冷库 tar 存证但需逐件对账后删；19 件红蓝跑批壳未取证 | 对账 SHA256SUMS.txt 后删 D 壳 |
| `tmp_db_dumps` | 0.33 GiB | 非本批声明项 | 走 DB 备份政策 |

`.runtime/tmp` 前十件实测（本批只读取证，属主判定留下批）：

| 袋 | 大小 | 目录 age(天) | git 身份 | dirty |
|----|------|------------|---------|-------|
| `.runtime/tmp/csx_pkg8` | 7.6G | 1.7 | 普通目录 | — |
| `.runtime/tmp/pytest_40916` | 2.6G | 0.0 | 普通目录 | — |
| `.runtime/tmp/sweep_tail` | 806M | 3.7 | 普通目录 | — |
| `.runtime/tmp/lane_gpu` | 304M | 1.9 | 普通目录 | — |
| `.runtime/tmp/csx_t14_wt` | 270M | 2.9 | 在册 worktree | 9 |
| `.runtime/tmp/cs-tbl` | 218M | 1.9 | 普通目录 | — |
| `.runtime/tmp/scratch_dev` | 214M | 3.1 | 在册 worktree | 0 |
| `.runtime/tmp/e2e_20260924` | 213M | 3.9 | 普通目录 | — |
| `.runtime/tmp/csx_t13_wt` | 206M | 2.9 | 在册 worktree | 4 |
| `.runtime/tmp/st-chief7-20260927` | 100M | 0.1 | 普通目录 | — |

### ⑦.7 本批正门缺口记档（施工班请修，勿再踩）

1. `scripts/session_worktree.py abort <sid>` 的 `_worktree_path` 只解析 `.worktrees/<sid>`；对 `.aidrafts/<sid>` 车道走
   "worktree 不存在" 分支——**目录不删，却会 unregister 会话 + kill heartbeat**（空转副作用，判活被静默改写）。
   `.aidrafts` 车道正门是 `zephyr.gov_enforcement.rule_bridge.session_worktree.session_worktree_abort(sid)`。
2. `scripts/governance/session_worktree_cli.py sweep` 只扫 `sess-*` 前缀目录，对本仓主流车道命名
   （`st-* / zc-lane-* / lane_* / ff_* / csx-*`）零覆盖 → 41+94 目录的车道积压根不会被自动清扫（本次 34.63 GiB 积压的直接成因）。
3. `session_worktree_abort` 不查 `SessionRegistry.list_active`（abort 语义=放弃，活会话保护靠调用方）→ 调用前必须自判活，
   本批已在驱动里逐道复核 dirty/unmerged/off-branch/active/locked 五条件（`.runtime/tmp/s1_abort_lanes.py`）。

### ⑦.8 取证件与台账路径（本批全量留痕）

- 台账：`.runtime/tmp/s1_space_ledger.md`（三列账正文，本节为其落地副本）；计划：`.runtime/tmp/s1_plan.md`
- 车道取证：`.runtime/tmp/s1_lane_survey.json`（144 在册 worktree 逐道 字节/件数/dirty/unmerged/locked）、
  `.runtime/tmp/s1_lanes_table.json`（131 车道判定表）、`.runtime/tmp/s1_unmerged_flagged.json`、`.runtime/tmp/s1_abort_log.json`
- 冷库对账：`.runtime/tmp/s1_cold_verify.json`（base，all_equal=True）+ 冷库内 `verification_report.json`/`SHA256SUMS.txt`/`file_manifest.jsonl`
- 驱动脚本（只读判定/正门调用，未落生产路径）：`.runtime/tmp/s1_survey.py`、`s1_table.py`、`s1_abort_lanes.py`、
  `s1_verify_cold.py`、`s1_verify_sft.py`、`s1_cold_proof.py`、`s1_unmerged_report.py`
- reaper 防误杀登记：`data/runtime/process_reaper_keep.txt` 追加 `robocopy`、`s1_cold_archive` 两行

## ⑧ 下午班追加实证（2026-09-27 20:00–23:00 停机压缩窗与提交链现场）

后续会话若要 (a) 跑存储长作业、或 (b) 调试"队列不落地/门禁不生效"，先读这六条：

1. **`HEAD 有修复 ≠ 运行中有修复`**。主区磁盘上的 `scripts/commit_queue.py` 曾被一次陈旧整文件写
   回退成修复前版本，而 belt daemon 读磁盘字节 ⇒ 当日 33 只袋被"已修好的缺陷"杀掉。
   判"能不能恢复"不许肉眼：算 **磁盘独有行集合**（`Counter(HEAD行) - Counter(磁盘行)`）；
   独有集为空或全是修复前旧码 ⇒ 恢复零丢失；独有集含他人未落地增量 ⇒ **禁动**，
   改做"HEAD 为基＋搬回该增量"超集重放。恢复前后要用**同一条命令**做因果对照。
2. **0 字节、无活体 git 持有者的 `index.lock` 会永久毒住一台 serializer worktree**
   （实测 `.git/worktrees/w0/index.lock` 陈 16.7h ⇒ 我的袋停 processing 33 分钟）。
   三证定性＝锁龄／锁体字节数／存活超 10 分钟的 git.exe 数；处置＝**移开不删**（留证可复原），
   移开应 <1 分钟见效，不见效即说明定性错了。
3. **停机压缩窗前置闸量什么**：CH 活体量（未完成备份+merges+未完成 mutations+运行中查询，
   减探针自己那条）＋非本会话在途袋。**注册会话数只作 advisory**——实测有心跳 16 秒前刚跳、
   最后写文件却是 9 小时前的会话壳；拿它当停机许可＝要么永久拒绝要么永久无视。
4. **窗口内禁止入袋**：门禁与 post-commit reconciler 要读 CH；CH 停着要么误杀好袋，
   要么**静默降级**（后者更坏＝未经完整验收落地）。
5. **两个"仪表说谎"口径**：① robocopy 就地覆盖同路径大文件时**卷空闲几乎不动**
   （只反映新旧尺寸差），不能当进度条，判存活看目标 mtime 递增＋进程 CPU 递增，判完成只能等退出码；
   ② PS5.1 `Write-Host` 不进管道，`& child.ps1 2>&1 | Tee-Object` 收不到本仓 ps1 的任何阶段行。
6. **`Get-VHD.MinimumSize` 才是"能回收多少"的真值源**（本机 MinSize 600.0 ≥ FileSize 599.0 GiB
   ⇒ 原地收益≈0）。**别拿虚拟机内部空闲反推宿主可回收量**——这正是"140–150 GiB"错估的来源。

## ⑨ 收尾审计自查到的回退（2026-10-08 复核，本会话自报）

`tests/dr/` 三把常驻尺（45+20+11 例：AutoCheck fail-open 治本尺、镜像删除帽尺、VM 取件裁决尺）
**已不在 HEAD**：被 `6324c9e0f6`（st-tests-chief-20261004「旧路径删除袋1/3」，129 旧一级目录全删）
删除，其自述"内容零删失（新路径真身在终装袋/盘面双证）"对这三件**不成立**——
新结构下无任何路径持有其内容（`git grep Get-MirrorPurgeCap HEAD -- tests` 零命中，
`tests/backup/` 只有另外两件）。字节可从 `5d5398e848` 完整复原，已恢复至
`tests/meta/scripts/backup/`（与 `test_backup_ps_scripts.py` 同处，判据=同为 scripts/backup/*.ps1 的尺）。
**教训**：大规模旧目录清除袋必须逐件证"新路径实存"，不能按目录整体宣称零删失；
收尾方复核口径＝`git grep -l <尺内独有符号> HEAD`，而不是"文件数对上了"。

---

## ⑩ 本班关闭现场：一处硬阻断＋§廿九 作废文（2026-10-09 01:1x，接班必读）

### ⑩.1 ⚑⚠ 硬阻断：`TAKEOVER-PENDING` 挡住 `99_delivery_report.md`，本班 §卅一 无法落地

死信 `q-20261009-st-fms-tc-20260927-0063`（dead_reason 全文在 `.runtime/commit_queue/dead/`）：

> 门禁 TAKEOVER-PENDING 阻断：命中 open 接管条目（死会话遗留资源面）——必须先按接管处方处置再提交。
> 死会话 `st-fc-landing-20261008`；命中文件 1 件：`docs/_working/fms_overhaul/99_delivery_report.md`

本班只读取证（**未动他道任何字节，未 `--resolve`，未 `git worktree remove`**）：

| 探针 | 实测 |
|---|---|
| 该 worktree | `.aidrafts/st-fc-landing-20261008` 在盘，dirty **55 件**（含整个 `docs/_working/fullcirculation_campaign/**` 新增战役簿面） |
| 其基座 | `224e447318` — `git merge-base --is-ancestor` 判 **是 HEAD 祖先**（未分叉） |
| 其 staged 版本报告 | **53,163 B**，`grep -c "## 廿九\|## 三十"` = **0** |
| HEAD 版本报告 | **62,285 B**，两节俱在（`271889ebd1` 本班落地面） |

⇒ **接班第一条红线**：处置该接管时**绝不可把其 staged 的 `99_delivery_report.md` 整体合回主区**——
那是"旧基座＋旧报告"的超集快照，合回即**静默回退本班 §廿九/§三十**（§2.5 归属篡改的同族，只是方向相反）。
若需收其 54 件战役簿成果，请**逐件**合回并对本报告做 `git log -- docs/_working/fms_overhaul/99_delivery_report.md` 反查后**跳过**。

处方（须由维护班或 Owner 指定的接管者做，本班不代裁）：
1. 逐件核 `.aidrafts/st-fc-landing-20261008` 的 55 件成果（本报告除外），成果 merge 或 abort；
   worktree remove 走裁定通道登记，**禁裸 `git worktree remove`**；
2. 确认进程已死后清理 `.runtime/sessions/st-fc-landing-20261008/` 心跳残留（ghost 活性）；
3. `python scripts/governance/session_takeover_ledger.py --resolve st-fc-landing-20261008 --by <接管者> --note <处置结论>`；
4. 解除阻断后，把 ⑩.2 的文字补进 `99_delivery_report.md` 作 §卅一（工作区里本班已写好但落不了地面，**勿 `git checkout HEAD --` 该文件**，否则 §卅一 直接消失）。

### ⑩.2 §廿九 定性作废文（原拟 §卅一 的核心，先在此入册防他人照旧文施工）

**HEAD 现存的 §廿九 说"全盘无 VM 级完整镜像＝活跃灾备空洞，后波重跑 `-CompactWindow`"——这条指令是错的，别照做。**

- `scripts/backup/backup_ch_vm.ps1` 自 `ca9c336746`（2026-10-04 17:23）起在 **L154 无条件 `exit 0`**，
  注释与 commit 正文同称"Owner conditional approval 2026-10-04 / Script is sealed -- do not run"；
  其 backup / AutoCheck / **CompactWindow** / 任务开关四路全部不可达；周任务 `ZephyrAlpha-WeeklyVMBackup` 已 **Disabled**（未注销）。
  ⇒ 重跑＝违逆封印；本班 §廿九 出此建议时未读 L154，属**本班自犯**（转述他人判据而未亲读返回行）。
- 数据面**没裸奔**：`G:\ch_backup_disk2.vhdx` = 1,032,239,185,920 B ≈ **961.35 GiB**，mtime 2026-10-08 07:16，
  内含 CH 逻辑备份 `market.zip` 278.4 GiB ＋ `inc.zip` 42.65 GiB（F 侧同链逐字节等值）；`G:\backup\db_dumps\20261008` 日 dump 在位。
  真实代价＝**VM 级整机快恢降级为"重建式"**（与 10-04 commit 自述一致），不是"数据无备份"。
- ⚑ 但那次批准**在册面查无**：`ruling_registry.yaml` 的 10-04 段（L4100–4163 四条）无一涉 ch_vm_backup/封印/镜像退役；
  grep `ch_vm_backup` 只命中 裁定#443、#445（均 09-30）。而 裁定#445 明写 F 盘摘除三段式 **"本裁定=排班与步骤备案，非执行授权"**，
  且其前置条件恰是"G 侧 ch_vm_backup 副本当日核验通过"——**被删的镜像正是摘 F 链的前置证据**。
  按宪法 §9.11（口头"Owner 说"不构成门禁豁免）→ **待裁 O-8：认技术处置＋补登记裁定面**（零施工）。
- 连坐缺陷：`capacity_guard` 四盘红线（F≥700/G≥500）**唯一读者 `backup_ch_vm.ps1:560` 在 L154 之后 ⇒ 现零活读者**；
  实测 **F free 529.4 GiB 已跌破 700 红线**而无人拦（D 36.8 / E 221.0 / G 1910.7 GiB，`Get-PSDrive` 与 `df -h` 同读数）。
  占用主体 `F:\ch_backup_disk.vhdx` = **950.29 GiB 仍 SCSI0.3 热挂**，裁定#414②/#445/#488-A①C109 的 F 链摘除至今未执行（716→950.29 在涨）。
  本班 09-27 的"写侧容量硬闸"（`f06efd2daa2`）随封印变装饰件——**记本班账上**。修法=内收到仍活着的 `backup.ps1` 写侧
  （w5_1"同真源可派生→必并"；击穿则跳过该目标并留痕，勿整轮 fail 复刻常红噪音）。

### ⑩.3 两处仪表说谎（本班会话自证，防下一班误判）

1. **#ARCH-084 热册守护把别道的写判给当窗测试**：跑本班三把尺（默认 pyproject 配置）＝76 passed ＋ 1 硬 ERROR，
   榜点两例"写了 `capability_canonical_file_registry.yaml`"。双证伪：①只跑被点名两例，该册前后
   `sha256/mtime_ns/size` 逐位不变（`93c0e0d2a5bec20a`/`1791476409987518000`/3,833,974）；
   ②同文件 `git diff HEAD --numstat` 在本班两次读数间自变 +285→+280→+285，且此刻由活跃他道 `st-chief2close-20261008` claim。
   机制＝`tests/conftest.py` 按"测试窗口内热册 sha 漂移"归因，分辨不了写者身份；`filterwarnings=["error"]` 又把它升成硬 ERROR。
   **本班未放宽判据**（往宽松方向改属 Owner 门位）。合法旁路（已用）＝裁定#278 精简跑法 `-c py.ini`。
2. **陈化盘点尺"有码无产"**：`library_hygiene.py` 的 created 轴版本 `14dc95cb05` 早就在 HEAD，
   但 `classify_working_docs` 直调 frontmatter 解析，而 `_working` tracked 面里混有 GBK 证据件
   （`night_sweep/ledgers_archive/NB2_evidence/schtasks_all_20260930.csv`）⇒ 一个件把整轮盘点打成 `UnicodeDecodeError`，
   **HYGIENE.md 史上零生成**。修＝按本班自己立的"读不得者单列计数"归 `undated`（**没有**改成"只扫 .md"，那会静默抹掉 674 件分母＝改口径）。
   因果自证：`fd5ef3f65a` 落地后 01:04 产物即出现（`docs/_working/ultimate_library/HYGIENE.md`，31,009 B，未跟踪，待 token 同袋）。
   真面首测（tracked 4,114 件）：aged **72** / undated **2,741** / fresh **1,299** / 其他 ttl 2 / 在册缺失 **0**；
   ⇒ 本簿 §廿六 那句"74% 无出生日"应为 **66.6%**（2,741/4,114，旧数含非 tracked 面）。

### ⑩.4 本班落地面与未落地清单（逐条可核）

| 状态 | 件 |
|---|---|
| 已落 | `271889ebd1` §廿九/§三十；`23c2d00e54` `backup.ps1` 删除帽上界＋三把尺复位（45+20+11=76 passed，尺传 `-Ceiling` 故与码同袋）；`fd5ef3f65a` 陈化生成器 GBK 治本＋两例红蓝 |
| 未落（工作区在，禁回退） | `docs/_working/fms_overhaul/99_delivery_report.md` 的 §廿九 作废注记＋§卅一（被 ⑩.1 阻断） |
| 未落（需 token，同 ⑩.1 之后） | `docs/_working/fms_overhaul/A1_landing_audit/README.md`、`A2_pending_rulings_a/README.md`、`A3_pending_rulings_b/README.md`、`docs/_working/ultimate_library/HYGIENE.md`。⚠ token 册 `capability_canonical_file_registry.yaml` 此刻带 **+285/−50 外来未落地条目**（本班实测其中 5 行系 `st-matrix-20261007` 的 `gov-adjudication-routing` 新条目）——袋＝整档快照，随袋提交即吸收他人未落地条目，本班按红线**未动**；`HEAD:99_delivery_report.md:682-683` 对三本案卷的引用因此仍是死引用 |
