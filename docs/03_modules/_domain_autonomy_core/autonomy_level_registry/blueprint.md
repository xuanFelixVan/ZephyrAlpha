---
blueprint_id: MOD-AU-005
module_id: MOD-AU-005
module_name: autonomy_level_registry
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
path: src/zephyr/autonomy_core/autonomy_level_registry.py
granularity: file
responsibility_domain: 
---

# MOD-AU-005 autonomy_level_registry 蓝图（Agent 自治边界 Level 0-3 四级自治模型）

> **module_id**: MOD-AU-005 | **域**: D_AUTONOMY_CORE | **优先级**: P0
> **来源**: CAND-AUTONOMYCORE-004（B11-02454，AUD-DRAFT-001-DIGEST P0 波 W2d）
> 代码：`src/zephyr/autonomy_core/autonomy_level_registry.py`

## 0. 定位

四级自治注册表：每 Agent 角色声明自治级别（L0 纯规则 / L1 建议 / L2 审批后执行 /
L3 自主）入 Agent Card；级别对三区映射（human_gated / immutable_core **不可降级**，
即声明级别抬不过区上限）；运行时供 autonomy_boundary_gate（MOD-AU-001）按级别
拦截，越级行为产出 kill_switch 触发信号与审计记录（委托 MOD-AU-002 执行，本模块
不 import 执行体，仅产信号）。

## 1. 级别语义与区上限

| 级别 | 语义 | execute 判定 |
|------|------|--------------|
| L0_RULE | 纯规则：仅确定性规则输出，无自主执行 | DENY（越级 immutable 时触发 kill_switch） |
| L1_SUGGEST | 建议：可产出建议，不执行 | DENY |
| L2_APPROVAL | 审批后执行 | REQUIRE_APPROVAL（approval_granted=True → ALLOW） |
| L3_AUTONOMOUS | 自主执行 | ALLOW（仍受区上限约束） |

区上限（声明不可抬升，"human_gated/immutable 不可降级"）：
`ai_modifiable→L3 / human_gated→L2 / immutable_core→L0`；
有效级别 = min(声明级别, 区上限)。immutable_core 上的 execute 一律 DENY 且
`kill_switch_triggered=True`。

## 2. 接口

```python
class AutonomyLevel(IntEnum): L0_RULE/L1_SUGGEST/L2_APPROVAL/L3_AUTONOMOUS
class BoundaryZone(str, Enum): AI_MODIFIABLE/HUMAN_GATED/IMMUTABLE_CORE
class AutonomyDecision(str, Enum): ALLOW/REQUIRE_APPROVAL/DENY
@dataclass(frozen=True) AgentAutonomyDeclaration: agent_role/level/declared_by/rationale
@dataclass(frozen=True) AutonomyCheckVerdict: agent_role/level/effective_level/action/zone/decision/reason/fail_closed/kill_switch_triggered; audit_record()
class AutonomyLevelRegistry(declarations=None, violation_hook=None):
    .register(agent_role, level, *, declared_by="", rationale="") -> AgentAutonomyDeclaration
    .level_of(agent_role) -> AutonomyLevel            # 未登记 fail-closed 视为 L0
    .check_action(agent_role, action, *, mode="execute", zone=AI_MODIFIABLE, approval_granted=False) -> AutonomyCheckVerdict
    .snapshot() -> tuple[AgentAutonomyDeclaration, ...]
class InvalidAutonomyDeclarationError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存纯函数：check_action 无 IO、同输入必同输出（<1ms 热路径兼容）。
- Fail-Closed：未登记角色按 L0 兜底（REQUIRE_APPROVAL，fail_closed=True）。
- 区上限不可被声明抬升；immutable_core 越级 execute → kill_switch_triggered + violation_hook 回调（hook 异常不阻断判定，留痕降级）。
- 审计记录由 verdict.audit_record() 产出 dict，持久化委托调用方（运行时装配批接 MOD-AU-001/MOD-AU-002 链路）。

## 4. 依赖

- MOD-AU-001 autonomy_boundary_gate（设计边：运行时按级别拦截的消费方）
- MOD-AU-002 kill_switch_orchestrator（设计边：越级 kill_switch 信号的执行方）

## 5. MVP 边界

- 运行时装配（boundary_gate 读取本注册表 / kill_switch_orchestrator 消费信号 /
  Agent Card YAML 持久化）留运行时装配批；本模块只交付级别模型 + 判定核心 +
  审计/熔断信号契约。

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
