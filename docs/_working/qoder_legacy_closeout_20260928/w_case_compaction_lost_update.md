---
ttl: task_bound
---

# W-CASE · commit_queue `_compact_pending` 同会话 supersede 压缩静默丢弃注册表增量（lost update）

> 病案登记：campaign st-zcloseout-20260928，Agent-J（registry integrity auditor），2026-09-28。
> 审计方法：逐袋 `git show <hash> --diff-filter=A` 取新增文件集 → 对 dev HEAD 两热册 grep token/translation → `git log -S` 判 EVICTED / NEVER-LANDED。

## 1. 缺陷陈述

`scripts/commit_queue.py` 的 `_compact_pending` 在同一 session_id 的兄弟 lane 先后入队两个都携带同一注册表路径的 pending 袋时，用后袋整份 blob 静默顶替前袋（supersede compaction），前袋对该注册表的增量行（creation_token / module_translation 条目）被丢弃，且无任何告警。后果：任何已入队注册表行都可能被同会话后入队袋驱逐；内容袋落地时 CREATE-GUARD 报"无 token"，但 token 明明入队过——丢失发生在队列内部，不在提交侧。

## 2. 证据链（三条独立）

| # | qid 对 | 时间戳（created_at / compacted_at） | blob grep 实证 |
|---|--------|--------------------------------------|----------------|
| 1 | dead 0037 ← compacted by 0038 | 0037 created 2026-09-28T10:21:51+08:00；meta.compacted_partial=true @10:53:12 == 0038 created 10:53:12；0038 meta.compacted_partial=true @10:58:25 | 0037 死因=CREATE-GUARD：6 本叶簿 .md 无 token（token 本应随其注册表袋落地，已被 0038 顶掉）；0038 死因=CREATE-GUARD：consumption 三 .py 无 token（同机制二次复发） |
| 2 | pending 0041 → superseded by 0042 | 0042 入队时整袋顶替 0041（同会话同注册表路径） | 0042 所携 capability_canonical blob grep `closeout_leaf_books` = **0**（Agent-I 首证）；含原 6 条叶簿 token 的 blob `blobs/3ee7253a…e5c66` 至今未落地 |
| 3 | 0045 → superseded by 0046 | 0046.meta.supersedes=["q-20260928-st-zcloseout-20260928-0045"]；0046 created 2026-09-28T12:33:29+08:00 | 0046 携带两热册 blob e87c19ba…2040 / 750e0150…a4704 grep `closeout_leaf_books` = **0**；dev HEAD 两册 grep = **0**；`git log -S closeout_leaf_books -- <册>` = 空（从未落地） |

补充实证：`git log dev -S consumption_census -S batch_window_preflight -- capability册` 命中 80eaa9771a（B3a 册先行袋）——B 组 token 曾被同机制驱逐过一次，靠总包"册先行"重投才恢复；属于同一缺陷的历史伤口。

## 3. 爆炸半径

触发条件=同一 session_id 多 lane 并行 + 各 lane 袋携带同一注册表路径。本战役（st-zcloseout-20260928 单会话挂 A/B/C/D/F/G/H 七 lane）全中：
- H 叶簿 6 token：被 0041→0042、0045→0046 两轮压缩驱逐，叶簿内容袋 0037 两死 CREATE-GUARD。
- G（F62）W140 token：随 0029 死亡未落地（W140.md+配套 test 至今不在 dev，属 NEVER-LANDED，非本缺陷独走）。
- B（three-piece）consumption 4 token + 5 翻译：被驱逐后由 80eaa9771a 重投恢复（HEAD 已核实在册）。
- C2/C3：token 现均在 HEAD（C3 两 .py 在册但内容件未落地=册先行态）。
凡"多 lane 共享会话 id + 注册表随袋"的战役均为易感人群；不修则每战役必复发。

## 4. 处方（给日班）

1. **治本**：`_compact_pending` 对共享路径必须二选一——(a) 对共享注册表路径做三向合并（以前袋 base_blob 为 merge base，逐条并集）；(b) 当两袋对同一路径的 (base_blob, blob) 快照分歧时**拒绝压缩**（放弃 supersede，两袋都保留，按序落地理顺）。
2. **过渡工装**：(a) 每 lane 独立 session_id（supersede 只在同会话内触发）；或 (b) 战役级注册表互斥——同一时间全局只允许一个携带注册表的袋在 pending/processing（本病例修复即按此互斥执行）。
3. **回归测试草图**（tests/governance/test_commit_queue_compaction_registry_merge.py）：
   - 造临时 queue_root；会话 S 入队袋 A：携带注册表 R（base=B0，blob=B0+token 集 T1）；
   - 同会话再入队袋 B：携带 R（base=B0，blob=B0+token 集 T2，T1∩T2=∅）；
   - 断言一：`_compact_pending` 后幸存袋的 R blob 含 T1∪T2（合并语义），或两袋均存（拒绝语义）；断言不得出现"幸存袋仅含 T2"。
   - 断言二（端到端）：drain 后 HEAD 的 R 文本包含 T1∪T2 全部 token 行，且两注册册身份集纯增（无净删）。
   - 变体：A 已 processing 时 B 入队（现行为合法路径）作对照组。

## 5. 邻接发现（审计附带，日班另一处方）

- `capability_canonical_file_registry.yaml` HEAD 存在波13 期登记的**过期平铺路径** token：`src/zephyr/governance/consumption_census.py`、`src/zephyr/governance/consumption_census_reconciler.py`（真源已迁 `src/zephyr/governance/consumption/` 包内）。真路径中仅 `consumption/__init__.py` 有 token（blob 3ee7253a 内 st-zcloseout-20260928 重登痕迹="前登被主区回退丢失"），`consumption_census.py`/`consumption_census_reconciler.py`/`scan_scope_converged.py` 三件真路径 token 缺失。
- 后果：B3b 消费普查内容袋（0038、0047）接连死于 CREATE-GUARD"无 token"——根因不是压缩，而是登记路径漂移；translation 册包路径四件已齐全（tr 册无需动）。
- 处方：由持有源件文件的 lane 对 `--prefix src/zephyr/governance/consumption` 跑 `batch_creation_tokens.py` 官方工具补登三件（工具按磁盘文件发现，无法跨 lane 代跑）；过期平铺路径两条 token 的清理按净零铁律另行走裁。
- 教训并入 §4-(1)：注册表行与文件真路径的一致性校验（token.file 必须命中磁盘/HEAD 真实路径）应入 `_compact_pending` 拒绝压缩判据与回归测试断言。

## 6. 本次修复记录（Agent-J）

- 审计结论：dev HEAD 已落地件的册行全部在册（13+9+3 件逐一核过）；唯一缺口=6 条 closeout_leaf_books token（EVICTED-IN-FLIGHT）+ 本病案 token。
- 修复：在本 lane 以 dev HEAD 两册为基，官方工具重登 6 token（batch_creation_tokens.py，参数同原 blob 3ee7253a：created_by=st-zcloseout-20260928，capability=closeout_leaf_books，merge_evaluation 逐字保留）+ 本病案 token；身份集纯增断言后单册袋入队。
- 文件名注记：任务简报原名 W_CASE_compaction_lost_update.md 被 NAMING gate（N-01/N-13 连续大写）拒绝，改 snake_case w_case_compaction_lost_update.md，语义不变。
