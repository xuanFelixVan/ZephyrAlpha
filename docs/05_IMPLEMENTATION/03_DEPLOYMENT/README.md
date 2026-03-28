# 部署指南 (Deployment Guide)

> **适用**: 个人开发者部署到生产环境  
> **目标**: 一键部署，简单可靠

---

##  文档导航

| 文档 | 说明 | 难度 |
|------|------|------|
| [one-click-deploy.md](./one-click-deploy.md) | 一键部署脚本 |  |
| [backup-restore.md](./backup-restore.md) | 备份与恢复 |  |

---

##  快速部署

### Windows 部署

```powershell
# 1. 运行部署脚本
.\scripts\deploy.ps1

# 2. 验证部署
python scripts/health_check.py

# 3. 启动服务
python scripts/start_server.py
```

### Linux 部署

```bash
# 1. 运行部署脚本
bash scripts/deploy.sh

# 2. 验证部署
python scripts/health_check.py

# 3. 启动服务（systemd）
sudo systemctl start quant-system
```

---

##  部署检查清单

部署前检查：

- [ ] 服务器已准备（本地/云服务器）
- [ ] Python 3.8+ 已安装
- [ ] 数据库已配置（如使用）
- [ ] 环境变量已设置
- [ ] 防火墙规则已配置

部署后验证：

- [ ] 服务正常启动
- [ ] 日志正常输出
- [ ] 能够访问 API
- [ ] 监控正常

---

##  下一步

- [运维手册](../04_OPERATIONS/README.md)
- [监控配置](../04_OPERATIONS/monitoring.md)
- [常见问题](../04_OPERATIONS/faq.md)

---

**最后更新**: 2026-03-28  
**状态**:  可用
