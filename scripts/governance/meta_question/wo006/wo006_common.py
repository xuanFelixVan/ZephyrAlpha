# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.wo006_common
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection reader/writer); zephyr.shared.io.file_utils (safe_write_text CAS)
# [CONSUMERS] wo006 同族四件：probe_source_c_ths / generate_node_binding_candidates / apply_node_bindings /
#            generate_merged_node_convergence / generate_micro_chain_retirement_nominations / recompute_pq0064
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读口径 SQL 与 PQ-0064 判据逐字同构（覆盖率=链内有公司映射节点/链总节点，A 档=≥0.8，
#            分母=有节点链 871，活跃口径剔 name LIKE '%已并入%'）；wo006 写面纯 INSERT，
#            以 source_doc 前缀 'wo006' 作可机检排他标记（复算 before 口径=排除该前缀，可无损重构写前面）；
#            RULE-DATA-OPS 三验证（必要性/真实性/可逆性）在任何写之前打印并回写案卷；
#            旁挂册统一 columns+rows 列式 YAML（生成器产出，禁手工维护）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达→抛出（调用方非零退出）；注册表文件缺失→FileError 抛出（禁静默降级空册）
# [TESTS] 探针复核（.runtime/tmp/st-metaq-gc-20260924/wo006/p*.py）+ recompute_pq0064.py 自校验
#         （before 快照 == 排除 wo006 前缀的实盘重算，逐链数字相等才算通过）
# [TTL] task_bound
"""WO-006 共用件：PG 只读探针、PQ-0064 同口径复算、RULE-DATA-OPS 留痕、旁挂册 CAS 写。

口径真源=docs/_working/meta_question_answers/results/b2/PQ-0064.yaml 的 evidence.query 原文，
本文件 `pq0064_metrics()` 是其逐字机械化，禁在别处另立第二套覆盖率算法。
"""

from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

SESSION = "st-metaq-gc-20260924"
WO_ID = "WO-006"
Q_ID = "PQ-0064"
RUN_DATE = date(2026, 9, 24)
CUTOFF = "2025-09-09"  # 战役闭卷切点（结构映射侧仅作取证约束，见案卷 pit_assertion）

REG_DIR = ROOT / "data" / "registers" / "metaq_node_binding"
SCRIPT_DIR = Path(__file__).resolve().parent
TMP_DIR = ROOT / ".runtime" / "tmp" / SESSION / "wo006"
CASE_PATH = ROOT / "docs" / "_working" / "meta_question_answers" / "build" / "WO-006.yaml"

# wo006 写面排他标记：ig_node_company.source_doc 首段（三段式第一段），复算 before 口径按此前缀剔除
TAG = "wo006"
TAG_SQL = "coalesce(source_doc,'') LIKE 'wo006|%'"

MERGED_PAT = "%已并入%"
# 旁挂册列式列序（=apply 件喂给 ingest 通道的字段 + 审计列）
BATCH_COLUMNS = [
    "node_id",
    "chain_id",
    "node_name",
    "symbol",
    "origin",
    "also_from",
    "role",
    "confidence",
    "evidence_text",
    "source_doc",
    "market",
    "valid_from",
]


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。两条口径查询一律用 {mp}/{rf}/{tw} 占位、
# 由调用方 .format() 注入（谓词真源=TAG_SQL/MERGED_PAT，PIT 排除口径由 exclude_wo006 决定），
# 禁把标记/日期字面量写进常量。
_SQL_METRICS = """
with n as (
  select node_id, chain_id, (name like '{mp}') as merged from ig_node
),
cov as (
  select distinct node_id from ig_node_company where not ({rf})
),
per as (
  select n.chain_id,
         count(*) as nodes,
         count(*) filter (where cov.node_id is not null) as covered,
         count(*) filter (where not n.merged) as nodes_a,
         count(*) filter (where not n.merged and cov.node_id is not null) as covered_a
    from n left join cov on cov.node_id = n.node_id
   group by 1
)
select (select count(*) from ig_chain) as chains_total,
       count(*) filter (where nodes > 0) as chains_with_nodes,
       count(*) filter (where nodes = 0) as chains_no_node,
       count(*) filter (where nodes > 0 and covered::float / nodes >= 0.8) as a_all,
       count(*) filter (where nodes_a > 0 and covered_a::float / nodes_a >= 0.8) as a_active,
       round((count(*) filter (where nodes > 0 and covered::float / nodes >= 0.8))::numeric
             / nullif(count(*) filter (where nodes > 0), 0), 4) as ratio_all,
       round((count(*) filter (where nodes_a > 0 and covered_a::float / nodes_a >= 0.8))::numeric
             / nullif(count(*) filter (where nodes > 0), 0), 4) as ratio_active,
       count(*) filter (where nodes > 0 and covered = 0) as cov_zero,
       count(*) filter (where nodes > 0 and covered > 0 and covered::float / nodes < 0.5) as cov_lt50,
       count(*) filter (where nodes > 0 and covered::float / nodes >= 0.5
                        and covered::float / nodes < 0.8) as cov_50to80,
       round(avg(covered::float / nodes) filter (where nodes > 0)::numeric, 4) as mean_cov_all,
       round(avg(covered_a::float / nodes_a) filter (where nodes_a > 0)::numeric, 4) as mean_cov_active,
       count(*) filter (where nodes_a <= 2 and nodes_a > 0 and covered_a = 0) as micro_zero_active,
       (select count(*) from ig_node) as nodes_total,
       (select count(*) from ig_node where name like '{mp}') as merged_nodes,
       (select count(*) from ig_node x where not exists (select 1 from ig_node_company y where y.node_id = x.node_id and not ({rf}))) as unattached_nodes,
       (select count(*) from ig_node x where x.name not like '{mp}' and not exists (select 1 from ig_node_company y where y.node_id = x.node_id and not ({rf}))) as unattached_active,
       (select count(*) from ig_node_company) as nc_rows_total,
       (select count(*) from ig_node_company where not ({tw})) as nc_rows_non_wo006,
       (select count(*) from ig_node_company where {tw}) as nc_rows_wo006,
       (select count(distinct node_id) from ig_node_company) as nc_distinct_nodes
  from per
"""
_SQL_PER_CHAIN = """
with n as (select node_id, chain_id, (name like '{mp}') merged from ig_node),
cov as (select distinct node_id from ig_node_company where not ({rf}))
select n.chain_id, count(*),
       count(*) filter (where cov.node_id is not null),
       count(*) filter (where not n.merged),
       count(*) filter (where not n.merged and cov.node_id is not null)
  from n left join cov on cov.node_id = n.node_id group by 1 order by 1
"""


# --------------------------------------------------------------------------- 连接
def reader():
    """PG 只读连接（depgraph_reader 角色，技术阻断写入）。"""
    return get_depgraph_pg_connection()


def rows(sql: str, conn=None):
    """只读查询便捷封装：全 SQL 字面量（禁参数插值，避免 % 转义口径漂移）。"""
    own = conn is None
    c = conn or reader()
    cur = c.cursor()
    try:
        cur.execute(sql)
        return list(cur.fetchall())
    finally:
        if own:
            c.close()


def one(sql: str, conn=None):
    r = rows(sql, conn)
    return r[0] if r else None


# --------------------------------------------------------------------------- 判据复算
# PQ-0064 题面判据机械化：A_all=全节点口径 A 档链占比；A_active=剔"已并入"节点口径。
# exclude_wo006=True 时把 wo006 补挂行视为不存在 → 精确重构施工前状态。
def pq0064_metrics(conn=None, exclude_wo006: bool = False) -> dict:
    """按题面判据出全部指标；exclude_wo006=True 出"施工前"同口径指标（剔除 wo006 前缀行）。"""
    rf = TAG_SQL if exclude_wo006 else "FALSE"  # 行过滤谓词：True=把 wo006 行当不存在（重构写前面）
    sql = _SQL_METRICS.format(mp=MERGED_PAT, rf=rf, tw=TAG_SQL)
    keys = [
        "chains_total",
        "chains_with_nodes",
        "chains_no_node",
        "aclass_chains_all",
        "aclass_chains_active",
        "ratio_all",
        "ratio_active",
        "chains_cov_zero",
        "chains_cov_lt50",
        "chains_cov_50to80",
        "mean_coverage_all",
        "mean_coverage_active",
        "micro_chains_zero_active",
        "nodes_total",
        "merged_nodes",
        "unattached_nodes",
        "unattached_active_nodes",
        "ig_node_company_rows_total",
        "ig_node_company_rows_non_wo006",
        "ig_node_company_rows_wo006",
        "ig_node_company_distinct_nodes",
    ]
    r = one(sql, conn)
    from decimal import Decimal

    out = dict(zip(keys, [float(x) if isinstance(x, Decimal) else x for x in r], strict=True))
    out["threshold"] = "A 档链占比≥80%（覆盖率≥80%）"
    out["pass_all"] = bool(out["ratio_all"] and out["ratio_all"] >= 0.8)
    out["pass_active"] = bool(out["ratio_active"] and out["ratio_active"] >= 0.8)
    return out


def per_chain_state(conn=None, exclude_wo006: bool = False) -> dict:
    """逐链四元组快照（before 留证 + after 对账用）；exclude_wo006=True=重构施工前状态。"""
    out = {}
    rf = TAG_SQL if exclude_wo006 else "FALSE"
    for cid, nodes, covered, nodes_a, covered_a in rows(_SQL_PER_CHAIN.format(mp=MERGED_PAT, rf=rf), conn):
        out[cid] = [nodes, covered, nodes_a, covered_a]
    return out


# --------------------------------------------------------------------------- RULE-DATA-OPS 三验证
def data_ops_verify(
    step: str, necessity: str, truthfulness: str, reversibility: str, log: list | None = None
) -> list[str]:
    """写操作三步验证：必要性/真实性/可逆性——打印 + 返回留痕行（回写案卷）。"""
    lines = [
        f"[RULE-DATA-OPS] step={step}",
        f"  1) 必要性: {necessity}",
        f"  2) 真实性: {truthfulness}",
        f"  3) 可逆性: {reversibility}",
    ]
    print("\n".join(lines))
    if log is not None:
        log.extend(lines)
    return lines


# --------------------------------------------------------------------------- 旁挂册 IO
def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def write_register(path: Path, payload: dict) -> str:
    """列式/字典 YAML 的 CAS 写（热文件规则同款 safe_write_text，失败降级 atomic 写并 warn）。"""
    path = Path(path).resolve()
    body = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=200)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = path.read_text(encoding="utf-8") if path.exists() else ""
    try:
        from zephyr.shared.io.file_utils import content_sha256, safe_write_text

        safe_write_text(path, body, expected_base_sha256=content_sha256(base) if base else None)
    except Exception as e:  # noqa: BLE001 — 降级不留白：直写后复核
        print(f"[WARN] safe_write_text 不可用({e})，降级直写+回读校验")
        path.write_text(body, encoding="utf-8", newline="\n")
        assert _sha(path.read_text(encoding="utf-8")) == _sha(body), "写后回读不一致"
    print(f"[WRITE] {path.relative_to(ROOT)} ({len(body)} chars, base_sha={_sha(base)})")
    return _sha(body)


def load_register(path: Path) -> dict:
    if not path.is_file():
        import errno
        import os

        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), str(path)
        )  # 旁挂册缺失（引用即重放凭证，禁静默空册）
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def reg_rows(payload: dict) -> list[dict]:
    """columns+rows 列式册 → dict 行（错列自检：位置解压一旦错位必须炸，禁静默喂脏行）。"""
    cols = payload["columns"]
    out = [dict(zip(cols, r, strict=True)) for r in payload["rows"]]
    for r in out:
        if not str(r.get("node_id", "")).startswith("ND-") or not str(r.get("symbol", ""))[:6].isdigit():
            raise ValueError(f"旁挂册错列/脏行（node_id/symbol 自检失败）: {r}")
    return out
