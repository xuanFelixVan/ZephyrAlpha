# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.ssot_redefinition_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.governance.capability_lookup (REGISTRY_YAML)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件中重新定义已 SSoT 化的符号(class/赋值)则阻断;SSoT 符号清单从 capability_canonical_file_registry.yaml aliases 自动派生(非新真源);canonical 文件本身定义豁免;tests/ 豁免;import/注释行豁免;registry 缺失/解析失败 fail-closed(阻断,除非 registry 本身在 staged 中正在修复);git diff 不可达 fail-open(logger.warning 告警检测器失效)
# [MODIFY-GUARD] gate_id="SSOT-REDEFINITION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 缺失/解析失败降级为 fail-closed(阻断,除非 registry 在 staged 中);git diff 异常降级为 fail-open(不阻断,logger.warning 告警);check_all 兜底 fail-closed
# [TESTS] tests/governance/commit_gates/test_ssot_redefinition_gate.py
# [A_module] module_id=MOD-GOV-ssot_redefinition_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁

检测 staged .py 文件的新增行中是否重新定义了已 SSoT 化的符号（class 定义或变量赋值）。
命中则硬阻断 commit，提示扩展现有 canonical 文件而非重新定义。

病根（ARCH-033 审核发现 P2）:
- CREATE-GUARD 只管新建文件，不管文件内重新定义
- 新 AI 可能在 privacy.py 里重新写 ``class PIICategory = ...`` 而非 import
- SSoT 靠约定不靠强制 -> 漂移风险

治本:
- 从 capability_canonical_file_registry.yaml 的 aliases 自动派生 SSoT 符号清单（非新真源）
- canonical 文件本身的定义豁免（合法定义）
- tests/ 豁免（测试可能 mock/重定义）
- import/注释行豁免

SSoT 符号筛选规则:
- alias 匹配 Python 标识符 (``^[A-Za-z_][A-Za-z0-9_]*$``) 且含至少一个大写字母
- 排除纯小写的文件名 token（如 ``rule_patterns`` 是文件名不是符号）

Usage::

    from zephyr.governance.commit_gates.ssot_redefinition_gate import make_ssot_redefinition_gate
    registry.register(make_ssot_redefinition_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_ssot_redefinition_gate"]

# Python 标识符 + 含至少一个大写字母 = SSoT 符号候选
_SYMBOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_COMMENT_RE = re.compile(r"^\s*#")
_IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import|import\s)")
_DOCSTRING_RE = re.compile(r"""^\s*('''|\"\"\")""")


def _is_ssot_symbol(alias: str) -> bool:
    """alias 是否是 SSoT 符号候选（Python 标识符 + 含大写字母）。"""
    return bool(_SYMBOL_RE.match(alias)) and any(c.isupper() for c in alias)


def make_ssot_redefinition_gate() -> GateSpec:
    """构造 SSoT 符号重复定义硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="SSOT-REDEFINITION", priority=65)。
        priority=65——在 create_guard(60) 之后、dangling_reference(70) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged added/modified .py 文件
        try:
            diff_result = gateway._run_git(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
            )
            if diff_result.returncode != 0:
                logger.warning(
                    "SSOT-REDEFINITION gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                    diff_result.returncode,
                )
                return True, ""
            staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
        except Exception as e:
            logger.warning(
                "SSOT-REDEFINITION gate fail-open: git diff 异常(%s: %s)，检测器失效。",
                type(e).__name__, e, exc_info=True
            )
            return True, ""

        py_files = [f for f in staged if f.endswith(".py") and not is_test_exempt(f)]
        if not py_files:
            return True, ""

        # 2. 从 capability registry 读取 SSoT 符号 -> canonical 文件映射
        from zephyr.governance.capability_lookup import REGISTRY_YAML

        # registry 修复豁免：若 registry 文件本身在 staged 中（正在修复），
        # 放行本次提交让修复落地（否则坏 registry 会 fail-closed 锁死所有 commit）。
        try:
            registry_rel = REGISTRY_YAML.relative_to(gateway.project_root).as_posix()
        except Exception:
            registry_rel = ""
        registry_being_fixed = bool(registry_rel) and registry_rel in staged

        if not REGISTRY_YAML.exists():
            if registry_being_fixed:
                logger.info(
                    "SSOT-REDEFINITION gate: registry 缺失(%s)但正在 staged 修复，放行。",
                    REGISTRY_YAML,
                )
                return True, ""
            logger.error(
                "SSOT-REDEFINITION gate fail-closed: registry 缺失(%s)，阻断。",
                REGISTRY_YAML,
            )
            return (
                False,
                f"SSOT-REDEFINITION gate fail-closed: capability registry 缺失"
                f"({REGISTRY_YAML})。修复 registry（在提交中包含该文件）"
                f"或恢复 registry 后重试。",
            )
        try:
            import yaml
            data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
        except Exception as e:
            if registry_being_fixed:
                logger.info(
                    "SSOT-REDEFINITION gate: registry 解析失败(%s: %s)但正在 staged 修复，放行。",
                    type(e).__name__, e,
                )
                return True, ""
            logger.error(
                "SSOT-REDEFINITION gate fail-closed: registry 解析失败(%s: %s)，阻断。",
                type(e).__name__, e, exc_info=True,
            )
            return (
                False,
                f"SSOT-REDEFINITION gate fail-closed: capability registry 解析失败"
                f"({type(e).__name__}: {e})。修复 registry YAML 语法"
                f"（在提交中包含该文件）后重试。",
            )

        if not isinstance(data, dict):
            return True, ""

        # symbol -> canonical 文件路径（相对路径，/ 分隔）
        symbol_to_canonical: dict[str, str] = {}
        for cap in data.get("capabilities", []) or []:
            if not isinstance(cap, dict):
                continue
            canonical = cap.get("canonical_override", "")
            if not canonical:
                continue
            canonical_norm = canonical.replace("\\", "/")
            for alias in cap.get("aliases", []) or []:
                if isinstance(alias, str) and _is_ssot_symbol(alias):
                    symbol_to_canonical[alias] = canonical_norm

        if not symbol_to_canonical:
            return True, ""

        # 3. 编译检测正则（符号按长度降序，避免短符号误匹配）
        symbols_sorted = sorted(symbol_to_canonical.keys(), key=len, reverse=True)
        symbols_alt = "|".join(re.escape(s) for s in symbols_sorted)
        # 匹配 class 定义或变量赋值/类型注解，捕获符号名
        define_re = re.compile(
            rf"^class\s+({symbols_alt})\b|^({symbols_alt})\s*[:=]"
        )

        # 4. 检测每个 staged .py 文件的 added 行
        violations: list[str] = []
        for py_file in py_files:
            try:
                file_diff = gateway._run_git(
                    ["git", "diff", "--cached", "--unified=0", "--", py_file]
                )
            except Exception as e:
                logger.warning(
                    "SSOT-REDEFINITION gate: git diff 失败 file=%s, %s",
                    py_file, e, exc_info=True,
                )
                continue
            if file_diff.returncode != 0:
                continue
            for raw_line in file_diff.stdout.splitlines():
                if not raw_line.startswith("+") or raw_line.startswith("+++"):
                    continue
                content = raw_line[1:]
                if _COMMENT_RE.match(content) or _IMPORT_RE.match(content) or _DOCSTRING_RE.match(content):
                    continue
                m = define_re.match(content)
                if not m:
                    continue
                symbol = m.group(1) or m.group(2)
                canonical = symbol_to_canonical.get(symbol, "")
                if canonical == py_file:
                    continue  # 合法定义（canonical 文件本身）
                violations.append(
                    f"{py_file}: 重新定义 SSoT 符号 '{symbol}' "
                    f"(canonical: {canonical}) -> {content.strip()}"
                )

        if violations:
            detail = (
                "SSoT 符号重复定义（硬阻断）：\n"
                + "\n".join(violations)
                + "\n-> 扩展现有 canonical 文件，勿重新定义。"
                  "查 capability_canonical_file_registry.yaml 找 canonical 文件。"
            )
            return False, detail
        return True, ""

    return GateSpec(gate_id="SSOT-REDEFINITION", check=_check, priority=65)
