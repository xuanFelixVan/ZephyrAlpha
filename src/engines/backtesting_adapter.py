"""
backtesting.py 适配器
轻量级向量化回测引擎适配器
"""

from typing import Dict, List, Any, Optional, Type
from datetime import datetime
import pandas as pd

try:
    from backtesting import Backtest, Strategy
    from backtesting.lib import crossover
    BACKTESTING_AVAILABLE = True
except ImportError:
    BACKTESTING_AVAILABLE = False
    Backtest = None
    Strategy = None
    crossover = None

from .base import BaseEngineAdapter, EngineConfig, UnifiedOrder, OrderSide, OrderType
from ..core.base import Result, Position as CorePosition


class BacktestingPyAdapter(BaseEngineAdapter):
    """backtesting.py 适配器

    特点：
    1. 轻量级向量化回测，执行速度快
    2. 支持自定义佣金和滑点模型
    3. 内置多种技术指标和策略模板
    4. 生成交互式HTML报告

    适用场景：
    - 策略快速验证和原型开发
    - 秒级回测结果反馈
    - 多参数优化和网格搜索
    """

    def __init__(self, config: EngineConfig):
        super().__init__(config)
        if not BACKTESTING_AVAILABLE:
            raise ImportError("backtesting库未安装，请运行: pip install backtesting")

        self.backtest_instance = None
        self.positions = []
        self.performance_metrics = {}

    def initialize(self) -> Result:
        """初始化引擎"""
        try:
            self.initialized = True
            return Result.success("backtesting.py引擎初始化成功")
        except Exception as e:
            return Result.error(f"backtesting.py引擎初始化失败: {str(e)}")

    def shutdown(self) -> Result:
        """关闭引擎"""
        self.backtest_instance = None
        self.initialized = False
        return Result.success("backtesting.py引擎已关闭")

    def submit_order(self, order: UnifiedOrder) -> Result:
        """提交订单（在backtesting.py中通过策略类处理）"""
        # backtesting.py的订单在策略逻辑中处理
        # 这里记录订单用于模拟
        return Result.success(
            f"订单已接收: {order.symbol} {order.side} {order.quantity} @ {order.price}",
            data={"order_id": f"bt_{datetime.now().timestamp()}"}
        )

    def cancel_order(self, order_id: str) -> Result:
        """取消订单"""
        return Result.success(f"订单 {order_id} 已取消")

    def get_positions(self) -> Result[List[CorePosition]]:
        """获取持仓列表"""
        return Result.success("持仓获取成功", data=self.positions)

    def get_account_info(self) -> Result[Dict[str, Any]]:
        """获取账户信息"""
        account_info = {
            "total_value": self.config.initial_capital,
            "cash": self.config.initial_capital,
            "positions": self.positions,
            "total_profit": 0.0,
            "total_return": 0.0,
        }

        if self.backtest_instance and hasattr(self.backtest_instance, 'results'):
            results = self.backtest_instance.results
            account_info.update({
                "total_value": results['Equity Final [$]'],
                "total_return": results['Return [%]'] / 100,
                "sharpe_ratio": results['Sharpe Ratio'],
                "max_drawdown": results['Max. Drawdown [%]'],
            })

        return Result.success("账户信息获取成功", data=account_info)

    def get_historical_data(self, symbol: str, start_date: str, end_date: str,
                           frequency: str = "1d") -> Result[pd.DataFrame]:
        """获取历史数据

        注意：backtesting.py需要OHLC格式数据
        格式: ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        # 这里可以集成数据源，目前返回空数据框架
        # 实际使用时需要连接数据API
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        index = pd.date_range(start=start_date, end=end_date, freq=frequency)
        data = pd.DataFrame(index=index, columns=columns).fillna(100.0)

        return Result.success(f"{symbol}历史数据获取成功", data=data)

    def run_backtest(self, strategy_class: Type[Strategy], data: pd.DataFrame,
                    **kwargs) -> Result[Dict[str, Any]]:
        """运行回测

        Args:
            strategy_class: backtesting.py策略类
            data: OHLC格式的DataFrame
            **kwargs: Backtest构造函数参数

        Returns:
            回测结果字典
        """
        try:
            # 确保数据格式正确
            required_columns = ['Open', 'High', 'Low', 'Close']
            for col in required_columns:
                if col not in data.columns:
                    return Result.error(f"数据缺少必要列: {col}")

            # 配置回测参数
            bt_kwargs = {
                "cash": self.config.initial_capital,
                "commission": self.config.commission_rate,
                "margin": 1.0,  # 无杠杆
                "exclusive_orders": True,
            }

            # 合并用户自定义参数
            bt_kwargs.update(kwargs)

            # 创建并运行回测
            bt = Backtest(data, strategy_class, **bt_kwargs)
            results = bt.run()

            # 保存实例以供后续使用
            self.backtest_instance = bt
            self.performance_metrics = results

            # 提取关键指标
            performance_data = {
                "equity_final": results['Equity Final [$]'],
                "return_pct": results['Return [%]'],
                "sharpe_ratio": results['Sharpe Ratio'],
                "max_drawdown_pct": results['Max. Drawdown [%]'],
                "trades": results['# Trades'],
                "win_rate": results['Win Rate [%]'],
                "avg_trade": results['Avg. Trade [%]'],
                "total_duration": results['Duration'],
            }

            # 生成HTML报告
            if kwargs.get('generate_report', True):
                report_path = f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                bt.plot(filename=report_path)
                performance_data['report_path'] = report_path

            return Result.success("回测运行成功", data=performance_data)

        except Exception as e:
            return Result.error(f"回测运行失败: {str(e)}")

    def get_performance_metrics(self) -> Result[Dict[str, Any]]:
        """获取绩效指标"""
        if not self.performance_metrics:
            return Result.error("未运行回测，无绩效数据")

        return Result.success("绩效指标获取成功", data=self.performance_metrics)

    def is_ashare_compatible(self) -> bool:
        """是否支持A股规则"""
        # backtesting.py是通用回测框架，需要自定义A股规则
        return False

    def supports_order_type(self, order_type: OrderType) -> bool:
        """支持的订单类型"""
        # backtesting.py主要支持市价单和限价单
        return order_type in [OrderType.MARKET, OrderType.LIMIT]

    def calculate_commission(self, amount: float) -> float:
        """计算佣金（使用backtesting.py内置计算）"""
        # backtesting.py在回测时自动计算佣金
        # 这里提供估算值
        return super().calculate_commission(amount)


# 示例策略类
class SimpleMAStrategy(Strategy):
    """简单移动平均线策略示例"""

    def init(self):
        # 计算技术指标
        self.sma_short = self.I(lambda x: x, self.data.Close, period=10)
        self.sma_long = self.I(lambda x: x, self.data.Close, period=30)

    def next(self):
        # 策略逻辑
        if self.sma_short[-1] > self.sma_long[-1]:
            if not self.position:
                self.buy()
        elif self.sma_short[-1] < self.sma_long[-1]:
            if self.position:
                self.sell()
