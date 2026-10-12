# [BLUEPRINT] MOD-BT-195 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.kronos_adapter
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; torch; model.kronos(官方仓 .runtime/tmp/kronos_repo); zephyr.data.ch_config; scripts.backtest.distribution_forecast_eval; zephyr.data.ch_writer; zephyr.data.table_registry; zephyr.shared.utils.time_utils
# [CONSUMERS] 策略生产全景图 FAC-E1E 车道E 模型基线（Kronos 接入，只当基线对台不当信号）；
#   E4 分布预测双标准考尺（MOD-BT-194）；工单 GPU-02 夜窗打分批 scripts/tasks/run/run_kronos_scoring.ps1
#   （--score-only 腿→c1_market.kronos_prediction_daily 只落不用）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] PIT：预测只用 ≤T 数据（walk-forward 无前视）；样本分位数=逐 horizon 跨
#   sample_count 样本取分位；K 线重复日期 drop_duplicates(keep=last)；权重目录
#   .runtime/tmp/kronos_weights（镜像下载）；本模块只做基线对台，判定权在 E4；
#   --score-only 腿与评估腿零交集（不 import distribution_forecast_eval、不取标签、不算分），
#   落表列序单点=schema INSERT_COLUMNS，落表失败即停非静默；分片宇宙序=SQL_UNIVERSE 成交额降序
#   （切片只按位置，不在本层重排），一夜一片×四夜一轮（统筹 R-3 裁定）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(仓/权重缺失); ValueError(数据不足/分片越界);
#   score-only 退出码：0=本片全成 1=硬败(宇宙空/落表败/零行) 3=本片跑完但有标的失手 4=让路闸掐断(覆盖不全)
# [TESTS] tests/research/backtest/test_kronos_adapter.py; tests/research/backtest/test_kronos_score_only.py
# [A_module] module_id=MOD-BT-195 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 适配器非常驻服务：由车道 E 基线评估事件调用，无常驻循环
"""FAC-E1E 车道E Kronos 接入适配器（MOD-BT-195）——K 线基础模型基线对台。

Kronos（AAAI 2026，shiyu-coder/Kronos）：K 线 token 化+自回归Transformer，逐样本生成
未来 OHLCV 路径。本适配器：
  1 CH kline → Kronos 输入（OHLCV+amount，去重日期）；
  2 样本路径生成（sample_count 条）→ 逐 horizon 分位数 = 分布预测；
  3 walk-forward 回放（无前视：每个测试日只喂 ≤T 数据）→ MOD-BT-194 双标准考尺评分；
  4 无信息基准对照（随机游走 ± 滚动 std 分位）——Kronos 必须跑赢它才算"有信息"。
Kronos 代码仓=.runtime/tmp/kronos_repo（VPN 克隆）；权重=.runtime/tmp/kronos_weights
（hf-mirror 下载：Tokenizer-base 15.8MB + small 99MB，GPU/CPU 双支持）。

用法:
  python scripts/backtest/kronos_adapter.py eval --symbol 600519.SH --n-test 20
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
KRONOS_REPO = _ROOT / "vendor" / "Kronos"
WEIGHTS_DIR = _ROOT / "vendor" / "kronos_weights"
QUANTILES = (0.05, 0.25, 0.5, 0.75, 0.95)


def _load_kronos_classes():
    """官方仓 model.kronos 导入（代码缺失 fail-closed 带指引）。"""
    # 检查真实模块文件而非仅目录（2026-09-16 事故：目录在但 .py 被批删，
    # 目录存在性检查假绿→import 期 ModuleNotFoundError）
    _kronos_mod = KRONOS_REPO / "model" / "kronos.py"
    if not _kronos_mod.exists():
        raise RuntimeError(
            f"Kronos 官方代码缺失: {_kronos_mod}"
            f"（恢复：git -C {KRONOS_REPO} checkout -- . ；"
            "或 VPN 开启后 git clone --depth 1 "
            "https://github.com/shiyu-coder/Kronos 到该目录）"
        )
    return None


SQL_KLINE_ONE = (
    "SELECT trade_date, open, high, low, close, volume, amount "
    "FROM {t} WHERE symbol_canonical = %(sym)s AND trade_date >= %(start)s "
    "ORDER BY trade_date"
)


def _make_cli():
    """CH 只读客户端（独立函数=测试可注入）。"""
    from clickhouse_driver import Client

    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    return Client(
        host=cfg["host"],
        port=int(cfg.get("port", 9000)),
        user=cfg.get("user", "default"),
        password=cfg.get("password", ""),
        connect_timeout=5,
    )


def fetch_kline(symbol: str, days: int) -> pd.DataFrame:
    """单标的 K 线长表（CH 后复权；重复日期 keep=last；数值化）。"""
    from zephyr.data.table_registry import get_registry

    cli = _make_cli()
    start = (date.today() - timedelta(days=int(days * 1.7))).isoformat()
    rows = cli.execute(
        SQL_KLINE_ONE.format(t=get_registry().table("market_kline_daily_hfq")), {"sym": symbol, "start": start}
    )
    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume", "amount"])
    for c in ("open", "high", "low", "close", "volume", "amount"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().drop_duplicates(["date"], keep="last").reset_index(drop=True)
    if len(df) < 60:
        raise ValueError(f"K 线数据不足: {symbol} {len(df)} 行")
    return df


def load_predictor(device: str = "auto", model_size: str = "small"):
    """加载 Tokenizer+模型+Predictor（权重缺失 fail-closed 带下载指引）。"""
    import torch  # noqa: F401  历史导入契约保留（调用方依赖 torch 已就绪态）

    return _load_model(model_size=model_size, device=device)


def _resolve_weight_dirs(model_size: str) -> tuple[Path, Path]:
    """档位 → (tokenizer 目录, predictor 目录)。

    daily_ft=微调成对档（tokenizer+predictor 同源自微调，token 空间自洽——
    2026-09-16 审计治本：predictor 训练时用的是微调 tokenizer
    （train_predictor.py 加载 finetuned_tokenizer_path），推理若配 base
    tokenizer 则 token 语义错位、微调收益被稀释）；small/mini=官方预训练底座。
    """
    if model_size == "daily_ft":
        return (WEIGHTS_DIR / "kronos_tokenizer_daily_ft", WEIGHTS_DIR / "kronos_daily_ft")
    return (
        WEIGHTS_DIR / ("kronos_tokenizer_base" if model_size != "mini" else "kronos_tokenizer_mini"),
        WEIGHTS_DIR / f"kronos_{model_size}",
    )


def _load_model(model_size: str = "small", device: str = "auto"):
    """加载 Kronos predictor（档位缺失 fail-closed 带指引）。"""
    import torch

    _load_kronos_classes()
    sys.path.insert(0, str(KRONOS_REPO))
    from model.kronos import Kronos, KronosPredictor, KronosTokenizer

    tok_dir, model_dir = _resolve_weight_dirs(model_size)
    for d in (tok_dir, model_dir):
        if not d.exists():
            raise RuntimeError(f"权重缺失: {d}（curl -L https://hf-mirror.com/NeoQuasar/... 到该目录）")
    tokenizer = KronosTokenizer.from_pretrained(str(tok_dir))
    model = Kronos.from_pretrained(str(model_dir))
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
    return predictor, device


def _sample_quantiles(samples: np.ndarray, quantiles: tuple) -> dict:
    """样本路径→逐 horizon 分位（samples 形状 (sample_count, pred_len)）。"""
    qs = np.quantile(samples, quantiles, axis=0)
    return {float(q): qs[i] for i, q in enumerate(quantiles)}


def predict_close_quantiles(
    predictor,
    kdf: pd.DataFrame,
    pred_len: int = 1,
    sample_count: int = 16,
    temperature: float = 1.0,
    top_p: float = 0.9,
) -> dict:
    """对 kdf 次日（pred_len 天）生成收盘价分位预测。

    实现：走 KronosPredictor.predict 的样本维（sample_count>1 时 predict 返回 3D，
    故绕开 DataFrame 封装直接取 (sample_count, pred_len) 的 close 列）。
    """
    import torch  # noqa: F401 — predictor 内部用

    ctx = kdf.copy()
    x_index = pd.Series(pd.to_datetime(ctx["date"]))
    y_index = pd.Series(pd.to_datetime(ctx["date"]).iloc[-1] + pd.tseries.offsets.BDay(1) * np.arange(1, pred_len + 1))
    # 样本保留版预测：preds 形状 (sample_count, pred_len)（close 通道）
    samples = _generate_with_stamps(predictor, ctx, y_index, pred_len, sample_count, temperature, top_p)
    return _sample_quantiles(samples, QUANTILES), y_index


def _generate_with_stamps(
    predictor, ctx: pd.DataFrame, y_index: pd.Index, pred_len: int, sample_count: int, temperature: float, top_p: float
) -> np.ndarray:
    """predict() 的样本保留版：归一化→时间戳编码→generate→反归一化。"""
    from model.kronos import calc_time_stamps

    cols = ["open", "high", "low", "close", "volume", "amount"]
    x = ctx[cols].values.astype(np.float32)
    x_stamp = calc_time_stamps(pd.Series(pd.to_datetime(ctx["date"]))).values.astype(np.float32)
    y_stamp = calc_time_stamps(pd.Series(pd.to_datetime(y_index))).values.astype(np.float32)
    x_mean, x_std = x.mean(axis=0), x.std(axis=0)
    xn = np.clip((x - x_mean) / (x_std + 1e-5), -5, 5)

    # 官方实现内部对 sample 维取均值（拿不到样本）——分布预测改为
    # sample_count 次单样本调用（每次一条完整路径），跨路径取分位=真分布。
    paths = []
    for _ in range(int(sample_count)):
        preds = predictor.generate(
            xn[np.newaxis, :],
            x_stamp[np.newaxis, :],
            y_stamp[np.newaxis, :],
            pred_len,
            T=temperature,
            top_k=0,
            top_p=top_p,
            sample_count=1,
            verbose=False,
        )
        paths.append(preds.squeeze(0) * (x_std + 1e-5) + x_mean)
    return np.stack(paths)[:, :, 3]  # (sample_count, pred_len) close 通道


def naive_quantiles(kdf: pd.DataFrame, dates: list, quantiles: tuple, window: int = 20) -> dict:
    """无信息基准：随机游走——pred=上日收盘 ± 滚动 std 的正态分位。"""
    close = kdf.set_index("date")["close"]
    out = {float(q): [] for q in quantiles}
    from scipy.stats import norm

    for d in dates:
        hist = close[close.index < d]
        last = hist.iloc[-1]
        sd = hist.iloc[-window:].diff().std()
        for q in quantiles:
            out[float(q)].append(last + norm.ppf(q) * (sd or 0.0))
    return out


def walk_forward_eval(
    predictor, kdf: pd.DataFrame, n_test: int = 20, sample_count: int = 16, quantiles: tuple = QUANTILES
) -> dict:
    """Walk-forward 分布预测回放（无前视）→ 194 考尺输入（Kronos vs 随机游走基准）。"""
    kdf = kdf.sort_values("date").reset_index(drop=True)
    test_dates = kdf["date"].iloc[-n_test:].tolist()
    krono = {float(q): [] for q in quantiles}
    naive = {float(q): [] for q in quantiles}
    realized = []
    for d in test_dates:
        pos = kdf.index[kdf["date"] == d][0]
        ctx = kdf.iloc[:pos]
        q_k, _ = predict_close_quantiles(predictor, ctx, pred_len=1, sample_count=sample_count)
        q_n = naive_quantiles(kdf, [d], quantiles)
        for q in quantiles:
            krono[float(q)].append(q_k[float(q)][0])
            naive[float(q)].append(q_n[float(q)][0])
        realized.append(float(kdf.loc[pos, "close"]))
    realized = np.asarray(realized)
    return {
        "n_test": n_test,
        "sample_count": sample_count,
        "kronos": krono,
        "naive": naive,
        "realized": realized,
        "dates": [str(d) for d in test_dates],
    }


def eval_multi(symbols: list[str], n_test: int, sample_count: int, days: int, model_size: str = "small") -> dict:
    """多票 walk-forward 评估（模型单次加载跨票复用）。"""
    predictor, device = load_predictor(model_size=model_size)
    per_symbol = []
    for sym in symbols:
        try:
            kdf = fetch_kline(sym, days)
            result = walk_forward_eval(predictor, kdf, n_test=n_test, sample_count=sample_count)
            from scripts.backtest.distribution_forecast_eval import (
                evaluate_distribution_forecast,
            )

            krono = evaluate_distribution_forecast(result["kronos"], result["realized"])
            naive = evaluate_distribution_forecast(result["naive"], result["realized"])
            per_symbol.append(
                {
                    "symbol": sym,
                    "n_test": result["n_test"],
                    "kronos": krono,
                    "naive_rw": naive,
                    "kronos_beats_naive_sharpness": krono["sharpness"] < naive["sharpness"],
                }
            )
            print(
                f"[{sym}] kronos sharp={krono['sharpness']:.2f} "
                f"cal={krono['calibrated_share']:.2f} | naive "
                f"sharp={naive['sharpness']:.2f} cal={naive['calibrated_share']:.2f}"
            )
        except Exception as exc:  # noqa: BLE001 — 单票失败不拖全局
            per_symbol.append({"symbol": sym, "error": str(exc)[:120]})
            print(f"[{sym}] FAIL: {exc}")
    return {"device": device, "per_symbol": per_symbol, "aggregate": aggregate_symbol_reports(per_symbol)}


def aggregate_symbol_reports(per_symbol: list[dict]) -> dict:
    """多票聚合计分板（纯函数）：中位数对比+胜场统计（锐度更紧=胜）。"""
    valid = [r for r in per_symbol if "error" not in r]
    wins = sum(1 for r in valid if r["kronos"]["sharpness"] < r["naive_rw"]["sharpness"])
    cal_wins = sum(1 for r in valid if r["kronos"]["calibrated_share"] >= r["naive_rw"]["calibrated_share"])

    def _med(key_path: str) -> float:
        vals = []
        for r in valid:
            v = r
            for k in key_path.split("."):
                v = v[k]
            if v is not None:
                vals.append(float(v))
        return round(float(np.median(vals)), 4) if vals else float("nan")

    return {
        "symbols_total": len(per_symbol),
        "symbols_ok": len(valid),
        "symbols_error": len(per_symbol) - len(valid),
        "kronos_sharp_wins": wins,
        "kronos_cal_wins": cal_wins,
        "win_rate_sharpness": round(wins / len(valid), 4) if valid else None,
        "median_kronos_calibrated_share": _med("kronos.calibrated_share"),
        "median_naive_calibrated_share": _med("naive_rw.calibrated_share"),
        "median_kronos_sharpness": _med("kronos.sharpness"),
        "median_naive_sharpness": _med("naive_rw.sharpness"),
        "median_kronos_pit_ks": _med("kronos.pit_ks"),
        "median_naive_pit_ks": _med("naive_rw.pit_ks"),
    }


def prepare_multi_symbol(symbols: list[str], days: int, min_history: int = 260) -> dict[str, pd.DataFrame]:
    """多标的公共日期面板：日期取交集（Kronos 批量要求同长上下文）；弱票容错跳过。"""
    dfs = {}
    skipped = []
    for s in symbols:
        try:
            dfs[s] = fetch_kline(s, days)
        except (RuntimeError, ValueError) as exc:
            skipped.append(f"{s}: {exc}")
    if skipped:
        print(f"SKIP {len(skipped)} 只数据不足: {'; '.join(skipped)[:200]}")
    common = None
    for df in dfs.values():
        s = set(pd.to_datetime(df["date"]).dt.date)
        common = s if common is None else (common & s)
    common = set(common)
    out = {}
    for s, df in dfs.items():
        d = df.copy()
        d["date"] = pd.to_datetime(d["date"]).dt.date
        d = d[d["date"].isin(common)].sort_values("date").reset_index(drop=True)
        if len(d) >= min_history:
            out[s] = d
    if len(out) < max(3, len(symbols) // 2):
        raise RuntimeError(f"公共日期面板标的不足: {len(out)}/{len(symbols)}；跳过明细见上方 SKIP")
    return out


def walk_forward_multi_batch(
    predictor, panels: dict[str, pd.DataFrame], n_test: int, sample_count: int, quantiles: tuple = QUANTILES
) -> dict:
    """多标的批量 walk-forward（无前视）：每个测试日一次批量 generate×sample_count。

    返回 {sym: {q: [逐日分位]}, realized: {sym: [逐日收盘]}, naive: {sym: {q: [...]}}}。
    """
    from model.kronos import calc_time_stamps

    syms = sorted(panels)
    b = len(syms)
    base = panels[syms[0]]
    dates = list(base["date"])
    n = len(dates)
    test_start = n - n_test
    cols = ["open", "high", "low", "close", "volume", "amount"]
    x = {s: panels[s][cols].values.astype(np.float32) for s in syms}
    mean = {s: x[s].mean(axis=0) for s in syms}
    std = {s: x[s].std(axis=0) for s in syms}
    close_sd = {s: float(std[s][3]) for s in syms}
    close_mean = {s: float(mean[s][3]) for s in syms}

    realized = {s: [] for s in syms}
    close_samples = {s: {ti: [] for ti in range(n_test)} for s in syms}
    naive_pool = {float(q): [] for q in quantiles}

    for ti, day_i in enumerate(range(test_start, n)):
        d = dates[day_i]
        batch = np.stack([np.clip((x[s][:day_i] - mean[s]) / (std[s] + 1e-5), -5, 5) for s in syms])
        x_stamp = calc_time_stamps(pd.Series(pd.to_datetime(dates[:day_i]))).values.astype(np.float32)
        y_stamp = calc_time_stamps(pd.Series(pd.to_datetime([d] * b))).values.astype(np.float32)
        for _ in range(int(sample_count)):
            preds = predictor.generate(
                batch,
                x_stamp[np.newaxis],
                y_stamp[np.newaxis],
                1,
                T=1.0,
                top_k=0,
                top_p=0.9,
                sample_count=1,
                verbose=False,
            )
            p = np.asarray(preds, dtype=float)
            if p.ndim == 3:
                p = p[:, 0, :]
            close_ch = p[:, 3] * np.array([close_sd[s] + 1e-5 for s in syms]) + np.array([close_mean[s] for s in syms])
            for j, s in enumerate(syms):
                close_samples[s][ti].append(float(close_ch[j]))

    naive_fn = naive_quantiles
    out = {"symbols": syms, "n_test": n_test, "sample_count": int(sample_count), "per_symbol": {}}
    from scipy.stats import norm

    for j, s in enumerate(syms):
        qp = {float(q): [] for q in quantiles}
        naive_q = {float(q): [] for q in quantiles}
        real = []
        for ti, day_i in enumerate(range(test_start, n)):
            samp = np.asarray(close_samples[s][ti], dtype=float)
            for q in quantiles:
                qp[float(q)].append(float(np.quantile(samp, q)))
            d = dates[day_i]
            hist = panels[s].set_index("date")["close"]
            hist = hist[hist.index < d]
            last, sd_hist = hist.iloc[-1], hist.iloc[-20:].diff().std()
            nd = norm.ppf
            for q in quantiles:
                naive_q[float(q)].append(last + nd(q) * (sd_hist or 0.0))
            real.append(float(panels[s].set_index("date")["close"].loc[d]))
        for q in quantiles:
            qp[float(q)] = np.asarray(qp[float(q)])
            naive_q[float(q)] = np.asarray(naive_q[float(q)])
        out["per_symbol"][s] = {"q_preds": qp, "naive_q": naive_q, "realized": np.asarray(real)}
        for q in quantiles:
            naive_pool[float(q)] += list(naive_q[float(q)])
    out["naive_pool"] = {q: np.asarray(v) for q, v in naive_pool.items()}
    return out


# ── 工单 GPU-02 缺件①：--score-only 前瞻打分腿 ─────────────────────────────────
# 与上方 walk-forward 评估腿零交集：本腿不取标签、不算分数、不 import
# distribution_forecast_eval，只把 T+1 收盘价的 5 分位分布写进
# c1_market.kronos_prediction_daily（只落不用；消费转正另走 B-007 人工门）。
# 列序真源=schemas/categories/market/market_kronos_prediction_daily.py 的 INSERT_COLUMNS。
SCORE_COLUMNS = (
    "run_id",
    "symbol",
    "asof_ts",
    "input_cutoff_ts",
    "as_of_date",
    "horizon",
    "pred_len",
    "target_field",
    "q005",
    "q025",
    "q050",
    "q075",
    "q095",
    "point_estimate",
    "interval_width",
    "context_len",
    "sample_count",
    "temperature",
    "top_p",
    "model_size",
    "data_source",
    "inputs_ref",
    "synthetic",
)

_CH_TZ = "Asia/Shanghai"


def _pick_last_window(kdf: pd.DataFrame, max_context: int = 400) -> pd.DataFrame:
    """取尾部上下文（Kronos 批量要求同长；截尾不影响 PIT——只用 ≤T 数据）。"""
    return kdf.iloc[-int(max_context) :].reset_index(drop=True)


def score_forward(
    predictor,
    kdf: pd.DataFrame,
    *,
    pred_len: int = 1,
    sample_count: int = 8,
    temperature: float = 1.0,
    top_p: float = 0.9,
) -> tuple[dict, pd.Series]:
    """单标的 T+pred_len 分位预测（复用既有样本路径腿，零新模型代码）。"""
    return predict_close_quantiles(
        predictor, kdf, pred_len=pred_len, sample_count=sample_count, temperature=temperature, top_p=top_p
    )


def build_prediction_row(
    *,
    symbol: str,
    quantiles: dict,
    kdf: pd.DataFrame,
    run_id: str,
    asof_ts,
    model_size: str,
    pred_len: int,
    sample_count: int,
    temperature: float,
    top_p: float,
    data_source: str,
    synthetic: int = 0,
) -> tuple:
    """一行前瞻预测（列序=SCORE_COLUMNS）。PIT 三时刻全在这里算，别处不拼。"""
    from datetime import timezone

    import pandas as _pd

    last_bar = _pd.to_datetime(kdf["date"].iloc[-1])
    # kline 日历日按 A 股收盘语义落上海时区；无 tz 的 bar 时间戳显式 localize
    cutoff_local = last_bar.tz_localize(_CH_TZ) if last_bar.tzinfo is None else last_bar.tz_convert(_CH_TZ)
    cutoff_utc = cutoff_local.astimezone(timezone.utc)
    as_of_local = _pd.Timestamp(year=last_bar.year, month=last_bar.month, day=last_bar.day).tz_localize(_CH_TZ)
    q = {float(k): v for k, v in quantiles.items()}
    q005, q025, q050, q075, q095 = (float(q[float(x)][0]) for x in QUANTILES)
    inputs_ref = f"rows={len(kdf)};last={last_bar.date().isoformat()};close={float(kdf['close'].iloc[-1]):.4f}"
    return (
        run_id,
        symbol,
        asof_ts,
        cutoff_utc.to_pydatetime(),
        as_of_local.to_pydatetime(),
        f"T+{pred_len}",
        int(pred_len),
        "close",
        q005,
        q025,
        q050,
        q075,
        q095,
        q050,
        q095 - q005,
        int(len(kdf)),
        int(sample_count),
        float(temperature),
        float(top_p),
        model_size,
        data_source,
        inputs_ref,
        int(synthetic),
    )


def write_kronos_predictions(rows: list[tuple], *, table: str | None = None) -> bool:
    """落表正门（ch_writer：列过滤/MATERIALIZED 排除/本地落盘兜底内建，禁裸 SQL）。"""
    from zephyr.data import ch_writer
    from zephyr.data.provider_base import FetchResult
    from zephyr.data.table_registry import get_registry

    if not rows:
        return True
    target = table or get_registry().table("market_kronos_prediction_daily")
    res = FetchResult(
        table=target,
        columns=list(SCORE_COLUMNS),
        rows=list(rows),
        last_key=str(rows[-1][0]),
        elapsed_sec=0.0,
        rows_fetched=len(rows),
    )
    return bool(ch_writer.write_result(res))


def resolve_score_universe(args) -> list[str]:
    """打分宇宙：显式 --symbols 优先，否则按成交额 top N 自动选（沿用评估腿同一 SQL_UNIVERSE）。"""
    if args.symbols:
        return [s.strip() for s in args.symbols.split(",") if s.strip()]
    from scripts.backtest.lane_c_formula_miner import SQL_UNIVERSE
    from zephyr.data.table_registry import get_registry

    start = (date.today() - timedelta(days=int(args.days * 1.7))).isoformat()
    return [
        r[0]
        for r in _make_cli().execute(
            SQL_UNIVERSE.format(kline=get_registry().table("market_kline_daily_hfq")), {"start": start, "n": args.top_n}
        )
    ]


def shard_universe(universe: list[str], *, shard_index: int, shard_count: int) -> list[str]:
    """把宇宙切成 shard_count 片、取第 shard_index 片（ceil 分片，末片可短）。

    宇宙序=SQL_UNIVERSE 的成交额降序，切片只按位置不重排——重排=同一夜换宇宙口径，
    跨夜可比性就没了（分片只扩覆盖面积，不改每只票的算法输入）。
    """
    if shard_count <= 1:
        return list(universe)
    if not 0 <= shard_index < shard_count:
        raise ValueError(f"shard_index={shard_index} 越界（shard_count={shard_count}，须 0≤idx<count）")
    size = -(-len(universe) // shard_count)
    return universe[shard_index * size : (shard_index + 1) * size]


def run_score_only(args) -> int:
    """前瞻打分主循环：宇宙→分片→逐标的（≤T 数据）→分位→攒批落表→打印统计。

    失败面纪律：单标的取数/打分失败计入 failed 明细并继续（夜窗不能被一只票卡死）；
    但**落表失败即停**（静默丢行比不跑更坏，与 LaneC 10-08 那条 all-green 空转同族）。
    分片口径（统筹 R-3）：一片一夜，未跑完/有失手一律非 0 退出——"明天接着跑"不能
    被记账成"今天跑完了"。
    """
    from datetime import timezone

    from zephyr.data.table_registry import get_registry
    from zephyr.shared.utils.time_utils import now_utc

    asof_ts = now_utc().astimezone(timezone.utc).replace(microsecond=0)
    run_id = args.run_id or f"kronos-score-{asof_ts.strftime('%Y%m%d-%H%M%S')}"
    full_universe = resolve_score_universe(args)
    if not full_universe:
        print("FAIL: 打分宇宙为空（--symbols 或 --top-n 至少给一个）", file=sys.stderr)
        return 1
    shard_index = int(getattr(args, "shard_index", 0) or 0)
    shard_count = max(1, int(getattr(args, "shard_count", 1) or 1))
    try:
        universe = shard_universe(full_universe, shard_index=shard_index, shard_count=shard_count)
    except ValueError as exc:
        print(f"FAIL: 分片参数非法: {exc}", file=sys.stderr)
        return 1
    if not universe:
        print(
            f"FAIL: 第 {shard_index}/{shard_count} 片为空（宇宙仅 {len(full_universe)} 只，分片过细）", file=sys.stderr
        )
        return 1
    kline_table = get_registry().table("market_kline_daily_hfq")
    predictor, device = load_predictor(model_size=args.model_size)

    rows: list[tuple] = []
    failed: list[str] = []
    written = 0
    # 让路闸：01:00-04:00 是 CH 让路窗（窗内零跑批零查询）。夜窗 00:30 起跑若不设上限
    # 必伸进该窗，故这里按分钟硬停——到点就收尾落表并如实报"本夜未跑完"，绝不静默续跑。
    max_runtime_min = int(getattr(args, "max_runtime_min", 0) or 0)
    deadline = asof_ts + timedelta(minutes=max_runtime_min) if max_runtime_min else None
    truncated = False
    for i, sym in enumerate(universe, start=1):
        if deadline is not None and now_utc() >= deadline:
            truncated = True
            break
        try:
            kdf = _pick_last_window(fetch_kline(sym, args.days), args.max_context)
            quantiles, _y = score_forward(
                predictor,
                kdf,
                pred_len=args.pred_len,
                sample_count=args.sample_count,
                temperature=args.temperature,
                top_p=args.top_p,
            )
            rows.append(
                build_prediction_row(
                    symbol=sym,
                    quantiles=quantiles,
                    kdf=kdf,
                    run_id=run_id,
                    asof_ts=asof_ts,
                    model_size=args.model_size,
                    pred_len=args.pred_len,
                    sample_count=args.sample_count,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    data_source=kline_table,
                    synthetic=1 if args.synthetic else 0,
                )
            )
        except (RuntimeError, ValueError) as exc:
            failed.append(f"{sym}: {str(exc)[:80]}")
            continue
        if len(rows) >= args.flush_every:
            if not write_kronos_predictions(rows):
                print(f"FAIL: 落表失败（已攒 {len(rows)} 行，宇宙停在第 {i} 只）", file=sys.stderr)
                return 1
            written += len(rows)
            rows = []
    if rows:
        if not write_kronos_predictions(rows):
            print(f"FAIL: 收尾落表失败（末批 {len(rows)} 行）", file=sys.stderr)
            return 1
        written += len(rows)
    # 首夜标定（R-3）：本片实测吞吐＋"上限内还能装几只"——分片粒度合不合适只能由实测说，
    # 不能由拍脑袋的 shard_count 说。零成本字段，不入表、不外发。
    elapsed_min = (now_utc() - asof_ts).total_seconds() / 60.0
    sec_per_symbol = (elapsed_min * 60.0 / written) if written else 0.0
    processed = written + len(failed)
    status = "truncated" if truncated else ("partial_failed" if failed else "complete")
    print(
        json.dumps(
            {
                "mode": "score_only",
                "run_id": run_id,
                "asof_ts": asof_ts.isoformat(),
                "device": device,
                "model_size": args.model_size,
                "universe_total": len(full_universe),
                "shard_index": shard_index,
                "shard_count": shard_count,
                "shard_size": len(universe),
                "shard_status": status,
                "scored": written,
                "unscored": len(universe) - processed,
                "yield_window_hit": truncated,
                "max_runtime_min": max_runtime_min,
                "failed": len(failed),
                "failed_detail": failed[:20],
                "calibration": {
                    "elapsed_min": round(elapsed_min, 2),
                    "sec_per_symbol": round(sec_per_symbol, 2),
                    "symbols_fit_in_cap": int(max_runtime_min * 60.0 / sec_per_symbol)
                    if sec_per_symbol > 0 and max_runtime_min
                    else None,
                },
                "sample_count": args.sample_count,
                "pred_len": args.pred_len,
                "max_context": args.max_context,
                "table": get_registry().table("market_kronos_prediction_daily"),
                "consumption": "只落不用（消费转正走 B-007）",
            },
            ensure_ascii=False,
            indent=1,
            default=str,
        )
    )
    if written == 0:
        return 1
    if truncated:
        return 4
    if failed:
        return 3
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1E Kronos 基线适配器（walk-forward 双标准评分）")
    ap.add_argument("--symbol", default=None, help="单标的模式")
    ap.add_argument("--symbols", default=None, help="逗号分隔多标的（窗口模式）")
    ap.add_argument("--top-n", type=int, default=None, help="成交额 top N 自动选票")
    ap.add_argument("--n-test", type=int, default=60)
    ap.add_argument("--sample-count", type=int, default=8)
    ap.add_argument("--days", type=int, default=250)
    ap.add_argument("--model-size", default="small", help="small=官方底座 | daily_ft=微调成对档（tok+pred 同源自洽）")
    # 工单 GPU-02 缺件①：前瞻打分模式（不评估、不取标签、只落表）
    ap.add_argument(
        "--score-only",
        action="store_true",
        help="全宇宙 T+1 分位前瞻打分并落 Kronos 预测日表（表名经 TableRegistry 解析；只落不用）",
    )
    ap.add_argument("--pred-len", type=int, default=1, help="score-only 预测步长（交易日）")
    ap.add_argument("--max-context", type=int, default=400, help="score-only 尾部上下文 bar 数")
    ap.add_argument("--temperature", type=float, default=1.0, help="score-only 采样温度")
    ap.add_argument("--top-p", type=float, default=0.9, help="score-only nucleus 阈值")
    ap.add_argument("--flush-every", type=int, default=200, help="score-only 攒批落表行数")
    ap.add_argument(
        "--max-runtime-min",
        type=int,
        default=0,
        help="score-only 运行上限分钟（0=不限；夜窗建议 50 以在 01:00 CH 让路窗前收住）",
    )
    # 工单 GPU-02 续令（统筹 R-3 裁定）：00:30 一夜一片×四夜一轮，替代"一夜扫全宇宙"的不可能算术
    ap.add_argument("--shard-index", type=int, default=0, help="score-only 本片序号（0≤idx<shard-count）")
    ap.add_argument("--shard-count", type=int, default=1, help="score-only 宇宙切片总数（1=不分片；R-3 口径=4）")
    ap.add_argument("--run-id", default=None, help="score-only 批次血缘 id（缺省按 asof_ts 生成）")
    ap.add_argument("--synthetic", action="store_true", help="score-only 落 synthetic=1 冒烟行")
    args = ap.parse_args()
    if args.score_only:
        # 早退在评估腿 import 之前：--score-only 全程不触碰 distribution_forecast_eval
        return run_score_only(args)
    try:
        from scripts.backtest.distribution_forecast_eval import (
            evaluate_distribution_forecast,
        )

        multi = args.symbols or args.top_n
        if multi:
            if not args.symbols:
                import datetime as _dt

                from scripts.backtest.kronos_adapter import _make_cli
                from scripts.backtest.lane_c_formula_miner import SQL_UNIVERSE

                start = (date.today() - timedelta(days=int(args.days * 1.7))).isoformat()
                from zephyr.data.table_registry import get_registry as _gr

                symbols = [
                    r[0]
                    for r in _make_cli().execute(
                        SQL_UNIVERSE.format(kline=_gr().table("market_kline_daily_hfq")),
                        {"start": start, "n": args.top_n},
                    )
                ]
            else:
                symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
            panels = prepare_multi_symbol(symbols, args.days)
            syms = sorted(panels)
            predictor, device = load_predictor(model_size=args.model_size)
            result = walk_forward_multi_batch(predictor, panels, n_test=args.n_test, sample_count=args.sample_count)
            per, per_naive = {}, {}
            pooled_k, pooled_r = [], []
            for s in syms:
                r = result["per_symbol"][s]
                per[s] = evaluate_distribution_forecast(r["q_preds"], r["realized"])
                per_naive[s] = evaluate_distribution_forecast(r["naive_q"], r["realized"])
                pooled_k += list(r["q_preds"][0.5])
                pooled_r += list(r["realized"])
            naive_rep = evaluate_distribution_forecast(result["naive_pool"], np.asarray(pooled_r))
            summary_rows = [
                {
                    "symbol": s,
                    "kronos_sharpness": per[s]["sharpness"],
                    "naive_sharpness": per_naive[s]["sharpness"],
                    "kronos_calibrated_share": per[s]["calibrated_share"],
                    "naive_calibrated_share": per_naive[s]["calibrated_share"],
                    "kronos_beats_naive_sharpness": per[s]["sharpness"] < per_naive[s]["sharpness"],
                }
                for s in syms
            ]
            pooled_median = {
                "kronos_p50_close": round(float(np.median(pooled_k)), 2),
            }
            print(
                json.dumps(
                    {
                        "mode": "window",
                        "symbols": syms,
                        "n_test": args.n_test,
                        "sample_count": args.sample_count,
                        "device": device,
                        "per_symbol": {
                            s: {
                                "calibrated_share": r["calibrated_share"],
                                "pit_ks": r["pit_ks"],
                                "sharpness": r["sharpness"],
                            }
                            for s, r in per.items()
                        },
                        "per_symbol_naive": {
                            s: {"calibrated_share": r["calibrated_share"]} for s, r in per_naive.items()
                        },
                        "naive_pool_p50_close": round(float(np.median(result["naive_pool"][0.5])), 2),
                        "pooled": pooled_median,
                        "summary_rows": summary_rows,
                    },
                    ensure_ascii=False,
                    indent=1,
                    default=str,
                )
            )
            return 0

        predictor, device = load_predictor(model_size=args.model_size)
        kdf = fetch_kline(args.symbol, args.days)
        result = walk_forward_eval(predictor, kdf, n_test=args.n_test, sample_count=args.sample_count)
        krono_rep = evaluate_distribution_forecast(result["kronos"], result["realized"])
        naive_rep = evaluate_distribution_forecast(result["naive"], result["realized"])
        print(
            json.dumps(
                {"symbol": args.symbol, "device": device, "kronos": krono_rep, "naive_rw": naive_rep},
                ensure_ascii=False,
                indent=1,
                default=str,
            )
        )
    except (RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
