# [BLUEPRINT] MOD-DATA-061 | docs/03_modules/_domain_data/（板块成分聚合族，depgraph node=15775269）
# [MODULE] scripts.data.kline_sector_intraday_from_constituents
# [DOMAIN] D_DATA
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service; c1_market.sector_constituent(只读); c1_market.kline_1min(只读); pandas
# [CONSUMERS] 调度器 intraday_sector 组（kline_sector_intraday 表下游全族：kline_sector_880_resample 口径复核/SEC 逆势榜/Dashboard 板块页）
# [STARTUP] scheduled
# [MATURITY] testing
# [INVARIANTS] 等权链式聚合（与 docs/_working/disk_reorg_campaign/a7_sector_switch_validation.md 校验批同法：成员分钟收盘前向填充→逐分钟成员收益均值→链乘）；基点=当日首分钟成员等权均价，逐日重置禁跨日拼接（tdx 点位历史不可拼，a7 §一）；code 统一后缀码 880xxx.SH（修复存量行业板裸码暗伤）；data_source='internal_eqw' 可溯源；1m 条为单点条 OHLC 相等（源无分钟内路径），5m/15m/30m/60m 由 1m 路径桶聚合出真实 OHLC；volume/amount=成员真实成交合计；ReplacingMergeTree (code,period,trade_date) 同键重跑幂等（merge 后新数据胜）；停牌成员前向填充收益记 0
# [MODIFY-GUARD] docs/_working/disk_reorg_campaign/a6_remaining_work_order.md §F+
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空成员/全停牌板跳过不炸；成员<3 板跳过并在 stderr 计数；CH 写失败非零退出；--pilot 只算 5 板不入库
# [TESTS] tests/zephyr/data/test_sector_eqw_from_constituents.py
# [CONVERGENCE-HOLD] 收敛裁定已落（2026-10-01，总包依 Owner 授权自裁）：**方案甲-强化版**——本件为板块分钟线收敛终点（下游两处 SQL 消费均分钟收益口径零点位依赖，M1 挖矿 A_mine.md；J 跨日链式三断且强依赖 t-1 日K 管线=脆弱源弃用）；J 计划任务 sector_board_synth_eod 遵 S12 不注销，runner 转 dry-run 留观；本件吸收 J 双保险=tdx 真值保护+回补清场 delete_where 非 tdx 旧行；证据链=A_mine.md+a7 §六

# -*- coding: utf-8 -*-
"""板块分钟线自产（tdx 断供替代源，Owner 工单 a6 §F+）。

背景：tdx 外部服务器断供，kline_sector_intraday 1m 自 09-30 全断（行业腿更早，
09-10 死）；本任务从 CH kline_1min（成分股，健康）按 sector_constituent 成员
等权聚合出自产板块分钟线，五周期一锅出（1m 直聚 + 5/15/30/60m 桶聚合），
不再依赖 tdx 与已停产的 resample 链。

口径（a7 校验批 PASS 背书）：等权 vs tdx 加权的结构性偏差=路径 RMS 中位 4.3bps/
分钟收益相关 0.90/日收益差中位 25.9bps；绝对点位与 tdx 不可拼接，切换日基点重置。

用法：
  python kline_sector_intraday_from_constituents.py --date 20260929   # 回补某日
  python kline_sector_intraday_from_constituents.py                    # 默认当日
  python kline_sector_intraday_from_constituents.py --date 20260929 --pilot
"""

from __future__ import annotations

import argparse
import sys
from datetime import date as _date
from datetime import datetime, timedelta

import pandas as pd

sys.path.insert(0, r"D:/ZephyrAlpha/src")

from zephyr.data.table_registry import get_registry  # noqa: E402

# 表名走 TableRegistry 真源（#ARCH-CH-024；market_sector_kline_intraday=既有正牌品类，本批归一）
TBL = get_registry().table("market_sector_kline_intraday")
TBL_STOCK_1M = get_registry().table("market_kline_1min")
TBL_MEMBERS = get_registry().table("market_sector_constituent_880")
PERIODS = ("1m", "5m", "15m", "30m", "60m")
BUCKET_MIN = {"5m": 5, "15m": 15, "30m": 30, "60m": 60}
MIN_MEMBERS = 3

SQL_MEMBERS = (
    "SELECT sector_code, stock_code FROM "
    + TBL_MEMBERS
    + " WHERE valid_from <= %(d)s AND (valid_to IS NULL OR valid_to > %(d)s)"
)
SQL_STOCK_1M = (
    "SELECT trade_time, symbol, close, volume, amount FROM " + TBL_STOCK_1M + " WHERE toDate(trade_date) = %(d)s"  # noqa: bare-sql  品类真源表名拼接+参数化日占位，模块级 SQL_ 常量
)


def compute_board_1m(member_close: pd.DataFrame) -> pd.Series | None:
    """成员分钟收盘宽表 → 板等权链式路径（单点分钟条）。成员<MIN_MEMBERS 或无有效格返回 None。

    member_close: index=分钟戳(升序), columns=成员裸码, values=close(Decimal/float)。
    """
    sub = member_close.astype(float)
    sub = sub.loc[:, sub.notna().sum() > 0]
    if sub.shape[1] < MIN_MEMBERS:
        return None
    sub = sub.ffill()
    if sub.isna().all().all() or len(sub) < 2:
        return None
    rets = sub.pct_change(fill_method=None).iloc[1:]
    base = float(sub.iloc[0].mean())
    path = base * (1.0 + rets.mean(axis=1).fillna(0.0)).cumprod()
    out = pd.concat([pd.Series([base], index=[sub.index[0]]), path])
    return out.sort_index()


def bucket_ohlc(
    path_1m: pd.Series, minutes: int, vol_1m: pd.Series | None = None, amt_1m: pd.Series | None = None
) -> pd.DataFrame:
    """1m 路径（单点条）→ N 分钟桶 OHLC（O=首/H=max/L=min/C=尾）+ 成交量额合计。"""
    grp = path_1m.index.floor(f"{minutes}min")
    rows = []
    for key, idx in pd.Series(range(len(path_1m)), index=path_1m.index).groupby(grp).groups.items():
        seg = path_1m.loc[idx]
        row = {
            "trade_date": key.to_pydatetime(),
            "open": round(float(seg.iloc[0]), 4),
            "high": round(float(seg.max()), 4),
            "low": round(float(seg.min()), 4),
            "close": round(float(seg.iloc[-1]), 4),
        }
        if vol_1m is not None:
            sub_v = vol_1m.reindex(idx).fillna(0)
            row["volume"] = int(sub_v.sum())
        if amt_1m is not None:
            sub_a = amt_1m.reindex(idx).fillna(0)
            row["amount"] = round(float(sub_a.sum()), 2)
        rows.append(row)
    return pd.DataFrame(rows)


def build_board_rows(
    code_suffixed: str, member_closes: pd.DataFrame, member_vol: pd.DataFrame, member_amt: pd.DataFrame
) -> list[tuple]:
    """单板全周期行集。返回 (trade_date, code, period, open, high, low, close, volume, amount, data_source)。"""
    path = compute_board_1m(member_closes)
    if path is None:
        return []
    rows: list[tuple] = []
    vol_sum = member_vol.sum(axis=1) if not member_vol.empty else None
    amt_sum = member_amt.sum(axis=1) if not member_amt.empty else None
    for period in PERIODS:
        if period == "1m":
            df = pd.DataFrame(
                {
                    "trade_date": [t.to_pydatetime() for t in path.index],
                    "open": path.round(4).values,
                    "high": path.round(4).values,
                    "low": path.round(4).values,
                    "close": path.round(4).values,
                    "volume": (vol_sum.reindex(path.index).fillna(0).astype("int64") if vol_sum is not None else 0),
                    "amount": (amt_sum.reindex(path.index).fillna(0).round(2) if amt_sum is not None else 0.0),
                }
            )
        else:
            df = bucket_ohlc(path, BUCKET_MIN[period], vol_1m=vol_sum, amt_1m=amt_sum)
        for _, r in df.iterrows():
            rows.append(
                (
                    r["trade_date"],
                    code_suffixed,
                    period,
                    float(r["open"]),
                    float(r["high"]),
                    float(r["low"]),
                    float(r["close"]),
                    int(r.get("volume", 0) or 0),
                    float(r.get("amount", 0) or 0),
                    "internal_eqw",
                )
            )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="板块分钟线自产（成分等权链式）")
    ap.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    ap.add_argument("--pilot", action="store_true", help="只算 5 板打印样例，不入库")
    ap.add_argument("--force", action="store_true", help="覆盖真值保护（目标日存在 tdx 行时仍写）")
    a = ap.parse_args()
    d = f"{a.date[:4]}-{a.date[4:6]}-{a.date[6:8]}"

    from zephyr.data.ch_writer import delete_where, write_tsv
    from zephyr.infrastructure.database_service import get_db_service

    cli = get_db_service().get_clickhouse_conn(role="reader", extra_kwargs={"settings": {"max_execution_time": 900}})

    # 真值保护（a7 §六裁定甲）：目标日存在 tdx 真值行则拒写，防等权值覆盖真值
    tdx_cnt = cli.execute(  # noqa: bare-sql  品类真源表名+参数化日占位，只读计数
        f"SELECT count() FROM {TBL} WHERE toDate(trade_date) = %(d)s AND data_source = 'tdx'",  # noqa: bare-sql  真值保护只读计数，表名走 Registry+参数化占位
        {"d": d},
    )[0][0]
    if tdx_cnt and not a.force:
        print(f"ABORT: {d} 存在 {tdx_cnt} 行 tdx 真值（真值保护）；确需覆盖加 --force", flush=True)
        return 1

    # 回补清场（收敛裁定甲）：清目标日非 tdx 旧行（synth_*/旧 internal_eqw），防双源同键混居
    if not a.pilot:
        if not delete_where(TBL, f"toDate(trade_date) = '{d}' AND data_source != 'tdx'"):  # noqa: bare-sql  回补清场 WHERE 片段经 delete_where 集中化通道
            print("ABORT: 回补清场 delete_where 失败", flush=True)
            return 1

    mem = pd.DataFrame(cli.execute(SQL_MEMBERS, {"d": d}), columns=["sector_code", "stock_code"])
    mem["bare"] = mem["stock_code"].str.split(".").str[0]
    if mem.empty:  # 行业板 09-30 前无成员 PIT 真值（a7 §二.5），回落当前快照
        mem = pd.DataFrame(cli.execute(SQL_MEMBERS, {"d": str(_date.today())}), columns=["sector_code", "stock_code"])
        mem["bare"] = mem["stock_code"].str.split(".").str[0]
        print(f"[warn] {d} 无 as-of 成员，回落当前快照（行业板漂移注记见 a7 §二.5）", flush=True)
    if mem.empty:
        print("ABORT: 成员名册为空", flush=True)
        return 1

    stk = pd.DataFrame(
        cli.execute(SQL_STOCK_1M, {"d": d}), columns=["trade_time", "symbol", "close", "volume", "amount"]
    )
    if stk.empty:
        print(f"ABORT: {d} kline_1min 无数据", flush=True)
        return 1
    stk["trade_time"] = pd.to_datetime(stk["trade_time"]).dt.floor("s")
    close_w = stk.pivot_table(index="trade_time", columns="symbol", values="close", aggfunc="last")
    vol_w = stk.pivot_table(index="trade_time", columns="symbol", values="volume", aggfunc="sum")
    amt_w = stk.pivot_table(index="trade_time", columns="symbol", values="amount", aggfunc="sum")
    amt_w = amt_w.astype(float)  # CH Decimal → object 列，强制数值防 .round TypeError
    for w in (close_w, vol_w, amt_w):
        w.index = pd.to_datetime(w.index).floor("s")
        w.sort_index(inplace=True)

    all_rows: list[tuple] = []
    skipped = 0
    boards = sorted(mem["sector_code"].unique())
    if a.pilot:
        qualified = [
            b
            for b in boards
            if sum(1 for m in mem.loc[mem["sector_code"] == b, "bare"].drop_duplicates() if m in close_w.columns)
            >= MIN_MEMBERS
        ]
        boards = qualified[:5]
        print(f"[pilot] qualified sample: {boards}", flush=True)
    for sector_code in boards:
        bare_members = mem.loc[mem["sector_code"] == sector_code, "bare"].drop_duplicates().tolist()
        secs = [m for m in bare_members if m in close_w.columns]
        if len(secs) < MIN_MEMBERS:
            skipped += 1
            continue
        code_suffixed = sector_code if "." in sector_code else f"{sector_code}.SH"
        rows = build_board_rows(code_suffixed, close_w[secs], vol_w[secs], amt_w[secs])
        all_rows.extend(rows)

    print(f"boards={len(boards)} skipped(<{MIN_MEMBERS} members)={skipped} rows={len(all_rows)}", flush=True)
    if a.pilot:
        for r in all_rows[:10]:
            print(r)
        return 0
    if not all_rows:
        print("nothing to write", flush=True)
        return 1

    cols = "(trade_date, code, period, open, high, low, close, volume, amount, data_source)"
    header = ",".join(cols.strip("()").split(", "))
    lines = []
    for r in all_rows:
        lines.append(
            "\t".join(
                [
                    r[0].strftime("%Y-%m-%d %H:%M:%S"),
                    r[1],
                    r[2],
                    f"{r[3]:.4f}",
                    f"{r[4]:.4f}",
                    f"{r[5]:.4f}",
                    f"{r[6]:.4f}",
                    str(r[7]),
                    f"{r[8]:.2f}",
                    r[9],
                ]
            )
        )
    ok = write_tsv(TBL, cols, ("\n".join(lines) + "\n").encode("utf-8"), create_fallback=False)
    if not ok:
        print("WRITE FAILED", flush=True)
        return 1
    print(f"written {len(lines)} rows -> {TBL} (data_source=internal_eqw)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
