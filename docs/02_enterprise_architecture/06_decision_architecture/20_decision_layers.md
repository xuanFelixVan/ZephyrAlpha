# 决策流图 · 层级详情图

> 生成时间: 2026-07-30T22:18:45
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 辅助图

L0-L6 层级卡片 + 频率/成熟度/状态 + 流向箭头 + 学习闭环反馈边。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    LL0["L0 数据接入与预处理层<br/>production/stable<br/>miniQMT + iFind + tushare + 另…"]
    LL1["L1 因子计算层<br/>production/stable<br/>因子工厂全生命周期管理 → 盘前全量/盘中增量双模计算 →…"]
    LL2A["L2A 信号层<br/>design/planned<br/>信号工厂 → 多策略投票 → 收益率条件密度预测 → Tr…"]
    LL2B["L2B 主力行为层<br/>design/planned<br/>六阶段识别 + 自迭代推演 + 庄家专项 + 群体博弈模拟…"]
    LL2C["L2C 市场状态与大盘预测层<br/>design/planned<br/>3×3矩阵 + 2叠加态 + 三层大盘预测 + T+1次日…"]
    LL2D["L2D 知识图谱与因果推演层<br/>design/planned<br/>六类知识图谱 → 事件影响链分析 → 因果传导推演 → G…"]
    LL3["L3 策略组合层<br/>production/generated<br/>多策略信号合成 → 资本分配 → 元策略路由 → 组合构建…"]
    LL4["L4 风控层<br/>production/stable<br/>Pre/Post-Trade 风控校验 + Kill Sw…"]
    LL5["L5 学习层<br/>design/planned<br/>7阶段学习流水线 → 模块工厂 → 知识采集 → 反馈闭环…"]
    LL6["L6 自评估层<br/>design/planned<br/>LLM 自评估(Judge+交叉验证) + 多模态金融推理…"]
    LL0 -->|triggering / 触发| LL1
    LL1 -->|triggering / 触发| LL2A
    LL2A -->|triggering / 触发| LL2B
    LL2B -->|triggering / 触发| LL2C
    LL2C -->|triggering / 触发| LL2D
    LL2D -->|triggering / 触发| LL3
    LL3 -->|triggering / 触发| LL4
    LL4 -->|triggering / 触发| LL5
    LL5 -->|triggering / 触发| LL6
    LL6 -.->|feedback / 反馈| LL1
    LL6 -.->|feedback / 反馈| LL5
```

