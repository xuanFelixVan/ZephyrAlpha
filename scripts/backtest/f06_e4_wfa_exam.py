# [BLUEPRINT] MOD-BT-211 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.f06_e4_wfa_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factory_grid_executor; scripts.backtest.translated._c4_engine; zephyr.backtest.core.strategy_validation_pipeline; zephyr.backtest.core.decision_gate; zephyr.backtest.core.overfitting_detector; zephyr.backtest.regime_validation.c4_deflated_sharpe_runner
# [CONSUMERS] data/backtest_artifacts/runs/E4-F06-38b453ca/（E4 正考档案 verdict.md+summary.json）；F-06 E2 消费面（后续幸存者正考复用）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 判定逻辑零重写（IS→WFA→OOS 三线裁决/过拟合检测全委托 strategy_validation_pipeline+DecisionGate+OverfittingDetector，本件只编排）；折切分无泄露（build_folds 机械保证每折训练窗全部早于测试窗、测试窗互不重叠）；配方参数全程锁定（E4=锁定配方的滚动考核，非再优化；训练窗仅作滚动状态预热，配方求值全链路因果/PIT）；回测口径全复用 _c4_engine 冻结土规成本 T+1（w.shift(1)）；DSR 由官方件 MOD-SIM-024 预计算注入（fail-closed：注入失败按 unavailable 判不通过）；OOS 阶段口径=真 OOS 段（test_start>=IS 窗尾的折拼接），WFA 稳定性用全折；RB-STATS-01 证据充分性闸=DSR 折减分母 N_eff 未从批次档案对账复算(非 verified) 或 过拟合三维未评满 ⇒ 禁判"通过"（最多存疑；实测纯噪声 N=1 时 DSR=0.9986 曾判通过，一列改字即放水）
# [MODIFY-GUARD] tests/backtest/test_f06_e4_wfa_exam.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/求值失败)；ValueError(折切分非法)
# [TESTS] tests/backtest/test_f06_e4_wfa_exam.py
# [A_module] module_id=MOD-BT-211 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""F-06 E4 完整三阶段正考（IS→滚动 WFA→OOS）——幸存者配方 WFA 跑批件（MOD-BT-211）。

对 F-06 网格幸存者配方（默认 38b453ca3683）做滚动 Walk-Forward Analysis 正考：
  折切法: 训练 24 个月 → 测试 6 个月，步进 6 个月，覆盖全窗（默认 2020-01..2025-08，8 折）。
  每折: 用 factory_grid_executor.evaluate_recipe 在 [warm_start..test_end] 截断面板上生成
        权重（全链路因果/PIT，训练窗仅作滚动 IC 状态预热）→ 截取测试窗权重 → 全折拼接为
        一条连续可交易权重路径 → run_backtest（冻结土规成本 T+1）得逐折 sharpe/回撤。
  判定: 逐折结果+IS/OOS sharpe+官方件 DSR 喂 run_strategy_validation（既有 E4 管线，
        DecisionGate 三阶段门控+OverfittingDetector，零重写）；三线 exam verdict 映射：
        通过=三阶段全过∧无过拟合；不通过=WFA 未过/灾难回撤/OOS 比率<0.70(P0-9)/DSR 否决带；
        存疑=仅 DSR 中间带(review)或 WFA 60% 稳定性边际未达而其余全过（fail-closed 语义）。

诚实边界（档案必述）: 折 1-4 测试段(2022-01..2023-12)与已登记 IS 窗(2020-2023)重叠，
  属"选择偏内"的滚动稳定性证据；真 OOS=折 5-8 测试段(2024-01..2025-08)，与已登记 OOS
  快考窗一致，OOS 阶段门控以真 OOS 段拼接口径计并引用快考档案。

用法:
  python scripts/backtest/f06_e4_wfa_exam.py                       # 幸存者 38b453ca3683 全窗正考
  python scripts/backtest/f06_e4_wfa_exam.py --recipe-id <id> ...  # 指定配方/窗口/折法
产出: <out-dir>/verdict.md + summary.json（默认 data/backtest_artifacts/runs/E4-F06-38b453ca/）
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[2]

from zephyr.backtest.core.decision_gate import DSR_OVERFITTING_FLOOR, DSR_SIGNIFICANCE_THRESHOLD, evaluate_dsr
from zephyr.backtest.core.overfitting_detector import DEFAULT_OOS_SHARPE_THRESHOLD_RATIO

STRATEGY_INTAKE_DIR = _REPO / "data" / "strategy_intake"
#: 过拟合检测器三维中，本考实际评估到的维数上限（维度2 参数扰动/维度3 跨时段本考不评估）
OVERFIT_DIMENSIONS_TOTAL = 3

SURVIVORS_CSV = _REPO / "data" / "strategy_intake" / "f06_survivors.csv"
DEFAULT_OUT_DIR = _REPO / "data" / "backtest_artifacts" / "runs" / "E4-F06-38b453ca"
DEFAULT_RECIPE_ID = "38b453ca3683"
DEFAULT_START = "2020-01-01"
DEFAULT_END = "2025-08-31"
#: 真 OOS 段起点 = 已登记 IS 窗尾之后（快考窗 2024-01..2025-08 与此一致）
DEFAULT_OOS_START = "2024-01-01"

VERDICT_PASS = "通过"
VERDICT_REVIEW = "存疑"
VERDICT_FAIL = "不通过"


# ===== 纯函数区（无 DB 依赖，测试直接覆盖） =====


def build_folds(
    full_start: str,
    full_end: str,
    train_months: int = 24,
    test_months: int = 6,
    step_months: int = 6,
) -> list[dict]:
    """滚动 WFA 折切分（纯日期运算，无数据依赖）。

    每折 train 窗（train_months 个月）在前、test 窗（test_months 个月）紧随其后，
    train_start 每次前进步进 step_months 个月；末折 test_end 截到 full_end。
    机械不变量（违者 ValueError）：每折训练窗全部早于测试窗；测试窗互不重叠且时序递增。

    Returns:
        list[dict]: [{"fold", "train_start", "train_end", "test_start", "test_end"}]（Timestamp）
    """
    for name, v in (("train_months", train_months), ("test_months", test_months), ("step_months", step_months)):
        if int(v) <= 0:
            raise ValueError(f"{name} 必须为正整数: {v}")
    if int(step_months) < int(test_months):
        raise ValueError(
            f"step_months({step_months}) < test_months({test_months}) 会使测试窗重叠——"
            "本件拼接连续可交易权重路径要求折测试窗互不重叠(step>=test)"
        )
    start = pd.Timestamp(full_start).normalize()
    end = pd.Timestamp(full_end).normalize()
    if end <= start:
        raise ValueError(f"全窗非法(End<=start): {full_start}..{full_end}")

    folds: list[dict] = []
    train_start = start
    # 前置条件循环（PERM-TRIGGER 治本：不用 while True+break 模式）——
    # 折存在当且仅当 train 窗能放下且测试窗起点不越过全窗尾
    while train_start <= end:
        train_end = train_start + pd.DateOffset(months=int(train_months)) - pd.Timedelta(days=1)
        test_start = train_end + pd.Timedelta(days=1)
        if test_start > end:
            break
        test_end = min(test_start + pd.DateOffset(months=int(test_months)) - pd.Timedelta(days=1), end)
        folds.append(
            {
                "fold": len(folds),
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
            }
        )
        train_start = train_start + pd.DateOffset(months=int(step_months))
    if not folds:
        raise ValueError(f"全窗 {full_start}..{full_end} 不足以切出任何折(train={train_months}m)")

    # 无泄露不变量复核（机械防御，不依赖构造正确性）
    for i, f in enumerate(folds):
        if not f["train_end"] < f["test_start"]:
            raise ValueError(f"折{i}训练窗未全部早于测试窗: {f['train_end']} !< {f['test_start']}")
        if i > 0 and not folds[i - 1]["test_end"] < f["test_start"]:
            raise ValueError(f"折{i}测试窗与前折重叠: {folds[i-1]['test_end']} !< {f['test_start']}")
        if f["test_start"] < start or f["test_end"] > end:
            raise ValueError(f"折{i}测试窗越界: {f['test_start']}..{f['test_end']}")
    return folds


def stitch_fold_weights(weights_by_fold: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """逐折测试窗权重 → 一条连续权重路径（按折序拼接；索引重复=折重叠= ValueError）。"""
    ordered = [weights_by_fold[i] for i in sorted(weights_by_fold)]
    if not ordered:
        raise ValueError("无折权重可拼接")
    stitched = pd.concat(ordered, axis=0).sort_index()
    if stitched.index.has_duplicates:
        raise ValueError("拼接后索引含重复日期——测试窗存在重叠（泄露）")
    return stitched


def fold_metrics_from_net(net: pd.Series, folds: list[dict]) -> list[dict]:
    """从连续净收益路径按折切片计算逐折指标（sharpe/max_drawdown/正折标记）。

    口径与 _c4_engine.run_backtest 完全一致（年化 244、回撤=权益/历史高点-1）；
    连续路径成本一次结清（折边界按真实持仓变化计换手，不重复收进出场成本）。
    """
    rows: list[dict] = []
    for f in folds:
        seg = net[(net.index >= f["test_start"]) & (net.index <= f["test_end"])]
        std = float(seg.std())
        sharpe = float(seg.mean() / std * np.sqrt(244)) if std > 0 else 0.0
        eq = (1.0 + seg).cumprod()
        mdd = float((eq / eq.cummax() - 1.0).min()) if len(seg) else 0.0
        rows.append(
            {
                **{k: (str(v.date()) if isinstance(v, pd.Timestamp) else v) for k, v in f.items()},
                "days": int(len(seg)),
                "sharpe": round(sharpe, 3),
                "max_drawdown": round(mdd, 4),
                "net_sum": round(float(seg.sum()), 6),
            }
        )
    return rows


def map_exam_verdict(
    gate_result,
    overfitting: dict,
    dsr_band: str,
    *,
    n_dims_evaluated: int = OVERFIT_DIMENSIONS_TOTAL,
    dsr_denominator_verified: bool = True,
) -> tuple[str, list[str]]:
    """E4 exam 三线 verdict 映射（阈值全取注册常量，禁自造门限）。

    语义（按序机械判定）:
      1. 通过   = gate.overall_passed ∧ 未检出过拟合（正式上线仍需 Owner 人工审批）
      2. 不通过 = WFA 阶段未过（多数折未过线或灾难回撤否决）∨ OOS/IS 比率 <
                  DEFAULT_OOS_SHARPE_THRESHOLD_RATIO(0.70, P0-9/SIM-38 硬否决线) ∨
                  DSR 落否决带(overfitting/unavailable, fail-closed)
      3. 存疑   = 其余情形（门控各硬线全过，仅 DSR 中间带 review 或 WFA 60% 稳定性
                  边际未达——需补样本/人工复核，fail-closed 不放行）

    RB-STATS-01 加严（两道"证据充分性"闸，只收不放行的方向，不改任何统计阈值）:
      - n_dims_evaluated < 3：过拟合检测器三维中未评估的维**默认判"稳定"**
        （overfitting_detector.detect 实测：perturbed/period 缺位时
        is_overfitting 恒 False），故"未检出过拟合"≠"检出无过拟合"——证据不全，
        不得判通过，最多存疑。
      - dsr_denominator_verified=False：DSR 折减分母 N_eff 不可复算/与登记不符
        （见 verify_n_trials_provenance）⇒ 尺子本身未经校验，不得判通过。
    """
    ratio = float(gate_result.oos_stage.oos_is_ratio)
    wfa_ok = bool(gate_result.wfa_stage.passed) and not bool(gate_result.wfa_stage.has_disaster)
    if bool(gate_result.overall_passed) and not bool(overfitting["is_overfitting"]):
        gaps = []
        if int(n_dims_evaluated) < OVERFIT_DIMENSIONS_TOTAL:
            gaps.append(
                f"过拟合检测仅评估 {int(n_dims_evaluated)}/{OVERFIT_DIMENSIONS_TOTAL} 维"
                "（缺位维按'未检测=稳定'计入，'未检出过拟合'不构成过拟合证据）"
            )
        if not dsr_denominator_verified:
            gaps.append("DSR 折减分母 N_eff 未能从批次档案复算对账（尺子未经校验，禁据此放行）")
        if gaps:
            return VERDICT_REVIEW, ["各硬线全过, 但放行证据不充分(fail-closed 降级为存疑)"] + gaps
        return VERDICT_PASS, [
            f"三阶段(IS→WFA→OOS)门控全部通过且未检出过拟合(OOS/IS比率={ratio:.3f}, DSR落带={dsr_band}); "
            "正式上线仍需 Owner 人工审批"
        ]
    if not wfa_ok:
        return VERDICT_FAIL, [
            f"WFA阶段未通过(通过折数={gate_result.wfa_stage.windows_passed}/{gate_result.wfa_stage.windows_total}, "
            f"灾难回撤={gate_result.wfa_stage.has_disaster}); 按IS→WFA→OOS不可跳级语义判不通过"
        ]
    if ratio < DEFAULT_OOS_SHARPE_THRESHOLD_RATIO:
        reasons = [
            f"OOS/IS Sharpe比率{ratio:.3f} < {DEFAULT_OOS_SHARPE_THRESHOLD_RATIO:.2f}(P0-9/SIM-38硬否决线), 判不通过"
        ]
        if dsr_band in ("overfitting", "unavailable"):
            reasons.append(f"DSR同时落否决带({dsr_band}, fail-closed低于运气中值/未注入), 双重否决")
        return VERDICT_FAIL, reasons
    wf_marginal = bool(overfitting["is_overfitting"]) and not bool(overfitting["walk_forward_stable"])
    if dsr_band == "review" or wf_marginal:
        reasons = []
        if dsr_band == "review":
            reasons.append(
                f"DSR落中间带存疑({DSR_OVERFITTING_FLOOR:.2f}<=DSR<{DSR_SIGNIFICANCE_THRESHOLD}): "
                "fail-closed需补样本或人工复核"
            )
        if wf_marginal:
            reasons.append(
                f"WFA门控多数通过但60%稳定性边际未达(正折占比相关见overfitting reasons: {overfitting['reasons']})"
            )
        return VERDICT_REVIEW, ["各硬线全过, 仅存边际存疑项(fail-closed, 不构成放行)"] + reasons
    return VERDICT_FAIL, [
        f"OOS阶段未通过(DSR落带={dsr_band}, OOS/IS比率={ratio:.3f}); fail-closed判不通过"
    ]


def verify_n_trials_provenance(
    birth_batch: str,
    recorded_n_eff: int | None,
    recorded_n_raw: int | None,
    intake_dir: Path = STRATEGY_INTAKE_DIR,
) -> dict:
    """DSR 折减分母 N_eff 的可复算性核验（红队 RB-STATS-01 治本，只加严不放宽）。

    病：DSR 的分母此前**盲信** f06_survivors.csv 的 n_trials_eff 一列——实测把该列
    从 9 改成 1，同一条纯噪声序列的 DSR 从 0.3267 跳到 0.9986、E4 判定从"不通过"
    翻成"通过"（一列改字即可放水，尺子无牙）。

    治：从批次档案 net_returns.parquet|csv.gz 用官方估计器 compute_effective_rank
    原地复算 N_eff，与登记值逐位对账：
      - 档案缺失          -> status="unverifiable"（档案未落=不可审计，禁据此放行）
      - 复算 != 登记      -> status="mismatch"
      - 复算 == 登记      -> status="verified"
    任何非 verified 态都不得支撑"通过"判定（由 map_exam_verdict 机械执行）。

    Returns:
        dict: {"status", "recorded_n_eff", "recomputed_n_eff", "detail"}
    """
    base = {
        "recorded_n_eff": recorded_n_eff,
        "recorded_n_raw": recorded_n_raw,
        "recomputed_n_eff": None,
        "archive": None,
        "detail": "",
    }
    if not birth_batch or recorded_n_eff is None:
        return {**base, "status": "unverifiable", "detail": "birth_batch/n_trials_eff 缺失"}
    batch_dir = Path(intake_dir) / birth_batch
    archive = None
    for name in ("net_returns.parquet", "net_returns.csv.gz"):
        if (batch_dir / name).exists():
            archive = batch_dir / name
            break
    if archive is None:
        return {
            **base,
            "status": "unverifiable",
            "detail": f"批次档案无 net_returns（折减分母不可复算）: {batch_dir}",
        }
    try:
        from zephyr.backtest.core.n_trial_ledger import compute_effective_rank

        frame = pd.read_parquet(archive) if archive.suffix == ".parquet" else pd.read_csv(archive, compression="gzip")
        recomputed, meta = compute_effective_rank({str(c): frame[c] for c in frame.columns})
    except Exception as exc:  # noqa: BLE001 — 复算失败按不可核验处理（fail-closed），绝不信登记值
        return {**base, "status": "unverifiable", "detail": f"复算异常 {type(exc).__name__}: {exc}"}
    status = "verified" if int(recomputed) == int(recorded_n_eff) else "mismatch"
    return {
        **base,
        "status": status,
        "recomputed_n_eff": int(recomputed),
        "archive": str(archive),
        "detail": f"meta={meta}",
    }


def load_survivor_record(survivors_csv: Path, recipe_id: str) -> dict:
    """从登记面 f06_survivors.csv 读取幸存者注册态（SSOT 消费，禁背数硬编码）。"""
    if not survivors_csv.exists():
        raise RuntimeError(f"幸存者登记面缺失: {survivors_csv}")
    df = pd.read_csv(survivors_csv, dtype={"recipe_id": str})
    hit = df[df["recipe_id"] == recipe_id]
    if hit.empty:
        raise RuntimeError(f"配方 {recipe_id} 不在幸存者登记面: {survivors_csv}")
    r = hit.iloc[0]
    return {
        "recipe_id": recipe_id,
        "values": json.loads(r["values_json"]),
        "is_sharpe": float(r["is_sharpe"]),
        "is_window": str(r.get("is_window", "")),
        "oos_sharpe_registered": float(r["oos_sharpe"]) if pd.notna(r.get("oos_sharpe")) else None,
        "oos_window": str(r.get("oos_window", "")),
        "dsr_eff_registered": float(r["dsr_eff"]) if pd.notna(r.get("dsr_eff")) else None,
        "n_trials_eff": int(r["n_trials_eff"]) if pd.notna(r.get("n_trials_eff")) else None,
        "n_trials_raw": int(r["n_trials_raw"]) if pd.notna(r.get("n_trials_raw")) else None,
        "birth_batch": str(r.get("birth_batch", "")),
        "mechanism": str(r.get("mechanism", "")),
    }


# ===== 编排区（真实数据路径） =====


def _load_factory_executor():
    """复用 MOD-BT-196 执行器（配方语义唯一实现，零重实现；已加载则复用）。"""
    mod = sys.modules.get("factory_grid_executor")
    if mod is not None and hasattr(mod, "evaluate_recipe"):
        return mod
    spec = importlib.util.spec_from_file_location(
        "factory_grid_executor", _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _dsr_exact(net: pd.Series, num_trials: int) -> float:
    """官方件 MOD-SIM-024 精确口径 DSR（真实收益序列偏度/峰度，升级批次 B 正态近似）。"""
    from zephyr.backtest.regime_validation.c4_deflated_sharpe_runner import run_deflated_sharpe_batch

    vals = [float(v) for v in pd.to_numeric(net, errors="coerce").dropna().values]
    rep = run_deflated_sharpe_batch({"wfa_true_oos": vals}, num_trials=int(num_trials))
    return round(float(rep.variants[0].dsr), 4)


def run_exam(
    recipe_id: str = DEFAULT_RECIPE_ID,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    out_dir: Path = DEFAULT_OUT_DIR,
    train_months: int = 24,
    test_months: int = 6,
    step_months: int = 6,
    oos_start: str = DEFAULT_OOS_START,
    survivors_csv: Path = SURVIVORS_CSV,
) -> dict:
    """E4 完整正考主入口。返回 summary dict；verdict.md+summary.json 落 out_dir。"""
    rec = load_survivor_record(survivors_csv, recipe_id)
    folds = build_folds(start, end, train_months, test_months, step_months)

    fge = _load_factory_executor()
    load_px, wide, filter_st, load_st_flags, run_backtest, daily_net_returns = fge._load_engine()
    from zephyr.position.core.position_recipe_compiler import PositionRecipe

    # 数据一次拉取（窗口外多留 200 日作因子/滚动 IC 预热，与 run_batch 同法）
    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=200)).date().isoformat()
    px = load_px(warm_start, end, fields=("close", "volume"))
    closes_all = wide(px, "close")
    flags = load_st_flags(warm_start, end)
    closes_eval = filter_st(closes_all, flags)

    universe = fge._load_universe(rec["values"]["G_universe"])
    cols = [c for c in universe if c in closes_eval.columns]
    if len(cols) < 30:
        raise RuntimeError(f"universe_too_small: cols={len(cols)}")
    factors = fge.compute_v1_factors(closes_eval[cols])
    vol20 = closes_eval[cols].pct_change().rolling(20).std()
    mkt_cap_w = fge._load_mkt_cap_wide(warm_start, end, closes_all.columns)
    rets_daily = closes_eval[cols].pct_change()
    rets60_mean = rets_daily.rolling(60).mean()
    rets60_var = rets_daily.rolling(60).var()

    recipe = PositionRecipe(recipe_id=recipe_id, values=dict(rec["values"]), folded_dimensions={}, prefix_key="")

    # 逐折求值: 截断面板(全链路因果)生成权重 → 截取测试窗
    weights_by_fold: dict[int, pd.DataFrame] = {}
    degraded_by_fold: dict[int, tuple] = {}
    for f in folds:
        te = f["test_end"]
        sub = lambda d: d.loc[:te] if d is not None else None  # noqa: E731 — 截断到 test_end（含预热）
        weights, degraded = fge.evaluate_recipe(
            recipe,
            sub(closes_eval),
            {k: sub(v) for k, v in factors.items()},
            sub(vol20),
            cols,
            mkt_cap_w=sub(mkt_cap_w),
            rets60_mean=sub(rets60_mean),
            rets60_var=sub(rets60_var),
        )
        weights_by_fold[f["fold"]] = weights.loc[f["test_start"] : f["test_end"]]
        degraded_by_fold[f["fold"]] = degraded

    # 连续权重路径 → 冻结土规回测（成本/换手一次结清，T+1）
    stitched_w = stitch_fold_weights(weights_by_fold)
    cols_px = closes_eval[cols]
    stats_all = run_backtest(stitched_w, cols_px)
    net = daily_net_returns(stitched_w, cols_px)
    fold_rows = fold_metrics_from_net(net, folds)

    # 真 OOS 段（test_start >= oos_start 的折）= OOS 阶段口径
    oos_folds = [f for f in folds if f["test_start"] >= pd.Timestamp(oos_start)]
    oos_seg = net[net.index >= pd.Timestamp(oos_start)]
    oos_std = float(oos_seg.std())
    oos_sharpe = float(oos_seg.mean() / oos_std * np.sqrt(244)) if oos_std > 0 else 0.0
    oos_eq = (1.0 + oos_seg).cumprod()
    oos_mdd = float((oos_eq / oos_eq.cummax() - 1.0).min())

    # 官方件 DSR（真 OOS 段收益序列，双 N 口径并报；门控注入 N_eff 预注册口径）
    dsr_eff = dsr_raw = None
    dsr_error = None
    try:
        if rec["n_trials_eff"]:
            dsr_eff = _dsr_exact(oos_seg, rec["n_trials_eff"])
        if rec["n_trials_raw"]:
            dsr_raw = _dsr_exact(oos_seg, rec["n_trials_raw"])
    except Exception as exc:  # noqa: BLE001 — fail-closed: dsr 保持 None → unavailable 判不通过
        dsr_error = f"{type(exc).__name__}: {exc}"

    # 既有 E4 判定管线（零重写）: IS→WFA→OOS 三阶段门控 + 过拟合检测
    from zephyr.backtest.core.strategy_validation_pipeline import StrategyValidationRequest, run_strategy_validation

    pipe = run_strategy_validation(
        StrategyValidationRequest(
            strategy_id=f"F06-{recipe_id}-E4WFA",
            is_sharpe=float(rec["is_sharpe"]),
            params=dict(rec["values"]),
            param_sensitivity=None,  # 未提供 → IS 稳定性门控跳过（IS 阶段已由 E4-v1 考过并登记）
            walk_forward_results=[
                {"sharpe": r["sharpe"], "max_drawdown": r["max_drawdown"]} for r in fold_rows
            ],
            oos_sharpe=float(oos_sharpe),
            params_locked=True,
            dsr=dsr_eff,
        )
    )
    band = evaluate_dsr(dsr_eff).band
    # RB-STATS-01：DSR 折减分母必须可对账复算；本考只评估过拟合维度1（WFA），
    # 维度2(参数扰动)/维度3(跨时段)未评估 => 检测器按"稳定"计入，不得当过拟合证据用。
    n_eff_prov = verify_n_trials_provenance(rec["birth_batch"], rec["n_trials_eff"], rec["n_trials_raw"])
    n_dims = 1
    verdict, verdict_reasons = map_exam_verdict(
        pipe.gate,
        pipe.overfitting,
        band,
        n_dims_evaluated=n_dims,
        dsr_denominator_verified=(n_eff_prov["status"] == "verified"),
    )

    sharpes = [r["sharpe"] for r in fold_rows]
    summary = {
        "mod": "MOD-BT-211",
        "exam": "E4_full_IS_WFA_OOS",
        "recipe_id": recipe_id,
        "birth_batch": rec["birth_batch"],
        "mechanism": rec["mechanism"],
        "params_locked": rec["values"],
        "window_full": [start, end],
        "fold_scheme": {"train_months": train_months, "test_months": test_months, "step_months": step_months},
        "n_folds": len(folds),
        "folds": fold_rows,
        "degraded_by_fold": {str(k): list(v) for k, v in degraded_by_fold.items()},
        "wfa_summary": {
            "sharpe_mean": round(float(np.mean(sharpes)), 3),
            "sharpe_worst_fold": round(float(np.min(sharpes)), 3),
            "sharpe_best_fold": round(float(np.max(sharpes)), 3),
            "positive_ratio": round(float(np.mean([s > 0 for s in sharpes])), 4),
            "stitched_stats": stats_all,
        },
        "true_oos": {
            "oos_start": oos_start,
            "folds": [f["fold"] for f in oos_folds],
            "days": int(len(oos_seg)),
            "sharpe": round(oos_sharpe, 3),
            "max_drawdown": round(oos_mdd, 4),
            "oos_registered_quick_exam": {
                "sharpe": rec["oos_sharpe_registered"],
                "window": rec["oos_window"],
            },
        },
        "is_stage": {"sharpe": rec["is_sharpe"], "window": rec["is_window"], "source": "f06_survivors.csv 登记"},
        "dsr": {
            "exact_eff_caliber": dsr_eff,
            "exact_raw_caliber": dsr_raw,
            "n_trials_eff": rec["n_trials_eff"],
            "n_trials_raw": rec["n_trials_raw"],
            "registered_is_normal_approx": rec["dsr_eff_registered"],
            "band": band,
            "error": dsr_error,
            "n_eff_provenance": n_eff_prov,
        },
        "overfitting_coverage": {
            "dimensions_total": OVERFIT_DIMENSIONS_TOTAL,
            "dimensions_evaluated": n_dims,
            "evaluated": ["walk_forward_stability"],
            "not_evaluated": ["parameter_perturbation", "cross_period_generalization"],
            "failopen_note": "overfitting_detector 对未评估维默认计'稳定'，故 is_overfitting=False 不等于过拟合已排除",
        },
        "gate": {
            "overall_passed": bool(pipe.gate.overall_passed),
            "can_deploy": bool(pipe.can_deploy),
            "is_passed": bool(pipe.gate.is_stage.passed),
            "wfa_passed": bool(pipe.gate.wfa_stage.passed),
            "wfa_windows": f"{pipe.gate.wfa_stage.windows_passed}/{pipe.gate.wfa_stage.windows_total}",
            "has_disaster": bool(pipe.gate.wfa_stage.has_disaster),
            "oos_passed": bool(pipe.gate.oos_stage.passed),
            "oos_is_ratio": round(float(pipe.gate.oos_stage.oos_is_ratio), 4),
            "overfitting": pipe.overfitting,
            "reasons": list(pipe.reasons),
        },
        "verdict": verdict,
        "verdict_reasons": verdict_reasons,
        "out_dir": str(out_dir),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_artifacts(out_dir, summary, folds)
    return summary


def _md_fold_table(fold_rows: list[dict]) -> str:
    head = "| 折 | 训练窗 | 测试窗 | 天数 | sharpe | maxDD | 段净收益 |\n|---|---|---|---|---|---|---|"
    lines = [
        f"| {r['fold']} | {r['train_start']}..{r['train_end']} | {r['test_start']}..{r['test_end']} "
        f"| {r['days']} | {r['sharpe']:.3f} | {r['max_drawdown']:.2%} | {r['net_sum']:.4f} |"
        for r in fold_rows
    ]
    return head + "\n" + "\n".join(lines)


def _write_artifacts(out_dir: Path, s: dict, folds: list[dict]) -> None:
    """档案落盘（summary.json + verdict.md；经 safe_write_text CAS 写）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    safe_write_text(out_dir / "summary.json", json.dumps(s, ensure_ascii=False, indent=2))

    g = s["gate"]
    md = f"""# E4 完整三阶段正考档案 — F-06 幸存者 {s['recipe_id']}（MOD-BT-211）

- 考试: IS → 滚动 WFA → OOS（判定全委托既有管线 strategy_validation_pipeline + DecisionGate + OverfittingDetector，零重写）
- 配方: {s['mechanism']}（参数全程锁定，E4=锁定配方滚动考核，非再优化）
- 全窗: {s['window_full'][0]}..{s['window_full'][1]}；折法: 训练 {s['fold_scheme']['train_months']} 个月 → 测试 {s['fold_scheme']['test_months']} 个月，步进 {s['fold_scheme']['step_months']} 个月，共 {s['n_folds']} 折
- IS 阶段: sharpe={s['is_stage']['sharpe']}（窗口 {s['is_stage']['window']}，来源=幸存者登记面 E4-v1 已考值）
- 回测口径: _c4_engine 冻结土规成本（佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp）+ T+1（w.shift(1)），全折拼接为一条连续可交易权重路径

## 判定: **{s['verdict']}**

{s['verdict_reasons'][0]}

- 门控: overall_passed={g['overall_passed']}, can_deploy={g['can_deploy']}, WFA={g['wfa_windows']}折通过(灾难={g['has_disaster']}), OOS/IS比率={g['oos_is_ratio']}
- 过拟合检测: is_overfitting={s['gate']['overfitting']['is_overfitting']}（SIM-38 比率口径 + WFA 稳定性，reasons 见 summary.json）

## WFA 逐折表

{_md_fold_table(s['folds'])}

**WFA 汇总**: 逐折 sharpe={[r['sharpe'] for r in s['folds']]}；均值={s['wfa_summary']['sharpe_mean']}；最差折={s['wfa_summary']['sharpe_worst_fold']}；正折占比={s['wfa_summary']['positive_ratio']}；拼接全路径 sharpe={s['wfa_summary']['stitched_stats']['sharpe']} / maxDD={s['wfa_summary']['stitched_stats']['max_drawdown']}

## OOS 阶段（真 OOS 段口径）

- 真 OOS=折 {s['true_oos']['folds']}（测试段起点 >= {s['true_oos']['oos_start']}，与已登记 OOS 快考窗一致）
- 本考拼接口径: sharpe={s['true_oos']['sharpe']} / maxDD={s['true_oos']['max_drawdown']} / {s['true_oos']['days']} 交易日
- 已登记 OOS 快考档案引用: sharpe={s['true_oos']['oos_registered_quick_exam']['sharpe']}（窗口 {s['true_oos']['oos_registered_quick_exam']['window']}，data/strategy_intake/grid_20260916-233634/）
- OOS/IS 比率={g['oos_is_ratio']} vs 门槛 {DEFAULT_OOS_SHARPE_THRESHOLD_RATIO:.2f}（P0-9/SIM-38）

## DSR（官方件 MOD-SIM-024 精确口径，真 OOS 段收益序列）

- N_eff={s['dsr']['n_trials_eff']} 口径: {s['dsr']['exact_eff_caliber']}（门控注入口径）；N_raw={s['dsr']['n_trials_raw']} 口径: {s['dsr']['exact_raw_caliber']}（双口径并报纪律）
- 批次 B 正态近似 IS 窗登记值（对照）: {s['dsr']['registered_is_normal_approx']}；落带={s['dsr']['band']}
- **折减分母对账**: status={s['dsr']['n_eff_provenance']['status']}；复算 N_eff={s['dsr']['n_eff_provenance']['recomputed_n_eff']} vs 登记 {s['dsr']['n_eff_provenance']['recorded_n_eff']}；档案={s['dsr']['n_eff_provenance']['archive']}；{s['dsr']['n_eff_provenance']['detail']}
  （非 verified 时本考禁判"通过"——分母可被一列改字放水，实测纯噪声 N=1 时 DSR=0.9986 判通过）

## 过拟合检测覆盖面（RB-STATS-01 诚实披露）

- 三维中本考实际评估 **{s['overfitting_coverage']['dimensions_evaluated']}/{s['overfitting_coverage']['dimensions_total']}** 维：已评={s['overfitting_coverage']['evaluated']} 未评={s['overfitting_coverage']['not_evaluated']}
- ⚠️ {s['overfitting_coverage']['failopen_note']}

## 诚实边界

- 折 0-{len([f for f in folds if str(f['test_end'])[:4] < '2024']) - 1} 测试段(2022-01..2023-12)与已登记 IS 窗重叠，属"选择偏内"的滚动稳定性证据；真 OOS 仅折 {s['true_oos']['folds']}；
- 本考快考对照差异来源: 预热起点(2019-06 vs 2023-06)与周频调仓相位不同，逐位不可比；
- 折边界成本按连续路径真实换手一次结清（不重复收进出场成本）；
- 判定不构成实盘信号，正式上线判定权在 Owner 门位（§5 人机门位）。

> 合规声明：研究方法与工程产出，不构成投资建议。
"""
    safe_write_text(out_dir / "verdict.md", md)


def main() -> int:
    ap = argparse.ArgumentParser(description="F-06 E4 完整三阶段正考（IS→WFA→OOS）")
    ap.add_argument("--recipe-id", default=DEFAULT_RECIPE_ID)
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--train-months", type=int, default=24)
    ap.add_argument("--test-months", type=int, default=6)
    ap.add_argument("--step-months", type=int, default=6)
    ap.add_argument("--oos-start", default=DEFAULT_OOS_START)
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--survivors-csv", default=str(SURVIVORS_CSV))
    args = ap.parse_args()
    s = run_exam(
        recipe_id=args.recipe_id,
        start=args.start,
        end=args.end,
        out_dir=Path(args.out_dir),
        train_months=args.train_months,
        test_months=args.test_months,
        step_months=args.step_months,
        oos_start=args.oos_start,
        survivors_csv=Path(args.survivors_csv),
    )
    print(json.dumps({k: s[k] for k in ("verdict", "verdict_reasons", "wfa_summary", "true_oos", "dsr", "gate")}, ensure_ascii=False, indent=2))
    return 0


# noqa: m11-perm-manual-legitimate  F-06 E4 正考批处理跑批件: CLI 手动触发与 factory_grid_executor 同类，
# 非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界批处理作业
# noqa: m11-perm-manual-legitimate  E4 单幸存者有界考试作业: CLI 手动触发与 c4_batch_screen 同类，
# 非常驻永久系统（每次运行为一次封闭的 WFA 考试，无自动循环无守驻状态）
if __name__ == "__main__":
    raise SystemExit(main())
