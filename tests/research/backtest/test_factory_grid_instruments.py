# [BLUEPRINT] MOD-BT-077 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.research.backtest.test_factory_grid_instruments
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.factory_grid_executor
# [CONSUMERS] T1 网格批仪表守卫（MODIFY-GUARD: factory_grid_executor 仪表面）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯合成数据（不连 CH，数据面钩子全打桩）；测试不写生产路径（INTAKE_DIR→tmp_path）；
#              引擎/求值/抽样走真件（engine="cpu"）；零漂移证尺=同 seed 两次批 manifest 格点集一致
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-077 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""T1 网格批仪表守卫（st-gpufeed-20261010）——批A 遗产（16.7h 零分段落盘）不再发。

覆盖面：
  1. run_batch 端到端（合成面板+打桩数据面）：四类遥测件出生且形状合法
     （batch_meta/progress/heartbeat/manifest_partial）+ 判据面零动（原三件套照常）。
  2. _GridInstruments 单元：停滞看门狗 dump、partial 原子重写、finalize 幂等。
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

import factory_grid_executor as fge  # noqa: E402

_DAYS, _SYMS = 300, 40


def _panel_wide(days: int = _DAYS, syms: int = _SYMS, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2024-01-02", periods=days)
    rets = rng.normal(0.0005, 0.02, size=(days, syms))
    return pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=idx, columns=[f"{i:06d}" for i in range(syms)])


@pytest.fixture()
def instrumented_env(tmp_path, monkeypatch):
    """数据面全打桩（零 CH）+ INTAKE_DIR 指向 tmp_path + 仪表强制开。"""
    import _c4_engine

    panel = _panel_wide()
    symbols = list(panel.columns)

    def fake_load_px(start, end, fields=("close",)):
        long_df = panel.stack(future_stack=True).rename("close").reset_index()
        long_df.columns = ["trade_date", "symbol", "close"]
        for extra in fields:
            if extra != "close":
                long_df[extra] = 1_000_000.0
        long_df["trade_date"] = pd.to_datetime(long_df["trade_date"])
        return long_df[["trade_date", "symbol", *fields]]

    def fake_load_st_flags(start, end):
        return pd.DataFrame(columns=["trade_date", "symbol", "st_flag"])

    def fake_seal_masks(index, columns):
        false_w = pd.DataFrame(False, index=index, columns=columns)
        return false_w, false_w.copy()

    real_engine = fge._load_engine()

    def fake_load_engine():
        # 引擎函数全走真件（pandas 纯算），只桩掉两个 CH 口（load_px/load_st_flags）
        # 与闸门数据口（_load_seal_masks 经 _c4_engine 模块级 patch 生效）
        return (fake_load_px, real_engine[1], real_engine[2], fake_load_st_flags) + real_engine[4:]

    monkeypatch.setattr(fge, "INTAKE_DIR", tmp_path)
    monkeypatch.setattr(fge, "_load_engine", fake_load_engine)
    monkeypatch.setattr(fge, "_load_universe", lambda g, start, end: set(symbols))
    monkeypatch.setattr(fge, "_load_mkt_cap_wide", lambda warm_start, end, columns: pd.DataFrame(index=panel.index))
    monkeypatch.setattr(fge, "_industry_map", lambda: {s: "fictitious_industry" for s in symbols})
    monkeypatch.setattr(_c4_engine, "_load_seal_masks", fake_seal_masks)
    monkeypatch.setattr(fge, "_GRID_INSTRUMENT", True)
    return tmp_path


class TestRunBatchEndToEnd:
    def test_instruments_born_and_judgment_surface_untouched(self, instrumented_env):
        tmp_path = instrumented_env
        summary = fge.run_batch(
            n_samples=8,
            seed=20260916,
            start="2024-01-02",
            end="2025-02-28",
            smoke=True,
            stratify_dims=("G_universe", "A1_factor_normalize", "B_top_n"),
            engine="cpu",
        )
        out_dir = Path(summary["out_dir"])
        # 判据面零动：原三件套照常出生
        assert (out_dir / "manifest.csv").exists()
        assert (out_dir / "negatives.csv").exists()
        assert (out_dir / "summary.json").exists()
        n_total = summary["n_sampled"]
        assert summary["evaluated"] + summary["eval_dead"] + summary["backtest_dead"] == n_total

        # 遥测件 1：批出生卡（自报家门——批A 验尸时 pid/起跑全靠台账拼图的反面）
        meta = json.loads((out_dir / "batch_meta.json").read_text(encoding="utf-8"))
        assert meta["pid"] == os.getpid()
        assert meta["n_picked"] == n_total
        assert meta["seed"] == 20260916
        assert isinstance(meta["argv"], list)

        # 遥测件 2：每格终态一行（分段计时+combine 命中面）
        rows = [json.loads(ln) for ln in (out_dir / "progress.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(rows) == n_total
        assert {r["i"] for r in rows} == set(range(n_total))
        pos = [r for r in rows if r["out"] == "pos"]
        assert pos, "合成面板上至少应有正格"
        for r in pos:
            assert r["combine"] in {"hit", "miss"}
            assert r["cache_n"] >= 1
            for k in ("fetch_s", "eval_s", "bt_s", "write_s", "tot_s"):
                assert isinstance(r[k], (int, float)) and r[k] >= 0.0
        for r in rows:
            if r["out"] == "neg":
                assert r["layer"] in {"eval", "backtest", "gate"}
                assert r["reason"]

        # 遥测件 3：心跳含 kind=hb 与 kind=done 终态行
        hb = [json.loads(ln) for ln in (out_dir / "heartbeat.jsonl").read_text(encoding="utf-8").splitlines()]
        assert any(r["kind"] == "done" for r in hb)
        done = next(r for r in hb if r["kind"] == "done")
        assert done["cells_done"] == n_total
        assert done["total"] == n_total
        assert done["note"] == "done"

        # 遥测件 4：partial 与最终 manifest 行数一致（finalize 末次 flush）
        partial = pd.read_csv(out_dir / "manifest_partial.csv")
        final = pd.read_csv(out_dir / "manifest.csv")
        assert len(partial) == len(final) == summary["evaluated"]

    def test_same_seed_same_cell_set(self, instrumented_env):
        """零漂移证尺：仪表加身后同 seed 两次批的 manifest 格点集逐位一致。"""
        tmp_path = instrumented_env
        ids = []
        for _ in range(2):
            s = fge.run_batch(
                n_samples=8,
                seed=20260916,
                start="2024-01-02",
                end="2025-02-28",
                smoke=True,
                stratify_dims=("G_universe", "A1_factor_normalize", "B_top_n"),
                engine="cpu",
            )
            m = pd.read_csv(Path(s["out_dir"]) / "manifest.csv")
            ids.append(sorted(m["recipe_id"].tolist()))
        assert ids[0] == ids[1]

    def test_prefix_sequential_execution_order(self, instrumented_env):
        """T2-A（st-gpufeed-20261010）：迭代序按 prefix_key 非降序——同 prefix 格点连续
        执行使 combine_cache LRU 命中（T1 实测 stratify 交错序命中率仅 1.5%）。manifest
        行序=完成序=迭代序，故直接对 manifest.prefix_key 断言非降序。"""
        tmp_path = instrumented_env
        s = fge.run_batch(
            n_samples=8,
            seed=20260916,
            start="2024-01-02",
            end="2025-02-28",
            smoke=True,
            stratify_dims=("G_universe", "A1_factor_normalize", "B_top_n"),
            engine="cpu",
        )
        m = pd.read_csv(Path(s["out_dir"]) / "manifest.csv")
        keys = m["prefix_key"].tolist()
        assert keys == sorted(keys), f"执行序未按 prefix 排序: {keys[:6]}"
        # 命中率增益由 200 点影子对照实测验证（smoke 8 格可能全为互异 prefix，无命中可断言）


class TestGridInstrumentsUnit:
    def test_stall_watchdog_dumps(self, tmp_path, monkeypatch):
        """停滞看门狗：无进展超阈 → heartbeat 行带 stall 标记（批A 静默窗缺失的证据面）。"""
        monkeypatch.setattr(fge, "_GRID_HB_INTERVAL_S", 0.05)
        monkeypatch.setattr(fge, "_GRID_STALL_THRESHOLD_S", 0.1)
        instr = fge._GridInstruments(tmp_path, total_cells=5)
        instr.start_heartbeat()
        time.sleep(0.8)  # ~16 拍心跳，全部停滞
        instr.finalize([], [])
        lines = [json.loads(ln) for ln in (tmp_path / "heartbeat.jsonl").read_text(encoding="utf-8").splitlines()]
        assert any(r.get("stall") for r in lines), f"未见 stall 标记: {lines[:3]}"
        assert any(r["kind"] == "done" for r in lines)

    def test_flush_partial_and_finalize_idempotent(self, tmp_path):
        instr = fge._GridInstruments(tmp_path, total_cells=100)
        instr.record_cell({"i": 0, "id": "r0", "out": "pos", "combine": "miss", "cache_n": 1})
        instr.record_cell({"i": 1, "id": "r1", "out": "neg", "layer": "eval", "reason": "universe_too_small"})
        assert instr.maybe_flush(["x"], ["y"]) == 0.0  # 2 条 < 25 不触发
        # 真型 flush：借 GridEvalOutcome 构造
        from factory_grid_executor import GridEvalOutcome

        rows = [GridEvalOutcome("r0", "p0", {"a": "b"}, ())]
        instr.flush_partial(rows, [])
        assert len(pd.read_csv(tmp_path / "manifest_partial.csv")) == 1
        instr.finalize(rows, [], note="done")
        instr.finalize(rows, [], note="done")  # 幂等：第二次为 no-op
        hb = (tmp_path / "heartbeat.jsonl").read_text(encoding="utf-8").splitlines()
        assert sum(1 for ln in hb if json.loads(ln)["kind"] == "done") == 1

    def test_gpu_sample_never_raises(self):
        """心跳采样面禁抛：nvidia-smi/NVML 任一路缺失都只出声降级，不得把心跳线程打死。

        三元组契约（st-gpux-20261011）：(设备 util, 设备 mem, 逐进程归因 dict)。
        归因 dict 缺失时=空 dict 或 available=False，**禁伪造 0**（"读不到"≠"没占用"）。
        """
        util, mem, attrib = fge._instr_gpu_sample()
        assert util is None or 0 <= float(util) <= 100
        assert mem is None or float(mem) >= 0
        assert isinstance(attrib, dict)
        if attrib.get("available"):
            assert attrib["sm_util_pct"] is None or 0 <= attrib["sm_util_pct"] <= 100
        else:
            assert attrib.get("sm_util_pct") is None, "不可用时禁给出数值（含 0）"
