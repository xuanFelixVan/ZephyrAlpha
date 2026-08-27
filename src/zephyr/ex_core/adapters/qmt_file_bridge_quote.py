# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.adapters.qmt_file_bridge_quote
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.signal_providers
# [CONSUMERS] zephyr.ex_core.trading_session; scripts.start_paper_session
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 尾部读取(64KB窗口); 残行跳过回退上一行; 新鲜度以文件mtime判定
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] QmtFileBridgeQuoteError
# [TESTS] tests/ex_core/adapters/test_qmt_file_bridge_quote.py
# [A_module] module_id=MOD-L06-002-QMTFQ | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT File Bridge Quote Provider——反向文件桥行情适配器

职责:
  - 读取 QMT 沙箱策略(ZEPHYR_QUOTE v15)写入的 quote.csv
  - 尾部读取(每 tick 追加一行，只取每个 symbol 最新一行)
  - 提供 5 档盘口快照 + PriceProvider 可调用对象(供 TradingSession 注入)
  - 新鲜度检测: 文件 mtime 超过阈值视为行情中断

约束:
  - 纯文件轮询，无网络连接
  - QMT 写端无锁，末行可能残缺 -> 跳过并回退上一行
  - 双环境物理隔离: env="real"(实盘) / env="sim"(模拟)

SSoT: docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Final

from zephyr.shared.utils.time_utils import now_utc

_logger = logging.getLogger(__name__)

# quote.csv 列数: symbol,lastPrice,open,high,low,lastClose,volume,amount,
# bid1..5, ask1..5, bidVol1..5, askVol1..5, timetag  => 8+5+5+5+5+1 = 29 列
_EXPECTED_COLUMNS: Final[int] = 29

# 尾部读取窗口（字节）。一行约 200B，64KB 覆盖 ~300 行，足够找到所有 symbol 的最新行
_TAIL_WINDOW: Final[int] = 64 * 1024


class QmtFileBridgeQuoteError(Exception):
    """QMT 文件桥行情错误"""

    error_code = "ZA-XC-QMTFQ"


@dataclass(frozen=True)
class QuoteSnapshot:
    """单标的行情快照（5档）"""

    symbol: str
    last_price: Decimal
    open: Decimal
    high: Decimal
    low: Decimal
    last_close: Decimal
    volume: int
    amount: Decimal
    bid_prices: tuple[Decimal, ...]  # 5 档买价
    ask_prices: tuple[Decimal, ...]  # 5 档卖价
    bid_vols: tuple[int, ...]  # 5 档买量
    ask_vols: tuple[int, ...]  # 5 档卖量
    timetag: str  # QMT 原始时间戳（格式不定，仅展示用）
    file_mtime: datetime  # 文件修改时间（新鲜度判定用）

    @property
    def bid1(self) -> Decimal:
        return self.bid_prices[0]

    @property
    def ask1(self) -> Decimal:
        return self.ask_prices[0]


class QmtFileBridgeQuoteProvider:
    """反向文件桥行情 Provider

    Usage:
        provider = QmtFileBridgeQuoteProvider(env="sim")
        provider.connect()

        snap = provider.get_quote("510300.SH")       # 5档快照
        price_fn = provider.make_price_provider()     # 注入 TradingSession
        prices = price_fn(["510300.SH"])
    """

    ENV_CONFIG: Final[dict[str, dict[str, str]]] = {
        "real": {
            "quote_file": r"E:\qmt_bridge\quote.csv",
        },
        "sim": {
            "quote_file": r"E:\qmt_bridge_sim\quote.csv",
        },
    }

    def __init__(self, env: str = "sim", stale_seconds: float = 10.0):
        """初始化

        Args:
            env: 环境标识 "real"(实盘) 或 "sim"(模拟)
            stale_seconds: 新鲜度阈值（秒），文件 mtime 超过该值视为行情中断
        """
        if env not in self.ENV_CONFIG:
            raise QmtFileBridgeQuoteError(f"非法环境标识: {env}，必须是 'real' 或 'sim'")

        self._env = env
        self._quote_file = Path(self.ENV_CONFIG[env]["quote_file"])
        self._stale_seconds = stale_seconds
        self._connected = False

    @property
    def provider_id(self) -> str:
        return f"qmt_file_quote_{self._env}"

    def connect(self) -> bool:
        """校验行情文件存在（QMT 端策略启动后由 init 创建）"""
        if not self._quote_file.exists():
            raise QmtFileBridgeQuoteError(
                f"行情文件不存在: {self._quote_file}，"
                f"请确认 QMT 端 ZEPHYR_QUOTE v15 策略已启动"
            )
        self._connected = True
        _logger.info(
            "QmtFileBridgeQuoteProvider connected env=%s file=%s",
            self._env, self._quote_file,
        )
        return True

    def is_fresh(self) -> bool:
        """行情是否新鲜（文件 mtime 在阈值内）"""
        if not self._quote_file.exists():
            return False
        age = now_utc().timestamp() - self._quote_file.stat().st_mtime
        return age <= self._stale_seconds

    def get_quote(self, symbol: str) -> QuoteSnapshot | None:
        """获取单标的最新快照

        Returns:
            QuoteSnapshot；文件不存在/无该标的/数据残破时返回 None
        """
        quotes = self.get_quotes([symbol])
        return quotes.get(symbol)

    def get_quotes(self, symbols: list[str]) -> dict[str, QuoteSnapshot]:
        """批量获取最新快照（一次尾读，多标的共享）"""
        if not self._quote_file.exists():
            return {}

        lines = self._read_tail_lines()
        if not lines:
            return {}

        mtime = datetime.fromtimestamp(self._quote_file.stat().st_mtime)
        wanted = set(symbols)
        result: dict[str, QuoteSnapshot] = {}

        # 从尾向头扫描，每个 symbol 取第一条完整行（即最新行）
        for line in reversed(lines):
            if not wanted:
                break
            row = line.strip().split(",")
            if len(row) != _EXPECTED_COLUMNS:
                continue  # 残行/表头行跳过
            sym = row[0]
            if sym not in wanted or sym == "symbol":
                continue
            snap = self._parse_row(row, mtime)
            if snap is not None:
                result[sym] = snap
                wanted.discard(sym)

        return result

    def make_price_provider(self):
        """生成 TradingSession 兼容的 PriceProvider 可调用对象

        新鲜度检查: 行情中断时返回空 dict（调用方按缺价处理，不会用错价下单）
        """
        def price_provider(symbols: list[str]) -> dict[str, Decimal]:
            if not self.is_fresh():
                _logger.warning(
                    "行情不新鲜(file=%s, stale_seconds=%s)，返回空价格",
                    self._quote_file, self._stale_seconds,
                )
                return {}
            quotes = self.get_quotes(symbols)
            return {sym: snap.last_price for sym, snap in quotes.items()}

        return price_provider

    def get_order_book(self, symbol: str) -> dict | None:
        """获取 5 档盘口（兼容 order_book 组件的 dict 形态）"""
        snap = self.get_quote(symbol)
        if snap is None:
            return None
        return {
            "symbol": snap.symbol,
            "bid_prices": list(snap.bid_prices),
            "ask_prices": list(snap.ask_prices),
            "bid_vols": list(snap.bid_vols),
            "ask_vols": list(snap.ask_vols),
            "last_price": snap.last_price,
            "timetag": snap.timetag,
        }

    # ── 内部方法 ──

    def _read_tail_lines(self) -> list[str]:
        """尾部窗口读取（避免全日文件增大后全量扫描）"""
        try:
            size = self._quote_file.stat().st_size
            with open(self._quote_file, "rb") as f:
                if size > _TAIL_WINDOW:
                    f.seek(-_TAIL_WINDOW, 2)  # SEEK_END
                raw = f.read()
            text = raw.decode("ascii", errors="ignore")
            lines = text.split("\n")
            # 若文件大于窗口，首行必然残缺，丢弃
            if size > _TAIL_WINDOW and lines:
                lines = lines[1:]
            return [ln for ln in lines if ln.strip()]
        except OSError as e:
            _logger.warning("读取行情文件失败: %r", e)
            return []

    @staticmethod
    def _parse_row(row: list[str], mtime: datetime) -> QuoteSnapshot | None:
        """解析一行 29 列 CSV，转换失败返回 None"""
        try:
            dec = _to_decimal
            ints = _to_int
            return QuoteSnapshot(
                symbol=row[0],
                last_price=dec(row[1]),
                open=dec(row[2]),
                high=dec(row[3]),
                low=dec(row[4]),
                last_close=dec(row[5]),
                volume=ints(row[6]),
                amount=dec(row[7]),
                bid_prices=tuple(dec(v) for v in row[8:13]),
                ask_prices=tuple(dec(v) for v in row[13:18]),
                bid_vols=tuple(ints(v) for v in row[18:23]),
                ask_vols=tuple(ints(v) for v in row[23:28]),
                timetag=row[28],
                file_mtime=mtime,
            )
        except (InvalidOperation, ValueError, IndexError) as e:
            _logger.debug("行情行解析失败: %r row=%s", e, row[:3])
            return None


def _to_decimal(s: str) -> Decimal:
    """安全 Decimal 转换，失败返回 0"""
    try:
        return Decimal(s.strip())
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _to_int(s: str) -> int:
    """安全 int 转换（容忍 float 字符串），失败返回 0"""
    try:
        return int(float(s.strip()))
    except (ValueError, OverflowError):
        return 0
