#!/usr/bin/env python3
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §data-supply-chain-map
# [MODULE] scripts.governance.d5_architecture.validators.validate_data_supply_chain_map
# noqa: m11-perm-manual-legitimate  合法 manual CLI 校验器（ARCH-051 裁定口径）：D11-G02 数据供应链图对账尺人工/AI 按需调用，task_bound 工具非永久自动运行器
# [DOMAIN] D_DATA
# [TTL] permanent
# [DEPENDENCIES] yaml; 生成器真源 config/data_supply_chain_map.yaml 的机生源（tasks.yaml / schedule.yaml
#   /骨架 §1 状态列 / docs/03_modules/path_ownership_map.yaml 的 depgraph 派生在册投影）；
#   门禁册与数据资产注册表仅 check_anchors / check_inv1 两个存在性面读取（validate_structure 零 I/O）；
#   zephyr.governance.depgraph_schema（module_id 在册性 DB 腿，不可达=降 warn，禁环境异常打死提交）
# [CONSUMERS] config/data_supply_chain_map.yaml 质量门禁；
#   zephyr.gov_enforcement.commit_gates.data_supply_chain_map_gate（结构校验单一真源复用）;
#   scripts.governance.d5_architecture.generators.align_all（第十一节挂轴）;
#   tests/governance/d5_architecture/test_data_supply_chain_map_adversarial.py;
#   CLI: python .../validate_data_supply_chain_map.py --map config/data_supply_chain_map.yaml
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 台账只读（本工具禁写任何图/真源文件）；结构错误=exit 1，警告不阻断；
# [MODIFY-GUARD] 判据口径真源=docs/_working/map_build/fig12_datachain/00_skeleton.md §1 与
#   03 号簿 §1/§2/§3；放宽任何检查项=改判据，须与图 YAML+gate+对抗测试同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 结构/锚/INV-1 违规=exit 1；图文件缺失/YAML 解析失败/顶层非对象=exit 2；
#   骨架/depgraph/门禁册等外部面不可达=对应子检查降 warn，绝不升级为 error；本件零写入
# [TESTS] tests/governance/d5_architecture/test_data_supply_chain_map_adversarial.py
#   validate_structure 是**唯一结构真源**（gate 只封阻塞语义，禁复制判据），除锚/在册腿外零 I/O;
#   检查项=顶层必填键/节点 L0-L1 必填字段/22 环节契约全集双向差集（越界=伪造环节、缺号=缺环节）/
#   CV-L0 旧别名残留即红（note_zh/doc_refs/source_anchors/fallback/downstream_action 统一名）/
#   CV-BUS 总线挂载（module_ref⇒module_id、MOD-* 形态、在册投影逐路径核、null 必配 red_reason）/
#   CV-DUAL 双轴（production⇔骨架 ✅ 逐节点+计数双判、分面行禁 production、production 必带
#   freshness_evidence 且 verdict∈{fresh,lagging}、probe_failed 一律不放行、通道禁空串语义）/
#   CV-FACET（分面节点≥2 腿+腿态合法+腿证据非空+行级 ✅ 仅当全腿 ✅）/
#   CV-GAP（gap 必带 red_reason∈枚举+禁 module_ref/module_id+禁 built+至少一条边+被 gap_refs 指到）/
#   CV-WAIT（boundary.waiting_table_gaps 5 表 + ghost_ref_gaps 1 表全部落到在册 gap 节点且表锚在节点内）/
#   边两端闭合/重复边/自环/未声明反馈环的反向边/五段枚举/built 必有代码锚/verified 必带 evidence/
#   越域挂载禁判据字段/store_refs 三要素/counts 与实数一致/decision_question 长度/INV-1 引用不复制;
#   CH 表存在性与 depgraph 在册性走注入 resolver 或只读腿，不可达=warn 不阻断（环境异常域）
# [MODIFY-GUARD] 判据口径真源=docs/_working/map_build/fig12_datachain/00_skeleton.md §1（22 环节契约与
#   状态格机读口径）与 docs/_working/map_build/03_final_blueprint_and_schema.md §1/§2/§3（三层字段、
#   CV-BUS、双轴）；放宽任何检查项=改判据，须总包裁定并与图 YAML+gate+对抗测试同批
# [STABILITY] evolving
# [SAFETY] L
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读不到实载集合必抛，禁降级为'无冲突'
# [TESTS] 见同批 tests/ 下 canary 件
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)=结构/锚/INV-1 违规; SystemExit(2)=文件缺失或 YAML 解析失败或顶层非对象;
#   骨架/depgraph/门禁册等外部面不可达=对应子检查降 warn（warnings 出参），绝不升级为 error
# [TESTS] tests/governance/d5_architecture/test_data_supply_chain_map_adversarial.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图12 数据供给链图结构校验器——schema v0.2（22 环节 + 三层字段 + 双轴）判据单一真源。

形态照图9 母版与图11 已定稿件（``validate_dev_delivery_map``）：``validate_structure(data, root=None,
warnings=None) -> list[str]`` 纯内存判据，gate 只封阻塞语义；``exit 1``=结构违规，``exit 2``=解析失败。

本图特有判据（血肉不许丢，也不许粉饰）：
- **挂槽≠在跑**：``wiring_status`` 必填枚举，``unwired*`` 节点禁标 ``built``；
- **检测≠修复**：``downstream_action`` 必填（detect_only/alert_only/auto_remediate/none），
  只检测无补跑通道的结论必须落进 ``gaps``/``gap_refs``；
- **终点不可证**：``boundary.terminal_gap`` 必须指向真实 ``node_type: gap`` 节点；
  消费方在等的 5 张未产表与 1 处幽灵引用必须由在册 gap 节点承载（CV-WAIT，禁隐没进散文）；
- **双轴不许混**：``verified_scope: production`` 数与骨架 §1 的 ✅ 数**不多不少**——
  多了算谎（逐节点判）、少了算欠（反向判），且分面行与 probe_failed 一律不得放行 production；
- **新鲜度口径**：production 断言必带 ``freshness_evidence``（table/date_col/max_date/probe_at_utc/
  lag_trading_days/channel/verdict/final_variant 八字段齐），通道只认失败即抛版，
  禁把 ``ch_reader/ch_writer`` 的"失败→空串"当证据（本役 ★坑1 的机生版）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_VALDIR = str(Path(__file__).resolve().parent)
if _VALDIR not in sys.path:
    sys.path.insert(0, _VALDIR)
from typing import Any, Callable

import yaml
from validate_construction_steps import (
    depgraph_missing_module_ids,  # noqa: E402  CLONEGUARD合并:兄弟校验器单一真源(原稿三胞胎helper,本件删副本改导入)
)

DEFAULT_MAP = Path("config/data_supply_chain_map.yaml")
_REPO_ROOT = Path(__file__).resolve().parents[4]
TASKS_YAML_REL = "src/zephyr/data/config/tasks.yaml"
SCHEDULE_YAML_REL = "src/zephyr/data/config/schedule.yaml"
ASSET_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml"
SKELETON_REL = "docs/_working/map_build/fig12_datachain/00_skeleton.md"
PATH_OWNERSHIP_REL = "docs/03_modules/path_ownership_map.yaml"

REQUIRED_TOP = [
    "schema_version",
    "map_id",
    "name_zh",
    "generator",
    "ssot_note_zh",
    "laws",
    "segments",
    "boundary",
    "nodes",
    "edges",
    "feedback_loops",
    "counts",
]
# L0 统一名（六图终局卷 §1 裁定一：同语义必同名；缺字段=判红）
REQUIRED_NODE = [
    "node_id",
    "name_zh",
    "segment",
    "node_type",
    "decision_question",
    "note_zh",
    "build_status",
    "wiring_status",
    "slot_source",
    "downstream_action",
    "confidence",
    "source_anchors",
    "doc_refs",
]
# 必须**存在**（值可为 null）的键：双轴与总线挂载面，禁静默缺失
REQUIRED_KEY_PRESENT = ["verified_scope", "module_id", "fallback", "store_refs", "gap_refs"]
# 废止别名（残留即 CV-L0 红）——统一名见冒号右值
BANNED_NODE_FIELDS = {
    "mech_note_zh": "note_zh",
    "semantics_zh": "note_zh",
    "clock_semantics_zh": "note_zh",
    "design_refs": "doc_refs",
    "doc_ref": "doc_refs",
    "miss_fallback_zh": "fallback",
    "degradation": "fallback",
    "silent_failover": "fallback",
    "data_anchors": "source_anchors + data_refs",
    "detection_only": "downstream_action",
}
# 越域挂载（决策判据归 TDM/算法域，本图 L1/L2 禁字段）
CROSS_DOMAIN_FIELDS = frozenset(
    {"judgment_basis", "factor_refs", "strategy_refs", "judgment_criteria", "indicator_refs", "action_plan_refs"}
)

SEGMENTS = ["S1_collect", "S2_ingest", "S3_derive", "S4_coldstore", "S5_recon"]
# 22 环节契约全集（骨架 §1 批次4 定稿：18→22，D12-10 拆 a/b，新立 D12-19/20/21；§6.3 封顶重宣）。
# 辅助节点（源面/汇聚/交接/通道/缺口显性化）须在 AUX_NODE_ID_CONTRACT 内且 node_type 落 AUX_NODE_TYPES
# ——stage 节点越界=伪造环节判红，缺号=缺环节判红（无逃生口）。
STAGE_UNIVERSE: frozenset[str] = frozenset(
    [f"DSC-{i:02d}" for i in range(1, 10)] + ["DSC-10A", "DSC-10B"] + [f"DSC-{i:02d}" for i in range(11, 22)]
)
AUX_NODE_ID_CONTRACT: frozenset[str] = frozenset(
    {
        "DSC-SRC",
        "DSC-FB",
        "DSC-HA",
        "DSC-HB",
        "DSC-HC",
        "DSC-14D",
        "DSC-GAP-NEWSGHOST",
        "DSC-GAP-MACRO",
        "DSC-GAP-L2TICK",
        "DSC-GAP-REPLAY",
        "DSC-GAP-DUPGUARD",
        "DSC-GAP-CONSENSUSCHAIN",
        "DSC-GAP-NAV",
        "DSC-GAP-EXECEP",
        "DSC-GAP-FFVAL",
        "DSC-GAP-FFSIG",
        "DSC-GAP-ARCHIVE-AUDIT",
        "DSC-GAP-CODEBACKUP",
        "DSC-GAP-MIRROR",
        "DSC-GAP-TERMINUS",
        "DSC-GAP-RECDIFF",
    }
)
AUX_NODE_TYPES = {"source", "convergence", "channel", "handoff", "gap"}
NODE_TYPES = {"source", "stage", "channel", "convergence", "handoff", "gap"}
BUILD_STATUS = {"built", "partial", "pending"}
WIRING_STATUS = {
    "wired_cron",
    "wired_import",
    "wired_stream",
    "wired_event",
    "wired_os_task",
    "wired_special_branch",
    "wired_manual",
    "decision_only",
    "partial",
    "running_unregistered",
    "unwired",
    "unwired_slot_hollow",
    "unwired_no_caller",
    "unwired_exempt_bypass",
}
SLOT_SOURCES = {"schedule", "schtasks", "event", "dloop_stage", "manual", "none"}
DOWNSTREAM_ACTIONS = {"auto_remediate", "alert_only", "detect_only", "none"}
CONFIDENCE = {"verified", "proposed", "untested"}
VERIFIED_SCOPE = {"production", "structure"}
RED_REASONS = {"terminal", "unwired", "broken_supply", "ghost_ref"}
FACET_STATUS = {"✅", "🔨", "⬜", "🟡", "🔴"}
EDGE_KINDS = {"data_flow", "degrade", "handoff_out", "feedback", "control", "trigger", "gap"}
EDGE_STATUS = {"live", "unwired", "degraded"}
GAP_SYMPTOMS = {
    "zero_rows",
    "near_empty",
    "stale_as_of",
    "written_but_stale",
    "source_side_lag",
    "future_value_polluted_max",
    "inversion",
    "unwired",
    "gate_bypassed",
    "doc_contradiction",
    "retired_not_removed",
    "unregistered_running",
    "false_success",
    "tool_broken",
    "hardcoded_main_repo",
    "detection_no_repair",
    "unprovable_slot",
    "stale_slot_run",
    "ledger_conflict",
    "no_periodic_audit",
    "guard_revived",
    "never_run",
    "manual_only",
    "untracked",
    "path_ghost",
    "attribution_moved",
    "dow_semantics_conflict",
    "epoch_sentinel_column",
    "coverage_shrink",
    "no_idempotency_key",
    "false_green_trap",
    "terminal_unprovable",
    "unresolved_gaps",
    "duplicate_task_id",
    "parallel_impl_cluster",
    "malformed_bus_id",
    "detector_scope_gap",
    "zero_fire_no_audit",
    "no_task_row",
    "run_failing",
    "slot_run_missing",
    "skip_silent",
    "nonterminal_result",
    "nominal_switch",
    "table_missing",
    "ghost_ref",
    "probe_failed",
}
DECISION_QUESTION_MAX = 120
# 缺口覆盖下限（真源=六图终局卷 §4 图12 终局判据③ + 11 卷 §1-C/§1-D 实扫：5 处等未产表、1 处幽灵）。
# 这是**下限**不是上限：新增断供必须加进来，把已实见的从账上抹掉即判红（禁"图变干净"）。
WAITING_TABLE_MIN = 5
GHOST_REF_MIN = 1
INV1_MIN_PROSE = 24  # 与真源正文逐字重合达此长度即判复制侵权
ANCHOR_PREFIXES = ("task:", "slot:", "file:", "node:", "table:", "source:", "status:")
# freshness_evidence 八字段（口径真源=12 号卷 §5-3；缺字段=判红，禁凭印象 ✅）
FRESHNESS_REQUIRED = [
    "table",
    "date_col",
    "max_date",
    "probe_at_utc",
    "lag_trading_days",
    "channel",
    "verdict",
    "final_variant",
]
FRESHNESS_VERDICTS = {"fresh", "lagging", "probe_failed", "not_applicable"}
PRODUCTION_VERDICTS = {"fresh", "lagging"}
# 证据通道白名单=失败即抛版；空串语义通道（ch_reader/ch_writer 的 query）一律不得作证据
_BAD_CHANNEL_RE = re.compile(r"ch_reader\.query|ch_writer\.query|query\(\s*[\"']SELECT", re.I)
_MODULE_ID_RE = re.compile(r"^MOD-[A-Z0-9][A-Z0-9_-]*$")
_SKELETON_ROW_RE = re.compile(r"^\|\s*(D12-\d{2}[ab]?)\s*\|([^|]*)\|([^|]*)\|\s*([✅🔨⬜]|分面)", re.M)
# 只读册/DB 扫描缓存（同一 gate 进程内逐节点复用；键含册的 mtime/size 或入参集，故不吞新鲜度）
_SCAN_CACHE: dict[str, tuple[Any, Any]] = {}
# module_ref 磁盘实存豁免（与图11/13 同口径：运行时态/外置盘/占位不做结构侧存在判定）
_ANCHOR_DISK_EXEMPT = (
    ".runtime/",
    ".ailocks/",
    ".aidrafts",
    "data/runtime/",
    "tmp/",
    "logs/",
    "F:",
    "G:",
    "f:",
    "g:",
    "待定",
)


def _err(errors: list[str], msg: str) -> None:
    """_err implementation."""
    errors.append(msg)


def _banned_key_hits(node: Any) -> list[str]:
    """递归收集节点内（含嵌套字段）出现的旧别名/禁挂判据字段名。"""
    found: list[str] = []

    def walk(obj: Any) -> None:
        """walk implementation."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in BANNED_NODE_FIELDS:
                    found.append(f"alias:{k}")
                if k in CROSS_DOMAIN_FIELDS:
                    found.append(f"domain:{k}")
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(node)
    return sorted(set(found))


def _cached_scan(key: str, path: Path, fn: Callable[[], Any]) -> Any:
    """按 (路径, mtime_ns, size) 缓存只读册扫描（gate/测试逐节点多次调用，禁重复解析 8k 条）。"""
    stamp = (str(path), path.stat().st_mtime_ns, path.stat().st_size) if path.exists() else None
    hit = _SCAN_CACHE.get(key)
    if hit and hit[0] == stamp:
        return hit[1]
    val = fn()
    _SCAN_CACHE[key] = (stamp, val)
    return val


def scan_skeleton_status(root: Path) -> dict[str, str]:
    """骨架 §1 状态列实扫（production 断言的**唯一**外部对照物）。

    状态格首字符=行级符号（✅/🔨/⬜）或 `分面`；与生成器同一张表同一个列，两侧不会各自漂移。
    骨架不可读/表形变更 ⇒ 空表，调用侧把 CV-DUAL 的 ✅ 对照降 warn（禁环境异常打死提交）。
    """
    p = root / SKELETON_REL

    def _run() -> dict[str, str]:
        """_run implementation."""
        if not p.exists():
            return {}
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = text.split("## §1 环节全集", 1)
        if len(parts) != 2:
            return {}
        body = parts[1].split("## §2", 1)[0]
        out: dict[str, str] = {}
        for m in _SKELETON_ROW_RE.finditer(body):
            out["DSC-" + m.group(1).split("-", 1)[1].upper()] = m.group(4)
        return out

    return _cached_scan(f"skeleton:{root}", p, _run)


def scan_module_id_index(root: Path) -> dict[str, str] | None:
    """depgraph 派生在册投影（claim_type=depgraph_node 的 路径→MOD-*）。None=册不可读（降 warn）。"""
    p = root / PATH_OWNERSHIP_REL

    def _run() -> dict[str, str] | None:
        """_run implementation."""
        if not p.exists():
            return None
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001 — 册不可解析=本腿降级
            return None
        out: dict[str, str] = {}
        for e in data.get("ownership") or []:
            if not isinstance(e, dict) or e.get("claim_type") != "depgraph_node":
                continue
            path, mid = e.get("path"), e.get("owner_blueprint")
            if isinstance(path, str) and isinstance(mid, str) and _MODULE_ID_RE.match(mid):
                out.setdefault(path.replace("\\", "/"), mid)
        return out

    return _cached_scan(f"modules:{root}", p, _run)


def validate_structure(data: dict, root: Path | None = None, warnings: list[str] | None = None) -> list[str]:
    """结构判据唯一真源（除骨架/在册投影两条只读腿外零 I/O）——gate 复用本函数，禁复制判据。"""
    errors: list[str] = []
    root = root or _REPO_ROOT
    for k in REQUIRED_TOP:
        if k not in data:
            _err(errors, f"缺顶层必填键: {k}")
    if errors:
        return errors
    if not data.get("laws"):
        _err(errors, "laws（全图铁律）不得为空")
    if not data.get("feedback_loops"):
        _err(errors, "feedback_loops 不得为空（图12 是反馈环图，无环即画错）")

    seg_orders: dict[str, int] = {}
    for s in data.get("segments", []):
        sid = s.get("segment_id")
        if sid not in SEGMENTS:
            _err(errors, f"segments 含非法段: {sid!r}（合法集={SEGMENTS}）")
            continue
        if not isinstance(s.get("order"), int) or isinstance(s.get("order"), bool):
            _err(errors, f"segments.{sid}: order 必须是整数")
            continue
        seg_orders[sid] = s["order"]
    for sid in SEGMENTS:
        if sid not in seg_orders:
            _err(errors, f"缺五段声明之一: {sid}")

    skeleton_status = scan_skeleton_status(root)
    if not skeleton_status and warnings is not None:
        warnings.append(f"骨架 §1 状态列不可读（{SKELETON_REL}）：CV-DUAL 的 ✅ 对照子检查降 warn")
    module_index = scan_module_id_index(root)
    if module_index is None and warnings is not None:
        warnings.append(f"depgraph 派生在册投影不可读（{PATH_OWNERSHIP_REL}）：CV-BUS 在册腿降 warn")

    nodes = data.get("nodes", [])
    ids: list[str] = []
    node_seg: dict[str, str] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for n in nodes:
        if not isinstance(n, dict):
            _err(errors, f"节点非对象: {n!r}")
            continue
        nid = n.get("node_id", "<无 node_id>")
        ids.append(nid)
        by_id[nid] = n
        node_type = n.get("node_type")
        # ── 契约面：环节越界/缺号 ──────────────────────────────────────────
        if node_type == "stage":
            if nid not in STAGE_UNIVERSE:
                _err(
                    errors,
                    f"{nid}: 节点越出 22 环节契约全集（骨架 §1 批次4 定稿+§6.3 封顶件；"
                    f"汇聚/交接/缺口等辅助节点须显式 node_type 非 stage）",
                )
        elif nid not in AUX_NODE_ID_CONTRACT:
            _err(errors, f"{nid}: 辅助节点不在契约辅助集（骨架外私加节点须先回写骨架再进图）")
        # ── CV-L0：旧别名残留 / 越域挂载 ──────────────────────────────────
        for hit in _banned_key_hits(n):
            if hit.startswith("alias:"):
                k = hit.split(":", 1)[1]
                _err(
                    errors,
                    f"{nid}: CV-L0 旧别名残留 {k}（L0/L1 统一名应为 {BANNED_NODE_FIELDS[k]}；六图终局卷 §1 裁定一）",
                )
            else:
                k = hit.split(":", 1)[1]
                _err(errors, f"{nid}: 越域挂载——节点夹带判据字段 {k}（判据归 TDM/算法域，本图只准存标识符与指针）")
        for f in REQUIRED_NODE:
            if f not in n or n[f] in (None, ""):
                _err(errors, f"{nid}: 缺必填字段 {f}")
        for f in REQUIRED_KEY_PRESENT:
            if f not in n:
                _err(errors, f"{nid}: 缺必填键 {f}（值可为 null，键必须在——双轴/总线/缺口挂载面不得静默缺失）")
        seg = n.get("segment")
        if seg not in SEGMENTS:
            _err(errors, f"{nid}: segment 非法或缺失 {seg!r}（五段枚举={SEGMENTS}）")
        else:
            node_seg[nid] = seg
        if node_type not in NODE_TYPES:
            _err(errors, f"{nid}: node_type 非法 {node_type!r}")
        elif node_type != "stage" and node_type not in AUX_NODE_TYPES:
            _err(errors, f"{nid}: 辅助节点 node_type 须落 {sorted(AUX_NODE_TYPES)}")
        if n.get("build_status") not in BUILD_STATUS:
            _err(errors, f"{nid}: build_status 非法 {n.get('build_status')!r}")
        if n.get("wiring_status") not in WIRING_STATUS:
            _err(errors, f"{nid}: wiring_status 非法（挂槽≠在跑须显式表态） {n.get('wiring_status')!r}")
        if n.get("slot_source") not in SLOT_SOURCES:
            _err(
                errors,
                f"{nid}: slot_source 非法 {n.get('slot_source')!r}"
                f"（时点从哪来须可指认，合法集={sorted(SLOT_SOURCES)}）",
            )
        if n.get("downstream_action") not in DOWNSTREAM_ACTIONS:
            _err(
                errors,
                f"{nid}: downstream_action 非法 {n.get('downstream_action')!r}"
                f"（检测≠修复：合法集={sorted(DOWNSTREAM_ACTIONS)}）",
            )
        if n.get("confidence") not in CONFIDENCE:
            _err(errors, f"{nid}: confidence 三态非法 {n.get('confidence')!r}")
        scope = n.get("verified_scope")
        if scope is not None and scope not in VERIFIED_SCOPE:
            _err(errors, f"{nid}: verified_scope 非法 {scope!r}（须 production/structure/null）")
        red = n.get("red_reason")
        if red is not None and red not in RED_REASONS:
            _err(errors, f"{nid}: red_reason 非法 {red!r}（枚举 terminal/unwired/broken_supply/ghost_ref）")
        if n.get("build_status") == "built" and not n.get("module_ref"):
            _err(errors, f"{nid}: built 节点必须有 module_ref 代码锚")
        if str(n.get("wiring_status", "")).startswith("unwired") and n.get("build_status") == "built":
            _err(errors, f"{nid}: 未接线（wiring_status={n.get('wiring_status')}）禁标 built")
        if node_type == "gap" and n.get("build_status") == "built":
            _err(errors, f"{nid}: gap（缺口）节点禁标 built")
        if n.get("confidence") == "verified" and not n.get("evidence"):
            _err(errors, f"{nid}: confidence=verified 必须带 evidence（实测指针）")
        if len(str(n.get("decision_question", ""))) > DECISION_QUESTION_MAX:
            _err(errors, f"{nid}: decision_question 超 {DECISION_QUESTION_MAX} 字")
        # ── CV-BUS：module_id 必挂在册，null 必配 red_reason ───────────────
        mod_id, mod_ref = n.get("module_id"), n.get("module_ref")
        if mod_ref and not mod_id:
            _err(errors, f"{nid}: CV-BUS——module_ref 非空而 module_id 空（有实现代码必挂 MOD-* 总线号）")
        if mod_id is not None and not _MODULE_ID_RE.match(str(mod_id)):
            _err(errors, f"{nid}: CV-BUS——module_id 非 MOD-* 形态：{mod_id!r}（禁自造号）")
        if mod_ref and mod_id and module_index is not None:
            rel = str(mod_ref).split(":")[0].replace("\\", "/")
            claimed = module_index.get(rel)
            if claimed is None:
                _err(
                    errors,
                    f"{nid}: CV-BUS——module_ref 路径 {rel} 不在 depgraph 派生在册投影内，"
                    f"却挂了 module_id={mod_id}（禁自造号；改挂在册代表路径并留账）",
                )
            elif claimed != mod_id:
                _err(errors, f"{nid}: CV-BUS——module_id={mod_id} 与在册投影 {claimed}（{rel}）不符")
        if not mod_id and not red:
            _err(errors, f"{nid}: CV-BUS——module_id 为空必配 red_reason（纯结构/终点聚合/gap 节点=合法 null 但要写因）")
        # ── CV-FACET：分面腿（行级 ✅ 仅当全腿 ✅ 的机生版）────────────────
        facets = n.get("facets") or []
        if facets:
            if not isinstance(facets, list) or len(facets) < 2:
                _err(errors, f"{nid}: facets 须为 ≥2 条腿的列表（单腿不叫分面，禁以分面掩盖整腿红）")
            for fct in facets if isinstance(facets, list) else []:
                fid = (fct or {}).get("leg_id", "?") if isinstance(fct, dict) else "?"
                if not isinstance(fct, dict) or not fct.get("name_zh"):
                    _err(errors, f"{nid}.facets[{fid}]: 缺 leg_id/name_zh（腿必须可指名）")
                    continue
                if fct.get("status") not in FACET_STATUS:
                    _err(
                        errors, f"{nid}.facets[{fid}]: 腿态非法 {fct.get('status')!r}（合法集={sorted(FACET_STATUS)}）"
                    )
                if not fct.get("evidence"):
                    _err(errors, f"{nid}.facets[{fid}]: 腿无证据即不许标态（禁印象 ✅）")
            if scope == "production":
                _err(errors, f"{nid}: CV-FACET——分面行禁宣 production（行级 ✅ 仅当全腿 ✅）")
        # ── CV-DUAL：双轴与骨架 §1 同源（多了算谎、少了算欠）──────────────
        sym = skeleton_status.get(nid)
        if scope == "production":
            if n.get("confidence") != "verified":
                _err(
                    errors,
                    f"{nid}: verified_scope=production 而 confidence={n.get('confidence')!r}（production 必 verified）",
                )
            _check_freshness(errors, nid, n)
            if skeleton_status and sym is None:
                _err(errors, f"{nid}: production 但骨架 §1 查无此行（禁给非契约环节宣在产）")
            elif skeleton_status and sym != "✅":
                _err(
                    errors,
                    f"{nid}: 谎——verified_scope=production 而骨架 §1 行级态为 {sym!r}"
                    f"（非 ✅ 不得宣在产；分面行须走 facets）",
                )
        elif skeleton_status and sym == "✅" and scope != "production":
            _err(errors, f"{nid}: 欠——骨架 ✅ 环节未宣 production（verified_scope={scope!r}）")
        for sr in n.get("store_refs", []) or []:
            if not isinstance(sr, dict) or not sr.get("artifact") or not sr.get("location") or not sr.get("retention"):
                _err(errors, f"{nid}: store_refs 条目缺 artifact/location/retention")
        for a in list(n.get("source_anchors", []) or []) + list(n.get("data_refs", []) or []):
            _check_anchor_format(errors, nid, a)
        for g in n.get("gaps", []) or []:
            if not isinstance(g, dict) or not g.get("anchor"):
                _err(errors, f"{nid}: gaps 条目缺 anchor")
                continue
            if not g.get("pointer"):
                _err(errors, f"{nid}: gaps 条目缺 pointer（实测出处，无出处=不许冒充）")
            if g.get("symptom") not in GAP_SYMPTOMS:
                _err(errors, f"{nid}: gaps.symptom 非法枚举 {g.get('symptom')!r}")
            if not g.get("measured_on"):
                _err(errors, f"{nid}: gaps 条目缺 measured_on（无时点的读数=散文）")

    if len(ids) != len(set(ids)):
        _err(errors, "node_id 存在重复")
    missing_stage = sorted(STAGE_UNIVERSE - set(ids))
    if missing_stage:
        _err(errors, f"缺环节（22 环节契约未建满）: {', '.join(missing_stage)}")
    valid_ids = set(ids)

    # ── CV-GAP：缺口不画孤岛；gap_refs 必须指到在册 gap 节点 ────────────────
    edges = data.get("edges", [])
    touched: set[str] = set()
    for e in edges:
        if isinstance(e, dict):
            touched.update({str(e.get("from")), str(e.get("to"))})
    referenced: set[str] = set()
    for n in nodes:
        if isinstance(n, dict):
            for ref in n.get("gap_refs") or []:
                referenced.add(str(ref))
                if str(ref) not in valid_ids:
                    _err(errors, f"{n.get('node_id')}: gap_refs 指向不存在节点 {ref}")
    for nid, n in by_id.items():
        if n.get("node_type") != "gap":
            continue
        if not n.get("red_reason"):
            _err(errors, f"{nid}: gap 节点必带 red_reason（枚举 terminal/unwired/broken_supply/ghost_ref）")
        if n.get("module_ref") or n.get("module_id"):
            _err(errors, f"{nid}: gap 节点禁挂 module_ref/module_id（缺口无实现代码可挂）")
        if nid not in touched:
            _err(errors, f"{nid}: gap 节点必须至少有一条边连到受影响环节（显性化不得孤岛）")
        if nid not in referenced:
            _err(errors, f"{nid}: gap 节点未被任何环节的 gap_refs 指到（缺口与生产面脱钩=隐没）")

    # ── CV-WAIT：5 处等未产表 + 1 处幽灵引用全部落到在册 gap 节点 ───────────
    boundary = data.get("boundary") or {}
    for key in ("terminal_declared", "terminal_provable", "terminal_gap"):
        vals = boundary.get(key)
        if vals is None:
            _err(errors, f"boundary 缺 {key}（终点面必须可指认）")
            continue
        for v in [vals] if isinstance(vals, str) else vals:
            if v not in valid_ids:
                _err(errors, f"boundary.{key} 引用不存在节点: {v}")
    tgap = boundary.get("terminal_gap")
    if isinstance(tgap, str) and tgap in by_id and by_id[tgap].get("node_type") != "gap":
        _err(errors, f"boundary.terminal_gap 必须指向 node_type=gap 节点: {tgap}")
    for grp, field, floor, reason in (
        ("waiting_table_gaps", "等未产表", WAITING_TABLE_MIN, None),
        ("ghost_ref_gaps", "幽灵引用", GHOST_REF_MIN, "ghost_ref"),
    ):
        mapping = boundary.get(grp) or {}
        if not mapping:
            _err(errors, f"boundary 缺 {grp}（{field}清单必须可机判，禁只写在散文/作业簿）")
            continue
        if len(mapping) < floor:
            _err(
                errors,
                f"CV-WAIT——{field}覆盖数 {len(mapping)} < 下限 {floor}"
                f"（真源=六图终局卷 §4 图12 判据③；已实见的断供不得从账上抹掉）",
            )
        for table, gid in mapping.items():
            node = by_id.get(str(gid))
            if node is None:
                _err(errors, f"CV-WAIT——{field} {table} 指向不存在节点 {gid}")
                continue
            if node.get("node_type") != "gap":
                _err(errors, f"CV-WAIT——{field} {table} 的挂载点 {gid} 不是 gap 节点")
            if reason and node.get("red_reason") != reason:
                _err(
                    errors,
                    f"CV-WAIT——{field}节点 {gid} 的 red_reason 必须为 {reason}（实际 {node.get('red_reason')!r}）",
                )
            blob = "\n".join(
                [str(x) for x in (node.get("data_refs") or [])] + [str(x) for x in (node.get("source_anchors") or [])]
            )
            if str(table).split(".")[-1] not in blob:
                _err(errors, f"CV-WAIT——{field} {table} 未出现在 gap 节点 {gid} 的锚里（禁隐没）")

    # ── counts 与实数一致（图 YAML 必须生成器再生产物）────────────────────
    counts = data.get("counts") or {}
    if isinstance(counts, dict) and counts:
        if counts.get("nodes") != len(nodes):
            _err(
                errors,
                f"counts.nodes={counts.get('nodes')} 与 nodes 实数 {len(nodes)} 不符"
                f"（图 YAML 须由生成器再生，禁手改后不回生成）",
            )
        if counts.get("edges") != len(edges):
            _err(errors, f"counts.edges={counts.get('edges')} 与 edges 实数 {len(edges)} 不符")
        real_prod = sum(1 for n in nodes if isinstance(n, dict) and n.get("verified_scope") == "production")
        if counts.get("production_nodes") != real_prod:
            _err(
                errors,
                f"counts.production_nodes={counts.get('production_nodes')} 与节点实扫 "
                f"{real_prod} 不符（静态清单禁手维）",
            )
        real_gap = sum(1 for n in nodes if isinstance(n, dict) and n.get("node_type") == "gap")
        if counts.get("gap_nodes") != real_gap:
            _err(errors, f"counts.gap_nodes={counts.get('gap_nodes')} 与节点实扫 {real_gap} 不符")
        if skeleton_status:
            real_ok = sum(1 for v in skeleton_status.values() if v == "✅")
            if counts.get("skeleton_ok_rows") != real_ok:
                _err(errors, f"counts.skeleton_ok_rows={counts.get('skeleton_ok_rows')} 与骨架实扫 {real_ok} 不符")
            # CV-DUAL 计数面（与逐节点判据双判：多=谎、少=欠）
            ok_ids = {nid for nid, s in skeleton_status.items() if s == "✅"}
            prod_ids = {
                n.get("node_id") for n in nodes if isinstance(n, dict) and n.get("verified_scope") == "production"
            }
            if ok_ids != prod_ids:
                _err(
                    errors,
                    f"CV-DUAL 计数：production 数 {len(prod_ids)} ≠ 骨架 ✅ 数 {len(ok_ids)}"
                    f"（多了算谎={sorted(prod_ids - ok_ids)}，"
                    f"少了算欠={sorted(ok_ids - prod_ids)}）",
                )

    # ── 边/反馈环闭合与段序 ────────────────────────────────────────────────
    seen_edges: set[tuple[str, str]] = set()
    feedback = {(f.get("from"), f.get("to")) for f in data.get("feedback_loops", []) if isinstance(f, dict)}
    for e in edges:
        if not isinstance(e, dict) or "from" not in e or "to" not in e:
            _err(errors, f"边格式非法（须含 from/to）: {e}")
            continue
        a, b = e["from"], e["to"]
        if a not in valid_ids or b not in valid_ids:
            _err(errors, f"边引用了不存在的节点: {a}->{b}")
            continue
        if e.get("kind") not in EDGE_KINDS:
            _err(errors, f"{a}->{b}: 边 kind 非法 {e.get('kind')!r}（合法集={sorted(EDGE_KINDS)}）")
        if e.get("status", "live") not in EDGE_STATUS:
            _err(errors, f"{a}->{b}: 边 status 非法 {e.get('status')!r}")
        if (a, b) in seen_edges:
            _err(errors, f"重复边: {a}->{b}")
        seen_edges.add((a, b))
        if a == b:
            _err(errors, f"自环边: {a}")
            continue
        if (a, b) in feedback:
            continue
        oa = seg_orders.get(node_seg.get(a, ""), 0)
        ob = seg_orders.get(node_seg.get(b, ""), 0)
        if oa and ob and oa > ob:
            _err(errors, f"未声明为反馈环的反向边: {a}->{b}（段序 {oa}->{ob}；反馈环必须在 feedback_loops 显式声明）")
    for f in data.get("feedback_loops", []):
        if not isinstance(f, dict) or not f.get("from") or not f.get("to"):
            _err(errors, f"feedback_loops 条目非法（须含 from/to）: {f!r}")
            continue
        if f.get("from") not in valid_ids or f.get("to") not in valid_ids:
            _err(errors, f"feedback_loops 引用不存在节点: {f.get('from')}->{f.get('to')}")
        if not f.get("note_zh"):
            _err(errors, f"feedback_loops 条目缺 note_zh: {f.get('from')}->{f.get('to')}")
    return errors


def _check_freshness(errors: list[str], nid: str, node: dict[str, Any]) -> None:
    """CV-DUAL 的证据半边：production 断言必带八字段齐、verdict 可用、通道非空串语义的新鲜度证据。"""
    fe = node.get("freshness_evidence")
    if not fe:
        _err(
            errors,
            f"{nid}: verified_scope=production 必带 freshness_evidence"
            "（骨架 ✅ 三腿的 (c) 腿；无实查新鲜度证据=不敢宣在产）",
        )
        return
    for i, ev in enumerate(fe if isinstance(fe, list) else []):
        tag = f"{nid}.freshness_evidence[{i}]"
        if not isinstance(ev, dict):
            _err(errors, f"{tag}: 必须是对象（table/date_col/max_date/... 八字段）")
            continue
        miss = [k for k in FRESHNESS_REQUIRED if ev.get(k) in (None, "")]
        if miss:
            _err(errors, f"{tag}: 缺字段 {miss}（口径真源=12 号卷 §5-3，缺字段=不可复跑）")
        verdict = str(ev.get("verdict"))
        if verdict and verdict not in FRESHNESS_VERDICTS:
            _err(errors, f"{tag}: verdict 非法 {verdict!r}（合法集={sorted(FRESHNESS_VERDICTS)}）")
        if verdict == "probe_failed":
            _err(
                errors,
                f"{tag}: probe_failed 一律不得放行 production——探测失败必须报红，"
                "禁把查不到写成无问题（本役宪法性纪律）",
            )
        elif verdict and verdict not in PRODUCTION_VERDICTS:
            _err(errors, f"{tag}: production 断言的 verdict 须 fresh/lagging（实际 {verdict!r}）")
        chan = str(ev.get("channel") or "")
        if _BAD_CHANNEL_RE.search(chan):
            _err(errors, f"{tag}: 证据通道 {chan!r} 属失败返回空串语义，不得作为任何证据（★坑1）")


def _check_anchor_format(errors: list[str], nid: str, anchor: Any) -> None:
    """锚形态：带前缀的标识符锚，或裸 `c<数字>_库.表` 形态的 CH 表锚（只放标识符，INV-1）。"""
    text = str(anchor)
    if not text:
        _err(errors, f"{nid}: 锚含空值")
        return
    if text.startswith(ANCHOR_PREFIXES):
        rest = text.split(":", 1)[1]
        if not rest or rest in {"/", "\\"}:
            _err(errors, f"{nid}: 锚 {text!r} 缺标识符")
        return
    parts = text.split(".")
    if len(parts) == 2 and parts[0][:1] == "c" and parts[0][1:2].isdigit():
        return
    _err(
        errors,
        f"{nid}: 锚形态非法（须 task:/slot:/file:/node:/table:/source:/status: 前缀或 <c数字>_db.table）: {text!r}",
    )


def _node_text_blob(node: dict[str, Any]) -> str:
    """把节点里承载语义的字符串收成一坨（machine 块=机生事实，不参与 INV-1 比对）。"""
    texts: list[str] = []

    def walk(obj: Any) -> None:
        """walk implementation."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "machine":
                    continue
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        elif isinstance(obj, str):
            texts.append(obj)

    walk({k: v for k, v in node.items() if k != "machine"})
    return "\n".join(texts)


def _is_prose(text: str) -> bool:
    """正文判定=含足量中文字符的描述性文本（标识符/表名/task_id 不属正文，引用它们合法）。"""
    return len(text) >= INV1_MIN_PROSE and sum(1 for ch in text if "一" <= ch <= "鿿") >= 10


def _prose_corpus(root: Path) -> list[str]:
    """从 tasks.yaml / data_asset_registry.yaml / 门禁册抽正文性长字符串（INV-1 比对集）。"""
    corpus: list[str] = []

    def harvest(obj: Any) -> None:
        """harvest implementation."""
        if isinstance(obj, dict):
            for v in obj.values():
                harvest(v)
        elif isinstance(obj, list):
            for v in obj:
                harvest(v)
        elif isinstance(obj, str) and _is_prose(obj):
            corpus.append(obj.strip())

    # 红队补洞 2026-09-24：INV-1 语料覆盖全部机生真源册（排班+任务+资产+两本门禁册），
    # 与图11/13 同纪律——任一册条目正文抄进本图节点即红。
    for rel in (
        TASKS_YAML_REL,
        SCHEDULE_YAML_REL,
        ASSET_REGISTRY_REL,
        "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml",
    ):
        path = root / rel
        if not path.exists():
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        harvest(doc)
    return corpus


def check_inv1(data: dict, root: Path | None = None) -> list[str]:
    """INV-1 引用不复制：节点正文禁逐字抄真源条目正文（只准存标识符与指针）。"""
    root = root or _REPO_ROOT
    corpus = _prose_corpus(root)
    if not corpus:
        return [f"INV-1 无法校验：真源正文集为空（{TASKS_YAML_REL} / {ASSET_REGISTRY_REL} 不可读）"]
    errors: list[str] = []
    for n in data.get("nodes", []) or []:
        if not isinstance(n, dict):
            continue
        blob = _node_text_blob(n)
        for prose in corpus:
            if prose in blob:
                errors.append(
                    f"{n.get('node_id')}: INV-1 复制侵权——节点正文逐字含真源条目"
                    f"正文（≥{INV1_MIN_PROSE} 字）: {prose[:40]}…"
                )
    return errors


def _repo_side_tables(root: Path) -> set[str]:
    """仓内可机判的表锚集合（tasks.yaml 目标表 + 注册表 datasets 物理名）。"""
    tables: set[str] = set()
    try:
        tasks = yaml.safe_load((root / TASKS_YAML_REL).read_text(encoding="utf-8"))["tasks"]
        tables |= {str(t["table"]) for t in tasks if t.get("table")}
    except Exception:  # noqa: BLE001 — 真源不可读时由调用侧的 CH 腿兜
        pass
    try:
        reg = yaml.safe_load((root / ASSET_REGISTRY_REL).read_text(encoding="utf-8"))
        for d in reg.get("datasets", []) or []:
            for key in ("physical_name", "table", "name", "location"):
                val = d.get(key)
                if isinstance(val, str) and "." in val:
                    tables.add(val.strip())
    except Exception:  # noqa: BLE001
        pass
    return tables


def _ch_table_resolver(root: Path) -> Callable[[set[str]], set[str]] | None:
    """CH 在册表解析器（只读、逐表 EXISTS TABLE）。

    本役纪律：**禁依赖 system.tables/parts/columns 枚举面**——09-25 03:55 实测一张坏表
    （187×0 字节部件）可把整套 system 枚举面打死，届时本函数返回 None、锚核验降 warn，
    绝不允许把"查不到"当成"没问题"（判红归判红，环境异常归环境异常）。
    """
    try:
        from zephyr.data.ch_config import ensure_ch_env_loaded

        ensure_ch_env_loaded()
        from zephyr.infrastructure.database_service import get_db_service

        conn = get_db_service().get_clickhouse_conn(role="reader")
        conn.execute("SELECT 1")  # 通道自检：失败即抛 ⇒ 整体降 warn

        def _resolve(wanted: set[str]) -> set[str]:
            known: set[str] = set()
            for t in sorted(wanted):
                if not _is_ch_table_anchor(t):
                    continue
                try:
                    rows = conn.execute(f"EXISTS TABLE {t}")  # noqa: S608 只读存在性探测，值来自图内锚
                    if rows and str(rows[0][0]) in ("1", "True"):
                        known.add(t)
                except Exception:  # noqa: BLE001 — 单表不可判 ⇒ 不入 known（调用侧记红/待裁）
                    continue
            return known

        return _resolve
    except Exception:  # noqa: BLE001 — 环境不可达由 allow_unverified 记账
        return None


def check_anchors(
    data: dict,
    root: Path | None = None,
    *,
    resolver: Callable[[set[str]], set[str]] | None = None,
    allow_unverified: bool = True,
) -> tuple[list[str], list[str]]:
    """数据锚在册实存：task_id/槽名/文件路径为硬判据，CH 表锚按可用腿核验。

    缺席表锚的唯一合法去处=在册 gap 节点（boundary.waiting_table_gaps/ghost_ref_gaps 所列）——
    查不到的表不许当在册数据引用混进 data_refs（禁把断供写成为 0 的正常态）。

    Args:
        data: 图 YAML 解析结果。
        root: 仓根（默认=本文件所在仓库/worktree）。
        resolver: 注入的表在册解析器（测试用桩；None 时尝试 CH 只读腿）。
        allow_unverified: CH 腿不可用时是否放行表锚（True=只 warn）。
    """
    root = root or _REPO_ROOT
    errors: list[str] = []
    warnings: list[str] = []
    task_ids: set[str] = set()
    slot_names: set[str] = set()
    try:
        task_ids = {
            t["task_id"]
            for t in yaml.safe_load((root / TASKS_YAML_REL).read_text(encoding="utf-8"))["tasks"]
            if t.get("task_id")
        }
    except Exception as exc:  # noqa: BLE001
        errors.append(f"task 锚无法校验：{TASKS_YAML_REL} 不可读（{exc}）")
    try:
        slot_names = set(yaml.safe_load((root / SCHEDULE_YAML_REL).read_text(encoding="utf-8"))["schedules"])
    except Exception as exc:  # noqa: BLE001
        errors.append(f"slot 锚无法校验：{SCHEDULE_YAML_REL} 不可读（{exc}）")

    boundary = data.get("boundary") or {}
    absent_ok = set(boundary.get("waiting_table_gaps") or {}) | set(boundary.get("ghost_ref_gaps") or {})
    table_anchors = {
        str(a)
        for n in data.get("nodes", []) or []
        if isinstance(n, dict)
        for a in (list(n.get("data_refs") or []) + list(n.get("source_anchors") or []))
        if _is_ch_table_anchor(str(a))
    }
    known_tables: set[str] | None = None
    if table_anchors:
        active = resolver if resolver is not None else _ch_table_resolver(root)
        if active is None:
            if allow_unverified:
                warnings.append(
                    f"CH 表锚 {len(table_anchors)} 个未核验（CH 不可达，"
                    f"按 allow_unverified 放行；禁把未核验读成已核验）"
                )
                known_tables = set(_repo_side_tables(root)) | table_anchors
            else:
                errors.append("CH 表锚核验不可用（CH 不可达且 allow_unverified=False）")
                known_tables = set(_repo_side_tables(root))
        else:
            known_tables = set(active(table_anchors)) | set(_repo_side_tables(root))

    for n in data.get("nodes", []) or []:
        if not isinstance(n, dict):
            continue
        nid = n.get("node_id", "<无 node_id>")
        anchors = list(n.get("source_anchors") or []) + list(n.get("data_refs") or [])
        mr = str(n.get("module_ref") or "").strip()
        if mr and "/" in mr and not mr.startswith("MOD-"):
            head, sep, tail = mr.rpartition(":")
            rel = head if (sep and tail.isdigit()) else mr
            if rel.startswith(_ANCHOR_DISK_EXEMPT):
                pass
            elif not (root / rel.replace("\\", "/")).exists():
                errors.append(f"{nid}: module_ref 路径锚磁盘实存检查失败（锚不存在）: {rel}")
        for a in anchors:
            text = str(a)
            if text.startswith("task:"):
                ident = text.split(":", 1)[1]
                if ident not in task_ids:
                    errors.append(f"{nid}: task 锚不在册 {ident!r}（tasks.yaml 查无此 task_id）")
            elif text.startswith("slot:"):
                ident = text.split(":", 1)[1]
                if ident not in slot_names and ident not in _special_slot_universe(data):
                    errors.append(f"{nid}: slot 锚不在册 {ident!r}（schedule.yaml 查无此槽名）")
            elif text.startswith("file:"):
                rel = text.split(":", 1)[1]
                if rel.startswith(_ANCHOR_DISK_EXEMPT):
                    continue
                if (
                    not (root / rel).exists()
                    and not Path(rel).is_absolute()
                    and not (root / rel.replace("\\", "/")).exists()
                ):
                    errors.append(f"{nid}: file 锚路径不存在 {rel!r}")
            elif _is_ch_table_anchor(text) and known_tables is not None and text not in known_tables:
                if text in absent_ok and n.get("node_type") == "gap":
                    continue  # 在册缺席表：只许以 gap 形态存在（CV-WAIT 已判其挂载点）
                errors.append(
                    f"{nid}: 数据锚指向不存在的表 {text!r}（CH 逐表 EXISTS 与仓内机生表集"
                    f"均查无；若确为缺席表，须挂到 boundary.waiting_table_gaps 的 gap 节点上）"
                )
        # slot_refs 在册实存：声称 slot_source=schedule 者必须能在 schedule.yaml（或 scheduler
        # 硬编码特殊槽面）查到槽名；schtasks 腿不在仓内真源面，改由 evidence 承担（禁凭空造槽名）。
        if str(n.get("slot_source") or "") == "schedule":
            for s in n.get("slot_refs") or []:
                if str(s) not in slot_names and str(s) not in _special_slot_universe(data):
                    errors.append(
                        f"{nid}: slot_refs 槽名不在册 {s!r}（slot_source=schedule，schedule.yaml 与特殊槽分派面均查无）"
                    )
    return errors, warnings


def _is_ch_table_anchor(text: str) -> bool:
    """裸 `c<数字>_库.表` 形态判定。"""
    parts = text.split(".")
    return len(parts) == 2 and parts[0][:1] == "c" and parts[0][1:2].isdigit() and all(parts)


def _special_slot_universe(data: dict) -> set[str]:
    """允许引用 scheduler 硬编码特殊槽（不在 schedule.yaml 的合法面）。"""
    out: set[str] = set()
    for n in data.get("nodes", []) or []:
        if not isinstance(n, dict):
            continue
        for slot, fact in ((n.get("machine") or {}).get("slots") or {}).items():
            if isinstance(fact, dict) and fact.get("special_dispatch"):
                out.add(slot)
    return out


def check_module_bus(data: dict, root: Path | None = None, warnings: list[str] | None = None) -> list[str]:
    """CV-BUS 的在册腿：module_id 是否真在 depgraph（PG 不可达=降 warn，不阻断）。"""
    root = root or _REPO_ROOT
    want = [str(n.get("module_id")) for n in data.get("nodes", []) or [] if isinstance(n, dict) and n.get("module_id")]
    missing = depgraph_missing_module_ids(sorted(set(want)), root)
    if missing is None:
        if warnings is not None:
            warnings.append("depgraph（PG）不可达：module_id 在册性核对降 warn（形态与投影判据仍硬过）")
        return []
    return [f"CV-BUS——module_id 不在 depgraph 在册：{m}（幽灵总线号，禁自造）" for m in missing]


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="图12 数据供给链图结构+双轴+锚+INV-1 校验（只读）")
    ap.add_argument("--map", default=str(DEFAULT_MAP), help="图 YAML 路径")
    ap.add_argument("--root", default=str(_REPO_ROOT), help="仓根（锚存在性解析用）")
    ap.add_argument("--skip-anchors", action="store_true", help="跳过数据锚在册实存核验")
    ap.add_argument("--skip-inv1", action="store_true", help="跳过 INV-1 复制侵权核验")
    ap.add_argument("--skip-bus", action="store_true", help="跳过 depgraph PG 在册核验")
    ap.add_argument("--strict-ch", action="store_true", help="CH 不可达时表锚不放行（判红；默认只 warn）")
    args = ap.parse_args()

    path = Path(args.map)
    if not path.exists():
        print(f"FAIL: 图文件不存在: {path}", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"FAIL: YAML 解析失败: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("FAIL: YAML 顶层非对象", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    warnings: list[str] = []
    errors = validate_structure(data, root, warnings)
    if not args.skip_inv1:
        errors.extend(check_inv1(data, root))
    if not args.skip_anchors:
        a_errors, a_warnings = check_anchors(data, root, allow_unverified=not args.strict_ch)
        errors.extend(a_errors)
        warnings.extend(a_warnings)
    if not args.skip_bus:
        errors.extend(check_module_bus(data, root, warnings))
    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"FAILED: {len(errors)} 个结构违规", file=sys.stderr)
        return 1
    counts = data.get("counts") or {}
    print(
        f"PASS: 结构校验通过（nodes={len(data['nodes'])} edges={len(data['edges'])} "
        f"production={counts.get('production_nodes')} structure="
        f"{counts.get('structure_nodes')} gap={counts.get('gap_nodes')} "
        f"骨架✅={counts.get('skeleton_ok_rows')}）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
