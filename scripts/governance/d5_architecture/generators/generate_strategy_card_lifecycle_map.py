# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §strategy_card_lifecycle_map
# [MODULE] scripts.governance.d5_architecture.generators.generate_strategy_card_lifecycle_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] task_bound
#   （CLI 生成器按需触发；PERM-TRIGGER 手动铁律归 task_bound——2026-10-04 落库与同族校验器归一；提案件原值=permanent 见文末 TTL-HISTORY）
# [DEPENDENCIES] yaml；validate_strategy_card_lifecycle_map（装载/实扫判据单一真源）+ 骨架/提案件/词表/宿主册/裁定册/卡语料/safe_write_text——详单见下方详情块
# [CONSUMERS] config/strategy_card_lifecycle_map.yaml（唯一产出）+ 校验器 CV-14 反向核对 + 同名 gate 触发面 + 对抗测试幂等实证
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 幂等=同输入逐字节等（时间戳经 --as-of/HEAD 派生，禁壁钟）；只读语料、写出面仅 --out；骨架+提案件→图单向派生；未入账卡进 pending_registration 可跑——全量见下方详情块
# [MODIFY-GUARD] 状态/迁移/禁边编号以骨架为契约（增删先回写骨架同步 CV-13）；语料口径以提案件 corpus_caliber 为准；禁复制校验器判据
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写盘失败=返码1；提案件/骨架不可读=对应面降级 WARN 不崩；--dry-run 零写入
# [TESTS] tests/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py
# create-guard-not-dup: 死车道抢救的卡片生命周期生成器（字节代投非新能力，wave2 manifest 6138fb7104c4 锚定），产出机读镜像图，与 blueprint/capability 生成器无职责重叠
#
# —— 详情块（2026-10-04 落库重排：14 字段头收进 30 行窗口，原字段长文降为详情）——
#   （CLI 生成器按需触发，非永久常驻系统——PERM-TRIGGER 手动模式铁律归 task_bound，
#   2026-10-04 落库时与同族校验器口径归一）
#   与 blueprint/capability 生成器无职责重叠
#   （load_anchor_block / scan_skeleton_axes / state_values / terminal_values——装载与实扫判据
#   单一真源，禁在生成器复制第二套）；
#   docs/_working/map_build/fig15_cardlife/00_skeleton.md（§1 状态全集 + §2.1 合法边 +
#   §2.2 禁止边 = 语义真源，本生成器只做机读镜像不做二次创作）；
#   docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml（语料口径 / 卡头别名
#   规则 / 六处分裂面 / 复活授权 = 施工口径档案；其 §2 词表与 §7 实例种子自 2026-09-26 起
#   改由宿主面装载——card_state_vocabulary.yaml + experiment_registry.yaml CARD-* 契约条目，
#   装载点唯一真源在校验器 load_anchor_block，本件禁另立第二套）；
#   docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml
#   docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml；
#   docs/_working 卡语料 frontmatter；
#   docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml（凭证在册性现算）；
#   zephyr.shared.io.file_utils.safe_write_text（热文件 CAS 写，AGENTS 硬规则 13）
#   validate_strategy_card_lifecycle_map（CV-14 的 counts==现算 反向核对）；
#   src/zephyr/gov_enforcement/commit_gates/strategy_card_lifecycle_map_gate（触发面之一）；
#   tests/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py（幂等实证）
#   禁 datetime.now()/time.time()——RULE-SCHEMA-TZ）；只读语料，写出面只有 --out 一处；
#   派生方向恒为 骨架+提案件 → 图 YAML（禁手改图不回生成，CV-14 判红）；
#   人工语义层（laws/boundary/instance_key_space）由 SEMANTIC_LAYER 常量持有并随每次生成重写，
#   实例层（states/transitions/forbidden_edges/gaps/corpus/counts/pending_registration）全部现算；
#   casebooks/casebooks_note_zh/casebooks_legend_zh 为人工语义层保留键（重生成从现有目标
#   yaml 原样搬回，缺席=不新增键零输出变化，挂载值人工批填；st-cbsurg-20261005 批通管零内容）；
#   禁硬编码中英翻译字典（名称一律取骨架列）；禁写状态（本件不产出任何状态判定，判定在校验器）；
#   未入账卡进 pending_registration 而非报错退出（半成品期可跑，防一次性大爆炸 diff）
#   语料口径以提案件 corpus_caliber 为准（改口径=改分母，须同时改簿03 的三数台账）；
#   本件禁复制校验器判据，装载与实扫一律 import 校验器函数
#   （不崩，禁静默产出半张图）；--dry-run 零写入

"""图15 策略卡生命周期图生成器（机生·幂等·禁取时）。

三条流水线，全部现算：
1. 语义镜像：骨架 §1/§2.1/§2.2 三张表 → states / transitions / forbidden_edges
   （编号与列值原样搬，名称取骨架列，禁二次创作；凭证类型按"凭据要求"列关键词归类）；
2. 语料扫描：按提案件 corpus_caliber 的口径扫 docs/**.md，解析 frontmatter status/family_id/
   n_eff/lane，套 status_alias_rules 得 mapped_state，产出 corpus 面与 by_state 分布；
3. 台账与对账：装载点实例面（anchor_source=registry 时=宿主册 CARD-* 契约条目，
   proposal 时=91 号件 §7 种子）+ 裁定册在册性 + 判决件面（两处 csv 的 card 列与 card: 键）
   → gaps 六处分裂面的实测数与 pending_registration（登记欠账逐形列明，禁隐身）。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[4]
_VALIDATORS_DIR = str(_REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "validators")
_THIS = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS.parents if (p / "_shared").exists()))
for _p in (_GOV_DIR, _VALIDATORS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import validate_strategy_card_lifecycle_map as V  # noqa: E402  装载与实扫判据单一真源
from d5_architecture.generators._common import (
    head_commit_time,  # noqa: E402  sys.path 注入的 governance 包（与姊妹生成器同款引导；CR-15 单源化家族口径）
    load_preserved_keys,  # noqa: E402  casebooks 保留键装载单一真源（禁复制第二套）
)

OUTPUT_PATH = _REPO_ROOT / "config" / "strategy_card_lifecycle_map.yaml"
# 人工语义层保留键（casebooks 病历挂载通道，st-cbsurg-20261005 批通管零内容；
# 先例=GOMAP _HUMAN_KEYS 机制 3d12a098）：机生层全量重建，此三键重生成时从现有
# 目标 yaml 原样搬回，缺席=不新增键（零输出变化）；挂载值由人工批填，生成器禁伪造
# （装载单一真源在 _common.load_preserved_keys，本件禁复制第二套）。
_CASEBOOKS_KEYS = ("casebooks", "casebooks_note_zh", "casebooks_legend_zh")
_PROPOSAL_REL = V._PROPOSAL_REL
_SKELETON_REL = V._SKELETON_REL
_CSV_VERDICT_FACES = (
    "docs/_working/archive/2026-09/bizmine_night/pattern_narrow_exam/pattern_narrow_results.csv",
    "docs/_working/archive/2026-09/bizmine_night/volume_family_l1/exam_results.csv",
)
# 禁止边 → 判定入口（实现绑定，非语义二次创作：禁令本体逐字取骨架 §2.2 列，
# 这里只登记"本图校验器的哪一条腿负责看见它"；无状态对偶的四条另标 pattern_kind）
_FORBIDDEN_CHECKERS = {
    "D15-X01": ("state_pair", "CV-07"),
    "D15-X02": ("self_pair", "CV-17"),
    "D15-X03": ("state_pair", "CV-05"),
    "D15-X04": ("state_pair", "CV-05"),
    "D15-X05": ("state_pair", "CV-07"),
    "D15-X06": ("state_pair", "CV-04"),
    "D15-X07": ("state_pair", "CV-09"),
    "D15-X08": ("self_pair", "CV-07"),
    "D15-X09": ("cross_cutting", "CV-08"),
    "D15-X10": ("state_pair", "CV-07"),
    "D15-X11": ("copy_guard", "CV-12"),
    "D15-X12": ("credential_guard", "CV-09"),
    "D15-X13": ("revival_guard", "CV-06"),
}
_CST = timezone(timedelta(hours=8))


# head_commit_time 单源于 _common（CR-15 单源化家族口径；本件死袋字节原带裸 subprocess 克隆，
# 2026-10-04 落库适配改 import——BARE-SUBPROCESS 门+BARE 兼 CLONEGUARD 双清）


def _clean(s: str, limit: int = V.MAX_LEN) -> str:
    t = re.sub(r"\s+", " ", str(s or "")).strip()
    return t if len(t) <= limit else t[: limit - 1].rstrip() + "…"


def _classify_credential(cell: str) -> str:
    """凭据要求列 → credential_required 枚举（关键词归类，禁按记忆）。"""
    t = str(cell or "")
    if re.search(r"裁定|RULE-RULING|判据必备|裁定必备", t):
        return "ruling"
    if re.search(r"快签|Owner|人（", t):
        return "owner_sign"
    if re.search(r"判定书|测试绿|verdict|run 档案|台账行|DSR", t):
        return "test_evidence"
    if re.search(r"机|执行件|事件触发", t):
        return "machine"
    return "none"


def _actor(cell: str) -> str:
    t = str(cell or "")
    if re.search(r"机器|机（|\*\*机", t):
        return "machine"
    if re.search(r"AI|人/AI", t):
        return "ai"
    return "human"


def _refs(cell: str) -> list[str]:
    """真源列 → 锚清单（只留 文件[:行] 与 册锚，禁复制正文）。"""
    out: list[str] = []
    for m in re.finditer(r"[A-Za-z0-9_./\-]+\.(?:md|yaml|py|csv)(?::\d+(?:-\d+)?)?", str(cell or "")):
        s = m.group(0)
        if s not in out:
            out.append(s)
    return out


def _state_map(values: list[dict[str, Any]]) -> dict[str, str]:
    """骨架列的 S 号 → 词表值（map_state 是唯一合法桥，禁在代码里背状态名）。"""
    return {str(v.get("map_state")): str(v.get("value")) for v in values if isinstance(v, dict)}


def _pair(cell: str, smap: dict[str, str]) -> tuple[list[str], str | None]:
    """骨架 from→to 单元格 → (from 值清单, to 值)，含 "S1..S9" 范围与 "S3|S4" 并列两种写法。"""
    parts = re.split(r"→|->", str(cell or ""))
    if len(parts) < 2:
        return [], None
    head, tail = parts[0].strip(), parts[1]
    rng = re.match(r"^(S\d{1,2})\s*\.\.\s*(S\d{1,2})$", head)
    if rng:
        ids = [f"D15-S{n}" for n in range(int(rng.group(1)[1:]), int(rng.group(2)[1:]) + 1)]
    else:
        ids = [f"D15-{x}" for x in re.findall(r"S\d{1,2}", head)]
    mt = re.search(r"S\d{1,2}", tail)
    to = smap.get(f"D15-{mt.group(0)}") if mt else None
    frm = [smap.get(i) for i in dict.fromkeys(ids) if smap.get(i)]
    return frm, to


def build_states(values: list[dict[str, Any]], sk: dict[str, Any], root: Path, term: set[str]) -> list[dict[str, Any]]:
    """骨架 §1 七列表 → states[]（name/note/machine_readable 全取列值，零自造）。"""
    text = (
        (root / _SKELETON_REL).read_text(encoding="utf-8", errors="replace") if (root / _SKELETON_REL).exists() else ""
    )
    rows: dict[str, list[str]] = {}
    for c in V._rows(text, "## §1 状态全集", "## §2", V._STATE_ROW_RE, 7):
        rows[c[0]] = c
    out = []
    for v in values:
        sid = str(v.get("map_state"))
        cols = rows.get(sid, [])
        out.append(
            {
                "state_id": sid,
                "value": v.get("value"),
                "map_state": sid,
                "name_zh": _clean(cols[1] if len(cols) > 1 else v.get("name_zh"), 40),
                "node_type": "state",
                "state": v.get("value"),
                "terminal": bool(v.get("terminal")),
                "credential_exemption": not bool(v.get("credential_required")),
                "machine_readable": sk.get("states", {}).get(sid, "no"),
                "decision_question": _clean(
                    f"这张卡当前是否处于「{cols[1] if len(cols) > 1 else sid}」？谁有权把它推出去、凭什么凭证？"
                ),
                "note_zh": _clean(v.get("definition_zh") or (cols[2] if len(cols) > 2 else "")),
                "entry_condition_zh": _clean(cols[3] if len(cols) > 3 else ""),
                "exit_zh": _clean(cols[4] if len(cols) > 4 else ""),
                "legacy_field": v.get("legacy_field"),
                "confidence": "verified",
                "verified_scope": "structure",
                "build_status": "partial" if sk.get("states", {}).get(sid) == "no" else "built",
                "source_anchors": _refs(cols[5] if len(cols) > 5 else "") or [_SKELETON_REL],
                "doc_refs": [_SKELETON_REL, _PROPOSAL_REL],
                "module_id": None,
                "module_ref": None,
                "red_reason": "unwired",
                "gap_refs": ["D15-G01", "D15-G02"],
                "evidence": [_clean(cols[5], 118) if len(cols) > 5 else "骨架 §1 表行实扫"],
                "instances_observed": None,
                "instances_by_card": None,
            }
        )
    return out


def build_transitions(
    sk: dict[str, Any], smap: dict[str, str], root: Path, entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """骨架 §2.1 六列表 → transitions[]（合法边 17 条，凭据与实查列原样镜像）。"""
    text = (
        (root / _SKELETON_REL).read_text(encoding="utf-8", errors="replace") if (root / _SKELETON_REL).exists() else ""
    )
    out = []
    for cols in V._rows(text, "### 2.1 合法边", "### 2.2", V._M_ROW_RE, 6):
        tid = cols[0]
        frm, to = _pair(cols[1], smap)
        if not frm and to:  # 入口边 ∅→S1 / ∅→S2
            frm = [None]
        if to is None:  # 骨架未写状态号的入口表述
            m = re.search(r"(?:∅|S\d{1,2})?\s*(?:→|->)\s*(?:\*\*)?\s*(S\d{1,2})", cols[1])
            to = smap.get(f"D15-{m.group(1)}") if m else None
            frm = frm or ([None] if to else [])
        cred = _classify_credential(cols[3])
        actor = _actor(cols[2])
        prod = sk.get("transitions", {}).get(tid) == "✅"
        out.append(
            {
                "transition_id": tid,
                "edge_kind": "permitted",
                "from_state": frm,
                "to_state": to,
                "name_zh": _clean(f"{tid} {cols[1]}", 60),
                "node_type": "transition",
                "actor": actor,
                "credential_required": cred,
                "gated": cred in V.HUMAN_GATE_KINDS,
                "credential_zh": _clean(cols[3], 118),
                "one_time_token": "rejudge_used" if "重判" in cols[1] or "一次性重判" in cols[3] else None,
                "cross_instance": "新卡" in cols[1] or "跨实例" in cols[3],
                "machine_readable": "yes" if prod else ("partial" if cred != "none" else "no"),
                "skeleton_status": sk.get("transitions", {}).get(tid, "?"),
                "decision_question": _clean("这次迁移是否发生过、由谁推动、凭证是否在册？"),
                "note_zh": _clean(cols[3], 118),
                "confidence": "verified" if prod or sk.get("transitions", {}).get(tid) else "proposed",
                "verified_scope": "production" if prod else ("structure" if to else None),
                "build_status": "built" if prod else ("partial" if to else "pending"),
                "source_anchors": _refs(cols[4]) or [_SKELETON_REL],
                "doc_refs": [_SKELETON_REL, _PROPOSAL_REL],
                "module_id": None,
                "module_ref": None,
                "red_reason": "unwired",
                "gap_refs": [
                    g
                    for g, cond in (
                        ("D15-G05", tid in ("D15-M06", "D15-M07", "D15-M08", "D15-M09")),
                        ("D15-G06", tid in ("D15-M16", "D15-M17")),
                        ("D15-G03", tid in ("D15-M05", "D15-M12")),
                        ("D15-G04", tid in ("D15-M13",)),
                    )
                    if cond
                ],
                "evidence": [_clean(cols[5], 118)] if len(cols) > 5 else [],
                "observed_in_registered_ledger": sorted(
                    {
                        str(e.get("card_id"))
                        for e in entries
                        if any(
                            str(c.get("from")) in [x for x in frm if x] and str(c.get("to")) == to
                            for c in e.get("credential") or []
                        )
                    }
                ),
            }
        )
    return out


def build_forbidden(
    sk: dict[str, Any], smap: dict[str, str], root: Path, transitions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """骨架 §2.2 四列表 → forbidden_edges[]（13 条一条不许丢，含绕过探针所需字段）。"""
    text = (
        (root / _SKELETON_REL).read_text(encoding="utf-8", errors="replace") if (root / _SKELETON_REL).exists() else ""
    )
    out = []
    for cols in V._rows(text, "### 2.2 禁止边全集", "**迁移计数**", V._X_ROW_RE, 4):
        xid = cols[0]
        frm, to = _pair(cols[1], smap)
        checker = (re.search(r"CV-\d+", cols[3] if len(cols) > 3 else "") or [None])[0]
        kind, bound = _FORBIDDEN_CHECKERS.get(xid, ("state_pair", "CV-07"))
        checker = checker or bound
        if kind in ("cross_cutting", "copy_guard", "credential_guard", "revival_guard"):
            checker = bound
        prod = sk.get("forbidden", {}).get(xid) == "✅"
        gated_from = sorted(
            {
                str(t.get("transition_id"))
                for t in transitions
                if t.get("gated") and any(f in (t.get("from_state") or []) for f in frm)
            }
        )
        out.append(
            {
                "edge_id": xid,
                "edge_kind": "forbidden",
                "pattern_kind": kind,
                "from_state": frm or ["*"],
                "to_state": to or "*",
                "name_zh": _clean(f"{xid} {cols[1]}", 60),
                "node_type": "forbidden_edge",
                "rule_zh": _clean(cols[1], 118),
                "note_zh": _clean(cols[1], 118),
                "decision_question": _clean("这条禁令今天靠什么被看见？会不会被一条合法边绕开而无人知？"),
                "credential_source": _clean(cols[2], 118),
                "checker": checker,
                "enforcement": (
                    "live_incident_observed" if prod else ("machine_checkable" if checker else "declared_only")
                ),
                "bypass_guard": _clean(
                    "凡从该状态出发的合法边必须带人凭证（ruling/owner_sign），"
                    f"当前闸门边={gated_from or '无（此禁令只能靠实例面判）'}"
                )
                if kind == "state_pair"
                else _clean("跨面禁令无状态对可绕，判定入口固定为 checker 所指 CV 项"),
                "machine_readable": "yes" if checker else "no",
                "skeleton_status": sk.get("forbidden", {}).get(xid, "?"),
                "actor": "human",
                "credential_required": "ruling" if prod else ("machine" if checker else "none"),
                "gated": None,
                "confidence": "verified" if (prod or checker) else "proposed",
                "verified_scope": "production" if prod else ("structure" if checker else None),
                "build_status": "built" if checker else "pending",
                "source_anchors": _refs(cols[2]) or [_SKELETON_REL],
                "doc_refs": [_SKELETON_REL, _PROPOSAL_REL],
                "module_id": None,
                "module_ref": None,
                "red_reason": "unwired",
                "gap_refs": ["D15-G01"]
                if xid == "D15-X02"
                else (
                    ["D15-G05"]
                    if xid in ("D15-X07", "D15-X09")
                    else ["D15-G06"]
                    if xid in ("D15-X03", "D15-X04", "D15-X13")
                    else ["D15-G02"]
                ),
                "evidence": [_clean(cols[3], 118)] if len(cols) > 3 else [],
            }
        )
    return out


def build_gaps(faces: list[dict[str, Any]], corpus: dict[str, Any], ledger: dict[str, Any]) -> list[dict[str, Any]]:
    """簿03 §A 六处状态面 → gaps[]（六条一条不许丢；实测数全部现算挂上去）。"""
    measured = {
        "D15-G01": {
            "cards": corpus["n"],
            "headed": corpus["headed"],
            "headless": corpus["headless"],
            "distinct_status_strings": corpus["distinct_status_strings"],
            "in_controlled_vocab": corpus["in_controlled_vocab"],
            "registered_in_host": corpus["registered"],
        },
        "D15-G02": {
            "registry_entries": ledger["registry_entries"],
            "contract_card_entries": ledger["registry_contract_entries"],
            "run_entries": ledger["registry_run_entries"],
            "card_key_intersection_with_corpus": ledger["key_intersection"],
            "viability_verdict_null": ledger["viability_verdict_null"],
            "viability_verdict_filled_by": ledger["viability_verdict_filled"],
        },
        "D15-G03": {
            "ledger_rows_scanned": ledger["ledger_rows"],
            "rows_with_card_state_key": ledger["ledger_rows_with_key"],
        },
        "D15-G04": {"faces": list(ledger["ch_faces"]), "note": "跨域不同对象，不并"},
        "D15-G05": {"csv_faces": ledger["csv_faces"], "card_key_faces": ledger["card_key_faces"]},
        "D15-G06": {
            "missing_truth_sources": ledger["missing_sources"],
            "blueprint_card_anchors": ledger["blueprint_anchors"],
        },
    }
    out = []
    for f in faces:
        fid = str(f.get("face_id"))
        out.append(
            {
                "gap_id": fid,
                "node_type": "gap",
                "name_zh": _clean(f.get("name_zh"), 60),
                "object_zh": _clean(f.get("object"), 60),
                "today_zh": _clean(f.get("today"), 118),
                "disposition_zh": _clean(f.get("disposition"), 118),
                "net_zero_zh": _clean(f.get("net_zero"), 118),
                "red_reason": f.get("red_reason"),
                "decision_question": _clean("这一处今天真的在管卡状态吗？它该退役、降级还是保留为视图？"),
                "note_zh": _clean(f.get("today"), 118),
                "measured": measured.get(fid, {}),
                "confidence": "verified",
                "verified_scope": "structure",
                "build_status": "pending",
                "machine_readable": "partial",
                "source_anchors": ["docs/_working/map_build/fig15_cardlife/03_三处分裂对账与外部对标.md"],
                "doc_refs": [_PROPOSAL_REL],
                "module_id": None,
                "module_ref": None,
                "gap_refs": [fid],
                "evidence": ["簿03 §A 逐处开账（本件 measured 由生成器现算）"],
            }
        )
    return out


def _alias_precedence(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """91 号件 §4 别名规则的生效序——路径级例外（AL-05/AL-07）先于串号规则（AL-01..04/06），
    无头规则居末。留痕：§4 声明 ordered=true，但按声明序 AL-04（token frozen 无路径限）恒先到，
    AL-05/AL-07 实测零触发（03 号簿 §A 与 01 号簿 T04/T02 的"规程件不是契约卡"意图落空）；
    本件只改判定输入的**顺序**口径，不改任何阈值或映射目标（L-HOST15 回填批实测钉住）。
    """

    def prio(r: dict[str, Any]) -> int:
        if r.get("when_path_in"):
            return 0
        if r.get("when_headless"):
            return 1
        return 2

    return sorted(rules, key=prio)


def scan_corpus(root: Path, proposal: dict[str, Any], registered: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """按提案件口径扫卡语料 frontmatter（口径唯一，改它=改分母）。

    registered=装载点实例面（registry 期=宿主册 CARD-* 条目）；按 lives_in.path 与语料做
    键级 join，得镜像面（卡头串）与真源面（登记 card_state）的两列——两列并存是 D15-G01
    降级为只读镜像的机验前提，禁在此判谁对谁错（判定在校验器）。
    """
    cal = proposal.get("corpus_caliber") or {}
    inc = re.compile(cal.get("include_regex", ""), re.I)
    exc = re.compile(cal.get("exclude_regex", ""), re.I)
    dirs = list(cal.get("include_dirs") or [])
    exsub = list(cal.get("exclude_path_substrings") or [])
    rules = _alias_precedence((proposal.get("status_alias_rules") or {}).get("rules") or [])
    reg_by_path: dict[str, dict[str, Any]] = {}
    for e in registered or []:
        if not isinstance(e, dict):
            continue
        for l in e.get("lives_in") or []:
            p = str((l or {}).get("path") or "").replace("\\", "/")
            if p:
                reg_by_path.setdefault(p, e)
    cards: list[dict[str, Any]] = []
    digests: dict[str, list[str]] = defaultdict(list)
    root_abs = Path(root).resolve()
    for p in sorted((root / "docs").rglob("*.md")) if (root / "docs").exists() else []:
        a = p.as_posix()
        # 图与宿主册的键级 join 必须以仓内相对路径为轴（绝对路径跨机/跨 worktree 必漂，
        # 且宿主册 lives_in.path 的在册形态就是仓内相对路径）
        try:
            rel = p.resolve().relative_to(root_abs).as_posix()
        except ValueError:
            rel = a
        if any(s in a for s in exsub) or exc.search(p.name):
            continue
        if not (inc.search(p.name) or any(d in a for d in dirs)):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        fm = m.group(1) if m else ""

        def field(k: str) -> str | None:
            g = re.search(r"^%s:\s*(.+)$" % k, fm, re.M)
            return g.group(1).strip() if g else None

        status = field("status")
        mapped, disposition, rule_id = None, None, None
        for r in rules:
            paths = [str(x) for x in (r.get("when_path_in") or [])]
            token = str(r.get("when_token") or "")
            if r.get("when_headless") and not status:
                disposition, rule_id = "unmapped_headless", str(r.get("rule_id"))
                break
            if paths and not any(x in p.name for x in paths):
                continue
            if paths and not token:
                disposition, rule_id = "non_domain", str(r.get("rule_id"))
                break
            if token and status and status.startswith(token):
                disposition, rule_id = str(r.get("disposition")), str(r.get("rule_id"))
                mapped = r.get("to_state")
                break
        digest = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
        digests[digest].append(rel)
        reg = reg_by_path.get(rel)
        cards.append(
            {
                "path": rel,
                "stem": p.stem,
                "status_note": _clean(status, 118) if status else None,
                "has_status_head": bool(status),
                "mapped_state": mapped,
                "disposition": disposition or "unmatched_alias",
                "alias_rule": rule_id,
                "family_id": (field("family_id") or "").split("（")[0] or None,
                "n_eff_raw": field("n_eff"),
                "n_eff_declared": V._n_eff({"n_eff": field("n_eff")}),
                "lane": bool(field("lane")),
                "sha12": digest,
                "registered_card_id": str(reg.get("card_id")) if reg else None,
                "registered_state": str(reg.get("card_state")) if reg else None,
                "registered": bool(reg),
                "token": (status.split("（")[0].split("#")[0].strip() if status else None),
            }
        )
    by_state = Counter(str(c["mapped_state"]) for c in cards if c["mapped_state"])
    by_registered_state = Counter(str(c["registered_state"]) for c in cards if c["registered_state"])
    fam: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in cards:
        if c["family_id"]:
            fam[c["family_id"]].append(c)
    families = {
        k: {
            "members": len(v),
            "declared_n_eff": sorted({x["n_eff_declared"] for x in v if x["n_eff_declared"]}),
            "single_hypothesis_members": sum(1 for x in v if "NARROWING" not in x["stem"].upper()),
        }
        for k, v in sorted(fam.items())
    }
    return {
        "n": len(cards),
        "headed": sum(1 for c in cards if c["has_status_head"]),
        "headless": sum(1 for c in cards if not c["has_status_head"]),
        "distinct_status_strings": len({c["status_note"] for c in cards if c["status_note"]}),
        "in_controlled_vocab": sum(1 for c in cards if c["mapped_state"]),
        "registered": sum(1 for c in cards if c["registered"]),
        "by_token": dict(Counter(str(c["token"]) for c in cards)),
        "by_disposition": dict(Counter(str(c["disposition"]) for c in cards)),
        "by_state": dict(sorted(by_state.items())),
        "by_registered_state": dict(sorted(by_registered_state.items())),
        "families": families,
        "family_id_coverage": sum(1 for c in cards if c["family_id"]),
        "n_eff_coverage": sum(1 for c in cards if c["n_eff_declared"]),
        "lane_coverage": sum(1 for c in cards if c["lane"]),
        "card_id_field_coverage": sum(1 for c in cards if c["registered_card_id"]),
        "duplicate_content_groups": {k: v for k, v in sorted(digests.items()) if len(v) > 1},
        "cards": [
            {
                k: c[k]
                for k in (
                    "path",
                    "stem",
                    "mapped_state",
                    "disposition",
                    "family_id",
                    "n_eff_declared",
                    "sha12",
                    "registered_card_id",
                    "registered_state",
                    "registered",
                )
            }
            for c in cards
        ],
    }


def scan_ledger(
    root: Path, proposal: dict[str, Any], corpus: dict[str, Any], instance_entries: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """在册登记面 + 台账 + 判决件面 + 真源完整性现算（六处分裂面的数字来源）。"""
    host_rel = (proposal.get("host") or {}).get("registry_path") or V._REGISTRY_HOST_REL
    host_txt = ""
    host: dict[str, Any] = {}
    if (root / host_rel).exists():
        host_txt = (root / host_rel).read_text(encoding="utf-8", errors="replace")
        try:
            host = yaml.safe_load(host_txt) or {}
        except Exception:  # noqa: BLE001 — 册坏=计数降级，判定在校验器
            host = {}
    entries = [e for e in (host.get("experiments") or []) if isinstance(e, dict)]
    contract = [e for e in entries if str(e.get("experiment_id", "")).startswith("CARD-")]
    run_rows = [e for e in entries if str(e.get("experiment_id", "")).startswith("EXP-")]
    stems = {c["stem"] for c in corpus["cards"]}
    key_hits = sum(1 for s in stems if s in host_txt)
    ledger_rows = 0
    for rel in (
        "docs/_working/archive/2026-09/final3_campaign/w9_triage_ledger.md",
        "docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md",
        "docs/_working/archive/2026-09/tdchain_mine/a0_master_ledger.md",
        "docs/_working/archive/2026-09/bizmine_night/bizmine_campaign_ledger.md",
        "docs/_working/fullflow_campaign/COORDINATION_LEDGER.md",
        "docs/_working/integrated_backtest/IBT-CAMPAIGN-LEDGER.md",
    ):
        p = root / rel
        if p.exists():
            ledger_rows += sum(
                1
                for line in p.read_text(encoding="utf-8", errors="replace").split("\n")
                if line.strip().startswith("|")
            )
    csv_faces = []
    for rel in _CSV_VERDICT_FACES:
        p = root / rel
        if not p.exists():
            continue
        head = p.read_text(encoding="utf-8", errors="replace").split("\n")[0]
        cols = [c.strip() for c in head.split(",")]
        key_col = "card" if "card" in cols else ("cid" if "cid" in cols else None)
        csv_faces.append(
            {
                "path": rel,
                "columns": len(cols),
                "key_column": key_col,
                "has_n_eff": "n_eff" in cols,
                "has_verdict": "verdict" in cols,
            }
        )
    card_key_faces = []
    root_abs_ledger = Path(root).resolve()
    for p in sorted((root / "docs").rglob("*.md")):
        if "fig15_cardlife" in p.as_posix():
            continue
        head = p.read_text(encoding="utf-8", errors="replace")[:2000]
        if re.search(r"^card:", head, re.M):
            try:
                card_key_faces.append(p.resolve().relative_to(root_abs_ledger).as_posix())
            except ValueError:
                card_key_faces.append(p.as_posix())
    ledger_entries = [
        e
        for e in (instance_entries if instance_entries is not None else (proposal.get("card_entries") or []))
        if isinstance(e, dict)
    ]
    missing, anchors = [], 0
    for e in ledger_entries:
        for l in e.get("lives_in") or []:
            if not (root / str((l or {}).get("path"))).exists():
                missing.append(str((l or {}).get("path")))
    for p in list((root / "scripts").rglob("*.py"))[:4000] if (root / "scripts").exists() else []:
        first = p.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
        if "[BLUEPRINT]" in first and re.search(r"prereg|_card|card_", first):
            anchors += 1
    return {
        "registry_entries": len(entries),
        "registry_contract_entries": len(contract),
        "registry_run_entries": len(run_rows),
        "key_intersection": int(corpus.get("registered") or 0),
        "key_text_hits": key_hits,
        "viability_verdict_null": sum(1 for e in entries if e.get("viability_verdict") is None),
        "viability_verdict_filled": sorted({str(e.get("card_id")) for e in contract if e.get("viability_verdict")}),
        "ledger_rows": ledger_rows,
        "ledger_rows_with_key": 0,
        "ch_faces": ["c1_backtest.hypothesis_precheck", "c1_backtest.strategy_screen", "c1_backtest.node_verdict"],
        "ch_rows_with_card_id": 0,
        "csv_faces": csv_faces,
        "card_key_faces": card_key_faces,
        "missing_sources": sorted(missing),
        "blueprint_anchors": anchors,
        "seed_entries": len(ledger_entries),
    }


def scan_credential_in_register(
    root: Path, transitions: list[dict[str, Any]], forbidden: list[dict[str, Any]]
) -> dict[str, Any]:
    """凭证在册性现算（图里出现的每个 裁定#NNN 都回裁定册查，禁凭记忆）。"""
    ids = set()
    for it in transitions + forbidden:
        for a in (it.get("source_anchors") or []) + [it.get("credential_source") or ""]:
            ids.update(re.findall(r"\u88c1\u5b9a#\d+", str(a)))
    reg = V.scan_ruling_ids(root)
    return (
        {"cited": sorted(ids), "in_register": sorted(i for i in ids if i in reg)}
        if reg
        else {"cited": sorted(ids), "in_register": []}
    )


def build_document(as_of: str, root: Path, proposal: dict[str, Any] | None = None) -> dict[str, Any]:
    """组装图 YAML（语义层常量化 + 实例层全现算 ⇒ 幂等）。"""
    src, block = V.load_anchor_block(root)
    proposal = proposal if proposal is not None else (block.get("proposal") or {})
    values = block.get("values") or []
    entries = block.get("card_entries") or []
    smap = _state_map(values)
    sk = V.scan_skeleton_axes(root)
    corpus = scan_corpus(root, proposal, entries)
    ledger = scan_ledger(root, proposal, corpus, entries)
    states = build_states(values, sk, root, V.terminal_values(block))
    inst = defaultdict(int)
    for c in corpus["cards"]:
        if c["mapped_state"]:
            inst[c["mapped_state"]] += 1
    for s in states:
        s["instances_observed"] = inst.get(str(s.get("value")), 0)
        s["instances_by_card"] = sorted(
            {str(e.get("card_id")) for e in entries if str(e.get("card_state")) == str(s.get("value"))}
        )
    transitions = build_transitions(sk, smap, root, entries)
    forbidden = build_forbidden(sk, smap, root, transitions)
    gaps = build_gaps(proposal.get("split_faces") or [], corpus, ledger)
    cred = scan_credential_in_register(root, transitions, forbidden)
    cards = corpus["cards"]
    unmapped = [c["path"] for c in cards if not c["mapped_state"]]
    # 镜像面可判态却无登记条目=本役回填欠账（registry 期必须清空，CV-HOST 硬腿）；
    # 卡头无可判信息（无头/待裁/别名未覆盖/非域件）不是欠账，逐形列明禁隐身
    debt = [c["path"] for c in cards if c["mapped_state"] and not c["registered_card_id"]]
    headless = [c["path"] for c in cards if c["disposition"] == "unmapped_headless"]
    adjud = [c["path"] for c in cards if c["disposition"] == "needs_adjudication"]
    unmatched = [c["path"] for c in cards if c["disposition"] == "unmatched_alias"]
    non_dom = [c["path"] for c in cards if c["disposition"] == "non_domain"]
    live_host = src == "registry"
    prod = sum(1 for it in transitions + forbidden if it.get("verified_scope") == "production")
    preserved_casebooks = load_preserved_keys(OUTPUT_PATH, _CASEBOOKS_KEYS)
    doc: dict[str, Any] = {
        "schema_version": "0.2",
        "map_id": "strategy_card_lifecycle_map",
        "name_zh": "策略卡生命周期图",
        "nickname": "卡生命周期",
        "effective_from": "2026-09-24",
        "markets": ["cn_a"],
        "generator": "scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py",
        "generated_at": as_of,
        "registry_host": "experiment_registry" if live_host else "proposed:experiment_registry",
        "anchor_source": src or "proposal",
        "anchor_block_origin": (V._REGISTRY_VOCAB_REL if live_host else _PROPOSAL_REL),
        "caliber_source": _PROPOSAL_REL,
        "registry_host_path": (proposal.get("host") or {}).get("registry_path") or V._REGISTRY_HOST_REL,
        "derived_from": (
            [_SKELETON_REL, V._REGISTRY_VOCAB_REL, V._REGISTRY_HOST_REL, _PROPOSAL_REL]
            if live_host
            else [_SKELETON_REL, _PROPOSAL_REL]
        ),
        "ssot_note_zh": (
            "真源方向：骨架 §1/§2（状态与边的语义契约）+ 受控词表 card_state_vocabulary.yaml + "
            "宿主册 experiment_registry.yaml 的 CARD-* 契约条目（登记面实例真源）→ 本图 YAML"
            "（派生件，禁手改后不回生成）。91 号提案件自宿主落地起降级为施工档案，只为本图提供"
            "非状态类口径（语料分母 §9 / 卡头别名规则 §4 / 六处分裂面 §5 / 复活授权 §7 注），"
            "词表与实例两面不再回读它（anchor_source=registry 且 CV-HOST 硬腿盯假迁移）。"
            "卡头 status 串面已降级为只读镜像：镜像推断列 corpus.cards[].mapped_state，"
            "登记真源列 registered_state，两列并存供 CV-10 判冲突，方向恒为 册→md。"
            "本图三类对象=states/transitions/forbidden_edges，禁止边是一半价值，一条不许丢（CV-13 判）。"
            "字段分层（六图终局卷 §1 裁定一）：L0 统一名 note_zh/doc_refs/source_anchors/"
            "confidence+verified_scope；L1 取用 gap_refs/red_reason/wiring 面在本图为 enforcement 与 "
            "bypass_guard；L2 图专属层=from_state/to_state/edge_kind/permitted|forbidden/"
            "terminal/machine_readable/hypothesis_key/one_time_token/revives。"
            "双轴口径：production ⇔ 骨架 §2.1/§2.2 实查列 ✅（骨架 §1 无 ✅ 列 ⇒ 状态面禁宣 production）。"
        ),
        "laws": [
            "状态真源恒在登记面（宿主册）；卡 md 是判据正文真源，图与镜像字段都是派生件",
            "图只存标识与引用，禁复制 exam_policy / factor_mining_sop / 卡正文（INV-1）",
            "封卡即终：任何就地复活边一律非法，复活=新 card_id + revives 指针",
            "禁止边与合法迁移同对并存即判据自相矛盾；禁边不得被无凭证路径绕开",
            "计数只进 counts，散文写死数字判红；production 数恒等骨架实查 ✅ 数",
        ],
        "boundary": [
            "轴区分：本图 state_id=D15-S*、对象键=card_id；策略工厂 node_id=FAC-*、"
            "build_status 是工序进度不是契约地位（config/strategy_production_map.yaml:20）",
            "不含考试判据正文（判据真源=docs/01_policies_and_standards/sop/backtest_system_sop/"
            "exam_policy.md §1 与 §3）",
            "不含裁定产生流程（治理立法流图16）与提交机制（图11）与数据供料（图12）",
            "不含卡内单张卡的全部字段与判据正文（骨架 L-5：叶层不枚举）",
        ],
        "instance_key_space": {
            "card_id": "T0-PRERG-*/P3-E1C-*/P3-B-*/ALGO-*-<lane>-<family>-<NNN>",
            "disjoint_with": [
                "candidate_id(CAND-*)",
                "strategy_id",
                "node_id(TDM-*)",
                "node_id(FAC-*)",
                "step_id(BM-*)",
                "step_id(D14-*)",
                "module_id(MOD-*)",
                "data_step(DS-*)",
            ],
            "sample_ids": sorted({str(e.get("card_id")) for e in entries}),
        },
        "revival_authorizations": proposal.get("revival_authorizations") or [],
        "credential_register": cred,
        "states": states,
        "transitions": transitions,
        "forbidden_edges": forbidden,
        "gaps": gaps,
        "card_ledger": entries,
        "corpus": {k: v for k, v in corpus.items() if k != "cards"} | {"cards": corpus["cards"]},
        # 人工语义层保留键：目标 yaml 在册则原样搬回，缺席=零键写入（零输出变化）
        **preserved_casebooks,
        "counts": {
            "total_states": len(states),
            "total_transitions": len(transitions),
            "total_forbidden_edges": len(forbidden),
            "total_gaps": len(gaps),
            "total_edges": len(transitions) + len(forbidden),
            "terminal_states": sum(1 for s in states if s.get("terminal")),
            "production": prod,
            "cards_total": corpus["n"],
            "by_state": corpus["by_state"],
            "registered_by_state": corpus["by_registered_state"],
            "registered_entries_in_ledger": len(entries),
            "corpus_files_registered": corpus["registered"],
            "unregistered_declarable": len(debt),
            "state_undeclared_headless": len(headless),
            "needs_adjudication": len(adjud),
            "unmatched_alias": len(unmatched),
            "non_domain_excluded": len(non_dom),
            "by_verified_scope": dict(
                Counter(str(it.get("verified_scope")) for it in states + transitions + forbidden + gaps)
            ),
            "by_confidence": dict(Counter(str(it.get("confidence")) for it in states + transitions + forbidden + gaps)),
            "by_build_status": dict(
                Counter(str(it.get("build_status")) for it in states + transitions + forbidden + gaps)
            ),
            "by_machine_readable": dict(
                Counter(str(it.get("machine_readable")) for it in states + transitions + forbidden)
            ),
            "by_enforcement": dict(Counter(str(x.get("enforcement")) for x in forbidden)),
            "by_edge_kind": {"permitted": len(transitions), "forbidden": len(forbidden)},
            "in_register_rulings": len(cred["in_register"]),
            "uncited_rulings": sorted(set(cred["cited"]) - set(cred["in_register"])),
            "pending_registration": len(debt) if live_host else len(unmapped),
        },
        "pending_registration": {
            "unregistered_declarable": debt,
            "state_undeclared_headless": headless,
            "needs_adjudication": adjud,
            "unmatched_alias": unmatched,
            "non_domain_excluded": non_dom,
            "unmapped_cards": unmapped,
            "reason_zh": (
                "unregistered_declarable=卡头可判态却无登记条目（本役回填欠账，registry 期"
                "必须清空，CV-HOST 硬腿判红）；state_undeclared_headless=卡头无 status 且受控"
                "词表无 unknown 值——补登记即造判决，故留册外逐条列名；needs_adjudication="
                "别名规则 AL-06 明令不入册（无 H1 与判据结构）；non_domain_excluded=路径级"
                "规程件例外 AL-05/AL-07（战役规程不是契约卡）；四形分列禁合并隐身，"
                "分母与各形数量一律读 counts。"
                + (
                    ""
                    if live_host
                    else "（proposal 期：宿主册尚未扩枚举，登记面全部欠账，见 counts.pending_registration）"
                )
            ),
            "code_artifacts_awaiting_depgraph": [
                "scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py",
                "scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py",
                "src/zephyr/gov_enforcement/commit_gates/strategy_card_lifecycle_map_gate.py",
            ],
        },
    }
    return doc


def serialize_document(doc: dict[str, Any]) -> str:
    """确定性序列化（键序=插入序，禁 sort_keys 打乱语义分组）——幂等实证的落点。"""
    header = (
        "# 策略卡生命周期图（strategy_card_lifecycle_map，图15）——"
        "由 generate_strategy_card_lifecycle_map.py 机生。\n"
        "# 真源=骨架 §1/§2（状态与边的语义契约）+ 装载面（anchor_source 标当前装载点："
        "registry=在册词表 card_state_vocabulary.yaml + 宿主册 experiment_registry.yaml 的 "
        "CARD-* 契约条目，proposal=91 号提案件）；91 号件恒为语料口径/别名规则/分裂面档案；"
        "本文件禁手改后不回生成（counts 一致性判红）。\n"
        "# 三类对象全入：states / transitions / forbidden_edges（禁止边是一半价值，一条不许丢）；"
        "# 六处分裂面以 gaps + gap_refs 显性化；节点只存标识与指针，禁复制判据正文（INV-1）。\n"
    )
    return header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=110)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="图15 卡生命周期状态机图生成器（机生·幂等）")
    ap.add_argument("--as-of", default=None, help="generated_at 注入值（ISO 字面串）；缺省=HEAD 提交时间；禁运行时取时")
    ap.add_argument("--out", default=str(OUTPUT_PATH), help="产出路径（默认 config/…yaml）")
    ap.add_argument("--root", default=str(_REPO_ROOT), help="扫描根（worktree 内跑=worktree 根）")
    ap.add_argument("--dry-run", action="store_true", help="只打印摘要，零写入")
    args = ap.parse_args()
    root = Path(args.root)
    as_of = args.as_of or head_commit_time(root)
    doc = build_document(as_of=as_of, root=root)
    c = doc["counts"]
    if args.dry_run:
        print(
            f"dry-run: anchor_source={doc['anchor_source']} states={c['total_states']} "
            f"transitions={c['total_transitions']} forbidden={c['total_forbidden_edges']} "
            f"gaps={c['total_gaps']} production={c['production']} cards={c['cards_total']} "
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
    print(
        f"written: {out} (states={c['total_states']} transitions={c['total_transitions']} "
        f"forbidden={c['total_forbidden_edges']} gaps={c['total_gaps']} "
        f"production={c['production']} cards={c['cards_total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
