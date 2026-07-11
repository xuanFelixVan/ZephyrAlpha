---
module_id: MOD-L11-001
submodule_path: src/zephyr/ml_train
title: "ML Platform Core 蓝图+施工图 — 机器学习平台"
doc_type: blueprint
status: Active
version: "2.1.0"
layer: L2_domain
functional_domain: research
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-12"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/ml_train/"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 2
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-15"
summary: "ML平台层。InferenceEngineBase OCP扩展点+ModelMetadata/InferenceResult数据类。Phase B骨架已就位。业务层已开放，可施工。"
rule_form: structural
scope: module
stability: evolving
verifiability: manual
depends_on:
  - target: MOD-INF-016
    at: §10
    why: Shared Core 承载
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\04_architecture_principles_decisions\\dependency_path_panorama.md"
    section: §3.13
    why: D_ML_TRAIN ML平台子模块级依赖图
tags: [ml-platform, l11, c-track, placeholder]
priority: P1
runtime_plane: warm
ssot_yaml: "architecture_model/layers/l11_ml_platform.yaml"
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

> ✅ **业务层已开放，可施工** — 本蓝图处于 C 轨占位状态，当前仅有 Phase B 骨架代码，可启动新施工。待 B 轨容量升级完成后按 ARB-11 三梯队策略激活。

> module_id: MOD-L11-001 | version: 2.1.0 | status: active | domain: ml_train
> actual_disk_path: src/zephyr/ml_train/ | generation: 2 | construction_progress: partially_implemented

# ML Platform Core 蓝图+施工图 — 机器学习平台

## 概述

本蓝图描述 ZephyrAlpha 机器学习平台核心层——它解决了模型推理标准化和模型注册管理问题。核心职责包括：模型推理(InferenceEngineBase OCP扩展点)、模型注册(ModelRegistry版本生命周期管理)、模型训练(ModelTrainerBase OCP扩展点)、模型元数据(ModelMetadata数据类)。当前规模 4 个核心类 + 1 个默认实现，目标容量为完整 ML 生命周期管理（6子模块：training/validation/serving-default/serving-hot/evaluation/scout）。上游依赖 D_FACTOR Alpha Factor(特征输入)和 MOD-INF-016 Shared Core(契约基座)，下游被 D_SIGNAL Signal Generation 和 D_PORTFOLIO_CORE Portfolio Construction 消费。

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

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L11-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | `__init__.py` | §3 | 模块入口，导出4个核心类 | 已实现 |
| 2 | `inference_base.py` | §3/§4 | InferenceEngineBase + ModelTrainerBase + ModelRegistry + ModelMetadata | 已实现 |
| 3 | `implementations/__init__.py` | §3 | 实现子包入口 | 已实现 |
| 4 | `implementations/default_inference_engine.py` | §3/§4 | DefaultInferenceEngine 默认推理引擎 | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls D:\ZephyrAlpha\src\zephyr\ml_train\` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" inference_base.py` | ☐ |
| DefaultInferenceEngine 继承 InferenceEngineBase | `grep "class DefaultInferenceEngine" default_inference_engine.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | 4核心类 + DefaultInferenceEngine | — | — |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 + 结构重组 | — | 结构重组，无功能变更 |
| v2.1.0 (模板v4.1回填+对齐) | 同 v2.0.0 + 代码bug修复 | 6子模块(training/validation/serving-default/serving-hot/evaluation/scout) | C轨占位，待ARB-11激活 |

---

## §1 设计背景与目标

### 1.1 背景

ML平台层是 C 轨业务价值线（线7）的 T1 核心层，负责模型训练→验证→推理→监控的完整生命周期。当前仅 Phase B 骨架就位，待 B 轨容量升级完成后按 ARB-11 三梯队策略激活。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 模型推理标准化 | InferenceEngineBase OCP扩展点可用 |
| 2 | ✅ 包含 | 模型注册管理 | ModelRegistry版本生命周期管理可用 |
| 3 | ✅ 包含 | 模型训练管线 | ModelTrainerBase OCP扩展点可用 |
| 4 | ✅ 包含 | 推理请求/响应 | CTR-P1-004/CTR-P1-005契约可产出 |
| 5 | ❌ 排除 | 实验编排 | 实验 Experimentation |
| 6 | ❌ 排除 | 系统可观测性 | MOD-INF-015 System Telemetry |
| 7 | ❌ 排除 | 数据摄取 | D_DATA Data Source |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 可施工 | 可启动新施工 |
| Windows 单机部署 | 无分布式协调需求 |
| Python 3.12+ | asyncio + Pydantic V2 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 | 设计+施工 | 审批权限 |
| D_SIGNAL/D_PORTFOLIO_CORE 下游 | 推理接口兼容性 | 集成 | 接口变更需通知 |
| 实验层 | 模型调用方式 | 集成 | 契约消费 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 推理服务 | DefaultInferenceEngine骨架 | 6子模块完整推理服务 | 5个子模块未实现 | P1 |
| 模型持久化 | 无 | 模型文件存储+版本管理 | GAP-002 | P2 |
| 异步推理 | 无 | 异步推理+队列 | GAP-001 | P2 |
| Scout Agent | 无 | arXiv/SSRN/GitHub自动研究 | 需AISG出站白名单 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 模型推理 | D_FACTOR因子特征到达 | ModelServingRequest→InferenceEngineBase.predict()→ModelServingResponse | 推理结果+置信度 |
| 模型注册 | 训练完成 | ModelTrainerBase.train()→validate()→ModelRegistry.register() | 注册的trainer_cls |
| 模型升级 | 新模型验证通过 | register→activate→旧模型deprecate | 活跃模型切换 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 模型推理 | InferenceEngineBase抽象 + DefaultInferenceEngine实现 | 本模块 |
| 2 | ✅ 包含 | 模型注册 | ModelRegistry（版本生命周期管理） | 本模块 |
| 3 | ✅ 包含 | 模型训练 | ModelTrainerBase抽象 | 本模块 |
| 4 | ✅ 包含 | 模型元数据 | ModelMetadata数据类 | 本模块 |
| 5 | ❌ 排除 | 实验设计 | 实验 Experimentation负责 | 实验 |
| 6 | ❌ 排除 | 遥测采集 | MOD-INF-015负责 | MOD-INF-015 |
| 7 | ❌ 排除 | 因子计算 | D_FACTOR Alpha Factor负责 | D_FACTOR |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | InferenceEngineBase | 推理引擎OCP扩展点 | ModelServingRequest/Response | 抽象基类+注册表 |
| 2 | ModelTrainerBase | 训练器OCP扩展点 | ModelRegistry | 抽象基类+注册表 |
| 3 | ModelRegistry | 模型版本生命周期管理 | ModelTrainerBase | 类方法注册/查找 |
| 4 | ModelMetadata | 模型元数据不可变数据类 | — | frozen dataclass |
| 5 | DefaultInferenceEngine | 默认推理引擎实现 | InferenceEngineBase, ModelMetadata | 继承+实现predict() |

> **依赖图 §3.13 子模块规划**（C轨占位，待施工）：
> l11-training(P1,Cold) / l11-validation(P2,Cold) / l11-serving-default(P1,Warm) / l11-serving-hot(P1,T3→Hot) / l11-evaluation(P2,Cold) / l11-scout(P2)

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_FACTOR Alpha Factor | 特征输入 → InferenceEngineBase.predict() | D_SIGNAL/D_PORTFOLIO_CORE | ModelServingRequest → ModelServingResponse |
| 2 | ModelTrainerBase | train() → validate() → ModelRegistry.register() | ModelRegistry | dict[str, float] 指标 |
| 3 | D_EXECUTION_CORE PositionSnapshot(CTR-006) | 持仓数据消费 | 模型监控 | CTR-006 |
| 4 | 模型性能指标 | 推理延迟/置信度/漂移 | MOD-INF-015(CTR-P1-013) | CTR-P1-013 Telemetry |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| registered | ModelRegistry.register() | registered | model_id 唯一 |
| registered | activate | active | 验证通过 |
| active | deprecate | deprecated | 有替代模型 |

---

## §4 接口契约

> ⚠️ ModelMetadata 使用 `@dataclass(frozen=True)` 而非 Pydantic V2 BaseModel（KBG-0040），属于技术债务，C轨激活时 MUST 迁移为 Pydantic V2 BaseModel。

### 4.1 公共 API

```python
class InferenceEngineBase(abc.ABC):
    def predict(self, request: ModelServingRequest) -> ModelServingResponse: ...
    def batch_predict(self, requests: list[ModelServingRequest]) -> list[ModelServingResponse]: ...

class ModelTrainerBase(abc.ABC):
    def train(self, features: dict[str, Any], target: Any, idempotency_key: str) -> dict[str, float]: ...
    def validate(self, features: dict[str, Any], target: Any) -> dict[str, float]: ...

class ModelRegistry:
    @classmethod
    def register(cls, trainer_cls: type[ModelTrainerBase]) -> type[ModelTrainerBase]: ...
    @classmethod
    def get(cls, model_id: str) -> type[ModelTrainerBase]: ...
```

### 4.2 数据模型

```python
@dataclass(frozen=True)
class ModelMetadata:
    model_id: str
    model_version: str
    model_type: str
    framework: str
    features: list[str]
    target: str
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "registered"
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `predict()` | `request: ModelServingRequest` | ✅ | 必须包含 model_id + input_features |
| `train()` | `features`, `target`, `idempotency_key` | ✅ | idempotency_key 非空 |
| `register()` | `trainer_cls` | ✅ | 必须有 `__model_id__` 属性 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `predict()` | `ModelServingResponse`：prediction + confidence + inference_ms | confidence=0.0, prediction=0.0 |
| `train()` | `dict[str, float]`：训练指标 | — |
| `register()` | 注册的 trainer_cls | `ValueError`(ID重复) / `AttributeError`(缺__model_id__) |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| CTR-P1-004 ModelServingRequest | FULL_BACKWARD | v1.0.0 |
| CTR-P1-005 ModelServingResponse | FULL_BACKWARD | v1.0.0 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | InferenceEngineBase为OCP扩展点 | 新推理策略只加不改 |
| 2 | ModelTrainerBase为OCP扩展点 | 新训练策略只加不改 |
| 3 | 推理输出必须标准化 | 下游D_SIGNAL/D_PORTFOLIO_CORE依赖统一格式 |
| 4 | ModelRegistry为单例 | 模型版本全局唯一 |
| 5 | Python 3.12+ | Pydantic V2 + dataclass |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 模型数 | 4 类 | 50 | 500 | ✅ | 超过500→分片注册表 |
| 推理QPS | <1 | 100 | 1000 | ✅ | 超过1000→异步推理+队列 |

### 5.3 迁移/废弃方案

本蓝图不涉及迁移。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 推理服务可用率 | 99.9% | 推理成功/总请求 | predict()成功率 | 99.9% | 每月允许0.1%失败 | <99.5%告警 |
| 延迟 | 推理延迟P95 | <100ms | time.perf_counter() | inference_ms | P95<100ms | — | P95>200ms告警 |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | `@dataclass` 用于新数据模型 | `Pydantic V2 BaseModel` | KBG-0040；ModelMetadata为技术债务，待迁移 |
| 2 | 导入源 | `from zephyr.l02_*` 直接导入 | 通过CTR-P1-004契约 | 分层约束 |
| 3 | 编码模式 | 推理引擎直接访问数据库 | 通过MOD-INF-016 SharedCore | 隔离约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 模型未加载时调用predict | model is None 检查 | 返回confidence=0.0的空响应 | 下游D_SIGNAL/D_PORTFOLIO_CORE收到零值预测 |
| 2 | 模型ID重复注册 | ModelRegistry.register() 检查 | 抛出ValueError | 注册流程中断 |
| 3 | 推理执行异常 | try/except 捕获 | 返回confidence=0.0的空响应+日志 | 下游收到零值预测 |
| 4 | 训练器缺少__model_id__ | hasattr检查 | 抛出AttributeError | 注册流程中断 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| l11_predict_latency_ms | Histogram | 自动埋点(inference_ms) | P95>200ms | P2 |
| l11_predict_confidence | Gauge | 自动埋点 | 平均<0.5持续5min | P2 |
| l11_model_registry_size | Gauge | ModelRegistry._registry | >400 | P3 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| DefaultInferenceEngine | 返回零值响应 | 实际推理 | confidence=0.0兜底 | 模型重新加载 |
| ModelRegistry | 已注册模型可用 | 新注册 | 只读模式 | 注册表恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 模型版本冲突 | 推理结果不一致 | ModelRegistry版本锁定+唯一性检查 | 重复注册抛出ValueError |
| 2 | 模型文件路径注入 | 加载恶意模型 | 模型路径白名单（待施工） | 路径校验 |
| 3 | Scout外部访问 | arXiv/SSRN/GitHub需出站 | 需AISG出站白名单（待施工） | 白名单校验 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | InferenceEngineBase/ModelRegistry | predict()空模型/已加载模型; register()重复ID | 覆盖率≥80% |
| 2 | 集成测试 | DefaultInferenceEngine + ModelServingRequest/Response | 端到端推理流程 | 端到端通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-016 Shared Core | 必须 | ModelServingRequest/Response契约基座 | v0.14.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |
| D_FACTOR Alpha Factor | 可选 | 特征输入(CTR-001) | — | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` |
| MOD-INF-015 System Telemetry | 可选 | 模型监控(CTR-P1-013) | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\system_telemetry\blueprint.md` |
| D_EXECUTION_CORE Trade Execution | 可选 | 持仓数据(CTR-006) | — | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.13 | 蓝图声明的每个依赖在依赖图中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-L11-001` |
| 2 | §11 产出物路径 ↔ 依赖图 §5 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

**执行顺序依赖**：

| 上游步骤 | 下游步骤 | 依赖关系 |
|---------|---------|---------|
| 无内部依赖 | — | — |

**数据流依赖**：

| 数据生产者 | 数据消费者 | 数据格式 |
|-----------|-----------|---------|
| 无内部依赖 | — | — |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | C轨占位，子模块未实现 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防漂移 | CI门禁 | validate_path_alignment.py | 无 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 不适用 | 无临时时态内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 否 | C轨已解除，可施工 | — | — | — | — | — |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\ml_train\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\ml_train\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_SIGNAL Signal Generation | 契约消费 | CTR-P1-004 ModelServingRequest | 信号层可消费推理请求 |
| D_PORTFOLIO_CORE Portfolio Construction | 契约消费 | CTR-P1-004/005 | 组合构建可消费推理结果 |
| 实验 Experimentation | 契约消费 | CTR-P1-004/005 | 实验层可调用模型推断 |
| MOD-INF-015 System Telemetry | instrumentation | CTR-P1-013 Telemetry | 模型性能指标可观测 |
| D_EXECUTION_CORE Trade Execution | 契约消费 | CTR-006 PositionSnapshot | 持仓数据消费 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| ml_experiment_domain-001 | ML实验域 | D_ML_TRAIN→实验模型产出→实验 | MOD-L13-001 | 修改D_ML_TRAIN推理接口必须同步更新实验蓝图 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress + version | 蓝图升级 |
| 2 | 模块ID注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 版本信息 | 蓝图升级 |
| 3 | YAML架构模型 | `D:\ZephyrAlpha\architecture_model\layers\l11_ml_platform.yaml` | 子模块声明 | 依赖图对齐 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|------|------|------|---------|------|
| 1 | 模型版本冲突 | 中 | 高 | ModelRegistry版本锁定 | 风险 |
| 2 | 推理延迟 | 中 | 中 | 异步推理 + 超时熔断（待施工） | 风险 |
| 3 | GPU资源竞争 | 低 | 中 | 资源池 + 优先级调度（待施工） | 风险 |
| 4 | ModelMetadata使用dataclass而非Pydantic | — | 中 | C轨激活时迁移为Pydantic V2 BaseModel | 负面后果 |
| 5 | C轨占位期间功能不完整 | — | — | — | 负面后果 |

---

## §16 施工指引

> ✅ **业务层已开放，可施工**。以下施工指引可执行。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | C轨占位已解除 | 确认✅标记 | ☐ |
| 3 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 4 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 5 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase |
| 施工模式 | 扩展（在现有骨架上完善） |
| 核心风险 | 推理正确性 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板v4.1回填+对齐） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | InferenceEngineBase定义 | 必须 | ✅ | ✅ |
| 2 | ModelTrainerBase定义 | 必须 | ✅ | ✅ |
| 3 | ModelRegistry定义 | 必须 | ✅ | ✅ |
| 4 | C轨占位解除(ARB-11) | 必须 | ❌ | ❌ |

### 16.3 实施步骤

> ✅ 以下步骤可执行（C轨占位已解除）。

#### 步骤 1：完善DefaultInferenceEngine

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ml_train\implementations\default_inference_engine.py` |
| 验收标准 | import成功 + predict()返回有效ModelServingResponse |
| 验证命令 | `python -c "from zephyr.ml_train.implementations.default_inference_engine import DefaultInferenceEngine; print('OK')"` |
| G7 检查项 | 上游依赖ModelServingRequest/Response是否可导入？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultInferenceEngine可实例化且predict()返回非None |

#### 步骤 2：完善ModelRegistry生命周期管理

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ml_train\inference_base.py` |
| 验收标准 | 版本注册/查找/废弃可用 |
| 验证命令 | `python -c "from zephyr.ml_train.inference_base import ModelRegistry; print('OK')"` |
| G7 检查项 | ModelRegistry单例约束是否满足？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | ModelRegistry.register/get/clear全部可用 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultInferenceEngine修改破坏已有功能 | `git checkout -- src/zephyr/ml_train/implementations/` |
| 2 | ModelRegistry扩展破坏注册逻辑 | `git checkout -- src/zephyr/ml_train/inference_base.py` |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | DefaultInferenceEngine 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | DefaultInferenceEngine 非空 | `cat` 有内容 | 完成 | ☐ |
| 3 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 4 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 7 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ☐ |
| 8 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | — |
| verification_status | unverified | — |
| code_alignment_verified | no | — |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 推理兜底逻辑 | 算法 | predict()模型未加载→返回confidence=0.0空响应；异常→同上+日志 | `default_inference_engine.py` |
| 2 | 注册表唯一性 | 协议 | ModelRegistry.register()检查__model_id__存在+唯一性，违反→ValueError/AttributeError | `inference_base.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/` | 单元测试 | — | 9 passed |
| 2 | 配置 | `l11_ml_platform.yaml` → `status` | 模块状态 | implemented/active | C轨已解除[ARCH-045 P0]，可施工 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | DefaultInferenceEngine导入失败 | 依赖缺失 | `pip install -e .[dev]` | 依赖安装 | 重新导入 |
| 2 | 运行 | 模型加载失败 | 文件不存在/格式错误 | 检查model_path+joblib.load | 降级为registry模型 | 重新加载 |
| 3 | 运行 | 推理超时 | 模型计算过慢 | 检查inference_ms+熔断 | 返回零值响应 | 模型优化 |

### 16.12 并发操作模型

本模块无并发操作（C轨占位，单进程运行）。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 核心类数 | 4 | `grep "class " inference_base.py` |
| 实现类数 | 1 | `ls implementations/` |
| 模型注册数 | 0 | ModelRegistry._registry 大小 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-001 | 无异步推理 | 异步推理+队列 | P2 | 推理QPS > 100 | v3.0.0 | 待施工 |
| GAP-002 | 无模型持久化 | 模型文件存储+版本管理 | P2 | 模型数 > 50 | v3.0.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 4核心类 + DefaultInferenceEngine | ✅ |
| v2.0.0 | 2 | 模板v3.3重构 | 章节重排+补缺章节+概述+标准锚点 | ✅ |
| v2.1.0 | 2 | 模板v4.1回填+对齐 | 回填缺失章节+依赖图对齐+代码bug修复 | ✅ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| l11-training | GAP-002 | 待创建 | Phase N | 待施工 |
| l11-validation | — | 待创建 | Phase N | 待施工 |
| l11-serving-default | — | 待创建 | Phase N | 待施工 |
| l11-serving-hot | — | 待创建 | Phase N | 待施工 |
| l11-evaluation | — | 待创建 | Phase N | 待施工 |
| l11-scout | — | 待创建 | Phase N | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L11001-01 | ModelMetadata用dataclass而非Pydantic | A:dataclass / B:Pydantic | A | frozen不可变需求+快速原型；C轨激活时迁移为B | 2026-05-05 |
| 2 | D-L11001-02 | 推理兜底返回零值而非抛异常 | A:零值 / B:异常 | A | 下游D_SIGNAL/D_PORTFOLIO_CORE需要连续信号流，异常会中断管线 | 2026-05-05 |
| 3 | D-L11001-03 | 模板v4.1升级+依赖图对齐 | 保持v2.0.0/按v4.1回填 | 按v4.1回填 | §0前移+缺失章节补全+依赖图对齐 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| OCP扩展点 | 开闭原则——对扩展开放，对修改关闭的抽象基类 | 插件 | OCP扩展点是蓝图级契约，插件是运行时加载 |
| ModelRegistry | 模型版本生命周期管理单例，管理registered→active→deprecated | 模型仓库 | Registry是内存注册表，仓库是持久化存储 |
| InferenceEngineBase | 推理引擎抽象基类，定义predict()契约 | 推理服务 | Base是OCP扩展点，服务是完整运行时 |
| CTR-P1-004 | ModelServingRequest契约——D_ML_TRAIN→D_SIGNAL/D_PORTFOLIO_CORE的推理请求格式 | CTR-P1-005 | 004是请求，005是响应 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | ModelMetadata使用dataclass而非Pydantic V2 BaseModel | 中 | 快速原型时选择dataclass | C轨激活时迁移为Pydantic V2 BaseModel | §5.7 #1 | 待解决 |
| 2 | DefaultInferenceEngine.load_model()依赖joblib | 低 | joblib是可选依赖 | 添加try/except降级 | §5.1 #5 | 待解决 |
| 3 | 6子模块(training/validation/serving-default/serving-hot/evaluation/scout)未实现 | 高 | C轨占位 | ARB-11激活后按梯队施工 | §1.6 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ✅ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 13 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | 6子模块全部实现+测试通过 | 仅骨架就位，子模块未实现 |
| 接口契约 | stable | 高 | CTR-P1-004/005无破坏性变更 | 推理请求/响应契约已稳定 |
| 数据模型 | evolving | 中 | ModelMetadata迁移为Pydantic V2 | dataclass技术债务 |
| 施工步骤 | evolving | 低 | C轨占位解除后验证 | 占位期间步骤仅为准备 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | 4核心类 + DefaultInferenceEngine | — | 已完成 |
| v2.0.0 | 模板v3.3重构 | v1.0.0 | 已完成 |
| v2.1.0 | 模板v4.1回填+依赖图对齐+代码bug修复 | v2.0.0 | 已完成 |
| v3.0.0 | 6子模块实现+Pydantic迁移 | v2.1.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 路径错误 |
| 2 | 必备链接不可省略 | 信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾 |
| 8 | 禁止模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复/跳过 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复 | 代码与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定 | 职责混淆 |
| 16 | 术语表不可省略 | 术语漂移 |
| 17 | 参考实现规格 vs 已实现代码重复 | 逻辑错误/双源漂移 |
| 18 | 对标验证表格 vs 对标散文 | 丢表格/留噪音 |
| 19 | SLO 必须定义 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明 | 部分失败行为不可预测 |

---

## 蓝图拆分判定标准

### 判定流程

| 步骤 | 判定 | 结果 |
|------|------|------|
| 1 | 蓝图内是否存在职责不同的多个子系统？ | 是→步骤2；否→原地升级 |
| 2 | 各子系统是否有独立的上游/下游依赖？ | 是→拆分独立蓝图；否→原地升级 |
| 3 | 拆分后各蓝图是否仍能自包含？ | 是→执行拆分；否→原地升级 |

### 判定示例

| 场景 | 职责不同？ | 独立依赖？ | 判定 |
|------|:---:|:---:|------|
| 模型推理 + 模型训练 | 否（同属ML平台） | 否（共享ModelRegistry） | 原地升级 |
| 模型推理 + 实验管线 | 是 | 是 | 拆分独立蓝图 |
| 模型注册 + 数据摄取 | 是 | 是 | 拆分独立蓝图 |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。ML Platform Core 为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 6 | Shared Core 蓝图 | MOD-INF-016 | 当前版本 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` | 契约承载 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | MOD-INF-016 Shared Core | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` | ModelServingRequest/Response契约 | Shared Core 是契约定义层，本蓝图是ML推理实现层 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | ML平台核心代码 | `D:\ZephyrAlpha\src\zephyr\ml_train\` | 修改 | 蓝图描述的核心代码 |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` | 修改 | 本文件 |
| 3 | YAML架构模型 | `D:\ZephyrAlpha\architecture_model\layers\l11_ml_platform.yaml` | 修改 | 子模块声明对齐 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| ML平台核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| ML平台施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| ML平台接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | D_SIGNAL Signal Generation 蓝图 | §4 接口契约、§10 依赖关系 |
| Tier 1 | D_PORTFOLIO_CORE Portfolio Construction 蓝图 | §4 接口契约、§10 依赖关系 |
| Tier 2 | 实验 Experimentation 集成点 | §12 集成点 |
| Tier 2 | MOD-INF-015 System Telemetry | §6.1 可观测性指标 |
| Tier 3 | `inference_base.py` / `default_inference_engine.py` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充 | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
