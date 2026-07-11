# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.bare_sql_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.commit_gates._diff_helpers; zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含裸SQL字面量(SELECT/INSERT INTO/UPDATE SET/DELETE FROM)时阻断commit(passed=False); tests/豁免; docstring/注释/import/SQL_*常量定义行豁免（R96 用 ast 精确识别多行常量定义范围，替代旧正则近似只豁免定义行）; git diff不可达fail-open; 检出违规则fail-closed
# [MODIFY-GUARD] gate_id="NO-BARE-SQL"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_bare_sql_gate.py
# [A_module] module_id=MOD-GOV-bare_sql_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BARE-SQL，§5.160.2 防复发）

检测 staged .py 文件 added 行中的裸 SQL 字面量。
违反 §5.160 SQL 集中化原则。

病根（第一性原理）
-----------------
architecture_debt §5.160.2：apply_depgraph.py 174处裸SQL + file_task_mapper.py 13条SQL。
修复需 SQL 常量集中化专项。但新 AI 仍可能写新的裸SQL——本 gate 在 commit 阶段硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免
  3. 对每个文件解析 diff，检查 added 行是否含 SQL 字面量
  4. 豁免 docstring / 注释 / import 行
  5. 命中 -> 硬阻断

设计权衡
--------
1. **只检测 added 行**：存量裸SQL由人工排查，gate 只防新增。
2. **diff-based**：与 hardcoded_url_gate 一致的检测模式。
3. **正则匹配**：覆盖 SELECT...FROM / INSERT INTO / UPDATE...SET / DELETE FROM。
4. **priority=87**：在 NO-LONG-PARAM-LIST(88) 之后，EXEMPT-ZONE-FM(87) 同级。

Usage::

    from zephyr.governance.commit_gates.bare_sql_gate import make_bare_sql_gate

    registry.register(make_bare_sql_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.governance.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _extract_sql_constant_lines,
    _get_added_lines,
    _get_staged_py_files,
    _is_exempt_line,
    _read_staged_file,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_bare_sql_gate"]

# 匹配字符串字面量中的 SQL DML 语句
# 覆盖 SELECT...FROM / INSERT [OR <conflict>] INTO / UPDATE...SET / DELETE FROM
# 修正（R94）：旧正则 SELECT\s+\S+\s+FROM 中 \S+ 只匹配单个非空白 token，
# 无法覆盖多列 SELECT(col1,col2 FROM)/DISTINCT/COUNT(DISTINCT)等常见模式。
# 改用 \b.*?\b 词边界匹配，并启用 DOTALL 以覆盖跨行 SQL 字面量。
# 修正（R97）：INSERT\s+INTO\b 漏检 SQLite 冲突解决子句变体
# (INSERT OR IGNORE/REPLACE/ABORT/FAIL/ROLLBACK INTO)，
# 改用 INSERT(?:\s+OR\s+\w+)?\s+INTO\b 可选匹配 OR <word> 子句。
# 注意：正则定义必须在单行内（_SQL_PATTERN = re.compile(...)），否则
# 续行中的 SQL 关键词会被 gate 自身检测到。
# SQL_* 常量定义行豁免由 _diff_helpers._extract_sql_constant_lines 用 ast
# 精确识别（R96 治本），替代旧 _SQL_CONSTANT_DEF_RE 正则近似。
# fmt: off
_SQL_PATTERN = re.compile(r"""['"`].*?(?:SELECT\b.*?\bFROM\b|INSERT(?:\s+OR\s+\w+)?\s+INTO\b|UPDATE\b.*?\bSET\b|DELETE\s+FROM\b)""", re.IGNORECASE | re.DOTALL)
# fmt: on


def make_bare_sql_gate() -> GateSpec:
    """构造裸SQL字面量阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-BARE-SQL", priority=87)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [f for f in _get_staged_py_files(gateway, "NO-BARE-SQL") if not is_test_exempt(f)]
        violations: list[str] = []
        for py_file in py_files:
            file_content = _read_staged_file(gateway, py_file)
            docstring_lines = _extract_docstring_lines(file_content) if file_content else set()
            sql_const_lines = _extract_sql_constant_lines(file_content) if file_content else set()
            for line_no, content in _get_added_lines(gateway, py_file, "NO-BARE-SQL"):
                if line_no in docstring_lines or _is_exempt_line(content):
                    continue
                if line_no in sql_const_lines:
                    continue
                if _SQL_PATTERN.search(content):
                    violations.append(f"  {py_file}:{line_no}: {content.strip()}")
        if violations:
            detail = (
                "NO-BARE-SQL：检测到裸 SQL 字面量，\n"
                "  违反 §5.160.2 SQL 集中化原则。\n"
                + "\n".join(violations)
                + "\n-> 将 SQL 提取到模块级常量或专用的 SQL 集中化文件"
            )
            logger.error("NO-BARE-SQL gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="NO-BARE-SQL", check=_check, priority=87)
