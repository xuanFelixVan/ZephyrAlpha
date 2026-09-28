---
ttl: task_bound
---

# W-CASE · commit_queue `_compact_pending` 同会话 supersede 压缩静默丢弃注册表增量（lost update）

> 病案登记：campaign st-zcloseout-20260928，Agent-J2（registry integrity auditor），2026-09-28。
> 审计方法：逐袋读 `.runtime/commit_queue/{done,dead}/*.json`（files/meta.supersedes/meta.compacted_at/dead_reason）+ blob 逐个 grep → 逐落地 commit `git show <hash> --diff-filter=A` 取新增文件集 → 对 dev HEAD（0a1940e43c）两热册做 YAML 身份集比对 → `git log -S` 判 EVICTED / NEVER-LANDED。

## 1. 缺陷陈述

`scripts/commit_queue.py` 的 `_compact_pending` 在同一 session_id 的兄弟 lane 先后入队两个都携带同一注册表路径的 pending 袋时，用后袋整份 blob 静默顶替前袋（supersede compaction，meta 标 `compacted_partial=true`），前袋对该注册表的增量行（creation_token / module_translation 条目）乃至内容文件被丢弃，且无任何告警。后果：任何已入队注册表行都可能被同会话后入队袋驱逐；内容袋落地时 CREATE-GUARD 报"无 token"，但 token 明明入队过——丢失发生在队列内部，不在提交侧。

## 2. 证据链（三条独立，全部机读可复现）

| # | qid 对 | 时间戳（created_at / compacted_at / dead_at） | blob grep 与死因实证 |
|---|--------|--------------------------------------|----------------|
| 1 | dead 0037 ← compacted by 0038 | 0037（P0-13 叶簿首批 6 本）created 2026-09-28T10:21:51+08:00，meta.compacted_partial=true @10:53:12 == 0038（B3b 消费普查）created 10:53:12；0037 dead 11:10:05，0038 dead 11:53:11 | 0037 死因=CREATE-GUARD：6 本叶簿 .md 无 token（其册袋增量已被顶掉）；0038 files 仅剩 5 件消费 .py——其 CREATE-GUARD 死因清单只列 3 件 .py、不含 6 本 .md，反证 6 本内容文件已被静默丢弃 |
| 2 | pending 0041 → superseded by 0042 →（随 0043 再顶替） | 0043（B3b 重投）created 12:07:44，meta.supersedes=["…-0042","…-0041"]，dead 12:29:23（ORPHAN-MODULE） | 0043 所携 CCR blob e87c19ba…2040 grep `closeout_leaf_books`=**0**；含原 6 条叶簿 token 的 blob `blobs/3ee7253aa234a6ff888d7606a0a91ae2831bc9c3e1bc83e6657fb61ffc9e5c66`（grep=6）至今未落地；0041/0042 袋 JSON 已被压缩物理删除，仅存于 supersedes 指针 |
| 3 | 0045 → superseded by 0046 | 0046（Z-4 接线袋）created 12:33:29，meta.supersedes=["…-0045"]，dead 13:07:35（TEST-SOURCE-CONSISTENCY） | 0046 携带两热册 blob e87c19ba…2040 / 750e0150…a4704 grep `closeout_leaf_books`=**0**；其后 0048（13:12:51，dead 13:41:09 CLAIM_REQUIRED）两册 blob grep 仍=**0**；dev HEAD（0a1940e43c）两册 grep=**0**，`git log -S closeout_leaf_books -- <册>`=空（从未落地） |

补链（修复袋亦中招）：0050（Agent-J 首轮修复册袋）created 13:41:59，其 CCR blob grep `closeout_leaf_books`=**6**（修复内容其实已入袋），dead 14:03:39——死因=R5-DIGIT-SUFFIX（`docs/_working/qoder_legacy_closeout_20260928/` 目录数字后缀），非内容错误。修复被目录命名门禁二次拦截，与本缺陷叠加成双死因链。

## 3. 爆炸半径

触发条件=同一 session_id 多 lane 并行 + 各 lane 袋携带同一注册表路径。本战役（st-zcloseout-20260928 单会话挂 A/B/C/D/F/G/H 七 lane）全中：
- H 叶簿 6 token：被 0041→0042、0045→0046 两轮压缩驱逐，叶簿内容袋 0037 两死 CREATE-GUARD。
- B（three-piece）consumption 4 token + 5 翻译：曾被同机制驱逐，靠总包"册先行"80eaa9771a（06:50）重投恢复（dev HEAD 已核实在册）。
- 凡"多 lane 共享会话 id + 注册表随袋"的战役均为易感人群；不修则每战役必复发。
- 附带（非本缺陷独走，审计同窗判定 NEVER-LANDED）：G（F62）order_manager G07/G09 接线袋 0029 死于 R5-DIGIT-SUFFIX（W140 表路径），接线至今不在 dev；C3 连接矩阵袋 0007 死于 BLUEPRINT-FORMAT，其 MTR 增量（test_connection_matrix_rulers 翻译）未落地；F 的 chart_condition_consumer.py 之 CCR token 从未落地（0046/0048 死袋所携，等 Z-4 接线袋重投自带），其 MTR 翻译已由 9219a50e0c 落地。

## 4. 处方（给日班）

1. **治本**：`_compact_pending` 对共享路径必须二选一——(a) 对共享注册表路径做三向合并（以前袋 base_blob 为 merge base，逐条并集）；(b) 当两袋对同一路径的 (base_blob, blob) 快照分歧时**拒绝压缩**（放弃 supersede，两袋都保留，按序落地理顺）。
2. **过渡工装**：(a) 每 lane 独立 session_id（supersede 只在同会话内触发）；或 (b) 战役级注册表互斥——同一时间全局只允许一个携带注册表的袋在 pending/processing（本病例修复即按此互斥执行）。
3. **回归测试草图**（tests/governance/test_commit_queue_compaction_registry_merge.py）：
   - 造临时 queue_root；会话 S 入队袋 A：携带注册表 R（base=B0，blob=B0+token 集 T1）；
   - 同会话再入队袋 B：携带 R（base=B0，blob=B0+token 集 T2，T1∩T2=∅）；
   - 断言一：`_compact_pending` 后幸存袋的 R blob 含 T1∪T2（合并语义），或两袋均存（拒绝语义）；断言不得出现"幸存袋仅含 T2"。
   - 断言二（端到端）：drain 后 HEAD 的 R 文本包含 T1∪T2 全部 token 行，且两注册册身份集纯增（无净删）。
   - 断言三（压缩不可丢内容）：supersede 幸存袋 files 必须是各被顶替袋 files 的并集（本案 0038 丢 6 本 .md 即违此条）。
   - 变体：A 已 processing 时 B 入队（现行为合法路径）作对照组。

## 5. 邻接发现（审计附带）

- 消费普查真路径 token 缺口已在 13:59 由 0a1940e43c（done 袋 0049，B3a5 册先行 v3）治愈：dev HEAD 已核实 `src/zephyr/governance/consumption/` 包内 census/reconciler/scan_scope/__init__ 四件 token 在册。B3b 内容袋（0038/0043/0047）之死发生在该治愈落地前的窗口期。
- 残留债（日班另裁，非本病例修复范围）：CCR 仍存波13 期两条**过期平铺路径** token（`src/zephyr/governance/consumption_census.py`、`src/zephyr/governance/scan_scope_converged.py`，真源已迁 consumption/ 包内），与真路径 token 并存构成双登记；清理属注册表净删，须走裁定+净零判据。
- 教训并入 §4-(1)：注册表行与文件真路径的一致性校验（token.file 必须命中磁盘/HEAD 真实路径）应入 `_compact_pending` 拒绝压缩判据与回归测试断言。

## 6. 本次修复记录（Agent-J2）

- 审计结论：dev HEAD（0a1940e43c）已落地件的册行全部在册（A1×2 脚本 token、B1 三 CASE token、B6a +21、B3a +20/+16、coordination token+翻译、D3 token×2+翻译×1、F 翻译×9 逐一核对）；**EVICTED=0**；唯一缺口=6 条 closeout_leaf_books token（EVICTED-IN-FLIGHT）+ 本病案 token。
- 修复：在本 lane 以 dev 两册为基，官方工具 batch_creation_tokens.py 重登（参数同原 blob 3ee7253a 与原 staged delta 逐字：created_by=st-zcloseout-20260928，capability=closeout_leaf_books / qoder_legacy_closeout，merge_evaluation 原文保留）+ 本病案 token；YAML 身份集断言纯增（CCR creation_tokens +7/−0，MTR entries ±0）；单册袋（registry-only）入队，落地后再投叶簿+病案内容袋。
- 命名注记（门禁强制最小修复）：目录 `qoder_legacy_closeout_20260928/` 触发 R5-DIGIT-SUFFIX（0050 死因实证）→ 改 `qoder_legacy_closeout/`；文件名 `W_CASE_…` 触发 trae_028 N-01（新建文件名禁大写）→ 改 `w_case_compaction_lost_update.md`。语义不变，token 名不变。
