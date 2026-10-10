---
blueprint_id: MOD-AU-006
module_id: MOD-AU-006
module_name: per_agent_gate
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P0
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/per_agent_gate.py
granularity: file
responsibility_domain: 
---

# MOD-AU-006 per_agent_gate 蓝图（单 Agent 门控层 / Per-Agent Gate）

> **module_id**: MOD-AU-006 | **域**: D_AUTONOMY_CORE | **优先级**: P0
> **来源**: CAND-AUTONOMYCORE-005（B11-02462，AUD-DRAFT-001-DIGEST P0 波 W2d）
> 代码：`src/zephyr/autonomy_core/per_agent_gate.py`

## 0. 定位

Per-Agent Gate：规则集（允许动作 / 禁止动作 / 限额 / 时段）内嵌 Agent Card，
门控为**纯内存规则匹配**（<0.1ms 无 IO）；DENY 产安全事件（委托
security_event_bus MOD-SEC-EVENTBUS 持久化，本模块经 event_sink 回调接线不 import）。
与 A2A 检查网关（CAND-INFRAA2A-001）双层分工：**本层管单 Agent 自约束，
网关管跨 Agent 通信**。与 task_gate/stop_gate（MOD-INF-035，任务级/停止级）
互补——本层是 Agent 内置规则门控。

## 1. 规则集与判定序

`AgentGateRuleSet`（frozen，内嵌 Agent Card）：
- `allow_actions` 白名单（空=不启用）；`deny_actions` 黑名单（**优先于白名单**）；
  两者交集非空视为配置矛盾拒绝登记。
- `max_notional_per_order` 单笔名义限额（None=不限）。
- `allowed_windows` 日内分钟窗（空=全时段；`[start_min, end_min)`，0<=start<end<=1440）。

判定序（短路）：①黑名单 DENY → ②白名单未命中 DENY → ③超限额 DENY →
④窗外 DENY → ⑤ALLOW。未登记 agent fail-closed DENY。

## 2. 接口

```python
@dataclass(frozen=True) TimeWindow: start_min/end_min; contains(minute)->bool
@dataclass(frozen=True) AgentGateRuleSet: agent_id/allow_actions/deny_actions/max_notional_per_order/allowed_windows
class GateDecision(str, Enum): ALLOW/DENY
@dataclass(frozen=True) AgentGateVerdict: agent_id/action/decision/matched_rule/reason/fail_closed; to_security_event()->dict
class PerAgentGate(rulesets=None, event_sink=None):
    .register(ruleset) / .check(agent_id, action, *, notional=None, minute_of_day=None) -> AgentGateVerdict
class InvalidAgentGateConfigError(ZephyrBaseError)
```

## 3. 不变量

- check 纯内存无 IO、同输入必同输出；DENY 时经 event_sink 写安全事件（sink 异常不阻断 DENY）。
- 未登记 agent / 空 agent_id / 空 action → fail-closed DENY。
- 黑名单恒优先；限额只在校验值非 None 时生效；时段只在声明了窗口时生效。
- 规则集 frozen 不可变，重复登记同一 agent_id 拒绝。

## 4. 依赖

- MOD-INF-035 capability_card（设计边：规则集内嵌 Agent Card 的契约宿点）
- MOD-SEC-EVENTBUS security_event_bus（设计边：DENY 安全事件持久化通道）

## 5. MVP 边界

- Agent Card YAML 落盘与热加载、security_event_bus 真实订阅接线留运行时装配批；
  本模块交付规则集模型 + 纯内存判定核心 + 安全事件契约（to_security_event dict）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
