# DEPLOYMENT.md - 部署规格

> **版本**：v4.0
> **日期**：2026-03-28
> **状态**：设计阶段

---

## 1. 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                     开发环境 (本地)                           │
│   quant_system_v4/                                         │
│   └── 开发、测试、调试                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                           │
│   ├── quant_system          # 主容器                        │
│   ├── redis                # 缓存 (可选)                    │
│   └── mongodb             # 日志存储 (可选)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     生产环境 (云服务器)                       │
│   • 阿里云/腾讯云                                           │
│   • 2核4G配置起步                                           │
│   • 自动备份                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Docker配置

### 2.1 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# 复制代码
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/  # 初始数据目录

# 环境变量
ENV PYTHONPATH=/app
ENV CONFIG_DIR=/app/config

EXPOSE 8000

CMD ["python", "-m", "src.main"]
```

### 2.2 docker-compose.yml

```yaml
version: '3.8'

services:
  quant_system:
    build: .
    container_name: quant_system_v4
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - ./output:/app/output
    environment:
      - MODE=${MODE:-backtest}
      - TZ=Asia/Shanghai
    restart: unless-stopped
    networks:
      - quant_network

  # 可选：Redis缓存
  redis:
    image: redis:7-alpine
    container_name: quant_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - quant_network

networks:
  quant_network:
    driver: bridge

volumes:
  redis_data:
```

---

## 3. 环境配置

### 3.1 开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3.2 生产环境

```bash
# 拉取代码
git clone <repo_url> quant_system_v4
cd quant_system_v4

# 配置环境变量
cp .env.example .env
# 编辑.env填入敏感信息

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 4. 运维手册

### 4.1 日常运维

```bash
# 查看系统状态
docker-compose ps

# 查看日志
docker-compose logs -f --tail=100

# 重启服务
docker-compose restart

# 更新代码
git pull
docker-compose build
docker-compose up -d
```

### 4.2 数据备份

```bash
# 备份数据目录
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 备份SQLite
cp data/quant.db data/quant.db.backup
```

### 4.3 监控

```bash
# 检查磁盘空间
df -h

# 检查内存
free -h

# 检查容器状态
docker stats
```

---

## 5. 灾难恢复

| 场景 | 恢复方案 |
|------|----------|
| 容器崩溃 | `docker-compose restart` |
| 数据损坏 | 从备份恢复 `tar -xzf backup_*.tar.gz` |
| 服务器故障 | 重新部署 + 从备份恢复 |
| 代码回滚 | `git revert` + `docker-compose build` |

详见：[disaster-recovery.md](../../docs/technical-specs/architecture/disaster-recovery.md)

---

## 6. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 初始版本，部署规格设计 |
