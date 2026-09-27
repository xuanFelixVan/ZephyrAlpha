---
ttl: task_bound
completes_when: "dead_letter_prescriptions.py 现读 dead/ 后每个簇均带四件处方（见 yaml.prescription）且与 11 册 §R-3 逐行 diff 已出"
---

# 死信「簇 → 处方」矩阵（机生禁手改）

- 生成器：`scripts/governance/wave1b/dead_letter_prescriptions.py`（重跑即覆盖本文件）
- 现读输入：`D:\ZephyrAlpha\.runtime\commit_queue\dead` → **730 封 / 63 处方簇**（census 分身口径 84 簇，全部映射到本矩阵某处方）
- 在册覆盖：18 簇命中 §R-3；本包新拟 45 簇 / 352 封
- 引用工具路径审计：20 条，缺失 0 条 []

## 0. 案卷头部四字段

| 字段 | 值 |
|---|---|
| turn_budget | 子代理 150 轮硬上限。本班会话实际用量：第 8 次工具调用内落第一份文件（生成器骨架）；调研块 10（指令卡软约束 ≤6，**如实记超**：签名探针×2、census 分母×2、门 id 名实×1、预检白名单×2、新见门名子型补抽×3），此后只落盘不再新调研；产物全部由生成器现读重跑复算，人工叙述零独立结论 |
| verified（实测） | dead/ 现读 730 封逐件解析，坏读 0 件；簇分布/首末时间/top3 会话/文件类型分布/子型占比全部由袋内字段计算；§R-3 在册 15 行从 11 册现读；预检白名单从 commit_preflight.py 源码现读（22 道）；门 id 名实核对从 gate_registry.yaml 现读 |
| assumed（未证） | ①`enqueue_preventable` 按'该门 id 是否在预检面'判，未实测预检真跑成功率（预检 degraded fail-open）；②FAM:注册表三向合并 的子型占比按 facet 计数，未逐封人工分型；③现读封数比 11 册 §R-3 成窗（700）多出的部分是 census 之后的新死，未逐簇回溯历史归属 |
| input_set_disjoint_with | wave2/wave3/wave9/wave10/wave11 目录（兄弟包在用）、`11_rescue_playbook.md`（在册真源，本包只出建议并稿行不改它）、`.runtime/commit_queue/**`（只读）、`docs/01_policies_and_standards/**`（热册零写）、CH/PG 零写、git 零写 |
| evidence_ref.cmd | `python scripts/governance/wave1b/dead_letter_prescriptions.py --dead-dir D:/ZephyrAlpha/.runtime/commit_queue/dead --out-dir docs/_working/total_command_closeout/wave1b`（车道内跑，PYTHONPATH 见 §5） |

## 1. 处方矩阵总表（全簇）

| # | 簇（处方族） | 封数 | 首末封 | 根因类别 | 在册覆盖 | 处方来源 | 入队可拦 |
|---|---|---|---|---|---|---|---|
| 1 | `GATE:GATE-PRECOMMIT-RUN` | 85 | 2026-09-23T02:33 → 2026-09-26T08:30 | 内容违规 | 是 R-3#4 | 在册 R-3#4 | 否 |
| 2 | `FAM:注册表三向合并` | 72 | 2026-09-23T02:54 → 2026-09-26T22:46 | 内容违规 | 是 R-3#1 | 在册 R-3#1 | 否 |
| 3 | `GATE:CREATE-GUARD` | 68 | 2026-09-23T14:58 → 2026-09-27T01:58 | 内容违规 | 是 R-3#3 | 在册 R-3#3 | 是 |
| 4 | `GATE:TRANSLATION-COVERAGE` | 55 | 2026-09-22T22:17 → 2026-09-27T01:42 | 内容违规 | 是 R-3#2 | 在册 R-3#2 | 是 |
| 5 | `FAM:LandingEnvironmentError` | 38 | 2026-09-23T03:07 → 2026-09-26T12:18 | 环境或依赖 | 否 | 本包新拟 | 否 |
| 6 | `GATE:TTL-METADATA` | 33 | 2026-09-23T16:33 → 2026-09-26T03:40 | 内容违规 | 否 | 本包新拟 | 是 |
| 7 | `FAM:NOTHING_TO_COMMIT` | 31 | 2026-09-24T01:13 → 2026-09-24T18:30 | 工具自伤 | 否 | 本包新拟 | 否 |
| 8 | `GATE:GATE-VOCAB` | 24 | 2026-09-23T22:06 → 2026-09-25T20:35 | 内容违规 | 否 | 本包新拟 | 否 |
| 9 | `FAM:cascade_stale` | 24 | 2026-09-24T16:05 → 2026-09-27T00:20 | 基底或竞态 | 否 | 本包新拟 | 否 |
| 10 | `GATE:COMPLEXITY-GUARD` | 22 | 2026-09-23T18:04 → 2026-09-26T06:27 | 内容违规 | 是 R-3#11 | 在册 R-3#11 | 否 |
| 11 | `GATE:REFERENCE-INTEGRITY` | 18 | 2026-09-24T04:31 → 2026-09-27T02:57 | 内容违规 | 是 R-3#6 | 在册 R-3#6 | 是 |
| 12 | `GATE:R5-DIGIT-SUFFIX` | 16 | 2026-09-23T05:58 → 2026-09-26T13:38 | 内容违规 | 是 R-3#8 | 在册 R-3#8 | 否 |
| 13 | `GATE:IMPORT-INTEGRITY` | 15 | 2026-09-23T18:30 → 2026-09-25T20:19 | 基底或竞态 | 否 | 本包新拟 | 否 |
| 14 | `FAM:CLAIM_REQUIRED_VIOLATION` | 14 | 2026-09-24T03:00 → 2026-09-27T01:34 | 工具自伤 | 否 | 本包新拟 | 否 |
| 15 | `GATE:DEPGRAPH-ENFORCEMENT` | 12 | 2026-09-24T22:38 → 2026-09-26T01:35 | 内容违规 | 是 R-3#10 | 在册 R-3#10 | 否 |
| 16 | `GATE:TEST-SOURCE-CONSISTENCY` | 11 | 2026-09-23T06:03 → 2026-09-27T01:26 | 内容违规 | 否 | 本包新拟 | 是 |
| 17 | `GATE:PERMANENT-SYSTEM-TRIGGER` | 11 | 2026-09-23T17:25 → 2026-09-26T01:07 | 内容违规 | 否 | 本包新拟 | 否 |
| 18 | `FAM:BASE-快照基底共祖冲突` | 11 | 2026-09-24T23:17 → 2026-09-26T23:35 | 基底或竞态 | 否 | 本包新拟 | 否 |
| 19 | `GATE:BLUEPRINT-FORMAT` | 10 | 2026-09-23T21:50 → 2026-09-25T16:36 | 内容违规 | 否 | 本包新拟 | 否 |
| 20 | `GATE:ORPHAN-MODULE` | 10 | 2026-09-23T17:30 → 2026-09-26T04:30 | 内容违规 | 是 R-3#9 | 在册 R-3#9 | 否 |
| 21 | `GATE:DIRECTORY-CONTRACT` | 9 | 2026-09-23T20:21 → 2026-09-25T19:49 | 内容违规 | 否 | 本包新拟 | 是 |
| 22 | `FAM:BASE-入队基底后dev推进同路径` | 9 | 2026-09-23T15:04 → 2026-09-24T20:59 | 基底或竞态 | 否 | 本包新拟 | 否 |
| 23 | `GATE:PROTECTED-PATHS` | 9 | 2026-09-23T22:19 → 2026-09-24T21:50 | 内容违规 | 否 | 本包新拟 | 是 |
| 24 | `GATE:MAP-ALIGNMENT` | 9 | 2026-09-24T01:02 → 2026-09-24T08:34 | 内容违规 | 否 | 本包新拟 | 否 |
| 25 | `GATE:SSOT-REDEFINITION` | 9 | 2026-09-24T06:07 → 2026-09-26T23:33 | 内容违规 | 否 | 本包新拟 | 否 |
| 26 | `GATE:ALGO-NOTE-SYNC` | 9 | 2026-09-24T22:31 → 2026-09-26T03:55 | 内容违规 | 否 | 本包新拟 | 否 |
| 27 | `GATE:CAPABILITY-OVERLAP` | 8 | 2026-09-23T06:16 → 2026-09-25T20:36 | 内容违规 | 否 | 本包新拟 | 否 |
| 28 | `GATE:ALGO-FLOW-LINK` | 7 | 2026-09-24T00:15 → 2026-09-25T20:55 | 内容违规 | 否 | 本包新拟 | 否 |
| 29 | `FAM:基底不可知` | 7 | 2026-09-24T21:47 → 2026-09-26T03:01 | 基底或竞态 | 是 R-3#5 | 在册 R-3#5 | 否 |
| 30 | `FAM:BASE-dev-CAS竞态同路径` | 6 | 2026-09-24T03:55 → 2026-09-26T01:50 | 基底或竞态 | 否 | 本包新拟 | 否 |
| 31 | `FAM:gate册条目坏-fresh-import亦败` | 6 | 2026-09-26T04:14 → 2026-09-26T07:39 | 环境或依赖 | 否 | 本包新拟 | 否 |
| 32 | `GATE:CAPABILITY-LOOKUP-REQUIRED` | 5 | 2026-09-23T17:30 → 2026-09-24T22:26 | 内容违规 | 否 | 本包新拟 | 是 |
| 33 | `GATE:NO-BARE-SQL` | 5 | 2026-09-24T05:38 → 2026-09-25T07:30 | 内容违规 | 否 | 本包新拟 | 是 |
| 34 | `GATE:CH-FINAL-GATE` | 4 | 2026-09-23T17:32 → 2026-09-26T01:55 | 内容违规 | 是 R-3#13 | 在册 R-3#13 | 否 |
| 35 | `GATE:MUTABLE-CONST-WITHOUT-FINAL` | 4 | 2026-09-23T19:30 → 2026-09-26T02:01 | 内容违规 | 否 | 本包新拟 | 否 |
| 36 | `FAM:landing-TimeoutExpired` | 4 | 2026-09-24T01:58 → 2026-09-25T03:16 | 环境或依赖 | 否 | 本包新拟 | 否 |
| 37 | `GATE:TABLE-NAME-REGISTRY` | 4 | 2026-09-24T06:04 → 2026-09-25T21:52 | 内容违规 | 否 | 本包新拟 | 是 |
| 38 | `GATE:NOQA-VALIDATION` | 3 | 2026-09-23T22:35 → 2026-09-23T23:57 | 内容违规 | 否 | 本包新拟 | 否 |
| 39 | `GATE:REGISTRY-MASS-DELETION` | 3 | 2026-09-23T17:28 → 2026-09-24T07:08 | 内容违规 | 是 R-3#14 | 在册 R-3#14 | 是 |
| 40 | `GATE:REAL-KEY-REFERENCE-SCAN` | 3 | 2026-09-24T04:45 → 2026-09-24T07:16 | 内容违规 | 否 | 本包新拟 | 否 |
| 41 | `GATE:FILE-PLACEMENT-TTL` | 3 | 2026-09-24T09:13 → 2026-09-25T02:19 | 内容违规 | 否 | 本包新拟 | 是 |
| 42 | `GATE:SESSION-REQUIRED` | 2 | 2026-09-26T22:16 → 2026-09-27T02:49 | 工具自伤 | 否 | 本包新拟 | 否 |
| 43 | `GATE:DATETIME-NOW-FORBIDDEN` | 2 | 2026-09-26T03:55 → 2026-09-26T04:11 | 内容违规 | 否 | 本包新拟 | 是 |
| 44 | `GATE:NO-HIGH-COMPLEXITY` | 1 | 2026-09-23T05:56 → 2026-09-23T05:56 | 内容违规 | 是 R-3#11 | 在册 R-3#11 | 否 |
| 45 | `FAM:prestage拒绝-gitignore快照路径` | 1 | 2026-09-23T18:04 → 2026-09-23T18:04 | 内容违规 | 否 | 本包新拟 | 否 |
| 46 | `GATE:NEW-FILE-DEPGRAPH-ENFORCEMENT` | 1 | 2026-09-23T04:53 → 2026-09-23T04:53 | 内容违规 | 是 R-3#10 | 在册 R-3#10 | 否 |
| 47 | `GATE:FILE-COPY` | 1 | 2026-09-23T15:50 → 2026-09-23T15:50 | 内容违规 | 否 | 本包新拟 | 否 |
| 48 | `GATE:HOT-FILE-BASE-FRESHNESS` | 1 | 2026-09-24T03:25 → 2026-09-24T03:25 | 基底或竞态 | 是 R-3#14 | 在册 R-3#14 | 否 |
| 49 | `GATE:FORGED-GW-MARKER` | 1 | 2026-09-24T07:41 → 2026-09-24T07:41 | 工具自伤 | 否 | 本包新拟 | 否 |
| 50 | `FAM:本包自撤` | 1 | 2026-09-24T22:22 → 2026-09-24T22:22 | 工具自伤 | 否 | 本包新拟 | 否 |
| 51 | `FAM:COMMIT_FAILED-nothing-to-commit` | 1 | 2026-09-24T01:24 → 2026-09-24T01:24 | 工具自伤 | 否 | 本包新拟 | 否 |
| 52 | `GATE:MSG-EXPOSURE` | 1 | 2026-09-25T18:00 → 2026-09-25T18:00 | 内容违规 | 否 | 本包新拟 | 否 |
| 53 | `GATE:MODULE-ID-CONSISTENCY` | 1 | 2026-09-25T18:14 → 2026-09-25T18:14 | 内容违规 | 否 | 本包新拟 | 否 |
| 54 | `GATE:MSG-STYLE` | 1 | 2026-09-25T09:12 → 2026-09-25T09:12 | 内容违规 | 否 | 本包新拟 | 否 |
| 55 | `FAM:BASE-dev-CAS重试耗尽` | 1 | 2026-09-25T19:14 → 2026-09-25T19:14 | 基底或竞态 | 否 | 本包新拟 | 否 |
| 56 | `GATE:RELATIVE-PATH-LITERAL` | 1 | 2026-09-25T08:05 → 2026-09-25T08:05 | 内容违规 | 否 | 本包新拟 | 否 |
| 57 | `GATE:EXEMPT-ZONE-FM` | 1 | 2026-09-25T21:25 → 2026-09-25T21:25 | 内容违规 | 否 | 本包新拟 | 是 |
| 58 | `GATE:UNDEFINED-NAME` | 1 | 2026-09-25T21:54 → 2026-09-25T21:54 | 内容违规 | 否 | 本包新拟 | 否 |
| 59 | `GATE:ENCODING-SAFETY` | 1 | 2026-09-26T03:17 → 2026-09-26T03:17 | 内容违规 | 是 R-3#12 | 在册 R-3#12 | 否 |
| 60 | `GATE:FUNCTION-DUP` | 1 | 2026-09-26T23:45 → 2026-09-26T23:45 | 内容违规 | 否 | 本包新拟 | 否 |
| 61 | `FAM:WorktreePunchThroughError` | 1 | 2026-09-26T01:04 → 2026-09-26T01:04 | 工具自伤 | 是 R-3#7 | 在册 R-3#7 | 否 |
| 62 | `GATE:DOC-HEADER-SUITE` | 1 | 2026-09-26T21:39 → 2026-09-26T21:39 | 内容违规 | 否 | 本包新拟 | 否 |
| 63 | `FAM:landing-git-reset硬复位超时` | 1 | 2026-09-27T00:35 → 2026-09-27T00:35 | 工具自伤 | 是 R-3#7 | 在册 R-3#7 | 否 |

## 2. Top 20 簇逐条处方（每条带实测样例：真实 qid + dead_reason 原文）

### 2.1 `GATE:GATE-PRECOMMIT-RUN` — 85 封
- **处方来源**：在册 R-3#4（在册原文：落地侧门禁账缺失 ⇒ 先跑 R-2 步骤 4｜册面袋数：2）
- **根因类别**：内容违规
- **子型分布（现读）**：{'INNER_FAIL:LINT': 27, 'INNER_FAIL:HOOK-GATE-PROTECTED-PATHS': 17, 'INNER_FAIL:HOOK-RUFF-FORMAT': 16, 'INNER_FAIL:HOOK-GATE-NAMING': 9, 'INNER_FAIL:HOOK-GATE-ANY-ABUSE': 3, '-': 2}
- **涉及会话 top3**：[('st-sweep-tail-20260923', 16), ('st-commitspeed-tbl-20260924', 16), ('st-qcure-20260925', 6)]
- **文件类型分布**：{'py': 352, 'md': 149, 'yaml': 62, 'sh': 7, 'ps1': 6, 'csv': 5}
- **最小复现命令**：`落地侧 pre-commit run 面复算（读 reason 尾行的 Failed 步名）：python scripts/governance/meta/gate_prerun.py --session <SID> --files "<逗号清单>" --message-file .runtime/tmp/<SID>/msg_<批名>.md`
- **照抄可用的修法**：此门是 runner 不是判据——**真死因在 reason 尾行点名的内层失败步**（现读分布：lint / gate-protected-paths / ruff-format / gate-naming / 未解决冲突标记）：①受保护路径（docs/01_policies_and_standards/rules/*.yaml 等）→ 摘出本袋另起小袋，或带 [ARCH-APPROVAL:<已登记 issue>] / 命中 ruling_registry.yaml approved_paths；②lint/format/naming → 在车道内跑与门同源的格式化/naming 通道改到 0 再投；③冲突标记 → 逐件 `grep -n '<<<<<<<' <file>` 解冲后重投（enqueue_preflight.py 已带冲突标记检测器，锁外可先验）。
- **禁止动作**：禁 --no-verify 或改 .pre-commit-config/hook 配置绕开；禁改门阈值；禁对同 payload 双 requeue 硬闯。
- **实测样例**：qid `q-20260926-st-qmine-20260925-0040`（袋文件 `dead/q-20260926-st-qmine-20260925-0040.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 GATE-PRECOMMIT-RUN 阻断: 落地前 pre-commit run 在 staged 面（own-scope 临时索引）发现本提交文件的违规（裁定#341 方案②，hook=['ruff', 'ruff-format']) 检测未解决的合并冲突标记（local 替代 external #ARCH-PRECOMMIT-OFFLINE-001）...........................................Passed 检测意外提交的私钥（local 替代 external #ARCH-PRECOMMIT-OFFLINE-001）.................................................Passed GATE-PROTECTED-PATHS: 受保护路径写入检测（#ARCH-MODEL-LIFECYCLE-001 P1 Layer 2）.....................................Skipped 检测危险 git 命令（65 号 §7.13，ABS-26/27/28）...`
- **注**：GATE-PRECOMMIT-RUN 不在 gate_registry.yaml 的 gate_id 集内（落地侧 runner，非注册门）⇒ 预检白名单结构性收不到它；治本面是把其内层判定并入预检面（protected-paths/naming/format 本身已在别处成门）。
- 分身 census 簇：['GATE:GATE-PRECOMMIT-RUN']

### 2.2 `FAM:注册表三向合并` — 72 封
- **处方来源**：在册 R-3#1（在册原文：走 R-1 修基底 + 该册变更单独成袋；勿 requeue 硬闯｜册面袋数：71（其中全文指名身份键 7））
- **根因类别**：内容违规
- **子型分布（现读）**：{'OURS-UNIDENTIFIABLE-ENTRY': 36, 'OURS-DUP-IDENTITY': 32, 'MERGE-OURS-OTHER': 2, '-': 1, 'NO-PLAINZH': 1}
- **涉及会话 top3**：[('st-library-final-20260924', 10), ('st-align-dirty-20260924', 7), ('st-k4-20260923', 6)]
- **文件类型分布**：{'md': 290, 'yaml': 176, 'py': 149, 'csv': 8, 'ps1': 3}
- **最小复现命令**：`按 reason 点名的册路径现读身份键重复度：grep -c '<身份键>: <值>' <册>（现读两子型 OURS-DUP-IDENTITY / OURS-UNIDENTIFIABLE-ENTRY）`
- **照抄可用的修法**：先分型（三型处方不同，前两型病灶都在**袋内该册自身**，不是基底）：①OURS-DUP-IDENTITY=同一身份键两条 ⇒ 保留真源条目删重复，热文件必用 safe_write_text（src/zephyr/shared/io/file_utils.py），件+册同袋重投；②OURS-UNIDENTIFIABLE-ENTRY=条目被压成非 dict（字符串/空段）⇒ 恢复映射结构，并核顶格根键唯一性（重复根键会被解析层静默忽略，REGISTRY-YAML-PARSE 坑）；③reason 明写双改/基底冲突才走 R-1 修基底 + 该册变更单独成袋。
- **禁止动作**：禁 requeue 硬闯（同字节必同结果）；禁整档覆盖热册（=第二次蒸发）；禁为摘他人条目回退基底。
- **实测样例**：qid `q-20260926-st-qmine-20260925-0044`（袋文件 `dead/q-20260926-st-qmine-20260925-0044.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`landing 异常: RuntimeError: [landing] 注册表三向合并失败（死信回退人工）: docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml: ours 同侧身份键重复且内容冲突（同键异容，仓库态缺陷）: decl|id=CAND-GOVTEST-005——死信回人工；处方: 跑 registry 去重对账器核对存量，勿手拼 YAML --- 在册先条 (first) --- id: CAND-GOVTEST-005 name: commit queue P1 级联+P2 监控（66号②③，随 MVP 验收后） aliases: - commit queue 扩展 domain: D_GOVERNANCE domain_status: active sub_layer: git 安全治理 problem: P1 级联标记+死信重入队+done TTL+worktree 强制升硬联动；P2 监控接入+temp-index+多分支评估。 proposal: 触发=CAND-GOVTEST-004 MV`
- **注**：★与在册 R-3#1 冲突：册把整族判为'基底病'（走 R-1），现读 ours 侧子型占绝对多数（facet 计数见 §5 该行证据）⇒ 建议该行拆三型，①②给可照抄修法。
- 分身 census 簇：['注册表三向合并失败(家族)']

### 2.3 `GATE:CREATE-GUARD` — 68 封
- **处方来源**：在册 R-3#3（在册原文：R-2 步骤 2；token 与件同袋｜册面袋数：8（六图役）+ 全局多封）
- **根因类别**：内容违规
- **子型分布（现读）**：{'NO-CREATION-TOKEN': 49, 'MISSING-HEADER-FIELDS': 10, '-': 6, 'CLASS-NAME-CONFLICT': 3}
- **涉及会话 top3**：[('st-cmd-20260924', 16), ('st-commitspeed-tbl-20260924', 10), ('st-mapbuild-20260924', 8)]
- **文件类型分布**：{'py': 448, 'md': 403, 'yaml': 130, 'csv': 15, 'ps1': 5, 'js': 2}
- **最小复现命令**：`python -c "from zephyr.gov_enforcement.commit_gates import create_guard" 后 python scripts/governance/meta/gate_prerun.py --session <SID> --files "<逗号清单>" --message-file .runtime/tmp/<SID>/msg_<批名>.md`
- **照抄可用的修法**：子型 MISSING-HEADER-FIELDS（ARCH-031）= 前 30 行补齐 15 字段头（BLUEPRINT/MODULE/DOMAIN/DEPENDENCIES/CONSUMERS/STARTUP/MATURITY/INVARIANTS/MODIFY-GUARD/STABILITY/SAFETY/AI_AUTONOMY/ERROR_CONTRACT/TESTS/TTL）；子型 NO-CREATION-TOKEN = python scripts/governance/batch_creation_tokens.py 批量登记且 **token 与件同袋**；子型 CLASS-NAME-CONFLICT（ARCH-034 类名跨模块）= 改类名或复用既有类，禁并行同名。
- **禁止动作**：禁抄别人 token 或 --created-by 填他会话；禁把 token 放后继袋（token 册先行=本袋永无 token）；禁删门判据。
- **实测样例**：qid `q-20260927-st-final-build-20260926-0015`（袋文件 `dead/q-20260927-st-final-build-20260926-0015.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 CREATE-GUARD 阻断: 无 creation_token，禁止造第二真源（trae_060 §2）: ['scripts/governance/wave1a/verified_promotion_check.py', 'scripts/governance/wave1b/dead_letter_census.py', 'scripts/governance/wave2/lane_inventory.py', 'scripts/signals/chart_condition_package.py', 'src/zephyr/data/date_normalize.py', 'src/zephyr/data/dual_source_guard.py', 'src/zephyr/data/miniqmt_caliber_sentinel.py', 'src/zephyr/gov_enforcement/rule_bridge/union_priority_ruler.py', 'src/zephyr/shared/foundation/flag_read_state.p`
- **注**：CREATE-GUARD 已在 _INLINE_PREFLIGHT_CHECKS 内联面仍大量死 ⇒ 两个候选解释：预检 degraded fail-open（设施异常放行）或'车道盘面≠袋内 blob 字节'；本包未实测预检真跑率（见案卷头部 assumed）。
- 分身 census 簇：['GATE:CREATE-GUARD']

### 2.4 `GATE:TRANSLATION-COVERAGE` — 55 封
- **处方来源**：在册 R-3#2（在册原文：`add_module_translation.py` **在主仓**跑，plain-zh ≥8 字，且必须落 `entries:` 段｜册面袋数：11（六图役））
- **根因类别**：内容违规
- **子型分布（现读）**：{'NO-PLAINZH': 55}
- **涉及会话 top3**：[('st-mapbuild-20260924', 11), ('st-commitspeed-tbl-20260924', 7), ('st-sweep-tail-20260923', 5)]
- **文件类型分布**：{'py': 296, 'yaml': 111, 'md': 99, 'csv': 15, 'ps1': 6, 'npy': 4}
- **最小复现命令**：`python scripts/governance/meta/gate_prerun.py --session <SID> --files "<逗号清单>" --message-file .runtime/tmp/<SID>/msg_<批名>.md（同一清单同 message 复算）`
- **照抄可用的修法**：python scripts/governance/d3_metadata/add_module_translation.py --path <file> --domain <D_*> --name-zh <中> --plain-zh <大白话≥8字> **必须在主区跑**（worktree 里跑出的条目落不进 HEAD 册，同批必再判'无 plain_zh'）；写后核 `grep -c '^entries:' 册` 与根键唯一性，再件+册同袋重投。
- **禁止动作**：禁在车道内改翻译册后指望落地；禁把门禁报错里的取样字面量回填进 YAML；禁调 plain_zh 长度判据。
- **实测样例**：qid `q-20260926-st-mapbuild-20260924-0037`（袋文件 `dead/q-20260926-st-mapbuild-20260924-0037.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 TRANSLATION-COVERAGE 阻断: TRANSLATION-COVERAGE: 5 个新建 .py 文件在翻译真源（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。修复：python scripts/governance/d3_metadata/add_module_translation.py --path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。详情: 无 plain_zh 简介[src/zephyr/gov_enforcement/commit_gates/construction_workflow_map_gate.py, src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py, src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py, src/zephyr/`
- **注**：在册 R-3#2 只说'在主仓跑'，未量化 55 封里 worktree 跑占多少——本包按 facet 现读补齐。
- 分身 census 簇：['GATE:TRANSLATION-COVERAGE']

### 2.5 `FAM:LandingEnvironmentError` — 38 封
- **处方来源**：本包新拟
- **根因类别**：环境或依赖
- **子型分布（现读）**：{'GATE-MODULE-IMPORT-FAIL': 38}
- **涉及会话 top3**：[('st-cmd-20260924', 13), ('st-commitspeed-tbl-20260924', 10), ('st-combine-20260923', 8)]
- **文件类型分布**：{'py': 124, 'md': 109, 'yaml': 68, 'csv': 8, 'yml': 4, 'sh': 2}
- **最小复现命令**：`python -c "import importlib;[importlib.import_module(m) for m in ['zephyr.gov_enforcement.commit_gates.<reason 点名模块>']]"`
- **照抄可用的修法**：落地侧主区 gate 模块 import 失败（ModuleNotFoundError / gate 册条目坏）⇒ 属主会话把门本体+它读的册同袋落主区；本袋只等环境修好后 requeue --adopt-prior-work。子型 PRIORITY-CONFLICT 走'后到者让位'改 priority（先例：ORPHAN-MODULE 86->89）。
- **禁止动作**：不是内容病：禁改本袋内容自证；禁删/注释自家 gate 注册；禁在本袋里顺手造别人的门模块。
- **实测样例**：qid `q-20260926-st-commitspeed-tbl-20260924-0166`（袋文件 `dead/q-20260926-st-commitspeed-tbl-20260924-0166.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`landing 异常: LandingEnvironmentError: landing 环境不可用: gate 装载失败但 fresh 子进程通过（本进程纪元陈旧/瞬态 IO）: gate auto-registration fail-closed (裁定#351): 4/103 gate(s) failed to load: REAL-KEY-REFERENCE-SCAN: import failed: ModuleNotFoundError: No module named 'zephyr.ai_layer.redline'; TASK-ORDER-DOCS-LOCK: import failed: ModuleNotFoundError: No module named 'zephyr.ai_layer.redline'; CONSTITUTION-LINE-LIMIT: import failed: ModuleNotFoundError: No module named 'zephyr.ai_layer.redline'; DOC-HEADER-SUITE: factory function not found:`
- **注**：38 封＝全队列第一大非内容簇；根因在主区依赖态，入队预检无从判（预检在车道里跑）。
- 分身 census 簇：['LandingEnvironmentError(landing 环境不可用)']

### 2.6 `GATE:TTL-METADATA` — 33 封
- **处方来源**：本包新拟
- **根因类别**：内容违规
- **子型分布（现读）**：{'NO-FRONTMATTER': 18, 'MISSING-TTL-FIELD': 6, 'CHECKER-EXEC-FAILED': 3, '-': 3, 'MISSING-DOC-TYPE': 2, 'BAD-FM-VALUE': 1}
- **涉及会话 top3**：[('st-cmd-20260924', 21), ('st-audit-fix-20260924', 2), ('st-commitspeed-tbl-20260924', 2)]
- **文件类型分布**：{'md': 288, 'py': 77, 'yaml': 39, 'csv': 33, 'importlinter': 1}
- **最小复现命令**：`python scripts/governance/d3_metadata/check_frontmatter_metadata.py --files "<清单>"（与本包 reason 同判据的独立尺；不可用时退 python scripts/governance/meta/gate_prerun.py --session <SID> --files "<逗号清单>" --message-file .runtime/tmp/<SID>/msg_<批名>.md）`
- **照抄可用的修法**：按现读四子型各一条：①NO-FRONTMATTER=新建 .md 完全没有题记 ⇒ 补 `ttl: task_bound` + `completes_when:` 两键（本包产物头部即合规写法）；②MISSING-TTL-FIELD=有题记但缺 ttl 键 ⇒ 只补 ttl 不动别的键；③MISSING-DOC-TYPE=缺 doc_type ⇒ 按该目录用途补 doc_type（FILE-PLACEMENT-TTL 会接力判 ttl 与区域相配）；④CHECKER-EXEC-FAILED=门的取样脚本自身在落地快照路径里跑挂 ⇒ **不是内容病**，属主会话先核 check_frontmatter_metadata.py 在本袋可执行，再 requeue --adopt-prior-work。⚠已实证坑：`completes_when:` 值里带裸冒号会被 YAML 解析成嵌套，门反读为'缺 ttl'——值加引号或改空格分隔；py 头部 `# [TTL] task_bound` 值须裸词。
- **禁止动作**：禁给临时区件写 ttl: permanent（FILE-PLACEMENT-TTL 接力拦）；禁删题记/删 doc_type 绕过；禁改门允许的键集或放宽必填判据。
- **实测样例**：qid `q-20260926-st-audit-fix-20260924-0042`（袋文件 `dead/q-20260926-st-audit-fix-20260924-0042.json`；requeued→`q-20260926-st-audit-fix-20260924-0044`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 TTL-METADATA 阻断: FAIL: .runtime\commit_queue\worktrees\w1\docs\_working\chain_fullflow_20260926\mine_pipe_blockage_substages.md invalid ttl='90d' (valid: ['permanent', 'task_bound']...) FAIL: .runtime\commit_queue\worktrees\w1\docs\_working\chain_fullflow_20260926\mine_pipe_false_green_census.md invalid ttl='90d' (valid: ['permanent', 'task_bound']...) FAIL: .runtime\commit_queue\worktrees\w1\docs\_working\chain_fullflow_20260926\mine_queue_liveness_and_trigger_mass.md invalid ttl='2026-12`
- **注**：reason 里的路径是 .runtime\commit_queue\worktree(s)\w<N>\... ⇒ 门读落地快照盘面而非车道盘面：只改车道不够，必须确认袋内 blob 字节（与 §4 degraded 结论同源）。
- 分身 census 簇：['GATE:TTL-METADATA']

### 2.7 `FAM:NOTHING_TO_COMMIT` — 31 封
- **处方来源**：本包新拟
- **根因类别**：工具自伤
- **子型分布（现读）**：{'BLOB-OLD-DEV-MISMATCH': 31}
- **涉及会话 top3**：[('st-stress-20260923', 29), ('st-chainpile-20260922', 1), ('st-sweep-tail-20260923', 1)]
- **文件类型分布**：{'md': 31, 'yaml': 2, 'py': 1}
- **最小复现命令**：`python scripts/commit_queue.py status && git cat-file -e <blob_ref>（只读核 blob 是否仍与 dev 同字节）`
- **照抄可用的修法**：防线语义='快照 blob 与 old_dev 不符，应用静默丢失' ⇒ 车道同步后重新入队取新字节；若盘面已等 dev ⇒ 本袋确无事可提交，走 dead_reason 属主会话复核（不删件）。
- **禁止动作**：禁 `git apply`/update-index 手工塞（§9.8 plumbing 红线）；禁删 dead 袋；禁把这条防线判成'门的错'去改它。
- **实测样例**：qid `q-20260924-st-chainpile-20260922-0075`（袋文件 `dead/q-20260924-st-chainpile-20260922-0075.json`；requeued→`q-20260924-st-chainpile-20260922-0077`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`NOTHING_TO_COMMIT 但快照未真应用 (blob 与 old_dev 不符: ['config/governance/noqa_exempt_registry.yaml', 'docs/_working/chain_piling_campaign/04_construction_map.md', 'docs/_working/chain_piling_campaign/snapshots/question_batch_w6.yaml', 'scripts/governance/check_meta_question_batch.py'])——应用静默丢失，死信回退重新入队（2026-09-15 q-0003 假落地事故防线）`
- **注**：31 封：防线在 2026-09-15 q-0003 假落地事故后加的，代价是竞态期高频死信——治本面是入队口核 blob 与 dev 差集。
- 分身 census 簇：['NOTHING_TO_COMMIT 但快照未真应用(blob 与 old_dev 不符)']

### 2.8 `GATE:GATE-VOCAB` — 24 封
- **处方来源**：本包新拟
- **根因类别**：内容违规
- **子型分布（现读）**：{'VOCAB-HARDCODE': 22, '-': 2}
- **涉及会话 top3**：[('st-chainpile-20260922', 8), ('st-ailayer-final-20260924', 5), ('st-pipeline-final-20260924', 4)]
- **文件类型分布**：{'py': 852, 'yaml': 120, 'md': 63, 'ps1': 16, 'html': 5}
- **最小复现命令**：`grep -rn 'layer_vocabulary\|status_vocabulary' src/zephyr scripts | head`
- **照抄可用的修法**：把 VALID_LAYERS/VALID_STATUSES 这类硬编码合法值改成从 docs/01_policies_and_standards/_registry/**/*_vocabulary.yaml 动态加载（复用既有 vocabulary loader，勿造第二个 loader）；新增合法值走词表册同袋。
- **禁止动作**：禁往词表塞值来迁就硬编码（＝造第二真源）；禁裸 `# noqa: gate-vocab`（NOQA-VALIDATION 会拦无理由豁免）。
- **实测样例**：qid `q-20260925-st-wm1-wave0-20260924-0018`（袋文件 `dead/q-20260925-st-wm1-wave0-20260924-0018.json`；requeued→`q-20260925-st-wm1-wave0-20260924-0027`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 GATE-VOCAB 阻断: [VOCAB-CHAIN] 新增 .py 文件含 SSoT 路径硬编码（应通过 capability_canonical_file_registry 反查发现，非硬编码）: src/zephyr/governance/registry_ledger/baseline.py: "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"; src/zephyr/governance/registry_ledger/baseline.py: "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"; src/zephyr/governance/registry_ledger/baseline.py: "docs/01_policies_and_standards/_registry/catalogs/rule_cata`
- 分身 census 簇：['GATE:GATE-VOCAB']

### 2.9 `FAM:cascade_stale` — 24 封
- **处方来源**：本包新拟
- **根因类别**：基底或竞态
- **子型分布（现读）**：{'STALE-BY-QID': 24}
- **涉及会话 top3**：[('st-audit-fix-20260924', 8), ('st-cmd-20260924', 4), ('st-commitspeed-tbl-20260924', 4)]
- **文件类型分布**：{'md': 53, 'py': 48, 'yaml': 28}
- **最小复现命令**：`python scripts/commit_queue.py status | grep <stale_by 点名 qid>`
- **照抄可用的修法**：前置袋已落地使基底重校验不适用 ⇒ 车道同步到当前 dev → requeue <qid> --adopt-prior-work（取工作树现字节）；同 payload 禁双 requeue。
- **禁止动作**：禁删 dead json（未落地字节唯一存活处）；禁手工把 blob 塞 index。
- **实测样例**：qid `q-20260925-st-cmd-20260924-0061`（袋文件 `dead/q-20260925-st-cmd-20260924-0061.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`cascade_stale: 基底重校验不适用 ['src/zephyr/strategy_pipeline/daily_gate_snapshot.py', 'src/zephyr/strategy_pipeline/daily_decision_orchestrator.py', 'src/zephyr/data/sector_state_pipeline.py', 'src/zephyr/signal_ashare/sector/sector_state_aggregator.py', 'scripts/backtest/sector_prereg_exam_runner.py', 'tests/strategy_pipeline/test_decision_orchestrator.py', 'tests/signal_ashare/sector/test_sector_state_aggregator.py', 'tests/data/test_sector_state_pipeline.py']（stale_by=q-20260925-st-cmd-20260924-0059）`
- 分身 census 簇：['cascade_stale(基底重校验不适用)']

### 2.10 `GATE:COMPLEXITY-GUARD` — 22 封
- **处方来源**：在册 R-3#11（在册原文：拆模块级 helper（参数 ≤7）；**禁调阈值**；用门禁自家 `_cyclomatic_complexity` 复算，别用第三方读数｜册面袋数：—）
- **根因类别**：内容违规
- **子型分布（现读）**：{'HIGH-COMPLEXITY': 18, '-': 4}
- **涉及会话 top3**：[('st-cmd-20260924', 9), ('st-metaq-20260923', 3), ('st-qcure-20260925', 2)]
- **文件类型分布**：{'py': 110, 'yaml': 43, 'md': 20, 'csv': 10, 'ps1': 2}
- **最小复现命令**：`python -c "from zephyr.gov_enforcement.commit_gates.complexity_guard import _cyclomatic_complexity" （门禁自家尺复算）`
- **照抄可用的修法**：拆模块级 helper（参数 ≤7）或查表法/策略模式；reason 点名行号即起点（实测 top：commit_queue_landing.py:_land_item complexity=42）。
- **禁止动作**：禁调阈值；禁第三方复杂度读数自证；禁 noqa 裸豁免。
- **实测样例**：qid `q-20260926-st-ddup-20260925-0028`（袋文件 `dead/q-20260926-st-ddup-20260925-0028.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 COMPLEXITY-GUARD 阻断: [NO-HIGH-COMPLEXITY] NO-HIGH-COMPLEXITY：检测到高循环复杂度函数（>15）， 违反 §5.158 循环复杂度反模式。 scripts/backtest/t1_t2_handover.py:357: run_acceptance(complexity=52 > 15) scripts/backtest/t1_t2_handover.py:629: build_t2_subspace(complexity=16 > 15) scripts/backtest/t1_t2_handover.py:827: run_handover(complexity=31 > 15) -> 考虑拆分为短函数/策略模式/查表法 [NO-LONG-PARAM-LIST] NO-LONG-PARAM-LIST：检测到长参数列表（>7参数）， 违反 §5.150 Long Parameter List 反模式。 scripts/backtest/t1_t2_handover.py:827: run_handover(13 p`
- **注**：与在册 R-3#11 同向，本包补 top 病灶点名。
- 分身 census 簇：['GATE:COMPLEXITY-GUARD']

### 2.11 `GATE:REFERENCE-INTEGRITY` — 18 封
- **处方来源**：在册 R-3#6（在册原文：**禁引用未登记裁定号**（工作树自赋 #414/#415 是悬空号）：改成文字描述，落地后经取号器正式补登｜册面袋数：2）
- **根因类别**：内容违规
- **子型分布（现读）**：{'RULING-DANGLING': 10, '-': 6, 'AGENTS-SECTION-DANGLING': 2}
- **涉及会话 top3**：[('st-audit-all-20260924', 4), ('st-mapbuild-20260924', 3), ('st-final-build-20260926', 3)]
- **文件类型分布**：{'md': 140, 'yaml': 38, 'py': 3}
- **最小复现命令**：`grep -n '^## \|^### ' AGENTS.md（拿真章节号）+ grep -c 'id: *<裁定号>' docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`
- **照抄可用的修法**：两子码两套修法（本包现读把两者并成同门 id，在册旧行只写了后者）：①子码 RULING-DANGLING=引用未登记裁定号 ⇒ 改文字描述，落地后经取号器正式补登（RULE-RULING 同 commit 原子）；②子码 AGENTS-SECTION-DANGLING=引用 AGENTS.md 不存在的 § ⇒ 以现读章节号改写引用或删该句（引用落笔前先 grep 命中，本案卷自犯教训在册）。
- **禁止动作**：禁自赋裁定号；禁改 AGENTS.md 章节号迁就引用；禁给 -D/-B 之类后缀猜号在册。
- **实测样例**：qid `q-20260925-st-commitspeed-tbl-20260924-0130`（袋文件 `dead/q-20260925-st-commitspeed-tbl-20260924-0130.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 REFERENCE-INTEGRITY 阻断: [ARCH-REFERENCE] 新增 ARCH-NNN（该议题号未登记于 architecture_issue_registry，非在册引用） 悬空引用（ARCH_REFERENCE_VIOLATION）——以下文件引用了 architecture_issue_registry.yaml 中未登记的编号： - docs/_working/commit_speedup_campaign/90_verification/CAMPAIGN_STATE_SNAPSHOT.md: ARCH-CROSS-COMMIT-ATOMICITY（该议题号未登记于 architecture_issue_registry，非在册引用） 修复：在 architecture_issue_registry.yaml 中补登对应条目，或移除/修正引用。（注：本门禁只检测新增引用，历史悬空引用不阻断。） [RULING-REFERENCE] 新增 裁定#NNN 悬空引用（RULING_REFERENCE_VIOLATION）——以下文件引用了 ruling_registry.yaml 中未登记的编号： - docs/_working/commit_speedup_campaign/60_deep_dive/r1_data/d_`
- **注**：RULING-REFERENCE 在预检白名单内仍死 ⇒ 同 degraded 面；在册 R-3#6 用子码当门名，现读门 id 是 REFERENCE-INTEGRITY。
- 分身 census 簇：['GATE:REFERENCE-INTEGRITY', 'GATE:REFERENCE-INTEGRITY(RULING-REFERENCE)']

### 2.12 `GATE:R5-DIGIT-SUFFIX` — 16 封
- **处方来源**：在册 R-3#8（在册原文：目录/文件名禁以数字结尾（判定式 `r"_\d+$"`，无白名单无逃生标）；已入库的历史违规按"已存在即跳过"｜册面袋数：多袋（一次违规拖死整袋））
- **根因类别**：内容违规
- **子型分布（现读）**：{'-': 16}
- **涉及会话 top3**：[('st-cmd-20260924', 7), ('st-qmine-20260925', 3), ('st-deepclean-20260923', 1)]
- **文件类型分布**：{'md': 105, 'yaml': 11, 'py': 4}
- **最小复现命令**：`python -c "import re;print(bool(re.search(r'_\d+$','registry_incident_20260922')))"`
- **照抄可用的修法**：目录/文件改名去 `_NN` 语义后缀（改用语义名，版本靠 message 不靠路径）；`git mv` 后 MUST python scripts/governance/generate_project_depgraph.py --force，并同步册内引用。
- **禁止动作**：此门无白名单无逃生标 ⇒ 禁试图加豁免或改判据；禁 git mv 后不重建 depgraph（RENAME-DEPGRAPH-SYNC 硬拦）。
- **实测样例**：qid `q-20260925-st-qmine-20260925-0008`（袋文件 `dead/q-20260925-st-qmine-20260925-0008.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 R5-DIGIT-SUFFIX 阻断: R5 数字后缀目录禁止: docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/ -> gov_doc_003_directory_semantics R5 禁止 _NN 数字后缀（暗示多真源，违反 SSoT 原则）。如需区分版本请用语义不同的目录名。`
- 分身 census 簇：['GATE:R5-DIGIT-SUFFIX']

### 2.13 `GATE:IMPORT-INTEGRITY` — 15 封
- **处方来源**：本包新拟
- **根因类别**：基底或竞态
- **子型分布（现读）**：{'DANGLING-IMPORT': 15}
- **涉及会话 top3**：[('st-commitspeed-tbl-20260924', 8), ('st-wm1-wave0-20260924', 3), ('st-k4-20260923', 1)]
- **文件类型分布**：{'py': 43, 'yaml': 6, 'md': 2}
- **最小复现命令**：`python -c "import importlib;importlib.import_module('<reason 点名模块>')"`
- **照抄可用的修法**：悬空 import 的目标模块未落地时：①与目标文件同袋；②目标在别的在途袋 ⇒ 等属主袋落地后 requeue；③外部库 ⇒ 先补 requirements 再投。
- **禁止动作**：禁注释掉 import '假修'（测试面会红）；禁自己造占位模块（CREATE-GUARD+ORPHAN-MODULE 双拦）。
- **实测样例**：qid `q-20260925-st-commitspeed-tbl-20260924-0084`（袋文件 `dead/q-20260925-st-commitspeed-tbl-20260924-0084.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 IMPORT-INTEGRITY 阻断: IMPORT-INTEGRITY: 悬空 import（目标模块不可解析，#ARCH-CROSS-COMMIT-ATOMICITY-001 治本） 病根：commit 引入了对不存在模块的 import——跨 commit 原子性违规 （import 语句先行于目标文件创建，多 session 并发无协调）。 修复：①将 import 与目标文件放同 commit； ②若目标文件已存在于其他分支，先 merge 再 import； ③若为外部库，先 pip install 并更新 requirements。 scripts/governance/commit_queue_landing.py:1756: dangling import 'zephyr.gov_enforcement.derived_dirty_ledger' (project module not resolvable in staged files or main HEAD) scripts/governance/commit_queue_landing.py:1`
- **注**：在册 R-3 无此行——本包新拟。跨袋原子性实证（本包自有证据）：门本体未落地时，读它的袋在 landing 侧整批崩，即 FAM:LandingEnvironmentError 的 ModuleNotFoundError 子型。
- 分身 census 簇：['GATE:IMPORT-INTEGRITY']

### 2.14 `FAM:CLAIM_REQUIRED_VIOLATION` — 14 封
- **处方来源**：本包新拟
- **根因类别**：工具自伤
- **子型分布（现读）**：{'-': 14}
- **涉及会话 top3**：[('st-ddup-20260925', 3), ('st-final-build-20260926', 3), ('st-align-dirty-20260924', 2)]
- **文件类型分布**：{'py': 39, 'yaml': 16, 'md': 14}
- **最小复现命令**：`python scripts/governance/lock_files.py status | grep <sid>`
- **照抄可用的修法**：落地侧按队列项 session 校 claim ⇒ python scripts/governance/lock_files.py acquire <file> <sid> 后 requeue；死会话 stale claim 挡道走 gateway.release_files('<死sid>', files) 再 claim。★本族 reason 里的路径是 .runtime\commit_queue\worktrees\w<N>\... ⇒ 队列自家 worktree 路径被判成目标文件，属队列工具自伤面，勿按车道文件去找 claim。
- **禁止动作**：禁改 ENQUEUE_SKIP_GATES（SESSION/CLAIM 的入队豁免是立法面）；禁给别的 session 名义 claim。
- **实测样例**：qid `q-20260927-st-final-build-20260926-0014`（袋文件 `dead/q-20260927-st-final-build-20260926-0014.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（CLAIM_REQUIRED_VIOLATION）: session 'st-final-build-20260926' 已注册但目标文件未 claim（claim 前移协议，宪法 RULE-WORKTREE「并发与提交」）: ['D:\\ZephyrAlpha\\.runtime\\commit_queue\\worktrees\\w1\\docs\\01_policies_and_standards\\_registry\\catalogs\\capability_canonical_file_registry.yaml', 'D:\\ZephyrAlpha\\.runtime\\commit_queue\\worktrees\\w1\\docs\\01_policies_and_standards\\_registry\\catalogs\\module_translation_registry.yaml', 'D:\\ZephyrAlpha\\.runtime\\commit_queue\\worktrees\\w1\\docs\\_working\\total_command_closeout\\wa`
- **注**：CLAIM-REQUIRED 被入队预检显式跳过（假红风暴实证 379 次）⇒ 这 14 封属'设计上的不可拦'，只能靠属主 claim 前移。
- 分身 census 簇：["OTHER:网关落盘失败（CLAIM_REQUIRED_VIOLATION）: session 's"]

### 2.15 `GATE:DEPGRAPH-ENFORCEMENT` — 12 封
- **处方来源**：在册 R-3#10（在册原文：`apply_depgraph.py --add-design-node`；重命名后 `generate_project_depgraph.py --force`｜册面袋数：—）
- **根因类别**：内容违规
- **子型分布（现读）**：{'-': 12}
- **涉及会话 top3**：[('st-commitspeed-tbl-20260924', 5), ('st-cmd-20260924', 3), ('st-commitspeed-pkg8-20260925', 2)]
- **文件类型分布**：{'py': 69, 'md': 38, 'yaml': 12, 'ps1': 2, 'patch': 1}
- **最小复现命令**：`python scripts/governance/apply_depgraph.py --add-design-node <path> <MOD-XX-NNN> <D_域> --granularity file --dry-run 类只读校（无 --dry-run 则读 PG nodes 计数）`
- **照抄可用的修法**：二选一：①先登记设计态 apply_depgraph.py --add-design-node；②施工完全量重扫 generate_project_depgraph.py --force（design 预登记节点自动转 producti…）。须在能连 depgraph PG 的主区跑。
- **禁止动作**：禁直写 PG nodes 表（RULE-SSOT：架构数据必经 apply_*.py）；禁造空壳模块凑登记。
- **实测样例**：qid `q-20260925-st-wm1-wave0-20260924-0031`（袋文件 `dead/q-20260925-st-wm1-wave0-20260924-0031.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 DEPGRAPH-ENFORCEMENT 阻断: [DEPGRAPH-WRITE-PATH] DEPGRAPH-WRITE-PATH：检测到 depgraph 写入权限参数 (read-only disabled / superuser / edge-delete enabled)， 但文件不在白名单中。裁定ARCH-DEPGRAPH（该议题号未登记于 architecture_issue_registry，非在册引用）_ACCESS_CONTROL 规定 仅以下文件可使用写入权限： - scripts/governance/apply_depgraph.py - scripts/governance/generate_project_depgraph.py - scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py - scripts/governance/_shared/constants.py - scripts/governance/sync_panorama_module.py - scripts/governance/generate_project_path_tree.py - scrip`
- 分身 census 簇：['GATE:DEPGRAPH-ENFORCEMENT']

### 2.16 `GATE:TEST-SOURCE-CONSISTENCY` — 11 封
- **处方来源**：本包新拟
- **根因类别**：内容违规
- **子型分布（现读）**：{'-': 11}
- **涉及会话 top3**：[('st-sweep-tail-20260923', 3), ('st-commitspeed-pkg8-20260925', 3), ('st-combine-20260923', 2)]
- **文件类型分布**：{'py': 72, 'yaml': 22, 'md': 16, 'json': 1, 'csv': 1}
- **最小复现命令**：`python scripts/governance/meta/gate_prerun.py --session <SID> --files "<逗号清单>" --message-file .runtime/tmp/<SID>/msg_<批名>.md`
- **照抄可用的修法**：测试 import 的符号在源码不存在 ⇒ 要么把源码符号改名同步进测试，要么删除该测试引用；符号确属另一在途袋新增 ⇒ 与那袋同批或等其落地。
- **禁止动作**：禁加 `# noqa` 式假修；禁删测试换绿。
- **实测样例**：qid `q-20260925-st-commitspeed-tbl-20260924-0045`（袋文件 `dead/q-20260925-st-commitspeed-tbl-20260924-0045.json`；requeued→`q-20260925-st-commitspeed-tbl-20260924-0060`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 TEST-SOURCE-CONSISTENCY 阻断: TEST-SOURCE-CONSISTENCY (§5.178)：检测到测试-源码符号漂移 测试文件 import 的符号在源码中不存在（名称漂移）。 tests/infrastructure/test_duckdb_runtime_gate.py:37: from zephyr.infrastructure.duckdb_runtime_gate import BareDuckDBConnectError -> 模块不存在（已删除/迁移？） tests/infrastructure/test_duckdb_runtime_gate.py:37: from zephyr.infrastructure.duckdb_runtime_gate import install -> 模块不存在（已删除/迁移？） tests/infrastructure/test_duckdb_runtime_gate.py:37: from zephyr.infrastructure.duckdb_runtime_gate import is`
- **注**：TEST-SOURCE-CONSISTENCY 在预检白名单内仍死 ⇒ 与 degraded fail-open/口径分歧两个候选解释一致（未实测真跑率）。
- 分身 census 簇：['GATE:TEST-SOURCE-CONSISTENCY']

### 2.17 `GATE:PERMANENT-SYSTEM-TRIGGER` — 11 封
- **处方来源**：本包新拟
- **根因类别**：内容违规
- **子型分布（现读）**：{'-': 11}
- **涉及会话 top3**：[('st-qmine-20260925', 3), ('st-cmd-20260924', 2), ('st-wm1-wave0-20260924', 2)]
- **文件类型分布**：{'py': 177, 'yaml': 22, 'md': 11, 'ps1': 10, 'html': 1}
- **最小复现命令**：`grep -n 'PERM-TRIGGER\|PERMANENT-SYSTEM-TRIGGER' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`
- **照抄可用的修法**：永久系统脚本禁时间触发：改事件订阅注册（先例见 reason 点名脚本的同类实现），删 cron/Timer/sleep-loop。
- **禁止动作**：禁加'仅测试用'cron；禁改门判据；禁靠 noqa。
- **实测样例**：qid `q-20260925-st-wm1-wave0-20260924-0026`（袋文件 `dead/q-20260925-st-wm1-wave0-20260924-0026.json`；requeued→`q-20260925-st-wm1-wave0-20260924-0030`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 PERMANENT-SYSTEM-TRIGGER 阻断: [MANUAL-ONLY-PERMANENT] 永久系统脚本使用 manual 触发模式（argparse/input/__main__+argv）但未注册事件订阅/自动触发（违反'永久系统必须全自动事件触发'铁律）: scripts/governance/registry_projection/registry_projection_generator.py`
- **注**：★名实不符实证：PREFLIGHT_GATES 白名单写的是 'PERM-TRIGGER'，死信门名是 'PERMANENT-SYSTEM-TRIGGER'（两者在 gate_registry 各自成 id）⇒ 预检面收不到真杀手的 id。
- 分身 census 簇：['GATE:PERMANENT-SYSTEM-TRIGGER']

### 2.18 `FAM:BASE-快照基底共祖冲突` — 11 封
- **处方来源**：本包新拟
- **根因类别**：基底或竞态
- **子型分布（现读）**：{'-': 11}
- **涉及会话 top3**：[('st-audit-fix-20260924', 3), ('st-cmd-20260924', 3), ('st-chief3-20260926', 2)]
- **文件类型分布**：{'md': 85, 'py': 84, 'yaml': 31, 'csv': 7, 'patch': 2}
- **最小复现命令**：`python scripts/commit_queue.py status（读该袋 base_head 与 dev 现 HEAD）`
- **照抄可用的修法**：reason 自带解法：同步工作区后重新入队（66 号 §6.4/§9.1）；重投带 --adopt-prior-work。
- **禁止动作**：禁改 base_head 字段硬过；禁手 git apply 到主区 index。
- **实测样例**：qid `q-20260925-st-t0-matrix-20260924-0035`（袋文件 `dead/q-20260925-st-t0-matrix-20260924-0035.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`冲突：快照基底 b3c52ff68ca2（与 dev 的共同祖先 03019f119b66）之后 dev 已推进且触及同路径 ['docs/_working/t0_matrix/FINAL_REPORT_t0_matrix_reexam.md', 'docs/_working/t0_matrix/REDEVID_mutation_probe_matrix.md', 'docs/_working/t0_matrix/T0_SCHEME_MATRIX.md', 'docs/_working/t0_matrix/reconcile_pack_v1_summary.csv', 'docs/_working/t0_matrix/t0_ceiling_daily.csv', 'docs/_working/t0_matrix/t0_ceiling_result.yaml', 'docs/_working/t0_matrix/t0_ceiling_verdict.md', 'scripts/audit/t0_ceiling_capacity_exam.py', 'scripts/audit/t0_conditional_e4_exam.py`
- 分身 census 簇：['OTHER:冲突：快照基底 0b3724ed148d（与 dev 的共同祖先 0b3724ed148', 'OTHER:冲突：快照基底 27449507e1c4（与 dev 的共同祖先 27449507e1c', 'OTHER:冲突：快照基底 461b25d0e8fc（与 dev 的共同祖先 461b25d0e8f', 'OTHER:冲突：快照基底 613dcc4f9cf8（与 dev 的共同祖先 613dcc4f9cf', 'OTHER:冲突：快照基底 77129e94b190（与 dev 的共同祖先 77129e94b19', 'OTHER:冲突：快照基底 9120a7aafc6f（与 dev 的共同祖先 9120a7aafc6']…

### 2.19 `GATE:BLUEPRINT-FORMAT` — 10 封
- **处方来源**：本包新拟
- **根因类别**：内容违规
- **子型分布（现读）**：{'-': 10}
- **涉及会话 top3**：[('st-cmd-20260924', 4), ('st-chainpile-20260922', 2), ('st-wm1-wave0-20260924', 2)]
- **文件类型分布**：{'py': 45, 'yaml': 4, 'md': 2, 'ps1': 1}
- **最小复现命令**：`python -c "import re;print(re.match(r'# \\[BLUEPRINT\\] (MOD-|SH-)', open('<file>',encoding='utf-8').readline()))"`
- **照抄可用的修法**：头部合规式：`# [BLUEPRINT] MOD-XXX | docs/03_modules/.../blueprint.md | §N.N`（tests/ 里也须有）；module_id 必 MOD-/SH- 前缀。
- **禁止动作**：禁空头部/SRC-XXX/DOM-XXX/路径当 module_id；禁自赋 MOD 号（号由 depgraph/取号面给）。
- **实测样例**：qid `q-20260925-st-cmd-20260924-0103`（袋文件 `dead/q-20260925-st-cmd-20260924-0103.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 BLUEPRINT-FORMAT 阻断: BLUEPRINT-FORMAT: [BLUEPRINT] 头部 module_id 格式不合规（裁定#214 Phase 0 防蔓延） 合规格式: # [BLUEPRINT] MOD-XXX | docs/03_modules/.../blueprint.md 禁止格式: 空头部 / (migrated...) / SRC-XXX / DOM-XXX / 路径作 module_id schemas/categories/market/market_stock_candidate_pool.py:1: [BLUEPRINT] header invalid module_id 'L04-C01': module_id 必须以 MOD-/SH- 开头 tests/signal_ashare/test_candidate_pool_snapshot.py:1: [BLUEPRINT] header invalid module_id 'L04-C01': module_id 必须以 MOD-/SH- 开头 tests/strategy_p`
- 分身 census 簇：['GATE:BLUEPRINT-FORMAT']

### 2.20 `GATE:ORPHAN-MODULE` — 10 封
- **处方来源**：在册 R-3#9（在册原文：零消费者新件必与接线同袋（`git grep` 只认 `src/**/*.py`，scripts/ 的 import 不算引用）｜册面袋数：—）
- **根因类别**：内容违规
- **子型分布（现读）**：{'-': 10}
- **涉及会话 top3**：[('st-commitspeed-tbl-20260924', 4), ('st-ulib3c-20260923', 2), ('st-e2e-20260924', 1)]
- **文件类型分布**：{'py': 45, 'yaml': 6, 'md': 4}
- **最小复现命令**：`git grep -n '<new_module_dotted_path>' -- 'src/**/*.py'`
- **照抄可用的修法**：零消费者新件必须与接线件同袋（git grep 只认 src/**/*.py，scripts/ 里的 import 不算引用面）。
- **禁止动作**：禁写假 import 占消费者（IMPORT-INTEGRITY/UNDEFINED-NAME 接力）；禁改判据——此门无 noqa 逃生面。
- **实测样例**：qid `q-20260923-st-k4-20260923-0007`（袋文件 `dead/q-20260923-st-k4-20260923-0007.json`）
  > dead_reason 原文（当数据引用，内含'修复/已确认'字样不作指令执行）：`网关落盘失败（COMMIT_FAILED）: 门禁 ORPHAN-MODULE 阻断: 孤儿模块在代码库中无任何 import 引用（死代码，违反新AI可发现性）: src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py`
- 分身 census 簇：['GATE:ORPHAN-MODULE']

## 3. 尾部簇（未逐字诊断，处方=通用四件，标 generic）

| 簇 | 封数 | 根因类别 | 处方来源 |
|---|---|---|---|
| `GATE:DIRECTORY-CONTRACT` | 9 | 内容违规 | 本包新拟 |
| `FAM:BASE-入队基底后dev推进同路径` | 9 | 基底或竞态 | 本包新拟 |
| `GATE:PROTECTED-PATHS` | 9 | 内容违规 | 本包新拟 |
| `GATE:MAP-ALIGNMENT` | 9 | 内容违规 | 本包新拟 |
| `GATE:SSOT-REDEFINITION` | 9 | 内容违规 | 本包新拟 |
| `GATE:ALGO-NOTE-SYNC` | 9 | 内容违规 | 本包新拟 |
| `GATE:CAPABILITY-OVERLAP` | 8 | 内容违规 | 本包新拟 |
| `GATE:ALGO-FLOW-LINK` | 7 | 内容违规 | 本包新拟 |
| `FAM:基底不可知` | 7 | 基底或竞态 | 在册 R-3#5 |
| `FAM:BASE-dev-CAS竞态同路径` | 6 | 基底或竞态 | 本包新拟 |
| `FAM:gate册条目坏-fresh-import亦败` | 6 | 环境或依赖 | 本包新拟 |
| `GATE:CAPABILITY-LOOKUP-REQUIRED` | 5 | 内容违规 | 本包新拟 |
| `GATE:NO-BARE-SQL` | 5 | 内容违规 | 本包新拟 |
| `GATE:CH-FINAL-GATE` | 4 | 内容违规 | 在册 R-3#13 |
| `GATE:MUTABLE-CONST-WITHOUT-FINAL` | 4 | 内容违规 | 本包新拟 |
| `FAM:landing-TimeoutExpired` | 4 | 环境或依赖 | 本包新拟 |
| `GATE:TABLE-NAME-REGISTRY` | 4 | 内容违规 | 本包新拟 |
| `GATE:NOQA-VALIDATION` | 3 | 内容违规 | 本包新拟 |
| `GATE:REGISTRY-MASS-DELETION` | 3 | 内容违规 | 在册 R-3#14 |
| `GATE:REAL-KEY-REFERENCE-SCAN` | 3 | 内容违规 | 本包新拟 |
| `GATE:FILE-PLACEMENT-TTL` | 3 | 内容违规 | 本包新拟 |
| `GATE:SESSION-REQUIRED` | 2 | 工具自伤 | 本包新拟 |
| `GATE:DATETIME-NOW-FORBIDDEN` | 2 | 内容违规 | 本包新拟 |
| `GATE:NO-HIGH-COMPLEXITY` | 1 | 内容违规 | 在册 R-3#11 |
| `FAM:prestage拒绝-gitignore快照路径` | 1 | 内容违规 | 本包新拟 |
| `GATE:NEW-FILE-DEPGRAPH-ENFORCEMENT` | 1 | 内容违规 | 在册 R-3#10 |
| `GATE:FILE-COPY` | 1 | 内容违规 | 本包新拟 |
| `GATE:HOT-FILE-BASE-FRESHNESS` | 1 | 基底或竞态 | 在册 R-3#14 |
| `GATE:FORGED-GW-MARKER` | 1 | 工具自伤 | 本包新拟 |
| `FAM:本包自撤` | 1 | 工具自伤 | 本包新拟 |
| `FAM:COMMIT_FAILED-nothing-to-commit` | 1 | 工具自伤 | 本包新拟 |
| `GATE:MSG-EXPOSURE` | 1 | 内容违规 | 本包新拟 |
| `GATE:MODULE-ID-CONSISTENCY` | 1 | 内容违规 | 本包新拟 |
| `GATE:MSG-STYLE` | 1 | 内容违规 | 本包新拟 |
| `FAM:BASE-dev-CAS重试耗尽` | 1 | 基底或竞态 | 本包新拟 |
| `GATE:RELATIVE-PATH-LITERAL` | 1 | 内容违规 | 本包新拟 |
| `GATE:EXEMPT-ZONE-FM` | 1 | 内容违规 | 本包新拟 |
| `GATE:UNDEFINED-NAME` | 1 | 内容违规 | 本包新拟 |
| `GATE:ENCODING-SAFETY` | 1 | 内容违规 | 在册 R-3#12 |
| `GATE:FUNCTION-DUP` | 1 | 内容违规 | 本包新拟 |
| `FAM:WorktreePunchThroughError` | 1 | 工具自伤 | 在册 R-3#7 |
| `GATE:DOC-HEADER-SUITE` | 1 | 内容违规 | 本包新拟 |
| `FAM:landing-git-reset硬复位超时` | 1 | 工具自伤 | 在册 R-3#7 |

## 4. 结构性可预防项（入队口能拦而未拦）

- 预检白名单（现读 `commit_preflight.py::PREFLIGHT_GATES ∪ _INLINE_PREFLIGHT_CHECKS`，共 22 道）：`ARCH-REFERENCE, CAPABILITY-LOOKUP-REQUIRED, CLAIM-REQUIRED, COMMIT-SCOPE, CREATE-GUARD, DATETIME-NOW-FORBIDDEN, DIRECTORY-CONTRACT, EXEMPT-ZONE-FM, FILE-PLACEMENT-TTL, FOLDER-CAPACITY-HARD-LIMIT, MANUAL-ONLY-PERMANENT, NO-BARE-SQL, PERM-TRIGGER, PROTECTED-PATHS, REGISTRY-MASS-DELETION, RULING-REFERENCE, SESSION-REQUIRED, TABLE-NAME-REGISTRY, TEST-SOURCE-CONSISTENCY, TRANSLATION-COVERAGE, TTL-METADATA, WORKTREE-REQUIRED`
- 入队面显式跳过（`enqueue_preflight.py::ENQUEUE_SKIP_GATES`）：`CLAIM-REQUIRED, SESSION-REQUIRED`

**判据**：门 id 出现在死信 reason 且不在预检面 ⇒ '入队不检、落地必死'。

| 门 id（死信现读） | 累计封数 | 在预检面 | 备注 |
|---|---|---|---|
| `GATE-PRECOMMIT-RUN` | 85 | 否 | GATE-PRECOMMIT-RUN 不在 gate_registry.yaml 的 gate_id 集内（落地侧 runner，非注册门） |
| `CREATE-GUARD` | 68 | 是 | CREATE-GUARD 已在 _INLINE_PREFLIGHT_CHECKS 内联面仍大量死 ⇒ 两个候选解释：预检 degraded  |
| `TRANSLATION-COVERAGE` | 55 | 是 | 在册 R-3#2 只说'在主仓跑'，未量化 55 封里 worktree 跑占多少——本包按 facet 现读补齐。 |
| `TTL-METADATA` | 33 | 是 | reason 里的路径是 .runtime\commit_queue\worktree(s)\w<N>\... ⇒ 门读落地快照盘面而非车道 |
| `GATE-VOCAB` | 24 | 否 |  |
| `COMPLEXITY-GUARD` | 22 | 否 | 与在册 R-3#11 同向，本包补 top 病灶点名。 |
| `REFERENCE-INTEGRITY` | 18 | 否 | RULING-REFERENCE 在预检白名单内仍死 ⇒ 同 degraded 面 |
| `R5-DIGIT-SUFFIX` | 16 | 否 |  |
| `IMPORT-INTEGRITY` | 15 | 否 | 在册 R-3 无此行——本包新拟。跨袋原子性实证（本包自有证据）：门本体未落地时，读它的袋在 landing 侧整批崩，即 FAM:Land |
| `DEPGRAPH-ENFORCEMENT` | 12 | 否 |  |
| `TEST-SOURCE-CONSISTENCY` | 11 | 是 | TEST-SOURCE-CONSISTENCY 在预检白名单内仍死 ⇒ 与 degraded fail-open/口径分歧两个候选解释一致（ |
| `PERMANENT-SYSTEM-TRIGGER` | 11 | 否 | ★名实不符实证：PREFLIGHT_GATES 白名单写的是 'PERM-TRIGGER'，死信门名是 'PERMANENT-SYSTEM- |
| `BLUEPRINT-FORMAT` | 10 | 否 |  |
| `ORPHAN-MODULE` | 10 | 否 |  |
| `DIRECTORY-CONTRACT` | 9 | 是 |  |
| `PROTECTED-PATHS` | 9 | 是 | ★实测连坐面：本族 9 封 + GATE-PRECOMMIT-RUN 内层 top 病灶同为 protected-paths ⇒ 同判据两处 |
| `MAP-ALIGNMENT` | 9 | 否 |  |
| `SSOT-REDEFINITION` | 9 | 否 |  |
| `ALGO-NOTE-SYNC` | 9 | 否 |  |
| `CAPABILITY-OVERLAP` | 8 | 否 |  |
| `ALGO-FLOW-LINK` | 7 | 否 |  |
| `CAPABILITY-LOOKUP-REQUIRED` | 5 | 是 |  |
| `NO-BARE-SQL` | 5 | 是 |  |
| `CH-FINAL-GATE` | 4 | 否 |  |
| `MUTABLE-CONST-WITHOUT-FINAL` | 4 | 否 |  |
| `CREATE-GUARD` | 4 | 是 |  |
| `TABLE-NAME-REGISTRY` | 4 | 是 |  |
| `NOQA-VALIDATION` | 3 | 否 |  |
| `REGISTRY-MASS-DELETION` | 3 | 是 |  |
| `REAL-KEY-REFERENCE-SCAN` | 3 | 否 | 此 id 不在 gate_registry.yaml 的 gate_id 集内（现读 181 id 无此名）⇒ 执法面在别处，预检白名单无从 |
| `FILE-PLACEMENT-TTL` | 3 | 是 |  |
| `SESSION-REQUIRED` | 2 | 是 | 入队面显式跳过；SESSION-REQUIRED 在 PREFLIGHT_GATES 内却被 ENQUEUE_SKIP_GATES 显式跳过（入队面假红风暴 |
| `DATETIME-NOW-FORBIDDEN` | 2 | 是 |  |
| `NO-HIGH-COMPLEXITY` | 1 | 否 | COMPLEXITY-GUARD 与 NO-HIGH-COMPLEXITY 在 gate_registry 各自成条，死信文案同判据 ⇒ 建 |
| `NEW-FILE-DEPGRAPH-ENFORCEMENT` | 1 | 否 | 与 GATE:DEPGRAPH-ENFORCEMENT 处方完全同真源 ⇒ 建议 R-3 并为一行。 |
| `FILE-COPY` | 1 | 否 | 实测样例的比对基准含 `.runtime\commit_queue\worktree\...` 自身路径 ⇒ 门在落地快照面比对，车道内自证 |
| `HOT-FILE-BASE-FRESHNESS` | 1 | 否 |  |
| `FORGED-GW-MARKER` | 1 | 否 | 在册 R-3 无此行（§9.8 已列红线但未入表）。 |
| `MSG-EXPOSURE` | 1 | 否 |  |
| `MODULE-ID-CONSISTENCY` | 1 | 否 |  |
| `MSG-STYLE` | 1 | 否 |  |
| `RELATIVE-PATH-LITERAL` | 1 | 否 |  |
| `EXEMPT-ZONE-FM` | 1 | 是 |  |
| `UNDEFINED-NAME` | 1 | 否 |  |
| `ENCODING-SAFETY` | 1 | 否 |  |
| `FUNCTION-DUP` | 1 | 否 |  |
| `DOC-HEADER-SUITE` | 1 | 否 | 此门 reason 具误导性（门名≠判据名）：照抄修法必须以 reason 尾行点名的内层判据为准。 |

- **在死信出现但预检不收的门 id 共 32 条**：`ALGO-FLOW-LINK, ALGO-NOTE-SYNC, BLUEPRINT-FORMAT, CAPABILITY-OVERLAP, CH-FINAL-GATE, COMPLEXITY-GUARD, DEPGRAPH-ENFORCEMENT, DOC-HEADER-SUITE, ENCODING-SAFETY, FILE-COPY, FORGED-GW-MARKER, FUNCTION-DUP, GATE-PRECOMMIT-RUN, GATE-VOCAB, HOT-FILE-BASE-FRESHNESS, IMPORT-INTEGRITY, MAP-ALIGNMENT, MODULE-ID-CONSISTENCY, MSG-EXPOSURE, MSG-STYLE, MUTABLE-CONST-WITHOUT-FINAL, NEW-FILE-DEPGRAPH-ENFORCEMENT, NO-HIGH-COMPLEXITY, NOQA-VALIDATION, ORPHAN-MODULE, PERMANENT-SYSTEM-TRIGGER, R5-DIGIT-SUFFIX, REAL-KEY-REFERENCE-SCAN, REFERENCE-INTEGRITY, RELATIVE-PATH-LITERAL, SSOT-REDEFINITION, UNDEFINED-NAME`
- **另三条治本面（非'加白名单'可解）**：①**预检 degraded fail-open**——已在预检面的 15 个簇累计 214 封死信（明细 [['GATE:CREATE-GUARD', 68], ['GATE:TRANSLATION-COVERAGE', 55], ['GATE:TTL-METADATA', 33], ['GATE:TEST-SOURCE-CONSISTENCY', 11], ['GATE:DIRECTORY-CONTRACT', 9], ['GATE:PROTECTED-PATHS', 9]]…），说明**拦不住的主因是预检没真跑成（设施异常放行）而非白名单缺项**；②基底/竞态/环境族（FAM:BASE-*、cascade_stale、NOTHING_TO_COMMIT、LandingEnvironmentError）的输入面是**主区依赖态与 dev 推进态**，入队口结构上判不了 ⇒ 需在落地侧重试/等待语义里治，不属预检扩容；③GATE-PRECOMMIT-RUN 是落地侧 runner 不在 gate_registry 门 id 集内，其内层判定（protected-paths/naming/format/冲突标记）虽各有独立门，但聚合面在预检里不可见——建议把这四路内层判据并入预检。

## 5. 与在册 §R-3 逐行 diff（新增 / 修订 / 冲突）

| §R-3 行 | 册面签名 | 册面袋数 | 本包现读封数 | 判定 | 证据 |
|---|---|---|---|---|---|
| #1 | 注册表三向合并失败（家族） | 71（其中全文指名身份键 7） | 72 | **冲突** | 在册把整族判为'基底病'（走 R-1 修基底），现读 70/72 封（97%）子型全在 **ours 侧**：同侧身份键重复 32 + 存在身份判不了的条目 38 ⇒ 病灶是袋内该册条目自身（重复键/非 dict 条目），修基底不解决；该行应拆两型并各给处方 |
| #2 | TRANSLATION-COVERAGE | 11（六图役） | 55 | **修订** | 在册袋数 11（六图役） vs 现读 55（差 +44） |
| #3 | CREATE-GUARD | 8（六图役）+ 全局多封 | 68 | **修订** | 在册袋数 8（六图役）+ 全局多封 vs 现读 68（差 +60） |
| #4 | GATE-PRECOMMIT-RUN | 2 | 85 | **冲突** | 在册处方='落地侧门禁账缺失 ⇒ 先跑预跑'；现读 85 封中 72 封的 reason 尾行点名具体内层失败步 {'INNER_FAIL:LINT': 27, 'INNER_FAIL:HOOK-GATE-PROTECTED-PATHS': 17, 'INNER_FAIL:HOOK-RUFF-FORMAT': 16} ⇒ 真病灶是被该 runner 聚合的内层门（protected-paths/lint/naming/conflict-marker），处方须指向'读尾行点名的内层门'而非'补门禁账'；且在册袋数 2 vs 现读 85 |
| #5 | 基底不可知 | 2 | 7 | **修订** | 在册袋数 2 vs 现读 7（差 +5） |
| #6 | RULING-REFERENCE | 2 | 18 | **冲突** | 在册签名把子码当门名（'RULING-REFERENCE'），现读门 id='REFERENCE-INTEGRITY'；该门现读两子码并存：裁定号悬空 10 封 + 宪法 §号悬空 2 封，两者处方不同 ⇒ 该行应改写为'REFERENCE-INTEGRITY#RULING-DANGLING' 并新增一行 '#AGENTS-SECTION-DANGLING' |
| #7 | `WorktreePunchThroughError`（EV-02 reset 打穿主仓） | ≥1 | 2 | **修订** | 一个在册行覆盖现读多门 id ['FAM:WorktreePunchThroughError', 'FAM:landing-git-reset硬复位超时']（建议拆行或注明同判据） |
| #8 | R5-DIGIT-SUFFIX | 多袋（一次违规拖死整袋） | 16 | **一致** |  |
| #9 | ORPHAN-MODULE | — | 10 | **一致** |  |
| #10 | NEW-FILE-DEPGRAPH / DEPGRAPH-ENFORCEMENT | — | 13 | **修订** | 一个在册行覆盖现读多门 id ['DEPGRAPH-ENFORCEMENT', 'NEW-FILE-DEPGRAPH-ENFORCEMENT']（建议拆行或注明同判据） |
| #11 | COMPLEXITY >15 | — | 23 | **修订** | 一个在册行覆盖现读多门 id ['COMPLEXITY-GUARD', 'NO-HIGH-COMPLEXITY']（建议拆行或注明同判据） |
| #12 | ENCODING-SAFETY | — | 1 | **一致** |  |
| #13 | CH-FINAL-GATE | — | 4 | **一致** |  |
| #14 | REGISTRY-MASS-DELETION / HOT-FILE-BASE-FRESHNESS | — | 4 | **修订** | 一个在册行覆盖现读多门 id ['REGISTRY-MASS-DELETION', 'HOT-FILE-BASE-FRESHNESS']（建议拆行或注明同判据） |
| #15 | `skipped_dirty` 类信号 | 1802/1805 | 0 | **本窗零命中** | 现读 dead/ 无任何袋命中原签名（在册行仍留，勿据本窗删） |

- **新增建议行 = 45 行**（未命中任何在册行的处方族；下表列 Top14），**修订建议 = 7 行**（在册袋数与现读偏差 ≥5 或一行覆盖多门 id 需拆），**与既有冲突 = 3 行**（在册判据方向与盘面证据相反，均以盘面为准，证据见上表）；本窗零命中 = 1 行、一致 = 4 行。
- 在册 §R-3 共 15 行，命中 14 行；未命中行 [15]（零命中≠无效，勿据此删行）。

| 建议并入 §R-3 的新行（signature → 四件摘要） |
|---|
| `FAM:LandingEnvironmentError`（38 封）→ 根因=环境或依赖；修法=落地侧主区 gate 模块 import 失败（ModuleNotFoundError / gate 册条目坏）⇒ 属主会话把门本体+它读的册同袋落主区；本袋只等环境修好后 requeue --adopt-prior-work。子型 PRI…；禁=不是内容病：禁改本袋内容自证；禁删/注释自家 gate 注册；禁在本袋里顺手造别人的门模块。… |
| `GATE:TTL-METADATA`（33 封）→ 根因=内容违规；修法=按现读四子型各一条：①NO-FRONTMATTER=新建 .md 完全没有题记 ⇒ 补 `ttl: task_bound` + `completes_when:` 两键（本包产物头部即合规写法）；②MISSING-TTL-FIELD=有题记…；禁=禁给临时区件写 ttl: permanent（FILE-PLACEMENT-TTL 接力拦）；禁删题记/删 doc_type 绕过；禁改门允许的键集或放宽必填判… |
| `FAM:NOTHING_TO_COMMIT`（31 封）→ 根因=工具自伤；修法=防线语义='快照 blob 与 old_dev 不符，应用静默丢失' ⇒ 车道同步后重新入队取新字节；若盘面已等 dev ⇒ 本袋确无事可提交，走 dead_reason 属主会话复核（不删件）。…；禁=禁 `git apply`/update-index 手工塞（§9.8 plumbing 红线）；禁删 dead 袋；禁把这条防线判成'门的错'去改它。… |
| `GATE:GATE-VOCAB`（24 封）→ 根因=内容违规；修法=把 VALID_LAYERS/VALID_STATUSES 这类硬编码合法值改成从 docs/01_policies_and_standards/_registry/**/*_vocabulary.yaml 动态加载（复用既有 vocabu…；禁=禁往词表塞值来迁就硬编码（＝造第二真源）；禁裸 `# noqa: gate-vocab`（NOQA-VALIDATION 会拦无理由豁免）。… |
| `FAM:cascade_stale`（24 封）→ 根因=基底或竞态；修法=前置袋已落地使基底重校验不适用 ⇒ 车道同步到当前 dev → requeue <qid> --adopt-prior-work（取工作树现字节）；同 payload 禁双 requeue。…；禁=禁删 dead json（未落地字节唯一存活处）；禁手工把 blob 塞 index。… |
| `GATE:IMPORT-INTEGRITY`（15 封）→ 根因=基底或竞态；修法=悬空 import 的目标模块未落地时：①与目标文件同袋；②目标在别的在途袋 ⇒ 等属主袋落地后 requeue；③外部库 ⇒ 先补 requirements 再投。…；禁=禁注释掉 import '假修'（测试面会红）；禁自己造占位模块（CREATE-GUARD+ORPHAN-MODULE 双拦）。… |
| `FAM:CLAIM_REQUIRED_VIOLATION`（14 封）→ 根因=工具自伤；修法=落地侧按队列项 session 校 claim ⇒ python scripts/governance/lock_files.py acquire <file> <sid> 后 requeue；死会话 stale claim 挡道走 gat…；禁=禁改 ENQUEUE_SKIP_GATES（SESSION/CLAIM 的入队豁免是立法面）；禁给别的 session 名义 claim。… |
| `GATE:TEST-SOURCE-CONSISTENCY`（11 封）→ 根因=内容违规；修法=测试 import 的符号在源码不存在 ⇒ 要么把源码符号改名同步进测试，要么删除该测试引用；符号确属另一在途袋新增 ⇒ 与那袋同批或等其落地。…；禁=禁加 `# noqa` 式假修；禁删测试换绿。… |
| `GATE:PERMANENT-SYSTEM-TRIGGER`（11 封）→ 根因=内容违规；修法=永久系统脚本禁时间触发：改事件订阅注册（先例见 reason 点名脚本的同类实现），删 cron/Timer/sleep-loop。…；禁=禁加'仅测试用'cron；禁改门判据；禁靠 noqa。… |
| `FAM:BASE-快照基底共祖冲突`（11 封）→ 根因=基底或竞态；修法=reason 自带解法：同步工作区后重新入队（66 号 §6.4/§9.1）；重投带 --adopt-prior-work。…；禁=禁改 base_head 字段硬过；禁手 git apply 到主区 index。… |
| `GATE:BLUEPRINT-FORMAT`（10 封）→ 根因=内容违规；修法=头部合规式：`# [BLUEPRINT] MOD-XXX | docs/03_modules/.../blueprint.md | §N.N`（tests/ 里也须有）；module_id 必 MOD-/SH- 前缀。…；禁=禁空头部/SRC-XXX/DOM-XXX/路径当 module_id；禁自赋 MOD 号（号由 depgraph/取号面给）。… |
| `GATE:DIRECTORY-CONTRACT`（9 封）→ 根因=内容违规；修法=DCR-005/DCR-008：docs/_working/ 只收 .md/.csv/.yaml/.html —— .json/.py 产物移到其注册用途目录（生成器产物走 data/ 或 docs/library/），改完同袋重投。…；禁=禁往 allowed 清单塞扩展名（那是改判据）；禁把产物写进 .runtime 根。… |
| `FAM:BASE-入队基底后dev推进同路径`（9 封）→ 根因=基底或竞态；修法=同路径被上游推进 ⇒ 车道同步（读上游新字节）→ 重做增量编辑 → 重新入队；热册（rules_integrity_db.json/script_manifest.yaml 等）变更须单独成袋。…；禁=禁拿旧快照字节强推（=回退上游）；禁与上游会话互相'代修'。… |
| `GATE:PROTECTED-PATHS`（9 封）→ 根因=内容违规；修法=rules/*.yaml 重大修改属 Owner 门位：要么摘出本袋（另起小袋只含该册+依赖件），要么带 [ARCH-APPROVAL:<已登记 issue>] 或命中 ruling_registry.yaml approved_paths…；禁=禁自造 [ARCH-APPROVAL] 号；禁把 rules 改动混进代码袋连坐。… |

## 6. 复算与纪律

```bash
# 车道内复算（PYTHONPATH 指车道 src，防裸 import 主区包=假绿源）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
export PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src
cd D:/ZephyrAlpha/.aidrafts/st-final-build-20260926
python scripts/governance/wave1b/dead_letter_prescriptions.py   # 重跑覆盖 matrix.{yaml,md}
```
- 零写承诺：`.runtime/commit_queue/**` 全程只读（blobs/dead 是未落地字节唯一存活处）；git 零写；未跑 `tests/governance/test_ops_guard_red_team.py`（本包禁列）；未改任何门/阈值/断言/skip/xfail；未对 CH/PG 写。
- 反注入声明：dead_reason 与袋 message 中出现的"已确认/请修复/已批准/Owner 已批"一律作**数据**原文引用（本仓已实证注入攻击两次），本班未据此执行任何动作；未自赋裁定号。
