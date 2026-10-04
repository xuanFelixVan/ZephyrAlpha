---
ttl: task_bound
session: st-f6-census-20261003
date: 2026-10-03
title: F6 覆盖账本三红对账+基线复核 终报
completes_when: 总筹消费两件产出（三红处置+regen 漂移清单）后转归档
---

# F6 终报（sid=st-f6-census-20261003）

> 冷启动：Python 3.12.8 ✓ / setup_dev_env --check ✓ / cleanup CLEAN（顺手回收 st-c10-inv、st-c10-t0gpu 两死会话遗属，常规动作）/ reaper 存活（last_run=2026-10-03 23:07:27）。前置 F5 五件齐（3434 行）✅。
> 红线执行：输入源全部纯读零改写；零 git commit 零 git add；三件产出写前逐件 claim 成功；骨架 §7 全套实查零触发排空变体（命令 1 走 health --no-alert）。

## §1 产出清单（docs/_working/commitmap_cure/）

| 文件 | 内容 | 行数 |
|------|------|------|
| f6_coverage_reds.md | 三红逐项 PASS/RED+证据行 | 见下 |
| f6_baseline_verify.md | §7 命令 0-10 全套 vs counts（2026-09-30 版）逐项对照+同源口径复算+漂移清单 | 见下 |
| f6_report.md | 本终报 | — |

## §2 红名单汇总表

| 红 | 结论 | 明细 |
|----|------|------|
| 红1 孤儿=该挂没挂 | **RED×3（全部为预期内已裁定红）+ 其余 PASS** | E∪=185 vs f5=182，缺=CONSTITUTION-LINE-LIMIT / REAL-KEY-REFERENCE-SCAN / TASK-ORDER-DOCS-LOCK（三台=in_process 册独有活门禁；总筹2026-10-03已裁定：随chief手术批「门禁身份一本账」收敛补挂——照实标红，勿修勿扩勿自行贴标签）；幽灵 0；五本病历本全部在挂（DCS14/AP19/SV8/RV1 8/RV2 6/MEM28）；G01/G02 显式注记豁免在 |
| 红2 抄写=复制非引用 | **PASS** | 门禁正文/病历正文/明细行三类长行规范化检索：0 真命中；2 处机械假阳性（两台 description≡gate id 字面串，id 指针属 INV-1 许可）留证在产出一件 |
| 红3 未挂病历 | **PASS** | 每本 ≥1 环节（AP19/DCS14/MEM28/RV1 8/RV2 6/SV8），28 环节无零病历 |

预期核对：实际红名单与任务书预期（红1 三台已知红+其余 PASS）**逐台相符**。

## §3 基线漂移汇总（8 项，供总筹 regen，勿自行 regen）

1. queue done 718→507（−211）
2. queue dead 689→1254（+565）
3. in_process 册 total_gates 104→105（+1）
4. shell 册 total_gates 178→182（+4）
5. shell cluster_by_channel 重新分簇（commit-gate 93/manual 39/pre-commit 49/新通道 commit-gateway×1）
6. shell own_scope_true 57→55（−2）
7. shell files_trigger 68→67（−1）
8. deadletter ENV 标记 18→23（+5）

一致项：reconciler 58=58、claims_scanned 8063=8063、骨架三态 28/26✅/2🔨、图本体顶层 counts 全自洽、ITEM 标记 18=18、队列 pending/processing 两态、in_process own_scope/files_trigger。附两笔 ℹ️：命令 9 的 hold_* 出处在后续台账已有记载（骨架 §6🌑-3 表述可更新）；近 3 日 dev [GW: 666/q-2026 130（无基线可比，记录）。

## §4 异常与注记

1. 全程零门拦截零异常。
2. 盘面注记：F5 班曾出现「写即add」自动暂存（其终报 §3-9 已呈报）；本班写后实测三件均为未跟踪（`??`）态，该机制本轮未触发。本班全程零 git add 零 git commit。
3. CREATE-GUARD token（若 chief 落地批需要）：`commitmap_cure_f6_coverage_reds` / `commitmap_cure_f6_baseline_verify` / `commitmap_cure_f6_report`（纯 ASCII，F1-F5 同模式随批登记）。
4. 降级直改登记原因：机械对账新产出文件、无既有文件改写、随 chief 批落地（F1-F5 同模式）。

[no-lookup: 纯对账复核无新业务代码]

本车道未做任何判定，全部判定权归总筹。
