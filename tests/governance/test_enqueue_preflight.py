# [A_test] module_id: MOD-GOV-046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-046 | scripts/governance/enqueue_preflight.py | §QCure-M1-M2
# [MODULE] tests.governance.test_enqueue_preflight
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.enqueue_preflight; zephyr.gov_enforcement.rule_bridge.commit_preflight
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_enqueue_preflight.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 隔离，不碰真实 .runtime/commit_queue 与生产注册表；QCure 四施工件红蓝例：M2.2 冲突字节预扫（真冲突命中/纯 setext ======= 不误报/二进制与超限跳过/转义样例行首锚定）、M1.1 预检挂线（blocking→exit 2 / 设施异常→fail-open 放行 / skip 集透传）、M1.3 requeue 三补（base_blobs 填充/envelope 继承/熔断+--force）、M3.3 处方与标记表
# [MODIFY-GUARD] QCure st-qcure-20260925 M1.1/M1.3/M2.2/M3.3 验收闸：判据/skip 集/熔断阈值变更打红本文件
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_enqueue_preflight.py — QCure 入队口预检四施工件验收（st-qcure-20260925）。

覆盖：M2.2 冲突标记字节预扫（enqueue_preflight.scan_conflict_markers + CLI 拒收）、
M1.1 入队预检挂线（run_enqueue_preflight + _cmd_enqueue 接线，mock 注入红蓝例）、
M1.3 requeue 三补（base_blobs/envelope/熔断）、M3.3 死因处方与标记表补齐。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.governance.enqueue_preflight as ep
from zephyr.gov_enforcement.rule_bridge.commit_preflight import (
    CommitPreflightResult,
    PreflightFinding,
)


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    """队列根固定落 tmp_path（隔离真实 .runtime/commit_queue，同 test_commit_queue 口径）。"""
    return tmp_path / "commit_queue"


@pytest.fixture()
def wt(tmp_path: Path) -> Path:
    """裸 CLI enqueue 用工作区（tmp 非 git 目录——网关构造必败=真实 degraded 通道）。"""
    w = tmp_path / "wt"
    w.mkdir()
    return w


def _blocking_result(gate_id: str = "CREATE-GUARD", detail: str = "a.py 无 creation_token") -> CommitPreflightResult:
    return CommitPreflightResult(
        findings=[PreflightFinding(gate_id=gate_id, detail=detail, escape_hint="登记 token")],
        degraded=[],
        elapsed_ms=1.0,
    )


def _make_dead(root: Path, files: list[tuple[str, bytes]] | None = None, meta_extra: dict | None = None) -> dict:
    """制造一枚死信项（enqueue → landing 注定失败 drain，同 test_commit_queue 口径）。"""
    item = cq.enqueue_item(
        "AI-R", "m-orig", files or [("a.txt", b"v1")], queue_root=root, options=cq.EnqueueOptions(meta_extra=meta_extra)
    )
    stats = cq.drain_queue(root, landing=lambda i, r: cq.LandingResult(ok=False, reason="boom-模拟门禁失败"))
    assert stats["dead"] == 1
    return item


def _read_dead(root: Path, qid: str) -> dict:
    return json.loads((root / "dead" / f"{qid}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# M2.2 冲突标记字节预扫（保守判据红蓝例）
# ---------------------------------------------------------------------------


class TestConflictMarkerScan:
    MAX = 10 * 1024 * 1024

    def test_true_conflict_hit(self) -> None:
        content = b"line1\n<<<<<<< HEAD\nmine\n=======\ntheirs\n>>>>>>> other\n"
        hit = ep.scan_conflict_markers("a.txt", content, max_bytes=self.MAX)
        assert hit is not None
        assert "第 2 行" in hit and "开始标记" in hit
        assert "三段冲突体" in hit  # 开始/结束/分隔三段俱全

    def test_end_marker_only_hit(self) -> None:
        hit = ep.scan_conflict_markers("a.txt", b"x\n>>>>>>> other\n", max_bytes=self.MAX)
        assert hit is not None and "结束标记" in hit

    def test_setext_heading_no_false_positive(self) -> None:
        """纯 markdown setext ======= 标题（无开始/结束标记）不误报——保守判据核心蓝例。"""
        assert ep.scan_conflict_markers("doc.md", b"Title\n=======\nbody text\n", max_bytes=self.MAX) is None
        assert ep.scan_conflict_markers("doc.md", b"Title\n==========\n", max_bytes=self.MAX) is None
        assert ep.scan_conflict_markers("doc.md", b"======= foo bar\n", max_bytes=self.MAX) is None

    def test_separator_alone_never_hits(self) -> None:
        """======= 仅在文件同时含开始/结束标记时才算——分隔线单独出现永不命中。"""
        assert ep.scan_conflict_markers("y.yaml", b"a: 1\n=======\nb: 2\n", max_bytes=self.MAX) is None

    def test_binary_skipped(self) -> None:
        assert ep.scan_conflict_markers("img.bin", b"\x00\x01<<<<<<< HEAD\n", max_bytes=self.MAX) is None

    def test_oversize_skipped(self) -> None:
        """超限跳过（与 blob 上限同源判据，上限内轻检另行拒收）。"""
        assert ep.scan_conflict_markers("big.txt", b"<<<<<<< HEAD\n", max_bytes=4) is None
        assert ep.scan_conflict_markers("big.txt", b"<<<<<<< HEAD\n", max_bytes=0) is None

    def test_escaped_sample_not_line_start(self) -> None:
        """转义样例：行内注释/缩进形态（非行首锚定）不命中。"""
        assert ep.scan_conflict_markers("x.py", b"x = 1  # <<<<<<< HEAD\\n\n", max_bytes=self.MAX) is None
        assert ep.scan_conflict_markers("x.py", b'x = ">>>>>>> side"\n', max_bytes=self.MAX) is None
        assert ep.scan_conflict_markers("x.py", b"\t>>>>>>> next\n", max_bytes=self.MAX) is None

    def test_crlf_line_ending_hit(self) -> None:
        assert ep.scan_conflict_markers("w.txt", b"ok\r\n<<<<<<< HEAD\r\n", max_bytes=self.MAX) is not None

    def test_clean_file_none(self) -> None:
        assert ep.scan_conflict_markers("ok.py", b"def f():\n    return '======='\n", max_bytes=self.MAX) is None

    def test_cli_rejects_conflict_snapshot(self, queue_root: Path, wt: Path, capsys: pytest.CaptureFixture) -> None:
        """CLI 端到端：冲突快照 exit 2 + 处方文本，且拒绝发生在 blob 落袋前（零垃圾 blob）。"""
        (wt / "conflicted.txt").write_bytes(b"a\n<<<<<<< HEAD\nmine\n=======\ntheirs\n>>>>>>> other\n")
        rc = cq.main(
            [
                "--queue-root",
                str(queue_root),
                "enqueue",
                "--session",
                "AI-T",
                "--files",
                "conflicted.txt",
                "--message",
                "m",
                "--worktree-root",
                str(wt),
                "--no-bootstrap",
            ]
        )
        assert rc == 2
        err = capsys.readouterr().err
        assert "DENIED" in err and "合并冲突标记" in err and "解决合并" in err
        assert not list((queue_root / "pending").glob("q-*.json")), "blob 落袋前拒绝=零垃圾 pending"
        assert not (queue_root / "blobs").exists() or not any((queue_root / "blobs").iterdir())


# ---------------------------------------------------------------------------
# M1.1 入队预检挂线（mock 注入红蓝例 + CLI 接线）
# ---------------------------------------------------------------------------


class TestRunEnqueuePreflight:
    def test_blocking_returns_prescription(self) -> None:
        captured: dict = {}

        def fake_gw(project_root):
            captured["root"] = project_root
            return object()

        result = ep.run_enqueue_preflight(
            "D:/some/wt",
            ["a.py"],
            "AI-S",
            "msg",
            gateway_factory=fake_gw,
            preflight_fn=lambda gw, files, sid, **kw: _blocking_result(),
        )
        assert result is not None
        assert "CREATE-GUARD" in result and "处方" in result
        assert str(captured["root"]) == str(Path("D:/some/wt"))

    def test_skip_set_and_audit_event_passthrough(self) -> None:
        captured: dict = {}

        def fake_pf(gw, files, sid, skip_gate_ids=frozenset(), **kw):
            captured["skip"] = set(skip_gate_ids)
            captured["audit_event"] = kw.get("audit_event")
            captured["message"] = kw.get("commit_message")
            captured["files"] = list(files)
            return CommitPreflightResult(findings=[], degraded=[], elapsed_ms=0.5)

        result = ep.run_enqueue_preflight(
            "wt",
            ["a.py", "b.py"],
            "AI-S",
            "hello",
            gateway_factory=lambda project_root: object(),
            preflight_fn=fake_pf,
        )
        assert result is None
        # v1 skip 集与审计标签（mode="enqueue"）必须透传到 run_preflight
        assert captured["skip"] == {"SESSION-REQUIRED", "CLAIM-REQUIRED"}
        assert captured["audit_event"] == "enqueue"
        assert captured["message"] == "hello"
        assert captured["files"] == ["a.py", "b.py"]

    def test_preflight_exception_fail_open(self) -> None:
        """预检设施异常→warn+放行（degraded fail-open，绝不堵入队）——红线例。"""

        def boom(gw, files, sid, **kw):
            raise RuntimeError("preflight 内部炸了")

        assert ep.run_enqueue_preflight("wt", ["a.py"], "AI-S", "", preflight_fn=boom) is None

    def test_gateway_construction_failure_fail_open(self) -> None:
        """网关构造失败（非 git 目录常态）→放行。"""

        def bad_gw(project_root):
            raise RuntimeError("Not a git repository")

        assert ep.run_enqueue_preflight("wt", ["a.py"], "AI-S", "", gateway_factory=bad_gw) is None

    def test_degraded_only_passes(self) -> None:
        result = ep.run_enqueue_preflight(
            "wt",
            ["a.py"],
            "AI-S",
            "",
            preflight_fn=lambda gw, f, s, **kw: CommitPreflightResult(findings=[], degraded=["X-GATE"], elapsed_ms=1.0),
        )
        assert result is None


class TestCmdEnqueueWiring:
    def test_blocking_exit2_no_bag_written(
        self, queue_root: Path, wt: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """blocking→exit 2+逐门禁处方；拒绝在 enqueue_item 之前=零垃圾 blob。"""
        (wt / "a.py").write_bytes(b"x = 1\n")
        monkeypatch.setattr(ep, "run_enqueue_preflight", lambda *a, **k: "入队预检拦截——CREATE-GUARD 处方：登记 token")
        rc = cq.main(
            [
                "--queue-root",
                str(queue_root),
                "enqueue",
                "--session",
                "AI-T",
                "--files",
                "a.py",
                "--message",
                "m",
                "--worktree-root",
                str(wt),
                "--no-bootstrap",
            ]
        )
        assert rc == 2
        err = capsys.readouterr().err
        assert "DENIED" in err and "CREATE-GUARD" in err
        assert not list((queue_root / "pending").glob("q-*.json"))

    def test_fail_open_enqueue_succeeds_end_to_end(
        self, queue_root: Path, wt: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """不 mock：tmp 非 git 工作区网关构造必败→真实 degraded 通道放行→入队成功。"""
        (wt / "a.py").write_bytes(b"x = 1\n")
        rc = cq.main(
            [
                "--queue-root",
                str(queue_root),
                "enqueue",
                "--session",
                "AI-T",
                "--files",
                "a.py",
                "--message",
                "m",
                "--worktree-root",
                str(wt),
                "--no-bootstrap",
            ]
        )
        assert rc == 0
        assert "ENQUEUED" in capsys.readouterr().out
        assert len(list((queue_root / "pending").glob("q-*.json"))) == 1


# ---------------------------------------------------------------------------
# M1.3 requeue 三补（base_blobs 填充 / envelope 继承 / 重投熔断）
# ---------------------------------------------------------------------------


class TestRequeueHardening:
    def test_base_blobs_filled(self, queue_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """M1.3-①：requeue 填 base_head/base_blobs（此前恒 None ⇒ 级联重校验空转）。"""
        import scripts.governance.commit_queue_landing as cql

        old = _make_dead(queue_root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2-current")
        monkeypatch.setattr(cql, "resolve_base_head", lambda repo: "f" * 40)
        monkeypatch.setattr(cql, "resolve_base_blobs", lambda repo, head, paths: {"a.txt": "deadbeef"})
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        new_item = result["item"]
        assert new_item["base_head"] == "f" * 40
        assert new_item["files"][0]["base_blob"] == "deadbeef"

    def test_base_head_none_wiring(self, queue_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """回归蓝例：基底取不到（head=None）→走 resolve_base_blobs(None) 契约=全 None，
        行为与修复前一致（本仓 conftest basetemp 在仓内，非 git 阴性以 head=None 注入）。"""
        import scripts.governance.commit_queue_landing as cql

        old = _make_dead(queue_root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2-current")
        monkeypatch.setattr(cql, "resolve_base_head", lambda repo: None)
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        assert result["item"]["base_head"] is None
        assert result["item"]["files"][0]["base_blob"] is None

    def test_envelope_inherited_from_meta(self, queue_root: Path, tmp_path: Path) -> None:
        """M1.3-②：死信袋 meta.envelope 带进新袋（requeue 是 envelope 唯一丢失点）。"""
        old = _make_dead(queue_root, meta_extra={"envelope": {"final_message": "FM"}})
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        assert result["item"]["meta"]["envelope"] == {"final_message": "FM"}

    def test_envelope_inherited_from_toplevel_fallback(self, queue_root: Path, tmp_path: Path) -> None:
        """M1.3-②：旧位顶层 envelope 同样继承（兼容读）。"""
        old = _make_dead(queue_root)
        dead_path = queue_root / "dead" / f"{old['qid']}.json"
        item = _read_dead(queue_root, old["qid"])
        item["envelope"] = {"final_message": "TOP"}
        dead_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        assert result["item"]["meta"]["envelope"] == {"final_message": "TOP"}

    def test_circuit_breaker_blocks_third_requeue(self, queue_root: Path, tmp_path: Path) -> None:
        """M1.3-③：requeue_count≥3 拒绝重投并给死因处方；原死信项不留 requeued 标注。"""
        old = _make_dead(queue_root, meta_extra={"requeue_count": 2})
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        with pytest.raises(cq.RequeueError, match="重投熔断") as exc_info:
            cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        assert "处方" in str(exc_info.value)
        assert "requeued" not in _read_dead(queue_root, old["qid"]), "熔断拒绝 MUST 不留 requeued 标注"
        assert not list((queue_root / "pending").glob("q-*.json")), "熔断拒绝 MUST 不产生新袋"

    def test_force_bypasses_with_audit_trail(self, queue_root: Path, tmp_path: Path) -> None:
        """M1.3-③：--force 显式越过熔断，计数推进+越权留痕。"""
        old = _make_dead(queue_root, meta_extra={"requeue_count": 2})
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt, force=True)
        meta = result["item"]["meta"]
        assert meta["requeue_count"] == 3
        assert meta["requeue_forced"] is True
        assert meta["requeued_from"] == old["qid"]

    def test_requeue_count_increments(self, queue_root: Path, tmp_path: Path) -> None:
        """M1.3-③：新袋 requeue_count=旧袋+1（首投=1，二投=2 均放行）。"""
        old = _make_dead(queue_root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        assert result["item"]["meta"]["requeue_count"] == 1
        # 第二轮：新项再死→requeue 仍放行（计数 1→2 < 阈值 3）
        cq.drain_queue(queue_root, landing=lambda i, r: cq.LandingResult(ok=False, reason="boom-again"))
        result2 = cq.requeue_dead_item(result["new_qid"], queue_root=queue_root, worktree_root=wt)
        assert result2["item"]["meta"]["requeue_count"] == 2

    def test_cli_force_flag(self, queue_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """CLI --force 旗：无旗熔断拒绝 exit 1，带旗越过 exit 0。"""
        old = _make_dead(queue_root, meta_extra={"requeue_count": 2})
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        base = ["--queue-root", str(queue_root), "requeue", old["qid"], "--worktree-root", str(wt), "--no-bootstrap"]
        assert cq.main(base) == 1
        assert "重投熔断" in capsys.readouterr().err
        assert cq.main([*base, "--force"]) == 0
        assert "REQUEUED" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# M3.3 死因处方 + 标记表补齐 + dead 落册字段
# ---------------------------------------------------------------------------


class TestDeadLetterPrescription:
    def test_create_guard_family(self) -> None:
        p = cq.dead_letter_prescription("landing 异常: CREATE-GUARD: a.py 无 creation_token")
        assert "batch_creation_tokens.py" in p

    @pytest.mark.parametrize(
        "reason,fragment",
        [
            ("注册表合并失败: 三向合并失败 docs/x.yaml", "三向合并"),
            ("身份键重复 module_id=X", "身份键"),
            ("BASE-UNKNOWN: 基底不可知", "BASE-UNKNOWN"),
            ("快照未真应用", "worktree"),
            ("冲突标记: 第 3 行", "解决合并"),
        ],
    )
    def test_new_families_have_prescription(self, reason: str, fragment: str) -> None:
        assert fragment in cq.dead_letter_prescription(reason)

    def test_category_fallbacks(self) -> None:
        assert "requeue" in cq.dead_letter_prescription("网关落盘失败（LOCK_TIMEOUT）")
        # item 类且无专属处方条目（快进判定失败）→三分类兜底
        assert "gate 标识" in cq.dead_letter_prescription("快进判定失败 base=X")
        assert "人工排查" in cq.dead_letter_prescription("boom-完全未知死因")
        assert cq.dead_letter_prescription("")  # 空串不上抛

    @pytest.mark.parametrize(
        "marker",
        ["三向合并失败", "身份键重复", "基底不可知", "BASE-UNKNOWN", "快照未真应用", "冲突标记"],
    )
    def test_marker_table_new_families_classified_item(self, marker: str) -> None:
        """M3.3 标记表补族：六类盲区死因从 other 归位 item。"""
        assert cq.classify_dead_reason(f"landing 失败: {marker} 详见 details") == "item"

    def test_dead_item_carries_prescription_and_owner(self, queue_root: Path) -> None:
        """死信落册点：dead 项 JSON 自带 prescription + owner_session 字段。"""
        item = cq.enqueue_item("AI-R", "m", [("a.txt", b"v")], queue_root=queue_root)
        cq.drain_queue(queue_root, landing=lambda i, r: cq.LandingResult(ok=False, reason="boom-模拟门禁失败"))
        dead = _read_dead(queue_root, item["qid"])
        assert dead["prescription"], "处方字段 MUST 非空"
        assert dead["owner_session"] == "AI-R"
