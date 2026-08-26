# [BLUEPRINT] MOD-ML-020 | docs/03_modules/_domain_machine_learning_train/reproducibility_manager/blueprint.md
# [MODULE] zephyr.ml_train.reproducibility_manager
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（纯内存/DI；env_collector/tracking_sink/hasher/clock 全注入；hash 缺省 hashlib/json stdlib；语义旁挂 build_reproducibility_verifier）
# [CONSUMERS] 运行时装配批（环境采集器绑定 / experiment_tracking 回调绑定 / 重跑比对编排装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 环境快照仅经注入采集(python+packages 排序元组); 全局种子按运行登记且为非负整数; 结果 hash 写后不可改; 重跑比对差异清单确定性排序; experiment_tracking 仅经注入回调且异常不阻断; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/reproducibility_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ReproducibilityError(占位 ZA-MLT-UNREGISTERED-REPRODUCIBILITY)——采集器未注入/快照载荷非法/种子非法/重复登记/结果缺失/未知运行时抛
# [TESTS] tests/ml_train/test_reproducibility_manager.py
# [A_module] module_id=MOD-ML-020 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ReproducibilityManager — 可复现性管理器（MOD-ML-020）。

B13-04338（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-028，A3 D-RESEARCH-05）：
**环境快照**（python/pip lock/关键 lib 版本采集注入）+ **全局种子登记**
（按运行记录种子）+ **结果 hash 校验**（重跑比对）+ **复现报告生成**
（差异清单）+ **experiment_tracking 集成回调**。

分工（蓝图 §0）：MOD-INF-081 打包器=产物打包；本件=种子/校验/报告协议面。
canonical 承接 WFO-004/FBLVERIF-001 归并。
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
from dataclasses import dataclass, replace
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "DiffItem",
    "EnvironmentSnapshot",
    "ReproReport",
    "ReproducibilityError",
    "ReproducibilityManager",
    "RunRecord",
]

#: 差异清单中缺失键占位符
_MISSING: Final = "<MISSING>"


class ReproducibilityError(Exception):
    """可复现性管理输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-REPRODUCIBILITY。
    """


@dataclass(frozen=True)
class EnvironmentSnapshot:
    """环境快照（frozen；packages 为 (名称,版本) 排序元组）。"""

    snapshot_id: str
    python_version: str
    packages: tuple[tuple[str, str], ...]
    captured_at: datetime.datetime


@dataclass(frozen=True)
class RunRecord:
    """运行登记（frozen；result_hash 写后不可改）。"""

    run_id: str
    seed: int
    env_snapshot_id: str
    result_hash: str | None
    registered_at: datetime.datetime


@dataclass(frozen=True)
class DiffItem:
    """单字段差异（frozen）。"""

    field: str
    expected: object
    actual: object


@dataclass(frozen=True)
class ReproReport:
    """复现报告（frozen；差异清单确定性排序）。"""

    run_id: str
    rerun_id: str
    matched: bool
    seed_matched: bool
    diffs: tuple[DiffItem, ...]
    generated_at: datetime.datetime


def _default_hash(payload: Mapping) -> str:
    """缺省结果 hash：JSON sort_keys 序列化后 sha256（确定性）。"""
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _validate_seed(seed: int, *, what: str = "seed") -> None:
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ReproducibilityError(f"{what} 非法: {seed!r}（须非负整数）")


class ReproducibilityManager:
    """可复现性管理器（环境快照 + 种子登记 + hash 校验 + 复现报告）。"""

    def __init__(
        self,
        *,
        env_collector: Callable[[], Mapping] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        tracking_sink: Callable[[Mapping], None] | None = None,
        hasher: Callable[[Mapping], str] | None = None,
    ) -> None:
        self._env_collector = env_collector
        self._clock = clock or datetime.datetime.now
        self._tracking_sink = tracking_sink
        self._hasher = hasher or _default_hash
        self._envs: dict[str, EnvironmentSnapshot] = {}
        self._env_order: list[str] = []
        self._env_counter = 0
        self._runs: dict[str, RunRecord] = {}
        self._results: dict[str, dict] = {}
        self._reports: list[ReproReport] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _run_or_raise(self, run_id: str) -> RunRecord:
        rec = self._runs.get(run_id)
        if rec is None:
            raise ReproducibilityError(f"未知运行: {run_id!r}")
        return rec

    def _hash_or_raise(self, payload: Mapping) -> str:
        digest = self._hasher(payload)
        if not isinstance(digest, str) or not digest:
            raise ReproducibilityError("hasher 返回非法结果 hash")
        return digest

    # ── 环境快照（采集注入） ────────────────────────────────────────────────

    def capture_environment(self) -> EnvironmentSnapshot:
        """环境快照：python 版本 + packages 版本映射（采集器未注入 Fail-Closed）。"""
        if self._env_collector is None:
            raise ReproducibilityError("env_collector 未注入（环境采集须注入回调）")
        raw = self._env_collector()
        if not isinstance(raw, Mapping):
            raise ReproducibilityError("env_collector 返回非映射")
        python_version = raw.get("python")
        if not isinstance(python_version, str) or not python_version:
            raise ReproducibilityError("环境快照缺 python 版本")
        packages_raw = raw.get("packages", {})
        if not isinstance(packages_raw, Mapping):
            raise ReproducibilityError("环境快照 packages 非映射")
        packages: list[tuple[str, str]] = []
        for name, version in packages_raw.items():
            if not isinstance(name, str) or not name:
                raise ReproducibilityError("环境快照存在空包名")
            if not isinstance(version, str) or not version:
                raise ReproducibilityError(f"环境快照包 {name!r} 版本非法: {version!r}")
            packages.append((name, version))
        self._env_counter += 1
        snap = EnvironmentSnapshot(
            snapshot_id=f"env-{self._env_counter:04d}",
            python_version=python_version,
            packages=tuple(sorted(packages)),
            captured_at=self._clock(),
        )
        self._envs[snap.snapshot_id] = snap
        self._env_order.append(snap.snapshot_id)
        _log.info("环境快照: %s (%d 包)", snap.snapshot_id, len(packages))
        return snap

    # ── 运行登记（全局种子） ────────────────────────────────────────────────

    def register_run(
        self, run_id: str, seed: int, env_snapshot_id: str | None = None
    ) -> RunRecord:
        """登记运行：全局种子 + 环境快照绑定（缺省取最近快照）。"""
        if not run_id:
            raise ReproducibilityError("run_id 为空")
        if run_id in self._runs:
            raise ReproducibilityError(f"run_id 重复登记: {run_id!r}")
        _validate_seed(seed)
        if env_snapshot_id is None:
            if not self._env_order:
                raise ReproducibilityError("尚无环境快照（先 capture_environment）")
            env_snapshot_id = self._env_order[-1]
        if env_snapshot_id not in self._envs:
            raise ReproducibilityError(f"未知环境快照: {env_snapshot_id!r}")
        rec = RunRecord(
            run_id=run_id,
            seed=seed,
            env_snapshot_id=env_snapshot_id,
            result_hash=None,
            registered_at=self._clock(),
        )
        self._runs[run_id] = rec
        return rec

    def record_result(self, run_id: str, result: Mapping) -> str:
        """记录原运行结果并留 hash（写后不可改）。"""
        rec = self._run_or_raise(run_id)
        if rec.result_hash is not None:
            raise ReproducibilityError(f"运行 {run_id!r} 结果已记录（不可改）")
        if not isinstance(result, Mapping) or not result:
            raise ReproducibilityError("result 为空或非映射")
        digest = self._hash_or_raise(result)
        self._runs[run_id] = replace(rec, result_hash=digest)
        self._results[run_id] = dict(result)
        return digest

    # ── 重跑比对 + 复现报告 ────────────────────────────────────────────────

    def verify_rerun(
        self,
        run_id: str,
        rerun_id: str,
        rerun_result: Mapping,
        rerun_seed: int | None = None,
    ) -> ReproReport:
        """重跑比对：结果 hash + 字段级差异清单 + 种子一致性 → 复现报告。"""
        rec = self._run_or_raise(run_id)
        if not rerun_id:
            raise ReproducibilityError("rerun_id 为空")
        if rec.result_hash is None:
            raise ReproducibilityError(f"运行 {run_id!r} 未记录结果 hash（无法比对）")
        if not isinstance(rerun_result, Mapping) or not rerun_result:
            raise ReproducibilityError("rerun_result 为空或非映射")
        if rerun_seed is not None:
            _validate_seed(rerun_seed, what="rerun_seed")
        new_hash = self._hash_or_raise(rerun_result)
        expected = self._results[run_id]
        diffs: list[DiffItem] = []
        for key in sorted(set(expected) | set(rerun_result)):
            if key not in rerun_result:
                diffs.append(DiffItem(field=key, expected=expected[key], actual=_MISSING))
            elif key not in expected:
                diffs.append(DiffItem(field=key, expected=_MISSING, actual=rerun_result[key]))
            elif expected[key] != rerun_result[key]:
                diffs.append(DiffItem(field=key, expected=expected[key], actual=rerun_result[key]))
        seed_matched = rerun_seed is None or rerun_seed == rec.seed
        matched = not diffs and new_hash == rec.result_hash and seed_matched
        report = ReproReport(
            run_id=run_id,
            rerun_id=rerun_id,
            matched=matched,
            seed_matched=seed_matched,
            diffs=tuple(diffs),
            generated_at=self._clock(),
        )
        self._reports.append(report)
        if self._tracking_sink is not None:
            try:
                self._tracking_sink({
                    "event": "repro_verify",
                    "run_id": run_id,
                    "rerun_id": rerun_id,
                    "matched": matched,
                    "diff_count": len(diffs),
                })
            except Exception:  # noqa: BLE001 — tracking 回调异常不阻断
                _log.exception("tracking_sink 回调失败")
        _log.info("复现报告: %s vs %s matched=%s diffs=%d", run_id, rerun_id, matched, len(diffs))
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    def environment(self, snapshot_id: str) -> EnvironmentSnapshot:
        """环境快照查询（未知 Fail-Closed）。"""
        snap = self._envs.get(snapshot_id)
        if snap is None:
            raise ReproducibilityError(f"未知环境快照: {snapshot_id!r}")
        return snap

    def run_record(self, run_id: str) -> RunRecord:
        """运行登记查询（未知 Fail-Closed）。"""
        return self._run_or_raise(run_id)

    def list_runs(self) -> tuple[str, ...]:
        """运行清单（字典序确定性）。"""
        return tuple(sorted(self._runs))

    def reports(self) -> tuple[ReproReport, ...]:
        """复现报告序列（生成序）。"""
        return tuple(self._reports)
