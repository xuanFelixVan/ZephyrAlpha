# 路径引用规范

**文档ID**: PATH_REFERENCE_STANDARD_001
**版本**: v1.0.0
**创建日期**: 2026-04-03
**状态**: Active
**适用范围**: 全系统文档路径引用

---

## 一、规范目标

### 1.1 质量目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 路径有效性 | 100% | 所有路径引用有效 |
| 路径简洁性 | ≥90% | 路径层级≤3层 |
| 路径一致性 | 100% | 同类文档使用相同路径格式 |
| 可维护性 | 高 | 路径变更易于维护 |

### 1.2 效率目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 文档定位时间 | ≤10秒 | 快速定位文档 |
| 路径理解时间 | ≤5秒 | 快速理解路径含义 |
| 路径维护成本 | 低 | 路径变更成本低 |

---

## 二、路径引用原则

### 2.1 核心原则

**原则1: 简洁性原则**
- 路径层级应尽量简洁
- 避免使用过多的`../`
- 优先使用最短路径

**原则2: 一致性原则**
- 同类文档使用相同的路径格式
- 跨模块引用使用统一的路径格式
- 归档文档使用统一的路径格式

**原则3: 可读性原则**
- 路径应易于理解
- 路径应反映文档位置
- 路径应便于维护

**原则4: 安全性原则**
- 优先使用相对路径
- 外部链接必须使用HTTPS
- 避免使用绝对路径（特殊情况除外）

---

## 三、路径引用规则

### 3.1 相对路径层级限制

**规则**: 相对路径层级不得超过3层`../`

**示例**:

✅ **推荐**:
```markdown
[文档](./SUBDIR/document.md)        # 同级子目录
[文档](../document.md)              # 上级目录
[文档](../../document.md)           # 上上级目录
[文档](../../SIBLING/doc.md)        # 上上级兄弟目录
```

❌ **不推荐**:
```markdown
[文档](../../../document.md)        # 3层以上（不推荐）
[文档](../../../../document.md)     # 4层以上（禁止）
[文档](../../../../../document.md)  # 5层以上（禁止）
```

**特殊情况处理**:
- 如果必须使用4层以上路径，应考虑：
  1. 重新组织目录结构
  2. 使用绝对路径（从`docs/`开始）
  3. 在文档中添加导航说明

### 3.2 相对路径格式规范

**规则**: 使用正斜杠`/`作为路径分隔符

**示例**:

✅ **推荐**:
```markdown
[文档](./SUBDIR/document.md)
[文档](../SIBLING/document.md)
```

❌ **禁止**:
```markdown
[文档](.\SUBDIR\document.md)        # Windows路径分隔符
[文档](..\\SIBLING\\document.md)    # Windows路径分隔符
```

### 3.3 路径大小写规范

**规则**: 路径大小写应与实际文件名一致

**示例**:

✅ **推荐**:
```markdown
[文档](./Blueprints/STRATEGY_ENGINE.md)  # 与文件名一致
```

❌ **禁止**:
```markdown
[文档](./blueprints/strategy_engine.md)  # 与文件名不一致
```

---

## 四、不同场景的路径引用规范

### 4.1 同模块内引用

**场景**: 在同一模块内引用其他文档

**推荐格式**:
```markdown
# 同级文档
[文档](./document.md)

# 子目录文档
[文档](./SUBDIR/document.md)

# 上级目录文档
[文档](../document.md)
```

**示例**:
```markdown
# 在 docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRATEGY_ENGINE_BLUEPRINT.md 中

# 引用同级文档
[风险监控蓝图](./RISK_MONITORING_BLUEPRINT.md)

# 引用子目录文档
[技术规格书](../05_TECHNICAL_SPECIFICATIONS/STRATEGY_ENGINE_TECHNICAL_SPECIFICATION.md)

# 引用上级目录文档
[实施层索引](../INDEX.md)
```

### 4.2 跨模块引用

**场景**: 跨模块引用其他模块的文档

**推荐格式**:
```markdown
# 使用相对路径（≤3层）
[文档](../../OTHER_MODULE/document.md)

# 如果路径层级>3，使用docs/开头的相对路径
[文档](docs/OTHER_MODULE/document.md)
```

**示例**:
```markdown
# 在 docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRATEGY_ENGINE_BLUEPRINT.md 中

# 引用框架层文档（路径层级=3）
[架构文档](../../../01_FRAMEWORK/ARCHITECTURE.md)

# 引用因子库文档（路径层级=3）
[因子库文档](../../../02_FACTOR_LIBRARY/README.md)

# 引用系统索引（路径层级=4，使用docs/开头）
[系统索引](docs/INDEX.md)
```

### 4.3 框架层与实施层引用

**场景**: 框架层文档与实施层文档相互引用

**推荐格式**:

**框架层文档引用实施层文档**:
```markdown
**实施层文档**: [实施文档链接](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MODULE_BLUEPRINT.md)
```

**实施层文档引用框架层文档**:
```markdown
**框架层文档**: [框架文档链接](../../01_FRAMEWORK/MODULE_BLUEPRINT.md)
```

**示例**:
```markdown
# 框架层文档: docs/01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md

**实施层文档**: [实时风险对冲引擎蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md)
- 具体实现方案和技术细节
- 核心子系统设计和代码示例
- 部署方案和实施路径

---

# 实施层文档: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md

**框架层文档**: [实时风险监控仪表板蓝图](../../../01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md)
- 定义整体架构和设计原则
- 分析专业机构实践
- 规划系统架构层次
```

### 4.4 归档文档引用

**场景**: 引用已归档的文档

**推荐格式**:
```markdown
[文档名称（已归档）](../../06_ARCHIVE/CATEGORY/DATE_MODULE/document_ARCHIVED.md)
```

**示例**:
```markdown
# 引用归档文档
[Layer 7深度审计报告（已归档）](../../06_ARCHIVE/duplicate_documents/20260403_layer7_audit/LAYER7_DEEP_AUDIT_REPORT_20260403_ARCHIVED.md)

# 引用归档说明
[归档说明](../../06_ARCHIVE/duplicate_documents/20260403_layer7_audit/ARCHIVE_README.md)
```

### 4.5 外部链接引用

**场景**: 引用外部网站或资源

**推荐格式**:
```markdown
[文档名称](https://example.com/path/to/document)
```

**安全要求**:
- ✅ 必须使用HTTPS协议
- ❌ 禁止使用HTTP协议
- ❌ 禁止使用不安全的链接

**示例**:
```markdown
✅ **推荐**:
[Python官方文档](https://docs.python.org/3/)
[pandas文档](https://pandas.pydata.org/docs/)
[NumPy文档](https://numpy.org/doc/stable/)

❌ **禁止**:
[Python官方文档](http://docs.python.org/3/)        # 不安全的HTTP
[未知网站](http://unknown-site.com)                # 不安全的HTTP
```

---

## 五、路径引用检查清单

### 5.1 创建文档时检查

- [ ] 路径层级是否≤3层
- [ ] 路径格式是否正确（使用`/`分隔符）
- [ ] 路径大小写是否与文件名一致
- [ ] 外部链接是否使用HTTPS
- [ ] 路径是否有效（链接可访问）

### 5.2 审计文档时检查

- [ ] 检查所有路径引用的有效性
- [ ] 检查路径层级是否符合规范
- [ ] 检查路径格式是否正确
- [ ] 检查外部链接的安全性
- [ ] 生成路径引用检查报告

### 5.3 维护文档时检查

- [ ] 文档移动后是否更新所有引用
- [ ] 文档重命名后是否更新所有引用
- [ ] 文档删除后是否移除所有引用
- [ ] 归档文档是否更新引用路径

---

## 六、路径引用工具

### 6.1 link_checker.py（链接检查器）

**功能**:
- 检查内部链接有效性
- 检查外部链接可访问性
- 检查路径层级是否符合规范
- 生成路径引用检查报告

**使用方式**:
```bash
# 检查单个文档
python scripts/link_checker.py --doc docs/PATH/TO/DOC.md

# 检查整个目录
python scripts/link_checker.py --dir docs/05_IMPLEMENTATION

# 检查全系统
python scripts/link_checker.py --all
```

**输出示例**:
```
路径引用检查报告
==================
检查范围: docs/05_IMPLEMENTATION
检查时间: 2026-04-03

检查结果:
- 总链接数: 150
- 有效链接: 145
- 无效链接: 3
- 路径层级超限: 2

问题详情:
1. [无效链接] docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRATEGY_ENGINE_BLUEPRINT.md:45
   - 链接: ../NON_EXISTENT.md
   - 建议: 检查文档是否存在

2. [路径层级超限] docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/BLOCK_D1_findings.md:159
   - 链接: ../../../../README.md
   - 建议: 使用docs/开头的相对路径
```

### 6.2 路径优化建议工具

**功能**:
- 分析路径引用结构
- 提供路径优化建议
- 自动生成优化后的路径

**使用方式**:
```bash
# 分析路径结构
python scripts/path_optimizer.py --analyze

# 生成优化建议
python scripts/path_optimizer.py --suggest

# 自动优化路径
python scripts/path_optimizer.py --optimize
```

---

## 七、常见问题与解决方案

### 问题1: 路径层级超过3层

**问题描述**: 文档引用路径使用了4层以上`../`

**解决方案**:
1. **方案1**: 使用`docs/`开头的相对路径
   ```markdown
   # 原路径
   [文档](../../../../README.md)
   
   # 优化后
   [文档](docs/INDEX.md)
   ```

2. **方案2**: 重新组织目录结构
   - 将文档移动到更合适的位置
   - 减少目录层级

3. **方案3**: 在文档中添加导航说明
   ```markdown
   > **导航**: [系统索引](docs/INDEX.md) > [模块索引](docs/MODULE/INDEX.md)
   ```

### 问题2: 路径大小写不一致

**问题描述**: 路径大小写与实际文件名不一致

**解决方案**:
1. 检查实际文件名
2. 更新路径引用，确保大小写一致
3. 使用link_checker.py工具自动检测

### 问题3: 外部链接不安全

**问题描述**: 外部链接使用了HTTP协议

**解决方案**:
1. 将HTTP链接改为HTTPS链接
2. 检查链接是否可访问
3. 如果链接失效，寻找替代链接

### 问题4: 路径引用失效

**问题描述**: 文档移动或删除后，路径引用失效

**解决方案**:
1. 使用link_checker.py工具检测失效链接
2. 更新所有引用路径
3. 在文档移动/删除前，先更新引用

---

## 八、规范执行与监督

### 8.1 执行机制

**自动化检查**:
- 使用link_checker.py工具定期检查
- 在CI/CD流程中集成路径检查
- 在文档创建时自动验证路径

**人工审查**:
- 在代码审查中检查路径引用
- 在文档审计中检查路径规范
- 在文档发布前检查路径有效性

### 8.2 监督机制

**定期审计**:
- 每周快速扫描：检查新增文档的路径引用
- 每月深度审计：检查全系统路径引用
- 每季度专项审计：检查路径引用规范执行情况

**问题跟踪**:
- 记录路径引用问题
- 跟踪问题整改进度
- 验证问题整改效果

### 8.3 违规处理

**轻微违规**（路径层级=4）:
- 口头提醒
- 要求限期整改

**中等违规**（路径层级≥5）:
- 书面警告
- 要求提交整改计划

**严重违规**（路径失效、不安全链接）:
- 立即整改
- 纳入绩效考核

---

## 九、规范版本管理

### 9.1 版本历史

| 版本 | 日期 | 变更内容 | 变更原因 |
|------|------|---------|---------|
| v1.0.0 | 2026-04-03 | 初始版本 | 建立路径引用规范 |

### 9.2 版本更新流程

1. 识别规范改进需求
2. 讨论并确定改进方案
3. 更新规范文档
4. 通知相关人员
5. 执行新规范

---

## 十、总结

### 10.1 核心规范要点

1. **路径层级限制**: ≤3层`../`
2. **路径格式规范**: 使用`/`分隔符
3. **路径大小写**: 与文件名一致
4. **外部链接安全**: 必须使用HTTPS
5. **路径有效性**: 所有链接必须有效

### 10.2 规范执行要点

1. **创建时检查**: 确保路径符合规范
2. **审计时检查**: 定期检查路径引用
3. **维护时检查**: 及时更新失效链接
4. **工具支持**: 使用link_checker.py工具

### 10.3 下一步行动

1. **立即执行**: 使用link_checker.py检查现有文档
2. **本周完成**: 整改路径层级超限问题
3. **本月完成**: 建立路径引用自动检查机制

---

**文档负责人**: 蓝图架构师
**创建日期**: 2026-04-03
**状态**: Active
**下次审查**: 2026-04-10
