---
module_id: LIVE_TRADING_INTERFACE_BLUEPRINT_001
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
module_id: LIVE_TRADING_INTERFACE_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha实盘交易界面
compliance_level: 专业标准
parent_document: ../index.md
implementation_status: 蓝图设计
open_source_project: Streamlit
github_url: https://github.com/streamlit/streamlit
license: Apache-2.0
responsibility:
  - 实盘交易界面，负责实盘交易操作、订单管理和交易监控，不负责策略回测和参数优化
## 1. 概述

### 1.1 定位与目标

**模块定位**: Layer 8交易执行核心组件，提供实盘交易监控、订单管理和风险控制界面

**核心目标**:
- 实时交易监控
- 订单管理和执行
- 持仓和资金查看
- 风险实时监控

### 1.2 业务价值

| 价值维度 | 说明 |
|---------|------|
| **交易监控** | 实时查看交易状态 |
| **风险控制** | 实时监控风险指标 |
| **订单管理** | 下单、撤单、改单 |
| **资金管理** | 查看资金和持仓 |

### 1.3 技术选型理由

| 项目 | Stars | 特点 | 选择理由 |
|------|-------|------|---------|
| **Streamlit** | 35k+ | 快速构建数据应用 | ✅ 已有使用经验，快速开发 |
| **Dash** | 21k+ | 企业级Dashboard | ⚠️ 学习曲线陡峭 |
| **Gradio** | 31k+ | ML模型界面 | ⚠️ 非交易专用 |

**最终选择**: **Streamlit** - 已有使用经验，快速开发

## 三、技术实现

### 3.1 安装配置

```bash
pip install streamlit plotly pandas numpy
```

### 3.2 核心代码实现

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

class LiveTradingInterface:
    def __init__(self):
        self.qmt_api = QMTTradingAPI()
    
    def get_account_info(self) -> Dict:
        return self.qmt_api.get_account()
    
    def get_positions(self) -> pd.DataFrame:
        return self.qmt_api.get_positions()
    
    def get_orders(self, status: str = 'all') -> pd.DataFrame:
        return self.qmt_api.get_orders(status=status)
    
    def place_order(
        self,
        symbol: str,
        direction: str,
        quantity: int,
        price: float = None,
        order_type: str = 'limit'
    ) -> Dict:
        return self.qmt_api.place_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            price=price,
            order_type=order_type
        )
    
    def cancel_order(self, order_id: str) -> Dict:
        return self.qmt_api.cancel_order(order_id)
    
    def get_risk_metrics(self) -> Dict:
        positions = self.get_positions()
        account = self.get_account_info()
        
        total_value = account['total_value']
        position_value = positions['market_value'].sum()
        
        return {
            'position_ratio': position_value / total_value,
            'max_single_position': positions['market_value'].max() / total_value,
            'num_positions': len(positions),
            'daily_pnl': account['daily_pnl'],
            'total_pnl': account['total_pnl']
        }
```

### 3.3 Streamlit界面实现

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from live_trading_interface import LiveTradingInterface

st.set_page_config(page_title="实盘交易", layout="wide")

interface = LiveTradingInterface()

st.title("📈 实盘交易监控")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "交易监控",
    "订单管理",
    "持仓管理",
    "风险监控",
    "交易日志"
])

with tab1:
    st.subheader("账户概览")
    
    account = interface.get_account_info()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总资产",
            value=f"¥{account['total_value']:,.2f}",
            delta=f"{account['daily_pnl']:,.2f}"
        )
    
    with col2:
        st.metric(
            label="可用资金",
            value=f"¥{account['available']:,.2f}"
        )
    
    with col3:
        st.metric(
            label="持仓市值",
            value=f"¥{account['position_value']:,.2f}"
        )
    
    with col4:
        st.metric(
            label="今日盈亏",
            value=f"¥{account['daily_pnl']:,.2f}",
            delta=f"{account['daily_pnl_pct']:.2%}"
        )
    
    st.subheader("实时持仓")
    positions = interface.get_positions()
    st.dataframe(
        positions,
        use_container_width=True,
        column_config={
            "market_value": st.column_config.NumberColumn("市值", format="¥%.2f"),
            "profit_loss": st.column_config.NumberColumn("盈亏", format="¥%.2f"),
            "profit_loss_pct": st.column_config.NumberColumn("盈亏%", format="%.2f%%"),
        }
    )

with tab2:
    st.subheader("下单")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.text_input("股票代码", value="000001.SZ")
        direction = st.selectbox("方向", ["买入", "卖出"])
    
    with col2:
        quantity = st.number_input("数量", min_value=100, step=100)
        price = st.number_input("价格", min_value=0.01, step=0.01)
    
    with col3:
        order_type = st.selectbox("订单类型", ["限价单", "市价单"])
        
        if st.button("下单", type="primary"):
            result = interface.place_order(
                symbol=symbol,
                direction="buy" if direction == "买入" else "sell",
                quantity=quantity,
                price=price,
                order_type="limit" if order_type == "限价单" else "market"
            )
            
            if result['success']:
                st.success(f"下单成功！订单号: {result['order_id']}")
            else:
                st.error(f"下单失败: {result['error']}")
    
    st.subheader("订单列表")
    
    status_filter = st.selectbox("订单状态", ["全部", "已报", "已成", "已撤", "已拒"])
    orders = interface.get_orders(status="all" if status_filter == "全部" else status_filter)
    
    st.dataframe(
        orders,
        use_container_width=True,
        column_config={
            "order_time": st.column_config.DatetimeColumn("下单时间"),
            "filled_quantity": st.column_config.NumberColumn("成交数量"),
            "filled_price": st.column_config.NumberColumn("成交价格", format="¥%.2f"),
        }
    )
    
    if st.button("刷新订单"):
        st.rerun()

with tab3:
    st.subheader("持仓明细")
    
    positions = interface.get_positions()
    
    st.dataframe(
        positions,
        use_container_width=True,
        column_config={
            "market_value": st.column_config.NumberColumn("市值", format="¥%.2f"),
            "profit_loss": st.column_config.NumberColumn("盈亏", format="¥%.2f"),
            "profit_loss_pct": st.column_config.NumberColumn("盈亏%", format="%.2f%%"),
        }
    )
    
    st.subheader("持仓分布")
    
    fig = go.Figure(data=[go.Pie(
        labels=positions['symbol'],
        values=positions['market_value'],
        hole=.3
    )])
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("风险指标")
    
    risk_metrics = interface.get_risk_metrics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="仓位比例",
            value=f"{risk_metrics['position_ratio']:.2%}"
        )
    
    with col2:
        st.metric(
            label="最大单仓位",
            value=f"{risk_metrics['max_single_position']:.2%}"
        )
    
    with col3:
        st.metric(
            label="持仓数量",
            value=f"{risk_metrics['num_positions']}"
        )
    
    st.subheader("风险预警")
    
    if risk_metrics['position_ratio'] > 0.8:
        st.warning("⚠️ 仓位过高，建议减仓")
    
    if risk_metrics['max_single_position'] > 0.3:
        st.warning("⚠️ 单一持仓过高，建议分散")
    
    if risk_metrics['daily_pnl'] < -account['total_value'] * 0.05:
        st.error("🚨 今日亏损超过5%，建议止损")

with tab5:
    st.subheader("交易日志")
    
    logs = interface.get_trading_logs()
    
    st.dataframe(
        logs,
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("时间"),
            "type": st.column_config.TextColumn("类型"),
            "message": st.column_config.TextColumn("消息"),
        }
    )

if st.button("刷新数据"):
    st.rerun()

time.sleep(5)
st.rerun()
```

## 五、安全控制

### 5.1 交易确认

```python
def confirm_trade(symbol: str, direction: str, quantity: int, price: float) -> bool:
    confirm = st.checkbox(
        f"确认{direction} {symbol} {quantity}股 @ ¥{price:.2f}",
        value=False
    )
    
    if not confirm:
        st.warning("请确认交易信息")
        return False
    
    return True
```

### 5.2 交易限制

```python
def check_trading_limits(
    symbol: str,
    direction: str,
    quantity: int,
    price: float
) -> Tuple[bool, str]:
    account = interface.get_account_info()
    positions = interface.get_positions()
    
    if direction == "buy":
        required_capital = quantity * price
        if required_capital > account['available']:
            return False, "资金不足"
        
        if quantity * price > account['total_value'] * 0.3:
            return False, "单一持仓超过总资产30%"
    
    if direction == "sell":
        position = positions[positions['symbol'] == symbol]
        if len(position) == 0:
            return False, "无持仓"
        
        if quantity > position['quantity'].values[0]:
            return False, "卖出数量超过持仓"
    
    return True, "检查通过"
```

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收条件 | 测试方法 |
|--------|---------|---------|
| 账户查询 | 可查看账户信息 | 功能测试 |
| 持仓查询 | 可查看持仓信息 | 功能测试 |
| 订单管理 | 可下单、撤单 | 交易测试 |
| 风险监控 | 风险指标正常 | 监控测试 |

### 7.2 性能验收

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 数据刷新 | < 1s | 数据更新时间 |
| 下单响应 | < 2s | 下单响应时间 |
| 界面加载 | < 3s | 页面加载时间 |

## 九、参考资料

### 9.1 开源项目

| 项目 | GitHub | Stars | License |
|------|--------|-------|---------|
| Streamlit | https://github.com/streamlit/streamlit | 35k+ | Apache-2.0 |
| Dash | https://github.com/plotly/dash | 21k+ | MIT |
| Gradio | https://github.com/gradio-app/gradio | 31k+ | Apache-2.0 |

### 9.2 文档资源

| 资源 | 链接 |
|------|------|
| Streamlit文档 | https://docs.streamlit.io/ |
| QMT API文档 | https://dict.thinktrader.net/nativeApi/start_now.html |

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 8: 人机交互层
##### 0.001. Live Trading Interface
- **模块ID**: LIVE_TRADING_INTERFACE_001
- **蓝图文档**: [LIVE_TRADING_INTERFACE_BLUEPRINT.md](./LIVE_TRADING_INTERFACE_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha实盘交易界面
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Live Trading Interface** | ZephyrAlpha实盘交易界面 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

## 📊 文档治理

### 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |

---
