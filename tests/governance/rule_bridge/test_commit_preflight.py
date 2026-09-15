"""P0-A commit_preflight 预检前移单测（方案 v2.1 §3.1，st-commitspeed-20260916）。

覆盖：一过式收集（不短路）/白名单过滤/skip 映射/逃生旗提示/设施异常降级/
审计落盘（tmp_path 隔离）。specs 注入位=fake gate specs，不依赖真实仓库态。
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from zephyr.gov_enforcement.rule_bridge.commit_preflight import (
    PREFLIGHT_GATES,
    PreflightFinding,
    CommitPreflightResult,
    run_preflight,
)


@dataclass
class _FakeSpec:
    gate_id: str
    passed: bool = True
    detail: str = ""
    raise_exc: bool = False
    priority: int = 100

    def check(self, gateway, files, **kwargs):  # noqa: ANN001, ANN003
        if self.raise_exc:
            raise RuntimeError("infra down")
        return self.passed, self.detail


class _FakeGateway:
    def __init__(self, root: object) -> None:
        self.project_root = root


def test_collects_all_failures_one_pass(tmp_path):
    """一过式：多 gate 违规全收集，不短路（治 30 连败重试环）。"""
    specs = [
        _FakeSpec("TTL-METADATA", passed=False, detail="FAIL: x.md missing ttl"),
        _FakeSpec("FOLDER-CAPACITY-HARD-LIMIT", passed=False, detail="121 文件 > 120"),
        _FakeSpec("SESSION-REQUIRED", passed=True),
    ]
    gw = _FakeGateway(tmp_path)
    result = run_preflight(gw, ["docs/_working/x.md"], "s1", specs=specs)
    assert result.blocking
    assert [f.gate_id for f in result.findings] == ["TTL-METADATA", "FOLDER-CAPACITY-HARD-LIMIT"]
    report = result.render_report("s1")
    assert "2 项违规一次给全" in report
    assert "TTL-METADATA" in report and "FOLDER-CAPACITY" in report
    # 逃生旗提示在报告里
    assert "ttl/completes_when" in report


def test_whitelist_filter_and_skip(tmp_path):
    """白名单外 gate 不碰；skip_gate_ids 剔除（逃生旗语义）。"""
    specs = [
        _FakeSpec("SESSION-REQUIRED", passed=False, detail="not registered"),
        _FakeSpec("ENCODING-SAFETY", passed=False, detail="should be ignored (not whitelisted)"),
        _FakeSpec("COMMIT-SCOPE", passed=False, detail="4 domains"),
    ]
    gw = _FakeGateway(tmp_path)
    result = run_preflight(gw, ["a.py"], "s1", skip_gate_ids={"SESSION-REQUIRED"}, specs=specs)
    # 白名单外的 ENCODING 未跑；SESSION-REQUIRED 被 skip；只剩 COMMIT-SCOPE
    assert [f.gate_id for f in result.findings] == ["COMMIT-SCOPE"]
    assert result.findings[0].escape_hint.startswith("--allow-multi-domain")


def test_infra_exception_degrades_not_blocks(tmp_path):
    """gate 抛异常=设施故障降级（degraded 记录，不进 findings 不阻断）。"""
    specs = [
        _FakeSpec("CREATE-GUARD", raise_exc=True),  # 不在白名单，不会被调用
        _FakeSpec("REGISTRY-MASS-DELETION", raise_exc=True),
        _FakeSpec("TTL-METADATA", passed=True),
    ]
    gw = _FakeGateway(tmp_path)
    result = run_preflight(gw, ["a.yaml"], "s1", specs=specs)
    assert not result.blocking
    assert result.degraded == ["REGISTRY-MASS-DELETION"]
    assert "degraded" in result.render_report("s1")


def test_preflight_self_exception_returns_degraded(tmp_path):
    """specs 解析整体异常=放行（锁内权威链兜底）。"""
    gw = _FakeGateway(tmp_path)
    result = run_preflight(gw, ["a.py"], "s1", specs=None)
    # _FakeGateway 无 _gate_registry → 整体异常路径 → __preflight__ degraded 放行
    assert not result.blocking
    assert result.degraded == ["__preflight__"]


def test_audit_written_to_tmp(tmp_path):
    """审计落 .runtime/audit/preflight_events.jsonl（project_root=tmp_path 隔离）。"""
    specs = [_FakeSpec("PROTECTED-PATHS", passed=False, detail="AGENTS.md protected")]
    gw = _FakeGateway(tmp_path)
    run_preflight(gw, ["AGENTS.md"], "s1", specs=specs)
    audit = tmp_path / ".runtime" / "audit" / "preflight_events.jsonl"
    assert audit.exists()
    rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
    assert rec["event"] == "blocked"
    assert rec["gates_failed"] == ["PROTECTED-PATHS"]
    assert rec["session_id"] == "s1"


def test_clean_pass_no_block(tmp_path):
    specs = [_FakeSpec(g, passed=True) for g in sorted(PREFLIGHT_GATES)]
    gw = _FakeGateway(tmp_path)
    result = run_preflight(gw, ["a.py", "b.md"], "s1", specs=specs)
    assert not result.blocking
    assert result.findings == []
    report = result.render_report("s1")
    assert "PASSED" in report and "BLOCKED" not in report


def test_finding_render_escape_hint():
    f = PreflightFinding(gate_id="WORKTREE-REQUIRED", detail="非 worktree commit", escape_hint="--allow-non-worktree")
    assert "--allow-non-worktree" in f.render()
    f2 = PreflightFinding(gate_id="X", detail="no hint")
    assert "逃生通道" not in f2.render()


def test_result_dataclass_defaults():
    r = CommitPreflightResult()
    assert r.blocking is False
    assert r.degraded == []
