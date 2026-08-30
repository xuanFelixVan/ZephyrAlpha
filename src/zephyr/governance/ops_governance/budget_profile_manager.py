# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.budget_profile_manager
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: profile_path 参数
#   fields: 参数 profile_path（无注解）
#   code: budget_profile_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BudgetProfileManager
#   name_en: BudgetProfileManager
#   intro: class BudgetProfileManager 源码 L65-L152
#   desc: 公共方法（定义序）: get, list_profiles, add, remove, set_active, match_for_task；源码 L65-L152
#   inputs: profile_path
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BudgetProfileManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class BudgetProfile:
    name: str
    token_limit: int
    cost_limit: float
    time_limit: float
    model_tier: str
    description: str = ""


class BudgetProfileManager:
    DEFAULT_PROFILES: dict[str, BudgetProfile] = {
        "minimal": BudgetProfile(
            name="minimal",
            token_limit=2000,
            cost_limit=0.05,
            time_limit=60.0,
            model_tier="minimal",
            description="极简模式：最小消耗",
        ),
        "standard": BudgetProfile(
            name="standard",
            token_limit=8000,
            cost_limit=0.30,
            time_limit=300.0,
            model_tier="economy",
            description="标准模式：常规任务",
        ),
        "premium": BudgetProfile(
            name="premium",
            token_limit=16000,
            cost_limit=0.80,
            time_limit=600.0,
            model_tier="standard",
            description="高级模式：复杂任务（需审批）",
        ),
    }

    def __init__(self, profile_path: str = "config/budget_profiles.yaml"):
        self._profile_path = Path(profile_path)
        self._profiles: dict[str, BudgetProfile] = dict(self.DEFAULT_PROFILES)
        self._load()

    def _load(self) -> None:
        if self._profile_path.exists():
            with open(self._profile_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    for name, cfg in data.items():
                        self._profiles[name] = BudgetProfile(
                            name=name,
                            token_limit=cfg.get("token_limit", 8000),
                            cost_limit=cfg.get("cost_limit", 0.30),
                            time_limit=cfg.get("time_limit", 300.0),
                            model_tier=cfg.get("model_tier", "economy"),
                            description=cfg.get("description", ""),
                        )

    def _save(self) -> None:
        data = {
            name: {
                "token_limit": p.token_limit,
                "cost_limit": p.cost_limit,
                "time_limit": p.time_limit,
                "model_tier": p.model_tier,
                "description": p.description,
            }
            for name, p in self._profiles.items()
        }
        with open(self._profile_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def get(self, name: str) -> BudgetProfile | None:
        return self._profiles.get(name)

    def list_profiles(self) -> list[str]:
        return list(self._profiles.keys())

    def add(self, profile: BudgetProfile) -> None:
        self._profiles[profile.name] = profile
        self._save()

    def remove(self, name: str) -> None:
        if name in self.DEFAULT_PROFILES:
            return
        self._profiles.pop(name, None)
        self._save()

    def set_active(self, name: str) -> BudgetProfile | None:
        return self._profiles.get(name)

    def match_for_task(self, estimated_tokens: int, estimated_cost: float) -> BudgetProfile:
        best = self._profiles["minimal"]
        for p in self._profiles.values():
            if p.token_limit >= estimated_tokens and p.cost_limit >= estimated_cost:
                if p.token_limit < best.token_limit:
                    best = p
        return best
