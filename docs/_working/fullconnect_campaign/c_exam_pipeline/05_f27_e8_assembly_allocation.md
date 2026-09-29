---
ttl: task_bound
title: F27 E8 组装与资金分配——L03 接线矿道案卷
session: zc-l03-20260927
updated: 2026-09-29
---

# F27 · E8 组装与资金分配

> 挖矿基册=01_strategy_factory/b2_f27_e8_assembly_allocation.md（SF-B）。本卷=09-27 独立复核+增量（09-24 业务日 marker 已落/毒丸=陈旧遗体/休市日缺口辨析）。

## 一、六向台账
| 向 | 实证锚点（09-27 实测） |
|----|------|
| 上游 | regime 日序（regime_snapshot_daily）；StrategyBook 读账本钱包；PIT 锚定四档表（allocation_inputs.load_anchored_cap，tuple/dict 双形态兼容治本注释 **在码实证 ：710-719**） |
| 下游 | alloc 三表（alloc_budget_daily/alloc_shrinkage_daily/alloc_budget_change_log）；sim_paper_ledger 钱包额度（**接线 diff 未落地维持**=E8-②）（已过时，见刷新批注——E8 袋 sleeve/再平衡/TDM 三面已落）；crisis_gate L1；TDM 组合流（F48 跨组欠账维持） |
| 自动触发 | maybe_emit_pf_alloc_daily 已投产维持（daily_kline 唤醒+trade_date 级幂等）；**marker 进展：pf_alloc_daily:2026-09-24 已落（09-25T00:42:31 写入，last_audit 实读）**——基册"09-24/25 日成验证待做"完成一半；**09-25/26/27 无 trade_date marker**：09-25 周五（中秋休市推断）+09-26/27 周末，下一预期 marker=trade_date 09-28（推断级，待 09-28 验证，见待裁注） |
| 真源注册表 | 图 FAC-E8 partial；MOD-PA-030 装配体（G15→G14 单向流）；MOD-PA-007/022/013/004/014/015；DDL=schemas/categories/alloc_*.py；TDM 17_f50 卷交叉：C3-03 装配体夜批已运行（RegimeMetaAllocator :1081 实例化）+"地图 note 待回填" |
| 门禁质量尺 | Σallocations=1.0 硬不变量；死成员显式剔除；全灭 fail-closed；现金三账闭合；alloc 三表只增+同日双写防 |
| 运行状态 | **绿转黄→黄收敛**。trade_date 09-15..09-24 八个业务日 marker 全在（基册记七日）；3 条 PIPE-20260923-* 毒丸 attempts=3/3/**6**（第三条又涨 3 次）仍占队——**但 09-23/24 trade_date marker 均在=毒丸已成陈旧遗体**（同日经再发射成功落 marker，事件未清队） |

## 二、子模块三级枚举
1. **代码面**：allocation_orchestrator.py（五模块链）；regime_meta_allocator.py；risk_budget_allocator.py（inverse_var/risk_parity/sharpe_weight）；maxdd_limit_allocator.py；strategy_correlation_gate.py（ρ>0.8 减半/>0.9 归零）；allocation_inputs.py（治本注释在码）；crisis_gate.py；vol_target_allocator.py。**IC_IR 加权件与资金渐进爬坡件仍无实件**（基册定性维持，待裁②之一）。
2. **注册表/文档面**：FAC-E8 图节点 partial；MOD-PA-030 CONSUMERS 自述（钱包接线待主会话）；TDM 17_f50 卷"地图 note 待回填"注记（TDM 域在途修正，非本卷处置）。
3. **数据面**：last_audit.json 八日 marker 实读；pending 3 毒丸（id/attempts/last_error=RuntimeError pf_alloc 日分配失败 rc=1）；alloc 三表行数本卷未直查（CH 面，基册口径）。

## 三、接线四态独立复核
- 总册 partial → **维持 partial**（装配体/事件链/三表/幂等闸 built；差：钱包接线+sleeve 落库语义+TDM 对接+两法注件）。
- **骨架勘误**：①"3 枚毒丸待重放"表述需修正——09-23/24 marker 已在，毒丸事件为**陈旧遗体非待办**（重放会撞 trade_date 幂等闸无害，清队即可）；②基册"09-24 起无 marker"已被 09-24 marker 推翻。
- L02/总册交叉：F27 partial 与今日清单 §1.4 一致。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 钱包额度接线未落地（预算≠拿额） | MOD-PA-030 自述 | 落地接线 diff（分配→钱包开户额度对齐）；S-M | **P0** |
| 2 | 3 毒丸遗体占队（attempts 3/3/6） | pending 实读 | 清队卫生项（幂等闸保护下无实害）；与 BP-3 同班 drain | P1 |
| 3 | 09-25/26/27 无 marker（休市推断） | last_audit+日历 | 待 09-28 自然唤醒验证；若 09-28 仍无 marker=升级排查 | P2（观察） |
| 4 | IC_IR 加权/资金爬坡两法注无实件 | 全仓 grep 维持 | 待裁：降级演进方向或立项（sharpe_weight 为最接近替代） | P2（待裁） |
| 5 | sleeve 落库语义+TDM 对接 | alloc 表 strategy 粒度 | sleeve 列裁定+F48 消费者登记（跨组） | P2 |

## 五、自审闸三态
**挖干可施工（复核维持+两勘误）**。治本注释在码实证；八日 marker 链实证；毒丸遗体定性修正；休市缺口=推断进待裁注（万无一失纪律：不判"断链"也不判"无恙"，以 09-28 验证为准）。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cat .runtime/strategy_pipeline/last_audit.json | tr ',' '\n' | grep "pf_alloc_daily" | tail -10
python -c "import json;[print(e['id'],e['attempts'],e.get('poison')) for e in map(json.loads,open('.runtime/strategy_pipeline/pending_events.jsonl',encoding='utf-8')) if e['kind']=='pf_alloc_daily']"
sed -n '710,720p' src/zephyr/pf_alloc/allocation_inputs.py    # 治本注释在码
python -m pytest tests/pf_alloc/test_allocation_chain.py -q
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更
- `a349ddc1fe`（09-28 E8/E9袋复活·21 件）：**F27 sleeve 装配+再平衡调度+TDM 对接**——allocation_orchestrator.py（+16）+schemas/categories/alloc_budget_daily.py（+24）+tests/pf_alloc/test_sleeve_provenance.py（156 行）；rebalance_check_runner.py（242 行新件）+algo_flow/rebalance_check_runner.yaml+src/zephyr/data/config/schedule.yaml（+12）+scheduler.py（+28）+tests/data/test_pf_alloc_rebalance_check_wiring.py（92 行）；config/strategy_production_map.yaml（+17）。
- `082d4591e7`（09-29 F34 L9 消费接线）：pf_alloc 增 L9 知识供给就绪度闸（allocation_inputs.load_l9_readiness；黄 0.90/红 0.70 工程缺省待 Owner 签批，一键失效开关在案）——清单外新增接线面。
- 数据面：**pf_alloc_daily:2026-09-28 marker 已落**（last_audit 实读）——缺口 3 的 09-28 唤醒验证通过；3 条 PIPE-20260923 毒丸 attempts 3/3/6 维持（陈旧遗体判定维持）。

### 缺口清单状态修订
- 缺口 3（休市缺口观察）：**翻面**——09-28 trade_date marker 在，休市推断成立、链未断。
- 缺口 5（sleeve 落库语义+TDM 对接）：**已施工**（a349ddc1fe sleeve provenance+strategy_production_map 对接）。
- 缺口 1（钱包额度接线）：a349ddc1fe 的 allocation_orchestrator +16 行为 sleeve 装配面，钱包开户额度对齐未见直接证据——维持 P0 待复核。
- 缺口 2（毒丸清队）／4（IC_IR/爬坡两法待裁）：维持。

### 自审闸三态
- **挖干可施工（维持）**；§一"接线 diff 未落地维持=E8-②"**已过时**（E8 袋已落 sleeve/再平衡/TDM 三面，见上）；marker 链更新至 09-28（八日→+1）。
