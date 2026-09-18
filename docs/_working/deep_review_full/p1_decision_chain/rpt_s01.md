---
ttl: task_bound
doc_type: report
title: 深度审查报告——水温五档（S01）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：水温五档（S01）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更，发现对两版均有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/core/daily_condition_sensor.py:45`（WaterTempTier）/ `:239`（evaluate_daily_condition 主入口）
- 生产调用方: **零**（唯一引用=`src/zephyr/signal_ashare/__init__.py:120` 门面导出 noqa F401；详见轴 C）
- 测试文件: tests/signal_ashare/test_daily_condition_sensor.py（24 测试，已审）
- 备注: 纯函数核零 IO；全仓 grep 确认基线后源文件无变更

## 1 对象快照

- **范围**：`daily_condition_sensor.py` 全文 320 行——11 信号（A 组实战 8 + B 组机构 3）三值计票 → 净分 → S0-S4 五档水温。纯函数、零 IO、frozen dataclass、阈值可注入。
- **排除项**：`sector/sector_gate.py`（响应侧，另行对象）；`market_state_sensor.py`（S05 单审）。分工声明见 `daily_condition_sensor.py:30-32`。
- **测试覆盖概况**：五档边界/缺数据降级/fail-closed 契约/确定性均有显式测试，含 -0.05 溢价边界口径矛盾的显式备注（测试 :203-209）。信任度：**信任（有长尾，见轴 A.3）**。
- **材料包缺项声明**：无运行时证据包（对象无生产调用方=无运行日志可查，本身即发现）；数据画像缺（纯函数无绑定表）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 溢价⑤边界口径文档漂移：注释/docstring 称"≤-5% → -1"，实现为严格 `<`（恰 -0.05 计中性） | daily_condition_sensor.py:75、:21 vs :169-178（_band_vote 严格比较） | P3 | 构造 `yesterday_limit_up_premium=-0.05` 跑 evaluate_daily_condition，details 中 yesterday_premium=NEUTRAL（与注释"≤"矛盾）；test_daily_condition_sensor.py:203-209 已固化实现行为 |
| A | ⑦量能诱多信号常态值计基础多头票：`volume_match_trap=False`（量价正常，多数交易日）→ +1，net 分布系统性右移约 1 票，五档经验阈值未显式补偿；回测校准前阈值隐含此偏置 | daily_condition_sensor.py:232-236（False→BULLISH）、:93-94（语义声明） | P2 | 统计任一历史区间"价升量缩"日占比 f；若 f≪50% 则 11 票中约 (1-f) 概率含 +1 基础票；对照 `_tier_of` 阈值（≥+4→S4）评估档位漂移 |
| A | 五档净分阈值未按可用信号数归一：missing 计 0 票，同比例 bullish 在数据稀缺时映射更低档（保守方向非风险向），但回测校准阈值时若 missing 分布与实盘不同，校准失效 | daily_condition_sensor.py:295-301（net=bullish-bearish 不除 available） | P3 | 构造 11/8/6 可用三组同比例（60% bullish）输入，比较 tier 输出差异 |
| A | 昨日基数=0 的环比信号按缺数据：极端情绪转折日（昨日 0 涨停→今日重现）信息丢失计中性——保守可接受，无除零风险 | daily_condition_sensor.py:158-160 | P3 | `DailyRawSignals(limit_up_count=100, limit_up_count_prev=0)` → missing=True（测试 :184-188 已固化） |
| A.3 | 测试长尾：⑥红盘 1500/2800、④跌停 30、⑨宽度领先 ±0.10 的**精确边界值**均无显式断言（当前实现为严格不等号，恰等计中性）；`>` 改 `>=` 无回归保护 | tests/signal_ashare/test_daily_condition_sensor.py:56-121（仅 0.50 炸板线有边界用例） | P3 | 测试文件内搜无 1500/2800/30/0.1 边界用例即证 |
| B | 全部 13 个输入由调用方注入（零 IO，header :4 称源自 DS-082/DS-059/DS-150），但**注入方不存在**（轴 C 零调用方）→ 上游隐式契约（None=缺 vs 0=零值）无生产侧文档化 | daily_condition_sensor.py:4、:99-111 | P2 | `grep -rn "evaluate_daily_condition\|DailyRawSignals" src scripts --include=*.py` 仅命中 `__init__.py:120` |
| B | **0 与 None 语义无区分防线**：`limit_down_count=0`、`advancers=0` 是合法值（0 家跌停→+1 正确），但上游若把"缺数"填 0 而非 None：advancers=0→BEARISH 假警报、limit_down=0→BULLISH 假多头；不触发 missing 计数、不触发 <6 fail-closed | daily_condition_sensor.py:210-218（==0→BULLISH）、:221-229（<1500→BEARISH） | **P1** | 见 §4.1 验证法：给足 6 真实信号+advancers=0 → tier 被假 BEARISH 拉低且无任何告警通道 |
| C | **孤儿裁定**：生产调用方=0。`[CONSUMERS]` 声称的 TDM-E-L1-S5/L1-AGG/L2-05-1 均未接线（仅门面导出）。MATURITY=design 诚实标注 → 定性"**待接线设计件**"而非死码；checklist#8"空转多久没发现"适用；接线前对决策链零影响 | 全仓 grep（src+scripts）仅 `__init__.py:120`；daily_condition_sensor.py:5 | P2 | grep 命令同上 |
| C | 下游消费方式未定义：接线时消费方拿到 `tier=None`（INSUFFICIENT_DATA）如何处置无任何约定——静默按中性处理=决策链带病传播 | daily_condition_sensor.py:145、:301-310 | P2 | 接线施工单验收项（当前无消费方可查） |
| D | **五档水温双份承载、无桥接**：本件 `WaterTempTier`（S0_ICE..S4_HOT）与 `sector_gate.WaterTemp`（NEUTRAL/RISK_ON/PANIC_REPAIR/RISK_OFF/CRASH）同概念两套枚举；docstring :32 声称"本模块输出可映射为其入参"，全仓无任何 S0-S4→gate 枚举映射函数——接线日必临时拍映射=口径漂移温床（checklist#4 双份承载漂移） | daily_condition_sensor.py:45-52、:32 vs sector/sector_gate.py:54-87 | **P1** | `grep -rn "WaterTempTier\|S0_ICE" src scripts --include=*.py` 除本件外零命中 |
| E | 静默失败面：缺数据一律记 missing 不报错（设计如此），部分断供（6≤可用<11）时 tier 照给且无代表性告警；纯函数无日志无遥测——"断了没人知道"完全依赖未来调用方 | daily_condition_sensor.py:295-301 | P3 | 造 6 可用（其余 None）输入 → tier 正常输出无异常/标记（details 的 missing 字段可审计，缓解） |
| E | 时序/幂等：纯函数同输入同输出（有测试固化），无状态无竞态——**已查无** | daily_condition_sensor.py:243、test :233-234 | — | test_determinism |
| F | 受阻：A股涨停情绪指标族检索被限流（429，2026-09-18），无 URL 级对照 | WebSearch"涨停板溢价/炸板率 研报"全部 429 | 受阻 | 重试检索或收口方补查 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 11 信号计票→五档合成（市场情绪广度计票范式） | **受阻**：检索限流无 URL；按 deep_review_policy §4.2 不凭训练记忆断言 | WebSearch 429（2026-09-18 实录） |
| 阈值"经验拍定+holdout 只考一次"校准纪律 | **对等已有**（与量化研究 standard holdout 实践同构；项目内部方法论自洽判定，不引外部权威） | 本件 :27-28 自述 |

## 4 缺陷清单（按严重级排序）

1. **P1｜0/None 语义无区分防线 + 五档枚举双份承载无桥接**（轴 B/D 合并）
   - 现状：0 是多个输入合法值，缺数须传 None 但无校验能识破"上游缺数填 0"；S0-S4 与 sector_gate 五档无映射代码。
   - 证据：daily_condition_sensor.py:210-229；sector/sector_gate.py:54-87；全仓无桥接（grep 实证）。
   - 影响与爆炸半径：接线后上游填 0 惯例混入 → 假票静默计入水温档 → 当日激进度误判（决策链系统性偏移，不报错只亏）；桥接缺失 → 接线日临时拍映射。
   - 建议修法：接线前（a）"缺数=None"契约写入接线集成测试；（b）增显式映射函数+测试（收口方施工）。
   - 验证法：`python -c "from zephyr.signal_ashare.core.daily_condition_sensor import *; r=evaluate_daily_condition(DailyRawSignals(limit_up_count=110,limit_up_count_prev=90,ladder_count=55,ladder_count_prev=40,failed_board_ratio=0.15,limit_down_count=0,yesterday_limit_up_premium=0.03,advancers=0)); print(r.tier, r.details[5].vote)"` → 观察假 BEARISH 混入仍给档。
2. **P2｜volume_match_trap=False 基础多头票偏置**（轴 A）——影响=净分右移、校准前阈值含隐含 +1；建议=回测校准时对"⑦仅 True 计票/False 中性"与现状双版对比；验证法=两版净分分布统计。
3. **P2｜上游注入方不存在 + tier=None 消费语义未定义**（轴 B/C）——接线施工单必须补输入清单与 None 处置约定；验证法=接线 PR 审查清单。
4. **P3｜溢价"≤"文档漂移**：改 :75 与 :21 注释对齐实现（测试已选实现侧）；验证法=对照注释与 test :203-209。
5. **P3｜净分阈值未归一+数值边界测试长尾**：见日志表；验证法=三组同比例输入对照。

## 5 挂起疑问

- 69 号备忘录 §2.11 D20 原文与 :198-208 映射是否逐条一致未核对（本报告仅对码文件内注释；收口方抽查）。
- B 组信号 ⑨⑩⑪ 的上游计算器（宽度领先/坏消息反应/市值分层宽度）仓库内是否存在——无调用方追无可追，接线时须补输入清单。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记）。
- 长尾：①D20 备忘录原文核对；②TDM 地图节点 TDM-E-L1-S5 地图侧锚点核对；③未来接线方 L1-AGG 实现形态（尚不存在）。
- 变更热力：1 commit（065a2615dc，2026-09-10），无返工史=低危。
- 测试审查结论：信任（断言强度足够、无日期依赖、无 mock 掉核心逻辑；长尾=数值边界用例缺失）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
