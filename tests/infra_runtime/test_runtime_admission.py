# [BLUEPRINT] docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md | §2.2 L-3 / §4 P2-c
# [MODULE] tests.infra_runtime.test_runtime_admission
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] src/zephyr/infra_runtime/runtime_admission.py
# [A_test] module_id: MOD-INF-RT-ADM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P2-c 运行时准入三件合一单元测试。

验收（排班 v2 方案 §2.2 L-3 / §4 P2-c）：三座零引用孤岛（capacity_budget 并发维 /
resource_scheduler 内存维 / api_cost_governor 速率维）由注册表供配额合一；池词表真源=
注册表 lanes（禁硬编码）；R-D 裁定 planned/retired 不占预算不获准入；三件全过方放行；
时钟注入确定性。测试仅写 tmp_path，不触 data/ 生产路径。
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.runtime_admission",
    reason="runtime_admission not importable",
)

from zephyr.infra_runtime.runtime_admission import (  # noqa: E402
    DEFAULT_REGISTRY_RELPATH,
    AdmissionResult,
    RuntimeAdmissionCoordinator,
    RuntimeAdmissionError,
    build_runtime_quotas,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


class _FakeClock:
    """确定性单调秒时钟。"""

    def __init__(self, t0: float = 1000.0) -> None:
        self.now = t0

    def __call__(self) -> float:
        return self.now

    def advance(self, dt: float) -> None:
        self.now += dt


def _registry_dict(
    *,
    lanes: tuple[str, ...] = ("heavy", "default"),
    workers: dict[str, int] | None = None,
    ceiling: float = 10.0,
    entities: list[dict] | None = None,
) -> dict:
    workers = workers if workers is not None else {"heavy": 10, "default": 4}
    return {
        "mem_ceiling_gb": ceiling,
        "pool_vocabulary": {"lanes": list(lanes), "workers": workers},
        "entities": entities or [],
    }


def _write_registry(tmp_path: Path, data: dict) -> Path:
    import yaml

    p = tmp_path / "resource_profile_registry.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _coord(data: dict, clock: _FakeClock | None = None) -> RuntimeAdmissionCoordinator:
    quotas = build_runtime_quotas(
        data["entities"], data["pool_vocabulary"], data["mem_ceiling_gb"]
    )
    return RuntimeAdmissionCoordinator(quotas, clock=clock or _FakeClock())


# ──────────────────────────────────────────────────────────────────────────────
# build_runtime_quotas：注册表派生 + R-D
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildRuntimeQuotas:
    def test_lanes_and_workers_from_registry(self) -> None:
        data = _registry_dict()
        q = build_runtime_quotas(
            data["entities"], data["pool_vocabulary"], data["mem_ceiling_gb"]
        )
        assert q.lanes == ("heavy", "default")
        assert q.per_pool["heavy"].workers == 10
        assert q.total_workers == 14
        assert q.mem_ceiling_gb == 10.0

    def test_rd_planned_retired_excluded(self) -> None:
        entities = [
            {"task_id": "a", "pool": "heavy", "peak_mem_gb": 3.0, "est_duration_min": 60, "status": "active"},
            {"task_id": "b", "pool": "heavy", "peak_mem_gb": 5.0, "est_duration_min": 120, "status": "planned"},
            {"task_id": "c", "pool": "heavy", "peak_mem_gb": 9.0, "est_duration_min": 999, "status": "retired"},
            {"task_id": "d", "pool": "heavy", "peak_mem_gb": 2.0, "est_duration_min": 30, "status": "active"},
        ]
        q = build_runtime_quotas(entities, {"lanes": ["heavy"], "workers": {"heavy": 4}}, 10.0)
        heavy = q.per_pool["heavy"]
        assert heavy.active_entity_count == 2  # 仅 a,d
        assert heavy.active_peak_mem_gb == pytest.approx(5.0)  # 3+2，planned/retired 不计
        assert heavy.max_est_duration_min == 60  # 不含 planned 120/retired 999

    def test_ghost_pool_entity_not_invented(self) -> None:
        entities = [{"task_id": "x", "pool": "light_ghost", "peak_mem_gb": 1.0, "status": "active"}]
        q = build_runtime_quotas(entities, {"lanes": ["heavy"], "workers": {"heavy": 2}}, 10.0)
        assert q.per_pool["heavy"].active_entity_count == 0  # 幽灵池不并入真池


# ──────────────────────────────────────────────────────────────────────────────
# from_registry：只读真源装载
# ──────────────────────────────────────────────────────────────────────────────


class TestFromRegistry:
    def test_load_synthetic(self, tmp_path: Path) -> None:
        data = _registry_dict(entities=[
            {"task_id": "a", "pool": "heavy", "peak_mem_gb": 1.0, "est_duration_min": 10, "status": "active"},
        ])
        path = _write_registry(tmp_path, data)
        coord = RuntimeAdmissionCoordinator.from_registry(path)
        assert coord.pool_quotas()["heavy"].workers == 10

    def test_missing_ceiling_raises(self, tmp_path: Path) -> None:
        data = _registry_dict()
        del data["mem_ceiling_gb"]
        path = _write_registry(tmp_path, data)
        import yaml

        raw = yaml.safe_dump(data, allow_unicode=True)
        path.write_text(raw, encoding="utf-8")
        with pytest.raises(RuntimeAdmissionError):
            RuntimeAdmissionCoordinator.from_registry(path)

    def test_real_registry_smoke(self) -> None:
        """真注册表只读冒烟：lanes 非空、含 default/heavy/realtime 真池，无写副作用。"""
        real = _REPO_ROOT / DEFAULT_REGISTRY_RELPATH
        if not real.exists():  # pragma: no cover
            pytest.skip("real registry missing")
        coord = RuntimeAdmissionCoordinator.from_registry(real)
        lanes = set(coord.pool_quotas())
        assert {"default", "heavy", "realtime"} <= lanes
        # R-D：active 计数为正、planned 实体不使 active 为负/异常
        assert coord.pool_quotas()["default"].active_entity_count >= 1


# ──────────────────────────────────────────────────────────────────────────────
# 并发维（capacity_budget）
# ──────────────────────────────────────────────────────────────────────────────


class TestConcurrencyDimension:
    def test_admit_within_workers(self) -> None:
        data = _registry_dict(workers={"heavy": 2, "default": 2}, ceiling=100.0)
        coord = _coord(data)
        assert coord.request_admission("t1", pool="heavy", mem_gb=1.0).granted
        assert coord.request_admission("t2", pool="heavy", mem_gb=1.0).granted

    def test_over_workers_rejected(self) -> None:
        data = _registry_dict(workers={"heavy": 2, "default": 2}, ceiling=100.0)
        coord = _coord(data)
        coord.request_admission("t1", pool="heavy", mem_gb=1.0)
        coord.request_admission("t2", pool="heavy", mem_gb=1.0)
        d = coord.request_admission("t3", pool="heavy", mem_gb=1.0)
        assert d.granted is False
        assert any("并发超泳道配额" in r for r in d.reasons)
        assert d.concurrency_granted is False

    def test_release_frees_slot(self) -> None:
        clock = _FakeClock()
        data = _registry_dict(workers={"heavy": 1, "default": 1}, ceiling=100.0)
        coord = _coord(data, clock=clock)
        assert coord.request_admission("t1", pool="heavy", mem_gb=1.0).granted
        coord.release("t1")  # 归还并发槽（队列空→无自动出队）
        clock.advance(2.0)  # 令牌桶随注入时钟回补（速率维自愈）
        assert coord.active_count("heavy") == 0
        assert coord.request_admission("t2", pool="heavy", mem_gb=1.0).granted


# ──────────────────────────────────────────────────────────────────────────────
# 内存维（resource_scheduler）
# ──────────────────────────────────────────────────────────────────────────────


class TestMemoryDimension:
    def test_over_mem_ceiling_rejected(self) -> None:
        data = _registry_dict(workers={"heavy": 10, "default": 10}, ceiling=4.0)
        coord = _coord(data)
        assert coord.request_admission("m1", pool="heavy", mem_gb=3.0).granted
        d = coord.request_admission("m2", pool="heavy", mem_gb=3.0)
        assert d.granted is False
        assert any("内存超预算" in r for r in d.reasons)
        assert d.concurrency_granted is False  # 已回滚并发


# ──────────────────────────────────────────────────────────────────────────────
# 速率维（api_cost_governor，注册表驱动参数）
# ──────────────────────────────────────────────────────────────────────────────


class TestRateDimension:
    def test_token_bucket_exhaustion_and_refill(self) -> None:
        # workers=1 → base_qps=1，容量 1；但并发 WIP=1 也会卡住第三个，
        # 故用 release 腾并发槽、同刻不推进时钟 → 令牌耗尽 → 速率拒；推进 1s → 回补 → 放行。
        clock = _FakeClock()
        data = _registry_dict(workers={"heavy": 1, "default": 1}, ceiling=100.0)
        coord = _coord(data, clock=clock)
        assert coord.request_admission("r1", pool="heavy", mem_gb=1.0).granted
        coord.release("r1")  # 腾并发槽，但时钟不动 → 桶仍空
        d = coord.request_admission("r2", pool="heavy", mem_gb=1.0)
        assert d.granted is False
        assert any("速率令牌不足" in r for r in d.reasons)
        assert d.concurrency_granted is False  # 速率失败已回滚并发
        clock.advance(2.0)  # 回补 1×2=2 令牌，封顶 1
        assert coord.request_admission("r3", pool="heavy", mem_gb=1.0).granted


# ──────────────────────────────────────────────────────────────────────────────
# 状态门 / 输入校验 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestGuardsAndDeterminism:
    def test_planned_entity_not_admissible(self) -> None:
        data = _registry_dict()
        coord = _coord(data)
        d = coord.request_admission("p1", pool="heavy", mem_gb=1.0, status="planned")
        assert d.granted is False
        assert any("未排产" in r for r in d.reasons)

    def test_admit_entity_uses_status_field(self) -> None:
        data = _registry_dict()
        coord = _coord(data)
        r = coord.admit_entity({"task_id": "e1", "pool": "heavy", "peak_mem_gb": 1.0, "status": "retired"})
        assert isinstance(r, AdmissionResult)
        assert r.granted is False

    def test_unknown_pool_raises(self) -> None:
        data = _registry_dict()
        coord = _coord(data)
        with pytest.raises(RuntimeAdmissionError):
            coord.request_admission("t", pool="ghost", mem_gb=1.0)

    def test_duplicate_task_raises(self) -> None:
        data = _registry_dict()
        coord = _coord(data)
        coord.request_admission("dup", pool="heavy", mem_gb=1.0)
        with pytest.raises(RuntimeAdmissionError):
            coord.request_admission("dup", pool="heavy", mem_gb=1.0)

    def test_empty_task_raises(self) -> None:
        coord = _coord(_registry_dict())
        with pytest.raises(RuntimeAdmissionError):
            coord.request_admission("", pool="heavy", mem_gb=1.0)

    def test_determinism_same_inputs(self) -> None:
        def _run() -> tuple:
            coord = _coord(_registry_dict(workers={"heavy": 2, "default": 2}, ceiling=3.0), _FakeClock(50.0))
            a = coord.request_admission("x1", pool="heavy", mem_gb=1.0)
            b = coord.request_admission("x2", pool="heavy", mem_gb=1.0)
            c = coord.request_admission("x3", pool="heavy", mem_gb=1.0)
            return (a.granted, b.granted, c.granted, tuple(c.reasons), coord.snapshot())

        r1 = _run()
        r2 = _run()
        assert r1 == r2

    def test_snapshot_view(self) -> None:
        coord = _coord(_registry_dict(workers={"heavy": 2, "default": 2}, ceiling=100.0))
        coord.request_admission("s1", pool="heavy", mem_gb=2.0)
        snap = coord.snapshot()
        assert snap["active_tasks"] == 1
        assert snap["plane_usage_mem_used_bytes"] == 2 * (1024**3)
