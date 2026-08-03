---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.0.0"
date: 2026-08-03
---

# 作战地图·仓位阶段

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/_zoomable_html/battle_map_08_position_management.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> battle_map §position_management 阶段，21 环节。
> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。

## 文档基本信息 / Document Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 阶段 | 仓位（position_management） | Stage | 仓位 |
| 环节数 | 21 | Steps | 21 |
| 流转边 | 30 | Edges | 30 |
| 状态分布 | 🟦 运营态（已建）=20 ｜ 🟨 候选态（候选池）=1 | State Distribution | 🟦 运营态（已建）=20 ｜ 🟨 候选态（候选池）=1 |

> **图例说明 / Legend**：
> - 🟦 **蓝色实线 = 运营态环节**（production，锚点模块已建）
> - 🟧 **橙色虚线 = 设计态环节**（design，锚点模块待施工）
> - 🟥 **红色 = 弃用态**（deprecated）
> - ⬜ **灰色 = 缺失态**（missing，环节无锚点，BM-INV-001 违例）
> - 🟨 **黄色虚线 = 候选态**（candidate，承载模块在候选池）
> - **实线箭头 ``-->`` = 运营态流转**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态流转**（含设计/候选/混合）

## 阶段图 / Stage Diagram

> 展示 仓位 阶段全部 21 个环节及流转边，颜色区分五态。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
%% 仓位阶段图
flowchart TD
    BM_POS_01["【BM-POS-01 仓位管理裁决】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）<br/>🟡候选承载"]
    BM_POS_06["【BM-POS-06 现金管理约束】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_08["【BM-POS-08 日历仓位约束】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_02["【BM-POS-02 标级仓位Kelly】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_03["【BM-POS-03 持仓状态机漂移】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_07["【BM-POS-07 再平衡执行】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_09["【BM-POS-09 卖出仓位反馈链路】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_04["【BM-POS-04 跨策略仓位硬限制】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_05["【BM-POS-05 资金曲线回撤缩放】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    BM_POS_10["【BM-POS-10 仓位审计追溯】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
    subgraph sg_BM_SEL_20 ["多策略交叉投票"]
        BM_SEL_20["【BM-SEL-20 多策略交叉投票】<br/>—<br/>仓位阶段 / position_management<br/>（候选态 / candidate）<br/>🟡候选承载"]
        BM_SEL_20_A["【BM-SEL-20-A 信号合成与决策去重】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_20_B["【BM-SEL-20-B 多策略资金分配】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_20_C["【BM-SEL-20-C 策略相关性门禁】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_20 -.->|嵌套| BM_SEL_20_A
        BM_SEL_20 -.->|嵌套| BM_SEL_20_B
        BM_SEL_20 -.->|嵌套| BM_SEL_20_C
    end
    subgraph sg_BM_SEL_21 ["组合优化"]
        BM_SEL_21["【BM-SEL-21 组合优化】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）<br/>🟡候选承载"]
        BM_SEL_21_A["【BM-SEL-21-A 策略引擎】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_21_B["【BM-SEL-21-B 组合优化器】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_21_C["【BM-SEL-21-C 再平衡调度】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_21_D["【BM-SEL-21-D 约束求解器】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_21_E["【BM-SEL-21-E 绩效归因引擎】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）"]
        BM_SEL_21_F["【BM-SEL-21-F 量化策略集】<br/>—<br/>仓位阶段 / position_management<br/>（生产态 / production）<br/>🟡候选承载"]
        BM_SEL_21 -.->|嵌套| BM_SEL_21_A
        BM_SEL_21 -.->|嵌套| BM_SEL_21_B
        BM_SEL_21 -.->|嵌套| BM_SEL_21_C
        BM_SEL_21 -.->|嵌套| BM_SEL_21_D
        BM_SEL_21 -.->|嵌套| BM_SEL_21_E
        BM_SEL_21 -.->|嵌套| BM_SEL_21_F
    end
    BM_POS_08 ~~~ BM_POS_09 ~~~ BM_POS_05 ~~~ BM_SEL_20 ~~~ BM_SEL_20_A ~~~ BM_SEL_20_B ~~~ BM_SEL_20_C ~~~ BM_SEL_21_A ~~~ BM_SEL_21_B ~~~ BM_SEL_21_C ~~~ BM_SEL_21_D ~~~ BM_SEL_21_E ~~~ BM_SEL_21_F
    BM_POS_01 ~~~ BM_POS_03 ~~~ BM_SEL_21
    BM_POS_06 ~~~ BM_POS_07
    BM_SEL_20 -.->|漏斗L5→L6 / data_flow| BM_SEL_21
    BM_POS_01 -->|风险配额→标级Kelly / data_flow| BM_POS_02
    BM_POS_02 -->|标级仓位→跨策略硬限制 / data_flow| BM_POS_04
    BM_POS_03 -->|漂移触发→标级仓位调整 / trigger| BM_POS_02
    BM_POS_05 -->|回撤缩放→标级仓位约束 / trigger| BM_POS_02
    BM_POS_05 -->|回撤缩放→跨策略硬限制 / trigger| BM_POS_04
    BM_POS_01 -->|风险配额→现金约束 / data_flow| BM_POS_06
    BM_POS_06 -->|现金约束→标级Kelly / data_flow| BM_POS_02
    BM_POS_03 -->|漂移触发→再平衡执行 / trigger| BM_POS_07
    BM_POS_07 -->|再平衡→标级仓位调整 / data_flow| BM_POS_02
    BM_POS_07 -->|再平衡→仓位审计 / data_flow| BM_POS_10
    BM_POS_08 -->|日历约束→仓位裁决上限 / trigger| BM_POS_01
    BM_POS_08 -->|日历约束→跨策略硬限制 / trigger| BM_POS_04
    BM_POS_09 -->|仓位反馈→状态机 / trigger| BM_POS_03
    BM_POS_02 -->|标级仓位→审计 / data_flow| BM_POS_10
    BM_POS_04 -->|实际仓位→审计 / data_flow| BM_POS_10
classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
classDef deprecated fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
classDef missing fill:#eeeeee,stroke:#9e9e9e,stroke-width:2px,color:#000
classDef candidate fill:#fffde7,stroke:#f9a825,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    class BM_POS_01,BM_POS_06,BM_POS_08,BM_POS_02,BM_POS_03,BM_POS_07,BM_POS_09,BM_POS_04,BM_POS_05,BM_POS_10,BM_SEL_21,BM_SEL_20_A,BM_SEL_20_B,BM_SEL_20_C,BM_SEL_21_A,BM_SEL_21_B,BM_SEL_21_C,BM_SEL_21_D,BM_SEL_21_E,BM_SEL_21_F production
    class BM_SEL_20 candidate
```

## 环节详情

### BM-POS-01 仓位管理裁决



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 编排后决策（买/卖）就绪 阈值: 仓位决策唯一裁决中心 |
| ② 消费数据/因子 | 编排后决策（来自 BM-BUY-03）<br>卖出决策（来自 BM-SELL-02）<br>分批仓位方案（来自 BM-BUY-04） |
| ③ 参数 | position_cap=目标仓位（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 买/卖决策+分批方案 → 处理: C-047 仓位唯一裁决 → 输出: 最终仓位指令 → 下游: BM-EXE-01 风控审批 |
| ⑤ 代码映射 | C-047 / 草图§1.8 主动脉（v4.0新增 P0） |
| ⑥ 降级/中止 | C-047 不可用 → 降级固定比例仓位查表 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0019 | supplement | candidate | — |
| depgraph | MOD-POS-001 | primary | stable | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-06 现金管理约束



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 资金流水变更 / 结算状态更新 / 节假日临近 阈值: — |
| ② 消费数据/因子 | 资金流水+结算状态（来自 D-EX-CORE CTR-006）<br>最低储备金配置（来自 D-PF-CORE）<br>节假日日历（来自 D-DATA） |
| ③ 参数 | 最低储备金=账户最低现金底线（范围 -，代码当前: 最低储备金约束，状态: implemented）<br>机会储备X%=预留突发机会现金比例（范围 -，代码当前: 机会储备比例，状态: implemented）<br>T+1结算约束=当日卖出资金T+1才可用（范围 -，代码当前: T+1结算约束，状态: implemented）<br>节假日现金比例=节前2天+节后1天提高5-15%（范围 5-15%，代码当前: 节假日持币规划，状态: implemented）<br>闲置资金逆回购=闲置现金逆回购生息（范围 -，代码当前: 逆回购，状态: implemented） |
| ④ 数据流 | 输入: 资金流水+结算状态 → 处理: 可用资金计算+现金约束判定 → 输出: 现金头寸+现金约束 → 下游: BM-POS-01 仓位裁决(现金可用额度内决策) |
| ⑤ 代码映射 | MOD-POS-006 / D-POSITION §1.1 POS-06 + §7.1 第一层组合层现金约束 |
| ⑥ 降级/中止 | 现金管理器未就绪 → 按T+1可用资金粗略估算(可能高估可用资金，需风控层兜底) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-006 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-08 日历仓位约束



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 当前日期命中风险日历事件 阈值: — |
| ② 消费数据/因子 | A股风险日历（来自 D-DATA）<br>当前持仓（来自 D-EX-CORE）<br>ST标记（来自 D-FACTOR）<br>市值分类（来自 D-FACTOR） |
| ③ 参数 | 期权交割日=否决新开仓位(仅允许减仓)（范围 -，代码当前: 期权交割日否决新开仓，状态: implemented）<br>4月下旬ST清零=ST股仓位强制清零（范围 -，代码当前: 年报截止日ST清零，状态: implemented）<br>预告截止日前5日=否决未出预告个股新买入（范围 -，代码当前: 预告截止日前5日否决新买入，状态: implemented）<br>微盘股空窗期=<50亿市值仓位上限收紧50%（范围 -，代码当前: 股东信息空窗期微盘股收紧50%，状态: implemented）<br>交割日前后=仓位上限临时下调5-10%（范围 5-10%，代码当前: 交割日前后下调5-10%，状态: implemented）<br>财报前3天=标的仓位上限下调+禁止新建（范围 -，代码当前: 财报前3天降仓位+禁新建，状态: implemented） |
| ④ 数据流 | 输入: 风险日历+当前日期 → 处理: 日历事件匹配+临时仓位上限调整 → 输出: CalendarPositionAlert+临时仓位上限 → 下游: BM-POS-01 仓位裁决上限 / BM-POS-04 跨策略硬限制 |
| ⑤ 代码映射 | MOD-POS-017 / D-POSITION §1.5 POS-17 + §7.4 A股风险日历 |
| ⑥ 降级/中止 | 日历数据缺失 → 跳过日历约束(仅依赖市场状态仓位上限，可能漏防周期性风险) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-017 | primary | stable | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-02 标级仓位Kelly



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 买入信号到达 / 再平衡触发 阈值: — |
| ② 消费数据/因子 | 买入信号+得分（来自 BM-BUY-04）<br>风险配额(每标的MRC)（来自 BM-POS-01风险预算层）<br>密度PDF(偏度/峰度/VaR/CVaR)（来自 BM-SEL-13）<br>流动性评分(退出时间<1天)（来自 BM-EXE-01） |
| ③ 参数 | Kelly公式=0.5×f*(半Kelly)（范围 -，代码当前: 待实现，状态: proposed）<br>半Kelly硬上限=禁止全Kelly（范围 -，代码当前: 待实现，状态: proposed）<br>偏度调整系数=正偏×(1+α)/负偏×(1-|α|)（范围 -，代码当前: 待实现，状态: proposed）<br>峰度惩罚系数=超额峰度>0→×(1-β)（范围 -，代码当前: 待实现，状态: proposed）<br>前瞻VaR阈值=95%VaR>阈值→仓位上限下调（范围 -，代码当前: 待实现，状态: proposed）<br>正偏加仓幅度=≤原优化仓位10%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 信号+风险配额+密度PDF → 处理: Kelly求解→半Kelly截断→风险配额约束→分布感知调整(防御性只减不增) → 输出: 标级仓位建议 → 下游: BM-POS-04 跨策略硬限制 → BM-EXE-01 风控 |
| ⑤ 代码映射 | MOD-POS-001 / 草图§1.5 第四层 + §20.13约束13.2 |
| ⑥ 降级/中止 | Kelly引擎未就绪 → 降级为固定比例仓位(按市场状态查表§20.3) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-001 | primary | stable | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-03 持仓状态机漂移



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 状态转换事件 / 仓位漂移>阈值 阈值: — |
| ② 消费数据/因子 | 持仓状态(NONE/BUILDING/ACTIVE/OBSERVING/REDUCING/EXITING/CLOSED)（来自 BM-POS-01）<br>当前权重（来自 BM-POS-01）<br>目标权重（来自 BM-POS-02）<br>漂移幅度（来自 BM-POS-01） |
| ③ 参数 | 组合漂移触发评估=±2%（范围 -，代码当前: 待实现，状态: proposed）<br>单标的漂移触发评估=±3%（范围 -，代码当前: 待实现，状态: proposed）<br>OBSERVING超时=收盘前15min（范围 -，代码当前: 15分钟 (observing_confirm_minutes=15)，状态: implemented）<br>观察期禁止新买入=是（范围 -，代码当前: OBSERVING状态逻辑规则（enter_observing后禁止新开仓），状态: implemented）<br>再平衡收益改善门槛=>2×交易成本（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 持仓状态+权重 → 处理: 状态机迁移+漂移检测+再平衡成本-收益决策 → 输出: 再平衡评估结果(执行/解除) → 下游: BM-POS-02 标级仓位调整 / BM-SELL-05 置换再平衡 |
| ⑤ 代码映射 | MOD-POS-002 / 草图§1.4 v6.0（MOD-POS-002状态机+MOD-POS-003漂移监控） |
| ⑥ 降级/中止 | 状态机未就绪 → 全部按ACTIVE处理，漂移监控退化为日终对账 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-002 | primary | stable | stable |
| depgraph | MOD-POS-003 | supplement | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-07 再平衡执行



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | DriftDetected漂移检测 / 周频日历 / 重大事件 阈值: 组合±2%/单标的±3% |
| ② 消费数据/因子 | 漂移检测结果（来自 BM-POS-03）<br>交易成本（来自 BM-EXE-03）<br>市场状态（来自 BM-SEL-03/C-021）<br>当前持仓（来自 D-EX-CORE CTR-006） |
| ③ 参数 | 收益改善门槛=>2×交易成本（范围 -，代码当前: 再平衡收益改善>2×成本，状态: implemented）<br>恶化市场成本系数=⑦⑧⑨成本×1.5（范围 -，代码当前: 恶化市场成本系数×1.5，状态: implemented）<br>周频强制触发=周频强制再平衡评估（范围 -，代码当前: 周频日历触发，状态: implemented）<br>再平衡后偏差=<1%（范围 -，代码当前: 组合仓位偏差<1%，状态: implemented） |
| ④ 数据流 | 输入: 漂移检测+再平衡调度 → 处理: 成本-收益决策 → 输出: RebalanceTriggered+调仓指令 → 下游: BM-POS-02 标级仓位调整 / BM-POS-10 仓位审计 |
| ⑤ 代码映射 | MOD-POS-004 / D-POSITION §1.1 POS-04 + §7.1 第四层 + §20.13约束13.4 |
| ⑥ 降级/中止 | 再平衡引擎未就绪 → 仅机会成本驱动置换，跳过权重偏离再平衡(保守原则) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-004 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-09 卖出仓位反馈链路



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 卖出决策到达 / 买入后即时验证窗口 / 仓位状态变更 阈值: — |
| ② 消费数据/因子 | 卖出决策（来自 BM-SELL-02 CTR-SELL-001）<br>仓位状态（来自 BM-POS-01/03）<br>买入价+分时均线+ATR（来自 D-MKT_DATA） |
| ③ 参数 | 盈利放宽阈值=盈利状态→卖出阈值放宽（范围 -，代码当前: 盈利状态卖出阈值放宽，状态: implemented）<br>亏损收紧阈值=亏损状态→卖出阈值收紧（范围 -，代码当前: 亏损状态卖出阈值收紧，状态: implemented）<br>5min跌破1%放量=→观察期(OBSERVING)（范围 -，代码当前: 5min跌破买入价>1%且放量→观察，状态: implemented）<br>15min破分时均线=→减仓50%（范围 -，代码当前: 15min跌破分时均线→减仓50%，状态: implemented）<br>30min反向2ATR=→全部止损（范围 -，代码当前: 30min反向运动>2ATR→全部止损，状态: implemented） |
| ④ 数据流 | 输入: 卖出决策+仓位状态 → 处理: 盈亏状态判定+即时验证 → 输出: PositionStateFeedback → 下游: D-SELL-DECISION 卖出阈值动态调整 / BM-POS-03 状态机 |
| ⑤ 代码映射 | MOD-POS-016 / D-POSITION §1.4 POS-16 Sell-Position Bidirectional Link(v6.0) |
| ⑥ 降级/中止 | 双向链路未就绪 → 卖出阈值固定不随盈亏调整(可能过早止盈或过晚止损) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-016 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-04 跨策略仓位硬限制



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 多策略同标的仓位合并 / 新策略上线 / 仓位上限框架触发 阈值: — |
| ② 消费数据/因子 | 各策略仓位建议（来自 BM-POS-02）<br>策略冷启动状态（来自 L3策略工厂）<br>仓位上限框架(9态+2叠加态)（来自 BM-SEL-03/C-021）<br>行业偏离/风格暴露（来自 BM-SEL-21）<br>C-047仓位裁决（来自 BM-POS-01） |
| ③ 参数 | 同标的多策略合并=取sum不超上限（范围 -，代码当前: 待实现，状态: proposed）<br>新策略仓位上限=正常×30%（范围 -，代码当前: 待实现，状态: proposed）<br>行业偏离=±10%/叠加态±15%/绝对30%（范围 -，代码当前: 绝对≤30% (sector_absolute_cap=0.30) / 基准±10% (sector_baseline_deviation=0.10)，状态: implemented）<br>风格暴露=±0.3标准差（范围 -，代码当前: 待实现，状态: proposed）<br>仓位裁决不可绕过=C-047唯一裁决(例外:C-004风控veto)（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 多策略仓位+冷启动+上限框架 → 处理: 合并+冷启动折扣+行业/风格硬约束截断+C-047裁决 → 输出: 实际仓位(≤硬上限) → 下游: BM-EXE-01 风控审批 → BM-EXE-02 执行 |
| ⑤ 代码映射 | MOD-POS-010 / 草图§1.5 第三层 + §20.13约束13.1 |
| ⑥ 降级/中止 | 限制器未就绪 → 单策略独立决策(超限风险，需风控层兜底) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-010 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-05 资金曲线回撤缩放



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 组合净值更新 / 回撤超阈值 / 连续亏损 阈值: — |
| ② 消费数据/因子 | 组合净值历史（来自 BM-REC-01）<br>回撤幅度（来自 BM-POS-01）<br>连续亏损天数（来自 BM-EXE-01/C-032）<br>资金曲线异常模式（来自 C-032） |
| ③ 参数 | 回撤>5%=仓位上限缩减10%（范围 -，代码当前: warning_threshold=0.05, 缩减10%(loss_contraction_5pct=0.10), 仓位上限0.80，状态: implemented）<br>回撤>10%=仓位上限缩减20%（范围 -，代码当前: critical_threshold=0.10, 缩减20%(loss_contraction_10pct=0.20), 仓位上限0.50，状态: implemented）<br>盈利扩张=每次+5%(不超§20.3硬上限)（范围 -，代码当前: profit_expansion_step=0.05(每次新高+5%), 硬上限2.00x，状态: implemented）<br>恢复条件=净值回到回撤前高点（范围 -，代码当前: 净值回到回撤前高点 → 解除收缩，状态: implemented）<br>连续N日亏损触发=C-032检测→C-015告警→C-031降级（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 净值+回撤+连续亏损 → 处理: 资金曲线自诊断+回撤检测+仓位上限缩放/扩张 → 输出: 仓位上限缩放系数 → 下游: BM-POS-02 标级仓位约束 / BM-POS-04 跨策略硬限制 |
| ⑤ 代码映射 | MOD-POS-007 / 草图§9.1 C-032（MOD-POS-007资金曲线+MOD-POS-008回撤控制） |
| ⑥ 降级/中止 | 回撤控制器未就绪 → 仅资金曲线告警不自动缩放(需人工干预) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-007 | primary | stable | stable |
| depgraph | MOD-POS-008 | supplement | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-10 仓位审计追溯



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 任意仓位变更事件(裁决/Kelly/漂移/再平衡/缩放/日历/合并) 阈值: — |
| ② 消费数据/因子 | 仓位变更事件（来自 BM-POS-01~09全部环节）<br>审批链（来自 D-RISK C-004）<br>执行结果（来自 D-EX-CORE） |
| ③ 参数 | 全记录=每次仓位变更全记录（范围 -，代码当前: 全记录，状态: implemented）<br>审批链=决策→裁决→风控→执行全链路（范围 -，代码当前: 审批链，状态: implemented）<br>哈希链防篡改=前一条哈希链接（范围 -，代码当前: 哈希链防篡改，状态: implemented） |
| ④ 数据流 | 输入: 仓位变更事件 → 处理: 全记录+审批链+哈希链 → 输出: PositionAuditReport → 下游: D-REPORTING 归档 / D-GOVERNANCE 合规审计 |
| ⑤ 代码映射 | MOD-POS-009 / D-POSITION §1.3 POS-09 Position Audit Logger |
| ⑥ 降级/中止 | 审计日志器未就绪 → 仓位决策阻断(审计是合规底线，无审计不允许执行，保守原则) |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-009 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-SEL-20 多策略交叉投票



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 30→30只 |
| ② 消费数据/因子 | 策略A价值反转（来自 L3）<br>策略B动量趋势（来自 L3）<br>策略C事件驱动（来自 L3）<br>C-034/C-036主力合力（来自 BM-SEL-05）<br>C-021状态否决（来自 BM-SEL-03） |
| ③ 参数 | 策略权重=A30%/B25%/C20%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 事件筛选输出~30只 → 处理: 多策略YES/NO+主力+合力+状态否决 → 输出: ~30只 → 下游: BM-SEL-21 组合优化 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§13 漏斗L5 |
| ⑥ 降级/中止 | 投票未就绪 → 单策略决定 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-3225 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21 组合优化



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 30→N≤10只 |
| ② 消费数据/因子 | 候选标的+得分（来自 BM-SEL-18）<br>仓位上限（来自 BM-SEL-03）<br>C-042策略容量（来自 L3）<br>C-045拥挤度（来自 L4）<br>密度PDF参数（来自 BM-SEL-13） |
| ③ 参数 | 行业偏离=±10%/叠加态±15%/绝对30%（范围 -，代码当前: 待实现，状态: proposed）<br>相关性上限=corr<0.7（范围 -，代码当前: 待实现，状态: proposed）<br>Kelly=半Kelly硬上限（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 投票输出~30只 → 处理: maxΣ(w×score) s.t.仓位/容量/行业/风格/相关性/拥挤 → 输出: N只下单清单+权重 → 下游: BM-BUY-01 多情景对策 |
| ⑤ 代码映射 | MOD-PF-002 / 草图§8.5 组合优化引擎（部分建设） |
| ⑥ 降级/中止 | 组合优化未就绪 → 等权配置 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-002 | primary | planned | generated |
| candidate | CAND-PFALLOC-001 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-20-A 信号合成与决策去重



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 多策略信号→重合加权重→合成信号+信号冲突检测+决策去重 阈值: 同标的同方向多策略重复信号→合并为一条指令 |
| ② 消费数据/因子 | 多策略信号（来自 BM-SEL-18 精筛评分）<br>因子信号（来自 BM-SEL-02-H 合成优化） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 多策略信号集 → 处理: 信号叠加→冲突检测→权重重分配→决策去重 → 输出: 合成信号(CTR-007前驱) → 下游: BM-SEL-20-B 资金分配 |
| ⑤ 代码映射 | MOD-PA-002 / 06-D-PF-ALLOC PA-02 |
| ⑥ 降级/中止 | 信号合成器异常 → 降级等权合成 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PA-002 | primary | production | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-20-B 多策略资金分配



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 多策略资金分配+风险预算分配+MaxDDLimit+策略容量约束 阈值: 策略权重之和=1.0 + MaxDD≤15% |
| ② 消费数据/因子 | 合成信号（来自 BM-SEL-20-A）<br>风险预算（来自 D-RISK） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 合成信号+风险预算 → 处理: 风险预算分解→Kelly约束→容量约束→权重分配 → 输出: 策略资金分配方案 → 下游: BM-SEL-20-C 相关性门禁 |
| ⑤ 代码映射 | MOD-PA-003 / 06-D-PF-ALLOC PA-03 |
| ⑥ 降级/中止 | 资金分配求解失败 → 降级等权分配 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PA-003 | primary | production | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-20-C 策略相关性门禁



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | G12策略相关性门禁: ρ>0.85拒绝/因子重叠>60%警告/股票池重叠>70%警告 阈值: 6个月滚动窗口+尾部相关EVT |
| ② 消费数据/因子 | 资金分配方案（来自 BM-SEL-20-B） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 策略组合+历史收益 → 处理: 相关性计算→因子重叠检测→股票池重叠检测→门禁裁决 → 输出: 门禁通过/拒绝/警告决策 → 下游: BM-SEL-21 组合优化 |
| ⑤ 代码映射 | MOD-PA-004 / 06-D-PF-ALLOC PA-04 |
| ⑥ 降级/中止 | 相关性数据不足 → 降级警告模式 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PA-004 | primary | production | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21-A 策略引擎



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 策略注册+选择+信号生成+生命周期+版本控制(OCP-002) 阈值: 新策略冷启动仓位上限=正常×30% |
| ② 消费数据/因子 | 门禁通过信号（来自 BM-SEL-20-C） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 门禁通过策略信号 → 处理: 策略注册→选择→信号生成→四维决策(选股/买入/卖出/仓位) → 输出: target_weights → 下游: BM-SEL-21-B 组合优化器 |
| ⑤ 代码映射 | MOD-PF-001 / 05-D-PF-CORE PC-01 |
| ⑥ 降级/中止 | 策略引擎异常 → 降级到上一交易日权重 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-001 | primary | production | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21-B 组合优化器



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 均值方差+风险平价+约束求解→TargetPortfolio(CTR-007) 阈值: Kelly仓位与优化仓位取min(Kelly只减不增) |
| ② 消费数据/因子 | target_weights（来自 BM-SEL-21-A） |
| ③ 参数 | — |
| ④ 数据流 | 输入: target_weights+风险预算 → 处理: 均值方差优化→风险预算→Kelly约束→约束求解 → 输出: TargetPortfolio CTR-007 → 下游: BM-SEL-21-C 再平衡调度 |
| ⑤ 代码映射 | MOD-PF-002 / 05-D-PF-CORE PC-02 |
| ⑥ 降级/中止 | 优化求解失败 → 降级等权+风险预算 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-002 | primary | production | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21-C 再平衡调度



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 阈值触发(±2%/±3%)+日历触发(每周五)+事件触发+风控触发 阈值: 收益改善>2×成本才执行；市场状态⑦⑧⑨成本系数×1.5 |
| ② 消费数据/因子 | TargetPortfolio（来自 BM-SEL-21-B） |
| ③ 参数 | — |
| ④ 数据流 | 输入: TargetPortfolio+当前持仓 → 处理: 漂移检测→触发判定→成本感知→再平衡决策 → 输出: 再平衡指令 → 下游: BM-SEL-21-D 约束求解 |
| ⑤ 代码映射 | MOD-PF-003 / 05-D-PF-CORE PC-03 |
| ⑥ 降级/中止 | 再平衡调度异常 → 延后到下一交易日 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-003 | primary | production | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21-D 约束求解器



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 行业集中度≤30%+偏离基准±10%+MDD≤5%+相关性对冲≤0.7+风格暴露≤±0.3σ 阈值: 拥挤度约束(策略相关性ρ>0.8降权) |
| ② 消费数据/因子 | 再平衡指令（来自 BM-SEL-21-C） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 再平衡指令+约束集 → 处理: 约束建模→求解器优化→可行性检验→权重调整 → 输出: 约束满足的最终权重 → 下游: 执行域 BM-EXE |
| ⑤ 代码映射 | MOD-PF-006 / 05-D-PF-CORE PC-04 |
| ⑥ 降级/中止 | 约束求解不可行 → 放宽软约束+告警 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-006 | primary | production | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21-E 绩效归因引擎



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | Brinson归因+因子归因+风险归因+策略退化检测(IC衰减>50%降权至0) 阈值: 拥挤度检测(策略相关性ρ>0.8/0.9) |
| ② 消费数据/因子 | 组合收益（来自 BM-SEL-21-B）<br>因子衰减（来自 BM-SEL-02-G） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 组合收益+因子表现 → 处理: Brinson分解→因子归因→风险归因→退化检测 → 输出: 归因报告+退化告警 → 下游: 反馈循环 / BM-SEL-02-I 因子治理 |
| ⑤ 代码映射 | MOD-PF-007 / 05-D-PF-CORE PC-10 |
| ⑥ 降级/中止 | 归因数据不足 → 降级粗粒度归因 |

**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-007 | primary | production | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management

### BM-SEL-21-F 量化策略集



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | TopN动量+盘口失衡+VWAP回归+盘中冲高回落策略 阈值: 多策略并行+策略引擎统一管理 |
| ② 消费数据/因子 | 因子信号（来自 BM-SEL-02-H）<br>行情数据（来自 BM-SEL-01） |
| ③ 参数 | — |
| ④ 数据流 | 输入: 因子+行情 → 处理: 策略信号生成→权重计算→风险调整 → 输出: 各策略target_weights → 下游: BM-SEL-21-A 策略引擎 |
| ⑤ 代码映射 | MOD-L05-001 / 05-D-PF-CORE strategies |
| ⑥ 降级/中止 | 策略集体异常 → 降级到TopN动量单策略 |

**锚点**：⚠ 无（BM-INV-001 君子协定违例——环节无锚点=悬空决策）

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L3 ｜ **阶段**：position_management


[← 返回总指挥图](battle_map_panorama.md)