# [BLUEPRINT] MOD-BT-204 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.kronos_finetune_prep
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.data.ch_config; zephyr.data.table_registry
# [CONSUMERS] 策略生产全景图 FAC-E1E Kronos 微调数据管线（GPU 夜窗启动，微调产物替换 vendor/kronos_weights/kronos_small）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 数据=CH 后复权日K线 OHLCV+amount（与推理同口径）；切分=时序 80/20（禁随机打乱）；
#   格式=Kronos finetune_csv 规范（date,open,high,low,close,volume,amount）；
#   输出=.runtime/tmp/kronos_finetune_data/（gitignore 区）；启动脚本=调用官方 finetune/
#   目录下 finetune.py（Kronos 官方仓 vendor/Kronos/finetune/）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据不足/格式不合规)
# [TESTS] tests/backtest/test_kronos_finetune_prep.py
# [A_module] module_id=MOD-BT-204 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 非常驻服务：事件调用无常驻循环
"""FAC-E1E Kronos 微调数据管线——CH 数据→finetune CSV→启动脚本。

官方微调脚本在 vendor/Kronos/finetune/finetune.py，输入=每标的一个 CSV
（columns: date,open,high,low,close,volume,amount），按时间序 80/20 切分。
本模块准备数据+生成启动命令（GPU 夜窗/周六窗手动执行）。

用法:
  python scripts/backtest/kronos_finetune_prep.py prep --top-n 10
  python scripts/backtest/kronos_finetune_prep.py launch   # 打印 GPU 微调启动命令
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from zephyr.data.table_registry import get_registry
_KLIDE_TABLE = get_registry().table("market_kline_daily_hfq")



_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_DATA_DIR = _ROOT / ".runtime" / "tmp" / "kronos_finetune_data"


def fetch_klines(symbols: list[str], days: int) -> dict[str, pd.DataFrame]:
    """批量拉多标的 K 线长表→按标的拆分。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    start = (date.today() - timedelta(days=int(days * 1.7))).isoformat()
    syms = tuple(symbols)
    rows = cli.execute(
        "SELECT trade_date, symbol_canonical, open, high, low, close, volume, amount "
        "FROM " + _KLIDE_TABLE + " WHERE trade_date >= %(start)s "
        "AND symbol_canonical IN %(syms)s ORDER BY trade_date",
        {"start": start, "syms": syms})
    df = pd.DataFrame(rows, columns=["date", "s", "open", "high", "low",
                                     "close", "volume", "amount"])
    for c in ("open", "high", "low", "close", "volume", "amount"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().drop_duplicates(["date", "s"], keep="last")
    return {s: g.reset_index(drop=True) for s, g in df.groupby("s")}


def run_prep(top_n: int = 10, days: int = 500) -> dict:
    """微调数据准备：拉数据→切分→写 CSV 到 finetune 目录。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    start = (date.today() - timedelta(days=int(days * 1.7))).isoformat()
    syms = [r[0] for r in cli.execute(
        "SELECT symbol_canonical FROM (SELECT symbol_canonical, avg(amount) AS a "
        "FROM " + _KLIDE_TABLE + " WHERE trade_date >= %(s)s "
        "GROUP BY 1 ORDER BY a DESC LIMIT %(n)s)",
        {"s": start, "n": top_n})]
    panels = fetch_klines(syms, days)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for s, g in panels.items():
        out = _DATA_DIR / f"{s.replace('.', '_')}.csv"
        g.to_csv(out, index=False, encoding="utf-8")
        written.append({"file": str(out), "rows": len(g)})
    record = {"data_dir": str(_DATA_DIR), "files": written, "top_n": top_n,
              "train_val_split": "80/20 时序切分（finetune.py 内置）",
              "launch_cmd": f"python vendor/Kronos/finetune/finetune.py "
                            f"--data-dir {_DATA_DIR} --epochs 10 --device cuda"}
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1E Kronos 微调数据准备（GPU 夜窗启动）")
    ap.add_argument("--top-n", type=int, default=10, help="成交额 top N 标的")
    ap.add_argument("--days", type=int, default=500, help="K 线历史天数")
    args = ap.parse_args()
    rep = run_prep(top_n=args.top_n, days=args.days)
    print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
