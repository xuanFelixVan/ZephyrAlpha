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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 项目级状态机框架 StateMachine
#   fields: StateDefinition / Transition / StateMachineConfig / StateMachineRegistry 泛型基类
#   code: zephyr.shared.lifecycle.state_machine（lifecycle_state_machine.py L26-32 import）
# - id: I2
#   name: 因子生命周期状态常量 str×8
#   fields: research/development/backtest/paper/grayscale/production/deprecated/retired
#   code: lifecycle_state_machine.py L37-44
# 层: 算法
# - id: A1
#   name_zh: ① 生命周期配置构建
#   name_en: _build_config
#   intro: 摆好8个状态、画好10条合法转换线，组装成一台状态机配置
#   desc: 8 StateDefinition（retired为终态）+ 10 Transition（线性推进+灰度回退纸面+废弃退役+异常回退research）→ StateMachineConfig(fsm_id=factor_lifecycle, initial=research)（L47-80）
#   inputs: I1 I2
#   outputs: StateMachineConfig[str]
#   invariant: 状态转换必须合法；retired为唯一终态
# - id: A2
#   name_zh: ② 全局注册表登记
#   name_en: register_factor_lifecycle
#   intro: 把因子生命周期配置登记进全局注册表，重复注册自动跳过
#   desc: get_state_machine_registry().register(config)，异常吞掉保幂等 → 返回 fsm_id（L83-96）
#   inputs: A1
#   outputs: fsm_id "factor_lifecycle"
# - id: A3
#   name_zh: ② 因子FSM实例创建
#   name_en: create_factor_fsm
#   intro: 每个因子发一台独立状态机，从 research 起跑
#   desc: _build_config() → StateMachine(config) 新实例（L99-108）
#   inputs: A1
#   outputs: StateMachine[str] 实例（初始 research）
# 层: 输出
# - id: O1
#   name_zh: 因子生命周期状态机实例 StateMachine
#   name_en: factor lifecycle FSM
#   intro: 因子从研究到退役的专属状态机，非法转换直接抛错
#   invariant: 非法转换→InvalidTransitionError
#   downstream: 六步流程 six_step_flow MOD-L02-016；治理引擎 engine MOD-L02-017
# - id: O2
#   name_zh: 状态机注册标识 fsm_id
#   name_en: registered fsm_id
#   intro: 全局注册表里的因子生命周期句柄 factor_lifecycle
#   downstream: 无下游/内部使用（全局状态机注册表）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> O2
# A3 --> O1
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
