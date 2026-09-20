---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# LLM_QUANT_FACTORY 六件套对标——策略工厂镜子 2026-09-20

> 外部事实 `[外部]`：仓库真实存在（github.com/khakhasshi/LLM_QUANT_FACTORY）；架构声明=LLM 只产假设与研究意见，回测/检验/风控/交付由**确定性组件**执行；**License=PolyForm Noncommercial 1.0.0（2026-07-29 起，禁商用，非 OSI）**；63★/21 fork/35 commits，**末次 push 2026-08-05 已停更**。
> 总判定：**B——只学思想不抄代码**（license 禁商用）；本项目策略工厂与其同构，互为印证；真正值得拿的是它的"确定性组合优化"设计输入。

## 六件套对标表（内部现状 `[亲验]`）

| 其模块 | 本项目对应物 | 内部现状 | 对标结论 |
|--------|-------------|---------|---------|
| AutoAlpha 自动因子研发 | E1C 车道 C（gplearn MOD-BT-155 + 智能体 MOD-BT-158；`scripts/backtest/lane_c_formula_miner.py`/`lane_c2_agentic_miner.py`） | partial | **同构互证**：双方都收敛到"LLM 产假设、确定性引擎验证" |
| 因子知识库+同质化管理 | clone_guard（`src/zephyr/clone_guard/`，L0 advisory+L1 提交硬阻断） | **production** | **我们更强**（它只是聚类标注，我们是门禁级硬阻断） |
| AutoCombine LLM 辅助组合 | 无统一件（组合讨论散在 E4 组队/沙箱） | 缺 | 观察：LLM 辅助组合应保持 advisory 位，决策权在确定性层——与我们裁定口径一致 |
| **QuantCombine 确定性组合优化（SFFS/NSGA-II/Pareto）** | Sharpe2 组队（沙箱 CSV，1.541 已标 suspect）；FAC-E7 pending / FAC-E8 partial；pf_alloc 13 分配器 wiring=exempt | **无生产件** | **最大借鉴点**：E7/E8 设计时把 SFFS/NSGA-II/Pareto 前沿三件套列入设计输入 |
| 纯多回测/选股/模拟交易/策略管理 | E 线全链（回测/E7 前哨/模拟盘） | 齐（E7 pending） | 我们覆盖更全 |
| 连续记忆/研究日志/审计/实验谱系 | ruling_registry/experiment_registry/trial_ledger/registry_of_logs（98 载体）+ docs/_audit | 部分 | 谱系设施我们有，"连续记忆"（跨会话研究上下文）弱于它——AI 层 v2.0 OBJ_M 线已在治 |

## 行动项

1. FAC-E7/E8（模拟盘前哨/组装与资金分配）设计时：把 QuantCombine 的 SFFS/NSGA-II/Pareto 三算法作为确定性组合优化候选（只读其 README/论文思想，**因其 PolyForm NC license，禁止复制其代码**）。
2. 同质化管理无需动（clone_guard 领先）。
3. 该仓库已停更，不作依赖源，仅作一次性设计输入。
