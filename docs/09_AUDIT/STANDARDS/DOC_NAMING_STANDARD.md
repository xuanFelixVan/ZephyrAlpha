# 文档命名规范（增强版）

**文档ID**: DOC_NAMING_STANDARD_001
**版本**: v2.0.0
**创建日期**: 2026-04-03
**状态**: Active
**适用范围**: 全系统文档命名管理

---

## 一、规范目标

### 1.1 质量目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 命名规范性 | 100% | 所有文档命名符合规范 |
| 命名一致性 | 100% | 同类文档使用相同命名格式 |
| 命名可读性 | 高 | 文件名易于理解和记忆 |
| 命名可维护性 | 高 | 文件名易于维护和更新 |

### 1.2 效率目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 文档识别时间 | ≤3秒 | 快速识别文档类型和内容 |
| 文档检索时间 | ≤5秒 | 快速检索文档 |
| 命名决策时间 | ≤10秒 | 快速确定文档命名 |

---

## 二、命名原则

### 2.1 核心原则

**原则1: 职责反映原则**
- 文件名必须反映文档核心职责
- 文件名应简洁明了
- 文件名应避免过于通用

**原则2: 英文优先原则**
- 使用英文命名，避免中文
- 使用标准英文单词
- 避免缩写和简写（除非是通用缩写）

**原则3: 版本标识原则**
- 重要文档需包含版本号
- 版本号格式统一（v1.0.0）
- 版本号位置统一

**原则4: 层级清晰原则**
- 使用下划线分隔层级
- 使用大写字母表示模块名
- 使用小写字母表示功能名

---

## 三、命名格式规范

### 3.1 蓝图文档命名

**格式**: `{MODULE_NAME}_BLUEPRINT.md`

**示例**:
```
STRATEGY_ENGINE_BLUEPRINT.md
RISK_MONITORING_BLUEPRINT.md
ECONOMIC_REGIME_ENGINE_BLUEPRINT.md
```

**命名规则**:
- 模块名使用大写字母
- 单词间使用下划线分隔
- 后缀统一为`_BLUEPRINT.md`

### 3.2 技术规格书命名

**格式**: `{MODULE_NAME}_TECHNICAL_SPECIFICATION.md`

**示例**:
```
SCENARIO_ANALYZER_TECHNICAL_SPECIFICATION.md
STRESS_TEST_REPORTER_TECHNICAL_SPECIFICATION.md
SIGNAL_QUALITY_REPORTER_TECHNICAL_SPECIFICATION.md
```

**命名规则**:
- 模块名使用大写字母
- 单词间使用下划线分隔
- 后缀统一为`_TECHNICAL_SPECIFICATION.md`

### 3.3 使用指南命名

**格式**: `{MODULE_NAME}_USAGE_GUIDE.md`

**示例**:
```
PORTFOLIO_OPTIMIZER_USAGE_GUIDE.md
FACTOR_LIBRARY_USAGE_GUIDE.md
BACKTEST_SYSTEM_USAGE_GUIDE.md
```

**命名规则**:
- 模块名使用大写字母
- 单词间使用下划线分隔
- 后缀统一为`_USAGE_GUIDE.md`

### 3.4 API文档命名

**格式**: `{MODULE_NAME}_API_REFERENCE.md`

**示例**:
```
LAYER7_REPORT_API_REFERENCE.md
FACTOR_ENGINE_API_REFERENCE.md
TRADING_SYSTEM_API_REFERENCE.md
```

**命名规则**:
- 模块名使用大写字母
- 单词间使用下划线分隔
- 后缀统一为`_API_REFERENCE.md`

### 3.5 索引文档命名

**格式**: `INDEX.md` 或 `{MODULE_NAME}_INDEX.md`

**示例**:
```
INDEX.md
FACTOR_LIBRARY_INDEX.md
IMPLEMENTATION_INDEX.md
```

**命名规则**:
- 主索引统一命名为`INDEX.md`
- 子索引可添加模块名前缀

### 3.6 审计报告命名

**格式**: `{REPORT_TYPE}_REPORT_{DATE}.md`

**示例**:
```
WEEKLY_SCAN_REPORT_001_20260403.md
DEEP_AUDIT_REPORT_20260403.md
LAYER7_AUDIT_REPORT_20260403.md
```

**命名规则**:
- 报告类型使用大写字母
- 日期格式为YYYYMMDD
- 后缀统一为`_REPORT_{DATE}.md`

### 3.7 规范文档命名

**格式**: `{STANDARD_TYPE}_STANDARD.md`

**示例**:
```
PATH_REFERENCE_STANDARD.md
DOC_REFERENCE_STANDARD.md
DOC_NAMING_STANDARD.md
```

**命名规则**:
- 规范类型使用大写字母
- 单词间使用下划线分隔
- 后缀统一为`_STANDARD.md`

---

## 四、命名模板库

### 4.1 蓝图文档模板

```
{MODULE_NAME}_BLUEPRINT.md

示例:
- STRATEGY_ENGINE_BLUEPRINT.md
- RISK_MONITORING_BLUEPRINT.md
- ECONOMIC_REGIME_ENGINE_BLUEPRINT.md
- PORTFOLIO_OPTIMIZER_BLUEPRINT.md
- FACTOR_ENGINE_BLUEPRINT.md
```

### 4.2 技术规格书模板

```
{MODULE_NAME}_TECHNICAL_SPECIFICATION.md

示例:
- SCENARIO_ANALYZER_TECHNICAL_SPECIFICATION.md
- STRESS_TEST_REPORTER_TECHNICAL_SPECIFICATION.md
- SIGNAL_QUALITY_REPORTER_TECHNICAL_SPECIFICATION.md
- ECONOMIC_REGIME_REPORTER_TECHNICAL_SPECIFICATION.md
```

### 4.3 使用指南模板

```
{MODULE_NAME}_USAGE_GUIDE.md

示例:
- PORTFOLIO_OPTIMIZER_USAGE_GUIDE.md
- FACTOR_LIBRARY_USAGE_GUIDE.md
- BACKTEST_SYSTEM_USAGE_GUIDE.md
- RISK_MONITORING_USAGE_GUIDE.md
```

### 4.4 API文档模板

```
{MODULE_NAME}_API_REFERENCE.md

示例:
- LAYER7_REPORT_API_REFERENCE.md
- FACTOR_ENGINE_API_REFERENCE.md
- TRADING_SYSTEM_API_REFERENCE.md
- RISK_MONITORING_API_REFERENCE.md
```

### 4.5 审计报告模板

```
{REPORT_TYPE}_REPORT_{DATE}.md

示例:
- WEEKLY_SCAN_REPORT_001_20260403.md
- DEEP_AUDIT_REPORT_20260403.md
- LAYER7_AUDIT_REPORT_20260403.md
- DOC_GOVERNANCE_REPORT_20260403.md
```

---

## 五、命名检查规则

### 5.1 禁止的命名

❌ **禁止使用**:

1. **中文文件名**
   ```
   ❌ 策略引擎蓝图.md
   ❌ 风险监控文档.md
   ❌ 因子库说明.md
   ```

2. **空格字符**
   ```
   ❌ Strategy Engine Blueprint.md
   ❌ Risk Monitoring Doc.md
   ```

3. **特殊字符**（除下划线、连字符外）
   ```
   ❌ Strategy@Engine#Blueprint.md
   ❌ Risk&Monitoring%Doc.md
   ```

4. **过于通用的命名**
   ```
   ❌ README.md（除非是项目根目录）
   ❌ DOCUMENT.md
   ❌ DOC.md
   ❌ NEW.md
   ❌ OLD.md
   ```

5. **过长的命名**（>50字符）
   ```
   ❌ THIS_IS_A_VERY_LONG_DOCUMENT_NAME_THAT_EXCEEDS_FIFTY_CHARACTERS_BLUEPRINT.md
   ```

### 5.2 推荐的命名

✅ **推荐使用**:

1. **职责明确的命名**
   ```
   ✅ STRATEGY_ENGINE_BLUEPRINT.md
   ✅ RISK_MONITORING_TECHNICAL_SPECIFICATION.md
   ✅ FACTOR_LIBRARY_USAGE_GUIDE.md
   ```

2. **格式统一的命名**
   ```
   ✅ MODULE_BLUEPRINT.md
   ✅ MODULE_TECHNICAL_SPECIFICATION.md
   ✅ MODULE_USAGE_GUIDE.md
   ```

3. **简洁明了的命名**
   ```
   ✅ INDEX.md
   ✅ README.md（项目根目录）
   ✅ CHANGELOG.md
   ```

---

## 六、命名检查工具

### 6.1 naming_validator.py（命名规范检查器）

**功能**:
- 检查文件名是否符合规范
- 检查是否有中文文件名
- 检查是否有特殊字符
- 检查命名长度
- 生成命名检查报告

**使用方式**:
```bash
# 检查单个文档
python scripts/naming_validator.py --doc docs/PATH/TO/DOC.md

# 检查整个目录
python scripts/naming_validator.py --dir docs/05_IMPLEMENTATION

# 检查全系统
python scripts/naming_validator.py --all
```

**输出示例**:
```
文档命名检查报告
==================
检查范围: docs/05_IMPLEMENTATION
检查时间: 2026-04-03

检查结果:
- 总文档数: 100
- 符合规范: 95
- 不符合规范: 5

问题详情:
1. [中文文件名] docs/05_IMPLEMENTATION/策略引擎蓝图.md
   - 建议: STRATEGY_ENGINE_BLUEPRINT.md

2. [空格字符] docs/05_IMPLEMENTATION/Strategy Engine Blueprint.md
   - 建议: STRATEGY_ENGINE_BLUEPRINT.md

3. [命名过长] docs/05_IMPLEMENTATION/THIS_IS_A_VERY_LONG_DOCUMENT_NAME_BLUEPRINT.md
   - 建议: 缩短文件名至50字符以内
```

### 6.2 命名建议生成工具

**功能**:
- 根据文档内容自动生成建议命名
- 提供多个命名选项
- 检查命名是否已存在

**使用方式**:
```bash
# 生成命名建议
python scripts/naming_suggester.py --doc docs/PATH/TO/DOC.md

# 批量生成命名建议
python scripts/naming_suggester.py --dir docs/05_IMPLEMENTATION
```

---

## 七、命名规范执行

### 7.1 创建文档时

**步骤**:
1. 确定文档类型
2. 选择合适的命名模板
3. 使用naming_validator.py检查命名
4. 创建文档

**检查清单**:
- [ ] 是否使用了正确的命名模板
- [ ] 是否使用了英文命名
- [ ] 是否避免了中文文件名
- [ ] 是否避免了空格和特殊字符
- [ ] 命名长度是否≤50字符

### 7.2 重命名文档时

**步骤**:
1. 确定新的命名是否符合规范
2. 使用naming_validator.py检查新命名
3. 更新所有引用该文档的文档
4. 重命名文档

**检查清单**:
- [ ] 新命名是否符合规范
- [ ] 是否更新了所有引用
- [ ] 是否通知了相关文档的维护者

### 7.3 审计文档时

**步骤**:
1. 使用naming_validator.py检查命名规范
2. 生成命名检查报告
3. 跟踪命名不规范问题
4. 督促整改

**检查清单**:
- [ ] 是否有中文文件名
- [ ] 是否有空格和特殊字符
- [ ] 命名长度是否合理
- [ ] 命名是否符合模板

---

## 八、常见问题与解决方案

### 问题1: 使用了中文文件名

**问题描述**: 文档使用了中文文件名

**解决方案**:
1. 使用naming_suggester.py生成英文命名建议
2. 重命名文档
3. 更新所有引用

**示例**:
```
❌ 策略引擎蓝图.md
✅ STRATEGY_ENGINE_BLUEPRINT.md
```

### 问题2: 使用了空格字符

**问题描述**: 文档命名中包含空格

**解决方案**:
1. 将空格替换为下划线
2. 重命名文档
3. 更新所有引用

**示例**:
```
❌ Strategy Engine Blueprint.md
✅ STRATEGY_ENGINE_BLUEPRINT.md
```

### 问题3: 命名过于通用

**问题描述**: 文档命名过于通用，无法反映文档职责

**解决方案**:
1. 分析文档核心职责
2. 使用职责相关的命名
3. 重命名文档

**示例**:
```
❌ DOCUMENT.md
✅ STRATEGY_ENGINE_BLUEPRINT.md
```

### 问题4: 命名过长

**问题描述**: 文档命名超过50字符

**解决方案**:
1. 简化命名，保留核心信息
2. 使用缩写（如果是通用缩写）
3. 重命名文档

**示例**:
```
❌ THIS_IS_A_VERY_LONG_DOCUMENT_NAME_THAT_EXCEEDS_FIFTY_CHARACTERS_BLUEPRINT.md
✅ STRATEGY_ENGINE_BLUEPRINT.md
```

---

## 九、规范执行与监督

### 9.1 执行机制

**自动化检查**:
- 使用naming_validator.py工具定期检查
- 在CI/CD流程中集成命名检查
- 在文档创建时自动验证命名

**人工审查**:
- 在代码审查中检查命名规范
- 在文档审计中检查命名规范
- 在文档发布前检查命名规范

### 9.2 监督机制

**定期审计**:
- 每周快速扫描：检查新增文档的命名规范
- 每月深度审计：检查全系统命名规范
- 每季度专项审计：检查命名规范执行情况

**问题跟踪**:
- 记录命名不规范问题
- 跟踪问题整改进度
- 验证问题整改效果

### 9.3 违规处理

**轻微违规**（命名过长）:
- 口头提醒
- 要求限期整改

**中等违规**（命名过于通用）:
- 书面警告
- 要求提交整改计划

**严重违规**（中文文件名、特殊字符）:
- 立即整改
- 纳入绩效考核

---

## 十、规范版本管理

### 10.1 版本历史

| 版本 | 日期 | 变更内容 | 变更原因 |
|------|------|---------|---------|
| v1.0.0 | 2026-04-03 | 初始版本 | 建立基础命名规范 |
| v2.0.0 | 2026-04-03 | 增强版本 | 添加命名模板库和检查工具 |

### 10.2 版本更新流程

1. 识别规范改进需求
2. 讨论并确定改进方案
3. 更新规范文档
4. 通知相关人员
5. 执行新规范

---

## 十一、总结

### 11.1 核心规范要点

1. **职责反映**: 文件名必须反映文档核心职责
2. **英文优先**: 使用英文命名，避免中文
3. **格式统一**: 使用统一的命名格式
4. **简洁明了**: 命名简洁明了，易于理解
5. **工具支持**: 使用naming_validator.py工具

### 11.2 规范执行要点

1. **创建时检查**: 确保命名符合规范
2. **审计时检查**: 定期检查命名规范
3. **维护时检查**: 及时更新不规范命名
4. **工具支持**: 使用命名检查工具

### 11.3 下一步行动

1. **立即执行**: 使用naming_validator.py检查现有文档
2. **本周完成**: 整改命名不规范问题
3. **本月完成**: 建立命名规范自动检查机制

---

**文档负责人**: 蓝图架构师
**创建日期**: 2026-04-03
**状态**: Active
**下次审查**: 2026-04-10
