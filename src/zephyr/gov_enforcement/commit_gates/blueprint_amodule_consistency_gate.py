# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_amodule_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); scripts.governance.d3_metadata.validate_module_id_naming (is_valid_module_id)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 [A_module] module_id 头部时，module_id 必须通过 is_valid_module_id() 校验（裁定#208 双轨制，与 BLUEPRINT-FORMAT gate 共用真源）；tests/豁免；docstring 行豁免；git diff 不可达 fail-open；检出违规则 fail-closed 阻断。治本（#ARCH-MODULE-ID-FORMAT-UNIFICATION-001，2026-07-22）：废除 malformation 正则，改用 is_valid_module_id() 统一校验，消除真源分裂
# [MODIFY-GUARD] gate_id="BLUEPRINT-AMODULE-CONSISTENCY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；diff-based 只检测 added 行
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_blueprint_amodule_consistency_gate.py
# [A_module] module_id=MOD-GOV-blueprint_amodule_consistency_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""blueprint_amodule_consistency_gate.py — [A_module] 头部 module_id 格式一致性门禁

裁定#ARCH-DRIFT-PREVENTION-001 (ADP-3)：从"检测驱动"转向"约束驱动"。
治本#ARCH-MODULE-ID-FORMAT-UNIFICATION-001（2026-07-22）：废除 malformation 正则，
改用 is_valid_module_id() 统一校验，消除与 validate_module_id_naming.py 的真源分裂。

检测 staged .py 文件 added 行中的 ``[A_module] module_id=XXX`` 头部，校验 XXX
通过 ``is_valid_module_id()`` 合规（裁定#208 双轨制）。

治本动机
--------
原设计使用靶向 malformation 正则 ``MOD-[A-Z]+_[a-z]`` 检测"层码后下划线+小写"，
但这与 ``validate_module_id_naming.py`` 的 is_valid_module_id() 真源分裂：
  - malformation 正则认为 ``MOD-GOV_domain_fk_gate`` 是违规（层码后下划线+小写）
  - is_valid_module_id() 认为 ``MOD-GOV_domain_fk_gate`` 是合法（大小写混合下划线段）
  - malformation 正则认为 ``MOD-GOV-domain_fk_gate`` 是合法（DASH 后小写）
  - is_valid_module_id() 认为 ``MOD-GOV-domain_fk_gate`` 是违规（DASH 后非数字）

此分裂导致并发 session 修复时方向相反（UNDERSCORE→DASH vs DASH→UNDERSCORE），
循环修复无法归零。治本：统一到 is_valid_module_id() 真源。

设计权衡
--------
1. **复用 is_valid_module_id()**：与 BLUEPRINT-FORMAT gate 共用真源，消除正则分裂。
   is_valid_module_id() 的 DOMAIN_DERIVED 正则 ``[A-Za-z]`` 允许大小写混合下划线段，
   不会误阻断 ``MOD-GOV_domain_fk_gate`` 等合法文件级 module_id。
2. **diff-based**：只检测 added 行；存量违规由批量修复脚本治理。
3. **priority=79**：在 GATE-DOMAIN-FK(78) 之后、VOCAB-HARDCODE(80) 之前。
4. **动态加载**：复用 BLUEPRINT-FORMAT gate 的 _load_is_valid_module_id 模式，
   确保 worktree 模式下使用 worktree 中的模块版本。

合法 vs 非法示例（is_valid_module_id() 真源）
----------------------------------------------
  合法: MOD-GOV_domain_fk_gate     (派生轨: MOD-{DOM}_{name}，下划线分隔)
  合法: MOD-GOV_SCRIPTS            (派生轨: MOD-{DOM}，全大写域段)
  合法: MOD-INF-025                (layer-master 轨: MOD-{LAYER}-{SEQ})
  合法: MOD-INFRA_A2A-005          (派生轨: MOD-{DOM}_{DOM}-{SEQ})
  合法: SH-DB-001                  (跨域共享轨: SH-{ABBR}-{NNN})
  非法: MOD-GOV-domain_fk_gate     (DASH 分隔多段，-domain_fk_gate 非数字)

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_amodule_consistency_gate import (
        make_blueprint_amodule_consistency_gate,
    )
    registry.register(make_blueprint_amodule_consistency_gate())
"""

from __future__ import annotations

import importlib.util
import logging
import re
from pathlib import Path

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

__all__ = ["make_blueprint_amodule_consistency_gate"]

# 匹配 [A_module] module_id=XXX 或 [A_module] module_id:XXX 头部
# 与 module_id_consistency_gate._RE_HEADER_MODULE_ID 一致（支持 = 和 : 分隔符）
_RE_AMODULE_HEADER = re.compile(
    r"^#\s*\[A_\w+\]\s*module_id[:=]\s*(\S+)"
)

# 治本（#ARCH-MODULE-ID-FORMAT-UNIFICATION-001，2026-07-22）：
# 废除 _MALFORMATION_RE，改用 is_valid_module_id() 统一校验
# 动态加载缓存（与 blueprint_format_gate.py 一致，确保 worktree 模式正确）
_validate_module_id_cache: dict[str, object] = {}


def _load_is_valid_module_id(project_root: Path):
    """从 project_root 动态加载 validate_module_id_naming.is_valid_module_id。

    与 blueprint_format_gate._load_is_valid_module_id 一致，确保 worktree 模式下
    使用 worktree 中的模块版本。
    """
    key = str(project_root)
    if key in _validate_module_id_cache:
        return _validate_module_id_cache[key]
    module_path = (
        project_root / "scripts" / "governance" / "d3_metadata"
        / "validate_module_id_naming.py"
    )
    if not module_path.exists():
        from zephyr.shared.io.paths import REPO_ROOT
        module_path = (
            REPO_ROOT / "scripts" / "governance" / "d3_metadata"
            / "validate_module_id_naming.py"
        )
    spec = importlib.util.spec_from_file_location(
        "_validate_module_id_naming_amodule", module_path,
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _validate_module_id_cache[key] = mod.is_valid_module_id
    return mod.is_valid_module_id


def _check_amodule_format(
    gateway, py_files: list[str]
) -> list[str]:
    """校验 staged .py 文件 added 行的 [A_module] module_id 格式。

    治本（#ARCH-MODULE-ID-FORMAT-UNIFICATION-001）：使用 is_valid_module_id()
    统一校验，与 BLUEPRINT-FORMAT gate 共用真源。

    diff-based 检测：只检查 added 行中的 [A_module] 声明。新文件全行 added
    故 [A_module] 必被检查；modified 文件仅当 [A_module] 行被改动时才检查。
    """
    is_valid_module_id = _load_is_valid_module_id(gateway.project_root)
    violations: list[str] = []
    for py_file in py_files:
        file_content = _read_staged_file(gateway, py_file)
        docstring_lines = (
            _extract_docstring_lines(file_content) if file_content else set()
        )
        for line_no, content in _get_added_lines(
            gateway, py_file, "BLUEPRINT-AMODULE-CONSISTENCY"
        ):
            if line_no in docstring_lines:
                continue
            m = _RE_AMODULE_HEADER.search(content)
            if not m:
                continue
            module_id = m.group(1)
            ok, reason = is_valid_module_id(module_id)
            if not ok:
                violations.append(
                    f"  {py_file}:{line_no}: [A_module] module_id="
                    f"'{module_id}' 格式错误——{reason}"
                )
    return violations


def _format_amodule_violations(violations: list[str]) -> tuple[bool, str]:
    """格式化 [A_module] 格式违规为阻断消息。"""
    return False, (
        "BLUEPRINT-AMODULE-CONSISTENCY：[A_module] module_id 格式不合规\n"
        "  裁定#ARCH-DRIFT-PREVENTION-001 (ADP-3) + #ARCH-MODULE-ID-FORMAT-UNIFICATION-001\n"
        "  合法格式（裁定#208 双轨制，is_valid_module_id() 真源）：\n"
        "    layer-master: MOD-{LAYER}-{SEQ}      如 MOD-INF-025\n"
        "    派生轨: MOD-{DOM}_{name}             如 MOD-GOV_domain_fk_gate\n"
        "    派生轨: MOD-{DOM}_{DOM}-{SEQ}        如 MOD-INFRA_A2A-005\n"
        "    跨域共享: SH-{ABBR}-{NNN}            如 SH-DB-001\n"
        "  非法：MOD-{DOM}-{name} (DASH 分隔多段)  如 MOD-GOV-domain_fk_gate\n"
        + "\n".join(violations)
        + "\n-> 修复 [A_module] module_id，DASH 分隔多段改为下划线分隔"
    )


def make_blueprint_amodule_consistency_gate() -> GateSpec:
    """构造 [A_module] 格式一致性门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="BLUEPRINT-AMODULE-CONSISTENCY", priority=79)。
        priority=79——在 GATE-DOMAIN-FK(78) 之后、VOCAB-HARDCODE(80) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [
            f for f in _get_staged_py_files(gateway, "BLUEPRINT-AMODULE-CONSISTENCY")
            if not is_test_exempt(f)
        ]
        if not py_files:
            return True, ""

        violations = _check_amodule_format(gateway, py_files)
        if violations:
            logger.error(
                "BLUEPRINT-AMODULE-CONSISTENCY gate block: %d violation(s)",
                len(violations),
            )
            return _format_amodule_violations(violations)
        return True, ""

    return GateSpec(
        gate_id="BLUEPRINT-AMODULE-CONSISTENCY",
        check=_check,
        priority=79,
    )
