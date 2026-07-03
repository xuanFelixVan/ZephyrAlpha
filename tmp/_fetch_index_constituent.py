"""#8 指数成分股 → index_constituent（iFind THS_DataPool，P1，倒序）。

策略：
- 倒序遍历日期（2026-07 → 2010，每半年一个快照: 06-30/12-31）
- 主要指数: 上证50(000016.SH)/沪深300(000300.SH)/中证500(000905.SH)/中证1000(000852.SH)/创业板指(399006.SZ)
- 每个快照日查每个指数的成分股
- 写入 index_constituent(trade_date, index_code, symbol, weight, action)

用法:
    python _fetch_index_constituent.py
    python _fetch_index_constituent.py --restart
    python _fetch_index_constituent.py --years 5

THS_DataPool 签名:
    THS_DataPool('index', '日期;指数代码', 'date:Y,thscode:Y,security_name:Y,weight:Y')
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, load_env, ch_insert_tsv, tsv_escape, load_progress, save_progress

log = setup_logging("fetch_index_constituent")
SLEEP_BETWEEN_CALLS = 1.5

# 主要宽基指数
INDEX_CODES = [
    ("000016.SH", "上证50"),
    ("000300.SH", "沪深300"),
    ("000905.SH", "中证500"),
    ("000852.SH", "中证1000"),
    ("399006.SZ", "创业板指"),
    ("399005.SZ", "中小板指"),
]

# 半年快照日期（倒序）
SNAPSHOT_DATES = []
for y in range(2026, 2009, -1):
    SNAPSHOT_DATES.append(f"{y}-06-30")
    SNAPSHOT_DATES.append(f"{y-1}-12-31")
# 去重保序
seen = set()
SNAPSHOT_DATES = [d for d in SNAPSHOT_DATES if not (d in seen or seen.add(d))]


def to_symbol(code):
    s = str(code).strip().upper()
    for pfx in (".SZ", ".SH", ".BJ", ".TI"):
        s = s.replace(pfx, "")
    for pfx in ("SH", "SZ", "BJ"):
        if s.startswith(pfx):
            s = s[len(pfx):]
    return s if s.isdigit() and len(s) == 6 else ""


def fetch_constituents(index_code: str, date: str):
    """获取某指数某日成分股。返回 [(symbol, weight), ...]。"""
    from iFinDPy import THS_DataPool
    try:
        data = THS_DataPool("index", f"{date};{index_code}",
                            "date:Y,thscode:Y,security_name:Y,weight:Y")
        table = data["tables"][0]["table"]
        codes = table["THSCODE"]
        weights = table.get("WEIGHT", table.get("weight", []))
        result = []
        for i, code in enumerate(codes):
            sym = to_symbol(code)
            if sym:
                w = weights[i] if i < len(weights) else ""
                result.append((sym, w))
        return result
    except Exception as e:
        log.warning(f"  {index_code} {date} 获取失败: {e}")
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--years", type=int)
    args = ap.parse_args()

    load_env()
    from iFinDPy import THS_iFinDLogin
    import os
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    dates = SNAPSHOT_DATES
    if args.years:
        dates = dates[:args.years * 2]
    log.info(f"快照日期数: {len(dates)}, 指数数: {len(INDEX_CODES)}")

    state = {} if args.restart else load_progress("fetch_index_constituent")
    last_key = state.get("last_key")  # "date|index_code"
    started = last_key is None

    for date in dates:
        for idx_code, idx_name in INDEX_CODES:
            key = f"{date}|{idx_code}"
            if not started:
                if key == last_key:
                    started = True
                continue
            log.info(f"获取 {idx_name}({idx_code}) @ {date}")
            members = fetch_constituents(idx_code, date)
            if members:
                lines = []
                for sym, w in members:
                    lines.append("\t".join([
                        date, idx_code, sym,
                        tsv_escape(w) if w else "0",
                        "",  # action 字段（加入/剔除），DataPool 不直接返回
                    ]))
                tsv = ("\n".join(lines) + "\n").encode("utf-8")
                if ch_insert_tsv("index_constituent", tsv):
                    log.info(f"  写入 {len(lines)} 行")
            else:
                log.info(f"  无数据")
            save_progress("fetch_index_constituent", {"last_key": key})
            time.sleep(SLEEP_BETWEEN_CALLS)

    log.info("指数成分股获取完成。")


if __name__ == "__main__":
    main()
