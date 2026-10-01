# [BLUEPRINT] MOD-BT-IBT-REEXAM | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.reexam_cpcv_harness
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/translated/_c4_engine; zephyr.backtest.core.cpcv;
#   zephyr.backtest.core.n_trial_ledger; zephyr.backtest.regime_validation.exam_cost_gate;
#   zephyr.regime.validation.overfitting_guard; zephyr.simulation.deflated_sharpe_calculator
# [CONSUMERS] LANE-REEXAM 退役/在册策略重考首考批；Owner 复查窗
# [STARTUP] manual CLI
# [MATURITY] experimental
# [INVARIANTS] 判据单一真源=docs/_working/reexam_strategy_lane/pre_registration_card.md 内嵌
#   reexam_prereg_params_v1 块（sha256 锁，改卡=作废重开；跑前必验锁，不一致拒绝跑批）；
#   禁新造切分器/DSR/PBO 数学（一律委托 cpcv + MOD-SIM-024）；成本档引用
#   config/exam_scale_cost_gate.yaml 冻结件，本件不自设数值；同卷同纪=历史成绩列仅观察禁入判据；
#   闭卷窗 >closed_book_from 的数据禁用于判档；逐条串行+限线程（RAM 紧，禁 GPU）；
#   断点续跑禁覆盖已判格；材料不足判 INSUFFICIENT_MATERIAL 禁混入判负；
#   每批必入 N 账本（漏计=DSR 分母污染）；产物只写 docs/_working/reexam_strategy_lane/runs/
#   （.md/.csv/.yaml 三格式，DCR-005/006）；本件不接实盘不下单、不改 strategy_registry 状态
#   （过复活线只给"模拟盘试用资格"，转正归 Owner 门位）
# [MODIFY-GUARD] tests/backtest/test_reexam_cpcv_harness.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 预注册卡缺失/锁不匹配=SystemExit 非静默；单策略失败记 ERROR 行不中断全批；
#   账本故障不阻断重考本体但必须留痕
# [TESTS] tests/backtest/test_reexam_cpcv_harness.py
# [TTL] task_bound
# [A_module] module_id=MOD-BT-IBT-REEXAM | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""退役/在册策略重考 harness（LANE-REEXAM，CPCV + 多重检验三件套逐格报告）。

用法:
  python scripts/backtest/reexam_cpcv_harness.py --batch p1_translated_jq_outpool --limit 30
  python scripts/backtest/reexam_cpcv_harness.py --batch b2 --offset 30 --limit 30     # 断点续跑
  python scripts/backtest/reexam_cpcv_harness.py --pool-file my_ids.yaml --batch b3    # 指定池
纪律: 同卷同纪（禁套旧成绩）· 逐格出数字证据（禁"全绿"）· 负结果如实入账 · 判据只引用不改写。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "src", ROOT / "scripts" / "backtest" / "translated", ROOT / "scripts" / "backtest" / "ibt"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

CARD_PATH = ROOT / "docs" / "_working" / "reexam_strategy_lane" / "pre_registration_card.md"
RUNS_DIR = ROOT / "docs" / "_working" / "reexam_strategy_lane" / "runs"
PREREG_LOCK = ROOT / ".runtime" / "reexam" / "prereg_lock.json"
DEFERRALS_CSV = ROOT / "data" / "strategy_intake" / "c4_deferrals.csv"
TRANSLATED_DIR = ROOT / "scripts" / "backtest" / "translated"
CARD_BLOCK = "reexam_prereg_params_v1"
PREREG_NAME = "reexam_same_paper_same_discipline_v1"
PERIODS_PER_YEAR = 252


# ---------------------------------------------------------------------------
# 一、预注册卡读取 + 锁校验（判据漂移硬拦）
# ---------------------------------------------------------------------------
def load_card_params(card_path: Path = CARD_PATH) -> tuple[dict, str]:
    """抽取卡内 fenced yaml 参数块，返回 (params, sha256)。

    fail-closed：卡缺失/块缺失/块非法 yaml 一律 SystemExit——判据不在=不得开考。
    """
    if not card_path.exists():
        raise SystemExit(f"FAIL: 预注册卡缺失 {card_path}（无卡不开考）")
    text = card_path.read_text(encoding="utf-8")
    m = re.search(r"```yaml\s*\n(" + CARD_BLOCK + r":.*?)\n```", text, re.S)
    if not m:
        raise SystemExit(f"FAIL: 卡内未找到 ```yaml {CARD_BLOCK} 参数块")
    params = yaml.safe_load(m.group(1))
    if not isinstance(params, dict) or CARD_BLOCK not in params:
        raise SystemExit("FAIL: 预注册参数块解析失败")
    blob = yaml.safe_dump(params, sort_keys=True, allow_unicode=True)
    return params[CARD_BLOCK], hashlib.sha256(blob.encode("utf-8")).hexdigest()


def verify_or_register_prereg(params: dict, digest: str, lock_path: Path = PREREG_LOCK) -> dict:
    """首跑登记 hash，复跑核验一致；不一致=判据变更 → 拒跑（须作废重开新卡）。"""
    from zephyr.regime.validation.overfitting_guard import PreRegistrationRegistry

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    reg = PreRegistrationRegistry(lock_path)
    try:
        reg.register(PREREG_NAME, {"sha256": digest, "params": params}, note="LANE-REEXAM 同卷同纪 v1")
        action = "registered"
    except RuntimeError:
        if not reg.verify(PREREG_NAME, {"sha256": digest, "params": params}):
            raise SystemExit(
                f"FAIL: 预注册卡与已登记锁不一致（{PREREG_NAME}）——判据已变更，"
                "本卡成绩全部作废，须升 schema_version 重开新预注册后考"
            ) from None
        action = "verified"
    return {"name": PREREG_NAME, "sha256": digest, "action": action}


# ---------------------------------------------------------------------------
# 二、池解析（可执行子集；在册 139 candidate 无 code_path，首考用外部代理批）
# ---------------------------------------------------------------------------
def _md5_of(fname: str) -> str:
    # c4_<md5_12>_<slug>.py
    parts = fname[:-3].split("_")
    return parts[1] if fname.startswith("c4_") and len(parts) >= 3 else ""


def resolve_pool(pool_file: Path | None, limit: int, offset: int) -> tuple[list[dict], dict]:
    """返回 (待考清单, 池披露)。单一真源=译件目录 ∩ 出局账本 ∪ ibt POOL（禁复制名单）。"""
    disclosed: dict = {}
    if pool_file is not None:
        rows = yaml.safe_load(pool_file.read_text(encoding="utf-8")) or []
        disclosed["source"] = str(pool_file.relative_to(ROOT))
        return rows[offset : offset + limit], disclosed

    out_md5: set[str] = set()
    if DEFERRALS_CSV.exists():
        import csv as _csv

        with DEFERRALS_CSV.open(encoding="utf-8-sig") as fh:
            out_md5 = {r["md5_12"] for r in _csv.DictReader(fh) if r.get("md5_12")}
    pool_md5: set[str] = set()
    try:
        from ibt_mining_matrix import POOL  # 单一真源（禁复制）

        pool_md5 = {row[1] for row in POOL}
        disclosed["ibt_pool_n"] = len(POOL)
    except Exception as exc:  # noqa: BLE001
        disclosed["ibt_pool_error"] = f"{type(exc).__name__}: {exc}"

    files = sorted(p.name for p in TRANSLATED_DIR.glob("c4_*.py"))
    disclosed["translated_total"] = len(files)
    sel = []
    seen: set[str] = set()
    for f in files:
        m12 = _md5_of(f)
        if not m12 or (m12 not in out_md5 and f not in pool_md5):
            continue
        # candidate_id 必须逐件唯一：同一 md5 可有多个变体件（如 value55/value_improved），
        # 只按 md5 编号会让 state.yaml 断点键相互覆盖（首考前实测 4 组撞名）
        slug = f[:-3].split("_", 2)[2] if len(f[:-3].split("_", 2)) > 2 else f[:-3]
        cid = f"JQ-{m12}-{slug}"
        n, k = 1, cid
        while k in seen:
            n, k = n + 1, f"{cid}-{n}"
        seen.add(k)
        sel.append(
            {
                "candidate_id": k,
                "file": f,
                "origin": "jq_outpool" if m12 in out_md5 else "jq_other",
                "backlink": "c4_deferrals.csv" if m12 in out_md5 else "ibt_mining_matrix.POOL",
            }
        )
    disclosed.update(deferrals_n=len(out_md5), selected_n=len(sel), unique_ids=len(seen))
    return sel[offset : offset + limit], disclosed


def load_strategy_module(fname: str):
    spec = importlib.util.spec_from_file_location("reex_" + Path(fname).stem, TRANSLATED_DIR / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for attr in ("STRATEGY_ID", "WINDOW_KIND", "build"):
        if not hasattr(mod, attr):
            # MSG-EXPOSURE：文件名走结构化载体不入消息文本——缺属性点位由 attr 定位，
            # 具体卷册由调用方（本 harness 卷清单）持有，不在此暴露路径信息。
            raise AttributeError(f"策略译册缺契约属性 {attr}（TRANSLATED_DIR 装载面）")
    return mod


def _norm_frame(frame: pd.DataFrame) -> pd.DataFrame:
    frame.index = pd.to_datetime(pd.Index(frame.index))
    frame.columns = [str(c).split(".")[0] for c in frame.columns]
    return frame


# ---------------------------------------------------------------------------
# 三、单卷逐格指标（三件套委托既有件，本件只装配）
# ---------------------------------------------------------------------------
def annualized_sharpe(rets: np.ndarray) -> float:
    rets = np.asarray(rets, dtype=float)
    if rets.size < 2:
        return float("nan")
    sd = rets.std(ddof=1)
    if sd <= 0 or not math.isfinite(sd):
        return float("nan")
    return float(rets.mean() / sd * math.sqrt(PERIODS_PER_YEAR))


def cpcv_trial_matrices(ret_mat: np.ndarray, cfg: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    """CPCV 切分（委托 generate_cpcv_splits）→ IS/OOS 年化 Sharpe 矩阵 (n_splits × n_trials)。"""
    from zephyr.backtest.core.cpcv import generate_cpcv_splits

    n, m = ret_mat.shape
    cp = cfg["cpcv"]
    horizon = int(cp["t1_horizon_daily"])
    splits = generate_cpcv_splits(
        n,
        int(cp["n_groups"]),
        int(cp["k_test"]),
        t1=[min(n - 1, i + horizon) for i in range(n)],
        embargo=int(cp["embargo_days"]),
    )
    is_m = np.full((len(splits), m), np.nan)
    oos_m = np.full((len(splits), m), np.nan)
    for s in splits:
        tr = np.asarray(s.train_indices, dtype=int)
        te = np.asarray(s.test_indices, dtype=int)
        for j in range(m):
            # ret_mat 轴向=（样本 × 试次）：切分索引取行（时间轴），试次取列
            is_m[s.split_id, j] = annualized_sharpe(ret_mat[tr, j])
            oos_m[s.split_id, j] = annualized_sharpe(ret_mat[te, j])
    return (
        is_m,
        oos_m,
        {
            "n_splits": len(splits),
            "train_min": int(min(len(s.train_indices) for s in splits)),
            "test_min": int(min(len(s.test_indices) for s in splits)),
        },
    )


def family_pbo(is_m: np.ndarray, oos_m: np.ndarray) -> dict:
    """PBO（委托 compute_pbo）；NaN 格（薄样本无 Sharpe）按 0 收益兜底并如实披露兜底数。"""
    from zephyr.backtest.core.cpcv import compute_pbo

    nan_n = int(np.isnan(is_m).sum() + np.isnan(oos_m).sum())
    a = np.nan_to_num(is_m, nan=0.0)
    b = np.nan_to_num(oos_m, nan=0.0)
    try:
        res = compute_pbo(a, b)
    except Exception as exc:  # noqa: BLE001 — PBO 不可算不得伪装成 0
        return {"pbo": None, "error": f"{type(exc).__name__}: {exc}", "nan_cells": nan_n}
    res["nan_cells_imputed_zero"] = nan_n
    return res


def per_trial_trio(ret_mat: np.ndarray, cfg: dict, n_trials_total: int) -> list[dict]:
    """逐格 haircut/DSR/稳健分；rank 按全期年化 Sharpe 的 t 降序（HTL Bonferroni 加权口径）。"""
    from zephyr.simulation.deflated_sharpe_calculator import (
        deflated_sharpe_from_moments,
        haircut_sharpe_harvey_liu,
    )

    thr = cfg["thresholds"]
    n = ret_mat.shape[0]
    rows: list[dict] = []
    stats = []
    for j in range(ret_mat.shape[1]):
        r = ret_mat[:, j]
        sr_p = float(r.mean() / r.std(ddof=1)) if r.std(ddof=1) > 0 else float("nan")
        stats.append((sr_p, float(pd.Series(r).skew()), float(pd.Series(r).kurt()), annualized_sharpe(r)))
    order = sorted(range(len(stats)), key=lambda i: -(stats[i][0] if math.isfinite(stats[i][0]) else -9e9))
    rank_of = {i: k + 1 for k, i in enumerate(order)}
    robust_from = 0.5  # 卡未锁稳健分线→仅观察披露，不入判据（禁自造阈值）
    for i, (sr_p, sk, ku, sr_ann) in enumerate(stats):
        if not math.isfinite(sr_p):
            rows.append({"degenerate": True, "reason": "零方差/薄样本=Sharpe 无定义"})
            continue
        hc = haircut_sharpe_harvey_liu(sr_p, n, n_trials_total, rank_of[i], skewness=sk, excess_kurtosis=ku, alpha=0.05)
        _, dsr, emz, deg = deflated_sharpe_from_moments(sr_p, n_trials_total, n, skewness=sk, excess_kurtosis=ku)
        rows.append(
            {
                "sharpe_period": round(sr_p, 6),
                "sharpe_annualized": round(sr_ann, 4) if math.isfinite(sr_ann) else None,
                "skew": round(sk, 4),
                "excess_kurt": round(ku, 4),
                "rank": rank_of[i],
                "haircut_sharpe": None if hc.degenerate else round(hc.haircut_sharpe, 6),
                "haircut_t": None if hc.degenerate else round(hc.t_stat, 4),
                "haircut_critical_t": round(hc.critical_t, 4),
                "haircut_pass": bool(hc.survives),
                "dsr": None if deg else round(dsr, 6),
                "dsr_pass": (not deg) and dsr >= float(thr["dsr_min"]),
                "dsr_degenerate": bool(deg),
                "expected_max_z": round(emz, 4),
                "robust_score_obs": None,
                "min_obs_floor_ok": n >= int(cfg["cost"]["min_days"]),
            }
        )
    _ = robust_from
    return rows


def robust_scores_of_oos(oos_m: np.ndarray, ids: list[str]) -> dict[str, float]:
    """稳健分（委托 compute_robust_scores 同族秩口径的等价实现——本件不重造秩，仅折列）。"""
    from zephyr.backtest.core.strategy_cpcv_matrix import _average_ranks_descending  # noqa: SLF001

    out: dict[str, float] = {}
    if oos_m.size == 0:
        return out
    acc = {i: [] for i in range(len(ids))}
    for s in range(oos_m.shape[0]):
        row = np.nan_to_num(oos_m[s], nan=0.0)
        rk = _average_ranks_descending(row) / len(ids)
        for j, v in enumerate(rk):
            acc[j].append(float(v))
    for j, sid in enumerate(ids):
        out[sid] = round(float(np.mean(acc[j])), 4)
    return out


# ---------------------------------------------------------------------------
# 四、判档
# ---------------------------------------------------------------------------
def adjudicate(row: dict, cost: dict, pbo_pass: bool, cfg: dict) -> tuple[str, list[str]]:
    thr = cfg["thresholds"]
    if row.get("material_insufficient"):
        return "INSUFFICIENT_MATERIAL", [row.get("reason", "材料不足")]
    fails: list[str] = []
    if bool(thr.get("cost_gate_required")) and not cost.get("passed", False):
        fails.append("cost_gate:" + "|".join(cost.get("reasons") or ["未过"]))
    if not row.get("haircut_pass", False):
        fails.append(f"haircut_sharpe(折后={row.get('haircut_sharpe')})")
    if not row.get("dsr_pass", False):
        fails.append(f"dsr(={row.get('dsr')}，线={thr['dsr_min']})")
    if not pbo_pass:
        fails.append("pbo(族级)")
    if not row.get("min_obs_floor_ok", True):
        fails.append(f"obs<{cfg['cost']['min_days']} 证据地板")
    return ("REVIVAL_CANDIDATE" if not fails else "RETAIN_RETIRED"), fails


# ---------------------------------------------------------------------------
# 五、N 账本 + 落盘
# ---------------------------------------------------------------------------
def record_ledger(batch: str, start: str, end: str, n_trials: int, session: str) -> str:
    try:
        from zephyr.backtest.core.n_trial_ledger import TrialLedger

        TrialLedger().record_run(
            kind="reexam_cpcv_harness",
            batch_id=f"{batch}_{start}_{end}",
            n_trials=int(n_trials),
            note=f"LANE-REEXAM 同卷同纪 CPCV 三件套重考 window={start}..{end}",
            recorded_by=session,
        )
        return "recorded"
    except Exception as exc:  # noqa: BLE001 — 账本故障不阻断重考本体，但必须留痕
        return f"ledger_error: {type(exc).__name__}: {exc}"


def ledger_cumulative() -> int | None:
    try:
        from zephyr.backtest.core.n_trial_ledger import TrialLedger

        led = TrialLedger()
        for name in ("cumulative_trials", "total_trials", "cumulative_n", "n_total"):
            if hasattr(led, name):
                return int(getattr(led, name))
        return None
    except Exception:  # noqa: BLE001
        return None


def _neg_row(cell: dict, batch: str, cfg: dict) -> dict:
    """负结果行按预注册卡 §六 列契约落盘（禁把整坨观察字段冒充负结果账）。"""
    win = cfg["universe"]["daily_window"]
    measured = {
        "sharpe_annualized": cell.get("sharpe_annualized"),
        "haircut_sharpe": cell.get("haircut_sharpe"),
        "dsr": cell.get("dsr"),
        "pbo_family": cell.get("pbo_family"),
        "days": cell.get("days"),
        "robust_score_obs": cell.get("robust_score_obs"),
    }
    return {
        "batch_id": batch,
        "candidate_id": cell.get("candidate_id"),
        "scope": "family_cpcv" if any("pbo" in str(x) for x in cell.get("failed_criteria") or []) else "per_cell",
        "failed_criterion": ";".join(str(x) for x in cell.get("failed_criteria") or []),
        "measured": measured,
        "window": f"{win[0]}..{win[1]}",
        "caliber": cfg["cost"]["engine_caliber"],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _write(
    out_dir: Path,
    batch: str,
    cfg: dict,
    disclosed: dict,
    prereg: dict,
    cells: list[dict],
    negatives: list[dict],
    family: dict,
    started: str,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "reexam_cpcv_harness/v1",
        "batch_id": batch,
        "lane": "LANE-REEXAM",
        "pre_registration": prereg,
        "criteria_source": str(CARD_PATH.relative_to(ROOT)) + " §五（frozen 件禁改，本件零自造阈值）",
        "honest_limits": {
            "pre_2019_universe": "2019 前日线/stk_limit 实测仅约 230-240 只存根宇宙，不构成全市场考核",
            "minute": "kline_1min 实测起点 2021-09-01",
            "etf": "kline_etf_daily 2021-2025 仅 1 只标的（159865）→ ETF 族判材料不足",
            "inregister_candidates": "在册 139 candidate 全部 code_path 空=当前不可直接考试（须先蒸馏成代码件）",
        },
        "window": {
            "start": cfg["universe"]["daily_window"][0],
            "end": cfg["universe"]["daily_window"][1],
            "closed_book_after": cfg["universe"]["closed_book_from"],
        },
        "pool": disclosed,
        "family_metrics": family,
        "counts": {
            "cells": len(cells),
            "negatives": len(negatives),
            "revival_candidate": sum(1 for c in cells if c["verdict"] == "REVIVAL_CANDIDATE"),
            "insufficient_material": sum(1 for c in cells if c["verdict"] == "INSUFFICIENT_MATERIAL"),
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at_utc": started,
        "caliber_note": "同卷同纪：历史 sharpe 列仅观察禁入判据；逐格出数字证据禁全绿表述",
    }
    (out_dir / "report.yaml").write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
    _csv(out_dir / "cells.csv", cells)
    _csv(out_dir / "negatives.csv", negatives)  # 零阴性也带表头
    return report


NEGATIVE_COLUMNS = [
    "batch_id",
    "candidate_id",
    "scope",
    "failed_criterion",
    "measured",
    "window",
    "caliber",
    "generated_at",
]


def _ret_path(out_dir: Path, cid: str) -> Path:
    return out_dir / f"ret_{cid}.csv"


def _save_ret(out_dir: Path, cid: str, rets: pd.Series) -> None:
    """断点必需件落盘：净收益序列（族卷重算的唯一材料），CSV 格式（DCR-006 允许面）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    rets.rename("net_ret").to_csv(_ret_path(out_dir, cid), encoding="utf-8")


def _load_ret(out_dir: Path, cid: str) -> pd.Series | None:
    path = _ret_path(out_dir, cid)
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
    except Exception:  # noqa: BLE001 — 残件不可信=视同缺失，走重算
        return None
    if df.empty or "net_ret" not in df.columns:
        return None
    return df["net_ret"].astype(float)


def _csv(path: Path, rows: list[dict]) -> None:
    import csv as _csv

    flat = [
        {k: (v if not isinstance(v, (dict, list)) else yaml.safe_dump(v, allow_unicode=True)) for k, v in r.items()}
        for r in rows
    ]
    cols = sorted({k for r in flat for k in r}) or NEGATIVE_COLUMNS
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = _csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()  # 零阴性也必须带表头（下游 pd.read_csv 禁得单匿名列）
        w.writerows(flat)


# ---------------------------------------------------------------------------
# 六、主流程
# ---------------------------------------------------------------------------
def run_batch(batch: str, pool_file: Path | None, limit: int, offset: int, out_root: Path) -> int:
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cfg, digest = load_card_params()
    prereg = verify_or_register_prereg(cfg, digest)
    print(f"[prereg] {prereg['action']} sha256={digest[:16]}…", flush=True)

    from _c4_engine import daily_net_returns, run_backtest  # 引擎口径唯一（冻结土规）

    from zephyr.backtest.regime_validation.exam_cost_gate import (
        CostGateConfig,
        evaluate_exam_cost_gate,
        run_cost_tier_scan,
    )
    from zephyr.regime.validation.overfitting_guard import walk_forward_efficiency

    gate_raw = yaml.safe_load((ROOT / "config" / "exam_scale_cost_gate.yaml").read_text(encoding="utf-8"))
    cg, tg = gate_raw["cost_gate"], gate_raw["turnover_gate"]
    gate_cfg = CostGateConfig(
        tiers_bp=tuple(cg["tiers_bp"]),
        survival_floor=float(cg["survival_floor"]),
        monotonic_tol=float(cg["monotonic_tol"]),
        min_days=int(cg["min_days"]),
        turnover_cap_annual_x=float(tg["cap_annual_x"]),
        turnover_days_basis=int(tg["days_basis"]),
    )
    assert list(cg["tiers_bp"]) == list(cfg["cost"]["tiers_bp"]), "卡与 frozen 成本件档位不一致=判据漂移"

    sel, disclosed = resolve_pool(pool_file, limit, offset)
    out_dir = out_root / batch
    state_path = out_dir / "state.yaml"
    done: dict[str, dict] = {}
    if state_path.exists():
        done = {
            d["candidate_id"]: d for d in (yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}).get("done", [])
        }
        disclosed["resumed_from"] = len(done)

    start, end = cfg["universe"]["daily_window"]
    rows: list[dict] = []
    costs: dict[str, dict] = {}
    series: dict[str, pd.Series] = {}
    restored = recomputed = 0
    for item in sel:
        cid, fname = item["candidate_id"], item["file"]
        if cid in done:
            prev = dict(done[cid])
            cost_prev = prev.pop("_cost", None)
            ret_prev = _load_ret(out_dir, cid)
            # 断点行只有标量观察值；族卷必需"净收益序列 + 成本档结果"：
            #   材料不足/执行错误格本就无序列，断点行即终态 → 直接复原；
            #   合格格缺任一必需件 → 重算，禁把缺材料的格子静默留在卷外
            #   （否则 resume 后 PBO/三件套只在残卷上算=假考，本车道接手夜实测定格）
            if prev.get("material_insufficient"):
                if cost_prev is not None:
                    costs[cid] = cost_prev
                restored += 1
                rows.append(prev)
                continue
            if cost_prev is not None and ret_prev is not None:
                costs[cid] = cost_prev
                series[cid] = ret_prev
                restored += 1
                rows.append(prev)
                continue
            recomputed += 1
            print(f"[{cid}] resume 必需件缺失（净收益序列/成本档）→ 重算，不残卷计入", flush=True)
        row: dict = {"candidate_id": cid, "file": fname, "origin": item.get("origin")}
        try:
            mod = load_strategy_module(fname)
            w, c = mod.build(start, end)
            w = _norm_frame(pd.DataFrame(w).copy()).fillna(0.0)
            c = _norm_frame(pd.DataFrame(c).copy())
            if w.empty or float(w.abs().to_numpy().sum()) <= 0:
                row.update({"material_insufficient": True, "reason": "窗内零信号=材料不足（非判负）"})
            else:
                rets = daily_net_returns(w, c).astype(float)
                rets = rets[rets.index <= pd.Timestamp(end)]
                if len(rets) < int(cfg["cost"]["min_days"]):
                    row.update({"material_insufficient": True, "reason": f"净收益日数 {len(rets)} < 证据地板"})
                else:
                    stats = run_backtest(w, c)
                    tiers = run_cost_tier_scan(w, c, daily_net_returns, gate_cfg)
                    v = evaluate_exam_cost_gate(
                        tiers,
                        mean_daily_turnover_1side=float(stats.get("avg_turnover_1side", 0.0)),
                        days=int(stats.get("days", 0)),
                        config=gate_cfg,
                    )
                    costs[cid] = {
                        "passed": bool(v.passed),
                        "reasons": list(v.reasons),
                        "tier_sharpes": {str(k): val for k, val in v.tier_sharpes.items()},
                        "annual_turnover_x": v.annual_turnover_x,
                        "monotonic": v.monotonic,
                        "full_cost_survived": v.full_cost_survived,
                    }
                    row.update(
                        {
                            "material_insufficient": False,
                            "days": int(stats.get("days", len(rets))),
                            "frozen_caliber_sharpe_obs": stats.get("sharpe"),
                            "window_obs": str(getattr(mod, "WINDOW_KIND", "")),
                        }
                    )
                    series[cid] = rets
        except Exception as exc:  # noqa: BLE001 — 单件失败不中断全批，但必须出声
            row.update({"material_insufficient": True, "reason": f"执行失败 {type(exc).__name__}: {exc}"})
            costs[cid] = {"passed": False, "reasons": ["execution_error"]}
        rows.append(row)
        print(
            f"[{cid}] {'INSUFF' if row.get('material_insufficient') else 'OK'} {row.get('reason', '')}"
            f"{'' if cid not in costs else ' cost=' + ('PASS' if costs[cid]['passed'] else 'FAIL')}",
            flush=True,
        )
        if cid in series:
            _save_ret(out_dir, cid, series[cid])
        done[cid] = {**row, **({"_cost": costs[cid]} if cid in costs else {})}
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            yaml.safe_dump({"done": list(done.values())}, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        # 分批落盘纪律（2026-09-25 收割器事故处方：末尾才写=击杀即全损）：
        # 逐格刷新进度件（非判据件，禁与 report.yaml 混读）
        (out_dir / "progress.yaml").write_text(
            yaml.safe_dump(
                {
                    "batch_id": batch,
                    "cells_done": len(done),
                    "cells_selected": len(sel),
                    "material_in_book": len(series),
                    "offset": offset,
                    "limit": limit,
                    "resume_restored": restored,
                    "resume_recomputed": recomputed,
                    "updated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "note": "进度件，非判据；三件套与三态只在批末 report.yaml 出",
                },
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    disclosed["resume_restored"] = restored
    disclosed["resume_recomputed"] = recomputed

    ids = [r["candidate_id"] for r in rows if r["candidate_id"] in series]
    fam: dict = {"note": "无合格样本卷，未算 CPCV/三件套"}
    if len(ids) >= 2:
        idx = series[ids[0]].index
        for s in series.values():
            idx = idx.intersection(s.index)
        mat = np.column_stack([series[i].reindex(idx).to_numpy() for i in ids])
        n_trials_cum = ledger_cumulative()
        n_trials_total = int(n_trials_cum or 0) + len(ids)
        is_m, oos_m, cut = cpcv_trial_matrices(mat, cfg)
        pbo = family_pbo(is_m, oos_m)
        rob = robust_scores_of_oos(oos_m, ids)
        trio = per_trial_trio(mat, cfg, n_trials_total)
        thr = cfg["thresholds"]
        pbo_val = pbo.get("pbo")
        pbo_pass = pbo_val is not None and pbo_val <= float(thr["pbo_max"])
        wfe_vals = []
        for j in range(len(ids)):
            a, b = np.nanmean(is_m[:, j]), np.nanmean(oos_m[:, j])
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                wfe_vals.append(walk_forward_efficiency(float(b), float(a)))
        fam = {
            "n_trials_in_book": len(ids),
            "n_trials_ledger_cumulative": n_trials_cum,
            "n_trials_used_for_correction": n_trials_total,
            "cpcv": {"n_groups": cfg["cpcv"]["n_groups"], "k_test": cfg["cpcv"]["k_test"], **cut},
            "pbo": {
                k: pbo[k] for k in ("pbo", "mean_logit", "n_splits", "n_trials", "nan_cells_imputed_zero") if k in pbo
            }
            | ({"error": pbo["error"]} if "error" in pbo else {}),
            "pbo_threshold": thr["pbo_max"],
            "pbo_pass": bool(pbo_pass),
            "wfe_mean": round(float(np.mean(wfe_vals)), 4) if wfe_vals else None,
            "wfe_threshold": thr["wfe_min"],
        }
        for r in rows:
            cid = r["candidate_id"]
            if cid not in ids:
                # 族外格（材料不足/零信号/执行错误）也必须有判档：_write 按 c["verdict"] 计数，
                # 缺键=整批 report.yaml 在跑完数小时后 KeyError 崩（本车道接手夜实测复现）
                r["verdict"], r["failed_criteria"] = adjudicate(r, costs.get(cid, {}), pbo_pass, cfg)
                continue
            t = trio[ids.index(cid)]
            r.update(t)
            r["pbo_family"] = pbo_val
            r["robust_score_obs"] = rob.get(cid)
            r["cost_passed"] = costs.get(cid, {}).get("passed")
            verdict, fails = adjudicate(r, costs.get(cid, {}), pbo_pass, cfg)
            r["verdict"], r["failed_criteria"] = verdict, fails
    else:
        for r in rows:
            r.setdefault("verdict", "INSUFFICIENT_MATERIAL")
            r.setdefault("failed_criteria", ["卷内合格样本 <2，族级 PBO 不可算"])

    negatives = [_neg_row(r, batch, cfg) for r in rows if r.get("verdict") == "RETAIN_RETIRED"]
    report = _write(out_dir, batch, cfg, disclosed, prereg, rows, negatives, fam, started)
    if ids:
        report["n_trial_ledger"] = record_ledger(batch, start, end, len(ids), "st-qmine-20260925")
    (out_dir / "report.yaml").write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(
        f"[done] {out_dir}/report.yaml | cells={report['counts']} | ledger={report.get('n_trial_ledger')}", flush=True
    )
    return 0


def main() -> int:
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        # RAM 余 ~19GB 且 T1 在跑——并发红线（预注册卡 §七）
        import os

        os.environ.setdefault(k, "2")
    ap = argparse.ArgumentParser(description="退役/在册策略 CPCV 三件套重考 harness")
    ap.add_argument("--batch", required=True)
    ap.add_argument("--pool-file", default=None)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--out-root", default=str(RUNS_DIR))
    a = ap.parse_args()
    card_cap = int(load_card_params()[0]["batch"]["batch_cap"])
    if a.limit > card_cap:
        raise SystemExit(f"FAIL: --limit {a.limit} 越出预注册 batch_cap {card_cap}（限额分批纪律）")
    return run_batch(a.batch, Path(a.pool_file) if a.pool_file else None, int(a.limit), int(a.offset), Path(a.out_root))


if __name__ == "__main__":
    raise SystemExit(main())
