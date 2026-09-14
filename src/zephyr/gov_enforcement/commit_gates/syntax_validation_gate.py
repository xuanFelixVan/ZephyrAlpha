# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.syntax_validation_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates._diff_helpers (_build_own_scope/_norm_rel/_audit_foreign_staged，own-scope 三件套)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（经 in_process_gate_registry.yaml auto_registrar 注册）；zephyr.gov_enforcement.rule_bridge.session_worktree.session_worktree_commit（worktree 通道 check_all 全量 gate）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——本 commit 提交清单（files 参数，网关 gate 链跑在 add 之前，files 才是真实入库内容源）中的 .py 文件 ast.parse 抛 SyntaxError 即阻断 commit（含文件名+行号+错误信息）；fail-closed 病根治本：全仓 6+ 个 AST 类 gate（create_guard/manual_only_permanent/bare_getenv/ch_final 等）对 SyntaxError 一律 fail-open 跳过（注释均写"语法错误由其他 gate 检测"——责任真空，实际无任何 gate 硬拦，红蓝 v3 S1.4 实弹：def broken(: 经主网关零拦截入库 2c6d1719d6）；本 gate 是语法错误唯一硬拦截真源；检测范围含 tests/（红蓝实证坏文件恰从 tests/ 进来），豁免只认 noqa 标记不认目录；AST 解析非 SyntaxError 异常（ValueError/UnicodeDecodeError 等）fail-open 放行（环境异常非违规，对标既有 gate 契约）；文件读取失败 fail-open；空 files 放行；noqa 豁免标记格式=# noqa: syntax-fixture + 2空格 + reason>=10字符（对标 m11-perm-manual-legitimate 模式，供测试夹具故意含语法坏文件时审计放行）；扫描源语义（probe 2i 实弹复验发现）：网关 gate 链跑在 git add 之前，暂存区只有上次手动 add 的残留，扫描暂存区会漏拦未暂存坏文件——扫描 files 参数才是真实入库内容
# [MODIFY-GUARD] gate_id="SYNTAX-VALIDATION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 失败/文件读取失败/非 SyntaxError 解析异常降级为 fail-open（passed=True，logger.warning）；SyntaxError 检出则 fail-closed 阻断（passed=False，detail 含文件名+行号+错误）
# [TESTS] tests/governance/commit_gates/test_syntax_validation_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
syntax_validation_gate.py — staged .py 文件语法错误硬阻断门禁（SYNTAX-VALIDATION，红蓝 v3 P0-1 批 2 治本）

病根（红蓝 v3 报告 §1 P0-1，2026-09-13 S1.4 实弹）
------------------------------------------------
语法坏文件零拦截入库。``def broken(:`` 的 Python 文件经主网关提交成功
（commit 2c6d1719d6，事后清理），全程无任何语法/AST 类 gate 拦截，堵点本零记录。

深挖根因：全仓 6+ 个 AST 类 gate 全部 ``except SyntaxError: fail-open``，
注释都写着"语法错误由其他 gate 检测"（create_guard.py / manual_only_permanent_gate.py /
bare_getenv_gate.py / ch_final_gate.py 等均有此模式）——责任真空，
实际没有任何 gate 硬拦语法错误。

治本方案
--------
本 gate 填补责任真空：staged 的 .py 文件逐个 ``ast.parse``，
SyntaxError 即 fail-closed 阻断（detail 含文件名+行号+错误信息）。

与既有 AST 类 gate 的关系
--------------------------
- 既有 AST gate（BLUEPRINT-NODE-ID-HARDCODE / FUNCTION-DUP / NO-GOD-CLASS 等）
  遇 SyntaxError 自己 fail-open 跳过该文件——它们检测的是"结构语义"，
  语法合法性由本 gate 唯一负责。
- 本 gate priority=49：排在协调类 gate（WORKTREE-REQUIRED=44 / FOREIGN-CHANGE=45 /
  DERIVED-FILE-DELETION=46 / HOT-FILE-BASE-FRESHNESS=47）与 COMMIT-SCOPE=48 之后、
  全部 AST 消费型 gate（54+）之前——语法错误先于 AST gate 静默 skip 报出。

设计权衡
--------
1. **检测范围含 tests/**：红蓝实证坏文件就是从 tests/ 进来的。
   tests/ 豁免边界是本设计唯一的坑——但探查结论（2026-09-14）：
   全仓 8003 个 tracked .py 文件 ast.parse 全通过，测试夹具里的坏语法
   全部是运行时在 tmp_path/内存字符串生成的，无 tracked 夹具依赖坏语法。
   仍保留 noqa 审计逃生口（未来真需要 tracked 坏语法夹具时用）。
2. **noqa 豁免标记**：``# noqa: syntax-fixture  <理由≥10字符>``
   （对标 manual_only_permanent_gate 的 m11 模式）。豁免只认标记不认目录。
3. **非 SyntaxError 解析异常 fail-open**：ValueError（null bytes 等源码级问题
   ast.parse 会抛 ValueError）/MemoryError 等视为环境异常放行——对标既有 gate
   "检测器失效不误伤提交人" 契约。SyntaxError 是唯一确定的违规信号。
4. **in-process AST**：纯 ast.parse，无 subprocess，自包含。
5. **UTF-8 errors=replace 读取**：编码坏文件（乱码/二进制）在 replace 后
   parse 通常抛 SyntaxError（若抛）——ENCODING-SAFETY(42) 已管编码规范，
   本 gate 优先报语法。真正 null-byte 文件抛 ValueError 走 fail-open。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: syntax_validation_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_syntax_validation_gate
#   name_en: make_syntax_validation_gate
#   intro: 构造 staged .py 语法错误硬阻断门禁 GateSpec（fail-closed 型）。
#   desc: 构造 staged .py 语法错误硬阻断门禁 GateSpec（fail-closed 型）。 Returns: GateSpec(gate_id="SYNTAX-VALIDATION", priority=49)；源码 L207-L268
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

import ast
import logging
import os
import re

from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import _build_own_scope, _norm_rel
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_syntax_validation_gate"]

# syntax-fixture noqa 豁免标记正则（对标 m11-perm-manual-legitimate 模式）
# 格式：`# noqa: syntax-fixture` + 2+ 空格 + reason（>= 10 字符，rstrip 后计数）
_SYNTAX_FIXTURE_NOQA_PATTERN: Final = re.compile(
    r"#\s*noqa:\s*syntax-fixture\s{2,}(\S.*)$",
    re.MULTILINE,
)

# 单次阻断消息中最多展示的违规文件数（防日志爆炸，对标既有 gate 的 [:5] 截断）
_MAX_VIOLATIONS_IN_DETAIL: Final[int] = 5


def _has_syntax_fixture_exemption(content: str) -> bool:
    """检测文件是否含合规的 syntax-fixture noqa 豁免标记。

    合规条件（与 m11-perm-manual-legitimate 一致的格式契约）：
      1. 含 ``# noqa: syntax-fixture`` 标记（``#`` 引导，``noqa:`` 前缀）
      2. 标记后跟 2+ 空格分隔的 reason
      3. reason 长度 >= 10 字符（rstrip 后计数）

    用途：测试夹具确实需要 tracked 坏语法文件时（2026-09-14 探查=零存量，
    此为未来逃生口），以显式标记+理由放行，保持审计可见性。

    Args:
        content: 文件全文内容。

    Returns:
        True = 含合规豁免标记（该文件跳过语法检查）；
        False = 无标记 / reason 不足 10 字符。
    """
    for match in _SYNTAX_FIXTURE_NOQA_PATTERN.finditer(content):
        reason = match.group(1).rstrip()
        if len(reason) >= 10:
            return True
    return False


def _resolve_wt_root(gateway) -> str:
    """解析 worktree root（绝对路径），供相对路径→绝对路径拼接。

    fail-open：git rev-parse 失败/异常时回退 gateway.project_root。
    """
    try:
        toplevel = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        return toplevel.stdout.strip() if toplevel.returncode == 0 else str(gateway.project_root)
    except Exception:  # noqa: BLE001 — broad exception catch for fail-open
        return str(getattr(gateway, "project_root", "."))


def _scan_py_file_syntax(rel_path: str, wt_root: str) -> str:
    """对单个 .py 文件 ast.parse，返回违规描述（空串=合规或跳过）。

    fail-open 契约：文件读取失败/非 SyntaxError 解析异常降级为放行（logger.warning）。
    """
    abs_path = rel_path if os.path.isabs(rel_path) else os.path.join(wt_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return ""  # delete/幻影场景：跳过

    try:
        with open(abs_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        logger.warning(
            "SYNTAX-VALIDATION gate skip file %s: 读取失败(%s: %s)。",
            abs_path,
            type(e).__name__,
            e,
        )
        return ""

    # noqa 豁免（测试夹具逃生口，对标 m11 模式）
    if _has_syntax_fixture_exemption(content):
        return ""

    try:
        ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        return f"{rel_path}:{e.lineno}: {e.msg}" + (
            f"（{os.path.basename(abs_path)} 第 {e.lineno} 行）" if e.lineno else ""
        )
    except Exception as e:  # noqa: BLE001 — ValueError/MemoryError 等环境异常 fail-open
        logger.warning(
            "SYNTAX-VALIDATION gate skip file %s: 解析异常(%s: %s)。",
            abs_path,
            type(e).__name__,
            e,
        )
        return ""
    return ""


def make_syntax_validation_gate() -> GateSpec:
    """构造 staged .py 语法错误硬阻断门禁 GateSpec（fail-closed 型）。

    Returns:
        GateSpec(gate_id="SYNTAX-VALIDATION", priority=49)。
        priority=49——排在协调类 gate（WORKTREE-REQUIRED=44 / FOREIGN-CHANGE=45 /
        DERIVED-FILE-DELETION=46 / HOT-FILE-BASE-FRESHNESS=47）与 COMMIT-SCOPE(48)
        之后、AST 消费型 gate（54+）之前的空闲位，
        语法错误先于 AST gate 静默 fail-open 报出。
        （初选 48 与 COMMIT-SCOPE 撞号，auto_registrar 实测抓出后让位 49——
        对齐 GateRegistrationError 报错内的后到者让位先例。）
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 扫描源=本 commit 真实提交清单（files 参数）而非暂存区——网关时序：
        # gate 链跑在 git add 之前（_check_gates_with_drift_watch → _commit_locked/add），
        # 暂存区只有上次手动 add 的残留；扫描暂存区会漏拦未暂存的坏文件
        # （probe 2i 实弹复验发现的盲区，2026-09-14）。files 由 commit() 归一化为
        # 绝对路径，是本次 commit 的最终内容源，扫描它=扫描真正要入库的东西。
        py_files = [str(f).replace("\\", "/") for f in files or [] if str(f).endswith(".py")]
        if not py_files:
            return True, ""
        wt_root = _resolve_wt_root(gateway)

        # 1.5 own-scope 过滤（#ARCH-310 R2，对标 NOQA-VALIDATION 模式）：扫描范围=
        # 本 commit files∪held；own_scope=None（未注册/直调场景）时退化为不过滤
        # （files 本身就是本 commit 清单，语义已自洽）。
        session_id = kwargs.get("session_id")
        own_scope = _build_own_scope(gateway, files, session_id)
        if own_scope is not None:
            py_files = [f for f in py_files if _norm_rel(gateway, f) in own_scope]
            if not py_files:
                return True, ""

        # 2. 逐文件 ast.parse，收集 SyntaxError 违规（单文件逻辑见 _scan_py_file_syntax）
        violations = [v for v in (_scan_py_file_syntax(rel, wt_root) for rel in py_files) if v]

        if violations:
            shown = "; ".join(violations[:_MAX_VIOLATIONS_IN_DETAIL])
            hidden = len(violations) - _MAX_VIOLATIONS_IN_DETAIL
            suffix = f"（另有 {hidden} 个文件未展示）" if hidden > 0 else ""
            return False, (
                f"staged Python 文件存在语法错误（SYNTAX-VALIDATION，红蓝 v3 P0-1 治本——"
                f"修复后再提交；确属测试夹具需保留坏语法时在文件内加 "
                f"'# noqa: syntax-fixture  <理由≥10字符>' 标记）: {shown}{suffix}"
            )
        return True, ""

    return GateSpec(gate_id="SYNTAX-VALIDATION", check=_check, priority=49)
