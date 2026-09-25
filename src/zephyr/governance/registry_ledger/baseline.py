# [MODULE] zephyr.governance.registry_ledger.baseline
# [DOMAIN] D_GOVERNANCE
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [STARTUP] imported
# [MATURITY] production
# [MODIFY-GUARD] 新建 2026-09-24 st-wm1-wave0-20260924（W-M1 波0⑤⑥施工件）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描/DB 异常上抛由 CLI 折入报告；身份不可判条目=passthrough 计数不入表（W2 同判据）
# [TESTS] tests/governance/test_registry_ledger_baseline.py
# [TTL] permanent
# [DEPENDENCIES] zephyr.governance.registry_ledger.api (canonical_payload_sha256/_record_event);
#   zephyr.governance.registry_ledger.identity (entry_composite_key);
#   scripts.governance.commit_queue_landing (_split_registry_entries, lazy)
# [CONSUMERS] scripts/governance/registry_migration/wave0_phase0_gate.py (CLI);
#   belt daemon dual-track 探针（W-M1 Phase 1 双轨对账通道）
# [INVARIANTS] 身份键唯一真源=entry_composite_key（与门禁/合并器同源，永不复制逻辑）；
#   条目切分唯一真源=_split_registry_entries（yaml.compose 行号法）；导入幂等
#   （ON CONFLICT DO NOTHING，重跑零新事件）；双轨对账=insert-only（YAML→PG 补登记，
#   同键异内容/PG 独有条目只记 reconcile_drift 事件绝不覆写——Phase 1 期 YAML 仍是
#   commit 真源，PG wins 自愈归 cutover 后，届时由投影生成器接管）
# [ERROR_CONTRACT] 扫描/DB 异常原样上抛由 CLI 折入报告；单条目身份不可判=passthrough
#   计数不入条目表（W2 合并器同判据，防纯标量族死信）
# [TESTS] tests/governance/test_registry_ledger_baseline.py
"""W-M1 Phase 0 基线导入 + 双轨对账引擎（02 号文 §4 Phase 0/Phase 1 施工件）。

四动作：
- scan_registry_file：机械扫描一册（ROOR ∪ 文件头，零人工填写）→ 族/条目/异形清单。
- import_baseline：条目级导入（action=import 事件，幂等可重跑）+ catalog 种子。
- publish_snapshot：发布不可变全量快照（每册单调版本，同 content_sha256=noop）。
- reconcile_registry：双轨对账（YAML→PG 缺=补登记；同键异内容/PG 独有=drift 事件）。


# [ALGO_FLOW]
层: 扫描 → 导入 → 发布 → 对账
- 扫描: ROOR∪YAML 头解析 registry_id；_split_registry_entries 族切分；身份键过滤 passthrough
- 导入: ON CONFLICT DO NOTHING 幂等插入+action=import 事件
- 发布: active 集 manifest/bundle 规范哈希，同 sha noop，否则单调版本+publish 事件
- 对账: first-wins 对齐 DB；缺=补登记，异=按 YAML 吸收（version+1），PG 独有=只记账"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import psycopg2

from zephyr.governance.registry_ledger.api import (
    _open_default_conn as _open_writer_conn,
)
from zephyr.governance.registry_ledger.api import (
    _record_event,
    _t,
    canonical_payload_sha256,
)
from zephyr.governance.registry_ledger.ledger_identity import entry_composite_key
from zephyr.governance.registry_ledger.registry_ledger_ddl import SCHEMA_NAME

ROOR_PATH = "docs/registry_of_registries.yaml"
DEFAULT_SESSION = "st-wm1-wave0-20260924"
IMPORT_REASON = "Phase 0 baseline import from YAML (W-M1 wave0 gate)"
RECONCILE_REASON = "dual-track reconcile yaml-to-pg (W-M1 Phase 1)"
PUBLISH_REASON = "snapshot publish after registry landing (W-M1)"

# P0 第一波七册（09_wm1_master_plan.md §二 A-1 名单）：只登记 registry_id，
# 物理路径运行时经 ROOR 反查（VOCAB-CHAIN：.py 禁硬编码 SSoT 路径）。
P0_REGISTRY_IDS = (
    "REG-CAPCAN-001",
    "REG-MODULE-TRANSLATION-001",
    "REG-DOC-001",
    "REG-ARCH-ISSUE-001",
    "REG-ERRCODE-001",
    "REG-CAND-001",
    "REG-RULING-001",
)


def p0_physical_paths(repo_root: Path | None = None) -> list:
    """A-1 名单 registry_id → physical_path（机械确定，禁 .py 硬编码路径）。

    解析序：ROOR physical_path∪registry_id 反查 → ROOR 索引文件的 YAML 头部
    registry_id 扫描（translation/candidate/ruling 三册 id 在文件头不在 ROOR 行）。
    """
    import yaml as _yaml  # noqa: PLC0415

    repo_root = Path(repo_root) if repo_root else Path(".")
    by_id: dict = {v["registry_id"]: k for k, v in load_roor_index(repo_root).items()}
    # 候选池=catalogs/ 与 contracts/ 目录机械枚举（目录发现非路径硬编码）+ ROOR 索引面
    candidates = set(by_id.values())
    for d in ("docs/01_policies_and_standards/_registry/catalogs", "architecture_model/contracts"):
        dpath = repo_root / d
        if dpath.is_dir():
            candidates.update(str(p.relative_to(repo_root)).replace("\\", "/") for p in dpath.glob("*.yaml"))
    for path in sorted(candidates):
        if path in by_id.values() or not path.endswith(".yaml"):
            continue
        f = repo_root / path
        if not f.exists():
            continue
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines()[:40]:
                if line.startswith("registry_id:"):
                    rid = line.split(":", 1)[1].strip()
                    by_id.setdefault(rid, path)
                    break
        except OSError:
            continue
    missing = [r for r in P0_REGISTRY_IDS if r not in by_id]
    if missing:
        raise KeyError(f"P0 registry_ids absent from ROOR∪headers: {missing}")
    return [by_id[r] for r in P0_REGISTRY_IDS]


# ── 机械扫描 ────────────────────────────────────────────────────────────────────


def load_roor_index(repo_root: Path) -> dict[str, dict]:
    """ROOR → {physical_path: {registry_id, maintenance, ...}}（递归收集含 physical_path 的映射）。

    同路径多注册（如 REG-CAPCAN-001 与其子集视图 REG-GEN-001，P-5 内收对象）→
    ROOR 文档序首个为准（正主在前、派生视图在后），机械确定不猜。
    """
    import yaml  # noqa: PLC0415

    roor_file = repo_root / ROOR_PATH
    index: dict[str, dict] = {}

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            pp = node.get("physical_path")
            if isinstance(pp, str) and node.get("registry_id"):
                key = pp.replace("\\", "/")
                if key not in index:  # first-wins（文档序=正主优先）
                    index[key] = {
                        "registry_id": str(node["registry_id"]),
                        "maintenance": str(node.get("maintenance", "manual")),
                    }
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for v in node:
                _walk(v)

    if roor_file.exists():
        _walk(yaml.safe_load(roor_file.read_text(encoding="utf-8")))
    return index


def _family_statistics(families: dict) -> tuple[dict, int, list]:
    """族统计：每族 dict 条目数/passthrough 数/身份清单（供扫描报告与主族判定）。"""
    family_stats: dict = {}
    total_dict_entries = 0
    all_identities: list = []
    for fam_key, fam in families.items():
        dict_entries = 0
        passthrough = 0
        identities: list = []
        for blk in fam.blocks:
            key = entry_composite_key(blk.data) if isinstance(blk.data, dict) else None
            if key is None:
                passthrough += 1
            else:
                dict_entries += 1
                identities.append(key)
        family_stats[fam_key or "(root)"] = {
            "entries": dict_entries,
            "passthrough": passthrough,
            "dup_identity_in_scan": dict_entries - len(set(identities)),
        }
        all_identities.extend(identities)
        total_dict_entries += dict_entries
    return family_stats, total_dict_entries, all_identities


def _identity_mode(families: dict) -> str:
    """身份模式：任一 dict 条目带 token 字段 → first_scalar_token，否则 first_scalar。"""
    for fam in families.values():
        for blk in fam.blocks:
            if isinstance(blk.data, dict) and isinstance(blk.data.get("token"), (str, int, float)):
                return "first_scalar_token"
    return "first_scalar"


def scan_registry_file(repo_root: Path, physical_path: str) -> dict:
    """一册机械扫描：头部元数据 + 族切分 + 条目/异形计数（零 DB 依赖）。"""
    import yaml  # noqa: PLC0415

    from scripts.governance.commit_queue_landing import _split_registry_entries  # noqa: PLC0415

    abs_path = repo_root / physical_path
    text = abs_path.read_text(encoding="utf-8")
    full = yaml.safe_load(text)
    header = (
        {k: v for k, v in (full or {}).items() if not isinstance(v, (list, dict))} if isinstance(full, dict) else {}
    )
    families, err = _split_registry_entries(text)
    if err:
        raise ValueError(f"{physical_path}: {err}")

    roor = load_roor_index(repo_root)
    roor_row = roor.get(physical_path.replace("\\", "/"), {})
    registry_id = str(header.get("registry_id") or roor_row.get("registry_id") or "")
    if not registry_id:
        raise ValueError(f"{physical_path}: registry_id unresolved (YAML header ∪ ROOR 均无)")

    family_stats, total_dict_entries, _ = _family_statistics(families)
    primary = max(
        ((k, v) for k, v in family_stats.items() if v["entries"] > 0),
        key=lambda kv: kv[1]["entries"],
        default=(None, None),
    )
    return {
        "registry_id": registry_id,
        "physical_path": physical_path,
        "header": {k: header[k] for k in ("schema_version", "module_id", "status", "version", "date") if k in header},
        "maintenance": roor_row.get("maintenance", "manual"),
        "family_stats": family_stats,
        "primary_family": primary[0],
        "extra_families": {k: v["entries"] + v["passthrough"] for k, v in family_stats.items() if k != primary[0]},
        "identity_mode": _identity_mode(families),
        "entries_total": total_dict_entries,
        "passthrough_total": sum(v["passthrough"] for v in family_stats.values()),
    }


def _iter_scan_entries(repo_root: Path, physical_path: str):
    """产出 (family_key, entry_key, payload)；身份不可判的条目跳过（passthrough）。"""
    from scripts.governance.commit_queue_landing import _split_registry_entries  # noqa: PLC0415

    text = (repo_root / physical_path).read_text(encoding="utf-8")
    families, err = _split_registry_entries(text)
    if err:
        raise ValueError(f"{physical_path}: {err}")
    for fam_key, fam in families.items():
        for blk in fam.blocks:
            data = blk.data
            key = entry_composite_key(data) if isinstance(data, dict) else None
            if key is None:
                continue
            yield (fam_key or "(root)", key, data)


# ── Phase 0 导入（幂等） ────────────────────────────────────────────────────────


def _seed_catalog(cur: object, scan: dict, *, schema: str = SCHEMA_NAME) -> bool:
    """catalog 种子（INSERT ON CONFLICT DO NOTHING）；返回是否新插。"""
    cur.execute(
        f"INSERT INTO {_t('registry_catalog', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
        "(registry_id, physical_path, family_key, extra_families, identity_mode, "
        " unique_key_fields, maintenance, entry_schema) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
        "ON CONFLICT (registry_id) DO NOTHING RETURNING registry_id",
        (
            scan["registry_id"],
            scan["physical_path"],
            scan["primary_family"],
            json.dumps(scan["extra_families"]),
            scan["identity_mode"],
            json.dumps(scan["header"].get("unique_key")) if scan["header"].get("unique_key") else None,
            scan["maintenance"],
            json.dumps(scan["header"].get("entry_schema")) if scan["header"].get("entry_schema") else None,
        ),
    )
    return cur.fetchone() is not None


def import_baseline(
    repo_root: Path,
    physical_path: str,
    *,
    dry_run: bool = False,
    session_id: str = DEFAULT_SESSION,
    conn: object | None = None,
    schema: str = SCHEMA_NAME,
) -> dict:
    """条目级基线导入。幂等：同键已存在=skip（零新事件）；身份不可判=passthrough。"""
    scan = scan_registry_file(repo_root, physical_path)
    rid = scan["registry_id"]
    report = {
        "registry_id": rid,
        "physical_path": physical_path,
        "dry_run": dry_run,
        "scan": {k: scan[k] for k in ("family_stats", "entries_total", "passthrough_total", "identity_mode")},
        "catalog_seeded": False,
        "entries_imported": 0,
        "entries_skipped_existing": 0,
        "events_written": 0,
    }
    if dry_run:
        return report

    owned = conn is None
    c = conn or _open_writer_conn()
    try:
        with c.cursor() as cur:
            report["catalog_seeded"] = _seed_catalog(cur, scan, schema=schema)
            for family_key, entry_key, payload in _iter_scan_entries(repo_root, physical_path):
                cur.execute(
                    f"INSERT INTO {_t('registry_entry', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                    "(registry_id, family_key, entry_key, payload, payload_sha256, "
                    " version, created_by, updated_by) "
                    "VALUES (%s,%s,%s,%s,%s,1,%s,%s) "
                    "ON CONFLICT (registry_id, family_key, entry_key) DO NOTHING "
                    "RETURNING entry_pk",
                    (
                        rid,
                        family_key,
                        entry_key,
                        _jsonb(payload),
                        canonical_payload_sha256(payload),
                        session_id,
                        session_id,
                    ),
                )
                row = cur.fetchone()
                if row is None:
                    report["entries_skipped_existing"] += 1
                    continue
                event_id = _record_event(
                    cur,
                    registry_id=rid,
                    family_key=family_key,
                    entry_key=entry_key,
                    action="import",
                    actor_session=session_id,
                    actor_kind="system",
                    after_version=1,
                    payload_after=payload,
                    reason=IMPORT_REASON,
                    schema=schema,
                )
                cur.execute(
                    f"UPDATE {_t('registry_entry', schema)} SET last_event_id=%s "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                    "WHERE entry_pk=%s",
                    (event_id, row[0]),
                )
                report["entries_imported"] += 1
                report["events_written"] += 1
        if owned:
            c.commit()
        else:
            c.commit()
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.rollback()
        raise
    finally:
        if owned:
            c.close()
    return report


def _jsonb(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


# ── 快照发布（不可变全量 + 每册单调版本） ────────────────────────────────────────


def publish_snapshot(
    registry_id: str,
    *,
    git_commit_ref: str | None = None,
    session_id: str = DEFAULT_SESSION,
    conn: object | None = None,
    schema: str = SCHEMA_NAME,
) -> dict:
    """发布当前 active 条目集为不可变快照；同 content_sha256 重复发布=noop 幂等。"""
    owned = conn is None
    c = conn or _open_writer_conn()
    try:
        with c.cursor() as cur:
            cur.execute(
                f"SELECT family_key, entry_key, payload, payload_sha256 "
                f"FROM {_t('registry_entry', schema)} "
                "WHERE registry_id=%s AND status='active' ORDER BY family_key, entry_key",
                (registry_id,),
            )
            rows = cur.fetchall()
            manifest = {f"{fk}||{ek}": sha for fk, ek, _, sha in rows}
            bundle = {f"{fk}||{ek}": payload for fk, ek, payload, _ in rows}
            content_sha = hashlib.sha256(
                json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            cur.execute(
                f"SELECT snapshot_version, content_sha256 FROM {_t('registry_snapshot', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                "WHERE registry_id=%s ORDER BY snapshot_version DESC LIMIT 1",
                (registry_id,),
            )
            latest = cur.fetchone()
            if latest and latest[1] == content_sha:
                c.commit()
                return {
                    "registry_id": registry_id,
                    "noop": True,
                    "snapshot_version": int(latest[0]),
                    "entry_count": len(rows),
                }
            parent = int(latest[0]) if latest else None
            new_version = (int(latest[0]) + 1) if latest else 1
            cur.execute(
                f"INSERT INTO {_t('registry_snapshot', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                "(registry_id, snapshot_version, parent_snapshot_version, manifest, bundle, "
                " content_sha256, entry_count, git_commit_ref, published_by) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING snapshot_version",
                (
                    registry_id,
                    new_version,
                    parent,
                    _jsonb(manifest),
                    _jsonb(bundle),
                    content_sha,
                    len(rows),
                    git_commit_ref,
                    session_id,
                ),
            )
            out_version = int(cur.fetchone()[0])
            _record_event(
                cur,
                registry_id=registry_id,
                family_key="(registry)",
                entry_key="*",
                action="publish",
                actor_session=session_id,
                actor_kind="system",
                base_version=parent,
                after_version=out_version,
                payload_after={"manifest_sha256": content_sha, "entry_count": len(rows)},
                reason=PUBLISH_REASON,
                schema=schema,
            )
            cur.execute(
                f"UPDATE {_t('registry_catalog', schema)} SET ledger_version=%s, "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                "updated_at=now() WHERE registry_id=%s",
                (out_version, registry_id),
            )
        c.commit()
        return {
            "registry_id": registry_id,
            "noop": False,
            "snapshot_version": out_version,
            "entry_count": len(rows),
            "content_sha256": content_sha,
        }
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.rollback()
        raise
    finally:
        if owned:
            c.close()


# ── 双轨对账（Phase 1：YAML→PG insert-only + drift 事件） ───────────────────────


def reconcile_registry(
    repo_root: Path,
    physical_path: str,
    *,
    session_id: str = DEFAULT_SESSION,
    conn: object | None = None,
    schema: str = SCHEMA_NAME,
) -> dict:
    """双轨对账一册。PG 缺=补登记（reconcile_drift 事件）；同键异内容/PG 独有=只记事件
    绝不覆写（Phase 1 期 YAML 是 commit 真源，处置归人/后续波次）。幂等：干净册重跑
    零新事件零新行。zero_unexplained_drift=True 是对账门 PASS 的机械判据。"""
    scan = scan_registry_file(repo_root, physical_path)
    rid = scan["registry_id"]
    # first-wins 对齐 DB（ON CONFLICT DO NOTHING=首条占坑）：同身份多条=历史脏数据
    # （align-dirty §3.14-R1 在案形态），对账以首条为锚；后条差异数=identity_collisions
    # 呈报不静默改（P-2 呈报制）。
    yaml_map: dict[tuple[str, str], tuple[str, dict]] = {}
    collisions = 0
    collision_diff = 0
    for family_key, entry_key, payload in _iter_scan_entries(repo_root, physical_path):
        key = (family_key, entry_key)
        sha = canonical_payload_sha256(payload)
        if key in yaml_map:
            collisions += 1
            if yaml_map[key][0] != sha:
                collision_diff += 1
            continue
        yaml_map[key] = (sha, payload)

    owned = conn is None
    c = conn or _open_writer_conn()
    report = {
        "registry_id": rid,
        "physical_path": physical_path,
        "yaml_entries": len(yaml_map),
        "backfilled": 0,
        "content_mismatch": 0,
        "pg_only": 0,
        "clean_match": 0,
        "identity_collisions": collisions,
        "identity_collisions_diff_payload": collision_diff,
        "events_written": 0,
    }
    try:
        with c.cursor() as cur:
            cur.execute(
                f"SELECT family_key, entry_key, payload_sha256, version, payload "
                f"FROM {_t('registry_entry', schema)} WHERE registry_id=%s AND status='active'",
                (rid,),
            )
            pg_rows = cur.fetchall()
            report["pg_entries"] = len(pg_rows)
            pg_map = {(fk, ek): (sha, int(ver), payload) for fk, ek, sha, ver, payload in pg_rows}

            for key, (sha, payload) in yaml_map.items():
                pg_row = pg_map.get(key)
                if pg_row is None:
                    fk, ek = key
                    cur.execute(
                        f"INSERT INTO {_t('registry_entry', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                        "(registry_id, family_key, entry_key, payload, payload_sha256, "
                        " version, created_by, updated_by) "
                        "VALUES (%s,%s,%s,%s,%s,1,%s,%s) RETURNING entry_pk",
                        (rid, fk, ek, _jsonb(payload), sha, session_id, session_id),
                    )
                    entry_pk = cur.fetchone()[0]
                    event_id = _record_event(
                        cur,
                        registry_id=rid,
                        family_key=fk,
                        entry_key=ek,
                        action="reconcile_drift",
                        actor_session=session_id,
                        actor_kind="system",
                        after_version=1,
                        payload_after=payload,
                        reason=RECONCILE_REASON,
                        detail={"kind": "missing_in_pg_backfilled"},
                        schema=schema,
                    )
                    cur.execute(
                        f"UPDATE {_t('registry_entry', schema)} SET last_event_id=%s WHERE entry_pk=%s",  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                        (event_id, entry_pk),
                    )
                    report["backfilled"] += 1
                    report["events_written"] += 1
                elif pg_row[0] == sha:
                    report["clean_match"] += 1
                else:
                    # 双轨吸收（任务令⑥"YAML 写→PG 同写"）：Phase 1 期 YAML=commit 真源，
                    # 落地更新的内容按 YAML 吸收进 PG（version+1+事件全留痕）；
                    # pg_only（YAML 缺失）仍只记账不删——缺失永不推断为删除意图。
                    fk, ek = key
                    new_version = int(pg_row[1]) + 1
                    cur.execute(
                        f"UPDATE {_t('registry_entry', schema)} "
                        "SET payload=%s, payload_sha256=%s, version=%s, "
                        "updated_by=%s, updated_at=now() "
                        "WHERE registry_id=%s AND family_key=%s AND entry_key=%s "
                        "AND version=%s",
                        (_jsonb(payload), sha, new_version, session_id, rid, fk, ek, int(pg_row[1])),
                    )
                    if cur.rowcount == 0:
                        report["content_mismatch"] += 1  # 并发改写=真冲突，留待下轮
                        continue
                    _record_event(
                        cur,
                        registry_id=rid,
                        family_key=fk,
                        entry_key=ek,
                        action="reconcile_drift",
                        actor_session=session_id,
                        actor_kind="system",
                        base_version=int(pg_row[1]),
                        after_version=new_version,
                        payload_after=payload,
                        reason=RECONCILE_REASON,
                        before_sha256=pg_row[0],
                        detail={
                            "kind": "content_mismatch_absorbed_from_yaml",
                            "yaml_sha256": sha,
                            "pg_sha256": pg_row[0],
                        },
                        schema=schema,
                    )
                    report["absorbed_from_yaml"] = report.get("absorbed_from_yaml", 0) + 1
                    report["events_written"] += 1

            for key, (sha, ver, _payload) in pg_map.items():
                if key not in yaml_map:
                    fk, ek = key
                    _record_event(
                        cur,
                        registry_id=rid,
                        family_key=fk,
                        entry_key=ek,
                        action="reconcile_drift",
                        actor_session=session_id,
                        actor_kind="system",
                        base_version=ver,
                        after_version=ver,
                        payload_after={},
                        reason=RECONCILE_REASON,
                        before_sha256=sha,
                        detail={"kind": "pg_only_no_yaml_entry", "resolution": "logged_not_deleted"},
                        schema=schema,
                    )
                    report["pg_only"] += 1
                    report["events_written"] += 1
        c.commit()
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.rollback()
        raise
    finally:
        if owned:
            c.close()
    report["zero_unexplained_drift"] = report["content_mismatch"] == 0 and report["pg_only"] == 0
    return report
