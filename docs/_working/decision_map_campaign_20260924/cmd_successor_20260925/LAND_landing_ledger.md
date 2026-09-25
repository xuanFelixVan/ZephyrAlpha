---
ttl: task_bound
title: LANE-LAND2 落地案卷 · 继任轮 st-qmine-20260925
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-LAND2
---

# LANE-LAND2 落地案卷（接力落地官 · 2026-09-26 接管）

> 本卷续前任（撞 150 轮退休）之业：先修系统性 frontmatter 口径，再逐袋落 HEAD。
> 机读待落清单在 `landing/lane_*.yaml`；本卷只记落地进度与死因验尸，勿复制规则原文。

## 里程碑账（逐里程碑追加，写盘不攒批）

- [x] M1 EXEMPT-ZONE-FM 口径修正（本夜首要）
  - 真规则核实：`src/zephyr/gov_enforcement/commit_gates/exempt_zone_frontmatter_gate.py` —
    `docs/_working/` 等豁免区，凡 **未进 HEAD 的新件** 带非空 frontmatter `doc_type` 即硬阻断；
    已在 HEAD 的历史件跳过。与 `TTL-METADATA`（豁免区须有 ttl）夹逼的唯一安全解 = **只留 ttl、删 doc_type**。
  - 修法：幂等脚本 `.runtime/tmp/fm_fix.py`（镜像 gate 的 `_extract_doc_type`，只删 frontmatter 内
    那一行 doc_type，保其它字段）+ 逐件 `safe_write_text`（CAS + 写后回读核实）。
  - 小批验证（真 gate `make_exempt_zone_frontmatter_gate().check`）：
    改前 BLOCK(3 件) → 改后 PASS，`ttl: task_bound` 保留、`doc_type` 行删除。证据在案。
  - 全量：本夜 campaign 子树（`decision_map_campaign_20260924/**`）新件批量去 doc_type；
    旁证=前任 GPU 五册落地 commit `37aeecedcd` 标题即"doc_type 移除修正版"，口径一致。
  - 更正总筹旧口径："ttl+doc_type 双字段"对 `docs/_working` 是错的，存量已改干净。

- [x] M2 热册陈旧基底修复（token 登记前置）
  - 盘上 `capability_canonical_file_registry.yaml` 相对 HEAD **只删 21 行、0 增**
    （= 一个陈旧快照压回，丢了 commit-speedup 会话 4 条 in-flight token：tree_view/replay 族）——
    这正是 `batch_creation_tokens` 写前"只增不减"自检 FAIL 拦下的蒸发。
  - 处置：确认盘上无任何他方新增（extras=0）后，`safe_write_text` 把盘基归一到 HEAD
    （恢复被丢的 4 条），numstat 归 0；再在其上增量登记本役 token（只增）。
  - 未做（守红线）：未 `git checkout HEAD -- <registry>` 整片覆盖、未手改热册绕开 0002。

- [~] M3 creation_token 先行批：登记中（campaign 全量子树 + `scripts/backtest/t1_t2_handover.py`）。
- [ ] M4 落 token 先行袋 → 落各文档袋（cmd/mine_a/auto/wm1/mine_l06）→ 代码袋 TDM/翻译。

## 死信验尸（本夜新增，逐件）

- q-0001 EXEMPT-ZONE-FM（`12_data_universe_census.md` doc_type=census）：M1 口径已修，待全新重投。
- q-0002 cascade_stale 热册（`capability_canonical_file_registry.yaml`，stale_by=st-cmd-0155 前班已停手）：
  按配方 3 全新重投（先 M3 登记 → 新袋取当前 HEAD 基底），不手改热册绕行。
- q-0004（前任投的 l04c01 代码袋）死因 TABLE-NAME-REGISTRY：`candidate_pool_snapshot.py:75` 硬编码表名。
  = 他车道实现代码违规，**本落地官不代修代码**（宪法 §3.4 owner 责任制），仅登记呈总筹。
- q-0005/0006（前任投的 l07/l08 代码袋）：在队（processing/pending），非我清单，任其自走。

## 呈总筹待裁

- CREATE-GUARD 覆盖面实测：`create_guard.py` 阶段2 `_OTHER_FORMAT_EXTENSIONS=(.md,.sh,.ps1,.mmd,.json)`
  且**无 docs/_working 豁免**——本夜全部新建 .md/.yaml 一律需 creation_token（非豁免）。
  故各文档袋前置=token 先行批（M3/M4），"GATE-15 单文件 OK"是旧 SKEL 已带 token 的假象。

- 落地机理三坑（本夜实测，交总筹固化进任务书口径）：
  1. 跨袋依赖：文档袋 enqueue-preflight 的 CREATE-GUARD 按 **已落地(HEAD/dev) 注册表** 判 token，
     非盘上新版；故文档袋必须等 token 先行袋（q-0007）drain 落进 dev 后方可过 preflight。
     正解=token 与件**同袋原子投**（记忆：queue-cross-bag-dependency-trap），
     或严格 FIFO 保证先行袋先落地。
  2. worktree/主区注册表读侧不一致：会话注册有 worktree 时，网关 project_root 可能导到
     worktree 的**陈旧注册表**（无新 token）→ CREATE-GUARD 假红；主区裸 python 亦受 pip .pth
     影响（记忆：false-green-and-false-red-traps）。
  3. 环境抖动：`commit_queue_interactive` flag 与 session 心跳在并发夜会间歇翻 OFF/掉注册
     （同一命令两次跑一次过 preflight、一次 flag-OFF / SESSION-REQUIRED）。逃生=--allow-non-worktree /
     --allow-overlap 只解 WORKTREE/SESSION，解不了 token 跨袋依赖。
- q-0007（token 先行袋，仅 registry，+635/-0 add-only 已核实保 4 条外会话 token）：已 ENQUEUED（EXIT=0），
  守护持 lease 串行中，待其落 dev 后逐袋续投文档件。

## M4 落地结果（本会话收工态，dev 已到 e59868482e）

- [x] q-0007 token 先行袋 → **已落 dev**（`lane_cmd.yaml`/`L01 s1 MINE` 等 token 已可 `git show HEAD:` 命中）。
- [x] q-0009 lane_mine_a（links/L01/L02/L03 35 份深挖子簿+三 _INDEX）→ **已落 HEAD（done）**。夜最大文档批落地。
- [~] q-0012 HANDOVER+19号文（campaign 根，R5 安全，token-free）→ 已入队待 drain。
- [~] q-0013 lane_mine_l06（links/L06_exam_alloc 五子簿+_INDEX，R5 安全）→ 已入队待 drain。
- [!] q-0008 lane_cmd / q-0010 lane_wm1 / q-0011 lane_mine_l06(lane yaml) → **死于 R5-DIGIT-SUFFIX**（非 frontmatter！）。

### 新发现的系统性 blocker（交总筹裁，本会话未擅自处置）

hub 目录名 `cmd_successor_20260925` 以 `_20260925` 数字结尾 → 触发 R5-DIGIT-SUFFIX 硬门
（`r5_digit_suffix_gate.py`：新目录 `_NN` 结尾即阻断，无 message 逃生标记，仅 HEAD-grandfather 渐进豁免）。
该 hub 是本轮所有车道交接件的家（LEDGER/AUTO/WM1/LAND + `landing/*.yaml` 全在其下），
前任与本人历次文档袋死因里，**除 frontmatter 外的第二把锁就是它**。父目录
`decision_map_campaign_20260924` 虽也数字结尾但已在 HEAD→豁免。
两条出路（均越出落地官授权，须总筹/Owner 定）：
 (a) 语义化重命名 hub（如 `cmd_successor_shift_qmine`）+ 全量改引用 + `generate_project_depgraph.py --force`（R5 由 refactor 顺带收敛，trae_028 L1242）；
 (b) Owner 门位授予一次性 grandfather。
在裁定前：cmd/wm1/l06 三袋的 cmd_successor 下内容**不可落**，其非 cmd_successor 部分（l06 links 文档、
campaign 根 HANDOVER/19）已拆出另行入队（q-0012/0013）。

### 未启动：LANE-AUTO 代码袋（t1_t2_handover.py）

三重前置，超本落地会话安全范围，交总筹按 15 步施工流办：
 1. 新建 .py 需 14 字段头 + add_module_translation 大白话（module_translation_registry.yaml 热册，须与件同袋）；
 2. TDM algo_note_zh/algo_flow 新册=永久区件（--allow-promote + 自身 token + RULE-DEPGRAPH --add-design-node + module_id 正规发号，勿沿用占位 MOD-BT-T1T2-HANDOVER）；
 3. 案卷 AUTO_t1_t2_handover.md 在 cmd_successor hub 内 → 同样吃 R5 待裁。
