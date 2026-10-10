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
#   身份声明制（册头 unique_key 声明优先，无声明退位置首标量）=st-sI-identity-20261004
#   手术1（f10 §6.1）；条目切分唯一真源=_split_registry_entries（yaml.compose 行号法）；
#   导入幂等（ON CONFLICT DO NOTHING，重跑零新事件）；双轨对账=insert-only
#   （YAML→PG 补登记，同键异内容/PG 独有条目只记 reconcile_drift 事件绝不覆写——
#   Phase 1 期 YAML 仍是 commit 真源，PG wins 自愈归 cutover 后，届时由投影生成器接管）；
#   同内容 rekey 迁移绝不插第二行（B3 重复行放大器封死）
# [MODIFY-GUARD] 新建 2026-09-24 st-wm1-wave0-20260924（W-M1 波0⑤⑥施工件）；
#   2026-10-04 st-sI-identity-20261004 身份声明制+bundle 身份置首+写前冒烟+rekey（F10 治本）
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

# 身份声明制真源委托（st-sI-identity-20261004 手术1）：声明解析+逐族适用性
# 真源=commit_queue_landing（QMine A1 件③），gate 侧已封装入口——账本/门禁/合并器
# 三方同一声明口径，永不复制逻辑
from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import _declared_fields_by_family
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

# [SQL] W-M1 ledger SQL 真源集中（参数化查询）——reconcile 复活路径（2026-10-03 B3 实弹治本）
_SQL_REACTIVATE_SELECT = (
    "SELECT entry_pk, version, status FROM {table} WHERE registry_id=%s AND family_key=%s AND entry_key=%s"
)
_SQL_REACTIVATE_UPDATE = (
    "UPDATE {table} "
    "SET status='active', payload=%s, payload_sha256=%s, version=%s, "
    "updated_by=%s, updated_at=now() WHERE entry_pk=%s"
)
# [SQL] 身份声明制批（st-sI-identity-20261004，F10 治本）：SQL 常量集中化（NOQA 密度治理）
_SQL_CATALOG_UNIQUE_KEY_FIELDS = "SELECT unique_key_fields FROM {table} WHERE registry_id=%s"
_SQL_CATALOG_PHYS_PATH = "SELECT physical_path FROM {table} WHERE registry_id=%s"
_SQL_CATALOG_DECL_BACKFILL = (
    "UPDATE {table} SET unique_key_fields=%s WHERE registry_id=%s AND unique_key_fields IS DISTINCT FROM %s::jsonb"
)
_SQL_SNAPSHOT_LATEST_BUNDLE = (
    "SELECT snapshot_version, content_sha256, bundle FROM {table} "
    "WHERE registry_id=%s ORDER BY snapshot_version DESC LIMIT 1"
)
# [SQL] 渐进腐蚀自锚（st-maint1-20261010 件①，2026-10-10 CAP 册 v157→v177 十五版
# 空上下文自我固化实录）：在本册自己的历史快照里找最近一份仍带 verbatim 上下文的
# bundle（header_lines 或 trailing_scalars 非空即候选）。unique_key_fields 是对象不是
# 数组，故只按前两件判候选。
_SQL_SNAPSHOT_CONTEXT_ANCHOR = (
    "SELECT snapshot_version, bundle->'header_lines', bundle->'trailing_scalars', "
    "       bundle->'unique_key_fields' "
    "FROM {table} WHERE registry_id=%s "
    "  AND (jsonb_array_length(COALESCE(bundle->'header_lines', '[]'::jsonb)) > 0 "
    "       OR jsonb_array_length(COALESCE(bundle->'trailing_scalars', '[]'::jsonb)) > 0) "
    "ORDER BY snapshot_version DESC LIMIT 1"
)
_SQL_ENTRY_KEY_EXISTS = "SELECT 1 FROM {table} WHERE registry_id=%s AND family_key=%s AND entry_key=%s"
_SQL_ENTRY_REKEY = (
    "UPDATE {table} SET entry_key=%s, updated_by=%s, updated_at=now() "
    "WHERE registry_id=%s AND family_key=%s AND entry_key=%s AND version=%s"
)
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
    retired 感知（裁定#503，2026-10-10 总统筹增补令·P1）：status=retired（墓碑）的
    条目不参与 first-wins——即便它排在文档序首位也让位给非墓碑同路径条目。
    病根=ROOR 双挂号（同路径挂 REG-CAPCAN-001 与空壳 REG-GEN-001）：任何路径→id
    反查取到空壳账本即持 0 条覆盖上万条投影（间歇性蒸发候选，A-12 真凶候选）。
    本函数是全仓唯一路径反查入口（render/物化/迁移/预检五通道同源），dedup 在此
    单点收紧即全通道闭环；红证=test_roor_path_resolution（构造 GEN 首位+墓碑仍返 CAPCAN）。
    """
    import yaml  # noqa: PLC0415

    roor_file = repo_root / ROOR_PATH
    index: dict[str, dict] = {}

    def _is_tombstoned(node: dict) -> bool:
        status = str(node.get("status", "")).lower()
        return status.startswith("retired") or status.startswith("墓碑")

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            pp = node.get("physical_path")
            if isinstance(pp, str) and node.get("registry_id"):
                key = pp.replace("\\", "/")
                tomb = _is_tombstoned(node)
                if key not in index:
                    if not tomb:  # first-wins（文档序=正主优先；墓碑条目不让座占位）
                        index[key] = {
                            "registry_id": str(node["registry_id"]),
                            "maintenance": str(node.get("maintenance", "manual")),
                        }
                elif tomb and not _is_tombstoned(index[key]):
                    pass  # 在册正主非墓碑 → 墓碑后来者不覆盖（防御序漂移）
                elif not tomb and _is_tombstoned(index[key]):
                    # 正主后到而先到者是墓碑 → 正主夺回（墓碑永不占位）
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


def _family_statistics(families: dict, declared: dict[object, tuple[str, ...]] | None = None) -> tuple[dict, int, list]:
    """族统计：每族 dict 条目数/passthrough 数/身份清单（供扫描报告与主族判定）。

    declared=身份声明计划（{族键: 声明字段元组}，None=位置口径）——身份键串按册内
    unique_key 声明推导（st-sI-identity-20261004 手术1：身份与字段位置解耦）。
    """
    family_stats: dict = {}
    total_dict_entries = 0
    all_identities: list = []
    for fam_key, fam in families.items():
        fields = (declared or {}).get(fam_key)
        dict_entries = 0
        passthrough = 0
        identities: list = []
        for blk in fam.blocks:
            key = entry_composite_key(blk.data, fields) if isinstance(blk.data, dict) else None
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
    # unique_key 声明本体是 list/dict 形态——头部标量过滤会漏收，显式并回（手术1b）
    if isinstance(full, dict) and "unique_key" in full:
        header["unique_key"] = full["unique_key"]
    families, err = _split_registry_entries(text)
    if err:
        raise ValueError(f"{physical_path}: {err}")

    roor = load_roor_index(repo_root)
    roor_row = roor.get(physical_path.replace("\\", "/"), {})
    registry_id = str(header.get("registry_id") or roor_row.get("registry_id") or "")
    if not registry_id:
        raise ValueError(f"{physical_path}: registry_id unresolved (YAML header ∪ ROOR 均无)")

    # 身份声明制（st-sI-identity-20261004）：册头 unique_key 声明 → 逐族适用计划
    declared = _declared_fields_by_family(text, full)
    family_stats, total_dict_entries, _ = _family_statistics(families, declared)
    primary = max(
        ((k, v) for k, v in family_stats.items() if v["entries"] > 0),
        key=lambda kv: kv[1]["entries"],
        default=(None, None),
    )
    return {
        "registry_id": registry_id,
        "physical_path": physical_path,
        # unique_key 进 header 面（手术1b：原头部键白名单漏收 → catalog 种子恒 None，
        # f10 §6.1 实证盲区）；声明本体（list/dict）保留原形态供种子落库
        "header": {
            k: header[k]
            for k in ("schema_version", "module_id", "status", "version", "date", "unique_key")
            if k in header
        },
        "maintenance": roor_row.get("maintenance", "manual"),
        "family_stats": family_stats,
        "primary_family": primary[0],
        "extra_families": {k: v["entries"] + v["passthrough"] for k, v in family_stats.items() if k != primary[0]},
        "identity_mode": _identity_mode(families),
        "declared_identity_families": sorted(str(k) for k in declared),
        "entries_total": total_dict_entries,
        "passthrough_total": sum(v["passthrough"] for v in family_stats.values()),
    }


def _scan_declared_plan(repo_root: Path, physical_path: str) -> dict[object, tuple[str, ...]]:
    """盘面册头 unique_key 声明计划（零 DB 依赖；读失败=空计划退位置口径）。"""
    import yaml  # noqa: PLC0415

    try:
        text = (repo_root / physical_path).read_text(encoding="utf-8")
        return _declared_fields_by_family(text, yaml.safe_load(text))
    except Exception:  # noqa: BLE001 — 声明面不可读=无声明，fail-open 退现状
        return {}


def _iter_scan_entries(repo_root: Path, physical_path: str, declared: dict[object, tuple[str, ...]] | None = None):
    """产出 (family_key, entry_key, payload)；身份不可判的条目跳过（passthrough）。

    declared=身份声明计划（None=现场自解析盘面声明；{} 显式空=位置口径）。
    """
    from scripts.governance.commit_queue_landing import _split_registry_entries  # noqa: PLC0415

    text = (repo_root / physical_path).read_text(encoding="utf-8")
    if declared is None:
        declared = _scan_declared_plan(repo_root, physical_path)
    families, err = _split_registry_entries(text)
    if err:
        raise ValueError(f"{physical_path}: {err}")
    for fam_key, fam in families.items():
        fields = declared.get(fam_key)
        for blk in fam.blocks:
            data = blk.data
            key = entry_composite_key(data, fields) if isinstance(data, dict) else None
            if key is None:
                continue
            yield (fam_key or "(root)", key, data)


# ── Phase 0 导入（幂等） ────────────────────────────────────────────────────────


def _seed_catalog(cur: object, scan: dict, *, schema: str = SCHEMA_NAME) -> bool:
    """catalog 种子（INSERT ON CONFLICT DO NOTHING）；返回是否新插。

    手术1b（st-sI-identity-20261004）：原头部键白名单漏收 unique_key → 种子恒 None
    （f10 §6.1 实证盲区）。现声明随扫描落库；既有行声明列空缺时回填（IS DISTINCT
    FROM 幂等，重跑零抖动）——api/publish 消费面由此取声明口径。
    """
    unique_key_decl = scan["header"].get("unique_key")
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
            json.dumps(unique_key_decl, ensure_ascii=False) if unique_key_decl is not None else None,
            scan["maintenance"],
            json.dumps(scan["header"].get("entry_schema")) if scan["header"].get("entry_schema") else None,
        ),
    )
    newly_seeded = cur.fetchone() is not None
    if not newly_seeded and unique_key_decl is not None:
        decl_json = json.dumps(unique_key_decl, ensure_ascii=False)
        # jsonb 语义等值比较（::text 会因 jsonb 键序规范化恒不等 → 每跑必写，非幂等）
        cur.execute(
            _SQL_CATALOG_DECL_BACKFILL.format(table=_t("registry_catalog", schema)),
            (decl_json, scan["registry_id"], decl_json),
        )
    return newly_seeded


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


def _projection_context_from_disk(
    registry_id: str,
    repo_root: Path | None,
    schema: str,
    c: object,
) -> tuple[list[str], list, int]:
    """快照投影上下文（header_lines/trailing_scalars/ledger_revision）提取。

    WM1_24h_evaluation §3.1 bundle 契约断裂治本（2026-09-30 F4，st-nightsweep2-nf-20260930）：
    读端 snapshot_from_bundle 契约要求 header_lines/sections/trailing_scalars（乙号文
    设计形态），旧写端只落扁平 map → load_latest_snapshot 恒抛"bundle 结构不符契约:
    'sections'"，render 通道物理不可执行。条目 sections 由 PG active 行构造（本函数
    只补 PG 不存的头部/尾部 verbatim+账本修订号）：按册 physical_path（registry_catalog
    反查）读盘上 YAML compose 提取；任一环失败降级空值（fail-open，快照仍可发布，
    渲染语义等值验收不受阻，仅 verbatim 头部缺位）。
    """
    header_lines: list[str] = []
    trailing: list = []
    ledger_revision = 0
    try:
        with c.cursor() as cur:
            cur.execute(
                f"SELECT physical_path, COALESCE(ledger_version,0) FROM {_t('registry_catalog', schema)} "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                "WHERE registry_id=%s",
                (registry_id,),
            )
            row = cur.fetchone()
        ledger_revision = int(row[1] or 0) if row else 0
        if row and repo_root is not None and row[0]:
            from zephyr.governance.registry_projection.model import snapshot_from_yaml  # noqa: PLC0415

            phys = str(row[0])
            text = (Path(repo_root) / phys).read_text(encoding="utf-8")
            snap = snapshot_from_yaml(text, registry_id=registry_id, physical_path=phys)
            return snap.header_lines, [list(p) for p in snap.trailing_scalars], ledger_revision
    except Exception:  # noqa: BLE001 — 投影上下文降级（快照发布主链不受阻）
        pass
    return header_lines, trailing, ledger_revision


def _projection_context_from_snapshot_anchor(
    registry_id: str,
    schema: str,
    c: object,
) -> tuple[list[str], list, dict[object, tuple[str, ...]]] | None:
    """账本自锚上下文（st-maint1-20261010 件①，渐进腐蚀自我固化治本）。

    病灶（2026-10-10 实弹）：`_projection_context_from_disk` 的
    header_lines/trailing_scalars/声明计划**唯一来源是盘面 YAML**，而盘面本身又是
    同一快照的渲染产物——盘面一旦被剥光（实测 registry_snapshot v157→v177 连续 15 版
    header_lines=[] / trailing_scalars=[] / unique_key_fields={}），下一次发布就把
    "剥光"重新烤进新快照，形成 盘面→bundle→render→盘面 的闭环自我固化；账本↔投影
    恒 zero-drift，故 render 永远自愈不了。落成的可见征状＝CAP 册顶层
    `di_seam_exemptions` 尾部键消失 → REGISTRY-YAML-PARSE「顶层 di_seam_exemptions
    键缺失」同签名熔断 6 次 → 全仓新建 .py/.md/.yaml 入库堵死。

    处方（证据制，非发明制）：只在本册**自己的历史快照**里取最近一份带非空上下文的
    bundle 作锚，由调用方逐件补缺（盘面已有的一律以盘面为准，锚不覆盖现值）。
    查无锚＝不补，保持现状——绝不凭空造上下文，零幻觉面。
    """
    try:
        with c.cursor() as cur:
            cur.execute(
                _SQL_SNAPSHOT_CONTEXT_ANCHOR.format(table=_t("registry_snapshot", schema)),
                (registry_id,),
            )
            row = cur.fetchone()
    except Exception:  # noqa: BLE001 — 锚不可读=不补（退现行为，发布主链不受阻）
        return None
    if row is None:
        return None

    def _as_list(raw: object) -> list:
        if raw is None:
            return []
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except Exception:  # noqa: BLE001 — 不可解析=无锚价值
                return []
            return parsed if isinstance(parsed, list) else []
        return raw if isinstance(raw, list) else []

    _anchor_version, raw_header, raw_trailing, raw_decl = row
    header = [str(x) for x in _as_list(raw_header)]
    trailing = [list(p) for p in _as_list(raw_trailing) if isinstance(p, list) and p]
    if isinstance(raw_decl, str):
        try:
            raw_decl = json.loads(raw_decl)
        except Exception:  # noqa: BLE001
            raw_decl = None
    decl: dict[object, tuple[str, ...]] = {}
    if isinstance(raw_decl, dict):
        for fam, fields in raw_decl.items():
            if isinstance(fields, list) and fields and all(isinstance(f, str) and f for f in fields):
                decl[str(fam)] = tuple(fields)
    if not header and not trailing and not decl:
        return None
    return header, trailing, decl


def _heal_projection_context(
    header_lines: list[str],
    trailing_scalars: list,
    declared: dict[object, tuple[str, ...]],
    anchor: tuple[list[str], list, dict[object, tuple[str, ...]]] | None,
) -> tuple[list[str], list, dict[object, tuple[str, ...]], dict[str, object]]:
    """自锚补洞纯函数（可测面）：锚只补**空洞**，盘面已有的一律以盘面为准。

    返回 (header_lines, trailing_scalars, declared, heal_manifest)；manifest 非空即
    表示本次发布有件来自历史快照锚，调用方须据此落 publish_context_heal 事件行。

    方向性纪律（判据本体）：这一手存在的唯一理由是阻止"空上下文"被当稳定态烤进新版
    （2026-10-10 v157→v177 十五版自我固化实录）。锚绝不覆盖盘面现值＝盘面前进优先；
    查无锚＝原样返回（零发明）。
    """
    if anchor is None:
        return header_lines, trailing_scalars, declared, {}
    a_header, a_trailing, a_decl = anchor
    healed: dict[str, object] = {}
    if not header_lines and a_header:
        header_lines = a_header
        healed["header_lines"] = len(a_header)
    if not trailing_scalars and a_trailing:
        trailing_scalars = a_trailing
        healed["trailing_scalars"] = [str(p[0]) for p in a_trailing if p]
    if not declared and a_decl:
        declared = a_decl
        healed["unique_key_fields"] = sorted(str(f) for f in a_decl)
    return header_lines, trailing_scalars, declared, healed


def _declared_plan_from_conn(registry_id: str, schema: str, c: object) -> dict[object, tuple[str, ...]]:
    """catalog 声明列 → 逐族计划（盘面声明缺位时的回退面；空/退化=空计划）。"""
    try:
        with c.cursor() as cur:
            cur.execute(
                _SQL_CATALOG_UNIQUE_KEY_FIELDS.format(table=_t("registry_catalog", schema)),
                (registry_id,),
            )
            row = cur.fetchone()
    except Exception:  # noqa: BLE001 — catalog 面不可读=空计划（fail-open 退位置口径）
        return {}
    if not row or not row[0]:
        return {}
    raw = row[0]
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:  # noqa: BLE001
            return {}
    plan: dict[object, tuple[str, ...]] = {}
    if isinstance(raw, list):
        if raw and all(isinstance(f, str) and f for f in raw):
            plan["*"] = tuple(raw)
    elif isinstance(raw, dict):
        for fam, fields in raw.items():
            if isinstance(fields, list) and fields and all(isinstance(f, str) and f for f in fields):
                plan[str(fam)] = tuple(fields)
    return plan


def _identity_first_pairs(payload: dict, fields: tuple[str, ...] | None) -> list[list]:
    """payload → 有序 [key,value] 对数组，声明身份字段置首（手术2：bundle 保全字段原序）。

    PG jsonb 按（键长,字节序）重排键序——render 照 bundle 序发射后重扫"位置首字段"
    换人 → 身份键串漂移（f10 §3.1 键序链主犯）。身份字段置首使 render 后重扫（含
    位置口径消费面）恒取同一首字段；其余字段维持 payload 原序（渲染=盘面形最大化）。
    无声明=原序直通（行为零变化）。
    """
    pairs = [[str(k), v] for k, v in payload.items()]
    if not fields:
        return pairs
    field_set = set(fields)
    head = [[f, payload[f]] for f in fields if f in payload]
    rest = [pair for pair in pairs if pair[0] not in field_set]
    return head + rest


def _bundle_render_skeleton(bundle: object) -> tuple | None:
    """bundle → 渲染骨架指纹（声明计划/头部/尾部/条目键序；None=旧形态/不可比）。

    手术2 noop 幂等扩展用：manifest sha 序不敏感（payload 键排序哈希），键序/声明
    前进不可见——骨架指纹补位（值不比，只比影响渲染形态与身份口径的结构面）。
    """
    if isinstance(bundle, str):
        try:
            bundle = json.loads(bundle)
        except Exception:  # noqa: BLE001 — 不可解析=不可比
            return None
    if not isinstance(bundle, dict) or "sections" not in bundle:
        return None
    try:
        key_order = tuple(
            (str(sec["root_key"]), tuple(tuple(str(k) for k, _v in entry) for entry in sec["entries"]))
            for sec in bundle["sections"]
        )
    except Exception:  # noqa: BLE001 — 结构异常=不可比
        return None
    return (
        json.dumps(bundle.get("unique_key_fields") or {}, sort_keys=True, ensure_ascii=False),
        tuple(str(line) for line in bundle.get("header_lines") or []),
        tuple((str(k), repr(v)) for k, v in bundle.get("trailing_scalars") or []),
        key_order,
    )


def publish_snapshot(
    registry_id: str,
    *,
    git_commit_ref: str | None = None,
    session_id: str = DEFAULT_SESSION,
    conn: object | None = None,
    schema: str = SCHEMA_NAME,
    repo_root: Path | None = None,
) -> dict:
    """发布当前 active 条目集为不可变快照；同 content_sha256 重复发布=noop 幂等。

    bundle 契约=读端 snapshot_from_bundle 结构形态（WM1_24h_evaluation §3.1 统一，
    2026-09-30）：{registry_id, header_lines[], sections[{root_key,entries[[k,v]...]}],
    trailing_scalars[[k,v]...], ledger_revision, snapshot_version, content_sha256,
    unique_key_fields{family:[field]}}——条目=有序 [key,value] 对数组（jsonb 数组
    保序+重复键可表达）；头部/尾部 verbatim 由 _projection_context_from_disk 从盘上
    YAML 提取（repo_root 提供时）。content_sha 仍按 manifest 哈希（noop 幂等语义不变）。

    手术2（st-sI-identity-20261004，f10 §3.1 键序链治本）：条目对构建时声明身份字段
    置首——PG jsonb（键长,字节序）重排不再抢占位置首字段，render 后重扫恒同键；
    unique_key_fields=已解析逐族声明计划随 bundle 固化（读端零再解析）。

    渐进腐蚀守卫（st-tclose-infracure2-20261005 件3）：repo_root=None 时
    _projection_context_from_disk/_scan_declared_plan 的盘面来源缺失（fail-open 降级
    空头部/空尾部/空声明），实战事故=渲染丢 di_seam_exemptions 等根键且 noop 幂等
    把腐蚀永久固化（骨架比对把"空尾部"当稳定态）。故裸发布机械拒绝。

    渐进腐蚀自锚（st-maint1-20261010 件①）：上一件只堵住了"repo_root 缺失"这一入口，
    没堵住"repo_root 在而盘面已被剥光"——2026-10-10 实弹 registry_snapshot v157→v177
    连续十五版 header_lines=[]/trailing_scalars=[]/unique_key_fields={}，闭源于
    上下文唯一来源=盘面而盘面=上一次 render 的产物，账本↔投影恒 zero-drift 故永不
    自愈。现三项上下文任一为空即回查本册历史快照锚补空洞（锚只补不覆盖，查无锚保持
    现状），补洞事实以 action=publish_context_heal 事件行入册。
    """
    if repo_root is None:
        raise ValueError(
            "publish_snapshot: repo_root 缺失将丢尾部段（header_lines/trailing_scalars/"
            "unique_key_fields 盘面来源缺失，渲染即丢 di_seam_exemptions 等根键），"
            "禁止裸发布——显式传 repo_root（仓库根，如 Path('.')）后重试"
        )
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
            content_sha = hashlib.sha256(
                json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            cur.execute(
                _SQL_SNAPSHOT_LATEST_BUNDLE.format(table=_t("registry_snapshot", schema)),
                (registry_id,),
            )
            latest = cur.fetchone()
            # noop 幂等扩展（手术2）：manifest 同 sha 且**渲染骨架**（声明计划/头部/
            # 尾部/条目键序）不变才 noop——条目内容不变而声明或键序前进（身份声明制
            # 落地窗口）必须出新版，否则旧 bundle 永远缺 unique_key_fields/身份置序，
            # render 侧 PG-wins 会把盘面声明私改回滚（v15→v16 窗口实证推演）。
            parent = int(latest[0]) if latest else None
            new_version = (int(latest[0]) + 1) if latest else 1
            # 身份声明计划（手术1/2，st-sI-identity-20261004）：盘面册头声明优先，
            # catalog 声明列回退；计划随 bundle 落显式键（读端零再解析）
            declared: dict[object, tuple[str, ...]] = {}
            if repo_root is not None:
                try:
                    with c.cursor() as dcur:  # 独立游标（禁遮蔽外层 cur：with 退出关闭会废掉外层名）
                        dcur.execute(
                            _SQL_CATALOG_PHYS_PATH.format(table=_t("registry_catalog", schema)),
                            (registry_id,),
                        )
                        prow = dcur.fetchone()
                    if prow and prow[0]:
                        declared = _scan_declared_plan(Path(repo_root), str(prow[0]))
                except Exception:  # noqa: BLE001 — 声明面失败=空计划（位置口径，快照仍可发布）
                    declared = {}
            if not declared:
                declared = _declared_plan_from_conn(registry_id, schema, c)
            header_lines, trailing_scalars, ledger_revision = _projection_context_from_disk(
                registry_id, repo_root, schema, c
            )
            # 渐进腐蚀自锚（st-maint1-20261010 件①）：三项上下文任一为空即回查本册历史
            # 快照锚，逐件补空洞（盘面已有=盘面赢，锚绝不覆盖现值）。必须在 sections
            # 构建之前完成——declared 决定条目身份字段置首，补晚了 bundle 声明与键序自相矛盾。
            # 缺这一手时"盘面剥光"会被下面的 noop 骨架比对当成稳定态永久固化
            # （2026-10-10 v157→v177 连续十五版空上下文实录）。
            context_heal: dict[str, object] = {}
            if not header_lines or not trailing_scalars or not declared:
                header_lines, trailing_scalars, declared, context_heal = _heal_projection_context(
                    header_lines,
                    trailing_scalars,
                    declared,
                    _projection_context_from_snapshot_anchor(registry_id, schema, c),
                )
            # 结构化 bundle（读端 snapshot_from_bundle 契约，WM1_24h_evaluation §3.1 统一）：
            # 条目按 family_key 分节段，条目=有序 [key, value] 对数组（jsonb 保序）；
            # 手术2：声明身份字段置首（jsonb 键序重排不再抢占位置首字段→render 后重扫同键）
            sections: dict[str, list] = {}
            for fk, ek, payload, _sha in rows:
                if isinstance(payload, dict):
                    pairs = _identity_first_pairs(payload, declared.get(str(fk)) or declared.get("*"))
                else:  # 非.dict payload 保底整值一条（import 面只收 dict，防御位）
                    pairs = [[str(ek), payload]]
                sections.setdefault(str(fk), []).append(pairs)
            bundle = {
                "registry_id": registry_id,
                "header_lines": header_lines,
                "sections": [{"root_key": fk, "entries": sections[fk]} for fk in sorted(sections)],
                "trailing_scalars": trailing_scalars,
                "ledger_revision": ledger_revision,
                "snapshot_version": new_version,
                "content_sha256": content_sha,
                # 声明计划随快照固化（读端 snapshot.unique_key_fields；旧读端忽略未知键）
                "unique_key_fields": {str(fk): list(fields) for fk, fields in declared.items()},
            }
            if (
                latest
                and latest[1] == content_sha
                and _bundle_render_skeleton(latest[2]) == _bundle_render_skeleton(bundle)
            ):
                c.commit()
                return {
                    "registry_id": registry_id,
                    "noop": True,
                    "snapshot_version": int(latest[0]),
                    "entry_count": len(rows),
                }
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
            if context_heal:
                # 自锚补洞必须留痕可审计：哪一版、补了哪几件、补了多少，事后能一命令查出
                _record_event(
                    cur,
                    registry_id=registry_id,
                    family_key="(registry)",
                    entry_key="*",
                    action="publish_context_heal",
                    actor_session=session_id,
                    actor_kind="system",
                    base_version=parent,
                    after_version=out_version,
                    payload_after=context_heal,
                    reason=PUBLISH_REASON,
                    detail={"kind": "projection_context_self_anchor", "disk_context_missing": True},
                    schema=schema,
                )
        c.commit()
        return {
            "registry_id": registry_id,
            "noop": False,
            "snapshot_version": out_version,
            "entry_count": len(rows),
            "content_sha256": content_sha,
            "context_heal": context_heal,
        }
    except psycopg2.Error:  # DB 错误回滚重抛；非 DB 异常由连接关闭路径回收事务
        c.rollback()
        raise
    finally:
        if owned:
            c.close()


# ── 双轨对账（Phase 1：YAML→PG insert-only + drift 事件） ───────────────────────


SMOKE_SAMPLE_SIZE = 50


def _identity_smoke(repo_root: Path, physical_path: str, declared: dict[object, tuple[str, ...]]) -> dict:
    """写前身份稳定性冒烟（手术4，st-sI-identity-20261004；f10 §6.5）。

    盘面抽样 ≤50 条 render-in-memory → 重扫比对身份键串 + 声明族撞并计数——
    不稳定只告警不阻断（报告行 identity_smoke_*）；零 DB 依赖零写盘。
    B3 病灶形态（jsonb 键序重排→位置首字段换人→身份坍缩）在此现形。
    """
    from zephyr.governance.registry_projection.model import ProjectionSnapshot, Section, snapshot_from_yaml
    from zephyr.governance.registry_projection.renderer import render

    report = {"identity_smoke_sampled": 0, "identity_smoke_unstable": 0, "identity_smoke_examples": []}
    try:
        text = (repo_root / physical_path).read_text(encoding="utf-8")
        snap = snapshot_from_yaml(text, registry_id="smoke", physical_path=physical_path)
        sampled: list[Section] = []
        for sec in snap.sections:
            if len(sec.entries) <= SMOKE_SAMPLE_SIZE:
                sampled.append(sec)
                continue
            step = len(sec.entries) / SMOKE_SAMPLE_SIZE  # 确定性等距抽样（无随机）
            picked = [sec.entries[int(i * step)] for i in range(SMOKE_SAMPLE_SIZE)]
            sampled.append(Section(root_key=sec.root_key, entries=picked))
        mini = ProjectionSnapshot(
            registry_id="smoke", physical_path=physical_path, header_lines=[], sections=sampled, trailing_scalars=[]
        )
        from scripts.governance.commit_queue_landing import _split_registry_entries  # noqa: PLC0415

        rescan, err = _split_registry_entries(render(mini))
        if err:
            report["identity_smoke_unstable"] = -1
            report["identity_smoke_examples"] = [f"render rescan error: {err[:120]}"]
            return report
        for sec in sampled:
            fields = declared.get(sec.root_key) or declared.get("*")
            rescan_ids = [
                entry_composite_key(bdata, fields) if isinstance((bdata := blk.data), dict) else None
                for blk in (rescan.get(sec.root_key).blocks if rescan.get(sec.root_key) else [])
            ]
            for idx, entry in enumerate(sec.entries):
                report["identity_smoke_sampled"] += 1
                expected = entry_composite_key(dict(entry), fields)
                got = rescan_ids[idx] if idx < len(rescan_ids) else None
                problems = []
                if expected != got:
                    problems.append(f"drift {expected!r}->{got!r}")
                if fields and expected is not None and rescan_ids.count(expected) > 1:
                    problems.append(f"collapse {expected!r}")
                if problems:
                    report["identity_smoke_unstable"] += 1
                    if len(report["identity_smoke_examples"]) < 5:
                        report["identity_smoke_examples"].append(f"{sec.root_key}[{idx}]: " + "; ".join(problems))
    except Exception as exc:  # noqa: BLE001 — 冒烟自身故障=不可判（-1 告警行，不阻断）
        report["identity_smoke_unstable"] = -1
        report["identity_smoke_examples"] = [f"smoke error: {type(exc).__name__}: {str(exc)[:120]}"]
    return report


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
    零新事件零新行。zero_unexplained_drift=True 是对账门 PASS 的机械判据。

    st-sI-identity-20261004 手术4（f10 §6.5 B3 放大器封堵）：
    - 写前身份稳定性冒烟：抽样 ≤50 键 render-in-memory 比对，不稳定=告警行不阻断；
    - 同内容 rekey 迁移：yaml 新键 ⇄ pg 旧键 canonical sha 相等（内容同一）时
      UPDATE 迁键（事件留痕），绝不插入第二行——键口径升级窗口零重复行注入。
    """
    scan = scan_registry_file(repo_root, physical_path)
    rid = scan["registry_id"]
    declared = _scan_declared_plan(repo_root, physical_path)
    smoke = _identity_smoke(repo_root, physical_path, declared)
    if smoke["identity_smoke_unstable"]:
        import logging  # noqa: PLC0415

        logging.getLogger(__name__).warning(
            "reconcile 身份稳定性冒烟不稳（%s %s）: sampled=%s unstable=%s examples=%s",
            rid,
            physical_path,
            smoke["identity_smoke_sampled"],
            smoke["identity_smoke_unstable"],
            smoke["identity_smoke_examples"],
        )
    # first-wins 对齐 DB（ON CONFLICT DO NOTHING=首条占坑）：同身份多条=历史脏数据
    # （align-dirty §3.14-R1 在案形态），对账以首条为锚；后条差异数=identity_collisions
    # 呈报不静默改（P-2 呈报制）。
    yaml_map: dict[tuple[str, str], tuple[str, dict]] = {}
    collisions = 0
    collision_diff = 0
    for family_key, entry_key, payload in _iter_scan_entries(repo_root, physical_path, declared):
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
        "rekeyed_identity": 0,
        "events_written": 0,
        **smoke,
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

            # 写前同内容 rekey 迁移（手术4，f10 §3.3/§6.5 B3 放大器封堵）：键口径升级/
            # 漂移窗口，yaml 新键与 pg 旧键指向同一内容（canonical sha 相等且唯一落点）时
            # UPDATE 迁键+事件留痕，绝不 INSERT 第二行——同键异内容（真冲突）永不 rekey。
            yaml_keys_by_sha: dict[tuple[str, str], list[tuple[str, str]]] = {}
            for yk, (sha, _p) in yaml_map.items():
                yaml_keys_by_sha.setdefault((yk[0], sha), []).append(yk)
            for pg_key in [k for k in pg_map if k not in yaml_map]:
                fk_old, ek_old = pg_key
                sha_old, ver_old, _payload_old = pg_map[pg_key]
                candidates = [yk for yk in yaml_keys_by_sha.get((fk_old, sha_old), ()) if yk not in pg_map]
                if len(candidates) != 1:
                    continue
                yk_new = candidates[0]
                cur.execute(
                    _SQL_ENTRY_KEY_EXISTS.format(table=_t("registry_entry", schema)),
                    (rid, yk_new[0], yk_new[1]),
                )
                if cur.fetchone() is not None:  # 目标键已存任何态行（含墓碑）→ 不迁，留 pg_only 通道
                    continue
                cur.execute(
                    _SQL_ENTRY_REKEY.format(table=_t("registry_entry", schema)),
                    (yk_new[1], session_id, rid, fk_old, ek_old, ver_old),
                )
                if cur.rowcount != 1:
                    continue  # 并发改写=放弃迁移，走既有 pg_only 呈报
                _record_event(
                    cur,
                    registry_id=rid,
                    family_key=fk_old,
                    entry_key=yk_new[1],
                    action="reconcile_rekey",
                    actor_session=session_id,
                    actor_kind="system",
                    base_version=ver_old,
                    after_version=ver_old,
                    payload_after=yaml_map[yk_new][1],
                    reason=RECONCILE_REASON,
                    detail={"kind": "identity_key_migration", "old_entry_key": ek_old, "same_payload_sha256": sha_old},
                    schema=schema,
                )
                pg_map[yk_new] = pg_map.pop(pg_key)
                report["rekeyed_identity"] += 1
                report["events_written"] += 1

            for key, (sha, payload) in yaml_map.items():
                pg_row = pg_map.get(key)
                if pg_row is None:
                    fk, ek = key
                    # 复活优先（2026-10-03 B3 实弹诊断）：同键墓碑行存在时裸 INSERT 撞
                    # uq_registry_entry——盘面回真场景（截短波后 HEAD 复原）必须复活：
                    # UPDATE status='active'+version+1+事件留痕，不新增第二行
                    cur.execute(
                        _SQL_REACTIVATE_SELECT.format(table=_t("registry_entry", schema)),
                        (rid, fk, ek),
                    )
                    existing = cur.fetchone()
                    if existing is not None:
                        entry_pk, old_version, old_status = existing
                        new_version = int(old_version) + 1
                        cur.execute(
                            _SQL_REACTIVATE_UPDATE.format(table=_t("registry_entry", schema)),
                            (_jsonb(payload), sha, new_version, session_id, entry_pk),
                        )
                        event_id = _record_event(
                            cur,
                            registry_id=rid,
                            family_key=fk,
                            entry_key=ek,
                            action="reconcile_reactivate",
                            actor_session=session_id,
                            actor_kind="system",
                            base_version=int(old_version),
                            after_version=new_version,
                            payload_after=payload,
                            reason=RECONCILE_REASON,
                            detail={"kind": "reactivated_from_tombstone", "prev_status": str(old_status)},
                            schema=schema,
                        )
                        cur.execute(
                            f"UPDATE {_t('registry_entry', schema)} SET last_event_id=%s WHERE entry_pk=%s",  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                            (event_id, entry_pk),
                        )
                        report["backfilled"] += 1
                        report["events_written"] += 1
                        continue
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
