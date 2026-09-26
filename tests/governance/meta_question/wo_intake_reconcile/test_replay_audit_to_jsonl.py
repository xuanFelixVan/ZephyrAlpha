# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md | §2.2 差集仲裁（pg_only→回放补账）
# [MODULE] tests.governance.meta_question.wo_intake_reconcile.test_replay_audit_to_jsonl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts/governance/meta_question/wo_intake_reconcile/replay_audit_to_jsonl.py（importlib 文件装载）
# [CONSUMERS] WO-002 收口验收（逐日事件数差=0 的补账臂可复算性）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 零 PG / 零生产账写入：行集与 JSONL 全在 tmp_path 构造
# [MODIFY-GUARD] scripts/governance/check_meta_question_audit_reconcile.py（身份键口径真源，改一边必改另一边）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红
# [TESTS] 本件即测试
# [TTL] permanent
"""回放补账器测试（WO-002）：缺行必补、幂等零写、越词表拒放、行形状与既有批同构。"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

_SPEC = importlib.util.spec_from_file_location(
    "replay_audit_to_jsonl",
    REPO_ROOT / "scripts" / "governance" / "meta_question" / "wo_intake_reconcile" / "replay_audit_to_jsonl.py",
)
replay = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = replay
_SPEC.loader.exec_module(replay)

VOCAB = frozenset({"register", "update", "degraded_check", "exam_writeback", "read"})


def _row(
    q_id: str = "PQ-0001",
    what: str = "update",
    *,
    day: str = "2026-09-24",
    evidence: str = "Phase0 分诊认领 W1",
    actor: str = "st-metaq-x",
) -> dict[str, Any]:
    when = datetime.fromisoformat(f"{day}T00:37:39.969893+00:00")
    return {
        "object": q_id,
        "who": actor,
        "what": what,
        "before": {"status": "answered"},
        "after": {"status": "mining"},
        "evidence": evidence,
        "when_utc": when,
    }


def _jsonl_with(rows: list[dict[str, Any]], tmp_path: Path) -> Path:
    path = tmp_path / "audit.jsonl"
    path.write_text("".join(json.dumps(replay._line(r), ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def test_no_gap_when_jsonl_already_covers(tmp_path: Path) -> None:
    rows = [_row("PQ-0001"), _row("PQ-0002")]
    existing = replay._load_existing_keys(_jsonl_with(rows, tmp_path))
    lines, findings = replay.build_missing_lines(rows, existing, VOCAB)
    assert lines == [] and findings == []


def test_red_missing_lines_are_rebuilt_byte_identical(tmp_path: Path) -> None:
    """红腿：生产账里删两行→回放补出的字节必须与被删原行逐字相同（键序/diff 形状不许自创）。"""
    rows = [_row(f"PQ-{i:04d}") for i in range(1, 6)]
    full = _jsonl_with(rows, tmp_path)
    original_lines = full.read_text(encoding="utf-8").splitlines()
    dropped = original_lines[2:4]  # 删 PQ-0003 / PQ-0004 两行
    kept = original_lines[:2] + original_lines[4:]
    full.write_text("".join(line + "\n" for line in kept), encoding="utf-8")
    lines, findings = replay.build_missing_lines(rows, replay._load_existing_keys(full), VOCAB)
    assert len(lines) == 2 and findings == []
    assert sorted(lines) == sorted(dropped)


def test_multiset_duplicate_rows_need_equal_rows(tmp_path: Path) -> None:
    rows = [_row("PQ-0001"), _row("PQ-0001")]  # 同键两行
    existing = replay._load_existing_keys(_jsonl_with(rows[:1], tmp_path))
    lines, _ = replay.build_missing_lines(rows, existing, VOCAB)
    assert len(lines) == 1


def test_off_vocab_row_is_refused_and_reported(tmp_path: Path) -> None:
    rows = [_row("PQ-0009", what="frobnicated")]
    lines, findings = replay.build_missing_lines(rows, replay._load_existing_keys(tmp_path / "none.jsonl"), VOCAB)
    assert lines == []
    assert findings and "off_vocab_what" in findings[0]


def test_line_shape_matches_registry_schema() -> None:
    line = replay._line(_row("PQ-0007", evidence="  带空白证据  "))
    assert list(line) == list(replay.LINE_KEYS)
    assert line["when"].endswith("+00:00")
    assert line["evidence"] == "带空白证据"
    assert line["diff"] == [{"before": {"status": "answered"}, "after": {"status": "mining"}}]


def test_identity_key_is_utc_independent_of_source_offset() -> None:
    east = {
        "object": "PQ-0001",
        "what": "update",
        "who": "s",
        "when_utc": datetime(2026, 9, 24, 8, 37, 39, 969893, tzinfo=timezone.utc).astimezone(timezone.utc),
    }
    same = replay._identity(east["object"], east["what"], east["who"], east["when_utc"], "e")
    assert same[3] == "2026-09-24T08:37:39.969893+00:00"


def test_malformed_existing_lines_are_skipped_not_fatal(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    path.write_text(
        '{"who":"s","when":"nonsense","what":"update","object":"PQ-1","diff":[],"evidence":""}\nnot json at all\n',
        encoding="utf-8",
    )
    assert sum(replay._load_existing_keys(path).values()) == 0


def test_main_dry_run_does_not_touch_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [_row("PQ-0001"), _row("PQ-0002")]
    target = _jsonl_with(rows[:1], tmp_path)
    monkeypatch.setattr(replay, "_load_pg_rows", lambda *_a, **_k: (rows, None))
    monkeypatch.setattr(replay, "_vocab", lambda: VOCAB)
    before = target.read_text(encoding="utf-8")
    assert replay.main(["--jsonl", str(target)]) == replay.EXIT_GAP
    assert target.read_text(encoding="utf-8") == before, "dry-run 禁写生产账"


def test_main_apply_appends_then_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [_row("PQ-0001"), _row("PQ-0002")]
    target = _jsonl_with(rows[:1], tmp_path)
    monkeypatch.setattr(replay, "_load_pg_rows", lambda *_a, **_k: (rows, None))
    monkeypatch.setattr(replay, "_vocab", lambda: VOCAB)
    assert replay.main(["--jsonl", str(target), "--apply"]) == replay.EXIT_DONE
    assert len(target.read_text(encoding="utf-8").splitlines()) == 2
    assert replay.main(["--jsonl", str(target), "--apply"]) == replay.EXIT_DONE
    assert len(target.read_text(encoding="utf-8").splitlines()) == 2, "幂等：重跑零追加"


def test_main_pg_failure_is_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(replay, "_load_pg_rows", lambda *_a, **_k: ([], "pg_connect_failed: x"))
    monkeypatch.setattr(replay, "_vocab", lambda: VOCAB)
    target = tmp_path / "audit.jsonl"
    assert replay.main(["--jsonl", str(target), "--apply"]) == replay.EXIT_ERROR
    assert not target.exists()
