# 清风量化主文档库

> 量化策略核心框架文档库

---

## 模块结构

```
main/
├── README.md                      # 本索引文件
├── CHANGELOG.md                   # 版本追踪
├── 01_FRAMEWORK/                  # 策略框架
│   └── 量化策略框架_v3.1.md       # 机构级优化版 ✅ 主文档
├── 02_TACTICS/                    # 战术库
│   ├── README.md                  # 战术库总索引
│   ├── 01_MARKET_REGIME/          # Layer 0: 市场状态
│   ├── 02_ALPHA_FACTORS/          # Layer 1: Alpha因子战术
│   │   ├── 01_趋势跟踪/
│   │   ├── 02_均值回归/
│   │   ├── 03_价值投资/
│   │   ├── 04_成长投资/
│   │   ├── 05_质量因子/
│   │   ├── 06_动量战术/
│   │   └── 07_情绪量化/
│   ├── 03_RISK_MANAGEMENT/        # Layer 3: 风险管理
│   ├── 04_EXECUTION/              # Layer 4: 执行优化
│   ├── 05_RISK_CONTROL/           # Layer 5: 风险控制
│   ├── 06_PERFORMANCE/            # Layer 6: 绩效归因
│   └── 07_ITERATION/              # Layer 7: 策略迭代
└── 03_ARCHIVE/                    # 历史归档
```

---

## 核心文档

### 量化策略框架_v3.1.md

| 项目 | 内容 |
|------|------|
| 策略名称 | 清风量化多策略系统 v3.1 Professional |
| 核心架构 | 8层量化流水线(Layer 0-7) |
| 机构标准 | 完整对标国际顶级量化基金 |
| 技术栈 | ML/DL/RL现代量化技术 |

**框架层次**：
```
Layer 0: 市场状态判断 (HMM/GMM)
Layer 1: Alpha因子库 (IC/IR检验)
Layer 2: 风险模型 (Barra因子模型)
Layer 3: 组合优化 (Black-Litterman)
Layer 4: 执行优化 (TWAP/VWAP)
Layer 5: 风控监控 (VaR/CVaR)
Layer 6: 绩效归因 (Brinson模型)
Layer 7: 策略迭代 (贝叶斯优化/RL)
```

---

## 文档导航

| 需求 | 文件 |
|------|------|
| 了解策略架构 | [01_FRAMEWORK/量化策略框架_v3.1.md](./01_FRAMEWORK/量化策略框架_v3.1.md) |
| 查看战术库索引 | [02_TACTICS/README.md](./02_TACTICS/README.md) |
| 版本变更记录 | [CHANGELOG.md](./CHANGELOG.md) |

### 战术库快速导航

| Layer | 类别 | 路径 |
|-------|------|------|
| Layer 0 | 市场状态 | [02_TACTICS/01_MARKET_REGIME](./02_TACTICS/01_MARKET_REGIME/README.md) |
| Layer 1-2 | Alpha因子 | [02_TACTICS/02_ALPHA_FACTORS](./02_TACTICS/02_ALPHA_FACTORS/README.md) |
| Layer 3 | 风险管理 | [02_TACTICS/03_RISK_MANAGEMENT](./02_TACTICS/03_RISK_MANAGEMENT/README.md) |
| Layer 4 | 执行优化 | [02_TACTICS/04_EXECUTION](./02_TACTICS/04_EXECUTION/README.md) |
| Layer 5 | 风险控制 | [02_TACTICS/05_RISK_CONTROL](./02_TACTICS/05_RISK_CONTROL/README.md) |
| Layer 6 | 绩效归因 | [02_TACTICS/06_PERFORMANCE](./02_TACTICS/06_PERFORMANCE/README.md) |
| Layer 7 | 策略迭代 | [02_TACTICS/07_ITERATION](./02_TACTICS/07_ITERATION/README.md) |

---

## 关联文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 因子库 | [../factor-library/00_INDEX/因子分类总表.md](../factor-library/00_INDEX/因子分类总表.md) | 5723+ THS_BD指标 |
| 战术手册 | [../trading-tactics/战术手册_v1.0.md](../trading-tactics/战术手册_v1.0.md) | 交易执行战术 |
| 技术文档 | [../technical-specs/技术文档_v1.0.md](../technical-specs/技术文档_v1.0.md) | 系统技术架构 |

---

## 文档索引规则

### 文件命名规范

- 框架文档: `量化策略框架_vX.X.md`
- 战术文档: `T.{分类}.{编号}.{名称}.md`
- 索引文件: `README.md`

### 防止文件漂移

- 所有跨目录引用使用相对路径
- 因子库索引位于 [../factor-library/04_DATA_SOURCE/iFind/因子主索引.md](../factor-library/04_DATA_SOURCE/iFind/因子主索引.md)
- 战术库索引位于 [02_TACTICS/README.md](./02_TACTICS/README.md)

---

## 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| v3.1 | 2026-03-28 | 机构级优化：策略目标升级、数学公式化、8层流水线、现代技术栈、战术库建设 |
| v3.0 | 2026-03-28 | 专业机构标准重构（已归档） |

---

> **维护部门**: 清风量化研究部
> **最后更新**: 2026-03-28
