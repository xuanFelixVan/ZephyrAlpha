# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.domain_name_zh_direct_access_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 DOMAIN_NAME_ZH 字典直接访问(.get(/[/pop/items/keys/values)时阻断 commit(passed=False)；定义文件 domain_name_mapping.py 豁免(SSoT 定义位置)；tests/ 豁免；import/注释/docstring 行豁免；git diff 不可达 fail-open(logger.warning)；检出违规则 fail-closed(passed=False)
# [MODIFY-GUARD] gate_id="NO-DOMAIN-NAME-ZH-DIRECT-ACCESS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_domain_name_zh_direct_access_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""
domain_name_zh_direct_access_gate.py — DOMAIN_NAME_ZH 字典直接访问硬阻断门禁

检测 staged .py 文件 added 行中是否直接访问 ``DOMAIN_NAME_ZH`` 字典
（如 ``DOMAIN_NAME_ZH.get(...)`` / ``DOMAIN_NAME_ZH[...]`` / ``DOMAIN_NAME_ZH.pop(...)`` 等）。
命中则硬阻断 commit，提示改走 ``get_domain_name_zh()`` / ``get_domain_name_zh_strict()`` helper。

病根（第一性原理，2026-07-19 Step 2.5 治本遗留风险修复）
------------------------------------------------------
v2.3 治本把 ``DOMAIN_NAME_ZH`` 从 73 entry 瘦身为 10 entry（仅测试域），
生产域中文名真源统一归 DB。``generate_domain_doc.py`` 中原 6 处直接访问
``DOMAIN_NAME_ZH.get(...)`` 已全部改走 ``get_domain_name_zh_strict()`` helper。

但**无门禁强制阻止新 AI 重新引入直接访问**——君子协定。
新 AI 可能在新文件或现有文件中写 ``DOMAIN_NAME_ZH.get(ext, "")`` 绕过 DB 优先级，
导致：①生产域走硬编码 fallback（DB 不可用时返回 domain_id）；②绕过 helper 的
strict/非strict 语义区分；③重构后 DOMAIN_NAME_ZH 已不再含生产域，直接访问
会返回空或 domain_id，破坏中文显示。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 过滤 tests/ 豁免 + SSoT 定义文件豁免
  3. 对每个文件解析 diff，检查 added 行是否含 ``DOMAIN_NAME_ZH.<dict_method>``
     或 ``DOMAIN_NAME_ZH[`` 模式
  4. 豁免 import/注释/docstring 行
  5. 命中 -> 硬阻断，提示改走 helper

设计权衡
--------
1. **只检测 added 行**：存量直接访问由人工排查，gate 只防新增。
2. **diff-based 检测**：与 hardcoded_url_gate / bare_sql_gate 一致的检测模式。
3. **正则匹配 dict 访问模式**：``DOMAIN_NAME_ZH\b\s*(?:\.|\[)`` 覆盖
   ``.get()`` / ``.pop()`` / ``.items()`` / ``.keys()`` / ``.values()`` / ``[key]``。
4. **SSoT 定义文件豁免**：``domain_name_mapping.py`` 是 ``DOMAIN_NAME_ZH`` 的
   合法定义位置，其内部访问（如 ``DOMAIN_NAME_ZH.get(domain_id, ...)``）是合法的。
5. **priority=72**：SSoT 防护族——原计划 priority=67 紧跟 SSOT-REDEFINITION(65) +
   UNSAFE-DICT-SPREAD(66)，但 67 已被 depgraph_freshness_gate 占用。
   治本（避免 priority 冲突 WARNING）：迁移到 72（noqa_validation(71) 与
   ruling_reference(74) 之间的空闲 slot），符合团队"priority 唯一"约定
   （参见 id_uniqueness 86→89 撞号治本先例）。

Usage::

    from zephyr.gov_enforcement.commit_gates.domain_name_zh_direct_access_gate import make_domain_name_zh_direct_access_gate

    registry.register(make_domain_name_zh_direct_access_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: domain_name_zh_direct_access_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_domain_name_zh_direct_access_gate
#   name_en: make_domain_name_zh_direct_access_gate
#   intro: 构造 DOMAIN_NAME_ZH 字典直接访问阻断 GateSpec（硬阻断型）。
#   desc: 构造 DOMAIN_NAME_ZH 字典直接访问阻断 GateSpec（硬阻断型）。 Returns: GateSpec(gate_id="NO-DOMAIN-NAME-ZH-D…；源码 L183-L215
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _is_exempt_line,
    _parse_diff_with_line_numbers,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_domain_name_zh_direct_access_gate"]

# DOMAIN_NAME_ZH 字典定义位置（SSoT 真源文件，合法直接访问）
_SSoT_EXEMPT_FILE = "scripts/governance/d5_architecture/generators/domain_name_mapping.py"

# 匹配 DOMAIN_NAME_ZH 字典直接访问：
# - DOMAIN_NAME_ZH.get(...)   / .pop(...) / .items() / .keys() / .values() / .update(...)
# - DOMAIN_NAME_ZH[key]
# 用 \b 词边界 + \s* 可选空白，避免匹配 DOMAIN_NAME_ZH_X 等扩展名
# 注意：不匹配 ``DOMAIN_NAME_ZH = {...}``（定义行），因 SSoT 文件已豁免，其他文件
# 重新定义 DOMAIN_NAME_ZH 会被 SSOT-REDEFINITION gate (priority=65) 拦截，无需重复。
_DIRECT_ACCESS_RE = re.compile(r"\bDOMAIN_NAME_ZH\b\s*(?:\.|\[)")


def _collect_staged_py_files(gateway):
    """获取 staged .py 文件列表（过滤 tests/ + SSoT 豁免）。

    None=fail-open(git diff 不可达)。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None

    # 过滤 .py 文件 + tests/ 豁免 + SSoT 定义文件豁免
    py_files = [f for f in staged if f.endswith(".py") and not is_test_exempt(f) and f != _SSoT_EXEMPT_FILE]
    return py_files


def _scan_file_violations(gateway, py_file):
    """扫描单个文件的 added 行，返回违规列表 [(file, line_no, content)]。"""
    # 预计算 docstring 行号集合
    file_content = _read_staged_file(gateway, py_file)
    docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

    # 解析 diff，获取 added 行及行号
    try:
        file_diff = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", py_file])
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS gate: git diff 失败 file=%s, %s",
            py_file,
            e,
        )
        return []
    if file_diff.returncode != 0:
        return []

    added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
    violations = []
    for line_no, content in added_lines:
        # 豁免：docstring 内的行
        if line_no in docstring_lines:
            continue
        # 豁免：注释 / import
        if _is_exempt_line(content):
            continue
        if _DIRECT_ACCESS_RE.search(content):
            violations.append(f"  {py_file}:{line_no}: {content.strip()}")
    return violations


def make_domain_name_zh_direct_access_gate() -> GateSpec:
    """构造 DOMAIN_NAME_ZH 字典直接访问阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-DOMAIN-NAME-ZH-DIRECT-ACCESS", priority=72)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = _collect_staged_py_files(gateway)
        if not py_files:
            return True, ""

        violations: list[str] = []
        for py_file in py_files:
            violations.extend(_scan_file_violations(gateway, py_file))

        if violations:
            detail = (
                "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS：检测到 DOMAIN_NAME_ZH 字典直接访问，\n"
                "  违反 v2.3 治本后的 SSoT 原则——DOMAIN_NAME_ZH 仅含测试域 fallback，\n"
                "  生产域中文名真源在 DB（通过 sync_yaml_to_depgraph.py 从 YAML 同步）。\n"
                "  直接访问绕过 DB 优先级，且 DOMAIN_NAME_ZH 已不含生产域，会返回空或 domain_id。\n"
                + "\n".join(violations)
                + "\n-> 改用 from domain_name_mapping import get_domain_name_zh / get_domain_name_zh_strict\n"
                "   （get_domain_name_zh：未找到返回 fallback/domain_id；\n"
                "    get_domain_name_zh_strict：未找到返回 ''，用于 mermaid 标签/表格单元格）"
            )
            logger.error("NO-DOMAIN-NAME-ZH-DIRECT-ACCESS gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="NO-DOMAIN-NAME-ZH-DIRECT-ACCESS", check=_check, priority=72)
