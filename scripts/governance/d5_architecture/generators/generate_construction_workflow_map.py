# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §construction_workflow_map
# [MODULE] scripts.governance.d5_architecture.generators.generate_construction_workflow_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# [DEPENDENCIES] yaml；scripts.governance._shared.terminology_loader（get_category_map，
#   build_status 双语标签经术语真源，禁硬编码翻译字典）；
#   scripts.governance._shared.module_translation_loader（get_module_name_bilingual，
#   module_ref 的中英标签经模块翻译真源）；zephyr.shared.io.file_utils（safe_write_text
#   热写通道）；git（只读 show 取 HEAD 提交时间派生时间戳）；
#   scripts.governance.d5_architecture.validators.validate_construction_steps
#   （scan_skeleton_axes / scan_module_id_index / scan_gate_ids / load_verifiability_values /
#   _policy_step_heads —— 真源扫描与判据逻辑单一真源在校验器，本生成器禁复制判据）；
#   docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
#   （机读锚块宿主，未来态）；docs/_working/map_build/fig14_construction/
#   91_step_anchor_block_proposal.yaml（锚块回落来源，现态）
# [CONSUMERS] config/construction_workflow_map.yaml（唯一产出物）；
#   tests/governance/d5_architecture/test_construction_workflow_map_adversarial.py
#   （幂等实证直调 build_document）；总包排产（政策嵌块后以 --anchors-from policy 重生成）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 真源方向=锚块（政策内嵌块 ∨ 91 号提案件）→ 图 YAML 单向派生，禁手改图后不回生成；
# [MODIFY-GUARD] 环节契约/段分层/回边台账改动前先回写 docs/_working/map_build/fig14_construction/
#   00_skeleton.md 与政策锚块；产出图禁手改后不回生成
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 锚块两源皆不可用/政策未嵌块/提案件无 step_anchors=raise SystemExit 并报来源路径；
#   git 或册不可读=对应面记 unobserved 占位不崩；写盘 CAS 失败=返回码 1；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_construction_workflow_map_adversarial.py
#   锚块来源优先级：政策内嵌块（anchor_source=policy）→ 找不到则回落提案件
#   （anchor_source=proposal）并把全部环节显式列进 pending_anchors（防"忘了就绿"），
#   --anchors-from 可强制切换；两列口径不合并（骨架状态列→build_status/verified_scope，
#   骨架可机验列→verifiability，原始列值同存 skeleton_status/skeleton_verifiability 供 CV-STATE
#   反查）；handoff 节点 verifiability 恒 manual（簿03 反洗白口径，禁借图11 的 auto 抬分）；
#   laws/boundary/loops 属锚块内人工语义层，生成器原样搬运不改写；
#   幂等=同输入两次产出逐字节等（时间戳必经 --as-of 或 HEAD 提交时间派生，禁壁钟取时函数
#   ——RULE-SCHEMA-TZ）；计数只进 counts 字段不进散文；节点只存标识符与指针（INV-1，
#   禁复制政策正文）；中英标签必经既有翻译 loader（禁硬编码翻译字典）；
#   字段名一律 L0 统一名（note_zh/doc_refs）；骨架不可读=对应派生项置 null 并计入
#   machine_facts 的 missing 面（禁崩溃、禁凭记忆补数）
# [MODIFY-GUARD] 环节契约/段分层/回边台账改动前必须先回写
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读不到实载集合必抛，禁降级为'无冲突'
# [TESTS] 见同批 tests/ 下 canary 件
#   docs/_working/map_build/fig14_construction/00_skeleton.md（本图唯一收敛基准）与政策锚块；
#   产出物 config/construction_workflow_map.yaml 禁手改后不回生成（counts 一致性校验判红）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 锚块不可解析=SystemExit(2) 并报来源路径；真源缺失=对应 machine_fact
#   记 {"exists": false} 不崩溃；safe_write_text CAS 失败=返回码 1；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_construction_workflow_map_adversarial.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_construction_workflow_map.py — AI 施工升级流图（图14）生成器。

域（骨架一句话）：一个施工任务从"冷启动+文档审查"到"验收+全景图转正"的任务序与每步的
可验锚——不管改动如何到达 dev（归图11），不管运行时模块归属（归 GOMAP）。

真源方向（本图第④门的落地形态）：
  政策 MD 内嵌机读锚块（`# <<<CONSTRUCTION_STEP_ANCHORS>>>` … `# >>>CONSTRUCTION_STEP_ANCHORS<<<`）
  = 唯一真源；本生成器抽块 → 派生 `config/construction_workflow_map.yaml`。
  政策尚未嵌块期间回落 `91_step_anchor_block_proposal.yaml`（提案件），图里标
  `anchor_source: proposal` 且把 17 个环节全量写进 `pending_anchors`（欠账显式化，禁静默）。

两层结构（照图 11/图 9 母版，机生优先 + 静态清单禁手工维护）：
  1. 机生层：骨架 §1 两列实扫（状态/可机验）+ depgraph 投影在册 module_id + 门禁两册
     gate_id 集合 + verifiability 受控词表值集 + 幽灵引用面重扫（在册可证部分）+
     政策 Step 段与 §2.3 矩阵行集
  2. 锚块层（人工语义，经校验器判据钉住）：环节名/段/角色/decision_question/note_zh/
     exec_source/gates/executable/cli_anchors/docs/rollback_to/evidence/red_findings +
     gap 节点 + laws/boundary/loops 台账

CLI:
    python scripts/governance/d5_architecture/generators/generate_construction_workflow_map.py
    python ... --dry-run                       # 只打印摘要，零写入
    python ... --anchors-from policy|proposal  # 强制锚块来源
    python ... --as-of 2026-09-25T12:00:00+08:00
"""

from __future__ import annotations

import argparse
import itertools
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[4]
_GOV_DIR = str(next(p for p in _THIS.parents if (p / "_shared").exists()))
_VALIDATORS_DIR = str(_REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "validators")
for _p in (_GOV_DIR, _VALIDATORS_DIR, str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.module_translation_loader import get_module_name_bilingual  # noqa: E402
from _shared.terminology_loader import (
    get_category_map,  # noqa: E402  # noqa: import-integrity  sys.path 注入的 _shared 包（仓库根自举前置，非包路径错装）
)
from d5_architecture.generators._common import (  # noqa: E402  # noqa: import-integrity  sys.path 注入的 governance 包
    head_commit_time,
    serialize_map_document,
)
from validate_construction_steps import (  # noqa: E402  # noqa: import-integrity  sys.path 动态加载的本地判据单一真源模块
    DEFAULT_POLICY,
    GAP_NODES,
    STEP_UNIVERSE,
    _policy_matrix_rows,
    load_verifiability_values,
    scan_fig11_node_ids,
    scan_gate_ids,
    scan_module_id_index,
    scan_skeleton_axes,
)

OUTPUT_PATH = _REPO_ROOT / "config" / "construction_workflow_map.yaml"
_PROPOSAL_REL = "docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml"
_SKELETON_REL = "docs/_working/map_build/fig14_construction/00_skeleton.md"
_MARK_BEGIN = "# <<<CONSTRUCTION_STEP_ANCHORS>>>"
_MARK_END = "# >>>CONSTRUCTION_STEP_ANCHORS<<<"
# 幽灵脚本引用面重扫的声明口径（写进 machine_facts，读数与口径同件可复核）
_GHOST_SCAN_WORD = "ide_health"
_GHOST_SCAN_DIRS = ("docs/01_policies_and_standards", "docs/03_modules", "src", "scripts", "tests", "config", ".trae")
_GHOST_SCAN_EXCLUDE = ("docs/_working", "docs/_archive", "__pycache__", ".runtime")
_GHOST_CATALOG_DIR = "docs/01_policies_and_standards/_registry/catalogs"

BUILD_STATUS_ZH_CATEGORY = "build_status"


def strip_fence(block: str) -> str:
    """去掉锚块外围的 ```yaml 围栏（政策 MD 里以 fenced block 承载）。"""
    lines = [l for l in block.split("\n") if not l.strip().startswith("```")]
    return "\n".join(lines)


def load_anchor_block(root: Path, anchors_from: str | None = None) -> tuple[str, dict[str, Any], str]:
    """锚块装载：政策内嵌块（未来态）优先，回落 91 号提案件（现态）。

    返回 (anchor_source, block, origin_path)。两侧解析出的 block 结构完全同构
    （step_anchors/gap_anchors/loops/laws/boundary/matrix_gaps），故图侧派生零分支。
    """
    policy_path = root / DEFAULT_POLICY
    if anchors_from in (None, "policy") and policy_path.exists():
        text = policy_path.read_text(encoding="utf-8", errors="replace")
        if _MARK_BEGIN in text and _MARK_END in text:
            raw = text.split(_MARK_BEGIN, 1)[1].split(_MARK_END, 1)[0]
            block = yaml.safe_load(strip_fence(raw)) or {}
            if isinstance(block, dict) and block.get("step_anchors"):
                return "policy", block, str(DEFAULT_POLICY)
    if anchors_from == "policy":
        raise SystemExit(f"[ERROR] 政策内未找到机读锚块（{DEFAULT_POLICY}）；嵌块前请用 --anchors-from proposal")
    prop = root / _PROPOSAL_REL
    if not prop.exists():
        raise SystemExit(f"[ERROR] 锚块两个来源都不可用：政策未嵌块且提案件缺失（{prop}）")
    block = yaml.safe_load(prop.read_text(encoding="utf-8")) or {}
    if not isinstance(block, dict) or not block.get("step_anchors"):
        raise SystemExit(f"[ERROR] 锚块提案件解析失败或无 step_anchors: {prop}")
    return "proposal", block, _PROPOSAL_REL


def scan_ghost_reference_surface(root: Path) -> dict[str, Any]:
    """幽灵脚本引用面重扫（在册可证部分=注册表册内命中，其余按声明口径的广度读数）。

    口径全部写进返回值：扫描目录集/排除段/匹配 token，读数与口径同件可复核（INV-1
    只挂计数与文件相对路径，禁复制条目正文）。
    """
    files: list[str] = []
    occurrences = 0
    catalogs: dict[str, int] = {}
    for base in _GHOST_SCAN_DIRS:
        b = root / base
        if not b.exists():
            continue
        for p in sorted(b.rglob("*")):
            if not p.is_file() or p.suffix not in (".py", ".yaml", ".yml", ".md", ".ps1"):
                continue
            rel = p.relative_to(root).as_posix()
            if any(rel.startswith(x) for x in _GHOST_SCAN_EXCLUDE):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001 — 读不出=不计入（口径里如实记）
                continue
            n = text.count(_GHOST_SCAN_WORD)
            if not n:
                continue
            files.append(rel)
            occurrences += n
            if rel.startswith(_GHOST_CATALOG_DIR) and "_archive" not in rel:
                catalogs[rel] = n
    return {
        "token": _GHOST_SCAN_WORD,
        "scanned_dirs": list(_GHOST_SCAN_DIRS),
        "excluded_prefixes": list(_GHOST_SCAN_EXCLUDE),
        "referencing_files": len(files),
        "occurrences": occurrences,
        "in_catalog_files": len(catalogs),
        "in_catalog_occurrences": sum(catalogs.values()),
        "in_catalog_breakdown": catalogs,
    }


def _step_node(
    a: dict[str, Any], sk: dict[str, str], module_index: dict[str, str], build_status_zh: dict[str, Any]
) -> dict[str, Any]:
    """单环节节点装配（锚块语义 + 骨架两列实扫 + depgraph 投影在册号）。"""
    nid = a["step_id"]
    status = sk.get("status") or None
    raw_mv = sk.get("verifiable") or None
    build_status = {"✅": "built", "🔨": "partial", "⬜": "pending"}.get(status or "", a.get("build_status"))
    role = "handoff" if sk.get("role") == "交接" else "internal"
    verifiability = {"yes": "automated", "partial": "inspection", "no": "manual"}.get(
        raw_mv or "", a.get("verifiability")
    )
    if role == "handoff" and verifiability in ("automated", "inspection"):  # noqa: gate-vocab  簿03反洗白域规则：handoff环节禁自证automated/inspection（比较词表值非枚举硬编码）
        verifiability = "manual"  # 簿03 反洗白：handoff 不借图11 的 auto 抬本图分数
    scope = {"✅": "production", "🔨": "structure"}.get(status or "")
    mod_ref = a.get("module_ref")
    mod_id = module_index.get(str(mod_ref).split(":")[0]) if mod_ref else None
    gap_ids = [g.get("gap_id") for g in (a.get("_gap_refs") or [])]
    node: dict[str, Any] = {
        "node_id": nid,
        "name_zh": a["name_zh"],
        "segment": sk.get("segment") or a["segment"],
        "node_type": "stage",
        "decision_question": a["decision_question"],
        "note_zh": a["note_zh"],
        "build_status": build_status,
        "build_status_zh": build_status_zh.get(build_status, build_status),
        "confidence": "verified" if status in ("✅", "🔨") else "untested",
        "verified_scope": scope,
        "evidence": list(a.get("evidence") or []),
        "module_id": mod_id,
        "module_ref": mod_ref,
        "source_anchors": [a.get("policy_anchor")]
        + [f"{x}" for x in (a.get("executable") or [])]
        + [f"{c.get('script')}#{c.get('option')}" for c in (a.get("cli_anchors") or [])]
        + [f"gate:{g}" for g in (a.get("gates") or [])],
        "doc_refs": [f"{DEFAULT_POLICY}#{a.get('policy_step')}", f"{_SKELETON_REL} §1 {nid}"]
        + [f"{d.get('path')}" + (f"#{d['symbol']}" if d.get("symbol") else "") for d in (a.get("docs") or [])],
        "data_refs": list(a.get("data_refs") or []),
        "store_refs": list(a.get("store_refs") or []),
        "runtime_refs": list(a.get("runtime_refs") or []),
        "verifiability": verifiability,
        "anchor_kind": a.get("anchor_kind"),
        "exec_source": a.get("exec_source"),
        "gates": list(a.get("gates") or []),
        "executable": list(a.get("executable") or []),
        "cli_anchors": list(a.get("cli_anchors") or []),
        "docs": list(a.get("docs") or []),
        "role": role,
        "handoff_to": list(a.get("handoff_to") or []),
        "order": a.get("order"),
        "conditional": bool(a.get("conditional")),
        "trigger_when": a.get("trigger_when"),
        "rollback_to": list(a.get("rollback_to") or []),
        "max_rounds_ref": a.get("max_rounds_ref"),
        "red_findings": list(a.get("red_findings") or []),
        "gap_refs": [g for g in gap_ids if g],
        "red_reason": a.get("red_reason"),
        "wiring_status": a.get("wiring_status"),
        "fallback": a.get("fallback"),
        "invalidation": a.get("invalidation"),
        "policy_step": a.get("policy_step"),
        "policy_anchor": a.get("policy_anchor"),
        "sub_workflow": a.get("sub_workflow"),
        "human_gate": a.get("human_gate"),
        "skeleton_status": status,
        "skeleton_verifiability": raw_mv,
    }
    if a.get("trigger_when") is not None and not a.get("conditional"):
        node["trigger_when"] = None
    if node["module_ref"] and mod_id is None:
        node["red_reason"] = node.get("red_reason") or "ghost_ref"
        node["module_ref"] = None  # 投影查无在册号 ⇒ 宁可不挂也不空挂总线（CV-BUS）
    if a.get("exec_evidence"):
        node["exec_evidence"] = list(a["exec_evidence"])
    if node["module_ref"]:
        label = get_module_name_bilingual(str(node["module_ref"]).split(":")[0])
        if label:
            node["module_label_bilingual"] = label
    return node


def _gap_node(g: dict[str, Any], host: dict[str, Any], order: int) -> dict[str, Any]:
    """gap 节点装配（"文档说有实则没有"的显性化；无实现代码可挂⇒module 双 null+red_reason）。"""
    node: dict[str, Any] = {
        "node_id": g["gap_id"],
        "name_zh": g["name_zh"],
        "segment": host.get("segment"),
        "node_type": "gap",
        "decision_question": g["decision_question"],
        "note_zh": g["note_zh"],
        "build_status": "pending",
        "confidence": "verified",
        "verified_scope": "structure",
        "evidence": list(g.get("evidence") or []),
        "module_id": None,
        "module_ref": None,
        "source_anchors": list(g.get("source_anchors") or [f"{DEFAULT_POLICY}#{host.get('policy_step')}"]),
        "doc_refs": list(g.get("doc_refs") or []),
        "data_refs": [],
        "store_refs": [],
        "runtime_refs": [],
        "verifiability": "manual",
        "anchor_kind": "none",
        "exec_source": None,
        "gates": [],
        "executable": [],
        "cli_anchors": [],
        "docs": [],
        "role": "internal",
        "handoff_to": [],
        "order": order,
        "conditional": False,
        "trigger_when": None,
        "rollback_to": [],
        "max_rounds_ref": None,
        "red_findings": [g["finding"]] if g.get("finding") else [],
        "host_steps": [g["host_step"]] if g.get("host_step") else list(g.get("host_steps") or []),
        "red_reason": g.get("red_reason"),
        "wiring_status": "unwired_no_caller",
        "fallback": None,
        "invalidation": "对应政策锚被补齐/幽灵件复活 ⇒ 本 gap 节点作废，须回写骨架后重生成",
        "policy_step": None,
        "policy_anchor": None,
        "sub_workflow": None,
        "human_gate": None,
        "skeleton_status": None,
        "skeleton_verifiability": None,
    }
    for k in ("ghost_refs", "ghost_cli_anchors", "ghost_options", "mismatch_anchors", "ghost_doc_anchor"):
        if g.get(k):
            node[k] = g[k]
    return node


def build_layers(block: dict[str, Any], skeleton: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    """段分层：值集取骨架 §1 段列实扫（骨架=契约），顺序按环节 order 首现序。"""
    seen: list[str] = []
    for a in sorted(block.get("step_anchors") or [], key=lambda x: x.get("order", 0)):
        seg = (skeleton.get(a["step_id"], {}) or {}).get("segment") or a.get("segment")
        if seg and seg not in seen:
            seen.append(seg)
    spans = {
        "前置": "起=接到施工任务；止=任务文档可施工",
        "判定": "起=可施工文档；止=要不要动架构与方案是否挖干",
        "设计登记": "起=方案定稿；止=depgraph 设计态 + 全图对齐 + 前端真源盘点",
        "施工": "起=登记通过；止=落码完成（含子 SOP 引用）",
        "验收": "起=落码；止=循环验收归零 + 长清单审查结论",
        "文档": "起=审查通过；止=施工文档与代码对齐",
        "文档转正": "起=文档对齐；止=全景图双态流转完成",
        "落地收尾": "起=流转完成；止=任务终态（机制归图11，本图只挂交接）",
    }
    return [
        {"layer_id": s, "name_zh": f"{s}段", "span_zh": spans.get(s, f"值集取骨架 §1 段列实扫（{s}）")} for s in seen
    ]


def build_document(as_of: str, root: Path, anchors_from: str | None = None) -> dict[str, Any]:
    """组装图文档：锚块语义层 ⊕ 机生 machine_facts（结构契约见校验器 validate_structure）。"""
    anchor_source, block, origin = load_anchor_block(root, anchors_from)
    skeleton = scan_skeleton_axes(root)
    module_index = scan_module_id_index(root)
    gate_ids = scan_gate_ids(root)
    verif_values = load_verifiability_values(root, None)
    fig11_ids = scan_fig11_node_ids(root)
    build_status_zh = get_category_map(BUILD_STATUS_ZH_CATEGORY) or {}

    steps = sorted(block.get("step_anchors") or [], key=lambda x: x.get("order", 0))
    gaps = list(block.get("gap_anchors") or [])
    # 环节 ↔ gap 归属（host_step / host_steps 两种形态都收）
    host_to_gaps: dict[str, list[str]] = {}
    for g in gaps:
        hosts = [g.get("host_step")] if g.get("host_step") else list(g.get("host_steps") or [])
        g["_hosts"] = [h for h in hosts if h]
        for h in g["_hosts"]:
            host_to_gaps.setdefault(h, []).append(g["gap_id"])

    nodes: list[dict[str, Any]] = []
    for a in steps:
        sk = skeleton.get(a["step_id"], {})
        a["_gap_refs"] = [{"gap_id": gid} for gid in host_to_gaps.get(a["step_id"], [])]
        node = _step_node(a, sk, module_index, build_status_zh)
        nodes.append(node)
    step_ids = [n["node_id"] for n in nodes]
    for g in gaps:
        host = next(
            (n for n in nodes if n["node_id"] == (g["_hosts"] or [None])[0]),
            {"segment": nodes[0]["segment"], "policy_step": None},
        )
        nodes.append(_gap_node(g, host, len(STEP_UNIVERSE) + GAP_NODES.index(g["gap_id"]) + 1))

    edges: list[list[str]] = [[a, b] for a, b in itertools.pairwise(step_ids)]  # B905/RUF007 落地整改（语义等值）
    for g in gaps:
        for h in g["_hosts"]:
            if h in step_ids:
                edges.append([h, g["gap_id"]])

    loops = [dict(l) for l in (block.get("loops") or [])]
    notes = {l.get("loop_id"): l.get("note_zh", "") for l in loops}
    feedback: list[dict[str, Any]] = []
    for n in nodes:
        for tgt in n.get("rollback_to") or []:
            lid = next(
                (
                    l.get("loop_id")
                    for l in loops
                    if l.get("from") == n["node_id"]
                    and l.get("to") == tgt
                    and str(l.get("kind", "")).startswith("in_graph")
                ),
                None,
            )
            feedback.append(
                {
                    "from": n["node_id"],
                    "to": tgt,
                    "loop_id": lid,
                    "note": notes.get(lid, "") or f"{n['node_id']} 失败回 {tgt}",
                }
            )

    pending_anchors = list(step_ids) if anchor_source == "proposal" else []
    skeleton_counts: dict[str, int] = {}
    for v in skeleton.values():
        skeleton_counts[v["status"]] = skeleton_counts.get(v["status"], 0) + 1
    mv_counts: dict[str, int] = {}
    for v in skeleton.values():
        mv_counts[v["verifiable"]] = mv_counts.get(v["verifiable"], 0) + 1

    def _dist(field: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for n in nodes:
            k = str(n.get(field))
            out[k] = out.get(k, 0) + 1
        return {k: out[k] for k in sorted(out)}

    policy_text = ""
    pp = root / DEFAULT_POLICY
    if pp.exists():
        policy_text = pp.read_text(encoding="utf-8", errors="replace")
    heads = sorted(set(re.findall(r"^### Step\s+(\S+)\s*·", policy_text, re.M)))
    matrix_rows = sorted(set(_policy_matrix_rows(policy_text)))
    ghost = scan_ghost_reference_surface(root)
    unresolvable_gates = sorted({g for n in nodes for g in (n.get("gates") or [])} - gate_ids)

    doc: dict[str, Any] = {
        "schema_version": "0.1",
        "map_id": "construction_workflow_map",
        "name_zh": "AI 施工升级流图",
        "nickname": "施工升级流",
        "effective_from": "2026-09-24",  # 骨架 §1 定稿日（人工层常量，非运行时取时）
        "markets": ["cn_a"],
        "generator": "scripts/governance/d5_architecture/generators/generate_construction_workflow_map.py",
        "generated_at": as_of,
        "anchor_source": anchor_source,
        "anchor_block_origin": origin,
        "derived_from": str(DEFAULT_POLICY),
        "ssot_note_zh": (
            "真源方向：政策 MD 内嵌机读锚块（唯一真源）→ 本图 YAML（派生件，禁手改后不回生成）。"
            f"本轮锚块来源 anchor_source={anchor_source}（{origin}）；政策未嵌块期间 17 个环节"
            "全量记入 pending_anchors，欠账显式化禁静默。\n"
            "字段分层（六图终局卷 §1 裁定一）：L0 通用层统一名 note_zh/doc_refs；L1 纵轴层本图取用 "
            "wiring_status/red_reason/fallback/invalidation/gap_refs；L2 图专属层字段清单="
            "verifiability/anchor_kind/exec_source/gates/executable/cli_anchors/docs/policy_step/"
            "policy_anchor/role/handoff_to/conditional/trigger_when/rollback_to/max_rounds_ref/"
            "red_findings/sub_workflow/human_gate/skeleton_status/skeleton_verifiability。\n"
            "双轴口径（六图终局卷 §3）：verified_scope=production ⇔ 骨架 §1 状态列 ✅（6 个，多了算谎"
            "少了算欠），structure=🔨 环节 + gap 节点；两列独立不合并——build_status 取状态列、"
            "verifiability 取可机验列（值集动态取 verifiability 受控词表），原始列值另存 "
            "skeleton_status/skeleton_verifiability 供 CV-STATE 反查。handoff 节点 verifiability 恒 "
            "manual（簿03 反洗白口径：禁借图11 的 auto 结论抬本图分数）。\n"
            "gap 节点 D14-G01~G12 取骨架 §1 红条目点名册的『文档说有、实则没有』9 条 + 幽灵脚本"
            "引用面在册可证部分 + 前端真源路径双份嫌疑 1 条，全部只挂标识符与复跑命令（INV-1）；"
            "无实现代码可挂 ⇒ module_id/module_ref 双 null + red_reason 必填。"
        ),
        "laws": list(block.get("laws") or []),
        "boundary": list(block.get("boundary") or []),
        "layers": build_layers(block, skeleton),
        "nodes": nodes,
        "edges": edges,
        "feedback_loops": feedback,
        "loops": loops,
        "pending_anchors": pending_anchors,
        "machine_facts": {
            "skeleton_status_scan": {
                "source": _SKELETON_REL,
                "steps_scanned": len(skeleton),
                "by_symbol": {k: skeleton_counts[k] for k in sorted(skeleton_counts)},
                "by_machine_verifiable": {k: mv_counts[k] for k in sorted(mv_counts)},
            },
            "anchor_block": {
                "source": anchor_source,
                "origin": origin,
                "step_anchors": len(steps),
                "gap_anchors": len(gaps),
                "loops_declared": len(loops),
            },
            "policy_step_heads": {"count": len(heads), "values": heads},
            "policy_matrix_rows": {
                "count": len(matrix_rows),
                "values": matrix_rows,
                "closure_diff": {
                    "heads_minus_rows": sorted(set(heads) - set(matrix_rows)),
                    "rows_minus_heads": sorted(set(matrix_rows) - set(heads)),
                },
            },
            "verifiability_vocabulary": {
                "source": "docs/01_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml",
                "values": sorted(verif_values),
            },
            "gate_face": {
                "gate_ids_scanned": len(gate_ids),
                "cited_gate_ids": len({g for n in nodes for g in (n.get("gates") or [])}),
                "unresolvable_gate_ids": unresolvable_gates,
            },
            "module_id_scan": {
                "nodes_with_module_id": sum(1 for n in nodes if n.get("module_id")),
                "nodes_with_module_ref": sum(1 for n in nodes if n.get("module_ref")),
                "nodes_null_module_id": sum(1 for n in nodes if not n.get("module_id")),
            },
            "handoff_face": {
                "fig11_ids_scanned": len(fig11_ids),
                "handoff_nodes": sum(1 for n in nodes if n.get("role") == "handoff"),
                "handoff_refs": len({h for n in nodes for h in (n.get("handoff_to") or [])}),
            },
            "ghost_reference_surface": ghost,
        },
        "counts": {
            "total_nodes": len(nodes),
            "total_steps": sum(1 for n in nodes if n["node_type"] == "stage"),
            "total_gaps": sum(1 for n in nodes if n["node_type"] == "gap"),
            "total_edges": len(edges),
            "total_feedback": len(feedback),
            "by_node_type": _dist("node_type"),
            "by_verified_scope": _dist("verified_scope"),
            "by_verifiability": _dist("verifiability"),
            "by_build_status": _dist("build_status"),
            "by_role": _dist("role"),
            "by_segment": _dist("segment"),
            "by_skeleton_status": {k: skeleton_counts[k] for k in sorted(skeleton_counts)},
            "pending_anchors": len(pending_anchors),
        },
    }
    return doc


_MAP_HEADER = (
    "# AI 施工升级流图（construction_workflow_map，图 14）——由 "
    "generate_construction_workflow_map.py 机生。\n"
    "# 真源=政策内嵌机读锚块（政策未嵌块期回落 91 号提案件，见 anchor_source）；"
    "本文件禁手改后不回生成（counts 一致性校验判红）。\n"
    "# 节点只存 step_id 与引用，禁复制政策正文（INV-1）；machine_facts 层重扫即刷新，"
    "人工语义层改动须先回写骨架与锚块。\n"
)


def serialize_document(doc: dict[str, Any]) -> str:
    """确定性序列化（键序=插入序，禁 sort_keys 打乱语义分组）——幂等实证的落点。"""
    return serialize_map_document(doc, _MAP_HEADER)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="AI 施工升级流图（图14）生成器（机生优先，幂等）")
    ap.add_argument(
        "--as-of", default=None, help="generated_at 注入值（ISO 字面串）；缺省=HEAD 提交时间派生；禁运行时取时"
    )
    ap.add_argument(
        "--anchors-from",
        default=None,
        choices=["policy", "proposal"],
        help="锚块来源：policy=政策内嵌块（未来态）；proposal=91 号提案件（现态）；"
        "缺省=先找政策、找不到自动回落 proposal",
    )
    ap.add_argument("--out", default=str(OUTPUT_PATH), help="产出路径（默认 config/construction_workflow_map.yaml）")
    ap.add_argument("--root", default=str(_REPO_ROOT), help="扫描根（默认仓库根；worktree 内跑=worktree 根）")
    ap.add_argument("--dry-run", action="store_true", help="只打印摘要，零写入")
    args = ap.parse_args()

    root = Path(args.root)
    as_of = args.as_of or head_commit_time(root)
    doc = build_document(as_of=as_of, root=root, anchors_from=args.anchors_from)
    if args.dry_run:
        c = doc["counts"]
        print(
            f"dry-run: anchor_source={doc['anchor_source']} nodes={c['total_nodes']} "
            f"steps={c['total_steps']} gaps={c['total_gaps']} edges={c['total_edges']} "
            f"production={(c['by_verified_scope'] or {}).get('production')} "
            f"generated_at={as_of}"
        )
        return 0
    payload = serialize_document(doc)
    out = Path(args.out)
    try:
        from zephyr.shared.io.file_utils import safe_write_text

        ok = safe_write_text(out, payload)
    except Exception:  # noqa: BLE001 — 非 zephyr 环境（tmp 测试根）降级直写，仍幂等
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8", newline="\n")
        ok = True
    if not ok:
        print(f"[ERROR] safe_write_text 失败（CAS 冲突？）: {out}", file=sys.stderr)
        return 1
    c = doc["counts"]
    print(
        f"written: {out} (nodes={c['total_nodes']} steps={c['total_steps']} "
        f"gaps={c['total_gaps']} edges={c['total_edges']} anchor_source={doc['anchor_source']})"
    )
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 本件=离线机生器（六图族）——对齐台/人工显式触发再生产物，非 cron/daemon/常驻服务；判据面由 validators+对抗尺承载（同款豁免先例=generate_connection_matrix.py:1480, 8454beec5a）
    sys.exit(main())
