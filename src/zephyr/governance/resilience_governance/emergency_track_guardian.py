# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.emergency_track_guardian
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] PyYAML(config/emergency_track.yaml);
#   zephyr.shared.utils.time_utils(now_utc); zephyr.shared.io.paths(REPO_ROOT);
#   zephyr.autonomy_core.kill_switch_orchestrator(get_orchestrator, 延迟解析——唯一保命动作入口);
#   zephyr.governance.resilience_governance.last_resort_watchdog(get_last_resort_watchdog, 延迟解析)
# [CONSUMERS] zephyr.trading.process_reaper(reap 尾部一次评估, OS 托管 10min 心跳=自动触发);
#   zephyr.trading.boot_hooks(A3 同款启动自检); tests/governance/resilience/test_emergency_track_guardian.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 保命动作唯一入口=KillSwitchOrchestrator.route_incident（本件零 import 任何一套
#   KillSwitch 本体，BRK-064 入口收敛）; 判据缺证据不动作（unknown 腿≠失效腿，宁漏不误熔断）;
#   本件不持任何开关状态（每次实时查/实时判，本件故障则各开关独立可用）;
#   复位不在本件职责（reset 须 approver 非空=Owner 批准语义）; 每次 evaluate 必留痕;
#   evaluate() 永不抛（宿主是收割器/启动链，反噬宿主=保命链自己制造事故）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EmergencyTrackConfigError(配置解析失败/未知键/阈值越界/腿清单非法);
#   evaluate() 永不抛——配置/探针/动作三类失败收入 verdict.errors 并 logger.error 出声
# [TESTS] tests/governance/resilience/test_emergency_track_guardian.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""emergency_track_guardian — 应急保命轨最小可运行实体（CC_07 / BRK-078）.

治什么：depgraph `decision_tracks` 早已登记 `emergency`（应急保命轨, priority=4,
activation_condition="所有模型/策略/信号失效时"），但 `decision_nodes` 213 行全 planned
（BRK-023）→ 该轨**有登记、有优先级、零节点**。叠加 BRK-004（五域编排器 boot 已挂但生产链
无人下单）+ BRK-005（last_resort 旗标只点亮、无人读）= 真出事时既判不出也降不下。

本件只做该轨的**最小可运行实体**（完整决策图是新建类大件，施工包见
docs/_working/fullflow_campaign/lanes/wiresafe_BRK-078_construction_pack.md）：

1. 判据（activation_condition 的机检形式）：三腿心跳 = 信号 / 策略 / 模型-决策编排。
   只有 **stale（文件在但过期）** 计入失效；**unknown（文件缺失/不可读）不计入**——
   未启动不等于已失效，这是验收规范 §6"crisis 误报代价"攻击面的防线。
2. 动作（保命）：`get_orchestrator().route_incident(incident_kind, reason)` —— 系统级总开关，
   域级一致生效由编排器传播保障。本件不 import 任何一套 KillSwitch 本体（入口唯一）。
3. 读 last_resort_watchdog 旗标：升级协议末端（L4 且重试耗尽）已点灯的，本件把它当作
   一条失效腿参与判定——补上 BRK-005 缺的"消费端"（旗标此前只写不读 = 静默兜底）。
4. 危机快照（BRK-072 消费端）：读 `crisis_drill_monthly.py` 最新 casualty_report 的新鲜度，
   逾期只报哨兵 breach（加重证据），不参与熔断必要条件。

四要素对齐（宪法 §9.3）：**自动触发**=复用已注册 OS 计划任务 process_reaper 的 10min 心跳
（本件零新建 cron/Timer/sleep-loop，亦**无 manual CLI/argparse 面**——MANUAL-ONLY-PERMANENT
门禁要求永久件必须事件驱动，本件唯一入口是 `run_emergency_track_check()`，由 reaper 调用）；
自动运行=reaper 每轮尾部跑一次并落审计（`.runtime/audit/emergency_track.jsonl`）；
自动维护=判据/阈值/窗口真源在 config/emergency_track.yaml（缺键即硬错，禁静默降级）；
自动关闭=one-shot 评估，本件无常驻线程。人工核查用 `python -m zephyr.trading.process_reaper
--status`（打印本轨 state/确认数/水位实测）。
# [ALGO_FLOW]
输入: config/emergency_track.yaml + 三腿心跳文件 mtime + last_resort 旗标 + 最新危机快照
输出: .runtime/audit/emergency_track.jsonl 每评一行；确认失效 → KillSwitchOrchestrator
      系统级拉闸（并同批落 orchestration 审计）；证据不足 → state=insufficient_evidence 只出声
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

CONFIG_RELPATH: Final[str] = "config/emergency_track.yaml"
DEFAULT_AUDIT_PATH: Final[str] = ".runtime/audit/emergency_track.jsonl"
DEFAULT_LEGS: Final[tuple[tuple[str, str, int], ...]] = (
    ("signal", "tmp/tick_subscriber_biz.heartbeat", 600),
    ("strategy", "tmp/live_strategy_biz.heartbeat", 600),
    ("model", "tmp/scheduler.heartbeat", 900),
)
DEFAULT_CONFIRMATIONS: Final[int] = 2
#: "曾经活着"的证据视界：心跳文件比这更老 = 未运行（unknown），不是失效（stale）。
#: 缺了这条就会在开盘前把昨天的旧心跳当成"三腿齐失效"而误熔断。
DEFAULT_EVIDENCE_HORIZON_S: Final[int] = 4 * 3600
DEFAULT_INCIDENT_KIND: Final[str] = "global"

STATE_NORMAL: Final[str] = "normal"
STATE_ARMING: Final[str] = "arming"
STATE_ACTIVATED: Final[str] = "activated"
STATE_INSUFFICIENT: Final[str] = "insufficient_evidence"
STATE_DISABLED: Final[str] = "disabled"
STATE_CONFIG_ERROR: Final[str] = "config_error"
STATE_OUTSIDE_WINDOW: Final[str] = "outside_active_window"

_LEG_ALIVE: Final[str] = "alive"
_LEG_STALE: Final[str] = "stale"
_LEG_UNKNOWN: Final[str] = "unknown"

#: 允许出现在 config/emergency_track.yaml 顶层的键（未知键=硬错，防拼写漂移静默不生效）
KNOWN_TOP_KEYS: Final[frozenset[str]] = frozenset(
    {"enabled", "legs", "consecutive_confirmations", "count_last_resort_as_stale_leg",
     "action", "crisis_snapshot", "audit_path", "active_window", "evidence_horizon_seconds"}
)
_KNOWN_LEG_KEYS: Final[frozenset[str]] = frozenset({"id", "desc_zh", "path", "max_stale_seconds"})
_KNOWN_ACTION_KEYS: Final[frozenset[str]] = frozenset({"incident_kind", "reason_zh"})
_KNOWN_WINDOW_KEYS: Final[frozenset[str]] = frozenset({"enabled", "start_hhmm", "end_hhmm", "timezone"})
_KNOWN_SNAPSHOT_KEYS: Final[frozenset[str]] = frozenset({"dir", "report_file", "max_age_days"})


def _hhmm_to_min(raw: str) -> int:
    """'09:30' → 分钟数（窗口边界真源在 YAML，禁代码里散落魔数）."""
    parts = raw.strip().split(":")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise EmergencyTrackConfigError(f"active_window 时间须为 HH:MM，实得 {raw!r}")
    minutes = int(parts[0]) * 60 + int(parts[1])
    if not 0 <= minutes <= 24 * 60:
        raise EmergencyTrackConfigError(f"active_window 时间越界: {raw!r}")
    return minutes


class EmergencyTrackConfigError(ValueError):
    """应急保命轨配置非法（解析失败/未知键/阈值越界）——fail-closed。"""


@dataclass(frozen=True)
class TrackLeg:
    """一条失效判据腿的配置口径."""

    leg_id: str
    path: str
    max_stale_seconds: int


@dataclass(frozen=True)
class EmergencyTrackConfig:
    """运行配置（冻结）。缺文件=缺省；解析失败/未知键/越界=硬错."""

    enabled: bool = True
    legs: tuple[TrackLeg, ...] = tuple(TrackLeg(i, p, s) for i, p, s in DEFAULT_LEGS)
    consecutive_confirmations: int = DEFAULT_CONFIRMATIONS
    count_last_resort_as_stale_leg: bool = True
    incident_kind: str = DEFAULT_INCIDENT_KIND
    action_reason: str = "应急保命轨触发：模型/策略/信号三腿全部确认失效"
    crisis_dir: str = "data/backtest_artifacts/drills"
    crisis_report_file: str = "casualty_report.json"
    crisis_max_age_days: int = 60
    audit_path: str = DEFAULT_AUDIT_PATH
    window_enabled: bool = True
    window_start_min: int = 9 * 60
    window_end_min: int = 15 * 60 + 30
    window_tz: str = "Asia/Shanghai"
    evidence_horizon_seconds: int = DEFAULT_EVIDENCE_HORIZON_S


@dataclass(frozen=True)
class LegReading:
    """单腿实测读数（status ∈ alive/stale/unknown）."""

    leg_id: str
    path: str
    status: str
    age_seconds: float | None
    max_stale_seconds: int
    detail: str = ""


@dataclass(frozen=True)
class EmergencyTrackVerdict:
    """单次评估裁定（不可变；动作失败收入 errors）."""

    ts: str
    state: str
    legs: tuple[LegReading, ...]
    stale_count: int = 0
    unknown_count: int = 0
    confirmations: int = 0
    required_confirmations: int = DEFAULT_CONFIRMATIONS
    last_resort_active: bool = False
    action: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    breaches: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "state": self.state,
            "stale_count": self.stale_count,
            "unknown_count": self.unknown_count,
            "confirmations": self.confirmations,
            "required_confirmations": self.required_confirmations,
            "last_resort_active": self.last_resort_active,
            "errors": dict(self.errors),
            "breaches": list(self.breaches),
            "action": dict(self.action),
            "legs": [
                {
                    "leg_id": r.leg_id,
                    "path": r.path,
                    "status": r.status,
                    "age_seconds": r.age_seconds,
                    "max_stale_seconds": r.max_stale_seconds,
                    "detail": r.detail,
                }
                for r in self.legs
            ],
        }


def _parse_legs(raw: Any) -> tuple[TrackLeg, ...]:
    """腿清单解析（缺省/空表=用内置三腿；非法=硬错）."""
    if raw is None:
        return EmergencyTrackConfig().legs
    if not isinstance(raw, list) or not raw:
        raise EmergencyTrackConfigError(f"legs 须为非空列表，实得 {type(raw).__name__}")
    legs: list[TrackLeg] = []
    for item in raw:
        if not isinstance(item, dict):
            raise EmergencyTrackConfigError(f"legs 条目须为映射: {item!r}")
        unknown = set(item) - _KNOWN_LEG_KEYS
        if unknown:
            raise EmergencyTrackConfigError(f"legs 含未知键 {sorted(unknown)}（拼写漂移防静默）")
        max_age = int(item.get("max_stale_seconds", 600))
        if max_age <= 0:
            raise EmergencyTrackConfigError(f"max_stale_seconds 须为正整数，实得 {max_age}")
        legs.append(
            TrackLeg(
                leg_id=str(item.get("id", "")).strip(),
                path=str(item.get("path", "")).strip(),
                max_stale_seconds=max_age,
            )
        )
    if any(not leg.leg_id or not leg.path for leg in legs):
        raise EmergencyTrackConfigError("legs 条目缺 id 或 path")
    return tuple(legs)


def _parse_config_root(loaded: dict[str, Any], defaults: EmergencyTrackConfig) -> EmergencyTrackConfig:
    """已解析映射 → 冻结配置（未知键=硬错，方向与 crisis_gate 同族）."""
    unknown = set(loaded) - KNOWN_TOP_KEYS
    if unknown:
        raise EmergencyTrackConfigError(f"{CONFIG_RELPATH} 含未知键 {sorted(unknown)}（拼写漂移防静默）")
    action = loaded.get("action") or {}
    if not isinstance(action, dict):
        raise EmergencyTrackConfigError("action 须为映射")
    unknown_action = set(action) - _KNOWN_ACTION_KEYS
    if unknown_action:
        raise EmergencyTrackConfigError(f"action 含未知键 {sorted(unknown_action)}")
    snap = loaded.get("crisis_snapshot") or {}
    if not isinstance(snap, dict):
        raise EmergencyTrackConfigError("crisis_snapshot 须为映射")
    unknown_snap = set(snap) - _KNOWN_SNAPSHOT_KEYS
    if unknown_snap:
        raise EmergencyTrackConfigError(f"crisis_snapshot 含未知键 {sorted(unknown_snap)}")
    window = loaded.get("active_window") or {}
    if not isinstance(window, dict):
        raise EmergencyTrackConfigError("active_window 须为映射")
    unknown_window = set(window) - _KNOWN_WINDOW_KEYS
    if unknown_window:
        raise EmergencyTrackConfigError(f"active_window 含未知键 {sorted(unknown_window)}")
    confirmations = int(loaded.get("consecutive_confirmations", defaults.consecutive_confirmations))
    if confirmations < 1:
        raise EmergencyTrackConfigError(f"consecutive_confirmations 须 ≥1，实得 {confirmations}")
    max_age_days = int(snap.get("max_age_days", defaults.crisis_max_age_days))
    if max_age_days <= 0:
        raise EmergencyTrackConfigError(f"crisis_snapshot.max_age_days 须为正，实得 {max_age_days}")
    return EmergencyTrackConfig(
        enabled=bool(loaded.get("enabled", defaults.enabled)),
        legs=_parse_legs(loaded.get("legs")),
        consecutive_confirmations=confirmations,
        count_last_resort_as_stale_leg=bool(
            loaded.get("count_last_resort_as_stale_leg", defaults.count_last_resort_as_stale_leg)
        ),
        incident_kind=str(action.get("incident_kind", defaults.incident_kind)),
        action_reason=str(action.get("reason_zh", defaults.action_reason)),
        crisis_dir=str(snap.get("dir", defaults.crisis_dir)),
        crisis_report_file=str(snap.get("report_file", defaults.crisis_report_file)),
        crisis_max_age_days=max_age_days,
        audit_path=str(loaded.get("audit_path", defaults.audit_path)),
        window_enabled=bool(window.get("enabled", defaults.window_enabled)),
        window_start_min=_hhmm_to_min(str(window.get("start_hhmm", "09:00"))),
        window_end_min=_hhmm_to_min(str(window.get("end_hhmm", "15:30"))),
        window_tz=str(window.get("timezone", defaults.window_tz)),
        evidence_horizon_seconds=_positive_int(
            loaded.get("evidence_horizon_seconds", defaults.evidence_horizon_seconds),
            "evidence_horizon_seconds",
        ),
    )


def _positive_int(raw: object, name: str) -> int:
    value = int(raw)  # type: ignore[arg-type]
    if value <= 0:
        raise EmergencyTrackConfigError(f"{name} 须为正整数，实得 {value}")
    return value


def load_emergency_track_config(
    path: str | Path | None = None, repo_root: Path = REPO_ROOT
) -> EmergencyTrackConfig:
    """读配置：缺文件=内置缺省；解析失败/根节点非映射/未知键=EmergencyTrackConfigError."""
    cfg_path = Path(path) if path is not None else repo_root / CONFIG_RELPATH
    if not cfg_path.exists():
        logger.warning("emergency_track 配置缺失 %s——按内置缺省运行（三腿+不动作开关=true）", cfg_path)
        return EmergencyTrackConfig()
    try:
        loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise EmergencyTrackConfigError(f"emergency_track 配置解析失败 {cfg_path}: {exc}") from exc
    if loaded is None:
        return EmergencyTrackConfig()
    if not isinstance(loaded, dict):
        raise EmergencyTrackConfigError(f"emergency_track 配置根节点须为映射: {cfg_path}")
    return _parse_config_root(loaded, EmergencyTrackConfig())


class EmergencyTrackGuardian:
    """应急保命轨守门人（只判定+下单一笔动作，不持开关状态）.

    用法::

        verdict = EmergencyTrackGuardian().evaluate()
        if verdict.state == "activated":
            ...  # 已系统级拉闸，复位须 Owner 批准（本件无复位面）

    ``orchestrator_provider`` / ``last_resort_provider`` 为注入位（测试与非 AutoRuntime
    宿主可用）；缺省延迟解析生产单例——注入缺失（import 失败）不静默通过：记 errors
    且 state 降级为 arming（无动作能力=不出手，但必须出声）。
    """

    def __init__(
        self,
        config: EmergencyTrackConfig | None = None,
        *,
        repo_root: Path = REPO_ROOT,
        config_path: str | Path | None = None,
        now_fn: Callable[[], Any] = now_utc,
        orchestrator_provider: Callable[[], Any] | None = None,
        last_resort_provider: Callable[[], Any] | None = None,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._now_fn = now_fn
        self._confirmations = 0
        self._orchestrator_provider = orchestrator_provider
        self._last_resort_provider = last_resort_provider
        self.config_error: str = ""
        if config is not None:
            self._config = config
        else:
            try:
                self._config = load_emergency_track_config(config_path, repo_root=self._repo_root)
            except EmergencyTrackConfigError as exc:
                # 配置读不懂 = 保命轨自身失能：不静默降级为缺省值（那会让坏配置永远不被发现）
                self._config = EmergencyTrackConfig(enabled=False)
                self.config_error = str(exc)
                logger.error("emergency_track 配置非法，保命轨失能（不动作+每次评估出声）: %s", exc)

    @property
    def config(self) -> EmergencyTrackConfig:
        return self._config

    @property
    def confirmations(self) -> int:
        return self._confirmations

    # ── 探针 ────────────────────────────────────────────────

    def read_legs(self) -> tuple[LegReading, ...]:
        """逐腿实测心跳年龄（文件缺失/不可读=unknown，不计入失效）."""
        now = self._now_fn()
        readings: list[LegReading] = []
        for leg in self._config.legs:
            target = self._repo_root / leg.path
            try:
                mtime = target.stat().st_mtime
            except OSError as exc:
                readings.append(
                    LegReading(leg.leg_id, leg.path, _LEG_UNKNOWN, None, leg.max_stale_seconds,
                               f"心跳文件不可读: {exc.__class__.__name__}")
                )
                continue
            age = max(0.0, now.timestamp() - mtime)
            if age <= leg.max_stale_seconds:
                status, detail = _LEG_ALIVE, ""
            elif age > self._config.evidence_horizon_seconds:
                status = _LEG_UNKNOWN
                detail = (f"心跳已 {round(age / 3600.0, 1)}h 未更新，超证据视界 "
                          f"{self._config.evidence_horizon_seconds}s——按未运行处理，不计入失效")
            else:
                status, detail = _LEG_STALE, ""
            readings.append(LegReading(leg.leg_id, leg.path, status, round(age, 1),
                                       leg.max_stale_seconds, detail))
        return tuple(readings)

    def _last_resort_active(self) -> tuple[bool, str]:
        """读终极逃生舱旗标（BRK-005 消费端）。失败=保守按 False 但记 errors+出声."""
        if self._last_resort_provider is not None:
            try:
                return bool(self._last_resort_provider().active), ""
            except Exception as exc:  # noqa: BLE001 — 探针不炸评估
                return False, f"last_resort 探针失败: {exc!r}"
        try:
            from zephyr.governance.resilience_governance.last_resort_watchdog import (
                get_last_resort_watchdog,
            )

            return bool(get_last_resort_watchdog().active), ""
        except Exception as exc:  # noqa: BLE001
            return False, f"last_resort 导入失败: {exc!r}"

    def crisis_snapshot_age_days(self) -> float | None:
        """最新危机快照年龄（天）；无快照/不可读=None（只作告警证据，不参与熔断）."""
        base = self._repo_root / self._config.crisis_dir
        try:
            runs = sorted(
                (d for d in base.iterdir() if (d / self._config.crisis_report_file).exists()),
                key=lambda d: d.stat().st_mtime,
            )
        except OSError as exc:
            logger.warning("危机快照目录不可读 %s: %s", base, exc)
            return None
        if not runs:
            return None
        latest = runs[-1] / self._config.crisis_report_file
        try:
            age = self._now_fn().timestamp() - latest.stat().st_mtime
        except OSError as exc:
            logger.warning("危机快照不可读 %s: %s", latest, exc)
            return None
        return round(age / 86400.0, 2)

    # ── 判定 + 动作 ─────────────────────────────────────────

    def evaluate(
        self, *, dry_run: bool = False, observe_only: bool = False
    ) -> EmergencyTrackVerdict:
        """一个评估周期：探针 → 判据 → （必要时）保命动作 → 落审计。永不抛.

        Args:
            dry_run: True=不落审计（boot 自检/回归用）。
            observe_only: True=只判不动作（保命轨演练/回归用；缺省 False=确认失效即下单）。
        """
        ts = self._now_fn().isoformat()
        errors: dict[str, str] = {}
        breaches: list[str] = []
        cfg = self._config
        if self.config_error:
            errors["config"] = self.config_error
            breaches.append("emergency_track_config_unreadable")
        if not cfg.enabled:
            return self._finish(
                EmergencyTrackVerdict(ts, STATE_DISABLED, (), errors=errors, breaches=tuple(breaches)),
                dry_run=dry_run,
            )
        readings = self.read_legs()
        last_resort, lr_error = self._last_resort_active()
        if lr_error:
            errors["last_resort"] = lr_error
        stale, unknown, all_dead, breaches = self._judge_legs(readings, last_resort, breaches)
        breaches.extend(self._snapshot_breaches())
        self._confirmations = self._confirmations + 1 if all_dead else 0
        base: dict[str, Any] = {
            "legs": readings,
            "stale_count": stale,
            "unknown_count": unknown,
            "confirmations": self._confirmations,
            "required_confirmations": cfg.consecutive_confirmations,
            "last_resort_active": last_resort,
        }
        if not all_dead:
            state = STATE_INSUFFICIENT if (unknown and stale) else STATE_NORMAL
            return self._finish(
                EmergencyTrackVerdict(ts, state, errors=errors, breaches=tuple(breaches),
                                      action={}, **base),
                dry_run=dry_run,
            )
        if self._confirmations < cfg.consecutive_confirmations:
            return self._finish(
                EmergencyTrackVerdict(ts, STATE_ARMING, errors=errors, breaches=tuple(breaches),
                                      action={}, **base),
                dry_run=dry_run,
            )
        if not self._in_active_window():
            # 盘后/周末三腿必然集体"过期"（干净收市≠失效）——无窗口闸门就是每晚误熔断。
            # 窗口外只判不动作（盘后主机失控由 reaper 收割处置，不需要拉资金闸），但必出声留痕。
            return self._finish(
                EmergencyTrackVerdict(
                    ts, STATE_OUTSIDE_WINDOW, errors=errors, action={"suppressed": True,
                    "reason": "outside_active_window"},
                    breaches=tuple(breaches) + ("trip_suppressed_outside_active_window",), **base,
                ),
                dry_run=dry_run,
            )
        action = self._execute_trip(reason=cfg.action_reason, observe_only=observe_only)
        if action.get("failed"):
            errors["action"] = str(action.get("error", "动作失败"))
            breaches.append("killswitch_trip_failed")
        return self._finish(
            EmergencyTrackVerdict(ts, STATE_ACTIVATED, errors=errors, breaches=tuple(breaches),
                                  action=action, **base),
            dry_run=dry_run,
        )

    def _judge_legs(
        self, readings: tuple[LegReading, ...], last_resort: bool, breaches: list[str]
    ) -> tuple[int, int, bool, list[str]]:
        """腿计数 → (stale, unknown, 全腿确认失效?, breaches)。口径见 config 注释与模块 docstring."""
        cfg = self._config
        stale = sum(1 for r in readings if r.status == _LEG_STALE)
        unknown = sum(1 for r in readings if r.status == _LEG_UNKNOWN)
        total = len(readings)
        if last_resort and cfg.count_last_resort_as_stale_leg:
            stale = min(total, stale + 1)
        all_dead = total > 0 and stale == total and unknown == 0
        breaches = breaches + [f"leg_stale:{r.leg_id}" for r in readings if r.status == _LEG_STALE]
        breaches = breaches + [
            f"leg_unknown:{r.leg_id}" for r in readings if r.status == _LEG_UNKNOWN
        ]
        return stale, unknown, all_dead, breaches

    def _snapshot_breaches(self) -> list[str]:
        """危机快照新鲜度 breach（BRK-072 消费端；只告警，不参与熔断必要条件）."""
        age = self.crisis_snapshot_age_days()
        if age is None:
            return ["crisis_snapshot_absent"]
        limit = self._config.crisis_max_age_days
        if age > limit:
            return [f"crisis_snapshot_stale:{age}d>{limit}d"]
        return []

    def _in_active_window(self) -> bool:
        """当前是否落在配置生效窗口（缺省=A股连续竞价时段 Asia/Shanghai）.

        窗口关闭 = 判据仍评估、仍留痕，只是不下单（见 evaluate 的出声分支）。
        """
        cfg = self._config
        if not cfg.window_enabled:
            return True
        from zoneinfo import ZoneInfo

        try:
            local = self._now_fn().astimezone(ZoneInfo(cfg.window_tz))
        except Exception as exc:  # noqa: BLE001 — 时区解析失败按窗口外处理（保守不动作）
            logger.error("active_window 时区解析失败（本周期按窗口外=不动作）: %r", exc)
            return False
        minutes = float(local.hour * 60 + local.minute)
        return float(cfg.window_start_min) <= minutes <= float(cfg.window_end_min)

    def _orchestrator(self) -> Any:
        if self._orchestrator_provider is not None:
            return self._orchestrator_provider()
        from zephyr.autonomy_core.kill_switch_orchestrator import get_orchestrator

        return get_orchestrator()

    def _execute_trip(self, *, reason: str, observe_only: bool) -> dict[str, Any]:
        """经唯一入口下单保命动作（永不抛，失败信息回传）."""
        cfg = self._config
        if observe_only:
            return {"observe_only": True, "incident_kind": cfg.incident_kind, "reason": reason}
        try:
            orch = self._orchestrator()
            result = orch.route_incident(cfg.incident_kind, reason)
        except Exception as exc:  # noqa: BLE001 — 动作面失败必须出声但不得炸宿主
            logger.error("应急保命轨下单失败（三腿已确认失效！请立即人工拉闸）: %r", exc)
            return {"executed": False, "failed": True, "incident_kind": cfg.incident_kind,
                    "reason": reason, "error": repr(exc)}
        payload = {
            "executed": bool(getattr(result, "success", False)),
            "failed": not bool(getattr(result, "success", False)),
            "level": getattr(result, "level", None),
            "tripped": list(getattr(result, "tripped", []) or []),
            "skipped": list(getattr(result, "skipped", []) or []),
            "errors": dict(getattr(result, "errors", {}) or {}),
            "incident_kind": cfg.incident_kind,
            "reason": reason,
            "entry": "kill_switch_orchestrator.route_incident",
        }
        if payload["failed"]:
            logger.error("应急保命轨：三腿确认失效但拉闸未完全成功 %s", payload["errors"])
        else:
            logger.error("应急保命轨已触发系统级熔断 %s", payload["tripped"])
        return payload

    def _finish(self, verdict: EmergencyTrackVerdict, *, dry_run: bool) -> EmergencyTrackVerdict:  # noqa: ANN401  语义见 evaluate
        if not dry_run:
            self._audit(verdict)
        if verdict.state in (STATE_ARMING, STATE_ACTIVATED):
            logger.error("应急保命轨 state=%s confirmations=%s/%s stale=%s unknown=%s",
                         verdict.state, verdict.confirmations,
                         verdict.required_confirmations, verdict.stale_count, verdict.unknown_count)
        return verdict

    def _audit(self, verdict: EmergencyTrackVerdict) -> None:
        """每次评估落一行 JSONL（失败不吞：logger.error 出声）."""
        path = self._repo_root / self._config.audit_path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8", buffering=1) as fh:
                fh.write(json.dumps({"schema_version": "1.0", "source": "emergency_track",
                                     **verdict.as_dict()}, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.error("emergency_track 审计留痕写入失败（判定仍生效）: %r", exc)


_guardian_instance: EmergencyTrackGuardian | None = None


def get_emergency_track_guardian() -> EmergencyTrackGuardian:
    """进程级单例（宿主=process_reaper/boot_hooks；配置只读一次）."""
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = EmergencyTrackGuardian()
    return _guardian_instance


def run_emergency_track_check(*, dry_run: bool = False, observe_only: bool = False) -> dict[str, Any]:
    """宿主调用面：一个评估周期，返回裁定字典。永不抛（缺省=真判定+真动作+真留痕）."""
    try:
        return get_emergency_track_guardian().evaluate(
            dry_run=dry_run, observe_only=observe_only
        ).as_dict()
    except Exception as exc:  # noqa: BLE001 — 保命轨自身不得反噬宿主（但必须出声）
        logger.error("emergency_track 评估异常（非静默：已记 error 日志）: %r", exc)
        return {"state": STATE_CONFIG_ERROR, "errors": {"evaluate": repr(exc)}}
