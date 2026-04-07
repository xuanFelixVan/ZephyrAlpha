---
module_id: QUICK_REFERENCE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 快速参文档
---

﻿---
module_id: QUICK_REFERENCE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 系统实施与部署管理与优化维护

---
---

---
module_id: IMPL_QUICK_REFERENCE_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: INDEX.md
implementation_status: 进行?---



# 快速参?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 的常用命令、API和配置速查?


## 1. 常用命令速查?

### Git命令

```bash
# 查看状?
git status

# 查看日志
git log --oneline -10

# 添加文件
git add .

# 提交
git commit -m "feat: 描述"

# 推?
git push origin main

# 拉取
git pull origin main

# 创建分支
git checkout -b feature/xxx

# 切换分支
git checkout main

# 合并分支
git merge feature/xxx

# 删除分支
git branch -d feature/xxx
```

### Docker命令

```bash
# 构建镜像
docker build -t qingfeng:v4.0.2 .

# 运行容器
docker run -d --name qingfeng qingfeng:v4.0.2

# 查看容器
docker ps -a

# 查看日志
docker logs -f qingfeng

# 停止容器
docker stop qingfeng

# 删除容器
docker rm qingfeng

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
```

### Python命令

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环?
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py

# 运行测试
pytest tests/ -v

# 生成覆盖率报?
pytest tests/ --cov=src --cov-report=html
```

### 系统命令

```bash
# 查看进程
ps aux | grep python

# 查看端口占用
netstat -ano | findstr :8000

# 查看磁盘空间
df -h

# 查看内存使用
free -h

# 查看CPU使用
top

# 查看日志
tail -f logs/error.log
```


## 2. API快速参?

### DataHub API

```python
from qingfeng.modules import DataHub

datahub = DataHub()

# 获取OHLCV数据
data = datahub.get_ohlcv(
    symbol="000001.SZ",
    start_date="2026-01-01",
    end_date="2026-03-28",
    frequency="daily"
)

# 获取财务数据
financial = datahub.get_financial(
    symbol="000001.SZ",
    report_date="2025-12-31"
)

# 获取行业数据
industry = datahub.get_industry(symbol="000001.SZ")
```

### FactorCalculator API

```python
from qingfeng.modules import FactorCalculator

calculator = FactorCalculator()

# 计算单个因子
factor_value = calculator.calculate(
    factor_id="ALPHA_001",
    symbol="000001.SZ",
    data=ohlcv_data
)

# 计算多个因子
factors = calculator.calculate_batch(
    factor_ids=["ALPHA_001", "ALPHA_002", "ALPHA_003"],
    symbol="000001.SZ",
    data=ohlcv_data
)
```

### StrategyEngine API

```python
from qingfeng.modules import StrategyEngine

engine = StrategyEngine()

# 生成交易信号
signal = engine.generate_signal(
    strategy_id="S001",
    factors=factor_values,
    market_data=ohlcv_data
)

# 获取策略配置
config = engine.get_config(strategy_id="S001")

# 更新策略参数
engine.update_params(
    strategy_id="S001",
    params={"ma_short": 15, "ma_long": 45}
)
```

### TradeExecutor API

```python
from qingfeng.modules import TradeExecutor

executor = TradeExecutor()

# 执行交易
order = executor.execute(
    symbol="000001.SZ",
    action="buy",
    quantity=1000,
    price=15.5,
    order_type="limit"
)

# 查询订单状?
status = executor.get_order_status(order_id="ORD_001")

# 取消订单
executor.cancel_order(order_id="ORD_001")
```


## 3. 配置文件模板

### system.yaml

```yaml
# 系统配置
system:
  name: "清风量化交易系统"
  version: "4.0.2"
  environment: "production"  # development, staging, production
  
# 数据库配?
database:
  host: "localhost"
  port: 5432
  user: "qingfeng"
  password: "${DB_PASSWORD}"
  database: "qingfeng"
  pool_size: 20
  
# 缓存配置
cache:
  host: "localhost"
  port: 6379
  db: 0
  ttl: 3600
  
# 消息队列配置
kafka:
  brokers:
    - "localhost:9092"
  topic_prefix: "qingfeng"
  
# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/app.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

### strategies.yaml

```yaml
# 策略配置
strategies:
  S001:
    name: "均线趋势跟踪"
    enabled: true
    params:
      ma_short: 20
      ma_long: 50
      stop_loss: 0.05
      take_profit: 0.15
    
  S002:
    name: "双均线MACD"
    enabled: false
    params:
      fast_period: 12
      slow_period: 26
      signal_period: 9
      
# 风险控制配置
risk_control:
  max_position_size: 0.1  # 单个头寸最大占?
  max_daily_loss: 0.02    # 单日最大亏?
  max_drawdown: 0.2       # 最大回?
  
# 交易配置
trading:
  market_open: "09:30"
  market_close: "15:00"
  min_volume: 100000      # 最小成交量
  max_slippage: 0.001     # 最大滑?
```

### factors.yaml

```yaml
# 因子配置
factors:
  ALPHA_001:
    name: "动量因子"
    category: "趋势"
    enabled: true
    params:
      period: 20
      
  ALPHA_002:
    name: "均值回归因?
    category: "均值回?
    enabled: true
    params:
      period: 30
      
# 因子权重
factor_weights:
  ALPHA_001: 0.1
  ALPHA_002: 0.15
  ALPHA_003: 0.12
  # ... 其他因子
```


## 4. 常见问题速查

### Q: 如何启动系统?

```bash
cd ZephyrAlpha
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py --mode production
```

### Q: 如何运行回测?

```bash
python scripts/backtest.py \
  --strategy S001 \
  --start-date 2025-01-01 \
  --end-date 2026-03-28 \
  --output results/backtest_s001.html
```

### Q: 如何查看日志?

```bash
# 实时查看
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看交易日志
tail -f logs/trading.log
```

### Q: 如何更新策略参数?

```python
from qingfeng.modules import StrategyEngine

engine = StrategyEngine()
engine.update_params(
    strategy_id="S001",
    params={"ma_short": 15, "ma_long": 45}
)
```

### Q: 如何部署到生产环境？

```bash
# 1. 构建镜像
docker build -t qingfeng:v4.0.2 .

# 2. 推送到仓库
docker push registry.example.com/qingfeng:v4.0.2

# 3. 部署到Kubernetes
kubectl apply -f k8s/

# 4. 验证部署
kubectl get pods
kubectl logs -f deployment/qingfeng-datahub
```


## 5. 性能优化建议

### 数据库优?

```sql
-- 创建索引
CREATE INDEX idx_symbol_date ON market_data(symbol, date);
CREATE INDEX idx_factor_date ON factor_data(factor_id, date);

-- 查询优化
EXPLAIN ANALYZE SELECT * FROM market_data WHERE symbol='000001.SZ' AND date>'2026-01-01';

-- 表分?
ALTER TABLE market_data PARTITION BY RANGE (YEAR(date)) (
  PARTITION p2025 VALUES LESS THAN (2026),
  PARTITION p2026 VALUES LESS THAN (2027)
);
```

### 缓存优化

```python
# 使用多层缓存
from qingfeng.cache import MultiLevelCache

cache = MultiLevelCache(
    l1=MemoryCache(max_size=10000),
    l2=RedisCache(ttl=3600),
    l3=DiskCache(ttl=86400)
)

# 预热缓存
cache.warmup(symbols=["000001.SZ", "000002.SZ", ...])
```

### 计算优化

```python
# 使用向量化计?
import numpy as np

prices = np.array([100, 101, 102, 103])
returns = np.diff(prices) / prices[:-1]  # 快速计?

# 使用JIT编译
from numba import jit

@jit(nopython=True)
def fast_calculation(data):
    result = np.zeros(len(data))
    for i in range(len(data)):
        result[i] = data[i] * 2
    return result
```


## 6. 监控指标速查

### 系统指标

| 指标 | 正常范围 | 告警阈?|
|------|---------|---------|
| CPU使用?| < 70% | > 80% |
| 内存使用?| < 75% | > 85% |
| 磁盘使用?| < 80% | > 90% |
| 网络延迟 | < 50ms | > 100ms |

### 应用指标

| 指标 | 正常范围 | 告警阈?|
|------|---------|---------|
| 请求延迟(P99) | < 500ms | > 1000ms |
| 错误?| < 0.1% | > 1% |
| 缓存命中?| > 90% | < 80% |
| 吞吐?| > 1000 QPS | < 100 QPS |

### 业务指标

| 指标 | 正常范围 | 告警阈?|
|------|---------|---------|
| 年化收益 | > 15% | < 5% |
| 夏普比率 | > 1.0 | < 0.5 |
| 最大回?| < 15% | > 20% |
| 胜率 | > 50% | < 40% |


**最后更?*: 2026-03-28  
**维护?*: 清风量化系统
