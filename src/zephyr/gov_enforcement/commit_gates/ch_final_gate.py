# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.ch_final_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——① staged 新增/修改 .py 直接调用 ch_writer.query() 时阻断（应改用 ch_reader.query() 自动注入 FINAL）；②staged .py 内字符串常量硬编码 `FROM <db>.<tbl>` 且该表引擎为 ReplacingMergeTree 而文本内无 FINAL、容器内无 ch_reader/inject_final 载体时阻断（覆盖 DatabaseService.get_clickhouse_conn().execute() 直连面，own-diff 作用域）; ch_reader.py/ch_writer.py 豁免; tests/ 豁免; 新增文件全文件 AST 检测; 修改文件检测 staged diff 新增行文本模式; AST/git 异常 fail-open; 引擎解析失败（CH 不可达）记 WARNING 出声、不静默放行；own 化 2026-09-23(st-gslim P2)：扫描范围=全暂存∩本 session，外来 staged warn+审计不阻断(_split_own_foreign)
# [MODIFY-GUARD] gate_id="CH-FINAL-GATE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——AST/IO/git/CH 引擎查询异常降级为 fail-open（passed=True，logger.warning）; 检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_ch_final_gate_no_final_reads.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ch_final_gate.py — ch_writer.query() 直接调用阻断门禁（CH-FINAL-GATE，裁定 #ARCH-CH-007 B5）

检测 staged .py 文件中是否直接调用 ch_writer.query()。
违反裁定 #ARCH-CH-007：所有 ClickHouse 查询应走 ch_reader.query() 自动注入 FINAL。

病根（第一性原理）
-----------------
ReplacingMergeTree 的去重是异步的（后台 merge 时才去重）。
查询时需加 FINAL 关键字强制去重。100% AI 开发模式下，AI 不会主动加 FINAL。
ch_reader.query() 自动注入 FINAL，但 AI 可能绕过 ch_reader 直接用 ch_writer.query()。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁：
  1. 新增文件(A)：全文件 AST 检测 ch_writer.query() 调用
  2. 修改文件(M)：检测 staged diff 新增行中的文本模式
  3. ch_reader.py / ch_writer.py 豁免（基础设施）
  4. tests/ 豁免

Usage::

    from zephyr.gov_enforcement.commit_gates.ch_final_gate import make_ch_final_gate

    registry.register(make_ch_final_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/ch_final_gate.yaml
"""

from __future__ import annotations

import ast
import logging
import os
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _build_own_scope,
    _extract_noqa_lines,
    _get_added_lines,
    _make_noqa_pattern,
    _norm_rel,
    _split_own_foreign,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_ch_final_gate"]

# ch_writer.query() 文本模式（用于 diff 新增行检测，覆盖常见别名 ch_writer / _chw）
_QUERY_CALL_PATTERN = re.compile(r"\b(ch_writer|_chw)\s*\.\s*query\s*\(")

# 基础设施文件豁免（文件名后缀）——ch_reader 内部调用 ch_writer.query 是正常的
_INFRA_EXEMPT_SUFFIXES = ("ch_reader.py", "ch_writer.py")

# ── 判据②（2026-09-18 红队 st-ff-pit2 加严）：无 FINAL 直读 ReplacingMergeTree ──
# 病根：判据①只盯 ch_writer.query()，而经
#   DatabaseService.get_clickhouse_conn().execute() 直连的 SQL 完全不过任何门禁
#   ⇒ 生产读路径可在合并未完成时读到未去重行（同键多版本、量纲相差 100 倍）。
# 覆盖面（如实）：只识别**字符串常量里硬编码的 `FROM <db>.<tbl>`**；
#   经 table_registry.get_registry().table(...) 以 f-string 变量注入表名的 SQL
#   静态不可见（这类位点由 ch_reader/inject_final 或人工纪律保证），本判据不覆盖。
# 判据面限定为"像 SQL 的常量"，并要求 db.tbl 后不接点号——
# 否则 Python 的 `from zephyr.data.ch_reader import x`（大小写不敏感的 from）、
# 散文里的 "derived from c1_market.kline_daily" 一类都会假红。
#
# ★ 2026-09-18 st-ff-gov2 复测修正：尾闸必须是 `(?![\w.])` 而非 `(?!\s*\.)`。
#   旧写法可被 **`\w+` 回溯**绕过：`FROM zephyr.data.ch_reader` 里 `data` 后接点号使
#   先行失败，引擎遂回溯成 `dat`（后接 `a`，非点号→先行通过），把 dotted 模块路径
#   **截断成假表名 `zephyr.dat`**——实测正是提交期
#   `CH-FINAL-GATE 判据②降级：2 个表引擎不可解析…['zephyr.dat','zephyr.data']` 的来源。
#   回溯型先行等于把"三段点号路径不判"降级成"判成两段的错表名"：既制造噪声、
#   又把真表名的判定面偷偷挪走（不可判定被当成豁免的同族病，#273）。
#   `(?![\w.])` 同时拒绝词字符与点号 ⇒ 回溯无出路，整条 FROM 匹配失败（真截断源）。
#   第二道闸 `(?!\s+import\b)`：两段点号名 `zephyr.data` 与 `db.tbl` 形状完全同构，
#   正则层面不可分（实测 scripts/ch/apply_market_tables_ddl.py:1190 的代码模板常量
#   含 `"from zephyr.data import ch_reader, ch_writer"` ⇒ 被当成表 `zephyr.data` 送去查引擎
#   ⇒ 又是一条降级噪声）。`import` 不是 SQL 保留字、也不可能在表引用后合法出现，
#   故"FROM x.y 紧跟 import"必是 Python 导入语句，判非表引用（通用判据，非白名单）。
_DB_QUALIFIED_FROM = re.compile(r"\bFROM\s+`?(\w+)`?\s*\.\s*`?(\w+)`?(?![\w.])(?!\s+import\b)", re.IGNORECASE)
_SQL_SHAPE = re.compile(r"\b(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|WITH)\b", re.IGNORECASE)
_FINAL_KEYWORD = re.compile(r"\bFINAL\b", re.IGNORECASE)
_FROM_KEYWORD = re.compile(r"\bFROM\b", re.IGNORECASE)
# 系统库/信息库不是 ReplacingMergeTree，且是门禁与诊断脚本的常规读取对象
_SKIP_DATABASES = frozenset({"system", "information_schema"})
# 容器内出现这些调用即认为走了自动注入面
_READER_INJECT_FUNCS = frozenset({"query", "query_table", "count"})
_NOQA_GATE_ID = "ch-final"


def _docstring_constant_ids(tree: ast.AST) -> set[int]:
    """收集模块/函数/类 docstring 的 Constant 节点 id（docstring 里的示例 SQL 不算违规）。"""
    doc_ids: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        if not isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            doc_ids.add(id(first.value))
    return doc_ids


def _has_reader_carrier(node: ast.AST) -> bool:
    """容器内是否存在自动注入 FINAL 的载体（ch_reader.query/query_table/count 或 inject_final）。

    inject_final 两种写法都要认：`ch_reader.inject_final(sql)`（Attribute）与
    `from zephyr.data.ch_reader import inject_final` 后的裸调用（Name）——后者漏认会把
    已正确注入的位点判成违规（本车道实测的第一批假红即此）。
    """
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if isinstance(func, ast.Attribute):
            if func.attr == "inject_final":
                return True
            if func.attr in _READER_INJECT_FUNCS and isinstance(func.value, ast.Name):
                if "reader" in func.value.id.lower():
                    return True
        elif isinstance(func, ast.Name) and func.id == "inject_final":
            return True
    return False


def _build_containers(tree: ast.AST) -> list[tuple[int, int, int, bool]]:
    """(跨度, 起, 止, 含注入载体) 列表，按跨度升序——用于取"最内层容器"。

    不含 Module：模块级 SQL 常量若因"该文件别处调过一次 ch_reader"就被整体豁免，
    等于给一个文件只注入一次就畅通无阻开后门（判据放松，#321 禁）。
    """
    containers: list[tuple[int, int, int, bool]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        start = getattr(node, "lineno", 1) or 1
        end = getattr(node, "end_lineno", start) or start
        containers.append((end - start + 1, start, end, _has_reader_carrier(node)))
    containers.sort()
    return containers


def _reader_covered(containers: list[tuple[int, int, int, bool]], lineno: int) -> bool:
    """该行所属最内层容器是否已有 FINAL 注入载体。"""
    for _, start, end, has_carrier in containers:
        if start <= lineno <= end:
            return has_carrier
    return False


def _resolve_engine(full_table: str) -> str:
    """查表引擎（复用 ch_writer.get_table_engine 的进程内缓存=单一真源）。

    延迟 import：门禁模块在 gateway 启动期被 import，不得因数据层不可用而打死提交通道。

    Returns:
        引擎名字符串；解析失败（CH 不可达 / 表不存在 / import 失败）返回空串。
    """
    try:
        from zephyr.data import ch_writer  # noqa: PLC0415 — 延迟 import 见 docstring
    except Exception as e:  # noqa: BLE001 — 数据层不可得时降级，不得打死 gateway
        logger.warning("CH-FINAL-GATE 引擎解析不可用（import ch_writer 失败）: %s", e)
        return ""
    try:
        return ch_writer.get_table_engine(full_table) or ""
    except Exception as e:  # noqa: BLE001 — CH 不可达时降级，由调用侧出声
        logger.warning("CH-FINAL-GATE 引擎解析异常 table=%s: %s", full_table, e)
        return ""


def _iter_sql_constants(tree: ast.AST) -> list[tuple[int, int, str]]:
    """过筛"像 SQL 的字符串常量"：非 docstring + 含 FROM + 形状含 SELECT 族关键字。

    Returns:
        (首行, 末行, 字面量值) 列表；末行用于隐式拼接的多行常量整体判定。
    """
    doc_ids = _docstring_constant_ids(tree)
    found: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if id(node) in doc_ids or not _FROM_KEYWORD.search(node.value):
            continue
        if not _SQL_SHAPE.search(node.value):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", start) or start
        found.append((start, end, node.value))
    return found


def _tables_to_judge(
    value: str, start: int, containers: list[tuple[int, int, int, bool]], seen: set[tuple[int, str]]
) -> list[str]:
    """单个 SQL 常量里需要查引擎的表名（去重/系统库/已被注入载体覆盖的都在此剔除）。"""
    tables: list[str] = []
    for db, tbl in _DB_QUALIFIED_FROM.findall(value):
        full = f"{db}.{tbl}"
        if db.lower() in _SKIP_DATABASES or (start, full.lower()) in seen:
            continue
        seen.add((start, full.lower()))
        if _reader_covered(containers, start):
            continue
        tables.append(full)
    return tables


def _scan_missing_final_reads(
    content: str, rel_path: str, added_lines: set[int] | None, noqa_lines: set[int]
) -> tuple[list[str], list[str]]:
    """检测"硬编码 FROM <db>.<tbl> 且无 FINAL 且无注入载体"的直连读。

    Args:
        content: 文件全文（staged 或工作区字节）。
        rel_path: 相对路径（仅用于违规描述）。
        added_lines: own-diff 作用域——仅这些新文件行号参与判定；None=全文件（新增文件）。
        noqa_lines: 带 ``noqa: ch-final`` 行内注释（井号前缀 + 两空格 + 理由）的行号，跳过。

    Returns:
        (违规描述列表, 引擎未能解析的表名列表)——后者非空即判据降级，须出声不静默。

    2026-09-18 st-ff-gov2 落地前置拆分：原单体实现圈复杂度 19 > 15，被
    NO-HIGH-COMPLEXITY 硬拦进死信（`q-20260918-st-ff-gov2-20260918-0002`）——
    即阵亡车道的半成品**从未具备可落地性**。现拆为
    `_iter_sql_constants`（选常量）+ `_tables_to_judge`（选表）+ 本函数（判定与出声），
    **判据语义逐行不变**（含 seen 的先记后判顺序），由 31 件测试钉住。
    """
    try:
        tree = ast.parse(content, filename=rel_path)
    except SyntaxError as e:
        logger.warning("CH-FINAL-GATE 判据② AST 解析失败 %s: %s", rel_path, e)
        return [], []
    containers = _build_containers(tree)
    violations: list[str] = []
    unresolved: list[str] = []
    seen: set[tuple[int, str]] = set()
    for start, end, value in _iter_sql_constants(tree):
        span = set(range(start, end + 1))
        if added_lines is not None and not (span & added_lines):
            continue
        if span & noqa_lines:
            continue
        if _FINAL_KEYWORD.search(value):
            continue
        for full in _tables_to_judge(value, start, containers, seen):
            engine = _resolve_engine(full)
            if not engine:
                unresolved.append(full)
                continue
            if "Replacing" in engine:
                violations.append(f"{rel_path}:L{start} (FROM {full} 无 FINAL 且未走 ch_reader)")
    return violations, unresolved


def _check_missing_final(gateway, rel_path: str, abs_path: str, added_lines: set[int] | None) -> list[str]:
    """判据②入口：读文件 → 扫无 FINAL 直连读 → 引擎不可解析时出声。"""
    try:
        with open(abs_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        logger.warning("CH-FINAL-GATE 判据②跳过 %s: 读取失败(%s)", abs_path, e)
        return []
    violations, unresolved = _scan_missing_final_reads(
        content, rel_path, added_lines, _extract_noqa_lines(content, _make_noqa_pattern(_NOQA_GATE_ID))
    )
    if unresolved:
        # 不静默放行：引擎面不可得 ⇒ 本轮该判据是"降级观测"，必须留痕可审计
        logger.warning(
            "CH-FINAL-GATE 判据②降级：%d 个表引擎不可解析（CH 不可达或表不存在），本轮未判定: %s",
            len(unresolved),
            sorted(set(unresolved))[:10],
        )
    return violations


def _added_line_numbers(gateway, rel_path: str) -> set[int]:
    """staged diff 的新文件行号集合（own-diff 作用域；git 失败→空集=不判定）。"""
    return {ln for ln, _ in _get_added_lines(gateway, rel_path, "CH-FINAL-GATE")}


def _collect_ch_writer_aliases(tree: ast.AST) -> set[str]:
    """收集 AST 中 ch_writer 的 import 别名。"""
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "ch_writer":
                    aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.endswith(".ch_writer") or alias.name == "ch_writer":
                    aliases.add(alias.asname or alias.name.split(".")[-1])
    return aliases


def _find_query_calls(tree: ast.AST, aliases: set[str]) -> list[int]:
    """检测 AST 中 alias.query() 调用，返回行号列表。"""
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "query" and isinstance(node.func.value, ast.Name):
                if node.func.value.id in aliases:
                    lines.append(node.lineno)
    return lines


def _is_infra_exempt(rel_path: str) -> bool:
    """检查文件是否为基础设施豁免（ch_reader.py / ch_writer.py / commit_gates/ 门禁检测器自身）。

    2026-08-20 波3 实证：本 gate 源码 docstring/pattern 含 ch_writer.query() 字面量（检测语义描述），
    modified 路径文本扫描自扫误报——与 msg_style/msg_exposure/perm_trigger/manual_only 自豁免
    同族补齐（commit_gates/ 子串匹配不限定父目录，防 governance→gov_enforcement 式迁移漂移）。
    2026-09-12 实证（apply_crypto_shadow_tables_ddl.py 首采批）：DDL 部署脚本（apply_*_ddl.py）
    的 writer.query 执行 CREATE/ALTER 语句是合法场景（FINAL 语义只作用于 SELECT，reader 只读账号
    无权建表）——部署脚本文件级豁免；配套纪律=部署脚本内 SELECT 验证一律 ch_reader.query。"""
    normalized = rel_path.replace("\\", "/")
    if "commit_gates/" in normalized:
        return True
    basename = normalized.rsplit("/", 1)[-1]
    if basename.startswith("apply_") and basename.endswith("_ddl.py"):
        return True
    return any(normalized.endswith(s) for s in _INFRA_EXEMPT_SUFFIXES)


def _check_new_file(abs_path: str, rel_path: str) -> str | None:
    """新增文件全文件 AST 检测，返回违规描述或 None。"""
    try:
        with open(abs_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        logger.warning("CH-FINAL-GATE skip %s: 读取失败(%s)", abs_path, e)
        return None
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning("CH-FINAL-GATE skip %s: AST 解析失败(%s)", abs_path, e)
        return None
    aliases = _collect_ch_writer_aliases(tree)
    if not aliases:
        return None
    lines = _find_query_calls(tree, aliases)
    if lines:
        return f"{rel_path}:L{lines[0]} (ch_writer.query → ch_reader.query)"
    return None


def _check_modified_file(gateway, rel_path: str) -> str | None:
    """修改文件检测 staged diff 新增行中的 ch_writer.query 文本模式。"""
    try:
        diff_content = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", rel_path])
        if diff_content.returncode != 0:
            return None
        added_lines = [
            line[1:] for line in diff_content.stdout.splitlines() if line.startswith("+") and not line.startswith("+++")
        ]
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None
    for line in added_lines:
        if _QUERY_CALL_PATTERN.search(line):
            return f"{rel_path} (modified: 新增 ch_writer.query 调用)"
    return None


def _get_staged_py_files(gateway) -> list[str]:
    """获取 staged added/modified .py 文件（过滤 tests/ 和基础设施豁免）。"""
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning("CH-FINAL-GATE fail-open: git diff 失败(rc=%d)", diff_result.returncode)
            return []
        staged = diff_result.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("CH-FINAL-GATE fail-open: git diff 异常(%s: %s)", type(e).__name__, e)
        return []
    return [
        f.replace("\\", "/") for f in staged if f.endswith(".py") and not is_test_exempt(f) and not _is_infra_exempt(f)
    ]


def _get_wt_root(gateway) -> str:
    """获取 worktree root 路径。"""
    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        return toplevel.stdout.strip() if toplevel.returncode == 0 else str(gateway.project_root)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return str(gateway.project_root)


def _get_added_set(gateway) -> set[str]:
    """获取 staged 新增(A)文件集合。"""
    try:
        added_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        return set(added_result.stdout.strip().splitlines()) if added_result.returncode == 0 else set()
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return set()


def _scan_violations(gateway, py_files: list[str], added_set: set[str], wt_root: str) -> list[str]:
    """逐文件检测两类违规，返回违规描述列表。

    判据①：直接调用 ch_writer.query()（绕开 ch_reader 的 FINAL 自动注入）；
    判据②：硬编码 ``FROM <db>.<tbl>`` 直读 ReplacingMergeTree 而无 FINAL
    （覆盖 ``DatabaseService.get_clickhouse_conn().execute()`` 这类不经 ch_reader 的直连面）。
    """
    violations: list[str] = []
    for rel_path in py_files:
        abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            continue
        is_new = rel_path in added_set
        v = _check_new_file(abs_path, rel_path) if is_new else _check_modified_file(gateway, rel_path)
        if v:
            violations.append(v)
        added_lines = None if is_new else _added_line_numbers(gateway, rel_path)
        if is_new or added_lines:
            violations.extend(_check_missing_final(gateway, rel_path, abs_path, added_lines))
    return violations


def make_ch_final_gate() -> GateSpec:
    """构造 ch_writer.query() 直接调用阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CH-FINAL-GATE", priority=37)。
        priority=37——紧邻 CH-BATCH-SIZE(36)，同为 ClickHouse 相关门禁。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = _get_staged_py_files(gateway)
        if not py_files:
            return True, ""
        # own 化（st-gslim-20260923 P2）：只检本 session staged，外来 warn+审计不阻断
        py_files = _split_own_foreign(gateway, py_files, files, kwargs.get("session_id"), gate_name="CH-FINAL-GATE")[0]
        if not py_files:
            return True, ""
        wt_root = _get_wt_root(gateway)
        added_set = _get_added_set(gateway)
        own_scope = _build_own_scope(gateway, files, kwargs.get("session_id"))
        if own_scope is not None:
            added_set = {f for f in added_set if _norm_rel(gateway, f) in own_scope}
        violations = _scan_violations(gateway, py_files, added_set, wt_root)
        if not violations:
            return True, ""
        detail = "; ".join(violations[:5])
        return False, (
            "ClickHouse 读取未强制去重（裁定 #ARCH-CH-007）：直调 ch_writer.query() 应改 ch_reader.query()，"
            f"硬编码 FROM <db>.<tbl> 直读 ReplacingMergeTree 须带 FINAL 或走 ch_reader（可加行内注释 "
            f"noqa: ch-final 两空格+理由 逐行豁免）: {detail}"
        )

    return GateSpec(gate_id="CH-FINAL-GATE", check=_check, priority=37)
