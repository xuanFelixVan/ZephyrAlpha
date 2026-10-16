---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-05
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-19-方案挖矿施工前先做方案方案先挖矿把矿挖干再施工 + 附录 D 锚块
---

# SD14-05 方案挖矿（policy Step 1.9）

## 1. 定义

任务涉及"建策略/建方案/建设计文档/调研选型"等内容产出时触发（conditional=true）：方案动笔前按六向寻路挖矿（上游/下游/算法机制/后端/前端/数据字段，每向内部反查+全网搜索双动作）→防噪音四闸（来源可溯/交叉验证/A 股适配/可回测）→矿脉枯竭封矿（挖干唯一判据=六向全查无+无未挖长尾）→挖矿日志写进方案→挖后自审闸三态裁定（施工/挂起排期/方案封矿）。先方案后施工，禁止无方案直接施工。新域开工先走 skeleton_mining_policy（骨架先挖根）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 内容产出类任务（mining_sop §1 触发表）；新域开工分支先走骨架挖矿 | `docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` §1；`.../mining_sop/skeleton_mining_policy.md`（两真源本批在盘实证） |
| 输出面 | 含"挖矿增补"章节+"挖后自审"三态裁定的定稿方案（design_memo/施工图 MD）——产出本身是文件，但结构无强制模板约束 | 政策 L246-266；checklist 第 16 项（政策 L809） |
| SSOT 真源 | `mining_sop_policy.md`（通用方法论真源）+`skeleton_mining_policy.md`（骨架前置）+TDM 域专用实例 `trading_decision_map_pathfinding_policy.md` | `docs/01_policies_and_standards/sop/mining_sop/` 三件 |
| 代码模块 | 零 checker（图 evidence：grep "挖矿增补" --include=*.py src scripts → 0 命中；两册 gate 零条目）——执法率 0 是设计后果，可自动化上限=MD 结构断言 | 图 YAML #D14-05 evidence |
| 门禁约束 | 零 gate（gates:[]）；唯一软约束=Step 6 长清单审查按"无方案回炉"（事后兜底）+checklist 第 16 项（人工勾） | 政策 L809；图 YAML #D14-05 |
| 自动化触发 | 无（wiring_status=unwired_no_caller；自环 B3 无轮次常量不入图） | 图 YAML #D14-05 loops B3 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 触发表/前置分支在册可判 |
| 输出面 | warn | 产出=方案文件实存，但挖矿章节/日志无结构 schema，"日志齐全"无机械判据 |
| SSOT 真源 | pass | mining_sop/skeleton_mining/pathfinding 三真源在盘（本批核验） |
| 代码模块 | warn | 零 checker；图已声明升 inspection 路径=结构 checker 落地（建议挂 d9_knowledge 零新目录） |
| 门禁约束 | fail | 判据全仓零执法面（两册 gate 零条目）——checklist 16 项靠自觉 |
| 自动化触发 | fail | unwired_no_caller |

## 4. 缺口与建议

- 缺口1：三条子判据（挖矿增补章节存在/日志表结构/自审三态留痕）零机检。建议：落一个 MD 结构断言 checker（挂 `scripts/governance/d9_knowledge/`），仅验"方案 MD 含挖矿增补章节+三态裁定行"，不验内容——即可把本段从 manual 升 inspection，与图 invalidation 条款预告一致。
- 缺口2：与"挖矿产能咽喉"（FACTORY-E1 想法进货）同名异物——本段是方案挖矿（方法论），FACTORY-E1 是策略想法进货（业务）。建议：术语册登记消歧（terminology_glossary.yaml），防跨图混淆。
- 缺口3：自环 B3（无日志回本步）无轮次上限。建议：政策补"补挖 ≤2 轮升级 Owner 排期"。
