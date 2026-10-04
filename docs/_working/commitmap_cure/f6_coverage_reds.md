---
ttl: task_bound
session: st-f6-census-20261003
date: 2026-10-03
title: F6 覆盖账本三红对账（红1 孤儿 / 红2 抄写 / 红3 未挂病历）
completes_when: 总筹复核采纳并随上户口批落地后转归档
---

# F6 覆盖账本三红对账

> 车道：机械对账零判定 · sid=st-f6-census-20261003 · 2026-10-03。
> 对象：F5 四件产出（f5_purpose_tags.yaml / f5_casebooks_mount.yaml / f5_trigger_facts.yaml / f5_consumers_agg.yaml）。
> 真源：门禁两册读 total_gates 字段（今日实值 in_process=**105** / shell=**182**，勿背数）；病历五本=f4_casebook_mount_plan.md §0 总表。

## 红1 孤儿=该挂没挂 —— RED×3（预期内，已裁定）+ 其余 PASS

**门禁腿**：两册 gate id 并集 **185**（in_process 105 + shell 182 − 两册交集 102）vs f5_purpose_tags.yaml gates 节 **182** 台。

| 检查 | 结果 |
|------|------|
| E∪ − f5（缺=孤儿） | **3 台**：`CONSTITUTION-LINE-LIMIT` / `REAL-KEY-REFERENCE-SCAN` / `TASK-ORDER-DOCS-LOCK` |
| f5 − E∪（幽灵） | **0 台** ✅ |
| 覆盖数 | 182/185（其余全部在挂）✅ |

- **RED 台逐条**（照实标红，勿修勿扩勿自行贴标签）：
  - `CONSTITUTION-LINE-LIMIT` — **RED** — 总筹2026-10-03已裁定：随chief手术批「门禁身份一本账」收敛补挂（in_process 册独有活门禁）
  - `REAL-KEY-REFERENCE-SCAN` — **RED** — 总筹2026-10-03已裁定：随chief手术批「门禁身份一本账」收敛补挂（in_process 册独有活门禁）
  - `TASK-ORDER-DOCS-LOCK` — **RED** — 总筹2026-10-03已裁定：随chief手术批「门禁身份一本账」收敛补挂（in_process 册独有活门禁）
- 三台与 F5 终报 T2 孤儿名单逐台相等（机械复核 expected_red_match=true）。

**病历本腿**：五本（F4 §0 总表身份）全部出现在 f5_casebooks_mount.yaml nodes 节：

| 病历本 | 册码 | 挂载环节数 | 样例节点 |
|--------|------|-----------|---------|
| death_cases_registry（module_id=CFG-COMMIT-DEATH-CASES-001） | DCS | 14 | C02/C05/C07/D01/D02/D04… |
| all_problems_ledger | AP | 19 | S01-S08/C01/C03/C05/C07/C08/C09/C10/C13/D01/D03/D06 |
| dead_letter_salvage_ledger_20261003 | SV | 8 | C08/C13/D01-D06 |
| review_findings 卷一 | RV1 | 8 | S04/S08/C05/C07/C10/C11/C13/D06 |
| review_findings_round2 卷二 | RV2 | 6 | S01/S02/S03/S08/C11/C13 |
| MEMORY.md 记忆教训索引 | MEM | 28 | 28 环节全覆盖 |

五本全部 ≥1 ✅（第五本行内含两卷，RV1/RV2 分别复算）。

**G01/G02 豁免腿**：f5_casebooks_mount.yaml unmounted_note 节含 D11-G01/D11-G02 显式注记（note_verbatim=「gap 节点 G01/G02 不挂（骨架外缺口件无运行代码可挂，其病历由 C07/C13 同章覆盖）。」逐字）→ **只认显式注记豁免，本件注记在，PASS** ✅。

## 红2 抄写=复制非引用 —— PASS（2 处机械假阳性留证）

**方法**：三类禁抄正文（门禁条目正文 / 病历条目正文 / 消费者明细行）长行规范化（去空白，≥30 字）后对 f5 四件全文做逐字子串检索；明细行另做整行（gate,path,category）逐行检索。

| 源 | 扫描量 | 命中 |
|----|--------|------|
| 门禁正文（两册 description/name_zh 等长文本字段） | 105+182 条 | 2 处，均为**机械假阳性**：`DERIVED-FILE-DELETION-PROTECTION` 与 `NO-DOMAIN-NAME-ZH-DIRECT-ACCESS` 两台的 description 字段即 gate id 字面串本身，命中文本≡gate id——id/名字指针属任务书 INV-1 明文许可（「只许计数、名字、册#章码、路径指针」），非正文抄写 |
| 病历条目正文（五本长行） | 5 册全文 | **0 命中** ✅ |
| 消费者明细行（f3_consumer_detail.csv 25717 行整行） | 25717 行 | **0 命中** ✅ |

**范围注记**：f5_purpose_tags 的 labels 一句话（指令=逐字抄 00_design_basis §1）与 f5_casebooks 的矩阵原胞/不挂注记（指令=逐字取 §1/§0）为 F5 任务书指令的逐字抄录层，属目的标签/挂载指针，不属三类禁抄正文。

**结论**：f5 四件无超 1 行正文复制 → **PASS**。

## 红3 未挂病历（完备性铁律复算） —— PASS

每本永久病历本挂载环节数复算（口径=「册码#」在矩阵原胞出现即计）：AP **19** / DCS **14** / MEM **28** / RV1 **8** / RV2 **6** / SV **8**——全部 ≥1 ✅；28 个环节节点全部 ≥1 本病历（无零病历环节）✅。

> 附注（只列不平）：本复算数与 F4 §4 自报数（13/14/9/14 两卷/30）存在差异，F5 终报 §3-2 已列明（§1=任务书指定唯一真源），本件不裁定。

——证据生成脚本=`.runtime/tmp/f5_mountdata_20261003/f6_reds.py`（只读）；三红判定权归总筹。
