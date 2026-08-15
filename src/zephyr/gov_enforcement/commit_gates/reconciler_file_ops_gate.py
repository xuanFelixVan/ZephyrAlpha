# [BLUEPRINT] MOD-GOV-044 | src/zephyr/gov_enforcement/commit_gates/reconciler_file_ops_gate.py | §
# [MODULE] zephyr.gov_enforcement.commit_gates.reconciler_file_ops_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] （纯 stdlib；GateSpec 来自 commit_gate_registry）
# [CONSUMERS] gate_auto_registrar（in_process_gate_registry.yaml 条目驱动）
# [STARTUP] imported by gate_auto_registrar
# [MATURITY] production
# [INVARIANTS] 只读扫描 staged 文件全文，零写入零副作用；ops_guard.py 自身豁免
# [MODIFY-GUARD] 裸原语正则与原语清单变更需同步 tests/governance/commit_gates/test_reconciler_file_ops_gate.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 扫描异常 → fail-open 放行 + reason 注明（不阻断无关 commit）
# [TESTS] tests/governance/commit_gates/test_reconciler_file_ops_gate.py
# [TTL] permanent
"""reconciler_file_ops_gate.py — 治理代理裸删除原语静态扫描门禁（RECONCILER-FILE-OPS）

#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1③ 双保险之一（2026-08-14 裁定）：
reconciler 删除/移动原语已全量收敛 ops_guard 安全 API（file_ops 声明制+审计+
回收站）。本 gate 防回流——staged 的治理代理代码新增裸 os.remove/os.unlink/
os.rmdir/os.rename/shutil.rmtree/shutil.move 调用即阻断。

运行时审计（另一保险）：ops_guard in-process 补丁 + guard_* API 全量落盘。

豁免：
- scripts/ops_guard.py 自身（补丁真源）
- tests/ 测试代码
- 行内 ``# ops-guard-exempt: <理由>`` 显式豁免标记
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

__all__: Final = ["make_reconciler_file_ops_gate", "scan_file_for_bare_primitives"]

#: 扫描范围（治理代理代码区，相对项目根前缀）
_SCAN_PREFIXES = (
    "src/zephyr/governance/",
    "src/zephyr/gov_enforcement/",
    "scripts/governance/",
    "scripts/backup/",
)

#: 豁免文件（补丁/安全 API 真源自身）
_EXEMPT_FILES = frozenset({
    "scripts/ops_guard.py",
})

#: 裸删除/移动原语调用形态（带括号的真实调用，注释/字符串提及不误伤）
_BARE_PRIMITIVE_RE = re.compile(
    r"\b(?:os\.remove|os\.unlink|os\.rmdir|os\.rename|shutil\.rmtree|shutil\.move)\s*\("
)

#: 行内豁免标记
_EXEMPT_MARKER = "# ops-guard-exempt"


def scan_file_for_bare_primitives(path: Path) -> list[tuple[int, str]]:
    """扫描单文件裸删除/移动原语调用行。

    Returns:
        [(lineno, line_stripped), ...] 违规行清单（注释行/豁免标记行已过滤）。
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    hits: list[tuple[int, str]] = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if _EXEMPT_MARKER in line:
            continue
        if _BARE_PRIMITIVE_RE.search(line):
            hits.append((lineno, stripped[:120]))
    return hits


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
            if not any(rel.startswith(p) for p in _SCAN_PREFIXES):
                continue
            try:
                hits = scan_file_for_bare_primitives(root / rel)
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
