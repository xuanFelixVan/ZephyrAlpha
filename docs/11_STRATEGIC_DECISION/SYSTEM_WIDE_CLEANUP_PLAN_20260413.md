---
module_id: SYSTEM_CLEANUP_PLAN_001
version: 1.0.0
status: Active
priority: P2
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 系统清理负责人
responsibility:
  - 系统全面清理规划
  - 废墟文件识别与清理
  - 存储空间优化
layer: layer_11
---

# 系统全面大清洗方案

> **执行日期**: 2026-04-13  
> **影响范围**: D:\ZephyrAlpha 全系统  
> **预计回收空间**: ~50 MB

---

## 执行摘要

经过全面废墟扫描，系统存在严重"数字废墟"问题，主要由脚本暴走产生。本方案提供分阶段、可回滚的清理策略。

### 问题统计

| 问题类型 | 数量 | 严重程度 | 预计回收空间 |
|---------|------|---------|-------------|
| .bak 备份文件 | 699 个 | 🔴 严重 | ~20 MB |
| 空目录 | 61 个 | 🟡 中等 | - |
| 重复文件 | 42 组 | 🟡 中等 | ~5 MB |
| 大PDF文件 | 2 个 | 🟢 低 | ~100 MB (可选) |
| 日志文件 | 5 个 | 🟢 低 | ~10 KB |

---

## 阶段一：低风险清理（立即执行）

### 1.1 清理 .bak 备份文件

**影响**: 699 个文件  
**风险**: 极低（.bak 是明确备份标记）  
**操作**:

```powershell
# 扫描所有 .bak 文件
Get-ChildItem -Path "D:\ZephyrAlpha" -Recurse -Filter "*.bak" | 
    Select-Object FullName, Length

# 移动到归档目录（安全做法）
$backupDir = "D:\ZephyrAlpha\99_ARCHIVE\BAK_FILES_20260413"
New-Item -ItemType Directory -Force -Path $backupDir

Get-ChildItem -Path "D:\ZephyrAlpha\scripts" -Filter "*.bak" | 
    Move-Item -Destination $backupDir
```

**预期结果**: 回收 ~20 MB 空间

### 1.2 清理空目录

**影响**: 61 个空目录（主要在 06_ARCHIVE）  
**风险**: 低  
**操作**:

```python
# 使用脚本清理空目录
python scripts/cleanup_empty_directories.py --execute
```

**清单**: 查看 `reports/system_cleanup_analysis_20260413_135615.md` 第3节

### 1.3 清理日志文件

**影响**: 5 个日志文件  
**风险**: 低  
**操作**: 压缩或移动到 logs/archive/

---

## 阶段二：中风险清理（需验证）

### 2.1 处理重复文件

**发现**: 42 组重复文件  
**主要原因**: Layer目录整合过程中产生（原文件和归档文件重复）  

**重复文件清单**（部分）:
- `docs/01_FRAMEWORK/integrated_from_01_Layer_Definition/INDEX.md`
- `docs/99_ARCHIVE/01_Layer_Definition_INTEGRATED_20260413_135113/INDEX.md`

**建议操作**:
1. 保留标准目录中的文件
2. 删除 99_ARCHIVE 中的重复文件
3. 或者保留 99_ARCHIVE，删除 integrated_from_* 中的文件

### 2.2 整合残留目录评估

**需人工决策的目录**:

| 目录 | 文件数 | 建议 |
|------|--------|------|
| `08_HUMAN_AI_INTERFACE/` | 156个 | 保留，可能是有效内容 |
| `09_RESEARCH_INNOVATION/` | 30个 | 评估后整合到 09_AUDIT/ |
| `07_RESEARCH/` | 18个 | 评估后整合到 07_GOVERNANCE_COMPLIANCE/ |
| `06_CONSTRUCTION_DOCS/` | 4个 | 评估是否迁移到 05_IMPLEMENTATION/ |
| `12_MODULE_DESIGNS/` | 3个 | 评估后整合 |

---

## 阶段三：高风险决策（需谨慎）

### 3.1 大文件处理

**发现**:
- `docs/00_RESOURCES/04_PLATFORM_DOCS/QMT_TRADING_SYSTEM_REFERENCE.pdf` (50.77 MB)
- `docs/00_RESOURCES/04_PLATFORM_DOCS/xuntou_qmt_trading_system_documentation.pdf` (50.77 MB)

**建议**:
- ✅ 保留：可能是重要参考资料
- 或者移动到外部存储/CDN

### 3.2 .audit_fix_backup 目录评估

**路径**: `D:\ZephyrAlpha\.audit_fix_backup\`  
**内容**: 包含 docs/ 下多个目录的备份  
**建议**: 
- 评估备份时间，如果是最新的可以考虑清理
- 或者压缩归档

---

## 自动化清理脚本

### 脚本清单

| 脚本 | 功能 | 状态 |
|------|------|------|
| `scripts/comprehensive_system_cleanup_analysis.py` | 废墟扫描 | ✅ 已完成 |
| `scripts/cleanup_bak_files.py` | 清理.bak文件 | ⬜ 待创建 |
| `scripts/cleanup_empty_directories.py` | 清理空目录 | ⬜ 待创建 |
| `scripts/deduplicate_files.py` | 去重处理 | ⬜ 待创建 |

### 执行顺序

```bash
# 1. 分析（已完成）
python scripts/comprehensive_system_cleanup_analysis.py

# 2. 清理 .bak 文件
python scripts/cleanup_bak_files.py --dry-run
python scripts/cleanup_bak_files.py --execute

# 3. 清理空目录
python scripts/cleanup_empty_directories.py --dry-run
python scripts/cleanup_empty_directories.py --execute

# 4. 去重
python scripts/deduplicate_files.py --dry-run
python scripts/deduplicate_files.py --execute

# 5. 验证
python scripts/comprehensive_system_cleanup_analysis.py
```

---

## 预期效果

### 清理前后对比

| 指标 | 清理前 | 清理后（预估） | 改善 |
|------|--------|---------------|------|
| 总文件数 | 6,819 | ~6,000 | -12% |
| 总目录数 | 672 | ~600 | -11% |
| 总大小 | 224 MB | ~200 MB | -11% |
| .bak 文件 | 699 | 0 | -100% |
| 空目录 | 61 | 0 | -100% |

### 系统健康度提升

- **存储空间**: 回收 ~24 MB
- **文件结构**: 更清晰，减少噪音
- **扫描速度**: 提升（文件减少12%）
- **可维护性**: 显著提升

---

## 风险控制

### 回滚策略

1. **所有删除操作先移动到归档目录**，不永久删除
2. **保留 99_ARCHIVE/** 作为安全网
3. **定期备份**（建议每周一次）

### 验证检查

每次清理后运行：
```bash
python scripts/comprehensive_system_cleanup_analysis.py
```

确认无新增问题。

---

## 后续建议

### 预防措施

1. **脚本规范**: 所有脚本在执行前创建 .bak 应有清理机制
2. **定期审计**: 每周运行一次废墟检查
3. **CI/CD 集成**: 在 GitHub Actions 中添加清理检查

### 监控指标

- 每周 .bak 文件增长率
- 空目录数量
- 重复文件组数

---

**版本**: v1.0.0  
**更新日期**: 2026-04-13  
**状态**: 待执行
