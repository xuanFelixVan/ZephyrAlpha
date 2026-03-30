---
module_id: DEVELOPER_RULES_001
version: 3.1
status: Active
last_updated: 2026-03-29
---

# 开发规则与标准

> 清风量化系统 v5.0 的开发规范、目录标准、工作流程
>
> **阅读前提**: 已阅读 [INDEX.md](./docs/INDEX.md) 和 [QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md)

---

## 一、目录结构规范

### 1.1 顶层结构

```
D:\ZephyrAlpha\
│
├── docs/                          # 文档中心（只读参考）
│   ├── INDEX.md                   # 文档导航入口
│   ├── QUICK_REFERENCE.md         # 快速命令参考
│   ├── System_Manifest.md         # 系统清单（架构、模块、权限）
│   ├── API_Contract.md            # 模块间接口契约
│   └── ...                        # 其他文档
│
├── src/                           # 源代码
├── tests/                         # 测试
├── config/                         # 配置
├── scripts/                         # 脚本
├── data/                          # 数据
├── logs/                          # 日志
└── notebooks/                      # Jupyter
```

### 1.2 ZephyrAlpha/ 详细结构

```
ZephyrAlpha/
├── config/                        # 配置（所有可修改配置）
│   ├── system.yaml               # 系统级配置
│   ├── data_sources.yaml         # 数据源配置
│   ├── factors/                   # 因子配置
│   │   └── selected_factors.yaml
│   ├── strategies/                # 策略配置
│   │   └── active_strategies.yaml
│   └── risk/                      # 风控配置
│       └── rules.yaml
│
├── src/                           # 源代码
│   ├── __init__.py
│   ├── main.py                    # 入口点
│   ├── core/                      # 核心基类
│   │   ├── __init__.py
│   │   ├── base.py                # Result, Signal, Order, Position
│   │   └── exceptions.py          # 异常类定义
│   ├── modules/                   # 功能模块（M01-M15）
│   │   ├── __init__.py
│   │   ├── datahub.py             # M01 数据中心
│   │   ├── factor_calculator.py    # M02 因子计算
│   │   ├── strategy_engine.py     # M03 策略引擎
│   │   ├── risk_manager.py        # M04 风险管理
│   │   ├── portfolio_optimizer.py # M05 组合优化
│   │   ├── trade_executor.py      # M06 交易执行
│   │   ├── risk_monitor.py        # M07 风险监控
│   │   ├── performance_analyzer.py # M08 绩效分析
│   │   ├── config_manager.py      # M09 配置管理
│   │   ├── log_manager.py         # M10 日志管理
│   │   ├── cache_manager.py       # M11 缓存管理
│   │   ├── event_bus.py           # M12 事件总线
│   │   ├── metrics_collector.py   # M13 指标采集
│   │   ├── alert_manager.py       # M14 告警管理
│   │   └── backtest_engine.py      # M15 回测引擎
│   ├── strategies/                # 策略实现
│   │   ├── __init__.py
│   │   ├── s001_trend_follow.py   # S001 趋势跟踪
│   │   └── s002_macd.py           # S002 MACD
│   ├── factors/                   # 因子实现
│   │   ├── __init__.py
│   │   ├── alpha_001_momentum.py  # ALPHA_001 动量因子
│   │   └── alpha_002_mean_reversion.py
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── data_utils.py
│       ├── math_utils.py
│       └── time_utils.py
│
├── tests/                         # 测试
│   ├── __init__.py
│   ├── unit/                      # 单元测试
│   │   ├── test_datahub.py
│   │   └── test_factor_calculator.py
│   ├── integration/               # 集成测试
│   │   └── test_strategy_engine.py
│   └── fixtures/                  # 测试数据
│       └── sample_data.csv
│
├── scripts/                       # 工具脚本
│   ├── download_data.py          # 数据下载
│   ├── backtest.py               # 回测脚本
│   └── init_db.py                # 数据库初始化
│
├── data/                          # 数据存储（gitignored）
│   ├── raw/                      # 原始数据
│   ├── processed/                # 处理后数据
│   └── cache/                    # 临时缓存
│
├── logs/                          # 日志（gitignored）
│
├── notebooks/                     # Jupyter（gitignored）
│
├── docs/                          # 代码库文档（项目私有）
│   ├── ARCHITECTURE.md           # 架构图
│   ├── MODULES.md                # 模块规格
│   └── ...
│
├── requirements.txt               # 依赖清单
├── pyproject.toml                # 项目配置
├── .env.example                  # 环境变量示例
├── .gitignore
└── README.md                      # 项目自述
```

### 1.3 禁止的目录和文件

| 禁止 | 原因 | 正确位置 |
|------|------|---------|
| `temp/` | 污染根目录 | `/tmp/` 或 `data/cache/` |
| `backup/` | 版本控制管理 | 使用 `git tag` |
| `old/` | 版本控制管理 | 使用 `06_ARCHIVE/` |
| `test_*.py` 在 `src/` | 测试应隔离 | `tests/unit/` |
| `tmp_*` | 污染目录 | `data/cache/` |
| 中文目录名 | 跨平台问题 | 英文命名 |

---

## 二、文件命名规范

### 2.1 Python 文件

```python
# ✅ 正确
datahub.py                  # 模块: 小写 + 下划线
s001_trend_follow.py        # 策略: s + 编号 + 下划线 + 名称
alpha_001_momentum.py       # 因子: alpha_ + 编号 + 下划线 + 名称
test_datahub.py             # 测试: test_ + 模块名

# ❌ 错误
DataHub.py                  # 不用 PascalCase
S001TrendFollow.py          # 不用 CamelCase
Alpha001Momentum.py         # 不用 CamelCase
test-datahub.py             # 不用连字符
```

### 2.2 配置文件

```yaml
# ✅ 正确
system.yaml                 # 系统配置
strategies.yaml             # 策略配置
factors.yaml                # 因子配置
data_sources.yaml           # 数据源配置

# ❌ 错误
config.yaml                 # 太通用
settings.json               # 使用 YAML
system_config.yaml          # 冗余
```

### 2.3 文档文件

```markdown
# ✅ 正确
README.md                   # 项目说明
DEVELOPER_RULES.md          # 开发规则
INDEX.md                    # 文档索引
CHANGELOG.md                # 变更日志

# ❌ 错误
readme.md                   # 用大写
quick-start.md              # 用连字符
```

---

## 三、代码标准

### 3.1 文件头部

```python
"""模块名称

功能描述
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
```

### 3.2 类定义

```python
class DataHub:
    """数据中心模块

    职责：获取和缓存市场数据

    属性：
        config: 配置对象
        cache: 缓存管理器

    示例：
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
    """计算移动平均线

    参数：
        prices: 价格列表
        window: 窗口大小

    返回：
        移动平均值

    异常：
        ValueError: 参数无效
    """
    if not prices or window <= 0:
        raise ValueError("参数无效")
    return sum(prices[-window:]) / window
```

### 3.4 类型提示

```python
# ✅ 正确
def process_data(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    ...

# ❌ 错误
def process_data(df, params):  # 无类型提示
    ...
```

---

## 四、配置管理

### 4.1 配置文件原则

- **不硬编码**: 所有配置通过 YAML 文件或环境变量
- **敏感信息**: 使用 `${VAR_NAME}` 或 `${VAR_NAME:default}` 语法
- **分层管理**: system.yaml → strategies.yaml → 策略私有配置

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

---

## 五、测试规范

### 5.1 测试文件位置

```
tests/
├── unit/                      # 单元测试
│   ├── test_datahub.py
│   └── test_factor_calculator.py
│
└── integration/              # 集成测试
    └── test_strategy_engine.py
```

### 5.2 测试命名

```python
# ✅ 正确
def test_calculate_ma_normal():
    """测试正常情况"""

def test_calculate_ma_empty_list():
    """测试空列表"""

def test_calculate_ma_invalid_window():
    """测试无效窗口"""

# ❌ 错误
def test_ma():       # 名称模糊
def test_1():        # 无意义编号
```

### 5.3 覆盖率要求

```bash
pytest tests/ --cov=src --cov-report=html
# 最低要求: > 80%
```

---

## 六、工作流程

### 6.1 开发流程

```
1. 创建分支
   git checkout -b feature/xxx

2. 编写代码
   - 遵循命名规范
   - 添加类型提示
   - 编写文档字符串
   - 添加单元测试

3. 本地测试
   pytest tests/ -v

4. 提交代码
   git add .
   git commit -m "feat: 描述"

5. 推送
   git push origin feature/xxx

6. 合并（审核后）
   git checkout main
   git merge feature/xxx
```

### 6.2 提交规范

```bash
# ✅ 正确
git commit -m "feat: 添加S001策略"
git commit -m "fix: 修复因子计算错误"
git commit -m "docs: 更新README"
git commit -m "test: 添加单元测试"
git commit -m "refactor: 重构DataHub模块"

# ❌ 错误
git commit -m "update"
git commit -m "fix bug"
git commit -m "WIP"
```

---

## 七、文件归属检查清单

创建文件前，问自己：

| 问题 | 如果是 | 放这里 |
|------|--------|--------|
| 代码文件？ | 是 | `src/` |
| 测试代码？ | 是 | `tests/` |
| 配置文件？ | 是 | `config/` |
| 工具脚本？ | 是 | `scripts/` |
| 文档参考？ | 是 | `docs/` |
| 临时数据？ | 是 | `data/cache/` |
| 分析笔记本？ | 是 | `notebooks/` |

---

## 八、依赖管理

### 8.1 添加依赖

```bash
# 1. 安装到虚拟环境
pip install package_name

# 2. 更新 requirements.txt
pip freeze > requirements.txt

# 3. 更新 pyproject.toml（如果是项目依赖）
```

### 8.2 依赖版本

```txt
# requirements.txt
package>=1.0.0        # 最低版本
package==1.2.3       # 固定版本（生产环境）
```

---

## 九、日志规范

```python
from loguru import logger

logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
logger.debug("调试日志")
```

日志文件位置: `logs/app.log`, `logs/error.log`, `logs/trading.log`

---

## 十、核心设计原则（源自4.0执行方案优化）

### 10.1 优先级驱动原则

| 优先级 | 定义 | 行动 |
|--------|------|------|
| **P0 - 立即执行** | 系统无法运行的核心功能 | 立即开发，不可推迟 |
| **P1 - 本周完成** | 重要但可延迟1-2天的功能 | 本周计划内完成 |
| **P2 - 可延期** | 有价值但不影响核心功能 | 有时间再做 |
| **P3 - 归档** | 过度工程或AI可替代的功能 | 不开发，后期评估 |

**应用场景**：
- 规划任务时按P0→P1→P2→P3排序
- 资源冲突时优先P0，暂停P2/P3
- 每周回顾时确认优先级是否需要调整

### 10.2 开源优先原则

```
✅ 优先使用成熟开源框架：
├── Backtrader      # 回测引擎
├── AKShare         # 数据采集
├── Tushare         # 财务数据
├── LangChain       # AI Agent
├── FastAPI         # API服务
└── SQLite          # 数据存储

❌ 不重复造轮子：
├── 不自研回测引擎 → Backtrader足够
├── 不自研数据采集 → AKShare足够
├── 不自研规则引擎 → if-then规则足够
└── 不自研AI框架 → LangChain足够
```

**决策树**：
1. 是否有成熟开源方案？ → ✅ 使用开源
2. 开源方案是否满足需求？ → ✅ 使用并适配
3. 开源方案有缺陷？ → ⚠️ Fork修改或包装
4. 无开源方案？ → 🔴 谨慎自研，需充分理由

### 10.3 容错与恢复机制

```python
# 容错设计示例
class RetryableOperation:
    """可重试操作"""

    def __init__(self, max_retries: int = 3, backoff: float = 1.0):
        self.max_retries = max_retries
        self.backoff = backoff

    def execute(self, operation, *args, **kwargs):
        """带重试的执行"""
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except TransientError as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"尝试 {attempt + 1} 失败，重试中...")
                time.sleep(self.backoff * (attempt + 1))
```

**恢复机制要求**：
| 场景 | 恢复策略 |
|------|----------|
| 数据采集失败 | 自动重试3次，记录失败日志 |
| 回测中断 | 保存中间状态，支持断点续跑 |
| 系统异常 | 记录堆栈，发送告警，保持日志 |
| 配置错误 | 启动前校验，清晰的错误提示 |

---

### 10.4 Graceful Shutdown机制

```python
import signal
import sys
from contextlib import contextmanager

class GracefulShutdown:
    """优雅关闭处理器

    索引: DEV.RELI.002
    确保系统关闭时完成正在执行的任务
    """

    def __init__(self):
        self.shutdown_requested = False
        self.active_tasks = []
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """处理关闭信号"""
        logger.info(f"收到关闭信号 {signum}，开始优雅关闭...")
        self.shutdown_requested = True

        for task in self.active_tasks:
            task.cancel()

    @contextmanager
    def task_context(self, task_name: str):
        """任务上下文管理器"""
        task = asyncio.current_task()
        self.active_tasks.append(task)
        try:
            yield task
        finally:
            self.active_tasks.remove(task)

    async def wait_for_completion(self, timeout: int = 30):
        """等待所有任务完成"""
        logger.info(f"等待 {len(self.active_tasks)} 个任务完成...")

        start_time = time.time()
        while self.active_tasks and time.time() - start_time < timeout:
            await asyncio.sleep(1)

        if self.active_tasks:
            logger.warning(f"等待超时，{len(self.active_tasks)} 个任务未完成")

    def is_shutting_down(self) -> bool:
        """检查是否正在关闭"""
        return self.shutdown_requested
```

**Graceful Shutdown流程**：
```
1. 收到SIGTERM/SIGINT信号
2. 设置shutdown_requested标志
3. 取消所有pending任务
4. 等待active任务完成（最多30秒）
5. 保存关键状态
6. 关闭数据库连接
7. 退出进程
```

---

### 10.5 系统自愈能力

```python
class HealthChecker:
    """健康检查器

    索引: DEV.RELI.003
    自动检测和修复系统故障
    """

    def __init__(self):
        self.checks = {}
        self.failure_count = {}

    def register_check(self, name: str, check_fn: Callable, threshold: int = 3):
        """注册健康检查

        参数:
            name: 检查名称
            check_fn: 检查函数，返回(bool, str)
            threshold: 连续失败阈值
        """
        self.checks[name] = check_fn
        self.failure_count[name] = 0

    async def run_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        results = {}

        for name, check_fn in self.checks.items():
            try:
                is_healthy, message = await check_fn()
                if not is_healthy:
                    self.failure_count[name] += 1
                else:
                    self.failure_count[name] = 0

                results[name] = {
                    'healthy': is_healthy,
                    'message': message,
                    'failures': self.failure_count[name]
                }
            except Exception as e:
                results[name] = {
                    'healthy': False,
                    'message': str(e),
                    'failures': self.failure_count.get(name, 0) + 1
                }

        return results

    def is_system_healthy(self) -> bool:
        """判断系统是否健康"""
        return all(
            count == 0 for count in self.failure_count.values()
        )

class AutoHealer:
    """自动修复器

    索引: DEV.RELI.003
    根据故障类型自动修复
    """

    HEALING_ACTIONS = {
        'memory_high': 'restart_memory_intensive',
        'disk_full': 'cleanup_old_files',
        'db_connection': 'reconnect_database',
        'api_timeout': 'reset_api_client',
        'process_crash': 'restart_process'
    }

    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
        self.healing_handlers = {}

    async def heal(self, issue: str) -> bool:
        """执行修复

        参数:
            issue: 问题标识

        返回:
            是否修复成功
        """
        action = self.HEALING_ACTIONS.get(issue)

        if not action:
            logger.warning(f"未知问题类型: {issue}")
            return False

        handler = self.healing_handlers.get(action)

        if not handler:
            logger.warning(f"未注册修复处理器: {action}")
            return False

        try:
            logger.info(f"开始修复: {issue} -> {action}")
            success = await handler()
            if success:
                logger.info(f"修复成功: {issue}")
            else:
                logger.error(f"修复失败: {issue}")
            return success
        except Exception as e:
            logger.error(f"修复异常: {issue} - {e}")
            return False
```

**自愈能力要求**：
| 故障类型 | 检测方法 | 自动修复 |
|----------|----------|----------|
| 内存过高 | psutil检测 | 清理缓存 |
| 磁盘满 | disk_usage检测 | 删除旧日志 |
| 数据库连接 | ping检测 | 重连数据库 |
| API超时 | 超时检测 | 重置客户端 |
| 进程崩溃 | 进程检测 | 重启进程 |

---

### 10.6 性能指标要求

```yaml
# 性能基线 (源自4.0合并文档简化)

system:
  uptime: 99.9%
  startup_time: < 30s
  shutdown_time: < 10s

response_times:
  button_click: <= 100ms
  page_switch: <= 500ms
  data_query: <= 1s
  api_call: <= 500ms

resource_usage:
  cpu_warning: 80%
  cpu_critical: 90%
  memory_warning: 85%
  memory_critical: 95%
  disk_warning: 80%
  disk_critical: 90%

monitoring:
  health_check_interval: 60s
  metrics_report_interval: 300s
  alert_delay: 30s
```

---

### 10.7 AI模块开发规范（AI自主量化系统）

#### 10.7.1 AI模块目录结构

```python
# AI模块必须放在 src/ai/ 目录下
src/ai/
├── __init__.py
├── market_regime.py       # A01 市场状态识别
├── strategy_router.py     # A02 策略路由器
├── dynamic_risk.py        # A03 动态风控
├── strategy_optimizer.py  # A04 策略优化器
├── feedback_loop.py       # A05 反馈学习闭环
└── approval_ui.py        # A06 授权确认界面
```

#### 10.7.2 AI模块编写标准

```python
"""市场状态识别模块

功能：根据技术指标判断市场所处状态
"""
import logging
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """市场状态枚举"""
    BULL = "牛市"        # 上升趋势
    BEAR = "熊市"        # 下降趋势
    SIDEWAYS = "震荡"    # 盘整
    HIGH_VOL = "高波动"  # 市场恐慌
    LOW_VOL = "低波动"   # 市场平静

class MarketRegimeDetector:
    """市场状态检测器

    职责：根据市场指标判断当前市场状态

    输入：
        - 技术指标（MA斜率、ATR、波动率等）
        - 市场宽度（涨跌停数量、成交量）

    输出：
        - MarketRegime 枚举值
        - 置信度 (0.0 - 1.0)

    示例：
        >>> detector = MarketRegimeDetector()
        >>> regime, confidence = detector.detect(indicators)
        >>> print(f"市场状态: {regime.value}, 置信度: {confidence:.2f}")
    """

    def __init__(self, config: Dict):
        self.config = config
        self._init_parameters()

    def _init_parameters(self) -> None:
        """初始化检测参数"""
        self.trend_threshold = self.config.get('trend_threshold', 0.05)
        self.volatility_threshold = self.config.get('volatility_threshold', 0.03)

    def detect(self, indicators: Dict) -> tuple[MarketRegime, float]:
        """检测市场状态

        参数：
            indicators: 技术指标字典

        返回：
            (市场状态, 置信度)

        异常：
            ValueError: 指标数据不完整
        """
        required = ['ma_slope_20d', 'atr_pct', 'volume_ratio']
        for key in required:
            if key not in indicators:
                raise ValueError(f"缺少必要指标: {key}")

        trend = indicators['ma_slope_20d']
        volatility = indicators['atr_pct']

        if trend > self.trend_threshold and volatility > self.volatility_threshold:
            return MarketRegime.BULL, 0.85
        elif trend < -self.trend_threshold and volatility > self.volatility_threshold:
            return MarketRegime.BEAR, 0.85
        elif volatility < 0.015:
            return MarketRegime.LOW_VOL, 0.70
        else:
            return MarketRegime.SIDEWAYS, 0.60
```

#### 10.7.3 AI模块配置文件

```yaml
# config/ai/regime_config.yaml
market_regime:
  trend_threshold: 0.05      # 趋势判定阈值
  volatility_threshold: 0.03  # 波动率阈值
  lookback_period: 20         # 回看周期

strategy_router:
  regime_strategies:
    BULL:
      - S001  # 趋势跟踪
      - S002  # 均线策略
      - S076  # 成长因子
    BEAR:
      - S056  # 价值投资
      - S057  # 超跌反弹
    SIDEWAYS:
      - S031  # 均值回归
      - S032  # 布林带策略
    HIGH_VOL:
      - S091  # 低波动策略
    LOW_VOL:
      - S056  # 价值投资

dynamic_risk:
  BULL:
    stop_loss: 0.07           # 7%止损
    max_position: 1.0        # 100%仓位
    max_drawdown: 0.15       # 15%最大回撤
  BEAR:
    stop_loss: 0.03           # 3%止损
    max_position: 0.2        # 20%仓位
    max_drawdown: 0.05       # 5%最大回撤
  SIDEWAYS:
    stop_loss: 0.05
    max_position: 0.5
    max_drawdown: 0.10
```

#### 10.7.4 AI模块测试要求

```python
# tests/unit/test_market_regime.py
import pytest
from src.ai.market_regime import MarketRegimeDetector, MarketRegime

class TestMarketRegimeDetector:
    """市场状态检测器测试"""

    def setup_method(self):
        self.detector = MarketRegimeDetector({'trend_threshold': 0.05})

    def test_bull_market_detection(self):
        """测试牛市检测"""
        indicators = {
            'ma_slope_20d': 0.08,
            'atr_pct': 0.04,
            'volume_ratio': 1.5
        }
        regime, confidence = self.detector.detect(indicators)
        assert regime == MarketRegime.BULL
        assert confidence > 0.8

    def test_missing_indicator_raises_error(self):
        """测试缺少指标抛出异常"""
        indicators = {'ma_slope_20d': 0.08}
        with pytest.raises(ValueError):
            self.detector.detect(indicators)
```

#### 10.7.5 AI模块安全规范

| 规则 | 说明 | 违规处罚 |
|------|------|----------|
| **禁止硬编码** | 所有AI参数必须从配置文件读取 | 🔴 严重 |
| **禁止直接交易** | AI只生成建议，必须人工授权 | 🔴 严重 |
| **风控不可绕过** | 风控规则优先级高于AI建议 | 🔴 严重 |
| **日志完整** | AI决策必须记录完整日志 | 🟡 中等 |
| **异常处理** | AI出错必须降级到人工决策 | 🟡 中等 |

---

## 十二、异常处理

```python
from src.core.exceptions import DataException, FactorException

def fetch_data(symbol: str):
    if not symbol:
        raise DataException(f"Invalid symbol: {symbol}", code="DATA_001")
```

---

## 十一、相关文档

| 文档 | 说明 |
|------|------|
| [INDEX.md](./docs/INDEX.md) | 完整文档导航 |
| [QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md) | 命令速查表 |
| [System_Manifest.md](./docs/System_Manifest.md) | 系统清单、模块、权限 |
| [API_Contract.md](./docs/API_Contract.md) | 模块接口定义 |

---

**最后更新**: 2026-03-28
