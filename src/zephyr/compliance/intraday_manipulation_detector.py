# [BLUEPRINT] MOD-CMP-011 | 待统筹登记（blueprint 未建，真源=43_compliance_discipline.md §7.3/§10）
# [MODULE] zephyr.compliance.intraday_manipulation_detector
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.compliance.trading_compliance_detector(检测规则唯一真源, 零重实现); zephyr.compliance.manipulation_stream_driver(30min 窗口塑形复用); zephyr.compliance.compliance_log; zephyr.shared.foundation.errors
# [CONSUMERS] T+1 合规审计/日终复盘编排(43号§7.6 数据流末端 compliance_log→T+1 归档); 未来盘中流编排就绪后实时侧由 manipulation_stream_driver 承载(同一 detector 实例)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测规则唯一真源=TradingComplianceDetector(批层零规则重实现); 窗口塑形复用 ManipulationStreamDriver(30min 滚动 trim); 首命中去重(每标的每日每类≤1 条报告命中, 日志全量留痕); minute_volume_provider 缺失→Spoofing 跳过不误判; 命中处置语义继承 detector(HARD_BLOCK); 零命中批也落 MANIPULATION_BATCH_SCAN(自证清白: 扫过且零命中)
# [MODIFY-GUARD] 43_compliance_discipline.md §7.3/§10
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ManipulationBatchError(ZA-CMP-0014)
# [TESTS] tests/compliance/test_intraday_manipulation_detector.py
# [A_module] module_id=MOD-CMP-011 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: ManipulationBatchInput(trade_date + 全日订单记录(含撤单时间) + 全日成交记录)——券商历史导出/订单日志重放
# F1: run_batch——按 symbol 分组→scan_symbol_orders 逐标的时间序重放(30min trim)→scan_trade 逐笔 WashTrade→聚合报告→落 MANIPULATION_BATCH_SCAN 汇总
# F2: scan_symbol_orders(symbol, orders)——实时兼容单标的人口: placed_at 时间序重放经 ManipulationStreamDriver(同一 detector 实例), 首命中去重
# F3: scan_trade(trade)——WashTrade 零容忍直查(detector.check_wash_trade)
# A1: 窗口口径=detector.thresholds.spoof_repeat_window_s(1800s, 43号§7.3)——trim_before(placed_at-窗口)后喂入, 与实时喂入命中集合一致
# O1: ManipulationBatchReport(首命中去重后 hits) + compliance_log 双类事件(MANIPULATION_VERDICT 逐命中/MANIPULATION_BATCH_SCAN 批汇总)
# [/ALGO_FLOW]
"""
D_COMPLIANCE — 盘中操纵检测三规则离线批处理口径 MVP（43 号 §7.3，BM-BUY-15 补强残余）。

43 号结案残余："对敲/拉抬/洗售（Spoofing/Layering/WashTrade）盘中实时检测未做
——需盘中实时流驱动"。实时侧适配已由 manipulation_stream_driver（2026-08-20）
承载；本模块补**离线批处理口径**——盘中流编排未就绪期间，以全日订单/成交历史
（券商导出/订单日志）离线重放完成同样的三类检测，服务 T+1 审计与"自证清白"
证据链（43 号 §7.3 检测目标=自我监控+证据留存）。

接口兼容实时（设计约束）：
- 记录类型与实时侧一致（ComplianceOrderRecord/ComplianceTradeRecord）；
- 批内按 placed_at 时间序重放 + 30min 滚动 trim（窗口口径取自
  detector.thresholds.spoof_repeat_window_s，与实时侧同一 SSoT），
  命中集合与实时喂入等价（批侧记录自带撤单时间，评估即全信息口径）；
- scan_symbol_orders/scan_trade 为单标的/单笔公开入口——未来盘中流编排
  就绪后可按标的增量喂同一组方法，或直接切换 manipulation_stream_driver
  （同一 TradingComplianceDetector 实例，规则/阈值/落日志唯一真源）。

检测规则与阈值（唯一真源=TradingComplianceDetector/ComplianceThresholds，43 号 §7.3）：
  | 类型      | 检测规则                                                    | 阈值默认值                          |
  |----------|------------------------------------------------------------|------------------------------------|
  | Spoofing | 大额挂单(>分钟均量 20%)后 10s 内撤单，同 pattern 30min ≥3 次 | spoof_size_ratio=0.2 / 10s / 3 次  |
  | Layering | 同侧连续 ≥3 档价格梯度单且序列内总撤单率 >80%                | layer_min_levels=3 / 0.80          |
  | WashTrade| 自成交（买卖双方同账户），零容忍                            | wash_self_trade=零容忍             |
阈值入册：risk_limit_registry（REG-RLM-001）入册草稿见
.runtime/construction_20260823/fragments/P2A_registry.yaml（写片段不直改共享注册表）。

误报率口径（留痕，43 号 §7.3"防误伤"+§8 开放问题"待 C1 实盘校准"）：
- 定义：误报率 = 人工复核判定非操纵的命中数 / 总命中数（逐月滚动窗口统计，
  复核结论以 compliance_log MANIPULATION_VERDICT 记录为分母真源）。
- MVP 无实盘基数：阈值取 43 号 §7.3 默认值——检测目标是自我监控+自证清白，
  口径宁严勿宽（命中=Hard Block 语义继承 detector，批侧仅报告不阻断）。
- 天然低误报论据：内部撤单率 ≤15% 远低于官方 50% 监控线（40 号 §2.13，
  中基协 2026-07 确认）；个人低频限频 ≤15 笔/秒（24 号 §3.7）。
- 报告去重口径=每标的每日每类至多 1 条命中（防告警风暴）；compliance_log
  保留全量命中证据（detector 逐命中落 MANIPULATION_VERDICT，不去重）。
- 校准路径：命中样本人工复核 → 误报率统计 → C1 实盘阶段按误拦截率回调阈值
  （与 43 号 §8 开放问题登记一致，本模块不预设自动调阈）。

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: detector 参数
#   fields: 参数 detector（无注解）
#   code: intraday_manipulation_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: minute_volume_provider 参数
#   fields: 参数 minute_volume_provider（无注解）
#   code: intraday_manipulation_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: logger 参数
#   fields: 参数 logger（无注解）
#   code: intraday_manipulation_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① IntradayManipulationDetector
#   name_en: IntradayManipulationDetector
#   intro: Spoofing/Layering/WashTrade 离线批处理检测器。
#   desc: Spoofing/Layering/WashTrade 离线批处理检测器。 Args: detector: TradingComplianceDetector 实例（None=自…；公共方法（定义序）: run_bat…
#   inputs: detector minute_volume_provider logger
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: IntradayManipulationDetector
#   downstream: T+1 合规审计/日终复盘编排(43号§7.6 数据流末端 compliance_log→T+1 归档); 未来盘中流编排就绪后实时侧由 manipulati…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Callable, Final

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.manipulation_stream_driver import ManipulationStreamDriver
from zephyr.compliance.trading_compliance_detector import (
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationType,
    ManipulationVerdict,
    TradingComplianceDetector,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "IntradayManipulationDetector",
    "ManipulationBatchError",
    "ManipulationBatchInput",
    "ManipulationBatchReport",
    "ManipulationHit",
]

#: 批扫描汇总事件类型（compliance_log 兼容格式；逐命中事件=detector 侧 MANIPULATION_VERDICT）
_EVENT_BATCH_SCAN: Final = "MANIPULATION_BATCH_SCAN"
#: 批扫描汇总事件 source 字段（与模块名一致，审计可溯）
_SOURCE: Final = "intraday_manipulation_detector"


class ManipulationBatchError(ZephyrBaseError):
    """批处理输入非法——空 trade_date、空 symbol 等。"""

    error_code = "ZA-CMP-0014"


@dataclass(frozen=True)
class ManipulationBatchInput:
    """离线批处理输入（一个交易日的订单+成交全量记录）。

    Attributes:
        trade_date: 交易日（ISO 日期串，审计锚点）。
        orders: 全日订单记录（含撤单时间；无需预排序，批内按 placed_at 重放）。
        trades: 全日成交记录（WashTrade 检测输入）。
    """

    trade_date: str
    orders: tuple[ComplianceOrderRecord, ...] = ()
    trades: tuple[ComplianceTradeRecord, ...] = ()


@dataclass(frozen=True)
class ManipulationHit:
    """单条命中（标的 + detector 结论）。"""

    symbol: str
    verdict: ManipulationVerdict


@dataclass(frozen=True)
class ManipulationBatchReport:
    """批扫描报告（首命中去重口径：每标的每日每类 ≤1 条）。

    Attributes:
        trade_date: 交易日。
        symbols_scanned: 扫描标的数。
        orders_scanned: 扫描订单条数。
        trades_scanned: 扫描成交条数。
        hits: 去重后命中（按 symbol/mtype 排序，确定性输出）。
    """

    trade_date: str
    symbols_scanned: int
    orders_scanned: int
    trades_scanned: int
    hits: tuple[ManipulationHit, ...] = field(default_factory=tuple)


class IntradayManipulationDetector:
    """Spoofing/Layering/WashTrade 离线批处理检测器。

    Args:
        detector: TradingComplianceDetector 实例（None=自建默认阈值实例）。
            同一实例驱动——检测规则/阈值/逐命中落日志全归 detector（唯一真源）。
        minute_volume_provider: callable(symbol) -> float 分钟均量供给
            （Spoofing 检测前提；None=Spoofing 跳过降级，防误伤）。
        logger: ComplianceLogger（批汇总事件落库；None=复用 detector 的 logger，
            保证批事件与逐命中事件同一证据链文件）。
    """

    def __init__(
        self,
        detector: TradingComplianceDetector | None = None,
        *,
        minute_volume_provider: Callable[[str], float] | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._detector = detector or TradingComplianceDetector(logger=logger)
        self._logger = logger or self._detector.logger
        self._minute_volume_provider = minute_volume_provider

    # ── 批处理主入口 ──

    def run_batch(self, batch: ManipulationBatchInput) -> ManipulationBatchReport:
        """全日订单/成交离线批扫描 → 去重报告 + compliance_log 汇总事件。

        零命中批也落 MANIPULATION_BATCH_SCAN（自证清白：当日扫过且零命中）。

        Raises:
            ManipulationBatchError: trade_date 空 / 记录 symbol 空。
        """
        trade_date = (batch.trade_date or "").strip()
        if not trade_date:
            raise ManipulationBatchError("trade_date 不能为空", details={"trade_date": repr(batch.trade_date)})

        by_symbol: dict[str, list[ComplianceOrderRecord]] = {}
        for o in batch.orders:
            self._require_symbol(o.symbol)
            by_symbol.setdefault(o.symbol, []).append(o)

        hits: list[ManipulationHit] = []
        for symbol in sorted(by_symbol):
            hits.extend(self.scan_symbol_orders(symbol, by_symbol[symbol]))
        for trade in batch.trades:
            self._require_symbol(trade.symbol)
            hit = self.scan_trade(trade)
            if hit is not None:
                hits.append(hit)
        hits.sort(key=lambda h: (h.symbol, h.verdict.mtype.value))

        report = ManipulationBatchReport(
            trade_date=trade_date,
            symbols_scanned=len(by_symbol),
            orders_scanned=len(batch.orders),
            trades_scanned=len(batch.trades),
            hits=tuple(hits),
        )
        self._logger.log(
            _EVENT_BATCH_SCAN,
            _SOURCE,
            {
                "trade_date": trade_date,
                "symbols_scanned": report.symbols_scanned,
                "orders_scanned": report.orders_scanned,
                "trades_scanned": report.trades_scanned,
                "hit_count": len(hits),
                "hit_types": sorted({h.verdict.mtype.value for h in hits}),
                "hit_symbols": sorted({h.symbol for h in hits}),
            },
        )
        return report

    # ── 实时兼容单标的/单笔入口 ──

    def scan_symbol_orders(
        self,
        symbol: str,
        orders: list[ComplianceOrderRecord] | tuple[ComplianceOrderRecord, ...],
    ) -> list[ManipulationHit]:
        """单标的订单序列扫描（Spoofing + Layering）。

        实时兼容口径：placed_at 时间序重放经 ManipulationStreamDriver
        （30min 滚动 trim，窗口=detector.thresholds.spoof_repeat_window_s），
        命中集合与实时喂入等价；首命中去重（每类 ≤1 条）。
        """
        self._require_symbol(symbol)
        if not orders:
            return []
        driver = ManipulationStreamDriver(self._detector, minute_volume_provider=self._minute_volume_provider)
        window_s = self._detector.thresholds.spoof_repeat_window_s
        first_hits: dict[ManipulationType, ManipulationVerdict] = {}
        for record in sorted(orders, key=lambda o: o.placed_at):
            driver.trim_before(record.placed_at - timedelta(seconds=window_s))
            for verdict in driver.on_order_placed(record):
                first_hits.setdefault(verdict.mtype, verdict)
        return [ManipulationHit(symbol=symbol, verdict=v) for v in first_hits.values()]

    def scan_trade(self, trade: ComplianceTradeRecord) -> ManipulationHit | None:
        """单笔成交 WashTrade 零容忍直查。"""
        self._require_symbol(trade.symbol)
        verdict = self._detector.check_wash_trade(trade)
        if verdict is None:
            return None
        return ManipulationHit(symbol=trade.symbol, verdict=verdict)

    # ── 内部 ──

    @staticmethod
    def _require_symbol(symbol: str) -> None:
        if not symbol or not symbol.strip():
            raise ManipulationBatchError("symbol 不能为空", details={"symbol": repr(symbol)})
