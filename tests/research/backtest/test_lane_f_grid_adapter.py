# [BLUEPRINT] MOD-BT-E1F-001 | docs/03_modules/_domain_backtest/blueprint.md | §FAC-E1 车道F
# [MODULE] tests.backtest.test_lane_f_grid_adapter
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas
# [CONSUMERS] MOD-BT-E1F-001 lane_f_grid_adapter 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM 零生产路径：manifest 夹具=grid_20260925-232032 真实样本行，
#   台账读写一律 tmp_path 注入；只验确定性转换/幂等卸货/诚实降级标注，不触真实 CH/Ollama
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-E1F-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1F 车道F 适配器单测——真实 manifest 样本夹具：转换映射/确定性/幂等/诚实降级。"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from scripts.backtest import factory_intake_pipeline as fip
from scripts.backtest import lane_f_grid_adapter as adapter

# 真实夹具：data/strategy_intake/grid_20260925-232032/manifest.csv 表头+前 2 行（逐字未改）
HEADER = "recipe_id,prefix_key,degraded_dimensions,sharpe,ann_return,max_drawdown,avg_turnover,net_days,values_json"
ROW1 = (
    '0caa81205873,"{""A1_factor_normalize"":""industsize_neutral"",""A2_combine_weight"":""equal"",'
    '""B_top_n"":""top20"",""G_universe"":""zz500""}",(),0.108,-0.0109,-0.566,0.037,1622,'
    '"{""A1_factor_normalize"": ""industsize_neutral"", ""A2_combine_weight"": ""equal"", '
    '""B_top_n"": ""top20"", ""C_sizing"": ""kelly_025"", ""D1_rebalance_freq"": ""daily"", '
    '""D2_rebalance_trigger"": ""periodic"", ""E_single_cap"": ""cap5"", ""F_merge_policy"": ""single"", '
    '""G_universe"": ""zz500"", ""H_turnover_lambda"": ""lambda_5bp"", ""I_cost_tier"": ""frozen_l0"", '
    '""J_regime_switch"": false, ""K_capital_ramp"": ""lump""}"'
)
ROW2 = (
    '612ec71a7762,"{""A1_factor_normalize"":""size_neutral"",""A2_combine_weight"":""halflife60"",'
    '""B_top_n"":""top50"",""G_universe"":""zz500""}",(),0.143,0.0099,-0.338,0.0236,1622,'
    '"{""A1_factor_normalize"": ""size_neutral"", ""A2_combine_weight"": ""halflife60"", '
    '""B_top_n"": ""top50"", ""C_sizing"": ""kelly_050"", ""D1_rebalance_freq"": ""monthly"", '
    '""D2_rebalance_trigger"": ""periodic"", ""E_single_cap"": ""cap5"", ""F_merge_policy"": ""single"", '
    '""G_universe"": ""zz500"", ""H_turnover_lambda"": ""lambda_5bp"", ""I_cost_tier"": ""frozen_l0"", '
    '""J_regime_switch"": false, ""K_capital_ramp"": ""lump""}"'
)


def _make_batch(tmp_path: Path, name: str, data_lines: list[str]) -> Path:
    d = tmp_path / name
    d.mkdir(parents=True, exist_ok=True)
    lines = [HEADER, *data_lines]
    (d / "manifest.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d / "manifest.csv"


@pytest.fixture()
def manifest2(tmp_path: Path) -> Path:
    return _make_batch(tmp_path, "grid_20260925-232032", [ROW1, ROW2])


class TestConvertManifest:
    def test_maps_e2_contract_columns(self, manifest2: Path):
        rows, rep = adapter.convert_manifest(manifest2, axis_descs={})
        assert rep["converted"] == 2 and rep["rows_in_manifest"] == 2
        need = {"candidate_id", "hypothesis_zh", "birth_channel", "birth_batch"}
        assert need <= set(rows[0])  # E2 台账四列契约
        by_id = {r["recipe_id"]: r for r in rows}
        r1 = by_id["0caa81205873"]
        assert r1["candidate_id"] == "F06-0caa81205873"
        assert r1["birth_channel"] == "F"
        assert r1["birth_batch"] == "E1F-grid_20260925-232032"
        assert float(r1["sharpe"]) == pytest.approx(0.108)
        assert int(r1["net_days"]) == 1622
        assert "grid_20260925-232032" in r1["birth_source"]
        # values_json 原样携带（E3/归因端可回溯全参数）
        assert "kelly_025" in r1["values_json"]

    def test_hypothesis_deterministic_and_honest(self, manifest2: Path):
        rows_a, _ = adapter.convert_manifest(manifest2, axis_descs={})
        rows_b, _ = adapter.convert_manifest(manifest2, axis_descs={})
        assert [r["hypothesis_zh"] for r in rows_a] == [r["hypothesis_zh"] for r in rows_b]
        h = rows_a[0]["hypothesis_zh"]
        assert "recipe_id=0caa81205873" in h  # 出处可溯
        assert "grid_20260925-232032" in h
        assert "A1_factor_normalize=industsize_neutral" in h  # 参数轴如实
        assert "sharpe=0.108" in h  # 指标观察如实
        assert "不编造机制" in h and "机制字段缺失" in h  # 诚实降级标注（禁编造）

    def test_axis_desc_from_schema_source(self, manifest2: Path):
        rows, _ = adapter.convert_manifest(manifest2)  # 缺省=读真源 schema YAML
        h = rows[0]["hypothesis_zh"]
        assert "A1_factor_normalize[因子标准化]=" in h  # desc 来自 position_recipe_grid_schema.yaml
        rows_raw, _ = adapter.convert_manifest(manifest2, axis_descs={})  # 注入空表=降级裸轴 id
        assert "A1_factor_normalize=industsize_neutral" in rows_raw[0]["hypothesis_zh"]
        assert "[" not in rows_raw[0]["hypothesis_zh"].split("。")[1]  # 不造词

    def test_malformed_row_skipped_not_fatal(self, tmp_path: Path):
        bad = (
            'deadbeefcafe,"{}","",0.1,0.02,-0.1,0.01,100,"{broken json"',  # values_json 损坏
        )
        m = _make_batch(tmp_path, "grid_20260926-000000", [ROW1, *bad])
        rows, rep = adapter.convert_manifest(m, axis_descs={})
        assert rep["converted"] == 1 and len(rep["skipped_malformed"]) == 1
        assert rows[0]["recipe_id"] == "0caa81205873"

    def test_empty_manifest_converts_zero(self, tmp_path: Path):
        m = _make_batch(tmp_path, "grid_20260929-040141", [])
        rows, rep = adapter.convert_manifest(m, axis_descs={})
        assert rows == [] and rep["converted"] == 0 and rep["rows_in_manifest"] == 0


class TestRunIntake:
    def test_write_then_idempotent_rerun(self, manifest2: Path, tmp_path: Path):
        ledger = tmp_path / "lane_f_candidates.csv"
        first = adapter.run_intake(manifest=manifest2, intake_csv=ledger)
        assert first["written"] == 2 and first["status"] == "ok"
        assert ledger.exists()
        df1 = pd.read_csv(ledger, encoding="utf-8-sig")
        assert len(df1) == 2
        # 同 recipe 重复消费跳过（幂等），台账不被重复追加
        second = adapter.run_intake(manifest=manifest2, intake_csv=ledger)
        assert second["written"] == 0 and second["skipped_existing"] == 2
        assert second["status"] == "no_new"
        df2 = pd.read_csv(ledger, encoding="utf-8-sig")
        assert len(df2) == 2 and list(df2["candidate_id"]) == list(df1["candidate_id"])

    def test_dry_run_writes_nothing(self, manifest2: Path, tmp_path: Path):
        ledger = tmp_path / "lane_f_candidates.csv"
        rec = adapter.run_intake(manifest=manifest2, intake_csv=ledger, dry_run=True)
        assert rec["converted"] == 2 and rec["written"] == 0 and rec["dry_run"] is True
        assert not ledger.exists()

    def test_empty_manifest_no_ledger_created(self, tmp_path: Path):
        m = _make_batch(tmp_path, "grid_20260929-040141", [])
        ledger = tmp_path / "lane_f_candidates.csv"
        rec = adapter.run_intake(manifest=m, intake_csv=ledger)
        assert rec["status"] == "empty_manifest" and rec["written"] == 0
        assert not ledger.exists()  # 空批不落空文件（诚实缺）

    def test_missing_batch_honest_no_batch(self, tmp_path: Path):
        rec = adapter.run_intake(manifest=tmp_path / "grid_none" / "manifest.csv", intake_csv=tmp_path / "x.csv")
        assert rec["status"] == "no_batch"
        assert adapter.latest_manifest(base=tmp_path) is None

    def test_corrupt_ledger_fails_closed(self, manifest2: Path, tmp_path: Path):
        ledger = tmp_path / "lane_f_candidates.csv"
        ledger.write_text("not,a,ledger\n1,2\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="不可读"):
            adapter.run_intake(manifest=manifest2, intake_csv=ledger)

    def test_latest_manifest_picks_newest_batch(self, tmp_path: Path):
        _make_batch(tmp_path, "grid_20260925-232032", [ROW1])
        newest = _make_batch(tmp_path, "grid_20260926-024947", [ROW2])
        assert adapter.latest_manifest(base=tmp_path) == newest


class TestPipelineWiring:
    def test_lane_specs_f_points_at_adapter_ledger(self):
        spec = next(s for s in fip._LANE_SPECS if s["lane"] == "F")
        assert spec["intake"] == "data/strategy_intake/lane_f_candidates.csv"
        assert Path(adapter._INTAKE_CSV).name == "lane_f_candidates.csv"

    def test_f_lane_in_compute_gate_results(self):
        lanes = {r["lane"] for r in fip.preflight_compute_gate()}
        assert "F" in lanes

    def test_ledger_passes_e2_reader_contract(self, manifest2: Path, tmp_path: Path):
        """端到端契约：适配器卸的台账能被 hypothesis_precheck.load_candidates 读取。"""
        from scripts.backtest import hypothesis_precheck

        ledger = tmp_path / "lane_f_candidates.csv"
        adapter.run_intake(manifest=manifest2, intake_csv=ledger)
        df = hypothesis_precheck.load_candidates(str(ledger))
        assert len(df) == 2
        assert set(df["birth_channel"]) == {"F"}
        assert df["hypothesis_zh"].str.contains("不编造机制").all()
        # 幂等键进 E2 选择器：已审 id 被剔除
        done = {str(df.iloc[0]["candidate_id"])}
        pending = hypothesis_precheck.select_pending(df, done)
        assert len(pending) == 1 and str(pending.iloc[0]["candidate_id"]) not in done

    def test_values_json_roundtrip_in_ledger(self, manifest2: Path, tmp_path: Path):
        ledger = tmp_path / "lane_f_candidates.csv"
        adapter.run_intake(manifest=manifest2, intake_csv=ledger)
        df = pd.read_csv(ledger, encoding="utf-8-sig")
        values = json.loads(df.iloc[0]["values_json"])
        assert values["G_universe"] == "zz500"  # 全参数可回溯（E3 构造端依赖）
