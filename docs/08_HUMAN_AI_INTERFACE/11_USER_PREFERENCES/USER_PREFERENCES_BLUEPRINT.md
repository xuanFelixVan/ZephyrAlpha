---
module_id: USER_PREFERENCES_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 蓝图设计、架构规划

---
---

﻿---
module_id: USER_PREFERENCES_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_name: 用户偏好设置
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha用户偏好
compliance_level: 专业标准
parent_document: ../index.md
implementation_status: 蓝图设计
responsibility:
  - 用户偏好设置，负责用户个性化配置、界面定制和偏好管理，不负责系统配置管理
---
# 用户偏好设置模块蓝图
> **核心职责**: User Preferences蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：User Preferences蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 📋 概述

本文档定义了USER PREFERENCES的核心功能和技术实现。


> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: SQLite + Streamlit
> **优先级**: P2（增强模块）

---

## 一、模块概述

### 1.1 功能定位

用户偏好设置模块提供个性化配置功能，支持用户自定义界面和通知偏好。

### 1.2 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 界面偏好 | 主题、语言、时区 | P0 |
| 通知偏好 | 通知方式、频率 | P0 |
| 显示偏好 | 图表样式、数据格式 | P1 |
| 快捷键设置 | 自定义快捷键 | P2 |

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  用户偏好技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Streamlit  │ ◄─── │   SQLite    │                 │
│  │  (界面)     │      │  (存储)     │                 │
│  └─────────────┘      └─────────────┘                 │
│                                                         │
│  偏好类型:                                              │
│  - 界面偏好 (UI)                                        │
│  - 通知偏好 (Notification)                              │
│  - 显示偏好 (Display)                                   │
│  - 快捷键 (Shortcuts)                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、架构设计

### 3.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    用户偏好系统架构                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Streamlit界面                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  偏好分类                                         │ │ │
│  │  │  - 界面偏好                                       │ │ │
│  │  │  - 通知偏好                                       │ │ │
│  │  │  - 显示偏好                                       │ │ │
│  │  │  - 快捷键                                         │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   偏好管理层                           │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  偏好加载  │ │  偏好保存  │ │  偏好验证  │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   SQLite数据库                         │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  user_preferences表                              │ │ │
│  │  │  - user_id (用户ID)                              │ │ │
│  │  │  - preference_key (偏好键)                       │ │ │
│  │  │  - preference_value (偏好值)                     │ │ │
│  │  │  - updated_at (更新时间)                         │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、偏好设置设计

### 4.1 界面偏好

| 偏好项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| theme | string | "light" | 主题 (light/dark) |
| language | string | "zh_CN" | 语言 |
| timezone | string | "Asia/Shanghai" | 时区 |
| font_size | int | 14 | 字体大小 |
| page_size | int | 20 | 每页显示数量 |

### 4.2 通知偏好

| 偏好项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| email_notification | bool | true | 邮件通知 |
| wechat_notification | bool | true | 微信通知 |
| alert_frequency | string | "immediate" | 告警频率 |
| daily_report | bool | true | 每日报告 |
| weekly_report | bool | true | 每周报告 |

### 4.3 显示偏好

| 偏好项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| chart_style | string | "line" | 图表样式 |
| date_format | string | "YYYY-MM-DD" | 日期格式 |
| number_format | string | "#,##0.00" | 数字格式 |
| currency | string | "CNY" | 货币单位 |
| decimal_places | int | 2 | 小数位数 |

### 4.4 快捷键设置

| 快捷键 | 默认值 | 功能 |
|--------|--------|------|
| save | "Ctrl+S" | 保存 |
| refresh | "F5" | 刷新 |
| search | "Ctrl+F" | 搜索 |
| help | "F1" | 帮助 |

---

## 五、界面设计

### 5.1 主界面布局

```
┌────────────────────────────────────────────────────────────┐
│                    ZephyrAlpha 用户偏好                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  偏好分类: [界面偏好 ▼]                              │ │
│  │                                                      │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  界面偏好                                       │ │ │
│  │  │                                                │ │ │
│  │  │  主题: [浅色 ▼]                                │ │ │
│  │  │  语言: [简体中文 ▼]                            │ │ │
│  │  │  时区: [Asia/Shanghai ▼]                       │ │ │
│  │  │  字体大小: [14]                                │ │ │
│  │  │  每页显示: [20]                                │ │ │
│  │  │                                                │ │ │
│  │  │  [保存偏好]  [恢复默认]                        │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  当前偏好摘要                                        │ │
│  │  主题: 浅色  语言: 简体中文  时区: Asia/Shanghai    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 六、实施步骤

### 6.1 数据库设计

```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
```

### 6.2 偏好管理类

```python
import sqlite3
import json
from typing import Dict, Any

class PreferenceManager:
    def __init__(self, db_path: str = "data/zephyr.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_key VARCHAR(100) NOT NULL,
                preference_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_key)
            )
        """)
        conn.commit()
        conn.close()
    
    def get_preference(self, user_id: int, key: str, default: Any = None) -> Any:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT preference_value FROM user_preferences WHERE user_id = ? AND preference_key = ?",
            (user_id, key)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
        return default
    
    def set_preference(self, user_id: int, key: str, value: Any):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO user_preferences 
               (user_id, preference_key, preference_value, updated_at) 
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (user_id, key, json.dumps(value))
        )
        conn.commit()
        conn.close()
    
    def get_all_preferences(self, user_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT preference_key, preference_value FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        preferences = {}
        for key, value in results:
            try:
                preferences[key] = json.loads(value)
            except:
                preferences[key] = value
        return preferences
```

### 6.3 Streamlit界面实现

```python
import streamlit as st
from preference_manager import PreferenceManager

st.set_page_config(page_title="ZephyrAlpha用户偏好", layout="wide")

st.title("ZephyrAlpha 用户偏好")

# 初始化偏好管理器
pref_manager = PreferenceManager()
user_id = 1  # 当前用户ID

# 偏好分类
pref_type = st.sidebar.selectbox(
    "偏好分类",
    ["界面偏好", "通知偏好", "显示偏好", "快捷键"]
)

if pref_type == "界面偏好":
    st.subheader("界面偏好")
    
    # 加载当前偏好
    theme = pref_manager.get_preference(user_id, "theme", "light")
    language = pref_manager.get_preference(user_id, "language", "zh_CN")
    timezone = pref_manager.get_preference(user_id, "timezone", "Asia/Shanghai")
    font_size = pref_manager.get_preference(user_id, "font_size", 14)
    page_size = pref_manager.get_preference(user_id, "page_size", 20)
    
    # 偏好编辑
    new_theme = st.selectbox("主题", ["light", "dark"], index=["light", "dark"].index(theme))
    new_language = st.selectbox("语言", ["zh_CN", "en_US"], index=["zh_CN", "en_US"].index(language))
    new_timezone = st.selectbox("时区", ["Asia/Shanghai", "America/New_York"], index=["Asia/Shanghai", "America/New_York"].index(timezone))
    new_font_size = st.slider("字体大小", 10, 20, font_size)
    new_page_size = st.slider("每页显示", 10, 50, page_size)
    
    # 保存按钮
    if st.button("保存偏好"):
        pref_manager.set_preference(user_id, "theme", new_theme)
        pref_manager.set_preference(user_id, "language", new_language)
        pref_manager.set_preference(user_id, "timezone", new_timezone)
        pref_manager.set_preference(user_id, "font_size", new_font_size)
        pref_manager.set_preference(user_id, "page_size", new_page_size)
        st.success("偏好保存成功！")

elif pref_type == "通知偏好":
    st.subheader("通知偏好")
    
    # 加载当前偏好
    email_notif = pref_manager.get_preference(user_id, "email_notification", True)
    wechat_notif = pref_manager.get_preference(user_id, "wechat_notification", True)
    alert_freq = pref_manager.get_preference(user_id, "alert_frequency", "immediate")
    
    # 偏好编辑
    new_email = st.checkbox("邮件通知", value=email_notif)
    new_wechat = st.checkbox("微信通知", value=wechat_notif)
    new_alert_freq = st.selectbox("告警频率", ["immediate", "hourly", "daily"], index=["immediate", "hourly", "daily"].index(alert_freq))
    
    if st.button("保存偏好"):
        pref_manager.set_preference(user_id, "email_notification", new_email)
        pref_manager.set_preference(user_id, "wechat_notification", new_wechat)
        pref_manager.set_preference(user_id, "alert_frequency", new_alert_freq)
        st.success("偏好保存成功！")
```

---

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 偏好加载 | 可加载用户偏好 | 功能测试 |
| 偏好保存 | 可保存用户偏好 | 功能测试 |
| 偏好应用 | 偏好生效 | 功能测试 |
| 偏好恢复 | 可恢复默认 | 功能测试 |

### 7.2 性能验收

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 偏好加载 | < 100ms | 加载用户偏好 |
| 偏好保存 | < 200ms | 保存用户偏好 |

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
- **模块ID**: 8.11
- **蓝图文档**: [USER_PREFERENCES_BLUEPRINT.md](../11_USER_PREFERENCES/USER_PREFERENCES_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha用户偏好
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha用户偏好 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active


---

## 📊 文档治理

### 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |

---
