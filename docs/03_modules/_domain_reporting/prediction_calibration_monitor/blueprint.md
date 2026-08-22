---
blueprint_id: MOD-RPT-029
module_name: prediction_calibration_monitor
domain: D_REPORTING
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-RPT-029 prediction_calibration_monitor 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘 §12.1 M4-④（"AI 通过日志调参"——实验结果→参数调整的登记与触发）+ 92号清单 §8.7（数据期需命中率积累，本批=统计器+触发器骨架+样本量守卫 <30 不触发）。机构对标：MLflow experiment tracking 反馈环 / WFA 滚动校准触发器（52号）。
> 代码：`src/zephyr/reporting/prediction_calibration_monitor.py`

## 0. 定位

日志→参数校准反馈闭环骨架——**只出"评审建议"，本模块永不自治修改任何参数**（调参动作恒人审/G04 流程）。消费方：G04 参数校准流程（人审）、CAND-SELL-001 同族触发器族（规划）、55号 周/月复盘编排（规划）。

## 1. 接口

```python
def record_outcome(trade_date, module, outcome_payload, asof_ts=None, db_path=None) -> int
    # 事后真值回写 prediction_log 本表 outcome 族；outcome_payload 须含 hit: bool（fail-closed 校验）

def compute_hit_rate_stats(module, window_days=60, db_path=None) -> CalibrationStats
    # 窗口期预测序列 → 命中率/样本量/趋势（纯数据不判定）

def evaluate_calibration_trigger(
    module, stats: CalibrationStats | None = None, config: CalibrationConfig | None = None,
    db_path=None, runtime_dir=None,
) -> TriggerVerdict                 # fail-open，永不外抛运行时异常
```

`CalibrationConfig`：hit_rate_threshold=0.55（对齐 44号 M3 注解栏 55% 口径族）/min_samples=30（样本量守卫）/window_days=60。

## 2. 输出契约

- `CalibrationStats`：module/window_days/window_start/window_end + prediction_count（剔除 outcome/calibration_trigger 族）+ sample_size（窗口内且能匹配当日预测行的 outcome 数）+ hit_count/hit_rate（sample_size=0 时 None）+ recent/previous_hit_rate（样本按 trade_date 升序对半分，|近段−前段|≤5pp 记 stable，样本<2 记 insufficient_data）
- `TriggerVerdict`：module/triggered/reason（词表闭集 insufficient_data/below_threshold/hold/error）/suggested_action（评审建议文本，供 G04 人审）/evidence（证据快照+落盘留痕）/evaluated_at
- 触发规则：样本<30 恒不触发（insufficient_data）；样本达标且命中率<0.55→触发"参数校准评审"建议（below_threshold）

**四项裁定**：① 真值回写落点=prediction_log 本表 outcome 族，不建姊妹表（单一账本，复用 92号 §7.13 幂等键/DDL 真源/查询 API）；② 命中判定归回写方（本模块只聚合不判定，骨架期口径无关）；③ experiment_registry 联动形态=**不写注册表 yaml**（human_gated 纪律），触发时输出评审建议工单 markdown 落 `.runtime/calibration_review/` 运行时区（同模块同日重写=覆盖同日工单，runtime 幂等非审计载体；审计载体=prediction_log 触发事件行 calibration_trigger 族）；④ 失败方向分层=输入/config/stats 校验 fail-closed（ValueError），评估与落盘异常 fail-open。

## 3. 不变量（头注 INVARIANTS 原文）

- 只出"评审建议"——本模块永不自治修改任何参数（调参动作恒人审/G04 流程）
- 评估/落盘异常 fail-open（不触发+TriggerVerdict.reason='error'+logging 留痕，绝不阻断调用方）
- 输入/config/stats 校验 fail-closed（ValueError）
- 不写任何注册表 yaml（experiment_registry 联动=输出工单文本落 .runtime/ 运行时区）
- DB 访问仅经 prediction_log_writer 公共 API（append-only，本模块零裸 SQL）
- 样本量守卫：样本<30（默认可配）恒不触发

## 4. 降级行为

- ERROR_CONTRACT：ValueError（module/config/stats/outcome_payload 非法 fail-closed）；compute_hit_rate_stats/record_outcome 的 sqlite3.Error 透传（evaluate_calibration_trigger 内统一收敛 fail-open 不外抛）
- 触发事件落盘失败不翻转判定（verdict 仍 triggered=True，evidence 记 persistence_error）——判定与留痕解耦

## 5. 边界（不做）

- 永不自治改参；不写注册表 yaml；不内嵌业务命中判定逻辑；不建第二真源

## 6. 测试

tests/reporting/test_prediction_calibration_monitor.py
