---
ttl: task_bound
date: 2026-08-04
author: Agent (执行 kimi3_battle_map_merge_instructions.md)
---

# 作战地图合并映射表

> 11个草稿的H3分类（自动分类+待人工审核）
> 总计 993 H3 | 能挂=501 排除=225 待定=267


## 00-架构图总览与索引.md (12 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L11 | §1 架构图全景 | §1.1 9+1 架构图总表 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 2 | L28 | §1 架构图全景 | §1.2 架构图之间的关系 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 3 | L72 | §1 架构图全景 | §1.3 架构图依赖与构建顺序 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 4 | L106 | §1 架构图全景 | §1.4 门禁架构图：A6 合规架构 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 5 | L140 | §2 每个架构图的边界定义 | §2.1 边界矩阵 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 6 | L155 | §2 每个架构图的边界定义 | §2.2 交叉引用规则 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 7 | L166 | §2 每个架构图的边界定义 | §2.3 各架构图的核心内容与排除内容 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 8 | L346 | §3 架构图与能力定位书的关系 | §3.1 能力定位书的定位 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 9 | L358 | §3 架构图与能力定位书的关系 | §3.2 引用规则 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 10 | L370 | §4 架构图与功能域的关系 | §4.1 层级关系 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 11 | L388 | §4 架构图与功能域的关系 | §4.2 架构图对功能域的约束 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |
| 12 | L409 | §5 架构图间交叉引用索引 | §5.1 已知交叉引用 |  |  | 否 | 排除 | 禁域/元文档(00-架构图总览与索引.md不挂作战地图) |

## Agent架构.md (84 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L16 |  | 📌 文档边界声明 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 2 | L32 | §0 架构定位 | §0.1 Agent架构在全局架构中的位置 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 3 | L48 | §0 架构定位 | §0.2 与其他架构图的关系 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 4 | L64 | §0 架构定位 | §0.3 Agent架构（唯一真源） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 5 | L180 | §0 架构定位 | §0.4 Agent协作流全景图（研究→信号→风控→执行→反思→记忆更新） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 6 | L356 | §1 Agent分层指挥链 | §1.1 三层指挥链架构图 | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 7 | L411 | §1 Agent分层指挥链 | §1.2 战略Agent | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 8 | L425 | §1 Agent分层指挥链 | §1.3 战术Agent | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 9 | L439 | §1 Agent分层指挥链 | §1.4 执行Agent | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 10 | L455 | §1 Agent分层指挥链 | §1.5 跨层交互规则 | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 11 | L485 | §1 Agent分层指挥链 | §1.6 与TiMi/Hi-DARTS/TAQUANT/ContestTrade/AGENTICAI | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 12 | L499 | §1 Agent分层指挥链 | 决策树与强化学习交易决策架构（Decision Tree & RL Trading Decision | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 13 | L547 | §1 Agent分层指挥链 | 动态信号权重模型（Dynamic Signal Weighting via Bayesian Mod | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 14 | L603 | §2 Agent能力矩阵 | §2.1 能力注册（Agent Card格式） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 15 | L691 | §2 Agent能力矩阵 | §2.2 能力边界 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 16 | L709 | §2 Agent能力矩阵 | §2.3 能力演进路径 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 17 | L750 | §3 Agent间通信协议 | §3.1 A2A检查协议（单机适配版） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 18 | L794 | §3 Agent间通信协议 | §3.2 消息格式（JSON-RPC 2.0 + A2A Task/Message/Part） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 19 | L888 | §3 Agent间通信协议 | §3.3 超时与重试 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 20 | L921 | §3 Agent间通信协议 | §3.4 通信安全 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 21 | L931 | §3 Agent间通信协议 | §3.5 Agent错误恢复与优雅降级 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 22 | L991 | §3 Agent间通信协议 | §3.6 A2A检查网关策略引擎 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 23 | L1045 | §3 Agent间通信协议 | §3.7 多智能体编排框架选型（A1§29.27迁移） | D_ORCHESTRATOR | buy_flow | 部分 | 仅调用点锚点 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow）；本节属调用点范围 |
| 24 | L1150 | §4 Agent自治边界 | §4.1 四级自治模型 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 25 | L1166 | §4 Agent自治边界 | §4.2 ai_modifiable（自治区：Agent可自主修改的范围） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 26 | L1182 | §4 Agent自治边界 | §4.3 human_gated（门控区：需人工审批的范围） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 27 | L1198 | §4 Agent自治边界 | §4.4 immutable（禁区：绝对不可变的范围） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 28 | L1213 | §4 Agent自治边界 | §4.5 自治边界变更流程 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 29 | L1234 | §4 Agent自治边界 | §4.6 人在闭环（HITL）机制 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 30 | L1295 | §5 Agent冷启动与技能注册 | §5.1 冷启动流程 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 31 | L1320 | §5 Agent冷启动与技能注册 | §5.2 技能注册（SKILL.md格式） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 32 | L1390 | Execution (references/scripts) | §5.3 技能发现与匹配 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 33 | L1399 | Execution (references/scripts) | §5.4 技能版本管理与退役 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 34 | L1408 | Execution (references/scripts) | §5.5 Agent版本管理策略 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 35 | L1446 | §6 自反Agent（Reflexion） | §6.1 自反架构（Actor-Evaluator-SelfReflection三组件） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 36 | L1486 | §6 自反Agent（Reflexion） | §6.2 多级反思（参考SAMULE三级反思） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 37 | L1519 | §6 自反Agent（Reflexion） | §6.3 前瞻反思（参考PreFlect） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 38 | L1539 | §6 自反Agent（Reflexion） | §6.4 实时轨迹内反思（参考Agent-R） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 39 | L1560 | §6 自反Agent（Reflexion） | §6.5 反思频率控制（参考ReflCtrl） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 40 | L1580 | §6 自反Agent（Reflexion） | §6.6 策略自我修正闭环 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 41 | L1615 | §6 自反Agent（Reflexion） | §6.7 与学习系统架构(A8)的接口 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 42 | L1630 | §7 Agent记忆架构 | §7.1 四层记忆模型 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 43 | L1652 | §7 Agent记忆架构 | §7.2 各层记忆规格 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 44 | L1661 | §7 Agent记忆架构 | §7.3 记忆巩固与遗忘 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 45 | L1685 | §7 Agent记忆架构 | §7.4 记忆与自反Agent的集成 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 46 | L1696 | §7 Agent记忆架构 | §7.5 记忆安全约束 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 47 | L1712 | §8 LLM Agent路由 | §8.1 路由架构（级联控制器） |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 48 | L1760 | §8 LLM Agent路由 | §8.2 本地/API分时分任务路由策略 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 49 | L1803 | §8 LLM Agent路由 | §8.3 成本控制 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 50 | L1835 | §8 LLM Agent路由 | §8.4 路由评估与优化 |  |  | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 51 | L1881 | §9 功能域映射 | §9.1 功能域清单 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 52 | L1901 | §9 功能域映射 | §9.2 架构组件→功能域映射 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 53 | L2054 | §13 成功指标 | §13.1 多Agent协作评估维度（参考MASEval/MultiAgentBench） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 54 | L2066 | §13 成功指标 | §13.2 生产级Agent关键指标（参考行业实践） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 55 | L2099 | §15 Agent可观测性 | §15.1 可观测性三支柱 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 56 | L2109 | §15 Agent可观测性 | §15.2 Trace层级模型 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 57 | L2131 | §15 Agent可观测性 | §15.3 治理感知遥测（GAAT适配） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 58 | L2151 | §15 Agent可观测性 | §15.4 关键可观测性指标 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 59 | L2163 | §15 Agent可观测性 | §15.5 可观测性安全约束 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 60 | L2179 | §16 Agent测试与混沌工程 | §16.1 测试层级模型 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 61 | L2189 | §16 Agent测试与混沌工程 | §16.2 混沌工程实验库 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 62 | L2206 | §16 Agent测试与混沌工程 | §16.3 行为模式测试（参考MASTest） | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 63 | L2216 | §16 Agent测试与混沌工程 | §16.4 测试自动化与CI/CD集成 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 64 | L2257 | §17 遗留问题裁定 | §17.1 LP-001 OPA Rego策略引擎 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 65 | L2269 | §17 遗留问题裁定 | §17.2 LP-002 Agent记忆向量检索(RAG) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 66 | L2281 | §17 遗留问题裁定 | §17.3 LP-003 串谋检测阈值 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 67 | L2293 | §17 遗留问题裁定 | §17.4 LP-004 影子模式测试 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 68 | L2305 | §17 遗留问题裁定 | §17.5 LP-005 EU AI Act正式合规文档 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 69 | L2317 | §17 遗留问题裁定 | §17.6 LP-006 混沌工程环境 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 70 | L2329 | §17 遗留问题裁定 | §17.7 LP-007 11个Agent分阶段上线 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 71 | L2347 | §17 遗留问题裁定 | §17.8 LP-008 本地LLM选型 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 72 | L2360 | §17 遗留问题裁定 | §17.9 LP-009 前瞻反思(PreFlect) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 73 | L2370 | §17 遗留问题裁定 | §17.10 LP-010 Agent密码学身份(DID+Ed25519) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 74 | L2380 | §17 遗留问题裁定 | §17.11 LP-011 内部竞赛机制(ContestTrade) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 75 | L2390 | §17 遗留问题裁定 | §17.12 LP-012 记忆图数据库(Neo4j/Graphiti) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 76 | L2400 | §17 遗留问题裁定 | §17.13 LP-013 Agent SRE正式SLO | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 77 | L2410 | §17 遗留问题裁定 | §17.14 LP-014 MCP×A2A集成框架 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 78 | L2420 | §17 遗留问题裁定 | §17.15 LP-015 Agent 365 OTel企业级管道 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 79 | L2430 | §17 遗留问题裁定 | §17.16 LP-016 NeMo Guardrails IORails并行护栏 | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 80 | L2440 | §17 遗留问题裁定 | §17.17 LP-017 另类数据域(D-ALT-DATA) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 81 | L2450 | §17 遗留问题裁定 | §17.18 LP-018 跨资产跨市场域(D-CROSS-ASSET) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 82 | L2460 | §17 遗留问题裁定 | §17.19 LP-019 合规监管域(D-COMPLIANCE) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 83 | L2470 | §17 遗留问题裁定 | §17.20 LP-020 交易运营域(D-TRADING) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |
| 84 | L2480 | §17 遗留问题裁定 | §17.21 LP-021 前端域(D-FRONTEND) | D_ORCHESTRATOR | buy_flow | 否 | 排除 | Agent主体不挂（仅D_ORCHESTRATOR调用点已挂buy_flow） |

## 交易决策架构.md (271 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L16 |  | 📌 🆕标记版本归属规则 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 2 | L24 |  | 📌 文档边界声明（契约式桥接） |  |  | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 3 | L44 |  | 📌 §0 架构定位 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 4 | L94 | §1 总体流水线架构 | §1.1 交易决策架构（唯一真源） |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 5 | L960 | §1 总体流水线架构 | §1.2 选股注解 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 6 | L966 | §1 总体流水线架构 | §1.3 买入注解 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 7 | L1007 | §1 总体流水线架构 | §1.4 卖出注解 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 8 | L1063 | §1 总体流水线架构 | §1.5 仓位注解 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 9 | L1069 | §1 总体流水线架构 | §1.6 支撑注解 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 10 | L1075 | §1 总体流水线架构 | §1.7 分布感知注解 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 11 | L1156 | §1 总体流水线架构 | §1.8 数据流主动脉与正向闭环 |  |  | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 12 | L1214 | §1 总体流水线架构 | §1.9 与v0.1的关键差异 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 13 | L1248 | §2 L0 数据接入与预处理层 | §2.1 多源数据接入与分层存储架构 | D_DATA/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-BT-02-B) | 与现有环节 BM-BT-02-B 多源数据接入 等价/被其包含(sim=1.00) |
| 14 | L1301 | §2 L0 数据接入与预处理层 | §2.2 事件总线事件分类 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 15 | L1312 | §2 L0 数据接入与预处理层 | §2.3 iFind QPS分配策略（C-022/C-044协同） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-20) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 16 | L1328 | §3 L1 因子计算层 | §3.1 因子工厂与生产线的职责边界 | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 17 | L1344 | §3 L1 因子计算层 | §3.2 双模运行机制 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BT-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 18 | L1353 | §3 L1 因子计算层 | §3.3 因子池管理 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 19 | L1366 | §3 L1 因子计算层 | §3.4 因子分类与数据源映射 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-11) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 20 | L1379 | §3 L1 因子计算层 | §3.5 🆕分布特征工程（密度预测的因子侧支撑） | D_FACTOR | stock_selection | 是 | 已覆盖(BM-SEL-12) | 与现有环节 BM-SEL-12 分布特征工程 等价/被其包含(sim=1.00) |
| 21 | L1409 | §3 L1 因子计算层 | 模块1 多维度情绪合成指数模型（Multi-Dimensional Sentiment Compos | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 22 | L1465 | §3 L1 因子计算层 | 模块2 波动率体制转换与关键时点预警模型（Volatility Regime Transition | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 23 | L1515 | §3 L1 因子计算层 | 模块3 缺口回补概率模型（Gap Fill Probability Model） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 24 | L1573 | §3 L1 因子计算层 | 模块4 逼空行情检测模型（Short Squeeze Detection Model） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 25 | L1634 | §3 L1 因子计算层 | 模块5 日内量能结构与订单流分析模型（Intraday Volume Structure & Ord | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 26 | L1684 | §3 L1 因子计算层 | 模块6 Wyckoff吸筹阶段与底部确认模型（Wyckoff Accumulation & Bott | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 27 | L1742 | §3 L1 因子计算层 | 模块7 多指标背离检测模型（Multi-Indicator Divergence Detection | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 28 | L1781 | §3 L1 因子计算层 | 模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 29 | L1832 | §3 L1 因子计算层 | 模块9 多维度相对强弱筛选模型（Multi-Dimensional Relative Strengt | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 30 | L1870 | §3 L1 因子计算层 | 模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 31 | L1926 | §3 L1 因子计算层 | 模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 32 | L1968 | §3 L1 因子计算层 | 模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Dete | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 33 | L2021 | §3 L1 因子计算层 | 模块14 极端情绪反转与恐慌底部检测模型（Extreme Sentiment Reversal & | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 34 | L2060 | §3 L1 因子计算层 | 模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detecti | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 35 | L2099 | §3 L1 因子计算层 | 模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 36 | L2148 | §3 L1 因子计算层 | 模块18 Wyckoff二次测试与动量延续模型（Wyckoff Secondary Test & M | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 37 | L2196 | §3 L1 因子计算层 | 模块19 市场体制转换模型（Regime-Switching Model） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 38 | L2258 | §3 L1 因子计算层 | 模块20 Wyckoff派发阶段与CVD背离检测模型（Wyckoff Distribution & | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 39 | L2310 | §3 L1 因子计算层 | 模块21 隔夜全球市场传导与事件影响评估模型（Overnight Global Market Con | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 40 | L2348 | §3 L1 因子计算层 | 模块22 产业链传导与供应链动量模型（Supply Chain Momentum & Industr | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 41 | L2381 | §3 L1 因子计算层 | 模块26 3秒级逆势资金流识别模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 42 | L2571 | §3 L1 因子计算层 | 模块30 多维度资金流体制识别模型（Multi-Dimensional Flow Regime Id | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 43 | L2619 | §3 L1 因子计算层 | 模块31 协同交易行为检测模型（Coordinated Trading Detection Mode | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 44 | L2673 | §3 L1 因子计算层 | 模块33 IC加权多因子涨停板潜力评分模型（IC-Weighted Multi-Factor Lim | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 45 | L2724 | §3 L1 因子计算层 | 模块34 异质参与者互动模型（Heterogeneous Agent Interaction Mod | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 46 | L2778 | §3 L1 因子计算层 | 模块35 开盘竞价微结构分析模型（Opening Auction Microstructure An | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 47 | L2827 | §3 L1 因子计算层 | 模块39 多因子选股评分模型（Multi-Factor Stock Selection Scorin | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 48 | L2861 | §3 L1 因子计算层 | 模块40 板块拥挤度与启动条件量化模型（Sector Crowding & Launch Condi | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RC-06-D 拥挤度) | 专业机构实践模块系列，双轨制下沉 indicators |
| 49 | L2893 | §3 L1 因子计算层 | 模块45 分时微结构分析与大小盘风格检测模型（Intraday Microstructure & S | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 50 | L2930 | §3 L1 因子计算层 | 模块50 北向资金流向与Smart Money信号模型（Northbound Capital Flo | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 51 | L2956 | §3 L1 因子计算层 | 模块51 波动率压缩与突破模型（Volatility Compression & Breakout | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 52 | L3009 | §3 L1 因子计算层 | 模块52 跨资产订单流网络与亏钱效应扩散模型（Cross-Asset Order Flow Netw | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 53 | L3049 | §3 L1 因子计算层 | 模块52 汇总：缺失模块与建议归属层映射（更新版） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 54 | L3125 | §3 L1 因子计算层 | 模块53 衍生品到期日效应与波动率日历模型（Derivatives Expiration Effec | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 55 | L3152 | §3 L1 因子计算层 | 模块55 A股日历效应与关键节点量化模型（A-Share Calendar Effect & Key | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 56 | L3180 | §3 L1 因子计算层 | 模块58 统一技术图形识别引擎（Unified Technical Pattern Recognit | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 57 | L3265 | §3 L1 因子计算层 | 模块58 附录：已有架构覆盖的功能（不重复列出） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 58 | L3288 | §3 L1 因子计算层 | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 59 | L3309 | §4 L2-A 信号生成层 | §4.1 信号工厂九大子阶段 | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 部分 | 归indicators(BM-SEL-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 60 | L3328 | §4 L2-A 信号生成层 | §4.2 信号与因子的关系 | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 61 | L3357 | §4 L2-A 信号生成层 | §4.3 多策略投票与加权模型（v0.1升级） | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 是 | 已覆盖(BM-SEL-02-K) | 与现有环节 BM-SEL-02-K 多策略投票与加权 等价/被其包含(sim=1.00) |
| 62 | L3377 | §4 L2-A 信号生成层 | §4.4 信号聚合器架构 | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 是 | 已覆盖(BM-SEL-02-L) | 与现有环节 BM-SEL-02-L 信号聚合器架构 等价/被其包含(sim=1.00) |
| 63 | L3412 | §4 L2-A 信号生成层 | §4.5 🆕收益率条件密度预测模型（信号层的分布增强） | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 是 | 已覆盖(BM-SEL-13) | 与现有环节 BM-SEL-13 收益率条件密度预测 等价/被其包含(sim=1.00) |
| 64 | L3467 | §4 L2-A 信号生成层 | §4.5.1 🆕密度预测专业机构实践增强 | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 部分 | 归indicators(BM-SEL-13) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 65 | L3635 | §4 L2-A 信号生成层 | 模块17 多维度底部确认与右侧入场模型（Multi-Dimensional Bottom Confi | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 66 | L3675 | §4 L2-A 信号生成层 | 模块29 次日上涨概率统一门槛模块 | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 67 | L3829 | §4 L2-A 信号生成层 | 模块44 量化模式匹配与执行策略库（Quantitative Pattern Matching & | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 68 | L3877 | §4 L2-A 信号生成层 | 模块49 财报季事件驱动与PEAD模型（Earnings Season Event-Driven & | D_SIGNAL/D_ASHARE_SIGNAL | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 69 | L3945 | §5 L2-B 主力行为分析层 | §5.1 三层递进架构 | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 70 | L3956 | §5 L2-B 主力行为分析层 | §5.2 C-011 资金行为分析（实时识别层） | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 71 | L3971 | §5 L2-B 主力行为分析层 | §5.3 C-034 主力资金行为自迭代分析（动态推演层） | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 72 | L3986 | §5 L2-B 主力行为分析层 | §5.4 C-035 庄家行为模式自迭代识别与模拟（庄家专项层） | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 73 | L4004 | §5 L2-B 主力行为分析层 | §5.5 C-036 资金群体生态与多方博弈模拟（多方博弈层） | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 是 | 已覆盖(BM-SEL-05-F) | 与现有环节 BM-SEL-05-F 多方博弈模拟 等价/被其包含(sim=1.00) |
| 74 | L4037 | §5 L2-B 主力行为分析层 | §5.6 主力行为层→信号层注入规则 | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 75 | L4060 | §5 L2-B 主力行为分析层 | 模块27 主力假动作与筹码派发识别模块 | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 76 | L4170 | §5 L2-B 主力行为分析层 | 模块54 信息不对称期与操纵行为检测模型（Information Asymmetry Period | D_ASHARE_SIGNAL/D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 77 | L4238 | §6 L2-C 市场状态与大盘预测层 | §6.1 C-021 市场状态判定 | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 78 | L4302 | §6 L2-C 市场状态与大盘预测层 | §6.1.1 连续评分升级路径 | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-18) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 79 | L4336 | §6 L2-C 市场状态与大盘预测层 | §6.1.2 跨市场Regime样本策略 | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 80 | L4373 | §6 L2-C 市场状态与大盘预测层 | §6.1.3 🆕v4.1 板块轮动序列追踪（Sector Rotation Sequence Tra | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-08) | 与现有环节 BM-SEL-08 板块轮动序列追踪 等价/被其包含(sim=1.00) |
| 81 | L4422 | §6 L2-C 市场状态与大盘预测层 | §6.2 C-014 大盘预测与次日走势预判 | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 82 | L4514 | §6 L2-C 市场状态与大盘预测层 | §6.3 C-039 跨市场传导量化模型 | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 83 | L4532 | §6 L2-C 市场状态与大盘预测层 | §6.4 体制转换检测（Regime Change Detection） | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-07) | 与现有环节 BM-SEL-07 体制转换检测 等价/被其包含(sim=1.00) |
| 84 | L4565 | §6 L2-C 市场状态与大盘预测层 | §6.5 市场状态层→流水线其他层的联动 | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 85 | L4602 | §6 L2-C 市场状态与大盘预测层 | §6.6 🆕v4.1 调整周期追踪（Adjustment Cycle Tracking） | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-09) | 与现有环节 BM-SEL-09 调整周期追踪 等价/被其包含(sim=1.00) |
| 86 | L4675 | §6 L2-C 市场状态与大盘预测层 | §6.7 🆕v4.1 行情生命周期阶段（Market Lifecycle Phase） | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-10) | 与现有环节 BM-SEL-10 行情生命周期阶段 等价/被其包含(sim=1.00) |
| 87 | L4754 | §6 L2-C 市场状态与大盘预测层 | 模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy M | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 88 | L4787 | §6 L2-C 市场状态与大盘预测层 | 模块25 板块轮动与主线切换量化模型（Sector Rotation & Theme Switchi | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 89 | L4820 | §6 L2-C 市场状态与大盘预测层 | 模块32 市场风格体制识别模型（Market Style Regime Identification | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 90 | L4853 | §6 L2-C 市场状态与大盘预测层 | 模块41 事件链推理与因果图模型（Event Chain Reasoning & Causal Gr | D_INTELLIGENCE/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 91 | L4913 | §7 L2-D 知识图谱与因果推演层 | §7.1 六类知识图谱 | D_KNOWLEDGE/D_INTELLIGENCE | stock_selection | 部分 | 归indicators(BM-SEL-11) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 92 | L4924 | §7 L2-D 知识图谱与因果推演层 | §7.2 事件驱动的因果推演流程 | D_KNOWLEDGE/D_INTELLIGENCE | stock_selection | 部分 | 归indicators(BM-BT-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 93 | L4940 | §7 L2-D 知识图谱与因果推演层 | 模块28 利好落地变利空（预期透支）模块 | D_KNOWLEDGE/D_INTELLIGENCE | stock_selection | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 94 | L5074 | §8 L3 策略决策与组合优化层 | §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 部分 | 归indicators(BM-SEL-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 95 | L5097 | §8 L3 策略决策与组合优化层 | §8.2 多情景对策与预案(C-005) | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 部分 | 归indicators(BM-BUY-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 96 | L5135 | §8 L3 策略决策与组合优化层 | §8.3 做T日内套利(C-012) | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 是 | 已覆盖(BM-SELL-08) | 与现有环节 BM-SELL-08 做T日内套利 等价/被其包含(sim=1.00) |
| 97 | L5161 | §8 L3 策略决策与组合优化层 | §8.4 C-013 外部指令盯盘 | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 是 | 已覆盖(BM-BUY-06) | 与现有环节 BM-BUY-06 外部指令盯盘 等价/被其包含(sim=1.00) |
| 98 | L5184 | §8 L3 策略决策与组合优化层 | §8.5 组合优化引擎 | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 是 | 已覆盖(BM-SEL-21) | 与现有环节 BM-SEL-21 组合优化 等价/被其包含(sim=1.00) |
| 99 | L5229 | §8 L3 策略决策与组合优化层 | 模块13 隔夜收益预测与开仓期望值模型（Overnight Return Prediction & | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 100 | L5268 | §8 L3 策略决策与组合优化层 | 模块24 核心-卫星仓位管理模型（Core-Satellite Position Managemen | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 部分 | 归indicators(BM-POS-02 核心-卫星) | 专业机构实践模块系列，双轨制下沉 indicators |
| 101 | L5302 | §8 L3 策略决策与组合优化层 | 模块47 Kelly Criterion仓位管理与Risk Parity组合优化模型（Kelly P | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 是 | 已覆盖(BM-SEL-21) | 与现有环节 BM-SEL-21 组合优化 等价/被其包含(sim=1.00) |
| 102 | L5353 | §8 L3 策略决策与组合优化层 | 模块56 量能×体制×风格三维策略矩阵模型（Volume×Regime×Style 3D Strat | D_PF_CORE/D_PF_ALLOC/D_ORCHESTRATOR | buy_flow | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 103 | L5434 | §9 L4 风控与执行层（→A4风险架构） | §9.1 C-004 自适应风控三层体系（→A4风险架构） | D_RISK/D_EX_CORE | execution/risk_control | 部分 | 归indicators(BM-EXE-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 104 | L5491 | §9 L4 风控与执行层（→A4风险架构） | §9.2 交易执行(C-002)与执行质量(C-046) | D_RISK/D_EX_CORE | execution/risk_control | 是 | 已覆盖(BM-EXE-02) | 与现有环节 BM-EXE-02 交易执行 等价/被其包含(sim=1.00) |
| 105 | L5534 | §9 L4 风控与执行层（→A4风险架构） | §9.3 风控与执行的交互规则 | D_RISK/D_EX_CORE | execution/risk_control | 部分 | 归indicators(BM-EXE-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 106 | L5553 | §9 L4 风控与执行层（→A4风险架构） | 模块36 买入后即时验证与快速纠错模型（Post-Entry Instant Validation | D_RISK/D_EX_CORE | execution/risk_control | 部分 | 归indicators(BM-BUY-03 买入后验证) | 专业机构实践模块系列，双轨制下沉 indicators |
| 107 | L5579 | §9 L4 风控与执行层（→A4风险架构） | 模块37 系统性风险分级预警与尾部风险管理模型（Systemic Risk Tiered Alert | D_RISK/D_EX_CORE | execution/risk_control | 部分 | 归indicators(BM-RC-12 系统性风险预警) | 专业机构实践模块系列，双轨制下沉 indicators |
| 108 | L5607 | §9 L4 风控与执行层（→A4风险架构） | 模块42 交易绩效归因与策略退化检测模型（Performance Attribution & Str | D_RISK/D_EX_CORE | execution/risk_control | 是 | 已覆盖(BM-REC-02-B) | 与现有环节 BM-REC-02-B 绩效归因 等价/被其包含(sim=1.00) |
| 109 | L5645 | §9 L4 风控与执行层（→A4风险架构） | 模块43 ATR动态止损与Bayesian参数优化模型（ATR Dynamic Stop-Loss | D_RISK/D_EX_CORE | execution/risk_control | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 110 | L5713 | 决策编排器——缺失功能模块 | 模块38 交易计划偏差检测与异常机会评估模型（Trade Plan Deviation Detect |  |  | 部分 | 归indicators(BM-REC-02-C 复盘) | 专业机构实践模块系列，双轨制下沉 indicators |
| 111 | L5740 | 决策编排器——缺失功能模块 | 模块46 决策树与强化学习交易决策架构（Decision Tree & RL Trading Dec |  |  | 部分 | 排除(Agent架构交叉引用,主体不挂) | 专业机构实践模块系列，双轨制下沉 indicators |
| 112 | L5788 | 决策编排器——缺失功能模块 | 模块48 动态信号权重模型（Dynamic Signal Weighting via Bayesia |  |  | 部分 | 归indicators(BM-SEL-02-K 动态信号权重) | 专业机构实践模块系列，双轨制下沉 indicators |
| 113 | L5840 | 决策编排器——缺失功能模块 | 模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） |  |  | 部分 | 归indicators(BM-SEL-02-J 信号模型库) | 专业机构实践模块系列，双轨制下沉 indicators（信号工厂模型库清单） |
| 114 | L5885 | §10 L5 闭环优化与自迭代层 | §10.0 C-010 报告/复盘/归因（闭环数据源） | D_FEEDBACK_LOOP/D_FBL_* | reconciliation | 是 | 已覆盖(BM-REC-02) | 与现有环节 BM-REC-02 报告复盘 等价/被其包含(sim=1.00) |
| 115 | L5906 | §10 L5 闭环优化与自迭代层 | §10.1 C-007 十五个优化维度 | D_FEEDBACK_LOOP/D_FBL_* | reconciliation | 部分 | 归indicators(BM-SEL-21) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 116 | L5928 | §10 L5 闭环优化与自迭代层 | §10.2 五大自迭代增强 | D_FEEDBACK_LOOP/D_FBL_* | reconciliation | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 117 | L5938 | §10 L5 闭环优化与自迭代层 | §10.3 C-041 元级迭代（二阶优化） | D_FEEDBACK_LOOP/D_FBL_* | reconciliation | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 118 | L5950 | §10 L5 闭环优化与自迭代层 | §10.4 闭环反馈路径 | D_FEEDBACK_LOOP/D_FBL_* | reconciliation | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 119 | L5982 | §11 L6 决策可解释性与人机协作层 | §11.1 C-030 决策溯源链 | D_INTELLIGENCE | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 120 | L6003 | §11 L6 决策可解释性与人机协作层 | §11.2 C-031 置信度分层决策 | D_INTELLIGENCE | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 121 | L6036 | §12 横切层 | §12.1 C-003 自动回测与仿真 | D_SHARED/D_INFRA_RUNTIME | stock_selection | 部分 | 归indicators(BM-BT-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 122 | L6069 | §12 横切层 | §12.2 C-008 AI自治运维（→A9运维架构） | D_SHARED/D_INFRA_RUNTIME | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 123 | L6075 | §12 横切层 | §12.3 C-029 ML模型工厂 | D_SHARED/D_INFRA_RUNTIME | stock_selection | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 124 | L6105 | §12 横切层 | §12.4 C-033 过拟合系统性防护 | D_SHARED/D_INFRA_RUNTIME | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 125 | L6120 | §12 横切层 | §12.5 通知与告警(C-015) + 审计与合规(C-043) + 成本治理(C-044)（→A | D_SHARED/D_INFRA_RUNTIME | stock_selection | 部分 | 归indicators(BM-RC-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 126 | L6273 | §14 盘中实时事件处理 | §14.1 事件完整清单与处理流程 | D_INTEGRATION | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 127 | L6285 | §14 盘中实时事件处理 | §14.2 事件处理流水线 | D_INTEGRATION | stock_selection | 部分 | 归indicators(BM-SEL-27) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 128 | L6325 | §15 计算节奏与时序 | §15.1 交易时段主流程 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 129 | L6381 | §15 计算节奏与时序 | §15.2 盘后研究迭代流程 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 130 | L6438 | §15 计算节奏与时序 | §15.3 计算频率汇总 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 131 | L6497 | §17 数据源到流水线映射 | §17.1 标准数据源映射 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 132 | L6538 | §17 数据源到流水线映射 | §17.2 另类数据映射 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 133 | L6553 | §17 数据源到流水线映射 | §17.3 本地计算指标映射 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 134 | L6566 | §17 数据源到流水线映射 | §17.4 知识图谱数据映射 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 135 | L6577 | §17 数据源到流水线映射 | §17.5 标准参考数据映射 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 136 | L6627 | §19 质量属性与边界规则引用 | §19.1 AI行为安全边界（B-001\~B-020） |  |  | 否 | 排除 | 引用类章节 |
| 137 | L6676 | §19 质量属性与边界规则引用 | §19.2 关键质量属性优先级 |  |  | 否 | 排除 | 引用类章节 |
| 138 | L6703 | §19 质量属性与边界规则引用 | §19.3 法规合规映射（→A6合规🔒） |  |  | 否 | 排除 | 引用类章节 |
| 139 | L6732 | §20 方法论约束与架构决策引用 | §20.1 方法论约束一：策略类型目录 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 140 | L6749 | §20 方法论约束与架构决策引用 | §20.2 方法论约束二：因子分类与IC阈值 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 141 | L6770 | §20 方法论约束与架构决策引用 | §20.3 方法论约束三：组合构建规则 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 142 | L6789 | §20 方法论约束与架构决策引用 | §20.4 方法论约束四：风险模型 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 143 | L6819 | §20 方法论约束与架构决策引用 | §20.5 方法论约束五：成本模型 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 144 | L6834 | §20 方法论约束与架构决策引用 | §20.6 方法论约束六：基准 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 145 | L6849 | §20 方法论约束与架构决策引用 | §20.7 方法论约束七：回测方法论 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 146 | L6997 | §20 方法论约束与架构决策引用 | §20.8 方法论约束八：训练-服务一致性(Feature Store) | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 147 | L7005 | §20 方法论约束与架构决策引用 | §20.9 方法论约束九：T+1次日预测约束 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 148 | L7022 | §20 方法论约束与架构决策引用 | §20.10 方法论约束十：流动性风险约束 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 149 | L7036 | §20 方法论约束与架构决策引用 | §20.11 方法论约束十一：数据分层使用约束 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 150 | L7054 | §20 方法论约束与架构决策引用 | §20.12 🆕方法论约束十二：收益率条件密度预测约束（v3.4新增） | D_DATA/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-13) | 与现有环节 BM-SEL-13 收益率条件密度预测 等价/被其包含(sim=1.00) |
| 151 | L7077 | §20 方法论约束与架构决策引用 | §20.13 🆕方法论约束十三：仓位管理约束（v4.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 152 | L7091 | §20 方法论约束与架构决策引用 | §20.14 架构决策引用 | D_DATA/D_MKT_DATA | stock_selection | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 153 | L7371 | §20 方法论约束与架构决策引用 | §20.15 熔断检测职责分配 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 154 | L7383 | §20 方法论约束与架构决策引用 | §20.16 硬边界约束引用 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 155 | L7935 | §21 资产与市场覆盖矩阵 | §21.1 分级标准 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-16) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 156 | L7945 | §21 资产与市场覆盖矩阵 | §21.2 资产覆盖矩阵 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 157 | L7993 | §21 资产与市场覆盖矩阵 | §21.3 关键时间节点 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-22) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 158 | L8007 | §22 角色与旅程 | §22.1 目标角色与诉求 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 159 | L8012 | §22 角色与旅程 | 角色总览 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 160 | L8021 | §22 角色与旅程 | 各角色详解 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 161 | L8065 | §22 角色与旅程 | 人机交互边界总结 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 162 | L8087 | §22 角色与旅程 | §22.2 核心用户旅程概要 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 163 | L8094 | §22 角色与旅程 | 旅程1：盘前准备 → 集合竞价 → 盘中执行（交易时段主流程） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-EXE-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 164 | L8159 | §22 角色与旅程 | 旅程2：盘后清算 → 龙虎榜 → AI学习 → 审批（研究迭代主流程） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-REC-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 165 | L8219 | §23 能力卡片完整引用 | P0 — 核心能力（没有它系统不可用，共14项） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 166 | L8435 | §23 能力卡片完整引用 | P1 — 重要能力（增强系统价值） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 167 | L8552 | §23 能力卡片完整引用 | P1 — 自我迭代增强能力（全维度闭环补全） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 168 | L8843 | §23 能力卡片完整引用 | P1 — A股博弈智能套件 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 169 | L8887 | §23 能力卡片完整引用 | P1 — 风控增强与执行质量（黑天鹅/跨市场/压力测试/容量/执行分析） | D_DATA/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-RC-08-C) | 与现有环节 BM-RC-08-C 压力测试 等价/被其包含(sim=1.00) |
| 170 | L8959 | §23 能力卡片完整引用 | P2 — 增强能力（C-041/C-043阶段二/C-044） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-23) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 171 | L8998 | §23 能力卡片完整引用 | P2 — 增强能力 + P1 已提升能力（锦上添花） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 172 | L9040 | §24 外部系统交互引用 | §24.0 数据源总览 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 173 | L9047 | §24 外部系统交互引用 | §24.1 外部系统交互矩阵 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 174 | L9062 | §24 外部系统交互引用 | §24.2 数据源分工与边界 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 175 | L9093 | §24 外部系统交互引用 | §24.3 外部依赖风险评估 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 176 | L9113 | §25 术语表引用 | 量化交易术语 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 177 | L9150 | §25 术语表引用 | 架构与设计术语 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 178 | L9211 | §25 术语表引用 | A股市场术语 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 179 | L9264 | §27 系统级成功指标引用 | 成功指标三档制 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 180 | L9307 | §27 系统级成功指标引用 | 失败指标（触发任一条即需重大调整） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 181 | L9324 | §28 能力全景图引用 | 分层架构总览 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 182 | L9404 | §28 能力全景图引用 | 能力血缘关系图 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 183 | L9526 | §28 能力全景图引用 | 数据流向主线 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 184 | L9532 | §28 能力全景图引用 | 依赖矩阵（谁依赖谁） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 185 | L9616 | §28 能力全景图引用 | 能力冲突矩阵 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SELL-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 186 | L9624 | §28 能力全景图引用 | 能力-域映射坐标 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-23) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 187 | L9681 | §28 能力全景图引用 | 交易日时间激活视图 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-EXE-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 188 | L9758 | §28 能力全景图引用 | 能力交互热点图 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 189 | L9778 | §28 能力全景图引用 | 正向闭环视图 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 190 | L9854 | §29 架构补充：基础设施必需项与方法论增强 | §29.A 基础设施与运维增强 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 191 | L9856 | §29 架构补充：基础设施必需项与方法论增强 | §29.1 多进程隔离与运行时架构（→A9运维架构） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 192 | L9862 | §29 架构补充：基础设施必需项与方法论增强 | §29.2 特征存储 (Feature Store) | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 193 | L9978 | §29 架构补充：基础设施必需项与方法论增强 | §29.3 模型注册与实验管理 (Model Registry + Experiment Track | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 194 | L10011 | §29 架构补充：基础设施必需项与方法论增强 | §29.4 时序数据库与分层存储架构（→A3数据架构） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 195 | L10019 | §29 架构补充：基础设施必需项与方法论增强 | §29.B ML模型与方法论增强 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 196 | L10021 | §29 架构补充：基础设施必需项与方法论增强 | §29.5 特征漂移与概念漂移检测 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-MT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 197 | L10075 | §29 架构补充：基础设施必需项与方法论增强 | §29.6 图神经网络用于股票关系建模 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 198 | L10121 | §29 架构补充：基础设施必需项与方法论增强 | §29.7 Transformer时序架构用于密度预测增强 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 199 | L10177 | §29 架构补充：基础设施必需项与方法论增强 | §29.8 签名方法 (Signature Methods / Rough Path Theory) | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 200 | L10228 | §29 架构补充：基础设施必需项与方法论增强 | §29.9 强化学习用于组合优化与订单执行 | D_DATA/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-21) | 与现有环节 BM-SEL-21 组合优化 等价/被其包含(sim=1.00) |
| 201 | L10318 | §29 架构补充：基础设施必需项与方法论增强 | §29.C 交易与执行增强 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-EXE-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 202 | L10320 | §29 架构补充：基础设施必需项与方法论增强 | §29.10 盘中即时反应决策引擎 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-25) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 203 | L10382 | §29 架构补充：基础设施必需项与方法论增强 | §29.11 大语言模型Agent用于基本面分析 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 204 | L10438 | §29 架构补充：基础设施必需项与方法论增强 | §29.12 另类数据源扩展 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 205 | L10477 | §29 架构补充：基础设施必需项与方法论增强 | §29.13 市场微观结构深度建模 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SIM-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 206 | L10517 | §29 架构补充：基础设施必需项与方法论增强 | §29.14 自动策略发现 (Automated Strategy Discovery) | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 207 | L10574 | §29 架构补充：基础设施必需项与方法论增强 | §29.15 \[编号保留—内容合并至§29.14] | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 208 | L10580 | §29 架构补充：基础设施必需项与方法论增强 | §29.E 统计推断与因果增强（v3.6+v5.1+v6.0） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-MT-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 209 | L10582 | §29 架构补充：基础设施必需项与方法论增强 | §29.16 Conformal Prediction（共形预测） | D_DATA/D_MKT_DATA | stock_selection | 是 | 已覆盖(BM-SEL-14) | 与现有环节 BM-SEL-14 共形预测 等价/被其包含(sim=1.00) |
| 210 | L10722 | §29 架构补充：基础设施必需项与方法论增强 | §29.17 Survival Analysis（生存分析用于交易决策） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-15) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 211 | L10782 | §29 架构补充：基础设施必需项与方法论增强 | §29.18 Causal ML 深度补充 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-MT-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 212 | L10849 | §29 架构补充：基础设施必需项与方法论增强 | §29.19 金融时序数据增强 (Financial Time Series Data Augmen | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 213 | L10930 | §29 架构补充：基础设施必需项与方法论增强 | §29.G v5.1+架构增强 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 214 | L10934 | §29 架构补充：基础设施必需项与方法论增强 | §29.22 Mamba/SSM状态空间模型用于金融时序建模（v5.1新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 215 | L11029 | §29 架构补充：基础设施必需项与方法论增强 | §29.23 数字孪生市场仿真（v5.1新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SIM-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 216 | L11106 | §29 架构补充：基础设施必需项与方法论增强 | §29.24 神经符号融合推理（v5.1新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-25) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 217 | L11226 | §29 架构补充：基础设施必需项与方法论增强 | §29.25 EU AI Act合规架构增强（→A6合规架构🔒） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-13) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 218 | L11242 | §29 架构补充：基础设施必需项与方法论增强 | §29.26 时序保形预测增强：TCP/DDCI/CP-VaR等价（v5.1新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 219 | L11248 | §29 架构补充：基础设施必需项与方法论增强 | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | D_DATA/D_MKT_DATA | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 220 | L11256 | §29 架构补充：基础设施必需项与方法论增强 | §29.28 模型压缩与推理加速（v5.1新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 221 | L11335 | §29 架构补充：基础设施必需项与方法论增强 | §29.29 量子-经典混合计算路线图（v5.1新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-REC-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 222 | L11406 | §29 架构补充：基础设施必需项与方法论增强 | §29.30 A股扩散模型数据增强：金融风洞/GBM-Diffusion/InterDiff（v5. | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 223 | L11489 | §29 架构补充：基础设施必需项与方法论增强 | §29.F 基础设施扩展与远期储备（v5.1+v6.0） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-07) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 224 | L11493 | §29 架构补充：基础设施必需项与方法论增强 | §29.31 \[编号保留—内容合并至§29.30] | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 225 | L11497 | §29 架构补充：基础设施必需项与方法论增强 | §29.32 LLM进化式策略搜索（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 226 | L11557 | §29 架构补充：基础设施必需项与方法论增强 | §29.33 KAN Kolmogorov-Arnold网络（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 227 | L11626 | §29 架构补充：基础设施必需项与方法论增强 | §29.34 xLSTM扩展长短期记忆网络（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-07) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 228 | L11684 | §29 架构补充：基础设施必需项与方法论增强 | §29.35 持续学习抗遗忘框架（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-MT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 229 | L11738 | §29 架构补充：基础设施必需项与方法论增强 | §29.36 因果强化学习 Causal RL（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-EXE-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 230 | L11790 | §29 架构补充：基础设施必需项与方法论增强 | §29.37 LLM自评估与交叉验证（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 231 | L11842 | §29 架构补充：基础设施必需项与方法论增强 | §29.38 多模态金融推理（v6.0新增） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-11) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 232 | L11887 | §29 架构补充：基础设施必需项与方法论增强 | §29.39 架构增强裁定书（2026-05-26更新） | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 233 | L12114 | §29 架构补充：基础设施必需项与方法论增强 | §29.Z 结论与实现路径 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 234 | L12120 | §29 架构补充：基础设施必需项与方法论增强 | §29.20 架构增强二元结论与实现路径 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 235 | L12202 | §29 架构补充：基础设施必需项与方法论增强 | §29.21 学习系统桥接声明 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-RC-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 236 | L12261 | §30 场外草稿区缺失模块补充 | §30.1 核心价值链域缺失模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 237 | L12442 | §30 场外草稿区缺失模块补充 | §30.2 增强与扩展域缺失模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 238 | L12568 | §30 场外草稿区缺失模块补充 | §30.3 核心交易链域缺失模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-EXE-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 239 | L12582 | §30 场外草稿区缺失模块补充 | P0 模块明细 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 240 | L12601 | §30 场外草稿区缺失模块补充 | P1 模块分类汇总（92个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 241 | L12621 | §30 场外草稿区缺失模块补充 | P2 模块分类汇总（30个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 242 | L12627 | §30 场外草稿区缺失模块补充 | P3 模块分类汇总（3个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 243 | L12633 | §30 场外草稿区缺失模块补充 | 域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 244 | L12647 | §30 场外草稿区缺失模块补充 | P0 模块明细 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 245 | L12660 | §30 场外草稿区缺失模块补充 | P1 模块分类汇总（99个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 246 | L12666 | §30 场外草稿区缺失模块补充 | P2 模块分类汇总（29个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 247 | L12672 | §30 场外草稿区缺失模块补充 | 域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 248 | L12686 | §30 场外草稿区缺失模块补充 | P0 模块明细 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 249 | L12705 | §30 场外草稿区缺失模块补充 | P1 模块分类汇总（85个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 250 | L12711 | §30 场外草稿区缺失模块补充 | P2 模块分类汇总（62个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 251 | L12717 | §30 场外草稿区缺失模块补充 | P3 模块分类汇总（1个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 252 | L12723 | §30 场外草稿区缺失模块补充 | 域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 253 | L12737 | §30 场外草稿区缺失模块补充 | P0 模块明细 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 254 | L12752 | §30 场外草稿区缺失模块补充 | P1 模块分类汇总（7个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 255 | L12758 | §30 场外草稿区缺失模块补充 | P2 模块分类汇总（11个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 256 | L12764 | §30 场外草稿区缺失模块补充 | 域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 257 | L12778 | §30 场外草稿区缺失模块补充 | P0 模块明细 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 258 | L12788 | §30 场外草稿区缺失模块补充 | P1 模块分类汇总（5个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 259 | L12794 | §30 场外草稿区缺失模块补充 | P2 模块分类汇总（7个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 260 | L12800 | §30 场外草稿区缺失模块补充 | XS-EXT 模块分类汇总（5个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 261 | L12806 | §30 场外草稿区缺失模块补充 | 域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 262 | L12820 | §30 场外草稿区缺失模块补充 | P0 模块明细 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 263 | L12829 | §30 场外草稿区缺失模块补充 | P1 模块分类汇总（14个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 264 | L12835 | §30 场外草稿区缺失模块补充 | P2 模块分类汇总（17个） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 265 | L12841 | §30 场外草稿区缺失模块补充 | 域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 266 | L12863 | §30 场外草稿区缺失模块补充 | ❌不能建模块门禁条件分布 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 267 | L12882 | §30 场外草稿区缺失模块补充 | §30.4 ML与数据工程域缺失模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BT-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 268 | L13059 | §30 场外草稿区缺失模块补充 | §30.5 自治与基础设施域缺失模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 269 | L13219 | §30 场外草稿区缺失模块补充 | §30.6 运维安全治理域缺失模块 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 270 | L13631 | §30 场外草稿区缺失模块补充 | §30.7 跨域交叉点与因果链缺失 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-MT-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 271 | L13642 | §30 场外草稿区缺失模块补充 | §30.8 §30域级裁定汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |

## 合规架构.md (64 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | 📌 备注体系说明 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 2 | L29 |  | 📌 门禁状态 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 3 | L59 |  | 📌 文档边界声明（激活后生效） |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 4 | L74 |  | 📌 §0 架构定位 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 5 | L363 | §1 交易合规 | §1.1 交易行为合规检测 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 6 | L378 | §1 交易合规 | §1.1.1 涨跌停交易约束 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 7 | L387 | §1 交易合规 | §1.2 市场操纵防护 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 8 | L414 | §1 交易合规 | 模块27：主力假动作与筹码派发识别模块 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 9 | L524 | §1 交易合规 | 模块31：协同交易行为检测模型（Coordinated Trading Detection Mode | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 10 | L578 | §1 交易合规 | 模块54：信息不对称期与操纵行为检测模型（Information Asymmetry Period | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 11 | L613 | §1 交易合规 | §1.3 交易速率与时间约束 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 12 | L621 | §1 交易合规 | §1.4 程序化交易报告义务 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 13 | L642 | §2 持仓合规 | §2.1 持仓限额 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 14 | L650 | §2 持仓合规 | §2.2 行业集中度 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 15 | L658 | §2 持仓合规 | §2.3 短线交易防护 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 16 | L668 | §2 持仓合规 | §2.4 内幕交易防护 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 17 | L678 | §3 报告合规 | §3.1 审计证据链架构 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 18 | L766 | §3 报告合规 | §3.2 决策溯源链 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 19 | L798 | §3 报告合规 | §3.3 监管报送 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 20 | L822 | §4 AI合规 | §4.1 AI风险分类 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 21 | L835 | §4 AI合规 | §4.2 可解释性要求 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 22 | L886 | §4 AI合规 | §4.3 模型注册与治理 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 23 | L937 | §4 AI合规 | §4.4 人类监督 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 24 | L954 | §4 AI合规 | §4.5 AI伦理声明 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 25 | L972 | §5 跨市场合规 | §5.1 市场合规规则矩阵 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 26 | L984 | §5 跨市场合规 | §5.2 合规规则引擎 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 27 | L1045 | §5 跨市场合规 | §5.3 法域冲突解决 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 28 | L1059 | §6 零知识审计 | §6.1 技术基础 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 29 | L1094 | §6 零知识审计 | §6.2 zkCA架构设计 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 30 | L1122 | §6 零知识审计 | §6.3 实施路线 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 31 | L1137 | §6 零知识审计 | §6.4 计算开销评估 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 32 | L1151 | §7 法规映射表 | §7.1 中国法规 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 33 | L1168 | §7 法规映射表 | §7.2 国际法规(跨市场扩展后适用) |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 34 | L1186 | §7 法规映射表 | §7.3 ESRB系统性风险关注 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 35 | L1210 | §8 合规技术架构 | §8.1 合规引擎架构 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 36 | L1262 | §8 合规技术架构 | §8.2 合规事件流 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 37 | L1282 | §8 合规技术架构 | §8.3 合规测试框架 |  |  | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 38 | L1297 | §9 合规治理与KPI | §9.1 合规变更审批 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 39 | L1310 | §9 合规治理与KPI | §9.2 三防线模型与AI治理 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 40 | L1322 | §9 合规治理与KPI | §9.3 合规KPI |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 41 | L1339 | §10 硬边界裁定 | §10.1 裁定原则 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 42 | L1348 | §10 硬边界裁定 | §10.2 47项功能二元裁定 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 43 | L1414 | §10 硬边界裁定 | §10.3 能建功能27项实施顺序 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 44 | L1448 | §10 硬边界裁定 | §10.4 门禁激活后功能扩展顺序 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 45 | L1467 | §11 信息合规 | §11.1 信息隔离墙 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 46 | L1479 | §11 信息合规 | §11.2 内幕交易深度防护 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 47 | L1494 | §11 信息合规 | §11.3 通信监控 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 48 | L1515 | §12 操作合规 | §12.1 操作风险防范 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 49 | L1531 | §12 操作合规 | §12.2 A股交易纪律合规检查 | D_COMPLIANCE | buy_flow | 部分 | 仅调用点锚点 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂）；本节属调用点范围 |
| 50 | L1555 | §12 操作合规 | §12.3 礼品与招待追踪 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 51 | L1568 | §12 操作合规 | §12.4 合规培训管理 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 52 | L1587 | §13 合规技术深度 | §13.1 合规策略即代码 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 53 | L1601 | §13 合规技术深度 | §13.2 合规规则版本控制与回测 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 54 | L1605 | §13 合规技术深度 | §13.3 合规事件升级 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 55 | L1609 | §13 合规技术深度 | §13.4 合规例外审批流 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 56 | L1623 | §13 合规技术深度 | §13.5 RegTech合规自动化 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 57 | L1638 | §13 合规技术深度 | §13.6 SBOM合规 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 58 | L1659 | §14 合规持续运营 | §14.1 AML/KYC引擎 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 59 | L1676 | §14 合规持续运营 | §14.2 合规证据图 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 60 | L1691 | §14 合规持续运营 | §14.3 法规自动解析与跨法规协调 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 61 | L1704 | §14 合规持续运营 | §14.4 合规知识持续积累 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 62 | L1721 | §15 硬边界裁定扩展 | §15.1 新增功能二元裁定 | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 63 | L1767 | §15 硬边界裁定扩展 | §15.2 A1§29.25 迁移内容：EU AI Act合规架构增强（历史参考） | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |
| 64 | L1775 | §15 硬边界裁定扩展 | §29.25 EU AI Act合规架构增强（v5.1新增） | D_COMPLIANCE | buy_flow | 否 | 排除 | 合规主体不挂（仅买入合规闸BM-BUY-08已挂） |

## 学习系统架构.md (60 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | 📌 文档边界声明 |  |  | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 2 | L25 |  | 📌 蓝图备注说明 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 3 | L33 | §0 架构定位 | §0.1 学习系统在全局架构中的位置 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 4 | L60 | §0 架构定位 | §0.2 与其他架构图的关系 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 5 | L74 | §0 架构定位 | §0.3 学习系统治理与安全约束摘要（统一视图） |  |  | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 6 | L133 | §1 行业对标与独创性分析 | §1.1 已公开系统对标 |  |  | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 7 | L151 | §1 行业对标与独创性分析 | §1.2 独创性评估 |  |  | 部分 | 归indicators(BM-SEL-22) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 8 | L164 | §1 行业对标与独创性分析 | §1.3 行业三条落地路径 |  |  | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 9 | L176 | §2 总体架构 | §2.1 学习系统架构总览（唯一真源） |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 10 | L287 | §2 总体架构 | §2.2 与交易决策流水线的关系定位 |  |  | 部分 | 归indicators(BM-MT-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 11 | L318 | §2 总体架构 | §2.3 知识流全景图（唯一真源） |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 12 | L476 | §3 S0 多模态知识采集层 | §3.1 采集源分类 | D_RESEARCH/D_INTELLIGENCE | research_incubation | 部分 | 归indicators(BM-RES-11) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 13 | L488 | §3 S0 多模态知识采集层 | §3.2 采集调度 | D_RESEARCH/D_INTELLIGENCE | research_incubation | 部分 | 归indicators(BM-RES-11) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 14 | L535 | §3 S0 多模态知识采集层 | §3.3 采集增强能力（v4.0新增） | D_RESEARCH/D_INTELLIGENCE | research_incubation | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 15 | L607 | §3 S0 多模态知识采集层 | §3.4 输出契约 | D_RESEARCH/D_INTELLIGENCE | research_incubation | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 16 | L637 | §4 S1 知识清洗与结构化层 | §4.1 清洗流水线 | D_RESEARCH/D_INTELLIGENCE | research_incubation | 部分 | 归indicators(BM-RES-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 17 | L709 | §4 S1 知识清洗与结构化层 | §4.2 输出契约 | D_RESEARCH/D_INTELLIGENCE | research_incubation | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 18 | L734 | §5 S2 知识分类与策略提取层 | §5.1 知识类型分类体系 | D_RESEARCH/D_ML_TRAIN | research_incubation/model_training | 是 | 已覆盖(BM-RES-09-A) | 与现有环节 BM-RES-09-A 知识类型分类体系 等价/被其包含(sim=1.00) |
| 19 | L812 | §5 S2 知识分类与策略提取层 | §5.2 策略提取流程 | D_RESEARCH/D_ML_TRAIN | research_incubation/model_training | 部分 | 归indicators(BM-RES-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 20 | L978 | §5 S2 知识分类与策略提取层 | §5.3 输出契约 | D_RESEARCH/D_ML_TRAIN | research_incubation/model_training | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 21 | L1018 | §6 S3 模块映射与工厂匹配层 | §6.1 模块工厂架构 | D_RESEARCH/D_ML_TRAIN | research_incubation/model_training | 是 | 已覆盖(BM-RES-10-A) | 与现有环节 BM-RES-10-A 模块工厂架构 等价/被其包含(sim=1.00) |
| 22 | L1142 | §6 S3 模块映射与工厂匹配层 | §6.2 与现有工厂的关系 | D_RESEARCH/D_ML_TRAIN | research_incubation/model_training | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 23 | L1166 | §6 S3 模块映射与工厂匹配层 | §6.3 输出契约 | D_RESEARCH/D_ML_TRAIN | research_incubation/model_training | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 24 | L1198 | §7 S4 模块创建与接入层 | §7.1 模块创建流程 | D_ML_TRAIN/D_INTEGRATION | model_training | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 25 | L1229 | §7 S4 模块创建与接入层 | §7.2 LLM辅助代码生成（v4.0升级：DSL约束+AST沙箱+三重语义一致性+进化式代码生成+ | D_ML_TRAIN/D_INTEGRATION | model_training | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 26 | L1331 | §7 S4 模块创建与接入层 | §7.3 输出契约 | D_ML_TRAIN/D_INTEGRATION | model_training | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 27 | L1360 | §7 S4 模块创建与接入层 | 四十六、决策树与强化学习交易决策架构（Decision Tree & RL Trading Deci | D_ML_TRAIN/D_INTEGRATION | model_training | 部分 | 归indicators(BM-BT-07) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 28 | L1410 | §8 S5 试运行与验证层 | §8.1 试运行流水线 | D_BACKTEST/D_SIMULATION | backtest_validation | 部分 | 归indicators(BM-MT-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 29 | L1583 | §8 S5 试运行与验证层 | §8.2 输出契约 | D_BACKTEST/D_SIMULATION | backtest_validation | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 30 | L1619 | §9 S6 元学习与自我进化层 | §9.1 元学习维度（v4.0升级：RSI架构4维度+技能库+在线EWC+轻量Agent化） | D_INTELLIGENCE/D_ML_TRAIN | research_incubation/model_training | 部分 | 归indicators(BM-MT-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 31 | L1771 | §9 S6 元学习与自我进化层 | §9.2 学习效果反馈闭环 | D_INTELLIGENCE/D_ML_TRAIN | research_incubation/model_training | 是 | 已覆盖(BM-MT-06-B) | 与现有环节 BM-MT-06-B 学习效果反馈闭环 等价/被其包含(sim=1.00) |
| 32 | L1801 | §9 S6 元学习与自我进化层 | 四十二、交易绩效归因与策略退化检测模型（Performance Attribution & Stra | D_INTELLIGENCE/D_ML_TRAIN | research_incubation/model_training | 是 | 已覆盖(BM-REC-02-B) | 与现有环节 BM-REC-02-B 绩效归因 等价/被其包含(sim=1.00) |
| 33 | L1841 | §10 横切层 | §10.1 知识库 (Knowledge Base) |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 34 | L1929 | §10 横切层 | §10.2 安全与审计 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 35 | L2064 | §10 横切层 | §10.3 MLOps闭环（v4.0新增，裁定✅R-13） |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 36 | L2084 | §11 与交易决策流水线的接口协议 | §11.1 知识注入接口 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 37 | L2190 | §11 与交易决策流水线的接口协议 | §11.2 效果反馈接口 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 38 | L2216 | §11 与交易决策流水线的接口协议 | §11.3 权重中心接口（v4.0新增，FinRL-X/Dnalyaw 2026） |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 39 | L2248 | §11 与交易决策流水线的接口协议 | §11.4 MLOps闭环（v4.0新增，AltStreet Quant 2.0 2025） |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 40 | L2283 | §12 分阶段实现路线 | §12.1 Phase 0: 手动学习系统 (MVP) |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 41 | L2306 | §12 分阶段实现路线 | §12.2 Phase 1: 半自动学习系统 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 42 | L2330 | §12 分阶段实现路线 | §12.3 Phase 2: 全自动学习系统 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 43 | L2354 | §12 分阶段实现路线 | §12.4 Phase 3: 自我进化学习系统 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 44 | L2381 | §13 成功标准 | §13.1 学习系统级成功标准 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 45 | L2392 | §13 成功标准 | §13.2 v4.0+新增功能成功标准 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 46 | L2495 | §13 成功标准 | §13.3 外部基准评估 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 47 | L2501 | §13 成功标准 | §13.4 失败指标 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 48 | L2518 | §14 行业前沿补充（2025-2026 自进化审查） | §14.0 二元裁定总表 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 49 | L2654 | §14 行业前沿补充（2025-2026 自进化审查） | §14.1 多模态知识采集前沿 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 50 | L2663 | §14 行业前沿补充（2025-2026 自进化审查） | §14.2 知识表示与推理 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 51 | L2672 | §14 行业前沿补充（2025-2026 自进化审查） | §14.3 因果发现与推断 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 52 | L2681 | §14 行业前沿补充（2025-2026 自进化审查） | §14.4 元学习与自进化机制 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 53 | L2695 | §14 行业前沿补充（2025-2026 自进化审查） | §14.5 模块化/组合式架构 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 54 | L2704 | §14 行业前沿补充（2025-2026 自进化审查） | §14.6 漂移检测与自适应 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 55 | L2714 | §14 行业前沿补充（2025-2026 自进化审查） | §14.7 自治系统安全与治理 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 56 | L2727 | §14 行业前沿补充（2025-2026 自进化审查） | §14.8 验证与回测方法论 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 57 | L2737 | §14 行业前沿补充（2025-2026 自进化审查） | §14.9 LLM在量化金融中的应用 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 58 | L2746 | §14 行业前沿补充（2025-2026 自进化审查） | §14.10 反馈闭环与持续学习 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 59 | L2757 | §14 行业前沿补充（2025-2026 自进化审查） | §14.11 第2轮深入发现（架构细节与新竞品） |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 60 | L2791 | §14 行业前沿补充（2025-2026 自进化审查） | §14.12 第3轮发现（头部机构实践+可解释AI+知识图谱+行业数据） |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |

## 安全架构.md (53 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | 文档边界声明 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 2 | L24 |  | 备注说明 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 3 | L38 |  | §0 架构定位 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 4 | L245 | §1 安全域划分 | §1.1 交易域 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 5 | L285 | §1 安全域划分 | §1.2 数据域 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 6 | L326 | §1 安全域划分 | §1.3 治理域 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 7 | L364 | §1 安全域划分 | §1.4 运维域 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 8 | L404 | §1 安全域划分 | §1.5 跨域交互规则 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 9 | L446 | §2 纵深防御6层 | §2.1 L1 网络与物理层 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 10 | L497 | §2 纵深防御6层 | §2.2 L2 主机与操作系统层 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 11 | L548 | §2 纵深防御6层 | §2.3 L3 应用与API层 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 12 | L692 | §2 纵深防御6层 | §2.4 L4 数据层 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 13 | L778 | §2 纵深防御6层 | §2.5 L5 身份与访问层 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 14 | L836 | §2 纵深防御6层 | §2.6 L6 监控与响应层 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 15 | L911 | §2 纵深防御6层 | §2.7 合规框架综合对标 [跨层章节·覆盖§2-§7] |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 16 | L973 | §3 IAM与访问控制 | §3.1 RBAC角色模型 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 17 | L1003 | §3 IAM与访问控制 | §3.2 ABAC策略引擎 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 18 | L1079 | §3 IAM与访问控制 | §3.3 一人开发场景下的IAM |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 19 | L1095 | §3 IAM与访问控制 | §3.4 Agent身份与权限 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 20 | L1155 | §4 密钥层级管理 | §4.1 三层密钥架构 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 21 | L1203 | §4 密钥层级管理 | §4.2 密钥轮换策略 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 22 | L1226 | §4 密钥层级管理 | §4.3 密钥保护机制 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 23 | L1257 | §4 密钥层级管理 | §4.4 后量子密码（PQC）迁移路线 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 24 | L1319 | §5 审计链 | §5.1 不可篡改操作日志 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 25 | L1408 | §5 审计链 | §5.2 审计日志查询 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 26 | L1436 | §5 审计链 | §5.3 区块链锚定时间戳（不能建，门禁条件见§14） |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 27 | L1466 | §6 Agent安全 | §6.1 对抗性韧性 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 28 | L1502 | §6 Agent安全 | §6.2 串谋检测 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 29 | L1598 | §6 Agent安全 | §6.3 涌现行为检测 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 30 | L1647 | §6 Agent安全 | §6.4 幻觉防护 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 31 | L1691 | §6 Agent安全 | §6.5 红队对抗框架 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 32 | L1757 | §6 Agent安全 | §6.6 Agent漏洞全景与防御升级 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 33 | L1817 | §6 Agent安全 | §6.7 记忆投毒防御 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 34 | L1911 | §7 内幕交易防护 | §7.1 数据分级与访问控制 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 35 | L1933 | §7 内幕交易防护 | §7.2 信息隔离墙（Ethical Wall，下文简称"隔离墙"） |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 36 | L2001 | §7 内幕交易防护 | §7.3 交易行为监控 |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 37 | L2061 | §7 内幕交易防护 | 三十一、协同交易行为检测模型（Coordinated Trading Detection Model |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 38 | L2115 | §7 内幕交易防护 | 五十四、信息不对称期与操纵行为检测模型（Information Asymmetry Period & |  |  | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 39 | L2275 | §14 遗留问题裁定 | §14.1 裁定总览 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 40 | L2294 | §14 遗留问题裁定 | §14.2 逐项裁定详情 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 41 | L2541 | §14 遗留问题裁定 | §14.3 不能建功能门禁清单 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 42 | L2558 | §15 功能域安全模块补全 | §15.1 供应链安全模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 43 | L2585 | §15 功能域安全模块补全 | §15.2 供应商风险管理模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 44 | L2600 | §15 功能域安全模块补全 | §15.3 安全策略即代码模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 45 | L2615 | §15 功能域安全模块补全 | §15.4 Agent安全扩展模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 46 | L2633 | §15 功能域安全模块补全 | §15.5 内容与数据安全模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 47 | L2643 | §15 功能域安全模块补全 | §15.6 运维安全模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 48 | L2656 | §15 功能域安全模块补全 | §15.7 跨域安全模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 49 | L2706 | §15 功能域安全模块补全 | §15.8 网络安全扩展模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 50 | L2713 | §15 功能域安全模块补全 | §15.9 合规安全模块补全 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 51 | L2732 | §15 功能域安全模块补全 | §15.10 卖出决策安全约束 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 52 | L2740 | §15 功能域安全模块补全 | §15.11 仿真安全约束 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |
| 53 | L2749 | §15 功能域安全模块补全 | §15.12 不能建功能门禁汇总 | D_SECURITY | risk_control | 否 | 排除 | 域禁止（安全架构主体不挂，仅MOD-INF-018已挂risk_control） |

## 数据架构.md (202 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | v3.0→v3.1 升级说明 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 2 | L21 |  | v2.1→v3.0 升级说明 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 3 | L42 | §0 数据架构唯一真源 | §0.1 数据架构总览（唯一真源） |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 4 | L163 | §0 数据架构唯一真源 | §0.2 数据流全景图（接入→处理→存储→服务→质量→治理） |  |  | 部分 | 归indicators(BM-SEL-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 5 | L314 | 第一部分：核心行情数据（A3-D1 数据接入域） | 1.1 数据源总览 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 6 | L368 | 第一部分：核心行情数据（A3-D1 数据接入域） | 1.2 miniQMT 3秒Tick数据 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 7 | L380 | 第一部分：核心行情数据（A3-D1 数据接入域） | 1.3 L0原始行情与L1标准化行情 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 8 | L406 | 第一部分：核心行情数据（A3-D1 数据接入域） | 1.4 行业最佳实践对标 | D_DATA/D_MKT_DATA | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 9 | L415 | 第一部分：核心行情数据（A3-D1 数据接入域） | 1.5 设计决策汇总 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 10 | L423 | 第一部分：核心行情数据（A3-D1 数据接入域） | 日内量能结构与订单流分析模型（Intraday Volume Structure & Order F | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-EXE-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 11 | L473 | 第一部分：核心行情数据（A3-D1 数据接入域） | 3秒级逆势资金流识别模块 | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-SEL-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 12 | L660 | 第一部分：核心行情数据（A3-D1 数据接入域） | 开盘竞价微结构分析模型（Opening Auction Microstructure Analysi | D_DATA/D_MKT_DATA | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 13 | L713 | 第二部分：基本面与另类数据（A3-D2 基本面域 + A3- | 2.1 基本面数据源 | D_ALT_DATA/D_FUNDAMENTAL_SIGNAL | stock_selection/research_incubation | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 14 | L728 | 第二部分：基本面与另类数据（A3-D2 基本面域 + A3- | 2.2 另类数据源 | D_ALT_DATA/D_FUNDAMENTAL_SIGNAL | stock_selection/research_incubation | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 15 | L743 | 第二部分：基本面与另类数据（A3-D2 基本面域 + A3- | 2.3 宏观与跨市场数据 | D_ALT_DATA/D_FUNDAMENTAL_SIGNAL | stock_selection/research_incubation | 部分 | 归indicators(BM-SEL-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 16 | L758 | 第二部分：基本面与另类数据（A3-D2 基本面域 + A3- | 2.4 行业最佳实践对标 | D_ALT_DATA/D_FUNDAMENTAL_SIGNAL | stock_selection/research_incubation | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 17 | L766 | 第二部分：基本面与另类数据（A3-D2 基本面域 + A3- | 2.5 设计决策汇总 | D_ALT_DATA/D_FUNDAMENTAL_SIGNAL | stock_selection/research_incubation | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 18 | L780 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 3.1 因子分类体系 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 19 | L790 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 3.2 因子值Schema | D_FACTOR | stock_selection | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 20 | L794 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 3.3 因子容量估算 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 21 | L798 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 3.4 行业最佳实践对标 | D_FACTOR | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 22 | L807 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 3.5 设计决策汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 23 | L815 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 统一技术图形识别引擎（Unified Technical Pattern Recognition E | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 24 | L904 | 第四部分：数据源质量评估 | 4.1 数据源质量评分 | D_DATA | stock_selection | 部分 | 归indicators(BM-BT-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 25 | L919 | 第四部分：数据源质量评估 | 4.2 各数据源关键质量风险 | D_DATA | stock_selection | 部分 | 归indicators(BM-RC-11) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 26 | L930 | 第四部分：数据源质量评估 | 4.3 行业最佳实践对标 | D_DATA | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 27 | L938 | 第四部分：数据源质量评估 | 4.4 设计决策汇总 | D_DATA | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 28 | L952 | 第五部分：数据源接入优先级与路线图 | 5.1 接入优先级 | D_DATA | stock_selection | 部分 | 归indicators(BM-BT-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 29 | L962 | 第五部分：数据源接入优先级与路线图 | 5.2 接入时间线 | D_DATA | stock_selection | 部分 | 归indicators(BM-BT-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 30 | L972 | 第五部分：数据源接入优先级与路线图 | 5.3 行业最佳实践对标 | D_DATA | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 31 | L980 | 第五部分：数据源接入优先级与路线图 | 5.4 设计决策汇总 | D_DATA | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 32 | L994 | 第六部分：知识图谱数据规划 | 6.1 图谱类型体系 | D_KNOWLEDGE | stock_selection | 部分 | 归indicators(BM-RES-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 33 | L1004 | 第六部分：知识图谱数据规划 | 6.2 远期规划 | D_KNOWLEDGE | stock_selection | 部分 | 归indicators(相关环节) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 34 | L1012 | 第六部分：知识图谱数据规划 | 6.3 行业最佳实践对标 | D_KNOWLEDGE | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 35 | L1020 | 第六部分：知识图谱数据规划 | 6.4 设计决策汇总 | D_KNOWLEDGE | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 36 | L1037 | §7 数据存储架构 | §7.1 三层存储架构 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(存储基础设施)) |
| 37 | L1072 | §7 数据存储架构 | §7.2 容量规划 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(存储基础设施)) |
| 38 | L1080 | §7 数据存储架构 | §7.3 生命周期管理 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(存储基础设施)) |
| 39 | L1093 | §7 数据存储架构 | §7.4 备份策略 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(存储基础设施)) |
| 40 | L1110 | §7 数据存储架构 | §7.5 行业最佳实践对标 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(存储基础设施)) |
| 41 | L1119 | §7 数据存储架构 | §7.6 设计决策汇总 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(存储基础设施)) |
| 42 | L1138 | §8 数据流动路径 | §8.1 L0→L6 全链路规格 | D_DATA | stock_selection | 部分 | 归indicators(BM-POS-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 43 | L1154 | §8 数据流动路径 | §8.2 批流分离设计 | D_DATA | stock_selection | 部分 | 归indicators(BM-RC-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 44 | L1165 | §8 数据流动路径 | §8.3 新鲜度检查点与延迟预算 | D_DATA | stock_selection | 部分 | 归indicators(BM-RC-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 45 | L1179 | §8 数据流动路径 | §8.4 行业最佳实践对标 | D_DATA | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 46 | L1188 | §8 数据流动路径 | §8.5 设计决策汇总 | D_DATA | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 47 | L1206 | §9 数据血缘与可追溯性 | §9.1 血缘链全景 | D_DATA_GOV | research_incubation | 否 | 排除 | 非作战动作(非作战动作(血缘)) |
| 48 | L1229 | §9 数据血缘与可追溯性 | §9.2 列级血缘 | D_DATA_GOV | research_incubation | 否 | 排除 | 非作战动作(非作战动作(血缘)) |
| 49 | L1243 | §9 数据血缘与可追溯性 | §9.3 OpenLineage标准适配 | D_DATA_GOV | research_incubation | 否 | 排除 | 非作战动作(非作战动作(血缘)) |
| 50 | L1255 | §9 数据血缘与可追溯性 | §9.4 MVP与完整实现路线 | D_DATA_GOV | research_incubation | 否 | 排除 | 非作战动作(非作战动作(血缘)) |
| 51 | L1264 | §9 数据血缘与可追溯性 | §9.5 行业最佳实践对标 | D_DATA_GOV | research_incubation | 否 | 排除 | 非作战动作(非作战动作(血缘)) |
| 52 | L1273 | §9 数据血缘与可追溯性 | §9.6 设计决策汇总 | D_DATA_GOV | research_incubation | 否 | 排除 | 非作战动作(非作战动作(血缘)) |
| 53 | L1293 | §10 数据质量SLA与治理 | §10.1 数据质量五维度定义（ISO 8000对齐） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 54 | L1318 | §10 数据质量SLA与治理 | §10.1.1 完整性（Completeness） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 55 | L1340 | §10 数据质量SLA与治理 | §10.1.2 准确性（Accuracy） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 56 | L1362 | §10 数据质量SLA与治理 | §10.1.3 一致性（Consistency） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 57 | L1383 | §10 数据质量SLA与治理 | §10.1.4 及时性（Timeliness） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 58 | L1405 | §10 数据质量SLA与治理 | §10.1.5 可用性（Availability） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 59 | L1426 | §10 数据质量SLA与治理 | §10.2 SLA分级体系 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 60 | L1460 | §10 数据质量SLA与治理 | §10.2.1 P0 关键数据SLA | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 61 | L1479 | §10 数据质量SLA与治理 | §10.2.2 P1 重要数据SLA | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 62 | L1499 | §10 数据质量SLA与治理 | §10.2.3 P2 背景数据SLA | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 63 | L1520 | §10 数据质量SLA与治理 | §10.3 自动化质量检查流水线 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 64 | L1559 | §10 数据质量SLA与治理 | §10.3.1 盘前质量检查（08:00-09:15） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 65 | L1603 | §10 数据质量SLA与治理 | §10.3.2 盘中实时监控（09:30-15:00） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 66 | L1641 | §10 数据质量SLA与治理 | §10.3.3 盘后一致性校验（15:00-17:00） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 67 | L1695 | §10 数据质量SLA与治理 | §10.4 违约处理流程 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 68 | L1722 | §10 数据质量SLA与治理 | §10.4.1 检测（Detect） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 69 | L1731 | §10 数据质量SLA与治理 | §10.4.2 告警（Alert） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 70 | L1739 | §10 数据质量SLA与治理 | §10.4.3 降级（Degrade） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 71 | L1751 | §10 数据质量SLA与治理 | §10.4.4 修复（Repair） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 72 | L1761 | §10 数据质量SLA与治理 | §10.4.5 验证（Verify） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 73 | L1774 | §10 数据质量SLA与治理 | §10.5 数据质量记分卡 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 74 | L1811 | §10 数据质量SLA与治理 | §10.5.1 评分规则 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 75 | L1823 | §10 数据质量SLA与治理 | §10.5.2 记分卡更新频率 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 76 | L1833 | §10 数据质量SLA与治理 | §10.5.3 记分卡数据模型 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 77 | L1851 | §10 数据质量SLA与治理 | §10.6 与A2治理架构的关系 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 78 | L1881 | §10 数据质量SLA与治理 | §10.6.1 职责边界 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 79 | L1895 | §10 数据质量SLA与治理 | §10.6.2 协作流程 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 80 | L1921 | §10 数据质量SLA与治理 | §10.7 行业最佳实践对标 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 81 | L1936 | §10 数据质量SLA与治理 | §10.8 技术选型（适配单机约束） | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 82 | L1949 | §10 数据质量SLA与治理 | §10.9 设计决策汇总 | D_DATA_GOV |  | 否 | 排除 | 非作战动作(非作战动作(SLA)) |
| 83 | L1972 | §11 特征存储架构 | §11.1 双存储架构 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 84 | L2026 | §11 特征存储架构 | §11.1.1 离线存储（Offline Store） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 85 | L2116 | §11 特征存储架构 | §11.1.2 在线存储（Online Store） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 86 | L2173 | §11 特征存储架构 | §11.2 特征注册表（Feature Registry） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 87 | L2206 | §11 特征存储架构 | §11.2.1 因子元数据（Metadata） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-EXE-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 88 | L2225 | §11 特征存储架构 | §11.2.2 数据血缘（Lineage） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RC-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 89 | L2245 | §11 特征存储架构 | §11.2.3 质量指标（Quality） | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 90 | L2260 | §11 特征存储架构 | §11.2.4 服务状态（Status） | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 91 | L2272 | §11 特征存储架构 | §11.2.5 版本历史（Version History） | D_FACTOR | stock_selection | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 92 | L2289 | §11 特征存储架构 | §11.3 训练-服务一致性保证 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-REC-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 93 | L2342 | §11 特征存储架构 | §11.3.1 单一定义原则详解 | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 94 | L2382 | §11 特征存储架构 | §11.3.2 PIT正确性详解 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-RES-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 95 | L2407 | §11 特征存储架构 | §11.3.3 版本对齐详解 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 96 | L2440 | §11 特征存储架构 | §11.4 特征生命周期 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 97 | L2486 | §11 特征存储架构 | §11.4.1 各阶段详细说明 | D_FACTOR | stock_selection | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 98 | L2501 | §11 特征存储架构 | §11.4.2 生命周期事件 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-SEL-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 99 | L2517 | §11 特征存储架构 | §11.5 与D-FACTOR域的关系 | D_FACTOR | stock_selection | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 100 | L2544 | §11 特征存储架构 | §11.5.1 职责边界 | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 101 | L2561 | §11 特征存储架构 | §11.6 行业最佳实践对标 | D_FACTOR | stock_selection | 否 | 排除 | 纯引用/外部对标，非本系统作战内容（决策树①） |
| 102 | L2577 | §11 特征存储架构 | §11.7 技术选型（适配单机约束） | D_FACTOR | stock_selection | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 103 | L2601 | §11 特征存储架构 | §11.8 设计决策汇总 | D_FACTOR | stock_selection | 部分 | 归indicators(BM-BUY-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 104 | L2624 | §12 事件溯源架构 | §12.1 事件溯源核心概念 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 105 | L2658 | §12 事件溯源架构 | §12.1.1 保存事件而非状态 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 106 | L2672 | §12 事件溯源架构 | §12.1.2 状态重建 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 107 | L2702 | §12 事件溯源架构 | §12.1.3 快照优化 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 108 | L2733 | §12 事件溯源架构 | §12.2 事件类型定义 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 109 | L2765 | §12 事件溯源架构 | §12.2.1 行情事件（TickEvent） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 110 | L2774 | §12 事件溯源架构 | §12.2.2 信号事件（SignalEvent） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 111 | L2783 | §12 事件溯源架构 | §12.2.3 决策事件（DecisionEvent） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 112 | L2792 | §12 事件溯源架构 | §12.2.4 执行事件（ExecutionEvent） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 113 | L2801 | §12 事件溯源架构 | §12.2.5 风控事件（RiskEvent） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 114 | L2810 | §12 事件溯源架构 | §12.2.6 系统事件（SystemEvent） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 115 | L2822 | §12 事件溯源架构 | §12.3 Event Store设计 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 116 | L2882 | §12 事件溯源架构 | §12.3.1 事件Schema（Parquet列定义） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 117 | L2897 | §12 事件溯源架构 | §12.3.2 幂等保证 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 118 | L2920 | §12 事件溯源架构 | §12.3.3 容量估算 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 119 | L2939 | §12 事件溯源架构 | §12.4 CQRS分离 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 120 | L2988 | §12 事件溯源架构 | §12.4.1 写端（Command Side） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 121 | L3008 | §12 事件溯源架构 | §12.4.2 读端（Query Side） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 122 | L3038 | §12 事件溯源架构 | §12.4.3 最终一致性 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 123 | L3051 | §12 事件溯源架构 | §12.5 快照策略 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 124 | L3098 | §12 事件溯源架构 | §12.5.1 快照Schema | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 125 | L3122 | §12 事件溯源架构 | §12.5.2 快照生成流程 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 126 | L3144 | §12 事件溯源架构 | §12.6 事件回放场景 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 127 | L3148 | §12 事件溯源架构 | §12.6.1 系统崩溃后状态恢复 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 128 | L3158 | §12 事件溯源架构 | §12.6.2 策略参数变更后重新计算 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 129 | L3181 | §12 事件溯源架构 | §12.6.3 合规审计时重建历史状态 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 130 | L3205 | §12 事件溯源架构 | §12.6.4 其他回放场景 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 131 | L3217 | §12 事件溯源架构 | §12.7 与A9运维架构的关系 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 132 | L3255 | §12 事件溯源架构 | §12.7.1 灾备恢复流程 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 133 | L3283 | §12 事件溯源架构 | §12.7.2 恢复演练计划 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 134 | L3294 | §12 事件溯源架构 | §12.8 行业最佳实践对标 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 135 | L3309 | §12 事件溯源架构 | §12.9 技术选型（适配单机约束） | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 136 | L3322 | §12 事件溯源架构 | §12.10 设计决策汇总 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(事件溯源)) |
| 137 | L3343 | §13 Point-in-Time一致性保证 | §13.1 三条公理 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 138 | L3372 | §13 Point-in-Time一致性保证 | §13.2 三平面统一 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 139 | L3382 | §13 Point-in-Time一致性保证 | §13.3 AS OF JOIN实现 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 140 | L3406 | §13 Point-in-Time一致性保证 | §13.4 Embargo期 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 141 | L3417 | §13 Point-in-Time一致性保证 | §13.5 PIT校验规则 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 142 | L3427 | §13 Point-in-Time一致性保证 | §13.6 行业最佳实践对标 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 143 | L3437 | §13 Point-in-Time一致性保证 | §13.7 设计决策汇总 | D_DATA |  | 否 | 排除 | 非作战动作(非作战动作(PIT)) |
| 144 | L3456 | §14 数据安全与合规约束 | §14.1 四级数据分类 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 145 | L3492 | §14 数据安全与合规约束 | §14.2 RBAC访问控制 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 146 | L3505 | §14 数据安全与合规约束 | §14.3 加密体系 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 147 | L3516 | §14 数据安全与合规约束 | §14.4 AI脱敏管道 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 148 | L3537 | §14 数据安全与合规约束 | §14.5 审计日志 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 149 | L3549 | §14 数据安全与合规约束 | §14.6 行业最佳实践对标 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 150 | L3559 | §14 数据安全与合规约束 | §14.7 设计决策汇总 | D_DATA_SEC | research_incubation | 否 | 排除 | 非作战动作(非作战动作) |
| 151 | L3578 | §15 可扩展性与演进性 | §15.1 数据源接入流程 |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 152 | L3602 | §15 可扩展性与演进性 | §15.2 Schema演进 |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 153 | L3614 | §15 可扩展性与演进性 | §15.3 存储扩展路径 |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 154 | L3646 | §15 可扩展性与演进性 | §15.4 技术栈演进 |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 155 | L3660 | §15 可扩展性与演进性 | §15.5 ADR（架构决策记录） |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 156 | L3673 | §15 可扩展性与演进性 | §15.6 行业最佳实践对标 |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 157 | L3685 | §15 可扩展性与演进性 | §15.7 设计决策汇总 |  |  | 否 | 排除 | 非作战动作(非作战动作(演进)) |
| 158 | L3703 | §16 2025-2026前沿实践对标与二元建设结论 | §16.1 清单1：数据源覆盖与冗余 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 159 | L3711 | §16 2025-2026前沿实践对标与二元建设结论 | §16.2 清单2：数据质量框架完整性 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 160 | L3718 | §16 2025-2026前沿实践对标与二元建设结论 | §16.3 清单3：Feature Store架构成熟度 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 161 | L3727 | §16 2025-2026前沿实践对标与二元建设结论 | §16.4 清单4：Event Sourcing与CQRS完整性 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 162 | L3735 | §16 2025-2026前沿实践对标与二元建设结论 | §16.5 清单5：Point-in-Time一致性保障 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 163 | L3743 | §16 2025-2026前沿实践对标与二元建设结论 | §16.6 清单6：数据安全与合规 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 164 | L3750 | §16 2025-2026前沿实践对标与二元建设结论 | §16.7 清单7：数据血缘与可追溯性 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 165 | L3758 | §16 2025-2026前沿实践对标与二元建设结论 | §16.8 清单8：存储架构与可扩展性 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 166 | L3767 | §16 2025-2026前沿实践对标与二元建设结论 | §16.9 清单9：数据流与延迟优化 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 167 | L3775 | §16 2025-2026前沿实践对标与二元建设结论 | §16.10 清单10：新兴技术与实践 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 168 | L3784 | §16 2025-2026前沿实践对标与二元建设结论 | §16.11 建设结论汇总 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 169 | L3838 | §16 2025-2026前沿实践对标与二元建设结论 | §16.12 ✅能建项目实施路线 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 170 | L3911 | §16 2025-2026前沿实践对标与二元建设结论 | §16.13 硬边界门禁路线图 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 171 | L3950 | §16 2025-2026前沿实践对标与二元建设结论 | §16.14 第二轮搜索补充发现 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 172 | L3960 | §16 2025-2026前沿实践对标与二元建设结论 | §16.15 第三轮搜索补充发现 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 173 | L3970 | §16 2025-2026前沿实践对标与二元建设结论 | §16.16 第四轮搜索补充发现 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 174 | L3982 | §16 2025-2026前沿实践对标与二元建设结论 | §16.17 自进化循环审查报告 |  |  | 否 | 排除 | 非作战动作(非作战动作(对标)) |
| 175 | L4048 | §17 依赖图域模块补充 | §17.1 D-DATA 数据域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 176 | L4085 | §17 依赖图域模块补充 | §17.2 D-DATA-ENG 数据工程域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 177 | L4099 | §17 依赖图域模块补充 | §17.3 D-ALT-DATA 另类数据域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 178 | L4112 | §17 依赖图域模块补充 | §17.4 D-FACTOR 因子域缺失模块 |  |  | 部分 | 归indicators(BM-BUY-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 179 | L4119 | §17 依赖图域模块补充 | §17.5 D-ML-TRAIN/D-ML-SERVE 训练/推理域缺失模块 |  |  | 部分 | 归indicators(BM-SEL-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 180 | L4126 | §17 依赖图域模块补充 | §17.6 D-COMPLIANCE 合规监管域缺失模块 |  |  | 部分 | 归indicators(BM-EXE-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 181 | L4133 | §17 依赖图域模块补充 | §17.7 D-SIMULATION 仿真域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 182 | L4139 | §17 依赖图域模块补充 | §17.8 D-SECURITY 安全域缺失模块 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 183 | L4146 | §17 依赖图域模块补充 | §17.9 D-GOVERNANCE 治理域缺失模块 |  |  | 部分 | 归indicators(BM-SEL-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 184 | L4152 | §17 依赖图域模块补充 | §17.10 D-KNOWLEDGE 知识域缺失模块 |  |  | 部分 | 归indicators(BM-BT-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 185 | L4159 | §17 依赖图域模块补充 | §17.11 跨域基础设施缺失模块 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 186 | L4169 | §17 依赖图域模块补充 | §17.12 D-SIGNAL 信号域缺失模块 |  |  | 部分 | 归indicators(BM-REC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 187 | L4180 | §17 依赖图域模块补充 | §17.13 D-RISK 风控域缺失模块 |  |  | 部分 | 归indicators(BM-SIM-07) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 188 | L4190 | §17 依赖图域模块补充 | §17.14 D-EX-CORE 执行核心域缺失模块 |  |  | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 189 | L4200 | §17 依赖图域模块补充 | §17.15 D-REPORTING 报告域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 190 | L4208 | §17 依赖图域模块补充 | §17.16 D-CROSS-ASSET 跨资产跨市场域缺失模块 |  |  | 部分 | 归indicators(BM-SEL-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 191 | L4214 | §17 依赖图域模块补充 | §17.17 D-INFRA-RUNTIME 运行时基础设施域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 192 | L4227 | §17 依赖图域模块补充 | §17.18 D-INFRA-OPS 运维基础设施域缺失模块 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 193 | L4236 | §17 依赖图域模块补充 | §17.19 D-INTEGRATION 集成域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 194 | L4243 | §17 依赖图域模块补充 | §17.20 D-RESEARCH 研究基础设施域缺失模块 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 195 | L4254 | §17 依赖图域模块补充 | §17.21 D-AUT-CORE 自治核心域缺失模块 |  |  | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 196 | L4266 | §17 依赖图域模块补充 | §17.22 D-AUT-PERM 自治保护域缺失模块 |  |  | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 197 | L4274 | §17 依赖图域模块补充 | §17.23 D-TRADING 交易运营域缺失模块 |  |  | 部分 | 归indicators(BM-REC-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 198 | L4283 | §17 依赖图域模块补充 | §17.24 D-OPS 运维域缺失模块 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 199 | L4291 | §17 依赖图域模块补充 | §17.25 低相关域声明 |  |  | 部分 | 归indicators(BM-SEL-20) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 200 | L4301 | §17 依赖图域模块补充 | §17.26 补充模块建设结论汇总 |  |  | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 201 | L4311 | §17 依赖图域模块补充 | §16.18 A1§29.4 迁移内容：时序数据库与分层存储架构（历史参考） |  |  | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 202 | L4317 | §17 依赖图域模块补充 | §29.4 时序数据库与分层存储架构 |  |  | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |

## 治理架构.md (39 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | 📌 蓝图建设状态备注说明 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 2 | L17 |  | 📌 文档边界声明 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 3 | L31 |  | 📌 §0 架构定位 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 4 | L65 |  | §0.3 治理架构唯一真源总览图 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 5 | L150 | §1 治理三层边界 | §1.1 Policy层（策略层） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 6 | L204 | §1 治理三层边界 | §1.2 Factory层（工厂层） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 7 | L218 | §1 治理三层边界 | §1.3 Runtime层（运行时层） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 8 | L238 | §1 治理三层边界 | §1.4 三层交互协议 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 9 | L267 | §1 治理三层边界 | §1.5 治理流全景图（规则定义→编译→发布→执行→监控→反馈→纠正→优化） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 10 | L438 | §1 治理三层边界 | 动态信号权重模型（Dynamic Signal Weighting via Bayesian Mod |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 11 | L494 | §2 变更审批流 | §2.1 变更分级（5级） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 12 | L506 | §2 变更审批流 | §2.2 审批链 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 13 | L570 | §2 变更审批流 | §2.3 门禁触发规则 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 14 | L590 | §3 架构漂移检测与纠正闭环 | §3.1 漂移类型（5类） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 15 | L604 | §3 架构漂移检测与纠正闭环 | §3.2 检测机制 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 16 | L629 | §3 架构漂移检测与纠正闭环 | §3.3 纠正闭环 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 17 | L669 | §3 架构漂移检测与纠正闭环 | 交易绩效归因与策略退化检测模型（Performance Attribution & Strategy |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 18 | L711 | §4 AI自治边界 | §4.1 三级自治分类 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 19 | L723 | §4 AI自治边界 | §4.2 自治边界与能力定位书的映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 20 | L741 | §4 AI自治边界 | §4.3 Agentic Drift防护（基于AISI 2026研究） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 21 | L770 | §5 治理激活时序 | §5.1 治理能力成熟度（5级） |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 22 | L784 | §5 治理激活时序 | §5.2 激活甘特图 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 23 | L817 | §6 蓝图-代码-文档三方对齐机制 | §6.1 三方对齐检查 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 24 | L846 | §6 蓝图-代码-文档三方对齐机制 | §6.2 一致性校验规则 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 25 | L870 | §7 治理自动化 | §7.1 自动化检查器 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 26 | L896 | §7 治理自动化 | §7.2 治理脚本 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 27 | L981 | §11 角色与交互旅程 | 角色交互旅程 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 28 | L1219 | §16 监管合规映射 | §16.1 中国A股程序化交易监管映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 29 | L1246 | §16 监管合规映射 | §16.2 ESRB系统性风险防护映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 30 | L1262 | §16 监管合规映射 | §16.3 A股监管合规日历 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 31 | L1284 | §16 监管合规映射 | §16.4 EU AI Act合规预留 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 32 | L1308 | §17 遗留问题裁定记录 | §17.1 裁定汇总 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 33 | L1323 | §17 遗留问题裁定记录 | §17.2 逐项裁定详情 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 34 | L1430 | §17 遗留问题裁定记录 | §17.3 门禁条件索引 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 35 | L1483 | §18 治理域模块映射与建设状态 | §18.1 D-GOVERNANCE子模块映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 36 | L1514 | §18 治理域模块映射与建设状态 | §18.2 基础设施层跨域治理模块映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 37 | L1558 | §18 治理域模块映射与建设状态 | §18.3 业务域跨域治理子模块映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 38 | L1621 | §18 治理域模块映射与建设状态 | §18.4 跨域治理契约与事件映射 |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |
| 39 | L1637 | §18 治理域模块映射与建设状态 | §18.5 场外规划模块（共265模块：86依赖基础设施层GATE-FPGA，152依赖GATE-S |  |  | 否 | 排除 | 禁域/元文档(治理架构.md不挂作战地图) |

## 运维架构.md (64 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | 📌 蓝图备注说明 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 2 | L18 |  | 📌 文档边界声明 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 3 | L32 |  | 📌 §0 架构定位 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 4 | L183 |  | §0.4 交易时段定义（权威） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 5 | L204 | §1 运行时架构 | §1.1 NSSM+5进程架构 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 6 | L294 | §1 运行时架构 | §1.2 Redis共享状态设计 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 7 | L358 | §1 运行时架构 | §1.3 GPU调度策略 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 8 | L443 | §2 三平面拓扑 | §2.1 三平面架构总览 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 9 | L483 | §2 三平面拓扑 | §2.2 Hot平面（<10ms） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 10 | L508 | §2 三平面拓扑 | 买入后即时验证与快速纠错模型（Post-Entry Instant Validation & Qui |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 11 | L534 | §2 三平面拓扑 | §2.3 Warm平面（10ms~1s） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 12 | L558 | §2 三平面拓扑 | §2.4 Cold平面（>1s） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 13 | L591 | §2 三平面拓扑 | §2.5 平面间隔离与延迟预算汇总 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 14 | L613 | §3 AI自治运维闭环 | §3.1 四阶段闭环架构 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 15 | L697 | §3 AI自治运维闭环 | §3.2 自治成熟度分级 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 16 | L733 | §3 AI自治运维闭环 | §3.3 自治策略库 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 17 | L746 | §3 AI自治运维闭环 | §3.4 自治熔断条件 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 18 | L787 | §4 应急保命轨 | §4.0 降级阈值速查表 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 19 | L799 | §4 应急保命轨 | §4.1 降级等级定义 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 20 | L837 | §4 应急保命轨 | §4.2 触发条件矩阵 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 21 | L857 | §4 应急保命轨 | §4.3 保命规则集（L2最简规则） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 22 | L885 | §4 应急保命轨 | §4.4 降级动作清单 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 23 | L896 | §4 应急保命轨 | §4.5 Knight Capital教训与防护 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 24 | L919 | §4 应急保命轨 | §4.6 熔断器模式（Circuit Breaker） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 25 | L953 | §4 应急保命轨 | 系统性风险分级预警与尾部风险管理模型（Systemic Risk Tiered Alert & Ta |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 26 | L983 | §5 灾备架构 | §5.1 RTO/RPO分级表 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 27 | L998 | §5 灾备架构 | §5.1.1 交易系统灾备核心差异——未平仓头寸问题（Open Position Problem） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 28 | L1011 | §5 灾备架构 | §5.2 D→E盘双副本策略 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 29 | L1051 | §5 灾备架构 | §5.2.2 备份黄金律——3-2-1-1-0规则 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 30 | L1067 | §5 灾备架构 | §5.3 断电断网恢复 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 31 | L1076 | §5 灾备架构 | §5.4 策略状态机断点恢复 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 32 | L1107 | §5 灾备架构 | §5.5 数据恢复流程 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 33 | L1117 | §5 灾备架构 | §5.6 灾备演练计划 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 34 | L1128 | §5 灾备架构 | §5.7 混沌工程实践 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 35 | L1151 | §6 监控体系 | §6.1 指标体系 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 36 | L1189 | §6 监控体系 | §6.2 告警分级与收敛 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 37 | L1241 | §6 监控体系 | §6.3 仪表盘设计 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 38 | L1254 | §6 监控体系 | §6.3.1 OpenTelemetry分布式追踪 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 39 | L1271 | §6 监控体系 | §6.4 异常检测 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 40 | L1293 | §6 监控体系 | §6.5 SLO定义 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 41 | L1307 | §7 变更管理 | §7.1 灰度发布流程 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 42 | L1349 | §7 变更管理 | §7.2 金丝雀验证 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 43 | L1360 | §7 变更管理 | §7.3 回滚策略 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 44 | L1389 | §7 变更管理 | §7.4 交易时段变更冻结 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 45 | L1399 | §7 变更管理 | §7.5 依赖库升级流程 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 46 | L1441 | §7 变更管理 | §7.6 Knight Capital教训与变更管理 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 47 | L1451 | §8 功能域映射 | §8.1 功能域清单 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 48 | L1466 | §8 功能域映射 | §8.2 运维架构组件→功能域映射 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 49 | L1480 | §8 功能域映射 | §8.3 运维相关模块清单（场外草稿区+场内项目交叉索引） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 50 | L1700 | §8 功能域映射 | §8.4 A1§29.1 迁移内容：多进程隔离与运行时架构（概念级） |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 51 | L1704 | §8 功能域映射 | §29.1 多进程隔离与运行时架构 |  |  | 否 | 排除 | 域禁止（运维架构主体不挂，仅D_OPS在reconciliation挂） |
| 52 | L1852 | §14 硬边界裁定书 | 裁定总览 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 53 | L1872 | §14 硬边界裁定书 | §14.1 进程守护方案 — ✅ 能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 54 | L1887 | §14 硬边界裁定书 | §14.2 GPU MPS多进程并发 — ❌ 不能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 55 | L1902 | §14 硬边界裁定书 | §14.3 eBPF for Windows内核监控 — ❌ 不能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 56 | L1917 | §14 硬边界裁定书 | §14.4 双机热备 — ❌ 不能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 57 | L1933 | §14 硬边界裁定书 | §14.5 AI自治L3/L4级 — ✅ 能建（渐进式） |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 58 | L1958 | §14 硬边界裁定书 | §14.6 混沌工程 — ✅ 能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 59 | L1976 | §14 硬边界裁定书 | §14.7 DORA合规正式对标 — ❌ 不能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 60 | L1991 | §14 硬边界裁定书 | §14.8 TNR安全规范 — ✅ 能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 61 | L1999 | §14 硬边界裁定书 | §14.9 GPU模型热交换 — ✅ 能建(进程级) / ❌ 不能建(Run:ai式) |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 62 | L2008 | §14 硬边界裁定书 | §14.10 熔断器模式 — ✅ 能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 63 | L2014 | §14 硬边界裁定书 | §14.11 OpenTelemetry分布式追踪 — ✅ 能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 64 | L2021 | §14 硬边界裁定书 | §14.12 Redis集群/哨兵 — ❌ 不能建 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |

## 集成架构.md (94 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L12 |  | 📌 文档边界声明 |  |  | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 2 | L35 |  | 📌 §0 架构定位 |  |  | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 3 | L307 | §1 外部系统交互矩阵 | §1.1 交易系统（miniQMT） | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 4 | L358 | §1 外部系统交互矩阵 | §1.2 数据源（iFind/tushare/另类数据） | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 5 | L402 | §1 外部系统交互矩阵 | 隔夜全球市场传导与事件影响评估模型（Overnight Global Market Contagio | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 6 | L440 | §1 外部系统交互矩阵 | 北向资金流向与Smart Money信号模型（Northbound Capital Flow & S | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 7 | L466 | §1 外部系统交互矩阵 | §1.3 AI服务（LLM API/Whisper） | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 8 | L522 | §1 外部系统交互矩阵 | §1.4 其他系统 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 9 | L537 | §2 集成风格 | §2.1 同步调用 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 10 | L556 | §2 集成风格 | §2.2 异步消息 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 11 | L573 | §2 集成风格 | §2.3 事件驱动 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 12 | L592 | §2 集成风格 | §2.4 批量导入 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 13 | L608 | §2 集成风格 | §2.5 集成风格决策矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 14 | L628 | §3 接口契约治理 | §3.1 API版本管理 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 15 | L659 | §3 接口契约治理 | §3.2 兼容性策略 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 16 | L696 | §3 接口契约治理 | §3.3 降级策略 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 17 | L730 | §4 数据源故障降级 | §4.1 三源互补 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 18 | L779 | §4 数据源故障降级 | §4.2 自动切换 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 19 | L812 | §4 数据源故障降级 | §4.3 数据质量降级 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 20 | L838 | §5 MCP协议集成 | §5.1 MCP在集成架构中的定位 | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 21 | L848 | §5 MCP协议集成 | §5.2 MCP架构适配 | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 22 | L883 | §5 MCP协议集成 | §5.3 MCP 2026-07-28规范适配 | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 23 | L903 | §5 MCP协议集成 | §5.4 MCP集成路线图 | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 24 | L914 | §5 MCP协议集成 | §5A A2A协议集成（Agent-to-Agent） | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 25 | L956 | §6 隔离策略 | §6.1 熔断器 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 26 | L1013 | §6 隔离策略 | §6.2 舱壁隔离 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 27 | L1048 | §6 隔离策略 | §6.3 超时与重试 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 28 | L1083 | §6 隔离策略 | §6.4 Kill-Switch多层防御 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 29 | L1137 | §6 隔离策略 | §6.5 混沌工程验证 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 30 | L1194 | §8 硬边界与约束 | §8.1 集成硬边界（HB-01~HB-13） |  |  | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 31 | L1212 | §8 硬边界与约束 | §8.2 AI行为安全边界（集成视角） |  |  | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 32 | L1228 | §8 硬边界与约束 | §8.3 硬边界与AI安全边界交叉引用 |  |  | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 33 | L1335 | §13 集成架构时序视图 | §13.1 交易日集成时序 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 34 | L1361 | §13 集成架构时序视图 | §13.2 故障场景时序 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 35 | L1428 | §15 遗留问题裁定 | §15.1 QP-01：交易通道熔断自动恢复 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 36 | L1440 | §15 遗留问题裁定 | §15.2 QP-02：MCP交易执行Server | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 37 | L1452 | §15 遗留问题裁定 | §15.3 QP-03：iFind QPS=20个人版限制 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 38 | L1464 | §15 遗留问题裁定 | §15.4 QP-04：混沌工程环境选择 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 39 | L1476 | §15 遗留问题裁定 | §15.5 QP-05：三源仲裁品种差异化阈值 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 40 | L1488 | §15 遗留问题裁定 | §15.6 QP-06：OpenTelemetry 2.0可观测性标准 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 41 | L1500 | §15 遗留问题裁定 | §15.7 QP-07：KS-L4硬停机后降额运行1天 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 42 | L1512 | §15 遗留问题裁定 | §15.8 QP-08：API网关统一入口 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 43 | L1524 | §15 遗留问题裁定 | §15.9 QP-09：集成测试框架 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 44 | L1536 | §15 遗留问题裁定 | §15.10 QP-10：Python原生可观测性替代OTel | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 45 | L1548 | §15 遗留问题裁定 | §15.11 QP-11：四级限流架构 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 46 | L1560 | §15 遗留问题裁定 | §15.12 QP-12：下单执行Saga编排 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 47 | L1572 | §15 遗留问题裁定 | §15.13 QP-13：A2A协议集成 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 48 | L1582 | §15 遗留问题裁定 | §15.14 QP-14：集成闭环优化 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 49 | L1592 | §15 遗留问题裁定 | §15.15 QP-15：集成合规治理 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 50 | L1602 | §15 遗留问题裁定 | §15.16 QP-16：集成层灾备 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 51 | L1612 | §15 遗留问题裁定 | §15.17 QP-17：成本感知LLM路由 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 52 | L1622 | §15 遗留问题裁定 | §15.18 裁定总览 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 53 | L1652 | §16 集成可观测性 | §16.1 可观测性三支柱（Python原生实现） | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 54 | L1660 | §16 集成可观测性 | §16.2 集成SLI/SLO体系 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 55 | L1670 | §16 集成可观测性 | §16.3 集成可观测性实现矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 56 | L1687 | §17 集成安全纵深 | §17.1 集成层安全威胁矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 57 | L1697 | §17 集成安全纵深 | §17.2 集成层安全能力矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 58 | L1712 | §17 集成安全纵深 | §17.3 API密钥轮换SLA | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 59 | L1729 | §18 集成测试策略 | §18.1 集成测试分层架构 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 60 | L1738 | §18 集成测试策略 | §18.2 集成测试能力矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 61 | L1750 | §18 集成测试策略 | §18.3 集成测试铁律 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 62 | L1766 | §19 API网关设计 | §19.1 API网关定位 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 63 | L1774 | §19 API网关设计 | §19.2 API网关能力矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 64 | L1788 | §19 API网关设计 | §19.3 API网关四层架构 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 65 | L1829 | §20 集成容量规划与限流 | §20.1 集成容量规划 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 66 | L1839 | §20 集成容量规划与限流 | §20.2 降级容量预算 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 67 | L1850 | §20 集成容量规划与限流 | §20.3 四级限流架构 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 68 | L1859 | §20 集成容量规划与限流 | §20.4 限流与熔断协同 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 69 | L1872 | §21 数据一致性保证 | §21.1 数据一致性SLA | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 70 | L1881 | §21 数据一致性保证 | §21.2 下单执行Saga | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 71 | L1895 | §21 数据一致性保证 | §21.3 Saga设计原则 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 72 | L1958 | §24 集成闭环优化与自迭代 | §24.1 集成闭环反馈路径 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 73 | L1970 | §24 集成闭环优化与自迭代 | §24.2 集成闭环能力矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 74 | L1982 | §24 集成闭环优化与自迭代 | §24.3 集成闭环铁律 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 75 | L1998 | §25 集成架构增强与演进路线图 | §25.1 集成能力演进路线 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 76 | L2007 | §25 集成架构增强与演进路线图 | §25.2 协议演进管理 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 77 | L2016 | §25 集成架构增强与演进路线图 | §25.3 集成架构增强项 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 78 | L2032 | §25 集成架构增强与演进路线图 | §25.4 集成域知识注入接口 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 79 | L2049 | §26 集成合规治理 | §26.1 外部系统合规维度 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 80 | L2059 | §26 集成合规治理 | §26.2 合规网关层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 81 | L2073 | §26 集成合规治理 | §26.3 集成合规铁律 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 82 | L2090 | §27 集成层灾备与状态可重建性 | §27.1 集成层灾备场景 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 83 | L2103 | §27 集成层灾备与状态可重建性 | §27.2 状态可重建性矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 84 | L2114 | §27 集成层灾备与状态可重建性 | §27.3 集成层灾备能力矩阵 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 85 | L2126 | §27 集成层灾备与状态可重建性 | §27.4 集成层灾备铁律 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 86 | L2144 | §28 集成域子模块全景与蓝图映射 | §28.1 接口与契约层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 87 | L2154 | §28 集成域子模块全景与蓝图映射 | §28.2 服务通信与路由层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 88 | L2171 | §28 集成域子模块全景与蓝图映射 | §28.3 跨域事务与可靠性层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 89 | L2183 | §28 集成域子模块全景与蓝图映射 | §28.4 安全集成层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 90 | L2192 | §28 集成域子模块全景与蓝图映射 | §28.5 治理与合规集成层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 91 | L2203 | §28 集成域子模块全景与蓝图映射 | §28.6 运维集成层 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 92 | L2217 | §28 集成域子模块全景与蓝图映射 | §28.7 A2A与MCP协议层 | D_INTEGRATION | stock_selection/buy_flow | 部分 | 仅调用点锚点 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂）；本节属调用点范围 |
| 93 | L2224 | §28 集成域子模块全景与蓝图映射 | §28.8 SBOM供应链安全系列 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |
| 94 | L2233 | §28 集成域子模块全景与蓝图映射 | §28.9 蓝图建设状态汇总 | D_INTEGRATION | stock_selection/buy_flow | 否 | 排除 | 集成基础设施不挂（仅D_INTEGRATION在选股/买入挂） |

## 风险架构.md (50 H3)

| # | 行号 | H2章节 | H3标题 | 推断域 | 阶段 | 能挂? | 处理动作 | 排除理由 |
|---|------|--------|--------|--------|------|-------|---------|---------|
| 1 | L10 |  | 📌 蓝图与项目状态备注说明 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 2 | L17 |  | 📌 文档边界声明 |  |  | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 3 | L35 |  | 📌 §0 架构定位 |  |  | 否 | 排除 | 指针/注解/元信息章节，非作战内容（决策树①） |
| 4 | L336 | §1 风险分类体系 | §1.1 市场风险 | D_RISK | risk_control | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 5 | L355 | §1 风险分类体系 | 系统性风险分级预警与尾部风险管理模型（Systemic Risk Tiered Alert & Ta | D_RISK | risk_control | 部分 | 归indicators(BM-RC-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 6 | L381 | §1 风险分类体系 | §1.2 模型风险 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 7 | L412 | §1 风险分类体系 | §1.3 流动性风险 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 8 | L482 | §1 风险分类体系 | §1.4 操作风险 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-08) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 9 | L494 | §1 风险分类体系 | 买入后即时验证与快速纠错模型（Post-Entry Instant Validation & Qui | D_RISK | risk_control | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 10 | L518 | §1 风险分类体系 | §1.5 AI/Agent特有风险 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 11 | L580 | §1 风险分类体系 | §1.6 交易对手风险 | D_RISK | risk_control | 部分 | 归indicators(BM-EXE-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 12 | L591 | §1 风险分类体系 | §1.7 信用风险 | D_RISK | risk_control | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 13 | L608 | §2 风险度量方法 | §2.1 VaR/CVaR/ES | D_RISK | risk_control | 部分 | 归indicators(BM-RC-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 14 | L629 | §2 风险度量方法 | §2.2 压力测试与情景分析 | D_RISK | risk_control | 是 | 已覆盖(BM-RC-08-C) | 与现有环节 BM-RC-08-C 压力测试 等价/被其包含(sim=1.00) |
| 15 | L676 | §2 风险度量方法 | §2.3 密度感知VaR/共形VaR | D_RISK | risk_control | 部分 | 归indicators(BM-RC-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 16 | L724 | §3 风险否决权 | §3.1 否决规则 | D_RISK | risk_control/execution | 部分 | 归indicators(BM-RC-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 17 | L766 | §3 风险否决权 | §3.2 否决执行机制 | D_RISK | risk_control/execution | 部分 | 归indicators(BM-RC-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 18 | L814 | §3 风险否决权 | §3.3 否决与策略逻辑的隔离 | D_RISK | risk_control/execution | 部分 | 归indicators(BM-RES-09) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 19 | L840 | §3 风险否决权 | ATR动态止损与Bayesian参数优化模型（ATR Dynamic Stop-Loss & Bay | D_RISK | risk_control/execution | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 20 | L896 | §4 风险数据流 | §4.1 独立风险数据管道 | D_RISK | risk_control | 是 | 已覆盖(BM-RC-11) | 与现有环节 BM-RC-11 独立风险数据管道 等价/被其包含(sim=1.00) |
| 21 | L941 | §4 风险数据流 | §4.2 风险指标计算 | D_RISK | risk_control | 是 | 已覆盖(BM-RC-11-A) | 与现有环节 BM-RC-11-A 独立风险指标计算 等价/被其包含(sim=0.56) |
| 22 | L953 | §4 风险数据流 | §4.3 风险报告 | D_RISK | risk_control | 是 | 已覆盖(BM-REC-02-E) | 与现有环节 BM-REC-02-E 风险报告 等价/被其包含(sim=1.00) |
| 23 | L968 | §5 风险治理 | §5.1 风控规则变更审批流 | D_RISK | risk_control | 部分 | 归indicators(BM-EXE-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 24 | L988 | §5 风险治理 | §5.2 风控参数版本管理 | D_RISK | risk_control | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 25 | L1007 | §5 风险治理 | §5.3 风控审计 | D_RISK | risk_control | 部分 | 归indicators(BM-EXE-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 26 | L1024 | §6 A股合规规则（代管） | §6.1 不操纵市场 | D_COMPLIANCE | buy_flow | 部分 | 归indicators(BM-SIM-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 27 | L1077 | §6 A股合规规则（代管） | 信息不对称期与操纵行为检测模型（Information Asymmetry Period & Man | D_COMPLIANCE | buy_flow | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 28 | L1112 | §6 A股合规规则（代管） | §6.2 持仓限额 | D_COMPLIANCE | buy_flow | 部分 | 归indicators(BM-RC-02) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 29 | L1121 | §6 A股合规规则（代管） | §6.3 涨跌停约束 | D_COMPLIANCE | buy_flow | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 30 | L1146 | §6 A股合规规则（代管） | §6.4 A股风险日历 | D_COMPLIANCE | buy_flow | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 31 | L1169 | §7 漂移检测与风险闭环 | §7.1 事前PSI检测 | D_RISK/D_FBL_* | reconciliation/risk_control | 部分 | 归indicators(BM-RC-06) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 32 | L1180 | §7 漂移检测与风险闭环 | §7.2 事中在线适应 | D_RISK/D_FBL_* | reconciliation/risk_control | 部分 | 归indicators(BM-EXE-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 33 | L1190 | §7 漂移检测与风险闭环 | §7.3 事后重训触发 | D_RISK/D_FBL_* | reconciliation/risk_control | 部分 | 归indicators(BM-RC-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 34 | L1225 | §7 漂移检测与风险闭环 | 交易绩效归因与策略退化检测模型（Performance Attribution & Strategy | D_RISK/D_FBL_* | reconciliation/risk_control | 是 | 已覆盖(BM-REC-02-B) | 与现有环节 BM-REC-02-B 绩效归因 等价/被其包含(sim=1.00) |
| 35 | L1298 | §9 硬边界与约束 | §9.1 遗留问题裁定表 |  |  | 否 | 排除 | 硬边界/方法论/角色等元信息章节 |
| 36 | L1419 | §14 极端事件与黑天鹅 | §14.1 黑天鹅模式库 | D_RISK | risk_control | 是 | 已覆盖(BM-RC-12-A) | 与现有环节 BM-RC-12-A 黑天鹅模式库 等价/被其包含(sim=1.00) |
| 37 | L1443 | §14 极端事件与黑天鹅 | §14.2 跨市场传导模型 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 38 | L1460 | §14 极端事件与黑天鹅 | §14.3 流动性危机模拟 | D_RISK | risk_control | 是 | 已覆盖(BM-RC-12-C) | 与现有环节 BM-RC-12-C 流动性危机模拟 等价/被其包含(sim=1.00) |
| 39 | L1468 | §14 极端事件与黑天鹅 | §14.4 反向压力测试 | D_RISK | risk_control | 是 | 已覆盖(BM-RC-08-C) | 与现有环节 BM-RC-08-C 压力测试 等价/被其包含(sim=1.00) |
| 40 | L1479 | §14 极端事件与黑天鹅 | §14.5 二阶效应与传染模型 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-12) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 41 | L1538 | §15 AI/Agent风险治理 | §15.1 有界自治(Bounded Autonomy) | D_RISK | risk_control | 部分 | 归indicators(BM-MT-03) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 42 | L1568 | §15 AI/Agent风险治理 | §15.2 保障缺口(Guarantee Gap)管理 | D_RISK | risk_control | 部分 | 归indicators(BM-BT-05) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 43 | L1580 | §15 AI/Agent风险治理 | §15.3 治理漂移(Governance Drift)防护 | D_RISK | risk_control | 部分 | 归indicators(BM-SEL-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 44 | L1601 | §15 AI/Agent风险治理 | §15.4 Agent行为监控 | D_RISK | risk_control | 部分 | 归indicators(BM-RC-04) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 45 | L1628 | §15 AI/Agent风险治理 | §15.5 ARS双轨结算模型 | D_RISK | risk_control | 部分 | 归indicators(BM-REC-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 46 | L1666 | §15 AI/Agent风险治理 | §15.6 ARA自适应风险架构原则 | D_RISK | risk_control | 部分 | 归indicators(BM-EXE-01) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 47 | L1763 | §17 跨域风险模块清单与蓝图映射 | §17.1 D-RISK域模块映射 | D_RISK | risk_control | 部分 | 归indicators(BM-RES-10) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 48 | L1904 | §17 跨域风险模块清单与蓝图映射 | §17.2 跨域风险模块 | D_RISK | risk_control | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
| 49 | L1980 | §17 跨域风险模块清单与蓝图映射 | §17.3 跨域因果链、契约与域事件 | D_RISK | risk_control | 部分 | 归indicators | 参数/契约/时序类，下沉到相关环节 indicators JSONB |
| 50 | L2027 | §17 跨域风险模块清单与蓝图映射 | §17.4 项目蓝图风险映射 | D_RISK | risk_control | 部分 | 归indicators(BM-SEL-24) | 概念级已被现有环节覆盖，细节下沉 indicators（双轨制） |
