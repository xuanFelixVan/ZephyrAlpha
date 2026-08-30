# [BLUEPRINT] MOD-L00-006 | docs/03_modules/_domain_data/wal_codec_blueprint.md
# [MODULE] zephyr.data.normalizers.ohlcv_normalizer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.normalizers.normalizer_base
# [CONSUMERS] zephyr.data.normalizers.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 输出 schema 恒为 7 列键（symbol/trade_date/open/high/low/close/amount 可选缺席）；按 (symbol, trade_date) 排序；同键去重 keep-last；负价/负量/high<low 剔除
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 字段缺失/类型不可转/日期不可解析 → 剔除该记录并记 issue（不中断整批）
# [TESTS] tests/zephyr/data/test_normalizers.py
# [A_module] module_id=MOD-L00-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
OHLCV 归一化器（MOD-L00-006 具体实现①）。

行情日线记录统一 schema：列名归一（常见别名→canonical）→ 类型强转
（价格/成交量 float，日期 ISO 串）→ 校验剔除（必需字段缺失/负价/负量/
high<low/日期不可解析）→ (symbol, trade_date) 排序 + 同键去重（keep-last，
后到的修正记录覆盖先到的）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ohlcv_normalizer.py
# 层: 算法
# - id: A1
#   name_zh: ① OhlcvNormalizer
#   name_en: OhlcvNormalizer
#   intro: OHLCV 记录归一化器。
#   desc: OHLCV 记录归一化器。；公共方法（定义序）: name, normalize；源码 L104-L154
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: OhlcvNormalizer
#   downstream: zephyr.data.normalizers.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
from typing import Final

from zephyr.data.normalizers.normalizer_base import DataNormalizer, NormalizeResult

__all__: Final = ["OhlcvNormalizer"]

#: 列名别名 → canonical（小写后匹配；A 股数据源常见变体）
_COLUMN_ALIASES: Final = {
    "日期": "trade_date",
    "date": "trade_date",
    "trade_date": "trade_date",
    "代码": "symbol",
    "code": "symbol",
    "symbol": "symbol",
    "开盘": "open",
    "open": "open",
    "最高": "high",
    "high": "high",
    "最低": "low",
    "low": "low",
    "收盘": "close",
    "close": "close",
    "成交量": "volume",
    "volume": "volume",
    "vol": "volume",
    "成交额": "amount",
    "amount": "amount",
}

_REQUIRED: Final = ("trade_date", "open", "high", "low", "close", "volume")
_FLOAT_FIELDS: Final = ("open", "high", "low", "close", "volume", "amount")


def _parse_date(value: object) -> str:
    """日期归一为 ISO 串（YYYY-MM-DD）。接受 date/datetime/ISO 串/YYYYMMDD 串。"""
    if isinstance(value, datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    s = str(value).strip()
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    # 先按 ISO 解析校验（容忍时间部分）
    try:
        return datetime.date.fromisoformat(s[:10]).isoformat()
    except ValueError:
        raise ValueError(f"日期不可解析: {value!r}") from None


class OhlcvNormalizer(DataNormalizer):
    """OHLCV 记录归一化器。"""

    @property
    def name(self) -> str:
        return "ohlcv"

    def normalize(self, records: list[dict]) -> NormalizeResult:
        kept: list[dict] = []
        issues: list[str] = []
        for idx, raw in enumerate(records):
            try:
                rec = self._normalize_one(raw)
            except ValueError as e:
                issues.append(f"row{idx}: {e}")
                continue
            kept.append(rec)
        kept.sort(key=lambda r: (r.get("symbol", ""), r["trade_date"]))
        # 同 (symbol, trade_date) 去重 keep-last（排序后稳定：后到覆盖先到）
        deduped: dict[tuple[str, str], dict] = {}
        for rec in kept:
            deduped[(rec.get("symbol", ""), rec["trade_date"])] = rec
        dropped_dupes = len(kept) - len(deduped)
        if dropped_dupes > 0:
            issues.append(f"dedup: {dropped_dupes} 条同键记录 keep-last 去重")
        out = tuple(deduped.values())
        return NormalizeResult(records=out, dropped=len(records) - len(out), issues=tuple(issues))

    def _normalize_one(self, raw: dict) -> dict:
        rec: dict = {}
        for k, v in raw.items():
            canon = _COLUMN_ALIASES.get(str(k).strip().lower())
            if canon is not None:
                rec[canon] = v
        missing = [f for f in _REQUIRED if f not in rec]
        if missing:
            raise ValueError(f"必需字段缺失: {missing}")
        rec["trade_date"] = _parse_date(rec["trade_date"])
        if "symbol" in rec:
            rec["symbol"] = str(rec["symbol"]).strip()
        for f in _FLOAT_FIELDS:
            if f in rec:
                try:
                    rec[f] = float(rec[f])
                except (TypeError, ValueError):
                    raise ValueError(f"字段 {f} 类型不可转: {rec[f]!r}") from None
        if min(rec["open"], rec["high"], rec["low"], rec["close"]) < 0 or rec["volume"] < 0:
            raise ValueError("负价/负量")
        if rec["high"] < rec["low"]:
            raise ValueError(f"high<low: {rec['high']}<{rec['low']}")
        return rec
