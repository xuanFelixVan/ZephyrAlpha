# [BLUEPRINT] MOD-QCURE-OFFSET | scripts/governance/qcure_offset_report.py | §对消报表
# [MODULE] scripts.governance.qcure_offset_report
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；scripts.commit_queue.classify_dead_reason（死因三分类唯一真源，经 importlib 文件加载复用，禁第二分类器）
# [CONSUMERS] QCure 战役总包（st-qcure-20260925 验收 §4-2"死信率下降"对消证据）；AI session 按需 CLI
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全程只读生产数据（.runtime/commit_queue/dead/ 与 .runtime/audit/preflight_events.jsonl 零写触；缺省输出 stdout，永不落盘 .runtime）；族判定唯一入口=classify_dead_reason（预检 gate 名仅做"连字符→下划线"字符串拼接后喂同一函数，供 gate ID 与 reason 标记两种命名风格匹配，不构成第二分类器）；周窗=7 天滚动半开桶 [start,end)，W1=最近一周；对消率口径=预检拦截÷(预检拦截+死信)，越高=失败越早被预检吸收未坠死信；账本缺行/坏行降级跳过并如实计数，零数据=诚实零
# [MODIFY-GUARD] none（只读报表生成器；观测簿 §3 矿脉1 / QCure 方案 §4-2 对消仪表落地件）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 账本文件缺失→按空账处理照常出表；单行/单文件 JSON 损坏→跳过计入 skipped 不中断；--out 写失败→exit 1；classify 加载失败（commit_queue.py 缺失）→exit 2 拒绝出表（禁无分类器出数）
# [TESTS] tests/governance/test_qcure_offset_report.py
# [A_module] module_id=QCURE-OBS-1 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""qcure_offset_report.py — 死信×预检对消周报生成器（QCure 观测线验收承重件，生产数据只读）。

背景：观测簿 §3 矿脉1 —— QCure 方案 §4-2 要求"周窗 preflight 拒收 vs dead/ 新增按死因族
对消"，此前全仓无任何机械可出此数（静态清单禁手工维护铁律 §9-5，故必须生成器）。

用法（仓库根，Python 3.12）：
    python scripts/governance/qcure_offset_report.py                # 近 2 周，stdout
    python scripts/governance/qcure_offset_report.py --weeks 4      # 近 4 周
    python scripts/governance/qcure_offset_report.py --out PATH     # 显式传参才落盘
                      （写 .runtime/tmp/ 须显式传参，本脚本自身绝不默认写 .runtime）
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — SSOT canonical（禁自建第二真源）

DEAD_DIR = REPO_ROOT / ".runtime" / "commit_queue" / "dead"
PREFLIGHT_PATH = REPO_ROOT / ".runtime" / "audit" / "preflight_events.jsonl"

# 族中文名对照（对齐 classify_dead_reason docstring 术语，一处注解不做翻译字典）
FAMILY_LABELS = {"env": "env（环境性）", "item": "item（物品性）", "other": "other（其他）"}
_WEEK = timedelta(days=7)
_REASON_TRUNC = 120  # 高频死因榜单里截断展示的字符数


def load_classifier():
    """importlib 文件加载 scripts/commit_queue.py，复用 classify_dead_reason（禁第二分类器）。"""
    cq_path = REPO_ROOT / "scripts" / "commit_queue.py"
    spec = importlib.util.spec_from_file_location("_qcure_offset_cq", cq_path)
    if spec is None or spec.loader is None:  # pragma: no cover — 路径恒存在，防御性
        raise RuntimeError(f"无法加载分类器真源: {cq_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.classify_dead_reason


def _parse_ts(raw: str) -> datetime | None:
    """解析账本时间戳（dead_at=本地带时区 / preflight=UTC 带时区）；naive 视为本地时区。"""
    try:
        ts = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return None
    return ts if ts.tzinfo else ts.astimezone()


def build_report(
    weeks: int = 2,
    *,
    dead_dir: Path | None = None,
    preflight_path: Path | None = None,
    now: datetime | None = None,
    classify=None,
) -> dict:
    """聚合周窗数据并返回报表结构（纯函数面，I/O 收敛在两本账读取）。"""
    if weeks < 1:
        raise ValueError("weeks 必须 >= 1")
    classify = classify or load_classifier()  # 惰性加载：分类器真源缺失则 RuntimeError 上抛
    now = now or datetime.now().astimezone()
    # 周桶：W1=最近一周 [now-7d, now)，W2=[now-14d, now-7d) …… 半开区间不重不漏
    buckets = [(f"W{i}", now - _WEEK * i, now - _WEEK * (i - 1)) for i in range(1, weeks + 1)]

    def bucket_of(ts: datetime) -> str | None:
        for label, start, end in buckets:
            if start <= ts < end:
                return label
        return None

    dead: Counter = Counter()  # (week, family) -> 死信数
    blocked: Counter = Counter()  # (week, family) -> 预检拦截数
    skipped = {"dead": 0, "preflight": 0}
    scanned = {"dead": 0, "preflight": 0}
    top_reasons: Counter = Counter()

    requeued = _aggregate_dead_ledger(dead_dir or DEAD_DIR, bucket_of, classify, dead, top_reasons, scanned, skipped)
    _aggregate_preflight_ledger(preflight_path or PREFLIGHT_PATH, bucket_of, classify, blocked, scanned, skipped)
    rows = _build_rows(dead, blocked, buckets)
    grand_dead = sum(r["dead"] for r in rows)
    grand_blocked = sum(r["blocked"] for r in rows)
    grand_denom = grand_dead + grand_blocked
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "weeks": weeks,
        "window": (buckets[-1][1], buckets[0][2]),
        "week_labels": [(label, start, end) for label, start, end in buckets],
        "scanned": scanned,
        "skipped": skipped,
        "requeued": requeued,
        "rows": rows,
        "grand": {
            "dead": grand_dead,
            "blocked": grand_blocked,
            "ratio": f"{grand_blocked / grand_denom * 100:.1f}%" if grand_denom else "n/a",
        },
        "top_reasons": top_reasons.most_common(5),
    }


def _aggregate_dead_ledger(
    dead_dir: Path,
    bucket_of,
    classify,
    dead: Counter,
    top_reasons: Counter,
    scanned: dict,
    skipped: dict,
) -> int:
    """死信账聚合（dead/q-*.json 顶层散件；archive_* 子目录刻意不计——封存非增量）。"""
    requeued = 0
    if not dead_dir.is_dir():
        return requeued
    for entry in sorted(dead_dir.glob("q-*.json")):
        if not entry.is_file():
            continue
        scanned["dead"] += 1
        try:
            item = json.loads(entry.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            skipped["dead"] += 1
            continue
        ts = _parse_ts(item.get("dead_at", ""))
        if ts is None:
            skipped["dead"] += 1
            continue
        week = bucket_of(ts)
        if week is None:
            continue  # 窗外死信不计（历史存量，非本窗增量）
        family = classify(item.get("dead_reason", ""))
        dead[(week, family)] += 1
        top_reasons[(family, item.get("dead_reason", ""))] += 1
        if item.get("requeued"):
            requeued += 1
    return requeued


def _aggregate_preflight_ledger(
    preflight_path: Path,
    bucket_of,
    classify,
    blocked: Counter,
    scanned: dict,
    skipped: dict,
) -> None:
    """预检账聚合（preflight_events.jsonl，仅 event=blocked 行参与对消）。"""
    if not preflight_path.is_file():
        return
    for line in preflight_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        scanned["preflight"] += 1
        try:
            event = json.loads(line)
        except ValueError:
            skipped["preflight"] += 1
            continue
        if event.get("event") != "blocked":
            continue
        ts = _parse_ts(event.get("timestamp", ""))
        if ts is None:
            skipped["preflight"] += 1
            continue
        week = bucket_of(ts)
        if week is None:
            continue
        gates = [str(g) for g in event.get("gates_failed") or []]
        # gate ID 是连字符命名（COMMIT-SCOPE），死因标记是下划线命名（COMMIT_SCOPE）：
        # 两形态拼接后仍只由 classify_dead_reason 单点判定，非第二分类器。
        probe = ";".join(gates) + ";" + ";".join(g.replace("-", "_") for g in gates)
        blocked[(week, classify(probe))] += 1


def _build_rows(dead: Counter, blocked: Counter, buckets: list) -> list[dict]:
    """按死因族出对消行（比率+趋势）。"""
    families = ("env", "item", "other")
    weeks_labels = [label for label, _, _ in buckets]
    rows = []
    for family in families:
        dead_total = sum(dead[(w, family)] for w in weeks_labels)
        blocked_total = sum(blocked[(w, family)] for w in weeks_labels)
        denom = dead_total + blocked_total
        ratio = f"{blocked_total / denom * 100:.1f}%" if denom else "n/a"
        latest = dead[(weeks_labels[0], family)]
        prior = dead[(weeks_labels[1], family)] if len(weeks_labels) > 1 else None
        if prior is None:
            trend = "—"
        elif latest > prior:
            trend = f"↑ {prior}->{latest}"
        elif latest < prior:
            trend = f"↓ {prior}->{latest}"
        else:
            trend = f"→ {prior}->{latest}"
        rows.append(
            {
                "family": family,
                "label": FAMILY_LABELS[family],
                "dead": dead_total,
                "blocked": blocked_total,
                "ratio": ratio,
                "trend": trend,
                "per_week": {w: (dead[(w, family)], blocked[(w, family)]) for w in weeks_labels},
            }
        )
    return rows


def render_markdown(report: dict) -> str:
    """报表结构 → markdown 对照表（验收 §4-2 承重输出）。"""
    start, end = report["window"]
    lines = [
        "# QCure 死信×预检对消报表（对消仪表）",
        "",
        f"- 生成时刻: {report['generated_at']}（qcure_offset_report.py，生产数据只读）",
        f"- 周窗: 近 {report['weeks']} 周（{start:%Y-%m-%d %H:%M} ~ {end:%Y-%m-%d %H:%M}，7 天滚动桶，W1=最近一周）",
        f"- 数据源: dead/ 扫描 {report['scanned']['dead']} 项、preflight_events 扫描 "
        f"{report['scanned']['preflight']} 行（损坏跳过: dead "
        f"{report['skipped']['dead']} / preflight {report['skipped']['preflight']}）",
        f"- 死信复活: {report['requeued']} 项带 requeued 标记（死信后已转运重排，非终态）",
        "- 口径: 族判定唯一真源=commit_queue.classify_dead_reason；"
        "对消率=预检拦截÷(预检拦截+死信)，越高=失败越早被预检吸收",
        "",
        "| 死因族 | 死信数 | 预检拦截数 | 对消率 | 趋势（死信 环比上周） |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(f"| {row['label']} | {row['dead']} | {row['blocked']} | {row['ratio']} | {row['trend']} |")
    g = report["grand"]
    lines.append(f"| 合计 | {g['dead']} | {g['blocked']} | {g['ratio']} | — |")
    lines += ["", "## 周粒度明细（每格=死信/预检拦截）", ""]
    header = (
        "| 死因族 | "
        + " | ".join(f"{label}（{start:%m-%d}~{end:%m-%d}）" for label, start, end in report["week_labels"])
        + " |"
    )
    lines.append(header)
    lines.append("|---|" + "---:|" * len(report["week_labels"]))
    for row in report["rows"]:
        cells = " | ".join(f"{d}/{b}" for d, b in (row["per_week"][label] for label, _, _ in report["week_labels"]))
        lines.append(f"| {row['label']} | {cells} |")
    if report["top_reasons"]:
        lines += ["", "## 高频死因 Top5（近窗全族）", "", "| 次数 | 族 | 死因（截断） |", "|---:|---|---|"]
        for (family, reason), n in report["top_reasons"]:
            reason_short = reason.replace("|", "\\|")[:_REASON_TRUNC]
            lines.append(f"| {n} | {FAMILY_LABELS[family]} | {reason_short} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None, *, dead_dir=None, preflight_path=None, now=None) -> int:
    parser = argparse.ArgumentParser(description="死信×预检对消周报（只读；缺省输出 stdout）")
    parser.add_argument("--weeks", type=int, default=2, help="周窗周数（默认 2）")
    parser.add_argument(
        "--out", type=Path, default=None, help="输出文件路径（缺省 stdout；写 .runtime/tmp/ 须显式传参）"
    )
    args = parser.parse_args(argv)
    try:
        report = build_report(args.weeks, dead_dir=dead_dir, preflight_path=preflight_path, now=now)
    except ValueError as exc:
        print(f"[offset-report] 参数错误: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:  # 分类器真源（commit_queue.py）不可加载——禁无分类器出数
        print(f"[offset-report] 分类器加载失败: {exc}", file=sys.stderr)
        return 2
    text = render_markdown(report)
    if args.out is None:
        sys.stdout.write(text)
        return 0
    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")  # 报表产物非热文件（非注册表/宪法/tracker 面）
        verified = args.out.read_text(encoding="utf-8")  # 写后读回核实（宪法 §1-13 同精神）
        if verified != text:
            print("[offset-report] 写回核验不一致", file=sys.stderr)
            return 1
    except OSError as exc:
        print(f"[offset-report] 输出写失败: {exc}", file=sys.stderr)
        return 1
    print(f"[offset-report] 已写出: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
