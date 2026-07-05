# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.detector_dispatcher
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; tests/audit/test_detector_dispatcher.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测器调度不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_detector_dispatcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Detector Dispatcher — detector_dispatcher.py





module_id: MOD-INF-023


并行调度器：asyncio subprocess pool 执行检测器脚本，含结果缓存和并行度控制。


对标 blueprint.md §2.4（增量扫描与性能 SLO）。"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field


def _compute_file_hash(fp: str) -> str:
    with open(fp, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


from .drift_models import Detector, ScanLevel


@dataclass
class DetectorResult:
    detector_id: str

    success: bool

    events: list[dict[str, object]] = field(default_factory=list)

    error: str = ""

    cached: bool = False

    elapsed_ms: float = 0.0


@dataclass
class ResultCache:
    _entries: dict[str, DetectorResult] = field(default_factory=dict)

    def get(self, key: str) -> DetectorResult | None:
        return self._entries.get(key)

    def put(self, key: str, result: DetectorResult) -> None:
        self._entries[key] = result

    def clear(self) -> None:
        self._entries.clear()


class DetectorDispatcher:
    def __init__(self, registry_path: str, max_parallel: int = 8):
        self._registry_path = registry_path

        self._max_parallel = max_parallel

        self._cache = ResultCache()

        self._scripts_root = ""

    @property
    def scripts_root(self) -> str:
        if not self._scripts_root:
            self._scripts_root = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "scripts",
                "governance",
            )

        return self._scripts_root

    async def dispatch(
        self,
        detectors: list[Detector],
        changed_files: list[str] | None = None,
    ) -> list[DetectorResult]:
        if changed_files is None:
            changed_files = []

        sem = asyncio.Semaphore(self._max_parallel)

        tasks = [self._run_detector(d, changed_files, sem) for d in detectors]

        return list(await asyncio.gather(*tasks))

    def cache_key(self, detector_id: str, file_path: str) -> str:
        content = f"{detector_id}:{file_path}"

        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def build_cache_key(self, detector: Detector, changed_files: list[str]) -> str | None:
        if not detector.script:
            return None

        script_path = os.path.join(self.scripts_root, detector.script)

        if not os.path.exists(script_path):
            return None

        combined = detector.id

        existing = [fp for fp in changed_files if os.path.exists(fp)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_compute_file_hash, fp): fp for fp in existing}
            for future in as_completed(futures):
                try:
                    combined += future.result()
                except OSError:
                    combined += futures[future]

        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    async def _run_detector(
        self,
        detector: Detector,
        changed_files: list[str],
        sem: asyncio.Semaphore,
    ) -> DetectorResult:
        start = time.perf_counter()

        cache_key = self.build_cache_key(detector, changed_files)

        if cache_key:
            cached = self._cache.get(cache_key)

            if cached is not None:
                return DetectorResult(
                    detector_id=detector.id,
                    success=cached.success,
                    events=cached.events,
                    error=cached.error,
                    cached=True,
                    elapsed_ms=cached.elapsed_ms,
                )

        async with sem:
            script = detector.script

            if not script:
                elapsed = (time.perf_counter() - start) * 1000

                return DetectorResult(
                    detector_id=detector.id,
                    success=True,
                    events=[],
                    elapsed_ms=elapsed,
                )

            script_path = os.path.join(self.scripts_root, script)

            if not os.path.exists(script_path):
                elapsed = (time.perf_counter() - start) * 1000

                return DetectorResult(
                    detector_id=detector.id,
                    success=False,
                    error=f"MISSING_SCRIPT: {script_path}",
                    elapsed_ms=elapsed,
                )

            proc = None
            try:
                proc = await asyncio.create_subprocess_exec(
                    "python",
                    script_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=30,
                )

                elapsed = (time.perf_counter() - start) * 1000

                if proc.returncode != 0:
                    result = DetectorResult(
                        detector_id=detector.id,
                        success=False,
                        error=stderr.decode("utf-8", errors="replace")[:500],
                        elapsed_ms=elapsed,
                    )

                    if cache_key:
                        self._cache.put(cache_key, result)

                    return result

                try:
                    output = json.loads(stdout.decode("utf-8"))

                except (json.JSONDecodeError, UnicodeDecodeError):
                    output = []

                result = DetectorResult(
                    detector_id=detector.id,
                    success=True,
                    events=output if isinstance(output, list) else [output],
                    elapsed_ms=elapsed,
                )

                if cache_key:
                    self._cache.put(cache_key, result)

                return result

            except TimeoutError:
                elapsed = (time.perf_counter() - start) * 1000

                return DetectorResult(
                    detector_id=detector.id,
                    success=False,
                    error="TIMEOUT: 30s exceeded",
                    elapsed_ms=elapsed,
                )

            except Exception as exc:
                elapsed = (time.perf_counter() - start) * 1000

                return DetectorResult(
                    detector_id=detector.id,
                    success=False,
                    error=str(exc),
                    elapsed_ms=elapsed,
                )
            finally:
                # 5.112.1 修复：CancelledError/TimeoutError路径确保子进程被kill，防止孤儿进程
                try:
                    if proc is not None and proc.returncode is None:
                        proc.kill()
                        await proc.wait()
                except Exception:
                    pass


def get_max_parallel_for_level(level: ScanLevel) -> int:
    if level is ScanLevel.LIGHT or level is ScanLevel.STANDARD:
        return 4

    else:
        return 8
