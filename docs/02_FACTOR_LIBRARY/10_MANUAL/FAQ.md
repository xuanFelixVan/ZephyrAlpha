---
module_id: FACTOR_LIBRARY_10_MANUAL_FAQ
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - 10_MANUAL目录FAQ文档
---

# FAQ

---
responsibility:
  - 提供10 Manual相关文档支持

module_id: 02_FACTOR_LIBRARY_10_MANUAL_001
---|
| 原始数据 | `data/raw/{type}/{year}/` | Parquet |
| 处理后数?| `data/processed/` | Parquet + SQLite |
| 因子数据 | `data/factors/{factor_id}/` | Parquet |
| 信号数据 | `data/signals/` | SQLite |
| 订单数据 | `data/orders/` | SQLite |
| 回测结果 | `data/backtest_results/` | Parquet |

### Q12: 如何更新数据?

**A**:

1. 配置数据源（`config/data_sources.yaml`?
2. 运行数据采集模块
3. 数据自动清洗和存?
4. 因子自动计算和更新

### Q13: 数据更新频率是多少？

**A**:

- 行情数据：日频（每天收盘后）
- 财务数据：季频（每季度发布后?
- 宏观数据：月频（每月发布后）

## 系统配置

### Q14: 如何修改系统配置?

**A**:

1. 编辑 `config/system.yaml`
2. 修改对应的参?
3. 重启系统使配置生?
4. ?`CHANGELOG.md` 中记录配置变?

**注意**: 不要在代码中硬编码配置，应该从配置文件读?

### Q15: 如何添加新的数据源？

**A**:

1. ?`config/data_sources.yaml` 中添加新数据源配?
2. ?`src/modules/data_collector.py` 中实现数据采集逻辑
3. ?`02_FACTOR_LIBRARY/04_DATA_SOURCE/` 中记录数据源信息
4. ?`CHANGELOG.md` 中记录新增数据源

### Q16: 如何修改风控参数?

**A**:

1. 编辑 `config/risk/limits.yaml`
2. 修改止损、止盈、仓位等参数
3. ?`CHANGELOG.md` 中记录参数变?
4. 重新运行回测验证参数有效?

## 版本管理

### Q17: 什么时候升级主版本?

**A**: 当发生以下情况时升级主版本（v4.0 ?v5.0）：

- 架构改变（系统架构层级重组?
- 核心模块替换
- 数据格式不兼?
- 接口版本升级

详见: VERSIONING.md

### Q18: 什么时候升级次版本?

**A**: 当发生以下情况时升级次版本（v4.0 ?v4.1）：

- 新增模块
- 新增因子库（>10因子）
- 新增策略?5个策略）
- 新增功能（不影响现有接口?

### Q19: 什么时候升级补丁版本？

**A**: 当发生以下情况时升级补丁版本（v4.0 ?v4.0.1）：

- Bug修复
- 文档更新
- 性能优化
- 因子参数调整

## AI协作

### Q20: AI可以修改哪些文件?

**A**: 

**?可写**:
- `docs/02_FACTOR_LIBRARY/02_ALPHA_FACTORS/`
- `docs/03_TRADING_TACTICS/`
- `src/modules/`
- `tests/`

**🔒 只读**:
- `docs/00_OVERVIEW/`
- `docs/01_FRAMEWORK/`
- `config/`
- `src/core/`

**?禁止**:
- `.env`
- `secrets/`
- `pyproject.toml`

详见: AI_Permissions.md

### Q21: 如何让AI添加新因子？

**A**:

1. 提供因子定义（公式、计算方法）
2. AI?`02_ALPHA_FACTORS_INDEX.md` 中添加因子信?
3. AI?`factors/` 目录下创建详细定?
4. AI?`CHANGELOG.md` 中记录新增因?
5. 人工审核并验证

### Q22: 如何让AI修改系统配置?

**A**: 

不建议让AI直接修改系统配置。应该：

1. 提出配置修改需?
2. 人工审核并批?
3. 人工修改配置文件
4. AI验证配置生效

## 故障排查

### Q23: 系统启动失败怎么办？

**A**:

1. 检查`CONTEXT_SNAPSHOT.json` 版本是否匹配
2. 检查依赖库是否安装（`pip install -r requirements.txt`?
3. 检查配置文件是否正确（`config/system.yaml`?
4. 查看日志文件（`logs/`）获取错误信?

### Q24: 因子计算失败怎么办？

**A**:

1. 检查数据源是否可用
2. 检查因子定义是否正?
3. 检查数据是否完整（是否有NaN值）
4. 查看日志文件获取错误信息

### Q25: 策略回测失败怎么办？

**A**:

1. 检查策略定义是否正?
2. 检查回测参数是否合?
3. 检查历史数据是否完?
4. 查看日志文件获取错误信息

## 其他

### Q26: 如何联系技术支持？

**A**: 

- 查看 `FAQ.md`（本文档案
- 查看相关模块?`README.md`
- 查看 `CHANGELOG.md` 了解最新变?
- 查看 `System_Manifest.md` 了解系统结构

### Q27: 如何贡献新因子或策略?

**A**:

1. 创建详细的因?策略定义文档
2. 提供回测验证报告
3. 提交到相应目?
4. 等待审核和合?

### Q28: 系统支持哪些数据源？

**A**:

- **行情数据**: AkShare、Baostock、Tushare
- **财务数据**: Tushare、iFind
- **宏观数据**: 待补?

详见: 

**版本**: 1.0 | **更新**: 2026-03-28 | **?*: ?活跃

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本 | 文档管理团队 |

