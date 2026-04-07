---
module_id: DEVELOPMENT_STANDARDS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 实施指南、部署文档

---
---

---
module_id: IMPL_DEV_STANDARDS_001
version: 1.0.15.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 风险预算
  - 因子计算
  - 组合优化
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部?
compliance_level: 实施标准
parent_document: ../INDEX.md
implementation_status: 进行?---



# 开发标准与规范
> **核心职责**: 标准规范制定
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.3 的开发标准、目录结构、代码规?
>
> **文档来源**: ?DEVELOPER_RULES.md 拆分而来，遵循职责驱动原?
> **相关文档**: [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md), [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md)


## 一、目录结构规?

### 1.1 顶层结构

```
D:\ZephyrAlpha\
?
├── docs/                          # 文档中心（只读参考）
?  ├── INDEX.md                   # 文档导航入口
?  ├── QUICK_REFERENCE.md         # 快速命令参?
?  ├── System_Manifest.md         # 系统清单（架构、模块、权限）
?  ├── API_Contract.md            # 模块间接口契?
?  └── ...                        # 其他文档
?
├── src/                           # 源代?
├── tests/                         # 测试
├── config/                        # 配置
├── scripts/                       # 脚本
├── data/                          # 数据
├── logs/                          # 日志
└── notebooks/                     # Jupyter
```

### 1.2 ZephyrAlpha/ 详细结构

```
ZephyrAlpha/
├── config/                        # 配置（所有可修改配置?
?  ├── system.yaml               # 系统级配?
?  ├── data_sources.yaml         # 数据源配?
?  ├── factors/                   # 因子配置
?  ?  └── selected_factors.yaml
?  ├── strategies/                # 策略配置
?  ?  └── active_strategies.yaml
?  └── risk/                      # 风控配置
?      └── rules.yaml
?
├── src/                           # 源代?
?  ├── __init__.py
?  ├── main.py                    # 入口?
?  ├── core/                      # 核心基类
?  ?  ├── __init__.py
?  ?  ├── base.py                # Result, Signal, Order, Position
?  ?  └── exceptions.py          # 异常类定?
?  ├── modules/                   # 功能模块（M01-M15?
?  ?  ├── __init__.py
?  ?  ├── datahub.py             # M01 数据中心
?  ?  ├── factor_calculator.py   # M02 因子计算
?  ?  ├── strategy_engine.py     # M03 策略引擎
?  ?  ├── risk_manager.py        # M04 风险管理
?  ?  ├── portfolio_optimizer.py # M05 组合优化
?  ?  ├── trade_executor.py      # M06 交易执行
?  ?  ├── risk_monitor.py        # M07 风险监控
?  ?  ├── performance_analyzer.py # M08 绩效分析
?  ?  ├── config_manager.py      # M09 配置管理
?  ?  ├── log_manager.py         # M10 日志管理
?  ?  ├── cache_manager.py       # M11 缓存管理
?  ?  ├── event_bus.py           # M12 事件总线
?  ?  ├── metrics_collector.py   # M13 指标采集
?  ?  ├── alert_manager.py       # M14 告警管理
?  ?  └── backtest_engine.py     # M15 回测引擎
?  ├── strategies/                # 策略实现
?  ?  ├── __init__.py
?  ?  ├── s001_trend_follow.py   # S001 趋势跟踪
?  ?  └── s002_macd.py           # S002 MACD
?  ├── factors/                   # 因子实现
?  ?  ├── __init__.py
?  ?  ├── alpha_001_momentum.py  # ALPHA_001 动量因子
?  ?  └── alpha_002_mean_reversion.py
?  └── utils/                     # 工具函数
?      ├── __init__.py
?      ├── data_utils.py
?      ├── math_utils.py
?      └── time_utils.py
?
├── tests/                         # 测试
?  ├── __init__.py
?  ├── unit/                      # 单元测试
?  ?  ├── test_datahub.py
?  ?  └── test_factor_calculator.py
?  ├── integration/               # 集成测试
?  ?  └── test_strategy_engine.py
?  └── fixtures/                  # 测试数据
?      └── sample_data.csv
?
├── scripts/                       # 工具脚本
?  ├── download_data.py          # 数据下载
?  ├── backtest.py               # 回测脚本
?  └── init_db.py                # 数据库初始化
?
├── data/                          # 数据存储（gitignored?
?  ├── raw/                      # 原始数据
?  ├── processed/                # 处理后数?
?  └── cache/                    # 临时缓存
?
├── logs/                          # 日志（gitignored?
?
├── notebooks/                     # Jupyter（gitignored?
?
├── docs/                          # 代码库文档（项目私有?
?  ├── ARCHITECTURE.md           # 架构?
?  ├── MODULES.md                # 模块规格
?  └── ...
?
├── requirements.txt               # 依赖清单
├── pyproject.toml                # 项目配置
├── .env.example                  # 环境变量示例
├── .gitignore
└── README.md                      # 项目自述
```

### 1.3 禁止的目录和文件

| 禁止 | 原因 | 正确位置 |
|------|------|---------|
| `temp/` | 污染根目?| `/tmp/` ?`data/cache/` |
| `backup/` | 版本控制管理 | 使用 `git tag` |
| `old/` | 版本控制管理 | 使用 `06_ARCHIVE/` |
| `test_*.py` ?`src/` | 测试应隔?| `tests/unit/` |
| `tmp_*` | 污染目录 | `data/cache/` |
| 中文目录?| 跨平台问?| 英文命名 |


## 二、文件命名规?

### 2.1 Python 文件

```python
# ?正确
datahub.py                  # 模块: 小写 + 下划?
s001_trend_follow.py        # 策略: s + 编号 + 下划?+ 名称
alpha_001_momentum.py       # 因子: alpha_ + 编号 + 下划?+ 名称
test_datahub.py             # 测试: test_ + 模块?

# ?错误
DataHub.py                  # 不用 PascalCase
S001TrendFollow.py          # 不用 CamelCase
Alpha001Momentum.py         # 不用 CamelCase
test-datahub.py             # 不用连字?
```

### 2.2 配置文件

```yaml
# ?正确
system.yaml                 # 系统配置
strategies.yaml             # 策略配置
factors.yaml                # 因子配置
data_sources.yaml           # 数据源配?

# ?错误
config.yaml                 # 太通用
settings.json               # 使用 YAML
system_config.yaml          # 冗余
```

### 2.3 文档文件

```markdown
# ?正确
README.md                   # 项目说明
DEVELOPMENT_STANDARDS.md    # 开发标?
INDEX.md                    # 文档索引
CHANGELOG.md                # 变更日志

# ?错误
readme.md                   # 用大?
quick-start.md              # 用连字符
```


## 三、代码标?

### 3.1 文件头部

```python
"""模块名称

功能描述
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
```

### 3.2 类定?

```python
class DataHub:
    """数据中心模块

    职责：获取和缓存市场数据

    属性：
        config: 配置对象
        cache: 缓存管理?

    示例?
        >>> hub = DataHub()
        >>> data = hub.get_ohlcv("000001.SZ", "2026-01-01", "2026-03-28")
    """

    def __init__(self, config: Dict):
        self.config = config
        self.cache = None
```

### 3.3 函数定义

```python
def calculate_ma(prices: List[float], window: int) -> float:
    """计算移动平均?

    参数?
        prices: 价格列表
        window: 窗口大小

    返回?
        移动平均?

    异常?
        ValueError: 参数无效
    """
    if not prices or window <= 0:
        raise ValueError("参数无效")
    return sum(prices[-window:]) / window
```

### 3.4 类型提示

```python
# ?正确
def process_data(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    ...

# ?错误
def process_data(df, params):  # 无类型提?
    ...
```


## 四、配置管?

### 4.1 配置文件原则

- **不硬编码**: 所有配置通过 YAML 文件或环境变?
- **敏感信息**: 使用 `${VAR_NAME}` ?`${VAR_NAME:default}` 语法
- **分层管理**: system.yaml ?strategies.yaml ?策略私有配置

### 4.2 system.yaml 示例

```yaml
system:
  name: "清风量化交易系统"
  version: "4.0.3"
  environment: "${ENVIRONMENT:development}"

database:
  host: "${DB_HOST:localhost}"
  password: "${DB_PASSWORD}"

cache:
  host: "${CACHE_HOST:localhost}"
  port: "${CACHE_PORT:6379}"
  ttl: 3600
```


## 五、测试规?

### 5.1 测试文件位置

```
tests/
├── unit/                      # 单元测试
?  ├── test_datahub.py
?  └── test_factor_calculator.py
?
└── integration/              # 集成测试
    └── test_strategy_engine.py
```

### 5.2 测试命名

```python
# ?正确
def test_calculate_ma_normal():
    """测试正常情况"""

def test_calculate_ma_empty_list():
    """测试空列?""

def test_calculate_ma_invalid_window():
    """测试无效窗口"""

# ?错误
def test_ma():       # 名称模糊
def test_1():        # 无意义编?
```

### 5.3 覆盖率要?

```bash
pytest tests/ --cov=src --cov-report=html
# 最低要? > 80%
```


## 六、文件归属检查清?

创建文件前，问自己：

| 问题 | 如果?| 放这?|
|------|--------|--------|
| 代码文件?| ?| `src/` |
| 测试代码?| ?| `tests/` |
| 配置文件?| ?| `config/` |
| 工具脚本?| ?| `scripts/` |
| 文档参考？ | ?| `docs/` |
| 临时数据?| ?| `data/cache/` |
| 分析笔记本？ | ?| `notebooks/` |


> **维护部门**: 清风量化开发部
> **最后更?*: 2026-04-01
> **文档版本**: v5.3

**相关文档**:
- [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) - 开发工作流?
- [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md) - 设计原则
- [DEVELOPER_RULES.md](./DEVELOPER_RULES.md) - 原文档（已拆分）
