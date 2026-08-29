# [BLUEPRINT] MOD-AU-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.1-S0.2 + §4.2-S1.2
# [MODULE] zephyr.autonomy_core.autonomy_boundary_gate
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pyyaml; zephyr.autonomy_core.agentic_drift_guard（S1.2 内联漂移检查，默认启用可关）
# [CONSUMERS] tests/autonomy/test_autonomy_boundary_gate.py; tests/autonomy/test_autonomy_gate_drift_hook.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] fail-closed(注册表不可读/目标未登记/内部异常 => 永不放行); 每次判定必留痕(.runtime/audit jsonl); 判定以 GOV-AI-001 注册表为唯一真源(文件头 [AI_AUTONOMY] 锚定仅为投影提示); S1.2 漂移内联挂接 drift_check_enabled=False 时零行为变化; 漂移检查仅作用于带 session_id 的留痕判定（内存滑窗增量，禁全量读 jsonl）; 漂移挂点自身异常不阻断原判定
# [MODIFY-GUARD] Owner approval required; 变更须同步 15号文 §4.1 S0.2 验收口径
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] check_write_permission() 永不抛异常; 任何内部失败降级为 fail-closed ESCALATE 判定
# [TESTS] tests/autonomy/test_autonomy_boundary_gate.py
# [A_module] module_id=MOD-AU-001 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""AutonomyBoundaryGate — 运行时写操作三分类判定门（MOD-AU-001）.

设计真源：15号文（15_autonomy_boundary_risk.md）§3.1 / §4.1-S0.2：
- 写操作（文件写入/注册表变更/配置修改）发生前查 GOV-AI-001 注册表：
  ai_modifiable 放行（留痕）/ human_gated 拦截并升级人审工单 / immutable_core 物理拦截并告警。
- fail-closed：注册表不可读、目标未登记、判定内部异常 → 拒绝自治写入，
  默认按 human_gated 处理（升级人审工单），永不放行。
- 事件产出按 16号文 §4.2 P0-1 统一事件 schema 落盘（schema_version/event_id/时间戳/
  来源域/威胁类别/严重度/证据指针/关联会话），source_domain=access_control。
- 与既有 commit_gates 互补：commit_gates 管提交时点，本 gate 管工作区内写操作时点。

留痕落点（runtime_dir 默认仓根 .runtime/）：
- 全部判定 → .runtime/audit/autonomy_boundary_gate.jsonl（追加，逐行 flush）
- human_gated 升级工单 → .runtime/autonomy_gate/queue/ticket-<verdict_id>.json（status=pending_review）
- immutable_core 告警 → .runtime/autonomy_gate/alerts.jsonl（severity=critical）

S1.2 内联漂移挂接（15号文 §4.2，默认启用，drift_check_enabled=False 整体关断）：
- 每次带 session_id 的留痕判定，把本步操作追加进该会话的内存滑窗（deque，
  与审计事件流 append 同步增量更新，不做全量 jsonl 读取），再交 AgenticDriftGuard
  做操作链漂移检查（纯函数核，性能预算对齐蓝图 L2 ABAC ≈0.25ms 量级）。
- DRIFT_WARNING → 不阻断，verdict 打 auto_guard 降级标记（autonomy_regressor 的
  auto_guard 档语义）；DRIFT_DETECTED → 原放行判定升级为 BLOCK（Hard-Gate），
  P0 告警由 AgenticDriftGuard 按 16号文统一事件 schema 落盘。
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from collections import deque
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final, final

import yaml

from zephyr.autonomy_core.agentic_drift_guard import (
    AgenticDriftGuard,
    ChainOperation,
    DriftCheckConfig,
    DriftLevel,
)

logger = logging.getLogger(__name__)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
_REGISTRY_REL: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml"

SCHEMA_VERSION: Final[str] = "1.0"
SOURCE_DOMAIN: Final[str] = "access_control"

# 注册表中无法做路径匹配的占位 path（子模块注解行/仓外资源），加载时跳过
_SKIP_PATH_MARKERS: Final[frozenset[str]] = frozenset(
    {"", "同上 子模块", "见 §2.9", "项目外 os 级"}
)


class GateDecision(str, Enum):
    """判定动作."""

    ALLOW = "allow"  # ai_modifiable：放行（留痕可回溯）
    ESCALATE = "escalate"  # human_gated / fail-closed：拦截并升级人审工单
    BLOCK = "block"  # immutable_core：物理拦截并告警


class AutonomyLayer(str, Enum):
    """三分类权限层 + fail-closed 兜底层."""

    AI_MODIFIABLE = "ai_modifiable"
    HUMAN_GATED = "human_gated"
    IMMUTABLE_CORE = "immutable_core"
    UNREGISTERED = "unregistered"  # 目标未在注册表登记（fail-closed）
    REGISTRY_UNAVAILABLE = "registry_unavailable"  # 注册表不可读（fail-closed）
    INTERNAL_ERROR = "internal_error"  # 判定内部异常（fail-closed）


_LAYER_TO_DECISION: Final[dict[AutonomyLayer, GateDecision]] = {
    AutonomyLayer.AI_MODIFIABLE: GateDecision.ALLOW,
    AutonomyLayer.HUMAN_GATED: GateDecision.ESCALATE,
    AutonomyLayer.IMMUTABLE_CORE: GateDecision.BLOCK,
}

_LAYER_REASON: Final[dict[AutonomyLayer, str]] = {
    AutonomyLayer.AI_MODIFIABLE: "ai_modifiable 放行（留痕可回溯）",
    AutonomyLayer.HUMAN_GATED: "human_gated 拦截，升级人审工单",
    AutonomyLayer.IMMUTABLE_CORE: "immutable_core 物理拦截并告警",
}


@dataclass(frozen=True)
class GateVerdict:
    """单次写操作判定结果（不可变）.

    auto_guard / drift_level / drift_verdict_id 为 S1.2 漂移内联检查投影字段：
    未启用或无 session_id 时保持默认值（零行为变化）；drift_level ∈
    {""/ok/warning/detected}，warning 时 auto_guard=True（不阻断），
    detected 且原判定放行时 decision 升级为 BLOCK（Hard-Gate）。
    """

    verdict_id: str
    action_id: str
    target: str
    decision: GateDecision
    layer: AutonomyLayer
    reason: str
    fail_closed: bool = False
    matched_path: str = ""
    matched_module: str = ""
    session_id: str = ""
    ticket_path: str = ""
    timestamp: str = ""
    auto_guard: bool = False
    drift_level: str = ""
    drift_verdict_id: str = ""

    @property
    def allowed(self) -> bool:
        """是否放行（仅 ai_modifiable 命中的 ALLOW 为 True）."""
        return self.decision is GateDecision.ALLOW

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典（decision/layer 取值字符串）."""
        return {
            "verdict_id": self.verdict_id,
            "action_id": self.action_id,
            "target": self.target,
            "decision": self.decision.value,
            "layer": self.layer.value,
            "reason": self.reason,
            "fail_closed": self.fail_closed,
            "matched_path": self.matched_path,
            "matched_module": self.matched_module,
            "session_id": self.session_id,
            "ticket_path": self.ticket_path,
            "timestamp": self.timestamp,
            "auto_guard": self.auto_guard,
            "drift_level": self.drift_level,
            "drift_verdict_id": self.drift_verdict_id,
        }


def _parse_permission(raw: str) -> AutonomyLayer | None:
    """解析注册表 permission 自由文本为三分类（兼容 "Immutable Core（追加专用）" 等变体）."""
    text = raw.strip().lower()
    if text.startswith("immutable"):
        return AutonomyLayer.IMMUTABLE_CORE
    if text.startswith("human"):
        return AutonomyLayer.HUMAN_GATED
    if text.startswith("ai-modifiable") or text.startswith("ai_modifiable"):
        return AutonomyLayer.AI_MODIFIABLE
    return None


def _normalize_registry_path(raw: str) -> str | None:
    """归一化注册表路径；占位 path 返回 None（不参与路径匹配）."""
    text = raw.strip()
    if text.casefold() in _SKIP_PATH_MARKERS:
        return None
    norm = text.replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    norm = norm.strip("/")
    if not norm:
        return None
    return norm.casefold()


class _RegistryIndex:
    """GOV-AI-001 注册表的 路径→权限 索引（mtime 缓存，注册表自动派生模式）."""

    def __init__(self, registry_path: Path) -> None:
        self._registry_path = registry_path
        self._stamp: tuple[int, int] | None = None
        self._entries: list[tuple[str, AutonomyLayer, str, str]] = []

    @property
    def entries(self) -> list[tuple[str, AutonomyLayer, str, str]]:
        """按路径长度降序的 (归一化路径, 权限层, 原始路径, 模块名) 列表.

        注册表不可读/解析失败时抛异常，由调用方按 fail-closed 处理；
        失败不缓存，下次调用重试（注册表修复后自动恢复）。
        """
        self._refresh()
        return self._entries

    def _refresh(self) -> None:
        stat = os.stat(self._registry_path)
        stamp = (stat.st_mtime_ns, stat.st_size)
        if stamp == self._stamp:
            return
        self._entries = self._parse()
        self._stamp = stamp

    def _parse(self) -> list[tuple[str, AutonomyLayer, str, str]]:
        with open(self._registry_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ValueError("registry root is not a mapping")
        table = data.get("permission_table")
        if not isinstance(table, dict):
            raise ValueError("permission_table missing or not a mapping")
        entries: list[tuple[str, AutonomyLayer, str, str]] = []
        for section in table.values():
            if not isinstance(section, list):
                continue
            for item in section:
                if not isinstance(item, dict):
                    continue
                raw_path = item.get("path")
                permission = item.get("permission")
                if not raw_path or not permission:
                    continue
                layer = _parse_permission(str(permission))
                if layer is None:
                    continue
                norm = _normalize_registry_path(str(raw_path))
                if norm is None:
                    continue
                module = str(item.get("module") or item.get("component") or "")
                entries.append((norm, layer, str(raw_path), module))
        # 最长前缀优先：子路径登记优先于父路径登记
        entries.sort(key=lambda entry: len(entry[0]), reverse=True)
        return entries


@final
class AutonomyBoundaryGate:
    """运行时写操作三分类判定门.

    用法::

        gate = AutonomyBoundaryGate()
        verdict = gate.check_write_permission("act-1", "src/zephyr/risk/engine.py")
        if not verdict.allowed:
            ...  # 阻断写操作；human_gated 已落人审工单，immutable_core 已告警

    热路径（缓存命中）只做一次 os.stat + 线性前缀扫描 + 一行 jsonl 追加，
    延迟实测见 docs/_working/reports/2026-08-22-autonomy-gate-latency.md。
    """

    def __init__(
        self,
        registry_path: str | Path | None = None,
        runtime_dir: str | Path | None = None,
        repo_root: str | Path | None = None,
        *,
        drift_check_enabled: bool = True,
        drift_config: DriftCheckConfig | None = None,
        drift_guard: AgenticDriftGuard | None = None,
    ) -> None:
        self._repo_root = Path(repo_root) if repo_root else _REPO_ROOT
        self._registry_path = (
            Path(registry_path) if registry_path else self._repo_root / _REGISTRY_REL
        )
        self._runtime_dir = Path(runtime_dir) if runtime_dir else self._repo_root / ".runtime"
        self._audit_path = self._runtime_dir / "audit" / "autonomy_boundary_gate.jsonl"
        self._queue_dir = self._runtime_dir / "autonomy_gate" / "queue"
        self._alerts_path = self._runtime_dir / "autonomy_gate" / "alerts.jsonl"
        self._index = _RegistryIndex(self._registry_path)
        self._audit_handle: Any = None
        self._alerts_handle: Any = None
        # S1.2 内联漂移挂接（15号文 §4.2）：默认启用；drift_check_enabled=False 时
        # 不建 guard/滑窗，判定链路与挂接前完全一致（零行为变化）。
        self._drift_guard: AgenticDriftGuard | None = None
        self._drift_window_size: int = 10
        self._session_ops: dict[str, deque[ChainOperation]] = {}
        if drift_check_enabled:
            self._drift_guard = drift_guard or AgenticDriftGuard(
                runtime_dir=self._runtime_dir, config=drift_config
            )
            self._drift_window_size = self._drift_guard.config.window_size

    def check_write_permission(
        self,
        action_id: str,
        target_path_or_resource: str,
        session_context: dict[str, Any] | None = None,
        *,
        trace: bool = True,
    ) -> GateVerdict:
        """写操作前三分类判定（永不抛异常，fail-closed）.

        Args:
            action_id: 写操作标识（调用方动作 ID，留痕用）.
            target_path_or_resource: 目标文件/资源路径（仓内相对路径或绝对路径）.
            session_context: 可选会话上下文（session_id 等，随留痕落盘）.
            trace: 是否写审计 jsonl（默认 True；仅延迟实测等探针场景关闭）.

        Returns:
            GateVerdict：decision=ALLOW 放行 / ESCALATE 拦截+人审工单 / BLOCK 物理拦截+告警；
            fail_closed=True 表示本次判定走了兜底（注册表不可读/目标未登记/内部异常）。
        """
        session_id = ""
        if isinstance(session_context, dict):
            session_id = str(session_context.get("session_id") or "")
        try:
            verdict = self._decide(str(action_id), str(target_path_or_resource), session_id)
        except Exception as exc:  # noqa: BLE001 — ERROR_CONTRACT：判定永不抛异常
            verdict = GateVerdict(
                verdict_id=uuid.uuid4().hex[:12],
                action_id=str(action_id),
                target=str(target_path_or_resource),
                decision=GateDecision.ESCALATE,
                layer=AutonomyLayer.INTERNAL_ERROR,
                reason=f"gate 内部异常，fail-closed 升级人审: {exc!r}",
                fail_closed=True,
                session_id=session_id,
                timestamp=datetime.now(UTC).isoformat(),
            )
        if verdict.decision is GateDecision.ESCALATE:
            ticket_rel = self._write_ticket(verdict, session_context)
            verdict = replace(verdict, ticket_path=ticket_rel)
        elif verdict.decision is GateDecision.BLOCK:
            self._write_alert(verdict, session_context)
        if trace:
            verdict = self._drift_inline_check(verdict, session_context)
            self._trace(verdict)
        return verdict

    def close(self) -> None:
        """关闭审计/告警文件句柄（测试/探针场景显式调用）."""
        for attr in ("_audit_handle", "_alerts_handle"):
            handle = getattr(self, attr)
            if handle is not None:
                try:
                    handle.close()
                except OSError:
                    pass
                setattr(self, attr, None)

    # ── 内部实现 ──────────────────────────────────────────────

    def _decide(self, action_id: str, target: str, session_id: str) -> GateVerdict:
        base = {
            "verdict_id": uuid.uuid4().hex[:12],
            "action_id": action_id,
            "target": target,
            "session_id": session_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            entries = self._index.entries
        except Exception as exc:  # noqa: BLE001 — 注册表不可读 → fail-closed
            return GateVerdict(
                decision=GateDecision.ESCALATE,
                layer=AutonomyLayer.REGISTRY_UNAVAILABLE,
                reason=f"注册表不可读，fail-closed 按 human_gated 升级人审: {exc!r}",
                fail_closed=True,
                **base,
            )
        layer, raw_path, module = self._lookup(entries, self._normalize_target(target))
        if layer is None:
            return GateVerdict(
                decision=GateDecision.ESCALATE,
                layer=AutonomyLayer.UNREGISTERED,
                reason="目标未在 GOV-AI-001 登记，fail-closed 按 human_gated 升级人审",
                fail_closed=True,
                **base,
            )
        return GateVerdict(
            decision=_LAYER_TO_DECISION[layer],
            layer=layer,
            reason=_LAYER_REASON[layer],
            matched_path=raw_path,
            matched_module=module,
            **base,
        )

    def _normalize_target(self, target: str) -> str:
        text = target.strip().replace("\\", "/")
        if os.path.isabs(text):
            try:
                text = Path(text).resolve().relative_to(self._repo_root).as_posix()
            except ValueError:
                pass  # 仓外绝对路径：保持原样，按未登记 fail-closed
        while text.startswith("./"):
            text = text[2:]
        return text.strip("/").casefold()

    @staticmethod
    def _lookup(
        entries: list[tuple[str, AutonomyLayer, str, str]], target_norm: str
    ) -> tuple[AutonomyLayer | None, str, str]:
        for norm, layer, raw_path, module in entries:
            if target_norm == norm or target_norm.startswith(norm + "/"):
                return layer, raw_path, module
        return None, "", ""

    def _drift_inline_check(
        self, verdict: GateVerdict, session_context: dict[str, Any] | None
    ) -> GateVerdict:
        """S1.2 操作链内联漂移检查（15号文 §4.2，挂在留痕判定链路上）.

        操作链真源 = 本 gate 审计事件流（session_id 键控有序事件），此处以每会话
        内存滑窗（deque，maxlen=window_size）增量承载——判定事件流 append 时同步
        更新，禁止每次全量读 jsonl；无 session_id 即无链可判，直接跳过。
        处置：WARNING → auto_guard 降级标记（autonomy_regressor 语义，不阻断）；
        DETECTED → 原 ALLOW 升级 BLOCK（Hard-Gate），P0 告警由 guard 侧落盘。
        挂点自身异常不阻断原判定（仅 logger.warning）。
        """
        if self._drift_guard is None or not verdict.session_id:
            return verdict
        try:
            window = self._session_ops.get(verdict.session_id)
            if window is None:
                window = deque(maxlen=self._drift_window_size)
                self._session_ops[verdict.session_id] = window
            op_type = "write"
            if isinstance(session_context, dict):
                op_type = str(session_context.get("op_type") or "write")
            window.append(
                ChainOperation(
                    op_type=op_type,
                    path=self._normalize_target(verdict.target),
                    timestamp=verdict.timestamp,
                )
            )
            drift = self._drift_guard.inspect(tuple(window))
        except Exception as exc:  # noqa: BLE001 — 漂移挂点异常不阻断 gate 原判定
            logger.warning("S1.2 内联漂移检查异常（原判定仍生效）: %r", exc)
            return verdict
        if drift.level is DriftLevel.DETECTED:
            decision = verdict.decision
            note = f"agentic drift DETECTED（{drift.reason}）"
            if decision is GateDecision.ALLOW:
                decision = GateDecision.BLOCK
                note = f"{note}，原放行判定被 Hard-Gate 拦截"
            return replace(
                verdict,
                decision=decision,
                reason=f"{verdict.reason}；{note}",
                drift_level=drift.level.value,
                drift_verdict_id=drift.verdict_id,
            )
        if drift.level is DriftLevel.WARNING:
            return replace(
                verdict,
                reason=(
                    f"{verdict.reason}；agentic drift WARNING（{drift.reason}），"
                    "降级 auto_guard"
                ),
                auto_guard=True,
                drift_level=drift.level.value,
                drift_verdict_id=drift.verdict_id,
            )
        return replace(
            verdict, drift_level=drift.level.value, drift_verdict_id=drift.verdict_id
        )

    def _trace(self, verdict: GateVerdict) -> None:
        severity = {
            GateDecision.ALLOW: "info",
            GateDecision.ESCALATE: "elevated",
            GateDecision.BLOCK: "critical",
        }[verdict.decision]
        threat_category = {
            GateDecision.ALLOW: "none",
            GateDecision.ESCALATE: (
                "unauthorized_write_attempt" if verdict.fail_closed else "human_approval_required"
            ),
            GateDecision.BLOCK: "immutable_core_violation",
        }[verdict.decision]
        if verdict.drift_level in (DriftLevel.WARNING.value, DriftLevel.DETECTED.value):
            threat_category = "agentic_drift"
            if verdict.decision is GateDecision.ALLOW:
                severity = "elevated"  # WARNING 不阻断，但严重度提升留痕
        record = {
            "schema_version": SCHEMA_VERSION,
            "event_id": verdict.verdict_id,
            "timestamp": verdict.timestamp,
            "source_domain": SOURCE_DOMAIN,
            "event_type": "autonomy_gate_decision",
            "threat_category": threat_category,
            "severity": severity,
            "session_id": verdict.session_id,
            "evidence": {
                "registry": str(self._registry_path),
                "matched_path": verdict.matched_path,
                "ticket_path": verdict.ticket_path,
                "drift_level": verdict.drift_level,
                "drift_verdict_id": verdict.drift_verdict_id,
            },
            **verdict.to_dict(),
        }
        self._audit_write(json.dumps(record, ensure_ascii=False) + "\n")

    def _write_ticket(self, verdict: GateVerdict, session_context: dict[str, Any] | None) -> str:
        """human_gated / fail-closed → 落人审工单队列文件，返回仓内相对路径."""
        rel_path = ""
        try:
            self._queue_dir.mkdir(parents=True, exist_ok=True)
            ticket_file = self._queue_dir / f"ticket-{verdict.verdict_id}.json"
            payload = {
                "schema_version": SCHEMA_VERSION,
                "ticket_id": verdict.verdict_id,
                "timestamp": verdict.timestamp,
                "source_domain": SOURCE_DOMAIN,
                "event_type": "autonomy_gate_escalation",
                "severity": "elevated",
                "status": "pending_review",
                "session_id": verdict.session_id,
                "session_context": session_context or {},
                "verdict": verdict.to_dict(),
            }
            ticket_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            try:
                rel_path = ticket_file.relative_to(self._repo_root).as_posix()
            except ValueError:
                rel_path = ticket_file.as_posix()
        except OSError as exc:
            logger.warning("autonomy_gate 人审工单落盘失败（判定仍生效）: %r", exc)
        return rel_path

    def _write_alert(self, verdict: GateVerdict, session_context: dict[str, Any] | None) -> None:
        """immutable_core → 物理拦截 + 告警留痕（持久句柄逐行 flush；IO 失败不阻断拦截）."""
        try:
            record = {
                "schema_version": SCHEMA_VERSION,
                "event_id": verdict.verdict_id,
                "timestamp": verdict.timestamp,
                "source_domain": SOURCE_DOMAIN,
                "event_type": "autonomy_gate_immutable_alert",
                "threat_category": "immutable_core_violation",
                "severity": "critical",
                "session_id": verdict.session_id,
                "session_context": session_context or {},
                "verdict": verdict.to_dict(),
            }
            if self._alerts_handle is None:
                self._alerts_path.parent.mkdir(parents=True, exist_ok=True)
                self._alerts_handle = open(self._alerts_path, "a", encoding="utf-8", buffering=1)
            self._alerts_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._alerts_handle.flush()
        except OSError as exc:
            logger.warning("autonomy_gate immutable 告警落盘失败（拦截仍生效）: %r", exc)

    def _audit_write(self, line: str) -> None:
        """审计 jsonl 追加（持久句柄 + 逐行 flush；IO 失败不阻断判定）."""
        try:
            if self._audit_handle is None:
                self._audit_path.parent.mkdir(parents=True, exist_ok=True)
                self._audit_handle = open(self._audit_path, "a", encoding="utf-8", buffering=1)
            self._audit_handle.write(line)
            self._audit_handle.flush()
        except OSError as exc:
            logger.warning("autonomy_gate 审计留痕写入失败（判定仍生效）: %r", exc)


_default_gate: AutonomyBoundaryGate | None = None


def get_default_gate() -> AutonomyBoundaryGate:
    """获取默认 gate 单例（默认注册表 + 仓根 .runtime/ 留痕）."""
    global _default_gate
    if _default_gate is None:
        _default_gate = AutonomyBoundaryGate()
    return _default_gate


def check_write_permission(
    action_id: str,
    target_path_or_resource: str,
    session_context: dict[str, Any] | None = None,
) -> GateVerdict:
    """模块级便捷入口：默认 gate 的写操作三分类判定."""
    return get_default_gate().check_write_permission(
        action_id, target_path_or_resource, session_context
    )


__all__ = [
    "SCHEMA_VERSION",
    "SOURCE_DOMAIN",
    "AutonomyBoundaryGate",
    "AutonomyLayer",
    "GateDecision",
    "GateVerdict",
    "check_write_permission",
    "get_default_gate",
]
