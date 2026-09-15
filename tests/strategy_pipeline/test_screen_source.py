# [BLUEPRINT] MOD-BT-191 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_screen_source
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.screen_source
# [CONSUMERS] MOD-BT-191 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零生产 IO（CH 查询/翻译件加载全 monkeypatch）；纯函数直测
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/screen_source.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-191 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""screen_source 测试——p 值/三轴启发式/bothwin 口径/ρ 矩阵（验收⑥回放的数据底座）。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline import screen_source as ss  # noqa: E402


class TestPureFunctions:
    def test_p_from_sharpe_monotone(self):
        p_high = ss.p_from_sharpe(2.0, 977)
        p_mid = ss.p_from_sharpe(1.0, 977)
        p_low = ss.p_from_sharpe(0.07, 977)
        assert p_high < p_mid < p_low <= 1.0
        assert ss.p_from_sharpe(1.0, 977) == pytest.approx(math.erfc(1.0 * math.sqrt(977 / 252) / math.sqrt(2)))
        assert ss.p_from_sharpe(None, 977) == 1.0 and ss.p_from_sharpe(1.0, 0) == 1.0

    def test_derive_class_keywords(self, tmp_path, monkeypatch):
        f = tmp_path / "c4_abc_bias_ql.py"
        f.write_text("# BIAS 乖离率 超卖回归", encoding="utf-8")
        monkeypatch.setattr(ss, "ROOT", tmp_path)
        assert ss.derive_class("c4_abc_bias_ql.py") == "value_reversal"

    def test_derive_class_fallback_multifactor(self, tmp_path, monkeypatch):
        f = tmp_path / "c4_abcdef01_mystery.py"
        f.write_text("# 完全无关关键词", encoding="utf-8")
        monkeypatch.setattr(ss, "ROOT", tmp_path)
        assert ss.derive_class("c4_abcdef01_mystery.py") == "multifactor"

    def test_derive_name_strips_hash(self):
        assert ss.derive_name("scripts/backtest/translated/c4_c72318f2da1c_bias_ql.py") == "bias_ql"
        assert ss.derive_name("scripts/backtest/translated/c4_weird.py") == "c4_weird"

    def test_family_of(self):
        assert ss.family_of("value_reversal") == "VREV"
        assert ss.family_of("multifactor") == "MULTIFACTOR"
        # 2026-09-15 家族法对齐：词表外类（含 daban 等未入 _CLASS_FAMILY 者）缺省 AUTO
        assert ss.family_of("daban") == "AUTO"
        assert ss.family_of("mystery_class") == "AUTO"

    def test_derive_axes_turnover_split(self):
        a = ss.derive_axes("c4_abcdef01_gap_hi.py", turnover=1.5)
        b = ss.derive_axes("c4_abcdef01_gap_hi.py", turnover=0.3)
        assert a["holding_period"] == "日内—次日" and b["holding_period"] == "波段"
        assert a["signal_axis"] == b["signal_axis"] == "daban"


class TestBothwin:
    def _fake_q(self, monkeypatch, is_rows, oos_rows):
        def fake_q(sql):
            if "oos_tested" in sql:
                return oos_rows
            return is_rows
        monkeypatch.setattr(ss, "_q", fake_q)
        monkeypatch.setattr(ss, "_decay_suspect", lambda: 0.5)

    def test_fetch_bothwin_gate_semantics(self, monkeypatch):
        is_rows = [
            ("CAND-good", 1.0, "scripts/backtest/translated/c4_good.py", 0.2, "n", -0.3),
            ("CAND-negoos", 1.0, "scripts/backtest/translated/c4_negoos.py", 0.2, "n", -0.3),
            ("CAND-decay", 1.0, "scripts/backtest/translated/c4_decay.py", 0.2, "n", -0.3),
            ("CAND-nooos", 1.0, "scripts/backtest/translated/c4_nooos.py", 0.2, "n", -0.3),
        ]
        oos_rows = [
            ("CAND-good", "scripts/backtest/translated/c4_good.py", "C4-OOS", 0.5, 0.1),
            ("CAND-negoos", "scripts/backtest/translated/c4_negoos.py", "C4-OOS", -0.5, None),
            ("CAND-decay", "scripts/backtest/translated/c4_decay.py", "C4-OOS", 0.5, 0.6),
        ]
        self._fake_q(monkeypatch, is_rows, oos_rows)
        items = ss.fetch_bothwin()
        assert [i["strategy_id"] for i in items] == ["CAND-good"]
        assert items[0]["key"] == "CAND-good@c4_good.py"

    def test_passing_with_p_family_includes_all(self, monkeypatch):
        self._fake_q(
            monkeypatch,
            [("CAND-a", 1.0, "s/a.py", 0.2, "n", -0.1), ("CAND-b", 0.5, "s/b.py", 0.2, "n", -0.1)],
            [("CAND-a", "s/a.py", "C4-OOS", 0.5, 0.1), ("CAND-b", "s/b.py", "C4-OOS", 0.5, 0.1)])
        monkeypatch.setattr(ss, "is_window_days", lambda: 977)
        p_map, items = ss.passing_with_p()
        assert set(p_map) == {"CAND-a@a.py", "CAND-b@b.py"}  # BH 族=及格全集（含弱者）
        assert p_map["CAND-a@a.py"] < p_map["CAND-b@b.py"]


class TestCorr:
    def test_corr_matrix_pairing_and_overlap_guard(self, monkeypatch):
        idx = pd.date_range("2020-01-01", periods=100, freq="B")
        s1 = pd.Series(range(100), index=idx, dtype=float)
        s2 = s1 * 2 + 1  # 完全正相关
        monkeypatch.setattr(ss, "net_returns", lambda sf: {"a.py": s1, "b.py": s2}[Path(sf).name])
        items = [{"key": "A@a.py", "source_file": "x/a.py"},
                 {"key": "B@b.py", "source_file": "x/b.py"}]
        corr = ss.corr_matrix(items)
        assert corr[("A@a.py", "B@b.py")] == pytest.approx(1.0, abs=1e-6)

    def test_corr_short_overlap_skipped(self, monkeypatch):
        idx = pd.date_range("2020-01-01", periods=30, freq="B")  # <60 重叠
        s1 = pd.Series(range(30), index=idx, dtype=float)
        s2 = pd.Series(range(30), index=idx, dtype=float)
        monkeypatch.setattr(ss, "net_returns", lambda sf: {"a.py": s1, "b.py": s2}[Path(sf).name])
        items = [{"key": "A@a.py", "source_file": "x/a.py"},
                 {"key": "B@b.py", "source_file": "x/b.py"}]
        assert ss.corr_matrix(items) == {}

    def test_corr_module_failure_not_fatal(self, monkeypatch):
        def boom(sf):
            raise RuntimeError("build fail")
        monkeypatch.setattr(ss, "net_returns", boom)
        items = [{"key": "A@a.py", "source_file": "x/a.py"},
                 {"key": "B@b.py", "source_file": "x/b.py"}]
        assert ss.corr_matrix(items) == {}  # 宁漏勿误：单件失败不阻断批
