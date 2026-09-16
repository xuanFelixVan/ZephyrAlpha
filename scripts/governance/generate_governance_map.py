#!/usr/bin/env python3
# [BLUEPRINT] node_id=13719062 | scripts/governance/generate_governance_map.py | §new
# [MODULE] scripts.governance.generate_governance_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml; zephyr.shared.io.file_utils; zephyr.shared.utils.time_utils
# [CONSUMERS] config/governance_operations_map.yaml; 治理全景图前端页(规划中)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 机器层(families)全量重建; 人工层(pipeline/out_of_scope_refs/effective_from)原样保留; 静态计数只进 counts 字段不进散文; --dry-run 零写入
# [MODIFY-GUARD] config/governance_operations_map.yaml
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描失败即报错退出; 单文件解析失败跳过并计数
# [TESTS] tests/test_generate_governance_map.py
# [A_module] module_id=scripts.governance.generate_governance_map | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_governance_map.py — 治理运行地图(GOMAP-001)骨架生成器。

2026-09-15 治理挖矿战役产物(方案地图=docs/_working/2026-09-15-governance-module-mining-sop-map.md)。
设计裁定(Owner 2026-09-15):一张图不拆多张;只画运行时治理流水线主轴
(孵化→监控→水位→熔断→收割→自愈→审计),其他治理域挂引用不重建;骨架机生
(宪法 §9.5 静态清单禁手工维护),人工只填语义层。

机器源(零手工清单):
1. 模块头 [MODULE]/[DOMAIN]/[CONSUMERS]/[MATURITY](src/ + scripts/ 扫描)
2. 族分类关键词表(本文件 _FAMILY_PATTERNS,优先级序)
3. AST import 边检测接线状态(wired=静态 import 实锚 / wired_dynamic=importlib 字符串解析 /
   wired_by_header=仅头声明 / suspect_orphan=无任何消费证据)——解析 ast.Import/ast.ImportFrom,
   字符串字面量与散文/`__all__` 永不构成 wired(2026-09-15 治本:旧 substring 判定自证造假)
   wired_by_header 只判 [CONSUMERS] 非空、不辨语义;否定式头("无装配消费方…"/"none")实测
   17 件全落在本图治理域之外(2026-09-16 量),故不预设排除谓词——真进图再按词表裁定

输出: config/governance_operations_map.yaml
  - families        机器层:族→模块清单(每次全量重建)
  - pipeline        人工层:GOM-L0..L6 流水线挂载(生成器保留不动)
  - out_of_scope_refs 人工层:域外治理真源引用(生成器保留不动)
  - effective_from  人工层:首次落定 '2026-09-15'(生成器保留,防重跑漂移)
  - ttl             permanent(对齐 TDM 头部惯例)

CLI:
    python scripts/governance/generate_governance_map.py            # 生成/刷新
    python scripts/governance/generate_governance_map.py --dry-run  # 只打印摘要
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

OUTPUT_PATH = REPO_ROOT / "config" / "governance_operations_map.yaml"
SCAN_ROOTS = ("src/zephyr", "scripts")
SCAN_EXCLUDE_PARTS = ("__pycache__", "_archive", "tests", "test")
# 业务/数据面排除(其 monitor/probe 属数据质量治理,非系统运行时治理,进图即噪音)
_BUSINESS_EXCLUDE_PREFIXES = (
    "src/zephyr/data/", "src/zephyr/data_eng/", "src/zephyr/factor/", "src/zephyr/backtest/",
    "src/zephyr/ex_core/", "src/zephyr/regime/", "scripts/data/", "scripts/backtest/",
)
_HEADER_SCAN_LINES = 45

# 族分类关键词表(优先级序,首命中即定族)——新增治理族在此登记
_FAMILY_PATTERNS: tuple[tuple[str, str], ...] = (
    ("L3_fuse", r"kill_switch|killswitch|circuit_breaker|fuse_|fuset|degrade|failover|deadman|abort_"),
    ("L4_reap", r"reaper|orphan|zombie|ghost|cleanup_stash"),
    ("L5_selfheal", r"self_heal|selfhealer|reconcil|auto_fix|repair"),
    ("L2_resource", r"resource_guard|resource_optimization|gpu_|vram|hot_plane_budget|capacity_assurance|budget"),
    ("L1_monitor", r"watchdog|health|heartbeat|probe|telemetry|monitor"),
    ("L0_lifecycle", r"process_pool|process_lifecycle|supervisor|nssm|lifecycle|boot_hook|startup|shutdown|windows_service|spawn|daemon_registry|stop_gate"),
    ("L6_audit", r"status_dashboard|ai_audit|ops_guard"),
)
_GOVERNANCE_UNIVERSE = "|".join(p for _, p in _FAMILY_PATTERNS)
_GOVERNANCE_RE = re.compile(_GOVERNANCE_UNIVERSE, re.IGNORECASE)

_HEADER_RE = {
    "module": re.compile(r"#\s*\[MODULE\]\s*(\S+)"),
    "domain": re.compile(r"#\s*\[DOMAIN\]\s*(\S+)"),
    # [ \t]* not \s* : \s matches newlines, so an empty "# [CONSUMERS]" line would otherwise
    # swallow the newline and capture the next header line as a phantom declared consumer.
    "consumers": re.compile(r"#\s*\[CONSUMERS\][ \t]*(.+)"),
    "maturity": re.compile(r"#\s*\[MATURITY\]\s*(\S+)"),
    "ttl": re.compile(r"#\s*\[TTL\]\s*(\S+)"),
}

_OUT_OF_SCOPE_DEFAULTS = [
    {"name_zh": "提交门禁体系", "ref": "docs/01_policies_and_standards/_registry/catalogs/commit_gate_registry.yaml", "note_zh": "门禁是每模块配套,非运行时流水线节点"},
    {"name_zh": "数据治理", "ref": "docs/01_policies_and_standards/sop/data_ops_sop/data_ops_policy.md"},
    {"name_zh": "代码质量治理", "ref": "src/zephyr/gov_code_quality"},
    {"name_zh": "交易决策治理", "ref": "config/trading_decision_map.yaml"},
]

_PIPELINE_DEFAULT = {
    "layers": [
        {"id": "GOM-L0", "name_zh": "孵化", "desc_zh": "进程/服务出生:统一 spawn 入口、NSSM 永久服务、boot 编排", "mounts": []},
        {"id": "GOM-L1", "name_zh": "运行监控", "desc_zh": "心跳/健康探针/看门狗互检/遥测", "mounts": []},
        {"id": "GOM-L2", "name_zh": "资源水位", "desc_zh": "内存/CPU/GPU/磁盘阈值与告警、预算", "mounts": []},
        {"id": "GOM-L3", "name_zh": "熔断降级", "desc_zh": "kill_switch/熔断器/降级级联/死人开关", "mounts": []},
        {"id": "GOM-L4", "name_zh": "收割清理", "desc_zh": "孤儿/僵尸/幽灵进程收割,残留清理", "mounts": []},
        {"id": "GOM-L5", "name_zh": "自愈对账", "desc_zh": "self-heal/reconciler 事件驱动修复", "mounts": []},
        {"id": "GOM-L6", "name_zh": "复盘审计", "desc_zh": "审计日志/状态面板/治理复盘", "mounts": []},
    ]
}


def classify_family(text: str) -> str | None:
    for fam, pat in _FAMILY_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return fam
    return None


def parse_header(path: Path) -> dict[str, Any]:
    try:
        text = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:_HEADER_SCAN_LINES])
    except OSError:
        return {}
    out: dict[str, Any] = {}
    for key, rx in _HEADER_RE.items():
        m = rx.search(text)
        if m:
            out[key] = m.group(1).strip()
    return out


def _iter_py_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            parts = set(p.parts)
            if parts & set(SCAN_EXCLUDE_PARTS):
                continue
            files.append(p)
    return files


def _import_spec(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[0] == "src":
        return ".".join(parts[1:])
    return ".".join(parts)


# 运行时字符串分发调用名:模块以完整点分字符串出现且文件用它们动态导入 → wired_dynamic
_DYNAMIC_DISPATCH_CALLS = frozenset({"import_module", "__import__"})

# 接线四态枚举(稳定序)——counts 分布与 CLI 摘要的唯一真源,禁在别处硬编码 tier 清单
_WIRING_TIERS = ("wired", "wired_dynamic", "wired_by_header", "suspect_orphan")


def _package_dotted(path: Path) -> str:
    """文件所属包的点分路径(用于解析相对 import)。__init__.py 的包即其所在目录。"""
    spec = _import_spec(path)
    if path.name == "__init__.py" and spec.endswith(".__init__"):
        return spec[: -len(".__init__")]
    return spec.rsplit(".", 1)[0] if "." in spec else ""


def _wiring_key(path: Path) -> str:
    """候选匹配 import 边用的点分标识:__init__.py 归一到其包路径(否则 '...__init__'
    永不匹配任何 import 边),其余用完整模块 spec。"""
    spec = _import_spec(path)
    if path.name == "__init__.py" and spec.endswith(".__init__"):
        return spec[: -len(".__init__")]
    return spec


def _import_edges(node: ast.AST, pkg: str) -> set[str]:
    """单个 import 节点 → 点分边集（相对 import 依 pkg 解析；`import x.*` 不产点分边）。"""
    if isinstance(node, ast.Import):
        return {a.name for a in node.names}
    if not isinstance(node, ast.ImportFrom):
        return set()
    base = node.module or ""
    if node.level:
        anchor = pkg
        for _ in range(node.level - 1):
            anchor = anchor.rsplit(".", 1)[0] if "." in anchor else ""
        full = f"{anchor}.{base}" if base else anchor
    else:
        full = base
    if not full:
        return set()
    return {full} | {f"{full}.{a.name}" for a in node.names if a.name != "*"}


def _dotted_literal(node: ast.AST) -> str | None:
    """整串即点分模块名的字符串字面量（散文/docstring 含空格换行不入集）。"""
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return None
    v = node.value
    return v if "." in v and v.replace(".", "").isidentifier() else None


def _is_dispatch_call(node: ast.AST) -> bool:
    """是否为 importlib.import_module / __import__ 运行时分发调用点。"""
    if not isinstance(node, ast.Call):
        return False
    fn = node.func
    name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
    return name in _DYNAMIC_DISPATCH_CALLS


def _file_wiring_signals(tree: ast.AST, pkg: str) -> tuple[set[str], set[str], bool]:
    """单文件 AST → (真实 import 点分边集, 完整点分字符串字面量集, 是否含运行时分发调用)。

    import 边含模块级与函数内 ast.Import/ast.ImportFrom(相对 import 依 pkg 解析)。
    字符串字面量仅收"整串即点分模块名"者——散文/docstring 含空格换行不入集,`__all__`
    里的裸名不含点也不入集,二者都永不构成 wired。
    """
    edges: set[str] = set()
    strmods: set[str] = set()
    dispatch = False
    for node in ast.walk(tree):
        edges |= _import_edges(node, pkg)
        lit = _dotted_literal(node)
        if lit is not None:
            strmods.add(lit)
        dispatch = dispatch or _is_dispatch_call(node)
    return edges, strmods, dispatch


def _build_wiring_index(files: list[Path], wiring_keys: set[str]) -> dict[str, Any]:
    """单遍 AST 扫描全部候选文件,构建接线判定四索引(键=完整点分标识,非 token 子串)。

    - static[full] : 含指向 full 的真实 import 边(dotted)的文件集合
    - bare[stem]   : 以裸名 `import stem` / `from stem import ...`(无点,sys.path 插件式)引用的文件集合
    - strspec[full]: 把 full 作为完整点分字符串字面量出现在其内的文件集合
    - dispatch     : 含 importlib.import_module / __import__ 运行时分发调用的文件集合

    (旧实现是 `if tok in text` 子串命中——把 `__all__` 与散文也算作消费,虚报 wired。)
    """
    static: dict[str, set[str]] = {k: set() for k in wiring_keys}
    strspec: dict[str, set[str]] = {k: set() for k in wiring_keys}
    bare: dict[str, set[str]] = {}
    dispatch: set[str] = set()
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError, ValueError, RecursionError):
            continue
        cf = str(f)
        edges, strmods, has_dispatch = _file_wiring_signals(tree, _package_dotted(f))
        if has_dispatch:
            dispatch.add(cf)
        for e in edges:
            if "." in e:
                bucket = static.get(e)
                if bucket is not None:
                    bucket.add(cf)
            else:
                bare.setdefault(e, set()).add(cf)
        for sm in strmods:
            bucket = strspec.get(sm)
            if bucket is not None:
                bucket.add(cf)
    return {"static": static, "bare": bare, "strspec": strspec, "dispatch": dispatch}


def _wiring_evidence(c: dict[str, Any], idx: dict[str, Any]) -> tuple[set[str], set[str]]:
    """单候选的接线证据 → (静态 import 方集合, 运行时分发字符串引用集合)(自引用剔除)。

    裸名 sys.path 插件式 import(from x_reconciler import make_...)仅存在于 scripts 侧,
    故只对 scripts.* 候选启用 stem 命中,避免 stdlib 同名裸 import 误判 src 为 wired。
    """
    key = c["_key"]
    own = str(REPO_ROOT / c["path"])
    importers = {f for f in idx["static"].get(key, set()) if f != own}
    stem = key.rsplit(".", 1)[-1]
    if not importers and stem != "__init__" and c["_spec"].startswith("scripts."):
        importers = {f for f in idx["bare"].get(stem, set()) if f != own}
    dynamic = {f for f in idx["strspec"].get(key, set()) if f != own and f in idx["dispatch"]}
    return importers, dynamic


def _wiring_tier(c: dict[str, Any], idx: dict[str, Any]) -> str:
    """四态判定(优先级序):静态实锚 > 运行时分发 > 仅头声明 > 无消费证据。"""
    importers, dynamic = _wiring_evidence(c, idx)
    if importers:
        return "wired"
    if dynamic:
        return "wired_dynamic"
    if c["_consumers_header"]:
        return "wired_by_header"
    return "suspect_orphan"


def scan() -> dict[str, Any]:
    files = _iter_py_files()
    candidates: list[dict[str, Any]] = []
    for p in files:
        header = parse_header(p)
        rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        if rel.startswith(_BUSINESS_EXCLUDE_PREFIXES):
            continue
        # 族分类只看路径(模块身份),不看头文本——头里 monitor/startup 等词会大面积误伤
        fam = classify_family(rel)
        if fam is None:
            continue
        spec = _import_spec(p)
        candidates.append(
            {
                "module": header.get("module") or spec,
                "path": rel,
                "domain": header.get("domain", ""),
                "maturity": header.get("maturity", ""),
                "family": fam,
                "_spec": spec,
                "_key": _wiring_key(p),
                "_consumers_header": header.get("consumers", ""),
            }
        )
    wiring_keys = {c["_key"] for c in candidates}
    idx = _build_wiring_index(files, wiring_keys)
    modules: dict[str, Any] = {}
    for c in candidates:
        c["wiring"] = _wiring_tier(c, idx)
        c.pop("_spec")
        c.pop("_key")
        c.pop("_consumers_header")
        modules.setdefault(c["family"], []).append(c)
    for fam in modules:
        modules[fam].sort(key=lambda m: m["path"])
    return modules


def _build_counts(families: dict[str, Any]) -> dict[str, int]:
    """接线四态分布计数(机生,零硬编码;键序沿 _WIRING_TIERS 稳定便于 diff)。"""
    tiers = {t: 0 for t in _WIRING_TIERS}
    for mods in families.values():
        for m in mods:
            if m.get("wiring") in tiers:
                tiers[m["wiring"]] += 1
    return {
        "total_modules": sum(len(v) for v in families.values()),
        "wired": tiers["wired"],
        "wired_dynamic": tiers["wired_dynamic"],
        "wired_by_header": tiers["wired_by_header"],
        "suspect_orphans": tiers["suspect_orphan"],
    }


def build_document(dry_run: bool) -> dict[str, Any]:
    families = scan()
    human_keys: dict[str, Any] = {}
    if OUTPUT_PATH.exists():
        try:
            existing = yaml.safe_load(OUTPUT_PATH.read_text(encoding="utf-8")) or {}
            human_keys = {
                k: existing[k]
                for k in ("pipeline", "out_of_scope_refs", "effective_from")
                if k in existing
            }
        except (OSError, yaml.YAMLError):
            human_keys = {}
    doc: dict[str, Any] = {
        "schema_version": "0.1",
        "map_id": "GOMAP-001",
        "name_zh": "治理运行地图",
        "ttl": "permanent",
        "effective_from": human_keys.get("effective_from", "2026-09-15"),
        "generator": "scripts/governance/generate_governance_map.py",
        "generated_at": now_utc().isoformat(),
        "ssot_note_zh": (
            "骨架机生(宪法 §9.5):families 层由生成器全量重建,禁手工编辑;"
            "pipeline/out_of_scope_refs/effective_from 为人工语义层,生成器保留"
            "(effective_from 首次落定 '2026-09-15',防重跑漂移)。"
            "模块明细以稳定标识符引用,禁复制条目内容(TDM INV-1 同款纪律)。"
        ),
        "counts": _build_counts(families),
        "out_of_scope_refs": human_keys.get("out_of_scope_refs", _OUT_OF_SCOPE_DEFAULTS),
        "pipeline": human_keys.get("pipeline", _PIPELINE_DEFAULT),
        "families": families,
    }
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description="治理运行地图(GOMAP-001)骨架生成器")
    ap.add_argument("--dry-run", action="store_true", help="只打印摘要,零写入")
    args = ap.parse_args()

    doc = build_document(dry_run=args.dry_run)
    summary = ", ".join(f"{fam}={len(mods)}" for fam, mods in sorted(doc["families"].items()))
    print(f"families: {summary}")
    print(f"counts: {doc['counts']}")
    orphans = [m["path"] for mods in doc["families"].values() for m in mods if m["wiring"] == "suspect_orphan"]
    if orphans:
        print("suspect_orphans:")
        for p in orphans:
            print(f"  - {p}")
    if args.dry_run:
        print("[dry-run] 零写入")
        return 0
    payload = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
    ok = safe_write_text(OUTPUT_PATH, payload)
    if not ok:
        print(f"[ERROR] safe_write_text 失败(CAS 冲突?): {OUTPUT_PATH}", file=sys.stderr)
        return 1
    print(f"written: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
