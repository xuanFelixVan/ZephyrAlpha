---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L26: （讲人话）、简洁性（防过拟合）——与本项目已建件**一一对应**：E5 协同去重=原创性正则、
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L7: > 2026-09-14 策略工厂后端施工班（st-facbe-20260914）起草，待 Owner 批复。
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 1、路径漂移 0）+ commit 提及 0 处。
> **判废弃引用（C-1）**：`docs/_working/2026-09-1X-agentic-mining-p0-notes.md`
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）





# 车道C 二轨立项申请书：LLM 智能体挖矿轨（原"AlphaGen 立项"重新划界 v1）

> 2026-09-14 策略工厂后端施工班（st-facbe-20260914）起草，待 Owner 批复。
> 性质：**立项申请书**（批准后才进施工闭环）；本稿本身即交付物。

## 一、为什么重新划界（全网检索结论，2026-09-14）

原设计稿 §二 把二轨锚定在 AlphaGen（RL 拼公式，KDD 2023）。2026-09 检索实证：该赛道已
两代更迭，纯 RL 路线已成"上一代"：

| 代际 | 代表 | 机制 | 状态 |
|---|---|---|---|
| 一代 2023 | AlphaGen | RL 逐因子生成 | 已过时（固定权重组合是其公认短板） |
| 二代 2024 | AlphaForge（AAAI 2025） | 生成式-预测式网络+**动态组合** | 基线参照 |
| 三代 2025-26 | **AlphaAgent**（KDD，arXiv 2502.16789）/ AlphaMuse（AAAI 2026，LLM+MCTS）/ Chain-of-Alpha（arXiv 2508.06312）/ AlphaAgentEvo | LLM 智能体+搜索/自进化+**抗衰减正则** | 当前前沿 |

来源：AlphaAgent arxiv.org/abs/2502.16789；AlphaMuse ojs.aaai.org/index.php/AAAI/article/view/37069
（arXiv 2505.11122）；Chain-of-Alpha arXiv 2508.06312；FAFM 基准 openreview.net/pdf?id=d97Q8r7ZKZ；
综述 FITEE jzus.zju.edu.cn（doi 10.1631/FITEE.2500386）；清单 github.com/Sasha-Cui/Awesome-Applied-Agents-for-Investment。

**关键发现（本项目的机会窗口）**：AlphaAgent 的三大正则——原创性（防重复挖）、经济逻辑
（讲人话）、简洁性（防过拟合）——与本项目已建件**一一对应**：E5 协同去重=原创性正则、
E2 假说预审=经济逻辑正则、init_depth+parsimony=简洁性正则。**业界的"正则化智体挖矿"
在我们厂里就是"智体产货+现有质检厂"**。二轨的正确姿势不是搬一台 AlphaGen 发动机，
而是给现有质检厂接一个 LLM 智能体产货口。

## 二、立项范围（批准后施工）

- **P0（半天）**：精读 AlphaAgent/AlphaMuse 论文+跑通其开源码（若在库），产出对照笔记；
- **P1（一个夜班）**：MVP 接线——LLM 产货口复用车道 B 管线形态（MOD-BT-150 模式）：
  主题种子→假说/公式生成（经 LSG）→正则约束写进生成 prompt（原创性=与现有因子池
  相关性上限、经济逻辑=必须给出机制自述、简洁=算子数上限）→卸 lane_c2 台账→E2/E4/E5 现行质检；
- **P2**：与 gplearn 轨赛马（同一考试、同一及格线），按 E4+E5 幸存率定主辅。

## 三、资源与决策点（等 Owner）

1. 批准本立项（范围=上表 P0/P1）；
2. GPU/时窗：P1 全程 CPU+本地 8B 可扛，无需新算力（与 gplearn 轨共享 E0 闸夜窗）；
3. 赛马及格线：两轨同线（E4 现行冻结阈值+DSR），不因技术路线新而放宽——"量越大及格线
   越狠"铁律不破。

## 四、与 gplearn 轨的关系

互补不替代：gplearn 轨=受控算子空间的机械搜索（便宜、稳定、已投产）；
智能体轨=开放式假说生成（贵、杂、上限高）。两轨货同走 E2→E4→E5 一条咽喉，
幸存者同入 factor_registry。


---

# 附二：Owner 裁定与开工记录（2026-09-15）

## §七 裁定（Owner 原话级）

1. **P0/P1/P2 全批**；
2. **P2 全批全启用（2026-09-15 二次裁定修订）**——初裁"建而不启用"系 token 顾虑；
   Owner 复核成本结构后撤销开关：赛马主力成本=E4 回测算力（走 E0 夜窗）+本地 8B
   推理（零 API token），**无 token 开销即无开关，直接建直接用**；
3. **施工方法论强制**：本模块=完整新模块，必须走**施工 SOP 15 步闭环**
   （construction_workflow_policy.md）+ **挖矿 SOP**（病菌寻路/六向寻路）——先用挖矿
   方法论把"矿机本身的功能矿脉"挖干净（六向：上游数据/下游消费/算法机制/后端/前端/
   数据字段），矿挖完（signal/noise 门达标）再按施工闭环动工。挖矿机自身也要被挖矿，
   本身先建得足够好。

## §八 P0 试驾对象确认（2026-09-15 检索）

- **AlphaAgent 官方开源仓：github.com/RndmVariableQ/AlphaAgent**（确认开源；
  论文实证覆盖 S&P 500 **与 CSI 500——中证500，A股直接可对标**，连熊牛周期抗衰减均验证）；
- 后续论文追踪：Cognitive Alpha Mining via LLM-Driven Code-Based（arXiv 2511.18850，
  已引用 AlphaAgent 为基准——三代目候选，P0 一并精读）；
- 对照笔记载体：P0 产出 `docs/_working/2026-09-1X-agentic-mining-p0-notes.md`（下一班）。

---

# 附三：P0 试驾对照笔记（§七.3 执行件，2026-09-15）

> 2026-09-15 策略工厂后端施工班（st-facbe-20260914）。立项书全批后的 P0 交付物：
> 两篇论文精读 + 官方仓侦察 + 六向寻路 + P1 设计输入。**裁定：不引入外部代码，借方法。**

## 一、AlphaAgent 精读（KDD 2025，arXiv 2502.16789v2）

### 1.1 三智能体闭环（论文机制骨架）

- **Idea Agent**：生成结构化市场假设 h（observations/knowledge/justification/specification
  四件套——specification 含数值与时间窗参数约束）；首轮种子假设后基于历史演化轨迹迭代；
- **Factor Agent**：每假设生成多候选（自然语言描述 d + 算子库表达式 f），按复杂度与
  对齐度过滤；维护**成败案例知识库**（失败按模式分类入库）；
- **Eval Agent**：回测+相似因子检索+三类指标（预测力/收益/风控）→ 反馈回 Idea Agent 闭环。

### 1.2 三正则公式（可直接抄进我们 prompt/验收的部分）

| 正则 | 论文实现 | 我们的对价 |
|---|---|---|
| 原创性 | **AST 最大同构公共子树相似度** S(f)=max s(f,φ)，对 alpha zoo（Alpha101）取最大值作惩罚项（公式5/6） | E5 是收益相关聚类（MOD-BT-086）——**AST 结构去重是互补新件**：表达式结构撞车在收益数据出现前就能拦 |
| 经济逻辑 | 假设-因子对齐 C(h,d,f)=0.5·c₁(h↔d)+0.5·c₂(d↔f)，LLM 打分 0-1（例：声称流动性因子但表达式无成交量项→c₂ 低分）（公式7） | **=E2 预审的内环版**。我们 E2 是管线闸（后置），他们是挖矿内环（前置）；P1 把对齐评分写进生成 prompt（事前）+E2 保留终审（事后），双层 |
| 简洁性 | R_g=α₁·符号长度 SL+α₂·自由参数个数 PC+α₃·ER；ER=β₁·AST相似+β₂·对齐分+β₃·log(1+特征使用量)（公式4/8） | init_depth+parsimony+length 已有等价物（MOD-BT-155 constraints） |

**注意**：论文摘要层面流传的"counterfactual reasoning"经全文核验**不存在**——机制是
交替优化预测性能 L 与正则 R_g 到局部最优。以全文为准，讹传止于本笔记。

### 1.3 CSI 500 实测（2021-01~2024-12 含交易费，Qlib+LightGBM 组合，top50 剔除 bottom5）

| 方法 | IC | ICIR | 年化超额 | IR | MDD |
|---|---|---|---|---|---|
| **AlphaAgent** | **0.0212** | **0.1938** | **11.00%** | **1.488** | -9.36% |
| AlphaForge | 0.0146 | 0.1299 | 3.45% | 0.327 | -17.67% |
| RD-Agent | 0.0113 | 0.0872 | 0.78% | 0.074 | -20.85% |

- **基础 LLM=GPT-3.5-turbo**（便宜模型成立！）；消融 DeepSeek-R1 版本最优（AR 9.19%，
  注意其测试窗不同）——**我们 Ollama 本地就有 deepseek-r1:8b，零成本对齐论文最优配置**；
- 消融：正则使命中率 0.29 vs 0.16（+81%）、开发成功率 0.83 vs 0.75、token 效率 +23%
  ——**正则不只保质量还省钱**，直接支撑"三正则写进生成 prompt"的 P1 设计；
- 数据：仅 OHLCV（Baostock CSI500）；组合=4 基础 alpha+新因子拼接喂 LightGBM。
  **与我们 c1_market 面板+特征表完全同构**。

## 二、AlphaMuse 精读（arXiv 2505.11122，AAAI 2026）

- 机制：**MCTS 组织探索树，LLM 扮演生成/变异算子**，金融回测的量化反馈引导树搜索；
- 核心创新：**frequency subtree avoidance（频繁子树规避）**——防止公式同质化，与我们的
  E5/AST 原创性同族，但作用于搜索过程（事前）而非验收（事后）；
- 全文深读与开源状态：摘要页未列官方代码（查无即记无）；对我们 P1 的增量=MCTS 组织方式
  （v3 可选，P1 不需要——gplearn 轨已是成熟的搜索组织器，MCTS 是未来第三轨选项）。

## 三、官方仓侦察（RndmVariableQ/AlphaAgent，WebFetch 通道）

> 本机 git 直连 GitHub 失败（代理 10808 未开+直连重置），改走 WebFetch 通道侦察；
> 下班前代理恢复可补 `git clone --depth 1` 实跑（P0 剩余半件事，不阻塞 P1 设计）。

- **仓库已高度工程化（演化版，超出论文）**：`alphaagent/` 核心包+`scripts/` CLI
  （fetch_market/build_panel/init_factorlib/ingest_factors/eval_factor/factor_mining_agentscope）+
  `artifacts/factorzoo/*/expressions/*.dsl`（因子以 DSL 表达式文件入库，git 同步团队共享）；
- 数据栈：**Tushare+parquet 面板**（panel_1d.parquet，label_1d/10d_close_to_close），
  universe=中证 1000（2015~2026，约 2757 只）——与我们的 CH+面板加载器完全不同栈；
- LLM：AgentScope 框架，README 只写 OpenAI 风格 key（Ollama 支持未文档化，需读源码）；
- **试驾裁定：不引入代码**。理由：数据栈（Tushare/parquet/Qlib）与我们（CH/面板加载器/
  factor_registry）异构，搬代码的适配成本 > 借方法的复刻成本；其增量价值=三正则公式+
  三智能体循环结构，已全部提取（§1）。

## 四、矿机自身六向寻路（挖矿 SOP，矿脉全闭合于现有件）

| 向 | 结论 |
|---|---|
| ①上游 | 面板加载器已有（MOD-BT-155 fetch_panel：7 特征+y_fwd5+118 列基座）；**种子假设=现成**：E2 台账 10 条 pass_mechanism_clear 假说反哺为挖矿种子（E2 通过→变矿种，闭环） |
| ②下游 | lane_c2 台账→E2 预审（MOD-BT-091）→E4 考试→E5 去重→factor_registry，**全现成零建设** |
| ③算法 | 生成=LLM 按白名单算子产 DSL 表达式（gplearn 轨同款算子约束）；三正则：对齐/原创写进 prompt 事前引导+验收事后把关；AST 结构去重=唯一候选新件 |
| ④后端 | scripts/backtest/lane_c2_agentic_miner.py（号段 MOD-BT-156，施工时按 MODULE-ID-CONSISTENCY 复核）+E0 问闸+出生证（照抄 MOD-BT-155 模式） |
| ⑤前端 | 无新页（工厂页已有车道 C 位），登记不施工 |
| ⑥数据字段 | 现有面板字段即够（论文亦仅 OHLCV）；label 口径沿用 y_fwd5 |

## 五、P1 施工清单（按 §七.3 双 SOP：先挖后建，本文=挖矿件；施工闭环下一班）

1. depgraph 设计态登记（MOD-BT-156）+ capability_lookup 反查留审；
2. `lane_c2_agentic_miner.py`：OllamaChat（本地 8B；消融档 deepseek-r1:8b）产 DSL→
   白名单算子校验→AST 相似度 vs REG-IND-001+gplearn 存货→增量 IC 验收→出生证→
   lane_c2_candidates.csv；
3. 三正则入生成 prompt：对齐评分要求（hypothesis↔description↔expression 三段自述）、
   AST 原创约束声明、长度/参数上限；
4. E2 消费 lane_c2 台账（管线现成，--source 换路径即用）；
5. 测试同批（纯函数：DSL 校验/AST 相似度/prompt 构造/出生证）。

## 六、开放项（不阻塞 P1）

- 本机代理恢复后补 `git clone --depth 1` 实跑（结构级试驾已完成，实跑=锦上添花）；
- AST 相似度实现选型：自研树编辑距离 vs 现成库（P1 施工时定，纯函数可测）；
- deepseek-r1:8b 消融档是否首班就上（本地已有，零成本，建议 P1 直接双模型对比）。
