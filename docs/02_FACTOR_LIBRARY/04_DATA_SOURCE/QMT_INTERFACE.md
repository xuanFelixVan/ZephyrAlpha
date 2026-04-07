---
module_id: DATA_QMT_INTERFACE_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 数据架构师
standard_type: 专业量化机构文档
applicable_scope: 数据源层
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计完成
architecture_layer: 数据基础设施层
timeframe_support:
- 宏观配置层
- 中观策略层
- 微观执行层
responsibility: QMT交易接口对接与行情数据获取
---
---

# QMT数据接口技术规格

> **核心职责**: QMT量化交易接口定义和使用说明，涉及数据接口技术规格
> **职责边界**: 
> - ✅ 本文档负责：QMT量化交易接口定义和使用说明
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: QMT数据接口技术规格
- 定义QMT数据接口规范
- 说明行情数据和交易数据获取方法
- 提供QMT API调用示例和最佳实践

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据源适配器 | [DATA_SOURCE_ADAPTERS.md](./DATA_SOURCE_ADAPTERS.md) | 上层架构 | 数据源统一适配器 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: QMT数据接口定义和使用说明
- ❌ 本文档不负责: 交易策略实现（由策略层负责）

> **版本**: v1.0
> **创建日期**: 2026-04-02
> **所属层�?*: 数据基础设施�?
> **设计状�?*: �?设计完成
> **迁移来源**: <!-- 归档链接已注�?  --> (已归�?

---

## 📖 QMT官方API参�?

### 官方文档资源

#### 核心文档链接
1. **[QMT快速开始指南](https://dict.thinktrader.net/innerApi/start_now.html)**
   - QMT系统概述和运行机�?
   - 回测模型与实盘模型区�?
   - 逐K线驱动、事件驱动、定时任务三种运行机�?

2. **[XtQuant原生API](https://dict.thinktrader.net/nativeApi/start_now.html)**
   - XtQuant Python库完整说�?
   - 行情模块(xtdata)和交易模�?xttrader)详细API
   - 支持Python 3.6-3.12�?4位）

3. **[QMT数据字典](https://dict.thinktrader.net/dictionary/)**
   - 完整API函数列表
   - 函数参数和返回值详细说�?
   - 使用示例和代码片�?

4. **[VBA公式系统](https://dict.thinktrader.net/VBA/start_now.html)**（可选）
   - VBA公式编写规则
   - 序列模式和逐K线模�?
   - 适合有VBA经验的开发�?

### XtQuant核心模块

#### 1. 行情模块 (xtdata)

**主要功能**�?
- 历史K线数据获�?
- 实时分笔数据订阅
- 财务数据查询
- 合约基础信息
- 板块和行业分�?

**核心API函数**�?
```python
from xtquant import xtdata

# 获取交易日期
trading_dates = xtdata.get_trading_dates('SH')

# 获取板块股票列表
stock_list = xtdata.get_stock_list_in_sector('沪深A�?)

# 获取合约详细信息
instrument_detail = xtdata.get_instrument_detail("000001.SZ")

# 获取历史K线数�?
market_data = xtdata.get_market_data_ex(
    stock_list=['000001.SZ'],
    period='1d',  # 周期�?d, 1m, 5m, 15m, 30m, 60m
    start_time='20230101',
    end_time='20231231',
    subscribe=False  # 回测模式使用本地数据
)

# 订阅实时行情
def on_tick(data):
    print(f"实时行情: {data}")
    
xtdata.subscribe_quote(
    stock_code='000001.SZ',
    callback=on_tick
)
```

#### 2. 交易模块 (xttrader)

**主要功能**�?
- 报单、撤�?
- 查询资产、委托、成交、持�?
- 接收资金、委托、成交、持仓变动推�?

**核心API函数**�?
```python
from xtquant import xttrader

# 连接交易账户
session_id = xttrader.connect(
    account='您的账户',
    password='您的密码'
)

# 股票下单
order_id = xttrader.order_stock(
    account='您的账户',
    stock_code='000001.SZ',
    order_type=xttrader.STOCK_BUY,  # 买入
    order_volume=100,  # 股数
    price_type=xttrader.FIX_PRICE,  # 限价�?
    price=10.0,  # 价格
    strategy_name='test_strategy',
    order_remark='test_order'
)

# 撤单
xttrader.cancel_order(
    account='您的账户',
    order_id=order_id
)

# 查询委托
orders = xttrader.query_stock_orders(
    account='您的账户'
)

# 查询持仓
positions = xttrader.query_stock_positions(
    account='您的账户'
)

# 查询资产
asset = xttrader.query_stock_asset(
    account='您的账户'
)
```

### 运行环境要求

#### 必需组件
1. **MiniQMT客户�?*
   - 必须先启动MiniQMT客户�?
   - 下载地址：联系券商或访问 https://xuntou.net/
   - 安装路径示例：`C:/国金证券/QMT`

2. **Python环境**
   - 版本要求：Python 3.6-3.12�?4位）
   - 不同版本导入时自动切�?

3. **Token获取**
   - 访问：https://xuntou.net/#/userInfo
   - 注册并获取token用于登录行情服务

#### 账号类型
1. **实盘账号**
   - 真实交易所柜台
   - 需要券商开通QMT交易权限

2. **模拟账号**
   - 模拟交易柜台
   - 联系券商或购买投研端账号

### 运行机制详解

#### 1. 逐K线驱�?(handlebar)
```python
def handlebar(ContextInfo):
    """
    主图历史K�?盘中订阅推�?
    - 运行开始时，历史K线从左向右每根触发一�?
    - 盘中时，每个新分笔数据到达触发一�?
    """
    # 获取当前K线数�?
    close = ContextInfo.get_market_data(
        ['close'], 
        stock_code=ContextInfo.stockcode,
        period=ContextInfo.period
    )
    
    # 交易逻辑
    if close > some_condition:
        passorder(...)  # 下单函数
```

#### 2. 事件驱动 (subscribe)
```python
def on_tick(data):
    """
    订阅指定品种的分笔数�?
    新分笔到达时触发回调函数
    """
    print(f"收到实时行情: {data}")

# 订阅实时行情
xtdata.subscribe_quote(
    stock_code='000001.SZ',
    callback=on_tick
)
```

#### 3. 定时任务 (run_time)
```python
from xtquant import xtdata

def scheduled_task():
    """定时执行的任�?""
    print("定时任务执行")

# �?秒执行一�?
xtdata.run_time(
    func=scheduled_task,
    period='5s'
)
```

### 数据下载说明

#### 首次使用需下载历史数据
1. 打开QMT客户�?
2. 左上�?�?操作 �?数据管理 �?补充行情
3. 选择周期（如日线�?
4. 选择板块（如沪深A股）
5. 时间范围：全�?
6. 点击下载

#### 设置定时更新
1. 点击客户端右下角"行情"按钮
2. 在批量下载界面选择需要每天更新的数据
3. 勾�?定时下载"选项
4. 设置定时时间

### 交易模式说明

#### 回测模型
- 遍历固定的历史数�?
- 使用`get_market_data_ex()`，`subscribe=False`读取本地数据
- 撮合规则：价格在K线高低点间按指定价格撮合，超过按收盘�?
- 数量超过可用数量时按可用数量撮合
- 必须以副图模式执�?

#### 实盘模型
**逐K线模�?*（quicktrade=0）：
- 盘中模拟历史上逐K线效�?
- 每个分笔触发handlebar，暂存信�?
- 新K线首个分笔到达时发送上一根K线的信号
- 前面分笔的信号会被丢�?

**立即下单模式**（quicktrade=2）：
- 运行后立刻发出委�?
- 不等待、不丢弃信号
- 需要用全局变量保存委托状�?
- 撮合规则以交易所为准

### 常见问题

#### Q1: 如何获取token�?
**A**: 访问 https://xuntou.net/#/userInfo 注册并获取token

#### Q2: XtQuant是否免费�?
**A**: XtQuant库本身免费，但需要QMT交易账户。实盘账号需券商开通，模拟账号可联系券商或购买投研端账号�?

#### Q3: 支持哪些Python版本�?
**A**: 支持64位Python 3.6�?.7�?.8�?.9�?.10�?.11�?.12，不同版本自动切换�?

#### Q4: 回测和实盘的区别�?
**A**: 
- **回测**：遍历历史数据，使用本地数据，模拟撮�?
- **实盘**：接收实时行情，真实下单，交易所撮合

#### Q5: 如何选择交易模式�?
**A**: 
- **逐K线模�?*：需要模拟历史逐K线效果，信号在K线结束时发�?
- **立即下单模式**：需要立即执行信号，不等待K线结�?

### 最佳实践建�?

#### 1. 开发流�?
```
1. 申请QMT账户并安装MiniQMT客户�?
2. 获取token并测试连�?
3. 下载历史数据
4. 编写回测模型验证策略
5. 切换到模拟账号测�?
6. 最后使用实盘账�?
```

#### 2. 错误处理
```python
from xtquant import xtdata
import time

def get_data_with_retry(stock_code, max_retries=3):
    """带重试的数据获取"""
    for i in range(max_retries):
        try:
            data = xtdata.get_market_data_ex([stock_code])
            return data
        except Exception as e:
            print(f"第{i+1}次尝试失�? {e}")
            time.sleep(2 ** i)  # 指数退�?
    raise Exception(f"获取数据失败，已重试{max_retries}�?)
```

#### 3. 性能优化
- 使用批量接口减少API调用次数
- 合理设置缓存大小和TTL
- 异步订阅实时行情
- 避免在handlebar中执行耗时操作

---

## 🎯 功能设计

### 核心功能列表
| 功能ID | 功能名称 | 功能描述 | 输入 | 输出 | 调用频率 |
|--------|----------|----------|------|------|----------|
| FUNC_001 | 实时行情订阅 | 订阅股票实时行情数据 | 股票代码列表 | 实时行情�?| 实时 |
| FUNC_002 | 历史K线获�?| 获取历史K线数�?| 股票代码、周期、起止时�?| K线数据列�?| 日频/按需 |
| FUNC_003 | 财务数据获取 | 获取财务报表数据 | 股票代码、报表类型、期�?| 财务数据字典 | 季频 |
| FUNC_004 | 交易执行 | 执行买卖订单 | 订单信息 | 成交结果 | 按需 |
| FUNC_005 | 账户信息查询 | 查询账户资金和持�?| 账户ID | 账户信息 | 实时 |
| FUNC_006 | 数据缓存管理 | 缓存高频访问数据 | 数据键�?| 缓存数据 | 实时 |

### 功能详细说明
```python
# FUNC_001: 实时行情订阅
async def subscribe_realtime_quotes(
    symbols: List[str], 
    callback: Callable[[QuoteData], None]
) -> SubscriptionHandle:
    """
    订阅股票实时行情数据
    
    Args:
        symbols: 股票代码列表，如 ["000001.SZ", "600000.SH"]
        callback: 行情数据回调函数，收到数据时调用
        
    Returns:
        SubscriptionHandle: 订阅句柄，用于取消订�?
        
    Raises:
        QMTConnectionError: QMT连接失败
        InvalidSymbolError: 股票代码无效
    """
```

```python
# FUNC_002: 历史K线获�?
def get_historical_bars(
    symbol: str,
    period: Literal["1m", "5m", "15m", "30m", "60m", "1d", "1w", "1M"],
    start_time: datetime,
    end_time: datetime,
    adjust: Literal["none", "qfq", "hfq"] = "qfq"
) -> List[BarData]:
    """
    获取历史K线数�?
    
    Args:
        symbol: 股票代码
        period: K线周�?
        start_time: 开始时�?
        end_time: 结束时间
        adjust: 复权方式
        
    Returns:
        List[BarData]: K线数据列�?
        
    Raises:
        DataNotAvailableError: 数据不可�?
        TimeoutError: 获取超时
    """
```

---

## 🔗 接口设计

### Python API
```python
class QMTDataInterface:
    """QMT数据接口主类"""
    
    def __init__(self, config: QMTConfig):
        """
        初始化QMT数据接口
        
        Args:
            config: QMT配置信息
                - qmt_path: QMT客户端安装路�?
                - account_id: 账户ID
                - password: 密码（加密存储）
                - cache_enabled: 是否启用缓存
        """
        pass
    
    async def connect(self) -> bool:
        """连接QMT客户�?""
        pass
    
    async def disconnect(self) -> None:
        """断开连接"""
        pass
    
    # 行情数据接口
    async def subscribe_quotes(self, symbols: List[str]) -> SubscriptionHandle:
        """订阅实时行情"""
        pass
    
    def get_bars(self, symbol: str, period: str, start: datetime, end: datetime) -> List[BarData]:
        """获取历史K�?""
        pass
    
    # 财务数据接口
    def get_financial_data(self, symbol: str, report_type: str, period: str) -> Dict[str, Any]:
        """获取财务数据"""
        pass
    
    # 交易接口
    async def place_order(self, order: OrderRequest) -> OrderResult:
        """下单"""
        pass
    
    def get_account_info(self) -> AccountInfo:
        """获取账户信息"""
        pass
    
    # 工具接口
    def get_available_symbols(self) -> List[str]:
        """获取可交易股票列�?""
        pass
    
    def get_trading_calendar(self) -> List[datetime]:
        """获取交易日历"""
        pass
```

### 数据接口

#### 输入数据格式
```python
# 订单请求
OrderRequest = TypedDict('OrderRequest', {
    'symbol': str,
    'side': Literal['buy', 'sell'],
    'order_type': Literal['limit', 'market'],
    'price': Optional[float],
    'quantity': int,
    'strategy_id': Optional[str],
    'remark': Optional[str]
})

# 历史数据请求
HistoryRequest = TypedDict('HistoryRequest', {
    'symbol': str,
    'period': str,
    'start_time': datetime,
    'end_time': datetime,
    'fields': List[str]
})
```

#### 输出数据格式
```python
# K线数�?
BarData = TypedDict('BarData', {
    'symbol': str,
    'timestamp': datetime,
    'open': float,
    'high': float,
    'low': float,
    'close': float,
    'volume': int,
    'amount': float,
    'adjust_factor': Optional[float]
})

# 实时行情
QuoteData = TypedDict('QuoteData', {
    'symbol': str,
    'timestamp': datetime,
    'last_price': float,
    'bid_price': float,
    'ask_price': float,
    'bid_volume': int,
    'ask_volume': int,
    'volume': int,
    'amount': float,
    'open': float,
    'high': float,
    'low': float,
    'pre_close': float
})

# 订单结果
OrderResult = TypedDict('OrderResult', {
    'order_id': str,
    'symbol': str,
    'status': Literal['pending', 'filled', 'cancelled', 'rejected'],
    'filled_price': Optional[float],
    'filled_quantity': int,
    'remaining_quantity': int,
    'timestamp': datetime,
    'error_message': Optional[str]
})
```

### 配置文件
```yaml
# config/qmt_config.yaml
qmt:
  enabled: true
  connection:
    qmt_path: "D:/国金证券QMT交易�?
    account_id: "您的账户ID"
    password_encrypted: "加密后的密码"
    auto_login: true
    timeout: 30
  
  data:
    cache_enabled: true
    cache_ttl: 300  # 缓存时间(�?
    max_retries: 3
    retry_delay: 1.0
  
  subscription:
    default_symbols: ["000001.SZ", "000002.SZ", "600000.SH"]
    heartbeat_interval: 60
  
  trading:
    enabled: true
    max_position_per_stock: 0.1  # 单只股票最大仓位比�?
    daily_turnover_limit: 1000000  # 日交易额限制
```

---

## ⚠️ 错误处理策略

### 错误类型定义
| 错误类型 | 错误�?| 处理方式 | 恢复策略 |
|----------|--------|----------|----------|
| 连接失败 | ERR_QMT_001 | 记录日志，尝试重�?| 指数退避重�?1s, 2s, 4s...) |
| 登录失败 | ERR_QMT_002 | 告警通知 | 检查账户密码，人工介入 |
| 数据获取超时 | ERR_QMT_003 | 返回缓存数据 | 标记数据源不可靠 |
| 交易执行失败 | ERR_QMT_004 | 记录详细错误 | 人工审核后重�?|
| 订阅断开 | ERR_QMT_005 | 自动重新订阅 | 检查网络连�?|
| 数据格式错误 | ERR_QMT_006 | 数据校验失败 | 记录日志，跳过错误数�?|
| 权限不足 | ERR_QMT_007 | 拒绝访问 | 检查账户权限配�?|
| 网络异常 | ERR_QMT_008 | 网络连接中断 | 自动重连，指数退�?|
| 内存不足 | ERR_QMT_009 | 缓存溢出 | 清理缓存，降低缓存大�?|
| API限流 | ERR_QMT_010 | 请求频率超限 | 降低请求频率，使用批量接�?|

### 错误类型定义代码
```python
from enum import Enum
from typing import Optional, Dict, Any

class QMTErrorCategory(Enum):
    """QMT错误分类"""
    CONNECTION = "connection"      # 连接相关错误
    AUTHENTICATION = "auth"        # 认证相关错误
    DATA = "data"                 # 数据相关错误
    TRADING = "trading"           # 交易相关错误
    SYSTEM = "system"             # 系统相关错误
    NETWORK = "network"           # 网络相关错误

class QMTError(Exception):
    """QMT基础错误�?""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        category: QMTErrorCategory,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
        retry_count: int = 0
    ):
        self.error_code = error_code
        self.message = message
        self.category = category
        self.details = details or {}
        self.recoverable = recoverable
        self.retry_count = retry_count
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格�?""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'category': self.category.value,
            'details': self.details,
            'recoverable': self.recoverable,
            'retry_count': self.retry_count,
            'timestamp': datetime.now().isoformat()
        }

class QMTConnectionError(QMTError):
    """QMT连接错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            error_code="ERR_QMT_001",
            message=message,
            category=QMTErrorCategory.CONNECTION,
            details=details,
            recoverable=True
        )

class QMTLoginError(QMTError):
    """QMT登录错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            error_code="ERR_QMT_002",
            message=message,
            category=QMTErrorCategory.AUTHENTICATION,
            details=details,
            recoverable=False
        )
```

---

## 🏗�?实现指南

### 类结构设�?
```python
class QMTDataInterface:
    """QMT数据接口主类"""
    
    def __init__(self, config: QMTConfig):
        self.config = config
        self._client = None
        self._subscriptions = {}
        self._cache = QMTCache()
        self._connection_manager = QMTConnectionManager()
        self._error_handler = QMTErrorHandler()
```

### 核心连接逻辑
```python
def _initialize_qmt_client(self) -> None:
    """
    初始化QMT客户�?
    
    技术要�?
    1. 使用xtquant�?(国金证券提供的Python SDK)
    2. 支持miniQMT模式 (无界�?
    3. 自动重连机制
    4. 心跳检测保持连�?
    """
    try:
        import xtquant
        from xtquant import xtdata
        
        # 设置QMT路径
        xtdata.set_path(self.config.qmt_path)
        
        # 登录
        if self.config.auto_login:
            success = xtdata.login(
                self.config.account_id,
                self.config.password
            )
            if not success:
                raise QMTLoginError("QMT登录失败")
        
        self._client = xtdata
        self._connection_manager._connected = True
        
    except ImportError:
        raise QMTDependencyError("xtquant库未安装")
    except Exception as e:
        raise QMTConnectionError(f"QMT连接失败: {str(e)}")
```

---

## 📚 相关文档

1. [数据源适配器](./DATA_SOURCE_ADAPTERS.md)
2. [数据获取规范](./DATA_ACQUISITION.md)
3. [数据质量管理系统](01_FRAMEWORK/DATA_QUALITY_MANAGEMENT_BLUEPRINT.md)
4. [专业多时间框架架构](../../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更�?|
|------|------|---------|--------|
| v1.0 | 2026-04-02 | 从L0_QMT.md迁移，去除旧架构标识 | Audit Sentinel |

---

**文档状�?*: �?已完成迁�? 
**最后更�?*: 2026-04-02  
**维护人员**: 数据架构�?


---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
