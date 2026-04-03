---
module_id: DOC_DOC_001
version: 1.0.0
status: Archived
created_date: 2026-04-01
last_updated: 2026-04-02
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 已归档
archive_date: 2026-04-02
archive_reason: 架构从Layer 0-8迁移到三级时间框架融合架构
new_document: ../../02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md
---

# L0_QMT 数据接口模块设计

> **⚠️ 本文档已归档**
> 
> - **归档日期**: 2026-04-02
> - **归档原因**: 架构从Layer 0-8迁移到三级时间框架融合架构
> - **新架构文档**: [QMT数据接口技术规范](../../02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md)
> - **内容状态**: 本文档内容已过时，仅供参考，请勿用于实际开发
> - **迁移执行**: Audit Sentinel

---

> **版本**: v1.0
> **创建日期**: 2026-04-01
> **所属层级**: Layer 0 (数据源层)
> **设计状态**: 🔄 设计进行中

---

## 📖 QMT官方API参考

### 官方文档资源

#### 核心文档链接
1. **[QMT快速开始指南](https://dict.thinktrader.net/innerApi/start_now.html)**
   - QMT系统概述和运行机制
   - 回测模型与实盘模型区别
   - 逐K线驱动、事件驱动、定时任务三种运行机制

2. **[XtQuant原生API](https://dict.thinktrader.net/nativeApi/start_now.html)**
   - XtQuant Python库完整说明
   - 行情模块(xtdata)和交易模块(xttrader)详细API
   - 支持Python 3.6-3.12（64位）

3. **[QMT数据字典](https://dict.thinktrader.net/dictionary/)**
   - 完整API函数列表
   - 函数参数和返回值详细说明
   - 使用示例和代码片段

4. **[VBA公式系统](https://dict.thinktrader.net/VBA/start_now.html)**（可选）
   - VBA公式编写规则
   - 序列模式和逐K线模式
   - 适合有VBA经验的开发者

### XtQuant核心模块

#### 1. 行情模块 (xtdata)

**主要功能**：
- 历史K线数据获取
- 实时分笔数据订阅
- 财务数据查询
- 合约基础信息
- 板块和行业分类

**核心API函数**：
```python
from xtquant import xtdata

# 获取交易日期
trading_dates = xtdata.get_trading_dates('SH')

# 获取板块股票列表
stock_list = xtdata.get_stock_list_in_sector('沪深A股')

# 获取合约详细信息
instrument_detail = xtdata.get_instrument_detail("000001.SZ")

# 获取历史K线数据
market_data = xtdata.get_market_data_ex(
    stock_list=['000001.SZ'],
    period='1d',  # 周期：1d, 1m, 5m, 15m, 30m, 60m
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

**主要功能**：
- 报单、撤单
- 查询资产、委托、成交、持仓
- 接收资金、委托、成交、持仓变动推送

**核心API函数**：
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
    price_type=xttrader.FIX_PRICE,  # 限价单
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

---

## 📋 归档说明

### 归档原因
本文档基于旧的Layer 0-8技术流水线架构编写，已不符合当前系统的三级时间框架融合架构。

### 迁移内容
本文档的核心价值内容已迁移至新文档：
- **新文档路径**: docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md
- **迁移日期**: 2026-04-02
- **迁移执行**: Audit Sentinel

### 保留原因
本文档保留作为历史记录，用于：
1. 架构演进历史追溯
2. 迁移过程完整性验证
3. 未来可能的架构回退参考

### 访问建议
- ✅ **推荐**: 访问新文档 [QMT数据接口技术规范](../../02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md)
- ⚠️ **警告**: 本文档内容已过时，请勿用于实际开发
- 📝 **记录**: 如需查看历史版本，可访问Git历史记录

---

**归档状态**: ✅ 已归档  
**归档日期**: 2026-04-02  
**归档人员**: Audit Sentinel
