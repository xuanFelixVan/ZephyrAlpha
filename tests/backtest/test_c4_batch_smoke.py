# [BLUEPRINT] MOD-BT-077 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_c4_batch_smoke
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.translated._c4_engine
# [CONSUMERS] C4 批测质量守卫（MODIFY-GUARD: _c4_engine / c4_batch_screen）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯合成数据（不连 CH）；测试不写生产路径；契约检查只 import 不 build
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-077 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 批测冒烟守卫——引擎单测（合成数据）+ translated 模块契约检查。"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_TRANSLATED = _REPO / "scripts" / "backtest" / "translated"
sys.path.insert(0, str(_TRANSLATED))

from _c4_engine import (  # noqa: E402
    batch_deflated_sharpe,
    daily_net_returns,
    knowledge_drift_report,
    parse_knowledge_effective_from,
    run_backtest,
    scan_knowledge_sentinels,
    window_for,
)


def _panel(days: int, syms: int, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=days)
    rets = rng.normal(0.0005, 0.02, size=(days, syms))
    px = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=idx,
                      columns=[f"{i:06d}" for i in range(syms)])
    return px


class TestRunBacktest:
    def test_zero_weights_flat(self):
        px = _panel(60, 3)
        w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
        stats = run_backtest(w, px)
        assert stats["equity_final"] == 1.0
        assert stats["sharpe"] == 0.0

    def test_constant_hold_matches_underlying(self):
        px = _panel(120, 2)
        w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
        w.iloc[5:, :] = 0.5
        stats = run_backtest(w, px)
        # 无成本口径的单利对照（容忍成本与浮点差）
        net = daily_net_returns(w, px)
        assert len(net) == len(px)
        assert stats["days"] == len(px)
        assert -0.9 < stats["max_drawdown"] <= 0.0

    def test_turnover_cost_positive(self):
        px = _panel(80, 2)
        w_hold = pd.DataFrame(0.0, index=px.index, columns=px.columns)
        w_hold.iloc[10:, :] = 0.5
        w_churn = w_hold.copy()
        w_churn.iloc[::10, :] = 0.0  # 制造换手
        s_hold = run_backtest(w_hold, px)
        s_churn = run_backtest(w_churn, px)
        assert s_churn["avg_turnover_1side"] > s_hold["avg_turnover_1side"]


class TestDeflatedSharpe:
    def test_strong_strategy_discounted_but_top(self):
        rng = np.random.default_rng(3)
        base = pd.Series(rng.normal(0, 0.01, 600), index=pd.bdate_range("2020-01-01", periods=600))
        strong = pd.Series(rng.normal(0.004, 0.01, 600), index=base.index)
        weak = pd.Series(rng.normal(-0.002, 0.01, 600), index=base.index)
        nets = {"a": base, "b": strong, "c": weak}
        out = batch_deflated_sharpe(nets)
        assert set(out) == set(nets)
        assert out["b"] > out["a"]
        assert 0.0 <= out["a"] <= 1.0

    def test_short_series_none(self):
        short = pd.Series([0.001, -0.002])
        out = batch_deflated_sharpe({"short": short})
        assert out["short"] is None

    def test_zero_variance_none(self):
        flat = pd.Series([0.0] * 50)
        out = batch_deflated_sharpe({"flat": flat})
        assert out["flat"] is None


class TestKnowledgeEffectiveSentinel:
    """S3 知识生效日哨兵（备忘 96 批 3）：AI 产物携带生效日，回测预检查漂移。"""

    def test_every_translation_carries_sentinel(self):
        """所有翻译件必须带哨兵——漏标=预检看不见该产物的知识漂移。"""
        files = sorted(_TRANSLATED.glob("c4_*.py"))
        missing = [p.name for p in files if parse_knowledge_effective_from(p) is None]
        assert not missing, f"缺知识生效日哨兵: {missing}"

    def test_sentinel_parse_format(self, tmp_path):
        p = tmp_path / "c4_dummy.py"
        p.write_text(
            '"""假翻译件。\n\n'
            '[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文 | 生成=AI 会话\n'
            '"""\n',
            encoding="utf-8",
        )
        assert parse_knowledge_effective_from(p) == "2026-09-14"
        assert parse_knowledge_effective_from(tmp_path / "nope.py") is None

    def test_drift_report_three_states(self, tmp_path):
        (tmp_path / "c4_a.py").write_text(
            '"""a.\n\n[KNOWLEDGE_EFFECTIVE_FROM] 2020-01-01 | 源=x\n"""\n', encoding="utf-8")
        # 无哨兵文件不进字典（诚实缺，不假装扫过）
        (tmp_path / "c4_b.py").write_text('"""b."""\n', encoding="utf-8")

        clean = knowledge_drift_report("2021-01-01", "2023-12-31", root=tmp_path)
        assert clean["verdict"] == "clean" and clean["scanned"] == 1

        drift = knowledge_drift_report("2019-01-01", "2019-12-31", root=tmp_path)
        assert drift["verdict"] == "drift" and drift["drift_count"] == 1
        assert drift["drift_items"][0]["artifact"] == "c4_a.py"

        empty = knowledge_drift_report("2020-01-01", "2023-12-31", root=tmp_path / "nope")
        assert empty["verdict"] == "empty"

    def test_is_window_declares_drift(self):
        """事实断言：IS 2020-2023 窗口早于全部 AI 翻译件的生成日 → 必判 drift（须声明）。"""
        rep = knowledge_drift_report(*window_for("stock"))
        assert rep["verdict"] == "drift"
        assert rep["drift_count"] == rep["scanned"] > 0
        # 未来窗口（晚于所有哨兵）→ clean，证明判据不是恒真
        assert knowledge_drift_report("2030-01-01", "2030-12-31")["verdict"] == "clean"


class TestWindowAndContract:
    def test_window_for(self):
        assert window_for("stock") == ("2020-01-01", "2023-12-31")
        assert window_for("etf")[0] >= "2021-04"

    def test_translated_modules_contract(self):
        files = sorted(_TRANSLATED.glob("c4_*.py"))
        assert len(files) >= 30, f"翻译件数量异常: {len(files)}"
        pat = re.compile(r"^(CAND-[0-9a-f]{12}|VAL-[A-Z0-9-]+)$")
        for p in files:
            spec = importlib.util.spec_from_file_location(f"contract_{p.stem}", p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            assert mod.STRATEGY_ID, f"STRATEGY_ID 缺失: {p.name}"
            assert pat.match(mod.STRATEGY_ID) or mod.STRATEGY_ID.startswith("VAL-"),                 f"STRATEGY_ID 非法: {p.name} -> {mod.STRATEGY_ID}"
            assert mod.WINDOW_KIND in {"stock", "index", "etf"}, f"WINDOW_KIND 非法: {p.name}"
            assert callable(mod.build), f"build 缺失: {p.name}"

    def test_oos_mode_dsr_computed(self):
        """回归：OOS 模式（include_pilots=False）不得提前返回跳过 DSR 计算（2026-09-13 实测 bug）。"""
        sys.path.insert(0, str(_REPO / "scripts" / "backtest"))
        import c4_batch_screen as runner

        results, failures = runner.run_batch(limit=3, window=("2024-01-01", "2026-06-30"),
                                             include_pilots=False)
        assert not failures
        assert results
        assert not any(r.get("pilot") for r in results)
        assert all(r.get("deflated_sharpe") is not None for r in results)

    def test_runner_exists(self):
        runner = _REPO / "scripts" / "backtest" / "c4_batch_screen.py"
        assert runner.exists()
        text = runner.read_text(encoding="utf-8")
        assert "C4-translated-20260912" in text
        assert "run_deflated_sharpe_batch" not in text  # 委托经引擎，runner 不直连官方件

    def test_dedup_key_four_tuple(self):
        """回归：幂等键=四元组 (batch, sid, verdict, source_file)——同 sid 多版本翻译件
        （族变体重构）不得被跨批判重挡掉，各留一行可溯（2026-09-14 Slater 族实测教训：
        三键判重把 slater_value/value55 原版挡在台账外，文件与成绩失联）。"""
        sys.path.insert(0, str(_REPO / "scripts" / "backtest"))
        import c4_batch_screen as runner

        batch, verdict = "C4-translated-20260912", "translated_c4"
        k_zulu = runner._translated_dedup_key(
            batch, {"strategy_id": "CAND-311220235636", "module": "c4_311220235636_zulu_value.py"}, verdict)
        k_slater = runner._translated_dedup_key(
            batch, {"strategy_id": "CAND-311220235636", "module": "c4_311220235636_slater_value.py"}, verdict)
        assert k_zulu != k_slater, "同 sid 不同文件必须产出不同幂等键（四键语义）"
        assert k_zulu == runner._translated_dedup_key(
            batch, {"strategy_id": "CAND-311220235636", "module": "c4_311220235636_zulu_value.py"},
            verdict), "同批同文件重跑必须同键（幂等保留）"
        assert runner._translated_dedup_key(
            batch, {"strategy_id": "CAND-40ca0da1a3ca", "module": "c4_40ca0da1a3ca_value55.py"},
            "oos_tested") != runner._translated_dedup_key(
            batch, {"strategy_id": "CAND-40ca0da1a3ca", "module": "c4_40ca0da1a3ca_value55.py"},
            "translated_c4"), "不同 verdict 不同键（deferred 不挡 translated）"
        assert runner._deferred_dedup_key(batch, "CAND-x", "orig.csv") == (
            batch, "CAND-x", "deferred_c4", "orig.csv")


class TestPitDailyFrame:
    """基本面门 PIT 语义（MOD-BT-096 2026-09-15 扩展）：值自 announce_date 起生效。"""

    def test_announce_date_effective_and_ffill(self):
        from _valuation_engine import pit_daily_frame

        ann = pd.DataFrame({
            "announce_date": pd.to_datetime(["2020-01-10", "2020-04-15"]),
            "symbol": ["000001", "000001"],
            "val": [5.0, 8.0],
        })
        idx = pd.date_range("2020-01-01", periods=120, freq="D")
        out = pit_daily_frame(ann, idx)
        assert pd.isna(out.loc["2020-01-09", "000001"]), "公告日前不得有值（防前视）"
        assert out.loc["2020-01-10", "000001"] == 5.0, "公告日当日生效"
        assert out.loc["2020-04-14", "000001"] == 5.0, "持续至下一公告前"
        assert out.loc["2020-04-15", "000001"] == 8.0, "新公告日切换"

    def test_multi_symbol_and_empty(self):
        from _valuation_engine import pit_daily_frame

        idx = pd.date_range("2020-01-01", periods=5, freq="D")
        empty = pit_daily_frame(pd.DataFrame(columns=["announce_date", "symbol", "val"]), idx)
        assert empty.shape == (5, 0), "空公告=零列全 NaN"
        ann = pd.DataFrame({
            "announce_date": pd.to_datetime(["2020-01-02", "2020-01-03"]),
            "symbol": ["000001", "000002"],
            "val": [1.0, 2.0],
        })
        out = pit_daily_frame(ann, idx)
        assert out.loc["2020-01-01"].isna().all(), "首日无任何公告=全 NaN"
        assert out.loc["2020-01-04", "000001"] == 1.0 and out.loc["2020-01-04", "000002"] == 2.0
