# 运维手册 (Operations Manual)

> **适用**: 个人开发者运维系统  
> **目标**: 简单监控，快速排障

---

##  文档导航

| 文档 | 说明 | 重要性 |
|------|------|--------|
| [monitoring.md](./monitoring.md) | 监控配置 |  建议 |
| [faq.md](./faq.md) | 常见问题 |  必须 |
| [performance-tips.md](./performance-tips.md) | 性能优化 |  建议 |

---

##  日常运维

### 每日检查

```bash
# 1. 检查服务状态
python scripts/health_check.py

# 2. 查看错误日志
tail -100 logs/error.log

# 3. 检查磁盘空间
df -h
```

### 每周检查

```bash
# 1. 清理旧日志
find logs/ -name "*.log.*.gz" -mtime +7 -delete

# 2. 备份数据
python scripts/backup.py

# 3. 检查性能
python scripts/performance_report.py
```

---

##  故障排查

遇到问题时的步骤：

### Step 1: 查看错误日志

```bash
tail -f logs/error.log
```

### Step 2: 检查常见问题

查看 [faq.md](./faq.md) 寻找解决方案。

### Step 3: 重启服务

```bash
# 停止服务
python scripts/stop_server.py

# 启动服务
python scripts/start_server.py
```

---

##  监控指标

### 基础监控

- CPU 使用率：< 80%
- 内存使用率：< 90%
- 磁盘使用率：< 85%
- 网络延迟：< 100ms

### 业务监控

- 策略运行状态
- 订单成功率
- 数据更新频率

---

##  相关文档

- [部署指南](../03_DEPLOYMENT/README.md)
- [错误处理](../02_DEVELOPMENT/error-handling.md)

---

**最后更新**: 2026-03-28  
**状态**:  可用
