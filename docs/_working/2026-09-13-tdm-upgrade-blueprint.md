---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（15 条，摘录）**
> - L5: # TDM 升级蓝图 v0.2——分布预测嵌入+储备库板块一归口（GAP 解除，模块已建成）
> - L9: > **依赖声明（v0.2 更新）：车道 E 分布预测 MVP 已建成（lane_e_quantile_baseline.py），
> - L10: > UP-2..5 GAP 全部解除。模块已建：forward_stop_loss/risk_budget_allocator/
> - L15: ### UP-1 组合流·仓位管理升级：凯利动态仓位 ✅ 已建成
> - L19: - 状态：**已建成**（ba47d30c9c），单测 8 用例全绿；A/B 回测对比验证待跑。
> - L21: ### UP-2 出场流·前瞻概率止损 ✅ 已建成
> - （另有 9 条完成信号，见正文）
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L45: ## 消费端接线（待施工）
> - L47: UP-1..UP-5 模块已建成但尚未接入 TDM 消费端。接线步骤：
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 5 个，其中判废弃 0、路径漂移 0）+ commit 提及 5 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# TDM 升级蓝图 v0.2——分布预测嵌入+储备库板块一归口（GAP 解除，模块已建成）

> 来源：①Owner 2025-09 笔记（决策树×PDF 嵌入表+储备库板块一）；②主讨论稿 v3/v9。
> 方法：病菌寻路 SOP §3（设计稿落档，不碰真源 YAML）+ §6 防噪音四道闸逐条过。
> **依赖声明（v0.2 更新）：车道 E 分布预测 MVP 已建成（lane_e_quantile_baseline.py），
> UP-2..5 GAP 全部解除。模块已建：forward_stop_loss/risk_budget_allocator/
> sector_distribution_comparator/tail_hedge_signal——待消费端接线。**

## 候选条目（五条，按四道闸逐条过）

### UP-1 组合流·仓位管理升级：凯利动态仓位 ✅ 已建成
- 简版（Phase 1）：K 基于**滚动历史波动率**目标化；
- 完整版（Phase 2）：K=E(R)/σ²，E(R)/σ 来自车道 E 分布预测；
- 模块：src/zephyr/pf_alloc/core/vol_target_allocator.py（MOD-BT-082）
- 状态：**已建成**（ba47d30c9c），单测 8 用例全绿；A/B 回测对比验证待跑。

### UP-2 出场流·前瞻概率止损 ✅ 已建成
- 模块：src/zephyr/pf_alloc/core/forward_stop_loss.py（MOD-PA-020）
- 规则：滚动预测 P(跌)>65% → 触发止损评审（替代固定百分比止损）；
- 状态：**已建成**（211333c734），基础版 forward_stop_signal() + 复合评分版
  composite_stop_score()（三分布位点插值+左尾厚比）。
- 对应节点：TDM 出场流止盈止损节点（升级）。

### UP-3 组合流·前瞻风险预算 ✅ 已建成
- 模块：src/zephyr/pf_alloc/core/risk_budget_allocator.py（MOD-PA-022）
- 规则：预测 VaR/CVaR 作为各 sleeve 风险资本分配依据（前瞻式，替代历史回溯）；
- 三种模式：inverse_var / risk_parity / sharpe_weight；
- 状态：**已建成**（53fb3584c2），测试含边界/模式/空输入。

### UP-4 板块流·分布比较选优 ✅ 已建成
- 模块：src/zephyr/pf_alloc/core/sector_distribution_comparator.py（MOD-PA-023）
- 规则：各候选板块独立分布预测，按预测收益-风险比排序配置；
- 板块池：kline_index 已有 000001/000016/000300/000905/000852/399006；
- 状态：**已建成**（53fb3584c2），测试覆盖比较排序。

### UP-5 风控层·尾部对冲指令 ✅ 已建成
- 模块：src/zephyr/pf_alloc/core/tail_hedge_signal.py（MOD-PA-024）
- 规则：组合预测 CVaR 破阈值→生成对冲建议（信号仅供决策参考非执行指令）；
- 状态：**已建成**（53fb3584c2），测试含正常市场无对冲/暴跌触发对冲。

## 消费端接线（待施工）

UP-1..UP-5 模块已建成但尚未接入 TDM 消费端。接线步骤：
1. TDM 出场流节点（止盈止损）引用 forward_stop_loss 输出
2. TDM 组合流节点（仓位管理）引用 vol_target_allocator 输出
3. TDM 板块流节点（板块比较）引用 sector_distribution_comparator 输出
4. TDM 风控层节点（尾部对冲）引用 tail_hedge_signal 输出
5. 每个引用需 validation_method_registry 登记 + 阈值冻结

## 储备库文档六板块归口表

| 储备库板块 | 归口 |
|---|---|
| 一 风险与仓位 | ✅ 本蓝图 UP-1..UP-5（模块已建成）|
| 二 交易执行 | QMT 桥/执行域（非 TDM） |
| 三 微观结构研究 | 研究储备 + 工厂车道 E 特征候选 |
| 四 人机协作哲学 | 治理原则（已体现于宪法/寻路 SOP 四闸） |
| 五 前沿模型观察 | 研究雷达（不施工） |
| 六 另类数据 | 数据基建规划（数据工厂域） |

## 依赖链状态

车道 E 分布预测 MVP ✅ 已建成 → UP-1..UP-5 GAP 全部解除。
剩余依赖：无（全部模块可独立运行）。

## 落图批流程

按病菌寻路 SOP §3：四道前置检查 → 拆分三条件复核 → 设计稿转正式稿 →
批量落图（TDM YAML+node_verdict 台账同 commit）→ 四关验收 → 冻结版本通知施工轨。
每条落图时同步：validation_method_registry 登记验证方法 + 阈值冻结（禁挪门柱）。
