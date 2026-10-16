---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-D06
name_zh: 死信归档轮换与清零战役
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-D06
---

# D11-D06 死信归档轮换与清零战役

## 1. 定义
死信车道第六环节（车道终点）：终态处置。决策问题=「死信最终去哪？轮换袋与清零战役的处置结论谁留档？」机制=dead/ 永不自动清理不变量→人工搬运进轮换袋（dead_archive_*/dead_purged_*/hold_*，袋名清单以实扫为准）→清零战役三分法处置（superseded/真未落地/历史留档）→结论落 docs/_working 战役记录；dead_archive_letters 机生写 manifest.jsonl 禁手写补录；hold_* 袋出处考古=🌑候选（骨架 §6 点名，图不编造出处）。

## 2. 六向台账

### 2.1 输入面
- dead 积压（378 件实测）+内容级甄别结论（D02）
- 战役授权（Owner 门位：物理不可逆删除类——purged 袋属最高审）

### 2.2 输出面
- 轮换袋 11 只（实查）：dead_archive（根袋）+dead_archive_20261004/06/07/09_deadcure/09_deadcure2/10_deadcure3/13/14 + dead_purged_20260920 + hold_st_gov2 + hold_stress_phaseB_20260923
- 战役记录两篇（实查在盘）：`docs/_archive/_working_cleared/archive/2026-09/c_class_scattered/2026-09-11-commit-queue-dead-zero-closure.md`+`docs/_archive/_working_cleared/archive/2026-09/final3_campaign/p12_queue_terminal_record.md`

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-D06`（wired/production；disposal_trichotomy 三分法在册）
- 骨架：08_死信全链.md §D06+§6 🌑考古候选

### 2.4 代码模块
- `scripts/commit_queue.py:3871` `def dead_archive_letters(`（manifest 机生）+`:4840` `def check_dead_burst(`（死信突发检测）
- CLI：dead-archive 子命令（--days/--no-verify-landed/--content-level/--execute/--session/--json 全参实读）+「与袋绑定清（Owner 2026-10-13 段二）：袋出 dead/ 即失该路引用，blob 转可清」段二语义
- 两篇战役记录+queue 侧机生台账行（qid/verdict/证据 sha）

### 2.5 门禁约束
- 不变量：dead/ 永不自动清理（宁留错不删错）；purged=物理不可逆删除邻域→Owner 门位（宪法 §5）；manifest 禁手写补录（机生唯一）

### 2.6 自动化触发
- 半自动：甄别/manifest/burst 检测自动；袋搬运与战役执行人工批（Owner 门位决定，非缺陷是设计）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 积压+甄别结论+授权面齐 |
| 输出面 | pass | 11 袋+2 战役记录实存（近两周新增 4 袋=战役持续在打） |
| SSOT真源 | pass | 图/骨架/三分法一致 |
| 代码模块 | pass | manifest/burst/CLI 实存 |
| 门禁约束 | pass | 永不清理+Owner 门位+禁手写在案 |
| 自动化触发 | warn | 人工段为主是设计使然，但 hold_* 两袋出处考古（🌑候选）至今未清，挂账未销 |

## 4. 缺口与建议
- 【挂账清销】hold_st_gov2/hold_stress_phaseB_20260923 两 hold 袋出处考古（骨架 §6 🌑候选）建议随下批清零战役一并定谳归档。
- 【行动衔接】dead=378 现量见 C13 行动项：建议直接复用本环节 dead-archive --content-level --execute 通道（机生 manifest+台账行），勿开新工具。
