---
module_id: FAQ_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 运维团队
standard_type: 专业量化机构指南
applicable_scope: ZephyrAlpha常见问题
---

# ZephyrAlpha常见问题FAQ

## 📋 文档概要

**文档职责**: 提供ZephyrAlpha系统的常见问题解答和解决方案
**适用范围**: 系统使用、故障排查、性能优化
**更新频率**: 每月更新

---

## 🚀 系统启动问题

### Q1: 应用启动失败，提示"ModuleNotFoundError"

**问题描述**:
```
ModuleNotFoundError: No module named 'zephyr'
```

**解决方案**:
```bash
# 1. 检查Python环境
python --version  # 确保Python 3.9+

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/zephyr"

# 4. 验证安装
python -c "import zephyr; print(zephyr.__version__)"
```

---

### Q2: 数据库连接失败，提示"Connection refused"

**问题描述**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**解决方案**:
```bash
# 1. 检查数据库服务状态
systemctl status postgresql

# 2. 检查数据库监听地址
sudo netstat -tulpn | grep 5432

# 3. 检查防火墙
sudo ufw status
sudo ufw allow 5432/tcp

# 4. 检查数据库配置
# postgresql.conf
listen_addresses = '*'

# pg_hba.conf
host all all 0.0.0.0/0 md5
```

---

### Q3: Redis连接失败，提示"Connection refused"

**问题描述**:
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

**解决方案**:
```bash
# 1. 检查Redis服务状态
systemctl status redis

# 2. 启动Redis服务
systemctl start redis

# 3. 检查Redis监听地址
redis-cli config get bind

# 4. 修改Redis配置
# /etc/redis/redis.conf
bind 0.0.0.0

# 5. 重启Redis
systemctl restart redis
```

---

## 💾 数据库问题

### Q4: 数据库迁移失败，提示"Target database is not up to date"

**问题描述**:
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**解决方案**:
```bash
# 1. 查看当前迁移版本
alembic current

# 2. 查看迁移历史
alembic history

# 3. 标记当前版本
alembic stamp head

# 4. 重新运行迁移
alembic upgrade head
```

---

### Q5: 数据库查询缓慢，响应时间超过10秒

**问题描述**:
数据库查询响应时间过长，影响系统性能。

**解决方案**:
```sql
-- 1. 分析查询计划
EXPLAIN ANALYZE SELECT * FROM factors WHERE name = 'momentum';

-- 2. 创建索引
CREATE INDEX idx_factors_name ON factors(name);

-- 3. 更新统计信息
ANALYZE factors;

-- 4. 检查锁等待
SELECT * FROM pg_stat_activity WHERE wait_event IS NOT NULL;

-- 5. 检查慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

---

### Q6: 数据库磁盘空间不足

**问题描述**:
数据库磁盘使用率超过90%，需要清理空间。

**解决方案**:
```sql
-- 1. 查看数据库大小
SELECT pg_size_pretty(pg_database_size('zephyr_alpha'));

-- 2. 查看表大小
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 3. 清理旧数据
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';

-- 4. 清理空间
VACUUM FULL;

-- 5. 重建索引
REINDEX DATABASE zephyr_alpha;
```

---

## 🔧 性能问题

### Q7: API响应时间过长，超过5秒

**问题描述**:
API接口响应缓慢，影响用户体验。

**解决方案**:
```bash
# 1. 检查应用日志
tail -f logs/app.log | grep "slow"

# 2. 检查数据库连接池
python scripts/check_db_pool.py

# 3. 检查缓存命中率
redis-cli info stats | grep hits

# 4. 优化查询
# 使用查询缓存
# 添加数据库索引
# 优化N+1查询

# 5. 增加缓存
# 使用Redis缓存热点数据
# 设置合理的过期时间
```

---

### Q8: 内存使用率过高，超过80%

**问题描述**:
系统内存使用率持续过高，可能导致OOM。

**解决方案**:
```bash
# 1. 检查内存使用
free -h
ps aux --sort=-%mem | head -10

# 2. 检查Python内存使用
python -c "import psutil; print(psutil.virtual_memory())"

# 3. 优化配置
# 减少worker数量
# 减少数据库连接池大小
# 减少缓存大小

# 4. 重启服务
systemctl restart zephyr-app
```

---

### Q9: CPU使用率过高，持续超过80%

**问题描述**:
系统CPU使用率持续过高，影响性能。

**解决方案**:
```bash
# 1. 检查CPU使用
top -p $(pgrep -d',' -f zephyr)

# 2. 分析CPU使用
py-spy top --pid $(pgrep -f zephyr)

# 3. 优化代码
# 使用性能分析工具
# 优化热点函数
# 使用异步处理

# 4. 调整并发配置
# 减少worker数量
# 调整线程池大小
```

---

## 🔐 安全问题

### Q10: 如何修改数据库密码？

**解决方案**:
```bash
# 1. 连接数据库
psql -U postgres

# 2. 修改密码
ALTER USER zephyr_user WITH PASSWORD 'new_secure_password';

# 3. 更新应用配置
# config/secrets/database.yaml
password: new_secure_password

# 4. 重启应用
systemctl restart zephyr-app
```

---

### Q11: 如何配置HTTPS？

**解决方案**:
```bash
# 1. 获取SSL证书
# 使用Let's Encrypt
certbot certonly --nginx -d zephyr-alpha.com

# 2. 配置Nginx
# /etc/nginx/sites-available/zephyr
server {
    listen 443 ssl;
    server_name zephyr-alpha.com;
    
    ssl_certificate /etc/letsencrypt/live/zephyr-alpha.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/zephyr-alpha.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}

# 3. 重启Nginx
systemctl restart nginx
```

---

### Q12: 如何限制API访问频率？

**解决方案**:
```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis()

async def rate_limit(request: Request, calls: int = 100, period: int = 60):
    ip = request.client.host
    key = f"rate_limit:{ip}"
    
    current = redis_client.get(key)
    if current and int(current) >= calls:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, period)
    pipe.execute()
```

---

## 📊 监控问题

### Q13: Prometheus无法采集指标

**问题描述**:
Prometheus无法从应用采集指标数据。

**解决方案**:
```bash
# 1. 检查指标端口
curl http://localhost:9090/metrics

# 2. 检查Prometheus配置
# prometheus.yml
scrape_configs:
  - job_name: 'zephyr'
    static_configs:
      - targets: ['localhost:9090']

# 3. 检查防火墙
sudo ufw allow 9090/tcp

# 4. 重启Prometheus
systemctl restart prometheus
```

---

### Q14: 告警通知未发送

**问题描述**:
触发告警规则但未收到通知。

**解决方案**:
```bash
# 1. 检查Alertmanager状态
systemctl status alertmanager

# 2. 检查Alertmanager配置
# alertmanager.yml
global:
  resolve_timeout: 5m
  
route:
  receiver: 'team-email'
  
receivers:
  - name: 'team-email'
    email_configs:
      - to: 'team@zephyr-alpha.com'
        from: 'alert@zephyr-alpha.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alert@zephyr-alpha.com'
        auth_password: 'app_password'

# 3. 测试告警
amtool alert add alertname="TestAlert" severity="warning"

# 4. 重启Alertmanager
systemctl restart alertmanager
```

---

## 🔄 备份恢复问题

### Q15: 如何备份和恢复数据库？

**解决方案**:
```bash
# 备份数据库
pg_dump -h localhost -U zephyr_user -d zephyr_alpha \
  -F c -f backup_$(date +%Y%m%d).dump

# 恢复数据库
pg_restore -h localhost -U zephyr_user -d zephyr_alpha \
  -j 4 backup_20260407.dump

# 自动备份脚本
# scripts/auto_backup.sh
#!/bin/bash
BACKUP_DIR="/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U zephyr_user -d zephyr_alpha \
  -F c -f ${BACKUP_DIR}/backup_${DATE}.dump

# 保留最近7天的备份
find ${BACKUP_DIR} -name "backup_*.dump" -mtime +7 -delete
```

---

## 📝 其他问题

### Q16: 如何查看系统日志？

**解决方案**:
```bash
# 查看应用日志
tail -f logs/app.log

# 查看系统日志
journalctl -u zephyr-app -f

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看数据库日志
tail -f /var/log/postgresql/postgresql-13-main.log
```

---

### Q17: 如何更新系统版本？

**解决方案**:
```bash
# 1. 备份数据
pg_dump -h localhost -U zephyr_user -d zephyr_alpha \
  -F c -f backup_before_update.dump

# 2. 拉取最新代码
git fetch --all
git checkout v1.1.0

# 3. 更新依赖
pip install -r requirements.txt

# 4. 运行迁移
alembic upgrade head

# 5. 重启服务
systemctl restart zephyr-app

# 6. 验证更新
curl http://localhost:8000/health
```

---

### Q18: 如何监控系统性能？

**解决方案**:
```bash
# 1. 使用系统监控工具
htop
iotop
nethogs

# 2. 使用应用监控
# Prometheus + Grafana
# 访问 http://localhost:3000

# 3. 使用日志分析
# ELK Stack
# 访问 http://localhost:5601

# 4. 使用APM工具
# Jaeger
# 访问 http://localhost:16686
```

---

## 🔗 相关文档

- [故障诊断指南](TROUBLESHOOTING_GUIDE.md)
- [错误代码参考](ERROR_CODES.md)
- [性能调优指南](PERFORMANCE_TUNING_GUIDE.md)
- [系统部署指南](../03_DEPLOYMENT/DEPLOYMENT_GUIDE.md)

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active
