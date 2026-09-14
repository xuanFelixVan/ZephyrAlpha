# [BLUEPRINT] MOD-BT-195 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.kronos_adapter
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; torch; model.kronos(官方仓 .runtime/tmp/kronos_repo); zephyr.data.ch_config; scripts.backtest.distribution_forecast_eval
# [CONSUMERS] 策略生产全景图 FAC-E1E 车道E 模型基线（Kronos 接入，只当基线对台不当信号）；
#   E4 分布预测双标准考尺（MOD-BT-194）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] PIT：预测只用 ≤T 数据（walk-forward 无前视）；样本分位数=逐 horizon 跨
#   sample_count 样本取分位；K 线重复日期 drop_duplicates(keep=last)；权重目录
#   .runtime/tmp/kronos_weights（镜像下载）；本模块只做基线对台，判定权在 E4
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(仓/权重缺失); ValueError(数据不足)
# [TESTS] tests/backtest/test_kronos_adapter.py
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
    """官方仓 model.kronos 导入（仓缺失 fail-closed 带指引）。"""
    if not KRONOS_REPO.exists():
        raise RuntimeError(
            f"Kronos 官方仓缺失: {KRONOS_REPO}（VPN 开启后 "
            "git clone --depth 1 https://github.com/shiyu-coder/Kronos 到该目录）")
    return None


SQL_KLINE_ONE = (
    "SELECT trade_date, open, high, low, close, volume, amount "
    "FROM {t} WHERE symbol_canonical = %(sym)s AND trade_date >= %(start)s "
    "ORDER BY trade_date"
)


def _make_cli():
    """CH 只读客户端（独立函数=测试可注入）。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    return Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                  user=cfg.get("user", "default"), password=cfg.get("password", ""),
                  connect_timeout=5)


def fetch_kline(symbol: str, days: int) -> pd.DataFrame:
    """单标的 K 线长表（CH 后复权；重复日期 keep=last；数值化）。"""
    from zephyr.data.table_registry import get_registry

    cli = _make_cli()
    start = (date.today() - timedelta(days=int(days * 1.7))).isoformat()
    rows = cli.execute(
        SQL_KLINE_ONE.format(t=get_registry().table("market_kline_daily_hfq")),
        {"sym": symbol, "start": start})
    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close",
                                     "volume", "amount"])
    for c in ("open", "high", "low", "close", "volume", "amount"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().drop_duplicates(["date"], keep="last").reset_index(drop=True)
    if len(df) < 60:
        raise ValueError(f"K 线数据不足: {symbol} {len(df)} 行")
    return df


def load_predictor(device: str = "auto", model_size: str = "small"):
    """加载 Tokenizer+模型+Predictor（权重缺失 fail-closed 带下载指引）。"""
    import torch

    _load_kronos_classes()
    sys.path.insert(0, str(KRONOS_REPO))
    from model.kronos import Kronos, KronosPredictor, KronosTokenizer

    tok_dir = WEIGHTS_DIR / ("kronos_tokenizer_base" if model_size != "mini" else
                             "kronos_tokenizer_mini")
    model_dir = WEIGHTS_DIR / f"kronos_{model_size}"
    for d in (tok_dir, model_dir):
        if not d.exists():
            raise RuntimeError(
                f"权重缺失: {d}（curl -L https://hf-mirror.com/NeoQuasar/... 到该目录）")
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


def predict_close_quantiles(predictor, kdf: pd.DataFrame, pred_len: int = 1,
                            sample_count: int = 16, temperature: float = 1.0,
                            top_p: float = 0.9) -> dict:
    """对 kdf 次日（pred_len 天）生成收盘价分位预测。

    实现：走 KronosPredictor.predict 的样本维（sample_count>1 时 predict 返回 3D，
    故绕开 DataFrame 封装直接取 (sample_count, pred_len) 的 close 列）。
    """
    import torch  # noqa: F401 — predictor 内部用

    ctx = kdf.copy()
    x_index = pd.Series(pd.to_datetime(ctx["date"]))
    y_index = pd.Series(pd.to_datetime(ctx["date"]).iloc[-1]
                        + pd.tseries.offsets.BDay(1) * np.arange(1, pred_len + 1))
    # 样本保留版预测：preds 形状 (sample_count, pred_len)（close 通道）
    samples = _generate_with_stamps(predictor, ctx, y_index, pred_len,
                                    sample_count, temperature, top_p)
    return _sample_quantiles(samples, QUANTILES), y_index


def _generate_with_stamps(predictor, ctx: pd.DataFrame, y_index: pd.Index,
                          pred_len: int, sample_count: int, temperature: float,
                          top_p: float) -> np.ndarray:
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
        preds = predictor.generate(xn[np.newaxis, :], x_stamp[np.newaxis, :],
                                   y_stamp[np.newaxis, :], pred_len,
                                   T=temperature, top_k=0, top_p=top_p,
                                   sample_count=1, verbose=False)
        paths.append(preds.squeeze(0) * (x_std + 1e-5) + x_mean)
    return np.stack(paths)[:, :, 3]  # (sample_count, pred_len) close 通道


def naive_quantiles(kdf: pd.DataFrame, dates: list, quantiles: tuple,
                    window: int = 20) -> dict:
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


def walk_forward_eval(predictor, kdf: pd.DataFrame, n_test: int = 20,
                      sample_count: int = 16, quantiles: tuple = QUANTILES) -> dict:
    """Walk-forward 分布预测回放（无前视）→ 194 考尺输入（Kronos vs 随机游走基准）。"""
    kdf = kdf.sort_values("date").reset_index(drop=True)
    test_dates = kdf["date"].iloc[-n_test:].tolist()
    krono = {float(q): [] for q in quantiles}
    naive = {float(q): [] for q in quantiles}
    realized = []
    for d in test_dates:
        pos = kdf.index[kdf["date"] == d][0]
        ctx = kdf.iloc[:pos]
        q_k, _ = predict_close_quantiles(predictor, ctx, pred_len=1,
                                         sample_count=sample_count)
        q_n = naive_quantiles(kdf, [d], quantiles)
        for q in quantiles:
            krono[float(q)].append(q_k[float(q)][0])
            naive[float(q)].append(q_n[float(q)][0])
        realized.append(float(kdf.loc[pos, "close"]))
    realized = np.asarray(realized)
    return {
        "n_test": n_test, "sample_count": sample_count,
        "kronos": krono, "naive": naive, "realized": realized,
        "dates": [str(d) for d in test_dates],
    }


def eval_multi(symbols: list[str], n_test: int, sample_count: int,
               days: int, model_size: str = "small") -> dict:
    """多票 walk-forward 评估（模型单次加载跨票复用）。"""
    predictor, device = load_predictor(model_size=model_size)
    per_symbol = []
    for sym in symbols:
        try:
            kdf = fetch_kline(sym, days)
            result = walk_forward_eval(predictor, kdf, n_test=n_test,
                                       sample_count=sample_count)
            from scripts.backtest.distribution_forecast_eval import (
                evaluate_distribution_forecast,
            )

            krono = evaluate_distribution_forecast(result["kronos"], result["realized"])
            naive = evaluate_distribution_forecast(result["naive"], result["realized"])
            per_symbol.append({
                "symbol": sym, "n_test": result["n_test"],
                "kronos": krono, "naive_rw": naive,
                "kronos_beats_naive_sharpness":
                    krono["sharpness"] < naive["sharpness"],
            })
            print(f"[{sym}] kronos sharp={krono['sharpness']:.2f} "
                  f"cal={krono['calibrated_share']:.2f} | naive "
                  f"sharp={naive['sharpness']:.2f} cal={naive['calibrated_share']:.2f}")
        except Exception as exc:  # noqa: BLE001 — 单票失败不拖全局
            per_symbol.append({"symbol": sym, "error": str(exc)[:120]})
            print(f"[{sym}] FAIL: {exc}")
    return {"device": device, "per_symbol": per_symbol,
            "aggregate": aggregate_symbol_reports(per_symbol)}


def aggregate_symbol_reports(per_symbol: list[dict]) -> dict:
    """多票聚合计分板（纯函数）：中位数对比+胜场统计（锐度更紧=胜）。"""
    valid = [r for r in per_symbol if "error" not in r]
    wins = sum(1 for r in valid
               if r["kronos"]["sharpness"] < r["naive_rw"]["sharpness"])
    cal_wins = sum(1 for r in valid
                   if r["kronos"]["calibrated_share"] >= r["naive_rw"]["calibrated_share"])

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
        "symbols_total": len(per_symbol), "symbols_ok": len(valid),
        "symbols_error": len(per_symbol) - len(valid),
        "kronos_sharp_wins": wins, "kronos_cal_wins": cal_wins,
        "win_rate_sharpness": round(wins / len(valid), 4) if valid else None,
        "median_kronos_calibrated_share": _med("kronos.calibrated_share"),
        "median_naive_calibrated_share": _med("naive_rw.calibrated_share"),
        "median_kronos_sharpness": _med("kronos.sharpness"),
        "median_naive_sharpness": _med("naive_rw.sharpness"),
        "median_kronos_pit_ks": _med("kronos.pit_ks"),
        "median_naive_pit_ks": _med("naive_rw.pit_ks"),
    }


def prepare_multi_symbol(symbols: list[str], days: int,
                         min_history: int = 260) -> dict[str, pd.DataFrame]:
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
        raise RuntimeError(f"公共日期面板标的不足: {len(out)}/{len(symbols)}；"
                           f"跳过明细见上方 SKIP")
    return out


def walk_forward_multi_batch(predictor, panels: dict[str, pd.DataFrame],
                             n_test: int, sample_count: int,
                             quantiles: tuple = QUANTILES) -> dict:
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
        batch = np.stack([
            np.clip((x[s][:day_i] - mean[s]) / (std[s] + 1e-5), -5, 5) for s in syms])
        x_stamp = calc_time_stamps(pd.Series(pd.to_datetime(dates[:day_i]))).values.astype(np.float32)
        y_stamp = calc_time_stamps(pd.Series(pd.to_datetime([d] * b))).values.astype(np.float32)
        for _ in range(int(sample_count)):
            preds = predictor.generate(batch, x_stamp[np.newaxis], y_stamp[np.newaxis],
                                       1, T=1.0, top_k=0, top_p=0.9,
                                       sample_count=1, verbose=False)
            p = np.asarray(preds, dtype=float)
            if p.ndim == 3:
                p = p[:, 0, :]
            close_ch = p[:, 3] * np.array([close_sd[s] + 1e-5 for s in syms])                 + np.array([close_mean[s] for s in syms])
            for j, s in enumerate(syms):
                close_samples[s][ti].append(float(close_ch[j]))

    naive_fn = naive_quantiles
    out = {"symbols": syms, "n_test": n_test, "sample_count": int(sample_count),
           "per_symbol": {}}
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
        out["per_symbol"][s] = {"q_preds": qp, "naive_q": naive_q,
                                "realized": np.asarray(real)}
        for q in quantiles:
            naive_pool[float(q)] += list(naive_q[float(q)])
    out["naive_pool"] = {q: np.asarray(v) for q, v in naive_pool.items()}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1E Kronos 基线适配器（walk-forward 双标准评分）")
    ap.add_argument("--symbol", default=None, help="单标的模式")
    ap.add_argument("--symbols", default=None, help="逗号分隔多标的（窗口模式）")
    ap.add_argument("--top-n", type=int, default=None, help="成交额 top N 自动选票")
    ap.add_argument("--n-test", type=int, default=60)
    ap.add_argument("--sample-count", type=int, default=8)
    ap.add_argument("--days", type=int, default=250)
    ap.add_argument("--model-size", default="small")
    args = ap.parse_args()
    try:
        from scripts.backtest.distribution_forecast_eval import (
            evaluate_distribution_forecast,
        )

        multi = args.symbols or args.top_n
        if multi:
            if not args.symbols:
                from scripts.backtest.kronos_adapter import _make_cli
                from scripts.backtest.lane_c_formula_miner import SQL_UNIVERSE
                import datetime as _dt

                start = (date.today() - timedelta(days=int(args.days * 1.7))).isoformat()
                from zephyr.data.table_registry import get_registry as _gr

                symbols = [r[0] for r in _make_cli().execute(
                    SQL_UNIVERSE.format(kline=_gr().table("market_kline_daily_hfq")),
                    {"start": start, "n": args.top_n})]
            else:
                symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
            panels = prepare_multi_symbol(symbols, args.days)
            syms = sorted(panels)
            predictor, device = load_predictor(model_size=args.model_size)
            result = walk_forward_multi_batch(predictor, panels,
                                              n_test=args.n_test,
                                              sample_count=args.sample_count)
            per, per_naive = {}, {}
            pooled_k, pooled_r = [], []
            for s in syms:
                r = result["per_symbol"][s]
                per[s] = evaluate_distribution_forecast(r["q_preds"], r["realized"])
                per_naive[s] = evaluate_distribution_forecast(
                    r["naive_q"], r["realized"])
                pooled_k += list(r["q_preds"][0.5])
                pooled_r += list(r["realized"])
            naive_rep = evaluate_distribution_forecast(
                result["naive_pool"], np.asarray(pooled_r))
            summary_rows = [
                {"symbol": s,
                 "kronos_sharpness": per[s]["sharpness"],
                 "naive_sharpness": per_naive[s]["sharpness"],
                 "kronos_calibrated_share": per[s]["calibrated_share"],
                 "naive_calibrated_share": per_naive[s]["calibrated_share"],
                 "kronos_beats_naive_sharpness":
                     per[s]["sharpness"] < per_naive[s]["sharpness"]}
                for s in syms]
            pooled_median = {
                "kronos_p50_close": round(float(np.median(pooled_k)), 2),
            }
            print(json.dumps({"mode": "window", "symbols": syms,
                              "n_test": args.n_test,
                              "sample_count": args.sample_count, "device": device,
                              "per_symbol": {s: {"calibrated_share": r["calibrated_share"],
                                                 "pit_ks": r["pit_ks"],
                                                 "sharpness": r["sharpness"]}
                                             for s, r in per.items()},
                              "per_symbol_naive": {
                                  s: {"calibrated_share": r["calibrated_share"]}
                                  for s, r in per_naive.items()},
                              "naive_pool_p50_close": round(
                                  float(np.median(result["naive_pool"][0.5])), 2),
                              "pooled": pooled_median,
                              "summary_rows": summary_rows},
                             ensure_ascii=False, indent=1, default=str))
            return 0

        predictor, device = load_predictor(model_size=args.model_size)
        kdf = fetch_kline(args.symbol, args.days)
        result = walk_forward_eval(predictor, kdf, n_test=args.n_test,
                                   sample_count=args.sample_count)
        krono_rep = evaluate_distribution_forecast(result["kronos"], result["realized"])
        naive_rep = evaluate_distribution_forecast(result["naive"], result["realized"])
        print(json.dumps({"symbol": args.symbol, "device": device,
                          "kronos": krono_rep, "naive_rw": naive_rep},
                         ensure_ascii=False, indent=1, default=str))
    except (RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
