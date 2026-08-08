---
ttl: permanent
doc_type: architecture_view
status: draft
version: "0.7.0"
date: 2026-08-04
---

# 交易决策作战地图能力定位书（第五全景图 / battle_map）

> 版本：V0.7.0（BM-INV-007 孤儿模块反向检测）| 2026-08-04
> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）
> 写法：大白话为主，配表格和 ASCII 图。变更历史见文末。
> **文档责任范围**：定义**交易决策作战地图**（`battle_map`）——项目第五全景图——的能力定位、数据模型、真源分工、双向对齐机制、迁移策略。它是 `07_trading_decision_architecture/` 人类视图背后的真源。

> **定位裁定**：`07_` 背后有第五全景图 `battle_map` 作真源，`07_` MD 是它的派生人类视图。全景图共五个：depgraph / dataflowgraph / decisiongraph / blueprint.md / battle_map。

---

## 一、作战地图是什么？（一句话）

**交易决策作战地图（battle_map）是项目的第五全景图——一张以"决策环节"为节点、以"钱怎么赚"为流程主线、把 decisiongraph / depgraph / 候选池 / 蓝图 / 数据流按业务流程串联起来的索引层真源图。**

它回答的问题不是"决策怎么分层"（那是 decisiongraph 的事），也不是"模块依赖谁"（那是 depgraph 的事），而是：

> **"我这个赚钱流程的每一个环节，到底落在哪些模块/候选/蓝图章节上？落地没有？谁来承载？"**

它存在 PostgreSQL（`battle_map_*` 三张表）里，由 `apply_battle_map.py` 写入，由 `generate_battle_map_diagram.py` 派生成 `07_trading_decision_architecture/battle_map/` 目录下的人类视图 MD（旧生成器 `generate_trading_flow_diagram.py` 已于 2026-08-02 退役删除）。

**和现有三图的关系**：

| 图 | 视角 | 节点粒度 | 回答 |
|---|---|---|---|
| depgraph | 依赖 | 模块（.py 文件） | 模块依赖谁 |
| dataflowgraph | 数据流 | 数据集/作业 | 数据怎么流 |
| decisiongraph | 决策零件 | 决策节点（细） | 决策怎么分层 |
| **battle_map（新）** | **作战环节** | **环节（粗，聚合多节点）** | **钱怎么赚、每环节落在哪** |

**和 07_ 视图的关系**：07_ MD 是 battle_map 的派生人类视图（只读）。battle_map 是真源，07_ 改了不算数，battle_map 改了重跑生成器更新 07_。

---

## 二、它解决什么问题？

它解决三个老毛病：

| 毛病 | battle_map 怎么治 |
|---|---|
| **AI 写决策时不知道落在哪** — 人说"加个买入信号融合"，AI 不知道这个环节现有哪些模块承载、是 design 还是没建 | battle_map 每个环节挂载锚点（modules/candidates），AI 查环节就知道落地情况，不凭记忆推断（防幻觉） |
| **零件和装配脱节** — decisiongraph 有 2758 个细粒度节点，没有"业务流程"的聚合视图 | battle_map 是装配图+故事线，把零件按"钱怎么赚"串起来；decisiongraph 是零件手册，两者互补 |
| **模块和作战目的脱节** — 看着 depgraph 某个模块，不知道它服务于赚钱流程的哪个环节、哪个阶段 | battle_map 双向查找：从模块能反查它在作战地图的位置（第几阶段、第几环节），看模块时就知道它的作战使命 |

**本质**：给人类一张作战指挥图，给 AI 一个"写决策时先查落地"的防漂移锚点，给所有模块一个"为什么而建"的作战使命归属。

---


## 三、系统架构上下文（草图 §1.1 / §1.8 摘要）

> 本节摘录草图 [交易决策架构.md](file:///d:/临时工作区/架构图/交易决策架构.md) §1.1（交易决策架构唯一真源）和 §1.8（数据流主动脉与正向闭环）的关键内容，作为作战地图定位的系统背景。作战地图的每个环节都落在下列架构层和数据流上——看环节时能对到"它在第几层、在数据流哪一跳"。
>
> **v9.0 统一架构**：系统架构图 + 决策流全景图合并为唯一真源。上半部分为系统架构（L0-L6 + 横切层），下半部分为决策流全景图（选股→买入→卖出→仓位→支撑）。作战地图（第五全景图）是决策流全景图的索引层真源——它把决策流的每个环节挂载到具体模块/候选/蓝图章节。

### 3.1 L0-L6 分层架构（草图 §1.1）

交易决策系统采用 **7 层并行 + 闭环** 架构（v9.0 唯一真源），数据从接入到决策闭环的完整路径如下：

| 层 | 名称 | 核心职责 | 关键能力/模块 |
|---|---|---|---|
| **L0** | 数据接入与预处理 | 多源数据接入 + 分层时序存储 | miniQMT + iFind + 另类数据源 → 事件总线 → Redis 热/ClickHouse 温/Parquet 冷；FWT 检索增强扩散 + GBM-Diffusion 数据增强 |
| **L1** | 因子计算 | 因子工厂全生命周期 + 分布特征工程 | 盘前全量/盘中增量双模；因子池（设计≥150，运行≤N_max≈64）；UFL 确定性事实层；KAN 可解释函数逼近；因果因子验证（DoWhy/DML）；FactorMAD 投票因子挖掘 |
| **L2-A** | 信号层 | 信号工厂 + 多策略投票 + 分布感知 | 收益率条件密度预测；Transformer/Mamba/xLSTM/Kronos 时序增强；共形预测；不确定性分解 |
| **L2-B** | 主力行为层 | 主力六阶段识别 + 庄家专项 + 群体博弈 | 自迭代推演；庄家行为识别；群体博弈模拟 |
| **L2-C** | 市场状态与大盘预测 | 3×3×3 立方体 + 2 叠加态 + T+1 次日 8 态预测 | 体制转换检测（HMM/变点）；量能第 3 维度；日历修饰器；跨市场传导；Survival 止盈止损时间预测 |
| **L2-D** | 知识图谱与因果推演 | 六类知识图谱 + 事件影响链 + 因果传导 | GNN 股票关系建模；Causal ML（DML+Causal Forest+DoWhy）；供应链传导 GNN；🔒Causal RL（门禁项） |
| **L3** | 策略决策与组合优化 | 策略工厂 + 多情景对策 + 做T + 外部指令 + 组合优化 | 自动发现（GP/SR/LLM 进化搜索/FactorMAD/R&D-Agent）；多策略共振融合；因子直通层；筛选漏斗 6 层；Copula-GARCH；RL 增强 |
| **L3.5** | 仓位管理 | 仓位唯一裁决中心 | 持仓状态机 + 仓位漂移监控 + 再平衡；资金曲线驱动缩放；分布感知仓位调整（半 Kelly） |
| **L4** | 风控与执行 | 三层风控 + 交易执行 | 预判层（前瞻性 VaR/CVaR + 共形 VaR）+ 监控层（流动性/相关性/C-045 拥挤度）+ 熔断层（B-001~B-006）；执行策略选择器（TWAP/VWAP/IS/POV）；微观结构建模；RL 最优执行 |
| **L5** | 闭环优化与自迭代 | 消费复盘数据 → 反馈全链路 | 15 优化维度 + 5 自迭代增强 + 元级迭代；密度预测偏差反馈；漂移检测三闭环；持续学习抗遗忘（EWC）；Alpha 衰减监控；R&D-Agent-Quant 联合优化 |
| **L6** | 决策可解释性与人机协作 | 决策溯源 + 置信度分层 + 信任度模型 | 密度感知溯源；VeNRA Double-Lock 零幻觉锚定；LLM 自评估；🔒多模态金融推理（门禁）；Sentinel 幻觉检测；Spectral Guardrails |

**四轨融合器（MTF）+ 决策编排器（DO）**（v8.0 新增，位于 L3 和 L3.5 之间）：
- **四轨融合器**：逻辑驱动轨 + 数据驱动轨 + 人工指令轨 + 应急保命轨 → 按优先级融合（应急 > 人工 > 自动）
- **决策编排器**：5 条决策路径（买入/卖出/做T/人工/应急）的统一出口，执行优先级仲裁 + 冲突消解 + 去重 + 时序编排

### 3.2 横切层（草图 §1.1 横切层）

贯穿 L0-L6 的全局机制，非数据流节点，而是横切服务：

| 横切层 | 职责 |
|---|---|
| 自动回测与仿真（C-003） | 策略/因子/信号验证的算力管道；样本外门禁 + 过拟合检验 |
| 运行时架构（S-001） | 多进程隔离 + 共享内存 + GPU 分时调度；Supervisor 监控 |
| AI 自治运维（C-008） | 自监控→自诊断→自修复；交易时段 99% AI 维护 |
| ML 模型工厂（C-029） | GPU 调度 + 模型全生命周期；密度预测/主力识别/大盘预测等模型产出 |
| 过拟合系统性防护（C-033） | 覆盖因子/策略/信号/ML 模型全生命周期 |
| 通知告警（C-015）+ 审计合规（C-043）+ 成本治理（C-044） | 运营支撑三件套 |
| 分布式可观测性 | 三支柱：追踪（OpenTelemetry）+ 指标（Prometheus）+ 日志（ClickHouse） |
| 事件溯源 | 状态变更事件持久化→可回放→可重建任意时刻状态 |
| 配置中心 | 策略参数/风控阈值集中管理 + 版本控制 + 热更新 |
| 数据质量 SLA | 端到端数据质量保障，每跳质量检查 |
| 合规自动检查引擎 🔒 | EU AI Act 合规清单自动判定 + AI 决策合规审查 |
| 全局状态聚合器 | 跨域统一状态视图（持仓/市场/风控/策略/资金/系统） |
| MCP 协议 | LLM Agent 工具调用标准化 |
| 模型量化与推理加速 | QNN/GNN→ONNX INT8；LLM→INT4 |

### 3.3 数据流主动脉（草图 §1.8）

**数据流主动脉 P0 串**（每 3 秒 miniQMT Tick 触发一轮）：

```
外部数据源 → C-001 → C-009 → C-005 → MTF → DO → C-047 → C-004 → C-002 → 成交回报
            数据    因子+   多情景  四轨   决策   仓位    自适应  交易
            接入    信号    对策    融合   编排   管理    风控    执行
```

- **8 节点 7 跳**构成主动脉，一旦断开当天无法产生任何交易决策
- C-021（市场状态，P1）激活时嵌入 C-009 和 C-005 之间
- C-014（T+1 次日预测，P1）激活时嵌入 C-021 和 C-005 之间
- 两者均激活时为 10 跳；均未就绪时降级为 8 节点 7 跳

**侧支信号注入**（并行注入决策流）：
- L2-B 主力行为 → 信号注入
- L2-C 大盘预测 → T+1 次日预测约束
- L2-C 体制转换 → 前瞻性预警
- L2-C Survival → 止盈/止损时间预测
- L2-D 知识图谱 → 事件传导
- L2-D Causal ML → 因子因果筛选
- 密度预测 → 条件 PDF + 分布参数
- 共形预测 → 覆盖率保证区间
- 盘中即时反应引擎 → 异常检测→快速执行

### 3.4 闭环反馈路径（草图 §1.8 反向）

```
C-002 交易执行 → C-017 交易运营（清算/费率/公司行为）→ C-010 报告复盘 → C-007 闭环优化
                                                                        │
                                                                        ▼
                                          反馈到 L1~L4 + L3.5 每层（15 优化维度）
```

| 反馈目标 | 优化内容 |
|---|---|
| L1 因子层 | IC 衰减→替代/退役 |
| L2-A 信号层 | 准确率监控→退役/替换 |
| L2-A 共形 | 覆盖率偏差→区间调整 |
| L2-B 主力层 | 推演偏差→画像修正 |
| L2-C 市场状态 | 判定准确率→模型重训练 |
| L2-C Survival | 时间预测偏差→模型重训练 |
| L2-D Causal ML | 因果效应稳定性→因子重筛选 |
| L3 策略层 | A/B 淘汰；参数微调 |
| L4 风控层 | 阈值校准；共形 VaR 覆盖率检验 |
| L4 执行层 | 下单算法优化 |

**回测门禁铁律**：C-007 每轮迭代改动必须经过 C-003 回测门禁（§20.7）。

### 3.5 工厂三兄弟（草图 §1.8）

```
C-027 因子工厂 → C-028 信号工厂 → C-006 策略工厂
   原材料           零件            产品
```

- **C-027 因子工厂**：产出因子（验证标准看 IC）
- **C-028 信号工厂**：消费因子产出信号（验证标准看方向准确率）
- **C-006 策略工厂**：消费信号产出策略（验证标准看 PnL）
- 每层独立退役互不影响；C-029 ML 模型工厂是"AI 岗位工厂"，不在三兄弟之列

### 3.6 作战地图与架构层的对应关系

作战地图的 11 个阶段对应架构层如下（环节→架构层映射，2026-08-03 全生命周期扩展：+5 新阶段）：

| 作战阶段 | 主要落点架构层 | 数据流主动脉位置 |
|---|---|---|
| 研究孵化（research_incubation） | L0 研究基础设施（D-RESEARCH） | 研究数据→特征存储(PIT)→实验追踪→假设管理→策略迭代 |
| 模型训练（model_training） | L0/L1 训练（D-ML-TRAIN） | 训练数据→模型训练→AutoML→实验晋升→漂移自适应 |
| 回测验证（backtest_validation） | L5 回测验证（D-BACKTEST） | 回测引擎→PIT撮合→过拟合检测→Walk-Forward→上线门禁 |
| 仿真验证（simulation_validation） | L5 仿真验证（D-SIMULATION） | 仿真引擎→蒙特卡洛→场景生成→压力测试→数字孪生 |
| 选股（stock_selection） | L1 因子 + L2 信号 + L3 策略工厂 + 筛选漏斗 | C-009 → C-005 前段 |
| 买入（buy_flow） | L3 策略决策 + MTF 四轨融合 + DO 决策编排 | C-005 → MTF → DO |
| 卖出（sell_flow） | L3 卖出决策引擎 + DO 决策编排 | C-005（卖出路径）→ DO |
| 仓位（position_management） | L3.5 仓位管理 | DO → C-047 |
| 风控管控（risk_control） | L4 风控核心（D-RISK） | 风控策略→限额管理→Kill Switch熔断→盘后审计→压力测试 |
| 执行（execution） | L4 风控 + 交易执行 | C-047 → C-004 → C-002 |
| 对账（reconciliation） | L5 闭环优化 + C-017 交易运营 | C-002 → C-017 → C-010 → C-007 |

---

## 四、它不是什么？（边界要画清楚）

| 不是这个 | 为什么不是 |
|---|---|
| decisiongraph 的副本 | battle_map 环节 ≠ decisiongraph 节点。一个环节聚合多个 decision_node + 多个 depgraph 模块 + 候选 + 蓝图章节。battle_map 引用这些图，不复制节点 |
| 07_ 视图本身 | 07_ MD 是 battle_map 的派生人类视图。battle_map 在 DB，07_ 在 docs |
| 策略参数文档 | battle_map 的 `indicators` 字段记录"指标方案的结构化引用"（trigger/threshold/source_module），不是策略参数清单。具体参数值在策略蓝图/代码里 |
| 新造的孤立图 | battle_map 是索引层，所有锚点指向已有各全景图+候选池的现存节点。不 invent 新模块 |
| 替代 trading_flow_narrative.yaml | 叙事职责移交给翻译真源 `battle_map_steps` 段；narrative.yaml 已于 2026-08-02 退役删除（4 横切段迁至 `module_translation_registry.yaml §battle_map_cross_cutting`） |

---

## 五、全景图体系裁定

全景图共**五个**：depgraph / dataflowgraph / decisiongraph / blueprint.md / **battle_map**。

- `07_` MD 是 **battle_map 的派生人类视图**
- `07_` 通过 battle_map 间接进对齐体系（battle_map 进，`07_` 作为派生视图跟随）
- 五态展示机制（production/design/deprecated/missing/candidate）→ 本文 §十
- SSoT 铁律（改真源不改派生物）→ 本文 §七
- 06_/07_ 区别（零件 vs 装配）→ 本文 §一、§二
- 四模式开关 + 应急保命降级 → 仍由翻译真源横切层承载，battle_map 环节引用

---

## 六、数据模型（三张表）

对标 `apply_depgraph.py` / `apply_decisiongraph.py` 模式，新建 `apply_battle_map.py` 写入 PostgreSQL。三张表：

### 6.1 battle_map_steps（作战环节表）—— 真源核心

每个环节一行。环节是"钱怎么赚"流程上的一个业务步骤（如"流动性过滤""四轨融合""风控审批"）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `step_id` | TEXT PK | 环节主键，格式 `BM-<阶段缩写>-<序号>`，如 `BM-BUY-03` |
| `step_name` | TEXT | 环节中文名（如"四轨融合"），与翻译真源 `name_zh` 一致 |
| `flow_stage` | TEXT | 所属阶段（research_incubation/model_training/backtest_validation/simulation_validation/stock_selection/buy_flow/sell_flow/position_management/risk_control/execution/reconciliation，2026-08-03 扩展至 11 阶段） |
| `layer` | TEXT | 映射层（L0/L1/L2A/.../横切），与 decisiongraph layer 对齐 |
| `sort_order` | INT | 环节在流程中的顺序（同 flow_stage 内排序） |
| `narrative_ref` | TEXT | 指向翻译真源 `battle_map_steps` 段的 step_id（叙事真源在外部 YAML） |
| `indicators` | JSONB | 结构化指标（trigger/threshold/source_modules/source_ref），见 §十三 |
| `source_ref` | TEXT | 出处（草图 §1.4 / 现有模块代码），可追溯 |
| `parent_step_id` | TEXT FK | 父环节 step_id（V0.4.0 新增），NULL=根环节，指向同表 step_id（ON DELETE SET NULL） |
| `depth` | INT | 层级深度（V0.4.0 新增，V0.6.0 扩展上限至3），0=根 / 1=子 / 2=孙 / 3=曾孙（上限3） |
| `design_maturity` | TEXT | production / design（环节本身是否已在实盘主链路） |
| `created_at` / `updated_at` | TIMESTAMP | 审计 |

#### 6.1.1 step_id 命名约定（四层嵌套，V0.6.0）

| 层级 | depth | step_id 格式 | 示例 |
|---|---|---|---|
| 根 | 0 | `BM-<阶段>-<序号>` | BM-BUY-02 |
| 子 | 1 | `BM-<阶段>-<序号>-<大写字母>` | BM-BUY-02-A |
| 孙 | 2 | `BM-<阶段>-<序号>-<大写字母>-<数字>` | BM-BUY-02-A-1 |
| 曾孙 | 3 | `BM-<阶段>-<序号>-<大写字母>-<数字>-<小写字母>` | BM-BUY-02-A-1-a |

> 命名规则：子环节用大写字母后缀（A/B/C/D），孙环节在子后加数字（1/2/3），曾孙在孙后加小写字母（a/b/c）。**全自动化**：生成器读 `parent_step_id` + `depth` 字段自动渲染嵌套 subgraph，写入时设置字段即可自动生成父子子孙关系，无需手改代码。

### 6.2 battle_map_anchors（双向对齐关系表）—— 双向查找的核心

每个"环节 ↔ 模块/候选/蓝图/数据流/决策节点"的关联一行。**这是双向查找的真源**（见 §八）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `anchor_id` | SERIAL PK | 锚点主键 |
| `step_id` | TEXT FK → battle_map_steps | 所属环节 |
| `target_graph` | TEXT | 目标图：depgraph / dataflowgraph / decisiongraph / candidate / blueprint |
| `target_id` | TEXT | 目标图里的节点 id（module_id / candidate_id / blueprint_section / decision_node_id / dataflow_node_id） |
| `target_role` | TEXT | 这个目标在该环节扮演的角色：primary（主承载）/ supplement（补充）/ degradation（降级兜底） |
| `status_snapshot` | TEXT | 快照 depgraph.build_status（production/planned/deprecated），给生成器上色用 |
| `created_at` | TIMESTAMP | 审计 |

### 6.3 battle_map_edges（环节流转表）

环节之间的流转关系（数据流/触发/降级）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `edge_id` | SERIAL PK | 边主键 |
| `from_step_id` | TEXT FK → battle_map_steps | 上游环节 |
| `to_step_id` | TEXT FK → battle_map_steps | 下游环节 |
| `edge_type` | TEXT | data_flow / trigger / degradation |
| `label` | TEXT | 边标签（如"候选池""portfolio_target"） |
| `created_at` | TIMESTAMP | 审计 |

### 6.4 环节粒度标准（6 件套）—— 作战地图的灵魂

每个 `battle_map_steps` 环节**必须带 6 件套**，写到"能和代码交互"的细度（比草图 §1.2-§1.6 注解更细）。这是防幻觉的核心——不写清楚，AI 没法和代码交互，人也看不出参数对不对。

| 要素 | 内容 | 例子（分批建仓环节 BM-BUY-04） |
|---|---|---|
| ① 触发条件 | 用什么判定、N/M 阈值 | 满足 2/3：调整周期到位 / 二次回落 / 缩量 |
| ② 消费的数据/因子 | 具体清单 + 来自哪个层/模块 | §6.6进度、§6.7阶段、§6.1.3轮动序列、量比 |
| ③ 参数 | 默认值 + 可配置范围 + **代码当前实际值** + 状态 | 分批数=2(2-4)、间隔=1交易日、满足阈值=2/3 |
| ④ 数据流 | 输入→处理→输出→下游环节 | 进度+阶段+轮动→条件判定→L3.5仓位→L4执行 |
| ⑤ 代码映射 | 实现模块 + 参数在代码位置 | MOD-xxx / src/zephyr/.../xxx.py:L120 |
| ⑥ 降级/中止条件 | 什么情况降级或中止 | 跌破前低→暂停后续批次→止损评估 |

**③ 参数字段支持双向**（代码↔地图双向反馈的核心）：

| 参数状态 | 含义 | 方向 | 用途 |
|---|---|---|---|
| `implemented` | 代码已实现，带 `current_code_value` | 代码→地图 | 把代码实际参数反馈到地图，人看到能提修改建议 |
| `proposed` | 代码没有，人在地图提参数 | 地图→代码 | 先提参数，再验证建代码测试 |
| `testing` | 提议参数正在回测验证 | 地图→代码 | 参数在回测中，未定稿 |

**粒度量化**：按 6 件套标准，6 阶段 × 8-15 环节，预计 **50-100 个环节**（比草图 §1.2-§1.6 的 5 段注解细很多）。6 件套的结构化部分（①②③④⑤⑥）进 DB 的 `indicators` JSONB，大段解释文案进翻译真源 `indicators_zh`。

---

## 七、真源分工（SSoT）

按项目 SSoT 分类铁律（TRAE-062），battle_map 的数据分两类真源：

```
规则数据真源（YAML）                    架构数据真源（PostgreSQL）
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│ module_translation_registry.yaml │    │ battle_map_steps   （环节表）    │
│   §battle_map_steps 段（新增）    │    │ battle_map_anchors （锚点表）    │
│   - name_zh/name_en/plain_zh     │    │ battle_map_edges   （流转表）    │
│   - mechanism_zh（机制说明）      │    │   + indicators JSONB（结构化）   │
│   - indicators_zh（指标文案）     │    │   + status_snapshot              │
└──────────────┬──────────────────┘    └──────────────┬──────────────────┘
               │                                      │
               └─────────────────┬────────────────────┘
                                 ▼
                    generate_battle_map_diagram.py（取代旧 generate_trading_flow_diagram.py，2026-08-02 退役）
                                 │
                                 ▼
              ┌────────────────────────────────────────┐
              │ 07_trading_decision_architecture/       │（派生产物）
              │   battle_map/ 7 MD + 7 HTML（带颜色）   │
              └────────────────────────────────────────┘
```

| 数据类型 | 真源 | 写入工具 | 说明 |
|---|---|---|---|
| 环节元数据（step_id/flow_stage/layer/sort_order/design_maturity） | DB | `apply_battle_map.py` | 架构数据 |
| 双向锚点（step↔target 关联） | DB | `apply_battle_map.py` | 架构数据，双向查找真源 |
| 环节流转（edges） | DB | `apply_battle_map.py` | 架构数据 |
| indicators 结构化字段（trigger/threshold/source_modules） | DB | `apply_battle_map.py` | 架构数据，要和模块代码联动 |
| 环节叙事（中英文名/大白话/机制/指标文案） | YAML 翻译真源 | 手工编辑 `module_translation_registry.yaml` | 规则数据，可被多视图复用 |
| 07_ MD + HTML | 派生产物 | `generate_battle_map_diagram.py` | 只读，禁止手编 |

**SSoT 铁律**：
- 改环节叙事 → 改翻译真源 `battle_map_steps` 段 → 重跑生成器
- 改环节结构/锚点/指标结构化字段 → 用 `apply_battle_map.py` 改 DB → 重跑生成器
- 禁止直接改 07_ MD（派生产物，会被覆盖）
- 禁止在生成器代码里硬编码叙事（必须读翻译真源）
- **备份先行**（对标 depgraph 备份铁律 trae_054 STEP0，2026-08-03 补）：改 battle_map 三表（steps/anchors/edges）前 MUST 先 `git commit` 备份当前 YAML + 生成产物。battle_map 同属 PostgreSQL 架构数据真源，虽回滚可靠 `apply_battle_map.py --remove-step` 级联删 anchor/edge，但备份先行防止结构丢失、提供可回溯基线。写 DB 用 `pg_advisory_lock 424245` + 事务原子性（`--batch` 任一失败回滚），备份是事务外的第二道防线。

---

## 八、双向查找机制（核心，本文档的灵魂）

这是作战地图区别于其他三图的核心能力。所有模块最终都是为了实现作战地图上的某个功能——所以必须能双向查找。

### 8.1 两个方向

**方向 A：环节 → 组成模块**（写决策时用）
> "这个买入环节由哪些模块组成？这些模块在全景图还是候选池？是 production 还是 planned？"

```
battle_map_steps.step_id
        │ 查 battle_map_anchors WHERE step_id=?
        ▼
target_graph + target_id + target_role + status_snapshot
        │
        ├─ target_graph=depgraph     → 已决定要建的模块（看 build_status）
        ├─ target_graph=candidate    → 候选池模块（deferred/candidate）
        ├─ target_graph=blueprint    → 蓝图章节（设计意图）
        ├─ target_graph=decisiongraph→ 决策零件节点
        └─ target_graph=dataflowgraph→ 数据流节点
```

**方向 B：模块 → 作战位置**（看模块时用）
> "depgraph 里这个模块，它服务于作战地图的哪个阶段、哪个环节？它的作战使命是什么？"

```
depgraph/candidate 的 module_id
        │ 查 battle_map_anchors WHERE target_graph=? AND target_id=?
        ▼
step_id → battle_map_steps.flow_stage + step_name
        │
        ▼
"这个模块是【买入阶段·四轨融合环节】的主承载模块"
```

### 8.2 为什么用 anchors 表做单一真源，而不在全景图模块上加独立字段

Owner 倾向"在三个全景图+候选池都给模块加一个 battle_map_position 字段"。这个直觉是对的（看模块时一眼看到作战位置），但直接加独立写入字段有**漂移风险**：anchors 表和模块字段两处要同步，一旦不一致就不知道哪个对（违反项目防漂移铁律）。

**推荐方案：单一真源 + 派生展示**
- **真源**：`battle_map_anchors` 表（唯一写入点，由 `apply_battle_map.py` 维护）
- **派生展示**（后置增强，battle_map 建起来后再加）：
  - 全景图模块节点加 `battle_map_step_ids` 字段（数组）——由 `apply_battle_map.py` 单向 sync 写入（anchors→各图字段），**只读缓存，禁止独立写入**
  - 生成器（generate_domain_doc 等）读这个字段，在模块节点上标注"📍 作战地图：买入·四轨融合"
  - 类比：depgraph 的 `gate_reason` 字段也是这种"真源在别处、模块上带快照"的模式（见 visualization_view_template §7.4）

这样既满足"看模块时一眼看到作战位置"，又保证单一真源不漂移。

### 8.3 查询工具

新建 `battle_map_reader.py`（对标 `DecisionGraphReader`），提供两个方向查询接口：
- `get_modules_by_step(step_id) -> list[anchor]`（方向 A）
- `get_steps_by_module(target_graph, target_id) -> list[step]`（方向 B）

### 8.4 不变量

- **BM-INV-001**：每个 `battle_map_steps` 必须至少有一个 `battle_map_anchors`（环节无锚点 = 悬空决策 = 幻觉风险，君子协定告警，跑顺后升级硬阻断）。**V1.1.0 三档分类**（治本）：已确认合理孤儿环节（acknowledged，如"计划中未实现"或"父环节已覆盖"）从违规列表排除——真源 `battle_map_domain_policy.yaml` §acknowledged_orphans.steps，带 review_frequency 到期强制复审。检测器 `align_battle_map.py` `_load_acknowledged_orphans()`。100% AI 开发适配：AI 看到 acknowledged 分类后不再尝试"修复"（消除治理振荡）
- **BM-INV-002**：`battle_map_anchors.target_id` 必须能在 `target_graph` 对应的图/仓库里找到（防幽灵锚点）
- **BM-INV-003**：环节叙事必须来自翻译真源 `battle_map_steps` 段，禁止在生成器硬编码
- **BM-INV-004**：anchor 的 target module/candidate 的 domain 必须在 step.flow_stage 对应的允许域列表里（防域漂移=语义错位，如把卖出决策挂在买入流程）。规则真源：`docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`，检测器：`align_battle_map.py` §5
- **BM-INV-005（未落地/规划中，2026-08-03 降级）**：全景图模块的 `battle_map_step_ids` 派生只读缓存——机制未建设（depgraph.nodes 无此列、apply_battle_map.py 无 sync、align_battle_map.py 不检测），当前通过 `battle_map_anchors` 反查（target_graph=depgraph + target_id=blueprint_id，idx_battle_map_anchors_target 索引支撑），无需派生缓存。未来若出现高频查询性能需求再评估建设。
- **BM-INV-006**（V0.4.0 新增）：父子嵌套一致性——① `parent_step_id` 必须指向同 flow_stage 的已存在环节（防悬空父引用+防跨阶段嵌套）；② `depth ≤ 3`（根→子→孙→曾孙，V0.6.0 扩展上限）；③ parent 链不能成环（A→B→A）；④ `depth` 值与 parent 链长度一致。写入校验：`apply_battle_map.py` op_add_step；对齐检测：`align_battle_map.py` `_check_parent_child_consistency()`
- **BM-INV-007**（V0.7.0 新增，V1.1.0 治本改造）：孤儿模块——业务域（`battle_map_domain_policy.yaml` §domain_classification.business_domains，V1.1.0 用显式分类替代原 flow_stage allowed 域并集——并集含工具域导致 106 个基础设施模块误报）内的 depgraph 节点（node_type=module，排除 deprecated），必须至少有一个 `battle_map_anchors` 指向它（target_graph=depgraph，target_id 命中其 blueprint_id 或 path）。无任何锚点指向 = 没有作战使命 = 造出来没用上 = 幻觉/浪费风险。工具域（D_INFRA_RUNTIME/D_INTEGRATION/D_SHARED/D_SECURITY 等基础设施/管道/支撑）铁律5不挂作战地图，由 domain_classification.tool_domains 天然排除。**V1.1.0 三档分类**（治本）：已确认合理孤儿模块（acknowledged，如 planned 待实现）从违规列表排除——真源 §acknowledged_orphans.modules，带 review_frequency 到期强制复审。对齐检测：`align_battle_map.py` `_business_modules_depgraph()` + 已锚定集合反查 + `_load_domain_classification()` + `_load_acknowledged_orphans()`。君子协定告警，不硬阻断。这是 BM-INV-001 的对偶——001 查"功能没模块"，007 查"模块没功能"，两个方向都显化落单。

---

## 九、与全景图对齐体系的关系

### 9.1 第五全景图

battle_map 和 depgraph / dataflowgraph / decisiongraph / blueprint.md 并列，是第五个全景图。**图名 `battlemap`**（对标 depgraph/dataflowgraph/decisiongraph 的 Xgraph 复合形式），**表前缀 `battle_map_*`**（对标 `decision_*` 的"全词_功能"形式）。在 `panorama_registry` 登记为 `PAN-BATTLE-MAP-01`。

### 9.2 两套对齐，正交不冲突

| 对齐 | 轴 | 回答 | 用途 | 工具 |
|---|---|---|---|---|
| 全景对齐 | `module_id` | 一个模块在4张图里一致吗 | 建模块时 | `align_panoramas.py`（保持不动） |
| 作战地图对齐（新） | `step_id` | 一个环节都落地了吗、落在哪 | 写决策时 | `align_battle_map.py`（新建） |

两套对齐正交：module_id 轴管"模块一致性"，step_id 轴管"环节落地性"。互不干扰。

### 9.3 align_battle_map.py（新建）

检查项（先君子协定，跑顺后升级硬阻断）：
- 环节无锚点（孤儿环节）→ 悬空决策告警
- 锚点 target_id 在目标图找不到（幽灵锚点）→ 告警
- 环节 flow_stage 与 anchors 目标模块的 domain 不匹配（域漂移）→ 告警

### 9.4 候选池挂载

候选池模块（`candidate_module_registry.yaml`）通过 `battle_map_anchors`（target_graph=candidate）挂到具体环节。不再只躺在附录2表格里，而是有明确的作战位置。候选 entry 可选加 `panorama_position.battle_map.step_id` 字段（派生展示，由 anchors sync）。

---

## 十、五态展示机制

07_ MD 按模块状态颜色标注（生成器 join depgraph.build_status 产出）：

| 态 | 来源 | 颜色 | 说明 |
|---|---|---|---|
| 运营态 | depgraph build_status=production | 🟦 蓝色实线 | 已上线运行 |
| 设计态 | depgraph build_status=planned | 🟧 橙色虚线 | 蓝图阶段，代码未写 |
| 弃用态 | depgraph build_status=deprecated | 🟥 红色 | 已弃用 |
| 缺失态 | 环节无锚点 or 锚点 target 找不到 | ⬜ 灰色 | 这个环节压根没模块承载（BM-INV-001 告警） |
| 候选态 | target_graph=candidate | 🟨 黄色 | 在候选池里，未进全景图 |

**治理合规**：过度工程不进 depgraph（设计准入一问标准），只进候选池。battle_map 通过 anchors 把候选挂到环节，07_ 展示时用黄色标注"候选承载"。

---

## 十一、可视化规范

遵循 [visualization_view_template.md](visualization_view_template.md)（三视图 + 可缩放 HTML + 节点四要素 + 预折行铁律 + acquisition 徽标）。battle_map 生成器（`generate_battle_map_diagram.py`，取代已退役的 `generate_trading_flow_diagram.py`）必须复用：
- 灰色主题头 + `flowchart TD`
- 节点四要素（成熟度 + 双语名称 + 大白话 + 路径/标识），叙事来自翻译真源 `battle_map_steps` 段
- `_wrap_label_text()` 预折行（禁止 CSS max-width 二次折行）
- 五类 classDef + 颜色（§十 的五态映射到 classDef）
- acquisition 徽标（设计态环节节点卡成熟度行下方显示 `（🔴自建）`/`（🟢开源）`/`（🟡借鉴）`/`（⬜弃用）`，模板 §4.13）
- HTML 联动生成到 `_zoomable_html/`

**作战地图特有的可视化**：
- 总指挥图：环节节点（按6阶段 subgraph 分层）+ 环节间流转边 + 每个环节挂载的模块小节点（用颜色标状态）
- 分阶段图：单阶段的环节 + 该阶段所有锚点模块
- 每个环节节点点击可展开"组成模块清单"（方向 A）

---

## 十二、生成器现状

`generate_battle_map_diagram.py`（已取代旧生成器 `generate_trading_flow_diagram.py`，旧生成器+旧叙事 YAML 已于 2026-08-02 退役删除）：

| 改造点 | 旧（已退役） | 新（当前真源） |
|---|---|---|
| 主真源 | decisiongraph + narrative.yaml | **battle_map 三表**（steps/anchors/edges） |
| 模块状态 | 不查 depgraph | join depgraph（build_status→颜色） |
| 候选挂载 | 只进附录2 | join 候选池，通过 anchors 挂到环节 |
| 节点细节 | decisiongraph 节点 | join decisiongraph（环节聚合的决策节点） |
| 叙事 | narrative.yaml | 翻译真源 `battle_map_steps` + `battle_map_cross_cutting` 段 |
| 颜色标注 | 仅 production/design | 五态（§十） |

**narrative.yaml 退场记录**（已完成 2026-08-02）：
- `trading_flow_narrative.yaml` 原是 07_ MD 的"故事底稿"（每阶段大白话/ASCII框图/指挥AI提示/横切层四轨共享信号应急降级四模式）
- 退场三步已完成：①迁移期→②4 横切段 YAML→YAML 迁移至 `module_translation_registry.yaml §battle_map_cross_cutting`（four_modes/emergency_degradation/four_tracks/shared_signal_injection）→③narrative.yaml + 旧生成器 + 9 旧 MD + 7 旧 HTML 全部删除
- 防幻觉铁律：两处叙事真源并行会漂移，故退役彻底删除而非永久并存

---

## 十三、迁移策略（草图 v9.0 → 真源）

草图 [交易决策架构.md](file:///d:/临时工作区/架构图/交易决策架构.md)（v9.0，1.4MB，30章）是作战地图的内容来源。分三批迁移：

| 批次 | 草图章节 | 迁移到 | 产出 |
|---|---|---|---|
| 第一批（骨架） | §1.1 主流程 + §1.2-§1.6 五段环节注解 | battle_map_steps + 翻译真源 battle_map_steps 段 | 作战地图骨架（约 20-30 个环节） |
| 第二批（锚点） | §2-§12 层详解里的模块 | battle_map_anchors | 每个环节挂载承载模块 |
| 第三批（横切） | §13 漏斗 / §16 冲突矩阵 / §30 缺失模块 | battle_map_edges + anchors | 流转边 + 缺失环节标灰 |

**迁移原则**：
- 草图里的过度工程（KAN/Mamba/Kronos 等）不进 battle_map，归候选池（设计准入一问标准）
- 草图里的实盘主链路进 battle_map_steps（design_maturity=production）
- 每个环节的 indicators 从草图注解结构化 + 从现有模块代码提炼大白话

---

## 十四、字段详细定义（附录，施工依据）

### 14.1 翻译真源 battle_map_steps 段 schema

在 `module_translation_registry.yaml` 顶层（与 `entries:` 平级）新增 `battle_map_steps:` 段：

```yaml
# 顶层段示例（与 entries: 平级）
battle_map_steps:
  - step_id: BM-BUY-03              # 与 DB battle_map_steps.step_id 一致
    name_zh: 四轨融合                # 环节中文名
    name_en: Four-Track Fusion       # 环节英文名
    plain_zh: |                      # 大白话（做什么/解决什么），可被多视图复用
      把模型驱动轨、数据驱动轨、人工指令轨、应急保命轨的信号
      按优先级融合成一个统一信号。人工>模型>数据，应急压制其他。
    mechanism_zh: |                  # 机制说明（怎么运作）
      四轨信号进仲裁器，按优先级表裁决。人工指令轨最高，应急保命轨
      触发时压制其他三轨。融合后产出 buy_signal 进 L3 策略组合层。
    indicators_zh: |                 # 指标文案解释（大段，结构化字段在 DB）
      融合权重：人工0.5/模型0.3/数据0.2。应急触发条件见 Kill Switch 配置。
      置信度低于0.4时降级到模型驱动轨单跑。
```

> **说明**：这就是"顶层段"——YAML 文件顶层除了已有的 `entries:`（模块条目），新增一个平级的 `battle_map_steps:`（环节条目）。复用同一个翻译真源文件和加载器（`_shared/module_translation_loader.py` 扩展），但不和模块条目混。环节级叙事和大白话可被作战地图视图、未来其他视图复用。

### 14.2 indicators JSONB 结构（DB battle_map_steps.indicators）—— 6 件套 + 双向参数

对齐 §6.4 的 6 件套标准。`indicators` 用灵活 JSONB（不同环节结构不同），定义推荐 schema 但允许扩展。结构化部分进 DB，大段解释文案（`indicators_zh`）进翻译真源。

```json
{
  "trigger": {
    "condition": "满足N/M即激活，默认2/3",
    "items": ["调整周期进度≥80%", "二次回落确认", "成交量萎缩(量比<阈值)"],
    "threshold_n": 2,
    "threshold_m": 3
  },
  "consumes": [
    {"name": "调整周期进度", "source_layer": "L2C", "source_module": "MOD-xxx"},
    {"name": "行情生命周期阶段", "source_layer": "L2C", "source_ref": "草图§6.7"},
    {"name": "轮动序列", "source_layer": "L2B", "source_ref": "草图§6.1.3"},
    {"name": "量比", "source_layer": "L0"}
  ],
  "params": [
    {
      "name": "分批数",
      "default": 2,
      "range": "2-4",
      "current_code_value": 2,
      "status": "implemented",
      "code_location": "src/zephyr/.../batch_buy.py:L42"
    },
    {
      "name": "批次间隔",
      "default": "1交易日",
      "current_code_value": "1交易日",
      "status": "implemented",
      "code_location": "src/zephyr/.../batch_buy.py:L58"
    },
    {
      "name": "满足阈值",
      "default": "2/3",
      "status": "proposed",
      "proposed_by": "Owner",
      "proposed_date": "2026-08-01"
    }
  ],
  "data_flow": "进度+阶段+轮动→条件判定→L3.5仓位(分批方案)→L4执行(分批下单)",
  "code_mapping": {
    "primary_module": "MOD-L05-001",
    "file": "src/zephyr/.../batch_buy.py",
    "function": "evaluate_batch_buy_condition"
  },
  "degradation": "跌破前低→暂停后续批次→触发止损评估",
  "indicators_zh_ref": "翻译真源 battle_map_steps.BM-BUY-04.indicators_zh"
}
```

**字段说明**：
- `params[].status`：`implemented`（代码已实现，带 `current_code_value`+`code_location`）/ `proposed`（代码没有，人提议）/ `testing`（回测中）。这是代码↔地图双向反馈的核心。
- `consumes[]`：消费的数据/因子清单，带来源层和模块，可追溯到具体数据源。
- `code_mapping`：主实现模块 + 代码文件 + 函数，AI 能直接定位到代码。
- `indicators_zh_ref`：指向翻译真源的大段解释文案（机制说明、参数讨论、业务逻辑叙述）。

### 14.3 battle_map_anchors.target_graph 值域

| target_graph | target_id 含义 | 来源 |
|---|---|---|
| depgraph | module_id | depgraph.nodes |
| dataflowgraph | dataflow_node_id | dataflow_datasets/jobs |
| decisiongraph | decision_node_id | decision_nodes |
| candidate | candidate_id | candidate_module_registry.yaml entry id |
| blueprint | blueprint_section | docs/03_modules/ 章节锚点 |

---

## 十五、已定决策汇总 + 剩余开放问题

### 15.1 已定决策（V0.2 拍板）

| # | 问题 | 决策 |
|---|---|---|
| Q1 | 环节粒度 | 6 件套标准（§6.4），50-100 个环节，比草图 §1.2-1.6 更细 |
| Q2 | 双向查找实现 | anchors 单一真源 + 全景图模块加派生只读字段（§8.2） |
| Q3 | 旧 trading_flow_panorama.md 处置 | 删除重建，battle_map_positioning.md 替代 |
| Q4 | align_battle_map 门禁强度 | 先君子协定，跑顺再升级硬阻断 |
| Q5 | 表前缀 / 图名 | 图名 `battlemap`（对标 depgraph/dataflowgraph/decisiongraph），表前缀 `battle_map_*`（对标 `decision_*`），不用 `bm_*` 缩写 |
| Q6 | narrative.yaml 退场时机 | ✅ 已完成（2026-08-02 退役删除，4 横切段迁至 `module_translation_registry.yaml §battle_map_cross_cutting`） |

### 15.2 剩余开放问题（待 Owner 拍板或施工时定）

1. **第一批环节清单**：50-100 个环节具体是哪些？需从草图 v9.0 逐章挖掘（§1.1主流程 + §1.2-1.6注解 + §2-12层详解），按 6 件套标准登记。这是施工第一步，建议蓝图定稿后专门做一次"草图→环节清单"的挖掘评审。
2. **panorama_registry 登记**：battle_map 登记为 `PAN-BATTLE-MAP-01`，确认登记号。
3. **battlemap schema 归属**：三图各有 schema 文件（depgraph_schema.py / dataflowgraph_schema.py / decisiongraph_schema.py），新建 `battlemap_schema.py`，确认放 `src/zephyr/governance/persistence/` 下。
4. **indicators 6 件套的必填校验**：哪些件是必填（如 trigger/consumes/code_mapping），哪些可选（如 degradation）？影响 BM-INV 校验。

---

## 十七、运作机制速查总览（一页纸看懂）

> 本节是整篇文档的"导读速查版"——把前面 §一~§十五 的核心机制浓缩成一页纸，方便 Owner 快速确认机制设计是否正确，也方便 AI 写决策前快速定位"该查哪、该写哪"。详细设计见各对应章节，本节不重复展开。

### 17.1 五张全景图定位

battle_map 是项目第五全景图。前三图（depgraph/dataflowgraph/decisiongraph）是横向切片（按 module/decision/entity 轴），blueprint.md 是模块级蓝图（按 module_id 轴），作战地图是纵向贯穿（按业务流程 step 轴），它把前四图的节点按"选股→买入→卖出→仓位→执行→对账"6 阶段重新编排成端到端作战链条。

| 全景图 | 真源 | 关注轴 | 回答的问题 |
|---|---|---|---|
| 依赖全景图 depgraph | PostgreSQL `nodes`/`edges` | module_id | "谁连谁？模块依赖关系是什么？" |
| 数据流全景图 dataflowgraph | PostgreSQL `dataflow_*` | entity/job | "数据怎么流？谁消费谁产出？" |
| 决策流全景图 decisiongraph | PostgreSQL `decision_*` | decision_id | "决策怎么编排？谁触发谁？" |
| 模块蓝图 blueprint.md | 蓝图文件 frontmatter | module_id | "模块怎么设计？接口契约/施工指引是什么？" |
| **作战地图 battle_map** | PostgreSQL `battle_map_*` + YAML 叙事 | **step_id** | "业务作战环节怎么串？每环节靠哪些模块落地？" |

详见 §一、§九。

### 17.2 作战地图三表结构

定义在 `src/zephyr/governance/persistence/battlemap_schema.py`，三张表共享 depgraph 的 PostgreSQL 实例（同一 DB，不同表前缀 `battle_map_*`）：

| 表 | 角色 | 关键列 |
|---|---|---|
| `battle_map_steps` | 作战环节（11 列） | `step_id`(PK) / `flow_stage`(6 选 1) / `narrative_ref`(指向 YAML 叙事) / `indicators`(JSONB 6 件套) / `design_maturity`(design/production) |
| `battle_map_anchors` | 双向对齐锚点（7 列） | `step_id` ↔ `target_graph`(5 选 1) + `target_id` + `target_role`(primary/supplement/degradation) |
| `battle_map_edges` | 环节流转（6 列） | `from_step_id` → `to_step_id` + `edge_type`(data_flow/trigger/degradation) |

详见 §六。

### 17.3 与其他全景图/真源的对齐机制（核心）

对齐通过 `battle_map_anchors.target_graph` 字段实现——每个锚点声明"这个作战环节由哪个图的哪个节点承载"。

#### 17.3.1 五类 target_graph 对齐路径

| target_graph | target_id 含义 | 合法 id 采集来源（align_battle_map.py 校验） |
|---|---|---|
| `depgraph` | module_id | depgraph.nodes 的 blueprint_id ∪ path |
| `dataflowgraph` | entity_name / job_name / module_id | dataflow_datasets + dataflow_jobs |
| `decisiongraph` | decision_node_id | decision_nodes |
| `candidate` | candidate_id | candidate_module_registry.yaml entry id |
| `blueprint` | blueprint_section | docs/03_modules/ 下蓝图文件锚点 |

校验逻辑见 `scripts/governance/align_battle_map.py` 的 `_valid_ids_*()` 函数族。详见 §8.4、§14.3。

#### 17.3.2 与翻译真源的对齐（BM-INV-003）

作战地图同时有"结构数据"（在 DB）和"叙事数据"（在 YAML），分属两条 SSoT 流：

| 数据类型 | 真源 | 写入工具 |
|---|---|---|
| 架构数据（环节/锚点/边的结构） | PostgreSQL `battle_map_*` 三表 | `apply_battle_map.py` 直接写 DB |
| 规则数据①环节叙事（name_zh/plain_zh/mechanism_zh/indicators_zh） | `module_translation_registry.yaml` 的 `battle_map_steps` 段 | 手编 YAML，生成器只读 |
| 规则数据②域漂移规则（哪个阶段允许哪个域） | `battle_map_domain_policy.yaml` | 手编 YAML，对齐器只读 |

`battle_map_steps.narrative_ref` 字段是 **DB → YAML 的指针**：DB 只存 step_id，叙事内容去 YAML 取。生成器 `generate_battle_map_diagram.py` 读取 YAML 渲染文档，**禁止在代码里硬编码叙事**（BM-INV-003）。详见 §七。

#### 17.3.3 承重墙不变量（BM-INV-001~004/007）

定义在 `battlemap_schema.py` §四条承重墙不变量段，由 `align_battle_map.py` 检测，输出到 `docs/02_enterprise_architecture/03_governance_reports/battle_map_alignment_report.md`：

| 编号 | 检查项 | 含义 | 触发条件 |
|---|---|---|---|
| BM-INV-001 | 孤儿环节 | step 无任何 anchor = 悬空决策 = AI 凭记忆推断 = 幻觉风险 | `battle_map_steps` 在 `battle_map_anchors` 中无记录 |
| BM-INV-002 | 幽灵锚点 | anchor.target_id 在 target_graph 对应图/仓库找不到 | target_id 不在 depgraph/dataflowgraph/decisiongraph/candidate/blueprint 的合法 id 集合里 |
| BM-INV-003 | 缺失叙事 | DB 有 step 但 YAML `battle_map_steps` 段无对应叙事 | 生成器降级到 DB step_name，文档质量受损 |
| BM-INV-004 | 域漂移 | anchor 的 target module/candidate 的 domain 不在 step.flow_stage 允许列表 | 如把 `D_SELL_DECISION`（卖出域）挂在 `buy_flow`（买入阶段）环节上 |
| BM-INV-007 | 孤儿模块 | 业务域 depgraph 模块无任何 anchor 指向 = 造出来没用上 = 幻觉/浪费风险 | `nodes`（domain_id ∈ 业务域白名单）的 blueprint_id/path 不在 `battle_map_anchors`（target_graph=depgraph）的 target_id 集合里 |

> BM-INV-005（派生只读字段禁令，未落地/规划中）属于派生展示层约束，不在对齐检测系列，详见 §8.4。当前通过 anchors 反查，无派生缓存字段（2026-08-03 核实：depgraph.nodes 无 battle_map_step_ids 列）。

#### 17.3.4 域漂移检查规则（BM-INV-004 真源）

规则真源在 `docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`，定义每个 `flow_stage` 允许挂载的 `domain_id`：

| flow_stage | 允许的域（节选） | 禁止典型 |
|---|---|---|
| research_incubation（研究孵化） | D_RESEARCH / D_DATA / D_ML_TRAIN / D_KNOWLEDGE / D_INTELLIGENCE | D_EX_CORE / D_SELL_DECISION / D_POSITION / D_FRONTEND |
| model_training（模型训练） | D_ML_TRAIN / D_FACTOR / D_DATA / D_RESEARCH | D_EX_CORE / D_SELL_DECISION / D_POSITION / D_FRONTEND |
| backtest_validation（回测验证） | D_BACKTEST / D_DATA / D_FACTOR / D_SIMULATION / D_RISK / D_POSITION | D_EX_CORE / D_SELL_DECISION / D_FRONTEND |
| simulation_validation（仿真验证） | D_SIMULATION / D_BACKTEST / D_RISK / D_DIGITAL_TWIN | D_EX_CORE / D_SELL_DECISION / D_POSITION / D_FRONTEND |
| stock_selection（选股） | D_FACTOR / D_ASHARE_SIGNAL / D_FUNDAMENTAL_SIGNAL / D_SIGNAL / D_INTELLIGENCE / D_KNOWLEDGE / D_INTEGRATION / D_MKT_DATA / D_DATA / D_ML_SERVE / D_ML_TRAIN / D_ALT_DATA / D_CROSS_ASSET / D_INFRA_RUNTIME / D_SHARED / D_SIGQC | D_PF_CORE / D_PF_ALLOC / D_SELL_DECISION / D_EX_CORE / D_POSITION |
| buy_flow（买入） | D_PF_CORE / D_PF_ALLOC / D_TRADING / D_RISK / D_INTEGRATION / D_ORCHESTRATOR / D_INTELLIGENCE / D_COMPLIANCE | D_SELL_DECISION / D_FRONTEND / D_EX_CORE / D_POSITION |
| sell_flow（卖出） | D_SELL_DECISION / D_TRADING / D_RISK / D_POSITION | D_PF_CORE / D_FRONTEND |
| position_management（仓位） | D_POSITION / D_PF_CORE / D_PF_ALLOC / D_RISK | D_SELL_DECISION / D_EX_CORE / D_FRONTEND |
| risk_control（风控管控） | D_RISK / D_REPORTING / D_POSITION / D_TRADING | D_FACTOR / D_SIGNAL / D_FRONTEND / D_SELL_DECISION |
| execution（执行） | D_EX_CORE / D_EX_SOR / D_TRADING / D_RISK / D_REPORTING | D_FACTOR / D_SIGNAL / D_FRONTEND / D_SELL_DECISION |
| reconciliation（对账） | D_REPORTING / D_BACKTEST / D_SIMULATION / D_TRADING / D_FACTOR / D_FEEDBACK_LOOP | D_EX_CORE / D_SELL_DECISION / D_FRONTEND |

**当前已知漂移**（V1.0.0 严格模式启用后预期发现 7 个，severity=warn 君子协定，不硬阻断）：
- `buy_flow`: D_SELL_DECISION(1) + D_FRONTEND(1)
- `stock_selection`: D_PF_CORE(3) + D_PF_ALLOC(2)

> 严格模式依据：组合优化（D_PF_CORE/D_PF_ALLOC）不属于 stock_selection——选股是"挑哪些股票"，组合优化是"挑完之后怎么配仓位"，语义正交。详见 `battle_map_domain_policy.yaml` 顶部注释。

### 17.4 运作机制图（数据流全貌）

```
┌─────────────────────────────────────────────────────────────────┐
│  真源层（SSoT 分类，TRAE-062）                                     │
├──────────────────────────┬──────────────────────────────────────┤
│  规则数据真源（YAML）     │  架构数据真源（PostgreSQL）            │
│  ① module_translation_    │  ① depgraph.nodes/edges              │
│     registry.yaml         │  ② dataflowgraph.dataflow_*          │
│     §battle_map_steps     │  ③ decisiongraph.decision_*          │
│     (环节叙事)            │  ④ battle_map.battle_map_*  ← 第四   │
│  ② battle_map_domain_     │     (steps/anchors/edges)             │
│     policy.yaml           │                                      │
│     (域漂移规则)          │                                      │
└──────────┬───────────────┴──────────────┬───────────────────────┘
           │ 只读                        │ 只读
           ▼                            ▼
┌──────────────────────────────────────┐ ┌────────────────────────┐
│  apply_battle_map.py（写 DB 唯一入口）│ │ align_battle_map.py    │
│  - add/update/remove step/anchor/edge│ │ (只读检测器)            │
│  - pg_advisory_lock=424245           │ │ - BM-INV-001~004 五查   │
│  - 写架构数据，不动 YAML             │ │ - 输出对齐报告 MD       │
└──────────────────────────────────────┘ └────────────────────────┘
           │                                       │
           ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  generate_battle_map_diagram.py（生成器，只读）                   │
│  读 DB 三表 + YAML 叙事 → 渲染 MD + 可缩放 HTML                   │
│  产物：07_trading_decision_architecture/battle_map/*.md          │
│       + _zoomable_html/*.html                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 17.5 写入流程决策表（改东西时该走哪条路）

按 SSoT 分类铁律（TRAE-062），**先问"规则数据还是架构数据"**：

| 想改的内容 | 数据类型 | 走哪条路 |
|---|---|---|
| 环节叙事（name_zh/plain_zh/mechanism_zh/indicators_zh） | 规则数据 | 改 `module_translation_registry.yaml` → 生成器读取 |
| 域策略（某阶段允许新域） | 规则数据 | 改 `battle_map_domain_policy.yaml` → 对齐器读取 |
| 新增/修改/删除环节、锚点、边 | 架构数据 | `apply_battle_map.py` 写 DB |
| indicators 结构化字段（trigger/consumes/params/code_mapping/degradation） | 架构数据 | `apply_battle_map.py --update-step` 写 DB |
| depgraph/dataflowgraph/decisiongraph 的节点 | 架构数据 | 各自的 `apply_*.py` 写 DB |

**禁止反向操作**：DB → YAML（如把 DB 的 step 同步回 YAML 叙事）是违规的。详见 §七 SSoT 铁律。

### 17.6 与前三图对齐的正交关系

`align_battle_map.py` 顶部明确：与 `align_panoramas.py` 正交，互不干扰。

| 对齐工具 | 轴 | 回答 | 用途 |
|---|---|---|---|
| `align_panoramas.py` | module_id | 一个模块在 4 张图里一致吗 | 建模块时 |
| `align_battle_map.py` | step_id | 一个环节都落地了吗、落在哪 | 写决策时 |

二者通过 `battle_map_anchors.target_id` 间接耦合——作战地图锚点指向的模块，必须在前三图里真实存在（BM-INV-002）。详见 §9.2。

---

## 十六、变更历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V0.8.0 | 2026-08-07 | acquisition 徽标 + 五态展示修正：①§十 标题"四态"→"五态"（表格已列 5 态但标题漏改）；②§十一 "四类 classDef"→"五类 classDef" + 新增 acquisition 徽标条目（设计态环节节点卡成熟度行下方显示 `（🔴自建）`/`（🟢开源）`/`（🟡借鉴）`/`（⬜弃用）`，模板 §4.13）；③L207 "三态"→"五态"；④同步 `visualization_view_template.md` V1.6（§4.13 acquisition 徽标章节 + §7.5 数据真源 + §4.7 五态 classDef 扩展）；⑤acquisition 字段分层 SSoT：设计态 depgraph `nodes_metadata.acquisition_method/source`（DDL CHECK）+ 候选态 `candidate_module_registry.yaml`（草稿层），107 决策表全量导入。 |
| V0.7.0 | 2026-08-04 | 新增 BM-INV-007 孤儿模块反向检测：①§8.4 不变量列表加 BM-INV-007（业务域 depgraph 模块无任何锚点指向=造出来没用上）；②`align_battle_map.py` 加 `_business_domain_whitelist()`（业务域白名单=所有 flow_stage 的 allowed 域并集，运行时从 YAML 取，零硬编码）+ `_business_modules_depgraph()`（采集业务域节点）+ 已锚定集合反查（target_graph=depgraph 的 target_id，blueprint_id/path 宽松匹配）；③报告加第 7 节孤儿模块 + 业务域模块统计行 + 处置建议顺移第 8 节；④§17.3.3 表加 BM-INV-007 行；⑤AGENTS.md/battlemap_schema.py 同步。这是 BM-INV-001 的对偶——001 查"功能没模块"，007 查"模块没功能"。君子协定 warn-only，不硬阻断。非业务域（D_GOVERNANCE/D_GOV_SCRIPTS/D_GOV_RULE/D_FRONTEND 等）天然排除。 |
| V0.6.0 | 2026-08-03 | 四层嵌套上限放开：①§6.1 `depth` 字段上限从2→3（根→子→孙→曾孙）；②§8.4 BM-INV-006 `depth≤2`→`depth≤3`；③§6.1.1 新增 step_id 四层命名约定表（根-子字母-孙数字-曾孙小写字母）；④`align_battle_map.py` L763 depth上限 2→3 + 文案；⑤`apply_battle_map.py` op_add_step 加 depth≤3 写入校验（前置防线）；⑥生成器递归函数无需改（已支持任意深度）。全自动化：写入时设 parent_step_id+depth → 生成器自动渲染嵌套 subgraph。 |
| V0.5.1 | 2026-08-03 | BM-INV-005 降级为未落地规划（方案B）：①核实 depgraph.nodes 无 `battle_map_step_ids` 列（information_schema 0 列）、apply_battle_map.py 无 sync、align_battle_map.py 不检测、无 trigger——原"派生只读缓存"机制四要素全缺；②删除 battlemap_schema.py 注释虚假描述"apply_battle_map.py 单向 sync：anchors→各图字段"（代码无此逻辑）；③§8.4 BM-INV-005 标注"未落地/规划中"，当前通过 `battle_map_anchors` 反查（target_graph=depgraph+target_id=blueprint_id，idx_battle_map_anchors_target 索引）；④AGENTS.md 同步：七类问题→六类问题（align 实检 001/002/003/004/006+悬空边），BM-INV-005 单列标注未落地。治本依据：反查路径已通（抽样5模块各7锚点），派生缓存冗余违反 SSoT+向内收。 |
| V0.5.0 | 2026-08-03 | 全生命周期扩展 +5 新阶段：①§3.6 阶段对应表从 6→11 阶段（+研究孵化/模型训练/回测验证/仿真验证/风控管控），按生命周期重排（研究→训练→回测→仿真→选股→买入→卖出→仓位→风控→执行→对账）；②§6.1 `flow_stage` 字段合法值扩展至 11 阶段；③§17.3.4 域策略表补入 5 新阶段的允许域/禁止域（与 `battle_map_domain_policy.yaml` V1.0.0 对齐）；④`battle_map_domain_policy.yaml` 同步补入 5 新阶段 `flow_stage_allowed_domains`；⑤`module_translation_registry.yaml` §battle_map_steps 补入 33 条新阶段环节叙事 + 44 条子环节叙事（含 BM-SEL-22~25 短线选股/游资接力/量化强度/双引擎融合子环节）；⑥生成器重新生成 12 阶段文档 + panorama 总图；⑦对齐报告 0 问题（steps=152/anchors=214/edges=114/叙事真源=152）。 |
| V0.4.0 | 2026-08-03 | 父子嵌套机制落地：①§6.1 `battle_map_steps` 表新增 `parent_step_id`（FK 自引用）+ `depth`（层级深度，上限2）两字段；②§8.4 新增 BM-INV-006 不变量（父存在+同阶段+无环+depth≤2+depth一致），写入校验在 `apply_battle_map.py` op_add_step，对齐检测在 `align_battle_map.py` `_check_parent_child_consistency()`；③生成器 `generate_battle_map_diagram.py` 支持 subgraph 渲染父子嵌套 + `-.->｜嵌套｜` 虚线边 + 子环节状态继承父环节 + 【】节点格式（⛔最前/成熟度最后/英文名最后）；④首批拆子落地：BM-BUY-02 四轨融合→4子环节（A逻辑驱动/B数据驱动/C人工指令/D应急保命）；⑤可视化模板 `visualization_view_template.md` V1.5 同步更新（§4.3 作战地图节点格式 + §4.12 父子嵌套关系） |
| V0.3.2 | 2026-08-03 | 新增 §十七「运作机制速查总览（一页纸看懂）」：把 §一~§十五 的核心机制浓缩成导读速查版，含①全景定位速查表②三表结构简表③五类 target_graph 对齐路径详表④四条承重墙不变量 BM-INV-001~004⑤域漂移规则与当前已知 7 漂移点⑥运作机制数据流 ASCII 图⑦写入流程决策表⑧与 align_panoramas 正交关系。补充文档此前分散/缺失的"一页纸总览"视角，方便 Owner 快速确认机制与 AI 写决策前定位。重复部分以"详见 §X"引用，不破坏现有设计章节。 |
| V0.1.0 | 2026-08-01 | 草案：第五全景图 battle_map 设计。三表数据模型 + 翻译真源 battle_map_steps 段 + 双向查找机制 + 取代 trading_flow_panorama.md V1.0.0。 |
| V0.3.1 | 2026-08-03 | BM-INV-004 域漂移检查实现落地：①新增规则真源 `battle_map_domain_policy.yaml`（flow_stage→允许 domain 列表，TRAE-062 规则数据真源=YAML）；②`align_battle_map.py` 新增 §5 域漂移检测（采集 depgraph/candidate 的 target domain，逐锚点校验是否在 flow_stage 允许列表）；③对齐报告新增域漂移段+处置建议。首跑发现 8 处漂移（含误报：MOD-INF-002 跨域巨型蓝图单一 domain_id 采集器局限，待采集器修复）。④不变量编号调整：原 BM-INV-004（派生只读字段禁令）renumber 为 BM-INV-005，BM-INV-004 归位为域漂移（与 001孤儿/002幽灵/003叙事同属 align_battle_map.py 对齐检查系列）。 |
| V0.3.0 | 2026-08-02 | 缺口2补完：①新增§三系统架构上下文（草图§1.1/§1.8摘要，L0-L6分层+数据流主动脉+闭环反馈+工厂三兄弟+作战地图对应关系）；②横切视图扩展§15计算节奏与时序+§1.7分布感知增强体系（翻译真源+生成器渲染函数）；③16个选股孤儿环节挂载candidate锚点；④13个非HARVEST候选池模块挂载到对应环节；⑤BM-SEL-01参数code_location反向回填。对齐报告0问题。 |
| V0.2.0 | 2026-08-01 | Owner 评审反馈落地：① 环节粒度升级为 6 件套标准（§6.4），50-100 个环节，indicators JSONB 扩展为 6 件套 + 双向参数（implemented/proposed/testing）；② 图名定为 battlemap，表前缀 battle_map_*（对标 decision_*）；③ 旧文档处置定为删除重建；④ narrative.yaml 退场定为并行观察；⑤ 双向查找确认 anchors 单真源 + 派生只读字段方案；⑥ 门禁君子协定。 |
