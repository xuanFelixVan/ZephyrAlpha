# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §construction_workflow_map
# [MODULE] scripts.governance.d5_architecture.validators.validate_construction_steps
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] task_bound
#   task_bound（CLI 工具按需触发；permanent+manual 撞 PERM-TRIGGER 铁律）
# create-guard-not-dup: 死车道抢救的FiveMaps生成器/校验器（字节代投非新能力），docstring描述读文本建图的既有动作，与canonical无重叠
# [DEPENDENCIES] yaml；docs/01_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml
#   （verifiability 值集唯一真源，动态加载——禁在本文件写死枚举字典）；
#   docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml 与
#   gate_registry.yaml（gate_id 在册集合 + INV-1 语料，册不可读=对应子检查降级不误伤）；
#   docs/03_modules/path_ownership_map.yaml（depgraph 派生投影，module_id 在册面）；
#   docs/_working/map_build/fig14_construction/00_skeleton.md（§1 状态列+可机验列，双轴同源）；
#   docs/_working/map_build/fig11_delivery/00_skeleton.md（D11-* 环节集合，CV-14 跨图引用）；
#   docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
#   （被图化的现行真源：Step 段闭合 / §2.3 矩阵 / INV-1 反复制语料）；
#   zephyr.governance.depgraph_schema（module_id DB 在册性，不可达=降 warn）
# [CONSUMERS] 图14（config/construction_workflow_map.yaml）质量门禁；
#   tests/governance/d5_architecture/test_construction_workflow_map_adversarial.py；
#   zephyr.gov_enforcement.commit_gates.construction_workflow_map_gate
#   （CONSTRUCTION-WORKFLOW-MAP gate，结构校验单一真源复用，禁复制判据）；
#   scripts.governance.d5_architecture.generators.align_all（总包挂轴，--json 内联复用）
# [STARTUP] imported（被 tests/门禁导入触发；CLI 面走 manual 语义已由 permanent+imported 格合规化）
# [MATURITY] testing
# [INVARIANTS] 台账只读（本工具禁写任何文件）；结构违规=exit 1，文件/解析失败=exit 2；
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读不到实载集合必抛，禁降级为'无冲突'
# [TESTS] 见同批 tests/ 下 canary 件
#   判据集合=CV-01 顶层必填键 / CV-02 节点必填字段 / CV-03 step_id 唯一与前缀形态 /
#   CV-04 政策↔图双向闭合（含 pending_anchors 显式白名单，禁静默）/ CV-05 exec_source
#   磁盘实存且"可执行"（.py ∧ argparse|add_parser|def main）/ CV-06 gate_id 双册在册 +
#   近似名点名 / CV-07 文档锚路径实存 + 符号命中 + 禁行号锚 / CV-08 deprecated|归档件
#   不得支撑 automated / CV-09 枚举合法（verifiability 动态取词表、build_status|confidence|
#   verified_scope|node_type|role|anchor_kind|wiring_status|red_reason|segment 值集校验）/
#   CV-10 边与回边（自环须带 max_rounds_ref、反向边必须显式声明、主序无环检测、重复边、
#   引用不存在节点）/ CV-11 §2.3 矩阵与 Step 段闭合 / CV-12 INV-1 反复制（>120 字 ∧
#   40 字滑窗命中政策正文）/ CV-13 计数只进 counts（散文写死数字判红）/ CV-14 handoff
#   边界（executable/gates 恒空 + handoff_to 命中图11 骨架 + internal 禁 handoff_to）/
#   CV-15 laws|boundary 非空 + boundary 逐字回源 / CV-16 状态自洽（automated⇒有 exec_source、
#   exec_source 声称而件不存在=红、built⇒evidence 带 YYYY-MM-DD）/ CV-BUS module_id 总线 /
#   CV-DUAL production⇔骨架 ✅（多了算谎少了算欠，计数与逐节点双向）/ CV-STATE 锚块声称值
#   与骨架实扫列一致 / CV-GHOST gap 节点的 ghost 断言可复核（幽灵复活即红）/
#   CV-L0 废止别名残留即红 / CV-GAP gap 节点结构 / CV-DOMAIN 越域挂载；
#   外部真源面（骨架/图11 骨架/册/PG/政策）不可达=对应子检查降 warn 入 warnings，
#   绝不升级为 error（禁环境异常打死无辜提交）；路径一律以 root 解析，禁 CWD 漂移
# [MODIFY-GUARD] 判据口径来自 docs/_working/map_build/fig14_construction/00_skeleton.md
#   （本图唯一收敛基准）+ 90_step_anchor_validator_spec.md（施工规格）+
#   docs/_working/map_build/03_final_blueprint_and_schema.md（三层字段/双轴裁定）；
#   放宽任何检查项或改阈值=改判据，须总包裁定，禁顺手放水
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)=结构违规; SystemExit(2)=文件不存在/解析失败/顶层非对象;
#   骨架/册/PG/政策不可达=对应子检查降 warn（warnings 出参），不升级为 error
# [TESTS] tests/governance/d5_architecture/test_construction_workflow_map_adversarial.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图14 步骤锚校验器（construction_workflow_map，AI 施工升级流）——结构契约单一真源。

形态照抄 validate_dev_delivery_map.py（图 11 定稿母版）/validate_strategy_production_map.py
（图 9 母版）：`validate_structure(data, root, warnings)` 纯结构判定供 gate 与 align_all
三方同源复用；`check_anchors(policy_text, data, root, warnings)` 做政策面闭合与锚实存。
只读，禁写任何文件。

与图 11 母版的差异（本图契约要求，不放宽任何一项）：
- 分组轴取 L0 四选一里的 `segment`（七段，值集由图 YAML `layers:` 声明，动态校验）；
- 环节契约全集=17 个 Step 段（骨架 §1，policy `^### Step` 实测 17）+10 个 gap 显性化节点；
- 双列口径不合并：`build_status`（骨架状态列 ✅/🔨/⬜ 派生）与 `verifiability`
  （骨架可机验列 yes/partial/no 派生，值集动态取 verifiability 受控词表），
  另存 `skeleton_verifiability` 原始列值供 CV-STATE 反查；
- 锚块两来源：政策内嵌机读块（未来态）与 91 号提案件（现态回落），由 `anchor_source`
  声明，校验器按来源判 `pending_anchors` 是否必须显式列全（防"忘了就绿"）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MAP = Path("config/construction_workflow_map.yaml")
DEFAULT_POLICY = Path("docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md")
_REPO_ROOT = Path(__file__).resolve().parents[4]
_SKELETON_REL = "docs/_working/map_build/fig14_construction/00_skeleton.md"
_FIG11_SKELETON_REL = "docs/_working/map_build/fig11_delivery/00_skeleton.md"
_VERIFIABILITY_VOCAB_REL = "docs/01_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml"
_PATH_OWNERSHIP_REL = "docs/03_modules/path_ownership_map.yaml"
# depgraph PG 在册性探测（F821 治理补缺：st-final-build 原稿常量段佚失，按 nodes.blueprint_id 列重建，占位符 {ph} 由调用方 .format 填充）
_SQL_BLUEPRINT_ID_LIST = "SELECT blueprint_id FROM nodes WHERE blueprint_id IN ({ph})"
_GATE_REGISTRIES = (
    # 落地整改：原稿 Path("docs" / "..." / ...) 把 / 运算写进字符串参数（str/str TypeError，import 即崩）
    str(_REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"),
    str(_REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"),
)

# 环节契约：17 个 Step 段（骨架 §1，D14-01~D14-17）+ 11 个 gap 节点（骨架 §1 红条目点名册
# 的"文档说有实则没有"族；D14-G10 已于 2026-10-02 依其 invalidation 条款作废——幽灵件
# src/zephyr/shared/vocab 2026-09-26 复活落仓 a2e820034bd，回写注记=00_skeleton.md R-08）。
# 增删须先回写骨架，禁在此自扩。
STEP_UNIVERSE: tuple[str, ...] = tuple(f"D14-{i:02d}" for i in range(1, 18))
GAP_NODES: tuple[str, ...] = tuple(gid for gid in (f"D14-G{i:02d}" for i in range(1, 13)) if gid != "D14-G10")
NODE_UNIVERSE: tuple[str, ...] = STEP_UNIVERSE + GAP_NODES

REQUIRED_TOP = [
    "schema_version",
    "map_id",
    "name_zh",
    "effective_from",
    "markets",
    "generator",
    "anchor_source",
    "laws",
    "boundary",
    "layers",
    "nodes",
    "edges",
    "feedback_loops",
    "pending_anchors",
    "loops",
    "counts",
]
# L0 通用层统一名（六图终局卷 §1 裁定一：同语义必同名）
REQUIRED_NODE = [
    "node_id",
    "name_zh",
    "segment",
    "node_type",
    "decision_question",
    "note_zh",
    "build_status",
    "confidence",
    "source_anchors",
    "doc_refs",
    "role",
    "order",
    "conditional",
    "wiring_status",
    "rollback_to",
    "evidence",
]
# stage 节点额外必填（gap 节点没有可执行锚面，这两项允许为 null，由 CV-GAP 腿单独判）
REQUIRED_FOR_STAGE = ["verifiability", "anchor_kind"]
# 必须**存在**（值可为 null）的键：双轴与总线挂载面 + 本图锚面
REQUIRED_KEY_PRESENT = [
    "verified_scope",
    "module_id",
    "module_ref",
    "exec_source",
    "skeleton_status",
    "skeleton_verifiability",
    "red_reason",
    "handoff_to",
    "max_rounds_ref",
]
# 废止别名（同义异名归一后不得残留）——出现即红
BANNED_NODE_FIELDS = {
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
NODE_TYPES = {"stage", "gap"}
BUILD_STATUS = {"built", "partial", "pending"}
CONFIDENCE = {"verified", "proposed", "untested"}
VERIFIED_SCOPE = {"production", "structure"}
WIRING_STATUS = {"wired", "unwired_slot_hollow", "unwired_no_caller", "partial"}
RED_REASONS = {"terminal", "unwired", "broken_supply", "ghost_ref"}
ROLES = {"internal", "handoff"}
ANCHOR_KINDS = {"gate_id", "script", "cli", "doc", "handoff", "none"}
SKELETON_STATUS_TO_BUILD = {"✅": "built", "🔨": "partial", "⬜": "pending"}
SKELETON_MV_TO_VERIFIABILITY = {"yes": "automated", "partial": "inspection", "no": "manual"}
LOOP_KINDS = {"in_graph", "in_graph_self_loop", "pending", "out_of_graph", "terminal_branch", "recovery_branch"}
STEP_ID_RE = re.compile(r"^D14-\d{2}$")
GAP_ID_RE = re.compile(r"^D14-G\d{2}$")
FIG11_REF_RE = re.compile(r"^D11-[SCD]\d{2}$")
# 本地符号改名 MODULE_ID_RE_LOCAL：canonical src/zephyr/governance/rule_patterns.py 的
# MODULE_ID_RE 是 YAML 行提取语义（r"^module_id:\s*(.+)$" MULTILINE），与本件的 MOD- 前缀
# 格式校验语义不同——不等价不可替换，按 SSoT/重名纪律重命名本地符号消冲突。
MODULE_ID_RE_LOCAL = re.compile(r"^MOD-[A-Z0-9][A-Z0-9_-]*$")
LINE_ANCHOR_RE = re.compile(r"\bL\d{2,}\b")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
# exec_evidence 的"可复跑把手"形态：命令（复跑/python/grep/git/ls/wc）或仓库内文件锚
_REPRO_RE = re.compile(r"(复跑|python |grep |git |ls |wc |scripts/|src/|config/|docs/)")
DECISION_Q_MAX = 120
NOTE_MAX = 120
_INV1_WINDOW = 40
_INV1_FIELD_MIN = 40
# 运行时/外置面不做磁盘实存检查（worktree/CI 无 .runtime 必假红）
_DISK_EXEMPT_PREFIXES = (".runtime/", ".ailocks/", ".aidrafts", "F:", "G:", "f:", "g:")
_TRACKED_PREFIXES = ("docs/", "config/", "scripts/", "src/", "tests/", "data/", "architecture_model/")


def _err(errors: list[str], msg: str) -> None:
    """_err implementation."""
    errors.append(msg)


def load_verifiability_values(root: Path, warnings: list[str] | None) -> set[str]:
    """verifiability 合法值集（动态取受控词表，禁硬编码字典——AGENTS 生成器 i18n 红线）。

    词表不可读/无 values ⇒ 返回空集并由调用方降级为 warn（不判红，但也不放绿：
    此时 CV-09 的 verifiability 腿整体跳过，counts 仍被节点实扫钉住）。
    """
    p = root / _VERIFIABILITY_VOCAB_REL
    if not p.exists():
        if warnings is not None:
            warnings.append(
                f"verifiability 受控词表不可读（{_VERIFIABILITY_VOCAB_REL}）：CV-09 的 verifiability 值集腿降 warn 跳过"
            )
        return set()
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — 词表解析失败=该腿降级
        if warnings is not None:
            warnings.append("verifiability 受控词表解析失败：CV-09 的 verifiability 腿降 warn 跳过")
        return set()
    values = {str(v.get("value")) for v in data.get("values") or [] if isinstance(v, dict)}
    return {v for v in values if v}


def scan_skeleton_axes(root: Path) -> dict[str, dict[str, str]]:
    """骨架 §1 环节表两列实扫：状态列（✅/🔨/⬜）+ 可机验列（yes/partial/no）+ 段/角色列。

    与生成器同口径（同一张表、同一列序），故两侧不会各自漂移；表形变更/文件不可读
    ⇒ 返回空表，调用方把相关子检查降级为 warn。
    """
    p = root / _SKELETON_REL
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    marker = "## §1 环节全集"
    if marker not in text:
        return {}
    body = text.split(marker, 1)[1].split("\n## §2", 1)[0]
    out: dict[str, dict[str, str]] = {}
    for line in body.split("\n"):
        if not re.match(r"^\|\s*D14-\d{2}\s*\|", line):
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) < 8:
            continue
        # 列序（骨架 §1 表）：0=空 1=环节编号 2=环节名 3=段 4=本图角色 5=状态 6=真源映射 7=可机验否
        nid, name, segment, role, status, verifiable = (cols[1], cols[2], cols[3], cols[4], cols[5], cols[7])
        out[nid] = {
            "name": name,
            "segment": segment,
            "role": role,
            "status": status,
            "verifiable": verifiable.split("（")[0].strip(),
        }
    return out


def scan_fig11_node_ids(root: Path) -> set[str]:
    """图11 骨架 §1 的 D11-* 环节集合（CV-14 跨图引用合法性；不可读=空集，调用方降 warn）。"""
    p = root / _FIG11_SKELETON_REL
    if not p.exists():
        return set()
    text = p.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"D11-[SCD]\d{2}", text))


def scan_gate_ids(root: Path) -> set[str]:
    """两本门禁册的 gate_id 并集（CV-06 在册判定；册不可读=空集，调用方降 warn）。

    一律读**条目集合**，不读 total_gates 字段（骨架 R-17 实测该字段本身已漂移）。
    """
    ids: set[str] = set()
    for rel in _GATE_REGISTRIES:
        p = root / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        ids |= set(re.findall(r"^\s*-?\s*gate_id:\s*([A-Za-z0-9_.\-]+)", text, re.M))
    return ids


def scan_module_id_index(root: Path) -> dict[str, str]:
    """depgraph 派生投影（path_ownership_map.yaml 的 claim_type=depgraph_node）→ MOD-* 面。"""
    p = root / _PATH_OWNERSHIP_REL
    if not p.exists():
        return {}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — 册不可解析=本面降级空表（CV-BUS 报未挂全）
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
    """depgraph 在册性核对（PG 只读）。None=不可达/无法判定（调用方降 warn）；
    列表=确实查不到的号（真幽灵总线号，判 error）。绝不因环境异常返回误判用的列表。"""
    want = sorted({m for m in module_ids if m})
    if not want:
        return []
    try:
        if str(root / "src") not in sys.path:
            sys.path.insert(0, str(root / "src"))
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: PLC0415
    except Exception:  # noqa: BLE001 — 依赖不可达≠图有错
        return None
    conn = None
    try:
        conn = get_depgraph_pg_connection(read_only=True)
        conn.autocommit = True
        placeholders = ", ".join(["%s"] * len(want))
        with conn.cursor() as cur:
            cur.execute(
                _SQL_BLUEPRINT_ID_LIST.format(ph=placeholders),  # noqa: S608  只读探测，参数全走占位符
                want,
            )
            found = {str(r[0]) for r in cur.fetchall() if r and r[0]}
        return [m for m in want if m not in found]
    except Exception:  # noqa: BLE001 — PG 离线/超时/权限不足=降 warn（图8/图9 fail-open 先例）
        return None
    finally:
        try:
            if conn is not None:
                conn.close()
        except Exception:  # noqa: BLE001
            pass


def _anchor_path(ref: str) -> str:
    """ "path:line" / "path#symbol" / "path §节 说明" 型锚取路径段；纯路径原样返回。

    doc_refs/source_anchors 允许"路径 + 空格 + 锚说明"形态（图11 母版同款），故先按空白
    切第一段；Windows 盘符冒号不误切（仅当末段冒号后全为数字才视为 :line 后缀）。
    """
    s = str(ref).strip()
    if not s:
        return ""
    s = s.split("#", 1)[0]
    s = s.split()[0] if s.split() else ""
    head, sep, tail = s.rpartition(":")
    if sep and tail.isdigit():
        return head
    return s


def _is_checkable_disk_path(p: str) -> bool:
    """仓库相对、非运行时豁免、看起来像路径才做实存检查。"""
    if not p or p.startswith(_DISK_EXEMPT_PREFIXES):
        return False
    return "/" in p or "\\" in p


def parse_exec_source(src: Any) -> dict[str, str] | None:
    """exec_source 形态解析：gate:X | script:<path> | cli:<path>#<option> | null。"""
    if src in (None, "", "null"):
        return None
    s = str(src).strip()
    kind, sep, rest = s.partition(":")
    if not sep or not rest:
        return {"kind": "<非法形态>", "ref": s}
    return {"kind": kind, "ref": rest}


def _is_executable_script(path: Path) -> tuple[bool, str]:
    """CV-05 的"可执行"机械定义：.py ∧ 含 argparse/add_parser/def main 之一。"""
    if not path.name.endswith(".py"):
        return False, "非 .py 件"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 — 读不出来按不可证处理
        return False, "不可读"
    if re.search(r"argparse|add_parser|def main", text):
        return True, ""
    return False, "无 argparse/add_parser/def main 入口面"


def _option_present(script_text: str, option: str) -> bool:
    """选项/子命令在册判定（裸名同时试 `--<name>` 选项形态——政策与锚块两态写法并存）。"""
    if not option:
        return False
    if option.startswith("--"):
        return bool(re.search(rf'["\']{re.escape(option)}["\']', script_text))
    e = re.escape(option)
    strict = (rf'add_parser\(\s*["\']{e}["\']', rf'==\s*["\']{e}["\']', rf'choices\s*=\s*\[[^\]]*["\']{e}["\']')
    return any(re.search(p, script_text) for p in strict) or bool(re.search(rf'["\']--{e}["\']', script_text))


def _policy_step_heads(policy_text: str) -> list[str]:
    """政策 `^### Step` 段的 Step 名集合（CV-04 闭合的真源侧）。"""
    return re.findall(r"^### Step\s+(\S+)\s*·", policy_text, re.M)


def _policy_matrix_rows(policy_text: str) -> list[str]:
    """政策 §2.3 关系矩阵首列 Step 名（CV-11 的靶；节名不匹配=返回空表，调用方降 warn）。"""
    marker = "### 2.3"
    if marker not in policy_text:
        return []
    body = policy_text.split(marker, 1)[1]
    body = re.split(r"\n###? ", body, maxsplit=1)[0]
    rows: list[str] = []
    for line in body.split("\n"):
        m = re.match(r"^\|\s*Step\s*([0-9]+(?:\.[0-9])?)\s", line)
        if m:
            rows.append(m.group(1))
    return rows


def _policy_bodies(policy_text: str) -> list[str]:
    """INV-1 反复制语料=政策正文行（≥阈值的散文行；表格/代码/标题行不入选）。"""
    out: list[str] = []
    in_code = False
    for line in policy_text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        s = line.strip()
        if len(s) < _INV1_FIELD_MIN or s.startswith(("#", "|", ">", "-", "*", "* ")):
            continue
        out.append(s)
    return out


def _copy_hit(text: str, bodies: list[str], window: int = _INV1_WINDOW) -> str | None:
    """40 字滑窗命中政策正文即返回命中文（CV-12 判据，图只准存标识符与指针）。"""
    t = re.sub(r"\s+", "", str(text))
    if len(t) < window:
        return None
    norm = {re.sub(r"\s+", "", b) for b in bodies if len(re.sub(r"\s+", "", b)) >= window}
    for i in range(0, len(t) - window + 1):
        seg = t[i : i + window]
        for b in norm:
            if seg in b:
                return seg
    return None


def validate_structure(
    data: dict, root: Path | None = None, warnings: list[str] | None = None, live: bool = True
) -> list[str]:
    """结构契约唯一真源（gate 与 align_all 与 CLI 三方同源动态 import，禁复制判据）。

    warnings 传入时收集降级项（词表/骨架/图11 骨架/门禁册/投影册/PG 不可达）；
    外部面异常一律不入 errors（禁环境异常打死无辜提交）。
    live=False（CLI --skip-live / gate 侧）只跳**磁盘实存与在册类**腿（CV-05/06/07/08
    与 PG/投影核对），结构面（枚举/闭合/双轴/计数/边/INV-1 长度）一项不放宽。
    """
    errors: list[str] = []
    root = root or _REPO_ROOT
    for k in REQUIRED_TOP:
        if k not in data:
            _err(errors, f"缺顶层必填键: {k}")
    if errors:
        return errors

    if not data.get("laws"):
        _err(errors, "laws（全图铁律）不得为空")
    if not data.get("boundary"):
        _err(errors, "boundary（明确不做边界）不得为空")
    anchor_source = str(data.get("anchor_source"))
    if anchor_source not in ("policy", "proposal"):
        _err(errors, f"anchor_source 非法 {anchor_source!r}（须 policy=政策已嵌块 / proposal=回落提案件）")

    layers = [l.get("layer_id") for l in data.get("layers", []) if isinstance(l, dict)]
    layer_ids = {x for x in layers if x}
    if not layer_ids:
        _err(errors, "layers 为空（段分层值集必须在图头声明，禁在校验器写死）")

    verif_values = load_verifiability_values(root, warnings)
    skeleton = scan_skeleton_axes(root)
    if not skeleton and warnings is not None:
        warnings.append(f"骨架 §1 两列不可读（{_SKELETON_REL}）：CV-DUAL/CV-STATE 的对照子检查降 warn")
    fig11_ids = scan_fig11_node_ids(root)
    if not fig11_ids and warnings is not None:
        warnings.append(f"图11 骨架不可读（{_FIG11_SKELETON_REL}）：CV-14 跨图引用腿降 warn 跳过")
    gate_ids = scan_gate_ids(root) if live else set()
    if live and not gate_ids and warnings is not None:
        warnings.append("门禁两册不可读：CV-06 gate 在册腿降 warn 跳过（禁把热册可用性耦合进地图校验）")
    module_index = scan_module_id_index(root) if live else {}
    if live and not module_index and warnings is not None:
        warnings.append(f"depgraph 投影册不可读（{_PATH_OWNERSHIP_REL}）：CV-BUS 在册一致性腿降 warn")

    nodes = data.get("nodes", [])
    ids: list[str] = []
    universe = set(NODE_UNIVERSE)
    gap_set = set(GAP_NODES)
    for n in nodes:
        if not isinstance(n, dict):
            _err(errors, f"{n!r}: 节点非对象")
            continue
        nid = n.get("node_id", "<无 node_id>")
        ids.append(nid)
        if nid not in universe:
            _err(errors, f"{nid}: 节点越出契约全集（17 Step 段 + 11 gap 显性化节点，骨架 §1 契约件，增删须先回写骨架）")
        # --- CV-L0：废止别名残留即红 ---
        for banned, canonical in BANNED_NODE_FIELDS.items():
            if banned in n:
                _err(errors, f"{nid}: 字段旧名残留 {banned}（L0 统一名应为 {canonical}）")
        for f in REQUIRED_NODE:
            if f not in n or n[f] in (None, ""):
                _err(errors, f"{nid}: 缺必填字段 {f}")
        if n.get("node_type") == "stage":
            for f in REQUIRED_FOR_STAGE:
                if not n.get(f):
                    _err(errors, f"{nid}: 缺环节节点必填字段 {f}（gap 节点才可空）")
        if not n.get("source_anchors"):
            _err(errors, f"{nid}: source_anchors 至少 1 条真源锚（L0 必填语义）")
        for f in REQUIRED_KEY_PRESENT:
            if f not in n:
                _err(errors, f"{nid}: 缺必填键 {f}（值可为 null，键必须在——双轴/总线/锚面不得静默缺失）")
        for xf in CROSS_DOMAIN_FIELDS:
            if xf in n:
                _err(errors, f"{nid}: 越域挂载——本图 L1/L2 禁字段 {xf}（决策判据真源=TDM）")

        node_type = n.get("node_type")
        if node_type not in NODE_TYPES:
            _err(errors, f"{nid}: node_type 非法 {node_type!r}")
        # --- CV-03 形态：Step 节点用 D14-\d{2}，gap 节点用 D14-G\d{2} ---
        if node_type == "stage" and not STEP_ID_RE.match(str(nid)):
            _err(errors, f"{nid}: stage 节点编号须为 D14-\\d{{2}} 形态")
        if node_type == "gap" and not GAP_ID_RE.match(str(nid)):
            _err(errors, f"{nid}: gap 节点编号须为 D14-G\\d{{2}} 形态")
        if n.get("segment") not in layer_ids:
            _err(errors, f"{nid}: segment 未挂到已声明层位 {n.get('segment')!r}")
        if n.get("build_status") not in BUILD_STATUS:
            _err(errors, f"{nid}: build_status 非法 {n.get('build_status')!r}")
        if n.get("confidence") not in CONFIDENCE:
            _err(errors, f"{nid}: confidence 非法 {n.get('confidence')!r}")
        scope = n.get("verified_scope")
        if scope is not None and scope not in VERIFIED_SCOPE:
            _err(errors, f"{nid}: verified_scope 非法 {scope!r}（须 production/structure/null）")
        if n.get("wiring_status") not in WIRING_STATUS:
            _err(
                errors, f"{nid}: wiring_status 非法 {n.get('wiring_status')!r}（须 {'/'.join(sorted(WIRING_STATUS))}）"
            )
        role = n.get("role")
        if role not in ROLES:
            _err(errors, f"{nid}: role 非法 {role!r}（须 internal/handoff）")
        if n.get("anchor_kind") not in ANCHOR_KINDS:
            _err(errors, f"{nid}: anchor_kind 非法 {n.get('anchor_kind')!r}（须 {'/'.join(sorted(ANCHOR_KINDS))}）")
        red = n.get("red_reason")
        if red is not None and red not in RED_REASONS:
            _err(errors, f"{nid}: red_reason 非法 {red!r}（枚举 terminal/unwired/broken_supply/ghost_ref）")
        verif = n.get("verifiability")
        if verif is not None and verif_values and verif not in verif_values:
            _err(
                errors,
                f"{nid}: verifiability 非法 {verif!r}"
                f"（合法值动态取 {_VERIFIABILITY_VOCAB_REL}：{'/'.join(sorted(verif_values))}）",
            )

        # --- CV-02/L0 语义面 ---
        if len(str(n.get("decision_question", ""))) > DECISION_Q_MAX:
            _err(errors, f"{nid}: decision_question 超 {DECISION_Q_MAX} 字")
        for sr in n.get("store_refs") or []:
            if not isinstance(sr, dict) or not sr.get("artifact") or not sr.get("location") or not sr.get("retention"):
                _err(errors, f"{nid}: store_refs 条目缺 artifact/location/retention 三要素")
        note = str(n.get("note_zh", ""))
        if len(note) > NOTE_MAX:
            _err(errors, f"{nid}: note_zh 超 {NOTE_MAX} 字（图只存标识符与指针，长文归作业簿）")
        if n.get("confidence") == "verified" and not n.get("evidence"):
            _err(errors, f"{nid}: confidence=verified 必带 evidence（proposed 冒充 verified 判红）")
        if n.get("build_status") == "built" and not n.get("module_ref"):
            _err(errors, f"{nid}: built 节点必须有 module_ref 代码锚")
        if n.get("build_status") == "built":
            ev = n.get("evidence") or []
            if not ev:
                _err(errors, f"{nid}: CV-16——built 却 evidence 空（✅ 必附实查的机读面）")
            for x in ev:
                if not DATE_PREFIX_RE.match(str(x)):
                    _err(errors, f"{nid}: CV-16——evidence 每条须以 YYYY-MM-DD 开头（实查留痕形态）: {str(x)[:40]}")

        # --- CV-16 + 任务硬要求①：automated 必须有 exec_source；声称而件不存在=红 ---
        es = parse_exec_source(n.get("exec_source"))
        if es is not None and es["kind"] not in ("gate", "script", "cli"):
            _err(errors, f"{nid}: exec_source 形态非法 {n.get('exec_source')!r}（须 gate:|script:|cli:|null）")
        if verif == "automated" and es is None:
            _err(
                errors,
                f"{nid}: CV-16——verifiability=automated 却无 exec_source"
                "（自动可验必须先有可跑/在册的锚，禁凭散文主张）",
            )
        if es is not None and es["kind"] == "gate" and live:
            gid = es["ref"]
            if gate_ids and gid not in gate_ids:
                _err(errors, f"{nid}: CV-05/06——exec_source 声称 gate {gid} 但两册均不在册（件不存在）")
        if es is not None and es["kind"] in ("script", "cli") and live:
            path = _anchor_path(es["ref"])
            ok = bool(path) and (root / path).exists()
            if not ok:
                _err(errors, f"{nid}: CV-05——exec_source 声称件不存在: {path}")
            else:
                good, why = _is_executable_script(root / path)
                if not good:
                    _err(errors, f"{nid}: CV-05——exec_source 的件不可执行（{why}）: {path}")
                if es["kind"] == "cli":
                    option = str(es["ref"]).split("#", 1)[1] if "#" in str(es["ref"]) else ""
                    if not option:
                        _err(errors, f"{nid}: CV-05——cli 型 exec_source 缺选项名: {es['ref']}")
                    else:
                        st = (root / path).read_text(encoding="utf-8", errors="replace")
                        if not _option_present(st, option):
                            _err(errors, f"{nid}: CV-05——声称的选项/子命令不存在: {path}#{option}")
        # executable/cli_anchors/gates 三个登记面同样判"声称有实则没有"（live 腿）
        for pth in (n.get("executable", []) or []) if live else []:
            rp = _anchor_path(str(pth))
            if not rp or not (root / rp).exists():
                _err(errors, f"{nid}: CV-05——executable 件不存在: {pth}")
                continue
            good, why = _is_executable_script(root / rp)
            if not good:
                _err(errors, f"{nid}: CV-05——executable 不可执行（{why}）: {rp}")
        for ca in (n.get("cli_anchors", []) or []) if live else []:
            if not isinstance(ca, dict) or not ca.get("script") or not ca.get("option"):
                _err(errors, f"{nid}: cli_anchors 条目缺 script/option: {ca!r}")
                continue
            rp = _anchor_path(str(ca["script"]))
            if not (root / rp).exists():
                _err(errors, f"{nid}: CV-05——cli_anchors 件不存在: {rp}")
                continue
            st = (root / rp).read_text(encoding="utf-8", errors="replace")
            if not _option_present(st, str(ca["option"])):
                _err(errors, f"{nid}: CV-05——cli_anchors 选项/子命令不存在: {rp}#{ca['option']}")
        for gid in n.get("gates", []) or []:
            if gate_ids and gid not in gate_ids:
                near = next((g for g in sorted(gate_ids) if _edit_distance_le2(str(gid), str(g))), None)
                if near:
                    if warnings is not None:
                        warnings.append(
                            f"{nid}: gate 名 {gid} 不在册，近似实名={near}（CV-06 告警面：图节点必须登记实名）"
                        )
                else:
                    _err(errors, f"{nid}: CV-06——gate 不在两册任何条目中: {gid}")

        # --- CV-07 文档锚：禁行号锚（内容腿，恒跑）+ 路径实存/符号命中（live 腿）---
        for d in n.get("docs", []) or []:
            if not isinstance(d, dict) or not d.get("path"):
                _err(errors, f"{nid}: docs 条目缺 path: {d!r}")
                continue
            dp = str(d["path"])
            if LINE_ANCHOR_RE.search(dp) or LINE_ANCHOR_RE.search(str(d.get("symbol", ""))):
                _err(errors, f"{nid}: CV-07——禁行号锚（骨架 R-13 实测 7/7 全偏）: {dp}")
            if not live:
                continue
            if not (root / dp).exists():
                _err(errors, f"{nid}: CV-07——文档/规则锚路径不存在: {dp}")
                continue
            sym = str(d.get("symbol") or "")
            if sym and sym not in (root / dp).read_text(encoding="utf-8", errors="replace"):
                _err(errors, f"{nid}: CV-07——符号锚未命中: {dp}#{sym}")
            if sym and verif == "automated" and _is_deprecated_or_archived(root / dp):
                _err(errors, f"{nid}: CV-08——automated 段的锚落在已废弃/归档件: {dp}")
        # policy_anchor 形态（禁行号恒判；路径实存属 live 腿）
        pa = str(n.get("policy_anchor") or "")
        if pa:
            if LINE_ANCHOR_RE.search(pa):
                _err(errors, f"{nid}: CV-07——policy_anchor 含行号锚: {pa}")
            pp = _anchor_path(pa)
            if pp and live and not (root / pp).exists():
                _err(errors, f"{nid}: CV-07——policy_anchor 路径不存在: {pp}")

        # --- CV-14 handoff 边界（防本图吞图11）---
        handoff_to = n.get("handoff_to") or []
        if role == "handoff":
            if n.get("executable"):
                _err(errors, f"{nid}: CV-14——handoff 节点禁登记 executable 机制锚（机制归图11）")
            if n.get("gates"):
                _err(errors, f"{nid}: CV-14——handoff 节点禁登记 gates 机制锚（机制归图11）")
            if not handoff_to:
                _err(errors, f"{nid}: CV-14——handoff 节点 handoff_to 不得为空")
            if fig11_ids:
                for h in handoff_to:
                    if not FIG11_REF_RE.match(str(h)):
                        _err(errors, f"{nid}: CV-14——handoff_to 形态非法: {h}")
                    elif h not in fig11_ids:
                        _err(errors, f"{nid}: CV-14——handoff_to 未在图11 骨架环节集命中: {h}")
        elif role == "internal" and handoff_to:
            _err(errors, f"{nid}: CV-14——internal 节点 handoff_to 必须为空")
        if not n.get("module_id") and red is None:
            _err(
                errors,
                f"{nid}: CV-BUS——module_id 为空必配 red_reason（纯结构/终点/handoff/gap 节点=合法 null 但要写因）",
            )

        # --- CV-BUS：module_id 总线挂载 ---
        mod_id, mod_ref = n.get("module_id"), n.get("module_ref")
        if mod_ref and not mod_id:
            _err(errors, f"{nid}: CV-BUS——module_ref 非空而 module_id 空（有实现代码必挂 MOD-* 总线号）")
        if mod_id is not None and not MODULE_ID_RE_LOCAL.match(str(mod_id)):
            _err(errors, f"{nid}: CV-BUS——module_id 非 MOD-* 形态：{mod_id!r}（禁自造号）")
        if mod_ref and not mod_id and role != "handoff":
            _err(errors, f"{nid}: CV-BUS——module_ref={mod_ref} 在 depgraph 投影查无 MOD-*（禁空挂/自造）")
        if mod_id and mod_ref and module_index:
            expect = module_index.get(str(mod_ref).split(":")[0].split("#")[0])
            if expect is not None and expect != mod_id:
                _err(
                    errors,
                    f"{nid}: CV-BUS——module_id={mod_id} 与投影在册答案 {expect} 不一致（总线号必经在册面取，禁凭记忆）",
                )
        if (
            mod_ref
            and live
            and _is_checkable_disk_path(_anchor_path(str(mod_ref)))
            and not (root / _anchor_path(str(mod_ref))).exists()
        ):
            _err(errors, f"{nid}: 路径锚磁盘实存检查失败（module_ref 不存在）: {_anchor_path(str(mod_ref))}")

        # --- 源锚/文档指针实存（live 腿；只查跟踪前缀，运行时面归生成器扫描时刻）---
        if live:
            anchors = [_anchor_path(str(x)) for x in (n.get("source_anchors") or [])]
            for x in n.get("doc_refs") or []:
                if _anchor_path(str(x)):
                    anchors.append(_anchor_path(str(x)))
            for dr in n.get("data_refs", []) or []:
                if str(dr).startswith(_TRACKED_PREFIXES):
                    anchors.append(_anchor_path(str(dr)))
            for a in anchors:
                if a and a.startswith(_TRACKED_PREFIXES) and not (root / a).exists():
                    _err(errors, f"{nid}: 路径锚磁盘实存检查失败（锚不存在）: {a}")

        # --- CV-DUAL：双轴与骨架两列同源（多了算谎、少了算欠）---
        if skeleton and nid in skeleton:
            sk = skeleton[nid]
            expect_build = SKELETON_STATUS_TO_BUILD.get(sk["status"])
            if n.get("build_status") != expect_build:
                _err(
                    errors,
                    f"{nid}: CV-STATE——build_status={n.get('build_status')!r} 与骨架状态列 "
                    f"{sk['status']}（应 {expect_build}）不一致",
                )
            if n.get("skeleton_status") != sk["status"]:
                _err(
                    errors,
                    f"{nid}: CV-STATE——skeleton_status={n.get('skeleton_status')!r} "
                    f"与骨架实扫 {sk['status']!r} 不一致（骨架=契约，改判据须回写骨架）",
                )
            if n.get("skeleton_verifiability") != sk["verifiable"]:
                _err(errors, f"{nid}: CV-STATE——skeleton_verifiability 与骨架可机验列 {sk['verifiable']!r} 不一致")
            expect_verif = SKELETON_MV_TO_VERIFIABILITY.get(sk["verifiable"])
            if role == "handoff" and expect_verif != "manual":
                expect_verif = "manual"  # 反洗白口径（簿03：handoff 不借图11 的 auto 抬分）
            if n.get("verifiability") != expect_verif:
                _err(
                    errors,
                    f"{nid}: CV-STATE——verifiability={n.get('verifiability')!r} 与骨架"
                    f"可机验列 {sk['verifiable']} 的映射 {expect_verif} 不一致",
                )
            if n.get("segment") != sk["segment"]:
                _err(errors, f"{nid}: CV-STATE——segment={n.get('segment')!r} 与骨架段列 {sk['segment']!r} 不一致")
            if n.get("role") != ("handoff" if sk["role"] == "交接" else "internal"):
                _err(errors, f"{nid}: CV-STATE——role 与骨架本图角色列（{sk['role']}）不一致")
        if scope == "production":
            if n.get("confidence") != "verified":
                _err(
                    errors,
                    f"{nid}: verified_scope=production 而 confidence={n.get('confidence')!r}（production 必 verified）",
                )
            if not n.get("exec_evidence"):
                _err(
                    errors,
                    f"{nid}: verified_scope=production 必带 exec_evidence"
                    "（复跑命令或 文件:行 锚，禁只凭接口存在宣在产）",
                )
            elif not any(_REPRO_RE.search(str(x)) for x in n.get("exec_evidence") or []):
                _err(errors, f"{nid}: exec_evidence 无可复跑把手（必含命令或 文件:行 锚）")
            if skeleton and nid in skeleton and skeleton[nid]["status"] != "✅":
                _err(
                    errors,
                    f"{nid}: 谎——verified_scope=production 而骨架状态列为 "
                    f"{skeleton[nid]['status']}（非 ✅ 不得宣在产）",
                )
        elif scope == "structure" and node_type == "stage":
            if skeleton and nid in skeleton and skeleton[nid]["status"] == "✅":
                _err(errors, f"{nid}: 欠——骨架 ✅ 环节未宣 production（verified_scope=structure）")

    if len(ids) != len(set(ids)):
        _err(errors, "node_id 存在重复")
    missing = sorted(universe - set(ids))
    if missing:
        _err(errors, f"缺环节（契约全集未建满）: {', '.join(missing)}")

    valid_ids = set(ids)
    # --- CV-GAP：gap 节点结构（缺口不得孤岛、不得洗成正常环节）---
    edge_pairs = {tuple(e) for e in data.get("edges", []) if isinstance(e, (list, tuple)) and len(e) == 2}
    for gid in gap_set & valid_ids:
        g = next((x for x in nodes if isinstance(x, dict) and x.get("node_id") == gid), {})
        if g.get("node_type") != "gap":
            _err(errors, f"{gid}: 契约编号为 gap 节点但 node_type={g.get('node_type')!r}")
        if not g.get("red_reason"):
            _err(errors, f"{gid}: gap 节点必带 red_reason（terminal/unwired/broken_supply/ghost_ref）")
        if g.get("module_ref"):
            _err(errors, f"{gid}: gap 节点不得挂 module_ref（缺口没有实现代码可证）")
        if not any(gid in p for p in edge_pairs):
            _err(errors, f"{gid}: gap 节点必须至少有一条边连到受影响环节（显性化不得孤岛）")

    # --- CV-DUAL 计数面：production 数 == 骨架 ✅ 数（不多不少）---
    prod_ids = {n.get("node_id") for n in nodes if isinstance(n, dict) and n.get("verified_scope") == "production"}
    if skeleton:
        ok_ids = {nid for nid, v in skeleton.items() if v["status"] == "✅"}
        over = sorted(prod_ids - ok_ids)
        under = sorted(i for i in ok_ids if i not in prod_ids and i in valid_ids)
        if over or under:
            _err(
                errors,
                f"CV-DUAL 计数：production 数 {len(prod_ids)} ≠ 骨架 ✅ 数 {len(ok_ids)}"
                f"（多了算谎={over}，少了算欠={under}）",
            )

    # --- CV-13 计数只进字段 ---
    counts = data.get("counts") or {}
    if isinstance(counts, dict):
        if counts.get("total_nodes") != len(nodes):
            _err(
                errors,
                f"counts.total_nodes={counts.get('total_nodes')} 与 nodes 实数 "
                f"{len(nodes)} 不符（图 YAML 须由生成器再生，禁手改后不回生成）",
            )
        if counts.get("total_edges") != len(data.get("edges", [])):
            _err(
                errors,
                f"counts.total_edges={counts.get('total_edges')} 与 edges 实数 {len(data.get('edges', []))} 不符",
            )
        steps_real = sum(1 for n in nodes if isinstance(n, dict) and n.get("node_type") == "stage")
        if counts.get("total_steps") != steps_real:
            _err(errors, f"counts.total_steps={counts.get('total_steps')} 与 stage 节点实数 {steps_real} 不符")
        scope_real: dict[str, int] = {}
        verif_real: dict[str, int] = {}
        type_real: dict[str, int] = {}
        role_real: dict[str, int] = {}
        for n in nodes:
            if not isinstance(n, dict):
                continue
            for key, field in (
                ("by_verified_scope", "verified_scope"),
                ("by_verifiability", "verifiability"),
                ("by_node_type", "node_type"),
                ("by_role", "role"),
            ):
                bucket = {
                    "by_verified_scope": scope_real,
                    "by_verifiability": verif_real,
                    "by_node_type": type_real,
                    "by_role": role_real,
                }[key]
                k = str(n.get(field))
                bucket[k] = bucket.get(k, 0) + 1
        for key, real in (
            ("by_verified_scope", scope_real),
            ("by_verifiability", verif_real),
            ("by_node_type", type_real),
            ("by_role", role_real),
        ):
            declared_counts = counts.get(key) or {}
            if {k: v for k, v in declared_counts.items() if v} != real:
                _err(errors, f"counts.{key}={declared_counts} 与节点实扫 {real} 不符")
        for f in ("total_steps", "total_edges"):
            text = str(counts.get(f, ""))
            if re.search(r"[一二三四五六七八九十]|\d+\s*步", text):
                _err(errors, f"CV-13——counts.{f} 写成散文（计数只准进数字字段，禁写死条数）: {text}")
        sk_counts_real: dict[str, int] = {}
        for v in skeleton.values():
            sk_counts_real[v["status"]] = sk_counts_real.get(v["status"], 0) + 1
        if skeleton:
            declared_sk = {k: v for k, v in (counts.get("by_skeleton_status") or {}).items() if v}
            if declared_sk != sk_counts_real:
                _err(
                    errors,
                    f"counts.by_skeleton_status={declared_sk} 与骨架 §1 状态列实扫 "
                    f"{sk_counts_real} 不符（骨架=契约，两列口径不得各说各话）",
                )

    # --- CV-10 边/回边 ---
    feedback: set[tuple[str, str]] = set()
    for fl in data.get("feedback_loops", []):
        if not isinstance(fl, dict) or not fl.get("from") or not fl.get("to"):
            _err(errors, f"feedback_loops 条目缺 from/to: {fl!r}")
            continue
        feedback.add((fl["from"], fl["to"]))
        if not fl.get("note"):
            _err(errors, f"反馈环 {fl['from']}->{fl['to']} 缺 note（环路语义须显式声明）")
    for fb in sorted(feedback):
        for side in fb:
            if side not in valid_ids:
                _err(errors, f"反馈环引用了不存在的节点: {side}")

    order = {n.get("node_id"): n.get("order") for n in nodes if isinstance(n, dict)}
    max_rounds = {n.get("node_id"): n.get("max_rounds_ref") for n in nodes if isinstance(n, dict)}
    seen_edges: set[tuple[str, str]] = set()
    forward: dict[str, list[str]] = {}
    for e in data.get("edges", []):
        if not isinstance(e, (list, tuple)) or len(e) != 2:
            _err(errors, f"边格式非法（须 [from,to]）: {e}")
            continue
        a, b = e[0], e[1]
        if a not in valid_ids or b not in valid_ids:
            _err(errors, f"边引用了不存在的节点: {a}->{b}")
            continue
        if (a, b) in seen_edges:
            _err(errors, f"重复边: {a}->{b}")
        seen_edges.add((a, b))
        if a == b:
            _err(errors, f"自环边不得进 edges（回边一律走 feedback_loops）: {a}")
            continue
        if (a, b) in feedback:
            continue
        oa, ob = order.get(a), order.get(b)
        if isinstance(oa, int) and isinstance(ob, int) and oa > ob:
            _err(errors, f"未声明为反馈环的反向边: {a}->{b}（回边必须在 feedback_loops 显式声明）")
        forward.setdefault(a, []).append(b)
    for nid in valid_ids:
        if order.get(nid) is None:
            _err(errors, f"{nid}: order 缺失或非整数")
    dup_orders = _dup_values([v for v in order.values() if isinstance(v, int)])
    if dup_orders:
        _err(errors, f"order 全图唯一性破坏（重复序号 {dup_orders}）")
    for fb in sorted(feedback):
        a, b = fb
        if a not in order or b not in order:
            continue
        if a == b:
            if not max_rounds.get(a):
                _err(errors, f"CV-10——自环 {a} 未带 max_rounds_ref（轮次常量引用），不得成为无界循环")
            continue
        oa, ob = order.get(a), order.get(b)
        if isinstance(oa, int) and isinstance(ob, int) and oa < ob:
            _err(errors, f"CV-10——回边必须指向更小 order（禁顺指向造环）: {a}->{b}")
    cyc = _first_cycle({(a, b) for a, bs in forward.items() for b in bs})
    if cyc:
        _err(errors, "CV-10——主序边成环（主序必须是 DAG，环只能由 feedback_loops 承载）: " + " -> ".join(cyc))

    # --- loops 台账（回边全集：in_graph 必须与 feedback_loops 一致）---
    loops = data.get("loops") or []
    if not isinstance(loops, list) or not loops:
        _err(errors, "loops（回边全集台账）不得为空——骨架 §2.2 B1~B15 逐条处置必须可见")
    else:
        declared = {(l.get("from"), l.get("to")) for l in loops if isinstance(l, dict)}
        seen_loop_ids: set[str] = set()
        for l in loops:
            if not isinstance(l, dict) or not l.get("loop_id"):
                _err(errors, f"loops 条目缺 loop_id: {l!r}")
                continue
            if l["loop_id"] in seen_loop_ids:
                _err(errors, f"loops.loop_id 重复: {l['loop_id']}")
            seen_loop_ids.add(l["loop_id"])
            kind = l.get("kind")
            if kind not in LOOP_KINDS:
                _err(errors, f"{l['loop_id']}: kind 非法 {kind!r}（枚举 {sorted(LOOP_KINDS)}）")
            f_, t_ = l.get("from"), l.get("to")
            if kind in ("in_graph", "in_graph_self_loop"):
                if f_ not in valid_ids or t_ not in valid_ids:
                    _err(errors, f"{l['loop_id']}: in_graph 回边两端必须在图内: {f_}->{t_}")
                if (f_, t_) not in feedback:
                    _err(errors, f"{l['loop_id']}: 声称 in_graph 却未进 feedback_loops（假门）")
            if kind in ("pending", "out_of_graph", "terminal_branch", "recovery_branch"):
                if not l.get("red_reason"):
                    _err(errors, f"{l['loop_id']}: 未进图的边必须写 red_reason（禁静默丢弃回边）")
                if t_ is not None and t_ != f_ and t_ in valid_ids and (f_, t_) not in feedback:
                    _err(
                        errors,
                        f"{l['loop_id']}: 目标 {t_} 已在图内却未声明 feedback_loops（用 pending 藏真回边=判据放水）",
                    )
                if kind == "pending" and t_ == f_ and max_rounds.get(f_):
                    _err(
                        errors,
                        f"{l['loop_id']}: 自环记 pending（称无轮次常量）却节点带 "
                        f"max_rounds_ref={max_rounds.get(f_)}——两口径互斥，必须进图",
                    )
        for fb in sorted(feedback):
            if fb not in declared:
                _err(errors, f"feedback_loops 条目 {fb[0]}->{fb[1]} 在 loops 台账无对应处置记录")

    # --- CV-15 boundary 逐字可回源（引用的仓内件必须存在）---
    for b in data.get("boundary", []) or []:
        path_m = re.search(r"([A-Za-z0-9_./\-]+\.(?:yaml|md))", str(b))
        if path_m:
            rel = path_m.group(1)
            if rel.startswith(_TRACKED_PREFIXES) and not (root / rel).exists():
                _err(errors, f"CV-15——boundary 引用的源文件不存在: {rel}")

    # --- CV-BUS 在册性（PG 不可达=降 warn，不阻断；--skip-live 整体跳）---
    want_ids = [str(n.get("module_id")) for n in nodes if isinstance(n, dict) and n.get("module_id")]
    missing_in_db = depgraph_missing_module_ids(sorted(set(want_ids)), root) if live else None
    if not live:
        pass  # --skip-live：PG 探测腿整体跳过（结构面零放宽，只断"提交时不做全仓探活"）
    elif missing_in_db is None:
        if warnings is not None:
            warnings.append("depgraph（PG）不可达：module_id 在册性核对降 warn（形态+投影两腿仍硬过）")
    else:
        for m in missing_in_db:
            _err(errors, f"CV-BUS——module_id 不在 depgraph 在册：{m}（幽灵总线号，禁自造）")

    # --- CV-12 INV-1 反复制（节点散文行不得抄政策正文）---
    pol = _read_policy(root)
    if pol:
        bodies = _policy_bodies(pol)
        for n in nodes:
            if not isinstance(n, dict):
                continue
            for f in ("name_zh", "decision_question", "note_zh", "fallback", "invalidation"):
                v = str(n.get(f, ""))
                if len(re.sub(r"\s+", "", v)) < _INV1_FIELD_MIN:
                    continue
                hit = _copy_hit(v, bodies)
                if hit:
                    _err(
                        errors,
                        f"{n.get('node_id')}: CV-12 INV-1 复制侵权——{f} 含政策正文"
                        f"连续 {len(hit)} 字（图只准存标识符与指针）: {hit[:40]}…",
                    )
    elif warnings is not None:
        warnings.append("政策 MD 不可读：CV-12 INV-1 反复制腿降 warn 跳过")
    return errors


def check_anchors(
    policy_text: str, data: dict, root: Path | None = None, warnings: list[str] | None = None
) -> list[str]:
    """政策面校验：Step 段双向闭合（CV-04）、pending_anchors 显式白名单、§2.3 矩阵（CV-11）、
    gap 节点 ghost 断言可复核（CV-GHOST）、deprecated 锚（CV-08）。

    gate 侧不调本函数（提交时不做全仓扫描，同 FACTORY-MAP 把仓储存在性排除在 gate 外的口径）；
    CLI 默认与 `--anchors-only` 调，align_all 经 `--json` 复用。
    """
    errors: list[str] = []
    root = root or _REPO_ROOT
    if not isinstance(data, dict) or not data.get("nodes"):
        _err(errors, "check_anchors：图数据为空或顶层非对象")
        return errors
    nodes = data.get("nodes", [])
    step_nodes = [n for n in nodes if isinstance(n, dict) and n.get("node_type") == "stage"]

    # --- CV-04 政策 ↔ 图 双向闭合 ---
    heads = set(_policy_step_heads(policy_text))
    declared = {str(n.get("policy_step", "")).replace("Step", "").strip() for n in step_nodes}
    pending = {str(x) for x in (data.get("pending_anchors") or [])}
    only_policy = sorted(heads - declared)
    only_graph = sorted(declared - heads)
    if only_policy:
        unaccounted = [s for s in only_policy if f"Step {s}" not in pending and f"D14-{s}" not in pending]
        if unaccounted:
            _err(errors, f"CV-04——政策有 Step 而图无节点且不在 pending_anchors: {', '.join(unaccounted)}")
    if only_graph:
        _err(errors, f"CV-04——图节点声称的 policy_step 在政策 Step 段集合中不存在（伪造环节）: {', '.join(only_graph)}")
    if len(step_nodes) != len(STEP_UNIVERSE):
        _err(errors, f"CV-04——stage 节点数 {len(step_nodes)} ≠ 契约环节数 {len(STEP_UNIVERSE)}")
    if str(data.get("anchor_source")) == "proposal" and not pending:
        _err(
            errors,
            "CV-04——anchor_source=proposal（政策未嵌块）却 pending_anchors 为空：欠账必须显式列全，禁『忘了就绿』",
        )
    if str(data.get("anchor_source")) == "policy" and pending:
        _err(errors, f"CV-04——政策已嵌块（anchor_source=policy）则 pending_anchors 必须清空，当前残留 {pending}")

    # --- CV-11 §2.3 关系矩阵 ↔ Step 段 ---
    rows = _policy_matrix_rows(policy_text)
    if not rows:
        if warnings is not None:
            warnings.append("政策 §2.3 矩阵不可解析：CV-11 降 warn 跳过")
    else:
        missing = sorted(heads - set(rows))
        extra = sorted(set(rows) - heads)
        if missing:
            _err(errors, f"CV-11——Step 段在 §2.3 矩阵缺行（骨架 R-15 同族）: {', '.join('Step ' + m for m in missing)}")
        if extra:
            _err(errors, f"CV-11——§2.3 矩阵有行而正文无对应 Step 段: {', '.join('Step ' + e for e in extra)}")

    # --- CV-GHOST：gap 断言可复核（幽灵复活即红；契约错类反向判）---
    for n in nodes:
        if not isinstance(n, dict) or n.get("node_type") != "gap":
            continue
        nid = n.get("node_id")
        ghosts = n.get("ghost_refs") or []
        gopts = n.get("ghost_options") or []
        gclis = n.get("ghost_cli_anchors") or []
        mm = n.get("mismatch_anchors") or []
        if not (ghosts or gopts or gclis or mm or n.get("ghost_doc_anchor")):
            _err(
                errors,
                f"{nid}: gap 节点必须至少一条可复核断言（ghost_refs / ghost_options /"
                f" ghost_cli_anchors / ghost_doc_anchor / mismatch_anchors）",
            )
        for g in ghosts:
            if (root / str(g)).exists():
                _err(errors, f"{nid}: CV-GHOST——断言为幽灵的件现已在盘（{g}）：须回写骨架并重生成，禁留着当红")
        for ca in list(gclis) + list(gopts):
            if not isinstance(ca, dict) or not ca.get("script") or not ca.get("option"):
                _err(errors, f"{nid}: ghost_cli_anchors/ghost_options 条目缺 script/option: {ca!r}")
                continue
            sp = root / str(ca["script"])
            if not sp.exists():
                _err(errors, f"{nid}: ghost 断言的件本身不存在（应归 missing-file 类）: {ca['script']}")
                continue
            if _option_present(sp.read_text(encoding="utf-8", errors="replace"), str(ca["option"])):
                _err(
                    errors,
                    f"{nid}: CV-GHOST——声称不存在的选项/子命令现已在册（{ca['script']}#"
                    f"{ca['option']}）：断言作废，须回写骨架",
                )
        for ma in mm:
            if not isinstance(ma, dict) or not ma.get("script") or not ma.get("option"):
                _err(errors, f"{nid}: mismatch_anchors 条目缺 script/option: {ma!r}")
                continue
            sp = root / str(ma["script"])
            if not sp.exists():
                _err(errors, f"{nid}: mismatch_anchors 的件不存在（应归 ghost_refs 类）: {ma['script']}")
                continue
            if not _option_present(sp.read_text(encoding="utf-8", errors="replace"), str(ma["option"])):
                _err(errors, f"{nid}: CV-GHOST——契约错断言失效（{ma['script']}#{ma['option']} 已不在册）：须回写骨架")
        da = n.get("ghost_doc_anchor")
        if da:
            dp = _anchor_path(str(da))
            sym = str(da).split("#", 1)[1] if "#" in str(da) else ""
            if not (root / dp).exists():
                _err(errors, f"{nid}: ghost_doc_anchor 路径不存在: {dp}")
            elif sym and sym in (root / dp).read_text(encoding="utf-8", errors="replace"):
                _err(errors, f"{nid}: CV-GHOST——声称不存在的符号锚已命中（{dp}#{sym}）：断言作废")

    # --- CV-08：deprecated/归档件支撑 automated ---
    for n in step_nodes:
        if n.get("verifiability") != "automated":
            continue
        for d in n.get("docs", []) or []:
            rel = str(d.get("path", "")) if isinstance(d, dict) else ""
            if rel and _is_deprecated_or_archived(root / rel):
                _err(errors, f"{n.get('node_id')}: CV-08——automated 环节的锚落在已废弃/归档件: {rel}")
    return errors


def _dup_values(pairs: list[Any]) -> list[int]:
    """order 重复检测（返回重复的序号值）。"""
    seen: dict[Any, int] = {}
    for v in pairs:
        seen[v] = seen.get(v, 0) + 1
    return sorted(k for k, c in seen.items() if c > 1)


def _first_cycle(edges: set[tuple[str, str]]) -> list[str] | None:
    """主序边环检测（DFS 三色，迭代栈防深递归）；有环返回环路径，无环返回 None。"""
    adj: dict[str, list[str]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
    nodes_all = sorted(set(adj) | {b for _, b in edges})
    WHITE, GRAY, BLACK = 0, 1, 2  # 三色标记：未访/在栈/已完成
    color = dict.fromkeys(nodes_all, WHITE)
    for start in nodes_all:
        if color[start] != WHITE:
            continue
        stack: list[tuple[str, list[str]]] = [(start, iter(sorted(adj.get(start, []))))]
        path: list[str] = [start]
        color[start] = GRAY
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = BLACK
                stack.pop()
                path.pop()
                continue
            if color.get(nxt) == GRAY:
                i = path.index(nxt)
                return path[i:] + [nxt]
            if color.get(nxt) == WHITE:
                color[nxt] = GRAY
                path.append(nxt)
                stack.append((nxt, iter(sorted(adj.get(nxt, [])))))
    return None


def _edit_distance_le2(a: str, b: str) -> bool:
    """近似名判定（编辑距离≤2，CV-06 点名"实名是 X"用；短串直接比长度上界）。"""
    if abs(len(a) - len(b)) > 2:
        return False
    if a == b:
        return True
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        if min(cur) > 2:
            return False
        prev = cur
    return prev[-1] <= 2


def _is_deprecated_or_archived(path: Path) -> bool:
    """CV-08：frontmatter status=deprecated 或路径含归档段 ⇒ 只能计 inspection/manual。"""
    if not path.exists():
        return False
    sp = path.as_posix()
    if "/_archive/" in f"/{sp}" or "/archive/" in f"/{sp}":
        return True
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return False
    head = text[:2000]
    return bool(re.search(r"^status:\s*deprecated", head, re.M))


def _read_policy(root: Path) -> str:
    """政策 MD 只读（不可读=空串，调用方降 warn）。"""
    p = root / DEFAULT_POLICY
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def check_prose_counts(map_text: str) -> list[str]:
    """CV-13 的散文腿：图 YAML 正文（非注释行）里不得写死"N 步/N 项"类计数。

    计数只准进 `counts:` 字段（骨架 R-12 实测政策六处计数漂移的图侧防线）。
    注释行以 `#` 开头，属生成器头说明，不入判。
    """
    errors: list[str] = []
    for i, line in enumerate(str(map_text).split("\n"), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if re.search(r"\d+\s*(步|环节|项)\b", s) and "counts" not in s:
            errors.append(f"CV-13——第 {i} 行把计数写进散文（改走 counts 字段）: {s[:60]}")
    return errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="图14 步骤锚校验（只读）")
    ap.add_argument("--steps", default=str(DEFAULT_MAP), help="图 YAML 路径")
    ap.add_argument(
        "--policy", default=str(DEFAULT_POLICY), help="政策 MD 路径（允许指向 fixture，供对抗测试与锚块预演）"
    )
    ap.add_argument(
        "--anchors-from",
        default=None,
        choices=["policy", "proposal"],
        help="锚块来源覆盖（缺省按图 YAML 的 anchor_source 字段）",
    )
    ap.add_argument("--anchors-only", action="store_true", help="只跑政策面/锚面校验（结构面必须已绿）")
    ap.add_argument(
        "--skip-live", action="store_true", help="跳过磁盘实存/在册类检查（CV-05/06/07/08 与 PG/投影腿），结构面零放宽"
    )
    ap.add_argument(
        "--json", action="store_true", dest="as_json", help="机器可读输出（供 align_all 内联复用，不 subprocess 自调）"
    )
    ap.add_argument("--root", default=str(_REPO_ROOT), help="路径锚磁盘实存的解析根（默认仓库根；禁 CWD 漂移）")
    args = ap.parse_args()

    path = Path(args.steps)
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
    if args.anchors_from:
        data["anchor_source"] = args.anchors_from

    root = Path(args.root)
    warnings: list[str] = []
    errors: list[str] = []
    if not args.anchors_only:
        errors += validate_structure(data, root=root, warnings=warnings, live=not args.skip_live)
        errors += check_prose_counts(raw)
    policy_path = Path(args.policy)
    policy_text = policy_path.read_text(encoding="utf-8", errors="replace") if policy_path.exists() else ""
    if not policy_text:
        warnings.append(f"政策 MD 不可读（{policy_path}）：CV-04/11/12 的政策腿降 warn")
    else:
        errors += check_anchors(policy_text, data, root=root, warnings=warnings)

    counts = data.get("counts") or {}
    scope = counts.get("by_verified_scope") or {}
    verif = counts.get("by_verifiability") or {}
    result = {
        "steps": str(path),
        "anchor_source": data.get("anchor_source"),
        "total_nodes": len(data.get("nodes") or []),
        "total_steps": counts.get("total_steps"),
        "total_gaps": (counts.get("by_node_type") or {}).get("gap"),
        "production": scope.get("production"),
        "structure": scope.get("structure"),
        "automated": verif.get("automated"),
        "inspection": verif.get("inspection"),
        "manual": verif.get("manual"),
        "errors": errors,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
    if errors:
        if not args.as_json:
            print(f"FAILED: {len(errors)} 个结构违规", file=sys.stderr)
        return 1
    if not args.as_json:
        print(
            f"PASS: 步骤锚校验通过（steps={result['total_steps']} "
            f"automated={result['automated']} inspection={result['inspection']} "
            f"manual={result['manual']} gap={result['total_gaps']} "
            f"production={result['production']} anchor_source={result['anchor_source']}）"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
