# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates._diff_helpers
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] —
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.unsafe_dict_spread_gate; zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate; zephyr.gov_enforcement.commit_gates.bare_sql_gate; zephyr.gov_enforcement.commit_gates.hardcoded_url_gate; zephyr.gov_enforcement.commit_gates.high_complexity_gate; zephyr.gov_enforcement.commit_gates.import_integrity_gate; zephyr.gov_enforcement.commit_gates.bare_subprocess_gate; zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate; zephyr.gov_enforcement.commit_gates.capability_overlap_gate
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] gate 共享 diff 解析工具模块——提取 unsafe_dict_spread_gate / datetime_now_forbidden_gate / bare_sql_gate / hardcoded_url_gate / high_complexity_gate / import_integrity_gate / bare_subprocess_gate / consumers_accuracy_gate 公共 diff 解析函数，消除 FUNCTION-DUP 重复定义；纯函数无副作用；不可达路径 fail-open（返回空集/空列表/None）；_extract_docstring_lines 用 ast 精确识别 docstring（R95 治本），不再用正则近似；_extract_sql_constant_lines 用 ast 精确识别 SQL_*/_SQL_* 常量定义行范围（R96 治本），替代 bare_sql_gate 的 _SQL_CONSTANT_DEF_RE 正则近似；_make_noqa_pattern + _extract_noqa_lines 消除 import_integrity_gate / bare_subprocess_gate 的 noqa 提取克隆（#ARCH-FORCE-MERGE-DEDUP-001）；_module_to_file_candidates 消除 import_integrity_gate / consumers_accuracy_gate 的模块路径转换克隆；_matches_any_prefix 消除 _is_project_module / _is_abstract_code 的前缀判断同构克隆；_is_cosmetic_only_change 用「去 docstring 后 AST 指纹」机械判定零可执行语义变更（裁定#273 触碰税豁免），读不到/解析不了一律判非 cosmetic（fail-closed 照常送检）；_audit_foreign_staged 三态（裁定#480 手术④顺路修复）：外来 staged=活会话在途（held_files∪task_files 归因命中，维持现状不代修）｜无主外来（不在任何活跃 session 双集——属主无活跃片/孤儿文件）审计附 ownerless_files+可顺路修处方（--adopt-prior-work 语义认领后随批修复+台账留痕）｜registry 不可读=分类不可判维持两态（fail-safe 不误开处方）；只改文案与判级，不自动改任何外来文件（宪法 §3.4 owner 责任制保留）
# [MODIFY-GUARD] 函数签名：_is_exempt_line(str)->bool, _extract_docstring_lines(str)->set[int], _extract_sql_constant_lines(str)->set[int], _parse_diff_with_line_numbers(str)->list[tuple[int,str]], _read_staged_file(gateway,str)->str|None, _read_head_file(gateway,str)->str|None, _collect_function_names(str)->set[str], _make_noqa_pattern(str)->re.Pattern, _extract_noqa_lines(str,re.Pattern)->set[int], _module_to_file_candidates(str)->list[str], _matches_any_prefix(str,tuple)->bool, _ast_semantic_fingerprint(str)->str|None, _is_cosmetic_only_change(gateway,str)->bool
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有函数永不抛异常——异常降级为空返回值（set()/[]/None）
# [TESTS] tests/governance/commit_gates/test_diff_helpers.py（直接测试）；tests/governance/commit_gates/test_unsafe_dict_spread_gate.py（间接覆盖）
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""_diff_helpers.py — gate 共享 diff 解析工具模块

提取自 unsafe_dict_spread_gate.py，供多个 commit-time gate 复用，
消除 FUNCTION-DUP gate 阻断（同目录同 name+body hash 重复函数）。

公共函数：
- _is_exempt_line: 行级豁免判定（注释/import）
- _extract_docstring_lines: docstring 行号集合提取（R95 用 ast 精确识别）
- _extract_sql_constant_lines: SQL_*/_SQL_* 常量定义行号集合提取（R96 用 ast 精确识别）
- _parse_diff_with_line_numbers: git diff 输出解析为 [(line_no, content)]
- _read_staged_file: 读取 staged 文件内容（git show :path）
- _get_staged_py_files: 获取 staged .py 文件列表
- _get_added_lines: 获取文件 added 行列表

S1 不可变树代理（st-commitspeed-tbl-20260924）：_read_staged_file /
_get_staged_py_files / _get_added_lines / _read_head_file 四入口为视图代理——
gateway 为 CommitTreeView 替身（flag commit_immutable_tree=ON 的门禁链内注入）
时读不可变树（有树读树），否则逐字走旧共享暂存区路径（无树读旧路径）。
分派原语 _own_tree_view 对视图/本体二值分派；15 台全索引门的分道真源在
CommitGateRegistry.check_all（不在本模块）。flag OFF 下无视图存在＝零行为变更。

Usage::

    from zephyr.gov_enforcement.commit_gates._diff_helpers import (
        _is_exempt_line,
        _extract_docstring_lines,
        _extract_sql_constant_lines,
        _parse_diff_with_line_numbers,
        _read_staged_file,
    )

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/_/_diff_helpers.yaml
"""

from __future__ import annotations

import ast
import json
import logging
import os
import re
import time
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = [
    "_COMMENT_RE",
    "_IMPORT_RE",
    "_HUNK_HEADER_RE",
    "_SQL_CONSTANT_NAME_RE",
    "_is_exempt_line",
    "_extract_docstring_lines",
    "_extract_sql_constant_lines",
    "_parse_diff_with_line_numbers",
    "_read_staged_file",
    "_read_head_file",
    "_repo_state_has_file",
    "_collect_function_names",
    "_get_staged_py_files",
    "_get_added_lines",
    "_make_noqa_pattern",
    "_extract_noqa_lines",
    "_module_to_file_candidates",
    "_matches_any_prefix",
    "_split_own_foreign",
]

# 行级豁免：注释 / import
_COMMENT_RE = re.compile(r"^\s*#")
_IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import|import\s)")

# hunk header: @@ -old_start,old_count +new_start,new_count @@
_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

# SQL 常量名判定：匹配 _?SQL_ 前缀的变量名（SQL_FOO / _SQL_PATTERN 等）
# R96 治本：替代 bare_sql_gate._SQL_CONSTANT_DEF_RE 正则近似（只豁免定义行不跟踪多行）
_SQL_CONSTANT_NAME_RE = re.compile(r"^_?SQL_\w+$")


def _is_exempt_line(content: str) -> bool:
    """行级豁免：注释 / import（docstring 由 _extract_docstring_lines 多行跟踪处理）。"""
    return bool(_COMMENT_RE.match(content) or _IMPORT_RE.match(content))


def _extract_docstring_lines(file_content: str) -> set[int]:
    """返回文件中所有 docstring 内的行号集合（1-based）。

    使用 ast 模块精确识别 Module/ClassDef/FunctionDef/AsyncFunctionDef 的
    docstring（body[0] 是 ``ast.Expr(value=ast.Constant(str))``）。

    设计意图（R95 治本，2026-07-10）：
    - 只豁免真正的 docstring（模块/类/函数的文档字符串 body[0]）
    - 不豁免行内字符串赋值（如 ``__manifest__ = \"\"\"...\"\"\"``）
    - 不豁免独立字符串表达式（非 body[0]）

    旧实现用 ``stripped.startswith('\"\"\"')`` 作判据，是正则近似，无法区分
    上述场景，导致 ``__manifest__ = \"\"\"...\"\"\"`` 的结束独立 ``\"\"\"`` 行
    被误判为新 docstring 起始，后续所有行被错误豁免（cleanup_p0_auto_bridged.py
    L78/L87 裸 SQL 漏检根因）。

    fail-open：ast.parse 失败（语法错误）时返回空集合——所有行都不豁免，
    可能误报但不漏检（语法错误文件本就会在其他阶段失败）。

    Args:
        file_content: Python 文件完整内容。

    Returns:
        docstring 覆盖的行号集合（1-based）。
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        logger.warning(
            "_extract_docstring_lines: ast.parse 失败（语法错误），fail-open 返回空集合——所有行都不豁免",
            exc_info=True,
        )
        return set()

    docstring_lines: set[int] = set()
    for node in ast.walk(tree):
        # docstring 仅出现在 Module/ClassDef/FunctionDef/AsyncFunctionDef 的 body[0]
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.body:
                continue
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                start = first.lineno
                end = getattr(first, "end_lineno", start)
                for i in range(start, end + 1):
                    docstring_lines.add(i)
    return docstring_lines


def _extract_sql_constant_lines(file_content: str) -> set[int]:
    """返回文件中所有 SQL_* / _SQL_* 常量定义覆盖的行号集合（1-based）。

    使用 ast 模块精确识别 Assign 节点，目标名匹配 ``^_?SQL_\\w+$``。
    豁免整个 Assign 节点的行范围（lineno 到 end_lineno），覆盖：
    - 单行定义：``SQL_X = "SELECT..."``
    - 括号多行：``SQL_X = (\\n    "SELECT..."\\n)``
    - 三引号多行：``SQL_X = \"\"\"\\nSELECT...\\n\"\"\"``
    - 反斜杠续行：``SQL_X = \\\\\\n    "SELECT..."``

    设计意图（R96 治本，2026-07-10）：
    旧实现用 ``_SQL_CONSTANT_DEF_RE = re.compile(r"^\\s*_?SQL_\\w+\\s*=")``
    只豁免定义行，不跟踪多行续行，导致括号隐式连接的续行含完整 SQL
    字符串字面量时被 ``_SQL_PATTERN`` 误报（file_task_mapper.py L67/L70/L73
    误报根因）。

    fail-open：ast.parse 失败（语法错误）时返回空集合——所有行都不豁免，
    可能误报但不漏检（语法错误文件本就会在其他阶段失败）。

    Args:
        file_content: Python 文件完整内容。

    Returns:
        SQL 常量定义覆盖的行号集合（1-based）。
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        logger.warning(
            "_extract_sql_constant_lines: ast.parse 失败（语法错误），fail-open 返回空集合——所有行都不豁免",
            exc_info=True,
        )
        return set()

    sql_const_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and _SQL_CONSTANT_NAME_RE.match(target.id):
                    start = node.lineno
                    end = getattr(node, "end_lineno", start)
                    for i in range(start, end + 1):
                        sql_const_lines.add(i)
                    break  # 一个 target 命中即可豁免整个 Assign
    return sql_const_lines


def _parse_diff_with_line_numbers(diff_stdout: str) -> list[tuple[int, str]]:
    """解析 git diff --unified=0 输出，返回 [(line_no, added_content), ...]。

    line_no 是新文件中的 1-based 行号。
    hunk header ``@@ -a,b +c,d @@`` 中 c 是新文件起始行号。
    added 行（``+`` 前缀）占用新行号；删除行（``-`` 前缀）不占用；上下文行占用。
    """
    result: list[tuple[int, str]] = []
    current_line = 0
    # 2026-08-17 AI-00 收口治本：splitlines() → split("\n") + 跳过裸空行——HEAD 侧 \r\r\n
    # 双 CR 损坏文件（2026-08-16 EOL 批残留）的删除行，经 subprocess text=True
    # （universal_newlines）翻译为 \n\n，切出幻影空行落入 else 分支虚增 current_line
    # （+1/删除行，实证 migrate_data.py 真 118 行报为 575），AST 豁免行号集与膨胀行号
    # 失配 → SQL_* 常量被裸 SQL 误报。unified=0 diff 无合法裸空行（空行必带 +/- 前缀）。
    for raw_line in diff_stdout.split("\n"):
        if raw_line == "":
            continue  # \r\r\n→\n\n 翻译幻影空行 / diff 末尾空串，不占新文件行号
        m = _HUNK_HEADER_RE.match(raw_line)
        if m:
            current_line = int(m.group(1))
            continue
        if raw_line.startswith("+++"):
            continue
        if raw_line.startswith("\\"):
            # "\ No newline at end of file" 是 diff 元数据，不占新文件行号
            # （2026-08-12 修复：整文件替换 diff 中该标记导致后续 added 行号 +1 偏移）
            continue
        if raw_line.startswith("+"):
            result.append((current_line, raw_line[1:]))
            current_line += 1
        elif raw_line.startswith("-"):
            pass  # 删除行不递增新行号
        else:
            current_line += 1  # 上下文行（unified=0 通常无，保险处理）
    return result


def _own_tree_view(gateway):
    """S1 视图感知分派原语（st-commitspeed-tbl-20260924，A4 阶梯"四入口改代理"执行件）。

    gateway 即 CommitTreeView 替身（只在 flag ``commit_immutable_tree``=ON 的门禁链
    内由 git_commit_gateway._build_own_tree_view 构造并经 check_all 注入，或重放器
    直注）→ 返回该视图，四入口走"读不可变树"快速路径；gateway 是本体
    GitCommitGateway（flag OFF 的全部现行为/测试直调/工具链路径）→ 返回 None，
    四入口逐字走旧路径。视图不存在处零分派成本（一次 lazy import 查表＋isinstance）。

    fail-open：import 失败一律 None（旧路径），永不影响现行为；15 台
    ``SHARED_INDEX_WITHOUT_OWN_SCOPE`` 分道门不在此处判定——它们的分道真源在
    check_all 逐台 gateway 分发（生产链里名单门拿到的本来就是本体 gateway），
    本原语对"视图作 gateway"与"本体作 gateway"二值分派，不持名单。
    """
    try:
        from zephyr.gov_enforcement.commit_gates._tree_view import (  # noqa: PLC0415
            CommitTreeView,
        )
    except Exception:  # noqa: BLE001 — 设施缺失=旧路径（fail-open 口径不变）
        return None
    return gateway if isinstance(gateway, CommitTreeView) else None


def _read_staged_file(gateway, py_file: str) -> str | None:
    """读取 staged 文件内容（index 版本，``git show :path``）。

    S1 代理：gateway 为不可变树视图时＝``git show <head_rev>:path``（视图域直读，
    字节口径与 ``git show :path`` 的视图改写结果逐字节一致——同一 head 树）。
    """
    view = _own_tree_view(gateway)
    if view is not None:
        return view.read_staged_file(py_file)
    try:
        result = gateway.run_git(["git", "show", ":" + py_file])
        if result.returncode == 0:
            return result.stdout
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass
    return None


def _get_staged_py_files(gateway, gate_name: str = "gate", include_renamed: bool = False) -> list[str]:
    """获取 staged added/modified .py 文件列表（fail-open）。

    失败时返回空列表并记录 warning。调用方应在返回空时 return True, ""（fail-open）。
    注意：不过滤 tests/，由调用方用 is_test_exempt() 过滤。
    include_renamed=True 时追加 rename（R）态文件——R 新路径不在 AM filter 内，
    "import 目标存在性"类检查必须看到 R 新路径，否则同批 rename+consumer 必误报悬空
    （2026-09-13 src/signal_ashare 拆分批实证；内容扫描型 gate 勿开——R 文件全文
    进扫描会误报存量克隆）。

    S1 代理：gateway 为不可变树视图时＝视图 ``staged_files``（``git diff
    <base> <head> --name-only``；共享 index 模拟视图则并噪声集）。集合语义与旧
    路径逐台等价；模拟视图的合并清单按字节序排序（仅重放仪器面顺序差异，
    verdict/hits 集合语义不变）。
    """
    view = _own_tree_view(gateway)
    if view is not None:
        return view.staged_files(gate_name=gate_name, include_renamed=include_renamed)
    try:
        result = gateway.run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AMR" if include_renamed else "--diff-filter=AM"]
        )
        if result.returncode != 0:
            logger.warning(
                "%s fail-open: git diff 失败(rc=%d)。",
                gate_name,
                result.returncode,
            )
            return []
        return [f.replace("\\", "/") for f in result.stdout.strip().splitlines() if f and f.endswith(".py")]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "%s fail-open: git diff 异常(%s: %s)。",
            gate_name,
            type(e).__name__,
            e,
            exc_info=True,
        )
        return []


def _get_added_lines(gateway, py_file: str, gate_name: str = "gate") -> list[tuple[int, str]]:
    """获取文件的 added 行列表（fail-open）。

    失败时返回空列表并记录 warning。

    S1 代理：gateway 为不可变树视图时＝视图 ``added_lines``（``git diff <base>
    <head> --unified=0 --ignore-cr-at-eol -- path``，行号解析同一真源）。
    """
    view = _own_tree_view(gateway)
    if view is not None:
        return view.added_lines(py_file, gate_name=gate_name)
    try:
        # --ignore-cr-at-eol：EOL 规范化提交（CRLF→LF 机械翻转）全文件行伪"added"，
        # 会把存量违规误报为新增——按内容判定 added，行尾差异不计（2026-08-16 EOL 批实证）
        result = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", py_file])
        if result.returncode != 0:
            return []
        return _parse_diff_with_line_numbers(result.stdout)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("%s: git diff 失败 file=%s, %s", gate_name, py_file, e)
        return []


def _read_head_file(gateway, py_file: str) -> str | None:
    """读取 HEAD 版本的文件内容（``git show HEAD:path``）。

    用于区分"新增函数"与"修改函数"——裁定#214 治本：
    NO-HIGH-COMPLEXITY gate 设计意图是"只检测新增函数"，
    但原实现 ``node.lineno in added_lines`` 捕获了修改签名的已有函数。
    本函数读取 HEAD 版本，供 gate 判断函数是否已存在。

    fail-open：文件不存在于 HEAD（新增文件）或 git 命令失败时返回 None。

    S1 代理：gateway 为不可变树视图时＝``git show <base_rev>:path``（base=
    门禁时刻 HEAD=本件父提交，对齐 CommitTreeView 契约"提交前仓库态"）。
    """
    view = _own_tree_view(gateway)
    if view is not None:
        return view.read_head_file(py_file)
    try:
        result = gateway.run_git(["git", "show", "HEAD:" + py_file])
        if result.returncode == 0:
            return result.stdout
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass
    return None


def _repo_state_has_file(gateway, rel_path: str, rev: str = "") -> bool:
    """存在性观测面=git 仓库态（裁定#279：index 或指定 rev），磁盘只作补充证据。

    门禁要判的命题是"本 commit 之后的仓库里有没有这个文件"，不是"本机磁盘上
    碰巧有没有"——序列化器落地 worktree 未 checkout 的 staged 新文件、他会话
    在途删除等场景下磁盘面必然误判（2026-09-17 同盲区家族清偿）。
    rev="" 查 index（ls-files --cached）；rev="HEAD" 等查该 tree（ls-tree）。
    布尔判别用输出行数而非退出码：``cat-file -e`` 的"不存在"与"git 故障"同为
    非零 rc 不可判别，ls-files/ls-tree 的 rc==0 恒成立、空输出=不存在。
    git 失败（rc!=0，环境故障）时退回磁盘 ``os.path.exists`` 并**告警留痕**
    （禁静默换口径——磁盘=本机暂态，非仓库态）。
    """
    args = ["git", "ls-tree", rev, "--", rel_path] if rev else ["git", "ls-files", "--cached", "--", rel_path]
    root = getattr(gateway, "project_root", None)
    try:
        result = gateway.run_git(args)
        if result.returncode == 0:
            if result.stdout.strip():
                return True
            # 仓库态没有 → 磁盘补充证据：未跟踪但在盘的目标对"存在性"判定合法
            # （断链/悬空检测关心的是读者能不能找到它）；staged 未落盘的假阳性
            # 场景由前面的仓库态分支消除。git 判"有"时不再问磁盘（主证据已足）。
            return bool(root) and (Path(root) / rel_path).exists()
        logger.warning(
            "_repo_state_has_file: git rc=%d（%s %s）——退回磁盘观测面（降级留痕，裁定#279）",
            result.returncode,
            args[1],
            rel_path,
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "_repo_state_has_file: git 异常（%s: %s）——退回磁盘观测面（降级留痕，裁定#279）",
            type(e).__name__,
            e,
        )
    return bool(root) and (Path(root) / rel_path).exists()


def _collect_function_names(file_content: str) -> set[str]:
    """收集文件中所有函数名（FunctionDef / AsyncFunctionDef 的 name 属性）。

    用于判断 staged 版本中的函数是否在 HEAD 版本中已存在（修改 vs 新增）。
    fail-open：ast.parse 失败时返回空集合（所有函数都视为"新增"——安全方向）。
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


# ── noqa / 模块路径 / 前缀判断共享 helper（#ARCH-FORCE-MERGE-DEDUP-001 消除克隆）──
# 提取自 import_integrity_gate / bare_subprocess_gate / consumers_accuracy_gate，
# 消除 CAPABILITY-OVERLAP 门禁检测到的 extract 级克隆（60% 相似度，3+ 副本）。


def _make_noqa_pattern(gate_id: str) -> re.Pattern:
    """构造行级 noqa 逃生标记正则——``# noqa: <gate_id>  <reason>``。

    对标 bare-subprocess / import-integrity / consumers-accuracy 等门禁的
    noqa 模式，统一为单一真源，消除逐 gate 复制的正则克隆。

    Args:
        gate_id: 门禁标识（如 ``"import-integrity"`` / ``"bare-subprocess"``）。

    Returns:
        编译后的正则 Pattern，匹配 ``# noqa: <gate_id>  <reason>`` 行
       （gate_id 后需 2+ 空格 + reason >= 1 字符）。
    """
    return re.compile(
        rf"#\s*noqa:\s*{re.escape(gate_id)}\s{{2,}}(\S.*)$",
        re.MULTILINE,
    )


def _extract_noqa_lines(file_content: str, pattern: re.Pattern) -> set[int]:
    """提取带 noqa 逃生标记的行号集合（1-based）。

    通行级 noqa 提取——供所有 commit-time gate 复用，消除逐 gate 复制的
    ``_extract_noqa_lines`` 函数克隆。

    Args:
        file_content: Python 文件完整内容。
        pattern: 由 ``_make_noqa_pattern(gate_id)`` 构造的正则。

    Returns:
        命中 noqa 标记的行号集合（1-based）。
    """
    noqa_lines: set[int] = set()
    for i, line in enumerate(file_content.splitlines(), start=1):
        if pattern.search(line):
            noqa_lines.add(i)
    return noqa_lines


def _module_to_file_candidates(module_path: str) -> list[str]:
    """将模块路径转为文件系统候选路径（module.py 或 module/__init__.py）。

    统一 import_integrity_gate / consumers_accuracy_gate 的模块路径转换逻辑，
    消除逐 gate 复制的 ``_module_to_file_candidates`` 函数克隆。

    Args:
        module_path: 点分模块路径（如 ``zephyr.gov_enforcement.foo``）。

    Returns:
        候选相对路径列表（按优先级排序）。
    """
    parts = module_path.split(".")
    base = "/".join(parts)
    return [
        f"src/{base}.py",
        f"src/{base}/__init__.py",
        f"{base}.py",
        f"{base}/__init__.py",
    ]


def _matches_any_prefix(s: str, prefixes: tuple[str, ...]) -> bool:
    """判断字符串是否以给定前缀元组中任一项开头。

    统一 ``_is_project_module`` / ``_is_abstract_code`` 等前缀判断单行函数，
    消除结构同构克隆（``any(x.startswith(p) for p in _PREFIXES)`` 3+ 副本）。

    Args:
        s: 待检查字符串。
        prefixes: 前缀元组。

    Returns:
        True 如果 ``s`` 以 ``prefixes`` 中任一项开头。
    """
    return any(s.startswith(p) for p in prefixes)


# ═══ session-scope helpers（#ARCH-GATE-OWN-SCOPE-001 推广 2026-09-10）═══
# 自 import_integrity_gate.py 平移泛化——"只查自己"改造的共享原语：
# 内容扫描型 gate 扫描范围收敛为「全暂存区 ∩ 本 session 范围」，外来 staged
# 不扫描、降级 warn+审计。平移语义不变；_audit_foreign_staged 的审计文件名
# 由 gate_name 派生（各 gate 各写各的审计，替代同族共用单文件）。

logger_ss = logging.getLogger(__name__)


def _norm_rel(gateway, path: str) -> str:
    """任意路径 → normcase 相对路径（正斜杠），供 own_scope 交集比对。

    commit() 传入绝对路径（git_commit_gateway abspath），_get_staged_py_files
    返回正斜杠相对路径；Windows 盘符/大小写差异用 normcase 归一。
    fail-open：relpath 失败时原样返回 normcase 后的输入（不抛异常）。
    """
    try:
        root = str(getattr(gateway, "project_root", "") or os.getcwd())
        p = str(path)
        if os.path.isabs(p):
            rel = os.path.relpath(p, root)
        else:
            # 已是仓库根相对路径（测试直调场景），不做 abspath（会锚定进程 CWD）
            rel = p
        rel = rel.replace("\\", "/")
    except Exception:  # noqa: BLE001 — 归一化失败不阻断（ERROR_CONTRACT，如跨盘符）
        rel = str(path).replace("\\", "/")
    return os.path.normcase(rel)


def _build_own_scope(gateway, files: list[str] | None, session_id: str | None) -> set[str] | None:
    """构建本 session 文件范围（normcase 相对路径集合）。

    范围 = 本次 commit files 清单 ∪ session claimed held_files（SessionRegistry 只读）。
    返回 None：files 与 session 归属信息均为空（历史直调/未注册场景）——
    调用方退化为旧行为（扫全量），保守面不改宽。
    fail-open：registry 读取异常降级为 files-only。
    """
    scope: set[str] = set()
    for f in files or []:
        scope.add(_norm_rel(gateway, f))
    if session_id:
        try:
            registry = getattr(gateway, "_registry", None)
            info = registry.get_session(session_id) if registry is not None else None
            for held in getattr(info, "held_files", None) or []:
                scope.add(_norm_rel(gateway, held))
        except Exception:  # noqa: BLE001 — registry 异常退化为 files-only（fail-open 红线）
            logger_ss.debug("own-scope held_files 读取失败（退化为 files-only）", exc_info=True)
    return scope or None


def _attribute_foreign(gateway, session_id: str | None, foreign_staged: list[str]) -> dict[str, str] | None:
    """外来 staged 文件尽力归因（活跃 session 只读；匹配不上不标）。

    裁定#480 手术④（顺路修复三态）判据面：归因集=活跃 session 的
    ``held_files ∪ task_files`` 双集（.runtime/session_registry/ 活跃片聚合，
    list_active 只回活跃片)——归因命中=活会话在途；未命中=无主外来
    （属主 session 无活跃片/孤儿文件）。

    Returns:
        {norm_path: 属主 sid} 归因映射；registry 不可读/异常 → None
        （分类不可判——调用方 fail-safe 维持两态现状，不误开顺路修处方）。
    """
    try:
        registry = getattr(gateway, "_registry", None)
        if registry is None:
            return None
        foreign_norm = {_norm_rel(gateway, f) for f in foreign_staged}
        attribution: dict[str, str] = {}
        for info in registry.list_active():
            if session_id and info.session_id == session_id:
                continue
            for held in list(info.held_files or []) + list(info.task_files or []):
                norm = _norm_rel(gateway, held)
                if norm in foreign_norm:
                    attribution.setdefault(norm, info.session_id)
        return attribution
    except Exception:  # noqa: BLE001 — 归因失败不影响审计主流程
        logger_ss.debug("foreign attribution failed (non-blocking)", exc_info=True)
        return None


# 无主外来「可顺路修」处方文案（裁定#480 手术④——只改文案与判级，不自动改外来文件；
# 宪法 §3.4 owner 责任制保留：活会话在途不代修）。
_OWNERLESS_PRESCRIPTION = (
    "无主外来（不在任何活跃 session 的 task_files/held_files，属主无活跃片）→ 可顺路修："
    "按 --adopt-prior-work 语义认领后随本批修复并在 gate_audit 台账留痕；"
    "活会话在途文件维持现状不代修（owner 责任制，宪法 §3.4）。"
)


def _audit_foreign_staged(
    gateway, session_id: str | None, foreign_staged: list[str], *, gate_name: str
) -> dict[str, list[str]] | None:
    """外来 session staged 文件落审计（jsonl append；fail-open：写失败不阻断）。

    审计文件名由 gate_name 派生（NO-HIGH-COMPLEXITY → no_high_complexity_foreign_staged.jsonl），
    各 gate 各写各的审计（IMPORT-INTEGRITY 派生名与历史文件名一致，行为兼容）。
    对标 protected_paths_gate._audit_bypass（.runtime/gate_audit/ 惯例）。

    三态（裁定#480 手术④「顺路修复三态」）：外来 staged = 活会话在途（归因命中，
    维持现状不代修）｜无主外来（属主 session 已死/孤儿文件——不在任何活跃 session
    的 task_files/held_files）→ 审计记录 ownerless_files + prescription 处方
    （--adopt-prior-work 语义认领后随批修复+台账留痕）；registry 不可读 →
    分类不可判，维持两态现状（fail-safe 不误开处方）。只改文案与判级，
    不自动改任何外来文件。

    Returns:
        {"in_flight": [...], "ownerless": [...]}（normcase 归一路径）分类摘要，
        供 _split_own_foreign warn 文案复用；registry 不可读 → None。
    """
    attribution = _attribute_foreign(gateway, session_id, foreign_staged)
    states: dict[str, list[str]] | None = None
    if attribution is not None:
        foreign_norm = {_norm_rel(gateway, f) for f in foreign_staged}
        states = {
            "in_flight": sorted(foreign_norm & set(attribution)),
            "ownerless": sorted(foreign_norm - set(attribution)),
        }
    try:
        root = Path(getattr(gateway, "project_root", "."))
        audit_dir = root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        fname = gate_name.lower().replace("-", "_") + "_foreign_staged.jsonl"
        record = {
            "timestamp": int(time.time()),  # noqa: m46-time 审计事件需 epoch 秒（gate 家族先例 protected_paths_gate 同口径）
            "gate": gate_name,
            "session_id": session_id or "?",
            "foreign_count": len(foreign_staged),
            "foreign_files": foreign_staged[:50],
            "attribution": attribution if attribution is not None else {},
        }
        if states is not None:
            record["states"] = states
            if states["ownerless"]:
                record["ownerless_prescription"] = _OWNERLESS_PRESCRIPTION
        with (audit_dir / fname).open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + chr(10))
    except Exception:  # noqa: BLE001 — 审计失败不阻断（check ERROR_CONTRACT）
        logger_ss.debug("foreign staged audit write failed (non-blocking)", exc_info=True)
    return states


_SRC_ZEPHYR_PREFIX = "src/zephyr/"


def _split_own_foreign(
    gateway,
    staged: list[str],
    files: list[str] | None,
    session_id: str | None,
    *,
    gate_name: str,
) -> tuple[list[str], list[str]]:
    """own 化标准拆分原语：staged 清单 → (本 session 文件, 外来文件)，外来自动审计。

    #ARCH-GATE-OWN-SCOPE-001 推广面（st-gslim-20260923 P2，C3 名单 31 台机械 own 化，
    gate_audit_report_v1 §C3/Owner 全批 E9）：全暂存内容扫描台扫「全暂存区 ∩ 本 session
    范围」，外来 staged 不扫描、不产生违规、不阻断（降级 warn+审计）——多会话连坐的
    结构性消除。31 台若各自内联本拆分即触发 FUNCTION-DUP/CAPABILITY-OVERLAP 自身门禁
    （同目录同构克隆），故收敛为共享原语（与本文件 own-scope 推广面定位一致）。

    - own_scope=None（files 与 session 归属信息均空，历史直调场景）→ 返回 (staged, [])：
      退化为旧行为扫全量，保守面不改宽（与 _build_own_scope 契约一致）。
    - 审计与 warn 在本函数内完成（对标 IMPORT-INTEGRITY 范本），调用方只需扫描 own 侧。
    - 永不抛异常（ERROR_CONTRACT）；输入参数不被修改，返回新列表。
    """
    try:
        staged = list(staged or [])  # None（fail-open 信号）归一为空清单——split 恒安全
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is None:
            return staged, []
        own: list[str] = []
        foreign: list[str] = []
        for f in staged:
            if _norm_rel(gateway, f) in own_scope:
                own.append(f)
            else:
                foreign.append(f)
    except Exception:  # noqa: BLE001 — 拆分失败退化为旧行为扫全量（保守面不改宽）
        logger_ss.debug("own-scope split failed (fallback to full scan)", exc_info=True)
        return list(staged or []), []
    if foreign:
        states = _audit_foreign_staged(gateway, session_id, foreign, gate_name=gate_name)
        prescription = ""
        if states is not None and states["ownerless"]:
            # 裁定#480 手术④：无主外来（属主无活跃片/孤儿文件）附「可顺路修」处方；
            # 活会话在途（in_flight）维持现状不代修（owner 责任制，宪法 §3.4）。
            prescription = " " + _OWNERLESS_PRESCRIPTION
        logger_ss.warning(
            "%s: %d 个外来 session staged 文件未检查（warn+审计，不阻断）: %s%s",
            gate_name,
            len(foreign),
            ", ".join(foreign[:5]) + ("..." if len(foreign) > 5 else ""),
            prescription,
        )
    return own, foreign


def _is_src_zephyr_file(py_file: str) -> bool:
    """判定 .py 文件是否在 src/zephyr/ 目录下（分隔符归一后前缀判断）。

    自 asyncio_run_in_context_gate / datetime_now_forbidden_gate 的同构实现合并
    （#ARCH-FORCE-MERGE-DEDUP-001，2026-09-10 st-legacy-clear-20260910）。
    """
    return str(py_file).replace("\\", "/").startswith(_SRC_ZEPHYR_PREFIX)


_DOC_BEARING_NODES = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def _ast_semantic_fingerprint(src: str) -> str | None:
    """去 docstring 后的 AST 指纹——「可执行语义是否等价」的机械判据。

    注释不入 AST、docstring 显式剥除，故纯文档串/注释/空白编辑两侧指纹相同；
    装饰器、签名、类型注解、字符串常量（非 docstring）全部入指纹，改了就不相等。
    永不抛异常：解析失败返回 None（调用方按 fail-closed 处理=照常送检）。
    """
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError, RecursionError):
        return None
    for node in ast.walk(tree):
        if not isinstance(node, _DOC_BEARING_NODES):
            continue
        body = list(getattr(node, "body", None) or [])
        if not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            node.body = body[1:] or [ast.Pass()]
    try:
        return ast.dump(tree, annotate_fields=True, include_attributes=False)
    except (RecursionError, ValueError):
        return None


def _is_cosmetic_only_change(gateway, py_file: str) -> bool:
    """HEAD↔staged 去 docstring 后 AST 等价 = 纯文档串/注释/空白编辑（零可执行语义变更）。

    病根（裁定#273，2026-09-16 P2-1 ALGO_FLOW 出仓波次）：出仓只把机器块从 docstring
    搬进 docs/ yaml，源码可执行语义逐字未动，但 CAPABILITY-OVERLAP 的 CloneGuard 按
    「staged .py 全量送检」把**两侧既有**的 extract 级克隆判给本批=触碰税，存量债让
    无辜批次硬阻断。语义零变更的编辑不该为存量克隆买单。

    fail-closed：新增文件（HEAD 无此件）、任一侧读取/解析失败 → False（照常送检）。
    """
    head = _read_head_file(gateway, py_file)
    staged = _read_staged_file(gateway, py_file)
    if head is None or staged is None:
        return False
    head_fp = _ast_semantic_fingerprint(head)
    staged_fp = _ast_semantic_fingerprint(staged)
    return head_fp is not None and head_fp == staged_fp
