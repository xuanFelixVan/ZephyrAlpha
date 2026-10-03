---
ttl: task_bound
completes_when: 图14 立项过 Owner 批（或否决）后转正式施工批文，本卡归档
title: 图14 AI 施工升级流图·立项卡（四道门过审论证）
owner: ZephyrAlpha-Owner
---

# 图14 AI 施工升级流图 立项卡

## 1. 一句话定位

AI 怎么把一个想法变成主区代码：接单→冷启动→挖矿→写码→考试→落地→合并→复盘，15 步闭环的全景图化。

## 2. 四道门过审（裁定#409）

| 门 | 论证 | 判 |
|---|---|---|
| ①独立触发+终点 | 触发=施工任务（TRAE 卡/裁定/Owner 指令）；终点=worktree 合并+全景图状态流转 production。与运行时图（GOMAP 管"系统自己跑"）正交：本图管"AI 改系统" | PASS |
| ②跨模块交接 | 15 步横跨 session_concurrency→capability_lookup→depgraph→门禁链→commit 队列→post-commit reconciler，交接面=claim/token/[GW:]标记/挂轴 | PASS |
| ③不被现有图覆盖 | 图11 交付流水线管"文件怎么落主区"（车道/锁/队列），本图管"任务级工序与验收门"（15 步+每步 gate）。互补不重叠：图11=物流，图14=工艺。GOMAP 管运行时非施工时 | PASS |
| ④机生真源 | 施工清单#17 前置件：步骤锚校验器（见 §3）。SOP 文本=语义层，锚=结构层 | 条件 PASS |

## 3. 前置施工件：步骤锚校验器（schema）

- SOP 真源：construction_workflow_policy.md §3 的 15 步（Step 0-12+小数步）
- 锚 schema：每步一锚 `{step_id, name, gate_refs[], evidence_files[], artifact_dir}`；
- 校验器判据四条：①SOP 步骤标题↔锚一一对应（漂移即红）②每步 gate_refs 非空（除显式 no-gate 步）③evidence_files 路径实存 ④step_id 有序无跳号
- 判据来源=generate_governance_map 的"机生层 vs 生成器重建比对"同款模式

## 4. 图形态

- 纵轴 DAG，节点=15 步锚+每步挂 gate_refs/evidence；MOD 总线挂载（session_concurrency/gov_enforcement/d5_architecture 等域模块）
- 生成器：scripts/governance/d5_architecture/generators/generate_construction_flow_map.py，输入=锚 YAML+SOP 解析
- 与图11 交界显式化：本图 Step 10（GitCommitGateway 落地）节点 ref→图11 提交车道，不复制

## 5. 立项裁定建议

**建议立**：100% AI 项目主航道无图=最大导航缺口；风险=与 SOP 双真源，解法=锚校验器强制同步（SOP 改而锚未跟=红）。
