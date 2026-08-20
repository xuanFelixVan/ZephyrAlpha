# [BLUEPRINT] MOD-CMP-001 | docs/03_modules/_domain_compliance/discipline_must_do_checker/blueprint.md
# [MODULE] zephyr.compliance.discipline_must_do_checker
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + zephyr.compliance.compliance_log
# [CONSUMERS] C-004 风控引擎（盘中执行项 Pre-Trade 嵌入，43 号 §3.4）; 盘前/盘后/晚间工作流编排
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 必做清单是纪律辅助非阻断（仅盘中执行项 Hard Block）; 超时处置方向一律"更保守"; 检测失效降级人工 checklist（盘中项失效按 Fail-Closed 拒单）
# [MODIFY-GUARD] 43_compliance_discipline.md §3（BM-BUY-08-A）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ChecklistCheckerError(ZA-CMP-0001)
# [TESTS] tests/compliance/test_discipline_must_do_checker.py
# [TTL] permanent

"""四项必做清单完成度检测（43_compliance_discipline §3，BM-BUY-08-A）。

交易日 4 个关键时点（盘前/盘中/盘后/晚间）自动检测四项必做清单完成度，
是操作合规的"自律层"——防"AI 全自动跑、人不复盘"的纪律衰减。

裁定（§3.2）：MVP 轻量检查器，4 时点 cron 语义由调用方触发，本模块只做
"完成度判定 + 处置分级"；必做是纪律辅助非阻断（盘中执行除外，Hard Block）。

四时点清单（§3.3，deadline 为本篇裁定值）：
  | 时点     | 必做内容                                  | 截止/检测时机            | 未完成动作          |
  |---------|------------------------------------------|-------------------------|--------------------|
  | 盘前复核 | 前日复盘摘要+今日计划+风险检查清单          | 08:00 前完成；08:00 检测  | Warning 推送        |
  | 盘中执行 | 策略信号合规检查+风控参数确认+仓位限额验证    | 实时（订单提交前）         | Hard Block（唯一）  |
  | 盘后复盘 | 当日决策回顾+偏差分析+纪律自评              | 收盘后至次日开盘前         | 次日开盘前 Warning  |
  | 晚间分析 | 收盘数据归档+明日策略+风险预判              | 当晚至次日盘前             | 次日盘前 Warning    |

完成度信号来源（§3.3）：复盘报告生成状态 / 分析任务提交状态 / C-004 风控参数
确认位——本模块通过注入的 ``completion_provider`` 消费，不侵入复盘/分析模块
内部逻辑（§3.4）。

Version: 1.0.0
"""

from __future__ import annotations

import enum
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.shared.foundation.errors import ZephyrBaseError


class ChecklistCheckerError(ZephyrBaseError):
    """必做清单检查器错误。"""

    error_code = "ZA-CMP-0001"


class ChecklistCheckpoint(enum.Enum):
    """四时点。"""

    PRE_MARKET = "PRE_MARKET"  # 盘前复核
    INTRADAY = "INTRADAY"  # 盘中执行（唯一 Hard Block 项）
    POST_MARKET = "POST_MARKET"  # 盘后复盘
    EVENING = "EVENING"  # 晚间分析


class ChecklistAction(enum.Enum):
    """处置动作。"""

    NONE = "NONE"  # 已完成，无动作
    WARNING = "WARNING"  # 推送提醒，不阻断
    HARD_BLOCK = "HARD_BLOCK"  # 阻断（仅盘中执行）


# 四时点必做内容（§3.3 表格真源，item key 稳定标识）
REQUIRED_ITEMS: dict[ChecklistCheckpoint, tuple[str, ...]] = {
    ChecklistCheckpoint.PRE_MARKET: ("prev_day_review", "today_plan", "risk_checklist"),
    ChecklistCheckpoint.INTRADAY: ("signal_compliance_check", "risk_param_confirm", "position_limit_verify"),
    ChecklistCheckpoint.POST_MARKET: ("decision_review", "deviation_analysis", "discipline_self_assessment"),
    ChecklistCheckpoint.EVENING: ("close_data_archive", "tomorrow_strategy", "risk_forecast"),
}

# 截止时间裁定值（§3.3 参数默认值）：盘后/晚间跨日，用"次日"时间表达
_DEADLINES: dict[ChecklistCheckpoint, time] = {
    ChecklistCheckpoint.PRE_MARKET: time(8, 0),  # 当日 08:00
    ChecklistCheckpoint.POST_MARKET: time(9, 15),  # 次日 09:15（开盘前）
    ChecklistCheckpoint.EVENING: time(8, 0),  # 次日 08:00（盘前）
}


@dataclass(frozen=True)
class ChecklistVerdict:
    """完成度判定结果（不可变）。"""

    checkpoint: ChecklistCheckpoint
    complete: bool
    missing_items: tuple[str, ...]
    action: ChecklistAction
    checked_at: datetime
    detail: str = ""


# 完成度信号提供者：入参 (checkpoint, trade_date)，返回当日已完成 item key 集合
CompletionProvider = Callable[[ChecklistCheckpoint, date], set[str]]


class ChecklistCompletionChecker:
    """四项必做清单完成度检查器（D-COMPLIANCE-23 组件 A）。

    Args:
        completion_provider: 完成度信号源（工作流 artifact 存在性抽象）。
        logger: 合规日志；None 时新建默认路径实例。
        pre_market_deadline / post_market_deadline / evening_deadline:
            截止时间覆盖（默认取 §3.3 裁定值）。
    """

    def __init__(
        self,
        completion_provider: CompletionProvider,
        logger: ComplianceLogger | None = None,
        *,
        pre_market_deadline: time = time(8, 0),
        post_market_deadline: time = time(9, 15),
        evening_deadline: time = time(8, 0),
    ) -> None:
        self._provider = completion_provider
        self._logger = logger or ComplianceLogger()
        self._deadlines = {
            ChecklistCheckpoint.PRE_MARKET: pre_market_deadline,
            ChecklistCheckpoint.POST_MARKET: post_market_deadline,
            ChecklistCheckpoint.EVENING: evening_deadline,
        }

    def check_checkpoint(
        self,
        checkpoint: ChecklistCheckpoint,
        now: datetime,
        trade_date: date | None = None,
    ) -> ChecklistVerdict:
        """检测某时点必做清单完成度。

        判定规则：
        - 全部完成 → action=NONE
        - 盘中执行（INTRADAY）：实时检查，任一缺失 → HARD_BLOCK
          （四时点中唯一阻断项，§3.3）
        - 其余时点：仅当 now 超过截止时间且仍有缺失 → WARNING
          （截止前缺失不算违规，属于正常进行中）

        Args:
            checkpoint: 时点。
            now: 检测时刻。
            trade_date: 清单所属交易日（工件按此日期取）；None=now.date()。
                盘后/晚间清单"次日开盘前"检测时，调用方应传前一交易日。
        """
        td = trade_date or now.date()
        try:
            completed = set(self._provider(checkpoint, td))
        except Exception as exc:  # noqa: BLE001 — 信号源失效类型不可枚举，Fail-Closed 降级必须全捕获
            # 降级（§3.3）：检测失效 → 降级人工 checklist 不阻断；
            # 盘中执行项失效按 Fail-Closed 拒单（§1.3 铁律）
            if checkpoint is ChecklistCheckpoint.INTRADAY:
                verdict = ChecklistVerdict(
                    checkpoint=checkpoint,
                    complete=False,
                    missing_items=REQUIRED_ITEMS[checkpoint],
                    action=ChecklistAction.HARD_BLOCK,
                    checked_at=now,
                    detail=f"完成度信号源失效，Fail-Closed 拒单: {exc}",
                )
                self._log(verdict)
                return verdict
            verdict = ChecklistVerdict(
                checkpoint=checkpoint,
                complete=False,
                missing_items=REQUIRED_ITEMS[checkpoint],
                action=ChecklistAction.WARNING,
                checked_at=now,
                detail=f"完成度信号源失效，降级人工 checklist: {exc}",
            )
            self._log(verdict)
            return verdict

        missing = tuple(k for k in REQUIRED_ITEMS[checkpoint] if k not in completed)
        if not missing:
            verdict = ChecklistVerdict(
                checkpoint=checkpoint,
                complete=True,
                missing_items=(),
                action=ChecklistAction.NONE,
                checked_at=now,
            )
            self._log(verdict)
            return verdict

        if checkpoint is ChecklistCheckpoint.INTRADAY:
            action = ChecklistAction.HARD_BLOCK
            detail = "盘中执行项缺失，Hard Block"
        elif self._is_overdue(checkpoint, now, td):
            action = ChecklistAction.WARNING
            detail = "超时未完成，Warning 推送（纪律辅助非阻断）"
        else:
            action = ChecklistAction.NONE
            detail = "截止前正常进行中"
        verdict = ChecklistVerdict(
            checkpoint=checkpoint,
            complete=False,
            missing_items=missing,
            action=action,
            checked_at=now,
            detail=detail,
        )
        self._log(verdict)
        return verdict

    def _is_overdue(self, checkpoint: ChecklistCheckpoint, now: datetime, td: date) -> bool:
        """是否超截止时间。

        盘前复核：截止 = 当日 deadline（08:00）；
        盘后复盘/晚间分析：截止 = 次日 deadline（09:15 / 08:00，跨日语义）。
        """
        deadline = self._deadlines.get(checkpoint)
        if deadline is None:
            return False  # INTRADAY 无 deadline（实时）
        day = td if checkpoint is ChecklistCheckpoint.PRE_MARKET else td + timedelta(days=1)
        return now > datetime.combine(day, deadline, tzinfo=now.tzinfo)

    def _log(self, verdict: ChecklistVerdict) -> None:
        self._logger.log(
            "CHECKLIST_VERDICT",
            "discipline_must_do_checker",
            {
                "checkpoint": verdict.checkpoint.value,
                "complete": verdict.complete,
                "missing_items": list(verdict.missing_items),
                "action": verdict.action.value,
                "detail": verdict.detail,
            },
            now=verdict.checked_at,
        )
