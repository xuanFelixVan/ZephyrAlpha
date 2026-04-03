---
standard_type: 操作指南
applicable_scope: 全系�?compliance_level: 正式标准
parent_document: ../README.md
implementation_status: 已完�?owner: 运维团队
version: 1.0.0
module_id: DEPLOYMENT_MANUAL
created_date: 2026-04-02
last_updated: 2026-04-02
---
# 系统部署手册

**文档版本**: 1.0.0
**最后更�?*: 2026-04-02
**文档所有�?*: 运维团队

---

## 1. 部署概述

### 1.1 部署目标

本文档提供ZephyrAlpha量化交易系统的完整部署指南，确保系统在生产环境中稳定运行�?
### 1.2 部署范围

- 生产环境部署
- 测试环境部署
- 开发环境部�?- 灾备环境部署

### 1.3 部署前置条件

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker 20+（可选）
- 8GB+ 内存
- 100GB+ 磁盘空间

---

## 2. 环境准备

### 2.1 系统要求

**操作系统**:
- Windows Server 2019+
- Ubuntu 20.04+
- CentOS 8+

**硬件要求**:
- CPU: 4核心+
- 内存: 8GB+
- 磁盘: 100GB+ SSD
- 网络: 100Mbps+

### 2.2 软件依赖

**必需软件**:
```bash
# Python环境
Python 3.8+
pip 21+

# 数据�?PostgreSQL 12+
Redis 6+

# 可选容器化
Docker 20+
Docker Compose 2+
```

**Python依赖**:
```bash
pip install -r requirements.txt
```

### 2.3 环境变量配置

创建 `.env` 文件�?```bash
# 数据库配�?DATABASE_URL=postgresql://user:password@localhost:5432/zephyr
REDIS_URL=redis://localhost:6379/0

# API配置
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/zephyr.log

# 安全配置
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

---

## 3. 数据库部�?
### 3.1 PostgreSQL部署

**安装PostgreSQL**:
```bash
# Ubuntu
sudo apt-get install postgresql-12

# Windows
# 下载安装�? https://www.postgresql.org/download/windows/
```

**创建数据�?*:
```sql
CREATE DATABASE zephyr;
CREATE USER zephyr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE zephyr TO zephyr_user;
```

**初始化表结构**:
```bash
python scripts/init_database.py
```

### 3.2 Redis部署

**安装Redis**:
```bash
# Ubuntu
sudo apt-get install redis-server

# Windows
# 下载: https://github.com/microsoftarchive/redis/releases
```

**配置Redis**:
```bash
# 编辑配置文件
sudo vi /etc/redis/redis.conf

# 设置密码
requirepass your_redis_password

# 设置最大内�?maxmemory 2gb
maxmemory-policy allkeys-lru
```

**启动Redis**:
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

---

## 4. 应用部署

### 4.1 代码部署

**克隆代码**:
```bash
git clone https://github.com/your-org/zephyr-alpha.git
cd zephyr-alpha
```

**安装依赖**:
```bash
python -m venv venv
source venv/bin/activate  # Linux
# �?venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

**配置文件**:
```bash
# 复制配置模板
cp config/system_config_template.yaml config/system_config.yaml

# 编辑配置文件
vi config/system_config.yaml
```

### 4.2 数据初始�?
**初始化数据库**:
```bash
python scripts/init_database.py
```

**导入初始数据**:
```bash
python scripts/import_initial_data.py
```

**验证数据**:
```bash
python scripts/verify_data.py
```

### 4.3 服务启动

**启动API服务**:
```bash
# 开发模�?python -m uvicorn src.api.main:app --reload

# 生产模式
gunicorn src.api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

**启动策略引擎**:
```bash
python src/strategy_engine/main.py
```

**启动监控服务**:
```bash
python src/monitoring/main.py
```

---

## 5. Docker部署

### 5.1 构建镜像

**创建Dockerfile**:
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "src.api.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**构建镜像**:
```bash
docker build -t zephyr-alpha:latest .
```

### 5.2 Docker Compose部署

**创建docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:12
    environment:
      POSTGRES_DB: zephyr
      POSTGRES_USER: zephyr_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6
    command: redis-server --requirepass your_redis_password
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  api:
    image: zephyr-alpha:latest
    environment:
      DATABASE_URL: postgresql://zephyr_user:your_password@postgres:5432/zephyr
      REDIS_URL: redis://:your_redis_password@redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

**启动服务**:
```bash
docker-compose up -d
```

---

## 6. 生产环境配置

### 6.1 Nginx配置

**安装Nginx**:
```bash
sudo apt-get install nginx
```

**配置反向代理**:
```nginx
upstream zephyr_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.zephyr-alpha.com;

    location / {
        proxy_pass http://zephyr_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 6.2 SSL配置

**安装Certbot**:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

**获取SSL证书**:
```bash
sudo certbot --nginx -d api.zephyr-alpha.com
```

### 6.3 防火墙配�?
**配置防火墙规�?*:
```bash
# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许SSH
sudo ufw allow 22/tcp

# 启用防火�?sudo ufw enable
```

---

## 7. 监控部署

### 7.1 日志管理

**配置日志轮转**:
```bash
# 创建日志轮转配置
sudo vi /etc/logrotate.d/zephyr

/var/log/zephyr/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 zephyr zephyr
}
```

### 7.2 性能监控

**安装监控工具**:
```bash
pip install prometheus-client grafana-api
```

**配置Prometheus**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zephyr'
    static_configs:
      - targets: ['localhost:8000']
```

### 7.3 告警配置

**配置告警规则**:
```yaml
# alert_rules.yml
groups:
  - name: zephyr_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
```

---

## 8. 备份策略

### 8.1 数据库备�?
**创建备份脚本**:
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/zephyr_$DATE.sql"

pg_dump -U zephyr_user zephyr > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 删除30天前的备�?find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

**配置定时任务**:
```bash
# 每天凌晨2点备�?0 2 * * * /path/to/backup_database.sh
```

### 8.2 配置备份

**备份配置文件**:
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/config"
DATE=$(date +%Y%m%d)
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/
```

---

## 9. 故障排查

### 9.1 常见问题

**问题1: 数据库连接失�?*
```bash
# 检查数据库状�?sudo systemctl status postgresql

# 检查连�?psql -U zephyr_user -d zephyr -h localhost
```

**问题2: Redis连接失败**
```bash
# 检查Redis状�?sudo systemctl status redis

# 测试连接
redis-cli -a your_redis_password ping
```

**问题3: API服务无响�?*
```bash
# 检查进�?ps aux | grep gunicorn

# 检查端�?netstat -tlnp | grep 8000

# 查看日志
tail -f logs/error.log
```

### 9.2 日志查看

**查看应用日志**:
```bash
tail -f logs/zephyr.log
tail -f logs/access.log
tail -f logs/error.log
```

**查看系统日志**:
```bash
tail -f /var/log/syslog
tail -f /var/log/nginx/access.log
```

---

## 10. 安全加固

### 10.1 系统安全

**更新系统**:
```bash
sudo apt-get update
sudo apt-get upgrade
```

**禁用不必要的服务**:
```bash
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

### 10.2 应用安全

**配置安全�?*:
```python
# 在API中添加安全头
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**配置速率限制**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api/endpoint")
@limiter.limit("100/minute")
async def endpoint():
    pass
```

---

## 11. 性能优化

### 11.1 数据库优�?
**配置连接�?*:
```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

**创建索引**:
```sql
-- 为常用查询创建索�?CREATE INDEX idx_strategy_name ON strategies(name);
CREATE INDEX idx_order_time ON orders(created_at);
```

### 11.2 缓存优化

**配置Redis缓存**:
```python
import redis
from functools import wraps

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    password='your_redis_password',
    db=0
)

def cache_result(expire=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            result = redis_client.get(cache_key)
            if result:
                return result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire, result)
            return result
        return wrapper
    return decorator
```

---

## 12. 部署检查清�?
### 12.1 部署前检�?
- [ ] 环境变量已配�?- [ ] 数据库已创建
- [ ] Redis已启�?- [ ] 配置文件已更�?- [ ] 依赖已安�?- [ ] SSL证书已配�?- [ ] 防火墙规则已设置

### 12.2 部署后检�?
- [ ] API服务正常响应
- [ ] 数据库连接正�?- [ ] Redis连接正常
- [ ] 日志正常输出
- [ ] 监控正常工作
- [ ] 备份任务已配�?- [ ] 告警规则已配�?
---

## 13. 参考文�?
- [系统配置模板](../04_CONFIG_TEMPLATES/system_config_template.yaml)
- [监控手册](./MONITORING_MANUAL.md)
- [维护手册](./MAINTENANCE_MANUAL.md)
- [预部署检查清单](../06_CHECKLISTS/PRE_DEPLOYMENT_CHECKLIST.md)

---

**文档状�?*: 正式标准
**下次审查**: 2026-07-02
