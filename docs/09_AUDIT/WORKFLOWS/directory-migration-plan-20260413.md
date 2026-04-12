# 目录命名违规迁移计划

**文档编号**: DIR_MIGRATION_PLAN_001  
**版本**: 1.0.0  
**创建日期**: 2026-04-13  
**责任层级**: Layer 09 - 审计与质量  
**关联检查**: D-07 目录命名规范检测

---

## 一、迁移概述

### 1.1 背景

外部审计发现系统存在 **16个历史遗留违规目录**，这些目录在 `check_directory_naming.py` 实施前已存在，需要逐步迁移到合规命名。

### 1.2 迁移原则

| 原则 | 说明 |
|------|------|
| **渐进式** | 每次迭代处理1-3个目录，避免大规模重构风险 |
| **可追溯** | 保留迁移记录，支持回滚 |
| **最小影响** | 优先处理活跃区目录，归档区目录延后处理 |
| **自动化** | 使用脚本批量更新引用路径 |

### 1.3 违规目录清单

| 序号 | 违规目录 | 违规类型 | 所在区域 | 建议新名称 | 优先级 |
|------|----------|----------|----------|------------|--------|
| 1 | `module_designs` | Layer命名 | docs/根目录 | `12_MODULE_DESIGNS` | 🔴 高 |
| 2 | `05_BACKTEST` | 禁止词test | 02_FACTOR_LIBRARY/ | `05_FACTOR_VALIDATION` | 🔴 高 |
| 3 | `17_FACTOR_BACKTEST_ENHANCED` | 禁止词test | 02_FACTOR_LIBRARY/ | `17_ADVANCED_VALIDATION` | 🔴 高 |
| 4 | `05_BACKTEST_UI` | 禁止词test | 08_HUMAN_AI_INTERFACE/ | `05_VALIDATION_INTERFACE` | 🟡 中 |
| 5 | `59_PERFORMANCE_BENCHMARK_TESTING` | 禁止词test | 08_HUMAN_AI_INTERFACE/ | `59_PERFORMANCE_BENCHMARK` | 🟡 中 |
| 6 | `DATA_TESTING_FRAMEWORK` | 禁止词test | 02_FACTOR_LIBRARY/04_DATA_SOURCE/ | `DATA_QUALITY_FRAMEWORK` | 🟡 中 |
| 7 | `TEMPLATES` | 禁止词temp | 09_AUDIT/ | `DOCUMENT_TEMPLATES` | 🟡 中 |
| 8 | `04_CONFIG_TEMPLATES` | 禁止词temp | 05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/ | `04_CONFIG_PATTERNS` | 🟡 中 |
| 9 | `46_BACKUP_RECOVERY` | 禁止词backup | 08_HUMAN_AI_INTERFACE/ | `46_DISASTER_RECOVERY` | 🟡 中 |
| 10 | `DATA_BACKUP_RECOVERY` | 禁止词backup | 02_FACTOR_LIBRARY/04_DATA_SOURCE/ | `DATA_RESILIENCE` | 🟡 中 |
| 11 | `20260407_old_layer_audit_reports` | 禁止词old | 06_ARCHIVE/ | `20260407_LEGACY_AUDIT_REPORTS` | 🟢 低 |
| 12 | `20260410_c2_document_metadata_template` | 禁止词temp | 06_ARCHIVE/ | `20260410_C2_DOCUMENT_METADATA` | 🟢 低 |
| 13 | `20260410_system_manifest_backup` | 禁止词backup | 06_ARCHIVE/ | `20260410_SYSTEM_MANIFEST_ARCHIVE` | 🟢 低 |
| 14 | `encoding_backups` | 禁止词backup | 06_ARCHIVE/ | `ENCODING_ARCHIVES` | 🟢 低 |
| 15 | `temporary` | 禁止词temp | 06_ARCHIVE/ | `TEMP_PROCESSING_202604` | 🟢 低 |
| 16 | `temp_pending` | 禁止词temp | 06_ARCHIVE/ | `PENDING_REVIEW_202604` | 🟢 低 |

---

## 二、分阶段迁移计划

### 阶段1: 活跃区高优先级（第1-2周）

**目标目录**: `module_designs`, `05_BACKTEST`, `17_FACTOR_BACKTEST_ENHANCED`

**迁移步骤**:

1. **预检查**
   ```bash
   # 检查目录引用数量
   grep -r "12_MODULE_DESIGNS" docs/ --include="*.md" | wc -l
   grep -r "05_BACKTEST" docs/ --include="*.md" | wc -l
   ```

2. **创建新目录**
   ```bash
   mkdir docs/12_MODULE_DESIGNS
   mkdir docs/02_FACTOR_LIBRARY/05_FACTOR_VALIDATION
   mkdir docs/02_FACTOR_LIBRARY/17_ADVANCED_VALIDATION
   ```

3. **迁移内容**
   ```bash
   # 使用脚本批量迁移
   python scripts/migrate_directory.py \
     --from docs/module_designs \
     --to docs/12_MODULE_DESIGNS \
     --update-links
   ```

4. **更新索引**
   ```bash
   python scripts/sync_index.py --dir docs/12_MODULE_DESIGNS
   ```

5. **验证**
   ```bash
   python scripts/check_directory_naming.py
   python scripts/run_comprehensive_audit.py
   ```

6. **归档旧目录**（验证通过后1周）
   ```bash
   mv docs/module_designs docs/06_ARCHIVE/20260413_module_designs_deprecated
   ```

### 阶段2: 活跃区中优先级（第3-4周）

**目标目录**: `05_BACKTEST_UI`, `59_PERFORMANCE_BENCHMARK_TESTING`, `DATA_TESTING_FRAMEWORK`

### 阶段3: 配置与模板（第5周）

**目标目录**: `TEMPLATES`, `04_CONFIG_TEMPLATES`, `46_BACKUP_RECOVERY`, `DATA_BACKUP_RECOVERY`

### 阶段4: 归档区清理（第6-8周）

**目标目录**: 06_ARCHIVE/ 下的所有违规目录

---

## 三、迁移脚本

### 3.1 目录迁移脚本

```python
#!/usr/bin/env python3
# scripts/migrate_directory.py

import shutil
from pathlib import Path

def migrate_directory(from_dir: Path, to_dir: Path, update_links: bool = True):
    """迁移目录并更新所有引用"""
    
    # 1. 复制目录内容
    shutil.copytree(from_dir, to_dir)
    
    # 2. 更新所有.md文件中的链接
    if update_links:
        update_all_links(from_dir, to_dir)
    
    # 3. 更新SITEMAP
    update_sitemap(from_dir, to_dir)
    
    # 4. 生成迁移报告
    generate_migration_report(from_dir, to_dir)

def update_all_links(old_path: Path, new_path: Path):
    """批量更新文档中的链接"""
    old_rel = old_path.relative_to(DOCS_ROOT)
    new_rel = new_path.relative_to(DOCS_ROOT)
    
    for md_file in DOCS_ROOT.rglob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        updated = content.replace(str(old_rel), str(new_rel))
        if updated != content:
            md_file.write_text(updated, encoding='utf-8')
```

### 3.2 迁移验证脚本

```bash
#!/bin/bash
# scripts/verify_migration.sh

echo "迁移验证..."

# 1. 检查新目录存在
if [ ! -d "$2" ]; then
    echo "❌ 新目录不存在: $2"
    exit 1
fi

# 2. 检查旧目录引用
refs=$(grep -r "$1" docs/ --include="*.md" | wc -l)
if [ $refs -gt 0 ]; then
    echo "⚠️ 仍有 $refs 个引用指向旧目录"
    grep -r "$1" docs/ --include="*.md"
fi

# 3. 运行全面检查
python scripts/run_comprehensive_audit.py

echo "✅ 验证完成"
```

---

## 四、风险控制

### 4.1 回滚计划

每个迁移批次必须满足以下条件才能执行：
- [ ] 完整备份已创建
- [ ] 迁移脚本已测试通过
- [ ] 回滚方案已准备
- [ ] 非工作时间执行

**回滚命令**:
```bash
# 紧急回滚
rm -rf docs/NEW_DIR
mv docs/06_ARCHIVE/OLD_DIR_deprecated docs/OLD_DIR
# 恢复链接（从git历史）
git checkout HEAD -- docs/
```

### 4.2 兼容性处理

对于外部系统的硬编码路径：
1. 在旧目录保留 `README.md` 指向新位置（保留1个月）
2. 在系统日志中记录迁移信息
3. 通知所有相关人员

---

## 五、进度追踪

| 阶段 | 计划时间 | 状态 | 负责人 |
|------|----------|------|--------|
| 阶段1: 活跃区高优先级 | 2026-04-13 ~ 04-27 | ⏳ 待开始 | 待分配 |
| 阶段2: 活跃区中优先级 | 2026-04-28 ~ 05-11 | ⏳ 待开始 | 待分配 |
| 阶段3: 配置与模板 | 2026-05-12 ~ 05-18 | ⏳ 待开始 | 待分配 |
| 阶段4: 归档区清理 | 2026-05-19 ~ 06-08 | ⏳ 待开始 | 待分配 |

---

## 六、关联文档

- [新目录创建SOP](./new-directory-creation-workflow.md)
- 目录命名检查脚本
- [外部审计安全评估](../../11_STRATEGIC_DECISION/EXTERNAL_AUDIT_SECURITY_ASSESSMENT_20260413.md)

---

**下次审查**: 每阶段完成后审查并更新本计划
