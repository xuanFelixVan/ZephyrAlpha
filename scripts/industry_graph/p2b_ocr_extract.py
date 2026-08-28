# [MODULE] scripts.industry_graph.p2b_ocr_extract
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); rapidocr_onnxruntime; pymupdf
# [CONSUMERS] P3a 结构化抽取; P3b 语料库
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等: 已完成(ocr_done/extracted)的 doc 跳过; PDF先尝试免OCR文字层(>=20字/页)再渲染OCR; 语料按 doc_id 命名
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单文件失败->parse_status='failed'继续; OCR引擎初始化失败->退出码2
# [TTL] permanent
"""T2/P2b：图片型文档 OCR 提取（RapidOCR CPU 引擎）。

处理队列（幂等，可中断重跑）：
  - doc_type='panorama_pdf' 且 parse_status='pending'（先试文字层，薄则渲染 OCR）
  - doc_type='research_report' 且 parse_status='empty'（T1 提出的空壳扫描件）
  - doc_type='atlas_image' 且 parse_status='pending'（PNG/JPG 图谱直接 OCR）

OCR 结果按页拼接写入语料目录 {doc_id}.md，回写 parse_status='ocr_done'。
单实例串行（CPU 推理，多开无收益），支持 --limit 抽样验证。

用法::

    python scripts/industry_graph/p2b_ocr_extract.py [--limit 20]
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import numpy as np
import pymupdf

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

CORPUS_DIR = Path(r"E:\数据下载\产业链数据_P2语料")
_TEXT_LAYER_MIN_PER_PAGE = 20  # 每页平均文字层低于此值判定为图片型，走 OCR
_DPI = 200


def _pdf_text_layer(path: str) -> tuple[str, int]:
    """免 OCR 快路径：返回 (全文, 页数)。文字层太薄时调用方决定走 OCR。"""
    doc = pymupdf.open(path)
    parts = []
    for i, page in enumerate(doc):
        parts.append(f"\n\n<!-- page {i + 1} -->\n")
        parts.append(page.get_text())
    n = len(doc)
    doc.close()
    return "".join(parts).strip(), n


def _ocr_pdf(engine, path: str) -> str:
    doc = pymupdf.open(path)
    parts = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=_DPI)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = img[:, :, :3]
        result, _ = engine(img)
        parts.append(f"\n\n<!-- page {i + 1} -->\n")
        if result:
            parts.append("\n".join(line[1] for line in result))
    doc.close()
    return "".join(parts).strip()


def _ocr_image(engine, path: str) -> str:
    result, _ = engine(path)
    return "\n".join(line[1] for line in result).strip() if result else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个（抽样验证）")
    args = ap.parse_args()

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("[ERROR] rapidocr_onnxruntime 未安装")
        return 2
    engine = RapidOCR()

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_depgraph_pg_connection(read_only=False, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, source_root || '\\' || relative_path, doc_type
            FROM ig_document
            WHERE is_canonical AND NOT excluded AND (
                (doc_type = 'panorama_pdf' AND parse_status = 'pending')
                OR (doc_type = 'research_report' AND parse_status = 'empty')
                OR (doc_type = 'atlas_image' AND parse_status = 'pending')
            )
            ORDER BY doc_type, size_bytes
            """
        )
        docs = cur.fetchall()
    if args.limit:
        docs = docs[: args.limit]
    print(f"[T2] OCR 队列 {len(docs)} 个文档")

    stats = {"ocr_done": 0, "extracted": 0, "empty": 0, "failed": 0}
    t0 = time.time()
    with conn.cursor() as cur:
        for idx, (doc_id, path, dtype) in enumerate(docs, 1):
            try:
                if dtype == "atlas_image":
                    text = _ocr_image(engine, path)
                    status = "ocr_done" if len(text) >= 10 else "empty"
                else:
                    text, n_pages = _pdf_text_layer(path)
                    if len(text) >= _TEXT_LAYER_MIN_PER_PAGE * max(n_pages, 1):
                        status = "extracted"  # 文字层够用，免 OCR
                    else:
                        text = _ocr_pdf(engine, path)
                        status = "ocr_done" if len(text) >= 10 else "empty"
                if status in ("ocr_done", "extracted"):
                    (CORPUS_DIR / f"{doc_id}.md").write_text(text, encoding="utf-8")
                    cur.execute(
                        "UPDATE ig_document SET parse_status=%s, extracted_text_path=%s, updated_at=now() WHERE doc_id=%s",
                        (status, str(CORPUS_DIR / f"{doc_id}.md"), doc_id),
                    )
                else:
                    cur.execute(
                        "UPDATE ig_document SET parse_status=%s, updated_at=now() WHERE doc_id=%s",
                        (status, doc_id),
                    )
                stats[status] += 1
            except Exception as exc:  # noqa: BLE001
                stats["failed"] += 1
                cur.execute(
                    "UPDATE ig_document SET parse_status='failed', updated_at=now() WHERE doc_id=%s",
                    (doc_id,),
                )
                print(f"[WARN] {doc_id} {path}: {str(exc)[:150]}")
            if idx % 20 == 0:
                rate = idx / max(time.time() - t0, 1)
                eta = (len(docs) - idx) / max(rate, 0.01) / 60
                print(f"[PROGRESS] {idx}/{len(docs)} stats={stats} 速率={rate:.2f}个/s ETA={eta:.0f}分钟")
    conn.close()
    print(f"[T2] 完成: {stats}, 总耗时 {(time.time() - t0) / 60:.1f} 分钟")
    return 0


if __name__ == "__main__":
    sys.exit(main())
