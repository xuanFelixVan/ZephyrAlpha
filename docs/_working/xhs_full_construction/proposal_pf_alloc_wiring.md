---
ttl: task_bound
session: st-xhs-full-20260922
topic: xhs_full_construction_20260922
---

# 组合层接电立项文档（工单 #9+#16，呈 Owner 批）

> 工单：#9+#16 合并（B，最大件）。输入=eng_quantcombine_idea_mining.md §7 十步蓝图+§8 Owner 修正案（2026-09-20 拍板"统一考尺，分卷考试"）+eng_benchmark_llm_quant_factory.md（LLM_QUANT_FACTORY=外仓禁商用，只学思想）。前置已解除：裁定#392 D-10（pf_alloc 13 分配器 wiring=exempt → 接电授权路opened）。

## 一、现状一句话

pf_alloc 13 分配器（逆波动/风险预算/波动率目标等"权重菜单"）已建成并测试在册，但 wiring=exempt=零调用方——组合层不出数；上游 E4 放行档策略长期为零，接电后也无米下锅。**接电分两段：管道先通电（本立项），米后到（考试链毕业策略）**。

## 二、立什么（三件，全部思想重建不抄代码）

### W-1 统一考尺重评器（尺子）
- 职能：对候选策略/因子统一口径重评——同一执行代理、同一成本模型（T+1 土规）、同一 PIT 数据源，输出可比分数。落点=调用既有 run_strategy_validation（MOD-BT-001）+promotion_combo_gate（G2 四阈值），不新建回测器。
- 输入：E4 出证记录+联赛档案（league_registry 已建成）。

### W-2 分卷考试器（Owner 修正案核心）
- 职能：按 regime 标签（anchored_state_machine 四档，裁定#230/#231 已验）把候选因子/策略分科——震荡卷/主升浪卷/下跌卷分别重评，**单科排名+跨科稳健性并报**。
- 落点=regime_validation 包扩 C5 分卷对比器（c1_comparator 同族），零新框架。
- 铁律：同一时戳内禁循环依赖；跨时戳反馈是特性（五角星死循环→时间分层定案已批）。

### W-3 分科组队与切换接线（队伍）
- 职能：组合层按状态各建一队（pf_alloc 分配器入参=分卷考出的单科队伍），regime 切换器换状态=换队伍；allocation_orchestrator 从 exempt 转接电（事件触发，禁 cron，沿 STAGE 4b 先例）。
- 硬门禁一票否决照搬：crisis_gate/crisis_shrinkage 轴在队前不在队后（裁定#229 约束③ L1 总闸不动）。

## 三、施工分期与验收（预注册，先冻结后跑）

| 期 | 交付 | 写域 | 验收门 |
|----|------|------|--------|
| P1 | W-1 统一考尺重评器+测试 | regime_validation/、scripts/backtest/ | 同一候选在旧尺/新尺下分数可比性对账报告；两轮零 |
| P2 | W-2 分卷对比器+regime 分段标签接线 | regime_validation/ | 合成数据三卷分段正确性红蓝；真实候选≥5 条分卷报告样本 |
| P3 | W-3 orchestrator 接电+分科组队 | pf_alloc/、strategy_pipeline/ | 组合层出数（allocation 日频产物非空）；exempt 标记摘除；crisis 闸前臂数据链验证 |
| P4 | 端到端：毕业策略→分卷考试→组队→组合出数→promotion 建议 | 全链 | G2 四阈值+分卷排名联合报告呈 Owner；模拟盘纸面联动 |

依赖：W-2 依赖 regime 夜批（anchored_state_build 已 6+ 交易日零缺勤）；P3 接电动作=production 流转属 Owner 门位（risk_tier_registry），届时逐项请批。

## 四、回流 Owner 决策点（三项）

1. **批次排序**：P1→P4 顺序 vs 先 P3 空转接电（无米空转不推荐）——请拍板。
2. **4440 因子判死**：eng 文档 §3 提及的既有 4440 候选池是否随统一考尺重判（与 IBT 整改方案 MAX-REMEDIATION-PLAN ⑥降换手改造联动）——请拍板。
3. **PP-001 生产配比**：分科队伍切换后 PP-001 排班表配比参数（每状态各队资金占比）——P3 前请给方向。

## 五、净零与合规

- 零新框架：W-1/2/3 全部落既有包（regime_validation/pf_alloc/strategy_pipeline）；QuantCombine 十步蓝图只取"确定性选人+菜单定权+硬门禁否决"三思想；LLM_QUANT_FACTORY 只学思想禁抄代码（PolyForm NC，对标档已立）。
- 本立项文档=工单 #9+#16 本班唯一交付物；**批文前零接电施工**（wiring=exempt 维持）。
