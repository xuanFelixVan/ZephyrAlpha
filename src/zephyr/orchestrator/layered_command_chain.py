# [BLUEPRINT] MOD-ORCH-001 | docs/03_modules/_domain_orchestrator/layered_command_chain/blueprint.md
# [MODULE] zephyr.orchestrator.layered_command_chain
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] 无（协议核心纯内存；a2a_gateway/alert_sink/clock/agent_layers 全注入）
# [CONSUMERS] 运行时装配批（五交易 Agent 层级声明 / 真实 A2A 网关绑定 / 告警接 alert 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层级词表闭合(strategic|tactical|execution); 合法委托仅逐层向下(战略→战术→执行); 越层注册/越层直连拒绝+告警留痕; 层间通信强制 A2A 网关(未注入 Fail-Closed 不旁路); packet 状态机 ISSUED→ACCEPTED→REPORTED; 上报须受托 child 本人; pending 按 (issued_at,packet_id) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_orchestrator/layered_command_chain/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CommandChainError(占位 ZA-ORCH-UNREGISTERED-COMMAND-CHAIN)——未知agent/越层注册/空packet_id/网关缺失/未知packet/非法状态迁移时抛
# [TESTS] tests/orchestrator/test_layered_command_chain.py
# [A_module] module_id=MOD-ORCH-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
LayeredCommandChain — Agent 分层指挥链（MOD-ORCH-001）。

B11-02451（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-ORCH-001，A7-Agent架构
§0边界声明/§1）：军事 C2 式**三层交易指挥链**——战略层（组合/风控目标）
→ 战术层（信号/择时）→ 执行层（订单/路由）**委托协议**（任务包 Schema +
结果上报 Schema）+ 层间通信**强制 A2A 网关** + 指挥链关系入 Agent 注册表
+ **越层直连拒绝并告警**。

查重分工（蓝图 §0）：agent_orchestrator=6角色×10域能力评分路由（本件不做
能力评分）；autonomy_core/agents=Agent 实体薄入口（本件=实体间指挥链关系
与协议层，不新建 Agent）；a2a_registry=L1 卡片发现（复用 agent_id 语义，
不重建注册表）；A2A 网关族=协议实现（本件强制经注入网关回调，不实现协
议）；reflctrl_gate=反思频率分层（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: agent_layers 参数
#   fields: 参数 agent_layers（无注解）
#   code: layered_command_chain.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: layered_command_chain.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: a2a_gateway 参数
#   fields: 参数 a2a_gateway（无注解）
#   code: layered_command_chain.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: layered_command_chain.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LayeredCommandChain
#   name_en: LayeredCommandChain
#   intro: 三层指挥链协议件（注册表 + 委托 + 上报 + 越层门禁）。
#   desc: 三层指挥链协议件（注册表 + 委托 + 上报 + 越层门禁）。；公共方法（定义序）: register_link, delegate, report, packet_status, chain_of, pending_…
#   inputs: agent_layers clock a2a_gateway alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: LayeredCommandChain
#   downstream: 运行时装配批（五交易 Agent 层级声明 / 真实 A2A 网关绑定 / 告警接 alert 路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChainLayer",
    "ChainLinks",
    "ChainViolation",
    "CommandChainError",
    "LayeredCommandChain",
    "PacketStatus",
    "ReportStatus",
    "ResultReport",
    "TaskPacket",
]

#: 层级序号（委托方向只能序号 +1 逐层向下）
_LAYER_RANK: Final[dict[ChainLayer, int]] = {}


class CommandChainError(Exception):
    """指挥链协议输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ORCH-UNREGISTERED-COMMAND-CHAIN。
    """


class ChainLayer(str, Enum):
    """指挥链层级（词表闭合）。"""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    EXECUTION = "execution"


_LAYER_RANK.update(
    {
        ChainLayer.STRATEGIC: 0,
        ChainLayer.TACTICAL: 1,
        ChainLayer.EXECUTION: 2,
    }
)


class PacketStatus(str, Enum):
    """任务包状态机。"""

    ISSUED = "issued"
    ACCEPTED = "accepted"
    REPORTED = "reported"
    REJECTED = "rejected"


class ReportStatus(str, Enum):
    """结果上报状态。"""

    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass(frozen=True)
class TaskPacket:
    """任务包 Schema（上层→下层委托载体，frozen）。"""

    packet_id: str
    parent_agent: str
    child_agent: str
    objective: str
    constraints: dict
    deadline_ts: datetime.datetime | None
    issued_at: datetime.datetime


@dataclass(frozen=True)
class ResultReport:
    """结果上报 Schema（下层→上层回执载体，frozen）。"""

    packet_id: str
    child_agent: str
    status: ReportStatus
    metrics: dict
    reported_at: datetime.datetime


@dataclass(frozen=True)
class ChainViolation:
    """越层/未注册直连违规（告警载荷）。"""

    parent_agent: str
    child_agent: str
    reason: str
    raised_at: datetime.datetime


@dataclass(frozen=True)
class ChainLinks:
    """单 Agent 的父/子链视图（确定性排序）。"""

    parents: tuple[str, ...]
    children: tuple[str, ...]


class LayeredCommandChain:
    """三层指挥链协议件（注册表 + 委托 + 上报 + 越层门禁）。"""

    def __init__(
        self,
        *,
        agent_layers: Mapping[str, ChainLayer],
        clock: Callable[[], datetime.datetime] | None = None,
        a2a_gateway: Callable[[TaskPacket], bool] | None = None,
        alert_sink: Callable[[ChainViolation], None] | None = None,
    ) -> None:
        if not agent_layers:
            raise CommandChainError("agent_layers 为空（无 Agent 层级声明）")
        for agent_id, layer in agent_layers.items():
            if not agent_id:
                raise CommandChainError("agent_id 为空")
            if not isinstance(layer, ChainLayer):
                raise CommandChainError(f"非法层级: {layer!r}")
        self._layers: dict[str, ChainLayer] = dict(agent_layers)
        self._clock = clock or datetime.datetime.now
        self._gateway = a2a_gateway
        self._alert_sink = alert_sink
        self._links: set[tuple[str, str]] = set()
        self._packets: dict[str, tuple[TaskPacket, PacketStatus]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, parent: str, child: str, reason: str) -> None:
        violation = ChainViolation(parent_agent=parent, child_agent=child, reason=reason, raised_at=self._clock())
        _log.warning("指挥链违规: %s -> %s (%s)", parent, child, reason)
        if self._alert_sink is not None:
            try:
                self._alert_sink(violation)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _layer_of(self, agent_id: str) -> ChainLayer:
        layer = self._layers.get(agent_id)
        if layer is None:
            raise CommandChainError(f"未知 agent: {agent_id!r}（未在层级声明中）")
        return layer

    # ── 指挥链注册 ────────────────────────────────────────────────────────

    def register_link(self, parent_agent: str, child_agent: str) -> None:
        """登记委托链：父层须恰为子层上一层；越层/逆向 → 拒绝+告警。"""
        parent_layer = self._layer_of(parent_agent)
        child_layer = self._layer_of(child_agent)
        if parent_agent == child_agent:
            raise CommandChainError(f"自链非法: {parent_agent!r}")
        if _LAYER_RANK[parent_layer] != _LAYER_RANK[child_layer] - 1:
            reason = (
                f"越层/逆向注册拒绝: {parent_agent}({parent_layer.value}) -> "
                f"{child_agent}({child_layer.value})，合法仅逐层向下"
            )
            self._alert(parent_agent, child_agent, reason)
            raise CommandChainError(reason)
        self._links.add((parent_agent, child_agent))  # set 幂等

    # ── 委托协议 ──────────────────────────────────────────────────────────

    def delegate(self, packet: TaskPacket) -> PacketStatus:
        """委托：链路校验（越层/未注册→REJECTED+告警）→ 强制 A2A 网关传递。"""
        if not packet.packet_id:
            raise CommandChainError("packet_id 为空")
        if packet.packet_id in self._packets:
            raise CommandChainError(f"packet_id 重复: {packet.packet_id!r}")
        parent_layer = self._layer_of(packet.parent_agent)
        child_layer = self._layer_of(packet.child_agent)
        self._packets[packet.packet_id] = (packet, PacketStatus.ISSUED)

        if (packet.parent_agent, packet.child_agent) not in self._links:
            reason = (
                f"越层/未注册直连拒绝: {packet.parent_agent}({parent_layer.value}) -> "
                f"{packet.child_agent}({child_layer.value}) 链路未登记"
            )
            self._alert(packet.parent_agent, packet.child_agent, reason)
            self._packets[packet.packet_id] = (packet, PacketStatus.REJECTED)
            return PacketStatus.REJECTED

        if self._gateway is None:
            # 层间通信强制 A2A 网关：未注入 Fail-Closed，不允许旁路直传
            del self._packets[packet.packet_id]
            raise CommandChainError("a2a_gateway 未注入（层间通信强制 A2A 网关，禁止旁路）")

        try:
            ok = bool(self._gateway(packet))
        except Exception:  # noqa: BLE001 — 网关异常按 NACK 处理不抛
            _log.exception("a2a_gateway 传递异常: %s", packet.packet_id)
            ok = False
        status = PacketStatus.ACCEPTED if ok else PacketStatus.REJECTED
        self._packets[packet.packet_id] = (packet, status)
        return status

    # ── 上报协议 ──────────────────────────────────────────────────────────

    def report(self, report: ResultReport) -> None:
        """上报：packet 须 ACCEPTED 且 child 为受托方本人 → REPORTED。"""
        entry = self._packets.get(report.packet_id)
        if entry is None:
            raise CommandChainError(f"未知 packet: {report.packet_id!r}")
        packet, status = entry
        if status is not PacketStatus.ACCEPTED:
            raise CommandChainError(
                f"非法状态迁移: packet {report.packet_id!r} 当前 {status.value}，须 ACCEPTED 方可上报"
            )
        if report.child_agent != packet.child_agent:
            raise CommandChainError(f"上报方不符: {report.child_agent!r} 非受托方 {packet.child_agent!r}")
        self._packets[report.packet_id] = (packet, PacketStatus.REPORTED)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def packet_status(self, packet_id: str) -> PacketStatus:
        """单 packet 状态查询（未知 → Fail-Closed）。"""
        entry = self._packets.get(packet_id)
        if entry is None:
            raise CommandChainError(f"未知 packet: {packet_id!r}")
        return entry[1]

    def chain_of(self, agent_id: str) -> ChainLinks:
        """父/子链视图（确定性排序）。"""
        self._layer_of(agent_id)
        parents = tuple(sorted(p for p, c in self._links if c == agent_id))
        children = tuple(sorted(c for p, c in self._links if p == agent_id))
        return ChainLinks(parents=parents, children=children)

    def pending_packets(self, child_agent: str) -> list[TaskPacket]:
        """受托方待办 packet（ACCEPTED 未上报；按 (issued_at, packet_id) 排序）。"""
        self._layer_of(child_agent)
        out = [
            pkt
            for pkt, status in self._packets.values()
            if pkt.child_agent == child_agent and status is PacketStatus.ACCEPTED
        ]
        out.sort(key=lambda p: (p.issued_at, p.packet_id))
        return out
