---
ttl: task_bound
doc_type: report
title: 深度审查报告——M02 次日八态预测（NextDay8StateForecaster）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：M02 次日八态预测（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 算法（一阶马尔可夫 8 态概率分布）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/ml_forecast/next_day_8state_forecast.py:78(NextDayState)(:234 forecast_next_day)`
- 生产调用方: 真实且多——plan_engine/scenario_probability_model.py、plan_engine/intraday_tomorrow_forecast.py（先验注入）、regime/market_forecast_fusion.py、regime/index_market_brief.py、frontend/dashboard/warroom.py、signal_ashare/market_state_sensor.py
- 测试文件: tests/signal_ashare/ml_forecast/test_next_day_8state_forecast.py（存在，184 行）
- 变更热力: 2026 年 4 commits（低热）
- 材料包缺项: 000300 指数真实数据画像缺（除权影响以口径走查判定）

## 1 对象快照

K 线→8 态分类→转移计数（Laplace α=1）→行归一→幂迭代平稳分布 π→(1−blend)·行+blend·π 归一→概率分布+置信度（top_prob×支持度因子）。边界声明：只出概率不出信号（90 号 §7 裁定）。排除项：analysis_utils 的 resolve_*（已走查，注入缺省 ch_reader.query ✓）；下游风控消费（轴 C 以调用方清单交付）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| B | **symbol 直插 SQL 无转义/白名单**：_SQL_INDEX_KLINE format 直接嵌 symbol，公共 API 可传任意串；单引号即破坏查询（ch_reader 只读，危害=错误/DoS 非注入提权，但违反参数化纪律） | next_day_8state_forecast.py:66-71, 316 | P2 | forecast(symbol="x' OR '1'='1") 观察 TSV 解析异常/空查询 |
| A | **除权/日期缺口不设防**：classify_daily_state prev_close=前一行 close（:177-183）；000300 为价格指数，成分股除息日指数自然回落→GAP_DOWN 类误判（系统性小偏置）；load_index_bars 不校验 trade_date 连续性，停市日/缺行均按相邻转移计入 | :151-165, 177-183, 318-335 | P2 | 取 5-6 月分红高峰期实跑，统计 GAP_DOWN 频率 vs 其他月 |
| A | 数学四问：Laplace 平滑行归一 ✓（:196-203，α=0 时零行兜底 :258-260）；幂迭代 π=π×M 每步归一化兜底 ✓（:206-231，收敛 1e-12/1000 轮，8 态成本可忽略）；blend 钳制 ✓（:255）；confidence=top_prob×min(1,support/30) ✓（:268-270，support 计数 i≤len-2 正确排除当日自身）；Σp=1 归一兜底 ✓——**递推/初值/归一全查无** | 各锚点 | ✓ 查无 | 单测+走查 |
| A（边界） | 空 states→ValueError ✓（:247-248）；单点/全同态序列→均匀转移（Laplace）✓；top_state 平票取 Enum 定义序（确定性）✓ | :247, 196-202, 264 | ✓ 查无 | 造 30 个同态序列跑 forecast |
| B | load 解析跳过不可解析行仅 warning（:331-332）——坏行静默缩短历史，若系统性坏行（如字段错位）历史被无声截断 | :318-334 | P3 | 造 50% 坏行看 bars 减半无告警 |
| C | 下游消费概率分布/置信度直接使用，无校准审计（confidence 未经 Brier/可靠性曲线标定）——90 号 §7 裁定已限定"不出点位"，风险受控 | :270-277; 消费方清单 | P3 | 抽 warroom/scenario 消费点走查 |
| D | **MATURITY=production vs 阈值"初拟待实盘标定"**（docstring :29 + ForecastConfig :108-115 自认）——标注漂移 | :7, 29, 108-115 | P3 | 对读 |
| A.3 | 测试存在；断言强度未逐条审（本批时间盒）——记长尾 | tests/.../test_next_day_8state_forecast.py | P3 | 抽读断言 |

## 3 SOTA 对照

- 一阶马尔可夫+Laplace 平滑+平稳分布混合为教科书口径（对等已有，无需外部源；与本仓 91 号 memo 路线裁定一致）。
- **立卡候选**：中文卖方金工对 A 股日内状态转移普遍用隐马尔可夫/regime 条件转移矩阵（中文学界独立矿脉）——本批检索预算已用于 WQ101/保形/TA-Lib，**受阻未搜**；登记为 M02 后续标定批的对照矿脉。

## 4 缺陷清单

1. **P2 symbol SQL 拼接**：建议参数化或白名单校验（symbol 形态 ^[0-9]{6}$）。验证法：§2 B-1。
2. **P2 除权/缺口偏置**：指数分红季 GAP 误判为系统性小偏置，长期转移矩阵带噪。建议：load 侧日期连续性校验+分红季标记，或换后复权指数序列。验证法：§2 A-2。
3. **P3 组**：坏行静默、confidence 未标定、production 标注漂移。

## 5 挂起疑问

- 000300 是否有可用的总收益（total return）版本数据源——决定除权偏置的修法方向（换源 vs 打标）。

## 6 完备性自评

六轴全查（F 部分受阻记）。数学四问全查 ✓（马尔可夫链递推/初值/归一/边界逐项）。长尾：①测试断言强度逐条审查（时间盒）；②_ STATE_INDEX 依赖 Enum 定义序的脆弱性（重排 Enum 即静默换矩阵行列序——有单测兜底则可控）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
