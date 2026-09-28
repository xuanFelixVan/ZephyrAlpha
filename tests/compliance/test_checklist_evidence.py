# [TESTS] tests/compliance/test_checklist_evidence.py
# [COVERAGE] src/zephyr/compliance/checklist_evidence.py（MOD-CMP-019）
# tests/ 豁免 creation_token（根宪法 §1 CREATE-GUARD）
# [TTL] permanent

"""清单闸完成度证据写侧测试（F62 雷三批）。

全部证据路径注入 tmp_path（根宪法 §9 第 6 条禁测试写生产 data/）；
交易日显式传参，避免跨午夜 flaky。
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from zephyr.compliance.checklist_evidence import (
    ACK_SECRET_KEY,
    DEFAULT_EVIDENCE_DIR,
    ChecklistEvidenceError,
    ChecklistEvidenceProvider,
    ChecklistEvidenceWriter,
    main,
    today_shanghai,
)
from zephyr.compliance.discipline_must_do_checker import (
    ChecklistAction,
    ChecklistCheckpoint,
    ChecklistCompletionChecker,
)

_TD = today_shanghai(datetime(2026, 9, 28, 4, 0, tzinfo=timezone.utc))  # 北京 12:00
_NOW = datetime(2026, 9, 28, 4, 0, tzinfo=timezone.utc)
_INTRADAY_KEYS = {"signal_compliance_check", "risk_param_confirm", "position_limit_verify"}


# ---------------------------------------------------------------------
# today_shanghai（交易日口径）
# ---------------------------------------------------------------------


def test_today_shanghai_converts_utc_to_beijing_date() -> None:
    """UTC 20:00 = 北京次日 04:00 → 交易日口径取北京日期（跨 UTC 午夜不跨北京日）。"""
    assert today_shanghai(datetime(2026, 9, 28, 20, 0, tzinfo=timezone.utc)) == date(2026, 9, 29)
    assert today_shanghai(datetime(2026, 9, 28, 4, 0, tzinfo=timezone.utc)) == date(2026, 9, 28)


# ---------------------------------------------------------------------
# 写者①②（机器）
# ---------------------------------------------------------------------


def test_writer_writes_machine_evidence_with_snapshot_and_limits(tmp_path: Path) -> None:
    """写侧①：时间戳+快照 id+limit 集；写侧②：快照 id+执行明细。"""
    writer = ChecklistEvidenceWriter(tmp_path)
    p1 = writer.write_risk_param_confirm(
        "snap-1",
        {"max_single_position": 0.05},
        trade_date=_TD,
        source="start_paper_session.assemble_session",
    )
    rec1 = json.loads(p1.read_text(encoding="utf-8"))
    assert rec1["item_key"] == "risk_param_confirm"
    assert rec1["trade_date"] == _TD.isoformat()
    assert rec1["snapshot_id"] == "snap-1"
    assert rec1["limits"] == {"max_single_position": 0.05}
    assert rec1["ts"]  # ISO 时间戳在场
    assert rec1["writer"] == "start_paper_session.assemble_session"

    p2 = writer.write_position_limit_verify(
        "snap-1",
        trade_date=_TD,
        source="trading_session._validate_and_submit",
        detail={"symbol": "600519.SH", "risk_blocked": False},
    )
    rec2 = json.loads(p2.read_text(encoding="utf-8"))
    assert rec2["item_key"] == "position_limit_verify"
    assert rec2["detail"] == {"symbol": "600519.SH", "risk_blocked": False}


def test_writer_rejects_empty_source_and_confirmed_by(tmp_path: Path) -> None:
    """无写者标识/无确认来源不受理（禁明文恒真）。"""
    writer = ChecklistEvidenceWriter(tmp_path)
    with pytest.raises(ChecklistEvidenceError):
        writer.write_risk_param_confirm("snap", {}, trade_date=_TD, source="  ")
    with pytest.raises(ChecklistEvidenceError):
        writer.write_position_limit_verify("snap", trade_date=_TD, source="")
    with pytest.raises(ChecklistEvidenceError):
        writer.write_signal_compliance_ack("  ", trade_date=_TD, ack_source="manual_ack_cli")
    assert list(tmp_path.iterdir()) == []  # 一个证据文件都没落


def test_writer_default_dir_is_main_repo_anchor() -> None:
    """默认目录=主仓 data/compliance_log/checklist（仓级锚定，不写测试零调用）。"""
    assert DEFAULT_EVIDENCE_DIR.name == "checklist"
    assert "data" in DEFAULT_EVIDENCE_DIR.parts and "compliance_log" in DEFAULT_EVIDENCE_DIR.parts


# ---------------------------------------------------------------------
# 写者③（人工 ack：HMAC / 来源标注）
# ---------------------------------------------------------------------


def test_ack_without_key_uses_source_annotation_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """密钥缺席=source_annotation_only 明示降级（不冒充强证据）。"""
    monkeypatch.delenv(ACK_SECRET_KEY, raising=False)
    path = ChecklistEvidenceWriter(tmp_path).write_signal_compliance_ack(
        "Owner", trade_date=_TD, ack_source="manual_ack_cli"
    )
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["auth_mode"] == "source_annotation_only"
    assert "hmac" not in rec
    assert rec["confirmed_by"] == "Owner"


def test_ack_with_key_is_hmac_signed_and_tamper_evident(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """密钥在场=强制 HMAC；改动确认人后验签不过=fail-closed 未完成。"""
    monkeypatch.setenv(ACK_SECRET_KEY, "test-ack-key")
    writer = ChecklistEvidenceWriter(tmp_path)
    writer.write_signal_compliance_ack("Owner", trade_date=_TD, ack_source="manual_ack_cli")
    provider = ChecklistEvidenceProvider(tmp_path)
    assert "signal_compliance_check" in provider(ChecklistCheckpoint.INTRADAY, _TD)

    # 篡改 confirmed_by（保 hmac 字段不动）→ 验签不过
    path = tmp_path / "signal_compliance_check.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec["confirmed_by"] = "Forger"
    path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    assert "signal_compliance_check" not in provider(ChecklistCheckpoint.INTRADAY, _TD)


def test_forged_hmac_mode_without_key_is_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """手写 hmac 形态但密钥未配置 → 无法验证 → 按未完成处理（fail-closed）。"""
    monkeypatch.delenv(ACK_SECRET_KEY, raising=False)
    path = tmp_path / "signal_compliance_check.json"
    path.write_text(
        json.dumps(
            {
                "item_key": "signal_compliance_check",
                "trade_date": _TD.isoformat(),
                "ts": _NOW.isoformat(),
                "writer": "manual_ack_cli",
                "auth_mode": "hmac_sha256",
                "hmac": "deadbeef",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    assert "signal_compliance_check" not in ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, _TD)


# ---------------------------------------------------------------------
# 读侧 provider（全 fail-closed）
# ---------------------------------------------------------------------


def test_provider_empty_dir_returns_empty_set(tmp_path: Path) -> None:
    assert ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, _TD) == set()


def test_provider_non_intraday_returns_empty_set(tmp_path: Path) -> None:
    """非 INTRADAY 时点本批无写者腿，诚实回空（未装配，不属本批施工面）。"""
    assert ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.PRE_MARKET, _TD) == set()


def test_provider_full_cycle_returns_all_three_keys(tmp_path: Path) -> None:
    writer = ChecklistEvidenceWriter(tmp_path)
    writer.write_risk_param_confirm("snap", {}, trade_date=_TD, source="asm")
    writer.write_position_limit_verify("snap", trade_date=_TD, source="ts")
    writer.write_signal_compliance_ack("Owner", trade_date=_TD, ack_source="manual_ack_cli")
    assert ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, _TD) == _INTRADAY_KEYS


def test_provider_stale_trade_date_is_not_completed(tmp_path: Path) -> None:
    """昨日证据不抵今日（按交易日取证，隔日必须重新落证）。"""
    writer = ChecklistEvidenceWriter(tmp_path)
    writer.write_risk_param_confirm("snap", {}, trade_date=_TD, source="asm")
    assert ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, _TD) == {"risk_param_confirm"}
    assert ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, date(_TD.year, 1, 1)) == set()


def test_provider_corrupt_json_fails_closed_per_item(tmp_path: Path) -> None:
    """烂 JSON 只拖垮对应腿（记未完成），不牵连其余两腿。"""
    writer = ChecklistEvidenceWriter(tmp_path)
    writer.write_risk_param_confirm("snap", {}, trade_date=_TD, source="asm")
    writer.write_signal_compliance_ack("Owner", trade_date=_TD, ack_source="cli")
    (tmp_path / "position_limit_verify.json").write_text("{corrupt", encoding="utf-8")
    completed = ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, _TD)
    assert completed == {"risk_param_confirm", "signal_compliance_check"}


def test_provider_source_annotation_ack_requires_confirmed_by(tmp_path: Path) -> None:
    """source 标注形态缺 confirmed_by=未完成（手删字段不可白嫖完成态）。"""
    writer = ChecklistEvidenceWriter(tmp_path)
    writer.write_signal_compliance_ack("Owner", trade_date=_TD, ack_source="cli")
    path = tmp_path / "signal_compliance_check.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    del rec["confirmed_by"]
    path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    assert "signal_compliance_check" not in ChecklistEvidenceProvider(tmp_path)(ChecklistCheckpoint.INTRADAY, _TD)


# ---------------------------------------------------------------------
# checker 集成（INTRADAY Hard Block 语义不放宽）
# ---------------------------------------------------------------------


def test_checker_complete_then_missing_flips_to_hard_block(tmp_path: Path) -> None:
    """三腿齐=NONE；删一腿=INTRADAY Hard Block（裁定值不改）。"""
    writer = ChecklistEvidenceWriter(tmp_path)
    provider = ChecklistEvidenceProvider(tmp_path)
    checker = ChecklistCompletionChecker(provider)

    writer.write_risk_param_confirm("snap", {}, trade_date=_TD, source="asm")
    writer.write_position_limit_verify("snap", trade_date=_TD, source="ts")
    writer.write_signal_compliance_ack("Owner", trade_date=_TD, ack_source="cli")
    verdict = checker.check_checkpoint(ChecklistCheckpoint.INTRADAY, _NOW, trade_date=_TD)
    assert verdict.action is ChecklistAction.NONE
    assert verdict.complete is True

    (tmp_path / "position_limit_verify.json").unlink()
    verdict = checker.check_checkpoint(ChecklistCheckpoint.INTRADAY, _NOW, trade_date=_TD)
    assert verdict.action is ChecklistAction.HARD_BLOCK
    assert verdict.missing_items == ("position_limit_verify",)


# ---------------------------------------------------------------------
# ack CLI
# ---------------------------------------------------------------------


def test_cli_ack_writes_receipt_and_status_reports_done(tmp_path: Path, capsys: pytest.Capsys) -> None:
    """ack 子命令落确认件；status 同日读出 DONE；跨日读出 MISSING。"""
    rc = main(
        [
            "ack",
            "--confirmed-by",
            "Owner",
            "--note",
            "信号合规已复核",
            "--base-dir",
            str(tmp_path),
            "--trade-date",
            _TD.isoformat(),
        ]
    )
    assert rc == 0
    ack_file = tmp_path / "signal_compliance_check.json"
    assert ack_file.is_file()
    rec = json.loads(ack_file.read_text(encoding="utf-8"))
    assert rec["confirmed_by"] == "Owner"
    assert rec["ack_source"] == "manual_ack_cli"

    rc = main(["status", "--base-dir", str(tmp_path), "--trade-date", _TD.isoformat()])
    assert rc == 0
    out = capsys.readouterr().out
    assert "signal_compliance_check: DONE" in out
    assert "risk_param_confirm: MISSING" in out
    assert "position_limit_verify: MISSING" in out


def test_cli_ack_rejects_blank_confirmed_by(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["ack", "--confirmed-by", "  ", "--base-dir", str(tmp_path), "--trade-date", _TD.isoformat()])
    assert list(tmp_path.iterdir()) == []


def test_cli_ack_rejects_bad_trade_date(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["ack", "--confirmed-by", "Owner", "--base-dir", str(tmp_path), "--trade-date", "2026/09/28"])
