# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_domain_library/blueprint.md | §5
# [MODULE] zephyr.gov_enforcement.commit_gates.library_coverage_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] gate_auto_registrar（in_process_gate_registry.yaml 条目驱动）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] warn-only 观察窗（W+1 收紧硬闸）：own-scope 新增 .py/.md 无索书号表头（asset_id 键或 # asset: 注释）即 logger.warning 列表；永不阻断（passed 恒 True）
# [MODIFY-GUARD] gate_id="LIBRARY-COVERAGE"
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——任何内部异常降级 fail-open（passed=True，logger.warning）
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""library_coverage_gate.py — 馆藏覆盖观察闸（LIBRARY-COVERAGE，warn-only）。

蓝图书店员四层强制的 L1 前哨（03 §4/08 §7）：own-scope 新增 .py/.md 文件
头部 30 行内无索书号（frontmatter ``asset_id:`` 或 ``# asset:`` 注释）即警告。
W+1 收紧为硬闸（呈批后）。真源：docs/_working/ultimate_library/08 §7。

Usage::

    from zephyr.gov_enforcement.commit_gates.library_coverage_gate import make_library_coverage_gate

    registry.register(make_library_coverage_gate())
# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/l/library_coverage_gate.yaml
"""

from __future__ import annotations

import logging
from typing import Final

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _build_own_scope,
    _get_staged_py_files,
    _norm_rel,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_library_coverage_gate"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）


def _has_call_number(content: str) -> bool:
    """检查文件头部 30 行是否含索书号（asset_id 键或 # asset: 注释）。

    Args:
        content: 文件全文。

    Returns:
        True=有索书号。
    """
    for line in content.splitlines()[:30]:
        stripped = line.strip()
        if stripped.startswith("asset_id:") or stripped.startswith("# asset:"):
            return True
    return False


def make_library_coverage_gate() -> GateSpec:
    """构造馆藏覆盖观察 GateSpec（warn-only）。

    Returns:
        GateSpec(gate_id="LIBRARY-COVERAGE", priority=145)。

    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        try:
            staged = [
                f for f in _get_staged_py_files(gateway, gate_name="LIBRARY-COVERAGE") if f.endswith((".py", ".md"))
            ]
            extra = [f for f in getattr(gateway, "staged_files", []) or [] if f.endswith(".md") and f not in staged]
            staged = staged + extra
            if not staged:
                return True, ""
            session_id = kwargs.get("session_id")
            own_scope = _build_own_scope(gateway, files, session_id)
            if own_scope is not None:
                staged = [f for f in staged if _norm_rel(gateway, f) in own_scope]
            missing: list[str] = []
            for path in staged:
                norm = path.replace("\\", "/")
                if "/_working/" in f"/{norm}" or norm.startswith("_working/"):
                    continue  # 梵蒂冈条款：场外区（working/临时）免索书号
                content = _read_staged_file(gateway, path)
                if content and not _has_call_number(content):
                    missing.append(path)
            if missing:
                logger.warning(
                    "LIBRARY-COVERAGE (warn-only): %d 个新增文件无索书号表头（W+1 收紧硬闸）: %s",
                    len(missing),
                    ", ".join(missing[:10]),
                )
            return True, ""
        except Exception as exc:  # noqa: BLE001 — 观察闸 fail-open
            logger.warning("LIBRARY-COVERAGE 内部异常降级 fail-open: %s", exc)
            return True, ""

    return GateSpec(gate_id="LIBRARY-COVERAGE", check=_check, priority=145)
