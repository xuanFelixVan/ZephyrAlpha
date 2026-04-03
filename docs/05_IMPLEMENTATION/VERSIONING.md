---
module_id: DOC_VERSIONING_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: INDEX.md
implementation_status: 进行?
---


# VERSIONING.md - 版本管理规范

> 清风量化系统版本号管理和升级规则


## 版本号格?

```
{主版本}.{次版本}.{补丁版本}
```

示例: `4.0.2`


## 版本升级规则

### 主版本升级（v4.0 ?v5.0?

**触发条件**:
- 架构改变（Layer 0-11重组?
- 核心模块替换
- 数据格式不兼?
- 接口版本升级（interface_version: 1.0 ?2.0?

**操作**:
1. 更新 `System_Manifest.md` 中的 `version` 字段
2. 更新 `CONTEXT_SNAPSHOT.json` 中的 `system_version`
3. ?`CHANGELOG.md` 中记录重大变?
4. 备份旧版本到 `archives/v4.0/`

**示例**:
```json
{
  "system_version": "5.0",
  "interface_version": "2.0",
  "breaking_changes": [
    "Layer 0-11架构重组",
    "数据格式从Parquet改为Arrow"
  ]
}
```

### 次版本升级（v4.0 ?v4.1?

**触发条件**:
- 新增模块
- 新增因子库（>10个因子）
- 新增策略?5个策略）
- 新增功能（不影响现有接口?

**操作**:
1. 更新 `System_Manifest.md` 中的 `version` 字段
2. 更新 `CONTEXT_SNAPSHOT.json` 中的 `system_version`
3. ?`CHANGELOG.md` 中记录新增功?
4. 更新 `02_ALPHA_FACTORS_INDEX.md` 中的因子统计

**示例**:
```markdown
## [v4.1] - 2026-04-15

### Added
- 新增10个动量因子（ALPHA_065-074?
- 新增5个策略（S010-S014?
- 新增市场状态识别模?
```

### 补丁版本升级（v4.0 ?v4.0.1?

**触发条件**:
- Bug修复
- 文档更新
- 性能优化
- 因子参数调整

**操作**:
1. 更新 `System_Manifest.md` 中的 `version` 字段
2. 更新 `CONTEXT_SNAPSHOT.json` 中的 `system_version`
3. ?`CHANGELOG.md` 中记录修复内?

**示例**:
```markdown
## [v4.0.1] - 2026-03-29

### Fixed
- 修复MA5计算中的NaN处理
- 修复PE_TTM因子的数据源错误

### Changed
- 优化因子计算性能（提?5%?
```


## 版本兼容性规?

| 版本类型 | 兼容?| 说明 |
|---------|--------|------|
| 主版?| ?不兼?| v4.0 的数?接口不能用于 v5.0 |
| 次版?| ?向后兼容 | v4.0 的代码可以用?v4.1 |
| 补丁版本 | ?完全兼容 | v4.0 ?v4.0.1 完全兼容 |


## 版本检查机?

### 启动时检?

```python
def check_version_compatibility():
    """检查系统版本兼容?""
    
    # 读取当前版本
    current_version = read_system_version()
    
    # 读取快照版本
    snapshot_version = read_snapshot_version()
    
    # 检查兼容?
    if current_version.major != snapshot_version.major:
        raise VersionMismatchError(
            f"主版本不匹配: {current_version} vs {snapshot_version}"
        )
    
    if current_version.minor < snapshot_version.minor:
        raise VersionMismatchError(
            f"次版本过? {current_version} < {snapshot_version}"
        )
```

### 接口版本协商

```python
def negotiate_interface_version():
    """协商接口版本"""
    
    client_version = "1.0"
    server_version = "1.0"
    
    if client_version == server_version:
        return True
    elif client_version < server_version:
        # 向后兼容
        return True
    else:
        # 客户端版本过?
        raise InterfaceVersionError()
```


## 版本发布流程

### 第一步：准备

- [ ] 更新所有版本号字段
- [ ] 更新 `CHANGELOG.md`
- [ ] 更新 `System_Manifest.md`
- [ ] 更新 `CONTEXT_SNAPSHOT.json`

### 第二步：验证

- [ ] 运行所有单元测?
- [ ] 运行集成测试
- [ ] 验证向后兼容?
- [ ] 验证接口版本

### 第三步：发布

- [ ] 创建Git标签（v4.0.2?
- [ ] 备份旧版?
- [ ] 更新文档
- [ ] 发布变更日志

### 第四步：验证

- [ ] 验证新版本可正常启动
- [ ] 验证数据迁移成功
- [ ] 验证所有模块正常运?


## 版本号字段位?

| 文件 | 字段 | 格式 |
|------|------|------|
| `System_Manifest.md` | `version` | `4.0.2` |
| `CONTEXT_SNAPSHOT.json` | `system_version` | `4.0.2` |
| `CONTEXT_SNAPSHOT.json` | `interface_version` | `1.0` |
| `CHANGELOG.md` | 标题 | `[v4.0.2]` |
| `pyproject.toml` | `version` | `4.0.2` |


## 版本历史

| 版本 | 发布日期 | 主要变更 |
|------|---------|---------|
| v4.0.2 | 2026-03-28 | 完成阶段一交付，优化因子库结构 |
| v4.0.1 | 2026-03-28 | 初始版本，完成系统架构设?|
| v4.0 | 2026-03-28 | 首次发布 |


**版本**: 1.0 | **更新**: 2026-03-28 | **状?*: ?活跃
