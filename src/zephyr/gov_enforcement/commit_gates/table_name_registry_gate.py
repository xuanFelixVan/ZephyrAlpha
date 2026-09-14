# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-CH-024
# [MODULE] zephyr.gov_enforcement.commit_gates.table_name_registry_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_get_staged_py_files, _get_added_lines, _read_staged_file, _extract_docstring_lines); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.data.table_registry (get_registry, TableRegistry)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] block——检测 .py added 行中的硬编码表名字符串（绕过 TableRegistry 真源）+ tasks.yaml 表名校验；命中返回 passed=False + detail（阻断 commit）；tests/豁免；docstring 行豁免；table_registry.py 自身豁免；fail-open（TableRegistry 空/不可用/git diff 不可达不阻断）；Phase 5 已升级为 block；own-scope（宪法 §3.3）：优先本次 commit files 清单，无清单退回全 staged（他会话 staged 文件不连坐）
# [MODIFY-GUARD] gate_id="TABLE-NAME-REGISTRY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——TableRegistry/git diff/YAML 异常降级为 fail-open（passed=True）
# [TESTS] tests/governance/commit_gates/test_table_name_registry_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
table_name_registry_gate.py — TABLE-NAME-REGISTRY block 门禁

裁定 #ARCH-CH-024 Phase 4：SSoT 真源强制闭环。

第一性原理根因（SSoT 真源三重闭环模型）
----------------------------------------
真源治理的三重闭环：
  1. 声明闭环——真源文件存在（business_data_categories.yaml，99 条品类）✅ 已建立
  2. 消费闭环——代码 import/读取真源派生数据 ✅ Phase 2 已建立（TableRegistry）
  3. 强制闭环——commit gate 阻断绕过真源的代码 ❌ 缺失 → 本 gate 建立

表名是"声明态规则数据"（trae_062 SSoT 分类铁律），真源是 YAML 而非 DB 实例态。
Phase 2 已建立消费闭环（TableRegistry + scheduler WARN 校验），但代码中仍有
约 240 处硬编码表名字符串绕过真源，且无 commit gate 强制消费。

检测模式
--------
1. **防蔓延检测（diff-based）**：staged .py（非 test）added 行 → AST Constant
   字符串值匹配注册表名（精确匹配=直接硬编码；子串匹配=SQL 含表名）→ WARN
   "use TableRegistry.table()"。只检测 added 行，不处理存量（对标
   BLUEPRINT-FORMAT gate "Phase 0 防蔓延"模式）。
2. **tasks.yaml 校验**：tasks.yaml 被 staged 时 → TableRegistry.validate_tasks_yaml
   → WARN 未注册表名（双真源漂移风险）。

设计权衡
--------
1. **block**（Phase 5 升级）：约 240 处存量硬编码已在 Phase 5 批量替换完毕，
   gate 从 warn-only 升级为 block，阻断新增硬编码表名（对标 #ARCH-CH-022 渐进式模式）。
2. **diff-based**：只检测 added 行；新文件全行 added 故必被检查；modified
   文件仅当含表名的行被改动时才检查（存量违规由 Phase 5 批量替换处理）。
3. **AST 精确检测**：只检查 ast.Constant 字符串节点，不检查注释/变量名
   （对标 bare_subprocess_gate.py AST 精确检测模式）。
4. **精确+子串双匹配**：精确匹配捕获 ``TABLE = "c1_market.kline_daily"``；
   子串匹配捕获 ``sql = "SELECT * FROM c1_market.kline_daily"``。
5. **fail-open**：TableRegistry 空/不可用 → 不阻断（开发环境友好）。
6. **priority=120**：紧接 ISSUE-RESOLVED-INTEGRITY(117)/STASH-ACCUMULATION(118)/
   NOQA-DENSITY(119)，作为最新 block gate。

Usage::

    from zephyr.gov_enforcement.commit_gates.table_name_registry_gate import (
        make_table_name_registry_gate,
    )
    registry.register(make_table_name_registry_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: gateway 参数
#   fields: 参数 gateway（无注解）
#   code: table_name_registry_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: py_file 参数
#   fields: 参数 py_file，类型注解 str
#   code: table_name_registry_gate.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: registered_tables 参数
#   fields: 参数 registered_tables，类型注解 set[str]
#   code: table_name_registry_gate.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: table_name_pattern 参数
#   fields: 参数 table_name_pattern，类型注解 re.Pattern | None
#   code: table_name_registry_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① check_hardcoded_tables_in_file
#   name_en: check_hardcoded_tables_in_file
#   intro: 检测单个 staged .py 文件 added 行中的硬编码表名。
#   desc: 检测单个 staged .py 文件 added 行中的硬编码表名。 diff-based 检测：只检查 added 行中的 ast.Constant 字符串节点。 精确匹配=直…；源码 L178-L233
#   inputs: gateway py_file registered_tables table_name_pattern
#   outputs: list[str]
# - id: A2
#   name_zh: ② check_tasks_yaml_tables
#   name_en: check_tasks_yaml_tables
#   intro: 校验 staged tasks.yaml 的表名是否在 TableRegistry 注册。
#   desc: 校验 staged tasks.yaml 的表名是否在 TableRegistry 注册。 Args: gateway: GitCommitGateway 实例。 registr…；源码 L236-L267
#   inputs: gateway registry
#   outputs: list[str]
# - id: A3
#   name_zh: ③ make_table_name_registry_gate
#   name_en: make_table_name_registry_gate
#   intro: 构造 TABLE-NAME-REGISTRY pre-commit block 门禁（priority=120）。
#   desc: 构造 TABLE-NAME-REGISTRY pre-commit block 门禁（priority=120）。 检测 staged .py added 行中的硬编码表名（绕过…；源码 L270-L333
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# - id: O2
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import ast
import logging
import re

from zephyr.data.table_registry import TableRegistry, get_registry
from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _get_added_lines,
    _get_staged_py_files,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = [
    "make_table_name_registry_gate",
    "check_hardcoded_tables_in_file",
    "check_tasks_yaml_tables",
]

# tasks.yaml 真源路径（Phase 4 Detection 2 触发条件）
_TASKS_YAML_REL = "src/zephyr/data/config/tasks.yaml"

# 豁免文件：table_registry.py 自身（构建映射，合法引用表名）
# table_name_registry_gate.py 自身（gate 逻辑引用表名）
_EXEMPT_SUFFIXES = (
    "table_registry.py",
    "table_name_registry_gate.py",
)
# DDL-as-Code 真源豁免（#ARCH-CH-024 补丁 2026-09-12）：schemas/categories/（含子簇）下的表
# 结构定义文件必然含字面 CREATE TABLE 表名——鸡生蛋（TableRegistry 从 business_data_categories
# .yaml 读表名，YAML 的 schema_file 又指向 DDL 文件）。语义边界：DDL 定义/部署脚本（apply_*_ddl
# .py）的 writer CREATE 合法（同 CH-FINAL-GATE apply 豁免先例）；业务代码读表仍 MUST 走
# TableRegistry.table() 派生。
_DDL_SCHEMA_EXEMPT = ("schemas/categories/", "apply_")
_DDL_SCHEMA_EXEMPT_SUFFIX = "_ddl.py"


def _is_ddl_schema_exempt(rel_path: str) -> bool:
    """DDL 真源/部署脚本豁免：schemas/categories/ 树内文件 或 apply_*_ddl.py 部署脚本。"""
    normalized = rel_path.replace("\\", "/")
    if normalized.endswith(_DDL_SCHEMA_EXEMPT_SUFFIX):
        return True
    return any(seg in normalized for seg in _DDL_SCHEMA_EXEMPT[:1])


def _build_table_name_pattern(registered_tables: set[str]) -> re.Pattern | None:
    """构建表名子串匹配正则（按长度降序避免短名误匹配）。

    Args:
        registered_tables: 已注册全限定表名集合（如 {"c1_market.kline_daily", ...}）。

    Returns:
        编译后的正则；空集合返回 None。
    """
    if not registered_tables:
        return None
    sorted_tables = sorted(registered_tables, key=len, reverse=True)
    return re.compile("|".join(re.escape(t) for t in sorted_tables))


def check_hardcoded_tables_in_file(
    gateway,
    py_file: str,
    registered_tables: set[str],
    table_name_pattern: re.Pattern | None,
) -> list[str]:
    """检测单个 staged .py 文件 added 行中的硬编码表名。

    diff-based 检测：只检查 added 行中的 ast.Constant 字符串节点。
    精确匹配=直接硬编码表名；子串匹配=SQL 字符串含表名。

    Args:
        gateway: GitCommitGateway 实例。
        py_file: 文件相对路径（正斜杠）。
        registered_tables: 已注册全限定表名集合。
        table_name_pattern: 表名子串匹配正则。

    Returns:
        违规警告消息列表（空=通过）。
    """
    file_content = _read_staged_file(gateway, py_file)
    if not file_content:
        return []

    added_line_set = {ln for ln, _ in _get_added_lines(gateway, py_file, "TABLE-NAME-REGISTRY")}
    if not added_line_set:
        return []

    docstring_lines = _extract_docstring_lines(file_content)

    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        return []

    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if node.lineno not in added_line_set:
            continue
        if node.lineno in docstring_lines:
            continue
        value = node.value
        # 精确匹配：直接硬编码表名
        if value in registered_tables:
            violations.append(f"  {py_file}:{node.lineno}: 硬编码表名 '{value}' -> use TableRegistry.table()")
            continue
        # 子串匹配：SQL 字符串含表名
        if table_name_pattern is not None:
            matches = table_name_pattern.findall(value)
            if matches:
                violations.append(
                    f"  {py_file}:{node.lineno}: 字符串含硬编码表名 {set(matches)} -> use TableRegistry.table()"
                )
    return violations


def check_tasks_yaml_tables(
    gateway,
    registry: TableRegistry,
) -> list[str]:
    """校验 staged tasks.yaml 的表名是否在 TableRegistry 注册。

    Args:
        gateway: GitCommitGateway 实例。
        registry: TableRegistry 实例（SSoT 消费层）。

    Returns:
        违规警告消息列表（空=通过）。
    """
    content = _read_staged_file(gateway, _TASKS_YAML_REL)
    if not content:
        return []

    try:
        import yaml

        data = yaml.safe_load(content)
    except Exception:  # noqa: BLE001 — fail-open
        return []

    if not isinstance(data, dict):
        return []

    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        return []

    return registry.validate_tasks_yaml(tasks)


def _to_rel_posix(gateway, path: str) -> str:
    """任意路径 → 仓库根相对 posix 路径（保留大小写，供 git show :path 用）。

    与 _diff_helpers._norm_rel 的区别：不做 normcase 小写化——git index 路径
    大小写敏感，normcase 后的路径会让 git show :path 误查失败致 gate 静默空转。
    """
    p = str(path).replace("\\", "/")
    try:
        root = str(getattr(gateway, "project_root", "") or "")
        if root and not p.startswith(root.replace("\\", "/") + "/"):
            import os

            if os.path.isabs(str(path)):
                p = os.path.relpath(str(path), root).replace("\\", "/")
        elif root and p.startswith(root.replace("\\", "/") + "/"):
            p = p[len(root.replace("\\", "/")) + 1 :]
    except Exception:  # noqa: BLE001 — 归一化失败退回原值（fail-open）
        p = str(path).replace("\\", "/")
    return p


def make_table_name_registry_gate() -> GateSpec:
    """构造 TABLE-NAME-REGISTRY pre-commit block 门禁（priority=120）。

    检测 staged .py added 行中的硬编码表名（绕过 TableRegistry 真源）+
    tasks.yaml 表名校验。命中返回 (False, detail) 阻断 commit。

    裁定 #ARCH-CH-024 Phase 4：建立 SSoT 真源强制闭环（warn-only 数据收集）。
    Phase 5 升级为 block（passed=False）：约 240 处存量硬编码已批量替换完毕，
    gate 阻断新增硬编码表名。

    Returns:
        GateSpec(gate_id="TABLE-NAME-REGISTRY", priority=120)。
        block：检出违规返回 (False, detail)，阻断 commit。
    """

    def _check(gateway, files: list[str], **_kwargs) -> tuple[bool, str]:
        # 加载 TableRegistry（SSoT: business_data_categories.yaml）
        try:
            registry = get_registry()
            registered_tables = set(registry.all_tables())
        except Exception:  # noqa: BLE001 — fail-open
            logger.warning("TABLE-NAME-REGISTRY fail-open: TableRegistry 加载失败")
            return True, ""

        if not registered_tables:
            return True, ""  # fail-open: 空注册表

        table_name_pattern = _build_table_name_pattern(registered_tables)
        warnings: list[str] = []

        # Detection 1: 防蔓延——.py added 行硬编码表名（own-scope 接续
        # #ARCH-GATE-OWN-SCOPE-001 推广批 + 宪法 §3.3：优先本次 commit files 清单，
        # 无清单退回全 staged 旧行为——他会话 staged 文件不再连坐阻断本次提交）
        if files:
            py_candidates = []
            for f in files:
                rel = _to_rel_posix(gateway, f)
                if not rel.endswith(".py"):
                    continue
                if is_test_exempt(rel) or rel.endswith(_EXEMPT_SUFFIXES) or _is_ddl_schema_exempt(rel):
                    continue
                py_candidates.append(rel)
        else:
            py_candidates = [
                f
                for f in _get_staged_py_files(gateway, "TABLE-NAME-REGISTRY")
                if not is_test_exempt(f) and not f.endswith(_EXEMPT_SUFFIXES) and not _is_ddl_schema_exempt(f)
            ]
        for py_file in py_candidates:
            warnings.extend(check_hardcoded_tables_in_file(gateway, py_file, registered_tables, table_name_pattern))

        # Detection 2: tasks.yaml 表名校验
        normalized_files = [f.replace("\\", "/") for f in files]
        if _TASKS_YAML_REL in normalized_files:
            warnings.extend(check_tasks_yaml_tables(gateway, registry))

        if warnings:
            detail = (
                "TABLE-NAME-REGISTRY (block)：检测到硬编码表名绕过"
                " TableRegistry 真源（#ARCH-CH-024 Phase 5 治本）\n"
                "  病根：SSoT 真源强制闭环被绕过——代码硬编码表名字符串"
                "绕过 business_data_categories.yaml 真源。\n"
                "  修复：将硬编码表名替换为 TableRegistry.table(category_id)"
                " 常量引用。\n"
                + "\n".join(warnings[:30])
                + (f"\n  ...(+{len(warnings) - 30} more)" if len(warnings) > 30 else "")
            )
            logger.error("TABLE-NAME-REGISTRY gate block:\n%s", detail)
            return False, detail  # block：passed=False 阻断 commit
        return True, ""

    return GateSpec(
        gate_id="TABLE-NAME-REGISTRY",
        check=_check,
        priority=120,
    )


if __name__ == "__main__":
    """CLI 入口——手动验证 gate 是否可正确构造。"""
    g = make_table_name_registry_gate()
    print(f"gate_id={g.gate_id}, priority={g.priority}, check_callable={callable(g.check)}")
