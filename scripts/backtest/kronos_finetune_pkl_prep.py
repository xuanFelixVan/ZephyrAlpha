# [BLUEPRINT] MOD-BT-204 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.kronos_finetune_pkl_prep
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; numpy; scripts.backtest.kronos_finetune_prep
# [CONSUMERS] 策略生产全景图 FAC-E1E Kronos 微调链路（vendor/Kronos/finetune/
#   train_tokenizer.py + train_predictor.py 经 QlibDataset 读本模块产物训练）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] pkl 结构={symbol: DataFrame(datetime+feature_list 六列)} 精确对齐
#   vendor/Kronos/finetune/dataset.py QlibDataset 契约（reset_index 后 'datetime'
#   列存在、按 timestamps 升序、重复日 keep=last）；切分=每标的时序 80/20 禁随机
#   打乱；val 头部回看 lookback_window 行上下文（官方 config 同款重叠实践）；
#   <250 行标的剔除；输出={config.dataset_path}/train_data.pkl|val_data.pkl
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(CSV 缺失/格式不合规); ValueError(单标的切分后窗口不足)
# [TESTS] tests/backtest/test_kronos_finetune_pkl_prep.py
# [A_module] module_id=MOD-BT-204 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 非常驻服务：GPU 夜窗训练前事件调用
"""FAC-E1E Kronos 微调 pkl 适配层——官方规范 CSV→QlibDataset 可读 pkl。

官方训练脚本（vendor/Kronos/finetune/train_*.py）只吃 QlibDataset：读
{config.dataset_path}/train_data.pkl|val_data.pkl，dict 按标的为键，窗口采样
结构见 dataset.py __getitem__（window=lookback+predict+1，时间特征由 datetime
现算）。本模块补齐 CSV→pkl 适配层：
  1 调 kronos_finetune_prep 产官方七列 CSV（或读既有 CSV 目录）；
  2 每标的清洗（升序/去重 keep=last/数值化）→时序 80/20 切分（禁随机打乱）；
  3 <min_rows 标的剔除；val 头部补 lookback_window 行上下文（官方重叠实践）；
  4 写 {config.dataset_path}/train_data.pkl 与 val_data.pkl + manifest.json。

用法:
  python scripts/backtest/kronos_finetune_pkl_prep.py --top-n 20 --days 1200
  python scripts/backtest/kronos_finetune_pkl_prep.py --from-existing
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pickle
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_VENDOR_FINETUNE_DIR = _ROOT / "vendor" / "Kronos" / "finetune"

CSV_COLS = ["timestamps", "open", "high", "low", "close", "volume", "amount"]
DATETIME_COL = "datetime"
DEFAULT_MIN_ROWS = 250
DEFAULT_TRAIN_RATIO = 0.8


def load_vendor_config():
    """加载 vendor/Kronos/finetune/config.py 的 Config（特征/路径真源，防漂移）。"""
    spec = importlib.util.spec_from_file_location(
        "kronos_finetune_config", _VENDOR_FINETUNE_DIR / "config.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"vendor config 缺失: {_VENDOR_FINETUNE_DIR / 'config.py'}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Config()


def _clean_panel(df: pd.DataFrame) -> pd.DataFrame:
    """单标的清洗：数值化→去缺失→时间升序→重复时间戳 keep=last（推理同口径）。"""
    out = df.copy()
    out["timestamps"] = pd.to_datetime(out["timestamps"], errors="coerce")
    for c in CSV_COLS[1:]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["timestamps"] + CSV_COLS[1:])
    out = (out.sort_values("timestamps")
              .drop_duplicates(subset=["timestamps"], keep="last")
              .reset_index(drop=True))
    return out


def temporal_split(df: pd.DataFrame, train_ratio: float = DEFAULT_TRAIN_RATIO,
                   lookback_window: int = 60) -> tuple[pd.DataFrame, pd.DataFrame]:
    """时序 80/20 切分（禁随机打乱）；val 头部回补 lookback 行上下文。

    官方 config 即用重叠（val_time_range 早于 train 结束）为 lookback 留上下文；
    切分点之后的数据不进 train，杜绝未来信息泄漏进训练集。
    """
    n = len(df)
    cut = int(n * train_ratio)
    if cut <= 0 or cut >= n:
        raise ValueError(f"切分点非法: n={n} ratio={train_ratio}")
    train = df.iloc[:cut].reset_index(drop=True)
    val = df.iloc[max(0, cut - int(lookback_window)):].reset_index(drop=True)
    return train, val


def _panel_to_contract(train: pd.DataFrame, val: pd.DataFrame,
                       feature_list: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """输出列重命名对齐 dataset.py 契约：datetime + feature_list 六列。"""
    def _fmt(df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns={"timestamps": DATETIME_COL})[
            [DATETIME_COL] + list(feature_list)]

    return _fmt(train), _fmt(val)


def build_pkl(data_dir: str | Path, out_dir: str | Path | None = None,
              min_rows: int = DEFAULT_MIN_ROWS,
              train_ratio: float = DEFAULT_TRAIN_RATIO) -> dict:
    """CSV 目录→train_data.pkl/val_data.pkl（结构对齐 QlibDataset 契约）。

    Returns:
        record dict: 各标的行数/窗口数/剔除原因 + pkl 路径，同步落 manifest.json。
    """
    cfg = load_vendor_config()
    feature_list = list(cfg.feature_list)
    window = cfg.lookback_window + cfg.predict_window + 1
    data_dir = Path(data_dir)
    if out_dir is None:
        out_dir = Path(cfg.dataset_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csvs = sorted(data_dir.glob("*.csv"))
    if not csvs:
        raise RuntimeError(f"无 CSV 可转换: {data_dir}")

    train_data: dict[str, pd.DataFrame] = {}
    val_data: dict[str, pd.DataFrame] = {}
    skipped: list[dict] = []
    details: list[dict] = []
    for csv in csvs:
        sym = csv.stem.replace("_", ".")
        raw = pd.read_csv(csv)
        if list(raw.columns) != CSV_COLS:
            skipped.append({"symbol": sym, "reason": f"列不规范: {list(raw.columns)}"})
            continue
        panel = _clean_panel(raw)
        if len(panel) < min_rows:
            skipped.append({"symbol": sym, "reason": f"行数不足 {len(panel)}<{min_rows}"})
            continue
        try:
            tr, va = temporal_split(panel, train_ratio=train_ratio,
                                    lookback_window=cfg.lookback_window)
        except ValueError as exc:
            skipped.append({"symbol": sym, "reason": str(exc)})
            continue
        if len(tr) < window or len(va) < window:
            skipped.append({"symbol": sym,
                            "reason": f"切分后窗口不足 train={len(tr)} val={len(va)} <{window}"})
            continue
        tr_c, va_c = _panel_to_contract(tr, va, feature_list)
        train_data[sym] = tr_c
        val_data[sym] = va_c
        details.append({
            "symbol": sym, "rows": len(panel),
            "train_rows": len(tr_c), "val_rows": len(va_c),
            "train_windows": len(tr_c) - window + 1,
            "val_windows": len(va_c) - window + 1,
        })

    if not train_data:
        raise RuntimeError(f"全部标的被剔除，无法构建 pkl: {skipped}")

    train_path = out_dir / "train_data.pkl"
    val_path = out_dir / "val_data.pkl"
    with open(train_path, "wb") as f:
        pickle.dump(train_data, f)
    with open(val_path, "wb") as f:
        pickle.dump(val_data, f)

    record = {
        "data_dir": str(data_dir), "train_pkl": str(train_path),
        "val_pkl": str(val_path),
        "lookback_window": cfg.lookback_window, "predict_window": cfg.predict_window,
        "window": window, "min_rows": min_rows, "train_ratio": train_ratio,
        "feature_list": feature_list,
        "time_feature_list_note": "TemporalEmbedding 硬契约 5 列(minute/hour/weekday/"
                                  "day/month)，日线 minute/hour 恒 0，由 dataset.py "
                                  "从 datetime 现算，pkl 不冗余存列",
        "symbols_used": sorted(train_data), "symbols_skipped": skipped,
        "details": details,
        "total_train_windows": sum(d["train_windows"] for d in details),
        "total_val_windows": sum(d["val_windows"] for d in details),
        "split": f"{train_ratio:.0%}/{1 - train_ratio:.0%} 时序切分(禁随机打乱), "
                 f"val 头部回补 {cfg.lookback_window} 行上下文",
    }
    manifest = out_dir / "manifest.json"
    manifest.write_text(json.dumps(record, ensure_ascii=False, indent=1, default=str),
                        encoding="utf-8")
    return record


def run(top_n: int, days: int, min_rows: int = DEFAULT_MIN_ROWS,
        train_ratio: float = DEFAULT_TRAIN_RATIO) -> dict:
    """全链：CH→CSV（复用 kronos_finetune_prep 产线）→pkl。"""
    from scripts.backtest.kronos_finetune_prep import run_prep

    prep_rec = run_prep(top_n=top_n, days=days)
    record = build_pkl(prep_rec["data_dir"], min_rows=min_rows,
                       train_ratio=train_ratio)
    record["prep"] = {"top_n": prep_rec["top_n"], "files": prep_rec["files"]}
    return record


def main() -> int:
    ap = argparse.ArgumentParser(
        description="FAC-E1E Kronos 微调 pkl 适配层（CSV→QlibDataset 契约 pkl）")
    ap.add_argument("--top-n", type=int, default=20, help="成交额 top N 标的")
    ap.add_argument("--days", type=int, default=1200, help="K 线历史天数")
    ap.add_argument("--min-rows", type=int, default=DEFAULT_MIN_ROWS,
                    help="最小行数过滤（<值剔除）")
    ap.add_argument("--train-ratio", type=float, default=DEFAULT_TRAIN_RATIO,
                    help="训练占比（时序切分）")
    ap.add_argument("--from-existing", action="store_true",
                    help="跳过 CH 拉取，直接转换既有 CSV 目录")
    args = ap.parse_args()
    if args.from_existing:
        cfg = load_vendor_config()
        csv_dir = Path(cfg.dataset_path).parent
        rec = build_pkl(csv_dir, min_rows=args.min_rows, train_ratio=args.train_ratio)
    else:
        rec = run(top_n=args.top_n, days=args.days, min_rows=args.min_rows,
                  train_ratio=args.train_ratio)
    print(json.dumps(rec, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
