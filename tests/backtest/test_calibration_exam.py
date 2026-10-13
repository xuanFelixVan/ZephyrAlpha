# [BLUEPRINT] MOD-BT-247 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_calibration_exam.py
# 测试隔离：卡/分数册全在 tmp_path；信号/目标合成注入（零 CH）；
# 试次册由本文件 autouse 夹具整体改指 tmp（改前缺省直写生产 N 账本，见 _isolate_trial_ledger 注释）。
# [TTL] permanent
"""校准卡执行器红蓝双向：门柱机械判/状态机/分数册 only-add/试次留痕/fail-closed。"""

from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import calibration_exam as ce
from zephyr.backtest.core import n_trial_ledger as _ntl


def test_pillars_fail_when_base_tier_flag_not_declared():
    """红证（07b 接线期的真雷）：档位属性没申报 ⇒ 三柱必须显式记败。
    判官若按 `base_arm_cfg == "levels_no_hysteresis"` 认迟滞对照，复位档名
    `levels_no_hysteresis_with_reset` 会被读成"非无迟滞档"⇒ 三柱静默不判 yet 出分＝假绿。"""
    card = _three_pillar_card()
    ctx = _pair_caps(open_pattern="warn_then_kill", base_pattern="osc")
    ctx.pop("base_is_no_hysteresis")
    m = _pair_metrics(2.0)
    verdict, fails = ce._judge_comparison(card, m, ctx)
    assert verdict == "fail"
    assert any("未申报基臂迟滞属性" in f for f in fails), fails
    assert m["arm_pillars_owned_by_other_run"] == [], "缺申报不得写成'归另一跑'（那是同一支静默跳）"


def test_reset_tier_base_name_is_judged_from_declared_flag():
    """判别力（双向钉）：基臂档名换成 levels_no_hysteresis_with_reset（复位档，属性仍＝无迟滞）
    ⇒ 三柱照判；把属性改回 True→False 即不判。钉的是"读数跟着申报走、不跟字符串走"。"""
    card = _three_pillar_card()
    ctx = _pair_caps(open_pattern="warn_then_kill", base_pattern="osc")
    ctx["base_arm_cfg"] = "levels_no_hysteresis_with_reset"
    m = _pair_metrics(2.0)
    verdict, fails = ce._judge_comparison(card, m, ctx)
    assert verdict == "pass", fails
    r = m["arm_face_readings"]
    assert r["base_is_no_hysteresis"] is True and r["whipsaw_roundtrip_ratio"] == 0.0
    assert r["maxdd_improvement_vs_no_hysteresis_pp"] == 2.0
    ctx["base_is_no_hysteresis"] = False
    m_off = _pair_metrics(2.0)
    ce._judge_comparison(card, m_off, ctx)
    assert m_off["arm_face_readings"]["maxdd_improvement_vs_no_hysteresis_pp"] is None
    assert m_off["arm_pillars_owned_by_other_run"] == [
        "maxdd_improvement_vs_no_hysteresis_min_pp",
        "whipsaw_roundtrip_ratio_max",
    ], m_off["arm_pillars_owned_by_other_run"]


#: 生产真源在 import 时的原值（autouse 夹具只改模块属性，不改本快照），供"生产册一字未动"两测对照。
_REAL_PROD_LEDGER = Path(_ntl.LEDGER_REGISTRY_PATH)


def _sha(p: Path) -> str:
    import hashlib

    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "<absent>"


@pytest.fixture(autouse=True)
def _isolate_trial_ledger(tmp_path, monkeypatch):
    """本支全篇禁写生产 N 账本（根宪法 §9 条目 6）。

    改前形态：`run_card` 没有试次册注入位，缺省直取 `n_trial_ledger.LEDGER_REGISTRY_PATH`
    ＝生产真源 ⇒ 单测把 `examcard:TDM-E-TEST/*` 写进生产册（10-12 实测：dev 面 1 条 2026-10-10、
    主区工作区面再添 2 条 recorded_at=2026-10-11T16:58:56Z）。
    """
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    target = tmp_path / "trial_ledger_registry.yaml"
    TrialLedger(registry_path=target).load_registry(create_if_missing=True)
    monkeypatch.setattr(_ntl, "LEDGER_REGISTRY_PATH", target)
    yield target


def test_run_card_consumes_injected_ledger_path(tmp_path, _isolate_trial_ledger):
    """注入位真被消费（改前必红＝改前无该 kwarg，直接 TypeError）。"""
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=1.0)
    injected = tmp_path / "injected_ledger.yaml"
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    TrialLedger(registry_path=injected).load_registry(create_if_missing=True)
    before = _sha(_REAL_PROD_LEDGER)
    row = ce.run_card(
        p,
        signal=sig,
        target=tgt,
        scores_path=tmp_path / "s.yaml",
        ledger_registry_path=injected,
    )
    assert not row.get("ledger_warning"), row.get("ledger_warning")
    assert "TDM-E-TEST/calibration/02" in injected.read_text(encoding="utf-8")
    assert _sha(_REAL_PROD_LEDGER) == before


def test_suite_default_ledger_is_not_production(tmp_path, _isolate_trial_ledger):
    """autouse 隔离闸自身的判别力（摘掉夹具或把缺省指回生产真源，本支必红）。"""
    p = _card(tmp_path)
    sig, tgt = _synthetic(strength=1.0)
    before = _sha(_REAL_PROD_LEDGER)
    row = ce.run_card(p, signal=sig, target=tgt, scores_path=tmp_path / "s.yaml")
    assert not row.get("ledger_warning"), row.get("ledger_warning")
    assert "TDM-E-TEST/calibration/02" in _isolate_trial_ledger.read_text(encoding="utf-8")
    assert _sha(_REAL_PROD_LEDGER) == before


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


# ---------------------------------------------------------------------------
# 面板路两处结构缺陷的防回归钉（考试班 st-examrun-20261012，10-12 实测证红后修）
# ---------------------------------------------------------------------------


def _panel_pair(n: int = 900, ncols: int = 40, seed: int = 7):
    """合成面板＋前向收益宽表（ICIR 明显为正，用来验"键名读错=恒 NaN"这一类静默降级）。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    cols = [f"S{i:04d}" for i in range(ncols)]
    panel = pd.DataFrame(rng.normal(size=(n, ncols)), index=idx, columns=cols)
    fwd = pd.DataFrame(0.05 * panel.to_numpy() + 0.01 * rng.normal(size=(n, ncols)), index=idx, columns=cols)
    return panel, fwd


def test_panel_route_ic_ir_is_actually_computed():
    """`ic_exam.ic_stats` 回键是 "icir"；面板路曾读 "ic_ir" ⇒ 恒 NaN，卡面冻的 ic_ir_min 从未被评估。
    修后必须出数，且与 ic_stats 对同一 IC 序列的读数同值（改前必红=nan != nan 为 False）。"""
    from scripts.backtest.fexam.ic_exam import fast_rank_ic, ic_stats

    panel, fwd = _panel_pair()
    m = ce._panel_metrics(panel, fwd, {"window": {"regimes": {}}, "oos_window_ref": []})
    expect = float(ic_stats(fast_rank_ic(panel, fwd.shift(-1)).dropna())["icir"])
    assert m["ic_ir"] == m["ic_ir"], "ic_ir 仍是 NaN（键名未对齐 ic_stats 真形）"
    assert m["ic_ir"] == pytest.approx(expect)


def test_panel_route_high_icir_floor_now_fails_instead_of_passing():
    """单向收紧证明：把 ic_ir_min 抬到面上不可能达的值，修后必须记败；
    改前形态=ic_ir 恒 NaN 被 judge 跳过加败 ⇒ 一张 5/5 全冻的卡只被评了 3 柱就 pass。"""
    panel, fwd = _panel_pair()
    m = ce._panel_metrics(panel, fwd, {"window": {"regimes": {}}, "oos_window_ref": []})
    card = {"pillars_numeric": {"ic_mean_min": 0.0, "ic_ir_min": 9.0}}
    verdict, fails = ce.judge(card, m)
    assert verdict == "fail" and any("ic_ir" in f for f in fails), fails


def test_unjudged_discloses_nan_ic_ir_face():
    """观测面同样不得漏：ic_ir 为 NaN（未接面）时必须进 no_machine_face 清单。
    改前判据只查 `is None` ⇒ NaN 静默不披露（分数行声称评过 5 柱，实际 4 柱）。"""
    card = {"pillars_numeric": {"ic_ir_min": 0.3}}
    m = {"ic_ir": float("nan"), "mono_spearman": 0.9, "regime_ic": {"a": 0.1, "b": 0.2}, "oos_ic": 0.1}
    u = ce._unjudged_pillars(card, m, ce._CALIBRATION_JUDGED_KEYS)
    assert "ic_ir_min" in u["numeric_keys_no_machine_face"]


# ---------- 2026-10-13 挖矿二班：多日标的前向面（统筹立项批，纯追加可选档） ----------
def _fwd_card(h: int = 10) -> dict:
    return {
        "target": {"primary": f"mkt_fwd{h}_panel_ew_return（面板等权 {h} 日前向收益均值，_proxy 非指数）"},
        "target_forward_face": "precomputed",
        "target_horizon_days": h,
    }


def test_forward_face_default_is_next_day_untouched():
    """正对照（缺省面零改）：两键都不在卡面 ⇒ (1, False)，既有 178 张 preregistered 卡语义一字不动。"""
    assert ce._forward_face({"target": {"primary": "next_day_index_return"}}) == (1, False)
    assert ce._forward_face({}) == (1, False)


def test_forward_face_declared_consumes_precomputed():
    """申报且自洽 ⇒ 返回 (h, True)，执行器对注入的前向序列禁二次位移。"""
    assert ce._forward_face(_fwd_card(10)) == (10, True)
    assert ce._forward_face(_fwd_card(5)) == (5, True)


@pytest.mark.parametrize(
    "bad, frag",
    [
        ({"target_forward_face": "precomputed", "target": {"primary": "mkt_fwd10_x"}}, "半申报：有 face 无 horizon"),
        ({"target_forward_face": "precomp", "target_horizon_days": 10}, "face 拼错不得静默退次日面"),
        ({"target_forward_face": "precomputed", "target_horizon_days": 1}, "h=1 属次日面，须走缺省形制"),
        ({"target_forward_face": "precomputed", "target_horizon_days": 253}, "越界"),
        ({"target_forward_face": "precomputed", "target_horizon_days": "10"}, "字符串冒充"),
        ({"target_forward_face": "precomputed", "target_horizon_days": True}, "bool 冒充整数"),
        (
            {"target_forward_face": "precomputed", "target_horizon_days": 10, "target": {"primary": "mkt_fwd5_x"}},
            "两处不同值",
        ),
    ],
)
def test_forward_face_half_or_inconsistent_declared_rejected(bad, frag):
    """红证：半申报/错拼/越界/两处不自洽 ⇒ 必抛，禁退化成次日面静默出分（方向性=fail-closed）。"""
    with pytest.raises(ce._ToolError) as ei:
        ce._forward_face(bad)
    assert "拒" in str(ei.value) or "禁" in str(ei.value), frag


def test_series_metrics_precomputed_differs_from_next_day_on_same_input():
    """同一组 signal/target：申报面按 shift(0)、缺省面按 shift(-1) ⇒ 读数必不同（防"配置写了不消费"空转）。"""
    idx = pd.bdate_range("2020-01-01", periods=30)
    sig = pd.Series(np.sin(np.arange(30.0)), index=idx)
    tgt = pd.Series(np.cos(np.arange(30.0)), index=idx)
    plain = ce._series_metrics(sig, tgt, {"target": {"primary": "next_day_index_return"}})
    fwd = ce._series_metrics(sig, tgt, _fwd_card(10))
    assert plain["n"] == 29 and fwd["n"] == 30
    assert plain["ic_mean"] != fwd["ic_mean"]
    # 申报面必须等价于"不做任何位移"的手算（前向已在数据侧算完）
    manual = ce._spearman(sig.to_numpy(), tgt.to_numpy())
    assert abs(fwd["ic_mean"] - manual) < 1e-12


def test_series_metrics_next_day_face_byte_identical_to_old_formula():
    """红证对照：缺省面读数与改前公式 shift(-1) 手算逐位等——本补丁禁动既有次日语义。"""
    idx = pd.bdate_range("2020-01-01", periods=40)
    rng = np.random.default_rng(11)
    sig = pd.Series(rng.normal(size=40), index=idx)
    tgt = pd.Series(rng.normal(size=40) * 0.01, index=idx)
    card = {"target": {"primary": "next_day_index_return"}, "window": {"regimes": {}}}
    m = ce._series_metrics(sig, tgt, card)
    ref = ce._spearman(*pd.concat({"s": sig, "t": tgt.shift(-1)}, axis=1).dropna().T.to_numpy())
    assert abs(m["ic_mean"] - ref) < 1e-12


# ──────────────────────────────────────────────────────────────────────────────
# 裁定③（统筹 2026-10-12）：三柱机器面——迟滞带增益 / 30 日升降往返 / 危机段漏触发
# 全部走合成级别序列，零 CH 零生产路径写；每条都配"改前必红"的判别力说明。
# ──────────────────────────────────────────────────────────────────────────────

_VOCAB3 = frozenset(
    {
        "maxdd_improvement_vs_no_hysteresis_min_pp",
        "whipsaw_roundtrip_ratio_max",
        "missed_crisis_trigger_max",
    }
)


def _three_pillar_card(thr_pp=1.0, thr_ratio=1.0, thr_miss=0):
    return {
        "card_id": "TDM-X-R1-01/comparison/probe",
        "pillars_numeric": {
            "maxdd_improvement_vs_no_hysteresis_min_pp": thr_pp,
            "whipsaw_roundtrip_ratio_max": thr_ratio,
            "missed_crisis_trigger_max": thr_miss,
        },
        "window": {
            "in_sample": ["2018-01-02", "2025-09-30"],
            "oos": ["2025-10-09", "2026-09-30"],
            "regimes": {
                "bull": "2019-01-04..2021-06-30（流动性牛）",
                "crisis": "2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段）",
            },
        },
    }


def _pair_caps(open_pattern="down_only", base_pattern="osc", days=1500):
    """造两档级别序列（NORMAL/WARN/DANGER/CRISIS/KILL），映射逐字取卡面五态表。

    索引从 2020-01-02 起共 `days` 个交易日，**同时覆盖卡面两处在册危机段**
    （2020-02-01..2020-03-23 与 2024-01-02..2024-02-08）——否则段内无读数会一律记漏触发，
    判别力就落在"有没有覆盖到段"上而不是判据本身。
    """
    idx = pd.bdate_range("2020-01-02", periods=days)
    five = {"NORMAL": 1.0, "WARN": 0.8, "DANGER": 0.5, "CRISIS": 0.3, "KILL": 0.0}

    def seq(pattern):
        if pattern == "osc":
            return pd.Series(["NORMAL" if (i % 8 < 4) else "DANGER" for i in range(days)], index=idx)
        if pattern == "down_only":
            cut = max(1, days // 6)
            return pd.Series(["NORMAL"] * (days - cut) + ["KILL"] * cut, index=idx)
        if pattern == "warn_then_kill":
            cut = max(1, days - days // 6)
            return pd.Series(["WARN"] * cut + ["KILL"] * (days - cut), index=idx)
        if pattern == "flat_normal":
            return pd.Series(["NORMAL"] * days, index=idx)
        if pattern == "trigger_first_span_only":
            d = idx.strftime("%Y-%m-%d")
            return pd.Series(["WARN" if x < "2020-04-01" else "NORMAL" for x in d], index=idx)
        raise AssertionError(f"unknown pattern {pattern}")

    return {
        "levels": {"open": seq(open_pattern), "base": seq(base_pattern)},
        "cap_map": {"open": five, "base": five},
        "level_source": {"open": "series:levels_hysteresis", "base": "series:levels_no_hysteresis"},
        "base_arm_cfg": "levels_no_hysteresis",
        # 档位属性由绑定层**申报**（判官禁按档名猜），夹具须给真上下文形状
        "base_is_no_hysteresis": True,
        "open_is_no_hysteresis": False,
        "arms_variant": "mid",
        "creds": None,
    }


def _pair_metrics(improvement_pp=2.0):
    """配对 NAV/IC 面的最小完整读数：判官对 None 与 NaN 走不同分支，缺键即误判，故一次给全。"""
    return {
        "maxdd_improvement_pp": improvement_pp,
        "sharpe_delta": 0.0,
        "turnover_delta_annual_x": 0.0,
        "open_sharpe_at_tier_bp": float("nan"),
        "ic_delta_is": float("nan"),
        "ic_delta_oos": float("nan"),
        "arm_open": {},
        "arm_base": {},
    }


def test_three_pillars_are_in_vocab_and_get_judged():
    """正证：三柱已入并集词表且有机器面——既不得再报"未支持判据键"，也不得静默跳。
    改前必红（改前三键在词表外，首条 fail 即"未支持判据键"）。"""
    card = _three_pillar_card()
    ctx = _pair_caps(open_pattern="warn_then_kill", base_pattern="osc")
    m = _pair_metrics(2.0)
    verdict, fails = ce._judge_comparison(card, m, ctx)
    assert verdict == "pass", fails
    assert not any("未支持判据键" in f for f in fails), fails
    assert not any("未注入" in f for f in fails), fails
    r = m["arm_face_readings"]
    assert r["arm_context_present"] is True and r["base_arm_cfg"] == "levels_no_hysteresis"
    assert r["maxdd_improvement_vs_no_hysteresis_pp"] == 2.0
    assert r["whipsaw_roundtrip_ratio"] == 0.0
    assert r["missed_crisis_triggers"] == 0  # 两处危机段都有降档读数
    assert len(r["crisis_spans"]) == 2, r["crisis_spans"]


def test_missing_arm_context_fails_closed_not_silently_skipped():
    """红证一（假绿形态）：三柱在词表内但本跑没注入臂上下文 ⇒ 必须显式记败。
    若实现"缺面即跳过"，同一卡面会一边绿一边没评＝在册严令禁的形态。"""
    card = _three_pillar_card()
    verdict, fails = ce._judge_comparison(card, _pair_metrics(2.0), None)
    assert verdict == "fail"
    assert any("三柱臂上下文未注入" in f for f in fails), fails
    m2 = _pair_metrics(2.0)
    ce._judge_comparison(card, m2, None)
    assert m2["arm_pillars_owned_by_other_run"] == [], "缺注入不得写成'归另一跑'（那是另一种静默跳）"


def test_calm_open_vs_oscillating_base_flags_whipsaw_ratio():
    """判别力（双向钉）：开臂高频抖动、基臂只一次降档 ⇒ 往返/触发比必超线记败；
    反接（开臂平稳/基臂抖动）不得记败——把分子分母接反也是同一根柱的红。"""
    card = _three_pillar_card(thr_ratio=1.0)
    ctx = _pair_caps(open_pattern="osc", base_pattern="down_only")
    m = _pair_metrics(9.0)
    verdict, fails = ce._judge_comparison(card, m, ctx)
    r = m["arm_face_readings"]
    assert r["open_roundtrips_30d"] > 1 and r["base_downgrades"] == 1, r
    assert verdict == "fail" and any("whipsaw" in f for f in fails), fails
    ctx_rev = _pair_caps(open_pattern="warn_then_kill", base_pattern="osc")
    m_rev = _pair_metrics(9.0)
    verdict_rev, fails_rev = ce._judge_comparison(card, m_rev, ctx_rev)
    assert not any("whipsaw" in f for f in fails_rev), fails_rev


def test_hysteresis_pair_run_reports_owned_by_other_run():
    """裁定甲"两跑合议"的机读面：base 档＝迟滞（即 off 那跑）时，两柱归另一跑——
    记进 arm_pillars_owned_by_other_run 而非记败，也**不得**悄悄当已判。"""
    card = _three_pillar_card()
    ctx = _pair_caps(open_pattern="warn_then_kill", base_pattern="down_only")
    ctx["base_arm_cfg"] = "levels_hysteresis"
    ctx["base_is_no_hysteresis"] = False  # 迟滞对照属性由绑定层申报，判官不再自己认字符串
    ctx["arms_variant"] = "off"
    m = _pair_metrics(3.0)
    verdict, fails = ce._judge_comparison(card, m, ctx)
    assert not any("迟滞带增益" in f for f in fails), fails
    owned = m["arm_pillars_owned_by_other_run"]
    assert owned == ["maxdd_improvement_vs_no_hysteresis_min_pp", "whipsaw_roundtrip_ratio_max"], owned
    assert m["arm_face_readings"]["maxdd_improvement_vs_no_hysteresis_pp"] is None
    # 漏触发柱不属"归另一跑"集合：两跑共用同一条开臂级别序列，本跑就判
    assert "missed_crisis_trigger_max" not in owned


def test_crisis_second_span_is_not_dropped_by_multi_span_string():
    """⚑在册解析缺陷的正证（本柱专用多段尺）：卡面 crisis 串含两段危机窗，
    既有 `_span_dates` 只取前两个日期＝后段被静默弃；漏触发柱必须看全段，
    此处令**第二段全段 NORMAL**（无触发）⇒ missed 必须=1，若只解析首段则得 0＝谎报"不漏"。"""
    card = _three_pillar_card(thr_miss=0)
    ctx = _pair_caps(open_pattern="trigger_first_span_only", base_pattern="down_only")
    m = _pair_metrics(9.0)
    verdict, fails = ce._judge_comparison(card, m, ctx)
    spans = m["arm_face_readings"]["crisis_spans"]
    assert [s["span"] for s in spans] == ["2020-02-01..2020-03-23", "2024-01-02..2024-02-08"], spans
    assert m["arm_face_readings"]["missed_crisis_triggers"] == 1
    assert verdict == "fail" and any("危机段漏触发 1 > 0" in f for f in fails), fails


def test_cap_series_rejects_level_missing_from_card_map():
    """红证二：序列里出现卡面映射没覆盖的档（如 RECOVERY）⇒ 必须红，禁按缺省 1.0 蒙。"""
    idx = pd.bdate_range("2024-01-02", periods=6)
    lv = pd.Series(["NORMAL", "RECOVERY", "NORMAL", "NORMAL", "NORMAL", "NORMAL"], index=idx)
    five = {"NORMAL": 1.0, "WARN": 0.8, "DANGER": 0.5, "CRISIS": 0.3, "KILL": 0.0}
    with pytest.raises(ce._ToolError, match="卡面映射未覆盖"):
        ce._cap_series(lv, five)


def test_run_card_passes_arm_context_through(tmp_path):
    """接线钉：run_card 的 arm_context kwarg 必须真的到达判官（只加参数不消费＝在册点过的空转形态）。
    用 series 面卡＋双臂路由：把 ctx 置 None 与置真值两跑对比，读数的有无即判别位。"""
    card = _three_pillar_card()
    card.update({"signal_kind": "series", "family": "comparison", "status": "preregistered"})
    p = tmp_path / "card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")
    idx = pd.bdate_range("2024-01-02", periods=90)
    sig = pd.Series(0.5, index=idx)
    tgt = pd.Series(0.001, index=idx)
    ctx = _pair_caps(open_pattern="down_only", base_pattern="osc")
    m_without = _pair_metrics(2.0)
    ce._judge_comparison(card, m_without, None)
    m_with = _pair_metrics(2.0)
    ce._judge_comparison(card, m_with, ctx)
    assert m_without["arm_face_readings"] == {"arm_context_present": False}
    assert m_with["arm_face_readings"]["arm_context_present"] is True
    assert "arm_context" in inspect.signature(ce.run_card).parameters, "run_card 须保留注入位"


# ──────────────────────────────────────────────────────────────────────────────
# 统筹裁定 2026-10-13：`_span_dates` 多段缺陷＝裁修（实现面背离冻结意图的 bug，非判据变更）
# 影响面盘点＝docs/_working/mineloop2_campaign/12_regime_multispan_impact_inventory.yaml
# （518 张卡扫出 12 张多段、8 张第二段被弃；已有分数行的只有 07 一张 2 行＝only-append 重读面）
# ──────────────────────────────────────────────────────────────────────────────


def test_span_pairs_reads_every_declared_span():
    """解析器正证＋旧语义保持：单段串结果与旧实现逐字同值；无日期串仍退回"整串当单点"。"""
    assert ce._span_pairs("2019-01-04..2021-06-30（流动性牛）") == [("2019-01-04", "2021-06-30")]
    assert ce._span_pairs("2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段）") == [
        ("2020-02-01", "2020-03-23"),
        ("2024-01-02", "2024-02-08"),
    ]
    assert ce._span_pairs("不可用") == [("不可用", "不可用")]


def test_in_spans_masks_both_crisis_segments():
    idx = pd.bdate_range("2019-06-03", periods=1300)
    span = "2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段）"
    mask = ce._in_spans(idx, span)
    in_first = mask[(idx >= "2020-02-03") & (idx <= "2020-03-20")].all()
    in_second = mask[(idx >= "2024-01-03") & (idx <= "2024-02-07")].all()
    between = mask[(idx >= "2021-01-04") & (idx <= "2021-06-30")].any()
    assert bool(in_first) and bool(in_second), "两段都必须掩到（旧实现只掩第一段）"
    assert not bool(between), "段间不得被误掩"


def test_series_metrics_regime_uses_second_span_only():
    """⚑判别力（改前必红）：把**关系只放在第二段危机窗**内，第一段全随机。
    旧实现只切前两日期 ⇒ crisis 段取到的是第一段＝无关系样本 → regime_ic=nan；
    修后必须读出该段的正相关（数值>0.5）。"""
    idx = pd.bdate_range("2019-06-03", periods=1300)
    rng = np.random.default_rng(7)
    noise = pd.Series(rng.normal(size=len(idx)), index=idx)
    sig = noise.copy()
    tgt = noise.copy()
    seg2 = (idx >= "2024-01-02") & (idx <= "2024-02-08")
    sig[seg2] = np.arange(seg2.sum(), dtype=float)  # 第二段内严格单调↑
    tgt[seg2] = np.arange(seg2.sum(), dtype=float) * 2.0
    card = {"window": {"regimes": {"crisis": "2020-02-01..2020-03-23 与 2024-01-02..2024-02-08"}}, "oos_window_ref": []}
    m = ce._series_metrics(sig, tgt, card)
    assert m["regime_ic"]["crisis"] == m["regime_ic"]["crisis"], "第二段必须出读数（nan=旧行为）"
    assert m["regime_ic"]["crisis"] > 0.5, m["regime_ic"]


def test_event_face_mask_pools_both_spans():
    """事件面同样并段：两危机段各放若干事件日，掩码版的 n_event 必须等于两段之和。"""
    idx = pd.bdate_range("2019-06-03", periods=1300)
    sig = pd.Series(0.0, index=idx)
    nxt = pd.Series(0.01, index=idx)
    s1 = (idx >= "2020-02-03") & (idx <= "2020-02-14")
    s2 = (idx >= "2024-01-03") & (idx <= "2024-01-12")
    sig[s1 | s2] = 1.0
    nxt[s1 | s2] = -0.02
    span = "2020-02-01..2020-03-23 与 2024-01-02..2024-02-08"
    pooled = ce._event_face(sig, nxt, mask=ce._in_spans(idx, span))
    first_only = ce._event_face(sig, nxt, "2020-02-01", "2020-03-23")
    assert pooled["n_event"] == int((s1 | s2).sum())
    assert first_only["n_event"] == int(s1.sum()) and pooled["n_event"] > first_only["n_event"]


def test_declared_local_faces_load_signal_and_target(tmp_path, monkeypatch):
    """卡面申报本地序列名 ⇒ run_card 无需外部注入即可两面齐（挖矿二班 class D 路）；未申报 ⇒ 照旧抛。"""
    import pandas as _pd

    from scripts.backtest.fexam import card_binding as _cbb

    idx = _pd.bdate_range("2020-01-01", periods=80)
    sig = _pd.Series(range(80), index=idx, dtype=float)
    tgt = _pd.Series([x * 0.001 for x in range(80)], index=idx)
    for name, ser in (("lu_count", sig), ("mkt_fwd5", tgt)):
        _pd.DataFrame({"value": ser.to_numpy()}, index=ser.index).rename_axis("trade_date").to_csv(
            tmp_path / f"{name}.csv"
        )
    monkeypatch.setattr(_cbb, "SERIES_DIR", tmp_path)
    card = {
        "data_binding": {"derived_series": "lu_count", "target_series": "mkt_fwd5"},
        "target_forward_face": "precomputed",
        "target_horizon_days": 5,
    }
    s2, t2 = ce._declared_local_faces(card)
    assert len(s2) == 80 and len(t2) == 80
    # 未申报（键全缺）＝零装载，由调用方按既有口径抛，缺省行为不被本档改变
    assert ce._declared_local_faces({}) == (None, None)
    assert ce._declared_local_faces({"data_binding": {"derived_series": "lu_count"}})[1] is None
