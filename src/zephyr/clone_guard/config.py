# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §6
# [MODULE] zephyr.clone_guard.config
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pathlib; yaml
# [CONSUMERS] zephyr.clone_guard.orchestrator; zephyr.clone_guard.engines.echo_guard_adapter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] clone_guard.yml 是 CloneGuard 统一配置 SSoT；配置缺失时使用安全默认值（extract 级阻断 + 30s 超时）
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置加载失败返回安全默认值（不抛异常）
# [TESTS] tests/clone_guard/test_config.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CloneGuard 配置加载器——从 clone_guard.yml 读取统一配置。

配置缺失或解析失败时使用安全默认值（extract 级阻断 + 30s 超时 + echo-guard 启用）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

__all__ = ["CloneGuardConfig", "load_config"]

_DEFAULT_CONFIG_PATH = "clone_guard.yml"


@dataclass(frozen=True)
class CloneGuardConfig:
    """CloneGuard 统一配置（从 clone_guard.yml 加载）。"""

    # Layer 1: pre-commit 拦截
    pre_commit_timeout_sec: int = 30
    fail_on_severity: str = "extract"  # extract=硬阻断, review=警告, none=不阻断
    echo_guard_enabled: bool = True

    # 降级策略
    fail_closed: bool = False  # echo-guard 全部超时/崩溃时是否阻断（False=warn-only 兜底）

    # 聚合策略（Phase B——多引擎结果合并）
    filter_minority: bool = False  # True=过滤仅单引擎报告的 findings，False=保留但标记 consensus="single"

    # 运行环境（L1 离线优先——HF_HUB_OFFLINE=1 强制 Tier 1 AST 哈希检测，跳过模型下载）
    env: dict[str, str] = field(default_factory=dict)

    # 忽略路径（除 echo-guard.yml 自身排除规则外）
    ignore_paths: tuple[str, ...] = (
        "tests/",
        "docs/",
        ".runtime/",
        ".echo-guard/",
        "**/_generated/",
    )

    @property
    def block_severities(self) -> set[str]:
        """返回应硬阻断的严重性集合。"""
        if self.fail_on_severity == "extract":
            return {"extract"}
        if self.fail_on_severity == "review":
            return {"extract", "review"}
        return set()


def load_config(repo_root: Path) -> CloneGuardConfig:
    """从 repo_root/clone_guard.yml 加载配置，失败时返回安全默认值。

    Args:
        repo_root: 仓库根目录路径。

    Returns:
        CloneGuardConfig 实例（加载失败时返回默认值）。
    """
    config_path = repo_root / _DEFAULT_CONFIG_PATH
    if not config_path.exists():
        logger.debug("clone_guard.yml 不存在(%s)，使用默认配置", config_path)
        return CloneGuardConfig()

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001  配置解析失败用默认值
        logger.warning("clone_guard.yml 解析失败(%s: %s)，使用默认配置", type(e).__name__, e)
        return CloneGuardConfig()

    if not isinstance(raw, dict):
        logger.warning("clone_guard.yml 顶层非 dict，使用默认配置")
        return CloneGuardConfig()

    # 安全提取字段——只认已知的 key，忽略未知 key
    pre_commit = raw.get("pre_commit", {}) or {}
    severity = raw.get("severity", {}) or {}
    aggregation = raw.get("aggregation", {}) or {}
    env_raw = raw.get("env", {}) or {}
    env = {str(k): str(v) for k, v in env_raw.items()} if isinstance(env_raw, dict) else {}

    return CloneGuardConfig(
        pre_commit_timeout_sec=int(pre_commit.get("timeout_sec", 30)),
        fail_on_severity=str(pre_commit.get("fail_on", severity.get("extract", "extract"))),
        echo_guard_enabled=bool(pre_commit.get("echo_guard_enabled", True)),
        fail_closed=bool(pre_commit.get("fail_closed", False)),
        filter_minority=bool(aggregation.get("filter_minority", False)),
        env=env,
        ignore_paths=tuple(raw.get("ignore_paths", ()) or CloneGuardConfig().ignore_paths),
    )
