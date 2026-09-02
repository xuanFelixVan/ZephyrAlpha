# [BLUEPRINT] MOD-SCRIPT-crypto_daily_review | scripts/crypto_daily_review.py | §
# [MODULE] scripts.crypto_daily_review
# [DOMAIN] D_TRADING
# [DEPENDENCIES] stdlib only（json/argparse/datetime/decimal/pathlib——无第三方依赖，离线可跑）
# [CONSUMERS] 24/7 连续市场班次运营——UTC 三班（00:00/08:00/16:00）交接班人工触发入口（本脚本不挂任何调度）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读数据落盘件+写 Markdown 报告（不写任何业务 DB/数据文件）；数据缺失=降级标注"无数据（未接线）"不伪造空比对；窗口半开 [start,end) UTC 口径严格；幂等（同 date+shift 重跑覆盖同名报告无副作用）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=报告已生成（含降级标注场景）；exit 1=参数非法/报告写盘失败
# [TESTS] tests/scripts/test_crypto_daily_review.py
# [A_module] module_id=MOD-SCRIPT-crypto_daily_review | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是班次交接人工触发的复盘 CLI（手动按需运行，无常驻进程无定时轮询），与 run_post_settlement.py 同类
# @高风险动作: 无（只读数据文件 + 写 docs/_working/reports/ 下 Markdown 报告）
"""crypto_daily_review.py — UTC 日切复盘脚本（24/7 连续市场班次运营）

功能
----
按 UTC 日切三班（00:00/08:00/16:00）生成班次复盘 Markdown 报告：

``python scripts/crypto_daily_review.py [--date YYYY-MM-DD] [--shift 0|8|16]``

- ``--date``：复盘日（UTC 日历日），缺省=今日（UTC）。
- ``--shift``：班次起始 UTC 小时（0/8/16），缺省=0。班次窗口为半开区间
  ``[date shift:00 UTC, date shift+8:00 UTC)``——shift=16 时窗口止于次日 00:00 UTC。

复盘内容五节：持仓变化 / 成交记录 / 资金费率 / 信号验证 / 系统状态。

数据口径
--------
只读 JSONL 落盘件，目录约定 ``data/crypto/{category}/{YYYYMMDD}.jsonl``
（category ∈ positions/fills/funding/signals/system）。每行一条 JSON 记录，
必带 ``ts`` 字段（ISO 8601；无时区按 UTC 计）。各品类字段约定：

- positions: ``{ts, symbol, side: long|short, qty, action: open|close|increase|decrease, price?}``
- fills:     ``{ts, symbol, side: buy|sell, price, qty, fee?, trade_id?, order_id?}``
- funding:   ``{ts, symbol, rate, payment?}``
- signals:   ``{ts, symbol, signal, outcome: hit|miss|pending}``
- system:    ``{ts, component, status: ok|warn|error, message?}``

窗口覆盖时读取当日与次日两个 JSONL 后按 ts 过滤（shift=16 窗口跨日界）。
数据文件缺失=该节标注"无数据（未接线）"并记入报告标注节——降级是正常
路径非故障（对标 run_post_settlement.py QMT 降级语义），绝不拿空数据
硬算"零成交/零持仓"的假复盘。

输出
----
报告写至 ``docs/_working/reports/{date}-crypto-daily-review.md``（同 date
多班次共用一份文件——按 shift 顺序追加覆盖为最新生成班次，报告头标注班次；
同班次重跑幂等覆盖）。

exit code
---------
- 0 = 报告已生成（含部分/全部数据缺失的降级标注场景）
- 1 = 参数非法（date 格式/shift 取值）或报告写盘失败
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
# 脚本直跑（python scripts/xxx.py）时保证 src 布局可导入（冒烟脚本同口径）
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

#: 合法班次起始 UTC 小时（三班 8 小时制）
SHIFTS: tuple[int, ...] = (0, 8, 16)
#: 班时长（小时）
SHIFT_HOURS = 8
#: 数据品类（与 data/crypto/ 子目录一一对应）
CATEGORIES: tuple[str, ...] = ("positions", "fills", "funding", "signals", "system")
#: 严格 YYYY-MM-DD 格式（四-二-二位，连字符分隔）
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

#: 默认数据根目录（JSONL 落盘件）
_DEFAULT_DATA_ROOT = _REPO_ROOT / "data" / "crypto"
#: 默认报告输出目录
_DEFAULT_REPORT_DIR = _REPO_ROOT / "docs" / "_working" / "reports"

#: 持仓动作方向（open/increase=+qty，close/decrease=-qty）
_ACTION_SIGN = {"open": 1, "increase": 1, "close": -1, "decrease": -1}
#: 持仓方向符号（long=+，short=-）
_SIDE_SIGN = {"long": 1, "short": -1}


# ── 数据结构 ─────────────────────────────────────────────────────────────────


@dataclass
class ReviewResult:
    """一次班次复盘的产物容器。

    Attributes:
        review_date: 复盘日（UTC 日历日，YYYY-MM-DD）。
        shift: 班次起始 UTC 小时（0/8/16）。
        window_start/window_end: 复盘窗口（UTC aware，半开区间）。
        markdown: 渲染完成的报告正文。
        notes: 降级/缺口标注（写入报告"标注"节并打印 stdout）。
        report_path: 写盘后的报告路径（未写盘时 None）。
    """

    review_date: str
    shift: int
    window_start: datetime
    window_end: datetime
    markdown: str
    notes: list[str] = field(default_factory=list)
    report_path: Path | None = None


# ── CLI 参数与日期/班次解析 ──────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 参数解析（--date/--shift 均可选，缺省=今日 UTC + 0 班）。"""
    parser = argparse.ArgumentParser(
        prog="crypto_daily_review.py",
        description="UTC 日切复盘脚本（24/7 连续市场三班运营；只读数据+写 Markdown 报告）",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="复盘日 YYYY-MM-DD（UTC 日历日）；缺省=今日（UTC）",
    )
    parser.add_argument(
        "--shift",
        type=int,
        default=0,
        choices=SHIFTS,
        help="班次起始 UTC 小时（0/8/16）；缺省=0",
    )
    return parser.parse_args(argv)


def resolve_date(arg: str | None, *, today: date | None = None) -> str:
    """解析复盘日：显式入参做严格 YYYY-MM-DD 校验；缺省=今日（UTC）。

    Raises:
        ValueError: 入参格式非法/非合法日历日。
    """
    if arg is None:
        return (today or datetime.now(timezone.utc).date()).isoformat()
    if not _DATE_RE.fullmatch(arg):
        raise ValueError(f"--date 格式非法（期望 YYYY-MM-DD）: {arg!r}")
    try:
        parsed = date.fromisoformat(arg)
    except ValueError as exc:
        raise ValueError(f"--date 不是合法日历日（YYYY-MM-DD）: {arg!r}") from exc
    return parsed.isoformat()


def shift_window(review_date: str, shift: int) -> tuple[datetime, datetime]:
    """班次窗口：半开区间 [date shift:00 UTC, +8h)（shift=16 止于次日 00:00 UTC）。"""
    if shift not in SHIFTS:
        raise ValueError(f"--shift 取值非法（期望 0/8/16）: {shift!r}")
    day = date.fromisoformat(review_date)
    start = datetime(day.year, day.month, day.day, shift, tzinfo=timezone.utc)
    return start, start + timedelta(hours=SHIFT_HOURS)


# ── 数据读取与窗口过滤 ───────────────────────────────────────────────────────


def _parse_ts(value: object) -> datetime:
    """解析记录 ts 字段为 UTC aware datetime（无时区按 UTC 计）。"""
    if not isinstance(value, str):
        raise ValueError(f"ts 字段类型非法（期望 ISO 字符串）: {value!r}")
    ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def load_category_records(data_root: Path, category: str, review_date: str) -> tuple[list[dict], bool]:
    """读取某品类当日+次日 JSONL（窗口跨日界时次日 00:00 边界记录兜底）。

    Returns:
        (records, file_found)：records=全部解析成功记录（未按窗口过滤）；
        file_found=当日与次日文件至少一个存在（False=数据未接线，走降级标注）。
        坏行（JSON 解析失败/缺 ts）跳过不阻断——单条脏数据不拖垮整班复盘。
    """
    day = date.fromisoformat(review_date)
    records: list[dict] = []
    file_found = False
    for d in (day, day + timedelta(days=1)):
        path = data_root / category / f"{d.strftime('%Y%m%d')}.jsonl"
        if not path.is_file():
            continue
        file_found = True
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rec["_ts"] = _parse_ts(rec.get("ts"))
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
            records.append(rec)
    return records, file_found


def filter_window(records: list[dict], start: datetime, end: datetime) -> list[dict]:
    """按半开窗口 [start, end) 过滤（records 须已过 _parse_ts 注入 _ts）。"""
    return sorted(
        (r for r in records if start <= r["_ts"] < end),
        key=lambda r: r["_ts"],
    )


def _dec(value: object, *, default: str = "0") -> Decimal:
    """宽容解析数值为 Decimal（None/非法值→default，脏数据不阻断聚合）。"""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def _fmt(value: Decimal) -> str:
    """Decimal 报告格式化（去尾零，整数不带小数点）。"""
    normalized = value.normalize()
    # normalize 对 0 得 0，对大数可能给科学计数——定点化保报告可读
    return format(normalized, "f")


# ── 五节聚合 ─────────────────────────────────────────────────────────────────


def summarize_positions(records: list[dict]) -> dict:
    """持仓变化聚合：按 symbol 汇总开/减量与净方向变动。

    净变动符号约定：action open/increase=+、close/decrease=-；side long=+、short=-。
    """
    per_symbol: dict[str, dict[str, Decimal | int]] = {}
    for r in records:
        symbol = str(r.get("symbol", "?"))
        qty = _dec(r.get("qty"))
        action_sign = _ACTION_SIGN.get(str(r.get("action", "")).lower(), 0)
        side_sign = _SIDE_SIGN.get(str(r.get("side", "")).lower(), 1)
        entry = per_symbol.setdefault(
            symbol, {"events": 0, "opened": Decimal(0), "closed": Decimal(0), "net": Decimal(0)}
        )
        entry["events"] = int(entry["events"]) + 1
        if action_sign > 0:
            entry["opened"] = entry["opened"] + qty  # type: ignore[operator]
        elif action_sign < 0:
            entry["closed"] = entry["closed"] + qty  # type: ignore[operator]
        entry["net"] = entry["net"] + qty * action_sign * side_sign  # type: ignore[operator]
    return {"total_events": len(records), "per_symbol": per_symbol}


def summarize_fills(records: list[dict]) -> dict:
    """成交记录聚合：笔数/买卖方向/名义额/手续费，含 per-symbol 明细。"""
    per_symbol: dict[str, dict[str, Decimal | int]] = {}
    buy_count = sell_count = 0
    total_notional = Decimal(0)
    total_fees = Decimal(0)
    for r in records:
        symbol = str(r.get("symbol", "?"))
        side = str(r.get("side", "")).lower()
        price = _dec(r.get("price"))
        qty = _dec(r.get("qty"))
        fee = _dec(r.get("fee"))
        notional = price * qty
        if side == "buy":
            buy_count += 1
        elif side == "sell":
            sell_count += 1
        total_notional += notional
        total_fees += fee
        entry = per_symbol.setdefault(
            symbol,
            {"count": 0, "buy_qty": Decimal(0), "sell_qty": Decimal(0), "notional": Decimal(0), "fees": Decimal(0)},
        )
        entry["count"] = int(entry["count"]) + 1
        if side == "buy":
            entry["buy_qty"] = entry["buy_qty"] + qty  # type: ignore[operator]
        elif side == "sell":
            entry["sell_qty"] = entry["sell_qty"] + qty  # type: ignore[operator]
        entry["notional"] = entry["notional"] + notional  # type: ignore[operator]
        entry["fees"] = entry["fees"] + fee  # type: ignore[operator]
    return {
        "total": len(records),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "total_notional": total_notional,
        "total_fees": total_fees,
        "per_symbol": per_symbol,
    }


def summarize_funding(records: list[dict]) -> dict:
    """资金费率聚合：per-symbol 均值/最新/极值与支付合计。"""
    per_symbol: dict[str, dict] = {}
    for r in records:
        symbol = str(r.get("symbol", "?"))
        rate = _dec(r.get("rate"))
        payment = _dec(r.get("payment"))
        entry = per_symbol.setdefault(
            symbol,
            {
                "count": 0,
                "rate_sum": Decimal(0),
                "latest_rate": Decimal(0),
                "min": rate,
                "max": rate,
                "payment_sum": Decimal(0),
                "_latest_ts": None,
            },
        )
        entry["count"] += 1
        entry["rate_sum"] += rate
        entry["payment_sum"] += payment
        entry["min"] = min(entry["min"], rate)
        entry["max"] = max(entry["max"], rate)
        if entry["_latest_ts"] is None or r["_ts"] >= entry["_latest_ts"]:
            entry["_latest_ts"] = r["_ts"]
            entry["latest_rate"] = rate
    for entry in per_symbol.values():
        entry["avg_rate"] = entry["rate_sum"] / entry["count"] if entry["count"] else Decimal(0)
    return {"total_events": len(records), "per_symbol": per_symbol}


def summarize_signals(records: list[dict]) -> dict:
    """信号验证聚合：outcome 计数与命中率（pending 不计入命中率分母）。"""
    hits = misses = pending = 0
    for r in records:
        outcome = str(r.get("outcome", "")).lower()
        if outcome == "hit":
            hits += 1
        elif outcome == "miss":
            misses += 1
        else:
            pending += 1
    resolved = hits + misses
    return {
        "total": len(records),
        "hits": hits,
        "misses": misses,
        "pending": pending,
        "hit_rate": (Decimal(hits) / Decimal(resolved)) if resolved else None,
    }


def summarize_system(records: list[dict]) -> dict:
    """系统状态聚合：按 status 计数，整体状态取最差（error>warn>ok），留末 5 条事件。"""
    counts = {"ok": 0, "warn": 0, "error": 0, "unknown": 0}
    for r in records:
        status = str(r.get("status", "")).lower()
        counts[status if status in counts else "unknown"] += 1
    if counts["error"]:
        overall = "error"
    elif counts["warn"]:
        overall = "warn"
    elif records:
        overall = "ok"
    else:
        overall = "unknown"
    latest = [
        {
            "ts": r["_ts"].isoformat(),
            "component": str(r.get("component", "?")),
            "status": str(r.get("status", "?")),
            "message": str(r.get("message", "")),
        }
        for r in records[-5:]
    ]
    return {"total_events": len(records), "counts": counts, "overall": overall, "latest": latest}


# ── Markdown 渲染 ────────────────────────────────────────────────────────────


def _render_positions_section(records: list[dict] | None) -> list[str]:
    if records is None:
        return ["_无数据（未接线）_"]
    summary = summarize_positions(records)
    lines = [f"本班持仓变动事件：**{summary['total_events']}** 笔", ""]
    if summary["per_symbol"]:
        lines += [
            "| 标的 | 事件数 | 开/加量 | 平/减量 | 净方向变动 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for symbol, e in sorted(summary["per_symbol"].items()):
            lines.append(f"| {symbol} | {e['events']} | {_fmt(e['opened'])} | {_fmt(e['closed'])} | {_fmt(e['net'])} |")
    else:
        lines.append("本班无持仓变动。")
    return lines


def _render_fills_section(records: list[dict] | None) -> list[str]:
    if records is None:
        return ["_无数据（未接线）_"]
    s = summarize_fills(records)
    lines = [
        f"本班成交：**{s['total']}** 笔（买 {s['buy_count']} / 卖 {s['sell_count']}）",
        f"- 名义额合计：{_fmt(s['total_notional'])}",
        f"- 手续费合计：{_fmt(s['total_fees'])}",
        "",
    ]
    if s["per_symbol"]:
        lines += [
            "| 标的 | 笔数 | 买量 | 卖量 | 名义额 | 手续费 |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for symbol, e in sorted(s["per_symbol"].items()):
            lines.append(
                f"| {symbol} | {e['count']} | {_fmt(e['buy_qty'])} | {_fmt(e['sell_qty'])} | {_fmt(e['notional'])} | {_fmt(e['fees'])} |"
            )
    else:
        lines.append("本班无成交。")
    return lines


def _render_funding_section(records: list[dict] | None) -> list[str]:
    if records is None:
        return ["_无数据（未接线）_"]
    s = summarize_funding(records)
    lines = [f"本班资金费率事件：**{s['total_events']}** 条", ""]
    if s["per_symbol"]:
        lines += [
            "| 标的 | 条数 | 平均费率 | 最新费率 | 最低 | 最高 | 支付合计 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for symbol, e in sorted(s["per_symbol"].items()):
            lines.append(
                f"| {symbol} | {e['count']} | {_fmt(e['avg_rate'])} | {_fmt(e['latest_rate'])} "
                f"| {_fmt(e['min'])} | {_fmt(e['max'])} | {_fmt(e['payment_sum'])} |"
            )
    else:
        lines.append("本班无资金费率事件。")
    return lines


def _render_signals_section(records: list[dict] | None) -> list[str]:
    if records is None:
        return ["_无数据（未接线）_"]
    s = summarize_signals(records)
    hit_rate = f"{_fmt(s['hit_rate'] * 100)}%" if s["hit_rate"] is not None else "—（无已验证信号）"
    return [
        f"本班信号：**{s['total']}** 条（命中 {s['hits']} / 未命中 {s['misses']} / 待验证 {s['pending']}）",
        f"- 命中率（已验证口径）：{hit_rate}",
    ]


def _render_system_section(records: list[dict] | None) -> list[str]:
    if records is None:
        return ["_无数据（未接线）_"]
    s = summarize_system(records)
    c = s["counts"]
    lines = [
        f"整体状态：**{s['overall']}**（ok {c['ok']} / warn {c['warn']} / error {c['error']} / unknown {c['unknown']}）",
        "",
    ]
    if s["latest"]:
        lines += [
            "| 时间 (UTC) | 组件 | 状态 | 消息 |",
            "| --- | --- | --- | --- |",
        ]
        for e in s["latest"]:
            lines.append(f"| {e['ts']} | {e['component']} | {e['status']} | {e['message']} |")
    else:
        lines.append("本班无系统状态事件。")
    return lines


def render_markdown(
    review_date: str,
    shift: int,
    window_start: datetime,
    window_end: datetime,
    sections: dict[str, list[dict] | None],
    notes: list[str],
    *,
    generated_at: datetime | None = None,
) -> str:
    """渲染班次复盘 Markdown（sections 值 None=该品类数据未接线走降级标注）。"""
    generated_at = generated_at or datetime.now(timezone.utc)
    end_label = (
        f"次日 {window_end.strftime('%H:%M')}"
        if window_end.date() > window_start.date()
        else window_end.strftime("%H:%M")
    )
    lines = [
        f"# UTC 日切复盘报告 — {review_date} 班次 {shift:02d}:00 UTC",
        "",
        f"- 复盘日（UTC）：{review_date}",
        f"- 班次：{shift:02d}:00–{end_label} UTC（24/7 三班制）",
        f"- 复盘窗口：`[{window_start.isoformat()}, {window_end.isoformat()})`",
        f"- 生成时间（UTC）：{generated_at.isoformat(timespec='seconds')}",
        "",
        "## 1. 持仓变化",
        "",
        *_render_positions_section(sections["positions"]),
        "",
        "## 2. 成交记录",
        "",
        *_render_fills_section(sections["fills"]),
        "",
        "## 3. 资金费率",
        "",
        *_render_funding_section(sections["funding"]),
        "",
        "## 4. 信号验证",
        "",
        *_render_signals_section(sections["signals"]),
        "",
        "## 5. 系统状态",
        "",
        *_render_system_section(sections["system"]),
        "",
        "## 标注",
        "",
    ]
    if notes:
        lines += [f"- {n}" for n in notes]
    else:
        lines.append("- （无）")
    lines.append("")
    return "\n".join(lines)


# ── 复盘构建与写盘 ───────────────────────────────────────────────────────────


def build_review(
    review_date: str,
    shift: int,
    *,
    data_root: Path,
    generated_at: datetime | None = None,
) -> ReviewResult:
    """构建班次复盘：读五品类数据 → 窗口过滤 → 聚合 → 渲染 Markdown。

    数据文件缺失的品类以 None 入 sections（渲染为"无数据（未接线）"）并记标注——
    降级是正常路径非故障。
    """
    start, end = shift_window(review_date, shift)
    sections: dict[str, list[dict] | None] = {}
    notes: list[str] = []
    for category in CATEGORIES:
        records, file_found = load_category_records(data_root, category, review_date)
        if not file_found:
            sections[category] = None
            notes.append(
                f"{category} 数据缺失（{data_root / category} 无当日/次日 JSONL）——该节未接线，不构成'零发生'口径"
            )
        else:
            sections[category] = filter_window(records, start, end)
    markdown = render_markdown(review_date, shift, start, end, sections, notes, generated_at=generated_at)
    return ReviewResult(
        review_date=review_date,
        shift=shift,
        window_start=start,
        window_end=end,
        markdown=markdown,
        notes=notes,
    )


def report_filename(review_date: str) -> str:
    """报告文件名口径：YYYY-MM-DD-crypto-daily-review.md。"""
    return f"{review_date}-crypto-daily-review.md"


def write_report(report_dir: Path, result: ReviewResult) -> Path:
    """写报告到 {report_dir}/{date}-crypto-daily-review.md（目录不存在则创建；同名幂等覆盖）。"""
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / report_filename(result.review_date)
    path.write_text(result.markdown, encoding="utf-8")
    result.report_path = path
    return path


# ── 主入口 ───────────────────────────────────────────────────────────────────


def main(
    argv: list[str] | None = None,
    *,
    data_root: Path | None = None,
    report_dir: Path | None = None,
    today: date | None = None,
) -> int:
    """CLI 主入口。

    Args:
        argv: 命令行参数（None=sys.argv）。
        data_root/report_dir: 测试注入隔离目录（None=生产默认 data/crypto 与
            docs/_working/reports）。
        today: 复盘日缺省基准（测试注入用；None=今日 UTC）。

    Returns:
        exit code（0=报告已生成，1=参数非法/写盘失败）。
    """
    args = parse_args(argv)
    try:
        review_date = resolve_date(args.date, today=today)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1
    shift = args.shift  # argparse choices 已卡 0/8/16

    result = build_review(
        review_date,
        shift,
        data_root=data_root or _DEFAULT_DATA_ROOT,
    )
    try:
        path = write_report(report_dir or _DEFAULT_REPORT_DIR, result)
    except OSError as exc:
        print(f"[ERROR] 报告写盘失败: {exc}")
        return 1

    print(f"[INFO] 复盘窗口: [{result.window_start.isoformat()}, {result.window_end.isoformat()})")
    for note in result.notes:
        print(f"[标注] {note}")
    print(f"[INFO] 报告已生成: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
