# [MODULE] scripts.industry_graph.p3b_corpus_manifest
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] NLP 管道; RAG 知识库
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重建 manifest; 只统计有提取文本的文档
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无已提取文档->退出码2
# [TTL] permanent
"""T3/P3b：语料归档一致性核对 + 生成语料清单（manifest.jsonl）。

核对 ig_document 中已提取文档与语料目录文件一致性，生成下游 NLP 可用的
manifest.jsonl（doc_id/标题/类型/年份/字数/语料路径），并输出归档总账。

用法::

    python scripts/industry_graph/p3b_corpus_manifest.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

CORPUS_DIR = Path(r"E:\数据下载\产业链数据_P2语料")
MANIFEST = CORPUS_DIR / "manifest.jsonl"


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=True, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, title, doc_type, year, org, bundle, parse_status, extracted_text_path
            FROM ig_document
            WHERE is_canonical AND NOT excluded AND parse_status IN ('extracted', 'ocr_done')
            ORDER BY doc_type, title
            """
        )
        docs = cur.fetchall()
    conn.close()
    if not docs:
        print("[ERROR] 无已提取文档")
        return 2

    n_missing, total_chars = 0, 0
    with open(MANIFEST, "w", encoding="utf-8") as out:
        for doc_id, title, dtype, year, org, bundle, status, text_path in docs:
            p = Path(text_path)
            if not p.is_file():
                n_missing += 1
                continue
            chars = p.stat().st_size
            total_chars += chars
            out.write(json.dumps({
                "doc_id": doc_id, "title": title, "doc_type": dtype, "year": year,
                "org": org, "bundle": bundle, "parse_status": status,
                "text_path": str(p), "approx_chars": chars,
            }, ensure_ascii=False) + "\n")

    print(f"[T3] manifest 写入 {len(docs) - n_missing} 条；缺失文件 {n_missing}；"
          f"语料总字符 {total_chars / 1e6:.1f}M；路径 {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
