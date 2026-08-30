# [BLUEPRINT] MOD-CMP-002 | docs/03_modules/_domain_compliance/discipline_prohibition_checker/blueprint.md
# [MODULE] zephyr.compliance.discipline_prohibition_checker
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + zephyr.compliance.compliance_log
# [CONSUMERS] C-004 风控引擎（订单提交前嵌入，43 号 §4.3）; MOD-PA-006 分批建仓（每批下单前过闸，41 号 §3.6）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 追高/补仓/报复=Hard Block；骄傲=Warning 不阻断；检测引擎失效=Fail-Closed 拒单；KillSwitchLite 仅策略级当日生效，失效升级全局 Kill Switch（RC-03）
# [MODIFY-GUARD] 43_compliance_discipline.md §4（BM-BUY-08-B）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DisciplineGuardError(ZA-CMP-0002)
# [TESTS] tests/compliance/test_discipline_prohibition_checker.py
# [TTL] permanent

"""



四项严禁自动化检测 + Kill Switch 轻量版（43_compliance_discipline §4，BM-BUY-08-B）。

订单提交前检测四类严禁交易行为——踏空追高 / 被套补仓 / 盈利骄傲 / 亏损报复。
41 号已定"命名 + Hard Block/Warning 定位"（§2.3/§3.1），本篇补检测阈值 +
检测算法 + Kill Switch 轻量版联动。阈值默认值与检测伪代码真源=43 号 §4.3
（chase_max_deviation=+2%/surge 30min+5%/补仓 -5%/骄傲 5 笔×1.5/报复 -2%×2.0×1.5；
追高与骄傲为 MVP 初始值待 C1 实盘校准），此处不重复表格。

Kill Switch 轻量版（§4.3）：仅停触发策略（当日禁止新开仓），次日自动复位 +
人工确认；失效 → 升级全局 Kill Switch（RC-03，35 号四级梯子）。

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: state_path 参数
#   fields: 参数 state_path（无注解）
#   code: discipline_prohibition_checker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: on_escalate 参数
#   fields: 参数 on_escalate（无注解）
#   code: discipline_prohibition_checker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: logger 参数
#   fields: 参数 logger（无注解）
#   code: discipline_prohibition_checker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① KillSwitchLite
#   name_en: KillSwitchLite
#   intro: 策略级轻量熔断（§4.3）：仅停触发策略，当日有效，次日自动复位。
#   desc: 策略级轻量熔断（§4.3）：仅停触发策略，当日有效，次日自动复位。 状态存储失效 → 升级全局 Kill Switch（on_escalate 回调，RC-03）。 state_…；公共方法（定义序）: trigger…
#   inputs: state_path on_escalate logger
#   outputs: 返回值
# - id: A2
#   name_zh: ② DisciplineGuard
#   name_en: DisciplineGuard
#   intro: 四项严禁检测引擎（D-COMPLIANCE-23 组件 B，嵌入 C-004 风控引擎）。
#   desc: 四项严禁检测引擎（D-COMPLIANCE-23 组件 B，嵌入 C-004 风控引擎）。 订单提交前调用（§4.3）：任一 Hard Block 命中即拒单；仅命中骄傲 → W…；公共方法（定义序）: check；源…
#   inputs: thresholds kill_switch logger
#   outputs: 返回值
#   （注：A2 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: KillSwitchLite, DisciplineGuard
#   downstream: C-004 风控引擎（订单提交前嵌入，43 号 §4.3）; MOD-PA-006 分批建仓（每批下单前过闸，41 号 §3.6）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import enum
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import MAIN_REPO_ROOT


class DisciplineGuardError(ZephyrBaseError):
    """纪律闸错误。"""

    error_code = "ZA-CMP-0002"


class ProhibitedBehavior(enum.Enum):
    """四类严禁行为。"""

    CHASING = "CHASING"  # 踏空追高
    ADDING_TO_LOSER = "ADDING_TO_LOSER"  # 被套补仓
    OVERCONFIDENCE = "OVERCONFIDENCE"  # 盈利骄傲
    REVENGE_TRADING = "REVENGE_TRADING"  # 亏损报复


class DisciplineAction(enum.Enum):
    """处置分级。"""

    PASS = "PASS"
    WARNING = "WARNING"
    HARD_BLOCK = "HARD_BLOCK"


@dataclass(frozen=True)
class DisciplineThresholds:
    """检测阈值（§4.3 默认值；chase_max_deviation/win_streak_n 为 MVP 初始值待校准）。"""

    chase_max_deviation: float = 0.02  # 追高：相对信号参考价最大追涨幅度
    surge_window_min: int = 30  # 追高：急剧拉升窗口（分钟）
    surge_threshold: float = 0.05  # 追高：窗口内涨幅阈值
    add_on_loss_threshold: float = -0.05  # 补仓：持仓浮亏阈值
    win_streak_n: int = 5  # 骄傲：连续盈利笔数
    risk_exposure_multiplier: float = 1.5  # 骄傲：风险敞口倍数
    revenge_loss_threshold: float = -0.02  # 报复：当日亏损阈值
    freq_multiplier: float = 2.0  # 报复：频率倍数（相对 20 日均值）
    size_multiplier: float = 1.5  # 报复：单笔规模倍数（相对 20 日均值）


@dataclass(frozen=True)
class OrderRequest:
    """待检测订单（最小契约）。"""

    symbol: str
    price: float
    strategy_id: str
    risk_exposure: float  # 本单风险敞口（占总资产比例）
    size: float  # 本单金额
    is_add: bool  # 是否对已有持仓同标的加仓


@dataclass(frozen=True)
class DisciplineContext:
    """检测上下文（§4.3：信号参考价/3秒Tick价/持仓盈亏/加仓记录/连续盈亏/当日盈亏/20日基线）。"""

    signal_ref_price: float | None  # 信号生成时价格（None=无信号锚，跳过追高检测）
    surge_30min_pct: float | None  # 近 30 分钟涨幅（小数）
    position_pnl_pct: float | None  # 该标的持仓浮盈（小数，无持仓=None）
    win_streak: int  # 连续盈利笔数
    normal_exposure: float  # 常规单笔风险敞口
    daily_pnl_pct: float  # 当日账户盈亏（小数）
    projected_daily_freq: float  # 当日预计下单频率（调用方按已过去交易时长外推）
    freq_baseline_20d: float  # 20 日交易频率基线
    size_baseline_20d: float  # 20 日单笔规模基线


@dataclass(frozen=True)
class DisciplineVerdict:
    """检测结论（不可变）。"""

    behavior: ProhibitedBehavior | None
    action: DisciplineAction
    detail: str
    kill_switch_triggered: bool = False


class KillSwitchLite:
    """策略级轻量熔断（§4.3）：仅停触发策略，当日有效，次日自动复位。

    状态存储失效 → 升级全局 Kill Switch（on_escalate 回调，RC-03）。
    state_path=None 时用默认生产路径（主仓锚定）。
    """

    def __init__(
        self,
        state_path: Path | None = None,
        on_escalate: Callable[[str, str], None] | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._path = state_path or (MAIN_REPO_ROOT / "data" / "compliance_log" / "kill_switch_lite_state.json")
        self._on_escalate = on_escalate
        self._logger = logger or ComplianceLogger()

    def trigger(self, strategy_id: str, reason: str, trade_date: date) -> bool:
        """触发熔断：strategy_id 当日禁止新开仓。返回是否成功落状态。

        状态存储失效 → 升级全局 Kill Switch（Fail-Closed，§4.3 降级链）。
        """
        state = self._load()
        if state is None:  # 状态不可读 → 升级全局
            self._escalate(strategy_id, f"状态不可读，升级全局 Kill Switch: {reason}")
            return False
        state[strategy_id] = {
            "reason": reason,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
            "expiry": trade_date.isoformat(),  # 当日收盘失效（次日自动复位）
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            self._escalate(strategy_id, f"状态写入失败，升级全局 Kill Switch: {reason}")
            return False
        self._logger.log(
            "KILL_SWITCH_LITE_TRIGGER",
            "discipline_prohibition_checker",
            {"strategy_id": strategy_id, "reason": reason, "expiry": trade_date.isoformat()},
        )
        return True

    def is_blocked(self, strategy_id: str, today: date) -> bool:
        """策略当日是否被熔断。状态不可读 → True（Fail-Closed 保守阻断）。"""
        state = self._load()
        if state is None:
            return True
        entry = state.get(strategy_id)
        if entry is None:
            return False
        return entry.get("expiry", "") >= today.isoformat()

    def reset(self, strategy_id: str) -> bool:
        """人工复位（当日违规已复盘确认后解除）。"""
        state = self._load()
        if state is None or strategy_id not in state:
            return False
        del state[strategy_id]
        self._path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        return True

    def _load(self) -> dict[str, Any] | None:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _escalate(self, strategy_id: str, reason: str) -> None:
        self._logger.log(
            "KILL_SWITCH_LITE_ESCALATE",
            "discipline_prohibition_checker",
            {"strategy_id": strategy_id, "reason": reason},
        )
        if self._on_escalate is not None:
            self._on_escalate(strategy_id, reason)


class DisciplineGuard:
    """四项严禁检测引擎（D-COMPLIANCE-23 组件 B，嵌入 C-004 风控引擎）。

    订单提交前调用（§4.3）：任一 Hard Block 命中即拒单；仅命中骄傲 → Warning
    不阻断；全过 → PASS。报复判定先于骄傲（Hard Block 优先于 Warning）。
    """

    def __init__(
        self,
        thresholds: DisciplineThresholds | None = None,
        kill_switch: KillSwitchLite | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._t = thresholds or DisciplineThresholds()
        self._ks = kill_switch
        self._logger = logger or ComplianceLogger()

    def check(self, order: OrderRequest, ctx: DisciplineContext) -> DisciplineVerdict:
        """订单提交前四项严禁检测，返回最高严重级结论。"""
        verdict = self._check_chasing(order, ctx)
        if verdict is not None:
            return verdict
        verdict = self._check_adding_to_loser(order, ctx)
        if verdict is not None:
            return verdict
        verdict = self._check_revenge(order, ctx)  # 先于骄傲（Hard Block 优先）
        if verdict is not None:
            return verdict
        verdict = self._check_overconfidence(order, ctx)
        if verdict is not None:
            return verdict
        return self._verdict(None, DisciplineAction.PASS, "四项严禁全过", order)

    def _check_chasing(self, order: OrderRequest, ctx: DisciplineContext) -> DisciplineVerdict | None:
        """踏空追高（Hard Block）：信号锚缺失时跳过（无锚不可判，留痕）。"""
        t = self._t
        _EPS = 1e-9  # 浮点尾差容差（恰达阈值不判违规，与"超阈值"语义一致）
        if ctx.signal_ref_price is None or ctx.surge_30min_pct is None:
            return None
        deviation = order.price / ctx.signal_ref_price - 1
        if deviation > t.chase_max_deviation + _EPS and ctx.surge_30min_pct > t.surge_threshold + _EPS:
            detail = (
                f"追涨幅度 {deviation:.2%} > {t.chase_max_deviation:.2%} 且"
                f"近{t.surge_window_min}min涨幅 {ctx.surge_30min_pct:.2%} > {t.surge_threshold:.2%}"
            )
            return self._verdict(ProhibitedBehavior.CHASING, DisciplineAction.HARD_BLOCK, detail, order)
        return None

    def _check_adding_to_loser(self, order: OrderRequest, ctx: DisciplineContext) -> DisciplineVerdict | None:
        """被套补仓（Hard Block）。"""
        t = self._t
        if order.is_add and ctx.position_pnl_pct is not None:
            if ctx.position_pnl_pct < t.add_on_loss_threshold:
                detail = f"持仓浮亏 {ctx.position_pnl_pct:.2%} < {t.add_on_loss_threshold:.2%} 仍加仓同标的"
                return self._verdict(ProhibitedBehavior.ADDING_TO_LOSER, DisciplineAction.HARD_BLOCK, detail, order)
        return None

    def _check_revenge(self, order: OrderRequest, ctx: DisciplineContext) -> DisciplineVerdict | None:
        """亏损报复（Hard Block + KillSwitchLite）。"""
        t = self._t
        if ctx.daily_pnl_pct >= t.revenge_loss_threshold:
            return None
        freq_abnormal = (
            ctx.freq_baseline_20d > 0 and ctx.projected_daily_freq > t.freq_multiplier * ctx.freq_baseline_20d
        )
        size_abnormal = ctx.size_baseline_20d > 0 and order.size > t.size_multiplier * ctx.size_baseline_20d
        if not (freq_abnormal or size_abnormal):
            return None
        ks_triggered = False
        if self._ks is not None:
            ks_triggered = self._ks.trigger(order.strategy_id, "REVENGE_TRADING", date.today())
        detail = (
            f"当日亏损 {ctx.daily_pnl_pct:.2%} < {t.revenge_loss_threshold:.2%} 且"
            f"频率异常={freq_abnormal}/规模异常={size_abnormal}"
        )
        return self._verdict(
            ProhibitedBehavior.REVENGE_TRADING,
            DisciplineAction.HARD_BLOCK,
            detail,
            order,
            kill_switch_triggered=ks_triggered,
        )

    def _check_overconfidence(self, order: OrderRequest, ctx: DisciplineContext) -> DisciplineVerdict | None:
        """盈利骄傲（Warning，不阻断）。"""
        t = self._t
        if (
            ctx.win_streak >= t.win_streak_n
            and ctx.normal_exposure > 0
            and order.risk_exposure > t.risk_exposure_multiplier * ctx.normal_exposure
        ):
            detail = (
                f"连续盈利 {ctx.win_streak} 笔 ≥ {t.win_streak_n} 且单笔风险敞口"
                f" {order.risk_exposure:.2%} > {t.risk_exposure_multiplier}×常规 {ctx.normal_exposure:.2%}"
            )
            return self._verdict(ProhibitedBehavior.OVERCONFIDENCE, DisciplineAction.WARNING, detail, order)
        return None

    def _verdict(
        self,
        behavior: ProhibitedBehavior | None,
        action: DisciplineAction,
        detail: str,
        order: OrderRequest,
        kill_switch_triggered: bool = False,
    ) -> DisciplineVerdict:
        verdict = DisciplineVerdict(
            behavior=behavior,
            action=action,
            detail=detail,
            kill_switch_triggered=kill_switch_triggered,
        )
        self._logger.log(
            "DISCIPLINE_VERDICT",
            "discipline_prohibition_checker",
            {
                "behavior": behavior.value if behavior else None,
                "action": action.value,
                "detail": detail,
                "symbol": order.symbol,
                "strategy_id": order.strategy_id,
                "kill_switch_triggered": kill_switch_triggered,
            },
        )
        return verdict
