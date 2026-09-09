# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.import_ths_profile
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_reader; schemas.categories.meta.meta_stock_profile_ths
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 源文件为 GBK 编码 \r 换行 TSV（伪装 .xlsx，禁 openpyxl）；行业层级 l2/l3 取独立列裸名；写经 ch_writer/读经 ch_reader（CH-FINAL-GATE 裁定 #ARCH-CH-007）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源文件缺失->退出码2; l2 空值比例>5%->退出码1(fail-visible); CH写入非COMMITTED->退出码2
# [TESTS] scripts/ch/import_ths_profile.py --verify
# [TTL] permanent
"""THS 个股元数据（细分行业+公司简介）导入 c1_market.stock_profile_ths（DS-223，2026-09-09）。

数据源：docs/_working/同花顺资料/个股1 (1).xlsx / 个股1 (2).xlsx
    两文件实为 GBK 编码、\r 换行的 TSV 文本（同花顺导出格式伪装 .xlsx，
    BadZipFile 实证），合计 5217 只沪深 A 股、零重叠（2026-09-09 实证）。

清洗规则：
    - 代码：SZ002317/SH600004 → 6 位裸码（exchange 由 MATERIALIZED 列派生）
    - 行业层级：l1 取"所属同花顺行业"【L1-L2-L3】首段；l2/l3 取独立列
      （"所属行业"/"细分行业"，裸名无申万式 Ⅱ/Ⅲ 后缀；与【】串 823 处
      后缀差异已实证为零真实口径差异，2026-09-09）；独立列为空时回退【】串
    - profile："--" 视为空串；tab/换行/控制字符由 ch_writer.tsv_escape 清洗
    - 证监会行业列不入库（1669 只"不详"质量不足，图谱侧仅交叉验证用）

用法::

    python scripts/ch/import_ths_profile.py             # 导入 + 校验
    python scripts/ch/import_ths_profile.py --dry-run   # 仅清洗统计，不写 CH
    python scripts/ch/import_ths_profile.py --verify    # 入库后抽验（ch_reader FINAL 读）

退出码：
    0 = 成功
    1 = 数据质量校验未过
    2 = 文件缺失 / CH 不可达
"""

from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from schemas.categories.meta.meta_stock_profile_ths import INSERT_COLUMNS, TABLE_NAME
from zephyr.data import ch_reader, ch_writer
from zephyr.shared.io.paths import REPO_ROOT  # SSoT 唯一真源（SSOT-REDEFINITION gate）

SOURCE_FILES = [
    os.path.join(REPO_ROOT, "docs", "_working", "同花顺资料", "个股1 (1).xlsx"),
    os.path.join(REPO_ROOT, "docs", "_working", "同花顺资料", "个股1 (2).xlsx"),
]

DATA_SOURCE = "ths_manual"
EXPECTED_HEADER = ["代码", "名称", "细分行业", "所属行业"]  # 前 4 列锚定（防源文件换版）


def _clean(v: str | None) -> str:
    """单元格清洗：去首尾空白，'--' 视为空。"""
    s = (v or "").strip()
    return "" if s == "--" else s


def _parse_ths_hierarchy(joint: str) -> tuple[str, str, str]:
    """解析【L1-L2-L3】行业层级串，段数!=3 返回 ('', '', '') 由调用方回退独立列。"""
    s = joint.strip().strip("【】")
    parts = [p.strip() for p in s.split("-") if p.strip()]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return "", "", ""


def _absorb_row(cells: list[str], rows: dict[str, dict], stats: dict[str, int]) -> None:
    """单行清洗入 rows：码归一 + 行业层级（独立列为主值）+ 简介统计。"""
    code_raw, name, sub_ind, ind2, _subs, _inv, profile, _csrc, ths_joint, *_rest = cells
    symbol = code_raw[-6:]  # SZ002317/SH600004 → 6位裸码
    if not symbol.isdigit() or len(code_raw) < 6:
        print(f"[WARN] 非法代码跳过: {code_raw!r}")
        return
    l1, j_l2, j_l3 = _parse_ths_hierarchy(ths_joint)
    l2 = ind2 or j_l2  # 独立列为主值（裸名，无 Ⅱ/Ⅲ 后缀）；为空回退【】串段
    l3 = sub_ind or j_l3
    if not profile:
        stats["profile_empty"] += 1
    if symbol in rows:
        stats["dup"] += 1
    rows[symbol] = {
        "symbol": symbol,
        "name": name,
        "industry_ths_l1": l1,
        "industry_ths_l2": l2,
        "industry_ths_l3": l3,
        "profile": profile,
    }


def _parse_source_file(fp: str, rows: dict[str, dict], stats: dict[str, int]) -> None:
    """解析单个 GBK TSV 源文件：表头锚定 + 逐行清洗入 rows。"""
    with open(fp, "rb") as fh:
        text = fh.read().decode("gb18030", errors="replace")
    lines = [l for l in text.split("\r") if l.strip()]
    header = [c.strip() for c in lines[0].split("\t")]
    if header[: len(EXPECTED_HEADER)] != EXPECTED_HEADER:
        print(f"[ERROR] 表头锚定失败（源文件可能换版）: {os.path.basename(fp)} -> {header[:6]}")
        raise SystemExit(2)
    for ln in lines[1:]:
        cells = [_clean(c) for c in ln.split("\t")]
        cells += [""] * (12 - len(cells))  # 行尾空列补齐
        _absorb_row(cells, rows, stats)


def load_ths_rows() -> list[dict]:
    """解析全部源文件，返回去重后的行 dict 列表（含质量统计打印）。"""
    rows: dict[str, dict] = {}
    stats = {"profile_empty": 0, "dup": 0}
    for fp in SOURCE_FILES:
        if not os.path.isfile(fp):
            print(f"[ERROR] 源文件缺失: {fp}")
            raise SystemExit(2)
        _parse_source_file(fp, rows, stats)
    total = len(rows)
    empty_l2 = sum(1 for r in rows.values() if not r["industry_ths_l2"])
    empty_l3 = sum(1 for r in rows.values() if not r["industry_ths_l3"])
    print(f"清洗完成: {total} 只（dup {stats['dup']}）")
    print(f"质量: l2 为空 {empty_l2} | l3 为空 {empty_l3} | 简介为空 {stats['profile_empty']}")
    if total == 0:
        print("[ERROR] 零行数据")
        raise SystemExit(2)
    if total > 0 and empty_l2 / total > 0.05:
        print("[ERROR] l2 空值比例 >5%，源文件格式疑似变更，fail-visible")
        raise SystemExit(1)
    return list(rows.values())


def build_tsv(rows: list[dict], trade_date: str) -> bytes:
    """行 dict → TSV 字节（列序与 INSERT_COLUMNS 一致）。"""
    lines = []
    for r in rows:
        fields = [
            trade_date,
            r["symbol"],
            r["name"],
            r["industry_ths_l1"],
            r["industry_ths_l2"],
            r["industry_ths_l3"],
            r["profile"],
            DATA_SOURCE,
        ]
        lines.append("\t".join(ch_writer.tsv_escape(v) for v in fields))
    return ("\n".join(lines) + "\n").encode("utf-8")


def do_import(trade_date: str) -> int:
    rows = load_ths_rows()
    tsv = build_tsv(rows, trade_date)
    outcome = ch_writer.write_tsv_outcome(
        f"c1_market.{TABLE_NAME}", INSERT_COLUMNS, tsv
    )
    print(f"写入 c1_market.{TABLE_NAME}: {outcome}")
    if not outcome.is_ch_committed:
        print("[ERROR] 未提交到 ClickHouse（LOCAL_DURABLE=已落盘待回灌 / NOT_DURABLE=失败）")
        return 2
    return do_verify(trade_date, expect=len(rows))


def do_verify(trade_date: str | None = None, expect: int | None = None) -> int:
    """入库后校验（ch_reader 只读通道，自动 FINAL）：行数 + 层级分布 + 单股抽验。"""
    where = f"WHERE trade_date = '{trade_date}'" if trade_date else ""
    raw = ch_reader.query(
        f"SELECT count(), uniqExact(symbol) FROM c1_market.{TABLE_NAME} {where} FORMAT TSV"
    ).strip()
    print(f"行数/唯一股票数: {raw}")
    if not raw:
        print("[ERROR] 校验查询返回空（CH 不可达或表空）")
        return 2
    if expect is not None:
        cnt = int(raw.split("\t")[0])
        if cnt < expect:
            print(f"[ERROR] 行数 {cnt} < 预期 {expect}")
            return 1
    dist = ch_reader.query(
        f"SELECT industry_ths_l1, count() FROM c1_market.{TABLE_NAME} {where} "
        "GROUP BY 1 ORDER BY 2 DESC LIMIT 8 FORMAT TSV"
    ).strip()
    print(f"一级行业 Top8:\n{dist}")
    sample_where = where or (
        f"WHERE trade_date = (SELECT max(trade_date) FROM c1_market.{TABLE_NAME})"
    )
    sample = ch_reader.query(
        f"SELECT symbol_canonical, name, industry_ths_l2, industry_ths_l3, "
        f"substring(profile, 1, 40) FROM c1_market.{TABLE_NAME} {sample_where} "
        "AND symbol IN ('688825', '600519', '000001') FORMAT TSV"
    ).strip()
    print(f"抽验:\n{sample}")
    return 0


def main() -> int:
    trade_date = datetime.date.today().isoformat()
    if "--verify" in sys.argv:
        return do_verify()
    if "--dry-run" in sys.argv:
        rows = load_ths_rows()
        sample = rows[0]
        print(f"样例: {sample['symbol']} {sample['name']} "
              f"L1={sample['industry_ths_l1']} L2={sample['industry_ths_l2']} "
              f"L3={sample['industry_ths_l3']} profile[:30]={sample['profile'][:30]}")
        print("dry-run 不写库")
        return 0
    return do_import(trade_date)


if __name__ == "__main__":
    raise SystemExit(main())
