---
ttl: task_bound
title: 深度审查报告——市场九宫格传感（S05）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：市场九宫格传感（S05）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/market_state_sensor.py:90`（MarketGridState/主逻辑）/ `:241`（sense_market_state 纯函数）/ `:344`（MarketStateSensor.sense DB 封装）
- 生产调用方: **零**（grep MarketStateSensor/sense_market_state 全仓 src/scripts 仅自身；S01 daily_condition_sensor 仅 docstring 提及分工）
- 测试文件: tests/signal_ashare/test_market_state_sensor.py（172 行 20 用例，已审）
- 备注: 关键发现已经 Python 3.12.8 实跑复现（n=60 崩溃）

## 1 对象快照

- **范围**：`market_state_sensor.py` 全文 352 行——10 号 regime spec §2.1 规则版：tanh 合成趋势分（20 日收益×MA20/MA60 偏离等权）∈[-1,1] × 已实现波动率 250 日分位 → 3×3 九宫格单状态 + 置信度；纯函数与 DB 加载隔离。
- **排除项**：regime/ HMM 检测器（MOD-REGIME-001，声明的交叉验证兄弟件，另对象）；daily_condition_sensor（S01 已审，分工声明一致）。
- **测试覆盖概况**：趋势分方向性/边界、分位数单调与界、九宫格全组合、假 query_fn 端到端、空查询 fail-closed。信任度：**信任（盲区=min_history 边界恰好踩中实现漏洞）**。
- **材料包缺项声明**：无运行时证据包（零调用方）；market_index_kline 缺档率未画像（列入挂起疑问）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **min_history 与 long_window 差一不一致（实跑复现）**：sense_market_state 门槛 n≥min_history=60 放行，随后 compute_trend_score 要求 n≥long_window+1=61 → **恰好 60 样本必崩**，且报错信息指向 compute_trend_score 而非配置矛盾；docstring :251 只声明"min_history（或波动率窗口+1）"未提趋势窗口+1 | market_state_sensor.py:136（min_history=60）vs :170-171（long_window+1 守卫）、:255-256 | **P2** | 已实跑：`sense_market_state([3000.0+i for i in range(60)])` → ValueError"closes 长度 60 不足 long_window+1=61"；n=61 正常 |
| A | 短样本波动率分位系统性偏高：样本刚过门槛时 trailing 窗仅 ~40 点且当前点含入 → 分位≥1/40；递增振幅序列可到 1.0 → HIGH；缓解=confidence 的 sample_factor 折扣，但 HIGH 分类本身可能已误导（分位语义在短窗上不稳健） | market_state_sensor.py:201-204（trailing 含当前点） | P3 | `compute_vol_percentile([...60 点...])` 看 len(trailing) 与分位 |
| A | 常数序列分位=1.0 → 判 HIGH vol（零波动判高波动）：docstring 自认"常数序列分位为 1.0"——数学自洽（含等值并入）但语义反直觉；真实指数难遇常数序列，低危 | market_state_sensor.py:188-189、:204 | P3 | 全等序列 → pct=1.0 → HIGH |
| A | 趋势分数学健全：tanh 有界压摆、等权合成、clamp [-1,1]；MA gap 除零有 `ma_long > 0` 防护（负价格不可能，防护冗余无害） | market_state_sensor.py:152-177 | —（已查无） | test_flat_closes_score_zero / test_score_bounded |
| A | 置信度合成健全但假设对称阈值：trend_margin 以 bull_min 归一，若注入非对称阈值（bull_min=0.3/bear_max=-0.1）则 bear 侧边际被高估——初拟阈值对称时无害 | market_state_sensor.py:266-268 | P3 | 注入非对称阈值看 confidence 跳变 |
| A.3 | 测试盲区即缺陷所在：三处 test_insufficient_history_raises（:46/:69/:147）用的长度都**跳过了恰好 60/61 的边界**（用明显更短序列）→ 差一漏洞无回归保护；其余 17 用例断言方向/界/全组合，质量良好 | tests/signal_ashare/test_market_state_sensor.py:46,69,147 | P2（随 P2-1 修复补边界用例） | 检索测试文件无 `range(60)`/`range(61)` 边界用例 |
| B | **loader 丢弃日期列、无连续性校验**：load_index_closes 只取 close 列（parts[1]），trade_date 抛弃 → 断档（数据缺失/停更日）时 returns 跨档计算、年化系数 √252 失真、分位窗错位——全部静默 | market_state_sensor.py:330-342（仅存 close）、:259（相邻差分收益） | **P2** | 造含空档的假 TSV（两行日期差 30 天）→ sense 正常出快照无任何告警 |
| B | **SQL 用 .format 字符串插值**，违反项目自家"参数化查询禁 f-string 插值"约定（同域 S04 mainline_probability.py:96 明文该约定）；symbol/start/end 均可被调用方注入 → 注入面+口径不一致 | market_state_sensor.py:82-87、:330 | P2 | 对照两文件 SQL 构造方式；`symbol="000300' OR 1=1 --"` 观察 SQL 拼接 |
| B | 不可解析行 warning 后跳过（部分数据接受）：可能静默缩短序列——长度不足时 fail-closed 兜底（好），但跳行造成的隐藏断档并入上一条发现 | market_state_sensor.py:336-339 | P3 | 假 TSV 混入坏行 → warning + 序列缩短 |
| C | **孤儿裁定**：生产调用方=0；header :5 CONSUMERS 全部"待 …"；**MATURITY=production 名不符实**（与 S03 同病：标签漂移误导治理分级）。定性：待接线规则版传感器，当前对决策链零影响 | 全仓 grep 零调用方；market_state_sensor.py:5、:7 | P2 | grep 命令实录 |
| C | 下游消费契约未定义：9 态输出给风控节流的消费语义（状态→节流映射表）尚不存在——接线期风险点（S01 同族问题：输出枚举↔消费枚举无映射代码） | market_state_sensor.py:5、:23-27 | P3 | 接线施工单验收项 |
| D | 兄弟件分工清晰：与 regime/ HMM 检测器（模型版）同源输入可交叉验证（:25-27 声明）；代理指数同为 000300（:62 注释声明与 regime 同代理）——口径一致正面记录；与 daily_condition_sensor 的"月/周级 vs 盘中环比"分工（S01 D 轴已核）一致 | market_state_sensor.py:25-27、:62 | —（一致） | 对照两处声明 |
| E | 静默失败面：查询空 → MarketStateDataError fail-closed（好）；坏行静默跳（B 轴已记）；无心跳（零调用方暂无运行面）；幂等纯函数重跑安全——总体对抗面小 | market_state_sensor.py:340-341 | P3 | test_load_index_closes_empty_raises |
| E | 时序攻击面：end 默认 2099-12-31 → 始终取最新数据，若表断更将拿旧数据算"当前状态"且无数据新鲜度检查（**stale-data 静默**：断更N月仍出状态快照）——checklist#6 正中 | market_state_sensor.py:322-324（end 默认 2099） | **P2** | 假 query_fn 返回截至半年前的数据 → sense 无告警出快照 |
| F | 趋势×波动九宫格 regime 分类 | **受阻**：本战役检索额度已尽（1 次限流）；知识注不作实证：trend/realized-vol 双轴 regime 分类是 CTA/风险平价常见做法 | 本战役检索记录 2026-09-18 | 收口方补检"volatility regime classification trading" |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| trend×vol 3×3 规则网格状态机 | **受阻**（检索额度已尽；范式本身常见无争议，"规则版轻量传感器 vs HMM 模型版"双轨并行的定位与业界可解释性诉求一致） | 本战役检索记录 2026-09-18 |
| tanh 压摆趋势得分 | **对等已有**：tanh squashing 有界化是信号合成常规手段，无外部权威依赖必要 | 本件 :157-177 自述 |

## 4 缺陷清单（按严重级排序）

1. **P2｜min_history=60 与 long_window+1=61 差一崩溃（实跑复现）**
   - 现状：恰好 60 样本过 sense 门槛后必被 compute_trend_score 拒绝，报错信息误导。
   - 证据：market_state_sensor.py:136 vs :170-171；实跑输出见 §2。
   - 影响与爆炸半径：接线后若调用方按 min_history 契约裁剪数据 → 边界日崩溃；fail-closed 崩溃非静默，危害限可用性。
   - 建议修法：min_history 默认改 61（或 sense 内部校验 max(min_history, long_window+1)），补 60/61 边界测试。
   - 验证法：§2 轴 A 单行命令复跑。
2. **P2｜断档静默+数据新鲜度缺失**（stale-data + gap）：loader 保日期列并校验连续性/最新日期距离；验证法=假 TSV 含空档与旧数据复跑。
3. **P2｜SQL .format 插值违反项目约定**：改参数化（对齐 S04 模式）；验证法=对照两文件 SQL 构造。
4. **P2｜孤儿+MATURITY 标签漂移**：production→design（或接线）；验证法=grep 调用方。
5. **P3｜短样本分位偏高/常数序列判 HIGH/非对称阈值置信度失真**：登记口径，接线前补边界用例；验证法=§2 对应行。

## 5 挂起疑问

- market_index_kline 表 000300 的实际缺档率/最新日期未画像（需 DB 只读查询）——决定 B-1/P2-2 现实暴露面。
- regime/ HMM 检测器（MOD-REGIME-001）交叉验证对账机制未建（两版输出一致性无测试）。
- 9 态→风控节流的消费映射（10 号 spec 后续章节？）未核。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记；A 轴含实跑复证）。
- 长尾：①regime/ HMM 兄弟件本体；②10 号 spec 原文逐节核对；③kline 表数据画像。
- 变更热力：4 commits（创建+搬家+锚点批），无算法返工=低危。
- 测试审查结论：信任（20 用例方向/界/全组合覆盖好；盲区=精确边界长度与断档，恰为 P2 所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
