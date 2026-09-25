---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F27 E8 组装与资金分配——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F27 · E8 组装与资金分配

> 组 SF·策略工厂供给链 B 后半册 5/7。上游 F26（E7 幸存者名单），下游 F74（转正汇总，PR 组）/F48（TDM 组合流）。
> 环节真源：config/strategy_production_map.yaml FAC-E8（build_status: partial 非 built——sleeve 装配落库+再平衡调度+TDM 对接未闭环）。

## 一、环节定义与边界

一句话：多策略 sleeve 装配（Owner"多策略赛马"方针的赛道本体）——regime 切换选 sleeve+风险平价/等风险贡献权重+IC_IR 加权禁朴素等权+资金渐进爬坡（drawdown 控制）。
供料方：E7 幸存者（策略池）、regime 快照（MOD-REGIME-001，regime_snapshot_daily 日更）、行情/净值面。消费方：alloc 三表（c1_backtest.alloc_budget_daily 等）、sim_paper_ledger 钱包额度、TDM 组合流（F48）。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | ①regime 日序（regime_snapshot_daily marker 09-15..09-24 连日在 last_audit.json）；②策略书 StrategyBook（LedgerStrategyBook 读账本钱包）；③PIT 锚定四档表（allocation_inputs.load_anchored_cap：trade_date≤当日禁未来函数，退化三态留痕）；④教材/alpha 面缺=.fail-closed |
| 下游消费 | ①alloc 三表=alloc_budget_daily/alloc_shrinkage_daily/alloc_budget_change_log（allocation_persistence.py:156-160 TABLE_NAMES 实测；只增不改）；②sim_paper_ledger 钱包额度（MOD-PA-030 CONSUMERS 自述"唯一生产消费方——接线 diff 待主会话落地"）；③crisis_gate L1（crisis_block_check，阻断日只 skip 不落 marker、解除后同日可重放） |
| 自动化触发 | **已接线且已投产**：maybe_emit_pf_alloc_daily=pipeline_events.py:771（daily_kline SUCCESS 唤醒、先于 sim_ledger_daily 入队、业务日=resolve_pf_alloc_trade_date 禁墙钟猜日、trade_date 级 marker 永久幂等闸、子进程 900s 有界）；此前"消而不产"（有派发/执行体/幂等闸却无发射方、alloc 三表恒 0 行）已由清单 #15 治本 |
| 真源与注册表 | 图节点 FAC-E8；MOD-PA-002..024 族+MOD-PA-030 装配体（src/zephyr/pf_alloc/allocation_orchestrator.py，G15→G14 单向数据流：regime→RegimeMetaAllocator→BudgetChangeHandler→StrategyBook→AdjudicationCenter→BatchedPositionBuilder）；MOD-PA-007 消费 MOD-REGIME-001；DDL 真源=schemas/categories/alloc_*.py |
| 门禁与质量尺 | Σ allocations=1.0 硬不变量（装配后 verify_allocation_invariants 复核）；死成员显式剔除留痕 budget=0、全灭面板 fail-closed 抛 AllocationInputError 禁静默等权；Σ effective_budget≤global_shrinkage≤1.0；现金三账闭合（deployed+cash_drag+unallocated=portfolio_total，cash_weight≥0.5 warning）；资金常量经 AllocationConfig 禁硬编码；alloc 三表只增不改+同日双写防（trade_date marker） |
| 当前运行状态 | **绿转黄（已投产、带 3 枚毒丸待清）**。证据：①pf_alloc_daily 成功 marker：trade_date 09-15/16/17/18/21/22/23 七个业务日在 last_audit.json（2026-09-25 实测）；②**3 条毒丸** PIPE-20260923-*：`RuntimeError: pf_alloc 日分配失败 rc=1`——根因=alloc 锚定档行 tuple 调 .get() AttributeError（allocation_inputs.py:702 一带）；**已修**：2026-09-24 st-gpu-final 治本注释在码（:715-719 dict/tuple 双形态兼容）；毒丸留档待重放，last_receipt.json 实测三次 poison_held |

## 三、子模块清单

| 模块 | 是什么 | 入口 | 状态 |
|------|--------|------|------|
| MOD-PA-030 allocation_orchestrator | 五模块链装配体（本环节治本件，PFA-1 判"链从未被组装"的回应） | src/zephyr/pf_alloc/allocation_orchestrator.py | built（生产日更 7 日实证） |
| MOD-PA-007 regime_meta_allocator | regime 元分配（消费 MOD-REGIME-001） | src/zephyr/pf_alloc/core/regime_meta_allocator.py | built |
| MOD-PA-022 risk_budget_allocator | 风险预算三模式（inverse_var/risk_parity/sharpe_weight） | src/zephyr/pf_alloc/core/risk_budget_allocator.py:29 | built |
| MOD-PA-013 maxdd_limit_allocator | 回撤限额 | src/zephyr/pf_alloc/core/maxdd_limit_allocator.py | built |
| MOD-PA-004 strategy_correlation_gate | 相关性闸（ρ>0.8 减半/>0.9 归零阈值体系，MOD-PF-007 复用） | src/zephyr/pf_alloc/core/strategy_correlation_gate.py | built |
| MOD-PA-014/015 strategy_screener_3d/regime_bma_weighting | 三维筛选/BMA 加权 | pf_alloc/core/ | built |
| allocation_inputs/persistence/config | PIT 输入/三表持久化/配置真值 | pf_alloc/allocation_*.py | built（毒丸根因已修待重放） |
| crisis_gate | L1 危机闸（阻断分配 fail-closed） | src/zephyr/pf_alloc/crisis_gate.py | built（crisis_gate_log 表在 schemas） |
| vol_target_allocator | 波动目标权重 | pf_alloc/core/vol_target_allocator.py | built |
| **IC_IR 加权件** | 图上法注"IC_IR 加权禁朴素等权" | **无实件**（全仓 ic_ir 仅 limit_up 打分器，无关） | **缺**（sharpe_weight 模式为最接近替代，口径待裁） |
| **资金渐进爬坡件** | capital_ramp（drawdown 控制爬坡） | 无独立实件（F06 配方轴 K_capital_ramp=lump 仅为回测口径） | **缺/待裁** |

## 四、堵点与病灶

1. **3 枚毒丸+09-24 起无 marker**（现象=journal 三条 attempts 满格 poison_held，last_audit 最后 pf_alloc marker=09-23；根因=tuple.get() 已修（09-24 治本注释），毒丸按设计不再自动重试；修法=修复后人工 `python -m zephyr.strategy_pipeline.pipeline_events drain` 重放（marker 未落，trade_date 级幂等闸天然防双写）；工作量=分钟级操作+一次验证；本车道可修=是，建议 Owner 派工与 BP-3 同一班 drain）。
2. **钱包额度接线未落地**：MOD-PA-030 自述 sim_paper_ledger 接线 diff 待主会话落地——分配链产出预算但纸面钱包未按预算拿额度，E8→账本半开（BP 前置清单 E8-②）。
3. **sleeve 语义落库待裁**：alloc_budget_daily 按 strategy 粒度落行，"sleeve"层（regime 组）是否落表/落哪列未定义——图上 partial 判定正确。
4. **TDM 组合流对接**：alloc_budget_daily 无 TDM 侧消费实件（F48 归 TD 组核）——跨组欠账登记。

## 五、提速与合并机会

- maybe_emit_pf_alloc_daily 与 SIM_DAILY_WAKE_TASKS 同波唤醒，已合并（正例）。
- 锚定档查询与 regime 快照同属"日晨只读面"，可合并一次采集（S 级收益）。

## 六、自审闸三态

**挖干可施工**。装配体+事件链+三表+幂等闸全实证；毒丸有根因+已修+重放路径；两项图上法注差件（IC_IR 加权/资金爬坡）已定性=待裁（裁"降级为演进方向"或"立项"）；剩余施工=钱包接线+TDM 对接（前置清单 E8 八项）。partial 判定维持，差件清单齐。

## 七、复核命令（10 分钟）

```bash
cat .runtime/strategy_pipeline/last_audit.json | tr ',' '\n' | grep pf_alloc     # 7 日成功 marker
python -c "import json;[print(e['id'],e['attempts'],(e.get('last_error') or '')[:80]) for e in map(json.loads,open('.runtime/strategy_pipeline/pending_events.jsonl',encoding='utf-8')) if e['kind']=='pf_alloc_daily']"  # 3 毒丸
sed -n '680,725p' src/zephyr/pf_alloc/allocation_inputs.py                        # 治本注释在码
sed -n '1,40p' src/zephyr/pf_alloc/allocation_orchestrator.py                     # 装配体契约头
python -m pytest tests/pf_alloc/test_allocation_chain.py -q                       # 链路测试
```
