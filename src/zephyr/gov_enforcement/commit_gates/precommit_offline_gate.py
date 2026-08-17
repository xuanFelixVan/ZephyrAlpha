# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-PRECOMMIT-OFFLINE-001
# [MODULE] zephyr.gov_enforcement.commit_gates.precommit_offline_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测 staged .pre-commit-config.yaml 中外部 repo 引用（http(s):// / git@ / 任何非 "local" 的 repo 字段）；命中硬阻断；fail-open：文件未在 staged / YAML 解析失败 / 非 Zephyr 项目时放行；rule 真源 trae_073；priority=111（110 被 CONSUMERS-ACCURACY 占用）
# [MODIFY-GUARD] gate_id="GATE-PRECOMMIT-OFFLINE"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 解析失败/git 异常降级为 fail-open（passed=True + warning detail）
# [TESTS] tests/governance/commit_gates/test_precommit_offline_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""precommit_offline_gate.py — pre-commit 配置离线可运行检测门禁（GATE-PRECOMMIT-OFFLINE）

对应铁律 trae_073（pre-commit hook 离线可运行纪律）。
裁定 #ARCH-PRECOMMIT-OFFLINE-001 治本——防止 .pre-commit-config.yaml 引入
外部 GitHub repo 依赖导致 pre-commit 工具在缓存失效/首次安装时尝试 git fetch
远程 repo，代理失败/离线环境卡死所有 commit。

病根（第一性原理）
-----------------
1. GitCommitGateway 永远 --no-verify，pre-commit hook 在合法路径不触发
2. pre-commit hook 是冗余第二防线，仅兜底裸 git commit
3. 但 .pre-commit-config.yaml 引用外部 GitHub repo（pre-commit/pre-commit-hooks）
   导致 pre-commit 工具在缓存失效时尝试 git fetch origin --tags——代理未启动或
   离线环境会卡死所有 commit
4. 网络依赖让"冗余防线"变成"单点故障"

治本方案
--------
本 gate 在 GitCommitGateway pre-commit 阶段检测 staged .pre-commit-config.yaml
中是否有外部 repo 引用（http(s):// / git@ / 任何非 "local" 的 repo 字段）。
命中则硬阻断 commit（PRECOMMIT_OFFLINE_VIOLATION）。

设计决策
--------
1. **只检测 staged .pre-commit-config.yaml**：通过 files 参数判断，未在 staged
   中则跳过（fail-open，避免无谓扫描）
2. **fail-open**：YAML 解析失败/git 异常时不阻断——环境异常降级为 warning
3. **priority=111**：紧接 CAPABILITY-LOOKUP-REQUIRED=110 之后，
   作为 config 完整性类检查（109 被 CONSUMERS-ACCURACY 占用）
4. **YAML 结构校验**：解析 repos[].repo 字段，任何非 "local" 值 → 阻断
5. **同时检测 language: python**：违反 trae_073 INV-002（language: system 强制）

Usage::

    from zephyr.gov_enforcement.commit_gates.precommit_offline_gate import make_precommit_offline_gate

    registry.register(make_precommit_offline_gate())
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_precommit_offline_gate", "scan_precommit_config_offline"]

# .pre-commit-config.yaml 相对路径
_PRECOMMIT_CONFIG_REL = ".pre-commit-config.yaml"

# 允许的 repo 值（trae_073 INV-001：所有 hook MUST 使用 repo: local）
_ALLOWED_REPO_VALUES: frozenset[str] = frozenset({"local"})

# 外部 repo URL 前缀（任何匹配即阻断）
_EXTERNAL_REPO_PREFIXES: tuple[str, ...] = (
    "https://",
    "http://",
    "git@",
    "ssh://",
    "ftp://",
)


def _is_external_repo(repo_value: str) -> bool:
    """判断 repo 值是否为外部 URL（非 local）。

    Args:
        repo_value: .pre-commit-config.yaml 中 repos[].repo 字段值。

    Returns:
        True=外部 URL（违规），False=local（合法）。
    """
    if not isinstance(repo_value, str):
        return False  # YAML 结构异常由调用方处理
    normalized = repo_value.strip().lower()
    if normalized in _ALLOWED_REPO_VALUES:
        return False
    # 任何非 local 值都视为外部（包括 URL / 本地路径 / 其他）
    # 严格策略：只允许 "local"，其他一律阻断
    return True


def _check_language_system(hooks: list) -> list[str]:
    """检测 hooks 中是否有 language 非 system 的（违反 trae_073 INV-002）。

    Args:
        hooks: repos[].hooks 列表（YAML 解析后的 dict 列表）。

    Returns:
        违规 hook id 列表（language != system 的 hook id）。
    """
    violations: list[str] = []
    if not isinstance(hooks, list):
        return violations
    for hook in hooks:
        if not isinstance(hook, dict):
            continue
        hook_id = hook.get("id", "<unknown>")
        language = hook.get("language", "system")
        if language != "system":
            violations.append(f"{hook_id} (language={language})")
    return violations


def scan_precommit_config_offline(config_text: str) -> tuple[bool, list[str], list[str]]:
    """扫描 .pre-commit-config.yaml 内容，检测外部 repo 引用 + language 违规。

    Args:
        config_text: .pre-commit-config.yaml 文件文本内容。

    Returns:
        (is_clean, external_repo_violations, language_violations) 三元组：
        - is_clean: True=无违规，False=有违规
        - external_repo_violations: 外部 repo URL 列表（如 ["https://github.com/..."]）
        - language_violations: language 非 system 的 hook id 列表
    """
    try:
        import yaml
        config = yaml.safe_load(config_text)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        # fail-open：YAML 解析失败不阻断（其他 gate 如 GATE-ENCODING 会兜底）
        logger.warning("GATE-PRECOMMIT-OFFLINE: YAML 解析失败 (fail-open): %s", e)
        return True, [], []

    if not isinstance(config, dict):
        return True, [], []

    repos = config.get("repos", [])
    if not isinstance(repos, list):
        return True, [], []

    external_violations: list[str] = []
    language_violations: list[str] = []

    for repo_entry in repos:
        if not isinstance(repo_entry, dict):
            continue
        repo_value = repo_entry.get("repo", "")
        if _is_external_repo(repo_value):
            external_violations.append(str(repo_value))
        # 检测 language: system 强制（仅对 local repo 的 hooks 检测）
        if repo_value == "local":
            hooks = repo_entry.get("hooks", [])
            lang_violations = _check_language_system(hooks)
            language_violations.extend(lang_violations)

    is_clean = not external_violations and not language_violations
    return is_clean, external_violations, language_violations


def _format_violations_detail(
    external_violations: list[str],
    language_violations: list[str],
) -> str:
    """格式化违规详情为可读字符串。"""
    lines: list[str] = []
    if external_violations:
        lines.append("外部 repo 引用违规（PRECOMMIT_OFFLINE_VIOLATION / RULE-PRECOMMIT-OFFLINE-INV-001）：")
        for repo in external_violations:
            lines.append(f"  - repo: {repo}")
        lines.append("  治本：删除外部 repo 引用，改为 repo: local + 纯 stdlib 实现的 local hook。")
        lines.append("  真源：docs/01_policies_and_standards/rules/trae_073_precommit_offline_discipline.yaml")
    if language_violations:
        lines.append("language 非 system 违规（PRECOMMIT_OFFLINE_VIOLATION / RULE-PRECOMMIT-OFFLINE-INV-002）：")
        for v in language_violations:
            lines.append(f"  - hook: {v}")
        lines.append("  治本：将 language: python 改为 language: system，避免虚拟环境创建 + 联网安装依赖。")
    return "\n".join(lines)


def make_precommit_offline_gate() -> GateSpec:
    """构造 GATE-PRECOMMIT-OFFLINE pre-commit 门禁（priority=109，硬阻断）。

    检测 staged .pre-commit-config.yaml 中是否有外部 repo 引用
    （http(s):// / git@ / 任何非 "local" 的 repo 字段）或 language 非 system。

    fail-open：.pre-commit-config.yaml 未在 staged / YAML 解析失败 / 非 Zephyr 项目时放行。

    裁定 #ARCH-PRECOMMIT-OFFLINE-001 治本（2026-07-21）：
    防止 pre-commit hook 网络单点故障复发。
    """

    def _check(gateway, files: list[str], **_kwargs) -> tuple[bool, str]:
        # 非 Zephyr 项目 skip（对标 ARCH-REFERENCE gate）
        _governance_dir = gateway.project_root / "scripts" / "governance" / "d1_structure"
        if not _governance_dir.is_dir():
            return True, "non-Zephyr project (no scripts/governance/d1_structure), skipping GATE-PRECOMMIT-OFFLINE"

        # 判断 .pre-commit-config.yaml 是否在 staged files 中
        project_root = gateway.project_root
        config_rel_normalized = _PRECOMMIT_CONFIG_REL.replace("\\", "/")
        config_in_commit = False
        for f in files:
            try:
                rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            except ValueError:
                continue
            if rel == config_rel_normalized:
                config_in_commit = True
                break

        if not config_in_commit:
            return True, ""  # .pre-commit-config.yaml 未在本次 commit，跳过

        # 读取工作区版本（commit 后的新真源）
        config_path = project_root / _PRECOMMIT_CONFIG_REL
        if not config_path.is_file():
            return True, ""  # 文件不存在（异常但 fail-open）

        try:
            config_text = config_path.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("GATE-PRECOMMIT-OFFLINE: 读取失败 (fail-open): %s", e)
            return True, ""  # fail-open

        is_clean, external_violations, language_violations = scan_precommit_config_offline(config_text)
        if is_clean:
            return True, ""

        detail = _format_violations_detail(external_violations, language_violations)
        logger.error("GATE-PRECOMMIT-OFFLINE block:\n%s", detail)
        return False, detail

    return GateSpec(gate_id="GATE-PRECOMMIT-OFFLINE", check=_check, priority=111)
