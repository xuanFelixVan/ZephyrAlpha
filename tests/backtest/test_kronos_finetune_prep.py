# [BLUEPRINT] MOD-BT-204 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_kronos_finetune_prep
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas; scripts.backtest.kronos_finetune_prep
# [CONSUMERS] MOD-BT-204 kronos_finetune_prep 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络（mock CH Client）；输出仅落 tmp_path；CSV=官方七列规范
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-204 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Kronos 微调数据管线单测——格式校验/清洗切分/启动命令内容，mock CH 零网络。"""
from __future__ import annotations

import pytest

import scripts.backtest.kronos_finetune_prep as kfp

OFFICIAL_COLS = ["timestamps", "open", "high", "low",
                 "close", "volume", "amount"]

_ROWS = [
    # trade_date, symbol, open, high, low, close, volume, amount
    ("2026-01-05", "SH600000", 10.0, 10.5, 9.8, 10.2, 1000, 10200.0),
    ("2026-01-06", "SH600000", 10.2, 10.6, 10.1, 10.4, 1100, 11440.0),
    ("2026-01-07", "SH600000", 10.4, 10.7, 10.0, 10.1, 1200, 12120.0),
    ("2026-01-05", "SZ000001", 20.0, 20.8, 19.9, 20.5, 800, 16400.0),
    ("2026-01-06", "SZ000001", 20.5, 20.9, 20.2, 20.3, 900, 18270.0),
    ("2026-01-06", "SZ000001", 20.5, 21.0, 20.2, 20.6, 950, 19570.0),  # 重复日→keep last
    ("2026-01-07", "SZ000001", 20.6, 20.7, 20.0, None, 700, 14000.0),  # close 空→dropna
]


class _FakeClient:
    """mock clickhouse_driver.Client：按 params 形状区分 top-n 查询与 K 线查询。"""

    def __init__(self, **kwargs):
        assert kwargs.get("host") == "fake-host"

    def execute(self, query, params):
        if "syms" in params:
            assert set(params["syms"]) <= {"SH600000", "SZ000001"}
            return [r for r in _ROWS if r[1] in params["syms"]]
        assert "n" in params
        return [("SH600000",), ("SZ000001",)]


@pytest.fixture()
def ch_env(monkeypatch, tmp_path):
    import zephyr.data.ch_config as chc
    monkeypatch.setattr(chc, "ensure_ch_env_loaded", lambda: None)
    monkeypatch.setattr(chc, "load_ch_reader_config",
                        lambda: {"host": "fake-host", "port": 9000,
                                 "user": "u", "password": "p"})
    monkeypatch.setattr("clickhouse_driver.Client", _FakeClient)
    data_dir = tmp_path / "kronos_ft"
    monkeypatch.setattr(kfp, "_DATA_DIR", data_dir)
    return data_dir


class TestFetchKlines:
    def test_columns_official_spec(self, ch_env):
        panels = kfp.fetch_klines(["SH600000", "SZ000001"], days=500)
        for sym, df in panels.items():
            assert list(df.columns) == OFFICIAL_COLS

    def test_split_by_symbol_and_dedup_keep_last(self, ch_env):
        panels = kfp.fetch_klines(["SH600000", "SZ000001"], days=500)
        assert set(panels) == {"SH600000", "SZ000001"}
        assert len(panels["SH600000"]) == 3  # 3 天无重复无缺失
        assert len(panels["SZ000001"]) == 2  # 重复日合并 + 缺失行剔除
        sz = panels["SZ000001"]
        assert sz.loc[sz["timestamps"] == "2026-01-06", "close"].item() == 20.6

    def test_numeric_coercion(self, ch_env):
        panels = kfp.fetch_klines(["SH600000"], days=500)
        df = panels["SH600000"]
        for c in OFFICIAL_COLS[1:]:
            assert df[c].dtype.kind in ("f", "i")


class TestRunPrep:
    def test_writes_official_csv_and_record(self, ch_env):
        rec = kfp.run_prep(top_n=2, days=500)
        assert rec["top_n"] == 2
        assert str(ch_env) == rec["data_dir"]
        assert len(rec["files"]) == 2
        for f in rec["files"]:
            p = ch_env / f["file"].replace("\\", "/").split("/")[-1]
            assert p.exists()
            header = p.read_text(encoding="utf-8").splitlines()[0]
            assert header == ",".join(OFFICIAL_COLS)

    def test_launch_cmd_content(self, ch_env):
        rec = kfp.run_prep(top_n=2, days=500)
        assert "finetune" in rec["launch_cmd"]
        assert "--epochs 10" in rec["launch_cmd"]
        assert "--device cuda" in rec["launch_cmd"]
        assert str(ch_env) in rec["launch_cmd"]

    def test_split_note_declares_temporal_80_20(self, ch_env):
        rec = kfp.run_prep(top_n=2, days=500)
        assert "80/20" in rec["train_val_split"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
