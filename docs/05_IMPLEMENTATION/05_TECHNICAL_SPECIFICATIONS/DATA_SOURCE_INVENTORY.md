---

### 2.5 Baostock - 🆓 免费A股历史数据

**基本信息**:
- **接口名称**: Baostock
- **接口类型**: Python库
- **付费状态**: 🆓 **完全免费**
- **数据覆盖**: A股、指数、基金
- **数据频率**: 日线、周线、月线
- **数据质量**: ⭐⭐⭐⭐（高质量）

**数据类型**:
- ✅ A股历史K线数据
- ✅ 指数数据
- ✅ 基金数据
- ✅ 复权因子

**接入方式**:
```python
import baostock as bs

class BaostockAdapter:
    """Baostock数据源适配器"""
    
    def __init__(self):
        self.logged_in = False
    
    def login(self):
        """登录"""
        lg = bs.login()
        if lg.error_code != '0':
            raise Exception(f"登录失败: {lg.error_msg}")
        self.logged_in = True
    
    def get_daily_data(self, code: str, start: str, end: str):
        """获取日线数据"""
        if not self.logged_in:
            self.login()
        
        rs = bs.query_history_k_data_plus(
            code,
            "date,code,open,high,low,close,volume",
            start_date=start,
            end_date=end,
            frequency="d",
            adjustflag="3"
        )
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        return data_list
```

**优先级**: **P1（补充数据源）**

**使用场景**:
- A股历史数据获取
- 数据质量校验
- 复权数据获取

---

### 2.6 EFinance - 🆓 免费东方财富数据

**基本信息**:
- **接口名称**: EFinance
- **接口类型**: Python库
- **付费状态**: 🆓 **完全免费**
- **数据覆盖**: A股、港股、美股、期货
- **数据频率**: 日线、分钟线、实时行情
- **数据质量**: ⭐⭐⭐⭐（高质量）

**数据类型**:
- ✅ A股行情数据
- ✅ 港股行情数据
- ✅ 美股行情数据
- ✅ 期货行情数据
- ✅ 实时行情

**接入方式**:
```python
import efinance as ef

class EFinanceAdapter:
    """EFinance数据源适配器"""
    
    def __init__(self):
        pass
    
    def get_stock_data(self, code: str, start: str, end: str):
        """获取股票数据"""
        df = ef.stock.get_quote_history(
            code,
            beg=start,
            end=end,
            klt=101,  # 日K
            fqt=1     # 前复权
        )
        return df
```

**优先级**: **P1（补充数据源）**

**使用场景**:
- 东方财富数据获取
- 实时行情数据
- 多市场数据

---

### 2.7 Qlib - 🆓 微软量化数据

**基本信息**:
- **接口名称**: Qlib（微软量化平台）
- **接口类型**: Python库
- **付费状态**: 🆓 **完全免费**
- **数据覆盖**: A股、美股
- **数据频率**: 日线
- **数据质量**: ⭐⭐⭐⭐（高质量）

**数据类型**:
- ✅ A股行情数据
- ✅ 美股行情数据
- ✅ 财务数据
- ✅ 因子数据

**接入方式**:
```python
import qlib
from qlib.data import D

class QlibAdapter:
    """Qlib数据源适配器"""
    
    def __init__(self):
        qlib.init()
    
    def get_stock_data(self, instruments, start_time, end_time, fields):
        """获取股票数据"""
        df = D.features(
            instruments=instruments,
            fields=fields,
            start_time=start_time,
            end_time=end_time
        )
        return df
```

**优先级**: **P2（补充数据源）**

**使用场景**:
- 微软量化平台数据
- 因子数据获取
- 机器学习数据

---
module_id: DATA_SOURCE_INVENTORY_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席技术评审官
standard_type: 数据接口清单
applicable_scope: 全系统数据源管理
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 清风量化系统数据接口清单

> 清风量化系统 v5.2 - 数据接口源完整清单
> **清单日期**: 2026-04-03
> **清单目的**: 明确系统所有数据接口源，标识付费接口，确保数据源管理规范


## 一、数据接口总览

### 1.1 当前可用数据接口

| 序号 | 数据接口名称 | 接口类型 | 付费状态 | 数据类型 | 接入方式 | 认证方式 | 优先级 | 状态 |
|------|------------|---------|---------|---------|---------|---------|--------|------|
| 1 | **iFind** | REST API | ✅ **已有** | 行情数据、财务数据 | REST API | Token | P0（主数据源） | ✅ 可用 |
| 2 | **QMT** | Python API | 🆓 **免费** | 行情数据、交易数据 | Python API | 券商账户 | P0（交易执行） | ✅ 可用 |

### 1.2 免费数据接口

| 序号 | 数据接口名称 | 接口类型 | 付费状态 | 数据类型 | 接入方式 | 认证方式 | 优先级 | 状态 |
|------|------------|---------|---------|---------|---------|---------|--------|------|
| 1 | **Tushare** | REST API | 🆓 **免费** | A股市场数据 | REST API | Token | P1（补充） | ✅ 可用 |
| 2 | **AKShare** | Python库 | 🆓 **免费** | 多市场数据 | Python库 | 无需认证 | P1（补充） | ✅ 可用 |
| 3 | **yfinance** | Python库 | 🆓 **免费** | 美股市场数据 | Python库 | 无需认证 | P2（补充） | ✅ 可用 |
| 4 | **Baostock** | Python库 | 🆓 **免费** | A股历史数据 | Python库 | 无需认证 | P1（补充） | ✅ 可用 |
| 5 | **EFinance** | Python库 | 🆓 **免费** | 东方财富数据 | Python库 | 无需认证 | P1（补充） | ✅ 可用 |
| 6 | **Qlib** | Python库 | 🆓 **免费** | 微软量化数据 | Python库 | 无需认证 | P2（补充） | ✅ 可用 |

---

## 二、详细数据接口说明

### 2.1 iFind（同花顺iFinD）- ✅ 主数据源

**基本信息**:
- **接口名称**: iFind（同花顺iFinD）
- **接口类型**: REST API
- **付费状态**: ✅ **已有账号**
- **数据覆盖**: A股、港股、美股、期货、债券、基金、宏观经济
- **数据频率**: 日线、分钟线、实时行情
- **数据质量**: ⭐⭐⭐⭐⭐（专业级）

**数据类型**:
- ✅ 行情数据（日K、分钟K、实时行情）
- ✅ 财务数据（财报、财务指标）
- ✅ 公司信息（公司基本信息、股东信息）
- ✅ 宏观经济数据
- ✅ 行业数据
- ✅ 指数数据

**接入方式**:
```python
import requests

class iFindAdapter:
    """iFind数据源适配器"""
    
    def __init__(self, token: str):
        self.base_url = "https://api.ifind.com"
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_market_data(self, symbol: str, start_date: str, end_date: str):
        """获取行情数据"""
        url = f"{self.base_url}/market/data"
        params = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()
```

**优先级**: **P0（主数据源）**

**使用场景**:
- 主要数据源，优先使用
- 所有行情数据、财务数据的首选来源

---

### 2.2 QMT（迅投）- 🆓 免费交易接口

**基本信息**:
- **接口名称**: QMT（迅投量化交易终端）
- **接口类型**: Python API (XtQuant库)
- **付费状态**: 🆓 **免费**（XtQuant库免费，需券商账户）
- **数据覆盖**: A股、期货、期权
- **数据频率**: 实时行情、Tick数据
- **数据质量**: ⭐⭐⭐⭐⭐（专业级）

**数据类型**:
- ✅ 实时行情数据
- ✅ Tick数据
- ✅ 交易执行接口
- ✅ 账户管理接口
- ✅ 订单管理接口

**接入方式**:
```python
from xtquant import xtdata

class QMTAdapter:
    """QMT数据源适配器"""
    
    def __init__(self, account: str, password: str):
        self.account = account
        self.password = password
        self.connected = False
    
    def connect(self):
        """连接QMT"""
        # 连接QMT终端
        self.connected = True
        return True
    
    def get_market_data(self, symbol: str, period: str = "1d"):
        """获取行情数据"""
        if not self.connected:
            self.connect()
        
        # 使用QMT API获取数据
        data = xtdata.get_market_data(
            stock_list=[symbol],
            period=period,
            start_time="20230101",
            end_time="20231231"
        )
        return data
```

**优先级**: **P0（交易执行）**

**使用场景**:
- 实时交易执行
- 实时行情订阅
- 账户和订单管理

**使用说明**:
- 🆓 XtQuant库免费使用（pip install xtquant）
- ⚠️ 需要在支持QMT的券商开户
- ⚠️ 需要下载安装QMT交易终端
- 📋 支持券商：国金、国盛、东财、华鑫等

---

### 2.3 Tushare - 🆓 免费补充数据源

**基本信息**:
- **接口名称**: Tushare
- **接口类型**: REST API
- **付费状态**: 🆓 **免费**（部分高级数据需积分）
- **数据覆盖**: A股、港股、美股、期货、数字货币
- **数据频率**: 日线、分钟线
- **数据质量**: ⭐⭐⭐⭐（高质量）

**数据类型**:
- ✅ 行情数据
- ✅ 财务数据
- ✅ 公司信息
- ✅ 宏观经济数据

**接入方式**:
```python
import tushare as ts

class TushareAdapter:
    """Tushare数据源适配器"""
    
    def __init__(self, token: str):
        ts.set_token(token)
        self.pro = ts.pro_api()
    
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str):
        """获取日线数据"""
        df = self.pro.daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )
        return df
```

**优先级**: **P1（补充数据源）**

**使用场景**:
- iFind数据补充
- 历史数据回补
- 数据质量校验

---

### 2.4 AKShare - 🆓 免费补充数据源

**基本信息**:
- **接口名称**: AKShare
- **接口类型**: Python库
- **付费状态**: 🆓 **完全免费**
- **数据覆盖**: A股、港股、美股、期货、期权、基金、债券、数字货币
- **数据频率**: 日线、分钟线
- **数据质量**: ⭐⭐⭐⭐（高质量）

**数据类型**:
- ✅ 行情数据
- ✅ 财务数据
- ✅ 宏观经济数据
- ✅ 行业数据

**接入方式**:
```python
import akshare as ak

class AKShareAdapter:
    """AKShare数据源适配器"""
    
    def __init__(self):
        pass
    
    def get_stock_daily(self, symbol: str):
        """获取股票日线数据"""
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            adjust="hfq"
        )
        return df
```

**优先级**: **P1（补充数据源）**

**使用场景**:
- iFind数据补充
- 实时数据获取
- 多市场数据

---

### 2.5 yfinance - 🆓 免费补充数据源（美股）

**基本信息**:
- **接口名称**: yfinance（Yahoo Finance）
- **接口类型**: Python库
- **付费状态**: 🆓 **完全免费**
- **数据覆盖**: 美股、港股、A股（部分）
- **数据频率**: 日线、分钟线
- **数据质量**: ⭐⭐⭐（中等质量）

**数据类型**:
- ✅ 美股行情数据
- ✅ 港股行情数据
- ⚠️ A股数据（部分）

**接入方式**:
```python
import yfinance as yf

class YFinanceAdapter:
    """yfinance数据源适配器"""
    
    def __init__(self):
        pass
    
    def get_stock_data(self, symbol: str, start: str, end: str):
        """获取股票数据"""
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end)
        return df
```

**优先级**: **P2（补充数据源）**

**使用场景**:
- 美股数据获取
- 港股数据补充
- 国际市场数据

---

## 三、数据源优先级策略

### 3.1 数据源优先级矩阵

| 数据类型 | 第一优先级 | 第二优先级 | 第三优先级 | 说明 |
|---------|-----------|-----------|-----------|------|
| **A股行情数据** | iFind | Tushare | AKShare | iFind为主，免费源补充 |
| **A股财务数据** | iFind | Tushare | - | iFind财务数据最完整 |
| **实时行情** | QMT | iFind | - | QMT实时性最好 |
| **交易执行** | QMT | - | - | 仅QMT支持交易执行 |
| **美股数据** | yfinance | - | - | 美股数据源 |
| **宏观经济** | iFind | Tushare | AKShare | 多源交叉验证 |

### 3.2 数据源切换策略

**主备切换规则**:
1. **iFind故障** → 自动切换到Tushare或AKShare
2. **QMT故障** → 无法交易，仅查询功能可用
3. **数据质量异常** → 多源交叉验证

**切换时间要求**:
- 故障发现时间: <30秒
- 主备切换时间: <60秒
- 数据恢复验证: <120秒

---

## 四、付费接口成本分析

### 4.1 付费接口成本对比

| 数据接口 | 年费估算 | 数据覆盖 | 性价比 | 建议 |
|---------|---------|---------|--------|------|
| **QMT** | 3-5万元 | A股、期货、期权 | ⭐⭐⭐⭐⭐ | ✅ **必需**（交易执行） |
| **Wind** | 5-10万元 | 全市场 | ⭐⭐⭐⭐ | ⚠️ 可选（iFind已覆盖） |
| **Bloomberg** | 20-30万元 | 全球市场 | ⭐⭐⭐ | ❌ 不推荐（成本高） |
| **东方财富Choice** | 2-3万元 | A股市场 | ⭐⭐⭐ | ❌ 不推荐（iFind已覆盖） |

### 4.2 成本优化建议

**当前方案（推荐）**:
- ✅ iFind（已有） - 主数据源
- ✅ QMT（付费） - 交易执行
- ✅ Tushare（免费） - 数据补充
- ✅ AKShare（免费） - 数据补充

**年成本**: 约3-5万元（仅QMT）

**备选方案**:
- 如果需要更全面的数据覆盖，可考虑Wind
- 如果需要全球市场数据，可考虑Bloomberg（成本较高）

---

## 五、数据源管理规范

### 5.1 数据源接入规范

**接入流程**:
1. 数据源评估（数据质量、成本、稳定性）
2. 接口开发（适配器开发）
3. 测试验证（功能测试、性能测试）
4. 上线部署（生产环境部署）
5. 监控运维（健康监控、告警）

**接入要求**:
- ✅ 必须实现统一的适配器接口
- ✅ 必须支持健康检查
- ✅ 必须支持错误处理和重试
- ✅ 必须记录访问日志

### 5.2 数据源使用规范

**使用原则**:
1. **优先级原则**: 按优先级使用数据源
2. **成本原则**: 优先使用免费数据源
3. **质量原则**: 关键数据多源验证
4. **稳定性原则**: 主备切换机制

**使用限制**:
- ⚠️ 避免频繁调用（遵循API限制）
- ⚠️ 避免重复获取（使用缓存）
- ⚠️ 避免高峰期调用（错峰使用）

---

## 六、数据源监控指标

### 6.1 监控指标定义

| 指标名称 | 指标说明 | 目标值 | 告警阈值 |
|---------|---------|--------|---------|
| **可用性** | 数据源可用时间占比 | ≥99.9% | <99% |
| **响应时间** | API响应时间 | <500ms | >1000ms |
| **错误率** | API调用错误率 | <0.1% | >1% |
| **数据完整性** | 数据字段完整率 | ≥99% | <95% |
| **数据准确性** | 数据正确率 | ≥99.9% | <99% |

### 6.2 监控告警规则

**告警级别**:
- **P0**: 数据源完全不可用
- **P1**: 数据源性能严重下降
- **P2**: 数据源偶发异常
- **P3**: 数据源轻微异常

**告警通知**:
- P0: 立即电话通知
- P1: 短信+邮件通知
- P2: 邮件通知
- P3: 系统记录

---

## 七、文档治理

### 7.1 文档索引

**本文档在系统中的位置**:
- **父文档**: [DATA_SOURCE_MANAGEMENT_BLUEPRINT.md](./DATA_SOURCE_MANAGEMENT_BLUEPRINT.md)
- **关联文档**:
  - [DATA_SOURCE_MANAGEMENT_BLUEPRINT.md](./DATA_SOURCE_MANAGEMENT_BLUEPRINT.md)
  - [ARCHITECTURE.md](../../01_FRAMEWORK/ARCHITECTURE.md)

### 7.2 版本管理

**版本历史**:
- v1.0.0 (2026-04-03): 初始版本，完成数据接口清单整理

---

**清单版本**: v1.0 | **创建日期**: 2026-04-03 | **状态**: ✅ 正式 | **维护者**: ZephyrAlpha技术团队
