"""F4 GATE-ARCH-DIAGRAM 波次并发调度核验（mocked subprocess，零真实生成器运行）。

证明调度结构正确性（byte-identical 的实证在 worktree 实验，见
docs/_working/flash_speedup/F4_generator_concurrency/DESIGN.md）：
  ① 15 个生成器各调用一次，无遗漏无重复；
  ② DAG 依赖屏障：下游生成器在上游全部结束后才启动
     （navigation_index←5图 / align_panoramas←capacity_report /
       data_acquisition_flow←dataflow_diagram 的 HTML 清目录 / panorama_registry←全部）；
  ③ 波内真并发（同时活跃子进程数 >= 2）；
  ④ 单生成器 rc!=0 记入 failed_gens，不阻断其余（部分失败→warn 明细可观测）；
  ⑤ 单生成器超时降级 rc=-1，不抛出、不中断整轮 reconcile。
"""
import subprocess
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import zephyr.governance.audit.reconciliation_registry as rr

ALL_GENS = [
    "generate_decision_diagram.py", "generate_dataflow_diagram.py", "generate_integration_topology.py",
    "generate_design_vs_production.py", "generate_cross_domain_matrix.py", "generate_constraint_violations.py",
    "generate_capacity_report.py", "generate_capability_heatmap.py", "generate_navigation_index.py",
    "generate_panorama_registry.py", "align_panoramas.py", "generate_asset_catalog.py",
    "generate_policies.py", "generate_data_inventory.py", "generate_data_acquisition_flow.py",
]

# 静态核验得到的真实 DAG 依赖（下游 -> 上游集合）。测的是契约（依赖），非实现细节（波次元组）。
DEPS = {
    "generate_navigation_index.py": {
        "generate_integration_topology.py", "generate_design_vs_production.py",
        "generate_cross_domain_matrix.py", "generate_constraint_violations.py",
        "generate_capacity_report.py",
    },
    "align_panoramas.py": {"generate_capacity_report.py"},
    "generate_data_acquisition_flow.py": {"generate_dataflow_diagram.py"},
    "generate_panorama_registry.py": set(ALL_GENS) - {"generate_panorama_registry.py"},
}


class _Recorder:
    """替身 _run_subprocess：记录每个生成器的 [start,end] 区间 + 并发峰值，可注入失败/超时。"""

    def __init__(self, fail=(), timeout=(), work=0.08):
        self.fail = set(fail)
        self.timeout = set(timeout)
        self.work = work
        self.calls = {}  # gen -> (start, end, rc)
        self._lock = threading.Lock()
        self._active = 0
        self._peak = 0

    def __call__(self, cmd, **kwargs):
        gen = str(cmd[1]).replace("\\", "/").split("/")[-1]
        with self._lock:
            self._active += 1
            self._peak = max(self._peak, self._active)
        start = time.time()
        rc = -1  # 默认（超时路径 raise 前 rc 未赋值，finally 仍需有效值）
        try:
            time.sleep(self.work)
            if gen in self.timeout:
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 1))
            rc = 1 if gen in self.fail else 0
            return subprocess.CompletedProcess(cmd, rc, stdout="", stderr=("boom" if rc else ""))
        finally:
            end = time.time()
            with self._lock:
                self._active -= 1
                self.calls[gen] = (start, end, rc)

    @property
    def peak_concurrency(self):
        return self._peak


def _run_reconcile(rec, monkeypatch):
    monkeypatch.setattr(rr, "_run_subprocess", rec)
    gw = MagicMock()
    gw.project_root = Path("/fake/root")
    # run_git 恒返回 returncode=0 + 空 stdout：pre_diff 无漂移→进生成器；post diff 无漂移→clean/warn。
    gw.run_git.return_value = subprocess.CompletedProcess(["git"], 0, stdout="", stderr="")
    spec = rr.make_arch_diagram_reconciler(gw)
    return spec.reconcile([], "st-test-f4")


def test_all_15_generators_run_exactly_once(monkeypatch):
    rec = _Recorder()
    _run_reconcile(rec, monkeypatch)
    assert set(rec.calls) == set(ALL_GENS), "生成器集合不符（漏排波次会被构造期 partition guard 拦，此处兜底）"
    assert len(rec.calls) == 15


def test_dag_dependency_barriers_respected(monkeypatch):
    """下游生成器的启动时刻 >= 其全部上游的结束时刻（波间串行屏障的语义等价断言）。"""
    rec = _Recorder(work=0.05)
    _run_reconcile(rec, monkeypatch)
    for downstream, ups in DEPS.items():
        d_start = rec.calls[downstream][0]
        for up in ups:
            up_end = rec.calls[up][1]
            assert d_start >= up_end, (
                f"依赖违例：{downstream} 于 {d_start:.4f} 启动，但上游 {up} 到 {up_end:.4f} 才结束"
            )


def test_intra_wave_concurrency_occurs(monkeypatch):
    """波内真并发：同时活跃子进程峰值 >= 2（默认 cap=4，wave0 有 11 个独立生成器）。"""
    rec = _Recorder(work=0.12)
    _run_reconcile(rec, monkeypatch)
    assert rec.peak_concurrency >= 2, f"未观测到并发（峰值={rec.peak_concurrency}），波内应并行"


def test_clean_result_when_no_failure(monkeypatch):
    rec = _Recorder()
    result = _run_reconcile(rec, monkeypatch)
    assert result.action == "clean"


def test_single_generator_failure_does_not_block_others(monkeypatch):
    """④ 一个生成器 rc!=0：其余 14 个仍运行，结果 warn 且明细含失败计数。"""
    rec = _Recorder(fail={"generate_capacity_report.py"})
    result = _run_reconcile(rec, monkeypatch)
    assert len(rec.calls) == 15, "失败生成器不应中断其余生成器"
    assert result.action == "warn"
    assert "1 generator(s) failed" in result.detail
    assert "generate_capacity_report.py" in result.detail


def test_generator_timeout_degrades_not_raises(monkeypatch):
    """⑤ 超时降级为 rc=-1 记入 failed_gens，_reconcile 不抛异常。"""
    rec = _Recorder(timeout={"generate_data_inventory.py"})
    result = _run_reconcile(rec, monkeypatch)  # 不应抛出
    assert len(rec.calls) == 15
    assert result.action == "warn"
    assert "1 generator(s) failed" in result.detail
    assert "generate_data_inventory.py" in result.detail


def test_all_generators_fail_returns_warn(monkeypatch):
    """全失败 -> warn 直接返回（保留原 all-failed 短路语义）。"""
    rec = _Recorder(fail=set(ALL_GENS))
    result = _run_reconcile(rec, monkeypatch)
    assert result.action == "warn"
    assert "all 15 generators failed" in result.detail


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
