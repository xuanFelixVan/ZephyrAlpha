# [BLUEPRINT] MOD-SIG-139 | docs/03_modules/_domain_signal/pool_tier_maintenance/blueprint.md
# [MODULE] zephyr.signal_ashare.core.pool_tier_maintenance
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数状态机核，零 IO；日产出达标集与池存量由调用方注入）
# [CONSUMERS] TDM-E-L3-09（股票池分层维护）；TDM-E-L3-08 候选池输出（Tier 标签消费，待接线）；TDM-E-L3-02 九阶段主链（T1 直通消费，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 升降级规则封闭：连续 2 日达标升一档（T1 封顶）/连续 5 日不达标降一档（T3 再降=剔除）/10 日陈旧剔除; 升降级后连击清零（防连跳）; 同码重复条目/未知档位→PoolTierInputError（fail-closed）; 陈旧与降级同日触发按降级优先（一次一事，结果 notes 留痕）; 输出按 (tier,code) 确定序; 无墙钟（as_of 仅审计透传）; 阈值=节点真源（2/5/10），proposed 待实盘标定
# [MODIFY-GUARD] 地图节点 TDM-E-L3-09
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 条目重复/档位非法/连击计数负值 → PoolTierInputError（fail-closed）
# [TESTS] tests/signal_ashare/test_pool_tier_maintenance.py
# [TTL] permanent
"""PoolTierMaintenance — 股票池三层就绪度分层维护（MOD-SIG-139，TDM-E-L3-09）。

节点语义（TDM-E-L3-09 algo_note 逐条对码）：
    持久池分层维护：Tier1（当日精选）/Tier2（观察池）/Tier3（备选池）。
    日产出更新各 Tier：连续 2 日达标升 Tier、5 日不达标降级、10 日陈旧剔除。
    防止每天从零重扫。

与 L3-03 双池正交——双池按风格（短线/波段）、Tier 按就绪度（晨审引 D29 注释）。
晨审 st-tdm-review-20260911 §7.1 定性"查无现成模块"→立 C 类候选；Owner 2026-09-11
夜班令"除币圈外开工"立项本件。

池成员状态存储：本件为纯函数状态机（entries 进、entries 出），持久化由调用方落
治理状态表/新 DS（外审 M-41 欠账，待登记施工）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Final, Iterable


class PoolTier(IntEnum):
    """就绪度三层（数值越小越靠前，用于排序与升降档算术）。"""

    TIER1 = 1  # 当日精选
    TIER2 = 2  # 观察池
    TIER3 = 3  # 备选池


#: 连续达标天数达此值升一档（节点真源：连续 2 日达标升 Tier）
PROMOTE_STREAK_DAYS: Final = 2
#: 连续不达标天数达此值降一档（节点真源：5 日不达标降级）
DEMOTE_STREAK_DAYS: Final = 5
#: 陈旧天数达此值剔除（节点真源：10 日陈旧剔除）
STALE_PURGE_DAYS: Final = 10


class PoolTierInputError(ValueError):
    """输入非法（同码重复条目/未知档位/负计数）——fail-closed。"""


@dataclass(frozen=True)
class PoolEntry:
    """池内单标的就绪度状态（frozen；日更由 update_pool_tiers 产出新版）。"""

    stock_code: str
    tier: PoolTier
    consecutive_qualify_days: int = 0  # 连续达标天数（进漏斗日产出达标集）
    consecutive_miss_days: int = 0  # 连续不达标天数
    stale_days: int = 0  # 陈旧天数（持续无产出贡献）


@dataclass(frozen=True)
class PoolUpdateResult:
    """日更结果（新池快照+三类变动清单，审计友好）。"""

    as_of: str  # 审计透传（调用方交易日，本件不校验日历）
    entries: tuple[PoolEntry, ...]  # 新池快照（按 (tier, code) 确定序）
    promoted: tuple[str, ...]  # 升档代码（确定序）
    demoted: tuple[str, ...]  # 降档代码（确定序）
    purged: tuple[tuple[str, str], ...]  # (代码, 原因) 剔除清单（确定序）

    def to_dict(self) -> dict:
        """全基本类型字典（JSON 可序列化）。"""
        return {
            "as_of": self.as_of,
            "entries": [e.__dict__ | {"tier": int(e.tier)} for e in self.entries],
            "promoted": list(self.promoted),
            "demoted": list(self.demoted),
            "purged": [list(p) for p in self.purged],
        }


def admit(stock_code: str) -> PoolEntry:
    """新标的入池工厂：TIER3 备选档起步，连击清零。"""
    if not stock_code:
        raise PoolTierInputError("stock_code 为空")
    return PoolEntry(stock_code=stock_code, tier=PoolTier.TIER3)


def update_pool_tiers(
    entries: Iterable[PoolEntry],
    qualified_codes: Iterable[str],
    as_of: str,
) -> PoolUpdateResult:
    """日更主入口：漏斗日产出达标集 × 池存量 → 升/降/剔后新池。

    Args:
        entries: 现有池条目（顺序不限；同码重复=fail-closed）。
        qualified_codes: 当日漏斗产出达标代码集（重复无害）。
        as_of: 交易日标签（仅审计透传，本件无墙钟）。

    Returns:
        PoolUpdateResult（frozen；entries 按 (tier, code) 升序）。

    Raises:
        PoolTierInputError: 同码重复/档位非法/负计数。
    """
    by_code: dict[str, PoolEntry] = {}
    for e in entries:
        if not isinstance(e.tier, PoolTier):
            raise PoolTierInputError(f"{e.stock_code} 档位非法: {e.tier!r}")
        if e.consecutive_qualify_days < 0 or e.consecutive_miss_days < 0 or e.stale_days < 0:
            raise PoolTierInputError(f"{e.stock_code} 计数为负")
        if e.stock_code in by_code:
            raise PoolTierInputError(f"同码重复条目: {e.stock_code}")
        by_code[e.stock_code] = e

    qualified = set(qualified_codes)
    promoted: list[str] = []
    demoted: list[str] = []
    purged: list[tuple[str, str]] = []
    new_entries: list[PoolEntry] = []

    for code in sorted(by_code):
        e = by_code[code]
        if code in qualified:
            cq = e.consecutive_qualify_days + 1
            tier = e.tier
            if cq >= PROMOTE_STREAK_DAYS and tier > PoolTier.TIER1:
                tier = PoolTier(tier - 1)
                cq = 0  # 升档后连击清零（防连跳）
                promoted.append(code)
            new_entries.append(PoolEntry(code, tier, cq, 0, 0))
        else:
            cm = e.consecutive_miss_days + 1
            stale = e.stale_days + 1
            tier = e.tier
            if cm >= DEMOTE_STREAK_DAYS:
                if tier >= PoolTier.TIER3:
                    purged.append((code, f"T3 连续 {cm} 日不达标降无可降"))
                    continue
                tier = PoolTier(tier + 1)
                demoted.append(code)
                cm = 0  # 降档后连击清零
                new_entries.append(PoolEntry(code, tier, 0, cm, stale))
                continue
            if stale >= STALE_PURGE_DAYS:
                purged.append((code, f"陈旧 {stale} 日无产出贡献"))
                continue
            new_entries.append(PoolEntry(code, tier, 0, cm, stale))

    return PoolUpdateResult(
        as_of=as_of,
        entries=tuple(sorted(new_entries, key=lambda x: (x.tier, x.stock_code))),
        promoted=tuple(sorted(promoted)),
        demoted=tuple(sorted(demoted)),
        purged=tuple(sorted(purged)),
    )
