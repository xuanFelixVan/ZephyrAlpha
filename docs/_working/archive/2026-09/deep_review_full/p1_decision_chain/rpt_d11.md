---
ttl: task_bound
title: 深度审查报告——Overlay信号构建（D11）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：Overlay信号构建（D11）

- 状态: **已审**
- 级别: P0｜类型: 信号组装（8 转换 32 维评分→D01 overlay 注入→仓位语义）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/overlay_signals_builder.py:143(OverlaySignalsConstructor)`（849 行全文通读；关键协作文件 `overlay_features.py:537-571`（wyckoff 委托/回退支）、`risk_signal_builder.py` 交叉点实地核查）
- 生产调用方: `regime_feature_builder.py:416-432`（enable_overlay=True 时 build_shrinkage_schedule 消费 build_for_date → D01 `_run_overlay` → p_overlay 注入 7 维概率 → Shrinkage/ConfidenceSignal → budget）。overlay 直接改仓位语义的传导路径=本报告轴 C 主线
- 测试文件: `tests/regime/test_overlay_signals_builder.py` + `test_overlay_signals_builder_valuation.py`
- 变更热力: **18 次，域内第一热**（反复返工高危区画像成立）

## 1 对象快照

- 审查范围：8 转换维度组装/PIT 预计算/降级纪律/Phase 2c 四数据源接线/北向融合/涨跌停指标/板块指标。排除项：`overlay_features.py` 约 30 个评分函数本体逐个深查（长尾，抽审 wyckoff/valuation 委托面）；`risk_signal_builder` 归 D12。
- 材料包缺项声明：THRESHOLD_CALIBRATION_LEDGER 全清单未逐项核；S2 walk-forward 验证报告（MC p=0.87 未过）原文未回读。
- 测试覆盖概况：builder 层有专项测试；OVB-2 连板修复不变式有钉住测试（docstring 自证）。
- 事件史：OVB-2/3/4/5 四起已治理事件（连板虚增/北向断供/阈值欠账/指数冒充龙头）——本模块是 regime 域事故密度最高也是治理最密的对象。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **32 维 key 契约与 D01 TRANSITION_CONFIG 逐一枚举对齐（查无拼写漂移）**：S1 四键/S2 十三键/T1 三键/T2 一键/T3 七键/T4 一键/T5 两键/T6 一键=32，与 TRANSITION_CONFIG 各 stage 的 keys_gte/keys_or_gte 全集精确匹配；stub 集已空（P1-E3 后全激活）；"breakdown 必须含 stub key=0.0 否则 .get(key,0) 语义混为不满足"的契约注释与 D01 `_eval_stage` 缺 key 计 0 行为互证 | overlay_signals_builder.py:92-134 ↔ regime_detector.py:232-335,949-968 | 已查无 | 两清单并排枚举比对（本审查已做） |
| A | F-A2 **阈值校准欠账是 overlay 层的系统性债务（OVB-4 已声明）**：32 维评分函数的阈值未经 A 股本土 walk-forward 复推，而 D01 各 stage 门槛（60/40/total 120-250）直接作用于这些分数尺度——"分数尺度未标定+门槛硬编码"的组合使 overlay 触发率的合理性无第一性保证；好在欠账有一次性告警+ledger 披露+D01 侧危机门控兜底 | overlay_signals_builder.py:228-244; overlay_features.ALERT_UNCALIBRATED_THRESHOLDS | P2 | 实例化 ctor 观察 debt warning 内容；读 ledger 清单 |
| A | F-A3 **wyckoff 维 MVP 回退支在本层接线（D09 F-C1 的传导位）**：high/low 缺失→warning+s2_wyckoff_score 回退 MVP（可达 70>S2 confirm 门槛 60），证伪置零被旁路——本层有日志但无阻断，与"数据缺失降级 0.0"的自身纪律不一致（其他维度缺数据=0，wyckoff 缺数据=换一个可达门槛的替代判据） | overlay_signals_builder.py:285-290,393-395 ↔ overlay_features.py:556-571 | P1(与 D09 F-C1 同案) | high=None 造数据跑 _precompute，观察 cache["wyckoff"] 非 0 |
| A | F-A4 PIT 链审查通过：全维度末尾统一 shift(1)（:539-541）+build_for_date 取 loc[:dt].iloc[-1]（:217-222）+NaN→0.0 显式；派生序列（pct_change/hk_z/sector 指标）先算后 shift——无前视 | :539-541,217-222 | 已查无 | 抽查 capitulation/one_day_mainline 两维时序 |
| A | F-A5 HHI 口径混入下跌幅（|ret| 份额）：`share=abs(pct)/Σabs(pct)`——普跌日"跌幅最大板块"也贡献集中度，mainline（主线聚焦度）语义在下跌市失真；top_pct 取 max(实际涨幅) 可为负——负值喂 t3_mainline_score 的行为未核（overlay_features 长尾） | :741-753 | P3 | 全板块下跌合成数据跑 _compute_sector_metrics |
| B | F-B1 **OVB-2 连板虚增治本（正面确认+实证在案）**：事件行表 cumsum→交易日历对齐 run-length（cp 差 1 才接续），CH 实测均连板 12.44→6.24、≥7 连板日占比 94.5%→37.5%——A股口径事故的教科书式修复；晋级率/大面率同步按日历日重定义 | :763-847 | 已查无 | 读 OVB-2 注释+钉住测试 |
| B | F-B2 **OVB-3 北向断供出声（正面确认）**：港交所 2024-08-16 停发明细→融合项恒 0，`_disclose_hk_flow_staleness` 按空窗交易日数出声且不变式由测试钉住（防把披露误读成已停用）——checklist#6 静默死亡的规范处置 | :136-140,652-675 | 已查无 | hk 断更数据跑观察 warning |
| B | F-B3 **OVB-5 指数冒充龙头禁用（正面确认）**：leader_break 只吃个股涨停 cohort 大面率（leader_distress），缺数据降级 0.0 并告警——"宁降级不冒充"纪律 | :509-519 | 已查无 | — |
| B | F-B4 北向融合量纲假设：hk_adj=clip(z,±3)×0.5（±1.5pp）直接加到 inflow_pct 上——两源量纲可比性（主力净流入占比 pp vs 北向 z 映射 pp）无校准依据，属 E9 融合的约定值 | :700-715 | P3 | 读 P1-E5 设计依据（未回读，材料包缺项） |
| C | F-C1 下游传导链与爆炸半径：overlay_scores → D01 `_run_overlay`→record_transition→stage 判定→p_overlay 注入 r10/r11/r12（max 合成）→overlay 门控（#1≥1.0 屏蔽）→7 维合并→ConfidenceSignal（r10-r12 稀有态折扣 0.85）→Shrinkage→budget——**overlay 对仓位的实际影响被三重稀释**（门控+稀有折扣+4 档映射），"直接改仓位"的严重度被上游结构缓和；但 S1 confirm 的 shrinkage 锚定 0.3 是硬值（TRANSITION_CONFIG :296）——确认级危机信号直接锚定深收缩 | overlay_signals_builder.py 全文 ↔ regime_detector.py:290-300,539-548,786-823 | P2(口径) | 沿 S1 confirm 分数注入跑 D01 detect 对照 shrinkage |
| C | F-C2 消费方唯一（D05 enable_overlay 路），无第二消费方；risk_constructor 参数预留未用（:180-182 自认）——无静默多路传播 | :164-191 | 已查无 | grep OverlaySignalsConstructor 调用方 |
| D | F-D1 与 risk_signal_builder 的兄弟对称性：同为"预计算+切片"范式、共享 feature_builder 数据、降级哲学一致（0.0+WARN）——口径一致性好；wyckoff 回退支是两文件间的口径裂缝（F-A3） | :34-44 ↔ risk_signal_builder.py（rpt_d12） | 见 F-A3 | — |
| E | F-E1 静默失败面：全维度缺失路径 100% 带 warning（本审查逐分支核对 :339-529 共 25 处降级分支全有 log）；残余静默=①单日 NaN→0.0（:222，可接受）②_fb_call 吞异常留 warning（:548-560，可接受）③wyckoff 回退支（F-A3，P1） | :339-529 | 见 F-A3 | 分支清单核对 |
| E | F-E2 幂等/性能：_precompute 一次性+缓存，walk-forward 2800+ 日 O(1) 切片——设计自觉；重复调用 build_for_date 无副作用 | :35-37,195-224 | 已查无 | — |
| E | F-E3 时序攻击面：one_day_mainline/prev_top3 用 rank(method="first") 平局序——并列板块时结果依赖列序（sector_df 列序由数据源排序决定，未显式 sort）——平局日信号可能随列序漂移 | :749 | P3 | 列重排对拍 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | breadth_thrust（V 反转析取通路） | **对等已有（谱系）/立卡候选（阈值）**——广度脉冲识别危机后复苏起步的经典定义=Zweig Breadth Thrust（10 日均值 0.40→0.615 穿越触发）；本项目 S2 confirm 析取腿同谱系；**立卡**：以 ZBT 标准参数为锚做 A 股本土阈值校准（挂进 OVB-4 ledger） | [Keytrade Bank: Zweig Breadth Thrust](https://www.keytradebank.be/en/our-blog/zweig-breadth-thrust)（Keytrade，指标定义；Zweig 原始 1970s 谱系） |
| 2 | capitulation 多过滤器（衰减加权/下影线/量过滤） | **对等已有（工程化超前期）**——恐慌抛售识别的多维聚合是常见实务；本项目 walk-forward 终选组合（WFE 3.44/fp60 0.8%）但 MC p=0.87 未过已在注释如实注记——诚实披露优于常见做法 | 项目内=reports/2026-08-29-s2-walkforward-validation.md §七（注释自引，仓内可查）；外部谱系=capitulation/panic bottom 度量（无单一定源如实记） |
| 3 | 关键词词典 NLP 情感（policy/bad_news_flat） | **立卡候选（低配现状）**——词典法是 NLP 情感 MVP 谱系低端；A 股政策语料的 LLM/FinBERT 升级路径存在但成本高；当前 MVP+降级 0.0 纪律可接受，接入面已留 | 词典法谱系公共域（Loughran-McDonald 金融词典为学术标准，项目未表明采用何种词典——挂疑问） |

## 4 缺陷清单（按严重级）

- **F-A3（P1，与 D09 F-C1 同案）wyckoff 回退支过 S2 门槛**：现状=high/low 缺失日 wyckoff 维换 MVP 判据（70 可达）继续参与 S2 confirm 析取 → 证据=三锚点 → 影响=危机复苏 confirm 可由未验证判据假触发（RECOVERY p_overlay 注入→假底加仓方向）；爆炸半径=S2 confirm（在产 overlay 链）→ 建议修法=回退支改降级 0.0（与其余 25 个维度纪律对齐）或纳入证伪披露；工程量小 → 验证法=high=None 复现非零 wyckoff。
- **F-A2（P2）阈值标定系统性债务**：OVB-4 已声明，建议收口时给 ledger 定清偿批次（S2 六维优先——直接挂 confirm 门槛）→ 验证法=ledger 清单核对。
- **F-C1（P2）传导链稀释系数文档化**：三重稀释（门控/稀有折扣/映射）使 overlay 实际弹性远小于分数直观——建议在 capability card 记录传导系数，防后续"调分数=调仓位"的线性误读 → 验证法=S1 confirm 场景对拍。
- **F-A5/B4/E3（P3）**：HHI 下跌混入、北向融合量纲约定、板块平局序——常规队列。

## 5 挂起疑问

1. THRESHOLD_CALIBRATION_LEDGER 全清单与 OVB-4 五项的清偿优先级——需 Owner 定批次（S2 直挂门槛六维 vs T 族）。
2. policy/bad_news_flat 关键词词典的词表来源与 PIT（新闻回填是否 as-of 安全）——NLP 管道（P1-E3）本体未审，研报快照冒充历史是 checklist#7 在案模式，建议对 news_sentiment 管道补 PIT 审计。
3. `_compute_t3_inputs` 的 money_flow 主力净流入口径（全市场 avg vs 流通市值加权）未核——量纲注记归数据域。

## 6 完备性自评

- 六轴全查：A（32 维契约枚举+PIT+HHI+回退支）、B（四数据源接线+三起 OVB 治理确认+量纲假设）、C（唯一消费方+三重稀释传导链）、D（与 D12 范式对称性）、E（25 处降级分支逐处核对全带 warning；静默面=wyckoff 回退支+平局序）、F（3 条带来源）。
- 长尾清单：①overlay_features 约 30 个评分函数本体（capitulation/breadth_thrust/three_yang 等已抽审委托面，公式级深查未做——独立对象候选）；②news_sentiment NLP 管道 PIT；③S2 walk-forward 验证报告原文。
