---
ttl: task_bound
author: Kimi3
date: 2026-08-05
---

# 检查 G：源文档章节→battle_map 承载对齐表

## 00-架构图总览与索引.md（6 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L9 | §1 架构图全景 | 排除 | 元文档（索引/边界定义），不挂载 |
| L136 | §2 每个架构图的边界定义 | 排除 | 元文档（索引/边界定义），不挂载 |
| L344 | §3 架构图与能力定位书的关系 | 排除 | 元文档（索引/边界定义），不挂载 |
| L368 | §4 架构图与功能域的关系 | 排除 | 元文档（索引/边界定义），不挂载 |
| L405 | §5 架构图间交叉引用索引 | 排除 | 元文档（索引/边界定义），不挂载 |
| L456 | 版本历史 | 排除 | 元文档（索引/边界定义），不挂载 |

## 交易决策架构.md（31 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L90 | §1 总体流水线架构 | 排除 | 元信息/引用章节，非作战内容 |
| L1243 | §2 L0 数据接入与预处理层 | 挂载 | battle_map_05_stock_selection.md |
| L1323 | §3 L1 因子计算层 | 挂载 | battle_map_05_stock_selection.md |
| L3304 | §4 L2-A 信号生成层 | 挂载 | battle_map_05_stock_selection.md |
| L3939 | §5 L2-B 主力行为分析层 | 挂载 | battle_map_05_stock_selection.md |
| L4231 | §6 L2-C 市场状态与大盘预测层 | 挂载 | battle_map_05_stock_selection.md |
| L4907 | §7 L2-D 知识图谱与因果推演层 | 挂载 | battle_map_01_research_incubation.md |
| L5068 | §8 L3 策略决策与组合优化层 | 挂载 | battle_map_08_position_management.md |
| L5426 | §9 L4 风控与执行层（→A4风险架构） | 挂载 | battle_map_09_risk_control.md |
| L5711 | 决策编排器——缺失功能模块 | 挂载 | battle_map_06_buy_flow.md |
| L5879 | §10 L5 闭环优化与自迭代层 | 挂载 | battle_map_11_reconciliation.md |
| L5977 | §11 L6 决策可解释性与人机协作层 | 排除 | 元信息/引用章节，非作战内容 |
| L6034 | §12 横切层 | 挂载 | battle_map_12_cross_cutting.md |
| L6145 | §13 筛选漏斗模型（v0.1升级） | 挂载 | battle_map_05_stock_selection.md |
| L6269 | §14 盘中实时事件处理 | 排除 | 元信息/引用章节，非作战内容 |
| L6323 | §15 计算节奏与时序 | 排除 | 元信息/引用章节，非作战内容 |
| L6451 | §16 能力冲突矩阵与仲裁规则 | 排除 | 元信息/引用章节，非作战内容 |
| L6493 | §17 数据源到流水线映射 | 排除 | 元信息/引用章节，非作战内容 |
| L6587 | §18 与下层设计的对接 | 排除 | 元信息/引用章节，非作战内容 |
| L6623 | §19 质量属性与边界规则引用 | 排除 | 元信息/引用章节，非作战内容 |
| L6724 | §20 方法论约束与架构决策引用 | 排除 | 元信息/引用章节，非作战内容 |
| L7931 | §21 资产与市场覆盖矩阵 | 排除 | 元信息/引用章节，非作战内容 |
| L8003 | §22 角色与旅程 | 排除 | 元信息/引用章节，非作战内容 |
| L8215 | §23 能力卡片完整引用 | 排除 | 元信息/引用章节，非作战内容 |
| L9036 | §24 外部系统交互引用 | 排除 | 元信息/引用章节，非作战内容 |
| L9109 | §25 术语表引用 | 排除 | 元信息/引用章节，非作战内容 |
| L9236 | §26 全局假设清单引用 | 排除 | 元信息/引用章节，非作战内容 |
| L9258 | §27 系统级成功指标引用 | 排除 | 元信息/引用章节，非作战内容 |
| L9318 | §28 能力全景图引用 | 排除 | 元信息/引用章节，非作战内容 |
| L9850 | §29 架构补充：基础设施必需项与方法论增强 | 排除 | 元信息/引用章节，非作战内容 |
| L12250 | §30 场外草稿区缺失模块补充 | 排除 | 元信息/引用章节，非作战内容 |

## Agent架构.md（21 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L30 | §0 架构定位 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L352 | §1 Agent分层指挥链 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L599 | §2 Agent能力矩阵 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L746 | §3 Agent间通信协议 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1146 | §4 Agent自治边界 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1291 | §5 Agent冷启动与技能注册 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1327 | Discovery (~100-200 tokens) | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1333 | Activation (<5000 tokens) | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1347 | Execution (references/scripts) | 部分挂载 | battle_map_10_execution.md（Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048）） |
| L1442 | §6 自反Agent（Reflexion） | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1626 | §7 Agent记忆架构 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1708 | §8 LLM Agent路由 | 部分挂载 | battle_map_10_execution.md（Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048）） |
| L1875 | §9 功能域映射 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L1985 | §10 硬边界与约束 | 部分挂载 | battle_map_12_cross_cutting.md（Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048）） |
| L2004 | §11 方法论约束与设计决策 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L2023 | §12 角色与交互旅程 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L2036 | §13 成功指标 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L2078 | §14 冲突与矛盾矩阵 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L2095 | §15 Agent可观测性 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L2175 | §16 Agent测试与混沌工程 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |
| L2228 | §17 遗留问题裁定 | 部分 | Agent主体不挂；仅 D_ORCHESTRATOR 调用点挂 buy_flow（BM-BUY-03 决策编排 supplement: MOD-INF-039/048） |

## 学习系统架构.md（16 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L31 | §0 架构定位 | 排除 | 元信息/引用章节，非作战内容 |
| L131 | §1 行业对标与独创性分析 | 排除 | 元信息/引用章节，非作战内容 |
| L174 | §2 总体架构 | 排除 | 元信息/引用章节，非作战内容 |
| L474 | §3 S0 多模态知识采集层 | 挂载 | battle_map_01_research_incubation.md |
| L635 | §4 S1 知识清洗与结构化层 | 挂载 | battle_map_01_research_incubation.md |
| L732 | §5 S2 知识分类与策略提取层 | 挂载 | battle_map_01_research_incubation.md |
| L1016 | §6 S3 模块映射与工厂匹配层 | 挂载 | battle_map_01_research_incubation.md |
| L1196 | §7 S4 模块创建与接入层 | 挂载 | battle_map_02_model_training.md |
| L1408 | §8 S5 试运行与验证层 | 挂载 | battle_map_02_model_training.md |
| L1617 | §9 S6 元学习与自我进化层 | 挂载 | battle_map_02_model_training.md |
| L1839 | §10 横切层 | 挂载 | battle_map_12_cross_cutting.md |
| L2082 | §11 与交易决策流水线的接口协议 | 排除 | 元信息/引用章节，非作战内容 |
| L2281 | §12 分阶段实现路线 | 排除 | 元信息/引用章节，非作战内容 |
| L2379 | §13 成功标准 | 排除 | 元信息/引用章节，非作战内容 |
| L2512 | §14 行业前沿补充（2025-2026 自进化审查） | 排除 | 元信息/引用章节，非作战内容 |
| L2841 | 版本历史 | 排除 | 元信息/引用章节，非作战内容 |

## 数据架构.md（18 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L38 | §0 数据架构唯一真源 | 排除 | 元信息/引用章节，非作战内容 |
| L310 | 第一部分：核心行情数据（A3-D1 数据接入域） | 挂载 | battle_map_05_stock_selection.md |
| L709 | 第二部分：基本面与另类数据（A3-D2 基本面域 + A3-D3 另类数据域） | 排除 | 元信息/引用章节，非作战内容 |
| L776 | 第三部分：计算指标与因子数据（A3-D4 因子域） | 挂载 | battle_map_05_stock_selection.md |
| L900 | 第四部分：数据源质量评估 | 排除 | 元信息/引用章节，非作战内容 |
| L948 | 第五部分：数据源接入优先级与路线图 | 排除 | 元信息/引用章节，非作战内容 |
| L990 | 第六部分：知识图谱数据规划 | 挂载 | battle_map_01_research_incubation.md |
| L1030 | §7 数据存储架构 | 排除 | 元信息/引用章节，非作战内容 |
| L1130 | §8 数据流动路径 | 排除 | 元信息/引用章节，非作战内容 |
| L1198 | §9 数据血缘与可追溯性 | 排除 | 元信息/引用章节，非作战内容 |
| L1284 | §10 数据质量SLA与治理 | 排除 | 元信息/引用章节，非作战内容 |
| L1963 | §11 特征存储架构 | 排除 | 元信息/引用章节，非作战内容 |
| L2615 | §12 事件溯源架构 | 排除 | 元信息/引用章节，非作战内容 |
| L3335 | §13 Point-in-Time一致性保证 | 排除 | 元信息/引用章节，非作战内容 |
| L3448 | §14 数据安全与合规约束 | 排除 | 元信息/引用章节，非作战内容 |
| L3570 | §15 可扩展性与演进性 | 排除 | 元信息/引用章节，非作战内容 |
| L3696 | §16 2025-2026前沿实践对标与二元建设结论 | 排除 | 元信息/引用章节，非作战内容 |
| L4044 | §17 依赖图域模块补充 | 排除 | 元信息/引用章节，非作战内容 |

## 合规架构.md（15 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L359 | §1 交易合规 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L638 | §2 持仓合规 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L674 | §3 报告合规 | 部分挂载 | battle_map_11_reconciliation.md（合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15）） |
| L811 | §4 AI合规 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L968 | §5 跨市场合规 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1055 | §6 零知识审计 | 部分挂载 | battle_map_01_research_incubation.md（合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15）） |
| L1147 | §7 法规映射表 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1206 | §8 合规技术架构 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1295 | §9 合规治理与KPI | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1335 | §10 硬边界裁定 | 部分挂载 | battle_map_12_cross_cutting.md（合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15）） |
| L1463 | §11 信息合规 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1511 | §12 操作合规 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1583 | §13 合规技术深度 | 部分 | 合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15） |
| L1655 | §14 合规持续运营 | 部分挂载 | battle_map_11_reconciliation.md（合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15）） |
| L1717 | §15 硬边界裁定扩展 | 部分挂载 | battle_map_12_cross_cutting.md（合规主体不挂；仅买入合规闸挂 buy_flow（BM-BUY-08/08-A/08-B/09/10/11/12/13/15）） |

## 安全架构.md（15 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L241 | §1 安全域划分 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L440 | §2 纵深防御6层 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L969 | §3 IAM与访问控制 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L1151 | §4 密钥层级管理 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L1315 | §5 审计链 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L1460 | §6 Agent安全 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L1907 | §7 内幕交易防护 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2152 | §8 功能域映射 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2171 | §9 硬边界与约束 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2193 | §10 方法论约束与设计决策 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2208 | §11 角色与交互旅程 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2233 | §12 成功指标 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2255 | §13 冲突与矛盾矩阵 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2271 | §14 遗留问题裁定 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |
| L2554 | §15 功能域安全模块补全 | 排除 | 域禁止：安全主体不挂；仅 MOD-INF-018 安全基线挂 risk_control（BM-RC 系列） |

## 运维架构.md（14 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L202 | §1 运行时架构 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L441 | §2 三平面拓扑 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L611 | §3 AI自治运维闭环 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L785 | §4 应急保命轨 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L981 | §5 灾备架构 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1149 | §6 监控体系 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1305 | §7 变更管理 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1447 | §8 功能域映射 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1777 | §9 硬边界与约束 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1791 | §10 方法论约束与设计决策 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1808 | §11 角色与交互旅程 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1820 | §12 成功指标 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1835 | §13 冲突与矛盾矩阵 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |
| L1848 | §14 硬边界裁定书 | 排除 | 域禁止：运维主体不挂；仅 D_OPS 反馈循环运营挂 reconciliation（BM-REC 系列） |

## 治理架构.md（18 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L146 | §1 治理三层边界 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L490 | §2 变更审批流 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L586 | §3 架构漂移检测与纠正闭环 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L707 | §4 AI自治边界 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L766 | §5 治理激活时序 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L813 | §6 蓝图-代码-文档三方对齐机制 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L866 | §7 治理自动化 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L912 | §8 功能域映射 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L935 | §9 硬边界与约束 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L956 | §10 方法论约束与设计决策 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L971 | §11 角色与交互旅程 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1035 | §12 成功指标 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1057 | §13 冲突与矛盾矩阵 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1076 | §14 行业对标与参考 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1164 | §15 自进化审查记录 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1215 | §16 监管合规映射 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1304 | §17 遗留问题裁定记录 | 排除 | 域禁止：治理架构完全不挂（铁律5） |
| L1479 | §18 治理域模块映射与建设状态 | 排除 | 域禁止：治理架构完全不挂（铁律5） |

## 集成架构.md（28 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L305 | §1 外部系统交互矩阵 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L533 | §2 集成风格 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L626 | §3 接口契约治理 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L728 | §4 数据源故障降级 | 部分挂载 | battle_map_12_cross_cutting.md（集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列）） |
| L834 | §5 MCP协议集成 | 部分挂载 | battle_map_12_cross_cutting.md（集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列）） |
| L951 | §6 隔离策略 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1164 | §7 功能域映射 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1190 | §8 硬边界与约束 | 部分挂载 | battle_map_12_cross_cutting.md（集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列）） |
| L1240 | §9 方法论约束与设计决策 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1271 | §10 角色与交互旅程 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1284 | §11 成功指标 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1311 | §12 冲突与矛盾矩阵 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1333 | §13 集成架构时序视图 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1392 | §14 行业对标与参考 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1424 | §15 遗留问题裁定 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1648 | §16 集成可观测性 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1683 | §17 集成安全纵深 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1725 | §18 集成测试策略 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1762 | §19 API网关设计 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1827 | §20 集成容量规划与限流 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1870 | §21 数据一致性保证 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1909 | §22 术语表 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1932 | §23 全局假设清单 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L1952 | §24 集成闭环优化与自迭代 | 部分挂载 | battle_map_11_reconciliation.md（集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列）） |
| L1994 | §25 集成架构增强与演进路线图 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L2045 | §26 集成合规治理 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L2086 | §27 集成层灾备与状态可重建性 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |
| L2138 | §28 集成域子模块全景与蓝图映射 | 部分 | 集成基础设施不挂；D_INTEGRATION 管线路由挂 stock_selection/buy_flow（BM-SEL-27/BM-BUY 系列） |

## 风险架构.md（17 个 H2）

| 行号 | H2 章节 | 承载 | battle_map 文件/环节 |
|---|---|---|---|
| L332 | §1 风险分类体系 | 挂载 | battle_map_09_risk_control.md |
| L604 | §2 风险度量方法 | 挂载 | battle_map_09_risk_control.md |
| L720 | §3 风险否决权 | 挂载 | battle_map_09_risk_control.md |
| L892 | §4 风险数据流 | 挂载 | battle_map_09_risk_control.md |
| L964 | §5 风险治理 | 挂载 | battle_map_09_risk_control.md |
| L1020 | §6 A股合规规则（代管） | 排除 | 元信息/引用章节，非作战内容 |
| L1165 | §7 漂移检测与风险闭环 | 挂载 | battle_map_02_model_training.md |
| L1263 | §8 功能域映射 | 排除 | 元信息/引用章节，非作战内容 |
| L1283 | §9 硬边界与约束 | 挂载 | battle_map_12_cross_cutting.md |
| L1315 | §10 方法论约束与设计决策 | 排除 | 元信息/引用章节，非作战内容 |
| L1359 | §11 角色与交互旅程 | 排除 | 元信息/引用章节，非作战内容 |
| L1371 | §12 成功指标 | 排除 | 元信息/引用章节，非作战内容 |
| L1395 | §13 冲突与矛盾矩阵 | 排除 | 元信息/引用章节，非作战内容 |
| L1415 | §14 极端事件与黑天鹅 | 挂载 | battle_map_09_risk_control.md |
| L1534 | §15 AI/Agent风险治理 | 挂载 | battle_map_09_risk_control.md |
| L1721 | §16 行业标准对标 | 排除 | 元信息/引用章节，非作战内容 |
| L1759 | §17 跨域风险模块清单与蓝图映射 | 挂载 | battle_map_09_risk_control.md |
