# 06_ARCHIVE - 统一归档目录

> 历史版本文档和过度工程化文档集中管理

**版本**: v5.0
**更新日期**: 2026-03-29

---

## 目录结构

```
06_ARCHIVE/
├── README.md                    # 本文档
│
├── main/                       # 主文档历史归档
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── NOZYIO_REFERENCE.md
│   ├── 量化策略框架_v3.1.md
│   ├── v4_development/         # v4.0 开发文档 (新增)
│   │   ├── 清风量化交易系统4.0开发粗稿.md
│   │   ├── 清风量化交易系统4.0开发细稿.md
│   │   └── ... (更多v4.0文档)
│   └── ...
│
├── factor-library/             # 因子库历史归档
│   ├── README.md
│   ├── ifind_factors_list.md
│   ├── ifind_factors_raw.json
│   ├── ifind_indicators.json
│   └── v4_reports/             # v4.0 报告 (新增)
│
├── over_engineered/            # 仍需归档的过度工程化文档
│   ├── README.md
│   ├── METADATA_MANAGEMENT.md  # 元数据管理 - 过于复杂
│   └── STORAGE_ARCHITECTURE.md # 多级存储 - 个人不需要
│
├── old_v4_plan_archive.md       # v4.0 开发方案归档
├── 战术手册_v1.0.md
├── 技术文档_v1.0.md
├── 策略池_v1.0.md
├── 系统增强手册_v1.0.md
└── 旧文档分析报告_清风量化交易系统4.0开发粗稿_backup.md
```

---

## v5.0 归档原则

| 原则 | 说明 |
|------|------|
| **统一归档** | 所有模块的历史文档统一到 06_ARCHIVE/ |
| **分类存储** | 按模块分子目录 (main/, factor-library/, over_engineered/) |
| **永久保留** | 所有历史版本永久保留 |
| **索引完备** | 每个归档有说明归档原因 |
| **版本隔离** | v4.0 开发文档隔离到 v4_development/ |

---

## v5.0 变更记录

### v5.0.0 (2026-03-29)

- ✅ 新增 `main/v4_development/` 目录
- ✅ 归档核心 v4.0 开发文档
- ✅ 创建 `factor-library/v4_reports/` 目录
- ✅ 更新本文档以反映 v5.0 结构

### v4.0 (2026-03-28)

- 初始归档结构

---

## 归档文件清单

### main/v4_development/ - v4.0 开发文档

| 文件 | 说明 | 归档日期 |
|------|------|----------|
| 清风量化交易系统4.0开发粗稿.md | v4.0 初始设计 | 2026-03-29 |
| 清风量化交易系统4.0开发细稿.md | v4.0 详细设计 | 2026-03-29 |
| 清风量化交易系统4.0开发方案.md | v4.0 开发方案 | 2026-03-29 |
| 清风量化交易系统4.0详细执行方案.md | v4.0 执行方案 | 2026-03-29 |
| 清风量化交易系统4.0_合并.md | v4.0 合并版 | 2026-03-29 |
| 清风量化交易系统4.0_归档说明.md | v4.0 归档说明 | 2026-03-29 |
| 清风量化交易系统4.0_设计文档归档.md | v4.0 设计归档 | 2026-03-29 |
| 清风量化交易系统4.0.txt | v4.0 文本版 | 2026-03-29 |
| 清风量化交易系统4.0开发粗稿 - 副本.md | v4.0 副本 | 2026-03-29 |
| 清风量化交易系统4.0开发粗稿_backup.md | v4.0 备份 | 2026-03-29 |

---

## 过度工程化文档 (over_engineered/)

这些文档对**1人+AI**模式来说**仍然过于复杂**：

| 文档 | 归档原因 |
|------|----------|
| METADATA_MANAGEMENT.md | 数据血缘追踪过于复杂，AI运行不需要 |
| STORAGE_ARCHITECTURE.md | 多级存储(热/温/冷)个人不需要 |

---

## 恢复的文档

以下文档之前归档，但因**1人+AI目标**评估后已恢复：

| 原归档位置 | 恢复位置 | 恢复原因 |
|-----------|----------|----------|
| over_engineered/docker_setup.md | 07_RESEARCH/01_ENVIRONMENT/ | AI研究环境隔离必需 |
| over_engineered/statistical_tools.md | 07_RESEARCH/02_EXPLORATORY_ANALYSIS/ | AI统计分析基础 |
| over_engineered/candle_patterns.md | 07_RESEARCH/03_PATTERN_RECOGNITION/ | AI模式识别必需 |
| over_engineered/36_FRAMEWORK.md | 04_EXECUTION/04_AI_COMMITTEE/ | AI决策核心 |
| over_engineered/REAL_TIME_MONITORING.md | 04_EXECUTION/03_MONITORING/ | AI监控必需 |
| over_engineered/PERFORMANCE_ATTRIBUTION.md | 04_EXECUTION/03_MONITORING/ | AI报告必需 |
| over_engineered/tca.md | 04_EXECUTION/02_TRADE_EXECUTOR/ | AI执行分析 |
| POSITION_MANAGEMENT/ | 03_TRADING_TACTICS/06_POSITION_MANAGEMENT/ | 风控规则(人决策) |
| ORDER_GENERATION/ | 03_TRADING_TACTICS/07_ORDER_GENERATION/ | AI执行层 |
| EVENT_ENGINE/ | 04_EXECUTION/01_EVENT_ENGINE/ | 事件驱动引擎 |

---

## 归档检查清单

创建新归档前检查：

- [ ] 是否是历史版本文档？
- [ ] 当前系统是否不再使用此文档？
- [ ] 是否有更优位置放置此文档？
- [ ] 归档原因是否明确记录？

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v5.0 | 2026-03-29 | 新增 v4_development/ 目录和归档清单 |
| v3.0 | 2026-03-29 | 恢复大部分文档（1人+AI目标） |
| v2.0 | 2026-03-28 | 新增over_engineered/目录 |
| v1.0 | 2026-03-28 | 统一归档策略 |
