# [BLUEPRINT] MOD-GOV_CHECK_ALGO_FLOW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d5_architecture.checkers.check_algo_flow
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants
# [CONSUMERS] .pre-commit-config.yaml hook gate-algo-flow-marker
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib；只查 staged 的 src/zephyr/**/*.py；module docstring 缺 # [ALGO_FLOW] 标记 → findings；exit 0=pass / 1=findings / 2=error
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不抛异常——AST/git 异常降级为 exit 2 + stderr 提示
# [TESTS] 无（门禁脚本，自验证）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: pre-commit hook 事件触发（.pre-commit-config.yaml gate-algo-flow-marker），CLI 仅供人工排查
"""check_algo_flow.py — ALGO_FLOW 标记门禁（算法地图全量落地配套，§4.16）。

目的（D2 目的声明）：防止运营态模块回退/新增缺失 `# [ALGO_FLOW]` docstring 标记——
该标记是算法全景图（08_algorithm_overview）推导流程图的唯一结构化真源。
2026-08-12 全量落地后 416/416 运营态模块已补标记，本门禁把「新增/修改模块必须含标记」
从君子协定升级为 pre-commit 硬门禁（用户裁定 2026-08-12）。

检查逻辑：staged 的 src/zephyr/**/*.py 文件，AST 提取 module docstring，
不含 `# [ALGO_FLOW]` → findings 列出。空包占位 __init__.py 也在检查范围
（全量落地已覆盖，含空包的三层最小标记）。

exit codes: 0=pass, 1=findings(缺标记), 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  ALGO_FLOW 标记门禁：staged 的 src/zephyr/**/*.py 必须含 # [ALGO_FLOW] docstring 标记
  （算法全景图推导流程图真源，§4.16，2026-08-12 全量落地后转强制）。
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

_ALGO_FLOW_MARKER = "# [ALGO_FLOW]"

# codegen 产物豁免（#ARCH-130 P0-A，2026-08-19）：
# frozen dataclass 契约文件（DO NOT EDIT codegen）是纯数据声明，无算法流程，
# 不纳入 ALGO_FLOW 算法全景图。判定：文件头注区含 codegen 标记。
_CODEGEN_MARKERS = (
    "DO NOT EDIT (codegen)",
    "Status: AUTO-GENERATED -- DO NOT EDIT BY HAND",
)


def _is_codegen_artifact(src: str) -> bool:
    """判定文件是否为 codegen 产物（纯数据契约，豁免 ALGO_FLOW）。"""
    head = src[:2000]  # 头注区+docstring 开头
    return any(m in head for m in _CODEGEN_MARKERS)


def _has_algo_flow(py_path: Path) -> tuple[bool, str]:
    """检查 .py 文件 module docstring 是否含 ALGO_FLOW 标记。

    :return: (has_marker, error)；error 非空表示检查本身失败。
    """
    try:
        src = py_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return False, f"读取失败: {e}"
    # codegen 产物豁免（纯数据契约无算法流程）
    if _is_codegen_artifact(src):
        return True, ""
    try:
        tree = ast.parse(src, filename=str(py_path))
    except SyntaxError as e:
        return False, f"AST解析失败: {e}"
    doc = ast.get_docstring(tree) or ""
    return _ALGO_FLOW_MARKER in doc, ""


def main(argv: list[str]) -> int:
    """Entry point: parse args, run logic, return exit code."""
    # pre-commit pass_filenames=true 传入 staged 文件；无参数时直接通过
    files = [a for a in argv if a.endswith(".py") and a.replace("\\", "/").startswith("src/zephyr/")]
    if not files:
        return EXIT_PASS

    missing: list[str] = []
    errors: list[str] = []
    for rel in files:
        ok, err = _has_algo_flow(Path(rel))
        if err:
            errors.append(f"{rel}: {err}")
        elif not ok:
            missing.append(rel)

    for e in errors:
        print(f"[ERR] {e}", file=sys.stderr)
    if missing:
        print("[GATE-ALGO-FLOW] 以下 src/zephyr 模块缺 # [ALGO_FLOW] docstring 标记（§4.16）：")
        for m in missing:
            print(f"  - {m}")
        print("  修复：在 module docstring 补 ALGO_FLOW 块（格式见 visualization_view_template.md §4.16；")
        print("  草稿生成器：python scripts/governance/_shared/algo_flow_drafter.py <file>）")
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # noqa: BLE001 — 门禁永不裸抛
        print(f"[ERR] check_algo_flow 异常: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
