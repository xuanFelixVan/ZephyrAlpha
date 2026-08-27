# [MODULE] tests.zephyr.trading.test_process_reaper
# [DOMAIN] D_INFRA_RUNTIME
# [TTL] permanent
"""process_reaper 判定矩阵单测（classify_process 纯函数，无 psutil 依赖）。

覆盖裁定矩阵全部分支（2026-08-28 裁定）：
白名单/Trae 后代永不杀、DANGEROUS 即杀、.runtime 孤儿即杀、孤儿分级、
非孤儿长命空转分级、自保。fail-safe 方向断言：边界条件一律偏向不杀。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.trading.process_reaper import classify_process  # noqa: E402

_BASE = dict(
    pid=1234,
    cmdline=r"python D:\ZephyrAlpha\some_script.py",
    age_s=100.0,
    mem_mb=100.0,
    cpu_pct=5.0,
    children=0,
    orphan=False,
    is_self_ancestor=False,
    is_trae_descendant=False,
    whitelist_hit=None,
)


def _classify(**overrides):
    kw = {**_BASE, **overrides}
    return classify_process(**kw)


class TestNeverKillGuards:
    """fail-safe 核心：三类保护命中时永不杀。"""

    def test_self_ancestor_never_killed(self):
        v = _classify(is_self_ancestor=True, mem_mb=99999.0, orphan=True, age_s=999999.0)
        assert v.action == "skip" and v.reason == "self_or_ancestor"

    def test_whitelist_never_killed(self):
        v = _classify(
            whitelist_hit="whitelist:zephyr\\.data\\.scheduler",
            cmdline=r"python -m zephyr.data.scheduler",
            age_s=999999.0,
            orphan=True,
            mem_mb=0.0,
            cpu_pct=0.0,
        )
        assert v.action == "skip" and v.reason.startswith("whitelist:")

    def test_trae_descendant_never_killed(self):
        v = _classify(is_trae_descendant=True, age_s=999999.0, cpu_pct=0.0)
        assert v.action == "skip" and v.reason == "trae_descendant"


class TestDangerous:
    def test_huge_memory_killed(self):
        v = _classify(mem_mb=11.0 * 1024, age_s=60.0)  # 即使年轻也杀
        assert v.action == "kill" and "dangerous" in v.reason

    def test_too_many_children_killed(self):
        v = _classify(children=51)
        assert v.action == "kill" and "dangerous" in v.reason

    def test_dangerous_beats_trae_protection(self):
        # Trae 后代保护优先于 DANGEROUS（IDE 子进程资源失控由 IDE 负责，fail-safe 不杀）
        v = _classify(is_trae_descendant=True, mem_mb=11.0 * 1024)
        assert v.action == "skip"


class TestRuntimeDirOrphan:
    """sweep_runner 族精准命中：.runtime/ 路径 + 孤儿 = 立即杀（无年龄门槛）。"""

    def test_runtime_dir_orphan_killed_immediately(self):
        v = _classify(
            cmdline=r"python .runtime\test_sweep\sweep_runner.py .runtime\test_sweep\manifest.txt",
            orphan=True,
            age_s=60.0,  # 仅 1 分钟也杀
        )
        assert v.action == "kill" and "runtime_dir_orphan" in v.reason

    def test_runtime_dir_non_orphan_not_killed(self):
        # 父活着的 .runtime 脚本（正在执行的合法短任务）不走此条，按正常规则判
        v = _classify(cmdline=r"python .runtime\test_sweep\sweep_runner.py", orphan=False, age_s=60.0)
        assert v.action == "skip"


class TestOrphanGrading:
    def test_orphan_aged_killed(self):
        v = _classify(orphan=True, age_s=3 * 3600.0)
        assert v.action == "kill" and "orphan_aged" in v.reason

    def test_orphan_watch_window_reported(self):
        v = _classify(orphan=True, age_s=3600.0)  # 1h：30min~2h 观察窗
        assert v.action == "report" and "orphan_watch" in v.reason

    def test_orphan_young_skipped(self):
        v = _classify(orphan=True, age_s=600.0)  # 10min：太年轻，给创建者留窗口
        assert v.action == "skip" and "orphan_young" in v.reason

    def test_orphan_boundary_2h_killed(self):
        v = _classify(orphan=True, age_s=2 * 3600.0 + 1)
        assert v.action == "kill"


class TestIdleGrading:
    """非孤儿长命空转（zombie_scanner 阈值修正版：必须年龄+CPU 双信号交叉）。"""

    def test_idle_aged_killed(self):
        v = _classify(age_s=7 * 3600.0, cpu_pct=0.1)
        assert v.action == "kill" and "idle_aged" in v.reason

    def test_aged_but_busy_not_killed(self):
        # 超龄但在真实干活（CPU 高）——scheduler 类业务繁忙场景，fail-safe 不杀
        v = _classify(age_s=7 * 3600.0, cpu_pct=50.0)
        assert v.action == "skip"

    def test_idle_watch_reported(self):
        v = _classify(age_s=2 * 3600.0, cpu_pct=0.05)
        assert v.action == "report" and "idle_watch" in v.reason

    def test_normal_skipped(self):
        v = _classify()
        assert v.action == "skip" and v.reason == "normal"


class TestRealWorldFixtures:
    """2026-08-28 事故实录回归：确保历史肇事者必被杀、被保留者必不杀。"""

    def test_sweep_runner_killed(self):
        v = _classify(
            cmdline=r'"C:\...\python.exe" .runtime\test_sweep\sweep_runner.py .runtime\test_sweep\manifest_b2_A.txt',
            orphan=True,
            age_s=18 * 60.0,  # 事故时仅 18 分钟龄
        )
        assert v.action == "kill"

    def test_orphan_pytest_aged_killed(self):
        v = _classify(
            cmdline=r'"C:\...\python.exe" -m pytest -n 0 -q --tb=short tests\infrastructure',
            orphan=True,
            age_s=3 * 3600.0,
        )
        assert v.action == "kill"

    def test_scheduler_whitelisted(self):
        v = _classify(
            cmdline=r'"C:\...\python.exe" -m zephyr.data.scheduler',
            whitelist_hit="whitelist:zephyr\\.data\\.scheduler",
            orphan=True,  # 事故实证：scheduler 父进程已死仍是合法服务
            age_s=8 * 3600.0,
            cpu_pct=100.0,
        )
        assert v.action == "skip"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
