# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.strategy_intake_inventory
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] SOP-C Step C1（盘点归一）; C2 粗筛（消费 manifest 列）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 破损/空文件记 unreadable 不修复不猜测(SOP-C §1); 原文件只读不删改; 归一副本统一 UTF-8 落 data/strategy_intake/normalized/; 清单落 data/strategy_intake/raw_manifest.csv(gitignore 区——产物可再生,预注册类资产才进 git)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源目录缺失->退出码2; 部分文件 unreadable 照常产出清单(列内标注)
# [TESTS] python scripts/backtest/strategy_intake_inventory.py --dry-run (smoke)
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  SOP-C C1 盘点 CLI 工具（代码归类表 A 类运维脚本），非常驻服务，漏斗批次按需触发
"""SOP-C Step C1：聚宽策略源码盘点归一（首批 600 条海选的漏斗入口）。

规范真源：docs/01_policies_and_standards/sop/backtest_system_sop/sop_c_strategy_library_intake.md §1。
裁定来源：docs/_working/2026-09-11-backtest-system-sop-discussion.md 问题三定稿（先入策略库，不直接挂图）。

逐文件登记：编号/年度/原文件名/字节数/行数/编码/是否含中文注释/平台特征/内容指纹(md5 前 12)；
统一转 UTF-8 副本落 normalized/<year>/；破损/空记 unreadable（不修复不猜测）。
平台特征启发式：initialize/handle_data/run_daily/before_trading_start/set_benchmark 等聚宽 API 标记。

用法::
    python scripts/backtest/strategy_intake_inventory.py             # 全量盘点+归一
    python scripts/backtest/strategy_intake_inventory.py --dry-run   # 只统计不落盘
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path
from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

_DEFAULT_SRC: Final = Path(r"E:\数据下载\qmt聚宽策略\2020-2026聚宽600条源码")
_OUT_DIR: Final = REPO_ROOT / "data" / "strategy_intake"
_CH_RE: Final = re.compile(r"[\u4e00-\u9fff]")
_JQ_MARKERS: Final[tuple] = (
    "initialize", "handle_data", "run_daily", "run_weekly", "run_monthly",
    "before_trading_start", "after_trading_end", "set_benchmark", "set_universe",
    "order_target_value", "order_value", "get_price", "get_fundamentals", "select_universe",
)


def _decode(raw: bytes) -> tuple[str | None, str]:
    """(text, encoding)；text=None=不可解码（unreadable）。"""
    for enc in ("utf-8", "gbk", "gb18030", "utf-16"):
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, "unknown"


def _platform_features(text: str) -> str:
    markers = [m for m in _JQ_MARKERS if m in text]
    return "|".join(markers)


def _ensure_norm_root(norm_root: Path, dry_run: bool) -> None:
    if not dry_run:
        norm_root.mkdir(parents=True, exist_ok=True)


def inventory(src: Path, *, dry_run: bool = False) -> int:
    if not src.exists():
        print(f"[FATAL] 源目录不存在: {src}")
        return 2
    norm_root = _OUT_DIR / "normalized"
    _ensure_norm_root(norm_root, dry_run)
    rows: list[dict] = []
    seq = 0
    unreadable = 0
    for year_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        year = year_dir.name
        files = sorted(p for p in year_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".txt", ".py"})
        for f in files:
            seq += 1
            raw = f.read_bytes()
            text, enc = _decode(raw)
            row = {
                "seq": seq,
                "year": year,
                "orig_name": f.name,
                "rel_path": str(f.relative_to(src)),
                "size_bytes": len(raw),
                "lines": (text.count("\n") + 1) if text is not None else "",
                "encoding": enc,
                "has_chinese": bool(text and _CH_RE.search(text)),
                "platform_features": _platform_features(text) if text is not None else "",
                "md5_12": hashlib.md5(raw).hexdigest()[:12],
                "unreadable": text is None or len(raw) == 0,
                "normalized_rel": "",
            }
            if row["unreadable"]:
                unreadable += 1
            elif not dry_run:
                out = norm_root / year / f.name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8", newline="\n")
                row["normalized_rel"] = str(out.relative_to(_OUT_DIR))
            rows.append(row)
    # 空文件/损坏如实标注（不修复不猜测）
    if not dry_run:
        _OUT_DIR.mkdir(parents=True, exist_ok=True)
        manifest = _OUT_DIR / "raw_manifest.csv"
        with manifest.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"manifest={manifest.relative_to(REPO_ROOT)}")
    dup = len(rows) - len({r["md5_12"] for r in rows})
    print(f"total={seq} unreadable={unreadable} dup_content={dup} years={sorted({r['year'] for r in rows})}")
    print("dry_run=true 未落盘" if dry_run else "归一副本+清单已落盘")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="SOP-C C1 聚宽源码盘点归一")
    ap.add_argument("--src", default=str(_DEFAULT_SRC), help="源码根目录")
    ap.add_argument("--dry-run", action="store_true", help="只统计不落盘")
    args = ap.parse_args()
    return inventory(Path(args.src), dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
