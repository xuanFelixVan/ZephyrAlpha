# [BLUEPRINT] MOD-AUTO-L3-003 | docs/_working/fullflow_campaign/FLOWTHROUGH_ACCEPTANCE_SPEC.md | §1-§4
# [MODULE] scripts.automation.flowthrough_verifier
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.utils.time_utils; zephyr.data.ch_reader（惰性）;
#   zephyr.infrastructure.database_service（惰性）; zephyr.shared.infra.process_pool; PyYAML
# [CONSUMERS] st-fullflow-20260918（总包验收）; docs/_working/fullflow_campaign/verification/;
#   tests/automation/test_flowthrough_verifier.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读测绘——零写业务表/零写 src/零写注册表（产物仅落 docs/_working/fullflow_campaign 与 .runtime/tmp）;
#   环节清单禁写死，一律由 6+ 独立真源现算（宪法 §9.5）;
#   所有实测数字走真源，禁缓存快照当真值，真源龄 >FF_STALE_SOURCE_DAYS 天即报"已过期";
#   三态裁定=建议值，最终裁定权在总包（规范 §2）;
#   ②转化能跑必须真执行，未执行的标 SKIP-需门位，禁假装跑过;
#   ⑥失败会响若仅静态推演必须明说，禁谎称动态注入;
#   --prove-red 不得 mock 本件自身判定路径（#ARCH-327 教训）;
#   探针还原按字节，禁 git checkout
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失→该源记 MISSING 不中断对账; 单表查询失败→记 -1（区分 0 行与查不到）;
#   DB 不可达→六向④降级为"无依赖边证据"并标黄; --prove-red 未报红→抛 RuntimeError
# [TESTS] tests/automation/test_flowthrough_verifier.py
# [A_module] module_id=MOD-AUTO-L3-003 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [PROVISIONAL] 暂编号 MOD-AUTO-L3-003：原申报 MOD-AUTO-L3-002 与 HEAD 已落地的
#   scripts/automation/source_card_drafter.py 撞号（ARCH-034 唯一性），本批改取号；docs/03_modules 解冻后按注册表重编
"""flowthrough_verifier — 全流通验收仪（把"通了没有"变成可机检命题）。

判据真源 = docs/_working/fullflow_campaign/FLOWTHROUGH_ACCEPTANCE_SPEC.md：
  §1 六向台账（①入口有料 ②转化能跑 ③出口有货 ④下游能取 ⑤哨兵在岗 ⑥失败会响）
  §2 自审闸三态（绿/黄/红 + 黄-门位）→ 本件只出**建议**，裁定权在总包
  §3.4 灌水试验的"能红"证明 → --prove-red
  §4.1 环节层面遗漏自检（≥5 独立真源两两差集）→ --crosscheck

用法（仓库根，Python 3.12）：
    python scripts/automation/flowthrough_verifier.py --crosscheck
    python scripts/automation/flowthrough_verifier.py --stage FF-01
    python scripts/automation/flowthrough_verifier.py --all --limit-runs 1
    python scripts/automation/flowthrough_verifier.py --verdict
    python scripts/automation/flowthrough_verifier.py --prove-red --hop-count 12
    python scripts/automation/flowthrough_verifier.py --e2e --trade-date 2026-09-17
    python scripts/automation/flowthrough_verifier.py --orphan-audit --domain D_AI_LAYER

R-024 修复批（verifier2 接力）三件核心变化：
  1) 逐跳断言取代链末端比总数（`FlowthroughHopSpec`/`measure_hop`/`hop_breaks`）——
     每跳按表记 4 数字并各自校验自洽，"藏在第 2 张表的断供"与"表消失(-1)"都不再被吞；
  2) --prove-red 扩到 ≥10 跳逐跳精确指名（A 族单跳注入 + B 族同表多跳断供），
     判据是"指对是哪一跳"（reason=supply_cut_at_read 的集合差），不是"报了红"；
  3) 每份报表必须带论域声明（`universe_declaration`/`universe_guard`，缺块直接抛错）。

落地批（verifier3 接力）：verifier2 的最后一笔编辑 old_string 过长，把
`DOC_MODULES_DIR/SKELETON_MD/SCAN_EXCLUDES/TABLE_LITERAL_RE/SINK_HINT_RE/CONSUMER_HEADER_RE/`
`SKIP_RUN_RE/DATE_COL_RE/SQL_DEPGRAPH_*/SQL_*_CONSUMERS/FlowthroughProbeContext/_sha256`
一并误删（13 个未定义名、8 件测试红）——本批按 commit_queue 死件 blob 原样回填该块，
保留其 ROOR 反查改造。故 ①ROOR 反查=verifier2 所写，②被误删常量块=verifier3 回填。
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc_str  # noqa: E402

# noqa: m11-perm-manual-legitimate  M11豁免: 验收仪=总包/车道按需手动调尺子，非进程内常驻服务，无自动触发语义

OUT_DIR: Final[Path] = REPO_ROOT / "docs" / "_working" / "fullflow_campaign" / "skeleton"
TMP_DIR: Final[Path] = REPO_ROOT / ".runtime" / "tmp" / "ff-verifier"
FF_STALE_SOURCE_DAYS: Final[int] = 7
FF_PROBE_POISON_SUFFIX: Final[str] = "__ff_probe_missing__"
FF_HOP_TABLE_CAP: Final[int] = 12
FF_PROVE_RED_MIN_HOPS: Final[int] = 10
FF_HOP_SEP: Final[str] = "→"
FF_KNOWN_MISSED_PAIRS: Final[tuple[str, ...]] = ("FF-01→FF-07", "FF-12→FF-02")
RESMON_PATH: Final[Path] = REPO_ROOT / ".runtime" / "tmp" / "fullflow" / "resmon.jsonl"
MEM_AVAIL_FLOOR_GB: Final[float] = 12.0
CPU_PCT_CEILING: Final[float] = 85.0

SRC_YAML: Final[dict[str, str]] = {
    "A_arch_model": "architecture_model/index.yaml",
    "D_trading_decision_map": "config/trading_decision_map.yaml",
    "E_data_tasks": "src/zephyr/data/config/tasks.yaml",
    "E_schedule": "src/zephyr/data/config/schedule.yaml",
    "F_data_supply_sentinel": "src/zephyr/data/config/data_supply_sentinel.yaml",
    "G_quality_sentinel_tables": "config/quality_sentinel_tables.yaml",
}
# 治理册一律经 ROOR 反查发现（RULE-REGISTRY：ROOR 是注册表发现的唯一真源；VOCAB-CHAIN 禁硬编码 SSoT 路径）
ROOR_PATH: Final[str] = "docs/registry_of_registries.yaml"
ROOR_REGISTRY_IDS: Final[dict[str, str]] = {
    "B_functional_domain_registry": "REG-FUNC-DOMAIN-001",
    "C_battle_map_domain_policy": "REG-BATTLE-MAP-DOMAIN-POLICY",
}
CATALOG_BASENAMES: Final[dict[str, str]] = {
    "B_functional_domain_registry": "functional_domain_registry.yaml",
    "C_battle_map_domain_policy": "battle_map_domain_policy.yaml",
}
CATALOG_DIR: Final[Path] = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_ROOR_PATHS: dict[str, str] | None = None


def _roor_registry_paths() -> dict[str, str]:
    """一次性把 ROOR 的 registry_id → physical_path 读成索引（真源不在盘=空索引，不猜）。"""
    global _ROOR_PATHS
    if _ROOR_PATHS is not None:
        return _ROOR_PATHS
    index: dict[str, str] = {}
    path = REPO_ROOT / ROOR_PATH
    if path.is_file():
        data = yaml_safe_load(path.read_text(encoding="utf-8")) or {}
        for tier in data.get("tiers", []) or []:
            for reg in (tier or {}).get("registries", []) or []:
                if isinstance(reg, dict) and reg.get("registry_id") and reg.get("physical_path"):
                    index[str(reg["registry_id"])] = str(reg["physical_path"])
    _ROOR_PATHS = index
    return index


def _source_rel_path(tag: str) -> tuple[str, str]:
    """真源相对路径 + 发现方式（ROOR 反查 / 目录拼接 / 字面登记），逐源如实标。"""
    if tag in SRC_YAML:
        return SRC_YAML[tag], "literal(非治理册)"
    rid = ROOR_REGISTRY_IDS.get(tag, "")
    hit = _roor_registry_paths().get(rid, "")
    if hit:
        return hit, f"ROOR:{rid}"
    base = CATALOG_BASENAMES.get(tag, "")
    if not base:
        return "", "unknown"
    rel = f"{CATALOG_DIR.relative_to(REPO_ROOT).as_posix()}/{base}"
    return rel, "catalog_dir_fallback(ROOR 无此册)"


DOC_MODULES_DIR: Final[Path] = REPO_ROOT / "docs" / "03_modules"
SKELETON_MD: Final[Path] = OUT_DIR / "00_stage_skeleton.md"
SCAN_EXCLUDES: Final[tuple[str, ...]] = (".aidrafts", ".worktrees", "__pycache__", "c4_pdf_cache", ".git")
TABLE_LITERAL_RE: Final[re.Pattern[str]] = re.compile(r"\b([a-z]\d_[a-z_]+|zephyr_[a-z_]+)\.([a-z][a-z0-9_]+)\b")
SINK_HINT_RE: Final[re.Pattern[str]] = re.compile(r"(insert|write|save|dump|upsert|to_csv|flush)", re.I)
CONSUMER_HEADER_RE: Final[re.Pattern[str]] = re.compile(r"^#\s*\[CONSUMERS\]\s*(.*)$")
SKIP_RUN_RE: Final[re.Pattern[str]] = re.compile(
    r"(place_order|submit_order|cancel_order|qmt|broker|production|live_trade|hedge|kill_?switch"
    r"|requests\.|urllib|socket\.|ollama|uvicorn|streamlit|duckdb)", re.I)
DATE_COL_RE: Final[re.Pattern[str]] = re.compile(r"\b(trade_date|dt|date|announce_date|as_of_date)\b")

SQL_DEPGRAPH_SIZE = (
    "SELECT (SELECT count(*) FROM nodes) AS nodes, (SELECT count(*) FROM edges) AS edges,"
    " (SELECT count(*) FROM domains) AS domains, (SELECT count(*) FROM dataflow_runs) AS runs,"
    " (SELECT count(*) FROM dataflow_jobs) AS jobs, (SELECT count(*) FROM dataflow_datasets) AS datasets,"
    " (SELECT count(*) FROM battle_map_steps) AS steps, (SELECT max(updated_at) FROM domains) AS sync_at")
SQL_DEPGRAPH_DOMAINS = (
    "SELECT domain_id, domain_name, layer_id, production_nodes, ssot_path FROM domains ORDER BY domain_id")
SQL_STAGE_CONSUMERS = (
    "SELECT DISTINCT src.path AS consumer, dst.path AS callee, e.dep_type AS dep_type"
    " FROM edges e JOIN nodes dst ON dst.node_id = e.to_node_id"
    " JOIN nodes src ON src.node_id = e.from_node_id WHERE dst.path LIKE %s")
SQL_MODULE_CONSUMERS = (
    "SELECT DISTINCT src.path AS consumer FROM edges e"
    " JOIN nodes dst ON dst.node_id = e.to_node_id JOIN nodes src ON src.node_id = e.from_node_id"
    " WHERE dst.path = %s")


@dataclass
class FlowthroughProbeContext:
    """六向实测的运行期口径（参数对象，避免长参数列表）。"""

    limit_tables: int = 6
    limit_runs: int = 2
    run_timeout_s: int = 90
    trade_date: str = ""
    use_db: bool = True
    skip_run_reasons: dict[str, str] = field(default_factory=dict)


# --------------------------------------------------------------------------
# 通用底座：真源加载 / 龄期 / 资源自守
# --------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _load_yaml(tag: str) -> tuple[Any, dict[str, Any]]:
    """按 tag 读真源 YAML，附实测规模与龄期（禁缓存快照当真值）。"""
    rel, found_by = _source_rel_path(tag)
    path = REPO_ROOT / rel if rel else Path("")
    meta: dict[str, Any] = {"source": tag, "path": rel, "found_by": found_by,
                            "exists": path.is_file(), "age_days": None,
                            "sha256": None, "missing": not path.is_file()}
    if not meta["exists"]:
        return None, meta
    raw = path.read_text(encoding="utf-8")
    meta["age_days"] = round((time.time() - path.stat().st_mtime) / 86400.0, 2)
    meta["sha256"] = _sha256(path)
    meta["lines"] = raw.count("\n") + 1
    try:
        return yaml_safe_load(raw), meta
    except Exception as exc:  # noqa: BLE001 — 真源损坏必须显式记录而非静默
        meta["parse_error"] = str(exc)[:200]
        return None, meta


def yaml_safe_load(text: str) -> Any:
    import yaml

    return yaml.safe_load(text)


def _source_age_warning(meta: dict[str, Any]) -> str:
    age = meta.get("age_days")
    if meta.get("missing"):
        return "MISSING(真源不在盘)"
    if age is not None and age > FF_STALE_SOURCE_DAYS:
        return f"STALE(已过期 {age} 天 > {FF_STALE_SOURCE_DAYS})"
    return f"fresh({age}d)"


def resmon_headroom() -> tuple[bool, str]:
    """全仓扫描前的资源自守：读 resmon 末行，内存不足/负载过高即拒绝起扫。"""
    if not RESMON_PATH.is_file():
        return True, "resmon 缺失=不拦（无观测）"
    try:
        lines = [ln for ln in RESMON_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
        import json as _json

        last = _json.loads(lines[-1])
    except Exception as exc:  # noqa: BLE001 — 观测器故障不阻断验收
        return True, f"resmon 解析失败({str(exc)[:60]})=不拦"
    avail = float(last.get("mem_avail_gb") or 0)
    cpu = float(last.get("cpu_pct") or 0)
    if avail < MEM_AVAIL_FLOOR_GB or cpu > CPU_PCT_CEILING:
        return False, f"mem_avail_gb={avail} cpu_pct={cpu} → 暂缓全仓扫描"
    return True, f"mem_avail_gb={avail} cpu_pct={cpu} → 放行"


def _iter_py(paths: list[Path], cap: int = 4000) -> list[Path]:
    out: list[Path] = []
    for base in paths:
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            if any(seg in SCAN_EXCLUDES for seg in p.parts):
                continue
            out.append(p)
            if len(out) >= cap:
                return out
    return out


# --------------------------------------------------------------------------
# 六个（+1 个运行时）独立真源 → 域/环节清单
# --------------------------------------------------------------------------
def derive_source_A() -> tuple[set[str], dict[str, Any]]:
    data, meta = _load_yaml("A_arch_model")
    doms = {d["id"] for d in (data or {}).get("domains", []) if isinstance(d, dict) and d.get("id")}
    meta["count"] = len(doms)
    meta["vocabulary"] = "D_* 域"
    return doms, meta


def derive_source_B() -> tuple[set[str], dict[str, Any]]:
    data, meta = _load_yaml("B_functional_domain_registry")
    entries = (data or {}).get("entries", []) or []
    doms = {e.get("domain") for e in entries if isinstance(e, dict) and e.get("domain")}
    meta["count"] = len(doms)
    meta["entries"] = len(entries)
    meta["vocabulary"] = "D_* 域"
    meta["ssot_paths"] = {e["domain"]: e.get("ssot_path", "") for e in entries if e.get("domain")}
    return doms, meta


def derive_source_C() -> tuple[set[str], dict[str, Any]]:
    data, meta = _load_yaml("C_battle_map_domain_policy")
    stages = (data or {}).get("flow_stage_allowed_domains", {}) or {}
    union: set[str] = set()
    per_stage: dict[str, list[str]] = {}
    for stage, spec in stages.items():
        allowed = list((spec or {}).get("allowed", []) or [])
        per_stage[stage] = allowed
        union |= set(allowed)
    meta["count"] = len(union)
    meta["stages"] = per_stage
    meta["stage_count"] = len(per_stage)
    meta["vocabulary"] = "D_* 域（11 flow_stage allowed 并集）"
    meta["classification"] = (data or {}).get("domain_classification", {}) or {}
    return union, meta


def derive_source_D() -> tuple[set[str], dict[str, Any]]:
    data, meta = _load_yaml("D_trading_decision_map")
    nodes = (data or {}).get("nodes", []) or []
    flows = sorted({n.get("flow", "?") for n in nodes if isinstance(n, dict)})
    layers = sorted({n.get("layer", "?") for n in nodes if isinstance(n, dict)})
    meta["count"] = len(nodes)
    meta["flows"] = flows
    meta["layers"] = layers
    meta["edges"] = len((data or {}).get("edges", []) or [])
    meta["vocabulary"] = "TDM 节点（flow/layer 词汇，与 D_* 异轴）"
    return {str(n.get("node_id")) for n in nodes if isinstance(n, dict)}, meta


def derive_source_E() -> tuple[set[str], dict[str, Any]]:
    tasks, tmeta = _load_yaml("E_data_tasks")
    sched, smeta = _load_yaml("E_schedule")
    tl = (tasks or {}).get("tasks", []) or []
    schedules = (sched or {}).get("schedules", {}) or {}
    tables = {t.get("table") for t in tl if isinstance(t, dict) and t.get("table")}
    meta = {"source": "E_tasks+schedule", "paths": [SRC_YAML["E_data_tasks"], SRC_YAML["E_schedule"]],
            "exists": tmeta.get("exists") and smeta.get("exists"),
            "missing": not (tmeta.get("exists") and smeta.get("exists")),
            "age_days": max([a for a in (tmeta.get("age_days"), smeta.get("age_days")) if a is not None] or [0]),
            "sha256": f"{tmeta.get('sha256')}/{smeta.get('sha256')}",
            "count": len(tl), "tables": sorted(tables), "table_count": len(tables),
            "schedule_count": len(schedules), "schedules": sorted(schedules),
            "no_deps": sum(1 for t in tl if not (t.get("dependencies") or [])),
            "vocabulary": "task_id（运行视角）+ 落点表"}
    meta["objects"] = sorted({str(t.get("task_id")) for t in tl if t.get("task_id")})
    return set(meta["objects"]), meta


def derive_source_F() -> tuple[set[str], dict[str, Any]]:
    dirs = [d for d in DOC_MODULES_DIR.glob("_domain_*") if d.is_dir()]
    md_count = 0
    doms: set[str] = set()
    for d in dirs:
        md_count += len([f for f in d.rglob("*.md")])
        doms.add("D_" + re.sub(r"[^0-9A-Z]+", "_", d.name[len("_domain_"):].upper()).strip("_"))
    empty = sorted(d.name for d in dirs if not list(d.rglob("*.md")))
    meta = {"source": "F_docs_03_modules", "path": "docs/03_modules/_domain_*/",
            "exists": DOC_MODULES_DIR.is_dir(), "missing": not DOC_MODULES_DIR.is_dir(),
            "age_days": None, "count": len(dirs), "md_files": md_count, "empty_dirs": empty,
            "vocabulary": "_domain_* 目录名→D_* 归一"}
    return doms, meta


def _depgraph_rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_depgraph_conn(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute(sql, params or None)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def derive_source_G() -> tuple[set[str], dict[str, Any]]:
    """depgraph 运行时真源（PG）：域表 + 图规模 + 同步龄 + dataflow_runs 行数。"""
    meta: dict[str, Any] = {"source": "G_depgraph_pg", "path": "depgraph PG nodes/edges/domains",
                            "exists": False, "missing": False, "vocabulary": "D_* 域（代码视角）"}
    try:
        rows = _depgraph_rows(SQL_DEPGRAPH_SIZE)[0]
        doms_rows = _depgraph_rows(SQL_DEPGRAPH_DOMAINS)
    except Exception as exc:  # noqa: BLE001 — DB 不可达=记不可测，不假装
        meta["error"] = str(exc)[:200]
        meta["missing"] = True
        return set(), meta
    meta.update({"exists": True, "nodes": rows["nodes"], "edges": rows["edges"],
                 "domains": rows["domains"], "dataflow_runs": rows["runs"],
                 "dataflow_jobs": rows["jobs"], "dataflow_datasets": rows["datasets"],
                 "battle_map_steps": rows["steps"], "count": len(doms_rows),
                 "domain_rows": {d["domain_id"]: d for d in doms_rows},
                 "sync_at": str(rows.get("sync_at")), "sha256": "n/a(实时查询)"})
    sync = str(rows.get("sync_at") or "")
    if len(sync) >= 10:
        try:
            stamp = time.mktime(time.strptime(sync[:10], "%Y-%m-%d"))
            meta["age_days"] = round((time.time() - stamp) / 86400.0, 2)
        except ValueError:
            meta["age_days"] = None
    return {d["domain_id"] for d in doms_rows if d.get("domain_id")}, meta


ALL_SOURCE_DERIVERS: Final[dict[str, Callable[[], tuple[set[str], dict[str, Any]]]]] = {
    "A_arch_model": derive_source_A,
    "B_functional_domain_registry": derive_source_B,
    "C_battle_map_domain_policy": derive_source_C,
    "D_trading_decision_map": derive_source_D,
    "E_data_tasks_and_schedule": derive_source_E,
    "F_docs_03_modules_dirs": derive_source_F,
    "G_depgraph_runtime": derive_source_G,
}
DOMAIN_VOCAB_SOURCES: Final[tuple[str, ...]] = ("A_arch_model", "B_functional_domain_registry",
                                                "C_battle_map_domain_policy", "F_docs_03_modules_dirs",
                                                "G_depgraph_runtime")


def collect_sources(tags: tuple[str, ...] = ()) -> dict[str, tuple[set[str], dict[str, Any]]]:
    want = tags or tuple(ALL_SOURCE_DERIVERS)
    return {t: ALL_SOURCE_DERIVERS[t]() for t in want}


# --------------------------------------------------------------------------
# 环节清单：机械推导 + 与骨架对照（不一致即报差异，不静默采信任何一方）
# --------------------------------------------------------------------------
def derive_stage_model(sources: dict[str, tuple[set[str], dict[str, Any]]]) -> dict[str, Any]:
    """环节清单自动推导：脊柱=C 的 11 flow_stage；余域按 depgraph layer_id/group 机械归口。"""
    policy = sources["C_battle_map_domain_policy"][1].get("stages", {}) or {}
    domain2stage = {d: f"FF-{i + 2:02d}:{s}" for i, (s, allowed) in enumerate(sorted(policy.items()))
                    for d in (allowed or [])}
    gmeta = sources["G_depgraph_runtime"][1]
    union_c = sources["C_battle_map_domain_policy"][0]
    universe = set().union(*[v[0] for v in sources.values() if v[0]]) if sources else set()
    depgraph_universe = sources["G_depgraph_runtime"][0] or sources["A_arch_model"][0]
    residual = sorted(depgraph_universe - union_c)
    cross_stages: dict[str, list[str]] = {}
    for dom in residual:
        bucket = "X_UNCLASSIFIED"
        if dom.startswith(("D_GOV", "D_ARCH", "D_CODE", "D_COMPLIANCE", "D_DATA_SCRIPTS", "D_META",
                           "D_SEC_SCRIPTS", "D_STRUCT", "D_ARCHIVE", "D_TEST", "D_AUDIT", "D_CONTRACTS")):
            bucket = "X_GOV_SUBSTRATE"
        elif dom.startswith(("D_AUTONOMY", "D_ORCHESTRATOR", "D_INFRA_A2A", "D_SECURITY_LLM",
                             "D_INTEGRATION_GATEWAY")):
            bucket = "X_AI_RUNTIME"
        elif dom.startswith(("D_FRONTEND", "D_SHARED", "D_INFRA_TELEMETRY", "D_INFRA_RUNTIME")):
            bucket = "X_DELIVERY"
        cross_stages.setdefault(bucket, []).append(dom)
    return {"spine": sorted(policy), "domain2stage": domain2stage, "cross_stages": cross_stages,
            "residual_domains": residual, "union_policy_domains": sorted(union_c),
            "universe_domains": sorted(universe), "depgraph_domains": sorted(depgraph_universe),
            "depgraph_meta": gmeta}


def parse_skeleton_stages() -> dict[str, dict[str, Any]]:
    """解析骨架 FF-01..FF-16 表（仅作对照，非采信源）。"""
    if not SKELETON_MD.is_file():
        return {}
    text = SKELETON_MD.read_text(encoding="utf-8")
    out: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(FF-\d{2})\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|\s*(\d+)\s*\|", line)
        if not m:
            continue
        out[m.group(1)] = {"name": m.group(2).strip(), "upstream": m.group(3).strip(),
                           "downstream": m.group(4).strip(), "packages": m.group(5).strip(),
                           "nodes": int(m.group(6))}
    return out


def skeleton_vs_derived(model: dict[str, Any], skeleton: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """推导环节 vs 骨架环节的差异清单（双向：骨架有/推导无、推导有/骨架无、域归属不一致）。"""
    diffs: list[dict[str, Any]] = []
    derived_stages = {v for v in model["domain2stage"].values()} | set(model["cross_stages"])
    if skeleton:
        diffs.append({"kind": "stage_count", "derived": len(derived_stages), "skeleton": len(skeleton)})
    mapped: dict[str, set[str]] = {}
    for dom, stage in model["domain2stage"].items():
        mapped.setdefault(stage.split(":", 1)[1], set()).add(dom)
    for bucket, doms in model["cross_stages"].items():
        mapped.setdefault(bucket, set()).update(doms)
    for stage, doms in sorted(mapped.items()):
        if stage.startswith("FF-"):
            continue
        diffs.append({"kind": "cross_bucket", "stage": stage, "domains": sorted(doms)})
    return diffs


# --------------------------------------------------------------------------
# --crosscheck
# --------------------------------------------------------------------------
def pairwise_domain_diffs(sources: dict[str, tuple[set[str], dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    tags = [t for t in DOMAIN_VOCAB_SOURCES if sources.get(t)]
    for i, left in enumerate(tags):
        for right in tags[i + 1:]:
            ls, rs = sources[left][0], sources[right][0]
            if not ls or not rs:
                rows.append({"left": left, "right": right, "direction": "n/a", "count": "n/a",
                             "items": [], "note": "一侧无对象（真源不可用），差集不可判"})
                continue
            rows.append({"left": left, "right": right, "direction": f"仅在 {left}",
                         "count": len(ls - rs), "items": sorted(ls - rs)})
            rows.append({"left": left, "right": right, "direction": f"仅在 {right}",
                         "count": len(rs - ls), "items": sorted(rs - ls)})
    return rows


def unassigned_objects(model: dict[str, Any], sources: dict[str, tuple[set[str], dict[str, Any]]]) -> dict[str, Any]:
    """规范 §4.1 判据：任一真源出现、但未被归入任何环节的对象数。

    异名先按 depgraph domains.ssot_path 机械归一（蓝图目录名≠域 id 是本仓真实存在的词汇差）。
    """
    covered = set(model["domain2stage"]) | {d for ds in model["cross_stages"].values() for d in ds}
    aliases = _alias_index(sources["G_depgraph_runtime"][1].get("domain_rows", {}))
    report: dict[str, Any] = {}
    for tag in DOMAIN_VOCAB_SOURCES:
        objs = sources.get(tag, (set(), {}))[0]
        raw_missing = sorted(objs - covered)
        resolved = {m: _resolve_alias(m, aliases) for m in raw_missing}
        still = sorted(m for m, r in resolved.items() if not r)
        report[tag] = {"objects": len(objs), "raw_unmatched": len(raw_missing),
                       "aliased": {m: r for m, r in resolved.items() if r},
                       "unassigned": len(still), "items": still}
    tasks = sources.get("E_data_tasks_and_schedule", (set(), {}))[1]
    report["E_data_tasks_and_schedule"] = {
        "objects": tasks.get("count", 0), "unassigned": 0,
        "note": (f"task_id={tasks.get('count')} 落点表={tasks.get('table_count')} "
                 f"档期={tasks.get('schedule_count')} 无 dependencies 声明={tasks.get('no_deps')}"
                 f"——全部为 FF-01 内部节拍（异词汇：任务不是域）")}
    tdm = sources.get("D_trading_decision_map", (set(), {}))[1]
    report["D_trading_decision_map"] = {
        "objects": tdm.get("count", 0), "unassigned": 0,
        "note": f"异词汇：{tdm.get('count')} 节点 / {len(tdm.get('flows', []))} 流 / "
                f"{len(tdm.get('layers', []))} layer 码 / {tdm.get('edges')} 边——决策点级颗粒，"
                f"归 FF-06..FF-12 子索引，不上升为环节"}
    return report


def _alias_index(dom_rows: dict[str, Any]) -> dict[str, str]:
    """候选别名 → 规范域 id：域名、ssot_path 末段都算别名（机械，不手维护）。"""
    index: dict[str, str] = {}
    for dom, info in (dom_rows or {}).items():
        leaf = str(info.get("ssot_path", "")).rstrip("/").split("/")[-1]
        for key in {dom, dom[2:] if dom.startswith("D_") else dom, leaf.upper(),
                    re.sub(r"[^0-9A-Z]+", "_", leaf.upper())}:
            index.setdefault(key, dom)
    return index


def _resolve_alias(name: str, aliases: dict[str, str]) -> str:
    """按 token 前缀互含做机械归一（唯一命中才认，多义不猜）。"""
    toks = _tokens(name.replace("D_", ""))
    if not toks:
        return ""
    hits = {canon for key, canon in aliases.items() if _tokens(key) and _tokens(key) <= toks}
    hits |= {canon for key, canon in aliases.items()
             if any(t.startswith(k) or k.startswith(t) for t in toks for k in _tokens(key) if len(k) > 2)}
    return hits.pop() if len(hits) == 1 else ""


def cmd_crosscheck(args: argparse.Namespace) -> dict[str, Any]:
    ok, why = resmon_headroom()
    sources = collect_sources()
    model = derive_stage_model(sources)
    skeleton = parse_skeleton_stages()
    result = {
        "generated_at": now_utc_str(),
        "resmon": {"proceed": ok, "detail": why},
        "sources": {t: {k: v for k, v in meta.items() if k != "ssot_paths"}
                    for t, (_, meta) in sources.items()},
        "source_freshness": {t: _source_age_warning(sources[t][1]) for t in sources},
        "pairwise_diffs": pairwise_domain_diffs(sources),
        "unassigned": unassigned_objects(model, sources),
        "derived_model": {k: model[k] for k in ("spine", "cross_stages", "residual_domains")},
        "skeleton_stages": skeleton,
        "skeleton_vs_derived": skeleton_vs_derived(model, skeleton),
    }
    result["universe"] = universe_declaration(sources, build_stage_catalog(model, sources),
                                              "环节/域词汇的跨真源交叉对账（对象=域与环节，非模块子孙穷举）",
                                              tuple(model["residual_domains"]))
    _write_crosscheck_md(result)
    return result


def _write_crosscheck_md(r: dict[str, Any]) -> None:
    lines = ["---", "ttl: task_bound",
             "completes_when: 全流通战役收官且验收仪 --crosscheck 可重跑复现", "---", "",
             "# 环节层面遗漏自检（验收仪 `--crosscheck` 实测产出，勿手改）", "",
             f"生成时间：{r['generated_at']}（生成件=`scripts/automation/flowthrough_verifier.py`）", "",
                     f"资源自守：{r['resmon']['detail']}", "", "## 1. 真源实测规模与新鲜度", "",
             "| 真源 | 路径 | 实测对象数 | 词汇 | 真源龄 | sha256 |", "|---|---|---|---|---|---|"]
    for tag, meta in r["sources"].items():
        path = meta.get("path") or ",".join(meta.get("paths", []))
        extra = _meta_extra(tag, meta)
        lines.append(f"| {tag} | `{path}` | **{meta.get('count')}** | {meta.get('vocabulary', '')} "
                     f"| {r['source_freshness'][tag]} | `{str(meta.get('sha256'))[:16]}` |")
        if extra:
            lines.append(f"| | ↳ {extra} | | | | |")
    lines += ["", "## 2. 两两差集（域词汇真源，逐条列非零项）", "",
              "| 左真源 | 右真源 | 方向 | 非零项数 | 逐条清单 |", "|---|---|---|---|---|"]
    for row in r["pairwise_diffs"]:
        items = ", ".join(f"`{i}`" for i in row.get("items", [])) or row.get("note", "0")
        lines.append(f"| {row['left']} | {row['right']} | {row['direction']} "
                     f"| **{row['count']}** | {items} |")
    lines += ["", "## 3. 未归入任何环节的对象数（§4.1 判据：应为 0）", "",
              "| 真源 | 对象数 | 字面未匹配 | 异名机械归一 | 归一后仍未归属 | 逐条 / 说明 |",
              "|---|---|---|---|---|---|"]
    for tag, row in r["unassigned"].items():
        alias = "; ".join(f"`{k}`→`{v}`" for k, v in sorted(row.get("aliased", {}).items())) or "—"
        items = ", ".join(f"`{i}`" for i in row.get("items", []))[:1200] or row.get("note", "—")
        lines.append(f"| {tag} | {row['objects']} | {row.get('raw_unmatched', 0)} | {alias[:700]} "
                     f"| **{row['unassigned']}** | {items} |")
    lines += ["", "## 4. 环节清单：推导 vs 骨架对照（不静默采信任何一方）", "",
              f"- 机械推导脊柱（源 C 的 flow_stage）：{len(r['derived_model']['spine'])} 段 "
              f"= {', '.join(r['derived_model']['spine'])}",
              f"- 未被任何 flow_stage 允许的 depgraph 域：**{len(r['derived_model']['residual_domains'])}** "
              f"→ 按域名前缀机械归口为 {len(r['derived_model']['cross_stages'])} 个横切环节",
              f"- 骨架声称环节数：{len(r['skeleton_stages'])}", ""]
    for d in r["skeleton_vs_derived"]:
        lines.append(f"- 差异 `{d['kind']}`：{_diff_row_preview(d)}")
    for bucket, doms in sorted(r["derived_model"]["cross_stages"].items()):
        lines.append(f"- **{bucket}**（{len(doms)} 域）：{', '.join(f'`{x}`' for x in doms)}")
    lines += ["", "## 5. 对骨架『未归属=0』声明的独立复核", "", _crosscheck_verdict_text(r), ""]
    universe = r.get("universe") or {}
    body = lines[:7] + render_universe_lines(universe) + [""] + lines[7:] if universe else lines
    text = "\n".join(body) + "\n"
    universe_guard(text)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "03_omission_crosscheck.md").write_text(text, encoding="utf-8")


def _diff_row_preview(d: dict[str, Any]) -> str:
    return json.dumps(d, ensure_ascii=False, default=str)[:600]


def _meta_extra(tag: str, meta: dict[str, Any]) -> str:
    if "trading_decision_map" in tag:
        return (f"layer 码 {len(meta.get('layers', []))} / 流 {len(meta.get('flows', []))} "
                f"/ 边 {meta.get('edges')}")
    if "battle_map" in tag:
        return f"flow_stage 数 {meta.get('stage_count')}"
    if "tasks" in tag:
        return (f"task {meta.get('count')} / 表 {meta.get('table_count')} / 档期 "
                f"{meta.get('schedule_count')} / 无依赖声明 {meta.get('no_deps')}")
    if "modules" in tag:
        return (f"_domain_ 目录 {meta.get('count')} / .md {meta.get('md_files')} / 空目录 "
                f"{meta.get('empty_dirs')}")
    if "depgraph" in tag:
        return (f"nodes {meta.get('nodes')} / edges {meta.get('edges')} / dataflow_runs "
                f"{meta.get('dataflow_runs')} / jobs {meta.get('dataflow_jobs')} / steps "
                f"{meta.get('battle_map_steps')} / 最后同步 {meta.get('sync_at')}")
    if "functional_domain_registry" in tag:
        return f"entries {meta.get('entries')}"
    return ""


# --------------------------------------------------------------------------
# 环节 → 域 → 代码路径（机械映射，禁写死）
# --------------------------------------------------------------------------
BATTLE_MAP_DIR: Final[Path] = (REPO_ROOT / "docs" / "02_enterprise_architecture"
                               / "07_trading_decision_architecture" / "battle_map")
BATTLE_MAP_FILE_RE: Final[re.Pattern[str]] = re.compile(r"^battle_map_(\d{2})_([a-z_]+)\.md$")


def battle_map_doc_order() -> dict[str, int]:
    """环节编号真源 = battle_map_*.md 文件名数字前缀（不写死，读盘现算）。"""
    order: dict[str, int] = {}
    if not BATTLE_MAP_DIR.is_dir():
        return order
    for p in sorted(BATTLE_MAP_DIR.glob("battle_map_*.md")):
        m = BATTLE_MAP_FILE_RE.match(p.name)
        if m:
            order[m.group(2)] = int(m.group(1))
    return order


def build_stage_catalog(model: dict[str, Any], sources: dict[str, tuple[set[str], dict[str, Any]]]
                        ) -> dict[str, dict[str, Any]]:
    """推导环节清单：FF-01=数据供给（源 E）；FF-(n+1)=battle_map 文档编号；余域按前缀归横切环节。"""
    doc_order = battle_map_doc_order()
    policy = sources["C_battle_map_domain_policy"][1].get("stages", {}) or {}
    dom_meta = sources["G_depgraph_runtime"][1].get("domain_rows", {})
    catalog: dict[str, dict[str, Any]] = {}
    e_meta = sources["E_data_tasks_and_schedule"][1]
    catalog["FF-01"] = {"name": "数据供给链（源 E：tasks+schedule）", "kind": "supply",
                        "domains": _data_domains(dom_meta), "objects": e_meta.get("count", 0)}
    for stage, num in sorted(doc_order.items(), key=lambda kv: kv[1]):
        if stage == "cross_cutting":
            continue
        ff = f"FF-{num + 1:02d}"
        catalog[ff] = {"name": stage, "kind": "pipeline", "stage_key": stage,
                       "domains": sorted(policy.get(stage, []))}
    if "cross_cutting" in doc_order:
        cc = _cross_cutting_mechanisms()
        catalog[f"FF-{doc_order['cross_cutting'] + 1:02d}"] = {
            "name": "横切机制层", "kind": "cross_cutting", "domains": [], "mechanisms": cc}
    nxt = max(int(k[3:]) for k in catalog) + 1
    for bucket, doms in sorted(model["cross_stages"].items()):
        catalog[f"FF-{nxt:02d}"] = {"name": bucket, "kind": "residual", "domains": sorted(doms)}
        nxt += 1
    for ff, spec in catalog.items():
        spec["paths"] = sorted({str((dom_meta.get(d, {}) or {}).get("ssot_path") or "")
                                for d in spec["domains"] if (dom_meta.get(d, {}) or {})})
        spec["code_paths"] = [REPO_ROOT / p for p in spec["paths"] if p]
    return catalog


def _data_domains(dom_meta: dict[str, Any]) -> list[str]:
    return sorted(d for d, info in dom_meta.items()
                  if str(info.get("ssot_path", "")).startswith(("src/zephyr/data", "src/zephyr/market_data",
                                                                "src/zephyr/alt_data", "src/zephyr/data_eng",
                                                                "src/zephyr/data_governance",
                                                                "src/zephyr/data_security",
                                                                "src/zephyr/integration")))


def _cross_cutting_mechanisms() -> list[str]:
    path = BATTLE_MAP_DIR / "battle_map_12_cross_cutting.md"
    if not path.is_file():
        return []
    return sorted(set(re.findall(r"\bCC_\d{2}\b", path.read_text(encoding="utf-8"))))


# --------------------------------------------------------------------------
# 六向实测
# --------------------------------------------------------------------------
SQL_CH_LIVENESS = "SELECT version()"
SQL_CH_DATABASES = "SELECT name FROM system.databases"
SQL_CH_TABLE_NAMES = "SELECT database, name FROM system.tables"
SQL_PARTS_ROWS_TMPL = ("SELECT sum(rows) FROM system.parts WHERE database='%s' AND table='%s'"
                                   " AND active")
TABLE_IDENT_RE: Final[re.Pattern[str]] = re.compile(r"^([a-z]\d*_[a-z0-9_]*)\.([a-z][a-z0-9_]*)$")
FF_ROWS_UNREACHABLE: Final[int] = -1
FF_ROWS_UNMEASURABLE: Final[int] = -2
_CHANNEL_STATE: dict[str, bool] = {}
_ROW_BASIS: dict[str, str] = {}


def ch_channel_alive() -> bool:
    """证据通道探活（区分"表真不存在=断链"与"通道故障=不可测"，防他会话在途代码造假红）。"""
    if "alive" in _CHANNEL_STATE:
        return _CHANNEL_STATE["alive"]
    alive = False
    try:
        from zephyr.data import ch_reader

        alive = bool((ch_reader.query(SQL_CH_LIVENESS, timeout=20) or "").strip())
    except (SyntaxError, ImportError, ModuleNotFoundError) as exc:
        log_line(f"  [通道] ch_reader 不可导入（他会话在途/语法坏件）：{str(exc)[:90]}")
    except Exception as exc:  # noqa: BLE001 — 连不上=通道故障
        log_line(f"  [通道] 探活失败：{str(exc)[:90]}")
    _CHANNEL_STATE["alive"] = alive
    return alive


_DB_CACHE: dict[str, set[str]] = {}
NOT_A_TABLE_SUFFIX: Final[tuple[str, ...]] = (".yaml", ".yml", ".json", ".md", ".csv", ".py", ".txt",
                                              ".html", ".parquet", ".db", ".j2", ".tmpl")


def ch_databases() -> set[str]:
    """实测 ClickHouse 库名集合——表字面量的唯一白名单（防把 s3_x.yaml 当表造成 mass false red）。"""
    if "dbs" in _DB_CACHE:
        return _DB_CACHE["dbs"]
    dbs: set[str] = set()
    if ch_channel_alive():
        try:
            from zephyr.data import ch_reader

            dbs = {ln.strip() for ln in (ch_reader.query(SQL_CH_DATABASES, timeout=20) or "").splitlines()
                   if ln.strip()}
        except Exception as exc:  # noqa: BLE001 — 取不到库名=退回模式判定
            log_line(f"  [通道] 库名清单失败：{str(exc)[:80]}")
    _DB_CACHE["dbs"] = dbs
    return dbs


def is_plausible_table(name: str) -> bool:
    """表名字面量可信度：后缀黑名单 + （通道可用时）库名必须在实测库名集合内。"""
    if name.endswith(NOT_A_TABLE_SUFFIX):
        return False
    db = name.split(".", 1)[0]
    known = ch_databases()
    return (db in known) if known else bool(db)


def _ch_known_tables() -> set[str]:
    """一次查询拿全仓"表存在性"名册——把『表不存在（断链）』与『查询超时（不可测）』分开。

    这是尺子可信度的地基：`ch_reader.query` 对**任何**失败都返回空串，
    旧实现一律记 -1=断链，于是"重表 count 超时"被当成"上游断供"、
    而真正的断供又和噪声混在一起——聚合层里谁也认不出来（R-024 的两处漏检即此）。
    """
    if "tables" in _DB_CACHE:
        return _DB_CACHE["tables"]
    tables: set[str] = set()
    if ch_channel_alive():
        try:
            from zephyr.data import ch_reader

            for line in (ch_reader.query(SQL_CH_TABLE_NAMES, timeout=30) or "").splitlines():
                parts = line.split("\t")
                if len(parts) == 2:
                    tables.add(f"{parts[0]}.{parts[1]}")
        except Exception as exc:  # noqa: BLE001 — 名册取不到=退回逐表判定，不假装
            log_line(f"  [通道] 表名册失败：{str(exc)[:80]}")
    _DB_CACHE["tables"] = tables
    return tables


def _rows_from_parts(table: str) -> int:
    """快口径：system.parts 活跃分区行数合计（元数据查询，秒级，不做 Replacing 去重）。

    仅用于"慢口径 count() FINAL 超时"时区分**有货**与**空表**：
    两口径都满足 ">0  iff 非空"，故逐跳自洽断言成立；量级差在报告里如实标 basis。
    """
    m = TABLE_IDENT_RE.match(table)
    if not m or not ch_channel_alive():
        return FF_ROWS_UNMEASURABLE
    from zephyr.data import ch_reader

    try:
        out = (ch_reader.query(SQL_PARTS_ROWS_TMPL % (m.group(1), m.group(2)), timeout=20) or "").strip()
    except Exception:  # noqa: BLE001 — 元数据也取不到=不可测，禁猜
        return FF_ROWS_UNMEASURABLE
    try:
        return int(out.splitlines()[-1])
    except (ValueError, IndexError):
        return FF_ROWS_UNMEASURABLE


def _row_count(table: str) -> int:
    """①③ 实测行数：走 ch_reader.query（内含 FINAL 注入 + DatabaseService 只读连接）。

    三态严格区分（这是"红/不可测"不互相污染的前提）：
      ≥0 = 实测行数；-1 = 表在 CH 名册里不存在=真断链（判红）；
      -2 = 通道故障或查询不可得=**不可测**（不判红也不判绿，绝不静默按 0 处理）。
    """
    if not ch_channel_alive():
        return FF_ROWS_UNMEASURABLE
    known = _ch_known_tables()
    if known and table not in known:
        _ROW_BASIS[table] = "absent(真断链)"
        return FF_ROWS_UNREACHABLE
    from zephyr.data import ch_reader

    try:
        out = ch_reader.query(f"SELECT count() FROM {table}", timeout=25)  # noqa: bare-sql  表名运行期插值，SQL 集中化不可机械施行（ruff 未选 S 族，原 S608 标记不生效故不并存）
    except Exception as exc:  # noqa: BLE001 — 异常分两类：名册里没有=断链，有=不可测
        log_line(f"  [①③] 查询失败 {table}: {str(exc)[:80]}")
        return FF_ROWS_UNMEASURABLE if (known and table in known) else FF_ROWS_UNREACHABLE
    text = (out or "").strip()
    if not text:
        fast = _rows_from_parts(table)
        _ROW_BASIS[table] = "system_parts(FINAL 计数不可得)" if fast >= 0 else "unmeasurable"
        return fast
    try:
        _ROW_BASIS[table] = "count_FINAL"
        return int(text.splitlines()[-1].strip())
    except ValueError:
        _ROW_BASIS[table] = "unparseable"
        return FF_ROWS_UNMEASURABLE


def _latest_stamp(table: str, date_col: str) -> str:
    try:
        from zephyr.data import ch_reader

        out = ch_reader.query(f"SELECT max(toString({date_col})) FROM {table}", timeout=25)  # noqa: bare-sql  表名/日期列运行期插值，SQL 集中化不可机械施行（ruff 未选 S 族，原 S608 标记不生效故不并存）
    except Exception as exc:  # noqa: BLE001
        log_line(f"  [①] 时间戳查询失败 {table}: {str(exc)[:80]}")
        return ""
    return (out or "").strip().splitlines()[-1].strip() if (out or "").strip() else ""


def log_line(text: str) -> None:
    print(text, flush=True)


def scan_stage_tables(paths: list[Path], cap_files: int = 900) -> dict[str, Any]:
    """代码字面量扫描：本环节声明读/写的落点表（AST 级，非猜）。"""
    sources: set[str] = set()
    sinks: set[str] = set()
    files = _iter_py(paths, cap=cap_files)
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            for m in TABLE_LITERAL_RE.finditer(line):
                full = f"{m.group(1)}.{m.group(2)}"
                if is_plausible_table(full):
                    (sinks if SINK_HINT_RE.search(line) else sources).add(full)
    return {"files_scanned": len(files), "read_tables": sorted(sources), "write_tables": sorted(sinks)}


def _probe_feed_rows(tables: list[str], date_cols: dict[str, str], ctx: FlowthroughProbeContext,
                     row_counter: Callable[[str], int], stage_tolerance_days: int) -> tuple[list[dict[str, Any]], list[str]]:
    """逐表实测行数/最新戳/滞后/新鲜度；返回（实测明细, 限流未测清单）。"""
    rows: list[dict[str, Any]] = []
    unmeasured = [t for t in tables[ctx.limit_tables:]]
    for table in tables[: max(0, ctx.limit_tables)]:
        cnt = row_counter(table)
        col = date_cols.get(table, "")
        stamp = _latest_stamp(table, col) if col and cnt != -1 else ""
        lag = _lag_days(stamp)
        rows.append({"table": table, "rows": cnt, "date_col": col, "latest": stamp,
                     "lag_days": lag,
                     "fresh": bool(lag is not None and lag <= stage_tolerance_days)})
    return rows, unmeasured


def _probe_feed_buckets(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """分桶：measured=实测≥0 / broken=名册无表(-1，真断链) / channel_down=不可测(-2) /
    empty=空表(0) / stale=有戳但超容差。-1 与 0 不混桶、-1 与 -2 不混桶。"""
    measured = [r for r in rows if r["rows"] >= 0]
    return {"measured": measured,
            "broken": [r["table"] for r in rows if r["rows"] == -1],
            "channel_down": [r["table"] for r in rows if r["rows"] == -2],
            "empty": [r["table"] for r in rows if r["rows"] == 0],
            "stale": [r["table"] for r in measured if r["latest"] and not r["fresh"]]}


def _probe_feed_verdict(buckets: dict[str, Any], unmeasured: list[str]) -> str:
    """三态建议裁定（判据与拆分的字面一致，未改语义；裁定权在总包）。"""
    if buckets["broken"] or buckets["empty"]:
        return "红"
    if buckets["measured"] and buckets["stale"]:
        return "黄"
    if buckets["measured"] and all(r["rows"] > 0 for r in buckets["measured"]):
        # 限流截断=还有声明读源没测过：绿最多只能是"未测部分不外推"的黄（禁以偏概全）
        return "黄" if unmeasured else "绿"
    return "不可测"


def _probe_feed_evidence(rows: list[dict[str, Any]], broken: list[str], stale: list[str],
                         unmeasured: list[str]) -> str:
    return (_feed_evidence(rows) + (f" || 断链={broken}" if broken else "")
            + (f" || 过期未落容差={stale}" if stale else "")
            + (f" || 限流未测 {len(unmeasured)} 表（绿不外推）" if unmeasured else ""))


def probe_feed(tables: list[str], date_cols: dict[str, str], ctx: FlowthroughProbeContext,
               row_counter: Callable[[str], int] = _row_count,
               stage_tolerance_days: int = 7) -> dict[str, Any]:
    """①入口有料：逐表实测行数 + 最新时间戳 + 新鲜度（真跑查询，非声明）。"""
    rows, unmeasured = _probe_feed_rows(tables, date_cols, ctx, row_counter, stage_tolerance_days)
    buckets = _probe_feed_buckets(rows)
    return {"verdict": _probe_feed_verdict(buckets, unmeasured), "detail": rows,
            "broken_hop": buckets["broken"], "empty_tables": buckets["empty"],
            "channel_down": buckets["channel_down"], "unmeasured_tables": unmeasured[:30],
            "stale_tables": buckets["stale"], "tolerance_days": stage_tolerance_days,
            "evidence": _probe_feed_evidence(rows, buckets["broken"], buckets["stale"], unmeasured)}


def _lag_days(stamp: str) -> float | None:
    if not stamp:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return round((time.time() - time.mktime(time.strptime(stamp[:19], fmt))) / 86400.0, 1)
        except ValueError:
            continue
    return None


def _feed_evidence(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "无读源表字面量（该环节可能为纯编排/无表输入）"
    parts = [f"{r['table']}={r['rows']}行" + (f"@{r['latest']}({r['lag_days']}d)" if r["latest"] else "")
             for r in rows]
    return "; ".join(parts)


def discover_entries(paths: list[Path], cap: int = 500) -> list[dict[str, Any]]:
    """AST 扫出真跑入口（含 `if __name__ == '__main__'` 且定义了 main）。"""
    found: list[dict[str, Any]] = []
    for p in _iter_py(paths, cap=cap):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, OSError):
            continue
        has_main = any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body)
        guard = any(isinstance(n, ast.If) and _is_name_main(n) for n in tree.body)
        if has_main and guard:
            text = p.read_text(encoding="utf-8", errors="ignore")
            reason = _skip_reason(text)
            found.append({"path": str(p.relative_to(REPO_ROOT)), "needs_gate": bool(reason),
                          "skip_reason": reason})
    return found


def _is_name_main(node: ast.If) -> bool:
    test = node.test
    return "__name__" in ast.dump(test) and "__main__" in ast.dump(test)


def _skip_reason(text: str) -> str:
    m = SKIP_RUN_RE.search(text)
    return f"SKIP-需门位（命中敏感符号 {m.group(1)[:20]}，实跑需外部服务/实盘/写权限）" if m else ""


def _exec_one_run(entry: dict[str, Any], run_timeout_s: int) -> dict[str, Any]:
    """真跑一个入口，记 rc + 耗时（禁假装跑过）。"""
    started = time.monotonic()
    rc, err = _exec_entry(entry["path"], run_timeout_s)
    return {"entry": entry["path"], "rc": rc, "stderr_tail": err,
            "elapsed_s": round(time.monotonic() - started, 2)}


def _annotate_rc2_usage(ran: list[dict[str, Any]]) -> None:
    """rc=2 是 argparse 用法错（缺必填参数）非崩溃——如实注记，不计入硬失败。"""
    for r in ran:
        if r["rc"] == 2:
            r["note"] = "rc=2=argparse 用法错（缺必填参数），非崩溃——需车道补调用口径"


def _runs_verdict(ran: list[dict[str, Any]], blocked_total: int, runnable_total: int) -> str:
    if not ran:
        return "黄-门位" if (blocked_total and not runnable_total) else "不可测"
    if all(r["rc"] == 0 for r in ran):
        return "绿"
    return "红" if [r for r in ran if r["rc"] not in (0, 2)] else "黄"


def _runs_evidence(ran: list[dict[str, Any]], blocked_total: int) -> str:
    return ("; ".join(f"{r['entry']} rc={r['rc']} {r['elapsed_s']}s"
                       + (f" 报错={r['stderr_tail']}" if r.get("stderr_tail") else "") for r in ran)
            or f"无可真跑入口（{blocked_total} 件需门位）")


def probe_runs(entries: list[dict[str, Any]], ctx: FlowthroughProbeContext) -> dict[str, Any]:
    """②转化能跑：真执行生产入口，记 rc + 耗时。未跑的一律标 SKIP-需门位，禁假装跑过。"""
    blocked = [e for e in entries if e["needs_gate"]]
    candidates = [e for e in entries if not e["needs_gate"]][: max(0, ctx.limit_runs)]
    ran = [_exec_one_run(e, ctx.run_timeout_s) for e in candidates]
    _annotate_rc2_usage(ran)
    return {"verdict": _runs_verdict(ran, len(blocked), len(candidates)), "ran": ran,
            "skipped_need_gate": [{"entry": e["path"], "reason": e["skip_reason"]} for e in blocked[:20]],
            "blocked_total": len(blocked), "evidence": _runs_evidence(ran, len(blocked))}


def _exec_entry(rel_path: str, timeout_s: int) -> tuple[int, str]:
    """真跑一次生产入口：返回 (rc, stderr 末行)。超时/崩溃如实记非零 rc。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    import os

    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    try:
        proc = run_subprocess_hidden([sys.executable, str(REPO_ROOT / rel_path)],
                                     capture_output=True, text=True, timeout=timeout_s,
                                     cwd=str(REPO_ROOT), env=env)
        err = _stderr_tail(getattr(proc, "stderr", "") or "")
        return int(getattr(proc, "returncode", -9)), err
    except Exception as exc:  # noqa: BLE001 — 超时/崩溃即红，须如实记录
        log_line(f"  [②] 执行异常 {rel_path}: {str(exc)[:100]}")
        return -9, str(exc)[:160]


def _stderr_tail(stderr: str) -> str:
    lines = [ln.strip() for ln in stderr.splitlines() if ln.strip()]
    return lines[-1][:180] if lines else ""


def probe_lands(sinks: list[str], paths: list[Path], ctx: FlowthroughProbeContext,
                row_counter: Callable[[str], int] = _row_count) -> dict[str, Any]:
    """③出口有货：读盘/读表取实测行数与字节数（只断返回值=没验）。"""
    tables = [{"table": t, "rows": row_counter(t)} for t in sinks[: max(0, ctx.limit_tables)]]
    files = scan_artifact_files(paths)
    good = [t for t in tables if t["rows"] > 0]
    landed_files = [f for f in files if f["bytes"] > 0]
    if good or landed_files:
        verdict = "绿"
    elif tables and all(t["rows"] == 0 for t in tables):
        verdict = "红"
    else:
        verdict = "不可测"
    return {"verdict": verdict, "tables": tables, "files": files[:15],
            "evidence": "; ".join(f"{t['table']}={t['rows']}行" for t in tables)
            + (" | " if tables and files else "")
            + "; ".join(f"{f['path']}={f['bytes']}B/{f['lines']}行" for f in files[:5])
            or "声明 sink 为空（需蓝图/注册表补）"}


ARTIFACT_LITERAL_RE: Final[re.Pattern[str]] = re.compile(
    r"[\"'](data/[A-Za-z0-9_./-]+\.(?:json|csv|parquet|db|duckdb))[\"']")


def scan_artifact_files(paths: list[Path], cap: int = 60) -> list[dict[str, Any]]:
    """读盘实测：代码里声明的落盘产物，真存在就报字节与行数。"""
    found: dict[str, dict[str, Any]] = {}
    for p in _iter_py(paths, cap=400):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for rel in ARTIFACT_LITERAL_RE.findall(text):
            if rel in found or len(found) >= cap:
                continue
            disk = REPO_ROOT / rel
            if disk.is_file():
                raw = disk.read_bytes()
                found[rel] = {"path": rel, "bytes": len(raw), "lines": len(raw.splitlines())}
    return sorted(found.values(), key=lambda d: -d["bytes"])


def probe_consumers(spec: dict[str, Any], ctx: FlowthroughProbeContext) -> dict[str, Any]:
    """④下游能取：depgraph 真实边 + scripts 不算引用 + 动态注册面 + 蓝图声明双向核对（R-013）。"""
    edges = spec.get("_edges", [])
    error = spec.get("_edges_error", "")
    real, scripts_only, tests_only = _bucket_consumers(edges)
    declared = collect_declared_consumers(spec["code_paths"])
    mismatch = crosscheck_declarations(declared, real, _global_consumers if not error else None)
    src_consumers = {a["consumer"] for a in real}
    callees = sorted({e["callee"] for e in edges if e.get("callee") and not e["callee"].endswith(
        "__init__.py")})
    zero_in = [c for c in callees if not any(
        e["callee"] == c and e["consumer"].startswith("src/") for e in edges)]
    dyn = dynamic_registration_hits(zero_in)
    orphan_modules = [m["module"] for m in zero_in_dynamic(zero_in, dyn)][:10]
    suggestions = suggest_consumers(orphan_modules, spec)
    verdict = "绿" if real else ("不可测" if error else ("黄" if dyn else "红"))
    return {"verdict": verdict, "real_consumers": real[:30], "scripts_only": scripts_only[:20],
            "tests_only": tests_only[:20], "consumer_count_src": len(real),
            "src_consumers": sorted(src_consumers)[:20],
            "dynamic_registration": dyn[:10], "declared_vs_actual": mismatch,
            "semantic_suggestions": suggestions, "orphan_modules": orphan_modules,
            "error": error,
            "evidence": f"src 真消费者 {len(real)} / scripts-only {len(scripts_only)} / "
                        f"tests-only {len(tests_only)} / 动态注册面 {len(dyn)}"}


def zero_in_dynamic(zero_in: list[str], dyn: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """零入度且无动态注册证据 = 真孤儿候选（机械事实）。"""
    registered = {d["module"] for d in dyn}
    return [{"module": m} for m in zero_in if m not in registered]


def spec_pairs(spec: dict[str, Any]) -> list[tuple[str, str]]:
    return [(c["consumer"], c["callee"]) for c in spec.get("_edges", [])]


def _bucket_consumers(edges: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[Any], list[Any]]:
    real: list[dict[str, Any]] = []
    scripts_only: list[dict[str, Any]] = []
    tests_only: list[dict[str, Any]] = []
    for row in edges:
        consumer = str(row.get("consumer") or "")
        item = {"consumer": consumer, "callee": str(row.get("callee") or ""),
                "dep_type": str(row.get("dep_type") or "")}
        if consumer.startswith("tests/"):
            tests_only.append(item)
        elif consumer.startswith("scripts/"):
            scripts_only.append(item)
        elif consumer.startswith("src/"):
            real.append(item)
    return real, scripts_only, tests_only


def collect_declared_consumers(paths: list[Path], cap: int = 300) -> list[dict[str, Any]]:
    """读模块头 `# [CONSUMERS]` 声明（蓝图侧证）。"""
    out: list[dict[str, Any]] = []
    for p in _iter_py(paths, cap=cap):
        head = "\n".join(p.read_text(encoding="utf-8", errors="ignore").splitlines()[:40])
        m = CONSUMER_HEADER_RE.search(head)
        if not m:
            continue
        tokens = [t.strip().rstrip(".") for t in re.split(r"[;,]", m.group(1)) if t.strip()]
        out.append({"module": str(p.relative_to(REPO_ROOT)), "declared": tokens})
    return out


def crosscheck_declarations(declared: list[dict[str, Any]], actual: list[dict[str, Any]],
                            lookup: Callable[[str], list[str]] | None = None) -> dict[str, Any]:
    """蓝图声明 vs 实际 import 双向核对——抓"蓝图说谎"与"接错对象"（R-013 机器防线）。"""
    actual_paths = {a["consumer"] for a in actual}
    callee_by_token: dict[str, set[str]] = {}
    for a in actual:
        callee_by_token.setdefault(a["callee"], set()).add(a["consumer"])
    liars: list[dict[str, Any]] = []
    for item in declared:
        pool = actual_paths | set(lookup(item["module"]) if lookup else [])
        dead = [tok for tok in item["declared"]
                if not any(tok.lower().strip("`") in path.lower() for path in pool)]
        if dead and len(item["declared"]) <= 6:
            liars.append({"module": item["module"], "declared_but_no_import": dead[:6],
                          "actual_src_consumers": sorted(pool)[:5]})
    undeclared: list[dict[str, Any]] = []
    declared_mods = {d["module"] for d in declared}
    for callee, consumers in sorted(callee_by_token.items()):
        if callee not in declared_mods:
            continue
        spec = next(d for d in declared if d["module"] == callee)
        undeclared += [{"module": callee, "imported_by_unlisted": c} for c in sorted(consumers)
                       if not any(tok.lower() in c.lower() for tok in spec["declared"])]
    return {"blueprint_lying_candidates": liars[:20], "unlisted_consumers": undeclared[:20],
            "declared_modules_scanned": len(declared), "liar_count": len(liars),
            "note": "声明有、实际不 import=蓝图说谎候选（假闭环防线）；实际 import 但声明未列=登记欠账"}


def _global_consumers(rel_path: str) -> list[str]:
    try:
        return [r["consumer"] for r in _depgraph_rows(SQL_MODULE_CONSUMERS, (rel_path,))
                if str(r.get("consumer", "")).startswith("src/")]
    except Exception:  # noqa: BLE001 — 单件查询失败不阻断双向核对
        return []


def suggest_consumers(orphan_modules: list[str], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """零入度件的**建议**消费方 + 词法匹配度（0~1）。机械事实≠语义裁定：只出建议。"""
    out: list[dict[str, Any]] = []
    pool = sorted({a["consumer"] for a in spec.get("_all_edges", [])})
    for mod in orphan_modules[:6]:
        stem = Path(mod).stem
        toks = _tokens(stem)
        scored = sorted(((len(toks & _tokens(Path(p).stem)) / max(1, len(toks | _tokens(Path(p).stem))),
                          p) for p in pool if p != mod), reverse=True)[:3]
        out.append({"orphan": mod, "candidates": [{"consumer": p, "lexical_match": round(s, 2)}
                                                  for s, p in scored if s > 0],
                    "advisory": "匹配度=词法信号，接给谁须人/总包裁定（R-013）"})
    return out


def _tokens(name: str) -> set[str]:
    return {t for t in re.split(r"[_\-.]", name.lower()) if len(t) > 2}


def dynamic_registration_hits(modules: list[str], cap: int = 40) -> list[dict[str, Any]]:
    """动态注册面（BRK-009）：importlib/注册表发现的模块，静态零入度扫描会假阳性。"""
    index = _registry_token_index()
    hits: list[dict[str, Any]] = []
    for mod in modules[:cap]:
        stem = Path(mod).stem
        where = sorted(index.get(stem, set()))[:4]
        if where:
            hits.append({"module": mod, "registered_in": where,
                         "note": "由注册表动态发现，不计为孤儿"})
    return hits


_REGISTRY_INDEX: dict[str, set[str]] | None = None


def _registry_token_index() -> dict[str, set[str]]:
    """一次性把 catalogs/*.yaml 的词建成倒排索引（动态注册面证据源）。

    排除"全量文件清单型"册子（如 canonical file / module translation 登记每只文件，
    命中它们等于没命中——只承认真正的**动态发现面**：技能/门禁/路由类注册表）。
    """
    global _REGISTRY_INDEX
    if _REGISTRY_INDEX is not None:
        return _REGISTRY_INDEX
    index: dict[str, set[str]] = {}
    for f in sorted(CATALOG_DIR.glob("*.yaml")):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if text.count(".py") > FILE_INDEX_REGISTRY_THRESHOLD:
            continue
        for tok in set(re.findall(r"\b[a-z][a-z0-9_]{5,}\b", text)):
            index.setdefault(tok, set()).add(f.name)
    _REGISTRY_INDEX = index
    return index


FILE_INDEX_REGISTRY_THRESHOLD: Final[int] = 300


def probe_sentinel(tables: list[str], ctx: FlowthroughProbeContext) -> dict[str, Any]:
    """⑤哨兵在岗：两册阈值行 + **allow_empty 白名单=不许判绿**（判黄注"豁免中"）+ 实跑 breach 数。

    规范 §1 第⑤向 + R-023 收口现状：z-failopen 已把 allow_empty 收到 1 件（带
    rationale_zh/reviewed_at/reviewed_by）。白名单里那张表**可以永远 0 行而不告警**，
    所以它出现在任何环节的 ⑤ 向里，该向就只配判黄——判绿=替盲区背书。
    """
    supply, _ = _load_yaml("F_data_supply_sentinel")
    quality, _ = _load_yaml("G_quality_sentinel_tables")
    rows = {r.get("table"): r for r in (supply or {}).get("tables", []) or [] if isinstance(r, dict)}
    qrows = {r.get("table"): r for r in (quality or {}).get("tables", []) or [] if isinstance(r, dict)}
    armed, blind, unwatched = [], [], []
    for t in tables:
        cfg = rows.get(t) or qrows.get(t)
        if not cfg:
            unwatched.append({"table": t, "in_supply_sentinel": False, "in_quality_sentinel": False,
                              "max_lag_days": None, "allow_empty": False,
                              "note": "两册皆无阈值行=该表哨兵盲区"})
            continue
        row = {"table": t, "in_supply_sentinel": t in rows, "in_quality_sentinel": t in qrows,
               "max_lag_days": cfg.get("max_lag_days"), "allow_empty": bool(cfg.get("allow_empty"))}
        if row["allow_empty"]:
            row.update({"豁免中": True, "rationale_zh": str(cfg.get("rationale_zh", ""))[:180],
                        "reviewed_at": cfg.get("reviewed_at"), "reviewed_by": cfg.get("reviewed_by"),
                        "判据": "allow_empty 白名单=该向自动失明，不许判绿"})
            blind.append(row)
        else:
            armed.append(row)
    breaches = run_sentinel_live(sorted({r["table"] for r in armed} | {t for t in tables if t in qrows}))
    verdict, why = sentinel_verdict(tables, armed, blind, unwatched, breaches)
    return {"verdict": verdict, "armed": armed[:20], "allow_empty_blind": blind[:20],
            "unwatched_tables": unwatched[:20], "breach_run": breaches,
            "verdict_reason": why,
            "evidence": f"有阈值行且未豁免 {len(armed)} 表 / allow_empty 白名单 {len(blind)} 表（判黄不判绿）"
                        f" / 两册无行 {len(unwatched)} 表 / breach 实跑={breaches.get('ran')}"
                        f" 违规={breaches.get('breaches')}｜{why}"}


def sentinel_verdict(tables: list[str], armed: list[dict[str, Any]], blind: list[dict[str, Any]],
                     unwatched: list[dict[str, Any]], breaches: dict[str, Any]) -> tuple[str, str]:
    """⑤ 向三态：全裸=红；有豁免/盲区/实跑失败=黄或红；只有真在岗且 breach=0 才绿。"""
    if not tables:
        return "不可测", "该环节无声明落点表，⑤向无从谈起"
    if not armed and not blind:
        return "红", "所有落点表在两只哨兵册里都没有阈值行=完全无监护"
    if breaches.get("failed"):
        return "红", "哨兵实跑报错（跑了但取不到数=不会响的哨兵）"
    if breaches.get("breaches"):
        return "红", f"哨兵实跑检出 {breaches['breaches']} 条 breach"
    if blind and unwatched:
        return "黄", f"{len(blind)} 表在 allow_empty 豁免中 + {len(unwatched)} 表两册无行"
    if blind:
        return "黄", f"{len(blind)} 表带 allow_empty 豁免（白名单=该向对该表自动失明）"
    if unwatched:
        return "黄", f"{len(unwatched)} 表两册无阈值行（未覆盖即不判绿）"
    if not breaches.get("ran"):
        return "黄", f"哨兵未实跑：{breaches.get('reason') or breaches.get('error', '')}"
    return "绿", f"{len(armed)} 表有阈值行、无豁免、实跑 breach=0"


def run_sentinel_live(tables: list[str]) -> dict[str, Any]:
    """实跑哨兵（进程内、零副作用：report_dir=None + notify=False）。"""
    if not tables:
        return {"ran": False, "reason": "该环节无已配阈值表"}
    try:
        from zephyr.data import quality_sentinel as qs

        specs = qs.load_specs(tables=tables)
        res = qs.run_sentinel(specs, output=qs.SentinelOutput(report_dir=None, notify=False))
        findings = res.get("findings") if isinstance(res, dict) else None
        return {"ran": True, "specs": len(specs), "breaches": len(findings or []),
                "failed": bool(isinstance(res, dict) and res.get("errors")),
                "finding_tables": sorted({str(f.get("table")) for f in (findings or [])
                                          if isinstance(f, dict)})[:10],
                "result_keys": sorted(res)[:8] if isinstance(res, dict) else str(type(res))}
    except Exception as exc:  # noqa: BLE001 — 实跑失败必须报，不改判绿
        return {"ran": False, "error": str(exc)[:200]}


FF_SILENT_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    ("silent_except_pass", r"except[^\n:]*:\s*(pass|\.\.\.)\s*$"),
    ("debug_then_proceed", r"logger?\.debug\([^)]*\)[^\n]*\n\s*(?:continue|return True|pass)\b"),
    ("always_true_gate", r"def\s+(?:check|verify|assert|guard)_\w*\([^)]*\)[^\n]*:\s*\n\s*return True\b"),
    ("fail_open_default", r"\.get\(\s*[A-Za-z_'\"][^)]*?,\s*True\s*\)"),
    ("latch_before_deliver", r"(?:set|_set|mark|update)[^\n]*alerted|latch[^\n]*=\s*True"),
)


def probe_failclose(paths: list[Path]) -> dict[str, Any]:
    """⑥失败会响：**本轮只做只读静态推演，禁碰生产写路径**（R-024 明令）。

    扫描五型静默放行：except…pass / debug 后放行 / 恒真判定 / `x.get(k, True)` 兜真 /
    投递前置闩（R-023 z-failopen 的 BRK-066/075 同族）。输出显式标
    `mode=STATIC-推演（非动态注入）`——禁谎称做过动态注入。
    """
    silent: list[str] = []
    by_pattern: dict[str, int] = {}
    alarm_wiring = 0
    files_scanned = 0
    for p in _iter_py(paths, cap=400):
        files_scanned += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"(send_alert|escalat|notify_|alerter|AlertService)", text):
            alarm_wiring += 1
        for name, pat in FF_SILENT_PATTERNS:
            by_pattern[name] = by_pattern.get(name, 0) + len(re.findall(pat, text, re.M))
        try:
            tree = ast.parse(text)
        except (SyntaxError, OSError):
            continue
        hits = _silent_excepts(tree)
        silent += [f"{p.relative_to(REPO_ROOT)}:{ln}" for ln in hits]
    verdict, why = failclose_verdict(silent, by_pattern, alarm_wiring, files_scanned)
    return {"verdict": verdict, "mode": "⑥=静态推演（STATIC，非动态注入；注入须写生产表故按 R-024 降级为只读）",
            "dynamic_injection": False, "silent_except_count": len(silent), "silent_sites": silent[:20],
            "pattern_counts": by_pattern, "alarm_wired_files": alarm_wiring,
            "files_scanned": files_scanned, "verdict_reason": why,
            "evidence": f"AST 静默 except {len(silent)} 处 / 模式命中 {by_pattern} / "
                        f"告警接线文件 {alarm_wiring} 件（扫描面 {files_scanned} 件）｜{why}"}


def failclose_verdict(silent: list[str], by_pattern: dict[str, int], alarm_wiring: int,
                      files_scanned: int) -> tuple[str, str]:
    """⑥ 向三态（静态推演口径）：无静默点且有告警接线才黄绿分界，绿=需要动态注入证据。"""
    total = sum(by_pattern.values())
    if not files_scanned:
        return "不可测", "该环节无代码面可扫描"
    if silent or total > 10:
        return "红", f"检出 {len(silent)} 处 AST 级静默放行 / 五模式合计 {total} 处命中"
    if not alarm_wiring:
        return "红", "无静默点，但全环节零告警接线=失败无人知晓"
    return "黄", "静态推演未见静默放行且有告警接线，但**未做动态注入证据**（§2 禁把黄说成绿）"


def _silent_excepts(tree: ast.AST) -> list[int]:
    """只 catch 不处置的 except 块（pass/仅 log.debug 级）。"""
    out: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        body = node.body
        only_pass = all(isinstance(s, ast.Pass) for s in body)
        only_log = all(isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                       and "log" in ast.dump(s.value.func).lower() for s in body)
        if only_pass or (only_log and not _raises(body)):
            out.append(node.lineno)
    return out


def _raises(body: list[ast.stmt]) -> bool:
    return any(isinstance(s, ast.Raise) for s in body)


def stage_tolerance_days(spec: dict[str, Any], schedule: dict[str, Any]) -> int:
    """新鲜度容差：由该环节声明的档期 cron 机械推导（日频→2、周频→8、月频→32）。"""
    names = set(schedule)
    if not names:
        return 7
    if any(("daily" in n or "intraday" in n or "pre_market" in n) for n in names):
        return 2
    if any("weekend" in n or "weekly" in n for n in names):
        return 8
    return 7


def verify_stage(ff_id: str, catalog: dict[str, Any], ctx: FlowthroughProbeContext,
                 sources: dict[str, tuple[set[str], dict[str, Any]]]) -> dict[str, Any]:
    spec = dict(catalog[ff_id])
    scan = scan_stage_tables(spec["code_paths"])
    e_meta = sources["E_data_tasks_and_schedule"][1]
    date_cols = _date_col_map(sources)
    tables = scan["read_tables"] or scan["write_tables"]
    tol = stage_tolerance_days(spec, set(e_meta.get("schedules", []) or []))
    feed = probe_feed(tables, date_cols, ctx, stage_tolerance_days=tol)
    runs = (probe_runs(discover_entries(spec["code_paths"]), ctx) if ctx.limit_runs else
            {"verdict": "不可测", "ran": [], "skipped_need_gate": [], "blocked_total": 0,
             "evidence": "--limit-runs 0=关闭真跑（仅静态，未证转化）"})
    lands = probe_lands(scan["write_tables"], spec["code_paths"], ctx)
    consumers = probe_consumers(_with_edges(spec, ctx), ctx)
    sentinel = probe_sentinel(sorted(set(scan["read_tables"]) | set(scan["write_tables"])), ctx)
    failclose = probe_failclose(spec["code_paths"])
    record = {"stage_id": ff_id, "name": spec.get("name"), "kind": spec.get("kind"),
              "domains": spec.get("domains"), "paths": spec.get("paths"),
              "files_scanned": scan["files_scanned"], "tolerance_days": tol,
              "mechanisms": spec.get("mechanisms", []),
              "read_tables": scan["read_tables"][:40], "write_tables": scan["write_tables"][:40],
              "sixway": {"①入口有料": feed, "②转化能跑": runs, "③出口有货": lands,
                         "④下游能取": consumers, "⑤哨兵在岗": sentinel, "⑥失败会响": failclose}}
    record["verdict_suggested"] = suggest_verdict(record)
    return record


def _date_col_map(sources: dict[str, tuple[set[str], dict[str, Any]]]) -> dict[str, str]:
    tasks, _ = _load_yaml("E_data_tasks")
    return {t["table"]: t.get("date_col", "") for t in (tasks or {}).get("tasks", []) or []
            if isinstance(t, dict) and t.get("table")}


def _with_edges(spec: dict[str, Any], ctx: FlowthroughProbeContext) -> dict[str, Any]:
    """一次性把该环节的全部边取回来（供④的正反两向与语义建议复用）。"""
    if not ctx.use_db:
        return spec
    edges: list[dict[str, Any]] = []
    try:
        for prefix in spec["paths"]:
            if prefix:
                edges += _depgraph_rows(SQL_STAGE_CONSUMERS, (f"{prefix}%",))
    except Exception as exc:  # noqa: BLE001
        spec["_edges_error"] = str(exc)[:160]
    spec["_edges"] = edges
    spec["_all_edges"] = edges
    return spec


def suggest_verdict(record: dict[str, Any]) -> str:
    """规范 §2 三态建议（裁定权在总包）。"""
    six = record["sixway"]
    core = [six["①入口有料"]["verdict"], six["②转化能跑"]["verdict"],
            six["③出口有货"]["verdict"], six["④下游能取"]["verdict"]]
    if any(v == "红" for v in core):
        return "红"
    if all(v in ("绿", "黄-门位") for v in core):
        aux = [six["⑤哨兵在岗"]["verdict"], six["⑥失败会响"]["verdict"]]
        if all(v == "绿" for v in aux):
            return "绿"
        return "黄-门位" if "黄-门位" in core else "黄"
    return "黄"



def _crosscheck_verdict_text(r: dict[str, Any]) -> str:
    bad = {t: row for t, row in r["unassigned"].items() if row["unassigned"]}
    if not bad:
        return ("**印证**：7 个真源逐源复核，未归属对象数全部为 0（任务/TDM 两个异词汇源按子索引归口）。")
    parts = ["**推翻/补强**：以下真源存在未归属对象，骨架『未归属=0』不成立（或依赖人工裁定兜底）："]
    for tag, row in bad.items():
        parts.append(f"- `{tag}` 未归属 {row['unassigned']} 项：{', '.join(f'`{x}`' for x in row['items'])}")
    parts.append("- 骨架 §5.1 表第 3/4 行已自记 19 域未被 policy 分类、FDR 与 depgraph 互缺，"
                 "本轮实测复现（见 §2 差集行），故骨架的 0 是**人工兜底后的 0**，非机械派生的 0。")
    return "\n".join(parts)


# --------------------------------------------------------------------------
# --stage / --all / --verdict：六向台账落盘（Markdown + 机器可读 YAML 双份）
# --------------------------------------------------------------------------
LEDGER_MD: Final[Path] = OUT_DIR / "04_sixway_ledger.md"
LEDGER_YAML: Final[Path] = OUT_DIR / "04_sixway_machine_ledger.yaml"


def cmd_stage(args: argparse.Namespace) -> list[dict[str, Any]]:
    ctx = FlowthroughProbeContext(limit_tables=args.limit_tables, limit_runs=args.limit_runs,
                                  run_timeout_s=args.timeout, trade_date=args.trade_date,
                                  use_db=not args.no_db)
    ok, why = resmon_headroom()
    if not ok and not args.force:
        log_line(f"[资源自守] {why} —— 加 --force 才继续（全仓扫描会压宿主）")
        return []
    sources = collect_sources()
    model = derive_stage_model(sources)
    catalog = build_stage_catalog(model, sources)
    ids = sorted(catalog) if args.all else [args.stage]
    records = [verify_stage(i, catalog, ctx, sources) for i in ids if i in catalog]
    if args.all:
        records.append(_stage_coverage_diff(catalog, sources, model))
    universe = universe_declaration(sources, catalog,
                                    "本台账所覆盖环节的六向实测（环节集由 7 真源机械推导）",
                                    tuple(model["residual_domains"]))
    _write_ledger(records, sources, catalog, universe)
    return records


def _stage_coverage_diff(catalog: dict[str, Any], sources: dict[str, tuple[set[str], dict[str, Any]]],
                         model: dict[str, Any]) -> dict[str, Any]:
    """环节清单对照：推导 vs 骨架（不静默采信任何一方）。"""
    skeleton = parse_skeleton_stages()
    derived = sorted(catalog)
    only_skel = sorted(set(skeleton) - set(derived))
    only_derived = sorted(set(derived) - set(skeleton))
    return {"stage_id": "COVERAGE-DIFF", "name": "推导环节 vs 骨架环节", "kind": "meta",
            "derived_stages": derived, "skeleton_stages": sorted(skeleton),
            "only_in_skeleton": only_skel, "only_in_derived": only_derived,
            "residual_domains": model["residual_domains"],
            "verdict_suggested": "绿" if not only_skel and not only_derived else "黄"}


def _write_ledger(records: list[dict[str, Any]], sources: dict[str, tuple[set[str], dict[str, Any]]],
                  catalog: dict[str, Any], universe: dict[str, Any] | None = None) -> None:
    import yaml

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    universe = universe or universe_declaration(sources, catalog, "六向台账（未显式传入论域=按台账自身口径）")
    payload = {"generated_at": now_utc_str(),
               "generator": "scripts/automation/flowthrough_verifier.py",
               "universe": universe,
               "source_freshness": {t: _source_age_warning(m) for t, (_, m) in sources.items()},
               "source_sizes": {t: m.get("count") for t, (_, m) in sources.items()},
               "stages": records}
    universe_guard_payload(universe)  # 机读件同受 R-024 论域禁令，口径换成字段级断言
    LEDGER_YAML.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    lines = ["---", "ttl: task_bound", "completes_when: 全流通战役收官且六向台账连续两轮红件=0", "---", "",
             "# 六向台账（验收仪实测产出，勿手改；生成件=`scripts/automation/flowthrough_verifier.py`）", "",
             f"生成时间：{payload['generated_at']} · 裁定权：总包（本表仅出**建议**，规范 §2）", "",
             "真源新鲜度：" + "; ".join(f"{k}={v}" for k, v in payload["source_freshness"].items()), ""]
    lines += render_universe_lines(universe)
    lines += ["", "## 三态建议分布", "", "| 环节 | ① | ② | ③ | ④ | ⑤ | ⑥ | 建议 |",
              "|---|---|---|---|---|---|---|---|"]
    for rec in records:
        six = rec.get("sixway", {})
        cells = [six.get(k, {}).get("verdict", "—") for k in
                 ("①入口有料", "②转化能跑", "③出口有货", "④下游能取", "⑤哨兵在岗", "⑥失败会响")]
        lines.append(f"| {rec['stage_id']} {rec.get('name', '')} | " + " | ".join(cells)
                     + f" | **{rec.get('verdict_suggested')}** |")
    dist: dict[str, int] = {}
    for rec in records:
        dist[rec.get("verdict_suggested", "?")] = dist.get(rec.get("verdict_suggested", "?"), 0) + 1
    lines += ["", "分布：" + ", ".join(f"{k}={v}" for k, v in sorted(dist.items())), "",
              "## 逐环节六向明细", ""]
    for rec in records:
        lines += _render_stage_md(rec)
    text = "\n".join(lines) + "\n"
    universe_guard(text)
    LEDGER_MD.write_text(text, encoding="utf-8")
    shutil_copy(LEDGER_YAML, TMP_DIR / "04_sixway_machine_ledger.yaml")
    log_line(f"[落盘] {LEDGER_MD} / {LEDGER_YAML}")


def shutil_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())


def _render_stage_md(rec: dict[str, Any]) -> list[str]:
    if "derived_stages" in rec:
        return [f"### {rec['stage_id']} {rec['name']}", "",
                f"- 推导环节（{len(rec['derived_stages'])}）：{', '.join(rec['derived_stages'])}",
                f"- 骨架环节（{len(rec['skeleton_stages'])}）：{', '.join(rec['skeleton_stages'])}",
                f"- 仅在骨架：{rec['only_in_skeleton'] or '无'}；仅在推导：{rec['only_in_derived'] or '无'}",
                f"- 未被 flow_stage 机械归口的 depgraph 域：{len(rec['residual_domains'])} 个", ""]
    out = [f"### {rec['stage_id']} {rec.get('name')} · 建议裁定 **{rec.get('verdict_suggested')}**", "",
           f"- 域：{', '.join(f'`{d}`' for d in rec.get('domains', []))}",
           f"- 代码路径：{', '.join(f'`{p}`' for p in rec.get('paths', []))}",
           f"- 扫描文件数（实测）：{rec.get('files_scanned')}", "",
           "| 向 | 判定 | 实测证据 |", "|---|---|---|"]
    for key, block in rec.get("sixway", {}).items():
        out.append(f"| {key} | {block.get('verdict')} | {block.get('evidence', '')[:900]} |")
    four = rec.get("sixway", {}).get("④下游能取", {})
    liars = four.get("declared_vs_actual", {}).get("blueprint_lying_candidates", [])
    if liars:
        out += ["", f"- **蓝图说谎候选（声明的消费方实际不 import，共 "
                    f"{four.get('declared_vs_actual', {}).get('liar_count')} 件）**："]
        out += [f"  - `{l['module']}` 声明但无 import：{', '.join(f'`{t}`' for t in l['declared_but_no_import'][:4])}"
                for l in liars[:8]]
    unlisted = four.get("declared_vs_actual", {}).get("unlisted_consumers", [])
    if unlisted:
        out += ["", f"- 实际引用但蓝图未登记的消费者（欠账 {len(unlisted)} 条，截 8 条）："]
        out += [f"  - `{u['module']}` ← `{u['imported_by_unlisted']}`" for u in unlisted[:8]]
    sugg = four.get("semantic_suggestions", [])
    if sugg:
        out += ["", "- 零入度件与建议消费方（**仅建议**，语义裁定归人/总包，R-013）："]
        for s in sugg[:5]:
            cands = ", ".join(f"`{c['consumer']}`({c['lexical_match']})" for c in s["candidates"]) or "无词法候选"
            out.append(f"  - 孤儿候选 `{s['orphan']}` → {cands}")
    dyn = four.get("dynamic_registration", [])
    if dyn:
        out += ["", f"- 动态注册面（BRK-009，不判孤儿）{len(dyn)} 件："
                    + "; ".join(f"`{Path(d['module']).name}`∈{d['registered_in'][:2]}" for d in dyn[:6])]
    return out + [""]


def cmd_verdict(args: argparse.Namespace) -> dict[str, Any]:
    """--verdict：读最近一次台账，出三态建议汇总（最终裁定权在总包）。"""
    if not LEDGER_YAML.is_file():
        log_line("[verdict] 台账不存在，先跑 --all")
        return {}
    data = yaml_safe_load(LEDGER_YAML.read_text(encoding="utf-8"))
    rows = []
    for rec in data.get("stages", []):
        six = rec.get("sixway", {})
        rows.append({"stage": rec.get("stage_id"), "name": rec.get("name"),
                     "suggested": rec.get("verdict_suggested"),
                     "red_directions": [k for k, b in six.items() if b.get("verdict") == "红"],
                     "yellow_directions": [k for k, b in six.items() if b.get("verdict") != "绿"
                                           and k in ("⑤哨兵在岗", "⑥失败会响")]})
    dist: dict[str, int] = {}
    for r in rows:
        dist[r["suggested"]] = dist.get(r["suggested"], 0) + 1
    log_line("[verdict] 三态建议分布：" + ", ".join(f"{k}={v}" for k, v in sorted(dist.items())))
    for r in rows:
        log_line(f"  {r['stage']} {str(r['name'])[:28]:30s} 建议={r['suggested']} "
                 f"红向={r['red_directions'] or '—'} 待补向={r['yellow_directions'] or '—'}")
    log_line("[verdict] 提示：本表是**建议**，裁定权在总包；永不说\"全绿\"（裁定#325）")
    return {"distribution": dist, "rows": rows}


# --------------------------------------------------------------------------
# --prove-red：尺子必须能红（规范 §3.4；禁 mock 自身判定路径）
# --------------------------------------------------------------------------
def _poisoned_table(real: str) -> str:
    return real + FF_PROBE_POISON_SUFFIX


def prove_red_chain_hop(tables: list[str], ctx: FlowthroughProbeContext,
                        broken_index: int = 0) -> dict[str, Any]:
    """断掉主链一跳（把某上游表指向不存在的表），走**同一条判定路径**重跑。"""
    poison = _poisoned_table(tables[broken_index])
    mutated = list(tables)
    mutated[broken_index] = poison
    date_cols = _date_col_map({})
    hit = probe_feed(mutated, date_cols, ctx)
    return {"injected_hop": tables[broken_index], "poisoned_to": poison, "verdict": hit["verdict"],
            "named_broken_hop": hit.get("broken_hop", []), "detail": hit["detail"]}


def prove_red_tasks_source(tag: str, ctx: FlowthroughProbeContext) -> dict[str, Any]:
    """断掉真源一跳：tasks.yaml **按字节**复制到临时件并改错一张表名，重跑判据。

    生产文件零触碰；前后 sha256 一致即证还原。
    """
    rel = SRC_YAML["E_data_tasks"]
    original = (REPO_ROOT / rel).read_bytes()
    base_sha = _sha256_of(original)
    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError:
        return {"error": "tasks.yaml 非 UTF-8，探针不可注入"}
    names = re.findall(r"^\s*table:\s*([a-z0-9_]+\.[a-z0-9_]+)\s*$", text, re.M)
    if not names:
        return {"error": "未从 tasks.yaml 取到表名，探针无法注入"}
    victim = names[0]
    dirty = text.replace(f"table: {victim}", f"table: {_poisoned_table(victim)}", 1)
    probe = TMP_DIR / "probe_tasks.yaml"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_bytes(dirty.encode("utf-8"))
    tables = re.findall(r"^\s*table:\s*([a-z0-9_]+\.[a-z0-9_]+)\s*$",
                        probe.read_text(encoding="utf-8"), re.M)
    hit = probe_feed(tables[:1], _date_col_map({}), ctx)
    after_sha = _sha256_of((REPO_ROOT / rel).read_bytes())
    return {"victim_table": victim, "poisoned_to": tables[0], "probe_copy": str(probe),
            "verdict": hit["verdict"], "named_broken_hop": hit.get("broken_hop", []),
            "production_untouched": base_sha == after_sha, "sha256": base_sha}


def _sha256_of(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()[:16]


def cmd_prove_red(args: argparse.Namespace) -> dict[str, Any]:
    """尺子可信度根：三条独立红证——A 逐跳注入（≥10 跳，逐跳精确指名）+
    B 全链同表断供（按跳集合精确归因，禁误指）+ C 真源字节探针。

    规范 §3.4 + 总包裁定 R-024：漏检 1/3 或把断点指错地方的尺子不得签发"全流通"。
    """
    ctx = FlowthroughProbeContext(limit_tables=4, limit_runs=0, use_db=not args.no_db)
    real = _clean_control_tables(ctx)
    if len(real) < 2:
        raise RuntimeError("真源里取不到 ≥2 张确有货的上游表，prove-red 无对照=工具不可信")
    chain = prove_red_chain_hop(real, ctx, broken_index=args.hop)
    control = probe_feed(real[:2], _date_col_map({}), ctx)
    src_probe = prove_red_tasks_source("E_data_tasks", ctx)
    hopset = prove_red_hop_injections(args.hop_count)
    control_ok = control["verdict"] in ("绿", "黄")
    red_ok = (control_ok and chain["verdict"] == "红" and chain["named_broken_hop"]
              and src_probe["verdict"] == "红" and src_probe.get("named_broken_hop")
              and src_probe.get("production_untouched") and hopset["pass"])
    if not control_ok:
        log_line("[prove-red] 对照未通过（证据通道故障或未注入即已红）→ 红证无意义，判 FAIL")
    result = {"generated_at": now_utc_str(), "control_verdict": control["verdict"],
              "chain_hop_break": chain, "hop_injections": hopset, "source_byte_break": src_probe,
              "assertion": (f"PASS=注入 {hopset['injected']}/{hopset['attempted']} 跳全部逐跳精确指名"
                            f"且无误指" if red_ok else "FAIL=尺子不会红或指错地方，本件判红"),
              "mock_free": "未 patch 本件任何判定函数：红路由真实 ClickHouse 查询失败/0 行产生"}
    if not red_ok:
        raise RuntimeError(f"prove-red 失败：{json.dumps(result, ensure_ascii=False, default=str)[:900]}")
    log_line(f"[prove-red] {result['assertion']} | 对照(未注入)={control['verdict']} "
             f"| 注入链跳→{chain['verdict']} 指名={chain['named_broken_hop']} "
             f"| 逐跳注入 {hopset['injected']}/{hopset['attempted']} 精确指名+无误指"
             f"| 注入真源→{src_probe['verdict']} 指名={src_probe.get('named_broken_hop')} "
             f"| 生产文件未触碰={src_probe.get('production_untouched')}")
    _dump_json("prove_red_result.json", result)
    return result


def prove_red_hop_injections(want: int = 12) -> dict[str, Any]:
    """A 族=一跳一跳地断供（每跳都必须**只**报出它自己）；B 族=一张表全局断供（报出所有用它交接的跳）。

    判据不是"报了红"，而是 **指对是哪一跳**：
      · 漏检 = 注入后该跳不在新增红跳集合里；
      · 误导归因 = 新增红跳集合里出现了未注入的跳（R-024 点名 FF-12→FF-02 的病）。
    """
    counter = _memo_counter(_row_count)
    hops, baseline = _hop_universe_for_probe(counter)
    pre_cuts = cut_hops([b for bs in baseline.values() for b in bs])
    injectable, victims = _injectable_hops(hops, counter)
    # 基线里已因"读侧断供"而红的跳不能当注入靶：往已经塌的地方再挖一锹证明不了尺子能看见
    eligible = [h for h in injectable if h.hop_id not in pre_cuts]
    # 已知漏检的两条排在最前——保证它们必进本轮注入集（R-024 复测要求）
    eligible.sort(key=lambda h: (h.hop_id not in FF_KNOWN_MISSED_PAIRS, h.hop_id))
    need = max(FF_PROVE_RED_MIN_HOPS, want)
    if len(eligible) < need:
        log_line(f"[prove-red] 合格注入靶仅 {len(eligible)} 条（需求 {need}，"
                 f"基线断供跳 {len(pre_cuts)} 条已如实排除）——不足即判 FAIL，禁降级断言凑数")
    results = [_inject_one_hop(h, hops, pre_cuts, counter, victims) for h in eligible[:need]]
    for r in results:
        log_line(f"[prove-red/A] {r['hop_id']} 注入断供={r.get('victim_table', '—')} "
                 f"→ {r.get('verdict_after', r.get('skipped'))} "
                 f"| 新增断供跳={r.get('newly_cut_hops')} | 误指={r.get('misattributed_to') or '无'}")
    a_pass = all(r["named_exact"] for r in results) and len(results) >= FF_PROVE_RED_MIN_HOPS
    b = _inject_global_supply_cut(hops, {k: v for k, v in victims.items() if k not in pre_cuts},
                                  counter, pre_cuts)
    for run in b.get("runs", []):
        log_line(f"[prove-red/B] 断供 {run['victim_table']}（供 {run['user_hops']} 跳）"
                 f"→ 应指 {len(run['expected_hops'])} 跳 / 实指 {len(run['named_hops'])} 跳 "
                 f"| 漏={run['missed'] or '无'} 误指={run['wrongly_named'] or '无'}")
    known = _mandated_pair_check(results, hops, baseline)
    return {"pass": bool(a_pass and b["pass"] and known["pass"]), "attempted": len(results),
            "injected": sum(1 for r in results if r["named_exact"]),
            "min_required": FF_PROVE_RED_MIN_HOPS, "family_A_per_hop": results,
            "family_B_global_table_cut": b, "known_missed_pairs": known,
            "all_broken_hops_baseline": sorted({k for k, v in baseline.items() if v}),
            "baseline_supply_cuts_excluded_as_targets": sorted(pre_cuts),
            "baseline_note": "基线=未注入时已存在的真断点（非本轮造假），注入判据看的是**新增**红跳集合"}


def _mandated_pair_check(results: list[dict[str, Any]], hops: list[FlowthroughHopSpec],
                         baseline: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """R-024 点名的两条漏检跳必须**分别**过关——这是"修好了"的最低证据。

    两种过关形态，按该跳是否可注入分：
      · 可注入 → 注入后必须精确指名该跳（治"FF-01→FF-07 完全没报"）；
      · 上游落点表本就不存在（FF-12 唯一产物表在 CH 无名册）→ 无法再"断"第二次，
        改为断言**基线红就记在该跳头上且原因指向它自己的交接表**（治"FF-12→FF-02 报成别的断点"）。
    两种都是"指对"，不是"报了红"。
    """
    by_hop = {r["hop_id"]: r for r in results}
    spec = {h.hop_id: h for h in hops}
    rows = []
    for pair in FF_KNOWN_MISSED_PAIRS:
        got = by_hop.get(pair)
        if got:
            rows.append({"pair": pair, "mode": "动态注入读侧断供", "pass": bool(got["named_exact"]),
                         "detail": got.get("evidence") or got.get("skipped", "")})
            continue
        own = [b for b in baseline.get(pair, [])
               if b["reason"] in ("upstream_table_absent", "upstream_landed_zero")
               and b["table"] in (spec[pair].handoff if pair in spec else ())]
        rows.append({"pair": pair, "mode": "基线归因核验（该跳上游落点本就不可用，不可再注入）",
                     "pass": bool(own), "own_breaks": own[:4],
                     "detail": (f"该跳交接表 {len(spec.get(pair).handoff) if pair in spec else 0} 张，"
                                f"其中 {own[0]['table']} 实测={own[0]['rows']}→已按本跳记账"
                                if own else "该跳无任何归属自己的断点=归因缺失")})
    return {"pass": all(r["pass"] for r in rows), "pairs": rows,
            "note": "R-024 记录的 2/6 漏检跳（FF-01→FF-07 完全未报 / FF-12→FF-02 误归因）"}


def _hop_universe_for_probe(counter: Callable[[str], int] | None = None
                            ) -> tuple[list[FlowthroughHopSpec], dict[str, list[dict[str, Any]]]]:
    """跑一遍真实逐跳断言，拿 (跳清单, 每跳基线断点)。基线非空不影响注入判据（按增量算）。

    counter 由调用方注入且**全run共用一个**：同一张表在一次实测里只查一次仓，
    否则"注入前后各查一次"会因 CH 负载抖动而得到不同行数——那是假误指/假漏检的温床。
    """
    sources = collect_sources()
    model = derive_stage_model(sources)
    catalog = build_stage_catalog(model, sources)
    order = sorted(k for k, v in catalog.items() if v.get("kind") in ("supply", "pipeline"))
    scans = {k: scan_stage_tables(catalog[k]["code_paths"]) for k in order}
    hops = enumerate_hops(catalog, scans, parse_skeleton_stages())
    evid = [measure_hop(h, counter or _memo_counter(_row_count)) for h in hops]
    base = {e["hop_id"]: e["breaks"] for e in evid}
    return hops, base


def _hop_injectable(hop: FlowthroughHopSpec,
                    counter: Callable[[str], int] = _row_count) -> list[str]:
    """可注入的交接表 = 该跳里"上游确有货"的表（断一张本就空/不可达的表证明不了任何事）。"""
    return [t for t in hop.handoff if counter(t) > 0]


def _injectable_hops(hops: list[FlowthroughHopSpec], counter: Callable[[str], int]
                     ) -> tuple[list[FlowthroughHopSpec], dict[str, list[str]]]:
    """一次实测得到"可注入跳清单 + 每跳有货交接表"（供 A/B 两族共用，避免重复打仓）。"""
    injectable: list[FlowthroughHopSpec] = []
    victims: dict[str, list[str]] = {}
    for hop in hops:
        got = _hop_injectable(hop, counter)
        if got:
            injectable.append(hop)
            victims[hop.hop_id] = got
    return injectable, victims


def cut_hops(breaks: list[dict[str, Any]]) -> set[str]:
    """报出"读侧断供"这一**指定原因**的跳集合（按原因取，不按"该跳有没有红"取）。

    这是"指对"与"报了红"的分离：一跳可能因别的真断点早就红了，
    只有 reason=supply_cut_at_read 才对应本轮注入，误指/漏检都按这一集合判。
    """
    return {b["hop_id"] for b in breaks if b.get("reason") == "supply_cut_at_read"}


def _inject_one_hop(hop: FlowthroughHopSpec, all_hops: list[FlowthroughHopSpec],
                    pre_cuts: set[str], counter: Callable[[str], int],
                    victims: dict[str, list[str]]) -> dict[str, Any]:
    """在该跳的读侧注入断供，重跑**全链**逐跳断言，判"新增断供跳集合是否恰好=这一跳"。

    判据按**增量**算且只看注入对应的原因：基线里其它真断点不参与归因判定。
    """
    avail = victims.get(hop.hop_id) or []
    if not avail:
        return {"hop_id": hop.hop_id, "skipped": "无有货交接表可注入", "named_exact": False,
                "verdict_after": "跳过"}
    table = avail[0]
    poison = {f"{hop.hop_id}|{table}": _poisoned_table(table)}
    after = evaluate_hops(all_hops, counter, read_poison=poison)
    newly = sorted(cut_hops(after["broken_detail"]) - pre_cuts)
    hit = [b for b in after["broken_detail"]
           if b.get("reason") == "supply_cut_at_read" and b["hop_id"] == hop.hop_id]
    return {"hop_id": hop.hop_id, "kind": hop.kind, "victim_table": table,
            "poisoned_to": _poisoned_table(table),
            "verdict_after": "精确指名" if newly == [hop.hop_id] else
                             ("漏检（未报出该跳）" if hop.hop_id not in newly else "误导归因"),
            "named_this_hop": hop.hop_id in newly, "named_exact": newly == [hop.hop_id],
            "newly_cut_hops": newly,
            "missed": [] if hop.hop_id in newly else [hop.hop_id],
            "misattributed_to": sorted(set(newly) - {hop.hop_id}),
            "evidence": f"{hop.hop_id} supply_cut_at_read 表={hit[0]['table']}"
                        f" 读到={hit[0]['rows']}" if hit else f"{hop.hop_id} 注入后无断供断点=漏检"}


def _inject_global_supply_cut(hops: list[FlowthroughHopSpec], victims: dict[str, list[str]],
                              counter: Callable[[str], int], pre_cuts: set[str]) -> dict[str, Any]:
    """B 族：一张表被多跳共用时断供，期望**所有**用它的跳报红、**其余**跳不得新增红。

    这是聚合层漏检的照妖镜：只在链末端比总数必然看不见（旧版 FF-01→FF-07 就是这么丢的）。
    """
    users: dict[str, list[str]] = {}
    for hop_id, tables in victims.items():
        for t in tables:
            users.setdefault(t, []).append(hop_id)
    shared = sorted(((len(v), t) for t, v in users.items() if len(v) >= 2), reverse=True)[:3]
    if not shared:
        return {"pass": False, "reason": "取不到被 ≥2 跳共用的有货交接表=B 族不可测（不判绿）"}
    runs = []
    for _, table in shared:
        expect = sorted(users[table])
        poison = {f"{hop_id}|{table}": _poisoned_table(table) for hop_id in expect}
        after = evaluate_hops(hops, counter, read_poison=poison)
        newly = cut_hops(after["broken_detail"]) - pre_cuts
        runs.append({"victim_table": table, "poisoned_to": _poisoned_table(table),
                     "user_hops": len(expect), "expected_hops": expect, "named_hops": sorted(newly),
                     "missed": sorted(set(expect) - newly), "wrongly_named": sorted(newly - set(expect)),
                     "pass": newly == set(expect)})
    return {"pass": all(r["pass"] for r in runs), "runs": runs,
            "note": "同一张表供多跳：逐跳断言必须把每一跳都点名，且不得点到没用它跳"}


def _dump_json(name: str, payload: dict[str, Any]) -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    (TMP_DIR / name).write_text(json.dumps(payload, ensure_ascii=False, indent=1, default=str),
                                encoding="utf-8")


def _clean_control_tables(ctx: FlowthroughProbeContext, candidates: int = 14) -> list[str]:
    """挑"确有货"的上游表做对照组：对照组不干净（未注入即红）则红证无意义，直接 FAIL。"""
    good: list[str] = []
    for table in _supply_tables()[:candidates]:
        if _row_count(table) > 0:
            good.append(table)
        if len(good) == ctx.limit_tables:
            break
    return good


def _supply_tables() -> list[str]:
    tasks, _ = _load_yaml("E_data_tasks")
    return sorted({t.get("table") for t in (tasks or {}).get("tasks", []) or [] if t.get("table")})


# --------------------------------------------------------------------------
# --e2e：主链灌水（规范 §3.1）
# --------------------------------------------------------------------------
def _e2e_hop(src: str, dst: str, scans: dict[str, Any], ctx: FlowthroughProbeContext) -> dict[str, Any]:
    """一跳四数字（薄封装，走 hop_measure_tables 的逐表口径——禁"取首表代表全跳"）。

    R-024 教训：旧实现每跳只测 `read_tables[:1]` / `write_tables[:1]`，
    于是"本环节读取"填的是**别的上游**的表（实测 FF-01→FF-02、FF-02→FF-03、FF-03→FF-04
    三跳的读取格都是同一张 c0_meta.fetch_perf）→ 单跳断供被掩盖、红被记到不相邻的跳上。
    现每跳逐表实测，四数字按表记账。
    """
    hop = FlowthroughHopSpec(
        src=src, dst=dst, handoff=hop_handoff_tables(src, dst, scans),
        produced=tuple(sorted(scans[dst]["write_tables"])[:FF_HOP_TABLE_CAP]))
    ev = measure_hop(hop, _memo_counter(_row_count), cap=ctx.limit_tables or FF_HOP_TABLE_CAP)
    rows_up = {t: ev["upstream_landed"][t]["rows"] for t in ev["upstream_landed"]}
    rows_prod = {t: ev["this_stage_produced"][t]["rows"] for t in ev["this_stage_produced"]}
    return {"from": src, "to": dst, "shared_tables": list(hop.handoff),
            "upstream_landed": rows_up,
            "this_stage_read": {t: v["rows"] for t, v in ev["this_stage_read"].items()},
            "this_stage_produced": rows_prod,
            "downstream_readable": len(ev["downstream_readable"]),
            "break": bool(ev["breaks"]), "breaks": ev["breaks"],
            "unmeasured": ev["unmeasured"],
            "note": ev["note"]}


# --------------------------------------------------------------------------
# 逐跳断言（R-024 治本核心）：一跳一对象，四数字按表各自校验自洽
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FlowthroughHopSpec:
    """一跳的**声明面**（谁交给谁、交接哪些表）——不含实测数字，实测在 measure_hop。"""

    src: str
    dst: str
    kind: str = "declared"
    handoff: tuple[str, ...] = ()
    produced: tuple[str, ...] = ()

    @property
    def hop_id(self) -> str:
        return f"{self.src}{FF_HOP_SEP}{self.dst}"


def declared_stage_edges(catalog: dict[str, Any], skeleton: dict[str, dict[str, Any]]
                         ) -> list[tuple[str, str]]:
    """声明边 = 骨架 upstream/downstream 列 ∪ 链上相邻。机械取，禁写死跳清单。"""
    edges: list[tuple[str, str]] = []
    order = sorted(k for k, v in catalog.items() if v.get("kind") in ("supply", "pipeline"))
    for i in range(len(order) - 1):
        edges.append((order[i], order[i + 1]))
    for dst, info in sorted(skeleton.items()):
        for src in re.findall(r"FF-\d{2}", str(info.get("upstream", ""))):
            edges.append((src, dst))
        for nxt in re.findall(r"FF-\d{2}", str(info.get("downstream", ""))):
            edges.append((dst, nxt))
    return sorted({e for e in edges if e[0] in catalog and e[1] in catalog and e[0] != e[1]})


def enumerate_hops(catalog: dict[str, Any], scans: dict[str, Any],
                   skeleton: dict[str, dict[str, Any]]) -> list[FlowthroughHopSpec]:
    """一跳一跳地列出待断言对象：声明边 + 其二阶传递边（FF-01→FF-07 型远端跳）。"""
    hops: list[FlowthroughHopSpec] = []
    seen: set[str] = set()
    primary = declared_stage_edges(catalog, skeleton)

    def _spec(src: str, dst: str, kind: str) -> FlowthroughHopSpec | None:
        if src not in scans or dst not in scans or src == dst:
            return None
        hop = FlowthroughHopSpec(src=src, dst=dst, kind=kind,
                                 handoff=hop_handoff_tables(src, dst, scans),
                                 produced=tuple(sorted(scans[dst]["write_tables"])[:FF_HOP_TABLE_CAP]))
        if hop.hop_id in seen:
            return None
        seen.add(hop.hop_id)
        return hop

    for src, dst in primary:
        hop = _spec(src, dst, "declared")
        if hop:
            hops.append(hop)
    first_step: dict[str, list[str]] = {}
    for src, dst in primary:
        first_step.setdefault(src, []).append(dst)
    for src, mids in sorted(first_step.items()):
        for mid in mids:
            for far in sorted(first_step.get(mid, [])):
                hop = _spec(src, far, "transitive")
                if hop:
                    hops.append(hop)
    return hops


def hop_handoff_tables(src: str, dst: str, scans: dict[str, Any]) -> tuple[str, ...]:
    """交接面 = 上游声明落点 ∩ 本环节声明读取；交集为空时退回上游全部落点（供"只写不读"判定）。"""
    up = set(scans[src]["write_tables"])
    down = set(scans[dst]["read_tables"])
    shared = sorted(up & down)
    return tuple((shared or sorted(up))[:FF_HOP_TABLE_CAP])


def _memo_counter(base: Callable[[str], int]) -> Callable[[str], int]:
    """同一次实测内按表名记忆行数（一次真查询=一个瞬间的真值，禁跨进程当缓存）。"""
    memo: dict[str, int] = {}

    def counter(table: str) -> int:
        if table not in memo:
            memo[table] = base(table)
        return memo[table]

    return counter


def measure_hop(hop: FlowthroughHopSpec, row_counter: Callable[[str], int], cap: int = FF_HOP_TABLE_CAP,
                read_poison: dict[str, str] | None = None) -> dict[str, Any]:
    """一跳四数字**逐表**实测 + 逐表自洽校验（这就是"不聚合"的那把尺）。

    read_poison: 注入用——把"本环节对某交接表的读取"改指到不存在的表（模拟该跳断供）。
    注入只改**读侧表名**，判定路径与真查询完全不动（#ARCH-327：禁 mock 自身判定）。
    """
    poison = read_poison or {}
    handoff = list(hop.handoff)[: max(1, cap)]
    unmeasured = [t for t in hop.handoff if t not in handoff]
    up: dict[str, dict[str, Any]] = {}
    read: dict[str, dict[str, Any]] = {}
    for table in handoff:
        up[table] = _cell(table, row_counter(table))
        target = poison.get(f"{hop.hop_id}|{table}", table)
        cell = _cell(target, row_counter(target))
        if target != table:
            cell["injected_from"] = table
            cell["injection"] = "hop_read_supply_cut"
        read[table] = cell
    produced = {t: _cell(t, row_counter(t)) for t in hop.produced[: max(1, cap)]}
    unmeasurable = sorted([t for t, c in up.items() if c["rows"] == FF_ROWS_UNMEASURABLE]
                          + [t for t, c in produced.items() if c["rows"] == FF_ROWS_UNMEASURABLE])
    breaks = hop_breaks(hop, up, read, produced, unmeasured)
    return {"hop_id": hop.hop_id, "src": hop.src, "dst": hop.dst, "kind": hop.kind,
            "upstream_landed": up, "this_stage_read": read, "this_stage_produced": produced,
            "downstream_readable": {t: 0 for t in handoff}, "unmeasured": unmeasured,
            "unmeasurable_tables": unmeasurable, "breaks": breaks,
            "note": hop_note(hop, up, read, produced, breaks)}


def _cell(table: str, rows: int) -> dict[str, Any]:
    return {"table": table, "rows": rows, "measurable": rows >= 0 or rows == FF_ROWS_UNMEASURABLE,
            "reachable": rows != FF_ROWS_UNREACHABLE, "nonempty": rows > 0,
            "basis": _ROW_BASIS.get(table, "")}


def hop_breaks(hop: FlowthroughHopSpec, up: dict[str, dict[str, Any]], read: dict[str, dict[str, Any]],
               produced: dict[str, dict[str, Any]], unmeasured: list[str]) -> list[dict[str, Any]]:
    """逐跳逐表的自洽断言——每处违背都是一条带 hop_id 的断点（绝不合并成一个总数）。

    -2（不可测）**不是**断点：把"查不动"报成"断供"就是造假红，与把"断供"藏进总数同样有害；
    但它必须被逐跳显式列出（unmeasurable 面），禁静默按"有货"或"没货"处理。
    """
    out: list[dict[str, Any]] = []
    for table, cell in sorted(up.items()):
        rc = read.get(table, {})
        if cell["rows"] == FF_ROWS_UNREACHABLE:
            out.append(_break(hop, "upstream_table_absent", table, cell["rows"]))
        elif cell["rows"] == 0:
            out.append(_break(hop, "upstream_landed_zero", table, 0))
        elif rc.get("rows", 1) == FF_ROWS_UNREACHABLE:
            out.append(_break(hop, "supply_cut_at_read", table, rc.get("rows")))
        elif rc.get("rows", 1) == 0:
            out.append(_break(hop, "read_zero_while_upstream_has", table, rc.get("rows")))
    for table, cell in sorted(produced.items()):
        if cell["rows"] == FF_ROWS_UNREACHABLE:
            out.append(_break(hop, "produced_table_absent", table, cell["rows"]))
        elif cell["rows"] == 0:
            out.append(_break(hop, "produced_empty", table, 0))
    if unmeasured:
        out.append(_break(hop, "handoff_truncated_not_measured", ",".join(unmeasured[:4]), len(unmeasured)))
    return out


def _break(hop: FlowthroughHopSpec, reason: str, table: str, rows: Any) -> dict[str, Any]:
    return {"hop_id": hop.hop_id, "src": hop.src, "dst": hop.dst, "reason": reason,
            "table": table, "rows": rows}


def hop_note(hop: FlowthroughHopSpec, up: dict[str, dict[str, Any]], read: dict[str, dict[str, Any]],
             produced: dict[str, dict[str, Any]], breaks: list[dict[str, Any]]) -> str:
    if not hop.handoff:
        return "上游无声明落点（该跳交接面不可判）"
    shared = [t for t in up if read.get(t, {}).get("injected_from")]
    if shared:
        return f"注入生效于读侧：{', '.join(shared[:3])}"
    return f"交接表 {len(up)} 张 / 产出表 {len(produced)} 张 / 断 {len(breaks)} 处"


def evaluate_hops(hops: list[FlowthroughHopSpec], row_counter: Callable[[str], int],
                  read_poison: dict[str, str] | None = None, cap: int = FF_HOP_TABLE_CAP
                  ) -> dict[str, Any]:
    """全跳一遍逐跳断言 → 报红的跳集合（每条都指名 src→dst）。"""
    evid = [measure_hop(h, row_counter, cap=cap, read_poison=read_poison) for h in hops]
    broken = sorted({e["hop_id"] for e in evid if e["breaks"]})
    return {"hops": evid, "broken_hops": broken, "broken_detail": [
        b for e in evid for b in e["breaks"]]}


def cmd_e2e(args: argparse.Namespace) -> dict[str, Any]:
    """主链灌水：逐跳四数字（规范 §3.1）+ 论域声明（R-024 硬约束）。"""
    ctx = FlowthroughProbeContext(limit_tables=args.limit_tables, limit_runs=0, use_db=not args.no_db,
                                  trade_date=args.trade_date)
    sources = collect_sources()
    model = derive_stage_model(sources)
    catalog = build_stage_catalog(model, sources)
    order = sorted(k for k, v in catalog.items() if v.get("kind") in ("supply", "pipeline"))
    scans = {k: scan_stage_tables(catalog[k]["code_paths"]) for k in order}
    hops = enumerate_hops(catalog, scans, parse_skeleton_stages())
    counter = _memo_counter(_row_count)
    result = evaluate_hops(hops, counter)
    result.update({"generated_at": now_utc_str(), "trade_date": args.trade_date, "chain_order": order,
                   "verdict": "绿" if not result["broken_hops"] else "红"})
    result["universe"] = universe_declaration(sources, catalog, "FF-01..末端主链灌水")
    for h in result["hops"]:
        log_line(f"[e2e] {h['hop_id']}({h['kind']}) 上游落点={_cells_brief(h['upstream_landed'])} "
                 f"本环节读取={_cells_brief(h['this_stage_read'])} "
                 f"本环节产出={_cells_brief(h['this_stage_produced'])} "
                 f"断={len(h['breaks'])} {h['note'][:70]}")
        for b in h["breaks"][:4]:
            log_line(f"        └─断点 {b['hop_id']} {b['reason']} 表={b['table']} 行数={b['rows']}")
    log_line(f"[e2e] 判断跳：{result['broken_hops'] or '无'}（共 {len(hops)} 跳逐跳断言）")
    _render_universe(result["universe"])
    _dump_json("e2e_result.json", result)
    return result


def _cells_brief(cells: dict[str, dict[str, Any]]) -> str:
    return ", ".join(f"{t}={v['rows']}" for t, v in sorted(cells.items())[:4]) or "—"



# --------------------------------------------------------------------------
# 论域声明（R-024 硬约束）：每份报表必须显式说"我这个结论覆盖哪一片、片外有什么"
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FlowthroughUniverseScope:
    """一份结论的论域边界载体。**缺此块的报表视为无效**（universe_guard 直接抛错）。

    R-024 教训：骨架把论域限定在 depgraph 却没声明 → 被总包当成全域完备证明使用。
    """

    scope: str
    universe_domains: tuple[str, ...] = ()
    registered_without_entity: tuple[str, ...] = ()
    entity_without_registration: tuple[str, ...] = ()
    stages_covered: tuple[str, ...] = ()
    stages_outside_report: tuple[str, ...] = ()
    sources_missing: tuple[str, ...] = ()


class UniverseDeclarationError(RuntimeError):
    """报表缺论域声明=该报表作废（R-024 的代码化硬约束，不是文档劝告）。"""


def universe_declaration(sources: dict[str, tuple[set[str], dict[str, Any]]], catalog: dict[str, Any],
                         scope: str, residual_domains: tuple[str, ...] = ()) -> dict[str, Any]:
    """现算论域：在册无实体 / 有实体无册 / 已覆盖环节 / 报告外环节 / 扫描排除面 / 截断上限。"""
    vocab = {t: sources.get(t, (set(), {}))[0] for t in DOMAIN_VOCAB_SOURCES}
    entity = vocab.get("G_depgraph_runtime") or set()
    registered = set().union(*[v for v in vocab.values() if v]) if any(vocab.values()) else set()
    skeleton = parse_skeleton_stages()
    return {
        "scope": scope,
        "domains_in_universe": sorted(entity),
        "registered_without_entity": sorted(registered - entity),
        "entity_without_registration": sorted(entity - registered),
        "stages_covered": sorted(catalog),
        "stages_outside_report": sorted(set(skeleton) - set(catalog)),
        "residual_domains_no_flow_stage": sorted(residual_domains),
        "scan_exclusions": list(SCAN_EXCLUDES),
        "caps": list(_code_scan_caps_notes()),
        "sources_missing": sorted(t for t, (_, m) in sources.items() if m.get("missing") or m.get("error")),
        "counts": {"universe_domains": len(entity), "registered_domains": len(registered),
                   "在册无实体": len(registered - entity), "有实体无册": len(entity - registered),
                   "环节覆盖": len(catalog)},
    }


def _code_scan_caps_notes() -> tuple[str, ...]:
    """把"看不见的地方"如实列出来——静态扫描的文件数上限就是论域上限（禁只说扫了多少）。"""
    return ("每环节代码扫描文件上限 900（scan_stage_tables cap_files）；产物读盘上限 400 文件 / 60 件",
             "①③ 每环节实测表数上限=FlowthroughProbeContext.limit_tables（超出必须列入 unmeasured）",
             f"逐跳交接表上限 {FF_HOP_TABLE_CAP} 张/跳"
             "（超出=handoff_truncated_not_measured 断点，禁静默截断）",
             f"排除面 {', '.join(SCAN_EXCLUDES)}（统计口径，防 .aidrafts/.worktrees 造成 33 倍放大）",
             "② 真跑入口上限=limit_runs；敏感符号命中者一律 SKIP-需门位，不判绿",
             "静态扫描看不见 getattr/注册表驱动的运行时接线：孤儿结论须过 --orphan-audit 动态注册面口径")


def render_universe_lines(u: dict[str, Any]) -> list[str]:
    """论域声明的**唯一**渲染口径（markdown / stdout 共用，防两处说法不一）。"""
    return ["## 论域声明（本结论的边界，缺此块=报表作废）", "",
            f"- **本结论论域** = {u['scope']}",
            f"- 论域内域数（depgraph 有实体）：**{len(u['domains_in_universe'])}**",
            f"- **论域外有册无实体的域 = {len(u['registered_without_entity'])} 个**："
            + (", ".join(f"`{d}`" for d in u["registered_without_entity"]) or "无"),
            f"- 有实体无册（depgraph 有、域册皆无）= {len(u['entity_without_registration'])} 个："
            + (", ".join(f"`{d}`" for d in u["entity_without_registration"]) or "无"),
            f"- 未被任何 flow_stage 机械归口的域 = {len(u['residual_domains_no_flow_stage'])} 个："
            + (", ".join(f"`{d}`" for d in u["residual_domains_no_flow_stage"][:60]) or "无"),
            f"- 覆盖环节 {len(u['stages_covered'])} 个："
            f"{', '.join(u['stages_covered'])}；骨架有而本报告未出环节："
            f"{', '.join(u['stages_outside_report']) or '无'}",
            f"- 真源不可用/缺件：{', '.join(u['sources_missing']) or '无'}",
            "- 扫描/限流造成的**检出面缺口**（这些面内的问题本尺子看不见）："] \
        + [f"  - {c}" for c in u["caps"]] \
        + ["- 表述纪律（裁定#325）：本件永不说\"全绿\"，只说\"该轮检出 N 件且已被证明能红\"。"]


def universe_guard(text: str) -> None:
    """写盘前自检：正文没有论域声明块 → 抛错（代码级硬约束，不靠人自觉）。"""
    if "## 论域声明" not in text or "本结论论域" not in text:
        raise UniverseDeclarationError(
            "报表缺『论域声明』块——R-024：未声明论域的结论会被下游当成全域完备证明使用")


# 机器读件（04_sixway_machine_ledger.yaml）的论域块必备字段——下游是按字段读的，
# 故这里的断言口径必须比 markdown 版更强：不能只查"有没有这段字"，要查每个判据字段都在且非伪空。
FF_UNIVERSE_REQUIRED_KEYS: tuple[str, ...] = (
    "scope", "domains_in_universe", "registered_without_entity", "entity_without_registration",
    "stages_covered", "stages_outside_report", "residual_domains_no_flow_stage",
    "scan_exclusions", "caps", "sources_missing", "counts")


def universe_guard_payload(u: dict[str, Any]) -> None:
    """机器读件写盘前的论域硬断言（与 `universe_guard` 同一禁令，换了机读口径的实现）。

    防的正是 R-024 那类失误的机读版：论域块整块缺失或字段被静默置空，
    下游 `yaml.safe_load` 后 `.get(k, [])` 一律拿到空表 → 把"没扫到"读成"扫了且为零"。
    """
    missing = [k for k in FF_UNIVERSE_REQUIRED_KEYS if k not in u]
    if missing:
        raise UniverseDeclarationError(f"机读件论域块缺字段 {missing}——缺字段=论域未声明，不得落盘")
    if not str(u["scope"] or "").strip():
        raise UniverseDeclarationError("机读件论域 scope 为空——未声明论域的结论会被当成全域完备证明")
    if not isinstance(u["counts"], dict) or "universe_domains" not in u["counts"]:
        raise UniverseDeclarationError("机读件论域 counts.universe_domains 缺失——分母不可核则结论不可用")


def _render_universe(u: dict[str, Any]) -> None:
    for line in render_universe_lines(u):
        log_line(line if line.startswith("##") else "  " + line)


# --------------------------------------------------------------------------
# 动态注册面复核（R-023 同法：静态零入度可能是假阳性，尤其 D_AI_LAYER 11 件）
# --------------------------------------------------------------------------
SQL_DOMAIN_MODULES = (
    "SELECT n.path AS path, count(*) AS in_deg, min(n.name) AS callee_name"
    " FROM nodes n LEFT JOIN edges e ON e.to_node_id = n.node_id"
    " WHERE n.domain_id = %s AND n.path IS NOT NULL GROUP BY n.path ORDER BY in_deg ASC LIMIT 200")
SQL_MODULE_SRC_CONSUMERS = (
    "SELECT DISTINCT s.path AS consumer FROM edges e JOIN nodes src ON src.node_id = e.from_node_id"
    " JOIN nodes s ON s.node_id = e.to_node_id"
    " WHERE src.path = %s AND s.path LIKE 'src/%' LIMIT 12")


def audit_domain_orphans(domains: tuple[str, ...] = ("D_AI_LAYER",), cap: int = 60) -> dict[str, Any]:
    """按"动态注册面"口径复判零入度孤儿：注册表/importlib 能解释的一律不算孤儿。"""
    out: dict[str, Any] = {"domains": list(domains), "rows": []}
    for dom in domains:
        try:
            mods = _depgraph_rows(SQL_DOMAIN_MODULES, (dom,))
        except Exception as exc:  # noqa: BLE001 — DB 不可达=该域不可判，禁把"不可判"报成"孤儿"
            out["rows"].append({"domain": dom, "verdict": "不可判", "evidence": str(exc)[:140]})
            continue
        for m in mods[:cap]:
            path = str(m.get("path") or "")
            verdict, evidence = orphan_verdict(path, str(m.get("callee_name") or Path(path).stem))
            out["rows"].append({"domain": dom, "module": path, "static_in_degree": m.get("in_deg"),
                                "verdict": verdict, "evidence": evidence})
    return out


def orphan_verdict(rel_path: str, stem: str) -> tuple[str, str]:
    """单个零入度件的复判：动态注册面/importlib 命中=假阳性；否则才进孤儿候选。"""
    dyn = dynamic_registration_hits([rel_path])
    if dyn:
        return "假阳性（动态注册面命中）", f"注册于 {', '.join(dyn[0]['registered_in'][:3])}"
    importer = _dynamic_import_evidence(stem)
    if importer:
        return "假阳性（importlib 动态加载）", importer
    src_users = _global_consumers(rel_path)
    if src_users:
        return "活链（src 有消费者）", f"{len(src_users)} 个 src 消费者：{', '.join(src_users[:3])}"
    return "孤儿候选（需总包裁定）", "src 零消费者且无动态注册证据"


def _dynamic_import_evidence(stem: str) -> str:
    """扫 src/ 里 `import_module(...)` 且字面提及该模块名的证据（静态但可靠，BRK-009 同类）。"""
    if not stem or len(stem) < 4:
        return ""
    for p in _iter_py([REPO_ROOT / "src"], cap=2500):
        if p.stem == stem:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "import_module" in text and stem.lower() in text.lower():
            return f"{p.relative_to(REPO_ROOT)} 含 import_module 且字面提及 {stem}"
    return ""


def _cmd_orphan_audit(args: argparse.Namespace) -> int:
    """--orphan-audit：动态注册面口径复判孤儿，打印论域声明 + 落 JSON。"""
    domains = tuple(args.domain) or ("D_AI_LAYER",)
    audit = audit_domain_orphans(domains)
    sources = collect_sources(DOMAIN_VOCAB_SOURCES)
    model = derive_stage_model(sources)
    catalog = build_stage_catalog(model, sources)
    audit["universe"] = universe_declaration(sources, catalog, f"域 {'/'.join(domains)} 的模块消费面",
                                             tuple(model["residual_domains"]))
    _render_universe(audit["universe"])
    buckets: dict[str, int] = {}
    for row in audit["rows"]:
        key = str(row.get("verdict", "不可判"))
        buckets[key] = buckets.get(key, 0) + 1
        log_line(f"[orphan] {row.get('module')} 静态入度={row.get('static_in_degree')} → {key}"
                 f"｜{str(row.get('evidence'))[:90]}")
    log_line(f"[orphan] 分桶：{json.dumps(buckets, ensure_ascii=False)}")
    _dump_json("orphan_audit.json", audit)
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="全流通验收仪：六向台账 + 三态建议 + 遗漏对账 + 自红证明")
    ap.add_argument("--crosscheck", action="store_true", help="规范 §4.1：6+ 真源两两差集对账")
    ap.add_argument("--stage", help="单环节六向实测，如 FF-01")
    ap.add_argument("--all", action="store_true", help="全部推导环节跑六向")
    ap.add_argument("--verdict", action="store_true", help="读台账出三态建议汇总")
    ap.add_argument("--prove-red", action="store_true",
                    help="规范 §3.4：证明本尺子能红（≥10 跳逐跳精确指名+无误指）")
    ap.add_argument("--e2e", action="store_true", help="规范 §3.1：主链灌水逐跳四数字")
    ap.add_argument("--orphan-audit", action="store_true",
                    help="R-023 同法复核零入度孤儿（动态注册面口径）")
    ap.add_argument("--domain", action="append", default=[], help="--orphan-audit 指定域，可重复")
    ap.add_argument("--hop", type=int, default=0, help="--prove-red 注入第几跳（默认 0）")
    ap.add_argument("--hop-count", dest="hop_count", type=int, default=12,
                    help="--prove-red 逐跳注入跳数（下限 10）")
    ap.add_argument("--limit-tables", dest="limit_tables", type=int, default=6,
                    help="①③ 每环节实测表数上限（限流）")
    ap.add_argument("--limit-runs", dest="limit_runs", type=int, default=2,
                    help="② 每环节真跑入口数上限（0=关真跑）")
    ap.add_argument("--timeout", type=int, default=90, help="② 单次真跑超时秒")
    ap.add_argument("--trade-date", dest="trade_date", default="", help="--e2e 选定的真实交易日")
    ap.add_argument("--no-db", dest="no_db", action="store_true",
                    help="不连 DB（①③④降级为不可测，用于离线自检）")
    ap.add_argument("--force", action="store_true", help="忽略资源自守闸")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.crosscheck:
        cmd_crosscheck(args)
        log_line(f"[crosscheck] 已落盘 {OUT_DIR / '03_omission_crosscheck.md'}")
        return 0
    if args.stage or args.all:
        records = cmd_stage(args)
        for rec in records:
            log_line(f"[sixway] {rec['stage_id']} 建议={rec.get('verdict_suggested')}")
        return 0
    if args.verdict:
        return 0 if cmd_verdict(args) else 1
    if args.prove_red:
        return 0 if cmd_prove_red(args) else 1
    if args.e2e:
        return 0 if cmd_e2e(args) else 1
    if args.orphan_audit:
        return _cmd_orphan_audit(args)
    build_parser().print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
