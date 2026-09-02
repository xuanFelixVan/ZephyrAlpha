# [MODULE] scripts.industry_graph.apply_industry_graph_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts.industry_graph.p0_scan_documents
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: ig_* 五表 DDL 真源即本文件; 全部幂等(CREATE IF NOT EXISTS); 角色分级 GRANT 幂等
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG不可达->打印错误+退出码2; 执行失败->抛出非零退出
# [TTL] permanent
"""产业链图谱（industry_graph）五表 DDL 部署脚本（PostgreSQL depgraph 图谱域）。

表结构（2026-08-27 与用户定稿）：
    ig_chain         产业链主表
    ig_node          环节节点（上游/中游/下游/设备/材料）
    ig_edge          环节间结构边（edge_type='structure'|'supply'，supply 公司级后置）
    ig_node_company  环节↔股票映射（龙头/主要/概念）
    ig_document      源文档登记表（P0 盘点使用，兼作语料库入口）

市场分片规范：五表均带 market 字段，当前批次全部为 'cn'。

用法::

    python scripts/industry_graph/apply_industry_graph_ddl.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# ========== DDL 定义（真源） ==========

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS ig_chain (
        chain_id     TEXT PRIMARY KEY,
        name         TEXT NOT NULL,
        category     TEXT,
        version_year SMALLINT,
        market       TEXT NOT NULL DEFAULT 'cn',
        status       TEXT NOT NULL DEFAULT 'active',
        source_note  TEXT,
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ig_node (
        node_id     TEXT PRIMARY KEY,
        chain_id    TEXT NOT NULL REFERENCES ig_chain(chain_id),
        name        TEXT NOT NULL,
        tier        TEXT,
        aliases     TEXT[],
        description TEXT,
        market      TEXT NOT NULL DEFAULT 'cn',
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ig_edge (
        edge_id    BIGSERIAL PRIMARY KEY,
        from_node  TEXT NOT NULL REFERENCES ig_node(node_id),
        to_node    TEXT NOT NULL REFERENCES ig_node(node_id),
        edge_type  TEXT NOT NULL DEFAULT 'structure',
        source_doc TEXT,
        market     TEXT NOT NULL DEFAULT 'cn',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (from_node, to_node, edge_type)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ig_node_company (
        id            BIGSERIAL PRIMARY KEY,
        node_id       TEXT NOT NULL REFERENCES ig_node(node_id),
        symbol        TEXT NOT NULL,
        role          TEXT,
        confidence    REAL,
        evidence_text TEXT,
        source_doc    TEXT,
        market        TEXT NOT NULL DEFAULT 'cn',
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (node_id, symbol)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ig_document (
        doc_id              TEXT PRIMARY KEY,
        relative_path       TEXT NOT NULL UNIQUE,
        source_root         TEXT,
        bundle              TEXT NOT NULL,
        file_name           TEXT NOT NULL,
        ext                 TEXT NOT NULL,
        size_bytes          BIGINT,
        mtime               TIMESTAMPTZ,
        file_hash           TEXT,
        dedup_group         TEXT,
        is_canonical        BOOLEAN NOT NULL DEFAULT TRUE,
        doc_type            TEXT NOT NULL,
        title               TEXT,
        year                SMALLINT,
        org                 TEXT,
        market              TEXT NOT NULL DEFAULT 'cn',
        excluded            BOOLEAN NOT NULL DEFAULT FALSE,
        exclude_reason      TEXT,
        parse_status        TEXT NOT NULL DEFAULT 'pending',
        extracted_text_path TEXT,
        source_note         TEXT NOT NULL DEFAULT 'taobao_purchase_internal_only',
        created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    # 已存在库的增量升级（幂等）
    "ALTER TABLE ig_document ADD COLUMN IF NOT EXISTS source_root TEXT",
    # P1: 解压产物指向来源压缩包 doc_id
    "ALTER TABLE ig_document ADD COLUMN IF NOT EXISTS parent_doc TEXT",
    """
    CREATE TABLE IF NOT EXISTS ig_company_edge (
        edge_id     BIGSERIAL PRIMARY KEY,
        from_symbol TEXT NOT NULL,
        to_symbol   TEXT NOT NULL,
        year        SMALLINT NOT NULL,
        product     TEXT,
        weight      REAL,
        weight_type TEXT,
        source      TEXT NOT NULL,
        source_doc  TEXT,
        from_name   TEXT,
        to_name     TEXT,
        amount      NUMERIC,
        rank        SMALLINT,
        market      TEXT NOT NULL DEFAULT 'cn',
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (from_symbol, to_symbol, year, source)
    )
    """,
    # 已存在库的增量升级（幂等）。约定：to_symbol='' 表示对手方为非上市公司，名称在 to_name
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS from_name TEXT",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS to_name TEXT",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS amount NUMERIC",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS rank SMALLINT",
    """
    CREATE TABLE IF NOT EXISTS ig_company_metric (
        id         BIGSERIAL PRIMARY KEY,
        symbol     TEXT NOT NULL,
        year       SMALLINT NOT NULL,
        metric     TEXT NOT NULL,
        value      REAL,
        value_aux  REAL,
        source     TEXT NOT NULL,
        market     TEXT NOT NULL DEFAULT 'cn',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (symbol, year, metric, source)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ig_document_dedup ON ig_document (dedup_group)",
    "CREATE INDEX IF NOT EXISTS idx_ig_document_type ON ig_document (doc_type)",
    "CREATE INDEX IF NOT EXISTS idx_ig_document_status ON ig_document (parse_status)",
    "CREATE INDEX IF NOT EXISTS idx_ig_node_chain ON ig_node (chain_id)",
    "CREATE INDEX IF NOT EXISTS idx_ig_node_company_symbol ON ig_node_company (symbol)",
    "CREATE INDEX IF NOT EXISTS idx_ig_company_edge_from ON ig_company_edge (from_symbol)",
    "CREATE INDEX IF NOT EXISTS idx_ig_company_edge_to ON ig_company_edge (to_symbol)",
    "CREATE INDEX IF NOT EXISTS idx_ig_company_metric_sym ON ig_company_metric (symbol, metric)",
]

# 裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: reader 只读 / writer 读写
_ALL_TABLES = (
    "ig_chain",
    "ig_node",
    "ig_edge",
    "ig_node_company",
    "ig_document",
    "ig_company_edge",
    "ig_company_metric",
)
GRANT_STATEMENTS = (
    [f"GRANT SELECT ON {t} TO depgraph_reader" for t in _ALL_TABLES]
    + [f"GRANT SELECT, INSERT, UPDATE, DELETE ON {t} TO depgraph_writer" for t in _ALL_TABLES]
    + [
        # BIGSERIAL 序列需 USAGE 才能插入
        "GRANT USAGE, SELECT ON SEQUENCE ig_edge_edge_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE ig_node_company_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE ig_company_edge_edge_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE ig_company_metric_id_seq TO depgraph_writer",
    ]
)


def main() -> int:
    try:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] PostgreSQL 不可达: {exc}")
        return 2

    with conn.cursor() as cur:
        for stmt in DDL_STATEMENTS:
            cur.execute(stmt)
        for stmt in GRANT_STATEMENTS:
            cur.execute(stmt)
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'ig\\_%'
            ORDER BY table_name
            """
        )
        tables = [r[0] for r in cur.fetchall()]
    conn.close()

    print(f"[OK] industry_graph 表部署完成: {tables}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
