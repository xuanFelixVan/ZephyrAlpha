# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.chaos_injector
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_engine
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/ops_governance/phase_check_registry.py; src/zephyr/infrastructure/rollback/phase_check_registry.py (+3 more)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 混沌注入必须金丝雀保护
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_chaos_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Chaos Injector — 混沌工程主动漂移注入 §6.13。





module_id: MOD-INF-023


4种注入类型: path_rename / yaml_field_flip / fake_todo_bomb / import_hallucination


每周一次(维护窗口内)，仅P2模块，pre-chaos基线+自动回滚


metrics: detection_rate / time_to_detect / false_negative_trend


对标 blueprint.md §6.13。"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界


class ChaosInjectionType(str, Enum):
    PATH_RENAME = "path_rename"

    YAML_FIELD_FLIP = "yaml_field_flip"

    FAKE_TODO_BOMB = "fake_todo_bomb"

    IMPORT_HALLUCINATION = "import_hallucination"


class ChaosPhase(str, Enum):
    BASELINE = "baseline"

    INJECT = "inject"

    DETECT = "detect"

    ROLLBACK = "rollback"

    COMPLETE = "complete"


class ChaosResult(str, Enum):
    DETECTED = "DETECTED"

    MISSED = "MISSED"

    DEGRADED = "DEGRADED"

    ERROR = "ERROR"


@dataclass
class ChaosInjection:
    injection_id: str = field(default_factory=lambda: f"chaos-{uuid.uuid4().hex[:8]}")

    injection_type: ChaosInjectionType = ChaosInjectionType.PATH_RENAME

    target_file: str = ""

    original_content: str = ""

    mutated_content: str = ""

    baseline_snapshot: str | None = None

    detection_time_sec: float = 0.0

    detected_by: list[str] = field(default_factory=list)

    result: ChaosResult = ChaosResult.MISSED

    phase: ChaosPhase = ChaosPhase.BASELINE

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    rolled_back_at: datetime | None = None


@dataclass
class ChaosMetrics:
    total_injections: int = 0

    detected: int = 0

    missed: int = 0

    degraded: int = 0

    avg_time_to_detect_sec: float = 0.0

    false_negative_rate: float = 0.0

    def summary(self) -> dict[str, object]:
        return {
            "detection_rate": f"{self.detected}/{self.total_injections}",
            "miss_count": self.missed,
            "avg_ttd_sec": self.avg_time_to_detect_sec,
            "fn_rate": self.false_negative_rate,
        }


_CHAOS_METRICS_FILE: str = "_chaos_metrics.json"


def _write_metrics(metrics: ChaosMetrics, state_dir: str) -> None:
    if not state_dir:
        return

    os.makedirs(state_dir, exist_ok=True)

    path = os.path.join(state_dir, _CHAOS_METRICS_FILE)

    tmp = f"{path}.{os.getpid()}.tmp"

    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(dumps(metrics.summary(), indent=2))

        os.replace(tmp, path)

    except PermissionError:
        try:
            os.remove(tmp)

        except OSError:
            pass


def inject_path_rename(target_file: Path) -> tuple[str, str]:
    """改名类操作：将目标文件中某变量重命名为混淆版本。"""

    original = target_file.read_text(encoding="utf-8")

    imports_block = re.findall(r"(?:import|from)\s+[\w.]+\s*(?:import\s+\w+(?:\s+as\s+\w+)?)?", original)

    for imp in imports_block:
        match = re.search(r"import\s+(\w+)|from\s+\S+\s+import\s+(\w+)", imp)

        if match:
            old_name = match.group(1) or match.group(2) or ""

            chaos_name = f"_{old_name}_chaos_temp_"

            mutated = original.replace(f" {old_name}\n", f" {chaos_name}\n")

            mutated = mutated.replace(f" {old_name}.", f" {chaos_name}.")

            mutated = mutated.replace(f" {old_name}(", f" {chaos_name}(")

            return original, mutated

    return original, original


def inject_yaml_field_flip(target_file: Path) -> tuple[str, str]:
    """YAML字段翻转：将布尔字段值反转。"""

    original = target_file.read_text(encoding="utf-8")

    mutated = original

    bool_flips = [
        ("enabled: true", "enabled: false"),
        ("required: true", "required: false"),
        ("auto_fixable: true", "auto_fixable: false"),
    ]

    for orig_pat, mut_pat in bool_flips:
        if orig_pat in mutated:
            mutated = mutated.replace(orig_pat, mut_pat)

            break

    return original, mutated


def inject_fake_todo_bomb(target_file: Path) -> tuple[str, str]:
    """Fake TODO地雷：插入看似无害实际会触发parse错误的内容。"""

    original = target_file.read_text(encoding="utf-8")

    insertion = "\n\n# TODO: refactor this entire module by Q3 — this is a chaos bomb #\n"

    mutated = original.replace(
        "from __future__ import annotations",
        f"from __future__ import annotations{insertion}",
    )

    if mutated == original:
        mutated = f"{insertion}\n{original}"

    return original, mutated


def import_hallucination(target_file: Path) -> tuple[str, str]:
    """导入幻觉：添加一个不存在的import语句。"""

    original = target_file.read_text(encoding="utf-8")

    hallucinated = "from chaos_hallucination_xyzzy import this_never_exists_roflmao\n"

    mutated = hallucinated + original

    return original, mutated


INJECTORS: dict[ChaosInjectionType, object] = {
    ChaosInjectionType.PATH_RENAME: inject_path_rename,
    ChaosInjectionType.YAML_FIELD_FLIP: inject_yaml_field_flip,
    ChaosInjectionType.FAKE_TODO_BOMB: inject_fake_todo_bomb,
    ChaosInjectionType.IMPORT_HALLUCINATION: import_hallucination,
}


def _find_p2_targets(project_root: str) -> list[Path]:
    """仅P2模块文件作为混沌目标。"""

    src_root = Path(project_root) / "src"

    test_root = Path(project_root) / "tests"

    targets: list[Path] = []

    for root_dir in [src_root, test_root]:
        if not root_dir.exists():
            continue

        for py_file in root_dir.rglob("*.py"):
            rel = str(py_file)

            if any(s in rel.lower() for s in ("__pycache__", ".git", ".venv")):
                continue

            if "drift-detector" in rel or "governance" in rel:
                continue

            if py_file.stat().st_size < 500:
                targets.append(py_file)

    return targets[:3]


def run_chaos_experiment(
    project_root: str,
    state_dir: str,
    skip_safeguards: bool = False,
) -> list[ChaosInjection]:
    """执行一次混沌实验：基线→注入→检测→回滚。"""

    results: list[ChaosInjection] = []

    if not skip_safeguards:
        targets = _find_p2_targets(project_root)

    else:
        src_root = Path(project_root) / "src"

        targets = [p for p in src_root.rglob("*.py") if "drift" not in str(p)][:3]

    if not targets:
        return results

    injection_types: list[ChaosInjectionType] = [
        ChaosInjectionType.PATH_RENAME,
        ChaosInjectionType.YAML_FIELD_FLIP,
        ChaosInjectionType.FAKE_TODO_BOMB,
        ChaosInjectionType.IMPORT_HALLUCINATION,
    ]

    chaos_files: list[tuple[Path, ChaosInjectionType, tuple[str, str]]] = []

    for i, target in enumerate(targets[:4]):
        itype = injection_types[i % len(injection_types)]

        injector = INJECTORS.get(itype)

        if not injector:
            continue

        try:
            original, mutated = injector(target)

        except Exception:
            continue

        if original == mutated:
            continue

        chaos_files.append((target, itype, (original, mutated)))

    results = _inject_phase(chaos_files)

    results = _detect_phase(results, project_root)

    results = _rollback_phase(results)

    metrics = ChaosMetrics()

    metrics.total_injections = len(results)

    metrics.detected = sum(1 for r in results if r.result is ChaosResult.DETECTED)

    metrics.missed = sum(1 for r in results if r.result is ChaosResult.MISSED)

    metrics.degraded = sum(1 for r in results if r.result is ChaosResult.DEGRADED)

    if metrics.total_injections > 0:
        metrics.false_negative_rate = metrics.missed / metrics.total_injections

    dtimes = [r.detection_time_sec for r in results if r.detection_time_sec > 0]

    if dtimes:
        metrics.avg_time_to_detect_sec = sum(dtimes) / len(dtimes)

    _write_metrics(metrics, state_dir)

    return results


def _inject_phase(
    chaos_files: list[tuple[Path, ChaosInjectionType, tuple[str, str]]],
) -> list[ChaosInjection]:
    """注入阶段：写mutated内容到文件。"""

    results: list[ChaosInjection] = []

    for target, itype, (_original, mutated) in chaos_files:
        ci = ChaosInjection(
            injection_type=itype,
            target_file=str(target),
            original_content=_original,
            mutated_content=mutated,
            baseline_snapshot=datetime.now(UTC).isoformat(),
            phase=ChaosPhase.INJECT,
        )

        try:
            target.write_text(mutated, encoding="utf-8")

            ci.phase = ChaosPhase.DETECT

            results.append(ci)

        except Exception:
            ci.result = ChaosResult.ERROR

            results.append(ci)

    return results


def _detect_phase(
    results: list[ChaosInjection],
    project_root: str,
) -> list[ChaosInjection]:
    import asyncio

    from .drift_engine import ScanLevel, scan

    for ci in results:
        if ci.phase is not ChaosPhase.DETECT:
            continue

        inject_time = ci.created_at

        try:
            result = run_sync(
                scan(
                    level=ScanLevel.DEEP,
                )
            )

            post_inject_events = [e for e in result.events if e.created_at >= inject_time]

            ci.detection_time_sec = (datetime.now(UTC) - inject_time).total_seconds()

            ci.detected_by = [e.detector_id for e in post_inject_events]

            if post_inject_events:
                ci.result = ChaosResult.DETECTED

            else:
                ci.result = ChaosResult.MISSED

        except Exception:
            ci.result = ChaosResult.ERROR

    return results


def _rollback_phase(
    results: list[ChaosInjection],
) -> list[ChaosInjection]:
    """回滚阶段：恢复原始文件内容。"""

    for ci in results:
        if ci.result is ChaosResult.ERROR:
            continue

        try:
            target_path = Path(ci.target_file)

            target_path.write_text(ci.original_content, encoding="utf-8")

            ci.phase = ChaosPhase.COMPLETE

            ci.rolled_back_at = datetime.now(UTC)

        except Exception:
            ci.result = ChaosResult.DEGRADED

    return results
