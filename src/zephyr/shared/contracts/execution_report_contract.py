# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.execution_report_contract
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.execution_report(CTR-P1-007 codegen); zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] D_REPORTING(TCA); D_PF_CORE(A1③归因/A8 mSPRT delta提取); D_RESEARCH
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] codegen契约(shared/contracts/execution_report.py)不改; 校验Fail-Closed; 序列化往返恒等(from∘to=id); Protocol仅结构子类型不反向依赖上层域
# [MODIFY-GUARD] cross_layer_contracts.yaml CTR-P1-007(字段真源=Owner窗口); architecture_model/contracts/cross_layer_contracts.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ExecutionReportContractError(ZA-SH-0054)
# [TESTS] tests/ex_core/test_execution_report_contract.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CTR-P1-007 ExecutionReport 契约层——校验 / 序列化 / 消费方 Protocol 对接位（GAP-L06-003）。

与既有产物的关系（并存，不破坏既有消费方）：
- 数据模型真源 = codegen frozen dataclass ``zephyr.shared.contracts.execution_report.
  ExecutionReport``（SSoT=cross_layer_contracts.yaml CTR-P1-007 v1.0，DO NOT EDIT）。
  本模块不重定义数据类，只在其上提供契约层能力。
- 产出逻辑 = ``zephyr.ex_core.execution_report.build_execution_report``
  （ZA-EX-0012 产出侧 4 条输入校验）。本模块的 validate 是**消费方入站**守卫
  （15 条+），两者互补：产出侧保证"造得对"，契约层保证"收得对"。

FIX 5.0 语义对标（字段取舍论证详见施工报告）：
- 已覆盖：order_id(37) / symbol(55) / direction(54) / intended_quantity(38 OrderQty) /
  actual_quantity(14 CumQty) / vwap_price(6 AvgPx) / commission(12) /
  execution_start~end(60 TransactTime 窗口) / idempotency_key(11 ClOrdID)。
- 不纳入（逐笔事件语义归 CTR-005 Fill）：exec_id(17 ExecID) / liquidity_flag(851
  LastLiquidityInd) / OrdStatus(39) / ExecType(150)——本契约是订单级**聚合**执行报告
  （TCA 输入），非 FIX 逐笔/状态事件流；status 由 actual<intended 隐含（部分成交）。
- A 股特性以**校验参数注入**纳入（不污染 codegen 契约）：board_lot 整手（BUY 强制、
  SELL 零股豁免，主板默认 100；分板块起买/递增规则真源=ex_core.board_lot）、
  price_limit_up/down 涨跌停（成交价物理边界，行情侧注入）。

消费方接口位（Protocol 预留，结构子类型）：
- ``ExecutionReportSource``——A1③ 归因/TCA 拉取口（按 order_id 取 / 按标的+窗口迭代）。
- ``ExecutionReportDeltaExtractor``——A8 mSPRT 对接位，方法签名对齐 pf_core 预留的
  ``ChampionChallengerDeltaExtractor``（extract_delta(champion, challenger) -> float），
  ``NetPnlDeltaExtractor`` 为默认实现：配对报告（同标的同方向，Fail-Closed）逐笔
  delta = net_cashflow(challenger) − net_cashflow(champion)。
"""

from __future__ import annotations

import math
from dataclasses import MISSING, fields
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping, Protocol, runtime_checkable

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.foundation.errors import ZephyrBaseError

CONTRACT_ID = "CTR-P1-007"
SCHEMA_VERSION = "1.0"
DEFAULT_BOARD_LOT = 100  # A 股主板/创业板/北交所整手（科创板分板块规则见 ex_core.board_lot）

_DIRECTIONS = frozenset({OrderSide.BUY.value, OrderSide.SELL.value})
_NON_EMPTY_STR_FIELDS = ("order_id", "symbol", "direction", "broker_id", "algo_type", "idempotency_key")
_DECIMAL_FIELDS = ("intended_price", "vwap_price", "commission")
_INT_FIELDS = ("intended_quantity", "actual_quantity")
_FLOAT_FIELDS = ("slippage_bps",)


class ExecutionReportContractError(ZephyrBaseError):
    """CTR-P1-007 契约层校验/序列化失败——Fail-Closed 拒绝非法 ExecutionReport。"""

    error_code = "ZA-SH-0054"


def _fail(message: str, **details: object) -> None:
    raise ExecutionReportContractError(message, details={k: str(v) for k, v in details.items()})


def _parse_iso_utc(value: str, field_name: str) -> datetime:
    """ISO 8601 解析 + 时区强制（契约口径：ISO 8601 UTC）。"""
    try:
        ts = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        _fail(f"{field_name} 非合法 ISO 8601 时间戳", field=field_name, value=value)
    if ts.tzinfo is None:
        _fail(f"{field_name} 缺时区信息（契约要求 ISO 8601 UTC）", field=field_name, value=value)
    return ts


def _check_decimal(report: ExecutionReport, field_name: str) -> Decimal:
    value = getattr(report, field_name)
    if not isinstance(value, Decimal):
        _fail(f"{field_name} 必须为 Decimal", field=field_name, actual_type=type(value).__name__)
    if not value.is_finite():
        _fail(f"{field_name} 必须为有限值", field=field_name, value=value)
    return value


def validate_execution_report(
    report: ExecutionReport,
    *,
    board_lot: int | None = None,
    price_limit_up: Decimal | None = None,
    price_limit_down: Decimal | None = None,
) -> ExecutionReport:
    """CTR-P1-007 消费方入站校验（Fail-Closed）。

    Args:
        report: 待校验 ExecutionReport（codegen frozen 契约）。
        board_lot: A 股整手股数（可选）；传入时 BUY 方向 intended_quantity 须为整手
            （SELL 零股豁免——上交所卖出可零股申报）。
        price_limit_up: 涨停价（可选，行情侧注入）；成交时 vwap_price 不得高于涨停。
        price_limit_down: 跌停价（可选，行情侧注入）；成交时 vwap_price 不得低于跌停。

    Returns:
        校验通过的 report 本体（恒等返回，便于链式）。

    Raises:
        ExecutionReportContractError: 任一字段非法（空标识/方向越枚举/量非正/超量成交/
            负价/负佣/时序倒置/裸时区/非有限滑点/版本不符/非整手/突破涨跌停）。
    """
    if not isinstance(report, ExecutionReport):
        _fail("report 必须为 ExecutionReport", actual_type=type(report).__name__)

    for name in _NON_EMPTY_STR_FIELDS:
        value = getattr(report, name)
        if not isinstance(value, str) or not value:
            _fail(f"{name} 必须为非空字符串", field=name, value=value)
    if report.direction not in _DIRECTIONS:
        _fail("direction 越枚举（BUY|SELL）", direction=report.direction)
    if report.schema_version != SCHEMA_VERSION:
        _fail("schema_version 不支持", schema_version=report.schema_version, supported=SCHEMA_VERSION)

    for name in _INT_FIELDS:
        value = getattr(report, name)
        if type(value) is not int:  # 严格 int——bool 是 int 子类，显式排除
            _fail(f"{name} 必须为 int", field=name, actual_type=type(value).__name__)
    if report.intended_quantity <= 0:
        _fail("intended_quantity 必须为正", intended_quantity=report.intended_quantity)
    if report.actual_quantity < 0:
        _fail("actual_quantity 不能为负", actual_quantity=report.actual_quantity)
    if report.actual_quantity > report.intended_quantity:
        _fail(
            "actual_quantity 不能超过 intended_quantity（超量成交）",
            actual_quantity=report.actual_quantity,
            intended_quantity=report.intended_quantity,
        )

    intended_price = _check_decimal(report, "intended_price")
    vwap_price = _check_decimal(report, "vwap_price")
    commission = _check_decimal(report, "commission")
    if intended_price < 0:
        _fail("intended_price 不能为负", intended_price=intended_price)
    if vwap_price < 0:
        _fail("vwap_price 不能为负", vwap_price=vwap_price)
    if report.actual_quantity > 0 and vwap_price <= 0:
        _fail("有成交量时 vwap_price 必须为正", actual_quantity=report.actual_quantity)
    if commission < 0:
        _fail("commission 不能为负", commission=commission)

    if isinstance(report.slippage_bps, bool) or not isinstance(report.slippage_bps, (int, float)):
        _fail("slippage_bps 必须为数值", actual_type=type(report.slippage_bps).__name__)
    if not math.isfinite(float(report.slippage_bps)):
        _fail("slippage_bps 必须为有限值", slippage_bps=report.slippage_bps)

    start = _parse_iso_utc(report.execution_start, "execution_start")
    end = _parse_iso_utc(report.execution_end, "execution_end")
    if start > end:
        _fail("execution_start 晚于 execution_end（时序倒置）", start=report.execution_start, end=report.execution_end)

    if board_lot is not None:
        if type(board_lot) is not int or board_lot <= 0:
            _fail("board_lot 必须为正整数", board_lot=board_lot)
        if report.direction == OrderSide.BUY.value and report.intended_quantity % board_lot != 0:
            _fail(
                "BUY 方向 intended_quantity 须为整手（A 股买入整手申报）",
                intended_quantity=report.intended_quantity,
                board_lot=board_lot,
            )

    for name, limit in (("price_limit_up", price_limit_up), ("price_limit_down", price_limit_down)):
        if limit is not None and (not isinstance(limit, Decimal) or not limit.is_finite() or limit <= 0):
            _fail(f"{name} 必须为正有限 Decimal", field=name, value=limit)
    if price_limit_up is not None and price_limit_down is not None and price_limit_up < price_limit_down:
        _fail("price_limit_up 低于 price_limit_down（涨跌停倒置）", up=price_limit_up, down=price_limit_down)
    if report.actual_quantity > 0:
        if price_limit_up is not None and vwap_price > price_limit_up:
            _fail("vwap_price 突破涨停价（物理不可能成交）", vwap_price=vwap_price, price_limit_up=price_limit_up)
        if price_limit_down is not None and vwap_price < price_limit_down:
            _fail("vwap_price 跌破跌停价（物理不可能成交）", vwap_price=vwap_price, price_limit_down=price_limit_down)

    return report


def execution_report_to_payload(report: ExecutionReport) -> dict[str, object]:
    """序列化为可 JSON 化的 payload（Decimal→str 保精度，其余原样）。

    按 codegen 契约字段全集迭代——契约字段漂移时本函数随之漂移，
    tests 侧以字段全集比对 + 计数守卫显式暴露漂移。
    """
    if not isinstance(report, ExecutionReport):
        _fail("report 必须为 ExecutionReport", actual_type=type(report).__name__)
    payload: dict[str, object] = {}
    for f in fields(ExecutionReport):
        value = getattr(report, f.name)
        payload[f.name] = str(value) if isinstance(value, Decimal) else value
    return payload


def _coerce_decimal(name: str, value: object) -> Decimal:
    # 拒绝 float（二进制浮点污染精度）与 bool；接受 str/int/Decimal
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        _fail(f"{name} 反序列化只接受 str/int", field=name, actual_type=type(value).__name__)
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        _fail(f"{name} 非合法十进制", field=name, value=value)


def execution_report_from_payload(payload: Mapping[str, object]) -> ExecutionReport:
    """从 payload 反序列化（缺键/类型错/版本不符 Fail-Closed；未知键忽略向前兼容）。

    入站即校验：解析成功后过 validate_execution_report，非法值即使类型正确也拒绝。
    """
    if not isinstance(payload, Mapping):
        _fail("payload 必须为 Mapping", actual_type=type(payload).__name__)

    kwargs: dict[str, object] = {}
    missing: list[str] = []
    for f in fields(ExecutionReport):
        if f.name not in payload:
            if f.default is not MISSING:  # codegen 默认（algo_type/schema_version）
                continue
            missing.append(f.name)
            continue
        value = payload[f.name]
        if f.name in _DECIMAL_FIELDS:
            kwargs[f.name] = _coerce_decimal(f.name, value)
        elif f.name in _INT_FIELDS:
            if type(value) is not int:
                _fail(f"{f.name} 反序列化只接受 int", field=f.name, actual_type=type(value).__name__)
            kwargs[f.name] = value
        elif f.name in _FLOAT_FIELDS:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                _fail(f"{f.name} 反序列化只接受数值", field=f.name, actual_type=type(value).__name__)
            kwargs[f.name] = float(value)
        else:
            if not isinstance(value, str):
                _fail(f"{f.name} 反序列化只接受 str", field=f.name, actual_type=type(value).__name__)
            kwargs[f.name] = value
    if missing:
        _fail("payload 缺必填字段", missing=",".join(sorted(missing)))

    return validate_execution_report(ExecutionReport(**kwargs))


def report_net_cashflow(report: ExecutionReport) -> Decimal:
    """单笔报告净现金流（组合视角）：SELL=+（成交额−佣金），BUY=−（成交额+佣金）。"""
    gross = report.vwap_price * report.actual_quantity
    if report.direction == OrderSide.SELL.value:
        return gross - report.commission
    return -(gross + report.commission)


@runtime_checkable
class ExecutionReportSource(Protocol):
    """ExecutionReport 拉取口——A1③ 归因/TCA 消费方对接位（结构子类型，运行时可查）。"""

    def get_execution_report(self, order_id: str) -> ExecutionReport | None:
        """按委托 ID 取单笔执行报告（无则 None）。"""
        ...

    def iter_execution_reports(self, symbol: str, window_start: str, window_end: str) -> Iterable[ExecutionReport]:
        """按标的 + ISO 8601 UTC 窗口迭代执行报告（TCA/归因批处理入口）。"""
        ...


@runtime_checkable
class ExecutionReportDeltaExtractor(Protocol):
    """A8 mSPRT delta 提取对接位——签名对齐 pf_core ChampionChallengerDeltaExtractor 预留槽。"""

    def extract_delta(self, champion_report: ExecutionReport, challenger_report: ExecutionReport) -> float:
        """从配对执行报告（同标的同方向同窗口）提取逐笔 delta = challenger − champion。"""
        ...


class NetPnlDeltaExtractor:
    """默认 delta 提取实现：净现金流差（Fail-Closed 校验配对合法性）。"""

    def extract_delta(self, champion_report: ExecutionReport, challenger_report: ExecutionReport) -> float:
        if champion_report.symbol != challenger_report.symbol:
            _fail("配对报告 symbol 不一致", champion=champion_report.symbol, challenger=challenger_report.symbol)
        if champion_report.direction != challenger_report.direction:
            _fail(
                "配对报告 direction 不一致",
                champion=champion_report.direction,
                challenger=challenger_report.direction,
            )
        return float(report_net_cashflow(challenger_report) - report_net_cashflow(champion_report))


class ExecutionReportContract:
    """CTR-P1-007 契约门面——校验 + 序列化往返单一入口（无状态，全静态委托）。"""

    CONTRACT_ID: str = CONTRACT_ID
    SCHEMA_VERSION: str = SCHEMA_VERSION

    @staticmethod
    def validate(
        report: ExecutionReport,
        *,
        board_lot: int | None = None,
        price_limit_up: Decimal | None = None,
        price_limit_down: Decimal | None = None,
    ) -> ExecutionReport:
        return validate_execution_report(
            report, board_lot=board_lot, price_limit_up=price_limit_up, price_limit_down=price_limit_down
        )

    @staticmethod
    def to_payload(report: ExecutionReport) -> dict[str, object]:
        return execution_report_to_payload(report)

    @staticmethod
    def from_payload(payload: Mapping[str, object]) -> ExecutionReport:
        return execution_report_from_payload(payload)


__all__ = [
    "CONTRACT_ID",
    "DEFAULT_BOARD_LOT",
    "SCHEMA_VERSION",
    "ExecutionReportContract",
    "ExecutionReportContractError",
    "ExecutionReportDeltaExtractor",
    "ExecutionReportSource",
    "NetPnlDeltaExtractor",
    "execution_report_from_payload",
    "execution_report_to_payload",
    "report_net_cashflow",
    "validate_execution_report",
]
