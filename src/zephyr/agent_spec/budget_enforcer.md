# Budget Enforcer Specialist (SKILL-DOM-BGT-001)

> **模块**: MOD-INF-024 (三维预算强制执行)
> **蓝图**: docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md (v0.7.0)
> **状态**: Phase 1 — 31/31 模块完成，测试全绿，集成就绪

---

## 触发条件

- **关键词**: budget, budget-enforcer, budget_enforcer, 预算, token budget, cost limit, 成本限制, token limit, 模型降级, pre_flight, degradation, trust-ring, 信任环, ipi-defense, 指令注入防御
- **模块匹配**: budget_enforcer, MOD-INF-024
- **阶段**: construction/verification/governance

---

## 模块定位

Budget Enforcer 是 ZephyrAlpha 的 **三维预算强制护栏**——对 AI Agent 的所有 LLM 调用施加 Token/Cost/Time 三维预算约束，超限自动降级或拒绝。

### 三维预算体系

```
Token 预算 — 五级封顶 (micro/mini/standard/premium/enterprise)
    ├─ 瞬时速率 (rpm/tpm-like)
    ├─ 日配额 (daily_limit)
    └─ 滚动窗口 (sliding_window)

Cost 预算 — 美元计价强制上限
    ├─ Provider 定价 (10 models x 4 providers)
    ├─ 日总消耗 (daily_limit)
    └─ 累计消耗 (cumulative_limit)

Time 预算 — 任务级时间约束
    ├─ 单任务上限 (task_limit)
    ├─ 日总时间 (daily_limit)
    └─ 会话超时 (session_timeout)
```

### 六级降级链

```
NORMAL     → 正常模式，无限制
NOTIFY     → 达 70% 上限，发送通知
WARNING    → 达 85% 上限，强制警告
MODEL_SWITCH → 达 95% 上限，自动切换到低价模型
COMPRESS   → 达 100%，强制上下文压缩
MINIMAL    → 达 110%，仅允许最简响应
HALT       → 达 120%，完全拒绝 LLM 调用
```

---

## 核心 API

### 预算引擎（最常用入口）
```python
from zephyr.budget_enforcer import BudgetEngine, BudgetDimension, BudgetLevel

engine = BudgetEngine()
result = engine.pre_flight_check(
    operation_id="task-001",
    estimated_tokens=500,
    estimated_cost=0.02,
)
# result.decision: GateDecision (ALLOW/DENY/ALTER)
# result.budget_level: BudgetLevel (NORMAL~HALT)
# result.reason: str
```

### 预算追踪
```python
from zephyr.budget_enforcer.budget_tracker import BudgetTracker

tracker = BudgetTracker()
tracker.track_request(
    operation_id="task-001",
    tokens_used=350,
    cost_incurred=0.015,
    model="glm-4-flash",
)
usage = tracker.get_current_usage(BudgetDimension.TOKEN)
```

### 降级管理
```python
from zephyr.budget_enforcer.degradation_manager import DegradationManager

dm = DegradationManager()
dm.evaluate(_usage_ratio=0.92)  # 92% → 可能触发 MODEL_SWITCH
print(dm.current_level)  # e.g., BudgetLevel.MODEL_SWITCH
```

### 模型路由
```python
from zephyr.budget_enforcer.model_router import ModelRouter

router = ModelRouter()
model = router.select_model(
    task_type="code_generation",
    budget_level=BudgetLevel.MODEL_SWITCH,
)
# 自动选 ECONOMY 级别模型替代 PREMIUM
```

---

## 信任环

```python
from zephyr.budget_enforcer.trust_ring_manager import TrustRingManager, RingLevel

tm = TrustRingManager()
tm.register_key(agent_id, public_key_pem)
tm.grant_trust(agent_id, RingLevel.R1_ADMIN)

# R0_OWNER:  修改预算/添加模型/禁用门禁/授予信任
# R1_ADMIN:  修改预算/添加模型/查看全部/审计全部
# R2_AGENT:  查看自身/使用模型
# R3_OBSERVER: 查看摘要
```

## 安全防御

- **IPI Defense**: 检测 10 种指令提示注入攻击载荷（Forcepoint X-Labs 2026）
- **Tamper-Evident Log**: SHA256 哈希链 append-only 审计日志
- **Cold Start Anti-Abuse**: 防止 agent 绕过冷启动预算重置
- **Spiral EWS**: 螺旋式早期预警，检测 Token/Cost/Depth 异常增长模式
- **Poison Cascade Detector**: 检测中毒级联签名，防止供应链污染扩散

## 配置

- 预算策略 SSoT: `config/budget_policy.yaml`
- 模型定价: `config/model_pricing.yaml`
- Gate 门禁: `src/zephyr/gates/gct_024_budget_enforcer.yaml`
