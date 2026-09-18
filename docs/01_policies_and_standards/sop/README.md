---
module_id: SOP-INDEX-001
doc_type: index
ttl: permanent
title: SOP 方法论真源地图（九族文件夹导航）
status: active
version: 1.5.0
owner: ZephyrAlpha-Owner
language: zh
---

# sop/ — 方法论真源地图

> **新 AI 入职第二读**（第一读=仓库根 `AGENTS.md` 冷启动序列）。本目录组织方式：**一个文件夹=一类方法论唯一真源**。接任务先查本表定位该读哪族，勿凭文件名猜测、勿凭记忆背诵——读真源原文。
>
> 2026-09-14 七族重分类：11 个根层散文件归入五族（governance/construction/trading_decision_map/ops/data_audit），mining_sop/ 与 backtest_system_sop/ 两族既有。根层仅留本文件与受保护文件（见下表末行）。

| 文件夹 / 文件 | 一句话功能（归属） | 何时必读 |
|---|---|---|
| `governance_sop/` | **宪法与对齐族**：现行宪法 L0 真源（agent_constitution_l0）+ v1 全文归档 + 全图全库对齐清单（alignment_checklist） | 每次会话冷启动；新建图/库/注册表前；对齐口径争执时 |
| `construction_sop/` | **施工族**：15 步施工闭环真源（construction_workflow_policy）+ 前端拆件 8 步闭环（frontend_component_split_policy）+ 文档七轮审查法（document_review_and_optimization_policy） | 写第一行业务代码/新模块施工前（宪法 RULE-CAPABILITY-LOOKUP 强制）；前端拆组件前；重要文档定稿前 |
| `mining_sop/` | **挖矿研究方法论族**：通用研究方法论真源（mining_sop_policy：六向寻路+防噪音四闸+矿脉枯竭终止+时间盒限流）+ TDM 消费场景寻路政策（trading_decision_map_pathfinding）+ **骨架构建政策（skeleton_mining：域骨架挖掘/四层分层/三问停止判据/状态纪律/封矿判据——新域开工先挖骨架）** | 全网调研/找方案/建策略/写方案类任务开工前（.trae PRE-OP 行强制）；**新域开工/新建骨架类任务开工前** |
| `backtest_system_sop/` | **回测体系族**：四卷——全图编排（sop_a）/节点循环（sop_b）/策略库入库（sop_c）/档案命名（sop_d） | 回测施工、策略入库、run 档案落地前（src/scripts 多处代码锚定此族路径） |
| `data_ops_sop/` | **数据操作族**：回灌/修复/判重/PIT/探针全流程方法论（data_ops_policy：三步验证+幂等回补+FINAL 逐位验证+勿物理删+探针手法+实战范例索引）＋**数据源全生命周期（data_source_onboarding_sop：全网挖矿→候选报批→建表→接入→调度→接通验收三查→消费端路由→退役）** | 数据回灌/坏数据修复/表结构变更/判重/缺口处置开工前；**新数据源接入开工前** |
| `trading_decision_map_sop/` | **TDM 地图族**：逐层讨论六步法（trading_decision_map_layering_policy：四道前置检查防撞车）+消费场景规程（tdm_consumption_policy：S1-S9 九场合——什么场合必须打开地图、读什么、验证什么） | TDM 地图结构讨论、血肉填充、建蓝图锚/策略挂图/回测预检/改判据/引擎变更/退役/复盘/转级 前 |
| `ops_sop/` | **运维协作与应急族**：冲突三分法（merge_conflict_resolution_policy：全项目冲突处理唯一真源）+ worktree 四证清理（worktree_cleanup_policy）+ 保命轨人工 Runbook（emergency_runbook，D-L1~D-L3） | 合并冲突时；清理 worktree 前（四证缺一不可）；系统应急时 |
| `data_audit_sop/` | **数据审计族**：产业链数据审计修复循环（industry_chain_data_audit_policy，配套标准=policies/graph_quality_standard.md） | 图谱数据质量修复、数据审计班次开工前 |
| `review_sop/` | **深度审查族**：代码与算法深度审查六轴法（deep_review_policy：数学正确性四问+上游/下游/旁系传导+红蓝对抗+SOTA 新鲜度+证据纪律+收口闭环）+ 缺陷模式库（defect_pattern_checklist：15 条历史系统性缺陷机械 checklist）+ **规则处置程序法**（rule_disposition_policy：六道闸判定 × 六类归宿，每条规则/每台裁判的唯一判决流程，是前三者与 audit_prompts 的共同下游） | 强模型审查窗口开工前；新算法/管线转 production 验收前；系统性漏洞横向排查（T3）前；**判任何一条规则该留/该改/该退役时** |
| 根下 `audit_prompts_20_ai.md` | **全仓打扫卫生+自主审计治本闭环 v4**：AI-00 总控 + 公共指令（唯一真源）+ AI-01~AI-22 域差异表（含门位优先、能红自证、无主区收编）。文件名保留 `audit_prompts_20_ai` 以稳引用（禁删/禁改名/禁挪路径；只读属性保护，修改走 attrib -r → claim → Gateway 提交 → 复位；旧 `skip-worktree` 声明实测已失效，见文件头） | 发起多模型交叉审计前（design memo 68 的执行蓝本） |

## 使用纪律

1. **族内唯一真源**：每族的方法论问题以该族文件为准；族文件互相引用已同批对齐（2026-09-14 重分类全量路径同步）。
2. **新 SOP 入驻**：新方法论按功能归族入对应文件夹；命名遵循 `*_policy.md`（doc_type=policy 时，N-11 命名闸）；新建文件须登记 creation_token。
3. **发现入口**：本表由 capability 反查（`capability_lookup`）与 `rule_catalog_registry.yaml`（生成器产出）双通道冗余可达；本文件是人为导航层，条目计数勿写死（只述族与功能）。
