---
module_id: TRADING_JOURNAL_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_id: 8.9
module_name: 交易日志系统
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha交易日志
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 蓝图设计
---

# 交易日志系统模块蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: SQLite + Streamlit
> **优先级**: P2（可选模块）

---

## 一、模块概述

交易日志系统用于记录交易决策过程，支持交易复盘和分析。

### 1.1 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 交易记录 | 记录交易决策 | P0 |
| 日志查询 | 查询历史日志 | P0 |
| 复盘分析 | 分析交易决策 | P1 |
| 统计报告 | 生成统计报告 | P2 |

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  交易日志技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Streamlit  │ ◄─── │   SQLite    │                 │
│  │  (界面)     │      │  (存储)     │                 │
│  └─────────────┘      └─────────────┘                 │
│                                                         │
│  功能:                                                  │
│  - 记录交易决策过程                                     │
│  - 标注交易理由                                         │
│  - 评估交易结果                                         │
│  - 生成复盘报告                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、日志内容

### 3.1 交易日志字段

| 字段 | 说明 |
|------|------|
| 交易日期 | 交易执行日期 |
| 交易标的 | 交易品种 |
| 交易方向 | 买入/卖出 |
| 交易理由 | 决策依据 |
| 预期目标 | 预期收益 |
| 止损位 | 止损价格 |
| 实际结果 | 实际收益 |
| 复盘总结 | 经验教训 |

### 3.2 日志界面

```
┌────────────────────────────────────────────────────────────┐
│                    ZephyrAlpha 交易日志                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  新增交易日志                                        │ │
│  │  交易日期: [2026-04-06]                             │ │
│  │  交易标的: [AAPL]                                   │ │
│  │  交易方向: [买入 ▼]                                 │ │
│  │  交易理由: [技术突破，突破前高]                     │ │
│  │  预期目标: [10%]                                    │ │
│  │  止损位: [145.0]                                    │ │
│  │                                                      │ │
│  │  [保存]                                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  历史交易日志                                        │ │
│  │  [表格显示历史记录]                                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 四、实施步骤

### 4.1 数据库设计

```sql
CREATE TABLE trading_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    reason TEXT,
    target_price DECIMAL(10, 2),
    stop_loss DECIMAL(10, 2),
    actual_result DECIMAL(10, 2),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Streamlit界面

```python
import streamlit as st
import sqlite3
import pandas as pd

st.title("ZephyrAlpha 交易日志")

# 新增日志
st.header("新增交易日志")
trade_date = st.date_input("交易日期")
symbol = st.text_input("交易标的")
direction = st.selectbox("交易方向", ["买入", "卖出"])
reason = st.text_area("交易理由")
target_price = st.number_input("预期目标价")
stop_loss = st.number_input("止损位")

if st.button("保存"):
    conn = sqlite3.connect('trading_journal.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trading_journal 
        (trade_date, symbol, direction, reason, target_price, stop_loss)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (trade_date, symbol, direction, reason, target_price, stop_loss))
    conn.commit()
    conn.close()
    st.success("保存成功")

# 查询历史
st.header("历史交易日志")
conn = sqlite3.connect('trading_journal.db')
df = pd.read_sql_query("SELECT * FROM trading_journal ORDER BY trade_date DESC", conn)
st.dataframe(df)
conn.close()
```

---

## 五、验收标准

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 日志记录 | 可记录交易 | 功能测试 |
| 日志查询 | 可查询历史 | 功能测试 |
| 日志编辑 | 可编辑日志 | 功能测试 |
| 日志导出 | 可导出数据 | 功能测试 |

---

**文档状态**: 🟢 活跃
**下次更新**: 2026-04-13
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 8: 人机交互层
##### 0.1. 未知模块
- **模块ID**: 8.9
- **蓝图文档**: [TRADING_JOURNAL_BLUEPRINT.md](./08_HUMAN_AI_INTERFACE\09_TRADING_JOURNAL\TRADING_JOURNAL_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha交易日志
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha交易日志 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
