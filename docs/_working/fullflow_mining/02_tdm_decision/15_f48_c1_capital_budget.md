---
ttl: task_bound
title: F48 C1 预算切分——TDM 组合流 C1 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F48 C1 预算切分（TDM-F-C1，组合流门户）

> **一句话**：总仓位预算按情绪六段灰度带切给各 sleeve（Millennium pod 单体版）；带内插值非查表，尾部预备金永不投出。**B 半唯一全链自动运行段的上游门户。**
> **上游**：F27 sleeve 组装/F71 池基、L1-AGG 六段 broadcast、C3-03 月度调权 feedback。**下游**：F-C2 组合聚合、C2-04 budget 三级。

## 一、环节定义与边界
- C1=预算带判定+切分（gate 型节点）；运行载体=pf_alloc 分配链（allocation_orchestrator MOD-PA-030），非节点字面上的 multi_strategy_capital_allocator 单件。

## 二、状态机血肉
| 判定面 | 规则 |
|--------|------|
| 六段预算带（v1.2.1 Owner 裁定灰度区间） | capitulation 0-10%（只试错）/accumulation 20-30%/ignition 30-50%/expansion 50-70%（verified 后 earned 上探 70-80%）/euphoria ≤30%（只卖不买）/distribution 0%（空仓）；带内实际仓位=状态分布加权插值 |
| 过渡带与预备金 | 最大隶属度<60% 预算×0.5-0.7；尾部预备金 10-15% 永不投出 |
| 切入 distribution | D98 终裁=Tier3 立即强裁（绕过 Tier2 收敛窗）；earned 存量降档日减半、7 交易日归位新带 |
| D88 预备金三件 | 存放分层（GC001 一层/T+1 短债一层）+动用条件≥2 条才可动用+回补规则；月报现金贡献行 |
| UP-3 前瞻风险预算（trial） | 各 sleeve 预测 VaR/CVaR 作带内再分配（DAL-RISK-BUDGET：inverse_var/risk_parity/sharpe_weight，权重和=1.0）；预算带仍为上限，与 C3-01 历史 Component VaR 双口径并存 |
| ANCHORED_CAP（2026-09-23 a54997e221 新增） | PIT 读 c1_backtest.regime_state_anchored 最新行，cap=1−0.70×clamp((vol_pct−0.30)/0.70,0,1)；旁路/无行/陈旧>7 日历日=applied False 不盲用；组合层与总暴露取 min 只减不加；一键切回=data/runtime/anchored_cap.disabled；回滚窗至 2026-10-23 |

## 三、六向台账
- **上游输入**：L1-AGG（daily broadcast，edge 实测）、C3-03 调权（feedback T-1）、PP-001 配置（allocation_inputs.load_pp001_plan）。
- **下游消费**：F-C2 sequence+C2-04 feed；**运行时真消费=daily_decision_orchestrator**（读 alloc_budget_daily，预算无来源=ctx.degrade D3_budget_run_missing 不出预算——消费端 fail-closed 语义实测于 daily_decision_orchestrator.py:619-621）。
- **自动化触发**：**事件触发合规链**（宪法 §9.3）——daily_loop_master_switch._stage_pf_alloc → pipeline_events.maybe_emit_pf_alloc_daily（"pf_alloc 日分配的唯一自动产出者"，行情日件 SUCCESS 自然唤醒，crisis_block_check fail-closed 不入队）→ `python -m zephyr.pf_alloc.allocation_orchestrator`（一次性装配体非定时器）→ alloc_budget_daily 落表。
- **真源与注册表**：trading_decision_map.yaml:3726-3757；DAL-BUDGET-BAND（**design、code_ref=null——带表数值只存在于 yaml 注释，无代码承载，缺口**）；DAL-RISK-BUDGET（trial）。
- **门禁与质量尺**：node_type=gate；crisis_gate.yaml 危机短路（裁定#392 D5）。
- **当前运行状态**：**绿（paper 域）**——git a54997e221 自述"夜批 09-14..09-22 七个交易日零缺勤+当日更新"；alloc_budget_daily 为空时下游拒绝出预算（D3 降级留痕）。

## 四、子模块清单
| 模块 | 行数 | 角色 | 状态 |
|------|------|------|------|
| pf_alloc/core/multi_strategy_capital_allocator.py（MOD-PA-003） | 307 | 节点字面锚；消费=signal_weight_adjuster | 在盘 |
| pf_alloc/allocation_orchestrator.py（MOD-PA-030） | ~1400 | 分配链装配体（regime→RMA→BCH→StrategyBook→AdjudicationCenter） | wired+夜批运行 |
| pf_alloc/allocation_inputs.py / allocation_persistence.py / crisis_gate.py | — | 供件/落表/危机闸 | wired |
| pf_alloc/core/risk_budget_allocator.py（DAL-RISK-BUDGET） | 96 | UP-3 trial | 休眠 |

## 五、堵点与病灶
1. **DAL-BUDGET-BAND 无代码承载**（六段带数值在地图注释而非代码/配置真源；修法=带表落 config 或 allocation_inputs 常量+登记真源指针；量级 0.5 天；本车道可修）。
2. **PP-001 权重演进计划未启动**（等权→逆波动率→半 Kelly+HRP→拼装回测归因；当前静态配置）。
3. **UP-3 前瞻预算 trial 休眠**（与 DAL-FWD-STOP/TAIL-HEDGE 同批，待回测验证）。
4. **C1 BT-P3-036 对象 plan=null**——组合归因验证（portfolio_attribution）未跑。

## 六、提速与合并机会
C1 预算带判定与 daily_decision_orchestrator 内 budget_band 解析（L414-428 sell_only/transition 语义）同源——禁第二处实现带表；anchored_cap 与旧 HMM 双轨对比器全量保留（回滚窗 2026-10-23 前勿删旧链）。

## 七、自审闸三态
**挖干可施工**（B 半唯一有夜批运行证据的环节；缺口=带表代码化+验证）。

## 八、复核命令
```bash
git log --oneline -1 -- src/zephyr/pf_alloc/allocation_orchestrator.py   # a54997e221 夜批证据
grep -n "maybe_emit_pf_alloc_daily" src/zephyr/strategy_pipeline/pipeline_events.py | head -2
grep -n "budget_run_missing" src/zephyr/strategy_pipeline/daily_decision_orchestrator.py
```
