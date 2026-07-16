# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_no_cross_plane_mutable_state.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_no_cross_plane_mutable_state
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.fitness_functions.__init__
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
"""check_no_cross_plane_mutable_state.py — INV-020 跨平面共享可变状态检查

对标 runtime_planes.yaml NO_SHARED_MUTABLE_STATE + invariants.yaml INV-020。
检查是否存在跨运行时平面的共享可变全局状态（如 global dict/list）。

当前状态：L2-static-scan——扫描 global 可变声明。
exit: 0=合规, 1=违规, 2=基础设施错误
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

SRC_ROOT = REPO_ROOT / "src" / "zephyr"

MUTABLE_TYPES = {"dict", "list", "set", "deque", "defaultdict", "OrderedDict"}

def _scan_file(path: Path) -> list[tuple[int, str]]:
    findings = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except Exception:
        return findings

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    if isinstance(node.value, ast.Call):
                        func = node.value.func
                        if isinstance(func, ast.Name) and func.id in MUTABLE_TYPES:
                            findings.append((node.lineno, f"global mutable: {target.id} = {func.id}()"))
                    elif isinstance(node.value, (ast.Dict, ast.List, ast.Set)):
                        findings.append((node.lineno, f"global mutable: {target.id} = literal"))
    return findings

def main() -> int:
    print("INV-020 跨平面共享可变状态检查\n")

    if not SRC_ROOT.exists():
        print("[SKIP] src/zephyr/ 不存在")
        return 0

    total_findings = 0
    for py_file in SRC_ROOT.rglob("*.py"):
        if "test_" in py_file.name or "conftest" in py_file.name:
            continue
        findings = _scan_file(py_file)
        for lineno, desc in findings:
            rel = py_file.relative_to(REPO_ROOT)
            print(f"  [WARN] {rel}:{lineno} — {desc}")
            total_findings += 1

    print(f"\n扫描完成，发现 {total_findings} 处全局可变状态声明")
    if total_findings > 0:
        print("[WARN] 请确认这些全局可变状态未跨运行时平面共享")
        print("[OK] 当前为 L2-static-scan 级别，无法确认跨平面共享——需 L3-runtime 验证")
        return 0

    print("[OK] 未发现全局可变状态声明")
    return 0

if __name__ == "__main__":
    sys.exit(main())
