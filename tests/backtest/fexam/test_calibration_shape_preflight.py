# [TTL] permanent
# [BLUEPRINT] MOD-BT-243 | tests/backtest/fexam/test_calibration_shape_preflight.py
# 测试隔离：卡/分数册/试次册全在 tmp_path；信号/目标合成注入（零 CH 零生产路径写）。
# 执行器形状预检红蓝双向（⑤席 2026-10-15，B 族 14 卡 ill-formed 教训根治件）：
# panel×series→blocked(shape_mismatch) 不翻卡；panel×panel（同列数）／series×series→照常判分。
"""形状预检单测：不匹配=blocked 诚实行（卡不翻、零异常），匹配=判分路径逐字不变。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import calibration_exam as ce
from zephyr.backtest.core import n_trial_ledger as _ntl


@pytest.fixture(autouse=True)
def _isolate_trial_ledger(tmp_path, monkeypatch):
    """同域 test_calibration_exam 同款：本支全篇禁写生产 N 账本（根宪法 §9 条目 6）。"""
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    target = tmp_path / "trial_ledger_registry.yaml"
    TrialLedger(registry_path=target).load_registry(create_if_missing=True)
    monkeypatch.setattr(_ntl, "LEDGER_REGISTRY_PATH", target)
    yield target


# ---------------------------------------------------------------------------
# 合成夹具（panel=多符号宽表；series=市场级单序列，"沪深300 明日涨跌幅"形态）
# ---------------------------------------------------------------------------


def _series_pair(n: int = 900, seed: int = 7, strength: float = 60.0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    sig = pd.Series(rng.normal(size=n), index=idx)
    tgt = pd.Series(0.01 * rng.normal(size=n) + strength * 0.02 * sig.shift(1).fillna(0).to_numpy(), index=idx)
    return sig, tgt


def _panel_pair(n: int = 900, ncols: int = 40, seed: int = 7):
    """合成面板＋前瞻收益宽表：fwd[t] 由 panel[t-1] 生成（执行器 shift(-1) 对齐 t→t+1，
    与既有 _synthetic 同一 PIT 模式）⇒ 匹配面真出强正 IC，判别力不落在夹具对齐缺陷上。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    cols = [f"S{i:04d}" for i in range(ncols)]
    panel = pd.DataFrame(rng.normal(size=(n, ncols)), index=idx, columns=cols)
    fwd = pd.DataFrame(
        0.05 * panel.shift(1).fillna(0).to_numpy() + 0.01 * rng.normal(size=(n, ncols)), index=idx, columns=cols
    )
    return panel, fwd


def _card(tmp_path, kind: str = "series", **kw) -> str:
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/shapereflight/01",
        "node_id": "TDM-E-TEST",
        "family": "calibration",
        "status": "preregistered",
        "signal_kind": kind,
        "window": {"in_sample": ["2020-01-01", "2023-12-31"], "regimes": {}},
        "pillars_numeric": {"ic_mean_min": 0.0, "oos_same_sign": True},
    }
    card.update(kw)
    p = tmp_path / "card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _with_oos(p: str, idx: pd.DatetimeIndex, start: int = 700) -> str:
    """给卡补一个覆盖末段的 oos 窗（series 门槛 n≥60、panel 门槛 n≥30，保证匹配面能出 oos 读数）。"""
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    card["oos_window_ref"] = [str(idx[start].date()), str(idx[-1].date())]
    Path(p).write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 红面：形状不配 → blocked(shape_mismatch) 诚实行，卡不翻 examined、零异常
# ---------------------------------------------------------------------------


def test_panel_signal_with_series_target_blocked(tmp_path):
    """事故形态复考（calibration_exam:261 实测 TypeError）：panel 信号卡配市场级单序列目标
    ⇒ 不再崩，改出 verdict=blocked 诚实行；分数册追加一行；卡字节零动不翻 examined。"""
    p = _card(tmp_path, kind="panel")
    panel, _ = _panel_pair()
    _, market_tgt = _series_pair()
    before = Path(p).read_bytes()
    row = ce.run_card(p, signal=panel, target=market_tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "blocked" and row["reason"] == "shape_mismatch"
    assert any(f.startswith("shape_mismatch: panel 信号") for f in row["fails"]), row["fails"]
    assert row["pillars_all_pass"] is False and row["run_id"]
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1 and reg["rows"][0]["verdict"] == "blocked"
    assert reg["rows"][0]["metrics"]["shape_preflight"]["signal_cols"] == 40
    # 卡零触碰：bytes 逐位不变（比"status 未翻"更强的钉），重发出题后可直接重考
    assert Path(p).read_bytes() == before
    assert yaml.safe_load(before.decode("utf-8"))["status"] == "preregistered"


def test_series_signal_with_panel_target_blocked(tmp_path):
    """规则②同向不配：series 信号配 panel 目标 ⇒ blocked（旧形态=_series_metrics concat 出
    MultiIndex 面静默算错），拦截行同样 only-add、卡不翻。"""
    p = _card(tmp_path, kind="series")
    sig, _ = _series_pair()
    _, fwd = _panel_pair()
    row = ce.run_card(p, signal=sig, target=fwd, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "blocked" and row["reason"] == "shape_mismatch"
    assert any("series 信号" in f and "panel 目标" in f for f in row["fails"]), row["fails"]
    assert yaml.safe_load(Path(p).read_text(encoding="utf-8"))["status"] == "preregistered"


def test_single_column_panel_target_with_wide_signal_blocked(tmp_path):
    """规则③（比崩更危险的静默错分面）：双面板但 target 仅 1 列而信号 40 列（悬殊且单列）
    ⇒ blocked 且细节点名两医列数——fast_rank_ic 列交集为空会出假 0 分，禁走到那一步。"""
    p = _card(tmp_path, kind="panel")
    panel, _ = _panel_pair(ncols=40)
    _, market_tgt = _series_pair()
    row = ce.run_card(p, signal=panel, target=market_tgt.to_frame("MKT"), scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "blocked" and row["reason"] == "shape_mismatch"
    assert any("40 列" in f and "1 列" in f for f in row["fails"]), row["fails"]
    assert row["metrics"]["shape_preflight"]["target_cols"] == 1


def test_blocked_row_records_no_trial_and_card_rerunnable(tmp_path):
    """预检拦截＝接线错误非研究试次：不记 n_trial_ledger（不占 DSR 分母）；
    卡保持 preregistered ⇒ 重发出题后 run_card 无需 --force 可直接重考。"""
    p = _card(tmp_path, kind="panel")
    panel, _ = _panel_pair()
    _, market_tgt = _series_pair()
    led = tmp_path / "led.yaml"
    ce.run_card(p, signal=panel, target=market_tgt, scores_path=tmp_path / "s.yaml", ledger_registry_path=led)
    assert not led.exists() or "TDM-E-TEST" not in led.read_text(encoding="utf-8")
    # 重考不抛（状态机未翻）
    row2 = ce.run_card(p, signal=panel, target=market_tgt, scores_path=tmp_path / "s.yaml")
    assert row2["verdict"] == "blocked"
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 2  # only-add：两跑两行


# ---------------------------------------------------------------------------
# 蓝面：形状匹配 → 照常判分（判分路径与改前逐字同），+_shape_preflight 单元规则
# ---------------------------------------------------------------------------


def test_panel_panel_same_cols_scores_normally(tmp_path):
    """panel×panel 同列数 ⇒ 预检放行，照常判分（强信号应 pass），卡翻 examined 带 lineage。"""
    p = _with_oos(_card(tmp_path, kind="panel"), _panel_pair()[0].index)
    panel, fwd = _panel_pair()
    row = ce.run_card(p, signal=panel, target=fwd, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "pass", row["fails"]
    assert row["metrics"]["ic_mean"] == row["metrics"]["ic_mean"]  # 真判分非拦截
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "examined" and card["lineage"]["run_id"]


def test_series_series_scores_normally(tmp_path):
    """series×series ⇒ 预检放行，照常判分（既有主面零回归：mono/ic/oos 照出）。"""
    p = _with_oos(_card(tmp_path, kind="series"), _series_pair()[0].index)
    sig, tgt = _series_pair()
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "pass", row["fails"]
    assert row["metrics"]["mono_spearman"] == row["metrics"]["mono_spearman"]
    assert yaml.safe_load(Path(p).read_text(encoding="utf-8"))["status"] == "examined"


def test_shape_preflight_unit_rules():
    """三条规则逐条钉：①panel×Series ②Series×panel ③悬殊单列 panel 目标→mismatch；
    三个匹配形态（panel×panel 同列、series×series、1×1 面板）→None。"""
    sig_s, tgt_s = _series_pair(n=30)
    panel, fwd = _panel_pair(n=30, ncols=5)
    assert ce._shape_preflight({"card_id": "x"}, panel, tgt_s) is not None  # ①
    assert ce._shape_preflight({"card_id": "x"}, sig_s, fwd) is not None  # ②
    assert ce._shape_preflight({"card_id": "x"}, panel, fwd[["S0000"]]) is not None  # ③ 5 列 vs 1 列
    assert ce._shape_preflight({"card_id": "x"}, panel, fwd) is None  # panel×panel 同列数
    assert ce._shape_preflight({"card_id": "x"}, sig_s, tgt_s) is None  # series×series
    assert ce._shape_preflight({"card_id": "x"}, fwd[["S0000"]], fwd[["S0001"]]) is None  # 1×1 合法


# ---------------------------------------------------------------------------
# 第二腿（⑤席 2026-10-17）：卡面 regimes 散文条目＝"装载崩"根治为诚实 blocked 行
# 真源＝⑦A 1016-03 与 ⑦c 1017-01 两班在册实测（13 枚卡崩于 pd.Timestamp(散文)）
# ---------------------------------------------------------------------------


def test_regimes_preflight_unit_rules():
    """只拦"零枚 ISO 日期"一支；**恰一枚日期者照 2026-10-13 裁修走旧语义（整串当单点）＝不拦**；
    两枚/多段声明/空 regimes/无 window 键皆不拦（负对照面，禁把本腿当恒拦尺）。"""
    assert ce._regimes_preflight({"window": {"regimes": {"crisis": "两处在册危机段"}}}) is not None
    assert ce._regimes_preflight({"window": {"regimes": {"crisis": "2020-03-23"}}}) is None  # 裁修旧语义
    assert ce._regimes_preflight({"window": {"regimes": {"crisis": "2020-02-01..2020-03-23"}}}) is None
    assert (
        ce._regimes_preflight({"window": {"regimes": {"c": "2020-02-01..2020-03-23 与 2024-01-02..2024-02-08"}}})
        is None
    )
    assert ce._regimes_preflight({"window": {"regimes": {}}}) is None
    assert ce._regimes_preflight({}) is None


def test_prose_regimes_card_becomes_honest_blocked_row(tmp_path):
    """事故形态复考：形状配、供数配，只卡面 regime 写成叙述句 ⇒ 旧行为抛 DateParseError，
    新行为出 verdict=blocked 诚实行（分数册 only-add 一行・卡字节零动不翻 examined・不记试次）
    ＝该卡从"崩在装载"变成"被诚实记为不可考"，且重发出题后可直接重考。"""
    p = _card(tmp_path, kind="series")
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    card["window"]["regimes"] = {"crisis": "两处在册危机段（散文，未写日期）"}
    Path(p).write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    sig, tgt = _series_pair()
    p = _with_oos(p, sig.index)
    before = Path(p).read_bytes()
    led = tmp_path / "led.yaml"
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml", ledger_registry_path=led)
    assert row["verdict"] == "blocked" and row["reason"] == "regimes_unparsable", row
    assert any(f.startswith("regimes_unparsable: ") and "两处在册危机段" in f for f in row["fails"]), row["fails"]
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1 and reg["rows"][0]["verdict"] == "blocked"
    assert Path(p).read_bytes() == before  # 卡零触碰（比"status 未翻"更强的钉）
    assert not led.exists() or "TDM-E-TEST" not in led.read_text(encoding="utf-8")


def test_parsable_regimes_still_judged(tmp_path):
    """负对照＝日期可解析的 regime 绝不被本腿拦；这条若也 blocked＝本腿恒真＝尺坏。"""
    p = _card(tmp_path, kind="series")
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    card["window"]["regimes"] = {"crisis": "2020-02-01..2020-03-23 与 2024-01-02..2024-02-08"}
    Path(p).write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    sig, tgt = _series_pair()
    p = _with_oos(p, sig.index)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s2.yaml")
    assert row["verdict"] != "blocked", row
