# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-RUNCOMMAND-WINDOW-FLASH-001
# [MODULE] zephyr.gov_enforcement.commit_gates.bare_subprocess_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——检测 staged .py added 行中裸 subprocess.run/Popen/check_output/check_call 调用（违反 trae_067 铁律2 CREATE_NO_WINDOW 强制）；命中返回 passed=False + detail（阻断 commit）；tests/ 豁免；6 个文件级例外（process_pool/diff_helpers/git_call_budget_gate/git_commit_gateway/bare_subprocess_gate 自身）；noqa: bare-subprocess 行级逃生；AST 精确检测；git diff 不可达 fail-open。2026-07-27 P2 升级落地（#ARCH-PREVENTABILITY-LAYER-001 第6层补齐——100% AI 场景下 warn=pass，必须 fail-closed）
# [MODIFY-GUARD] gate_id="BARE-SUBPROCESS"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True）；ast.parse 失败 fail-open；检出违规则 fail-closed 阻断（passed=False + detail）
# [TESTS] tests/governance/commit_gates/test_bare_subprocess_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: bare-subprocess  自身豁免: 本文件是BARE-SUBPROCESS检测器,源码含检测模式字符串(subprocess.run/Popen)用于AST匹配,非实际调用
"""bare_subprocess_gate.py — 裸 subprocess 调用硬阻断门禁（BARE-SUBPROCESS）

对应铁律 trae_067 RULE-EIGHTEEN-INV-001（CREATE_NO_WINDOW 强制）。
裁定 #ARCH-RUNCOMMAND-WINDOW-FLASH-001 Phase 1.6 补漏后立项（P8）。
2026-07-27 P2 升级落地：warn-only → fail-closed（#ARCH-PREVENTABILITY-LAYER-001 第6层补齐）。

病根（第一性原理）
-----------------
trae_067 铁律2 + INV-001 要求"AI 内部代码 spawn python 子进程 MUST 设
CREATE_NO_WINDOW，复用 process_pool.py"，但 enforcement.paired_gate_id=null
（君子协定）。100% AI 开发场景下 AI 上下文有限，会遗漏——本案 Phase 1.6
治本存在 55+ 处遗漏（已修复），证明君子协定不可靠。warn-only 同样不可靠：
100% AI 场景下 warn=pass（#ARCH-PREVENTABILITY-LAYER-001），AI 会忽略 warning
继续提交裸 subprocess，故 P2 升级为 fail-closed 硬阻断。

治本方案（本 gate，fail-closed P2）
---------------------------------------
1. AST 精确检测：ast.walk + ast.Attribute(attr in run/Popen/check_output/check_call)
   + func.value.id == 'subprocess'（或 import alias）
2. 只检测 added 行：存量违规由人工排查，gate 只防新增（added-lines 机制 = 事实基线，
   翻转 fail-closed 不会阻断 171 处存量）
3. fail-closed：检出违规返回 (False, detail) 阻断 commit——对标其余 5 个
   fail-closed 门禁（zephyr_env/asyncio/open/mutable-Final/mcp-version），
   补齐 #ARCH-PREVENTABILITY-LAYER-001 第6层最后一块
4. 6 个文件级例外 + noqa 行级逃生：合法保留场景（检测器自身 / process_pool
   定义点 / git_call_budget_gate AST 检测器 / git_commit_gateway 注释引用）

设计权衡
--------
1. **fail-closed（P2，2026-07-27 落地）**：检出违规阻断 commit。P1 warn-only 阶段
   已建立检测能力 + 数据收集；现升级为 block（INV-001 violation_action=reject_change）。
   只扫 added 行确保不阻断存量 171 处的 CI。
2. **AST 精确检测**：比正则更准确，天然不检测字符串/注释内的 subprocess.run 引用
3. **只检测 added 行**：存量违规由人工排查，gate 只防新增
4. **priority=108**：在 IMPORT-INTEGRITY=107 之后，CAPABILITY-LOOKUP-REQUIRED=110 之前
5. **import alias 识别**：`import subprocess as sp; sp.run(...)` 也检测

Usage::

    from zephyr.gov_enforcement.commit_gates.bare_subprocess_gate import make_bare_subprocess_gate

    registry.register(make_bare_subprocess_gate())
"""

from __future__ import annotations

import ast
import logging

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_noqa_lines,
    _get_added_lines,
    _get_staged_py_files,
    _make_noqa_pattern,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_bare_subprocess_gate"]

# 文件级豁免：定义点 / 检测器自身 / AST 检测器引用 subprocess.run 字符串
# - process_pool.py: 定义 run_subprocess_hidden / spawn_python_hidden（必然含 subprocess.run/Popen）
# - _diff_helpers.py: gate 共享 helper（_read_staged_file 内部 gateway.run_git，不直接 subprocess）
# - git_call_budget_gate.py: AST 检测器，源码含 "subprocess.run" 字符串用于检测模式
# - git_commit_gateway.py: 注释引用 "subprocess.run(["git",...])" AST 检测逻辑说明
# - bare_subprocess_gate.py: 本检测器自身
_EXEMPT_FILES = {
    "process_pool.py",
    "_diff_helpers.py",
    "git_call_budget_gate.py",
    "git_commit_gateway.py",
    "bare_subprocess_gate.py",
}

# noqa 行级逃生：对标 m10-time-trigger / m11-perm-manual-legitimate 模式
# 格式：`# noqa: bare-subprocess` + 2+ 空格 + reason（>=10 字符）
# 共享 helper（#ARCH-FORCE-MERGE-DEDUP-001 消除克隆）：正则由 _make_noqa_pattern 构造，
# 提取由 _diff_helpers._extract_noqa_lines 执行——消除与 import_integrity_gate 的逐字符克隆
_NOQA_PATTERN = _make_noqa_pattern("bare-subprocess")

# subprocess 调用方法名集合
_SUBPROCESS_CALL_ATTRS = frozenset({"run", "Popen", "check_output", "check_call"})


def _is_bare_subprocess_exempt_file(py_file: str) -> bool:  # noqa: m03-duplicate  M03豁免: 与git_call_budget_gate._is_git_budget_exempt_file共享实现模式（各gate持自身_EXEMPT_FILES常量）
    """文件级豁免：process_pool / _diff_helpers / git_call_budget_gate / git_commit_gateway / 本 gate 自身 /
    _archive 目录（归档一次性代码不参与扫描——同族先例：undefined_name_gate 裁定#E / bare_sql_gate 同口径）。"""
    normalized = py_file.replace("\\", "/")
    if "_archive" in normalized:  # 2026-08-20 波3 实证补齐
        return True
    return any(normalized.endswith(f"/{name}") or py_file == name for name in _EXEMPT_FILES)


def _collect_subprocess_aliases(tree: ast.AST) -> set[str]:
    """收集 import subprocess as <alias> 的别名集合（含 'subprocess' 自身）。

    覆盖：
      - ``import subprocess`` → {'subprocess'}
      - ``import subprocess as sp`` → {'sp'}
    """
    aliases: set[str] = {"subprocess"}  # 默认名总是有效
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    aliases.add(alias.asname or alias.name)
    return aliases


def _is_bare_subprocess_call(node: ast.AST, subprocess_aliases: set[str]) -> bool:
    """判断 AST 节点是否是 subprocess.run/Popen/check_output/check_call 调用。

    覆盖：
      - ``subprocess.run(...)`` / ``sp.run(...)`` — ast.Attribute(attr='run')
      - ``subprocess.Popen(...)`` / ``sp.Popen(...)`` — ast.Attribute(attr='Popen')
      - ``subprocess.check_output(...)`` — ast.Attribute(attr='check_output')
      - ``subprocess.check_call(...)`` — ast.Attribute(attr='check_call')

    func.value 必须是 ast.Name 且 id 在 subprocess_aliases 中。
    """
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr not in _SUBPROCESS_CALL_ATTRS:
        return False
    # func.value 必须是 Name 且 id 是 subprocess 别名
    if not isinstance(func.value, ast.Name):
        return False
    return func.value.id in subprocess_aliases


def _is_bare_subprocess_ref(node: ast.AST, subprocess_aliases: set[str]) -> bool:
    """检测 subprocess.run/Popen/check_output/check_call 作为**引用**传递（非直接调用）。

    覆盖 gate 盲区（2026-07-29 修复，#ARCH-PREVENTABILITY-LAYER-001）：
      - ``executor.submit(subprocess.run, ...)`` — subprocess.run 作为 callable 参数传递
      - ``fn = subprocess.run`` — subprocess.run 赋值给变量
      - ``callback(subprocess.Popen, ...)`` — subprocess.Popen 作为参数传递

    这类模式绕过 _is_bare_subprocess_call 的 ast.Call.func 检测，但同样会在
    Windows 上创建控制台窗口闪现（trae_067 铁律2）。

    检测逻辑：node 是 ast.Attribute 且 attr in _SUBPROCESS_CALL_ATTRS 且
    value.id in subprocess_aliases——无论 node 出现在 AST 的哪个位置。
    排除直接调用形式（由 _is_bare_subprocess_call 覆盖，避免重复报告）。
    """
    if not isinstance(node, ast.Attribute):
        return False
    if node.attr not in _SUBPROCESS_CALL_ATTRS:
        return False
    if not isinstance(node.value, ast.Name):
        return False
    return node.value.id in subprocess_aliases


def _collect_direct_call_func_ids(tree: ast.AST, subprocess_aliases: set[str]) -> set[int]:
    """收集所有直接调用 subprocess.run(...) 的 func Attribute 节点 id。

    用于排除 _is_bare_subprocess_ref 的重复报告——直接调用 ``subprocess.run(...)``
    中的 ``subprocess.run`` 是 ast.Call.func（ast.Attribute），ast.walk 会同时
    访问 Call 和 Attribute 节点，若不排除会导致同一行被报告两次（调用 + 引用传递）。
    """
    consumed: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_bare_subprocess_call(node, subprocess_aliases):
            # node.func 是 ast.Attribute，记录其 id 供 ref 检测排除
            consumed.add(id(node.func))
    return consumed


# _extract_noqa_lines 已提取至 _diff_helpers（#ARCH-FORCE-MERGE-DEDUP-001 消除克隆）
# 调用处使用 _extract_noqa_lines(file_content, _NOQA_PATTERN)


def make_bare_subprocess_gate() -> GateSpec:
    """构造裸 subprocess 调用 fail-closed GateSpec。

    Returns:
        GateSpec(gate_id="BARE-SUBPROCESS", priority=108)。
        fail-closed：检出违规返回 (False, detail)，阻断 commit。
        2026-07-27 P2 升级（warn-only → fail-closed）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f
            for f in _get_staged_py_files(gateway, "BARE-SUBPROCESS")
            if not is_test_exempt(f) and not _is_bare_subprocess_exempt_file(f)
        ]
        if not py_files:
            return True, ""

        warnings: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            if not file_content:
                continue
            added_lines = {ln for ln, _ in _get_added_lines(gateway, py_file, "BARE-SUBPROCESS")}
            if not added_lines:
                continue

            try:
                tree = ast.parse(file_content)
            except SyntaxError:
                logger.warning(
                    "BARE-SUBPROCESS: ast.parse 失败 %s（语法错误），fail-open 跳过",
                    py_file,
                    exc_info=True,
                )
                continue

            subprocess_aliases = _collect_subprocess_aliases(tree)
            noqa_lines = _extract_noqa_lines(file_content, _NOQA_PATTERN)
            # 预收集直接调用的 func Attribute 节点 id——避免 ref_pass 重复报告同一行
            direct_call_func_ids = _collect_direct_call_func_ids(tree, subprocess_aliases)

            for node in ast.walk(tree):
                # 检测 1：直接调用 subprocess.run(...)（_is_bare_subprocess_call）
                # 检测 2：引用传递 executor.submit(subprocess.run, ...)（_is_bare_subprocess_ref）
                # 两个检测器互补——_is_bare_subprocess_call 检测 ast.Call.func 位置，
                # _is_bare_subprocess_ref 检测 ast.Attribute 在任意位置（含参数传递/赋值）
                is_direct_call = _is_bare_subprocess_call(node, subprocess_aliases)
                is_ref_pass = (
                    not is_direct_call
                    and id(node) not in direct_call_func_ids
                    and _is_bare_subprocess_ref(node, subprocess_aliases)
                )
                if not is_direct_call and not is_ref_pass:
                    continue
                call_line = node.lineno
                if call_line not in added_lines:
                    continue  # 不是 added 行，放行（存量违规由人工排查）
                if call_line in noqa_lines:
                    continue  # 行级 noqa 逃生
                # 提取 attr 名称——直接调用走 node.func.attr，引用传递走 node.attr
                attr_name = node.func.attr if is_direct_call else node.attr
                violation_type = "调用" if is_direct_call else "引用传递（绕过 gate 检测）"
                warnings.append(
                    f"  {py_file}:{call_line}: 裸 subprocess.{attr_name}(...) {violation_type}"
                    f"（违反 trae_067 铁律2 CREATE_NO_WINDOW 强制）"
                )

        if warnings:
            detail = (
                "BARE-SUBPROCESS：检测到裸 subprocess.run/Popen/check_output/check_call 调用，\n"
                "  违反铁律 trae_067 RULE-EIGHTEEN-INV-001 CREATE_NO_WINDOW 强制——\n"
                "  裸 subprocess 在 Windows 上会创建控制台窗口闪现。\n"
                + "\n".join(warnings)
                + "\n-> 改用 process_pool 统一入口："
                "from zephyr.shared.infra.process_pool import run_subprocess_hidden; "
                "run_subprocess_hidden(cmd, **kwargs)"
                + "\n-> 逃生通道：行尾加 `# noqa: bare-subprocess  <reason>` 注释（reason >= 10 字符）"
            )
            logger.error("BARE-SUBPROCESS gate block:\n%s", detail)
            return False, detail  # fail-closed：passed=False 阻断 commit
        return True, ""

    return GateSpec(gate_id="BARE-SUBPROCESS", check=_check, priority=108)
