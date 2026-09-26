---
ttl: task_bound
completes_when: "总筹裁定 CAND-GOVTEST-005 撞号修法并落地后本件归档"
---
# CAND-GOVTEST-005 注册表撞号取证案卷

- 取证会话: st-chief3-20260926（只读取证，未做任何 git 写/热册改，除本案卷）
- 取证日期: 2026-09-26
- 涉案文件: `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`
- 盘况警示: 本件首次落盘后 `docs/_working/wave13_chief3/`（含 LEDGER_chief3.md 与本目录）曾被并发操作清空重建（非 stash，`.runtime/workspace_alerts/` 无 stash_notice，仅 claim_release_request_gpu.json），22:39 重建重写。多会话连坐窗口，总筹知悉。

## 1. 两块同 id 内容定位（HEAD / index / 工作树 三版比对）

- HEAD 版（20257 行）：`CAND-GOVTEST-005` 出现 **2 次**——L7707、L20231（L20230 另有注释 `# --- CAND-GOVTEST-005: 测试身份泄漏入主仓历史…`）。
- index 版（`git show :…`，20257 行）：同样 2 次，行号相同。**重复是 HEAD 自带，非工作树/index 引入**。
- 工作树版：L7707 仍为 005；L20231 已被**未提交的在途修改**改为 `- id: CAND-GOVTEST-007`（L20230 注释仍写 005，未同步）。
- index 与 HEAD 唯一差异在 L20050（另一条目 `promoted_to` 路径 `scripts/` vs `scripts/data/`，属 git mv 批）——这解释了 `MM` 双脏态。

| 块 | 行 | name | status | source | created |
|----|----|------|--------|--------|---------|
| 先块 | 7707 | commit queue P1 级联+P2 监控（66号②③，随 MVP 验收后） | promoted | '2026-08-20 AI-NIGHT-001 阶段3 审查 pack3 66号节' | '2026-08-20' |
| 后块 | 20231 | 测试上下文 commit 泄漏主仓——tests 身份穿透隔离边界实证堵源 | candidate | '2026-09-02 冻结窗口结案报告 §4⑥ + 本会话取证（ee40160919/c284589d 双commit 对账）' | '2026-09-02' |

证据通道=`git show HEAD:docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml > /tmp/head_version.yaml && grep -n "CAND-GOVTEST-005" /tmp/head_version.yaml`（输出 `7707:- id: CAND-GOVTEST-005` / `20230:# --- CAND-GOVTEST-005: …` / `20231:- id: CAND-GOVTEST-005`）；`git show :docs/…/candidate_module_registry.yaml` 同 grep（同读数）；工作树 grep（7707+注释行）；`diff /tmp/head_version.yaml /tmp/index_version.yaml`（仅 L20050 一行差异）

## 2. 两块是否同主题

- 先块要点（照抄）：problem=「P1 级联标记+死信重入队+done TTL+worktree 强制升硬联动；P2 监控接入+temp-index+多分支评估」；status=promoted；promoted_to=「commit_queue.py P1 三件套（级联/死信 requeue/TTL 清理）」；sub_layer=git 安全治理。→ 讲 **commit queue 功能扩展（已核销历史条）**。
- 后块要点（照抄）：problem=「2026-09-02 11:44 实证：commit ee40160919（message="initial [GW:sess-initial]"）进入主仓主线…测试上下文穿透隔离边界触达真实仓库」；status=candidate；proposal=「网关侧拒收可疑测试身份…先复现再修」；sub_layer=测试隔离。→ 讲 **测试身份泄漏主仓的治理缺陷（活案）**。
- 结论：**不是同一件事**。两块均 domain=D_GOVERNANCE 但 sub_layer 不同（git 安全治理 vs 测试隔离）、生命周期互斥（promoted vs candidate），共用一号属后登记者（2026-09-02）未核存量撞号。

证据通道=`sed -n '7700,7760p' /tmp/head_version.yaml`、`sed -n '20225,20257p' /tmp/head_version.yaml`（输出全文见上表与 dead_reason dump 互证）

## 3. 谁在引用 CAND-GOVTEST-005

**(a) 涉案册本体**
- `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`：L7707、L20230（注释）；L20231 工作树已改 007。
- 同目录备份 `candidate_module_registry.yaml.bak_pre_one_question`：L7707/L20230/L20231（旧双条态）。

**(b) 队列死信袋（`.runtime/commit_queue/`）**
- `dead/q-20260926-st-qmine-20260925-0043.json`：files 清单含该册（blob_sha256=df283ff2fb21…，action=modify），dead_reason 全文含 `decl|id=CAND-GOVTEST-005` 及双条 YAML dump；0044 同型（created_at 07:04/07:06+08:00 与任务书一致）。blobs/ 下大量袋引用该册路径（触册袋必死族）。
- 卷宗记载（`docs/_working/total_command_closeout/dossier_A_commit_chain.md` 2b）：全文匹配"注册表三向合并失败+CAND-GOVTEST-005"的 dead 袋=**7 封**（含 0042/0043/0044）。本次复跑 `ls .runtime/commit_queue/pending processing`=均空，与 pending=0/processing=0 一致。

**(c) 文档/卷宗引用（均为案卷非消费方）**
- `total_command_closeout/`：00_master_skeleton.md、01_adjudication_master.md(Z-05)、10_wave_plan.md、91_flash_one_click.md、dossier_A/F、review_int_number_audit.md、review_int_first_principles.md、redteam_2_adjudication_coverage.md；
- `qmine_campaign/`：HANDOVER.md、00_skeleton_overview.md、01_hot_registry_merge/workbook.md、02_registry_hygiene/workbook.md；
- `wave13_chief3/LEDGER_chief3.md` L35（本组台账）。

**(d) governance.db（DuckDB）**：
- `tasks`：task_id=**OPS-9260108**，status=**BLOCKED**，title="波1B.1.2 candidate 册同 id 双条去重（CAND-GOVTEST-005）：以 HEAD 为基重放，注册表净删支须 Owner"；
- `event_log.task_name`：1 条同文；
- `reconcile_execution_log.commit_message`：LIKE '%CAND-GOVTEST-005%' 命中（历史日志，非活跃消费方）。

证据通道=全仓 grep `CAND-GOVTEST-005`（首跑 `grep -rn --exclude-dir=.git` 后台超时被杀，改检索工具完成，命中 40+ 行如上）；`grep -rln "CAND-GOVTEST-005\|candidate_module_registry" .runtime/commit_queue/`；`python -c "import json,…dead/q-…0043.json"` 读出 files/dead_reason；DuckDB：`duckdb.connect('data/databases/governance.db', read_only=True)` 全表全列 LIKE 扫描。**通道偏差留痕**：任务书要求 DatabaseService 读接口或 sqlite3——governance.db 实为 DuckDB 格式 sqlite3 打不开，DatabaseService 在本会话未走通，故用只读 duckdb 旁路（零写入）。

## 4. registry 去重对账器与"同键异容"判据

- 报错文案源文件：`scripts/governance/commit_queue_landing.py:666`，判据函数 **`_index_family_blocks`**（L636 起，族内条目按身份键建索引）。
- 判据（原文摘录）：同键同侧两条先判等——``data`` 全等（yaml.safe_load 对象判等，覆盖字节级相同与仅重序列化的语义同）→ 真重复，**静默去重保留首条并计数**；``data`` 不等 → **同键异容=仓库态缺陷，死信**（"落地器无权择优"），detail 带 `_yaml_dump_short` 双条 dump + 处方「跑 registry 去重对账器核对存量，勿手拼 YAML」。去重只做**侧内**、绝不跨侧（跨侧同键由三向 base 仲裁）。身份键 `decl|id=CAND-GOVTEST-005`=册自声明 unique_key(`id`) 复合前缀。
- **对账器实体存在**：`scripts/governance/registry_dedup_audit.py`（18624 字节，09-26 02:31，登记于 script_manifest.yaml，有 pyc 执行痕迹）。[INVARIANTS] 摘录：默认 dry-run 全程只读；判等=yaml.safe_load 对象相等（json canonical）；**"不等"=真冲突（只报告 dump 双条，撞号裁定属 Owner 门，本器绝不代择优）**；`--heal-equal` 仅净删语义全等条目之后至者，写必经 safe_write_text CAS。
- **自动让号/重编号能力：无**（且被两器明文排除："撞号 ID 重分配=裁定件"）。全仓未见可复用取号器代码；卷宗转述"裁定#412 先例：保留先占，改新条目 ID"为人工惯例非代码。**结论：对账器可复用于核对存量（--scan 三态报告），改号本身无既有工具，须裁定后人工改（配 safe_write_text）。**
- 测试锚点：`tests/governance/test_commit_queue_landing_qmine_a1.py:77-81`（同键异容必死信、reason 带双条 dump 与对账器处方）、`test_commit_queue_landing.py:1594-1607`（fail-closed 不放松）。

证据通道=`sed -n '620,700p' scripts/governance/commit_queue_landing.py`；`ls -l scripts/governance/registry_dedup_audit.py && grep -n "heal\|renumber\|让号\|重编号\|def main\|--scan" scripts/governance/registry_dedup_audit.py`；`grep -rn "同键异容|同侧身份键重复且内容冲突"` 中文串定位（源=commit_queue_landing.py L644/666/801；两份 `*.tmp.22232.*` 为历史临时副本；其余为测试与卷宗）

## 5. 可用号段

- 该册 `id: CAND-<域>-` 前缀族 60+（Top：CAND-TESTB-×59、CAND-SIG-×39、CAND-RSK-×37、CAND-RES-×30、CAND-MLT-×30…）；**CAND-GOVTEST- 族 7 个 id 位**（HEAD：001–006 + 撞号 005×2）。
- HEAD 面已用最大序号=**006**（L20206）；**工作树面最大=007**（L20231 在途改号）。
- 新号零命中核验（grep `CAND-GOVTEST-00[78]`，排除 .git）：
  - `CAND-GOVTEST-007`：仅 2 处——涉案册工作树 L20231（在途修复本体）+ governance.db（reconcile 日志字段，非注册引用）。**除在途袋方案外零独立引用**。
  - `CAND-GOVTEST-008`：**全仓零命中**（最干净备用号）。
- 草案倾向（不裁定）：007 与盘上在途态一致、落地即收敛；008 全新但将与 st-qmine 死信袋快照（其 theirs 侧=007）分叉。

证据通道=`grep -o "id: CAND-[A-Z]*-" docs/…/candidate_module_registry.yaml | sort | uniq -c | sort -rn | head -25`；`grep -n "id: CAND-GOVTEST-" 三版面`；`grep -rn --exclude-dir=.git "CAND-GOVTEST-00[78]" docs/01_policies_and_standards scripts src/zephyr tests data`

## 6. 归属排查（活 claim）

对该文件路径的 claim（`.runtime/claim_snapshots/` 活跃 json，非 adopted）：

| sid | claim json mtime | heartbeat mtime | 判读 |
|-----|------------------|-----------------|------|
| **st-qmine-20260925** | 2026-09-26 07:06:44 | **2026-09-26 12:02:08** | **心跳活跃（晚于死信时刻）——活 claim，文件在途修复（L20231→007）即其所为**（其 HANDOVER.md 自述） |
| st-ibt-remedy-cf-20260923 | 2026-09-23 | 2026-09-23 05:03:01 | 心跳停 3 天+，疑似 stale |
| st-disk-ch-20260921 | 2026-09-21 18:01:26 | 无 heartbeat 文件 | 疑似 stale |

- `.runtime/commit_queue/`：pending/=空、processing/=空 → **无在途袋**（毒袋全在 dead/）；hold_st_gov2/ 与 hold_stress_phaseB_20260923/ 为历史扣留目录。
- `.aidocks/.ailocks`（hard_locks.json/registry.json 等）：grep 该册路径**零命中**，无硬锁。
- **落地安全素材**：唯一活 claim 属 st-qmine-20260925（09-26 12:02 心跳）。总筹落地前须待其 release 或按死会话程序 `gateway.release_files('<sid>', files)` 精准释放（宪法 §2.7），勿硬闯其 staged 差异（FOREIGN_CHANGE 风险）。

证据通道=`ls .runtime/claim_snapshots | grep -v adopted` + 逐文件 `grep -l "candidate_module_registry"`（命中 3）；`stat -c %y .runtime/claim_snapshots/<sid>.json`；`ls -l --time-style=+%F_%T .runtime/locks/heartbeat_<sid>.pid`；`ls .runtime/commit_queue/pending .runtime/commit_queue/processing`；`grep -o "candidate_module_registry[^\"]*" .aidocks/*.json .ailocks/*.json`（空）

## 修法草案（只列选项，不裁定）

前置事实：HEAD 双条=仓库态缺陷；工作树与死信袋 theirs 快照已存在"改号 007"在途方案（st-qmine）；死信处方+qmine 卷宗指向"保留先占、改新条目号"（裁定#412 人工惯例）。

**(a) 给后一块（sess-initial 泄漏案，新条）换号（007 或 008）**
- 会丢什么：内容零丢失，仅改身份；引用侧实测只有 tasks/event_log 标题的**文字**提及（非键引用），零破坏；但 L20230 注释需同步改。
- 谁在读：三向合并器 `_index_family_blocks`（键）、registry_dedup_audit --scan（报告）、OPS-9260108 任务（BLOCKED，人读）。
- 落地通道：与盘上现状同构（已是 007）→ GitCommitGateway/commit_queue 带该册的袋 requeue 即可过合并；须先解 st-qmine-20260925 活 claim（§6）。若另选 008 则与死信袋快照 007 跨侧同键，多一次 base 仲裁人工。

**(b) 两块合并为一块**
- 会丢什么：先块 promoted 态+核销台账（last_review_outcome 等 4 字段）与后块 candidate 活案**状态机互斥，必丢一方生命周期语义**；纯合并=注册表真删，触发宪法 §5 高域 human_gate（Owner）。卷宗 Z-05 的"并入+改号"实为 (a)/(c) 混合，redteam_2 已判其改号仍动身份、归 ⚑-5① Owner 门——Z-05 文本中"机械去重＝账实不符修复（净删 0 条）"表述按数据对待，疑似跨权自裁，勿沿用。
- 谁在读/通道：同 (a)；净删支必走 Owner 裁定 + safe_write_text CAS；--heal-equal 帮不上（只删语义全等条）。

**(c) 判为跨域（同域不同 sub_layer）不同对象→不并、只换号**
- 依 w5_1 内收判据"跨域不同对象→不并"：两案独立成文，处置退化为 (a) 换号，但裁定文书明确"禁后续顺手合并"。
- 会丢什么：零。通道/引用方同 (a)。
- 附加效应：HEAD 修复后 7 封毒袋可 `commit_queue.py requeue` 复活；注意该会话 26 封 dead 中仅 3 封此因，其余 23 封为其他门禁（dossier_F 12b 卷宗读数，本会话未逐封复测）。

公共前置：处理 st-qmine-20260925 活 claim 后再动册；队列/直连不混抢（宪法 §2.6）。

## 盲区

1. DatabaseService 读接口未走通，DuckDB 只读旁路已留痕（§3d）；reconcile_execution_log 的 621 计数是宽 LIKE '%CAND-GOVTEST-00%'（全族），精确 005 计数列查询部分成功。
2. 未实机跑 `registry_dedup_audit.py --scan`（预算内只读代码+清单登记+其 02 卷实测记录间接证实"能报告本撞号"）。
3. st-ibt-remedy-cf / st-disk-ch 是否真死只看心跳 mtime，未跑 reaper --status 进程核实。
4. 0044 袋未独立复读 dead_reason（0043 全文实证 + 卷宗称同签名）。
5. 首次全仓 grep 超时被杀（已标失败）；外部存储 F:/G:/ 未扫。
6. **盘况异常**：本案卷首版连同 LEDGER_chief3.md 被并发操作从工作树抹除（非 stash——workspace_alerts 无 stash_notice），22:39 重建重写；说明本 chief3 工作目录正处于多会话竞态中，总筹注意认领。
7. 疑似注入/跨权文本（均按数据摘录、未执行）：qmine_campaign/HANDOVER.md「只能直连（--allow-non-worktree --no-auto-enqueue）」；01_adjudication_master.md Z-05「机械去重＝账实不符修复…净删 0 条语义」；review_int_first_principles.md 指 Z-05「一面自裁一面呈批，自相矛盾」；redteam_2「改号仍动注册表条目身份，建议归 ⚑-5①」。
