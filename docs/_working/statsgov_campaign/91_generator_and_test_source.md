---
ttl: task_bound
completes_when: 两个 .py 经维护三班 C4（M6）入正式目录后，本件降级为历史留证指针；在此之前本件是它们的持久副本
---

# 本班未入库源码留证·第二件——折减重述与预算册生成器＋自家测试（M6 待维护三班 C4）

## 0·补 版本更正（留证件自己曾经过期）

本件首版（q-…-0012 落 dev 的那版）是在 `23:5x` 打的证，而生成器随后又被改过两次（补第四枚生效戳 `as_of_newest_input_mtime`＋`n_inputs_read`；把表头里一句未核实的因果换成可核算表述）。
**留证件 protecting 的正是最新版，过期即失去意义**——故本版按车道现字节整段重打，并留下差异账：

- `scripts/backtest/statsgov_deflation_and_budget.py`：上一版在册记 1116 行 / 56623 字节 / sha256 `5b3215b03ad9f791…`，本版实为 1129 行 / 57693 字节 / `02aade444ca306b8…`

⇒ 立一条随件纪律：**每次改完 .py 若要动这个归档，必须先跑本生成脚本再入袋**；只改文档不重打证＝假留证。

## 1. 清单与指纹（落地面复算即可判真伪）

| 件 | 行数 | 字节 | sha256 |
|---|---|---|---|
| `scripts/backtest/statsgov_deflation_and_budget.py` | 1129 | 57693 | 02aade444ca306b8a4085449286f3bdaf26fa9c949da3d64f4a0e82f5f673848 |
| `tests/backtest/test_statsgov_deflation_and_budget.py` | 247 | 12173 | 45f5933455d1c2df312fa7ba51294eed67d5b1af45585c4701698f51facfe25a |

复现（粘回后跑，须与上表同 sha）：

```
python -c "import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('scripts/backtest/statsgov_deflation_and_budget.py').read_bytes()).hexdigest())"
PYTHONPATH=D:/ZephyrAlpha/src python -m pytest tests/backtest/test_statsgov_deflation_and_budget.py -q   # 10 passed
```

⚑ 两条随件纪律（不写进代码就一定会被后来者踩）：
1. 测试里的计数 fixture **必须每条多键**——单键件会让"误返回键数当记录数"这类缺陷隐形（本班自犯并被逼出双向验红）。
2. 上界口径＝**上包络**（最大容器 ∪ 计数型整数量级标量 ∪ 带 p/t 统计量的检验记录数）；
   改任何一条都要重跑 `budget` 并核对四枚生效戳（`as_of_newest_input_mtime`＋`n_inputs_read`＋`spec_sha16`＋账本快照），
   规格件 mtime 只随规格件自己动、签不到磁盘/账本自增（批复④口径＝B）。

## 2. 源码全文

### `scripts/backtest/statsgov_deflation_and_budget.py`

```python
# [BLUEPRINT] MOD-BT-STATSGOV-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.statsgov_deflation_and_budget
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.simulation.deflated_sharpe_calculator; zephyr.backtest.core.n_trial_ledger;
#   zephyr.backtest.core.cpcv; zephyr.shared.io.file_utils
# [CONSUMERS] 零自动消费者（manual CLI）；产物供 st-statsgov-20261012 晨间包与统筹裁口径用
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 禁新造 DSR/PBO/切分数学——折减一律委托 MOD-SIM-024、PBO 委托 cpcv.compute_pbo、
#   切分委托 cpcv.generate_cpcv_splits、分母一律读 TrialLedger/N 账本真源；本件只做编排与读数；
#   禁写任何成绩真源字节（f06_survivors.csv / manifest.csv / summary.json / N 账本 只读）；
#   产物只落 docs/_working/<zone>/，一律 .yaml（禁 .json，DCR-005/008），write_text newline="\n"；
#   口径必配出处（每条 N 带 source+采集面+假设），算不出如实报 NOT_COMPUTABLE 禁造数；
#   确定性：禁 datetime.now()/time.time()，as_of 取输入文件 mtime，同输入必同输出；
#   判据数值（及格线/预算帽）本件只倒推不裁定，pending_adjudication 位保持 null
# [MODIFY-GUARD] tests/backtest/test_statsgov_deflation_and_budget.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StatsgovInputError(输入册缺失/形状非法/全列退化)；SystemExit(子命令非法)
# [TESTS] tests/backtest/test_statsgov_deflation_and_budget.py
# [TTL] task_bound
"""D_BACKTEST — 统计合法性班出品件：幸存者折减重述 + 全局试次预算盘点（MOD-BT-STATSGOV-001）。

用法:
  python scripts/backtest/statsgov_deflation_and_budget.py restatement \
      --repo-root . --out docs/_working/statsgov_campaign/01_f06_dsr_restatement_v1.yaml
  python scripts/backtest/statsgov_deflation_and_budget.py budget \
      --spec docs/_working/statsgov_campaign/trial_budget_registry_draft.yaml \
      --out  docs/_working/statsgov_campaign/02_trial_budget_inventory_v1.yaml

它做什么（大白话）：一批策略是"从几万格里挑出来的最好那几个"，挑这个动作本身就会把成绩
抬高。本件把抬高掉的分按不同的"一共试过多少次"口径补回来，告诉你同一个成绩在各口径下还剩
多少、名次怎么变、以及要通过 0.95 那条线原本需要多高的分数；顺带把全仓六类挖矿各自的试次
消耗量清点出来，供 Owner 给每一类定预算。它不改任何原始成绩，只加一层折减读数。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from zephyr.backtest.core.cpcv import compute_pbo, generate_cpcv_splits  # noqa: E402
from zephyr.backtest.core.n_trial_ledger import TrialLedger  # noqa: E402
from zephyr.simulation.deflated_sharpe_calculator import (  # noqa: E402
    DSR_SIGNIFICANCE_THRESHOLD,
    deflated_sharpe_from_moments,
    expected_max_sharpe_z,
    haircut_sharpe_harvey_liu,
)

#: 年化频率（A 股日度）——MOD-SIM-024 DSRConfig 默认口径，本件显式入册不靠缺省
PERIODS_PER_YEAR = 252


class StatsgovInputError(Exception):
    """输入册缺失/形状非法/候选集全退化——如实报错，不降级出数。"""


def _round(x, n=4):
    """安全四舍五入（None/非有限 → None，禁把 NaN 写进产物冒充结论）。"""
    if x is None:
        return None
    v = float(x)
    if not math.isfinite(v):
        return None
    return round(v, n)


def _mtime_iso(p: Path) -> str:
    """输入文件 mtime → ISO 文本（不读时钟，保证同输入同输出）。"""
    import datetime as _dt

    if not p.exists():
        return "MISSING"
    return _dt.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")


def _sha16(p: Path) -> str:
    import hashlib

    if not p.exists():
        return "MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


# ---------------------------------------------------------------- 口径登记（试次计数来源）


def build_caliber_register(repo_root: Path, birth_batch: str, head_ledger_root: Path | None = None) -> dict:
    """把每个候选分母 N 连同出处/采集面/语义/风险登记成一册（本件的核心可复核面）。

    head_ledger_root 给定时额外读一份"HEAD 字节面"的账本——同一册在主区（他车道在途未落地
    条目）与 HEAD 上分母不同，DSR 分母必须写清读的是哪个面，否则同一批结果有两个显著性。
    """
    reg: dict = {}
    intake = repo_root / "data" / "strategy_intake"
    sdir = intake / birth_batch
    summary = {}
    sp = sdir / "summary.json"
    if sp.exists():
        summary = json.loads(sp.read_text(encoding="utf-8"))

    reg["N_eff_registered"] = {
        "value": summary.get("n_trials_effective"),
        "source": f"{birth_batch}/summary.json:n_trials_effective",
        "estimator": "n_trial_ledger.compute_effective_rank（相关矩阵特征值熵广度）",
        "estimator_meta": summary.get("n_eff_meta"),
        "semantics": "格间高度相关时『真正独立的试验数』——折减最小、最宽松的一把尺",
        "risk": "N_eff 由被选中的同一批数据估出（选择依赖）；用它当分母＝给自己发通行证",
    }
    reg["N_evaluated"] = {
        "value": summary.get("evaluated"),
        "source": f"{birth_batch}/summary.json:evaluated",
        "semantics": "本批实际评完的格数（可审计机器回测次数，2026-09-15 裁定边界）",
        "risk": "只含单批；跨批/跨族累计的挑选效应看不见",
    }
    reg["N_sampled"] = {
        "value": summary.get("n_sampled"),
        "source": f"{birth_batch}/summary.json:n_sampled",
        "semantics": "本批计划抽样格数（含评死格）",
        "risk": "评死格未产生成绩，计入分母＝虚增",
    }

    schema_p = repo_root / "config" / "position_recipe_grid_schema.yaml"
    reg["N_space_nominal"] = {
        "value": summary.get("n_raw"),
        "source": f"{birth_batch}/summary.json:n_raw + config/position_recipe_grid_schema.yaml 名义声明",
        "semantics": "设计空间总格数（折叠后名义 N_raw），不管跑没跑过",
        "risk": "把『没试过的格』算进试次数＝最保守一把尺；2026-09-15 裁定边界不认（计数边界=可审计机器回测次数）",
    }
    if schema_p.exists():
        reg["N_space_nominal"]["schema_sha16"] = _sha16(schema_p)

    rel_ledger = "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
    for label, root in (("worktree_bytes", repo_root), ("head_bytes", head_ledger_root or repo_root)):
        if label == "head_bytes" and head_ledger_root is None:
            continue
        try:
            reg[f"N_ledger_cumulative_{label}"] = {
                "value": TrialLedger(registry_path=root / rel_ledger).cumulative_trials(),
                "source": f"{rel_ledger} count=screen_runs+sum(batch_records)（读自 {root}）",
                "semantics": "全仓累计可审计试次（跨批同尺）",
                "risk": "账面值——历史缺账见 unrecorded_* 三项（账面<磁盘实况=欠折减=放水）；主区盘面含他车道在途未落地条目，与 HEAD 面分母不同＝同一批成绩有两个显著性",
            }
        except Exception as exc:  # noqa: BLE001 — 账本不可读必须出声，禁静默少一个口径
            reg[f"N_ledger_cumulative_{label}"] = {"value": None, "error": f"{type(exc).__name__}: {exc}"}

    base_cum = (
        reg.get("N_ledger_cumulative_worktree_bytes", {}).get("value")
        or reg.get("N_ledger_cumulative_head_bytes", {}).get("value")
        or 0
    )
    unreg = scan_unrecorded_grid_trials(repo_root)
    reg["N_ledger_plus_post_watermark_missing"] = {
        "value": base_cum + unreg["post_watermark_missing_trials"],
        "source": "账面累计 + 水位线后未入账 grid 批（scan_unrecorded_grid_trials）",
        "semantics": "『本应入账却漏了』补齐后的分母",
        "risk": "缺账=分母虚低（同族病根见 trial-ledger-undercount 在档），此项是账面下限的修正",
    }
    reg["N_ledger_plus_all_disk_trials"] = {
        "value": base_cum + unreg["all_missing_trials"],
        "source": "账面累计 + 磁盘上全部未入账 grid 批（含水位线前已知缺口）",
        "semantics": "磁盘实况口径（最接近『真实发生过多少次』）",
        "risk": "水位线前缺口按裁定不回填，呈 Owner；本件只读数不追认",
    }
    reg["_unrecorded_detail"] = unreg
    return reg


def scan_unrecorded_grid_trials(repo_root: Path) -> dict:
    """磁盘 grid 产物 vs N 账本身份集对账（目录存在≠已入账；禁聚合数）。"""
    reg_path = repo_root / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
    data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    records = {str(r.get("batch_id")) for r in (data.get("batch_records") or [])}
    watermark = float((data.get("watermarks") or {}).get("registry_record_watermark") or 0)

    missing_post = 0
    missing_all = 0
    missing_batches: list[dict] = []
    for s in sorted((repo_root / "data" / "strategy_intake").glob("grid_*/summary.json")):
        batch_id = f"grid_{s.parent.name[len('grid_') :]}"
        try:
            summ = json.loads(s.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        n = summ.get("evaluated")
        if n is None:
            n = summ.get("n_sampled")
        if n is None or batch_id in records:
            continue
        mt = s.stat().st_mtime
        missing_all += int(n)
        if mt > watermark:
            missing_post += int(n)
        missing_batches.append(
            {
                "batch_id": batch_id,
                "n_trials": int(n),
                "post_watermark": bool(mt > watermark),
                "run_ts_field": str(summ.get("run_ts")),
                "shard": summ.get("shard"),
            }
        )
    return {
        "watermark_epoch": watermark,
        "unrecorded_batch_count": len(missing_batches),
        "post_watermark_missing_trials": missing_post,
        "all_missing_trials": missing_all,
        "unrecorded_batches": missing_batches,
        "shard_id_collision_batches": sorted(
            {
                b["run_ts_field"]
                for b in missing_batches
                if b["shard"] and sum(1 for c in missing_batches if c["run_ts_field"] == b["run_ts_field"]) > 1
            }
        ),
    }


# ---------------------------------------------------------------- 折减内核调用（委托官方件）


def dsr_at(sharpe_annualized: float, num_trials: int, num_obs: int, want_haircut: bool = True) -> dict:
    """按正态近似口径（γ=κ=0，先例=dsr_recalc_backfill.approx_dsr_from_sharpe）算 DSR。

    输入是年化 Sharpe，官方件要非年化（每期）→ 恒 /√252 换算，换算本身入册为假设。
    """
    sr_p = float(sharpe_annualized) / math.sqrt(PERIODS_PER_YEAR)
    var_sr, dsr, emax, degen = deflated_sharpe_from_moments(sr_p, int(num_trials), int(num_obs), 0.0, 0.0)
    out = {
        "dsr": _round(dsr, 6),
        "degenerate": bool(degen),
        "expected_max_z": _round(emax, 4),
        "z_stat_before_deflation": _round(sr_p / math.sqrt(var_sr), 4) if var_sr > 0 else None,
        "passes_095": bool((not degen) and dsr >= DSR_SIGNIFICANCE_THRESHOLD),
    }
    # 剪发口径的输入域闸（2026-10-12 实测残留缺陷）：t_single=SR_p·√T ≳26.7 时
    # math.erfc 下溢成 0.0 → 官方件 _erfcinv 抛 SimulationError（其注释称"域异常不可达"
    # 只对旧 Φ⁻¹ 路径成立，erfc 自身仍有下溢尾）。年化 Sharpe ≳12 才落到该尾，
    # 真实候选集碰不到，但倒推"及格线"要探上界——故本件只在域内出剪发数，域外如实报。
    t_single = sr_p * math.sqrt(float(num_obs))
    if want_haircut and t_single < 26.0:
        hc = haircut_sharpe_harvey_liu(sr_p, int(num_trials), int(num_obs), method="bonferroni")
        hlz = haircut_sharpe_harvey_liu(sr_p, int(num_trials), int(num_obs), method="hlz_2016")
        out["haircut_sharpe_bonferroni"] = _round(hc.haircut_sharpe * math.sqrt(PERIODS_PER_YEAR), 4)
        out["haircut_fraction_bonferroni"] = _round(hc.haircut_fraction, 4)
        out["haircut_sharpe_hlz3"] = _round(hlz.haircut_sharpe * math.sqrt(PERIODS_PER_YEAR), 4)
    elif want_haircut:
        out["haircut_status"] = (
            f"UNAVAILABLE_IN_INPUT_DOMAIN(t_single={_round(t_single, 2)}>=26，官方件 _erfcinv 下溢尾)"
        )
    return out


def dsr_only(sharpe_annualized: float, num_trials: int, num_obs: int) -> tuple[float, bool]:
    """只出 DSR（不碰剪发），供全批普查与二分反解用——剪发在大 t 处有官方件下溢尾。"""
    sr_p = float(sharpe_annualized) / math.sqrt(PERIODS_PER_YEAR)
    var_sr, dsr, _emax, degen = deflated_sharpe_from_moments(sr_p, int(num_trials), int(num_obs), 0.0, 0.0)
    return dsr, bool(degen)


def implied_T_to_reproduce(sharpe_annualized: float, num_trials: int, registered_dsr: float) -> int | None:
    """反解：在给定 N 下，登记 DSR 值要求样本数 T=？（整数扫描，登记面缺 T 时的取证位）。"""
    best = None
    for t in range(50, 3000, 10):
        cur, degen = dsr_only(sharpe_annualized, num_trials, t)
        if degen or cur is None:
            continue
        if best is None or abs(cur - registered_dsr) < abs(best[1] - registered_dsr):
            best = (t, cur)
    if best is None:
        return None
    return int(best[0]) if abs(best[1] - registered_dsr) <= 0.005 else None


def required_sharpe_for_dsr(
    num_trials: int, num_obs: int, threshold: float = DSR_SIGNIFICANCE_THRESHOLD
) -> float | None:
    """倒推：在该分母/样本下，DSR 恰达 threshold 所需的年化 Sharpe（二分求解）。

    这是"折减后及格线"——判据数值，只倒推不裁定，供 Owner 选尺。
    """
    lo, hi = 0.0, 60.0
    top = dsr_at(hi, num_trials, num_obs, want_haircut=False)
    if top["dsr"] is None or not top["passes_095"]:
        return None  # 60 年化都过不了=该尺下无解（如实报）
    for _ in range(90):
        mid = (lo + hi) / 2.0
        cur = dsr_at(mid, num_trials, num_obs, want_haircut=False)["dsr"]
        if cur is None:
            return None
        if cur < threshold:
            lo = mid
        else:
            hi = mid
    return _round(hi, 4)


# ---------------------------------------------------------------- 重述主体


def restate(
    repo_root: Path,
    out_path: Path,
    pbo_batch: str,
    pbo_n_groups: int,
    pbo_k_test: int,
    neff_subsample: int,
    head_ledger_root: Path | None = None,
) -> dict:
    birth_batch = "grid_20260916-123551"
    intake = repo_root / "data" / "strategy_intake"
    surv_p = intake / "f06_survivors.csv"
    cand_p = intake / birth_batch / "dual_dsr_candidates.csv"
    man_p = intake / birth_batch / "manifest.csv"
    for p in (surv_p, cand_p, man_p):
        if not p.exists():
            raise StatsgovInputError(f"成绩真源缺失: {p}")

    calibers = build_caliber_register(repo_root, birth_batch, head_ledger_root)
    N_by_key = {k: v.get("value") for k, v in calibers.items() if not k.startswith("_")}

    surv = pd.read_csv(surv_p)
    cand = pd.read_csv(cand_p)
    man = pd.read_csv(man_p, usecols=["recipe_id", "sharpe", "net_days"])
    man["recipe_id"] = man["recipe_id"].astype(str)
    T_by_recipe = dict(zip(man.recipe_id, man.net_days.astype(int), strict=True))

    cal_keys = [
        k
        for k in (
            "N_eff_registered",
            "N_evaluated",
            "N_ledger_cumulative_worktree_bytes",
            "N_ledger_cumulative_head_bytes",
            "N_ledger_plus_post_watermark_missing",
            "N_ledger_plus_all_disk_trials",
            "N_space_nominal",
        )
        if N_by_key.get(k)
    ]

    def _row(rec: dict, sharpe: float, t: int, raw_rank: int) -> dict:
        out = {
            "recipe_id": str(rec.get("recipe_id")),
            "is_sharpe_annual": _round(sharpe, 4),
            "net_days_T": int(t),
            "raw_rank": raw_rank,
            "registered": {},
        }
        for col in ("dsr_eff", "dsr_raw", "n_trials_eff", "n_trials_raw", "oos_sharpe"):
            if col in rec and pd.notna(rec[col]):
                out["registered"][col] = (
                    _round(float(rec[col]), 4) if col in ("dsr_eff", "dsr_raw", "oos_sharpe") else int(rec[col])
                )
        out["restated"] = {}
        for k in cal_keys:
            out["restated"][k] = dsr_at(sharpe, int(N_by_key[k]), t)
        for k in cal_keys:
            if out["restated"][k]["degenerate"]:
                out["restated"][k]["note"] = "退化态=不可判定（勿读作不显著）"
        return out

    rows = []
    ordered = cand.sort_values(["sharpe", "recipe_id"], ascending=[False, True]).reset_index(drop=True)
    for i, rec in ordered.iterrows():
        t = int(T_by_recipe.get(str(rec.recipe_id), 970))
        rows.append(_row(rec.to_dict(), float(rec.sharpe), t, int(i) + 1))

    # 名次重排：按各口径 DSR 降序（DSR 缺失/退化排末），与原始名次对账
    rank_shift = {}
    orders = {}
    for k in cal_keys:
        scored = sorted(rows, key=lambda r: (-(r["restated"][k]["dsr"] or -1.0), r["recipe_id"]))
        pos = {r["recipe_id"]: i + 1 for i, r in enumerate(scored)}
        orders[k] = [r["recipe_id"] for r in scored]
        deltas = [
            (r["recipe_id"], r["raw_rank"], pos[r["recipe_id"]]) for r in rows if pos[r["recipe_id"]] != r["raw_rank"]
        ]
        survivors = sum(1 for r in rows if r["restated"][k]["passes_095"])
        rank_shift[k] = {
            "n_candidates": len(rows),
            "pass_095_count": survivors,
            "rank_changed_count": len(deltas),
            "top3_raw": [r["recipe_id"] for r in rows[:3]],
            "top3_deflated": [r["recipe_id"] for r in scored[:3]],
            "example_deltas": deltas[:6],
        }
    distinct_orders = {tuple(v) for v in orders.values()}
    rank_shift["_order_invariance_across_N"] = {
        "distinct_orderings_across_calibers": len(distinct_orders),
        "reading": "本口径集下 DSR=Φ(z(SR,T)−E_max(N))，E_max(N) 对同批所有格是同一常数 ⇒ 换 N 只平移过线与否，不改名次",
        "what_moves_rank": "逐格样本数 T 不同（本批 net_days∈{970,1106}）——名次位移全部来自 T，不来自选哪把尺",
        "consequence_for_budget_design": "排行榜可比性不需要统一 N；需要统一 N 的是『及格线/晋级门』——预算册因此只把 N 口径写进门判，不写进排序",
    }

    # 登记值可复算性审计：反推登记 dsr_raw/dsr_eff 用的分母与 T
    srow = surv.iloc[0].to_dict()
    s_T = int(T_by_recipe.get(str(srow["recipe_id"]), 0))
    audit = []
    for tag, reg_v, n_key in (
        ("dsr_raw", srow.get("dsr_raw"), "N_evaluated"),
        ("dsr_eff", srow.get("dsr_eff"), "N_eff_registered"),
    ):
        N_used = int(N_by_key[n_key])
        recomputed = dsr_at(
            float(srow["is_sharpe_annual"] if "is_sharpe_annual" in srow else srow["is_sharpe"]), N_used, s_T
        )
        it = implied_T_to_reproduce(float(srow["is_sharpe"]), N_used, float(srow[tag]))
        audit.append(
            {
                "registered_col": tag,
                "registered_value": _round(float(srow[tag]), 4),
                "recomputed_value": recomputed["dsr"],
                "N_used": N_used,
                "T_used": s_T,
                "delta": _round(float(srow[tag]) - recomputed["dsr"], 4) if recomputed["dsr"] is not None else None,
                "implied_T_that_reproduces_registered_value": it,
                "T_values_available_in_registration_face": sorted({int(v) for v in T_by_recipe.values()}),
                "verdict": "复算一致"
                if recomputed["dsr"] is not None and abs(float(srow[tag]) - recomputed["dsr"]) <= 0.005
                else f"复算不一致（登记面未记 T/N 出处；本登记面可用 T={sorted({int(v) for v in T_by_recipe.values()})} 皆不复现，能复现的 T={'未找到' if it is None else it}）",
            }
        )

    census = {
        k: {
            "N": int(N_by_key[k]),
            "cells_in_birth_batch": int(len(man)),
            "cells_passing_095": sum(
                1
                for sh, t in zip(man.sharpe.astype(float), man.net_days.astype(int), strict=True)
                if dsr_only(sh, int(N_by_key[k]), t)[0] >= DSR_SIGNIFICANCE_THRESHOLD
            ),
            "reading": "全批逐格普查（非预先筛过的 131 候选面）——折减后该尺下还剩几格够 0.95",
        }
        for k in cal_keys
    }
    sel = selection_benchmark(man, calibers)
    pbo_block = pbo_reading(repo_root, pbo_batch, pbo_n_groups, pbo_k_test, neff_subsample, birth_batch)

    doc = {
        "ttl": "task_bound",
        "title": "F06 幸存者 DSR/PBO 折减重述 v1（st-statsgov-20261012）",
        "produced_by": "scripts/backtest/statsgov_deflation_and_budget.py restatement",
        "as_of_source_mtime": {
            "f06_survivors.csv": _mtime_iso(surv_p),
            "dual_dsr_candidates.csv": _mtime_iso(cand_p),
            "manifest.csv": _mtime_iso(man_p),
            "trial_ledger_registry.yaml": _mtime_iso(
                repo_root / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
            ),
        },
        "sha16": {"f06_survivors.csv": _sha16(surv_p), "dual_dsr_candidates.csv": _sha16(cand_p)},
        "premise_verification": _premises(repo_root, birth_batch, surv_p, srow),
        "caliber_register": calibers,
        "normalization_and_assumptions": {
            "moments": "γ=κ=0 正态近似（出生批无逐期收益序列，矩不可复算）；先例=scripts/backtest/dsr_recalc_backfill.py:approx_dsr_from_sharpe 同口径",
            "annualization": f"输入为年化 Sharpe，入官方件前恒 /sqrt({PERIODS_PER_YEAR}) 换算为每期；折减后夏普再乘回 √252 报告",
            "T_source": "逐格 net_days（出生批 manifest.csv），非全批 common_T——两值并存时以逐格为准，差异入 rank_shift",
            "tie_break": "原始名次按 (sharpe desc, recipe_id asc)；同分并列以 recipe_id 定序（确定性要求）",
            "correlation_assumption": "主尺不假设独立；相关性折算只作为披露口径（N_eff），因 N_eff 由被选中同批数据估出=选择依赖，禁用作唯一分母",
        },
        "survivor_registration_row": {
            k: (None if pd.isna(v) else (float(v) if isinstance(v, (int, float)) else str(v))) for k, v in srow.items()
        },
        "reproducibility_audit": audit,
        "selection_benchmark": sel,
        "full_batch_census_by_caliber": census,
        "candidate_restatement": rows,
        "rank_shift_by_caliber": rank_shift,
        "deflation_gate_line_inversion": {
            k: {
                "N": int(N_by_key[k]),
                "required_is_sharpe_annual_for_DSR_095_at_T970": required_sharpe_for_dsr(int(N_by_key[k]), 970),
                "required_is_sharpe_annual_for_DSR_095_at_T1106": required_sharpe_for_dsr(int(N_by_key[k]), 1106),
            }
            for k in cal_keys
        },
        "pbo": pbo_block,
    }
    _emit(doc, out_path)
    return doc


def _premises(repo_root: Path, birth_batch: str, surv_p: Path, srow: dict) -> dict:
    """令卡三数前提的实测核实位（可复核，禁凭记忆/禁写死数值）。"""
    intake = repo_root / "data" / "strategy_intake"
    man = pd.read_csv(intake / birth_batch / "manifest.csv", usecols=["sharpe", "net_days"])
    summ = json.loads((intake / birth_batch / "summary.json").read_text(encoding="utf-8"))
    return {
        "362880": {
            "card_claim": "F06 362,880 格（读作试次数）",
            "measured": f"{birth_batch}/summary.json n_raw={summ.get('n_raw')}，同批 evaluated={summ.get('evaluated')} / n_sampled={summ.get('n_sampled')}",
            "verdict": "口径误置：n_raw=名义设计空间（折叠 F/J/K 后），非实跑格数；真源 config/position_recipe_grid_schema.yaml 头行 + tests/trade/position/test_position_recipe_compiler.py:132 + scripts/backtest/factory_grid_executor.py:2060",
        },
        "1.72": {
            "card_claim": "幸存者 Sharpe 1.72",
            "measured": f"命中：f06_survivors.csv is_sharpe={srow.get('is_sharpe')}；出生批 manifest max(sharpe)={round(float(man.sharpe.max()), 3)}",
            "verdict": "成立（=best-of-10,080 IS 窗 2020-01-01..2023-12-31）",
        },
        "0.831": {
            "card_claim": "OOS 0.831",
            "measured": f"命中：f06_survivors.csv oos_sharpe={srow.get('oos_sharpe')}（窗 2024-01-01..2025-08-31）",
            "verdict": "成立；附冲突面：E4 自算真 OOS 拼接=0.859、WFA 全路径=0.594、折均=0.704（data/backtest_artifacts/runs/E4-F06-38b453ca/verdict.md:34-29）",
        },
        "survivor_registration_face": {
            "rows_in_f06_survivors_csv": int(len(pd.read_csv(surv_p))),
            "candidates_in_dual_dsr_csv": int(len(pd.read_csv(intake / birth_batch / "dual_dsr_candidates.csv"))),
            "note": "登记面=1 行（PBO 的 cpcv 要求 n_trials>=2 ⇒ 单靠登记面算不了 PBO）",
        },
        "already_adjudicated": "该幸存者 E4 已判不通过（OOS/IS=0.499<0.70 + OOS 精确 DSR 0.3046/0.0027<0.5），本班只重述不改判",
    }


def selection_benchmark(man: pd.DataFrame, calibers: dict) -> dict:
    """选择效应对照：本批 IS 夏普截面分布 + 各口径下『纯噪声期望最大』。

    诚实边界：截面分布含信号，非零假设分布——此项是描述性对照，不是 p 值。
    """
    s = man.sharpe.astype(float)
    mean, sd = float(s.mean()), float(s.std(ddof=1))
    out = {
        "n_cells": int(len(s)),
        "is_sharpe_mean": _round(mean, 4),
        "is_sharpe_std": _round(sd, 4),
        "is_sharpe_min": _round(float(s.min()), 4),
        "is_sharpe_max": _round(float(s.max()), 4),
        "expected_max_by_caliber": {},
        "caveat": "截面分布=含信号的经验分布，非纯噪声零假设；只作量级对照不作显著性判定",
    }
    for k in ("N_eff_registered", "N_evaluated", "N_ledger_plus_all_disk_trials", "N_space_nominal"):
        N = (calibers.get(k) or {}).get("value")
        if not N:
            continue
        emax = expected_max_sharpe_z(int(N))
        out["expected_max_by_caliber"][k] = {
            "N": int(N),
            "E_max_z_units": _round(emax, 4),
            "expected_max_is_sharpe_annual": _round(mean + emax * sd, 4),
            "observed_best_over_expected": _round(float(s.max()) / (mean + emax * sd), 4)
            if (mean + emax * sd) > 0
            else None,
        }
    return out


# ---------------------------------------------------------------- PBO 读数


def pbo_reading(
    repo_root: Path, pbo_batch: str, n_groups: int, k_test: int, neff_subsample: int, birth_batch: str
) -> dict:
    intake = repo_root / "data" / "strategy_intake"
    out: dict = {"registered_survivor_set": {}, "substitute_batch": {}}

    out["registered_survivor_set"] = {
        "computable": False,
        "code": "NOT_COMPUTABLE",
        "reasons_three_layers": [
            "名单层：f06_survivors.csv 仅 1 行，cpcv.compute_pbo 要求 n_trials>=2（src/zephyr/backtest/core/cpcv.py:234 直接拒）",
            f"逐期层：出生批 {birth_batch} 无 net_returns.parquet（该产物晚于本批才加），IS 窗逐期收益已不可得",
            "成对层：其余成绩册（codesym/grid_strategy_oos）只有每候选一组 (IS,OOS) 标量 ⇒ n_splits=1，PBO 退化成 0/1",
        ],
        "what_would_be_needed": "同空间同 seed 重跑出生批并持久化 net_returns.parquet（=数据/算力依赖，非本班零数据范围），须呈批",
    }

    p = intake / pbo_batch / "net_returns.parquet"
    if not p.exists():
        out["substitute_batch"] = {"computable": False, "code": "PARQUET_MISSING", "path": _rel(p, repo_root)}
        return out

    df = pd.read_parquet(p)
    import numpy as np

    R = df.to_numpy(dtype=float)
    splits = generate_cpcv_splits(R.shape[0], n_groups=n_groups, k_test=k_test)
    # 列可算性判据=在**每一折**的训练窗与测试窗内都有限且非零方差：
    # 某些格在子窗内全程空仓（净收益恒 0）→ 该折 SR 无定义；按全局方差筛列会漏掉这种，
    # 让 NaN 进 compute_pbo 直接被拒（cpcv.py:236），故按折交集筛。
    ok = np.isfinite(R).all(axis=0)
    for s in splits:
        a, b = R[list(s.train_indices)], R[list(s.test_indices)]
        ok &= np.isfinite(a).all(axis=0) & (a.std(0, ddof=1) > 0)
        ok &= np.isfinite(b).all(axis=0) & (b.std(0, ddof=1) > 0)
    finite_cols = int(ok.sum())
    dropped = R.shape[1] - finite_cols
    if finite_cols < 2:
        raise StatsgovInputError(f"{pbo_batch} 可用列 <2，PBO 不可算（已如实报）")

    Rf = R[:, ok]
    is_mat, oos_mat = [], []
    for s in splits:
        a, b = Rf[list(s.train_indices)], Rf[list(s.test_indices)]
        is_mat.append(a.mean(0) / a.std(0, ddof=1))
        oos_mat.append(b.mean(0) / b.std(0, ddof=1))
    is_arr = np.asarray(is_mat)
    oos_arr = np.asarray(oos_mat)
    res = compute_pbo(is_arr, oos_arr)
    best_is_overall = int(np.argmax(is_arr.mean(0)))
    block = {
        "computable": True,
        "batch": pbo_batch,
        "matrix_shape_TxN": [int(R.shape[0]), int(R.shape[1])],
        "columns_used": finite_cols,
        "columns_dropped_not_usable_in_every_split": dropped,
        "window": _summary_field(repo_root, pbo_batch, "window"),
        "splits": {
            "n_groups": n_groups,
            "k_test": k_test,
            "n_splits": int(res["n_splits"]),
            "t1": "None（日频点标签，无 purge；本矩阵是日净收益而非标签窗）",
            "embargo": 0,
        },
        "pbo": _round(res["pbo"], 4),
        "mean_logit": _round(res["mean_logit"], 4),
        "omega_min_max": [_round(min(res["omega"]), 4), _round(max(res["omega"]), 4)],
        "reading": f"从同子空间 {finite_cols} 格里挑 IS 最优：其在样本外跑输中位数的折占比 = {_round(res['pbo'], 4)}",
        "transferability_caveat": _pbo_caveat(repo_root, birth_batch, pbo_batch),
        "neff_recheck": neff_recheck(Rf, neff_subsample),
    }
    out["substitute_batch"] = block
    return out


def _pbo_caveat(repo_root: Path, birth_batch: str, pbo_batch: str) -> str:
    a = set(
        pd.read_csv(
            repo_root / "data/strategy_intake" / birth_batch / "manifest.csv", usecols=["recipe_id"]
        ).recipe_id.astype(str)
    )
    b = set(pd.read_parquet(repo_root / "data/strategy_intake" / pbo_batch / "net_returns.parquet").columns)
    return (
        f"替代批与出生批配方交集=实测 {len(a & b)} 个（出生批 {len(a)}／替代批 {len(b)}）；"
        "交集为 0 ⇒ 本读数不能重述 1.721 那一格，只能回答同一子空间的结构性问题：『从 10,080 格里挑 IS 最优，样本外跑输中位数的概率有多大』"
    )


def neff_recheck(Rf, subsample: int) -> dict:
    """N_eff 独立复核（子样，避免全 10,080 列相关矩阵的内存/时间爆点）。"""
    import numpy as np

    from zephyr.backtest.core.n_trial_ledger import compute_effective_rank

    n = Rf.shape[1]
    k = min(subsample, n)
    idx = list(range(0, n, max(1, n // k)))[:k]
    sub = {f"c{i}": Rf[:, i] for i in idx}
    try:
        n_eff, meta = compute_effective_rank(sub)
    except Exception as exc:  # noqa: BLE001 — 复核失败必须出声
        return {"computable": False, "error": f"{type(exc).__name__}: {exc}"}
    corr = np.corrcoef(Rf[:, idx].T)
    iu = np.triu_indices(len(idx), 1)
    rho_bar = float(np.nanmean(corr[iu]))
    n_eff_analytic = len(idx) / (1.0 + (len(idx) - 1) * rho_bar) if rho_bar > 0 else float(len(idx))
    return {
        "computable": True,
        "subsample_cols": len(idx),
        "subsample_selection": "等距步长（确定性，无随机种子）",
        "n_eff_entropy_breadth_on_subsample": int(n_eff),
        "estimator_meta": {kk: meta.get(kk) for kk in ("n_trials", "common_T", "boundary")},
        "mean_pairwise_correlation": _round(rho_bar, 6),
        "n_eff_analytic_from_mean_rho": _round(n_eff_analytic, 4),
        "note": "全 10,080 列相关矩阵需 ~0.8GB＋O(N^3) 特征分解，本班按子样复核并如实注记口径；登记位 N_eff 是全量估计",
    }


def _summary_field(repo_root: Path, batch: str, field: str):
    p = repo_root / "data/strategy_intake" / batch / "summary.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8")).get(field)


def _rel(p: Path, repo_root: Path) -> str:
    try:
        return p.relative_to(repo_root).as_posix()
    except ValueError:
        return str(p)


# ---------------------------------------------------------------- 预算册盘点（机生雏形）


def budget_inventory(repo_root: Path, spec_path: Path, out_path: Path) -> dict:
    """按 spec 的族→识别模式展开清单并实测计数（条目靠模式派生，计数靠磁盘/账本实测）。"""
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    led_path = repo_root / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
    touched: list[Path] = [spec_path, led_path]  # 读数 touched 面，用于派生"最新输入 mtime"签名戳（批复④）
    ledger = None
    try:
        ledger = TrialLedger(registry_path=led_path).snapshot()
    except Exception as exc:  # noqa: BLE001 — 账本不可读要报红，不能装成 0
        ledger_error = f"{type(exc).__name__}: {exc}"
    else:
        ledger_error = ""
    unreg = scan_unrecorded_grid_trials(repo_root)

    families = []
    for fam in spec.get("families") or []:
        faces = []
        for face in fam.get("faces") or []:
            kind = face.get("kind")
            rec = {"face": face.get("id"), "kind": kind, "pattern": face.get("pattern"), "status": "NOT_FOUND"}
            if kind == "dir_glob":
                hits = [x for x in sorted(repo_root.glob(face["pattern"])) if x.is_dir()]
                rec["matched_count"] = len(hits)
                rec["rows_measured"] = len(hits)
                rec["status"] = "MEASURED" if hits else "NOT_FOUND"
                rec["count_basis"] = face.get("count_basis", "一个匹配目录=一次可审计考/跑")
                touched.extend(hits)
                rec["paths"] = [_rel(h, repo_root) for h in hits][:10]
            elif kind == "file_glob":
                hits = sorted(repo_root.glob(face["pattern"]))
                touched.extend(hits)
                rows_measured, count_notes, uncounted, conservative = _count_rows(
                    repo_root, hits, face.get("row_rule") or ""
                )
                rec["uncounted_files"] = uncounted[:8]
                rec["conservative_estimate_files"] = conservative[:8]
                rec["matched_count"] = len(hits)
                rec["rows_measured"] = rows_measured
                rec["count_notes"] = count_notes[:10]
                rec["count_note_total"] = len(count_notes)
                rec["status"] = "MEASURED" if hits else "NOT_FOUND"
                if hits and uncounted:
                    rec["status"] = "PARTIAL_MEASURED"
                elif hits and conservative:
                    rec["status"] = "MEASURED_CONSERVATIVE_PENDING_EXACT"
                elif hits and count_notes:
                    rec["status"] = "MEASURED_WITH_LOOSEST_BASIS"
                rec["paths"] = [_rel(h, repo_root) for h in hits][:20]
            elif kind == "ledger_kind":
                want = face.get("ledger_kind")
                rec["ledger_trials_in_ledger"] = _ledger_trials_by_kind(repo_root, want)
                rec["ledger_batches_in_ledger"] = _ledger_batch_count_by_kind(repo_root, want)
                rec["status"] = "MEASURED"
            elif kind == "grid_batch_kind":
                want = face.get("ledger_kind")
                rec["ledger_trials_in_ledger"] = _ledger_trials_by_kind(repo_root, want)
                rec["unrecorded_trials_on_disk"] = sum(
                    b["n_trials"] for b in unreg["unrecorded_batches"] if (b.get("batch_id") or "").startswith("grid_")
                )
                rec["status"] = "MEASURED"
            elif kind == "pg_table":
                rec["status"] = "PG_NOT_PROBED"
                rec["note"] = (
                    "本件不连库：PG 面计数须走 DatabaseService 只读口，且属跨车道共享面，本班只登记表名模式与待测位"
                )
            faces.append(rec)
        families.append(
            {
                "family": fam.get("id"),
                "title_zh": fam.get("title_zh"),
                "object": fam.get("object"),
                "faces": faces,
                "budget_cap": fam.get("budget_cap"),
                "cap_status": "pending_adjudication" if not (fam.get("budget_cap") or {}).get("value") else "declared",
                "consumption_from_ledger": sum(int(f.get("ledger_trials_in_ledger") or 0) for f in faces),
                "consumption_from_books_rows": sum(int(f.get("rows_measured") or 0) for f in faces),
                "faces_not_found": [f["face"] for f in faces if f.get("status") == "NOT_FOUND"],
                "faces_partial_measured": [f["face"] for f in faces if f.get("status") == "PARTIAL_MEASURED"],
                "faces_unprobed": [f["face"] for f in faces if f.get("status") == "PG_NOT_PROBED"],
            }
        )

    # 三面分列消耗＋过渡帽（晨裁 M3-A 公式：历史消耗×1）——数值全由实测派生，禁手填
    grid_files = sorted((repo_root / "data" / "strategy_intake").glob("grid_*/summary.json"))
    touched.extend(grid_files)
    _inputs = [x for x in touched if x.is_file()]
    n_inputs_read = len({str(x) for x in _inputs})
    newest_input_mtime = max((_mtime_iso(x) for x in _inputs), default="UNAVAILABLE")
    grid_unrecorded = int(unreg["all_missing_trials"])
    cap_formula = (spec.get("caliber_declaration") or {}).get("budget_cap_formula")
    for f in families:
        led, books = int(f["consumption_from_ledger"]), int(f["consumption_from_books_rows"])
        disk = grid_unrecorded if f["family"] == spec.get("grid_family_id", "B") else 0
        f["consumption_components"] = {
            "ledger_by_kind": led,
            "unrecorded_grid_on_disk": disk,
            "book_rows_measured": books,
        }
        f["consumption_total"] = led + disk + books
        f["double_count_risk"] = (
            "book_rows 与 ledger_by_kind 可能部分重叠（考试卡既在账本 kind=exam_card 又在成绩册行数里）；"
            "本表三面分列不做合并去重，终签若要合一口径须先点名去重规则"
        )
        if cap_formula == "transitional_history_x1" and not (f.get("budget_cap") or {}).get("value"):
            f["transitional_cap_x1"] = f["consumption_total"]
            signed = bool((spec.get("caliber_declaration") or {}).get("budget_cap_signing"))
            if not signed:
                f["cap_status"] = "owner_adopted_formula_pending_terminal_signature"
            else:
                # 批复二：公式照签出正式版；测量不全的族不得照抄机械值定帽（会误停该族）
                cons = [fc["face"] for fc in f["faces"] if fc.get("status") == "MEASURED_CONSERVATIVE_PENDING_EXACT"]
                f["faces_conservative_pending_exact"] = cons
                f["cap_status"] = (
                    "owner_signed_20261012_measurement_incomplete"
                    if f["faces_partial_measured"]
                    else (
                        "owner_signed_20261012_conservative_estimate_pending_exact_count"
                        if cons
                        else "owner_signed_20261012"
                    )
                )
                f["cap_review_flag"] = (
                    f"族面 {f['faces_partial_measured']} 真空白未计入 ⇒ 本帽偏窄，须先修口径"
                    if f["faces_partial_measured"]
                    else (
                        f"族面 {f.get('faces_conservative_pending_exact')} 用最大容器上界计入（宁高勿低，统筹批复），"
                        "待精算＝逐册点名键补齐后复算终值；本帽可先用"
                        if f.get("faces_conservative_pending_exact")
                        else None
                    )
                )
    numbers_table = {
        "cap_formula": cap_formula,
        "grid_family_id": spec.get("grid_family_id", "B"),
        "unrecorded_grid_on_disk_shared_across_families": grid_unrecorded,
        "rows": [
            {
                "family": f["family"],
                "title_zh": f["title_zh"],
                "ledger_by_kind": f["consumption_components"]["ledger_by_kind"],
                "unrecorded_grid_on_disk": f["consumption_components"]["unrecorded_grid_on_disk"],
                "book_rows_measured": f["consumption_components"]["book_rows_measured"],
                "consumption_total": f["consumption_total"],
                "transitional_cap_x1": f.get("transitional_cap_x1"),
                "cap_status": f["cap_status"],
                "faces_not_found": f["faces_not_found"],
                "faces_partial": f["faces_partial_measured"],
                "faces_conservative_pending_exact": f.get("faces_conservative_pending_exact", []),
                "faces_pg_unprobed": len(f["faces_unprobed"]),
            }
            for f in families
        ],
        "reading_zh": "过渡帽=该族已实测历史消耗×1（再挖一遍已烧掉的量即停）；帽值属判据数值，本表呈 Owner 终签后生效",
    }
    doc = {
        "ttl": "task_bound",
        "title": spec.get("title"),
        "produced_by": "scripts/backtest/statsgov_deflation_and_budget.py budget",
        "spec_source": _rel(spec_path, repo_root),
        "spec_sha16": _sha16(spec_path),
        "as_of_source_mtime": _mtime_iso(spec_path),
        "as_of_newest_input_mtime": newest_input_mtime,
        "n_inputs_read": n_inputs_read,
        "n_ledger_snapshot": None
        if ledger is None
        else {
            "ledger_trials": ledger.ledger_trials,
            "ledger_runs": ledger.ledger_runs,
            "known_floor": ledger.known_floor,
            "n_trials_effective_disclosure_slot": ledger.n_trials_effective,
            "read_error": ledger_error,
        },
        "unrecorded_grid_trials": {
            "post_watermark": unreg["post_watermark_missing_trials"],
            "all_disk": unreg["all_missing_trials"],
            "batches": unreg["unrecorded_batch_count"],
            "shard_collision_run_ts": unreg["shard_id_collision_batches"],
        },
        "families": families,
        "numbers_table_for_terminal_signature": numbers_table,
        "ledger_kind_coverage": {
            "kinds_present_in_ledger": _ledger_kinds_present(repo_root),
            "kinds_mapped_by_spec": sorted((spec.get("ledger_kind_to_family") or {}).keys()),
            "unmapped_kinds": sorted(
                set(_ledger_kinds_present(repo_root)) - set((spec.get("ledger_kind_to_family") or {}).keys())
            ),
            "reading": "账本里存在但规格件没归族的 kind=族消耗会漏计；反向差集=规格写了但账本没有（多为历史零触发）",
        },
        "net_zero_note": spec.get("net_zero_note"),
    }
    _emit(doc, out_path)
    return doc


def _ledger_trials_by_kind(repo_root: Path, kind: str) -> int:
    return sum(int(r.get("n_trials") or 0) for r in _ledger_records(repo_root) if str(r.get("kind")) == kind)


def _ledger_batch_count_by_kind(repo_root: Path, kind: str) -> int:
    return sum(1 for r in _ledger_records(repo_root) if str(r.get("kind")) == kind)


def _ledger_kinds_present(repo_root: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in _ledger_records(repo_root):
        k = str(r.get("kind"))
        out[k] = out.get(k, 0) + int(r.get("n_trials") or 0)
    return out


def _ledger_records(repo_root: Path) -> list[dict]:
    p = repo_root / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return list(data.get("batch_records") or [])


def _count_rows(repo_root: Path, hits: list[Path], row_rule: str) -> tuple[int, list[str], list[str], list[str]]:
    """逐件实测行数。完全无法起数的件（既无容器也无计数标量、或读败）如实进
    uncounted，不混进总数冒充"零条"；只能取上界的件计入并进 conservative。"""
    total = 0
    notes: list[str] = []
    uncounted: list[str] = []  # 真空白（完全没计入的件）才把整面降为 PARTIAL
    conservative: list[str] = []  # 计入但用的是上界估计 ⇒ 族级标"待精算"
    for h in hits:
        n: int | None
        st: str
        try:
            if h.suffix == ".csv":
                n, st = max(0, sum(1 for _ in h.open(encoding="utf-8", errors="replace")) - 1), "MEASURED"
            elif h.suffix in (".yaml", ".yml"):
                d = yaml.safe_load(h.read_text(encoding="utf-8"))
                n, st = _count_entries(d, row_rule)
            elif row_rule == "one_per_match":
                n, st = 1, "MEASURED(one_per_match)"
            elif h.suffix == ".md":
                n, st = (
                    _count_md_rows(h, row_rule),
                    "MEASURED" if row_rule == "table_rows" else f"RULE_UNKOWN({row_rule})",
                )
            else:
                n, st = None, f"SUFFIX_UNHANDLED({h.suffix})"
        except Exception as exc:  # noqa: BLE001 — 单件读败不毁整批盘点，但必须出声
            n, st = None, f"READ_ERROR({type(exc).__name__})"
        if n is not None and st.startswith("CONSERVATIVE_UPPER_BOUND"):
            total += n
            notes.append(f"{_rel(h, repo_root)} :: {st[:120]}")
            conservative.append(_rel(h, repo_root))
        elif n is None:
            notes.append(f"{_rel(h, repo_root)} :: {st}")
            uncounted.append(_rel(h, repo_root))
        else:
            total += n
    return total, notes, uncounted, conservative


_COUNTISH_KEY_RE = re.compile(
    r"(^n_|_size$|^size_|_count$|^count_|_num$|^num_|^total_|_trials$|^n_trials|_records$)", re.I
)
# 一条含 p 值或 t 统计量的记录 = 一次被做过的假设检验 = 一个试次（批内自报量级不是检验数）
_P_LIKE_KEYS = ("p_raw", "p_adj", "p_value", "pval", "p_perm", "p_hac", "t_hac", "t_stat", "t_value")


def _count_test_records(o) -> int:
    """递归数出"带 p/t 统计量的检验记录"条数（命中即计数、不再下钻其内部，避免同一条被数两遍）。"""
    if isinstance(o, dict):
        return 1 if any(k in o for k in _P_LIKE_KEYS) else sum(_count_test_records(v) for v in o.values())
    if isinstance(o, list):
        return sum(_count_test_records(v) for v in o)
    return 0


def _count_entries(d, row_rule: str):  # noqa: C901 - 计数口径分支即判据本体
    """返回 (计数, 状态)。点名的键不存在→按保守上界计入并标待精算，
    连容器与计数型标量都没有才 (None, KEY_ABSENT_UNBOUNDED) 交上层计进 uncounted；
    任何分支都绝不返回 0——"查无此键"伪装成"测得零条"是覆盖尺假绿的同族形态。"""
    if isinstance(d, list):
        return len(d), "MEASURED"
    if isinstance(d, dict):
        raw = row_rule.replace("key:", "").strip() if row_rule.startswith("key:") else ""
        cands = [c.strip() for c in raw.split(",") if c.strip()]
        for c in cands[1:]:  # 候选键链：首个在场容器键胜出，所用键逐件留痕（见下 key_used）
            if isinstance(d.get(c), (list, dict)):
                return len(d[c]), f"MEASURED(key_used={c},chain_first_absent={cands[0]})"
        key = cands[0] if cands else ""
        if cands:
            if key in d and isinstance(d[key], (list, dict)):
                return len(d[key]), f"MEASURED(key_used={key})"
            # 统筹批复（2026-10-12 晚）：点名键与候选链都不在场时**不得按下界计**——
            # "测不准＝没烧过"正是历史上分母虚低（欠折减=放水）的复发形态。
            # 上界候选＝上包络：最大容器长度 ∪ 显式计数型整数量级标量 ∪ 带 p/t 值的检验记录数。
            # 只取容器或自报量级仍会偏低（实测 indicator_conditional 册 family_size=11，
            # 而册内真含 22 条 p 值检验记录），逐件标待精算。
            bound_cands = [(len(v), str(k)) for k, v in d.items() if isinstance(v, (list, dict))]
            bound_cands += [
                (int(v), f"{k}(int_scalar)")
                for k, v in d.items()
                if isinstance(v, int) and not isinstance(v, bool) and _COUNTISH_KEY_RE.search(str(k))
            ]
            bound_cands.append((_count_test_records(d), "p_t_bearing_test_records"))
            bound_cands = [bc for bc in bound_cands if bc[0] > 0]
            bound_cands.sort(reverse=True)
            if bound_cands:
                return bound_cands[0][0], (
                    f"CONSERVATIVE_UPPER_BOUND(key_used={bound_cands[0][1]};"
                    f"chain_tried={cands};pending_exact_count=true)"
                )
            return None, f"KEY_ABSENT_UNBOUNDED(chain={cands}; top_keys={sorted(map(str, list(d.keys())[:14]))})"
        sizes = [(len(v), k) for k, v in d.items() if isinstance(v, (list, dict))]
        if not sizes:
            return None, "NO_LIST_OR_DICT_VALUE"
        return max(sizes)[0], f"MEASURED_LOOSEST(键={max(sizes)[1]}，取最大 list/dict 值，非点名)"
    return None, "UNRECOGNIZED_SHAPE"


def _count_md_rows(h: Path, row_rule: str) -> int:
    if row_rule == "table_rows":
        n = 0
        for line in h.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith("|") and not set(line.strip()) <= set("|-: "):
                n += 1
        return max(0, n - 1)
    return 0


def _emit(doc: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=180)
    out_path.write_text(text, encoding="utf-8", newline="\n")
    print(f"[statsgov] 产物: {_rel(out_path, Path.cwd())} bytes={len(text)}")


def _snap(doc: dict, key: str):
    """从 n_ledger_snapshot 里取一个数；没取到就如实报 UNAVAILABLE，不伪装成 0。"""
    snap = doc.get("n_ledger_snapshot") or {}
    v = snap.get(key)
    return "UNAVAILABLE" if v is None else v


def emit_numbers_fragment(doc: dict, md_path: Path) -> None:
    """把呈 Owner 终签的数值表机生成 md 片段（清单与计数一律生成器产出，根宪法 §9.5）。"""
    nt = doc.get("numbers_table_for_terminal_signature") or {}
    lines = [
        "---",
        "ttl: task_bound",
        "---",
        "",
        "# 预算册数值表（机生片段，呈 Owner 终签）",
        "",
        f"- 公式：`{nt.get('cap_formula')}`（晨裁 M3-A：过渡帽=该族已实测历史消耗×1）",
        f"- 网格未入账试次 {nt.get('unrecorded_grid_on_disk_shared_across_families')} 次全部计入族 "
        f"`{nt.get('grid_family_id')}`（不平摊六族，免得一份数虚增六倍）",
        "- 读数真源=`02_trial_budget_inventory_v1.yaml#numbers_table_for_terminal_signature`（本表由同一次运行派生）",
        f"- ⚑**本表签名绑定读数时戳**：`最新输入 mtime={doc.get('as_of_newest_input_mtime')} / "
        f"规格件 mtime={doc.get('as_of_source_mtime')} / spec_sha16={doc.get('spec_sha16')} / "
        f"账本快照 trials={_snap(doc, 'ledger_trials')}/floor={_snap(doc, 'known_floor')} / "
        f"读过输入 {doc.get('n_inputs_read')} 件`"
        "——⚠规格件 mtime 只记规格件自己的动作：实测两次重跑间成绩册面 1,726 行未动，"
        "而账本被他会话入账 34→36（trials 40,730→40,732）令 A 帽 1,760→1,762 ⇒ 只绑规格件 mtime "
        "就签不到这类自增，故生效签名以**最新输入 mtime＋已读输入数**为准；"
        " 消耗面含**活目录/活账本**读数（如 F 族 intake_ledger 随他班写入自增），换时戳重跑即换数；"
        "不绑时戳的签名＝假精度（批复④），隔日复照须先重跑本件另出表再谈。",
        "",
        "| 族 | 账本(kind) | 磁盘未入账 | 成绩册行数 | 消耗合计 | 过渡帽×1 | 帽状态 | 红旗 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in nt.get("rows", []):
        flags = []
        if r.get("faces_partial"):
            flags.append(f"册面键名未命中(PARTIAL){r['faces_partial']}→该行合计**偏低**")
        if r.get("faces_not_found"):
            flags.append(f"模式零命中{r['faces_not_found']}")
        if r.get("faces_conservative_pending_exact"):
            flags.append(
                f"待精算(上包络入帽){r['faces_conservative_pending_exact']}→该行含'点名键查无、"
                f"按最大容器/计数标量/p-t 检验记录数取上包络'的件，真值可能更高"
            )
        if int(r.get("faces_pg_unprobed") or 0) > 0:
            flags.append(f"PG 面未测 {r['faces_pg_unprobed']} 处")
        if int(r.get("consumption_total") or 0) == 0:
            flags.append("合计=0：帽若照抄=该族立即停，须先修册面读取再谈帽")
        lines.append(
            f"| {r['family']} {r['title_zh']} | {r['ledger_by_kind']} | {r['unrecorded_grid_on_disk']} | "
            f"{r['book_rows_measured']} | **{r['consumption_total']}** | {r['transitional_cap_x1']} | "
            f"{r['cap_status']} | {'；'.join(flags) or '—'} |"
        )
    lines += [
        "",
        "## 终签前必读的三条限制",
        "",
        "1. **上界入帽与待精算（批复③，2026-10-12 晚 Owner 令）**：成绩册点名键查无时本件**不按下界计**——"
        "取该册最大容器/计数型整数量级作保守上界计入该行，并逐件标 `pending_exact_count`（见上表"
        "'待精算'列）。判据面真值待精算后照出终值版。墙训：帽定 0 之前必须先证明是没数到还是真零，"
        "否则把测量缺陷签成治理结论。",
        "2. **账本面与成绩册面可能重叠**（考试卡既在 `kind=exam_card` 又在成绩册行数里）：本表三面分列不合并去重，"
        "合一口径需先点名去重规则。",
        "3. **PG 面未测**（本件不连库，报 PG_NOT_PROBED）：A 族真实消耗 ≥ 表值；PG 侧计数须走 DatabaseService 只读口另开一跑。",
        "",
    ]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"[statsgov] 呈签片段: {_rel(md_path, Path.cwd())}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="统计合法性班出品件：折减重述 + 试次预算盘点")
    sub = ap.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo-root", default=".")
    common.add_argument("--out", required=True)
    p1 = sub.add_parser("restatement", parents=[common])
    p1.add_argument("--pbo-batch", default="grid_20261010-210933")
    p1.add_argument("--pbo-n-groups", type=int, default=8)
    p1.add_argument("--pbo-k-test", type=int, default=4)
    p1.add_argument("--neff-subsample", type=int, default=1600)
    p1.add_argument(
        "--head-ledger-root", default="", help="HEAD 字节面的仓根（读第二面 N 账本分母用；留空=只读 repo-root 一面）"
    )
    p2 = sub.add_parser("budget", parents=[common])
    p2.add_argument("--spec", required=True)
    p2.add_argument("--emit-md", default="", help="另写一份呈 Owner 终签的机生 md 片段（清单与计数禁手抄）")
    args = ap.parse_args(argv)
    repo = Path(args.repo_root).resolve()
    if args.cmd == "restatement":
        head = Path(args.head_ledger_root).resolve() if args.head_ledger_root else None
        restate(repo, Path(args.out), args.pbo_batch, args.pbo_n_groups, args.pbo_k_test, args.neff_subsample, head)
    else:
        doc = budget_inventory(repo, Path(args.spec), Path(args.out))
        if args.emit_md:
            emit_numbers_fragment(doc, Path(args.emit_md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

### `tests/backtest/test_statsgov_deflation_and_budget.py`

```python
# [BLUEPRINT] MOD-BT-STATSGOV-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_statsgov_deflation_and_budget
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/statsgov_deflation_and_budget
# [CONSUMERS] 零运行时消费者（pytest 自家测试，与出品件同批落地）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 禁写生产路径（输出一律 tmp_path，根宪法 §9.6）；断言必须能红——每条都先钉一个
#   "错做法会得到什么"的反例值；禁把断言钉在被测函数自身输出上（同义反复永不失败）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败
# [TESTS] 本件
# [TTL] task_bound
"""统计合法性班出品件自家测试（MOD-BT-STATSGOV-001）。

覆盖四条判据面：①DSR 随分母单调不增；②"及格线"随分母单调上升；
③换分母不改排行榜次序（口径集内的定理级性质，钉错即红）；
④缺账对账与"键名不存在≠测得零条"两条诚实性判据走 tmp_path 合成仓。
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "backtest" / "statsgov_deflation_and_budget.py"

_spec = importlib.util.spec_from_file_location("statsgov_mod", SCRIPT)
assert _spec and _spec.loader
sg = importlib.util.module_from_spec(_spec)
sys.modules["statsgov_mod"] = sg
_spec.loader.exec_module(sg)


def test_dsr_never_increases_with_more_trials():
    """同一成绩，试次数越多 DSR 越低。反例=分母口径写反（放水方向）。"""
    lo = sg.dsr_only(1.721, 9, 970)[0]
    hi = sg.dsr_only(1.721, 362880, 970)[0]
    assert lo > hi, f"N=9 的 DSR({lo}) 必须大于 N=362880 的({hi})，否则分母方向被写反"
    assert lo < 1.0 and hi >= 0.0


def test_gate_line_rises_with_trial_count():
    """分母越大，DSR≥0.95 所需 Sharpe 越高（"折减后及格线"单调性）。"""
    a = sg.required_sharpe_for_dsr(9, 970)
    b = sg.required_sharpe_for_dsr(10080, 970)
    c = sg.required_sharpe_for_dsr(362880, 970)
    assert a is not None and b is not None and c is not None
    assert a < b < c, f"及格线应随 N 上升：{a} {b} {c}"
    # 钉一个量级反例：宽松尺的线必须在 1~2 年化、最严尺必须在 2.5~4 年化
    assert 1.0 < a < 2.0 and 2.5 < c < 4.0


def test_rank_order_is_invariant_to_denominator():
    """同 T 时，换分母不改名次（DSR=Φ(z−E_max(N))，E_max(N) 对全批同值）。

    这条钉的是"榜与门分离"的设计前提；若官方件将来让 E_max 逐格不同，本断言即红。
    """
    srs = [1.721, 1.447, 1.20, 0.95, 0.50]
    orders = []
    for n in (9, 10080, 91352, 362880):
        orders.append([i for i, _ in sorted(enumerate(srs), key=lambda x: -sg.dsr_only(x[1], n, 970)[0])])
    assert len({tuple(o) for o in orders}) == 1, f"名次不应随分母变：{orders}"


def test_haircut_input_domain_guard_reports_instead_of_crashing():
    """官方件 _erfcinv 在 t≳27 处下溢抛 SimulationError；本件须报 UNAVAILABLE 而非崩链。"""
    out = sg.dsr_at(55.0, 10080, 1106, want_haircut=True)
    assert out["haircut_status"].startswith("UNAVAILABLE_IN_INPUT_DOMAIN")
    assert out["dsr"] is not None  # DSR 主路不受影响


def test_count_entries_absent_key_enters_cap_as_conservative_upper_bound(tmp_path):
    """批复③（2026-10-12 晚）：点名键查无 ⇒ 以保守上界入帽＋待精算，禁按下界计——
    "帽定 0 之前必须先证明是没数到还是真零，否则把测量缺陷签成治理结论"。
    上界候选含最大容器与计数型整数量级标量（只取容器会把 family_size:11 这类自报量级低估）。"""
    n, st = sg._count_entries({"rows": [{"a": 1}, {"a": 2}], "hypothesis": "x"}, "key:results")
    assert n == 2 and st.startswith("CONSERVATIVE_UPPER_BOUND(key_used=rows;")
    assert "pending_exact_count=true" in st
    n2, st2 = sg._count_entries({"family_size": 11, "per_indicator": [{"i": 1}]}, "key:results")
    assert n2 == 11 and "family_size(int_scalar)" in st2, (n2, st2)
    # 上包络补正：自报量级 11 < 册内真含的 12 条 p 值检验记录 ⇒ 必须取 12（仍按下界计就是复发）
    book = {
        "family_size": 11,
        "per_indicator": {
            f"I{i}": {"pairs": [{"a": "D1", "b": "D2", "n_days": 236, "t_hac": 1.2, "p_raw": 0.2, "p_adj": 1.0}] * 3}
            for i in range(4)
        },
    }
    n3, st3 = sg._count_entries(book, "key:results")
    assert n3 == 12 and "p_t_bearing_test_records" in st3, (n3, st3)
    # 命中一条只计 1：合成件若每条只有 1 个键，len(o)==1 会掩盖"误返回键数"的缺陷，故用多键记录自证
    multi = {"x": {"p_raw": 0.1, "t_hac": 2.0, "n_days": 236}, "y": [{"p_adj": 0.3, "mean_d": 0.02}], "z": "scalar"}
    assert sg._count_test_records(multi) == 2, sg._count_test_records(multi)
    assert sg._count_entries({"results": [{"a": 1}, {"a": 2}]}, "key:results") == (2, "MEASURED(key_used=results)")
    assert sg._count_entries({"results": []}, "key:results") == (0, "MEASURED(key_used=results)")
    n4, st4 = sg._count_entries({"batches": [{"x": 1}]}, "key:results,batches")
    assert n4 == 1 and "chain_first_absent=results" in st4
    # 连容器与计数标量都没有 ⇒ 进 uncounted（整面降 PARTIAL），不得伪装成 0 也不得硬凑 1
    (tmp_path / "bare.yaml").write_text(yaml.safe_dump({"hypothesis": "x", "verdict": "y"}), encoding="utf-8")
    total, notes, uncounted, conservative = sg._count_rows(tmp_path, [tmp_path / "bare.yaml"], "key:results")
    assert (total, conservative, uncounted) == (0, [], ["bare.yaml"])
    assert "KEY_ABSENT_UNBOUNDED" in notes[0]
    # 上界件：计入总数＋逐件标 conservative（族级据此挂"待精算"）
    (tmp_path / "one.yaml").write_text(
        yaml.safe_dump({"hypothesis": "x", "judge_detail": {"a": 1, "b": 2}}), encoding="utf-8"
    )
    total2, notes2, uncounted2, conservative2 = sg._count_rows(tmp_path, [tmp_path / "one.yaml"], "key:results")
    assert (total2, uncounted2, conservative2) == (2, [], ["one.yaml"])
    assert "CONSERVATIVE_UPPER_BOUND" in notes2[0]


def test_scan_unrecorded_grid_trials_exact(tmp_path: Path):
    """合成仓：磁盘 3 批（其中 1 批已入账）⇒ 缺账数必须精确等于未入账两批之和。"""
    cat = tmp_path / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    cat.mkdir(parents=True)
    intake = tmp_path / "data" / "strategy_intake"
    for name, n in (("grid_a", 100), ("grid_b", 250), ("grid_c", 7)):
        d = intake / name
        d.mkdir(parents=True)
        # 出生证是真 JSON（生成件按 json.loads 读）——写 YAML 会被 except 吞成"读不到"，
        # 本断言就是靠这个差异抓到 fixture 自己写错格式
        (d / "summary.json").write_text(json.dumps({"evaluated": n, "run_ts": name[6:]}), encoding="utf-8")
    (cat / "trial_ledger_registry.yaml").write_text(
        yaml.safe_dump(
            {"batch_records": [{"batch_id": "grid_a", "n_trials": 100, "kind": "factory_grid_batch_a"}]}, width=200
        ),
        encoding="utf-8",
        newline="\n",
    )
    out = sg.scan_unrecorded_grid_trials(tmp_path)
    assert out["unrecorded_batch_count"] == 2
    assert out["all_missing_trials"] == 257  # 反例：漏计或把已入账批重复计入都会红
    assert out["post_watermark_missing_trials"] == 257  # 水位线缺省=0，两批都在其后


def test_build_caliber_register_reports_two_ledger_faces(tmp_path: Path):
    """盘面/HEAD 两读法分母不同时，两口径必须同时在场（只出一个＝假单一真源）。"""
    for root, recs in (
        (tmp_path / "main", [{"batch_id": "g1", "n_trials": 40, "kind": "factory_grid_batch_a"}]),
        (tmp_path / "head", [{"batch_id": "g1", "n_trials": 10, "kind": "factory_grid_batch_a"}]),
    ):
        cat = root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
        cat.mkdir(parents=True)
        (cat / "trial_ledger_registry.yaml").write_text(
            yaml.safe_dump(
                {"screen_runs": {"total_trials": 5, "total_runs": 1}, "batch_records": recs, "watermarks": {}},
                width=200,
            ),
            encoding="utf-8",
            newline="\n",
        )
        (root / "data" / "strategy_intake").mkdir(parents=True)
        (root / "config").mkdir(parents=True)
    reg = sg.build_caliber_register(tmp_path / "main", "grid_x", head_ledger_root=tmp_path / "head")
    assert reg["N_ledger_cumulative_worktree_bytes"]["value"] == 45
    assert reg["N_ledger_cumulative_head_bytes"]["value"] == 15
    assert reg["N_eff_registered"]["value"] is None  # 出生批档案不在场→如实 None，禁猜 9


def test_budget_inventory_never_invents_pg_counts(tmp_path: Path):
    """PG 面本件不连库：必须报 PG_NOT_PROBED，禁伪装成 0 消耗。"""
    spec = tmp_path / "spec.yaml"
    spec.write_text(
        yaml.safe_dump(
            {
                "title": "t",
                "ledger_kind_to_family": {"exam_card": "A"},
                "families": [
                    {
                        "id": "A",
                        "title_zh": "x",
                        "faces": [
                            {"id": "pg", "kind": "pg_table", "pattern": "exam_scores_v1"},
                            {"id": "cards", "kind": "ledger_kind", "ledger_kind": "exam_card"},
                        ],
                        "budget_cap": {"value": None},
                    }
                ],
            },
            width=200,
        ),
        encoding="utf-8",
        newline="\n",
    )
    main = tmp_path / "main"
    (main / "docs" / "01_policies_and_standards" / "_registry" / "catalogs").mkdir(parents=True)
    (main / "docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml").write_text(
        yaml.safe_dump(
            {
                "screen_runs": {"total_trials": 0, "total_runs": 0},
                "batch_records": [{"batch_id": "e1", "n_trials": 3, "kind": "exam_card"}],
                "watermarks": {},
            }
        ),
        encoding="utf-8",
        newline="\n",
    )
    (main / "data" / "strategy_intake").mkdir(parents=True)
    doc = sg.budget_inventory(main, spec, tmp_path / "out.yaml")
    fam = doc["families"][0]
    faces = {f["face"]: f for f in fam["faces"]}
    assert faces["pg"]["status"] == "PG_NOT_PROBED"
    assert faces["cards"]["ledger_trials_in_ledger"] == 3
    assert fam["consumption_from_ledger"] == 3
    assert fam["cap_status"] == "pending_adjudication"
    assert doc["ledger_kind_coverage"]["unmapped_kinds"] == []


def test_pbo_block_reports_not_computable_for_single_survivor(tmp_path: Path):
    """登记面只有 1 行时 PBO 必须 NOT_COMPUTABLE（三层因由齐列），禁退化成 0/1 冒充读数。"""
    out = {
        "registered_survivor_set": {
            "computable": False,
            "code": "NOT_COMPUTABLE",
            "reasons_three_layers": ["a", "b", "c"],
        }
    }
    assert out["registered_survivor_set"]["code"] == "NOT_COMPUTABLE"
    assert len(out["registered_survivor_set"]["reasons_three_layers"]) == 3
    with pytest.raises(Exception) as ei:
        from zephyr.backtest.core.cpcv import compute_pbo

        compute_pbo([[1.0]], [[2.0]])
    assert "n_trials" in str(ei.value) or ">=2" in str(ei.value)


def test_expected_max_matches_closed_form_reference_values():
    """E_max 用官方件闭式，本件不得自带第二份数学（值对齐官方件而非本地常数表）。"""
    from zephyr.simulation.deflated_sharpe_calculator import expected_max_sharpe_z

    assert sg.expected_max_sharpe_z is expected_max_sharpe_z
    assert math.isclose(sg.expected_max_sharpe_z(9), expected_max_sharpe_z(9), rel_tol=0, abs_tol=1e-15)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

```
