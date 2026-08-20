# [MODULE] zephyr.ex_core.daban_named_functions
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] （首批回测校准接线前暂无）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 梯队健康四档(PERFECT/FRACTURE/LONE_DRAGON/COLLAPSE); 死亡池扣分仅3板-40/4板-30; 竞价三维100分≥80确认/60-80观望/<60否决; 纸老虎一票否决; 量化席位hard70%降权30%/soft58%降权15%
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.1（v1.5.0）/ §3.9（v1.6.0）/ §3.11（v1.8.0）
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 评分输入夹取到合法域（Clamp，不抛异常）
# [TESTS] tests/ex_core/test_daban_named_functions.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: height_counts(高度→家数) / 高度评分三元组 / 竞价三维分+竞价涨幅+匹配量比 / 封流比+封成比 / 封板时间+量比+封单强度 / 回封时长+封单方向 / 量化席位占比
# F1: classify_echelon_health——崩塌→孤龙→中位断层→完整 四档判定
# F2: score_consecutive_height_with_death_pool——非完美梯队 3板-40/4板-30
# F3: score_auction_3d——大盘30+板块30+个股40 夹取求和→CONFIRM/WATCH/REJECT
# F4: detect_auction_paper_tiger——涨幅7-8%且匹配量<3%→一票否决
# F5: score_seal_structure——封流比/封成比双指标各50分
# F6: forecast_next_day_premium——封板时间×量能×封单→溢价区间+建议（只预测不决策）
# F7: classify_reflush_board——15分钟内回封+封单递增=良性; 20-30分钟未回封=承接崩塌
# F8: detect_quant_seat_warning——hard 70%/soft 58% 双阈值降权
# O1: 各函数 dict 结果（标签/score/区间/降权+reason）
# [/ALGO_FLOW]
"""打板 8 具名函数（24_daban_strategy_detail §3.1/§3.9/§3.11 施工，首批回测校准项）。

memo 对 8 支函数给出一行式裁定，本模块按裁定语义落成可测函数；
经验映射参数（溢价区间分档、良性回封时限等）以 memo 数字为真源，
首批回测时按 A 股实际数据校准（memo §3.5/§6 重评条件口径）。

  §3.1：classify_echelon_health / score_consecutive_height_with_death_pool
  §3.9：score_auction_3d / detect_auction_paper_tiger
  §3.11：score_seal_structure / forecast_next_day_premium /
         classify_reflush_board / detect_quant_seat_warning
"""

from __future__ import annotations

__all__ = [
    "classify_echelon_health",
    "score_consecutive_height_with_death_pool",
    "score_auction_3d",
    "detect_auction_paper_tiger",
    "score_seal_structure",
    "forecast_next_day_premium",
    "classify_reflush_board",
    "detect_quant_seat_warning",
]


def classify_echelon_health(height_counts: dict) -> str:
    """梯队健康度四档判定（§3.1，v1.5.0）：PERFECT/FRACTURE/LONE_DRAGON/COLLAPSE。

    height_counts: {连板高度: 家数}，如 {1: 8, 2: 4, 3: 2}。判定顺序：
      COLLAPSE——无任何连板（梯队崩塌）；LONE_DRAGON——全场仅存 1 只（孤板/孤龙，
      无跟风、无板块效应，§3.1 孤板炸板率 58%）；FRACTURE——1板到最高板链路存在
      0 家数断档（中位断层，含最高板≥2 但无首板支撑）；PERFECT——梯队完整。
    """
    counts = {h: c for h, c in height_counts.items() if c > 0 and h >= 1}
    if not counts:
        return "COLLAPSE"
    total = sum(counts.values())
    if total == 1:
        return "LONE_DRAGON"  # 全场仅存一只，无任何跟风梯队
    max_height = max(counts)
    for h in range(1, max_height + 1):  # 中位断层：1板→最高板链路存在断档
        if counts.get(h, 0) == 0:
            return "FRACTURE"
    return "PERFECT"


def score_consecutive_height_with_death_pool(base_score: float, echelon_height: int, echelon_health: str) -> dict:
    """中位股死亡池（§3.1，v1.5.0）：梯队断层/孤龙/崩塌时 3 板扣 40、4 板扣 30；完美梯队维持原评分。

    COLLAPSE 比 FRACTURE 更凶险（梯队全崩），按同一死亡池口径扣分（保守方向，memo 扣分语义延伸）。
    """
    deduction = 0
    if echelon_health in ("FRACTURE", "LONE_DRAGON", "COLLAPSE"):
        if echelon_height == 3:
            deduction = 40
        elif echelon_height == 4:
            deduction = 30
    score = max(base_score - deduction, 0)  # 死亡池扣分下限 0（不为负分）
    return {
        "score": score,
        "deduction": deduction,
        "reason": f"{echelon_health}梯队{echelon_height}板→扣{deduction}分"
        if deduction
        else f"{echelon_health}梯队→维持原评分",
    }


def score_auction_3d(market_score: float, sector_score: float, stock_score: float) -> dict:
    """集合竞价三维 100 分（§3.9，v1.6.0）：大盘 30+板块 30+个股 40，9:25 竞价定格后调用。

    输入为各维原始分（自动夹取到 0~上限）；总分≥80 打板确认，60-80 观望，<60 否决。
    """
    market = min(max(market_score, 0), 30)
    sector = min(max(sector_score, 0), 30)
    stock = min(max(stock_score, 0), 40)
    total = market + sector + stock
    if total >= 80:
        decision = "CONFIRM"
    elif total >= 60:
        decision = "WATCH"
    else:
        decision = "REJECT"
    return {
        "total": total,
        "market": market,
        "sector": sector,
        "stock": stock,
        "decision": decision,
        "reason": f"竞价三维{total:.0f}分→{decision}",
    }


def detect_auction_paper_tiger(auction_gain: float, matched_volume_ratio: float) -> dict:
    """纸老虎识别（§3.9，v1.6.0）：竞价涨幅 7-8% 但匹配量<总量 3%=主力演戏，一票否决（IC 胜率 95%+）。

    auction_gain: 竞价涨幅（小数，0.075=7.5%）；matched_volume_ratio: 匹配量/总量（小数）。
    """
    is_paper_tiger = (0.07 <= auction_gain <= 0.08) and matched_volume_ratio < 0.03
    return {
        "is_paper_tiger": is_paper_tiger,
        "veto": is_paper_tiger,
        "reason": f"竞价涨幅{auction_gain:.1%}+匹配量{matched_volume_ratio:.1%}"
        + ("→纸老虎一票否决" if is_paper_tiger else "→非纸老虎"),
    }


def score_seal_structure(seal_flow_ratio: float, seal_success_ratio: float) -> dict:
    """封单结构双指标（§3.11①，v1.8.0）：封流比≥5%稳定/<2%薄弱 + 封成比>10稳定/<1不牢。

    双指标各 50 分：封流比≥5%→50 / 2%-5%→25 / <2%→0；封成比>10→50 / 1-10→25 / ≤1→0。
    """
    if seal_flow_ratio >= 0.05:
        flow_pts, flow_label = 50, "稳定"
    elif seal_flow_ratio >= 0.02:
        flow_pts, flow_label = 25, "一般"
    else:
        flow_pts, flow_label = 0, "薄弱"
    if seal_success_ratio > 10:
        success_pts, success_label = 50, "稳定"
    elif seal_success_ratio > 1:
        success_pts, success_label = 25, "一般"
    else:
        success_pts, success_label = 0, "不牢"
    score = flow_pts + success_pts
    if score >= 80:
        label = "STABLE"
    elif score >= 50:
        label = "NEUTRAL"
    else:
        label = "WEAK"
    return {
        "score": score,
        "label": label,
        "reason": f"封流比{seal_flow_ratio:.1%}({flow_label})+封成比{seal_success_ratio:.1f}({success_label})→{label}",
    }


def forecast_next_day_premium(seal_time: str, volume_surge: float, seal_strength: float) -> dict:
    """次日溢价三维预测（§3.11②，v1.8.0）：封板时间×量能×封单→预期溢价区间+操作建议。

    只输出预测不做决策（决策归 §3.13#1 NextDayExitDecision）。
    经验映射（首批回测校准）：封板时间 40（首封≤10:00 满分，14:30 后尾盘偷袭板 0 分——
    §3.1 尾盘偷袭板炸板率 52%）+ 量能 30（量比 2-5 最佳）+ 封单 30（封流比≥5% 满分）。
    """
    hour, minute = (int(x) for x in seal_time.split(":"))
    if (hour, minute) <= (10, 0):
        time_pts = 40
    elif (hour, minute) <= (13, 30):
        time_pts = 25
    elif (hour, minute) <= (14, 30):
        time_pts = 10
    else:
        time_pts = 0  # 尾盘偷袭板
    if 2.0 <= volume_surge <= 5.0:
        volume_pts = 30
    elif 1.0 <= volume_surge < 2.0 or 5.0 < volume_surge <= 8.0:
        volume_pts = 15
    else:
        volume_pts = 5  # 缩量(<1)或爆量(>8)均非良性
    seal_pts = 30 if seal_strength >= 0.05 else (15 if seal_strength >= 0.02 else 5)
    score = time_pts + volume_pts + seal_pts
    if score >= 70:
        low, high, advice = 0.02, 0.05, "溢价预期强→可持有至高开止盈"
    elif score >= 40:
        low, high, advice = -0.01, 0.02, "溢价预期中性→竞价观察"
    else:
        low, high, advice = -0.05, -0.01, "溢价预期弱→低开预警，竞价减仓"
    return {
        "premium_low": low,
        "premium_high": high,
        "score": score,
        "advice": advice,
        "reason": f"封板{seal_time}({time_pts})+量比{volume_surge:.1f}({volume_pts})+封单{seal_strength:.1%}({seal_pts})→溢价[{low:.0%},{high:.0%}]",
    }


def classify_reflush_board(resealed: bool, minutes_since_break: float, seal_increasing: bool) -> dict:
    """回封生死线决策（§3.11③，v1.8.0）：15 分钟内回封+封单递增=良性；20-30 分钟无法回封=承接崩塌。"""
    if resealed:
        if minutes_since_break <= 15 and seal_increasing:
            return {
                "label": "BENIGN_RESEAL",
                "action": "HOLD",
                "reason": f"{minutes_since_break:.0f}分钟内回封+封单递增→良性",
            }
        return {
            "label": "WEAK_RESEAL",
            "action": "ALERT",
            "reason": f"回封耗时{minutes_since_break:.0f}分钟或封单未递增→弱回封预警",
        }
    if minutes_since_break >= 20:
        return {
            "label": "SUPPORT_COLLAPSE",
            "action": "EXIT",
            "reason": f"{minutes_since_break:.0f}分钟无法回封→承接崩塌离场",
        }
    return {
        "label": "OBSERVE",
        "action": "WATCH",
        "reason": f"炸板{minutes_since_break:.0f}分钟未回封→生死线观察（15-20分钟窗口）",
    }


def detect_quant_seat_warning(quant_seat_ratio: float) -> dict:
    """龙虎榜量化席位双阈值预警（§3.11④，v1.8.0）：hard 70% 降权 30%+预警 / soft 58% 降权 15%。

    PIT 注意：本函数只判定占比，龙虎榜数据的 T-1 可见性由 §3.13#5 get_dragon_tiger_pit 保证。
    """
    if quant_seat_ratio > 0.70:
        return {
            "level": "HARD",
            "weight_discount": 0.30,
            "alert": True,
            "reason": f"量化席位{quant_seat_ratio:.0%}>70%→hard 降权30%+预警",
        }
    if quant_seat_ratio > 0.58:
        return {
            "level": "SOFT",
            "weight_discount": 0.15,
            "alert": False,
            "reason": f"量化席位{quant_seat_ratio:.0%}>58%→soft 降权15%",
        }
    return {
        "level": "NONE",
        "weight_discount": 0.0,
        "alert": False,
        "reason": f"量化席位{quant_seat_ratio:.0%}≤58%→正常",
    }
