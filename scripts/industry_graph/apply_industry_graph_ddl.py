# [MODULE] scripts.industry_graph.apply_industry_graph_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts.industry_graph.p0_scan_documents
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: ig_* 九表 DDL 真源即本文件; 全部幂等(CREATE IF NOT EXISTS + ADD COLUMN IF NOT EXISTS); 角色分级 GRANT 幂等; v2 增量(SOP §4.8/§4.9): ig_company_edge PIT 三时间戳+边元数据五列, ig_chunk/ig_fact 内容层与事实层
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG不可达->打印错误+退出码2; 执行失败->抛出非零退出
# [TTL] permanent
"""产业链图谱（industry_graph）十三表 DDL 部署脚本（PostgreSQL depgraph 图谱域）。

表结构（2026-08-27 与用户定稿；v2 2026-09-07 按 SOP §4.8/§4.9 增补；v3 2026-09-08 按 SOP §4.10 增补；v4 2026-09-09 深度体系+分域增补；v5 2026-09-09 收尾增补 ig_chain.level；v6 2026-09-10 增补 ig_unlisted_entity.covered）：
    ig_chain         产业链主表
    ig_node          环节节点（v4: +child_chain_id/drill_status 层级下钻）
    ig_edge          环节间结构边（edge_type='structure'|'supply'，supply 公司级后置）
    ig_node_company  环节↔股票映射（v4: +PIT 三时间戳+pit_strength）
    ig_document      源文档登记表（P0 盘点使用，兼作语料库入口）
    ig_company_edge  公司间供应链边（v2: PIT 三时间戳+边元数据 v2；v4: +capacity/exclusivity 供给侧）
    ig_company_metric 公司年度指标（供应链集中度指标层，v4: +PIT 化）
    ig_chunk         内容层（E盘语料 76,112 块全量入库，内容颗粒度零丢失）
    ig_fact          事实层（五元组事实，回链证据块，量化可 SQL 检索最小单元）
    ig_unlisted_entity 未上市实体编码表（v3: UE- 永久编码+上市替换，SOP §4.10）
    ig_equity_edge   股权穿透边表（v4: 业务/资本分域——被投/持股/实控，与 ig_company_edge 分开）
    ig_product_revenue 产品营收归因表（v4: 图谱侧财务唯一表，通用财务主数据进 c1_market 防双真源）
    （v5 2026-09-09 收尾: ig_chain.level 链层级列——模板决策#8 level 落库、parent 派生）
    （v6 2026-09-10: ig_unlisted_entity.covered 主数据收录标记——外部实体留痕登记,产业链↔主数据对账桥梁）

市场分片规范：各表均带 market 字段（ig_chunk/ig_unlisted_entity 除外——语料/实体无市场语义）。

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
    # v7 增量(2026-09-11 ig_fact 事实层 PIT 收口,Owner 裁定): 事实层关闭唯一通道=ingest
    # fact_close 盖 valid_to(幂等可逆,禁 DELETE);分析查询默认 valid_to IS NULL 过滤
    "ALTER TABLE ig_fact ADD COLUMN IF NOT EXISTS valid_to DATE",
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
    # ========== v2 增量（SOP industry_chain_data_audit_sop §4.8/§4.9，2026-09-07 Owner 裁定） ==========
    # --- ig_company_edge PIT 三时间戳 + 边元数据 v2（FactSet/Bloomberg 对标） ---
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS valid_from DATE",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS valid_to DATE",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS as_of DATE",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS evidence_type TEXT",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS revenue_pct REAL",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS subsidiary TEXT",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS relevance SMALLINT",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS transmission_type TEXT[]",
    "CREATE INDEX IF NOT EXISTS idx_ig_company_edge_valid_from ON ig_company_edge (valid_from)",
    "CREATE INDEX IF NOT EXISTS idx_ig_company_edge_valid_to ON ig_company_edge (valid_to)",
    "CREATE INDEX IF NOT EXISTS idx_ig_company_edge_as_of ON ig_company_edge (as_of)",
    # --- ig_chunk 内容层（E盘 chunks.sqlite 76,112 块全量入库，内容颗粒度零丢失） ---
    """
    CREATE TABLE IF NOT EXISTS ig_chunk (
        chunk_id   TEXT PRIMARY KEY,
        doc_id     TEXT REFERENCES ig_document(doc_id),
        title      TEXT,
        doc_type   TEXT,
        year       SMALLINT,
        chunk_text TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ig_chunk_doc ON ig_chunk (doc_id)",
    "CREATE INDEX IF NOT EXISTS idx_ig_chunk_type ON ig_chunk (doc_type)",
    # --- ig_fact 事实层（量化可检索的最小事实单元，每条回链证据块） ---
    """
    CREATE TABLE IF NOT EXISTS ig_fact (
        fact_id            BIGSERIAL PRIMARY KEY,
        subject            TEXT NOT NULL,
        relation           TEXT NOT NULL,
        object             TEXT NOT NULL,
        value              TEXT,
        evidence_chunk_id  TEXT REFERENCES ig_chunk(chunk_id),
        confidence         REAL,
        as_of              DATE,
        source             TEXT NOT NULL DEFAULT 'websearch',
        market             TEXT NOT NULL DEFAULT 'cn',
        created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (subject, relation, object, as_of, source)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ig_fact_subject ON ig_fact (subject)",
    "CREATE INDEX IF NOT EXISTS idx_ig_fact_object ON ig_fact (object)",
    "CREATE INDEX IF NOT EXISTS idx_ig_fact_relation ON ig_fact (relation)",
    # ========== v3 增量（SOP industry_chain_data_audit_sop §4.10，2026-09-08 Owner 裁定：现在就干） ==========
    # --- ig_unlisted_entity 未上市实体编码表（UE- 永久编码，上市后一键替换全库存量边） ---
    """
    CREATE TABLE IF NOT EXISTS ig_unlisted_entity (
        ue_id         TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        country       TEXT NOT NULL DEFAULT 'CN',
        status        TEXT NOT NULL DEFAULT 'unlisted',
        listed_symbol TEXT,
        source_doc    TEXT,
        as_of         DATE,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (name, country)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ig_unlisted_name ON ig_unlisted_entity (name)",
    "CREATE INDEX IF NOT EXISTS idx_ig_unlisted_status ON ig_unlisted_entity (status)",
    "CREATE INDEX IF NOT EXISTS idx_ig_unlisted_symbol ON ig_unlisted_entity (listed_symbol)",
    # ========== v4 增量（graph_quality_standard.md §6 深度体系，2026-09-09 Owner 定稿） ==========
    # --- ig_node 层级下钻列（子链挂接+砖标记） ---
    "ALTER TABLE ig_node ADD COLUMN IF NOT EXISTS child_chain_id TEXT",
    "ALTER TABLE ig_node ADD COLUMN IF NOT EXISTS drill_status TEXT",
    "CREATE INDEX IF NOT EXISTS idx_ig_node_child ON ig_node (child_chain_id)",
    # --- ig_node_company PIT 列（S13/S4 引擎转正前提,graph_quality_standard.md §4） ---
    "ALTER TABLE ig_node_company ADD COLUMN IF NOT EXISTS valid_from DATE",
    "ALTER TABLE ig_node_company ADD COLUMN IF NOT EXISTS valid_to DATE",
    "ALTER TABLE ig_node_company ADD COLUMN IF NOT EXISTS pit_strength TEXT",
    "CREATE INDEX IF NOT EXISTS idx_ig_node_company_valid_to ON ig_node_company (valid_to)",
    # --- ig_company_edge 供给侧两列（Owner 2026-09-09 裁定: capacity 产能+exclusivity 独供双供） ---
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS capacity TEXT",
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS exclusivity TEXT",
    # --- 边级新闻关键词（2026-09-09 全网调研: FactSet keywords 对标,新闻联动边级命中） ---
    "ALTER TABLE ig_company_edge ADD COLUMN IF NOT EXISTS keywords TEXT[]",
    # --- 环节职能角色列（Owner 2026-09-09 质疑裁定: tier 三值化位置语义,职能拆出,深交所八值词表） ---
    "ALTER TABLE ig_node ADD COLUMN IF NOT EXISTS function_role TEXT",
    # --- ig_node PIT 关闭列（2026-09-12 ig_fact 空壳链填充任务: 节点层治理收口,对标 ig_fact.valid_to
    #     先例——孤岛节点等治理对象的唯一合法处置=PIT 关闭(禁 DELETE);关闭只走 websearch_ingest node_close
    #     (幂等可逆,reason_doc 留痕);分析查询默认过滤 valid_to IS NULL） ---
    "ALTER TABLE ig_node ADD COLUMN IF NOT EXISTS valid_to DATE",
    # --- 股权表成本两列（Owner 2026-09-09 裁定: 取得成本+取得日,股权避坑核心） ---
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS acquisition_cost NUMERIC",
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS acquisition_date DATE",
    # --- 股权表 UBO 五列（2026-09-09 全网调研: 人行《受益所有人信息管理办法》+瑞士LETA+EU 5AMLD 国际对标） ---
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS voting_pct NUMERIC",
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS control_method TEXT",
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS holder_name TEXT",
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS holder_country TEXT",
    "ALTER TABLE ig_equity_edge ADD COLUMN IF NOT EXISTS verification TEXT",
    # --- 股权质押风险（2026-09-09 调研: 中登口径+2025 质押新规——质押=股权域事件,relation 扩枚举,
    #     预警线/平仓线/质押率放 relation='pledge' 行的 evidence/weight 列,不另加列） ---
    # relation 词表扩: invests_in/subsidiary/shareholding/actual_control/pledge(质押)/judicial_frozen(司法冻结)
    # --- ig_company_metric PIT 化（Owner 2026-09-09 裁定: 指标层保留不融不删,加 PIT 防回测切片前视） ---
    "ALTER TABLE ig_company_metric ADD COLUMN IF NOT EXISTS as_of DATE",
    "ALTER TABLE ig_company_metric ADD COLUMN IF NOT EXISTS valid_from DATE",
    "ALTER TABLE ig_company_metric ADD COLUMN IF NOT EXISTS valid_to DATE",
    # --- ig_equity_edge 股权穿透表（Owner 2026-09-09 三裁定: 同库独立表,业务/资本分域） ---
    """
    CREATE TABLE IF NOT EXISTS ig_equity_edge (
        edge_id     BIGSERIAL PRIMARY KEY,
        holder      TEXT NOT NULL,
        held        TEXT NOT NULL,
        stake_pct   NUMERIC,
        layer       SMALLINT NOT NULL DEFAULT 1,
        relation    TEXT NOT NULL,
        as_of       DATE,
        valid_from  DATE,
        valid_to    DATE,
        source      TEXT NOT NULL,
        source_doc  TEXT,
        evidence    TEXT,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (holder, held, as_of, source)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ig_equity_holder ON ig_equity_edge (holder)",
    "CREATE INDEX IF NOT EXISTS idx_ig_equity_held ON ig_equity_edge (held)",
    # --- ig_chain.level 链层级列（2026-09-09 收尾裁定: DDL v4 遗漏补建,模板决策#8="level 落库、parent 派生"——
#     根链=1,子链经 node.child_chain_id 递归=父+1;挂接写入时顺手落值防递归爆栈,一致性由 quality_closeout_check.py 抽查） ---
"ALTER TABLE ig_chain ADD COLUMN IF NOT EXISTS level SMALLINT",
"CREATE INDEX IF NOT EXISTS idx_ig_chain_level ON ig_chain (level)",
# --- ig_product_revenue 产品营收归因（图谱侧财务唯一表: symbol→产品→revenue_pct→挂环节;通用财务进 c1_market） ---
    """
    CREATE TABLE IF NOT EXISTS ig_product_revenue (
        id           BIGSERIAL PRIMARY KEY,
        symbol       TEXT NOT NULL,
        year         SMALLINT NOT NULL,
        product      TEXT NOT NULL,
        revenue_pct  REAL,
        node_ref     TEXT,
        source       TEXT NOT NULL,
        source_doc   TEXT,
        evidence     TEXT,
        as_of        DATE,
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (symbol, year, product, source)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ig_prodrev_symbol ON ig_product_revenue (symbol)",
    # ========== v6 增量（Owner 2026-09-10 指令: 外部实体留痕登记——凡查到代码或名字的非 A 股实体
    #     一律入编码表,多一个"主数据收录没有"标记;将来主数据扩源(北交所/美股/港股)后按 covered=false
    #     清单逐个 promote 对上,编码表即产业链↔主数据的对账桥梁） ---
    "ALTER TABLE ig_unlisted_entity ADD COLUMN IF NOT EXISTS covered BOOLEAN NOT NULL DEFAULT FALSE",
    "CREATE INDEX IF NOT EXISTS idx_ig_unlisted_covered ON ig_unlisted_entity (covered)",
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
    "ig_chunk",
    "ig_fact",
    "ig_unlisted_entity",
    "ig_equity_edge",
    "ig_product_revenue",
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
        "GRANT USAGE, SELECT ON SEQUENCE ig_fact_fact_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE ig_equity_edge_edge_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE ig_product_revenue_id_seq TO depgraph_writer",
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
