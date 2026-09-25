# [MODULE] tests.governance.test_standard_checkup
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §standards_governance
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""standard_checkup 单元测试——全部 tmp_path/合成数据，零生产路径写入、零 DB 依赖。

覆盖：load_stats 坏行跳过+缺文件抛错 / trigger_rates 已知值（10 提交 2 触发=20%）/
split_windows 两窗切分边界 / retire_candidates 四态+判据线边界 /
false_positive_proxy 豁免计数+缺席诚实返回 / build_proposal schema+两问 /
write_proposal 落盘回读 / CLI --demo 与零候选退出码。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from zephyr.governance.standards_governance.standard_checkup import (
    FP_PROXY_NOTE,
    MIN_WINDOWS,
    CheckupError,
    build_proposal,
    false_positive_proxy,
    load_stats,
    main,
    retire_candidates,
    run_checkup,
    split_windows,
    trigger_rates,
    write_proposal,
)
from zephyr.shared.utils.time_utils import now_utc

AS_OF = datetime(2026, 9, 23, 12, 0, 0, tzinfo=UTC)


def _rec(
    ts: datetime,
    failed: list[str] | None = None,
    reused: dict[str, str] | None = None,
) -> dict[str, object]:
    return {
        "timestamp": ts.isoformat(),
        "n_specs": 100,
        "failed": failed or [],
        "reused": reused or {},
        "ms": {},
        "total_ms": 0.0,
    }


def _win(runs: int, rates: dict[str, float]) -> dict[str, object]:
    """构造 retire_candidates 的单窗报告 fixture（{"runs", "rates"}）。"""
    return {
        "runs": runs,
        "rates": {
            gate: {"fires": int(rate * runs), "runs": runs, "rate": rate}
            for gate, rate in rates.items()
        },
    }


# ────────────────────────── load_stats ──────────────────────────


def test_load_stats_skips_bad_lines(tmp_path: Path) -> None:
    stats = tmp_path / "stats.jsonl"
    good1 = _rec(AS_OF - timedelta(days=1), ["G1"])
    good2 = _rec(AS_OF - timedelta(days=2))
    lines = [
        json.dumps(good1),
        "{this is not json",
        "",
        json.dumps(good2),
        "[1, 2, 3]",
    ]
    stats.write_text("\n".join(lines) + "\n", encoding="utf-8")
    records = load_stats(stats)
    assert len(records) == 2
    assert records[0]["failed"] == ["G1"]
    assert records[1]["failed"] == []


def test_load_stats_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(CheckupError):
        load_stats(tmp_path / "missing.jsonl")


# ────────────────────────── trigger_rates ──────────────────────────


def test_trigger_rates_known_values() -> None:
    records = [_rec(AS_OF - timedelta(hours=i + 1)) for i in range(10)]
    records[0]["failed"] = ["G1"]
    records[1]["failed"] = ["G1", "G2"]
    rates = trigger_rates(records, 30, as_of=AS_OF)
    assert rates["G1"] == {"fires": 2, "runs": 10, "rate": 0.2}
    assert rates["G2"]["fires"] == 1
    assert rates["G2"]["rate"] == pytest.approx(0.1)


def test_trigger_rates_excludes_out_of_window() -> None:
    records = [_rec(AS_OF - timedelta(hours=i + 1), ["G1"]) for i in range(10)]
    records.append(_rec(AS_OF - timedelta(days=31), ["G1"]))
    rates = trigger_rates(records, 30, as_of=AS_OF)
    assert rates["G1"]["runs"] == 10
    assert rates["G1"]["fires"] == 10


# ────────────────────────── split_windows ──────────────────────────


def test_split_windows_two_window_boundary() -> None:
    edge = _rec(AS_OF - timedelta(days=10))            # 恰在窗 0 起点（半开 [start, end)）→ 窗 1
    in_w0 = _rec(AS_OF - timedelta(days=9, hours=23))  # 窗 0 内
    in_w1 = _rec(AS_OF - timedelta(days=19, hours=23))  # 窗 1 内
    too_old = _rec(AS_OF - timedelta(days=20, hours=1))  # 落窗外（index 2）→ 丢弃
    future = _rec(AS_OF + timedelta(days=1))           # 未来时间戳 → 丢弃
    buckets = split_windows([edge, in_w0, in_w1, too_old, future], 10, 2, as_of=AS_OF)
    assert len(buckets) == 2
    assert buckets[0] == [in_w0]
    assert buckets[1] == [edge, in_w1]


def test_split_windows_drops_untimestamped_records() -> None:
    bad = {"n_specs": 1, "failed": []}  # 无 timestamp
    buckets = split_windows([bad], 30, 2, as_of=AS_OF)
    assert buckets == [[], []]


# ────────────────────────── retire_candidates ──────────────────────────


def test_retire_candidates_four_states() -> None:
    windows = [
        _win(200, {"G-RETIRE": 0.005, "G-NOISE": 0.60, "G-NORMAL": 0.10}),
        _win(200, {"G-RETIRE": 0.000, "G-NOISE": 0.55, "G-NORMAL": 0.20}),
    ]
    verdict = retire_candidates(windows)
    assert verdict["windows_evaluated"] == 2
    assert verdict["retire"] == ["G-RETIRE"]
    assert verdict["noise"] == ["G-NOISE"]
    assert verdict["normal"] == ["G-NORMAL"]
    assert verdict["insufficient"] == []
    assert verdict["evaluated_rates"]["G-RETIRE"] == [0.005, 0.0]


def test_retire_candidates_insufficient_single_window() -> None:
    verdict = retire_candidates([_win(50, {"G1": 0.30})])
    assert verdict["windows_evaluated"] == 1
    assert verdict["windows_evaluated"] < MIN_WINDOWS
    assert verdict["insufficient"] == ["G1"]
    assert verdict["retire"] == [] and verdict["noise"] == []


def test_retire_candidates_absent_gate_in_valid_window_counts_zero() -> None:
    # G-HIST 仅老窗（index 2，不进 evaluated）有触发 → 近两窗按 0 计 → 退役候选
    windows = [_win(100, {}), _win(100, {}), _win(100, {"G-HIST": 0.30})]
    verdict = retire_candidates(windows)
    assert verdict["retire"] == ["G-HIST"]
    assert verdict["evaluated_rates"]["G-HIST"] == [0.0, 0.0]


def test_retire_candidates_boundary_exact_lines_are_normal() -> None:
    at_retire = [_win(100, {"G-EDGE": 0.01}), _win(100, {"G-EDGE": 0.01})]
    verdict = retire_candidates(at_retire)
    assert verdict["retire"] == [] and verdict["normal"] == ["G-EDGE"]
    at_noise = [_win(100, {"G-EDGE": 0.50}), _win(100, {"G-EDGE": 0.50})]
    assert retire_candidates(at_noise)["noise"] == []


# ────────────────────────── false_positive_proxy ──────────────────────────


def test_false_positive_proxy_counts_embedded_skip_events() -> None:
    records = [
        _rec(AS_OF, reused={"HELD-OVERLAP": "skipped"}),
        _rec(AS_OF, reused={"HELD-OVERLAP": "skipped", "X": "preflight_reused"}),
        _rec(AS_OF, reused={"OTHER": "preflight_reused"}),
    ]
    assert false_positive_proxy(records) == {"HELD-OVERLAP": 2}


def test_false_positive_proxy_explicit_records_take_precedence() -> None:
    records = [_rec(AS_OF, reused={"A": "skipped"})]
    explicit = [{"gate_id": "B"}, {"gate_id": "B"}, {"gate_id": "C"}]
    assert false_positive_proxy(records, explicit) == {"B": 2, "C": 1}


def test_false_positive_proxy_absent_returns_empty_with_note() -> None:
    assert false_positive_proxy([_rec(AS_OF)]) == {}
    assert FP_PROXY_NOTE  # 诚实注记常量在案——报告必携带，不虚构精度


# ────────────────────────── build_proposal / write_proposal ──────────────────────────


def test_build_proposal_schema_complete_with_two_questions() -> None:
    proposal = build_proposal(
        "STD-PROP-TEST-001",
        "gate_trigger_rate",
        {"metric": "trigger_rate", "observed": 0.004},
        ".runtime/audit/gate_execution_stats.jsonl",
        {"windows_evaluated": 2},
        {"action": "retire_candidate"},
        impact_note="退役近零触发 gate，降规范预算",
    )
    for key in (
        "proposal_id", "date", "ruler_id", "current_value", "source_path",
        "evidence", "proposed_value", "replay_criteria_preview",
        "expected_impact", "status",
    ):
        assert key in proposal, f"缺字段 {key}"
    assert proposal["status"] == "draft"
    parsed = datetime.fromisoformat(proposal["date"])
    assert parsed.tzinfo is not None and proposal["date"].endswith("+00:00")
    preview = proposal["replay_criteria_preview"]
    assert "new_pass = 0" in preview["P1_该拦放走"]
    assert "0.02" in preview["P2_误拦不增"]
    assert "0.98" in preview["P3_集合保持"] and "0.95" in preview["P3_集合保持"]
    assert "P4_分层稳健" in preview
    assert set(proposal["expected_impact"]) == {"q1_better_where", "q2_manual_eliminated"}
    note = "退役近零触发 gate，降规范预算"
    assert proposal["expected_impact"]["q1_better_where"] == note
    assert proposal["expected_impact"]["q2_manual_eliminated"] == note


def test_build_proposal_impact_defaults_to_placeholder() -> None:
    proposal = build_proposal("P", "ruler", {}, "src", {}, {})
    assert "待补" in proposal["expected_impact"]["q1_better_where"]
    assert "待补" in proposal["expected_impact"]["q2_manual_eliminated"]


def test_write_proposal_roundtrip(tmp_path: Path) -> None:
    proposal = build_proposal(
        "STD-PROP-TEST-002", "gate_trigger_rate", {"observed": 0.6},
        "stats.jsonl", {"kind": "noise"}, {"action": "noise_candidate"},
        impact_note="噪音候选观察",
    )
    out = write_proposal(proposal, tmp_path)
    assert out == tmp_path / "STD-PROP-TEST-002.yaml"
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["proposal_id"] == "STD-PROP-TEST-002"
    assert loaded["status"] == "draft"
    assert loaded["expected_impact"]["q1_better_where"] == "噪音候选观察"


def test_write_proposal_missing_id_raises(tmp_path: Path) -> None:
    with pytest.raises(CheckupError):
        write_proposal({"status": "draft"}, tmp_path)


# ────────────────────────── run_checkup 编排 ──────────────────────────


def test_run_checkup_generates_proposals_and_report(tmp_path: Path) -> None:
    now = now_utc()
    records: list[dict[str, object]] = []
    for window in range(2):
        for i in range(20):
            ts = now - timedelta(days=1 + window * 30 + (i % 28), minutes=i)
            failed = ["G-N"] if i < 12 else (["G-X"] if i < 13 else [])
            reused = {"HELD-OVERLAP": "skipped"} if i % 10 == 0 else {}
            records.append(_rec(ts, failed, reused))
    stats = tmp_path / "stats.jsonl"
    stats.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "proposals"
    report = run_checkup(stats, out, window_days=30)
    assert report["bad_lines_skipped"] == 0
    assert report["records_total"] == 40
    assert report["candidates"]["noise"] == ["G-N"]
    assert report["candidates"]["normal"] == ["G-X"]
    assert report["false_positive_proxy"] == {"HELD-OVERLAP": 4}
    assert report["false_positive_proxy_note"] == FP_PROXY_NOTE
    assert len(report["proposals_written"]) == 1
    written = list(out.glob("*.yaml"))
    assert len(written) == 1 and "G-N" in written[0].name


def test_run_checkup_missing_stats_raises(tmp_path: Path) -> None:
    with pytest.raises(CheckupError):
        run_checkup(tmp_path / "nope.jsonl", tmp_path / "out")


# ────────────────────────── CLI ──────────────────────────


def test_cli_demo_end_to_end(tmp_path: Path) -> None:
    rc = main(["checkup", "--demo", "--out", str(tmp_path)])
    assert rc == 0
    yamls = list(tmp_path.glob("*.yaml"))
    assert yamls, "--demo 应产出退役/噪音候选草案"
    all_text = "".join(p.read_text(encoding="utf-8") for p in yamls)
    assert "DEMO-NOISE" in all_text and "DEMO-QUIET" in all_text


def test_cli_zero_candidates_exit_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    now = now_utc()
    records = [_rec(now - timedelta(days=i + 1)) for i in range(5)]
    stats = tmp_path / "stats.jsonl"
    stats.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8",
    )
    out = tmp_path / "out"
    rc = main(["checkup", "--stats", str(stats), "--out", str(out), "--window", "30"])
    assert rc == 0
    assert "零候选" in capsys.readouterr().out
    assert not out.exists() or not list(out.glob("*.yaml"))


def test_cli_missing_stats_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["checkup", "--stats", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path)])
    assert rc == 2
    assert "REFUSED" in capsys.readouterr().err
