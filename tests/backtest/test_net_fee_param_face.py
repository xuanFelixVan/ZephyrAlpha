# [BLUEPRINT] MOD-BT-242 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_net_fee_param_face
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.fexam.calibration_exam; config/exam_scale_cost_gate.yaml;
#   scripts/backtest/translated/_c4_engine.py（只读源码取常量，禁 import——引擎带重依赖）
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 全合成数据零 CH 零 DB 零写生产路径（宪法 §9.6 测试隔离，落盘只进 tmp_path）;
#   net_fee 节唯一参数面=config/exam_scale_cost_gate.yaml（禁双头硬编码，裁定#506）;
#   本节数值必须等于引擎冻结土规常数的组合解 2.5*2+10.0+5.0*2=25.0（与 _c4_engine 源码对拍）;
#   净费读数只进 metrics 不进 judge()（verdict 零影响，在册 05_owner_decisions.yaml 依据）
# [MODIFY-GUARD] none（新增测试件；被测锚=calibration_exam._round_trip_cost_bp 与 _series_metrics 净费腿）
# [STABILITY] evolving
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_net_fee_param_face.py — G1 净费参数面落地测试（裁定#506 参数腿，⑨席 04 班修⑨的收口件）。

背景：裁定#506 令"参数入 exam_scale_cost_gate.yaml net_fee 节唯一参数面，禁硬编码"，但该节
自 2026-10-10 起缺席⇒消费腿 `_round_trip_cost_bp()` 走 except→nan 分支，`net_bucket_medians`
恒 NaN 而 `mono_spearman` 照常有值（毛面读数挂进门柱，⑨席在册修⑨）。本件钉四件事：
①参数面存在且等于引擎土规组合解；②尺能红（缺节→nan，非静默 0）；③消费腿真产净面；
④净面不进 judge()（改判据门柱的自检）。
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import calibration_exam as ce

REPO = Path(__file__).resolve().parents[2]
GATE_CFG = REPO / "config" / "exam_scale_cost_gate.yaml"
ENGINE = REPO / "scripts" / "backtest" / "translated" / "_c4_engine.py"


def _engine_cost_constants() -> tuple[float, float, float]:
    """从引擎源码取冻结土规常量（AST 字面量，不 import 重依赖模块）。"""
    tree = ast.parse(ENGINE.read_text(encoding="utf-8"))
    found: dict[str, float] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("COMMISSION_BP", "STAMP_BP", "SLIPPAGE_BP"):
                found[node.targets[0].id] = float(node.value.value)  # type: ignore[arg-type]
    assert set(found) == {"COMMISSION_BP", "STAMP_BP", "SLIPPAGE_BP"}, f"引擎常量缺失：{found}"
    return found["COMMISSION_BP"], found["STAMP_BP"], found["SLIPPAGE_BP"]


def _synthetic_pair(n: int = 400) -> tuple[pd.Series, pd.Series]:
    idx = pd.bdate_range("2024-01-01", periods=n)
    rng = np.random.default_rng(20261015)
    sig = pd.Series(np.cumsum(rng.normal(0.0, 1.0, n)), index=idx)
    tgt = pd.Series(0.05 * sig.to_numpy() + rng.normal(0.0, 1.0, n) / 100.0, index=idx)
    return sig, tgt


def test_net_fee_section_exists_in_true_source():
    """①参数面存在：net_fee 节在册且消费键为浮点 bp（缺席即红，禁静默）。"""
    data = yaml.safe_load(GATE_CFG.read_text(encoding="utf-8"))
    assert "net_fee" in data, "exam_scale_cost_gate.yaml 缺 net_fee 节（裁定#506 唯一参数面未落地）"
    rt = data["net_fee"]["round_trip_cost_bp"]
    assert isinstance(rt, float), f"round_trip_cost_bp 须为浮点 bp，实得 {type(rt)}"


def test_net_fee_value_equals_engine_frozen_caliber():
    """①单头自证：册面值 == 引擎土规组合解 2*C+S+2*slip（禁两处各写一套）。"""
    commission, stamp, slippage = _engine_cost_constants()
    expected = commission * 2 + stamp + slippage * 2
    got = ce._round_trip_cost_bp()
    assert not math.isnan(got), "净费读数取到 nan——参数面或消费腿断了"
    assert got == pytest.approx(expected), f"册面 {got} != 引擎式解 {expected}（{commission}/{stamp}/{slippage}）"


def test_consumer_reads_real_config_value():
    """①消费腿读真册：无参调用即得裁定#506 口径 25.0bp。"""
    assert ce._round_trip_cost_bp() == pytest.approx(25.0)


def test_missing_section_yields_nan_not_zero(tmp_path):
    """②尺能红（负对照）：缺 net_fee 节必须返 nan，不得伪造 0 成本。"""
    cfg = tmp_path / "no_net_fee.yaml"
    cfg.write_text(yaml.safe_dump({"cost_gate": {"tiers_bp": [0, 5]}}), encoding="utf-8")
    assert math.isnan(ce._round_trip_cost_bp(cfg))
    # 正对照：同一路径换上带节的册⇒同一个函数必须返数（证明红是节造成的，不是函数坏了）
    cfg2 = tmp_path / "with_net_fee.yaml"
    cfg2.write_text(yaml.safe_dump({"net_fee": {"round_trip_cost_bp": 12.5}}), encoding="utf-8")
    assert ce._round_trip_cost_bp(cfg2) == pytest.approx(12.5)


def test_series_metrics_produces_finite_net_bucket_medians():
    """③真产：合成数据出分面 net_bucket_medians 逐桶==毛面减 25bp，且全为有限值。"""
    sig, tgt = _synthetic_pair()
    m = ce._series_metrics(sig, tgt, {})
    gross = m["bucket_medians"]
    net = m["net_bucket_medians"]
    assert gross, "合成面未产桶中位收益（测试前提失效）"
    assert net is not None, "净费面未产（net_fee 节缺席时消费腿给 None/nan，属在册静默失效形态）"
    assert len(net) == len(gross)
    for g, v in zip(gross, net):
        assert math.isfinite(v), f"净费读数非有限值：{v}"
        assert v == pytest.approx(round(g - 25.0 / 10000.0, 6), abs=1e-9)
    assert m["round_trip_cost_bp"] == pytest.approx(25.0)


def test_net_face_absent_when_param_face_dead(monkeypatch):
    """③反向自证：把参数读回打桩成 nan（=落地前形态），净面必须显式变 nan 而非冒充已过。

    钉的是"降级态与未触发同形"这一类假绿：净面若与参数面无因果，则本件应红。
    """
    sig, tgt = _synthetic_pair()
    monkeypatch.setattr(ce, "_round_trip_cost_bp", lambda config_path=None: float("nan"))
    m = ce._series_metrics(sig, tgt, {})
    assert all(math.isnan(v) for v in m["net_bucket_medians"]), "参数面断供而净面仍有值⇒净费腿是装饰件"


def test_net_face_not_consumed_by_judge():
    """④门柱零影响：judge() 对同一 metrics 有净面/无净面给出同一 verdict。"""
    card = {
        "family": "calibration",
        "pillars_numeric": {"ic_mean_min": 0.02},
        "window": {"in_sample": ["2021-01-01", "2022-12-31"], "oos": ["2023-01-01", "2024-06-30"]},
    }
    base = {
        "ic_mean": 0.05,
        "mono_spearman": 0.9,
        "n": 400,
        "regime_ic": {"bull": 0.05, "bear": 0.05},
        "oos_ic": 0.05,
        "ic_ir": None,
        "bucket_medians": [0.001, 0.002],
        "n_buckets_used": 2,
    }
    with_net = dict(base, net_bucket_medians=[-0.03, -0.02], round_trip_cost_bp=25.0)
    v0, f0 = ce.judge(card, base)
    v1, f1 = ce.judge(card, with_net)
    assert (v0, f0) == (v1, f1), "净费读数影响了 verdict⇒本件挪了判据门柱（违裁定#506 与 G4-5）"
