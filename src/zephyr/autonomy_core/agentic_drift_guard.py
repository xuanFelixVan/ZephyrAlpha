# [BLUEPRINT] MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.1/S1.2
# [MODULE] zephyr.autonomy_core.agentic_drift_guard
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.ai_behavior_baseline（S1.1 基线口径复用，BM-RC-04-F）
# [CONSUMERS] tests/autonomy_core/test_agentic_drift_guard.py；S0.2 gate 链路（内联挂点预留）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数核无副作用（check_operation_chain/evaluate_dual_dimension 不触 IO）; 小样本不判（窗口 <min_ops 不熵判）; DETECTED 必 blocked+P0 告警事件; 落盘 IO 失败不阻断判定; 错误/原因消息禁含 session_id
# [MODIFY-GUARD] Owner approval required; 参数口径变更须同步 RBAC 蓝图决策 D-018-21 与 15号文 §4.2
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftGuardError（裸异常——ZA-AU 前缀未在 error_code_registry 声明，沿域先例 MOD-AU-002 同款，禁自创前缀）; AgenticDriftGuard.inspect() 永不抛异常，IO 失败仅 logger.warning
# [TESTS] tests/autonomy_core/test_agentic_drift_guard.py
# [A_module] module_id=MOD-AU-003 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
# [ALGO_FLOW]
# I1: Sequence[ChainOperation]（op_type/path）；I2: confidence×intent_deviation；I3: 历史 SessionBehavior 序列
# F1: S1.2 内联漂移检查——10 步滑窗内类型熵>1.5 且类型偏离率>drift_tolerance → WARNING(auto_guard)；路径熵>2.0 且路径偏离率>drift_tolerance → DETECTED(blocked+P0)
# F2: 双维度 Hard-Gate——置信度<0.3 × 意图偏差>0.3 双坏 → DETECTED(blocked)；单维异常 → WARNING(auto_guard)
# F3: S1.1 行为基线——委托 ai_behavior_baseline（compute_baseline/detect_anomalies，BM-RC-04-F 口径）
# F4: Challenge 工单——字段=原始任务意图复述+动作链对齐说明+检测器证据；degraded=True → degraded_human_review
# O1: DriftVerdict（level/blocked/auto_guard/熵值/证据）；O2: 16号文统一事件 schema jsonl（audit + P0 alerts）；O3: challenge-<id>.json 工单
# [/ALGO_FLOW]
"""



AgenticDriftGuard — Agentic Drift 防护实时档（MOD-AU-003，15号文 §4.2 S1.1/S1.2）.

设计真源：15号文（15_autonomy_boundary_risk.md）§3.2 / §4.2 + RBAC 蓝图决策 D-018-21：
- S1.1 行为基线：复用 governance.lifecycle_governance.ai_behavior_baseline（61 号备忘
  BM-RC-04-F 口径）——会话操作频率（commits/hour）与触碰模块集合基线，z-score 偏离 +
  首次触碰基线外模块双规则；基线投毒防护挂既有 gov_drift/baseline_poisoning_guard.py。
- S1.2 操作链内联漂移检查（实时档）：drift_tolerance=0.3、10 步滑动窗口、
  类型熵>1.5、路径熵>2.0。类型漂移 → DRIFT_WARNING（auto_guard 降级标记，autonomy_regressor
  承载）；路径漂移 → DRIFT_DETECTED（blocked + P0 告警事件）。纯函数核，性能预算对齐
  蓝图 L2 ABAC 参考值（≈0.25ms 量级）；内联挂点预留 S0.2 gate 链路。
- 双维度阈值（置信度 × 意图偏差度）Hard-Gate：把「低置信但守规矩」与「高置信但跑偏」
  分开处置——单维异常 WARNING(auto_guard)，双维同坏 Hard-Gate blocked。
- Agent Challenge（Q2 已裁定）：本模块只产工单与降级标记——工单字段=原始任务意图复述 +
  当前动作链对齐说明 + 检测器证据；交叉会话复审由外部编排执行，交叉会话不可用/超时 →
  degraded=True 直接进人审队列（degraded_human_review），人兜底不可省。

事件产出按 16号文 §4.2 P0-1 统一事件 schema（source_domain=gov_drift）：
- 全量检查 → .runtime/audit/agentic_drift_guard.jsonl
- DETECTED P0 告警 → .runtime/audit/agentic_drift_guard_alerts.jsonl（severity=critical）
- challenge 工单 → 调用方指定目录 challenge-<ticket_id>.json

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: counts 参数
#   fields: 参数 counts，类型注解 Sequence[int]
#   code: agentic_drift_guard.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: ops 参数
#   fields: 参数 ops，类型注解 Sequence[ChainOperation]
#   code: agentic_drift_guard.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: config 参数
#   fields: 参数 config，类型注解 DriftCheckConfig | None
#   code: agentic_drift_guard.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: confidence 参数
#   fields: 参数 confidence，类型注解 float
#   code: agentic_drift_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DriftCheckConfig
#   name_en: DriftCheckConfig
#   intro: S1.2 内联检查参数（RBAC 蓝图决策 D-018-21 口径；参数>7 收 dataclass 纪律）。
#   desc: S1.2 内联检查参数（RBAC 蓝图决策 D-018-21 口径；参数>7 收 dataclass 纪律）。；公共方法（定义序）: validate；源码 L211-L231
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② shannon_entropy
#   name_en: shannon_entropy
#   intro: Shannon 熵（log2）。
#   desc: Shannon 熵（log2）。空序列/全零 → 0.0。；源码 L261-L272
#   inputs: counts
#   outputs: float
# - id: A3
#   name_zh: ③ check_operation_chain
#   name_en: check_operation_chain
#   intro: S1.2 操作链内联漂移检查（纯函数核，无 IO，性能预算 ≈0.25ms 量级）。
#   desc: S1.2 操作链内联漂移检查（纯函数核，无 IO，性能预算 ≈0.25ms 量级）。 取最近 window_size 步：类型熵>阈值且类型偏离率>drift_tolerance…；源码 L291-L359
#   inputs: ops config
#   outputs: DriftVerdict
# - id: A4
#   name_zh: ④ evaluate_dual_dimension
#   name_en: evaluate_dual_dimension
#   intro: 双维度阈值 Hard-Gate（置信度 × 意图偏差度，15号文 §3.2）。
#   desc: 双维度阈值 Hard-Gate（置信度 × 意图偏差度，15号文 §3.2）。 低置信（<confidence_floor）× 高意图偏差（>drift_tolerance）双坏…；源码 L362-L399
#   inputs: confidence intent_deviation config
#   outputs: DriftVerdict
# - id: A5
#   name_zh: ⑤ build_behavior_baseline
#   name_en: build_behavior_baseline
#   intro: S1.1：从历史会话统计行为基线（操作频率 + 触碰模块集合；委托 BM-RC-04-F 实现）。
#   desc: S1.1：从历史会话统计行为基线（操作频率 + 触碰模块集合；委托 BM-RC-04-F 实现）。；源码 L405-L411
#   inputs: sessions min_sessions
#   outputs: BehaviorBaseline
# - id: A6
#   name_zh: ⑥ check_session_against_baseline
#   name_en: check_session_against_baseline
#   intro: S1.1：单会话异常检出（z-score 偏离 + 首次触碰基线外模块；空列表=正常）。
#   desc: S1.1：单会话异常检出（z-score 偏离 + 首次触碰基线外模块；空列表=正常）。 告警通道待 55 号定型承接，当前 interim=logger.warning + 异…；源码 L414-L431
#   inputs: session baseline z_threshold
#   outputs: list[BehaviorAnomaly]
# - id: A7
#   name_zh: ⑦ ChallengeTicket
#   name_en: ChallengeTicket
#   intro: Agent Challenge 工单（Q2 裁定：统一落盘载体与降级形态，人兜底不可省）。
#   desc: Agent Challenge 工单（Q2 裁定：统一落盘载体与降级形态，人兜底不可省）。；公共方法（定义序）: to_dict；源码 L438-L460
#   inputs: 无参数
#   outputs: 返回值
# - id: A8
#   name_zh: ⑧ build_challenge_ticket
#   name_en: build_challenge_ticket
#   intro: 检测器判疑 → 生成 challenge 工单（degraded=True 即降级直进人审队列）。
#   desc: 检测器判疑 → 生成 challenge 工单（degraded=True 即降级直进人审队列）。；源码 L463-L490
#   inputs: verdict original_intent_restatement action_chain_alignment degraded
#   outputs: ChallengeTicket
# - id: A9
#   name_zh: ⑨ write_challenge_ticket
#   name_en: write_challenge_ticket
#   intro: 工单落盘接口位：写 challenge-<ticket_id>.json，返回文件名（交叉会话复审由外部编排消费）。
#   desc: 工单落盘接口位：写 challenge-<ticket_id>.json，返回文件名（交叉会话复审由外部编排消费）。；源码 L493-L499
#   inputs: ticket tickets_dir
#   outputs: str
# - id: A10
#   name_zh: ⑩ AgenticDriftGuard
#   name_en: AgenticDriftGuard
#   intro: S1.2 编排壳：纯函数核 + 审计/P0 告警落盘（挂 S0.2 gate 链路的内联点）。
#   desc: S1.2 编排壳：纯函数核 + 审计/P0 告警落盘（挂 S0.2 gate 链路的内联点）。 用法:: guard = AgenticDriftGuard() verdict…；公共方法（定义序）: config,…
#   inputs: runtime_dir config
#   outputs: 返回值
#   （注：A10 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy_core/test_agentic_drift_guard.py；S0.2 gate 链路（内联挂点预留）
# - id: O2
#   name_zh: DriftVerdict
#   name_en: DriftVerdict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy_core/test_agentic_drift_guard.py；S0.2 gate 链路（内联挂点预留）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

import json
import logging
import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final, Sequence

from zephyr.governance.lifecycle_governance.ai_behavior_baseline import (
    BehaviorAnomaly,
    BehaviorBaseline,
    SessionBehavior,
    compute_baseline,
    detect_anomalies,
)

logger = logging.getLogger(__name__)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

SCHEMA_VERSION: Final[str] = "1.0"
SOURCE_DOMAIN: Final[str] = "gov_drift"
THREAT_CATEGORY: Final[str] = "agentic_drift"


class DriftGuardError(Exception):
    """配置/输入非法（裸异常——ZA-AU 前缀未声明，沿 MOD-AU-002 域先例）。消息禁含 session_id。"""


class DriftLevel(str, Enum):
    """漂移判定级别。"""

    OK = "ok"
    WARNING = "warning"
    DETECTED = "detected"


@dataclass(frozen=True)
class DriftCheckConfig:
    """S1.2 内联检查参数（RBAC 蓝图决策 D-018-21 口径；参数>7 收 dataclass 纪律）。"""

    window_size: int = 10
    type_entropy_threshold: float = 1.5
    path_entropy_threshold: float = 2.0
    drift_tolerance: float = 0.3
    confidence_floor: float = 0.3
    min_ops: int = 4

    def validate(self) -> None:
        if self.window_size < 2:
            raise DriftGuardError(f"window_size 须 >= 2: {self.window_size}")
        if self.type_entropy_threshold <= 0 or self.path_entropy_threshold <= 0:
            raise DriftGuardError("熵阈值须 > 0")
        if not 0.0 < self.drift_tolerance < 1.0:
            raise DriftGuardError(f"drift_tolerance 须落在 (0,1): {self.drift_tolerance}")
        if not 0.0 < self.confidence_floor < 1.0:
            raise DriftGuardError(f"confidence_floor 须落在 (0,1): {self.confidence_floor}")
        if self.min_ops < 2:
            raise DriftGuardError(f"min_ops 须 >= 2: {self.min_ops}")


DEFAULT_DRIFT_CONFIG: Final[DriftCheckConfig] = DriftCheckConfig()


@dataclass(frozen=True)
class ChainOperation:
    """操作链单步（op_type 如 read/write/delete；path 为仓内相对路径）。"""

    op_type: str
    path: str
    timestamp: str = ""


@dataclass(frozen=True)
class DriftVerdict:
    """单次漂移判定结果（不可变）。blocked=True 即 Hard-Gate 阻断。"""

    verdict_id: str
    level: DriftLevel
    blocked: bool
    auto_guard: bool
    type_entropy: float = 0.0
    path_entropy: float = 0.0
    dimension: str = "none"  # none / type / path / both / dual_dimension
    reason: str = ""
    timestamp: str = ""


def shannon_entropy(counts: Sequence[int]) -> float:
    """Shannon 熵（log2）。空序列/全零 → 0.0。"""
    total = sum(counts)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        entropy -= p * math.log2(p)
    return entropy


def _top_segment(path: str) -> str:
    """路径顶层段（路径熵维度粒度；空路径归 (root)）。"""
    norm = path.strip().replace("\\", "/").strip("/")
    if not norm:
        return "(root)"
    return norm.split("/", 1)[0].casefold()


def _drift_ratio(counts: Sequence[int]) -> float:
    """偏离率 = 1 - 主导类占比（drift_tolerance 的比较对象）。"""
    total = sum(counts)
    if total <= 0:
        return 0.0
    return 1.0 - max(counts) / total


def check_operation_chain(
    ops: Sequence[ChainOperation],
    config: DriftCheckConfig | None = None,
) -> DriftVerdict:
    """S1.2 操作链内联漂移检查（纯函数核，无 IO，性能预算 ≈0.25ms 量级）。

    取最近 window_size 步：类型熵>阈值且类型偏离率>drift_tolerance → 类型漂移；
    路径熵>阈值且路径偏离率>drift_tolerance → 路径漂移。
    仅类型漂移 → WARNING（auto_guard 降级标记）；含路径漂移 → DETECTED（blocked）。
    窗口样本 <min_ops 小样本不判 → OK（对齐基线 fail-closed 口径）。
    """
    cfg = config or DEFAULT_DRIFT_CONFIG
    cfg.validate()
    window = list(ops)[-cfg.window_size :]
    base = {
        "verdict_id": uuid.uuid4().hex[:12],
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if len(window) < cfg.min_ops:
        return DriftVerdict(
            level=DriftLevel.OK,
            blocked=False,
            auto_guard=False,
            reason=f"窗口样本 {len(window)} < min_ops {cfg.min_ops}，小样本不判",
            **base,
        )

    type_counts: dict[str, int] = {}
    path_counts: dict[str, int] = {}
    for op in window:
        t = (op.op_type or "").strip().casefold() or "(unknown)"
        type_counts[t] = type_counts.get(t, 0) + 1
        p = _top_segment(op.path)
        path_counts[p] = path_counts.get(p, 0) + 1

    type_entropy = shannon_entropy(list(type_counts.values()))
    path_entropy = shannon_entropy(list(path_counts.values()))
    type_drift = (
        type_entropy > cfg.type_entropy_threshold and _drift_ratio(list(type_counts.values())) > cfg.drift_tolerance
    )
    path_drift = (
        path_entropy > cfg.path_entropy_threshold and _drift_ratio(list(path_counts.values())) > cfg.drift_tolerance
    )

    if path_drift:
        level = DriftLevel.DETECTED
        dimension = "both" if type_drift else "path"
        reason = (
            f"路径熵={path_entropy:.2f}>{cfg.path_entropy_threshold}（路径漂移，维度={dimension}）→ blocked + P0 告警"
        )
    elif type_drift:
        level = DriftLevel.WARNING
        dimension = "type"
        reason = f"类型熵={type_entropy:.2f}>{cfg.type_entropy_threshold}（类型漂移）→ 降级 auto_guard"
    else:
        level = DriftLevel.OK
        dimension = "none"
        reason = "操作链熵值在阈值内"

    return DriftVerdict(
        level=level,
        blocked=level == DriftLevel.DETECTED,
        auto_guard=level == DriftLevel.WARNING,
        type_entropy=type_entropy,
        path_entropy=path_entropy,
        dimension=dimension,
        reason=reason,
        **base,
    )


def evaluate_dual_dimension(
    confidence: float,
    intent_deviation: float,
    config: DriftCheckConfig | None = None,
) -> DriftVerdict:
    """双维度阈值 Hard-Gate（置信度 × 意图偏差度，15号文 §3.2）。

    低置信（<confidence_floor）× 高意图偏差（>drift_tolerance）双坏 → DETECTED(blocked)；
    单维异常（低置信但守规矩 / 高置信但跑偏）→ WARNING(auto_guard)，分开处置。
    """
    cfg = config or DEFAULT_DRIFT_CONFIG
    cfg.validate()
    for name, value in (("confidence", confidence), ("intent_deviation", intent_deviation)):
        if not 0.0 <= value <= 1.0:
            raise DriftGuardError(f"{name} 须落在 [0,1]: {value}")
    low_conf = confidence < cfg.confidence_floor
    high_dev = intent_deviation > cfg.drift_tolerance
    if low_conf and high_dev:
        level, dimension = DriftLevel.DETECTED, "dual_dimension"
        reason = (
            f"置信度={confidence:.2f}<{cfg.confidence_floor} 且 "
            f"意图偏差={intent_deviation:.2f}>{cfg.drift_tolerance}（双维同坏）→ Hard-Gate blocked"
        )
    elif low_conf or high_dev:
        level, dimension = DriftLevel.WARNING, "dual_dimension"
        reason = "单维异常（%s）→ 降级 auto_guard" % ("低置信但守规矩" if low_conf else "高置信但跑偏")
    else:
        level, dimension = DriftLevel.OK, "none"
        reason = "双维均在阈值内"
    return DriftVerdict(
        verdict_id=uuid.uuid4().hex[:12],
        level=level,
        blocked=level == DriftLevel.DETECTED,
        auto_guard=level == DriftLevel.WARNING,
        dimension=dimension,
        reason=reason,
        timestamp=datetime.now(UTC).isoformat(),
    )


# ── S1.1 行为基线（复用 ai_behavior_baseline，BM-RC-04-F 口径）────────────


def build_behavior_baseline(
    sessions: Sequence[SessionBehavior],
    *,
    min_sessions: int = 3,
) -> BehaviorBaseline:
    """S1.1：从历史会话统计行为基线（操作频率 + 触碰模块集合；委托 BM-RC-04-F 实现）。"""
    return compute_baseline(sessions, min_sessions=min_sessions)


def check_session_against_baseline(
    session: SessionBehavior,
    baseline: BehaviorBaseline,
    *,
    z_threshold: float = 3.0,
) -> list[BehaviorAnomaly]:
    """S1.1：单会话异常检出（z-score 偏离 + 首次触碰基线外模块；空列表=正常）。

    告警通道待 55 号定型承接，当前 interim=logger.warning + 异常清单回传（61 号 §3.6 裁定）。
    """
    anomalies = detect_anomalies(session, baseline, z_threshold=z_threshold)
    if anomalies:
        logger.warning(
            "S1.1 行为基线异常 %d 条（%s）",
            len(anomalies),
            ",".join(sorted({a.rule for a in anomalies})),
        )
    return anomalies


# ── Agent Challenge 工单（只产工单与降级标记；交叉会话复审由外部编排）────────


@dataclass(frozen=True)
class ChallengeTicket:
    """Agent Challenge 工单（Q2 裁定：统一落盘载体与降级形态，人兜底不可省）。"""

    ticket_id: str
    created_at: str
    status: str  # pending_cross_review / degraded_human_review
    degraded: bool
    original_intent_restatement: str
    action_chain_alignment: str
    detector_evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "ticket_id": self.ticket_id,
            "created_at": self.created_at,
            "ticket_type": "agent_challenge",
            "status": self.status,
            "degraded": self.degraded,
            "original_intent_restatement": self.original_intent_restatement,
            "action_chain_alignment": self.action_chain_alignment,
            "detector_evidence": self.detector_evidence,
        }


def build_challenge_ticket(
    verdict: DriftVerdict,
    *,
    original_intent_restatement: str,
    action_chain_alignment: str,
    degraded: bool = False,
) -> ChallengeTicket:
    """检测器判疑 → 生成 challenge 工单（degraded=True 即降级直进人审队列）。"""
    if not original_intent_restatement.strip():
        raise DriftGuardError("original_intent_restatement 禁空（人兜底可审前提）")
    if not action_chain_alignment.strip():
        raise DriftGuardError("action_chain_alignment 禁空（人兜底可审前提）")
    return ChallengeTicket(
        ticket_id=uuid.uuid4().hex[:12],
        created_at=datetime.now(UTC).isoformat(),
        status="degraded_human_review" if degraded else "pending_cross_review",
        degraded=degraded,
        original_intent_restatement=original_intent_restatement.strip(),
        action_chain_alignment=action_chain_alignment.strip(),
        detector_evidence={
            "verdict_id": verdict.verdict_id,
            "level": verdict.level,
            "dimension": verdict.dimension,
            "type_entropy": verdict.type_entropy,
            "path_entropy": verdict.path_entropy,
            "reason": verdict.reason,
        },
    )


def write_challenge_ticket(ticket: ChallengeTicket, tickets_dir: str | Path) -> str:
    """工单落盘接口位：写 challenge-<ticket_id>.json，返回文件名（交叉会话复审由外部编排消费）。"""
    out_dir = Path(tickets_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"challenge-{ticket.ticket_id}.json"
    (out_dir / name).write_text(json.dumps(ticket.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return name


# ── Guard 编排层（内联检查 + 16号文统一事件落盘）──────────────────────────


class AgenticDriftGuard:
    """S1.2 编排壳：纯函数核 + 审计/P0 告警落盘（挂 S0.2 gate 链路的内联点）。

    用法::

        guard = AgenticDriftGuard()
        verdict = guard.inspect(ops)
        if verdict.blocked:
            ...  # Hard-Gate 阻断；P0 告警事件已落盘
    """

    def __init__(
        self,
        runtime_dir: str | Path | None = None,
        config: DriftCheckConfig | None = None,
    ) -> None:
        self._runtime_dir = Path(runtime_dir) if runtime_dir else _REPO_ROOT / ".runtime"
        self._audit_path = self._runtime_dir / "audit" / "agentic_drift_guard.jsonl"
        self._alerts_path = self._runtime_dir / "audit" / "agentic_drift_guard_alerts.jsonl"
        self._config = config or DEFAULT_DRIFT_CONFIG

    @property
    def config(self) -> DriftCheckConfig:
        """生效配置（只读；S0.2 gate 内联挂接据此对齐会话滑窗宽度）。"""
        return self._config

    def inspect(
        self,
        ops: Sequence[ChainOperation],
        *,
        trace: bool = True,
    ) -> DriftVerdict:
        """内联漂移检查（永不抛异常；DETECTED → blocked + P0 告警事件产出）。"""
        try:
            verdict = check_operation_chain(ops, self._config)
        except DriftGuardError:
            raise
        except Exception as exc:  # noqa: BLE001 — ERROR_CONTRACT：判定永不抛异常
            logger.warning("agentic_drift_guard 内部异常，fail-closed 按 WARNING 降级: %r", exc)
            verdict = DriftVerdict(
                verdict_id=uuid.uuid4().hex[:12],
                level=DriftLevel.WARNING,
                blocked=False,
                auto_guard=True,
                dimension="internal_error",
                reason="内联检查内部异常，fail-closed 降级 auto_guard",
                timestamp=datetime.now(UTC).isoformat(),
            )
        if trace:
            self._trace(verdict)
        if verdict.level == DriftLevel.DETECTED:
            self._write_p0_alert(verdict)
        return verdict

    def close(self) -> None:
        """句柄占位（当前逐写即 flush，无持久句柄；保留与 MOD-AU-001 同款接口）。"""

    # ── 内部实现 ──────────────────────────────────────────────

    def _trace(self, verdict: DriftVerdict) -> None:
        record = {
            "schema_version": SCHEMA_VERSION,
            "event_id": verdict.verdict_id,
            "timestamp": verdict.timestamp,
            "source_domain": SOURCE_DOMAIN,
            "event_type": "drift_check",
            "threat_category": THREAT_CATEGORY if verdict.level != DriftLevel.OK else "none",
            "severity": {
                DriftLevel.OK: "info",
                DriftLevel.WARNING: "elevated",
                DriftLevel.DETECTED: "critical",
            }[verdict.level],
            "level": verdict.level,
            "blocked": verdict.blocked,
            "auto_guard": verdict.auto_guard,
            "reason": verdict.reason,
            "evidence": {
                "type_entropy": verdict.type_entropy,
                "path_entropy": verdict.path_entropy,
                "dimension": verdict.dimension,
            },
        }
        self._append_jsonl(self._audit_path, record)

    def _write_p0_alert(self, verdict: DriftVerdict) -> None:
        """DETECTED → P0 告警事件（severity=critical，16号文统一事件 schema）。"""
        record = {
            "schema_version": SCHEMA_VERSION,
            "event_id": verdict.verdict_id,
            "timestamp": verdict.timestamp,
            "source_domain": SOURCE_DOMAIN,
            "event_type": "agentic_drift_detected",
            "threat_category": THREAT_CATEGORY,
            "severity": "critical",
            "level": verdict.level,
            "blocked": verdict.blocked,
            "reason": verdict.reason,
            "evidence": {
                "type_entropy": verdict.type_entropy,
                "path_entropy": verdict.path_entropy,
                "dimension": verdict.dimension,
            },
        }
        self._append_jsonl(self._alerts_path, record)

    @staticmethod
    def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
        """jsonl 追加（逐写即 flush；IO 失败不阻断判定，仅留 warning）。"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8", buffering=1) as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("agentic_drift_guard 事件落盘失败（判定仍生效）: %r", exc)


__all__: Final = [
    "DEFAULT_DRIFT_CONFIG",
    "SCHEMA_VERSION",
    "SOURCE_DOMAIN",
    "AgenticDriftGuard",
    "ChainOperation",
    "ChallengeTicket",
    "DriftCheckConfig",
    "DriftGuardError",
    "DriftLevel",
    "DriftVerdict",
    "build_behavior_baseline",
    "build_challenge_ticket",
    "check_operation_chain",
    "check_session_against_baseline",
    "evaluate_dual_dimension",
    "shannon_entropy",
    "write_challenge_ticket",
]
