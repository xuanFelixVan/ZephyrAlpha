# 场外文档内容分层审计任务卡 v5.0

> **创建**: 2026-05-29
> **融合自**: content-layering-protocol.md v1.0 + cross-document-audit_protocol.md v1.0 + depgraph-v3-audit-task-cards.md v1.0 + domain_model_migration_plan.md DM-031~108（该文件已归档至architecture_upgrade_discussion.md §22.11）
> **目标文档**: `D:\ZephyrAlpha\data\asset_index\project_entity_depgraph_v3_domain_draft.yaml`
> **维度**: 正向审计(按域,30张) + 反向审计(按文件,45张) = 75张
> **已完成**: FA-008(D-DATA)部分 ✅ | RA-001~RA-003 ✅

---

## 通用执行方法（每张卡MUST内联本方法）

### 分层标准

| 标记 | 含义 | 写入目标 |
|------|------|_______--|
| `[全景]` | 域/子域/模块级的**关系结构**——谁依赖谁、什么类型、什么契约、什么事件 | depgraph v3 |
| `[蓝图]` | 模块**如何实现**——具体技术选型、代码接口、数据结构、算法参数、目录结构 | 各模块蓝图 |
| `[混合]` | 两者兼有，需拆分 | 拆分后分别写入 |

### 机械判定表

| # | 问题 | YES→ | NO→ |
|---|------|------|-----|
| Q1 | 描述"谁依赖谁"或"谁发出什么事件"或"谁消费什么契约"？ | `[全景]` | Q2 |
| Q2 | 描述域/子域/模块的ID、名称、职责、优先级、建设状态？ | `[全景]` | Q3 |
| Q3 | 描述不变量、硬边界、契约的存在性（有/无）？ | `[全景]` | Q4 |
| Q4 | 描述具体代码签名（dataclass/函数参数/返回类型）？ | `[蓝图]` | Q5 |
| Q5 | 描述具体技术方案（存储选型/算法参数/目录结构/配置值）？ | `[蓝图]` | Q6 |
| Q6 | 描述设计决策的理由和替代方案对比？ | `[蓝图]` | Q7 |
| Q7 | 同时包含关系结构和实现细节？ | `[混合]` | `[待定]`人工判定 |

### 章节默认标记

| 章节类型 | 默认标记 |
|_______--|:---:|
| §0 域定义 | `[全景]` |
| §1 子模块清单(ID/名称/职责/优先级/建设状态) | `[全景]` |
| §1 子模块清单(门禁/对标/合并自) | `[蓝图]` |
| §1 C轨映射/子域分组 | `[全景]` |
| §1 架构图(mermaid) | `[全景]` |
| §1 数据目录结构/冷热分层/Quality Gate/Feature Store | `[蓝图]` |
| §2 域内依赖图/三计算平面映射 | `[全景]` |
| §3 域间依赖(关系+契约存在性) | `[全景]` |
| §3 接口定义(dataclass/代码)/流水线对接 | `[蓝图]` |
| §4 域事件流 | `[全景]` |
| §5 激活前提 | `[全景]` |
| §6 设计决策 | `[蓝图]` |
| §7 合规(法规编号) | `[全景]` |
| §7 合规(执行方式) | `[蓝图]` |
| §8 学习系统/采集方案/质量架构 | `[蓝图]` |
| 代码映射(正向/反向/缺口) | `[全景]` |
| 因果链(域级事件流) | `[全景]` |
| 因果链(模块级步骤+待量化参数) | `[蓝图]` |
| 主观术语量化转换表 | `[蓝图]` |

### 执行步骤

```
STEP 1  读取源文件 → 逐章节标注[全景]/[蓝图]/[混合]
STEP 2  [混合]章节拆分 → 关系结构→[全景]，实现细节→[蓝图]
STEP 3  将[全景]内容与depgraph v3逐句核对（详细审计协议）
  3.0 准备: 读取源文件全文+depgraph v3结构地图(Grep定位顶层键行号)
  3.1 逐语义单元核对:
      - 语义单元粒度: 表格行=一行含所有列; 列表项=一个; 段落=一个陈述句; 矩阵=一个单元格; 元数据=一个key-value
      - 核对判定: ✅完全存在→跳过; ⚠️部分存在→补充; ❌不存在→插入
  3.2 补充/插入策略:
      A: 键值替换(key: 旧值→新值)
      B: 字段追加(节点内追加新字段)
      C: 段落插入(相邻段之间插入新段)
      D: 多位置插入(分别SearchReplace)
  3.3 每次操作后Grep验证写入成功
STEP 4  [蓝图]内容不写入depgraph，但记录锚点(blueprint_id/design_decisions/compliance_refs)
STEP 5  两轮循环 → 新发现=0 → 关闭
```

### 审计维度说明

| 维度 | 方向 | 卡片类型 | 说明 |
|------|------|_______--|------|
| 正向审计(按域) | 源文件→depgraph域节点 | FA-001~FA-030 | 扫描全部源文件中与该域相关的内容，核对depgraph中该域节点是否完整 |
| 反向审计(按文件) | depgraph→源文件 | RA-001~RA-045 | 读取源文件全文，逐句核对depgraph v3是否已包含 |

**执行顺序**: 反向审计先行（逐文件完整审计）→ 正向审计跟进（域视角查漏补缺）

### 轮次退出条件

| 轮次 | 退出条件 |
|:---:|_______--|
| R1 | 已核对源文件中所有[全景]内容(L1~L13强制检查) |
| R2 | 重读源文件，确认无遗漏（7类易遗漏项+L10~L13逐章覆盖） |
| RN | 本轮新发现=0 |
| RN+1 | **连续第2轮新发现=0** → 审计完成 |

### 蓝图锚点规则

| 蓝图内容类型 | depgraph锚点 |
|_______-----|_______------|
| 具体代码签名 | 模块`blueprint_id`字段 |
| 设计决策 | 域节点`design_decisions`列表(仅ID+标题) |
| 合规执行方式 | 域节点`compliance_refs`列表 |
| 因果链模块步骤 | `causal_chains`仅保留域级事件流 |

### 特殊场景处理

| 场景 | 处理 |
|------|------|
| depgraph比源文件更详细 | ✅跳过(好事，不回退) |
| 分类体系不同(表格vs嵌套YAML) | 建立列名→字段名映射，逐字段核对 |
| 矩阵类内容(30×30) | 按行提取→转化为边列表(H→hard_depends, S→soft_depends, E→event_depends) |
| 多位置插入 | 对每个位置分别SearchReplace |
| [混合]章节拆分 | 关系结构部分→[全景]，实现细节部分→[蓝图] |

### 质量门禁

审计任务完成的充要条件:
✅ R1: 源文件每个[全景]语义单元都已核对
✅ R2: 重读源文件全文，7类易遗漏项+L10~L13逐章覆盖已检查，新发现已补充
✅ RN: 重读源文件全文，新发现=0
✅ RN+1: **连续第2轮新发现=0**
✅ L1~L13强制检查清单全部打勾
✅ 所有Todo项标记completed
✅ 输出最终总结(含每轮补充内容清单)

缺少任何一项 → 审计未完成

### 工具使用规范

| 工具 | 用途 | 规则 |
|------|------|------|
| Read | 读取文件 | 大文件分段: offset+limit; 定位读取: 先Grep定位行号 |
| Grep | 搜索 | 精确: pattern="D-XXX"; 模糊: pattern="关键词"; 结构: pattern="^key:" |
| SearchReplace | 编辑 | 唯一编辑手段; old_str必须唯一匹配; 禁止删+建; 每次只改一个位置; 改完Grep验证 |
| TodoWrite | 跟踪 | 每章节一个Todo项; 开始→in_progress; 完成→completed(附summary) |

### 禁止项

- 禁止创建辅助脚本(所有审查手工逐句执行)
- 禁止批量读取100句后批量核对(容易遗漏)
- 禁止跳过"看起来不重要"的注释/图例/来源行
- 禁止一次SearchReplace修改多个不相关位置
- 禁止补充后不验证(必须Grep确认)
- 禁止删+建(编辑优先原则)
- 禁止占位符(TODO/.../pass/NotImplementedError)

### TC-002审计教训（MUST在每张卡执行前阅读）

| # | 教训 | 根因 | 检查方法 | 修复方法 |
|---|------|------|_______--|_______--|
| L1 | **ID编号体系冲突**：源文档用稀疏编号(如D-DATA-77)，depgraph用顺序编号(如D-DATA-20) | 初始生成时未统一编号 | 对比源文档模块ID与depgraph模块ID，建立映射表 | 不改编号体系，但MUST在depends_on/consumer_modules中使用depgraph ID |
| L2 | **description按源ID取值导致错位**：depgraph中D-DATA-06的description取自源文档ID=06的模块 | 生成时description和display_name取自不同来源 | 逐模块比对display_name与description语义是否匹配 | 按display_name语义重写description |
| L3 | **depends_on/consumer_modules引用断裂**：字段值引用源文档稀疏ID | L1的编号冲突未在引用字段中同步 | Grep搜索所有D-DATA-XX引用，检查XX是否在01~N范围内 | 按L1映射表替换为depgraph顺序ID |
| L4 | **子域覆盖能力缺失**：源文档每个子域有"覆盖能力"列，depgraph无此字段 | 初始生成时未包含 | 检查源文档§1子域分组表是否有"覆盖能力"列 | 在域节点添加subdomains列表(含id/name/coverage) |
| L5 | **激活前提和三计算平面映射缺失**：源文档§5和§2有完整结构，depgraph无 | 初始生成时未包含 | 检查源文档§5激活前提和§2三计算平面映射 | 新增activation_prerequisites.{域ID}和three_plane_mapping.{域ID} |

**每张卡执行前的强制检查清单**：

```
□ L1检查: 建立源文档模块ID → depgraph模块ID映射表
□ L2检查: 逐模块比对display_name与description语义是否匹配
□ L3检查: Grep搜索所有模块引用，确认引用ID在depgraph范围内
□ L4检查: 源文档子域分组表是否有覆盖能力列 → 补充subdomains
□ L5检查: 源文档§5激活前提 → 补充activation_prerequisites
□ L5检查: 源文档§2三计算平面映射 → 补充three_plane_mapping
□ L6检查: 源文档域事件流 → 每条事件补充trigger_condition/priority/broadcast/internal_subscribers
□ L6检查: 源文档消费的外部事件 → 新增{域}_consumed节(source_domain/consumer_submodule/handling)
□ L7检查: 源文档域间接口 → 接口签名补充provider_submodule归属；消费接口补充consumed_interfaces annotation
□ L8检查: 源文档能力定位书 → 补充capability_submodule_mapping annotation(子模块→能力精细映射)
□ L8检查: 源文档软依赖降级策略 → 补充soft_dependency_fallback annotation
□ L9检查: 源文档域内依赖 → 补充internal_dependencies annotation(子模块间依赖边+硬/软类型)
□ L9检查: 源文档核心拦截/执行链路 → 补充critical_path或interception_chain annotation
□ L10检查: 源文档逐章覆盖核对 → 每个章节必须有≥1条annotation覆盖，无覆盖=遗漏
□ L10检查: 源文档架构参数提取 → 进程模型/Redis命名空间/GPU调度/延迟预算/时段定义/降级矩阵等参数化全景内容
□ L11检查: 源文档自治/安全/治理模型 → RBAC/ABAC/熔断器/HITL/不可变项/变更流程/Kill Switch双路径等模型级全景内容
□ L11检查: 源文档域边界逐维度对比 → 不止高层概述，必须有逐维度(权限/审计/密钥/Kill Switch等)对比表
□ L12检查: 源文档因果链/价值流 → 核心因果链+价值流事件链(域级)
□ L12检查: 源文档合规/风险分类 → 合规控制级别+操作风险分类+冲突仲裁矩阵
□ L13检查: 源文档实现决策(方案对比) → 多方案对比中采用理由是全景(为什么不选X)
□ L13检查: 源文档行业对标 → 对标框架映射(Pact.io/OpenAPI/CloudEvents等)是全景
□ L13检查: 源文档v1→v2迁移 → 模块演变路径(保留/合并/移除)是全景
```

### 模块13必填字段（DM卡规范）

| # | 字段 | 类型 | 示例 |
|:---:|------|:---:|------|
| 1 | `module_id` | str | `D-AUTONOMY-CORE-01` |
| 2 | `name` | str | `AgentRBAC` |
| 3 | `description` | str | `Agent身份注册...` |
| 4 | `type` | str | `module` |
| 5 | `physical_files` | list[str] | `[src/zephyr/agent_rbac/__init__.py, ...]` |
| 6 | `path` | str | `src/zephyr/agent_rbac/` |
| 7 | `domain` | str | `D-AUTONOMY-CORE` |
| 8 | `blueprint_id` | str | `""` 或 `MOD_INF_007` |
| 9 | `stability` | enum | `stable` |
| 10 | `safety_level` | enum | `H` |
| 11 | `ai_autonomy` | enum | `immutable_core` |
| 12 | `build_status` | enum | `built` |
| 13 | `priority` | enum | `P0` |

---

## A. 正向审计（按域，30张）

> 每张卡对应depgraph v3一个域，扫描全部源文件中与该域相关的内容，核对depgraph v3中该域节点是否完整。
> 执行时机：反向审计完成后，以域视角查漏补缺。

### FA-001: D-FACTOR 因子域

- **域ID**: D-FACTOR
- **主要源文件**: 03-D-FACTOR-因子域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-002: D-SIGNAL 信号域

- **域ID**: D-SIGNAL
- **主要源文件**: 04-D-SIGNAL-信号域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-003: D-PF-CORE 组合核心域

- **域ID**: D-PF-CORE
- **主要源文件**: 05-D-PF-CORE-组合核心域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-004: D-PF-ALLOC 组合分配域

- **域ID**: D-PF-ALLOC
- **主要源文件**: 06-D-PF-ALLOC-组合分配域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-005: D-POSITION 仓位管理域

- **域ID**: D-POSITION
- **主要源文件**: 07-D-POSITION-仓位管理域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-006: D-EX-CORE 执行核心域

- **域ID**: D-EX-CORE
- **主要源文件**: 08-D-EX-CORE-执行核心域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-007: D-EX-SOR 执行路由域

- **域ID**: D-EX-SOR
- **主要源文件**: 09-D-EX-SOR-执行路由域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md, 集成架构.md
- **状态**: 待执行

### FA-008: D-DATA 数据域

- **域ID**: D-DATA
- **主要源文件**: 02-D-DATA-数据域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 数据架构.md, 交易决策架构.md
- **状态**: ✅ 部分完成（RA-003反向审计已完成，正向需验证域节点完整性）
- **已完成工作**: TC-002三轮审计(R1:10项, R2:10项, R3:0项)

### FA-009: D-REPORTING 报告域

- **域ID**: D-REPORTING
- **主要源文件**: 10-D-REPORTING-报告域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-010: D-RISK 风控域

- **域ID**: D-RISK
- **主要源文件**: 11-D-RISK-风控域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md, 风险架构.md
- **状态**: 待执行

### FA-011: D-ML-TRAIN 训练域

- **域ID**: D-ML-TRAIN
- **主要源文件**: 12-D-ML-TRAIN-训练域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 学习系统架构.md
- **状态**: 待执行

### FA-012: D-ML-SERVE 推理域

- **域ID**: D-ML-SERVE
- **主要源文件**: 13-D-ML-SERVE-推理域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 学习系统架构.md
- **状态**: 待执行

### FA-013: D-ALT-DATA 另类数据域

- **域ID**: D-ALT-DATA
- **主要源文件**: 14-D-ALT-DATA-另类数据域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 数据架构.md
- **状态**: 待执行

### FA-014: D-DATA-ENG 数据工程域

- **域ID**: D-DATA-ENG
- **主要源文件**: 15-D-DATA-ENG-数据工程域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 数据架构.md
- **状态**: 待执行

### FA-015: D-CROSS-ASSET 跨资产跨市场域

- **域ID**: D-CROSS-ASSET
- **主要源文件**: 16-D-CROSS-ASSET-跨资产跨市场域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 集成架构.md
- **状态**: 待执行

### FA-016: D-COMPLIANCE 合规监管域

- **域ID**: D-COMPLIANCE
- **主要源文件**: 17-D-COMPLIANCE-合规监管域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 合规架构.md
- **状态**: 待执行

### FA-017: D-TRADING 交易运营域

- **域ID**: D-TRADING
- **主要源文件**: 18-D-TRADING-交易运营域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 集成架构.md
- **状态**: 待执行

### FA-018: D-SIMULATION 仿真域

- **域ID**: D-SIMULATION
- **主要源文件**: 19-D-SIMULATION-仿真域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 学习系统架构.md
- **状态**: 待执行

### FA-019: D-RESEARCH 研究基础设施域

- **域ID**: D-RESEARCH
- **主要源文件**: 20-D-RESEARCH-研究基础设施域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 学习系统架构.md
- **状态**: 待执行

### FA-020: D-KNOWLEDGE 知识域

- **域ID**: D-KNOWLEDGE
- **主要源文件**: 21-D-KNOWLEDGE-知识域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 学习系统架构.md
- **状态**: 待执行

### FA-021: D-AUTONOMY-CORE 自治核心域

- **域ID**: D-AUTONOMY-CORE
- **主要源文件**: 22-D-AUT-CORE-自治核心域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, Agent架构.md
- **状态**: 待执行

### FA-022: D-AUTONOMY-PERM 自治保护域

- **域ID**: D-AUTONOMY-PERM
- **主要源文件**: 23-D-AUT-PERM-自治保护域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, Agent架构.md
- **状态**: 待执行

### FA-023: D-INFRA-RUNTIME 运行时基础设施域

- **域ID**: D-INFRA-RUNTIME
- **主要源文件**: 24-D-INFRA-RUNTIME-运行时基础设施域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 运维架构.md
- **状态**: 待执行

### FA-024: D-INFRA-OPS 运维基础设施域

- **域ID**: D-INFRA-OPS
- **主要源文件**: 25-D-INFRA-OPS-运维基础设施域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 运维架构.md
- **状态**: 待执行

### FA-025: D-SECURITY 安全域

- **域ID**: D-SECURITY
- **主要源文件**: 26-D-SECURITY-安全域.md（已融合v1+v2）
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 安全架构.md
- **状态**: 待执行

### FA-026: D-INTEGRATION 集成域

- **域ID**: D-INTEGRATION
- **主要源文件**: 27-D-INTEGRATION-集成域.md（已融合v1+v2）
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 集成架构.md
- **状态**: 待执行

### FA-027: D-FRONTEND 前端域

- **域ID**: D-FRONTEND
- **主要源文件**: 28-D-FRONTEND-前端域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

### FA-028: D-GOVERNANCE 治理域

- **域ID**: D-GOVERNANCE
- **主要源文件**: 29-D-GOVERNANCE-治理域.md（已融合v1+v2）
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 治理架构.md
- **状态**: 待执行

### FA-029: D-OPS 运维域

- **域ID**: D-OPS
- **主要源文件**: 30-D-OPS-运维域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 运维架构.md
- **状态**: 待执行

### FA-030: D-SELL-DECISION 卖出决策域

- **域ID**: D-SELL-DECISION
- **主要源文件**: 31-D-SELL-DECISION-卖出决策域.md
- **跨域源文件**: 00-总览与索引.md, 01-跨域交叉点与因果链.md, 交易决策架构.md
- **状态**: 待执行

---

## B. 反向审计（按文件，45张）

> 每张卡对应一个源文件，逐句阅读该文件，核对每句话是否已在depgraph v3中体现。
> 执行时机：先行执行，逐文件完整审计。

### RA-001: 00-总览与索引.md ✅ COMPLETED

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\00-总览与索引.md`
- **状态**: ✅ 三轮审计完成，新发现=0

### RA-002: 01-跨域交叉点与因果链.md 🔄 RE-AUDIT v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\01-跨域交叉点与因果链.md`
- **行数**: ~830行
- **内容结构**: 主观术语量化转换(47项)+硬边界约束总表(B-001~020/HB-SEC-01~13/HB-INT-01~13/HB-GOV-01~10)+功能域模块(17域)+跨域交叉点(CP-01~09)+因果链(4条)+契约矩阵(CTR-001~006/CTR-TRACE-001/CTR-ERR-001~006/CTR-BP-001~003/CTR-P1-001~015/OCP-001~003/EXT-001~004/VER-R1~R5)+领域事件(22条)+事件因果链(4条)+频率分档(L1~L4)+Saga事务(4条)+容量升级依赖(12条)+建设受限门禁总表(4类)
- **v3已有映射**: global_annotations中`architecture_cross_references`(40条XREF)+`architecture_domain_constraints`(10架构图约束)+`external_contracts`(EXT-001~004)+`ocp_extension_points`(OCP-001~003)+`v2_migration_delta`+`edge_migration_audit`
- **审查深度**: v5.0(L1~L13+连续2轮新发现=0退出)
- **审查重点**: 
  - L1~L5: 基础结构核对(硬边界/契约/事件/交叉点)
  - L6~L9: 7类易遗漏项(条件/阈值/跨域引用/编号/例外/对标/演变)
  - L10~L13: 深度检查(主观术语量化转换表→v3映射/因果链完整性/Saga补偿/容量升级依赖/建设门禁)
- **首轮状态**: ✅ R1完成(6项遗漏已修复: 3项🔴事件ID冲突+因果链断裂+2项⚠️契约消费者补全+1项⚠️CP-08参数引用)

### RA-003: 02-D-DATA-数据域.md ✅ COMPLETED

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\02-D-DATA-数据域.md`
- **域ID**: D-DATA
- **分层标注**: ✅ 已完成
- **状态**: ✅ 三轮审计完成(R1:10项, R2:10项, R3:0项)
- **关键修复**: description错位7处+引用断裂21处+子域覆盖能力11条+事件边7条+激活前提13条+三计算平面映射11条+缺失模块10个+P0模块priority 26个

### RA-004: 03-D-FACTOR-因子域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\03-D-FACTOR-因子域.md`
- **域ID**: D-FACTOR
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-005: 04-D-SIGNAL-信号域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\04-D-SIGNAL-信号域.md`
- **域ID**: D-SIGNAL
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-006: 05-D-PF-CORE-组合核心域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\05-D-PF-CORE-组合核心域.md`
- **域ID**: D-PF-CORE
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-007: 06-D-PF-ALLOC-组合分配域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\06-D-PF-ALLOC-组合分配域.md`
- **域ID**: D-PF-ALLOC
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-008: 07-D-POSITION-仓位管理域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\07-D-POSITION-仓位管理域.md`
- **域ID**: D-POSITION
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-009: 08-D-EX-CORE-执行核心域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\08-D-EX-CORE-执行核心域.md`
- **域ID**: D-EX-CORE
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-010: 09-D-EX-SOR-执行路由域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\09-D-EX-SOR-执行路由域.md`
- **域ID**: D-EX-SOR
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-011: 10-D-REPORTING-报告域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\10-D-REPORTING-报告域.md`
- **域ID**: D-REPORTING
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-012: 11-D-RISK-风控域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\11-D-RISK-风控域.md`
- **域ID**: D-RISK
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-013: 12-D-ML-TRAIN-训练域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\12-D-ML-TRAIN-训练域.md`
- **域ID**: D-ML-TRAIN
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-014: 13-D-ML-SERVE-推理域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\13-D-ML-SERVE-推理域.md`
- **域ID**: D-ML-SERVE
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-015: 14-D-ALT-DATA-另类数据域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\14-D-ALT-DATA-另类数据域.md`
- **域ID**: D-ALT-DATA
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-016: 15-D-DATA-ENG-数据工程域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\15-D-DATA-ENG-数据工程域.md`
- **域ID**: D-DATA-ENG
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-017: 16-D-CROSS-ASSET-跨资产跨市场域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\16-D-CROSS-ASSET-跨资产跨市场域.md`
- **域ID**: D-CROSS-ASSET
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-018: 17-D-COMPLIANCE-合规监管域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\17-D-COMPLIANCE-合规监管域.md`
- **域ID**: D-COMPLIANCE
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-019: 18-D-TRADING-交易运营域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\18-D-TRADING-交易运营域.md`
- **域ID**: D-TRADING
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-020: 19-D-SIMULATION-仿真域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\19-D-SIMULATION-仿真域.md`
- **域ID**: D-SIMULATION
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-021: 20-D-RESEARCH-研究基础设施域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\20-D-RESEARCH-研究基础设施域.md`
- **域ID**: D-RESEARCH
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-022: 21-D-KNOWLEDGE-知识域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\21-D-KNOWLEDGE-知识域.md`
- **域ID**: D-KNOWLEDGE
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-023: 22-D-AUT-CORE-自治核心域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\22-D-AUT-CORE-自治核心域.md`
- **域ID**: D-AUTONOMY-CORE
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-024: 23-D-AUT-PERM-自治保护域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\23-D-AUT-PERM-自治保护域.md`
- **域ID**: D-AUTONOMY-PERM
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-025: 24-D-INFRA-RUNTIME-运行时基础设施域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\24-D-INFRA-RUNTIME-运行时基础设施域.md`
- **域ID**: D-INFRA-RUNTIME
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-026: 25-D-INFRA-OPS-运维基础设施域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\25-D-INFRA-OPS-运维基础设施域.md`
- **域ID**: D-INFRA-OPS
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-027: 26-D-SECURITY-安全域.md（已融合v1+v2）

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\26-D-SECURITY-安全域.md`
- **域ID**: D-SECURITY
- **说明**: 已融合24-D-SECURITY(v2精炼版)+26-D-SECURITY(v1原始版)
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-028: 27-D-INTEGRATION-集成域.md（已融合v1+v2）

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\27-D-INTEGRATION-集成域.md`
- **域ID**: D-INTEGRATION
- **说明**: 已融合25-D-INTEGRATION(v2精炼版)+27-D-INTEGRATION(v1原始版)
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-029: 28-D-FRONTEND-前端域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\28-D-FRONTEND-前端域.md`
- **域ID**: D-FRONTEND
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-030: 29-D-GOVERNANCE-治理域.md（已融合v1+v2）

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\29-D-GOVERNANCE-治理域.md`
- **域ID**: D-GOVERNANCE
- **说明**: 已融合27-D-GOVERNANCE(v2精炼版)+29-D-GOVERNANCE(v1原始版)
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-031: 30-D-OPS-运维域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\30-D-OPS-运维域.md`
- **域ID**: D-OPS
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-032: 31-D-SELL-DECISION-卖出决策域.md

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\31-D-SELL-DECISION-卖出决策域.md`
- **域ID**: D-SELL-DECISION
- **分层标注**: 待执行
- **待执行**: STEP 1(标注) → STEP 3(核对) → STEP 5(验证)

### RA-033: 场内模块清单.csv

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\场内模块清单.csv`
- **内容**: 2,434条物理文件→blueprint_id映射
- **分层判定**: 全部`[全景]`（物理文件→模块映射关系）
- **待执行**: STEP 3(核对每条csv行→depgraph模块是否存在) → STEP 5(验证)

### RA-034: 旧版依赖图 project_entity_depgraph.yaml

- **源文件**: `D:\ZephyrAlpha\临时工作区\依赖图\project_entity_depgraph.yaml`
- **内容**: 28域138条边、域节点字段
- **分层判定**: 全部`[全景]`（域间依赖关系）
- **待执行**: STEP 3(逐域逐边核对depgraph v3) → STEP 5(验证)

### RA-035: 00-架构图总览与索引.md ✅ COMPLETED

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\00-架构图总览与索引.md`
- **状态**: ✅ 验证性审查完成

### RA-036: 交易决策架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\交易决策架构.md`
- **覆盖域**: D-DATA/D-FACTOR/D-SIGNAL/D-PF-CORE/D-PF-ALLOC/D-SELL-DECISION/D-POSITION/D-EX-CORE/D-EX-SOR/D-REPORTING/D-RISK/D-FRONTEND
- **状态**: ✅ v5.0深度审查完成(26项遗漏+2项概念不一致修正)

### RA-037: 治理架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\治理架构.md`
- **覆盖域**: D-GOVERNANCE
- **验证性审查**: ✅ 已完成(10项遗漏已补充)
- **v5.0深度审查**: ✅ R1完成(22项遗漏→8个annotation已写入)

### RA-038: 数据架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\数据架构.md`
- **覆盖域**: D-DATA/D-ALT-DATA/D-DATA-ENG
- **验证性审查**: ✅ 已完成(3项遗漏已补充)
- **v5.0深度审查**: ✅ R1完成(43项遗漏→15个annotation已写入)

### RA-039: 风险架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\风险架构.md`
- **覆盖域**: D-RISK
- **验证性审查**: ✅ 已完成(35条RD决策+AI-Agent风险治理层已补充)
- **v5.0深度审查**: ✅ R1完成(55项遗漏→8个annotation已写入)

### RA-040: 安全架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\安全架构.md`
- **覆盖域**: D-SECURITY
- **验证性审查**: ✅ 已完成(10项遗漏已补充)
- **v5.0深度审查**: ✅ R1完成(35项遗漏→8个annotation已写入)

### RA-041: 合规架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\合规架构.md`
- **覆盖域**: D-COMPLIANCE
- **验证性审查**: ✅ 已完成
- **v5.0深度审查**: ✅ R1完成(25项遗漏→8个annotation已写入)

### RA-042: Agent架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\Agent架构.md`
- **覆盖域**: D-AUTONOMY-CORE/D-AUTONOMY-PERM
- **验证性审查**: ✅ 已完成(5个核心维度已补充)
- **v5.0深度审查**: ✅ R1完成(21项遗漏→8个annotation已写入)

### RA-043: 学习系统架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\学习系统架构.md`
- **覆盖域**: D-ML-TRAIN/D-ML-SERVE/D-SIMULATION/D-RESEARCH/D-KNOWLEDGE
- **验证性审查**: ✅ 已完成(16项遗漏已补充)
- **v5.0深度审查**: ✅ R1完成(18项遗漏→6个annotation已写入)

### RA-044: 运维架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\运维架构.md`
- **覆盖域**: D-INFRA-RUNTIME/D-INFRA-OPS/D-OPS
- **验证性审查**: ✅ 已完成
- **v5.0深度审查**: ✅ R1完成(25项遗漏→8个annotation已写入+2项概念修正)

### RA-045: 集成架构.md ✅ COMPLETED v5.0

- **源文件**: `D:\ZephyrAlpha\临时工作区\架构图\集成架构.md`
- **覆盖域**: D-EX-SOR/D-CROSS-ASSET/D-TRADING/D-INTEGRATION
- **验证性审查**: ✅ 已完成(15项遗漏已补充)
- **v5.0深度审查**: ✅ R1完成(遗漏→8个annotation已写入)

---

## C. 执行顺序

### 反向审计执行顺序（先行）

按依赖深度排序（深度浅→深）：

| 顺序 | 卡片 | 域ID | 依赖深度 |
|:---:|------|------|:---:|
| 1 | RA-003 | D-DATA | 2 |
| 2 | RA-023 | D-AUTONOMY-CORE | 0 |
| 3 | RA-024 | D-AUTONOMY-PERM | 1 |
| 4 | RA-025 | D-INFRA-RUNTIME | 1 |
| 5 | RA-027 | D-SECURITY | 1 |
| 6 | RA-028 | D-INTEGRATION | 1 |
| 7 | RA-026 | D-INFRA-OPS | 2 |
| 8 | RA-015 | D-ALT-DATA | 2 |
| 9 | RA-016 | D-DATA-ENG | 2 |
| 10 | RA-013 | D-ML-TRAIN | 2 |
| 11 | RA-017 | D-CROSS-ASSET | 2 |
| 12 | RA-022 | D-KNOWLEDGE | 2 |
| 13 | RA-030 | D-GOVERNANCE | 2 |
| 14 | RA-031 | D-OPS | 2 |
| 15 | RA-004 | D-FACTOR | 3 |
| 16 | RA-012 | D-RISK | 3 |
| 17 | RA-014 | D-ML-SERVE | 3 |
| 18 | RA-018 | D-COMPLIANCE | 3 |
| 19 | RA-021 | D-RESEARCH | 3 |
| 20 | RA-005 | D-SIGNAL | 4 |
| 21 | RA-020 | D-SIMULATION | 4 |
| 22 | RA-006 | D-PF-CORE | 5 |
| 23 | RA-007 | D-PF-ALLOC | 6 |
| 24 | RA-032 | D-SELL-DECISION | 6 |
| 25 | RA-008 | D-POSITION | 7 |
| 26 | RA-009 | D-EX-CORE | 7 |
| 27 | RA-019 | D-TRADING | 7 |
| 28 | RA-010 | D-EX-SOR | 8 |
| 29 | RA-011 | D-REPORTING | 8 |
| 30 | RA-029 | D-FRONTEND | 8 |
| 31 | RA-033 | 场内模块清单.csv | — |
| 32 | RA-034 | 旧版depgraph.yaml | — |
| 33-45 | RA-035~045 | 架构图(11个) | — |

### 正向审计执行顺序（后行）

反向审计全部完成后，按依赖深度排序执行正向审计：

| 顺序 | 卡片 | 域ID | 依赖深度 |
|:---:|------|------|:---:|
| 1 | FA-021 | D-AUTONOMY-CORE | 0 |
| 2 | FA-022 | D-AUTONOMY-PERM | 1 |
| 3 | FA-023 | D-INFRA-RUNTIME | 1 |
| 4 | FA-025 | D-SECURITY | 1 |
| 5 | FA-026 | D-INTEGRATION | 1 |
| 6 | FA-008 | D-DATA | 2 |
| 7 | FA-024 | D-INFRA-OPS | 2 |
| 8 | FA-013 | D-ALT-DATA | 2 |
| 9 | FA-014 | D-DATA-ENG | 2 |
| 10 | FA-011 | D-ML-TRAIN | 2 |
| 11 | FA-015 | D-CROSS-ASSET | 2 |
| 12 | FA-020 | D-KNOWLEDGE | 2 |
| 13 | FA-028 | D-GOVERNANCE | 2 |
| 14 | FA-029 | D-OPS | 2 |
| 15 | FA-001 | D-FACTOR | 3 |
| 16 | FA-010 | D-RISK | 3 |
| 17 | FA-012 | D-ML-SERVE | 3 |
| 18 | FA-016 | D-COMPLIANCE | 3 |
| 19 | FA-019 | D-RESEARCH | 3 |
| 20 | FA-002 | D-SIGNAL | 4 |
| 21 | FA-018 | D-SIMULATION | 4 |
| 22 | FA-003 | D-PF-CORE | 5 |
| 23 | FA-004 | D-PF-ALLOC | 6 |
| 24 | FA-030 | D-SELL-DECISION | 6 |
| 25 | FA-005 | D-POSITION | 7 |
| 26 | FA-006 | D-EX-CORE | 7 |
| 27 | FA-017 | D-TRADING | 7 |
| 28 | FA-007 | D-EX-SOR | 8 |
| 29 | FA-009 | D-REPORTING | 8 |
| 30 | FA-027 | D-FRONTEND | 8 |
