---
module_id: DEPLOYMENT_BLUEPRINT_001
version: 1.0
status: Active
last_updated: 2026-03-28
---

# 部署蓝图

> 清风量化系统 v4.0 的部署架构和流程

---

## 1. 部署架构

### 1.1 开发环境

**目标**: 本地开发和测试

**配置**:
```
本地机器 (Windows/Mac/Linux)
├── Python 3.9+
├── 虚拟环境 (venv)
├── 依赖包 (requirements.txt)
├── 本地数据库 (SQLite)
└── 本地缓存 (内存)
```

**启动命令**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py --mode dev
```

---

### 1.2 测试环境

**目标**: 功能测试和集成测试

**配置**:
```
测试服务器
├── Docker容器 (单机)
├── PostgreSQL (测试数据库)
├── Redis (测试缓存)
├── 测试数据集 (1年历史数据)
└── 监控工具 (Prometheus)
```

**部署命令**:
```bash
docker-compose -f docker-compose.test.yml up -d
pytest tests/ -v
```

---

### 1.3 模拟环境

**目标**: 模拟交易验证

**配置**:
```
模拟服务器
├── Docker容器 (多机器)
├── PostgreSQL (生产级数据库)
├── Redis集群 (高可用缓存)
├── Kafka (消息队列)
├── 完整历史数据 (5年)
└── 监控告警 (Prometheus + Grafana)
```

**部署命令**:
```bash
docker-compose -f docker-compose.staging.yml up -d
./scripts/init-staging.sh
```

---

### 1.4 生产环境

**目标**: 实盘交易

**配置**:
```
生产集群 (Kubernetes)
├── 8个FactorCalculator容器 (并行计算)
├── 2个StrategyEngine容器 (高可用)
├── 2个TradeExecutor容器 (高可用)
├── PostgreSQL主从 (数据持久化)
├── Redis集群 (高可用缓存)
├── Kafka集群 (消息队列)
├── ELK日志系统 (日志聚合)
├── Prometheus + Grafana (监控告警)
└── Vault (密钥管理)
```

**部署命令**:
```bash
kubectl apply -f k8s/
./scripts/init-production.sh
```

---

## 2. 部署流程

### 2.1 代码构建

**步骤**:
1. 代码检查 (pylint, flake8)
2. 单元测试 (pytest)
3. 代码覆盖率检查 (coverage > 80%)
4. 构建Docker镜像
5. 推送到镜像仓库

**命令**:
```bash
# 代码检查
pylint src/
flake8 src/

# 单元测试
pytest tests/unit/ -v --cov=src

# 构建镜像
docker build -t qingfeng:v4.0.2 .
docker push registry.example.com/qingfeng:v4.0.2
```

---

### 2.2 依赖安装

**步骤**:
1. 安装Python依赖
2. 安装系统依赖
3. 验证依赖版本
4. 生成依赖锁文件

**命令**:
```bash
# 安装依赖
pip install -r requirements.txt

# 生成锁文件
pip freeze > requirements.lock

# 验证依赖
pip check
```

---

### 2.3 配置初始化

**步骤**:
1. 加载系统配置
2. 初始化数据库
3. 初始化缓存
4. 初始化消息队列
5. 验证配置有效性

**命令**:
```bash
# 初始化数据库
python scripts/init_db.py

# 初始化缓存
python scripts/init_cache.py

# 验证配置
python scripts/validate_config.py
```

---

### 2.4 数据准备

**步骤**:
1. 下载历史数据
2. 数据清洗
3. 数据预处理
4. 数据验证
5. 数据备份

**命令**:
```bash
# 下载数据
python scripts/download_data.py --start 2021-01-01 --end 2026-03-28

# 数据清洗
python scripts/clean_data.py

# 数据验证
python scripts/validate_data.py
```

---

### 2.5 系统启动

**步骤**:
1. 启动基础服务 (数据库、缓存、消息队列)
2. 启动核心模块 (DataHub、FactorCalculator等)
3. 启动监控系统 (Prometheus、Grafana)
4. 启动告警系统 (AlertManager)
5. 健康检查

**命令**:
```bash
# 启动所有服务
docker-compose up -d

# 健康检查
./scripts/health_check.sh

# 查看日志
docker-compose logs -f
```

---

## 3. 容器化方案

### 3.1 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ src/
COPY config/ config/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "src/main.py"]
```

---

### 3.2 Docker Compose

```yaml
version: '3.8'

services:
  # 数据库
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: qingfeng
      POSTGRES_USER: qingfeng
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # 缓存
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  # 消息队列
  kafka:
    image: confluentinc/cp-kafka:6.0.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    ports:
      - "9092:9092"

  # 数据中心
  datahub:
    build: .
    environment:
      MODULE: datahub
      DB_HOST: postgres
      REDIS_HOST: redis
      KAFKA_HOST: kafka
    depends_on:
      - postgres
      - redis
      - kafka
    ports:
      - "8001:8000"

  # 因子计算 (8个并行)
  factor_calculator_1:
    build: .
    environment:
      MODULE: factor_calculator
      INSTANCE: 1
      DB_HOST: postgres
      REDIS_HOST: redis
    depends_on:
      - postgres
      - redis

  # ... factor_calculator_2 到 factor_calculator_8

  # 策略引擎
  strategy_engine:
    build: .
    environment:
      MODULE: strategy_engine
      DB_HOST: postgres
      REDIS_HOST: redis
    depends_on:
      - postgres
      - redis
    ports:
      - "8003:8000"

  # 交易执行
  trade_executor:
    build: .
    environment:
      MODULE: trade_executor
      DB_HOST: postgres
      REDIS_HOST: redis
    depends_on:
      - postgres
      - redis
    ports:
      - "8004:8000"

  # 监控
  prometheus:
    image: prom/prometheus
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

---

### 3.3 Kubernetes配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qingfeng-datahub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qingfeng-datahub
  template:
    metadata:
      labels:
        app: qingfeng-datahub
    spec:
      containers:
      - name: datahub
        image: registry.example.com/qingfeng:v4.0.2
        env:
        - name: MODULE
          value: "datahub"
        - name: DB_HOST
          value: "postgres-service"
        - name: REDIS_HOST
          value: "redis-service"
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 4. 监控告警

### 4.1 系统监控

**指标**:
- CPU使用率
- 内存使用率
- 磁盘使用率
- 网络流量
- 进程数

**告警规则**:
```yaml
- alert: HighCPUUsage
  expr: cpu_usage > 80
  for: 5m
  annotations:
    summary: "CPU使用率过高"

- alert: HighMemoryUsage
  expr: memory_usage > 85
  for: 5m
  annotations:
    summary: "内存使用率过高"
```

---

### 4.2 性能监控

**指标**:
- 请求延迟
- 吞吐量
- 错误率
- 缓存命中率

**告警规则**:
```yaml
- alert: HighLatency
  expr: request_latency_p99 > 1000
  for: 5m
  annotations:
    summary: "请求延迟过高"

- alert: HighErrorRate
  expr: error_rate > 1%
  for: 5m
  annotations:
    summary: "错误率过高"
```

---

### 4.3 业务监控

**指标**:
- 策略信号数
- 交易成交数
- 投资组合收益
- 风险指标

**告警规则**:
```yaml
- alert: NoSignal
  expr: signal_count == 0
  for: 1h
  annotations:
    summary: "1小时内无交易信号"

- alert: HighDrawdown
  expr: max_drawdown > 20%
  for: 1d
  annotations:
    summary: "最大回撤超过20%"
```

---

## 5. 灾备恢复

### 5.1 备份策略

**数据库备份**:
```bash
# 每天凌晨2点执行全量备份
0 2 * * * pg_dump qingfeng > /backup/qingfeng_$(date +\%Y\%m\%d).sql

# 每小时执行增量备份
0 * * * * pg_basebackup -D /backup/incremental_$(date +\%Y\%m\%d\%H)
```

**配置备份**:
```bash
# 备份配置文件
tar -czf /backup/config_$(date +%Y%m%d).tar.gz config/

# 备份代码
git archive --format tar.gz HEAD > /backup/code_$(date +%Y%m%d).tar.gz
```

---

### 5.2 恢复流程

**数据库恢复**:
```bash
# 1. 停止应用
docker-compose down

# 2. 恢复数据库
psql qingfeng < /backup/qingfeng_20260328.sql

# 3. 启动应用
docker-compose up -d

# 4. 验证数据
./scripts/verify_data.sh
```

---

### 5.3 故障转移

**主从切换**:
```bash
# 1. 检测主库故障
./scripts/check_primary.sh

# 2. 提升从库为主库
pg_ctl promote -D /var/lib/postgresql/data

# 3. 更新连接配置
sed -i 's/primary_host/secondary_host/g' config/database.yaml

# 4. 重启应用
docker-compose restart
```

---

## 6. 扩展性方案

### 6.1 水平扩展

**因子计算扩展**:
```bash
# 从8个容器扩展到16个
docker-compose up -d --scale factor_calculator=16
```

**策略引擎扩展**:
```bash
# 使用Kubernetes自动扩展
kubectl autoscale deployment qingfeng-strategy-engine --min=2 --max=10 --cpu-percent=80
```

---

### 6.2 垂直扩展

**增加单机资源**:
```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "2000m"
  limits:
    memory: "4Gi"
    cpu: "4000m"
```

---

### 6.3 性能优化

**缓存优化**:
```python
# 使用多层缓存
cache = MultiLevelCache(
    l1=MemoryCache(max_size=10000),
    l2=RedisCache(ttl=3600),
    l3=DiskCache(ttl=86400)
)
```

**计算优化**:
```python
# 使用向量化计算
factors = np.vectorize(calculate_factor)(data)

# 使用JIT编译
@numba.jit
def fast_calculation(data):
    return data * 2
```

---

## 7. 部署检查清单

- [ ] 代码检查通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 代码覆盖率 > 80%
- [ ] Docker镜像构建成功
- [ ] 配置文件验证通过
- [ ] 数据库初始化完成
- [ ] 缓存初始化完成
- [ ] 监控系统启动
- [ ] 告警规则配置
- [ ] 备份策略配置
- [ ] 健康检查通过
- [ ] 性能基准测试通过
- [ ] 文档更新完成

---

**最后更新**: 2026-03-28  
**维护者**: 清风量化系统
