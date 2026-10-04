#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-MCA-01 | docs/03_modules/_domain_governance/blueprint.md | §join_checker
# [MODULE] scripts.governance.d5_architecture.generators.generate_map_coverage_attribution
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.depgraph_schema; analyze_change_impact.ChangeImpactAnalyzer;
#   generate_governance_map._build_wiring_index/_wiring_tier; yaml
# [CONSUMERS] 覆盖账本 v2 验收闭环（裁定#481 分母）：六图覆盖率归属总表 30 号+孤儿簇报告 31 号；
#   align_all 后续新节（评估中，首跑 report-only）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 宇宙口径=裁定#481（主账 src/zephyr .py+scripts .py+frontend js/html，空壳 __init__ 并入
#   父包；辅账 tests/docs 记数不追责）；MOD-* 反查走 depgraph PG nodes 表，查无=dangling_keys
#   显式段禁静默丢弃，PG 不可达=报错退出禁 fail-open；闭包 BFS 复用
#   ChangeImpactAnalyzer._bfs_dependents 禁重写；孤儿判级复用 generate_governance_map._wiring_tier
#   四档禁另造；多图挂载合法（maps_direct 列全量）；机生禁手填
# [MODIFY-GUARD] 六图 YAML 键形变更（module_id/module_ref/source_anchors/families/mounts）须同步本文件
#   提取器；输出 schema 变更须过红蓝三攻击样例
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit (PG unreachable / universe empty)
# [TESTS] tests/governance/generators/test_map_coverage_attribution.py
# [A_module] module_id=MOD-GOV-MCA-01 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本生成器为按需调用的 permanent runner（join checker 首跑/重跑与 align_all 接入后事件调用），非 cron/daemon/常驻服务，manual CLI 即其真实形态
"""覆盖账本 v2·join checker（裁定#481 分母的执行件）——六图挂载×依赖闭包→全模块归属总表。

照稿施工依据：docs/_working/map_build/20_join_checker_design.md（rev2，禁改设计）。
三段 join（§2）：①键归一（zephyr dotted / src 路径 / MOD-* 三形态→file_path，MOD-* 经 depgraph
PG 反查，查无=dangling 禁静默）②归属判定（直接挂载→direct；依赖闭包达挂载件→derived；
两不沾→孤儿，判级复用 GOMAP 四档）③多图归一（一文件多图合法，列全量）。
输出（§3）：accounting_units_total/by_map/closure_derived/dangling_keys/auxiliary_ledger/
orphans/units 全量明细，机生禁手填，幂等可重跑。
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import yaml

_REPO = Path(__file__).resolve().parents[4]
for _p in (
    str(_REPO),
    str(_REPO / "scripts" / "governance"),
    str(_REPO / "scripts" / "governance" / "d5_architecture"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402  trae_067 CREATE_NO_WINDOW 统一入口
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402  生成器禁 datetime.now 任何形式，统一走 time_utils 单点

_MAP_IDS = ("GOMAP", "TDM", "FACTORY", "FIG11", "FIG12", "FIG13")
_MAP_FILES = {
    "GOMAP": "config/governance_operations_map.yaml",
    "TDM": "config/trading_decision_map.yaml",
    "FACTORY": "config/strategy_production_map.yaml",
    "FIG11": "config/dev_delivery_map.yaml",
    "FIG12": "config/data_supply_chain_map.yaml",
    "FIG13": "config/trading_day_cycle_map.yaml",
}
_MOD_RE = re.compile(r"^MOD-[A-Za-z0-9_-]+$")
_SQL_NODES_BLUEPRINT = "SELECT path, blueprint_id FROM nodes WHERE blueprint_id IS NOT NULL"
_SQL_EDGES = "SELECT from_node_id, to_node_id FROM edges"
_UNIVERSE_EXPECTED = 5200  # 裁定#481 预估口径（对拍用，非判据）


@dataclass
class DepgraphView:
    """依赖闭包+MOD 反查的可注入视图（测试用；生产路径走 PG 自加载）。"""

    mod_to_paths: dict[str, list[str]] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)  # (from_path, to_path) = from imports to


# ---------------------------------------------------------------- universe


def _is_empty_init(path: Path) -> bool:
    """空壳判据：模块体仅 docstring/Pass（注释天然不进 AST）。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError, RecursionError):
        return False
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if isinstance(node, ast.Pass):
            continue
        return False
    return True


def _dotted_of(rel: str) -> str | None:
    """仓内相对路径→点分模块名（非 .py 返回 None）。"""
    p = Path(rel)
    if p.suffix != ".py":
        return None
    parts = list(p.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if parts[:2] == ["src", "zephyr"]:
        parts = ["zephyr"] + parts[2:]
    return ".".join(parts) if parts else None


def build_universe(repo_root: Path) -> dict:
    """裁定#481 宇宙清点：主账单元+辅账计数。空壳 __init__ 并入父包（不设单元）。"""
    src = repo_root / "src" / "zephyr"
    scripts = repo_root / "scripts"
    frontend = repo_root / "src" / "zephyr" / "frontend"
    units: list[str] = []
    merged_empty_init = 0
    for base in (src, scripts):
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*.py")):
            rel = f.relative_to(repo_root).as_posix()
            if base == src and f.name == "__init__.py" and _is_empty_init(f):
                merged_empty_init += 1
                continue
            units.append(rel)
    frontend_files: list[str] = []
    if frontend.is_dir():
        for pat in ("*.js", "*.html"):
            frontend_files.extend(f.relative_to(repo_root).as_posix() for f in sorted(frontend.rglob(pat)))
    units.extend(frontend_files)
    tests_py = sum(1 for _ in (repo_root / "tests").rglob("*.py")) if (repo_root / "tests").is_dir() else 0
    docs_files = sum(1 for _ in (repo_root / "docs").rglob("*")) if (repo_root / "docs").is_dir() else 0
    return {
        "units": sorted(set(units)),
        "frontend_files": frontend_files,
        "aux": {"tests_py_count": tests_py, "docs_file_count": docs_files, "merged_empty_init": merged_empty_init},
    }


# ---------------------------------------------------------------- key normalization


def _anchor_strip(anchor: str) -> str:
    """source_anchors 形态 path[:line] → path（尾段纯数字才剥，防误伤 Windows 盘符）。"""
    a = anchor.strip()
    m = re.match(r"^(.*?):(\d+)$", a)
    return m.group(1) if m else a


class KeyNormalizer:
    """三形态挂载键 → 仓内 file_path（MOD-* 经基表反查，查无=悬空）。"""

    def __init__(self, universe: set[str], mod_to_paths: dict[str, list[str]]):
        """__init__ implementation."""
        self.universe = universe
        self.mod_to_paths = mod_to_paths
        self._path_index = {p: True for p in universe}

    def resolve(self, raw: str) -> tuple[list[str], str | None]:
        """→(命中路径列表, dangling MOD 号或 None)。路径键查无=静默无贡献（§4 仅 MOD-* 判悬空）。"""
        key = raw.strip()
        if not key or " " in key or key.startswith(("docs/", ".runtime", "http")):
            return [], None
        if _MOD_RE.match(key):
            paths = [p for p in self.mod_to_paths.get(key, []) if p in self._path_index]
            if self.mod_to_paths.get(key):
                return paths, None  # 反查有案（可能全在图外=非悬空，仅无贡献）
            return [], key  # 查无=悬空
        if "/" in key or "\\" in key or key.endswith((".py", ".js", ".html")):
            cands = self._path_candidates(_anchor_strip(key).replace("\\", "/"))
            return [c for c in cands if c in self._path_index], None
        return self._dotted_candidates(key), None

    def _path_candidates(self, p: str) -> list[str]:
        """_path_candidates implementation."""
        p = p.strip("/")
        out = [p, p + ".py", p + "/__init__.py"]
        return out

    def _dotted_candidates(self, dotted: str) -> list[str]:
        """_dotted_candidates implementation."""
        parts = dotted.split(".")
        cands: list[str] = []
        if parts[0] == "zephyr":
            base = ["src"] + parts
        elif parts[0] == "scripts":
            base = parts
        else:
            base = ["src"] + parts
        cands.append("/".join(base) + ".py")
        cands.append("/".join(base + ["__init__.py"]))
        return [c for c in cands if c in self._path_index]


# ---------------------------------------------------------------- map mount extraction


def extract_mount_keys(map_id: str, data: dict) -> Iterable[str]:
    """六图挂载键提取（键形照设计稿 §1 实证表，横轴图不入）。"""
    if map_id == "GOMAP":
        for fam in (data.get("families") or {}).values():
            for m in fam or []:
                if isinstance(m, dict):
                    if m.get("path"):
                        yield m["path"]
                    if m.get("module"):
                        yield m["module"]
        for layer in (data.get("pipeline") or {}).get("layers") or []:
            yield from layer.get("mounts") or []
        return
    for n in data.get("nodes") or []:
        if not isinstance(n, dict):
            continue
        if map_id == "TDM":
            if n.get("module_ref"):
                yield n["module_ref"]  # 单键可空=缺口节点不计
        elif map_id == "FACTORY":
            # 盘面实证：图9 的 MOD-* 值装在 module_ref 字段（16 主链+323 机制节点，无 module_id 字段）
            if n.get("module_ref"):
                yield n["module_ref"]
        else:  # FIG11/FIG12/FIG13 双键
            if n.get("module_id"):
                yield n["module_id"]
            if n.get("module_ref"):
                yield n["module_ref"]
            yield from n.get("source_anchors") or []


# ---------------------------------------------------------------- depgraph sources


def build_depgraph_view_from_pg() -> DepgraphView:
    """生产路径：PG 直查 nodes(blueprint_id→path 反查基表)+edges。不可达=fail-loud。"""
    try:
        conn = get_depgraph_pg_connection()
    except Exception as exc:  # noqa: BLE001  PG 错误族过广——统一转 fail-loud
        raise RuntimeError(f"depgraph PG 连接失败（禁 fail-open）: {exc}") from exc
    try:
        cur = conn.cursor()
        cur.execute(_SQL_NODES_BLUEPRINT)
        mod_to_paths: dict[str, list[str]] = defaultdict(list)
        path_by_node: dict[str, str] = {}
        node_by_path: dict[str, str] = {}
        for i, (path, bp) in enumerate(cur.fetchall()):
            if path:
                path_by_node[str(i)] = path
                node_by_path[path] = str(i)
                if bp:
                    mod_to_paths[str(bp)].append(path)
        cur.execute(_SQL_EDGES)
        edges: list[tuple[str, str]] = []
        for a, b in cur.fetchall():
            pa, pb = path_by_node.get(str(a)), path_by_node.get(str(b))
            if pa and pb:
                edges.append((pa, pb))
        return DepgraphView(mod_to_paths=dict(mod_to_paths), edges=edges)
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001  close 防御性吞（不得掩主错误）
            pass


def _make_analyzer(repo_root: Path, view: DepgraphView | None):
    """闭包引擎：复用 ChangeImpactAnalyzer（禁重写 BFS）。override 注入或 PG 自加载。"""
    from analyze_change_impact import ChangeImpactAnalyzer

    analyzer = ChangeImpactAnalyzer(str(repo_root))
    if view is None:
        try:
            analyzer._load_depgraph()
        except Exception as exc:  # noqa: BLE001  PG 错误族过广——统一转 fail-loud
            raise RuntimeError(f"depgraph PG 加载失败（禁 fail-open）: {exc}") from exc
        return analyzer
    nodes = {str(i): {"path": p} for i, p in enumerate(sorted({p for e in view.edges for p in e}))}
    idx = {p: nid for nid, meta in nodes.items() for p in [meta["path"]]}
    analyzer._depgraph = {
        "nodes": nodes,
        "edges": [{"from": idx[a], "to": idx[b]} for a, b in view.edges if a in idx and b in idx],
    }
    analyzer._build_adjacency()
    analyzer._loaded = True
    return analyzer


# ---------------------------------------------------------------- orphan tiering (reuse GOMAP)


def _consumers_header_nonempty(path: Path) -> bool:
    """_consumers_header_nonempty implementation."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return False
    m = re.search(r"#\s*\[CONSUMERS\]\s*(.*)", text)
    if not m:
        return False
    if m.group(1).strip():
        return True
    for line in text[m.end() :].splitlines():
        if not line.startswith("#"):
            break
        cont = line[1:].strip()
        if not cont:
            continue
        if re.match(r"^\[\w[\w-]*\]", cont):
            break
        return True
    return False


def _tier_orphans(
    orphan_units: list[dict], repo_root: Path, all_py_units: list[str], frontend_refs: set[str]
) -> dict[str, tuple[str, int]]:
    """判级复用 generate_governance_map._wiring_tier 四档（import 复用禁另造）。
    索引必须扫全宇宙 .py（只扫孤儿=互相引用才见）；js/html 走 frontend_map 引用面
    （辅助 join）：被引用=wired_by_header，否则 suspect_orphan。返回 file→(tier, imports_in)。"""
    from generate_governance_map import _build_wiring_index, _wiring_tier  # noqa: import-integrity  sys.path 动态加载

    wiring_keys = {d for d in (_dotted_of(u) for u in all_py_units) if d}
    idx = (
        _build_wiring_index([repo_root / u for u in all_py_units], wiring_keys)
        if wiring_keys
        else {"static": {}, "bare": {}, "strspec": {}, "dispatch": set()}
    )
    out: dict[str, tuple[str, int]] = {}
    for u in orphan_units:
        rel = u["file"]
        if rel.endswith(".py"):
            c = {
                "_key": u.get("_dotted") or "",
                "path": rel,
                "_spec": rel.replace("/", ".")[:-3],
                "_consumers_header": _consumers_header_nonempty(repo_root / rel),
            }
            importers, _dynamic = _wiring_evidence_safe(c, idx)
            out[rel] = (_wiring_tier(c, idx), len(importers))
        else:  # js/html
            out[rel] = ("wired_by_header" if rel in frontend_refs else "suspect_orphan", 0)
    return out


def _wiring_evidence_safe(c: dict, idx: dict) -> tuple[set[str], set[str]]:
    """generate_governance_map._wiring_evidence 的同源复用（模块级 import 懒加载）。"""
    from generate_governance_map import _wiring_evidence  # noqa: import-integrity  sys.path 动态加载

    return _wiring_evidence(c, idx)


def _frontend_referenced(frontend_map: Path | None) -> set[str]:
    """frontend_map.yaml（辅助 join）提到的前端文件路径集。"""
    if not frontend_map or not Path(frontend_map).exists():
        return set()
    try:
        data = yaml.safe_load(Path(frontend_map).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return set()
    refs: set[str] = set()
    for f in data.get("features") or []:
        if isinstance(f, dict):
            for k in ("file", "backend_ref", "files"):
                v = f.get(k)
                if isinstance(v, str) and ("/" in v or v.endswith((".js", ".html", ".py"))):
                    refs.add(v.split(":")[-1].strip())
            for v in f.get("files") or []:
                if isinstance(v, str):
                    refs.add(v)
    return refs


def _git_last_commit_default(repo_root: Path, rel: str) -> str:
    """_git_last_commit_default implementation."""
    try:
        out = run_subprocess_hidden(
            ["git", "log", "-1", "--format=%as", "--", rel],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (out.stdout or "").strip() or "untracked"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


# ---------------------------------------------------------------- main engine


def run_attribution(
    repo_root: Path | str,
    *,
    map_files: dict[str, Path] | None = None,
    depgraph_override: DepgraphView | None = None,
    script_manifest: Path | None = None,
    frontend_map: Path | None = None,
    output_yaml: Path | str | None = None,
    output_md: Path | str | None = None,
    git_last_commit: Callable[[Path, str], str] | None = None,
) -> dict:
    """归属总表主引擎（幂等可重跑；返回报告 dict 并落 30/31 两件）。"""
    repo_root = Path(repo_root).resolve()
    map_files = map_files or {k: repo_root / v for k, v in _MAP_FILES.items()}
    git_cb = git_last_commit or (lambda root, rel: _git_last_commit_default(root, rel))

    # ① 宇宙（裁定#481）
    uni = build_universe(repo_root)
    universe = set(uni["units"])
    if not universe:
        raise SystemExit("宇宙清点为空——检查 repo_root（fail-loud，禁空跑）")

    # ② MOD 反查基表 + 闭包引擎（PG 不可达=显式退出，禁 fail-open）
    try:
        if depgraph_override is not None:
            view = depgraph_override
        else:
            view = build_depgraph_view_from_pg()
        analyzer = _make_analyzer(repo_root, depgraph_override)
    except RuntimeError as exc:
        raise SystemExit(f"[join-checker] {exc}") from exc
    normalizer = KeyNormalizer(universe, view.mod_to_paths)

    # ③ 六图挂载键归一（三形态→file_path；悬空显式报）
    mounted: dict[str, set[str]] = defaultdict(set)
    dangling: list[dict] = []
    out_of_universe = 0
    for mid in _MAP_IDS:
        mf = map_files.get(mid)
        data = {}
        if mf and Path(mf).exists():
            try:
                data = yaml.safe_load(Path(mf).read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                raise SystemExit(f"[join-checker] 图 YAML 损坏 {mid}: {mf}（fail-closed）: {exc}") from exc
        else:
            continue
        for raw in extract_mount_keys(mid, data):
            paths, dang = normalizer.resolve(raw)
            if dang:
                dangling.append({"key": dang, "source_map": mid})
            for p in paths:
                if p in universe:
                    mounted[p].add(mid)
                else:
                    out_of_universe += 1

    # ④ 闭包归属（复用 analyzer 反向 BFS；按图独立多源 BFS——共享 visited 会吞跨图标签）
    derived: dict[str, set[str]] = defaultdict(set)
    path_to_node = getattr(analyzer, "_path_to_node", {})
    node_to_path = getattr(analyzer, "_node_to_path", {})
    mounted_by_map: dict[str, set[str]] = defaultdict(set)
    for p, mids in mounted.items():
        for mid in mids:
            mounted_by_map[mid].add(p)
    all_mounted_nids = {path_to_node[p] for p in mounted if p in path_to_node}
    not_in_depgraph = sum(1 for p in mounted if p not in path_to_node)
    for mid in _MAP_IDS:
        visited: set[str] = set(all_mounted_nids)
        for mpath in sorted(mounted_by_map.get(mid, ())):
            nid = path_to_node.get(mpath)
            if nid is None:
                continue
            for dep_nid in analyzer._bfs_dependents(nid, visited):
                visited.add(dep_nid)
                dep_path = node_to_path.get(dep_nid)
                if dep_path in universe:
                    derived[dep_path].add(mid)

    # ⑤ 逐单元定态（direct > derived > orphan；多图归一）
    units: list[dict] = []
    orphans: list[dict] = []
    for rel in uni["units"]:
        md = sorted(mounted.get(rel, set()))
        mv = sorted(set(derived.get(rel, set())) - set(md))
        status = "direct" if md else ("derived" if mv else "orphan")
        row = {"file": rel, "maps_direct": md, "maps_derived": mv, "status": status, "_dotted": _dotted_of(rel)}
        units.append(row)
        if status == "orphan":
            orphans.append(row)

    # ⑥ 孤儿判级（复用 GOMAP 四档，索引扫全宇宙）+ 证据
    frontend_refs = _frontend_referenced(
        frontend_map or repo_root / "src/zephyr/frontend/dashboard/web/frontend_map.yaml"
    )
    all_py_units = [u["file"] for u in units if u["file"].endswith(".py")]
    tiers = _tier_orphans(orphans, repo_root, all_py_units, frontend_refs)
    rev_deg: dict[str, int] = defaultdict(int)
    for a, b in view.edges:
        rev_deg[b] += 1
    orphan_rows = []
    for u in orphans:
        rel = u["file"]
        parts = Path(rel).parts
        cluster = ".".join(parts[:3]) if parts[0] == "src" else ".".join(parts[:2])
        tier, imports_in = tiers.get(rel, ("suspect_orphan", 0))
        orphan_rows.append(
            {
                "file": rel,
                "cluster_hint": cluster,
                "tier": tier,
                "evidence": {
                    "imports_in": imports_in,
                    "imported_by": rev_deg.get(rel, 0),
                    "last_commit": git_cb(repo_root, rel),
                },
            }
        )

    # ⑦ 汇总（schema §3 顺序）
    by_map = {mid: sum(1 for u in units if mid in u["maps_direct"]) for mid in _MAP_IDS}
    derived_by_map = {mid: sum(1 for u in units if mid in u["maps_derived"]) for mid in _MAP_IDS}
    manifest_total = None
    if script_manifest and Path(script_manifest).exists():
        try:
            mdata = yaml.safe_load(Path(script_manifest).read_text(encoding="utf-8")) or {}
            manifest_total = mdata.get("total_scripts")
        except (OSError, yaml.YAMLError):
            manifest_total = None
    total = len(units)
    report = {
        "accounting_units_total": total,
        "by_map": by_map,
        "closure_derived": sum(1 for u in units if u["status"] == "derived"),
        "dangling_keys": dangling,
        "auxiliary_ledger": {
            **uni["aux"],
            "frontend_file_count": len(uni["frontend_files"]),
            "scripts_manifest_total": manifest_total,
        },
        "orphans": orphan_rows,
        "units": [{k: u[k] for k in ("file", "maps_direct", "maps_derived", "status")} for u in units],
        "meta": {
            "generated_at": now_utc().isoformat(timespec="seconds"),
            "ruling": "裁定#481（主账=src/zephyr .py+scripts .py+frontend js/html≈5200；辅账 tests/docs）",
            "design_spec": "docs/_working/map_build/20_join_checker_design.md rev2",
            "map_sources": {k: str(v) for k, v in map_files.items()},
            "closure_engine": "analyze_change_impact.ChangeImpactAnalyzer（复用 _bfs_dependents，禁重写）",
            "tier_engine": "generate_governance_map._wiring_tier（四档复用，禁另造）",
            "counts_diag": {
                "mounted_files": len(mounted),
                "mounted_not_in_depgraph": not_in_depgraph,
                "keys_out_of_universe": out_of_universe,
                "derived_by_map": derived_by_map,
                "orphan_count": len(orphan_rows),
            },
            "crosscheck_ruling481": {
                "expected_approx": _UNIVERSE_EXPECTED,
                "actual": total,
                "deviation_pct": round((total - _UNIVERSE_EXPECTED) / _UNIVERSE_EXPECTED * 100, 1),
            },
        },
    }

    if output_yaml:
        Path(output_yaml).parent.mkdir(parents=True, exist_ok=True)
        Path(output_yaml).write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8"
        )
    if output_md:
        _write_md(report, Path(output_md), repo_root, frontend_refs)
    return report


# ---------------------------------------------------------------- 31 号报告


def _write_md(report: dict, out_md: Path, repo_root: Path, frontend_refs: set[str]) -> None:
    """_write_md implementation."""
    total = report["accounting_units_total"]
    by_map = report["by_map"]
    dmap = report["meta"]["counts_diag"]["derived_by_map"]
    clusters: dict[str, list[dict]] = defaultdict(list)
    for o in report["orphans"]:
        clusters[o["cluster_hint"]].append(o)
    lines: list[str] = []
    ap = lines.append
    ap("---")
    ap("ttl: task_bound")
    ap("completes_when: 覆盖账本 v2 验收闭环（孤儿清零/入图判罚完）后本报告随 30 号转归档")
    ap("title: 孤儿簇报告与六图覆盖率（join checker 首跑，机生禁手改）")
    ap("owner: st-joinchk-20261004")
    ap("---")
    ap("")
    ap("# 孤儿簇报告（31 号·机生）")
    ap("")
    xc = report["meta"]["crosscheck_ruling481"]
    ap(
        f"> 宇宙={total}（裁定#481 预估≈{xc['expected_approx']}，偏差 {xc['deviation_pct']:+.1f}%）；"
        f"直接挂载 {sum(by_map.values())}；闭包归属 {report['closure_derived']}；"
        f"孤儿 {len(report['orphans'])}（簇 {len(clusters)}）；悬空键 {len(report['dangling_keys'])}。"
    )
    ap("")
    ap("## 六图覆盖率一栏表")
    ap("")
    ap("| 行 | GOMAP | TDM | FACTORY | FIG11 | FIG12 | FIG13 |")
    ap("|---|---|---|---|---|---|---|")
    ap("| direct（直接挂载） | " + " | ".join(str(by_map[m]) for m in _MAP_IDS) + " |")
    ap("| closure（闭包归属） | " + " | ".join(str(dmap[m]) for m in _MAP_IDS) + " |")
    cov = [f"{(by_map[m] + dmap[m]) / total * 100:.1f}%" if total else "-" for m in _MAP_IDS]
    ap("| 覆盖率%（direct+closure）/宇宙 | " + " | ".join(cov) + " |")
    ap("")
    ap("> 孤儿为全集判（六图两不沾），跨图共享一份清单；上表第三行按 (direct+closure)/宇宙 计单图覆盖。")
    ap("")
    ap("## 孤儿簇（按顶级包聚簇，判级四档）")
    ap("")
    for cname in sorted(clusters, key=lambda c: -len(clusters[c])):
        members = clusters[cname]
        tiers = {}
        for o in members:
            tiers[o["tier"]] = tiers.get(o["tier"], 0) + 1
        ap(f"### {cname}（{len(members)} 台：" + "，".join(f"{k}={v}" for k, v in sorted(tiers.items())) + "）")
        for o in members[:3]:
            ev = o["evidence"]
            ap(f"- `{o['file']}`（{o['tier']}，imported_by={ev['imported_by']}，last_commit={ev['last_commit']}）")
        if len(members) > 3:
            ap(f"- …其余 {len(members) - 3} 台见 30 号 units 段")
        ap("")
    if report["dangling_keys"]:
        ap("## 悬空键（MOD-* 反查查无，禁静默——逐条判罚或修键）")
        ap("")
        for d in report["dangling_keys"][:20]:
            ap(f"- `{d['key']}`（{d['source_map']}）")
        if len(report["dangling_keys"]) > 20:
            ap(f"- …其余 {len(report['dangling_keys']) - 20} 条见 30 号 dangling_keys 段")
        ap("")
    ap("## align_all 第十节接入方案（评估·只评估不施工）")
    ap("")
    ap(
        "1. 调用点：align_all.py 现有第十节（图12 数据供给链）之后新增一节，"
        "单行复用本生成器 run_attribution()（同仓同真源，读六图 YAML+depgraph PG，产出即本 30 号 schema）。"
    )
    ap(
        "2. 阈值参数化建议：首跑 report-only——新增 `--orphan-threshold`（默认 None=只报数字不判硬），"
        "Owner 看完首跑基线后随孤儿填充班递降（如 500→100→0），到 0 时改 exit>0 硬门。"
    )
    ap(
        "3. exit 语义：report-only 阶段恒 exit 0（数字进总览报告）；翻硬后 orphans>threshold 即 exit 1，"
        "与现行 align_all「硬>0=exit 1」同口径，悬空键恒硬报（禁静默）。"
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="覆盖账本 v2·join checker（裁定#481 归属总表生成器）")
    ap.add_argument("--repo-root", default=str(_REPO))
    ap.add_argument("--out-yaml", default=str(_REPO / "docs/_working/map_build/30_attribution_table.yaml"))
    ap.add_argument("--out-md", default=str(_REPO / "docs/_working/map_build/31_orphan_clusters.md"))
    ap.add_argument("--script-manifest", default=str(_REPO / "scripts/script-manifest.yaml"))
    ap.add_argument("--frontend-map", default=str(_REPO / "src/zephyr/frontend/dashboard/web/frontend_map.yaml"))
    ns = ap.parse_args(argv)
    report = run_attribution(
        ns.repo_root,
        script_manifest=Path(ns.script_manifest),
        frontend_map=Path(ns.frontend_map),
        output_yaml=ns.out_yaml,
        output_md=ns.out_md,
    )
    print(
        f"[join-checker] units={report['accounting_units_total']}"
        f" direct={sum(report['by_map'].values())} derived={report['closure_derived']}"
        f" orphans={len(report['orphans'])} dangling={len(report['dangling_keys'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
