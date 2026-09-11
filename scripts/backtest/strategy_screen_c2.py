# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.strategy_screen_c2
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] SOP-C Step C2（粗筛出局）; C3 翻译适配（消费 candidate 清单）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 硬排除=SOP-C §2 四类判据（非股票标的/非日线级/结构不可迁移/演示作业）; 机器启发式只做第一遍——命中判据才出局，模棱两可一律 candidate 待人工/AI 复核（宁漏勿误）; 原文件只读; 结果落 data/strategy_intake/screen_c2.csv（gitignore 区）不回写 manifest
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] manifest 缺失->退出码2; 无出局也不报错（退出码0）
# [TESTS] python scripts/backtest/strategy_screen_c2.py (smoke)
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  SOP-C C2 粗筛 CLI 工具（代码归类表 A 类运维脚本），非常驻服务，漏斗批次按需触发
"""SOP-C Step C2：聚宽策略粗筛出局（硬排除清单的机器第一遍）。

规范真源：docs/01_policies_and_standards/sop/backtest_system_sop/sop_c_strategy_library_intake.md §2。
判据（硬排除）：非股票标的（期货/基金定投/可转债/港美股专用）、非日线级（分钟/tick 主逻辑）、
结构不可迁移（配对交易/股指对冲/融券裸卖空）、演示作业类（向导产物/明显教学）。

机器启发式=关键词+代码特征打分，命中即标 excluded:<类别>；**启发式天然不全——
未命中判据一律 candidate，存疑由后续人工/AI 复核兜底（宁漏勿误）**。
用法::
    python scripts/backtest/strategy_screen_c2.py            # 全量粗筛
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Final

from zephyr.shared.io.paths import REPO_ROOT

_INTAKE_DIR = REPO_ROOT / "data" / "strategy_intake"
_MANIFEST = _INTAKE_DIR / "raw_manifest.csv"
_OUT = _INTAKE_DIR / "screen_c2.csv"

# 类别 -> (文件名/内容关键词, 代码特征正则元组)
_RULES: Final[dict[str, tuple[tuple[str, ...], tuple[str, ...]]]] = {
    "futures": (
        ("期货", "股指", "螺纹", "甲醇", "沥青", "豆粕", "铁矿石"),
        (r"\b(CFFEX|SHFE|DCE|CZCE|INE)\b", r"\b(buy_open|sell_close)\b"),
    ),
    "fund": (
        ("基金", "定投", "基金定投"),
        (r"\b(510|512|159|518)\d{3}\.(XSHG|XSHE)\b",),
    ),
    "cb": (
        ("可转债", "转股", "转债"),
        (r"\b11[02]\d{4}\.(XSHG|XSHE)\b",),
    ),
    "hk_us": (
        ("港股", "美股", "纳斯达克", "特斯拉", "腾讯控股"),
        (r"[A-Z]{3,5}\.US\b", r"\d{5}\.HK\b"),
    ),
    "intraday": (
        ("5分钟", "30分钟", "60分钟", "分时", "日内高频"),
        (r"frequency\s*=\s*['\"](1m|5m|15m|30m|60m)['\"]", r"get_bars\s*\([^)]*(m1|m5|m15)"),
    ),
    "pairs_hedge": (
        ("配对", "对冲", "套利", "价差回归", "融券", "卖空", "做空"),
        (r"\b(pair_trading|stat_arb|short_sell)\b",),
    ),
    "demo": (
        ("示例", "样例", "教学", "教程", "hello"),
        (r"(?i)^\s*#\s*(demo|example)",),
    ),
}
_MIN_LINES_DEMO: Final = 15   # 超短且无 initialize 的脚本疑似向导产物


# 工具型排除（fund/cb/hk_us）必须命中交易上下文同行——读价当指数代理（如 set_benchmark/
# get_price('510300') 择时）不构成"交易该标的"；宁漏勿误（误候选会被 C3/C4 自动过滤）。
_TRADE_CTX: Final = re.compile(r"order|universe|target|buy|sell|purchase", re.IGNORECASE)
_TRADE_CTX_CATS: Final[frozenset[str]] = frozenset({"fund", "cb", "hk_us"})


def _hit_code(text: str, pat: str, cat: str) -> bool:
    """代码特征匹配：benchmark 行不计；工具型类别须同行含交易上下文。"""
    need_ctx = cat in _TRADE_CTX_CATS
    for line in text.splitlines():
        if "benchmark" in line.lower():
            continue
        if not re.search(pat, line):
            continue
        if need_ctx and not _TRADE_CTX.search(line):
            continue
        return True
    return False


def _classify(text: str, name: str) -> str:
    """返回第一个命中的排除类别；无命中返回 candidate（宁漏勿误）。"""
    low_name = name.lower()
    for cat, (kws, patterns) in _RULES.items():
        hit_kw = any(k.lower() in low_name or k in text for k in kws)
        hit_re = any(_hit_code(text, pat, cat) for pat in patterns)
        if hit_kw or hit_re:
            return cat
    if "initialize" not in text and len(text.splitlines()) < _MIN_LINES_DEMO:
        return "demo"
    return "candidate"


def screen() -> int:
    if not _MANIFEST.exists():
        print(f"[FATAL] manifest 缺失: {_MANIFEST}——先跑 strategy_intake_inventory")
        return 2
    rows = list(csv.DictReader(_MANIFEST.open(encoding="utf-8-sig", newline="")))
    out_rows = []
    stats: dict[str, int] = {}
    for r in rows:
        text = ""
        norm = r.get("normalized_rel") or ""
        unreadable = r.get("unreadable") in ("True", "true", "1")
        if norm and not unreadable:
            f = _INTAKE_DIR / norm
            if f.exists():
                text = f.read_text(encoding="utf-8", errors="ignore")
        if unreadable or not norm:
            verdict = "unreadable"
        elif not text:
            verdict = "unreadable"   # 归一副本缺失/空——按不可读处理（不猜测）
        else:
            verdict = _classify(text, r.get("orig_name", ""))
        stats[verdict] = stats.get(verdict, 0) + 1
        out_rows.append({
            "seq": r["seq"], "year": r["year"], "orig_name": r["orig_name"],
            "md5_12": r.get("md5_12", ""),
            "screen": ("excluded:" + verdict) if verdict in _RULES or verdict == "demo" else verdict,
        })
    with _OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"screened={len(out_rows)} -> {_OUT.relative_to(REPO_ROOT)}")
    print("stats:", dict(sorted(stats.items(), key=lambda kv: -kv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(screen())
