# T.09.AR002.系统架构参考

> A股量化交易系统架构与Tick数据仓库设计参考
>
> **来源**：量化策略专业分层方案_v3.0 附录AC/AN
>
> **说明**：本文档为架构愿景参考，个人开发者可分阶段实现，AI可据此生成具体代码

---

## 1. 系统架构概览

### 1.1 三阶段架构

```python
系统架构 = {
    '第一阶段(研究域)': '将投资思想转化为经过严格验证的、可部署的策略代码',
    '第二阶段(模拟交易)': '使用与实盘完全相同的交易API，接入实时或延迟行情',
    '第三阶段(实盘交易)': '统一交互入口 + AI增强工具'
}
```

### 1.2 个人开发者实现建议

| 阶段 | 内容 | 个人实现难度 | AI辅助 |
|------|------|-------------|--------|
| 第一阶段 | 研究域（数据/因子/回测） | ⭐⭐ 中 | ⭐⭐⭐⭐⭐ 高 |
| 第二阶段 | 模拟交易 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 高 |
| 第三阶段 | 实盘交易 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ 中 |

---

## 2. 数据平台架构

### 2.1 完整架构（企业级）

```python
数据平台架构 = {
    '数据采集层': {
        '功能': '多源对接（交易所、数据商、另类API）、实时流捕获、批量下载'
    },
    '数据处理层': {
        '核心': '核心中的核心',
        '清洗': '处理缺失、异常、停牌期',
        '对齐': '时间戳对齐、跨市场对齐',
        '计算': '实时计算标的复权价格、收益率、基础指标',
        '结构化': '生成标准格式的OHLCV、Level2快照、订单簿重建数据'
    },
    '数据存储层': {
        '时序数据库': '存储Tick、分钟、日级行情',
        '关系型数据库': '存储基本面、宏观、公司行为等结构化数据',
        '对象存储/数据湖': '存储非结构化另类数据、原始日志'
    },
    '数据服务层': {
        '功能': '提供统一的、高性能的API/SDK，供上层所有模块调用'
    }
}
```

### 2.2 个人开发者简化版

```python
个人数据平台 = {
    '数据采集层': 'AkShare/Baostock/EFinance API',
    '数据处理层': 'Pandas数据清洗和对齐',
    '数据存储层': {
        '日线数据': '本地CSV/Parquet',
        '分钟数据': '本地SQLite/Parquet',
        '财务数据': 'MySQL/CSV'
    },
    '数据服务层': 'Python函数封装'
}
```

---

## 3. 因子研究与策略开发平台

### 3.1 完整架构

```python
因子研究平台 = {
    '因子库': {
        '因子工厂': '技术指标、基本面因子、另类因子、组合因子的标准化实现与管理',
        '因子分析工具': '因子IC/IR分析、衰减分析、分层回测、可视化'
    },
    '策略IDE与研究环境': {
        '交互式分析': '集成Jupyter Notebook，支持Python/R',
        '策略模板': '事件驱动、向量化回测等多种模板',
        '版本控制集成': '代码与实验的Git管理'
    },
    '回测引擎': {
        '事件调度器': '驱动回测时间线',
        '订单管理器': '管理订单生命周期',
        '撮合模拟器': '模拟市场微观结构（滑点、冲击、佣金）',
        '组合账户管理器': '多资产、多策略的仓位与资金核算'
    },
    '策略分析平台': {
        '绩效分析器': '计算夏普、最大回撤等指标',
        '归因分析器': 'Brison模型、行业暴露、风格暴露分析',
        '可视化报告生成器': '自动生成PDF/HTML报告'
    }
}
```

### 3.2 清风量化系统已实现

| 模块 | 状态 | 文档位置 |
|------|------|----------|
| 因子库 | ✅ 已实现 | `factor-library/` |
| 因子分析工具 | ✅ 已实现 | `02_ALPHA_FACTORS/01_METHODOLOGY/` |
| 回测引擎 | ⚠️ 基础实现 | `03_BACKTEST/` |
| 绩效分析 | ✅ 已实现 | `T.06.PF001.Brinson归因.md` |

---

## 4. 研究资产管理系统

### 4.1 完整架构

```python
研究资产管理系统 = {
    '特征/因子库': '不仅仅是最终因子，包括所有测试过的特征版本',
    '模型仓库': '存储训练好的模型文件、超参数、性能指标',
    '研究结果存储': '结构化存储每次研究的输入、输出、配置',
    '实验数据版本': '记录研究使用的数据快照版本'
}
```

### 4.2 个人开发者建议

```python
个人研究管理 = {
    '因子版本': '使用Git管理，文件名包含版本号',
    '模型存储': '本地目录 + 模型卡片记录',
    '实验记录': 'Jupyter Notebook + 实验日志',
    '数据版本': '数据文件名包含日期版本'
}
```

---

## 5. Tick数据仓库架构

### 5.1 完整架构

```python
Tick数据仓库架构 = {
    '数据采集层': {
        '实时采集': '券商API / 交易所直连 / 数据商',
        '历史补录': '历史Tick数据导入',
        '格式转换': '原始二进制 → 结构化DataFrame'
    },
    '数据存储层': {
        '实时数据': 'Redis / Kafka',
        '历史Tick': 'ClickHouse / HDFS',
        '分钟数据': 'MySQL / ClickHouse',
        '日线数据': 'MySQL / CSV'
    },
    '数据服务层': {
        '实时API': 'gRPC / WebSocket',
        '历史查询': 'REST API',
        '计算服务': '因子计算 / 指标计算'
    }
}
```

### 5.2 个人开发者建议

```python
个人Tick处理 = {
    '数据来源': 'AkShare分钟数据（可接受）',
    '存储方案': 'Parquet文件按日期存储',
    '查询方式': 'pandas直接读取',
    '升级路径': '未来可迁移到ClickHouse'
}
```

### 5.3 ClickHouse建表（企业级参考）

```sql
-- Tick数据表
CREATE TABLE tick_data (
    stock_code String,
    timestamp DateTime64(3),
    price Float64,
    open Float64,
    high Float64,
    low Float64,
    volume Float64,
    amount Float64,
    bid_price1 Float64,
    bid_volume1 Float64,
    ask_price1 Float64,
    ask_volume1 Float64,
    total_bid_volume Float64,
    total_ask_volume Float64,
    order_imbalance Float64,
    spread Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (stock_code, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- 分钟K线聚合表
CREATE TABLE minute_kline (
    stock_code String,
    minute_start DateTime,
    minute_end DateTime,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,
    amount Float64,
    tick_count UInt32,
    avg_spread Float64,
    avg_imbalance Float64
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(minute_start)
ORDER BY (stock_code, minute_start);
```

---

## 6. Tick数据采集器（参考实现）

### 6.1 企业级实现

```python
class TickDataCollector:
    """
    Tick数据采集器（企业级）
    """

    def __init__(self, broker_config):
        self.broker = BrokerAdapter(broker_config)
        self.kafka_producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def start_realtime_collection(self, stock_list):
        """
        启动实时采集
        """
        for stock in stock_list:
            self.broker.subscribe(stock, self.on_tick_received)

    def on_tick_received(self, tick_data):
        """
        Tick数据回调
        """
        formatted = self.format_tick(tick_data)
        self.kafka_producer.send('tick_data', formatted)
        self.update_redis(formatted)

    def format_tick(self, tick_data):
        """
        格式化Tick数据
        """
        return {
            'stock_code': tick_data['code'],
            'timestamp': tick_data['time'],
            'price': tick_data['last_price'],
            'open': tick_data['open_price'],
            'high': tick_data['high_price'],
            'low': tick_data['low_price'],
            'volume': tick_data['volume'],
            'amount': tick_data['amount'],
            'bid_price1': tick_data['bid1'],
            'bid_volume1': tick_data['bid_vol1'],
            'ask_price1': tick_data['ask1'],
            'ask_volume1': tick_data['ask_vol1'],
            'total_bid_volume': sum(tick_data[f'bid_vol{i}'] for i in range(1, 6)),
            'total_ask_volume': sum(tick_data[f'ask_vol{i}'] for i in range(1, 6)),
        }
```

### 6.2 个人开发者简化实现

```python
class SimpleTickCollector:
    """
    简化版Tick数据采集（个人开发者）
    使用AkShare获取分钟数据
    """

    def __init__(self):
        self.akshare = None

    def get_minute_data(self, stock_code: str, period: str = '5') -> pd.DataFrame:
        """
        获取分钟K线数据

        Parameters:
            stock_code: 股票代码
            period: '1'/'5'/'15'/'30'/'60'

        Returns:
            DataFrame with OHLCV数据
        """
        import akshare as ak
        try:
            df = ak.stock_zh_a_minute(
                symbol=stock_code,
                period=period,
                adjust='qfq'
            )
            return df
        except Exception as e:
            print(f"获取分钟数据失败: {e}")
            return pd.DataFrame()

    def aggregate_to_tick(self, minute_df: pd.DataFrame) -> pd.DataFrame:
        """
        将分钟数据聚合为近似Tick数据
        """
        if minute_df.empty:
            return pd.DataFrame()

        return pd.DataFrame({
            'timestamp': minute_df['时间'],
            'price': minute_df['收盘'],
            'volume': minute_df['成交量'],
            'amount': minute_df['成交额']
        })
```

---

## 7. 模拟交易平台

### 7.1 完整架构

```python
模拟交易平台 = {
    '仿真引擎': '使用与实盘完全相同的交易API，接入实时或延迟行情',
    '实盘环境模拟': '模拟真实下单、成交确认、资金冻结/解冻的完整延迟',
    '仿真监控': '提供与实盘监控类似的界面，观察策略在实时环境下的表现'
}
```

### 7.2 清风量化系统状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 仿真引擎 | ⚠️ 基础实现 | 使用akshare实时数据 |
| 实盘环境模拟 | ⏳ 待实现 | 需要券商API |
| 仿真监控 | ⚠️ 基础实现 | 自定义监控界面 |

---

## 8. AI增强研究工具

```python
AI增强工具 = {
    '因子挖掘': '自动发现新因子',
    '参数优化': '作为高级优化算法',
    '报告解读': '自动分析回测报告',
    'AI智能体框架': {
        '智能体核心模块': '自主决策代理',
        '核心功能': '智能体核心能力'
    }
}
```

### 清风量化系统已实现

| 工具 | 状态 | 文档位置 |
|------|------|----------|
| 因子衰减检测 | ✅ 已实现 | `T.08.AI001.因子衰减检测.md` |
| IC/IR监控 | ✅ 已实现 | `T.08.AI002.ICIR监控.md` |
| AI自我优化 | ✅ 已实现 | `T.08.AI003.AI自我优化框架.md` |

---

## 9. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合附录AC/AN系统架构参考 |
