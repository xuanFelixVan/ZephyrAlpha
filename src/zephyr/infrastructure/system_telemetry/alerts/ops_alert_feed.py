# [A_module] module_id=MOD-INF-OPS-ALERT-FEED | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-OPS-ALERT-FEED | docs/03_modules/_domain_infrastructure_operations/ops_alert_feed/blueprint.md | §
# [MODULE] zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed
# [INVARIANTS] 通知必落盘 JSONL（进程重启不丢）; 同 dedup key 静默窗口内只刷新不重复; probe 异常 fail-safe 不抛出; 板目录可注入（测试隔离禁写生产 .runtime）
# [MODIFY-GUARD] config/alert_rules.yaml; src/zephyr/frontend/dashboard/api_server.py（/api/ops-notifications + 探针线程段）
# [CONSUMERS] src/zephyr/frontend/dashboard/api_server.py（告警段 30s 探针线程 + /api/ops-notifications 端点）; tests/frontend/test_ops_alert_feed.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OSError; yaml.YAMLError
# [TESTS] tests/frontend/test_ops_alert_feed.py
# [TTL] permanent

"""OpsAlertFeed — 运营告警供给线（治理战役 A2，2026-09-16）。

背景（治理挖矿地图 §4 发现 3）：config/alert_rules.yaml 的 ALERT-SYS-002
（OOM>8GB critical）自 2026-05 起无人生产 ``system.memory_rss_bytes`` 指标，
facade 定时 evaluate("__scheduled__") 是空转占位——规则引擎在、触发链断。
2026-09-15 裁定删除飞书/SMTP 通道后，通知唯一出口=前端 promotion 页。

本模块补上供给线，三段：

1. ``probe_project_rss_bytes`` — 项目衍生进程 RSS 探针（psutil）：
   当前进程树（self+全部后代）∪ cmdline/exe 引用仓根路径的进程。
   8GB 阈值语义=项目自身内存即将失控（9-15 事故：9 孤儿 llama-server ≈12GB）。
2. ``OpsAlertFeed.publish/list_active`` — 通知板（JSONL 落盘
   ``.runtime/ops_notifications/notifications.jsonl``，safe_write_text CAS 写）：
   同 dedup key 静默窗口内只刷新 count/last_seen 不重复发布；resolve 语义打
   resolved_at 时间戳（前端灰显近期已解除项）。
3. ``OpsAlertFeed.tick`` — 一个监测周期：探针取值 → 按规则评估（复用
   AlertSubsystem._check_condition 的条件解析，零复制语义）→ critical 触发即
   publish（静默窗口取规则 silence_window）→ 上一周期仍有活动 OOM 项且本周期
   回落阈值*0.9（滞回）→ resolve。

api_server 侧接线（告警段）：模块级 daemon 线程 30s 一 tick + 只读端点
``GET /api/ops-notifications``；前端 promotion 页横幅轮询该端点。

边界：本模块不投递任何外部通道（飞书/SMTP 已裁撤），不碰 facade 调度器，
不做收割（收割=reaper，M3 闭环另线）。
"""

from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from pathlib import Path
from typing import Callable

import yaml

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

_DEFAULT_BOARD_DIRNAME = "ops_notifications"
_BOARD_FILE = "notifications.jsonl"

# 与 facade alert 调度同拍（30s）；首轮延迟 5s 避开 api_server 启动尖峰
TICK_INTERVAL_S = 30.0
FIRST_TICK_DELAY_S = 5.0

# OOM 解除滞回：回落到阈值*0.9 才算解除（防阈值附近振荡刷板）
RESOLVE_HYSTERESIS = 0.9

# 已解除通知在前端的保留时长（灰显供回看）
RESOLVED_RETENTION_S = 3600.0


def board_dir() -> Path:
    """通知板目录：环境变量可重定向（测试隔离主通道），缺省生产 .runtime 路径。"""
    env = os.environ.get("ZEPHYR_OPS_NOTIFICATION_DIR", "")
    if env:
        return Path(env)
    return REPO_ROOT / ".runtime" / _DEFAULT_BOARD_DIRNAME


def _repo_root_lower() -> str:
    return str(REPO_ROOT).lower()


def probe_project_rss_bytes() -> int:
    """项目衍生进程 RSS 总量（字节）：当前进程树 ∪ cmdline/exe 引用仓根的进程。

    fail-safe：任何 psutil 异常（权限/消失竞态/缺席）按可测部分返回，绝不抛出——
    探针是常驻周期调用，抛异常=供给线自杀。
    """
    root_lower = _repo_root_lower()
    total = 0
    try:
        import psutil

        me = psutil.Process()
        try:
            total += me.memory_info().rss
        except psutil.Error:
            pass
        # 当前进程树（后代递归，消失即跳过）
        seen: set[int] = {me.pid}
        stack = list(me.children(recursive=False))
        while stack:
            proc = stack.pop()
            try:
                if proc.pid in seen:
                    continue
                seen.add(proc.pid)
                total += proc.memory_info().rss
                stack.extend(proc.children(recursive=False))
            except psutil.Error:
                continue
        # 仓根引用进程（llama-server 加载项目模型/项目内脚本等，去重已计树的）
        for proc in psutil.process_iter(["pid", "cmdline", "exe"]):
            try:
                if proc.info["pid"] in seen:
                    continue
                blob = " ".join(proc.info["cmdline"] or []).lower()
                exe = (proc.info["exe"] or "").lower()
                if root_lower in blob or root_lower in exe:
                    total += proc.memory_info().rss
            except (psutil.Error, psutil.NoSuchProcess):
                continue
    except Exception:  # noqa: BLE001 — 探针绝不抛出（INVARIANTS）
        logger.debug("probe_project_rss_bytes degraded", exc_info=True)
    return total


class OpsAlertFeed:
    """运营告警通知板：规则评估 → 落盘发布 → 只读清单。

    Args:
        board_dir: 通知板目录；None 时经模块级 board_dir()（环境变量可重定向）。
        rules_path: 告警规则 YAML；None 时用 config/alert_rules.yaml。
        module_id: 通知来源标识。
    """

    def __init__(
        self,
        board_dir: str | Path | None = None,
        rules_path: str | Path | None = None,
        module_id: str = "ops-alert-feed",
    ):
        self._board_dir = Path(board_dir) if board_dir else None
        self._rules_path = Path(rules_path) if rules_path else None
        self._module_id = module_id
        self._rules: list[dict] = []
        self._rules_loaded = False
        self._lock = threading.Lock()

    # ── 板存储 ──

    def _dir(self) -> Path:
        return self._board_dir if self._board_dir else board_dir()

    def _board_path(self) -> Path:
        return self._dir() / _BOARD_FILE

    def _read_entries(self) -> list[dict]:
        p = self._board_path()
        if not p.exists():
            return []
        out: list[dict] = []
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    out.append(obj)
            except json.JSONDecodeError:
                logger.warning("ops notification board: skip corrupt line in %s", p)
        return out

    def _write_entries(self, entries: list[dict]) -> None:
        p = self._board_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        content = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries)
        expected = None
        if p.exists():
            # CAS base=读到的原文本 content_sha256（UTF-8 语义 hash，同 safe_write_text 校验口径）
            from zephyr.shared.io.file_utils import content_sha256

            expected = content_sha256(p.read_text(encoding="utf-8"))
        safe_write_text(p, content, expected_base_sha256=expected)

    # ── 发布 / 清单 / 解除 ──

    def publish(
        self,
        *,
        key: str,
        severity: str,
        title: str,
        message: str,
        source: str | None = None,
        labels: dict | None = None,
        silence_window_s: float = 300.0,
        now: float | None = None,
    ) -> dict:
        """发布一条通知（静默窗口内同 key 只刷新不重复）。返回该次操作结果。"""
        import time

        ts = now if now is not None else time.time()
        with self._lock:
            entries = self._read_entries()
            for e in entries:
                if e.get("key") == key and not e.get("resolved_at"):
                    if ts - float(e.get("last_seen", 0)) < silence_window_s:
                        e["last_seen"] = ts
                        e["count"] = int(e.get("count", 1)) + 1
                        self._write_entries(entries)
                        return {"op": "refresh", "id": e.get("id"), "key": key}
            entry = {
                "id": uuid.uuid4().hex[:12],
                "key": key,
                "module_id": self._module_id,
                "severity": severity,
                "title": title,
                "message": message,
                "source": source or self._module_id,
                "labels": labels or {},
                "first_seen": ts,
                "last_seen": ts,
                "count": 1,
                "resolved_at": None,
            }
            entries.append(entry)
            self._write_entries(entries)
            return {"op": "created", "id": entry["id"], "key": key}

    def list_active(self, resolved_retention_s: float = RESOLVED_RETENTION_S, now: float | None = None) -> list[dict]:
        """活动通知清单（未解除 + 近期解除灰显项），first_seen 倒序。"""
        import time

        ts = now if now is not None else time.time()
        entries = self._read_entries()
        out = [
            e
            for e in entries
            if not e.get("resolved_at") or (ts - float(e.get("resolved_at", 0))) <= resolved_retention_s
        ]
        out.sort(key=lambda e: (bool(e.get("resolved_at")), -float(e.get("first_seen", 0))))
        return out

    def resolve(self, key: str, now: float | None = None) -> int:
        """解除指定 key 的全部活动通知，返回解除条数。"""
        import time

        ts = now if now is not None else time.time()
        with self._lock:
            entries = self._read_entries()
            n = 0
            for e in entries:
                if e.get("key") == key and not e.get("resolved_at"):
                    e["resolved_at"] = ts
                    n += 1
            if n:
                self._write_entries(entries)
            return n

    # ── 规则评估与周期 tick ──

    def _load_rules(self) -> list[dict]:
        if self._rules_loaded:
            return self._rules
        path = self._rules_path or (REPO_ROOT / "config" / "alert_rules.yaml")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            self._rules = data.get("rules", []) or []
        except (OSError, yaml.YAMLError):
            self._rules = []
        self._rules_loaded = True
        return self._rules

    def evaluate_memory_rules(self, value: float) -> list[dict]:
        """对内存类规则（metric 含 memory 的字节型规则）评估，返回触发规则列表。"""
        triggered: list[dict] = []
        for rule in self._load_rules():
            metric = str(rule.get("metric", ""))
            if "memory" not in metric or "bytes" not in metric:
                continue
            condition = str(rule.get("condition", ""))
            if self._check(value, condition):
                triggered.append(rule)
        return triggered

    @staticmethod
    def _check(value: float, condition: str) -> bool:
        # 复用 AlertSubsystem 的条件解析（零复制语义）；静态方法无实例依赖
        from zephyr.infrastructure.system_telemetry.alerts import AlertSubsystem

        return AlertSubsystem._check_condition(value, condition)

    def tick(
        self,
        probe: Callable[[], int] | None = None,
        now: float | None = None,
    ) -> dict:
        """一个监测周期：探针→评估→发布/解除。返回周期摘要（供日志与测试断言）。

        fail-safe：探针/评估异常降级为 {"ok": False}，绝不抛出——调用方是常驻线程。
        """
        import time

        ts = now if now is not None else time.time()
        probe_fn = probe or probe_project_rss_bytes
        try:
            value = probe_fn()
        except Exception as exc:  # noqa: BLE001 — INVARIANTS: fail-safe
            logger.debug("ops alert feed probe failed: %s", exc)
            return {"ok": False, "reason": f"probe failed: {exc}", "ts": ts}

        try:
            triggered = self.evaluate_memory_rules(float(value))
        except Exception as exc:  # noqa: BLE001 — 规则评估异常降级（红蓝 2026-09-16）
            logger.debug("ops alert feed evaluate failed: %s", exc)
            return {"ok": False, "reason": f"evaluate failed: {exc}", "ts": ts}
        ops: list[dict] = []
        for rule in triggered:
            if str(rule.get("severity", "")).lower() != "critical":
                continue
            silence = self._parse_silence(rule.get("silence_window", "5m"))
            try:
                ops.append(
                    self.publish(
                        key=str(rule.get("id", "ALERT-UNKNOWN")),
                        severity="critical",
                        title=str(rule.get("name", "oom_risk")),
                        message=str(rule.get("description", "")) + f"（实测 {value} 字节）",
                        labels={"metric": rule.get("metric"), "value": value},
                        silence_window_s=silence,
                        now=ts,
                    )
                )
            except Exception as exc:  # noqa: BLE001 — 板 CAS 拒写降级不炸 tick（红蓝 2026-09-16）
                logger.warning("ops alert feed publish failed: %s", exc)
                ops.append({"op": "failed", "key": rule.get("id"), "reason": str(exc)[:120]})
        # 无 critical 触发 → 按滞回解除既有 OOM 项
        if not any(str(r.get("severity")).lower() == "critical" for r in triggered):
            for rule in self._load_rules():
                if "memory" not in str(rule.get("metric", "")):
                    continue
                condition = str(rule.get("condition", ""))
                threshold = self._threshold_of(condition)
                if threshold is None:
                    continue
                if float(value) <= threshold * RESOLVE_HYSTERESIS:
                    n = self.resolve(str(rule.get("id", "")), now=ts)
                    if n:
                        ops.append({"op": "resolved", "key": rule.get("id"), "count": n})
        return {"ok": True, "ts": ts, "value": value, "triggered": [r.get("id") for r in triggered], "ops": ops}

    @staticmethod
    def _threshold_of(condition: str) -> float | None:
        try:
            return float(str(condition).strip()[1:])
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse_silence(raw: object) -> float:
        """silence_window 字符串（"5m"/"30s"/"1d"）→ 秒；解析失败缺省 300s。"""
        try:
            s = str(raw).strip()
            unit = s[-1]
            num = float(s[:-1])
            return {"s": num, "m": num * 60, "h": num * 3600, "d": num * 86400}.get(unit, 300.0)
        except (ValueError, TypeError, IndexError):
            return 300.0


__all__ = [
    "FIRST_TICK_DELAY_S",
    "RESOLVED_RETENTION_S",
    "RESOLVE_HYSTERESIS",
    "TICK_INTERVAL_S",
    "OpsAlertFeed",
    "board_dir",
    "probe_project_rss_bytes",
]
