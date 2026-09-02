# [MODULE] scripts.industry_graph.p0_scan_documents
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); scripts.industry_graph.apply_industry_graph_ddl
# [CONSUMERS] P1 归一解压流水线
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重跑(UPSERT); doc_id=md5(相对路径); dedup_group=md5(文件内容); 只读扫描源目录不改动任何源文件
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源目录不存在->退出码2; 单文件读取失败->file_hash=NULL继续
# [TTL] permanent
"""P0 产业链源文档全量盘点登记 + 文件级 MD5 去重。

扫描 E:\\数据下载\\产业链数据（或 --root 指定目录），将每个文件登记到
ig_document 表：路径/大小/MD5/文档类型/年份/机构/排除标记/去重组。
内容级（PDF 内文本）二次去重属 P1 阶段，本脚本只做文件级。

用法::

    python scripts/industry_graph/p0_scan_documents.py
    python scripts/industry_graph/p0_scan_documents.py --root "E:\\数据下载\\产业链数据"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from psycopg2.extras import execute_values

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

DEFAULT_ROOT = r"E:\数据下载\产业链数据"
SUMMARY_PATH = Path(__file__).resolve().parents[2] / ".runtime" / "industry_graph" / "p0_summary.json"

_ARCHIVE_EXT = {".zip", ".rar", ".7z"}
_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}
_STRUCTURED_EXT = {".xlsx", ".xls", ".dta", ".csv"}
_CODE_EXT = {".do", ".py", ".r"}
_PANORAMA_KW = ("全景图", "产业链图", "图谱", "图解")
# 与 A 股产业链无关内容的剔除关键词（保守，宁缺毋滥）
_EXCLUDE_KW = ("赠品", "数字游民", "淘宝店")
# 券商/机构名识别（文件名中含"XX证券图谱"等）
_ORG_KW = (
    "天风证券",
    "国盛证券",
    "中信建投",
    "华鑫证券",
    "民生证券",
    "中航证券",
    "安信证券",
    "中信证券",
    "华泰证券",
    "国泰君安",
    "招商证券",
    "广发证券",
    "海通证券",
    "兴业证券",
    "东吴证券",
    "浙商证券",
    "华西证券",
    "国金证券",
    "平安证券",
    "银河证券",
    "中金",
    "国信证券",
    "光大证券",
    "申万宏源",
)
_YEAR_RE = re.compile(r"(20\d{2})\s*年?")


def _long(p: str) -> str:
    """Windows 超长路径（>260）加 \\\\?\\ 前缀，防止 os.walk/open 失败。"""
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        return "\\\\?\\" + os.path.abspath(p)
    return p


def _md5(path: str, chunk: int = 4 << 20) -> str | None:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while True:
                buf = f.read(chunk)
                if not buf:
                    break
                h.update(buf)
        return h.hexdigest()
    except OSError as exc:
        print(f"[WARN] 读取失败，hash 置空: {path} ({exc})")
        return None


def _doc_type(ext: str, name: str) -> str:
    if ext in _ARCHIVE_EXT:
        return "archive"
    if ext in _IMAGE_EXT:
        return "atlas_image"
    if ext in _STRUCTURED_EXT:
        return "structured_data"
    if ext in _CODE_EXT:
        return "code"
    if ext == ".pdf":
        return "panorama_pdf" if any(k in name for k in _PANORAMA_KW) else "research_report"
    return "other"


def _exclusion(rel_path: str) -> tuple[bool, str | None]:
    for kw in _EXCLUDE_KW:
        if kw in rel_path:
            return True, f"keyword:{kw}"
    return False, None


def _parse_year(name: str) -> int | None:
    m = _YEAR_RE.search(name)
    if not m:
        return None
    y = int(m.group(1))
    return y if 2000 <= y <= 2030 else None


def _parse_org(name: str) -> str | None:
    for org in _ORG_KW:
        if org in name:
            return org
    return None


def scan(root: str) -> list[tuple]:
    long_root = _long(root)
    rows: list[tuple] = []
    for dirpath, _dirnames, filenames in os.walk(long_root):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, long_root)
            bundle = rel.split(os.sep)[0]
            ext = os.path.splitext(fn)[1].lower()
            try:
                st = os.stat(full)
                size, mtime = st.st_size, datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
            except OSError as exc:
                print(f"[WARN] stat 失败跳过: {rel} ({exc})")
                continue
            file_hash = _md5(full)
            excluded, reason = _exclusion(rel)
            doc_id = "DOC-" + hashlib.md5(rel.encode("utf-8")).hexdigest()[:20]
            rows.append(
                (
                    doc_id,
                    rel,
                    root,  # source_root
                    bundle,
                    fn,
                    ext,
                    size,
                    mtime,
                    file_hash,
                    "DG-" + file_hash[:16] if file_hash else None,
                    True,  # is_canonical 入库后统一按组重算
                    _doc_type(ext, fn),
                    os.path.splitext(fn)[0],
                    _parse_year(fn),
                    _parse_org(fn),
                    excluded,
                    reason,
                )
            )
            if len(rows) % 500 == 0:
                print(f"[PROGRESS] 已扫描 {len(rows)} 个文件 ...")
    return rows


def upsert(conn, rows: list[tuple]) -> None:
    sql = """
        INSERT INTO ig_document (
            doc_id, relative_path, source_root, bundle, file_name, ext, size_bytes, mtime,
            file_hash, dedup_group, is_canonical, doc_type, title, year, org,
            excluded, exclude_reason
        ) VALUES %s
        ON CONFLICT (doc_id) DO UPDATE SET
            relative_path  = EXCLUDED.relative_path,
            source_root    = EXCLUDED.source_root,
            bundle         = EXCLUDED.bundle,
            file_name      = EXCLUDED.file_name,
            ext            = EXCLUDED.ext,
            size_bytes     = EXCLUDED.size_bytes,
            mtime          = EXCLUDED.mtime,
            file_hash      = EXCLUDED.file_hash,
            dedup_group    = EXCLUDED.dedup_group,
            doc_type       = EXCLUDED.doc_type,
            title          = EXCLUDED.title,
            year           = EXCLUDED.year,
            org            = EXCLUDED.org,
            excluded       = EXCLUDED.excluded,
            exclude_reason = EXCLUDED.exclude_reason,
            updated_at     = now()
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=500)
        # 组内 canonical = 相对路径字典序最小者（全局重算，保证重跑幂等）
        cur.execute(
            """
            UPDATE ig_document d
            SET is_canonical = (d.relative_path = sub.min_path), updated_at = now()
            FROM (
                SELECT dedup_group, MIN(relative_path) AS min_path
                FROM ig_document
                WHERE dedup_group IS NOT NULL
                GROUP BY dedup_group
            ) sub
            WHERE d.dedup_group = sub.dedup_group
            """
        )
    conn.commit()


def summarize(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), coalesce(sum(size_bytes),0) FROM ig_document")
        total, total_bytes = cur.fetchone()
        cur.execute("SELECT doc_type, count(*) FROM ig_document GROUP BY 1 ORDER BY 2 DESC")
        by_type = dict(cur.fetchall())
        cur.execute("SELECT ext, count(*) FROM ig_document GROUP BY 1 ORDER BY 2 DESC")
        by_ext = dict(cur.fetchall())
        cur.execute("SELECT bundle, count(*) FROM ig_document GROUP BY 1 ORDER BY 2 DESC")
        by_bundle = dict(cur.fetchall())
        cur.execute("SELECT count(*) FROM ig_document WHERE excluded")
        excluded_n = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT dedup_group) FROM ig_document WHERE dedup_group IS NOT NULL")
        groups = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM ig_document WHERE file_hash IS NULL")
        hash_fail = cur.fetchone()[0]
        cur.execute(
            """
            SELECT count(*), coalesce(sum(size_bytes),0) FROM ig_document
            WHERE dedup_group IS NOT NULL AND NOT is_canonical
            """
        )
        dup_n, dup_bytes = cur.fetchone()
        cur.execute(
            """
            SELECT dedup_group, count(*) c, min(relative_path) FROM ig_document
            WHERE dedup_group IS NOT NULL AND NOT excluded
            GROUP BY 1 HAVING count(*) > 1 ORDER BY c DESC LIMIT 10
            """
        )
        top_dups = cur.fetchall()
    return {
        "total_files": total,
        "total_gb": round(float(total_bytes) / 1e9, 2),
        "by_type": by_type,
        "by_ext": by_ext,
        "by_bundle": by_bundle,
        "excluded": excluded_n,
        "hash_failed": hash_fail,
        "unique_content_groups": groups,
        "duplicate_files": dup_n,
        "duplicate_gb": round(float(dup_bytes) / 1e9, 2),
        "effective_files": total - dup_n - excluded_n,
        "top_dup_groups": [{"group": g, "copies": c, "sample": p} for g, c, p in top_dups],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--summary-only", action="store_true", help="跳过扫描，仅对库内已有数据出摘要")
    args = ap.parse_args()

    if not args.summary_only and not os.path.isdir(args.root):
        print(f"[ERROR] 源目录不存在: {args.root}")
        return 2

    conn = get_depgraph_pg_connection(read_only=False, autocommit=False)
    try:
        if not args.summary_only:
            print(f"[P0] 开始扫描: {args.root}")
            rows = scan(args.root)
            print(f"[P0] 扫描完成，共 {len(rows)} 个文件，开始入库 ...")
            upsert(conn, rows)
        summary = summarize(conn)
    finally:
        conn.close()

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[P0] 完成，摘要已写入 {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
