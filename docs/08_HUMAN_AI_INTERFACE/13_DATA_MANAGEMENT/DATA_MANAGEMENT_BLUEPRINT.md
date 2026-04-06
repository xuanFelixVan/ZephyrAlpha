---
module_id: DATAMANAGEMENTBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 数据质量
  - 因子计算
  - 数据源
layer: Layer 8 (人机交互层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准---


﻿---
module_id: DATA_MANAGEMENT_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_id: 8.13
module_name: 数据管理界面
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha数据管理
compliance_level: 专业标准
parent_document: ../index.md
implementation_status: 蓝图设计
---

# 数据管理界面模块蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: Streamlit + Pandas
> **优先级**: P2（增强模块）

---

## 一、模块概述

### 1.1 功能定位

数据管理界面提供市场数据的导入、导出、查询和可视化功能。

### 1.2 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 数据查询 | 查询历史数据 | P0 |
| 数据导出 | 导出数据文件 | P0 |
| 数据导入 | 导入外部数据 | P1 |
| 数据可视化 | 数据图表展示 | P1 |

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  数据管理技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Streamlit  │ ◄─── │   Pandas    │                 │
│  │  (界面)     │      │  (数据处理) │                 │
│  └──────┬──────┘      └─────────────┘                 │
│         │                                               │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                       │
│  │  Parquet    │                                       │
│  │  (存储)     │                                       │
│  └─────────────┘                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、架构设计

### 3.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    数据管理系统架构                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Streamlit界面                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  功能模块                                         │ │ │
│  │  │  - 数据查询                                       │ │ │
│  │  │  - 数据导出                                       │ │ │
│  │  │  - 数据导入                                       │ │ │
│  │  │  - 数据可视化                                     │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   数据处理层                           │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  数据查询  │ │  数据转换  │ │  数据验证  │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   数据存储层                           │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  Parquet   │ │    CSV     │ │   SQLite   │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、数据管理功能设计

### 4.1 数据查询

| 查询类型 | 说明 | 参数 |
|---------|------|------|
| 按股票查询 | 查询指定股票数据 | 股票代码、日期范围 |
| 按日期查询 | 查询指定日期数据 | 日期范围 |
| 按指标查询 | 查询指定指标数据 | 指标名称、股票列表 |

### 4.2 数据导出

| 导出格式 | 说明 | 用途 |
|---------|------|------|
| CSV | 逗号分隔文件 | Excel兼容 |
| Parquet | 列式存储 | 大数据存储 |
| Excel | Excel格式 | 报告使用 |
| JSON | JSON格式 | API使用 |

### 4.3 数据导入

| 导入格式 | 说明 | 验证规则 |
|---------|------|---------|
| CSV | 逗号分隔文件 | 字段验证 |
| Excel | Excel格式 | 字段验证 |
| JSON | JSON格式 | 格式验证 |

---

## 五、界面设计

### 5.1 主界面布局

```
┌────────────────────────────────────────────────────────────┐
│                    ZephyrAlpha 数据管理                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  功能选择: [数据查询 ▼]                              │ │
│  │                                                      │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  数据查询                                       │ │ │
│  │  │                                                │ │ │
│  │  │  股票代码: [AAPL]                              │ │ │
│  │  │  开始日期: [2025-01-01]                        │ │ │
│  │  │  结束日期: [2025-12-31]                        │ │ │
│  │  │  数据类型: [日K线 ▼]                           │ │ │
│  │  │                                                │ │ │
│  │  │  [查询数据]                                    │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  查询结果                                            │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  日期       开盘    最高    最低    收盘    成交量│ │ │
│  │  │  2025-01-02  150.0   152.0   149.0   151.0   1M │ │ │
│  │  │  2025-01-03  151.0   153.0   150.0   152.5   1.2M│ │ │
│  │  │  ...                                           │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                      │ │
│  │  [导出CSV] [导出Excel] [导出Parquet]                │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  数据可视化                                          │ │
│  │  [K线图表]                                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 六、实施步骤

### 6.1 安装依赖

```bash
pip install streamlit pandas pyarrow openpyxl
```

### 6.2 数据管理类

```python
import pandas as pd
from pathlib import Path
from typing import List, Optional
from datetime import datetime

class DataManagement:
    def __init__(self, data_dir: str = "data/market_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def query_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        data_type: str = "daily"
    ) -> pd.DataFrame:
        file_path = self.data_dir / f"{symbol}_{data_type}.parquet"
        
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_parquet(file_path)
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        return df
    
    def export_data(
        self,
        df: pd.DataFrame,
        output_path: str,
        format: str = "csv"
    ) -> bool:
        try:
            if format == "csv":
                df.to_csv(output_path, index=False)
            elif format == "excel":
                df.to_excel(output_path, index=False)
            elif format == "parquet":
                df.to_parquet(output_path, index=False)
            elif format == "json":
                df.to_json(output_path, orient='records', indent=2)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def import_data(
        self,
        file_path: str,
        symbol: str,
        data_type: str = "daily"
    ) -> bool:
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                return False
            
            # 验证数据格式
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                return False
            
            # 保存数据
            output_path = self.data_dir / f"{symbol}_{data_type}.parquet"
            df.to_parquet(output_path, index=False)
            
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False
    
    def list_available_data(self) -> List[str]:
        files = list(self.data_dir.glob("*.parquet"))
        return [f.stem for f in files]
```

### 6.3 Streamlit界面实现

```python
import streamlit as st
import pandas as pd
from data_management import DataManagement
from datetime import datetime

st.set_page_config(page_title="ZephyrAlpha数据管理", layout="wide")

st.title("ZephyrAlpha 数据管理")

# 初始化数据管理器
data_manager = DataManagement()

# 功能选择
function = st.sidebar.selectbox(
    "功能选择",
    ["数据查询", "数据导出", "数据导入", "数据可视化"]
)

if function == "数据查询":
    st.header("数据查询")
    
    # 查询参数
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("股票代码", "AAPL")
        start_date = st.date_input("开始日期", datetime(2025, 1, 1))
    
    with col2:
        data_type = st.selectbox("数据类型", ["daily", "hourly", "minute"])
        end_date = st.date_input("结束日期", datetime(2025, 12, 31))
    
    # 查询按钮
    if st.button("查询数据"):
        df = data_manager.query_data(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            data_type
        )
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # 导出选项
            st.subheader("导出数据")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("导出CSV"):
                    data_manager.export_data(df, f"{symbol}_data.csv", "csv")
                    st.success("CSV导出成功！")
            
            with col2:
                if st.button("导出Excel"):
                    data_manager.export_data(df, f"{symbol}_data.xlsx", "excel")
                    st.success("Excel导出成功！")
            
            with col3:
                if st.button("导出Parquet"):
                    data_manager.export_data(df, f"{symbol}_data.parquet", "parquet")
                    st.success("Parquet导出成功！")
            
            with col4:
                if st.button("导出JSON"):
                    data_manager.export_data(df, f"{symbol}_data.json", "json")
                    st.success("JSON导出成功！")
        else:
            st.warning("未找到数据")

elif function == "数据导入":
    st.header("数据导入")
    
    # 导入参数
    symbol = st.text_input("股票代码", "AAPL")
    data_type = st.selectbox("数据类型", ["daily", "hourly", "minute"])
    
    # 文件上传
    uploaded_file = st.file_uploader("选择文件", type=['csv', 'xlsx', 'json'])
    
    if uploaded_file is not None:
        if st.button("导入数据"):
            # 保存临时文件
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 导入数据
            success = data_manager.import_data(temp_path, symbol, data_type)
            
            if success:
                st.success("数据导入成功！")
            else:
                st.error("数据导入失败！请检查文件格式。")

elif function == "数据可视化":
    st.header("数据可视化")
    
    # 选择数据
    available_data = data_manager.list_available_data()
    selected_data = st.selectbox("选择数据", available_data)
    
    if selected_data:
        # 解析股票代码和数据类型
        parts = selected_data.split('_')
        symbol = parts[0]
        data_type = parts[1] if len(parts) > 1 else "daily"
        
        # 加载数据
        df = data_manager.query_data(
            symbol,
            "2000-01-01",
            "2099-12-31",
            data_type
        )
        
        if not df.empty:
            # 显示K线图
            st.subheader("K线图")
            
            fig = go.Figure(data=[go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )])
            
            st.plotly_chart(fig, use_container_width=True)
```

---

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 数据查询 | 可查询数据 | 功能测试 |
| 数据导出 | 可导出多种格式 | 功能测试 |
| 数据导入 | 可导入数据 | 功能测试 |
| 数据可视化 | 可显示图表 | 功能测试 |

### 7.2 性能验收

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 查询速度 | < 1s | 查询10万条数据 |
| 导出速度 | < 5s | 导出10万条数据 |
| 导入速度 | < 10s | 导入10万条数据 |

---

**文档状态**: 🟢 活跃
**下次更新**: 2026-04-13
**维护周期**: 每周审查
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 8: 人机交互层
##### 0.1. 未知模块
- **模块ID**: 8.13
- **蓝图文档**: [DATA_MANAGEMENT_BLUEPRINT.md](./08_HUMAN_AI_INTERFACE\13_DATA_MANAGEMENT\DATA_MANAGEMENT_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha数据管理
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha数据管理 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
