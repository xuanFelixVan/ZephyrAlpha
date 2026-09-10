---
ttl: task_bound
---

# TDM 病菌寻路增长施工文档（增长轨，2026-09-09 夜）

> **职责**：本文档归今晚后端负责人会话（st-tdmbe-20260909）——与模块施工轨（[2026-09-09-tdm-missing-modules-construction.md](2026-09-09-tdm-missing-modules-construction.md)）并行，同会话负责。
> **方法论真源（已升 permanent）**：本文件 §1/§1.5/§1.6 于 2026-09-09 深夜升为 [sop/trading_decision_map_pathfinding_sop.md](../01_policies_and_standards/sop/trading_decision_map_pathfinding_sop.md)（长期增长机制，含半年复审 T2 模式）——**方法论冲突以 SOP 为准**，本文档降级为 2026-09-09 夜的执行实例（种子分支 G1-G6+台账）。
> **Owner 目标原话**：每一个节点去延伸新的节点，不断寻找，直到能查的都查到——先把全景画完整，再逐个开发。
> **开工**：Owner 下令即开（今晚晚些时候），与施工轨按 §4 节拍交错。

## §0 双轨关系与铁律（为什么不能边施工边改图）

| 轨 | 干什么 | 动什么文件 |
|---|---|---|
| 增长轨（本文档） | 画图：设计新节点→批量落图→验收冻结 | `config/trading_decision_map.yaml` + 本文档台账 |
| 施工轨（清单文档） | 建模块：C/B 类落码 + module_ref 回填 | src/zephyr/ 域包 + tests/ + 回填地图引用 |

**铁律：施工中途禁改图。** 两轨只在"批次边界"交换：增长批落图并验收通过→地图冻结为新版本号→施工轨才继续（它的回填目标以冻结版为准）。防的是"一边加节点一边回填，目标漂移两头乱"。

## §1 增长方法论：病菌寻路五步循环（每批一次）

1. **选母节点**：从当前施工波次的节点、或 §2 职能缺口清单出发
2. **四道前置检查**（trading_decision_map_layering_sop 真源，一道不过不长）：
   ①已有资产盘点五选一（复用/扩展/已有/占位/新建）②四路外部调研 ③上层完整性（父节点立了吗）④枝干分级（该在哪层）
3. **拆分三条件过滤**（D108 铁律）：独立数据输入或动作输出 + 行为差异可回测区分 + 非纯参数变化——三条不全满足=不配成节点（写进设计稿驳回原因）
4. **设计稿落档**：在本文档 §5 台账登记草案（node_id 预编号/name_zh/decision_question≤100 字/algo_note 大白话/五联锚候选/父节点/依赖数据），**此步不碰真源**
5. **批量落图+四关验收**：validate error=0 + 双测试 90/90 + align_all exit 0 + 层位闸留痕 → 网关提交（地图 YAML+本文档台账同 commit）→ 冻结版本号（v129+批1=n₁）→ 通知施工轨消费

**循环终止判据（什么叫"画完了"）**：§2 全部职能有节点承载 + 每条"输入→决策"边之间无未建模的中间判断 + 已有代码能力全部入图或入 D 类不建清单。**节点数不是判据**（业界无决策地图形态，"机构有多少节点"无真源，禁为多而多）。

## §1.5 六向寻路协议（每个母节点的标准作业，Owner 2026-09-09 深夜补立）

对每个选定的母节点，**六个方向**逐一探测（每向=内部反查+全网搜索双动作），每向产出 ≥1 条发现或"已查无"结论（查无也是有效结论，记档）：

| 方向 | 问的问题 | 内部动作（反查优先） | 全网搜索动作 | 产出物 |
|---|---|---|---|---|
| ①上游 | 还有什么信息应该喂进来？ | 该节点 data_refs 反向审计；data_asset_registry 按类扫 | 机构做同类决策看什么数据（研报/公开文档） | 新 data_refs 候选 / DS 缺口单 |
| ②下游 | 这个输出还该喂给谁？ | 地图边反向审计+决策链断点扫描 | 机构里这个判断会触发哪些后续动作 | 新边 / 新消费节点候选 |
| ③算法/机制 | 业界学界最新怎么做？ | capability_lookup + Grep（**内部已有实现优先复用，禁重复造**） | **最新学术论文（SSRN/arXiv/顶刊顶会）+ 一线机构研报**，必须带 URL+发布方+年份 | 算法候选卡（含来源清单） |
| ④后端 | 代码侧缺什么？ | Step 1.5 三重搜索（src/+scripts/+tests/） | 开源实现参考（GitHub，标注 license 与成熟度） | 复用结论 或 拟建模块路径 |
| ⑤前端 | 怎么呈现给 Owner？ | web/frontend_map.yaml 查重（同功能点禁重建） | 同类终端的信息呈现惯例 | 前端需求登记单（**只登记不施工**，归前端会话） |
| ⑥数据字段 | 算法要什么字段？我们有吗？ | field_dictionary（259 条）+ data_asset_registry 逐字段核对 | 该字段的行业口径定义 | 字段清单 + DATA-GAP 标记 |

**时间盒（防无限延伸）**：每母节点单批最多 3 个新候选节点，长尾排下一批；每向搜索 ≤20 分钟；深挖顺序=价值高的方向先（算法/数据 > 前端）。

## §1.6 来源与审查纪律（防噪音四道闸——Owner 铁律：编出来的东西是噪音，没意义）

1. **来源可溯闸**：每个外部发现必须带 来源 URL+发布方+年份，写进候选卡；**禁凭模型记忆断言"业界都这么做"**。学术论文优先 SSRN/arXiv/期刊顶会；研报限一线机构；超过 10 年的经典方法可用但标"经典"。
2. **交叉验证闸**：关键结论 ≥2 个独立来源相互印证；单来源=状态"待验证"，不入图。
3. **A 股适配闸**：外部方法逐条过 A 股微观结构（T+1/涨跌停/散户主导/无做市商），不适配的写明改造方案或直接驳回。
4. **可回测+数据可得闸**：新节点必须能回答"怎么算对错"（validation_method_registry 五类之一）**且**所需字段已登记或可登记；任一不满足=标 GAP-METHOD / DATA-GAP 挂起，禁带病入图。

四闸全过 → 才进 §1 第 3 步（拆分三条件）→ 设计稿 → 落图。审查动作全部记入 §5 台账；自审口径按长城指令 §3（连续两轮 0 问题）；学术硬结论（DSR/PBO 类统计检验）超夜班能力时挂晨审 GLM5.3 复核清单。

## §2 职能完备性对照表（增长的总地图——往这上面找缺口）

| 决策职能族 | 现有承载 | 缺口判定 |
|---|---|---|
| 大盘判断（今天能不能做） | L1 五传感器+AGG+总闸；L0 作战计划 | **G1：明日情绪盘中滚动预测缺（见 §3）** |
| 板块/赛道（打哪里） | L2 十环节 | 较完整；反查后微调 |
| 个股（买哪只） | L3 十二环节 | 较完整；L3-04 负面否决今晚 C7 建 |
| 执行（怎么成交） | L4 十三环节+SOR 零件 | TCA/成本反馈闭环弱——G5 候选 |
| 持仓管理（手上怎么办） | P1/P2/P3 | P1-03 今晚 C8 建 |
| 离场（怎么走） | X-S1/S2/R1 | 较完整 |
| 组合反馈（钱怎么分） | F-C1/C2/C3 | 较完整 |
| **资讯→决策传导（新体系）** | 零件散落（alt_data/intelligence/nlp/产业链图谱），**无入图主干** | **G2：本批增长主分支（设计归本轨，管道归接线会话，见姊妹指令）** |
| 明日推演（明天怎么办） | tomorrow_boundary_planner（盘后）+ 8 态预测零件 | **G1：盘中滚动预测断链** |
| 币圈 | TDM-C-* 四节点骨架 | G3：展开设计先行，实现待 Owner 排期 |

## §3 种子分支清单（首批增长候选，按价值排序；每批从中取 2-3 个）

| # | 分支 | 母节点 | 拟增节点草案（名称/一句话） | 前置检查 | 状态 |
|---|---|---|---|---|---|
| G1 | **明日情绪盘中滚动预测** | L0-02 偏离监控（姊妹节点）或 L1-S5 扩展 | "明日情绪滚动预测→回写今日仓位档"：盘中每 N 分钟用 8 态预测+相似日推理滚动更新明日概率，悲观则下调今日 stance（Owner 场景：拿不准明天→今天减仓） | 盘点：next_day_8state_forecast/similar_day_evaluator/brier_calibration 零件在；tomorrow_boundary_planner 明文"不读盘中数据"=断链实证 | 设计中（反查先行） |
| G2 | **资讯-产业链传导**（主分支） | L1-S0 宏观传感器 + L2-09 催化剂 + L3-04 负面否决 | 事件→产业链节点命中→受冲击标的/板块→盘中消费（偏离监控/盘中扫描/否决器）。节点规格由接线会话交付，本轨统一落图 | 管道在建（他会话）；入图设计归本轨 | 待接线交付 |
| G3 | 币圈四节点展开 | TDM-C-L1~L4 | 每节点下设计 L1 传感器/赛道/币对/执行的子骨架（设计稿，实现待 Owner 立项） | 待做 | 挂起 |
| G4 | 执行成本反馈闭环 | L4-09/L4-13 | TCA 实测冲击成本→回写执行算法选择（EXA 选型自学习） | 盘点：ex_sor/slippage_analyzer+execution_quality_scorer+t0_cost_model 在 | **已落图**（增长批2：TDM-E-L4-14，2026-09-10 夜班） |
| G5 | 现有节点有据拆分 | L4-02 等 | 竞价/盘中/尾盘三段——**先挂起**：流根落地看过全景再定（Owner 已裁先不动） | — | 挂起 |
| G6 | 流根四节点 | 四流末端 | TDM-E-FLOW 建仓流/TDM-P-FLOW 持仓流/TDM-X-FLOW 离场流/TDM-F-FLOW 组合流（aggregation，输出=今日买卖清单） | 设计已完成（上轮方案） | **已落地**（他会话合并批次 23da636683 入图，2026-09-09 深夜；地图 133 节点/185 边） |

### §3.1 今晚寻路作业队列（首批母节点×六向起点；发现全部记 §5 台账）

| 母节点 | ①上游搜索起点 | ③算法/机制搜索起点 | ②下游重点 | 备注 |
|---|---|---|---|---|
| G1 明日情绪滚动预测 | 隔夜外盘（期货/ADR/港股夜盘）/舆情数据源 | overnight return predictability、next-day sentiment/regime forecast、市场情绪状态转移模型 | L0-01 stance 回写、L3-06 环境开关 | Owner 场景直连，最高优先 |
| L1-S1 大盘指数传感器（Owner 举例） | 指数择时常用数据（板块宽度/期限结构/北向） | 指数趋势结构打分、A 股指数择时因子研究 | L1-AGG 打分权重；前端指数卡需求 | **六向全走一遍做样板**，跑通后复制到其余节点 |
| L1-S2 市场内部结构 | 涨停生态/连板梯队/炸板数据源 | market breadth 指标体系、涨停生态研究 | L1-AGG；题材生命周期 | 数据源可得性重点核对 |
| L2-05 水温响应 | 情绪周期数据（赚钱效应/亏钱效应） | A 股情绪周期/游资行为研究 | L2-05-2 响应三件套 | 与 sentiment_cycle.py 反查联动 |
| G2 资讯-产业链传导 | （依赖接线会话交付规格卡） | event study、news-driven trading、产业链传导研究 | L3-04 负面否决、L0-02 偏离修订 | 等他会话交付后启动落图 |
| L4-06 执行算法 | 盘口/微观结构数据源 | optimal execution、TWAP/VWAP 变体、RL 执行 | L4-13 对账反馈（G4 联动） | 与 EXA 登记表查重 |
| X-R1 熔断族 | 极端行情数据（历史熔断样本） | 回撤控制/动态风险预算/组合保险（CPPI 类） | X-R1-02 减仓序 | CORE 域，发现挂晨审 |

### §3.2 盲点自查记录（2026-09-09 深夜 Owner 发问触发，已补入本文档）

1. **六向寻路协议缺失**（原稿只有增长方法论，没有 per-node 作业矩阵）→ 已补 §1.5
2. **防噪音审查闸缺失**（全网搜索可溯源/交叉验证/A 股适配/可回测四闸）→ 已补 §1.6
3. **数据可得性盲点**：找到算法没字段=白搭 → DATA-GAP 标记机制（§1.5⑥/§1.6 闸 4）
4. **前端职责盲点**：寻路会探到前端需求，但今晚前端归前端会话 → 只出"需求登记单"不施工（§1.5⑤）
5. **爆炸控制盲点**：寻路无限延伸会失控 → 时间盒（每母节点单批 ≤3 候选、每向 ≤20 分钟）
6. **查重盲点**：寻路发现可能与既有 140 因子/146 策略/256 形态/DAL 算法撞车 → 内部反查动作已含层位闸①+§1.5 各行
7. **字段审查真源**：字段口径对齐 field_dictionary（259 条）与 data_asset_registry，不另起词表（向内收）

**保留盲点（诚实交底）**：①深夜全网搜索的源质量与可得性依赖执行会话工具，无法事先保证；②统计硬结论（DSR/PBO 类）超夜班能力时一律挂晨审 GLM5.3；③寻路发现的"最新研报"若涉收费墙，只登记题录+可获取摘要，禁编造内容。

## §4 与施工轨的节拍表（今晚执行序）

| 时刻/事件 | 增长轨 | 施工轨 |
|---|---|---|
| 波次0 | G1 反查定界+设计稿；G6 流根（若批）设计定稿 | 反查 12 项定 C/B/A 边界 |
| **边界1** | **落图：流根+G1（若设计过四关）→验收→冻结 v_n₁** | — |
| 波次1 | （停笔，等施工） | 风控执行 C11/C12+回填 |
| **边界2** | 增长批2：G4/G2 首批节点落图→冻结 v_n₂ | — |
| 波次2/3 | （停笔） | 传感器/选股链 |
| **边界3** | 增长批3：G2 后续+crypto 骨架设计稿落档 | — |
| 波次4 | （停笔） | 持仓组合+全表清账 |
| 收工 | 增长台账全部三态标注（已落图/已驳回/挂起）+交接包 | R1/R21 清零复核 |

## §5 增长台账（每条候选走完五步循环在此销账）

| 候选 | 五步进度 | 四关结果 | 落图 commit | 终态 |
|---|---|---|---|---|
| G1 明日情绪盘中滚动预测（TDM-E-L0-04，2026-09-10 夜班批1） | 五步全走完：①母节点=L0-02 姊妹（定为 TDM-E-L0-04，parent=TDM-E-L0）②四道前置检查过——盘点：next_day_8state_forecast(MOD-SIG-037)/similar_day_inference(MOD-SIG-063)/brier_calibration(MOD-PLAN-010) 零件全在=引用；tomorrow_boundary_planner 不变量明文"不读盘中实时数据"=断链实证；外部调研见下；父节点 L0 定稿✓；树枝级✓ ③D108 三条件过（独立输入输出✓/可回测=agg_discrimination✓/非参数变体✓）④设计稿=本行+地图注释 ⑤落图 137 节点 | validate ok=true / 双测试 98 绿 / align_all exit0 / 网关提交 | c8f678d8 | 已落图（红节点；模块=施工清单 C13 待建；latency_budget 留 R39 欠账待 C13 实测补） |

**G1 六向寻路记录**（防噪音四闸留痕，2026-09-10 夜班）：
- ①上游：DS-150 指数日线（8 态先验+盘中重算）/ DS-082 涨跌停生态（盘中情绪）/ DS-107 新闻情绪窗——全已登记✓；增强候选=期指基差（futures_basis_monitor 已有件，暂不挂）。
- ②下游：TDM-E-L0-04→TDM-E-L0-02 feed（修订权在偏离监控）；机构实践=盘中检查点评审（69 号 §2.13 D24 机构四阶段，已网验）。
- ③算法：内部=8 态马尔可夫转移+相似日 KNN+Brier 校准降权（全已有件）；外部佐证（来源可溯闸+交叉验证闸≥2 独立源）：
  - Lou, Poli & Gao《The Day Destroys the Night, Night Extends the Day》（经典：隔夜收益延续/日内反转）https://www.carloalberto.org/wp-content/uploads/2023/01/Day-Destroys-The-Night-Night-Extends-The-Day.pdf
  - Akbas et al. 2021《Overnight returns, daytime reversals, and future stock returns》（高情绪期预测性更强）
  - Renault, Journal of Banking & Finance 2017《Intraday online investor sentiment and return patterns》（盘中前半小时情绪更新预测尾盘收益）https://ideas.repec.org/a/eee/jbfina/v84y2017icp25-40.html
  - SSRN 5599654《News Sentiment and Overnight Return Prediction》（CSI300 隔夜预测，A 股直接适配）https://papers.ssrn.com/sol3/Delivery.cfm/02eb9d1c-a89b-483f-a9e7-160e8e07a8e6-MECA.pdf?abstractid=5599654&mirid=1
  - arXiv 2507.04481 (2025)《Does Overnight News Explain Overnight Returns?》https://arxiv.org/html/2507.04481v1
- ④后端：断链实证成立；缺盘中滚动组合器→施工清单 C13（拟 src/zephyr/plan_engine/intraday_tomorrow_forecast.py）。
- ⑤前端：既有呈现=F-MODLIB-AUTO-33"明日 8 态推演"+F-REVIEW-AUTO-17"明日预案"；**需求登记单（只登记不施工，归前端会话）**：8 态推演卡的盘中滚动版（四时点刷新）+降档预警徽章。
- ⑥数据字段：DS-150/082/107 全已登记，无 DATA-GAP；A 股适配闸=T+1 下"今天减仓防明天"合法（SSRN CSI300 直接适配）。

**增长批2 晨审移交清单**（2026-09-10 夜班，night-pathfinding-2300）：
1. **R21 module_id 格式冲突**（落图时实锤）：execution_quality_scorer.py 的 depgraph blueprint_id=`MOD-EX_SOR_EXT-002`（带下划线），地图 R21 正则 `MOD-[A-Z0-9]+(-[A-Z0-9]+)*` 不认下划线——写原 id 报格式错、去下划线报对账错，两真源格式互斥。涉 id 改名跨域（depgraph 缓存+44 号域文档+模块蓝图头），非夜班轨可决；TDM-E-L4-14 暂留 module_ref 无 module_id（warn 级欠账有先例）。
2. **X-R1 外部方法三件**的 A 股离散化改造方案：CPPI（Black-Perold 1992）/回撤控制（Grossman-Zhou 1993）/趋势危机 alpha（Hurst-Ooi-Pedersen 2017），URL 见台账 X-R1 行。
3. **G4 RL 执行远期候选**：arXiv 2411.06389 (2024)、2507.06345 (2025)——A 股 T+1/涨跌停/拆单限制（execution_route_policy"打板不可拆单"）需改造，暂不立项。
4. **DAL 补登**：DAL-MA-ALIGN code_ref 补 `src/zephyr/regime/features/index_sensor.py`（现 registry code_ref=None 而代码已在产）；DAL-BREADTH-SCORE 广度计分核=施工候选（MOD-DATA-062 采集在、计分缺）。
5. **前端需求两张**（只登记，移交 st-tdmfe）：指数趋势分卡（L1-S1，-2~+2+四时点刷新）；涨停板生态卡（L1-S2，梯队/断层/晋级率，limit_up_ecosystem_leadership 模块头已注候选）。
6. **G1 遗留**：latency_budget R39 欠账（随 C13 实测补，前批已登记）。

| G2 资讯-产业链传导 | 复核（2026-09-10 夜班批2）：L2-09-1/L2-09-2 红节点在图（bc0e322b 骨架）；今晚活跃会话无接线轨（session registry 核实），W3/W4 规格卡未交付 | — | — | 挂起（维持，等交付） |
| G3 币圈四节点展开 | 未启动 | — | — | 挂起 |
| G5 现有节点拆分 | Owner 裁先不动 | — | — | 挂起 |
| G6 流根四节点 | 已落地（他会话 23da636683） | — | 23da636683 | 已落图 |
| L1-S1 大盘指数传感器（样板六向，2026-09-10 增长批2） | 六向全走：③算法=挂 DAL-MA-ALIGN（design）——code=index_sensor.py MOD-REGIME-016 已挂 module_ref 且模块消费者行点名本节点，registry↔code↔map 三角闭合；①上游=查无缺口：北向盘中信号**驳回**（披露机制 2024-05-13 取消实时买卖额、2024-08-19 起个股持股改季度——盘中无数据可算；来源：证券时报 stcn.com/article/detail/1203876.html + 沪深交易所 2024-04-12 两阶段公告）；DS-110 A50 期货候选**暂不挂**（index_sensor 零消费 A50，挂了=挂而不用，待隔夜腿立项）；D109 终裁已规划攻防板块特征（DS-170 注释在节点上）不重复；②下游=L1-AGG 已接、权重=DAL-AGG-DUALAX 在 DAL；④后端=MOD-REGIME-016 在；⑤前端需求登记单：指数趋势分卡（-2~+2 视觉化+四时点刷新，归前端会话，只登记不施工）；⑥数据=DS-150 在产 | validate errors=0 / 双测试 98 绿 / align_all exit0 | 本批（增长批2） | 已落图（algo_refs 挂载；样板结论：传感器层缺的是 registry 三角闭合，不是新节点） |
| L1-S2 市场内部结构传感器（2026-09-10 增长批2） | ①上游=data_refs+[DS-108] 分钟级宽度快照（MOD-DATA-062 采集器 production 在产）；连板梯队明细=**DATA-GAP 挂账**（limit_up_pool_collector testing 待 DDL 建表，GAP-F-13；字段可登记=封板资金/炸板次数/连板高度已在采集器 invariants 全列）；③算法=挂 DAL-BREADTH-SCORE（design 无代码=广度计分核缺口：采集在/计分缺→施工候选挂晨审）；MOD-SIG-097 连板梯队 leadership（testing）=深化候选记档；外部佐证（两独立源印证涨停生态结构信息含量）：Seasholes-Wu 2007 *Journal of Empirical Finance* 14(5) 590-610 上证涨停板注意力买入（sciencedirect.com/science/article/abs/pii/S0927539807000308）+磁吸效应实证《管理科学学报》涨停侧存在/跌停侧无（jmsc.tju.edu.cn/jmsc/article/html/20080514） | validate errors=0 / 双测试 98 绿 / align_all exit0 | 本批（增长批2） | 已落图（data_refs/algo_refs 挂载；DATA-GAP 挂账待 DDL） |
| L2-05 水温响应（2026-09-10 增长批2） | ①上游=已通（S5 11 信号环比→L2-05-1 主判+月/周封顶）；③算法=sentiment_cycle.py 五阶段 phase_prob+STRATEGY_DEPLOYMENT_MATRIX 与 L2-05-2 信号响应三件套语义对位，但 MATURITY=new、CONSUMERS 全"待 G07 相关性验证"→**闸 4 不过禁入图**，挂起候选（验证过后挂 L2-05-2）；DAL 无对应条目（DAL-EMO-SIXSEG=六段周级，非五阶段情绪周期，勿混）；外部佐证：Baker-Wurgler 2006 *Journal of Finance* 61(4) 经典（pages.stern.nyu.edu/~jwurgler/papers/wurgler_baker_cross_section.pdf）+A 股 CICSI/PCA 派生文献多源+北大中国投资者情绪指数 | 四闸：闸 4 不过（算法未验证） | — | 挂起（待 G07 相关性验证） |
| G4 执行成本反馈闭环→L4-06（TDM-E-L4-14，2026-09-10 夜班批2） | 五步全走完：①母节点=L4-06 姊妹（定为 TDM-E-L4-14，parent=TDM-E-L4，盘后）②四道前置检查过——盘点：slippage_analyzer(MOD-EX_SOR_EXT-001 production)+execution_quality_scorer(MOD-EX_SOR_EXT-002 production)+algo_execution_selector(MOD-XS-011 production) 三零件全在；**断链实证=scorer 消费者行写"MOD-XS-011 算法选择器反馈环"，但 selector 源码零 import quality/feedback（grep 实证 2026-09-10）=闭环未接线**；父节点 L4 定稿✓；树枝级✓ ③D108 三条件过（独立输入=成交流水/独立输出=选型偏好回写/可回测=分算法执行成本对比/非参数变体）④设计稿=本行+地图节点 ⑤落图 138 节点+2 边（L4-10→L4-14 feed、L4-14→L4-06 feedback，S1↔S3 双向 feedback 同款先例）+施工清单立 C14；外部佐证：Almgren-Chriss 2000 *Journal of Risk* 3(2) 经典（risk.net/journal-risk/2161150）+RL 执行近作 arXiv 2411.06389(2024)/2507.06345(2025)（远期候选挂晨审：A 股 T+1/涨跌停/拆单限制需改造） | validate errors=0 / 双测试 98 绿 / align_all exit0 / 网关提交 | 本批（增长批2） | 已落图（模块=C14 接线待排期；module_id 欠账=R21 格式冲突挂晨审） |
| X-R1 熔断族（2026-09-10 增长批2，CORE 域发现挂晨审） | ①上游=查无缺口（DAL-CIRCUIT-5 production 输入=组合日盈亏+回撤，组合内部量非外部 DS，data_refs 留空正当）；③算法外部三件全带 URL 挂晨审：CPPI=Black-Perold 1992 *JEDC* 16(3-4)（sciencedirect.com/science/article/pii/016518899290043E）+回撤控制=Grossman-Zhou 1993 ***Mathematical Finance*** 3(3)（常被误引 JF，onlinelibrary.wiley.com/doi/10.1111/j.1467-9965.1993.tb00044.x）+趋势危机 alpha=Hurst-Ooi-Pedersen 2017 *JPM* 44(1) 1880 起 67 市场危机期正收益（fairmodel.econ.yale.edu/ec439/hurst.pdf）；A 股适配闸：T+1+跌停无法卖出→CPPI 连续调仓不可行需离散化改造（晨审议题）；②下游=已接（R1→X-S1-06/F-C2-01/P2-01） | 发现全挂晨审（CORE 域纪律） | — | 挂起（晨审清单 3 项） |

**纪律**：真源 YAML 只在批次边界动；禁越级立节点（父未定不立子）；新节点必须有数据来源或标 [ASSUMPTION]；每批台账+地图同 commit；本文档 ttl: task_bound，增长收官归档。
