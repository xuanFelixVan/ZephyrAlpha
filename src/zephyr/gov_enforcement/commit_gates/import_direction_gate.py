# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.import_direction_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged shared 层 .py 文件含向上依赖 import（from zephyr.trading/governance/integration/infrastructure...）时阻断 commit（passed=False）；tests/ 豁免；TYPE_CHECKING 块内 import 豁免（类型检查专用无运行时导入）；AST/git 异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="NO-UPWARD-IMPORT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_import_direction_gate.py
# [A_module] module_id=MOD-GOV-import_direction_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""import_direction_gate.py — shared 层向上依赖阻断门禁（NO-UPWARD-IMPORT，§5.152 防复发）

检测 staged shared 层（src/zephyr/shared/）.py 文件中是否含向上依赖 import——
违反架构分层原则（L0 shared 禁止依赖 L2 governance / L3 trading / L1 integration 等
上层域），是 5.152 类型真源下沉修复的防复发门禁。

病根（第一性原理）
-----------------
architecture_debt §5.152：shared 层（L0）向上 import trading/governance 等上层域
枚举/类型，导致底层→上层的违规依赖。修复方式是将跨切面类型从业务域下沉到 shared 层。
但新 AI 仍可能在 shared 层文件中写新的向上 import——本 gate 在 commit 阶段硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤到 shared 层文件（路径含 src/zephyr/shared/）
  3. AST 解析，收集 if TYPE_CHECKING 块内的 ImportFrom 节点（豁免集）
  4. 遍历所有 ImportFrom 节点，排除 TYPE_CHECKING 豁免集后检查 module 前缀
  5. module 以 zephyr.trading / zephyr.governance / zephyr.integration /
     zephyr.infrastructure / zephyr.intelligence / zephyr.backtest /
     zephyr.portfolio / zephyr.risk / zephyr.signal 等上层域开头 -> 违规

设计权衡
--------
1. **只检测 shared 层文件**：向上依赖只在 shared→上层时违规，上层→上层不检测。
2. **TYPE_CHECKING 豁免**：if TYPE_CHECKING: 块内的 import 是类型检查专用，
   无运行时导入，不构成向上依赖。用 AST 收集 TYPE_CHECKING If 节点的后代 ImportFrom。
3. **只检测 ImportFrom**：``from zephyr.trading.xxx import YYY`` 是主要违规模式。
   ``import zephyr.trading.xxx`` 极罕见，暂不检测（可后续扩展）。
4. **fail-open on AST error**：语法错误文件不阻断（由其他 gate 管语法）。
5. **priority=93**：在现有 gate 之后（最高 92），作为架构方向性 gate。

Usage::

    from zephyr.gov_enforcement.commit_gates.import_direction_gate import make_import_direction_gate

    registry.register(make_import_direction_gate())
"""

from __future__ import annotations

import ast
import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_import_direction_gate"]

# shared 层路径标识
_SHARED_PATH_PART = "src/zephyr/shared/"

# 禁止的向上依赖前缀（L0 shared 不可依赖的上层域）
_UPWARD_PREFIXES = (
    "zephyr.trading",
    "zephyr.governance",
    "zephyr.integration",
    "zephyr.infrastructure",
    "zephyr.intelligence",
    "zephyr.backtest",
    "zephyr.portfolio",
    "zephyr.risk",
    "zephyr.signal",
    "zephyr.autonomy",
    "zephyr.data_eng",
    "zephyr.reporting",
    "zephyr.frontend",
    "zephyr.knowledge",
    "zephyr.ml_train",
    "zephyr.ml_serve",
    "zephyr.security",
    "zephyr.ops",
)


def _collect_type_checking_imports(tree: ast.Module) -> set[int]:
    """收集 if TYPE_CHECKING: 块内所有 ImportFrom 节点的 id（用于豁免）。

    遍历 If 节点，判定 test 是否为 TYPE_CHECKING（Name(id="TYPE_CHECKING")
    或 Attribute(value=Name(id="typing"), attr="TYPE_CHECKING")）。
    对匹配的 If 节点，收集其所有后代 ImportFrom 的 id()。
    """
    exempt_ids: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        is_tc = False
        # if TYPE_CHECKING:
        if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
            is_tc = True
        # if typing.TYPE_CHECKING:
        elif (isinstance(test, ast.Attribute)
              and test.attr == "TYPE_CHECKING"
              and isinstance(test.value, ast.Name)
              and test.value.id == "typing"):
            is_tc = True
        if not is_tc:
            continue
        # 收集该 If 块内所有 ImportFrom 的 id
        for child in ast.walk(node):
            if isinstance(child, ast.ImportFrom):
                exempt_ids.add(id(child))
    return exempt_ids


def make_import_direction_gate() -> GateSpec:
    """构造 shared 层向上依赖阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-UPWARD-IMPORT", priority=93)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "NO-UPWARD-IMPORT gate fail-open: git diff 失败(rc=%d)。",
                    diff_result.returncode,
                )
                return True, ""
            staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
        except Exception as e:
            logger.warning(
                "NO-UPWARD-IMPORT gate fail-open: git diff 异常(%s: %s)。",
                type(e).__name__, e, exc_info=True,
            )
            return True, ""

        # 2. 过滤到 shared 层 .py 文件 + tests/ 豁免
        shared_files = [
            f for f in staged
            if f.endswith(".py")
            and _SHARED_PATH_PART in f
            and not is_test_exempt(f)
        ]
        if not shared_files:
            return True, ""

        # 3. 获取 worktree root
        try:
            toplevel_result = gateway._run_git(["git", "rev-parse", "--show-toplevel"])
            wt_root = toplevel_result.stdout.strip() if toplevel_result.returncode == 0 else str(gateway.project_root)
        except Exception:
            wt_root = str(gateway.project_root)

        # 4. 解析为绝对路径
        abs_files = []
        for rel in shared_files:
            p = rel if os.path.isabs(rel) else os.path.join(wt_root, rel.replace("/", os.sep))
            if os.path.isfile(p):
                abs_files.append(p)
        if not abs_files:
            return True, ""

        # 5. AST 检测
        all_violations: list[str] = []
        for abs_path in abs_files:
            try:
                content = open(abs_path, "r", encoding="utf-8", errors="replace").read()
            except OSError as e:
                logger.warning("NO-UPWARD-IMPORT gate skip %s: %s", abs_path, e)
                continue

            try:
                tree = ast.parse(content, filename=abs_path)
            except SyntaxError as e:
                logger.warning("NO-UPWARD-IMPORT gate skip %s: AST 解析失败(%s)", abs_path, e)
                continue

            # 收集 TYPE_CHECKING 块内的 import（豁免集）
            exempt_ids = _collect_type_checking_imports(tree)

            # 遍历所有 ImportFrom，排除豁免集
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if id(node) in exempt_ids:
                    continue
                module = node.module or ""
                if any(module.startswith(prefix) for prefix in _UPWARD_PREFIXES):
                    rel_name = os.path.relpath(abs_path, wt_root).replace("\\", "/")
                    names = ", ".join(a.name for a in node.names)
                    all_violations.append(
                        f"{rel_name}:{node.lineno} from {module} import {names} "
                        f"—— shared 层禁止向上依赖（§5.152）"
                    )

        if all_violations:
            detail = "; ".join(all_violations[:5])
            return False, f"shared 层向上依赖 import（§5.152 防复发）: {detail}"
        return True, ""

    return GateSpec(gate_id="NO-UPWARD-IMPORT", check=_check, priority=93)
