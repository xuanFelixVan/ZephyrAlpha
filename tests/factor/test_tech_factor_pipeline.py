# [TESTS] tests/factor/test_tech_factor_pipeline.py
# [TTL] permanent
# CNS-01 计算链单测——monkeypatch read_indicator，测试隔离铁律（零 DB/CH 触达）。

import pandas as pd
import pytest

from zephyr.factor.analysis import tech_factor_pipeline as tfp


def _fake_frame(rows=5, drop_col=None):
    data = {c: [float(i + 1) * (j + 1) for i in range(rows)] for j, c in enumerate(tfp.DEFAULT_TECH_COLUMNS)}
    df = pd.DataFrame(data)
    df["trade_date"] = [f"2026-10-0{i + 1}" for i in range(rows)]
    df["trade_time"] = ""
    df["symbol"] = "000852"
    df["period"] = "daily"
    if drop_col:
        df = df.drop(columns=[drop_col])
    return df


class TestBuildPanel:
    def test_panel_from_wide_table(self, monkeypatch):
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: _fake_frame())
        panel = tfp.build_tech_factor_values("000852")
        assert set(panel.keys()) == set(tfp.DEFAULT_TECH_COLUMNS)
        assert all(isinstance(v, pd.Series) and len(v) == 5 for v in panel.values())

    def test_empty_table_returns_empty_dict(self, monkeypatch):
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: pd.DataFrame(columns=["trade_date", "symbol"]))
        assert tfp.build_tech_factor_values("000852") == {}

    def test_missing_column_fail_closed(self, monkeypatch):
        # 读层返回缺列（白名单漂移模拟）→ fail-closed
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: _fake_frame(drop_col="rsi_6"))
        with pytest.raises(ValueError, match="rsi_6"):
            tfp.build_tech_factor_values("000852")

    def test_empty_columns_rejected(self, monkeypatch):
        with pytest.raises(ValueError, match="不能为空"):
            tfp.build_tech_factor_values("000852", columns=())

    def test_all_nan_column_dropped(self, monkeypatch):
        df = _fake_frame()
        df["bias_6"] = float("nan")
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: df)
        panel = tfp.build_tech_factor_values("000852")
        assert "bias_6" not in panel  # 全 NaN 预热列不进面板


class TestSynthesizeChain:
    def test_equal_weight_chain(self, monkeypatch):
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: _fake_frame())
        sig = tfp.synthesize_tech_signal("000852", method="equal_weight")
        assert isinstance(sig, pd.Series) and len(sig) == 5

    def test_default_method_from_config(self, monkeypatch):
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: _fake_frame())
        sig = tfp.synthesize_tech_signal("000852")  # method=None → 配置默认
        assert isinstance(sig, pd.Series)

    def test_empty_chain_no_signal(self, monkeypatch):
        monkeypatch.setattr(tfp, "read_indicator", lambda **kw: pd.DataFrame(columns=["trade_date"]))
        sig = tfp.synthesize_tech_signal("000852")
        assert sig.empty  # 不造信号

    def test_illegal_method_fail_closed(self):
        with pytest.raises(ValueError, match="非法 method"):
            tfp.synthesize_tech_signal("000852", method="magic")

    def test_pit_passthrough(self, monkeypatch):
        # PIT 语义透传：end>as_of 由 read_indicator 硬拒（此处验证参数原样透传）
        captured = {}

        def fake_read(**kw):
            captured.update(kw)
            return _fake_frame()

        monkeypatch.setattr(tfp, "read_indicator", fake_read)
        tfp.build_tech_factor_values("000852", start="2026-09-01", end="2026-09-30", as_of="2026-09-30")
        assert captured["start"] == "2026-09-01" and captured["as_of"] == "2026-09-30"
