# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.blueprint_format_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d3_metadata.validate_module_id_naming (is_valid_module_id)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 [BLUEPRINT] 头部时，module_id 必须合规（裁定#208 双轨制：MOD-/SH- 前缀）；存量基线违规 grandfathered（只检 added 行）；git diff不可达fail-open；检出违规则fail-closed。治本（#ARCH-DATAQUALITY-V1.1）：移除 tests/ 豁免——100% AI 开发下豁免区=债务温床，482 个 SRC-XXX 违规因 tests/ 豁免累积
# [MODIFY-GUARD] gate_id="BLUEPRINT-FORMAT"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_blueprint_format_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""blueprint_format_gate.py — [BLUEPRINT] 头部 module_id 格式阻断门禁（BLUEPRINT-FORMAT，裁定#214 Phase 0 防蔓延）

检测 staged .py 文件 added 行中的 [BLUEPRINT] 头部，校验 module_id 格式
是否符合裁定#208 双轨制（MOD-/SH- 前缀）。

病根（第一性原理）
-----------------
裁定#214 调研发现 139 条 SRC-XXX 旧格式 + 10 条 (migrated) + 6 条空头 +
2 条其他格式错误的 [BLUEPRINT] 头部。Phase 1 已修复 18 个文件，但若无门禁，
新 AI 会继续制造同类违规——格式蔓延的根因是"无 commit 阶段强制"。

治本方案
--------
在 GitCommitGateway pre-commit 阶段注册门禁：
  1. 获取 staged added/modified .py 文件
  2. 对每个文件解析 diff，检查 added 行是否含 [BLUEPRINT] 头部
  3. 提取 module_id，调用 validate_module_id_naming.is_valid_module_id() 校验
  4. 不合规 -> 硬阻断

设计权衡
--------
1. **只检测 added 行**：存量 139 条 SRC-XXX 违规由专项任务清理，gate 只防新增。
2. **diff-based**：与 bare_sql_gate / hardcoded_url_gate 一致的检测模式。
3. **复用真源**：is_valid_module_id() 是格式校验唯一真源（裁定#208），禁止复制正则。
4. **priority=77**：在 RULE-FOUR-WAY(76) 之后，VOCAB-HARDCODE(80) 之前。
5. **移除 tests/ 豁免**（#ARCH-DATAQUALITY-V1.1，2026-07-18）：原设计豁免 tests/，
   导致 482 个 SRC-XXX 违规在 tests/ 下无限累积（AI 复制现有模式）。100% AI 开发
   下任何豁免区=债务温床。存量 grandfathered（只检 added 行），新增必须合规。

Usage::

    from zephyr.gov_enforcement.commit_gates.blueprint_format_gate import make_blueprint_format_gate
    registry.register(make_blueprint_format_gate())
"""

from __future__ import annotations

import importlib.util
import logging
import re
from pathlib import Path

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_blueprint_format_gate"]

# 治本（#ARCH-WORKTREE-002 缺陷1，2026-07-19）：动态加载 validate_module_id_naming
# 原设计：模块级 import 通过 REPO_ROOT 定位 scripts/governance/d3_metadata/
# 问题：REPO_ROOT 基于 __file__ 永远指向主工作区（src/zephyr/shared/io/paths.py:65），
#       worktree 模式下 pre-merge gate import 主工作区旧版本而非 worktree 新版本
#       （实测：regex 修复 [A-Z]→[A-Za-z] 后仍被旧版本拒绝 MOD-migrate_sqlite_to_pg）
# 方案：用 importlib.util.spec_from_file_location 从 gateway.project_root 动态加载，
#       确保 worktree 模式下使用 worktree 中的模块版本。缓存按 project_root key，
#       避免 repeated exec_module（实际 project_root 只有主工作区/worktree 两个值）
_validate_module_id_cache: dict[str, object] = {}


def _load_is_valid_module_id(project_root: Path):
    """从 project_root 动态加载 validate_module_id_naming.is_valid_module_id。

    治本（#ARCH-WORKTREE-002 缺陷1）：用 gateway.project_root 而非 REPO_ROOT，
    确保 worktree 模式下 import worktree 中的模块版本。

    Args:
        project_root: gateway.project_root（worktree 模式下为 worktree 路径）

    Returns:
        validate_module_id_naming.is_valid_module_id 函数引用

    Raises:
        FileNotFoundError: 模块文件不存在（project_root 异常时回退到 REPO_ROOT）
    """
    key = str(project_root)
    if key in _validate_module_id_cache:
        return _validate_module_id_cache[key]
    module_path = (
        project_root / "scripts" / "governance" / "d3_metadata"
        / "validate_module_id_naming.py"
    )
    if not module_path.exists():
        # 回退到 REPO_ROOT（非 worktree 模式或路径异常）
        from zephyr.shared.io.paths import REPO_ROOT
        module_path = (
            REPO_ROOT / "scripts" / "governance" / "d3_metadata"
            / "validate_module_id_naming.py"
        )
    spec = importlib.util.spec_from_file_location(
        "_validate_module_id_naming_dynamic", module_path,
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _validate_module_id_cache[key] = mod.is_valid_module_id
    return mod.is_valid_module_id

# 匹配 [BLUEPRINT] 头部行，提取 module_id token（第一个非空白 token）
# 合规：# [BLUEPRINT] MOD-INF-029 | docs/...
# 违规：# [BLUEPRINT]（空）/ # [BLUEPRINT] (migrated...) / # [BLUEPRINT] SRC-XXX | ...
_BP_HEADER_RE = re.compile(r"^#\s*\[BLUEPRINT\]\s*(\S+)?")


def make_blueprint_format_gate() -> GateSpec:
    """构造 [BLUEPRINT] 头部格式门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="BLUEPRINT-FORMAT", priority=77)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 治本（#ARCH-DATAQUALITY-V1.1，2026-07-18）：移除 tests/ 豁免——100% AI 开发下，
        # 豁免区=债务温床（482 个 SRC-XXX 违规因 tests/ 豁免累积）。存量 grandfathered
        # （只检 added 行），但新增 tests/ 文件必须用合规 MOD-/SH- 前缀。
        # 治本（#ARCH-WORKTREE-002 缺陷1，2026-07-19）：从 gateway.project_root 动态加载
        # is_valid_module_id，确保 worktree 模式下使用 worktree 中的模块版本
        is_valid_module_id = _load_is_valid_module_id(gateway.project_root)
        py_files = _get_staged_py_files(gateway, "BLUEPRINT-FORMAT")
        violations: list[str] = []
        for py_file in py_files:
            for line_no, content in _get_added_lines(gateway, py_file, "BLUEPRINT-FORMAT"):
                m = _BP_HEADER_RE.match(content)
                if not m:
                    continue
                # [BLUEPRINT] 头部行被 added/modified——校验 module_id
                module_id = m.group(1)
                if not module_id:
                    violations.append(
                        f"  {py_file}:{line_no}: [BLUEPRINT] header missing module_id "
                        f"(expected: # [BLUEPRINT] MOD-XXX | docs/...)"
                    )
                    continue
                ok, reason = is_valid_module_id(module_id)
                if not ok:
                    violations.append(
                        f"  {py_file}:{line_no}: [BLUEPRINT] header invalid module_id "
                        f"'{module_id}': {reason}"
                    )
        if violations:
            detail = (
                "BLUEPRINT-FORMAT: [BLUEPRINT] 头部 module_id 格式不合规"
                "（裁定#214 Phase 0 防蔓延）\n"
                "  合规格式: # [BLUEPRINT] MOD-XXX | docs/03_modules/.../blueprint.md\n"
                "  禁止格式: 空头部 / (migrated...) / SRC-XXX / DOM-XXX / 路径作 module_id\n"
                + "\n".join(violations)
                + "\n-> 修复 [BLUEPRINT] 头部，使用合规的 MOD-/SH- 前缀 module_id"
            )
            logger.error("BLUEPRINT-FORMAT gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="BLUEPRINT-FORMAT", check=_check, priority=77)
