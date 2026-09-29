"""TRD-A20/21 双闸机械判定器测试（G1 密钥轮换 + G7 仓位参数 confirmed）。

覆盖：G1 步骤5 完成态+回执 verified 双条件；叫核对只报键名绝不打印值、
占位符/缺失 fail-closed 拦截；G7 proposed=FAIL+effective_hard_cap=0（fail-closed）、
confirmed 全绿、签发不完整=FAIL、表值与代码常量漂移=FAIL、文件缺失=FAIL。
全部读写 tmp_path，禁写生产路径。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

sys_path_entry = str(
    next(p for p in Path(__file__).resolve().parents if (p / "scripts" / "governance").exists())
    / "scripts"
    / "governance"
)
if sys_path_entry not in __import__("sys").path:
    __import__("sys").path.insert(0, sys_path_entry)

from check_trd_a20_a21_dual_gates import (  # noqa: E402
    check_g1_key_rotation,
    check_g7_position_params,
    effective_hard_cap,
    run_all,
    verify_key_presence,
)


def _write_report(tmp_path: Path, done: bool) -> Path:
    marker = "✅" if done else "**催办 Owner**"
    report = tmp_path / "tc10_owner_report.md"
    report.write_text(
        "| 步骤 | 内容 | 状态 | 交接 |\n|---|---|---|---|\n"
        f"| 步骤5 | 密钥轮换后核对（AI 只报键名/格式绝不打印值） | {marker} | Owner 轮换后主动叫核对 |\n",
        encoding="utf-8",
    )
    return report


def _write_receipt(tmp_path: Path, verified: bool) -> Path:
    rdir = tmp_path / "receipts"
    rdir.mkdir(exist_ok=True)
    (rdir / "2026-09-30.json").write_text(
        json.dumps({"verified": verified, "keys": ["OKX_ACCESS_KEY"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    return rdir


def _write_params(tmp_path: Path, **overrides) -> Path:
    params = {
        "schema_version": 1,
        "status": "proposed",
        "hard_cap": 0.60,
        "transition": {"threshold": 0.60, "factor_low": 0.5, "factor_high": 0.7},
        "budget_bands": {
            "capitulation": [0.00, 0.10],
            "accumulation": [0.20, 0.30],
            "ignition": [0.30, 0.50],
            "expansion": [0.50, 0.70],
            "euphoria": [0.00, 0.30],
            "distribution": [0.00, 0.00],
        },
        "owner_sign": {"signed_by": "", "signed_at": "", "ruling_ref": ""},
    }
    params.update(overrides)
    path = tmp_path / "position_parameters.yaml"
    path.write_text(yaml.safe_dump(params, allow_unicode=True), encoding="utf-8")
    return path


# ============ G1 密钥轮换（TRD-A20） ============


def test_g1_fail_when_owner_not_done(tmp_path: Path) -> None:
    """现状红：步骤5=催办 Owner → FAIL（fail-closed，不因催办中而放行）。"""
    gate = check_g1_key_rotation(report_path=_write_report(tmp_path, done=False), receipt_dir=tmp_path / "nope")
    assert gate["verdict"] == "FAIL"
    assert "Owner" in gate["evidence"] or "非完成态" in gate["evidence"]


def test_g1_fail_when_done_but_receipt_missing(tmp_path: Path) -> None:
    gate = check_g1_key_rotation(report_path=_write_report(tmp_path, done=True), receipt_dir=tmp_path / "empty")
    (tmp_path / "empty").mkdir()
    assert (
        check_g1_key_rotation(report_path=_write_report(tmp_path, True), receipt_dir=tmp_path / "empty")["verdict"]
        == "FAIL"
    )
    assert gate["verdict"] == "FAIL"


def test_g1_pass_when_done_and_receipt_verified(tmp_path: Path) -> None:
    gate = check_g1_key_rotation(
        report_path=_write_report(tmp_path, done=True), receipt_dir=_write_receipt(tmp_path, verified=True)
    )
    assert gate["verdict"] == "PASS"


def test_g1_fail_when_receipt_not_verified(tmp_path: Path) -> None:
    gate = check_g1_key_rotation(
        report_path=_write_report(tmp_path, done=True), receipt_dir=_write_receipt(tmp_path, verified=False)
    )
    assert gate["verdict"] == "FAIL"


def test_verify_key_presence_reports_names_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """只报键名/状态，绝不回传值；缺失键=fail 状态（fail-closed）。"""
    monkeypatch.setenv("ZEPHYR_TEST_OK_KEY", "sk-real-value-7712abc")
    results = verify_key_presence(("ZEPHYR_TEST_OK_KEY", "ZEPHYR_TEST_MISSING_KEY"))
    by_key = {r["key"]: r["status"] for r in results}
    assert by_key["ZEPHYR_TEST_OK_KEY"] == "ok"
    assert by_key["ZEPHYR_TEST_MISSING_KEY"].startswith("fail:")
    dump = json.dumps(results)
    assert "sk-real-value-7712abc" not in dump  # 值零泄漏


def test_verify_key_presence_intercepts_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    """占位值（"changeme" 等）=拦截为 fail（F105 fail-closed 通道联动）。"""
    monkeypatch.setenv("ZEPHYR_TEST_PLACEHOLDER_KEY", "changeme")
    results = verify_key_presence(("ZEPHYR_TEST_PLACEHOLDER_KEY",))
    assert results[0]["status"].startswith("fail:")


# ============ G7 仓位参数（TRD-A21） ============


def test_g7_fail_while_proposed(tmp_path: Path) -> None:
    gate = check_g7_position_params(_write_params(tmp_path))
    assert gate["verdict"] == "FAIL"
    assert "Owner" in gate["evidence"]


def test_g7_effective_hard_cap_zero_until_confirmed(tmp_path: Path) -> None:
    """fail-closed 消费口径：confirmed 前 cap=0.0（零仓位容许）。"""
    params = yaml.safe_load(_write_params(tmp_path).read_text(encoding="utf-8"))
    assert effective_hard_cap(params) == 0.0


def test_g7_pass_when_confirmed_and_signed(tmp_path: Path) -> None:
    path = _write_params(
        tmp_path,
        status="confirmed",
        owner_sign={"signed_by": "Owner", "signed_at": "2026-09-30", "ruling_ref": "#400"},
    )
    assert check_g7_position_params(path)["verdict"] == "PASS"
    params = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert effective_hard_cap(params) == 0.60


def test_g7_fail_when_confirmed_but_unsigned(tmp_path: Path) -> None:
    """status=confirmed 但 signed_by 空=签发不完整 → FAIL 且 cap 仍 0（禁 AI 代签）。"""
    path = _write_params(tmp_path, status="confirmed")
    assert check_g7_position_params(path)["verdict"] == "FAIL"
    assert effective_hard_cap(yaml.safe_load(path.read_text(encoding="utf-8"))) == 0.0


def test_g7_fail_on_drift_from_code_constants(tmp_path: Path) -> None:
    """表值与 daily_decision_orchestrator 代码常量漂移 → FAIL（双真源禁分叉）。"""
    path = _write_params(
        tmp_path,
        status="confirmed",
        hard_cap=0.80,
        owner_sign={"signed_by": "Owner", "signed_at": "2026-09-30", "ruling_ref": "#400"},
    )
    gate = check_g7_position_params(path)
    assert gate["verdict"] == "FAIL"
    assert "漂移" in gate["evidence"]


def test_g7_fail_when_file_missing(tmp_path: Path) -> None:
    assert check_g7_position_params(tmp_path / "nope.yaml")["verdict"] == "FAIL"


# ============ 联跑契约 ============


def test_run_all_output_contract(tmp_path: Path) -> None:
    """输出契约=admission_gate_design.md §3：逐门 gate_id/verdict/evidence/checked_at + all_green。"""
    result = run_all(
        report_path=_write_report(tmp_path, done=False),
        receipt_dir=tmp_path / "nope",
        params_path=_write_params(tmp_path),
    )
    assert result["all_green"] is False
    assert [g["gate_id"] for g in result["gates"]] == ["G1", "G7"]
    for g in result["gates"]:
        assert set(g) == {"gate_id", "verdict", "evidence", "checked_at"}
