# [BLUEPRINT] MOD-BT-COND-PACKAGE-TEST | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_condition_package
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas; zephyr.backtest.regime_validation.condition_package
# [CONSUMERS] CI（MODIFY-GUARD 契约钉：tests/backtest/test_condition_package.py）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试隔离：零生产路径写入，落盘一律 tmp_path fixture；红蓝口径=灰度边界逐点+地板下沉+选族守卫+roundtrip 位面一致；禁"全绿"断言，逐条如实
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试红
# [TESTS] self
# [TTL] permanent
# [A_module] module_id=MOD-BT-COND-PACKAGE-TEST | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""条件轴输入包契约钉（MOD-BT-COND-PACKAGE）。

红证口径：灰度五档边界、>5 态 fail-closed、30 日地板下沉、save/load roundtrip、
F4 选族过滤（load 路径 monkeypatch ch_reader）。
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.backtest.regime_validation import condition_package as cp


class TestGreyBand:
    def test_band5_boundaries_frozen(self):
        assert cp.grey_band(0.0) == "ice"
        assert cp.grey_band(0.2) == "ice"  # ≤0.2 含边界
        assert cp.grey_band(0.21) == "cooling"
        assert cp.grey_band(0.4) == "cooling"
        assert cp.grey_band(0.6) == "mild"
        assert cp.grey_band(0.8) == "warming"
        assert cp.grey_band(0.81) == "boiling"
        assert cp.grey_band(1.0) == "boiling"

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError, match="越界"):
            cp.grey_band(-0.01)
        with pytest.raises(ValueError, match="越界"):
            cp.grey_band(1.01)


def _panel(rows: list[tuple[str, float, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["date", "value", "state"]).assign(date=lambda d: pd.to_datetime(d["date"]))


class TestBuildConditionPack:
    def test_floor_sink_and_cells(self):
        # 4 bands × 1 state；boiling 胞仅 2 日 <30 → 下沉
        rows = [(f"2025-01-{i:02d}", 0.3, "neutral") for i in range(1, 29)]  # cooling 28 日 <30
        rows += [(f"2025-02-{i:02d}", 0.5, "neutral") for i in range(1, 29)]  # mild 28 日 <30
        rows += [(f"2025-03-{i:02d}", 0.7, "neutral") for i in range(1, 32)]  # warming 31 日 达标
        rows += [("2025-03-30", 0.9, "neutral"), ("2025-03-31", 0.95, "neutral")]  # boiling 2 日
        pack = cp.build_condition_pack(_panel(rows))
        assert set(pack.cells["cell_id"]) == {
            "gmild|sneutral",
            "gcooling|sneutral",
            "gwarming|sneutral",
            "gboiling|sneutral",
        }
        elig = pack.eligible_cells()
        assert elig == ["gwarming|sneutral"]
        # 未达标日期下沉：cell_id 为空但行保留（标注层不丢行）
        sub = pack.frame[pack.frame["grey_band"] == "boiling"]
        assert sub["cell_eligible"].all() is False or (~sub["cell_eligible"]).all()
        assert sub["cell_id"].isna().all()
        assert pack.provenance["cells_eligible"] == 1

    def test_dropped_bands_recorded(self):
        rows = [(f"2025-01-{i:02d}", 0.5, "neutral") for i in range(1, 32)]
        pack = cp.build_condition_pack(_panel(rows))
        assert "ice" in pack.dropped_bands and "boiling" in pack.dropped_bands

    def test_over_five_states_fail_closed(self):
        rows = [(f"2025-01-{i:02d}", 0.5, f"s{i % 6}") for i in range(1, 32)]
        with pytest.raises(ValueError, match="映射册"):
            cp.build_condition_pack(_panel(rows))


class TestRoundtrip:
    def test_save_load_preserves_cells(self, tmp_path):
        rows = [(f"2025-01-{i:02d}", 0.5, "neutral") for i in range(1, 32)]
        pack = cp.build_condition_pack(_panel(rows))
        fp = cp.save_pack(pack, tmp_path)
        assert fp.exists()
        back = cp.load_pack(tmp_path)
        pd.testing.assert_frame_equal(back.frame, pack.frame)
        assert back.eligible_cells() == pack.eligible_cells()
        assert back.provenance["cells_total"] == pack.provenance["cells_total"]

    def test_lookup_and_keyerror(self):
        rows = [(f"2025-01-{i:02d}", 0.5, "neutral") for i in range(1, 32)]
        pack = cp.build_condition_pack(_panel(rows))
        assert pack.lookup("2025-01-15")[0] == "mild"
        with pytest.raises(KeyError):
            pack.lookup("2030-01-01")


class TestLoadPath:
    def test_family_filter_and_merge(self, monkeypatch):
        emo_tsv = "\n".join([f"2025-01-{i:02d}\t0.55" for i in range(1, 32)])
        st_tsv = "\n".join([f"2025-01-{i:02d}\trisk_on" for i in range(1, 32)])
        captured: list[str] = []

        def fake_query(sql: str, timeout: int = 30) -> str:
            captured.append(sql)
            return st_tsv if "alt_regime_signal" in sql else emo_tsv

        monkeypatch.setattr(cp.ch_reader, "query", fake_query)
        pack = cp.load_condition_pack()
        assert any("F4_BDI_MOMENTUM_Z20" in s for s in captured), "状态查询必须按 F4 族过滤"
        assert pack.states == ("risk_on",)
        assert len(pack.frame) == 31

    def test_empty_axis_raises(self, monkeypatch):
        monkeypatch.setattr(cp.ch_reader, "query", lambda sql, timeout=30: "")
        with pytest.raises(RuntimeError, match="空结果"):
            cp.load_condition_pack()
