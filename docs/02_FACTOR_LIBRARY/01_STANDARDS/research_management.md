---
module_id: RESEARCH_MANAGEMENT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: STANDARDS_RESEARCH_MGMT_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 因子研究与管理框架设计与优化维护
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---



# 研究项目管理
> **核心职责**: 研究项目管理的定义、实现和应用
> **职责边界**: 
> - ✅ 本文档负责：研究管理流程和规范相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> 量化研究项目的标准化管理方法
>
> **版本**: v1.0
> **最后更?*: 2026-03-28
> **来源**: ?.0开发细稿迁移（务实版）
> **索引**: `RES.MGMT.001`

---

## 一、设计原?

### 1.1 务实选择

```
?4.0过度设计: Docker+Airflow+K8s+Neo4j全套
?5.0务实选择: Obsidian笔记 + Jupyter研究 + 简单文件管?
```

### 1.2 工具?

| 用?| 工具 | 理由 |
|------|------|------|
| **笔记管理** | Obsidian | 知识网络、Markdown友好、本地存?|
| **代码研究** | Jupyter Notebook | 交互式分析、事实标?|
| **版本控制** | Git | 代码和文档版本管?|
| **文件组织** | 标准化目?| 简单直接，不过度设?|

---

## 二、项目目录结?

### 2.1 研究项目模板

```
research_projects/
└── {project_name}/
    ├── README.md                 # 项目说明
    ├── config.yaml               # 项目配置
    ?
    ├── notebooks/                # Jupyter笔记?
    ?  ├── 01_数据探索.ipynb
    ?  ├── 02_因子计算.ipynb
    ?  ├── 03_IC分析.ipynb
    ?  └── 04_策略回测.ipynb
    ?
    ├── scripts/                  # 可执行脚?
    ?  ├── data_loader.py
    ?  ├── factor_calculator.py
    ?  └── backtest_runner.py
    ?
    ├── data/                     # 研究数据
    ?  ├── raw/                  # 原始数据
    ?  ├── processed/            # 处理后数?
    ?  └── results/              # 分析结果
    ?
    ├── docs/                     # 研究文档
    ?  ├── hypothesis.md         # 研究假设
    ?  ├── findings.md           # 研究发现
    ?  └── conclusion.md         # 研究结论
    ?
    ├── logs/                     # 运行日志
    ?  └── backtest_20260328.log
    ?
    └── .gitignore
```

### 2.2 README模板

```markdown
# {项目名称}

## 核心假设
?-2句话概括研究的核心假?

## 研究目标
1. 目标1
2. 目标2

## 数据来源
- 数据?
- 数据?

## 关键结论
- 结论1
- 结论2

## 下一步计?
- 下一?
- 下一?

## 研究时间?
| 阶段 | 开始日?| 结束日期 | 状?|
|------|----------|----------|------|
| 数据探索 | 2026-01-01 | 2026-01-07 | ?|
| 因子研究 | 2026-01-08 | 2026-01-21 | 🔄 |
| 回测验证 | 2026-01-22 | 2026-02-04 | ?|
```

---

## 三、研究流?

### 3.1 标准流程

```
┌─────────────────────────────────────────────────────────────?
?                     研究流程                                 ?
└─────────────────────────────────────────────────────────────?

[1. 假设提出] ?[2. 数据探索] ?[3. 因子计算] ?[4. IC分析]
                                                     ?
[8. 归档总结] ?[7. 策略验证] ?[6. 回测优化] ?[5. 参数调优]
```

### 3.2 各阶段说?

| 阶段 | 产出?| 工具 |
|------|--------|------|
| **假设提出** | hypothesis.md | Obsidian |
| **数据探索** | 01_数据探索.ipynb | Jupyter |
| **因子计算** | 02_因子计算.ipynb | Jupyter |
| **IC分析** | 03_IC分析.ipynb | Jupyter |
| **参数调优** | 04_参数调优.ipynb | Jupyter |
| **回测优化** | 05_策略回测.ipynb | Jupyter |
| **策略验证** | 验证报告 | Jupyter |
| **归档总结** | conclusion.md | Obsidian |

---

## 四、笔记管理（Obsidian?

### 4.1 笔记分类

```
Obsidian Vault/
├── 00_项目索引/
?  ├── 项目总览.md
?  └── 项目列表.md
?
├── 01_想法?
?  ├── 2026-01-01_均线交叉想法.md
?  └── 2026-02-15_布林带均值回?md
?
├── 02_研究项目/
?  ├── P001_趋势因子研究/
?  ?  ├── README.md
?  ?  └── 笔记...
?  └── P002_价值因子研?
?
├── 03_知识?
?  ├── 因子知识/
?  ├── 策略知识/
?  └── 市场知识/
?
├── 04_失败案例/
?  ├── P003_失败原因分析.md
?  └── 教训总结.md
?
└── 05_最佳实?
    ├── 因子研究流程.md
    └── 笔记规范.md
```

### 4.2 笔记链接

利用Obsidian的双向链接功能：

```markdown
# P001_趋势因子研究

## 相关笔记
- [[2026-01-01_均线交叉想法]] - 研究起源
- [[IC分析模板]] - 使用的方?
- [[P002_价值因子研究]] - 相关项目

## 失败案例
- [[F001_过度拟合]] - 教训
```

---

## 五、实验追踪（简化版?

### 5.1 实验记录?

不使用MLflow等重型系统，使用简单的CSV记录?

```csv
# experiments_log.csv
date,experiment_id,description,parameters,result_ic,result_ir,status
2026-03-28,EXP001,MACD金叉,fast:12,slow:26,signal:9,0.052,1.82,pass
2026-03-28,EXP002,MACD金叉,fast:10,slow:20,signal:5,0.048,1.65,pass
2026-03-28,EXP003,RSI超卖,period:14,threshold:30,0.041,1.42,fail
```

### 5.2 参数追踪

```python
# scripts/track_experiment.py
import csv
from datetime import datetime
from pathlib import Path

EXPERIMENT_LOG = Path("experiments_log.csv")

def log_experiment(
    description: str,
    parameters: dict,
    result_ic: float,
    result_ir: float,
    status: str
):
    """记录实验结果"""
    row = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "experiment_id": f"EXP{datetime.now().strftime('%m%d%H%M')}",
        "description": description,
        "parameters": str(parameters),
        "result_ic": result_ic,
        "result_ir": result_ir,
        "status": status
    }

    # 追加到CSV
    with open(EXPERIMENT_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if f.tell() == 0:  # 文件为空，写入表?
            writer.writeheader()
        writer.writerow(row)
```

---

## 六、代码版本控?

### 6.1 Git工作?

```
# 创建研究分支
git checkout -b feature/P001_trend_factor

# 开?..

# 提交
git add .
git commit -m "feat: 添加趋势因子IC分析"

# 合并回主分支
git checkout main
git merge feature/P001_trend_factor
```

### 6.2 .gitignore模板

```gitignore
# Jupyter
.ipynb_checkpoints/
*/.ipynb_checkpoints/

# Data
*.csv
*.parquet
*.h5

# Logs
*.log

# Python
__pycache__/
*.pyc
.pytest_cache/

# OS
.DS_Store
Thumbs.db
```

---

## 七、知识积?

### 7.1 失败案例?

```markdown
# F001_过度拟合

## 策略描述
均线交叉策略??20?

## 失败表现
- 回测年化收益 35%
- 模拟盘年化收?8%
- 偏差 77%

## 失败原因
1. 参数过度优化?个参数）
2. 样本内数据过拟合
3. 未考虑交易成本

## 教训
- 参数数量不超??
- 样本外衰减控制在20%以内
- 加入滑点估算

## 相关项目
- [[P001_趋势因子研究]]
```

### 7.2 最佳实践库

```markdown
# 因子研究最佳实?

## IC分析标准
1. IC均?> 0.02
2. ICIR > 1.0
3. IC胜率 > 60%

## 回测标准
1. 回测周期 >= 5?
2. 样本外比?>= 20%
3. 交易成本 >= ?

## 参数优化标准
1. 参数数量 <= 3
2. 优化步长合理
3. 交叉验证
```

---

## 八、扩展计?

### 8.1 当前版本（v1.0?

- ?标准化目录结?
- ?Obsidian笔记管理
- ?简单实验追?
- ?Git版本控制
- ?知识积累机制

### 8.2 未来扩展（按需?

| 功能 | 时机 | 说明 |
|------|------|------|
| MLflow实验追踪 | 实验数量>100?| 当前CSV足够 |
| Airflow工作?| 流程完全标准化后 | 当前Jupyter足够 |
| Docker环境隔离 | 多项目冲突时 | 当前conda足够 |

---

**设计原则**: 工具简单、流程清晰、持续积?

**维护?*: 清风量化系统
**版本**: v1.0
**最后更?*: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
