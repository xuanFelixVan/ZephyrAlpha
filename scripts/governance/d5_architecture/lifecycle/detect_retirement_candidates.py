# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/d5_architecture/lifecycle/detect_retirement_candidates.py | §
# [MODULE] scripts.governance.d5_architecture.lifecycle.detect_retirement_candidates
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants; zephyr.shared.io.file_utils
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读探测：零 DDL/零写库；除自己的报告（--output/--staging）零写盘；候选仅为情报提示，永不直接改任何模块状态
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=报告产出（候选为情报非门禁）；exit 2=数据源/参数错误；任一数据源不可用时该路信号按未知处理=保守排除，宁漏报不误报
# [TESTS] tests/governance/lifecycle/test_detect_retirement_candidates.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""detect_retirement_candidates.py — 退役候选四路机械探测器（MLC-003 前置情报，B10-P1）

对标：trae_032 mod_003 MLC-003 退役七步（从未实现，本件为其候选探测第一真身）；
     S9 挖矿簿 docs/_working/fms_overhaul/S9_module_retirement/README.md §4.1。

四路数据源（全部只读，零 DDL）：
  R_d  depgraph 反向入边计数（nodes.blueprint_id/belongs_to 归属聚合 edges 入边）
  G_d  git 活动度：注册路径距最后一次 commit 的天数
  P_d  图书馆 lib_assets.potential_consumers 基数（活跃资产，asset_id/home 匹配）
  C_d  capability 反查：capability_canonical_file_registry.yaml canonical_override 命中

候选公式（S9 簿 §4.1 提案原文）：
  候选(m) := (R_d==0) AND (G_d>=90) AND (P_d in {0,NULL}) AND (C_d==0)
             AND (status==active) AND 不在白名单
  白名单 := P0 ∪ risk_tier=high 域 ∪ capability canonical 命中 ∪ 近30天有 commit ∪ ROOR 在册
  评分: score = 2*零R_d + 2*(G_d>=90) + 1*零P_d + 1*零C_d + 1*(G_d>=180)  # 仅排序展示

P0 红线：P0 模块永不自动判退役——只提示（P0_HINT 节），禁入候选。
保守性铁律：任一路数据源不可用（PG 不可达/词表缺/git 无记录）→ 该路信号按
"未知"处理，未知不满足候选公式 → 宁漏报不误报。探测结果只是候选，
无 Owner 批准（裁定登记）不得改任何模块状态。

automation 分级（宪法 §5 + risk_tier_registry）：本件=全自动周报级（纯只读零风险）；
标记 deprecated/git mv/IFC-007 确认=Owner 门位，走 retire_module.py --owner-ruling。

C_d 余量登记（P1 降级处方）：capability 派生 canonical_file（磁盘头部+git log 机生）
未纳入——只读引用声明式 canonical_override；派生面并入 P2。
"""

from __future__ import annotations

__manifest__ = """
args: [--output, --staging, --session, --registry, --capability-registry, --roor,
       --candidate-registry, --risk-tier-registry, --top, --p0-extra]
description: 退役候选四路机械探测（MLC-003 前置情报；只读；候选仅提示）
dimensions:
- D5
priority: P2
timeout_seconds: 120
warn_only: true
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
import yaml  # noqa: E402
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT  # noqa: E402

# SQL 集中化（§5.160.2 NO-BARE-SQL）：模块级常量，禁散落
_SQL_DEPGRAPH_NODE_CONSUMERS = (
    "SELECT n.blueprint_id AS bid, n.belongs_to AS bel, n.domain_id AS dom, "
    "COUNT(e.edge_id) AS c "
    "FROM nodes n LEFT JOIN edges e ON e.to_node_id = n.node_id "
    "GROUP BY n.blueprint_id, n.belongs_to, n.domain_id"
)
_SQL_LIBASSET_CONSUMERS = (
    "SELECT asset_id, cardinality(potential_consumers) AS c FROM lib_assets "
    "WHERE status = 'active' AND (asset_id = %s OR home = %s OR home LIKE %s)"
)

DEFAULT_REGISTRY = Path("architecture_model/module_id_registry.yaml")
DEFAULT_CAPABILITY_REGISTRY = Path(
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
)
DEFAULT_CANDIDATE_REGISTRY = Path("docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml")
DEFAULT_RISK_TIER_REGISTRY = Path("docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml")
DEFAULT_ROOR = Path("docs/registry_of_registries.yaml")

STALE_DAYS = 90
RECENT_DAYS = 30
VERY_STALE_DAYS = 180


# ---------- 数据模型 ----------


@dataclass
class Evidence:
    """单模块四路证据。None=该路数据源不可用/无法判定（保守：不满足候选公式）。"""

    r_d: int | None = None
    g_d: int | None = None
    p_d: int | None = None
    p_d_assets: list[str] = field(default_factory=list)
    c_d: int | None = None
    domains: list[str] = field(default_factory=list)
    p0: bool = False
    p0_sources: list[str] = field(default_factory=list)
    whitelist: list[str] = field(default_factory=list)
    sources_ok: dict[str, bool] = field(default_factory=dict)


@dataclass
class Row:
    module_id: str
    path: str
    status: str
    ev: Evidence
    score: int = 0
    is_candidate: bool = False
    tier: str = "-"


# ---------- 四路数据源（只读） ----------


def load_registry_modules(registry_path: Path) -> list[dict]:
    """读 module_id_registry.yaml registered_ids 条目（含 status/path）。"""
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    return [e for e in (data.get("registered_ids") or []) if isinstance(e, dict) and e.get("module_id")]


def fetch_depgraph_inedges(conn: Any) -> tuple[dict[str, int], dict[str, list[str]], bool]:
    """depgraph 反向入边计数，按 blueprint_id/belongs_to 归属聚合；附带域归属。

    返回 (module_id->入边总数, module_id->domains 列表, 数据源是否可用)。
    """
    if conn is None:
        return {}, {}, False
    try:
        rows = conn.execute(_SQL_DEPGRAPH_NODE_CONSUMERS).fetchall()
    except Exception:  # noqa: BLE001 -- fail-open 哨兵：数据源不可用即放弃反向计数，不限异常族
        return {}, {}, False
    edges: dict[str, int] = {}
    domains: dict[str, list[str]] = {}
    for r in rows:
        for mid in {r["bid"], r["bel"]}:
            if not mid:
                continue
            edges[mid] = edges.get(mid, 0) + int(r["c"] or 0)
            if r["dom"] and r["dom"] not in domains.setdefault(mid, []):
                domains[mid].append(r["dom"])
    return edges, domains, True


def fetch_library_consumers(conn: Any, module_id: str, path: str) -> tuple[int | None, list[str], bool]:
    """图书馆潜在消费者基数：活跃资产 asset_id 精确/home 前缀匹配 potential_consumers。

    返回 (最大基数或 None=未评估, 命中 asset_id 列表, 数据源是否可用)。
    """
    if conn is None:
        return None, [], False
    try:
        rows = conn.execute(
            _SQL_LIBASSET_CONSUMERS,
            (module_id, path, (path or "\x00") + "%"),
        ).fetchall()
    except Exception:  # noqa: BLE001 -- fail-open 哨兵：数据源不可用即放弃消费者基数，不限异常族
        return None, [], False
    if not rows:
        return None, [], True
    best = max(int(r["c"] or 0) for r in rows)
    return best, [r["asset_id"] for r in rows], True


def git_days_since_last_commit(repo_root: Path, rel_path: str) -> int | None:
    """注册路径距最后一次 commit 的天数；无记录/路径缺失→None。"""
    if not rel_path:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%ci", "--", rel_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    if not out:
        return None
    try:
        # git %ci 形如 '2026-09-20 12:20:26 +0800'——固定取前 19 字符解析（时区偏移不参与）
        dt = datetime.strptime(out.strip()[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return (datetime.now() - dt).days


def load_capability_canonical_paths(registry_path: Path) -> tuple[set[str], bool]:
    """capability 反查面（P1 降级处方：只读声明式 canonical_override）。"""
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return set(), False
    paths = set()
    for cap in data.get("capabilities") or []:
        if isinstance(cap, dict) and cap.get("canonical_override"):
            paths.add(str(cap["canonical_override"]).replace("\\", "/"))
    return paths, True


def load_risk_tier_high_domains(registry_path: Path) -> tuple[set[str], bool]:
    """risk_tier_registry domain_tiers 中 tier==high 的域集合。"""
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return set(), False
    highs = set()
    for e in data.get("domain_tiers") or []:
        if isinstance(e, dict) and e.get("tier") == "high" and e.get("domain"):
            highs.add(str(e["domain"]))
    return highs, True


def load_roor_paths(roor_path: Path) -> tuple[set[str], bool]:
    """ROOR 全树扫 physical_path 类路径串（ROOR 在册=治理活资产，白名单）。"""
    try:
        data = yaml.safe_load(roor_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return set(), False
    paths: set[str] = set()

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in {"physical_path", "path", "ssot_path", "canonical_file"} and isinstance(v, str):
                    paths.add(v.replace("\\", "/"))
                else:
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return paths, True


def _p0_frontmatter_hit(repo_root: Path, module_path: str) -> bool:
    """P0 源①：条目文件头 2000 字符 frontmatter priority==P0 判定（不可读=不命中，保守）。"""
    if not module_path:
        return False
    p = repo_root / module_path
    if not p.exists():
        return False
    try:
        head = p.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return False
    for line in head.splitlines():
        s = line.strip()
        if s.startswith("priority:") and "P0" in s:
            return True
    return False


def _p0_candidate_registry_hit(candidate_registry_path: Path, module_id: str, module_path: str) -> bool:
    """P0 源②：候选池 P0 条目按 module_id/path/candidate_id/title token 命中（册不可读=不命中，保守）。"""
    try:
        data = yaml.safe_load(candidate_registry_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return False
    for cand in data.get("candidates") or data.get("entries") or []:
        if not isinstance(cand, dict) or cand.get("priority") != "P0":
            continue
        tokens = {str(cand.get(k, "")) for k in ("module_id", "path", "candidate_id", "title")}
        if module_id in tokens or (module_path and module_path in tokens):
            return True
    return False


def detect_p0(
    module_id: str,
    module_path: str,
    repo_root: Path,
    candidate_registry_path: Path,
    extra_ids: list[str],
) -> tuple[bool, list[str]]:
    """P0 判定（保守多源）：条目文件 frontmatter priority==P0 ∪ 候选池 P0 条目命中 ∪ Owner 附加清单。"""
    sources: list[str] = []
    if module_id in extra_ids:
        sources.append("owner-extra")
    if _p0_frontmatter_hit(repo_root, module_path):
        sources.append("frontmatter-priority")
    if _p0_candidate_registry_hit(candidate_registry_path, module_id, module_path):
        sources.append("candidate-registry-P0")
    return bool(sources), sorted(set(sources))


# ---------- 判定核心 ----------


def _assign_tier(row: Row, ev: Evidence, very_stale: bool) -> None:
    """建议档位（原位赋值 row.tier）：P0 提示 > 候选-A > 候选-B > 观察名单（缺省 "-"）。"""
    if ev.p0:
        row.tier = "P0-仅提示（禁自动退役）"
    elif row.is_candidate and very_stale:
        row.tier = "候选-A-优先尽调（半年度静止）"
    elif row.is_candidate:
        row.tier = "候选-B-常规尽调"
    elif row.score >= 5:
        row.tier = "观察名单"


def evaluate_module(entry: dict, ev: Evidence) -> Row:
    """候选公式 + 白名单 + 评分 + 建议档位（纯函数，可测）。"""
    mid = entry["module_id"]
    path = str(entry.get("path") or "")
    status = str(entry.get("status") or "")
    row = Row(module_id=mid, path=path, status=status, ev=ev)

    known_zero_r = ev.r_d == 0  # None（源不可用）不算零
    stale = ev.g_d is not None and ev.g_d >= STALE_DAYS
    no_lib_consumers = ev.p_d is None or ev.p_d == 0
    no_capability = ev.c_d == 0  # None（源不可用）不算零
    very_stale = ev.g_d is not None and ev.g_d >= VERY_STALE_DAYS

    row.score = (
        2 * int(known_zero_r)
        + 2 * int(stale)
        + 1 * int(no_lib_consumers)
        + 1 * int(no_capability)
        + 1 * int(very_stale)
    )

    wl = ev.whitelist
    row.is_candidate = (
        status == "active" and known_zero_r and stale and no_lib_consumers and no_capability and not ev.p0 and not wl
    )
    _assign_tier(row, ev, very_stale)
    return row


def _capability_signal(path: str, capability_paths: set[str], capability_ok: bool) -> int | None:
    """C_d 信号：1=canonical 命中；0=可用未命中；None=数据源不可用（保守未知）。"""
    if not capability_ok:
        return None
    return 1 if (path and path in capability_paths) else 0


def _append_whitelist_reasons(
    ev: Evidence,
    path: str,
    *,
    capability_ok: bool,
    high_domains: set[str],
    high_ok: bool,
    roor_paths: set[str],
    roor_ok: bool,
) -> None:
    """白名单原因追加：P0 红线 / capability canonical / 近30天活跃 / high 域 / ROOR 在册。"""
    if ev.p0:
        ev.whitelist.append("P0 红线（" + ",".join(ev.p0_sources) + "）")
    if capability_ok and ev.c_d:
        ev.whitelist.append("capability canonical 命中")
    if ev.g_d is not None and ev.g_d < RECENT_DAYS:
        ev.whitelist.append(f"近{RECENT_DAYS}天活跃（G_d={ev.g_d}）")
    if high_ok and ev.domains and set(ev.domains) & high_domains:
        ev.whitelist.append("high 风险域（" + ",".join(sorted(set(ev.domains) & high_domains)) + "）")
    if roor_ok and path and path in roor_paths:
        ev.whitelist.append("ROOR 在册")


@dataclass
class _EvidenceInputs:
    """assemble_evidence 环境输入打包（NO-LONG-PARAM-LIST 治理件：11 参→2 参，行为零变化）。"""

    conn: Any
    repo_root: Path
    capability_paths: set[str]
    capability_ok: bool
    high_domains: set[str]
    high_ok: bool
    roor_paths: set[str]
    roor_ok: bool
    candidate_registry_path: Path
    extra_p0: list[str]


def assemble_evidence(entry: dict, inputs: _EvidenceInputs) -> Evidence:
    """四路证据装配（数据源环境经 _EvidenceInputs 打包注入）。"""
    mid = entry["module_id"]
    path = str(entry.get("path") or "")
    ev = Evidence()

    edge_map, ev.domains, depgraph_ok = fetch_depgraph_inedges(inputs.conn)
    ev.r_d = edge_map.get(mid, 0) if depgraph_ok else None
    ev.sources_ok["depgraph"] = depgraph_ok

    ev.p_d, ev.p_d_assets, lib_ok = fetch_library_consumers(inputs.conn, mid, path)
    ev.sources_ok["library"] = lib_ok

    ev.g_d = git_days_since_last_commit(inputs.repo_root, path)
    ev.sources_ok["git"] = ev.g_d is not None

    ev.c_d = _capability_signal(path, inputs.capability_paths, inputs.capability_ok)
    ev.sources_ok["capability"] = inputs.capability_ok

    ev.p0, ev.p0_sources = detect_p0(mid, path, inputs.repo_root, inputs.candidate_registry_path, inputs.extra_p0)
    _append_whitelist_reasons(
        ev,
        path,
        capability_ok=inputs.capability_ok,
        high_domains=inputs.high_domains,
        high_ok=inputs.high_ok,
        roor_paths=inputs.roor_paths,
        roor_ok=inputs.roor_ok,
    )
    return ev


# ---------- 报告 ----------


def _sorted_candidates(rows: list[Row]) -> list[Row]:
    """候选排序（score 降序、module_id 升序）。"""
    return sorted([r for r in rows if r.is_candidate], key=lambda r: (-r.score, r.module_id))


def _sorted_watchers(rows: list[Row]) -> list[Row]:
    """观察名单：未入候选、非 P0、score>=5，score 降序。"""
    return sorted(
        [r for r in rows if not r.is_candidate and not r.ev.p0 and r.score >= 5],
        key=lambda r: (-r.score, r.module_id),
    )


def _render_candidate_table(candidates: list[Row], top: int) -> list[str]:
    """Top 候选 markdown 表体（表头由 build_report 拼装）。"""
    lines: list[str] = []
    for i, r in enumerate(candidates[:top], 1):
        lines.append(
            f"| {i} | {r.module_id} | {r.score} | {r.ev.r_d} | {r.ev.g_d} | {r.ev.p_d} "
            f"| {r.ev.c_d} | {r.tier} | {r.path} |"
        )
    return lines


def _render_evidence_summary(candidates: list[Row], top: int) -> list[str]:
    """候选证据链摘要行。"""
    lines: list[str] = []
    for r in candidates[:top]:
        lib_part = r.ev.p_d if r.ev.p_d is not None else "NULL(未评估)"
        assets_part = f"（{','.join(r.ev.p_d_assets[:3])}）" if r.ev.p_d_assets else ""
        lines.append(
            f"- **{r.module_id}**：depgraph 入边={r.ev.r_d}；git 静止={r.ev.g_d} 天"
            f"（阈值 {STALE_DAYS}）；图书馆声明消费者={lib_part}"
            f"{assets_part}；"
            f"capability 命中={r.ev.c_d}；白名单=无"
        )
    return lines


def _render_p0_hints(p0_hints: list[Row]) -> list[str]:
    """P0 提示节（永不自动退役，仅提示 Owner）；无 P0 返回空。"""
    if not p0_hints:
        return []
    lines = ["", "## P0 提示（永不自动退役，仅提示 Owner）", ""]
    for r in p0_hints:
        lines.append(f"- {r.module_id}（score={r.score}）：{'; '.join(r.ev.whitelist) or 'P0'}")
    return lines


def _watcher_miss_reasons(r: Row) -> list[str]:
    """未入候选原因明细（观察名单单行）。"""
    miss = []
    if r.ev.r_d != 0:
        miss.append(f"R_d={r.ev.r_d}")
    if r.ev.g_d is None or r.ev.g_d < STALE_DAYS:
        miss.append(f"G_d={r.ev.g_d}")
    if r.ev.p_d not in (0, None):
        miss.append(f"P_d={r.ev.p_d}")
    if r.ev.c_d:
        miss.append("capability 命中")
    if r.ev.whitelist:
        miss.append("白名单:" + ";".join(r.ev.whitelist))
    if r.status != "active":
        miss.append(f"status={r.status}")
    return miss


def _render_watchers(watchers: list[Row], top: int) -> list[str]:
    """观察名单节（score>=5 未入候选）。"""
    lines = ["", "## 观察名单（score>=5 未入候选）", ""]
    for r in watchers[:top]:
        miss = _watcher_miss_reasons(r)
        lines.append(f"- {r.module_id}（score={r.score}）：未入候选原因= {'；'.join(miss) or '未知'}")
    return lines


def build_report(rows: list[Row], *, top: int = 10, generated_at: str | None = None) -> str:
    """markdown 报告：top 候选+P0 提示+证据链摘要。"""
    now = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    candidates = _sorted_candidates(rows)
    p0_hints = [r for r in rows if r.ev.p0]
    watchers = _sorted_watchers(rows)
    lines = [
        "# 退役候选探测报告（B10-P1 四路机械判定）",
        "",
        f"- 生成：{now}",
        "- 性质：只读情报，候选≠退役；任何状态变更须经 Owner 裁定（retire_module.py --owner-ruling）。",
        f"- 扫描条目：{len(rows)}；候选：{len(candidates)}；P0 提示（不入候选）：{len(p0_hints)}",
        "",
        f"## Top-{min(top, len(candidates))} 候选",
        "",
        "| # | module_id | score | R_d | G_d | P_d | C_d | 档位 | 路径 |",
        "|---|-----------|-------|-----|-----|-----|-----|------|------|",
    ]
    lines += _render_candidate_table(candidates, top)
    lines += ["", "## 证据链摘要", ""]
    lines += _render_evidence_summary(candidates, top)
    lines += _render_p0_hints(p0_hints)
    lines += _render_watchers(watchers, top)
    return "\n".join(lines) + "\n"


def staging_report_path(repo_root: Path, session: str, now: datetime | None = None) -> Path:
    """周报落点：.runtime/sessions/<sid>/staging/retirement_candidates/<date>.md。"""
    d = (now or datetime.now()).strftime("%Y%m%d")
    return repo_root / ".runtime" / "sessions" / session / "staging" / "retirement_candidates" / f"{d}.md"


# ---------- CLI ----------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="退役候选四路机械探测（MLC-003 前置情报；只读）")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="module_id_registry.yaml 路径")
    parser.add_argument("--capability-registry", default=str(DEFAULT_CAPABILITY_REGISTRY))
    parser.add_argument("--candidate-registry", default=str(DEFAULT_CANDIDATE_REGISTRY))
    parser.add_argument("--risk-tier-registry", default=str(DEFAULT_RISK_TIER_REGISTRY))
    parser.add_argument("--roor", default=str(DEFAULT_ROOR))
    parser.add_argument("--top", type=int, default=10, help="stdout 摘要条数")
    parser.add_argument("--output", default="", help="报告写盘路径（缺省零写盘）")
    parser.add_argument("--staging", action="store_true", help="报告写 .runtime/sessions/<sid>/staging/")
    parser.add_argument("--session", default="", help="会话 ID（--staging 落点必需）")
    parser.add_argument("--p0-extra", default="", help="额外 P0 module_id 逗号清单（Owner 口头补登通道）")
    args = parser.parse_args(argv)

    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = REPO_ROOT / registry_path
    if not registry_path.exists():
        print(f"ERROR: registry 不存在: {registry_path}", file=sys.stderr)
        return EXIT_ERROR

    entries = load_registry_modules(registry_path)
    if not entries:
        print("ERROR: registered_ids 为空", file=sys.stderr)
        return EXIT_ERROR

    conn = None
    try:
        from _shared.constants import get_depgraph_pg_connection  # noqa: PLC0415  惰性：PG 缺失不炸 CLI 参数面

        conn = get_depgraph_pg_connection(read_only=True)
    except Exception as exc:  # noqa: BLE001  保守降级：depgraph 不可用→该路按未知
        print(f"WARN: depgraph/lib 不可用，R_d/P_d 按未知处理（保守排除）: {exc}", file=sys.stderr)

    capability_paths, capability_ok = load_capability_canonical_paths(REPO_ROOT / args.capability_registry)
    high_domains, high_ok = load_risk_tier_high_domains(REPO_ROOT / args.risk_tier_registry)
    roor_paths, roor_ok = load_roor_paths(REPO_ROOT / args.roor)
    extra_p0 = [s.strip() for s in args.p0_extra.split(",") if s.strip()]

    rows: list[Row] = []
    inputs = _EvidenceInputs(
        conn=conn,
        repo_root=REPO_ROOT,
        capability_paths=capability_paths,
        capability_ok=capability_ok,
        high_domains=high_domains,
        high_ok=high_ok,
        roor_paths=roor_paths,
        roor_ok=roor_ok,
        candidate_registry_path=REPO_ROOT / args.candidate_registry,
        extra_p0=extra_p0,
    )
    for entry in entries:
        ev = assemble_evidence(entry, inputs)
        rows.append(evaluate_module(entry, ev))

    report = build_report(rows, top=args.top)
    candidates = [r for r in rows if r.is_candidate]
    print(
        f"[DETECT-RETIRE] scanned={len(rows)} candidates={len(candidates)} p0_hints={sum(1 for r in rows if r.ev.p0)}"
    )
    for r in sorted(candidates, key=lambda x: (-x.score, x.module_id))[: args.top]:
        print(
            f"  CANDIDATE {r.module_id} score={r.score} tier={r.tier} "
            f"R_d={r.ev.r_d} G_d={r.ev.g_d} P_d={r.ev.p_d} C_d={r.ev.c_d} path={r.path}"
        )

    out_path: Path | None = None
    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = REPO_ROOT / out_path
    elif args.staging:
        if not args.session:
            print("ERROR: --staging 需要 --session（.runtime/sessions/<sid>/staging/ 落点）", file=sys.stderr)
            return EXIT_ERROR
        out_path = staging_report_path(REPO_ROOT, args.session)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"[DETECT-RETIRE] report -> {out_path}")
    print(json.dumps({"scanned": len(rows), "candidates": len(candidates)}))
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
