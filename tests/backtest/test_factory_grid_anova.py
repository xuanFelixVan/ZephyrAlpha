# [BLUEPRINT] MOD-BT-197 | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_factory_grid_anova
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_anova
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 构造数据上主效应占比可精确预期; 降级格点剔除 fail-closed; 三件套齐备
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_factory_grid_anova.py — ANOVA 方差分解测试（构造数据上主效应精确可预期）。"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "factory_grid_anova", _REPO / "scripts" / "backtest" / "factory_grid_anova.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _spec.loader.exec_module(mod) or mod


def _synth_manifest(n: int = 2000, seed: int = 3) -> pd.DataFrame:
    """构造数据: D1 频率真实影响 sharpe（weekly 高 0.5），其余维零效应。"""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        freq = rng.choice(["daily", "weekly", "monthly"])
        cap = rng.choice(["cap5", "cap10", "cap20"])
        norm = rng.choice(["raw", "rank"])
        effect = {"daily": 0.0, "weekly": 0.5, "monthly": 0.1}[freq]
        rows.append({
            "recipe_id": f"r{i:05d}",
            "sharpe": effect + rng.normal(0, 0.2),
            "degraded_dimensions": "[]" if i % 10 else "['A1_factor_normalize']",
            "values_json": json.dumps({
                "D1_rebalance_freq": freq, "E_single_cap": cap,
                "A1_factor_normalize": norm,
            }),
        })
    return pd.DataFrame(rows)


class TestLoadManifest:
    def test_degraded_excluded(self) -> None:
        tmp = Path(_REPO) / ".runtime" / "tmp" / "anova_t1.csv"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        _synth_manifest().to_csv(tmp, index=False)
        clean = mod.load_manifest(tmp)
        assert len(clean) == 1800  # 10% 降级剔除
        assert "perf_bin" in clean.columns

    def test_insufficient_rows_fail_closed(self) -> None:
        tmp = Path(_REPO) / ".runtime" / "tmp" / "anova_t2.csv"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        df = _synth_manifest(30)
        df.to_csv(tmp, index=False)
        with pytest.raises(ValueError, match="不足 50"):
            mod.load_manifest(tmp)


class TestImportance:
    def test_true_effect_ranks_top(self) -> None:
        df = _synth_manifest_df()
        dims = ["D1_rebalance_freq", "E_single_cap", "A1_factor_normalize"]
        imp = mod.importance_table(df, dims)
        assert imp.iloc[0]["dimension"] == "D1_rebalance_freq"  # 真实效应维度排第一
        # 主效应占比量级合理: weekly+0.5 / 噪声 0.2 → 组间方差应显著
        top = float(imp.iloc[0]["main_effect_ratio"])
        assert 0.1 < top < 1.0

    def test_zero_effect_dim_near_zero(self) -> None:
        df = _synth_manifest_df()
        imp = mod.importance_table(df, ["E_single_cap"])
        assert float(imp.iloc[0]["main_effect_ratio"]) < 0.05  # 零效应维占比≈0


class TestInteractionAndPrune:
    def test_prunable_finds_null_dims(self) -> None:
        df = _synth_manifest_df()
        dims = ["D1_rebalance_freq", "E_single_cap", "A1_factor_normalize"]
        imp = mod.importance_table(df, dims)
        inter = mod.interaction_table(df, dims, imp.head(3)["dimension"].tolist())
        prunable = [p["dimension"] for p in mod.prunable_dims(imp, inter)]
        assert "E_single_cap" in prunable  # 零效应零交互 → 可砍
        assert "D1_rebalance_freq" not in prunable  # 主效应维不可砍


class TestRunAnova:
    def test_three_deliverables_present(self) -> None:
        tmp = Path(_REPO) / ".runtime" / "tmp" / "anova_t3.csv"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        _synth_manifest().to_csv(tmp, index=False)
        report = mod.run_anova(tmp)
        assert set(report) >= {"importance", "significant_interactions", "prunable_dims"}
        assert len(report["importance"]) >= 3


def _synth_manifest_df() -> pd.DataFrame:
    return mod._parse_values(mod.load_manifest(_write_tmp()))


def _write_tmp() -> Path:
    tmp = Path(_REPO) / ".runtime" / "tmp" / "anova_shared.csv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    if not tmp.exists():
        _synth_manifest().to_csv(tmp, index=False)
    return tmp
