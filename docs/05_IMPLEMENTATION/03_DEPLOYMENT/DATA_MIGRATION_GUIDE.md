---
module_id: DATA_MIGRATION_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 运维团队
standard_type: 专业量化机构指南
applicable_scope: ZephyrAlpha数据迁移
responsibility:
  - DATA_MIGRATION操作指南
---

# ZephyrAlpha数据迁移指南

## 📋 文档概要

**文档职责**: 提供ZephyrAlpha系统的数据迁移流程和注意事项
**适用范围**: 版本升级、环境迁移、数据备份恢复
**前置条件**: 已完成系统部署和数据库配置

---

## 🎯 迁移目标

### 迁移原则

1. **数据完整性**: 确保数据不丢失、不损坏
2. **业务连续性**: 最小化业务中断时间
3. **可回滚性**: 支持迁移失败后的快速回滚
4. **可验证性**: 迁移结果可验证、可追溯

---

### 迁移类型

| 迁移类型 | 描述 | 风险等级 |
|---------|------|---------|
| **版本升级迁移** | 系统版本升级时的数据迁移 | 中 |
| **环境迁移** | 从一个环境迁移到另一个环境 | 高 |
| **数据备份恢复** | 从备份中恢复数据 | 低 |
| **数据整合迁移** | 多个数据源整合迁移 | 高 |

---

## 📦 迁移准备

### 1. 数据评估

#### 1.1 数据量评估

```sql
-- 评估数据库大小
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE pg_database.datname = 'zephyr_alpha';

-- 评估表大小
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### 1.2 数据质量检查

```sql
-- 检查数据完整性
SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT id) AS unique_ids,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) AS active_records
FROM factors;

-- 检查数据一致性
SELECT 
    table_name,
    column_name,
    COUNT(*) AS null_count
FROM information_schema.columns
WHERE table_schema = 'public'
GROUP BY table_name, column_name;
```

---

### 2. 迁移计划

#### 2.1 时间窗口

| 迁移阶段 | 预计时间 | 业务影响 |
|---------|---------|---------|
| **数据备份** | 1-2小时 | 无 |
| **数据导出** | 2-4小时 | 低 |
| **数据导入** | 4-8小时 | 高 |
| **数据验证** | 1-2小时 | 低 |
| **总计** | 8-16小时 | - |

#### 2.2 资源准备

- [ ] 备份存储空间（至少2倍数据量）
- [ ] 迁移服务器资源
- [ ] 网络带宽保障
- [ ] 人员安排（至少2人）

---

## 🚀 迁移流程

### 阶段1: 数据备份

#### 1.1 完整备份

```bash
# PostgreSQL完整备份
pg_dump -h localhost -U zephyr_user -d zephyr_alpha \
  -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# 验证备份文件
pg_restore --list backup_20260407_120000.dump
```

#### 1.2 增量备份

```bash
# WAL归档备份
pg_basebackup -h localhost -U replication_user \
  -D /backup/wal_backup -Ft -z -P

# 配置WAL归档
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal_archive/%f'
```

---

### 阶段2: 数据导出

#### 2.1 导出策略

**全量导出**:
```bash
# 导出所有数据
pg_dump -h source_host -U zephyr_user -d zephyr_alpha \
  -F c -f full_export.dump

# 导出特定表
pg_dump -h source_host -U zephyr_user -d zephyr_alpha \
  -t factors -t portfolios -F c -f partial_export.dump
```

**增量导出**:
```bash
# 导出指定时间范围的数据
pg_dump -h source_host -U zephyr_user -d zephyr_alpha \
  --column-inserts \
  --where="created_at > '2026-01-01'" \
  -t transactions > incremental_export.sql
```

#### 2.2 数据压缩

```bash
# 压缩导出文件
gzip full_export.dump

# 验证压缩文件
gunzip -t full_export.dump.gz
```

---

### 阶段3: 数据传输

#### 3.1 传输方式

**方式1: 直接传输**
```bash
# 使用scp传输
scp full_export.dump.gz target_host:/backup/

# 使用rsync传输（推荐）
rsync -avz --progress full_export.dump.gz target_host:/backup/
```

**方式2: 流式传输**
```bash
# 直接管道传输
pg_dump -h source_host -U zephyr_user -d zephyr_alpha \
  -F c | gzip | ssh target_host "cat > /backup/full_export.dump.gz"
```

#### 3.2 传输验证

```bash
# 验证文件完整性
md5sum full_export.dump.gz > full_export.dump.gz.md5

# 在目标端验证
md5sum -c full_export.dump.gz.md5
```

---

### 阶段4: 数据导入

#### 4.1 导入前准备

```bash
# 创建目标数据库
psql -h target_host -U postgres -c "CREATE DATABASE zephyr_alpha_new;"

# 创建用户和权限
psql -h target_host -U postgres -c "CREATE USER zephyr_user WITH PASSWORD 'secure_password';"
psql -h target_host -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE zephyr_alpha_new TO zephyr_user;"
```

#### 4.2 数据导入

```bash
# 解压文件
gunzip full_export.dump.gz

# 导入数据
pg_restore -h target_host -U zephyr_user -d zephyr_alpha_new \
  -j 4 --no-owner --no-privileges full_export.dump

# 验证导入
psql -h target_host -U zephyr_user -d zephyr_alpha_new -c "SELECT COUNT(*) FROM factors;"
```

#### 4.3 索引重建

```sql
-- 重建索引
REINDEX DATABASE zephyr_alpha_new;

-- 更新统计信息
ANALYZE;
```

---

### 阶段5: 数据验证

#### 5.1 数据量验证

```sql
-- 对比源库和目标库的数据量
-- 源库
SELECT 'factors' AS table_name, COUNT(*) AS count FROM factors
UNION ALL
SELECT 'portfolios', COUNT(*) FROM portfolios
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;

-- 目标库
SELECT 'factors' AS table_name, COUNT(*) AS count FROM factors
UNION ALL
SELECT 'portfolios', COUNT(*) FROM portfolios
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;
```

#### 5.2 数据质量验证

```sql
-- 验证数据完整性
SELECT 
    'factors' AS table_name,
    COUNT(*) AS total,
    COUNT(DISTINCT id) AS unique_ids,
    MIN(created_at) AS earliest,
    MAX(created_at) AS latest
FROM factors;

-- 验证数据一致性
SELECT 
    f.id,
    f.name,
    COUNT(p.id) AS portfolio_count
FROM factors f
LEFT JOIN portfolios p ON f.id = p.factor_id
GROUP BY f.id, f.name
HAVING COUNT(p.id) = 0;
```

#### 5.3 业务验证

```bash
# 运行业务验证脚本
python scripts/validate_migration.py --source source_host --target target_host

# 运行集成测试
pytest tests/integration/test_migration.py -v
```

---

## 🔄 切换流程

### 1. 应用切换

#### 1.1 停止源应用

```bash
# 停止应用服务
systemctl stop zephyr-app

# 确认服务已停止
systemctl status zephyr-app
```

#### 1.2 最终数据同步

```bash
# 同步最后的数据变更
pg_dump -h source_host -U zephyr_user -d zephyr_alpha \
  --data-only -t transactions > final_sync.sql

# 导入到目标库
psql -h target_host -U zephyr_user -d zephyr_alpha_new < final_sync.sql
```

#### 1.3 切换数据库连接

```bash
# 更新应用配置
sed -i 's/source_host/target_host/g' config/settings.yaml
sed -i 's/zephyr_alpha/zephyr_alpha_new/g' config/settings.yaml

# 重启应用
systemctl start zephyr-app
```

---

### 2. 验证切换

```bash
# 健康检查
curl http://localhost:8000/health

# 功能验证
pytest tests/smoke/ -v

# 性能验证
python scripts/check_performance.py
```

---

## 🚨 回滚流程

### 快速回滚

```bash
# 1. 停止目标应用
systemctl stop zephyr-app

# 2. 恢复数据库连接配置
sed -i 's/target_host/source_host/g' config/settings.yaml
sed -i 's/zephyr_alpha_new/zephyr_alpha/g' config/settings.yaml

# 3. 重启应用
systemctl start zephyr-app

# 4. 验证回滚
curl http://localhost:8000/health
```

---

## 📊 迁移检查清单

### 迁移前检查

- [ ] 数据量评估完成
- [ ] 数据质量检查通过
- [ ] 备份空间充足
- [ ] 迁移计划制定
- [ ] 人员安排到位

### 迁移中检查

- [ ] 数据备份完成
- [ ] 数据导出成功
- [ ] 数据传输完成
- [ ] 数据导入成功
- [ ] 数据验证通过

### 迁移后检查

- [ ] 应用切换成功
- [ ] 功能验证通过
- [ ] 性能指标正常
- [ ] 监控告警正常
- [ ] 文档更新完成

---

## 🔗 相关文档

- [系统部署指南](DEPLOYMENT_GUIDE.md)
- [环境配置指南](ENVIRONMENT_CONFIG_GUIDE.md)
- 故障诊断指南
- [常见问题FAQ](../07_OPERATIONS/IMPLEMENTATION_OPERATIONS_FAQ.md)

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active
