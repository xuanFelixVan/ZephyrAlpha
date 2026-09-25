# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools
# [MODULE] zephyr.ai_layer.tools.inventory_generator
# [DOMAIN] D_GOVERNANCE
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.io.file_utils (safe_write_text);
#                zephyr.shared.utils.time_utils (now_utc); zephyr.ai_layer.tools (词表/ToolBenchError)
# [CONSUMERS] CLI python -m zephyr.ai_layer.tools.inventory_generator [--out PATH] [--report PATH];
#             config/tool_inventory.yaml（产出真源，禁手工增条目）;
#             resource_profile_registry 生成器第四源（C8 接线=后续授权批，本班不改既有生成器）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 五源聚合（capability_cards+mcp.json+tool_contracts.yaml+会话技能扫描+scripts 入口）
#              100% 索引；静态清单生成器产出禁手工维护（宪法 §9.5）——条目增删只经本模块再生；
#              幂等：条目载荷 canonical sha256（content_sha256）同输入同值，generated_at 不入幂等域；
#              family=删除 的工具缺 delete_class=拒产出（InventoryError 全清单列出，fail-closed，
#              OBJ_T DESIGN §6.1 接口点 1=登记闸）；删除类判词与判级词表 total 映射（测试护栏）；
#              运营态字段（usage/failure/latency/last_used）本表恒 null——真源=DB ai_tools
#              .tool_usage_stats（C2），不虚构计量（manual_v0 缺口诚实暴露于 stat_source 词表）；
#              卡≠运行态：capability_cards 只聚合 capability_id 做索引（organ=eye 系 DESIGN §2.3
#              族标签），不标运行态安全级；数量零写死（目录实读计数，宪法 §8 计数用字段）；
#              产出经 safe_write_text CAS 写入（热文件写入铁律）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §2（盘点 schema v0 真源；
#                字段增删先改设计稿；delete_class 判级映射改动须同批改测试）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源文件缺失/畸形→InventoryError（fail-closed，禁静默空源）；
#                  删除类缺 delete_class→InventoryError 逐条列出（拒产出）；
#                  capability_cards 内坏 YAML→跳过+计数留痕（fail-open，extraction_warnings）；
#                  写盘回读校验失败→safe_write_text 异常上抛（不吞）
# [TESTS] tests/ai_layer/tools/test_inventory_generator.py（五源聚合/删除闸拒产出/幂等双跑/
#         坏卡跳过留痕/词表 total 映射护栏/tmp_path 零生产路径）
"""inventory_generator — T1 工具资产盘点生成器（OBJ_T DESIGN §2，施工项 C1）。

五源聚合产出 ``config/tool_inventory.yaml``（治理锚定头+条目 schema v0）::

    S1 data/capability_cards/*.yaml      → kind=card（capability_id 索引，卡≠运行态）
    S2 config/mcp.json servers           → kind=mcp_server（safety_level=申报档位保守取高）
    S3 src/zephyr/integration/mcp/
       tool_contracts.yaml               → 契约锚 MOD-INF-013；仅在契约不在 mcp.json 的
                                            server=设计预留 → status=trial
    S4 ZCode 插件缓存技能扫描            → kind=skill（browser-use/computer-use 等，
                                            目录机扫零手工清单；缺席=诚实空源）
    S5 scripts/*.py 顶层入口清单          → kind=script（"入口清单"=顶层入口；
                                            递归展开属后续批次；删除族判词命中→family=删除）

删除红线接口点 1（登记闸，DESIGN §6.1）：family=删除 缺 delete_class=拒产出——
判词→判级 total 映射在码内（生成器自有知识，非手维护清单）；映射不认识的删除类
新工具=生成器拒绝产出并点名，补映射走代码评审而非改 YAML。
"""

from __future__ import annotations

from dataclasses import dataclass

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.ai_layer.tools import DELETE_CLASSES, STATUSES, ToolBenchError
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final = [
    "InventoryError",
    "DEFAULT_OUT_PATH",
    "DEFAULT_REPORT_PATH",
    "ENTRY_FIELDS",
    "build_inventory",
    "content_sha256",
    "generate",
    "main",
]

DEFAULT_OUT_PATH: Final = REPO_ROOT / "config" / "tool_inventory.yaml"
DEFAULT_REPORT_PATH: Final = (
    REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "OBJ_T_tools" / "inventory_v0_report.md"
)
MCP_JSON_PATH: Final = REPO_ROOT / "config" / "mcp.json"
TOOL_CONTRACTS_PATH: Final = REPO_ROOT / "src" / "zephyr" / "integration" / "mcp" / "tool_contracts.yaml"
CAPABILITY_CARDS_DIR: Final = REPO_ROOT / "data" / "capability_cards"
SCRIPTS_DIR: Final = REPO_ROOT / "scripts"
SKILL_CACHE_ROOT: Final = Path.home() / ".zcode" / "cli" / "plugins" / "cache"
CONTRACTS_BLUEPRINT_REF: Final = "MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md"

#: 条目 schema v0 字段序（DESIGN §2.1 盘点维度字段表；键序=产出键序，禁乱）
ENTRY_FIELDS: Final = (
    "tool_id", "name", "organ", "family", "kind",
    "entry_path", "module_id", "blueprint_ref", "capability_card_ref",
    "safety_level", "delete_class",
    "usage_30d", "failure_rate_30d", "latency_p50_s", "last_used_at", "stat_source",
    "model_affinity", "resource_profile_ref",
    "status", "registered_at", "review_at", "meta",
)

#: 删除族 token 词表（stem 按非字母数字切分后整词命中——子串匹配会误伤 settlement/battle）
DELETION_TOKENS: Final = (
    "reap", "reaper", "tombstone", "retire", "ttl", "cleanup", "clean",
    "purge", "delete", "del", "rm", "remove",
)
#: 删除 token→delete_class（total 映射；unknown=拒产出，DESIGN §6.1 接口点 1）
DELETE_CLASS_BY_TOKEN: Final = {
    "reap": "owner_gated",     # process_reaper：杀进程族=Owner 门位
    "reaper": "owner_gated",
    "tombstone": "tombstone",  # 墓碑登记族
    "retire": "tombstone",     # 退役族=墓碑
    "ttl": "ttl_only",         # TTL 清理族（.runtime/tmp 临时域）
    "cleanup": "ttl_only",
    "clean": "ttl_only",
    "purge": "owner_gated",    # 强清除族=Owner 门位
    "delete": "owner_gated",
    "del": "owner_gated",
    "rm": "owner_gated",
    "remove": "owner_gated",
}
#: 修改族 token 词表（scripts family=修改）
MUTATION_TOKENS: Final = (
    "generate", "gen", "apply", "sync", "register", "write", "update", "edit",
    "rename", "mv", "migrate", "patch", "regen",
)
#: 观测族 token 词表（scripts family=观测）
OBSERVE_TOKENS: Final = (
    "check", "verify", "audit", "status", "inspect", "monitor", "probe", "watch",
)
BUILTIN_TOOLS: Final = (  # 会话内建工具（DESIGN §2.3 眼·搜索/观测族实例；码内常量=生成器知识）
    ("builtin:WebSearch", "WebSearch"),
    ("builtin:WebFetch", "WebFetch"),
)


class InventoryError(ToolBenchError):
    """盘点失败（fail-closed：源缺失/畸形/删除闸拒产出，禁静默降级出表）。"""


@dataclass(frozen=True)
class EntrySpec:
    """_entry 的 13 字段规格对象（NO-LONG-PARAM-LIST 治本 2026-09-24）。"""

    tool_id: str
    name: str
    organ: str
    kind: str
    entry_path: str
    family: str | None
    safety_level: str | None
    status: str
    module_id: str | None = None
    blueprint_ref: str | None = None
    capability_card_ref: str | None = None
    delete_class: str | None = None
    meta: dict[str, Any] | None = None


def _entry(spec: "EntrySpec") -> dict[str, Any]:
    """按 ENTRY_FIELDS 键序构造单条目（运营态字段恒 null——真源=DB，见模块 docstring）。"""
    return {
        "tool_id": spec.tool_id,
        "name": spec.name,
        "organ": spec.organ,
        "family": spec.family,
        "kind": spec.kind,
        "entry_path": spec.entry_path,
        "module_id": spec.module_id,
        "blueprint_ref": spec.blueprint_ref,
        "capability_card_ref": spec.capability_card_ref,
        "safety_level": spec.safety_level,
        "delete_class": spec.delete_class,
        "usage_30d": None,
        "failure_rate_30d": None,
        "latency_p50_s": None,
        "last_used_at": None,
        "stat_source": None,
        "model_affinity": [],
        "resource_profile_ref": None,
        "status": spec.status,
        "registered_at": None,   # 由 generate 统一盖 generated_at，幂等域之外
        "review_at": None,
        "meta": spec.meta or {},
    }


def _stem_tokens(stem: str) -> list[str]:
    """stem→小写 token 序列（非字母数字切分；battle/settlement 不再误伤 ttl 子串）。"""
    import re

    return [t for t in re.split(r"[^a-z0-9]+", stem.lower()) if t]


def _script_family(stem: str, extra_deletion_tokens: tuple[str, ...] = ()) -> str:
    """脚本 family 判定（删除 token 优先，其余修改/观测/执行兜底；整词命中禁子串）。"""
    tokens = _stem_tokens(stem)
    if any(t in DELETION_TOKENS or t in extra_deletion_tokens for t in tokens):
        return "删除"
    if any(t in MUTATION_TOKENS for t in tokens):
        return "修改"
    if any(t in OBSERVE_TOKENS for t in tokens):
        return "观测"
    return "执行"


def _collect_cards(cards_dir: Path, *, warnings: list[str]) -> list[dict[str, Any]]:
    """S1 capability_cards：capability_id 索引（坏卡跳过留痕；目录实读计数零写死）。"""
    entries: list[dict[str, Any]] = []
    if not cards_dir.is_dir():
        raise InventoryError("capability_cards 目录不存在", details={"path": str(cards_dir)})
    for path in sorted(cards_dir.glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            warnings.append(f"bad_card_yaml:{path.name}:{type(exc).__name__}")
            continue
        if not isinstance(doc, dict) or not doc.get("capability_id"):
            warnings.append(f"not_a_card:{path.name}")
            continue
        cid = str(doc["capability_id"])
        entries.append(_entry(EntrySpec(
            f"card:{cid}", str(doc.get("name") or cid),
            organ="eye", kind="card", entry_path=str(path.relative_to(REPO_ROOT)),
            family=None, safety_level=None, status="active",
            module_id=str(doc.get("module_id") or "") or None,
            capability_card_ref=path.name,
            meta={"note": "卡≠运行态：索引件，capability_id 聚合（DESIGN §2.3）"},
        )))
    return entries


def _load_mcp_servers(path: Path) -> dict[str, Any]:
    """S2 前置：读 mcp.json servers 节（缺文件/畸形=InventoryError）。"""
    if not path.is_file():
        raise InventoryError("mcp.json 不存在", details={"path": str(path)})
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InventoryError(f"mcp.json 畸形: {exc}") from exc
    servers = doc.get("servers")
    if not isinstance(servers, dict) or not servers:
        raise InventoryError("mcp.json 缺 servers 节（空源=禁静默）")
    return servers


_SAFETY_RANK: Final = {"L": 0, "M": 1, "H": 2}


def _canonical_server_id(server_id: str) -> str:
    """跨源 server 归一 id（连字符/下划线同判——vector-memory 与 vector_memory 同件）。"""
    return server_id.replace("-", "_")


def _collect_mcp_servers(mcp_path: Path, contracts_path: Path) -> list[dict[str, Any]]:
    """S2+S3：mcp.json 全 servers（active）+ 仅在契约的 server（trial=设计预留）。"""
    servers = _load_mcp_servers(mcp_path)
    by_canonical: dict[str, dict[str, Any]] = {}
    for server_id, spec in sorted(servers.items()):
        levels = [str(x) for x in (spec.get("safety_level") or []) if str(x) in _SAFETY_RANK]
        safety = max(levels, key=lambda x: _SAFETY_RANK[x]) if levels else None
        by_canonical[_canonical_server_id(server_id)] = _entry(EntrySpec(
            f"mcp:{server_id}", server_id,
            organ="foot", kind="mcp_server", entry_path=f"mcp://{server_id}",
            family="MCP", safety_level=safety, status="active",
            module_id="MOD-INF-013", blueprint_ref=CONTRACTS_BLUEPRINT_REF,
            meta={
                "tool_count": spec.get("tool_count"),
                "transport": spec.get("transport"),
                "in_mcp_json": True,
            },
        ))
    if not contracts_path.is_file():
        raise InventoryError("tool_contracts.yaml 不存在", details={"path": str(contracts_path)})
    try:
        contracts = yaml.safe_load(contracts_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InventoryError(f"tool_contracts.yaml 畸形: {exc}") from exc
    if not isinstance(contracts, dict):
        raise InventoryError("tool_contracts.yaml 结构畸形（非映射）")
    for key, spec in sorted(contracts.items()):
        if not isinstance(spec, dict) or "server_id" not in spec:
            continue
        server_id = str(spec["server_id"])
        canonical = _canonical_server_id(server_id)
        existing = by_canonical.get(canonical)
        if existing is not None:
            existing["meta"]["contract_stability"] = spec.get("stability")
            if server_id != existing["name"]:
                existing["meta"]["contract_spelling"] = server_id
            continue
        by_canonical[canonical] = _entry(EntrySpec(
            f"mcp:{server_id}", server_id,
            organ="foot", kind="mcp_server", entry_path=f"mcp://{server_id}",
            family="MCP", safety_level=None, status="trial",
            module_id="MOD-INF-013", blueprint_ref=CONTRACTS_BLUEPRINT_REF,
            meta={"in_mcp_json": False, "note": "契约在档 mcp.json 未挂=skeleton/设计预留（DESIGN §2.3）"},
        ))
    return list(by_canonical.values())


def _collect_session_skills(skill_roots: tuple[Path, ...]) -> list[dict[str, Any]]:
    """S4 会话技能扫描（插件缓存 SKILL.md 机扫；多版本插件取最高版一条；根缺席=空源留痕）。"""
    best: dict[tuple[str, str], tuple[str, Path]] = {}
    for root in skill_roots:
        if not root.is_dir():
            continue
        for skill_md in sorted(root.glob("*/*/*/skills/*/SKILL.md")):
            plugin = skill_md.parts[-5]
            skill_name = skill_md.parts[-2]
            version = skill_md.parts[-4]
            key = (plugin, skill_name)
            if key not in best or _version_key(version) > _version_key(best[key][0]):
                best[key] = (version, skill_md)
    entries: list[dict[str, Any]] = []
    for (plugin, skill_name), (version, skill_md) in sorted(best.items()):
        family = "浏览器" if "browser" in plugin or "computer" in plugin else "传输"
        entries.append(_entry(EntrySpec(
            f"skill:{plugin}:{skill_name}", skill_name,
            organ="foot", kind="skill", entry_path=f"skill:{plugin}:{skill_name}",
            family=family, safety_level=None, status="active",
            meta={"plugin": plugin, "plugin_version": version, "scan_root": str(skill_roots[0])},
        )))
    return entries


def _version_key(version: str) -> tuple[int, ...]:
    """版本号→可比较元组（非数字段按 0 处理；仅用于多版本去选取新，不作语义承诺）。"""
    parts: list[int] = []
    for seg in version.split("."):
        parts.append(int(seg) if seg.isdigit() else 0)
    return tuple(parts)


def _collect_scripts(scripts_dir: Path, *, extra_deletion_tokens: tuple[str, ...] = (),
                     warnings: list[str] | None = None) -> list[dict[str, Any]]:
    """S5 scripts 顶层入口清单（*.py 非递归=入口语义；删除族缺 delete_class=拒产出）。"""
    if not scripts_dir.is_dir():
        raise InventoryError("scripts 目录不存在", details={"path": str(scripts_dir)})
    entries: list[dict[str, Any]] = []
    rejected: list[str] = []
    for path in sorted(scripts_dir.glob("*.py")):
        stem = path.stem
        family = _script_family(stem, extra_deletion_tokens)
        delete_class: str | None = None
        if family == "删除":
            tokens = [t for t in _stem_tokens(stem) if t in DELETION_TOKENS or t in extra_deletion_tokens]
            classes = {DELETE_CLASS_BY_TOKEN[t] for t in tokens if t in DELETE_CLASS_BY_TOKEN}
            if not classes:
                rejected.append(stem)   # 判词命中但判级缺=登记闸拒产出（fail-closed）
                continue
            if len(classes) > 1:
                rejected.append(f"{stem}:ambiguous_delete_class:{sorted(classes)}")
                continue
            delete_class = classes.pop()
        entries.append(_entry(EntrySpec(
            f"script:{stem}", stem,
            organ="hand", kind="script", entry_path=str(path.relative_to(REPO_ROOT)),
            family=family, safety_level="H" if delete_class else None,
            status="active", delete_class=delete_class,
            meta={"delete_class_source": "pattern_map" if delete_class else None},
        )))
    if rejected:
        raise InventoryError("删除类工具缺 delete_class=拒产出（DESIGN §6.1 接口点1）: " + ", ".join(rejected))
    if warnings is not None:
        warnings.append("scripts_scope:top_level_entry_only:入口清单=顶层 *.py（递归展开属后续批次）")
    return entries


def _collect_builtins() -> list[dict[str, Any]]:
    """S4 附录：会话内建工具（DESIGN §2.3 眼族实例；码内常量=生成器知识非手维护 YAML）。"""
    return [
        _entry(EntrySpec(tool_id, name, organ="eye", kind="builtin", entry_path=tool_id,
               family="搜索", safety_level=None, status="active",
               meta={"note": "会话内建工具（无仓内入口文件，manual 通道）"}))
        for tool_id, name in BUILTIN_TOOLS
    ]


def _validate_delete_gate(entries: list[dict[str, Any]]) -> None:
    """登记闸终检：family=删除 缺 delete_class=拒产出（含非 scripts 源，防御性）。"""
    bad = [e["tool_id"] for e in entries if e["family"] == "删除" and not e["delete_class"]]
    if bad:
        raise InventoryError("删除类缺 delete_class=拒产出: " + ", ".join(sorted(bad)))
    unknown = [
        (e["tool_id"], e["delete_class"]) for e in entries
        if e["delete_class"] is not None and e["delete_class"] not in DELETE_CLASSES
    ]
    if unknown:
        raise InventoryError(f"delete_class 词表外: {unknown}")


def build_inventory(
    *,
    cards_dir: Path = CAPABILITY_CARDS_DIR,
    mcp_path: Path = MCP_JSON_PATH,
    contracts_path: Path = TOOL_CONTRACTS_PATH,
    scripts_dir: Path = SCRIPTS_DIR,
    skill_roots: tuple[Path, ...] = (SKILL_CACHE_ROOT,),
) -> dict[str, Any]:
    """五源聚合 → 盘点文档 dict（条目按 tool_id 排序；content_sha256 入幂等域）。"""
    warnings: list[str] = []
    entries = []
    entries.extend(_collect_cards(cards_dir, warnings=warnings))
    entries.extend(_collect_mcp_servers(mcp_path, contracts_path))
    entries.extend(_collect_session_skills(skill_roots))
    entries.extend(_collect_builtins())
    entries.extend(_collect_scripts(scripts_dir, warnings=warnings))
    if not entries:
        raise InventoryError("五源聚合零条目（全空源=禁出表）")
    if not any(e["kind"] == "card" for e in entries):
        raise InventoryError("capability_cards 源零条目（S1 缺席=禁出表）")
    _validate_delete_gate(entries)
    entries.sort(key=lambda e: e["tool_id"])
    if not skill_roots or not skill_roots[0].is_dir():
        warnings.append("session_skills_scan_root_absent:S4 空源（诚实留痕，禁手补）")
    payload = json.dumps(entries, sort_keys=True, ensure_ascii=False)
    return {
        "schema_version": "1.0.0",
        "doc_type": "register",
        "ttl": "permanent",
        "title": "工具资产盘点表（tool inventory，生成器产出）",
        "status": "active",
        "generated_by": "zephyr.ai_layer.tools.inventory_generator",
        "maintenance": "auto",
        "counting_rule": "tools 数组条目数（五源全量再生；条目禁手工增删）",
        "total_tools": len(entries),
        "source_counts": {
            "capability_cards": sum(1 for e in entries if e["kind"] == "card"),
            "mcp_servers": sum(1 for e in entries if e["kind"] == "mcp_server"),
            "session_skills": sum(1 for e in entries if e["kind"] == "skill"),
            "builtin_tools": sum(1 for e in entries if e["kind"] == "builtin"),
            "script_entries": sum(1 for e in entries if e["kind"] == "script"),
        },
        "content_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "operations_note": (
            "运营态字段（usage/failure/latency/last_used/stat_source）本表恒 null——"
            "真源=DB ai_tools.tool_usage_stats（OBJ_T C2），不虚构计量"
        ),
        "extraction_warnings": warnings,
        "tools": entries,
    }


def content_sha256(doc: dict[str, Any]) -> str:
    """重算条目载荷 sha256（幂等核验口；generated_at 不入域）。"""
    payload = json.dumps(doc["tools"], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _render_report(doc: dict[str, Any]) -> str:
    """v0 盘点报告（一次性快照非第二真源；含人工核对栏）。"""
    lines = [
        "---",
        "ttl: task_bound",
        "title: OBJ_T T1 盘点报告 v0（一次性快照，长期真源=config/tool_inventory.yaml）",
        "status: snapshot",
        f"generated_at: {now_utc().isoformat()}",
        "---",
        "",
        "# T1 工具资产盘点 v0 报告（DESIGN §2.2 登记处）",
        "",
        f"- total_tools: {doc['total_tools']}（计数用字段，禁写死散文）",
        f"- source_counts: {doc['source_counts']}",
        f"- content_sha256: {doc['content_sha256']}",
        "",
        "## 人工核对栏（勾选后本报告方可作验收证据）",
        "",
        "- [ ] 删除族条目 delete_class 逐条抽核",
        "- [ ] mcp servers 与 config/mcp.json 实挂面一致",
        "- [ ] 会话技能扫描缺席项确认（S4 空源留痕）",
        "",
        "## extraction_warnings",
        "",
    ]
    lines.extend(f"- {w}" for w in (doc["extraction_warnings"] or ["（无）"]))
    return "\n".join(lines) + "\n"


def generate(
    *,
    out_path: Path = DEFAULT_OUT_PATH,
    report_path: Path | None = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    """再生盘点表并 CAS 落盘（幂等：同输入 content_sha256 同值）。返回文档 dict。"""
    doc = build_inventory()
    stamp = now_utc().isoformat()
    doc["generated_at"] = stamp
    for entry in doc["tools"]:
        entry["registered_at"] = stamp
    text = (
        "# --- 治理锚定 ---\n"
        "# blueprint: MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools\n"
        "# design_source: docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §2（盘点 schema v0）\n"
        "# 净零声明: 吸收 data/capability_cards/ 静态盘点为聚合索引（卡保留原位不删不改）；\n"
        "#           本表由生成器产出替代手工盘点清单（静态清单禁手工维护，宪法 §9.5）\n"
        "# --- 治理锚定结束 ---\n"
        + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, default_flow_style=False, width=110)
    )
    from zephyr.shared.io.file_utils import safe_write_text

    result = safe_write_text(out_path, text)
    logger.info("inventory written: %s (sha=%s)", out_path, result.after_sha256)
    if report_path is not None:
        safe_write_text(report_path, _render_report(doc))
    return doc


def main(argv: list[str] | None = None) -> int:
    """CLI：再生盘点表（--report 传空串关闭报告落盘；--out 落点重定向供测试）。"""
    parser = argparse.ArgumentParser(description="T1 工具盘点生成器（五源聚合，幂等）")
    parser.add_argument("--out", default=str(DEFAULT_OUT_PATH), help="产出 YAML 路径")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH),
                        help="盘点报告路径（传空串=关闭；缺省=OBJ_T_tools 目录快照）")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = Path(args.report) if args.report else None
    try:
        doc = generate(out_path=Path(args.out), report_path=report)
    except (InventoryError, OSError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"OK tools={doc['total_tools']} sha={doc['content_sha256'][:12]} out={args.out}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    sys.exit(main())
