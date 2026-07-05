# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-IDE
# [MODULE] zephyr.trading.speed_baseline_checker
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] scripts/ide_health_service.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] script-manifest.yaml 是脚本基线唯一数据源; process_iter 必须同时检查 cmdline + cwd;
# [MODIFY-GUARD] 修改分类阈值前必须确认与 zombie_scanner 的分类不重叠冲突
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MANIFEST_NOT_FOUND: 记录错误并返回空结果，不阻断守护进程循环;
# [TESTS] test_speed_baseline_checker.py
# [A_module] module_id=MOD-ORC_speed_baseline_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

import psutil
import yaml

_MANIFEST_PATH = REPO_ROOT / "scripts" / "script-manifest.yaml"
_BASELINE_CACHE_TTL = 300.0

_LONG_RUNNING_KEYWORDS = [
    "ide_health_service",
    "ide_health_nanny",
    "_nanny",
    "daemon",
    "windows_service",
]


class SpeedCategory(Enum):
    NORMAL = "normal"
    SLOW = "slow"
    VERY_SLOW = "very_slow"
    CRITICAL_SLOW = "critical_slow"


# 5.137.2 修复：会话间隔阈值魔数提取为命名常量
_UNMATCHED_RUNTIME_CRITICAL_S = 600
_UNMATCHED_DEFAULT_BASELINE_S = 60


SPEED_THRESHOLDS = {
    SpeedCategory.SLOW: 0.8,
    SpeedCategory.VERY_SLOW: 1.0,
    SpeedCategory.CRITICAL_SLOW: 2.0,
}


@dataclass
class SpeedAnomaly:
    pid: int
    category: SpeedCategory
    script_name: str
    cmdline: str
    runtime_s: float
    timeout_baseline_s: float
    ratio: float


@dataclass
class SpeedCheckResult:
    scanned: int = 0
    anomalies: list[SpeedAnomaly] = field(default_factory=list)
    classifications: dict = field(default_factory=dict)


class SpeedBaselineChecker:
    def __init__(self):
        self._manifest_path: Path = _MANIFEST_PATH
        self._cache: dict[str, int] = {}
        self._cache_loaded_at: float = 0.0

    def _load_script_baselines(self) -> dict[str, int]:
        now = time.time()
        if self._cache and (now - self._cache_loaded_at) < _BASELINE_CACHE_TTL:
            return self._cache
        try:
            raw = yaml.safe_load(self._manifest_path.read_text(encoding="utf-8"))
            baselines: dict[str, int] = {}
            for entry in raw.get("scripts", []):
                name = entry.get("name", "")
                timeout = entry.get("timeout_seconds", 60)
                if name and isinstance(timeout, (int, float)):
                    baselines[name] = int(timeout)
            self._cache = baselines
            self._cache_loaded_at = now
            return baselines
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"[SpeedBaselineChecker] MANIFEST_NOT_FOUND: {e}")
            return self._cache if self._cache else {}

    @staticmethod
    def _classify(runtime_s: float, baseline_s: int) -> SpeedCategory:
        if baseline_s <= 0:
            baseline_s = 60
        ratio = runtime_s / baseline_s
        if ratio < SPEED_THRESHOLDS[SpeedCategory.SLOW]:
            return SpeedCategory.NORMAL
        if ratio < SPEED_THRESHOLDS[SpeedCategory.VERY_SLOW]:
            return SpeedCategory.SLOW
        if ratio < SPEED_THRESHOLDS[SpeedCategory.CRITICAL_SLOW]:
            return SpeedCategory.VERY_SLOW
        return SpeedCategory.CRITICAL_SLOW

    def check_active_processes(self) -> SpeedCheckResult:
        baselines = self._load_script_baselines()
        project_root_str = str(REPO_ROOT)
        result = SpeedCheckResult()

        for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time", "cwd"]):
            try:
                cmdline_list = proc.info.get("cmdline") or []
                cmdline = " ".join(cmdline_list)
                cwd = proc.info.get("cwd") or ""
                belongs_to_project = (project_root_str in cmdline) or (project_root_str in cwd)
                if not belongs_to_project:
                    continue
                if proc.info["name"].lower() not in ("python", "python.exe", "python3"):
                    continue
                if any(kw in cmdline.lower() for kw in _LONG_RUNNING_KEYWORDS):
                    continue
                result.scanned += 1
                runtime_s = time.time() - (proc.info.get("create_time") or time.time())
                matched_script = None
                matched_baseline = 60
                for cmd_part in cmdline_list:
                    for script_name, timeout in baselines.items():
                        if script_name in cmd_part:
                            matched_script = script_name
                            matched_baseline = timeout
                            break
                    if matched_script:
                        break
                if not matched_script:
                    if runtime_s > _UNMATCHED_RUNTIME_CRITICAL_S:
                        matched_script = "_unknown_"
                        matched_baseline = _UNMATCHED_DEFAULT_BASELINE_S
                    else:
                        continue
                category = self._classify(runtime_s, matched_baseline)
                if category is SpeedCategory.NORMAL:
                    continue
                ratio = runtime_s / max(matched_baseline, 1)
                anomaly = SpeedAnomaly(
                    pid=proc.info["pid"],
                    category=category,
                    script_name=matched_script,
                    cmdline=cmdline[:200],
                    runtime_s=round(runtime_s, 1),
                    timeout_baseline_s=matched_baseline,
                    ratio=round(ratio, 2),
                )
                result.anomalies.append(anomaly)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        result.classifications = {
            "slow": len([a for a in result.anomalies if a.category is SpeedCategory.SLOW]),
            "very_slow": len([a for a in result.anomalies if a.category is SpeedCategory.VERY_SLOW]),
            "critical_slow": len([a for a in result.anomalies if a.category is SpeedCategory.CRITICAL_SLOW]),
        }
        return result


def check_speed_anomalies() -> SpeedCheckResult:
    checker = SpeedBaselineChecker()
    return checker.check_active_processes()


__all__ = [
    "SPEED_THRESHOLDS",
    "SpeedAnomaly",
    "SpeedBaselineChecker",
    "SpeedCategory",
    "SpeedCheckResult",
    "check_speed_anomalies",
]
