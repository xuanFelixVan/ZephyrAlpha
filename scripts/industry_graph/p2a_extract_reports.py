# [MODULE] scripts.industry_graph.p2a_extract_reports
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] P3a 结构化抽取; P3b 语料库
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等: 已 extracted 的 doc 跳过; 语料输出按 doc_id 命名; 进程池并行解析
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单文件解析失败->parse_status='failed'继续
# [TTL] permanent
"""T1/P2a：484 份文字型研报 PyMuPDF 全文提取（进程池并行）。

对 ig_document 中 doc_type='research_report' 的 canonical 文档，用 PyMuPDF
提取全文写入语料目录 {doc_id}.md，回写 parse_status/extracted_text_path。
文字型 PDF 提取为零模型纯解析，ProcessPool 并行。

用法::

    python scripts/industry_graph/p2a_extract_reports.py [--workers 6]
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pymupdf

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

CORPUS_DIR = Path(r"E:\数据下载\产业链数据_P2语料")


def extract_one(args: tuple[str, str, str]) -> tuple[str, str, int, str | None]:
    """worker: 提取单个 PDF。返回 (doc_id, status, n_chars, error)。"""
    doc_id, path, out_dir = args
    try:
        doc = pymupdf.open(path)
        parts = []
        for i, page in enumerate(doc):
            parts.append(f"\n\n<!-- page {i + 1} -->\n")
            parts.append(page.get_text())
        doc.close()
        text = "".join(parts).strip()
        if len(text) < 20:
            return doc_id, "empty", len(text), None
        out = Path(out_dir) / f"{doc_id}.md"
        out.write_text(text, encoding="utf-8")
        return doc_id, "extracted", len(text), None
    except Exception as exc:  # noqa: BLE001
        return doc_id, "failed", 0, str(exc)[:200]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_depgraph_pg_connection(read_only=False, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, source_root || '\\' || relative_path
            FROM ig_document
            WHERE doc_type = 'research_report' AND is_canonical AND NOT excluded
              AND parse_status = 'pending'
            ORDER BY size_bytes
            """
        )
        docs = cur.fetchall()
    print(f"[T1] 待提取研报 {len(docs)} 份, workers={args.workers}")

    tasks = [(d, p, str(CORPUS_DIR)) for d, p in docs]
    stats = {"extracted": 0, "empty": 0, "failed": 0}
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool, conn.cursor() as cur:
        futures = {pool.submit(extract_one, t): t[0] for t in tasks}
        for fut in as_completed(futures):
            doc_id, status, n_chars, err = fut.result()
            stats[status] += 1
            cur.execute(
                "UPDATE ig_document SET parse_status=%s, extracted_text_path=%s, updated_at=now() WHERE doc_id=%s",
                (status, str(CORPUS_DIR / f"{doc_id}.md") if status == "extracted" else None, doc_id),
            )
            if err:
                print(f"[WARN] {doc_id}: {err}")
            done += 1
            if done % 50 == 0:
                print(f"[PROGRESS] {done}/{len(tasks)} (extracted={stats['extracted']})")
    conn.close()
    print(f"[T1] 完成: {stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
