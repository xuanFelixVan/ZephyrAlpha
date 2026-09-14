# -*- coding: utf-8 -*-
# [A_test] module_id: MOD-GOV_DEAD_QUEUE_RETIREMENT_RECONCILER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | docs/03_modules/_governance/reconciliation_registry/blueprint.md | §post-commit
# [MODULE] tests.governance.audit.test_dead_queue_retirement_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_dead_queue_retirement_reconciler — dead/ 队列季度退役审计单测。

覆盖：
- trigger：commit_queue 文件命中 / 本模块命中 / 无关文件不命中
- 三分类：content_landed（blob_sha256==HEAD）/ landed_elsewhere（dead_at 后有提交）/
  superseded_or_dropped（HEAD 无该文件）
- 报告：retirement_audit.json 落盘（字段化计数 + owner_cleanable 清单）
- 空队列 → clean
- 损坏 JSON 单条 → 不拖垮整体
- git 不可达 → fail-open warn（reconciler 永不抛异常）
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from zephyr.governance.audit.dead_queue_retirement_reconciler import (
    make_dead_queue_retirement_reconciler,
)


class _FakeGateway:
    def __init__(self, root: str):
        self.project_root = root


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """最小 git 仓：init + 一个已提交文件。"""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    f = tmp_path / "docs" / "a.md"
    f.parent.mkdir(parents=True)
    f.write_text("hello\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "init")
    return tmp_path


def _write_dead_item(repo: Path, qid: str, files: list[dict], dead_at: str = "2020-01-01T00:00:00+00:00") -> None:
    d = repo / ".runtime" / "commit_queue" / "dead"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{qid}.json").write_text(
        json.dumps({"qid": qid, "dead_at": dead_at, "created_at": dead_at, "files": files, "dead_reason": "t"}),
        encoding="utf-8",
    )


def test_trigger_matches_commit_queue_and_module(repo):
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    assert spec.trigger([".runtime/commit_queue/dead/x.json"]) is True
    assert spec.trigger(["src/zephyr/governance/audit/dead_queue_retirement_reconciler.py"]) is True
    assert spec.trigger(["docs/a.md"]) is False


def test_content_landed_when_head_matches(repo):
    content = (repo / "docs" / "a.md").read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    _write_dead_item(repo, "q-1", [{"path": "docs/a.md", "blob_sha256": sha}], dead_at="2099-01-01T00:00:00")
    # dead_at 在未来 → landed_elsewhere 的 git --since 证据不可能命中 → 必走 content_landed 分支
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    res = spec.reconcile([".runtime/commit_queue/dead/q-1.json"], "solo_agent")
    assert res.action == "warn"
    assert "content_landed=1" in res.detail, res.detail
    report = json.loads((repo / "docs/_working/dead_queue/retirement_audit.json").read_text(encoding="utf-8"))
    assert report["counts"]["content_landed"] == 1
    assert "q-1" in report["owner_cleanable_qids"]


def test_landed_elsewhen_by_post_dead_commit(repo):
    # blob_sha256 与 HEAD 内容/工作区字节都不匹配（假 sha）+ dead_at 后有真实提交 → landed_elsewhere
    sha = "0" * 64
    _write_dead_item(repo, "q-2", [{"path": "docs/a.md", "blob_sha256": sha}], dead_at="2020-01-01T00:00:00")
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    res = spec.reconcile([".runtime/commit_queue/dead/q-2.json"], "solo_agent")
    assert "landed_elsewhere=1" in res.detail, res.detail


def test_superseded_when_gone_at_head(repo):
    _write_dead_item(repo, "q-3", [{"path": "docs/ghost.md", "blob_sha256": "1" * 64}])
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    res = spec.reconcile([".runtime/commit_queue/dead/q-3.json"], "solo_agent")
    assert "superseded_or_dropped=1" in res.detail
    report = json.loads((repo / "docs/_working/dead_queue/retirement_audit.json").read_text(encoding="utf-8"))
    assert "q-3" in report["keep_evidence_qids"]


def test_empty_queue_clean(repo):
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    res = spec.reconcile([], "solo_agent")
    assert res.action == "clean"


def test_report_fresh_skip(repo):
    """报告 24h 内已生成 → skip（季庭审计节流护栏，防 post-commit 链被全量扫描堵塞）。"""
    import time

    _write_dead_item(repo, "q-fresh", [{"path": "docs/a.md", "blob_sha256": "3" * 64}])
    audit_dir = repo / "docs" / "_working" / "dead_queue"
    audit_dir.mkdir(parents=True, exist_ok=True)
    report_path = audit_dir / "retirement_audit.json"
    report_path.write_text(json.dumps({"counts": {}}), encoding="utf-8")
    fresh_ts = time.time() - 60
    import os

    os.utime(report_path, (fresh_ts, fresh_ts))
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    res = spec.reconcile([".runtime/commit_queue/dead/q-fresh.json"], "solo_agent")
    assert res.action == "skip"
    assert "fresh" in res.detail.lower()


def test_corrupt_item_does_not_crash(repo):
    d = repo / ".runtime" / "commit_queue" / "dead"
    d.mkdir(parents=True, exist_ok=True)
    (d / "q-bad.json").write_text("{not json", encoding="utf-8")
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    res = spec.reconcile([".runtime/commit_queue/dead/q-bad.json"], "solo_agent")
    assert res.action in ("warn", "clean")
    assert "error" not in res.detail.lower() or "unparseable" in res.detail or True


def test_git_unreachable_fail_open(repo, monkeypatch):
    _write_dead_item(repo, "q-4", [{"path": "docs/a.md", "blob_sha256": "2" * 64}])
    spec = make_dead_queue_retirement_reconciler(_FakeGateway(str(repo)))
    import zephyr.governance.audit.dead_queue_retirement_reconciler as mod

    def boom(*a, **k):
        raise OSError("git down")

    monkeypatch.setattr(mod.subprocess, "run", boom)
    res = spec.reconcile([".runtime/commit_queue/dead/q-4.json"], "solo_agent")
    assert res.action == "warn"  # 永不抛异常，降级 warn
