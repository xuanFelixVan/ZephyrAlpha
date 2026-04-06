---
module_id: STRATEGYMANAGEMENTBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
layer: Layer 3 (策略层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: STRATEGY_MANAGEMENT_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_id: 8.14
module_name: 策略管理界面
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha策略管理
compliance_level: 专业标准
parent_document: ../index.md
implementation_status: 蓝图设计
---

# 策略管理界面模块蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: Streamlit + SQLite
> **优先级**: P2（增强模块）

---

## 一、模块概述

### 1.1 功能定位

策略管理界面提供策略的创建、编辑、删除和启用/禁用功能。

### 1.2 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 策略列表 | 查看所有策略 | P0 |
| 策略创建 | 创建新策略 | P0 |
| 策略编辑 | 编辑策略参数 | P0 |
| 策略启用/禁用 | 控制策略运行 | P0 |

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  策略管理技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Streamlit  │ ◄─── │   SQLite    │                 │
│  │  (界面)     │      │  (存储)     │                 │
│  └──────┬──────┘      └─────────────┘                 │
│         │                                               │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                       │
│  │  Strategy   │                                       │
│  │  Engine     │                                       │
│  └─────────────┘                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、架构设计

### 3.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    策略管理系统架构                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Streamlit界面                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  功能模块                                         │ │ │
│  │  │  - 策略列表                                       │ │ │
│  │  │  - 策略创建                                       │ │ │
│  │  │  - 策略编辑                                       │ │ │
│  │  │  - 策略控制                                       │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   策略管理层                           │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  策略CRUD  │ │  策略验证  │ │  策略调度  │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   SQLite数据库                         │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  strategies表                                    │ │ │
│  │  │  - id (策略ID)                                   │ │ │
│  │  │  - name (策略名称)                               │ │ │
│  │  │  - type (策略类型)                               │ │ │
│  │  │  - parameters (策略参数)                         │ │ │
│  │  │  - status (策略状态)                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、策略数据模型

### 4.1 策略表结构

```sql
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    parameters TEXT,
    status VARCHAR(20) DEFAULT 'disabled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP,
    performance_metrics TEXT
);
```

### 4.2 策略类型

| 策略类型 | 说明 | 参数示例 |
|---------|------|---------|
| 双均线策略 | 均线交叉策略 | short_window=5, long_window=20 |
| 动量策略 | 价格动量策略 | lookback=20, threshold=0.02 |
| 均值回归 | 均值回归策略 | window=20, std_dev=2 |
| 突破策略 | 价格突破策略 | period=20, breakout_pct=0.05 |

### 4.3 策略状态

| 状态 | 说明 | 可转换状态 |
|------|------|-----------|
| enabled | 启用中 | disabled |
| disabled | 已禁用 | enabled |
| running | 运行中 | stopped |
| stopped | 已停止 | running |

---

## 五、界面设计

### 5.1 主界面布局

```
┌────────────────────────────────────────────────────────────┐
│                    ZephyrAlpha 策略管理                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  策略列表                                            │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  名称        类型      状态      操作          │ │ │
│  │  │  双均线策略  双均线    🟢启用    [编辑][禁用]  │ │ │
│  │  │  动量策略    动量      🔴禁用    [编辑][启用]  │ │ │
│  │  │  均值回归    均值回归  🟢启用    [编辑][禁用]  │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                      │ │
│  │  [创建新策略]                                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  策略详情: 双均线策略                                │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  策略名称: 双均线策略                           │ │ │
│  │  │  策略类型: 双均线                               │ │ │
│  │  │  策略描述: 基于均线交叉的趋势跟踪策略           │ │ │
│  │  │                                                │ │ │
│  │  │  策略参数:                                     │ │ │
│  │  │  短期均线: 5                                   │ │ │
│  │  │  长期均线: 20                                  │ │ │
│  │  │                                                │ │ │
│  │  │  性能指标:                                     │ │ │
│  │  │  总收益率: 35%                                 │ │ │
│  │  │  夏普比率: 1.85                                │ │ │
│  │  │  最大回撤: 12%                                 │ │ │
│  │  │                                                │ │ │
│  │  │  [保存修改]  [运行回测]                        │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 六、实施步骤

### 6.1 安装依赖

```bash
pip install streamlit
```

### 6.2 策略管理类

```python
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class StrategyManager:
    def __init__(self, db_path: str = "data/zephyr.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                description TEXT,
                parameters TEXT,
                status VARCHAR(20) DEFAULT 'disabled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                performance_metrics TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def create_strategy(self, name: str, strategy_type: str, description: str = "", parameters: Dict = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO strategies (name, type, description, parameters) 
               VALUES (?, ?, ?, ?)""",
            (name, strategy_type, description, json.dumps(parameters or {}))
        )
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return strategy_id
    
    def get_strategy(self, strategy_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategies WHERE id = ?", (strategy_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "description": row[3],
                "parameters": json.loads(row[4]) if row[4] else {},
                "status": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "last_run": row[8],
                "performance_metrics": json.loads(row[9]) if row[9] else {}
            }
        return None
    
    def list_strategies(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, status FROM strategies")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "status": row[3]
            }
            for row in rows
        ]
    
    def update_strategy(self, strategy_id: int, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key == "parameters":
                updates.append(f"{key} = ?")
                values.append(json.dumps(value))
            else:
                updates.append(f"{key} = ?")
                values.append(value)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(strategy_id)
        
        cursor.execute(
            f"UPDATE strategies SET {', '.join(updates)} WHERE id = ?",
            values
        )
        conn.commit()
        conn.close()
    
    def toggle_strategy(self, strategy_id: int):
        strategy = self.get_strategy(strategy_id)
        if strategy:
            new_status = "disabled" if strategy["status"] == "enabled" else "enabled"
            self.update_strategy(strategy_id, status=new_status)
    
    def delete_strategy(self, strategy_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM strategies WHERE id = ?", (strategy_id,))
        conn.commit()
        conn.close()
```

### 6.3 Streamlit界面实现

```python
import streamlit as st
from strategy_manager import StrategyManager

st.set_page_config(page_title="ZephyrAlpha策略管理", layout="wide")

st.title("ZephyrAlpha 策略管理")

# 初始化策略管理器
strategy_manager = StrategyManager()

# 侧边栏
st.sidebar.header("操作")
action = st.sidebar.radio("选择操作", ["策略列表", "创建策略"])

if action == "策略列表":
    st.header("策略列表")
    
    # 获取策略列表
    strategies = strategy_manager.list_strategies()
    
    if strategies:
        # 显示策略列表
        for strategy in strategies:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
            
            with col1:
                st.write(f"**{strategy['name']}**")
            
            with col2:
                st.write(strategy['type'])
            
            with col3:
                status_emoji = "🟢" if strategy['status'] == 'enabled' else "🔴"
                st.write(f"{status_emoji} {strategy['status']}")
            
            with col4:
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("编辑", key=f"edit_{strategy['id']}"):
                        st.session_state['editing_strategy'] = strategy['id']
                
                with col_b:
                    toggle_text = "禁用" if strategy['status'] == 'enabled' else "启用"
                    if st.button(toggle_text, key=f"toggle_{strategy['id']}"):
                        strategy_manager.toggle_strategy(strategy['id'])
                        st.experimental_rerun()
                
                with col_c:
                    if st.button("删除", key=f"delete_{strategy['id']}"):
                        strategy_manager.delete_strategy(strategy['id'])
                        st.experimental_rerun()
            
            st.divider()
    else:
        st.info("暂无策略，请创建新策略")
    
    # 编辑策略
    if 'editing_strategy' in st.session_state:
        st.header("编辑策略")
        strategy = strategy_manager.get_strategy(st.session_state['editing_strategy'])
        
        if strategy:
            with st.form("edit_strategy_form"):
                name = st.text_input("策略名称", strategy['name'])
                strategy_type = st.selectbox(
                    "策略类型",
                    ["双均线", "动量", "均值回归", "突破"],
                    index=["双均线", "动量", "均值回归", "突破"].index(strategy['type'])
                )
                description = st.text_area("策略描述", strategy['description'])
                
                st.subheader("策略参数")
                parameters = strategy['parameters']
                
                if strategy_type == "双均线":
                    short_window = st.number_input("短期均线", value=parameters.get('short_window', 5))
                    long_window = st.number_input("长期均线", value=parameters.get('long_window', 20))
                    new_parameters = {'short_window': short_window, 'long_window': long_window}
                
                if st.form_submit_button("保存修改"):
                    strategy_manager.update_strategy(
                        strategy['id'],
                        name=name,
                        type=strategy_type,
                        description=description,
                        parameters=new_parameters
                    )
                    st.success("策略更新成功！")
                    del st.session_state['editing_strategy']
                    st.experimental_rerun()

elif action == "创建策略":
    st.header("创建新策略")
    
    with st.form("create_strategy_form"):
        name = st.text_input("策略名称")
        strategy_type = st.selectbox("策略类型", ["双均线", "动量", "均值回归", "突破"])
        description = st.text_area("策略描述")
        
        st.subheader("策略参数")
        
        if strategy_type == "双均线":
            short_window = st.number_input("短期均线", value=5)
            long_window = st.number_input("长期均线", value=20)
            parameters = {'short_window': short_window, 'long_window': long_window}
        
        if st.form_submit_button("创建策略"):
            if name:
                strategy_id = strategy_manager.create_strategy(
                    name=name,
                    strategy_type=strategy_type,
                    description=description,
                    parameters=parameters
                )
                st.success(f"策略创建成功！ID: {strategy_id}")
            else:
                st.error("请输入策略名称")
```

---

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 策略创建 | 可创建策略 | 功能测试 |
| 策略编辑 | 可编辑策略 | 功能测试 |
| 策略删除 | 可删除策略 | 功能测试 |
| 策略启用/禁用 | 可控制策略 | 功能测试 |

### 7.2 数据验证

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 参数验证 | 100% | 所有参数必须验证 |
| 状态一致性 | 100% | 状态转换正确 |

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
- **模块ID**: 8.14
- **蓝图文档**: [STRATEGY_MANAGEMENT_BLUEPRINT.md](./08_HUMAN_AI_INTERFACE\14_STRATEGY_MANAGEMENT\STRATEGY_MANAGEMENT_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha策略管理
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha策略管理 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
