# [BLUEPRINT] MOD-BT-228 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_trial_ledger_batch_record
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; zephyr.backtest.core.n_trial_ledger; scripts.backtest.factory_grid_executor
# [CONSUMERS] P0-6 试验台账记账治本红证（2026-09-28）：批末 record 幂等 + 水位线单调 +
#   --verify-counts 红/绿两态 + t2 不可绕逻辑防回退钉
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 全用例零写生产账本（TrialLedger 一律 monkeypatch 绑 tmp_path）；
#   网格产物全落 tmp_path；零网络零 ClickHouse
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-228 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P0-6 试验台账批末记账红证。

根因复盘（2026-09-26/27 实测）：账本 20,632 vs 实际 ~24,905（17.4% 漏记），
机制=没人调 record/sync + summary 只在批末写。本文件钉四条行为：
  1. record_run 幂等（同 batch_id 二次登记不重复计数）；
  2. 水位线单调（回退调用静默无效）；
  3. _verify_counts 红/绿两态（缺账 exit 1 且点名；补账后 exit 0）；
  4. t2 不可绕逻辑防回退钉（--skip-compute-gate 对 stage=t2 无效的行为锚仍在）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "backtest"))

import factory_grid_executor as fge  # noqa: E402

from zephyr.backtest.core import n_trial_ledger as ntl  # noqa: E402


@pytest.fixture()
def tmp_ledger_cls(monkeypatch, tmp_path):
    """TrialLedger 全员绑 tmp_path——生产账本零接触（INVARIANTS 硬约束）。"""
    real_cls = ntl.TrialLedger

    def _factory(*_a, **_kw):
        inst = real_cls(registry_path=tmp_path / "trial_ledger.yaml")
        inst.load_registry(create_if_missing=True)  # tmp 骨架引导（生产件本就存在）
        return inst

    monkeypatch.setattr(ntl, "TrialLedger", _factory)
    return _factory


def test_record_run_idempotent_and_watermark_monotone(tmp_path):
    led = ntl.TrialLedger(registry_path=tmp_path / "ledger.yaml")
    led.load_registry(create_if_missing=True)
    first = led.record_run("factory_grid_batch_a", "grid_t1", 5, recorded_by="test")
    assert first["status"] == "recorded"
    again = led.record_run("factory_grid_batch_a", "grid_t1", 5, recorded_by="test")
    assert again["status"] == "exists"
    snap = led.load_registry()
    assert len(snap["batch_records"]) == 1  # 幂等：不重复计数
    led.set_watermark("wm_test", 100.0)
    led.set_watermark("wm_test", 50.0)  # 回退必须无效
    assert led.get_watermark("wm_test") == 100.0


def test_auto_record_advances_ledger_idempotently(tmp_ledger_cls, tmp_path):
    summary = {"run_ts": "20260928-0001", "evaluated": 12}
    out = fge._auto_record_and_advance(tmp_path, summary)
    assert out["record"]["status"] == "recorded"
    assert out["record"]["n_trials"] == 12
    assert out["watermark"]["watermark"] > 0
    out2 = fge._auto_record_and_advance(tmp_path, summary)  # 同批重放
    assert out2["record"]["status"] == "exists"


def test_verify_counts_red_then_green(tmp_ledger_cls, tmp_path):
    root = tmp_path / "intake"
    for ts, n in (("20260928-0001", 5), ("20260928-0002", 7)):
        d = root / f"grid_{ts}"
        d.mkdir(parents=True)
        (d / "summary.json").write_text(json.dumps({"run_ts": ts, "evaluated": n}), encoding="utf-8")
    led = ntl.TrialLedger(registry_path=tmp_path / "ledger.yaml")
    led.record_run("factory_grid_batch_a", "grid_20260928-0001", 5, recorded_by="test")
    # 红态：0002 缺账 → exit 1 且点名
    rc = fge._verify_counts(str(root))
    assert rc == 1
    # 绿态：补登 0002 → exit 0
    led.record_run("factory_grid_batch_a", "grid_20260928-0002", 7, recorded_by="test")
    assert fge._verify_counts(str(root)) == 0


def test_t2_gate_logic_pin_unchanged():
    """K2 (f6e288fc54) 行为锚防回退：stage=t2 时 --skip-compute-gate 无效的判断仍在。"""
    src = Path(fge.__file__).read_text(encoding="utf-8")
    assert 'args.stage == "t2"' in src
    assert "--skip-compute-gate" in src
    assert "or args.stage ==" in src
