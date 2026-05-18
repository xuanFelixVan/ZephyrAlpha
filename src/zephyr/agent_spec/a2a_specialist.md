---
blueprint_id: MOD-INF-019
---

# A2A Protocol Specialist (SKILL-DOM-A2A-001)

> **模块**: MOD-INF-025 (A2A 协调协议)
> **蓝图**: docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md (v0.10.0, 215KB, 150盲点)
> **状态**: R81-C04 Hold — Phase 1 核心就绪，Phase 2+ 待触发条件激活

---

## 触发条件

- **关键词**: a2a, agent-to-agent, agent_coordination, 多agent, 多智能体, 协调, 冲突, conflict
- **模块匹配**: a2a_protocol, MOD-INF-025
- **阶段**: construction/verification (R81-C04 Hold 时自动跳过)

---

## 模块定位

A2A 协议是 ZephyrAlpha 的 **Agent 间协调与冲突解决层**——当多个 AI Agent 并发施工时，提供发现、通信、调度、冲突检测、仲裁、死锁防护的完整框架。

### 三层架构

```
Layer 1 (发现/身份) — agent_card.py + a2a_registry.py + identity_verifier.py
    ├─ Agent Card 声明 (7 capabilities)
    ├─ Registry 注册/发现 (按capability过滤)
    └─ HMAC-SHA256 身份验证 (sign/verify + challenge)

Layer 2 (通信/任务) — a2a_schemas.py + a2a_state.py + message_router.py
    ├─ Message/Part 消息模型 (6 PartType)
    ├─ 9-state 任务状态机 (VALID_TRANSITIONS)
    ├─ Handoff/Streaming/Push 通信原语
    └─ 上下文打包 (ContextPackage: blueprints/decisions/session/locks)

Layer 3 (协调/仲裁) — supervisor.py + 42 coordination files
    ├─ Supervisor: 任务调度/死锁检测/超时升级 + Agent负载追踪
    ├─ Guards: deadlock_guard / livelock_detector / cascade_guard
    ├─ Quality: 委托链深度 / 幂等去重 / 并发准入 / 休眠/唤醒
    ├─ Security: block/unblock / consent / vector_reputation
    ├─ Economics: token→USD 成本追踪 + carbon 碳足迹
    └─ [Phase 2+]: conflict_detector / arbitrator / debate / negotiation / formal_verification / red_team
```

---

## 核心 API

### 发现与身份
```python
from zephyr.l01_infrastructure.a2a_protocol.layer1_discovery import AgentCard, A2ARegistry, IdentityVerifier
```

### 通信与任务
```python
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication import (
    A2AMessage, PartType, A2AStateMachine, MessageRouter, ContextPackage,
    HandoffManager, PushNotifier,
)
```

### 协调与调度
```python
from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination import (
    Supervisor, ConstructionVerifier,
    DeadlockGuard, LivelockDetector, CascadeGuard,
    A2AEconomics, A2AForgetting,
)
```

### 治理桥接
```python
from zephyr.a2a import GovernanceAdapter
from zephyr.governance.agent_rbac.a2a_check import verify_a2a_pair
from zephyr.governance.escalation.a2a_failure import A2AFailureHandler
```

---

## R81-C04 Hold 决策

**当前状态**: 单 Agent + 多 IDE 场景，A2A 不急需。
**触发条件**: Agent >= 3 且冲突+跨Agent任务交接 >= 5次/天。
**触发后行动**:
1. conflict_detector / arbitrator 从脚手架升级为真实实现
2. 红队攻击向量框架 → 具体攻击逻辑执行
3. 集成测试 + E2E 测试补全
4. A2A TLA+/Coq 形式化验证启动

---

## 关键文件

| 类别 | 路径 | 行数 | 状态 |
|------|------|:---:|:---:|
| 蓝图 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md | 215KB | v0.10.0 |
| 宪法 | src/zephyr/l01_infrastructure/a2a_protocol/CONSTITUTION.md | 7条 | ✅ |
| 施工验证器 | layer3_coordination/construction_verifier.py | 239行 | ✅ 自指悖论 |
| Supervisor | layer3_coordination/supervisor.py | 69行 | ✅ |
| 状态机 | layer2_communication/a2a_state.py | 55行 | ✅ |
| 注册表 | skill_registry.yaml | — | ✅ SKILL-DOM-A2A-001 |
