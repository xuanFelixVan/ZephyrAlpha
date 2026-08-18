---
title: 量化核心算法正确性审查报告（第一轮·Kimi K3）
date: 2026-08-16
doc_type: review_report
ttl: task_bound
reviewer: "Kimi K3（coord-0815-gov3 统筹会话）"
review_round: "第一轮（非盲审——审查者持有项目上下文）"
completes_when: "Qwen3.8 Max 盲审二审完成后做差异比对裁定"
---

# 量化核心算法正确性审查报告（第一轮）

> 依据任务书 `2026-08-16-codex-external-review-brief.md` R1-R5 执行。
> **方法论声明**：不看测试锚点做结论，全部结论来自代码+memo 公式独立推演；测试仅用于反向定位"锚点是否镜像了错误假设"。

## 发现汇总

| # | 级别 | 标题 | 状态 |
|---|---|---|---|
| F1 | **P1** | ES 线性插值致尾部样本数抖动（小样本口径漂移） | 待裁定 |
| F2 | **P1** | VaRCalculator 静默过滤 NaN——数据缺口期间风险被低估且无信号 | 待裁定 |
| F3 | **P1** | 幽灵持仓检测枚举不全——"策略侧无记录"的持仓完全不报 | 待裁定 |
| F4 | P2 | Inf 输入穿透 VaR 计算（风控件未 fail-closed） | 待裁定 |
| F5 | P2 | RegimeMeta 死代码两则（n_downside==0 不可达分支；兜底路径数学不可达） | 待裁定 |
| F6 | 阴性 | R2 双重折扣担心排除（不变量成立，代码与 memo 一致） | 确认健康 |
| F7 | 阴性 | R3 Kelly 公式/截 0/边界校验全部正确 | 确认健康 |

---

## F1 [P1] ES 线性插值致尾部样本数抖动

**位置**：`src/zephyr/risk/core/tail_risk_monitor.py:447-453`

```python
var_quantile = float(np.quantile(returns, 1 - confidence))  # 默认 linear 插值
tail = returns[returns <= var_quantile]
es = -float(np.mean(tail))
```

**推演**：`np.quantile` 默认 **linear 插值**。30 样本（min_history）95% 置信：5% 分位落在排序后第 1.45 位，插值产出**样本中不存在的虚拟值**。若第 2 差样本 > 插值点，tail 只剩 1 个样本 → ES 退化为"最差单笔损失"；若第 2 差样本 ≤ 插值点，tail=2 个。**尾部样本数在 1/2 间抖动，ES 估计不连续**。memo §3.2 意图是"最差 (1-c) 比例收益的均值"（30×5%=1.5 个），与实现存在口径漂移。

注：`ES >= VaR` 不变量不受影响（同一插值点筛选，恒成立），故强制校验无法发现此问题。

**修复建议**：改用 `np.quantile(returns, 1-c, method='lower')`（取实有样本点），或排序后取 `sorted[:max(1, floor(n*(1-c)))]`；同步在 memo §3.2 补插值口径裁定。

## F2 [P1] VaRCalculator 静默过滤 NaN

**位置**：`src/zephyr/risk/core/var_calculator.py:469`

```python
arr = arr[~np.isnan(arr)]
if len(arr) < self._config.min_history: raise ...
```

**推演**：上游数据缺口产生 NaN → 静默剔除 → 剩余 ≥30 即照常出 VaR。**数据洞期间波动率样本被"幸存者化"**（缺的日子通常是停牌/极端行情——恰恰是高波动日），VaR 系统性偏低，且监控层无任何信号知悉样本被裁过。违 fail-closed 原则。

**修复建议**：NaN 剔除比例 >0 时至少 warning + 写入 VaRResult 新字段（如 `nan_dropped: int`）；比例超阈值（如 5%）直接 raise。数据洞场景应与 known_data_gaps.yaml 联动。

## F3 [P1] 幽灵持仓检测枚举不全（最危险幽灵漏报）

**位置**：`src/zephyr/risk/stop_loss.py:383-386`

```python
if qty != 0 and strategy_state.get(sym) == "CLOSED":   # 只覆盖"CLOSED"
```

**推演**：`strategy_state.get(sym)` 返回 `None`（策略侧**从无此标的记录**）时不报。而这正是最危险的幽灵：crash 丢状态 / 策略 universe 换血 / 券商端异常持仓——broker 有仓、系统完全无感知。Kill Switch OPEN（正常运行态）时情况 2 不兜底。**Crash-only 语义下（#95 QUANT-002 状态外部化未施工前）此缺口真实可达**：崩溃恢复后 strategy_state 为空 dict，全部 broker 持仓均为不可见仓位。

**修复建议**：补第三枚举——`strategy_state.get(sym) is None and qty != 0` → ghost_type="unknown_to_strategy"；或在调用侧约定 strategy_state 必须含全 universe 键（贵在全量初始化纪律）。与 #95 联动登记。

## F4 [P2] Inf 输入穿透 VaR 计算

**位置**：`var_calculator.py:463-473`

**推演**：`~np.isnan` 不滤 Inf。上游除零事故产出 Inf → mean/std/quantile 全污染 → VaR=nan/inf 静默传播进监控告警链。风控件应 fail-closed。

**修复建议**：`arr = arr[np.isfinite(arr)]`（同时滤 NaN+Inf，与 F2 合并修）。

## F5 [P2] RegimeMeta 死代码两则

**位置**：`regime_meta_allocator.py:632` + `:549-554`

**推演**：①L632 `if n_downside == 0` 不可达——L625 `n_downside < 15` 已拦截 return。②L549-554 "无法重分配"兜底路径数学不可达（归一化后 Σ=1，cap=0.4 时最多 2 个越 cap；全 ≤floor 与 Σ=1 矛盾）——已推演证明为防御性死路径，Σ=1.0 不变量实际安全。

**修复建议**：死代码删除或注释标记"防御性不可达"，降低后续维护者误读成本。非紧急。

## F6 [阴性] R2 双重折扣担心排除

`allocate()` L334-345：raw_allocation 不含 shrinkage → normalize+clip → effective_budget 最后乘一次 global_shrinkage。与文件头 INVARIANTS（L8/L36-39）"归一化约掉全局乘性因子"数学一致。**无双重折扣**。CRISIS floor 切换无状态残留（每次调用现算，frozen dataclass 返回）。

## F7 [阴性] R3 Kelly 核心正确

`_compute_kelly_fraction` L336-350：f*=(bp-q)/b 公式正确；f*≤0 截 0；p∉(0,1)/b≤0 显式报错（p=1 报错=保守正确，估计无必胜）。半 Kelly 上限链（0.5×f*+13 约束+10% 应急帽）完整。

---

## 未审透项（移交二审重点覆盖）

1. **R4 crash 恢复幂等性**：reconciliation_loop/position_reconciler 的重放路径——"重复恢复=重复成交"担心未证伪（需读事件溯源消费侧）
2. **R5 Kill Switch 清算幂等**：execute_kill_switch_liquidation 重复触发行为；多 Protocol 同刻触发除 regime/CRISIS（已定义）外，流动性危机 vs 回撤的汇聚仲裁
3. **R1 POT 厚尾拟合**（fit_pot L458+）：GPD ξ 估计的小样本稳定性未审
4. **FHS**：36 memo 提到的 FHS 在 var_calculator.py 未见实现（只有 parametric/historical/conservative_max 三法）——需确认 FHS 是远期项还是落在别处

## 审查者自陈局限

本审查由持有项目上下文的统筹会话执行——优势是未将有意设计误报为缺陷（如 32 memo 净额替代仲裁、n-1 分母口径均有 memo 裁定背书）；盲区是可能与原施工 AI 共享同一族假设。**F1-F4 的最终裁定建议等 Qwen3.8 Max 盲审报告到手后做差异比对**——若 Qwen 独立推出相同结论，置信度封顶。
