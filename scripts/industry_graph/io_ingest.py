# [MODULE] scripts.industry_graph.io_ingest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); parse 段另需 pyreadr(仅解析 .rda 时)
# [CONSUMERS] 无(数据资产装载器,消费端=图谱校准/断链补边 evidence,SQL 直查 ig_io_edge)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 架构数据直写 DB(RULE-SSOT 裁定,方案 docs/_working/2026-09-13-io-structure-anchor-plan.md D3); 幂等(UNIQUE year+from+to ON CONFLICT); 零值流量不落库(flow_wan<=0=无传导语义); PIT: as_of=数据基准年末, valid_from=官方发布可知时点; parse sanity: 列中间流量和≈TII 行(±0.1%), 违和即拒出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据文件缺失->退出码2; sanity 违和->退出码3(拒出防脏数); PG 不可达->退出码2
# [TTL] permanent
"""投入产出结构锚装载器：国家统计局投入产出表 → ig_io_edge 部门级上下游强度。

数据来源：ionet 学术包转存的官方《中国投入产出表》R 数据文件（.rda，GitHub
Carol-seven/ionet，原始真源=国家统计局《中国2020年投入产出表》2022-08 出版）。
parse 段产出标准矩阵 JSON（含 sanity 对账），load 段幂等入库 ig_io_edge。
两段分离：生产重跑 load 无需 pyreadr。

用法::

    python scripts/industry_graph/io_ingest.py parse --rda china_2020_153.rda --out io_matrix_2020_153.json
    python scripts/industry_graph/io_ingest.py load --matrix io_matrix_2020_153.json
    python scripts/industry_graph/io_ingest.py status
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SANITY_TOL = 0.001  # 列流量和对账容差 0.1%


def cmd_parse(rda: str, out: str) -> int:
    import pyreadr

    src = Path(rda)
    if not src.exists():
        print(f"[ERROR] 数据文件不存在: {src}")
        return 2
    obj_name = src.stem  # 约定: rda 对象名=文件名(china_2020_153)
    df = list(pyreadr.read_r(str(src)).values())[0]

    cols = [c for c in df.columns if c.isdigit()]  # 部门列 001..153
    sector_rows = df["Code"].astype(str).str.isdigit()
    n = len(cols)
    rows = df[sector_rows].reset_index(drop=True)
    if n != 153 or len(rows) != 153:
        print(f"[ERROR] 部门数违和: cols={n} rows={len(rows)} (期望 153)")
        return 3

    sectors = [
        {"code": str(r.Code).zfill(3), "en": str(r.Description), "cn": str(r.DescriptionInChinese)}
        for r in rows.itertuples()
    ]
    ti_row = df[df["Code"] == "TI"]  # 总投入行(原始 df,153 过滤之外)
    tii_row = df[df["Code"] == "TII"]  # 中间投入合计行
    if ti_row.empty or tii_row.empty:
        print("[ERROR] 找不到 TI/TII 汇总行,文件口径不符")
        return 3
    ti = {str(c).zfill(3): float(ti_row.iloc[0][c]) for c in cols}
    tii = {str(c).zfill(3): float(tii_row.iloc[0][c]) for c in cols}

    codes = [str(c).zfill(3) for c in cols]
    cn = {s["code"]: s["cn"] for s in sectors}
    m = rows.set_index("Code")[[c for c in cols]].astype(float)  # 153×153 流量矩阵(行=来源,列=去向)
    m.index = codes
    m.columns = codes
    import numpy as np

    arr = m.values  # arr[i][j] = 部门 i 投入到部门 j 的流量
    ti_vec = np.array([ti[c] for c in codes])
    tii_vec = np.array([tii[c] for c in codes])
    col_sums = arr.sum(axis=0)
    rel = np.abs(col_sums - tii_vec) / np.where(tii_vec > 0, tii_vec, 1)
    worst = float(rel.max())
    if worst > SANITY_TOL:
        print(f"[ERROR] sanity 违和: 列流量和 vs 中间投入合计最大偏差 {worst:.4%} > {SANITY_TOL:.1%}, 拒出")
        return 3

    edges = []
    for i, fi in enumerate(codes):
        for j, tj in enumerate(codes):
            v = arr[i][j]
            if v > 0 and ti_vec[j] > 0:
                edges.append({"from": fi, "from_cn": cn[fi], "to": tj, "to_cn": cn[tj],
                              "flow_wan": v, "coefficient": float(v / ti_vec[j])})

    parts = obj_name.split("_")  # 约定命名 china_YYYY_N / china_YYYY_42
    year = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 2020
    payload = {
        "dataset": obj_name, "year": year, "unit": "万元(生产者价格)",
        "sectors": sectors, "edges": edges, "sanity": {
            "max_col_deviation": worst, "tolerance": SANITY_TOL,
            "sector_count": n, "edge_count": len(edges),
        },
    }
    Path(out).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] {obj_name}: {n} 部门, {len(edges)} 条非零传导边, sanity 最大偏差 {worst:.6%} -> {out}")
    return 0


def cmd_load(matrix: str) -> int:
    p = Path(matrix)
    if not p.exists():
        print(f"[ERROR] 矩阵文件不存在: {p}")
        return 2
    data = json.loads(p.read_text(encoding="utf-8"))
    year, edges = data["year"], data["edges"]
    as_of = f"{year}-12-31"
    valid_from = "2022-08-31"  # 《中国2020年投入产出表》官方发布可知时点
    sd = f"io_{data['dataset']}|ionet(github Carol-seven/ionet) 官方表转存|{date.today().isoformat()}"

    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    sql = """
        INSERT INTO ig_io_edge (year, from_sector_code, from_sector, to_sector_code, to_sector,
                                flow_wan, coefficient, source, source_doc, market, as_of, valid_from)
        VALUES (%s,%s,%s,%s,%s,%s,%s,'io_official',%s,'cn',%s,%s)
        ON CONFLICT (year, from_sector_code, to_sector_code) DO UPDATE SET
            flow_wan=EXCLUDED.flow_wan, coefficient=EXCLUDED.coefficient,
            updated_at=now()
    """
    batch = [
        (year, e["from"], e["from_cn"], e["to"], e.get("to_cn", e["to"]), e["flow_wan"], e["coefficient"], sd, as_of, valid_from)
        for e in edges
    ]
    cur.executemany(sql, batch)
    conn.commit()
    cur.execute("SELECT count(*), count(DISTINCT from_sector_code) FROM ig_io_edge WHERE year=%s", (year,))
    n, ns = cur.fetchone()
    conn.close()
    print(f"[OK] ig_io_edge year={year}: 本批 {len(batch)} 行, 表内 {n} 行 / {ns} 个源部门 | as_of={as_of}")
    return 0


def _ionet_inventory() -> list[dict]:
    """探测 ionet 学术包(GitHub 转存官方表)的在库文件清单。"""
    import json as _json
    import urllib.request

    url = "https://api.github.com/repos/Carol-seven/ionet/contents/data"
    req = urllib.request.Request(url, headers={"User-Agent": "zephyr-io-ingest"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        items = _json.loads(resp.read().decode("utf-8"))
    out = []
    for it in items:
        name = it.get("name", "")
        if name.startswith("china_") and name.endswith(".rda"):
            parts = name[:-4].split("_")  # china_YYYY_N
            if len(parts) < 3 or not parts[1].isdigit() or not parts[2].isdigit():
                continue  # china_employment 等非表文件
            out.append({"name": name, "year": int(parts[1]), "sectors": int(parts[2]),
                        "size": it.get("size", 0), "url": it.get("download_url")})
    return sorted(out, key=lambda x: (x["year"], x["sectors"]))


def cmd_fetch(year: int | None, out_dir: str) -> int:
    inv = _ionet_inventory()
    if not inv:
        print("[ERROR] ionet repo 探测失败(网络/接口变更)")
        return 2
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT year FROM ig_io_edge")
    have = {r[0] for r in cur.fetchall()}
    conn.close()
    print(f"上游可用表: {[(i['year'], i['sectors']) for i in inv]}")
    print(f"库内已装载年份: {sorted(have)}")
    targets = [i for i in inv if (year is None and i["year"] not in have and i["year"] > max(have, default=0))
               or (year is not None and i["year"] == year)]
    # 同年取部门数最细版
    by_year: dict[int, dict] = {}
    for i in targets:
        if i["year"] not in by_year or i["sectors"] > by_year[i["year"]]["sectors"]:
            by_year[i["year"]] = i
    if not by_year:
        print("[OK] 无新表可取(上游无库外新年份;显式取表用 --year)")
        return 0
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)
    for i in by_year.values():
        dest = outp / i["name"]
        import urllib.request

        print(f"下载 {i['name']} ({i['size']} bytes) ...")
        urllib.request.urlretrieve(i["url"], dest)  # noqa: S310 白名单域名静态文件
        print(f"[OK] -> {dest}")
        print(f"后续: python scripts/industry_graph/io_ingest.py parse --rda {dest} --out {dest.with_suffix('.matrix.json')}")
    return 0


def cmd_status() -> int:
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute("""SELECT year, count(*), count(DISTINCT from_sector_code), min(coefficient), max(coefficient)
                   FROM ig_io_edge WHERE valid_to IS NULL GROUP BY year ORDER BY year""")
    rows = cur.fetchall()
    if not rows:
        print("ig_io_edge 空")
        return 0
    for year, n, ns, cmin, cmax in rows:
        print(f"year={year}: {n} 边 / {ns} 源部门 / 系数域 [{cmin:.2e}, {cmax:.4f}]")
    conn.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="投入产出结构锚装载器(parse/load/status)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("parse")
    p1.add_argument("--rda", required=True)
    p1.add_argument("--out", required=True)
    p2 = sub.add_parser("load")
    p2.add_argument("--matrix", required=True)
    p3 = sub.add_parser("fetch")
    p3.add_argument("--year", type=int, default=None, help="显式取某年表(默认只取库外新年份)")
    p3.add_argument("--out-dir", default=".runtime/tmp")
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "parse":
        return cmd_parse(a.rda, a.out)
    if a.cmd == "load":
        return cmd_load(a.matrix)
    if a.cmd == "fetch":
        return cmd_fetch(a.year, a.out_dir)
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
