---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-07
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-3-全图全库对齐七图自动align_all-单命令简称裁定-arch-align-naming-001 + 附录 D 锚块
---

# SD14-07 全图全库对齐（policy Step 3）

## 1. 定义

Step 2 完成后触发：sync_panorama_module 派生其余三图 + align_all 单命令验证多图对齐 + frontend_map 人工核对（涉前端时）。对齐图族张数以 `alignment_checklist.md §3` 为准（政策"七图定义"表为过期散文，图不引）；对齐 key=module_id（前四图）/step_id（battle_map）/feature_id（frontend_map）/node_id（trading_decision_map）。硬阻断=domain_mismatches>0 / ghost_anchors>0。简称裁定 #ARCH-ALIGN-NAMING-001。verified_scope=production（骨架 ✅）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | depgraph planned 节点已登记（D14-06 产物）；对齐键清单 | 政策 L299-330；`docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md#全景图` |
| 输出面 | align_all 通过报告（图 1-5 自动+图 6 校验内嵌）；不通过处置=回 D14-06 修正（回边 B5） | `scripts/governance/d5_architecture/generators/align_all.py`（module_id=MOD-GOV-ALIGN-ALL，在盘实证）；`scripts/governance/sync_panorama_module.py#--all`（在盘） |
| SSOT 真源 | `trae_080_panorama_alignment.yaml#panorama_alignment` + `alignment_checklist.md §3`（图族张数真源） | 两件在盘 |
| 代码模块 | align_all.py + sync_panorama_module.py 双执行体（含 argparse/def main，图 evidence 实证；本批 ls 在盘） | 同输出面 |
| 门禁约束 | `MAP-ALIGNMENT` 聚合台（in_process 在册 1 条+gate_registry 34 处引用，本批实证；聚合 6 子台触发式） | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml` |
| 自动化触发 | apply_depgraph 执行后 sync 默认自动触发；提交期 MAP-ALIGNMENT 聚合台；triple_alignment_on_verified 钩子在任务 VERIFIED 时自动三方对齐（Step 3/8 手动验证仍需） | 政策 L154-155；图 exec_source=gate:MAP-ALIGNMENT |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | D14-06 产物即输入，链条闭合 |
| 输出面 | pass | 通过报告+回边处置条款齐 |
| SSOT 真源 | pass | 图族张数真源已切换 alignment_checklist（政策过期散文已隔离不引） |
| 代码模块 | pass | 双执行体在盘实证 |
| 门禁约束 | pass | MAP-ALIGNMENT 双册在册 |
| 自动化触发 | pass | 三层（sync 自动/聚合台/钩子） |

## 4. 缺口与建议

- 缺口1（WJ-R-09/R-12 关联）：政策正文"七图定义"表与 alignment_checklist 张数口径漂移（图已裁决不引政策表）——建议政策该表加"以 alignment_checklist 为准"前置句，防新 AI 误引（宪法 §4.4 文档矛盾=事故）。
- 缺口2：自环 B6（孤儿/漂移重跑 sync+align）无轮次常量。建议：同 D14-04 补重试上限条款。
- 备注：本段是 17 段中机械化程度最高的段之一（六向全 pass），可作为其他 manual 段升 inspection 的参照样板。
