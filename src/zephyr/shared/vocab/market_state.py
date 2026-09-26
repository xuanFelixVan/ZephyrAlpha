# [BLUEPRINT] SH-VOCAB-001 | docs/_working/daily_loop_campaign/02_state_vocabulary_unification.md（立法真源） | §
# [MODULE] zephyr.shared.vocab.market_state
# [DOMAIN] D_SHARED
# [DEPENDENCIES] stdlib.enum
# [CONSUMERS] 全系统状态/情绪消费方（存量 28 套词表逐步收编，映射见
#             docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯常量零逻辑零IO；新增状态值必须先登记 state_vocabulary_registry
# [MODIFY-GUARD] 新增/改名状态值前置=state_vocabulary_registry.yaml 登记
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] n/a（纯常量，无运行期错误面）
# [TESTS] tests/plan_engine/test_daily_loop_master_switch.py（回归冒烟，不直测本模块）
# [A_module] module_id=SH-VOCAB-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""官方状态词表——全系统描述大盘状态与情绪阶段的唯一官方常量本体（W1 立法件）。

立法依据：DLOOP-V2-STATE-VOCAB-UNIFICATION 第一步"词表本体立法"（Owner 已批 W1+W2）。
零逻辑零 IO：本模块只声明常量，不做任何计算、不读任何外部数据；消费方自行取值。

撞名消歧（普查冲突 C1）：AnchoredTier 的 r1-r4 与 MacroRegime 的 r1-r4 撞号且语义
几乎镜像（HMM 七态 r3=牛市趋势 vs 锚定四档 r3=低风险），消费时必须声明轴来源
（宏观 regime 轴 or 个股锚定风险档轴），禁止裸写 "r1"~"r4" 字面量跨轴传递。

"最坏状态"统一口径（普查冲突 C11）：九种写法经 EXTREME_STATE_ALIASES 归一到
MacroRegimeVocab.R10，禁止消费方自建别名表。

# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/market_state.yaml
"""

from enum import Enum
from typing import Final

__all__: Final[list[str]] = [
    "ANCHORED_R1",
    "ANCHORED_R2",
    "ANCHORED_R3",
    "ANCHORED_R4",
    "AnchoredTierVocab",
    "EmotionCycleSixVocab",
    "EXTREME_STATE_ALIASES",
    "INTRADAY_TO_SIX",
    "IntradayFiveVocab",
    "MacroRegimeVocab",
]


class MacroRegimeVocab(Enum):
    """宏观 regime 轴官方词表：HMM 七态（官方宏观轴）。

    出处：src/zephyr/regime/core/regime_detector.py:107（REGIME_STATES，
    10_regime_detector_spec §3；r10 CRISIS / r11 RECOVERY / r12 BREAKOUT 为叠加态）。
    """

    R1 = "低波震荡"
    R2 = "中波震荡"
    R3 = "牛市趋势"
    R4 = "熊市阴跌"
    R10 = "危机"
    R11 = "修复"
    R12 = "突破"


class EmotionCycleSixVocab(Enum):
    """情绪周期六段官方词表（官方情绪轴）。

    出处：config/trading_decision_map.yaml:4474（state_matrix.states，v1.2 定稿，
    Owner 裁定"机构命名+修复期独立成段"，Wyckoff 阶段论+行为金融标准术语）。
    """

    CAPITULATION = "投降(冰点)"
    ACCUMULATION = "蓄势"
    IGNITION = "点火"
    EXPANSION = "主升"
    EUPHORIA = "亢奋"
    DISTRIBUTION = "退潮(派发)"


class IntradayFiveVocab(Enum):
    """盘中五态官方词表（盘中情绪/盘面强度轴）。

    出处：TDM 六段上游的盘中判别口径（盘中五态→情绪六段降采样消费，
    立法真源 02_state_vocabulary_unification.md §3 第二步挂起项的现状固化）。
    """

    LOW = "低迷"
    DEFENSE = "防御"
    OSCILLATION = "震荡"
    ATTACK = "进攻"
    EUPHORIC = "亢奋"


# 盘中五态 → 情绪周期六段映射（降采样口径）。
# 注意：亢奋→IGNITION 为 proposed 待 Owner 校准（亢奋亦可主张 EUPHORIA，
# 立法真源 §3 第二步"盘中五态→六段映射挂起等 4 态收敛专项定论"）。
INTRADAY_TO_SIX: dict[IntradayFiveVocab, EmotionCycleSixVocab] = {
    IntradayFiveVocab.LOW: EmotionCycleSixVocab.CAPITULATION,
    IntradayFiveVocab.DEFENSE: EmotionCycleSixVocab.DISTRIBUTION,
    IntradayFiveVocab.OSCILLATION: EmotionCycleSixVocab.ACCUMULATION,
    IntradayFiveVocab.ATTACK: EmotionCycleSixVocab.EXPANSION,
    IntradayFiveVocab.EUPHORIC: EmotionCycleSixVocab.IGNITION,  # proposed 待 Owner 校准
}


class AnchoredTierVocab:
    """锚定四档消歧常量（个股锚定风险档轴，非宏观 regime 轴）。

    出处：src/zephyr/regime/core/anchored_state_machine.py:86（STATE_NAMES）。
    与 MacroRegime 的 r1-r4 撞号（普查冲突 C1），且语义几乎镜像
    （锚定档 r3=低风险 vs HMM 七态 r3=牛市趋势）——消费时必须声明轴来源，
    禁止跨轴传递裸 "r1"~"r4" 字面量。
    """

    ANCHORED_R1 = "中高风险"
    ANCHORED_R2 = "中风险"
    ANCHORED_R3 = "低风险"
    ANCHORED_R4 = "高风险"


# 模块级消歧常量（消费方免 class 前缀直接引用，语义同 AnchoredTier）。
ANCHORED_R1 = AnchoredTierVocab.ANCHORED_R1
ANCHORED_R2 = AnchoredTierVocab.ANCHORED_R2
ANCHORED_R3 = AnchoredTierVocab.ANCHORED_R3
ANCHORED_R4 = AnchoredTierVocab.ANCHORED_R4

# 市场"最坏状态"九种写法 → 官方统一值 MacroRegimeVocab.R10（普查冲突 C11 的止血映射）。
# 九种写法：r10(=CRISIS 本尊) / crisis / CRISIS(vol>0.9) / EMERGENCY / CRASH /
# S0_ICE / ICE / 冰点 / 退潮。消费方禁止再自建别名表；新写法先登记
# state_vocabulary_registry 再入本表。
# 用途限定：仅宏观 regime 语境归一（冰点/退潮 在情绪轴另有语义，禁跨轴引用——红队 P2-10）
EXTREME_STATE_ALIASES: dict[str, MacroRegimeVocab] = {
    "CRISIS": MacroRegimeVocab.R10,  # 红队补漏：裸大写 CRISIS（大小写口径：先精确后小写）
    "r10": MacroRegimeVocab.R10,
    "crisis": MacroRegimeVocab.R10,
    "CRISIS(vol>0.9)": MacroRegimeVocab.R10,
    "EMERGENCY": MacroRegimeVocab.R10,
    "CRASH": MacroRegimeVocab.R10,
    "S0_ICE": MacroRegimeVocab.R10,
    "ICE": MacroRegimeVocab.R10,
    "冰点": MacroRegimeVocab.R10,
    "退潮": MacroRegimeVocab.R10,
}
