# [BLUEPRINT] MOD-BT-T1T2-HANDOVER | docs/03_modules/_domain_backtest/blueprint.md（被测件挂靠）
# [MODULE] tests.backtest.test_t1_t2_handover
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.t1_t2_handover
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全程 tmp_path 合成仓面（测试隔离铁律：禁写生产 data/）；不真发车（launcher/e0/gpu/proc
#   全注入）；四证尺=①全过→选层≤cap 且确定性 ②完成率红→必红且不发车 ③claim 在场→拒发车
#   ④进程在+manifest 缺→WAITING 不误判死；每条证尺的红证（缺陷注入即失败）登记于案卷
#   AUTO_t1_t2_handover.md §六
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_t1_t2_handover.py — T1→T2 守望交接件单元测试（合成数据，零生产面写入，零真发车）。"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("t1_t2_handover", _REPO / "scripts" / "backtest" / "t1_t2_handover.py")
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)

TIER1 = 60
TIER2 = 8

# 维面：3 主效应维（各 2 层）× 3 参数弱维（各 2 层）→ 全组合 8 种…实际 2^6=64 组合取 60
DIMS = {
    "G_universe": ["hs300", "zz500"],
    "A1_factor_normalize": ["zscore", "rank"],
    "A2_combine_weight": ["equal", "ic_mean"],
    "C_sizing": ["equal_weight", "inv_vol"],
    "D1_rebalance_freq": ["weekly", "monthly"],
    "E_single_cap": ["cap5", "cap20"],
}
STRONG = ["G_universe", "A1_factor_normalize", "A2_combine_weight"]
WEAK = ["C_sizing", "D1_rebalance_freq", "E_single_cap"]


def _fake_importance(vals_df, score, dims):
    importance = {d: (0.9 - 0.1 * i) for i, d in enumerate(dims)}
    prunable = [d for d in dims if d in WEAK]
    return importance, set(prunable)


def _mk_manifest_df(n: int, seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    combos = list(itertools.product(*[DIMS[k] for k in DIMS]))
    rows = []
    for i in range(n):
        vals = {k: v for k, v in zip(DIMS, combos[i % len(combos)], strict=False)}
        vals["I_cost_tier"] = "frozen_l0"  # 常量维：S1 应剔除
        rid = f"r{i:04d}"
        rows.append(
            {
                "recipe_id": rid,
                "prefix_key": "x",
                "degraded_dimensions": "()",
                "sharpe": round(float(rng.uniform(0.05, 0.6)), 4),  # 全部 <2：好得可疑线零命中
                "ann_return": 0.05,
                "max_drawdown": -0.3,
                "avg_turnover": 0.03,
                "net_days": 1600,
                "values_json": json.dumps(vals, sort_keys=True),
            }
        )
    return pd.DataFrame(rows)


def _write_run(repo: Path, n_manifest: int = TIER1, n_sampled: int = TIER1, neg_extra_rows: int = 0) -> Path:
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    run.mkdir(parents=True, exist_ok=True)
    mf = _mk_manifest_df(n_manifest)
    mf.to_csv(run / "manifest.csv", index=False)
    neg_cols = ["recipe_id", "death_layer", "death_reason", "values", "degraded_dimensions", "detail"]
    neg = pd.DataFrame(
        [
            {
                "recipe_id": f"n{i}",
                "death_layer": "eval",
                "death_reason": "synthetic",
                "values": "{}",
                "degraded_dimensions": "",
                "detail": "",
            }
            for i in range(neg_extra_rows)
        ],
        columns=neg_cols,
    )
    neg.to_csv(run / "negatives.csv", index=False)
    (run / "summary.json").write_text(
        json.dumps(
            {
                "run_ts": "20260925-111219",
                "mode": "batch_a_census",
                "n_sampled": n_sampled,
                "evaluated": n_manifest,
                "eval_dead": 0,
                "backtest_dead": 0,
                "gate_dead": 0,
                "degraded_recipes": 0,
                "window": ["2019-01-04", "2025-09-09"],
                "seed": 20260915,
                "n_trials_effective": 12,
                "net_returns_file": None,
            }
        ),
        encoding="utf-8",
    )
    return run


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "config" / "search_space_prereg.yaml").write_text(
        yaml.safe_dump(
            {
                "budget_caps": {
                    "tier1_points": TIER1,
                    "tier2_points": TIER2,
                    "cost_gate_in_every_tier": True,
                    "per_point_seconds_measured": 35.33,
                    "vram": {"concurrency": 1},
                },
                "tracks": {"f06_grid": {"condition_stratification": {"search_window": ["2019-01-04", "2025-09-09"]}}},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (tmp_path / "config" / "exam_scale_cost_gate.yaml").write_text(
        yaml.safe_dump(
            {
                "cost_gate": {"tiers_bp": [0, 5, 10, 20, 40], "survival_floor": 0.0, "monotonic_tol": 1e-09},
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (tmp_path / "data" / "runtime").mkdir(parents=True)
    (tmp_path / "data" / "runtime" / "process_reaper_keep.txt").write_text("", encoding="utf-8")
    (tmp_path / ".runtime" / "logs").mkdir(parents=True)
    (tmp_path / ".runtime" / "logs" / "grid_t1_restart9_20260925.log").write_text(
        "line1\nline2\nboom\n", encoding="utf-8"
    )
    return tmp_path


class _FakeProc:
    def __init__(self, rc=None):
        self._rc = rc
        self.pid = 424242

    def poll(self):
        return self._rc


class _Recorder:
    def __init__(self, rc=None):
        self.calls = []
        self._rc = rc

    def __call__(self, cmd, cwd, log_path):
        self.calls.append((list(cmd), Path(cwd), Path(log_path)))
        return _FakeProc(self._rc)


def _replay_ok(run_dir, cells, tiers):
    return {rid: {float(b): 0.5 - 0.01 * i for i, b in enumerate(sorted(tiers))} for rid, _ in cells}


def _procs_nothing():
    return []


def _gpu_free():
    return []


def _e0_ok(_repo_root=None):
    return True, "injected_ok"


# ------------------------------------------------------------------ 证尺① 全过→选层正确且确定
def test_full_pass_builds_subspace_and_launches_once(repo: Path):
    run = _write_run(repo)
    rec = _Recorder()
    status, code = mod.run_handover(
        repo,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=rec,
        e0_gate=_e0_ok,
        observe_seconds=0.0,
    )
    assert status == "LAUNCHED" and code == 0

    verdict = yaml.safe_load((run / "handover_verdict.yaml").read_text(encoding="utf-8"))
    assert verdict["all_green"] is True
    assert verdict["garbage_hits"] == []
    assert {k: v["pass"] for k, v in verdict["criteria"].items()} == {k: True for k in verdict["criteria"]}

    sub = json.loads((run / "t2_subspace.json").read_text(encoding="utf-8"))
    # 弱维参数展开（全层保留）；主效应维裁到 ≤ceil(0.2*n 层)；常量维 I_cost_tier 不入册
    assert "I_cost_tier" not in sub
    for d in WEAK:
        assert sorted(sub[d]) == sorted(DIMS[d])
    for d in STRONG:
        assert len(sub[d]) <= max(1, int(np.ceil(0.2 * len(DIMS[d]))))
    pts = 1
    for vs in sub.values():
        pts *= len(vs)
    assert pts <= TIER2  # 穷尽点数 ≤tier2_points（cap 内）

    # 确定性：同 manifest 重建必产出同字节 JSON
    b1 = (run / "t2_subspace.json").read_bytes()

    # cap 剪枝腿单测：全维弱（不裁层）→ 原生积 2^6=64 超 cap=8 → 剪枝必把穷尽点数压回 ≤cap
    caps = mod.load_prereg_caps(repo / "config" / "search_space_prereg.yaml")
    probe = mod.build_t2_subspace(run, caps, importance_fn=lambda v, s, d: ({x: 0.5 for x in d}, set(d)))
    pts_probe = 1
    for vs in probe["subspace"].values():
        pts_probe *= len(vs)
    assert probe["meta"]["pruned_levels"], "超 cap 必触发确定性剪层"
    assert pts_probe <= TIER2 and probe["expected_points"] <= TIER2
    mod.build_t2_subspace(run, caps, importance_fn=_fake_importance)
    assert (run / "t2_subspace.json").read_bytes() == b1

    # 发车命令沿用既有 CLI 语义
    cmd = rec.calls[0][0]
    assert "--stage" in cmd and cmd[cmd.index("--stage") + 1] == "t2"
    # 执行器消费面 = _json.loads(args.subspace_json) 内联 JSON（2026-09-29 SW4 实障修复：
    # 旧版传文件路径串必 JSONDecodeError 秒崩 LAUNCH_FAILED 循环）——断言该参为合法 JSON
    # 且与 t2_subspace.json 落盘负载逐字段一致。
    assert "--subspace-json" in cmd
    inline_arg = cmd[cmd.index("--subspace-json") + 1]
    assert json.loads(inline_arg) == json.loads((run / "t2_subspace.json").read_text(encoding="utf-8"))
    assert cmd[cmd.index("--start") + 1] == "2019-01-04"
    # 认领标记 + reaper keep 登记
    claim = yaml.safe_load((run / "t2_handover_claim.yaml").read_text(encoding="utf-8"))
    assert claim["launched"] is True
    keep = (repo / "data" / "runtime" / "process_reaper_keep.txt").read_text(encoding="utf-8")
    assert "factory_grid_executor" in keep

    # 再巡一轮：ALREADY_CLAIMED，不双发
    status2, code2 = mod.run_handover(
        repo,
        proc_scan=lambda: [(1, "python x/factory_grid_executor.py --stage t2")],
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=rec,
        e0_gate=_e0_ok,
        observe_seconds=0.0,
    )
    assert status2 == "ALREADY_CLAIMED" and code2 == 0
    assert len(rec.calls) == 1
    # 五档重放只发生一次（verdict 缓存按 manifest sha256）
    calls_before = len(rec.calls)
    assert calls_before == 1


# ------------------------------------------------------------------ 证尺② 完成率红→必红且不发车
def test_completion_shortfall_verdict_red_and_no_launch(repo: Path):
    run = _write_run(repo, n_manifest=TIER1 - 5, n_sampled=TIER1)  # 55/60≈91.7%<95%
    rec = _Recorder()
    status, code = mod.run_handover(
        repo,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=rec,
        e0_gate=_e0_ok,
        observe_seconds=0.0,
    )
    assert status == "VERDICT_RED" and code == 1
    assert rec.calls == []  # 红=绝不发车
    assert not (run / "t2_handover_claim.yaml").exists()  # 红=绝不认领
    verdict = yaml.safe_load((run / "handover_verdict.yaml").read_text(encoding="utf-8"))
    assert verdict["all_green"] is False
    assert "manifest_points" in verdict["blocking_criteria"]
    g = verdict["garbage_lines"]["completion_rate"]
    assert g["hit"] is True and abs(g["measured"] - 55 / 60) < 1e-6


# ------------------------------------------------------------------ 证尺③ claim 在场→拒发车
def test_existing_claim_blocks_second_launch(repo: Path):
    run = _write_run(repo)
    (run / "t2_handover_claim.yaml").write_text(
        yaml.safe_dump({"pid": 999999, "launched": False, "note": "另一守望器先手"}), encoding="utf-8"
    )
    rec = _Recorder()
    status, code = mod.run_handover(
        repo,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=rec,
        e0_gate=_e0_ok,
        observe_seconds=0.0,
    )
    assert status == "ALREADY_CLAIMED" and code == 0
    assert rec.calls == []
    assert not (run / "handover_verdict.yaml").exists()  # 认领在场连验收都不重做（防双写）


# ------------------------------------------------------------------ 证尺④ T1 在跑无 manifest→WAITING
def test_running_t1_without_manifest_waits(repo: Path):
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    run.mkdir(parents=True)
    procs = [(3584, "python scripts/backtest/factory_grid_executor.py --stage t1 --start 2019-01-04 --end 2025-09-09")]
    status, code = mod.run_handover(
        repo,
        proc_scan=lambda: procs,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=_Recorder(),
        e0_gate=_e0_ok,
    )
    assert status == "WAITING" and code == 0
    assert not (run / "handover_verdict.yaml").exists()  # WAITING 不误判死也不误验收

    # 进程亡且无 manifest → T1_DIED（附日志尾部指针，不自动重启）
    status2, code2 = mod.run_handover(
        repo,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=_Recorder(),
        e0_gate=_e0_ok,
    )
    assert status2 == "T1_DIED" and code2 == 1
    assert status2 == "T1_DIED"


# ------------------------------------------------------------------ 附加护栏（非四证尺）
def test_gpu_busy_defers_and_releases_claim(repo: Path):
    _write_run(repo)
    rec = _Recorder()
    busy = [(777, "python scripts/backtest/factory_grid_executor.py --stage t1")]
    status, code = mod.run_handover(
        repo,
        proc_scan=lambda: busy,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=rec,
        e0_gate=_e0_ok,
        observe_seconds=0.0,
    )
    assert status.startswith("DEFERRED") and code == 0
    assert rec.calls == []
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    assert not (run / "t2_handover_claim.yaml").exists()  # DEFERRED 不留僵尸认领


def test_instant_death_launch_releases_claim(repo: Path):
    _write_run(repo)
    rec = _Recorder(rc=3)  # 秒败（如 E0 拒）
    status, code = mod.run_handover(
        repo,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=rec,
        e0_gate=_e0_ok,
        observe_seconds=3.0,
    )
    assert status == "LAUNCH_FAILED" and code == 1
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    assert not (run / "t2_handover_claim.yaml").exists()  # 撤认领供下轮重试


def test_spot_below_monotonic_fails_verdict(repo: Path):
    run = _write_run(repo)

    def _replay_violate(run_dir, cells, tiers):
        out = _replay_ok(run_dir, cells, tiers)
        k = next(iter(out))
        rows = out[k]
        rows[max(rows)] = rows[min(rows)] + 1.0  # 40bp 档反超 0bp=非单调+穿地板
        return out

    status, code = mod.run_handover(
        repo,
        allow_launch=False,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_violate,
        importance_fn=_fake_importance,
        launcher=_Recorder(),
        e0_gate=_e0_ok,
    )
    assert status == "VERDICT_RED" and code == 1
    verdict = yaml.safe_load((run / "handover_verdict.yaml").read_text(encoding="utf-8"))
    assert verdict["criteria"]["cost_gate_spot"]["pass"] is False
    assert "cost_gate_spot" in verdict["blocking_criteria"]


# ------------------------------------------------------------------ ⚑-2② v2 机器门（W2-T2 2026-09-30）
# v1 回退零漂移钉死 + v2 c* 全量普查双向 + 出生证 fail-closed


def _write_exam_yaml(repo: Path, v2: bool) -> None:
    base = {"cost_gate": {"tiers_bp": [0, 5, 10, 20, 40], "survival_floor": 0.0, "monotonic_tol": 1e-09}}
    if v2:
        base["breakeven_cost_gate"] = {
            "version": "2.0.0",
            "criterion_id": "G-COST-BREAKEVEN-40BP",
            "declaration": "docs/_working/night_sweep/c_exam/flag2_declaration_b.md",
            "gates": {
                "p1_median_bp_min": 40.0,
                "p2_p10_bp_min": 0.0,
                "p3_stratified_pass_ratio_min": 0.80,
                "p3_layer_min_n": 30,
                "p4_scale_sensitivity_max": 0.20,
                "p5_data_version_required": ["adjustment_basis", "snapshot_date", "snapshot_sha256", "n_trials"],
            },
            "bisect": {"lo_bp": 0.0, "hi_bp": 200.0, "tol_bp": 0.1, "over_hi_label": ">200"},
        }
        base["cost_gate_active"] = {
            "active_version": "2.0.0",
            "fallback_version": "1",
            "launch_gate_scope": ["p1_median_bp_min", "p2_p10_bp_min"],
        }
    (repo / "config" / "exam_scale_cost_gate.yaml").write_text(
        yaml.safe_dump(base, allow_unicode=True), encoding="utf-8"
    )


def _mk_v2_run(repo: Path, cells_spec: list[tuple[float, int]], to: float = 0.03) -> Path:
    """合成 v2 run：net 序列（冻结土规 5bp 档）+manifest（sharpe/avg_turnover 引擎同式）。"""
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    run.mkdir(parents=True, exist_ok=True)
    n = sum(k for _c, k in cells_spec)
    idx = pd.bdate_range("2024-01-01", periods=120)
    alt = np.array([1.0, -1.0] * 60)  # 确定性交替：样本均值=目标均值（零抽样误差），sharpe≈1<2
    cols = {}
    mf_rows = []
    j = 0
    for c_star, k in cells_spec:
        mean_at_ref = (c_star - 5.0) * 2.0 * to / 1e4
        amp = abs(mean_at_ref) * np.sqrt(244.0) if mean_at_ref != 0 else 1e-4
        for _ in range(k):
            series = pd.Series(mean_at_ref + amp * alt, index=idx)
            cols[j] = series
            rid = f"r{j:04d}"
            combos = list(itertools.product(*[DIMS[d] for d in DIMS]))
            vals = {d: v for d, v in zip(DIMS, combos[j % len(combos)], strict=False)}
            sharpe = series.mean() / series.std() * np.sqrt(244)
            mf_rows.append(
                {
                    "recipe_id": rid,
                    "prefix_key": "x",
                    "degraded_dimensions": "()",
                    "sharpe": round(float(sharpe), 3),
                    "ann_return": 0.05,
                    "max_drawdown": -0.3,
                    "avg_turnover": to,
                    "net_days": len(idx),
                    "values_json": json.dumps(vals, sort_keys=True),
                }
            )
            j += 1
    pd.DataFrame(cols).to_parquet(run / "net_returns.parquet")
    pd.DataFrame(mf_rows).to_csv(run / "manifest.csv", index=False)
    pd.DataFrame(
        columns=["recipe_id", "death_layer", "death_reason", "values", "degraded_dimensions", "detail"]
    ).to_csv(run / "negatives.csv", index=False)
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8")) if (run / "summary.json").exists() else {}
    summary.update(
        {
            "eval_dead": 0,
            "backtest_dead": 0,
            "gate_dead": 0,
            "degraded_recipes": 0,
            "n_sampled": n,
            "evaluated": n,
            "window": ["2019-01-04", "2025-09-09"],
            "n_trials_effective": 15,
            "net_returns_file": "net_returns.parquet",
        }
    )
    (run / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return run


def test_load_cost_gate_params_v1_fallback_zero_drift(repo: Path):
    _write_exam_yaml(repo, v2=False)
    cg = mod.load_cost_gate_params(repo / "config" / "exam_scale_cost_gate.yaml")
    assert cg["active_version"] == "v1"
    assert cg["tiers"] == [0.0, 5.0, 10.0, 20.0, 40.0]
    assert cg["survival_floor"] == 0.0
    assert "breakeven" not in cg and "launch_gate_scope" not in cg


def test_load_cost_gate_params_v2_active(repo: Path):
    _write_exam_yaml(repo, v2=True)
    cg = mod.load_cost_gate_params(repo / "config" / "exam_scale_cost_gate.yaml")
    assert cg["active_version"] == "v2"
    assert cg["breakeven"]["p1_median_bp_min"] == 40.0
    assert cg["breakeven"]["hi_bp"] == 200.0
    assert cg["launch_gate_scope"] == ["p1_median_bp_min", "p2_p10_bp_min"]
    assert cg["survival_floor"] == 0.0  # v1 键仍随行（并列读数用）


def test_v2_census_birthcert_and_tail_mapping(repo: Path):
    """出生证校验（序列↔manifest 逐格 sharpe 3 位舍入一致）+尾行阴性登记映射。"""
    _write_exam_yaml(repo, v2=True)
    run = _mk_v2_run(repo, [(45.0, 4), (10.0, 2)])
    # 追加 2 行阴性登记（无序列）=裁定#446 定稿态形（有效+阴性守恒）
    mf = pd.read_csv(run / "manifest.csv")
    extra = mf.tail(2).copy()
    extra["recipe_id"] = ["neg_x", "neg_y"]
    extra["negative_note"] = "endogenous_zero_variance"
    pd.concat([mf, extra], ignore_index=True).to_csv(run / "manifest.csv", index=False)
    be = mod.load_cost_gate_params(repo / "config" / "exam_scale_cost_gate.yaml")
    c_star, evidence = mod._census_c_star(run, pd.read_csv(run / "manifest.csv"), be["breakeven"])
    assert len(c_star) == 6
    assert evidence["series_cells"] == 6 and evidence["auditable_negatives"] == 2
    assert all(0 < c <= 200 for c in c_star.values())


def test_v2_full_flow_green_dryrun(repo: Path):
    _write_exam_yaml(repo, v2=True)
    _mk_v2_run(repo, [(10.0, 10), (45.0, 50)])  # 幸存者中位=45bp>=40，P10=10>=0
    status, code = mod.run_handover(
        repo,
        allow_launch=False,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=_Recorder(),
        e0_gate=_e0_ok,
    )
    assert status == "GREEN_DRYRUN" and code == 0
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    verdict = yaml.safe_load((run / "handover_verdict.yaml").read_text(encoding="utf-8"))
    crit = verdict["criteria"]["cost_gate_spot"]
    assert crit["pass"] is True
    m = crit["measured"]
    assert m["active_version"] == "v2" and m["criterion_id"] == "G-COST-BREAKEVEN-40BP"
    assert m["gates"]["p1_median"]["state"] == "PASS"
    assert m["gates"]["p2_p10"]["state"] == "PASS"
    assert m["gates"]["p3_stratified"]["state"] == "INDETERM"  # 分层=T2 波次证据面，如实判灰
    assert m["gates"]["p4_scale"]["state"] == "INDETERM"
    assert m["tri_state"] == "INDETERM" and m["scope_fail"] == []
    assert m["survivors_k"] == 60 and m["n_candidates"] == 60
    assert "v1_parallel" in m


def test_v2_p1_fail_verdict_red(repo: Path):
    _write_exam_yaml(repo, v2=True)
    _mk_v2_run(repo, [(10.0, 50), (45.0, 10)])  # 中位=10bp<40 → P1 FAIL
    status, code = mod.run_handover(
        repo,
        allow_launch=False,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=_Recorder(),
        e0_gate=_e0_ok,
    )
    assert status == "VERDICT_RED" and code == 1
    run = repo / "data" / "strategy_intake" / "grid_20260925-111219"
    verdict = yaml.safe_load((run / "handover_verdict.yaml").read_text(encoding="utf-8"))
    assert verdict["criteria"]["cost_gate_spot"]["pass"] is False
    assert "cost_gate_spot" in verdict["blocking_criteria"]
    assert verdict["criteria"]["cost_gate_spot"]["measured"]["scope_fail"] == ["p1_median_bp_min"]


def test_v2_birthcert_tamper_fail_closed(repo: Path):
    _write_exam_yaml(repo, v2=True)
    run = _mk_v2_run(repo, [(45.0, 60)])
    mf = pd.read_csv(run / "manifest.csv")
    mf.loc[3, "sharpe"] = round(float(mf.loc[3, "sharpe"]) + 0.01, 3)  # 篡改出生证
    mf.to_csv(run / "manifest.csv", index=False)
    status, code = mod.run_handover(
        repo,
        allow_launch=False,
        proc_scan=_procs_nothing,
        gpu_probe=_gpu_free,
        replay_fn=_replay_ok,
        importance_fn=_fake_importance,
        launcher=_Recorder(),
        e0_gate=_e0_ok,
    )
    assert status == "VERDICT_RED" and code == 1
    verdict = yaml.safe_load((run / "handover_verdict.yaml").read_text(encoding="utf-8"))
    crit = verdict["criteria"]["cost_gate_spot"]
    assert crit["pass"] is False and "出生证校验败" in crit["measured"]["error"]
