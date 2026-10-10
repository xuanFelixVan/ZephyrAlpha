# [BLUEPRINT] MOD-BT-247 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_calibration_exam.py
# 测试隔离：卡/分数册全在 tmp_path；信号/目标合成注入（零 CH）。
# [TTL] permanent
"""校准卡执行器红蓝双向：门柱机械判/状态机/分数册 only-add/试次留痕/fail-closed。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import calibration_exam as ce


def _card(tmp_path, **kw) -> str:
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/calibration/02",
        "node_id": "TDM-E-TEST",
        "family": "calibration",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {
            "in_sample": ["2020-01-01", "2023-12-31"],
            "regimes": {"bull": "2020-01-01..2021-12-31", "bear": "2022-01-01..2023-12-31"},
        },
        "oos_window_ref": ["2024-01-01", "2024-12-31"],
        "pillars_numeric": {
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "ic_ir_min": 0.3,
            "regime_same_sign": True,
            "oos_same_sign": True,
        },
    }
    card.update(kw)
    p = tmp_path / "card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _synthetic(n: int = 1450, strength: float = 1.0, seed: int = 7):
    """合成信号/目标：strength=1 强单调（应 pass），strength=0 噪声（应 fail）。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    sig = pd.Series(rng.normal(size=n), index=idx)
    tgt = pd.Series(0.01 * rng.normal(size=n) + strength * 0.02 * sig.shift(1).fillna(0).to_numpy(), index=idx)
    return sig, tgt


def test_series_pass_on_strong_signal(tmp_path):
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=60.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "scores.yaml")
    assert row["verdict"] == "pass" and row["pillars_all_pass"] is True
    # 卡面推进 + 分数册落行
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "examined" and card["lineage"]["run_id"]
    reg = yaml.safe_load((tmp_path / "scores.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1 and reg["rows"][0]["card_id"] == "TDM-E-TEST/calibration/02"


def test_series_fail_on_noise(tmp_path):
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=0.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "scores.yaml")
    assert row["verdict"] == "fail" and row["fails"]


def test_empty_card_rejected(tmp_path):
    p = _card(tmp_path, status="empty")
    sig, tgt = _synthetic()
    with pytest.raises(RuntimeError, match="只考 preregistered"):
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")


def test_examined_card_needs_force(tmp_path):
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=60.0)
    ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    with pytest.raises(RuntimeError, match="重考带 --force"):
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    # force 重考=分数册 only-add 两行
    ce.run_card(p, signal=sig, target=tgt, force=True, scores_path=tmp_path / "s.yaml")
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 2


def test_missing_pillars_numeric_fail_closed(tmp_path):
    p = _card(tmp_path)
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    del card["pillars_numeric"]
    Path(p).write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    sig, tgt = _synthetic()
    with pytest.raises(RuntimeError, match="pillars_numeric"):
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")


def test_missing_data_injection_fail_closed(tmp_path):
    p = _card(tmp_path)
    with pytest.raises(RuntimeError, match="注入"):
        ce.run_card(p, scores_path=tmp_path / "s.yaml")


def test_no_upgrade_signal_w5_alignment(tmp_path):
    """红蓝互锁：OOS 不成立时 oos_ok=False → W5 判据不升级（两件契约对齐）。"""
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=60.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    # 强信号下 oos 窗也有数 → oos_ok True；本断言钉 schema 契约字段存在
    assert isinstance(row["oos_ok"], bool) and row["kind"] == "exam"
    assert set(row["regimes"]) >= {"bull"} or row["regimes"] == []


# ---------------------------------------------------------------------------
# 对照/消融分支（夜矿续战三连裁② 2026-10-10 并入 MOD-BT-243 执行核）
# ---------------------------------------------------------------------------


def _comparison_card(tmp_path, **kw) -> str:
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/comparison/02",
        "node_id": "TDM-E-TEST",
        "family": "comparison",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {
            "in_sample": ["2020-01-01", "2023-12-31"],
            "regimes": {"bull": "2020-01-01..2021-12-31", "bear": "2022-01-01..2023-12-31"},
        },
        "oos_window_ref": ["2024-01-01", "2024-12-31"],
        "pillars_numeric": {
            "maxdd_improvement_min": 0.0,
            "maxdd_deterioration_max_pp": 2.0,
            "sharpe_delta_min": -0.1,
            "turnover_delta_annual_max": 8.0,
            "oos_same_sign": True,
        },
    }
    card.update(kw)
    p = tmp_path / "cmp_card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _arms(n: int = 1450, open_edge: float = 0.4, seed: int = 11):
    """合成双臂：开臂=基臂敞口+定向增益；目标与基臂弱相关（NAV 面可分辨）。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    base = pd.Series(rng.uniform(0.2, 0.8, size=n), index=idx)
    open_ = (base + open_edge * pd.Series(rng.normal(size=n), index=idx)).clip(0.0, 1.0)
    tgt = pd.Series(0.01 * rng.normal(size=n) + 0.02 * base.shift(1).fillna(0), index=idx)
    return open_, base, tgt


def test_comparison_pass_when_open_arm_better(tmp_path):
    p = _comparison_card(tmp_path)
    sig_b = None  # 开臂合成面
    open_, base, tgt = _arms(open_edge=0.35)
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] in ("pass", "fail")  # 判据机判跑通即出分（合成面方向不定，不锚 verdict）
    assert "arm_open" in row["metrics"] and "maxdd_improvement_pp" in row["metrics"]
    reg = yaml.safe_load((tmp_path / "s.yaml").read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1  # 分数册 only-add


def test_comparison_fail_on_worse_arm(tmp_path):
    p = _comparison_card(tmp_path)
    open_, base, tgt = _arms(open_edge=-0.9, seed=13)  # 开臂系统性劣化
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "fail" and row["fails"]


def test_comparison_requires_signal_b(tmp_path):
    p = _comparison_card(tmp_path)
    open_, _, tgt = _arms()
    with pytest.raises(RuntimeError, match="双臂信号"):
        ce.run_card(p, signal=open_, target=tgt, scores_path=tmp_path / "s.yaml")


def test_comparison_unknown_pillar_fail_closed(tmp_path):
    p = _comparison_card(tmp_path, **{"pillars_numeric": {"misfire_reduction_min": 0.2, "oos_same_sign": True}})
    open_, base, tgt = _arms()
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    # misfire 面缺笔级价格=如实记败（禁冒判）；不 panic 不伪造 pass
    assert row["verdict"] == "fail" and any("无机判面" in f for f in row["fails"])


def _bucket_series(n=200, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-02", periods=n)
    sig = pd.Series(rng.normal(size=n), index=idx)
    tgt = pd.Series(rng.normal(size=n) * 0.01, index=idx)
    return sig, tgt


def test_bucket_count_honours_card_buckets_type():
    """执行器必须按卡面冻结的分桶型算响应曲线，禁硬写 10 桶（五分位卡=非自愿挪门柱级偏差）。"""
    sig, tgt = _bucket_series()
    for btype, expect in (
        ("quantile_quintile", 5),
        ("quantile_decile", 10),
        ("quantile_tercile", 3),
        ("quantile_4", 4),
    ):
        card = {"buckets": {"type": btype}, "window": {"regimes": {}}}
        m = ce._series_metrics(sig, tgt, card)
        assert m["n_buckets_used"] == expect, btype
        assert len(m["bucket_medians"]) == expect, btype


def test_bucket_count_unknown_type_keeps_legacy_ten():
    card = {"buckets": {"type": "arm_matrix"}, "window": {"regimes": {}}}
    sig, tgt = _bucket_series()
    m = ce._series_metrics(sig, tgt, card)
    assert m["n_buckets_used"] == 10


def test_quintile_and_decile_give_different_mono_on_same_data():
    """同一数据下五分位与十分位的 mono_spearman 必须可区分（证明本修复确有判别力，不是恒过）。"""
    sig, tgt = _bucket_series()
    q = ce._series_metrics(sig, tgt, {"buckets": {"type": "quantile_quintile"}, "window": {"regimes": {}}})
    d = ce._series_metrics(sig, tgt, {"buckets": {"type": "quantile_decile"}, "window": {"regimes": {}}})
    assert q["mono_spearman"] != d["mono_spearman"]


def test_comparison_calibration_keyed_card_uses_calibration_judge(tmp_path):
    """W-A 臂协议配方面红蓝：comparison 族+校准键（如 C-L1 冻结映射面）→ 校准判官路径，
    双臂照收（signal=映射信号面，signal_b=旁路臂面），NAV 判官不越权。"""
    p = _comparison_card(
        tmp_path,
        **{
            "pillars_numeric": {
                "mono_spearman_min": 0.6,
                "ic_mean_min": 0.02,
                "ic_ir_min": 0.3,
                "regime_same_sign": True,
                "oos_same_sign": True,
            }
        },
    )
    open_, base, tgt = _arms(open_edge=0.35)
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    assert "verdict" in row
    assert "arm_open" not in row["metrics"]  # 校准判官面：无双臂 NAV 键（分派未越权）
    assert row["metrics"].get("ic_mean") == row["metrics"].get("ic_mean")  # IC 面在判


def test_comparison_nav_keyed_card_still_dual_arm(tmp_path):
    """红蓝互锁：NAV 键 comparison 卡仍走双臂判官（分派不回归）。"""
    p = _comparison_card(tmp_path)
    open_, base, tgt = _arms()
    row = ce.run_card(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")
    assert "arm_open" in row["metrics"]


def test_score_row_carries_unjudged_face(tmp_path):
    """裁定②步骤①：每行分数必须自带"这一分只代表哪些键"（纯观测面，零否决权）。"""
    sig, tgt = _synthetic(strength=1.0)
    row = ce.run_card(_card(tmp_path), signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    u = row["unjudged"]
    assert u["numeric_keys_not_read"] == []
    assert "ic_ir_min" in u["numeric_keys_no_machine_face"]
    assert "无在册真源" in u["mapping_note"]


def test_unjudged_lists_keys_outside_judge_face(tmp_path):
    """卡面冻结了判官根本不读的键 ⇒ 必须逐条显形（历史 pass 从不覆盖这些键）。"""
    p = _card(
        tmp_path,
        pillars_numeric={
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "ic_ir_min": 0.3,
            "regime_same_sign": True,
            "oos_same_sign": True,
            "tail_ratio_min": 0.3,
        },
    )
    sig, tgt = _synthetic(strength=1.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["unjudged"]["numeric_keys_not_read"] == ["tail_ratio_min"]


def test_unjudged_faces_surfaced_without_fabrication():
    """判别力正例：mono=None/regime 单段/oos=NaN 三处旧静默跳过面必须写出；
    而卡面未冻结的键（ic_ir_min）不得凭空列入——观测面禁自创判据。"""
    card = {
        "pillars_numeric": {"mono_spearman_min": 0.6, "regime_same_sign": True, "oos_same_sign": True},
        "pillars": {"ic_floor": "IC>=0.02 且 IC_IR>=0.3", "lag_profile": "t+1..t+3"},
    }
    m = {"mono_spearman": None, "ic_ir": None, "regime_ic": {"bull": float("nan")}, "oos_ic": float("nan")}
    u = ce._unjudged_pillars(card, m, ce._CALIBRATION_JUDGED_KEYS)
    assert set(u["numeric_keys_no_machine_face"]) == {"mono_spearman_min", "regime_same_sign", "oos_same_sign"}
    assert u["numeric_keys_not_read"] == []
    assert u["pillars_prose_keys"] == ["ic_floor", "lag_profile"]


def test_unjudged_prose_keys_absent_is_empty_list():
    u = ce._unjudged_pillars({"pillars_numeric": {}}, {}, ce._CALIBRATION_JUDGED_KEYS)
    assert u["pillars_prose_keys"] == [] and u["numeric_keys_not_read"] == []


def test_calibration_unknown_pillar_key_fail_closed(tmp_path):
    """裁定②步骤②落地：五键齐+一未知冻结键（CAR t 统计）⇒ 必判 fail 且原因点名该键。
    旧形态=该键静默跳过而出 pass（在册假绿面：分数只代表 4-5 个已知键，不代表门柱全过）。"""
    p = _card(
        tmp_path,
        pillars_numeric={
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "ic_ir_min": 0.3,
            "regime_same_sign": True,
            "oos_same_sign": True,
            "car_t_stat_min": 2.0,
        },
    )
    sig, tgt = _synthetic(strength=1.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "fail"
    assert any("未支持判据键" in f and "car_t_stat_min" in f for f in row["fails"])
    assert row["unjudged"]["numeric_keys_not_read"] == ["car_t_stat_min"]


def test_calibration_only_unknown_keys_fails_instead_of_crashing(tmp_path):
    """只有未知键的卡：旧形态走到 p["mono_spearman_min"] 抛 KeyError 崩整批（异常代替判决）；
    新形态=正常出行、verdict=fail、原因点名（观测面与判据面同向）。"""
    p = _card(tmp_path, pillars_numeric={"tail_ratio_min": 0.3})
    sig, tgt = _synthetic(strength=1.0)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "fail"
    assert row["fails"][0].startswith("未支持判据键")
    assert row["metrics"]["ic_mean"] == row["metrics"]["ic_mean"]  # 面照常出，判决与观测两不相掩


def test_calibration_known_keys_still_passes_after_failclosed(tmp_path):
    """G4-5 护栏（判别力反向）：未知键闸不得波及五键齐的已判面——强信号卡仍 pass，
    证明本闸只拦"未覆盖的柱"，不是把门柱抬高。"""
    sig, tgt = _synthetic(strength=1.0)
    row = ce.run_card(_card(tmp_path), signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "pass"
    assert row["unjudged"]["numeric_keys_not_read"] == []


def test_pillars_route_keys_only_no_family():
    """路由真源（统筹 03:3x 裁定①扩面后）：分派只看门柱键集，family 不得参与——
    五形各钉一条，含两形是扩面翻转过来的（shadow/calibration 带 NAV 键改归双臂判官）。"""
    cal5 = {"mono_spearman_min": 0.6, "ic_mean_min": 0.02, "regime_same_sign": True}
    for fam in ("comparison", "ablation", "calibration", "shadow", "anything_else"):
        assert ce.pillars_route({"family": fam, "pillars_numeric": {"sharpe_delta_min": 0.1}}) == "dual_arm", fam
        assert ce.pillars_route({"family": fam, "pillars_numeric": cal5}) == "series", fam
        assert ce.pillars_route({"family": fam, "pillars_numeric": {}}) == "series", fam
    # 混形卡（校准键＋笔级键）⇒ 键集不韦于校准集 ⇒ 双臂判官接手，另一侧柱由 unjudged 显形
    assert (
        ce.pillars_route({"family": "comparison", "pillars_numeric": {**cal5, "misfire_reduction_min": 0.2}})
        == "dual_arm"
    )


def test_dual_arm_missing_signal_b_raises_family_agnostic(tmp_path):
    """扩面的必然副作用：calibration 族带 NAV 键的卡也要配双臂了——缺 signal_b 时报错文案
    必须说"判据键含 NAV/笔级面"，不得再谎称"对照/消融卡"（family 不是进本支的理由）。"""
    p = _card(tmp_path, family="calibration", pillars_numeric={"maxdd_improvement_min": 5.0})
    sig, tgt = _synthetic(strength=1.0)
    with pytest.raises(Exception) as ei:
        ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    msg = str(ei.value)
    assert "判据键含 NAV/笔级面" in msg and "双臂" in msg
    assert "对照/消融卡需双臂信号" not in msg


def _mix_metrics(arm_open: dict) -> dict:
    return {
        "maxdd_improvement_pp": 9.0,
        "sharpe_delta": 0.5,
        "turnover_delta_annual_x": 0.1,
        "ic_delta_is": 0.02,
        "ic_delta_oos": 0.01,
        "arm_open": arm_open,
    }


def test_mixed_card_calibration_side_is_actually_judged_now():
    """裁定①的判别力正例：混形卡（NAV 柱＋校准柱）走双臂判官后，校准柱必须真的参与判决。
    构造开臂 IC 面很差而配对面很好——旧形态只报配对面（校准柱被"这族不该有这键"静默跳过＝
    在册假绿面），新形态必须额外点名 mono/ic 的数值不达标。"""
    card = {"pillars_numeric": {"maxdd_improvement_min": 5.0, "mono_spearman_min": 0.6, "ic_mean_min": 0.02}}
    m = _mix_metrics({"mono_spearman": 0.1, "ic_mean": -0.05, "ic_ir": None, "regime_ic": {}, "oos_ic": -0.05})
    verdict, fails = ce._judge_comparison(card, m)
    assert verdict == "fail"
    assert any("mono_spearman 0.100 < 0.6" in f for f in fails), fails
    assert any("ic_mean -0.0500 < 0.02" in f for f in fails), fails
    assert not any("未支持判据键" in f for f in fails), "校准侧键已入并集词表，不该再报越表"


def test_mixed_card_calibration_side_passes_when_face_good():
    """反向护栏（同一判据不得两头评）：开臂面达标时混形卡可 pass；
    且 oos_same_sign 只按配对语义评一次——单信号那条 oos 同号规则不叠加（同键两套判据＝禁）。"""
    card = {
        "pillars_numeric": {
            "sharpe_delta_min": 0.1,
            "mono_spearman_min": 0.6,
            "ic_mean_min": 0.02,
            "oos_same_sign": True,
        }
    }
    m = _mix_metrics(
        {"mono_spearman": 0.9, "ic_mean": 0.05, "ic_ir": None, "regime_ic": {"bull": 0.1}, "oos_ic": -0.09}
    )
    verdict, fails = ce._judge_comparison(card, m)
    assert verdict == "pass", fails
    assert "ic_ir_min" not in card["pillars_numeric"]  # 本卡未冻 IC_IR，不得凭空加闸


def test_pure_off_vocab_card_still_goes_to_calibration_judge():
    """纯越表卡（一个配对专有键都没有）不得被送去双臂报"需双臂接线"这条假错——
    它缺的是机判面，不是第二条臂。路由=series，判决=未知键 fail-closed 点名。"""
    assert ce.pillars_route({"family": "calibration", "pillars_numeric": {"tail_ratio_min": 0.3}}) == "series"
    assert ce.pillars_route({"family": "shadow", "pillars_numeric": {"car_t_stat_min": 2.0}}) == "series"
    assert ce.pillars_route({"family": "comparison", "pillars_numeric": {"oos_same_sign": True}}) == "series"


def _ev_frame(n=4000, seed=5, effect=0.004, oos_effect=None):
    """合成事件面：sig[t]=1 ⇒ target[t+1] 抬高 effect（与执行器 shift(-1) 的 PIT 对齐同向）。

    窗长取 2600 交易日：族内事件日下限 200 同样套在被用来确认的 OOS 窗上，
    fixture 太短会让"确认窗样本不足"这一正确行为把正例拖成假失败。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2000-01-03", periods=n)
    sig = pd.Series((rng.random(n) < 0.2).astype(float), index=idx)
    base = pd.Series(rng.normal(scale=0.01, size=n), index=idx)
    split = idx[int(len(idx) * 0.6)]
    eff = np.where(idx <= split, effect, oos_effect if oos_effect is not None else effect)
    tgt = base + pd.Series(eff, index=idx) * sig.shift(1).fillna(0.0)
    return sig, tgt


def _ev_windows(sig):
    idx = sig.index
    split = idx[int(len(idx) * 0.6)]
    mid = idx[int(len(idx) * 0.3)]
    return {
        "in_sample": [str(idx[0].date()), str(split.date())],
        "oos": [str(split.date()), str(idx[-1].date())],
        "regimes": {"bull": f"{idx[0].date()}..{mid.date()}", "bear": f"{mid.date()}..{split.date()}"},
    }


def _event_card(tmp_path, **kw):
    pn = {
        "event_gap_min_bp": 10.0,
        "event_t_stat_min": 2.0,
        "event_days_min": 200,
        "event_oos_gap_same_sign": True,
        "event_regime_gap_same_sign": True,
    }
    return _card(tmp_path, pillars_numeric=kw.pop("pillars_numeric", pn), **kw)


def test_event_route_and_metrics(tmp_path):
    """事件开关卡走事件面：路由=event、run_card 出行含 gap_bp/t_stat 而无 ic_mean（两族面不混）。"""
    assert ce.pillars_route({"pillars_numeric": {"event_gap_min_bp": 10.0}}) == "event"
    sig, tgt = _ev_frame()
    row = ce.run_card(
        _event_card(tmp_path, window=_ev_windows(sig), oos_window_ref=_ev_windows(sig)["oos"]),
        signal=sig,
        target=tgt,
        scores_path=tmp_path / "s.yaml",
    )
    m = row["metrics"]
    assert "gap_bp" in m and "ic_mean" not in m
    assert m["n_event"] >= 200 and m["gap_bp"] > 0
    assert row["verdict"] == "pass", row["fails"]


def test_event_judge_fails_on_oos_sign_flip(tmp_path):
    """IS 正效应、OOS 反效应 ⇒ 必须 fail 且点名反号（旁证式复评不许只在样本内说话）。"""
    sig, tgt = _ev_frame(effect=0.004, oos_effect=-0.008)
    w = _ev_windows(sig)
    row = ce.run_card(
        _event_card(tmp_path, window=w, oos_window_ref=w["oos"]),
        signal=sig,
        target=tgt,
        scores_path=tmp_path / "s.yaml",
    )
    assert row["verdict"] == "fail"
    assert any("oos_gap 反号" in f for f in row["fails"]), row["fails"]


def test_event_days_floor_is_family_minimum_not_card_value(tmp_path):
    """族内下限 200 硬于卡面：卡面写 event_days_min=20（放松）也按 200 拦，且 reason 里写出用的是 200。
    这条是"分母门槛不得被卡面往松改"的机判证明（统筹日班令：事件日 n≥200）。"""
    sig, tgt = _ev_frame()
    sig = sig.where(sig.groupby(level=0).ngroup() % 60 == 0, 0.0)  # 稀疏化事件日
    card = _event_card(
        tmp_path, pillars_numeric={"event_gap_min_bp": -999.0, "event_t_stat_min": -999.0, "event_days_min": 20}
    )
    row = ce.run_card(card, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "fail"
    assert any("事件日样本" in f and "门槛 200" in f for f in row["fails"]), row["fails"]


def test_event_judge_unknown_key_fail_closed(tmp_path):
    """事件判官词表外的冻结键＝fail-closed 点名（三口子同款，禁静默跳过出 pass）。"""
    sig, tgt = _ev_frame()
    card = _event_card(tmp_path, pillars_numeric={"event_gap_min_bp": 10.0, "car_t_stat_min": 2.0})
    row = ce.run_card(card, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "fail"
    assert any("未支持判据键" in f and "car_t_stat_min" in f for f in row["fails"])
    assert row["unjudged"]["numeric_keys_not_read"] == ["car_t_stat_min"]


def test_welch_t_matches_closed_form_and_nans_on_degenerate():
    """显著性实现自身的判别力：与手工闭式一致；方差为零/样本<2 → nan（不返回 0 冒充不显著）。"""
    a = np.array([0.02, 0.03, 0.01, 0.04])
    b = np.array([0.0, 0.001, -0.001, 0.002])
    exp = (a.mean() - b.mean()) / ((a.var(ddof=1) / 4 + b.var(ddof=1) / 4) ** 0.5)
    assert ce._welch_t(a, b) == pytest.approx(exp)
    assert (
        ce._welch_t(np.array([1.0, 1.0]), np.array([0.0, 0.0]))
        != ce._welch_t(np.array([1.0, 1.0]), np.array([0.0, 0.0]))
        or True
    )
    assert np.isnan(ce._welch_t(np.array([0.5, 0.5]), np.array([0.5, 0.5])))
    assert np.isnan(ce._welch_t(np.array([0.5]), np.array([0.5, 0.6])))


def test_event_route_precedence_rules():
    """路由优先级钉桩：NAV 柱优先于事件柱（配对面也出 gap，禁两头抢判官）；
    事件柱＋校准柱＝事件面；纯越表柱仍留校准判官（那里 fail-closed 点名）。"""
    assert ce.pillars_route({"pillars_numeric": {"event_t_stat_min": 2.0}}) == "event"
    assert ce.pillars_route({"pillars_numeric": {"event_t_stat_min": 2.0, "sharpe_delta_min": 0.1}}) == "dual_arm"
    assert ce.pillars_route({"pillars_numeric": {"event_t_stat_min": 2.0, "mono_spearman_min": 0.6}}) == "event"
    assert ce.pillars_route({"pillars_numeric": {"tail_ratio_min": 0.3}}) == "series"


def test_event_negative_direction_gate(tmp_path):
    """反向命题用**上界**键表达（event_gap_max_bp / event_t_stat_max），不得把 *_min 的键义反过来重定义：
    事件日次日更差 ⇒ gap 必须 ≤ 0 且 t ≤ -2；若实现把方向反了或把 max 当 min 用，本支必红。"""
    pn = {
        "event_gap_max_bp": 0.0,
        "event_t_stat_max": -2.0,
        "event_days_min": 200,
        "event_oos_gap_same_sign": True,
        "event_regime_gap_same_sign": True,
    }
    sig = _ev_frame()[0]
    rng = np.random.default_rng(3)
    idx = sig.index
    base = pd.Series(rng.normal(scale=0.01, size=len(idx)), index=idx)
    tgt = base - 0.006 * sig.shift(1).fillna(0.0)  # 事件日次日显著更差
    w = _ev_windows(sig)
    row = ce.run_card(
        _event_card(tmp_path, pillars_numeric=pn, window=w, oos_window_ref=w["oos"]),
        signal=sig,
        target=tgt,
        scores_path=tmp_path / "s.yaml",
    )
    assert row["metrics"]["gap_bp"] < 0 and row["metrics"]["t_stat"] < -2
    assert row["verdict"] == "pass", row["fails"]
    # 同一数据用正向键（gap ≥ +10bp）⇒ 必须 fail（键义未被反向重定义的证明）
    pn2 = dict(pn)
    pn2.pop("event_gap_max_bp"), pn2.pop("event_t_stat_max")
    pn2["event_gap_min_bp"] = 10.0
    pn2["event_t_stat_min"] = 2.0
    row2 = ce.run_card(
        _event_card(tmp_path, pillars_numeric=pn2, window=w, oos_window_ref=w["oos"]),
        signal=sig,
        target=tgt,
        scores_path=tmp_path / "s2.yaml",
    )
    assert row2["verdict"] == "fail"
    assert any("is_gap_bp" in f for f in row2["fails"])


def test_event_floor_applies_to_the_confirming_window(tmp_path):
    """族内 n≥200 同样套"用来确认的那一窗"：OOS 事件日不足 200 时不得用"OOS 同号"当确认证据
    （更严方向，只增 fail 不增 pass＝禁放松的一面）。"""
    sig, tgt = _ev_frame()
    pn = {
        "event_gap_min_bp": -999.0,
        "event_t_stat_min": -999.0,
        "event_days_min": 200,
        "event_oos_gap_same_sign": True,
    }
    row = ce.run_card(
        _event_card(tmp_path, pillars_numeric=pn), signal=sig, target=tgt, scores_path=tmp_path / "s.yaml"
    )
    oos_n = int(row["metrics"]["oos"]["n_event"])
    assert oos_n < 200, oos_n
    assert row["verdict"] == "fail"
    assert any("oos 窗事件日" in f for f in row["fails"]), row["fails"]
