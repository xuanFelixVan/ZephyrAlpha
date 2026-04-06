---
module_id: PERMISSION_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 权限管理系统，负责细粒度权限控制、角色管理和权限审计，不负责基础认证授权
layer: Layer 8 (人机交互层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准---


﻿---
module_id: PERMISSION_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_id: PERMISSION_MANAGEMENT_001
module_name: 权限管理界面
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha权限管理
compliance_level: 专业标准
parent_document: ../index.md
implementation_status: 蓝图设计
---
# 权限管理界面模块蓝图
> **核心职责**: Permission Management蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Permission Management蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 📋 概述

本文档定义了PERMISSION MANAGEMENT的核心功能和技术实现。


> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: Streamlit + FastAPI-Users
> **优先级**: P2（增强模块）

---

## 一、模块概述

### 1.1 功能定位

权限管理界面提供用户角色和权限的管理功能，支持细粒度的权限控制。

### 1.2 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 用户列表 | 查看所有用户 | P0 |
| 角色管理 | 管理角色权限 | P0 |
| 权限分配 | 分配用户权限 | P0 |
| 权限审计 | 审计权限变更 | P1 |

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  权限管理技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Streamlit  │ ◄─── │FastAPI-Users│                 │
│  │  (界面)     │      │  (认证)     │                 │
│  └──────┬──────┘      └─────────────┘                 │
│         │                                               │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                       │
│  │   SQLite    │                                       │
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
│                    权限管理系统架构                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Streamlit界面                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  功能模块                                         │ │ │
│  │  │  - 用户管理                                       │ │ │
│  │  │  - 角色管理                                       │ │ │
│  │  │  - 权限分配                                       │ │ │
│  │  │  - 权限审计                                       │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   权限管理层                           │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  用户CRUD  │ │  角色管理  │ │  权限检查  │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   SQLite数据库                         │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  用户表    │ │  角色表    │ │  权限表    │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、权限模型设计

### 4.1 RBAC权限模型

```
┌─────────────────────────────────────────────────────────────┐
│                    RBAC权限模型                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户 ──────► 角色 ──────► 权限                            │
│                                                             │
│  示例:                                                      │
│  admin ──────► 管理员 ──────► 全部权限                     │
│  trader ─────► 交易员 ──────► 交易权限                     │
│  researcher ─► 研究员 ──────► 研究权限                     │
│  viewer ─────► 观察者 ──────► 只读权限                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 角色定义

| 角色 | 权限范围 | 说明 |
|------|---------|------|
| **admin** | 全部权限 | 系统管理员 |
| **trader** | 交易权限 | 交易操作、查看监控 |
| **researcher** | 研究权限 | 回测、报告、查看数据 |
| **viewer** | 只读权限 | 查看监控、报告 |

### 4.3 权限列表

| 权限 | 说明 | 角色 |
|------|------|------|
| `view_monitoring` | 查看监控 | admin, trader, researcher, viewer |
| `execute_trading` | 执行交易 | admin, trader |
| `run_backtest` | 运行回测 | admin, trader, researcher |
| `modify_config` | 修改配置 | admin |
| `manage_users` | 用户管理 | admin |
| `view_reports` | 查看报告 | admin, trader, researcher, viewer |
| `export_data` | 导出数据 | admin, trader, researcher |

---

## 五、界面设计

### 5.1 主界面布局

```
┌────────────────────────────────────────────────────────────┐
│                    ZephyrAlpha 权限管理                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  功能选择: [用户管理 ▼]                              │ │
│  │                                                      │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  用户列表                                       │ │ │
│  │  │  ┌──────────────────────────────────────────┐ │ │ │
│  │  │  │  用户名    邮箱          角色      状态  │ │ │ │
│  │  │  │  admin    admin@...     管理员    活跃  │ │ │ │
│  │  │  │  trader1  trader@...    交易员    活跃  │ │ │ │
│  │  │  │  research researcher@... 研究员   活跃  │ │ │ │
│  │  │  └──────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  │  [创建用户]                                    │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  角色权限矩阵                                        │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  权限          admin  trader  researcher  viewer│ │ │
│  │  │  查看监控       ✅      ✅       ✅        ✅   │ │ │
│  │  │  执行交易       ✅      ✅       ❌        ❌   │ │ │
│  │  │  运行回测       ✅      ✅       ✅        ❌   │ │ │
│  │  │  修改配置       ✅      ❌       ❌        ❌   │ │ │
│  │  │  用户管理       ✅      ❌       ❌        ❌   │ │ │
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

### 6.2 权限管理类

```python
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class PermissionManager:
    def __init__(self, db_path: str = "data/zephyr.db"):
        self.db_path = db_path
        self._init_db()
        
        self.roles = {
            "admin": ["view_monitoring", "execute_trading", "run_backtest", 
                     "modify_config", "manage_users", "view_reports", "export_data"],
            "trader": ["view_monitoring", "execute_trading", "run_backtest", 
                      "view_reports", "export_data"],
            "researcher": ["view_monitoring", "run_backtest", "view_reports", "export_data"],
            "viewer": ["view_monitoring", "view_reports"]
        }
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permission_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(50),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, email: str, role: str = "viewer") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO users (username, email, role) 
               VALUES (?, ?, ?)""",
            (username, email, role)
        )
        
        user_id = cursor.lastrowid
        
        # 审计记录
        cursor.execute(
            """INSERT INTO permission_audit (user_id, action, details) 
               VALUES (?, ?, ?)""",
            (user_id, "create_user", json.dumps({"username": username, "role": role}))
        )
        
        conn.commit()
        conn.close()
        return user_id
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "status": row[4],
                "created_at": row[5],
                "last_login": row[6]
            }
        return None
    
    def list_users(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, status FROM users")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "status": row[4]
            }
            for row in rows
        ]
    
    def update_user_role(self, user_id: int, new_role: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user = self.get_user(user_id)
        
        cursor.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role, user_id)
        )
        
        # 审计记录
        cursor.execute(
            """INSERT INTO permission_audit (user_id, action, details) 
               VALUES (?, ?, ?)""",
            (user_id, "update_role", json.dumps({"old_role": user['role'], "new_role": new_role}))
        )
        
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user = self.get_user(user_id)
        
        # 审计记录
        cursor.execute(
            """INSERT INTO permission_audit (user_id, action, details) 
               VALUES (?, ?, ?)""",
            (user_id, "delete_user", json.dumps({"username": user['username']}))
        )
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def check_permission(self, role: str, permission: str) -> bool:
        return permission in self.roles.get(role, [])
    
    def get_user_permissions(self, role: str) -> List[str]:
        return self.roles.get(role, [])
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT pa.*, u.username 
               FROM permission_audit pa 
               LEFT JOIN users u ON pa.user_id = u.id 
               ORDER BY pa.timestamp DESC 
               LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "action": row[2],
                "details": json.loads(row[3]) if row[3] else {},
                "timestamp": row[4],
                "username": row[5]
            }
            for row in rows
        ]
```

### 6.3 Streamlit界面实现

```python
import streamlit as st
from permission_manager import PermissionManager

st.set_page_config(page_title="ZephyrAlpha权限管理", layout="wide")

st.title("ZephyrAlpha 权限管理")

# 初始化权限管理器
permission_manager = PermissionManager()

# 侧边栏
st.sidebar.header("功能")
function = st.sidebar.radio("选择功能", ["用户管理", "角色权限", "权限审计"])

if function == "用户管理":
    st.header("用户列表")
    
    # 用户列表
    users = permission_manager.list_users()
    
    if users:
        for user in users:
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1, 2])
            
            with col1:
                st.write(f"**{user['username']}**")
            
            with col2:
                st.write(user['email'])
            
            with col3:
                st.write(user['role'])
            
            with col4:
                status_emoji = "🟢" if user['status'] == 'active' else "🔴"
                st.write(f"{status_emoji} {user['status']}")
            
            with col5:
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("编辑", key=f"edit_{user['id']}"):
                        st.session_state['editing_user'] = user['id']
                
                with col_b:
                    if st.button("删除", key=f"delete_{user['id']}"):
                        permission_manager.delete_user(user['id'])
                        st.success("用户已删除")
                        st.experimental_rerun()
            
            st.divider()
    
    # 创建用户
    st.subheader("创建新用户")
    
    with st.form("create_user_form"):
        username = st.text_input("用户名")
        email = st.text_input("邮箱")
        role = st.selectbox("角色", ["admin", "trader", "researcher", "viewer"])
        
        if st.form_submit_button("创建用户"):
            if username and email:
                user_id = permission_manager.create_user(username, email, role)
                st.success(f"用户创建成功！ID: {user_id}")
            else:
                st.error("请填写完整信息")
    
    # 编辑用户
    if 'editing_user' in st.session_state:
        st.subheader("编辑用户")
        user = permission_manager.get_user(st.session_state['editing_user'])
        
        if user:
            with st.form("edit_user_form"):
                new_role = st.selectbox(
                    "角色",
                    ["admin", "trader", "researcher", "viewer"],
                    index=["admin", "trader", "researcher", "viewer"].index(user['role'])
                )
                
                if st.form_submit_button("保存修改"):
                    permission_manager.update_user_role(user['id'], new_role)
                    st.success("用户角色已更新")
                    del st.session_state['editing_user']
                    st.experimental_rerun()

elif function == "角色权限":
    st.header("角色权限矩阵")
    
    # 权限列表
    all_permissions = [
        "view_monitoring", "execute_trading", "run_backtest",
        "modify_config", "manage_users", "view_reports", "export_data"
    ]
    
    permission_names = {
        "view_monitoring": "查看监控",
        "execute_trading": "执行交易",
        "run_backtest": "运行回测",
        "modify_config": "修改配置",
        "manage_users": "用户管理",
        "view_reports": "查看报告",
        "export_data": "导出数据"
    }
    
    # 显示权限矩阵
    st.subheader("权限矩阵")
    
    header = st.columns([2, 1, 1, 1, 1])
    header[0].write("**权限**")
    header[1].write("**admin**")
    header[2].write("**trader**")
    header[3].write("**researcher**")
    header[4].write("**viewer**")
    
    for permission in all_permissions:
        cols = st.columns([2, 1, 1, 1, 1])
        cols[0].write(permission_names[permission])
        
        for idx, role in enumerate(["admin", "trader", "researcher", "viewer"]):
            has_permission = permission_manager.check_permission(role, permission)
            cols[idx + 1].write("✅" if has_permission else "❌")

elif function == "权限审计":
    st.header("权限审计日志")
    
    # 获取审计日志
    audit_log = permission_manager.get_audit_log(limit=50)
    
    if audit_log:
        for log in audit_log:
            col1, col2, col3 = st.columns([2, 2, 4])
            
            with col1:
                st.write(f"**{log['username'] or 'System'}**")
            
            with col2:
                st.write(log['action'])
            
            with col3:
                st.write(log['timestamp'])
            
            with st.expander("详情"):
                st.json(log['details'])
            
            st.divider()
    else:
        st.info("暂无审计日志")
```

---

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 用户管理 | 可管理用户 | 功能测试 |
| 角色管理 | 可管理角色 | 功能测试 |
| 权限检查 | 可检查权限 | 功能测试 |
| 权限审计 | 可审计权限 | 功能测试 |

### 7.2 安全验收

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 权限验证 | 100% | 所有操作验证权限 |
| 审计记录 | 100% | 所有变更记录审计 |
| 最小权限 | 遵循 | 最小权限原则 |

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
- **模块ID**: 8.15
- **蓝图文档**: [PERMISSION_MANAGEMENT_BLUEPRINT.md](../15_PERMISSION_MANAGEMENT/PERMISSION_MANAGEMENT_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha权限管理
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha权限管理 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
