---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-04
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-18-架构评审门控判定-4-种变更触发 + 附录 D 锚块
---

# SD14-04 架构评审门控判定（policy Step 1.8）

## 1. 定义

变更类型命中触发清单（新增模块/删除模块/修改模块间接口/更换核心技术栈/修改数据流方向）时触发：6 项清单评审（KB 冲突/循环依赖/可观测性/数据一致性/回滚方案/性能/文档清单）+ L1-L4 架构变更分级（微调/局部/跨层/架构级）+ 治理顺序因果链。评审必须 Owner 亲自执行或书面委托（人门位）；纯内容修改可豁免。通过判据=6 项全 PASS+评审记录落盘。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 变更类型清单命中判定（5 触发项）；Step 1.5 通过 | 政策 L215-243；图 YAML #D14-04 trigger_when |
| 输出面 | 评审记录 MD（政策指认目录 `docs/_working/audit/architecture-reviews/YYYY-MM-DD-变更简述.md` **不在盘**——R-11 实测；archive 侧 `docs/_working/archive/2026-09/audit/architecture-reviews/` 仅 2 条） | 政策 L229（已带 R-11 更正注记）；两目录本批核验：活跃侧不存在、归档侧在 |
| SSOT 真源 | `trae_036_arch_gate_transition.yaml#gov_arch_002`（6 项清单）+ `trae_049_ops_domain_manual.yaml#OPS-DEV-002`（L1-L4 分级）+ `trae_017_arch_governance_order.yaml`（因果链）——三册均在盘，符号命中（图 evidence 实证） | `docs/01_policies_and_standards/rules/` 三件 |
| 代码模块 | 无执行件（module_id/module_ref 双 null）——人门位设计上不可自动化；图 anchor_kind=doc | 图 YAML #D14-04 |
| 门禁约束 | 人门位=Owner（执行或书面委托）；任一否决条件命中→重新设计。注：图节点 human_gate 字段记 null——Owner 门位未在图上结构化登记 | 政策 L233；图 YAML #D14-04 human_gate: null |
| 自动化触发 | 无（wiring_status=unwired_no_caller） | 图 YAML #D14-04 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 触发清单/前置条件在册 |
| 输出面 | fail | 评审记录唯一活跃落点目录不存在（R-11），归档侧仅 2 条历史——输出面断链（broken_supply） |
| SSOT 真源 | pass | 三规则册在盘、符号锚命中（2026-09-25 复跑+本批路径核验） |
| 代码模块 | warn | 零执行件是"人门位不可自动化"的设计后果，非断链；但连辅助面（清单模板/校验器）也无 |
| 门禁约束 | warn | Owner 门位在政策在册，但图 human_gate=null 未结构化——门位账务缺登记 |
| 自动化触发 | fail | unwired_no_caller |

## 4. 缺口与建议

- 缺口1（D14-G12 关联）：政策指认记录目录失效。建议：总包裁定评审记录唯一落点（活跃目录重建 or 正式承认 archive 侧+新路径），裁定前不得升 inspection（invalidation 条款原文）。
- 缺口2：人门位未结构化。建议：按宪法 §5 人机门位，将"架构评审 Owner 门位"登记进 `risk_tier_registry.yaml` 相应域（medium/high tier human_gate），替代散文。
- 缺口3：评审记录自环 B2（否决→重设计→再评审）无轮次常量，按图法不入图。建议：政策补最大重评轮数阈值（如 3 轮升级 Owner 判定），否则可无限循环。
