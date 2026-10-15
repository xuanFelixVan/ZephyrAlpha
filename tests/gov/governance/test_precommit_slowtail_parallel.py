# [A_test] module_id: MOD-INF-precommit-slowtail-parallel-test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.test_precommit_slowtail_parallel
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""G3 慢尾组级并行单元测试（st-maint9-20261015，Owner 2026-10-15 批）。

覆盖：
  - 分组性质：全覆盖不重不漏、两台 pytest 系 hook 互斥不同组、确定性（同输入同分组）
  - 门控：pytest 环境自动串行、env 0/1=串行、缺省=2 组、非法值回缺省
  - 执行：_precommit_execute_auto 组数<2 走串行原通道；并行时按组 spawn（位置参数
    选 hook）、合并输出 rc=max、组 infra 不可用回退串行；变异重跑同口径
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    _PRECOMMIT_SLOW_TAIL_HOOKS,
    _PRECOMMIT_SLOWTAIL_PYTEST_HOOKS,
    GitCommitGateway,
    _precommit_slowtail_parallel_groups,
)


@pytest.fixture(autouse=True)
def _outside_pytest_env(monkeypatch):
    """分组函数的 pytest 探测被打桩为 False——单测覆盖并行分支（真 pytest 环境默认串行）。"""
    monkeypatch.setattr(
        "zephyr.gov_enforcement.rule_bridge.git_commit_gateway._precommit_under_pytest",
        lambda: False,
    )
    monkeypatch.delenv("ZEPHYR_PRECOMMIT_SLOWTAIL_PARALLEL", raising=False)


class TestSlowtailPartition:
    def test_default_two_groups_full_cover(self):
        groups = _precommit_slowtail_parallel_groups()
        assert groups is not None and len(groups) == 2
        flat = [h for g in groups for h in g]
        assert sorted(flat) == sorted(_PRECOMMIT_SLOW_TAIL_HOOKS)
        assert len(flat) == len(set(flat))

    def test_pytest_hooks_never_cogrouped(self):
        for n in (2, 3, 4):
            import os

            os.environ["ZEPHYR_PRECOMMIT_SLOWTAIL_PARALLEL"] = str(n)
            try:
                groups = _precommit_slowtail_parallel_groups()
                assert groups is not None
                for a in _PRECOMMIT_SLOWTAIL_PYTEST_HOOKS:
                    for b in _PRECOMMIT_SLOWTAIL_PYTEST_HOOKS:
                        if a == b:
                            continue
                        ga = next(i for i, g in enumerate(groups) if a in g)
                        gb = next(i for i, g in enumerate(groups) if b in g)
                        assert ga != gb, f"n={n}: {a} 与 {b} 同组"
            finally:
                del os.environ["ZEPHYR_PRECOMMIT_SLOWTAIL_PARALLEL"]

    def test_deterministic(self):
        assert _precommit_slowtail_parallel_groups() == _precommit_slowtail_parallel_groups()

    def test_serial_gates(self, monkeypatch):
        for v in ("0", "1", "off"):
            monkeypatch.setenv("ZEPHYR_PRECOMMIT_SLOWTAIL_PARALLEL", v)
            assert _precommit_slowtail_parallel_groups() is None, v
        monkeypatch.setenv("ZEPHYR_PRECOMMIT_SLOWTAIL_PARALLEL", "garbage")
        assert _precommit_slowtail_parallel_groups() is not None  # 非法值回缺省 2
        monkeypatch.setattr(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway._precommit_under_pytest",
            lambda: True,
        )
        assert _precommit_slowtail_parallel_groups() is None  # pytest 环境自动串行


class _FakeProc:
    def __init__(self, rc: int, out: str = ""):
        self.returncode = rc
        self.stdout = out
        self.stderr = ""


class TestExecuteAuto:
    def _gw(self):
        gw = GitCommitGateway.__new__(GitCommitGateway)
        gw.project_root = "/tmp/nonexistent-repo"
        return gw

    def test_below_two_groups_uses_serial(self):
        gw = self._gw()
        with patch.object(GitCommitGateway, "_precommit_execute", return_value=("serial", 0, False, "")) as m:
            out = gw._precommit_execute_auto({}, [[]], None)
            assert out == ("serial", 0, False, "")
            m.assert_called_once()
        with patch.object(GitCommitGateway, "_precommit_execute", return_value=("serial", 0, False, "")) as m:
            gw._precommit_execute_auto({}, [[]], [("gate-vocab",)])
            m.assert_called_once()

    def test_parallel_spawns_groups_and_merges(self, monkeypatch):
        gw = self._gw()
        groups = [("gate-a", "gate-test"), ("gate-errcode-consistency", "gate-b")]
        calls: list[list[str]] = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            # 第 1 组（含 gate-test）返回失败，第 2 组绿——rc=max 语义
            rc = 1 if "gate-a" in cmd else 0
            return SimpleNamespace(returncode=rc, stdout=f"out-{cmd[4]}", stderr="")

        monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", fake_run)
        output, rc, mutation, infra = gw._precommit_execute_auto({}, [[]], groups)
        assert rc == 1
        assert infra == ""
        assert len(calls) == 2
        for cmd in calls:
            assert cmd[2:4] == ["pre_commit", "run"]  # 形态：-m pre_commit run <ids...> --files
            assert "--files" in cmd
        assert "out-gate-a" in output and "out-gate-errcode-consistency" in output
        # 捕证归因：失败组（rc=1）的 meta 被登记
        assert isinstance(gw._pc_proc_meta, dict)

    def test_file_not_found_falls_back_to_serial(self, monkeypatch):
        gw = self._gw()
        groups = [("gate-a",), ("gate-b",)]

        def fake_run(cmd, **kwargs):
            raise FileNotFoundError("pre_commit missing")

        monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", fake_run)
        with patch.object(GitCommitGateway, "_precommit_execute", return_value=("serial-out", 0, False, "")) as m:
            out = gw._precommit_execute_auto({}, [[]], groups)
            assert out == ("serial-out", 0, False, "")
            m.assert_called_once()

    def test_mutation_triggers_rerun(self, monkeypatch):
        gw = self._gw()
        groups = [("gate-a",), ("gate-b",)]
        state = {"n": 0}

        def fake_run(cmd, **kwargs):
            state["n"] += 1
            out = "files were modified by this hook" if state["n"] <= 2 else "clean"
            return SimpleNamespace(returncode=0, stdout=out, stderr="")

        monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", fake_run)
        _, _, mutation, _ = gw._precommit_execute_auto({}, [[]], groups)
        assert mutation is False  # 第二次消解后干净
        assert state["n"] == 4  # 2 组 × 2 次尝试
