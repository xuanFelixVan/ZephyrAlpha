# [BLUEPRINT] MOD-SIG-021 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
from zephyr.signal_ashare.signal_factory import SignalFactory
from zephyr.signal_ashare.capital_behavior_orchestrator import CapitalBehaviorOrchestrator
from zephyr.signal_ashare.auction_microstructure_analyzer import AuctionMicrostructureAnalyzer
from zephyr.signal_ashare.t0_trading_pipeline import T0TradingPipeline
from zephyr.signal_ashare.unified_pattern_engine import UnifiedPatternEngine
from zephyr.signal_ashare.risk_event_consumer import RiskEventConsumer
from zephyr.signal_ashare.factor_result_bridge import FactorResultBridge
from zephyr.signal_ashare.gap_fill_model import GapFillModel
from zephyr.signal_ashare.intraday_volume_orderflow import IntradayVolumeOrderflow
from zephyr.signal_ashare.wyckoff_accumulation_signal import WyckoffAccumulationSignal
from zephyr.signal_ashare.multi_indicator_divergence import MultiIndicatorDivergence
from zephyr.signal_ashare.relative_strength_screener import RelativeStrengthScreener
from zephyr.signal_ashare.limit_up_ecosystem_leadership import LimitUpEcosystemLeadership
from zephyr.signal_ashare.sector_momentum_persistence import SectorMomentumPersistence
from zephyr.signal_ashare.extreme_sentiment_reversal_detector import ExtremeSentimentReversalDetector
from zephyr.signal_ashare.false_breakout_trap_detector import FalseBreakoutTrapDetector
from zephyr.signal_ashare.sentiment_price_divergence import SentimentPriceDivergence
from zephyr.signal_ashare.limit_up_potential_scorer import LimitUpPotentialScorer
from zephyr.signal_ashare.bottom_confirmation_entry import BottomConfirmationEntry
from zephyr.signal_ashare.next_day_probability_gate import NextDayProbabilityGate
# NOTE(P1W05 2026-08-25): scaffold 自动追加的 5 条类级 eager import 已按可逆模式
# 注释（SellNewsOverdraftDetector/OvernightReturnExpectancy/StrategyCrossVoteFunnel/
# PatternMatchStrategyLibrary/MultiFactorTimingOverlay）——实现就位前保持包可导入；
# 实现+测试绿后由后续波次按 P1W06 先例恢复，或届时由主代理统一恢复。
# from zephyr.signal_ashare.sell_news_overdraft_detector import SellNewsOverdraftDetector
# from zephyr.signal_ashare.overnight_return_expectancy import OvernightReturnExpectancy
# from zephyr.signal_ashare.strategy_cross_vote_funnel import StrategyCrossVoteFunnel
# from zephyr.signal_ashare.pattern_match_strategy_library import PatternMatchStrategyLibrary
# from zephyr.signal_ashare.multi_factor_timing_overlay import MultiFactorTimingOverlay
# NOTE(P1W06 2026-08-25): P1W01 窗口期可逆注释的两行 export 已按 NOTE 约定恢复
# （FactorResultBridge/RiskEventConsumer 实现就位，88 测全绿）。
# [BLUEPRINT] MOD-SIGNAL_ASHARE | (pending)
# [MODULE] zephyr.signal_ashare
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
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
# 原 module_id=MOD-INF-038 与 shared/lifecycle/state_machine.py（MOD-INF-038 状态机引擎）
# 在 depgraph 撞号（跨域同 ID 双文件），2026-08-17 审计治本修正为 MOD-SIGNAL_ASHARE，
# 与本包 6 个子包 __init__ 的既有约定一致。
# [A_module] module_id=MOD-SIGNAL_ASHARE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# signal_ashare domain package
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python包导入请求
#   fields: import zephyr.signal_ashare 触发的包初始化, 无数据输入
#   code: signal_ashare/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 信号域包初始化
#   name_en: signal_ashare package init
#   intro: A股信号域的包标记文件，只声明域归属不导出任何符号，真正的实现都在子模块里
#   desc: 仅含模块头元数据(BLUEPRINT/MODULE/DOMAIN=D_ASHARE_SIGNAL等治理标记) + __all__=[] 空导出列表
#   inputs: I1
#   outputs: 空包命名空间
# 层: 输出
# - id: O1
#   name_zh: signal_ashare 包命名空间
#   name_en: zephyr.signal_ashare
#   intro: D_ASHARE_SIGNAL域包命名空间，子模块经其被导入，本身无导出符号
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = []

__all__.append("SignalFactory")

__all__.append("FactorResultBridge")

__all__.append("RiskEventConsumer")

__all__.append("CapitalBehaviorOrchestrator")

__all__.append("AuctionMicrostructureAnalyzer")

__all__.append("T0TradingPipeline")

__all__.append("UnifiedPatternEngine")

__all__.append("GapFillModel")

__all__.append("IntradayVolumeOrderflow")

__all__.append("WyckoffAccumulationSignal")

__all__.append("MultiIndicatorDivergence")

__all__.append("RelativeStrengthScreener")

__all__.append("LimitUpEcosystemLeadership")

__all__.append("SectorMomentumPersistence")

__all__.append("ExtremeSentimentReversalDetector")

__all__.append("FalseBreakoutTrapDetector")

__all__.append("SentimentPriceDivergence")

__all__.append("LimitUpPotentialScorer")

__all__.append("BottomConfirmationEntry")

__all__.append("NextDayProbabilityGate")

# NOTE(P1W05 2026-08-25): 与上方注释 import 配套，5 条 append 同步可逆注释。
# __all__.append("SellNewsOverdraftDetector")

# __all__.append("OvernightReturnExpectancy")

# __all__.append("StrategyCrossVoteFunnel")

# __all__.append("PatternMatchStrategyLibrary")

# __all__.append("MultiFactorTimingOverlay")
