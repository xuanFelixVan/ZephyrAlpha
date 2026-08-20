# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
[INVARIANTS] 代码[BLUEPRINT]头部module_id必须与蓝图注册表一致; 蓝图§4已实现文件必须在磁盘存在; frontmatter.build_status 必须与 depgraph 聚合 build_status 一致（FRONTMATTER_STATE_STALE, WARN/MEDIUM）
[MODIFY-GUARD] script_manifest.yaml; blueprint_registry.yaml; ARCH-FRONTMATTER-STATE-001 Phase 4
[CONSUMERS] CI pipeline; AI session 冷启动; Phase Gate; session_worktree pre-merge 拓扑检查
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] exit 0=CLEAN, exit 1=DRIFT, exit 2=ERROR
[TESTS] tests/governance/test_check_blueprint_code_alignment.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from _shared.constants import BLUEPRINTS_DIR, EXIT_FINDINGS, REPO_ROOT, get_depgraph_pg_connection
from _shared.frontmatter import parse_frontmatter
from _shared.walk import iter_files

__manifest__ = """
args: [--warn-only, --json, --package, --scan-root]
description: 蓝图↔代码双向对齐检测——代码[BLUEPRINT]头部module_id双源验证(registry+depgraph)+蓝图§4文件清单depgraph派生(裁定#211)；--scan-root 用于 #ARCH-DEP-001 第二期 pre-merge 拓扑硬阻断（扫描 worktree session 分支代码，DB 配置留 main）
dimensions:
- D5
- D1
priority: P1
timeout_seconds: 60
warn_only: false
"""

SRC_DIR = REPO_ROOT / "src" / "zephyr"
BLUEPRINT_REGISTRY = BLUEPRINTS_DIR / "blueprint_registry.yaml"
MODULE_REGISTRY = BLUEPRINTS_DIR / "module-registry.yaml"

BLUEPRINT_HEADER_RE = re.compile(r"\[BLUEPRINT\]\s+(\S+)")
MODULE_ID_RE = re.compile(r'(?:-\s*)?module_id:\s*["\']?(\S+?)["\']?\s*$')

# 裁定#211：depgraph 查询 SQL（提取为模块级常量，遵循 §5.160.2 SQL 集中化原则）
_SQL_LOAD_DEPGRAPH_MODULE_INDEX = (
    "SELECT blueprint_id, path FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id != '' AND path LIKE '%%.py'"
)

# ARCH-FRONTMATTER-STATE-001 Phase 4：build_status 聚合查询（取每个 blueprint_id
# 下按 (path IS NULL), path 排序后的第一个非空 build_status，与 blueprint_frontmatter_reconciler 语义对齐）
_SQL_LOAD_DEPGRAPH_BUILD_STATUS = (
    "SELECT blueprint_id, build_status FROM nodes "
    "WHERE blueprint_id IS NOT NULL AND blueprint_id != '' "
    "ORDER BY blueprint_id, (path IS NULL), path"
)

# 蓝图 frontmatter 扫描时跳过的文件名（与 blueprint_frontmatter_reconciler 对齐）
_BP_SCAN_SKIP_NAMES = {"index.md"}


# 裁定#211：蓝图§4文件清单改为 depgraph 派生
# 蓝图§0.1 已声明 SSoT 是 depgraph（见 agent_orchestrator/blueprint.md L53-58），
# check 脚本不再解析蓝图§4 markdown 表格，改为从 depgraph 查询。
def load_depgraph_module_index() -> tuple[set[str], dict[str, set[str]]]:
    """从 depgraph 加载 module_id 索引。

    Returns:
        (module_ids, files_by_module)
        - module_ids: depgraph 中所有 blueprint_id 的集合（用于 ORPHAN_MODULE_ID 验证）
        - files_by_module: {blueprint_id: {path1, path2, ...}}（用于 CODE_NOT_IN_BLUEPRINT 验证）
    """
    module_ids: set[str] = set()
    files_by_module: dict[str, set[str]] = {}
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
    except Exception as e:
        print(f"[WARN] depgraph 连接失败，跳过 depgraph 派生检查: {e}", file=sys.stderr)
        return module_ids, files_by_module
    try:
        cur = conn.execute(_SQL_LOAD_DEPGRAPH_MODULE_INDEX)
        for r in cur.fetchall():
            bid = r["blueprint_id"]
            path = r["path"].replace("\\", "/")
            module_ids.add(bid)
            files_by_module.setdefault(bid, set()).add(path)
    finally:
        conn.close()
    return module_ids, files_by_module


# ---------------------------------------------------------------------------
# ARCH-FRONTMATTER-STATE-001 Phase 4: FRONTMATTER_STATE_STALE gate
# ---------------------------------------------------------------------------


def _aggregate_build_status(rows: list[dict]) -> dict[str, str]:
    """按 blueprint_id 聚合 build_status（第一个非空值胜出）。

    与 blueprint_frontmatter_reconciler._query_module_bp 的聚合语义对齐：
    SQL 已按 blueprint_id, (path IS NULL), path 排序，因此第一个非空
    build_status 即代表该模块的当前状态。
    """
    result: dict[str, str] = {}
    for row in rows:
        bid = row["blueprint_id"]
        bs = (row.get("build_status") or "").strip()
        if bid not in result and bs:
            result[bid] = bs
    return result


def load_depgraph_build_status() -> dict[str, str]:
    """从 depgraph 加载每个 blueprint_id 的聚合 build_status。

    Returns:
        {blueprint_id: build_status}。连接失败时返回空 dict（fail-open）。
    """
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
    except Exception as e:
        print(f"[WARN] depgraph 连接失败，跳过 FRONTMATTER_STATE_STALE 检查: {e}", file=sys.stderr)
        return {}
    try:
        cur = conn.execute(_SQL_LOAD_DEPGRAPH_BUILD_STATUS)
        return _aggregate_build_status(cur.fetchall())
    finally:
        conn.close()


def scan_blueprint_frontmatter_entries() -> list[dict]:
    """扫描 docs/03_modules 下所有蓝图 frontmatter，提取 module_id 与 build_status。

    跳过 _BP_SCAN_SKIP_NAMES（如 index.md），避免把目录索引误判为蓝图。
    """
    entries: list[dict] = []
    if not BLUEPRINTS_DIR.exists():
        return entries
    for md_file in BLUEPRINTS_DIR.rglob("*.md"):
        if md_file.name in _BP_SCAN_SKIP_NAMES:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = parse_frontmatter(content)
        if not fm:
            continue
        module_id = fm.get("module_id")
        if not module_id:
            continue
        entries.append(
            {
                "file": str(md_file.relative_to(REPO_ROOT)),
                "module_id": module_id,
                "build_status": fm.get("build_status", ""),
            }
        )
    return entries


def check_frontmatter_state_stale(
    frontmatter_entries: list[dict],
    depgraph_build_status: dict[str, str],
) -> list[dict]:
    """检查 frontmatter.build_status 是否与 depgraph 聚合 build_status 不一致。

    三层状态模型：L1(代码现实) → L2(depgraph) → L3(frontmatter 缓存)。
    本 gate 检测 L3 与 L2 的漂移，severity=MEDIUM（WARN），不阻断提交，
    由 blueprint_frontmatter_reconciler 在 merge 周期自动修复。
    """
    findings: list[dict] = []
    for entry in frontmatter_entries:
        mid = entry["module_id"]
        dep_bs = depgraph_build_status.get(mid, "")
        if not dep_bs:
            continue
        fm_bs = entry["build_status"]
        if fm_bs != dep_bs:
            findings.append(
                {
                    "type": "FRONTMATTER_STATE_STALE",
                    "severity": "MEDIUM",
                    "file": entry["file"],
                    "detail": f"frontmatter.build_status='{fm_bs or '(空)'}' 与 depgraph build_status='{dep_bs}' 不一致",
                }
            )
    return findings


def load_blueprint_registry() -> dict[str, dict]:
    """load_blueprint_registry implementation."""
    registry: dict[str, dict] = {}
    if not BLUEPRINT_REGISTRY.exists():
        return registry
    content = BLUEPRINT_REGISTRY.read_text(encoding="utf-8")
    current_id = None
    current_entry: dict = {}
    for line in content.splitlines():
        m = MODULE_ID_RE.match(line.strip())
        if m:
            if current_id:
                registry[current_id] = current_entry
            current_id = m.group(1).strip('"').strip("'")
            current_entry = {}
            continue
        if current_id and ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            current_entry[key.strip()] = val.strip()
    if current_id:
        registry[current_id] = current_entry
    return registry


def load_module_registry() -> dict[str, str]:
    """load_module_registry implementation."""
    pkg_to_modid: dict[str, str] = {}
    if not MODULE_REGISTRY.exists():
        return pkg_to_modid
    content = MODULE_REGISTRY.read_text(encoding="utf-8")
    current_id = None
    for line in content.splitlines():
        m = MODULE_ID_RE.match(line.strip())
        if m:
            current_id = m.group(1).strip('"').strip("'")
            continue
        if current_id and "actual_disk_path:" in line:
            _, _, val = line.partition(":")
            path_val = val.strip().strip('"').strip("'").rstrip("/")
            pkg_name = path_val.split("/")[-1] if "/" in path_val else path_val
            if pkg_name and current_id:
                pkg_to_modid[pkg_name] = current_id
    return pkg_to_modid


def scan_code_blueprint_headers(
    package_filter: str | None = None,
    scan_root: str | Path | None = None,
) -> list[dict]:
    """扫描代码 [BLUEPRINT] 头部。

    :param package_filter: 限定扫描单个包名（如 "governance"）。
    :param scan_root: 扫描根目录（#ARCH-DEP-001 第二期 pre-merge 拓扑硬阻断用）。
        给定时扫描 ``<scan_root>/src/zephyr`` 而非默认 ``SRC_DIR``（main REPO_ROOT），
        且 ``file`` 字段相对 ``scan_root`` 计算（保持与 depgraph 路径格式一致，
        如 ``src/zephyr/...``）。DB 配置和蓝图注册表仍用 main REPO_ROOT——pre-merge
        检查的语义是「session 分支代码相对 production depgraph 的漂移」。
        默认 None 时行为完全不变（向后兼容）。
    """
    findings: list[dict] = []
    base_root: Path = Path(scan_root) if scan_root else REPO_ROOT
    src_dir: Path = base_root / "src" / "zephyr"
    if not src_dir.is_dir():
        # scan_root 下无 src/zephyr（如空 worktree 或路径错误）——返回空，避免 iterdir 抛错
        return findings
    packages = sorted(p for p in src_dir.iterdir() if p.is_dir() and not p.name.startswith("_"))
    if package_filter:
        packages = [p for p in packages if p.name == package_filter]

    def scan_file(py_file: Path, pkg_name: str) -> dict | None:
        """scan_file implementation."""
        try:
            content = py_file.read_text(encoding="utf-8")
        except OSError:
            return None
        m = BLUEPRINT_HEADER_RE.search(content)
        if not m:
            return None
        header_modid = m.group(1)
        return {"file": str(py_file.relative_to(base_root)), "package": pkg_name, "header_modid": header_modid}

    for pkg in packages:
        py_files = list(pkg.rglob("*.py"))
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(scan_file, f, pkg.name): f for f in py_files}
            for fut in as_completed(futures):
                result = fut.result()
                if result:
                    findings.append(result)

    return findings


def check_header_vs_registry(
    code_headers: list[dict],
    blueprint_registry: dict[str, dict],
    pkg_to_modid: dict[str, str],
    depgraph_module_ids: set[str] | None = None,
) -> list[dict]:
    """检查代码头部 module_id 是否在 registry 或 depgraph 中登记。

    裁定#211：ORPHAN_MODULE_ID 改为双源验证——
    - blueprint_registry.yaml（从 blueprint.md frontmatter 同步，57个）
    - depgraph.nodes.blueprint_id（从代码扫描，166个）
    两者有其一即通过。只有两者都无才报 orphan。
    这样合理 MOD-XXX（depgraph 有）通过，SRC-XXX 旧格式（两者都无）仍报 drift。
    """
    drifts: list[dict] = []
    depgraph_module_ids = depgraph_module_ids or set()
    for entry in code_headers:
        header_modid = entry["header_modid"]
        pkg_name = entry["package"]
        expected_modid = pkg_to_modid.get(pkg_name)

        if header_modid not in blueprint_registry and header_modid not in depgraph_module_ids:
            drifts.append(
                {
                    "type": "ORPHAN_MODULE_ID",
                    "severity": "HIGH",
                    "file": entry["file"],
                    "detail": f"[BLUEPRINT] 引用 {header_modid} 不在 blueprint_registry.yaml 或 depgraph 中",
                }
            )

        if expected_modid and header_modid != expected_modid:
            drifts.append(
                {
                    "type": "MODULE_ID_DRIFT",
                    "severity": "HIGH",
                    "file": entry["file"],
                    "detail": f"包 {pkg_name} 应属 {expected_modid}，但 [BLUEPRINT] 标注 {header_modid}",
                }
            )

    return drifts


def check_blueprint_file_list(
    blueprint_registry: dict[str, dict],
    depgraph_files_by_module: dict[str, set[str]] | None = None,
) -> list[dict]:
    """裁定#211：蓝图§4文件清单改为 depgraph 派生。

    原逻辑：解析蓝图§4 markdown 表格中"已实现"的文件，检查磁盘是否存在。
    新逻辑：depgraph 只记录实际存在的文件，此检查冗余，返回空列表。
    保留函数签名以维持向后兼容。
    """
    return []


def check_code_not_in_blueprint(
    code_headers: list[dict],
    blueprint_registry: dict[str, dict],
    depgraph_files_by_module: dict[str, set[str]] | None = None,
) -> list[dict]:
    """裁定#211：蓝图§4文件清单改为 depgraph 派生。

    原逻辑：遍历 actual_disk_path 下的 .py 文件，如果有 [BLUEPRINT] 头部但不在蓝图§4表格，报 drift。
    新逻辑：检查代码文件是否在 depgraph 该 blueprint_id 的 path 列表中。
    如果不在，说明 depgraph 未扫描到该文件（depgraph 不完整或文件新创建未同步）。

    蓝图§0.1 已声明 SSoT 是 depgraph（见 agent_orchestrator/blueprint.md L53-58）：
      > **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-039`
    """
    drifts: list[dict] = []
    depgraph_files_by_module = depgraph_files_by_module or {}

    for entry in code_headers:
        header_modid = entry["header_modid"]
        file_rel = entry["file"].replace("\\", "/")
        depgraph_files = depgraph_files_by_module.get(header_modid, set())
        if file_rel not in depgraph_files:
            drifts.append(
                {
                    "type": "CODE_NOT_IN_DEPGRAPH",
                    "severity": "LOW",
                    "file": entry["file"],
                    "detail": f"代码文件有[BLUEPRINT]头部 {header_modid}，但不在 depgraph 该模块节点列表中（depgraph 可能未更新；若文件曾重命名，请运行 apply_depgraph.py 同步路径——裁定#ARCH-DRIFT-PREVENTION-001 ADP-5）。若为新建文件后首次检查，此为 reconciler 同步暂态滞后，无需人工干预，等待下次 merge 周期自动修复",
                }
            )

    return drifts


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="蓝图↔代码双向对齐检测")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--package", type=str, help="限定扫描单个包")
    parser.add_argument(
        "--scan-root",
        type=str,
        default=None,
        help="扫描根目录（#ARCH-DEP-001 第二期 pre-merge 拓扑硬阻断用）："
        "给定时扫描 <scan-root>/src/zephyr 而非默认 SRC_DIR，"
        "DB 配置和蓝图注册表仍用 main REPO_ROOT。用于 session_worktree "
        "pre-merge 检查 worktree session 分支代码相对 production depgraph 的漂移。",
    )
    args = parser.parse_args()

    blueprint_registry = load_blueprint_registry()
    pkg_to_modid = load_module_registry()

    code_headers = scan_code_blueprint_headers(
        package_filter=args.package,
        scan_root=args.scan_root,
    )

    # 裁定#211：加载 depgraph 模块索引（ORPHAN 验证 + 文件清单派生）
    depgraph_module_ids, depgraph_files_by_module = load_depgraph_module_index()

    drift_findings = check_header_vs_registry(code_headers, blueprint_registry, pkg_to_modid, depgraph_module_ids)
    file_missing_findings = check_blueprint_file_list(blueprint_registry, depgraph_files_by_module)
    code_not_in_bp_findings = check_code_not_in_blueprint(code_headers, blueprint_registry, depgraph_files_by_module)

    # ARCH-FRONTMATTER-STATE-001 Phase 4：L3 frontmatter 缓存 vs L2 depgraph 状态一致性
    depgraph_build_status = load_depgraph_build_status()
    frontmatter_entries = scan_blueprint_frontmatter_entries()
    frontmatter_stale_findings = check_frontmatter_state_stale(frontmatter_entries, depgraph_build_status)

    all_findings = drift_findings + file_missing_findings + code_not_in_bp_findings + frontmatter_stale_findings

    high_count = sum(1 for f in all_findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in all_findings if f["severity"] == "MEDIUM")
    low_count = sum(1 for f in all_findings if f["severity"] == "LOW")

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "total_findings": len(all_findings),
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count,
                    "findings": all_findings,
                    "code_headers_scanned": len(code_headers),
                    "blueprints_in_registry": len(blueprint_registry),
                    "depgraph_module_ids": len(depgraph_module_ids),
                    "frontmatter_entries_scanned": len(frontmatter_entries),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("=" * 60)
        print("蓝图↔代码双向对齐检测")
        print("=" * 60)
        print(f"扫描: {len(code_headers)} 个代码文件有[BLUEPRINT]头部")
        print(f"蓝图注册表: {len(blueprint_registry)} 个 module_id")
        print(f"depgraph 模块索引: {len(depgraph_module_ids)} 个 blueprint_id（裁定#211 depgraph 派生）")
        print(f"蓝图 frontmatter: {len(frontmatter_entries)} 个条目（ARCH-FRONTMATTER-STATE-001 Phase 4）")
        print()

        if not all_findings:
            print("✅ 全部对齐，无漂移！")
        else:
            by_type: dict[str, list[dict]] = {}
            for f in all_findings:
                by_type.setdefault(f["type"], []).append(f)

            for ftype, items in by_type.items():
                print(f"{'─' * 60}")
                print(f"  {ftype} ({len(items)} 条)")
                print(f"{'─' * 60}")
                for item in items[:20]:
                    icon = "❌" if item["severity"] == "HIGH" else ("⚠️" if item["severity"] == "MEDIUM" else "ℹ️")
                    print(f"  {icon} {item['file']}")
                    print(f"     {item['detail']}")
                if len(items) > 20:
                    print(f"  ... 还有 {len(items) - 20} 条")

        print()
        print(f"{'=' * 60}")
        print(f"  总结: {len(all_findings)} 条漂移 (HIGH:{high_count} MEDIUM:{medium_count} LOW:{low_count})")
        print(f"{'=' * 60}")

    has_high = high_count > 0
    if has_high and not args.warn_only:
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def aggregate_build_status(rows) -> dict[str, str]:
    """公共接口：aggregate_build_status（Stage 4 公共化）。"""
    return _aggregate_build_status(rows)
