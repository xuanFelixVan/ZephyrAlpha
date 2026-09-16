# [BLUEPRINT] MOD-AUTO-L6-001(暂编号) | docs/_working/automation/campaign/blueprints/risk_redline_blueprint.md | §
# [MODULE] zephyr.ex_sor.risk_redline
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] stdlib（dataclasses/datetime）
# [CONSUMERS] 实盘监控执行器（施工待实盘开通）; rl_exec_boundary（同域，语义对齐）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯函数引擎（零 IO 零时钟读取——时间由调用方注入）;
#   红线动作三档：YELLOW 减半仓观察 / RED 清仓冻结 / GRACE 黑天鹅缓冲（仅市场性暴跌，regime 门仲裁由调用方注入）;
#   熔断（4h 级）≠下架判据（日内噪音不够格动整装）;
#   阈值默认值=骨架 §9 v0 草案，生产前须按各组合回测分布校准并经标准库 freeze
# [MODIFY-GUARD] 阈值变更须同步 config/standards.yaml STD-LIVE-REDLINE-001
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入空序列→空动作列表; 日期乱序→按日期排序后处理
# [TESTS] tests/ex_sor/test_risk_redline.py
# [A_module] module_id=MOD-AUTO-L6-001 | layer=library | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
"""risk_redline — 实盘红线分级引擎 v0（骨架 v1.1 §9 的规则执行纯函数）。

输入：组合日度记录序列 [{date, pnl_pct}]（可带黑天鹅标记）+ 配置 + 回测基准。
输出：按日触发的动作列表（YELLOW/RED/GRACE/HALT-RESPECT），供执行器消费。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RedlineConfig:
    daily_yellow: float = 0.02      # 单日回撤黄线：减半仓+归因
    daily_red: float = 0.04         # 单日红线：清仓冻结（或超回测最差日 2 倍）
    weekly_red: float = 0.05        # 周红线
    monthly_red: float = 0.10       # 月红线
    backtest_worst_day_multiple: float = 2.0  # 超"回测历史最大单日亏损"倍数=红线
    blackswan_grace_days: int = 2   # 市场性暴跌观察窗（regime 门仲裁后由调用方标记）


@dataclass
class DayRecord:
    date: str            # YYYY-MM-DD
    pnl_pct: float       # 当日组合收益（负=亏损，0.03=+3%）
    market_crash: bool = False   # L1 regime 门仲裁：当日为市场性暴跌（β 非 α）


@dataclass
class Action:
    date: str
    level: str           # YELLOW / RED / GRACE / GRACE_EXPIRED
    rule: str
    detail: str


def _date_key(d: str) -> str:
    """日期排序键：尽力归一为 ISO（容非补零），失败回退原串。"""
    try:
        from datetime import date as _d

        y, m, dd = (int(x) for x in str(d).split("-"))
        return _d(y, m, dd).isoformat()
    except (ValueError, TypeError):
        return str(d)


def _iso_week(d: str) -> str:
    from datetime import date as _d

    y, m, dd = (int(x) for x in d.split("-"))
    iso = _d(y, m, dd).isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _month(d: str) -> str:
    return d[:7]


def evaluate(records: list[DayRecord], config: RedlineConfig = RedlineConfig(),
             backtest_worst_day: float | None = None) -> list[Action]:
    """逐日评估红线。周/月线先于日线判定且带闩锁（一次触发不重复）；返回动作列表（时间升序）。

    红队修复记录（2026-09-17）：①周/月线此前被日线 continue 吞掉 ②backtest_worst_day=0 误伤平盘日
    ③周月线无闩锁重复触发 ④日期排序未归一 ⑤GRACE 文案与实际保护窗不符。
    """
    actions: list[Action] = []
    recs = sorted(records, key=lambda r: _date_key(r.date))
    grace_used = 0
    grace_open = False
    grace_start: str | None = None
    grace_episode_done = False  # 本轮崩盘 episode 的缓冲窗已耗尽（不再重开，直到出现非红线日）
    week_fired: set[str] = set()
    month_fired: set[str] = set()
    week_pnl: dict[str, float] = {}
    month_pnl: dict[str, float] = {}
    wt_mult = config.backtest_worst_day_multiple if (backtest_worst_day or 0) > 0 else None
    wt_effective = backtest_worst_day * wt_mult if wt_mult else None

    for r in recs:
        dkey = _date_key(r.date)
        loss = -r.pnl_pct  # 正值=回撤
        wk, mo = _iso_week(dkey), _month(dkey)
        week_pnl[wk] = week_pnl.get(wk, 0.0) + r.pnl_pct
        month_pnl[mo] = month_pnl.get(mo, 0.0) + r.pnl_pct

        daily_red_hit = loss >= config.daily_red or (
            wt_effective is not None and loss >= wt_effective)
        yellow_hit = loss >= config.daily_yellow
        if not daily_red_hit:
            grace_episode_done = False  # 出现非红线日=episode 结束，缓冲窗可对新 episode 重新武装

        # 黑天鹅缓冲窗状态机（计数按记录数）
        if grace_open and grace_start is not None and dkey > _date_key(grace_start):
            grace_used += 1
            if grace_used >= config.blackswan_grace_days:
                grace_open = False
                grace_episode_done = True  # 观察窗耗尽：同 episode 不再重开

        # 开窗判定先于周/月评估——首日即崩的场景，窗当日就要开（否则周线会抢跑"清仓冻结"）
        grace_opened_today = False
        if daily_red_hit and r.market_crash and not grace_open and not grace_episode_done:
            grace_open = True
            grace_start = dkey
            grace_used = 0
            grace_opened_today = True

        # 周/月红线评估：闩锁防重复；缓冲窗开启期间挂起（观察窗与"清仓冻结"不并施），
        # 窗闭当日若 breach 仍在→立即升级（黑天鹅修复则自动消解）
        weekly_breach = -week_pnl[wk] >= config.weekly_red
        monthly_breach = -month_pnl[mo] >= config.monthly_red
        if not grace_open:
            if weekly_breach and wk not in week_fired:
                week_fired.add(wk)
                actions.append(Action(dkey, "RED", "weekly_red",
                                      f"周累计 {-week_pnl[wk]:.2%} ≥ {config.weekly_red:.0%}：清仓冻结"))
            if monthly_breach and mo not in month_fired:
                month_fired.add(mo)
                actions.append(Action(dkey, "RED", "monthly_red",
                                      f"月累计 {-month_pnl[mo]:.2%} ≥ {config.monthly_red:.0%}：清仓冻结"))

        # 日线动作
        if daily_red_hit:
            if grace_open:
                detail = ("市场性暴跌（β），开放至多 "
                          f"{config.blackswan_grace_days} 个交易日观察窗，暂缓清仓" if grace_opened_today
                          else "观察窗内：暂缓红线动作（不补仓，只观察）")
                actions.append(Action(dkey, "GRACE", "blackswan_buffer", detail))
                continue
            actions.append(Action(dkey, "RED", "daily_red",
                                  f"单日回撤 {loss:.2%} ≥ {config.daily_red:.0%}"
                                  + (f" 或超回测最差日 {config.backtest_worst_day_multiple}x" if wt_effective is not None else "")
                                  + "：清仓冻结待查"))
            continue
        if yellow_hit:
            actions.append(Action(dkey, "YELLOW", "daily_yellow",
                                  f"单日回撤 {loss:.2%} ≥ {config.daily_yellow:.0%}：减半仓+当日归因"))
    return actions


if __name__ == "__main__":
    pass
