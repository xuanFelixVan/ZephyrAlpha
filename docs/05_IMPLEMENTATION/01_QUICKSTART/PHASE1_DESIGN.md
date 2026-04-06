---
module_id: IMPL_QUICKSTART_PHASE1_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 扩展功能、辅助模块
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 实施标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---
---


# Phase 1 详细设计：Backtrader回测框架
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 - 第一个可运行的回测框�?

---

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────�?
�?                    回测框架架构                             �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ┌─────────────�?    ┌─────────────�?    ┌─────────────�? �?
�? �? 数据获取    �?──�?�? 策略执行    �?──�?�? 回测报告    �? �?
�? �?DataLoader  �?    �?Cerebro     �?    �?Analyzer    �? �?
�? └─────────────�?    └─────────────�?    └─────────────�? �?
�?        �?                  �?                  �?         �?
�?        �?                  �?                  �?         �?
�? ┌─────────────�?    ┌─────────────�?    ┌─────────────�? �?
�? �?数据缓存    �?    �? 风控规则    �?    �? 可视�?    �? �?
�? �?Cache       �?    �?RiskManager �?    �?Matplotlib  �? �?
�? └─────────────�?    └─────────────�?    └─────────────�? �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

### 1.2 模块关系

```
DataLoader �?Strategy �?Cerebro �?Broker �?Analyzer �?Report
                              �?
                              �?
                        RiskManager
```

---

## 2. 目录结构

```
ZephyrAlpha/
├── config/
�?  └── backtest.yaml              # 回测配置
├── src/
�?  ├── __init__.py
�?  ├── main.py                    # 主入�?
�?  ├── modules/
�?  �?  ├── __init__.py
�?  �?  ├── dataloader.py          # 数据加载�?�?
�?  �?  ├── strategies/
�?  �?  �?  ├── __init__.py
�?  �?  �?  └── s001_ma_cross.py   # 均线交叉策略 �?
�?  �?  ├── analyzers/
�?  �?  �?  ├── __init__.py
�?  �?  �?  └── performance.py     # 绩效分析 �?
�?  �?  └── risk/
�?          ├── __init__.py
�?          └── rules.py           # 风控规则 �?
├── data/
�?  └── raw/                       # 原始数据
├── output/
�?  └── backtest/                  # 回测输出
└── tests/
    └── test_backtest.py           # 测试
```

---

## 3. 核心模块代码

### 3.1 主入�?(main.py)

```python
"""
清风量化系统 v5.0 - 回测主入�?
"""
import argparse
import logging
from datetime import datetime

import backtrader as bt

from src.modules.dataloader import StockDataLoader
from src.modules.strategies.s001_ma_cross import MaCrossStrategy
from src.modules.analyzers.performance import setup_analyzers
from src.modules.risk.rules import RiskManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='清风量化回测系统')

    parser.add_argument('--code', type=str, default='000001.SZ',
                        help='股票代码')
    parser.add_argument('--start', type=str, default='2024-01-01',
                        help='开始日�?)
    parser.add_argument('--end', type=str, default='2024-12-31',
                        help='结束日期')
    parser.add_argument('--capital', type=float, default=100000.0,
                        help='初始资金')
    parser.add_argument('--commission', type=float, default=0.0003,
                        help='佣金费率')
    parser.add_argument('--fast', type=int, default=10,
                        help='快速均线周�?)
    parser.add_argument('--slow', type=int, default=30,
                        help='慢速均线周�?)

    return parser.parse_args()


def run_backtest(args):
    """运行回测"""
    logger.info(f"开始回�?- 股票:{args.code} 日期:{args.start}~{args.end}")

    # 1. 创建Cerebro引擎
    cerebro = bt.Cerebro()

    # 2. 设置初始资金和佣�?
    cerebro.broker.setcash(args.capital)
    cerebro.broker.setcommission(commission=args.commission)

    # 3. 添加策略
    cerebro.addstrategy(
        MaCrossStrategy,
        fast_period=args.fast,
        slow_period=args.slow
    )

    # 4. 加载数据
    data_loader = StockDataLoader()
    data = data_loader.load(
        code=args.code,
        start=args.start,
        end=args.end
    )
    cerebro.adddata(data)

    # 5. 添加分析�?
    setup_analyzers(cerebro)

    # 6. 添加风控
    cerebro.addriskmanager(RiskManager)

    # 7. 运行回测
    logger.info(f'初始资金: {cerebro.broker.getvalue():.2f}')

    results = cerebro.run()

    # 8. 输出结果
    final_value = cerebro.broker.getvalue()
    logger.info(f'最终资�? {final_value:.2f}')
    logger.info(f'总收益率: {(final_value - args.capital) / args.capital * 100:.2f}%')

    return results, final_value


if __name__ == '__main__':
    args = parse_args()
    run_backtest(args)
```

---

### 3.2 数据加载�?(dataloader.py)

```python
"""
数据加载�?- 支持多种数据�?
"""
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import backtrader as bt
import akshare as ak

logger = logging.getLogger(__name__)


class StockDataFrameData(bt.feeds.PandasData):
    """自定义数据格�?""

    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', -1),
    )


class StockDataLoader:
    """
    股票数据加载�?

    支持数据�?
    1. akshare (免费)
    2. tushare (需要token)
    3. 本地CSV
    """

    def __init__(self, cache_dir: str = 'data/raw'):
        self.cache_dir = cache_dir

    def load(self, code: str, start: str, end: str) -> StockDataFrameData:
        """
        加载股票数据

        Args:
            code: 股票代码，如 '000001.SZ'
            start: 开始日�?'YYYY-MM-DD'
            end: 结束日期 'YYYY-MM-DD'

        Returns:
            Backtrader格式的数�?
        """
        # 尝试从本地加�?
        df = self._load_from_cache(code, start, end)

        if df is None:
            # 从网络获�?
            logger.info(f"从akshare获取数据: {code}")
            df = self._fetch_from_akshare(code, start, end)
            self._save_to_cache(df, code)

        # 转换为Backtrader格式
        return self._to_backtrader_data(df)

    def _fetch_from_akshare(self, code: str, start: str, end: str) -> pd.DataFrame:
        """从akshare获取数据"""
        try:
            # 统一股票日线行情
            df = ak.stock_zh_a_hist(
                symbol=code.split('.')[0],
                period='daily',
                start_date=start.replace('-', ''),
                end_date=end.replace('-', ''),
                adjust='qfq'  # 前复�?
            )

            # 重命名列
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'turnover']

            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # 按日期排�?
            df = df.sort_index()

            logger.info(f"获取数据成功: {len(df)}�?)

            return df

        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            raise

    def _load_from_cache(self, code: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """从本地缓存加�?""
        import os
        cache_file = os.path.join(self.cache_dir, f"{code.replace('.', '_')}.csv")

        if os.path.exists(cache_file):
            try:
                df = pd.read_csv(cache_file, index_col='date', parse_dates=True)
                df = df[start:end]
                if len(df) > 0:
                    logger.info(f"从缓存加载数�? {len(df)}�?)
                    return df
            except Exception as e:
                logger.warning(f"缓存读取失败: {e}")

        return None

    def _save_to_cache(self, df: pd.DataFrame, code: str):
        """保存到本地缓�?""
        import os
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_file = os.path.join(self.cache_dir, f"{code.replace('.', '_')}.csv")
        df.to_csv(cache_file)
        logger.info(f"数据已缓�? {cache_file}")

    def _to_backtrader_data(self, df: pd.DataFrame) -> StockDataFrameData:
        """转换为Backtrader格式"""
        # 确保列名正确
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"数据缺少必要�? {col}")

        return StockDataFrameData(dataname=df)
```

---

### 3.3 均线交叉策略 (s001_ma_cross.py)

```python
"""
均线交叉策略 - s001

策略说明:
- 金叉买入(快速均线上穿慢速均�?
- 死叉卖出(快速均线下穿慢速均�?

参数:
- fast_period: 快速均线周�?默认10)
- slow_period: 慢速均线周�?默认30)
"""
import backtrader as bt
import logging

logger = logging.getLogger(__name__)


class MaCrossStrategy(bt.Strategy):
    """
    均线交叉策略

    买入条件:
    - 快速均线上穿慢速均�?金叉)

    卖出条件:
    - 快速均线下穿慢速均�?死叉)
    """

    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('printlog', True),
    )

    def __init__(self):
        """初始化策略指�?""
        # 创建均线指标
        self.fast_ma = bt.ind.SMA(
            self.data.close,
            period=self.params.fast_period,
            plotname='Fast MA'
        )
        self.slow_ma = bt.ind.SMA(
            self.data.close,
            period=self.params.slow_period,
            plotname='Slow MA'
        )

        # 创建交叉信号
        self.crossover = bt.ind.CrossOver(self.fast_ma, self.slow_ma)

        # 订单跟踪
        self.order = None
        self.buy_price = None
        self.buy_comm = None

    def log(self, txt, dt=None):
        """日志输出"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            logger.info(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行, 价格: {order.executed.price:.2f}, '
                         f'成本: {order.executed.value:.2f}, '
                         f'手续�? {order.executed.comm:.2f}')
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            else:
                self.log(f'卖出执行, 价格: {order.executed.price:.2f}, '
                         f'成本: {order.executed.value:.2f}, '
                         f'手续�? {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单被拒�?取消')

        self.order = None

    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return

        self.log(f'交易利润, 毛利�? {trade.pnl:.2f}, '
                 f'净利润: {trade.pnl - trade.commission:.2f}')

    def next(self):
        """每个bar执行一�?""
        # 检查是否有待处理订�?
        if self.order:
            return

        # 检查是否持�?
        if not self.position:
            # 金叉买入
            if self.crossover > 0:
                self.log(f'买入信号, 价格: {self.data.close[0]:.2f}')
                self.order = self.buy()

        else:
            # 死叉卖出
            if self.crossover < 0:
                self.log(f'卖出信号, 价格: {self.data.close[0]:.2f}')
                self.order = self.sell()

    def stop(self):
        """策略结束时调�?""
        self.log(f'策略停止, 快速均线周�? {self.params.fast_period}, '
                 f'慢速均线周�? {self.params.slow_period}', dt=None)
```

---

### 3.4 绩效分析�?(performance.py)

```python
"""
绩效分析�?- Backtrader分析器集�?
"""
import backtrader as bt


def setup_analyzers(cerebro):
    """
    配置回测分析�?

    添加以下分析:
    1. 收益统计
    2. 回撤分析
    3. 交易记录
    4. 夏普比率
    """

    # 收益分析
    cerebro.addanalyzer(
        bt.analyzers.Returns,
        _name='returns'
    )

    # 回撤分析
    cerebro.addanalyzer(
        bt.analyzers.DrawDown,
        _name='drawdown'
    )

    # 夏普比率
    cerebro.addanalyzer(
        bt.analyzers.SharpeRatio,
        _name='sharpe',
        timeframe=bt.TimeFrame.Days,
        riskfreerate=0.03,
        annualize=True
    )

    # 交易统计
    cerebro.addanalyzer(
        bt.analyzers.TradeAnalyzer,
        _name='trades'
    )

    #  annualized return
    cerebro.addanalyzer(
        bt.analyzers.AnnualReturn,
        _name='annual'
    )

    # SQN (System Quality Number)
    cerebro.addanalyzer(
        bt.analyzers.SQN,
        _name='sqn'
    )


def print_analyzer_results(strategy):
    """打印分析结果"""
    print("\n" + "=" * 60)
    print("回测分析报告")
    print("=" * 60)

    # 获取分析器结�?
    results = {}

    try:
        results['returns'] = strategy.analyzers.returns.get_analysis()
    except:
        pass

    try:
        results['drawdown'] = strategy.analyzers.drawdown.get_analysis()
    except:
        pass

    try:
        results['sharpe'] = strategy.analyzers.sharpe.get_analysis()
    except:
        pass

    try:
        results['trades'] = strategy.analyzers.trades.get_analysis()
    except:
        pass

    try:
        results['sqn'] = strategy.analyzers.sqn.get_analysis()
    except:
        pass

    # 打印收益
    print("\n【收益指标�?)
    if 'returns' in results:
        print(f"  总收益率: {results['returns'].get('rtot', 0) * 100:.2f}%")
        print(f"  年化收益�? {results['returns'].get('rnorm100', 0):.2f}%")

    # 打印回撤
    print("\n【回撤指标�?)
    if 'drawdown' in results:
        print(f"  最大回�? {results['drawdown'].get('max', {}).get('drawdown', 0):.2f}%")
        print(f"  最大回撤时�? {results['drawdown'].get('max', {}).get('len', 0)}�?)

    # 打印夏普比率
    print("\n【风险指标�?)
    if 'sharpe' in results:
        sharpe = results['sharpe'].get('sharperatio', None)
        if sharpe is not None and not str(sharpe).lower() == 'nan':
            print(f"  夏普比率: {sharpe:.2f}")

    # 打印交易统计
    print("\n【交易统计�?)
    if 'trades' in results:
        ta = results['trades']
        print(f"  总交易次�? {ta.get('total', {}).get('total', 0)}")
        print(f"  盈利交易: {ta.get('won', {}).get('total', 0)}")
        print(f"  亏损交易: {ta.get('lost', {}).get('total', 0)}")

        if ta.get('won', {}).get('total', 0) > 0:
            print(f"  胜率: {ta['won']['total'] / ta['total']['total'] * 100:.2f}%")

        if 'pnl' in ta:
            print(f"  平均盈利: {ta['pnl']['gross']['average']:.2f}")
            print(f"  平均亏损: {ta['pnl']['loss']['average']:.2f}")

    # 打印SQN
    print("\n【系统质量�?)
    if 'sqn' in results:
        sqn = results['sqn'].get('sqn', 0)
        print(f"  SQN: {sqn:.2f}")
        print(f"  SQN评级: {get_sqn_rating(sqn)}")

    print("=" * 60)


def get_sqn_rating(sqn):
    """SQN评级"""
    if sqn >= 2.0:
        return "★★★★�?优秀"
    elif sqn >= 1.5:
        return "★★★★�?良好"
    elif sqn >= 1.0:
        return "★★★☆�?一�?
    elif sqn >= 0.5:
        return "★★☆☆�?较差"
    else:
        return "★☆☆☆�?很差"
```

---

### 3.5 风控规则 (rules.py)

```python
"""
风控规则管理�?

实现简单的风控规则:
1. 单笔交易限额
2. 最大持仓比�?
3. 日内止损
"""
import backtrader as bt
import logging

logger = logging.getLogger(__name__)


class RiskManager(bt.RiskRules):
    """
    风控规则管理�?

    在每次交易前检�?
    1. 订单金额不超过总资产的一定比�?
    2. 持仓比例不超过限�?
    3. 当日亏损超过阈值时禁止开新仓
    """

    params = (
        ('max_position_pct', 0.2),      # 最大持仓比�?0%
        ('max_single_trade_pct', 0.1),  # 单笔交易最大比�?0%
        ('daily_loss_limit_pct', 0.05), # 日内最大亏�?%
        ('printlog', True),
    )

    def __init__(self):
        self.daily_pnl = 0.0
        self.daily_start_value = None

    def start(self):
        """策略开�?""
        self.daily_start_value = self.broker.getvalue()
        logger.info(f"风控启动, 初始资金: {self.daily_start_value:.2f}")

    def stop(self):
        """策略结束"""
        logger.info("风控停止")

    def _check_position_limit(self, order):
        """检查持仓限�?""
        total_value = self.broker.getvalue()
        position_value = abs(order.executed.value if order.executed else 0)
        position_pct = position_value / total_value if total_value > 0 else 0

        if position_pct > self.params.max_position_pct:
            logger.warning(f"持仓比例 {position_pct:.2%} 超过限制 {self.params.max_position_pct:.2%}")
            return False
        return True

    def _check_single_trade_limit(self, order):
        """检查单笔交易限�?""
        if not order.executed:
            return True

        total_value = self.broker.getvalue()
        trade_value = abs(order.executed.value)
        trade_pct = trade_value / total_value if total_value > 0 else 0

        if trade_pct > self.params.max_single_trade_pct:
            logger.warning(f"单笔交易 {trade_pct:.2%} 超过限制 {self.params.max_single_trade_pct:.2%}")
            return False
        return True

    def _check_daily_loss_limit(self):
        """检查日内亏损限�?""
        current_value = self.broker.getvalue()

        if self.daily_start_value:
            daily_pnl_pct = (current_value - self.daily_start_value) / self.daily_start_value

            if daily_pnl_pct < -self.params.daily_loss_limit_pct:
                logger.warning(
                    f"日内亏损 {daily_pnl_pct:.2%} 超过限制 {self.params.daily_loss_limit_pct:.2%}, "
                    f"禁止开新仓"
                )
                return False

        return True

    def risk(self, order):
        """风控检�?""
        # 检查单笔交�?
        if not self._check_single_trade_limit(order):
            return order.reject()

        # 检查日内亏�?
        if not self._check_daily_loss_limit():
            return order.reject()

        return order.accept()
```

---

## 4. 配置文件 (config/backtest.yaml)

```yaml
# 回测配置
backtest:
  # 数据源配�?
  data_source:
    type: akshare  # akshare / tushare / csv
    cache_dir: data/raw
    adjust: qfq  # qfq(前复�? / hfq(后复�? / none(不复�?

  # 回测参数
  parameters:
    initial_capital: 100000.0      # 初始资金
    commission: 0.0003             # 佣金费率
    stamp_duty: 0.001              # 印花税率(卖出时收�?

  # 策略配置
  strategies:
    - id: s001
      name: 均线交叉策略
      enabled: true
      params:
        fast_period: 10
        slow_period: 30

  # 风控配置
  risk:
    max_position_pct: 0.2          # 最大持�?0%
    max_single_trade_pct: 0.1     # 单笔交易最�?0%
    daily_loss_limit_pct: 0.05    # 日内最大亏�?%

  # 输出配置
  output:
    dir: output/backtest
    save_trades: true
    save_equity: true
    generate_report: true
```

---

## 5. 运行脚本

### 5.1 命令行运�?

```bash
# 基本运行
python src/main.py --code 000001.SZ --start 2024-01-01 --end 2024-12-31

# 自定义参�?
python src/main.py \
    --code 000001.SZ \
    --start 2024-01-01 \
    --end 2024-12-31 \
    --capital 200000 \
    --fast 5 \
    --slow 20

# 高杠杆测�?
python src/main.py --code 000001.SZ --commission 0.001
```

### 5.2 输出示例

```
2024-03-29 10:00:00 - __main__ - INFO - 开始回�?- 股票:000001.SZ 日期:2024-01-01~2024-12-31
2024-03-29 10:00:00 - __main__ - INFO - 初始资金: 100000.00
2024-03-29 10:00:01 - __main__ - INFO - 最终资�? 125000.00
2024-03-29 10:00:01 - __main__ - INFO - 总收益率: 25.00%

============================================================
回测分析报告
============================================================

【收益指标�?
  总收益率: 25.00%
  年化收益�? 25.00%

【回撤指标�?
  最大回�? 8.50%
  最大回撤时�? 15�?

【风险指标�?
  夏普比率: 1.85

【交易统计�?
  总交易次�? 12
  盈利交易: 8
  亏损交易: 4
  胜率: 66.67%

【系统质量�?
  SQN: 1.95
  SQN评级: ★★★★�?良好

============================================================
```

---

## 6. 常见问题排查

### 问题1: 买入失败

```
可能原因:
1. 资金不足
2. 涨停股票无法买入
3. 风控规则拒绝

排查:
- 检查日志中的风控警�?
- 增加初始资金
- 调整风控参数
```

### 问题2: 收益为负

```
可能原因:
1. 震荡行情均线策略表现�?
2. 参数不适合当前股票
3. 手续费侵蚀利润

解决:
- 尝试不同周期的均线组�?
- 添加其他指标过滤
- 优化手续费设�?
```

### 问题3: 数据获取失败

```
可能原因:
1. 网络问题
2. akshare接口变更
3. 股票代码错误

解决:
- 检查网络连�?
- 更新akshare: pip install akshare --upgrade
- 使用正确的股票代码格�? 000001.SZ
```

---

## 7. 下一步学�?

学完Phase 1后，您可�?

1. **修改策略参数**: 尝试不同的均线周期组�?
2. **添加新策�?*: 在strategies目录创建新策�?
3. **学习因子选股**: 进入Phase 2

---

**最后更�?*: 2026-03-29
**版本**: v5.0
**前置文档**: [LEARNING_PATH.md](./LEARNING_PATH.md)
**下一步文�?*: [因子计算详细设计](./factor_design.md)
