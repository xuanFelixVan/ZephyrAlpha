# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_dispatcher
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] tests/audit/test_detector_dispatcher.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测器调度不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
Detector Dispatcher — detector_dispatcher.py


并行调度器：asyncio subprocess pool 执行检测器脚本，含结果缓存和并行度控制。


对标 blueprint.md §2.4（增量扫描与性能 SLO）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: level 参数
#   fields: 参数 level，类型注解 ScanLevel
#   code: detector_dispatcher.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ResultCache
#   name_en: ResultCache
#   intro: class ResultCache 源码 L111-L121
#   desc: 公共方法（定义序）: get, put, clear；源码 L111-L121
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② DetectorDispatcher
#   name_en: DetectorDispatcher
#   intro: class DetectorDispatcher 源码 L124-L328
#   desc: 公共方法（定义序）: max_parallel, registry_path, scripts_root, dispatch, cache_key, build_cache_key；源码 L124-L328
#   inputs: registry_path max_parallel
#   outputs: 返回值
# - id: A3
#   name_zh: ③ get_max_parallel_for_level
#   name_en: get_max_parallel_for_level
#   intro: get_max_parallel_for_level(level) 源码 L331-L336
#   desc: 源码 L331-L336
#   inputs: level
#   outputs: int
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/audit/test_detector_dispatcher.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_parallel(self):
        """只读：max_parallel（Stage 4 公共化）。"""
        return self._max_parallel

    @max_parallel.setter
    def max_parallel(self, value):
        """写入：max_parallel（Stage 4 公共化）。"""
        self._max_parallel = value

    @property
    def registry_path(self):
        """只读：registry_path（Stage 4 公共化）。"""
        return self._registry_path

    @registry_path.setter
    def registry_path(self, value):
        """写入：registry_path（Stage 4 公共化）。"""
        self._registry_path = value

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

            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.debug("suppressed error in detector_dispatcher", exc_info=True)


def get_max_parallel_for_level(level: ScanLevel) -> int:
    if level is ScanLevel.LIGHT or level is ScanLevel.STANDARD:
        return 4

    else:
        return 8
