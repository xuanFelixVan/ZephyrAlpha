# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] scripts.data.backfill_kline_daily_history
# [DOMAIN] D_DATA
# [A_module] module_id=scripts-data-kline-daily-history-backfill | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.buffered_writer; zephyr.data.implementations.baostock_provider; zephyr.data.provider_base; zephyr.data.table_registry
# [CONSUMERS] Owner/施工会话手动补数（2026-10-12 统筹裁定②：窗口化在市股历史回填立在册；首件=段二 2017-2018 价量半边）
# [STARTUP] manual
# [MATURITY] candidate
# [INVARIANTS] 取数与换算全走生产 BaostockProvider.fetch(capability='kline_daily')——不复权 adjustflag=3（#196 主口径）、
#  volume/amount 用 baostock 原生"股/元"（与 2026-09-22 批10 量纲治本后的 kline_daily 主口径一致），本件零自算换算；
#  写入走 BufferedWriter 正门（裁定 #ARCH-CH-003 批量），禁手写 INSERT；
#  ReplacingMergeTree 同键 (trade_date,symbol) 覆盖幂等可重跑；分片按票集互斥（禁双开实质判据），单进程内串行；
#  续跑=state 文件逐票记完成，重跑只补未完成的票；dry-run 不落库。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FetchResult.error 计数并进失败清单（单票隔离，不污染他票）；BufferedWriter.add/flush 失败即 RuntimeError 非零退出；
#  收尾打印 failed=N，N>0 时退出码 1（重跑同一命令即自愈，因 state 只跳过已完成票）
# [TESTS] tests/data/data/data/test_backfill_kline_daily_history_window.py（窗口/续跑/量纲三条钉：给定 symbols-file 与窗口断言 payload 形状、state 跳过重跑、行序与 provider.columns 对齐且 data_source='Baostock'）
# noqa: m11-perm-manual-legitimate  历史窗口回填属手动运维件（人工触发是设计意图），常驻供数由 kline_daily_incremental 与 kline_daily_delisted_backfill 承担
"""A 股日K线历史窗口回填器（按票清单＋起止日，走生产 provider→BufferedWriter 同链路）。

背景（2026-10-12 实测）：c1_market.kline_daily 在 2016-2018 是 240 票级 stub（2017=240/2018=237，
data_source='Baostock'，量纲已=股/元），而 2019 起才 3,771/4,366 票——"表面 1990 起实则 237 票"的
假完整在档三次记录。调度闭环里没有"按窗口给在市股补历史日线"的入口：kline_daily_incremental 是
miniqmt 水位日增、integrator 的 run 子命令只有"今天"语义、kline_daily_delisted_backfill 只覆盖退市股
且 incremental=false（首跑=数千票×30 年全史）。本件把"窗口＋票清单"这一格补齐，取数与换算零自算，
全部复用 BaostockProvider 的在册 kline_daily 能力（该能力 supports_symbols_null=False，本就要求显式票清单）。

用法：
    python scripts/data/backfill_kline_daily_history.py --start 2017-01-01 --end 2018-12-31 \
        --symbols-file .runtime/tmp/<sid>/seg2/universe_part1.txt \
        --state-file .runtime/tmp/<sid>/seg2/state_part1.txt --dry-run
    # 去掉 --dry-run 即落库；重跑同一命令只补 state 里没有的票（自愈）

票清单格式：一行一个代码，接受 baostock 形（sh.600000/sz.000001）或 6 位纯码（自动补交易所前缀，
前缀集与在册 _DELISTED_A_PREFIXES 同族：60/68→sh，00/30→sz；其余判"不支持"计入失败清单不静默吞）。

单位与口径：本件不换算 volume/amount（baostock 原生股/元）；不复权（adjustflag=3）；turnover/
market_type/quality_flag/adj_factor 由表 DEFAULT 填充（与在册 kline_daily 写腿同款缺省语义）。
"""

from __future__ import annotations

import argparse
import datetime
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.data.buffered_writer import BufferedWriter  # noqa: E402
from zephyr.data.implementations.baostock_provider import BaostockProvider  # noqa: E402
from zephyr.data.provider_base import FetchPayload  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

TABLE = str(get_registry().table("market_kline_daily"))
_PREFIX = {"60": "sh.", "68": "sh.", "00": "sz.", "30": "sz."}


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def to_bs_code(raw: str) -> str | None:
    """票清单归一为 baostock 码；无法归一返回 None（调用方计入失败清单，不静默吞）。"""
    s = raw.strip().lower()
    if not s:
        return None
    if "." in s:
        pref, _, six = s.partition(".")
        if pref not in ("sh", "sz", "bj"):
            return None
        if pref == "bj":
            return s  # 北交所 baostock 无覆盖为在册已知缺口，原样交给 provider 判空
        return s if six[:2] in _PREFIX else None
    if len(s) == 6 and s[:2] in _PREFIX:
        return f"{_PREFIX[s[:2]]}{s}"
    return None


def load_symbols(path: Path) -> tuple[list[str], list[str]]:
    codes: list[str] = []
    bad: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        code = to_bs_code(line)
        (codes if code else bad).append(code or line.strip())
    return codes, bad


def done_set(state_file: Path) -> set[str]:
    if not state_file.exists():
        return set()
    return {ln.strip() for ln in state_file.read_text(encoding="utf-8").splitlines() if ln.strip()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="窗口起日 YYYY-MM-DD（含）")
    ap.add_argument("--end", required=True, help="窗口止日 YYYY-MM-DD（含）")
    ap.add_argument("--symbols-file", required=True, help="票清单（baostock 码或 6 位纯码，一行一个）")
    ap.add_argument("--state-file", required=True, help="逐票完成态（续跑/自愈判据）")
    ap.add_argument("--sleep", type=float, default=0.05, help="每票间隔秒（baostock 有 IP 拉黑前科，勿置零放量）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 票（试点用，0=全跑）")
    ap.add_argument("--dry-run", action="store_true", help="只取数与打印，不落库不写 state")
    args = ap.parse_args()

    start = datetime.date.fromisoformat(args.start)
    end = datetime.date.fromisoformat(args.end)
    symbols, bad = load_symbols(Path(args.symbols_file))
    done = done_set(Path(args.state_file))
    todo = [s for s in symbols if s not in done]
    if args.limit > 0:
        todo = todo[: args.limit]
    log(
        f"START table={TABLE} window={start}..{end} list={args.symbols_file} "
        f"parsed={len(symbols)} unparsable={len(bad)} already_done={len(done)} to_run={len(todo)} dry_run={args.dry_run}"
    )
    if bad:
        log(f"UNPARSABLE（未取数未写库，样例 {bad[:5]}）")

    provider = BaostockProvider()
    provider.connect()
    state_fh = None if args.dry_run else open(args.state_file, "a", encoding="utf-8")  # noqa: SIM115
    writer = BufferedWriter(TABLE, max_seconds=30)
    rows_written = ok_n = fail_n = zero_n = 0
    zero_path = Path(args.state_file).with_name(Path(args.state_file).name + ".zero_row.txt")
    zero_fh = None if args.dry_run else open(zero_path, "a", encoding="utf-8")  # noqa: SIM115
    t_all = time.monotonic()
    try:
        for i, code in enumerate(todo, 1):
            payload = FetchPayload(
                table=get_registry().table("market_kline_daily"),
                symbols=[code],
                start=start,
                end=end,
                incremental=False,
                extra={"capability": "kline_daily"},
            )
            failed: str | None = None
            n_rows = 0
            yielded = False
            for result in provider.fetch(payload, None):
                yielded = True
                if result.error:
                    failed = str(result.error)[:160]
                    break
                n_rows += len(result.rows)
                if not args.dry_run and result.rows:
                    if not writer.add(result):
                        raise RuntimeError(f"BufferedWriter.add 失败 code={code}（非零退出，state 未记该票）")
            if failed:
                fail_n += 1
                log(f"  [{i}/{len(todo)}] {code} FAIL {failed}")
                continue
            if not yielded or n_rows == 0:
                # 在册 provider 的这段循环是 `while rs.error_code=='0' and rs.next()`：
                # baostock 返回 error_code!=0（限流/IP 黑名单 10001011）时既不给行也不给 error，
                # 与"窗口内真无行情"同形。票单里每只都应在窗口内有行 ⇒ 零行一律按未完成处理，
                # 不写 state（下一轮自愈会重试），并单独计数，绝不计成成功。
                zero_n += 1
                if zero_fh is not None:
                    zero_fh.write(code + "\n")
                    zero_fh.flush()
                continue
            ok_n += 1
            rows_written += n_rows
            if state_fh is not None:
                state_fh.write(code + "\n")
                state_fh.flush()
            if i % 25 == 0:
                rate = i / max(time.monotonic() - t_all, 0.001)
                log(
                    f"  progress {i}/{len(todo)} ok={ok_n} fail={fail_n} zero={zero_n} rows={rows_written} "
                    f"last={code} rate={rate:.2f}/s eta={(len(todo) - i) / max(rate, 0.01) / 60:.0f}min"
                )
            time.sleep(args.sleep)  # noqa: m10-time-trigger  逐票节流等待（baostock 有 IP 拉黑前科），手动运维件一次性限速，非周期轮询常驻
        if not args.dry_run:
            if not writer.flush():
                raise RuntimeError("BufferedWriter.flush 失败（未落库部分不得宣称完成）")
            rows_flushed = writer.total_flushed
            log(f"FLUSHED total={rows_flushed} pending_at_exit={writer.pending_rows}")
    finally:
        if state_fh is not None:
            state_fh.close()
        if zero_fh is not None:
            zero_fh.close()
        provider.disconnect()

    log(
        f"DONE dry_run={args.dry_run} ok={ok_n} fail={fail_n} zero_row_unconfirmed={zero_n} "
        f"zero_list={'' if args.dry_run else zero_path} "
        f"rows={'(dry-run 未落库)' if args.dry_run else rows_written} "
        f"elapsed={(time.monotonic() - t_all) / 60:.1f}min"
    )
    return 1 if (fail_n or zero_n) else 0


if __name__ == "__main__":
    sys.exit(main())
