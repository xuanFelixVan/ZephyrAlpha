# [BLUEPRINT] MOD-INT-EVENT-GEO | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.5b
# [MODULE] zephyr.intelligence.event_geopolitical_map
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（纯函数+静态映射表）
# [CONSUMERS] 事件驱动 sleeve（地缘/宏观事件类→受益/受害板块 alpha 方向）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 5 类地缘事件静态映射（MVP）；未知 event_nlp_tag → ([], [], 0.0) 不抛异常；event_score 沿用 26 号 §2.5 首版公式（权重 1.4×方向×情绪×衰减×1.0）；sentiment 裁剪 [-1,1]
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5b
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——未知标签/越界输入降级不抛
# [TESTS] tests/intelligence/test_event_geopolitical_map.py
# [A_module] module_id=MOD-INT-EVENT-GEO | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.5b 地缘/宏观事件→板块受益传导链
# [ALGO_FLOW]
# I1: event_nlp_tag（NLP 事件标签/规则匹配降级）+ sentiment_score∈[-1,1] + days_since_event
# F1: GEOPOLITICAL_SECTOR_MAP 静态映射查表（5 类）
# F2: event_score = 1.4 × direction × sentiment × decay(rising_hl 内 1.0 否则 0.5) × 1.0
# O1: (beneficiary_sectors, victim_sectors, event_score)
# [/ALGO_FLOW]
"""
MOD-INT-EVENT-GEO — 地缘/宏观事件→A 股板块受益传导链（26 号 §2.5b 施工化）。

MVP 静态映射表（Phase 2 演进为 NLP 动态识别）。三层正交边界：
本 sleeve 作**选股 alpha**（买受益/卖受损）；32 号作风控压力测试（RMATS）；
10 号 D-SIGNAL-68 作 regime 节流。

与 NLP 管道协同（§2.7）：地缘事件多来自海外 RSS（production）。NLP 管道须产出
``event_nlp_tag``（映射到本表 key）+ ``sentiment_score``；首版用**规则匹配**降级
（如含 "Iran/Israel/Hormuz/红海"→middle_east_conflict；"tariff/export ban/
entity list"→trade_war_escalation），NLP 就绪后升级语义分类。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5b
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event_nlp_tag 参数
#   fields: 参数 event_nlp_tag，类型注解 str
#   code: event_geopolitical_map.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: sentiment_score 参数
#   fields: 参数 sentiment_score，类型注解 float
#   code: event_geopolitical_map.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: days_since_event 参数
#   fields: 参数 days_since_event，类型注解 int
#   code: event_geopolitical_map.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① map_geopolitical_event_to_sectors
#   name_en: map_geopolitical_event_to_sectors
#   intro: 地缘事件→受益/受害板块映射 + event_score（§2.5b）。
#   desc: 地缘事件→受益/受害板块映射 + event_score（§2.5b）。 Parameters ---------- event_nlp_tag : NLP 产出的事件标签（GE…；源码 L130-L166
#   inputs: event_nlp_tag sentiment_score days_since_event
#   outputs: tuple[list[str], list[str], float]
# 层: 输出
# - id: O1
#   name_zh: tuple[list[str], list[str], float]
#   name_en: tuple[list[str], list[str], float]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 事件驱动 sleeve（地缘/宏观事件类→受益/受害板块 alpha 方向）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Any, Final

# 地缘事件类 event_score 权重（26 号 §2.5 event_class_weight，v1.6.0）
GEO_EVENT_CLASS_WEIGHT: Final[float] = 1.4
# rising 窗口内衰减因子 / 窗口外（§2.5 首版 decay_stage_factor 口径）
DECAY_FACTOR_RISING: Final[float] = 1.0
DECAY_FACTOR_AFTER: Final[float] = 0.5

# ── 地缘事件→受益板块静态映射表（26 号 §2.5b，MVP 简单映射）──
GEOPOLITICAL_SECTOR_MAP: Final[dict[str, dict[str, Any]]] = {
    "middle_east_conflict": {  # 中东冲突（美伊战争/霍尔木兹海峡/红海危机）
        "beneficiary_sectors": ["油气开采", "油气炼化", "黄金", "军工", "船舶"],
        "victim_sectors": ["航空", "化工(原油成本)", "纺织(原油成本)"],
        "transmission_logic": "地缘冲突→原油/黄金避险溢价→上游资源股受益",
        "rising_half_life_days": "5-15",  # 远长于业绩/并购（§2.4 衰减表）
        "empirical_basis": "final_report_0724: 电气设备3日+123亿/有色+144亿断层领先",
    },
    "trade_war_escalation": {  # 贸易战升级（关税/出口管制/实体清单）
        "beneficiary_sectors": ["稀土", "农业(大豆替代)", "半导体(国产替代)", "软件(信创)"],
        "victim_sectors": ["出口导向(家电/纺服)", "苹果产业链"],
        "transmission_logic": "贸易摩擦→国产替代加速+战略资源溢价→自主可控受益",
        "rising_half_life_days": "5-10",
    },
    "currency_depreciation": {  # 人民币贬值
        "beneficiary_sectors": ["出口导向(纺织/家电/机械)", "黄金"],
        "victim_sectors": ["进口导向(航空/造纸)"],
        "transmission_logic": "汇率贬值→出口竞争力提升+外币资产升值",
        "rising_half_life_days": "3-7",
    },
    "commodity_price_surge": {  # 大宗商品价格异动（铜/锂/稀土）
        "beneficiary_sectors": ["有色(对应金属)", "采掘"],
        "victim_sectors": ["下游制造(成本端)"],
        "transmission_logic": "大宗涨价→上游资源股直接受益+下游成本承压",
        "rising_half_life_days": "5-15",
    },
    "tech_sanctions": {  # 科技制裁（芯片/EDA/设备出口限制）
        "beneficiary_sectors": ["半导体(国产替代)", "软件(信创)", "军工"],
        "victim_sectors": ["被制裁企业", "依赖进口技术的企业"],
        "transmission_logic": "技术制裁→国产替代加速+自主可控战略强化",
        "rising_half_life_days": "10-20",  # 国产替代是长期逻辑，持续性最长
    },
}


def _clip_sentiment(x: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return max(-1.0, min(1.0, v))


def map_geopolitical_event_to_sectors(
    event_nlp_tag: str,
    sentiment_score: float,
    days_since_event: int = 0,
) -> tuple[list[str], list[str], float]:
    """地缘事件→受益/受害板块映射 + event_score（§2.5b）。

    Parameters
    ----------
    event_nlp_tag : NLP 产出的事件标签（GEOPOLITICAL_SECTOR_MAP 的 key；
        首版规则匹配降级，NLP 就绪后语义分类）。未知标签 → ([], [], 0.0)。
    sentiment_score : NLP 情绪分 [-1, +1]（越界裁剪）。
    days_since_event : 距事件日交易日数（衰减判定：≤rising 半衰期下限→1.0，
        否则→0.5；memo 伪代码自由变量显式化为参数）。

    Returns
    -------
    (beneficiary_sectors, victim_sectors, event_score) —— event_score 沿用
    §2.5 首版公式：1.4（地缘权重）× surprise_direction × sentiment ×
    decay_stage_factor × 1.0（地缘事件通常 |reaction|≤3%，极端修正=1.0）。
    """
    mapping = GEOPOLITICAL_SECTOR_MAP.get(event_nlp_tag, {})
    if not mapping:
        return [], [], 0.0

    beneficiary: list[str] = list(mapping["beneficiary_sectors"])
    victim: list[str] = list(mapping["victim_sectors"])
    rising_hl = int(str(mapping["rising_half_life_days"]).split("-")[0])

    event_score = (
        GEO_EVENT_CLASS_WEIGHT
        * (1 if beneficiary else -1)  # surprise_direction: 有受益板块=利好
        * _clip_sentiment(sentiment_score)
        * (DECAY_FACTOR_RISING if days_since_event <= rising_hl else DECAY_FACTOR_AFTER)
        * 1.0  # extreme_reaction_modifier：地缘事件通常 |reaction|≤3%
    )
    return beneficiary, victim, event_score


__all__: Final = [
    "GEO_EVENT_CLASS_WEIGHT",
    "DECAY_FACTOR_RISING",
    "DECAY_FACTOR_AFTER",
    "GEOPOLITICAL_SECTOR_MAP",
    "map_geopolitical_event_to_sectors",
]
