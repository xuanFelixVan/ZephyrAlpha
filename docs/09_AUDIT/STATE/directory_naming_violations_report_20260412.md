---
module_id: DIR_NAMING_VIOLATIONS_REPORT_001_2162
version: 1.0.0
status: Active
created_date: 2026-04-12
last_updated: 2026-04-12
owner: 首席文档架构师
standard_type: 审计报告
applicable_scope: 全系统目录命名合规性
compliance_level: 强制修复
layer: layer_09
responsibility:
  - 记录目录命名违规发现
  - 提供修复建议和时间表
  - 跟踪修复进度
---

# 目录命名违规审计报告

> **审计日期**: 2026-04-12
> **审计工具**: `scripts/check_directory_naming.py --verbose`
> **审计范围**: `docs/` 全目录
> **违规总数**: 16 个
> **风险等级**: 🔴 **高** — 需要立即修复

```
```---
```

## 执行摘要

本次审计使用升级后的目录命名规范检查器扫描全系统，发现 **16 个目录命名违规**。其中：

| 违规类型 | 数量 | 占比 | 风险等级 |
|---------|------|------|---------|
| Layer 目录命名违规 | 1 | 6% | 🔴 高 |
| 禁止关键词（test） | 6 | 38% | 🟡 中 |
| 禁止关键词（backup） | 3 | 19% | 🟡 中 |
| 禁止关键词（temp） | 4 | 25% | 🟡 中 |
| 禁止关键词（old） | 1 | 6% | 🟢 低 |
| **总计** | **16** | **100%** | — |

```
```---
```

## 详细违规清单

### 🔴 P0: 立即修复（Layer 目录违规）

#### 1. `module_designs` — Layer 目录命名违规

**问题描述**:
- 路径: `docs/module_designs`
- 问题: 不符合一级目录命名规范 `数字_大写下划线` 格式
- 当前名称: `module_designs`（小写，无数字前缀）
- 应有名称: `12_MODULE_DESIGNS`

**影响分析**:
- ⚠️ 与现有 `docs/12_MODULE_DESIGNS/` 目录重复
- ⚠️ 造成命名混乱，破坏层级结构一致性
- ⚠️ 可能影响 SITEMAP.md 和 INDEX.md 的权威性

**修复建议**:
```bash
# 方案 A: 如果内容与 12_MODULE_DESIGNS 重复，直接删除
rm -rf docs/module_designs

# 方案 B: 如果内容唯一，合并到 12_MODULE_DESIGNS
mv docs/module_designs/* docs/12_MODULE_DESIGNS/
rmdir docs/module_designs
```

**验证方式**:
```bash
python scripts/check_directory_naming.py --verbose | grep module_designs
# 应无输出
```

```
```---
```

### 🟡 P1: 本周修复（禁止关键词）

#### 2-3. `BACKTEST` 相关目录（含 test）

| # | 违规路径 | 关键词 | 建议新名称 |
|---|---------|-------|-----------|
| 2 | `02_FACTOR_LIBRARY/05_BACKTEST` | test | `05_BACKTESTING` 或 `05_BT_ENGINE` |
| 3 | `02_FACTOR_LIBRARY/17_FACTOR_BACKTEST_ENHANCED` | test | `17_FACTOR_BT_ENHANCED` |
| 10 | `08_HUMAN_AI_INTERFACE/05_BACKTEST_UI` | test | `05_BT_UI` 或 `05_BACKTESTING_UI` |
| 12 | `08_HUMAN_AI_INTERFACE/59_PERFORMANCE_BENCHMARK_TESTING` | test | `59_PERF_BENCHMARK_VALIDATION` |
| 15 | `02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_TESTING_FRAMEWORK` | test | `DATA_VALIDATION_FRAMEWORK` |

**修复命令示例**:
```bash
# 示例: 修复 02_FACTOR_LIBRARY/05_BACKTEST
cd docs/02_FACTOR_LIBRARY
mv 05_BACKTEST 05_BACKTESTING
# 更新所有引用该路径的文件
```

#### 4-9, 11, 13-16. 其他禁止关键词

| # | 违规路径 | 关键词 | 建议新名称 | 优先级 |
|---|---------|-------|-----------|--------|
| 4 | `06_ARCHIVE/20260407_old_layer_audit_reports` | old | `20260407_LAYER_AUDIT_REPORTS` | P2 |
| 5 | `06_ARCHIVE/20260410_c2_document_metadata_template` | temp | `20260410_C2_DOC_METADATA_TMPL` | P2 |
| 6 | `06_ARCHIVE/20260410_system_manifest_backup` | backup | `20260410_SYSTEM_MANIFEST_BAK` | P2 |
| 7 | `06_ARCHIVE/encoding_backups` | backup | `ENCODING_ARCHIVES` 或 `ENCODING_STORE` | P1 |
| 8 | `06_ARCHIVE/temporary` | temp | `TEMP_HOLDING` → 或合并到其他目录 | P1 |
| 9 | `06_ARCHIVE/temp_pending` | temp | `PENDING_ITEMS` | P1 |
| 11 | `08_HUMAN_AI_INTERFACE/46_BACKUP_RECOVERY` | backup | `46_DISASTER_RECOVERY` 或 `46_DATA_RECOVERY` | P1 |
| 13 | `09_AUDIT/TEMPLATES` | temp | `TEMPLATE_LIBRARY` 或 `FORM_TEMPLATES` | P1 |
| 14 | `02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_BACKUP_RECOVERY` | backup | `DATA_RECOVERY` | P1 |
| 16 | `05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/04_CONFIG_TEMPLATES` | temp | `04_CONFIG_TMPL` 或 `04_CONFIGURATION_TEMPLATES` | P1 |

```
```---
```

## 批量修复脚本

### 步骤 1: 创建修复脚本

```bash
#!/bin/bash
# scripts/fix_directory_naming_violations.sh

cd docs

# P0: 修复 module_designs
echo "修复 P0: module_designs..."
if [ -d "module_designs" ]; then
    if [ -d "12_MODULE_DESIGNS" ]; then
        # 合并内容
        cp -r module_designs/* 12_MODULE_DESIGNS/ 2>/dev/null || true
        rm -rf module_designs
        echo "✅ 已合并到 12_MODULE_DESIGNS/"
    else
        mv module_designs 12_MODULE_DESIGNS
        echo "✅ 已重命名为 12_MODULE_DESIGNS/"
    fi
fi

# P1: 修复 BACKTEST 目录
echo "修复 P1: BACKTEST 目录..."
cd 02_FACTOR_LIBRARY
mv 05_BACKTEST 05_BACKTESTING 2>/dev/null || echo "⚠️ 05_BACKTEST 不存在或已修复"
mv 17_FACTOR_BACKTEST_ENHANCED 17_FACTOR_BT_ENHANCED 2>/dev/null || true
cd ..

# P1: 修复其他关键目录
echo "修复 P1: 其他关键目录..."
cd 06_ARCHIVE
mv temporary TEMP_HOLDING 2>/dev/null || true
mv temp_pending PENDING_ITEMS 2>/dev/null || true
mv encoding_backups ENCODING_ARCHIVES 2>/dev/null || true
cd ..

echo "修复完成！请运行验证命令:"
echo "  python scripts/check_directory_naming.py --verbose"
```

### 步骤 2: 运行修复脚本

```bash
chmod +x scripts/fix_directory_naming_violations.sh
./scripts/fix_directory_naming_violations.sh
```

### 步骤 3: 验证修复

```bash
# 重新运行检查
python scripts/check_directory_naming.py --verbose

# 预期结果: 应显示 "✅ 所有目录命名符合规范"
```

```
```---
```

## 影响评估

### 文件引用影响

以下文件可能包含对被修复目录的引用，需要同步更新：

```bash
# 查找所有引用 05_BACKTEST 的文件
grep -r "05_BACKTEST" docs/ --include="*.md" | head -20

# 查找所有引用 module_designs 的文件
grep -r "module_designs" docs/ --include="*.md" | head -20
```

**建议**: 使用自动化链接修复脚本更新引用：

```bash
python scripts/batch_fix_invalid_links_v2.py
```

### SITEMAP.md 更新

修复后需要更新 SITEMAP.md 中的目录映射：

```text
# 更新前
- \[module_designs/]<!-- -->(./module_designs/) - 模块设计草图

# 更新后
- \[12_MODULE_DESIGNS/]<!-- -->(./12_MODULE_DESIGNS/) - 模块设计草图
```

```
```---
```

## 修复时间表

| 阶段 | 任务 | 负责人 | 截止日期 | 验收标准 |
|------|------|--------|---------|---------|
| **P0** | 修复 `module_designs` 目录 | 文档架构师 | 2026-04-13 | 检查通过 |
| **P1** | 修复 `BACKTEST` / `test` 相关目录 | 开发团队 | 2026-04-15 | 检查通过 |
| **P1** | 修复 `backup` / `temp` 相关目录（活跃区） | 开发团队 | 2026-04-17 | 检查通过 |
| **P2** | 修复归档区违规目录 | 维护团队 | 2026-04-20 | 检查通过 |
| **验证** | 全量检查 + 链接修复 | QA 团队 | 2026-04-22 | 0 违规 |

```
```---
```

## 预防措施

### 已实施的防护措施

1. ✅ **L0 Pre-commit 钩子**: 已扩大检测范围至所有 `docs/` 文件
2. ✅ **D-06 升级**: 目录映射缺失已升级为阻止级错误
3. ✅ **命名规范**: 规则已明确记录在 `check_directory_naming.py`

### 建议额外措施

1. **CI/CD 集成**: 在 CI 流程中添加全量目录命名检查
   ```yaml
   - name: Directory Naming Check
     run: python scripts/check_directory_naming.py
   ```

2. **定期审计**: 每周运行一次全量检查并生成报告

3. **培训**: 为新成员提供目录命名规范培训

```
```---
```

## 附录：检查规则摘要

```python
# Layer主目录: 数字前缀+大写下划线
"^\d{2}_[A-Z_]+$"  # 如: 02_FACTOR_LIBRARY

# 子目录: 小写下划线 或 全大写下划线
"^[a-z0-9_]+|[A-Z0-9_]+$"

# 禁止关键词
temp, tmp, backup, old, test, new, draft, copy
副本, 备份, 临时, 测试, 无标题, 新建文件夹

# 最大深度: 6 层
```

```
```---
```

**报告生成**: 2026-04-12
**下次审计**: 2026-04-19
**状态**: 待修复
