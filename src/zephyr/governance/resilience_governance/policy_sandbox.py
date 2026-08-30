# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.policy_sandbox
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: policy_path 参数
#   fields: 参数 policy_path（无注解）
#   code: policy_sandbox.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PolicySandbox
#   name_en: PolicySandbox
#   intro: class PolicySandbox 源码 L66-L194
#   desc: 公共方法（定义序）: sandbox_policy, policy_path, changes, assess_impact, set_nested, load_current, start_sandbox, prop…
#   inputs: policy_path
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: PolicySandbox
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import copy
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SandboxTrial:
    policy_changes: dict
    simulated_impact: dict[str, float]
    safe: bool
    rollback_available: bool
    trial_id: str
    timestamp: float = field(default_factory=time.time)


class PolicySandbox:
    def __init__(self, policy_path: str | None = None):
        """初始化 PolicySandbox。

        Args:
            policy_path: 预算策略 YAML 路径。None 时使用项目根的
                config/budget_policy.yaml 绝对路径（铁律：禁相对路径）。
        """
        if policy_path is None:
            # 项目根 = src/zephyr/governance/resilience_governance -> 上溯 4 级
            _project_root = Path(__file__).resolve().parents[4]
            self._policy_path = _project_root / "config" / "budget_policy.yaml"
        else:
            self._policy_path = Path(policy_path)
        self._sandbox_policy: dict | None = None
        self._changes: dict = {}
        self._trials: list[SandboxTrial] = []
        self._trial_counter: int = 0

    @property
    def sandbox_policy(self) -> dict | None:
        """只读：sandbox_policy（Stage 4 公共化）。"""
        return self._sandbox_policy

    @sandbox_policy.setter
    def sandbox_policy(self, value):
        """写入：sandbox_policy（Stage 4 公共化）。"""
        self._sandbox_policy = value

    @property
    def policy_path(self):
        """只读：policy_path（Stage 4 公共化）。"""
        return self._policy_path

    @policy_path.setter
    def policy_path(self, value):
        """写入：policy_path（Stage 4 公共化）。"""
        self._policy_path = value

    @property
    def changes(self) -> dict:
        """只读：changes（Stage 4 公共化）。"""
        return self._changes

    @changes.setter
    def changes(self, value):
        """写入：changes（Stage 4 公共化）。"""
        self._changes = value

    def assess_impact(self, policy) -> dict[str, float]:
        """公共接口：assess_impact（Stage 4 公共化）。"""
        return self._assess_impact(policy)

    @staticmethod
    def set_nested(d: dict, path: str, value) -> None:
        keys = path.split(".")
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def load_current(self) -> dict:
        with open(self._policy_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def start_sandbox(self) -> None:
        self._sandbox_policy = self.load_current()
        self._changes = {}

    def propose_change(self, path: str, value) -> None:
        if self._sandbox_policy is None:
            self.start_sandbox()
        self._changes[path] = value

    def simulate(self) -> SandboxTrial:
        if self._sandbox_policy is None:
            self.start_sandbox()
        trial_policy = copy.deepcopy(self._sandbox_policy)
        for path, value in self._changes.items():
            self._set_nested(trial_policy, path, value)

        impact = self._assess_impact(trial_policy)
        safe = all(v < 1.0 for v in impact.values())
        self._trial_counter += 1

        trial = SandboxTrial(
            policy_changes=dict(self._changes),
            simulated_impact=impact,
            safe=safe,
            rollback_available=True,
            trial_id=f"trial-{self._trial_counter:04d}",
        )
        self._trials.append(trial)
        return trial

    def commit(self) -> None:
        if self._sandbox_policy is None:
            return
        trial_policy = copy.deepcopy(self._sandbox_policy)
        for path, value in self._changes.items():
            self._set_nested(trial_policy, path, value)
        trial_policy["policy_version"] = f"0.{self._trial_counter}.0-sandbox"
        trial_policy["last_updated"] = time.strftime("%Y-%m-%d")
        with open(self._policy_path, "w", encoding="utf-8") as f:
            yaml.dump(trial_policy, f, default_flow_style=False, allow_unicode=True)

    def rollback(self) -> None:
        self._sandbox_policy = None
        self._changes = {}

    def _assess_impact(self, policy: dict) -> dict[str, float]:
        impact: dict[str, float] = {}
        levels = policy.get("budget_levels", {})
        for level_name, cfg in levels.items():
            hard = cfg.get("hard_limit", 0)
            soft = cfg.get("soft_limit", 0)
            if hard > 0 and soft > 0:
                ratio = soft / hard
                impact[f"{level_name}_strictness"] = ratio
            else:
                impact[f"{level_name}_strictness"] = 0.5
        return impact

    @staticmethod
    def _set_nested(d: dict, path: str, value) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return PolicySandbox.set_nested(d, path, value)

    def recent_trials(self, n: int = 10) -> list[SandboxTrial]:
        return self._trials[-n:]
