# [MODULE] tests.backtest.test_exp_ic_evidence
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas; numpy
# [CONSUMERS] MOD: scripts.backtest.exp_ic_evidence 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 零网络零 CH：全部数据访问走 exp_ic_evidence._ch_query 注入缝（fake query
#   返回罐装 TSV），统计核断言用合成面板；禁触生产路径（tmp_path fixture）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [TTL] permanent
"""exp_ic_evidence 零网骨单测——探表/加载缝/因子面板/判读门/出证 YAML 组装。"""
from __future__ import annotations

import pandas as pd
import pytest

from scripts.backtest import eval_exp_expectations as ev
from scripts.backtest import exp_ic_evidence as exe


# ---------------------------------------------------------------- 探表（fake TSV）
class TestProbe:
    def test_probe_tables_parses_counts_and_grades(self):
        def fake_query(sql, timeout=60):
            if "count()" in sql and "consensus_daily_repaired" in sql:
                return "1563996\n"
            if "uniqExact" in sql:
                return "2017-01-03\t2021-12-31\t3253\n"
            if "GROUP BY confidence" in sql:
                return "high\t39101\nlow\t1\nmid\t153263\n"
            if "count()" in sql and "pdf_forecast_extracted" in sql:
                return "192365\n"
            raise AssertionError(f"意外 SQL: {sql[:80]}")

        p = exe.probe_tables(query=fake_query)
        assert p["consensus_daily_repaired"]["rows"] == 1563996
        assert p["consensus_daily_repaired"]["span"] == ["2017-01-03", "2021-12-31"]
        assert p["consensus_daily_repaired"]["symbols"] == 3253
        # 三档计数齐全（mid/low=诊断计数档，结构上必须在场）
        assert p["pdf_forecast_extracted"]["confidence_counts"] == {
            "high": 39101, "mid": 153263, "low": 1}

    def test_main_zero_data_path_writes_honest_file(self, monkeypatch, tmp_path):
        def boom():
            raise RuntimeError("CH 不可达")

        monkeypatch.setattr(exe, "probe_tables", boom)
        monkeypatch.setattr("sys.argv", ["exp_ic_evidence", "--out", str(tmp_path / "z.yaml")])
        assert exe.main() == 0
        text = (tmp_path / "z.yaml").read_text(encoding="utf-8")
        assert "zero_data: true" in text and "CH 不可达" in text
        assert "零造数" in text  # reason 末尾带零造数声明（诚实件契约）


# ---------------------------------------------------------------- 加载缝（fake 月度分块）
class TestLoadConsensus:
    def test_fy1_selection_and_columns(self):
        calls: list[str] = []

        def fake_query(sql, timeout=60):
            calls.append(sql)
            if "toDate('2018-01-01')" in sql:
                # symbol, td, fy, eps_consensus, eps_std, rating_mean
                return ("600519.SH\t2018-01-05\t2018\t12.5\t0\t4.2\n"
                        "600519.SH\t2018-01-05\t2019\t13.0\t0\t4.2\n"
                        "600519.SH\t2018-01-31\t2018\t12.8\t0\t4.5\n")
            return ""

        df = exe.load_consensus_fy1(query=fake_query)
        assert list(df.columns) == ["symbol", "td", "eps_consensus", "eps_std",
                                    "rating_mean", "eps_mean"]
        # fy1=>=当年最小预测年：同 (symbol,td) 两行 fy=2018/2019 → 取 2018（升序首行）
        row = df[(df["symbol"] == "600519.SH") & (df["td"] == pd.Timestamp("2018-01-05"))]
        assert len(row) == 1 and float(row.iloc[0]["eps_consensus"]) == 12.5
        assert any("consensus_daily_repaired" in c for c in calls)


# ---------------------------------------------------------------- 因子面板（合成）
class TestFactorPanels:
    def _fixtures(self):
        cal = ["2018-01-02", "2018-01-31", "2018-02-01", "2018-02-28",
               "2018-03-01", "2018-03-30"]
        mes = ["2018-01-31", "2018-02-28", "2018-03-30"]
        syms = ["A", "B", "C"]
        idx = pd.to_datetime(cal)
        px = pd.DataFrame([[10.0, 20.0, 5.0], [11.0, 18.0, 6.0], [10.5, 22.0, 4.5],
                           [12.0, 19.0, 5.5], [11.5, 21.0, 5.0], [12.5, 20.0, 6.0]],
                          index=idx, columns=syms)
        cons = pd.DataFrame({
            "symbol": ["A"] * 3 + ["B"] * 3 + ["C"] * 3,
            "td": list(idx[:3]) * 3,
            "eps_consensus": [1.0, 1.1, 1.2, 2.0, 2.1, 2.2, 0.5, 0.4, 0.3],
            "eps_std": [0.0] * 9, "rating_mean": [4.0] * 9, "eps_mean": [1.0] * 9})
        return cal, mes, syms, px, cons

    def test_exp01_panel_is_eps_over_close(self):
        cal, mes, _, px, cons = self._fixtures()
        fac = exe.factor_panel_exp01(cons, px, cal, mes)
        assert not fac.empty
        jan = fac[fac["td"] == pd.Timestamp("2018-01-31")].set_index("symbol")["f"]
        # A: 1.1/11.0  B: 2.1/18.0  C: 0.4/6.0（2018-01-31 快照 eps/close，正向=EP 高）
        assert jan["A"] == pytest.approx(1.1 / 11.0)
        assert jan["B"] == pytest.approx(2.1 / 18.0)
        assert jan["C"] == pytest.approx(0.4 / 6.0)

    def test_exp03_breadth_snapshot_as_of_month_end(self):
        cal, mes, _, px, cons = self._fixtures()
        one = cons[cons["symbol"] == "A"][["td", "eps_consensus"]]
        cons_a = one.set_index("td")["eps_consensus"].sort_index()
        pdf = pd.DataFrame({
            "symbol": ["A"] * 3,
            "publish_date": pd.to_datetime(["2018-01-05", "2018-01-20", "2018-02-10"]),
            "forecast_year": [2018] * 3,
            "eps": [1.5, 0.9, 1.3],  # vs 前值 1.0/1.0/1.1 → 上/下/上
        })
        fac = exe.factor_panel_exp03(pdf, cons[cons["symbol"] == "A"]
                                     [["symbol", "td", "eps_consensus", "eps_std",
                                       "rating_mean", "eps_mean"]], cal, mes)
        assert not fac.empty
        jan = fac[fac["td"] == pd.Timestamp("2018-01-31")].set_index("symbol")["f"]["A"]
        feb = fac[fac["td"] == pd.Timestamp("2018-02-28")].set_index("symbol")["f"]["A"]
        # 1 月末快照=最后事件 2018-01-20 的窗口占比（1 上 1 下=0.5，63 自然日窗覆盖两事件）
        assert jan == pytest.approx(0.5)
        # 2 月末快照=最后事件 2018-02-10（2 上 1 下≈0.6667）
        assert feb == pytest.approx(2.0 / 3.0)

    def test_exp03_same_day_reports_dedupe_no_crash(self):
        """回归（首跑零数据件教训 2026-09-18）：同标的同发布日多份研报 → 事件网格
        重复标签，reindex 崩（cannot reindex on an axis with duplicate labels）。
        同日各行滚动窗口一致 → keep=last 去重值不变。"""
        cal = ["2018-01-02", "2018-01-31", "2018-02-28"]
        mes = ["2018-01-31"]
        cons = pd.DataFrame({
            "symbol": ["A"] * 2,
            "td": pd.to_datetime(["2018-01-02", "2018-01-02"]),
            "eps_consensus": [1.0, 1.0],
            "eps_std": [0.0] * 2, "rating_mean": [4.0] * 2, "eps_mean": [1.0] * 2})
        cons = cons.drop_duplicates(["symbol", "td"])
        pdf = pd.DataFrame({
            "symbol": ["A"] * 2,
            "publish_date": pd.to_datetime(["2018-01-05", "2018-01-05"]),  # 同日两份
            "forecast_year": [2018] * 2,
            "eps": [1.5, 1.2],  # 同日两份均>前值 1.0（双上调）→ 同日窗口占比 1.0
        })
        fac = exe.factor_panel_exp03(pdf, cons, cal, mes)
        assert not fac.empty
        jan = fac[fac["td"] == pd.Timestamp("2018-01-31")].set_index("symbol")["f"]["A"]
        assert jan == pytest.approx(1.0)  # 同日两份均上调 → 窗口占比 1.0


# ---------------------------------------------------------------- 判读门（exp_r36 判据）
class TestSegAndJudge:
    def _icdf(self, mu: float, n_months: int = 36,
              ic_values: list[float] | None = None) -> pd.DataFrame:
        import numpy as np

        rng = np.random.default_rng(7)
        vals = ic_values if ic_values is not None else list(rng.normal(mu, 0.02, n_months))
        return pd.DataFrame({
            "td": [f"2019-{m:02d}-28" if m <= 12 else f"2020-{m - 12:02d}-28"
                   for m in range(1, n_months + 1)][:n_months],
            "n": [200] * n_months,
            "ic": vals,
            "mom_ic": [0.0] * n_months,
        })

    def test_green_requires_all_three_gates(self):
        seg = exe.seg_with_t(self._icdf(0.05), "2021-12-31", 36)
        assert seg["rank_ic_mean"] == seg["ic_mean"]  # IC=秩IC 同值双标
        assert seg["sig_rule_met"] and abs(seg["t_stat"]) > 3.0
        v, reasons = exe.judge(seg)
        assert v == exe.VERDICT_GREEN and reasons == []

    def test_red_when_t_below_3(self):
        # 确定性构造：mean=0.03（过 |IC| 门）、半幅 0.3 → |t|=25.1*0.03/0.3≈2.51（不过 t 门）
        seg = exe.seg_with_t(
            self._icdf(0.03, ic_values=[0.33, -0.27] * 18), "2021-12-31", 36)
        assert abs(seg["ic_mean"] - 0.03) < 1e-9 and abs(seg["t_stat"]) < 3.0
        v, reasons = exe.judge(seg)
        assert v == exe.VERDICT_RED
        assert any("|t|" in r for r in reasons)

    def test_insufficient_months_not_evaluable(self):
        seg = exe.seg_with_t(self._icdf(0.05, n_months=5), "2021-12-31", 36)
        assert seg["ic_mean"] is None and seg["sig_rule_met"] is False
        v, reasons = exe.judge(seg)
        assert v == exe.VERDICT_NOT_EVALUABLE

    def test_not_evaluable_entries_frozen(self):
        for f in ("exp02", "exp05"):
            e = exe.not_evaluable_entry(f, exe._NOT_EVALUABLE_REASONS[f])
            assert e["status"] == exe.VERDICT_NOT_EVALUABLE
            assert e["promotion_authority"] == "none"
            assert e["is_window"] == list(ev._PROTOCOLS["exp_r36"]["is"])


# ---------------------------------------------------------------- 出证 YAML 组装
class TestRender:
    def _probe(self):
        return {
            "consensus_daily_repaired": {"table": "c3_fundamental.consensus_daily_repaired",
                                         "rows": 100, "span": ["2017-01-03", "2021-12-31"],
                                         "symbols": 10},
            "pdf_forecast_extracted": {"table": "c3_fundamental.pdf_forecast_extracted",
                                       "rows": 50,
                                       "confidence_counts": {"high": 30, "mid": 19, "low": 1}},
        }

    def test_yaml_carries_verbatim_ruling_marker_and_grades(self):
        text = exe.render_yaml(self._probe(),
                               {"exp01_consensus_ep": {
                                   "verdict": exe.VERDICT_RED, "n_months": 36,
                                   "ic_mean": 0.01, "rank_ic_mean": 0.01, "t_stat": 1.0,
                                   "t_p": 0.3, "coverage_mean": 800.0,
                                   "coverage_ratio": 1.0, "mom_ic_mean": 0.0,
                                   "red_reasons": ["|IC|=0.0100 < 0.02（效应量地板不动）"],
                                   "promotion_authority": "none"}},
                               [f"2019-{m:02d}-28" for m in range(1, 13)], 36)
        # 裁定逐字引用完整在件（拆行/改词=伪造，禁）
        assert exe.RULING_338_4_VERBATIM in text
        assert "窗缩" in text
        assert "high: 30" in text and "mid: 19" in text and "low: 1" in text
        assert "rank_ic_mean: 0.01" in text
        assert "promotion_authority: none" in text

    def test_yaml_is_parseable(self):
        import yaml

        text = exe.render_yaml(self._probe(), {}, ["2019-01-31"], 36)
        doc = yaml.safe_load(text)
        assert doc["caliber"]["window_shrink_marker"] == "窗缩"
        assert doc["probe"]["exp_grade_counts"]["high"] == 30
        assert doc["caliber"]["ruling_338_4_verbatim"].strip() == exe.RULING_338_4_VERBATIM

    def test_yaml_parseable_with_red_factor_and_reasons(self):
        """回归（首跑件实证）：reason/red_reasons 以 | 开头（如 |IC|=0.0191）会被 YAML
        当块标量指示符 → 整件不可解析。生成器必须加引号壳。"""
        import yaml

        factors = {
            "exp06_rating_momentum": {
                "verdict": exe.VERDICT_RED, "n_months": 36,
                "ic_mean": -0.0191, "rank_ic_mean": -0.0191, "t_stat": -1.3242,
                "t_p": 0.19403, "coverage_mean": 190.0, "coverage_ratio": 1.0,
                "mom_ic_mean": -0.0122,
                "red_reasons": ["|IC|=0.0191 < 0.02（效应量地板不动）",
                                "|t|=1.3242 未超 3.0（Harvey-Liu-Zhu 收紧门槛）"],
                "promotion_authority": "none"},
            "exp02_revision_momentum": exe.not_evaluable_entry(
                "exp02", exe._NOT_EVALUABLE_REASONS["exp02"]),
        }
        doc = yaml.safe_load(exe.render_yaml(self._probe(), factors,
                                             ["2019-01-31"], 36))
        f = doc["factors"]["exp06_rating_momentum"]
        assert f["verdict"] == "RED"
        assert f["red_reasons"][0].startswith("|IC|=")  # 引号壳后内容原样保留
        assert doc["factors"]["exp02_revision_momentum"]["status"] == "NOT_EVALUABLE"

    def test_zero_data_yaml_parseable_and_honest(self):
        import yaml

        doc = yaml.safe_load(exe.render_zero_data("探表失败（X）"))
        assert doc["zero_data"] is True and doc["status"] == "NOT_EVALUABLE"
        assert doc["factors"] == {}

    def test_zero_data_reason_with_exception_colon_parsable(self):
        """红队批回归：_fail_reason 摘要恒含 "类型: 消息" 的 ": "（异常格式化必有），
        裸拼时 YAML 把第二个 ": " 当 mapping → 零数据件自身不可解析（实证
        ScannerError line 8）。引号壳后须可解析且内容原样。"""
        import yaml

        reason = ("探表失败（HTTPError: 404 bad gateway @ ch_reader.py:50 query）——"
                  "数据不可考，零造数")
        doc = yaml.safe_load(exe.render_zero_data(reason))
        assert doc["zero_data"] is True
        assert doc["reason"].startswith("探表失败（HTTPError: 404")


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
