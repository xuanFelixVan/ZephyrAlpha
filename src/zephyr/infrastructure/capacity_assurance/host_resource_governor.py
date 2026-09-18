# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.host_resource_governor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__; psutil(实探);
#   ctypes.kernel32.GlobalMemoryStatusEx(Windows 提交内存);
#   zephyr.infrastructure.system_telemetry.alerts(阈值条件解析, 延迟 import);
#   zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed(通知板发布, 延迟 import)
# [CONSUMERS] zephyr.trading.process_reaper(reap 尾部水位真闸, OS 计划任务 10min 心跳驱动);
#   tests/autonomy/test_host_resource_governor.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 探针必须是实探——禁硬编码读数（历史缺陷：probe() 曾恒返 12.5%/OK 的假通道）;
#   阈值真源=config/alert_rules.yaml，代码零副本（缺规则=不告警并 loud warning，不臆造阈值）;
#   探针/发布失败不得抛给宿主（收割器每 10min 跑一次，反噬宿主=把保命链变成事故源）;
#   非 Windows 平台 commit 面缺席=按 RAM 面降级并如实标注 note，禁拿 RAM 冒充 commit
# [MODIFY-GUARD] config/alert_rules.yaml（阈值真源，本件只读禁改）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OSError/yaml.YAMLError 收入返回值的 note 字段；probe 系列函数永不抛
# [TESTS] tests/autonomy/test_host_resource_governor.py
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/host_resource_governor.py 迁移至
#   infrastructure/capacity_assurance/host_resource_governor.py（blueprint actual_disk_path 真源）。
"""
host_resource_governor.py — 主机资源治理 (B17, DD91, TASK-017) + 全系统内存水位真闸 (BRK-066)

历史缺陷（2026-09-18 治本，全流通战役 BRK-066）：`probe()` 曾返回硬编码
`ResourceStatus(16000, 2000, 12.5, degraded=False, "OK")`——docstring 自称"psutil RAM probe"
而全件没有一个 psutil 调用。这是**假通道**，比无人看护更坏：它让"水位有人看"在评审里
过关，而把 20 核打到 99%、RAM 可用从 32GB 掉到 17.6GB 的那些时刻它恒报 OK。
GOMAP GOM-L2 的断点记载"无人看护全系统提交内存水位"根因即在此。

本件现为实探，三段：
1. `probe_system_watermark()` — RAM 用量 + **Windows 提交内存（commit charge）** + CPU；
   commit 面经 `GlobalMemoryStatusEx` 的 `ullTotalPageFile/ullAvailPageFile`（这才是
   "提交内存"口径，RAM 面替代不了——页面文件扩容后上限会变，本仓曾实证需要扩容）。
2. `check_system_watermark()` — 按 `config/alert_rules.yaml` 的 metric 规则评估
   （条件解析复用 `AlertSubsystem._check_condition`，零第二口径）→ 命中即发布到
   既有通知板 `OpsAlertFeed`（前端 promotion 页是唯一出口，飞书/SMTP 已 2026-09-15 裁撤）。
   规则真源在 YAML：代码里没有一条阈值。
3. `HostResourceGovernor` — 保留原 API（ResourceStatus/check_model_loading，25% 模型装载线）。

消费方：`zephyr.trading.process_reaper`（已注册的 OS 计划任务，10min 一次 one-shot），
即"自动触发"复用现存心跳脉冲，本件零新建 cron/Timer/sleep-loop（宪法 §9.3）。
告警指标面：system.commit_mem_pct / system.mem_avail_gb / system.cpu_percent。
# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/capacity_assurance/host_resource_governor.yaml
"""

from __future__ import annotations

import ctypes
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

_GIB: Final[float] = 1024.0 ** 3
#: 本件产出的指标名 → 取值口径（**告警**阈值与严重度真源在 config/alert_rules.yaml，此处零副本；
#: 下方 _MODEL_DEGRADE_PCT 是 DD91 模型装载降级的内置保守线，不是告警阈值口径）
METRIC_COMMIT_PCT: Final[str] = "system.commit_mem_pct"
METRIC_MEM_AVAIL_GB: Final[str] = "system.mem_avail_gb"
METRIC_RAM_PCT: Final[str] = "system.mem_used_pct"
METRIC_CPU_PCT: Final[str] = "system.cpu_percent"
DEFAULT_SILENCE_S: Final[float] = 1800.0
_MODEL_DEGRADE_PCT: Final[float] = 90.0
#: 本件**可**供给的全部指标名（规则筛选面）。注意与 `SystemWatermark.metric_values()`
#: 的区别：后者是"本快照实际有值的面"（非 Windows 时 commit 缺席），前者决定哪些规则行
#: 归本件评估——用后者做筛选会让 commit 规则在缺省/失败态被永久过滤掉（首版即踩此坑，
#: 由 tests/autonomy/test_system_watermark_gate.py::test_breach_publishes_to_board 抓出）。
_SUPPLIED_METRICS: Final[frozenset[str]] = frozenset(
    {METRIC_COMMIT_PCT, METRIC_MEM_AVAIL_GB, METRIC_RAM_PCT, METRIC_CPU_PCT}
)
_RULES_RELPATH: Final[str] = "config/alert_rules.yaml"


@dataclass
class ResourceStatus:
    total_ram_mb: float
    used_ram_mb: float
    usage_pct: float
    degraded: bool
    recommendation: str


@dataclass(frozen=True)
class SystemWatermark:
    """全系统水位实测快照（commit 面非 Windows 时为 None，禁拿 RAM 冒充）."""

    ram_total_gb: float
    ram_avail_gb: float
    ram_used_pct: float
    commit_total_gb: float | None
    commit_used_gb: float | None
    commit_pct: float | None
    cpu_pct: float
    degraded: bool = False
    note: str = ""

    def metric_values(self) -> dict[str, float]:
        """本快照可供给告警引擎的指标值（缺席面不产出，绝不假装有值）."""
        values = {
            METRIC_RAM_PCT: self.ram_used_pct,
            METRIC_MEM_AVAIL_GB: self.ram_avail_gb,
            METRIC_CPU_PCT: self.cpu_pct,
        }
        if self.commit_pct is not None and self.commit_total_gb is not None:
            values[METRIC_COMMIT_PCT] = self.commit_pct
        return values


class _MemoryStatusEx(ctypes.Structure):
    """Windows GLOBALSTATUSEX 布局（GlobalMemoryStatusEx 唯一能给出 commit 面的入口）."""

    _fields_ = [  # noqa: RUF012  ctypes 布局要求可变序列
        ("dwLength", ctypes.c_uint32),
        ("dwMemoryLoad", ctypes.c_uint32),
        ("ullTotalPhys", ctypes.c_uint64),
        ("ullAvailPhys", ctypes.c_uint64),
        ("ullTotalPageFile", ctypes.c_uint64),
        ("ullAvailPageFile", ctypes.c_uint64),
        ("ullTotalVirtual", ctypes.c_uint64),
        ("ullAvailVirtual", ctypes.c_uint64),
        ("ullAvailExtendedVirtual", ctypes.c_uint64),
    ]


def _commit_charge() -> tuple[float, float, float] | None:
    """Windows 提交内存 (limit_gb, used_gb, pct)；非 Windows/调用失败=None."""
    if not hasattr(ctypes.windll, "kernel32"):  # pragma: no cover - 非 Windows 分支
        return None
    try:
        stat = _MemoryStatusEx()
        stat.dwLength = ctypes.sizeof(_MemoryStatusEx)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return None
        limit = float(stat.ullTotalPageFile)
        if limit <= 0:
            return None
        used = limit - float(stat.ullAvailPageFile)
        return limit / _GIB, used / _GIB, round(100.0 * used / limit, 2)
    except Exception as exc:  # noqa: BLE001 — 探针永不抛（INVARIANTS）
        logger.warning("commit charge 探针失败（本周期 commit 面缺席，不冒充）: %r", exc)
        return None


def probe_system_watermark() -> SystemWatermark:
    """全系统水位实探（RAM + commit + CPU）。psutil 不可用时 RAM/CPU 面=None→0 并标注."""
    note = ""
    ram_total_gb = ram_avail_gb = ram_used_pct = 0.0
    cpu_pct = 0.0
    try:
        import psutil

        vm = psutil.virtual_memory()
        ram_total_gb = round(vm.total / _GIB, 2)
        ram_avail_gb = round(vm.available / _GIB, 2)
        ram_used_pct = float(vm.percent)
        cpu_pct = float(psutil.cpu_percent(interval=None))
    except Exception as exc:  # noqa: BLE001 — 探针永不抛（INVARIANTS）
        note = f"psutil 探测失败: {exc!r}"
        logger.warning("host_resource_governor psutil 探测失败，水位面失真: %r", exc)
    commit = _commit_charge()
    if commit is None and not note:
        note = "commit 面不可得（非 Windows 或 API 失败）——按 RAM 面降级，已如实标注"
    commit_total_gb = commit_used_gb = commit_pct = None
    if commit is not None:
        commit_total_gb, commit_used_gb, commit_pct = commit
    degraded = bool(ram_total_gb and ram_used_pct >= _MODEL_DEGRADE_PCT) or bool(
        commit_pct is not None and commit_pct >= _MODEL_DEGRADE_PCT
    )
    return SystemWatermark(
        ram_total_gb=ram_total_gb,
        ram_avail_gb=ram_avail_gb,
        ram_used_pct=ram_used_pct,
        commit_total_gb=commit_total_gb,
        commit_used_gb=commit_used_gb,
        commit_pct=commit_pct,
        cpu_pct=cpu_pct,
        degraded=degraded,
        note=note,
    )


def _load_watermark_rules(rules_path: str | Path | None) -> list[dict]:
    """读 alert_rules.yaml 中 metric 落在本件供给面的规则（真源=YAML，零硬编码阈值）."""
    import yaml

    path = Path(rules_path) if rules_path else REPO_ROOT / _RULES_RELPATH
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        logger.error("水位规则不可读 %s: %r——本周期不评估（宁漏不假绿）", path, exc)
        return []
    produced = set(_SUPPLIED_METRICS)
    rules = [
        r for r in (data.get("rules") or []) if str(r.get("metric", "")).strip() in produced
    ]
    if not rules:
        logger.warning(
            "config/alert_rules.yaml 无 system.* 水位规则（%s）——内存水位闸不生效，请补规则行",
            ", ".join(sorted(produced)),
        )
    return rules


def _rule_silence_s(rule: dict) -> float:
    """静默窗口秒（缺省 DEFAULT_SILENCE_S；解析口径与 OpsAlertFeed._parse_silence 同族）."""
    raw = str(rule.get("silence_window", "")).strip()
    if raw.endswith("m"):
        return float(raw[:-1]) * 60.0
    if raw.endswith("h"):
        return float(raw[:-1]) * 3600.0
    if raw.endswith("s"):
        return float(raw[:-1])
    return DEFAULT_SILENCE_S


def check_system_watermark(
    *,
    rules_path: str | Path | None = None,
    board_dir: str | Path | None = None,
    publish: bool = True,
    watermark: SystemWatermark | None = None,
) -> dict[str, Any]:
    """一个水位评估周期：实探 → 按 YAML 规则判定 → 命中即发通知板。永不抛.

    Returns:
        {"watermark": {...}, "breached": [rule_id...], "published": [key...], "note": str}
    """
    wm = watermark or probe_system_watermark()
    values = wm.metric_values()
    breached: list[dict] = []
    for rule in _load_watermark_rules(rules_path):
        value = values.get(str(rule.get("metric", "")).strip())
        if value is None:
            continue
        try:
            from zephyr.infrastructure.system_telemetry.alerts import AlertSubsystem

            hit = AlertSubsystem._check_condition(value, str(rule.get("condition", "")))
        except Exception as exc:  # noqa: BLE001 — 判定器异常不炸宿主（但出声）
            logger.error("水位规则 %s 评估异常: %r", rule.get("id"), exc)
            continue
        if hit:
            breached.append(dict(rule))
    published: list[str] = []
    if breached and publish:
        try:
            from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

            feed = OpsAlertFeed(board_dir=board_dir, rules_path=rules_path,
                                module_id="host-resource-governor")
            for rule in breached:
                metric = str(rule.get("metric", "")).strip()
                feed.publish(
                    key=str(rule.get("id", "ALERT-WATERMARK")),
                    severity=str(rule.get("severity", "critical")),
                    title=str(rule.get("name", "system_watermark")),
                    message=(
                        f"{rule.get('description', '')}（实测 {metric}={values.get(metric)}，"
                        f"条件 {rule.get('condition')}）"
                    ),
                    source="capacity_assurance.host_resource_governor",
                    labels={"metric": metric, "value": values.get(metric),
                            "commit_pct": wm.commit_pct, "note": wm.note},
                    silence_window_s=_rule_silence_s(rule),
                )
                published.append(str(rule.get("id")))
        except Exception as exc:  # noqa: BLE001 — 发布失败必须出声（水位仍已判定）
            logger.error("水位通知板发布失败（判定仍生效，请人工看板）: %r", exc)
    return {
        "watermark": {
            "ram_total_gb": wm.ram_total_gb,
            "ram_avail_gb": wm.ram_avail_gb,
            "ram_used_pct": wm.ram_used_pct,
            "commit_total_gb": wm.commit_total_gb,
            "commit_used_gb": wm.commit_used_gb,
            "commit_pct": wm.commit_pct,
            "cpu_pct": wm.cpu_pct,
            "degraded": wm.degraded,
        },
        "breached": [str(r.get("id")) for r in breached],
        "published": published,
        "note": wm.note,
    }


class HostResourceGovernor:
    """psutil RAM probe; model loading < 25% total RAM; 超限降级 (DD91)."""

    def probe(self) -> ResourceStatus:
        """实探 RAM（原硬编码 12.5%/OK 假通道已治本，见模块 docstring）."""
        wm = probe_system_watermark()
        used_mb = max(0.0, (wm.ram_total_gb - wm.ram_avail_gb)) * 1024.0
        if wm.ram_total_gb <= 0:
            return ResourceStatus(0.0, 0.0, 0.0, True, "PROBE-FAILED: psutil 不可用，水位失真")
        recommendation = "OK"
        if wm.degraded:
            recommendation = f"DEGRADED: RAM {wm.ram_used_pct}% / commit {wm.commit_pct}%"
        return ResourceStatus(
            total_ram_mb=round(wm.ram_total_gb * 1024.0, 1),
            used_ram_mb=round(used_mb, 1),
            usage_pct=wm.ram_used_pct,
            degraded=wm.degraded,
            recommendation=recommendation,
        )

    def probe_watermark(self) -> SystemWatermark:
        """全系统水位快照（RAM + 提交内存 + CPU）——供门禁/调度/看板取用."""
        return probe_system_watermark()

    def check_model_loading(self, model_size_mb: float) -> bool:
        status = self.probe()
        return model_size_mb < status.total_ram_mb * 0.25
