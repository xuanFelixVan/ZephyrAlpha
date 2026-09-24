# [BLUEPRINT] MOD-BT-COND-ATTR-TEST | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_condition_attribution
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas; numpy; scripts.backtest.condition_attribution
# [CONSUMERS] CI（MODIFY-GUARD 契约钉）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试隔离：合成产物写 tmp_path fixture 零生产路径；红证=达标胞过滤+残差披露+零重叠炸
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试红
# [TESTS] self
# [TTL] permanent
# [A_module] module_id=MOD-BT-COND-ATTR-TEST | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""条件胞归因契约钉（MOD-BT-COND-ATTR）：合成 run×pack 面板红蓝。"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.condition_attribution import attribute_run
from zephyr.backtest.regime_validation import condition_package as cp


def _make_pack(tmp_path):
    rows = [(f"2025-01-{i:02d}", 0.5, "neutral") for i in range(1, 32)]  # mild|neutral 31 日达标
    rows += [("2025-02-03", 0.9, "neutral"), ("2025-02-04", 0.9, "neutral")]  # boiling 2 日 → 下沉
    pack = cp.build_condition_pack(
        pd.DataFrame(rows, columns=["date", "value", "state"]).assign(date=lambda d: pd.to_datetime(d["date"]))
    )
    cp.save_pack(pack, tmp_path / "pack")
    return pack


def _make_run(tmp_path, pack):
    dates = pd.DatetimeIndex([d for d, *_ in [(r,) for r in pack.frame["date"]]])
    rng = np.random.default_rng(7)
    nr = pd.DataFrame({"r1": rng.normal(0.001, 0.01, len(dates))}, index=dates)
    nr.index.name = "date"
    run = tmp_path / "run"
    run.mkdir()
    nr.to_parquet(run / "net_returns.parquet")
    (run / "summary.json").write_text(
        json.dumps({"net_returns_file": str(run / "net_returns.parquet")}), encoding="utf-8"
    )
    return run


def test_attribute_filters_ineligible_cells(tmp_path):
    pack = _make_pack(tmp_path)
    run = _make_run(tmp_path, pack)
    table = attribute_run(run, tmp_path / "pack")
    assert set(table["cell_id"]) == {"gmild|sneutral"}  # boiling 下沉不入表
    assert table.attrs["residual_days"] == 2
    assert table.attrs["total_days"] == 33
    assert table["days"].sum() == 31


def test_missing_net_returns_raises(tmp_path):
    _make_pack(tmp_path)
    run = tmp_path / "run_empty"
    run.mkdir()
    (run / "summary.json").write_text(json.dumps({"net_returns_file": "nope.parquet"}), encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        attribute_run(run, tmp_path / "pack")


def test_zero_overlap_raises(tmp_path):
    pack = _make_pack(tmp_path)
    run = tmp_path / "run_far"
    run.mkdir()
    far = pd.DataFrame({"r1": [0.0, 0.01]}, index=pd.DatetimeIndex(["2030-01-01", "2030-01-02"]))
    far.index.name = "date"
    far.to_parquet(run / "net_returns.parquet")
    (run / "summary.json").write_text(
        json.dumps({"net_returns_file": str(run / "net_returns.parquet")}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="零重叠"):
        attribute_run(run, tmp_path / "pack")
