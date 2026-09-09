# [BLUEPRINT] GREATWALL-20260910-EQUITY-HK | (长城任务 2026-09-10 接续) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.ths_equity_hk_refill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config (hk_stock_list 只读反查); websearch_ingest (ingest 唯一通道)
# [CONSUMERS] 长城任务股权线②接续——263 被投缺口中港股子集机械复归(上夜 report_20260910 开放问题 15/下夜班种子①)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部落库走 websearch_ingest ingest 通道(禁手写 SQL); 反幻觉纪律: held 代码只来自
#              hk_stock_list 在库真源的名称精确匹配(禁凭记忆/禁模糊 LIKE); 同名多 code 命中>1 留缺口
#              (防重名误配); 匹配两轮=NFKC 归一全等→剥上市后缀(-W/-B/-S/-WR 等)再全等; 未命中留缺口
#              不落库; 幂等(UNIQUE holder,held,as_of,source,与上夜 621 条 A 股 held 零冲突); 台账回写留痕
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 台账/源清单缺失->exit 2; ingest 校验拒绝->exit 3(批次拒收不落库)
# [TESTS] 首跑对账: 命中数+拒绝数+ingest 行数三方一致; 幂等复跑零新增
from __future__ import annotations

"""THS 被投缺口港股子集机械复归 ig_equity_edge（长城股权线接续 2026-09-10）。

背景：上夜 ths_equity_import.py 解析 884 股入 621 条，263 条缺口（被投方为港股/北交所/
美股/退市更名，A股 stock_basic 反查不过）登记 ths_equity_gaps_20260909.md。
本脚本只处理其中的港股子集：CH hk_stock_list（2798 只在库快照）名称精确反查——
真源在库零搜索零幻觉，符合缺口台账"禁凭名称编造 symbol"纪律的核证通道扩展。

北交所（stock_basic 无 BJ 行）/美股（无在库清单真源）/退市更名：留缺口，本脚本不碰。

用法::

    python scripts/industry_graph/thq_equity_hk_refill.py --dry-run   # 只看命中
    python scripts/industry_graph/ths_equity_hk_refill.py             # 生成批次+ingest+台账回写
"""

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

GAP_LEDGER = REPO / ".runtime" / "industry_graph" / "night_audit" / "ths_equity_gaps_20260909.md"
BATCH_DIR = REPO / ".runtime" / "industry_graph" / "night_audit" / "batches"
SOURCE_DOC = "同花顺导出|个股1(1+2) 被投资公司简称(已上市)[2025财年 年报] 港股复归 hk_stock_list 反查|2026-09-10"
AS_OF = "2025-12-31"   # 与上夜 THS 批次同口径（列名年份戳 2025财年 年报）
HK_SUFFIX = ".HK"

# 上市后缀剥离表（港股命名惯例，NFKC 归一后剥离再比对；只剥这些，防误伤名称本体）
LISTING_SUFFIXES = ("-W", "-WR", "-B", "-S", "-R", "-SW", "-SB")


def _norm(s: str) -> str:
    s = (s or "").replace("&amp;", "&")   # 台账名含 HTML 转义（&amp;），先还原再归一
    return unicodedata.normalize("NFKC", s).replace(" ", "").replace("\u3000", "").upper()


def _strip_suffixes(s: str) -> str:
    for suf in LISTING_SUFFIXES:
        if s.endswith(suf) and len(s) > len(suf):
            return s[: -len(suf)]
    return s


def load_gap_rows() -> list[tuple[str, str]]:
    """缺口台账 markdown 表格解析 → [(holder, 被投名称)]。"""
    rows: list[tuple[str, str]] = []
    for line in GAP_LEDGER.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{6}\.(?:SZ|SH|BJ))\s*\|\s*([^|]+?)\s*\|\s*未解析", line)
        if m:
            rows.append((m.group(1), m.group(2).strip()))
    return rows


def load_hk_names() -> dict[str, list[str]]:
    """hk_stock_list 只读快照 → {NFKC 归一名: [code, ...]}（同名多 code 保留全列表防误配）。"""
    from clickhouse_driver import Client
    from zephyr.data.ch_config import load_ch_config

    cfg = load_ch_config()
    ch = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                user=cfg.get("reader_user") or cfg.get("user", "default"),
                password=cfg.get("reader_password") or cfg.get("password", ""),
                database=cfg.get("database", "c1_market"), connect_timeout=3, send_receive_timeout=15)
    rows = ch.execute("SELECT code, name FROM hk_stock_list WHERE valid_to IS NULL")
    out: dict[str, list[str]] = {}
    for code, name in rows:
        out.setdefault(_norm(name), []).append(str(code))
    return out


def match_gaps(gaps: list[tuple[str, str]], hk: dict[str, list[str]]) -> tuple[list[dict], list[tuple[str, str, str]]]:
    """缺口逐条反查 → (命中列表, 未命中列表)。同名多 code 防误配留人工核。"""
    matched: list[dict] = []
    still_gap: list[tuple[str, str, str]] = []
    for holder, name in gaps:
        n = _norm(name)
        codes = hk.get(n) or hk.get(_strip_suffixes(n)) or []
        codes = sorted(set(codes))
        if len(codes) == 1:
            matched.append({"holder": holder, "held": codes[0] + HK_SUFFIX, "name": name,
                            "match": "exact" if n in hk else "suffix-stripped"})
        elif len(codes) > 1:
            still_gap.append((holder, name, f"港股同名多代码 {codes}（防重名误配留人工核）"))
        else:
            still_gap.append((holder, name, "港股清单未命中（美股/退市/名称不一致/北交所）"))
    return matched, still_gap


def write_batch_and_ingest(matched: list[dict]) -> int:
    """批次落盘 + ingest 通道提交（exit 3=拒收不落库）。"""
    records = [{
        "type": "equity_edge",
        "holder": m["holder"],
        "held": m["held"],
        "relation": "invests_in",
        "as_of": AS_OF,
        "source": "ths_export",
        "verification": "unverified",
        "source_doc": SOURCE_DOC,
    } for m in matched]
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    bp = BATCH_DIR / "equity_hk_refill_001.json"
    bp.write_text(json.dumps({"batch_id": "equity_hk_refill_001", "records": records},
                             ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"批次落盘 {bp} ({len(records)} records)")

    r = subprocess.run([sys.executable, str(REPO / "scripts" / "industry_graph" / "websearch_ingest.py"),
                        "ingest", "--batch", str(bp)], capture_output=True, text=True)
    for ln in (r.stdout or "").splitlines()[-6:]:
        print("  |", ln)
    if r.returncode != 0:
        print(f"[ERROR] ingest 拒收 exit={r.returncode}（批次拒收不落库，按报错修正重提）")
        print((r.stderr or "")[-500:])
        return 3
    return 0


def rewrite_ledger(matched: list[dict]) -> None:
    """台账回写：命中行标注"已复归→code.HK"（幂等复跑不再命中）。"""
    text = GAP_LEDGER.read_text(encoding="utf-8")
    hit_map = {m["holder"] + "|" + m["name"]: m for m in matched}
    out_lines = []
    for line in text.splitlines():
        mm = re.match(r"^(\|\s*(\d{6}\.(?:SZ|SH|BJ))\s*\|\s*)([^|]+?)\s*(\|.*未解析)", line)
        if mm and f"{mm.group(2)}|{mm.group(3).strip()}" in hit_map:
            m = hit_map[f"{mm.group(2)}|{mm.group(3).strip()}"]
            out_lines.append(f"{mm.group(1)}{mm.group(3)} | 已复归→{m['held']}（hk_stock_list 精确反查 2026-09-10）|")
        else:
            out_lines.append(line)
    GAP_LEDGER.write_text("\n".join(out_lines) + "\n", encoding="utf-8", newline="\n")
    print(f"台账回写完成：复归 {len(matched)} 条标注")


def main(dry_run: bool = False) -> int:
    if not GAP_LEDGER.is_file():
        print(f"[ERROR] 缺口台账缺失: {GAP_LEDGER}")
        return 2
    gaps = load_gap_rows()
    hk = load_hk_names()
    print(f"缺口 {len(gaps)} 条, hk_stock_list 归一名 {len(hk)} 个")

    matched, still_gap = match_gaps(gaps, hk)
    print(f"命中 {len(matched)} / 未命中 {len(still_gap)}")
    for m in matched[:8]:
        print(f"  ✓ {m['holder']} → {m['held']}  {m['name']}  [{m['match']}]")

    if dry_run or not matched:
        for g in still_gap[:5]:
            print(f"  ✗ {g[0]} {g[1]}  {g[2]}")
        return 0

    rc = write_batch_and_ingest(matched)
    if rc != 0:
        return rc
    rewrite_ledger(matched)
    return 0


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))
