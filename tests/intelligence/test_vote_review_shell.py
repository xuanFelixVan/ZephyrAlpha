# [BLUEPRINT] MOD-VOTE_REVIEW_SHELL | docs/03_modules/_domain_autonomy_core/vote_review_shell/blueprint.md | §
# [MODULE] tests.intelligence.test_vote_review_shell
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_vote_review_shell.py -q
# [TTL] permanent
"""test_vote_review_shell.py — 投票评审壳（12号文 §3.6/§4.3 P1-2）单元测试.

覆盖 P1-2 验收口径：
①3 候选构造集跑通 approve/reject/abstain+quorum+权重计票全路径（真实
  A2AVoting 引擎内存实例，引擎复用零改动的集成佐证）；胜出候选落盘
  selected/，裁决报告 JSON 字段完整且 human_gate_required 恒 true。
②quorum 不足（投票人数 < participant_count×quorum）→ 候选不通过 →
  no_consensus，缺投会话记 warning。
③平票（approve_weight == reject_weight）→ passed=False → no_consensus，
  不落盘胜出文件。
④候选文件缺失：输入目录缺失 → VoteReviewError(fail-closed)；选票指向缺失
  候选 → warning 记录并忽略，不阻断计票。
⑤引擎异常降级：tally 抛异常 → verdict=engine_error，报告仍落盘交人，不抛出。
⑥人手动 CLI 入口：main(argv) 正常返回 0；输入目录缺失 exit code 2。
全程 tmp_path 文件交接 + 内存引擎/mock，零网络零外部服务。
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_voting import A2AVoting
from zephyr.intelligence.reflexion.vote_review_shell import (
    VoteReviewError,
    main,
    run_review,
)


def _ballot(agent_id: str, votes: dict[str, str], weight: float = 1.0) -> dict:
    return {"agent_id": agent_id, "weight": weight, "votes": votes}


def _write_inbox(tmp_path: Path, candidates: dict[str, str], ballots: list[dict]) -> Path:
    inbox = tmp_path / "inbox"
    (inbox / "candidates").mkdir(parents=True)
    (inbox / "votes").mkdir(parents=True)
    for cid, content in candidates.items():
        (inbox / "candidates" / f"{cid}.md").write_text(content, encoding="utf-8")
    for i, ballot in enumerate(ballots):
        (inbox / "votes" / f"session-{i}.json").write_text(json.dumps(ballot), encoding="utf-8")
    return inbox


def test_three_candidates_full_path(tmp_path):
    """3 候选×3 会话：approve/reject/abstain+权重+quorum 全路径，最优落盘."""
    inbox = _write_inbox(
        tmp_path,
        {"cand-a": "候选A内容", "cand-b": "候选B内容", "cand-c": "候选C内容"},
        [
            _ballot("s1", {"cand-a": "abstain", "cand-b": "approve", "cand-c": "reject"}),
            _ballot("s2", {"cand-a": "approve", "cand-b": "approve", "cand-c": "abstain"}),
            _ballot("s3", {"cand-a": "reject", "cand-b": "approve", "cand-c": "approve"}, weight=2.0),
        ],
    )
    out = tmp_path / "report.json"
    report = run_review(inbox, out)

    assert report["verdict"] == "selected"
    assert report["winner"] == "cand-b"  # 净票 4-0 胜过 cand-c 的 2-1
    assert report["participant_count"] == 3
    assert report["quorum"] == 0.5
    assert report["error"] is None
    assert report["human_gate_required"] is True
    assert len(report["candidates"]) == 3

    by_id = {c["candidate_id"]: c for c in report["candidates"]}
    assert by_id["cand-a"]["passed"] is False  # approve 1 < reject 2
    assert by_id["cand-a"]["abstain_weight"] == 1.0
    assert by_id["cand-b"]["passed"] is True
    assert by_id["cand-b"]["approve_weight"] == 4.0  # 权重 1+1+2 计票
    assert by_id["cand-b"]["quorum_met"] is True
    assert {v["action"] for v in by_id["cand-b"]["votes"]} == {"approve"}
    assert by_id["cand-c"]["passed"] is True  # approve 2 > reject 1
    assert by_id["cand-c"]["reject_weight"] == 1.0

    # 最优落盘 + 报告落盘（全程文件交接）
    assert (tmp_path / "selected" / "cand-b.md").read_text(encoding="utf-8") == "候选B内容"
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk["verdict"] == "selected"
    assert on_disk["winner"] == "cand-b"


def test_quorum_not_met(tmp_path):
    """3 会话仅 1 投票 → 1 < 3×0.5 → quorum_met=False → no_consensus."""
    inbox = _write_inbox(
        tmp_path,
        {"cand-a": "A"},
        [_ballot("s1", {"cand-a": "approve"}), _ballot("s2", {}), _ballot("s3", {})],
    )
    report = run_review(inbox, tmp_path / "report.json")

    assert report["verdict"] == "no_consensus"
    assert report["winner"] is None
    cand = report["candidates"][0]
    assert cand["quorum_met"] is False
    assert cand["passed"] is False
    assert len(report["warnings"]) == 2  # s2/s3 未对 cand-a 投票
    assert not (tmp_path / "selected").exists()


def test_tie_no_consensus(tmp_path):
    """平票 approve_weight == reject_weight → passed=False → 不选优不落盘."""
    inbox = _write_inbox(
        tmp_path,
        {"cand-a": "A"},
        [_ballot("s1", {"cand-a": "approve"}), _ballot("s2", {"cand-a": "reject"}),
         _ballot("s3", {"cand-a": "abstain"})],
    )
    report = run_review(inbox, tmp_path / "report.json")

    assert report["verdict"] == "no_consensus"
    assert report["winner"] is None
    assert report["selected_file"] is None
    cand = report["candidates"][0]
    assert cand["quorum_met"] is True  # 全员到齐
    assert cand["passed"] is False  # approve 1 不严格大于 reject 1
    assert not (tmp_path / "selected").exists()


def test_missing_input_dir_fail_closed(tmp_path):
    """候选目录缺失 → VoteReviewError，fail-closed 不产报告."""
    with pytest.raises(VoteReviewError):
        run_review(tmp_path / "nonexistent", tmp_path / "report.json")
    assert not (tmp_path / "report.json").exists()


def test_vote_to_missing_candidate_warns(tmp_path):
    """选票指向缺失候选 → warning 记录并忽略，不阻断正常计票."""
    inbox = _write_inbox(
        tmp_path,
        {"cand-a": "A"},
        [_ballot("s1", {"cand-a": "approve", "ghost-cand": "approve"})],
    )
    report = run_review(inbox, tmp_path / "report.json")

    assert report["verdict"] == "selected"
    assert report["winner"] == "cand-a"
    assert any("ghost-cand" in w for w in report["warnings"])
    assert len(report["candidates"]) == 1  # ghost-cand 不进计票


def test_invalid_vote_action_fail_closed(tmp_path):
    """非法投票动作 → VoteReviewError（非引擎异常，不降级）."""
    inbox = _write_inbox(
        tmp_path,
        {"cand-a": "A"},
        [_ballot("s1", {"cand-a": "maybe"})],
    )
    with pytest.raises(VoteReviewError):
        run_review(inbox, tmp_path / "report.json")


def test_engine_error_degrades_to_report(tmp_path):
    """引擎异常 → verdict=engine_error，已计票明细+错误落盘交人，不抛出."""
    inbox = _write_inbox(tmp_path, {"cand-a": "A"}, [_ballot("s1", {"cand-a": "approve"})])
    engine = Mock(spec=A2AVoting)
    engine.tally.side_effect = RuntimeError("boom")
    out = tmp_path / "report.json"

    report = run_review(inbox, out, engine=engine)

    assert report["verdict"] == "engine_error"
    assert "boom" in report["error"]
    assert report["winner"] is None
    assert not (tmp_path / "selected").exists()
    assert json.loads(out.read_text(encoding="utf-8"))["verdict"] == "engine_error"


def test_no_candidates(tmp_path):
    """候选池为空 → verdict=no_candidates，不选优."""
    inbox = _write_inbox(tmp_path, {}, [_ballot("s1", {})])
    report = run_review(inbox, tmp_path / "report.json")

    assert report["verdict"] == "no_candidates"
    assert report["candidates"] == []
    assert report["winner"] is None


def test_cli_manual_entry(tmp_path, capsys):
    """人手动 CLI 唯一入口：正常计票返回 0，报告落盘."""
    inbox = _write_inbox(tmp_path, {"cand-a": "A"}, [_ballot("s1", {"cand-a": "approve"})])
    out = tmp_path / "report.json"

    rc = main(["--candidates-dir", str(inbox), "--output", str(out)])

    assert rc == 0
    assert json.loads(out.read_text(encoding="utf-8"))["winner"] == "cand-a"
    printed = json.loads(capsys.readouterr().out)
    assert printed["verdict"] == "selected"


def test_cli_missing_dir_exit_2(tmp_path, capsys):
    """CLI 输入目录缺失 → exit code 2（fail-closed）."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--candidates-dir", str(tmp_path / "nope"), "--output", str(tmp_path / "r.json")])
    assert exc_info.value.code == 2
    capsys.readouterr()
