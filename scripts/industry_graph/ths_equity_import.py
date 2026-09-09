# [BLUEPRINT] GREATWALL-20260909-EQUITY-IMPORT | (长城任务 2026-09-09) | §
# [TTL] permanent
# [MODULE] scripts.industry_graph.ths_equity_import
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer (stock_basic 反查); websearch_ingest (ingest 唯一通道)
# [CONSUMERS] 长城任务 Phase1 THS 被投导入 ig_equity_edge(Owner 2026-09-09 三裁定: 同库独立表/今晚并行跑/THS 被投进股权表)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部落库走 websearch_ingest ingest 通道(禁手写 SQL); 简称解析三步(精确->NFKC 归一->ST 前缀剥离),解析不到不落库只登记缺口(禁编造代码); as_of=年报口径期末日 2025-12-31(列名年份戳); relation=invests_in 固定(THS 被投列语义); 幂等(UNIQUE holder,held,as_of,source)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 原档缺失->exit 2; ingest 校验拒绝->exit 3(批次拒收不落库)
# [TESTS] 2026-09-09 首跑: 621 条入 ig_equity_edge/263 缺口台账/幂等复跑
# [TTL] permanent
"""THS 被投清单导入 ig_equity_edge（Owner 2026-09-09 裁定执行）。

数据源：docs/_working/同花顺资料/个股1 (1).xlsx / 个股1 (2).xlsx（GBK TSV 伪 xlsx）
列：被投资公司简称(已上市)[2025财年 年报]——THS 终端导出，仅限本机内部研究消费。

分流纪律：被投（资本关系）→ ig_equity_edge，禁入 ig_company_edge（SOP 开放问题 7 v2 裁定）。
解析不到 A 股代码的（港股/美股上市被投、北交所被投[stock_basic 无 BJ]、退市/更名）
→ 只落缺口台账，不落库（反幻觉：禁凭名称编造 symbol）。

用法::

    python scripts/industry_graph/ths_equity_import.py            # 生成批次+ingest+缺口台账
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

THS_DIR = REPO / "docs" / "_working" / "同花顺资料"
SOURCE_FILES = [THS_DIR / "个股1 (1).xlsx", THS_DIR / "个股1 (2).xlsx"]
INVEST_COL = "被投资公司简称(已上市)[2025财年 年报]"
BATCH_DIR = REPO / ".runtime" / "industry_graph" / "night_audit" / "batches"
GAP_LEDGER = REPO / ".runtime" / "industry_graph" / "night_audit" / "ths_equity_gaps_20260909.md"
SOURCE_DOC = "同花顺导出|个股1(1+2) 被投资公司简称(已上市)[2025财年 年报]|2026-09-09"
AS_OF = "2025-12-31"  # 年报口径期末日（列名年份戳 2025财年 年报）


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).replace(" ", "").replace("\u3000", "").upper()


def _strip_st(s: str) -> str:
    return re.sub(r"^\*?ST", "", s)


def load_name2sym() -> dict[str, str]:
    from zephyr.data import ch_writer

    tsv = ch_writer.query(
        "SELECT name, symbol_canonical FROM c1_market.stock_basic FINAL WHERE valid_to IS NULL"
    )
    m: dict[str, str] = {}
    for ln in tsv.strip().splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2:
            m[_norm(parts[0])] = parts[1].strip()
    return m


def resolve(name: str, name2sym: dict[str, str]) -> str | None:
    """三步解析：精确 -> NFKC 归一 -> ST 前缀剥离。"""
    for cand in (name, _norm(name), _strip_st(_norm(name))):
        if cand in name2sym:
            return name2sym[cand]
    # stock_basic 侧 ST 前缀形态（如 *ST合力泰）：剥掉目标名前缀后比对
    st_stripped = { _strip_st(k): v for k, v in name2sym.items() if k.startswith(("ST", "*ST")) }
    return st_stripped.get(_norm(name))


def ths_code_to_symbol(code: str) -> str:
    m = re.match(r"^(SH|SZ|BJ)(\d{6})$", code)
    if not m:
        raise ValueError(f"THS 代码格式异常: {code}")
    return f"{m.group(2)}.{m.group(1)}"


def main() -> int:
    rows: list[dict] = []
    for fn in SOURCE_FILES:
        if not fn.is_file():
            print(f"[ERROR] 原档缺失: {fn}")
            return 2
        with open(fn, encoding="gbk", errors="replace") as f:
            header = f.readline().rstrip("\n").split("\t")
            for line in f:
                vals = line.rstrip("\n").split("\t")
                rows.append(dict(zip(header, vals)))

    name2sym = load_name2sym()
    records: list[dict] = []
    gaps: list[tuple[str, str, str, str]] = []  # holder, held_name, reason, resolved?
    seen_pairs: set[tuple[str, str]] = set()
    for r in rows:
        held_name = (r.get(INVEST_COL) or "").strip()
        if not held_name or held_name == "--":
            continue
        holder_code = r.get("代码", "")
        holder = ths_code_to_symbol(holder_code)
        sym = resolve(held_name, name2sym)
        if sym is None:
            reason = "未解析(海外上市/北交所不在stock_basic/退市更名)"
            gaps.append((holder, held_name, reason, ""))
            continue
        if (holder, sym) in seen_pairs:
            continue
        seen_pairs.add((holder, sym))
        records.append({
            "type": "equity_edge",
            "source": "ths_export",
            "holder": holder,
            "held": sym,
            "relation": "invests_in",
            "layer": 1,
            "as_of": AS_OF,
            "verification": "unverified",
            "holder_country": "CN",
            "evidence": f"THS 被投资公司简称(已上市)[2025财年 年报]='{held_name}'",
            "source_doc": SOURCE_DOC,
        })

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    batch_path = BATCH_DIR / "ths_equity_001.json"
    batch_path.write_text(
        json.dumps({"batch_id": "ths_equity_001", "records": records}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(json.dumps({"batch": str(batch_path), "records": len(records), "gaps": len(gaps)},
                     ensure_ascii=False))
    if records:
        rc = subprocess.call([sys.executable, str(REPO / "scripts" / "industry_graph" / "websearch_ingest.py"),
                              "ingest", "--batch", str(batch_path)])
        if rc != 0:
            return rc

    if gaps:
        lines = [
            "# THS 被投缺口台账（解析不到 A 股代码，未落库）",
            f"# 生成 2026-09-09 by ths_equity_import.py；反幻觉纪律：禁凭名称编造 symbol",
            "",
            "| holder | 被投名称 | 原因 |",
            "|---|---|---|",
        ]
        for holder, held_name, reason, _ in sorted(gaps):
            lines.append(f"| {holder} | {held_name} | {reason} |")
        GAP_LEDGER.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[GAPS] {len(gaps)} 条未落库, 台账: {GAP_LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
