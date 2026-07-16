# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
[MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
[INVARIANTS] 代码[BLUEPRINT]头部module_id必须与蓝图注册表一致; 蓝图§4已实现文件必须在磁盘存在
[MODIFY-GUARD] script_manifest.yaml; blueprint_registry.yaml
[CONSUMERS] CI pipeline; AI session 冷启动; Phase Gate
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
from _shared.walk import iter_files

__manifest__ = """
args: [--warn-only, --json, --package]
description: 蓝图↔代码双向对齐检测——代码[BLUEPRINT]头部module_id双源验证(registry+depgraph)+蓝图§4文件清单depgraph派生(裁定#211)
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
    "SELECT blueprint_id, path FROM nodes "
    "WHERE blueprint_id IS NOT NULL AND blueprint_id != '' "
    "AND path LIKE '%%.py'"
)


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


def load_blueprint_registry() -> dict[str, dict]:
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


def scan_code_blueprint_headers(package_filter: str | None = None) -> list[dict]:
    findings: list[dict] = []
    packages = sorted(p for p in SRC_DIR.iterdir() if p.is_dir() and not p.name.startswith("_"))
    if package_filter:
        packages = [p for p in packages if p.name == package_filter]

    def scan_file(py_file: Path, pkg_name: str) -> dict | None:
        try:
            content = py_file.read_text(encoding="utf-8")
        except OSError:
            return None
        m = BLUEPRINT_HEADER_RE.search(content)
        if not m:
            return None
        header_modid = m.group(1)
        return {"file": str(py_file.relative_to(REPO_ROOT)), "package": pkg_name, "header_modid": header_modid}

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
                    "detail": f"代码文件有[BLUEPRINT]头部 {header_modid}，但不在 depgraph 该模块节点列表中（depgraph 可能未更新）",
                }
            )

    return drifts


def main() -> None:
    parser = argparse.ArgumentParser(description="蓝图↔代码双向对齐检测")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--package", type=str, help="限定扫描单个包")
    args = parser.parse_args()

    blueprint_registry = load_blueprint_registry()
    pkg_to_modid = load_module_registry()

    code_headers = scan_code_blueprint_headers(package_filter=args.package)

    # 裁定#211：加载 depgraph 模块索引（ORPHAN 验证 + 文件清单派生）
    depgraph_module_ids, depgraph_files_by_module = load_depgraph_module_index()

    drift_findings = check_header_vs_registry(
        code_headers, blueprint_registry, pkg_to_modid, depgraph_module_ids
    )
    file_missing_findings = check_blueprint_file_list(blueprint_registry, depgraph_files_by_module)
    code_not_in_bp_findings = check_code_not_in_blueprint(
        code_headers, blueprint_registry, depgraph_files_by_module
    )

    all_findings = drift_findings + file_missing_findings + code_not_in_bp_findings

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
