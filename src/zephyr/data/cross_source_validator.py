# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cross_source_validator
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer
# [CONSUMERS] zephyr.data.scheduler.run_schedule("cross_validation")
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只校验不阻断; 结果写入 cross_validation_log 表; 使用 ch_reader 查询
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->log warning+返回空报告; 无数据->返回空报告
# [TESTS] tests/zephyr/data/test_cross_source_validator.py
# [A_module] module_id=MOD-GOV-cross_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



多源交叉校验器——比较 QMT 主源与 TDX 备源 tick 数据一致性（P1-4）。

升级 integrity_checker 从行数阈值校验到内容级多源比对：
  1. 价格偏差: |price_qmt - price_tdx| / price_tdx < threshold
  2. 成交量偏差: |volume_qmt - volume_tdx| / max(volume_tdx, 1) < threshold
  3. 缺失标的: 主源有但备源无（或反之），标记 missing

校验结果写入 c1_market.cross_validation_log 表，供后续分析。

用法::

    from zephyr.data.cross_source_validator import CrossSourceValidator
    validator = CrossSourceValidator()
    report = validator.validate(time_window_minutes=5)
    print(report)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: price_threshold 参数
#   fields: 参数 price_threshold（无注解）
#   code: cross_source_validator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: volume_threshold 参数
#   fields: 参数 volume_threshold（无注解）
#   code: cross_source_validator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ValidationReport
#   name_en: ValidationReport
#   intro: 交叉校验报告。
#   desc: 交叉校验报告。；公共方法（定义序）: is_healthy, summary；源码 L118-L141
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② CrossSourceValidator
#   name_en: CrossSourceValidator
#   intro: 多源交叉校验器——QMT 主源 vs TDX 备源 tick 数据比对。
#   desc: 多源交叉校验器——QMT 主源 vs TDX 备源 tick 数据比对。 校验逻辑： 1. 查询最近 N 分钟 tick_data 表，按 symbol+data_source…；公共方法（定义序）: validate…
#   inputs: price_threshold volume_threshold
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ValidationReport, CrossSourceValidator
#   downstream: zephyr.data.scheduler.run_schedule("cross_validation")
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from decimal import Decimal

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024，P2-3）
_TBL_TICK = get_registry().table("market_tick")
_TBL_CROSS_VALIDATION_LOG = get_registry().table("market_cross_validation_log")

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
# 查询最近 N 分钟内每个 symbol+data_source 的最新 price/volume
_SQL_LATEST_PER_SOURCE = """
SELECT symbol, data_source,
       argMax(price, timestamp) as last_price,
       argMax(volume, timestamp) as last_volume
FROM {tick_table}
WHERE timestamp >= now() - INTERVAL {minutes} MINUTE
  AND data_source IN ('miniqmt', 'tdx_backup')
GROUP BY symbol, data_source
"""

# 写入校验日志
_SQL_INSERT_LOG = f"""
INSERT INTO {_TBL_CROSS_VALIDATION_LOG}
(check_time, check_date, symbol, metric, primary_value, backup_value,
 deviation, threshold, status, detail)
VALUES
"""

# 默认阈值
_PRICE_THRESHOLD = Decimal("0.001")  # 0.1% 价格偏差
_VOLUME_THRESHOLD = Decimal("0.05")  # 5% 成交量偏差


@dataclass
class ValidationReport:
    """交叉校验报告。"""

    check_time: datetime.datetime
    total_symbols: int = 0
    passed: int = 0
    warnings: int = 0
    failures: int = 0
    missing_in_backup: int = 0
    missing_in_primary: int = 0
    details: list[dict] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """是否健康（无 fail）。"""
        return self.failures == 0

    def summary(self) -> str:
        return (
            f"CrossValidation(symbols={self.total_symbols}, "
            f"pass={self.passed}, warn={self.warnings}, fail={self.failures}, "
            f"missing_backup={self.missing_in_backup}, "
            f"missing_primary={self.missing_in_primary})"
        )


class CrossSourceValidator:
    """多源交叉校验器——QMT 主源 vs TDX 备源 tick 数据比对。

    校验逻辑：
    1. 查询最近 N 分钟 tick_data 表，按 symbol+data_source 聚合最新 price/volume
    2. 对每个有两源数据的 symbol，计算价格/成交量偏差
    3. 标记仅出现在一源的 symbol 为 missing
    4. 结果写入 cross_validation_log 表
    """

    def __init__(
        self,
        price_threshold: Decimal = _PRICE_THRESHOLD,
        volume_threshold: Decimal = _VOLUME_THRESHOLD,
    ) -> None:
        self._price_threshold = price_threshold
        self._volume_threshold = volume_threshold

    def validate(self, time_window_minutes: int = 5) -> ValidationReport:
        """执行交叉校验。

        Args:
            time_window_minutes: 查询最近 N 分钟的数据（默认 5 分钟）

        Returns:
            ValidationReport 校验报告
        """
        report = ValidationReport(check_time=datetime.datetime.now())

        # 查询 ClickHouse
        raw = ch_reader.query(_SQL_LATEST_PER_SOURCE.format(tick_table=_TBL_TICK, minutes=time_window_minutes))
        if not raw or not raw.strip():
            log.info("交叉校验: 最近 %d 分钟无 tick 数据", time_window_minutes)
            return report

        # 解析查询结果: {symbol: {source: (price, volume)}}
        source_data: dict[str, dict[str, tuple[Decimal, int]]] = {}
        for line in raw.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            symbol, data_source, price_str, vol_str = parts[0], parts[1], parts[2], parts[3]
            try:
                price = Decimal(price_str)
                volume = int(vol_str)
            except (ValueError, TypeError):
                continue
            source_data.setdefault(symbol, {})[data_source] = (price, volume)

        report.total_symbols = len(source_data)

        # 逐 symbol 比对
        log_entries: list[str] = []
        for symbol, sources in source_data.items():
            primary = sources.get("miniqmt")
            backup = sources.get("tdx_backup")

            if primary and backup:
                # 两源都有 → 比对价格和成交量
                self._compare_price(symbol, primary, backup, report, log_entries)
                self._compare_volume(symbol, primary, backup, report, log_entries)
            elif primary and not backup:
                report.missing_in_backup += 1
                self._add_log_entry(
                    log_entries,
                    symbol,
                    "missing",
                    str(primary[0]),
                    "N/A",
                    Decimal("1"),
                    Decimal("0"),
                    "warn",
                    "备源缺失此标的",
                )
                report.warnings += 1
            elif backup and not primary:
                report.missing_in_primary += 1
                self._add_log_entry(
                    log_entries,
                    symbol,
                    "missing",
                    "N/A",
                    str(backup[0]),
                    Decimal("1"),
                    Decimal("0"),
                    "fail",
                    "主源缺失此标的",
                )
                report.failures += 1

        # 写入校验日志
        if log_entries:
            self._write_log(log_entries)

        log.info("交叉校验完成: %s", report.summary())
        return report

    def _compare_price(
        self,
        symbol: str,
        primary: tuple[Decimal, int],
        backup: tuple[Decimal, int],
        report: ValidationReport,
        log_entries: list[str],
    ) -> None:
        """比较价格偏差。"""
        p_price, _ = primary
        b_price, _ = backup
        if b_price == 0:
            return  # 备源价格为 0 跳过

        deviation = abs(p_price - b_price) / b_price
        status = "pass"
        if deviation > self._price_threshold:
            status = "fail"
            report.failures += 1
        else:
            report.passed += 1

        self._add_log_entry(
            log_entries,
            symbol,
            "price",
            str(p_price),
            str(b_price),
            deviation,
            self._price_threshold,
            status,
            f"价格偏差 {deviation:.4%}" if status != "pass" else "",
        )

    def _compare_volume(
        self,
        symbol: str,
        primary: tuple[Decimal, int],
        backup: tuple[Decimal, int],
        report: ValidationReport,
        log_entries: list[str],
    ) -> None:
        """比较成交量偏差。"""
        _, p_vol = primary
        _, b_vol = backup
        if b_vol == 0:
            return

        deviation = Decimal(abs(p_vol - b_vol)) / Decimal(b_vol)
        status = "pass"
        if deviation > self._volume_threshold:
            status = "warn"
            report.warnings += 1
        else:
            report.passed += 1

        self._add_log_entry(
            log_entries,
            symbol,
            "volume",
            str(p_vol),
            str(b_vol),
            deviation,
            self._volume_threshold,
            status,
            f"成交量偏差 {deviation:.4%}" if status != "pass" else "",
        )

    @staticmethod
    def _add_log_entry(
        entries: list[str],
        symbol: str,
        metric: str,
        primary_val: str,
        backup_val: str,
        deviation: Decimal,
        threshold: Decimal,
        status: str,
        detail: str,
    ) -> None:
        """构造一行 INSERT VALUES 并加入列表。"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.date.today().isoformat()
        # 转义单引号
        detail_escaped = detail.replace("'", "\\'")
        entries.append(
            f"(now(), '{today}', '{symbol}', '{metric}', "
            f"'{primary_val}', '{backup_val}', "
            f"{deviation}, {threshold}, '{status}', '{detail_escaped}')"
        )

    @staticmethod
    def _write_log(entries: list[str]) -> None:
        """将校验日志写入 ClickHouse。"""
        from zephyr.data import ch_writer

        sql = _SQL_INSERT_LOG + ",\n".join(entries)
        try:
            ch_writer.query(sql)
        except Exception as e:  # noqa: BLE001
            log.warning("写入 cross_validation_log 失败: %s", e)
