# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §strategy_card_lifecycle_map
# [MODULE] scripts.governance.d5_architecture.validators.validate_strategy_card_lifecycle_map
# [DOMAIN] D_GOV_SCRIPTS
# [CONSUMERS] config/strategy_card_lifecycle_map.yaml 质量门禁；
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全程只读（本工具禁写任何文件；禁就地改状态——判定只产 error/warn 清单，
# [MODIFY-GUARD] none（只读校验，无写盘）
# [STABILITY] stable
# [SAFETY] L（只读校验，无写盘无资金路径）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 结构违规=exit 1；语料/宿主册不可读=对应面降 warn 并打印，禁把'读不到'当'无冲突'
# [TESTS] tests/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py
# [TTL] task_bound
#   （原值 permanent——CLI 校验器非永久常驻系统，PERM-TRIGGER 手动模式铁律归 task_bound）
# create-guard-not-dup: 死车道抢救的卡片生命周期校验器（字节代投非新能力），校验词表卡必然读写yaml/词表术语，与canonical词汇装载器无职责重叠

# [DEPENDENCIES] yaml；docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml
#   （proposal 期回落装载点：词表 + 实例种子 + 复活授权 + 语料口径/别名规则/分裂面；
#   宿主落地后（anchor_source=registry）只继续提供非状态类口径，词表与实例面禁回读=禁双源）；
#   docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml
#   （registry 期状态词表真源，存在即优先，禁与提案件双读）；
#   docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml
#   （registry 期实例真源=CARD-* 契约条目，schema 2.2）；
#   docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml（凭证在册性 CV-09）；
#   docs/_working/map_build/fig15_cardlife/00_skeleton.md（§1 机可读列 / §2.1 实查列 /
#   §2.2 禁边实查列——双轴与覆盖度同源，禁在校验器写死状态集）；
#   docs/03_modules/path_ownership_map.yaml 与 zephyr.governance.depgraph_schema（CV-BUS 在册面）；
#   docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md 与
#   factor_mining_sop_policy.md（CV-12 INV-1 反复制语料）


"""图15 策略卡生命周期（状态机）校验器——结构契约与实例判据的唯一真源。

本图不是 DAG：三类对象 = 状态（13）+ 合法迁移（17）+ 禁止边（13）。禁止边是本图一半价值，
故校验器分两半：`validate_structure` 管图自身（枚举闭集/状态机良构/禁边可枚举且不可绕过/
双轴/计数/越域），`check_instances` 管实例台账（非法迁移、终态就地改状态、SEALED 就地复活、
复活不指向新卡 id、同假设双卡、凭证在册、镜像一致、指纹与判重）。gate 只调前者（live=False），
CLI 与 align_all 调两者——与图14 同族口径。

回炉说明（总包已裁，91 号件 §validator_rework 留痕）：CV-06 与 CV-08 的**阈值一字未改**，
改的是输入口径——CV-06 的复活判定不再依赖 family_id 等值（唯一真复活链的族名是新的，
按旧写法必漏判），改读"revives 字段 / 复活授权裁定引用 / 终态卡号或族名命中"三元；
CV-08 不再把 family_id 当"同一假设"的键（多成员族合法，按旧写法 89 张口径误伤 37 张，
而其为之而生的 F-07 一条抓不到），改为 A 假设身份 + B 卡号↔文件↔判决三元组 + C 族账对账。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MAP = Path("config/strategy_card_lifecycle_map.yaml")
_REPO_ROOT = Path(__file__).resolve().parents[4]
# depgraph PG 在册性探测（F821 治理补缺：常量段佚失，MOD 号经 nodes.blueprint_id 列承载；{} 由调用方 % 填充占位符）
_SQL_MODULE_ID_LIST = "SELECT blueprint_id FROM nodes WHERE blueprint_id IN ({})"
_SKELETON_REL = "docs/_working/map_build/fig15_cardlife/00_skeleton.md"
_PROPOSAL_REL = "docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml"
_REGISTRY_VOCAB_REL = "docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml"
_REGISTRY_HOST_REL = str(
    Path("docs" / "01_policies_and_standards" / "_registry" / "catalogs") / "experiment_registry.yaml"
)
_RULING_REGISTRY_REL = str(
    Path("docs" / "01_policies_and_standards" / "_registry" / "catalogs") / "ruling_registry.yaml"
)
_PATH_OWNERSHIP_REL = "docs/03_modules/path_ownership_map.yaml"
_INV1_CORPUS_RELS = (
    "docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md",
    "docs/01_policies_and_standards/sop/factor_mining_sop_policy.md",
)

# 契约全集：编号形态与"骨架=契约"的集合差判定用（集合内容本身一律从骨架/图实读，勿在此写死）
STATE_ID_RE = re.compile(r"^D15-S\d{1,2}$")
TRANSITION_ID_RE = re.compile(r"^D15-M\d{2}$")
EDGE_ID_RE = re.compile(r"^D15-X\d{2}$")
FACE_ID_RE = re.compile(r"^D15-G\d{2}$")
CARD_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){1,4}$")
# SSoT 注：canonical rule_patterns.MODULE_ID_RE 为 YAML 行提取语义，与本文件正则不等价，故本地改名免 SSOT-REDEFINITION
MODULE_ID_RE_LOCAL = re.compile(r"^MOD-[A-Z0-9][A-Z0-9_-]*$")
_OTHER_KEY_PATTERNS = {
    "candidate_id(CAND-*)": re.compile(r"^CAND-"),
    "node_id(TDM-*)": re.compile(r"^TDM-"),
    "node_id(FAC-*)": re.compile(r"^FAC-"),
    "step_id(BM-*)": re.compile(r"^BM-"),
    "step_id(D14-*)": re.compile(r"^D14-"),
    "module_id(MOD-*)": re.compile(r"^MOD-"),
    "data_step(DS-*)": re.compile(r"^DS-"),
}
# 六处分裂面的契约号（簿03 §A 实测把普查的"三处"改判为六处；增删须先回写作业簿）
GAP_UNIVERSE: tuple[str, ...] = tuple(f"D15-G{i:02d}" for i in range(1, 7))

REQUIRED_TOP = [
    "schema_version",
    "map_id",
    "name_zh",
    "effective_from",
    "markets",
    "generator",
    "generated_at",
    "registry_host",
    "anchor_source",
    "anchor_block_origin",
    "derived_from",
    "ssot_note_zh",
    "laws",
    "boundary",
    "instance_key_space",
    "states",
    "transitions",
    "forbidden_edges",
    "gaps",
    "revival_authorizations",
    "corpus",
    "counts",
    "pending_registration",
]
# L0 通用层统一名（六图终局卷 §1 裁定一）：状态/边/面三类对象共用同一套必填名
REQUIRED_ITEM = [
    "name_zh",
    "node_type",
    "decision_question",
    "note_zh",
    "confidence",
    "verified_scope",
    "source_anchors",
    "doc_refs",
    "module_id",
    "module_ref",
    "build_status",
    "gap_refs",
    "red_reason",
    "evidence",
]
# 其中值不得为空者（module_id/module_ref/red_reason/verified_scope 允许 null 但键必须在）
REQUIRED_NONEMPTY = {
    "name_zh",
    "node_type",
    "decision_question",
    "note_zh",
    "confidence",
    "source_anchors",
    "build_status",
}
REQUIRED_KEY_PRESENT = [
    "machine_readable",
    "from_state",
    "to_state",
    "edge_kind",
    "actor",
    "credential_required",
    "gated",
    "enforcement",
    "bypass_guard",
    "checker",
    "terminal",
    "value",
    "map_state",
    "credential_exemption",
    "skeleton_status",
]
# 废止别名（同义异名归一后不得残留）——出现即红（六图终局卷 §1 裁定一）
BANNED_FIELDS = {
    "mech_note_zh": "note_zh",
    "semantics_zh": "note_zh",
    "clock_semantics_zh": "note_zh",
    "design_refs": "doc_refs",
    "doc_ref": "doc_refs",
    "miss_fallback_zh": "fallback",
    "degradation": "fallback",
    "silent_failover": "fallback",
}
CROSS_DOMAIN_FIELDS = ("judgment_basis", "factor_refs", "strategy_refs")
NODE_TYPES = {"state", "gap"}
BUILD_STATUS = {"built", "partial", "pending"}
CONFIDENCE = {"verified", "proposed", "untested"}
VERIFIED_SCOPE = {"production", "structure"}
RED_REASONS = {"terminal", "unwired", "broken_supply", "ghost_ref"}
EDGE_KINDS = {"permitted", "forbidden"}
ACTORS = {"human", "ai", "machine"}
CREDENTIAL_KINDS = {"ruling", "owner_sign", "test_evidence", "machine", "none"}
ENFORCEMENT = {"machine_checkable", "declared_only", "live_incident_observed"}
MACHINE_READABLE = {"yes", "partial", "no"}
ANCHOR_SOURCES = {"proposal", "registry"}
# 人凭证集：禁止边"不可被绕过"判定的闸门定义（无凭证边不算闸门；机判判定书与裁定同为闸门）
HUMAN_GATE_KINDS = {"ruling", "owner_sign"}
QUALIFYING_GATE_KINDS = {"ruling", "owner_sign", "test_evidence"}
# 终态卡的可追加字段白名单（规格 §2 lives_in/viability_verdict/derived_by 是派生或追加面）
APPENDABLE_TERMINAL_FIELDS = {
    "lives_in",
    "viability_verdict",
    "derived_by",
    "history_from",
    "card_id",
    "entry_kind",
    "family_id",
    "hypothesis_key",
    "n_eff",
    "note_zh",
    "status_note",
}
MAX_LEN = 120  # 规格 CV-12：字符串字段 ≤120 字（图9 判据同源）
_INV1_WINDOW = 40
_INV1_MIN = 40
_DISK_EXEMPT_PREFIXES = (".runtime/", ".aidrafts", "F:", "G:", "f:", "g:")
_TRACKED_PREFIXES = ("docs/", "config/", "scripts/", "src/", "tests/", "data/", "architecture_model/")
_STATE_ROW_RE = re.compile(r"^\|\s*D15-S\d{1,2}\s*\|")
_M_ROW_RE = re.compile(r"^\|\s*D15-M\d{2}\s*\|")
_X_ROW_RE = re.compile(r"^\|\s*D15-X\d{2}\s*\|")


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 装载点（宿主词表优先，回落提案件）——唯一真源，生成器同源复用，禁复制
# ---------------------------------------------------------------------------
def load_anchor_block(root: Path, warnings: list[str] | None = None) -> tuple[str, dict[str, Any]]:
    """状态词表 + 实例台账的装载：registry 面（宿主已扩）优先，proposal 面回落。

    返回 (anchor_source, block)。两面都读不到 ⇒ ("", {})，调用方降 warn（禁环境异常打死提交）。
    **禁止在此写任何状态字面量**——值集 100% 来自装载点，否则 CV-02 的动态加载红证失效。

    registry 期（宿主已扩枚举）的两面真源：
      值集=_registry/vocabularies/card_state_vocabulary.yaml（受控词表在册面）
      实例=catalogs/experiment_registry.yaml 的 CARD-* 契约条目（登记面在册条目）
    提案件此时**只**继续提供非状态类的施工口径（语料口径 §9 / 卡头别名规则 §4 /
    六处分裂面 §5 / 复活授权 §7 注 / 宿主锚 §1）——词表与实例面不再回读它，禁双源。
    """
    reg = root / _REGISTRY_VOCAB_REL
    if reg.exists():
        try:
            d = _load_yaml(reg) or {}
            if isinstance(d, dict) and isinstance(d.get("values"), list) and d["values"]:
                host = _load_yaml(root / _REGISTRY_HOST_REL) if (root / _REGISTRY_HOST_REL).exists() else {}
                entries = (host or {}).get("experiments") or []
                caliber: dict[str, Any] = {}
                if (root / _PROPOSAL_REL).exists():
                    caliber = _load_yaml(root / _PROPOSAL_REL) or {}
                return "registry", {
                    "values": d["values"],
                    "card_entries": [
                        e
                        for e in entries
                        if isinstance(e, dict) and str(e.get("experiment_id", "")).startswith("CARD-")
                    ],
                    "revival_authorizations": caliber.get("revival_authorizations") or [],
                    "proposal": caliber,
                }
        except Exception as e:  # noqa: BLE001 — 宿主面损坏=回落提案件，不静默判通过
            if warnings is not None:
                warnings.append(f"宿主词表不可装载（{_REGISTRY_VOCAB_REL}）: {e}")
    pro = root / _PROPOSAL_REL
    if pro.exists():
        try:
            d = _load_yaml(pro) or {}
        except Exception as e:  # noqa: BLE001
            if warnings is not None:
                warnings.append(f"锚块提案件不可装载（{_PROPOSAL_REL}）: {e}")
            return "", {}
        if isinstance(d, dict):
            vocab = ((d.get("card_state_vocabulary") or {}).get("values")) or []
            return "proposal", {
                "values": vocab,
                "card_entries": d.get("card_entries") or [],
                "revival_authorizations": d.get("revival_authorizations") or [],
                "proposal": d,
            }
    return "", {}


def state_values(block: dict[str, Any]) -> set[str]:
    return {str(v.get("value")) for v in block.get("values") or [] if isinstance(v, dict) and v.get("value")}


def host_contract_entries(root: Path) -> list[dict[str, Any]]:
    """宿主册 CARD-* 契约条目现读（registry 面的实例真源；装载失败=空表，调用方判红/降 warn）。"""
    p = root / _REGISTRY_HOST_REL
    if not p.exists():
        return []
    try:
        host = _load_yaml(p) or {}
    except Exception:  # noqa: BLE001 — 册损坏由 CV-HOST 的装载腿显性判红
        return []
    return [
        e
        for e in (host.get("experiments") or [])
        if isinstance(e, dict) and str(e.get("experiment_id", "")).startswith("CARD-")
    ]


def registry_face_problems(root: Path, data: dict) -> list[str]:
    """CV-HOST 的 registry 期两腿（91 号件 host_migration_checklist.regression_when_landed）。

    图声称宿主已落地（anchor_source=registry）时，宿主两面必须真的在盘且有内容：
    ①词表装载点 `_registry/vocabularies/card_state_vocabulary.yaml` 可装载且值集非空；
    ②宿主册有 CARD-* 契约条目（登记面实例真源已存在，不是空壳）；
    ③登记欠账必须清空（unregistered_declarable==[]——卡头可判态却无册条目=回填偷懒，禁"忘了就绿"）。
    三形皆是"声称已切源而实面未切"=假迁移，error 级，不降 warn（warn 只留给外部真源不可达）。
    """
    errors: list[str] = []
    vp = root / _REGISTRY_VOCAB_REL
    try:
        vocab = _load_yaml(vp) if vp.exists() else None
    except Exception as e:  # noqa: BLE001
        return [f"CV-HOST——宿主词表解析失败（{vp.name}）: {e}"]
    if not vp.exists() or not isinstance(vocab, dict) or not (vocab.get("values") or []):
        errors.append(
            f"CV-HOST——anchor_source=registry 而宿主词表不可装载（{_REGISTRY_VOCAB_REL}）"
            "=词表装载点未切到 registry 面（假迁移）"
        )
    if not host_contract_entries(root):
        errors.append(
            f"CV-HOST——anchor_source=registry 而宿主册无 CARD-* 契约条目（{_REGISTRY_HOST_REL}）=实例面未落地（假迁移）"
        )
    pend = data.get("pending_registration")
    if isinstance(pend, dict):
        debt = pend.get("unregistered_declarable")
        if debt is None:
            errors.append("CV-HOST——registry 期 pending_registration 缺 unregistered_declarable 位（欠账面不得隐身）")
        elif debt:
            errors.append(
                f"CV-HOST——registry 期登记欠账未清空 "
                f"unregistered_declarable={len(debt)} 项（宿主已落地却仍有可判态卡未入册）"
            )
    return errors


def terminal_values(block: dict[str, Any]) -> set[str]:
    return {str(v.get("value")) for v in block.get("values") or [] if isinstance(v, dict) and v.get("terminal") is True}


# ---------------------------------------------------------------------------
# 骨架实扫（双轴与覆盖度的对照真源；不可读=空表，调用方降 warn）
# ---------------------------------------------------------------------------
def _cells(line: str, ncols: int) -> list[str]:
    """MD 表行 → 逻辑列清单（多成员 `from→to` 单元格里的裸竖线会切碎列，先归并再取列）。"""
    parts = [c.strip() for c in str(line).strip().strip("|").split("|")]
    if len(parts) > ncols:
        extra = len(parts) - ncols
        parts = [parts[0], "|".join(parts[1 : 2 + extra])] + parts[2 + extra :]
    return parts


def _rows(text: str, marker: str, stop: str, row_re: re.Pattern[str], ncols: int) -> list[list[str]]:
    i = text.find(marker)
    if i < 0:
        return []
    body = text[i + len(marker) :]
    j = body.find(stop)
    if j > 0:
        body = body[:j]
    return [_cells(line, ncols) for line in body.split("\n") if row_re.match(line)]


def scan_skeleton_axes(root: Path) -> dict[str, Any]:
    """骨架 §1 机可读列 + §2.1 实查列 + §2.2 禁边实查列 + 三表编号全集（同源对照面）。"""
    p = root / _SKELETON_REL
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    states: dict[str, str] = {}
    for c in _rows(text, "## §1 状态全集", "## §2", _STATE_ROW_RE, 7):
        if len(c) > 6:
            states[c[0]] = c[6].split("（")[0].strip()
    trans: dict[str, str] = {}
    for c in _rows(text, "### 2.1 合法边", "### 2.2", _M_ROW_RE, 6):
        if len(c) > 5:
            trans[c[0]] = c[5][:1].strip()
    forb: dict[str, str] = {}
    for c in _rows(text, "### 2.2 禁止边全集", "**迁移计数**", _X_ROW_RE, 4):
        if len(c) > 3:
            forb[c[0]] = c[3][:1].strip()
    return {
        "states": states,
        "transitions": trans,
        "forbidden": forb,
        "state_ids": set(states),
        "transition_ids": set(trans),
        "forbidden_ids": set(forb),
        "production_transitions": {k for k, v in trans.items() if v == "✅"},
        "production_forbidden": {k for k, v in forb.items() if v == "✅"},
    }


def _scan_id_set(root: Path, rel: str, pattern: str) -> set[str]:
    """CLONEGUARD 合并整改：scan_ruling_ids/_load_registry_runs 同构体委托本 helper（单源）。"""
    p = root / rel
    if not p.exists():
        return set()
    return set(re.findall(pattern, p.read_text(encoding="utf-8", errors="replace")))


def scan_ruling_ids(root: Path) -> set[str]:
    return _scan_id_set(root, _RULING_REGISTRY_REL, r"ruling_id:\s*'?(\u88c1\u5b9a#\d+)")


def scan_module_id_index(root: Path) -> dict[str, str]:
    p = root / _PATH_OWNERSHIP_REL
    if not p.exists():
        return {}
    try:
        data = _load_yaml(p) or {}
    except Exception:  # noqa: BLE001 — 册不可解析=本面降级空表（CV-BUS 降 warn）
        return {}
    out: dict[str, str] = {}
    for e in data.get("ownership") or []:
        if not isinstance(e, dict) or e.get("claim_type") != "depgraph_node":
            continue
        path, mid = e.get("path"), e.get("owner_blueprint")
        if isinstance(path, str) and isinstance(mid, str) and mid.startswith("MOD-"):
            out.setdefault(path.replace("\\", "/"), mid)
    return out


def depgraph_missing_module_ids(module_ids: list[str], root: Path) -> list[str] | None:
    """depgraph 在册性（PG 不可达=None=调用方降 warn，不升级为 error）。"""
    want = sorted({m for m in module_ids if m})
    if not want:
        return []
    try:
        if str(root / "src") not in sys.path:
            sys.path.insert(0, str(root / "src"))
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: PLC0415

        conn = get_depgraph_pg_connection()
    except Exception:  # noqa: BLE001 — 依赖不可达≠图有错
        return None
    try:
        found = {r[0] for r in conn.execute(_SQL_MODULE_ID_LIST % ",".join(["%s"] * len(want)), want)}
    except Exception:  # noqa: BLE001
        return None
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass
    return [m for m in want if m not in found]


def _anchor_path(ref: str) -> str:
    s = str(ref or "").strip().strip("'\"")
    s = re.split(r"#L\d", s)[0]
    s = re.split(r":\d", s)[0]
    m = re.match(r"(?:^|[\s(])([A-Za-z0-9_./\\-]+\.(?:md|yaml|yml|py|csv|ps1|json|sql))", s)
    if m:
        return m.group(1).replace("\\", "/")
    return s.replace("\\", "/") if s.startswith(_TRACKED_PREFIXES) else ""


def _is_checkable_disk_path(p: str) -> bool:
    return bool(p) and p.startswith(_TRACKED_PREFIXES) and not p.startswith(_DISK_EXEMPT_PREFIXES)


def _norm(p: str) -> str:
    return str(p or "").replace("\\", "/").strip()


def _copy_hit(text: str, bodies: list[str], window: int = _INV1_WINDOW) -> str | None:
    """40 字滑窗命中判据正文（INV-1 / X11）。"""
    t = re.sub(r"\s+", "", text)
    if len(t) < window:
        return None
    for body in bodies:
        b = re.sub(r"\s+", "", body)
        for i in range(0, max(0, len(b) - window) + 1, 8):
            if b[i : i + window] in t:
                return b[i : i + window]
    return None


def _policy_bodies(root: Path) -> tuple[list[str], bool]:
    bodies: list[str] = []
    ok = False
    for rel in _INV1_CORPUS_RELS:
        p = root / rel
        if not p.exists():
            continue
        ok = True
        for seg in re.split(r"\n(?=#{1,3} )", p.read_text(encoding="utf-8", errors="replace")):
            if len(re.sub(r"\s+", "", seg)) >= _INV1_WINDOW:
                bodies.append(seg)
    return bodies, ok


# ---------------------------------------------------------------------------
# 结构面（图自身）
# ---------------------------------------------------------------------------
def validate_structure(
    data: dict,
    root: Path | None = None,
    warnings: list[str] | None = None,
    live: bool = True,
    block: dict[str, Any] | None = None,
) -> list[str]:
    """结构契约唯一真源（gate / align_all / CLI 三方同源动态 import，禁复制判据）。

    live=False（gate 与提交面）只跳**磁盘实存与在册探活类**腿（CV-16/17/18、PG 探活、
    INV-1 滑窗语料），结构面（枚举/状态机良构/禁边闭合与绕过/双轴/计数/长度）一项不放宽。
    """
    errors: list[str] = []
    root = root or _REPO_ROOT
    for k in REQUIRED_TOP:  # CV-01
        if k not in data:
            _err(errors, f"缺顶层必填键: {k}")
    if errors:
        return errors
    if not data.get("laws") or not data.get("boundary"):  # CV-15
        _err(errors, "CV-15——laws 与 boundary 均不得为空")
    if not data.get("revival_authorizations"):
        _err(errors, "revival_authorizations（复活授权裁定集）不得为空——CV-06 的输入面")

    # --- CV-HOST 宿主与回落判据 ---
    host, anchor = str(data.get("registry_host")), str(data.get("anchor_source"))
    if anchor not in ANCHOR_SOURCES:
        _err(errors, f"anchor_source 非法 {anchor!r}（须 proposal=回落提案件 / registry=宿主已扩）")
    if not host.startswith(("proposed:", "experiment_registry")):
        _err(errors, f"registry_host 非法 {host!r}（唯一宿主=扩 experiment_registry，禁第二真源）")
    if host.startswith("proposed:") and anchor != "proposal":
        _err(errors, f"registry_host={host} 而 anchor_source={anchor}（未落地却称已切源=假迁移）")
    if host == "experiment_registry" and anchor != "registry":
        _err(
            errors,
            f"registry_host={host} 而 anchor_source={anchor}（声称宿主已扩却仍回落提案件=假迁移，两口径必须同批翻转）",
        )
    if anchor == "registry" and host != "experiment_registry":
        _err(errors, "anchor_source=registry 却 registry_host≠experiment_registry（两口径互斥）")
    declared_origin = _norm(data.get("anchor_block_origin"))
    if declared_origin and not (root / declared_origin).exists():
        _err(errors, f"CV-HOST——anchor_block_origin 声称的装载点不存在: {declared_origin}")
    if anchor == "registry":
        for msg in registry_face_problems(root, data):
            _err(errors, msg)
    elif not host_contract_entries(root) and (root / _REGISTRY_HOST_REL).exists():
        # proposal 期允许宿主未扩，但必须把"未扩"这件事说在图上（registry_host 带 proposed: 前缀）
        if not host.startswith("proposed:"):
            _err(errors, f"CV-HOST——宿主未扩却 registry_host={host}（proposed: 前缀是唯一诚实表述）")

    # --- 装载点（词表 + 实例种子）---
    loaded_src, loaded = (anchor, block or {}) if block else load_anchor_block(root, warnings)
    if block is not None:
        loaded_src = loaded_src or anchor
    if not loaded:
        if warnings is not None:
            warnings.append("词表与实例种子均不可装载（宿主册与提案件都读不到）：CV-02/CV-06/CV-08 的装载腿降 warn")
    vocab = state_values(loaded)
    term = terminal_values(loaded)

    states = data.get("states") or []
    transitions = data.get("transitions") or []
    forbidden = data.get("forbidden_edges") or []
    gaps = data.get("gaps") or []
    sv = {str(s.get("value")) for s in states if isinstance(s, dict)}
    sid = {str(s.get("state_id")) for s in states if isinstance(s, dict)}

    # --- CV-02 枚举闭集（图 states ↔ 装载点词表双向；值集绝不写死在本文件）---
    if vocab:
        for miss in sorted(sv - vocab):
            _err(errors, f"CV-02——图 states 值 {miss} 不在受控词表内（词表是唯一真源，禁自造值）")
        for miss in sorted(vocab - sv):
            _err(errors, f"CV-02——词表值 {miss} 未进图 states（词表有图无=状态机残缺）")
    if term:
        for s in states:
            if isinstance(s, dict) and bool(s.get("terminal")) != (str(s.get("value")) in term):
                _err(errors, f"CV-02——{s.get('state_id')} terminal 标记与词表不一致")
    for s in states:
        if not isinstance(s, dict):
            _err(errors, f"states 条目非对象: {s!r}")

    sk = scan_skeleton_axes(root)
    if not sk and warnings is not None:
        warnings.append(f"骨架不可读（{_SKELETON_REL}）：CV-13/CV-DUAL/CV-STATE 对照腿降 warn")

    # --- CV-03 标识唯一与形态 + CV-13 覆盖度 + 分组轴与 L0 必填 ---
    seen: dict[str, int] = Counter()
    for kind, items, key in (
        ("states", states, "state_id"),
        ("transitions", transitions, "transition_id"),
        ("forbidden_edges", forbidden, "edge_id"),
    ):
        for it in items:
            if isinstance(it, dict) and it.get(key):
                seen[str(it[key])] += 1
    for k, n in seen.items():
        if n > 1:
            _err(errors, f"CV-03——标识重复 {k}（{n} 次）")
        if not (STATE_ID_RE.match(k) or TRANSITION_ID_RE.match(k) or EDGE_ID_RE.match(k)):
            _err(errors, f"CV-03——标识形态非法 {k}（须 D15-S*/M**/X**）")
    for s in states:
        if isinstance(s, dict) and not STATE_ID_RE.match(str(s.get("state_id"))):
            _err(errors, f"CV-03——state_id 形态非法: {s.get('state_id')}")
    for t in transitions:
        if isinstance(t, dict) and not TRANSITION_ID_RE.match(str(t.get("transition_id"))):
            _err(errors, f"CV-03——transition_id 形态非法: {t.get('transition_id')}")
    for x in forbidden:
        if isinstance(x, dict) and not EDGE_ID_RE.match(str(x.get("edge_id"))):
            _err(errors, f"CV-03——edge_id 形态非法: {x.get('edge_id')}")
    if sk:
        named = {str(s.get("state_id")) for s in states if isinstance(s, dict)}
        for got, want, what in (
            (named, sk["state_ids"], "states"),
            (
                {str(t.get("transition_id")) for t in transitions if isinstance(t, dict)},
                sk["transition_ids"],
                "transitions",
            ),
            ({str(x.get("edge_id")) for x in forbidden if isinstance(x, dict)}, sk["forbidden_ids"], "forbidden_edges"),
        ):
            for miss in sorted(want - got):
                _err(errors, f"CV-13——骨架 §1/§2 声明的 {what} 编号未入图: {miss}（骨架=契约，增删须先回写骨架）")
            for extra in sorted(got - want):
                _err(errors, f"CV-13——图内 {what} 越出骨架契约全集: {extra}")

    # --- CV-L0 / CV-DOMAIN / 必填字段 / 长度 ---
    all_items = (
        [("state", s) for s in states]
        + [("transition", t) for t in transitions]
        + [("forbidden_edge", x) for x in forbidden]
        + [("gap", g) for g in gaps]
    )
    for kind, it in all_items:
        if not isinstance(it, dict):
            _err(errors, f"{kind} 条目非对象: {it!r}")
            continue
        iid = str(it.get("state_id") or it.get("transition_id") or it.get("edge_id") or it.get("gap_id") or kind)
        for banned, canon in BANNED_FIELDS.items():
            if banned in it:
                _err(errors, f"{iid}: CV-L0——字段旧名残留 {banned}（L0 统一名应为 {canon}）")
        for xf in CROSS_DOMAIN_FIELDS:
            if xf in it:
                _err(errors, f"{iid}: CV-DOMAIN——越域挂载禁字段 {xf}（考试判据真源在 exam_policy）")
        for f in REQUIRED_ITEM:
            if f not in it:
                _err(errors, f"{iid}: 缺必填字段 {f}（值可为 null，键必须在）")
                continue
            if f in REQUIRED_NONEMPTY and it[f] in (None, "", []):
                _err(errors, f"{iid}: 必填字段 {f} 不得为空")
        if it.get("verified_scope") is None and str(it.get("confidence")) == "verified":
            _err(errors, f"{iid}: verified 必带 verified_scope（六图终局卷 §3 双轴，缺轴即口径混用）")
        for f in ("decision_question", "note_zh", "rule_zh", "name_zh", "definition_zh"):
            v = str(it.get(f) or "")
            if len(v) > MAX_LEN:
                _err(
                    errors,
                    f"{iid}: CV-12 长度面——{f} 超 {MAX_LEN} 字（INV-1 反复制，图只存标识"
                    f"与指针，判据正文各归各库）: {len(v)} 字",
                )
        if str(it.get("build_status")) not in BUILD_STATUS:
            _err(errors, f"{iid}: build_status 非法 {it.get('build_status')!r}")
        if str(it.get("confidence")) not in CONFIDENCE:
            _err(errors, f"{iid}: confidence 非法 {it.get('confidence')!r}")
        if it.get("verified_scope") not in (None, *VERIFIED_SCOPE):
            _err(errors, f"{iid}: verified_scope 非法 {it.get('verified_scope')!r}")
        if str(it.get("confidence")) == "verified" and it.get("verified_scope") is None:
            _err(errors, f"{iid}: verified 必带 verified_scope（六图终局卷 §3 双轴，缺轴即口径混用）")
        if it.get("verified_scope") == "production" and str(it.get("confidence")) != "verified":
            _err(
                errors,
                f"{iid}: 谎——verified_scope=production 而 confidence="
                f"{it.get('confidence')!r}（production 必 verified）",
            )
        if it.get("verified_scope") == "production" and not (it.get("evidence") or []):
            _err(errors, f"{iid}: production 必带可复跑 evidence（禁凭散文宣在产）")
        if str(it.get("node_type")) not in NODE_TYPES | {"transition", "forbidden_edge"}:
            _err(errors, f"{iid}: node_type 非法 {it.get('node_type')!r}")
        if not (it.get("source_anchors") or []):
            _err(errors, f"{iid}: source_anchors 至少 1 条真源锚（L0 必填语义）")
        if not it.get("module_id") and not it.get("red_reason"):
            _err(errors, f"{iid}: CV-BUS——module_id 为空必配 red_reason（无实现代码要写因）")
        if it.get("module_ref") and not it.get("module_id"):
            _err(errors, f"{iid}: CV-BUS——module_ref 非空而 module_id 空（有码必挂 MOD-* 总线号）")
        if it.get("module_id") is not None and not MODULE_ID_RE_LOCAL.match(str(it.get("module_id"))):
            _err(errors, f"{iid}: CV-BUS——module_id 非 MOD-* 形态 {it.get('module_id')!r}（禁自造）")
        for a in it.get("source_anchors") or []:
            ap = _anchor_path(str(a))
            if ap and ap.startswith(_TRACKED_PREFIXES) and not (root / ap).exists():
                _err(errors, f"{iid}: 真源锚磁盘实存失败: {ap}")
    module_index = scan_module_id_index(root)
    if not module_index and warnings is not None:
        warnings.append(f"投影册不可读（{_PATH_OWNERSHIP_REL}）：CV-BUS 在册一致性腿降 warn")
    want_ids = [str(it.get("module_id")) for _, it in all_items if isinstance(it, dict) and it.get("module_id")]
    if live:
        miss = depgraph_missing_module_ids(sorted(set(want_ids)), root)
        if miss is None:
            if warnings is not None:
                warnings.append("depgraph（PG）不可达：module_id 在册性核对降 warn（形态与投影两腿仍硬过）")
        else:
            for m in miss:
                _err(errors, f"CV-BUS——module_id 不在 depgraph 在册: {m}（幽灵总线号，禁自造）")
    if module_index:
        for _, it in all_items:
            if not isinstance(it, dict) or not (it.get("module_id") and it.get("module_ref")):
                continue
            expect = module_index.get(_norm(it["module_ref"]).split(":")[0])
            if expect is not None and expect != it["module_id"]:
                _err(
                    errors,
                    f"{it.get('state_id') or it.get('transition_id') or it.get('edge_id')}: "
                    f"CV-BUS——module_id={it['module_id']} 与投影在册答案 {expect} 不一致",
                )

    # --- CV-FSM 状态机良构 + CV-04 图侧迁移合法性 ---
    perm_pairs: set[tuple[str, str]] = set()
    graph: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for t in transitions:
        if not isinstance(t, dict):
            continue
        tid = str(t.get("transition_id"))
        froms = t.get("from_state") or []
        froms = [froms] if isinstance(froms, str) else list(froms)
        to = str(t.get("to_state") or "")
        if not froms or not to:
            _err(errors, f"{tid}: CV-04——from_state 与 to_state 不得为空")
            continue
        if to in froms:
            _err(errors, f"{tid}: CV-FSM——自环迁移非法（frozen→frozen 即 X02 静默改，S4→S4 即 X08）")
        kind = str(t.get("edge_kind"))
        if kind != "permitted":
            _err(errors, f"{tid}: edge_kind={kind!r} 而条目在 transitions（三类不得混装）")
        cr = str(t.get("credential_required"))
        if cr not in CREDENTIAL_KINDS:
            _err(errors, f"{tid}: credential_required 非法 {cr!r}（枚举 {sorted(CREDENTIAL_KINDS)}）")
        if t.get("gated") is not (cr in HUMAN_GATE_KINDS):
            _err(
                errors,
                f"{tid}: gated 标记必须等于 credential_required 是否人凭证"
                "（禁止边绕过判定的闸门由此派生，禁手写两口径）",
            )
        for f in [x for x in froms + [to] if x is not None]:
            if f not in sv:
                _err(errors, f"{tid}: 迁移端点 {f} 不在图 states 值域内")
        if t.get("cross_instance"):
            # M17 复活边是**跨实例**边（旧卡终态 → 新卡 draft），不得进实例状态机图：
            # 进了就等于给"就地复活"开合法通道，CV-05/CV-07 的封卡即终随之失效
            continue
        for f in [x for x in froms if x is not None] or ["__entry__"]:
            perm_pairs.add((f, to))
            graph[f].append((to, tid))
        if None in froms:  # 入口边 ∅→S1 / ∅→S2
            perm_pairs.add(("__entry__", to))
    if not perm_pairs:
        _err(errors, "CV-FSM——transitions 为空，状态机无合法边")

    forb_pairs: set[tuple[str, str]] = set()
    for x in forbidden:
        if not isinstance(x, dict):
            continue
        xid = str(x.get("edge_id"))
        if str(x.get("edge_kind")) != "forbidden":
            _err(errors, f"{xid}: edge_kind 必须为 forbidden（三类不得混装）")
        froms = x.get("from_state") or []
        froms = [froms] if isinstance(froms, str) else list(froms)
        to = str(x.get("to_state") or "")
        if not froms or not to:
            _err(errors, f"{xid}: CV-07——禁止边必须可枚举（from_state 与 to_state 齐）")
            continue
        for f in [x for x in froms + [to] if x not in (None, "*")]:
            if f not in sv:
                _err(errors, f"{xid}: 禁止边端点 {f} 不在图 states 值域内")
        p = {(f, to) for f in froms}
        forb_pairs |= p
        overlap = p & perm_pairs
        for fa, ta in sorted(overlap):
            twin = _find(transitions, "to_state", ta)
            ok = twin is not None and str(twin.get("credential_required")) != "none"
            if not ok:
                _err(
                    errors,
                    f"{xid}: CV-07——禁止边与合法迁移同对并存 {(fa, ta)} 且该合法边无凭证"
                    "（同对既准又禁=判据自相矛盾；条件性禁令必须由凭证限定）",
                )
        if str(x.get("enforcement")) not in ENFORCEMENT:
            _err(errors, f"{xid}: enforcement 非法 {x.get('enforcement')!r}")
        if not x.get("bypass_guard"):
            _err(errors, f"{xid}: CV-07——禁止边必写 bypass_guard（声明它靠哪条人凭证闸门不被绕开）")
        if not x.get("checker"):
            _err(errors, f"{xid}: CV-07——禁止边必指 checker（CV-* 号），否则=不可判禁边静默丢弃")
    # 禁止边"不可被绕过边规避"：任何从 a 到 b 的图路径必须至少穿过一条人凭证边
    gated_pairs = {
        (str(f), str(t.get("to_state")))
        for t in transitions
        if isinstance(t, dict) and str(t.get("credential_required")) in QUALIFYING_GATE_KINDS
        for f in (t.get("from_state") or [])
    }
    for a, b in sorted(forb_pairs):
        if a == b or "*" in (a, b):
            continue  # 自环禁令与跨面禁令无"绕行路径"可言，判定入口在实例面
        path = _find_path(graph, a, b, gated_pairs)
        if path:
            _err(
                errors,
                f"CV-07——禁止边 ({a},{b}) 可被绕过边规避：存在不含人凭证闸门的全程合法路径 "
                + " -> ".join(path)
                + "（补 credential_required 或删该边，勿删禁边）",
            )

    # --- CV-FSM 终态与可达性 ---
    entry_states = {
        str(t.get("to_state")) for t in transitions if isinstance(t, dict) and t.get("from_state") == [None]
    }
    incoming = {dst for pair in graph.values() for dst, _tid in pair}
    for s in states:
        if not isinstance(s, dict):
            continue
        v = str(s.get("value"))
        out_edges = [tid for _dst, tid in graph.get(v, [])]
        if bool(s.get("terminal")) and out_edges:
            _err(errors, f"CV-FSM——终态 {v} 存在出边 {out_edges}（终态即封死，复活只走跨实例 M17）")
        if not bool(s.get("terminal")) and v not in incoming and v not in entry_states:
            _err(errors, f"CV-FSM——非终态 {v} 无任何入边（孤岛状态，迁移集未闭合）")
    for s in states:
        if isinstance(s, dict) and not s.get("terminal") and not _can_reach_terminal(graph, str(s.get("value")), term):
            _err(errors, f"CV-FSM——非终态 {s.get('value')} 走不到任何终态（状态机存在死循环分支）")

    # --- CV-GAP 六处分裂面 ---
    gap_ids = {str(g.get("gap_id")) for g in gaps if isinstance(g, dict)}
    for miss in sorted(set(GAP_UNIVERSE) - gap_ids):
        _err(errors, f"CV-GAP——分裂面未入图: {miss}（簿03 §A 六处面，一条不许丢）")
    for extra in sorted(gap_ids - set(GAP_UNIVERSE)):
        _err(errors, f"CV-GAP——分裂面越出契约全集: {extra}（增面须先回写作业簿）")
    for g in gaps:
        if not isinstance(g, dict):
            continue
        gid = str(g.get("gap_id"))
        if str(g.get("node_type")) != "gap":
            _err(errors, f"{gid}: 契约编号为分裂面但 node_type={g.get('node_type')!r}")
        if str(g.get("red_reason")) not in RED_REASONS:
            _err(errors, f"{gid}: 分裂面 red_reason 非法 {g.get('red_reason')!r}")
        if g.get("module_ref"):
            _err(errors, f"{gid}: 分裂面不得挂 module_ref（缺口没有实现代码可证）")
        refed = any(
            gid in (it.get("gap_refs") or []) for _, it in all_items if isinstance(it, dict) and it.get("gap_id") != gid
        )
        if not refed:
            _err(errors, f"{gid}: 分裂面必须被至少一个状态/迁移/禁边 gap_refs 引用（显性化不得孤岛）")

    # --- CV-DUAL 双轴 ⇔ 骨架实查列（逐条双向 + 计数）---
    if sk:
        for items, key, prod_set, table in (
            (transitions, "transition_id", sk["production_transitions"], "§2.1"),
            (forbidden, "edge_id", sk["production_forbidden"], "§2.2"),
        ):
            got = {
                str(it.get(key)) for it in items if isinstance(it, dict) and it.get("verified_scope") == "production"
            }
            for over in sorted(got - prod_set):
                _err(errors, f"CV-DUAL——{key} {over} 宣 production 而骨架 {table} 非 ✅（多了算谎）")
            for short in sorted(prod_set - got):
                _err(errors, f"CV-DUAL——骨架 {table} ✅ 的 {short} 未宣 production（少了算欠）")
        for s in states:
            if isinstance(s, dict) and s.get("verified_scope") == "production":
                _err(
                    errors,
                    f"CV-DUAL——状态 {s.get('state_id')} 不得宣 production：骨架 §1 无 ✅ 列，状态面只有结构性事实",
                )
        for s in states:
            if (
                isinstance(s, dict)
                and sk["states"].get(str(s.get("state_id")))
                and s.get("machine_readable") != sk["states"][str(s.get("state_id"))]
            ):
                _err(
                    errors,
                    f"CV-STATE——{s.get('state_id')} machine_readable="
                    f"{s.get('machine_readable')!r} 与骨架 §1 实扫列 "
                    f"{sk['states'][str(s.get('state_id'))]!r} 不一致（骨架=契约）",
                )

    # --- CV-11 键空间互斥 + CV-14 counts + CV-02 键在必须 ---
    iks = data.get("instance_key_space") or {}
    if not iks.get("disjoint_with"):
        _err(errors, "CV-11——instance_key_space.disjoint_with 不得为空（防撞第二真源）")
    for cid in iks.get("sample_ids") or []:
        for name, pat in _OTHER_KEY_PATTERNS.items():
            if pat.match(str(cid)):
                _err(errors, f"CV-11——card_id 样本 {cid} 命中他域键值域 {name}")
    counts = data.get("counts") or {}
    if isinstance(counts, dict):
        pairs = (
            ("total_states", len(states)),
            ("total_transitions", len(transitions)),
            ("total_forbidden_edges", len(forbidden)),
            ("total_gaps", len(gaps)),
            ("terminal_states", sum(1 for s in states if isinstance(s, dict) and s.get("terminal"))),
            ("total_edges", len(transitions) + len(forbidden)),
        )
        for k, real in pairs:
            if counts.get(k) != real:
                _err(
                    errors,
                    f"CV-14——counts.{k}={counts.get(k)} 与实数 {real} 不符（图 YAML 必经生成器再生，禁手改不回生成）",
                )
        by = counts.get("by_state") or {}
        cor = data.get("corpus") or {}
        if isinstance(by, dict):
            if counts.get("cards_total") != cor.get("n"):
                _err(errors, f"CV-14——counts.cards_total={counts.get('cards_total')} 与语料现算 {cor.get('n')} 不符")
            mapped_real = sum(1 for c in cor.get("cards") or [] if c.get("mapped_state"))
            if sum(by.values()) != mapped_real:
                _err(
                    errors,
                    f"CV-14——sum(by_state)={sum(by.values())} 与语料已落位数 "
                    f"{mapped_real} 不符（未落位者走 pending_registration，禁硬凑分母）",
                )
            for v, n in by.items():
                real = sum(1 for c in cor.get("cards") or [] if c.get("mapped_state") == v)
                if real != n:
                    _err(errors, f"CV-14——by_state[{v}]={n} 与语料现算 {real} 不符（散文写死数必漂）")
        prod_real = sum(
            1 for it in transitions + forbidden if isinstance(it, dict) and it.get("verified_scope") == "production"
        )
        if counts.get("production") != prod_real:
            _err(errors, f"CV-14——counts.production={counts.get('production')} 与实数 {prod_real} 不符")
    # --- CV-16 boundary 逐字回源 + CV-12 长度/滑窗 ---
    for b in data.get("boundary") or []:
        txt = str(b)
        m = re.search(r"([A-Za-z0-9_./\-]+\.(?:md|yaml|py))", txt)
        q = re.search(r"[\"“'](.{6,}?)[\"”']", txt)
        if m and not (root / m.group(1)).exists():
            _err(errors, f"CV-16——boundary 引用的源文件不存在: {m.group(1)}")
        elif m and q and live:
            body = (root / m.group(1)).read_text(encoding="utf-8", errors="replace")
            if _norm(q.group(1))[-40:] not in re.sub(r"\s+", "", body):
                _err(errors, f"CV-16——boundary 引文在 {m.group(1)} 未命中（逐字引用禁意译）")
    bodies, ok = _policy_bodies(root)
    if ok and live:
        for _, it in all_items:
            if not isinstance(it, dict):
                continue
            for f in ("name_zh", "decision_question", "note_zh", "rule_zh", "definition_zh"):
                v = str(it.get(f) or "")
                if len(re.sub(r"\s+", "", v)) < _INV1_MIN:
                    continue
                hit = _copy_hit(v, bodies)
                if hit:
                    _err(
                        errors,
                        f"{it.get('state_id') or it.get('transition_id') or it.get('edge_id')}"
                        f": CV-12 INV-1——{f} 含判据正文连续 {len(hit)} 字: {hit[:32]}…",
                    )
    elif warnings is not None and not ok:
        warnings.append("INV-1 语料（exam_policy / factor_mining_sop_policy）不可读：滑窗腿降 warn")
    for f in ("counts", "corpus", "pending_registration"):
        if not isinstance(data.get(f), (dict, list)):
            _err(errors, f"{f} 必须是映射或清单（现算面）")
    return errors


def _find_path(
    graph: dict[str, list[tuple[str, str]]], src: str, dst: str, gated: set[tuple[str, str]], max_depth: int = 5
) -> list[str] | None:
    """BFS：src→dst 的**全程不含人凭证闸门边**的路径（禁止边绕过探针）。"""
    if src == dst:
        return [src]
    stack: list[list[str]] = [[src]]
    while stack:
        path = stack.pop(0)
        cur = path[-1]
        if len(path) > max_depth:
            continue
        for nxt, _tid in graph.get(cur, []):
            if (cur, nxt) in gated or nxt in path:
                continue
            if nxt == dst:
                return path + [nxt]
            stack.append(path + [nxt])
    return None


def _can_reach_terminal(graph: dict[str, list[tuple[str, str]]], src: str, term: set[str]) -> bool:
    seen, stack = set(), [src]
    while stack:
        cur = stack.pop()
        for nxt, _ in graph.get(cur, []):
            if nxt in term:
                return True
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return src in term


def _err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _find(items: list[Any], key: str, val: Any) -> dict | None:
    for it in items:
        if isinstance(it, dict) and it.get(key) == val:
            return it
    return None


# ---------------------------------------------------------------------------
# 实例面（登记台账）——回炉后的 CV-05/06/07/08/09/10 全在这里
# ---------------------------------------------------------------------------
def check_instances(
    entries: list[dict],
    data: dict,
    root: Path | None = None,
    warnings: list[str] | None = None,
    live: bool = True,
    block: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """实例判据（禁就地改状态：本函数只读 entries，绝不返回被修改过的条目）。

    返回 (errors, warnings_extra)。gate 不调本函数（全仓扫描语义），CLI 与 align_all 调。
    """
    errors: list[str] = []
    warns: list[str] = []
    root = root or _REPO_ROOT
    _src, loaded = block if block is not None else load_anchor_block(root, warnings)
    term = terminal_values(loaded) or {
        str(s.get("value")) for s in data.get("states") or [] if isinstance(s, dict) and s.get("terminal")
    }
    exempt = {
        str(s.get("value")) for s in data.get("states") or [] if isinstance(s, dict) and s.get("credential_exemption")
    }
    perm = set()
    one_time = {}
    for t in data.get("transitions") or []:
        if not isinstance(t, dict):
            continue
        for f in t.get("from_state") or []:
            perm.add((str(f), str(t.get("to_state"))))
            if t.get("one_time_token"):
                one_time[(str(f), str(t.get("to_state")))] = str(t["one_time_token"])
    forbidden = {}
    for x in data.get("forbidden_edges") or []:
        if not isinstance(x, dict):
            continue
        for f in x.get("from_state") or []:
            forbidden[(str(f), str(x.get("to_state")))] = str(x.get("edge_id"))
    ruling_ids = scan_ruling_ids(root)
    if not ruling_ids and warnings is not None:
        warnings.append("裁定册不可读：CV-09 在册性腿降 warn（在册即凭证，禁凭记忆放行）")
    entry_ids = {str(e.get("card_id")) for e in entries if isinstance(e, dict)}
    family_of: dict[str, set[str]] = defaultdict(set)
    for e in entries:
        if isinstance(e, dict) and e.get("family_id"):
            family_of[str(e["family_id"])].add(str(e.get("card_id")))

    # --- CV-03 卡号形态与前缀互斥 ---
    vocab = state_values(loaded)
    for e in entries:
        cid = str(e.get("card_id") or "")
        if not CARD_ID_RE.match(cid):
            errors.append(f"CV-03——card_id 形态非法: {cid!r}（业务键须大写字母-数字段，禁中文名）")
        if str(e.get("experiment_id") or "").startswith("EXP-"):
            errors.append(f"CV-03——契约条目 {cid} 的 experiment_id 用了 EXP- 前缀（CARD-/EXP- 必须互斥）")
        # CV-02 实例腿（90 号件 §5：card_state 必须命中受控词表，值集一律动态装载禁写死）
        st = e.get("card_state")
        if vocab and str(st) not in vocab:
            errors.append(f"CV-02——{cid} 的 card_state={st!r} 不在受控词表装载面内（登记面禁自造状态值）")

    # --- CV-04/05/06/07 逐条流水 ---
    for e in entries:
        cid = str(e.get("card_id"))
        state = str(e.get("card_state"))
        creds = [c for c in (e.get("credential") or []) if isinstance(c, dict)]
        path = [f"{c.get('from')}@{c.get('seq')}" for c in creds] + [state]
        for i, c in enumerate(creds):
            frm, to = str(c.get("from")), str(c.get("to"))
            pair = (frm, to)
            if pair in forbidden:  # CV-07 禁边出现即红（点名 X 号）
                errors.append(
                    f"CV-07——{cid} 第 {c.get('seq')} 跳 {frm}->{to} 命中禁止边 "
                    f"{forbidden[pair]}（禁边不可豁免，也不可用中间态绕行）"
                )
            if pair not in perm:  # CV-04 非法迁移
                errors.append(
                    f"CV-04——{cid} 第 {c.get('seq')} 跳 {frm}->{to} 不在图 transitions（非法迁移，须先有合法边与凭证）"
                )
            if to not in (state,) and i == len(creds) - 1:
                errors.append(f"CV-10——{cid} 末跳 to_state={to} 与登记 card_state={state} 不一致")
            rid = c.get("ruling_id")
            if rid:  # CV-09 在册性
                if ruling_ids and str(rid) not in ruling_ids:
                    errors.append(
                        f"CV-09——{cid} 第 {c.get('seq')} 跳凭证 {rid} 不在册（RULE-RULING 同源，禁第二套引用判据）"
                    )
            elif c.get("flag") in (None, "none", ""):
                warns.append(f"{cid} 第 {c.get('seq')} 跳无凭证（flag:none 计红账，不阻断）")
        hops = Counter((str(c.get("from")), str(c.get("to"))) for c in creds)
        for pair, tok in one_time.items():  # M10 一次性令牌全局唯一
            if hops[pair] > 1:
                errors.append(
                    f"CV-05——{cid} 一次性令牌 {tok} 对应迁移 {pair[0]}->{pair[1]} "
                    f"在本卡流水中出现 {hops[pair]} 次（全局唯一，再判即 X03/X01）"
                )
        seq_states = [str(c.get("from")) for c in creds] + ([state] if creds else [])
        for a, b in pairwise(seq_states):
            if a in term and b not in term:
                errors.append(
                    f"CV-05——{cid} 状态从终态 {a} 回到非终态 {b}：封卡就地复活（唯一出路是跨实例 M17 指向新卡 id）"
                )
        # CV-06 复活判定（回炉口径：三元命中，不靠 family_id 等值）
        cites = set(str(x) for x in (e.get("parent_context_cites") or []))
        for c in creds:
            if c.get("ruling_id"):
                cites.add(str(c["ruling_id"]))
        revived_auth = {str(a) for a in data.get("revival_authorizations") or []}
        text_blob = " ".join(
            [str(e.get("parent_context") or ""), str(e.get("status_note") or "")]
            + [f"{l.get('path')}" for l in e.get("lives_in") or []]
        )
        hit_terminal_card = next(
            (c for c in entry_ids if c != cid and c in text_blob and _state_of(entries, c) in term), None
        )
        hit_terminal_family = next(
            (
                f
                for f, members in family_of.items()
                if f in text_blob
                and f != e.get("family_id")
                and all(_state_of(entries, m) in term for m in members)
                and members
            ),
            None,
        )
        triggered = (
            bool(e.get("revives")) or bool(cites & revived_auth) or bool(hit_terminal_card) or bool(hit_terminal_family)
        )
        if triggered:
            rv = e.get("revives")
            if not rv:
                why = (
                    ("引用了复活授权 " + ",".join(sorted(cites & revived_auth)))
                    if cites & revived_auth
                    else ("文本命中终态卡 " + str(hit_terminal_card))
                    if hit_terminal_card
                    else ("文本命中终态族 " + str(hit_terminal_family))
                    if hit_terminal_family
                    else "自带 revives 字段"
                )
                errors.append(
                    f"CV-06——{cid} 命中复活判据（{why}）而 revives 缺省：X13"
                    "（复活必指向新卡 id 之外的旧卡号，否则同一死假设可被当新假设再考）"
                )
            else:
                if str(rv) == cid:
                    errors.append(f"CV-06——{cid} 的 revives 指向自身（就地复活，X03/X13 双违）")
                elif str(rv) not in entry_ids:
                    errors.append(f"CV-06——{cid} 的 revives={rv} 在台账查无该卡（断链指针）")
                elif _state_of(entries, str(rv)) not in term:
                    errors.append(
                        f"CV-06——{cid} 的 revives={rv} 未处于终态（"
                        "复活口只开给终态契约，其余为派生，须走 derived_from）"
                    )
        # CV-05 字段级：终态卡除可追加面外不得有变更记录
        if state in term:
            for ch in e.get("field_changes") or []:
                fld = str((ch or {}).get("field") or "")
                if fld and fld not in APPENDABLE_TERMINAL_FIELDS:
                    errors.append(
                        f"CV-05——{cid} 已处终态 {state} 仍变更字段 {fld}"
                        f"（可追加集={sorted(APPENDABLE_TERMINAL_FIELDS)}）"
                    )

    # --- CV-08 三条独立腿（回炉：读三元组与假设身份，不读单字段等值）---
    by_hyp: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        hk = e.get("hypothesis_key")
        if str(e.get("card_state")) in term:
            continue
        if str(e.get("entry_kind")) != "single_hypothesis":
            continue
        if hk:
            by_hyp[str(hk)].append(str(e.get("card_id")))
        else:
            warns.append(f"CV-08A——{e.get('card_id')} 无 hypothesis_key（假设身份不可判，只计红账不猜）")
    for hk, cards in sorted(by_hyp.items()):
        if len(set(cards)) > 1:
            errors.append(f"CV-08——X09 同一假设双卡（N_eff 双重计分）：hypothesis_key={hk} 命中 {sorted(set(cards))}")
    owner: dict[str, str] = {}
    for e in entries:
        for l in e.get("lives_in") or []:
            owner[_norm((l or {}).get("path"))] = str(e.get("card_id"))
    for e in entries:  # B 腿：卡号↔文件↔判决三元对齐
        cid = str(e.get("card_id"))
        for b in e.get("verdict_bindings") or []:
            if not isinstance(b, dict):
                continue
            ep = _norm(b.get("evidence_path"))
            if not ep:
                errors.append(f"CV-08B——{cid} 的判决绑定缺 evidence_path（三元组读不全）")
                continue
            own = owner.get(ep)
            if own and own != cid:
                errors.append(
                    f"CV-08B——卡号↔文件↔判决三元错绑：{cid} 的 verdict="
                    f"{b.get('verdict')} 证据件 {Path(ep).name} 实为 {own} 所属文件"
                    f"（{b.get('defect_ref') or 'F-07 同型'}）"
                )
            elif not own and not (b.get("ruling_id") or b.get("report_path")):
                warns.append(f"CV-08B——{cid} 判决件 {ep} 无所属卡且无裁定引用（悬空判决）")
            if b.get("ruling_id") and ruling_ids and str(b["ruling_id"]) not in ruling_ids:
                errors.append(f"CV-09——{cid} 判决绑定引用未在册裁定号 {b['ruling_id']}")
    for e in entries:  # C 腿输入：族成员取语料全量（非种子局部）
        pass
    corpus_families = (data.get("corpus") or {}).get("families") or {}
    fam_iter = (
        {
            k: {
                "single_hypothesis_members": v.get("single_hypothesis_members", 0),
                "declared_n_eff": v.get("declared_n_eff") or [],
            }
            for k, v in corpus_families.items()
        }
        if corpus_families
        else {
            f: {
                "single_hypothesis_members": len(
                    [m for m in ms if str((_entry(entries, m) or {}).get("entry_kind")) == "single_hypothesis"]
                ),
                "declared_n_eff": sorted({_n_eff(_entry(entries, m)) for m in ms} - {None}),
            }
            for f, ms in family_of.items()
        }
    )
    for fam, info in sorted(fam_iter.items()):
        singles = int(info.get("single_hypothesis_members") or 0)
        declared = sorted({d for d in (info.get("declared_n_eff") or []) if isinstance(d, int)})
        if declared and singles != declared[0]:
            errors.append(
                f"CV-08C——族 {fam} 的单假设成员数 {singles} ≠ 声明 n_eff {declared[0]}"
                "（N_eff 封闭族账不平；族级文书不计入成员）"
            )
    for e in entries:  # D 腿：n_eff 缺声明只 warn
        if _n_eff(e) is None:
            warns.append(f"CV-08D——{e.get('card_id')} n_eff 未声明（计红账，禁默认 1）")
        if str(e.get("card_state")) not in exempt and not (e.get("credential") or []):
            errors.append(
                f"CV-09——{e.get('card_id')} 处于 {e.get('card_state')} 却无迁移凭证"
                "（免凭证状态由图 credential_exemption 声明，禁写死）"
            )

    # --- CV-10 三处一致性（镜像==真源、run→卡外键、viability_verdict 映射）---
    legacy_map = {
        "supported": [
            str(s.get("value"))
            for s in data.get("states") or []
            if isinstance(s, dict) and s.get("legacy_field") and "supported" in str(s["legacy_field"])
        ],
        "refuted": [
            str(s.get("value"))
            for s in data.get("states") or []
            if isinstance(s, dict) and s.get("legacy_field") and "refuted" in str(s["legacy_field"])
        ],
        "inconclusive": [
            str(s.get("value"))
            for s in data.get("states") or []
            if isinstance(s, dict) and s.get("legacy_field") and "inconclusive" in str(s["legacy_field"])
        ],
    }
    for e in entries:
        cid = str(e.get("card_id"))
        face = e.get("card_face_state")
        if face and face != e.get("card_state"):
            errors.append(
                f"CV-10——{cid} 卡面镜像 {face} ≠ 登记真源 {e.get('card_state')}"
                "（派生面与真源冲突，F-03 同型；方向恒为 册→md）"
            )
        vv = e.get("viability_verdict")
        st = str(e.get("card_state"))
        if vv and legacy_map.get(str(vv)) and st not in legacy_map[str(vv)]:
            errors.append(f"CV-10——{cid} viability_verdict={vv} 与 card_state={st} 映射不一致")
        for run in e.get("runs") or []:
            rid = _norm((run or {}).get("experiment_id") or (run or {}).get("run_id"))
            if rid and not rid.startswith("EXP-"):
                errors.append(f"CV-03——{cid} 的 runs 外键 {rid} 非 EXP-* 形态")
    for e in entries:  # run→卡 反查（宿主在册面，live）
        for run in e.get("runs") or []:
            rid = _norm((run or {}).get("experiment_id"))
            if not rid or not live:
                continue
            host = _load_registry_runs(root)
            if host and rid not in host:
                errors.append(f"CV-10——{e.get('card_id')} 指向的 run {rid} 不在宿主册（悬空外键，须登记 pending_fk）")

    # --- CV-17/18 指纹与判重（live 腿）---
    if live:
        digests: dict[str, list[str]] = defaultdict(list)
        for e in entries:
            cid = str(e.get("card_id"))
            for l in e.get("lives_in") or []:
                rel = _norm((l or {}).get("path"))
                if not rel:
                    continue
                p = root / rel
                if not _is_checkable_disk_path(rel):
                    continue
                if not p.exists():
                    errors.append(f"CV-17——{cid} 的真源卡件不在盘: {rel}（判据灭失必须显性红，禁静默 warn=F-10 型）")
                    continue
                dig = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                digests[dig].append(rel)
                bf = e.get("body_fingerprint") or {}
                want = _norm(bf.get("path")) or rel
                if (
                    want == rel
                    and bf.get("content_sha256")
                    and str(bf["content_sha256"])[:16] != hashlib.sha256(p.read_bytes()).hexdigest()[:16]
                    and str(e.get("card_state")) in (term | set())
                ):
                    has_amend = any(
                        str(c.get("to")) == "frozen_amended" or str(c.get("to")) == "void"
                        for c in e.get("credential") or []
                        if isinstance(c, dict)
                    )
                    if not has_amend:
                        errors.append(
                            f"CV-17——{cid} 正文指纹与盘上字节不符且无 frozen_amended/void "
                            "凭证（X02 静默改 frozen 参数）"
                        )
        for dig, files in digests.items():
            if len(set(files)) > 1:
                errors.append(f"CV-18——同字节内容跨条目重复（双真源，sha={dig}）: {sorted(files)}")
    return errors, warns


def _state_of(entries: list[dict], cid: str) -> str | None:
    e = _entry(entries, cid)
    return str(e.get("card_state")) if e else None


def _entry(entries: list[dict], cid: str) -> dict | None:
    for e in entries:
        if isinstance(e, dict) and str(e.get("card_id")) == cid:
            return e
    return None


def _n_eff(e: dict) -> int | None:
    v = e.get("n_eff")
    if isinstance(v, int):
        return v
    m = re.match(r"^\s*(\d+)", str(v or ""))
    return int(m.group(1)) if m else None


def _load_registry_runs(root: Path) -> set[str]:
    return _scan_id_set(root, _REGISTRY_HOST_REL, r"experiment_id:\s*'(EXP-[^']+)'")


def check_prose_counts(data: dict) -> list[str]:
    """CV-14 的散文腿：**人工撰写的语义层**（laws/boundary/ssot_note_zh）不得把图自身的计数
    写进散文（计数只准进 counts 字段——宪章"计数用字段勿写死在散文"）。

    派生镜像字段（note_zh/today_zh/credential_zh 等逐字取骨架列，含实测数）不入判，
    否则等于要求骨架不写实测数，与本图"骨架=契约"的前提冲突。
    """
    errors: list[str] = []
    fields = list(data.get("laws") or []) + list(data.get("boundary") or []) + [str(data.get("ssot_note_zh") or "")]
    for i, txt in enumerate(fields, 1):
        s = re.sub(r"\s+", " ", str(txt))
        if re.search(r"\d+\s*(态|条边|条迁移|张卡|个状态|禁止边)", s) and "counts" not in s:
            errors.append(f"CV-14——语义层第 {i} 条把图自身计数写进散文（改走 counts 字段）: {s[:60]}")
    return errors


def main() -> int:
    """CLI 契约（照图14/图9 母版）：0=PASS, 1=违规, 2=文件/解析失败。"""
    ap = argparse.ArgumentParser(description="图15 卡生命周期状态机校验（只读）")
    ap.add_argument("--map", default=str(DEFAULT_MAP), help="图 YAML 路径")
    ap.add_argument("--registry", default=None, help="宿主册路径覆盖（对抗测试可指 fixture；缺省按装载点自动选）")
    ap.add_argument(
        "--repo-root",
        "--root",
        dest="repo_root",
        default=str(_REPO_ROOT),
        help="路径锚解析根（默认仓库根；禁 CWD 漂移）",
    )
    ap.add_argument("--structure-only", action="store_true", help="只跑结构面（不读实例台账，不读文件系统实例证据）")
    ap.add_argument("--skip-live", action="store_true", help="跳过磁盘实存/在册探活类腿（gate 同口径），结构面零放宽")
    ap.add_argument(
        "--json", action="store_true", dest="as_json", help="机器可读输出（供 align_all 内联复用，禁 subprocess 自调）"
    )
    args = ap.parse_args()

    path = Path(args.map)
    if not path.exists():
        print(f"FAIL: 图文件不存在: {path}", file=sys.stderr)
        return 2
    raw = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        print(f"FAIL: YAML 解析失败: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("FAIL: YAML 顶层非对象", file=sys.stderr)
        return 2

    root = Path(args.repo_root)
    warnings: list[str] = []
    src, block = load_anchor_block(root, warnings)
    entries = list(block.get("card_entries") or [])
    if args.registry:
        rp = Path(args.registry)
        if not rp.exists():
            print(f"FAIL: 实例台账不存在: {rp}", file=sys.stderr)
            return 2
        try:
            rdata = yaml.safe_load(rp.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            print(f"FAIL: 台账 YAML 解析失败: {exc}", file=sys.stderr)
            return 2
        if isinstance(rdata, list):
            entries = [e for e in rdata if isinstance(e, dict)]
        elif isinstance(rdata, dict):
            entries = [e for e in (rdata.get("experiments") or rdata.get("card_entries") or []) if isinstance(e, dict)]

    errors = validate_structure(data, root=root, warnings=warnings, live=not args.skip_live, block=block)
    errors += check_prose_counts(data)
    inst_errors: list[str] = []
    if not args.structure_only:
        inst_errors, extra_warns = check_instances(
            entries, data, root=root, warnings=warnings, live=not args.skip_live, block=(src, block)
        )
        errors += inst_errors
        warnings += extra_warns

    counts = data.get("counts") or {}
    out = {
        "map": str(path),
        "anchor_source": data.get("anchor_source"),
        "loaded_from": src,
        "registry_host": data.get("registry_host"),
        "states": counts.get("total_states"),
        "transitions": counts.get("total_transitions"),
        "forbidden_edges": counts.get("total_forbidden_edges"),
        "gaps": counts.get("total_gaps"),
        "production": counts.get("production"),
        "cards_total": counts.get("cards_total"),
        "instances": len(entries),
        "instance_errors": len(inst_errors),
        "errors": errors,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        if not args.as_json:
            print(f"FAILED: {len(errors)} 个违规（结构+实例）", file=sys.stderr)
        return 1
    if not args.as_json:
        print(
            f"PASS: 卡生命周期校验通过（states={out['states']} transitions={out['transitions']} "
            f"forbidden={out['forbidden_edges']} gaps={out['gaps']} "
            f"production={out['production']} cards={out['cards_total']} "
            f"anchor_source={out['loaded_from']}）"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
