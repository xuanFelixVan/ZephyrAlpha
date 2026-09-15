#!/usr/bin/env python3
# [BLUEPRINT] node_id=13719062 | scripts/governance/generate_governance_map.py | §new
# [MODULE] scripts.governance.generate_governance_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml; zephyr.shared.io.file_utils; zephyr.shared.utils.time_utils
# [CONSUMERS] config/governance_operations_map.yaml; 治理全景图前端页(规划中)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 机器层(families)全量重建; 人工层(pipeline/out_of_scope_refs)原样保留; 静态计数只进 counts 字段不进散文; --dry-run 零写入
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
3. import 反查接线状态(wired / wired_by_header / suspect_orphan)

输出: config/governance_operations_map.yaml
  - families        机器层:族→模块清单(每次全量重建)
  - pipeline        人工层:GOM-L0..L6 流水线挂载(生成器保留不动)
  - out_of_scope_refs 人工层:域外治理真源引用(生成器保留不动)

CLI:
    python scripts/governance/generate_governance_map.py            # 生成/刷新
    python scripts/governance/generate_governance_map.py --dry-run  # 只打印摘要
"""

from __future__ import annotations

import argparse
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
    "consumers": re.compile(r"#\s*\[CONSUMERS\]\s*(.+)"),
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


def _build_wiring_index(files: list[Path], tokens: set[str]) -> dict[str, set[str]]:
    """单遍扫描:token → 引用它的文件集合(排除 token 自身文件名命中)。"""
    index: dict[str, set[str]] = {t: set() for t in tokens}
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        stem = f.stem
        for tok in tokens:
            if tok == stem:
                continue  # 自身文件名不构成消费
            if tok in text:
                index[tok].add(str(f))
    return index


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
        tok = spec.rsplit(".", 1)[-1]
        candidates.append(
            {
                "module": header.get("module") or spec,
                "path": rel,
                "domain": header.get("domain", ""),
                "maturity": header.get("maturity", ""),
                "family": fam,
                "_token": tok,
                "_consumers_header": header.get("consumers", ""),
            }
        )
    tokens = {c["_token"] for c in candidates}
    wiring_index = _build_wiring_index(files, tokens)
    modules: dict[str, Any] = {}
    for c in candidates:
        refs = wiring_index.get(c["_token"], set())
        if refs:
            wiring = "wired"
        elif c["_consumers_header"]:
            wiring = "wired_by_header"
        else:
            wiring = "suspect_orphan"
        c.pop("_token")
        c.pop("_consumers_header")
        c["wiring"] = wiring
        modules.setdefault(c["family"], []).append(c)
    for fam in modules:
        modules[fam].sort(key=lambda m: m["path"])
    return modules


def build_document(dry_run: bool) -> dict[str, Any]:
    families = scan()
    human_keys: dict[str, Any] = {}
    if OUTPUT_PATH.exists():
        try:
            existing = yaml.safe_load(OUTPUT_PATH.read_text(encoding="utf-8")) or {}
            human_keys = {k: existing[k] for k in ("pipeline", "out_of_scope_refs") if k in existing}
        except (OSError, yaml.YAMLError):
            human_keys = {}
    doc: dict[str, Any] = {
        "schema_version": "0.1",
        "map_id": "GOMAP-001",
        "name_zh": "治理运行地图",
        "effective_from": now_utc().date().isoformat(),
        "generator": "scripts/governance/generate_governance_map.py",
        "generated_at": now_utc().isoformat(),
        "ssot_note_zh": (
            "骨架机生(宪法 §9.5):families 层由生成器全量重建,禁手工编辑;"
            "pipeline/out_of_scope_refs 为人工语义层,生成器保留。"
            "模块明细以稳定标识符引用,禁复制条目内容(TDM INV-1 同款纪律)。"
        ),
        "counts": {
            "total_modules": sum(len(v) for v in families.values()),
            "suspect_orphans": sum(
                1 for mods in families.values() for m in mods if m["wiring"] == "suspect_orphan"
            ),
        },
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
