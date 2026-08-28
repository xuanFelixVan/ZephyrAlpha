# [MODULE] scripts.industry_graph.rag_query
# [DOMAIN] D_DATA
# [DEPENDENCIES] sentence_transformers; scripts.industry_graph.rag_build_index
# [CONSUMERS] 前端 RAG 问答视图
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读检索; 余弦相似度(归一化点积)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 索引不存在->退出码2
# [TTL] permanent
"""RAG 检索查询：自然语言 → top-k 语料块（带来源引用）。

用法::

    python scripts/industry_graph/rag_query.py "硅料环节有哪些公司" [--topk 5]
"""

from __future__ import annotations

import argparse
import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 必须先于 sentence_transformers 导入

import sqlite3
import sys
from pathlib import Path

CORPUS_DIR = Path(r"E:\数据下载\产业链数据_P2语料")
SQLITE = CORPUS_DIR / "chunks.sqlite"
EMB = CORPUS_DIR / "embeddings.npy"
MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--topk", type=int, default=5)
    args = ap.parse_args()

    if not SQLITE.is_file() or not EMB.is_file():
        print("[ERROR] 索引未构建，先跑 rag_build_index.py")
        return 2

    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)

    emb = np.load(EMB)
    db = sqlite3.connect(SQLITE)
    q = model.encode([args.query], normalize_embeddings=True, convert_to_numpy=True)[0]
    scores = emb @ q
    top = np.argpartition(-scores, args.topk)[: args.topk]
    top = top[np.argsort(-scores[top])]

    for rank, idx in enumerate(top, 1):
        row = db.execute(
            "SELECT chunk_id, title, doc_type, year, chunk_text FROM chunks WHERE rowid=?",
            (int(idx) + 1,),
        ).fetchone()
        print(f"\n[{rank}] score={scores[idx]:.3f} | {row[1]} ({row[2]}, {row[3]}) | {row[0]}")
        print(row[4][:300].replace("\n", " "))
    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
