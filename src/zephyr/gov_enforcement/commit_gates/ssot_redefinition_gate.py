# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.ssot_redefinition_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.governance.capability_lookup (REGISTRY_YAML)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件中重新定义已 SSoT 化的符号(class/赋值)则阻断;SSoT 符号清单从 capability_canonical_file_registry.yaml aliases 自动派生(非新真源);canonical 文件本身定义豁免;tests/ 豁免;import/注释行豁免;registry 缺失/解析失败 fail-closed(阻断,除非 registry 本身在 staged 中正在修复);git diff 不可达 fail-open(logger.warning 告警检测器失效);own 化 2026-09-23(st-gslim P2):扫描范围=全暂存∩本 session,外来 staged warn+审计不阻断(_split_own_foreign);阻断消息处方直给（A3 任务4 st-circ-a3r-20260930）=逐符号附 `from <canonical_module> import <符号>` 可执行处方+同符号复读≥2 处消息头升级点名（结构性分裂必须收敛）
# [MODIFY-GUARD] gate_id="SSOT-REDEFINITION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry 缺失/解析失败降级为 fail-closed(阻断,除非 registry 在 staged 中);git diff 异常降级为 fail-open(不阻断,logger.warning 告警);check_all 兜底 fail-closed
# [TESTS] tests/governance/commit_gates/test_ssot_redefinition_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁

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
- 阻断消息处方直给（A3 任务4，st-circ-a3r-20260930）：逐符号附 ``from <canonical_module>
  import <符号>`` 可执行处方（dotted module 由 canonical 路径机械派生），同符号复读
  ≥2 处消息头升级点名——结构性分裂必须收敛到唯一 canonical

SSoT 符号筛选规则:
- alias 匹配 Python 标识符 (``^[A-Za-z_][A-Za-z0-9_]*$``) 且含至少一个大写字母
- 排除纯小写的文件名 token（如 ``rule_patterns`` 是文件名不是符号）

Usage::

    from zephyr.gov_enforcement.commit_gates.ssot_redefinition_gate import make_ssot_redefinition_gate
    registry.register(make_ssot_redefinition_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/s/ssot_redefinition_gate.yaml
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._capability_registry_io import parse_capability_registry_cached
from zephyr.gov_enforcement.commit_gates._diff_helpers import _split_own_foreign
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

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


# === 裁定#217 Tier2 P1 Extract Method 重构（2026-07-15）===
# 原 _check 140 行 McCabe=36（pipeline 串联：取staged→加载registry→建symbol_map→
# 编译regex→扫描文件→返回）。治本：提取为 6 个模块级 helper（均 McCabe≤15），
# _check 简化为 ~25 行 pipeline（McCabe≈6）。行为等价契约：每 helper 显式传参，
# early exit 用 (data, early_exit) 元组传递。


def _get_staged_files(gateway) -> list[str] | None:
    """获取 staged added/modified 文件列表。None=fail-open(git diff 不可达)。"""
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "SSOT-REDEFINITION gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        return [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "SSOT-REDEFINITION gate fail-open: git diff 异常(%s: %s)，检测器失效。", type(e).__name__, e, exc_info=True
        )
        return None


def _load_registry_yaml(gateway, staged: list[str]) -> tuple[dict | None, tuple[bool, str] | None]:
    """加载 capability registry YAML。返回 (data, early_exit)。

    data=dict 成功; early_exit=(True,"") 放行; early_exit=(False,msg) 阻断。
    registry 缺失/解析失败 fail-closed（除非 registry 在 staged 中正在修复）。
    """
    from zephyr.governance.capability_lookup import REGISTRY_YAML

    try:
        registry_rel = REGISTRY_YAML.relative_to(gateway.project_root).as_posix()
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        registry_rel = ""
    registry_being_fixed = bool(registry_rel) and registry_rel in staged

    if not REGISTRY_YAML.exists():
        if registry_being_fixed:
            logger.info(
                "SSOT-REDEFINITION gate: registry 缺失(%s)但正在 staged 修复，放行。",
                REGISTRY_YAML,
            )
            return None, (True, "")
        logger.error(
            "SSOT-REDEFINITION gate fail-closed: registry 缺失(%s)，阻断。",
            REGISTRY_YAML,
        )
        return None, (
            False,
            f"SSOT-REDEFINITION gate fail-closed: capability registry 缺失"
            f"({REGISTRY_YAML})。修复 registry（由持有该文件的会话提交修复后自动恢复）"
            f"或恢复 registry 后重试。",
        )
    # T8 簇1 共册解析（st-commitspeed-pkg8-20260925）：与 CREATE-GUARD/CAPABILITY-OVERLAP
    # 共享一次 yaml.safe_load（同真源可派生→必并）；判据零变化——本台 fail-open/
    # fail-closed 分支、消息文案逐字节保留，仅读入+解析走共享缓存（永不抛，错经 exc 返回）。
    data, parse_err = parse_capability_registry_cached(REGISTRY_YAML)
    if parse_err is not None:
        if registry_being_fixed:
            logger.info(
                "SSOT-REDEFINITION gate: registry 解析失败(%s: %s)但正在 staged 修复，放行。",
                type(parse_err).__name__,
                parse_err,
            )
            return None, (True, "")
        logger.error(
            "SSOT-REDEFINITION gate fail-closed: registry 解析失败(%s: %s)，阻断。",
            type(parse_err).__name__,
            parse_err,
            exc_info=True,
        )
        return None, (
            False,
            f"SSOT-REDEFINITION gate fail-closed: capability registry 解析失败"
            f"({type(parse_err).__name__}: {parse_err})。修复 registry YAML 语法"
            f"（由持有该文件的会话提交修复后自动恢复）后重试。",
        )

    if not isinstance(data, dict):
        return None, (True, "")
    return data, None


def _build_symbol_map(data: dict) -> dict[str, str]:
    """从 registry data 构建 symbol -> canonical 文件路径映射。"""
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
    return symbol_to_canonical


def _compile_define_re(symbols) -> re.Pattern:
    """编译符号定义检测正则（符号按长度降序，避免短符号误匹配）。"""
    symbols_sorted = sorted(symbols, key=len, reverse=True)
    symbols_alt = "|".join(re.escape(s) for s in symbols_sorted)
    return re.compile(rf"^class\s+({symbols_alt})\b|^({symbols_alt})\s*[:=]")


def _canonical_to_module(canonical: str) -> str:
    """canonical 文件路径 → dotted module（处方 import 语句用）。

    ``src/zephyr/governance/rule_patterns.py`` → ``zephyr.governance.rule_patterns``；
    非 src/ 前缀或无法解析时原样返回（处方退化为路径提示，不阻断格式）。
    """
    p = canonical.replace("\\", "/")
    if p.startswith("src/"):
        p = p[len("src/") :]
    if p.endswith(".py"):
        p = p[:-3]
    if not p or p.startswith("/"):
        return canonical
    return p.replace("/", ".")


def _scan_file_violations(
    gateway, py_file: str, symbol_to_canonical: dict[str, str], define_re: re.Pattern
) -> list[tuple[str, str, str, str]]:
    """扫描单个 staged .py 文件的 added 行，返回违规结构列表 (py_file, symbol, canonical, content)。"""
    try:
        file_diff = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", py_file])
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "SSOT-REDEFINITION gate: git diff 失败 file=%s, %s",
            py_file,
            e,
            exc_info=True,
        )
        return []
    if file_diff.returncode != 0:
        return []
    violations: list[str] = []
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
        violations.append((py_file, symbol, canonical, content.strip()))
    return violations


def _format_violations(violations: list[tuple[str, str, str, str]]) -> str:
    """格式化违规详情为阻断消息（A3 任务4 st-circ-a3r-20260930 治本）。

    处方直给：每符号附 `从 canonical import` 的可执行 import 语句——溯源者不再需要
    二跳查册。同符号复读 ≥2 处升级：消息头点名复读符号（结构性分裂必须收敛）。
    """
    symbol_counts: dict[str, int] = {}
    for _f, symbol, _c, _content in violations:
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    lines = []
    for py_file, symbol, canonical, content in violations:
        repeat_tag = f"【复读×{symbol_counts[symbol]}】" if symbol_counts[symbol] >= 2 else ""
        lines.append(f"{py_file}: 重新定义 SSoT 符号 '{symbol}'{repeat_tag} (canonical: {canonical}) -> {content}")
    repeated = sorted((s, n) for s, n in symbol_counts.items() if n >= 2)
    header = "SSoT 符号重复定义（硬阻断）：\n"
    if repeated:
        header = (
            "SSoT 符号重复定义（硬阻断·升级：同符号复读 "
            + ", ".join(f"'{s}'×{n}" for s, n in repeated)
            + "——同一符号散落多处属结构性分裂，必须收敛到唯一 canonical 定义）\n"
        )
    imports = []
    seen: set[tuple[str, str]] = set()
    for _f, symbol, canonical, _content in violations:
        key = (symbol, canonical)
        if key in seen or not canonical:
            continue
        seen.add(key)
        imports.append(f"   from {_canonical_to_module(canonical)} import {symbol}")
    tail = "-> 处方：删除本重复定义，直接从 canonical 导入（勿重新定义，扩展现有文件）：\n" + "\n".join(imports)
    return header + "\n".join(lines) + "\n" + tail + "。查 capability_canonical_file_registry.yaml 找 canonical。"


def make_ssot_redefinition_gate() -> GateSpec:
    """构造 SSoT 符号重复定义硬阻断 GateSpec。

    Returns:
        GateSpec(gate_id="SSOT-REDEFINITION", priority=65)。
        priority=65——在 create_guard(60) 之后、dangling_reference(70) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged = _get_staged_files(gateway)
        if staged is None:
            return True, ""
        # own 化（st-gslim-20260923 P2，#ARCH-GATE-OWN-SCOPE-001 推广）：扫描范围=
        # 全暂存区∩本 session 范围；外来 staged 不扫描不阻断（warn+审计在共享原语内）。
        own_staged = _split_own_foreign(
            gateway, staged, files, kwargs.get("session_id"), gate_name="SSOT-REDEFINITION"
        )[0]
        py_files = [f for f in own_staged if f.endswith(".py") and not is_test_exempt(f)]
        if not py_files:
            return True, ""

        data, early_exit = _load_registry_yaml(gateway, own_staged)
        if early_exit is not None:
            return early_exit
        symbol_to_canonical = _build_symbol_map(data)
        if not symbol_to_canonical:
            return True, ""

        define_re = _compile_define_re(symbol_to_canonical.keys())
        violations: list[str] = []
        for py_file in py_files:
            violations.extend(_scan_file_violations(gateway, py_file, symbol_to_canonical, define_re))

        if violations:
            return False, _format_violations(violations)
        return True, ""

    return GateSpec(gate_id="SSOT-REDEFINITION", check=_check, priority=65)
