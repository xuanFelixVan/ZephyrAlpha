---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-02
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-1-文档审查 + 附录 D 锚块
---

# SD14-02 文档审查（policy Step 1）

## 1. 定义

施工 AI 接到任务后第一步：按 AI_review_instructions 12 节指令审查待施工文档完整性/施工算法成熟度/多图对齐情况；按 A-E 改动分类跳过不适用条款。通过判据=12 节全 PASS；产出物=审查结论（政策明文"直接在对话里给出，禁止创建任何报告文件"）。前置条件=Step 0 完成 + 待施工文档 frontmatter status=active。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 待施工文档（frontmatter status=active，draft 回讨论环节）；Step 0 就绪状态 | `docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md` L176-191（Step 1 节）；地图逐层讨论任务加读 `sop/trading_decision_map_sop/trading_decision_map_layering_policy.md` 四道前置检查 |
| 输出面 | 审查结论（对话内）+ GAP 清单（回补则登记 design_memo/ARCH 条目）——**无结构留痕落点**（政策禁创建报告文件） | 同上 L188-189；图 YAML `config/construction_workflow_map.yaml#D14-02`（exec_source=null，red_reason=broken_supply） |
| SSOT 真源 | 政策 Step 1 锚在册；但被指认审查指令真源 `docs/_archive/AI_review_instructions.md` 已 status=deprecated（2026-08-28 Owner 裁定归档不更新）；审查清单实际宿主=本政策附录 A（与 D14-11 同物） | 政策 L181（自述 deprecated）；`docs/_archive/AI_review_instructions.md`（在盘）；政策附录 A L861-1025 |
| 代码模块 | 现行审查机制=68 号审查流水线 `src/zephyr/gov_enforcement/behavioral_admission/code_review_ai.py`（在盘，本批 find 实证）；无与"文档审查"环节的自动接线 | 上述路径实存 |
| 门禁约束 | 零专属 gate（图 YAML gates:[]）；约束全靠政策散文（禁边审边改/先报告→再修复→再自检） | 图 YAML #D14-02 gates 空 |
| 自动化触发 | 无（wiring_status=unwired_no_caller；confidence=untested） | 图 YAML #D14-02 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 前置条件与触发路径在册可循 |
| 输出面 | fail | 审查结论政策明禁留痕文件 ⇒ 结构性无输出落点，验收无从回查 |
| SSOT 真源 | fail | 被指认真源 deprecated，清单宿主实为他段同物（附录 A），双重真源漂移（R-10/WJ-R-03/WJ-R-06） |
| 代码模块 | warn | code_review_ai.py 在盘可作现行机制锚，但政策未把本段接上它（无机检接线） |
| 门禁约束 | warn | 零 gate，全靠人工纪律 |
| 自动化触发 | fail | unwired_no_caller，无任何触发面 |

## 4. 缺口与建议

- 缺口1（结构性，build_status=pending 首因）：审查结论禁留痕 ⇔ 机验面互斥。建议：按本节点 invalidation 条款走裁定——允许 `.runtime/sessions/<sid>/staging/` 会话内留痕（免跟踪+24h TTL），即可升 inspection，不违"禁创建报告文件"原意（该禁令防的是 docs 永久区报告污染）。
- 缺口2：真源指认失效（AI_review_instructions deprecated）。建议：政策 Step 1 改指附录 A 为唯一清单真源，deprecated 件按墓碑制处置。
- 缺口3：与 D14-11 长清单审查的清单同物（附录 A）——两段判据重复登记。建议：净零内收（宪法 §4.2 同真源可派生必并），D14-02 聚焦"施工前文档可施工性"，D14-11 聚焦"施工后产物审查"，清单单源共享。
