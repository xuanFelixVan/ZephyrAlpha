---
blueprint_id: MOD-PLAN-004
module_name: overnight_boundary_reviser
domain: D_PLAN
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: testing
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-PLAN-004 overnight_boundary_reviser 蓝图

> 紧凑版（92 号清单波次落地配套，SOP Step 4 补建）。设计真源：44号备忘 §4 M3-①a⑦⑧ 盘前包 + §9.6/§9.10/§9.12。
> 代码：`src/zephyr/plan_engine/overnight_boundary_reviser.py`

## 0. 定位

盘前隔夜边界修正器——44号 §4 M3 盘前综合预判的"今晨修正"计算核心。MOD-PLAN-002 只"加载昨夜边界"不修正，本模块提供"用外盘隔夜+盘后资金面+事件日历修正边界档位"的增量载体，输出 final_shift 供 M3-③ scenario_planner 消费。

## 1. 接口

```python
def compute_overnight_revision(
    trade_date: str | datetime.date,
    ch_client: Callable[[str], str] | None = None,   # None=走 ch_reader.query 默认 CH 通道
    config: OvernightRevisionConfig | None = None,    # None=44号设计真源默认值
    bs005_triggered: bool = False,                    # BS-005 外围冲击硬触发（上游注入）
) -> OvernightRevision
```

类形态：`OvernightBoundaryReviser(ch_client, config).compute(trade_date, bs005_triggered)`。ch_client 可注入（测试 mock/离线）。

## 2. 输出契约

`OvernightRevision`（frozen dataclass，`to_dict()` JSON 可序列化，供 prediction_log 落库）：

| 字段 | 语义 |
|---|---|
| final_shift | 最终档位修正 ∈ {-1, -0.5, 0, +0.5, +1}（由消费方应用到基线档位） |
| gap_adj / gap_adj_degraded | 外盘隔夜加权修正系数；符号空值缺陷退化单序列代理时 degraded=True |
| fund_score / fund_detail | 资金面四件套 z 合成（None=四件全无数据）+ 分量留痕 |
| event_flags | 事件日历命中标记（含 A50 交割规则自算标注） |
| sensitivity_scale | 敏感度缩放（事件夜/A50 交割升半档=整档阈值降至 1.0%） |
| m1_threshold_scale / basis_weight_scale / a50_channel_weight | 期权到期 0.8 / 交割周 0.5 / A50 交割日 0.45（否则 1.0/None） |
| reasons / trace | 决策理由链 + 通道状态留痕（ok/degraded/skipped/error） |

修正规则（§9.6）：|gap_adj|<0.5% 不变档；0.5%~1.5% ±半档；≥1.5% 或 BS-005 触发 ±一档。资金面同向确认（×1.0），反向且 |fund_score|>1σ 否决半档（§9.10）。

## 3. 不变量（头注 INVARIANTS 原文）

- fail-open 不阻塞主流程
- 单通道异常=该通道降级不炸整体
- calendar_event 空表静默跳过+留痕
- 输出纯 dataclass JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：单通道异常→该通道降级（None/缺省值）+trace 留痕；整体不抛异常（仅 trade_date 非法抛 ValueError，fail-closed）
- us_index 表 index_code 空值缺陷：无法区分标普/纳指→退化单序列美股代理 + gap_adj_degraded=True
- z-score 历史不足 5 点或标准差为 0→该资金分量降级（权重重归一）
- etf_flow 候选缺省=0（权重重归一）；A50 交割日 calendar_event 暂无此类→按规则自算标注（每月倒数第 2 个工作日）
- 表名解析失败→fallback 全限定名（fail-open）

## 5. 边界（不做）

- 不直接改 TomorrowBoundary（消费方 M3-③ 负责应用 final_shift）
- 不做方向点预测（90号 §7 裁定，只画栏杆不算命）
- 不碰既有三文件（tomorrow_boundary_planner/premarket_constraint_loader/closing_session_decision）

## 6. 测试

tests/plan_engine/test_overnight_boundary_reviser.py
