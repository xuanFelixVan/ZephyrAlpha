---
ttl: task_bound
completes_when: 12 条车道的脏件全部完成 sha256/size/mtime/in_head/head_sha 字节归账，且表1/表2/表3 与 byte_matrix.yaml 同步落地
---

# 波13 车道待落面 · 字节归账案卷（纯测量，无裁定）

测量者：本 worktree（只读测量，零 git 写）。测量时刻：2026-09-26 22:2x（本地）。
主区 dev HEAD = `461b25d0e8fc28a9a874c8c057b0d28d68e728d7`（branch `dev`）。

## 0. 任务边界

- **只做**：脏件枚举 → sha256 / size / mtime / HEAD 存在性 / HEAD sha / 与 HEAD 差异行数 / 同路径跨道可比事实摊开。
- **不做**：不指定权威版本、不判对错、不落地、不改阈值/断言/skip、不动热册（`capability_canonical_file_registry.yaml`、`module_translation_registry.yaml`、`ruling_registry.yaml`、`registry_of_registries.yaml`、任何 `in_process_gate_registry.yaml` 全程只读）。
- **口径**：`git status --porcelain -uall`（`-uall` = 目录型条目展开到其下每个文件；等价于任务书"以 `/` 结尾要展开"，但由 git 展开，无手漏）。排除任何以 `.runtime/` 开头的路径。

## 1. 测量通道（每条结论可由下列命令复跑）

1.2 车道枚举与 HEAD 指纹（12/12 目录均在，`status` 全部成功，`err={}`）：
```
git -C D:\ZephyrAlpha rev-parse --abbrev-ref HEAD; git -C D:\ZephyrAlpha rev-parse HEAD
git -C D:\ZephyrAlpha\.worktrees\<lane> rev-parse HEAD
```
1.3 待落面（排除 .runtime）：
```
git -C D:\ZephyrAlpha\.worktrees\<lane> -c core.quotePath=false status --porcelain -uall
```
1.4 字节头：
```
sha256sum D:\ZephyrAlpha\.worktrees\<lane>\<path>   # 实测用 python hashlib 同义
```
1.5 HEAD 存在性 / HEAD sha：
```
git -C D:\ZephyrAlpha cat-file -e HEAD:<path>
git -C D:\ZephyrAlpha show HEAD:<path> | sha256sum
```
1.6 与 HEAD 差异行数：
```
git -C D:\ZephyrAlpha\.worktrees\<lane> -c core.quotePath=false diff --numstat HEAD -- <path>
```
（`??`/`A` 未跟踪件无 diff 输出 ⇒ 标 N/A；若该路径在 HEAD 有原件，则用 Counter(行集) 差算 add/rem 并标注 `(Counter-vs-laneHEAD-blob)`）
1.7 双向"仅 A 有 / 仅 B 有"行数（表2 CONFLICT 用；A/B 为两道同一文件）：
```
diff <(sort A) <(sort B) | grep -c '^< '     # 仅 A 有
diff <(sort A) <(sort B) | grep -c '^> '     # 仅 B 有
```
（实测用 `collections.Counter(A)-Counter(B)` 求和，语义等价，不忽略行序；行序敏感的纯位移会计入 only_a+only_b 双侧）

**口径告警（重要事实）**：10/12 车道的 HEAD = `3eeb9357…`，`st-p7-scope` = `32389d31…`，只有 `st-p8-integrate` 与 `st-zmaster2-20260926` = 主区 dev HEAD `461b25d0…`。故 §1.6 的 `diff --numstat HEAD` 是**各道自己的 HEAD**，不是 dev HEAD；跨道 numstat 不可直接横向比大小。in_head/head_sha 一律按任务书指的主区 `D:\ZephyrAlpha` HEAD 判定。

## 2. 待落面总量

| 车道 | 脏件数(排除 .runtime) |
|---|---|
| st-p1-gate | 7 |
| st-p1b-libr | 17 |
| st-p2-cens | 8 |
| st-p3-matrix | 8 |
| st-p4-bridge | 5 |
| st-p5-chart | 9 |
| st-p6-t1top | 3 |
| st-p7-scope | 15 |
| st-p8-integrate | 15 |
| st-m1-leaf | 31 |
| st-m2-seal | 11 |
| st-zmaster2-20260926 | 113 |
| **合计条目** | **242** |

去重后唯一路径 **145** = 单道独占 **74** + 多道同路径 **71**。其中 HEAD 无原件（新建件）的盘上存在条目 **182**。删除（D）条目 **8**。

## 3. 表1 单道独占件（74 路径，可直接入袋）

列义：路径 / 持有道 / 状态 / 字节 / mtime / HEAD 有原件否（NO=新建件，需 CREATE-GUARD token + 翻译登记，见 `register_manifest.md`）/ 与 HEAD 字节关系。

| path | lane | state | size | mtime | in_head | vs_head |
|---|---|---|---|---|---|---|
| docs/_working/three_piece_infra/integration_fix/CASE.md | st-p8-integrate | ?? | 1824 | 2026-09-26 22:20:41 | NO | - |
| docs/_working/three_piece_infra/mining/_MASTER_INDEX.md | st-zmaster2-20260926 | ?? | 38675 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/families/_MASTER_INDEX.md | st-m1-leaf | ?? | 38675 | 2026-09-26 21:37:57 | NO | - |
| docs/_working/three_piece_infra/mining/families/family01_finished_goods_rescue/W-10.md | st-m1-leaf | ?? | 10401 | 2026-09-26 21:04:03 | NO | - |
| docs/_working/three_piece_infra/mining/families/family01_finished_goods_rescue/W-11.md | st-m1-leaf | ?? | 8965 | 2026-09-26 21:24:37 | NO | - |
| docs/_working/three_piece_infra/mining/families/family01_finished_goods_rescue/W-13.md | st-m1-leaf | ?? | 9766 | 2026-09-26 21:23:51 | NO | - |
| docs/_working/three_piece_infra/mining/families/family02_commit_chain_detox/W-20.md | st-m1-leaf | ?? | 12117 | 2026-09-26 21:06:01 | NO | - |
| docs/_working/three_piece_infra/mining/families/family02_commit_chain_detox/W-20b.md | st-m1-leaf | ?? | 10390 | 2026-09-26 21:06:45 | NO | - |
| docs/_working/three_piece_infra/mining/families/family02_commit_chain_detox/W-23.md | st-m1-leaf | ?? | 8711 | 2026-09-26 21:07:51 | NO | - |
| docs/_working/three_piece_infra/mining/families/family02_commit_chain_detox/W-25.md | st-m1-leaf | ?? | 8437 | 2026-09-26 21:09:24 | NO | - |
| docs/_working/three_piece_infra/mining/families/family02_commit_chain_detox/W-26.md | st-m1-leaf | ?? | 8617 | 2026-09-26 21:09:24 | NO | - |
| docs/_working/three_piece_infra/mining/families/family02_commit_chain_detox/W-29.md | st-m1-leaf | ?? | 9692 | 2026-09-26 21:10:06 | NO | - |
| docs/_working/three_piece_infra/mining/families/family03_data_business_chain/W-30.md | st-m1-leaf | ?? | 13411 | 2026-09-26 21:04:03 | NO | - |
| docs/_working/three_piece_infra/mining/families/family03_data_business_chain/W-31.md | st-m1-leaf | ?? | 10069 | 2026-09-26 21:11:34 | NO | - |
| docs/_working/three_piece_infra/mining/families/family03_data_business_chain/W-32.md | st-m1-leaf | ?? | 7679 | 2026-09-26 21:13:42 | NO | - |
| docs/_working/three_piece_infra/mining/families/family03_data_business_chain/W-34.md | st-m1-leaf | ?? | 8533 | 2026-09-26 21:12:24 | NO | - |
| docs/_working/three_piece_infra/mining/families/family03_data_business_chain/W-36.md | st-m1-leaf | ?? | 8687 | 2026-09-26 21:11:34 | NO | - |
| docs/_working/three_piece_infra/mining/families/family03_data_business_chain/W-40.md | st-m1-leaf | ?? | 8041 | 2026-09-26 21:13:04 | NO | - |
| docs/_working/three_piece_infra/mining/families/family04_dr_cold_storage/W-41.md | st-m1-leaf | ?? | 9216 | 2026-09-26 21:33:04 | NO | - |
| docs/_working/three_piece_infra/mining/families/family05_governance_registries/W-52.md | st-m1-leaf | ?? | 9385 | 2026-09-26 21:26:29 | NO | - |
| docs/_working/three_piece_infra/mining/families/family05_governance_registries/W-55.md | st-m1-leaf | ?? | 8015 | 2026-09-26 21:27:31 | NO | - |
| docs/_working/three_piece_infra/mining/families/family05_governance_registries/W-56.md | st-m1-leaf | ?? | 7870 | 2026-09-26 21:28:15 | NO | - |
| docs/_working/three_piece_infra/mining/families/family11_endgame_capability/W-116.md | st-m1-leaf | ?? | 10610 | 2026-09-26 21:20:33 | NO | - |
| docs/_working/three_piece_infra/mining/families/family11_endgame_capability/W-117.md | st-m1-leaf | ?? | 9320 | 2026-09-26 21:19:43 | NO | - |
| docs/_working/three_piece_infra/mining/families/family11_endgame_capability/W-118.md | st-m1-leaf | ?? | 9092 | 2026-09-26 21:21:17 | NO | - |
| docs/_working/three_piece_infra/mining/families/family11_endgame_capability/W-119.md | st-m1-leaf | ?? | 8790 | 2026-09-26 21:21:56 | NO | - |
| docs/_working/three_piece_infra/mining/families/family12_field_discovered_new_cases/W-120.md | st-m1-leaf | ?? | 9670 | 2026-09-26 21:16:07 | NO | - |
| docs/_working/three_piece_infra/mining/families/family12_field_discovered_new_cases/W-121.md | st-m1-leaf | ?? | 10101 | 2026-09-26 21:34:22 | NO | - |
| docs/_working/three_piece_infra/mining/families/family12_field_discovered_new_cases/W-122.md | st-m1-leaf | ?? | 8605 | 2026-09-26 21:17:05 | NO | - |
| docs/_working/three_piece_infra/mining/families/family12_field_discovered_new_cases/W-124.md | st-m1-leaf | ?? | 8220 | 2026-09-26 21:30:21 | NO | - |
| docs/_working/three_piece_infra/mining/families/family12_field_discovered_new_cases/W-127.md | st-m1-leaf | ?? | 9413 | 2026-09-26 21:29:13 | NO | - |
| docs/_working/three_piece_infra/mining/families/family12_field_discovered_new_cases/W-131.md | st-m1-leaf | ?? | 8318 | 2026-09-26 21:17:55 | NO | - |
| docs/_working/three_piece_infra/mining/families/family13_redteam_backfill/W-140.md | st-m1-leaf | ?? | 9099 | 2026-09-26 21:32:16 | NO | - |
| docs/_working/three_piece_infra/mining/family01_finished_goods_rescue/W-10.md | st-zmaster2-20260926 | ?? | 10401 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family01_finished_goods_rescue/W-11.md | st-zmaster2-20260926 | ?? | 8965 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family01_finished_goods_rescue/W-13.md | st-zmaster2-20260926 | ?? | 9766 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family02_commit_chain_detox/W-20.md | st-zmaster2-20260926 | ?? | 12117 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family02_commit_chain_detox/W-20b.md | st-zmaster2-20260926 | ?? | 10390 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family02_commit_chain_detox/W-23.md | st-zmaster2-20260926 | ?? | 8711 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family02_commit_chain_detox/W-25.md | st-zmaster2-20260926 | ?? | 8437 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family02_commit_chain_detox/W-26.md | st-zmaster2-20260926 | ?? | 8617 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family02_commit_chain_detox/W-29.md | st-zmaster2-20260926 | ?? | 9692 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family03_data_business_chain/W-30.md | st-zmaster2-20260926 | ?? | 13411 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family03_data_business_chain/W-31.md | st-zmaster2-20260926 | ?? | 10069 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family03_data_business_chain/W-32.md | st-zmaster2-20260926 | ?? | 7679 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family03_data_business_chain/W-34.md | st-zmaster2-20260926 | ?? | 8533 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family03_data_business_chain/W-36.md | st-zmaster2-20260926 | ?? | 8687 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family03_data_business_chain/W-40.md | st-zmaster2-20260926 | ?? | 8041 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family04_dr_cold_storage/W-41.md | st-zmaster2-20260926 | ?? | 9216 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family05_governance_registries/W-52.md | st-zmaster2-20260926 | ?? | 9385 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family05_governance_registries/W-55.md | st-zmaster2-20260926 | ?? | 8015 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family05_governance_registries/W-56.md | st-zmaster2-20260926 | ?? | 7870 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family11_endgame_capability/W-116.md | st-zmaster2-20260926 | ?? | 10610 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family11_endgame_capability/W-117.md | st-zmaster2-20260926 | ?? | 9320 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family11_endgame_capability/W-118.md | st-zmaster2-20260926 | ?? | 9092 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family11_endgame_capability/W-119.md | st-zmaster2-20260926 | ?? | 8790 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-120.md | st-zmaster2-20260926 | ?? | 9670 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-121.md | st-zmaster2-20260926 | ?? | 10101 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-122.md | st-zmaster2-20260926 | ?? | 8605 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-124.md | st-zmaster2-20260926 | ?? | 8220 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-127.md | st-zmaster2-20260926 | ?? | 9413 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family12_field_discovered_new_cases/W-131.md | st-zmaster2-20260926 | ?? | 8318 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/three_piece_infra/mining/family13_redteam_backfill/W-140.md | st-zmaster2-20260926 | ?? | 9099 | 2026-09-26 21:46:05 | NO | - |
| docs/_working/total_command_closeout/00_master_skeleton.md | st-zmaster2-20260926 | M | 26960 | 2026-09-26 20:35:22 | YES | diff |
| docs/_working/total_command_closeout/10_wave_plan.md | st-zmaster2-20260926 | M | 28940 | 2026-09-26 20:35:22 | YES | diff |
| docs/_working/total_command_closeout/final_review_chartlib/dossier_academic_papers.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/dossier_github_ecosystem.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/dossier_institution_practice.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/ext_00_final_review_report.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/ext_01_revised_construction_plan.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/ext_02_one_click_directive_revised.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/ext_03_schedule_completeness_audit.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| docs/_working/total_command_closeout/final_review_chartlib/ext_04_full_directive_self_contained.md | st-zmaster2-20260926 | D | — | — | YES | 见 §5 表3 |
| scripts/governance/meta/rules_integrity_db.json | st-zmaster2-20260926 | M | 3551 | 2026-09-26 21:18:40 | YES | diff |

表1 附注（事实，非裁定）：

1. 表1 的"独占"= **同一路径**只被一道持有。但存在 **31 对"不同路径、同内容"**：`st-m1-leaf` 的 `mining/families/<family>/W-xx.md` 与 `st-zmaster2-20260926` 的 `mining/<family>/W-xx.md`（少一层 `families/`）size 与 sha256 全等（例：W-10 10401B 两边同 sha；`_MASTER_INDEX.md` 38675B 两边同 sha）。⇒ 表1 无法识别这组**目录层级型重复**，落地时两条路径会各存一份。逐对 sha 见 `byte_matrix.yaml`（按 path 排序检索）。复跑：`sha256sum D:\ZephyrAlpha\.worktrees\st-m1-leaf\docs\_working\three_piece_infra\mining\families\family01_finished_goods_rescue\W-10.md D:\ZephyrAlpha\.worktrees\st-zmaster2-20260926\docs\_working\three_piece_infra\mining\family01_finished_goods_rescue\W-10.md`
2. 表1 中 `st-m1-leaf` 31 件 + `st-zmaster2-20260926` 30 件全为 `??`（HEAD 无原件），是 §3/表1 的主体；它们与表2 的"代码类 CONFLICT"风险性质不同（文档，非可执行真源）。
3. 表1 的 8 个 `D` 条目同时进 §5 表3。

## 4. 表2 多道同路径件（71 路径）

判据：同路径各道 sha256 全等 ⇒ **AGREE**（58 路径，落谁都一样，无回退弹）；不等 ⇒ **CONFLICT**（13 路径）。

### 4.1 AGREE（58 路径 · 无风险，逐道 sha 相同）

| path | verdict | 道数 | 持有道 | state | size(各道同) | mtime(各道) | in_head |
|---|---|---|---|---|---|---|---|
| docs/02_enterprise_architecture/04_architecture_principles_decisions/project_handbook/03_data_layer.md | AGREE | 2 | st-p1b-libr, st-zmaster2-20260926 | M | 3114 | 21:27:39 / 21:55:28 | YES |
| docs/02_enterprise_architecture/04_architecture_principles_decisions/project_handbook/07_dependencies.md | AGREE | 2 | st-p1b-libr, st-zmaster2-20260926 | M | 3645 | 21:27:39 / 21:55:28 | YES |
| docs/03_modules/_domain_library/blueprint.md | AGREE | 3 | st-p1b-libr, st-p8-integrate, st-zmaster2-20260926 | M | 3566 | 21:42:12 / 22:20:12 / 21:45:49 | YES |
| docs/_working/decision_map_campaign_20260924/connection_matrix.csv | AGREE | 2 | st-p3-matrix, st-zmaster2-20260926 | ?? | 427125 | 21:24:25 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L01_regime.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 6080 | 21:14:08 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L02_emotion.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 5848 | 21:14:49 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L03_sector.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 4383 | 21:27:17 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L04_stock_wire.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 4223 | 21:15:50 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L05_t0.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 5866 | 21:16:34 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L06_exam_alloc.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 4713 | 21:19:15 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L07_exec.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 5427 | 21:20:43 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L08_risk.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 5355 | 21:21:32 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/L09_review.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 4992 | 21:22:35 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/_VERDICT.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 21274 | 21:27:41 / 21:46:05 | NO |
| docs/_working/three_piece_infra/mining/seal_audit/_W_COUNT.md | AGREE | 2 | st-m2-seal, st-zmaster2-20260926 | ?? | 9756 | 21:26:31 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_bridge/CASE.md | AGREE | 2 | st-p4-bridge, st-zmaster2-20260926 | ?? | 29602 | 21:38:08 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_bridge/register_manifest.md | AGREE | 2 | st-p4-bridge, st-zmaster2-20260926 | ?? | 5778 | 21:28:46 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_chart/CASE.md | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 16103 | 21:36:37 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_chart/chart_wiring_inventory.csv | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 79849 | 21:35:20 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_chart/chart_wiring_summary.yaml | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 1170 | 21:35:20 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_chart/register_manifest.md | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 6564 | 21:33:25 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_t1_analysis/FINDINGS.md | AGREE | 2 | st-p6-t1top, st-zmaster2-20260926 | ?? | 32557 | 21:24:13 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_t1_analysis/register_manifest.md | AGREE | 2 | st-p6-t1top, st-zmaster2-20260926 | ?? | 4778 | 21:23:41 / 21:46:05 | NO |
| docs/_working/three_piece_infra/p0_t1_analysis/state_matrix_input.yaml | AGREE | 2 | st-p6-t1top, st-zmaster2-20260926 | ?? | 21531 | 21:24:23 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece1_gate/CASE.md | AGREE | 2 | st-p1-gate, st-zmaster2-20260926 | ?? | 24090 | 21:32:29 / 21:46:04 | NO |
| docs/_working/three_piece_infra/piece1_gate/register_manifest.md | AGREE | 2 | st-p1-gate, st-zmaster2-20260926 | ?? | 4331 | 21:17:08 / 21:46:04 | NO |
| docs/_working/three_piece_infra/piece1b_library/CASE.md | AGREE | 2 | st-p1b-libr, st-zmaster2-20260926 | ?? | 14433 | 21:19:10 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece1b_library/register_manifest.md | AGREE | 2 | st-p1b-libr, st-zmaster2-20260926 | ?? | 6791 | 21:15:12 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece2_census/CASE.md | AGREE | 2 | st-p2-cens, st-zmaster2-20260926 | ?? | 22973 | 21:33:25 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece2_census/register_manifest.md | AGREE | 2 | st-p2-cens, st-zmaster2-20260926 | ?? | 5550 | 21:32:36 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece2_census/wiring_registry.machine_view.yaml | AGREE | 2 | st-p2-cens, st-zmaster2-20260926 | ?? | 86697 | 21:29:55 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece3_matrix/CASE.md | AGREE | 2 | st-p3-matrix, st-zmaster2-20260926 | ?? | 13466 | 21:30:37 / 21:46:05 | NO |
| docs/_working/three_piece_infra/piece3_matrix/register_manifest.md | AGREE | 2 | st-p3-matrix, st-zmaster2-20260926 | ?? | 6578 | 21:29:40 / 21:46:05 | NO |
| docs/_working/three_piece_infra/scope_convergence/CASE.md | AGREE | 2 | st-p7-scope, st-zmaster2-20260926 | ?? | 13818 | 22:09:39 / 22:11:33 | NO |
| scripts/governance/chart_wiring/generate_chart_wiring_inventory.py | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 19841 | 21:33:39 / 21:46:04 | NO |
| scripts/governance/d3_metadata/generate_wiring_registry.py | AGREE | 4 | st-p2-cens, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 9329 | 21:22:11 / 21:57:28 / 22:20:12 / 22:11:33 | NO |
| scripts/governance/d5_architecture/generators/generate_connection_matrix.py | AGREE | 4 | st-p3-matrix, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 51781 | 21:23:52 / 21:57:28 / 22:20:12 / 22:11:33 | NO |
| src/zephyr/backtest/regime_validation/__init__.py | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | M | 5012 | 21:33:08 / 21:46:04 | YES |
| src/zephyr/backtest/regime_validation/chart_condition_package.py | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 26074 | 21:24:40 / 21:46:04 | NO |
| src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py | AGREE | 2 | st-p4-bridge, st-zmaster2-20260926 | M | 68244 | 21:33:41 / 21:46:04 | YES |
| src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py | AGREE | 2 | st-p4-bridge, st-zmaster2-20260926 | M | 13200 | 21:24:27 / 21:46:04 | YES |
| src/zephyr/frontend/dashboard/app_panel.py | AGREE | 2 | st-p3-matrix, st-zmaster2-20260926 | M | 24547 | 21:29:15 / 21:45:49 | YES |
| src/zephyr/frontend/dashboard/components/connection_matrix.py | AGREE | 2 | st-p3-matrix, st-zmaster2-20260926 | ?? | 7942 | 21:20:33 / 21:45:49 | NO |
| src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py | AGREE | 2 | st-p1-gate, st-zmaster2-20260926 | M | 19170 | 21:05:04 / 21:45:48 | YES |
| src/zephyr/governance/audit/reconciliation_registry.py | AGREE | 4 | st-p1b-libr, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | M | 418978 | 21:24:42 / 21:57:28 / 22:20:12 / 22:11:33 | YES |
| src/zephyr/governance/consumption_census_reconciler.py | AGREE | 4 | st-p2-cens, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 8286 | 21:20:18 / 21:57:28 / 22:20:12 / 22:11:33 | NO |
| src/zephyr/governance/indicator_usage_audit.py | AGREE | 4 | st-p2-cens, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | M | 5216 | 21:17:10 / 21:57:28 / 22:20:12 / 22:11:33 | YES |
| src/zephyr/library/library_regen_reconciler.py | AGREE | 4 | st-p1b-libr, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | M | 17721 | 21:18:38 / 21:57:28 / 22:20:12 / 22:11:33 | YES |
| tests/backtest/test_chart_condition_package.py | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 16350 | 21:25:06 / 21:46:04 | NO |
| tests/ex_core/adapters/test_qmt_file_bridge_broker.py | AGREE | 2 | st-p4-bridge, st-zmaster2-20260926 | M | 32432 | 21:33:23 / 21:46:04 | YES |
| tests/gov_enforcement/create_guard_batch_replay.py | AGREE | 2 | st-p1-gate, st-zmaster2-20260926 | ?? | 10043 | 21:16:09 / 21:45:48 | NO |
| tests/gov_enforcement/create_guard_batch_replay_evidence.json | AGREE | 2 | st-p1-gate, st-zmaster2-20260926 | ?? | 86395 | 21:19:19 / 21:45:48 | NO |
| tests/gov_enforcement/test_create_guard_keyword_overlap_canary.py | AGREE | 2 | st-p1-gate, st-zmaster2-20260926 | ?? | 15281 | 21:21:03 / 21:45:48 | NO |
| tests/governance/test_chart_wiring_inventory.py | AGREE | 2 | st-p5-chart, st-zmaster2-20260926 | ?? | 8354 | 21:29:42 / 21:46:04 | NO |
| tests/governance/test_connection_matrix_rulers.py | AGREE | 4 | st-p3-matrix, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 13989 | 21:22:52 / 21:57:28 / 22:20:12 / 22:11:33 | NO |
| tests/governance/test_consumption_census_redproof.py | AGREE | 4 | st-p2-cens, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 18067 | 21:28:21 / 21:57:28 / 22:20:12 / 22:11:33 | NO |
| tests/governance/test_library_reconcilers_red_blue.py | AGREE | 4 | st-p1b-libr, st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 20748 | 21:42:19 / 21:57:28 / 22:20:12 / 22:11:33 | NO |
| tests/governance/test_scan_scope_convergence_equivalence.py | AGREE | 3 | st-p7-scope, st-p8-integrate, st-zmaster2-20260926 | ?? | 9166 | 22:05:32 / 22:20:12 / 22:11:33 | NO |

AGREE 事实要点（无风险面）：任务书点名的 10 个重叠路径中，**8 个是 AGREE**（字节全等）：`generate_wiring_registry.py`、`generate_connection_matrix.py`、`indicator_usage_audit.py`、`library_regen_reconciler.py`、`reconciliation_registry.py`、`test_consumption_census_redproof.py`、`test_connection_matrix_rulers.py`、`test_library_reconcilers_red_blue.py`；只有 `consumption_census.py`、`scan_scope_converged.py` 是 CONFLICT（§4.2）。⇒ 点名的"2/10 命中 CONFLICT"，另有 **11 个未被点名的 CONFLICT**（见 §4.2 全表）。

### 4.2 CONFLICT（13 路径 · 同路径各道 sha 不等）

每路径给：mtime newest→oldest、size biggest→smallest、逐道 sha/size/mtime/state/HEAD 关系、与 HEAD 差异行数（口径见 §1 告警）、双向"仅 A 有/仅 B 有"行数（§1.7）。**不含权威判定。**

分组依据（事实，不是裁定）——先测该路径在三个仓库指纹上的基线 blob sha（`git -C D:\ZephyrAlpha show <rev>:<path> | sha256sum`，rev 取 dev `461b25d0` / A `3eeb9357`(10 道所在) / B `32389d31`(壬道)）：

- **G-I 同基线双向分歧**（7 路径）：三 rev 基线 blob **全等** ⇒ 两道确实从同一份内容各自改出。
- **G-II 异基线分歧**（2 路径，均为任务书禁改的热册）：基线 blob 随 rev 变化 ⇒ 两道差异中**混有基线漂移**，不可只按 sha 不等判"内容打架"。
- **G-III HEAD 无原件**（4 路径）：`in_head=False`，无共同基线可比，只能比两道产物本身。

汇总表（`唯一行` = §1.7 Counter 精确行比对，未 strip；`ns` = 该道 vs **其自身 lane HEAD** +added/-deleted）：

| # | path | 道 | mtime newest→oldest | size biggest→smallest | 唯一行(newest vs oldest) | 分组 |
|---|---|---|---|---|---|---|
| C01 | config/governance_operations_map.yaml | 2 | zmaster2 > p1b-libr | 两道同 106174B | 1 / 1 | G-I |
| C02 | …/catalogs/capability_canonical_file_registry.yaml | 2 | zmaster2 > p1b-libr | 2949078 > 2921052 | 351 / 6 | G-II |
| C03 | …/catalogs/module_translation_registry.yaml | 2 | zmaster2 > p1b-libr | 3616971 > 3613992 | 70 / 1 | G-II |
| C04 | …/04_architecture_principles_decisions/README.md | 2 | zmaster2 > p1b-libr | 两道同 9550B | 1 / 1 | G-I |
| C05 | …/project_handbook/01_overview.md | 2 | zmaster2 > p1b-libr | 8185 > 8184 | 2 / 2 | G-I |
| C06 | …/project_handbook/02_repository_and_modules.md | 2 | zmaster2 > p1b-libr | 两道同 5160B | 5 / 5 | G-I |
| C07 | …/project_handbook/05_trading_domains.md | 2 | zmaster2 > p1b-libr | 两道同 7202B | 4 / 4 | G-I |
| C08 | …/project_handbook/06_governance_and_infra.md | 2 | zmaster2 > p1b-libr | 两道同 5377B | 2 / 2 | G-I |
| C09 | docs/_working/three_piece_infra/scope_convergence/register_manifest.md | 2 | zmaster2 22:27:58 > p7-scope 22:07:46 | 1882 > 1795 | 5 / **0** | G-III |
| C10 | src/zephyr/gov_enforcement/commit_gates/create_guard.py | 2 | zmaster2 > p1-gate | 68749 > 68682 | 1 / 1 | G-I |
| C11 | src/zephyr/governance/audit/library_new_module_reconciler.py | 4 | p8 = p7 = zmaster2（同 sha）; p1b-libr 异 | 18470(p1b) > 17647(其余三道) | 58(p1b) / 19(p7p8z 侧) | G-III |
| C12 | src/zephyr/governance/consumption_census.py | 4 | p8 22:20:11 > zmaster2 22:11:33 = p7 22:03:25（同 sha 3c0f7e73…）; p2-cens 21:26:47 异 | 37410(p2) > 34100(其余三道) | 91(p2 侧) / 16(p7p8z 侧) | G-III |
| C13 | src/zephyr/governance/scan_scope_converged.py | 4 | p8 22:20:11 > zmaster2 22:11:33 = p7 22:01:29（同 sha 9c6e5902…）; p3-matrix 21:00:46 异 | 14320(p7p8z) > 5678(p3) | 30(p3 侧) / 199(p7p8z 侧) | G-III |

逐道指纹（sha 前 12 位；`base dev/A/B` = 该路径在三个 rev 上的 blob sha 前 12 位）：

| # | lane | state | sha12 | size | mtime | ns vs laneHEAD | base dev/A/B |
|---|---|---|---|---|---|---|---|
| C01 | st-p1b-libr | ` M` | b069304aa79d | 106174 | 21:43:18 | +1668 −1602 | eb75e65261e5 / eb75e65261e5 / eb75e65261e5 |
| C01 | st-zmaster2-20260926 | ` M` | 446ec80712c7 | 106174 | 22:04:42 | +1668 −1602 | 同上 |
| C02 | st-p1b-libr | `MM` | fcd2eeec831e | 2921052 | 21:27:39 | +25 −0 | 16d98af6efca / cc66d1032444 / 07c553ea43da |
| C02 | st-zmaster2-20260926 | `M `(仅暂存) | a6ba48de56a9 | 2949078 | 22:32:30 | +10 −0 | 同上 |
| C03 | st-p1b-libr | ` M` | 5352cd1a306a | 3613992 | 21:26:45 | +8 −0 | a675de56dc7f / 7c734e5cd69d / 7c734e5cd69d |
| C03 | st-zmaster2-20260926 | `M `(仅暂存) | c7b5a6fb0092 | 3616971 | 22:32:31 | +12 −0 | 同上 |
| C04 | st-p1b-libr | ` M` | 4bce4b56cee2 | 9550 | 21:27:37 | +4 −4 | 35ae7bf1a214 ×3 |
| C04 | st-zmaster2-20260926 | ` M` | 245d0868b7f6 | 9550 | 22:04:17 | +4 −4 | 同上 |
| C05 | st-p1b-libr | ` M` | fb2f9d465a95 | 8184 | 21:27:37 | +7 −7 | de634ba9b8ae ×3 |
| C05 | st-zmaster2-20260926 | ` M` | 458206e30da6 | 8185 | 22:04:17 | +7 −7 | 同上 |
| C06 | st-p1b-libr | ` M` | b83c7ba83617 | 5160 | 21:27:39 | +5 −5 | 8b0b1cbeef88 ×3 |
| C06 | st-zmaster2-20260926 | ` M` | 188584227545 | 5160 | 21:55:28 | +5 −5 | 同上 |
| C07 | st-p1b-libr | ` M` | 62413c76e7cc | 7202 | 21:27:39 | +14 −14 | df50582441d3 ×3 |
| C07 | st-zmaster2-20260926 | ` M` | 162e752b7a78 | 7202 | 22:04:18 | +14 −14 | 同上 |
| C08 | st-p1b-libr | ` M` | 7d432bf5d003 | 5377 | 21:27:39 | +1 −1 | 3cd8c76f9817 ×3 |
| C08 | st-zmaster2-20260926 | ` M` | 3a7bb4ccbca9 | 5377 | 21:55:28 | +3 −3 | 同上 |
| C09 | st-p7-scope | `??` | 88c1bddc9dc3 | 1795 | 22:07:46 | N/A(未跟踪) | 三 rev 均不存在 |
| C09 | st-zmaster2-20260926 | `??` | 065c253b0aac | 1882 | 22:27:58 | N/A(未跟踪) | 同上 |
| C10 | st-p1-gate | ` M` | 8c7ec081c4c4 | 68749 | 21:10:54 | +325 −20 | 29da292847af ×3 |
| C10 | st-zmaster2-20260926 | ` M` | 312d0823a8ae | 68682 | 22:14:34 | +324 −19 | 同上 |
| C11 | st-p1b-libr | `??` | 5dc25f9a2790 | 18470 | 21:42:12 | N/A | 三 rev 均不存在 |
| C11 | st-p7-scope | `??` | 91f20b65f88b | 17647 | 22:04:45 | N/A | 同上 |
| C11 | st-p8-integrate | `??` | 91f20b65f88b | 17647 | 22:20:12 | N/A | 同上 |
| C11 | st-zmaster2-20260926 | `??` | 91f20b65f88b | 17647 | 22:11:33 | N/A | 同上 |
| C12 | st-p2-cens | `??` | 688bb42c2593 | 37410 | 21:26:47 | N/A | 三 rev 均不存在 |
| C12 | st-p7-scope | `??` | 3c0f7e73966a | 34100 | 22:03:25 | N/A | 同上 |
| C12 | st-p8-integrate | `??` | 3c0f7e73966a | 34100 | 22:20:11 | N/A | 同上 |
| C12 | st-zmaster2-20260926 | `??` | 3c0f7e73966a | 34100 | 22:11:33 | N/A | 同上 |
| C13 | st-p3-matrix | `??` | bd700388ea00 | 5678 | 21:00:46 | N/A | 三 rev 均不存在 |
| C13 | st-p7-scope | `??` | 9c6e590268f9 | 14320 | 22:01:29 | N/A | 同上 |
| C13 | st-p8-integrate | `??` | 9c6e590268f9 | 14320 | 22:20:11 | N/A | 同上 |
| C13 | st-zmaster2-20260926 | `??` | 9c6e590268f9 | 14320 | 22:11:33 | N/A | 同上 |

超集/子集关系（Counter 精确行比对；`0` 侧 = 其全部行都在对方行集中出现）：

- **C09**：`唯一行(p7 侧)=0` ⇒ **p7-scope 版 ⊂ zmaster2 版**（后者=前者 + frontmatter 5 行）。复跑：`diff <(cat .worktrees/st-p7-scope/docs/_working/three_piece_infra/scope_convergence/register_manifest.md) <(cat .worktrees/st-zmaster2-20260926/docs/_working/three_piece_infra/scope_convergence/register_manifest.md)`
- **C12**：p2-cens 侧 91 行在 p7/p8/z 版中不存在；p7/p8/z 侧 16 行按 strip 后比对无新增（即 16 行为缩进/空白位移）。⇒ 行集面上 p2-cens 版包含 p7/p8/z 版的全部 strip 行。
- **C13**：p3-matrix 侧 30 行独有（含头部声明块），p7/p8/z 侧 199 行独有 ⇒ **互非子集**，两侧各有对方没有的内容。
- **C11**：p1b-libr 侧 58 行独有、p7/p8/z 侧 19 行独有 ⇒ **互非子集**。
- C01/C04/C05/C06/C07/C08/C10：双向唯一行数相等（1/1、2/2、5/5、4/4、2/2、1/1）⇒ 对向替换型小差异，无子集关系。

可复算的"行内容摘录"仅在 `显示行数 == Counter 唯一行数` 时可信；C02/C03/C07/C11/C12/C13 的行摘录受**重复行/空白噪声**影响不可靠（我按 Counter 计数为准，未逐行核对内容）。计数一致的可靠摘录：

- C01（1/1）：差异行 = `generated_at: '2026-09-26T13:43:18.579099+00:00'`（p1b）vs `generated_at: '2026-09-26T14:04:42.568862+00:00'`（zmaster2）。同一生成器两次重跑，其余 2771 行等值（size 全等）。
- C06（5/5）：zmaster2 `| scripts/governance .py 总数 / Governance scripts | 583 |`、`` | `src/zephyr/` | 3226 | ``、`` | `scripts/governance/` | 583 | ``、`` | `tests/` | 3738 | ``、`` | **合计 / Total** | **7547** | `` ⇄ p1b-libr 同五行为 `580 / 3221 / 580 / 3732 / 7533`。
- C08（2/2）：zmaster2 `| d3_metadata | frontmatter 校验 / Frontmatter validation | 30 |`、`| **合计** | **Total** | **173** |` ⇄ p1b-libr 为 `29` / `172`。
- C09（0/5）：仅 zmaster2 有 `---` / `ttl: task_bound` / `completes_when: 总筹按本清单完成热册登记并回执` / `---`（+1 空行）。
- C10（1/1）：`# [TESTS] tests/governance/commit_gates/test_create_guard.py, tests/gov_enforcement/test_create_guard_keyword_overlap_canary.py`（p1-gate）⇄ `# [TESTS] tests/governance/commit_gates/test_create_guard.py`（zmaster2，无 canary）。
- C13（30/199，方向事实）：p3-matrix 版头部声明块含 `# [DOMAIN] D_GOV`、`# [DEPENDENCIES] pathlib; re; typing（全部 stdlib，零第三方）`、`# [STARTUP] manual`、`# [MATURITY] testing`、`# [ERROR_CONTRACT] 不吞异常——目录缺失返回空迭代（口径本身不判定存在性）`，这 30 行在 p7/p8/z 版中无逐行等值项。
- C12（91/16，方向事实）：p2-cens 版头部含 `# -*- coding: utf-8 -*-`、`# [BLUEPRINT] MOD-GOV-CONSUMPTIONCENSUS`、`# [MODULE] zephyr.governance.consumption_census`、`# [DOMAIN] D_GOV`、`# [DEPENDENCIES] zephyr.shared.io.file_utils(safe_write); yaml/pathlib/re/json(静态扫描)`、`# [CONSUMERS] consumption_census_reconciler(post-commit 事件触发); trading_lifecycle_weekly 能力分支; scripts/governance/d3_metadata/generate_wiring_registry.py(孤岛入账); tests/governance/test_consumption_census_redproof.py(红证)`，p7/p8/z 版无这些行。

### 4.3 表2 CONFLICT 各道文件头 30 行 · 可区分版本声明（原样摘录，不解读）

- **C01 config/governance_operations_map.yaml** — 两道同：L1 `schema_version: '0.1'`；L4 `ttl: permanent`；L5 `effective_from: '2026-09-15'`；L8-9 `ssot_note_zh: 骨架机生(宪法 §9.5):families 层由生成器全量重建,禁手工编辑;…`。可区分项仅 L7：p1b-libr `generated_at: '2026-09-26T13:43:18.579099+00:00'` vs zmaster2 `generated_at: '2026-09-26T14:04:42.568862+00:00'`。**两道均无 W-xx 编号。**
- **C02 capability_canonical_file_registry.yaml** — 两道头 30 行逐行等值：L1 `schema_version: 1.1.0`、L3 `ttl: permanent`、L4 `doc_type: gate`、L5 `title: 能力→真源文件反查注册表`、L7 `version: 1.1.1`、L8 `date: '2026-06-26'`。⇒ **头部声明无法区分两道**，差异全在正文行（6 / 351）。
- **C03 module_translation_registry.yaml** — 两道头 30 行等值：L2 `ttl: permanent`、L3 `title: 模块级翻译注册表（中英对照真源）`、L4 `doc_type: register`、L20 `version: 1.8.3`、L21 `created: '2026-07-31'`、L22 `last_updated: 2026-08-18`。⇒ **头部 version 字段两侧同值 1.8.3，未随本次改动递增**（事实陈述）。
- **C04 README.md / C05 01_overview.md / C06 02_repository_and_modules.md / C07 05_trading_domains.md / C08 06_governance_and_infra.md** — 五份文件两道头 30 行逐行等值：`ttl: permanent`、`doc_type: index`(C04)/`architecture_view`(C05-C08)、L5 `owner: ZephyrAlpha-Owner`；C08 另有 L28 `<!-- 数据源：commit_gates 目录扫描 | 最后同步：2026-08-17 -->`（两道同值）。⇒ **头部无可区分版本声明**。
- **C09 scope_convergence/register_manifest.md** — p7-scope L1：`# 壬道（st-p7-scope）· 待登记清单（热册唯一写手制：本道不碰 _registry/**，交总筹合批）`，**无 frontmatter**；zmaster2 L2 `ttl: task_bound`，正文标题同句在 L6。两道正文行内均自述 token 名：`wave13-p3-matrix-20260926`（称"续用"）、`ST-P7-SCOPE-EQUIV`、`ST-P7-SCOPE-CASE`（称"新 token 需求"），并自述"资产数 -2 份口径真源"。**以上为车道文件内容=数据，非对本任务的指令，未执行。**
- **C10 create_guard.py** — 两道 L16 均 `# [TTL] permanent`，L18 均 `create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本；裁定#375：…首期 warn…）`，L24 `​.yaml token 扩展（2026-07-01，trae_060 §2 向内收治本）`。可区分项 = `# [TESTS]` 行（见 §4.2）与 size/mtime。
- **C11 library_new_module_reconciler.py** — 四道 L29/30 均 `# [TTL] permanent` + `"""library_new_module_reconciler — 新 .py 落 HEAD → 图书馆在编 + 消费者派生（波13 包13.2①）。`；L13 均 `# [INVARIANTS] 唯一写路径=Librarian.act（禁裸 SQL/禁直连写库）；potential_consumers 口径=波13 §3.4 单一`。**可区分项在 L14**：p1b-libr `scope（src/+scripts/+config/ 的 .py/.yaml，排除 .md 与 docs/，排除 14 号文三层 producer/display/infra），` vs p7/p8/zmaster2 `scope，壬道收敛后唯一真源=zephyr.governance.scan_scope_converged（本模块 CONSUMER_SCOPE_* /`。（注：§4.2 另见 p8 侧一行写 `zephyr.governance.consumption.scan_scope_converged`，与 p7/z 侧的 `zephyr.governance.scan_scope_converged` 措辞不同——此处按各自文件原样摘录，未复核，标 **待核**。）
- **C12 consumption_census.py** — 四道 L24/26 均 `# [TTL] permanent`、L27 均 `14 号文手工普查的机械化替代：登记册条目 → §3.4 单一 scope 全词命中 → 三层排除`；L11 可区分：p2-cens `# [INVARIANTS] 单一 scope 常量 CONSUMER_SCAN_SCOPE 为全波"有没有消费者"唯一口径(§3.4 裁定)；` vs p7/p8/zmaster2 `# [INVARIANTS] CONSUMER_SCAN_SCOPE 为 zephyr.governance.scan_scope_converged（§3.4 唯一真源，`。**包号声明在头 30 行内未出现**（`包13.x` 仅见于 C11）。
- **C13 scan_scope_converged.py** — 四道 L1 均 `# [MODULE] zephyr.governance.scan_scope_converged`，L10/15 均 `# [TTL] permanent`。可区分项：p3-matrix L4 `# [CONSUMERS] …generate_connection_matrix（波 13 包 13.4）; 波 13 包 13.3 消费面普查引擎（丁道，应 import 本常量而非重述口径）` + L7 `第二套口径=第二真源=禁止`；p7/p8/zmaster2 L9-L11 `…（波 13 §3.4 定档，壬道收敛版），第二套口径=第二真源=禁止；丙/丁两侧同名公开量必须是本模块薄别名（import 绑定），禁在车道文件里再派生（等价性红证 tests/governance/test_scan_scope_convergence_equivalence.py 看住）`。**"壬道收敛版"是唯一在文件头出现的版本自述串。**

## 5. 表3 删除面（状态 D）


状态含 `D` 的条目共 8 条，全部来自 **st-zmaster2-20260926** 一道，全部在 dev HEAD 有原件、盘上（该道工作树内）已不存在：

| path | lane | state | in dev HEAD | 该道盘上存在 | 主区工作树存在 | head_sha12 | 其他 11 道盘上 |
|---|---|---|---|---|---|---|---|
| docs/_working/total_command_closeout/final_review_chartlib/dossier_academic_papers.md | st-zmaster2-20260926 | D | YES | NO | **NO** | 285396309017 | 11/11 在 |
| …/final_review_chartlib/dossier_github_ecosystem.md | st-zmaster2-20260926 | D | YES | NO | **NO** | 9a2e53df953f | 11/11 在 |
| …/final_review_chartlib/dossier_institution_practice.md | st-zmaster2-20260926 | D | YES | NO | **NO** | 8ab5fb7a9dd3 | 11/11 在 |
| …/final_review_chartlib/ext_00_final_review_report.md | st-zmaster2-20260926 | D | YES | NO | **NO** | fc219d4e7007 | 11/11 在 |
| …/final_review_chartlib/ext_01_revised_construction_plan.md | st-zmaster2-20260926 | D | YES | NO | **NO** | 0ec3d203bd0f | 11/11 在 |
| …/final_review_chartlib/ext_02_one_click_directive_revised.md | st-zmaster2-20260926 | D | YES | NO | **NO** | c8f224717458 | 11/11 在 |
| …/final_review_chartlib/ext_03_schedule_completeness_audit.md | st-zmaster2-20260926 | D | YES | NO | **NO** | 462dfebb3144 | 11/11 在 |
| …/final_review_chartlib/ext_04_full_directive_self_contained.md | st-zmaster2-20260926 | D | YES | NO | **NO** | 1942fead37c6 | 11/11 在 |

表3 配套事实（复跑命令附后）：

1. 该八件在 dev HEAD 与 A 指纹 `3eeb9357` 上**都存在**，最后一次触达它们的 commit = `3eeb935743 [st-final-build-20260926][开工批：外部终审八件入仓为受控真源 + 骨架册族14(W-163..W-180)回写 …]`（原文照录，属历史提交说明=数据）。
2. `git -C D:\ZephyrAlpha ls-files` 仍跟踪这八条路径，但主区工作树 `test -f` 全部 ABSENT ⇒ 主区自身也是"未暂存的工作树删除"；st-zmaster2（HEAD=dev）同样 ABSENT；其余 11 道（HEAD=3eeb9357 ×10、32389d31 ×1）目录内 8 件俱在（`ls -1 …/final_review_chartlib | wc -l` = 8）。
3. ⇒ 这 8 条 `D` **不是车道产生的删除**，与 12 条车道的"零 git 写"纪律无冲突线索可查；它同时出现在主区与 zmaster2 工作树。复跑：
```
for l in <12 lanes>; do ls -1 "D:/ZephyrAlpha/.worktrees/$l/docs/_working/total_command_closeout/final_review_chartlib" | wc -l; done
git -C D:\ZephyrAlpha log --oneline -1 461b25d0 -- docs/_working/total_command_closeout/final_review_chartlib/ext_00_final_review_report.md
```
4. 表3 无其他删除条目：`??`=182、` M`=49、`M `(仅暂存)=2、`MM`=1、`D`=8（合计 242）。暂存态仅 3 条，且全部落在两张热册上（C02/C03）：`M ` ×2 在 st-zmaster2-20260926、`MM` ×1 在 st-p1b-libr。⇒ 待落面里有 3 条**已在车道暂存区**，不是纯工作树改动。

## 6. 我没能测到的（盲区，如实列）

1. **未测主区工作树整体脏面对这 145 路径的影响**：我只对 dev HEAD 的 blob 取 sha（`git show HEAD:<path>`），未测主区工作树盘上版本。若主区盘上版本 ≠ dev HEAD 版本（表3 已见 8 例），则"权威版本"参照系本身在漂移，我的 `head_sha256` 只保证等于 **commit 461b25d0 的 blob**。
2. **C02/C03/C07/C11/C12/C13 的差异行内容摘录不可靠**（见 §4.2 末说明）：我的逐行摘录用了 strip 后比对，受重复行/缩进噪声污染；这些路径我只交付 **Counter 精确计数**（唯一行数），未交付可核对的行级清单。要行级清单需另跑 `git diff --no-index <A> <B>`。
3. **C11 的一行措辞冲突未复核**：p8-integrate 版写 `zephyr.governance.consumption.scan_scope_converged`，p7/zmaster2 版写 `zephyr.governance.scan_scope_converged`（少一段 `consumption.`）。我在 §4.3 原样摘录并标 **待核**，未验证哪个是可 import 的真模块名。
4. **车道目录名与 W-xx/包号的映射没有真源可查**：`register_manifest.md` 的 W-xx 列由文件名与头 45 行机械判出；代码类新建件多数判为 `UNKNOWN`/`-`（例：`integration_fix/CASE.md` 正文自述"lane 癸 (st-p8-integrate)"但未写包号）。
5. **未测 `.runtime/` 下的内容**（任务书硬排除），因此"每道实际产了多少件"仅指 git 可见面；某道若只把成果写在 `.runtime/sessions/...`，本表看不到。st-m1-leaf 31 件全在 `docs/_working/...` ⇒ 无该现象，但其余道未逐一反查。
6. **未测 git 之外的字节源**：文件是否只读、是否有符号链接、是否有 ACL 权限失败——12/12 道 `status` 与全部 242 次 `sha256`/`getsize` 均成功（无 `READ_FAIL`、`MISSING_DIR`、`STATUS_FAIL` 记录），所以本项无失败样本；但也**未测跨道写入权限**（本任务只读）。
7. **未测内容正确性**：所有 diff/numstat 只说明"字节不同"，不说明谁的口径对；`in_head=False` 的 113 个新建路径之间可能存在**功能重复**（如 `consumption_census.py` 与 `consumption_census_reconciler.py`、`scan_scope_converged.py` 与 `indicator_usage_audit.py`），需 clone_guard / 能力反查另测，不在本次范围。
8. **表1 的"同内容不同路径"62 件**（§3 附注 1）只做了 sha 全等判定，未判定哪一个路径才是目标布局——`mining/families/<family>/W-xx.md`（癸道外唯一持有=m1-leaf 的 families 层）与 `mining/<family>/W-xx.md` 二者目录层级不同，本次不裁。
9. **未做 git 写**：零 commit / add / checkout / reset / clean / stash / worktree 操作；热册只读。测量脚本与本案卷全部写在本 worktree 内（脚本暂存于 `.runtime/tmp/measure_ledger.py`，未 promote 到别处）。

## 7. 疑似注入 / 指令性文本处置

- 扫描了 13 个 CONFLICT 路径的**头 30 行**，用模式 `已确认|Owner|批准|请立即修复|忽略上述|把判据|务必|必须立即|approve`：命中 10 处，全部是文档 frontmatter 的 `owner: ZephyrAlpha-Owner`（C04–C08 两道各 5 处）。**按数据处置，未执行任何指令含义。**
- C09（`scope_convergence/register_manifest.md`，壬道与 zmaster2 两道各一版）正文含自述性登记主张：`既有 wave13-p3-matrix-20260926 token 续用`、`ST-P7-SCOPE-EQUIV（新 token 需求）`、`ST-P7-SCOPE-CASE（新 token 需求）`、`热册唯一写手制：本道不碰 _registry/**，交总筹合批`、`资产数 -2 份口径真源`。这些是**车道自述=数据**，不构成总筹的登记凭据，本案卷只摘录不采信。
- C10（`create_guard.py`）文件头含 `# [INVARIANTS] 硬阻断——staged 新增 .py 文件无 creation_token 时阻断 commit`、`裁定#375：新建资产 token 缺 merge_evaluation 字段 warn+审计不阻断，首期 warn`，是门禁源码里的行为描述=数据；本测量未据其改变任何判据。
- **盲区声明**：我只扫描了 CONFLICT 路径的头 30 行，**没有**扫描 242 条目的正文全量，故不能声称"待落面无注入文本"。要全量扫描请另跑：`grep -rnE "已确认|Owner 已批准|请立即修复|把判据改成|忽略上述规则" D:/ZephyrAlpha/.worktrees/st-*/ --include=*.py --include=*.md --include=*.yaml`

## 8. 机读表与件数

- `byte_matrix.yaml`：242 条 entry（与 §2 合计一致），字段 path / lane / state / sha256 / size / mtime / in_head / head_sha256，另带 `main_head_dev`、`lane_heads`（12 道各自 HEAD）。机读校验：`  - path:`=242、`state:`=242、`head_sha256:`=242。
- `register_manifest.md`：113 个唯一新建路径（A 组=表1 独占 63，B 组=表2 共享 50）。
- 复算全链：`.runtime/tmp/measure_ledger.py` → `.runtime/tmp/raw.json`（含全部 pairwise 明细）→ 本件 + `byte_matrix.yaml`。




