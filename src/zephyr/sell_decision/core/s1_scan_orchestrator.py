# [BLUEPRINT] MOD-SELL-016 | docs/03_modules/_domain_sell_decision/s1_scan_orchestrator/blueprint.md | §1
# [MODULE] zephyr.sell_decision.core.s1_scan_orchestrator
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.sell_decision.core.sell_signal_collector; zephyr.sell_decision.core.sell_signal_fusion_engine; zephyr.sell_decision.core.sell_urgency_scorer; zephyr.sell_decision.core.position_triage
# [CONSUMERS] TDM-X-S2-01 路由口（f46 卷 S2-01 入口消费方）; 57号文日循环 SOP 槽位/既有 continuous 节拍持有方（事件驱动调用 scan_once）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 事件/槽位驱动 scan_once 无常驻线程(禁 cron/Timer/sleep-loop); 与 P1-02 position_triage 共享单扫描循环(D104, 调用方用同一节拍喂 triage_levels); mode 默认 paper 且 live 需 allow_live 显式解锁(G45-1 先 paper 档); 无信号=诚实空跑(empty_run 如实标记不伪造); 未就绪节点显式跳过留痕不假装消费; 融合输入空=跳过融合(InvalidFusionInputError 契约不硬吃); 18 节点验证态=pending 常量如实披露(不连业务库); S1-06 组合级触发归 X-R1/F47 不重复接线
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] S1ScanError(mode 违规); 单节点/provider 故障隔离为 NodeTrace 不阻断其余节点; sink.deliver 异常隔离计数不中断扫描
# [TESTS] tests/sell_decision/test_s1_scan_orchestrator.py
# [A_module] module_id=MOD-SELL-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
S1 信号扫描编排器（G45-1 治缺口：S1 全族零生产消费 → 立编排接线）。

把 TDM-X-S1 信号族（S1-01 收集/S1-02 止损/S1-03 止盈/S1-04 破位/S1-05 融合/
S1-06 强清绕过）串成**一次可事件触发的扫描**：providers 产信号 → 融合引擎出
willingness → 紧迫度评分 → 结构化信封投递 S2-01 路由口（f46 卷消费方）。

设计真源:
    - docs/_working/fullconnect_campaign/e_decision_chain/09_f45_s1_sell_signal.md
      §四 G45-1（编排工单，挂 continuous 节拍先 paper 档，与 P1-02 共享扫描循环）
    - docs/_working/2026-09-10-xflow-batch-report.md（18 节点验证全 pending 台账
      VAL-20260909-164042——本模块以常量如实披露，不连业务库读取）
    - config/trading_decision_map.yaml TDM-X-S1-01..06（module_ref 真源）

触发方式（宪法 §9.3 永久系统四要素——本模块只做"可被触发的纯编排"）:
    不自带线程/定时器。由既有 continuous 槽位持有方（57号文日循环 SOP/盘口事件
    循环）在节拍上调用 ``scan_once(symbols, triage_levels=...)``；triage_levels
    必须来自与 P1-02 position_triage **同一个扫描循环**（D104 已统一口径），防两
    套 ticker。无调用=不扫描（自动关闭语义由槽位持有方承担）。

诚实性契约（本模块存在的意义——G45-1 病根就是"空转假象"）:
    - 无 providers 注册/无信号 → ``empty_run=True`` 的诚实空跑记录，不伪造信号。
    - 未就绪节点（模块缺失/provider 未注册/触发扫描件未建）→ 逐节点 ``NodeTrace``
      显式跳过留痕，不假装消费。
    - 18 节点验证态 = ``pending``（全族），信封与报告如实携带，不升格。

用法（SOP 槽位侧）::

    from zephyr.sell_decision.core.s1_scan_orchestrator import (
        S1SignalScanOrchestrator, FileOutboxSink,
    )

    orch = S1SignalScanOrchestrator(
        sink=FileOutboxSink("data/runtime/s1_scan_outbox"),  # paper 档路由口
    )
    orch.register_collector_provider("TECHNICAL", my_technical_provider)
    orch.register_node_provider("TDM-X-S1-02", my_stoploss_provider)
    report = orch.scan_once(
        symbols=["000001.SZ"],
        triage_levels={"000001.SZ": "MONITOR"},   # 与 P1-02 同循环产出
    )
    if report.empty_run:
        ...  # 诚实空跑：本轮无信号、无投递

# [ALGO_FLOW] external: docs/03_modules/_domain_sell_decision/algo_flow/s1_scan_orchestrator.yaml
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Final, Protocol

from zephyr.sell_decision.core.sell_signal_collector import (
    SellSignal,
    SellSignalCollector,
)
from zephyr.sell_decision.core.sell_signal_fusion_engine import (
    FusedSellDecision,
    SellSignalFusionEngine,
)
from zephyr.sell_decision.core.sell_urgency_scorer import (
    SellUrgencyScorer,
)

# create-guard-not-dup: 本模块是卖出信号族（TDM-X-S1）的扫描编排接线（G45-1 治缺口件），
# 与命中的 runtime_llm_call_interceptor/yaml_anchor_consistency_scanner/dual_run/apply_depgraph
# 各能力无语义重叠——仅"scan/mode/node spec"等通用词字面撞车，非第二真源。
__all__: Final[list[str]] = [
    "S1ScanError",
    "S1ScanMode",
    "NodeReadiness",
    "NodeTrace",
    "S1RouteEnvelope",
    "S1ScanReport",
    "S2RouteSink",
    "InMemorySink",
    "FileOutboxSink",
    "S1_NODE_SPECS",
    "XFLOW_VALIDATION_STATE",
    "S1SignalScanOrchestrator",
]

_OUTBOX_SCHEMA_VERSION = "TDM-X-S2-01_INBOX/v1"

# 18 节点验证态真源=VAL-20260909-164042 台账（2026-09-10 X 流验证批，全 pending）。
# 刻意不连业务库读取（宪法 §9.1 数据红线）：常量披露 + 指针，验证态流转由验证批
# runner 落台账，本模块消费时如实携带，不升格不猜测。
XFLOW_VALIDATION_STATE = "pending"

_S1_FUSION_URGENCY_BYPASS_FLOOR = 1.0


class S1ScanError(Exception):
    """扫描编排违规（如 live 档未解锁）。"""


class S1ScanMode(str, Enum):
    """扫描档位——G45-1 处方：先 paper 档（3-5 天）再评 live。"""

    PAPER = "paper"
    LIVE = "live"


@dataclass(frozen=True)
class _NodeSpec:
    """S1 族节点规格（module_ref 真源=TDM yaml，勿手改；重对齐时随地图更新）。"""

    node_id: str
    name: str
    module_ref: str
    kind: str  # collector / strategy / fusion / bypass


@dataclass(frozen=True)
class _ScanRound:
    """单轮扫描上下文束（参数对象——替代长参数表，§5.150）。"""

    scan_id: str
    symbols: tuple[str, ...]
    now: datetime
    context: dict[str, Any]
    triage_levels: dict[str, str]


@dataclass(frozen=True)
class _EnvelopeCore:
    """信封核心字段束（参数对象——替代长参数表，§5.150）。"""

    scan_id: str
    node_id: str
    symbol: str
    willingness: float
    urgency: float
    strategy: str
    reason: str


S1_NODE_SPECS: tuple[_NodeSpec, ...] = (
    _NodeSpec(
        "TDM-X-S1-01", "信号收集与六桶分类", "src/zephyr/sell_decision/core/sell_signal_collector.py", "collector"
    ),
    _NodeSpec("TDM-X-S1-02", "止损族判定", "src/zephyr/sell_decision/core/stop_loss_strategy.py", "strategy"),
    _NodeSpec("TDM-X-S1-03", "止盈族判定", "src/zephyr/sell_decision/core/take_profit_strategy.py", "strategy"),
    _NodeSpec(
        "TDM-X-S1-04", "破位与情绪退潮信号", "src/zephyr/sell_decision/core/breakout_failure_detector.py", "strategy"
    ),
    _NodeSpec(
        "TDM-X-S1-05", "信号融合与紧迫度评分", "src/zephyr/sell_decision/core/sell_signal_fusion_engine.py", "fusion"
    ),
    _NodeSpec("TDM-X-S1-06", "强制清仓绕过通道", "src/zephyr/trading/strategy_abnormal_exit_orchestrator.py", "bypass"),
)

NodeProvider = Callable[[str, datetime, dict[str, Any] | None], "list[SellSignal]"]
BypassTrigger = Callable[[str, datetime, dict[str, Any] | None], "bool | dict[str, Any] | None"]


@dataclass(frozen=True)
class NodeReadiness:
    """单节点就绪面——接线判定+跳过理由的机生事实。"""

    node_id: str
    module_ref: str
    code_ready: bool  # module_ref 在盘可导入
    validation_state: str  # X 流 18 节点台账态（当前全 pending）
    wired: bool  # 本编排器本轮是否消费该节点
    detail: str  # 未接线原因/接线方式说明（诚实留痕）

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "module_ref": self.module_ref,
            "code_ready": self.code_ready,
            "validation_state": self.validation_state,
            "wired": self.wired,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class NodeTrace:
    """单节点本轮扫描留痕（wired 或显式跳过）。"""

    node_id: str
    status: str  # "wired" | "skipped"
    detail: str
    signal_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "status": self.status,
            "detail": self.detail,
            "signal_count": self.signal_count,
        }


@dataclass(frozen=True)
class S1RouteEnvelope:
    """S2-01 路由口投递信封（f46 卷消费契约，schema v1）。"""

    schema_version: str
    scan_id: str
    node_id: str  # 产信号节点（TDM-X-S1-05 融合 / TDM-X-S1-06 绕过）
    symbol: str
    mode: str  # paper / live
    willingness: float  # S1-05 融合意愿 [0,1]；绕过通道=1.0
    urgency: float  # S1-05 评分紧迫度 [0,1]；绕过通道=1.0
    execution_strategy: str  # MARKET_FAST / LIMITED_TIME / PATIENT_LIMIT / BYPASS_FORCE
    validation_state: str  # 18 节点台账态（当前 pending，如实携带）
    reason: str
    dominant_signal_type: str
    contributing_signal_count: int
    created_at: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scan_id": self.scan_id,
            "node_id": self.node_id,
            "symbol": self.symbol,
            "mode": self.mode,
            "willingness": self.willingness,
            "urgency": self.urgency,
            "execution_strategy": self.execution_strategy,
            "validation_state": self.validation_state,
            "reason": self.reason,
            "dominant_signal_type": self.dominant_signal_type,
            "contributing_signal_count": self.contributing_signal_count,
            "created_at": self.created_at,
            "payload": dict(self.payload),
        }


class S2RouteSink(Protocol):
    """S2-01 路由口协议——f46 卷落 S2-01 执行器后替换实现即可，编排器零改动。"""

    def deliver(self, envelope: S1RouteEnvelope) -> bool: ...


class InMemorySink:
    """内存收集 sink（默认；测试/影子观察用，不落盘）。"""

    def __init__(self) -> None:
        self.envelopes: list[S1RouteEnvelope] = []

    def deliver(self, envelope: S1RouteEnvelope) -> bool:
        self.envelopes.append(envelope)
        return True


class FileOutboxSink:
    """文件 outbox sink——paper 档 S2-01 路由口的缺省交接面（JSONL append-only）。

    落点默认 ``data/runtime/s1_scan_outbox/``（业务运行时区，非 .runtime 根）；
    f46 卷的 S2-01 消费方按 schema_version 逐行读即可。目录/文件不存在时惰性创建。
    """

    def __init__(self, outbox_dir: str | Path, file_name: str = "s2_route_inbox.jsonl") -> None:
        self._dir = Path(outbox_dir)
        self._file = self._dir / file_name

    @property
    def path(self) -> Path:
        return self._file

    def deliver(self, envelope: S1RouteEnvelope) -> bool:
        self._dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps(envelope.to_dict(), ensure_ascii=False)
        with open(self._file, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return True


@dataclass(frozen=True)
class S1ScanReport:
    """单次扫描报告——空跑/跳过/投递全留痕（"结论必须能翻到过程"）。"""

    scan_id: str
    mode: str
    now: str
    symbols: tuple[str, ...]
    node_traces: tuple[NodeTrace, ...]
    signal_count: int
    fused_count: int
    delivered_count: int
    empty_run: bool
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "mode": self.mode,
            "now": self.now,
            "symbols": list(self.symbols),
            "node_traces": [t.to_dict() for t in self.node_traces],
            "signal_count": self.signal_count,
            "fused_count": self.fused_count,
            "delivered_count": self.delivered_count,
            "empty_run": self.empty_run,
            "notes": self.notes,
        }


class S1SignalScanOrchestrator:
    """S1 信号扫描编排器——一次 scan_once 串 S1 族→融合→紧迫度→S2-01 投递。

    无常驻循环：由既有槽位/事件触发方调用 ``scan_once``；triage_levels 由调用方
    从与 P1-02 共享的同一扫描循环传入（D104 单循环铁律）。
    """

    def __init__(
        self,
        *,
        mode: S1ScanMode | str = S1ScanMode.PAPER,
        collector: SellSignalCollector | None = None,
        fusion_engine: SellSignalFusionEngine | None = None,
        urgency_scorer: SellUrgencyScorer | None = None,
        sink: S2RouteSink | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._mode = S1ScanMode(mode)
        self._collector = collector or SellSignalCollector()
        self._fusion = fusion_engine or SellSignalFusionEngine()
        self._scorer = urgency_scorer or SellUrgencyScorer()
        self._sink: S2RouteSink = sink if sink is not None else InMemorySink()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._node_providers: dict[str, NodeProvider] = {}
        self._bypass_triggers: dict[str, BypassTrigger] = {}
        self._readiness_cache: dict[str, NodeReadiness] | None = None
        if self._mode is S1ScanMode.LIVE:
            raise S1ScanError(
                "live 档禁止在构造时启用——G45-1 先 paper 档；live 须 scan_once(allow_live=True) 显式单次解锁"
            )

    # ── 接线面 ──

    @property
    def mode(self) -> S1ScanMode:
        return self._mode

    @property
    def collector(self) -> SellSignalCollector:
        """S1-01 收集器本体——provider 注册走 collector.register(signal_type, p)。"""
        return self._collector

    @property
    def sink(self) -> S2RouteSink:
        return self._sink

    def register_node_provider(self, node_id: str, provider: NodeProvider) -> None:
        """按 TDM 节点 id 接判定族信号源（S1-02/03/04…）。

        Args:
            node_id: TDM-X-S1-0N（须在 S1_NODE_SPECS 内）。
            provider: (symbol, now, context) -> list[SellSignal]。

        Raises:
            S1ScanError: node_id 不在 S1 族规格内。
        """
        if node_id not in {s.node_id for s in S1_NODE_SPECS}:
            raise S1ScanError(f"未知 S1 节点: {node_id}（真源=S1_NODE_SPECS/TDM 地图）")
        self._node_providers[node_id] = provider
        self._readiness_cache = None

    def register_bypass_trigger(self, name: str, trigger: BypassTrigger) -> None:
        """接 S1-06 强清绕过触发源（黑天鹅/K≥3/主力弃庄扫描件建成后再注册）。

        注意分工红线：KillSwitch **组合级**触发归 X-R1/F47 既有横切线，勿在此重复
        接线（09_f45 案卷 §三 勘误 3）；本接口只收单仓强清触发。
        """
        self._bypass_triggers[name] = trigger
        self._readiness_cache = None

    # ── 就绪面 ──

    def readiness(self, *, refresh: bool = False) -> dict[str, NodeReadiness]:
        """六节点就绪面盘点（机生，勿手抄）。

        判定口径：
            code_ready = module_ref 文件在盘（importlib.util.spec_from_file_location）。
            wired = 结构位（collector/fusion 本体常在）或本轮已注册 provider/触发源。
            validation_state = XFLOW_VALIDATION_STATE（18 节点台账全 pending，如实披露）。
        """
        if self._readiness_cache is not None and not refresh:
            return dict(self._readiness_cache)
        out: dict[str, NodeReadiness] = {}
        for spec in S1_NODE_SPECS:
            code_ready = self._module_on_disk(spec.module_ref)
            if spec.kind == "collector":
                wired, detail = (
                    True,
                    "本体常驻；信号源经 collector.register 接入（当前注册=%d 类）"
                    % len(self._collector.registered_types),
                )
            elif spec.kind == "fusion":
                wired, detail = True, "本体常驻；输入=上游节点信号，空输入诚实跳过"
            elif spec.kind == "strategy":
                if spec.node_id in self._node_providers:
                    wired, detail = True, "provider 已注册"
                else:
                    wired, detail = False, "provider 未注册——显式跳过（判定库在盘，等待信号源接线）"
            else:  # bypass
                if self._bypass_triggers:
                    wired, detail = True, f"绕过触发源已注册 {sorted(self._bypass_triggers)}"
                else:
                    wired, detail = (
                        False,
                        (
                            "触发扫描件未建（黑天鹅/K≥3/主力弃庄）——显式跳过；"
                            "KillSwitch 组合级归 X-R1/F47 不在本节点重复接线"
                        ),
                    )
            out[spec.node_id] = NodeReadiness(
                node_id=spec.node_id,
                module_ref=spec.module_ref,
                code_ready=code_ready,
                validation_state=XFLOW_VALIDATION_STATE,
                wired=wired,
                detail=detail,
            )
        self._readiness_cache = out
        return dict(out)

    @staticmethod
    def _module_on_disk(module_ref: str) -> bool:
        return (Path(module_ref)).is_file()

    # ── 扫描主入口 ──

    def scan_once(
        self,
        symbols: list[str],
        *,
        now: datetime | None = None,
        context: dict[str, Any] | None = None,
        triage_levels: dict[str, str] | None = None,
        allow_live: bool = False,
    ) -> S1ScanReport:
        """执行一次扫描（事件/槽位触发，无常驻循环）。

        Args:
            symbols: 本轮扫描标的（必填，可空列表=诚实空跑）。
            now: 扫描时间（默认 clock()）。
            context: 透传给各 provider 的上下文。
            triage_levels: 与 P1-02 position_triage 共享循环产出的分级
                （WATCH/MONITOR/HOLD）——只随信封留痕，不改变本轮判定（节拍调度
                责任在槽位持有方）。
            allow_live: live 档单次显式解锁（G45-1 处方默认 paper，勿轻开）。

        Returns:
            S1ScanReport（含逐节点 trace；空跑 empty_run=True）。

        Raises:
            S1ScanError: mode=LIVE 且 allow_live=False。
        """
        self._ensure_mode_unlocked(allow_live)
        now = now or self._clock()
        round_ = _ScanRound(
            scan_id=uuid.uuid4().hex[:12],
            symbols=tuple(symbols or []),
            now=now,
            context=context or {},
            triage_levels=triage_levels or {},
        )
        traces: list[NodeTrace] = []
        readies = self.readiness()

        signals = self._collect_signals(round_, readies, traces)
        envelopes = self._scan_bypass(round_, readies, traces)
        fused, urgency_by_symbol = self._fuse_and_score(signals, now, traces)
        envelopes.extend(self._build_fused_envelopes(fused, urgency_by_symbol, round_))
        delivered = self._deliver_all(envelopes, traces)

        return self._build_report(round_, traces, signals, fused, envelopes, delivered)

    def _ensure_mode_unlocked(self, allow_live: bool) -> None:
        """live 档单次显式解锁闸（G45-1 处方：先 paper 档；paper 档无需解锁）。"""
        if self._mode is S1ScanMode.LIVE and not allow_live:
            raise S1ScanError("live 档未解锁——G45-1 处方先 paper 档，live 须单次 allow_live=True")

    def _collect_signals(
        self,
        round_: _ScanRound,
        readies: dict[str, NodeReadiness],
        traces: list[NodeTrace],
    ) -> list[SellSignal]:
        """S1-01 收集 + S1-02/03/04 判定族（未注册显式跳过，故障隔离）。"""
        signals: list[SellSignal] = []
        n01 = readies["TDM-X-S1-01"]
        if n01.wired and self._collector.registered_types:
            for symbol in round_.symbols:
                signals.extend(self._collector.collect(symbol, now=round_.now, context=round_.context))
            traces.append(
                NodeTrace(
                    "TDM-X-S1-01",
                    "wired",
                    f"收集 {len(signals)} 条（注册类型={self._collector.registered_types}）",
                    len(signals),
                )
            )
        else:
            traces.append(NodeTrace("TDM-X-S1-01", "skipped", "collector 无注册 provider——诚实空收集（不伪造信号）", 0))
        for spec in S1_NODE_SPECS:
            if spec.kind == "strategy":
                signals.extend(self._collect_strategy_node(spec, round_, traces))
        return signals

    def _collect_strategy_node(
        self,
        spec: _NodeSpec,
        round_: _ScanRound,
        traces: list[NodeTrace],
    ) -> list[SellSignal]:
        provider = self._node_providers.get(spec.node_id)
        if provider is None:
            traces.append(NodeTrace(spec.node_id, "skipped", "provider 未注册——显式跳过（不假装消费）", 0))
            return []
        got: list[SellSignal] = []
        try:
            for symbol in round_.symbols:
                got.extend(provider(symbol, round_.now, round_.context) or [])
        except Exception as exc:  # noqa: BLE001 — 单节点故障隔离（同 collector 隔离契约）
            traces.append(NodeTrace(spec.node_id, "skipped", f"provider 故障隔离: {exc!r}", 0))
            return []
        traces.append(NodeTrace(spec.node_id, "wired", f"产出 {len(got)} 条", len(got)))
        return got

    def _scan_bypass(
        self,
        round_: _ScanRound,
        readies: dict[str, NodeReadiness],
        traces: list[NodeTrace],
    ) -> list[S1RouteEnvelope]:
        """S1-06 绕过通道（触发=urgency 1.0 直送不经过融合；未接线显式跳过）。"""
        envelopes: list[S1RouteEnvelope] = []
        n06 = readies["TDM-X-S1-06"]
        if not n06.wired:
            traces.append(NodeTrace("TDM-X-S1-06", "skipped", n06.detail, 0))
            return envelopes
        for name, trigger in self._bypass_triggers.items():
            envelopes.extend(self._probe_bypass_trigger(name, trigger, round_, traces))
        traces.append(
            NodeTrace(
                "TDM-X-S1-06",
                "wired",
                f"触发源 {sorted(self._bypass_triggers)} 已扫，命中 {len(envelopes)} 笔",
                len(envelopes),
            )
        )
        return envelopes

    def _probe_bypass_trigger(
        self,
        name: str,
        trigger: BypassTrigger,
        round_: _ScanRound,
        traces: list[NodeTrace],
    ) -> list[S1RouteEnvelope]:
        out: list[S1RouteEnvelope] = []
        for symbol in round_.symbols:
            try:
                hit = trigger(symbol, round_.now, round_.context)
            except Exception as exc:  # noqa: BLE001 — 触发源故障隔离
                traces.append(NodeTrace("TDM-X-S1-06", "skipped", f"触发源 {name} 故障隔离: {exc!r}", 0))
                continue
            if hit:
                out.append(
                    self._to_envelope(
                        _EnvelopeCore(
                            scan_id=round_.scan_id,
                            node_id="TDM-X-S1-06",
                            symbol=symbol,
                            willingness=_S1_FUSION_URGENCY_BYPASS_FLOOR,
                            urgency=_S1_FUSION_URGENCY_BYPASS_FLOOR,
                            strategy="BYPASS_FORCE",
                            reason=f"S1-06 绕过通道触发（{name}）——资金安全>一切优化，直送 S2-01",
                        ),
                        dominant="BYPASS",
                        contributing=0,
                        now=round_.now,
                        payload={"trigger": name, "triage": round_.triage_levels.get(symbol, "")},
                    )
                )
        return out

    def _fuse_and_score(
        self,
        signals: list[SellSignal],
        now: datetime,
        traces: list[NodeTrace],
    ) -> tuple[list[FusedSellDecision], dict[str, Any]]:
        """S1-05 融合+紧迫度（空输入诚实跳过——InvalidFusionInputError 契约不硬吃）。"""
        if not signals:
            traces.append(NodeTrace("TDM-X-S1-05", "skipped", "输入空——诚实跳过融合（不伪造决策）", 0))
            return [], {}
        fused = self._fusion.fuse(signals, now=now)
        traces.append(NodeTrace("TDM-X-S1-05", "wired", f"融合 {len(fused)} 标的决策", len(fused)))
        urgency_by_symbol: dict[str, Any] = self._score_urgency(signals, traces)
        return fused, urgency_by_symbol

    def _score_urgency(self, signals: list[SellSignal], traces: list[NodeTrace]) -> dict[str, Any]:
        try:
            return {score.symbol: score for score in self._scorer.score(sell_signals=signals)}
        except Exception as exc:  # noqa: BLE001 — 评分故障隔离：融合结果仍可投递（urgency 缺省 willingness）
            traces.append(NodeTrace("TDM-X-S1-05", "skipped", f"紧迫度评分故障隔离（融合结果按意愿投递）: {exc!r}", 0))
            return {}

    def _build_fused_envelopes(
        self,
        fused: list[FusedSellDecision],
        urgency_by_symbol: dict[str, Any],
        round_: _ScanRound,
    ) -> list[S1RouteEnvelope]:
        envelopes: list[S1RouteEnvelope] = []
        for decision in fused:
            score = urgency_by_symbol.get(decision.symbol)
            envelopes.append(
                self._to_envelope(
                    _EnvelopeCore(
                        scan_id=round_.scan_id,
                        node_id="TDM-X-S1-05",
                        symbol=decision.symbol,
                        willingness=decision.willingness,
                        urgency=score.urgency if score is not None else decision.willingness,
                        strategy=score.strategy.value if score is not None else "PATIENT_LIMIT",
                        reason=decision.reason,
                    ),
                    dominant=decision.dominant_signal_type.value,
                    contributing=len(decision.contributing_signals),
                    now=round_.now,
                    payload={
                        "triage": round_.triage_levels.get(decision.symbol, ""),
                        "consistency": decision.consistency.value,
                    },
                )
            )
        return envelopes

    def _deliver_all(self, envelopes: list[S1RouteEnvelope], traces: list[NodeTrace]) -> int:
        delivered = 0
        for env in envelopes:
            try:
                if self._sink.deliver(env):
                    delivered += 1
            except Exception as exc:  # noqa: BLE001 — sink 故障不中断扫描，计数留痕
                traces.append(NodeTrace("S2-ROUTE", "skipped", f"sink 投递故障隔离: {exc!r}", 0))
        return delivered

    def _build_report(
        self,
        round_: _ScanRound,
        traces: list[NodeTrace],
        signals: list[SellSignal],
        fused: list[FusedSellDecision],
        envelopes: list[S1RouteEnvelope],
        delivered: int,
    ) -> S1ScanReport:
        empty_run = not signals and not envelopes
        notes = (
            "诚实空跑：本轮零信号零投递（18 节点验证态=pending 如实携带）"
            if empty_run
            else f"投递 {delivered}/{len(envelopes)} 信封至 S2-01 路由口（mode={self._mode.value}）"
        )
        return S1ScanReport(
            scan_id=round_.scan_id,
            mode=self._mode.value,
            now=round_.now.isoformat(),
            symbols=round_.symbols,
            node_traces=tuple(traces),
            signal_count=len(signals),
            fused_count=len(fused),
            delivered_count=delivered,
            empty_run=empty_run,
            notes=notes,
        )

    # ── 信封工厂 ──

    def _to_envelope(
        self,
        core: _EnvelopeCore,
        *,
        dominant: str,
        contributing: int,
        now: datetime,
        payload: dict[str, Any],
    ) -> S1RouteEnvelope:
        return S1RouteEnvelope(
            schema_version=_OUTBOX_SCHEMA_VERSION,
            scan_id=core.scan_id,
            node_id=core.node_id,
            symbol=core.symbol,
            mode=self._mode.value,
            willingness=round(float(core.willingness), 4),
            urgency=round(float(core.urgency), 4),
            execution_strategy=core.strategy,
            validation_state=XFLOW_VALIDATION_STATE,
            reason=core.reason,
            dominant_signal_type=dominant,
            contributing_signal_count=contributing,
            created_at=now.astimezone(timezone.utc).isoformat(),
            payload=payload,
        )


if __name__ == "__main__":  # ORPHAN-MODULE 入口豁免面——SOP 槽位/人工纸档触发口
    import argparse

    parser = argparse.ArgumentParser(description="S1 信号扫描编排器手动单次触发（paper 档）")
    parser.add_argument("--symbols", required=True, help="逗号分隔标的，如 000001.SZ,600000.SH")
    parser.add_argument("--outbox", default="data/runtime/s1_scan_outbox", help="S2-01 路由口 outbox 目录")
    args = parser.parse_args()
    _report = S1SignalScanOrchestrator(sink=FileOutboxSink(args.outbox)).scan_once(
        [s.strip() for s in args.symbols.split(",") if s.strip()]
    )
    print(_report.to_dict())
