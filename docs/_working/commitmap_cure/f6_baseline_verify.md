---
ttl: task_bound
session: st-f6-census-20261003
date: 2026-10-03
title: F6 图11 基线复核包（骨架 §7 实查命令 0-10 全套 vs dev_delivery_map counts 2026-09-30 版）
completes_when: 总筹 regen 消费漂移清单并重新生成后转归档
---

# F6 图11 基线复核包

> 基线：config/dev_delivery_map.yaml 内嵌 counts（generated_at=**2026-09-30T08:30:35+08:00**，schema 0.2）。
> 实测：2026-10-03 23:10-23:20 本车道只读复跑；命令 1 走 `commit_queue.py health --no-alert`（status/触发排空变体零执行）；重算子项全部按生成器同源口径（`scan_gate_registry`/`scan_module_id_index`/AST Tuple，源=generate_dev_delivery_map.py + validate_construction_steps.py 逐字读）。

## §1 命令 0-10 逐项

| # | 命令（§7 原文） | 实测输出 | 基线 counts | 判定 |
|---|----------------|---------|------------|------|
| 0 | RULE-ENV 环境 | Python 3.12.8 | — | ✅ 可执行 |
| 1 | `commit_queue.py health --no-alert` + 四目录 ls + 最新 done | pending **1** / processing **1** / done **507**（health 口径）/ dead **1254**（health 口径；ls 目录条目=1257，差 3=非条目项）/ blobs **11576**；最新 done=`q-20261003-st-tdm-mount-flash-20261003-0003.json` | queue_state_dirs: pending 1 / processing 1 / done 718 / dead 689 | done ⚠️ / dead ⚠️ / pending ✅ / processing ✅（blobs 无基线，ℹ️ 记录） |
| 2 | 近 3 日 dev 活性 grep | `[GW:` **666** 条 / `q-2026` **130** 条 | counts 无此项（骨架 §1 旧证据 1242/283=2026-09-24 口径） | ℹ️ 记录 |
| 3 | 单写者断言 docstring | 「断言 dev 历史只经 Serializer 通道落盘（全部 commit 带 [GW:{sid}:{qid}] 队列标记）。」 | — | ✅ 机制在位 |
| 4 | flags.yaml 开关面 | 五键全在：commit_queue_serializer:94 / gate_result_cache:99 / gate_preflight:104 / gate_precommit_run:109 / commit_queue_interactive:114，**全部 enabled:true** | — | ✅（与骨架门④记载一致） |
| 5 | 两册 total_gates | in_process **105** / shell **182** | in_process_gate_facts.total_gates_field **104** / shell_gate_facts.total_gates_field **178** | 双册 ⚠️（+1 / +4） |
| 6 | reconciler 注册数 | **58** | reconciler_register_calls **58** | ✅ |
| 7 | 会话车道活性 | session_registry sessions=**10**；handoffs 非空（handoff_A/B.json 等） | — | ✅ 活性在 |
| 8 | 死信复活活链抽查 | 样例 q-20260922-…-0031 在盘：dead_reason=COMMIT_FAILED(TRANSLATION-COVERAGE 阻断)、requeued→q-20260923-…-0055 | — | ✅ 活链完好 |
| 9 | hold_* 出处考古 | 两目录仍在盘；今日 grep **有命中**（docs/_working/cleanup_final/cleanup_ledger.md:26、docs/_working/cmd_ledger/automation_master_plan.md:63/:127 有台账记载） | — | ℹ️ 骨架 §6🌑-3「全仓 grep 无出处」表述已被后续台账记录覆盖，供 regen 更新该🌑项 |
| 10 | GOMAP 排除面原文 | out_of_scope_refs 四行与骨架 §0 门③引文逐字一致 | — | ✅ |

## §2 counts.machine 子项同源口径复算

| 子项 | 实测 | 基线(09-30) | 判定 |
|------|------|------------|------|
| reconciler_register_calls | 58 | 58 | ✅ |
| in_process total_gates_field / entries | 105 / 105 | 104 / 104 | ⚠️ +1 |
| in_process cluster_by_channel | unspecified 105 | unspecified 104 | ⚠️ 随总数 |
| in_process own_scope_true_entries | 0 | 0 | ✅ |
| in_process files_trigger_entries | 25 | 25 | ✅ |
| shell total_gates_field / entries | 182 / 182 | 178 / 178 | ⚠️ +4 |
| shell cluster_by_channel | commit-gate **93** / manual **39** / pre-commit **49** / **commit-gateway 1（新通道名）** | commit-gate 99 / manual 28 / pre-commit 51 | ⚠️ 重新分簇+新通道 |
| shell own_scope_true_entries | 55 | 57 | ⚠️ −2 |
| shell files_trigger_entries | 67 | 68 | ⚠️ −1 |
| queue_state_dirs 四态 | 1 / 1 / 507 / 1254 | 1 / 1 / 718 / 689 | done ⚠️ −211 / dead ⚠️ +565（前两态 ✅） |
| deadletter ENV 标记（AST Tuple 口径） | **23** | 18 | ⚠️ +5 |
| deadletter ITEM 标记（AST Tuple 口径） | 18 | 18 | ✅ |
| skeleton_status_scan | 28 节点 ✅26 🔨2 | 同 | ✅ |
| module_id claims_scanned | **8063**（ownership 8095 行、depgraph_node 8095、按 path 去重 8063） | 8063 | ✅ |
| nodes_with_module_id / module_ref / null | 28 / 28 / 2 | 28 / 28 / 2 | ✅ |
| counts 顶层自洽（total_nodes 30 / total_edges 31 / by_lane S9-C15-D6 / gap2-stage28 / production26-structure4 / wired22-partial4-unwired_no_caller2-unwired_slot_hollow2） | 逐项相等 | 同 | ✅（图本体自生成以来未变） |

## §3 漂移清单（供总筹 regen，勿自行 regen）

1. queue done 718→**507**（−211）
2. queue dead 689→**1254**（+565；health 条目口径，ls 目录条目 1257）
3. in_process 册 total_gates 104→**105**（+1 台；与 F5/F6 孤儿三台同册面演变相关）
4. shell 册 total_gates 178→**182**（+4 台）
5. shell cluster_by_channel 重新分簇：commit-gate 99→93 / manual 28→39 / pre-commit 51→49 / 新增 **commit-gateway×1** 通道名
6. shell own_scope_true 57→**55**（−2）
7. shell files_trigger 68→**67**（−1）
8. deadletter ENV 标记 18→**23**（+5，含历史补盲批注模式的标记表增长）

机械观察（非判定，供 regen 备注参考）：done 下降方向与 done TTL 7 天轮换语义一致（queue cleanup 不变量「dead 永不清理」不变，dead 净增）；两册门禁净增与 09-30→10-03 战役批内登记活动同窗。

——实测脚本=`.runtime/tmp/f5_mountdata_20261003/f6_baseline.py` + `f6_baseline2.py`（全部只读）；regen 决定权归总筹。
