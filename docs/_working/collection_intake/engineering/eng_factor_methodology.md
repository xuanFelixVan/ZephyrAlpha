---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# 因子工程方法论汇编与"Fast Start File"证伪 2026-09-20

> 收录剪报中的方法论类内容：可用者归档挂点，不可证伪者记录在案。文献核实见 factor_pool_comment_leads.md 附节（四篇 Factor Zoo 文献已 Crossref 逐字核实）。

## 1. 拥挤度轮动（判定 C P2）

- 机制：因子拥挤度轮动——用的人少→有效；挤入→失效；弃用→复活。"因子没有不能用，只有太拥挤不显著"。
- 内部 `[亲验]`：无拥挤度度量。行动：E4 出证维度增"拥挤度"（代理口径候选：因子多空两端换手异动、横截面相关度抬升、策略入池数量增速）；上下线信号挂 E4 放行档复核。

## 2. 降回撤双法 + WorldQuant MOE（判定 B——pf_alloc 接电时引用）

- 双法：①多策略多品种分散；②按近期市场数据动态变参。现代多策略基金两者结合。
- WorldQuant 模式：全球最优策略分散给上百 PM 优胜劣汰=MOE（mixture of experts）；低相关组合出理想 alpha（Ray Dalio 风险平价类比）。
- 内部 `[亲验]`：`src/zephyr/pf_alloc/` 有 risk_budget_allocator / vol_target_allocator / regime_bma_weighting / strategy_screener_3d / synergy_dedup 等 13 分配器，但 wiring_status=**exempt（纯库未接电）**，唯一接触点 daily_decision_orchestrator 只读 import。
- 行动：pf_alloc 接电（组合层立项）时，本文作为设计引用；MOE 结构对应本项目"策略赛马计分板+优胜劣汰"已有雏形（race 子命令）。

## 3. 组合使用三原则（存档）

单因子弱、组合强；关键=多样性与低相关；保留主观修改层（"要主观修改组合"）——与 Owner"组合层条件化"思路一致（bizmine 高波桶 MID 荒漠解先例 `[记忆]`）。

## 4. trade_when 条件调仓算子（判定 B 速赢）

`[外部]` 语义证实：`trade_when(trigger, alpha, exit)`——trigger 真时用 alpha 更新仓位；exit 真时清仓（优先级最高）；否则沿用原仓位；exit=-1 永不主动平。官方算子文档在 WorldQuant BRAIN 平台。
行动：E1C `config/factor_mining_whitelist.yaml` 增补条件调仓算子（等价语义），让"放量才调仓/破位即退出"类表达式可被挖掘。

## 5. 超级 Alpha + 内部撮合（存档）

101 论文：海量 alpha 整合为统一"超级阿尔法因子"，交易自动内部净额撮合省执行成本。挂点：执行层成本优化思想（与撮合 564 三态成本账同方向 `[记忆]`）。

## 6. 反方观点：信息维度论（存档）

"公开信息已 price-in；因子=提取规律性盈利信息；AI 时代规律被挖得差不多；除非有私有信息——大道至简长均线择时。"作为系统性反方观点存档：提示因子挖掘边际收益递减，组合层/执行层/数据壁垒三条腿要平衡。

## 7. "Anthropic Fast Start File"——证伪记录 `[外部]`

- 剪报声称：黑客松冠军开源方案、研究/产品/界面/运营四全自动部门流水线、半小时搭好、一天约 1.6 美元。
- 核查结论：**GitHub 全站精确短语 0 命中；Anthropic 公开黑客松获奖名单无此项目；全网无任何一手出处——判定不存在**（编造或张冠李戴）。
- 真实替代物：①Anthropic 官方工程博客《How we built our multi-agent research system》（orchestrator-worker 架构）；②Claude Code 官方 subagents 机制（`.claude/agents/`）。
- 本项目视角：四部门流水线的**排程思想**（串行排关键路径、并行任务同时跑、部门数不突破依赖链）早已内化——本项目多代理编排自产件在 `orchestrator/voting_first_multi_agent.py`、`intelligence/model_routing/cascade_orchestrator.py` 等 `[亲验]`，且通宵总包令"线内挖矿线间流水"即同一思想 `[记忆]`。**无需外采任何东西。**
