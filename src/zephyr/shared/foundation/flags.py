# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.flags
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Self

"""
flags.py —— Feature Flag / 功能开关系统（Phase 2 新增 | 盲点 B7 修复）

痛点修复：100% AI 施工 + 1人+AI 维护下，没有开关控制 AI 的行为——
  1. AI 改了不该改的功能——无法紧急关闭
  2. 新功能灰度上线——无法仅对特定模块/用户开启
  3. 回滚依赖 full git revert——太重了

设计对标：
  - Google //shared/flags (Guava FeatureFlag)
  - LaunchDarkly / Unleash 的配置驱动模式
  - K8s feature gates（alpha -> beta -> GA 渐进式启用）

设计原则：
  - 配置驱动（YAML/JSON）——不改代码就能开关功能
  - 三态：ALWAYS_ON / CONDITIONAL / ALWAYS_OFF
  - 支持按 module_id / agent_id 粒度控制
  - 默认安全：新 flag 默认为 OFF（AI 新增的功能不自动打开）

AI 施工约定：
  - 所有实验性功能 MUST 通过 FeatureFlag 守护
  - AI 新加功能时 MUST 创建对应 flag（初始 OFF）
  - 运维在 config/ 中启用 flag 后才生效
  - 禁止 AI 自行修改 flag 状态——那是人工运维的权限

5.38.1/5.38.7 治本：本模块是全项目唯一 canonical 特性开关真源
（原 zephyr.orchestrator.governance.feature_flag 已删除，能力收敛于此）。

SSoT: MOD-INF-016 §2.8 shared-feature-flags
Version: 0.1.0
"""


import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, unique
from pathlib import Path
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "FeatureFlag",
    "FlagNotFoundError",
    "FlagRegistry",
    "FlagState",
    "ensure_global_flags_loaded",
    "global_flag_registry",
    "load_flags_from_yaml",
]

logger = logging.getLogger(__name__)


@unique
class FlagState(str, Enum):
    ALWAYS_ON = "ALWAYS_ON"
    CONDITIONAL = "CONDITIONAL"
    ALWAYS_OFF = "ALWAYS_OFF"


class FlagNotFoundError(ZephyrBaseError):
    """请求的 FeatureFlag 未在注册表中找到。"""

    error_code = "ZA-SH-0047"


@dataclass(frozen=True)
class FeatureFlag:
    # 5.38.9 修复: 增加生命周期管理字段 (created_at/expires_at/owner)
    key: str
    state: FlagState = FlagState.ALWAYS_OFF
    description: str = ""
    allowed_modules: list[str] = field(default_factory=list)
    allowed_agents: list[str] = field(default_factory=list)
    rollout_pct: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    owner: str = ""

    def __post_init__(self) -> None:
        # 5.155.12 修复: 添加范围校验 (0-100), 防止 >100 时恒为 True 全员启用
        # frozen dataclass 需用 object.__setattr__ 修改字段
        if self.rollout_pct < 0 or self.rollout_pct > 100:
            object.__setattr__(self, "rollout_pct", max(0, min(100, self.rollout_pct)))

    def is_expired(self, *, now: datetime | None = None) -> bool:
        """5.38.9: 判断 flag 是否已过期。expires_at 为 None 表示永不过期。"""
        if self.expires_at is None:
            return False
        ref = now or datetime.now(UTC)
        return ref >= self.expires_at

    def is_enabled(
        self,
        *,
        module_id: str | None = None,
        agent_id: str | None = None,
    ) -> bool:
        if self.state is FlagState.ALWAYS_ON:
            return True
        if self.state is FlagState.ALWAYS_OFF:
            return False

        if self.allowed_modules and module_id:
            if module_id not in self.allowed_modules:
                return False

        if self.allowed_agents and agent_id:
            if agent_id not in self.allowed_agents:
                return False

        # 5.38.5 修复: rollout_pct > 0 时必须有稳定标识符 (module_id/agent_id) 做分桶,
        # 无标识符时默认 False (安全默认)——原代码直接返回 True (CONDITIONAL)
        # 导致未传 module_id 时灰度分桶失效、全量放行
        if self.rollout_pct > 0:
            bucket_key = module_id or agent_id
            if bucket_key is None:
                return False  # 无标识符无法稳定分桶, 安全默认 OFF
            import hashlib

            bucket = int(hashlib.md5(bucket_key.encode()).hexdigest(), 16) % 100
            return bucket < self.rollout_pct

        return self.state is FlagState.CONDITIONAL


class FlagRegistry:
    """全局 FeatureFlag 注册表（单例）。

    Usage::

        registry = FlagRegistry()
        registry.register(FeatureFlag("use_gpt4o", FlagState.ALWAYS_OFF,
                                       description="启用 GPT-4o 替代 GPT-4o-mini"))

        if registry.is_enabled("use_gpt4o", module_id="MOD-CONTEXT_ENGINE"):
            model = "gpt-4o"
        else:
            model = "gpt-4o-mini"

    5.38.6 修复: 审计轨迹持久化——register/unregister/set 除写入内存
    ``_audit`` list 外，当 ``persist_audit=True``（或显式传 ``audit_path``）
    时同时追加 JSONL（默认 ``.runtime/audit/feature_flags.jsonl``，惰性解析
    REPO_ROOT；2026-08-14 自 tracked 区 data/audit_logs/ 迁出——#55/
    #ARCH-RECONCILER-AUTO-DELETE-GOV-001 裁定4：门禁运行写 tracked 文件致
    外部 pre-commit 链结构性不可过，审计写一律落 gitignored 运行区）。
    默认实例不持久化，避免测试意外写生产路径（ARCH-BENCH-LEAK-001）。
    审计写入失败仅 warning，绝不阻断 flag 操作。
    """

    def __init__(
        self,
        *,
        audit_path: Path | str | None = None,
        persist_audit: bool = False,
    ) -> None:
        self._flags: dict[str, FeatureFlag] = {}
        self._audit: list[dict[str, Any]] = []
        self._audit_path: Path | None = Path(audit_path) if audit_path is not None else None
        self._persist_audit: bool = persist_audit or self._audit_path is not None

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def audit(self) -> list[dict[str, Any]]:
        """只读：audit（Stage 4 公共化）。"""
        return self._audit

    @audit.setter
    def audit(self, value):
        """写入：audit（Stage 4 公共化）。"""
        self._audit = value

    @property
    def flags(self) -> dict[str, FeatureFlag]:
        """只读：flags（Stage 4 公共化）。"""
        return self._flags

    @flags.setter
    def flags(self, value):
        """写入：flags（Stage 4 公共化）。"""
        self._flags = value

    def _default_audit_path(self) -> Path | None:
        """惰性解析默认审计路径——shared 层禁止向上 import audit 组件，JSONL 落盘即可。"""
        try:
            from zephyr.shared.io.paths import REPO_ROOT

            # #55 治本（2026-08-14）：审计写迁出 tracked 区 → .runtime/audit/（gitignored）
            return REPO_ROOT / ".runtime" / "audit" / "feature_flags.jsonl"
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return None

    def _record_audit(self, action: str, *, key: str, state: str = "", description: str = "") -> None:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "action": action,
            "key": key,
            "state": state,
            "description": description,
        }
        self._audit.append(entry)
        if not self._persist_audit:
            return
        path = self._audit_path if self._audit_path is not None else self._default_audit_path()
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001 — 审计写入失败绝不阻断 flag 操作（OSError/ValueError 等）
            logger.warning("flag audit write failed (%s): %s", path, exc)

    def register(self, flag: FeatureFlag) -> None:
        self._flags[flag.key] = flag
        self._record_audit("register", key=flag.key, state=flag.state.value, description=flag.description)
        logger.info("feature flag registered: %s (state=%s)", flag.key, flag.state.value)

    def unregister(self, key: str) -> None:
        existed = self._flags.pop(key, None)
        self._record_audit("unregister", key=key, state=existed.state.value if existed else "")

    def set(self, key: str, enabled: bool, description: str = "") -> FeatureFlag:
        """便捷开关接口（收敛 orchestrator FeatureFlagManager.set，5.38.1）。

        enabled=True -> ALWAYS_ON；enabled=False -> ALWAYS_OFF（安全默认）。
        """
        flag = FeatureFlag(
            key=key,
            state=FlagState.ALWAYS_ON if enabled else FlagState.ALWAYS_OFF,
            description=description,
        )
        self.register(flag)
        return flag

    def get_all(self) -> dict[str, bool]:
        """返回 {key: 当前是否启用} 映射（收敛 FeatureFlagManager.get_all，5.38.1）。"""
        return {k: f.is_enabled() for k, f in self._flags.items()}

    def get(self, key: str) -> FeatureFlag:
        flag = self._flags.get(key)
        if flag is None:
            raise FlagNotFoundError(
                f"FeatureFlag '{key}' not found in registry",
                details={"key": key},
            )
        return flag

    def is_enabled(
        self,
        key: str,
        *,
        module_id: str | None = None,
        agent_id: str | None = None,
        default: bool | None = None,
    ) -> bool:
        """查询 flag 是否启用。

        flag 未注册时：``default`` 非 None 则返回 ``default``（调用方显式声明
        缺省语义，如守护点默认 ON 可关闭）；``default`` 为 None 则抛
        FlagNotFoundError（安全默认，未注册不等于启用）。
        """
        flag = self._flags.get(key)
        if flag is None:
            if default is not None:
                return default
            raise FlagNotFoundError(
                f"FeatureFlag '{key}' not found in registry",
                details={"key": key},
            )
        return flag.is_enabled(module_id=module_id, agent_id=agent_id)

    def list_all(self) -> dict[str, FeatureFlag]:
        return dict(self._flags)

    def reset(self) -> None:
        self._flags.clear()


global_flag_registry = FlagRegistry(persist_audit=True)


_DEFAULT_FLAGS_YAML = "config/flags.yaml"


def _default_flags_yaml_path() -> Path | None:
    try:
        from zephyr.shared.io.paths import REPO_ROOT

        return REPO_ROOT / _DEFAULT_FLAGS_YAML
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None


def load_flags_from_yaml(
    path: Path | str | None = None,
    *,
    registry: FlagRegistry | None = None,
) -> int:
    """5.38.4 修复: 从 YAML 加载特性开关到 FlagRegistry。

    默认读取 ``config/flags.yaml`` 的 ``flags:`` 段并注册到
    ``global_flag_registry``——每个顶层 key 映射为一个 FeatureFlag：
    ``enabled: true`` -> ALWAYS_ON，否则 -> ALWAYS_OFF（安全默认）。
    重复调用幂等（同 key 覆盖注册）。返回注册的 flag 数。
    """
    reg = registry if registry is not None else global_flag_registry
    yaml_path = Path(path) if path is not None else _default_flags_yaml_path()
    if yaml_path is None or not yaml_path.exists():
        logger.warning("flags yaml not found: %s", yaml_path)
        return 0

    import yaml

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    flags_section = data.get("flags") or {}
    count = 0
    for key, spec in flags_section.items():
        if not isinstance(spec, dict):
            continue
        reg.register(
            FeatureFlag(
                key=str(key),
                state=FlagState.ALWAYS_ON if spec.get("enabled", False) else FlagState.ALWAYS_OFF,
                description=str(spec.get("description", "")),
            )
        )
        count += 1
    logger.info("loaded %d feature flags from %s", count, yaml_path)
    return count


_global_flags_loaded = False


def ensure_global_flags_loaded() -> int:
    """5.38.2 修复: 启动流程幂等加载入口——首次调用时把 config/flags.yaml
    注册进 global_flag_registry，后续调用直接返回当前 flag 数（不重复注册）。
    """
    global _global_flags_loaded
    if _global_flags_loaded:
        return len(global_flag_registry.list_all())
    _global_flags_loaded = True
    return load_flags_from_yaml()
