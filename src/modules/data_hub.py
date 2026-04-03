"""
数据中心模块 (DataHub)
提供统一的数据访问接口，支持市场数据、基本面数据和股票列表查询

技术层次: Layer 0 - 数据访问层 | 业务架构: 三级时间框架融合架构

使用方式:
    from src.modules.data_hub import DataHub
    
    hub = DataHub()
    ohlcv = hub.get_ohlcv("000001.SZ", "2026-01-01", "2026-01-31")
    symbols = hub.list_symbols("A")

状态说明:
    ⚠️ 当前为占位符实现 (v5.1阶段)
    - 返回示例数据用于开发和测试
    - 生产环境需要连接真实数据源 (AKShare/Tushare等)
    - 完整实现见开发路线图 Phase 2

数据源集成规划:
    ✅ AKShare: 免费数据源 (A股、港股、美股、期货、期权)
    ✅ Tushare: 专业数据源 (需要Token)
    ⏳ 同花顺iFind: 机构数据源 (需要授权)
    ⏳ Wind: 金融终端数据 (需要授权)
"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from src.core.exceptions import DataException, ValidationException

logger = logging.getLogger(__name__)


class IDataHub(ABC):
    """数据中心接口 (抽象基类)

    索引: API.DH.001
    技术层次: Layer 0 - 数据访问层 | 业务架构: 三级时间框架融合架构
    上游: 数据源(AKShare/Tushare)
    下游: FactorCalculator, Monitor
    状态: 规划中 (v5.1阶段占位符实现)
    """

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """获取OHLCV数据
        
        Args:
            symbol: 股票代码，如 "000001.SZ"
            start_date: 开始日期，格式 "YYYY-MM-DD"
            end_date: 结束日期，格式 "YYYY-MM-DD"
            fields: 可选字段列表，如 ["open", "high", "low", "close", "volume"]
            
        Returns:
            pandas.DataFrame: OHLCV数据，索引为日期
            
        Raises:
            ValidationException: 参数验证失败
            DataException: 数据获取失败
        """
        pass

    @abstractmethod
    def get_fundamental(
        self,
        symbol: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取基本面数据
        
        Args:
            symbol: 股票代码
            fields: 可选字段列表
            
        Returns:
            Dict[str, Any]: 基本面数据字典
        """
        pass

    @abstractmethod
    def list_symbols(self, market: str = "A") -> List[str]:
        """获取股票列表
        
        Args:
            market: 市场代码，"A"表示A股，"HK"表示港股，"US"表示美股
            
        Returns:
            List[str]: 股票代码列表
        """
        pass


class DataHub(IDataHub):
    """数据中心实现 (占位符版本)
    
    当前返回示例数据，用于开发和测试。
    生产环境需要连接真实数据源。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化DataHub
        
        Args:
            config: 配置字典，支持以下键:
                - data_source: 数据源类型 ("akshare", "tushare", "mock")
                - cache_enabled: 是否启用缓存 (默认True)
                - max_retries: 最大重试次数 (默认3)
        """
        self.config = config or {}
        self.data_source = self.config.get("data_source", "mock")
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.max_retries = self.config.get("max_retries", 3)
        
        logger.info(f"DataHub初始化完成，数据源: {self.data_source}")
    
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """获取OHLCV数据 (占位符实现)
        
        当前返回示例数据，模拟20个交易日的OHLCV数据。
        生产环境需要替换为真实数据源调用。
        """
        # 参数验证
        if not symbol or not start_date or not end_date:
            raise ValidationException("symbol, start_date, end_date不能为空")
        
        logger.debug(f"获取OHLCV数据: {symbol}, {start_date} 到 {end_date}")
        
        # 生成示例数据
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValidationException(f"日期格式错误: {e}")
        
        # 生成20个交易日数据
        dates = pd.date_range(start=start_dt, end=end_dt, freq='D')
        if len(dates) > 20:
            dates = dates[:20]  # 限制数据量
        
        # 生成随机但合理的OHLCV数据
        np.random.seed(42)  # 固定随机种子以保证可重复性
        n_days = len(dates)
        
        # 基础价格序列 (随机游走)
        base_price = 100.0
        returns = np.random.normal(0.001, 0.02, n_days)  # 日收益率
        price_series = base_price * np.cumprod(1 + returns)
        
        # 生成OHLCV
        data = []
        for i in range(n_days):
            close_price = price_series[i]
            open_price = close_price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.005)))
            volume = np.random.randint(1000000, 10000000)
            
            data.append({
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=dates)
        
        # 如果指定了字段，则过滤
        if fields:
            available_fields = ['open', 'high', 'low', 'close', 'volume']
            valid_fields = [f for f in fields if f in available_fields]
            if valid_fields:
                df = df[valid_fields]
        
        logger.info(f"生成示例OHLCV数据: {symbol}, 形状: {df.shape}")
        return df
    
    def get_fundamental(
        self,
        symbol: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取基本面数据 (占位符实现)
        
        当前返回示例基本面数据。
        生产环境需要连接真实财务数据源。
        """
        if not symbol:
            raise ValidationException("symbol不能为空")
        
        logger.debug(f"获取基本面数据: {symbol}")
        
        # 示例基本面数据
        fundamental_data = {
            "symbol": symbol,
            "pe_ratio": round(np.random.uniform(10, 30), 2),  # 市盈率
            "pb_ratio": round(np.random.uniform(1, 5), 2),    # 市净率
            "roe": round(np.random.uniform(0.05, 0.25), 4),   # 净资产收益率
            "dividend_yield": round(np.random.uniform(0.01, 0.05), 4),  # 股息率
            "market_cap": np.random.randint(10_000_000_000, 100_000_000_000),  # 市值
            "debt_to_equity": round(np.random.uniform(0.3, 1.5), 2),  # 负债权益比
            "current_ratio": round(np.random.uniform(1.0, 3.0), 2),   # 流动比率
            "revenue_growth": round(np.random.uniform(-0.1, 0.3), 4), # 营收增长率
            "net_profit_growth": round(np.random.uniform(-0.2, 0.4), 4),  # 净利润增长率
            "update_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # 如果指定了字段，则过滤
        if fields:
            result = {k: v for k, v in fundamental_data.items() if k in fields}
            # 确保symbol始终包含
            if "symbol" not in result:
                result["symbol"] = symbol
            return result
        
        return fundamental_data
    
    def list_symbols(self, market: str = "A") -> List[str]:
        """获取股票列表 (占位符实现)
        
        当前返回示例股票列表。
        生产环境需要从交易所或数据源获取实时列表。
        """
        logger.debug(f"获取股票列表，市场: {market}")
        
        # 示例股票列表
        if market == "A":
            symbols = [
                "000001.SZ",  # 平安银行
                "000002.SZ",  # 万科A
                "000858.SZ",  # 五粮液
                "600519.SH",  # 贵州茅台
                "600036.SH",  # 招商银行
                "000333.SZ",  # 美的集团
                "002415.SZ",  # 海康威视
                "300750.SZ",  # 宁德时代
                "601318.SH",  # 中国平安
                "601888.SH",  # 中国中免
            ]
        elif market == "HK":
            symbols = [
                "00700.HK",  # 腾讯控股
                "00941.HK",  # 中国移动
                "01299.HK",  # 友邦保险
                "02318.HK",  # 中国平安
                "03988.HK",  # 中国银行
            ]
        elif market == "US":
            symbols = [
                "AAPL",   # Apple
                "MSFT",   # Microsoft
                "GOOGL",  # Alphabet
                "AMZN",   # Amazon
                "TSLA",   # Tesla
            ]
        else:
            symbols = []
            logger.warning(f"不支持的市场代码: {market}")
        
        logger.info(f"返回股票列表，市场: {market}, 数量: {len(symbols)}")
        return symbols


# 全局单例实例（可选）
_default_datahub = None

def get_default_datahub() -> DataHub:
    """获取默认的DataHub实例（单例模式）"""
    global _default_datahub
    if _default_datahub is None:
        _default_datahub = DataHub()
    return _default_datahub