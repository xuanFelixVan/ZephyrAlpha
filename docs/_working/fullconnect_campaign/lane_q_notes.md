---
ttl: task_bound
completes_when: "zc-lane-q-20260927 两任务代码已备（工作区就绪）+ FOLDER-CAPACITY 阻断解除后落地，并被协调会话核销后即作废"
lane: zc-lane-q-20260927
status: blocked-gate
created: 2026-09-27
---

# lane_q_notes — Q 线施工登记（M1 C-1/C-2 + M2 候选 D-①）

## 0. 【当前阻断】FOLDER-CAPACITY-HARD-LIMIT 硬拦提交（需 Owner/治理动作）

代码已完成并全量自测（见 §1），但 git_commit.py 锁外预检 3 拦：
- WORKTREE-REQUIRED → `--allow-non-worktree`（2026-08-13 裁定 AI 可默认）✅ 可解
- COMMIT-SCOPE 2 域 → `--allow-multi-domain`（宪法 §2.4 gate+自家测试同批）✅ 可解
- **FOLDER-CAPACITY-HARD-LIMIT：scripts/ 平铺 122 > 120 硬上限** ❌ 无旗标逃生——
  该门 own-scope 合法命中（本袋确改 scripts/commit_queue.py），处方=「拆子目录/迁移」，
  但 scripts/ 超限系他会话在途件累积（未跟踪散件+staged-new 多件，见 §3.7），动它们=
  宪法 §3.4「他会话在途违规不代修」禁区+需 RULE-DEPGRAPH 重建，属 Owner 门位。
  **Q 线按纪律 §4 登记后停**。解除路径：任一有权限车道把 scripts/ 平铺数降到 ≤120
  （挪 2 件即可）后，用 `--adopt-prior-work --allow-non-worktree --allow-multi-domain`
  重试（3 个 claim 已保留；TTL 300s 过期则重新 claim）。
  ⚠️ 时效风险：工作区未提交态曾两度被旧快照袋回退（§2）——本袋改动建议协调会话
  优先处置，或先 `git_commit.py --enqueue` 之外的人工兜底（见 §3.8）。

## 1. 交付摘要

- **Q1-a（C-2，requeue 挂预检）**：`requeue_dead_item` 冲突标记预扫之后、基底补全之前挂
  `_run_registration_gate(wt, …, audit_event="requeue")`——登记三族（CREATE-GUARD/
  TTL-METADATA/TRANSLATION-COVERAGE）轻量内联判定，非 36s 全门重放；拒绝→RequeueError
  带逐门禁处方；拦截写 `.runtime/audit/preflight_events.jsonl`（event=blocked/path=requeue）
  ——**E-2 的 B 级证据由此可升 A**（投袋看 audit，test_requeue_channel_blocked 阳性例已证）。
- **Q1-b（C-1，enqueue_item API 层强制）**：`enqueue_item` 在 R2 大批硬顶之后、blob 落袋
  之前挂同款 `_run_registration_gate`——结构性补口第四裸入口（E-3：直接 import
  enqueue_item 的脚本化入队，mapbuild 四件 meta 裸无 options 实证）。判据落地面=
  `opts.worktree_root`（缺省回退 cwd，覆盖裸调用方）；root 无 .git（tmp 隔离测试）或袋内
  无三族扩展名 ⇒ 零 git 面整体跳过。拒绝→QueueReject（exit 2 同口径）；**放行证据随袋**
  （meta.registration_gate 摘要 + meta.preflight_face 面貌快照），放行面不写文件审计
  （防锁外高频 jsonl 写放大；拦截面必写——拦截无袋可查）。
- **Q1-c（E-4 TOCTOU 消减）**：判据采集两登记册 HEAD blob sha 随袋（meta.preflight_face）；
  `drain_queue` 死信出口 `_annotate_preflight_face_drift` 比对当前 HEAD 面貌，漂移 ⇒ 死信
  增 `preflight_face_drift` 明细+处方补「直接重投」指引+warning 留痕。观测级增信，不改
  死信裁决。
- **Q2（W17/候选 D-①）**：**核实 HEAD 已含修复**——3709af04ea（09-26 13:37）「回补快照
  自洽见证层 + W17 恒取 base_blobs」已把 `--base-head` 分支改为恒走 `resolve_base_blobs`
  并带判别尺 `test_cli_enqueue_with_explicit_base_head_still_fills_blob`。任务书引用的
  `:2782-2796` 行号对应的是**工作区回退态**（见 §2）。本次未另写第二份判别尺（净零），
  以既有尺全绿为准（22/22 passed）。
- 复用纪律：判据 100% 复用 `commit_preflight` 既有内联检查函数与 TTL spec
  （`run_registration_inline_checks` 为唯一新增公共入口，零第二真源）；面貌比对复用
  `resolve_base_blobs/resolve_base_head`。

## 2. 【重要发现】旧快照袋回退第三轮（3709af04ea 修复被工作区回退）

施工前工作区考古（classify_workspace_wip.py 判读 + CASE.md 归因）发现 `commit_queue.py`
工作区态 = HEAD ⊖ 3709af04ea 回补内容（快照自洽见证标记/处方、ATK-2 from-bag 基底继承、
**W17 修复本体**）⊕ st-p23-rebase 已交付未落地增量（mergeable_pred，其 CASE.md 自证
「_revalidate_stale_base = 旧版」）；`commit_queue_landing.py` 同形态（-121 行≈见证层被
剥）、`test_commit_queue_base_head.py` 被剥 W17 判别尺（-47 行）。判定：**stale_rollback
污染 + 他车道交付件混态**，非在飞修改（mtime 02:13 < HEAD 05:20、无 claim、st-p23 不在
active_sessions）。
处置：施工前置 stash（stash@{1}，全文保留可溯）→ 基于 HEAD（修复齐全态）施工 → 提交
只含 Q 线三文件 → 提交后重建 st-p23 真增量（仅 mergeable_pred 两 hunk，回退污染 hunk
不回植——它们与 HEAD 修复矛盾且被分类器判 stale_rollback）。混态原文备份：
`.runtime/tmp/lane_q_20260927/commit_queue.frankenstein.py`。
**因 §0 阻断，提交未落地 ⇒ 重建亦未执行**（避免未提交混态叠未提交混态）：当前
commit_queue.py 工作区=纯 Q 线改动；st-p23 真增量完整保存在 stash@{1} 与上述备份，
解除 §0 后按「先提 Q 线三文件、再回植 mergeable_pred 两 hunk（import Callable +
_revalidate_stale_base 签名/正文/docstring）」次序操作。

## 3. 登记项（只登记不自裁）

1. **未能做：落地侧 pool 腿死信出口的 E-4 增信**——`commit_queue_landing.py` 工作区驮着
   他车道未落地混态（§2），避碰；直连腿（drain_queue）已覆盖。pool 腿补点=后车道义务。
2. **未能做：按漂移改判死因/阻断落地**——会使预检升格为权威，动「预检非新权威」在册
   原则语义，属 Owner 门位（mine_door_registration_completion §8 O-2 同源）。
3. **已知限界：--from-bag 重投的判定面**——三族判据读工作区盘面；from-bag 原袋重建时
   盘上缺文件即被检查器按缺失跳过（fail-open，不阻断原袋取回）；盘面≠袋字节残余窗由
   落地权威链兜底。已在 requeue 挂点注释明示。
4. **成本口径**：裸调用方首件 ~3s（GitCommitGateway 构造+roster 分析）、后续 ~2.4s 级/
   袋（ls-tree 面）——与 C-1 在册预算「2.4s 级内联判定」一致；未加进程级 gateway 缓存
   （净零：非必需不新增机制）。
5. **工作区既有失败（与本袋无关，全数基线复证）**：test_preflight_homolog×2、
   pool×2、integration FIFO 时序 flake（纯 HEAD 复现同签名 timeout+fail）、pkg14×10
   （全部打在 landing.py 工作区混态上）——建议协调会话优先修复 landing.py 混态（§2），
   这些尺才能恢复判读力。
6. **stash 遗留**：stash@{1}=commit_queue.py 混态全文（§2 处置锚，协调会话核销后可
   drop）；stash@{0}="lane-q-bisect" 显示为 375 文件大快照（bisect 期间产物，本车道
   未再动它，内容与用途请 Owner/协调核销时定性，**未敢自行 drop**）。
7. **lane_q_notes.md 本体未获 token**：capability_canonical_file_registry.yaml 被
   st-final-build-20260926（册先行袋）+st-pqmine-20260927 双持锁，本车道不得碰；
   本文件暂以未跟踪态存盘，待注册表解锁后由后续车道补 creation_token 随袋入册。
8. **重试注意**：解除 FOLDER-CAPACITY 后重试提交时，若 claim 已过期需重新
   `lock_files.py acquire` 三文件；提交面=本节 §1 所列三文件，勿混入 §2 混态文件。
