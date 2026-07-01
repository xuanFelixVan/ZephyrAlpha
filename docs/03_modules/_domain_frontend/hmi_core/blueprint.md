---
module_id: MOD-L08-001
submodule_path: src/zephyr/frontend
title: "Human Machine Interface Core 蓝图 — 人机交互层（C轨·禁止施工）"
doc_type: blueprint
status: Active
version: "2.1.0"
layer: frontend
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/frontend/"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 2
functional_domain: interface
summary: "⛔ C轨业务层未开放，禁止施工。人机交互层。DashboardBase+NotificationManagerBase+ApprovalGatewayBase为OCP扩展点。Streamlit Dashboard 5页面已实现。默认实现待施工。"
tags: [human-ai-interface, l08, dashboard, streamlit, notification, approval, blocked-by-infrastructure, do-not-implement]
priority: P1
runtime_plane: warm
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-FLE
    at: "§10"
    why: "FitnessFunctionFramework + FitnessInputs"
  - target: MOD-DATABASE
    at: "§10"
    why: "TaskRepository"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l08_human_ai_interface.yaml"
    section: ""
    why: "架构层YAML真源"
codification_level: L1
codification_at: "2026-05-15"
ai_read_only_hint: DO_NOT_IMPLEMENT
---

> ⛔ **C轨业务层未开放，禁止施工**
>
> 本蓝图所属的C轨业务层当前处于 `not_started` 状态。
> 开工触发条件（同 MOD-MASTER_BLUEPRINT §零）：
> (a) MOD-MASTER_BLUEPRINT 的 construction_progress >= implementation_phase；
> (b) Gate Engine 覆盖了本层相关的业务检查类型；
> (c) 至少一个 CT-* 契约从规划到部分实现，打通了本层的集成通路。
> 在此条件满足前，本蓝图仅供 AI 阅读以了解架构意图，**严禁生成业务代码或执行施工步骤**。

> module_id: MOD-L08-001 | version: 2.1.0 | status: active | domain: frontend
> actual_disk_path: src/zephyr/frontend/ | generation: 2 | construction_progress: not_started

# Human Machine Interface Core 蓝图+施工图 — 人机交互层（C轨·禁止施工）

> **真源声明**：本蓝图是 ZephyrAlpha 人机交互层的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 人机交互层——它解决了系统与用户之间的标准化交互问题。核心职责包括：监控面板(DashboardBase)、通知分发(NotificationManagerBase)、人工审批(ApprovalGatewayBase)三个 OCP 扩展点，以及 Streamlit Dashboard 5 页面组件。当前规模 3 个 Base 类 + 5 个 Dashboard 组件已实现，DefaultNotificationManager 和 DefaultApprovalGateway 待施工。上游依赖 FLE Fitness Functions 和 TaskRepository，下游被 L04 Risk Management 和 L07 Post-Trade Analytics 消费。

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
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L08-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | interface_base.py | §3.1 | DashboardBase + NotificationManagerBase + ApprovalGatewayBase + Notification + ApprovalRequest + NotificationLevel + ApprovalAction | 已实现 |
| 2 | dashboard/app.py | §3.1 | Streamlit Dashboard 主应用 (DashboardApp + create_app + main) | 已实现 |
| 3 | dashboard/components/fitness_functions.py | §3.1 | Fitness Functions 组件 | 已实现 |
| 4 | dashboard/components/gate_statistics.py | §3.1 | 门禁统计组件 | 已实现 |
| 5 | dashboard/components/knowledge_overview.py | §3.1 | 知识库概览组件 | 已实现 |
| 6 | dashboard/components/olap_trend.py | §3.1 | OLAP 趋势组件 | 已实现 |
| 7 | dashboard/components/task_progress.py | §3.1 | 任务进度组件 | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = not_started → 代码目录存在但业务实现不完整 | `ls src/zephyr/frontend/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| §0.1 已实现文件全部存在 | 逐文件 `ls` | ☐ |
| §0.1 未实现文件确实不存在 | 逐文件 `ls` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | DashboardBase, NotificationManagerBase, ApprovalGatewayBase, DashboardApp, 5 个组件 | DefaultNotificationManager, DefaultApprovalGateway | C轨禁止施工 |
| v2.0.0 (模板重构) | 同 v1.0.0 + 结构重组 | DefaultNotificationManager, DefaultApprovalGateway | C轨禁止施工 |
| v2.1.0 (回填+禁止施工) | 同 v2.0.0 + 接口契约与代码对齐 | DefaultNotificationManager, DefaultApprovalGateway | C轨禁止施工 |

---

## §1 设计背景与目标

### 1.1 背景

C轨人机交互层是系统与用户之间的桥梁。当前B轨治理基础设施已稳定运行，但C轨业务层尚未开放施工（ARB-11裁定：T0先行层需等待B轨容量升级完成）。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 监控面板标准化 | DashboardBase OCP 扩展点可用 |
| 2 | ✅ 包含 | 通知分发标准化 | NotificationManagerBase OCP 扩展点可用 |
| 3 | ✅ 包含 | 人工审批标准化 | ApprovalGatewayBase OCP 扩展点可用 |
| 4 | ✅ 包含 | Streamlit Dashboard | 5 页面可渲染 |
| 5 | ✅ 包含 | Fitness Functions 展示 | EXT-DASHBOARD-FLE-001 消费 FLE Facade |
| 6 | ❌ 排除 | 风险计算 | L04 Risk Management |
| 7 | ❌ 排除 | 归因分析 | L07 Post-Trade Analytics |
| 8 | ❌ 排除 | 数据采集 | L00 Data Source |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Streamlit 为可选依赖 | import 失败时降级为 CLI 输出 |
| Dashboard 组件独立可渲染 | 每个组件 fetch+render 分离 |
| OLAPEngine 可能不可用 | 门禁统计/OLAP 趋势组件返回空 dataclass |
| C轨 not_started | 业务代码禁止施工，仅B轨集成代码可运行 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策+施工审批 | 设计+施工 | C轨开放审批权 |
| L04 Risk Management | 风险仪表盘数据消费 | 集成 | CTR-P1-008 |
| L07 Post-Trade Analytics | 归因报告数据消费 | 集成 | CTR-P1-009 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 通知渠道 | 0 实现 | 3 渠道 | 无 DefaultNotificationManager | P1 |
| 审批流程 | 0 实现 | 5 流程 | 无 DefaultApprovalGateway | P1 |
| C轨集成 | blocked | active | B轨容量升级未完成 | P0 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| Dashboard 查看任务进度 | 用户打开 Dashboard | DashboardApp.get_task_progress() → fetch_task_progress(task_repo) → render | TaskProgressData |
| 风控硬限审批 | L05/L06 触达风控硬限 | ApprovalGatewayBase.submit(request) → 人工查看 → decide(approve/reject) | 审批结果写回 |
| 告警通知 | 系统异常/SLI越界 | NotificationManagerBase.send(notification, channels) → 多渠道分发 | 通知送达确认 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 监控面板 | DashboardBase + DashboardApp (Streamlit) | 本模块 |
| 2 | ✅ 包含 | 通知分发 | NotificationManagerBase | 本模块 |
| 3 | ✅ 包含 | 人工审批 | ApprovalGatewayBase | 本模块 |
| 4 | ✅ 包含 | 任务进度看板 | TaskProgressData + fetch_task_progress | 本模块 |
| 5 | ✅ 包含 | 知识库概览 | KnowledgeOverviewData + fetch_knowledge_overview | 本模块 |
| 6 | ✅ 包含 | 门禁统计 | GateStatisticsData + fetch_gate_statistics | 本模块 |
| 7 | ✅ 包含 | Fitness Functions 仪表盘 | FitnessDashboardData + fetch_fitness_data | 本模块 |
| 8 | ✅ 包含 | OLAP 趋势 | OLAPTrendData + fetch_olap_trends | 本模块 |
| 9 | ❌ 排除 | 风险计算 | L04 Risk Management | L04 |
| 10 | ❌ 排除 | 绩效归因 | L07 Post-Trade Analytics | L07 |
| 11 | ❌ 排除 | Fitness Functions 计算 | feedback_loop/fitness_functions.py | MOD-FEEDBACK_LOOP |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | DashboardBase | 面板 OCP 扩展点（render/refresh） | — | 同步调用 |
| 2 | NotificationManagerBase | 通知 OCP 扩展点（send/channels） | — | 同步调用 |
| 3 | ApprovalGatewayBase | 审批 OCP 扩展点（submit/decide/pending） | — | 同步调用 |
| 4 | DashboardApp | Streamlit 主应用 | DashboardBase | 组合 |
| 5 | Dashboard 组件(5 个) | 独立可渲染面板 | DashboardApp | 组合 |
| 6 | Notification | 通知消息 dataclass | — | 数据传递 |
| 7 | ApprovalRequest | 审批请求 dataclass | — | 数据传递 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | FLE Fitness Functions | fetch → render | 用户 | FitnessDashboardData |
| 2 | TaskRepository | fetch → render | 用户 | TaskProgressData |
| 3 | KbRepo | fetch → render | 用户 | KnowledgeOverviewData |
| 4 | OLAPEngine | fetch → render | 用户 | GateStatisticsData / OLAPTrendData |
| 5 | L04 Risk Management | CTR-P1-008 消费 | Dashboard | RiskDashboardSnapshot |
| 6 | L07 Post-Trade Analytics | CTR-P1-009 消费 | Dashboard | PerformanceAttributionReport |

### 3.3 状态生命周期

本模块无状态机。

---

## §4 接口契约

> ⚠️ 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。
> 本模块 interface_base.py 中 Notification/ApprovalRequest 使用 `@dataclass(frozen=True)` 是历史遗留，新模型 MUST 使用 Pydantic BaseModel。

### 4.1 公共 API

```python
from zephyr.frontend.interface_base import (
    DashboardBase, NotificationManagerBase, ApprovalGatewayBase,
    Notification, ApprovalRequest, NotificationLevel, ApprovalAction,
)

class DashboardBase:
    """面板 OCP 扩展点——新面板类型继承此类"""
    def render(self, data: dict[str, Any]) -> None: ...
    def refresh(self, interval_s: float = 5.0) -> dict[str, Any]: ...

class NotificationManagerBase:
    """通知 OCP 扩展点——新通知渠道继承此类"""
    def send(self, notification: Notification, channels: list[str] | None = None) -> bool: ...
    def channels(self) -> list[str]: ...

class ApprovalGatewayBase:
    """审批 OCP 扩展点——新审批流程继承此类"""
    def submit(self, request: ApprovalRequest) -> str: ...
    def decide(self, request_id: str, action: ApprovalAction, comment: str = "") -> bool: ...
    def pending(self) -> list[ApprovalRequest]: ...
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum

class NotificationLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    DELEGATE = "delegate"
    ESCALATE = "escalate"

class TaskProgressData(BaseModel):
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., description="进度百分比")

class FitnessDashboardData(BaseModel):
    metric_name: str = Field(..., description="度量名称")
    value: float = Field(..., description="度量值")
    trend: str = Field(default="stable", description="趋势")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `send()` | `notification` | ✅ | Notification 实例 |
| `send()` | `channels` | ❌ | list[str] 或 None |
| `submit()` | `request` | ✅ | ApprovalRequest 实例 |
| `decide()` | `request_id` | ✅ | 非空字符串 |
| `decide()` | `action` | ✅ | ApprovalAction 枚举 |
| `decide()` | `comment` | ❌ | 字符串 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `send()` | `bool (True)` | `NotificationError` |
| `channels()` | `list[str]` | — |
| `submit()` | `request_id: str` | `ApprovalError` |
| `decide()` | `bool` | `ApprovalNotFoundError` |
| `pending()` | `list[ApprovalRequest]` | — |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Base 子类 | ✅ 向后兼容 | OCP 扩展 |
| Dashboard 组件新增 | ✅ 向后兼容 | 不影响已有组件 |
| 删除/重命名 Base 方法 | ❌ 破坏性 | 需 Owner 审批+迁移方案 |

**变更通知**：破坏性变更→Owner 审批+蓝图 minor+1。兼容性变更→AI 自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | DashboardBase 为 OCP 扩展点 | 新面板类型只加不改 |
| 2 | NotificationManagerBase 为 OCP 扩展点 | 新通知渠道只加不改 |
| 3 | ApprovalGatewayBase 为 OCP 扩展点 | 新审批流程只加不改 |
| 4 | Dashboard 组件独立可渲染 | fetch+render 分离 |
| 5 | Streamlit 为可选依赖 | import 失败时降级为 CLI |
| 6 | C轨 not_started | 禁止施工，仅可阅读 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| Dashboard 页面数 | 5 | 10 | 无上限 | ✅ | 组件化扩展 |
| 通知渠道数 | 0 (待实现) | 3 | 无上限 | ✅ | OCP 扩展 |
| 审批流程数 | 0 (待实现) | 5 | 无上限 | ✅ | OCP 扩展 |

### 5.3 迁移

本蓝图不涉及迁移。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | Dashboard 可渲染率 | 99% | 页面加载测试 | 渲染成功率 | 99% | 每月允许1次不可用 | 连续2次不可用 |
| 可维护性 | 新组件接入时间 | <30min | 开发记录 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 直接 import streamlit 在 interface_base.py | dashboard/app.py 内部 import | Streamlit 为可选依赖 |
| 2 | 导入源 | from zephyr.l04_* 直接调用 | 通过 CTR-P1-008 契约消费 | 分层约束 |
| 3 | 编码模式 | 在 Base 类中写业务逻辑 | Base 类只定义抽象接口 | OCP 扩展点约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Streamlit 未安装 | ImportError | 降级为 CLI 输出 | Dashboard 不可用 |
| 2 | OLAPEngine 不可用 | 连接异常 | 组件返回空 dataclass | 门禁统计/OLAP 趋势为空 |
| 3 | KbRepo 不可用 | 连接异常 | 组件返回空 dataclass | 知识库概览为空 |
| 4 | FLE Facade 不可用 | 连接异常 | Fitness 组件显示错误状态 | Fitness 仪表盘不可用 |
| 5 | 未知页面名 | render_page default | 返回 {"error": "Unknown page: ..."} | 单页面不可用 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| dashboard_render_success_rate | Gauge | 自动埋点 | <95% | P2 |
| notification_send_latency_ms | Histogram | 手动上报 | >5000ms | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| Streamlit | CLI 输出 | Dashboard 渲染 | 降级为 CLI | Streamlit 安装 |
| OLAPEngine | 其他4页面 | 门禁统计/OLAP趋势 | 返回空 dataclass | OLAPEngine 恢复 |
| KbRepo | 其他4页面 | 知识库概览 | 返回空 dataclass | KbRepo 恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 审批绕过 | 高 | ApprovalGatewayBase 强制审批流 | 单元测试验证审批不可跳过 |
| 2 | 通知信息泄露 | 中 | 敏感信息脱敏后发送 | 扫描脚本检测 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | DashboardBase/组件 | fetch 返回正确 dataclass | 覆盖率>80% |
| 2 | 单元测试 | NotificationManagerBase | send 返回 bool | 覆盖率>80% |
| 3 | 单元测试 | ApprovalGatewayBase | submit/decide/pending 返回正确类型 | 覆盖率>80% |
| 4 | 集成测试 | DashboardApp + 数据源 | 5 页面端到端渲染 | 端到端通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| feedback_loop/fitness_functions | 必须 | FitnessFunctionFramework + FitnessInputs | — | `D:\ZephyrAlpha\src\zephyr\feedback_loop\fitness_functions.py` |
| db/task_repo | 必须 | TaskRepository | — | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` |
| db/kb_repo | 可选 | KbRepo | — | `D:\ZephyrAlpha\src\zephyr\db\kb_repo.py` |
| db/olap_engine | 可选 | OLAPEngine | — | `D:\ZephyrAlpha\src\zephyr\db\olap_engine.py` |
| MOD-L04-001 Risk Management | 可选 | CTR-P1-008 RiskDashboardSnapshot | — | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\risk-core\blueprint.md` |
| MOD-L07-001 Post-Trade Analytics | 可选 | CTR-P1-009 PerformanceAttributionReport | — | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\analytics_core\blueprint.md` |
| MOD-INF-035 系统大脑 | 可选 | 运维可视化 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-INF-015 系统遥测 | 可选 | 告警通道 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infra_ops\system_telemetry\blueprint.md` |
| MOD-GATE_ENGINE 门禁引擎 | 可选 | 人机协同 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐状态 | 说明 |
|---|--------|:---:|------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.7 | 已对齐 | L08 3子模块+Manifest额外资产+消费契约一致 |
| 2 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 未对齐 | C轨DEP待注册(ARB-15) |
| 3 | §10.1 依赖声明 ↔ 各依赖蓝图 §4 契约 | 未对齐 | CTR-P1-008/009待验证 |

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| interface_base.py | dashboard/app.py | DashboardBase/NotificationManagerBase/ApprovalGatewayBase | 函数调用 |
| dashboard/components/*.py | dashboard/app.py | 各组件 Data + render 函数 | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块简单 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | C轨DEP注册盲区 | CI门禁 | validate_path_alignment.py | C轨未注册 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 不适用 | — | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | C轨开放后需验证 | pytest+ruff | pytest | C轨blocked | CI pipeline | 代码提交时 |

---

## §11 产出物

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_frontend\hmi_core\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\frontend\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\frontend\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| FLE Fitness Functions | EXT-DASHBOARD-FLE-001 消费 | Dashboard 可展示 Fitness 度量 | Dashboard 可渲染 |
| TaskRepository | 直接查询 | 任务进度看板可渲染 | 看板可渲染 |
| KbRepo | 直接查询 | 知识库概览可渲染 | 概览可渲染 |
| OLAPEngine | 直接查询 | 门禁统计+OLAP 趋势可渲染 | 统计可渲染 |
| L04 Risk Management | CTR-P1-008 消费 | 风险仪表盘可展示 | 风险面板可渲染 |
| MOD-INF-035 系统大脑 | 运维可视化 | Dashboard 嵌入系统大脑 | Dashboard 可渲染 |
| MOD-INF-015 系统遥测 | 告警通道 | 通知推送 | 通知可达 |
| MOD-GATE_ENGINE 门禁引擎 | 人机协同 | CLI 命令交互 | CLI 可执行 |

### 12.1 域契约锚点

本模块无域治理集成契约。

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新为 not_started | C轨禁止施工 |
| 2 | 架构层 YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l08_human_ai_interface.yaml` | module id 统一为 hmi_core (ARB-21) | 命名统一 |

---

## §14 风险

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | Streamlit 未安装 | 中 | Dashboard 无法渲染 | import 降级为 CLI 输出 | 风险 |
| 2 | YAML module id 不一致 | 低 | 发现困难 | ARB-21 统一为 hmi_core | 风险 |
| 3 | OLAPEngine 不可用 | 中 | 门禁统计/OLAP 趋势为空 | 组件返回空 dataclass | 风险 |
| 4 | KbRepo 不可用 | 中 | 知识库概览为空 | 组件返回空 dataclass | 风险 |
| 5 | C轨未开放导致蓝图与代码不同步 | 中 | 蓝图标注blocked但代码已存在 | 蓝图明确标注已实现代码范围 | 风险 |
| 6 | 新渠道需实现对应 Base 类 | — | 中 | OCP 扩展点文档 + 示例 | 负面后果 |
| 7 | 依赖 Streamlit 运行时 | — | 中 | 可选依赖 + CLI 降级 | 负面后果 |

---

## §16 施工指引

> ⛔ **C轨业务层禁止施工**——以下施工步骤仅在 C轨开放后可执行。
> 开工触发条件见蓝图开头禁止施工声明。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 5 | C轨已开放施工（construction_progress ≠ not_started） | 检查 frontmatter | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | Dashboard 数据源稳定性 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板 v4.1 重构） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | DashboardBase 定义 | hard | 已实现 | ✅ |
| 2 | NotificationManagerBase 定义 | hard | 已实现 | ✅ |
| 3 | ApprovalGatewayBase 定义 | hard | 已实现 | ✅ |
| 4 | TaskRepository | hard | 已实现 | ✅ |
| 5 | FitnessFunctionFramework | hard | 已实现 | ✅ |
| 6 | C轨开放施工 | hard | blocked | ❌ |

### 16.3 实施步骤

#### 步骤 1：实现 DefaultNotificationManager

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 NotificationManagerBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_notification_manager.py` |
| 验收标准 | import 成功，send 返回 bool，channels 返回 list[str] |
| 验证命令 | `python -c "from zephyr.frontend.implementations.default_notification_manager import DefaultNotificationManager"` |
| G7 检查项 | 上游 interface_base.py 存在，下游可调用 |
| AI 自治范围 | human_gated |
| 检查点 | 文件存在且非空 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-L08-001 | default_notification_manager.py | code | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_notification_manager.py` |

#### 步骤 2：实现 DefaultApprovalGateway

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 ApprovalGatewayBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_approval_gateway.py` |
| 验收标准 | import 成功，submit 返回 request_id，decide 返回 bool，pending 返回 list |
| 验证命令 | `python -c "from zephyr.frontend.implementations.default_approval_gateway import DefaultApprovalGateway"` |
| G7 检查项 | 上游 interface_base.py 存在，下游可调用 |
| AI 自治范围 | human_gated |
| 检查点 | 文件存在且非空 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-L08-001 | default_approval_gateway.py | code | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\default_approval_gateway.py` |

#### 步骤 3：接入 CTR-P1-008/P1-009

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 DashboardBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\app.py` |
| 验收标准 | 新增风险/归因 Dashboard 页面，L04/L07 数据可展示 |
| 验证命令 | `python -m pytest tests/frontend/ -k dashboard` |
| G7 检查项 | 下游 L04/L07 数据可消费 |
| AI 自治范围 | ai_modifiable |
| 检查点 | Dashboard 6 页面可渲染 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultNotificationManager 实现失败 | 还原 implementations/ |
| 2 | DefaultApprovalGateway 实现失败 | 还原 implementations/ |
| 3 | Dashboard 页面接入失败 | 还原 dashboard/app.py |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | DefaultNotificationManager 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | DefaultApprovalGateway 存在 | `ls` exit 0 | 完成 | ☐ |
| 3 | DashboardApp 6 页面可渲染 | pytest 通过 | 完成 | ☐ |
| 4 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | DashboardApp 页面路由 | 算法 | page_name → fetch_{page}() → render_{page}() | dashboard/app.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `streamlit run src/zephyr/frontend/dashboard/app.py` | 启动 Dashboard | — | Streamlit Web UI |
| 2 | 命令 | `python -m pytest tests/frontend/` | 运行测试 | `-k {pattern}` | pytest 输出 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | Streamlit 启动失败 | ImportError | `pip install streamlit` | Dashboard 可用 | 重新启动 |
| 2 | 运行 | 数据源不可用 | 连接异常 | 检查 SQLite/DuckDB 路径 | 组件返回空 dataclass | 数据源恢复 |
| 3 | 运行 | 紧急冻结 | 安全事件 | 冻结写入+只读 | — | 威胁解除 |

### 16.12 并发操作模型

本模块无并发操作。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| Dashboard 页面数 | 5 | 组件计数 |
| 通知渠道数 | 0 | NotificationManagerBase 子类计数 |
| 审批流程数 | 0 | ApprovalGatewayBase 子类计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L08-001 | 无通知渠道实现 | 实现 DefaultNotificationManager | P1 | 通知需求>0 | v2.1.0 | 待施工 |
| GAP-L08-002 | 无审批流程实现 | 实现 DefaultApprovalGateway | P1 | 审批需求>0 | v2.1.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | DashboardBase+NotificationManagerBase+ApprovalGatewayBase+5 组件 | ⚠️ |
| v2.0.0 | 2 | 模板重构 | 章节重排+新增概述+frontmatter 补全 | ⚠️ |
| v2.1.0 | 2 | 回填+禁止施工 | 接口契约与代码对齐+模板回填+禁止施工标注 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工 Phase | 状态 |
|--------|---------|---------|----------|:---:|
| DefaultNotificationManager | GAP-L08-001 | default_notification_manager.py | Phase 1 | 待施工 |
| DefaultApprovalGateway | GAP-L08-002 | default_approval_gateway.py | Phase 2 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L08-01 | C轨占位策略 | A: 完整蓝图 / B: 占位蓝图 | B | ARB-11裁定C轨blocked | 2026-05-05 |
| 2 | D-L08-02 | Streamlit 可选依赖 | A: 必选 / B: 可选+CLI降级 | B | 1人运维约束(ARB-3) | 2026-05-05 |
| 3 | D-L08-03 | OCP 扩展点设计 | A: 具体实现 / B: 抽象基类+注册表 | B | 开闭原则+多渠道扩展 | 2026-05-05 |
| 4 | D-L08-04 | Notification/Approval 使用 dataclass | A: Pydantic BaseModel / B: dataclass(frozen=True) | B | 历史遗留；新模型MUST用Pydantic(KBG-0040) | 2026-05-05 |
| 5 | D-L08-05 | 模板v4.1升级 | A: 保持v3.3 / B: 按v4.1升级 | B | v4.1模板合规 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| OCP 扩展点 | 开闭原则扩展点——Base 抽象类，新类型继承扩展，不修改已有代码 | 插件 | 插件可独立加载；OCP扩展点需继承Base |
| C轨 | C-Track，业务价值线（L00-L13） | B轨 | B轨=基础设施治理线；C轨=业务交易线 |
| blocked_by_infrastructure | 因基础设施未就绪而禁止施工的状态 | design_only | design_only=仅设计未施工；blocked=有设计但被外部条件阻断 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | Notification/Approval 使用 dataclass 而非 Pydantic BaseModel | 中 | 历史遗留 | 新模型MUST用Pydantic；旧模型待迁移 | §4 | 待解决 |
| 2 | CTR-P1-008/009 契约未注册到 cross-module-dependency-registry.yaml | 中 | C轨DEP注册盲区(ARB-15) | C轨开放时补注册 | §10.2 | 待解决 |
| 3 | §0.1 已实现文件缺少 implementations/ 目录 | 低 | Default 实现未施工 | C轨开放后施工 | §16.3 | 待解决 |

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
| 11 | 中 | 新代码文件头部十字段完整 | 逐文件核对 | ☐ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | C轨开放+Default实现完成 | OCP扩展点设计稳定 |
| 接口契约 | stable | 高 | Default实现验证通过 | Base类接口与代码对齐 |
| 数据模型 | evolving | 中 | 迁移dataclass→Pydantic | 历史遗留dataclass |
| 施工步骤 | evolving | 中 | C轨开放 | blocked状态 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | C轨占位蓝图 | — | 已完成 |
| v1.0.0 | Base类+5组件实现 | v0.1.0 | 已完成 |
| v2.0.0 | 模板重构+压缩 | v1.0.0 | 已完成 |
| v2.1.0 | 回填+禁止施工标注+接口对齐 | v2.0.0 | 已完成 |
| v2.2.0 | DefaultNotificationManager+DefaultApprovalGateway | v2.1.0 | 待施工(C轨开放后) |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 关键信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 上下文缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复 | 蓝图与代码漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定 | 职责混淆 |
| 16 | 术语表不可省略 | 术语理解漂移 |
| 17 | 参考实现规格 vs 已实现代码重复 | 逻辑实现错误/双源漂移 |
| 18 | 对标验证表格 vs 对标散文 | 丢表格/留散文 |
| 19 | SLO 必须定义 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略 | 上线后黑盒 |
| 21 | 退化矩阵必须声明 | 部分失败时行为不可预测 |

---

## 蓝图拆分判定标准

### 判定流程

| 步骤 | 判定问题 | 判定结果 | 行动 |
|------|---------|---------|------|
| 1 | 拟新增/修改的内容与当前蓝图的职责是否相同？ | 相同 → 继续；不同 → 步骤 2 | 职责相同→原地升级 |
| 2 | 不同职责的内容是否有独立的上游/下游依赖链？ | 有 → 步骤 3；无 → 原地升级 | 无独立依赖→原地升级 |
| 3 | 拆分后两个蓝图是否各自自包含？ | 是 → 拆分；否 → 原地升级 | 自包含→拆分独立蓝图 |

### 判定示例

| 场景 | 职责相同？ | 独立依赖链？ | 各自自包含？ | 判定 |
|------|:---:|:---:|:---:|------|
| L08 新增通知渠道实现 | ✅ 相同 | — | — | 原地升级 |
| L08 新增数据采集模块 | ❌ 不同 | ✅ 有 | ✅ 是 | 拆分独立蓝图 |
| L08 新增风控计算逻辑 | ❌ 不同 | ✅ 有 | ✅ 是 | 拆分独立蓝图(L04已覆盖) |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。人机交互层为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type 词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

无。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | interface_base.py | `D:\ZephyrAlpha\src\zephyr\frontend\interface_base.py` | 读取 | 无变更 |
| 2 | dashboard/ | `D:\ZephyrAlpha\src\zephyr\frontend\dashboard\` | 修改 | 完善组件 |
| 3 | implementations/ | `D:\ZephyrAlpha\src\zephyr\frontend\implementations\` | 新建 | 默认实现(C轨开放后) |

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
| Tier 1 | FLE Fitness Functions | §4 接口契约、§10 依赖关系 |
| Tier 2 | L04 Risk Management | CTR-P1-008 RiskDashboardSnapshot |
| Tier 2 | L07 Post-Trade Analytics | CTR-P1-009 PerformanceAttributionReport |
| Tier 2 | MOD-INF-035 系统大脑 | 运维可视化 |
| Tier 2 | MOD-INF-015 系统遥测 | 告警通道 |
| Tier 2 | MOD-GATE_ENGINE 门禁引擎 | 人机协同 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| Base 类接口变更 | 需 Owner 审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| Dashboard 组件变更 | AI 可自主修改 | — | 更新配置文件 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | — | — |
| 非关键补充 | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
