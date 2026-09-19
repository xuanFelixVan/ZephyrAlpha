# [BLUEPRINT] MOD-ENTITY-GRAPH | docs/_working/altdata_line/02_entity_graph_equity_person.md | §
# [MODULE] scripts.entity_graph.apply_entity_graph_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] scripts.entity_graph.entity_graph_ingest; scripts.entity_graph.equity_penetration
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: entity_graph 六表+穿透函数 DDL 真源即本文件(照 scripts/industry_graph/apply_industry_graph_ddl.py 模式);
#   全部幂等(CREATE IF NOT EXISTS + ADD COLUMN IF NOT EXISTS + CREATE OR REPLACE FUNCTION);
#   设计真源=docs/_working/altdata_line/02_entity_graph_equity_person.md 六决策:
#   ①uscc 主键(node_company.uscc PK;node_entity.uscc 可空+部分唯一索引,缺失时名字符串键+low_confidence)
#   ②PIT 双轴(事实时间 valid_from/valid_to ≠ 采集时间 ingested_at;变更追加新版本不覆盖)
#   ③持股≠控制(role 与 control 分离,一致行动/表决权委托/代持/VIE 图上不可见)
#   ④境外穿透断线(BVI/开曼即止,不编造边)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG不可达->打印错误+退出码2; 执行失败->抛出非零退出
# [TESTS] 2026-09-19 首跑: 六表+equity_penetration(TEXT,INT,DATE) 部署成功; 幂等复跑通过(含 DROP 旧签名重载); 三家样本穿透链实测通过
# [TTL] permanent
"""实体图（entity_graph）六表+N 度股权穿透函数 DDL 部署脚本（PostgreSQL depgraph 图谱域）。

表结构（2026-09-17 设计定稿 docs/_working/altdata_line/02_entity_graph_equity_person.md；W7 施工 2026-09-19）：
    node_entity   统一节点表（person/company 统一身份锚；uscc 可空+low_confidence 标记）
    node_person   人物明细（曾用名/出生年份/任职轨迹 hash/关联公司交集——消歧金矿）
    node_company  公司明细（uscc PK；注册资本/成立日期/注册地址/行业/年报电话邮箱——共现挖掘暗器）
    edge_holding  股权边（from_entity→to_entity；比例/出资额；role；PIT 双轴版本化追加不覆盖）
    edge_role     任职边（person↔company 职务；带版本区间，与股权边同权重）
    edge_link     隐形边（同电话/同邮箱/同地址/共同任职/共同持股/同校/同前雇主；每条带证据+as_of）
    equity_penetration()  N 度向上穿透函数（输入公司→股东链递归，path 数组防环，默认现行版本 valid_to IS NULL）

edge_tech/edge_inventor/edge_family 按设计不建新表（同一 node_entity，第二批续聊）。
node_entity.symbol 为 A 股上市代码锚（canonical symbol，部分唯一）——A 层 akshare 无 uscc 的
上市实体身份落点；uscc 富化后 symbol 保留为上市 handle（与 ig_entity_code_map 互补，防双真源：
本表只挂 entity↔代码归属，代码↔市场映射真源仍在 ig_entity_code_map）。

用法::

    python scripts/entity_graph/apply_entity_graph_ddl.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# ========== DDL 定义（真源） ==========

DDL_STATEMENTS = [
    # ========== W7-1（2026-09-19，设计真源 02_entity_graph_equity_person.md §2/§4） ==========
    """
    CREATE TABLE IF NOT EXISTS node_entity (
        entity_id      TEXT PRIMARY KEY,
        entity_type    TEXT NOT NULL CHECK (entity_type IN ('person', 'company')),
        name           TEXT NOT NULL,
        name_norm      TEXT NOT NULL,
        symbol         TEXT,
        uscc           TEXT,
        low_confidence BOOLEAN NOT NULL DEFAULT FALSE,
        source         TEXT NOT NULL,
        first_seen     DATE,
        last_seen      DATE,
        created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    # uscc 事实主键（决策①）：非空即全库唯一
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_node_entity_uscc ON node_entity (uscc) WHERE uscc IS NOT NULL",
    # 上市代码锚：一个代码一个实体
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_node_entity_symbol ON node_entity (symbol) WHERE symbol IS NOT NULL",
    # 名字符串键身份（uscc 缺失路径，low_confidence=TRUE 标记同名合并风险）
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_node_entity_namestr ON node_entity (entity_type, name_norm) WHERE uscc IS NULL",
    "CREATE INDEX IF NOT EXISTS idx_node_entity_name_norm ON node_entity (name_norm)",
    "CREATE INDEX IF NOT EXISTS idx_node_entity_type ON node_entity (entity_type)",
    """
    CREATE TABLE IF NOT EXISTS node_person (
        person_id       TEXT PRIMARY KEY REFERENCES node_entity(entity_id),
        former_names    TEXT[] NOT NULL DEFAULT '{}',
        birth_year      SMALLINT,
        career_hash     TEXT,
        company_overlap TEXT[] NOT NULL DEFAULT '{}',
        created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    # node_company.uscc = PK（决策①，A 层无 uscc 源故 v1 空，B/C/D 层富化回填）
    """
    CREATE TABLE IF NOT EXISTS node_company (
        uscc          TEXT PRIMARY KEY,
        reg_capital   TEXT,
        est_date      DATE,
        reg_address   TEXT,
        industry      TEXT,
        annual_phone  TEXT,
        annual_email  TEXT,
        status        TEXT,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS edge_holding (
        edge_id       BIGSERIAL PRIMARY KEY,
        from_entity   TEXT NOT NULL REFERENCES node_entity(entity_id),
        to_entity     TEXT NOT NULL REFERENCES node_entity(entity_id),
        stake_pct     NUMERIC,
        shares        NUMERIC,
        shares_type   TEXT,
        role          TEXT NOT NULL DEFAULT 'shareholder',
        rank_no       SMALLINT,
        hold_change   NUMERIC,
        valid_from    DATE NOT NULL,
        valid_to      DATE,
        announce_date DATE,
        source        TEXT NOT NULL,
        source_ref    TEXT,
        ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (from_entity, to_entity, role, valid_from, source)
    )
    """,
    # 边 role 词表（持股≠控制，决策③）：shareholder(股东)/invests_in(被投)/subsidiary(子公司)/
    # actual_control(实控)/gp(普通合伙人)/lp(有限合伙人)/concert_party(一致行动人)
    # —— control_method 类信号进 role,不与 stake_pct 混算
    "CREATE INDEX IF NOT EXISTS idx_edge_holding_from ON edge_holding (from_entity)",
    "CREATE INDEX IF NOT EXISTS idx_edge_holding_to ON edge_holding (to_entity)",
    "CREATE INDEX IF NOT EXISTS idx_edge_holding_valid_to ON edge_holding (valid_to)",
    "CREATE INDEX IF NOT EXISTS idx_edge_holding_to_from ON edge_holding (to_entity, from_entity)",
    """
    CREATE TABLE IF NOT EXISTS edge_role (
        edge_id       BIGSERIAL PRIMARY KEY,
        from_entity   TEXT NOT NULL REFERENCES node_entity(entity_id),
        to_entity     TEXT NOT NULL REFERENCES node_entity(entity_id),
        title         TEXT NOT NULL,
        title_norm    TEXT,
        valid_from    DATE,
        valid_to      DATE,
        announce_date DATE,
        source        TEXT NOT NULL,
        source_ref    TEXT,
        ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (from_entity, to_entity, title, valid_from, source)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_edge_role_from ON edge_role (from_entity)",
    "CREATE INDEX IF NOT EXISTS idx_edge_role_to ON edge_role (to_entity)",
    """
    CREATE TABLE IF NOT EXISTS edge_link (
        edge_id       BIGSERIAL PRIMARY KEY,
        from_entity   TEXT NOT NULL REFERENCES node_entity(entity_id),
        to_entity     TEXT NOT NULL REFERENCES node_entity(entity_id),
        link_type     TEXT NOT NULL,
        evidence      TEXT,
        as_of         DATE,
        valid_from    DATE,
        valid_to      DATE,
        source        TEXT NOT NULL,
        source_ref    TEXT,
        ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (from_entity, to_entity, link_type, as_of, source)
    )
    """,
    # link_type 词表：same_phone/same_email/same_address/co_director/co_holder/same_school/former_employer
    "CREATE INDEX IF NOT EXISTS idx_edge_link_from ON edge_link (from_entity)",
    "CREATE INDEX IF NOT EXISTS idx_edge_link_to ON edge_link (to_entity)",
    "CREATE INDEX IF NOT EXISTS idx_edge_link_type ON edge_link (link_type)",
    # ========== N 度股权穿透函数（W7-3）：输入公司（entity_id/symbol/name_norm 皆可）→向上 N 层股东链 ==========
    # 先卸 2 参旧签名（CREATE OR REPLACE 换签名=新重载,不覆盖,防双真源）
    "DROP FUNCTION IF EXISTS equity_penetration(TEXT, INT)",
    # p_min_valid_from: 观测窗下沿（可选）——A 层"最后观测即现行"语义下,过滤陈年观测
    # （十大股东掉榜≠卖出,valid_to=NULL=最后观测态;要最新快照传当期 report_period）
    """
    CREATE OR REPLACE FUNCTION equity_penetration(
        p_root           TEXT,
        p_max_depth      INT DEFAULT 5,
        p_min_valid_from DATE DEFAULT NULL
    )
    RETURNS TABLE (
        depth      INT,
        from_entity TEXT,
        from_name  TEXT,
        from_type  TEXT,
        to_entity  TEXT,
        to_name    TEXT,
        role       TEXT,
        stake_pct  NUMERIC,
        valid_from DATE
    )
    LANGUAGE SQL
    STABLE
    AS $func$
        WITH RECURSIVE walk AS (
            SELECT 1 AS depth,
                   h.from_entity, h.to_entity, h.role, h.stake_pct, h.valid_from,
                   ARRAY[h.to_entity, h.from_entity] AS path
            FROM edge_holding h
            JOIN node_entity root ON root.entity_id = h.to_entity
            WHERE (root.entity_id = p_root OR root.symbol = p_root OR root.name_norm = p_root)
              AND h.valid_to IS NULL
              AND (p_min_valid_from IS NULL OR h.valid_from >= p_min_valid_from)
            UNION ALL
            SELECT w.depth + 1,
                   h.from_entity, h.to_entity, h.role, h.stake_pct, h.valid_from,
                   w.path || h.from_entity
            FROM walk w
            JOIN edge_holding h ON h.to_entity = w.from_entity
            WHERE h.valid_to IS NULL
              AND (p_min_valid_from IS NULL OR h.valid_from >= p_min_valid_from)
              AND w.depth < p_max_depth
              AND NOT (h.from_entity = ANY(w.path))
        )
        SELECT w.depth, w.from_entity, fe.name, fe.entity_type,
               w.to_entity, te.name, w.role, w.stake_pct, w.valid_from
        FROM walk w
        JOIN node_entity fe ON fe.entity_id = w.from_entity
        JOIN node_entity te ON te.entity_id = w.to_entity
        ORDER BY w.depth, w.to_entity, w.stake_pct DESC NULLS LAST
    $func$
    """,
]

# 裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: reader 只读 / writer 读写（照 ig_* 先例）
_ALL_TABLES = (
    "node_entity",
    "node_person",
    "node_company",
    "edge_holding",
    "edge_role",
    "edge_link",
)
GRANT_STATEMENTS = (
    [f"GRANT SELECT ON {t} TO depgraph_reader" for t in _ALL_TABLES]
    + [f"GRANT SELECT, INSERT, UPDATE, DELETE ON {t} TO depgraph_writer" for t in _ALL_TABLES]
    + [
        "GRANT USAGE, SELECT ON SEQUENCE edge_holding_edge_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE edge_role_edge_id_seq TO depgraph_writer",
        "GRANT USAGE, SELECT ON SEQUENCE edge_link_edge_id_seq TO depgraph_writer",
        "GRANT EXECUTE ON FUNCTION equity_penetration(TEXT, INT, DATE) TO depgraph_reader, depgraph_writer",
    ]
)


# 裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: reader 只读 / writer 读写（照 ig_* 先例）
# SQL 集中化（§5.160.2）
SQL_LIST_ENTITY_TABLES = """
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN ('node_entity','node_person','node_company',
                         'edge_holding','edge_role','edge_link')
    ORDER BY table_name
"""
SQL_COUNT_PENETRATION_FN = "SELECT count(*) FROM information_schema.routines WHERE routine_name = 'equity_penetration'"


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
        cur.execute(SQL_LIST_ENTITY_TABLES)
        tables = [r[0] for r in cur.fetchall()]
        cur.execute(SQL_COUNT_PENETRATION_FN)
        fn_count = cur.fetchall()[0][0]
    conn.close()

    print(f"[OK] entity_graph 表部署完成: {tables} | equity_penetration 函数: {fn_count} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
