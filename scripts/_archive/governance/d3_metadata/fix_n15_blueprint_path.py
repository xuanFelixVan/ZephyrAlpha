# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/fix_n15_blueprint_path.py | §
# [MODULE] scripts.governance.d3_metadata.fix_n15_blueprint_path
# [INVARIANTS] Only modifies [BLUEPRINT] header line; preserves module_id and section ref
# [MODIFY-GUARD] OLD_TO_NEW_DOMAIN_MAP changes require Owner approval
# [CONSUMERS] check_naming_convention.py N-15; governance pipeline
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=clean or fixes applied; exit 1=unresolved findings; exit 2=usage error
# [TESTS] --dry-run mode validates without writing
"""修复 N-15 命名违规：[BLUEPRINT] 头部路径不存在。

两类问题：
  1. 旧架构路径 l0X_yyy → 新架构 _domain-yyy / _cross_layer
  2. 路径缺少 docs/ 前缀（如 03_modules/... → docs/03_modules/...）

修复策略（按优先级）：
  a) 旧层目录映射：l01_infrastructure → _domain-autonomy_perm 等
  b) 模块名搜索：在 docs/03_modules/ 下按模块名查找 blueprint.md
  c) module_id 搜索：在所有 blueprint.md 中搜索 module_id 匹配
  d) 前缀修复：路径缺 docs/ 前缀时自动补齐
  e) 以上均失败 → UNRESOLVED
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

BLUEPRINT_HEADER_RE = re.compile(
    r"^(\s*#\s*\[BLUEPRINT\]\s+)(\S+)(\s*\|\s*)(\S+)(\s*\|.*)$",
    re.MULTILINE,
)

OLD_TO_NEW_DOMAIN_MAP: dict[str, str] = {
    "l01-infrastructure": "_domain-autonomy_perm",
    "l02_data": "_domain-data",
    "l03_signal": "_domain-signal",
    "l04_risk": "_domain-risk",
    "l05_portfolio": "_domain-pf_core",
    "l06_execution": "_domain-ex_core",
    "l07_research": "_domain-research",
    "l08_knowledge": "_domain-knowledge",
    "l09_governance": "_domain-governance",
    "l10-compliance": "_domain-compliance",
    "l11_reporting": "_domain-reporting",
    "l12_simulation": "_domain-simulation",
    "l13_ml_training": "_domain-ml_train",
    "l14_frontend": "_domain-frontend",
    "l15_factor": "_domain-factor",
    "l16_integration": "_domain-integration",
}

MODULE_TO_DOMAIN_MAP: dict[str, str] = {
    "budget-enforcer": "_domain-autonomy_perm",
    "escalation-engine": "_domain-autonomy_perm",
    "audit-trail": "_domain-governance",
    "a2a-protocol": "_domain-infra_ops",
    "knowledge-base": "_domain-knowledge",
    "gate-engine": "_cross_layer",
    "feedback-loop": "_cross_layer",
    "context-engine": "_cross_layer",
    "llm-security": "_cross_layer",
    "mcp-servers": "_cross_layer",
    "pipeline": "_cross_layer",
    "auto-fix-engine": "_cross_layer",
    "auto-runtime-core": "_cross_layer",
    "agent-orchestrator": "_cross_layer",
    "audit-orchestrator": "_cross_layer",
    "behavioral-auditor": "_cross_layer",
    "red-blue-validator": "_cross_layer",
    "orphan-judge": "_cross_layer",
    "model-profiler": "_cross_layer",
    "model-capability-exam": "_cross_layer",
    "semantic-auditor": "_cross_layer",
    "shared-core": "_cross_layer",
    "resource-optimization-engine": "_cross_layer",
    "database": "_cross_layer",
    "drift-detector": "_domain-governance",
    "capacity-assurance": "_domain-infra_ops",
    "asset-inventory": "_domain-infra_ops",
    "system-telemetry": "_domain-infra_ops",
    "runtime-integration": "_domain-infra_runtime",
    "task-system": "_domain-infra_runtime",
    "state-machine-engine": "_domain-infra_runtime",
    "agent-rbac": "_domain-autonomy_core",
    "agent-spec": "_domain-autonomy_core",
    "rollback-system": "_domain-autonomy_core",
    "task-card-kms": "_domain-autonomy_core",
    "governance-automation": "_domain-governance",
    "registry-governance": "_domain-governance",
    "code-dedup-engine": "_domain-governance",
    "capacity-upgrade": "_domain-governance",
    "vibe-coding-pipelines": "_domain-governance",
    "datasource-core": "_domain-data",
    "signal-generation-core": "_domain-signal",
    "risk-management-core": "_domain-risk",
    "portfolio-core": "_domain-pf_core",
    "execution-core": "_domain-ex_core",
    "research-core": "_domain-research",
    "vector-memory": "_domain-knowledge",
    "compliance-core": "_domain-compliance",
    "analytics-core": "_domain-reporting",
    "experiment-core": "_domain-simulation",
    "ml-core": "_domain-ml_train",
    "hmi-core": "_domain-frontend",
    "alpha-factor-core": "_domain-factor",
    "local-model": "_domain-integration",
}

SCAN_DIRS = [
    REPO_ROOT / "src" / "zephyr",
    REPO_ROOT / "tests",
]

BLUEPRINT_SEARCH_ROOT = REPO_ROOT / "docs" / "03_modules"


@dataclass
class FixResult:
    filepath: Path
    old_path: str
    new_path: str | None
    status: str  # "FIXED", "ALREADY_OK", "UNRESOLVED"
    reason: str = ""


@dataclass
class BlueprintIndex:
    """Pre-built index of all blueprint.md files for fast lookup."""

    by_module_name: dict[str, Path] = field(default_factory=dict)
    by_module_id: dict[str, Path] = field(default_factory=dict)
    all_paths: list[Path] = field(default_factory=list)


def build_blueprint_index() -> BlueprintIndex:
    """Scan docs/03_modules/ and build lookup indexes."""
    idx = BlueprintIndex()
    _module_id_re = re.compile(r"^module_id:\s*(\S+)", re.MULTILINE)

    for bp in BLUEPRINT_SEARCH_ROOT.rglob("blueprint.md"):
        rel = bp.relative_to(REPO_ROOT)
        idx.all_paths.append(bp)
        module_name = bp.parent.name
        idx.by_module_name[module_name] = bp
        try:
            content = bp.read_text(encoding="utf-8", errors="replace")
            m = _module_id_re.search(content)
            if m:
                idx.by_module_id[m.group(1)] = bp
        except Exception:
            pass
    return idx


def _try_old_layer_mapping(declared_path: str) -> str | None:
    """Map old l0X_yyy/... paths to new _domain-yyy/... paths."""
    for old_layer, new_domain in OLD_TO_NEW_DOMAIN_MAP.items():
        if f"/{old_layer}/" in declared_path or declared_path.startswith(f"{old_layer}/"):
            parts = declared_path.split("/")
            new_parts: list[str] = []
            replaced = False
            for part in parts:
                if part == old_layer and not replaced:
                    new_parts.append(new_domain)
                    replaced = True
                else:
                    new_parts.append(part)
            candidate = "/".join(new_parts)
            if (REPO_ROOT / candidate).exists():
                return candidate
            parent_dir = new_domain.lstrip("_domain-")
            module_name = parts[-2] if len(parts) >= 2 else ""
            if module_name in MODULE_TO_DOMAIN_MAP:
                mapped_domain = MODULE_TO_DOMAIN_MAP[module_name]
                alt_parts = list(new_parts)
                alt_parts[alt_parts.index(new_domain)] = mapped_domain
                candidate2 = "/".join(alt_parts)
                if (REPO_ROOT / candidate2).exists():
                    return candidate2
    return None


def _try_prefix_fix(declared_path: str) -> str | None:
    """Fix paths missing docs/ prefix: 03_modules/... → docs/03_modules/..."""
    if declared_path.startswith("03_modules/"):
        candidate = f"docs/{declared_path}"
        if (REPO_ROOT / candidate).exists():
            return candidate
    return None


def _try_module_name_search(declared_path: str, index: BlueprintIndex) -> str | None:
    """Search for blueprint.md by module name extracted from the path."""
    parts = declared_path.replace("\\", "/").split("/")
    module_name = parts[-2] if len(parts) >= 2 else ""
    if module_name and module_name in index.by_module_name:
        bp = index.by_module_name[module_name]
        return str(bp.relative_to(REPO_ROOT)).replace("\\", "/")
    return None


def _try_module_id_search(module_id: str, index: BlueprintIndex) -> str | None:
    """Search for blueprint.md containing the given module_id."""
    if module_id in index.by_module_id:
        bp = index.by_module_id[module_id]
        return str(bp.relative_to(REPO_ROOT)).replace("\\", "/")
    return None


def _try_combined_old_layer_and_prefix(declared_path: str) -> str | None:
    """Fix both old layer mapping AND missing docs/ prefix simultaneously."""
    if not declared_path.startswith("03_modules/"):
        return None
    path_with_prefix = f"docs/{declared_path}"
    result = _try_old_layer_mapping(path_with_prefix)
    if result:
        return result
    return None


def resolve_blueprint_path(
    module_id: str,
    declared_path: str,
    index: BlueprintIndex,
) -> tuple[str | None, str]:
    """Try all heuristics to find the correct blueprint path.

    Returns (new_path_or_None, strategy_used_or_reason).
    """
    if (REPO_ROOT / declared_path).exists():
        return declared_path, "ALREADY_OK"

    strategies = [
        ("prefix_fix", lambda: _try_prefix_fix(declared_path)),
        ("old_layer_mapping", lambda: _try_old_layer_mapping(declared_path)),
        ("combined_old_layer+prefix", lambda: _try_combined_old_layer_and_prefix(declared_path)),
        ("module_name_search", lambda: _try_module_name_search(declared_path, index)),
        ("module_id_search", lambda: _try_module_id_search(module_id, index)),
    ]

    for strategy_name, strategy_fn in strategies:
        result = strategy_fn()
        if result and (REPO_ROOT / result).exists():
            return result, strategy_name

    return None, "UNRESOLVED"


def process_file(
    filepath: Path,
    index: BlueprintIndex,
    apply: bool,
) -> list[FixResult]:
    """Process a single .py file: find and fix N-15 violations."""
    results: list[FixResult] = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        results.append(
            FixResult(
                filepath=filepath,
                old_path="",
                new_path=None,
                status="UNRESOLVED",
                reason=f"读取失败: {e}",
            )
        )
        return results

    matches = list(BLUEPRINT_HEADER_RE.finditer(content))
    if not matches:
        return results

    new_content = content
    offset = 0

    for match in matches:
        full_line = match.group(0)
        module_id = match.group(2)
        declared_path = match.group(4)

        new_path, strategy = resolve_blueprint_path(module_id, declared_path, index)

        if strategy == "ALREADY_OK":
            results.append(
                FixResult(
                    filepath=filepath,
                    old_path=declared_path,
                    new_path=declared_path,
                    status="ALREADY_OK",
                )
            )
            continue

        if new_path:
            old_full = full_line
            new_full = f"{match.group(1)}{module_id}{match.group(3)}{new_path}{match.group(5)}"
            start = match.start() + offset
            end = match.end() + offset
            new_content = new_content[:start] + new_full + new_content[end:]
            offset += len(new_full) - len(old_full)

            results.append(
                FixResult(
                    filepath=filepath,
                    old_path=declared_path,
                    new_path=new_path,
                    status="FIXED",
                    reason=strategy,
                )
            )
        else:
            results.append(
                FixResult(
                    filepath=filepath,
                    old_path=declared_path,
                    new_path=None,
                    status="UNRESOLVED",
                    reason=f"无法定位 blueprint (module_id={module_id})",
                )
            )

    if apply and any(r.status == "FIXED" for r in results):
        tmp_path = f"{filepath}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_path, str(filepath))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            for r in results:
                if r.status == "FIXED":
                    r.status = "UNRESOLVED"
                    r.reason = "写入失败: PermissionError"

    return results


def collect_py_files() -> list[Path]:
    """Collect all .py files from scan directories."""
    files: list[Path] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for root, _dirs, filenames in os.walk(scan_dir):
            for fn in filenames:
                if fn.endswith(".py"):
                    files.append(Path(root) / fn)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="修复 N-15 命名违规：[BLUEPRINT] 头部路径不存在",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际修改文件（默认 dry-run 只显示）",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="并行线程数（默认 8）",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="有 UNRESOLVED 时也返回 exit 0",
    )
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[fix_n15_blueprint_path] 模式: {mode}")
    print(f"[fix_n15_blueprint_path] 项目根: {REPO_ROOT}")

    print("[fix_n15_blueprint_path] 构建蓝图索引...")
    index = build_blueprint_index()
    print(f"[fix_n15_blueprint_path] 索引完成: {len(index.by_module_name)} 模块名, {len(index.by_module_id)} module_id")

    print("[fix_n15_blueprint_path] 收集 .py 文件...")
    py_files = collect_py_files()
    print(f"[fix_n15_blueprint_path] 共 {len(py_files)} 个 .py 文件")

    all_results: list[FixResult] = []
    fixed_count = 0
    already_ok_count = 0
    unresolved_count = 0

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(process_file, fp, index, args.apply): fp for fp in py_files}
        for future in as_completed(futures):
            try:
                results = future.result()
            except Exception as e:
                fp = futures[future]
                print(f"[ERROR] {fp}: {e}", file=sys.stderr)
                continue
            all_results.extend(results)

    for r in all_results:
        if r.status == "FIXED":
            fixed_count += 1
            action = "FIX" if not args.apply else "FIXED"
            print(f"  [{action}] {r.filepath.relative_to(REPO_ROOT)}")
            print(f"         {r.old_path}")
            print(f"      →  {r.new_path}  (策略: {r.reason})")
        elif r.status == "UNRESOLVED":
            unresolved_count += 1
            print(f"  [UNRESOLVED] {r.filepath.relative_to(REPO_ROOT)}")
            print(f"         {r.old_path}")
            print(f"         原因: {r.reason}")
        else:
            already_ok_count += 1

    print()
    print("=" * 60)
    print(f"汇总: FIXED={fixed_count}  ALREADY_OK={already_ok_count}  UNRESOLVED={unresolved_count}")
    print("=" * 60)

    if not args.apply and fixed_count > 0:
        print("\n提示: 使用 --apply 实际执行修改（当前为 dry-run）")

    if unresolved_count > 0 and not args.warn_only:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
