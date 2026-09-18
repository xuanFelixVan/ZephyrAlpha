# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.alert_webhook_dispatch
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.alerter(failures/*.json 生产方，本件只读其目录不写);
#   zephyr.security.access_control.kill_switch(触发源二); zephyr.shared.security.secrets(凭据，禁裸 getenv);
#   zephyr.shared.utils.time_utils(now_utc); zephyr.shared.io.file_utils(safe_write_text);
#   zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed(通道自身不可用的落板出口);
#   config/flags.yaml §flags.alerts.auto_escalation(升级读方，本件是它在全仓的唯一读者);
#   stdlib(urllib.request; os.environ 仅用于 ZEPHYR_ALERT_WEBHOOK_DIR 测试隔离覆盖位，非凭据面)
# [CONSUMERS] zephyr.data.alerter.Alerter._write_failure_file（CRITICAL 落盘成功的同进程事件钩子
#   dispatch_on_failure_event —— 宪法 §9.3 事件触发，禁 cron/Timer/sleep-loop）;
#   本模块 main()（人工复推/本地桩双验证 CLI）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 可插拔：本件**不内置任何具体厂商通道**（飞书/SMTP 已于 2026-09-15 裁撤，Owner 裁定通知=前端 promotion 页；本件只实现"通用 webhook POST + 端点从配置来"的机器侧骨架）；
#   缺省 fail-closed：配置缺失/enabled=false/端点为空 → 一律不推送并返回 blocked+reason（禁静默假成功）；**投递失败永不静默**：失败/受阻既进返回报告，也落 trail JSONL，还投影到 OpsAlertFeed 通知板（"通道不可用"本身必须是可观测状态——R-021：写了没人读的通道等于没建）；
#   URL 与凭据只从 config/alert_webhook.yaml + zephyr.shared.security.secrets 来（禁硬编码/禁裸 os.getenv）；触发源闭合两类：data/failures/*.json 的 level=CRITICAL ∨ kill_switch 非 normal（探针失败按"疑似触发"出声）；
#   **去重指纹按端点独立**（ep_name × fingerprint）：A 端点成功绝不替 B 端点吞掉同一条告警——共享指纹会让"部分端点永久失败"看起来像已送达（本件接管时实测的原始缺陷，已治）；升级面（flags.alerts.auto_escalation）缺省 false=只发新触发不发积压；
#   true=把未送达积压一并外推并打 ESCALATED 标记；两态都如实上报 skipped/reason，禁静默；
#   本件只读 failures/，永不写生产表；派发留痕 JSONL（含 HTTP 状态码，不含凭据明文）；
#   事件钩子路径**禁止全目录扫描**（data/failures 实测 12968 件，逐件读=每个告警点几秒 I/O），全目录扫描只经 CLI/人工复推路径且按文件名日期前缀剪枝；
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlertWebhookError：配置解析失败/未知键/端点 URL 非 http(s)/凭据键缺失；
#   网络失败=该端点记 error 不抛（多端点互不连坐）；dispatch_on_failure_event 永不抛（告警钩子不反噬告警器）；路径等定位信息进 exc.details 不进消息文本（MSG-EXPOSURE）
# [TESTS] tests/data/test_alert_webhook_dispatch.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""alert_webhook_dispatch — E7/BRK-055 告警外发机器侧（可插拔 webhook，缺省 fail-closed）.

施工真源：docs/_working/fullflow_campaign/COORDINATION_LEDGER.md 预裁 R-K4 + 本车道任务书 T1/T2。

为何"可插拔 + 无内置厂商通道"（Owner 已裁定，勿重开）：2026-09-15 飞书/SMTP 通道被彻底删除，
通知以前端 promotion 页为准。所以本件只做**机器侧出口机制**：取触发事件 → 组装 payload →
按配置里的端点做通用 HTTP POST。任何具体厂商（Server酱/钉钉/Telegram…）都只是
"配置里的一条端点"，代码里不出现厂商名，凭据一律走 secrets 注册表（缺凭据=Owner 四类事，只登记）。

缺省 fail-closed：没有配置、enabled=false、端点为空 → **不推送**并如实返回 blocked+reason，
并把"通道不可用"投影到 OpsAlertFeed（promotion 页横幅）——因为"以为通了其实没通"比
"明确知道没通"危险得多（本仓 BRK-005/R-021 两起实证：写了没人读的通道=假通道）。

# [ALGO_FLOW]
输入: 事件记录（alerter 的 CRITICAL failure 落盘成功）或 CLI 全量扫描 + config/alert_webhook.yaml
      + config/flags.yaml §flags.alerts.auto_escalation + kill_switch 探针
前置检查: 配置可解析（未知键=硬错）；enabled；端点非空且 URL scheme∈{http,https}；凭据键可解析
执行: ① 归一触发清单 ② 按端点剔除已送达指纹（去重键=端点×指纹）③ 逐端点 POST（超时+状态码判定）
      ④ 成功端点各记自身指纹 ⑤ 留痕 JSONL ⑥ 受阻/失败投影到通知板（fail-closed 可观测）
输出: DispatchReport（scanned/triggered/sent/failed/blocked + 逐端点结果 + 升级态 + 通道健康）
降级: 端点为空/未启用 → blocked（不假成功）；单端点网络失败不影响其他端点；钩子异常 log+落痕不抛
不变量: 同一(端点,指纹)在状态文件存续期内只发一次；凭据明文永不进日志/留痕；
        任何"未送达"都同时出现在三处：返回报告 + trail + 通知板
# [/ALGO_FLOW]
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Final, Mapping

from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "AlertWebhookConfig",
    "AlertWebhookDispatcher",
    "AlertWebhookEndpoint",
    "AlertWebhookError",
    "channel_health",
    "dispatch_on_failure_event",
    "load_alert_webhook_config",
    "main",
    "maybe_dispatch_alerts",
    "read_auto_escalation_flag",
    "scan_critical_failures",
]

CONFIG_RELATIVE_PATH: Final = "config/alert_webhook.yaml"
FLAGS_RELATIVE_PATH: Final = "config/flags.yaml"
SINK_DIR_ENV: Final = "ZEPHYR_ALERT_WEBHOOK_DIR"
DEFAULT_STATE_RELATIVE: Final = "data/runtime/alert_webhook_state.json"
DEFAULT_TRAIL_RELATIVE: Final = "data/runtime/alert_webhook_trail.jsonl"
DEFAULT_SCAN_WINDOW_HOURS: Final = 24
DEFAULT_BOARD_MODULE_ID: Final = "alert-webhook-dispatch"
_ALLOWED_SCHEMES: Final = frozenset({"http", "https"})
_ESCALATION_BOARD_KEY: Final = "alert-webhook/channel-unavailable"
_FINGERPRINT_SEP: Final = "\x1f"

_KNOWN_CONFIG_KEYS: Final = frozenset({
    "enabled", "failures_dir", "state_path", "trail_path", "scan_window_hours",
    "include_kill_switch", "timeout_s", "max_payload_bytes", "endpoints", "board_module_id",
})
_KNOWN_ENDPOINT_KEYS: Final = frozenset({
    "name", "url", "secret_key", "header_name", "method", "content_type",
})


class AlertWebhookError(ValueError):
    """告警外推配置非法（fail-closed）。

    路径类定位信息进 **details 字段**、不进消息文本（MSG-EXPOSURE 要求，
    先例 zephyr.shared.io.file_utils.WriteVerificationError 同型）。
    """

    # 待 A1-b：`error_code_registry.yaml` 属 PROTECTED-PATHS（Owner 授权面），在册建议号 ZA-DATA-0030。
    # 沿 R-044 判例：宁可 None，不自造/不借用编号（伪造码会让 GATE-ERRCODE-CONSISTENCY 永久红且审计失真）。
    error_code = None

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details: dict[str, Any] = dict(details or {})


@dataclass(frozen=True)
class AlertWebhookEndpoint:
    """一条可插拔端点（无厂商语义：名字/URL/凭据键/头部名 全由配置给）。"""

    name: str
    url: str
    secret_key: str = ""       # secrets 注册表里的**键名**（不是凭据值）
    header_name: str = ""      # 凭据注入的请求头名（空=不注入）
    method: str = "POST"
    content_type: str = "application/json"

    def __post_init__(self) -> None:
        scheme = self.url.split(":", 1)[0].lower() if ":" in self.url else ""
        if scheme not in _ALLOWED_SCHEMES:
            raise AlertWebhookError(
                f"端点 {self.name!r} URL scheme={scheme!r} 非法（只允许 http/https，"
                f"禁 file://、禁本地路径伪装外推）"
            )
        if self.method.upper() not in ("POST", "PUT"):
            raise AlertWebhookError(f"端点 {self.name!r} method={self.method!r} 只允许 POST/PUT")


@dataclass(frozen=True)
class AlertWebhookConfig:
    """告警外推配置（冻结）。缺文件 = enabled=False + 零端点（fail-closed）。"""

    enabled: bool = False
    endpoints: tuple[AlertWebhookEndpoint, ...] = ()
    failures_dir: Path = Path("data/failures")
    state_path: Path = Path(DEFAULT_STATE_RELATIVE)
    trail_path: Path = Path(DEFAULT_TRAIL_RELATIVE)
    scan_window_hours: int = DEFAULT_SCAN_WINDOW_HOURS
    include_kill_switch: bool = True
    timeout_s: float = 10.0
    max_payload_bytes: int = 8192
    board_module_id: str = DEFAULT_BOARD_MODULE_ID

    @property
    def dispatchable(self) -> bool:
        """可派发=启用且至少一条端点（否则 fail-closed blocked）。"""
        return bool(self.enabled and self.endpoints)

    @property
    def blocked_reason(self) -> str:
        """不可派发的**如实**原因（fail-closed 必须说清为什么没出声）。"""
        if not self.enabled:
            return "enabled=false（缺省 fail-closed：无端点配置即不外发）"
        return "endpoints 为空（无端点=不推送，fail-closed）"


def _repo_root() -> Path:
    try:
        from zephyr.shared.io.paths import REPO_ROOT

        return Path(REPO_ROOT)
    except Exception:  # noqa: BLE001 — 仅路径解析降级（本件被 alerter 钩子调用，禁反噬）
        return Path(__file__).resolve().parents[3]


def _sink_root() -> Path:
    """可写落点（state/trail/failures 读取根）的锚定根。

    为什么不按 cwd 解析相对路径：配置里写的是 `data/runtime/...`，按 cwd 解析会让
    **同一份去重账本随工作目录分裂**——换个目录跑就"没发过"，同一 CRITICAL 重发；
    或在别的盘/别的 worktree 里造出第二份 trail。告警面的账本错位=静默失效（R-021 同族）。
    故一律锚仓库根（与 config 自身解析同根，见 load_alert_webhook_config）。

    ZEPHYR_ALERT_WEBHOOK_DIR 是测试/多仓隔离覆盖位（先例：ZEPHYR_OPS_NOTIFICATION_DIR
    之于通知板、ZEPHYR_COMMIT_QUEUE_DIR 之于提交队列），缺省=生产锚定根。
    """
    env = os.environ.get(SINK_DIR_ENV, "")
    if env:
        return Path(env)
    return _repo_root()


def _anchored(raw: str | Path) -> Path:
    """相对路径 → 锚到 _sink_root()；绝对路径原样返回（测试注入 tmp_path 用）。"""
    p = Path(str(raw))
    return p if p.is_absolute() else _sink_root() / p


def load_alert_webhook_config(yaml_path: str | Path | None = None) -> AlertWebhookConfig:
    """装配告警外推配置。缺文件=enabled=False（不抛，返回不可派发配置）；读不懂=硬错。"""
    path = Path(yaml_path) if yaml_path is not None else (_repo_root() / CONFIG_RELATIVE_PATH)
    if not path.exists():
        log.warning("[ALERT-WEBHOOK] 配置缺失 %s → enabled=False（fail-closed，不推送）", path)
        return AlertWebhookConfig(enabled=False)
    import yaml  # 仓内既有依赖

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AlertWebhookError(
            f"alert_webhook 配置解析失败（YAML 非法）: {type(exc).__name__}",
            details={"config_path": str(path), "cause": str(exc)},
        ) from exc
    if loaded is None:
        return AlertWebhookConfig(enabled=False)
    if not isinstance(loaded, Mapping):
        raise AlertWebhookError(
            "alert_webhook 配置根节点须为映射",
            details={"config_path": str(path), "got": type(loaded).__name__},
        )
    unknown = set(loaded) - _KNOWN_CONFIG_KEYS
    if unknown:
        raise AlertWebhookError(
            f"alert_webhook 配置含未知键 {sorted(unknown)}（防拼写漂移静默）",
            details={"config_path": str(path)},
        )
    return AlertWebhookConfig(
        enabled=bool(loaded.get("enabled", False)),
        endpoints=tuple(_parse_endpoint(e) for e in (loaded.get("endpoints") or [])),
        failures_dir=_anchored(loaded.get("failures_dir", "data/failures")),
        state_path=_anchored(loaded.get("state_path", DEFAULT_STATE_RELATIVE)),
        trail_path=_anchored(loaded.get("trail_path", DEFAULT_TRAIL_RELATIVE)),
        scan_window_hours=int(loaded.get("scan_window_hours", DEFAULT_SCAN_WINDOW_HOURS)),
        include_kill_switch=bool(loaded.get("include_kill_switch", True)),
        timeout_s=float(loaded.get("timeout_s", 10.0)),
        max_payload_bytes=int(loaded.get("max_payload_bytes", 8192)),
        board_module_id=str(loaded.get("board_module_id", DEFAULT_BOARD_MODULE_ID)),
    )


def _parse_endpoint(raw: Any) -> AlertWebhookEndpoint:
    if not isinstance(raw, Mapping):
        raise AlertWebhookError(f"端点条目须为映射: {raw!r}")
    unknown = set(raw) - _KNOWN_ENDPOINT_KEYS
    if unknown:
        raise AlertWebhookError(f"端点条目含未知键 {sorted(unknown)}")
    name = str(raw.get("name") or "").strip()
    url = str(raw.get("url") or "").strip()
    if not name or not url:
        raise AlertWebhookError("端点条目缺 name/url（URL 只从配置来，禁硬编码）")
    return AlertWebhookEndpoint(
        name=name, url=url, secret_key=str(raw.get("secret_key") or ""),
        header_name=str(raw.get("header_name") or ""), method=str(raw.get("method") or "POST"),
        content_type=str(raw.get("content_type") or "application/json"),
    )


# ── 升级开关的**唯一读方**（BRK-052 实现侧；flag 翻转本身属 Owner 门位）──────────
#
# 实测（2026-09-18 本车道）：`config/flags.yaml` 的 `flags.alerts.auto_escalation` 在全仓
# **零读者**——`zephyr.shared.foundation.flags.load_flags_from_yaml` 只把每个顶层键的
# `enabled` 注册成 FeatureFlag，嵌套子键（auto_escalation/strict_mode/dlq_enabled）
# 根本不进注册表。故"把 flag 翻成 true"在当前代码面上**零效果**（教科书式只写不读）。
# 本函数是它的第一位、也是唯一的读者：读真源 YAML、不做代码副本、读不懂=如实报 blocked 原因。


def read_auto_escalation_flag(flags_path: str | Path | None = None) -> dict[str, Any]:
    """读 §flags.alerts.auto_escalation（缺省 fail-closed=False，并如实带回观察值）。"""
    path = Path(flags_path) if flags_path is not None else (_repo_root() / FLAGS_RELATIVE_PATH)
    out: dict[str, Any] = {"enabled": False, "observed": "missing", "reason": "", "path": str(path)}
    if not path.exists():
        out["reason"] = f"flags 文件不存在 → 缺省 false（fail-closed：不升级）"
        return out
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        spec = (data.get("flags") or {}).get("alerts") or {}
        out["observed"] = str(spec.get("auto_escalation", "absent")).lower()
        out["enabled"] = out["observed"] in ("true", "1", "yes", "on")
    except Exception as exc:  # noqa: BLE001 — 读不懂=不升级并留痕，禁反噬告警链
        out["observed"] = f"unreadable:{type(exc).__name__}"
        out["reason"] = "flags.alerts.auto_escalation 不可解析 → 缺省 false（fail-closed）"
        log.error("[ALERT-WEBHOOK] flags 读取异常（按不升级处置）: %s: %s", type(exc).__name__, exc)
    if not out["enabled"] and not out["reason"]:
        out["reason"] = f"auto_escalation={out['observed']}（Owner 门位未放行，升级面关闭）"
    return out


# ── 触发源扫描（闭合两类：CRITICAL failure 文件 / kill_switch）──────────────────


def _fingerprint(task_id: str, level: str, error: str) -> str:
    return hashlib.sha256(f"{task_id}|{level}|{error}".encode("utf-8")).hexdigest()[:16]


def _delivered_key(endpoint_name: str, fp: str) -> str:
    """去重键=端点×指纹（共享指纹会让部分端点永久失败被掩盖——见 [INVARIANTS]）。"""
    return f"{endpoint_name}{_FINGERPRINT_SEP}{fp}"


def trigger_from_failure_record(data: Mapping[str, Any], *, file_name: str = "") -> dict[str, Any]:
    """把 alerter 的 failure 记录归一成触发项（事件路径用，禁全目录扫描）。"""
    return {
        "source_kind": "failure_file",
        "file": file_name,
        "task_id": str(data.get("task_id") or "unknown"),
        "level": str(data.get("level") or "ERROR").upper(),
        "error": str(data.get("error") or "")[:500],
        "timestamp": str(data.get("timestamp") or ""),
        "origin": str(data.get("source") or ""),
    }


def scan_critical_failures(failures_dir: str | Path, *, since_iso: str = "") -> list[dict[str, Any]]:
    """扫 failures/*.json 的 CRITICAL 行（只读；坏文件跳过并计数，不抛）。

    仅 CLI/人工复推路径使用；事件路径走 trigger_from_failure_record（见 [INVARIANTS]）。

    Args:
        failures_dir: alerter 的失败汇总目录（默认 data/failures）。
        since_iso: 只取 timestamp ≥ 该 ISO 时刻的行（空=不过滤）。
            同时按文件名前缀 YYYYMMDD 剪枝（实测该目录 12968 件，全读会打爆事件路径 I/O）。
    """
    root = Path(failures_dir)
    out: list[dict[str, Any]] = []
    if not root.exists():
        return out
    since_day = since_iso[:10].replace("-", "") if len(since_iso) >= 10 else ""
    skipped = 0
    for fp in sorted(root.glob("*.json")):
        if since_day and fp.name[:8] < since_day:
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            skipped += 1
            continue
        if not isinstance(data, dict):
            continue
        if str(data.get("level") or "").upper() != "CRITICAL":
            continue
        ts = str(data.get("timestamp") or "")
        if since_iso and ts and ts < since_iso:
            continue
        out.append(trigger_from_failure_record(data, file_name=fp.name))
    if skipped:
        log.warning("[ALERT-WEBHOOK] %s 下 %d 个 failure 文件不可解析被跳过", root, skipped)
    return out


def scan_kill_switch() -> list[dict[str, Any]]:
    """探 kill_switch：非 normal = 触发；**探针失败也出声**（fail-closed：不知道≠没事）。"""
    try:
        from zephyr.security.access_control.kill_switch import get_kill_switch

        raw = get_kill_switch().state
        val = str(getattr(raw, "value", raw) or "").lower()
    except Exception as exc:  # noqa: BLE001 — 探针失败按"疑似触发"处置（安全方向）
        return [{"source_kind": "kill_switch", "task_id": "kill_switch_probe",
                 "level": "CRITICAL", "error": f"kill_switch 探针失败: {type(exc).__name__}",
                 "timestamp": now_utc().isoformat(), "origin": "kill_switch"}]
    if val in ("", "normal"):
        return []
    return [{"source_kind": "kill_switch", "task_id": "kill_switch", "level": "CRITICAL",
             "error": f"kill_switch 状态={val}", "timestamp": now_utc().isoformat(),
             "origin": "kill_switch"}]


# ── 派发器 ──────────────────────────────────────────────────────────


class AlertWebhookDispatcher:
    """通用 webhook 派发器（可插拔：端点全从配置来，代码零厂商耦合）。

    注入面（单测/本地桩用）：poster（默认 urllib POST）、clock、board_publisher。
    **默认路径全真**：poster 缺省 = _urllib_post（真 HTTP），测试用本地 http 桩打真请求。
    """

    def __init__(self, config: AlertWebhookConfig | None = None, *,
                 poster: Callable[[str, bytes, dict[str, str], float], tuple[int, str]] | None = None,
                 clock: Callable[[], Any] | None = None,
                 board_publisher: Callable[..., dict[str, Any]] | None = None,
                 flags_path: str | Path | None = None) -> None:
        base = config if config is not None else load_alert_webhook_config()
        # 路径锚定与 load 路径同源：直接构造 AlertWebhookConfig() 的调用方（含缺配置降级分支、
        # 含测试）若给相对路径，也一律落到 _sink_root() 下，绝不随 cwd 分裂去重账本。
        self.cfg = replace(
            base,
            failures_dir=_anchored(base.failures_dir),
            state_path=_anchored(base.state_path),
            trail_path=_anchored(base.trail_path),
        )
        self._poster = poster or _urllib_post
        self._clock = clock or now_utc
        self._board_publisher = board_publisher
        self._flags_path = flags_path

    # ── 状态（按端点去重，持久化）───────────────────────────────────────

    def _load_sent(self) -> set[str]:
        try:
            if self.cfg.state_path.exists():
                data = json.loads(self.cfg.state_path.read_text(encoding="utf-8"))
                return set(data.get("delivered_keys") or [])
        except (OSError, ValueError):
            log.warning("[ALERT-WEBHOOK] 状态文件损坏 %s → 按空集处理（宁可重发一次不可漏发）",
                        self.cfg.state_path)
        return set()

    def _save_sent(self, sent: set[str]) -> None:
        from zephyr.shared.io.file_utils import safe_write_text

        self.cfg.state_path.parent.mkdir(parents=True, exist_ok=True)
        safe_write_text(self.cfg.state_path, json.dumps(
            {"delivered_keys": sorted(sent), "updated_at": self._clock().isoformat()},
            ensure_ascii=False, indent=1), newline="\n")

    def _trail(self, record: dict[str, Any]) -> None:
        try:
            self.cfg.trail_path.parent.mkdir(parents=True, exist_ok=True)
            with self.cfg.trail_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        except OSError as exc:
            # 留痕是最后一条腿：它失败必须 loud（禁"告警系统自己出事没人知道"）
            log.error("[ALERT-WEBHOOK] 留痕落盘失败（外发面已无可审计证据）: %s: %s",
                      type(exc).__name__, exc, exc_info=True)

    # ── 通知板投影（让"通道不可用"成为可观测状态）───────────────────────

    def _publish_board(self, *, severity: str, title: str, message: str,
                       labels: dict[str, Any]) -> None:
        """把通道自身状态投到既有 promotion 页出口（不改 ops_alert_feed 本体，只当生产者）。"""
        try:
            publish = self._board_publisher
            if publish is None:
                from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import (
                    OpsAlertFeed,
                )

                publish = OpsAlertFeed(module_id=self.cfg.board_module_id).publish
            publish(key=_ESCALATION_BOARD_KEY, severity=severity, title=title,
                    message=message, source=f"config/{Path(CONFIG_RELATIVE_PATH).name}",
                    labels=labels)
        except Exception as exc:  # noqa: BLE001 — 投影失败不反噬外发主链，但必须 loud + 落痕
            log.error("[ALERT-WEBHOOK] 通知板投影失败: %s: %s", type(exc).__name__, exc, exc_info=True)
            self._trail({"kind": "board_error", "error": f"{type(exc).__name__}: {exc}"[:200],
                         "at": self._clock().isoformat()})

    # ── 组装 / 发送 ──────────────────────────────────────────────────

    def _payload(self, triggers: list[dict[str, Any]], *, escalated: bool) -> bytes:
        body: dict[str, Any] = {
            "schema": "zephyralpha.alert_webhook.v1",
            "sent_at": self._clock().isoformat(),
            "host": platform.node(),
            "count": len(triggers),
            "escalated": escalated,
            "alerts": triggers,
        }
        raw = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        limit = self.cfg.max_payload_bytes
        if len(raw) > limit:
            # 钳制：只保第一条 + 计数（禁把整批失败文件糊进一个请求把通道打爆）
            body["alerts"] = triggers[:1]
            body["truncated"] = True
            body["count"] = len(triggers)
            raw = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        return raw[:limit]

    def _headers(self, ep: AlertWebhookEndpoint) -> dict[str, str]:
        headers = {"Content-Type": ep.content_type, "User-Agent": "ZephyrAlpha-AlertWebhook/1.0"}
        if ep.secret_key and ep.header_name:
            from zephyr.shared.security.secrets import get_secret_or_default

            token = get_secret_or_default(ep.secret_key, "")
            if not token:
                # fail-closed：凭据键声明了却取不到 → 该端点不发（禁无凭据裸发到外网）
                raise AlertWebhookError(
                    f"端点 {ep.name!r} 声明凭据键 {ep.secret_key!r} 但 secrets 取不到值——拒发"
                )
            headers[ep.header_name] = token
        return headers

    def _post_one(self, ep: AlertWebhookEndpoint, payload: bytes) -> tuple[int, str]:
        try:
            return self._poster(ep.url, payload, self._headers(ep), self.cfg.timeout_s)
        except Exception as exc:  # noqa: BLE001 — 单端点失败不连坐其他端点（含凭据缺失）
            return 0, f"{type(exc).__name__}: {exc}"[:200]

    # ── 对外派发面 ───────────────────────────────────────────────────

    def _post_to_endpoint(self, ep: AlertWebhookEndpoint, triggers: list[dict[str, Any]],
                          esc: dict[str, Any], delivered: set[str]) -> dict[str, Any]:
        """单端点派发：挑未送达 → POST → 留痕 + 失败投影。返回 {result, newly, ok}。

        从 dispatch_triggers 抽出（整块留在一个函数里 = NO-HIGH-COMPLEXITY 超阈值，救回件自带）。

        去重键必须含 **本端点名**：写死共享哨兵名（历史实现用 "ALL"）会让 A 端点的成功替
        B 端点吞掉同一条告警——"部分端点永久失败"看起来像已送达（[INVARIANTS] 承诺的正是这条，
        测试钉 test_per_endpoint_dedup_alive_does_not_swallow_dead）。
        ok=None 表示"本端点无可发内容"（去重命中），不计成功也不计失败。
        """
        keys = [_delivered_key(ep.name, _fingerprint(t["task_id"], t["level"], t["error"]))
                for t in triggers]
        fresh_idx = [i for i, k in enumerate(keys) if k not in delivered]
        backlog_idx = [i for i, k in enumerate(keys) if k in delivered]
        pick = fresh_idx + (backlog_idx if esc.get("enabled") else [])
        if not pick:
            return {"result": {"name": ep.name, "status": 0, "ok": False, "skipped": "dedup"},
                    "newly": [], "ok": None}
        payload = self._payload([triggers[i] for i in pick],
                                escalated=bool(esc.get("enabled")) and bool(backlog_idx))
        status, err = self._post_one(ep, payload)
        ok = 200 <= int(status) < 300
        if not ok:
            # 未送达必须可观测：投影到前端真读的通知板（禁只写 trail 等人来翻）
            self._publish_board(
                severity="critical", title="告警外发通道投递失败",
                message=f"端点 {ep.name} HTTP status={status} {err[:120]}；"
                        f"{len(pick)} 条告警未送达，将在下一个事件重试",
                labels={"kind": "channel_failed", "endpoint": ep.name, "status": int(status)},
            )
        self._trail({"kind": "post", "endpoint": ep.name, "status": int(status), "ok": ok,
                     "delivered": len(pick), "error": "" if ok else err[:200],
                     "escalated": bool(esc.get("enabled")), "at": self._clock().isoformat()})
        return {"result": {"name": ep.name, "status": int(status), "ok": ok,
                           "delivered": len(pick), "error": "" if ok else err[:200]},
                "newly": [keys[i] for i in fresh_idx] if ok else [], "ok": ok}

    def dispatch_triggers(self, triggers: list[dict[str, Any]], *,
                          escalate: bool | None = None) -> dict[str, Any]:
        """把一批触发项逐端点外发（事件路径与 CLI 路径共用）。返回如实报告，禁假成功。"""
        if not self.cfg.dispatchable:
            reason = self.cfg.blocked_reason
            self._trail({"kind": "blocked", "reason": reason, "triggers": len(triggers),
                         "at": self._clock().isoformat()})
            self._publish_board(severity="critical", title="告警外发通道不可用（fail-closed）",
                                message=f"{reason}；本轮 {len(triggers)} 条告警无机器侧出口",
                                labels={"kind": "channel_blocked", "triggers": len(triggers)})
            return {"action": "blocked", "reason": reason, "scanned": len(triggers),
                    "triggered": 0, "sent": 0, "failed": 0, "escalated": False, "endpoints": []}

        esc = self.read_escalation() if escalate is None else {"enabled": bool(escalate),
                                                              "observed": "injected", "reason": ""}
        delivered = self._load_sent()
        results: list[dict[str, Any]] = []
        sent_total = failed_total = 0
        newly: list[str] = []
        for ep in self.cfg.endpoints:
            one = self._post_to_endpoint(ep, triggers, esc, delivered)
            results.append(one["result"])
            newly.extend(one["newly"])
            if one["ok"] is True:
                sent_total += 1
            elif one["ok"] is False:
                failed_total += 1
        if newly:
            self._save_sent(delivered | set(newly))
        return {"action": "dispatched" if (sent_total or failed_total) else "nothing_new",
                "scanned": len(triggers), "triggered": sum(int(r.get("delivered") or 0)
                                                           for r in results),
                "sent": sent_total, "failed": failed_total,
                "escalated": bool(esc.get("enabled")), "escalation_reason": esc.get("reason", ""),
                "endpoints": results}

    def read_escalation(self) -> dict[str, Any]:
        """升级开关读取（可被测试/调用方覆盖）。"""
        return read_auto_escalation_flag(self._flags_path)

    def dispatch_once(self, *, since_iso: str = "", scan_dir: bool = True) -> dict[str, Any]:
        """一次扫描+派发（CLI/人工复推路径）。返回结构化报告（blocked/failed 都如实计数）。"""
        triggers: list[dict[str, Any]] = []
        if scan_dir:
            triggers.extend(scan_critical_failures(self.cfg.failures_dir, since_iso=since_iso))
        if self.cfg.include_kill_switch:
            triggers.extend(scan_kill_switch())
        return self.dispatch_triggers(triggers)


def _urllib_post(url: str, payload: bytes, headers: dict[str, str],
                 timeout_s: float) -> tuple[int, str]:
    """默认 HTTP 派发（stdlib urllib，零新依赖）。返回 (status_code, error_text)。"""
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310 — 配置侧已限 http/https
            return int(getattr(resp, "status", 200) or 200), ""
    except urllib.error.HTTPError as exc:
        return int(exc.code), f"HTTPError {exc.code}"[:200]
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return 0, f"{type(exc).__name__}: {exc}"[:200]


# ── 事件钩子（alerter 侧唯一接线点）──────────────────────────────────


def dispatch_on_failure_event(record: Mapping[str, Any], *, file_name: str = "",
                              config: AlertWebhookConfig | None = None) -> dict[str, Any]:
    """alerter 写完 CRITICAL 失败汇总后的**同进程事件**外发（宪法 §9.3：事件触发，无轮询）。

    永不抛：告警外发绝不反噬告警器本体（alerter 的 ERROR_CONTRACT=不抛异常）。
    不静默：任何异常既 log.error(exc_info) 也落 trail（禁 #ARCH-327 式 except 空转）。
    """
    level = str(record.get("level") or "").upper()
    if level != "CRITICAL":
        return {"action": "skipped", "reason": f"level={level or 'empty'} 非 CRITICAL"}
    try:
        cfg = config if config is not None else load_alert_webhook_config()
        out = AlertWebhookDispatcher(cfg).dispatch_triggers(
            [trigger_from_failure_record(record, file_name=file_name)])
        return out
    except Exception as exc:  # noqa: BLE001 — 钩子永不反噬告警器，但必须留痕
        log.error("[ALERT-WEBHOOK] 事件外发异常（已落痕，未静默）: %s: %s",
                  type(exc).__name__, exc, exc_info=True)
        try:
            cfg = config if config is not None else load_alert_webhook_config()
            AlertWebhookDispatcher(cfg)._trail(  # noqa: SLF001 — 异常路径直落留痕，禁再造一层
                {"kind": "event_error", "error": f"{type(exc).__name__}: {exc}"[:200],
                 "at": now_utc().isoformat()})
        except Exception:  # noqa: BLE001 — 留痕面自身失败只剩日志（已到通道最外层）
            log.critical("[ALERT-WEBHOOK] 连留痕都失败——外发通道完全不可用")
        return {"action": "error", "error": f"{type(exc).__name__}"[:200]}


def maybe_dispatch_alerts(task_id: Any = None, success: bool = True,
                          **_kwargs) -> dict[str, Any]:
    """兼容旧签名的唤醒入口（历史批次曾声称挂在 pipeline_events，实测零消费方，见交工报告）。

    永不抛。缺省 fail-closed（无配置=blocked，不假成功）。幂等：按端点指纹去重。
    """
    try:
        cfg = load_alert_webhook_config()
        out = AlertWebhookDispatcher(cfg).dispatch_once()
        out["wake_task_id"] = str(task_id or "")
        out["wake_success"] = bool(success)
        return out
    except Exception as exc:  # noqa: BLE001 — 钩子永不反噬唤醒链
        log.error("[ALERT-WEBHOOK] 派发钩子异常（不反噬唤醒链）: %s: %s",
                  type(exc).__name__, exc, exc_info=True)
        return {"action": "error", "error": f"{type(exc).__name__}"[:200]}


def channel_health(flags_path: str | Path | None = None,
                   config: AlertWebhookConfig | None = None) -> dict[str, Any]:
    """通道自身健康（机器可读）：available/blocked/failed/undelivered 积压。"""
    cfg = config if config is not None else load_alert_webhook_config()
    delivered: set[str] = set()
    try:
        disp = AlertWebhookDispatcher(cfg, flags_path=flags_path)
        delivered = disp._load_sent()  # noqa: SLF001 — 同件内部状态只读投影
    except Exception as exc:  # noqa: BLE001 — 健康探针自身不因读盘失败而抛
        return {"status": "unreadable", "error": f"{type(exc).__name__}"[:200]}
    last_post: dict[str, Any] = {}
    try:
        if cfg.trail_path.exists():
            for line in cfg.trail_path.read_text(encoding="utf-8").splitlines()[-50:]:
                obj = json.loads(line)
                if isinstance(obj, dict) and obj.get("kind") in ("post", "blocked", "event_error"):
                    last_post = obj
    except (OSError, ValueError):
        last_post = {"kind": "unreadable_trail", "trail_path": str(cfg.trail_path)}
    esc = read_auto_escalation_flag(flags_path)
    if not cfg.dispatchable:
        status, detail = "blocked", cfg.blocked_reason
    elif last_post.get("kind") == "post" and not last_post.get("ok"):
        status, detail = "failing", f"最近一次投递 status={last_post.get('status')}"
    else:
        status, detail = "available", f"delivered_keys={len(delivered)}"
    return {"status": status, "detail": detail, "enabled": cfg.enabled,
            "endpoints": [e.name for e in cfg.endpoints],
            "delivered_keys": len(delivered), "last_event": last_post,
            "auto_escalation": esc.get("observed"), "escalation_reason": esc.get("reason", "")}


# noqa: m11-perm-manual-legitimate  M11豁免: 生产触发路径=alerter 事件钩子；本 CLI 为本地桩双验证/人工复推面
def main(argv: list[str] | None = None) -> int:
    """CLI：本地桩双验证 / 人工复推（生产触发路径是 alerter 事件钩子，不是本 CLI）。"""
    import argparse

    ap = argparse.ArgumentParser(description="E7 告警外发机器侧（可插拔 webhook，缺省 fail-closed）")
    ap.add_argument("--config", default=None, help="配置路径（默认 config/alert_webhook.yaml）")
    ap.add_argument("--scan-only", action="store_true", help="只扫触发源不派发")
    ap.add_argument("--health", action="store_true", help="只报通道健康（fail-closed 可观测面）")
    ap.add_argument("--force", action="store_true", help="忽略指纹去重（人工复推）")
    ap.add_argument("--since", default="", help="扫描窗口 ISO 时刻（配 --scan-only/--派发）")
    args = ap.parse_args(argv)
    cfg = load_alert_webhook_config(args.config)
    if args.health:
        print(json.dumps(channel_health(config=cfg), ensure_ascii=False, indent=1))
        return 0
    if args.scan_only:
        hits = scan_critical_failures(cfg.failures_dir, since_iso=args.since)
        if cfg.include_kill_switch:
            hits.extend(scan_kill_switch())
        print(json.dumps({"scanned": len(hits), "alerts": hits}, ensure_ascii=False, indent=1))
        return 0
    disp = AlertWebhookDispatcher(cfg)
    if args.force:
        disp._save_sent(set())  # noqa: SLF001 — 人工复推逃生口（CLI 面，非生产路径）
    print(json.dumps(disp.dispatch_once(since_iso=args.since), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
