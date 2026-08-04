---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.0.0"
date: 2026-08-04
---

# 作战地图·模型训练阶段

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/_zoomable_html/battle_map_02_model_training.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> battle_map §model_training 阶段，9 环节（9 锚点）。
> 🔑 锚点表 `battle_map_anchors` 是环节↔模块**双向对齐枢纽**（step↔module 唯一查找真源），详见各环节「锚点」小节。
> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。

## 文档基本信息 / Document Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 阶段 | 模型训练（model_training） | Stage | 模型训练 |
| 环节数 | 9 | Steps | 9 |
| 锚点数（双向对齐） | 9 | Anchors (Bidirectional) | 9 |
| 流转边 | 6 | Edges | 6 |
| 状态分布 | 🟨 候选态（候选池）=5 ｜ 🟧 设计态（待施工）=2 ｜ 🟦 运营态（已建）=1 ｜ ⬜ 缺失态（无锚点）=1 | State Distribution | 🟨 候选态（候选池）=5 ｜ 🟧 设计态（待施工）=2 ｜ 🟦 运营态（已建）=1 ｜ ⬜ 缺失态（无锚点）=1 |

> **图例说明 / Legend**：
> - 🟦 **蓝色实线 = 运营态环节**（production，锚点模块已建）
> - 🟧 **橙色虚线 = 设计态环节**（design，锚点模块待施工）
> - 🟧**设计态子环节** = 父环节已建但此子环节待施工（特殊标记，易被忽略）
> - 🟥 **红色 = 弃用态**（deprecated）
> - ⬜ **灰色 = 缺失态**（missing，环节无锚点，BM-INV-001 违例）
> - 🟨 **黄色虚线 = 候选态**（candidate，承载模块在候选池）
> - **实线箭头 ``-->`` = 运营态流转**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态流转**（含设计/候选/混合）

## 阶段图 / Stage Diagram

> 展示 模型训练 阶段全部 9 个环节及流转边，颜色区分五态。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
%% 模型训练阶段图
flowchart TD
    subgraph sg_BM_MT_01 ["训练流水线"]
        BM_MT_01["⛔ ML训练域，设计已就绪，等待开发排期<br/>【BM-MT-01 训练流水线】<br/>把研究出的因子和特征喂给模型训练，PyTorch<br/>训完导出 ONNX，全程管 seed 和 config<br/>保证可复现。<br/>（设计态 / design）<br/>🟡候选承载<br/>【Training Pipeline】"]
        BM_MT_01_A["【BM-MT-01-A 训练基座<br/>（训练器ABC+模型注册表+元数据）】<br/>训练域的基座抽象——ModelTrainerBase<br/>训练器接口、ModelRegistry<br/>模型版本注册表、ModelMetadata 元数据，是 MT-01<br/>训练流水线的地基。<br/>（生产态 / production）<br/>【Training Base （Trainer ABC + Model Registry +<br/>Metadata）】"]
        BM_MT_01_B["⛔ ML训练域，设计已就绪，等待开发排期<br/>【BM-MT-01-B AI辅助代码生成与分析师Agent反馈】<br/>LLM 生成模块代码，Critic Agent<br/>审漏洞，多轮反馈收敛后过 AST<br/>沙箱——把人力调参瓶颈用 AI 填上。<br/>（设计态 / design）<br/>🟧设计态子环节<br/>【AI-Assisted Code Generation &amp; Analyst Agent<br/>Feedback】"]
        BM_MT_01 -.->|嵌套| BM_MT_01_A
        BM_MT_01 -.->|嵌套| BM_MT_01_B
    end
    BM_MT_02["【BM-MT-02 实验追踪与自动晋升】<br/>A/B 实验对比新模型和老模型，统计上显著更好才自动<br/>晋升为 Champion，否则留在 Challenger 继续观察。<br/>（候选态 / candidate）<br/>🟡候选承载<br/>【Experiment Tracking &amp; Auto-Promotion】"]
    BM_MT_03["【BM-MT-03 AutoML与超参优化】<br/>不靠人手调参——贝叶斯优化自动找最佳超参，早停省时<br/>间，还能自动挖因子。<br/>（候选态 / candidate）<br/>🟡候选承载<br/>【AutoML &amp; Hyperparameter Optimization】"]
    BM_MT_04["【BM-MT-04 因子发现与因果发现】<br/>不只找相关性强的因子，还要找因果关系——用 PC/GES<br/>/LiNGAM 算因果图，避免'假相关'误导。<br/>（候选态 / candidate）<br/>🟡候选承载<br/>【Factor Discovery &amp; Causal Discovery】"]
    subgraph sg_BM_MT_05 ["漂移检测与自适应重训练"]
        BM_MT_05["【BM-MT-05 漂移检测与自适应重训练】<br/>市场变了模型就老了——实时检测概念漂移，触发重训练<br/>，元学习让新模型快速适应不忘旧。<br/>（候选态 / candidate）<br/>🟡候选承载<br/>【Drift Detection &amp; Adaptive Retraining】"]
        BM_MT_05_A["【BM-MT-05-A 持续学习防遗忘（EWC+伪回放）】<br/>模型学新市场时不忘旧——Fisher信息矩阵正则化关键参<br/>数，让新模型快速适应新分布又不丢历史知识。<br/>（候选态 / candidate）<br/>🟡候选承载<br/>【Continual Learning Anti-Forgetting （EWC +<br/>Pseudo-Replay）】"]
        BM_MT_05 -.->|嵌套| BM_MT_05_A
    end
    BM_MT_06["【BM-MT-06 元学习与自我进化】<br/>—<br/>（缺失态 / missing）<br/>⚠无锚点"]
    BM_MT_01 ~~~ BM_MT_01_A ~~~ BM_MT_01_B ~~~ BM_MT_05_A ~~~ BM_MT_06
    BM_MT_01 -.->|训练→实验晋升 / data_flow| BM_MT_02
    BM_MT_02 -.->|晋升→AutoML优化 / trigger| BM_MT_03
    BM_MT_03 -.->|AutoML→因子发现 / data_flow| BM_MT_04
    BM_MT_04 -.->|因子→漂移检测 / trigger| BM_MT_05
classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
classDef deprecated fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
classDef missing fill:#eeeeee,stroke:#9e9e9e,stroke-width:2px,color:#000
classDef candidate fill:#fffde7,stroke:#f9a825,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    class BM_MT_01_A production
    class BM_MT_01,BM_MT_01_B design
    class BM_MT_06 missing
    class BM_MT_02,BM_MT_03,BM_MT_04,BM_MT_05,BM_MT_05_A candidate
```

## 环节详情

### BM-MT-01 训练流水线 / Training Pipeline

> **大白话**：把研究出的因子和特征喂给模型训练，PyTorch 训完导出 ONNX，全程管 seed 和 config 保证可复现。

**机制说明**：

MT-01 TrainingPipeline 负责模型训练+验证+可复现性（PyTorch→ONNX导出、seed管理、config快照、
进化式代码生成 S4 DSL+AST沙箱、分析师Agent反馈循环）。是 D-ML-TRAIN 域的核心入口，
盘后 20:00-23:59 模型重训练的核心承载。产出 ModelTrained 事件喂 D-ML-SERVE 推理域。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘后定时/研究员手动/漂移触发(BM-MT-05) |
| ② 消费数据/因子 | BM-RES-01 特征存储(PIT)+BM-RES-02 实验追踪 |
| ③ 参数 | PyTorch→ONNX、seed管理、config快照、S4 DSL代码生成、AST沙箱 |
| ④ 数据流 | 特征(PIT)→训练→验证→ONNX模型→BM-MT-02晋升→D-ML-SERVE |
| ⑤ 代码映射 | MT-01 TrainingPipeline（stable, 已有ABC） |
| ⑥ 降级/中止 | 训练失败→回退上一版模型+告警(不阻塞推理) |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘后定时/研究员手动/漂移触发(BM-MT-05)；②消费：BM-RES-01 特征存储(PIT)+BM-RES-02 实验追踪；③参数：PyTorch→ONNX、seed管理、config快照、S4 DSL代码生成、AST沙箱；④数据流：特征(PIT)→训练→验证→ONNX模型→BM-MT-02晋升→D-ML-SERVE；⑤代码：MT-01 TrainingPipeline（stable, 已有ABC）；⑥降级：训练失败→回退上一版模型+告警(不阻塞推理)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-ML-001 | primary | planned | planned |
| candidate | CAND-HARVEST-0728 | supplement | planned | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-01-A 训练基座（训练器ABC+模型注册表+元数据） / Training Base (Trainer ABC + Model Registry + Metadata)

> **大白话**：训练域的基座抽象——ModelTrainerBase 训练器接口、ModelRegistry 模型版本注册表、ModelMetadata 元数据，是 MT-01 训练流水线的地基。

**机制说明**：

MOD-L11-001 提供 D_ML_TRAIN 域核心抽象基座：ModelTrainerBase（train/validate/save_model ABC）、ModelRegistry（register/get/clear + lineage 管理）、ModelMetadata（model_id/version/framework/features/metrics）。是 MOD-ML-001 TrainingPipeline 的构建基础，已有生产代码。

**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | MT-01 训练流水线启动时加载基座 |
| ② 消费数据/因子 | 训练数据+因子特征 |
| ③ 参数 | model_id=—（范围 —，代码当前: —，状态: proposed）<br>framework=—（范围 —，代码当前: —，状态: proposed）<br>features=—（范围 —，代码当前: —，状态: proposed）<br>target=—（范围 —，代码当前: —，状态: proposed）<br>seed管理=—（范围 —，代码当前: —，状态: proposed）<br>模型版本号=—（范围 —，代码当前: —，状态: proposed） |
| ④ 数据流 | 输入: 训练数据+因子特征 → 处理: ModelTrainerBase.train()/validate() → 输出: ModelMetadata+训练指标 → 下游: ModelRegistry.register()→MOD-MT-02 |
| ⑤ 代码映射 | MOD-L11-001 / src/zephyr/ml_train/trainer_base.py |
| ⑥ 降级/中止 | 基座缺失 → 无法训练（硬依赖） |

**指标文案（翻译真源 indicators_zh）**：

①触发：MT-01 训练流水线启动时加载；②消费：训练数据+因子特征；③参数：model_id/framework/features/target、seed管理、模型版本号；④数据流：训练数据→ModelTrainerBase.train()→ModelMetadata→ModelRegistry.register()→MOD-ML-001流水线；⑤代码：MOD-L11-001 trainer_base.py（production, 已有ABC+ModelRegistry）；⑥降级：基座缺失→无法训练（硬依赖）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L11-001 | primary | production | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-01-B AI辅助代码生成与分析师Agent反馈 / AI-Assisted Code Generation & Analyst Agent Feedback

> **大白话**：LLM 生成模块代码，Critic Agent 审漏洞，多轮反馈收敛后过 AST 沙箱——把人力调参瓶颈用 AI 填上。

**机制说明**：

MOD-ML-002 ai_operator 对应设计文档§9.2：Generator(GLM-5.1)生成代码→Critic(DeepSeek V4 Pro)审查→反馈循环→Judge(Claude)综合评估→AST沙箱三层安全→人工审核。含因子DSL约束（6类算子）、三重语义一致性、进化式代码生成、轨迹级进化。是 MT-01 的智能代码生成侧。

**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | BM-MT-01 训练前/研究员配置新模块需求 |
| ② 消费数据/因子 | ModuleRequirementSpec+交易流水线架构文档 |
| ③ 参数 | Generator/Critic/Judge模型=—（范围 —，代码当前: —，状态: proposed）<br>AST沙箱白名单+复杂度+语义三层=—（范围 —，代码当前: —，状态: proposed）<br>DSL 6类算子=—（范围 —，代码当前: —，状态: proposed）<br>进化轮数上限5=—（范围 —，代码当前: —，状态: proposed） |
| ④ 数据流 | 输入: ModuleRequirementSpec → 处理: LLM生成→Critic审查→反馈收敛→AST沙箱 → 输出: 模块代码+测试+配置 → 下游: 人工审核→注册Module Registry |
| ⑤ 代码映射 | MOD-ML-002 / src/zephyr/ml_train/ai_operator/ |
| ⑥ 降级/中止 | AI生成未就绪 → 人工编写代码（效率低） |

**指标文案（翻译真源 indicators_zh）**：

①触发：BM-MT-01 训练前/研究员配置新模块需求；②消费：ModuleRequirementSpec+交易流水线架构文档；③参数：Generator/Critic/Judge模型、AST沙箱白名单+复杂度+语义三层、DSL 6类算子、进化轮数上限5；④数据流：需求→LLM生成→Critic审查→反馈收敛→AST沙箱→人工审核→注册Module Registry；⑤代码：MOD-ML-002 ai_operator（planned）；⑥降级：AI生成未就绪→人工编写代码（效率低）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-ML-002 | primary | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-02 实验追踪与自动晋升 / Experiment Tracking & Auto-Promotion

> **大白话**：A/B 实验对比新模型和老模型，统计上显著更好才自动晋升为 Champion，否则留在 Challenger 继续观察。

**机制说明**：

MT-02 ExperimentTracker 提供 A/B实验+Champion-Challenger+统计验证+自动晋升（wandb集成、实验血缘追踪、
DSR/CPCV v2/White's Reality/Probabilistic BT）。是模型上线的"裁判"，防止过拟合模型混入生产。
与 D-ML-SERVE INV-011 影子验证联动——晋升前必须影子验证通过。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | BM-MT-01 训练完成 |
| ② 消费数据/因子 | 新模型+现役Champion模型+回测指标 |
| ③ 参数 | A/B实验、Champion-Challenger、DSR/CPCV v2/White's Reality/Probabilistic BT、统计显著性阈值 |
| ④ 数据流 | 新模型→A/B对比→统计验证→晋升/留观→D-ML-SERVE影子验证 |
| ⑤ 代码映射 | MT-02 ExperimentTracker（stable, 已有） |
| ⑥ 降级/中止 | 统计验证未就绪→人工review决定晋升(无自动门禁) |

**指标文案（翻译真源 indicators_zh）**：

①触发：BM-MT-01 训练完成；②消费：新模型+现役Champion模型+回测指标；③参数：A/B实验、Champion-Challenger、DSR/CPCV v2/White's Reality/Probabilistic BT、统计显著性阈值；④数据流：新模型→A/B对比→统计验证→晋升/留观→D-ML-SERVE影子验证；⑤代码：MT-02 ExperimentTracker（stable, 已有）；⑥降级：统计验证未就绪→人工review决定晋升(无自动门禁)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0729 | primary | planned | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-03 AutoML与超参优化 / AutoML & Hyperparameter Optimization

> **大白话**：不靠人手调参——贝叶斯优化自动找最佳超参，早停省时间，还能自动挖因子。

**机制说明**：

MT-03 AutoMLEngine 提供自动模型选择+超参优化+因子挖掘（Optuna贝叶斯优化、早停、Qlib因子挖掘、
辩论式因子精炼 FactorMAD、质量-多样性优化 QuantEvolve）。是研究孵化的"加速器"，
把人力调参的瓶颈用算力填上。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | BM-MT-01 训练前/研究员配置 |
| ② 消费数据/因子 | BM-RES-01 特征+搜索空间定义 |
| ③ 参数 | Optuna贝叶斯优化、早停、Qlib因子挖掘、FactorMAD辩论精炼、QuantEvolve质量-多样性 |
| ④ 数据流 | 搜索空间→贝叶斯优化→试验→早停→最佳超参→BM-MT-01训练 |
| ⑤ 代码映射 | MT-03 AutoMLEngine（planned） |
| ⑥ 降级/中止 | AutoML未就绪→人工网格搜索(效率低) |

**指标文案（翻译真源 indicators_zh）**：

①触发：BM-MT-01 训练前/研究员配置；②消费：BM-RES-01 特征+搜索空间定义；③参数：Optuna贝叶斯优化、早停、Qlib因子挖掘、FactorMAD辩论精炼、QuantEvolve质量-多样性；④数据流：搜索空间→贝叶斯优化→试验→早停→最佳超参→BM-MT-01训练；⑤代码：MT-03 AutoMLEngine（planned）；⑥降级：AutoML未就绪→人工网格搜索(效率低)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0730 | primary | planned | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-04 因子发现与因果发现 / Factor Discovery & Causal Discovery

> **大白话**：不只找相关性强的因子，还要找因果关系——用 PC/GES/LiNGAM 算因果图，避免"假相关"误导。

**机制说明**：

MT-04 FeatureDiscovery 提供因子发现+因果发现+特征工程（PC/GES/LiNGAM因果发现、AutoML因子挖掘、
特征交叉、辩论式因子精炼、三重语义一致性）。产出 NewFactorDiscovered 事件喂 D-FACTOR 因子域入池。
是"因子工厂"的智能上游，区别于纯统计因子挖掘。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | BM-MT-01 训练中/研究员触发 |
| ② 消费数据/因子 | BM-RES-01 特征+BM-RES-03 假设 |
| ③ 参数 | PC/GES/LiNGAM因果发现、特征交叉、FactorMAD辩论精炼、三重语义一致性 |
| ④ 数据流 | 特征→因果发现→新因子→语义一致性校验→D-FACTOR入池 |
| ⑤ 代码映射 | MT-04 FeatureDiscovery（planned） |
| ⑥ 降级/中止 | 因果发现未就绪→纯统计因子挖掘(无因果保证) |

**指标文案（翻译真源 indicators_zh）**：

①触发：BM-MT-01 训练中/研究员触发；②消费：BM-RES-01 特征+BM-RES-03 假设；③参数：PC/GES/LiNGAM因果发现、特征交叉、FactorMAD辩论精炼、三重语义一致性；④数据流：特征→因果发现→新因子→语义一致性校验→D-FACTOR入池；⑤代码：MT-04 FeatureDiscovery（planned）；⑥降级：因果发现未就绪→纯统计因子挖掘(无因果保证)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0731 | primary | planned | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-05 漂移检测与自适应重训练 / Drift Detection & Adaptive Retraining

> **大白话**：市场变了模型就老了——实时检测概念漂移，触发重训练，元学习让新模型快速适应不忘旧。

**机制说明**：

MT-05 DriftAdapter 提供概念漂移检测+自适应重训练+元学习（DDM/EDDM/ADWIN检测、MAML快速适应、
在线EWC防遗忘、技能库 Voyager、元反思、AutoSkill）。是模型"保鲜"的关键，
防止"上线时好用，三个月后失效"。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘中漂移检测信号/定时 |
| ② 消费数据/因子 | 实时预测误差+特征分布 |
| ③ 参数 | DDM/EDDM/ADWIN检测阈值、MAML快速适应、在线EWC防遗忘、Voyager技能库 |
| ④ 数据流 | 预测误差→漂移检测→重训练触发→MAML适应→EWC防遗忘→BM-MT-01训练 |
| ⑤ 代码映射 | MT-05 DriftAdapter（planned） |
| ⑥ 降级/中止 | 漂移检测未就绪→定时重训练(无自适应) |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘中漂移检测信号/定时；②消费：实时预测误差+特征分布；③参数：DDM/EDDM/ADWIN检测阈值、MAML快速适应、在线EWC防遗忘、Voyager技能库；④数据流：预测误差→漂移检测→重训练触发→MAML适应→EWC防遗忘→BM-MT-01训练；⑤代码：MT-05 DriftAdapter（planned）；⑥降级：漂移检测未就绪→定时重训练(无自适应)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0732 | primary | planned | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-05-A 持续学习防遗忘（EWC+伪回放） / Continual Learning Anti-Forgetting (EWC + Pseudo-Replay)

> **大白话**：模型学新市场时不忘旧——Fisher信息矩阵正则化关键参数，让新模型快速适应新分布又不丢历史知识。

**机制说明**：

CAND-HARVEST-0922 对应设计文档§10.1 维度7：在线EWC防遗忘（ProAdapt 2026）+伪回放。Fisher信息矩阵计算每个参数对历史任务的重要性，更新时对重要参数施加正则化约束，保留历史知识+适应新知识。是 MT-05 DriftAdapter 的防遗忘子能力，EWC正则化强度由Meta-Harness动态调整。

**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | BM-MT-05 漂移检测触发重训练时 |
| ② 消费数据/因子 | 历史任务参数Fisher信息+新训练数据 |
| ③ 参数 | EWC正则化强度=—（范围 —，代码当前: —，状态: proposed）<br>Fisher信息计算方法=—（范围 —，代码当前: —，状态: proposed）<br>伪回放样本数=—（范围 —，代码当前: —，状态: proposed） |
| ④ 数据流 | 输入: 重训练请求+历史Fisher信息 → 处理: Fisher信息计算→重要参数正则化 → 输出: 适应新分布且不遗忘旧的模型 → 下游: BM-MT-01训练 |
| ⑤ 代码映射 | CAND-HARVEST-0922 / candidate_module_registry.yaml §CAND-HARVEST-0922 |
| ⑥ 降级/中止 | EWC未就绪 → 全量重训练（有灾难性遗忘风险） |

**指标文案（翻译真源 indicators_zh）**：

①触发：BM-MT-05 漂移检测触发重训练时；②消费：历史任务参数Fisher信息+新训练数据；③参数：EWC正则化强度、Fisher信息计算方法、伪回放样本数；④数据流：重训练→Fisher信息计算→重要参数正则化→新模型适应新分布且不遗忘旧→BM-MT-01训练；⑤代码：CAND-HARVEST-0922 Continual Learning Anti-Forgetting（candidate, 待评估）；⑥降级：EWC未就绪→全量重训练（有灾难性遗忘风险）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0922 | primary | planned | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：production ｜ **层**：L11 ｜ **阶段**：model_training

### BM-MT-06 元学习与自我进化



**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | BM-MT-04 因子发现产出新策略 / BM-MT-05 漂移重训触发后，需跨任务积累经验加速学习 |
| ② 消费数据/因子 | 历史训练轨迹 + 策略表现 + BM-MT-02 实验追踪数据 + 技能库 |
| ③ 参数 | RSI架构4维度(技能/记忆/推理/迁移) + 技能库 + 在线EWC(Elastic Weight Consolidation) + 轻量Agent化 + 学习效果反馈闭环 |
| ④ 数据流 | 训练轨迹→技能抽象→技能库积累→新任务迁移加速→反馈闭环优化元学习策略 |
| ⑤ 代码映射 | 待开发（planned，D_ML_TRAIN 域） |
| ⑥ 降级/中止 | 元学习失效→回退 BM-MT-01 标准训练流水线（按任务独立训练） |

**锚点**：⚠ 无（BM-INV-001 君子协定违例——环节无锚点=悬空决策）

**有效状态**：⬜ 缺失态（无锚点） ｜ **环节自报**：design ｜ **层**：L11 ｜ **阶段**：model_training


[← 返回总指挥图](battle_map_panorama.md)