#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_SYNC_PANORAMA | docs/_working/2026-07-09-panorama_module_sync_engine.md | §Phase2
# [MODULE] scripts.governance.sync_panorama_module
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.persistence.dataflowgraph_schema (get_dataflowgraph_pg_connection); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection)
# [CONSUMERS] generate_project_depgraph.py; apply_depgraph.py; GitCommitGateway
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 单向派生（depgraph→dataflow/decision/blueprint）;占位记录用 entity_type='module_placeholder' / track='placeholder'
# [MODIFY-GUARD] sync_module_panorama/sync_all_panorama 为对外入口；SQL 常量集中在模块级 _SQL_*；占位记录策略不可改（entity_type/track 值为契约）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph无此模块→exit 3;DB异常→exit 4
# [TESTS] tests/governance/test_sync_panorama_module.py
# [A_module] module_id=MOD-GOV_SYNC_PANORAMA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-056 #ARCH-058
"""sync_panorama_module.py — 五图模块同步引擎（ARCH-056）

从 depgraph.nodes 读取模块核心字段，单向派生到：
  1. dataflow_jobs（占位记录，entity_type='module_placeholder'）
  2. decision_layers（占位记录，layer_id=module_id, track='placeholder'）
  3. blueprint.md frontmatter（如蓝图存在，由 blueprint_frontmatter_reconciler 处理）

核心字段（4个）：module_id / domain_id / design_maturity / build_status

用法:
    python scripts/governance/sync_panorama_module.py MOD-XXX
    python scripts/governance/sync_panorama_module.py --all
"""

from __future__ import annotations

__manifest__ = """
args: []
description: sync_panorama_module.py — 五图模块同步引擎（ARCH-056）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_DIR = _REPO_ROOT / "src"
_GOV_DIR = _REPO_ROOT / "scripts" / "governance"
for _p in (str(_REPO_ROOT), str(_SRC_DIR), str(_GOV_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    acquire_dataflow_write_lock,
    get_dataflowgraph_pg_connection,
    release_dataflow_write_lock,
)
from zephyr.governance.persistence.decisiongraph_schema import get_decisiongraph_pg_connection  # noqa: E402

try:
    from d5_architecture.panorama_common import min_maturity as _min_mat
    from d5_architecture.panorama_common import weighted_domain_vote
except ImportError:
    import importlib as _im
    import sys as _sys

    _pc_path = str(Path(__file__).resolve().parent / "d5_architecture")
    if _pc_path not in _sys.path:
        _sys.path.insert(0, _pc_path)
    _pc_mod = _im.import_module("panorama_common")
    weighted_domain_vote = _pc_mod.weighted_domain_vote
    _min_mat = _pc_mod.min_maturity

# Ruling:100PCT-AI-GOVERNANCE P1-1 (2026-07-19) 治本：
# 统一用 normalize_to_none() 替代 `or None` 模式。
# 原因：`or None` 会误转所有 falsy 值（0/False/[]），
# normalize_to_none 只转空字符串，类型安全且意图明确。
from zephyr.shared.utils.converters import normalize_to_none

# ---------------------------------------------------------------------------
# SQL 常量（SQL 集中化，§5.160.2）
# ---------------------------------------------------------------------------
# 注意：不使用 LIMIT 1 — 同一 blueprint_id 可有多行（跨域模块），
# _query_depgraph_module 在 Python 中用多数投票聚合，
# 与 align_panoramas._fetch_depgraph_nodes 聚合策略一致。
_SQL_QUERY_MODULE = (
    "SELECT blueprint_id, domain_id, design_maturity, build_status, path "
    "FROM nodes WHERE blueprint_id = %s AND blueprint_id <> '' "
    "ORDER BY (path IS NULL), path"
)
_SQL_QUERY_ALL_MODULES = "SELECT DISTINCT blueprint_id FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"
_SQL_UPDATE_DATAFLOW_JOB = (
    "UPDATE dataflow_jobs SET domain_id=%s, design_maturity=%s, build_status=%s, module_id=%s WHERE job_name=%s"
)
_SQL_UPSERT_DATAFLOW_PLACEHOLDER = (
    "INSERT "
    "INTO dataflow_jobs (job_name, entity_type, module_id, domain_id, "
    "design_maturity, build_status, trigger_type) "
    "VALUES (%s, 'module_placeholder', %s, %s, %s, %s, NULL) "
    "ON CONFLICT (job_name) DO UPDATE SET "
    "entity_type='module_placeholder', module_id=EXCLUDED.module_id, "
    "domain_id=EXCLUDED.domain_id, design_maturity=EXCLUDED.design_maturity, "
    "build_status=EXCLUDED.build_status"
)
_SQL_UPDATE_DECISION_LAYER = (
    "UPDATE decision_layers SET domain_id=%s, design_maturity=%s, build_status=%s, module_id=%s WHERE layer_id=%s"
)
_SQL_UPSERT_DECISION_PLACEHOLDER = (
    "INSERT "
    "INTO decision_layers (layer_id, layer_name, layer_name_en, track, "
    "module_id, domain_id, design_maturity, build_status) "
    "VALUES (%s, %s, %s, 'placeholder', %s, %s, %s, %s) "
    "ON CONFLICT (layer_id) DO UPDATE SET "
    "module_id=EXCLUDED.module_id, domain_id=EXCLUDED.domain_id, "
    "design_maturity=EXCLUDED.design_maturity, build_status=EXCLUDED.build_status"
)
_SQL_QUERY_DECISION_PLACEHOLDERS = "SELECT layer_id FROM decision_layers WHERE track = 'placeholder'"
_SQL_DELETE_DECISION_LAYER = "DELETE FROM decision_layers WHERE layer_id = %s"
_SQL_QUERY_DATAFLOW_PLACEHOLDERS = "SELECT job_name FROM dataflow_jobs WHERE entity_type = 'module_placeholder'"
_SQL_DELETE_DATAFLOW_JOB = "DELETE FROM dataflow_jobs WHERE job_name = %s"
# 2026-08-29 增量治本：skip-identical 判定需要既有行的完整字段（原只查 entity_type/track）
_SQL_CHECK_DATAFLOW_JOB_FULL = (
    "SELECT entity_type, domain_id, design_maturity, build_status, module_id FROM dataflow_jobs WHERE job_name = %s"
)
_SQL_CHECK_DECISION_LAYER_FULL = (
    "SELECT track, domain_id, design_maturity, build_status, module_id FROM decision_layers WHERE layer_id = %s"
)


def _open_sync_conns() -> dict:
    """一次打开三条同步连接（2026-08-29 批量路径连接复用治本）。

    原 sync_all_panorama 每模块开/关 3 条全新 PG 连接（616 模块 ≈ 1850 次连接建立，
    占 ~370s 耗时大头）。批量入口（sync_all/sync_modules）改为循环外开一次复用。
    单模块入口（conns=None）维持原每次开关语义。
    """
    return {
        "depgraph": get_depgraph_pg_connection(),
        # FP-ISO.4C：写路径必须 read_only=False（详见 sync_module_panorama 注释）
        "dataflow": get_dataflowgraph_pg_connection(read_only=False, allow_design_delete=True),
        "decision": get_decisiongraph_pg_connection(read_only=False, allow_design_delete=True),
    }


def _close_sync_conns(conns: dict) -> None:
    for c in conns.values():
        try:
            c.close()
        except Exception:  # noqa: BLE001 — 关闭异常不掩盖主流程
            pass


def _values_unchanged(existing: dict, module: dict) -> bool:
    """skip-identical 判定（2026-08-29）：既有行核心字段与新值全部相等（NULL/'' 归一）。

    normalize_to_none 语义对齐：'' 与 NULL 视为同一值（写入侧也是 normalize_to_none）。
    """

    def _n(v):
        return None if v in ("", None) else v

    return (
        _n(existing.get("domain_id")) == _n(module["domain_id"])
        and _n(existing.get("design_maturity")) == _n(module["design_maturity"])
        and _n(existing.get("build_status")) == _n(module["build_status"])
        and _n(existing.get("module_id")) == _n(module["module_id"])
    )


def _query_depgraph_module(conn, module_id: str) -> dict | None:
    """从 depgraph.nodes 查询单个模块的核心字段（加权投票聚合）。

    depgraph.nodes 中同一 blueprint_id 可有多行（跨域模块的正常现象）。
    聚合策略与 align_panoramas._fetch_depgraph_nodes 一致：
    - domain_id: 加权投票（测试文件降权，平局字母序，panorama_common.weighted_domain_vote）
    - design_maturity: 取最 design 的状态（design < production，panorama_common.min_maturity）
    - build_status: 取第一个非空
    - path: 取第一个非空（ORDER BY 保证非空优先）
    """
    with conn.cursor() as cur:
        cur.execute(_SQL_QUERY_MODULE, (module_id,))
        rows = cur.fetchall()
    if not rows:
        return None
    maturities: list[str] = []
    build_status = ""
    path = ""
    for row in rows:
        if isinstance(row, dict):
            dm = row.get("design_maturity")
            bs = row.get("build_status")
            p = row.get("path")
        else:
            dm = row[2] if len(row) > 2 else None
            bs = row[3] if len(row) > 3 else None
            p = row[4] if len(row) > 4 else None
        if dm:
            maturities.append(dm)
        if not build_status and bs:
            build_status = bs
        if not path and p:
            path = p
    domain_id = weighted_domain_vote(rows)
    design_maturity = _min_mat(maturities) if maturities else ""
    # Ruling:100PCT-AI-GOVERNANCE P1-1 (2026-07-19) 治本：
    # 用 normalize_to_none() 替代 `or None` 模式（类型安全，不误转 falsy 值）。
    # 背景：weighted_domain_vote/min_maturity 在无值时返回 ""，但 decision_layers
    # 的 chk_decision_layers_domain_id_not_empty 约束允许 NULL 禁止 ''，
    # 导致 540 个空 domain_id 模块的 decision_layers INSERT 静默失败。
    # 转为 None 让 PostgreSQL 写入 NULL，对齐约束语义。
    return {
        "module_id": module_id,
        "domain_id": normalize_to_none(domain_id),
        "design_maturity": normalize_to_none(design_maturity),
        "build_status": normalize_to_none(build_status),
        "path": normalize_to_none(path),
    }


def _sync_to_dataflow(conn, module: dict) -> str:
    """同步到 dataflow_jobs 占位记录。

    占位策略：entity_type='module_placeholder', job_name=module_id。
    如已存在非占位记录（entity_type!='module_placeholder'），更新核心字段但不改 entity_type。
    2026-08-29 skip-identical：既有行核心字段与新值全等时跳过写入，返回 "unchanged"；
    发生写入返回 "changed"（供批量路径统计与下游跳过决策）。
    """
    mid = module["module_id"]
    with conn.cursor() as cur:
        cur.execute(_SQL_CHECK_DATAFLOW_JOB_FULL, (mid,))
        existing = cur.fetchone()
        if existing is not None:
            if not isinstance(existing, dict):
                existing = {
                    "entity_type": existing[0],
                    "domain_id": existing[1],
                    "design_maturity": existing[2],
                    "build_status": existing[3],
                    "module_id": existing[4],
                }
            if _values_unchanged(existing, module):
                return "unchanged"
            if existing.get("entity_type") != "module_placeholder":
                cur.execute(
                    _SQL_UPDATE_DATAFLOW_JOB,
                    (module["domain_id"], module["design_maturity"], module["build_status"], mid, mid),
                )
                return "changed"
        cur.execute(
            _SQL_UPSERT_DATAFLOW_PLACEHOLDER,
            (mid, mid, module["domain_id"], module["design_maturity"], module["build_status"]),
        )
        return "changed"


def _sync_to_decision(conn, module: dict) -> str:
    """同步到 decision_layers 占位记录。

    占位策略：layer_id=module_id, track='placeholder'。
    如已存在非占位 layer（track!='placeholder'），更新核心字段但不改 track。
    2026-08-29 skip-identical：同 _sync_to_dataflow，返回 "unchanged"/"changed"。
    """
    mid = module["module_id"]
    with conn.cursor() as cur:
        cur.execute(_SQL_CHECK_DECISION_LAYER_FULL, (mid,))
        existing = cur.fetchone()
        if existing is not None:
            if not isinstance(existing, dict):
                existing = {
                    "track": existing[0],
                    "domain_id": existing[1],
                    "design_maturity": existing[2],
                    "build_status": existing[3],
                    "module_id": existing[4],
                }
            if _values_unchanged(existing, module):
                return "unchanged"
            if existing.get("track") != "placeholder":
                cur.execute(
                    _SQL_UPDATE_DECISION_LAYER,
                    (module["domain_id"], module["design_maturity"], module["build_status"], mid, mid),
                )
                return "changed"
        cur.execute(
            _SQL_UPSERT_DECISION_PLACEHOLDER,
            (mid, mid, mid, mid, module["domain_id"], module["design_maturity"], module["build_status"]),
        )
        return "changed"


def sync_module_panorama(module_id: str, conns: dict | None = None) -> int:
    """同步单个模块的全景核心字段。

    Args:
        module_id: 模块 ID（blueprint_id）。
        conns: 2026-08-29 连接复用——批量入口（sync_all/sync_modules）传入
            _open_sync_conns() 的共享连接字典，循环内不再每模块开/关 3 条连接；
            None（默认）时维持原"每次自开自关"语义（单模块 CLI/调用方不变）。

    Returns: 0=成功, 3=模块不存在, 4=DB异常, 5=部分下游同步失败（dataflow/decision/blueprint）
    """
    _own_conns = conns is None
    if _own_conns:
        depgraph_conn = get_depgraph_pg_connection()
    else:
        depgraph_conn = conns["depgraph"]
    try:
        module = _query_depgraph_module(depgraph_conn, module_id)
        if not module:
            print(f"[ERROR] 模块 {module_id} 在 depgraph 中不存在", file=sys.stderr)
            return 3
    finally:
        if _own_conns:
            depgraph_conn.close()

    # ARCH-FRONTMATTER-STATE-001 Phase 2：dataflow/decision 同步失败不阻断 frontmatter 对齐。
    # 三个下游 sync 目标（dataflow/decision/blueprint）相互独立，
    # 环境级权限问题（InsufficientPrivilege on dataflow_jobs）不应让 frontmatter reconciler 失效。
    # FP-ISO.4C 修复（2026-07-19）：必须传 read_only=False，否则连接工厂默认只读角色，
    # INSERT/UPDATE 会被 PostgreSQL 拒绝（"对表 dataflow_jobs 权限不够"），同步静默失败。
    #
    # #Ruling:100PCT-AI-GOVERNANCE P0-2 (2026-07-19) 治本：
    # 原 try/except 吞异常 + 始终 return 0，导致父 reconciler
    # (make_blueprint_frontmatter_reconciler) 看到 rc=0 误以为全部成功，
    # "616 模块 0 失败" 实际全失败的静默反模式。
    # 治本：保留"三个下游相互独立、不互相阻断"的设计（继续独立 try/except），
    # 但用 failed_count 计数 + 返回 exit 5 + stderr 最后一行打印 FAILED_COUNT=N，
    # 让父 reconciler 检测到部分失败并升级为 critical_warn（P0-1 已对接）。
    failed_count = 0
    if _own_conns:
        dataflow_conn = get_dataflowgraph_pg_connection(
            read_only=False,
            allow_design_delete=True,
        )
    else:
        dataflow_conn = conns["dataflow"]
    try:
        _sync_to_dataflow(dataflow_conn, module)
        # FP-FIX-DECISION-COMMIT (2026-08-05, 治本 decision_layers 静默回滚):
        # 显式 commit 对齐两条路径事务语义。根因：get_dataflowgraph_pg_connection
        # 默认 autocommit=True（INSERT 自动提交），而 get_decisiongraph_pg_connection
        # 在 writer 角色下默认 autocommit=False，不显式 commit 会让 decision_layers
        # 的 INSERT 在 conn.close() 时被静默回滚（sync 报 rc=0 但 DB 无记录）。
        # commit() 对 autocommit=True 连接是 no-op，防御性调用安全。
        dataflow_conn.commit()
    except Exception as e:  # noqa: BLE001 - 三个下游相互独立，单点失败不阻断其他下游
        failed_count += 1
        print(f"[ERROR] dataflow 同步失败（module={module_id}）: {e}", file=sys.stderr)
    finally:
        if _own_conns:
            dataflow_conn.close()

    if _own_conns:
        decision_conn = get_decisiongraph_pg_connection(
            read_only=False,
            allow_design_delete=True,
        )
    else:
        decision_conn = conns["decision"]
    try:
        _sync_to_decision(decision_conn, module)
        # FP-FIX-DECISION-COMMIT (2026-08-05)：见上方 dataflow_conn.commit() 注释。
        # 此处为治本核心——decision_layers 的 INSERT 在 autocommit=False 下必须显式 commit，
        # 否则 405 个模块的占位记录（含 MOD-PLAN-002/003）会被 conn.close() 静默回滚。
        decision_conn.commit()
    except Exception as e:  # noqa: BLE001 - 三个下游相互独立，单点失败不阻断其他下游
        failed_count += 1
        print(f"[ERROR] decision 同步失败（module={module_id}）: {e}", file=sys.stderr)
    finally:
        if _own_conns:
            decision_conn.close()

    # 蓝图 frontmatter 对齐（如蓝图存在）
    try:
        from d5_architecture.syncers.blueprint_frontmatter_reconciler import (
            reconcile_blueprint_frontmatter,
        )

        reconcile_blueprint_frontmatter(module_id)
    except Exception as e:  # noqa: BLE001 - 三个下游相互独立，单点失败不阻断其他下游
        failed_count += 1
        print(f"[ERROR] 蓝图 frontmatter 对齐失败（module={module_id}）: {e}", file=sys.stderr)

    if failed_count > 0:
        # stderr 最后一行打印结构化失败计数，供父 reconciler 解析（机器可读契约）
        print(f"FAILED_COUNT={failed_count} module={module_id}", file=sys.stderr)
        return 5
    return EXIT_PASS


def sync_all_panorama() -> int:
    """同步所有有 blueprint_id 的模块。

    Returns: 0=全部成功, 1=至少一个模块失败（rc=3/4/5）
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_QUERY_ALL_MODULES)
            modules = [row["blueprint_id"] if isinstance(row, dict) else row[0] for row in cur.fetchall()]
    finally:
        conn.close()

    failed = 0
    partial = 0  # P0-2: 部分下游失败（rc=5）单独计数
    # 缺蓝图 WARN 聚合（2026-08-15 治本：827 行/rebuild 噪音稀释真信号）——
    # 批量期间逐条 WARN 静音并累积，循环后打印一行汇总。
    from d5_architecture.syncers import blueprint_frontmatter_reconciler as _bfr

    # 2026-08-29 连接复用治本：循环外开一次 3 条连接（原每模块开/关 3 条 ≈ 616×3 次建立）。
    # 空模块列表提前返回（不白开连接，也避免测试环境真实连库）。
    if not modules:
        print("[OK] 同步完成：0 个模块，0 个失败，0 个部分下游失败")
        return EXIT_PASS
    _conns = _open_sync_conns()
    _bfr.set_quiet_missing(True)
    try:
        for mid in modules:
            rc = sync_module_panorama(mid, conns=_conns)
            if rc == 5:
                # P0-2: 部分下游失败——不重复打印（sync_module_panorama 已打印详情）
                partial += 1
            elif rc != 0:
                print(f"[WARN] 同步 {mid} 失败 (rc={rc})", file=sys.stderr)
                failed += 1
    finally:
        _missing_bp = _bfr.pop_missing_modules()
        _bfr.set_quiet_missing(False)
        _close_sync_conns(_conns)
    # P0-2: 汇总行打印结构化计数，供父 reconciler 解析
    print(f"[OK] 同步完成：{len(modules)} 个模块，{failed} 个失败，{partial} 个部分下游失败")
    print(
        f"[OK] 蓝图缺失跳过 {len(_missing_bp)} 个模块（容忍常态：单文件模块文档真源=头标+注册表，域级才强制 blueprint.md）",
        file=sys.stderr,
    )
    if failed > 0:
        return EXIT_FINDINGS
    if partial > 0:
        # P0-2: 部分下游失败也返回非零，让父 reconciler 检测到（升级为 critical_warn）
        return EXIT_FINDINGS
    return EXIT_PASS


def sync_modules_panorama(module_ids: list[str]) -> int:
    """增量同步指定的模块列表（#ARCH-PRE-EXISTING-DEBT-001 治本，2026-07-20）。

    与 sync_all_panorama 的区别：只同步传入的 module_id 列表，避免全量扫描 616+ 模块。
    供 reconciler 增量分发使用（committed_files → module_ids → 本函数）。

    Args:
        module_ids: 要同步的模块 ID 列表（如 ["MOD-INF-013", "MOD-GOV-001"]）。

    Returns: 0=全部成功, 1=至少一个模块失败（rc=3/4/5）
    """
    if not module_ids:
        print("[WARN] sync_modules_panorama: 空模块列表，跳过", file=sys.stderr)
        return EXIT_PASS
    failed = 0
    partial = 0
    # 缺蓝图 WARN 聚合（同 sync_all_panorama，2026-08-15 治本）
    from d5_architecture.syncers import blueprint_frontmatter_reconciler as _bfr

    # 2026-08-29 连接复用治本（同 sync_all_panorama）
    _conns = _open_sync_conns()
    _bfr.set_quiet_missing(True)
    try:
        for mid in module_ids:
            rc = sync_module_panorama(mid, conns=_conns)
            if rc == 5:
                partial += 1
            elif rc != 0:
                print(f"[WARN] 同步 {mid} 失败 (rc={rc})", file=sys.stderr)
                failed += 1
    finally:
        _missing_bp = _bfr.pop_missing_modules()
        _bfr.set_quiet_missing(False)
        _close_sync_conns(_conns)
    print(f"[OK] 增量同步完成：{len(module_ids)} 个模块，{failed} 个失败，{partial} 个部分下游失败")
    if _missing_bp:
        print(f"[OK] 蓝图缺失跳过 {len(_missing_bp)} 个模块（容忍常态）", file=sys.stderr)
    if failed > 0 or partial > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


def prune_orphans() -> dict:
    """删除 decision_layers + dataflow_jobs 中的孤儿占位记录（ARCH-057 + ARCH-058）。

    孤儿定义：
    - decision_layers: track='placeholder' 且 layer_id 不在 depgraph.nodes.blueprint_id 中
    - dataflow_jobs: entity_type='module_placeholder' 且 job_name 不在 depgraph.nodes.blueprint_id 中

    根因：sync 只 UPSERT 不 DELETE，depgraph 删模块后 decision_layers/dataflow_jobs 残留占位记录。

    幂等：删除孤儿后再次运行不会删除任何东西。

    Returns:
        {"deleted_decision": int, "deleted_dataflow": int,
         "orphan_decision": list[str], "orphan_dataflow": list[str]}
    """
    # 1. 查询 depgraph 中所有 blueprint_id
    depgraph_conn = get_depgraph_pg_connection()
    try:
        with depgraph_conn.cursor() as cur:
            cur.execute(_SQL_QUERY_ALL_MODULES)
            rows = cur.fetchall()
        blueprint_ids = {row["blueprint_id"] if isinstance(row, dict) else row[0] for row in rows}
    finally:
        depgraph_conn.close()

    # 2. 清理 decision_layers 孤儿占位层
    decision_conn = get_decisiongraph_pg_connection(
        allow_design_delete=True,
        read_only=False,
    )
    orphan_decision: list[str] = []
    deleted_decision = 0
    try:
        with decision_conn.cursor() as cur:
            cur.execute(_SQL_QUERY_DECISION_PLACEHOLDERS)
            rows = cur.fetchall()
            placeholders = [row["layer_id"] if isinstance(row, dict) else row[0] for row in rows]
            orphan_decision = [lid for lid in placeholders if lid not in blueprint_ids]
            for lid in orphan_decision:
                cur.execute(_SQL_DELETE_DECISION_LAYER, (lid,))
                deleted_decision += 1
        decision_conn.commit()
    finally:
        decision_conn.close()

    # 3. 清理 dataflow_jobs 孤儿占位记录（ARCH-058 扩展，治本 2026-07-16）
    #    走 dataflow 连接工厂（责任边界对齐）+ WRITER 角色（read_only=False，DELETE 权限）
    #    + allow_design_delete（绕过 protect_dataflow_design_maturity 触发器，ARCH-053）
    #    + acquire_dataflow_write_lock（pg_advisory_lock 424243，并发互斥）
    dataflow_conn = get_dataflowgraph_pg_connection(
        read_only=False,
        autocommit=False,
        allow_design_delete=True,
    )
    orphan_dataflow: list[str] = []
    deleted_dataflow = 0
    try:
        acquire_dataflow_write_lock(dataflow_conn)
        with dataflow_conn.cursor() as cur:
            cur.execute(_SQL_QUERY_DATAFLOW_PLACEHOLDERS)
            rows = cur.fetchall()
            placeholders = [row["job_name"] if isinstance(row, dict) else row[0] for row in rows]
            orphan_dataflow = [jid for jid in placeholders if jid not in blueprint_ids]
            for jid in orphan_dataflow:
                cur.execute(_SQL_DELETE_DATAFLOW_JOB, (jid,))
                deleted_dataflow += 1
        dataflow_conn.commit()
    finally:
        release_dataflow_write_lock(dataflow_conn)
        dataflow_conn.close()

    return {
        "deleted_decision": deleted_decision,
        "deleted_dataflow": deleted_dataflow,
        "orphan_decision": orphan_decision,
        "orphan_dataflow": orphan_dataflow,
    }


def main():
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="五图模块同步引擎（ARCH-056）")
    parser.add_argument("module_ids", nargs="*", help="要同步的模块 ID 列表（MOD-XXX MOD-YYY ...）")
    parser.add_argument("--all", action="store_true", help="同步所有模块")
    parser.add_argument(
        "--prune-orphans",
        action="store_true",
        help="删除 decision_layers + dataflow_jobs 中的孤儿占位记录（ARCH-057 + ARCH-058）",
    )
    args = parser.parse_args()

    if args.prune_orphans:
        result = prune_orphans()
        print(
            f"Prune orphans: decision deleted={result['deleted_decision']}, "
            f"dataflow deleted={result['deleted_dataflow']}, "
            f"orphan_decision={result['orphan_decision']}, "
            f"orphan_dataflow={result['orphan_dataflow']}"
        )
        return EXIT_PASS
    if args.all:
        return sync_all_panorama()
    if args.module_ids:
        # 增量模式：多模块入口（#ARCH-PRE-EXISTING-DEBT-001 治本，2026-07-20）
        return sync_modules_panorama(args.module_ids)
    parser.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def query_depgraph_module(conn, module_id) -> dict | None:
    """公共接口：query_depgraph_module（Stage 4 公共化）。"""
    return _query_depgraph_module(conn, module_id)
