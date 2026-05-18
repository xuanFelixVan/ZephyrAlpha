# ZephyrAlpha — AI Agent 接入宪法

> **硬规则入口**: [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（IDE 自动注入，50 行以内全读完再开工）
> **施工指导**: [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)（详细规则/冷启动序列/方法论索引）
> **内部 Agent 系统**: [`src/zephyr/agent_spec/AGENTS.md`](file:///d:/ZephyrAlpha/src/zephyr/agent_spec/AGENTS.md)（L0/L1/L2/L3 渐进披露，Pipeline 自动注入，非 IDE AI 使用）

## 1. 项目概述

ZephyrAlpha 是一个 AI 治理框架。AutoRuntime Core 是其**系统大脑**——负责三层运行时编排、节律调度、健康监控、审计日志、工作编排、自动接入。

## 2. 终极目标

**接入项目里的所有模块、系统、脚本，能灵活运用所有东西。**

衡量标准：孤儿率 = 未接入模块数 / 总模块数 → 目标 = **0%**

## 3. 核心系统

| 系统 | 入口 | 职责 |
|------|------|------|
| AutoRuntime Core | `python -m zephyr.runtime` | 系统大脑，调度所有 AI 运行时 |
| PipelineOrchestrator | `zephyr.pipeline` | 管线编排（M1-M11） |
| AgentOrchestrator | `zephyr.orchestrator` | Agent 生命周期管理 |
| TaskRepository | `zephyr.db.task_repo` | 任务状态机（10 状态） |
| A2A Protocol | `zephyr.l01_infrastructure.a2a_protocol` | Agent 间通信与冲突解决（MOD-INF-025） |

## 4. 发现可用服务

```python
from zephyr.runtime.capability_registry import CapabilityRegistry
registry = CapabilityRegistry()
all_capabilities = registry.list_all()
inference_caps = registry.find_by_tags(["inference", "text"])
a2a_caps = registry.find_by_tags(["a2a", "coordination"])
```

### 4.1 Agent 间通信（A2A Protocol）

```python
from zephyr.l01_infrastructure.a2a_protocol import card_registry
agents = card_registry.discover(capability="write")

from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, A2AMessagePart, PartType
msg = A2AMessage(from_agent="your-id", to_agent="target-id", task_id="t-1")

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.conflict_detector import ConflictDetector, ChangeSet
from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.arbitrator import Arbitrator, AgentMeta, AgentRole
```

## 5. 三层 AI 工作分配

- **L1 Trae**: 人在 IDE 交互时使用，免费，人在环
- **L2 Local**: 24/7 自动化，Ollama 本地推理（BGE-M3 + qwen3:8b），零成本
- **L3 API**: 夜班/高价值/不确定，DeepSeek V4 Pro / Claude，有成本

## 6. 关键路径

- `specs/auto-runtime-core/`: AutoRuntime Core 蓝图规范
- `src/zephyr/runtime/`: AutoRuntime Core 实现
- `data/audit_logs/`: AI 行为审计日志
- `data/capability_cards/`: 能力卡片定义
- `data/work_dags/`: 工作 DAG 定义
- `architecture-model/`: 全部蓝图 YAML

## 7. 代码规范

- Python 3.11+, ruff lint, pydantic v2
- 所有新组件**必须**注册 CapabilityCard 到 CapabilityRegistry
- 所有 AI 行为**必须**写入 AiAuditLogger
- 详细编码约束见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（四条铁律 + 写代码三条）和 [`code-construction-standards.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)（GOV-ENG-001）
- 治理决策方法论见 [`governance-methodology-standard.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/meta/governance-methodology-standard.md)（PS-STD-011）——含MTH-006诊断反转验证：深挖后MUST回溯初始诊断，不一致时追问"为什么初始诊断错了？"
- 审计脚本质量见 [`quality-standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality-standard.md)（SCRIPT-QUALITY-001）
- 产出物规格化见 [`compression-workflow-standard.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/compression-workflow-standard.md)（GOV-DOC-011）

## 8. 永远不要做的事

> 完整禁止清单见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 四条铁律。此处仅列项目宪法级禁令：

- 不要删除 `data/` 下的任何文件
- 不要跳过 `CapabilityRegistry.register()`
- 不要修改 `AiAuditLogger` 的已有日志
- 不要创建新模块而不注册到大脑

## 9. 新模块接入规则

创建新模块时，必须：
1. 构造 CapabilityCard 并注册到 CapabilityRegistry
2. 在 `data/capability_cards/` 下创建对应的 YAML
3. 如果有自动化工作，创建 WorkDAG 并注册到 WorkOrchestrator
4. 写入 AiAuditLogger 记录注册事件

如果不注册，ModuleOnboardingScanner 会在扫描时发现并自动触发接入流程。