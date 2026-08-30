# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.resilience.degradation_chain
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: degradation_chain.py
# 层: 算法
# - id: A1
#   name_zh: ① DegradationChain
#   name_en: DegradationChain
#   intro: class DegradationChain 源码 L82-L129
#   desc: 公共方法（定义序）: config, get_chain, add_component, add_dependency, propagate；源码 L82-L129
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DegradationChain
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

try:
    from zephyr.shared.io.paths import REPO_ROOT
except ImportError:
    REPO_ROOT = Path(__file__).resolve().parents[4]  # fallback

_DEGRADATION_CONFIG_PATH: Path = REPO_ROOT / "config" / "degradation_chain.yaml"


class DegradationLevel(Enum):
    NORMAL = 0
    DEGRADED = 1
    CRITICAL = 2
    FAILED = 3


@dataclass
class DegradationNode:
    component: str
    level: DegradationLevel
    affected_by: list[str] = field(default_factory=list)


class DegradationChain:
    def __init__(self):
        self._nodes: dict[str, DegradationNode] = {}
        self._edges: dict[str, list[str]] = {}
        # 治本(2026-07-17): 加载 config/degradation_chain.yaml 配置
        self._config: dict[str, Any] = self._load_config()

    @staticmethod
    def _load_config() -> dict[str, Any]:
        # 治本(2026-07-17): 消费 config/degradation_chain.yaml 真源
        if yaml is None or not _DEGRADATION_CONFIG_PATH.exists():
            return {}
        try:
            with open(_DEGRADATION_CONFIG_PATH, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return {}

    @property
    def config(self) -> dict[str, Any]:
        return self._config

    def get_chain(self, chain_id: str) -> dict[str, Any] | None:
        for chain in self._config.get("chains", []):
            if chain.get("chain_id") == chain_id:
                return chain
        return None

    def add_component(self, name: str) -> None:
        self._nodes[name] = DegradationNode(name, DegradationLevel.NORMAL)
        self._edges[name] = []

    def add_dependency(self, source: str, target: str) -> None:
        if source in self._edges:
            self._edges[source].append(target)

    def propagate(self, component: str, level: DegradationLevel) -> list[DegradationNode]:
        if component not in self._nodes:
            raise KeyError(f"Component '{component}' not registered in DegradationChain")
        affected = []
        self._nodes[component].level = level
        affected.append(self._nodes[component])
        for dep in self._edges.get(component, []):
            if dep in self._nodes and self._nodes[dep].level.value < level.value:
                self._nodes[dep].level = level
                self._nodes[dep].affected_by.append(component)
                affected.append(self._nodes[dep])
        return affected
