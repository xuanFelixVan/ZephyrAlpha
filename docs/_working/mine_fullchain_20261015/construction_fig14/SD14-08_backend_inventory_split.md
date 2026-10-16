---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-08
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-35-后端盘点与拆件判定前端施工前置 + 附录 D 锚块
---

# SD14-08 后端盘点与拆件判定（policy Step 3.5）

## 1. 定义

前端页面新建/改造/加数据区块时触发（conditional=true，Owner 2026-09-04 立规）：取数清单→后端三查+前端一查（api_server 端点/data_asset_registry/其他服务端点+depgraph/frontend_map 查重）→三分支决策（有且唯一→消费/有重复→先治后端/没有→先建后端）→拆件判定（四判据，真源=TRAE-086 §split_judgment）→有得拆转拆件 SOP 8 步闭环（子流程 B7 出图）/没得拆进 Step 4。通过判据=每条数据需求唯一后端真源且前端已接线+判定结论留痕。wiring=unwired_slot_hollow（slot 在链但空心）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 前端数据需求清单（字段/粒度/刷新节奏）；`web/frontend_map.yaml` 查重输入——**政策路径幽灵** | 政策 L333-358；真身两份=`architecture_model/frontend/frontend_map.yaml`（71738B）+`src/zephyr/frontend/dashboard/web/frontend_map.yaml`（116421B，本批 wc -c 实证，差值较图证据时点 113652B 扩大——双真源漂移在恶化） |
| 输出面 | 盘点结论+拆件判定留痕（进设计备忘或验收单 ACC-*.yaml）——ACC-* 69 张实测无读方（图 evidence） | `docs/01_policies_and_standards/sop/construction_sop/frontend_component_split_policy.md`（拆件 8 步闭环真源）；`.runtime/gate_audit/frontend_truth_source.jsonl`（warn 审计面） |
| SSOT 真源 | `trae_086_frontend_module_construction.yaml#truth_source_wiring+#split_judgment`（铁律+判据单源）+alignment_checklist §3+`data_asset_registry.yaml` | `docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml` 等 |
| 代码模块 | `scripts/governance/d5_architecture/generators/check_frontend_map.py`（module_ref）+`src/zephyr/gov_enforcement/commit_gates/frontend_truth_source_gate.py`（`_HARD_BLOCK=False` L83 本批实证——warn-only 起步） | 两件在盘 |
| 门禁约束 | `FRONTEND-TRUTH-SOURCE`（in_process 在册，warn 兜底）+`FRONTEND-MAP`（gate_registry 在册 137）；阻断位关闭=有台不等于有门禁 | 两册 grep 实证；gate 件头注释 L8/L42 |
| 自动化触发 | 提交期 gate warn+审计落盘；硬阻断升级路径=`_HARD_BLOCK=True` 一行（待 Owner 门位） | gate 件 L83 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 触发条件/四查清单在册 |
| 输出面 | warn | 判定留痕两宿主（设计备忘已归档/ACC-* 无读方）——留痕面弱化 |
| SSOT 真源 | fail | 前端真源图三份不一（政策路径幽灵+双真源字节不同且差距扩大）——查重判据的输入本体不可信（D14-G09，X-13 待裁） |
| 代码模块 | pass | 校验器+gate 件在盘，阻断位状态实证 |
| 门禁约束 | warn | 台子在册但 `_HARD_BLOCK=False`——warn-only 有审计无阻断 |
| 自动化触发 | warn | unwired_slot_hollow：gate 在链但空心（不阻断） |

## 4. 缺口与建议

- 缺口1（D14-G09，X-13 待裁）：前端真源图唯一宿主待 Owner 裁定；收敛前本段禁升 automated（invalidation 条款原文）。建议：裁定 `src/zephyr/frontend/dashboard/web/frontend_map.yaml`（贴代码侧）为唯一真源、architecture_model 侧转派生或退役；先 byte-diff 定漂移方向再动。
- 缺口2：FRONTEND-TRUTH-SOURCE 阻断位关闭是"先跑 warn 收集误报率"的既定路线（gate 件 L42）——建议设复核时点，误报率达标即翻硬，勿无限期 warn。
- 缺口3：ACC-*.yaml 69 张无读方——按内收判据 w5_1（零触发零消费→退役）评估：或给读方（验收门消费）或归档退役。
