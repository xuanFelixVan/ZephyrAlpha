# ZephyrAlpha — AI Agent 接入宪法

> 任何 AI 进入本项目，**首先读取此文件**。

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
# 按 tag 搜索
inference_caps = registry.find_by_tags(["inference", "text"])
# 发现 A2A 协调能力
a2a_caps = registry.find_by_tags(["a2a", "coordination"])
```

### 4.1 Agent 间通信（A2A Protocol）

当你需要与其他 Agent 协作、交接任务、或解决冲突时，使用 A2A Protocol：

```python
# 发现可用 Agent
from zephyr.l01_infrastructure.a2a_protocol import card_registry
agents = card_registry.discover(capability="write")

# 发送跨 Agent 消息
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, A2AMessagePart, PartType
msg = A2AMessage(from_agent="your-id", to_agent="target-id", task_id="t-1")

# 冲突检测与仲裁
from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.conflict_detector import ConflictDetector, ChangeSet
from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.arbitrator import Arbitrator, AgentMeta, AgentRole

# 触发关键词: a2a, agent-to-agent, 冲突, 协调, 冲突解决, 多agent
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

## 8. 永远不要做的事

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
