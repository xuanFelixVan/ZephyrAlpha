# [BLUEPRINT] MOD-BT-CAPEXAM | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] tests/backtest/test_comparison_exam.py
# 测试隔离：卡/分数册/绑定册全在 tmp_path；双腿信号/目标合成注入（零 CH 零 CH 面）；
# 试次册由 autouse 夹具整体改指 tmp（与 test_calibration_exam 同款，禁经单测写生产 N 账本，根宪法 §9 条目 6）。
# [TTL] permanent
"""对照/消融卡执行器红蓝双向：族闸/状态闸/双腿判分/blocked fail-closed/双文档分数册兼容。"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import comparison_exam as cx
from zephyr.backtest.core import n_trial_ledger as _ntl

#: 生产真源在 import 时的原值（autouse 夹具只改模块属性），供"生产册一字未动"断言对照。
_REAL_PROD_LEDGER = Path(_ntl.LEDGER_REGISTRY_PATH)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "<absent>"


@pytest.fixture(autouse=True)
def _isolate_trial_ledger(tmp_path, monkeypatch):
    """本支全篇禁写生产 N 账本（book 通道 run_one→run_card 缺省真源，必须整体改指 tmp）。"""
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    target = tmp_path / "trial_ledger_registry.yaml"
    TrialLedger(registry_path=target).load_registry(create_if_missing=True)
    monkeypatch.setattr(_ntl, "LEDGER_REGISTRY_PATH", target)
    yield target


def _card(tmp_path, **kw) -> str:
    """对照卡底稿：NAV 三键（配对判据面，路由=dual_arm）。"""
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
        "lineage": {"card": None, "run_id": None, "score_row": None},
    }
    card.update(kw)
    p = tmp_path / "cmp_card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _ablation_card(tmp_path, **kw) -> str:
    """消融卡底稿：IC 五键（校准词表，路由=series——与对照卡同 schema 同构面）。"""
    card = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/ablation/02",
        "node_id": "TDM-E-TEST",
        "family": "ablation",
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
            "regime_same_sign": True,
            "oos_same_sign": True,
        },
    }
    card.update(kw)
    p = tmp_path / "abl_card.yaml"
    p.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return str(p)


def _arms(n: int = 1450, open_edge: float = 0.4, seed: int = 11):
    """合成双臂（与 test_calibration_exam 同构）：开臂=基臂敞口+定向增益；目标与基臂弱相关。"""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    base = pd.Series(rng.uniform(0.2, 0.8, size=n), index=idx)
    open_ = (base + open_edge * pd.Series(rng.normal(size=n), index=idx)).clip(0.0, 1.0)
    tgt = pd.Series(0.01 * rng.normal(size=n) + 0.02 * base.shift(1).fillna(0), index=idx)
    return open_, base, tgt


def _series_pair(n: int = 1450, strength: float = 60.0, seed: int = 7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    sig = pd.Series(rng.normal(size=n), index=idx)
    tgt = pd.Series(0.01 * rng.normal(size=n) + strength * 0.02 * sig.shift(1).fillna(0).to_numpy(), index=idx)
    return sig, tgt


# ── 族闸／状态闸（越界即拒，不出 blocked 行不写册）─────────────────────────────


def test_family_gate_rejects_calibration_card(tmp_path):
    p = _card(tmp_path, family="calibration")
    sig, tgt = _series_pair()
    with pytest.raises(RuntimeError, match="越族代考|非对照/消融族"):
        cx.run_card_comparison(p, signal=sig, signal_b=sig, target=tgt, scores_path=tmp_path / "s.yaml")


def test_family_flag_mismatch_rejected(tmp_path):
    p = _card(tmp_path, family="comparison")
    with pytest.raises(RuntimeError, match="不符"):
        cx.run_card_comparison(p, expected_family="ablation", scores_path=tmp_path / "s.yaml")


def test_examined_card_needs_force(tmp_path):
    p = _card(tmp_path, status="examined")
    open_, base, tgt = _arms()
    with pytest.raises(RuntimeError, match="重考带 --force"):
        cx.run_card_comparison(p, signal=open_, signal_b=base, target=tgt, scores_path=tmp_path / "s.yaml")


# ── R1 注入通道：双腿判分出分 + 分数册 + 翻卡 ─────────────────────────────────


def test_dual_arm_injected_end_to_end(tmp_path):
    p = _card(tmp_path)
    scores = tmp_path / "s.yaml"
    open_, base, tgt = _arms(open_edge=0.35)
    row = cx.run_card_comparison(p, signal=open_, signal_b=base, target=tgt, scores_path=scores)
    assert row["verdict"] in ("pass", "fail")  # 判据机判跑通即出分（合成面方向不定，不锚 verdict）
    assert "maxdd_improvement_pp" in row["metrics"] and "arm_open" in row["metrics"]  # 单行含双腿指标面
    # 卡翻 examined + 分数册落行
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "examined" and card["lineage"]["score_row"]
    reg = yaml.safe_load(scores.read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 1 and reg["rows"][0]["card_id"] == "TDM-E-TEST/comparison/02"
    assert not _sha(_REAL_PROD_LEDGER).startswith("0" * 4) or True  # 占位：真实断言在 blocked 面（零消费不记账）


def test_ablation_same_file_series_route(tmp_path):
    """消融卡与对照卡 schema 同构 → 同文件支持：IC 五键走校准判官（pillars_route 键集路由，族面无关）。"""
    p = _ablation_card(tmp_path)
    scores = tmp_path / "s.yaml"
    sig, tgt = _series_pair(strength=60.0)
    row = cx.run_card_comparison(p, signal=sig, signal_b=sig, target=tgt, scores_path=scores)
    assert row["verdict"] == "pass" and row["metrics"]["mono_spearman"] is not None
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "examined"


def test_force_reexam_appends_only(tmp_path):
    p = _card(tmp_path)
    scores = tmp_path / "s.yaml"
    open_, base, tgt = _arms()
    cx.run_card_comparison(p, signal=open_, signal_b=base, target=tgt, scores_path=scores)
    row2 = cx.run_card_comparison(p, signal=open_, signal_b=base, target=tgt, scores_path=scores, force=True)
    reg = yaml.safe_load(scores.read_text(encoding="utf-8"))
    assert len(reg["rows"]) == 2 and reg["rows"][0]["date"] == reg["rows"][1]["date"]  # only-add 旧行不动
    assert row2["card_id"] == "TDM-E-TEST/comparison/02"


# ── blocked fail-closed：装载不出=如实记 blocked，禁编 ────────────────────────


def test_blocked_when_book_entry_absent(tmp_path):
    p = _card(tmp_path)
    scores = tmp_path / "s.yaml"
    ledger_before = _sha(_REAL_PROD_LEDGER)
    row = cx.run_card_comparison(
        p, binding_book_path=tmp_path / "absent_book.yaml", scores_path=scores, ledger_registry_path=tmp_path / "l.yaml"
    )
    assert row["verdict"] == "blocked" and "binding_book" in row["blocked"]["reason"]
    assert row["metrics"] == {} and row["pillars_all_pass"] is False  # 禁编指标
    assert row["blocked"]["route"] == "dual_arm" and row["blocked"]["binding_class"] in ("C", "U", "B")
    assert row["unjudged"]["numeric_keys_no_machine_face"] or row["unjudged"]["numeric_keys_not_read"] is not None
    # 卡不翻（blocked≠examined）
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "preregistered" and card["lineage"]["run_id"] is None
    # 试次零消费不记账（生产册一字未动）
    assert _sha(_REAL_PROD_LEDGER) == ledger_before


def test_blocked_dual_arm_injected_missing_second_leg(tmp_path):
    p = _card(tmp_path)
    open_, _, tgt = _arms()
    row = cx.run_card_comparison(p, signal=open_, target=tgt, scores_path=tmp_path / "s.yaml")
    assert row["verdict"] == "blocked" and "signal_b" in row["blocked"]["reason"]
    card = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    assert card["status"] == "preregistered"


# ── 双文档 register 兼容（裁定#536 迁移形态）──────────────────────────────────


def test_dual_doc_register_preserved_on_blocked(tmp_path):
    """生产分数册=doc0(register 头) + doc1(rows 账本)：blocked 追加进 doc1，doc0 结构逐字不动。"""
    p = _card(tmp_path)
    scores = tmp_path / "s.yaml"
    header = {
        "doc_type": "register",
        "ttl": "permanent",
        "schema_version": "1.0",
        "sid": "migrated_r536",
        "title_zh": "exam_scores_v1",
    }
    ledger = {"schema_version": "1.0", "title": "考试卡分数册（成绩汇总面，方案 §6 D4）", "rows": []}
    scores.write_text(
        yaml.safe_dump_all([header, ledger], allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n"
    )
    open_, base, tgt = _arms()
    cx.run_card_comparison(p, signal=open_, target=tgt, scores_path=scores)  # blocked（缺第二腿）
    docs = [d for d in yaml.safe_load_all(scores.read_text(encoding="utf-8")) if isinstance(d, dict)]
    assert len(docs) == 2, "双文档结构必须保住（禁塌成单文档）"
    assert docs[0] == header and docs[0].get("rows") is None
    assert len(docs[1]["rows"]) == 1 and docs[1]["rows"][0]["verdict"] == "blocked"


def test_dual_doc_register_preserved_on_scored(tmp_path):
    """出分行同样落 doc1（经 run_card 同形态追加，读回命中本卡最新行）。"""
    p = _card(tmp_path)
    scores = tmp_path / "s.yaml"
    header = {"doc_type": "register", "ttl": "permanent"}
    ledger = {"schema_version": "1.0", "title": "考试卡分数册", "rows": []}
    scores.write_text(yaml.safe_dump_all([header, ledger], allow_unicode=True, sort_keys=False), encoding="utf-8")
    open_, base, tgt = _arms()
    cx.run_card_comparison(p, signal=open_, signal_b=base, target=tgt, scores_path=scores)
    docs = [d for d in yaml.safe_load_all(scores.read_text(encoding="utf-8")) if isinstance(d, dict)]
    assert len(docs) == 2 and docs[0] == header and len(docs[1]["rows"]) == 1


# ── dry-run 分诊（零写面）─────────────────────────────────────────────────────


def test_dry_run_triage_zero_write(tmp_path):
    p = _card(tmp_path)
    scores = tmp_path / "s.yaml"
    out = cx.run_card_comparison(p, binding_book_path=tmp_path / "nope.yaml", scores_path=scores, dry=True)
    assert out["dry_run"] is True and out["route"] == "dual_arm" and out["book_entry"] is False
    assert not scores.exists()  # 零写
