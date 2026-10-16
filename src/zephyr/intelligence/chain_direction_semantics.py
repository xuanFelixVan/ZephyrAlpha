# [BLUEPRINT] MOD-SIG-162 | docs/_working/infoaxis/10_chain_workbook.md §2/§3/§6-D2 | 方向语义件
# [MODULE] zephyr.intelligence.chain_direction_semantics
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（纯内存语义表；触发词表+方向矩阵零 IO）
# [CONSUMERS] chain_impact_resolver.resolve_directed（事件类型×链上角色→符号翻转）;
#   chain_impact_stream（事件分类注入，二期接线）; W1-W6 管线结案面; condaxis S5 双锚
#   （建议默认 A：规则词表先行+LLM 蒸馏后置走 LSG——LLM 蒸馏面不在本件）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯内存语义表零 IO 零触网; 事件类型封闭集（六类 v0，扩展须同步测试+词表册）;
#   方向矩阵=事件类型×(供方侧/需方侧)→符号乘子 ∈{+1,-1}，机械可查禁语义裁量;
#   角色判定真源=supplies_to 边方向（供→客）——structure/supply 边无向时 role 未知→乘子恒 +1
#   （同向传导=旧 MVP 行为，方向语义只对可判定角色的跳生效，禁硬猜）; 触发词分类=最长词优先
#   （linker 同款纪律）; 未命中词表→event_type=None（调用方按无向同向处理，fail-open 禁抛）;
#   判据数值零自拟（符号翻转是结构性语义非数值门柱）
# [MODIFY-GUARD] tests/intelligence/test_chain_direction_semantics.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] classify 空文本→None; role_sign 未知类型→+1 留痕非抛; 全模块禁抛（语义件）
# [TESTS] tests/intelligence/test_chain_direction_semantics.py
# [TTL] permanent

"""链上事件方向语义件（st-infoaxis-20261013 P2 传导链主施工面＝S5/W4 遗留"成本反号未建模"之闭合）。

真源：docs/_working/infoaxis/10_chain_workbook.md §3（外部对标裁定：事件类型×主体角色→方向
符号两段式，勿硬写链向反号词表——本件=第一段事件分类+符号矩阵；第二段 LLM 蒸馏后置走 LSG）。

方向矩阵语义（经济逻辑，非数值门柱）：
  涨价：供方受益（售价↑），需方受损（成本↑）——W4 known simplification 的核心反例
  断供：供方出货受阻受损，原需方断料受损，替代供方受益
  扩产：设备/原料需方受益（订单↑），同业竞争者受损
  订单（大额中标）：承接方（供方）受益，同业竞争者受损
  技术突破：突破方受益，被替代技术链受损（近似按供需角色）
  政策利好：产业链两侧同向受益（不翻号，细分留 LLM 蒸馏）
# [ALGO_FLOW]
# 层: 输入 → 触发词分类 → 角色符号查表
# - 输入: 事件文本/标题（classify）; (event_type, side)（role_sign）
# - 分类: 六类触发词表最长词优先单遍扫描，多类命中取词长和最大者
# - 查表: 方向矩阵[event_type][side] → ±1（涨价·需方=-1 断供双侧=-1 替代方=+1 等）
# [/ALGO_FLOW]
"""

from __future__ import annotations

from typing import Final

__all__: Final = [
    "EVENT_TYPES",
    "TRIGGER_LEXICON",
    "DIRECTION_MATRIX",
    "classify_event",
    "role_sign",
    "effective_sign",
]

#: 事件类型封闭集 v0（六类；扩展须同步词表+矩阵+测试）
EVENT_TYPES: Final[tuple[str, ...]] = (
    "price_up",  # 涨价（原料/产品价格上涨）
    "supply_cut",  # 断供（停产/缺货/出口管制/制裁）
    "capacity_exp",  # 扩产（扩产/新产线/增资扩产）
    "big_order",  # 大额订单/中标
    "tech_break",  # 技术突破/国产替代
    "policy_good",  # 政策利好（产业政策/补贴）
)

#: 触发词表 v0（规则词表先行；LLM 蒸馏后置=condaxis S5 默认 A）——最长词优先
TRIGGER_LEXICON: Final[dict[str, tuple[str, ...]]] = {
    "price_up": ("涨价", "提价", "价格上调", "价格上涨", "价格飙升", "缺货涨价", "供需紧张", "上涨", "大涨", "创新高"),
    "supply_cut": ("断供", "停产", "减产", "供应中断", "出口管制", "制裁", "禁运", "缺芯", "断料"),
    "capacity_exp": ("扩产", "新增产能", "新产线", "产能翻倍", "增资扩产", "投产"),
    "big_order": ("中标", "签订大额", "大额订单", "斩获订单", "订单暴涨", "框架协议"),
    "tech_break": ("技术突破", "国产替代", "自主研发成功", "量产突破", "专利获批", "打破垄断"),
    "policy_good": ("政策利好", "产业政策", "补贴", "税收优惠", "纳入规划", "专项资金"),
}

#: 方向矩阵：事件类型 × 链上角色侧 → 符号乘子（+1 同向 / -1 反号）
#: role 侧判定真源=supplies_to 边方向；structure/supply 边 role 未知→恒 +1（同向 MVP 保留）。
DIRECTION_MATRIX: Final[dict[str, dict[str, int]]] = {
    "price_up": {"supplier_side": 1, "customer_side": -1},
    "supply_cut": {"supplier_side": -1, "customer_side": -1, "substitute_side": 1},
    "capacity_exp": {"supplier_side": 1, "customer_side": 1, "peer_side": -1},
    "big_order": {"supplier_side": 1, "customer_side": 1, "peer_side": -1},
    "tech_break": {"supplier_side": 1, "customer_side": 1, "disrupted_side": -1},
    "policy_good": {"supplier_side": 1, "customer_side": 1},
}


def classify_event(text: str) -> str | None:
    """事件文本 → 事件类型（最长词优先；多类命中取命中词总长最大者；未命中→None）。"""
    if not text:
        return None
    scores: dict[str, int] = {}
    for etype, words in TRIGGER_LEXICON.items():
        total = sum(len(w) for w in words if w in text)
        if total > 0:
            scores[etype] = total
    if not scores:
        return None
    return max(scores.items(), key=lambda kv: (kv[1], kv[0]))[0]


def role_sign(event_type: str | None, side: str) -> int:
    """方向矩阵查表：未知类型/未知侧→+1（同向留痕，禁抛禁硬猜）。"""
    if event_type is None:
        return 1
    return DIRECTION_MATRIX.get(event_type, {}).get(side, 1)


def effective_sign(polarity_sign: int, event_type: str | None, side: str) -> int:
    """事件对某侧标的的有效方向 = polarity 符号 × 角色乘子。"""
    return polarity_sign * role_sign(event_type, side)
