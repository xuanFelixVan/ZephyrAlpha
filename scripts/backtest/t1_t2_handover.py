# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（MOD-BT-196 执行器之交接姊妹件）
# [MODULE] scripts.backtest.t1_t2_handover
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor（发车 CLI 沿用）; scripts.backtest.factory_grid_anova（主效应重要性）;
#   scripts.backtest.compute_window_gate（E0 问闸复用）; zephyr.backtest.regime_validation.exam_cost_gate（五档真扫描）;
#   config/search_space_prereg.yaml + config/exam_scale_cost_gate.yaml（阈值真源，禁双头硬编码）
# [CONSUMERS] 30 分钟薄壳自动化（qoder cron，总筹建）；LANE-AUTO 案卷 AUTO_t1_t2_handover.md
# [STARTUP] auto（外部调度器周期调用；本件自身无常驻循环——每次调用=一次有界幂等检查）
# [MATURITY] experimental
# [INVARIANTS] 幂等：同一 manifest 重复调用必产出同一 verdict/subspace（确定性算法+固定种子）；
#   判据口径真源=docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §一，本件只执行不改阈值；
#   claim 文件 O_EXCL 原子创建防双发 T2（单卡禁共存 prereg vram.concurrency=1）；发车前 E0 问闸+GPU 独占探测，
#   任一不过=DEFERRED 并撤销本次 claim（下轮重试）；本件永不重启/击杀任何在跑作业（T1_DIED 只报告不处置）；
#   正式跑批禁跳 E0 问闸——本件在问闸拒绝时同样不发车
# [MODIFY-GUARD] tests/backtest/test_t1_t2_handover.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(0)=WAITING/DEFERRED/ALREADY_CLAIMED/LAUNCHED 等正常态；
#   SystemExit(1)=T1_DIED/VERDICT_RED/NO_RUN_DIR/STALE_CLAIM/LAUNCH_FAILED（需人/总筹介入）；
#   RuntimeError(判据输入非法/回放失败)；ValueError(subspace 非法)
# [TESTS] tests/backtest/test_t1_t2_handover.py
# [A_module] module_id=MOD-BT-T1T2-HANDOVER | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  有界批处理交接件：每次调用一遍检查即退出，无常驻状态/无自动循环，
#   周期触发由外部调度器（总筹注册的薄壳任务）承担——本件本体保持 pull-once 语义
"""T1→T2 守望交接件（LANE-AUTO，2026-09-25 断链重建）。

替代件：上一轮总指挥的自然语言"守望器自动化"（每 30 分钟：GPU T1 完赛自动验收→
自动发 T2 900 格→自删）。该自动化从未落地为代码（qoder_cron list 实测无此任务，
12:00-13:00 窗口零执行痕迹）——本件把它变成仓内可测代码，薄壳自动化只需一行调用。

幂等状态机（每次调用输出一行 STATUS=<token> 供调度侧机读）：
  1  定位最新 t1 run（data/strategy_intake/grid_*；--t1-run 可显式指定）；
  2  claim 在场→ALREADY_CLAIMED（防双发 T2 的头号护栏；未发车且超时限→STALE_CLAIM 交人）；
  3  manifest.csv 缺：T1 进程在→WAITING(0)；进程亡→T1_DIED(1)+日志尾部指针（不自动重启不处置）；
  4  manifest 在→逐条跑 17 号文 §一验收判据→handover_verdict.yaml（机读 measured/threshold/pass
     + 垃圾触发线；verdict 缓存以 manifest sha256 为键，绿则不重做五档重放）；
  5  全过→确定性构造 T2 子空间 JSON（选层规则=案卷 AUTO_t1_t2_handover.md §四，可复算）；
  6  发车序列：claim 原子创建 → GPU 独占探测 → E0 问闸；任一不过→撤销本次 claim→DEFERRED(0)；
  7  沿用执行器 CLI 无窗脱管子进程发 `--stage t2 --subspace-json <file>`（预算帽/全档成本门/
     E0 由执行器自身 fail-closed），cmdline 子串确保在 process_reaper_keep.txt 在册，
     短窗观察即 LAUNCHED(0)/LAUNCH_FAILED(1，撤 claim 供下轮重试)。

用法（薄壳自动化可直接执行）：
  python scripts/backtest/t1_t2_handover.py                 # 全周期（该发车则发车）
  python scripts/backtest/t1_t2_handover.py --dry-run       # 只验收+落 subspace，不发车不认领
  python scripts/backtest/t1_t2_handover.py --release-claim --t1-run grid_<ts>   # 人工解锁
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import yaml

_REPO_DEFAULT = Path(__file__).resolve().parents[2]
_TZ = ZoneInfo("Asia/Shanghai")

# ---- 判据常数（口径真源=17 号文 §一 + prereg/exam_scale_cost_gate YAML；此处只引用不发明）----
N_EFF_FLOOR = 12.0  # 17 号文 §一"有效样本 N_eff≥12（T0 实测口径）"
SPOT_CHECK_N = 50  # 17 号文 §一"抽查 ≥50 格五档全真跑"（下界=50，不多测省算力）
SPOT_CHECK_SEED = 20260925  # 确定性抽样种子（同 manifest 必抽同格集）
TOP_SHARE = 0.20  # prereg tier2_points 注"主效应前 20% 层"
GARBLE_COMPLETION_LT = 0.95  # 垃圾触发线：完成率<95%
GARBLE_DEATH_GT = 0.01  # 垃圾触发线：死亡率>1%
GARBLE_SHARPE_GT = 2.0  # 垃圾触发线：sharpe>2 的格子（好得可疑）
GARBLE_SHARPE_SHARE_GT = 0.05  # 占比>5%
CLAIM_STALE_HOURS = 6.0  # 未发车 claim 超此时限=僵尸认领，交人（禁自动删）
LAUNCH_OBSERVE_SECONDS = 25  # 发车后短窗观察（E0 拒/秒崩在此暴露）
MONOTONIC_TOL_FALLBACK = 1.0e-9  # 仅当 exam 配置缺键时兜底（真源=config/exam_scale_cost_gate.yaml）
REAPER_KEEP_SUBSTRING = "factory_grid_executor"  # T2 走同一入口脚本，keep 子串即 cmdline 子串
GPU_BUSY_EXECUTOR_SUBSTRINGS = ("factory_grid_executor.py",)  # 独占探测命中面（发车前存在即拒）


# --------------------------------------------------------------------------- 基础读取
def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_text(path: Path, text: str) -> None:
    """原子落盘（tmp+os.replace）——守望器 30 分钟一巡，禁半截文件被下轮误读。"""
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_prereg_caps(prereg_path: Path) -> dict:
    """prereg budget_caps + 搜索窗（fail-closed：缺册/缺 tier 点数即抛）。"""
    if not prereg_path.exists():
        raise RuntimeError(f"prereg 缺失: {prereg_path}（预注册真源不在=禁一切交接动作）")
    cfg = yaml.safe_load(prereg_path.read_text(encoding="utf-8")) or {}
    caps = cfg.get("budget_caps") or {}
    if "tier1_points" not in caps or "tier2_points" not in caps:
        raise RuntimeError("prereg budget_caps 缺 tier1_points/tier2_points——禁交接")
    win = (((cfg.get("tracks") or {}).get("f06_grid") or {}).get("condition_stratification") or {}).get("search_window")
    win = win or ["2019-01-04", "2025-09-09"]
    return {
        "tier1_points": int(caps["tier1_points"]),
        "tier2_points": int(caps["tier2_points"]),
        "search_window": [str(win[0]), str(win[1])],
    }


def load_cost_gate_params(exam_cfg_path: Path) -> dict:
    """全档/存活地板/单调容差真源（config/exam_scale_cost_gate.yaml，禁双头改）。"""
    cfg = (yaml.safe_load(exam_cfg_path.read_text(encoding="utf-8")) or {}).get("cost_gate") or {}
    return {
        "tiers": [float(t) for t in (cfg.get("tiers_bp") or [0, 5, 10, 20, 40])],
        "survival_floor": float(cfg.get("survival_floor", 0.0)),
        "monotonic_tol": float(cfg.get("monotonic_tol", MONOTONIC_TOL_FALLBACK)),
    }


# --------------------------------------------------------------------------- 进程/GPU 探测
def scan_processes_default() -> list[tuple[int, str]]:
    """(pid, cmdline) 清单。psutil 不可用=抛错（fail-closed：判"进程亡"必须有证据）。"""
    try:
        import psutil
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("psutil 不可用——无法证明 T1 进程生死，禁判死也禁发车") from exc
    out: list[tuple[int, str]] = []
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            cl = " ".join(p.info["cmdline"] or [])
            if cl:
                out.append((int(p.info["pid"]), cl))
        except Exception:  # noqa: BLE001 进程瞬亡/权限：跳过该条不崩探测
            continue
    return out


def _stage_token(cmdline: str) -> str | None:
    tok = cmdline.split()
    for i, a in enumerate(tok):
        if a == "--stage" and i + 1 < len(tok):
            return tok[i + 1]
        if a.startswith("--stage="):
            return a.split("=", 1)[1]
    return None


def t1_process_alive(procs: list[tuple[int, str]]) -> bool:
    return any("factory_grid_executor.py" in cl and _stage_token(cl) == "t1" for _, cl in procs)


def gpu_exclusive_ok(procs: list[tuple[int, str]], nvidia_query_fn) -> tuple[bool, list[str]]:
    """单卡禁共存（prereg vram.concurrency=1）：executor 系在跑=硬拒；
    nvidia-smi 计算进程（python，≥1GB）=硬拒；探针自身失败只留痕不硬拦（进程探测为主网）。"""
    hard: list[str] = []
    notes: list[str] = []
    for pid, cl in procs:
        if pid == os.getpid():
            continue
        if any(s in cl for s in GPU_BUSY_EXECUTOR_SUBSTRINGS):
            hard.append(f"gpu_job_process pid={pid} cmd={cl[:160]}")
    try:
        for pid, name, mem_mib in nvidia_query_fn():
            if pid == os.getpid():
                continue
            if "python" in str(name).lower() and float(mem_mib) >= 1024:
                hard.append(f"nvidia_compute pid={pid} name={name} mem_mib={mem_mib}")
    except Exception as exc:  # noqa: BLE001
        notes.append(f"nvidia_probe_failed:{type(exc).__name__}:{exc}")
    return (not hard), (hard + notes)


def nvidia_compute_apps() -> list[tuple[int, str, float]]:
    res = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    rows = []
    for line in res.stdout.splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) >= 3:
            try:
                rows.append((int(parts[0]), parts[1], float(parts[2])))
            except ValueError:
                continue
    return rows


# --------------------------------------------------------------------------- run 定位与产物
def find_t1_run(intake_dir: Path, tier1_points: int, override: str | None) -> Path | None:
    """定位被守望 run 目录，序=①显式 --t1-run ②带 claim 认领的目录（发过 T2 的 T1 目录恒优先，
    这使 T2 跑中新建的 grid_* 空目录不会骗走守望器）③manifest 行数恰=tier1_points 的目录
    ④最新无 manifest 目录（跑中/死掉）⑤最新目录（死T1留半截 manifest→交验收判红）。"""
    if override:
        d = intake_dir / override
        if not d.is_dir():
            raise RuntimeError(f"--t1-run 指定目录不存在: {d}")
        return d
    cands = sorted([p for p in intake_dir.glob("grid_*") if p.is_dir()], key=lambda p: p.name, reverse=True)
    if not cands:
        return None
    for d in cands:
        if (d / "t2_handover_claim.yaml").exists():
            return d
    for d in cands:
        mf = d / "manifest.csv"
        if mf.exists() and _csv_row_count(mf) == tier1_points:
            return d
    for d in cands:
        if not (d / "manifest.csv").exists():
            return d
    return cands[0]


def _csv_row_count(p: Path) -> int:
    try:
        df = pd.read_csv(p)
        return int(len(df))
    except pd.errors.EmptyDataError:
        return 0


def _grid_log_tail(repo_root: Path, n_lines: int = 15) -> dict:
    """T1_DIED 时附最新 grid_t1 日志尾部指针（只读，不重启不处置）。"""
    logs = sorted((repo_root / ".runtime" / "logs").glob("grid_t1*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        return {"path": None, "tail": ""}
    p = logs[0]
    tail = "".join(p.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)[-n_lines:])
    return {"path": str(p), "tail": tail}


# --------------------------------------------------------------------------- 验收判据（17 号文 §一）
def _manifest_frame(run_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(run_dir / "manifest.csv")
    if "values_json" not in df.columns:
        raise RuntimeError("manifest 缺 values_json——非本引擎出生证，禁盲验收")
    return df


def _values(df: pd.DataFrame) -> pd.DataFrame:
    return df["values_json"].apply(json.loads).apply(pd.Series)


def _spot_sample(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    import numpy as np

    k = min(len(df), n)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(df), size=k, replace=False)
    return df.iloc[sorted(int(i) for i in idx)]


def _check_cost_rows(rows: dict[float, float], tiers: list[float], floor: float, tol: float) -> tuple[bool, str]:
    got = sorted(float(k) for k in rows)
    if got != sorted(float(t) for t in tiers):
        return False, f"档位集非全真五档: {got}"
    sharpes = [float(rows[k]) for k in got]
    for i in range(len(sharpes) - 1):
        if sharpes[i + 1] > sharpes[i] + tol:
            return False, (f"五档非单调非增: {got[i]:g}bp={sharpes[i]} -> {got[i + 1]:g}bp={sharpes[i + 1]}")
    if sharpes[-1] < floor:
        return False, f"{got[-1]:g}bp 档 sharpe={sharpes[-1]} < survival_floor({floor:g})"
    return True, "ok"


def replay_cost_tiers_via_engine(
    run_dir: Path, cells: list[tuple[str, dict]], tiers: list[float]
) -> dict[str, dict[float, float]]:
    """成本门真实性之"抽查重放"腿（17 号文 §一度量列原文）：用冻结引擎对抽中格点
    重跑五档扫描（引擎复用零重实现，与 run_batch 评估链同构）。懒加载重量依赖，
    仅 manifest 无 cost 列时触发；单测注入替身，不真跑。"""
    import importlib.util

    repo = run_dir.parents[2]
    exec_path = repo / "scripts" / "backtest" / "factory_grid_executor.py"
    spec = importlib.util.spec_from_file_location("_fge_for_replay", exec_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_fge_for_replay"] = mod  # py3.12 dataclass 解析需 sys.modules 反查（缺=AttributeError NoneType）
    sys.path.insert(0, str(repo / "scripts" / "backtest" / "translated"))
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    from zephyr.backtest.regime_validation.exam_cost_gate import run_cost_tier_scan
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    start, end = summary["window"]
    # st-ddup-20260925 去重改造②适配：_load_engine 已升级 7 元组（run_backtest_full/
    # net_returns_by_tiers 替代两连调）；本重放腿仍走逐档 daily_net_returns 口径
    # （抽查面量小，掩码缓存自动惠及，无需切注入路径）。
    load_px, wide, filter_st, load_st_flags, _rbt_full, daily_net_returns, _nets_by_tiers = mod._load_engine()
    recipes = {r.recipe_id: r for r in GridCompiler.from_yaml(mod.SCHEMA_PATH).compile(mod.DEFAULT_CONTEXT).recipes}

    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=200)).date().isoformat()
    px = load_px(warm_start, end, fields=("close", "volume"))
    closes_all = wide(px, "close")
    closes = closes_all.loc[(closes_all.index >= pd.Timestamp(start)) & (closes_all.index <= pd.Timestamp(end))]
    flags = load_st_flags(start, end)
    closes_eval = filter_st(closes_all, flags).loc[closes.index]
    vol20 = closes_eval.pct_change().rolling(20).std()
    try:
        mkt = mod._load_mkt_cap_wide(warm_start, end, closes_all.columns)
    except Exception:  # noqa: BLE001 市值宽表缺失→mkt_cap 格点复算自然 fail-closed（与正跑同语义）
        mkt = None
    rets = closes_eval.pct_change()
    r60m, r60v = rets.rolling(60).mean(), rets.rolling(60).var()
    try:
        imap = mod._industry_map()
    except Exception:  # noqa: BLE001
        imap = None

    uni_cache: dict[str, list[str]] = {}
    fac_cache: dict[str, dict[str, pd.DataFrame]] = {}
    out: dict[str, dict[float, float]] = {}
    for rid, _vals in cells:
        r = recipes.get(rid)
        if r is None:
            out[rid] = {}  # 出生证查无=证据缺失，判定面按 fail-closed 处理
            continue
        g = r.values["G_universe"]
        if g not in uni_cache:
            cols_all = mod._load_universe(g, start, end)
            uni_cache[g] = [c for c in cols_all if c in closes_eval.columns]
            fac_cache[g] = mod.compute_v1_factors(closes_eval[uni_cache[g]])
        cols = uni_cache[g]
        closes_g = closes_eval[cols]
        weights, _deg = mod.evaluate_recipe(
            r,
            closes_g,
            fac_cache[g],
            vol20[cols],
            cols,
            mkt_cap_w=mkt,
            rets60_mean=r60m,
            rets60_var=r60v,
            industry_map=imap,
        )
        out[rid] = {
            float(k): float(v)
            for k, v in run_cost_tier_scan(weights, closes_g, daily_net_returns, tiers_bp=tuple(tiers)).items()
        }
    return out


def _load_prev_verdict(run_dir: Path) -> dict:
    """上轮 verdict 读取（缓存判据用）；损坏视为无缓存必留痕重算（本件自写原子替换）。"""
    verdict_p = run_dir / "handover_verdict.yaml"
    if not verdict_p.exists():
        return {}
    try:
        return yaml.safe_load(verdict_p.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 本件自写原子替换，损坏必留痕重算
        return {}


def _put_criterion(crit: dict):
    """判据写入闭包（键序=验收判据固定呈现序，机读面稳定）。"""

    def _put(name, measured, threshold, passed, note=""):
        crit[name] = {"measured": measured, "threshold": threshold, "pass": bool(passed), "note": note}

    return _put


def _criterion_manifest_points(put, df: pd.DataFrame, tier1: int) -> None:
    put("manifest_points", len(df), f"=={tier1}±0", len(df) == tier1, "grid manifest.csv 行数（17 号文 §一 完成率行）")


def _criterion_dead_zero(put, summary: dict | None) -> None:
    if summary is None:
        put(
            "dead_zero",
            None,
            "backtest_dead=0 & eval_dead=0 & gate_dead=0",
            False,
            "summary.json 未落盘（产物期末连写，下轮重验自愈）",
        )
        return
    d_e = int(summary.get("eval_dead", -1))
    d_b = int(summary.get("backtest_dead", -1))
    d_g = int(summary.get("gate_dead", 0))
    put(
        "dead_zero",
        {"eval_dead": d_e, "backtest_dead": d_b, "gate_dead": d_g},
        "backtest_dead=0 & eval_dead=0 & gate_dead=0",
        d_e == 0 and d_b == 0 and d_g == 0,
    )


def _criterion_degraded(put, df: pd.DataFrame) -> None:
    deg_hits = int(
        df["degraded_dimensions"].astype(str).apply(lambda s: s.strip() not in ("()", "[]", "", "nan")).sum()
    )
    put("degraded_zero", deg_hits, "degraded 格点数==0", deg_hits == 0)


def _criterion_negatives_discipline(put, neg_p: Path, df: pd.DataFrame, n_sampled: int, neg_rows: int | None) -> None:
    put(
        "negatives_discipline",
        {
            "negatives_exists": neg_p.exists(),
            "neg_rows": neg_rows,
            "accounted": (len(df) + (neg_rows or 0)),
            "n_sampled": n_sampled,
        },
        "negatives.csv 存在 且 manifest+negatives 恰=送评格数"
        "（主效应前 20% 层外负结果入册的完备性前置，17 号文 §一 负结果纪律行）",
        bool(neg_p.exists()) and neg_rows is not None and len(df) + neg_rows == n_sampled,
    )


def _criterion_n_eff(put, summary: dict | None) -> None:
    n_eff = None if summary is None else summary.get("n_trials_effective")
    put(
        "n_eff",
        n_eff,
        f">={N_EFF_FLOOR:g}",
        n_eff is not None and float(n_eff) >= N_EFF_FLOOR,
        "summary.json n_trials_effective（T0 实测口径，17 号文 §一 有效样本行）",
    )


def _criterion_dsr(put) -> None:
    put(
        "dsr",
        None,
        "e7_defense 浮动门槛（n_trial_ledger 累计口径）",
        True,
        "deferred：17 号文 §一 DSR 行的度量=自动管线（成绩单件消费），"
        "非 T2 发车前置；此处 pass=True 仅指'不阻塞发车'，非'DSR 已完成'声明（诚实位）",
    )


def _cost_rows_from_manifest_column(sample: pd.DataFrame) -> dict[str, dict[float, float]]:
    """证据径①：manifest 自带 cost_tier_sharpes_json 列（零重放）。"""
    rows_out: dict[str, dict[float, float]] = {}
    for _, row in sample.iterrows():
        try:
            raw = json.loads(row["cost_tier_sharpes_json"])
            rows_out[str(row["recipe_id"])] = {float(k): float(v) for k, v in raw.items()}
        except Exception:  # noqa: BLE001 单元格 cost 证据损坏→缺席，判定面 fail-closed
            rows_out[str(row["recipe_id"])] = {}
    return rows_out


def _cost_rows_from_prev_cache(
    prev: dict, fingerprint: str, n_rows: int, force_replay: bool
) -> dict[str, dict[float, float]] | None:
    """证据径②：上轮 verdict 重放缓存（manifest sha256+行数双键命中且未强制重放才复用）。"""
    cached = prev.get("cost_replay") if isinstance(prev.get("cost_replay"), dict) else None
    if cached and not force_replay and cached.get("manifest_sha256") == fingerprint and cached.get("n_rows") == n_rows:
        return {
            str(k): {float(b): float(v) for b, v in (d or {}).items()} for k, d in (cached.get("rows") or {}).items()
        }
    return None


def _cost_rows_via_replay(
    run_dir: Path, sample: pd.DataFrame, tiers: list[float], replay_fn
) -> dict[str, dict[float, float]]:
    """证据径③：冻结引擎真重放（fail-closed 面：注入替身缺失=异常上抛交 ACCEPTANCE_ERROR）。"""
    sample_vals = _values(sample)
    cells = [
        (str(rid), sample_vals.loc[i].to_dict()) for i, rid in zip(sample_vals.index, sample["recipe_id"], strict=True)
    ]
    replayed = replay_fn(run_dir, cells, tiers) or {}
    out: dict[str, dict[float, float]] = {}
    for rid, rows in replayed.items():
        out[str(rid)] = {float(b): float(v) for b, v in (rows or {}).items()}
    return out


def _criterion_cost_gate_spot(
    put, run_dir: Path, df: pd.DataFrame, cg: dict, prev: dict, replay_fn, force_replay: bool
) -> tuple[str, dict[str, dict[float, float]]]:
    """成本门真实性判据（抽查≥50 格五档全真跑，三径择一）；返回 (证据来源, cache_rows)。"""
    tiers, floor, tol = cg["tiers"], cg["survival_floor"], cg["monotonic_tol"]
    if len(df) < SPOT_CHECK_N:
        put(
            "cost_gate_spot",
            {"manifest_rows": len(df)},
            f"抽查≥{SPOT_CHECK_N} 格五档全真跑",
            False,
            "格点不足抽样下界（fail-closed，证据不足非跳过）",
        )
        return "n/a", {}
    sample = _spot_sample(df, SPOT_CHECK_N, SPOT_CHECK_SEED)
    if "cost_tier_sharpes_json" in df.columns:
        src = "manifest_cost_column"
        cache_rows = _cost_rows_from_manifest_column(sample)
    else:
        fingerprint = _sha256_file(run_dir / "manifest.csv")
        cache_rows = _cost_rows_from_prev_cache(prev, fingerprint, len(df), force_replay)
        if cache_rows is None:
            src = "replay"
            cache_rows = _cost_rows_via_replay(run_dir, sample, tiers, replay_fn)
        else:
            src = "replay_cache"
    bad: list[str] = []
    ok_n = 0
    for rid in sample["recipe_id"].astype(str):
        rows = cache_rows.get(rid)
        if not rows:
            bad.append(f"{rid}:missing")
            continue
        ok, why = _check_cost_rows(rows, tiers, floor, tol)
        ok_n += int(ok)
        if not ok:
            bad.append(f"{rid}:{why}")
    put(
        "cost_gate_spot",
        {"source": src, "sampled": int(len(sample)), "ok": ok_n, "bad_head": bad[:10]},
        f"抽查≥{SPOT_CHECK_N} 格五档全真跑；最高档({max(tiers):g}bp) sharpe>="
        f"survival_floor({floor:g})；逐档非增（容差 {tol:g}）",
        ok_n >= SPOT_CHECK_N and not bad,
        f"bad={len(bad)}",
    )
    return src, cache_rows


def _condition_axis_zero(run_dir: Path) -> object:
    """条件轴零样本垃圾线实测（归因件缺/坏=只报不崩）。"""
    cond_p = run_dir / "condition_attribution.csv"
    cond_zero: object = "not_evaluable(归因件未生成，巡检脚本补位)"
    if cond_p.exists():
        try:
            cadf = pd.read_csv(cond_p)
            per = cadf.groupby("cell_id")["days"].sum()
            cond_zero = "clean" if len(per) and bool((per > 0).all()) else f"zero_cells:{list(per[per <= 0].index)[:5]}"
        except Exception as exc:  # noqa: BLE001
            cond_zero = f"unreadable:{type(exc).__name__}"
    return cond_zero


def _garbage_measurements(
    run_dir: Path, df: pd.DataFrame, summary: dict | None, neg_rows: int | None, n_sampled: int
) -> tuple[float, float, float, object, bool]:
    """垃圾触发线实测：完成率/死亡率/可疑 sharpe 占比/条件轴零样本 + 死率命中位。"""
    done_frac = (len(df) + (neg_rows or 0)) / n_sampled if n_sampled else 0.0
    dead_frac = 0.0
    death_hit = False
    if summary is not None:
        dead_frac = (
            int(summary.get("eval_dead", 0)) + int(summary.get("backtest_dead", 0)) + int(summary.get("gate_dead", 0))
        ) / (n_sampled or 1)
        death_hit = dead_frac > GARBLE_DEATH_GT
    sh = pd.to_numeric(df.get("sharpe"), errors="coerce").dropna()
    s_gt2 = float((sh > GARBLE_SHARPE_GT).mean()) if len(sh) else 1.0
    return done_frac, dead_frac, s_gt2, _condition_axis_zero(run_dir), death_hit


def _garbage_lines(
    pre_hash: str, hash_hit: bool, done_frac: float, dead_frac: float, death_hit: bool, s_gt2: float, cond_zero: object
) -> dict:
    """垃圾触发线五条（任一命中即报=同时阻断发车；口径=17 号文 §一垃圾线）。"""
    return {
        "completion_rate": {
            "measured": round(done_frac, 6),
            "threshold": f">={GARBLE_COMPLETION_LT}",
            "hit": done_frac < GARBLE_COMPLETION_LT,
        },
        "death_rate": {
            "measured": round(dead_frac, 6),
            "threshold": f"<={GARBLE_DEATH_GT}",
            "hit": death_hit,
        },
        "suspicious_sharpe_share": {
            "measured": round(s_gt2, 6),
            "threshold": f"sharpe>{GARBLE_SHARPE_GT:g} 占比<={GARBLE_SHARPE_SHARE_GT}",
            "hit": s_gt2 > GARBLE_SHARPE_SHARE_GT,
        },
        "condition_axis_zero_sample": {
            "measured": cond_zero,
            "threshold": "条件轴任一胞零样本即报",
            "hit": isinstance(cond_zero, str) and cond_zero.startswith("zero_cells"),
        },
        "prereg_hash_drift": {
            "measured": pre_hash,
            "threshold": "与上轮记录一致",
            "hit": hash_hit,
            "note": "首轮=建基线（prev 无哈希不判）；跑中改 prereg=作废重开（冻结语义）",
        },
    }


def run_acceptance(
    run_dir: Path,
    caps: dict,
    cg: dict,
    prereg_path: Path,
    *,
    replay_fn=replay_cost_tiers_via_engine,
    force_replay: bool = False,
) -> dict:
    """逐条 §一判据 → 机读 verdict（并原子落盘 handover_verdict.yaml）。
    含垃圾触发线与 prereg hash 记录。all_green=硬判据全过且垃圾线零命中。"""
    tier1 = caps["tier1_points"]
    mf = run_dir / "manifest.csv"
    summary_p = run_dir / "summary.json"
    summary = json.loads(summary_p.read_text(encoding="utf-8")) if summary_p.exists() else None
    df = _manifest_frame(run_dir)
    prev = _load_prev_verdict(run_dir)

    ranking_metric = "cost_adjusted_sharpe" if "cost_adjusted_sharpe" in df.columns else "sharpe"
    n_sampled = int(summary["n_sampled"]) if summary and "n_sampled" in summary else tier1
    neg_p = run_dir / "negatives.csv"
    neg_rows = _csv_row_count(neg_p) if neg_p.exists() else None

    crit: dict[str, dict] = {}
    put = _put_criterion(crit)
    _criterion_manifest_points(put, df, tier1)
    _criterion_dead_zero(put, summary)
    _criterion_degraded(put, df)
    _criterion_negatives_discipline(put, neg_p, df, n_sampled, neg_rows)
    _criterion_n_eff(put, summary)
    src, cache_rows = _criterion_cost_gate_spot(put, run_dir, df, cg, prev, replay_fn, force_replay)
    _criterion_dsr(put)

    # 垃圾触发线（任一命中即报=同时阻断发车）
    pre_hash = _sha256_file(prereg_path)
    hash_hit = bool(prev.get("prereg_sha256")) and prev.get("prereg_sha256") != pre_hash
    done_frac, dead_frac, s_gt2, cond_zero, death_hit = _garbage_measurements(run_dir, df, summary, neg_rows, n_sampled)
    garbage = _garbage_lines(pre_hash, hash_hit, done_frac, dead_frac, death_hit, s_gt2, cond_zero)

    blocking = [k for k, v in crit.items() if not v["pass"]]
    garbage_hits = [k for k, v in garbage.items() if v.get("hit")]
    verdict = {
        "schema": "t1_t2_handover/verdict-1",
        "run": run_dir.name,
        "generated_at": datetime.now(_TZ).isoformat(timespec="seconds"),
        "manifest_sha256": _sha256_file(mf),
        "prereg_sha256": pre_hash,
        "ranking_metric": ranking_metric,
        "criteria": crit,
        "garbage_lines": garbage,
        "blocking_criteria": blocking,
        "garbage_hits": garbage_hits,
        "all_green": not blocking and not garbage_hits,
    }
    if src == "replay" and cache_rows:
        verdict["cost_replay"] = {
            "manifest_sha256": _sha256_file(mf),
            "n_rows": len(df),
            "rows": {k: {str(b): v for b, v in d.items()} for k, d in cache_rows.items()},
        }
    _atomic_write_text(run_dir / "handover_verdict.yaml", yaml.safe_dump(verdict, allow_unicode=True, sort_keys=False))
    return verdict


# --------------------------------------------------------------------------- T2 选层（确定性）
def _canon(v) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True)


def _dim_scores(vals_df: pd.DataFrame, score: pd.Series) -> dict[str, dict[str, float]]:
    """每维每层（dim, canonical(value)）= 该层格点主目标均值。"""
    out: dict[str, dict[str, float]] = {}
    sv = score.to_numpy(dtype=float)
    for dim in vals_df.columns:
        agg: dict[str, list[float]] = {}
        for col_vals, s in zip(vals_df[dim].tolist(), sv, strict=True):
            if s is None or (isinstance(s, float) and math.isnan(s)):
                continue
            agg.setdefault(_canon(col_vals), []).append(float(s))
        out[dim] = {k: sum(vs) / len(vs) for k, vs in agg.items()}
    return out


def _default_anova(vals_df: pd.DataFrame, score: pd.Series, dims: list[str]):
    """主效应/可砍维判定复用 MOD-BT-197（ANOVA 阈值冻结值，禁在本件重发明）。"""
    import importlib.util

    repo = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "_fga_for_select", repo / "scripts" / "backtest" / "factory_grid_anova.py"
    )
    anova = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(anova)  # type: ignore[union-attr]
    frame = vals_df.copy().reset_index(drop=True)
    frame["sharpe"] = score.to_numpy(dtype=float)
    frame = frame.dropna(subset=["sharpe"])
    imp_tbl = anova.importance_table(frame, dims)
    top_main = imp_tbl.head(6)["dimension"].tolist()
    inter_tbl = anova.interaction_table(frame, dims, top_main)
    importance = {str(r["dimension"]): float(r["main_effect_ratio"]) for r in imp_tbl.to_dict("records")}
    prunable = {str(r["dimension"]) for r in anova.prunable_dims(imp_tbl, inter_tbl)}
    return importance, prunable


def _strong_dims(dims: list[str], prunable: set[str], importance: dict) -> list[str]:
    """强维=非可砍维；全可砍病态时强制重要性第 1 维入主效应维（S3 兜底）。"""
    strong = [d for d in dims if d not in prunable]
    if not strong:
        strong = [max(importance, key=importance.get)] if importance else [sorted(dims)[0]]
    return strong


def _select_levels(dims: list[str], strong: list[str], dsc: dict) -> dict[str, list[str]]:
    """S3 选层：主效应维取层主目标均值前 20%（ceil，至少 1 层）；弱维=参数展开全层保留。"""
    levels: dict[str, list[str]] = {}  # dim -> 有序 canonical json 键列表
    for d in sorted(dims):
        ordered = sorted(dsc[d], key=lambda k: (-dsc[d][k], k))  # 分降序，平局 json 键升序
        if d in strong:
            k = max(1, math.ceil(TOP_SHARE * len(ordered)))
            levels[d] = ordered[:k]
        else:  # 弱维=参数展开：全层保留，按 json 键升序（确定性）
            levels[d] = sorted(ordered)
    return levels


def _as_values(mapping: dict[str, list[str]]) -> dict[str, list]:
    return {d: [json.loads(x) for x in vs] for d, vs in mapping.items()}


def _default_count(sub: dict[str, list]) -> int:
    n = 1
    for vs in sub.values():
        n *= max(len(vs), 1)
    return n


def _prune_levels(levels: dict[str, list[str]], dims: list[str], dsc: dict, cap: int, count_fn) -> list[str]:
    """S4 穷尽点数超帽剪层：按全局最低层分逐层剔除（平局=维名、层 json 键升序）直至 ≤cap。"""
    cf = count_fn or _default_count
    pruned: list[str] = []
    guard = 0
    while cf(_as_values(levels)) > cap:
        guard += 1
        if guard > 100000:  # 防御性保险丝（数学上单例仍超帽时靠下方 cands 空判抛出）
            raise RuntimeError("subspace 剪枝迭代异常，交总筹重排配比")
        cands = [(dsc[d].get(key, float("-inf")), d, key) for d in dims for key in levels[d][1:]]
        if not cands:
            raise RuntimeError(f"subspace 穷尽点数恒>{cap}（每维仅剩 1 层），交总筹重排配比")
        cands.sort(key=lambda t: (t[0], t[1], t[2]))
        _, worst_d, worst_key = cands[0]
        levels[worst_d] = [x for x in levels[worst_d] if x != worst_key]
        pruned.append(f"{worst_d}={worst_key}")
    return pruned


def build_t2_subspace(run_dir: Path, caps: dict, *, count_fn=None, importance_fn=None) -> dict:
    """选层规则（案卷 §四钉死、可复算）：
    S1 候选维 = T1 manifest values_json 中取值数>1 的维（常量维不入 subspace，由 schema 折叠）；
    S2 主效应占比/可砍维判定 = factory_grid_anova（MOD-BT-197 冻结阈 PRUNE_THRESHOLD）；
       弱维（prunable）=参数展开维：保留该维全部观测层；
    S3 主效应维各取其层主目标均值前 20%（ceil，至少 1 层；全维可砍病态时强制重要性第 1 维入
       主效应维）——即 prereg "主效应前 20% 层"注；
    S4 subspace=逐维值集（执行器 --subspace-json 的笛卡尔过滤语义）；穷尽点数（count_fn，
       缺省=积算近似上界；生产注入 GridCompiler 真匹配数）超 tier2_points 时按全局最低层分
       逐层剔除（平局=维名、层 json 键升序）直至 ≤cap。
    同 manifest 必得同 JSON（无随机源）。落盘 t2_subspace.json（引擎既有 .json 消费面，
    真源=executor main 的 _json.loads）+ t2_subspace_meta.yaml（机读元数据用 .yaml）。
    """
    df = _manifest_frame(run_dir)
    vals = _values(df)
    score_col = "cost_adjusted_sharpe" if "cost_adjusted_sharpe" in df.columns else "sharpe"
    score = pd.to_numeric(df[score_col], errors="coerce")

    dims = [d for d in vals.columns if vals[d].nunique(dropna=False) > 1]
    if not dims:
        raise RuntimeError("manifest 无任何多值维——无从选层")

    if importance_fn is None:
        importance, prunable = _default_anova(vals, score, dims)
    else:
        importance, prunable = importance_fn(vals, score, dims)

    strong = _strong_dims(dims, prunable, importance)
    dsc = _dim_scores(vals[dims], score)
    levels = _select_levels(dims, strong, dsc)

    cap = int(caps["tier2_points"])
    pruned = _prune_levels(levels, dims, dsc, cap, count_fn)

    subspace = _as_values(levels)
    payload = {d: subspace[d] for d in sorted(subspace)}
    expected = int((count_fn or _default_count)(payload))
    _atomic_write_text(
        run_dir / "t2_subspace.json", json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    meta = {
        "generated_by": "scripts/backtest/t1_t2_handover.py",
        "rule": "S1-S4 确定性选层（案卷 AUTO_t1_t2_handover.md §四，可复算）",
        "ranking_metric": score_col,
        "strong_dims": sorted(strong),
        "weak_dims_expanded": sorted(d for d in dims if d not in strong),
        "top_share": TOP_SHARE,
        "pruned_levels": pruned,
        "expected_points": expected,
        "cap": cap,
        "manifest_sha256": _sha256_file(run_dir / "manifest.csv"),
        "executor_clamp": f"引擎 --n-samples 缺省 20000 → _apply_prereg_budget 钳至 "
        f"tier2_points={cap}（seed 默认 20260915，抽样确定性）",
    }
    _atomic_write_text(run_dir / "t2_subspace_meta.yaml", yaml.safe_dump(meta, allow_unicode=True, sort_keys=False))
    return {"subspace": payload, "expected_points": expected, "meta": meta}


# --------------------------------------------------------------------------- claim / 发车
def claim_path(run_dir: Path) -> Path:
    return run_dir / "t2_handover_claim.yaml"


def _load_claim(run_dir: Path) -> dict:
    p = claim_path(run_dir)
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001
        return {"_corrupt": True}


def acquire_claim(run_dir: Path, session_note: str) -> bool:
    """O_CREAT|O_EXCL 原子创建（存在即 False）——重复守望器双发 T2 的头号护栏。"""
    body = yaml.safe_dump(
        {
            "schema": "t1_t2_handover/claim-1",
            "pid": os.getpid(),
            "created_at": datetime.now(_TZ).isoformat(timespec="seconds"),
            "launched": False,
            "note": session_note,
        },
        allow_unicode=True,
        sort_keys=False,
    )
    p = claim_path(run_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    try:
        os.write(fd, body.encode("utf-8"))
    finally:
        os.close(fd)
    return True


def _claim_age_hours(p: Path) -> float:
    return (time.time() - p.stat().st_mtime) / 3600.0


def mark_claim_launched(run_dir: Path, pid: int, log_path: Path) -> None:
    c = _load_claim(run_dir)
    c.update(
        {
            "launched": True,
            "t2_pid": pid,
            "t2_log": str(log_path),
            "launched_at": datetime.now(_TZ).isoformat(timespec="seconds"),
        }
    )
    _atomic_write_text(claim_path(run_dir), yaml.safe_dump(c, allow_unicode=True, sort_keys=False))


def ensure_reaper_keep(keep_path: Path, substring: str) -> bool:
    """cmdline 子串登记（防误杀；幂等，已在册返回 False=未改动）。"""
    if not keep_path.exists():
        keep_path.parent.mkdir(parents=True, exist_ok=True)
        keep_path.write_text(substring + "\n", encoding="utf-8")
        return True
    text = keep_path.read_text(encoding="utf-8", errors="replace")
    if any(line.strip() == substring for line in text.splitlines()):
        return False
    with open(keep_path, "a", encoding="utf-8") as f:
        f.write(("\n" if text and not text.endswith("\n") else "") + substring + "\n")
    return True


def default_launcher(cmd: list[str], cwd: Path, log_path: Path) -> subprocess.Popen:
    """子进程无窗口 + 脱管（日志进 .runtime/logs/）。"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(log_path, "a", encoding="utf-8")
    flags = 0
    if os.name == "nt":
        flags = (
            getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        )
    return subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=fh,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=flags,
        close_fds=True,
    )


def e0_gate_allowed(repo_root: Path) -> tuple[bool, str]:
    """E0 问闸（正式跑批禁跳；拒=DEFERRED 下轮重试）。导入失败按拒绝处理（fail-closed）。"""
    try:
        sys.path.insert(0, str(repo_root / "scripts" / "backtest"))
        from compute_window_gate import check_gate  # 懒加载（依赖 zephyr 包面）

        dec = check_gate("f06_grid_batch", "local_gpu", datetime.now(_TZ))
        return bool(dec.get("allowed")), str(dec.get("reason_code", ""))
    except Exception as exc:  # noqa: BLE001
        return False, f"e0_import_or_query_failed:{type(exc).__name__}"


# --------------------------------------------------------------------------- 主状态机
@dataclass
class HandoverDeps:
    """run_handover 依赖/选项束（原 13 参签名 dataclass 化；字段缺省=生产缺省）。

    proc_scan/gpu_probe/replay_fn/count_fn/importance_fn/launcher/e0_gate 全可注入
    （单测不碰生产面/不真发车）。
    """

    t1_run: str | None = None
    allow_launch: bool = True
    release_claim: bool = False
    force_replay: bool = False
    proc_scan: Any = scan_processes_default
    gpu_probe: Any = nvidia_compute_apps
    replay_fn: Any = replay_cost_tiers_via_engine
    count_fn: Any = None
    importance_fn: Any = None
    launcher: Any = default_launcher
    e0_gate: Any = e0_gate_allowed
    observe_seconds: float = LAUNCH_OBSERVE_SECONDS


def _claim_phase(run_dir: Path, release_claim: bool) -> tuple[str, int] | None:
    """claim 在场状态机（防双发 T2 的头号护栏）；None=无 claim，继续主流程。"""
    claim = _load_claim(run_dir)
    if not claim:
        if release_claim:
            return "NO_CLAIM", 0
        return None
    if release_claim:
        claim_path(run_dir).unlink(missing_ok=True)
        return "CLAIM_RELEASED", 0
    if claim.get("_corrupt"):
        return "STALE_CLAIM", 1  # 认领文件损坏=不可判定归属，交人（禁自动删）
    if claim.get("launched"):
        return "ALREADY_CLAIMED", 0  # T2 已发车（在跑或完赛）——守望器使命完成
    if _claim_age_hours(claim_path(run_dir)) > CLAIM_STALE_HOURS:
        return "STALE_CLAIM", 1  # 认领超时未落地=半路死亡，禁自动删，交人
    return "ALREADY_CLAIMED", 0


def _wait_phase(repo_root: Path, run_dir: Path, proc_scan) -> tuple[str, int] | None:
    """T1 产物不全时的等待/死亡判定；None=产物齐，进入验收。"""
    manifest = run_dir / "manifest.csv"
    if not manifest.exists():
        try:
            procs = proc_scan()
        except RuntimeError as exc:
            return f"PROC_SCAN_UNAVAILABLE:{exc}", 1
        if t1_process_alive(procs):
            return "WAITING", 0
        tail = _grid_log_tail(repo_root)
        print(f"[T1_DIED] run={run_dir.name} log_tail_pointer={tail['path']}\n{tail['tail']}")
        return "T1_DIED", 1
    if not (run_dir / "summary.json").exists():
        try:
            summary_alive = t1_process_alive(proc_scan())
        except RuntimeError:
            summary_alive = False
        if summary_alive:
            return "WAITING", 0  # 期末连写窗口（manifest 先、summary 后数毫秒），下轮自愈
    return None


def _accept_and_build(
    run_dir: Path, caps: dict, cg: dict, prereg_path: Path, deps: HandoverDeps
) -> tuple[str, int] | dict:
    """验收→红则止；绿则确定性构造 T2 子空间。返回 dict(built) 或 (STATUS, code)。"""
    try:
        verdict = run_acceptance(
            run_dir, caps, cg, prereg_path, replay_fn=deps.replay_fn, force_replay=deps.force_replay
        )
    except RuntimeError as exc:
        return f"ACCEPTANCE_ERROR:{exc}", 1
    if not verdict["all_green"]:
        print(
            f"[VERDICT_RED] blocking={verdict['blocking_criteria']} "
            f"garbage={verdict['garbage_hits']} verdict={run_dir / 'handover_verdict.yaml'}"
        )
        return "VERDICT_RED", 1
    try:
        built = build_t2_subspace(run_dir, caps, count_fn=deps.count_fn, importance_fn=deps.importance_fn)
    except RuntimeError as exc:
        return f"SUBSPACE_INFEASIBLE:{exc}", 1
    print(
        f"[SUBSPACE] expected_points={built['expected_points']} "
        f"cap={caps['tier2_points']} file={run_dir / 't2_subspace.json'}"
    )
    return built


def _launch_sequence(run_dir: Path, repo_root: Path, caps: dict, deps: HandoverDeps) -> tuple[str, int]:
    """发车序列：claim 先手（防双发）→ GPU 独占 → E0 问闸 → keep 登记 → 无窗 Popen → 短窗观察。"""
    if not acquire_claim(run_dir, session_note="lanes=LANE-AUTO watchdog tick"):
        return "ALREADY_CLAIMED", 0  # 检查与创建之间另一守望抢先（原子认领竞态的正解）
    try:
        try:
            procs = deps.proc_scan()
        except RuntimeError as exc:
            return _defer_and_release(run_dir, f"PROC_SCAN_UNAVAILABLE:{exc}")
        ok, why = gpu_exclusive_ok(procs, deps.gpu_probe)
        if not ok:
            return _defer_and_release(run_dir, f"gpu_exclusive: {'; '.join(why)}")
        try:  # E0 问闸：注入面统一 contract=callable(repo_root)->(bool, str) | bool
            out = deps.e0_gate(repo_root)
            if isinstance(out, tuple):
                allowed, reason = bool(out[0]), str(out[1])
            else:
                allowed, reason = bool(out), "injected"
        except Exception as exc:  # noqa: BLE001 fail-closed=拒
            allowed, reason = False, f"e0_raised:{type(exc).__name__}"
        if not allowed:
            return _defer_and_release(run_dir, f"E0_gate({reason})")
        keep_changed = ensure_reaper_keep(
            repo_root / "data" / "runtime" / "process_reaper_keep.txt", REAPER_KEEP_SUBSTRING
        )
        if keep_changed:
            print(f"[KEEP] 已登记 process_reaper_keep.txt: {REAPER_KEEP_SUBSTRING}")
        start, end = caps["search_window"]
        log_path = repo_root / ".runtime" / "logs" / f"grid_t2_handover_{time.strftime('%Y%m%d-%H%M%S')}.log"
        # 执行器消费面 = main 里 _json.loads(args.subspace_json)（内联 JSON，非文件路径）——
        # 2026-09-29 SW4 实障修复：旧版传路径串必 JSONDecodeError 秒崩（LAUNCH_FAILED 循环）。
        subspace_inline = (run_dir / "t2_subspace.json").read_text(encoding="utf-8")
        cmd = [
            sys.executable,
            str(repo_root / "scripts" / "backtest" / "factory_grid_executor.py"),
            "--stage",
            "t2",
            "--subspace-json",
            subspace_inline,
            "--start",
            start,
            "--end",
            end,
        ]
        proc = deps.launcher(cmd, repo_root, log_path)
        deadline = time.time() + deps.observe_seconds
        while time.time() < deadline:
            rc = proc.poll()
            if rc is not None:
                claim_path(run_dir).unlink(missing_ok=True)  # 秒败→撤认领，下轮自愈重试
                tail = ""
                if log_path.exists():
                    tail = log_path.read_text(encoding="utf-8", errors="replace")[-800:]
                print(f"[LAUNCH_FAILED] rc={rc} log={log_path}\n{tail}")
                return "LAUNCH_FAILED", 1
            time.sleep(min(2.0, max(0.2, deps.observe_seconds / 10.0)))
        mark_claim_launched(run_dir, int(getattr(proc, "pid", -1)), log_path)
        return "LAUNCHED", 0
    except Exception as exc:  # noqa: BLE001 发车异常必撤本次认领，防僵尸 claim
        return _defer_and_release(run_dir, f"LAUNCH_ERROR:{type(exc).__name__}:{exc}", status="LAUNCH_FAILED")


def run_handover_core(repo_root: Path, deps: HandoverDeps) -> tuple[str, int]:
    """一次幂等巡检（新调用面：构造 HandoverDeps 后入此）。返回 (STATUS, exit_code)。"""
    repo_root = Path(repo_root)
    intake = repo_root / "data" / "strategy_intake"
    prereg_path = repo_root / "config" / "search_space_prereg.yaml"
    caps = load_prereg_caps(prereg_path)
    cg = load_cost_gate_params(repo_root / "config" / "exam_scale_cost_gate.yaml")

    try:
        run_dir = find_t1_run(intake, caps["tier1_points"], deps.t1_run) if intake.exists() else None
    except RuntimeError as exc:
        return f"NO_RUN_DIR:{exc}", 1
    if run_dir is None:
        return "NO_RUN_DIR", 1

    claim = _claim_phase(run_dir, deps.release_claim)
    if claim is not None:
        return claim

    wait = _wait_phase(repo_root, run_dir, deps.proc_scan)
    if wait is not None:
        return wait

    outcome = _accept_and_build(run_dir, caps, cg, prereg_path, deps)
    if not isinstance(outcome, dict):
        return outcome
    if not deps.allow_launch:
        return "GREEN_DRYRUN", 0
    return _launch_sequence(run_dir, repo_root, caps, deps)


def run_handover(repo_root, **legacy: Any) -> tuple[str, int]:
    """DEPRECATED 薄包装：保留原 13 参关键字签名（逐参语义不变），内部转 HandoverDeps。

    新调用面请直接 ``run_handover_core(repo_root, HandoverDeps(...))``；
    本包装仅为既有调用方/单测的兼容面，行为与旧签名逐一等价。
    """
    return run_handover_core(Path(repo_root), HandoverDeps(**legacy))


def _defer_and_release(run_dir: Path, why: str, status: str = "DEFERRED") -> tuple[str, int]:
    c = _load_claim(run_dir)
    if c.get("pid") == os.getpid() and not c.get("launched"):
        claim_path(run_dir).unlink(missing_ok=True)
    code = 0 if status == "DEFERRED" else 1
    return f"{status}:{why}", code


def main() -> int:
    ap = argparse.ArgumentParser(description="T1→T2 守望交接（幂等一遍查）")
    ap.add_argument("--repo-root", default=str(_REPO_DEFAULT))
    ap.add_argument("--t1-run", default=None, help="显式 run 目录名（缺省自动定位最新 t1 run）")
    ap.add_argument("--dry-run", action="store_true", help="只验收+落 subspace，不发车不认领")
    ap.add_argument("--release-claim", action="store_true", help="人工撤销认领（唯一删 claim 通道）")
    ap.add_argument("--force-replay", action="store_true", help="忽略重放缓存强制五档重放")
    args = ap.parse_args()
    status, code = run_handover_core(
        Path(args.repo_root),
        HandoverDeps(
            t1_run=args.t1_run,
            allow_launch=not args.dry_run,
            release_claim=args.release_claim,
            force_replay=args.force_replay,
        ),
    )
    print(f"STATUS={status}")
    return code


# noqa: m11-perm-manual-legitimate  有界巡检交接件（周期触发由外部薄壳调度，本体 pull-once 即退）
if __name__ == "__main__":
    raise SystemExit(main())
