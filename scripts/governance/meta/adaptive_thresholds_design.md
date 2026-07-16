---
blueprint_id: MOD-INF-005
ttl: task_bound
doc_type: policy
---

# MOD-INF-005 自适应阈值设计

> 蓝图 §30.1 — P2 期 Backlog
> 状态：设计文档 — 尚未施工

## 1. 目标

将 `_shared/thresholds.yaml` 中的静态阈值升级为基于历史数据的自适应建议。

## 2. 算法框架

### Phase A: 历史数据采集
- 输入：`sla_metrics.jsonl` 全量历史记录
- 采集维度：扫描耗时趋势 / Finding 数量趋势 / 假阳性率趋势

### Phase B: 分位数计算
- `P50 / P75 / P90 / P95 / P99` 历史 scan_duration_s 分位数
- `P50 / P75 / P90 / P95 / P99` 历史 total_findings 分位数
- 滑动窗口：最近 28 天（4 周）

### Phase C: 建议生成
- 当前阈值在 P50-P75 → 建议保持不变
- 当前阈值在 P75-P90 → 建议上移（WARNING）
- 当前阈值 < P50 → 建议收紧（可提高质量标准）
- 持续 3 周 > P90 → 建议上移（SUSTAINED OVERLOAD）

## 3. 参数化建议公式

```
suggested_per_script_timeout = max(existing_threshold, P95_recent_28d * 1.2)
suggested_global_timeout = max(existing_global, P99_recent_28d * 1.1)
```

## 4. AI 自助权限

- AI 可生成建议但不自动应用
- 建议输出 → `meta/adaptive_threshold_suggestions.yaml`
- Owner 审查后 → 手动 merge 到 `_shared/thresholds.yaml`

## 5. 成熟度跃迁路径

- L3.6（当前）：静态阈值 + 人工调优
- L4.0：自动分位数计算 + 建议生成
- L4.5：自动建议 → Owner 一键审批 → 自动应用

## 6. 相关文件

- `_shared/thresholds.yaml` — 当前阈值定义 SSoT
- `meta/compute_sla_metrics.py` — SLA 指标计算（历史数据源）
- `meta/sla_metrics.jsonl` — 原始扫描指标记录
