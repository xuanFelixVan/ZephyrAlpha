# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.programmatic_trading_guard
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] ex_core.trading_session ; ex_core.adapters.miniqmt_broker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 实盘+未报备=拒下单; 报备信息变更需重新报备; PAPER/SIMULATION豁免; 启动+下单双校验; CheckResult不可变
# [MODIFY-GUARD] 40_execution_broker.md §决策⑱
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProgrammaticTradingGuardError(ZA-EX-0010)
# [TESTS] tests/ex_core/test_programmatic_trading_guard.py
# [TTL] permanent

"""

程序化交易报备合规守卫（40_execution_broker §决策⑱ gap 18 施工）。

实盘生存项——"未报备就上实盘"是合规硬违规。2025-07-07《证券市场程序化交易管理
实施细则》正式实施，明确程序化交易必须事前报备（策略/算法/服务器/风控），
未报备限制交易。本模块为实盘下单前置硬校验开关。

报备范围（§决策⑱）：
  | 报备项            | 内容                                              |
  |------------------|---------------------------------------------------|
  | 策略名称/标识      | 策略ID + 策略类别（多因子/打板/事件驱动等）         |
  | 算法类型           | TWAP/VWAP/IS/POV/市价 等                          |
  | 服务器位置         | 物理位置 + IP + 是否托管于券商机房                 |
  | 风控规则版本       | 风控配置 hash + max_single_order_pct 等关键阈值    |
  | 交易参数           | 报备时点全账户日最大下单笔数/撤单率上限             |

校验时机：
  - **启动校验**（TradingSession.start）：实盘 broker + 未报备 → 拒绝启动
  - **下单校验**（每笔 submit_order 前置）：双保险，防绕过 start 直连 broker

豁免规则：
  - PAPER（回测/纸面）：不接实盘券商，豁免
  - SIMULATION（模拟盘）：模拟 broker_id，豁免
  - LIVE（实盘）：必须校验

为何下单前再校验一次：start 到 submit 之间可能存在配置热更新或人为修改，
下单前再校验是"双保险"——风控红线不依赖单点。

报备信息变更检测：
  - 报备时记录风控配置 hash（hash_risk_config）
  - 启动时若当前风控配置 hash ≠ 报备时 hash → 触发"配置漂移"警告并视为未报备
  - 强制重新报备（record_registration）后才能恢复交易

依据：40_execution_broker.md v2.4.0 §决策⑱
      《证券市场程序化交易管理实施细则》（2025-07-07 实施）
      中基协私募委员会 2026-07 权威解读

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 守卫配置 ProgrammaticTradingGuardConfig
#   fields: mode(PAPER/SIMULATION/LIVE) / live_broker_ids / enforce_on_start / enforce_on_submit / allow_drift_warning_only
#   code: ProgrammaticTradingGuardConfig L194
# - id: I2
#   name: 报备信息 RegistrationInfo 入参
#   fields: registration_id / strategy_id / algorithm_types / server_location / risk_config_hash / max_total_orders_per_day / cancel_rate_limit
#   code: record_registration L331
# - id: I3
#   name: 当前风控配置 dict（运行时查询）
#   fields: max_single_order_pct / max_symbol_orders_per_day / max_total_orders_per_day / cancel_rate_limit
#   code: risk_config_provider() L265
# - id: I4
#   name: 券商标识 broker_id 字符串
#   fields: 如 miniqmt（启动/下单校验对象）
#   code: check_can_trade(broker_id) L413
# 层: 算法
# - id: A1
#   name_zh: ① 风控配置哈希
#   name_en: hash_risk_config
#   intro: 把4项关键风控阈值拼成串算SHA-256，得到稳定可比对的指纹
#   desc: 4项阈值格式化后按 key 字典序拼接 → SHA-256 → 64字符 hex；extra 项可扩展
#   inputs: I3
#   outputs: 风控配置 hash（64字符hex）
#   code: hash_risk_config L221
# - id: A2
#   name_zh: ② 报备信息登记
#   name_en: record_registration
#   intro: 记录一次券商报备，生成不可变快照，旧的留审计历史
#   desc: 参数合法性校验（id非空/笔数>0/撤单率∈(0,1]/算法列表非空）→ 生成 RegistrationInfo；重复调用旧实例入 _registration_history
#   inputs: I2
#   outputs: RegistrationInfo 不可变快照
#   invariant: 报备信息变更需重新报备
# - id: A3
#   name_zh: ③ 配置漂移检测
#   name_en: _detect_config_drift
#   intro: 重算当前风控hash与报备时hash比对，不一致视为报备失效
#   desc: 调 risk_config_provider 取当前配置 → hash_risk_config 重算 → 与报备 risk_config_hash 比对；未配置provider/未报备/查询异常 → None（保守放行）
#   inputs: A1 A2
#   outputs: 当前hash（漂移时）或 None
#   invariant: 查询失败保守放行不阻断交易
# - id: A4
#   name_zh: ④ 五规则合规校验
#   name_en: check_can_trade
#   intro: 按优先级过5条规则：非实盘豁免、白名单、未报备、漂移、放行
#   desc: 非LIVE→ALLOWED豁免 → broker不在live_broker_ids→BLOCKED_LIVE_BROKER保守拒 → 未报备→BLOCKED_UNREGISTERED → 漂移→BLOCKED_CONFIG_DRIFT（可配仅告警） → 全过→ALLOWED
#   inputs: I1 I4 A2 A3
#   outputs: CheckResult（outcome/reason/registration_id/config_hash_drift）
#   invariant: 实盘+未报备=拒下单；CheckResult不可变
# - id: A5
#   name_zh: ⑤ 启动/下单双断言
#   name_en: assert_can_start / assert_can_submit
#   intro: 启动和每笔下单前各校验一次，被阻断就抛合规异常
#   desc: 调 check_can_trade，is_blocked 且对应 enforce 开关开 → 抛 ProgrammaticTradingGuardError(ZA-EX-0010)；enforce 关则仅告警（宽松模式）
#   inputs: A4
#   outputs: CheckResult 或 ProgrammaticTradingGuardError
#   invariant: 启动+下单双校验防绕过单点
# 层: 输出
# - id: O1
#   name_zh: CheckResult 合规校验结果
#   name_en: CheckResult
#   intro: 不可变的校验结论（放行/拒因），供审计日志留存
#   invariant: 不可变 frozen dataclass
#   downstream: ex_core.trading_session（启动校验）/ ex_core.adapters.miniqmt_broker（下单校验）
# - id: O2
#   name_zh: 合规阻断异常 ZA-EX-0010
#   name_en: ProgrammaticTradingGuardError
#   intro: 实盘未报备或报备失效时抛出，硬阻断启动/下单
#   downstream: 调用方捕获 → 审计/告警（D_EX_CORE）
# [/ALGO_FLOW]
#
# 边:
# I3 --> A1
# I2 --> A2
# A1 --> A2
# A1 --> A3
# A2 --> A3
# I1 --> A4
# I4 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> A5
# A4 --> O1
# A5 --> O1
# A5 --> O2
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

__all__: Final = [
    "TradingMode",
    "CheckOutcome",
    "CheckResult",
    "RegistrationInfo",
    "ProgrammaticTradingGuardConfig",
    "ProgrammaticTradingGuardError",
    "ProgrammaticTradingGuard",
    "hash_risk_config",
]

_logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class ProgrammaticTradingGuardError(Exception):
    """程序化交易报备合规校验失败——实盘未报备或报备信息失效。"""

    error_code = "ZA-EX-0010"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class TradingMode(str, Enum):
    """交易模式——决定是否触发报备校验，以及执行路径选择（GAP-004 四模式开关）。

    BACKTEST: 回测（历史数据，不接 broker，豁免）
    PAPER: 纸面/模拟盘，实时行情模拟撮合，不接 broker，豁免
    SIMULATION: 影子账户，模拟 broker，豁免
    LIVE: 实盘，必须报备

    四模式对应 CC-06 横切开关：决策代码路径同构（generate_signal → portfolio_optimize →
    risk_check → execute），区别仅在 execute 层：
    - BACKTEST: MatchingLogic 撮合（历史 Tick 回放）
    - PAPER: paper matching 引擎（实时行情模拟撮合）
    - SIMULATION: MiniQmtBroker 真实下单但小仓位
    - LIVE: MiniQmtBroker 真实下单全量
    """

    BACKTEST = "backtest"
    PAPER = "paper"
    SIMULATION = "simulation"
    LIVE = "live"


class CheckOutcome(str, Enum):
    """校验结果——决定是否放行下单/启动。"""

    ALLOWED = "allowed"  # 通过（已报备或豁免模式）
    BLOCKED_UNREGISTERED = "blocked_unregistered"  # 实盘未报备
    BLOCKED_CONFIG_DRIFT = "blocked_config_drift"  # 报备信息漂移（风控配置变了）
    BLOCKED_LIVE_BROKER = "blocked_live_broker"  # 未识别 broker_id，保守拒绝


# ──────────────────────────────────────────────────────────────────────────────
# 不可变数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CheckResult:
    """报备校验结果——不可变，用于审计/日志/断言。

    Attributes:
        outcome: 校验结论
        broker_id: 被校验的 broker_id
        mode: 当前交易模式
        reason: 人类可读原因（BLOCKED 时为拒因，ALLOWED 时为放行说明）
        registration_id: 已报备的报备编号（未报备为 None）
        config_hash_drift: 配置漂移标志（True=报备时 hash ≠ 当前 hash）
    """

    outcome: CheckOutcome
    broker_id: str
    mode: TradingMode
    reason: str
    registration_id: str | None = None
    config_hash_drift: bool = False

    @property
    def is_allowed(self) -> bool:
        """是否放行（ALLOWED）。"""
        return self.outcome is CheckOutcome.ALLOWED

    @property
    def is_blocked(self) -> bool:
        """是否阻断（任一 BLOCKED_* 状态）。"""
        return not self.is_allowed


@dataclass(frozen=True)
class RegistrationInfo:
    """程序化交易报备信息——记录报备时点的关键信息。

    不可变快照，record_registration 时生成。变更需重新调用 record_registration
    生成新实例（旧实例保留作审计历史）。

    Attributes:
        registration_id: 报备编号（券商/交易所返回）
        strategy_id: 策略标识
        algorithm_types: 算法类型列表（如 ["TWAP", "VWAP"]）
        server_location: 服务器物理位置描述
        risk_config_hash: 报备时风控配置 hash
        max_total_orders_per_day: 报备时全账户日最大下单笔数
        cancel_rate_limit: 报备时撤单率上限（如 0.15）
        registered_at: 报备时间戳（ISO 字符串，避免 datetime 序列化复杂度）
    """

    registration_id: str
    strategy_id: str
    algorithm_types: tuple[str, ...]
    server_location: str
    risk_config_hash: str
    max_total_orders_per_day: int
    cancel_rate_limit: float
    registered_at: str


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ProgrammaticTradingGuardConfig:
    """程序化报备守卫配置。

    Attributes:
        mode: 交易模式（PAPER/SIMULATION/LIVE），决定是否触发校验
        live_broker_ids: 视为实盘的 broker_id 集合（如 {"miniqmt"}）。
            不在此集合的 broker_id 视为模拟盘（豁免）。
            若为 None，则所有 broker_id 都视为实盘（最严格）。
        enforce_on_start: 启动时是否强制校验（True=未报备拒绝启动）
        enforce_on_submit: 每笔下单前是否强制校验（True=未报备拒绝下单）
        allow_drift_warning_only: 报备信息漂移时是否仅告警不阻断（False=严格阻断）。
            默认 False（严格）——配置漂移意味着实际部署 ≠ 报备时声明，必须重新报备。
    """

    mode: TradingMode = TradingMode.SIMULATION
    live_broker_ids: set[str] | None = None  # None=所有 broker 视为实盘
    enforce_on_start: bool = True
    enforce_on_submit: bool = True
    allow_drift_warning_only: bool = False


# ──────────────────────────────────────────────────────────────────────────────
# 工具：风控配置 hash
# ──────────────────────────────────────────────────────────────────────────────


def hash_risk_config(
    max_single_order_pct: float,
    max_symbol_orders_per_day: int,
    max_total_orders_per_day: int,
    cancel_rate_limit: float,
    *,
    extra: dict[str, str] | None = None,
) -> str:
    """计算风控配置 hash（用于报备信息漂移检测）。

    将关键风控阈值按字典序拼接后 SHA-256，得到稳定 hash。
    报备时记录此 hash，启动/下单时重算对比，若不一致则判定报备信息漂移。

    Args:
        max_single_order_pct: 单票单笔最大占比（如 0.04）
        max_symbol_orders_per_day: 单票日最大下单笔数
        max_total_orders_per_day: 全账户日最大下单笔数
        cancel_rate_limit: 撤单率上限（如 0.15）
        extra: 额外配置项（如 max_position_pct 等，key/value 必须可序列化为 str）

    Returns:
        SHA-256 hex digest（64 字符）
    """
    items: dict[str, str] = {
        "max_single_order_pct": f"{max_single_order_pct:.6f}",
        "max_symbol_orders_per_day": str(max_symbol_orders_per_day),
        "max_total_orders_per_day": str(max_total_orders_per_day),
        "cancel_rate_limit": f"{cancel_rate_limit:.6f}",
    }
    if extra:
        items.update({k: str(v) for k, v in extra.items()})
    # 按 key 字典序排序，确保 hash 稳定
    canonical = "|".join(f"{k}={items[k]}" for k in sorted(items))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# 主类：ProgrammaticTradingGuard
# ──────────────────────────────────────────────────────────────────────────────


# 当前风控配置查询函数签名：() -> dict[str, object]
#   返回 dict 至少含 max_single_order_pct / max_symbol_orders_per_day /
#   max_total_orders_per_day / cancel_rate_limit 等字段
RiskConfigProvider = Callable[[], dict[str, object]]


class ProgrammaticTradingGuard:
    """程序化交易报备合规守卫——实盘下单前置硬校验。

    用法::

        guard = ProgrammaticTradingGuard(
            config=ProgrammaticTradingGuardConfig(
                mode=TradingMode.LIVE,
                live_broker_ids={"miniqmt"},
            ),
        )

        # 上线前报备（券商返回报备编号 + 报备时风控配置 hash）
        guard.record_registration(
            registration_id="PTR-2026-0001",
            strategy_id="daban_v1",
            algorithm_types=("TWAP", "VWAP"),
            server_location="上海券商机房托管",
            risk_config_hash=hash_risk_config(
                max_single_order_pct=0.04,
                max_symbol_orders_per_day=10,
                max_total_orders_per_day=50,
                cancel_rate_limit=0.15,
            ),
            max_total_orders_per_day=50,
            cancel_rate_limit=0.15,
        )

        # 启动时校验（TradingSession.start 调用）
        guard.assert_can_start("miniqmt")

        # 每笔下单前校验（OrderManager.submit_order 调用）
        guard.assert_can_submit("miniqmt")

    设计要点:
      - **启动+下单双校验**：start 与 submit 前各校验一次，防绕过单点
      - **配置漂移检测**：报备时记录风控 hash，运行时重算对比，漂移则视为未报备
      - **保守拒绝**：未识别的 broker_id（不在 live_broker_ids 且 mode=LIVE）
        保守按"实盘未报备"拒绝，避免误放行
      - **审计友好**：每次 check 返回 CheckResult（不可变），可记录到审计日志
      - **可测试**：mode 与 live_broker_ids 可注入，覆盖 PAPER/SIMULATION/LIVE 三模式
    """

    def __init__(
        self,
        config: ProgrammaticTradingGuardConfig | None = None,
        risk_config_provider: RiskConfigProvider | None = None,
    ) -> None:
        """初始化守卫。

        Args:
            config: 守卫配置（None=默认 SIMULATION 模式，豁免所有校验）
            risk_config_provider: 当前风控配置查询函数（用于运行时漂移检测）。
                None=不做漂移检测（仅校验是否已报备）。
        """
        self._config = config or ProgrammaticTradingGuardConfig()
        self._risk_config_provider = risk_config_provider
        self._registration: RegistrationInfo | None = None
        # 报备历史（审计用，按 registration_id 索引）
        self._registration_history: dict[str, RegistrationInfo] = {}

    # ── 报备信息管理 ──────────────────────────────────────────────────────

    def record_registration(
        self,
        registration_id: str,
        strategy_id: str,
        algorithm_types: tuple[str, ...] | list[str],
        server_location: str,
        risk_config_hash: str,
        max_total_orders_per_day: int,
        cancel_rate_limit: float,
    ) -> RegistrationInfo:
        """记录程序化交易报备信息。

        调用此方法表示已完成券商/交易所报备流程。后续启动/下单校验将基于
        此报备信息判断是否放行。

        重复调用（报备信息变更需重新报备）：生成新 RegistrationInfo，
        旧的保留在 _registration_history 中作审计。

        Args:
            registration_id: 报备编号（券商/交易所返回）
            strategy_id: 策略标识
            algorithm_types: 算法类型列表
            server_location: 服务器物理位置
            risk_config_hash: 报备时风控配置 hash（用 hash_risk_config 计算）
            max_total_orders_per_day: 报备时全账户日最大下单笔数
            cancel_rate_limit: 报备时撤单率上限

        Returns:
            RegistrationInfo: 不可变的报备信息快照
        """
        if not registration_id:
            raise ProgrammaticTradingGuardError("registration_id 不能为空")
        if not strategy_id:
            raise ProgrammaticTradingGuardError("strategy_id 不能为空")
        if max_total_orders_per_day <= 0:
            raise ProgrammaticTradingGuardError(f"max_total_orders_per_day 必须 > 0, 实际={max_total_orders_per_day}")
        if not (0 < cancel_rate_limit <= 1):
            raise ProgrammaticTradingGuardError(f"cancel_rate_limit 必须在 (0, 1] 区间, 实际={cancel_rate_limit}")

        algos = tuple(algorithm_types)
        if not algos:
            raise ProgrammaticTradingGuardError("algorithm_types 不能为空")

        from datetime import datetime, timezone

        info = RegistrationInfo(
            registration_id=registration_id,
            strategy_id=strategy_id,
            algorithm_types=algos,
            server_location=server_location,
            risk_config_hash=risk_config_hash,
            max_total_orders_per_day=max_total_orders_per_day,
            cancel_rate_limit=cancel_rate_limit,
            registered_at=datetime.now(timezone.utc).isoformat(),
        )
        # 旧的报备信息保留到历史（审计）
        if self._registration is not None:
            self._registration_history[self._registration.registration_id] = self._registration
        self._registration = info
        _logger.info(
            "程序化交易报备信息已记录: id=%s strategy=%s algos=%s hash=%s... orders_limit=%d cancel_limit=%.2f",
            registration_id,
            strategy_id,
            algos,
            risk_config_hash[:8],
            max_total_orders_per_day,
            cancel_rate_limit,
        )
        return info

    @property
    def registration(self) -> RegistrationInfo | None:
        """当前生效的报备信息（None=未报备）。"""
        return self._registration

    @property
    def registration_history(self) -> dict[str, RegistrationInfo]:
        """历史报备信息（审计用，按 registration_id 索引）。"""
        return dict(self._registration_history)

    # ── 校验主入口 ────────────────────────────────────────────────────────

    def check_can_trade(self, broker_id: str) -> CheckResult:
        """校验是否允许交易（启动/下单前置校验）。

        校验规则（按优先级）：
          1. 非 LIVE 模式（PAPER/SIMULATION）→ 直接放行（豁免）
          2. broker_id 不在 live_broker_ids → 保守按"实盘未识别 broker"拒绝
             （仅当 live_broker_ids 非空且 broker 不在集合内时）
          3. 未报备（_registration is None）→ 拒绝（BLOCKED_UNREGISTERED）
          4. 报备信息漂移（risk_config_hash ≠ 当前 hash）→ 拒绝（BLOCKED_CONFIG_DRIFT）
          5. 全部通过 → 放行

        Args:
            broker_id: 待校验的 broker_id

        Returns:
            CheckResult: 校验结果（不可变，含 outcome/reason）
        """
        mode = self._config.mode

        # 规则1：非 LIVE 豁免
        if mode is not TradingMode.LIVE:
            return CheckResult(
                outcome=CheckOutcome.ALLOWED,
                broker_id=broker_id,
                mode=mode,
                reason=f"非实盘模式（{mode.value}）豁免报备校验",
            )

        # 规则2：broker_id 不在 live_broker_ids → 保守拒绝
        # （live_broker_ids=None 时跳过此校验，所有 broker 视为实盘）
        if self._config.live_broker_ids is not None:
            if broker_id not in self._config.live_broker_ids:
                return CheckResult(
                    outcome=CheckOutcome.BLOCKED_LIVE_BROKER,
                    broker_id=broker_id,
                    mode=mode,
                    reason=(
                        f"实盘模式（{mode.value}）下 broker_id={broker_id} "
                        f"不在已识别实盘 broker 集合 {sorted(self._config.live_broker_ids)}，"
                        f"保守拒绝（避免未识别 broker 误放行）"
                    ),
                )

        # 规则3：未报备
        if self._registration is None:
            return CheckResult(
                outcome=CheckOutcome.BLOCKED_UNREGISTERED,
                broker_id=broker_id,
                mode=mode,
                reason=(
                    f"实盘模式（{mode.value}）broker={broker_id} 未完成程序化交易报备，"
                    f"禁止交易。请先调用 record_registration() 完成报备"
                ),
            )

        # 规则4：报备信息漂移检测
        drift_hash = self._detect_config_drift()
        if drift_hash is not None:
            # 漂移（drift_hash 是当前配置 hash，与报备时不一致）
            if self._config.allow_drift_warning_only:
                _logger.warning(
                    "报备信息漂移（仅告警模式）：报备 hash=%s... 当前 hash=%s... "
                    "实际部署风控配置与报备时声明不一致，建议尽快重新报备",
                    self._registration.risk_config_hash[:8],
                    drift_hash[:8],
                )
                return CheckResult(
                    outcome=CheckOutcome.ALLOWED,
                    broker_id=broker_id,
                    mode=mode,
                    reason=f"已报备（{self._registration.registration_id}），配置漂移仅告警",
                    registration_id=self._registration.registration_id,
                    config_hash_drift=True,
                )
            return CheckResult(
                outcome=CheckOutcome.BLOCKED_CONFIG_DRIFT,
                broker_id=broker_id,
                mode=mode,
                reason=(
                    f"报备信息漂移：报备时 hash={self._registration.risk_config_hash[:8]}... "
                    f"当前 hash={drift_hash[:8]}... 实际部署风控配置与报备时声明不一致，"
                    f"必须重新调用 record_registration() 完成重新报备后才能交易"
                ),
                registration_id=self._registration.registration_id,
                config_hash_drift=True,
            )

        # 规则5：全部通过
        return CheckResult(
            outcome=CheckOutcome.ALLOWED,
            broker_id=broker_id,
            mode=mode,
            reason=f"已报备（{self._registration.registration_id}），校验通过",
            registration_id=self._registration.registration_id,
        )

    def assert_can_start(self, broker_id: str) -> CheckResult:
        """启动校验——实盘未报备抛 ProgrammaticTradingGuardError。

        用于 TradingSession.start() 前置校验。enforce_on_start=False 时跳过
        （仅记录日志），允许"宽松启动"用于历史报备信息已存在的过渡期。

        Args:
            broker_id: 待校验的 broker_id

        Returns:
            CheckResult: 校验结果

        Raises:
            ProgrammaticTradingGuardError: 实盘未报备/配置漂移/未识别 broker
        """
        result = self.check_can_trade(broker_id)
        if result.is_blocked:
            if self._config.enforce_on_start:
                _logger.error(
                    "启动报备校验失败: broker=%s outcome=%s reason=%s",
                    broker_id,
                    result.outcome.value,
                    result.reason,
                )
                raise ProgrammaticTradingGuardError(f"[启动校验] {result.reason} (broker={broker_id})")
            _logger.warning(
                "启动报备校验失败但 enforce_on_start=False（宽松模式，跳过）: %s",
                result.reason,
            )
        else:
            _logger.info(
                "启动报备校验通过: broker=%s %s",
                broker_id,
                result.reason,
            )
        return result

    def assert_can_submit(self, broker_id: str) -> CheckResult:
        """下单校验——实盘未报备抛 ProgrammaticTradingGuardError。

        用于 OrderManager.submit_order() 前置校验。enforce_on_submit=False 时
        跳过（仅记录日志），双保险失效但不阻断。

        Args:
            broker_id: 待校验的 broker_id

        Returns:
            CheckResult: 校验结果

        Raises:
            ProgrammaticTradingGuardError: 实盘未报备/配置漂移/未识别 broker
        """
        result = self.check_can_trade(broker_id)
        if result.is_blocked:
            if self._config.enforce_on_submit:
                _logger.error(
                    "下单报备校验失败: broker=%s outcome=%s reason=%s",
                    broker_id,
                    result.outcome.value,
                    result.reason,
                )
                raise ProgrammaticTradingGuardError(f"[下单校验] {result.reason} (broker={broker_id})")
            _logger.warning(
                "下单报备校验失败但 enforce_on_submit=False（宽松模式，跳过）: %s",
                result.reason,
            )
        return result

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _detect_config_drift(self) -> str | None:
        """检测风控配置漂移。

        Returns:
            None = 未配置 risk_config_provider 或未漂移（放行）
            str = 当前配置 hash（与报备时不一致，漂移）
        """
        if self._risk_config_provider is None:
            return None  # 未配置查询函数，不做漂移检测
        if self._registration is None:
            return None  # 未报备，由规则3拦截
        try:
            current = self._risk_config_provider()
            current_hash = hash_risk_config(
                max_single_order_pct=float(current.get("max_single_order_pct", 0)),
                max_symbol_orders_per_day=int(current.get("max_symbol_orders_per_day", 0)),
                max_total_orders_per_day=int(current.get("max_total_orders_per_day", 0)),
                cancel_rate_limit=float(current.get("cancel_rate_limit", 0)),
            )
        except Exception as exc:  # noqa: BLE001 — 查询失败保守放行（不阻断交易）
            _logger.warning(
                "风控配置查询失败，跳过漂移检测（保守放行）: %s",
                exc,
                exc_info=True,
            )
            return None
        if current_hash != self._registration.risk_config_hash:
            return current_hash
        return None

    def is_live_broker(self, broker_id: str) -> bool:
        """判断 broker_id 是否为实盘（用于审计/日志）。

        实盘判定：mode=LIVE 且（live_broker_ids is None 或 broker_id 在集合内）。
        """
        if self._config.mode is not TradingMode.LIVE:
            return False
        if self._config.live_broker_ids is None:
            return True
        return broker_id in self._config.live_broker_ids
