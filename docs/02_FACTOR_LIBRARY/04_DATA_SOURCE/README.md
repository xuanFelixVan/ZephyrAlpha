---
module_id: FACTOR_README_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 04_DATA_SOURCE 数据源索�?

> 数据源因子整合导�?
>
> **版本**：v1.0
> **更新日期**�?026-03-28

---

## 快速导�?

| 目录 | 内容 | 说明 |
|------|------|------|
| [./iFind/](./iFind/) | iFind数据 | iFind数据接口文档 |
| [QMT_INTERFACE.md](./QMT_INTERFACE.md) | QMT数据接口 | 国金证券QMT量化平台数据接入接口 |
| [T.01.DS001.free_data_sources.md](./T.01.DS001.free_data_sources.md) | 免费数据�?| Baostock/AkShare/Efinance整合 |
| [DATA_QUALITY.md](./DATA_QUALITY.md) | 数据质量控制 | 缺失值、异常值、重复检�?|
| [STATISTICAL_TOOLS.md](./STATISTICAL_TOOLS.md) | 统计分析工具 | 描述性统计、分布分析、相关�?|
| [CORRELATION_ANALYSIS.md](./CORRELATION_ANALYSIS.md) | 高级相关�?| 偏相关、协整、配对交�?|

---

## 目录结构

```
04_DATA_SOURCE/
├── README.md                 # 本文档（数据源导航）
├── QMT_INTERFACE.md          # QMT数据接口 [P0] �?新增
├── T.01.DS001.free_data_sources.md  # 免费数据源整合文�?
├── DATA_QUALITY.md           # 数据质量控制 [P0] �?
├── STATISTICAL_TOOLS.md      # 统计分析工具 [P1] �?
├── CORRELATION_ANALYSIS.md   # 高级相关性分�?[P1] �?
└── iFind/                    # iFind数据
    ├── factor_master_index.md
    ├── factor_master_index.csv
    ├── factor_list.csv
    └── financial_statements/
```

---

## 数据源概�?

| 数据�?| 因子数量 | 评级 | 核心优势 | 费用 |
|--------|----------|------|----------|------|
| Baostock | 28+ | ⭐⭐⭐⭐�?| 财务数据全面、历史长 | 免费 |
| AkShare | 115+ | ⭐⭐⭐⭐�?| 覆盖全面、实时性好 | 免费 |
| Efinance | 65+ | ⭐⭐⭐⭐ | 资金流数据独�?| 免费 |
| Tushare | 35+ | ⭐⭐�?| 需积分、深度数�?| 需积分 |
| iFind | 5700+ | ⭐⭐⭐⭐�?| 机构级数�?| 付费 |

---

## 新增数据源因�?

### T.01.DS001 免费数据源整�?

| 因子类别 | 数据�?| 因子数量 | 文档 |
|----------|--------|----------|------|
| 行情数据 | Baostock + AkShare | 50+ | [T.01.DS001.free_data_sources.md](./T.01.DS001.free_data_sources.md) |
| 财务数据 | Baostock + AkShare | 45+ | 同上 |
| 资金流向 | Efinance | 13+ | 同上 |
| 市场数据 | AkShare | 29+ | 同上 |
| 北向资金 | Efinance + AkShare | 10+ | 同上 |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.1 | 2026-04-02 | 新增QMT数据接口文档，从L0_QMT.md迁移 |
| v1.0 | 2026-03-28 | 初始版本，整合附录AA数据源因子体�?|
