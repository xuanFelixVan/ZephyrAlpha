# [BLUEPRINT] MOD-BT-249 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_arm_protocol_binding
# [TESTS] tests/backtest/test_arm_protocol_binding.py
# [TTL] permanent
# 测试隔离：合成臂面全在 tmp_path；真卡面只读不写（零分数册/零卡件改动/零 CH）。
"""臂协议绑定层红蓝双向：引句自闸/未知算子抛/未冻结参数拒出/三态分箱对真卡/非 ASCII 路径不误伤。

判别力声明（在册教训：判通过的脚本须先证明能红）——引句不在卡面、算子名未知、臂参数缺数值
三处都写"应当拒"的正例；任一被写成恒过即红。三态分箱另用两张真卡钉住预期态（跑偏即红）。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from scripts.backtest.fexam import arm_protocol_binding as apb

REPO_ROOT = Path(__file__).resolve().parents[2]
CARDS = REPO_ROOT / "docs" / "03_modules" / "_domain_backtest" / "exam_cards"


def _load(rel_path: str) -> dict:
    return yaml.safe_load((CARDS / rel_path).read_text(encoding="utf-8"))


def _card(**kw) -> dict:
    """合成臂协议卡（零生产路径；data_binding.arm_protocol 用可核验的自造原文）。"""
    base = {
        "schema_version": "1.0",
        "card_id": "TDM-E-TEST/comparison/02_x",
        "node_id": "TDM-E-TEST",
        "family": "comparison",
        "status": "preregistered",
        "signal_kind": "series",
        "window": {"in_sample": ["2019-01-04", "2023-12-31"], "frozen_note": "看数前冻结（合成件）"},
        "buckets": {"type": "arm_matrix", "on": "关臂=满仓 vs 开臂=三级仓位映射（A 100%/B 60%/C 0%）"},
        "pillars_numeric": {"maxdd_improvement_min": 5.0, "sharpe_delta_min": -0.1, "oos_same_sign": True},
        "target": {"primary": "next_day_index_return（合成）"},
        "data_binding": {
            "signal_table": "由 TableRegistry 品类解析（合成件不写字面量表名）",
            "signal_derivation": "基线臂日净值序列",
            "target_source": "风控层改写后的净值路径，减仓=按级别比例，现金停放 0 收益",
            "arm_protocol": "三臂输入同一基线净值序列与同一成交口径；级别→仓位映射（A 100%/B 60%/C 0%）冻结于本卡",
        },
    }
    base.update(kw)
    return base


def _base_series() -> pd.Series:
    idx = pd.date_range("2024-01-02", periods=10, freq="D")
    return pd.Series(1.0, index=idx, name="exposure")


# ── 红正例 1：引句不在卡面 → 拒绑（自造口径形态）────────────────────────────
def test_quote_absent_on_card_is_rejected() -> None:
    card = _card()
    entry = {
        "card_id": card["card_id"],
        "op_open": "arm_level_cap_multiply",
        "op_base": "arm_identity",
        "quote_open": "级别→仓位映射（L1 100%/L2 100% 禁新开/L3 梯度 80/60/40%/L4 0%）冻结于本卡",
        "params_open": {
            "level_map": {"L1": 1.0, "L3": 0.6, "L4": 0.0},
            "levels": pd.Series(["L1"] * 10, index=_base_series().index),
        },
    }
    with pytest.raises(apb.ArmQuoteNotFound):
        apb.build_arms(card, entry, base=_base_series())


# ── 红正例 2：算子名未知 → 抛 ───────────────────────────────────────────────
def test_unknown_arm_op_raises() -> None:
    card = _card()
    for entry in (
        {"op_open": "arm_teleport", "op_base": "arm_identity"},
        {"op_open": "arm_identity"},  # 基臂未声明
    ):
        with pytest.raises(apb.ArmOpUnknown):
            apb.build_arms(card, entry, base=_base_series())


# ── 红正例 3：臂参数缺数值 → 拒（禁替卡拍数）───────────────────────────────
def test_unfrozen_arm_param_raises() -> None:
    card = _card()
    # 门乘子未给 factor（卡面"降风险预算"无数值时不得由代码补）
    entry = {
        "op_open": "arm_gate_multiply",
        "op_base": "arm_identity",
        "quote_open": "三臂输入同一基线净值序列与同一成交口径",
        "params_open": {"gate": pd.Series([True] * 10, index=_base_series().index)},
    }
    with pytest.raises(apb.ArmParamUnfrozen):
        apb.build_arms(card, entry, base=_base_series())
    # level_map 缺档位数值同样拒
    entry2 = {
        "op_open": "arm_level_cap_multiply",
        "op_base": "arm_identity",
        "quote_open": "级别→仓位映射（A 100%/B 60%/C 0%）冻结于本卡",
        "params_open": {"level_map": {"A": 1.0}, "levels": pd.Series(["C"] * 10, index=_base_series().index)},
    }
    with pytest.raises(apb.ArmParamUnfrozen):
        apb.build_arms(card, entry2, base=_base_series())


# ── 绿正例：算子语义正确（敞口=底座×档位乘子；引句空格排版不误伤）───────────
def test_level_cap_multiply_semantics_and_space_tolerant_quote() -> None:
    card = _card()
    base = _base_series()
    entry = {
        "op_open": "arm_level_cap_multiply",
        "op_base": "arm_identity",
        # 引句与卡面只差空格（校验面空格归一，同 run_binding_book 的 prose_quote 形制）
        "quote_open": "级别 → 仓位 映射（A 100%/B 60%/C 0%）冻结于本卡",
        "params_open": {
            "level_map": {"A": 1.0, "B": 0.6, "C": 0.0},
            "levels": pd.Series(["A", "A", "B", "B", "C", "C", "A", "A", "B", "C"], index=base.index),
        },
    }
    open_arm, base_arm, ev = apb.build_arms(card, entry, base=base)
    assert list(open_arm)[:5] == [1.0, 1.0, 0.6, 0.6, 0.0]
    assert open_arm.iloc[5] == 0.0 and base_arm.iloc[-1] == 1.0
    assert ev["op"] == {"open": "arm_level_cap_multiply", "base": "arm_identity"}
    assert open_arm.index.equals(base.index)


def test_constant_and_subset_and_gate_ops() -> None:
    card = _card()
    base = _base_series()
    idx = base.index
    assert apb.arm_constant(base, {"value": 0.0}, {}).eq(0.0).all()
    masked = apb.arm_subset_mask(base, {"mask": pd.Series([True, False] * 5, index=idx), "fill": 0.0}, {})
    assert masked.iloc[1] == 0.0 and masked.iloc[0] == 1.0
    gated = apb.arm_gate_multiply(
        base,
        {"gate": pd.Series(["trend_down", "trend_up"] * 5, index=idx), "on_values": ["trend_down"], "factor": 0.6},
        {},
    )
    assert gated.iloc[0] == 0.6 and gated.iloc[1] == 1.0
    with pytest.raises(apb.ArmParamUnfrozen):
        apb.arm_gate_multiply(base, {"gate": pd.Series([True] * 10, index=idx), "factor": 1.7}, {})
    with pytest.raises(apb.ArmBaseMissing):
        apb.arm_identity(None, {}, {})
    with pytest.raises(apb.ArmBaseMissing):
        apb.arm_subset_mask(pd.DataFrame({"a": [1.0]}, index=idx[:1]), {"mask": None, "fill": 0.0}, {})


# ── 分箱：真卡钉态（跑偏即红）──────────────────────────────────────────────
def test_triage_real_feasible_card() -> None:
    card = _load("exit_flow/X1/TDM-X-R1-01__comparison__02_熔断五级梯度减仓对照.yaml")
    r = apb.triage_card(card)
    assert r["state"] == "feasible_now"
    assert r["signal_kind"] == "series" and r["arm_count"] == 3
    assert r["scalar_expressible"] is True and r["numeric_frozen"] is True
    # 门柱词表外键须如实点出（P1 立法面），禁谎报"全在机判面内"
    assert "whipsaw_roundtrip_ratio_max" in r["out_of_vocab_pillars"]


def test_triage_real_panel_card_goes_to_engine() -> None:
    card = _load("exit_flow/S2/TDM-X-S2-01__comparison__02_执行方式路由与流动性三查对照.yaml")
    r = apb.triage_card(card)
    assert r["state"] == "needs_matching_engine"
    assert r["missing_device"] and "切片" in r["missing_device"]


def test_triage_unfrozen_magnitude_credential_on_real_card() -> None:
    """体制门幅度词"降风险预算"卡面无相邻数值 → 凭据点名（但三态不因它翻转，缺件优先）。"""
    card = _load("exit_flow/X1/TDM-X-R1-01__ablation__03_市场体制条件下熔断减仓增量.yaml")
    r = apb.triage_card(card)
    assert r["state"] in ("feasible_now", "unfrozen_arm_definition")
    assert any("降风险" in x or "趋势门" in x for x in apb.pending_numeric_params(card))


def test_triage_no_arm_face_card_does_not_claim_feasible() -> None:
    card = _card()
    card["data_binding"].pop("arm_protocol")
    card["buckets"].pop("on")
    card["window"].pop("frozen_note")
    card["target"].pop("primary")
    r = apb.triage_card(card)
    assert r["state"] == "needs_matching_engine"
    assert "无臂协议" in r["credential"]


def test_non_ascii_path_not_harmed(tmp_path: Path) -> None:
    """非 ASCII 文件名/目录不得被误判为"无臂协议面"或漏收（卡册实测中文件名是常态）。"""
    d = tmp_path / "臂协议试点"
    d.mkdir()
    card = _card()
    (d / "TDM-E-TEST__comparison__02_熔断档位对照.yaml").write_text(
        yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    rows = apb.triage_dir(d)
    assert len(rows) == 1
    assert rows[0]["state"] == "feasible_now"
    assert "熔断档位" in rows[0]["path"]
    # 真卡册全量扫一遍：件名全中文，须一支不漏且零异常
    all_rows = apb.triage_dir(CARDS)
    assert len(all_rows) >= 19
    assert all("state" in r and r["card_id"] for r in all_rows)
