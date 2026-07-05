# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.ifind_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] iFinDPy SDK (THS_iFinDLogin/THS_BasicData/THS_Trans2DataFrame)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] connect() 从 IFIND_LICENSE 环境变量读 license；配额错误码-4318/-4309 透传不重试
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常→yield FetchResult(error=str)；配额耗尽→yield error 并 return
# [TESTS] tests/zephyr/data/test_providers.py::TestIFindHelpers
# [A_module] module_id=MOD-L00-004-ifind_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IFindProvider 实现（MOD-L00-004 §4.3 数据源集成器）。

封装同花顺 iFinDPy SDK，继承 DataSourceBase，提供日频估值等数据拉取能力。

支持的能力（capability，通过 payload.extra["capability"] 路由）：
- daily_valuation: 日频估值（PE/PB/PS/PCF），写入 c1_market.daily_valuation

设计要点：
- THS_iFinDLogin / THS_BasicData 等在方法内部 import，避免模块加载时就要求 iFinDPy 安装
- 月度配额错误码 -4318/-4309 直接透传给上层（配额耗尽重试无意义，不在 retry_on 中）
- THS_BasicData 调用经基类 _call_with_policy 包裹，自动限流 + 重试
- license_key 从环境变量 IFIND_LICENSE 读取
"""
from __future__ import annotations

import os
import time
import logging
from typing import Iterator

from ..provider_base import DataSourceBase, FetchPayload, FetchResult, DataSourceMeta
from ..policy_registry import SourcePolicy


class IFindProvider(DataSourceBase):
    """同花顺 iFind 数据源 Provider。

    通过 iFinDPy SDK 拉取 A 股估值/K线/资金流等数据。
    认证方式：license_key（环境变量 IFIND_LICENSE）。
    线程安全模型：thread_local（每个线程需独立登录）。
    """

    source_name: str = "ifind"
    meta: DataSourceMeta = DataSourceMeta(
        name="ifind",
        display_name="同花顺 iFind",
        auth_type="license_key",
        requires_process=False,
        thread_safety="thread_local",
        rate_limit_default=0,
        capabilities=["kline_daily", "daily_valuation", "money_flow", "index_kline"],
        known_issues=["月度配额-4318", "试用账号不支持沪深港通"],
    )

    # iFind 估值指标串（PE/PB/PS/PCF_TTM）
    _VALUATION_INDICATORS = "ths_pe_stock;ths_pb_stock;ths_ps_stock;ths_pcf_stock_ttm"
    # iFind 估值参数模板（100=静态），4 个指标对应 4 段参数
    _VALUATION_PARAM_TEMPLATE = "{date},100;{date},100;{date},100;{date},100"

    # 估值表列顺序
    _VALUATION_COLUMNS = ["trade_date", "symbol", "pe_ttm", "pb_mrq", "ps_ttm", "pcf_ncf_ttm"]
    # 估值目标表
    _VALUATION_TABLE = "c1_market.daily_valuation"

    # 每批 yield 的行数上限
    _BATCH_SIZE = 500

    def __init__(self):
        super().__init__()
        # THS_iFinDLogin 的返回值，供诊断/重登判断
        self._login_result: int | None = None

    # ============== 连接 / 登出 ==============

    def connect(self) -> None:
        """登录 iFind：从环境变量读取 license_key，调用 THS_iFinDLogin。

        成功（返回 0 或正数）则置 _connected=True；失败（负数）抛 RuntimeError。
        login 返回值存入 self._login_result 供后续诊断。

        Raises:
            RuntimeError: license_key 缺失或登录返回负数错误码。
        """
        from iFinDPy import THS_iFinDLogin

        license_key = os.environ.get("IFIND_LICENSE")
        if not license_key:
            raise RuntimeError("环境变量 IFIND_LICENSE 未设置，无法登录 iFind")

        self._log.info("正在登录 iFind ...")
        result = THS_iFinDLogin(license_key)
        self._login_result = result

        # 0 或正数表示成功，负数表示失败
        if isinstance(result, (int, float)) and result < 0:
            self._connected = False
            raise RuntimeError(f"iFind 登录失败，错误码: {result}")

        self._connected = True
        self._log.info(f"iFind 登录成功，返回值: {result}")

    def health_check(self) -> bool:
        """探活：用 000001.SZ 的 PE 查询做心跳。

        不抛异常即视为健康（iFind 错误码以异常或 dict 形式返回时被捕获）。

        Returns:
            True 表示连接可用。
        """
        if not self._connected:
            return False
        try:
            from iFinDPy import THS_BasicData
            THS_BasicData("000001.SZ", "ths_pe_stock", "2024-12-31,100")
            return True
        except Exception as e:
            self._log.warning(f"iFind 健康检查失败: {e}")
            return False

    def disconnect(self) -> None:
        """登出 iFind。即使登出抛异常也标记为已断开。"""
        try:
            from iFinDPy import THS_iFinDLogout
            THS_iFinDLogout()
            self._log.info("iFind 已登出")
        except Exception as e:
            self._log.warning(f"iFind 登出异常（已忽略）: {e}")
        finally:
            self._connected = False

    # ============== 数据拉取 ==============

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按策略拉取数据，根据 payload.extra["capability"] 路由到具体子方法。

        Args:
            payload: 下载请求，extra["capability"] 决定走哪个子方法。
            policy: 调用策略（限流/重试）。

        Yields:
            FetchResult: 分批结果或错误结果。
        """
        extra = payload.extra or {}
        capability = extra.get("capability")

        if capability == "daily_valuation":
            yield from self._fetch_daily_valuation(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"未知 capability: {capability}",
            )

    def _fetch_daily_valuation(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取日频估值（PE/PB/PS/PCF），写入 c1_market.daily_valuation。

        输入：
            payload.symbols: ts_code 列表，如 ["000001.SZ","000002.SZ"]
            payload.extra["snapshot_dates"]: 日期字符串列表，如 ["2024-12-31","2024-06-30"]

        输出列顺序: ["trade_date","symbol","pe_ttm","pb_mrq","ps_ttm","pcf_ncf_ttm"]
        每 500 行 yield 一个 FetchResult；last_key 为当前处理的 date。

        遇到配额耗尽（-4318/-4309）或其他 iFind 错误码时，yield 错误结果并 return。
        """
        from iFinDPy import THS_BasicData, THS_Trans2DataFrame

        symbols = payload.symbols or []
        extra = payload.extra or {}
        snapshot_dates = extra.get("snapshot_dates", [])

        if not symbols or not snapshot_dates:
            yield FetchResult(
                table=self._VALUATION_TABLE,
                columns=self._VALUATION_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="symbols 或 snapshot_dates 为空",
            )
            return

        batch_rows: list[tuple] = []
        start_ts = time.time()

        for date in snapshot_dates:
            params = self._VALUATION_PARAM_TEMPLATE.format(date=date)

            for ts_code in symbols:
                # 调用 SDK（自动限流 + 重试）
                try:
                    raw = self._call_with_policy(
                        THS_BasicData, policy,
                        ts_code, self._VALUATION_INDICATORS, params,
                    )
                except Exception as e:
                    self._log.error(f"THS_BasicData 调用异常 {ts_code}@{date}: {e}")
                    yield FetchResult(
                        table=self._VALUATION_TABLE,
                        columns=self._VALUATION_COLUMNS,
                        rows=[],
                        last_key=date,
                        elapsed_sec=time.time() - start_ts,
                        error=str(e),
                    )
                    return

                # 检查 iFind 错误码（配额耗尽等），错误则终止
                is_error, code, msg = self._check_ifind_error(raw)
                if is_error:
                    if code in (-4318, -4309):
                        err_msg = f"iFind配额耗尽: {code}"
                    else:
                        err_msg = f"iFind错误: {code} {msg}".strip()
                    self._log.error(f"{ts_code}@{date} {err_msg}")
                    yield FetchResult(
                        table=self._VALUATION_TABLE,
                        columns=self._VALUATION_COLUMNS,
                        rows=[],
                        last_key=date,
                        elapsed_sec=time.time() - start_ts,
                        error=err_msg,
                    )
                    return

                # 转换为 DataFrame
                try:
                    df = THS_Trans2DataFrame(raw)
                except Exception as e:
                    self._log.warning(f"THS_Trans2DataFrame 失败 {ts_code}@{date}: {e}")
                    continue

                # 从 DataFrame 提取 4 个指标值
                pe = pb = ps = pcf = None
                try:
                    if df is not None and len(df) > 0:
                        row = df.iloc[0]
                        pe = self.safe_float(row.get("ths_pe_stock"))
                        pb = self.safe_float(row.get("ths_pb_stock"))
                        ps = self.safe_float(row.get("ths_ps_stock"))
                        pcf = self.safe_float(row.get("ths_pcf_stock_ttm"))
                except Exception as e:
                    self._log.warning(f"提取指标值失败 {ts_code}@{date}: {e}")

                symbol = self._ts_code_to_symbol(ts_code)
                batch_rows.append((date, symbol, pe, pb, ps, pcf))

                # 每 500 行 yield 一次
                if len(batch_rows) >= self._BATCH_SIZE:
                    yield FetchResult(
                        table=self._VALUATION_TABLE,
                        columns=self._VALUATION_COLUMNS,
                        rows=batch_rows[:],
                        last_key=date,
                        elapsed_sec=time.time() - start_ts,
                    )
                    batch_rows.clear()
                    start_ts = time.time()

            # 当前 date 处理完，yield 剩余行（避免跨 date 拼批）
            if batch_rows:
                yield FetchResult(
                    table=self._VALUATION_TABLE,
                    columns=self._VALUATION_COLUMNS,
                    rows=batch_rows[:],
                    last_key=date,
                    elapsed_sec=time.time() - start_ts,
                )
                batch_rows.clear()
                start_ts = time.time()

    # ============== 辅助方法 ==============

    @staticmethod
    def _ts_code_to_symbol(ts_code: str) -> str:
        """ts_code 转纯代码：'000001.SZ' → '000001'。

        Args:
            ts_code: iFind 标的代码，格式 'XXXXXX.SZ/SH/BJ'。

        Returns:
            点号前的部分；输入为空则返回空串。
        """
        if not ts_code:
            return ""
        return ts_code.split(".")[0]

    @staticmethod
    def safe_float(v) -> float | None:
        """安全转 float，失败或 NaN 返回 None。

        Args:
            v: 待转换值（str/float/int/None 等）。

        Returns:
            float 值或 None。
        """
        if v is None:
            return None
        try:
            f = float(v)
        except (TypeError, ValueError):
            return None
        # NaN 视为 None
        if f != f:
            return None
        return f

    def _check_ifind_error(self, raw) -> tuple[bool, int | None, str]:
        """检查 iFind 返回值是否含错误码。

        iFind 错误返回通常为 dict，含 errorcode/errcode 等键。
        常见错误码：
            -4318 / -4309: 月度配额耗尽
            -201: 通用失败

        Args:
            raw: THS_BasicData 的返回值。

        Returns:
            (is_error, code, msg): 是否错误 / 错误码 / 错误消息。
        """
        if not isinstance(raw, dict):
            return (False, None, "")

        # 兼容多种错误码键名
        code = None
        for key in ("errorcode", "errcode", "error_code", "code"):
            if key in raw:
                try:
                    code = int(raw[key])
                except (TypeError, ValueError):
                    code = raw[key]
                break

        if code is None:
            return (False, None, "")

        # 错误消息
        msg = ""
        for key in ("errmsg", "errormsg", "error_msg", "message", "msg"):
            if key in raw:
                msg = str(raw[key])
                break

        # 负数错误码视为错误
        if isinstance(code, int) and code < 0:
            return (True, code, msg)
        # 字符串形态的负数错误码
        if isinstance(code, str) and code.strip().startswith("-"):
            try:
                return (True, int(code), msg)
            except ValueError:
                pass

        return (False, code, msg)
