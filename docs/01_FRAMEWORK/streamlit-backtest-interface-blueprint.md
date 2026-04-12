---

module_id: STREAMLIT_BACKTEST_INTERFACE_001

version: 1.0.0

status: Active

created_date: 2026-04-05

last_updated: '2026-04-07'

owner: 系统架构师

standard_type: 专业量化机构蓝图

applicable_scope: Layer 8 - Streamlit交互式回测界面

compliance_level: 顶级专业标准

reference_models:

- Two Sigma Research Platform

- Citadel Quant Dashboard

- Renaissance Backtest Interface

related_documents:

- HUMAN_AI_INTERACTION_BLUEPRINT.md

- GRAFANA_MONITORING_BLUEPRINT.md

parent_document: ./HUMAN_AI_INTERACTION_BLUEPRINT.md

implementation_status: 蓝图设计完成

layer: layer_08

responsibility_boundary: '本文档负责Streamlit交互式回测界面设计，包括：



  - 交互式回测界面



  - 回测参数配置



  - 回测结果可视化





  人机交互层战略规划请参考：HUMAN_AI_INTERACTION_BLUEPRINT.md'

responsibility:

- STREAMLIT_BACKTEST_INTERFACE蓝图设计

---

# Streamlit交互式回测界面蓝图

> **核心职责**: Streamlit Backtest Interface蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：Streamlit Backtest Interface蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容





> **版本**: v1.0  

> **创建日期**: 2026-04-05  

> **实施周期**: 1周  

> **目标**: 构建专业级交互式回测界面，使用Streamlit替代自研前端



---



## 📋 执行摘要



### 核心定位



Streamlit交互式回测界面是Layer 8人机交互层的**快速原型工具**，负责：

- 策略参数实时调整

- 回测结果交互式展示

- 因子分析可视化

- 绩效报告生成



### 开源优先策略



**核心原则**: 使用成熟开源前端框架，不自研前端系统



| 组件 | 开源项目 | 成熟度 | 适用场景 |

|------|---------|--------|---------|

| **快速原型** | Streamlit | ⭐⭐⭐⭐⭐ | 策略研究/回测 |

| **专业仪表板** | Dash (Plotly) | ⭐⭐⭐⭐⭐ | 生产环境 |

| **数据表格** | AG Grid | ⭐⭐⭐⭐⭐ | 大数据展示 |

| **图表库** | Plotly | ⭐⭐⭐⭐⭐ | 交互式图表 |



---



## 一、系统架构设计



### 1.1 整体架构



```

┌─────────────────────────────────────────────────────────────────┐

│              Streamlit交互式回测界面架构                          │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │          用户交互层 (User Interface)                       │ │

│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │

│  │  │参数配置  │  │策略选择  │  │回测控制  │  │结果展示  │ │ │

│  │  │  Panel   │  │  Panel   │  │  Panel   │  │  Panel   │ │ │

│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                           ↓                                     │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │          业务逻辑层 (Business Logic)                       │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ Streamlit App                                       │ │ │

│  │  │ ├── 策略参数管理                                    │ │ │

│  │  │ ├── 回测引擎调用                                    │ │ │

│  │  │ ├── 结果数据处理                                    │ │ │

│  │  │ └── 可视化生成                                      │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                           ↓                                     │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │          数据层 (Data Layer)                               │ │

│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │

│  │  │回测引擎  │  │数据存储  │  │结果缓存  │               │ │

│  │  │(Backtest)│  │(Parquet) │  │ (Redis)  │               │ │

│  │  └──────────┘  └──────────┘  └──────────┘               │ │

│  └───────────────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────────────┘

```



---



## 二、核心组件实现



### 2.1 Streamlit应用结构



```python

import streamlit as st

import pandas as pd

import numpy as np

import plotly.graph_objects as go

from plotly.subplots import make_subplots

from datetime import datetime, timedelta



from backtest.engine import BacktestEngine

from strategies.factory import StrategyFactory

from data.loader import DataLoader





class BacktestDashboard:

    """回测仪表板"""

    

    def __init__(self):

        self.engine = BacktestEngine()

        self.loader = DataLoader()

        

    def run(self):

        """运行仪表板"""

        st.set_page_config(

            page_title="ZephyrAlpha回测系统",

            page_icon="📊",

            layout="wide"

        )

        

        st.title("📊 ZephyrAlpha交互式回测系统")

        

        # 侧边栏配置

        self._render_sidebar()

        

        # 主内容区

        tab1, tab2, tab3, tab4 = st.tabs([

            "📈 回测配置",

            "📊 绩效分析",

            "🔍 因子分析",

            "📋 详细报告"

        ])

        

        with tab1:

            self._render_backtest_config()

        

        with tab2:

            self._render_performance_analysis()

        

        with tab3:

            self._render_factor_analysis()

        

        with tab4:

            self._render_detailed_report()

    

    def _render_sidebar(self):

        """渲染侧边栏"""

        st.sidebar.header("⚙️ 系统配置")

        

        # 策略选择

        strategy_name = st.sidebar.selectbox(

            "选择策略",

            ["双均线策略", "动量策略", "均值回归策略", "因子策略"]

        )

        

        # 时间范围

        start_date = st.sidebar.date_input(

            "开始日期",

            datetime.now() - timedelta(days=365)

        )

        end_date = st.sidebar.date_input(

            "结束日期",

            datetime.now()

        )

        

        # 初始资金

        initial_capital = st.sidebar.number_input(

            "初始资金",

            value=1000000,

            min_value=10000,

            step=10000

        )

        

        # 存储到session_state

        st.session_state['strategy'] = strategy_name

        st.session_state['start_date'] = start_date

        st.session_state['end_date'] = end_date

        st.session_state['initial_capital'] = initial_capital

    

    def _render_backtest_config(self):

        """渲染回测配置"""

        st.header("📈 回测配置")

        

        col1, col2 = st.columns([1, 1])

        

        with col1:

            st.subheader("策略参数")

            

            # 根据策略类型显示不同参数

            strategy = st.session_state.get('strategy', '双均线策略')

            

            if strategy == "双均线策略":

                short_window = st.slider("短期均线", 5, 50, 20)

                long_window = st.slider("长期均线", 20, 200, 60)

                st.session_state['params'] = {

                    'short_window': short_window,

                    'long_window': long_window

                }

            

            elif strategy == "动量策略":

                lookback = st.slider("回看期", 10, 100, 20)

                threshold = st.slider("动量阈值", 0.01, 0.1, 0.05)

                st.session_state['params'] = {

                    'lookback': lookback,

                    'threshold': threshold

                }

        

        with col2:

            st.subheader("交易成本")

            

            commission = st.number_input(

                "手续费率",

                value=0.0003,

                format="%.4f"

            )

            slippage = st.number_input(

                "滑点",

                value=0.0001,

                format="%.4f"

            )

            st.session_state['costs'] = {

                'commission': commission,

                'slippage': slippage

            }

        

        # 运行回测按钮

        if st.button("🚀 运行回测", type="primary"):

            self._run_backtest()

    

    def _run_backtest(self):

        """运行回测"""

        with st.spinner("回测运行中..."):

            # 获取参数

            strategy = st.session_state['strategy']

            params = st.session_state.get('params', {})

            costs = st.session_state.get('costs', {})

            

            # 加载数据

            data = self.loader.load(

                st.session_state['start_date'],

                st.session_state['end_date']

            )

            

            # 创建策略

            strategy_obj = StrategyFactory.create(strategy, params)

            

            # 运行回测

            result = self.engine.run(

                data=data,

                strategy=strategy_obj,

                initial_capital=st.session_state['initial_capital'],

                commission=costs['commission'],

                slippage=costs['slippage']

            )

            

            # 存储结果

            st.session_state['backtest_result'] = result

            

            st.success("✅ 回测完成!")

    

    def _render_performance_analysis(self):

        """渲染绩效分析"""

        st.header("📊 绩效分析")

        

        if 'backtest_result' not in st.session_state:

            st.warning("⚠️ 请先运行回测")

            return

        

        result = st.session_state['backtest_result']

        

        # 关键指标

        col1, col2, col3, col4 = st.columns(4)

        

        with col1:

            st.metric(

                "总收益率",

                f"{result['total_return']:.2%}",

                delta=f"{result['annual_return']:.2%}"

            )

        

        with col2:

            st.metric(

                "夏普比率",

                f"{result['sharpe_ratio']:.2f}",

                delta="基准: 1.0"

            )

        

        with col3:

            st.metric(

                "最大回撤",

                f"{result['max_drawdown']:.2%}",

                delta_color="inverse"

            )

        

        with col4:

            st.metric(

                "胜率",

                f"{result['win_rate']:.2%}",

                delta=f"{result['profit_factor']:.2f}"

            )

        

        # 净值曲线

        st.subheader("净值曲线")

        fig = self._plot_equity_curve(result)

        st.plotly_chart(fig, use_container_width=True)

        

        # 回撤曲线

        st.subheader("回撤曲线")

        fig = self._plot_drawdown(result)

        st.plotly_chart(fig, use_container_width=True)

    

    def _plot_equity_curve(self, result):

        """绘制净值曲线"""

        fig = make_subplots(

            rows=2, cols=1,

            shared_xaxes=True,

            vertical_spacing=0.03,

            row_heights=[0.7, 0.3]

        )

        

        # 净值曲线

        fig.add_trace(

            go.Scatter(

                x=result['dates'],

                y=result['equity_curve'],

                mode='lines',

                name='净值',

                line=dict(color='#1f77b4', width=2)

            ),

            row=1, col=1

        )

        

        # 基准曲线

        fig.add_trace(

            go.Scatter(

                x=result['dates'],

                y=result['benchmark_curve'],

                mode='lines',

                name='基准',

                line=dict(color='#ff7f0e', width=1, dash='dash')

            ),

            row=1, col=1

        )

        

        # 成交量

        fig.add_trace(

            go.Bar(

                x=result['dates'],

                y=result['volume'],

                name='成交量',

                marker_color='lightblue'

            ),

            row=2, col=1

        )

        

        fig.update_layout(

            height=600,

            showlegend=True,

            hovermode='x unified'

        )

        

        return fig

    

    def _plot_drawdown(self, result):

        """绘制回撤曲线"""

        fig = go.Figure()

        

        fig.add_trace(

            go.Scatter(

                x=result['dates'],

                y=result['drawdown'],

                mode='lines',

                name='回撤',

                fill='tozeroy',

                line=dict(color='red', width=1)

            )

        )

        

        fig.update_layout(

            height=300,

            title="回撤曲线",

            xaxis_title="日期",

            yaxis_title="回撤",

            hovermode='x'

        )

        

        return fig

    

    def _render_factor_analysis(self):

        """渲染因子分析"""

        st.header("🔍 因子分析")

        

        if 'backtest_result' not in st.session_state:

            st.warning("⚠️ 请先运行回测")

            return

        

        result = st.session_state['backtest_result']

        

        # IC分析

        col1, col2 = st.columns(2)

        

        with col1:

            st.subheader("IC分布")

            fig = self._plot_ic_distribution(result)

            st.plotly_chart(fig, use_container_width=True)

        

        with col2:

            st.subheader("IC衰减")

            fig = self._plot_ic_decay(result)

            st.plotly_chart(fig, use_container_width=True)

        

        # 分层回测

        st.subheader("分层回测")

        fig = self._plot_layered_backtest(result)

        st.plotly_chart(fig, use_container_width=True)

    

    def _render_detailed_report(self):

        """渲染详细报告"""

        st.header("📋 详细报告")

        

        if 'backtest_result' not in st.session_state:

            st.warning("⚠️ 请先运行回测")

            return

        

        result = st.session_state['backtest_result']

        

        # 交易记录

        st.subheader("交易记录")

        df_trades = pd.DataFrame(result['trades'])

        st.dataframe(df_trades, use_container_width=True)

        

        # 持仓记录

        st.subheader("持仓记录")

        df_positions = pd.DataFrame(result['positions'])

        st.dataframe(df_positions, use_container_width=True)

        

        # 导出按钮

        col1, col2 = st.columns(2)

        

        with col1:

            csv_trades = df_trades.to_csv(index=False).encode('utf-8')

            st.download_button(

                "下载交易记录",

                csv_trades,

                "trades.csv",

                "text/csv"

            )

        

        with col2:

            csv_positions = df_positions.to_csv(index=False).encode('utf-8')

            st.download_button(

                "下载持仓记录",

                csv_positions,

                "positions.csv",

                "text/csv"

            )





if __name__ == "__main__":

    dashboard = BacktestDashboard()

    dashboard.run()

```



### 2.2 策略参数管理



```python

import streamlit as st

from typing import Dict, Any





class StrategyParameterManager:

    """策略参数管理器"""

    

    @staticmethod

    def render_params(strategy_name: str) -> Dict[str, Any]:

        """渲染策略参数"""

        params = {}

        

        if strategy_name == "双均线策略":

            col1, col2 = st.columns(2)

            with col1:

                params['short_window'] = st.number_input(

                    "短期均线周期",

                    min_value=5,

                    max_value=50,

                    value=20

                )

            with col2:

                params['long_window'] = st.number_input(

                    "长期均线周期",

                    min_value=20,

                    max_value=200,

                    value=60

                )

        

        elif strategy_name == "动量策略":

            params['lookback'] = st.slider(

                "回看期",

                min_value=10,

                max_value=100,

                value=20

            )

            params['threshold'] = st.slider(

                "动量阈值",

                min_value=0.01,

                max_value=0.10,

                value=0.05,

                step=0.01

            )

        

        elif strategy_name == "因子策略":

            params['factors'] = st.multiselect(

                "选择因子",

                ["动量", "价值", "质量", "波动率", "流动性"],

                default=["动量", "价值"]

            )

            

            params['factor_weights'] = {}

            for factor in params['factors']:

                params['factor_weights'][factor] = st.slider(

                    f"{factor}权重",

                    min_value=0.0,

                    max_value=1.0,

                    value=1.0/len(params['factors'])

                )

        

        return params

```



---



## 三、可视化组件



### 3.1 绩效指标卡片



```python

import streamlit as st





def render_metrics_card(result: Dict):

    """渲染绩效指标卡片"""

    col1, col2, col3, col4 = st.columns(4)

    

    with col1:

        st.metric(

            "总收益率",

            f"{result['total_return']:.2%}",

            delta=f"{result['annual_return']:.2%} 年化"

        )

    

    with col2:

        st.metric(

            "夏普比率",

            f"{result['sharpe_ratio']:.2f}",

            delta="基准: 1.0"

        )

    

    with col3:

        st.metric(

            "最大回撤",

            f"{result['max_drawdown']:.2%}",

            delta_color="inverse"

        )

    

    with col4:

        st.metric(

            "胜率",

            f"{result['win_rate']:.2%}",

            delta=f"盈亏比: {result['profit_factor']:.2f}"

        )

```



### 3.2 交互式图表



```python

import plotly.graph_objects as go

from plotly.subplots import make_subplots





def create_interactive_chart(result: Dict):

    """创建交互式图表"""

    fig = make_subplots(

        rows=3, cols=1,

        shared_xaxes=True,

        vertical_spacing=0.05,

        row_heights=[0.5, 0.3, 0.2]

    )

    

    # K线图

    fig.add_trace(

        go.Candlestick(

            x=result['dates'],

            open=result['open'],

            high=result['high'],

            low=result['low'],

            close=result['close'],

            name='K线'

        ),

        row=1, col=1

    )

    

    # 买卖信号

    buy_signals = result[result['signal'] == 'buy']

    sell_signals = result[result['signal'] == 'sell']

    

    fig.add_trace(

        go.Scatter(

            x=buy_signals['dates'],

            y=buy_signals['close'],

            mode='markers',

            marker=dict(symbol='triangle-up', size=10, color='red'),

            name='买入'

        ),

        row=1, col=1

    )

    

    fig.add_trace(

        go.Scatter(

            x=sell_signals['dates'],

            y=sell_signals['close'],

            mode='markers',

            marker=dict(symbol='triangle-down', size=10, color='green'),

            name='卖出'

        ),

        row=1, col=1

    )

    

    # 净值曲线

    fig.add_trace(

        go.Scatter(

            x=result['dates'],

            y=result['equity_curve'],

            mode='lines',

            name='净值',

            line=dict(color='blue', width=2)

        ),

        row=2, col=1

    )

    

    # 回撤曲线

    fig.add_trace(

        go.Scatter(

            x=result['dates'],

            y=result['drawdown'],

            mode='lines',

            name='回撤',

            fill='tozeroy',

            line=dict(color='red', width=1)

        ),

        row=3, col=1

    )

    

    fig.update_layout(

        height=800,

        showlegend=True,

        hovermode='x unified',

        xaxis_rangeslider_visible=False

    )

    

    return fig

```



---



## 四、实施计划



### 4.1 实施阶段



| 阶段 | 时间 | 目标 | 交付物 |

|------|------|------|--------|

| **阶段1** | 第1天 | Streamlit环境搭建 | 基础应用框架 |

| **阶段2** | 第2-3天 | 回测配置界面 | 参数配置+回测控制 |

| **阶段3** | 第4-5天 | 绩效分析界面 | 指标展示+图表可视化 |

| **阶段4** | 第6-7天 | 因子分析+报告 | 因子分析+详细报告 |



### 4.2 运行方式



```bash

# 安装依赖

pip install streamlit plotly pandas numpy



# 运行应用

streamlit run backtest_dashboard.py



# 指定端口

streamlit run backtest_dashboard.py --server.port 8501



# 允许外部访问

streamlit run backtest_dashboard.py --server.address 0.0.0.0

```



---



## 五、最佳实践



### 5.1 性能优化



| 优化项 | 方法 | 效果 |

|--------|------|------|

| **数据缓存** | @st.cache_data | 减少重复计算 |

| **组件缓存** | @st.cache_resource | 减少对象创建 |

| **异步加载** | st.spinner | 提升用户体验 |

| **懒加载** | st.lazy | 按需加载组件 |



### 5.2 用户体验



| 实践 | 说明 | 效果 |

|------|------|------|

| **响应式布局** | st.columns + use_container_width | 适配不同屏幕 |

| **实时反馈** | st.spinner + st.success | 提升交互体验 |

| **错误处理** | try-except + st.error | 友好错误提示 |

| **快捷操作** | st.button + st.download_button | 便捷操作 |



---



## 六、总结



Streamlit交互式回测界面通过**开源优先策略**，实现了：



1. **快速开发** - 1周完成专业级界面

2. **交互式体验** - 实时参数调整

3. **丰富可视化** - Plotly交互式图表

4. **易于部署** - 单文件部署



**核心优势**:

- ✅ 使用成熟开源框架

- ✅ 开发效率高（比自研快10倍）

- ✅ 用户体验好

- ✅ 易于维护



**下一步**:

1. 搭建Streamlit环境（第1天）

2. 开发回测配置界面（第2-3天）

3. 开发绩效分析界面（第4-5天）

4. 开发因子分析+报告（第6-7天）

---



## 1. 文档治理



### 1.1 System_Manifest.md索引



```markdown

#### Layer 8: 人机交互层

##### 0.001. Streamlit Backtest Interface Blueprint

- **模块ID**: STREAMLIT_BACKTEST_INTERFACE_BLUEPRINT_001

- **蓝图文档**: [STREAMLIT_BACKTEST_INTERFACE_BLUEPRINT.md](#)

- **技术规格书**: 待创建

- **职责**: Layer 8 - Streamlit交互式回测界面

- **状态**: Active

```



### 1.2 模块职责边界



| 模块 | 职责 | 边界 |

|------|------|------|

| **Streamlit Backtest Interface Blueprint** | Layer 8 - Streamlit交互式回测界面 | **核心模块** |



### 1.3 版本管理



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |



---



**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active

