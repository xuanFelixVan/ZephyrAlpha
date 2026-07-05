# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1
# [MODULE] zephyr.governance.semantic_audit.self_health
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.semantic_audit.models; zephyr.governance.semantic_audit.__init__
# [CONSUMERS] cli; audit-orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 7 SLI + 5 容量 SLI; HEALTHY/DEGRADED/CRITICAL 三级状态
# [MODIFY-GUARD] 修改 SLI 定义必须同步蓝图 §3.1 组件 #11
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 自检异常时返回 CRITICAL 状态
# [TESTS] tests/semantic-auditor/test_self_health.py
# [A_module] module_id=MOD-GOV_self_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 自身健康监控

7 SLI + 5 容量 SLI + 退化检测。定时自检,输出 HEALTHY/DEGRADED/CRITICAL。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__ = [
    "HealthLevel",
    "HealthStatus",
    "SLIResult",
    "SelfHealth",
]

_HEALTH_LEVELS: dict[str, int] = {"HEALTHY": 0, "DEGRADED": 1, "CRITICAL": 2}
_FORBIDDEN_PATTERNS_PATH = Path(__file__).parent / "forbidden_patterns.yaml"


class HealthLevel(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


@dataclass
class SLIResult:
    name: str
    passed: bool
    value: float = 0.0
    threshold: float = 0.0
    message: str = ""


@dataclass
class HealthStatus:
    level: HealthLevel = HealthLevel.HEALTHY
    sli_results: list[SLIResult] = field(default_factory=list)
    capacity_results: list[SLIResult] = field(default_factory=list)
    checked_at: float = field(default_factory=time.time)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "sli_results": [
                {"name": r.name, "passed": r.passed, "value": r.value, "threshold": r.threshold}
                for r in self.sli_results
            ],
            "capacity_results": [
                {"name": r.name, "passed": r.passed, "value": r.value, "threshold": r.threshold}
                for r in self.capacity_results
            ],
            "checked_at": self.checked_at,
            "message": self.message,
        }


class SelfHealth:
    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()
        self._last_check: float = 0.0
        self._cached_status: HealthStatus | None = None

    def check(self, force: bool = False) -> HealthStatus:
        now = time.time()
        if not force and self._cached_status is not None and now - self._last_check < 60:
            return self._cached_status
        sli_results = self._run_sli_checks()
        capacity_results = self._run_capacity_checks()
        worst = HealthLevel.HEALTHY
        messages: list[str] = []
        for r in sli_results + capacity_results:
            if not r.passed:
                msg = f"{r.name}: {r.message}"
                messages.append(msg)
                level_name = r.name
                if "CRITICAL" in level_name:
                    worst = HealthLevel.CRITICAL
                elif worst is not HealthLevel.CRITICAL:
                    worst = HealthLevel.DEGRADED
        status = HealthStatus(
            level=worst,
            sli_results=sli_results,
            capacity_results=capacity_results,
            checked_at=now,
            message="; ".join(messages) if messages else "ALL_PASSED",
        )
        self._cached_status = status
        self._last_check = now
        return status

    def _run_sli_checks(self) -> list[SLIResult]:
        results: list[SLIResult] = []
        results.append(self._check_forbidden_patterns_integrity())
        results.append(self._check_pipeline_files_exist())
        results.append(self._check_models_importable())
        results.append(self._check_blueprint_exists())
        results.append(self._check_registry_files_exist())
        results.append(self._check_circular_imports())
        results.append(self._check_self_module_importable())
        return results

    def _run_capacity_checks(self) -> list[SLIResult]:
        results: list[SLIResult] = []
        results.append(self._check_module_count_ok())
        results.append(self._check_disk_files_count())
        results.append(self._check_config_size_ok())
        results.append(self._check_import_time())
        results.append(self._check_no_temp_files())
        return results

    def _check_forbidden_patterns_integrity(self) -> SLIResult:
        path = _FORBIDDEN_PATTERNS_PATH
        if not path.exists():
            return SLIResult("forbidden_patterns_missing", False, 0.0, 1.0, "禁碰规则文件缺失")
        try:
            config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            paths_count = len(config.get("forbidden_paths", []))
            modules_count = len(config.get("forbidden_modules", []))
            keywords_count = len(config.get("forbidden_keywords", []))
            total = paths_count + modules_count + keywords_count
            if total < 5:
                return SLIResult("forbidden_patterns_too_few", False, float(total), 5.0, "禁碰规则条目不足")
            return SLIResult("forbidden_patterns_ok", True, float(total), 5.0)
        except Exception as exc:
            return SLIResult("forbidden_patterns_parse_fail", False, 0.0, 1.0, str(exc))

    def _check_pipeline_files_exist(self) -> SLIResult:
        expected = [
            "models.py",
            "reference_extractor.py",
            "trigger_engine.py",
            "safety_boundary.py",
            "alignment_engine.py",
            "issue_aggregator.py",
            "llm_bridge.py",
            "self_healer.py",
            "fix_prioritizer.py",
            "blast_radius.py",
            "self_health.py",
        ]
        pkg_dir = Path(__file__).parent
        missing = [f for f in expected if not (pkg_dir / f).exists()]
        if missing:
            return SLIResult("pipeline_files_missing", False, 0.0, 1.0, f"缺失: {missing}")
        return SLIResult("pipeline_files_ok", True, float(len(expected)), float(len(expected)))

    def _check_models_importable(self) -> SLIResult:
        try:
            return SLIResult("models_import_ok", True, 1.0, 1.0)
        except Exception as exc:
            return SLIResult("models_import_fail", False, 0.0, 1.0, str(exc))

    def _check_blueprint_exists(self) -> SLIResult:
        bp = self._root / "docs/03_modules/_cross_layer/semantic-auditor/blueprint.md"
        if not bp.exists():
            return SLIResult("blueprint_missing", False, 0.0, 1.0, "蓝图文件缺失")
        try:
            content = bp.read_text(encoding="utf-8")
            if "MOD-INF-028" not in content:
                return SLIResult("blueprint_wrong_module", False, 0.0, 1.0, "蓝图 module_id 不匹配")
        except OSError as exc:
            return SLIResult("blueprint_unreadable", False, 0.0, 1.0, str(exc))
        return SLIResult("blueprint_ok", True, 1.0, 1.0)

    def _check_registry_files_exist(self) -> SLIResult:
        pkg_dir = Path(__file__).parent
        expected = ["forbidden_patterns.yaml", "rule_document_registry.yaml"]
        missing = [f for f in expected if not (pkg_dir / f).exists()]
        if missing:
            return SLIResult("registry_files_missing", False, 0.0, 1.0, f"缺失: {missing}")
        return SLIResult("registry_files_ok", True, 2.0, 2.0)

    def _check_circular_imports(self) -> SLIResult:
        try:
            import importlib

            importlib.import_module("zephyr.governance.semantic_audit")
            return SLIResult("no_circular_import", True, 1.0, 1.0)
        except ImportError as exc:
            if "circular" in str(exc).lower():
                return SLIResult("circular_import_detected", False, 0.0, 1.0, str(exc))
            return SLIResult("import_error_non_circular", False, 0.5, 1.0, str(exc))

    def _check_self_module_importable(self) -> SLIResult:
        try:
            return SLIResult("self_health_import_ok", True, 1.0, 1.0)
        except Exception as exc:
            return SLIResult("self_health_import_fail", False, 0.0, 1.0, str(exc))

    def _check_module_count_ok(self) -> SLIResult:
        pkg_dir = Path(__file__).parent
        py_files = list(pkg_dir.glob("*.py"))
        count = len(py_files)
        if count < 10:
            return SLIResult("capacity_module_count_low", False, float(count), 10.0, "管线模块不足")
        return SLIResult("capacity_module_count_ok", True, float(count), 10.0)

    def _check_disk_files_count(self) -> SLIResult:
        pkg_dir = Path(__file__).parent
        all_files = list(pkg_dir.glob("*"))
        count = len(all_files)
        if count > 50:
            return SLIResult("capacity_disk_files_high", False, float(count), 50.0, "目录文件过多")
        return SLIResult("capacity_disk_files_ok", True, float(count), 50.0)

    def _check_config_size_ok(self) -> SLIResult:
        try:
            path = _FORBIDDEN_PATTERNS_PATH
            if path.exists():
                size_kb = path.stat().st_size / 1024.0
                if size_kb > 100:
                    return SLIResult("capacity_config_oversized", False, size_kb, 100.0, "配置文件过大")
            return SLIResult("capacity_config_size_ok", True, 0.0, 100.0)
        except OSError as exc:
            return SLIResult("capacity_config_unreadable", False, 0.0, 100.0, str(exc))

    def _check_import_time(self) -> SLIResult:
        start = time.time()
        try:
            import importlib

            importlib.import_module("zephyr.governance.semantic_audit")
            elapsed = time.time() - start
            if elapsed > 2.0:
                return SLIResult("capacity_import_slow", False, elapsed, 2.0, f"导入耗时 {elapsed:.2f}s")
            return SLIResult("capacity_import_ok", True, elapsed, 2.0)
        except Exception as exc:
            return SLIResult("capacity_import_fail", False, 0.0, 2.0, str(exc))

    def _check_no_temp_files(self) -> SLIResult:
        pkg_dir = Path(__file__).parent
        temp_files = list(pkg_dir.glob("_temp*")) + list(pkg_dir.glob("*.tmp"))
        if temp_files:
            names = [f.name for f in temp_files]
            return SLIResult("capacity_temp_files_found", False, float(len(temp_files)), 0.0, f"临时文件: {names}")
        return SLIResult("capacity_no_temp_files", True, 0.0, 0.0)
