---
module_id: DOC_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: INDEX.md
implementation_status: 进行中
---


# FAQ.md - 常见问题

> 清风量化系统常见问题解答


## 系统架构

### Q1: Layer 0-7 是什么？

**A**: Layer 0-7 是系统的分层架构：

- **Layer 0**: 数据层 - 数据采集、清洗、存储
- **Layer 1**: 前置层 - 市场状态识别
- **Layer 2**: Alpha层 - 因子生成、信号预测
- **Layer 3**: 风险层 - 风险建模、归因
- **Layer 4**: 组合层 - 组合优化、权重分配
- **Layer 5**: 执行层 - 订单生成、交易执行
- **Layer 6**: 监控层 - 实时监控、告警
- **Layer 7**: 归因层 - 绩效归因、分析

详见: [01_FRAMEWORK/README.md](../../README.md)

### Q2: 系统支持多少个策略？

**A**: 系统设计支持 30-50 个策略的动态管理。当前已实现 1 个策略（S001），其他策略在开发中。

### Q3: 如何添加新的 Layer？

**A**: 不建议添加新的 Layer。如需扩展功能，应该在现有 Layer 内添加新模块。


## 因子管理

### Q4: 如何添加新因子？

**A**: 

1. 在 `02_ALPHA_FACTORS_INDEX.md` 中分配新的因子ID（如 ALPHA_088）
2. 在对应类别的表格中添加因子信息
3. 在 `factors/` 目录下创建详细定义文件
4. 在 `CHANGELOG.md` 中记录新增因子
5. 更新 `CONTEXT_SNAPSHOT.json`

**示例**:
```markdown
| ALPHA_088 | 新因子名称 | 计算方法 | 数据源 | 日 | ✅ |
```

### Q5: 如何修改因子定义？

**A**:

1. 在 `02_ALPHA_FACTORS_INDEX.md` 中更新因子信息
2. 在 `factors/{FACTOR_ID}.md` 中更新详细定义
3. 在 `CHANGELOG.md` 中记录修改内容
4. 更新 `CONTEXT_SNAPSHOT.json` 中的文件哈希

### Q6: 如何删除因子？

**A**:

1. 不要直接删除，改为标记为"已弃用"
2. 在 `02_ALPHA_FACTORS_INDEX.md` 中将状态改为 `⚠️ 已弃用`
3. 在 `CHANGELOG.md` 中记录弃用原因
4. 保留历史记录以便追踪

### Q7: 因子库中有多少个因子？

**A**: 当前有 87 个 Alpha 因子 + 46 个风险因子 = 133 个因子。

详见: [02_ALPHA_FACTORS_INDEX.md](02_ALPHA_FACTORS_INDEX.md)


## 策略开发

### Q8: 如何创建新策略？

**A**:

1. 创建 `Strategy_Spec_S{ID}.md` 文件
2. 定义策略逻辑（赚钱逻辑、公式、伪代码）
3. 定义风险控制（止损、止盈、仓位）
4. 定义异常处理
5. 在 `03_TRADING_TACTICS/` 中创建策略文档
6. 在 `CHANGELOG.md` 中记录新增策略

详见: [Strategy_Spec_S001.md](../03_TRADING_TACTICS/Strategy_Spec_S001.md)

### Q9: 如何运行策略回测？

**A**:

1. 准备历史数据（至少3年）
2. 配置回测参数（初始资金、手续费等）
3. 运行回测框架
4. 生成回测报告
5. 将报告保存到 `05_BACKTEST/strategy_reports/S{ID}/`

### Q10: 回测报告应该包含什么内容？

**A**:

- 策略说明
- 回测参数
- 性能指标（夏普比、最大回撤、胜率等）
- 权益曲线
- 交易统计
- 风险分析

详见: [05_BACKTEST/strategy_reports/README.md](../../README.md)


## 数据管理

### Q11: 数据存储在哪里？

**A**:

| 数据类型 | 存储位置 | 格式 |
|---------|---------|------|
| 原始数据 | `data/raw/{type}/{year}/` | Parquet |
| 处理后数据 | `data/processed/` | Parquet + SQLite |
| 因子数据 | `data/factors/{factor_id}/` | Parquet |
| 信号数据 | `data/signals/` | SQLite |
| 订单数据 | `data/orders/` | SQLite |
| 回测结果 | `data/backtest_results/` | Parquet |

### Q12: 如何更新数据？

**A**:

1. 配置数据源（`config/data_sources.yaml`）
2. 运行数据采集模块
3. 数据自动清洗和存储
4. 因子自动计算和更新

### Q13: 数据更新频率是多少？

**A**:

- 行情数据：日频（每天收盘后）
- 财务数据：季频（每季度发布后）
- 宏观数据：月频（每月发布后）


## 系统配置

### Q14: 如何修改系统配置？

**A**:

1. 编辑 `config/system.yaml`
2. 修改对应的参数
3. 重启系统使配置生效
4. 在 `CHANGELOG.md` 中记录配置变更

**注意**: 不要在代码中硬编码配置，应该从配置文件读取。

### Q15: 如何添加新的数据源？

**A**:

1. 在 `config/data_sources.yaml` 中添加新数据源配置
2. 在 `src/modules/data_collector.py` 中实现数据采集逻辑
3. 在 `02_FACTOR_LIBRARY/04_DATA_SOURCE/` 中记录数据源信息
4. 在 `CHANGELOG.md` 中记录新增数据源

### Q16: 如何修改风控参数？

**A**:

1. 编辑 `config/risk/limits.yaml`
2. 修改止损、止盈、仓位等参数
3. 在 `CHANGELOG.md` 中记录参数变更
4. 重新运行回测验证参数有效性


## 版本管理

### Q17: 什么时候升级主版本？

**A**: 当发生以下情况时升级主版本（v4.0 → v5.0）：

- 架构改变（Layer 0-7重组）
- 核心模块替换
- 数据格式不兼容
- 接口版本升级

详见: [VERSIONING.md](../05_IMPLEMENTATION/VERSIONING.md)

### Q18: 什么时候升级次版本？

**A**: 当发生以下情况时升级次版本（v4.0 → v4.1）：

- 新增模块
- 新增因子库（>10���因子）
- 新增策略（>5个策略）
- 新增功能（不影响现有接口）

### Q19: 什么时候升级补丁版本？

**A**: 当发生以下情况时升级补丁版本（v4.0 → v4.0.1）：

- Bug修复
- 文档更新
- 性能优化
- 因子参数调整


## AI协作

### Q20: AI可以修改哪些文件？

**A**: 

**✅ 可写**:
- `docs/02_FACTOR_LIBRARY/02_ALPHA_FACTORS/`
- `docs/03_TRADING_TACTICS/`
- `src/modules/`
- `tests/`

**🔒 只读**:
- `docs/00_OVERVIEW/`
- `docs/01_FRAMEWORK/`
- `config/`
- `src/core/`

**❌ 禁止**:
- `.env`
- `secrets/`
- `pyproject.toml`

详见: [AI_Permissions.md](../08_AI_GOVERNANCE/AI_Permissions.md)

### Q21: 如何让AI添加新因子？

**A**:

1. 提供因子定义（公式、计算方法）
2. AI在 `02_ALPHA_FACTORS_INDEX.md` 中添加因子信息
3. AI在 `factors/` 目录下创建详细定义
4. AI在 `CHANGELOG.md` 中记录新增因子
5. 人工审核并验证

### Q22: 如何让AI修改系统配置？

**A**: 

不建议让AI直接修改系统配置。应该：

1. 提出配置修改需求
2. 人工审核并批准
3. 人工修改配置文件
4. AI验证配置生效


## 故障排查

### Q23: 系统启动失败怎么办？

**A**:

1. 检查 `CONTEXT_SNAPSHOT.json` 版本是否匹配
2. 检查依赖库是否安装（`pip install -r requirements.txt`）
3. 检查配置文件是否正确（`config/system.yaml`）
4. 查看日志文件（`logs/`）获取错误信息

### Q24: 因子计算失败怎么办？

**A**:

1. 检查数据源是否可用
2. 检查因子定义是否正确
3. 检查数据是否完整（是否有NaN值）
4. 查看日志文件获取错误信息

### Q25: 策略回测失败怎么办？

**A**:

1. 检查策略定义是否正确
2. 检查回测参数是否合理
3. 检查历史数据是否完整
4. 查看日志文件获取错误信息


## 其他

### Q26: 如何联系技术支持？

**A**: 

- 查看 `FAQ.md`（本文档）
- 查看相关模块的 `README.md`
- 查看 `CHANGELOG.md` 了解最新变更
- 查看 `System_Manifest.md` 了解系统结构

### Q27: 如何贡献新因子或策略？

**A**:

1. 创建详细的因子/策略定义文档
2. 提供回测验证报告
3. 提交到相应目录
4. 等待审核和合并

### Q28: 系统支持哪些数据源？

**A**:

- **行情数据**: AkShare、Baostock、Tushare
- **财务数据**: Tushare、iFind
- **宏观数据**: 待补充

详见: 


**版本**: 1.0 | **更新**: 2026-03-28 | **状态**: ✅ 活跃
