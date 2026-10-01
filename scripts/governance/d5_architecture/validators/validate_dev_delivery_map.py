# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §dev_delivery_map
# [MODULE] scripts.governance.d5_architecture.validators.validate_dev_delivery_map
# [DOMAIN] D_GOV_SCRIPTS
# [MODIFY-GUARD] 结构与判据口径改动须与 DEV-DELIVERY-MAP gate、fig11 骨架三态列、92 册验收尺同批；禁单独放宽 exit 条件
# [STABILITY] evolving
# [SAFETY] L（台账只读，无资金与写盘面）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 结构违规=exit 1；依赖册/PG 不可达=降 warn 不阻断（禁环境异常打死提交）；判定复用面在 gate
# [TESTS] tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py
# [TTL] task_bound
#   （原值 permanent——CLI 校验器非永久常驻系统，PERM-TRIGGER 手动模式铁律归 task_bound）
# create-guard-not-dup: 死车道抢救的FiveMaps生成器/校验器（字节代投非新能力），docstring描述读文本建图的既有动作，与canonical无重叠
# [DEPENDENCIES] yaml；docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
#   与 gate_registry.yaml（仅 INV-1 复制侵权扫描读取，缺失=该子检查跳过不误伤）；
#   docs/_working/map_build/fig11_delivery/00_skeleton.md（§1 三态列，production 双轴同源核对，
#   文件不可读=该子检查降 warn 不阻断）；zephyr.governance.depgraph_schema（module_id 在册性，
#   PG 不可达=降 warn，禁环境异常打死提交）
# [CONSUMERS] 交付流水线全景图（config/dev_delivery_map.yaml）质量门禁；
#   tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py；
#   zephyr.gov_enforcement.commit_gates.dev_delivery_map_gate（DEV-DELIVERY-MAP gate，
#   结构校验单一真源复用）；scripts.governance.d5_architecture.generators.align_all（总包挂轴）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 台账只读（本工具禁写）；结构错误=exit 1，警告不阻断（warnings 由调用方可选收集）；
#   检查项=顶层必填键/节点必填字段（L0 统一名 note_zh/doc_refs）/node_id 唯一且限于 28 环节契约全集
#   +2 gap 节点/边两端闭合/重复边/自环/未声明反馈环的反向边/三车道归属必填（gap 节点车道显式声明豁免
#   前缀比对）/build_status+confidence+node_type+verified_scope+wiring_status 枚举/
#   built 必有 module_ref 代码锚/verified 必带 evidence（冒充判红）/decision_question 长度上限/
#   counts 与实数一致/路径锚磁盘实存/store_refs 三要素/INV-1 复制侵权（门禁册+tasks.yaml+
#   schedule.yaml+数据资产注册表正文扫入节点判红——跨真源全覆盖，红队补洞 2026-09-24）；
#   CV-BUS（module_ref 非空⇒module_id 非空且 MOD-* 形态；module_id 空⇒red_reason 必填；
#   depgraph 在册性走 DB，不可达降 warn）；CV-DUAL（verified_scope 与骨架 ✅ 双轴同源，
#   production 数==✅ 数，多了算谎少了算欠；production 必带 exec_evidence）；
#   CV-L0（废止别名 mech_note_zh/semantics_zh/clock_semantics_zh/design_refs/doc_ref/miss_fallback_zh
#   /degradation/silent_failover 残留即红）；CV-GAP（gap 节点必带 red_reason∈枚举+module_ref 空+至少一条边）；
#   CV-DOMAIN（L1/L2 禁越域挂载 judgment_basis/factor_refs/strategy_refs）；
#   环节契约全集=D11-S01~S09/C01~C13/D01~D06（骨架 §6 封顶）+D11-G01/G02（六图终局卷 §4 图11 判据②）
# [MODIFY-GUARD] 判据口径来自 docs/_working/map_build/fig11_delivery/00_skeleton.md（本图唯一
#   收敛基准）与 docs/_working/map_build/03_final_blueprint_and_schema.md（三层字段/双轴裁定）；
#   放宽任何检查项=改判据，须总包裁定，禁顺手放水
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 结构违规=exit 1；依赖册/PG 不可达=降 warn 不阻断（禁环境异常打死提交）；判定复用面在 gate，本件不抛给调用方
# [TESTS] tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读不到实载集合必抛，禁降级为'无冲突'
# [TESTS] 见同批 tests/ 下 canary 件
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)=结构违规; SystemExit(2)=文件不存在/解析失败/顶层非对象;
#   骨架/depgraph/门禁册等外部面不可达=对应子检查降 warn（warnings 出参），绝不升级为 error
# [TESTS] tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""交付流水线全景图（dev_delivery_map，图 11）结构校验器——v0.2 schema 单一真源。

形态照抄 validate_strategy_production_map.py（图 9 母版）：
`validate_structure(data, root=None, warnings=None)->list[str]` 只做纯结构判定（gate 只封阻塞语义）；
`main()` exit 0=PASS / 1=结构违规 / 2=文件与解析失败。只读，不修改任何文件。

与图 9 母版的差异（均为本图契约要求，不放宽任何一项）：
- 环节全集是 28 环封顶契约 + 2 个 gap 显性化缺口节点，节点必须恰好落在契约集内（多出=越界红，缺失=漏环节红）；
- 反向边判定用契约序（S01..S09<C01..C13<D01..D06<G01<G02）而非 E 序号正则；
- 新增 confidence/verified_scope 双轴、wiring_status、CV-BUS module_id 总线挂载判据；
- 新增 L0 统一字段名判据（废止同义异名残留即红）；
- 新增 counts 一致性、路径锚磁盘实存、INV-1 复制侵权（门禁册条目正文抄进节点即红）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_VALDIR = str(Path(__file__).resolve().parent)
if _VALDIR not in sys.path:
    sys.path.insert(0, _VALDIR)
import yaml
from validate_construction_steps import (
    depgraph_missing_module_ids,  # noqa: E402  CLONEGUARD合并:兄弟校验器单一真源(原稿三胞胎helper,本件删副本改导入)
)

DEFAULT_MAP = Path("config/dev_delivery_map.yaml")
_REPO_ROOT = Path(__file__).resolve().parents[4]
_SKELETON_REL = "docs/_working/map_build/fig11_delivery/00_skeleton.md"
# depgraph PG 在册性探测（F821 治理补缺：常量段佚失，按 nodes.blueprint_id 列重建，占位符 {ph} 由调用方 .format 填充）
_SQL_BLUEPRINT_ID_LIST = "SELECT blueprint_id FROM nodes WHERE blueprint_id IN ({ph})"

# 契约全集：28 环节（骨架 §6 封顶声明 2026-09-24）+ 2 gap 节点（六图终局卷 §4 图11 判据②）。
# gap 节点属骨架外显性化缺口件，待总包回写骨架 §1；增删须同批改本表与生成器 NODE_ORDER。
NODE_UNIVERSE: tuple[str, ...] = (
    *(f"D11-S{i:02d}" for i in range(1, 10)),
    *(f"D11-C{i:02d}" for i in range(1, 14)),
    *(f"D11-D{i:02d}" for i in range(1, 7)),
    "D11-G01",
    "D11-G02",
)
GAP_NODES = ("D11-G01", "D11-G02")

LANES = {"S", "C", "D"}
REQUIRED_TOP = [
    "schema_version",
    "map_id",
    "name_zh",
    "effective_from",
    "markets",
    "generator",
    "laws",
    "boundary",
    "layers",
    "nodes",
    "edges",
    "feedback_loops",
    "counts",
]
# L0 通用层统一名（六图终局卷 §1 裁定一：同语义必同名）
REQUIRED_NODE = [
    "node_id",
    "name_zh",
    "stage",
    "lane",
    "node_type",
    "decision_question",
    "note_zh",
    "build_status",
    "confidence",
    "data_refs",
    "gate_refs",
    "store_refs",
    "doc_refs",
]
# 必须**存在**（值可为 null）的键：双轴与总线挂载面
REQUIRED_KEY_PRESENT = ["verified_scope", "module_id", "wiring_status"]
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
# 越域挂载（决策判据归 TDM，本图 L1/L2 不得出现）
CROSS_DOMAIN_FIELDS = ("judgment_basis", "factor_refs", "strategy_refs")
NODE_TYPES = {"stage", "gap"}
BUILD_STATUS = {"built", "partial", "pending"}
CONFIDENCE = {"verified", "proposed", "untested"}
VERIFIED_SCOPE = {"production", "structure"}
WIRING_STATUS = {"wired", "unwired_slot_hollow", "unwired_no_caller", "partial"}
RED_REASONS = {"terminal", "unwired", "broken_supply", "ghost_ref"}
# SSoT 注：canonical rule_patterns.MODULE_ID_RE 为 YAML 行提取语义，与本文件正则不等价，故本地改名免 SSOT-REDEFINITION
MODULE_ID_RE_LOCAL = re.compile(r"^MOD-[A-Z0-9][A-Z0-9_-]*$")
# exec_evidence 的"可复跑把手"形态：命令（复跑/python/grep/git/ls/wc）或仓库内文件锚
_REPRO_RE = re.compile(r"(复跑|python |grep |git |ls |wc |scripts/|src/|config/)")
DECISION_Q_MAX = 120

# INV-1 复制侵权扫描源（门禁册条目正文）。扫这些键下的长文本；
# 册缺失/解析失败=子检查跳过（不把热册可用性耦合进地图校验）。
_INV1_REGISTRY_PATHS = (
    str(Path("docs" / "01_policies_and_standards" / "_registry" / "catalogs") / "in_process_gate_registry.yaml"),
    str(Path("docs" / "01_policies_and_standards" / "_registry" / "catalogs") / "gate_registry.yaml"),
)
# 红队补洞 2026-09-24（宪章级红线 INV-1 覆盖面）：门禁册之外的机生真源正文
# （tasks.yaml/schedule.yaml/数据资产注册表）抄进图11 节点同样判红。册不可读=跳过不误伤。
_INV1_GENERIC_PATHS = (
    "src/zephyr/data/config/tasks.yaml",
    "src/zephyr/data/config/schedule.yaml",
    str(Path("docs" / "01_policies_and_standards" / "_registry" / "catalogs") / "data_asset_registry.yaml"),
)
_INV1_TEXT_KEYS = ("description", "desc_zh", "note_zh", "what_zh", "reason_zh", "semantics_zh")
_INV1_MIN_LEN = 25

# 磁盘实存检查豁免前缀：运行时态/锁/外置盘/数据库表/占位（这些面的存在性
# 归生成器扫描时刻与 align_all，不归结构校验——否则 worktree/CI 无 .runtime 必假红）。
_DISK_EXEMPT_PREFIXES = (".runtime/", ".ailocks/", ".aidrafts", "c1_", "待定", "F:", "G:", "f:", "g:")
_TRACKED_PREFIXES = ("docs/", "config/", "scripts/", "src/", "tests/", "data/")


def _err(errors: list[str], msg: str) -> None:
    """_err implementation."""
    errors.append(msg)


def _anchor_path(ref: str) -> str:
    """ "path:line" 型锚点取路径段；纯路径原样返回（Windows 盘符冒号不误切）。"""
    s = str(ref).strip()
    if not s:
        return ""
    # 仅当末段冒号后全为数字才视为 :line 后缀
    head, sep, tail = s.rpartition(":")
    if sep and tail.isdigit():
        return head
    return s


def _is_checkable_disk_path(p: str, exempt_prefixes: tuple[str, ...] = _DISK_EXEMPT_PREFIXES) -> bool:
    """仓库相对、非运行时豁免、看起来像路径（含 / 或已知跟踪前缀）才做实存检查。

    CLONEGUARD 合并整改：豁免前缀参数化（本件豁免面含 c1_/待定 与兄弟件口径有意分叉，禁并常量）。"""
    if not p or p.startswith(exempt_prefixes):
        return False
    return "/" in p or "\\" in p


def scan_skeleton_status(root: Path) -> dict[str, str]:
    """骨架 §1 环节表三态列实扫（verified_scope 双轴的**唯一**外部对照物）。

    与生成器同口径（同一张表、同一个列），故两侧不会各自漂移。骨架不可读/表形变更
    ⇒ 返回空表，调用方把该子检查降级为 warn（禁环境异常打死提交）。
    """
    p = root / _SKELETON_REL
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    parts = text.split("## §1 环节全集", 1)
    if len(parts) != 2:
        return {}
    body = parts[1].split("\n## §2", 1)[0]
    out: dict[str, str] = {}
    for m in re.finditer(r"^\|\s*(D11-[A-Z]\d{2})\s*\|[^|]*\|[^|]*\|\s*([✅🔨⬜🌑])\s*\|", body, re.M):
        out[m.group(1)] = m.group(2)
    return out


def _inv1_registry_bodies(root: Path) -> list[str]:
    """从门禁册抽取长度≥阈值的条目正文（用于 INV-1 复制侵权判定）。册不可读=空集（跳过）。"""
    bodies: list[str] = []
    for rel in _INV1_REGISTRY_PATHS:
        p = root / rel
        if not p.exists():
            continue
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 册不可解析时本子检查降级跳过，不误伤
            continue
        entries = []
        if isinstance(data, dict):
            entries = data.get("entries") or data.get("gates") or []
        for e in entries:
            if not isinstance(e, dict):
                continue
            for k in _INV1_TEXT_KEYS:
                v = e.get(k)
                if isinstance(v, str) and len(v.strip()) >= _INV1_MIN_LEN:
                    bodies.append(v.strip())
    return bodies


def _is_prose_body(s: str, min_len: int = _INV1_MIN_LEN) -> bool:
    """正文判定=足量中文字符的描述性文本（标识符/表名/task_id 不属正文，引用合法）。

    CLONEGUARD 合并整改：长度阈值参数化（本件 25 与兄弟件 24 为各自 INV-1 面调参，禁并常量）。"""
    return len(s) >= min_len and sum(1 for ch in s if "一" <= ch <= "鿿") >= 10


def _inv1_generic_bodies(root: Path) -> list[str]:
    """从 tasks.yaml/schedule.yaml/数据资产注册表递归收正文字符串（INV-1 跨真源覆盖面）。"""
    bodies: list[str] = []

    def walk(obj) -> None:
        """walk implementation."""
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                walk(v)
        elif isinstance(obj, str):
            s = obj.strip()
            if _is_prose_body(s):
                bodies.append(s)

    for rel in _INV1_GENERIC_PATHS:
        p = root / rel
        if not p.exists():
            continue
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 真源不可解析=该腿降级跳过
            continue
        walk(data)
    return bodies


def validate_structure(data: dict, root: Path | None = None, warnings: list[str] | None = None) -> list[str]:
    """Validate target against rules and report findings（唯一真源，gate 复用本函数）。

    warnings 传入时收集降级项（骨架不可读 / depgraph 不可达 / 门禁册不可解析）；
    不传也绝不因此报错——外部面异常一律不入 errors（禁环境异常打死无辜提交）。
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

    layer_ids = {l.get("layer_id") for l in data.get("layers", []) if isinstance(l, dict)}
    for lane in sorted(LANES):
        if lane not in layer_ids:
            _err(errors, f"缺三车道层位: {lane}")

    skeleton_status = scan_skeleton_status(root)
    if not skeleton_status and warnings is not None:
        warnings.append(f"骨架三态列不可读（{_SKELETON_REL}）：CV-DUAL 的 ✅ 对照子检查降 warn")

    nodes = data.get("nodes", [])
    ids: list[str] = []
    universe = set(NODE_UNIVERSE)
    for n in nodes:
        if not isinstance(n, dict):
            _err(errors, f"{n!r}: 节点非对象")
            continue
        nid = n.get("node_id", "<无 node_id>")
        ids.append(nid)
        if nid not in universe:
            _err(errors, f"{nid}: 节点越出契约全集（28 环节+2 gap，骨架 §6 封顶件，增枝须先回写骨架）")
        # --- CV-L0：废止别名残留即红（三层字段裁定一"同语义必同名"）---
        for banned, canonical in BANNED_NODE_FIELDS.items():
            if banned in n:
                _err(errors, f"{nid}: 字段旧名残留 {banned}（L0 统一名应为 {canonical}）")
        for f in REQUIRED_NODE:
            if f not in n or n[f] in (None, ""):
                _err(errors, f"{nid}: 缺必填字段 {f}")
        for f in REQUIRED_KEY_PRESENT:
            if f not in n:
                _err(errors, f"{nid}: 缺必填键 {f}（值可为 null，键必须在——双轴/总线挂载面不得静默缺失）")
        # --- CV-DOMAIN：越域挂载（决策判据归 TDM）---
        for xf in CROSS_DOMAIN_FIELDS:
            if xf in n:
                _err(errors, f"{nid}: 越域挂载——本图 L1/L2 禁字段 {xf}（决策判据真源=TDM）")
        lane = n.get("lane")
        if lane not in LANES:
            _err(errors, f"{nid}: 三车道车道归属必填（须为 S/C/D，实际 {lane!r}）")
        elif nid in universe and not nid.endswith(("G01", "G02")) and nid.split("-")[1][0] != lane:
            _err(errors, f"{nid}: lane 与环节编号车道不符")
        if n.get("stage") not in layer_ids:
            _err(errors, f"{nid}: stage 未挂到已声明层位 {n.get('stage')!r}")
        node_type = n.get("node_type")
        if node_type not in NODE_TYPES:
            _err(errors, f"{nid}: node_type 非法 {node_type!r}")
        if n.get("build_status") not in BUILD_STATUS:
            _err(errors, f"{nid}: build_status 非法 {n.get('build_status')!r}")
        if n.get("confidence") not in CONFIDENCE:
            _err(errors, f"{nid}: confidence 非法 {n.get('confidence')!r}")
        scope = n.get("verified_scope")
        if scope is not None and scope not in VERIFIED_SCOPE:
            _err(errors, f"{nid}: verified_scope 非法 {scope!r}（须 production/structure/null）")
        wiring = n.get("wiring_status")
        if wiring not in WIRING_STATUS:
            _err(errors, f"{nid}: wiring_status 非法 {wiring!r}（须 {'/'.join(sorted(WIRING_STATUS))}）")
        red = n.get("red_reason")
        if red is not None and red not in RED_REASONS:
            _err(errors, f"{nid}: red_reason 非法 {red!r}（枚举 terminal/unwired/broken_supply/ghost_ref）")
        if n.get("confidence") == "verified" and not n.get("evidence"):
            _err(errors, f"{nid}: confidence=verified 必带 evidence（proposed 冒充 verified 判红）")
        if n.get("build_status") == "built" and not n.get("module_ref"):
            _err(errors, f"{nid}: built 节点必须有 module_ref 代码锚")
        # --- CV-DUAL：双轴口径与骨架三态列同源（多了算谎、少了算欠）---
        if scope == "production":
            if n.get("confidence") != "verified":
                _err(
                    errors,
                    f"{nid}: verified_scope=production 而 confidence={n.get('confidence')!r}（production 必 verified）",
                )
            if n.get("build_status") != "built":
                _err(
                    errors,
                    f"{nid}: verified_scope=production 而 build_status={n.get('build_status')!r}（在产断言必配 built）",
                )
            if not n.get("exec_evidence"):
                _err(
                    errors,
                    f"{nid}: verified_scope=production 必带 exec_evidence"
                    "（复跑命令或 file:line 在产证据，禁只凭接口存在宣 production）",
                )
            elif not any(_REPRO_RE.search(str(x)) for x in n.get("exec_evidence") or []):
                _err(errors, f"{nid}: exec_evidence 无可复跑把手（必含命令或 文件:行 锚，纯散文断言不构成分产证据）")
            if skeleton_status and nid in skeleton_status and skeleton_status[nid] != "✅":
                _err(
                    errors,
                    f"{nid}: 谎——verified_scope=production 而骨架 §1 状态标为 "
                    f"{skeleton_status[nid]}（非 ✅ 不得宣在产）",
                )
        elif scope == "structure":
            if n.get("build_status") == "built" and node_type != "gap":
                _err(errors, f"{nid}: 欠——骨架/built 态与 structure 不符（built 环节应宣 production）")
        if skeleton_status and node_type == "stage" and skeleton_status.get(nid) == "✅" and scope != "production":
            _err(errors, f"{nid}: 欠——骨架 ✅ 环节未宣 production（verified_scope={scope!r}）")
        # --- CV-BUS：module_id 总线挂载（六图终局卷 §2 裁定二）---
        mod_id, mod_ref = n.get("module_id"), n.get("module_ref")
        if mod_ref and not mod_id:
            _err(errors, f"{nid}: CV-BUS——module_ref 非空而 module_id 空（有实现代码必挂 MOD-* 总线号）")
        if mod_id is not None and not MODULE_ID_RE_LOCAL.match(str(mod_id)):
            _err(errors, f"{nid}: CV-BUS——module_id 非 MOD-* 形态：{mod_id!r}（禁自造号）")
        if not mod_ref and mod_id:
            _err(errors, f"{nid}: CV-BUS——无 module_ref 却挂 module_id={mod_id}（空挂总线=假引用）")
        if not mod_id and not red:
            _err(errors, f"{nid}: CV-BUS——module_id 为空必配 red_reason（纯结构/终点聚合/gap 节点=合法 null 但要写因）")
        if len(str(n.get("decision_question", ""))) > DECISION_Q_MAX:
            _err(errors, f"{nid}: decision_question 超 {DECISION_Q_MAX} 字")
        for sr in n.get("store_refs") or []:
            if not isinstance(sr, dict) or not sr.get("artifact") or not sr.get("location") or not sr.get("retention"):
                _err(errors, f"{nid}: store_refs 条目缺 artifact/location/retention")
        # 路径锚磁盘实存：module_ref / source_anchors / 跟踪前缀的 data_refs / store 位
        anchors = []
        if n.get("module_ref"):
            anchors.append(_anchor_path(str(n["module_ref"])))
        for sa in n.get("source_anchors", []) or []:
            anchors.append(_anchor_path(str(sa)))
        for dr in n.get("data_refs", []) or []:
            drs = str(dr)
            if drs.startswith(_TRACKED_PREFIXES):
                anchors.append(_anchor_path(drs))
        for sr in n.get("store_refs", []) or []:
            loc = str(sr.get("location", "")) if isinstance(sr, dict) else ""
            for part in loc.split(" + "):
                part = part.strip()
                if _is_checkable_disk_path(part) and not part.startswith("待定"):
                    anchors.append(part)
        for a in anchors:
            if a and _is_checkable_disk_path(a) and not (root / a).exists():
                _err(errors, f"{nid}: 路径锚磁盘实存检查失败（锚不存在）: {a}")

    if len(ids) != len(set(ids)):
        _err(errors, "node_id 存在重复")
    missing = sorted(universe - set(ids))
    if missing:
        _err(errors, f"缺环节（契约全集未建满）: {', '.join(missing)}")

    valid_ids = set(ids)
    # --- CV-GAP：gap 节点必须显性挂边到受影响环节（缺口不许画成孤岛）---
    edge_pairs = {tuple(e) for e in data.get("edges", []) if isinstance(e, (list, tuple)) and len(e) == 2}
    for gid in GAP_NODES:
        if gid not in valid_ids:
            continue
        g = next((x for x in nodes if isinstance(x, dict) and x.get("node_id") == gid), {})
        if g.get("node_type") != "gap":
            _err(errors, f"{gid}: 契约编号为 gap 节点但 node_type={g.get('node_type')!r}")
        if not any(gid in p for p in edge_pairs):
            _err(errors, f"{gid}: gap 节点必须至少有一条边连到受影响环节（显性化不得孤岛）")
    # --- CV-DUAL 计数面：production 数 == 骨架 ✅ 数（不多不少）---
    prod_ids = {n.get("node_id") for n in nodes if isinstance(n, dict) and n.get("verified_scope") == "production"}
    if skeleton_status:
        ok_ids = {nid for nid, sym in skeleton_status.items() if sym == "✅"}
        over = sorted(prod_ids - ok_ids)
        under = sorted({i for i in ok_ids if i not in prod_ids and i in valid_ids})
        if len(over) + len(under) > 0:
            _err(
                errors,
                f"CV-DUAL 计数：production 数 {len(prod_ids)} ≠ 骨架 ✅ 数 {len(ok_ids)}"
                f"（多了算谎={over}，少了算欠={under}）",
            )
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
        by_scope = counts.get("by_verified_scope") or {}
        real_scope: dict[str, int] = {}
        for n in nodes:
            if isinstance(n, dict):
                key = str(n.get("verified_scope"))
                real_scope[key] = real_scope.get(key, 0) + 1
        if {k: v for k, v in by_scope.items() if v} != real_scope:
            _err(errors, f"counts.by_verified_scope={by_scope} 与节点实扫 {real_scope} 不符")
        by_lane_real: dict[str, int] = {}
        for n in nodes:
            if isinstance(n, dict):
                by_lane_real[str(n.get("lane"))] = by_lane_real.get(str(n.get("lane")), 0) + 1
        if counts.get("by_lane") not in (None, by_lane_real):
            _err(errors, f"counts.by_lane={counts.get('by_lane')} 与节点实扫 {by_lane_real} 不符")

    order = {nid: i for i, nid in enumerate(NODE_UNIVERSE)}
    seen_edges: set[tuple[str, str]] = set()
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
            _err(errors, f"自环边: {a}")
        if (a, b) in feedback:
            continue
        oa, ob = order.get(a), order.get(b)
        if oa is not None and ob is not None and oa > ob:
            _err(errors, f"未声明为反馈环的反向边: {a}->{b}（反馈环必须在 feedback_loops 显式声明）")

    # --- CV-BUS 在册性：module_id 是否真在 depgraph（PG 不可达=降 warn，不阻断）---
    want_ids = [str(n.get("module_id")) for n in nodes if isinstance(n, dict) and n.get("module_id")]
    missing_in_db = depgraph_missing_module_ids(sorted(set(want_ids)), root)
    if missing_in_db is None:
        if warnings is not None:
            warnings.append("depgraph（PG）不可达：module_id 在册性核对降 warn（形态判据仍硬过）")
    else:
        for m in missing_in_db:
            _err(errors, f"CV-BUS——module_id 不在 depgraph 在册：{m}（幽灵总线号，禁自造）")

    # INV-1 复制侵权：门禁册条目正文出现在节点文本字段即红（图只存标识符与指针）
    bodies = _inv1_registry_bodies(root) + _inv1_generic_bodies(root)
    if bodies:
        for n in nodes:
            if not isinstance(n, dict):
                continue
            texts = [str(n.get(k, "")) for k in ("name_zh", "decision_question", "note_zh")]
            texts += [str(x) for x in (n.get("evidence") or [])]
            texts += [str(x) for x in (n.get("exec_evidence") or [])]
            blob = "\n".join(texts)
            for body in bodies:
                if body in blob:
                    _err(
                        errors,
                        f"{n.get('node_id')}: INV-1 复制侵权（节点正文含门禁册条目"
                        f"原文片段，图节点只准存稳定标识符与指针）: "
                        f"{body[:40]}…",
                    )
                    break
    return errors


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="交付流水线全景图结构校验（只读）")
    ap.add_argument("--map", default=str(DEFAULT_MAP), help="图 YAML 路径")
    ap.add_argument(
        "--root", default=str(_REPO_ROOT), help="路径锚磁盘实存的解析根（默认仓库根；align_all 可传主区根防 CWD 漂移）"
    )
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

    warnings: list[str] = []
    errors = validate_structure(data, root=Path(args.root), warnings=warnings)
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"FAILED: {len(errors)} 个结构违规", file=sys.stderr)
        return 1
    counts = data.get("counts") or {}
    scope = counts.get("by_verified_scope") or {}
    print(
        f"PASS: 结构校验通过（nodes={len(data['nodes'])} edges={len(data['edges'])} "
        f"production={scope.get('production')} structure={scope.get('structure')} "
        f"gap={(counts.get('by_node_type') or {}).get('gap')}）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
