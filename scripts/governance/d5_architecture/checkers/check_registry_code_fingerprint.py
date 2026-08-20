# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_registry_code_fingerprint.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_registry_code_fingerprint
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS] manual / reconciler（后续批接线）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 指纹对账只告警不自动双写（--fix-in-place 需显式传入）; 合并态豁免
# [MODIFY-GUARD] #ARCH-BREG-002 门禁B
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 漂移→exit 1+清单; 无漂移→exit 0; 环境异常→exit 2
# [TESTS] tests/governance/commit_gates/test_registry_code_anchor_gate.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_registry_code_fingerprint.py —— 业务注册表实现指纹对账（#ARCH-BREG-002 门禁B）

分域真源：算法实现域 owner=代码。库侧 code_fingerprint 是代码实现（AST canonical）的
快照，代码实现变更后指纹不一致=实现域已漂移，库侧 evidence/algorithm_status 需重估。

指纹算法（canonical AST hash）：
  1. AST 解析 code_symbol 目标函数/类（Class.method 支持）
  2. 剥离 docstring（表达式语句且值为字符串常量的首个 body 元素）
  3. ast.dump(node, include_attributes=False) canonical 序列化
  4. sha256 取前 16 hex

对账规则（不自动双写——漂移只告警，快照更新须显式 --fix-in-place）：
  - code_symbol=null：设计态条目，跳过
  - code_fingerprint=null：缺快照（warn，提示 --fix-in-place 建档）
  - 指纹不一致：漂移告警（exit 1）
  - status ∈ {deprecated, retired}：豁免

Usage:
    python check_registry_code_fingerprint.py                 # 对账（warn 清单，漂移 exit 1）
    python check_registry_code_fingerprint.py --fix-in-place  # 更新库侧快照（reconciler fix-in-place 语义）
exit codes: 0=pass, 1=drift found, 2=error
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装")
    sys.exit(EXIT_ERROR)

__manifest__ = """
args:
- --ci
- --fix-in-place
description: 业务注册表实现指纹对账（code_fingerprint vs 代码 AST hash，#ARCH-BREG-002 门禁B，告警不自动双写）
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: true
"""

_CATALOGS = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"

# 与门禁A 一致的 15 库清单（file -> 主条目列表键）
REGISTRY_LISTS: dict[str, list[str]] = {
    "factor_registry.yaml": ["factors"],
    "strategy_registry.yaml": ["strategies"],
    "technical_indicator_registry.yaml": ["indicators"],
    "universe_registry.yaml": ["universes"],
    "benchmark_registry.yaml": ["benchmarks"],
    "cost_model_registry.yaml": ["cost_models"],
    "execution_algo_registry.yaml": ["execution_algos"],
    "risk_limit_registry.yaml": ["risk_limits"],
    "data_asset_registry.yaml": ["sources", "datasets", "jobs"],
    "chart_pattern_registry.yaml": ["chart_patterns"],
    "field_dictionary.yaml": ["fields"],
    "experiment_registry.yaml": ["experiments"],
    "model_registry.yaml": ["models"],
    "regime_cycle_registry.yaml": ["cycles"],
    "portfolio_model_registry.yaml": ["portfolio_models"],
}

_ID_KEYS = (
    "factor_id",
    "strategy_id",
    "indicator_id",
    "universe_id",
    "benchmark_id",
    "cost_model_id",
    "execution_algo_id",
    "risk_limit_id",
    "source_id",
    "dataset_id",
    "job_id",
    "pattern_id",
    "field_id",
    "experiment_id",
    "model_id",
    "cycle_id",
    "event_type_id",
)


def _is_merge_in_progress() -> bool:
    """合并进行中（.git/MERGE_HEAD 存在）→ 半合并工作区不可信，豁免。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            return False
        return (Path(result.stdout.strip()) / "MERGE_HEAD").exists()
    except Exception:  # noqa: BLE001 — 检测失败保守返回 False
        return False


def _entry_id(entry: dict) -> str:
    """_entry_id implementation."""
    for k in _ID_KEYS:
        v = entry.get(k)
        if v:
            return str(v)
    return "(unknown)"


def _find_symbol_node(tree: ast.Module, dotted: str):
    """在 AST 中定位符号（顶层 def/class 或 Class.method）。"""
    parts = dotted.split(".")
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == parts[0]:
            if len(parts) == 1:
                return node
            if isinstance(node, ast.ClassDef) and len(parts) == 2:
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name == parts[1]:
                        return sub
    return None


def _strip_docstring(node) -> None:
    """就地剥离函数/类节点的 docstring（首个 body 元素为字符串常量表达式）。"""
    body = getattr(node, "body", None)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        node.body = body[1:]


def compute_fingerprint(py_path: Path, symbol: str) -> str | None:
    """计算符号的 canonical AST 指纹（sha256 前 16 hex）。失败返回 None。"""
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None
    node = _find_symbol_node(tree, symbol)
    if node is None:
        return None
    node = ast.fix_missing_locations(node)
    _strip_docstring(node)
    # 类节点需递归剥离方法 docstring
    if isinstance(node, ast.ClassDef):
        for sub in node.body:
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _strip_docstring(sub)
    dump = ast.dump(node, include_attributes=False)
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()[:16]


def reconcile(fix_in_place: bool = False) -> int:
    """主对账函数。fix_in_place=True 时把漂移/缺失条目的库侧快照更新为当前代码指纹。"""
    if _is_merge_in_progress():
        print("[SKIP] 合并进行中（MERGE_HEAD 存在）——半合并态工作区不可信，指纹对账豁免")
        return EXIT_PASS

    drifts: list[str] = []
    missing: list[str] = []
    skipped_design = 0
    skipped_dead = 0
    checked = 0
    fixes: dict[str, list[tuple[str, str]]] = {}  # reg_name -> [(entry_id, new_fp)]

    for name, lists in REGISTRY_LISTS.items():
        reg = _CATALOGS / name
        if not reg.is_file():
            continue
        data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
        for lk in lists:
            for entry in data.get(lk) or []:
                if not isinstance(entry, dict):
                    continue
                if entry.get("status") in ("deprecated", "retired"):
                    skipped_dead += 1
                    continue
                code_symbol = entry.get("code_symbol")
                if not code_symbol:
                    skipped_design += 1
                    continue
                sym = str(code_symbol)
                if "::" not in sym:
                    continue
                rel, _, symbol = sym.partition("::")
                target = REPO_ROOT / rel.strip()
                fp = compute_fingerprint(target, symbol.strip()) if target.suffix == ".py" else None
                if fp is None:
                    continue  # 文件/符号不存在由门禁A负责报告，此处不重复
                checked += 1
                stored = entry.get("code_fingerprint")
                eid = _entry_id(entry)
                if not stored:
                    missing.append(f"  - [缺快照] {name} {lk}/{eid}: {sym}")
                    fixes.setdefault(name, []).append((eid, fp))
                elif stored != fp:
                    drifts.append(
                        f"  - [实现漂移] {name} {lk}/{eid}: {sym} "
                        f"(库侧 {stored} ≠ 代码 {fp})——evidence/algorithm_status 需重估"
                    )
                    fixes.setdefault(name, []).append((eid, fp))

    if fix_in_place and fixes:
        n_fix = _apply_fixes(fixes)
        print(f"[FIX-IN-PLACE] 已更新 {n_fix} 条库侧指纹快照")

    for line in missing:
        print(line)
    for line in drifts:
        print(line)

    if drifts:
        print(f"\n[FAIL] 指纹对账发现 {len(drifts)} 条实现漂移（REGISTRY_CODE_FINGERPRINT_DRIFT）")
        return EXIT_FINDINGS
    print(
        f"[PASS] 指纹对账完成：checked={checked} 缺快照={len(missing)} "
        f"设计态跳过={skipped_design} tombstone 豁免={skipped_dead}"
    )
    return EXIT_PASS


def _apply_fixes(fixes: dict[str, list[tuple[str, str]]]) -> int:
    """把新指纹写回库条目 code_fingerprint 行（文本级替换，保持格式）。"""
    n = 0
    for name, pairs in fixes.items():
        reg = _CATALOGS / name
        lines = reg.read_text(encoding="utf-8").split("\n")
        id_to_fp = dict(pairs)
        current_id = None
        for i, ln in enumerate(lines):
            m_id = re.match(r"^\s*- (\w+_id):\s*[\"']?([^\"'\s]+)", ln)
            if m_id:
                current_id = m_id.group(2)
                continue
            if current_id in id_to_fp and re.match(r"^\s+code_fingerprint:", ln):
                indent = ln[: len(ln) - len(ln.lstrip())]
                lines[i] = f'{indent}code_fingerprint: "{id_to_fp[current_id]}"'
                n += 1
                current_id = None
        reg.write_text("\n".join(lines), encoding="utf-8")
    return n


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="业务注册表实现指纹对账（code_fingerprint vs 代码 AST hash，#ARCH-BREG-002 门禁B）"
    )
    parser.add_argument("--ci", action="store_true", help="CI 模式")
    parser.add_argument(
        "--fix-in-place",
        action="store_true",
        help="更新库侧指纹快照为当前代码指纹（reconciler fix-in-place 语义，默认只告警不双写）",
    )
    args = parser.parse_args()
    sys.exit(reconcile(fix_in_place=args.fix_in_place))


if __name__ == "__main__":
    main()
