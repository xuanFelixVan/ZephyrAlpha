---
module_id: FACTOR_DOC_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 研究标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 因子分类总表

> 清风量化交易系统因子库完整分类体系
>
> **版本**: v5.1
> **更新日期**: 2026-03-28

---

## 一、因子分类体系

```
因子库 (Factor Library)
│
├── 1. Alpha因子层 (87+)
│   ├── 1_趋势跟踪因子.md
│   ├── 2_均值回归因子.md
│   ├── 3_价值因子.md
│   ├── 4_成长因子.md
│   ├── 5_质量因子.md
│   ├── 6_动量因子.md
│   └── 7_情绪因子.md
│
├── 2. 风险因子层 (46+)
│   ├── T.03.RF001.barra_style_factors.md
│   ├── T.03.RF002.industry_factors.md
│   └── T.03.RF003.tail_risk_factors.md
│
└── 3. 数据源因子层 (5700+)
    ├── factor_master_index.md              # 因子关联信息入口
    ├── ths_bd_complete_indicator_list.md    # Markdown格式
    ├── factor_list.csv              # CSV快速检索 (5800+)
    ├── IC验证记录/               # IC验证（核心）
    ├── 回测报告/                 # 单因子回测（核心）
    ├── 相关性矩阵/               # 因子相关性分析
    ├── 版本追踪/                 # 因子版本历史
    └── 血缘追踪/                 # 因子血缘关系
```

---

## 四、因子统计总览

| 因子类别 | 因子数量 | 文档位置 |
|----------|----------|----------|
| Alpha趋势 | 14+ | 02_ALPHA_FACTORS/ |
| Alpha均值回归 | 12+ | 02_ALPHA_FACTORS/ |
| Alpha价值 | 11+ | 02_ALPHA_FACTORS/ |
| Alpha成长 | 10+ | 02_ALPHA_FACTORS/ |
| Alpha质量 | 17+ | 02_ALPHA_FACTORS/ |
| Alpha动量 | 9+ | 02_ALPHA_FACTORS/ |
| Alpha情绪 | 14+ | 02_ALPHA_FACTORS/ |
| Barra风格 | 10 | 03_RISK_FACTORS/ |
| 行业因子 | 28+ | 03_RISK_FACTORS/ |
| 尾部风险 | 8+ | 03_RISK_FACTORS/ |
| THS_BD数据源 | 5700+ | 04_DATA_SOURCE/ |
| **合计** | **5900+** | | |

---

## 三、快速导航

| 需求 | 路径 |
|------|------|
| 返回索引 | [README.md](./README.md) |
| Alpha因子列表 | [02_ALPHA_FACTORS/](../02_ALPHA_FACTORS/) |
| 风险因子列表 | [03_RISK_FACTORS/](../03_RISK_FACTORS/) |
| THS_BD完整指标 | [04_DATA_SOURCE/](../04_DATA_SOURCE/iFind/financial_statements/) |
| 因子研究方法论 |  |

---

> **维护部门**: 清风量化研究部
> **最后更新**: 2026-03-28