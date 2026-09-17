# [BLUEPRINT] MOD-SIG-137 | docs/03_modules/_domain_fundamental_signal/negative_veto/blueprint.md
# [MODULE] zephyr.signal_fundamental.negative_veto
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] 无（纯函数核，零 IO；负面事实由调用方从事件源/基本面库算好注入）
# [CONSUMERS] TDM-E-L3-04（负面否决器，STR-MULTIFACTOR-034~041 规则承载）；候选池漏斗 BM-SEL 族（待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 六项负面清单一票否决（业绩暴雷/立案调查/大股东减持/解禁>5% 流通盘/商誉减值风险/配股圈钱）+黑名单; 命中任一即 vetoed=True（负面清单优先级高于一切加分项）; 不短路——返回全部命中原因（可审计）; 解禁阈值默认 5% 流通盘 config 可调; 事实缺失(None)不算命中（证据不足不否决，由上游数据完整性负责）; 同输入必同输出(frozen)
# [MODIFY-GUARD] 地图节点 TDM-E-L3-04 + 策略库 STR-MULTIFACTOR-034~041
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 解禁比例/商誉比率越界 → NegativeVetoError（fail-closed）
# [TESTS] tests/signal_fundamental/test_negative_veto.py
# [TTL] permanent
"""NegativeVeto — 候选池负面否决器（MOD-SIG-137，TDM-E-L3-04）。

节点语义逐条吸收（真源=TDM-E-L3-04 algo_note）：
一票否决清单——业绩暴雷（预告亏损）/立案调查/大股东减持公告/解禁>5% 流通盘/
商誉减值风险/配股圈钱。命中任一条直接出池，不管打分多高——**负面清单优先级
高于一切加分项**。

设计原则：
- 否决器只认"已发生/已公告的负面事实"（调用方注入），不做预测不做灰度推断；
- 证据不足（None）不否决——宁可漏放由打分池兜底，不可凭空否决（与风控层
  fail-closed 方向相反：本件是筛选漏斗不是下单闸）；
- 全量披露命中原因（不短路），供漏斗日志与复盘。

查重分工（蓝图 §1）：risk_veto_engine（MOD-RK-24）=订单级下单硬否决（限额/
停牌/T+1，安全 H，fail-closed）；strategy_cross_vote_funnel=市场状态否决门
（allow_buy 布尔）；本件=**候选池筛选层**的负面清单一票否决（个股基本面/事件
维度），三者在漏斗不同层，语义正交。
"""

from __future__ import annotations

from dataclasses import dataclass

_UNLOCK_RATIO_DEFAULT = 0.05  # 解禁 >5% 流通盘（节点口径）


class NegativeVetoError(ValueError):
    """非法输入（fail-closed）：比例越界。"""


@dataclass(frozen=True)
class NegativeVetoConfig:
    """否决阈值（解禁比例为唯一数值阈值，其余为事实布尔）。"""

    unlock_ratio_threshold: float = _UNLOCK_RATIO_DEFAULT

    def __post_init__(self) -> None:
        if not (0.0 < self.unlock_ratio_threshold <= 1.0):
            raise NegativeVetoError(
                f"unlock_ratio_threshold 须 ∈ (0,1]: {self.unlock_ratio_threshold}"
            )


@dataclass(frozen=True)
class NegativeFacts:
    """候选股负面事实快照（None=该维度暂无数据，不参与判定）。"""

    earnings_forecast_loss: bool | None = None  # 业绩暴雷（预告亏损）
    under_investigation: bool | None = None  # 立案调查
    major_shareholder_reduction_pending: bool | None = None  # 大股东减持公告
    unlock_ratio: float | None = None  # 待解禁市值 / 流通盘
    goodwill_impairment_risk: bool | None = None  # 商誉减值风险（上游模型判定）
    rights_issue_pending: bool | None = None  # 配股圈钱
    blacklisted: bool | None = None  # 黑名单（Owner/风控维护）
    high_accrual: bool | None = None  # 高应计（Sloan 剔除器，fundamentals.accrual_negative_screen 产出；裁定#231）

    def __post_init__(self) -> None:
        for name in ("unlock_ratio",):
            v = getattr(self, name)
            if v is not None and (v != v or v < 0.0 or v > 1.0):
                raise NegativeVetoError(f"{name} 越界 [0,1]: {v}")


@dataclass(frozen=True)
class NegativeVetoVerdict:
    """否决裁决（frozen，全量披露命中原因）。"""

    vetoed: bool
    reasons: tuple[str, ...]  # 全部命中项（可审计）；未否决为空元组


_REASON_KEYS = (
    ("earnings_forecast_loss", "业绩暴雷（预告亏损）"),
    ("under_investigation", "立案调查"),
    ("major_shareholder_reduction_pending", "大股东减持公告"),
    ("goodwill_impairment_risk", "商誉减值风险"),
    ("rights_issue_pending", "配股圈钱"),
    ("blacklisted", "黑名单"),
    ("high_accrual", "高应计（Sloan 盈余质量差）"),
)


def apply_negative_veto(
    facts: NegativeFacts, config: NegativeVetoConfig | None = None
) -> NegativeVetoVerdict:
    """负面清单一票否决（纯函数，同输入必同输出）。

    命中任一项 → vetoed=True 并披露全部命中原因；证据缺失（None）不否决。
    """
    cfg = config or NegativeVetoConfig()
    reasons: list[str] = []
    for attr, label in _REASON_KEYS:
        v = getattr(facts, attr)
        if v is True:
            reasons.append(label)
    if facts.unlock_ratio is not None and facts.unlock_ratio > cfg.unlock_ratio_threshold:
        reasons.append(f"解禁 {facts.unlock_ratio:.1%} > 阈值 {cfg.unlock_ratio_threshold:.0%}")
    return NegativeVetoVerdict(vetoed=bool(reasons), reasons=tuple(reasons))
