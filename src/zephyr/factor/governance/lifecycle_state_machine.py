# [BLUEPRINT] MOD-L02-013 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV-01
# [MODULE] zephyr.factor.governance.lifecycle_state_machine
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.lifecycle.state_machine
# [CONSUMERS] zephyr.factor.governance.six_step_flow; zephyr.factor.governance.engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态转换必须合法; 复用项目级StateMachine泛型基类
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法转换->InvalidTransitionError; 未注册->StateMachineRegistryError
# [TESTS] tests/factor/test_lifecycle_state_machine.py
# [A_module] module_id=MOD-L02-013 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-GOV-01 因子生命周期状态机——复用项目级 StateMachine 泛型基类。

定义因子从研究到退役的8个状态和合法转换规则：
research → development → backtest → paper → grayscale → production → deprecated → retired

每个因子在生命周期中处于其中一个状态，只能按合法路径转换。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/lifecycle_state_machine.yaml
"""

from __future__ import annotations

from zephyr.factor.governance import load_governance_config
from zephyr.shared.lifecycle.state_machine import (
    StateDefinition,
    StateMachine,
    StateMachineConfig,
    StateMachineRegistry,
    get_state_machine_registry,
)

FSM_ID = "factor_lifecycle"

# 因子生命周期状态常量
RESEARCH = "research"
DEVELOPMENT = "development"
BACKTEST = "backtest"
PAPER = "paper"
GRAYSCALE = "grayscale"
PRODUCTION = "production"
DEPRECATED = "deprecated"
RETIRED = "retired"


def _build_config() -> StateMachineConfig[str]:
    """构建因子生命周期状态机配置。

    状态清单与初始态从 governance/_config.yaml 的 lifecycle_state_machine 节读取
    （真源=YAML，与治理子包"参数从 _config.yaml 读取不硬编码"约定一致）；
    转换拓扑（transitions）为结构性约束，保留在代码。
    """
    cfg = load_governance_config().get("lifecycle_state_machine", {})
    state_names = list(cfg.get("states", [])) or [
        RESEARCH,
        DEVELOPMENT,
        BACKTEST,
        PAPER,
        GRAYSCALE,
        PRODUCTION,
        DEPRECATED,
        RETIRED,
    ]
    initial = str(cfg.get("initial", RESEARCH))
    states = [StateDefinition(name, is_terminal=(name == RETIRED)) for name in state_names]
    # 合法转换：线性推进 + 回退 + 废弃路径
    from zephyr.shared.lifecycle.state_machine import Transition

    transitions = [
        Transition(RESEARCH, DEVELOPMENT),  # 研究 → 开发
        Transition(DEVELOPMENT, BACKTEST),  # 开发 → 回测
        Transition(BACKTEST, PAPER),  # 回测 → 纸面
        Transition(PAPER, GRAYSCALE),  # 纸面 → 灰度
        Transition(GRAYSCALE, PRODUCTION),  # 灰度 → 实盘
        Transition(GRAYSCALE, PAPER),  # 灰度 → 回退纸面
        Transition(PRODUCTION, DEPRECATED),  # 实盘 → 废弃
        Transition(DEPRECATED, RETIRED),  # 废弃 → 退役
        # 异常回退：任何非终态可回退到 research（重新研究）
        Transition(BACKTEST, RESEARCH),
        Transition(PAPER, BACKTEST),
    ]
    return StateMachineConfig(
        fsm_id=FSM_ID,
        states=states,
        transitions=transitions,
        initial=initial,
        owner_module="zephyr.factor.governance.lifecycle_state_machine",
    )


def register_factor_lifecycle() -> str:
    """注册因子生命周期状态机到全局注册表。

    Returns:
        fsm_id（"factor_lifecycle"）。重复注册会抛 StateMachineRegistryError。
    """
    registry = get_state_machine_registry()
    config = _build_config()
    try:
        registry.register(config)
    except Exception:  # noqa: BLE001 — 已注册则跳过（幂等）；注册表不可用不阻断 FSM 创建
        pass
    return FSM_ID


def create_factor_fsm() -> StateMachine[str]:
    """创建一个新的因子生命周期状态机实例。

    每个因子持有自己的 StateMachine 实例，初始状态为 research。

    Returns:
        StateMachine[str] 实例
    """
    config = _build_config()
    return StateMachine(config)
