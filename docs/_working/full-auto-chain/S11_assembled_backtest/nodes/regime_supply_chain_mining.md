---
ttl: task_bound
title: T1-α 节点挖矿：regime 检测与供给链内核
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 节点挖矿：regime 检测与供给链内核（父环节 S11_assembled_backtest；真源 MOD-REGIME-001）

> 挖矿依据：decision_kernel_mining §5 子节点清单第 1 件——"regime 错=权重错"生死线的
> 判定本体。链条=RegimeDetector（regime_detector.py，861 行全读）→ print_regime_history
> （唯一写方）→ c1_backtest.regime_snapshot_history → fw_backtest/auto_mount 消费。
> 产出=数据，采纳裁定归主力会话施工班。

## 1 现状盘点（逐条带 file:line 锚点）

### 1.1 检测器五子模块架构（regime_detector.py）

- ① HMM 4 态（hmmlearn GaussianHMM，BIC 定 K=4；9 态降 4 态的实证：OOS/IS 一致率
  0.34<0.7 门槛，L38-47）；② D-SIGNAL-68 覆盖层（r10 CRISIS/r11 RECOVERY/r12 BREAKOUT
  规则态+8 转换 T1-T6/S1/S2 三阶段评分，TRANSITION_CONFIG L139-242）；③ ConfidenceSignal
  （max(P) 4 档×稀有态折扣，L718-754）；④ RiskSignal（13 参数聚合+#1 门控+共振惩罚+
  机会恢复，L756-803）；⑤ Shrinkage=Confidence×Risk（可开关，L805-829）。
- 输出契约：**7 维灰度概率（Σ=1）+ Shrinkage 标量，禁硬标签**（INVARIANTS L8）；
  dominant=argmax 仅作展示字段（L705）。

### 1.2 数学正确性四问审查

| 算法 | 四问结论 |
|------|---------|
| HMM 拟合 n_init=3 取最优 log-likelihood | **正确**（EM 局部最优+数值敏感性的已知对策，L491-493 有 C1 实证动机：固定 seed 仍致 Shrinkage 不可复现 0.818 vs 0.589） |
| 温度缩放 tempering：softmax(logP/T) | **数学有效但非严格 TS**（自述 L370-376：HMM log_proba 是对数后验非 pre-softmax logits，非 Guo2017 Brier 最优；正式 T 学习登记 P1 §2.2.6 Step3 未施工）——登记待验证 |
| overlay 合并：overlay_mass 压缩 HMM 后 Σ=1（L681-716） | **正确**；overlay_mass>1 等比压缩回 1.0（L691-695）边界有处理；全零回退均匀分布（L834-840） |
| S2 析取通路 keys_or_gte ∧ keys_gte（L842-861） | **正确**（合取/析取并存时两组均须通过，缺 key 计 0.0 语义明确） |
| 转换阶段优先级 strong_confirm>confirm>trigger>fail 取首个满足（L585-589） | **正确**（fail 语义=防守性降级锚定，非触发） |

### 1.3 核心发现 F1——标签漂移病灶已传导到整装权重表（本节点最高优先）

- **前科**：`_STATE_RISK_FACTORS`（L117-125）按 r1-r4 数字标签套风险系数，C1 验证
  2026-08-06 判死刑废弃（L106-110 自述两个致命缺陷：①无监督 HMM 标签在 walk-forward
  各季 refit 间无一致语义——"r1 本季=Bull-Low，下季可能=Bear-High"，按标签套风险=
  随机惩罚；②震荡态永久惩罚致 Sharpe 0.37→0.10）。危机保护改由 feature_risk
  （vol_pct+slope）承担。
- **传导**：`config/framework_plans.yaml` 三套预设的 regime_overrides 恰恰按 r3/r4
  标签套权重（r3=牛市进攻上调、r4=熊市防御加码，framework_plans.yaml:70-97 等），
  权重差幅大（fw-balanced r3 底仓 0.15 vs r4 底仓 0.45）。若 walk-forward 季度重拟合
  使 r3 标签漂移，权重表查到的"牛市"可能是熊市——**与 C1 判死的病灶同源**。
- **缓解事实**：r10/r11/r12 是规则态（overlay），语义稳定不受 refit 影响；受影响的是
  r1-r4 四个 HMM 标签态，其中 r3/r4 承担最大权重差。
- **供给链实证**：print_regime_history.py:99-141 走 `build_shrinkage_schedule`，
  walk-forward（train_years/detect_window 参数）真实发生季度级重拟合；L151-185 落库
  dominant 列未见任何跨段标签对齐（label alignment/Viterbi 统计特征锚定）步骤——
  **待验证**：RegimeFeatureBuilder 内部是否有对齐逻辑（本挖矿未读该文件，登记施工
  前必查）。13_regime_phase3_engineering_plan §2.1.6.4"标签对齐协议"有规划位，
  状态未核实。

### 1.4 核心发现 F2——回测/实盘双轨语义分叉（整装回测证据的系统性偏差）

- 整装回测链消费 regime 的方式=**硬标签查表**：regime_snapshot_history.dominant →
  fw_backtest.load_regime_series（fw_backtest.py:167-185）→ composer 逐日查
  regime_overrides（framework_composer.py:579-683）。
- 实盘运行时链消费方式=**灰度概率×Shrinkage**：RegimeMetaAllocator（MOD-PA-007）
  消费 RegimeProbabilities+ShrinkageResult（regime_detector.py:5 CONSUMERS）做
  budget 分配；Shrinkage 危机时最低 0.147（L741）。
- **分叉后果**：整装回测不含 Shrinkage 节流（回测永远满仓），实盘预算会被 Shrinkage
  压缩——回测证据外推实盘**系统性偏乐观**，且偏差方向随 regime 分布变化（危机/熊市
  段越长偏得越多）。与 decision_kernel T1A-5（现金语义裁定）同族但更隐蔽：现金语义
  是"能不能表达"，本发现是"两条链各自表达了不同的资金曲线"。

### 1.5 核心发现 F3——日序供给件"差最后一公里"

- 唯一写方=print_regime_history.py（manual CLI）；fw_backtest.py:44-54 已把挂点 A
  （DataScheduler daily_kline 完成钩子加一行 `ensure_regime_snapshot()`，事件触发
  合规）/挂点 B（独立 kind=regime_snapshot_daily 事件）**精确到行地写好施工说明**，
  且 `ensure_regime_snapshot()/regime_snapshot_freshness()`（staleness≤3 天零成本
  返回，超限告警不阻塞）已交付可调用——**登记"主会话执行"未施工**（fw_backtest.py:44）。
- 消费侧新鲜度闸已上线：fw_backtest_due 每跑先 `ensure_regime_snapshot()`（L217-218），
  证据包自动引用表新鲜度（fw_backtest.py:181/54）。

### 1.6 降级链红蓝对抗审查（fail 方向审查）

| 失效场景 | 行为 | 方向 |
|---------|------|------|
| hmmlearn 不可用/拟合失败 | 均匀分布 1/4（L608-609/644） | 中性偏保守（max(P)=0.25→Confidence 0.8 档） |
| detect 单日异常（供给链批量回放） | 当日 Shrinkage=1.0 满部署（shrinkage_provider.py:156-159） | **fail-open 偏乐观**——危机检测失效日静默满仓；有 warn 无阻断 |
| risk_inputs 缺失 | RiskSignal=1.0（L778-781） | 同上，满部署 |
| overlay 门控（#1≥1.0 非危机期） | overlay 概率注入屏蔽（L439-442） | 防假阳性压仓（#ARCH-REGIME-OVERLAY-001 方案 A，有 B4 验证配套：转换评估记录保留，S2 不漏触发 L431-438） |
| CH 不可达（regime_snapshot 查询） | 静态降级+note 落证据包（fw_backtest.py:184-185） | 披露合格 |

红蓝结论：降级链整体**披露合格、方向偏乐观**——"断了没人知道"风险低（note/warn 齐），
"断了悄悄变满仓"风险中（1.6 行 2/3 两场景）。建议危机检测失效日计入证据包 warn 而非
仅 logger.warning（登记见 §4）。

### 1.7 治理与卫生

- naive `datetime.now()` 三处（L592/715/818）——noqa 注释自证"UTC 迁移登记专项"，不重复立项。
- 概率 NaN 清洗+QA 统计（print_regime_history.py:159-163 红蓝对抗 A2 自证）——卫生合格。
- walk-forward 产物先归档后落库（L227 自述"落库失败=run 留未归档态，巡检器曝光"）——合格。

## 2 六向挖矿日志表

| 向 | 内部发现 | 外部发现（URL+发布方+年份） | 判定 |
|----|---------|---------------------------|------|
| ①上游 | 检测器特征源=RegimeFeatureBuilder（4 指数日线+全量 risk 参数）；**标签对齐有无未核实**（1.3 待验证） | HMM 市场状态检测惯例=特征工程驱动（LSEG Market regime detection，developers.lseg.com，2023） | signal |
| ②下游 | 下游三方：composer 查表（硬标签）/MOD-PA-007 预算（灰度×Shrinkage）/auto_mount 消费先例——F2 双轨分叉 | 动态资产分配消费 regime 概率而非标签（arXiv:2406.09578，2024） | signal |
| ③机制 | F1 标签漂移传导；C1 前科同源（1.3） | 标签切换是 HMM 已知问题、业界以概率消费/多模型投票缓解（ResearchGate ensemble-HMM voting，2026；arXiv:2606.06190 MS-GARCH 多尺度，2026）；中文语境 A 股 regime 识别调研（tbxsx.cn，2026；中邮证券 LSTM-GHMM 择时，2026） | signal |
| ④后端 | F3 供给件差最后一公里（1.5）；挂点方案已写到行级 | — | signal |
| ⑤前端 | regime 概率/状态无面板透出（仅证据包/QA 报告）——登记不施工 | — | 已查无 |
| ⑥数据字段 | regime_snapshot_history 全 7 维概率+dominant+shrinkage 已落库（print_regime_history.py:168-190）；缺=风险分量（confidence_signal/risk_signal 置 None，L156-158 自述"P0-002 需分量时再扩展"） | — | signal |

**计数：signal 5 / noise 0 / 受阻 0 / 已查无 1（⑤前端）。**

## 3 业界与开源对照（逐条过四闸）

| 对照项 | 来源 | 四闸结论 |
|--------|------|---------|
| HMM 标签漂移缓解：概率消费/集成投票 | ResearchGate ensemble-HMM voting framework（2026）；arXiv:2606.06190 Multi-Scale Markov-Switching GARCH（2026） | **立卡候选**：本项目已有正解雏形（C1 已把风险表换成 feature_risk；输出本就是灰度概率）——治本方向=让下游都消费概率而非标签（与 F2 修复同向）。**待验证**（ensemble 方案对 A 股 T+1 低频适配未经回测，单来源） |
| regime 概率驱动的动态资产配置 | arXiv:2406.09578（2024） | **对等已有+接线缺口**：检测器已输出概率，缺的是 composer 侧概率消费路径（见 §4 RSC-2） |
| A 股 regime 识别 SOTA（中文语境） | tbxsx.cn 调研（2026）；中邮证券 LSTM-GHMM（2026） | **登记参考**：无超过本项目五子模块架构的增量；LSTM 混合路线登记远期矿脉 |

## 4 堵点与欠账清单（concrete）

| # | 堵点 | 位置 | 验收标准 |
|---|------|------|---------|
| RSC-1 | **标签对齐核实与补齐**：施工前必查 RegimeFeatureBuilder 是否有跨 refit 标签对齐；若无，r1-r4 键入 regime_overrides 前必须先落对齐（13_regime_phase3 §2.1.6.4 协议落地），或把权重表键改绑 feature 信号/仅保留规则态 r10-r12 | src/zephyr/regime/regime_feature_builder.py（待读）；framework_plans.yaml r3/r4 键 | 核实结论落档；fw-balanced 动态模式重跑前，r3/r4 键语义有对齐证明或键位重构 |
| RSC-2 | **Shrinkage 进整装回测**（F2 治本）：composer 增 shrinkage_by_date 可选参数（供给链已有 build_schedule_from_detector 现成生产），合成面板行乘当日 Shrinkage（≤1 只减不增），剩余质量落现金——与 decision_kernel T1A-5 现金语义裁定**合并裁定** | framework_composer.py compose 算子；shrinkage_provider.py:130 现成 | 动态整装回测双跑（Shrinkage 开/关），两条净值曲线+差值章进证据包（对应 C1 一票否决验证语义） |
| RSC-3 | 日序供给件挂点施工：按 fw_backtest.py:44-54 挂点 A 一行接入 DataScheduler | DataScheduler 任务钩子 | 静置 3 个交易日 regime_snapshot_history 自动日更；freshness 闸从告警转直通 |
| RSC-4 | 降级日证据包披露：detect 异常日/Shrinkage=1.0 降级日清单进 fw-backtests 证据包（现只 logger.warning） | fw_backtest.py 证据包组装 | 证据包含 degraded_days 字段；单测注入异常日验证 |
| RSC-5 | 温度缩放正式化（远期）：P1 §2.2.6 Step3 的 IS 数据 BCE 学习 T 落地，替换手动 tempering | regime_detector.py:632-640 | B1 校准对比报告（tempering vs 学习 T） |
| RSC-6 | 风险分量落库：confidence_signal/risk_signal 两列现恒 None，扩展 print_regime_history 落库 | print_regime_history.py:156-158 | 表两列非空；QA 报告可分段归因 |

## 5 子节点清单

| 节点 | 为什么值得挖 | 建议投喂材料 |
|------|-------------|-------------|
| RegimeFeatureBuilder 特征管道 | RSC-1 的核实对象；vol_pct/slope/fr_5d 特征工程质量直接决定 HMM 可信度；从未被挖 | src/zephyr/regime/regime_feature_builder.py + features/ 五件（index_sensor/overlay_features 等） |
| MOD-PA-007 RegimeMetaAllocator（实盘侧消费端） | F2 的另一半：实盘预算分配算法从未与回测侧对表；pf_alloc/core 14 件库边界 | src/zephyr/pf_alloc/core/ + 30_multi_strategy_concurrency §2.2 |
| 8 转换评分维度生产件（T1-T6/S1/S2 的 dim score 来源） | TRANSITION_CONFIG 的 bqs/rcs/vix_panic 等维度键由谁生产、阈值是否经 A 股校准（S2 vix 已校准至 30 有实证，其余"P1 阶段精调"状态未核实） | overlay_features.py + evolution_signals.py + TRANSITION_CONFIG 对照 |

## 6 封矿判定

- **本节点主体封批**：检测器五子模块数学四问全过（1.2）；三大发现（标签漂移传导/
  双轨语义分叉/供给件最后一公里）已 concrete 到 file:line+验收（§4 RSC-1~6）；
  降级链红蓝过审（1.6）。
- **未枯竭部分转子节点**（§5 三件）：特征管道、实盘消费端、转换维度生产件。
- 一句话结论：**检测器本体是全链最成熟的模块之一（数学对、披露齐、验证接口全），
  真正的险情在消费端——C1 用血泪换来的"别信 HMM 标签"教训，没有被 regime_overrides
  权重表和整装回测链继承：权重表仍在按标签下重注，回测链仍在把 Shrinkage 关在门外。**
