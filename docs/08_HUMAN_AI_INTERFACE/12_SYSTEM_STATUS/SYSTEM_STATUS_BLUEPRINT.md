---
module_id: SYSTEM_STATUS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 系统状态监控，负责系统健康状态检查、服务可用性监控和状态展示，不负责性能监控和告警
layer: Layer 2 (Alpha因子层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准---


﻿---
module_id: SYSTEM_STATUS_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_id: SYSTEM_STATUS_001
module_name: 系统状态面板
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha系统状态
compliance_level: 专业标准
parent_document: ../index.md
implementation_status: 蓝图设计
---
# 系统状态面板模块蓝图
> **核心职责**: System Status蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：System Status蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 📋 概述

本文档定义了SYSTEM STATUS的核心功能和技术实现。


> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: Streamlit + Prometheus API
> **优先级**: P2（增强模块）

---

## 一、模块概述

### 1.1 功能定位

系统状态面板提供实时系统运行状态监控，包括服务状态、资源使用和健康检查。

### 1.2 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 服务状态 | 各服务运行状态 | P0 |
| 资源监控 | CPU、内存、磁盘 | P0 |
| 健康检查 | 系统健康状态 | P0 |
| 性能指标 | 响应时间、吞吐量 | P1 |

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  系统状态技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │  Streamlit  │ ◄─── │ Prometheus  │                 │
│  │  (界面)     │      │   API       │                 │
│  └─────────────┘      └─────────────┘                 │
│         │                                               │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                       │
│  │  psutil     │                                       │
│  │ (系统信息)  │                                       │
│  └─────────────┘                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 三、架构设计

### 3.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    系统状态面板架构                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Streamlit界面                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  状态面板                                         │ │ │
│  │  │  - 服务状态                                       │ │ │
│  │  │  - 资源使用                                       │ │ │
│  │  │  - 健康检查                                       │ │ │
│  │  │  - 性能指标                                       │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│          ┌─────────────────┼─────────────────┐              │
│          ▼                 ▼                 ▼              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │ Prometheus  │   │   psutil    │   │  Health     │      │
│  │   API       │   │  (本地)     │   │  Check      │      │
│  └─────────────┘   └─────────────┘   └─────────────┘      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、状态指标设计

### 4.1 服务状态

| 服务 | 检查方式 | 状态 |
|------|---------|------|
| FastAPI | HTTP健康检查 | 运行中/停止 |
| Grafana | HTTP健康检查 | 运行中/停止 |
| Prometheus | HTTP健康检查 | 运行中/停止 |
| Streamlit | HTTP健康检查 | 运行中/停止 |

### 4.2 资源使用

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| CPU使用率 | CPU占用百分比 | > 80% |
| 内存使用率 | 内存占用百分比 | > 85% |
| 磁盘使用率 | 磁盘占用百分比 | > 90% |
| 网络IO | 网络流量 | 异常波动 |

### 4.3 健康检查

| 检查项 | 说明 | 频率 |
|--------|------|------|
| 数据库连接 | 检查数据库连接 | 每30秒 |
| API响应 | 检查API响应时间 | 每1分钟 |
| 磁盘空间 | 检查磁盘剩余空间 | 每5分钟 |
| 日志错误 | 检查错误日志数量 | 每1分钟 |

---

## 五、界面设计

### 5.1 主界面布局

```
┌────────────────────────────────────────────────────────────┐
│                    ZephyrAlpha 系统状态                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  系统概览                                            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│ │
│  │  │ 服务状态 │ │ CPU使用  │ │ 内存使用 │ │ 磁盘使用 ││ │
│  │  │   4/4    │ │   45%    │ │   62%    │ │   35%    ││ │
│  │  │   🟢     │ │   🟢     │ │   🟢     │ │   🟢     ││ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘│ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  服务状态                                            │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  服务名称      状态      端口      响应时间    │ │ │
│  │  │  FastAPI       🟢运行    8000      45ms        │ │ │
│  │  │  Grafana       🟢运行    3000      120ms       │ │ │
│  │  │  Prometheus    🟢运行    9090      80ms        │ │ │
│  │  │  Streamlit     🟢运行    8501      200ms       │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  资源使用趋势                                        │ │
│  │  [CPU使用率图表]                                     │ │
│  │  [内存使用率图表]                                    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  健康检查                                            │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  检查项        状态      最后检查    详情      │ │ │
│  │  │  数据库连接    🟢正常    10:30:45    连接正常  │ │ │
│  │  │  API响应       🟢正常    10:30:40    45ms      │ │ │
│  │  │  磁盘空间      🟢正常    10:25:00    65%可用   │ │ │
│  │  │  日志错误      🟢正常    10:30:30    0个错误   │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 六、实施步骤

### 6.1 安装依赖

```bash
pip install streamlit psutil requests
```

### 6.2 系统状态检查类

```python
import psutil
import requests
from typing import Dict, List
from datetime import datetime

class SystemStatusChecker:
    def __init__(self):
        self.services = {
            "FastAPI": {"url": "http://localhost:8000/health", "port": 8000},
            "Grafana": {"url": "http://localhost:3000/api/health", "port": 3000},
            "Prometheus": {"url": "http://localhost:9090/-/healthy", "port": 9090},
            "Streamlit": {"url": "http://localhost:8501/_stcore/health", "port": 8501}
        }
    
    def check_service_status(self, service_name: str) -> Dict:
        service = self.services.get(service_name)
        if not service:
            return {"status": "unknown", "response_time": None}
        
        try:
            start_time = datetime.now()
            response = requests.get(service["url"], timeout=5)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {"status": "running", "response_time": response_time}
            else:
                return {"status": "error", "response_time": response_time}
        except:
            return {"status": "stopped", "response_time": None}
    
    def get_system_resources(self) -> Dict:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
    
    def check_health(self) -> List[Dict]:
        health_checks = []
        
        # 数据库连接检查
        try:
            import sqlite3
            conn = sqlite3.connect('data/zephyr.db')
            conn.close()
            health_checks.append({
                "name": "数据库连接",
                "status": "normal",
                "last_check": datetime.now().strftime("%H:%M:%S"),
                "detail": "连接正常"
            })
        except:
            health_checks.append({
                "name": "数据库连接",
                "status": "error",
                "last_check": datetime.now().strftime("%H:%M:%S"),
                "detail": "连接失败"
            })
        
        # 磁盘空间检查
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        health_checks.append({
            "name": "磁盘空间",
            "status": "normal" if disk_percent < 90 else "warning",
            "last_check": datetime.now().strftime("%H:%M:%S"),
            "detail": f"{100 - disk_percent:.1f}%可用"
        })
        
        return health_checks
```

### 6.3 Streamlit界面实现

```python
import streamlit as st
from system_status_checker import SystemStatusChecker
import time

st.set_page_config(page_title="ZephyrAlpha系统状态", layout="wide")

st.title("ZephyrAlpha 系统状态")

# 初始化状态检查器
status_checker = SystemStatusChecker()

# 自动刷新
auto_refresh = st.sidebar.checkbox("自动刷新", value=True)
if auto_refresh:
    refresh_interval = st.sidebar.slider("刷新间隔(秒)", 5, 60, 10)
    time.sleep(refresh_interval)
    st.experimental_rerun()

# 系统概览
st.header("系统概览")
col1, col2, col3, col4 = st.columns(4)

# 服务状态统计
services = status_checker.services
running_count = sum(1 for s in services if status_checker.check_service_status(s)["status"] == "running")

with col1:
    st.metric("服务状态", f"{running_count}/{len(services)}", delta=None)
    st.write("🟢" if running_count == len(services) else "🔴")

# 资源使用
resources = status_checker.get_system_resources()

with col2:
    st.metric("CPU使用", f"{resources['cpu_percent']:.1f}%")
    st.write("🟢" if resources['cpu_percent'] < 80 else "🔴")

with col3:
    st.metric("内存使用", f"{resources['memory_percent']:.1f}%")
    st.write("🟢" if resources['memory_percent'] < 85 else "🔴")

with col4:
    st.metric("磁盘使用", f"{resources['disk_percent']:.1f}%")
    st.write("🟢" if resources['disk_percent'] < 90 else "🔴")

# 服务状态详情
st.header("服务状态")
service_data = []
for service_name in services:
    status = status_checker.check_service_status(service_name)
    service_data.append({
        "服务名称": service_name,
        "状态": "🟢运行" if status["status"] == "running" else "🔴停止",
        "端口": services[service_name]["port"],
        "响应时间": f"{status['response_time']:.0f}ms" if status['response_time'] else "N/A"
    })

st.dataframe(service_data, use_container_width=True)

# 健康检查
st.header("健康检查")
health_checks = status_checker.check_health()
health_data = []
for check in health_checks:
    health_data.append({
        "检查项": check["name"],
        "状态": "🟢正常" if check["status"] == "normal" else "🔴异常",
        "最后检查": check["last_check"],
        "详情": check["detail"]
    })

st.dataframe(health_data, use_container_width=True)

# 手动刷新按钮
if st.button("立即刷新"):
    st.experimental_rerun()
```

---

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 服务状态 | 可显示服务状态 | 功能测试 |
| 资源监控 | 可显示资源使用 | 功能测试 |
| 健康检查 | 可执行健康检查 | 功能测试 |
| 自动刷新 | 可自动刷新 | 功能测试 |

### 7.2 性能验收

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 页面加载 | < 2s | 页面加载时间 |
| 状态检查 | < 5s | 全部服务检查 |
| 刷新间隔 | 可配置 | 自动刷新间隔 |

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
- **模块ID**: 8.12
- **蓝图文档**: [SYSTEM_STATUS_BLUEPRINT.md](../12_SYSTEM_STATUS/SYSTEM_STATUS_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha系统状态
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha系统状态 | **核心模块** |

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
