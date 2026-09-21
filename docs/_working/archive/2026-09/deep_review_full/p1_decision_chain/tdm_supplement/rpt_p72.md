---
ttl: task_bound
title: 深度审查作业簿——止盈族判定
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：止盈族判定（P72）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/sell_decision/core/take_profit_strategy.py:83`（TakeProfitStrategy.compute_exit_price）
- TDM 节点: TDM-X-S1-03（stage，config/trading_decision_map.yaml:3310，note 称"峰值回撤 D50 欠账本轮落位"）
- 生产调用方: **零**——TakeProfitStrategy 全仓无实例化（grep 零命中）；header 声明的 MOD-SELL-007 融合引擎/D-POSITION 零实际调用
- 测试文件: tests/sell_decision/test_take_profit_strategy.py（114 passed 同批，与 P73-P76 合跑 3.58s）

## 1 对象快照

- 范围：TakeProfitStrategy 全文件（131 行）——统一 Chandelier 退出价计算薄壳：自动 phase 判定（浮盈≥1×ATR→盈利区紧 trailing N=22/M=2.0，否则亏损区宽 N=10/M=3.0）+委托 MOD-SELL-005 核心计算（真源唯一）+ATR 缺失降级固定%。
- 排除项：StopLossStrategy/MOD-SELL-005 数学（其本体归止损族对象，本报告按消费口径核读委托链）；分批退出（归 MOD-SELL-017，:32-33 自划界）。
- 测试覆盖概况：phase 判定/降级/委托链覆盖；无峰值回撤场景（模块无此功能）。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **止盈三式只落一式，TDM 注释却宣称"峰值回撤本轮落位"（checklist #12 假完成状态同族）**：TDM-X-S1-03 声明止盈三式=①移动止盈（Chandelier 盈利区）②**峰值回撤（从最高浮盈回落 30% 兑现——"赚过没拿住是最大利润漏点"）**③目标位（预期涨幅达成/打板票次日不板走）；注释更写「峰值回撤兑现（D50 欠账**本轮落位**：peak_pnl 回落 X% 强制兑现）」——模块只有①（Chandelier 委托壳）：**peak_pnl 追踪/浮盈峰值回落 30% 兑现零代码**（highest_close_fn 是 N 日最高收盘价，价格锚非浮盈锚——从最高收盘回撤 M×ATR 与从最高浮盈回撤 30% 是两个不同触发表）；③目标位/打板次日不板走零代码。**图上"已落位"的保护（赚过没拿住的最大利润漏点封堵）实际不存在** | config/trading_decision_map.yaml:3310-3330（三式+落位注） vs take_profit_strategy.py 全文（grep peak_pnl/目标位/次日不板 零命中） | P1 | 对照三式逐条 grep；读模块全文确认无峰值浮盈状态 |
| A | phase 判定数学（已核）：unrealized_pnl_pct=(cur−entry)/entry 对 atr_pct=ATR/entry，比较同量纲（相对 entry 口径一致）✓；≥1×ATR 切盈利区与 TDM/D57"只看市场状态变量不看连赢次数"一致；ATR≤0/None 降级委托 005 固定%分支（phase 传 LOSS 占位且有注释说明不生效原因，:115-122） | take_profit_strategy.py:124-131 | —（已核） | — |
| A | 真源唯一纪律执行好：本件是 005 的消费者层不复制公式（INVARIANTS"不维护两套%参数"兑现）——与 P52 双锚分叉形成对照 | take_profit_strategy.py:25-26,130-131 | — | — |
| C | 孤儿死码（checklist #8）：零调用方；止盈触发链（X-S1-03→S1-05 融合→S2 执行）全断 | take_profit_strategy.py:5；grep 零命中 | P2 | `grep -rn "TakeProfitStrategy" src/ --include=*.py` |
| B | phase 判定的隐式契约：highest_close_fn 由调用方注入——N 日窗语义（盈利区 22/亏损区 10）由 005 内部选择回看数，本件不校验 fn 返回的窗口一致性；若调用方注入错窗口函数，Chandelier 锚错而静默 | take_profit_strategy.py:86-100 | P3 | 注入恒返现价的 fn 看 trailing 退化 |

## 3 SOTA 对照

- Chandelier Exit（最高高−M×ATR，Le Beau 创制/Elder 推广）：**对等已有**——经典公式 22 日窗+3×ATR（StockCharts ChartSchool Chandelier Exit，chartschool.stockcharts.com，经典文献；Corporate Finance Institute chandelier-exit，corporatefinanceinstitute.com，2026；TrendSpider profit-protection，trendspider.com，2026——同窗用于 high 与 ATR 是要点）；本模块盈利区 N=22/M=2.0 比经典 3.0 更紧（锁利取向，与 42 号 §3.4 双区参数一致，方向合理）。
- 峰值浮盈回撤兑现（give-back X% 即走）：**对等已有**——利润回撤兑现（profit giveback limit）是趋势跟踪利润管理常规（与 R 多单位分批止盈同族，Van Tharp 型 R 模型，vantharpinstitute.com，经典文献）；TDM 三式中②恰是 A 股短线语境最关键的一式（打板/情绪票利润衰减快），**缺位即节点核心价值缺位**（主发现）。
- 目标位止盈（预期涨幅达成）：**对等已有**——目标价退出是最基础止盈形态（同上 Investopedia 族）；打板票"次日不板走"为 A 股社区纪律（雪球/知乎打板教程，xueqiu.com，2024-2026，同 P65 引）。

## 4 缺陷清单

1. **[P1] 止盈三式缺二（峰值回撤 30% 兑现+目标位），TDM 注释"本轮落位"与代码不符**。影响："赚过没拿住"的利润漏点封堵=图上有码上无；峰值浮盈保护比 Chandelier 价格 trailing 更贴合短线利润管理。建议修法：施工批次补 peak_pnl 追踪+回落 X% 兑现+目标位字段（X-S1-01 信号面加峰值回撤类型），并修正 TDM 注释的落位声明；或把"落位"改指 Chandelier 近似并在节点写明两者触发表差异。验证法：§2 轴 D grep。
2. **[P2] 孤儿死码**。建议修法：随 S1-05 融合/S1-01 收集器接线批次统一接线（X 流 signal 侧三件 P52/P71/P72 全孤儿，宜同批）。验证法：grep。
3. **[P3] highest_close_fn 窗口契约无校验**。建议修法：契约注明"fn 必须按 005 请求的 N 回看"；或改传数据快照。验证法：注入探针。

## 5 挂起疑问

- "峰值回撤 30%"的 X 值与浮盈峰值口径（盘中最高浮盈 vs 日收盘浮盈）需回测校准定稿——TDM 用 30% 占位。
- 与 MOD-SELL-017 scaling_out（+1R 减 50% 阶梯）的分工：本件管"何时该走"价位、017 管"走多少"——两件均孤儿，接线时须同时上避免半链。

## 6 完备性自评

六轴全查（A 数学四问：phase 判定同量纲比较/降级路径/委托链已核、边界=ATR 缺失/零/负已测；B 上游=SellPositionSnapshot/highest_close_fn 契约已查；C 下游=零调用方判孤儿；D=三式对账（主发现）+与 005 真源唯一纪律核读；E 五问：静默失败=落位假声明、假阳性=无、断供=ATR 缺失降级（已防）、重复触发=纯函数幂等、时序=无时钟依赖）。长尾：①MOD-SELL-005 Chandelier 核心数学详查归止损族对象（本报告只按委托口径抽查其 N/M 分支存在性）；②MOD-SELL-017 scaling_out 未审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
