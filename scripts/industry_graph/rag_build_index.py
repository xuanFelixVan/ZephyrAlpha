# [MODULE] scripts.industry_graph.rag_build_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] sentence_transformers; zephyr.governance.depgraph_schema
# [CONSUMERS] scripts.industry_graph.rag_query; 前端 RAG 问答视图
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等重建; 分块按页标记再滑窗; 向量 L2 归一化(余弦=点积); chunks.sqlite 行序与 embeddings.npy 一致
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 模型下载失败->切 hf-mirror 重试一次; 无语料->退出码2
# [TTL] permanent
"""RAG 检索层构建：语料分块 + bge-small-zh 向量化（CPU 本地推理）。

语料 manifest.jsonl → 分块（页标记切分 + 800 字滑窗 step 500）
→ chunks.sqlite（chunk 元数据）+ embeddings.npy（float32 N×512，已归一化）。

用法::

    python scripts/industry_graph/rag_build_index.py [--limit 20]
"""

from __future__ import annotations

import argparse
import json
import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 必须先于 sentence_transformers 导入（常量导入期固化）

import re
import sqlite3
import sys
import time
from pathlib import Path

CORPUS_DIR = Path(r"E:\数据下载\产业链数据_P2语料")
MANIFEST = CORPUS_DIR / "manifest.jsonl"
SQLITE_OUT = CORPUS_DIR / "chunks.sqlite"
EMB_OUT = CORPUS_DIR / "embeddings.npy"
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
_PAGE_RE = re.compile(r"<!--\s*page\s*\d+\s*-->")
_WIN, _STEP, _MIN = 800, 500, 50


def load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def chunk_text(text: str) -> list[str]:
    pages = _PAGE_RE.split(text)
    chunks = []
    for pg in pages:
        pg = pg.strip()
        if len(pg) < _MIN:
            continue
        if len(pg) <= _WIN:
            chunks.append(pg)
        else:
            for i in range(0, len(pg) - _MIN, _STEP):
                chunks.append(pg[i : i + _WIN])
    return chunks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if not MANIFEST.is_file():
        print(f"[ERROR] manifest 不存在: {MANIFEST}")
        return 2
    docs = [json.loads(line) for line in open(MANIFEST, encoding="utf-8")]
    if args.limit:
        docs = docs[: args.limit]
    print(f"[RAG] 文档 {len(docs)} 份，开始分块 ...")

    rows = []
    for d in docs:
        try:
            text = open(d["text_path"], encoding="utf-8").read()
        except OSError:
            continue
        for seq, chunk in enumerate(chunk_text(text)):
            rows.append((f"{d['doc_id']}#{seq}", d["doc_id"], d["title"], d["doc_type"],
                         d.get("year"), chunk))
    print(f"[RAG] 分块 {len(rows)} 条")

    if SQLITE_OUT.exists():
        SQLITE_OUT.unlink()
    db = sqlite3.connect(SQLITE_OUT)
    db.execute(
        "CREATE TABLE chunks (chunk_id TEXT PRIMARY KEY, doc_id TEXT, title TEXT, doc_type TEXT, year INTEGER, chunk_text TEXT)"
    )
    db.executemany("INSERT INTO chunks VALUES (?,?,?,?,?,?)", rows)
    db.execute("CREATE INDEX idx_chunks_doc ON chunks (doc_id)")
    db.commit()
    db.close()

    print(f"[RAG] 加载模型 {MODEL_NAME} 并向量化 ...")
    model = load_model()
    import numpy as np

    texts = [r[5] for r in rows]
    t0 = time.time()
    emb = model.encode(
        texts, batch_size=64, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True,
    ).astype(np.float32)
    np.save(EMB_OUT, emb)
    dt = time.time() - t0
    print(f"[RAG] 完成: {emb.shape[0]} 条 × {emb.shape[1]} 维, 耗时 {dt / 60:.1f} 分钟 "
          f"({emb.shape[0] / max(dt, 1):.0f} 条/s), 向量存 {EMB_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
