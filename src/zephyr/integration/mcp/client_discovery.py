# [BLUEPRINT] MOD-INF-058 | docs/03_modules/MOD-INF-058/ | §
# [MODULE] zephyr.integration.mcp.client_discovery
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp(tool_contracts.yaml); (lazy) zephyr.infrastructure.system_telemetry.facade(MetricsFacade); zephyr.shared.io.paths(REPO_ROOT)
# [CONSUMERS] tests/infrastructure/test_mcp_client_discovery.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 传输层仅 localhost HTTP+SSE(STDIO/非 localhost/非 http(s) 一律 fail-closed 拒收); 发现即校验——未知工具默认拒绝(即使名字像只读),safety_level M/H 必须契约命中才放行; 工具注册执行 MCP-Scan 剥离指令性语言; diff 结果必 emit 遥测; 漂移消除自动清状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TransportRejectedError(ZA-IG-0019); ToolContractError(ZA-IG-0020); 错误消息零 session_id
# [TESTS] tests/infrastructure/test_mcp_client_discovery.py
# [A_module] module_id=MOD-INF-058 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClientDiscovery — MCP Client 动态发现 + 契约漂移对账（MOD-INF-058）.

设计真源：10号文 §3.2/§3.2.2/§4 Phase 2 步骤 2.1/2.2：

- 传输层约束（§3.2.2）：仅 localhost HTTP+SSE，STDIO 禁用；非 localhost、
  非 http(s) 协议一律 TransportRejectedError（fail-closed）。
- 发现即校验（步骤 2.1）：连接后经 MCPTransport.list_tools() 拉取工具目录，
  与 tool_contracts.yaml（MOD-INF-013 契约 SSoT）双向 diff——未知工具告警 +
  ToolVerdict.DENIED_UNKNOWN 默认拒绝（即使名字像只读）；契约中消失的工具记
  missing；safety_level M/H 以契约命中为唯一放行凭据。
- MCP-Scan（步骤 2.1）：工具注册时按句扫描描述，剥离指令性语言
  （you must/ignore previous/你必须/务必/系统提示 等保守模式），剥离片段留痕；
  declarative 描述不碰（裸「禁止/always/never」类安全说明刻意不收，防误损）。
- 漂移对账入遥测（步骤 2.2）：diff 结果 emit mcp.contract_drift.* 指标
  （detected/unknown_tools/missing_tools/duration_hours/escalated，tag server_id），
  默认 sink = MOD-INF-015 MetricsFacade（metrics ring，telemetry.metrics_snapshot
  子系统同源通道）；漂移 first_seen 持久化 drift_state.json（原子写），
  持续 >24h 升级告警（escalated=1 + logger.warning），漂移消除自动清记录。

传输层协议注入：本件不含真实 HTTP+SSE 实现（设计声明协议注入；业务侧 MCP
Server 规划落地时由调用方实现 MCPTransport 协议）。
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final, Protocol, runtime_checkable
from urllib.parse import urlparse

import yaml

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

DEFAULT_CONTRACT_PATH: Final[Path] = Path(__file__).resolve().parent / "tool_contracts.yaml"
DEFAULT_STATE_PATH: Final[Path] = REPO_ROOT / ".runtime" / "mcp_client_discovery" / "drift_state.json"

# 漂移指标名（步骤 2.2，tag server_id 随指标走）
METRIC_DRIFT_DETECTED: Final[str] = "mcp.contract_drift.detected"
METRIC_DRIFT_UNKNOWN: Final[str] = "mcp.contract_drift.unknown_tools"
METRIC_DRIFT_MISSING: Final[str] = "mcp.contract_drift.missing_tools"
METRIC_DRIFT_DURATION: Final[str] = "mcp.contract_drift.duration_hours"
METRIC_DRIFT_ESCALATED: Final[str] = "mcp.contract_drift.escalated"

ESCALATION_THRESHOLD_HOURS: Final[float] = 24.0

_ALLOWED_TRANSPORT: Final[str] = "http_sse"
_LOCALHOST_HOSTS: Final[frozenset[str]] = frozenset({"127.0.0.1", "localhost", "::1"})


class TransportRejectedError(Exception):
    """MCP server 连接配置被拒（STDIO 禁用/非 localhost/非 http(s)）——fail-closed."""

    error_code = "ZA-IG-0019"


class ToolContractError(Exception):
    """MCP 工具契约加载失败（文件缺失/不可读/非法结构）——fail-closed."""

    error_code = "ZA-IG-0020"


class ToolVerdict(str, Enum):
    """单工具放行判决（发现即校验）."""

    ALLOWED = "ALLOWED"
    DENIED_UNKNOWN = "DENIED_UNKNOWN"


@runtime_checkable
class MCPTransport(Protocol):
    """MCP 传输层协议（协议注入；真实 HTTP+SSE 实现由调用方落地）."""

    def list_tools(self) -> list[dict]: ...


@dataclass(frozen=True)
class ServerConnectionConfig:
    """MCP server 连接配置（校验对象）."""

    server_id: str
    transport: str  # 仅 http_sse 合法（STDIO 禁用）
    url: str  # 仅 localhost http(s) 合法


@dataclass(frozen=True)
class SanitizedDescription:
    """MCP-Scan 剥离结果：净化文本 + 被剥离片段留痕."""

    text: str
    stripped: tuple[str, ...] = ()


@dataclass(frozen=True)
class SanitizedTool:
    """注册时完成 MCP-Scan 的工具（描述已剥离指令性语言）."""

    name: str
    description: str
    original_description: str
    stripped: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiscoveryReport:
    """一次动态发现的 diff 报告（unknown/missing 双向，确定性排序输出）."""

    server_id: str
    discovered: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    verdicts: dict[str, ToolVerdict] = field(default_factory=dict)
    safety_levels: dict[str, str] = field(default_factory=dict)
    sanitized_tools: dict[str, SanitizedTool] = field(default_factory=dict)
    stripped_count: int = 0
    has_drift: bool = False
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "server_id": self.server_id,
            "timestamp": self.timestamp,
            "has_drift": self.has_drift,
            "discovered": list(self.discovered),
            "unknown": list(self.unknown),
            "missing": list(self.missing),
            "verdicts": {name: verdict.value for name, verdict in self.verdicts.items()},
            "safety_levels": dict(self.safety_levels),
            "sanitized_tools": {
                name: {
                    "description": tool.description,
                    "original_description": tool.original_description,
                    "stripped": list(tool.stripped),
                }
                for name, tool in self.sanitized_tools.items()
            },
            "stripped_count": self.stripped_count,
        }


class ToolContractIndex:
    """tool_contracts.yaml 只读索引（契约 SSoT 消费面）."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def tools_for(self, server_id: str) -> dict[str, dict[str, Any]]:
        """按 server_id 取契约工具表（name → 契约条目）；未知 server 返回空表."""
        section = self._data.get(server_id)
        if not isinstance(section, dict):
            return {}
        tools = section.get("tools") or []
        return {str(tool["name"]): tool for tool in tools if isinstance(tool, dict) and tool.get("name")}


# ── MCP-Scan 指令性语言剥离（保守模式集；declarative 安全说明不碰） ──
_IMPERATIVE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\byou\s+must\b",
        r"\byou\s+should\b",
        r"\byou\s+shall\b",
        r"\byou\s+are\s+(required|supposed|expected)\b",
        r"\b(must|should)\s+(call|use|invoke|run)\s+(this|the)\s+tool\b",
        r"\balways\s+(call|use|invoke)\b",
        r"\bnever\s+(skip|ignore|forget)\b",
        r"\bignore\s+(all\s+)?(previous|prior|above)\b",
        r"\bdisregard\s+(all\s+)?(previous|prior|above)\b",
        r"\bforget\s+(all\s+)?(previous|prior)\b",
        r"\bsystem\s+prompt\b",
        r"\bdo\s+not\s+tell\b",
        r"你必须",
        r"你务必",
        r"务必(调用|使用|执行|遵守)",
        r"请(务必)?忽略",
        r"忽略(之前|以上|先前|所有)(指令|指示|提示)",
        r"系统提示",
    )
)

_SENTENCE_SPLIT: Final[re.Pattern[str]] = re.compile(r"((?<=[。！？.!?])\s*|\n+)")


def sanitize_tool_description(text: str) -> SanitizedDescription:
    """MCP-Scan：按句剥离指令性语言，剥离片段留痕；declarative 描述原文保留."""
    if not text:
        return SanitizedDescription(text="", stripped=())
    parts = _SENTENCE_SPLIT.split(text)
    kept: list[str] = []
    stripped: list[str] = []
    for idx in range(0, len(parts), 2):
        sentence = parts[idx]
        separator = parts[idx + 1] if idx + 1 < len(parts) else ""
        if sentence and any(pattern.search(sentence) for pattern in _IMPERATIVE_PATTERNS):
            stripped.append(sentence.strip())
        else:
            kept.append(sentence + separator)
    return SanitizedDescription(text="".join(kept), stripped=tuple(stripped))


def validate_connection_config(config: ServerConnectionConfig) -> None:
    """传输层校验（§3.2.2）：仅 localhost HTTP+SSE，其余一律 fail-closed 拒收."""
    transport = str(config.transport or "").strip().lower()
    if transport != _ALLOWED_TRANSPORT:
        raise TransportRejectedError(f"MCP 传输类型被拒（仅允许 localhost HTTP+SSE，STDIO 禁用）: {transport!r}")
    parsed = urlparse(str(config.url or ""))
    if parsed.scheme not in ("http", "https"):
        raise TransportRejectedError(f"MCP server URL 协议被拒（仅 http/https）: {config.url!r}")
    host = (parsed.hostname or "").strip().lower()
    if host not in _LOCALHOST_HOSTS:
        raise TransportRejectedError(f"MCP server URL 主机被拒（仅 localhost）: {config.url!r}")


class _MetricsFacadeSink:
    """默认遥测 sink：MOD-INF-015 MetricsFacade gauge → metrics ring（同源 metrics_snapshot）."""

    def __init__(self, module_id: str = "MOD-INF-058") -> None:
        from zephyr.infrastructure.system_telemetry.facade import MetricsFacade

        self._metrics = MetricsFacade(module_id)

    def emit(self, metric_name: str, value: float, tags: dict) -> None:
        self._metrics.gauge(metric_name, value, **tags)


class ClientDiscovery:
    """MCP Client 动态发现引擎：发现即校验 + 漂移对账入遥测."""

    def __init__(
        self,
        contract_path: str | Path = DEFAULT_CONTRACT_PATH,
        state_path: str | Path = DEFAULT_STATE_PATH,
        telemetry_sink: Any = None,
        clock: Any = None,
    ) -> None:
        self._contract_path = Path(contract_path)
        self._state_path = Path(state_path)
        self._sink = telemetry_sink if telemetry_sink is not None else _MetricsFacadeSink()
        self._clock = clock if clock is not None else (lambda: datetime.now(UTC))
        self._contract_index: ToolContractIndex | None = None

    @property
    def contract_index(self) -> ToolContractIndex:
        """契约索引（惰性加载；缺失/非法即 ToolContractError fail-closed）."""
        if self._contract_index is None:
            self._contract_index = ToolContractIndex(self._load_contract())
        return self._contract_index

    def _load_contract(self) -> dict[str, Any]:
        if not self._contract_path.exists():
            raise ToolContractError(f"MCP 工具契约文件缺失: {self._contract_path}")
        try:
            data = yaml.safe_load(self._contract_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ToolContractError(f"MCP 工具契约文件不可读: {self._contract_path}（{exc!r}）") from exc
        if not isinstance(data, dict):
            raise ToolContractError(f"MCP 工具契约顶层须为 dict: {self._contract_path}（{type(data)!r}）")
        return data

    # ── 发现即校验 + diff ──────────────────────────────────────

    def discover(self, config: ServerConnectionConfig, transport: MCPTransport) -> DiscoveryReport:
        """连接发现 → MCP-Scan 注册 → 契约 diff → 遥测 emit（fail-closed 未知默认拒）."""
        validate_connection_config(config)
        contract_tools = self.contract_index.tools_for(config.server_id)
        raw_tools = transport.list_tools()
        discovered: list[str] = []
        verdicts: dict[str, ToolVerdict] = {}
        safety_levels: dict[str, str] = {}
        sanitized_tools: dict[str, SanitizedTool] = {}
        stripped_count = 0
        for raw in raw_tools:
            name = str((raw or {}).get("name", ""))
            if not name:
                continue
            discovered.append(name)
            original = str((raw or {}).get("description", "") or "")
            scan = sanitize_tool_description(original)
            stripped_count += len(scan.stripped)
            sanitized_tools[name] = SanitizedTool(
                name=name,
                description=scan.text,
                original_description=original,
                stripped=scan.stripped,
            )
            hit = contract_tools.get(name)
            if hit is None:
                verdicts[name] = ToolVerdict.DENIED_UNKNOWN
                logger.warning(
                    "MCP 发现未知工具，默认拒绝（发现即校验）: server=%s tool=%s",
                    config.server_id,
                    name,
                )
            else:
                # safety_level 以契约为准：M/H 契约治理内才放行
                verdicts[name] = ToolVerdict.ALLOWED
                safety_levels[name] = str(hit.get("safety_level", ""))
        discovered_set = set(discovered)
        unknown = tuple(sorted(name for name, verdict in verdicts.items() if verdict is ToolVerdict.DENIED_UNKNOWN))
        missing = tuple(sorted(name for name in contract_tools if name not in discovered_set))
        report = DiscoveryReport(
            server_id=config.server_id,
            discovered=tuple(discovered),
            unknown=unknown,
            missing=missing,
            verdicts=verdicts,
            safety_levels=safety_levels,
            sanitized_tools=sanitized_tools,
            stripped_count=stripped_count,
            has_drift=bool(unknown or missing),
            timestamp=self._clock().isoformat(),
        )
        self._emit_drift_metrics(report)
        return report

    # ── 漂移对账入遥测（步骤 2.2） ─────────────────────────────

    def _emit_drift_metrics(self, report: DiscoveryReport) -> None:
        tags = {"server_id": report.server_id}
        self._emit(METRIC_DRIFT_DETECTED, 1.0 if report.has_drift else 0.0, tags)
        self._emit(METRIC_DRIFT_UNKNOWN, float(len(report.unknown)), tags)
        self._emit(METRIC_DRIFT_MISSING, float(len(report.missing)), tags)
        state = self._load_state()
        now = self._clock()
        if report.has_drift:
            entry = state.get(report.server_id)
            if isinstance(entry, dict) and entry.get("first_seen"):
                first_seen = self._parse_timestamp(entry["first_seen"]) or now
            else:
                first_seen = now
                state[report.server_id] = {"first_seen": now.isoformat()}
            duration_hours = max(0.0, (now - first_seen).total_seconds() / 3600.0)
            escalated = 1.0 if duration_hours >= ESCALATION_THRESHOLD_HOURS else 0.0
            self._emit(METRIC_DRIFT_DURATION, duration_hours, tags)
            self._emit(METRIC_DRIFT_ESCALATED, escalated, tags)
            if escalated:
                logger.warning(
                    "MCP 契约漂移持续超 %.0fh，升级告警: server=%s duration=%.1fh",
                    ESCALATION_THRESHOLD_HOURS,
                    report.server_id,
                    duration_hours,
                )
        else:
            # 漂移消除 → 状态记录清除
            state.pop(report.server_id, None)
        self._save_state(state)

    def _emit(self, metric_name: str, value: float, tags: dict) -> None:
        try:
            self._sink.emit(metric_name, value, dict(tags))
        except Exception as exc:  # noqa: BLE001 — 遥测失败不阻断发现主流程
            logger.warning("MCP 漂移指标 emit 失败（发现结果仍生效）: %r", exc)

    @staticmethod
    def _parse_timestamp(raw: Any) -> datetime | None:
        try:
            parsed = datetime.fromisoformat(str(raw))
        except (TypeError, ValueError):
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed

    # ── 漂移状态持久化（原子写） ───────────────────────────────

    def _load_state(self) -> dict[str, Any]:
        if not self._state_path.exists():
            return {}
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("MCP 漂移状态文件不可读，按空态处理: %r", exc)
            return {}
        return raw if isinstance(raw, dict) else {}

    def _save_state(self, state: dict[str, Any]) -> None:
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._state_path.with_suffix(self._state_path.suffix + f".{os.getpid()}.tmp")
            tmp_path.write_text(
                json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.replace(tmp_path, self._state_path)
        except OSError as exc:
            logger.warning("MCP 漂移状态落盘失败（遥测仍已 emit）: %r", exc)


__all__ = [
    "DEFAULT_CONTRACT_PATH",
    "DEFAULT_STATE_PATH",
    "ESCALATION_THRESHOLD_HOURS",
    "METRIC_DRIFT_DETECTED",
    "METRIC_DRIFT_DURATION",
    "METRIC_DRIFT_ESCALATED",
    "METRIC_DRIFT_MISSING",
    "METRIC_DRIFT_UNKNOWN",
    "ClientDiscovery",
    "DiscoveryReport",
    "MCPTransport",
    "SanitizedDescription",
    "SanitizedTool",
    "ServerConnectionConfig",
    "ToolContractError",
    "ToolContractIndex",
    "ToolVerdict",
    "TransportRejectedError",
    "sanitize_tool_description",
    "validate_connection_config",
]
