#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §trading-day-cycle-map
# [MODULE] scripts.governance.d5_architecture.validators.validate_trading_day_cycle_map
# create-guard-not-dup: 图13 48节点契约对账尺（图族新能力面：结构判据唯一真源，消费方=gate/align_all/对抗测试）；探针命中词 read yaml 只是 docstring 描述装图动作的片段，本件不实现 stale base 覆写禁止，与 trae_085 canonical 零重叠
# noqa: m11-perm-manual-legitimate  合法 manual CLI 校验器（ARCH-051 口径）：图13 对账尺人工/AI 按需调用，转正批落地兑现生成器 [CONSUMERS] 声明
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# [DEPENDENCIES] yaml; scripts.governance.d5_architecture.generators.generate_trading_day_cycle_map（骨架/在册/TDM 四面单一真源复用其 scan_*，禁复制；生成器模块自带 sys.path 自举）；config/trading_day_cycle_map.yaml（只读）
# [CONSUMERS] trading_day_cycle_map_gate（结构校验单一真源，MAP-ALIGNMENT subs）；align_all 第十一节挂轴；test_trading_day_cycle_map_adversarial.py（对抗尺，红优先）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 台账只读（禁写图/真源文件）；结构错误=exit 1 警告不阻断；validate_structure 纯内存判据（gate 只封阻塞语义，禁复制判据）；外部面（骨架状态列/depgraph 在册投影/TDM 在册/路径锚磁盘/INV-1 三真源）不可达=对应子检查降 warn 绝不升级 error（禁环境异常打死无辜提交）；判据真源=docs/_working/map_build/fig13_daycycle/00_skeleton.md §0-§3 与六图终局卷 §1 三层字段裁定；放宽任何检查项=改判据须与图 YAML+gate+对抗测试同批
# [MODIFY-GUARD] gap 节点增删须同步本件 NODE_UNIVERSE 与生成器 NODE_ORDER（生成器同款）；NODE_UNIVERSE/SEGMENT_OF_GAP 为契约常量，改动=改 48 节点契约须总包裁定
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)=结构/锚/INV-1 违规；SystemExit(2)=文件缺失或 YAML 解析失败或顶层非对象；外部面不可达=对应子检查降 warn（warnings 出参）绝不升级；本件零写入
# [TESTS] tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py（红组 A-M 70+ 例逐条钉死错误语义 + 绿组真图零 error + 生成器幂等与取时禁令）
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""图13 交易日循环全景图结构校验器——48 节点契约（44 环节 + 4 gap）判据单一真源。

形态照图12 已定稿件（``validate_data_supply_chain_map``）：``validate_structure(data, root=None,
warnings=None) -> list[str]`` 纯内存判据，gate 只封阻塞语义；``exit 1``=结构违规，``exit 2``=解析失败。

本图特有判据（三条硬让渡的字面化，骨架 §0.2/§1/§3）：
- **时刻值不搬家**：全树禁 cron 字面量（节点只存槽名/tn 名/entity_id/段名）；
- **决策内容不进图**：judgment_basis/strategy_refs/factor_refs 越域挂载即红（含嵌套键规避形态），
  判据唯一出路 tdm_refs（在册实存校验，伪造=TDM 幽灵交叉引用）；
- **管线内部结构不重画**：slot_source 三路指针（schedule/schtasks/dloop_stage）逐一在册实存，
  none 路夹带指针=绕开实存判定即红；
- **双轴不许混**：verified_scope=production 数与骨架 §2 状态列 ✅ 数**不多不少**——
  多了算谎（逐节点判）、少了算欠（反向判），production 必带可复跑 exec_evidence；
- **挂槽≠在跑**：wiring_status 是「槽挂着但没跑」唯一表达位，节点侧 idle_slot 标记与
  machine_facts 台账交叉核对；
- **缺席必须记账**：每环节 ready_gate 布尔必填——门格必带拒准入语义与真实存在的准入出边
  （CV-ADMIT 假门/空门判红），非门格必带 no_ready_gate_reason_zh；
- **缺口不许隐身**：CV-DANGLE 双向对账（台账对象必有节点认领、节点 task:/slot: 指针必在台账），
  gap 节点孤岛/洗成 stage/module_ref 伪装即红（CV-GAP）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

_VALDIR = str(Path(__file__).resolve().parent)
if _VALDIR not in sys.path:
    sys.path.insert(0, _VALDIR)

import yaml  # noqa: E402

# 四个外部面单一真源复用（生成器与校验器同函数同口径，禁复制——CLONEGUARD）；
# 生成器模块自带 sys.path 自举（_shared/src 两目录），本件只负责把 generators 目录挂上。
_GENERATORS_DIR = str(Path(__file__).resolve().parents[1] / "generators")
if _GENERATORS_DIR not in sys.path:
    sys.path.insert(0, _GENERATORS_DIR)
from generate_trading_day_cycle_map import (  # noqa: E402  import-integrity  sys.path 动态加载
    SEGMENTS,
    scan_module_id_index,
    scan_roster_module_ids,
    scan_skeleton_status,
    scan_tdm_node_ids,
)

DEFAULT_MAP = Path("config/trading_day_cycle_map.yaml")
_REPO_ROOT = Path(__file__).resolve().parents[4]

# ---------------------------------------------------------------------------
# 契约常量（48 节点全集；改动=改契约，须总包裁定并与生成器 NODE_ORDER 同批）
# ---------------------------------------------------------------------------
NODE_UNIVERSE: tuple[str, ...] = tuple(f"D13-{i:02d}" for i in range(1, 45)) + (
    "D13-G01",
    "D13-G02",
    "D13-G03",
    "D13-G04",
)
CONTRACT_UNIVERSE: frozenset[str] = frozenset(NODE_UNIVERSE)
GAP_NODES: tuple[str, ...] = ("D13-G01", "D13-G02", "D13-G03", "D13-G04")
_STAGE_NODES: tuple[str, ...] = tuple(f"D13-{i:02d}" for i in range(1, 45))
# 契约序（时点序）：倒序边（序号回接）必须声明反馈环
_NODE_ORDER_INDEX: dict[str, int] = {nid: i for i, nid in enumerate(NODE_UNIVERSE)}

# 段名全集经生成器 SEGMENTS 动态装载（词表 SSoT，禁字面量集合——GATE-VOCAB 同源）
_SEGMENT_IDS: frozenset[str] = frozenset(SEGMENTS)

# 段归属契约：编号落段（盘前 12／盘中 12／盘后 11／夜窗 9）+ gap 显式声明段
SEGMENT_OF_GAP: dict[str, str] = {"D13-G01": "A", "D13-G02": "B", "D13-G03": "C", "D13-G04": "B"}


def _expected_segment(nid: str) -> str | None:
    """编号契约落段；契约全集外的伪造编号返回 None（由越界判据负责报红，落段比较跳过）。"""
    if nid in SEGMENT_OF_GAP:
        return SEGMENT_OF_GAP[nid]
    if nid not in CONTRACT_UNIVERSE:
        return None
    idx = int(nid.split("-")[1])
    if idx <= 12:
        return "A"
    if idx <= 24:
        return "B"
    if idx <= 35:
        return "C"
    return "D"


# 值域（枚举口径=真图实态 + 骨架/作业簿判据；放宽=改判据须同批）
VERIFIED_SCOPE_ENUM = frozenset({"production", "structure"})
WIRING_STATUS_ENUM = frozenset({"wired", "partial", "unwired_no_caller", "unwired_slot_hollow"})
DOWNSTREAM_ACTION_ENUM = frozenset({"execute", "none", "auto_remediate", "alert_only", "detect_only", "orchestrate"})
MISS_POLICY_ENUM = frozenset({"rerun", "absorb", "none", "alert"})
BUILD_STATUS_ENUM = frozenset({"built", "partial", "pending"})
RED_REASON_ENUM = frozenset({"unwired", "broken_supply", "ghost_ref"})
SLOT_SOURCE_ENUM = frozenset({"schedule", "schtasks", "dloop_stage", "event", "none"})
# schema 0.3（转正批加性迁移）：血肉四字段分阶段开关
BLOOD_STAGE_ENUM = frozenset({"f1_pending", "f2_done"})
BLOOD_FOUR_FIELDS: tuple[str, ...] = ("purpose_tag", "casebooks", "trigger_facts", "consumers")
# schema 加性迁移白名单（0.2→0.3 纯加性：新增图头键 blood_stage/purpose_tags + 节点四字段，
# 不动既有键语义；破坏性迁移禁入本表）
ADDITIVE_SCHEMA_MIGRATIONS: dict[str, str] = {"0.2": "0.3"}
SUPPORTED_SCHEMA_VERSIONS = frozenset({"0.2", "0.3"})

REQUIRED_TOP: tuple[str, ...] = (
    "schema_version",
    "map_id",
    "name_zh",
    "generator",
    "ssot_note_zh",
    "laws",
    "boundary",
    "segments",
    "admission_edges",
    "nodes",
    "edges",
    "feedback_loops",
    "machine_facts",
    "counts",
)

# 键必须存在（值可为 null/空——删键=静默缺失判红，先例 CV-ADMIT/双轴面）
REQUIRED_NODE_PRESENT: tuple[str, ...] = (
    "node_id",
    "name_zh",
    "node_type",
    "segment",
    "decision_question",
    "note_zh",
    "build_status",
    "wiring_status",
    "downstream_action",
    "fallback",
    "ready_gate",
    "no_ready_gate_reason_zh",
    "confidence",
    "verified_scope",
    "module_id",
    "module_ref",
    "slot_source",
    "slot_refs",
    "schtasks_refs",
    "entity_refs",
    "dloop_stages",
    "tdm_refs",
    "gap_refs",
    "exec_evidence",
    "evidence",
    "source_anchors",
    "doc_refs",
)
# schema 0.3 起血肉四字段键进必存面（值可空——删键=静默缺失）
REQUIRED_NODE_PRESENT_03: tuple[str, ...] = REQUIRED_NODE_PRESENT + BLOOD_FOUR_FIELDS

# CV-L0：三层字段裁定一废止别名（同义异名十一件，残留即红）
LEGACY_FIELD_ALIASES: dict[str, str] = {
    "mech_note_zh": "note_zh",
    "clock_semantics_zh": "note_zh",
    "semantics_zh": "note_zh",
    "beat_zh": "cadence_zh",
    "miss_fallback_zh": "fallback",
    "degradation": "fallback",
    "silent_failover": "fallback",
    "ready_gate_zh": "ready_gate",
    "design_refs": "doc_refs",
    "doc_ref": "doc_refs",
    "dangling_refs": "gap_refs",
}

# 让渡二：判据字段越域挂载（含嵌套键规避形态，递归扫）
BANNED_JUDGMENT_KEYS: frozenset[str] = frozenset({"judgment_basis", "strategy_refs", "factor_refs"})

# 让渡一：cron 字面量（五段 cron 的数字-数字-星-星形态；时点语义只许存槽名/段名）
_CRON_RE = re.compile(r"\b[0-9]{1,2}\s+[0-9]{1,2}\s+\*\s+\*\s+[0-9][0-9*\-,/]*")
# exec_evidence 可复跑把手：复跑字样 / grep 命令 / 路径:行号 三形态之一
_RERUN_HANDLE_RE = re.compile(r"\.[A-Za-z0-9_]+:\d+")
# 路径锚锚体（剥 :行号 后的仓内相对路径）
_ANCHOR_PATH_RE = re.compile(r"^([^:]+):?\d*$")

_INV1_MIN_BODY = 25  # 真源正文整段复制判定的最小长度（短句引用不算侵权）


def _iter_string_values(obj: Any) -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for v in obj.values():
            out.extend(_iter_string_values(v))
    elif isinstance(obj, list):
        for x in obj:
            out.extend(_iter_string_values(x))
    elif isinstance(obj, str):
        out.append(obj)
    return out


def _iter_dict_keys(obj: Any) -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.append(str(k))
            out.extend(_iter_dict_keys(v))
    elif isinstance(obj, list):
        for x in obj:
            out.extend(_iter_dict_keys(x))
    return out


def _anchor_rel(ref: str) -> str:
    """module_ref/source_anchors 条目 → 仓内相对路径（剥 :行号）。"""
    m = _ANCHOR_PATH_RE.match(str(ref).strip())
    return (m.group(1) if m else str(ref)).replace("\\", "/")


def _read_yaml(root: Path, rel: str) -> Any:
    p = root / rel
    if not p.exists():
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 外部面不可解析=降级 None（调用方降 warn）
        return None


def _inv1_sources(root: Path) -> list[tuple[str, list[str]]]:
    """INV-1 三真源正文面：schedule.yaml 描述 / tasks.yaml capability / 门禁册条目正文。

    文件不可读=空列表（该真源跳过——外部面缺席不升级 error）。
    """
    out: list[tuple[str, list[str]]] = []
    sched = _read_yaml(root, "src/zephyr/data/config/schedule.yaml")
    if isinstance(sched, dict):
        bodies = [
            str((v or {}).get("description") or "").strip()
            for v in (sched.get("schedules") or {}).values()
            if isinstance(v, dict)
        ]
        out.append(("schedule.yaml", [b for b in bodies if len(b) >= _INV1_MIN_BODY]))
    tasks = _read_yaml(root, "src/zephyr/data/config/tasks.yaml")
    if isinstance(tasks, dict):
        bodies = [
            str((t or {}).get("capability") or "").strip() for t in tasks.get("tasks") or [] if isinstance(t, dict)
        ]
        out.append(("tasks.yaml", [b for b in bodies if len(b) >= _INV1_MIN_BODY]))
    greg = _read_yaml(root, "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml")
    if isinstance(greg, dict):
        bodies = []
        for g in greg.get("gates") or []:
            if not isinstance(g, dict):
                continue
            body = str(g.get("description") or "").strip()
            if len(body) >= _INV1_MIN_BODY and sum(1 for c in body if "一" <= c <= "鿿") >= 10:
                bodies.append(body)
        out.append(("gate_registry.yaml", bodies))
    return out


def validate_structure(
    data: dict[str, Any],
    root: Path | str | None = None,
    warnings: list[str] | None = None,
) -> list[str]:
    """图13 结构全量判据（纯内存；外部面经 root 只读，缺席降 warn）。

    返回 error 列表（空=通过）；warnings 出参承载降级注记与软提示。
    """
    errors: list[str] = []
    warns: list[str] = []
    root_p = Path(root) if root is not None else _REPO_ROOT

    # ---- 顶层必填键 ----
    if not isinstance(data, dict):
        return ["图文档顶层非对象（YAML 结构损坏）"]
    for k in REQUIRED_TOP:
        if k not in data:
            errors.append(f"缺顶层必填键: {k}")
    if not data.get("laws"):
        errors.append("laws 空置——骨架 §0.2 三条硬让渡必须落成 laws/boundary（撞车判定的边界=图本体边界）")

    # ---- schema 版本面（加性迁移白名单；破坏性版本=红）----
    ver_disk = str(data.get("schema_version"))
    if ver_disk not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(
            f"schema_version {ver_disk!r} 不受支持（支持域 {sorted(SUPPORTED_SCHEMA_VERSIONS)}，"
            f"加性迁移白名单 {ADDITIVE_SCHEMA_MIGRATIONS}；破坏性迁移禁入——须总包裁定）"
        )

    # ---- CV-BLOOD 血肉四字段分阶段（schema 0.3）----
    blood_stage = data.get("blood_stage")
    if "blood_stage" in data and (blood_stage is None or str(blood_stage) not in BLOOD_STAGE_ENUM):
        errors.append(f"blood_stage 非法: {blood_stage!r}（值域 f1_pending/f2_done——显式 null 同判自造口径）")
    purpose_tags = data.get("purpose_tags") or []
    tag_ids = {str(t.get("id")) for t in purpose_tags if isinstance(t, dict) and t.get("id")}
    if purpose_tags and not isinstance(purpose_tags, list):
        errors.append("purpose_tags 须为列表（图头图例标签枚举）")
    blood_active = blood_stage is not None and str(blood_stage) in BLOOD_STAGE_ENUM
    if blood_active and str(blood_stage) == "f2_done" and not tag_ids:
        errors.append("CV-BLOOD: f2_done 而图头 purpose_tags 空表（翻闸前置=图例标签 Owner 终审冻结入图头）")
    elif blood_active and str(blood_stage) != "f2_done":
        warns.append(
            "血肉未满（blood_stage=f1_pending 期：四字段以空/默认值在图不灌肉不贴标签——F2 批填满翻 f2_done 后 CV-BLOOD 转硬判）"
        )

    nodes = data.get("nodes") or []
    edges = data.get("edges") or []
    if not isinstance(nodes, list) or not isinstance(edges, list):
        errors.append("nodes/edges 非列表（YAML 结构损坏）")
        return errors

    by_id: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for n in nodes:
        if not isinstance(n, dict) or not n.get("node_id"):
            errors.append(f"节点缺 node_id 或非对象: {n!r:.80}")
            continue
        nid = str(n["node_id"])
        if nid in seen:
            errors.append(f"node_id 存在重复: {nid}")
        seen.add(nid)
        by_id[nid] = n

    # ---- 契约全集双向差集（越界=伪造环节、缺号=缺环节/缺口节点）----
    for nid in _STAGE_NODES:
        if nid not in by_id:
            errors.append(f"缺环节: {nid}（契约 44 环节缺一不可，骨架 §2）")
    for gid in GAP_NODES:
        if gid not in by_id:
            errors.append(f"缺环节/缺口节点: {gid}（GAP 契约 4 件缺一不可）")
    for nid in sorted(set(by_id) - CONTRACT_UNIVERSE):
        errors.append(f"{nid} 越出契约全集（D13-01..44 + D13-G01..G04 之外=伪造环节）")

    # ---- CV-BLOOD 节点级（f2_done 翻闸硬红面；by_id 就绪后判）----
    if blood_active and str(blood_stage) == "f2_done":
        for nid, n in sorted(by_id.items()):
            if n.get("node_type") == "gap":
                continue
            missing_blood = [k for k in BLOOD_FOUR_FIELDS if k not in n]
            if missing_blood:
                errors.append(f"CV-BLOOD: {nid} 血肉四字段缺键 {missing_blood}（f2_done 硬红——f1_pending 期降 warn）")
            pt = n.get("purpose_tag")
            if pt and tag_ids and str(pt) not in tag_ids:
                errors.append(f"CV-BLOOD: {nid} purpose_tag {pt!r} 不在图头 purpose_tags 枚举（禁贴图例外标签）")
            if str(n.get("verified_scope")) == "production" and not n.get("trigger_facts"):
                errors.append(f"CV-BLOOD: {nid} production 节点 trigger_facts 必非空（实测触发数=在产证据位）")

    # ---- 外部面（可缺席，缺席降 warn）----
    surfaces = (
        ((data.get("machine_facts") or {}).get("trigger_surfaces") or {})
        if isinstance(data.get("machine_facts"), dict)
        else {}
    )
    sched_slots = (
        set((surfaces.get("scheduler_slots") or {}).keys())
        if isinstance(surfaces.get("scheduler_slots"), dict)
        else set()
    )
    if not sched_slots:
        warns.append("机生面 scheduler_slots 缺席——schedule 槽在册实存检查降级跳过")
    scht = surfaces.get("registered_schtasks") or {}
    scht_names = set((scht or {}).get("task_names") or []) if isinstance(scht, dict) else set()
    if not scht_names:
        warns.append("机生面 registered_schtasks 缺席——schtasks 在册实存检查降级跳过")
    dloop = surfaces.get("dloop_phases") or {}
    stage_universe = set((dloop or {}).get("stage_universe") or []) if isinstance(dloop, dict) else set()
    sync_outliers = list((dloop or {}).get("sync_outliers") or []) if isinstance(dloop, dict) else []
    if not stage_universe:
        warns.append("机生面 dloop_phases.stage_universe 缺席——PHASE_STAGES 实存检查降级跳过")
    regent = surfaces.get("registry_entities") or {}
    entity_ids = set((regent or {}).get("referenced_entity_ids") or []) if isinstance(regent, dict) else set()
    unknown_entity_refs = list((regent or {}).get("unknown_refs") or []) if isinstance(regent, dict) else []

    roster = scan_roster_module_ids(root_p)
    if not roster:
        warns.append("depgraph 在册投影面不可读（CV-BUS 在册腿降级 warn，禁环境异常打死提交）")
    mid_index = scan_module_id_index(root_p)
    tdm_ids = scan_tdm_node_ids(root_p)
    if not tdm_ids:
        warns.append("TDM 在册面不可读（CV-TDM 降级 warn，热册可用性不耦合进图门禁）")

    skeleton = scan_skeleton_status(root_p)
    skeleton_ok = bool(skeleton)
    if not skeleton_ok:
        warns.append(
            "骨架状态列不可读（docs/_working/map_build/fig13_daycycle/00_skeleton.md 缺席或表形变更）"
            "——CV-DUAL 双轴腿降级 warn"
        )

    disk_face_ok = (root_p / "src").is_dir()
    if not disk_face_ok:
        warns.append("路径锚磁盘面不可达（root 非本仓形态）——磁盘实存检查降级 warn")
    inv1_sources = _inv1_sources(root_p)

    # ---- 逐节点判据 ----
    prod_ids: set[str] = set()
    wiring_counter: dict[str, int] = {}
    segment_counter: dict[str, int] = {}
    node_type_counter: dict[str, int] = {}
    slot_source_counter: dict[str, int] = {}
    module_id_count = 0
    idle_true_count = 0
    claimed_ledger_ids: set[str] = set()

    for nid, n in sorted(by_id.items()):
        # 缺必填键（键必须存在，值可 null——删键=静默缺失；schema 0.3 起加血肉四字段键）
        _required_node = REQUIRED_NODE_PRESENT_03 if ver_disk == "0.3" else REQUIRED_NODE_PRESENT
        for k in _required_node:
            if k not in n:
                if k == "slot_source":
                    errors.append(f"{nid} slot_source 必填（值域 schedule/schtasks/dloop_stage/event/none）")
                else:
                    errors.append(f"缺必填键 {k}: {nid}")

        # 四段段归属：必填 + 值域 + 编号落段
        seg = n.get("segment")
        expected_seg = _expected_segment(nid)
        if seg is None:
            errors.append(f"{nid} 四段段归属必填且∈{{A,B,C,D}}（骨架 §2 四段）")
        elif str(seg) not in _SEGMENT_IDS:
            errors.append(f"{nid} 四段段归属必填且∈{{A,B,C,D}}：got {seg!r}")
        elif expected_seg is not None and str(seg) != expected_seg:
            errors.append(f"{nid} 落段冲突：声明段 {seg}，编号契约落段应为 {expected_seg}")

        # CV-L0 旧名残留
        for legacy, canonical in LEGACY_FIELD_ALIASES.items():
            if legacy in n:
                errors.append(f"{nid} CV-L0 旧名残留：{legacy}（统一名应为 {canonical}——三层字段裁定一）")

        # 让渡二：判据字段越域挂载（递归，含嵌套键规避形态）
        banned_hits = sorted({k for k in _iter_dict_keys(n) if k in BANNED_JUDGMENT_KEYS})
        for k in banned_hits:
            errors.append(f"{nid} 越域挂载：{k}（让渡二——判据唯一出路 tdm_refs 引 TDM 节点，本图禁带判据字段）")

        # cadence_zh 双子键 + 长度
        cad = n.get("cadence_zh")
        if cad is not None:
            if not isinstance(cad, dict) or "declared" not in cad:
                errors.append(f"{nid} cadence_zh 须为 declared/observed 双子键 map（写成散文串即红）")
            else:
                if len(str(cad.get("declared") or "")) > 160:
                    errors.append(f"{nid} cadence_zh.declared 超 160 字：{str(cad.get('declared'))[:40]}…")

        dq = n.get("decision_question")
        if dq is not None and len(str(dq)) > 120:
            errors.append(f"{nid} decision_question 超 120 字（时序问题一句钉死）")

        # 值域枚举
        vs = n.get("verified_scope")
        if vs is not None and str(vs) not in VERIFIED_SCOPE_ENUM:
            errors.append(f"{nid} verified_scope 非法: {vs!r}（值域 production/structure）")
        ws = n.get("wiring_status")
        if ws is not None and str(ws) not in WIRING_STATUS_ENUM:
            errors.append(
                f"{nid} wiring_status 非法: {ws!r}（值域 wired/partial/unwired_no_caller/unwired_slot_hollow）"
            )
        act = n.get("downstream_action")
        if act is not None and str(act) not in DOWNSTREAM_ACTION_ENUM:
            errors.append(
                f"{nid} downstream_action 非法: {act!r}（五态 execute/none/auto_remediate/alert_only/detect_only/orchestrate——「看着」与「动手」不得混判）"
            )
        mp = n.get("miss_policy")
        if mp is not None and str(mp) not in MISS_POLICY_ENUM:
            errors.append(f"{nid} miss_policy 非法: {mp!r}（值域 rerun/absorb/none/alert——表A-A6 落格口径）")
        bs = n.get("build_status")
        if bs is not None and str(bs) not in BUILD_STATUS_ENUM:
            errors.append(f"{nid} build_status 非法: {bs!r}（值域 built/partial/pending）")
        rr = n.get("red_reason")
        if rr is not None and str(rr) not in RED_REASON_ENUM:
            errors.append(f"{nid} red_reason 非法: {rr!r}（值域 unwired/broken_supply/ghost_ref）")
        ss = n.get("slot_source")
        if ss is not None and str(ss) not in SLOT_SOURCE_ENUM:
            errors.append(f"{nid} slot_source 值域非法: {ss!r}（schedule/schtasks/dloop_stage/event/none 四路+无槽）")

        # slot_source 三路指针在册实存
        if ss is not None:
            slot_refs = n.get("slot_refs") or []
            scht_refs = n.get("schtasks_refs") or []
            stages = n.get("dloop_stages") or []
            if str(ss) == "schedule":
                if not slot_refs:
                    errors.append(f"{nid} slot_refs 为空——slot_source=schedule 须至少挂一槽（在册实存前提）")
                for r in slot_refs:
                    if sched_slots and str(r) not in sched_slots:
                        errors.append(
                            f"伪造 slot_source：{nid} slot_refs {r!r} 不在 schedule.yaml 槽全集（在册实存失败——文档说有实则无）"
                        )
            elif str(ss) == "schtasks":
                if not scht_refs:
                    errors.append(f"{nid} schtasks_refs 为空——slot_source=schtasks 须至少挂一 tn")
                for r in scht_refs:
                    if scht_names and str(r) not in scht_names:
                        errors.append(
                            f"伪造 slot_source：{nid} schtasks_refs {r!r} 不在计划任务声明/查询面（在册实存失败）"
                        )
            elif str(ss) == "dloop_stage":
                if not stages:
                    errors.append(f"{nid} dloop_stages 为空——slot_source=dloop_stage 须至少挂一段")
                for s in stages:
                    if stage_universe and str(s) not in stage_universe:
                        errors.append(f"伪造 slot_source：{nid} dloop_stages {s!r} 不在 PHASE_STAGES 实扫集合")
            elif str(ss) == "none":
                if slot_refs or scht_refs or stages:
                    errors.append(
                        f"{nid} 无槽环节（slot_source=none）夹带 schedule/schtasks/dloop_stage 指针——绕开在册实存判定即红"
                    )
            # event 路：无槽指针要求（事件驱动环节以 entity/doc_refs 承载，不强制槽指针）

        for r in n.get("entity_refs") or []:
            if entity_ids and str(r) not in entity_ids:
                errors.append(f"伪造 entity_ref：{nid} entity_refs {r!r} 不在排班资源册（在册实存失败）")
        for r in n.get("tdm_refs") or []:
            if tdm_ids and str(r) not in tdm_ids:
                errors.append(f"伪造 tdm_ref：{nid} tdm_refs {r!r} 不在 TDM 在册节点（幽灵交叉引用——CV-TDM）")

        # CV-BUS：module_id 必挂、来源唯一、禁自造
        mid = n.get("module_id")
        mref = n.get("module_ref")
        if mref and not mid:
            errors.append(f"CV-BUS: {nid} module_ref 有实现锚而 module_id 空（有码无号=红，查不到号须 red_reason）")
        if mid:
            module_id_count += 1
            if not str(mid).startswith("MOD-"):
                errors.append(
                    f"CV-BUS: {nid} module_id 非 MOD-* 形态: {mid!r}（总线号只能来自 depgraph 在册投影，禁自造）"
                )
            else:
                if roster and str(mid) not in roster:
                    errors.append(
                        f"CV-BUS: {nid} module_id {mid!r} 不在 depgraph 在册投影面（形态合法而号不在册同样判红）"
                    )
                if mref and mid_index:
                    rel = _anchor_rel(str(mref))
                    owner = mid_index.get(rel)
                    if owner and owner != str(mid):
                        errors.append(
                            f"CV-BUS: {nid} module_id 与在册面对不符：路径 {rel} 在册号={owner}，图挂={mid}（张冠李戴）"
                        )
            if not mref:
                errors.append(f"CV-BUS: {nid} 空挂总线——挂 {mid!r} 而无 module_ref 实现锚")
        if not mid and not rr:
            errors.append(f"module_id 为空必配 red_reason: {nid}（无号须写红因，禁静默）")

        # built 必有代码锚
        if str(bs) == "built" and not mref:
            errors.append(f"built 节点必须有 module_ref: {nid}")

        # confidence × verified_scope × evidence
        if str(vs) == "production":
            prod_ids.add(nid)
            if str(n.get("confidence")) != "verified":
                errors.append(f"{nid} production 必 verified（confidence={n.get('confidence')!r}）")
            exec_ev = n.get("exec_evidence") or []
            if not exec_ev:
                errors.append(f"{nid} production 必带 exec_evidence（分产证据不许空）")
            for it in exec_ev:
                text = str(it)
                if "复跑" not in text and "grep" not in text and not _RERUN_HANDLE_RE.search(text):
                    errors.append(f"{nid} exec_evidence 无可复跑把手（纯散文不构成分产证据）: {text[:50]}")
        if str(n.get("confidence")) == "verified" and not (n.get("evidence") or []):
            errors.append(f"{nid} verified 必带 evidence（实证不许空口）")

        # 缺席必须记账（骨架 §1 门④）
        fallback = n.get("fallback")
        if fallback is not None and str(fallback) == "":
            errors.append(f"{nid} fallback 不得为空串（无兜底须写 none:<理由>，空串≠声明）")
        gate = n.get("ready_gate")
        if gate is True:
            if not str(n.get("admission_denied_zh") or ""):
                errors.append(f"{nid} 拒准入语义缺失：ready_gate 门格必带 admission_denied_zh（拒准入语义须落在字面）")
            if not any(isinstance(a, dict) and a.get("from") == nid for a in data.get("admission_edges") or []):
                errors.append(f"CV-ADMIT: 就绪门 {nid} 无任何准入出边（空门——语义边只在散文里=红）")
        else:
            if "no_ready_gate_reason_zh" in n and not str(n.get("no_ready_gate_reason_zh") or ""):
                errors.append(f"{nid} no_ready_gate_reason_zh 空置——非门格须写明前置由谁承载（骨架 §1 门④）")

        # CV-GAP：缺口节点形态
        if nid in GAP_NODES:
            if n.get("node_type") != "gap":
                errors.append(f"契约编号为 gap 节点但 node_type={n.get('node_type')!r}: {nid}（洗成 stage=伪装已实现）")
            if n.get("module_ref"):
                errors.append(f"CV-GAP: gap 节点不该有 module_ref: {nid}（缺口挂实现锚=把缺口伪装成已实现件）")
            if not rr:
                errors.append(f"CV-GAP: gap 节点必带 red_reason: {nid}")
            if not any(isinstance(e, (list, tuple)) and nid in e for e in edges):
                errors.append(f"CV-GAP: 缺口节点 {nid} 不得孤岛（至少一条边挂进图体）")

        # 路径锚磁盘实存（外部面，缺席降 warn）
        if disk_face_ok:
            for a in n.get("source_anchors") or []:
                rel = _anchor_rel(str(a))
                if rel and not (root_p / rel).exists():
                    errors.append(f"路径锚磁盘实存检查失败: {a}（{nid}——文档说有实则无）")

        # 节点级 machine_facts：idle_slot 标记计数（与台账交叉核对）
        nmf = n.get("machine_facts") or {}
        if isinstance(nmf, dict) and isinstance(nmf.get("slot_facts"), dict):
            if nmf["slot_facts"].get("idle_slot") is True:
                idle_true_count += 1

        # CV-DANGLE 节点侧：task:/slot: 指针须在台账
        for r in n.get("gap_refs") or []:
            text = str(r)
            if text.startswith(("task:", "slot:")):
                claimed_ledger_ids.add(text)

        # 计数器
        wiring_counter[str(ws)] = wiring_counter.get(str(ws), 0) + 1
        segment_counter[str(seg)] = segment_counter.get(str(seg), 0) + 1
        node_type_counter[str(n.get("node_type"))] = node_type_counter.get(str(n.get("node_type")), 0) + 1
        slot_source_counter[str(ss)] = slot_source_counter.get(str(ss), 0) + 1

    # 在册实存失败台账腿：unknown_refs 必须为空
    for r in unknown_entity_refs:
        errors.append(f"在册实存失败：registry_entities.unknown_refs 非空 {r!r}（生成期已判幽灵，禁放行进图）")

    # 段序契约：dispatch 漂移
    for o in sync_outliers:
        errors.append(f"段序契约破损：dloop_phases.sync_outliers 非空 {o!r}（PHASE_STAGES 与 dispatch 漂移）")

    # CV-DUAL 双轴（骨架面可用才判）
    if skeleton_ok:
        ok_ids = {nid for nid, sym in skeleton.items() if sym == "✅"}
        extra = prod_ids - ok_ids
        missing = ok_ids - set(by_id) or ok_ids - prod_ids
        for nid in sorted(extra):
            errors.append(
                f"CV-DUAL 谎——verified_scope=production 但骨架状态列非 ✅: {nid}（多了算谎；骨架 §2 状态列=双轴唯一同源口径）"
            )
        if ok_ids - prod_ids:
            errors.append(
                f"CV-DUAL 欠——骨架 ✅ 环节未宣 production: {sorted(ok_ids - prod_ids)}（少了算欠，禁用降态让图变干净）"
            )
        if extra or ok_ids - prod_ids:
            errors.append(f"CV-DUAL 计数：图 production={len(prod_ids)} vs 骨架 ✅={len(ok_ids)}（双轴计数失衡）")

    # ---- 边判据 ----
    edge_set: set[tuple[str, str]] = set()
    for e in edges:
        if not isinstance(e, (list, tuple)) or len(e) != 2:
            errors.append(f"边形态非法（须 [from, to] 二元组）: {e!r:.60}")
            continue
        u, v = str(e[0]), str(e[1])
        if u not in by_id or v not in by_id:
            errors.append(f"边引用了不存在的节点: {u}->{v}")
            continue
        if u == v:
            errors.append(f"自环边: {u}->{v}")
        if (u, v) in edge_set:
            errors.append(f"重复边: {u}->{v}")
        edge_set.add((u, v))

    # 反馈环
    loops = data.get("feedback_loops") or []
    declared_loops: set[tuple[str, str]] = set()
    for lp in loops:
        if not isinstance(lp, dict):
            errors.append(f"反馈环形态非法（须 {{from,to,note}} 对象）: {lp!r:.60}")
            continue
        u, v = str(lp.get("from")), str(lp.get("to"))
        if u not in by_id or v not in by_id:
            errors.append(f"反馈环引用了不存在的节点: {u}->{v}")
            continue
        if not str(lp.get("note") or ""):
            errors.append(f"反馈环缺 note: {u}->{v}（段序/逆时点环须写明语义）")
        declared_loops.add((u, v))
    for u, v in sorted(edge_set):
        ou, ov = _NODE_ORDER_INDEX.get(u), _NODE_ORDER_INDEX.get(v)
        if ou is not None and ov is not None and ou > ov and (u, v) not in declared_loops:
            errors.append(f"未声明为反馈环的反向边: {u}->{v}（时点倒序/跨段回接边必须入 feedback_loops 声明）")

    # CV-ADMIT：声明拒准入边必须真实存在 + note 必填
    for a in data.get("admission_edges") or []:
        if not isinstance(a, dict):
            errors.append(f"admission_edges 形态非法（须 {{from,to,note_zh}} 对象）: {a!r:.60}")
            continue
        u, v = str(a.get("from")), str(a.get("to"))
        if not str(a.get("note_zh") or ""):
            errors.append(f"admission_edges 缺 note_zh: {u}->{v}（拒准入语义须落在字面）")
        if u in by_id and v in by_id and (u, v) not in edge_set:
            errors.append(f"CV-ADMIT: 声明的拒准入边 {u}->{v} 不在 edges（假门——声明而无边）")

    # ---- counts 一致性（机生面，禁散文改数）----
    counts = data.get("counts") or {}
    if isinstance(counts, dict):
        if counts.get("total_nodes") != len(nodes):
            errors.append(f"counts.total_nodes 漂移: 册 {counts.get('total_nodes')} vs 实算 {len(nodes)}")
        if counts.get("total_edges") != len(edges):
            errors.append(f"counts.total_edges 漂移: 册 {counts.get('total_edges')} vs 实算 {len(edges)}")
        if counts.get("by_segment") != segment_counter:
            errors.append(f"counts.by_segment 四段分布漂移: 册 {counts.get('by_segment')} vs 实算 {segment_counter}")
        if counts.get("by_node_type") != node_type_counter:
            errors.append(f"counts.by_node_type 漂移: 册 {counts.get('by_node_type')} vs 实算 {node_type_counter}")
        if counts.get("by_verified_scope") != {
            "production": len(prod_ids),
            "structure": len(nodes) - len(prod_ids),
        }:
            errors.append(
                f"counts.by_verified_scope 漂移: 册 {counts.get('by_verified_scope')} vs 实算 "
                f"{{'production': {len(prod_ids)}, 'structure': {len(nodes) - len(prod_ids)}}}"
            )
        if counts.get("by_wiring_status") != wiring_counter:
            errors.append(f"counts.by_wiring_status 漂移: 册 {counts.get('by_wiring_status')} vs 实算 {wiring_counter}")
        if counts.get("by_slot_source") != slot_source_counter:
            errors.append(
                f"counts.by_slot_source 漂移: 册 {counts.get('by_slot_source')} vs 实算 {slot_source_counter}"
            )
        mach = counts.get("machine") or {}
        if isinstance(mach, dict):
            mis = mach.get("module_id_scan") or {}
            if (
                isinstance(mis, dict)
                and "nodes_with_module_id" in mis
                and mis.get("nodes_with_module_id") != module_id_count
            ):
                errors.append(
                    f"counts.machine.module_id_scan 漂移: 册 {mis.get('nodes_with_module_id')} vs 实算 {module_id_count}"
                )
            for ghost in mach.get("dangling_unclaimed") or []:
                errors.append(
                    f"counts.machine.dangling_unclaimed 非空: {ghost!r}（生成期已判无处可查的落空对象，禁放行进图）"
                )

    # ---- CV-DANGLE 台账双向对账 ----
    dang = surfaces.get("dangling_objects") or {}
    if isinstance(dang, dict) and dang:
        entries = dang.get("entries") or []
        ledger_ids = {str(e.get("id")) for e in entries if isinstance(e, dict) and e.get("id")}
        for e in entries:
            if isinstance(e, dict) and not (e.get("owner_nodes") or []):
                errors.append(f"CV-DANGLE: 落空对象 {e.get('id')!r} 无归属环节（owner_nodes 空）")
        unclaimed = sorted(i for i in ledger_ids if i not in claimed_ledger_ids)
        for i in unclaimed:
            errors.append(f"CV-DANGLE: 落空对象无节点认领: {i}（缺口隐身——台账在册而节点侧不认账）")
        for nid, n in sorted(by_id.items()):
            for r in n.get("gap_refs") or []:
                text = str(r)
                if text.startswith(("task:", "slot:")) and ledger_ids and text not in ledger_ids:
                    errors.append(f"CV-DANGLE: {nid} gap_refs 引用台账在册外对象: {text}（伪造缺口或图未回生成）")
        dtot = dang.get("total")
        led_len = len(entries)
        if dtot != led_len:
            errors.append(f"dangling_total 漂移: 台账 total={dtot} vs entries={led_len}")
        cmach = (counts or {}).get("machine") or {}
        if isinstance(cmach, dict) and "dangling_total" in cmach and cmach.get("dangling_total") != led_len:
            errors.append(
                f"dangling_total 漂移: counts.machine.dangling_total={cmach.get('dangling_total')} vs entries={led_len}"
            )
        fake_slots = [str(x) for x in dang.get("fake_channel_slots") or []]
        idle_slots_counts = [str(x) for x in (cmach.get("idle_slots") or [])] if isinstance(cmach, dict) else []
        if sorted(fake_slots) != sorted(idle_slots_counts):
            errors.append(
                f"空转槽台账须同源：dangling_objects.fake_channel_slots={sorted(fake_slots)} vs "
                f"counts.machine.idle_slots={sorted(idle_slots_counts)}"
            )
        if idle_true_count != len(fake_slots):
            errors.append(
                f"idle_slot 真落空标记数不符：节点侧 idle_slot=True 共 {idle_true_count} vs 台账 fake_channel_slots {len(fake_slots)}"
                "（「槽挂着但没跑」唯一表达位=wiring_status/idle_slot 机生面，禁节点侧抹平）"
            )

    # ---- INV-1 复制侵权（排班两册 + 门禁册正文整段抄进节点）----
    node_text_faces = ("note_zh", "decision_question", "failure_visibility_zh", "admission_denied_zh")
    for label, bodies in inv1_sources:
        for body in bodies:
            for nid, n in sorted(by_id.items()):
                for face in node_text_faces:
                    if body and body in str(n.get(face) or ""):
                        errors.append(
                            f"INV-1 复制侵权：{nid} {face} 整段复制 {label} 正文（INV-1 只存标识符与指针，禁复制真源）"
                        )

    # ---- 让渡一：cron 字面量全树禁入 ----
    for text in _iter_string_values(data):
        m = _CRON_RE.search(text)
        if m:
            errors.append(
                f"cron 字面量进图（让渡一——时刻值不搬家，节点只存槽名/tn 名/entity_id/段名）: {m.group(0)!r} @ {text[:50]!r}"
            )
            break

    if warnings is not None:
        warnings.extend(warns)
    return errors


def main() -> int:  # noqa: C901  CLI 薄壳
    parser = argparse.ArgumentParser(description="图13 交易日循环全景图结构校验器（48 节点契约）")
    parser.add_argument(
        "--map", default=str(DEFAULT_MAP), help="图 YAML 路径（默认 config/trading_day_cycle_map.yaml）"
    )
    args = parser.parse_args()
    map_path = Path(args.map)
    if not map_path.exists():
        print(f"FAIL: 图文件不存在: {map_path}")
        return 2
    try:
        data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 解析失败=exit 2
        print(f"FAIL: 图 YAML 解析异常: {e}")
        return 2
    if not isinstance(data, dict):
        print("FAIL: 图文档顶层非对象")
        return 2
    warnings: list[str] = []
    errors = validate_structure(data, root=_REPO_ROOT, warnings=warnings)
    nodes_n = len(data.get("nodes") or [])
    print(f"[validate_trading_day_cycle_map] nodes={nodes_n} errors={len(errors)} warnings={len(warnings)}")
    for e in errors[:20]:
        print(f"  FAIL: {e}")
    for w in warnings[:10]:
        print(f"  WARN: {w}")
    if errors:
        print("结构违规：修图后重跑（机生面走生成器重生成，禁手改）")
        return 1
    print("PASS: 图13 结构校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
