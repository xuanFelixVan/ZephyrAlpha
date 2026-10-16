---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-D02
name_zh: 死因三分类甄别
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-D02
---

# D11-D02 死因三分类甄别

## 1. 定义
死信车道第二环节：死因判定。决策问题=「这次死法是环境病、项内病、还是 other？」机制=_DEAD_REASON_ENV_MARKERS/_DEAD_REASON_ITEM_MARKERS 两标记表（含历史补盲批注 0916/0922）+classify_dead_reason 三分类（env/item/other）+dead_letter_prescription 处方映射+make_dead_letter_content_gate 内容级判定门（袋字节→git blob sha 对现值/全史比对，禁按条数估）。

## 2. 六向台账

### 2.1 输入面
- dead 项 dead_reason 串（D01 产物）
- 内容级判据输入：袋 blob sha vs dev 现值/全史（dead-archive --content-level）

### 2.2 输出面
- 三分类标签+处方串（dead_letter_prescription）
- 甄别台账：`.runtime/commit_queue/dead_triage_*.jsonl`（实查 6 份：20260831/20260914/20260919_x1/20260919_x1b/20261014_maint6/20261014_maint7——10-14 新增两份，甄别持续在产）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-D02`（wired/production；machine_facts.deadletter_marker_counts：ENV=23/ITEM=18）
- 标记串条目=叶层进作业簿 08（INV-1 图只挂表位置指针）
- 判定尺：`docs/01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md`（data_refs 在册）

### 2.4 代码模块
- `scripts/commit_queue.py:275` `_DEAD_REASON_ENV_MARKERS`（图记 :240）+`:319` `_DEAD_REASON_ITEM_MARKERS`（图记 :274）+`:4282` `def classify_dead_reason(`（图记 :1709）+`:4333` `def dead_letter_prescription(`+`:3785` `def make_dead_letter_content_gate(`
- 本车道粗扫引号串 ENV 块计 26 条 vs 册面 23——标记表增补后图 machine_facts 未跟（见自审）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=「当日四态分诊不隔夜」（宪法 §2.6）+内容级判定铁律（袋字节→git blob sha 比对，聚合数禁用）

### 2.6 自动化触发
- dead-archive --content-level 批量甄别；处方串随分类自动映射

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | dead_reason 串+内容级判据实存 |
| 输出面 | pass | 6 份甄别台账（含本周两份） |
| SSOT真源 | warn | ENV 标记册面 23 vs 本车道粗扫 26（引号串口径）——标记表增补后图机生计数未刷新，需 AST 口径复核对账 |
| 代码模块 | pass | 五函数实存（行锚漂移大） |
| 门禁约束 | pass | 不隔夜+内容级铁律在案 |
| 自动化触发 | pass | 批量甄别自动 |

## 4. 缺口与建议
- 【计数对账】marker_counts 23/18 与现表差异应随下次地图重生抽平（生成器 AST 读表即刷新）；建议顺带在表头加最后增补日期注释，免再漂。
- 【建议】处方串（dead_letter_prescription）建议与 C02 的 GUIDE 锚点同源化（同一本 playbook 检索），避免两套处方文案漂移。
