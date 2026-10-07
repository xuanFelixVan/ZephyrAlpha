# [BLUEPRINT] MOD-GOV-044 | src/zephyr/gov_enforcement/commit_gates/reconciler_file_ops_gate.py | §
# [MODULE] zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] （纯 stdlib；GateSpec 来自 commit_gate_registry）
# [CONSUMERS] gate_auto_registrar（in_process_gate_registry.yaml 条目驱动）
# [STARTUP] imported by gate_auto_registrar
# [MATURITY] production
# [INVARIANTS] own-diff 作用域只读扫描（C338：modified 只判本包新增行、新文件保持全文），零写入零副作用；ops_guard.py 自身豁免
# [MODIFY-GUARD] 裸原语正则与原语清单变更需同步 tests/gov/governance/commit_gates/test_reconciler_file_ops_gate.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描异常 → fail-open 放行 + reason 注明（不阻断无关 commit）
# [TESTS] —
# [TTL] permanent
"""
reconciler_file_ops_gate.py — 治理代理裸删除原语静态扫描门禁（RECONCILER-FILE-OPS）

#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1③ 双保险之一（2026-08-14 裁定）：
reconciler 删除/移动原语已全量收敛 ops_guard 安全 API（file_ops 声明制+审计+
回收站）。本 gate 防回流——staged 的治理代理代码新增裸 os.remove/os.unlink/
os.rmdir/os.rename/shutil.rmtree/shutil.move 调用即阻断。

运行时审计（另一保险）：ops_guard in-process 补丁 + guard_* API 全量落盘。

豁免：
- scripts/ops_guard.py 自身（补丁真源）
- tests/ 测试代码
- 行内 ``# ops-guard-exempt: <理由>`` 显式豁免标记

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/r/reconciler_file_ops_gate.yaml
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

__all__: Final = [
    "make_reconciler_file_ops_gate",
    "scan_file_for_bare_primitives",
    "scan_own_diff_for_bare_primitives",
]

#: 扫描范围（治理代理代码区，相对项目根前缀）
_SCAN_PREFIXES = (
    "src/zephyr/governance/",
    "src/zephyr/gov_enforcement/",
    "scripts/governance/",
    "scripts/backup/",
)

#: 豁免文件（补丁/安全 API 真源自身）
_EXEMPT_FILES = frozenset(
    {
        "scripts/ops_guard.py",
        # GW 提交基础设施自管锁/临时文件生命周期（lock/pathspec/msg 临时文件清理），
        # 非治理代理对用户/治理产物的业务删除——与 ops_guard.py"安全 API 真源自身"同族
        # （2026-08-20 波3 实证 19 处 5 文件存量浮出：format 重排致伪"新增"）
        "src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py",
        "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
        "src/zephyr/gov_enforcement/rule_bridge/session_worktree.py",
        "src/zephyr/gov_enforcement/rule_bridge/worktree_manager.py",
        "src/zephyr/gov_enforcement/rule_bridge/worktree_pool.py",
    }
)

#: 裸删除/移动原语调用形态（带括号的真实调用，注释/字符串提及不误伤）
_BARE_PRIMITIVE_RE = re.compile(r"\b(?:os\.remove|os\.unlink|os\.rmdir|os\.rename|shutil\.rmtree|shutil\.move)\s*\(")

#: 行内豁免标记
_EXEMPT_MARKER = "# ops-guard-exempt"


def scan_file_for_bare_primitives(path: Path) -> list[tuple[int, str]]:
    """扫描单文件全文裸删除/移动原语调用行（新文件路径与独立复测入口）。

    Returns:
        [(lineno, line_stripped), ...] 违规行清单（注释行/豁免标记行/docstring 行已过滤）。
    """
    from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: PLC0415
        _extract_docstring_lines,
    )

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    # 2026-08-20 波3 实证：审计脚本 docstring 枚举被审计原语（``os.remove()`` 等）致自扫误报，
    # docstring 行豁免与 bare_sql_gate（R95 _extract_docstring_lines）同口径
    doc_lines = _extract_docstring_lines(text)
    return _judge_lines(enumerate(text.splitlines(), 1), doc_lines)


def _judge_lines(numbered_lines, doc_lines: set[int]) -> list[tuple[int, str]]:
    """行级判定（全文/新增行两路共用的唯一真源，C338 拆件防口径漂移）。

    Returns:
        [(lineno, line_stripped), ...] 违规行清单。
    """
    hits: list[tuple[int, str]] = []
    for lineno, line in numbered_lines:
        if lineno in doc_lines:
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if _EXEMPT_MARKER in line:
            continue
        if _BARE_PRIMITIVE_RE.search(line):
            hits.append((lineno, stripped[:120]))
    return hits


def scan_own_diff_for_bare_primitives(gateway, rel: str, root: Path) -> list[tuple[int, str]]:
    """own-diff 作用域扫描（C338，#ARCH-GATE-OWN-SCOPE 同族口径，参照
    _diff_helpers own-scope 家族）：

    - modified 文件（HEAD 有此文件）＝只判本包新增行（unified=0 diff 行号集合化）
      ——存量违规不因 format 重排/无关触碰被误报为本包新增（2026-08-20 波3 同族
      病形：format 重排致伪"新增"）；
    - 新文件（HEAD 无此文件，含 git 故障 fail-open）＝保持全文扫描，语义不变窄；
    - fail-open：diff 不可得（[]）＝无新增证据，放行不误报（gate ERROR_CONTRACT：
      扫描异常 → fail-open 放行）。

    Returns:
        [(lineno, line_stripped), ...] 违规行清单。
    """
    from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: PLC0415
        _extract_docstring_lines,
        _get_added_lines,
        _read_head_file,
        _read_staged_file,
    )

    head_text = _read_head_file(gateway, rel)
    if head_text is None:
        # 新文件（或 HEAD 面不可读——保守退旧口径）：全文扫描，不收窄
        return scan_file_for_bare_primitives(root / rel)
    added = _get_added_lines(gateway, rel, gate_name="RECONCILER-FILE-OPS")
    if not added:
        return []  # 无新增行证据＝own-diff 放行（存量面不在本 gate 判责内）
    staged = _read_staged_file(gateway, rel)
    if staged is None:
        # index 面读不到 → 退磁盘（docstring 判定需全文上下文）；盘也无 → 放行
        try:
            staged = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []
    doc_lines = _extract_docstring_lines(staged)
    return _judge_lines(added, doc_lines)


def make_reconciler_file_ops_gate() -> GateSpec:
    """构造 RECONCILER-FILE-OPS 静态扫描门禁 GateSpec。

    priority=117：在 CONSUMERS-ACCURACY(116) 之后——语义层门禁先行，本 gate 管代码形态层。
    （priority 分配避让实录：114=DERIVATION-ANNOTATION / 116=CONSUMERS-ACCURACY 已占）
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        root = Path(str(gateway.project_root))
        violations: list[str] = []
        for f in files:
            rel = str(f).replace("\\", "/")
            if not rel.endswith(".py"):
                continue
            if rel in _EXEMPT_FILES or is_test_exempt(rel):
                continue
            # 排除 _archive 目录（归档一次性代码不参与扫描——同族先例：undefined_name_gate 裁定#E /
            # bare_sql_gate 2026-08-20 同口径补齐；归档脚本裸原语属冻结历史非回流新增）
            if "_archive" in rel:
                continue
            if not any(rel.startswith(p) for p in _SCAN_PREFIXES):
                continue
            try:
                hits = scan_own_diff_for_bare_primitives(gateway, rel, root)  # C338 own-diff 作用域（新文件保持全文）
            except Exception as e:  # noqa: BLE001 — 单文件扫描异常不阻断
                return True, f"scan degraded for {rel}: {e}"
            for lineno, snippet in hits:
                violations.append(f"  {rel}:{lineno}: {snippet}")

        if violations:
            return False, (
                "RECONCILER-FILE-OPS: 治理代理代码新增裸删除/移动原语（T1③ 防回流，"
                "#ARCH-RECONCILER-AUTO-DELETE-GOV-001）——删除/移动 MUST 收敛 "
                "ops_guard 安全 API（guard_remove/guard_rmtree/guard_move/guard_recycle，"
                "file_ops 声明制+全量审计+回收站可逆）：\n"
                + "\n".join(violations[:20])
                + ("\n  ...(more)" if len(violations) > 20 else "")
                + "\n逃生：确属补丁真源/特殊场景加行内标记 # ops-guard-exempt: <理由>"
            )
        return True, "no bare delete/move primitives in staged governance code"

    return GateSpec(gate_id="RECONCILER-FILE-OPS", check=_check, priority=117)
