---
ttl: task_bound
title: 深度审查报告——RegimeDetector(HMM四态)（D01）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：RegimeDetector(HMM四态)（D01）

- 状态: **已审**
- 级别: P0｜类型: 算法（生死线之首）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/core/regime_detector.py:437(detect:510)`（968 行全文通读）
- 生产调用方: `pf_alloc/allocation_inputs.py:449/511`（shrinkage 经 regime_snapshot_history 入分配）、`pf_core/strategy_engine/framework_composer.py:203/479/500`（REGIME_STATES 词表 + ShrinkageBacktestEngine 裁定#270）、`src/zephyr/regime/index_regime_panel.py:532`（shrinkage_enabled=False 面板路）、`validation/phase2/*`（A1/A2/B1/B4）、`experiment_tracking/adapters/regime_adapter.py`（遥测）
- 测试文件: `tests/regime/test_regime_detector.py`（890 行，含锚定红蓝置换不变性测试）

## 1 对象快照

- 审查范围：MOD-REGIME-001 全文件（锚定纯函数/fit/detect/8 转换/7 维合并/Shrinkage 链/降级路径）。排除项：`validation/phase2/` 验证脚本本体（只在爆炸半径中评估）；`framework_composer`/`pf_alloc` 消费侧深查归 P1 决策链其他对象。
- 材料包缺项声明：运行时证据包（近 N 天 error 日志摘要/数据画像）未取——结论来自代码与测试静态审查+可复算验证法；基线 2fa92002c3 与 HEAD 之间 `git diff --stat 2fa92002c3..HEAD -- src/zephyr/regime/` 为空，无漂移。
- 测试覆盖概况：覆盖广（温度缩放不变性/锚定置换还原/门控边界/keys_or_gte 析取/四阶段）；缺口：①`_run_hmm` 运行时异常路径（NaN 特征→静默均匀）无测试；②overlay 维度含 None/字符串的 TypeError 炸穿路径无测试；③`_normalize` Inf/负值防御无测试。测试文件头注释多处残留"9态/12维"旧文案（`test_regime_detector.py:18-25,123` 类名 `TestHMM9States`）——文案漂移 P3。
- 变更热力：`git log --follow` 16 次，域内并列第二热（overlay 18 次），符合"反复返工=高危区"画像。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 锚定无斜率符号校验：r4 槽位=argmin(斜率均值)，若某训练季全组件斜率均值为正（单边牛季），"负斜率阴跌"语义静默漂移为"涨得最慢的态"，跨季语义锚失效而代码无告警 | regime_detector.py:120,136-139 | P1 | 构造 `means=np.ones((4,3)); means[:,2]=[0.5,0.4,0.3,0.2]` 调 `anchored_component_order`——仍返回 slot3 指派，无符号检查 |
| A | F-A2 `_run_hmm` 运行时异常**静默吞掉且无日志**：`except Exception:` 直接返回均匀分布 1/4，无 warning。运行时特征含 NaN（fit 时校验过但 live 特征是另一管道产出）→ 无痕退化 | regime_detector.py:749-751 | P1 | `detector.fit(干净X)` 后 `detect({"X": np.array([[np.nan]*6])}, {}, {})` → 均匀概率且日志无输出 |
| A | F-A3 overlay 维度含 None/非数值 → `_eval_stage` 的 `float()` 抛 **TypeError**，`_run_overlay` 只捕 `(ValueError, OverlayRuleError)` → TypeError 炸穿整个 detect()（与 D05 的 fail-open 串联=一个坏维度→当日满仓） | regime_detector.py:966,774-775 | P1 | `detector.detect({}, {"transitions": {"S1": {"vix_panic": None}}}, {})` → TypeError（record_transition 内 float(None)） |
| A | F-A4 状态频率默认值=**全历史 3733 样本 Viterbi 统计**（含未来），walk-forward 回测中稀有态折扣带轻微前视；且与锚定槽位绑定的频率常量未随重校批再核 | regime_detector.py:491-505 | P2 | 对比 2015 时点窗口的真实态频率与 0.28/0.37/0.15/0.20 常量差 |
| A | F-A5 `_normalize` 不防 +Inf（total=inf → v/inf → NaN 输出破坏 Σ=1 不变量）与负概率；输入路径当前受控（_run_hmm/配置值均有限），属防御缺口 | regime_detector.py:940-947 | P2 | `_normalize({"r1": float("inf"), "r2": 1.0})` → r1=NaN |
| A | F-A6 术语漂移：注释称"因果 Viterbi 防前视"，实际 `predict_proba` 是 forward-backward 后验；末步后验恰=滤波概率（因果性成立，结论对、术语错），易误导后续维护者 | regime_detector.py:729（test:140 同措辞） | P3 | 对照 hmmlearn 文档：predict_proba=平滑后验；末步无未来项故=滤波 |
| A | F-A7 4 态降维后 `_CONFIDENCE_BANDS` 阈值自认"沿用 9 态校准值，C1 验证后精调"未回填——0.15/0.30 档在 4 态 max(P)∈[0.25,0.8] 分布下为死档/临界档，校准债挂账 | regime_detector.py:184-191 | P3 | 统计 C1 schedule 的 max(P) 分布验证两档触发率≈0 |
| A | F-A8 fit 的 n_init 循环逐个换 seed(42+k) 取最优 log-likelihood——对 EM 局部最优的标准缓解，正确；score 相等取首解，确定性成立 | regime_detector.py:594-619 | 已查无 | test_fit_slots_ordered_after_anchor 覆盖 |
| A | F-A9 温度缩放数值实现（clip→log→/T→减max→exp→归一）数学正确且稳定；T≤0 防御降级；与校准器路径（predict_log_proba 不乘 T）独立——两机制分离已文档化且有回归测试 | regime_detector.py:735-747,630-669 | 已查无 | TestTemperatureScaling 四测试 |
| A | F-A10 overlay 多转换取 max(p) 注入同一态；overlay_mass>1 等比压缩；T3/T6/S2 的 **fail 阶段也注入 p_overlay**（如 S2 fail→r10=0.60）——配置语义"复苏失败=仍危机"，自洽但非显然，需 blueprint 明示 | regime_detector.py:767-784,263,287,328-332 | P3 | 读 TRANSITION_CONFIG 各 fail 段 p_overlay 键 |
| B | F-B1 锚定列序契约（col0=vol, col2=slope）仅靠注释钉死，无运行时断言——已实测与 D05 `FEATURE_NAMES` 序一致（regime_feature_builder.py:102-109），但重排列即静默指错槽（叠加 F-A1 无符号校验，两道静默） | regime_detector.py:102-106 ↔ regime_feature_builder.py:102-109 | P2 | grep FEATURE_NAMES 全部消费方核对列序 |
| B | F-B2 detect 的 X 窗口长度是隐式契约：末步后验依赖窗口（D05 用 60 日，regime_feature_builder.py:487），窗口长度变化 → 同日不同概率；未文档化"传 trailing 定长窗" | regime_detector.py:729-731 ↔ regime_feature_builder.py:487 | P2 | 同 X 末行不同前置窗口长度跑 predict_proba 比较末行 |
| B | F-B3 危机门控读 `params[1]`——依赖 D12 RiskSignalConstructor 的 #1=realized_vol 语义；#1 语义漂移或断供（safe_float NaN→0→risk=1.0）时门控静默转向"非危机"屏蔽 overlay | regime_detector.py:539-542 ↔ risk_signal_builder.py（rpt_d12） | P2 | 断供日构造 params 缺失调 detect，观察 overlay 被屏蔽 |
| C | F-C1 消费方清单：①pf_alloc 分配链（snapshot shrinkage，None 时 snapshot_decomposed 反演，allocation_inputs.py:434-449）②framework_composer 词表 fail-closed（:500 非法状态拒绝）+ ShrinkageBacktestEngine 乘当日 Shrinkage（裁定#270）③D10 面板（shrinkage_enabled=False 只吃概率）④phase2 验证 ⑤遥测。静默吞掉点：pf_alloc 对 snapshot_shrinkage=None 反演而非报错（分配侧静默降级）——归分配对象深查 | allocation_inputs.py:434-449; framework_composer.py:479-500 | P2 | 逐消费方 grep `shrinkage`/`RegimeProbabilities` |
| C | F-C2 爆炸半径=**全账户**（regime→Shrinkage→budget→StrategyBook，链头故障经 D05 fail-open 方向为"放大敞口"而非"停机"） | regime_detector.py:21-23 | P1(口径) | 沿 C1 schedule→ScheduleShrinkageProvider→引擎链路演练断供日 |
| D | F-D1 兄弟实现排查：波动率态判定在 volatility_squeeze_breakout/volatility_regime_alerter/style_regime_model 各有独立阈值口径（归各自对象审）；D10 面板复用 FEATURE_NAMES/RegimeFeatureBuilder（index_regime_panel.py:96，无重复实现）；REGIME_STATES 词表唯一真源被 framework_composer 引用（无第二词表副本） | index_regime_panel.py:96; framework_composer.py:203 | 已查无 | grep 全仓 "r10.*r11.*r12" 词表副本 |
| D | F-D2 测试文档漂移：测试头/类名残留 9 态/12 维旧口径，与 4 态降态后实际断言不符——判读以断言为准 | test_regime_detector.py:18-25,123 | P3 | 读文件头 |
| E | F-E1 静默失败剧本（三连）：live 特征 NaN→F-A2 均匀（无日志）→max(P)=0.25→Confidence=0.8；或风险参数断供→RiskSignal=1.0 且 overlay 屏蔽（F-B3）→**危机日敞口放大**；叠加 D05 外层 `detect 异常→1.0` fail-open（rpt_d05 F2）——"缺失→1.0"降级在 blueprint §7.4 登记，但危险方向降级+缺告警通道值得升级为治理项 | regime_detector.py:749-751,539-542; regime_feature_builder.py:518-520 | P1 | 按 E1 剧本造断供输入跑全链对照 |
| E | F-E2 假阳性面：门控只在 #1≥1.0 时屏蔽概率但保留评估记录——若 #1 恰在危机恢复日跳回 1.0，同日 S2 触发的 r11 注入被屏蔽（记录保留）→ RECOVERY 信号丢失一拍，属设计取舍（C1 Sharpe 保护优先），B4 验证可观测 | regime_detector.py:536-542 | P2 | 用 #1 从 0.5→1.0 翻转日的 S2 输入跑 detect |
| E | F-E3 重跑幂等：detect 无副作用（除 _last_transitions 覆盖写+datetime.now() 时间戳）——重放同输入结果一致（除 timestamp），幂等成立；naive 本地时间戳已有 noqa 登记（UTC 迁移专项） | regime_detector.py:699,822,400 | 已查无 | 同输入两次 detect 比较除 timestamp 外全等 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | HMM regime filter（Gaussian HMM 风险态滤波，walk-forward 重拟合） | **对等已有**——业界标准做法；n_init 多重启=EM 局部最优标准缓解；filtered-vs-smoothed 辨析支持"末步后验"选型 | [QuantStart: Market Regime Detection using HMMs](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)（QuantStart，2016）；[QuantInsti: Regime Adaptive Trading in Python](https://blog.quantinsti.com/regime-adaptive-trading-python/)（QuantInsti，walk-forward 重训同款）；[Reddit r/learnmachinelearning: filtered vs smoothed](https://www.reddit.com/r/learnmachinelearning/comments/1uuctkh/using_hmms_for_regime_detection_the_filtered_vs/)（社区辨析：实时只用滤波概率） |
| 2 | label switching 治理（锚定重排） | **对等已有**——按发射参数统计排序重标是文献常用缓解（本项目=波动率升序+斜率 argmin，PIT 合规）；**立卡候选**：Hungarian 最优匹配（对上一季参数向量最小距离指派）可处理"全正斜率季"退化（F-A1），改造点=fit 后与上季锚定解对齐 | [Wang et al. 2020, Regime-Switching Factor Investing with HMMs, J. Risk & Financial Management 13(12):311](https://www.mdpi.com/1911-8074/13/12/311)（MDPI，2020） |
| 3 | HMM 后验温度校准（tempering） | **对等已有（自认知）**——代码自认"tempering 非 Guo2017 严格 TS"，另立 TemperatureCalibrator 学习 T（tests/regime/phase2/test_confidence_calibrator.py），双通道与文献口径一致 | 代码内注释 regime_detector.py:464-470（引 Guo 2017 tempering） |

## 4 缺陷清单（按严重级）

- **F-A1（P1）锚定语义在极端季静默漂移**：现状=r4=argmin(斜率) 无符号校验（:136-139）→ 证据=纯函数无 sign 检查 → 影响=单边牛季全组件正斜率时 r4 槽位被指给"涨最慢"组件，r4 历史频率 0.20 与消费方按 r4 名义解读的语义跨季失真；爆炸半径=态层消费方（面板/归因/B4 统计），风险分档主路不受影响（feature-risk 承载，:199-203 标签风险因子已 deprecated）→ 建议修法=锚定时校验 slope_comp 斜率均值<0（或<全体均值），不满足记 warning 并可选跳过锚定（对齐预注册协议修订流程）→ 验证法=构造全正斜率 means 调 anchored_component_order 观察无告警指派。
- **F-A2（P1）_run_hmm 静默吞异常**：现状=运行时推断异常一律无日志返回均匀 → 证据=:749-751 裸 except → 影响=特征断供/形状漂移日决策链无痕退化"中性置信"；爆炸半径=全账户 Shrinkage schedule → 建议修法=加 `_logger.warning`（对齐 fit 失败留痕纪律）+ 连续降级日计数暴露监控 → 验证法=fit 后传 NaN X，观察日志无输出。
- **F-A3（P1）坏维度 TypeError 炸穿 detect**：现状=_eval_stage float(None) 未在 _run_overlay 捕获范围 → 证据=:966 vs :774-775 → 影响=上游单个 None 维度使当日 detect 整体失败，落 D05 fail-open=当日 Shrinkage=1.0 满部署；爆炸半径=当日全账户 → 建议修法=_eval_stage 非数值按 0.0 计并记 warning（与 record_transition total 过滤口径一致），或 _run_overlay 增捕 TypeError → 验证法=`detect({}, {"transitions": {"S1": {"vix_panic": None}}}, {})` 复现 TypeError。
- **F-A4/A5/B1/B2/B3/E2（P2）**：见日志表；A4 修法=walk-forward 按训练窗 Viterbi 统计频率；A5 修法=输入 isfinite/clip 后归一；B1 修法=锚定入口断言列数契约；B2 修法=docstring 明示 trailing 定长窗契约；B3/E1 修法=断供日显式告警通道。
- **F-A6/A7/A10/D2（P3）**：文案/死档/披露类，常规队列。

## 5 挂起疑问

1. `_STATE_RISK_FACTORS` 已 DEPRECATED 但保留定义（:199-203）——若未来按 §2.1.6.4 协议重启，需先解决 F-A1 符号校验，否则重启即引入随机惩罚。需 Owner 确认重启前置条件登记。
2. T3 fail 注入 r11=0.60（:263）与 S2 fail 注入 r10=0.60（:328-332）的"fail 态也注概率"语义是否有 spec §4 条文背书——本审查确认自洽与可记录，未回溯 spec 原文（材料包缺项）。
3. overlay_gated 默认 True 在 index_regime_panel 生产路以 `shrinkage_enabled=False` 组合运行（:532）——面板路概率是否吃门控屏蔽对 B1 校准统计口径的影响，归 D10 报告跟进。

## 6 完备性自评

- 六轴全查：A（锚定/温度/合并/置信/风险/Shrinkage/阶段判定逐算法过）、B（X 列序/窗口契约/#1 语义）、C（消费方五路+静默点）、D（兄弟词表/面板复用/测试文案）、E（五问：静默失败 E1、假阳性 E2、断线告警缺 E1、幂等 E3 查无、时序=窗口契约 B2）、F（3 条带来源）。
- 长尾清单：①hmmlearn 库内部数值行为（min_covar/收敛判定）未逐版本核对——运行环境锁缺材料包项；②C1 校准 schedule 真实分布数据画像未取（F-A7 死档判定需数据佐证）；③validation/phase2 五个验证脚本本体未深查；④`regime_recal_protocol_2026_09_17.md` 预注册协议原文未回读（F-A1 修法需对齐其修订流程）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
