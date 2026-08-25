---
blueprint_id: MOD-ORCH-001
module_name: layered_command_chain
domain: D_ORCHESTRATOR
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ORCHESTRATOR
path: src/zephyr/orchestrator/layered_command_chain.py
granularity: file
---

# MOD-ORCH-001 layered_command_chain 蓝图（Agent 分层指挥链：战略→战术→执行）

> **module_id**: MOD-ORCH-001 | **域**: D_ORCHESTRATOR | **优先级**: P1
> **来源**: B11-02451（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-ORCH-001，A7-Agent架构 §0边界声明/§1）
> 代码：`src/zephyr/orchestrator/layered_command_chain.py`

## 0. 定位

军事 C2 式**三层交易指挥链**：战略层（组合/风控目标）→ 战术层
（信号/择时）→ 执行层（订单/路由）**委托协议**（任务包 Schema +
结果上报 Schema）+ 层间通信**强制 A2A 网关** + 指挥链关系入 Agent
注册表 + **越层直连拒绝并告警**。

查重分工（W-P1-25 铁律⑤探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| agent_orchestrator | MOD-INF-039 | 6 角色×10 域 capability 静态评分**路由** | 任务→角色匹配；本件=层级**委托/上报协议**与越层门禁，不做能力评分 |
| autonomy_core/agents 包 | MOD-EXE-AGENTS | 四类 Agent 薄入口（Phase 0 手动/无总线）+ R1 五交易 Agent（researcher/signal_analyst/timing_analyst/t0_trader/risk_manager） | Agent 实体在案；本件=实体间**指挥链关系与协议层**，不新建 Agent |
| a2a_registry / agent_card | MOD-INF-025（L1 发现） | Agent 卡片注册与能力发现 | 本件把指挥链关系（上层→下层委托权）登记为链上元数据，复用其 agent_id 语义，不重建注册表 |
| a2a 网关族（layer3_coordination 等） | D_INFRA_A2A | A2A 协议网关/追踪 | 本件层间通信**强制经注入 a2a_gateway 回调**（DI），不实现协议 |
| reflctrl_gate | D_INTELLIGENCE | 反思频率分层（execution/tactical/strategic） | 反思触发频率；与委托协议零交集 |
| voting_first_multi_agent | D_ORCHESTRATOR | 多 Agent 投票编排 | 同层投票；本件=跨层指挥链 |

TSV 裁定原文："已有治理/业务/算法/自我迭代四类Agent薄入口（Phase 0手动
形态/无总线），但战略-战术-执行三层交易指挥链（层间委托/上报协议）未
建"——施工形态=纯内存协议件，网关/注册表回调全 DI。

## 1. 规则（确定性，纯内存）

- **层级** ChainLayer：STRATEGIC / TACTICAL / EXECUTION；合法委托方向
  仅 STRATEGIC→TACTICAL、TACTICAL→EXECUTION（逐层向下）。
- **指挥链注册表**：`register_link(parent_agent, child_agent)`——
  父层必须恰为子层上一层（越层注册如 STRATEGIC→EXECUTION 直接拒绝
  +告警回调）；同 (parent, child) 幂等；agent 层级经构造注入
  `agent_layers` 映射声明。
- **任务包** TaskPacket（frozen）：packet_id/parent_agent/child_agent/
  objective/constraints(dict)/deadline_ts(可选)/issued_at（注入时钟）。
- **结果上报** ResultReport（frozen）：packet_id/child_agent/status
  （COMPLETED/REJECTED/FAILED）/metrics(dict)/reported_at。
- **委托协议** `delegate(packet)`：
  1. 链路存在性校验（(parent,child) 须在注册表）——越层/未注册直连
     → 拒绝 + `alert_sink` 告警（ChainViolation，含 reason）；
  2. 层间通信强制 A2A 网关——`a2a_gateway` 回调未注入 → Fail-Closed
     （不允许旁路直传）；
  3. 网关回执 ok → 状态 ACCEPTED 留痕（packet 状态机
     ISSUED→ACCEPTED→REPORTED）。
- **上报协议** `report(report)`：packet 须为 ACCEPTED 且 child 匹配；
  状态非法 → Fail-Closed。
- **查询**：`chain_of(agent)` 返回父/子链；`pending_packets(child)` 按
  (issued_at, packet_id) 确定性排序。
- Fail-Closed：空 agent_id/未知 packet/非法状态迁移 →
  CommandChainError；告警不阻断（log+计数）。

## 2. 接口

```python
class ChainLayer(str, Enum): STRATEGIC/TACTICAL/EXECUTION
class PacketStatus(str, Enum): ISSUED/ACCEPTED/REPORTED/REJECTED
class ReportStatus(str, Enum): COMPLETED/REJECTED/FAILED
@dataclass(frozen=True) class TaskPacket: ...
@dataclass(frozen=True) class ResultReport: ...
@dataclass(frozen=True) class ChainViolation: parent_agent/child_agent/reason/raised_at

class LayeredCommandChain:
    __init__(*, agent_layers: Mapping[str, ChainLayer], clock=None, a2a_gateway=None, alert_sink=None)
    register_link(parent_agent, child_agent) -> None
    delegate(packet: TaskPacket) -> PacketStatus
    report(report: ResultReport) -> None
    chain_of(agent_id: str) -> ChainLinks
    pending_packets(child_agent: str) -> list[TaskPacket]
CommandChainError(ZephyrBaseError)  # 占位 ZA-ORCH-UNREGISTERED-COMMAND-CHAIN（纪律⑦）
```

## 3. 依赖

- 设计边：`agent_orchestrator`（node 10626488，能力路由分工）、
  `a2a_registry`（node 10626021，Agent 注册表语义复用）、
  `autonomy_core/agents`（node 10624424，Agent 实体分工）。
- 运行时装配（非本件）：五交易 Agent 层级声明（risk_manager=战略 /
  signal_analyst·timing_analyst=战术 / t0_trader·sor=执行）、真实
  A2A 网关绑定、告警接 alert 路由。

## 4. 测试

`tests/orchestrator/test_layered_command_chain.py`（[TTL] permanent）。
