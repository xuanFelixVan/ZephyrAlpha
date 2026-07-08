# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.policy_sandbox
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_policy_sandbox | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
        keys = path.split(".")
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def recent_trials(self, n: int = 10) -> list[SandboxTrial]:
        return self._trials[-n:]
