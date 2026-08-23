# [BLUEPRINT] MOD-EX-035 | docs/03_modules/MOD-EX-035/
# [MODULE] zephyr.ex_core.live_simulation_switcher
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L06-001(TradingSession 模式门) ; MOD-EX-058(miniQMT Channel Manager 实盘通道)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 默认模拟盘(构造即 SIMULATION); 模拟→实盘必须显式确认令牌(验证失败/空令牌→LiveSwitchError 且停留原模式,Fail-Closed); 实盘→模拟降风险方向免令牌; 每次切换留痕(SwitchRecord frozen,令牌只存 sha256 指纹不落原文); 本模块只管模式与留痕,不触发任何真实下单
# [MODIFY-GUARD] docs/03_modules/MOD-EX-035/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LiveSwitchError(ZA-EX-0019)
# [TESTS] tests/ex_core/test_live_simulation_switcher.py
# [A_module] module_id=MOD-EX-035 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""Live/Simulation Switcher — 实盘/模拟切换开关 (MOD-EX-035)

D-EX-CORE-35（2026-08-23 门禁修正版）：A 股/QMT 实盘与模拟盘一键切换 +
状态同步 + 资金隔离。原门禁依赖 OKX/XTP/CTP（超约束三，已删），现门禁为
"miniQMT 实盘通道就绪"（MOD-EX-058 通道管理器可用）。

铁律：
  - 默认模拟盘语义：构造即 SIMULATION，任何路径不得默认实盘。
  - 模拟→实盘必须显式确认令牌（token_verifier 注入，生产接线 Owner 签发
    的一次性令牌）；验证失败/空令牌一律 LiveSwitchError 且停留模拟盘
    （Fail-Closed，B-007 人工闸门口径）。
  - 实盘→模拟是风险收敛方向，免令牌随时可切。
  - 全程留痕：SwitchRecord 记录时刻/方向/原因/操作人/令牌指纹
    （sha256 前 12 位，原文不落盘）。
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "LiveSimulationSwitcher",
    "LiveSwitchError",
    "SwitchRecord",
    "TradingMode",
]


def _utcnow() -> datetime:
    return datetime.now(UTC)


class LiveSwitchError(ZephyrBaseError):
    """实盘切换错误（令牌验证失败/非法迁移），Fail-Closed 停留原模式。"""

    error_code = "ZA-EX-0019"


class TradingMode(str, Enum):
    """交易模式（默认模拟）。"""

    SIMULATION = "simulation"
    LIVE = "live"


@dataclass(frozen=True)
class SwitchRecord:
    """切换留痕（frozen；token_fingerprint 为 sha256 前 12 位，非原文）。"""

    switched_at: datetime
    from_mode: TradingMode
    to_mode: TradingMode
    reason: str
    operator: str
    token_fingerprint: str  # 实盘→模拟免令牌时为空串


def _fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]


class LiveSimulationSwitcher:
    """实盘/模拟切换开关（默认模拟盘；切实盘需显式确认令牌+留痕）。

    Args:
        token_verifier: 确认令牌验证器（注入；生产接线 Owner 签发的一次性
            令牌校验，验证器异常按验证失败处理，Fail-Closed）。
        clock: 时钟注入（默认 UTC now，测试可注入假钟）。
        audit_sink: 审计下沉（可选；每次切换除内存留痕外回调一份，
            生产接线 audit_journal）。
    """

    def __init__(
        self,
        token_verifier: Callable[[str], bool],
        *,
        clock: Callable[[], datetime] = _utcnow,
        audit_sink: Callable[[SwitchRecord], None] | None = None,
    ) -> None:
        self._token_verifier = token_verifier
        self._clock = clock
        self._audit_sink = audit_sink
        self._mode = TradingMode.SIMULATION  # 默认模拟盘语义（不变量）
        self._records: list[SwitchRecord] = []

    @property
    def current_mode(self) -> TradingMode:
        """当前交易模式。"""
        return self._mode

    @property
    def is_live(self) -> bool:
        """实盘判据（调用方据此决定是否走 MOD-EX-058 真单通道）。"""
        return self._mode is TradingMode.LIVE

    def switch_history(self) -> tuple[SwitchRecord, ...]:
        """全部切换留痕（只读快照）。"""
        return tuple(self._records)

    def switch_to_live(
        self,
        *,
        confirmation_token: str,
        reason: str,
        operator: str = "owner",
    ) -> SwitchRecord:
        """模拟→实盘：显式确认令牌 + 留痕。验证失败 Fail-Closed 停留模拟盘。"""
        if self._mode is TradingMode.LIVE:
            raise LiveSwitchError(
                "已处于实盘模式，拒绝重复切换",
                details={"current_mode": self._mode.value},
            )
        if not confirmation_token:
            raise LiveSwitchError(
                "实盘切换缺少确认令牌（Fail-Closed，停留模拟盘）",
                details={"reason": "empty_token"},
            )
        try:
            verified = bool(self._token_verifier(confirmation_token))
        except Exception as exc:  # noqa: BLE001 — 验证器异常按验证失败处理
            _logger.error("确认令牌验证器异常(按验证失败处理): %s", type(exc).__name__)
            verified = False
        if not verified:
            raise LiveSwitchError(
                "实盘确认令牌验证失败（Fail-Closed，停留模拟盘）",
                details={"reason": "token_rejected"},
            )
        if not reason.strip():
            raise LiveSwitchError(
                "实盘切换必须填写原因（留痕必填）",
                details={"reason": "empty_reason"},
            )
        return self._commit(
            to_mode=TradingMode.LIVE,
            reason=reason,
            operator=operator,
            token_fingerprint=_fingerprint(confirmation_token),
        )

    def switch_to_simulation(
        self,
        *,
        reason: str,
        operator: str = "owner",
    ) -> SwitchRecord:
        """实盘→模拟：风险收敛方向免令牌，随时可切 + 留痕。"""
        if self._mode is TradingMode.SIMULATION:
            raise LiveSwitchError(
                "已处于模拟模式，拒绝重复切换",
                details={"current_mode": self._mode.value},
            )
        return self._commit(
            to_mode=TradingMode.SIMULATION,
            reason=reason or "risk_reduction",
            operator=operator,
            token_fingerprint="",
        )

    def _commit(
        self,
        *,
        to_mode: TradingMode,
        reason: str,
        operator: str,
        token_fingerprint: str,
    ) -> SwitchRecord:
        record = SwitchRecord(
            switched_at=self._clock(),
            from_mode=self._mode,
            to_mode=to_mode,
            reason=reason,
            operator=operator,
            token_fingerprint=token_fingerprint,
        )
        self._mode = to_mode
        self._records.append(record)
        _logger.warning(
            "交易模式切换: %s → %s (operator=%s, reason=%s)",
            record.from_mode.value,
            record.to_mode.value,
            operator,
            reason,
        )
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception as exc:  # noqa: BLE001 — 审计下沉异常不回滚切换
                _logger.error("切换留痕审计下沉失败: %s", type(exc).__name__)
        return record
