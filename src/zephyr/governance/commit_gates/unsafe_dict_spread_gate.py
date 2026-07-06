# [BLUEPRINT] MOD-GOV-commit_gates | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] zephyr.governance.commit_gates.unsafe_dict_spread_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn 级（passed=True 不阻断，仅 stderr+logger 告警）——检测 staged .py 新增行中 SomeClass(**varname) 直接展开模式，varname 来自反序列化（json.loads/yaml.safe_load/DB row）时遇 schema 演进会 TypeError；合法模式豁免：**kwargs/**kwds（显式关键字参数透传）、**filter_dataclass_fields(...)（已用 SSoT 过滤，5.147.12）、**{...}（字典字面量）、**func(...)（函数调用，正则不匹配）；tests/ 豁免；import/注释/docstring 豁免；YAML/git diff 不可达 fail-open（logger.warning 检测器失效）
# [MODIFY-GUARD] gate_id="UNSAFE-DICT-SPREAD"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（不阻断、不告警、logger.warning 记录检测器失效）
# [TESTS] tests/governance/commit_gates/test_unsafe_dict_spread_gate.py
# [A_module] module_id=MOD-GOV-unsafe_dict_spread_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""unsafe_dict_spread_gate.py — ``**data`` 直接展开模式 warn 级门禁

检测 staged .py 文件新增行中的 ``SomeClass(**varname)`` 直接展开模式（5.147.12 同族防复发）。

病根（5.147.5 / 5.147.12 审核发现）:
- ``SomeClass(**data)`` 中 ``data`` 来自 ``json.loads`` / ``yaml.safe_load`` / DB row
- 当 schema 演进（字段新增/删除/重命名）时，旧持久化数据展开会触发 ``TypeError``
- Pydantic ``BASE_CONFIG`` 含 ``extra="forbid"`` 同样硬拒未知字段
- 5.147.12 已用 SSoT ``filter_dataclass_fields(cls, data)`` 修复 13 处存量债务
- 但新 AI 写新功能时若不自觉，仍会制造同类债务 → 需 Gate 持续盯

治本（warn 级，不阻断）:
- 检测 ``\\b(\\w+)\\(\\*\\*([A-Za-z_]\\w*)\\s*\\)`` 模式
- 豁免 ``**kwargs`` / ``**kwds``（显式关键字参数透传，合法）
- 豁免 ``**filter_dataclass_fields(...)``（已用 SSoT 过滤——但正则要求 ``**`` 后是纯标识符，
  函数调用 ``filter_dataclass_fields(...)`` 后跟 ``(`` 不会匹配，天然豁免）
- 豁免 ``**{...}``（字典字面量，正则要求 ``**`` 后是 ``\\w``，``{`` 不匹配）
- tests/ 豁免；import/注释/docstring 豁免
- 命中时 stderr + logger.warning 输出告警，**不阻断 commit**
- 选择 warn 而非 hard-block：避免误报阻断正常开发（如 ``dict(**other)`` 合法用法）；
  warn 级让 AI/人类 reviewer 知晓风险，由人工判断是否需修复

为什么 warn 不 block:
- 误报风险：``dict(**a)``、``OrderedDict(**a)`` 等内置容器构造是合法的
- ``**kwargs`` 透传场景无法静态判断目标类是否 dataclass/Pydantic
- warn 既能提醒又不阻断正常开发流，符合"治本不治标"原则——
  真正的治本是 SSoT ``filter_dataclass_fields``（已落地），gate 是防复发预警

Usage::

    from zephyr.governance.commit_gates.unsafe_dict_spread_gate import make_unsafe_dict_spread_gate
    registry.register(make_unsafe_dict_spread_gate())
"""

from __future__ import annotations

import logging
import re
import sys

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_unsafe_dict_spread_gate"]

# 合法的 **varname 集合：显式关键字参数透传
_SAFE_KWARGS_NAMES: frozenset[str] = frozenset({"kwargs", "kwds"})

# 匹配 SomeClass(**varname) —— varname 是纯标识符（非函数调用、非字典字面量）
# 后跟可选空白和 `)` —— 不匹配 `**func(...)` 因后面是 `(` 而非 `)`
# 不匹配 `**{...}` 因 `{` 不是 `\w`
_UNSAFE_SPREAD_RE = re.compile(r"\b(\w+)\(\*\*([A-Za-z_]\w*)\s*\)")

# 行级豁免：注释 / import
_COMMENT_RE = re.compile(r"^\s*#")
_IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import|import\s)")

# hunk header: @@ -old_start,old_count +new_start,new_count @@
_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _is_exempt_line(content: str) -> bool:
    """行级豁免：注释 / import（docstring 由 _extract_docstring_lines 多行跟踪处理）。"""
    return bool(_COMMENT_RE.match(content) or _IMPORT_RE.match(content))


def _extract_docstring_lines(file_content: str) -> set[int]:
    """返回文件中所有 docstring 内的行号集合（1-based）。

    跟踪 ``\"\"\"...\"\"\"`` 和 ``'''...'''`` 多行 docstring 范围。
    单行 docstring（同行开闭）只标记该行。
    用于豁免 docstring 中的示例代码（如 ``SomeClass(**varname)``），
    避免 gate 误报 docstring 示例（5.147.12 gate 自身 docstring 触发 warn 的修复）。
    """
    lines = file_content.splitlines()
    docstring_lines: set[int] = set()
    in_docstring = False
    quote = ""
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if not in_docstring:
            for q in ('"""', "'''"):
                if stripped.startswith(q):
                    in_docstring = True
                    quote = q
                    docstring_lines.add(i)
                    # 检查同行是否结束（单行 docstring）
                    rest = stripped[len(q):]
                    if quote in rest:
                        in_docstring = False
                        quote = ""
                    break
        else:
            docstring_lines.add(i)
            if quote in stripped:
                in_docstring = False
                quote = ""
    return docstring_lines


def _parse_diff_with_line_numbers(diff_stdout: str) -> list[tuple[int, str]]:
    """解析 git diff --unified=0 输出，返回 [(line_no, added_content), ...]。

    line_no 是新文件中的 1-based 行号。
    hunk header ``@@ -a,b +c,d @@`` 中 c 是新文件起始行号。
    added 行（``+`` 前缀）占用新行号；删除行（``-`` 前缀）不占用；上下文行占用。
    """
    result: list[tuple[int, str]] = []
    current_line = 0
    for raw_line in diff_stdout.splitlines():
        m = _HUNK_HEADER_RE.match(raw_line)
        if m:
            current_line = int(m.group(1))
            continue
        if raw_line.startswith("+++"):
            continue
        if raw_line.startswith("+"):
            result.append((current_line, raw_line[1:]))
            current_line += 1
        elif raw_line.startswith("-"):
            pass  # 删除行不递增新行号
        else:
            current_line += 1  # 上下文行（unified=0 通常无，保险处理）
    return result


def _read_staged_file(gateway, py_file: str) -> str | None:
    """读取 staged 文件内容（index 版本，``git show :path``）。"""
    try:
        result = gateway._run_git(["git", "show", ":" + py_file])
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def make_unsafe_dict_spread_gate() -> GateSpec:
    """构造 ``**data`` 直接展开 warn 级 GateSpec。

    Returns:
        GateSpec(gate_id="UNSAFE-DICT-SPREAD", priority=66)。
        priority=66——在 ssot_redefinition(65) 之后、dangling_reference(70) 之前，
        与 SSoT 符号检测同组（代码模式检测）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "UNSAFE-DICT-SPREAD gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
        except Exception as e:
            logger.warning(
                "UNSAFE-DICT-SPREAD gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        py_files = [f for f in staged if f.endswith(".py") and not is_test_exempt(f)]
        if not py_files:
            return True, ""

        # 2. 检测每个 staged .py 文件的 added 行
        warnings: list[str] = []
        for py_file in py_files:
            # 2a. 读取 staged 完整文件，预计算 docstring 行号集合（豁免 docstring 示例）
            file_content = _read_staged_file(gateway, py_file)
            docstring_lines = _extract_docstring_lines(file_content) if file_content else set()

            # 2b. 解析 diff，获取 added 行及行号
            try:
                file_diff = gateway._run_git(
                    ["git", "diff", "--cached", "--unified=0", "--", py_file]
                )
            except Exception as e:
                logger.warning(
                    "UNSAFE-DICT-SPREAD gate: git diff 失败 file=%s, %s",
                    py_file, e, exc_info=True,
                )
                continue
            if file_diff.returncode != 0:
                continue

            added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
            for line_no, content in added_lines:
                # 豁免：docstring 内的行（多行 docstring 跟踪）
                if line_no in docstring_lines:
                    continue
                # 豁免：注释 / import
                if _is_exempt_line(content):
                    continue
                m = _UNSAFE_SPREAD_RE.search(content)
                if not m:
                    continue
                cls_name, var_name = m.group(1), m.group(2)
                # 豁免 **kwargs / **kwds（显式关键字参数透传，合法）
                if var_name in _SAFE_KWARGS_NAMES:
                    continue
                warnings.append(
                    f"  {py_file}:{line_no}: {cls_name}(**{var_name}) -> {content.strip()}"
                )

        # 3. warn 级：不阻断 commit，仅 stderr + logger 告警
        if warnings:
            detail = (
                "UNSAFE-DICT-SPREAD warn（不阻断）：检测到 **data 直接展开模式，\n"
                "  schema 演进时会触发 TypeError（5.147.5/5.147.12 同族债务）。\n"
                + "\n".join(warnings)
                + "\n→ 建议改用 filter_dataclass_fields(Cls, data) 过滤未知字段：\n"
                "    from zephyr.shared.io.serialization import filter_dataclass_fields\n"
                "    obj = Cls(**filter_dataclass_fields(Cls, data))\n"
                "→ 若确为 **kwargs 透传或 dict(**other) 合法用法，可忽略本告警。"
            )
            # stderr 输出（用户可见）+ logger 记录
            print(f"[GATE] UNSAFE-DICT-SPREAD warn:\n{detail}", file=sys.stderr)
            logger.warning("UNSAFE-DICT-SPREAD gate warn:\n%s", detail)
            return True, detail

        return True, ""

    return GateSpec(gate_id="UNSAFE-DICT-SPREAD", check=_check, priority=66)
