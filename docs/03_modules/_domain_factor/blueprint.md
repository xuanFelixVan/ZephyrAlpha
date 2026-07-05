---
module_id: MOD-L02-001
submodule_path: src/zephyr/factor
title: "Alpha Factor Core 蓝图+施工图 — 因子工厂·C-027管理+C-009执行双角色"
doc_type: blueprint
status: Active
version: "4.0.0"
layer: L2_domain
layer_name: alpha_factor
functional_domain: intelligence
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: "2026-05-12"
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/factor/"
belongs_to: ""
parent_module: ""
codification_level: L1
codification_at: "2026-07-05"
last_verified: "2026-07-05"
last_updated: "2026-07-05"
generation: 3
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
business_layer_status: active
business_layer_blocked_reason: "C轨业务层已开放[ARCH-045 P0]。可施工。"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l02_alpha_factor.yaml"
    section: ""
    why: "架构层YAML真源"
depends_on:
  - target: MOD-L00-001
    at: "§4"
    why: "CTR-001 NormalizedMarketData"
  - target: MOD-INF-015
    at: "§10"
    why: "因子计算监控"
  - target: MOD-L03-001
    at: "§4,§3"
    why: "因子→信号域集成（CTR-002 FactorSignal）"
priority: P0
runtime_plane: hot
tags:
  - alpha-factor
  - l02
  - c-track
  - factor-factory
  - ocp-extension-point
summary: "因子工厂蓝图——C-027管理角色（发现/审批/入池/退役）+ C-009执行角色（盘前全量+盘中增量计算）。FactorBase OCP扩展点+FactorRegistry注册表+DSL算子+十阶段生命周期+双存储架构。因子输出标准化供D_SIGNAL消费。"
# ============================================================
# 子模块清单（蓝图内部使用，不进入blueprint_registry）
# 命名体系：D-FACTOR-XX（依赖图设计态子模块ID）
# 蓝图module_id保持MOD-L02-001（域级单一ID，SSoT）
# ============================================================
submodules:
  # ===== P0 核心骨架（FAC-CORE）=====
  - id: D-FACTOR-01
    name: Engine
    description: "因子计算引擎（FactorBase ABC + DSL + 增量计算 + DAG调度）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "factor_base.py + engine/"
  - id: D-FACTOR-02
    name: Registry
    description: "因子注册表（四维索引：名称/类别/状态/SLA + 因子元数据 + 版本树 + 血缘）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "factor_base.py FactorRegistry"
  - id: D-FACTOR-03
    name: Evaluation
    description: "因子评估（IC/IR + 过拟合3维度 + 多重回归校验 + OOS正率）"
    priority: P0
    construction_status: not_started
    gates: []
    corresponds_to: "services/evaluation/"
  - id: D-FACTOR-04
    name: Pipeline
    description: "因子管线（DAG调度 + 双模运行：盘前全量+盘中增量 + 背压）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "alpha_signal_pipeline.py"
  # ===== P1 扩展能力 =====
  - id: D-FACTOR-05
    name: Factor Mining Agent
    description: "AI因子挖掘（FactorMAD投票 + AST沙箱 + 进化式生成）"
    priority: P1
    construction_status: not_started
    gates: [GATE-05-01, GATE-05-02, GATE-05-03]
    corresponds_to: "services/mining/"
  - id: D-FACTOR-06
    name: Barra Risk Model
    description: "风格因子(10大)+行业因子(28申万)+中性化"
    priority: P1
    construction_status: not_started
    gates: [GATE-06-01, GATE-06-02, GATE-06-03]
    corresponds_to: "services/barra/"
  - id: D-FACTOR-07
    name: Governance Engine
    description: "因子治理引擎（准入门禁 + 运行时监控 + 废弃审批 + 漂移检测39类）"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/governance/"
  - id: D-FACTOR-08
    name: Decay Monitor
    description: "IC衰减监控（CUSUM控制图 + IC-Based Replacement 末位淘汰）"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/decay/"
  # ===== P2 分析能力 =====
  - id: D-FACTOR-09
    name: Correlation Analyzer
    description: "因子相关性分析 + 语义去重"
    priority: P2
    construction_status: not_started
    gates: []
    corresponds_to: "services/correlation/"
  - id: D-FACTOR-10
    name: Turnover Analyzer
    description: "换手率分析"
    priority: P2
    construction_status: not_started
    gates: []
    corresponds_to: "services/turnover/"
  - id: D-FACTOR-11
    name: Exposure Calculator
    description: "因子暴露实时计算"
    priority: P2
    construction_status: not_started
    gates: [GATE-11-01]
    corresponds_to: "services/exposure/"
  - id: D-FACTOR-24
    name: Factor Risk Budget Allocator
    description: "因子风险预算分配"
    priority: P2
    construction_status: not_started
    gates: [GATE-24-01, GATE-24-02]
    corresponds_to: "services/risk_budget/"
# ============================================================
# 因子池容量管理（ADR-FAC-006）
# ============================================================
factor_pool_capacity:
  n_max: 64                    # 运行上限
  design_capacity: 150         # 设计容量
  active_pool_max: 60          # 活跃池上限 (n_max-4)
  dormant_pool_max: 4          # 休眠池上限
  core_factors_exempt: true    # 核心因子(Fama-French等)不参与末位淘汰
# ============================================================
# 因子生命周期十阶段状态机
# ============================================================
factor_lifecycle:
  states:
    - CREATED                  # 已创建（代码已写，未验证）
    - VALIDATED                # 已验证（单元测试通过）
    - REGISTERED               # 已注册（FactorRegistry登记）
    - ONLINE                   # 在线（活跃池，参与计算）
    - MONITORED                # 监控中（IC/IR持续追踪）
    - DECAYING                 # 衰退中（IC低于阈值）
    - DEPRECATED               # 已废弃（不再参与计算）
    - DORMANT                  # 休眠（保留代码，不加载）
    - RETIRED                  # 退役（代码标记deprecated）
    - REACTIVATED              # 重激活（从DORMANT回到MONITORED）
  admission_gate:
    ic_threshold_price_volume: 0.03    # 量价因子IC入池阈值
    ic_threshold_fundamental: 0.02     # 基本面因子IC入池阈值
    ic_threshold_alternative: 0.025    # 另类因子IC入池阈值
    icir_threshold: 0.5                # ICIR入池阈值
    oos_positive_rate: 0.60            # OOS正率入池阈值
# ============================================================
# C-027管理角色 vs C-009执行角色 职责边界
# ============================================================
dual_role:
  c027_management:
    responsibility: "因子发现/解析/代码生成/IC回测/入池审批/退役"
    output: "因子代码 + 因子池"
    modules: [D-FACTOR-01, D-FACTOR-02, D-FACTOR-03, D-FACTOR-05, D-FACTOR-07]
  c009_execution:
    responsibility: "盘前全量计算/盘中增量修正/因子值输出"
    output: "因子值 + 信号"
    modules: [D-FACTOR-04]
    downstream: "D-SIGNAL"
  cycle_break: "C-009启动用默认因子列表快照，C-027异步注册新因子→时序分离无死锁"
# ============================================================
# 双存储架构（训练-服务一致性）
# ============================================================
dual_storage:
  offline:
    format: "Parquet + DuckDB"
    pit_query: "AS OF JOIN"
    latency: "~100ms"
    usage: "训练/回测"
  online:
    format: "Redis Hash"
    latency: "<5ms"
    usage: "推理"
  registry:
    format: "SQLite"
    content: "元数据 + 血缘 + 质量 + 版本"
  consistency: "同一 Engine.compute() 驱动两种存储写入 → 消除15-25%偏差"
---

> ✅ **业务层可施工声明**：本蓝图所属C轨业务层已开放[ARCH-045 P0]，可施工。
> AI 可自主施工。

> actual_disk_path: src/zephyr/factor/ (14 .py files, 含6个占位子包__init__.py)

# Alpha Factor Core 蓝图+施工图 — 因子工厂·C-027管理+C-009执行双角色

> module_id: MOD-L02-001 | version: 4.0.0 | status: active | domain: factor
> actual_disk_path: src/zephyr/factor/ | generation: 3 | construction_progress: partially_implemented
> 子模块体系: D-FACTOR-01~11+24（蓝图内部编号，不进blueprint_registry）

## 概述

本蓝图描述 ZephyrAlpha **因子工厂**——采用 C-027 管理角色（发现/审批/入池/退役）+ C-009 执行角色（盘前全量+盘中增量计算）双角色架构。核心职责包括：

- **管理角色（C-027）**：FactorBase OCP扩展点 + FactorRegistry注册表（四维索引） + 因子评估（IC/IR） + AI因子挖掘 + 因子治理引擎（39类漂移检测）
- **执行角色（C-009）**：因子管线（DAG调度 + 双模运行：盘前全量+盘中增量） + 因子值输出

当前规模 2 个因子（Momentum20d + ValueFactor）+ 8 个占位子包，目标容量 N_max≈64（活跃池≤60 + 休眠池≤4）。上游依赖 D_DATA 的 CTR-001 NormalizedMarketData，下游被 D_SIGNAL（消费 CTR-002 FactorSignal）和 D_RISK（消费因子值）使用。

**双角色循环依赖破解**：C-009 启动用默认因子列表快照，C-027 异步注册新因子 → 时序分离无死锁。

**双存储架构**：离线 Parquet+DuckDB（PIT AS OF JOIN，~100ms，训练/回测）+ 在线 Redis Hash（<5ms，推理）+ SQLite 注册表（元数据+血缘+版本）。同一 Engine.compute() 驱动两种存储写入 → 消除 15-25% 偏差。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L02-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | factor_base.py | §3.1/§4.1 | FactorBase OCP扩展点+FactorMeta+FactorRegistry+autodiscover_factors | 已实现 |
| 2 | base.py | §3.1 | 旧版FactorBase（已被factor_base.py取代） | 已实现(待废弃) |
| 3 | momentum_factor.py | §3.1 | Momentum20d动量因子实现 | 已实现 |
| 4 | value_factor.py | §3.1 | ValueFactor估值因子实现 | 已实现 |
| 5 | alpha_signal_pipeline.py | §3.1/§16.3 | 因子管线（D-FACTOR-04 Pipeline骨架） | 已实现 |
| 6 | bus_factor_defense.py | §3.1 | 防御性因子（业务扩展） | 已实现 |
| 7 | __init__.py | — | 包入口，导出FactorBase/FactorMeta/FactorRegistry/autodiscover_factors | 已实现 |
| 8 | engine/__init__.py | §3.1 | D-FACTOR-01 Engine子包入口（占位） | 占位 |
| 9 | ctr_001_consumer/__init__.py | §3.1 | CTR-001消费者子包入口（占位） | 占位 |
| 10 | _extensions/__init__.py | — | 扩展点子包入口（占位） | 占位 |
| 11 | services/__init__.py | §3.1 | D-FACTOR-03/05/07/08/09/10/11/24 服务子包入口（占位） | 占位 |
| 12 | infrastructure/__init__.py | — | 基础设施子包入口（占位） | 占位 |
| 13 | core/__init__.py | — | 核心子包入口（占位） | 占位 |
| 14 | api/__init__.py | — | API子包入口（占位） | 占位 |

> **注**：factors/ 子目录在v3.0.0版本中规划但未实际创建，因子实现文件（momentum_factor.py/value_factor.py）已平铺在 src/zephyr/factor/ 根目录。后续如需重新组织可考虑迁移。

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| 代码[BLUEPRINT]字段指向MOD-L02-001 | `grep BLUEPRINT *.py` | ☐(v4.0.0蓝图已修正，代码层待同步) |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (占位) | 无 | 全部 | partially_implemented |
| v2.1.0 (模板升级) | FactorBase+FactorRegistry+Momentum20d+ValueFactor | base.py清理 | 结构升级 |
| v3.0.0 (审查回填) | 同v2.1.0 | base.py废弃迁移 | 代码-蓝图对齐修正 |

---

## §1 设计背景与目标

### 1.1 背景

Alpha因子是量化投资的核心输入——因子质量直接决定信号质量。当前痛点：因子计算逻辑分散在各处、接口不统一、新增因子需要修改多处代码。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | FactorBase OCP扩展点 | 新因子只加不改 |
| 2 | ✅ 包含 | FactorRegistry因子注册表 | 因子自动发现+按域查询 |
| 3 | ✅ 包含 | 动量/价值因子实现 | Momentum20d+ValueFactor可计算 |
| 4 | ✅ 包含 | 因子输出标准化 | CTR-002 FactorSignal供D_SIGNAL消费 |
| 5 | ❌ 排除 | 数据摄取 | D_DATA Data Source |
| 6 | ❌ 排除 | 信号生成 | D_SIGNAL Signal Generation |
| 7 | ❌ 排除 | 组合构建 | D_PORTFOLIO_CORE Portfolio Construction |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 因子计算必须向量化 | 禁止逐行循环，必须使用NumPy/Pandas |
| 数据缺失时因子输出NaN | 下游必须处理NaN |
| 因子计算延迟<100ms | 实时因子必须在100ms内完成 |
| C轨已开放 | 业务代码可施工 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 因子架构决策 | 设计+施工 | 审批FactorBase接口变更 |
| D_SIGNAL Signal | 因子输出格式 | 集成 | 消费CTR-002 |
| D_RISK Risk | 因子值准确性 | 集成 | 因子用于风控指标 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 因子数量 | 2 | 20+ | 缺少行业/另类因子 | P2 |
| 因子注册 | FactorRegistry单例 | 分布式注册 | 单进程限制 | P2 |
| 因子缓存 | 无 | FactorCache | 重复计算浪费 | P2 |
| base.py | 旧版FactorBase | 废弃 | 双FactorBase共存 | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 新增因子 | 研究员提出新因子 | 继承FactorBase→实现compute→@FactorRegistry.register→autodiscover自动加载 | 因子可计算 |
| 因子计算 | D_DATA推送行情数据 | data传入compute()→向量化计算→返回pd.Series | CTR-002 FactorSignal |
| 因子查询 | D_SIGNAL需要某域因子 | FactorRegistry.list_by_domain()→获取因子类→调用compute | 因子值列表 |
| 因子入池 | 新因子IC通过阈值 | C-027提交→IC/IR评估→OOS正率校验→治理引擎审批→入活跃池 | 因子状态=ONLINE |
| 因子退役 | IC持续低于阈值 | Decay Monitor触发CUSUM告警→治理引擎审批→DEPRECATED→DORMANT→RETIRED | 因子状态=RETIRED |
| 盘前全量计算 | 09:00盘前 | C-009 Pipeline启动→加载活跃池→全量计算→写离线Parquet+在线Redis | 因子值双写 |
| 盘中增量修正 | 09:30-15:00 | tick事件触发→incremental_compute()→增量更新Redis | 实时因子值 |

### 1.8 子模块清单（D-FACTOR-XX 体系）

> **命名体系说明**：子模块编号 D-FACTOR-XX 是**蓝图内部编号**，用于门禁挂载和契约落点，**不进入 blueprint_registry**。蓝图 module_id 保持 MOD-L02-001（域级单一ID，SSoT）。详见 frontmatter `submodules` 字段。

#### 1.8.1 P0 核心骨架（FAC-CORE）

| 子模块ID | 名称 | 职责 | 优先级 | 建设状态 | 受限门禁 |
|---------|------|------|:------:|:-------:|---------|
| D-FACTOR-01 | Engine | 因子计算引擎（FactorBase ABC + DSL + 增量计算 + DAG调度） | P0 | partially_implemented | — |
| D-FACTOR-02 | Registry | 因子注册表（四维索引：名称/类别/状态/SLA + 元数据 + 版本树 + 血缘） | P0 | partially_implemented | — |
| D-FACTOR-03 | Evaluation | 因子评估（IC/IR + 过拟合3维度 + 多重回归校验 + OOS正率） | P0 | not_started | — |
| D-FACTOR-04 | Pipeline | 因子管线（DAG调度 + 双模运行：盘前全量+盘中增量 + 背压） | P0 | partially_implemented | — |

#### 1.8.2 P1 扩展能力

| 子模块ID | 名称 | 职责 | 优先级 | 建设状态 | 受限门禁 |
|---------|------|------|:------:|:-------:|---------|
| D-FACTOR-05 | Factor Mining Agent | AI因子挖掘（FactorMAD投票 + AST沙箱 + 进化式生成） | P1 | not_started | GATE-05-01~03 |
| D-FACTOR-06 | Barra Risk Model | 风格因子(10大)+行业因子(28申万)+中性化 | P1 | not_started | GATE-06-01~03 |
| D-FACTOR-07 | Governance Engine | 因子治理（准入门禁 + 运行时监控 + 废弃审批 + 漂移检测39类） | P1 | not_started | — |
| D-FACTOR-08 | Decay Monitor | IC衰减监控（CUSUM控制图 + IC-Based Replacement 末位淘汰） | P1 | not_started | — |

#### 1.8.3 P2 分析能力

| 子模块ID | 名称 | 职责 | 优先级 | 建设状态 | 受限门禁 |
|---------|------|------|:------:|:-------:|---------|
| D-FACTOR-09 | Correlation Analyzer | 因子相关性分析 + 语义去重 | P2 | not_started | — |
| D-FACTOR-10 | Turnover Analyzer | 换手率分析 | P2 | not_started | — |
| D-FACTOR-11 | Exposure Calculator | 因子暴露实时计算 | P2 | not_started | GATE-11-01（需D-FACTOR-06就绪） |
| D-FACTOR-24 | Factor Risk Budget Allocator | 因子风险预算分配 | P2 | not_started | GATE-24-01（需06+11就绪）/ GATE-24-02（需D-RISK就绪） |

#### 1.8.4 C-027 vs C-009 双角色职责边界

| 维度 | C-027 因子工厂（管理角色） | C-009 生产线（执行角色） |
|------|----------------------|---------------------|
| 职责 | 因子发现/解析/代码生成/IC回测/入池审批/退役 | 盘前全量计算/盘中增量修正/因子值输出 |
| 产出 | 因子代码 + 因子池 | 因子值 + 信号 |
| 对应子模块 | D-FACTOR-01/02/03/05/07 | D-FACTOR-04 + 下游 D-SIGNAL |
| 循环依赖破解 | C-009启动用默认因子列表快照，C-027异步注册新因子→时序分离无死锁 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 因子抽象基类 | FactorBase OCP扩展点+FactorMeta元数据 | 本模块 |
| 2 | ✅ 包含 | 因子注册表 | FactorRegistry单例+autodiscover自动发现 | 本模块 |
| 3 | ✅ 包含 | 具体因子实现 | Momentum20d+ValueFactor | 本模块 |
| 4 | ❌ 排除 | 行情数据获取 | D_DATA Data Source负责 | D_DATA |
| 5 | ❌ 排除 | 信号合成 | D_SIGNAL Signal Generation负责 | D_SIGNAL |
| 6 | ❌ 排除 | 风险评估 | D_RISK Risk Management负责 | D_RISK |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | FactorBase | 因子OCP扩展点(abc.ABC) | — | 继承 |
| 2 | FactorMeta | 因子元数据定义 | — | 数据类 |
| 3 | FactorRegistry | 因子注册表(单例) | FactorBase | 装饰器注册 |
| 4 | autodiscover_factors | 因子自动发现 | FactorRegistry | pkgutil扫描 |
| 5 | Momentum20d | 20日动量因子 | FactorBase | 继承+注册 |
| 6 | ValueFactor | 估值因子 | FactorBase | 继承+注册 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_DATA NormalizedMarketData(pd.DataFrame) | FactorBase.compute()→向量化计算 | D_SIGNAL/D_RISK | pd.Series(CTR-002 FactorSignal) |

### 3.3 状态生命周期

本模块无状态机。FactorRegistry为进程级单例，随Python进程生命周期。

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。
> 注：当前代码使用 `@dataclass` 定义 FactorMeta，需迁移至 Pydantic BaseModel。

### 4.1 公共 API

```python
class FactorBase(abc.ABC):
    meta: ClassVar[FactorMeta]
    @abc.abstractmethod
    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series: ...
    def validate(self, data: pd.DataFrame) -> bool: ...

class FactorRegistry:
    @classmethod
    def register(cls, factor_cls: type[FactorBase]) -> type[FactorBase]: ...
    @classmethod
    def get(cls, factor_id: str) -> type[FactorBase]: ...
    @classmethod
    def list_all(cls) -> list[FactorMeta]: ...
    @classmethod
    def list_by_domain(cls, domain: str) -> list[FactorMeta]: ...

def autodiscover_factors(package_path: str | None = None) -> None: ...
```

### 4.2 数据模型

```python
class FactorMeta(BaseModel):
    factor_id: str = Field(..., description="全局唯一因子ID，如 momentum_20d")
    name: str = Field(..., description="人类可读名称")
    domain: str = Field(..., description="所属域: technical/fundamental/alternative/macro")
    version: str = Field(default="1.0.0", description="语义版本号")
    description: str = Field(default="", description="因子说明")
    dependencies: list[str] = Field(default_factory=list, description="依赖的其他因子ID")
    tags: list[str] = Field(default_factory=list, description="标签")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `compute()` | `data` | ✅ | pd.DataFrame，index为datetime，columns至少含OHLCV |
| `compute()` | `**kwargs` | ❌ | 扩展参数(如window/earnings_per_share) |
| `validate()` | `data` | ✅ | 同compute()输入 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `compute()` | `pd.Series`(index与data对齐，值为因子截面得分) | NaN(数据缺失时) |
| `validate()` | `bool`(True=通过) | `False` |
| `FactorRegistry.get()` | `type[FactorBase]` | `KeyError`(因子未注册) |
| `FactorRegistry.register()` | `type[FactorBase]`(原类) | `ValueError`(ID重复)/`AttributeError`(缺meta) |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增Factor子类 | ✅ 向后兼容 | OCP扩展 |
| FactorMeta新增字段 | ✅ 向后兼容 | 不影响已有消费者 |
| FactorMeta删除字段 | ❌ 破坏性 | 需Owner审批+迁移方案 |
| compute()签名变更 | ❌ 破坏性 | 需Owner审批 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | FactorBase为OCP扩展点 | 新因子只加不改 |
| 2 | 因子输入必须为pd.DataFrame | D_DATA标准化输出 |
| 3 | 因子计算必须向量化 | NumPy/Pandas，禁止逐行循环 |
| 4 | FactorRegistry为单例 | 进程级唯一 |
| 5 | 因子必须通过@FactorRegistry.register注册 | autodiscover自动发现 |
| 6 | 禁止look-ahead bias | 因子计算不得使用未来数据 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 因子数量 | 2 | 20 | 无上限 | ✅ | OCP扩展 |
| 计算延迟 | <100ms | <50ms | NumPy限制 | ✅ | 缓存+预计算 |
| 注册表内存 | <1KB | <100KB | Python进程内存 | ✅ | — |

### 5.3 迁移

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | base.py(旧版FactorBase) | `src/zephyr/factor/base.py` | 删除 | 标记deprecated→Phase2物理删除 | Grep全项目引用base.py→更新为factor_base.py |

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 因子计算成功率 | 99.9% | 计算结果非NaN率 | 非NaN率 | 99.9% | 每月允许0.1%NaN | NaN率>1% |
| 可维护性 | 新因子接入时间 | <30min | 从继承到注册耗时 | — | — | — | — |
| 性能 | 因子计算延迟 | P95<100ms | 性能测试 | P95延迟 | <100ms | — | P95>200ms |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 逐行循环计算因子 | NumPy/Pandas向量化 | 性能瓶颈 |
| 2 | 编码模式 | look-ahead bias | 仅使用历史数据 | 因子失效 |
| 3 | 导入源 | zephyr.signal.* | zephyr.factor.* | 分层约束：D_FACTOR不依赖D_SIGNAL |
| 4 | 编码模式 | 直接实例化因子类 | @FactorRegistry.register装饰器 | 注册表完整性 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 数据缺失导致因子NaN | NaN检测 | 缺失值填充+下游处理NaN | 因子输出不可用 |
| 2 | 因子计算超时 | 超时监控 | 降级为缓存值 | 实时性不足 |
| 3 | 因子计算异常 | try/except捕获 | 返回NaN+告警 | 下游需处理 |
| 4 | 因子ID重复注册 | FactorRegistry.register校验 | 抛出ValueError | 注册失败 |
| 5 | 因子缺meta属性 | FactorRegistry.register校验 | 抛出AttributeError | 注册失败 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| factor_compute_duration_seconds | Histogram | 自动埋点 | P95>200ms | P2 |
| factor_nan_rate | Gauge | 自动埋点 | >1% | P1 |
| factor_registry_count | Gauge | 注册时上报 | — | — |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| FactorRegistry | 无 | 所有因子计算 | 进程重启+autodiscover | 注册表重建 |
| 单个因子 | 其他因子可用 | 该因子输出NaN | 下游跳过NaN | 因子修复 |
| D_DATA数据源 | 缓存数据可用 | 实时因子 | 使用最近缓存值 | D_DATA恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 因子计算逻辑错误 | 高 | 单元测试+因子值回归测试 | 覆盖率>80% |
| 2 | look-ahead bias | 高 | validate()校验+代码审查 | 回归测试无未来数据泄露 |
| 3 | 因子注册表污染 | 中 | FactorRegistry.register重复ID校验 | 重复注册抛ValueError |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | FactorBase/FactorRegistry/Momentum20d/ValueFactor | compute返回pd.Series;注册/查询/重复注册 | 覆盖率>80% |
| 2 | 回归测试 | 因子值稳定性 | 固定输入→固定输出 | 值偏差<1e-6 |
| 3 | 集成测试 | autodiscover_factors | 自动发现+注册 | 所有因子自动加载 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L00-001 Data Source | 必须 | CTR-001 NormalizedMarketData | — | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |
| MOD-INF-015 Telemetry | 可选 | 因子计算监控 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\system_telemetry\blueprint.md` |
| MOD-L03-001 Signal Generation | 必须 | 因子→信号域集成（CTR-002 FactorSignal） | v3.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_signal\blueprint.md` |
| MOD-L11-001 ML Platform | 可选 | ModelPrediction因子增强 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` |
| D-RISK Risk Management | 可选 | 因子值消费（风控指标） | — | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` |

> **注**：v3.0.0 中的 `MOD-ALPHA_SIGNAL_DOMAIN` 依赖已移除（域已拆分为 D_FACTOR + D_SIGNAL 两个平级独立域，详见 [contract_mapping_table.yaml v1.1.0](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/contract_mapping_table.yaml) 变更记录）。

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.11 | 蓝图声明的每个依赖在依赖图中有对应节点 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-L02-001` |
| 2 | §11 产出物路径 ↔ 依赖图 §5 模块归属表 | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

**执行顺序依赖**：

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| factor_base.py | factors/momentum_factor.py | FactorBase定义 | import成功 |
| factor_base.py | factors/value_factor.py | FactorBase定义 | import成功 |

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| factor_base.py | factors/*.py | FactorBase抽象类 | 继承 |
| factors/*.py | FactorRegistry | 因子类 | 装饰器注册 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块简单，手动维护 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防漂移 | CI门禁 | validate_path_alignment.py | — | CI门禁 | PR提交时 |
| 3 | 因子注册自动发现 | 是 | 新因子自动加载 | autodiscover_factors | 已实现 | — | __init__.py | 包导入时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\factor\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\factor\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_DATA Data Source | CTR-001消费 | NormalizedMarketData(pd.DataFrame) | 因子可读取行情数据 |
| D_SIGNAL Signal Generation | 因子产出 | CTR-002 FactorSignal(pd.Series) | 信号合成可消费因子结果 |
| D_RISK Risk Management | 因子值消费 | CTR-002 FactorSignal | 风控指标可使用因子值 |
| INF-015 Telemetry | instrumentation | 因子计算指标 | 指标可观测 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress+version更新 | 进度变更 |
| 2 | 架构层YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l02_alpha_factor.yaml` | 补充factors/子目录文件 | 文件清单同步 |
| 3 | 代码文件头部 | `D:\ZephyrAlpha\src\zephyr\factor\*.py` | [BLUEPRINT]指向MOD-L02-001 | 当前指向alpha_signal_domain-001，漂移 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 因子计算性能瓶颈 | 中 | 实时性不足 | 向量化计算+缓存 | 风险 |
| 2 | 数据缺失导致因子失效 | 中 | 因子输出NaN | 缺失值处理+下游NaN容忍 | 风险 |
| 3 | 新因子需实现FactorBase | — | 中 | OCP扩展点设计，新因子继承即可 | 负面后果 |
| 4 | 因子计算依赖D_DATA数据质量 | — | 中 | QualityGate前置校验 | 负面后果 |
| 5 | base.py与factor_base.py双FactorBase共存 | 高 | 导入混乱 | 废弃base.py | 风险 |
| 6 | FactorMeta使用@dataclass而非Pydantic BaseModel | 中 | 违反KBG-0040 | 迁移至Pydantic | 风险 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | business_layer_status = active → 确认可施工 | 检查frontmatter | ☑ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 渐进式 |
| 核心风险 | 因子计算正确性+代码-蓝图对齐 |
| 目标 generation | 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | FactorBase定义 | hard | ✅ | ✅ |
| 2 | CTR-001 NormalizedMarketData | hard | ⚠️ D_DATA部分实现 | ☐ |
| 3 | business_layer_status=active | hard | ✅ active | ☑ |

### 16.3 实施步骤

#### 步骤 1：修正代码[BLUEPRINT]字段

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §0.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\factor\*.py` |
| 验收标准 | 所有.py文件[BLUEPRINT]字段指向MOD-L02-001 |
| 验证命令 | `grep -r "BLUEPRINT" src/zephyr/factor/` |
| G7 检查项 | 所有6个.py文件已修正 |
| AI 自治范围 | ai_modifiable |
| 检查点 | grep输出全部包含MOD-L02-001 |

**创建文件清单**：无新建文件，修改现有文件头部。

#### 步骤 2：废弃base.py

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5.3 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\factor\base.py` |
| 验收标准 | base.py标记deprecated，无其他模块引用 |
| 验证命令 | `grep -r "from.*base import\|from.*factor.base" src/zephyr/` |
| G7 检查项 | 无外部引用base.py |
| AI 自治范围 | human_gated |
| 检查点 | grep无结果 |

#### 步骤 3：FactorMeta迁移至Pydantic BaseModel

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\factor\factor_base.py` |
| 验收标准 | FactorMeta继承BaseModel，所有字段有Field(description) |
| 验证命令 | `python -c "from zephyr.factor.factor_base import FactorMeta; print(FactorMeta.model_fields)"` |
| G7 检查项 | Momentum20d/ValueFactor仍可正常注册 |
| AI 自治范围 | human_gated |
| 检查点 | import成功+FactorRegistry.list_all()返回2个因子 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | [BLUEPRINT]字段修正导致导入错误 | 还原[BLUEPRINT]字段 |
| 2 | base.py废弃导致引用断裂 | 恢复base.py |
| 3 | FactorMeta迁移导致因子注册失败 | 还原@dataclass版本 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 所有.py文件[BLUEPRINT]指向MOD-L02-001 | grep确认 | 完成 | ☐ |
| 2 | base.py已标记deprecated | 文件存在+注释标记 | 完成 | ☐ |
| 3 | FactorMeta为Pydantic BaseModel | import成功 | 完成 | ☐ |
| 4 | SLO已定义且可测量 | §5.4每项SLI有测量方式 | 就绪 | ☐ |
| 5 | 回滚方案已验证 | §16.4回滚操作可执行 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 动量因子计算 | 算法 | `data["close"].pct_change(window)` | `factors/momentum_factor.py` |
| 2 | 估值因子计算 | 算法 | `1 / (avg_price / earnings_estimate)` | `factors/value_factor.py` |
| 3 | 因子注册 | 协议 | `@FactorRegistry.register`装饰器→`_registry[factor_id] = factor_cls` | `factor_base.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -c "from zephyr.factor import FactorRegistry; FactorRegistry.list_all()"` | 列出所有注册因子 | — | FactorMeta列表 |
| 2 | 命令 | `python -c "from zephyr.factor import autodiscover_factors; autodiscover_factors()"` | 触发因子自动发现 | `package_path: 可选` | 无输出，副作用注册 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 因子注册失败 | @register抛ValueError | 检查factor_id是否重复 | 修改factor_id | 重新注册 |
| 2 | 运行 | 因子计算全NaN | 数据缺失 | 检查D_DATA数据源 | 恢复数据源 | 因子值恢复 |
| 3 | 运行 | autodiscover加载失败 | 因子模块语法错误 | 检查warnings输出 | 修复语法 | 重新autodiscover |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同因子ID并发注册 | FactorRegistry.register校验 | 后注册者抛ValueError | — |
| 多AI Session同时新增因子 | factor_id唯一性 | 先注册者胜出 | — |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 因子数量 | 2 | `len(FactorRegistry)` |
| 计算延迟 | <100ms | 性能测试 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L02-001 | 因子数量增长后计算延迟 | 因子缓存+预计算 | P2 | 因子>10或延迟>50ms | v3.1.0 | 待施工 |
| GAP-L02-002 | FactorMeta使用@dataclass | 迁移至Pydantic BaseModel | P1 | KBG-0040合规 | v3.0.0 | 待施工 |
| GAP-L02-003 | base.py旧版FactorBase | 废弃迁移 | P1 | 代码清洁度 | v3.0.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 占位 | partially_implemented | ❌ |
| v2.1.0 | 2 | 模板升级 | §0前移+§7/§15删除+§10拆分 | ⚠️ |
| v3.0.0 | 2 | 审查回填 | 代码-蓝图对齐+模板合规回填 | ⚠️ |
| v4.0.0 | 3 | 工厂体系升级 | 子模块清单(D-FACTOR-01~11+24)+双角色架构(C-027/C-009)+十阶段生命周期+双存储+因子池容量+§0.1对齐14文件 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| FactorCache | GAP-L02-001 | factor_cache.py | Phase 3 | 待施工 |
| FactorMeta Pydantic迁移 | GAP-L02-002 | factor_base.py | Phase 1 | 待施工 |
| base.py废弃 | GAP-L02-003 | base.py | Phase 1 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L02-01 | FactorBase使用OCP扩展点 | 继承/注册表/直接调用 | 继承 | 新因子只加不改 | 2026-05-05 |
| 2 | D-L02-02 | 因子输出格式为pd.Series | dict/Pydantic/dataclass | pd.Series | 向量化计算需要 | 2026-05-05 |
| 3 | D-L02-03 | FactorRegistry使用装饰器注册 | 手动注册/装饰器/配置文件 | 装饰器 | autodiscover自动发现 | 2026-05-05 |
| 4 | D-L02-04 | FactorMeta使用@dataclass(待迁移Pydantic) | @dataclass/Pydantic | @dataclass→Pydantic | KBG-0040强制Pydantic V2 | 2026-05-05 |
| 5 | D-L02-05 | compute()输入为pd.DataFrame | NormalizedMarketData/pd.DataFrame | pd.DataFrame | D_DATA产出为DataFrame | 2026-05-05 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| FactorBase | 因子抽象基类，OCP扩展点 | base.py中的旧FactorBase | factor_base.py为新版，base.py待废弃 |
| FactorRegistry | 因子全局注册表(单例) | — | 唯一注册入口 |
| FactorMeta | 因子元数据定义 | — | 每个因子类必须有meta类属性 |
| CTR-002 | 因子信号契约(FactorSignal) | CTR-001(NormalizedMarketData) | CTR-002是D_FACTOR产出，CTR-001是D_DATA产出 |
| OCP | 开闭原则(Open-Closed Principle) | — | 新因子只加不改 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 代码[BLUEPRINT]指向alpha_signal_domain-001而非MOD-L02-001 | 高 | 初始代码生成时未对齐蓝图ID | 修正[BLUEPRINT]字段 | §0.2 | 待解决 |
| 2 | base.py与factor_base.py双FactorBase共存 | 高 | 旧版未清理 | 废弃base.py | §5.3 | 待解决 |
| 3 | FactorMeta使用@dataclass违反KBG-0040 | 中 | 初始实现未遵循Pydantic要求 | 迁移至Pydantic BaseModel | §4.2 | 待解决 |
| 4 | compute()签名蓝图与代码不一致 | 高 | 蓝图写NormalizedMarketData，代码用pd.DataFrame | 蓝图修正为pd.DataFrame | §4.1 | 已解决(v3.0.0) |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3每个组件在§4有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4每个接口在§16有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5每个约束在§9有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1每个代码文件在§11有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10每个依赖在dependency_path_panorama.md有对应条目 | 逐依赖核对 | ✅ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 已知问题中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 9 | 中 | 每步施工后执行验证命令 | exit 0才进下一步 | ☐ |
| 10 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 11 | 后 | §0代码对齐验证已更新 | construction_progress与实际一致 | ☐ |
| 12 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | FactorBase接口变更需Owner审批 | OCP扩展点已稳定 |
| 接口契约 | evolving | 中 | compute()签名已修正，FactorMeta待迁移Pydantic | 数据模型待规范化 |
| 数据模型 | evolving | 中 | FactorMeta迁移Pydantic后升级为stable | @dataclass→Pydantic |
| 施工步骤 | evolving | 中 | 3步施工完成后升级为stable | 代码-蓝图对齐修正 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 占位蓝图(blocked) | — | 已完成 |
| v2.1.0 | 模板升级+初步实现 | v0.1.0 | 已完成 |
| v3.0.0 | 审查回填+代码-蓝图对齐 | v2.1.0 | 已完成 |
| v4.0.0 | 工厂体系升级：子模块清单+双角色+生命周期+双存储+因子池容量 | v3.0.0 | 蓝图就绪，待施工 |
| v4.1.0 | D-FACTOR-03 Evaluation + D-FACTOR-07 Governance 实现 | v4.0.0 | 待施工 |
| v4.2.0 | D-FACTOR-05 Mining Agent + D-FACTOR-08 Decay Monitor 实现 | v4.1.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 实现与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责混乱 |
| 16 | 术语表不可省略 | 术语理解漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格MUST保留在§16.7 | 关键逻辑实现错误 |
| 18 | 对标验证表格保留，对标散文删除 | 噪音淹没关键信息 |
| 19 | SLO必须定义 | 容错策略无依据 |
| 20 | 可观测性不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明 | 部分失败行为不可预测 |

### 蓝图拆分判定标准

**判定流程**：
1. 当前蓝图是否包含 ≥2 个独立职责域？→ 否 → 不拆分
2. 各职责域是否各自有独立的消费者和演进节奏？→ 否 → 不拆分
3. 拆分后各蓝图是否各自自包含（接口+依赖+施工）？→ 是 → 拆分

| 判定示例 | 职责域数量 | 消费者独立？ | 演进独立？ | 结论 |
|---------|:---:|:---:|:---:|------|
| 因子计算层（本蓝图） | 1 | 否 | 否 | 不拆分 |
| 假设：因子计算+因子存储 | 2 | 是 | 是 | 拆分为 D_FACTOR-FactorCompute + D_FACTOR-FactorStore |
| 假设：因子计算+因子回测 | 2 | 否 | 否 | 不拆分（职责紧密） |

---

## ⚠️ 安全删除协议

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 安全删除方案 |
|---|---------------|------------|---------|------------|
| 1 | base.py | `D:\ZephyrAlpha\src\zephyr\factor\base.py` | 废弃型 | 标记deprecated→确认无引用→Phase2物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 物理删除只能在stable搬入阶段执行 | 给足缓冲期 |
| 3 | 物理删除必须人类确认 | AI不得自行决定删除文件 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| — | 无 | — | — | — |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | factor_base.py | `D:\ZephyrAlpha\src\zephyr\factor\factor_base.py` | 修改 | FactorMeta迁移Pydantic |
| 2 | base.py | `D:\ZephyrAlpha\src\zephyr\factor\base.py` | 废弃 | 标记deprecated |
| 3 | factors/momentum_factor.py | `D:\ZephyrAlpha\src\zephyr\factor\factors\momentum_factor.py` | 修改 | [BLUEPRINT]字段修正 |
| 4 | factors/value_factor.py | `D:\ZephyrAlpha\src\zephyr\factor\factors\value_factor.py` | 修改 | [BLUEPRINT]字段修正 |
| 5 | __init__.py | `D:\ZephyrAlpha\src\zephyr\factor\__init__.py` | 修改 | [BLUEPRINT]字段修正 |
| 6 | factors/__init__.py | `D:\ZephyrAlpha\src\zephyr\factor\factors\__init__.py` | 修改 | [BLUEPRINT]字段修正 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图的核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 本模块的施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块的接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | D_SIGNAL Signal Generation | §4 接口契约、§10 依赖关系 |
| Tier 1 | D_RISK Risk Management | CTR-002 FactorSignal |
| Tier 2 | D_RESEARCH Research | 因子回测 |
| Tier 3 | INF-015 Telemetry | 因子计算指标 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步（下游蓝图） | Tier 2 同步（集成系统） |
|---------|---------|---------------------|---------------------|
| 接口契约新增/修改（§4） | 需Owner审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需Owner审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需§0对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调（命令、路径修正） | AI可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充（风险缓解、后果描述） | AI可自主修改 | — | — |
| 容量升级方案新增（§17） | 需Owner审批 | 下游评估影响 | 更新容量预算 |

---

## 变更记录

> 变更历史通过 Git log 追踪。
