# [BLUEPRINT] MOD-ML-021 | docs/03_modules/_domain_machine_learning_train/research_data_sandbox/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-021 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_research_data_sandbox
# [TESTS] src/zephyr/ml_train/research_data_sandbox.py
"""MOD-ML-021 单元测试：research_data_sandbox 研究数据沙箱。

蓝图验收（B13-04339/CAND-MLT-029，A3 D-RESEARCH-12）：
独立工作目录（注入 root）+ 生产数据只读视图（写入拦截 Fail-Closed）+
资源配额声明校验 + 产出回写评审状态机（PENDING→APPROVED|REJECTED）。
生产视图/时钟全注入内存替身，不触真实文件系统。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.research_data_sandbox",
    reason="research_data_sandbox not importable",
)

from zephyr.ml_train.research_data_sandbox import (  # noqa: E402
    ResearchDataSandbox,
    ResearchSandboxError,
    ResourceQuota,
    ReviewStatus,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_QUOTA = ResourceQuota(cpu_cores=4.0, memory_mb=8192)
_PROD = {"kline/600519.SH.csv": "date,close\n...", "kline/000001.SH.csv": "date,close\n..."}


def _sandbox(**kw) -> ResearchDataSandbox:
    kw.setdefault("sandbox_root", "/sandbox/researcher-a")
    kw.setdefault("production_root", "/prod/market")
    kw.setdefault("quota", _QUOTA)
    kw.setdefault("production_files", _PROD)
    kw.setdefault("clock", lambda: _T0)
    return ResearchDataSandbox(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# 构造：root / 配额声明校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_roots_empty_or_same_raise(self) -> None:
        with pytest.raises(ResearchSandboxError):
            _sandbox(sandbox_root="")
        with pytest.raises(ResearchSandboxError):
            _sandbox(production_root="")
        with pytest.raises(ResearchSandboxError):
            _sandbox(sandbox_root="/x", production_root="/x")

    def test_roots_nested_raise(self) -> None:
        with pytest.raises(ResearchSandboxError):
            _sandbox(sandbox_root="/prod/market/sb")  # 沙箱嵌套于生产
        with pytest.raises(ResearchSandboxError):
            _sandbox(production_root="/sandbox/researcher-a/prod")  # 生产嵌套于沙箱

    def test_quota_non_positive_raise(self) -> None:
        with pytest.raises(ResearchSandboxError):
            _sandbox(quota=ResourceQuota(cpu_cores=0.0, memory_mb=1024))
        with pytest.raises(ResearchSandboxError):
            _sandbox(quota=ResourceQuota(cpu_cores=1.0, memory_mb=-1))

    def test_quota_over_budget_raise(self) -> None:
        budget = ResourceQuota(cpu_cores=2.0, memory_mb=4096)
        with pytest.raises(ResearchSandboxError):
            _sandbox(max_quota=budget)  # cpu 4>2 且 mem 8192>4096
        ok = _sandbox(quota=ResourceQuota(cpu_cores=2.0, memory_mb=4096), max_quota=budget)
        assert ok.quota.cpu_cores == 2.0

    def test_production_files_bad_path_raise(self) -> None:
        with pytest.raises(ResearchSandboxError):
            _sandbox(production_files={"../escape.csv": "x"})


# ──────────────────────────────────────────────────────────────────────────────
# 生产数据只读视图
# ──────────────────────────────────────────────────────────────────────────────


class TestProductionView:
    def test_read_and_list(self) -> None:
        sb = _sandbox()
        assert sb.read_production("kline/600519.SH.csv").startswith("date,close")
        assert sb.list_production() == ("kline/000001.SH.csv", "kline/600519.SH.csv")

    def test_read_unknown_or_bad_path_raise(self) -> None:
        sb = _sandbox()
        with pytest.raises(ResearchSandboxError):
            sb.read_production("ghost.csv")
        with pytest.raises(ResearchSandboxError):
            sb.read_production("/prod/market/kline/x.csv")  # 绝对路径
        with pytest.raises(ResearchSandboxError):
            sb.read_production("../secret.csv")  # 越界
        with pytest.raises(ResearchSandboxError):
            sb.read_production("")

    def test_write_always_blocked_fail_closed(self) -> None:
        sb = _sandbox()
        with pytest.raises(ResearchSandboxError):
            sb.write_production("kline/600519.SH.csv", "tamper")
        with pytest.raises(ResearchSandboxError):
            sb.write_production("new.csv", "x")
        assert sb.list_production() == ("kline/000001.SH.csv", "kline/600519.SH.csv")  # 未变


# ──────────────────────────────────────────────────────────────────────────────
# 独立工作目录
# ──────────────────────────────────────────────────────────────────────────────


class TestWorkspace:
    def test_write_read_list(self) -> None:
        sb = _sandbox()
        full = sb.write_workspace("out/report.md", "结论")
        assert full == "/sandbox/researcher-a/out/report.md"
        assert sb.read_workspace("out/report.md") == "结论"
        sb.write_workspace("out/report.md", "结论v2")  # 覆盖写
        assert sb.read_workspace("out/report.md") == "结论v2"
        assert sb.list_workspace() == ("out/report.md",)

    def test_workspace_bad_path_or_content_raise(self) -> None:
        sb = _sandbox()
        with pytest.raises(ResearchSandboxError):
            sb.write_workspace("C:/abs/x", "x")
        with pytest.raises(ResearchSandboxError):
            sb.write_workspace("a//b", "x")  # 空段
        with pytest.raises(ResearchSandboxError):
            sb.write_workspace("ok.txt", 123)  # 非字符串
        with pytest.raises(ResearchSandboxError):
            sb.read_workspace("ghost.txt")


# ──────────────────────────────────────────────────────────────────────────────
# 产出回写评审状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestWritebackReview:
    def _submitted(self, sb: ResearchDataSandbox, artifact_id: str = "art-1"):
        sb.write_workspace("out/factor.py", "def f(): ...")
        return sb.submit_writeback(artifact_id, "out/factor.py", "researcher-a")

    def test_submit_pending(self) -> None:
        sb = _sandbox()
        art = self._submitted(sb)
        assert art.status is ReviewStatus.PENDING
        assert sb.review_status("art-1") is ReviewStatus.PENDING

    def test_submit_invalid_raise(self) -> None:
        sb = _sandbox()
        sb.write_workspace("out/factor.py", "x")
        with pytest.raises(ResearchSandboxError):
            sb.submit_writeback("", "out/factor.py", "r")
        with pytest.raises(ResearchSandboxError):
            sb.submit_writeback("art-1", "ghost.py", "r")  # 产出不存在
        with pytest.raises(ResearchSandboxError):
            sb.submit_writeback("art-1", "out/factor.py", "")  # 空提交人
        sb.submit_writeback("art-1", "out/factor.py", "r")
        with pytest.raises(ResearchSandboxError):
            sb.submit_writeback("art-1", "out/factor.py", "r")  # 重复

    def test_approve_archives_content(self) -> None:
        sb = _sandbox()
        self._submitted(sb)
        decision = sb.review_writeback("art-1", approve=True, reviewer="lead")
        assert decision.status is ReviewStatus.APPROVED
        assert sb.review_status("art-1") is ReviewStatus.APPROVED
        assert sb.approved_content("art-1") == "def f(): ..."  # 通过才入回写存档

    def test_reject_no_archive(self) -> None:
        sb = _sandbox()
        self._submitted(sb)
        decision = sb.review_writeback("art-1", approve=False, reviewer="lead", reason="缺验证")
        assert decision.status is ReviewStatus.REJECTED
        assert decision.reason == "缺验证"
        with pytest.raises(ResearchSandboxError):
            sb.approved_content("art-1")

    def test_review_invalid_raise(self) -> None:
        sb = _sandbox()
        self._submitted(sb)
        with pytest.raises(ResearchSandboxError):
            sb.review_writeback("ghost", approve=True, reviewer="lead")  # 未知回写单
        with pytest.raises(ResearchSandboxError):
            sb.review_writeback("art-1", approve=True, reviewer="")  # 空评审人
        sb.review_writeback("art-1", approve=True, reviewer="lead")
        with pytest.raises(ResearchSandboxError):
            sb.review_writeback("art-1", approve=False, reviewer="lead")  # 单次迁移
        with pytest.raises(ResearchSandboxError):
            sb.review_status("ghost")

    def test_queue_filter_and_order(self) -> None:
        sb = _sandbox()
        sb.write_workspace("a.py", "a")
        sb.write_workspace("b.py", "b")
        self._submitted(sb, "art-2")
        self._submitted(sb, "art-1")
        sb.review_writeback("art-1", approve=True, reviewer="lead")
        queue = sb.writeback_queue()
        assert [a.artifact_id for a in queue] == ["art-1", "art-2"]  # 同刻按 id 排序
        pending = sb.writeback_queue(ReviewStatus.PENDING)
        assert [a.artifact_id for a in pending] == ["art-2"]
        approved = sb.writeback_queue(ReviewStatus.APPROVED)
        assert [a.artifact_id for a in approved] == ["art-1"]
        with pytest.raises(ResearchSandboxError):
            sb.writeback_queue("pending")  # 非法状态过滤
