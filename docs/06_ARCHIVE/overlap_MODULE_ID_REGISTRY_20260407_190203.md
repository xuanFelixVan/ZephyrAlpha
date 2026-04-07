---
module_id: MODULE_ID_REGISTRY
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - Module ID 注册表文档
---

﻿---
module_id: MODULE_ID_REGISTRY_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 审计系统
standard_type: 审计管理文档
applicable_scope: 全系统module_id管理
compliance_level: 专业标准
responsibility:
  - 审计报告、合规检查

---
---

# Module ID 注册表
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0.0
> **创建日期**: 2026-04-06
> **核心定位**: 全系统module_id唯一性管理和查询
> **索引**: `MODULE_ID_REGISTRY_001`

---

## 📋 注册表概览

### 统计信息

| 指标 | 数值 |
|------|------|
| **总module_id数** | 903 |
| **活跃文档** | 903 |
| **归档文档** | 排除 |
| **重复ID** | 0 ✅ |

### 命名规范

#### 前缀规范

| 前缀 | 含义 | 示例 |
|------|------|------|
| `LAYER1_` | Layer 1 数据预处理层 | `LAYER1_DATA_PREPROCESSING_001` |
| `LAYER2_` | Layer 2 数据源层 | `LAYER2_DATA_SOURCE_001` |
| `LAYER3_` | Layer 3 中观策略层 | `LAYER3_ALPHA_FACTOR_001` |
| `LAYER4_` | Layer 4 交易策略层 | `LAYER4_TRADING_STRATEGY_001` |
| `LAYER5_` | Layer 5 执行层 | `LAYER5_EXECUTION_001` |
| `LAYER6_` | Layer 6 组合优化层 | `LAYER6_PORTFOLIO_OPT_001` |
| `LAYER7_` | Layer 7 AI报告层 | `LAYER7_AI_REPORT_001` |
| `LAYER8_` | Layer 8 人机交互层 | `LAYER8_HUMAN_AI_001` |
| `MESO_` | 中观层职责 | `MESO_MARKET_REGIME_001` |
| `MACRO_` | 宏观层职责 | `MACRO_STRATEGIC_WEIGHTING_001` |
| `MICRO_` | 微观层职责 | `MICRO_INTRADAY_STRATEGY_001` |
| `ARCHIVED_` | 归档文档 | `ARCHIVED_IMPL_DATA_SECURITY_BP_001` |

#### 命名规则

1. **唯一性**: 每个module_id必须全局唯一
2. **可读性**: ID应反映文档职责和层级
3. **一致性**: 同类文档使用统一命名格式
4. **可追溯**: ID变更需记录变更历史

---

## 🔍 查询指南

### 按层级查询

#### Layer 1 数据预处理层

```bash
# 查询Layer 1相关module_id
grep -r "^module_id: LAYER1_" docs/ --include="*.md"
```

#### Layer 2 数据源层

```bash
# 查询Layer 2相关module_id
grep -r "^module_id: LAYER2_" docs/ --include="*.md"
```

#### Layer 3 中观策略层

```bash
# 查询Layer 3相关module_id
grep -r "^module_id: LAYER3_" docs/ --include="*.md"
grep -r "^module_id: MESO_" docs/ --include="*.md"
```

#### Layer 4 交易策略层

```bash
# 查询Layer 4相关module_id
grep -r "^module_id: LAYER4_" docs/ --include="*.md"
```

#### Layer 5 执行层

```bash
# 查询Layer 5相关module_id
grep -r "^module_id: LAYER5_" docs/ --include="*.md"
grep -r "^module_id: MICRO_" docs/ --include="*.md"
```

#### Layer 6 组合优化层

```bash
# 查询Layer 6相关module_id
grep -r "^module_id: LAYER6_" docs/ --include="*.md"
```

#### Layer 7 AI报告层

```bash
# 查询Layer 7相关module_id
grep -r "^module_id: LAYER7_" docs/ --include="*.md"
```

#### Layer 8 人机交互层

```bash
# 查询Layer 8相关module_id
grep -r "^module_id: LAYER8_" docs/ --include="*.md"
```

### 按职责查询

#### 市场状态识别

```bash
# 查询市场状态识别相关module_id
grep -r "MARKET_REGIME" docs/ --include="*.md" | grep "module_id:"
```

#### 风险预算

```bash
# 查询风险预算相关module_id
grep -r "RISK_BUDGET" docs/ --include="*.md" | grep "module_id:"
```

#### 数据质量

```bash
# 查询数据质量相关module_id
grep -r "DATA_QUALITY" docs/ --include="*.md" | grep "module_id:"
```

---

## 📊 注册表维护

### 新增module_id流程

1. **检查唯一性**: 在注册表中搜索确认ID未被使用
2. **遵循规范**: 使用正确的层级前缀和命名格式
3. **记录变更**: 在文档变更历史中记录ID创建
4. **更新注册表**: 将新ID添加到注册表

### 修改module_id流程

1. **评估影响**: 分析ID变更对其他文档的影响
2. **创建备份**: Git提交当前状态
3. **批量替换**: 更新所有引用该ID的文档
4. **更新注册表**: 修改注册表中的ID记录
5. **验证修复**: 运行审计检查确认无重复

### 删除module_id流程

1. **确认归档**: 文档已移至archive目录
2. **添加前缀**: 为归档文档ID添加`ARCHIVED_`前缀
3. **更新状态**: 修改文档status为`Archived`
4. **更新注册表**: 在注册表中标记为归档状态

---

## 🛡️ 防重复机制

### 自动检查脚本

```powershell
# 检查module_id重复
$files = Get-ChildItem -Path "docs" -Recurse -Filter "*.md" |
         Where-Object { $_.FullName -notlike "*audit_state*" -and
                       $_.FullName -notlike "*archive*" }

$moduleIds = @{}
foreach ($file in $files) {
    $content = Get-Content $file.FullName -First 20
    $moduleIdLine = $content | Where-Object { $_ -match "^module_id:" } |
                    Select-Object -First 1
    if ($moduleIdLine) {
        $moduleId = $moduleIdLine.Trim()
        if ($moduleIds.ContainsKey($moduleId)) {
            $moduleIds[$moduleId] += @($file.FullName)
        } else {
            $moduleIds[$moduleId] = @($file.FullName)
        }
    }
}

$duplicates = $moduleIds.GetEnumerator() |
              Where-Object { $_.Value.Count -gt 1 }

if ($duplicates) {
    Write-Host "发现重复的module_id:" -ForegroundColor Red
    $duplicates | Format-Table
} else {
    Write-Host "✅ 未发现重复的module_id" -ForegroundColor Green
}
```

### Git Hook检查

建议在Git pre-commit hook中添加module_id重复检查，防止重复ID被提交。

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建，包含903个module_id | 审计系统 |

---

## 🔗 相关文档

- 专业文档治理审计指南
- 文档治理审计检查清单
- 审计标准v5.1
- 深度系统审计报告V12

---

**注册表状态**: ✅ 活跃
**维护频率**: 每周更新
**下次更新**: 2026-04-13
