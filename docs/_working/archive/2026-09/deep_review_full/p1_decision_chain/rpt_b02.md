---
ttl: task_bound
title: 深度审查作业簿——向量化回测引擎
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：向量化回测引擎（B02）

- 状态: **已审**
- 级别: P0｜类型: 引擎
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/implementations/vectorized_engine.py:160`（DefaultBacktestEngine）；BacktestConfig :103
- 生产调用方: shrinkage_engine、regime_validation/c1_runner、services/scheduler、pf_core/strategy_engine/framework_composer+strategy_runner、trading/validation/ablation、experiment_tracking/vectorized_adapter 等 15+ 处（grep 详单在案）
- 测试文件: **无专属文件**（[TESTS] 头空，vectorized_engine.py:16）；实际由 tests/backtest/test_bt_financial_correctness_p0.py（31 断言项）+test_h3h4_cash_pit_exec_chain+test_cost_model_wiring+metamorphic s11/s12+lane_k 等 20 文件集成承载
- 备注: 任务指定"无专属测试缺口重点审"——结论见 §2 A.3 行

## 1 对象快照

- 范围：run() 主循环（T+1 执行滞后/PIT 标的池/流动性约束/拒单披露）、_normalize_day_signals 满仓归一、PitUniverseProvider、EXECUTION_MODEL_CAPABILITY 披露表。
- 排除项：MatchingEngine 细节归 B03；metrics 归 B01 报告；shrinkage_engine 只按继承关系核对。
- 测试覆盖概况（重点审）：**无同名专属测试文件，但 P0 语义被 test_bt_financial_correctness_p0.py 定向锁定**——same_bar 硬断言(:79)、次日 open 成交价(:112-121)、末日信号永不成交(:123)、参与率收缩精确值(:150-158)、冲击调价 rel=1e-9(:160-187)、无 volume 列旁路(:199)、universe 过滤/降级/合成码豁免(:232-316)、合理性护栏(:325+)。断言强度高（精确值+rel=1e-9），非绕过型 fixture。缺口：BacktestConfig 开关组合矩阵（lag×liquidity×universe×sanity）无正交单测；`_get_day_signals` KeyError/TypeError 吞没路径（:570-572）零测试。
- 材料包缺项声明：运行时证据包未取；数据画像未做（依赖 load_history 出口，归 TDM 侧对象）。
- 变更热力：**41 commits——本批 9 对象最高**，高危返工区，末次 2026-09-16。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 前视偏差专项（A股口径）：T+1 硬断言在且 fail-closed——execution_lag_days<1 且未显式 allow_same_bar_execution 即 raise；T 日执行 T-lag 信号、成交价=T 日 open 优先/close 兜底（T-lag 收盘信号→T 开盘，零前视；open 缺失回退 T 收盘仍非前视但口径混合） | vectorized_engine.py:239-246,291-303；engine_base.py:158-166 | 已查无破口（模型正确） | test_same_bar_hard_assert + test_next_bar_executes_at_open_price 实证 |
| A | 执行价混合口径：同日内部分标的按 open、缺失者按 close 成交——同一信号日两种成交基准，成本/收益归属不纯（非前视，但漂移源） | vectorized_engine.py:292-295 | P2 | 造 open 缺一行面板对比全 open 口径收益差 |
| A | `_get_day_signals` KeyError/TypeError 静默吞→rows_absent++→当日不下单：信号面板 dtype/布局漂移=系统性减仓，无 warn（仅产物 stats 可事后见） | vectorized_engine.py:560-572 | P2 | 传 symbol-major 信号面板跑 run，看 last_signal_row_stats.rows_absent 与 trades=0 |
| A | 数学四问：满仓归一 Σ→1（:957-987）与 H3-C 绊线披露一致；佣金/滑点经 MatchingConfig 单一真源（:180-183）；年化 252（metrics）与全仓 252 一致（grep 244 零命中——"244 vs 252 域内漂移前科"本轮**已查无**复发） | vectorized_engine.py:957-987；grep "244" src/zephyr/backtest/ = 0 hit | 已查无 | grep 命令见锚点 |
| A.3 | 无专属测试文件但 P0 语义有强集成测试（见 §1）；缺 BacktestConfig 正交开关矩阵与异常路径测试 | vectorized_engine.py:16（[TESTS] 空）；test_bt_financial_correctness_p0.py:79-330 | P2 | 试点 mutation（policy §8 立卡项）验证测试敏感度 |
| B | PIT 标的池三重 fail-open：listing_registry 空表/CH 故障→不过滤（:917-925）；ST 腿故障→不剔 ST（:866-868）；stk_limit provider 故障→规则兜底。"宁可漏剔不误剔"方向已声明，但幸存者偏差守卫在数据故障期整体静默退役，仅 warn 一次 | vectorized_engine.py:836-931;907-925;865-868 | P2 | 断 CH 后跑含已退市标的回测，确认无拦截告警计数 |
| B | volume 无列时流动性约束旁路仅 info 级一次性日志（:285-289）——容量失真风险显影弱 | vectorized_engine.py:283-289 | P3 | 删 volume 列跑 run 查日志级别 |
| C | 拒单三腿披露（last_signal_row_stats/last_skipped_fills/EXECUTION_MODEL_CAPABILITY）由整装回测透传 artifact——静默传播点已制度化封堵（H3-C/H4-D）；消费方 framework_composer 需抽查透传完整性（长尾） | vectorized_engine.py:443-485,84-99 | 亮点 | grep last_skipped_fills src/zephyr/pf_core/ |
| D | 四个桥接方法与 event_driven_engine 逐行重复 ~140 行（同 B01 轴D） | vectorized_engine.py:609-739 | P2 | diff 两文件 |
| D | shrinkage_engine 继承 DefaultBacktestEngine 复用主循环（继承式兄弟，口径同源无第二实现）——已查无平行实现漂移 | shrinkage_engine.py 类声明 | 已查无 | grep 第二处 generate_fills 调用 |
| E | run() 重入安全：绊线每 run 重置（:272-274），_results 累积可复用——重跑幂等性 OK；prev_close 跨日结转逻辑正确（:360） | vectorized_engine.py:272-274,360 | 已查无 | 两次 run 结果互不污染 |
| E | sanity_guard 读 config 直接属性（:402），event_driven 用 getattr 兜底——同守卫两引擎防御深度不一（config 类型漂移时 vectorized 会 AttributeError） | vectorized_engine.py:402 vs event_driven_engine.py:357 | P3 | 传无 sanity_guard 属性的 config |

## 3 SOTA 对照

- T+1/执行滞后建模：**对等已有且更强**——vectorbt 惯例 signal.shift(1)（约定式，漏 shift 无拦截）；本引擎 fail-closed 硬断言+显式豁免位，强于业界惯例。（来源：vectorbt Tutorial: avoiding look-ahead bias, quantt.co.uk, 2026；Implementation Risk in Portfolio Backtesting, arXiv:2603.20319, 2026）
- 容量约束：**对等已有**——参与率上限+A-C 冲击与 VectorBT.volume_limited/Nautilus 佣金模型同构；分层滑点标定（2.34~7.24bp ADV 五分位）比业界固定 bps 更进一步。（来源：The Python Backtesting Landscape, python.financial, 2026）
- 执行模型能力披露表：**立卡候选（反向输出）**——EXECUTION_MODEL_CAPABILITY 式"未建模清单随产物披露"在开源引擎中无先例，可作项目对 SOTA 的贡献点。（来源：同上两文检索面内未见同类）

## 4 缺陷清单

1. **[P2] 执行价 open/close 混合口径**：同日缺 open 的标的按 close 成交，收益归属不纯且不可配置。建议修法：口径入 BacktestConfig（strict_open_only=True 时缺 open 拒单计数进 skipped_fills）。验证法：§2 轴A 行。
2. **[P2] 信号面板异常静默吞没**（:570-572）：dtype/布局漂移=无交易，只有产物 stats 事后可查。建议修法：rows_absent 首次非零时 warn 一次。验证法：symbol-major 面板跑 run。
3. **[P2] PIT 守卫三重 fail-open 无显影计数**：建议修法：降级事件计数进 last_skipped_fills 同款产物腿。验证法：§2 轴B 行。
4. **[P2] 无专属测试文件**（header [TESTS] 空）：P0 语义有集成测试兜住，但开关矩阵/异常路径裸奔。建议修法：建 test_vectorized_engine.py 收编 test_bt_financial_correctness_p0 之外的正交用例（仅加测试，勿动源）。验证法：运行 `python -m pytest tests/backtest/test_bt_financial_correctness_p0.py -q`（本批已验证关联测试全绿）。
5. **[P2] 与 event_driven 桥接方法双份承载**：同 B01 §4.5。
6. **[P3] sanity_guard 防御深度不一**（:402 直接属性访问）；volume 旁路 info 级日志弱（:285-289）。

## 5 挂起疑问

- enable_stk_limit_provider 默认 True：CH 不可达环境每回测日一次 warn 降级，测试噪音与生产降级信号混杂——是否按环境分级待 Owner 裁定。
- EXECUTION_MODEL_CAPABILITY 的透传完整性（framework_composer 是否三腿全带）未逐行核（长尾登记）。

## 6 完备性自评

六轴全查。长尾：①shrinkage_engine 覆写方法逐行 diff 未做；②framework_composer 透传链；③load_history→market_units 归一出口（INV-UNIT-001 上游）归 TDM 侧对象审；④运行时证据包缺。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
