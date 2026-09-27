# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.domain_fk_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py added 行含 [DOMAIN] D_XXX 头部时，D_XXX 必须在 functional_domain_registry.yaml 的 entries 中存在；tests/豁免；docstring 行豁免；git diff 不可达 fail-open；YAML 不可读 fail-open；检出违规则 fail-closed 阻断
# [MODIFY-GUARD] gate_id="GATE-DOMAIN-FK"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；真源=functional_domain_registry.yaml（staged 版本，SSoT TRAE-062）；diff-based 只检测 added 行
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff / YAML 读取异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_domain_fk_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
domain_fk_gate.py — [DOMAIN] 头部域注册表 FK 校验门禁（GATE-DOMAIN-FK）

裁定#ARCH-DRIFT-PREVENTION-001 (ADP-1)：从"检测驱动"转向"约束驱动"。

检测 staged .py 文件 added 行中的 ``[DOMAIN] D_XXX`` 头部声明，验证 D_XXX 在
functional_domain_registry.yaml（域注册表真源，SSoT TRAE-062）的 entries 中存在。

治本动机
--------
原架构依赖 generate_project_depgraph.py 的 FK 约束被动拦截无效域，但 INSERT
失败被静默吞没（只 WARN 前 10 个），导致 CODE_NOT_IN_DEPGRAPH drift 永久存在
（如 pure_assertion_gate.py 的 D_GOV_DOC_QUALITY、check_pure_assertion.py 的
D_GOV_DOC_QUALITY）。本 gate 在 commit 前置阶段主动校验，从源头阻断无效域
写入代码库。

真源选择（SSoT TRAE-062）
--------------------------
- 域注册表是"规则数据（注册表）"，真源是 functional_domain_registry.yaml
- domains 表是 DB 缓存（sync_yaml_to_depgraph.py 同步产物）
- gate 读取 YAML 真源（staged 版本），不依赖 DB 连接——更快且权威，
  且避免"YAML 已更新但 DB 未同步"的滞后误判

设计权衡
--------
1. **diff-based**：只检测 added 行；新文件全行 added 故 [DOMAIN] 必被检查；
   存量违规（modified 文件未改 [DOMAIN] 行）由 drift detection + Phase 4 处理。
2. **YAML 真源**：避免 DB 连接开销，避免 DB 滞后于 YAML 的误判。
3. **staged 版本**：若 YAML 与 .py 同提交交，读 staged YAML 确保新域被识别。
4. **priority=78**：在 BLUEPRINT-FORMAT(77) 之后、BLUEPRINT-AMODULE-CONSISTENCY(79)
   之前——先校验格式再校验语义。

Usage::

    from zephyr.gov_enforcement.commit_gates.domain_fk_gate import make_domain_fk_gate

    registry.register(make_domain_fk_gate())

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/d/domain_fk_gate.yaml
"""

from __future__ import annotations

import logging
import re

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

__all__ = ["make_domain_fk_gate"]

# 域注册表真源（SSoT TRAE-062：注册表属规则数据，真源=YAML）
_DOMAIN_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"

# 匹配 [DOMAIN] D_XXX 头部（frontmatter 注释行，列 0 起始）
_DOMAIN_HEADER_RE = re.compile(r"^#\s*\[DOMAIN\]\s*(\S+)")

# 匹配 YAML entries 段中的 "- domain: D_XXX" 条目
# 仅匹配 "- domain:" 行（entry_schema 中的 "  domain: str" 缩进不同不会误匹配）
_YAML_DOMAIN_ENTRY_RE = re.compile(r"^-\s*domain:\s*(\S+)", re.MULTILINE)

# ── 真域错挂归属判据（wave7.3 红蓝 2026-09-28，st-zc8-lane-rb2）──────────────────
# 病根：本门原本只拦"假域"（FK 存在性），同一真实域错挂到无关包的 module 无判据
# （st-c7-rb-20260927 V3b 在案发现）。本表为内嵌判据（不动注册名册）：
# src/zephyr/<pkg>/ 下 .py 的 [DOMAIN] 声明必须命中所属包的域族规则。
# 派生方式：机械扫描 src/zephyr 全库现有 (包, 域) 头分布（2026-09-28 快照），
# 每个现库 (包, 域) 对均放行——零误伤基线；匹配语义 = domain == rule 或
# domain.startswith(rule)（域族前缀，如 D_GOV 覆盖 D_GOV_*/D_GOVERNANCE）。
# 包不在表内（新增包/非 src 树）= 不判（fail-open，误伤代价高于漏拦）。
_PKG_DOMAIN_RULES: dict[str, tuple[str, ...]] = {
    "ai_layer": ("D_GOVERNANCE",),
    "alt_data": ("D_ALT_DATA",),
    "autonomy_core": ("D_AUTONOMY_CORE",),
    "backtest": ("D_BACKTEST", "D_DATA"),
    "clone_guard": ("D_GOV_CODE_QUALITY",),
    "compliance": ("D_COMPLIANCE", "D_GOVERNANCE"),
    "cross_asset": ("D_CROSS_ASSET",),
    "data": ("D_DATA", "D_MKT_DATA", "D_ALT_DATA", "D_INFRA_RUNTIME", "D_GOVERNANCE"),
    "data_eng": ("D_DATA_ENG",),
    "data_governance": ("D_DATA_GOV",),
    "data_security": ("D_DATA_SEC",),
    "digital_twin": ("D_DIGITAL_TWIN",),
    "execution_simulation": ("D_EXEC_SIM",),
    "experiment_tracking": ("D_INFRA_TELEMETRY",),
    "ex_core": ("D_EX_CORE", "D_EXECUTION_CORE"),
    "ex_sor": ("D_EX_SOR",),
    "factor": ("D_FACTOR",),
    "feedback_loop": ("D_FEEDBACK_LOOP", "D_FBL_DETECTORS", "D_FBL_DIAGNOSERS", "D_FBL_VERIFICATION"),
    "frontend": ("D_FRONTEND",),
    "governance": ("D_GOV", "D_OPS", "D_SECURITY", "D_BACKTEST", "D_EX_CORE", "D_AUTONOMY_CORE", "D_INFRA_RECOVERY"),
    "gov_audit": ("D_GOV_AUDIT", "D_GOV_DRIFT"),
    "gov_code_quality": ("D_GOV_CODE_QUALITY",),
    "gov_drift": ("D_GOV_DRIFT", "D_SECURITY"),
    "gov_enforcement": ("D_GOV",),
    "gov_rule": ("D_GOV_RULE",),
    "infrastructure": ("D_INFRA", "D_GOVERNANCE", "D_AUTONOMY_CORE", "D_OPS"),
    "infra_ops": ("D_INFRA_OPS",),
    "infra_runtime": ("D_INFRA_RUNTIME",),
    "integration": ("D_INTEGRATION", "D_GOVERNANCE", "D_AUTONOMY_CORE"),
    "intelligence": ("D_INTELLIGENCE", "D_GOVERNANCE", "D_AUTONOMY_CORE"),
    "knowledge": ("D_KNOWLEDGE",),
    "library": ("D_GOVERNANCE",),
    "market_data": ("D_MKT_DATA",),
    "ml_serve": ("D_ML_SERVE",),
    "ml_train": ("D_ML_TRAIN",),
    "nlp": ("D_DATA",),
    "orchestrator": ("D_ORCHESTRATOR",),
    "pf_alloc": ("D_PF_ALLOC", "D_BACKTEST"),
    "pf_core": ("D_PF_CORE",),
    "plan_engine": ("D_PLAN", "D_TRADING"),
    "position": ("D_POSITION",),
    "red_blue_validator": ("D_SECURITY",),
    "regime": ("D_REGIME",),
    "reporting": ("D_REPORTING",),
    "research": ("D_FACTOR", "D_KNOWLEDGE", "D_RESEARCH"),
    "risk": ("D_RISK",),
    "runtime": ("D_INFRA_RUNTIME",),
    "security": ("D_SECURITY", "D_AUTONOMY_CORE"),
    "sell_decision": ("D_SELL_DECISION",),
    "shared": (
        "D_SHARED",
        "D_AUTONOMY_CORE",
        "D_GOVERNANCE",
        "D_INTEGRATION",
        "D_INFRASTRUCTURE",
        "D_CONTRACTS",
        "D_INFRA_RUNTIME",
        "D_INFRA_OPS",
    ),
    "signal_ashare": ("D_ASHARE_SIGNAL", "D_SIGNAL_ASHARE", "D_SIGNAL"),
    "signal_fundamental": ("D_FUNDAMENTAL_SIGNAL",),
    "signal_quality": ("D_SIGQC",),
    "simulation": ("D_SIMULATION", "D_AUDITTEST"),
    "strategy_factory": ("D_ASHARE_SIGNAL",),
    "strategy_pipeline": ("D_BACKTEST",),
    "trading": ("D_TRADING", "D_INFRA_RUNTIME"),
}


def _package_of(py_file: str) -> str:
    """取 src/zephyr/<pkg>/ 的包名；非 src 树或包根散文件返回 ""（不判）。"""
    norm = py_file.replace("\\", "/")
    marker = "src/zephyr/"
    i = norm.find(marker)
    if i < 0:
        return ""
    rest = norm[i + len(marker):]
    if "/" not in rest:
        return ""
    return rest.split("/", 1)[0]


def _domain_family_allows(pkg: str, domain: str) -> bool | None:
    """归属判据：True=域族放行；False=真域错挂；None=包不在册（不判，fail-open）。"""
    rules = _PKG_DOMAIN_RULES.get(pkg)
    if rules is None:
        return None
    return any(domain == r or domain.startswith(r) for r in rules)


def _load_valid_domains(gateway) -> set[str] | None:
    """从 functional_domain_registry.yaml（staged 版本）加载有效域集合。

    真源选择（SSoT TRAE-062）：域注册表是规则数据，真源是 YAML 文件。
    domains 表是 DB 缓存（sync_yaml_to_depgraph.py 同步产物），gate 读取
    YAML 真源避免 DB 连接开销和"YAML 已更新但 DB 未同步"的滞后问题。

    读取 staged 版本（``git show :path``）：若 YAML 与使用新域的 .py 文件
    同提交交，staged YAML 已含新域条目，gate 不会误阻断。

    Args:
        gateway: GitCommitGateway 实例（提供 _run_git / project_root）。

    Returns:
        有效域 ID 集合（如 {"D_GOV_CODE_QUALITY", "D_INFRA_A2A", ...}）；
        YAML 不可读时返回 None（调用方 fail-open）。
    """
    content = _read_staged_file(gateway, _DOMAIN_REGISTRY_REL)
    if content is None:
        logger.warning("GATE-DOMAIN-FK fail-open: 无法读取 functional_domain_registry.yaml（staged 版本）")
        return None
    domains = set(_YAML_DOMAIN_ENTRY_RE.findall(content))
    if not domains:
        logger.warning("GATE-DOMAIN-FK fail-open: functional_domain_registry.yaml 未解析出任何域条目（格式异常？）")
        return None
    return domains


def _check_domain_fk(gateway, py_files: list[str], valid_domains: set[str]) -> list[str]:
    """校验 staged .py 文件 added 行的 [DOMAIN] 头部值在有效域集合中。

    diff-based 检测：只检查 added 行中的 [DOMAIN] 声明。新文件全行 added
    故 [DOMAIN] 必被检查；modified 文件仅当 [DOMAIN] 行被改动时才检查
    （存量违规由 drift detection 处理，不阻断无关修改）。
    """
    violations: list[str] = []
    for py_file in py_files:
        file_content = _read_staged_file(gateway, py_file)
        docstring_lines = _extract_docstring_lines(file_content) if file_content else set()
        for line_no, content in _get_added_lines(gateway, py_file, "GATE-DOMAIN-FK"):
            if line_no in docstring_lines:
                continue
            m = _DOMAIN_HEADER_RE.search(content)
            if not m:
                continue
            domain = m.group(1)
            if domain not in valid_domains:
                violations.append(f"  {py_file}:{line_no}: [DOMAIN] {domain} 不在 functional_domain_registry.yaml 中")
                continue
            # 真域错挂归属判据（wave7.3）：域真实存在但与所在包域族不符 → 同样阻断。
            pkg = _package_of(py_file)
            if not pkg:
                continue
            allowed = _domain_family_allows(pkg, domain)
            if allowed is False:
                violations.append(
                    f"  {py_file}:{line_no}: [DOMAIN] {domain} 真域错挂——包 zephyr.{pkg} "
                    f"的声明域族 {_PKG_DOMAIN_RULES.get(pkg, ())} 不含该域"
                    "（GATE-DOMAIN-FK 归属判据；改声明为所属域族，或将文件移入对应包）"
                )
    return violations


def _format_domain_fk_violations(violations: list[str]) -> tuple[bool, str]:
    """格式化域 FK / 真域错挂违规为阻断消息。"""
    return False, (
        "GATE-DOMAIN-FK：[DOMAIN] 头部声明未通过域校验（存在性 FK 或包归属判据）\n"
        "  真源：docs/01_policies_and_standards/_registry/catalogs/"
        "functional_domain_registry.yaml\n"
        "  修复方式（二选一）：\n"
        "    A. 将 [DOMAIN] 改为已注册的域（查看真源 YAML 的 entries 列表）\n"
        "    B. 在 functional_domain_registry.yaml 的 entries 中新增域条目\n"
        "       （需与使用该域的 .py 文件在同一 commit 提交）\n" + "\n".join(violations)
    )


def make_domain_fk_gate() -> GateSpec:
    """构造 [DOMAIN] 头部域 FK 校验 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="GATE-DOMAIN-FK", priority=78)。
        priority=78——在 BLUEPRINT-FORMAT(77) 之后、
        BLUEPRINT-AMODULE-CONSISTENCY(79) 之前。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = [f for f in _get_staged_py_files(gateway, "GATE-DOMAIN-FK") if not is_test_exempt(f)]
        if not py_files:
            return True, ""

        valid_domains = _load_valid_domains(gateway)
        if valid_domains is None:
            return True, ""  # fail-open：YAML 不可读时不阻断

        violations = _check_domain_fk(gateway, py_files, valid_domains)
        if violations:
            logger.error("GATE-DOMAIN-FK gate block: %d violation(s)", len(violations))
            return _format_domain_fk_violations(violations)
        return True, ""

    return GateSpec(gate_id="GATE-DOMAIN-FK", check=_check, priority=78)
