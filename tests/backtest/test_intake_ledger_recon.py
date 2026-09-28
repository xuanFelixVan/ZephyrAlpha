# [BLUEPRINT] MOD-BT-231 | docs/03_modules/_domain_backtest/blueprint.md | §E1 进货台账对账与蒸发重建
# [MODULE] tests.backtest.test_intake_ledger_recon
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas
# [CONSUMERS] MOD-BT-231 intake_ledger_recon 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零生产路径：CH 索引以样本注入、台账读写一律 tmp_path；
#   红样=蒸发态（CH 有台账无）/重复/id 与假说不符，绿样=两集相等或台账多出未审行
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-231 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1 台账对账/蒸发重建单测——红样=蒸发态与占坑态，全部 tmp_path + 注入 CH 样本。"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from scripts.backtest import intake_ledger_recon as recon

HEADER = [
    "candidate_id",
    "theme",
    "hypothesis_zh",
    "mechanism_hint",
    "horizon",
    "universe",
    "birth_channel",
    "birth_batch",
    "birth_source",
]


def cand_id(text: str) -> str:
    """与车道 B 同源的内容寻址 id（CAND-md5_12("E1B:"+全文)）。"""
    return f"CAND-{hashlib.md5(f'E1B:{text.strip()}'.encode()).hexdigest()[:12]}"


def row(text: str, *, batch: str = "E1B-20260914-053418", cid: str | None = None) -> dict:
    return {
        "candidate_id": cid or cand_id(text),
        "theme": "动量",
        "hypothesis_zh": text,
        "mechanism_hint": "机制",
        "horizon": "5日",
        "universe": "沪深300",
        "birth_channel": "B",
        "birth_batch": batch,
        "birth_source": "llm:qwen3:8b",
    }


def ch_row(text: str, *, batch: str = "E1B-20260916-021130", cid: str | None = None) -> dict:
    return {
        "candidate_id": cid or cand_id(text),
        "birth_channel": "B",
        "birth_batch": batch,
        "hypothesis_zh": text,
    }


def write_ledger(tmp_path: Path, rows: list[dict], *, name: str = "lane_b_candidates.csv") -> Path:
    pd.DataFrame(rows, columns=HEADER).to_csv(tmp_path / name, index=False, lineterminator="\n")
    return tmp_path / name


class TestReconcile:
    def test_evaporated_rows_are_drift(self, tmp_path):
        """红样（F16 事故态复现）：CH 已审 3 条、台账只剩 2 条 → drift + 报出缺失 id。"""
        write_ledger(tmp_path, [row("甲"), row("乙")])
        index = [ch_row("甲"), ch_row("乙"), ch_row("丙")]
        report = recon.reconcile_one("lane_b_candidates.csv", index, intake_dir=tmp_path)
        assert report["status"] == recon.STATUS_DRIFT
        assert report["missing_in_csv"] == [cand_id("丙")]
        assert report["ch_unique_ids"] == 3 and report["csv_unique_ids"] == 2

    def test_matched_ledger_is_ok(self, tmp_path):
        write_ledger(tmp_path, [row("甲"), row("乙")])
        index = [ch_row("甲", batch="E1B-1"), ch_row("乙", batch="E1B-2")]
        report = recon.reconcile_one("lane_b_candidates.csv", index, intake_dir=tmp_path)
        assert report["status"] == recon.STATUS_OK
        assert report["missing_in_csv"] == []

    def test_unexamined_rows_are_not_drift(self, tmp_path):
        """台账多出 CH 未审行=正常在途态（missing_in_ch），不得判事故。"""
        write_ledger(tmp_path, [row("甲"), row("乙"), row("丁")])
        report = recon.reconcile_one("lane_b_candidates.csv", [ch_row("甲"), ch_row("乙")], intake_dir=tmp_path)
        assert report["status"] == recon.STATUS_OK
        assert report["missing_in_ch"] == [cand_id("丁")]

    def test_dup_and_integrity_failures_surface(self, tmp_path):
        write_ledger(tmp_path, [row("甲"), row("甲"), row("乙", cid="CAND-badsign00000")])
        report = recon.reconcile_one(
            "lane_b_candidates.csv", [ch_row("甲"), ch_row("乙", cid="CAND-badsign00000")], intake_dir=tmp_path
        )
        assert report["status"] == recon.STATUS_DRIFT
        assert report["dup_ids"] == [cand_id("甲")]
        assert report["id_integrity_failures"] == ["CAND-badsign00000"]

    def test_missing_ledger_file_is_drift_not_silence(self, tmp_path):
        report = recon.reconcile_one("lane_b_candidates.csv", [ch_row("甲")], intake_dir=tmp_path)
        assert report["status"] == recon.STATUS_DRIFT

    def test_check_all_unknown_ledger_raises(self, tmp_path):
        with pytest.raises(RuntimeError, match="未知台账"):
            recon.check_all(["not_a_ledger.csv"], ch_index=[], intake_dir=tmp_path)

    def test_check_all_probe_failure_is_loud_red(self, tmp_path, monkeypatch):
        """CH 不可达必须报 probe_failed——禁静默归零后自称全绿。"""

        def boom(channels=None):
            raise RuntimeError("clickhouse down")

        monkeypatch.setattr(recon, "fetch_ch_index", boom)
        report = recon.check_all(["lane_b_candidates.csv"])
        assert report["status"] == recon.STATUS_PROBE_FAILED
        assert "clickhouse down" in report["error"]
        assert report["ledgers"] == []

    def test_preflight_reports_drift_and_skips_unknown_ledgers(self, tmp_path):
        write_ledger(tmp_path, [row("甲")])
        index = [ch_row("甲"), ch_row("戊")]
        out = recon.preflight("data/strategy_intake/lane_b_candidates.csv", intake_dir=tmp_path, ch_index=index)
        assert out["status"] == recon.STATUS_DRIFT
        assert out["missing_in_csv"] == 1
        assert out["detail"]["missing_in_csv"] == [cand_id("戊")]
        unknown = recon.preflight("some_other_source.csv", intake_dir=tmp_path)
        assert unknown["status"] == recon.STATUS_UNKNOWN_LEDGER
        absent = recon.preflight("lane_c2_candidates.csv", intake_dir=tmp_path)
        assert absent["status"] == recon.STATUS_LEDGER_ABSENT

    def test_preflight_probe_failure_never_raises_to_e2(self, tmp_path, monkeypatch):
        """E2 前置 fail-open：探针炸了对账器只报状态，不把异常抛进预审主链。"""

        def boom(channels=None):
            raise RuntimeError("connection refused")

        monkeypatch.setattr(recon, "fetch_ch_index", boom)
        write_ledger(tmp_path, [row("甲")])
        out = recon.preflight("lane_b_candidates.csv", intake_dir=tmp_path)
        assert out["status"] == recon.STATUS_PROBE_FAILED


class TestRebuild:
    def test_plan_refuses_content_address_mismatch(self, tmp_path):
        """CH 行 id 与假说原文不符=不可信行，拒绝入账并单独报出（不写坏台账）。"""
        write_ledger(tmp_path, [row("甲")])
        index = [ch_row("乙", cid="CAND-forged000000")]
        plan = recon.plan_rebuild("lane_b_candidates.csv", index, intake_dir=tmp_path)
        assert plan["rows"] == []
        assert plan["refused"][0]["candidate_id"] == "CAND-forged000000"

    def test_plan_declares_unrecoverable_columns(self, tmp_path):
        write_ledger(tmp_path, [row("甲")])
        plan = recon.plan_rebuild("lane_b_candidates.csv", [ch_row("乙")], intake_dir=tmp_path)
        assert set(plan["unrecoverable_columns"]) == {"theme", "mechanism_hint", "horizon", "universe", "birth_source"}

    def test_dry_run_writes_nothing(self, tmp_path):
        path = write_ledger(tmp_path, [row("甲")])
        before = path.read_bytes()
        result = recon.rebuild_missing(
            "lane_b_candidates.csv", apply=False, ch_index=[ch_row("乙")], intake_dir=tmp_path
        )
        assert result["applied"] is False
        assert result["rebuilt"] == [cand_id("乙")]
        assert path.read_bytes() == before

    def test_apply_appends_and_preserves_existing_rows(self, tmp_path):
        """只追加：既有行字节原样保留，重建行补齐出生证，不可恢复列如实留空。"""
        path = write_ledger(tmp_path, [row("甲")])
        before = path.read_text(encoding="utf-8")
        result = recon.rebuild_missing(
            "lane_b_candidates.csv", apply=True, ch_index=[ch_row("乙"), ch_row("丙")], intake_dir=tmp_path
        )
        assert result["applied"] is True and result["written_rows"] == 2
        after = path.read_text(encoding="utf-8")
        assert after.startswith(before)
        df = pd.read_csv(path, encoding="utf-8-sig")
        assert list(df["candidate_id"]) == [cand_id("甲"), cand_id("乙"), cand_id("丙")]
        assert df["hypothesis_zh"].tolist()[1:] == ["乙", "丙"]
        assert df["theme"].iloc[1:].isna().all()  # CH 不携带列如实留空（禁编造）
        assert df["birth_channel"].tolist() == ["B", "B", "B"]

    def test_rebuild_is_idempotent(self, tmp_path):
        write_ledger(tmp_path, [row("甲")])
        index = [ch_row("乙"), ch_row("丙")]
        first = recon.rebuild_missing("lane_b_candidates.csv", apply=True, ch_index=index, intake_dir=tmp_path)
        second = recon.rebuild_missing("lane_b_candidates.csv", apply=True, ch_index=index, intake_dir=tmp_path)
        assert first["written_rows"] == 2
        assert second["rebuilt"] == [] and second["applied"] is False
        assert len(pd.read_csv(tmp_path / "lane_b_candidates.csv", encoding="utf-8-sig")) == 3

    def test_rebuild_after_apply_clears_drift(self, tmp_path):
        write_ledger(tmp_path, [row("甲")])
        index = [ch_row("甲"), ch_row("乙")]
        assert recon.reconcile_one("lane_b_candidates.csv", index, intake_dir=tmp_path)["status"] == recon.STATUS_DRIFT
        recon.rebuild_missing("lane_b_candidates.csv", apply=True, ch_index=index, intake_dir=tmp_path)
        assert recon.reconcile_one("lane_b_candidates.csv", index, intake_dir=tmp_path)["status"] == recon.STATUS_OK

    def test_birth_batch_filter_scopes_rebuild(self, tmp_path):
        write_ledger(tmp_path, [row("甲")])
        index = [ch_row("乙", batch="E1B-20260916-021130"), ch_row("丙", batch="E1B-20260917-000000")]
        result = recon.rebuild_missing(
            "lane_b_candidates.csv", "E1B-20260916-021130", apply=True, ch_index=index, intake_dir=tmp_path
        )
        assert result["rebuilt"] == [cand_id("乙")]

    def test_append_goes_through_cas_channel(self, tmp_path, monkeypatch):
        """写盘必经 safe_write_text（根宪法 §1 条目13）——绕开 CAS 即红。"""
        seen = {}

        def fake_safe_write_text(path, content, **kw):
            seen["kwargs"] = kw
            seen["content"] = content

            class _R:
                before_sha256 = "before"
                after_sha256 = "after"

            Path(path).write_text(content, encoding="utf-8", newline="")
            return _R()

        import zephyr.shared.io.file_utils as fu

        monkeypatch.setattr(fu, "safe_write_text", fake_safe_write_text)
        path = write_ledger(tmp_path, [row("甲")])
        out = recon.append_ledger_rows(path, [row("乙")], HEADER)
        assert "expected_base_sha256" in seen["kwargs"]
        assert out["before_sha256"] == "before" and out["after_sha256"] == "after"
        assert out["rows"] == 1

    def test_stale_base_refused_propagates(self, tmp_path, monkeypatch):
        """CAS base 漂移=拒写上抛，绝不静默覆盖。"""
        from zephyr.shared.io.file_utils import StaleWriteRefused

        def refuse(*a, **kw):
            raise StaleWriteRefused("base 漂移")

        import zephyr.shared.io.file_utils as fu

        monkeypatch.setattr(fu, "safe_write_text", refuse)
        path = write_ledger(tmp_path, [row("甲")])
        with pytest.raises(StaleWriteRefused):
            recon.append_ledger_rows(path, [row("乙")], HEADER)


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
