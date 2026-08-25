# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [MODULE] zephyr.data.normalizers.format_transformer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.contracts.market_data
# [CONSUMERS] （P1 接线：scheduler/provider 落库前格式收口）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 记录级失败不抛错——隔离进 quarantined 留痕；输入记录不被修改；幂等键同输入同值；时间戳统一 UTC aware
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 schema 名→ValueError（fail-closed）；记录级校验失败→隔离不抛
# [TESTS] tests/zephyr/data/test_format_transformer.py
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Schema 驱动的多源格式转换器（CAND-DAT-010 / B1-00343 / D-INT-16 DataFormatTransformer）。

深挖裁定=做(P1)：normalizers 仅 normalizer_base/ohlcv_normalizer 骨架，
多格式（json/csv/parquet 行记录）与 Schema 映射验证未成组件。本模块收口：

1. Schema 驱动：``SCHEMA_REGISTRY`` 声明源字段→CTR-001 契约字段映射，
   pandera 式字段校验（必填/类型强转/值域，pandera 未装机故自实现轻量内核）。
2. 单位/时区归一：``scale`` 倍率（手→股、万元→元）；
   naive 时间戳按 ``source_tz`` 本地化后统一转 UTC aware。
3. 失败样本隔离：记录级失败不中断整批，进 ``quarantined`` 留痕，
   ``quarantine_report()`` 产出质量门控可消费的统计载荷。

与既有分工：normalizer_base 管"形状统一"（列名归一/排序去重），
本模块管"源格式→CTR-001 契约"的语义级转换；quality_gate 管质量判定，
本模块仅向其供给隔离样本，不替代判定。
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

from zephyr.shared.contracts.market_data import NormalizedMarketData

log = logging.getLogger(__name__)

__all__ = [
    "SCHEMA_REGISTRY",
    "FieldSpec",
    "FormatTransformer",
    "QuarantinedRecord",
    "SchemaSpec",
    "TransformIssue",
    "TransformResult",
]

_SYMBOL_PREFIX_RE = re.compile(r"^(sh|sz|bj)(\d{6})$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Schema 定义
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldSpec:
    """单字段映射与校验规则。

    Attributes:
        source: 源记录字段名
        target: 契约字段名
        dtype: decimal / int / str / datetime
        required: 必填（缺失即隔离）
        min_value: 下界（None=不校验）
        min_exclusive: 下界是否开区间（如价格 >0）
        scale: 单位归一倍率（手→股=100，万元→元=10000）
    """

    source: str
    target: str
    dtype: str
    required: bool = True
    min_value: Decimal | None = None
    min_exclusive: bool = False
    scale: Decimal = Decimal("1")


@dataclass(frozen=True)
class SchemaSpec:
    """源格式 → CTR-001 契约的映射 Schema。

    Attributes:
        name: schema 注册名
        fields: 字段规则（覆盖契约必填列：symbol/timestamp/open/high/low/close/volume）
        data_source: 契约 data_source 戳记
        source_tz: naive 时间戳的源时区（默认 Asia/Shanghai）
    """

    name: str
    fields: tuple[FieldSpec, ...]
    data_source: str
    source_tz: str = "Asia/Shanghai"


_OHLCV_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("symbol", "symbol", "str"),
    FieldSpec("timestamp", "timestamp", "datetime"),
    FieldSpec("open", "open", "decimal", min_value=Decimal("0"), min_exclusive=True),
    FieldSpec("high", "high", "decimal", min_value=Decimal("0"), min_exclusive=True),
    FieldSpec("low", "low", "decimal", min_value=Decimal("0"), min_exclusive=True),
    FieldSpec("close", "close", "decimal", min_value=Decimal("0"), min_exclusive=True),
    FieldSpec("volume", "volume", "decimal", min_value=Decimal("0")),
)

SCHEMA_REGISTRY: dict[str, SchemaSpec] = {
    # 通用 OHLCV（成交量=股）
    "ctr001_ohlcv": SchemaSpec(
        name="ctr001_ohlcv",
        fields=_OHLCV_FIELDS,
        data_source="format_transformer",
    ),
    # 成交量单位=手（×100 归一为股）
    "ctr001_ohlcv_hand": SchemaSpec(
        name="ctr001_ohlcv_hand",
        fields=tuple(
            FieldSpec(
                f.source,
                f.target,
                f.dtype,
                required=f.required,
                min_value=f.min_value,
                min_exclusive=f.min_exclusive,
                scale=Decimal("100") if f.target == "volume" else f.scale,
            )
            for f in _OHLCV_FIELDS
        ),
        data_source="format_transformer",
    ),
}


# ---------------------------------------------------------------------------
# 结果模型
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransformIssue:
    """单条校验失败留痕。"""

    index: int
    field: str
    reason: str
    raw: str


@dataclass(frozen=True)
class QuarantinedRecord:
    """被隔离的原始记录 + 失败原因集。"""

    index: int
    raw: Mapping[str, Any]
    issues: tuple[TransformIssue, ...]


@dataclass
class TransformResult:
    """转换输出：合格契约记录 + 隔离样本。"""

    schema: str
    records: list[NormalizedMarketData] = field(default_factory=list)
    quarantined: list[QuarantinedRecord] = field(default_factory=list)

    def quarantine_report(self, max_samples: int = 20) -> dict[str, Any]:
        """质量门控可消费的隔离统计载荷。"""
        return {
            "schema": self.schema,
            "total": len(self.records) + len(self.quarantined),
            "ok": len(self.records),
            "failed": len(self.quarantined),
            "samples": [
                {
                    "index": q.index,
                    "issues": [
                        {"field": i.field, "reason": i.reason, "raw": i.raw}
                        for i in q.issues
                    ],
                }
                for q in self.quarantined[:max_samples]
            ],
        }


# ---------------------------------------------------------------------------
# 转换器
# ---------------------------------------------------------------------------


class FormatTransformer:
    """Schema 驱动的源记录 → CTR-001 NormalizedMarketData 转换器。

    Usage::

        tf = FormatTransformer("ctr001_ohlcv")
        result = tf.transform(rows)          # rows: Iterable[Mapping]
        result.records                        # 合格契约记录
        result.quarantine_report()            # 隔离样本 → 质量门控
    """

    def __init__(self, schema: str | SchemaSpec) -> None:
        if isinstance(schema, SchemaSpec):
            self._spec = schema
        else:
            spec = SCHEMA_REGISTRY.get(schema)
            if spec is None:
                raise ValueError(
                    f"未知 schema: {schema!r}（已注册: {sorted(SCHEMA_REGISTRY)}）"
                )
            self._spec = spec
        self._tz = ZoneInfo(self._spec.source_tz)

    @property
    def schema(self) -> SchemaSpec:
        return self._spec

    # -- 主入口 ----------------------------------------------------------

    def transform(self, records: Iterable[Mapping[str, Any]]) -> TransformResult:
        """批量转换：合格进 records，失败隔离进 quarantined（不抛零散异常）。"""
        result = TransformResult(schema=self._spec.name)
        for idx, raw in enumerate(records):
            values, issues = self._validate_record(idx, raw)
            if issues:
                result.quarantined.append(
                    QuarantinedRecord(index=idx, raw=raw, issues=tuple(issues))
                )
                continue
            result.records.append(self._to_contract(values))
        return result

    # -- 校验 ------------------------------------------------------------

    def _validate_record(
        self, index: int, raw: Mapping[str, Any]
    ) -> tuple[dict[str, Any], list[TransformIssue]]:
        values: dict[str, Any] = {}
        issues: list[TransformIssue] = []
        for fspec in self._spec.fields:
            raw_val = raw.get(fspec.source)
            if raw_val is None or (isinstance(raw_val, str) and not raw_val.strip()):
                if fspec.required:
                    issues.append(
                        TransformIssue(index, fspec.target, "必填字段缺失", str(raw_val))
                    )
                continue
            val, err = self._coerce(fspec, raw_val)
            if err is not None:
                issues.append(TransformIssue(index, fspec.target, err, str(raw_val)))
                continue
            values[fspec.target] = val
        return values, issues

    def _coerce(self, fspec: FieldSpec, raw_val: Any) -> tuple[Any, str | None]:
        try:
            if fspec.dtype == "decimal":
                val = Decimal(str(raw_val).strip()) * fspec.scale
            elif fspec.dtype == "int":
                val = int(Decimal(str(raw_val).strip()) * fspec.scale)
            elif fspec.dtype == "datetime":
                return self._coerce_datetime(raw_val)
            else:
                val = str(raw_val).strip()
        except (InvalidOperation, ValueError, ArithmeticError):
            return None, f"类型强转失败（期望 {fspec.dtype}）"
        if fspec.min_value is not None and isinstance(val, (Decimal, int)):
            if fspec.min_exclusive and not val > fspec.min_value:
                return None, f"值域违例（须 >{fspec.min_value}）"
            if not fspec.min_exclusive and not val >= fspec.min_value:
                return None, f"值域违例（须 >={fspec.min_value}）"
        return val, None

    def _coerce_datetime(self, raw_val: Any) -> tuple[datetime | None, str | None]:
        if isinstance(raw_val, datetime):
            ts = raw_val
        else:
            text = str(raw_val).strip()
            parsed: datetime | None = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue
            if parsed is None:
                try:
                    parsed = datetime.fromisoformat(text)
                except ValueError:
                    return None, "类型强转失败（期望 datetime）"
            ts = parsed
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=self._tz)
        return ts.astimezone(timezone.utc), None

    # -- 契约装配 --------------------------------------------------------

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        m = _SYMBOL_PREFIX_RE.match(symbol)
        if m:
            return f"{m.group(2)}.{m.group(1).upper()}"
        return symbol.upper()

    def _to_contract(self, values: dict[str, Any]) -> NormalizedMarketData:
        symbol = self._normalize_symbol(values["symbol"])
        ts = values["timestamp"]
        idem = hashlib.md5(
            f"{self._spec.data_source}|{symbol}|{ts.isoformat()}".encode("utf-8")
        ).hexdigest()
        return NormalizedMarketData(
            symbol=symbol,
            timestamp=ts,
            open=values["open"],
            high=values["high"],
            low=values["low"],
            close=values["close"],
            volume=values["volume"],
            data_source=self._spec.data_source,
            idempotency_key=idem,
        )
