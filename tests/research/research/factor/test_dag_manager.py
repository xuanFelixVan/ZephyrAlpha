# [A_test] module_id: MOD-GOV_dag_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_dag_manager
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_dag_manager.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR core dag_manager 测试——executor.py。

覆盖：
- DagExecutorConfig 默认值
- 简单 2 层 DAG 执行
- 上游失败下游跳过
- 未注册因子处理
- backpressure 集成
- 超时处理
- report 字段完整性
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
import pytest

executor_mod = pytest.importorskip("zephyr.factor.core.dag_manager.executor")
dag_mod = pytest.importorskip("zephyr.factor.core.factor_dag.dag")
factor_base = pytest.importorskip("zephyr.factor.factor_base")
bp_mod = pytest.importorskip("zephyr.factor.core.backpressure.limiter")

DagExecutor = executor_mod.DagExecutor
DagExecutorConfig = executor_mod.DagExecutorConfig

FactorDAG = dag_mod.FactorDAG
FactorNode = dag_mod.FactorNode
build_dag_from_registry = dag_mod.build_dag_from_registry

FactorBase = factor_base.FactorBase
FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry

BackpressureLimiter = bp_mod.BackpressureLimiter
BackpressureConfig = bp_mod.BackpressureConfig


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _register_factor(fid: str, deps: list[str] | None = None, compute_fn: Any = None) -> None:
    """动态注册因子到 FactorRegistry。"""

    class _Factor(FactorBase):
        meta = FactorMeta(factor_id=fid, name=fid, domain="test", dependencies=deps or [])

        def compute(self, data, **kwargs):
            if compute_fn is not None:
                return compute_fn(data, **kwargs)
            return data["close"]

    FactorRegistry.register(_Factor)


def _make_data(n: int = 5) -> pd.DataFrame:
    """构造测试行情数据。"""
    return pd.DataFrame(
        {
            "close": [100.0 + i for i in range(n)],
            "open": [99.0 + i for i in range(n)],
            "high": [101.0 + i for i in range(n)],
            "low": [98.0 + i for i in range(n)],
            "volume": [1000 + i for i in range(n)],
        },
        index=pd.date_range("2026-01-01", periods=n, freq="D"),
    )


class TestDagExecutorConfig:
    def test_defaults(self) -> None:
        cfg = DagExecutorConfig()
        assert cfg.max_workers == 4
        assert cfg.factor_timeout_s == 60.0


class TestSimpleDagExecution:
    def test_single_factor(self) -> None:
        _register_factor("a")
        dag = build_dag_from_registry(["a"], dag_id="t")
        executor = DagExecutor()
        report = executor.execute(dag, _make_data())
        assert report.dag_id == "t"
        assert report.layer_count == 1
        assert "a" in report.results
        assert report.results["a"].success
        assert report.results["a"].series is not None
        assert report.failed_factors == []

    def test_two_layer_dag(self) -> None:
        """a <- b（b 依赖 a）→ 两层。"""
        _register_factor("a")
        _register_factor("b", deps=["a"])
        dag = build_dag_from_registry(["a", "b"], dag_id="t")
        executor = DagExecutor()
        report = executor.execute(dag, _make_data())
        assert report.layer_count == 2
        assert report.results["a"].success
        assert report.results["b"].success
        assert report.failed_factors == []

    def test_parallel_layer(self) -> None:
        """a, b 无依赖；c 依赖两者 → [a,b], [c]。"""
        _register_factor("a")
        _register_factor("b")
        _register_factor("c", deps=["a", "b"])
        dag = build_dag_from_registry(["a", "b", "c"], dag_id="t")
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        report = executor.execute(dag, _make_data())
        assert report.layer_count == 2
        for fid in ["a", "b", "c"]:
            assert report.results[fid].success, f"{fid} 应成功"


class TestUpstreamFailure:
    def test_downstream_skipped_on_upstream_failure(self) -> None:
        """a 失败 → b（依赖 a）标记 upstream failed。"""

        def failing_compute(data, **kwargs):
            raise RuntimeError("故意失败")

        _register_factor("a", compute_fn=failing_compute)
        _register_factor("b", deps=["a"])

        dag = build_dag_from_registry(["a", "b"], dag_id="t")
        executor = DagExecutor()
        report = executor.execute(dag, _make_data())

        assert not report.results["a"].success
        assert "compute error" in report.results["a"].error
        assert not report.results["b"].success
        assert "upstream failed" in report.results["b"].error
        assert "a" in report.results["b"].error
        assert sorted(report.failed_factors) == ["a", "b"]

    def test_sibling_not_blocked(self) -> None:
        """a 失败不影响同层 b（无依赖关系）。"""

        def failing_compute(data, **kwargs):
            raise RuntimeError("故意失败")

        _register_factor("a", compute_fn=failing_compute)
        _register_factor("b")  # 同层，不依赖 a

        dag = build_dag_from_registry(["a", "b"], dag_id="t")
        executor = DagExecutor()
        report = executor.execute(dag, _make_data())

        assert not report.results["a"].success
        assert report.results["b"].success  # 同层不受影响
        assert report.failed_factors == ["a"]


class TestUnregisteredFactor:
    def test_unregistered_factor_marked_failed(self) -> None:
        """factor_id 不在 FactorRegistry → 标记 not registered。"""
        # 手动构造 DAG（不通过 build_dag_from_registry，绕过注册检查）
        dag = FactorDAG(dag_id="t")
        dag.add_node(FactorNode(factor_id="nonexistent"))
        executor = DagExecutor()
        report = executor.execute(dag, _make_data())
        assert not report.results["nonexistent"].success
        assert "not registered" in report.results["nonexistent"].error


class TestBackpressureIntegration:
    def test_backpressure_rejection_marks_failed(self) -> None:
        """backpressure PAUSED 时 acquire 失败 → 因子标记 backpressure rejected。"""
        _register_factor("a")
        dag = build_dag_from_registry(["a"], dag_id="t")
        bp = BackpressureLimiter(BackpressureConfig(max_inflight=1))
        bp.pause()  # 强制拒绝
        executor = DagExecutor(backpressure=bp)
        report = executor.execute(dag, _make_data())
        assert not report.results["a"].success
        assert "backpressure rejected" in report.results["a"].error

    def test_backpressure_allows_normal_execution(self) -> None:
        """backpressure NORMAL 时正常执行。"""
        _register_factor("a")
        dag = build_dag_from_registry(["a"], dag_id="t")
        bp = BackpressureLimiter(BackpressureConfig(max_inflight=2))
        executor = DagExecutor(backpressure=bp)
        report = executor.execute(dag, _make_data())
        assert report.results["a"].success


class TestTimeout:
    def test_timeout_marks_failed(self) -> None:
        """因子计算超时 → 标记 timeout。"""

        def slow_compute(data, **kwargs):
            time.sleep(2.0)
            return data["close"]

        _register_factor("slow", compute_fn=slow_compute)
        dag = build_dag_from_registry(["slow"], dag_id="t")
        executor = DagExecutor(DagExecutorConfig(factor_timeout_s=0.2))
        report = executor.execute(dag, _make_data())
        assert not report.results["slow"].success
        assert "timeout" in report.results["slow"].error.lower()


class TestReportIntegrity:
    def test_report_has_all_fields(self) -> None:
        _register_factor("a")
        dag = build_dag_from_registry(["a"], dag_id="my_dag")
        executor = DagExecutor()
        report = executor.execute(dag, _make_data())
        assert report.dag_id == "my_dag"
        assert report.layer_count == 1
        assert isinstance(report.results, dict)
        assert report.duration_s >= 0.0
        assert isinstance(report.failed_factors, list)

    def test_extra_kwargs_passed(self) -> None:
        """extra_kwargs 应传给 compute。"""
        captured: dict[str, Any] = {}

        def capturing_compute(data, **kwargs):
            captured.update(kwargs)
            return data["close"]

        _register_factor("a", compute_fn=capturing_compute)
        dag = build_dag_from_registry(["a"], dag_id="t")
        executor = DagExecutor()
        executor.execute(dag, _make_data(), extra_kwargs={"a": {"window": 5}})
        assert captured.get("window") == 5
