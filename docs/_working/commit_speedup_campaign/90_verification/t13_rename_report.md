---
ttl: task_bound
---

# T13 卷宗改名合规 + token 换绑报告

- 会话: st-commitspeed-tbl-20260924（车道 T13）
- 日期: 2026-09-24
- 背景: q-...-0006 战役文档袋死于 gate-naming 门（af8852afa6 S-19 立法：全小写
  snake_case + basename 全局唯一 + 目录名禁大写）。本车道完成卷宗改名合规与
  capability 注册表 token 路径换绑，产出可入队批次材料。**未入队未提交**（待 Max 复核统一投）。

## 一、改名映射（2 目录 + 22 文件，两步走=Windows 大小写不敏感防呆）

| 旧 | 新 | 方式 |
|---|---|---|
| `10_D1_D2/` | `10_d1_d2/` | 两步走 |
| `40_B0_derived_offload/` | `40_b0_derived_offload/` | 两步走 |
| `00_HANDOFF.md` | `00_handoff.md` | 两步走 |
| `00_MASTER_PLAN.md` | `00_commit_speedup_master_plan.md` | 单步（专名避撞） |
| `00_skeleton/S1_stage_inventory.md` | `00_skeleton/s1_stage_inventory.md` | 两步走 |
| `00_skeleton/S2_substage_tree.yaml` | `00_skeleton/s2_substage_tree.yaml` | 两步走 |
| `00_skeleton/S3_gaps_and_blindspots.md` | `00_skeleton/s3_gaps_and_blindspots.md` | 两步走 |
| `10_D1_D2/D1_stats_lock.md` | `10_d1_d2/d1_stats_lock.md` | 两步走 |
| `10_D1_D2/D2_env_flag_leak.md` | `10_d1_d2/d2_env_flag_leak.md` | 两步走 |
| `10_D1_D2/README.md` | `10_d1_d2/d1_d2_readme.md` | 单步（README 专名化） |
| `20_target_arch/A1_conflict_graph.yaml` | `20_target_arch/a1_conflict_graph.yaml` | 两步走 |
| `20_target_arch/A2_target_architecture.md` | `20_target_arch/a2_target_architecture.md` | 两步走 |
| `20_target_arch/A3_gate_repointing_matrix.yaml` | `20_target_arch/a3_gate_repointing_matrix.yaml` | 两步走 |
| `20_target_arch/A4_migration_ladder.md` | `20_target_arch/a4_migration_ladder.md` | 两步走 |
| `20_target_arch/README.md` | `20_target_arch/target_arch_readme.md` | 单步（README 专名化） |
| `30_gate_census/C1_gate_dossier.md` | `30_gate_census/c1_gate_dossier.md` | 两步走 |
| `30_gate_census/P3_integrity_head_derivative_prep.md` | `30_gate_census/p3_integrity_head_derivative_prep.md` | 两步走 |
| `40_B0_derived_offload/B0_1_sync_sites.md` | `40_b0_derived_offload/b0_1_sync_sites.md` | 两步走 |
| `40_B0_derived_offload/B0_2_gate_dependency_matrix.yaml` | `40_b0_derived_offload/b0_2_gate_dependency_matrix.yaml` | 两步走 |
| `40_B0_derived_offload/B0_3_design_and_tests.md` | `40_b0_derived_offload/b0_3_design_and_tests.md` | 两步走 |
| `40_B0_derived_offload/README.md` | `40_b0_derived_offload/b0_readme.md` | 单步（README 专名化） |
| `90_verification/MAX_RULINGS.md` | `90_verification/max_rulings.md` | 两步走 |
| `90_verification/MAX_RULING_QUEUE.md` | `90_verification/max_ruling_queue.md` | 两步走 |
| `90_verification/T1_ledger_readings.md` | `90_verification/t1_ledger_readings.md` | 两步走 |

未动件（已合规）: `90_verification/decisions_log.md`（HEAD 已在档）、
`docs/_working/commitspeed_audit/2026-09-24-commit_wait_investigation_report.md`。

命名要点:
1. master plan 不用 `00_master_plan.md`——git 追踪区已有
   cold_backup_automation/unified_campaign 两处同名（N-16 全局唯一会撞），
   改用 `00_commit_speedup_master_plan.md`（保留 00_ 前缀排序语义）。
2. 3 件 README 按目录语义专名化（d1_d2/target_arch/b0）。
3. `.aidrafts/` 下存在同名拷贝但该目录 git-ignored，不计入 N-16 基准。

## 二、卷宗内部路径引用同步（防 DOC-REF-BROKEN）

17 件文件完成 token 级路径引用替换（含 yaml：s2_substage_tree.yaml、
b0_2_gate_dependency_matrix.yaml）；替换后扫描残留大写名与旧 token 均为零。
内容零变更取证: 对拍暂存区 blob（0006 死批遗留的 A 条目），11 件 byte-exact
（仅路径 token 差异），其余 11 件差异与改名前 git status 的 AM/MM 集合完全
一致（即他车道既有工作区改动 + d1/d2/a2 的纯 CRLF 表象，非本车道引入）。

## 三、token 换绑（scratch worktree: .runtime/tmp/csx_t13_wt，基于 dev=1d2bc6ef85）

- created_by=st-commitspeed-tbl-20260924 条目 20 条: 18 条 file: 路径改写为新名，
  2 条（decisions_log.md、commitspeed_audit 报告）文件名未变无需改写。
- 新增 3 条 token（p3 预制件 / max_ruling_queue / max_rulings），经
  batch_creation_tokens.py 逐文件登记，capability=commit_speedup。
- 施工顺序: 先在 pristine 册上登记 3 条新 token，再做 18 行锚定换绑
  （反向顺序会触发工具"只增不减"写前门卫——file::token 键已变，被判缺条）。
- 验证: git diff numstat = +33/-18（3 个新条目块 + 18 行旧路径 file: 全数改写，
  无任何其他删除）；yaml.safe_load 解析通过；token 条目 23 条（20+3），
  总 creation_tokens 10853 = HEAD 10850 + 3；20 条新路径全部在主区实际存在。

## 四、入队材料

- 清单: `.runtime/tmp/csx_t13_files.txt`（全部改名后文档 + scratch 注册表路径）
- message: `.runtime/tmp/csx_t13_msg.txt`
- scratch: `.runtime/tmp/csx_t13_wt`（保留勿删，注册表从它取）
- 改名脚本: `.runtime/tmp/csx_t13_rename.py`；换绑脚本: `.runtime/tmp/csx_t13_rebind.py`

## 五、遗留

1. 本报告文件自身未登记 creation_token（任务书红线限定注册表只动 20+3 条）——
   入队时 CREATE-GUARD 若拦，需 Max 决定补登第 4 条 token 或走豁免通道。
2. 主区盘上注册表未动（任务书禁改主区册）；注意主区盘上册（10803 条）旧于
   dev HEAD（10850 条），落地侧合并时以 scratch 册为基准做条目级合并，
   禁整册覆盖（EVAP-02 同型风险）。
3. batch_creation_tokens.py 对"改名换绑"场景无原生支持（file::token 键变更被
   判缺条），本次以顺序编排绕开；可作为工具改进候选登记。
4. 主区暂存区仍持有 0006 死批的旧路径 A 条目（本车道禁 git add 未清理）；
   建议走 --enqueue 由 serializer worktree 干净暂存区落地，结构性免疫。
5. scratch 内有为满足登记工具存在性检查而复制的 3 件卷宗副本（untracked），
   属 scratch 一次性内容，不入队、随 scratch 处置。
