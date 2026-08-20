# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.secret_registry_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); yaml
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .env.example 或 config/secret_registry.yaml 变更时，校验两者 KEY 一致性；不一致阻断 commit（passed=False）；AST/git 异常 fail-open（logger.warning）
# [MODIFY-GUARD] gate_id="SECRET-REGISTRY-CONSISTENCY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_secret_registry_consistency_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""secret_registry_consistency_gate.py — .env.example 与 secret_registry.yaml 一致性门禁

裁定 #ARCH-SECRETS-GOV-001 S-3（Phase 2 硬化检测）

检测 staged .env.example 或 config/secret_registry.yaml 变更时，两者 KEY 是否一致：
  - .env.example 有但 registry 无 → 违规（新增密钥未注册到 registry）
  - registry env_file=.env 有但 .env.example 无 → 违规（新增密钥未文档化到 .env.example）

治本目标
--------
100% AI 开发场景下，AI 新增密钥时容易遗漏文档化（只加 .env 不更新 .env.example）
或遗漏注册（只加 .env.example 不更新 registry）。本 gate 强制三步流程
（加 KEY → 更新 .env.example → 更新 registry）的最后一步对齐。

设计权衡
--------
1. **只检测 staged 变更**：仅当 .env.example 或 secret_registry.yaml 在 staged 中时
   才触发检查，避免每次 commit 都解析两个文件。
2. **只比较 env_file=.env 的 KEY**：.env.example 是根目录 .env 的模板，只对应
   registry 中 env_file=.env 的条目；config/.env.{service} 的 KEY 不在 .env.example 中。
3. **fail-open on parse error**：YAML 解析失败不阻断（由其他 gate 管 YAML 语法）。
4. **priority=127**：在 MCP-VERSION-FIELD(126) 之后、200 段（CAPABILITY-OVERLAP）之前。
   80-126 段已满（NO-BARE-GETENV=81 / MSG-EXPOSURE=83 / ... / MCP-VERSION-FIELD=126），
   127 是 80 段之后首个空位。

Usage::

    from zephyr.gov_enforcement.commit_gates.secret_registry_consistency_gate import (
        make_secret_registry_consistency_gate,
    )
    registry.register(make_secret_registry_consistency_gate())
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Final

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__: Final = ["make_secret_registry_consistency_gate"]

_ENV_EXAMPLE = ".env.example"
_REGISTRY = "config/secret_registry.yaml"


def _extract_env_example_keys(content: str) -> set[str]:
    """从 .env.example 内容提取 KEY 名（非注释行，KEY= 格式）。"""
    keys: set[str] = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]*)=", line)
        if m:
            keys.add(m.group(1))
    return keys


def _extract_registry_dotenv_keys(content: str) -> set[str]:
    """从 secret_registry.yaml 内容提取 env_file=.env 的 KEY 名。"""
    keys: set[str] = set()
    current_key: str | None = None
    current_env_file: str | None = None
    for line in content.splitlines():
        m = re.match(r"^\s*-\s+key:\s+(\S+)", line)
        if m:
            if current_key and current_env_file == ".env":
                keys.add(current_key)
            current_key = m.group(1)
            current_env_file = None
        m2 = re.match(r"^\s*env_file:\s+(\S+)", line)
        if m2:
            current_env_file = m2.group(1)
    # 最后一个条目
    if current_key and current_env_file == ".env":
        keys.add(current_key)
    return keys


def make_secret_registry_consistency_gate() -> GateSpec:
    """构造 .env.example ↔ secret_registry.yaml 一致性门禁 GateSpec。

    Returns:
        GateSpec(gate_id="SECRET-REGISTRY-CONSISTENCY", priority=127)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 检测 staged 中是否包含目标文件
        try:
            diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only"])
            if diff_result.returncode != 0:
                logger.warning(
                    "SECRET-REGISTRY-CONSISTENCY gate fail-open: git diff 失败(rc=%d)",
                    diff_result.returncode,
                )
                return True, ""
            staged_files = set(diff_result.stdout.strip().splitlines())
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "SECRET-REGISTRY-CONSISTENCY gate fail-open: git diff 异常(%s: %s)",
                type(e).__name__,
                e,
                exc_info=True,
            )
            return True, ""

        # 只在 .env.example 或 secret_registry.yaml 变更时触发
        if _ENV_EXAMPLE not in staged_files and _REGISTRY not in staged_files:
            return True, ""

        # 2. 解析两个文件
        wt_root = _resolve_worktree_root(gateway)
        env_example_path = Path(wt_root) / _ENV_EXAMPLE
        registry_path = Path(wt_root) / _REGISTRY

        try:
            env_example_content = env_example_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.warning(
                "SECRET-REGISTRY-CONSISTENCY gate fail-open: 读取 %s 失败(%s: %s)",
                env_example_path,
                type(e).__name__,
                e,
            )
            return True, ""

        try:
            registry_content = registry_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.warning(
                "SECRET-REGISTRY-CONSISTENCY gate fail-open: 读取 %s 失败(%s: %s)",
                registry_path,
                type(e).__name__,
                e,
            )
            return True, ""

        # 3. 提取 KEY 并比较
        env_example_keys = _extract_env_example_keys(env_example_content)
        registry_keys = _extract_registry_dotenv_keys(registry_content)

        only_in_example = env_example_keys - registry_keys
        only_in_registry = registry_keys - env_example_keys

        violations: list[str] = []
        if only_in_example:
            violations.append(f".env.example 有但 secret_registry.yaml 未登记: {sorted(only_in_example)}")
        if only_in_registry:
            violations.append(f"secret_registry.yaml 有但 .env.example 未文档化: {sorted(only_in_registry)}")

        if violations:
            detail = "; ".join(violations)
            return False, (
                f"SECRET-REGISTRY-CONSISTENCY: {detail}. "
                f"新增密钥三步流程（裁定 S-1 §3）: 1)加 KEY 到 .env → "
                f"2)更新 .env.example → 3)更新 config/secret_registry.yaml"
            )
        return True, ""

    return GateSpec(gate_id="SECRET-REGISTRY-CONSISTENCY", check=_check, priority=127)


def _resolve_worktree_root(gateway) -> str:
    """解析 worktree 根目录，失败回退 project_root。"""
    try:
        result = gateway.run_git(["git", "rev-parse", "--show-toplevel"])
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    return str(gateway.project_root)
