---
ttl: task_bound
doc_type: report
title: 深度审查报告——指数共振评分（S10）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：指数共振评分（S10）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/index_resonance_scorer.py:92`（ResonanceConfig）/ `:254`（compute_resonance 纯函数核）/ `:449`（score_index_resonance 主入口）
- 生产调用方: **零**（grep compute_resonance/score_index_resonance 全仓 src/scripts 仅自身；GAP-F-31 综合观点卡消费位未接线）
- 测试文件: tests/signal_ashare/test_index_resonance_scorer.py（15 用例，已审）
- 备注: 关键发现（全平序列→高置信卖出信号）已经 Python 3.12.8 实跑复现

## 1 对象快照

- **范围**：`index_resonance_scorer.py` 全文 526 行——七族（MACD/KDJ/RSI/量能/均线/BOLL/趋势）三值投票加权合成 [-1,1] → 买/卖/中性 + 共振 x/7 + 启发式置信度；含 kline_index 只读加载层。
- **排除项**：kline_index 表本体（数据层）；GAP-F-31 前端契约原文。
- **测试覆盖概况**：15 用例（七族投票/阈值/降级/overrides 白名单/frozen）。信任度：**信任（盲区=等值边界与平坦序列）**。
- **材料包缺项声明**：无运行时证据包；kline_index 真实分布未画像。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **等值边界全面偏空 + RSI 平坦悖论：全平序列输出"卖出/置信 75.2/共振 4/7"（实跑复现）**——精确相等时 MACD(`dif>dea else -1`)、KDJ、BOLL、趋势(`close>ref else -1`)四族全判 -1，RSI 在 avg_loss=0 时无条件返回 100 判 +1（平坦本应中性），净合 -0.44 触发卖出并给高置信。触发面：指数长期冻结/停牌期同值回填/数据冻结——**带 75.2 置信度的反向假信号** | index_resonance_scorer.py:306（dif>dea else -1）、:223-224（avg_loss=0→100）、:386（>ref else -1）、:374 | **P1** | 实跑：`compute_resonance([DailyBar('d',100,100,100,100,1000) for _ in range(60)])` → signal=卖出、score=-0.44、conf=75.2（本报告实测输出在案） |
| A | **数据新鲜度缺失（stale-data 静默）**：trade_date None → PIT 上限=2100-01-01"不过滤"（:487 注释自认），表断更时拿旧数据照常出"当日"观点卡，无最新日期距今检查——checklist#6 正中（与 S05 同病；S04 资金腿断供→缺维、本件断供→旧照发） | index_resonance_scorer.py:483-487 | **P2** | 假 client 返回截至半年前数据 → 无告警出 signal |
| A | 指标实现质量总体好于同域均值：EMA 用 SMA 暖机种子（:165，优于 S06 首值种子）、DIF 对齐 zip 尾段（:184 正确对齐）、RSI Wilder 递推正确、KDJ 递推+平盘 rsv=50 防护（:201）——主链健全 | index_resonance_scorer.py:160-226 | —（正面） | 对照 test 文件 |
| A | 共振计数含零权重族：`aligned` 过滤只看 vote 不看 weight>0——overrides 把某族权重置 0 后该族票仍计入"x/7"（分数不含、共振含，口径分裂） | index_resonance_scorer.py:400-407 | P3 | overrides={"macd":0} + macd 反向票 → score 不含但 resonance_count 含 |
| A | compute_resonance 直接调用返回 symbol=""（:270,:285,:414 硬编码空串）——导出 API（__all__ :55）直呼者拿到空 symbol，仅包装层回填；API 契约瑕疵 | index_resonance_scorer.py:414、:55 | P3 | 直接调 compute_resonance 看 result.symbol |
| A.3 | 测试盲区：无平坦/等值序列用例（P1 正中）、无断更/旧数据用例（P2-1）、无零权重共振计数用例；15 用例主路径覆盖良好 | tests/signal_ashare/test_index_resonance_scorer.py | P2（随 P1 修复补测） | 搜测试无 flat/等值用例 |
| B | 加载层：SQL 参数化 ✓（合规，反例=S05 的 .format）；DESC LIMIT+reversed 升序 ✓；NULL 行 float(None)→TypeError **未被捕获**（try 只包 execute，:502-512 列表推导在 try 外）→ 单行 NULL 炸主入口（fail-closed 崩溃非降级，违反自家 ERROR_CONTRACT "查询异常→degraded 不抛"精神） | index_resonance_scorer.py:488-512、:13 | P2 | 假 client 返回含 None 行 → TypeError 未降级 |
| B | bars 注入路径零校验：negative/NaN close 直接进指标计算（与加载路径同样无校验）——NaN 传播模式同 S03/S06 家族 | index_resonance_scorer.py:254-301 | P3 | NaN close 注入 → 各族 vote 行为未定义 |
| C | **孤儿裁定**：生产调用方=0；GAP-F-31 指数详情页综合观点卡未接线；MATURITY=testing 诚实（无标签漂移，S03/S05/S08 反例） | 全仓 grep 零调用方；index_resonance_scorer.py:5、:7 | P2 | grep 命令实录 |
| C | 下游消费契约：signal/confidence/resonance 的前端展示语义（degraded → confidence=None 前端如何显示）未约定；爆炸半径=观点卡误导（显示层），非资金路径 | index_resonance_scorer.py:139-152 | P3 | 接线施工单验收项 |
| D | **weight_overrides 语义与 S04 相反**：本件 update 合并（未覆盖键保留默认 :250），S04 整体替换（未覆盖键=0）——同代两件动态权重接口语义相反，调用方跨模块迁移必踩 | index_resonance_scorer.py:245-251 vs mainline_probability.py:266 | P3 | 两件各传 {"macd":0.5} 对照剩余键权重 |
| E | 静默失败面：stale-data（P2-1）为主；查询异常/客户端缺失降级+notes ✓ 健康；幂等纯函数；无遥测（接线时补） | index_resonance_scorer.py:469-501 | P2（并入 P2-1） | — |
| E | 时序：PIT ≤ trade_date ✓；无竞态；frozen ✓——已查无 | index_resonance_scorer.py:80 | — | test 文件 frozen 用例 |
| F | 七族技术指标投票共振 | **受阻**：检索额度已尽；知识注不作实证：多指标投票确认（voting/confluence）是经典 TA 体系做法，KDJ 口径声明与 regime risk_features 同源（仓内一致性） | 本战役检索记录 2026-09-18 | 可选补检"technical indicator confluence voting" |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 多指标三值投票+加权共振 | **受阻**（额度已尽；经典范式无争议，权重初拍待标定自认） | 本战役检索记录 2026-09-18 |
| EMA SMA-暖机种子 | **对等已有**：与主流 MACD 实现（TA-Lib 等）暖机口径同构（比首值种子更接近收敛值） | index_resonance_scorer.py:160-169 实现（对照口径说明） |
| KDJ(9,3,3) 递推 | **对等已有**：K=2/3·K+1/3·RSV 标准递推（仓内与 regime risk_features 同口径双承载，见轴 D 挂接） | 本件 :191-204 |

## 4 缺陷清单（按严重级排序）

1. **P1｜等值边界系统性偏空 + RSI 平坦悖论 → 全平序列出高置信卖出信号（实跑复现）**
   - 现状：四处等值比较全走 -1 分支；`_rsi_wilder` avg_loss=0 无条件返回 100（平坦判极多）；净分 -0.44 → 卖出+75.2 置信。
   - 证据：index_resonance_scorer.py:306、:374、:386、:223-224；实测输出（signal=卖出 score=-0.44 conf=75.2 resonance=4）。
   - 影响与爆炸半径：指数长期冻结/停牌回填/数据冻结场景 → 观点卡高置信反向假信号（决策卡直接消费的显式买卖语义）；精确相等触发面窄但后果重（置信度放大误导）。
   - 建议修法：(a) 四处等值边界改 0（中性）；(b) `_rsi_wilder` avg_loss=0 且 avg_gain=0 → 返回 50（对齐 S06 的 :180-181 处理）；(c) 补平坦序列用例。
   - 验证法：§2 P1 行单行命令复跑。
2. **P2｜断更旧数据静默照发（无新鲜度检查）**：加载后校验 bars[-1].date 距今阈值 → 超限 degraded；验证法=假 client 旧数据复跑。
3. **P2｜NULL 行 TypeError 未降级**：行构造入 try 或逐字段容错；验证法=None 行假数据复跑。
4. **P2｜孤儿未接线**（GAP-F-31 位）；验证法=grep。
5. **P3｜共振计数含零权重族/直呼 symbol 空/overrides 语义与 S04 相反/NaN 注入**：登记+统一；验证法=§2 对应行。

## 5 挂起疑问

- KDJ 口径"与 regime risk_features 同源"的双承载（本件 :191-204 vs regime 模块）未逐行对照——checklist#4 登记，建议对账测试。
- 前端观点卡契约原文（GAP-F-31 行）与输出字段语义核对未做。
- buy/sell 阈 ±0.2 与权重初拍值的标定计划（G09）无跟踪锚。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记；A 轴含实跑复证）。
- 长尾：①regime risk_features KDJ 对账；②前端契约核对；③真实 kline_index 数据画像（断更历史/NULL 率）。
- 变更热力：3 commits（创建+搬家+锚点），无算法返工=低危。
- 测试审查结论：信任（主路径+降级覆盖好；盲区=平坦序列/断更，恰为 P1/P2 所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
