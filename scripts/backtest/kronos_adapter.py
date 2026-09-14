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


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1E Kronos 基线适配器（walk-forward 双标准评分）")
    ap.add_argument("--symbol", default="600519.SH")
    ap.add_argument("--n-test", type=int, default=20)
    ap.add_argument("--sample-count", type=int, default=16)
    ap.add_argument("--days", type=int, default=250)
    ap.add_argument("--model-size", default="small")
    args = ap.parse_args()
    try:
        predictor, device = load_predictor(model_size=args.model_size)
        kdf = fetch_kline(args.symbol, args.days)
        result = walk_forward_eval(predictor, kdf, n_test=args.n_test,
                                   sample_count=args.sample_count)
        from scripts.backtest.distribution_forecast_eval import evaluate_distribution_forecast
        krono_rep = evaluate_distribution_forecast(result["kronos"], result["realized"])
        naive_rep = evaluate_distribution_forecast(result["naive"], result["realized"])
        krono_rep["verdict"] = {
            "calibrated": krono_rep["calibrated_share"] >= 0.6,
            "beats_naive_sharpness": (
                krono_rep["sharpness"] < naive_rep["sharpness"]
                if krono_rep["sharpness"] and naive_rep["sharpness"] else False),
        }
        naive_rep["verdict"] = {"calibrated": naive_rep["calibrated_share"] >= 0.6}
        print(json.dumps({"symbol": args.symbol, "device": device,
                          "kronos": krono_rep, "naive_rw": naive_rep},
                         ensure_ascii=False, indent=1, default=str))
    except (RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
