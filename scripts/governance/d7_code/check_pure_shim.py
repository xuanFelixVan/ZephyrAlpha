# [BLUEPRINT] MOD-GOV-SCRIPTS | scripts/governance/d7_code/check_pure_shim.py | §
# [MODULE] scripts.governance.d7_code.check_pure_shim
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS] GATE-NO-PURE-SHIM pre-commit hook
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 re-export shim 检测器——防止新 AI 创建纯跨包 re-export shim 文件（重蹈 shared_08 覆辙）
# [MODIFY-GUARD] 检测逻辑变更 MUST 同步更新 AGENTS.md 对应规则段落
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] --ci 模式发现纯 shim 返回 EXIT_FINDINGS(2)；--warn-only 模式返回 EXIT_PASS(0)+告警
# [TESTS] python scripts/governance/d7_code/check_pure_shim.py --ci <staged_files>
# [TTL] permanent
"""
check_pure_shim.py — GATE-NO-PURE-SHIM 检测器（治本漏洞1 2026-06-29）

防止新 AI 创建纯 re-export shim 文件（`from zephyr.shared.* import *` 无实质代码），
重蹈 shared_08 冗余 proxy 层覆辙（commit 98c990141c 删除 144 文件治本）。

判定标准（全部满足才阻断）：
  1. 文件不是 __init__.py（包聚合豁免）
  2. 文件头部无 `# [TTL] task_bound` + `# [DEPRECATED]` 标记（临时过渡豁免）
  3. AST 白名单分析（代码 is_pure_reexport_shim() 为唯一真源）：
     - 有至少一个 ImportFrom，module 以 "zephyr.shared." 开头（跨包 re-export）
     - 无实质代码——白名单方式：仅允许以下节点不算实质代码
       * ImportFrom / Import（导入语句）
       * Assign 且 target 是 __all__ / __version__（包元数据赋值）
       * Expr + Constant（docstring / 模块级字符串）
       * Pass（空语句）
       其他所有节点类型都算实质代码（ClassDef/FunctionDef/AsyncFunctionDef/
       If/For/While/Try/With/Raise/Assert/Delete/Global/Nonlocal/AugAssign/
       AnnAssign 等）

合法 re-export 场景（不阻断）：
  - __init__.py 包聚合（`from . import sub1, sub2` + `__all__`）
  - TTL=task_bound + # [DEPRECATED] 标记的临时过渡 shim
  - 含实质代码的文件（class/function/非 __all__ 赋值/if 等任意语句）

真源：本文件 is_pure_reexport_shim() 函数（判定逻辑唯一真源）
规则：AGENTS.md「禁止纯 re-export shim」规则段落（描述"做什么"，不描述"怎么做"）
病根分析：docs/_working/ 下治本漏洞1调研报告
"""

from __future__ import annotations

import sys
from pathlib import Path

# bootstrap sys.path —— 包外消费者一次性极简 bootstrap
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, EXIT_PASS

__manifest__ = """
args:
- --ci
- --warn-only
description: GATE-NO-PURE-SHIM - 检测纯 re-export shim 文件（跨包 from zephyr.shared.* import + 无实质代码）
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""

import ast


def is_pure_reexport_shim(filepath: Path, content: str) -> tuple[bool, str]:
    """检测文件是否为纯 re-export shim。

    返回 (is_shim, reason)。
    """
    # 例外1: __init__.py 包聚合豁免
    if filepath.name == "__init__.py":
        return False, "__init__.py 包聚合豁免"

    # 例外2: TTL=task_bound + DEPRECATED 标记豁免（临时过渡 shim）
    if "# [TTL] task_bound" in content and "# [DEPRECATED]" in content:
        return False, "临时过渡 shim（TTL=task_bound + DEPRECATED 标记）"

    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return False, "语法错误，跳过检测"

    has_cross_pkg_reexport = False
    has_substantial_code = False

    # 白名单方式：只允许特定的非实质节点，其他都算实质代码（防绕过）
    # 红蓝对抗发现：原黑名单方式漏检 ast.Pass（pass 语句）导致绕过
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # 跨包 re-export：from zephyr.shared.* import
            if module.startswith("zephyr.shared."):
                has_cross_pkg_reexport = True
            # ImportFrom 本身不算实质代码（无论是否跨包）

        elif isinstance(node, ast.Import):
            # 普通 import 不算实质代码，也不算跨包 re-export
            pass

        elif isinstance(node, ast.Assign):
            # 仅 __all__ / __version__ 赋值不算实质代码
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("__all__", "__version__"):
                    continue
                has_substantial_code = True
                break
            if has_substantial_code:
                break

        elif isinstance(node, ast.AugAssign):
            # 增强赋值（+=, |= 等）算实质代码（如 __all__ += [...] 是动态构造）
            has_substantial_code = True
            break

        elif isinstance(node, ast.AnnAssign):
            # 带注解赋值算实质代码
            has_substantial_code = True
            break

        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            # docstring / 模块级字符串常量 / Ellipsis(...)，不算实质代码
            pass

        elif isinstance(node, ast.Pass):
            # pass 语句不算实质代码（无操作）
            pass

        else:
            # 其他节点类型（ClassDef/FunctionDef/AsyncFunctionDef/If/For/While/
            # Try/With/Raise/Assert/Delete/Global/Nonlocal 等）算实质代码
            has_substantial_code = True
            break

    if has_cross_pkg_reexport and not has_substantial_code:
        return True, "纯 re-export shim（跨包 from zephyr.shared.* import + 无实质代码）"

    return False, "非 shim"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    warn_only = "--warn-only" in args
    ci_mode = "--ci" in args or not warn_only

    # pre-commit 传入 staged 文件列表（过滤出 .py 文件）
    files = [a for a in args if not a.startswith("--")]

    if not files:
        # 无文件传入时不阻断（pre-commit 未触发）
        return EXIT_PASS

    findings: list[str] = []

    for f in files:
        filepath = Path(f)
        if not filepath.is_file():
            continue
        if filepath.suffix != ".py":
            continue

        try:
            content = filepath.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue

        is_shim, reason = is_pure_reexport_shim(filepath, content)
        if is_shim:
            findings.append(f"  BLOCKED: {f}\n    原因: {reason}")
            findings.append(
                "    治本: 删除此文件，消费者改引 canonical 路径（zephyr.shared.*）"
            )
            findings.append(
                "    规则: AGENTS.md「禁止纯 re-export shim」"
            )

    if findings:
        print("GATE-NO-PURE-SHIM: 检测到纯 re-export shim 文件", file=sys.stderr)
        print(
            "纯 re-export shim（跨包 from zephyr.shared.* import + 无实质代码）被禁止。",
            file=sys.stderr,
        )
        print(
            "理由：真源分裂温床，AI 无法确定真源产生漂移（shared_08 案例 commit 98c990141c）。",
            file=sys.stderr,
        )
        print("例外：__init__.py 包聚合 / TTL=task_bound + # [DEPRECATED] 临时过渡", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        for line in findings:
            print(line, file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        print(
            "修复：删除 shim 文件，消费者改引 canonical 路径；或添加 # [TTL] task_bound + # [DEPRECATED] 标记作为临时过渡。",
            file=sys.stderr,
        )
        if warn_only:
            print("[WARN-ONLY] 仅告警，不阻断", file=sys.stderr)
            return EXIT_PASS
        return EXIT_FINDINGS

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
