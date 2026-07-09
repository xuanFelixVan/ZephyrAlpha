---
module_id: MOD-L13-001
submodule_path: src/zephyr/simulation
title: "Experimentation Core 蓝图+施工图 — 实验管理平台"
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
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/simulation/"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 2
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-15"
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-L11-001
    at: "§10"
    why: CTR-011 ModelCheckpoint + CTR-P1-004/005 模型推断
  - target: MOD-L09-001
    at: "§10"
    why: CTR-010 ExperimentMetric 上报 + CTR-P1-014 ExperimentResult 消费
references:
  - path: "D:\\ZephyrAlpha\\architecture_model\\layers\\l13_experimentation.yaml"
    section: "§0"
    why: SSoT YAML 真源
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\03-application_architecture.md"
    section: "§4.3"
    why: AI/ML Platform 架构上下文
summary: "实验层。ExperimentPipelineBase + ScoutAgentBase OCP 扩展点 + ExperimentConfig/ExperimentMetric。Phase B 骨架已就位，CTR-009~012 待施工。"
tags: [experimentation, l13, c-track, ocp, scout-agent, ab-test, t2-deferred]
priority: P2
runtime_plane: warm
ssot_yaml: "architecture_model/layers/l13_experimentation.yaml"
c_track_status: "active"
construction_gate: "ARB-11: C轨T2层已解除blocked，开工条件已满足。"
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

> ✅ **业务层已开放·可施工** — 本蓝图所属 实验 实验管线层已解除 C 轨 T2-deferred 状态。Owner 已解除占位禁令，基础设施已就绪，AI 可自主实施本层业务代码。

> module_id: MOD-L13-001 | version: 2.1.0 | status: active | domain: simulation
> actual_disk_path: src/zephyr/simulation/ | generation: 2 | construction_progress: partially_implemented

# Experimentation Core 蓝图+施工图 — 实验管理平台

> **真源声明**：本蓝图是 ZephyrAlpha 实验管理体系的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 实验管理层——它解决了策略和因子验证缺乏标准化管线的问题。核心职责包括：实验管线抽象（ExperimentPipelineBase OCP 扩展点）、Scout Agent 自动化实验编排（ScoutAgentBase OCP 扩展点）、实验配置下发（ExperimentConfig）、实验指标统计验证（ExperimentMetric，含 Cohen's d / p-value / effect_size）。当前规模 2 个 OCP 扩展点 + 1 个默认实现（DefaultExperimentPipeline），目标覆盖 A/B 测试、因子消融、策略变种三类实验。上游依赖 D_ML_TRAIN ML Platform（模型推断 + 检查点）和 D_DATA Data Source（市场数据），下游被 D_RESEARCH Research（实验结论消费）和 INF-012 Database（产物归档）消费。

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

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L13-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | pipeline_base.py | §3.1 | ExperimentPipelineBase + ScoutAgentBase + ExperimentConfig + ExperimentMetric | 已实现 |
| 2 | implementations/default_experiment_pipeline.py | §3.1 | DefaultExperimentPipeline A/B 对照 + 统计验证 | 已实现 |
| 3 | __init__.py | — | 模块导出 | 已实现 |
| 4 | implementations/__init__.py | — | 子包导出 | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls D:\ZephyrAlpha\src\zephyr\simulation\` | ☐ |
| ExperimentPipelineBase 类存在于代码 | `grep "class ExperimentPipelineBase" pipeline_base.py` | ☐ |
| ScoutAgentBase 类存在于代码 | `grep "class ScoutAgentBase" pipeline_base.py` | ☐ |
| DefaultExperimentPipeline 类存在于代码 | `grep "class DefaultExperimentPipeline" implementations/default_experiment_pipeline.py` | ☐ |
| ExperimentConfig / ExperimentMetric 数据类存在 | `grep "class Experiment" pipeline_base.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | ExperimentPipelineBase + ScoutAgentBase + ExperimentConfig + ExperimentMetric + DefaultExperimentPipeline | CTR-009~012 契约实现 | T2 blocked |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 + 结构重组 | 同上 | 结构重组，无功能变更 |
| v2.1.0 (回填+压缩) | 同 v2.0.0 | 同上 | 模板合规回填+压缩 |

---

## §1 设计背景与目标

### 1.1 背景

策略和因子验证缺乏标准化管线——每次验证需手动搭建实验框架，无法复用、无法对比、无法归档。实验 实验层提供统一的实验管线抽象和自动化编排能力，使验证过程可复现、可对比、可归档。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 实验管线标准化 | ExperimentPipelineBase OCP 扩展点可用，新策略只加不改 |
| 2 | ✅ 包含 | Scout Agent 自动化 | ScoutAgentBase 可编排自动化实验，产出 ExperimentResult |
| 3 | ✅ 包含 | 实验配置下发 | CTR-009 ExperimentConfig 可产出至 D_ML_TRAIN |
| 4 | ✅ 包含 | 实验指标上报 | CTR-010 ExperimentMetric 可产出至 D_RESEARCH |
| 5 | ✅ 包含 | 模型检查点导入 | CTR-011 ModelCheckpoint 可从 D_ML_TRAIN 消费 |
| 6 | ✅ 包含 | 实验产物归档 | CTR-012 ExperimentArtifact 可归档至 INF-012 |
| 7 | ❌ 排除 | 模型推理 | D_ML_TRAIN ML Platform 负责 |
| 8 | ❌ 排除 | 系统可观测性 | MOD-INF-015 系统遥测负责 |
| 9 | ❌ 排除 | 数据摄取 | D_DATA Data Source 负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows 单机部署 | 无分布式协调需求 |
| 实验结论必须统计验证 | p-value / effect_size / power analysis 强制 |
| Scout Agent 不可污染生产环境 | 沙箱执行 + 审批门禁 |
| 实验产物必须归档 | CTR-012 保证实验可复现 |
| C轨T2已激活 | ARB-11: 开工条件已满足 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 + CTR契约审批 | 设计+施工 | 审批权限 |
| D_ML_TRAIN ML Platform | 模型推断结果消费 + 检查点提供 | 集成 | CTR-009/011 契约对齐 |
| D_RESEARCH Research | 实验结论消费 | 集成 | CTR-010/P1-014 契约对齐 |
| INF-012 Database | 实验产物归档 | 集成 | CTR-012 契约对齐 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 实验管线 | OCP骨架+默认实现 | 3类实验(A/B/消融/变种) | 缺消融+变种管线 | P2 |
| 契约集成 | CTR-P1-014已定义 | CTR-009~012全部实现 | 4条契约未实现 | P1 |
| 统计验证 | 简化p-value估计 | scipy.stats精确计算 | 精度不足 | P1 |
| 数据模型 | dataclass | Pydantic V2 BaseModel | KBG-0040不符 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| A/B策略对比 | 新策略假设提出 | 创建ExperimentConfig→DefaultExperimentPipeline.run()→统计验证→ExperimentResult | supported/rejected/inconclusive |
| Scout自动实验 | 外部资讯变化 | ScoutAgentBase.scout()→设计实验→执行→归档 | ExperimentResult + archived_to_kms=True |
| 因子消融 | 因子重要性验证 | 配置control/treatment_params→run()→逐指标effect_size | ExperimentMetric列表 |
| 冠军模型提升 | 实验结论显著 | 实验→D_ML_TRAIN(模型部署) + 实验→D_RESEARCH(结论归档) | CTR-012归档 + CTR-P1-014通知 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 实验管线 | ExperimentPipelineBase 抽象 + DefaultExperimentPipeline 实现 | 本模块 |
| 2 | ✅ 包含 | Scout Agent | ScoutAgentBase 自动化实验编排 | 本模块 |
| 3 | ✅ 包含 | 实验配置 | ExperimentConfig 数据类 | 本模块 |
| 4 | ✅ 包含 | 实验指标 | ExperimentMetric 数据类 | 本模块 |
| 5 | ✅ 包含 | 实验产物归档 | CTR-012 ExperimentArtifact 归档至数据库 | 本模块 |
| 6 | ❌ 排除 | 模型训练/推理 | D_ML_TRAIN ML Platform 负责 | D_ML_TRAIN |
| 7 | ❌ 排除 | 遥测采集 | MOD-INF-015 系统遥测负责 | INF-015 |
| 8 | ❌ 排除 | 数据存储 | INF-012 Database 负责 | INF-012 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | ExperimentPipelineBase | 实验管线 OCP 扩展点 | ExperimentConfig, ExperimentMetric | 抽象基类 + 注册表 |
| 2 | DefaultExperimentPipeline | 默认 A/B 对照 + 统计验证实现 | ExperimentPipelineBase | 继承 |
| 3 | ScoutAgentBase | Scout Agent OCP 扩展点 | ExperimentResult | 抽象基类 + 注册表 |
| 4 | ExperimentConfig | 实验配置数据类 | — | frozen dataclass |
| 5 | ExperimentMetric | 实验指标数据类 | — | frozen dataclass |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_DATA NormalizedMarketData | ExperimentPipelineBase.run(config) → A/B 分组 → 统计验证 | ExperimentMetric 列表 | ExperimentMetric dataclass |
| 2 | ExperimentMetric 列表 | ScoutAgentBase.scout(context) → 汇总结论 | D_RESEARCH Research | ExperimentResult (CTR-P1-014) |
| 3 | ScoutAgentBase 结论 | archive_to_kms(result) → 归档 | KMS 知识管道 | ExperimentResult |
| 4 | D_ML_TRAIN ModelCheckpoint | ScoutAgent 消费模型推断结果 | 实验分析 | ModelServingResponse |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| registered | ExperimentConfig 创建 | registered | experiment_id 非空 |
| registered | ExperimentPipelineBase.run() 调用 | running | config.status == "registered" |
| running | 所有 metric 计算完成 | completed | len(metrics) == len(config.metrics) |
| completed | ScoutAgentBase.scout() 汇总 | concluded | confidence >= 0.7 |
| concluded | archive_to_kms() 调用 | archived | conclusion in [supported, rejected] |

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），当前使用 dataclass 为过渡态（GAP-003）。

### 4.1 公共 API

```python
class ExperimentPipelineBase(abc.ABC):
    """实验管线基类（OCP 扩展点 实验-EXP）"""
    _registry: ClassVar[dict[str, type["ExperimentPipelineBase"]]] = {}

    @abc.abstractmethod
    def run(self, config: ExperimentConfig,
            idempotency_key: str) -> list[ExperimentMetric]:
        """执行实验，返回各指标的统计结果"""

    @staticmethod
    def compute_effect_size(control: float, treatment: float,
                            pooled_std: float) -> float:
        """Cohen's d 效应量计算"""


class ScoutAgentBase(abc.ABC):
    """Scout Agent 自动化实验编排器（OCP 扩展点 实验-SCT）"""
    _registry: ClassVar[dict[str, type["ScoutAgentBase"]]] = {}

    @abc.abstractmethod
    def scout(self, context: dict[str, Any],
              idempotency_key: str) -> ExperimentResult:
        """自动化实验编排：扫码外部信息 → 设计实验 → 执行 → 产出结论"""

    @abc.abstractmethod
    def archive_to_kms(self, result: ExperimentResult) -> bool:
        """将确认的实验结论归档到 KMS 知识管道"""


class DefaultExperimentPipeline(ExperimentPipelineBase):
    """默认实验管线——A/B 对照 + 统计验证"""
    def run(self, config: ExperimentConfig,
            idempotency_key: str) -> list[ExperimentMetric]: ...
    def get_results(self, experiment_id: str) -> Optional[list[ExperimentMetric]]: ...
```

### 4.2 数据模型

```python
@dataclass(frozen=True)
class ExperimentConfig:
    """实验配置"""
    experiment_id: str
    hypothesis: str
    control_params: dict[str, Any]
    treatment_params: dict[str, Any]
    metrics: list[str]
    start_date: str
    end_date: str
    status: str = "registered"


@dataclass(frozen=True)
class ExperimentMetric:
    """单指标实验结果统计"""
    experiment_id: str
    metric_name: str
    control_value: float
    treatment_value: float
    effect_size: float
    p_value: float
    is_significant: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `ExperimentPipelineBase.run()` | `config` | ✅ | ExperimentConfig 实例，experiment_id 非空 |
| `ExperimentPipelineBase.run()` | `idempotency_key` | ✅ | 非空字符串，保证幂等 |
| `ScoutAgentBase.scout()` | `context` | ✅ | dict，含实验上下文信息 |
| `ScoutAgentBase.scout()` | `idempotency_key` | ✅ | 非空字符串 |
| `ScoutAgentBase.archive_to_kms()` | `result` | ✅ | ExperimentResult 实例 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `ExperimentPipelineBase.run()` | `list[ExperimentMetric]`：各指标统计结果 | `ValueError`：config 无效 |
| `ScoutAgentBase.scout()` | `ExperimentResult`：实验结论（CTR-P1-014） | `RuntimeError`：实验执行失败 |
| `ScoutAgentBase.archive_to_kms()` | `bool`：True=归档成功 | `bool`：False=归档失败 |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| ExperimentConfig 新增字段 | ✅ 向后兼容 | frozen dataclass，新字段需默认值 |
| ExperimentMetric 新增字段 | ✅ 向后兼容 | 同上 |
| ExperimentPipelineBase 新增抽象方法 | ❌ 破坏性 | 需 Owner 审批 + 所有子类更新 |
| ScoutAgentBase 新增抽象方法 | ❌ 破坏性 | 需 Owner 审批 + 所有子类更新 |
| CTR-P1-014 ExperimentResult 变更 | ❌ 破坏性 | 需通知 D_RESEARCH/D_ML_TRAIN |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | ExperimentPipelineBase 为 OCP 扩展点 | 新实验策略只加不改 |
| 2 | ScoutAgentBase 为 OCP 扩展点 | 新 Scout 策略只加不改 |
| 3 | 实验结论必须统计验证 | p-value / effect_size / power analysis |
| 4 | 实验产物必须归档 | CTR-012 保证实验可复现 |
| 5 | confidence < 0.7 的结论不应发布 | D_RESEARCH/D_ML_TRAIN 消费端应忽略低置信度结论 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 并发实验数 | 1 | 10 | 50 | ✅ | >50 → 实验队列 + 优先级调度 |
| 指标数/实验 | 5 | 20 | 100 | ✅ | >100 → 分批计算 |
| Scout Agent 数 | 0 | 5 | 20 | ✅ | >20 → Agent 池 + 负载均衡 |

### 5.3 迁移/废弃方案

本蓝图不涉及文件迁移或废弃。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 实验管线可用率 | 99% | 实验执行成功率 | run()成功率 | 99% | 每月≤7次失败 | 成功率<95% |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | — | — | — | — |
| 延迟 | 实验执行耗时(P95) | <60s | 时间戳差值 | run()耗时P95 | <60s | — | >120s |
| 正确性 | 统计验证精度 | 误差<1% | 已知数据集校验 | effect_size误差 | <1% | — | >5% |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 直接修改生产数据 | 沙箱执行+审批门禁 | Scout Agent 安全 |
| 2 | 编码模式 | 发布 confidence<0.7 结论 | 标记inconclusive+不发布 | 防止低质量结论误用 |
| 3 | 编码模式 | 使用 @dataclass 做输出契约 | Pydantic V2 BaseModel | KBG-0040（过渡期豁免，GAP-003） |
| 4 | 导入源 | zephyr.pf_core.* | 通过 CTR 契约间接交互 | 分层约束 |
| 5 | 导入源 | zephyr.signal.* | 通过 CTR 契约间接交互 | 分层约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 实验结果不可复现 | CTR-012 归档校验 + ExperimentConfig 版本化 | 强制归档 + 配置快照 | 结论不可信 |
| 2 | Scout Agent 误操作 | 沙箱执行异常 | 审批门禁 + 回滚实验 | 生产环境被污染 |
| 3 | pooled_std=0 导致 effect_size 不可计算 | compute_effect_size 守卫 | 返回 0.0 + 日志告警 | 指标失真 |
| 4 | ExperimentConfig 参数缺失 | dataclass 字段校验 | 拒绝执行 + ValueError | 实验无法启动 |
| 5 | CTR-009~012 契约未实现 | 集成测试失败 | Phase B 优先实现 | D_ML_TRAIN/D_RESEARCH/INF-012 集成断裂 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| experiment_run_total | Counter | 自动埋点 | — | — |
| experiment_run_duration_seconds | Histogram | 自动埋点 | P95>120s | P2 |
| experiment_significance_rate | Gauge | 自动埋点 | <50% | P3 |
| scout_agent_archive_failures | Counter | 手动上报 | >3/小时 | P2 |
| experiment_config_validation_errors | Counter | 自动埋点 | >10/小时 | P3 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| DefaultExperimentPipeline | 无（核心组件） | 全部实验执行 | 返回空metrics+告警 | 重启实例 |
| ScoutAgentBase | 手动实验执行 | 自动化编排 | 降级为手动实验 | Agent恢复 |
| CTR-012归档通道 | 实验执行 | 产物归档 | 本地缓存+异步重试 | INF-012恢复 |
| scipy.stats精确计算 | 简化p-value估计 | 精确统计 | 降级为Cohen's d估计 | scipy可用 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | Scout Agent 污染生产环境 | 高 | 沙箱执行 + 审批门禁 | 写操作 100% 可预演 |
| 2 | 实验配置篡改 | 中 | ExperimentConfig frozen + 版本化 | 配置不可变 |
| 3 | 低置信度结论误用 | 中 | confidence < 0.7 不发布 | D_RESEARCH/D_ML_TRAIN 消费端校验 |
| 4 | 实验数据泄露 | 低 | CTR-012 归档加密 | 归档数据访问审计 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | ExperimentPipelineBase + ScoutAgentBase | compute_effect_size 计算；p-value 估计；幂等性验证 | 覆盖率≥80% |
| 2 | 集成测试 | DefaultExperimentPipeline 端到端 | config→run→metrics 完整流程 | 端到端通过 |
| 3 | 统计验证测试 | Cohen's d / p-value | 已知数据集的 effect_size 和 p-value 正确性 | 误差 < 1% |
| 4 | 契约测试 | CTR-P1-014 / CTR-009~012 | ExperimentResult 格式兼容 D_RESEARCH/D_ML_TRAIN | 0 契约破坏 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L11-001 ML Platform | 必须 | CTR-011 ModelCheckpoint + CTR-P1-004/005 ModelServing | — | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` |
| MOD-L09-001 Research | 可选 | CTR-010 ExperimentMetric 上报 + CTR-P1-014 ExperimentResult 消费 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_research\blueprint.md` |
| D_DATA Data Source | 可选 | CTR-001 NormalizedMarketData | — | — |
| INF-012 Database | 必须 | CTR-012 ExperimentArtifact 归档 | — | — |
| shared/contracts/experiment | 必须 | ExperimentResult 数据类 | — | `D:\ZephyrAlpha\src\zephyr\shared\contracts\experiment\experiment_result.py` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.19 | 实验→D_ML_TRAIN(模型产出) + 实验→D_RESEARCH(实验结论) + D_RESEARCH→实验(研究假设) 一致 | 已对齐 | 人工核对 |
| 2 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-L13-001` |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | l13_experimentation.yaml 已注册 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

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
| 1 | 依赖图自动生成 | 否 | 模块简单，手动维护可行 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防止契约漂移 | CI门禁 | validate_path_alignment.py | 需补实验条目 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 否 | 当前无临时时态内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | 防止虚假进度 | pytest+ruff | — | 测试代码缺失 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_simulation\blueprint.md` | 本文件 |
| 业务代码（基类+数据类） | `D:\ZephyrAlpha\src\zephyr\simulation\pipeline_base.py` | ExperimentPipelineBase + ScoutAgentBase + ExperimentConfig + ExperimentMetric |
| 业务代码（默认实现） | `D:\ZephyrAlpha\src\zephyr\simulation\implementations\default_experiment_pipeline.py` | DefaultExperimentPipeline |
| 测试代码 | `D:\ZephyrAlpha\tests\simulation\` | 测试用例（待创建） |
| 模型服务响应契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\experiment\model_serving_response.py` | 模型服务响应结构（归属 MOD-INF-016） |
| 模型服务请求契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\model_serving_request.py` | 模型服务请求结构（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_ML_TRAIN ML Platform | 契约消费/生产 | CTR-009 ExperimentConfig + CTR-011 ModelCheckpoint | 实验配置可下发至 ML 平台 |
| D_RESEARCH Research | 契约生产 | CTR-P1-014 ExperimentResult + CTR-010 ExperimentMetric | 研究层可消费实验结论和指标 |
| INF-012 Database | 契约生产 | CTR-012 ExperimentArtifact | 实验产物可归档 |
| MOD-INF-015 系统遥测 | 契约消费 | CTR-P1-013 TelemetryEmitter | 实验运行数据可观测 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | version: 2.1.0 + construction_progress 更新 | 蓝图升级 |
| 2 | SSoT YAML | `D:\ZephyrAlpha\architecture_model\layers\l13_experimentation.yaml` | 新增 CTR-009~012 契约 | 契约扩展 |
| 3 | 跨层契约 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\cross_layer_contracts.yaml` | 新增 CTR-009~012 契约定义 | 契约注册 |
| 4 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 确认 MOD-L13-001 注册 | 编号验证 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 实验结果不可复现 | 中 | 高 | CTR-012 强制归档 + ExperimentConfig 版本化 | 风险 |
| 2 | Scout Agent 误操作 | 中 | 高 | 沙箱执行 + 审批门禁 | 风险 |
| 3 | CTR-009~012 契约未实现 | 高 | 高 | Phase B 优先实现 | 风险 |
| 4 | DefaultExperimentPipeline p-value 估计过于简化 | 中 | 中 | Phase C 引入 scipy.stats 精确计算 | 风险 |
| 5 | ExperimentConfig 使用 dataclass 而非 Pydantic BaseModel | 低 | 低 | Phase C 迁移至 Pydantic V2（KBG-0040） | 风险 |
| 6 | 新策略需实现ExperimentPipelineBase | — | — | — | 负面后果 |
| 7 | CTR-009~012增加契约维护成本 | — | — | — | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 7 | ✅ C轨T2层可施工——开工条件已满足 | 确认ARB-11条件 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 扩展为主（已有骨架扩展）+ 新建（契约实现） |
| 核心风险 | 实验统计正确性 + CTR-009~012 契约集成 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | ExperimentPipelineBase 定义 | 必须 | ✅ 已实现 | ✅ |
| 2 | ScoutAgentBase 定义 | 必须 | ✅ 已实现 | ✅ |
| 3 | D_ML_TRAIN InferenceEngineBase | 必须 | ⚠️ 部分实现 | ☐ |
| 4 | INF-012 Database | 可选 | ⚠️ 部分实现 | ☐ |
| 5 | ✅ ARB-11 开工条件 | 必须 | ✅ 已解除 | ✅ |

### 16.3 实施步骤

> [时态:临时] 通过验证后可删除（pytest+mypy+ruff exit 0），只保留"步骤N:已完成"。

#### 步骤 1：完善 DefaultExperimentPipeline

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 DefaultExperimentPipeline |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\simulation\implementations\default_experiment_pipeline.py` |
| 验收标准 | import 成功 + 单元测试通过 |
| 验证命令 | `python -m pytest tests/simulation/ -k test_default -v` |
| G7 检查项 | 上游pipeline_base.py已列出；下游产出物路径精确；回滚方案可执行 |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultExperimentPipeline 可实例化并执行 run() |

#### 步骤 2：实现 CTR-009 ExperimentConfig 产出

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.3 CTR-009 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\simulation\pipeline_base.py` 扩展 |
| 验收标准 | D_ML_TRAIN 可消费 ExperimentConfig |
| 验证命令 | `python -m pytest tests/simulation/ -k test_ctr009 -v` |
| G7 检查项 | CTR-009 契约格式与 cross_layer_contracts.yaml 一致 |
| AI 自治范围 | ai_modifiable |
| 检查点 | ExperimentConfig 可序列化为 CTR-009 格式 |

#### 步骤 3：实现 CTR-010 ExperimentMetric 产出

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.3 CTR-010 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\simulation\pipeline_base.py` 扩展 |
| 验收标准 | D_RESEARCH 可消费 ExperimentMetric |
| 验证命令 | `python -m pytest tests/simulation/ -k test_ctr010 -v` |
| AI 自治范围 | ai_modifiable |
| 检查点 | ExperimentMetric 可序列化为 CTR-010 格式 |

#### 步骤 4：实现 CTR-011 ModelCheckpoint 消费

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.3 CTR-011 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\simulation\pipeline_base.py` 扩展 |
| 验收标准 | D_ML_TRAIN 检查点可导入 |
| 验证命令 | `python -m pytest tests/simulation/ -k test_ctr011 -v` |
| AI 自治范围 | ai_modifiable |
| 检查点 | ModelCheckpoint 可反序列化并用于实验 |

#### 步骤 5：实现 CTR-012 ExperimentArtifact 归档

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.3 CTR-012 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\simulation\pipeline_base.py` 扩展 |
| 验收标准 | INF-012 可归档 |
| 验证命令 | `python -m pytest tests/simulation/ -k test_ctr012 -v` |
| AI 自治范围 | ai_modifiable |
| 检查点 | ExperimentArtifact 可写入 INF-012 |

#### 步骤 6：D_ML_TRAIN/D_RESEARCH/INF-012 集成测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §12 集成目标 |
| 产出位置 | `D:\ZephyrAlpha\tests\simulation\` |
| 验收标准 | 端到端通过 |
| 验证命令 | `python -m pytest tests/simulation/ -v` |
| AI 自治范围 | ai_modifiable |
| 检查点 | 全部集成测试通过 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultExperimentPipeline 修改破坏已有功能 | `git checkout -- src/zephyr/simulation/implementations/` |
| 2 | 契约扩展导致接口不兼容 | 回退 pipeline_base.py 到扩展前版本 |
| 3 | 集成测试失败 | 逐契约排查，回退失败的契约实现 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | pipeline_base.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 2 | default_experiment_pipeline.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 3 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 4 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 7 | 测试代码已创建 | tests/simulation/ 非空 | 完成 | ☐ |
| 8 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | yes | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | Cohen's d 效应量 | 算法 | d = (treatment - control) / pooled_std; pooled_std=0 → return 0.0 | pipeline_base.py |
| 2 | 简化 p-value 估计 | 算法 | \|d\|<0.2→0.5; <0.5→0.1; <0.8→0.01; else→0.001 | default_experiment_pipeline.py |
| 3 | 实验状态机 | 协议 | registered→running→completed→concluded→archived | pipeline_base.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/simulation/` | 运行测试 | `-k`: 过滤用例 | exit 0=通过 |
| 2 | 配置 | `l13_experimentation.yaml` → `status` | 层级状态 | implemented/blocked | — |
| 3 | 契约 | `CTR-P1-014` → `ExperimentResult` | 实验结论出站 | frozen dataclass | D_RESEARCH/D_ML_TRAIN消费 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 测试代码缺失 | pytest 发现空目录 | 创建 test_pipeline_base.py + test_default_experiment_pipeline.py | 测试代码 | pytest exit 0 |
| 2 | 运行 | 实验执行超时 | run() 超过 SLO | 检查实验配置指标数 + 数据量 | 降级为简化统计 | P95<60s |
| 3 | 运行 | 归档通道不可用 | INF-012 不可达 | 本地缓存 + 异步重试 | 缓存数据 | INF-012恢复后重试 |
| 4 | 运行 | 紧急冻结 | 安全事件 | 冻结实验执行+只读 | — | 威胁解除 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同实验并发run() | idempotency_key 去重 | 后写者返回缓存结果 | 首次执行结果为准 |
| 同配置并发修改 | ExperimentConfig frozen | 不可变，无冲突 | — |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 并发实验数 | 1 | DefaultExperimentPipeline 实例数 |
| OCP 扩展点数 | 2 | ExperimentPipelineBase + ScoutAgentBase |
| 已实现管线数 | 1 | DefaultExperimentPipeline |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-001 | p-value 估计为简化版 | 引入 scipy.stats 精确计算 | P1 | 需要精确统计时 | v2.1.0 | 待施工 |
| GAP-002 | 无实验队列调度 | 实验队列 + 优先级调度 | P2 | 并发实验 > 10 | v3.0.0 | 待施工 |
| GAP-003 | dataclass 非 Pydantic | 迁移至 Pydantic V2 BaseModel | P2 | KBG-0040 强制时 | v3.0.0 | 待施工 |
| GAP-004 | CTR-009~012 未实现 | Phase B 优先施工 | P1 | D_ML_TRAIN/D_RESEARCH 集成需求 | v2.1.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | C轨填充：ExperimentPipelineBase + ScoutAgentBase + DefaultExperimentPipeline | ✅ |
| v2.0.0 | 2 | 模板v3.3重构 | 章节重排+补缺 | ✅ |
| v2.1.0 | 2 | 回填+压缩 | 模板合规回填+压缩+对齐 | ✅ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| CTR-009 ExperimentConfig 产出 | GAP-004 | pipeline_base.py 扩展 | Phase B | 待施工 |
| CTR-010 ExperimentMetric 产出 | GAP-004 | pipeline_base.py 扩展 | Phase B | 待施工 |
| CTR-011 ModelCheckpoint 消费 | GAP-004 | pipeline_base.py 扩展 | Phase B | 待施工 |
| CTR-012 ExperimentArtifact 归档 | GAP-004 | pipeline_base.py 扩展 | Phase B | 待施工 |
| scipy.stats 精确 p-value | GAP-001 | default_experiment_pipeline.py | Phase C | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L13001-01 | 实验管线使用OCP扩展点 | 继承+注册表/函数式/配置驱动 | 继承+注册表 | 新策略只加不改，注册表支持运行时发现 | 2026-05-05 |
| 2 | D-L13001-02 | 统计验证使用Cohen's d | t-test/ANOVA/Cohen's d | Cohen's d | 效应量比p-value更有实际意义，且计算简单 | 2026-05-05 |
| 3 | D-L13001-03 | p-value初始使用简化估计 | 简化估计/scipy.stats | 简化估计 | 骨架阶段无需精确计算，GAP-001跟踪升级 | 2026-05-05 |
| 4 | D-L13001-04 | 数据模型使用dataclass | Pydantic BaseModel/dataclass | dataclass | 骨架阶段快速实现，GAP-003跟踪迁移 | 2026-05-05 |
| 5 | D-L13001-05 | 模板v4.1升级 | 保持v3.3/按v4.1升级 | 按v4.1升级 | §0前移+§7/§15删除+§10拆分+铁律扩展 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| ExperimentPipeline | 实验管线——从配置到指标结果的执行框架 | 实验管线基类 | 管线=框架，基类=OCP扩展点 |
| Scout Agent | 自动化实验编排器——外部资讯→实验→结论 | 实验管线 | Scout编排多个管线，管线执行单个实验 |
| Cohen's d | 标准化效应量=(treatment-control)/pooled_std | p-value | d衡量大小，p衡量显著性 |
| effect_size | 效应量——本蓝图特指Cohen's d | effect | effect=因果效果，effect_size=量化度量 |
| OCP扩展点 | 开闭原则扩展点——新策略只加不改 | 抽象基类 | OCP扩展点=抽象基类+注册表+运行时发现 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 测试代码完全缺失 | 高 | 骨架阶段未创建 | 步骤6创建测试 | §9 #1 | 待解决 |
| 2 | p-value估计精度不足 | 中 | 骨架阶段简化实现 | GAP-001引入scipy.stats | §5.1 #3 | 待解决 |
| 3 | dataclass不符合KBG-0040 | 低 | 骨架阶段快速实现 | GAP-003迁移Pydantic V2 | §5.7 #3 | 待解决 |
| 4 | CTR-009~012契约未实现 | 高 | T2 blocked | GAP-004 Phase B施工 | §4.3 | 待解决 |
| 5 | cross-module-dependency-registry.yaml缺实验条目 | 中 | 注册遗漏 | §10.2 #2 补注册 | §10.2 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ✅ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | CTR-009~012全部实现 | OCP扩展点设计稳定 |
| 接口契约 | evolving | 中 | Pydantic迁移+精确p-value | dataclass过渡+简化统计 |
| 数据模型 | evolving | 中 | KBG-0040强制迁移 | frozen dataclass→Pydantic V2 |
| 施工步骤 | evolving | 中 | T2 blocked解除 | 开工条件未满足 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | C轨填充：OCP骨架+默认实现 | — | 已完成 |
| v2.0.0 | 模板v3.3重构+章节补全 | v1.0.0 | 已完成 |
| v2.1.0 | 模板v4.1回填+压缩+对齐 | v2.0.0 | 已完成 |
| v2.2.0 | CTR-009~012契约实现+scipy.stats | v2.1.0 | 待施工(T2 blocked) |
| v3.0.0 | Pydantic V2迁移+实验队列调度 | v2.2.0 | 待施工 |

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
| 7 | 迁移/废弃方案必须写 | 断链/垃圾 |
| 8 | 禁止模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复/跳过 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复 | 代码与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分；职责相同→原地升级 | 职责混淆 |
| 19 | SLO 必须定义（§5.4） | 容错策略无依据 |
| 20 | 可观测性不可省略（§6.1） | 上线后黑盒 |
| 21 | 退化矩阵必须声明（§6.2） | 部分失败行为不可预测 |

---

## 蓝图拆分判定标准

| 判定条件 | 结果 | 操作 |
|---------|------|------|
| 服务对象相同 + 变更频率同步 + 依赖关系重叠 | 原地升级 | 在 §17 容量升级附录中增量记录 |
| 有独立 module_id 前缀 | 拆分 | 创建子蓝图，belongs_to=本蓝图 |
| 有独立 Phase 路线图和交付节奏 | 拆分 | 同上 |
| 有独立依赖关系图（与主体 depends_on 交集<50%） | 拆分 | 同上 |

| 场景 | 职责不同？ | 独立依赖？ | 判定 |
|------|:---:|:---:|------|
| 实验管线 + Scout Agent | 否 | 否 | 原地升级 |
| 实验管线 + 模型推理 | 是 | 是 | 拆分独立蓝图 |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。实验层为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 6 | SSoT YAML | — | — | `D:\ZephyrAlpha\architecture_model\layers\l13_experimentation.yaml` | 层级真源 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | shared/contracts/experiment/experiment_result.py | `D:\ZephyrAlpha\src\zephyr\shared\contracts\experiment\experiment_result.py` | ExperimentResult 数据类 | 共享契约——实验 消费/生产，非功能重叠 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 实验层代码 | `D:\ZephyrAlpha\src\zephyr\simulation\` | 修改 | 蓝图描述的核心代码 |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_simulation\blueprint.md` | 修改 | 本文件 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 实验层架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 实验层施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 实验层接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` (MOD-L11-001) | §4 接口契约、§10 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_research\blueprint.md` (MOD-L09-001) | §4 接口契约、§10 依赖关系 |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\simulation\` (代码) | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 更新产出物引用 | 更新配置文件 |
| 非关键补充 | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 评估影响 | 更新容量预算 |
