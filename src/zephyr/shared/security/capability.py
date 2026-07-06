# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.security.capability
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_capability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CBAC 能力检查器 (Capability-Based Access Control)

任务编号 : T-V2-004（experimental CBAC 最小版）
权限层级 : Immutable Core（G1 §2.10 声明）
真源声明 : ai_autonomy_authority_registry.yaml §2.10
创建日期 : 2026-04-27

功能说明
--------
基于 config/capabilities.yaml 的能力注册表，提供运行时权限检查：
1. 启动时一次性加载 YAML 规则
2. capability_check(action, target_path) 入口函数
3. deny 规则不可绕过（命中 deny 必须返回 CapabilityDenied）
4. allow 规则支持 glob 多模式 OR 匹配
5. ai_modifiable 能力调用带 provenance: True 标记
"""

from __future__ import annotations

from typing import Final
import fnmatch
from pathlib import Path
from threading import RLock
from typing import Any, Self, final

try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "pydantic 未安装，请运行: pip install pydantic>=2.0.0\n"
        "或一键就绪: python scripts/governance/env_check.py --install"
    )

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML 未安装，请运行 `pip install pyyaml`")

from zephyr.shared.io.paths import REPO_ROOT

CAPABILITIES_YAML_PATH: Final[Path] = REPO_ROOT / "config" / "capabilities.yaml"


class CapabilityDenied(Exception):
    def __init__(self, action: str, target_path: str, rule_name: str, reason: str = "deny"):
        self.action = action
        self.target_path = target_path
        self.rule_name = rule_name
        self.reason = reason
        super().__init__(
            f"CapabilityDenied: action='{action}' target='{target_path}' rule='{rule_name}' reason='{reason}'"
        )


@final
class Capability(BaseModel, frozen=True):
    name: str = Field(min_length=1)
    description: str = ""
    allow: list[str] = Field(default_factory=list)
    deny: list[str] = Field(default_factory=list)


class CapabilityRegistry:
    _instance: CapabilityRegistry | None = None
    _initialized: bool = False
    _lock = RLock()

    def __new__(cls) -> Self:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        # Phase 2 P2 修复（并发安全 MEDIUM）：__init__ 双重检查锁——__new__ 已加锁但 __init__ 未加锁，并发首次调用可重复 _load_from_yaml
        with type(self)._lock:
            if self._initialized:
                return
            self._capabilities: list[Capability] = []
            self._load_from_yaml()
            self._initialized = True

    def _load_from_yaml(self) -> None:
        if not CAPABILITIES_YAML_PATH.exists():
            import warnings

            warnings.warn(
                f"capabilities.yaml not found: {CAPABILITIES_YAML_PATH} — registry empty, all operations denied",
                stacklevel=2,
            )
            return
        with open(CAPABILITIES_YAML_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or "rules" not in data:
            import warnings

            warnings.warn(
                "capabilities.yaml empty or missing 'rules' key — registry empty, all operations denied",
                stacklevel=2,
            )
            return
        for rule_data in data["rules"]:
            cap = Capability(
                name=rule_data.get("name", ""),
                description=rule_data.get("description", ""),
                allow=rule_data.get("allow", []),
                deny=rule_data.get("deny", []),
            )
            if not cap.allow and not cap.deny:
                import warnings

                warnings.warn(
                    f"Capability rule '{cap.name}' has empty allow and deny — dead rule (matches nothing)",
                    stacklevel=2,
                )
            for patterns, field_name in [(cap.allow, "allow"), (cap.deny, "deny")]:
                for pat in patterns:
                    if "{" in pat or "}" in pat:
                        import warnings

                        warnings.warn(
                            f"Capability rule '{cap.name}' {field_name} pattern '{pat}' "
                            f"contains {{ or }} — brace expansion not supported by fnmatch. "
                            f"The pattern will match literal curly braces only (effectively dead). "
                            f"Expand into multiple independent patterns instead.",
                            stacklevel=2,
                        )
            self._capabilities.append(cap)

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls._initialized = False

    @property
    def capabilities(self) -> list[Capability]:
        return list(self._capabilities)

    def _match_glob(self, pattern: str, path: str) -> bool:
        normalized_pattern = pattern.replace("\\", "/")
        normalized_path = path.replace("\\", "/")
        if "**" in normalized_pattern:
            parts = normalized_pattern.split("**", 1)
            prefix = parts[0]
            suffix = parts[1].lstrip("/") if len(parts) > 1 else ""
            if prefix and not normalized_path.startswith(prefix):
                return False
            if not suffix:
                return True
            filename = normalized_path.split("/")[-1]
            return fnmatch.fnmatch(filename, suffix)
        return fnmatch.fnmatch(normalized_path, normalized_pattern)

    def _match_any_glob(self, patterns: list[str], path: str) -> bool:
        for pattern in patterns:
            if self._match_glob(pattern, path):
                return True
        return False

    def check(self, action: str, target_path: str) -> tuple[bool, dict[str, Any]]:
        relative_path = target_path
        if Path(target_path).is_absolute():
            try:
                relative_path = str(Path(target_path).relative_to(REPO_ROOT))
            except ValueError:
                relative_path = target_path

        relative_path = relative_path.replace("\\", "/")

        for cap in self._capabilities:
            deny_matched = self._match_any_glob(cap.deny, relative_path)
            allow_matched = self._match_any_glob(cap.allow, relative_path)
            if deny_matched and not allow_matched:
                return False, {
                    "action": action,
                    "target": relative_path,
                    "rule": cap.name,
                    "reason": "deny",
                    "provenance": False,
                }

        for cap in self._capabilities:
            if self._match_any_glob(cap.allow, relative_path):
                return True, {
                    "action": action,
                    "target": relative_path,
                    "rule": cap.name,
                    "reason": "allow",
                    "provenance": True,
                }

        return False, {
            "action": action,
            "target": relative_path,
            "rule": "default_deny",
            "reason": "no_matching_rule",
            "provenance": False,
        }


def capability_check(action: str, target_path: str) -> tuple[bool, dict[str, Any]]:
    registry = CapabilityRegistry()
    allowed, info = registry.check(action, target_path)
    if not allowed:
        raise CapabilityDenied(
            action=action,
            target_path=target_path,
            rule_name=info.get("rule", "unknown"),
            reason=info.get("reason", "unknown"),
        )
    return allowed, info
