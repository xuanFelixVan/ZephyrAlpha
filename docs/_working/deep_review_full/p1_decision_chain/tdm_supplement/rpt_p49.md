---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——资金分配多标的
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：资金分配多标的（P49）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_fundamental/capital/capital_allocator.py`（42 行 re-export shim；审查范围含其真源链：strategy/capital_allocator.py（二次 shim，41 行）→ gen/aggregator_base.py:83 CapitalAllocatorBase（ABC）→ strategy/implementations/default_capital_allocator.py（唯一具体实现，154 行））
- TDM 节点: TDM-E-L4-04（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-L03-001；节点"资金分配多标的"实际映射到双层兼容 shim+一个零消费 ABC——TDM 落图应指向 default_capital_allocator 或 C01/C02 域分配器（见 §5）
- 生产调用方: **全链 0：ABC 零生产实现消费；DefaultCapitalAllocator 唯一实例化=`scripts/construction/demo_e2e_pipeline.py:188`（演示脚本）；双层 shim 仅被包 `capital/__init__.py:18` 门面再导出；[CONSUMERS] 头注空=诚实但 [MATURITY]=production 虚标；[TESTS] 空=无专属测试（仅 e2e/import 链测试间接覆盖）**
- 测试文件: **无专属测试**（头注 [TESTS] 空；grep 仅 tests/governance/trading/test_e2e_pipeline.py 与 tests/phase/test_phase_c_import_chain.py 间接触及）——测试缺口在册

## 1 对象快照

四层链：双层兼容 shim→ABC（allocate 抽象+三枚举方法声明）→DefaultCapitalAllocator（四法：等权/信号加权/Sharpe（confidence 代理）/风险平价（|signal|/3 波动代理）+min_signal 0.2 过滤+单策略 0.40 截顶）。PIT 纪律亮点：allocation_date 取信号 as_of 禁 wall-clock（:104-106 注释声明）。范围排除：pf_alloc 域分配器（C01/C02 已审域——本件与彼为不同层：本件=策略间资本分配 ABC，彼=组合层资金分配）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：**截顶不重归一→欠部署：`min(base,0.40)` 后无再归一（:113-115）——n=1 时 sum=0.40、n=2 时 sum=0.80，total_allocated_weight<1.0 静默欠部署**（ABC 注释自declared"total_allocated_weight 通常=1.0" :92 与实现矛盾）；signal/sharpe/risk_parity 三法同患（单点 >40% 即触发）；与 C01 ledger"AGGRESSIVE 单批欠部署"同族模式 | default_capital_allocator.py:92,113-137 | P2 | `DefaultCapitalAllocator().allocate([单信号], 'k')` 观察 total=0.4 |
| A 深度 | 边界②：`_sharpe_alloc` 用 `s.confidence or 0.5`（:125）——**confidence=0.0（合法值）被 or 吞成 0.5**（falsy 替换语义缺陷：零置信策略获中位权重）；NaN confidence：NaN or 0.5=NaN 传播→权重 NaN；_risk_parity 的 |signal|/3 波动代理为未声明启发式（信号幅值≠波动率，量纲语义未文档化） | :125,131-137 | P3 | confidence=0.0 与 0.5 两实例对拍权重 |
| A 深度 | PIT③：allocation_date=信号 as_of（:104-106 纪律正确）；空信号回退 wall-clock 有"仅实时路径"注释（:142-143）——回测空信号路径会注入当日日期=回测 PIT 破口（注释自declared边界但未机械阻断） | :104-106,139-150 | P3 | 空信号+回测语境观察 allocation_date=今天 |
| B 上游 | checklist #6 断供：输入=SynthesizedSignal 列表注入；空列表→空分配（:81-82）；全信号低于阈值→空分配保留 PIT（:86-88 降级正确）；G01 已实证 signal_synthesizer 为 stub（恒空 registry）——**上游合成信号生产端是 stub（G01 收口结论），本件 allocate 在生产中永收到空列表** | G01 报告链 | P2(链路缺口) | 对照 rpt_g01 |
| C 下游 | **全链孤儿裁定**：产消两端均未接线（上游 stub+下游 D_PORTFOLIO_CORE 消费未建）；[TESTS] 空；爆炸半径=策略间资本权重错配（接线后直达资金语义，Owner 门位级） | grep 证据 | P1(接线期) | `grep -rn "DefaultCapitalAllocator(\|CapitalAllocatorBase" src/ scripts/ --include=*.py`（仅 demo+定义） |
| D 旁系 | **checklist #4 双承载实锤：CTR-P1-003 契约两份独立 codegen 产物——`shared/contracts/capital_allocation_result.py` 与 `trading/trading_contracts/execution/capital_allocation_result.py` 同名同类同 CODGEN 标记，字段序不同（strategy_allocations 第 7 vs 第 5 位）——位置参数构造在两定义间静默错位赋值**（`CTR(d,0.4,'m','k',{})` 在 shared 版会把 {} 赋给 rebalance_threshold）；shim 头注"禁止重复定义——多真源同步漂移根因"（:30-31）与 codegen 自身双产物形成反讽 | shared/contracts/capital_allocation_result.py:44-52 vs trading/trading_contracts/execution/capital_allocation_result.py:25-33 | P2 | 两文件字段序 diff+位置构造对拍 |
| E 对抗 | 五问：①静默失败=欠部署静默（total<1 无告警）②假阳性=confidence=0 获 0.5 权重③断供=上游 stub→恒空分配④重触发=idempotency_key 由调用方传入本件不校验唯一性（幂等键语义悬空——键冲突无检测）⑤时序=PIT 纪律好（wall-clock 回退除外） | :105-111 | P3 | 同 key 调两次观察无去重 |
| F 新鲜度 | 等权/信号加权/Sharpe/风险平价四法为策略间资本分配教科书谱系（Grinold-Kahn 族，对照检索见 rpt_p38 F 轴 URL；风险平价正源见 W05 收口立卡 Quantpedia/PO book）；**对等已有**；实现量级为 MVP 简化（风险平价用信号幅值代理波动=名实差距需声明） | 同族结论（URL 见 rpt_p38 §3） | 通过（同族复用） | — |

## 3 SOTA 对照

- 对等已有：四分配法为标准方法学；风险平价的信号幅值代理为实现简化非文献口径（与 W05 真 ERC 立卡项同题，建议一并裁定）。

## 4 缺陷清单

1. P2：**CTR-P1-003 契约双 codegen 产物字段序漂移**（checklist #4 位置构造错位风险）——建议 codegen 收敛单产物+另一路径 re-export；验证法=§2 D 轴 diff。
2. P2：截顶不重归一欠部署（n<3 时 total<1.0 静默）——与 C01 同族模式，建议截顶后按比例重归一或显式披露欠部署比例；验证法=单信号 allocate 观察 total=0.4。
3. P1（接线期）：全链孤儿（上游 G01 stub+零专属测试+demo 唯一消费）；验证法=§2 C 轴 grep。
4. P3：confidence or 0.5 falsy 吞零；NaN 权重传播；风险平价代理量纲未声明；空信号 wall-clock 回测 PIT 破口；幂等键无冲突检测。

## 5 挂起疑问

- TDM-E-L4-04 节点映射到双层 shim 是否恰当——真实现是 default_capital_allocator（亦孤儿），且 pf_alloc 域已有生产层分配器（C01 链）——**同一"资金分配"语义域三层承载（本件/pf_alloc/position 划拨链），职责切分需 Owner 裁定**（本件与 C02 multi_strategy_capital_allocator 的语义边界尤其含混：均为"多策略→资本权重"）。

## 6 完备性自评

六轴全查（F 同族复用）。长尾：①SynthesizedSignal 契约字段未审（shared/contracts 生成件）②demo_e2e 管道的 allocator 分支未审③零专属测试=数学四问无法以测试对照（全手算）。

## 7 收口裁定（收口方填）
