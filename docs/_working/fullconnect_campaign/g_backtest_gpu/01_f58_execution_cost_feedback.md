---
ttl: task_bound
title: "F58 执行成本反馈——执行质量评分→选型回写（G4 增长批闭环）"
session: zc-l07-20260927
updated: 2026-09-29
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F58 · 执行成本反馈（总册状态 partial/P1；本卷独立复核=确认 partial，断链一米未接）（断链已于 09-28 T 袋码面闭合——已过时，见刷新批注）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | 成交回报 vs 发单前成本预估（TDM-E-L4-09 预估）；滑点按冲击/时机/价差三分量拆解由 slippage_analyzer 供（其 CONSUMERS 头注实锚 `services/slippage_analyzer.py:5` "MOD-XS-018(ExecutionQualityScorer, 消费 SlippageResult)"）；数据源 DS-008（TDM 节点 data_refs） |
| 下游消费 | TDM 边 `L4-14→L4-06 feedback`（trading_decision_map.yaml:5352，payload=feedback，lag T-1）→ 执行算法选择器换算法；间接 F28 归因。**码面实测：algo_execution_selector.py（677 行）零处引用 execution_quality/scorer（本日 grep 复证）** |
| 自动化触发 | 节点 activation=postmarket（yaml:2559）；无计划任务无常驻——属盘后事件位，当前零外部装配（ex_sor 全族生产不可达，M7-05 已判"传递性不可达"） |
| 真源与注册表 | 节点=config/trading_decision_map.yaml:2536（TDM-E-L4-14，module_ref=execution_quality_scorer.py，module_id=MOD-XS-018，note_confirmed 2026-09-16）；蓝图=docs/03_modules/_domain_ex_sor/execution_quality_scorer/blueprint.md；G4 出处=docs/_working/2026-09-09-tdm-growth-blueprint.md:112/242（"G4 执行成本反馈闭环"，增长批2 落图 2026-09-10，施工清单立 C14 接线待排期） |
| 门禁与质量尺 | 质量三档（好/可/差）=scorer 判据（f41 册 §三"判据-码面差异=一致"）；tests/ex_sor/test_execution_quality_scorer.py 在册（本班禁实跑只数）；scorer 532 行 production |
| 当前运行状态 | **partial 确认**：零件三件全 production（scorer 532 行/selector 677 行/slippage_analyzer），TDM 边已落图，但**选择器零消费评分=闭环最后一米未接**（节点 algo_note 自认"断链实证 2026-09-10"；本日独立复证同判） |

## 二、子模块三级枚举（域→子包→件，本日实扫）

- **ex_sor.services**（10 .py 含 __init__）：execution_quality_scorer.py（532 行，本环节真身，零生产装配）；slippage_analyzer.py（喂 scorer）；transaction_cost_optimizer.py（715 行族内最大，零装配）；t0_cost_model.py（144 行，testing，交叉 F69）
- **ex_sor.core**（11 件）：algo_execution_selector.py（677 行，MOD-XS-011，**回写目标、缺评分输入**）；execution_route_policy.py（testing，90 号 §19 路由裁定）；sor_agent.py（CONSUMERS 自注"运行时装配批待兑现"）
- **TDM 判定面**：TDM-E-L4-14 节点+2 边（:5351 feed / :5352 feedback）——判据面齐，码面断

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| scorer 本体 | 码 built/装配未接线 | 532 行+测试在册；全仓消费者=services/__init__ 导出+slippage_analyzer 头注，零运行时调用方 |
| L4-14→L4-06 回写边 | **未接线（码缺）** | selector 全文零 scorer 引用（本日 grep 复证，与 TDM 节点自认断链一致） |
| ex_sor 生产可达性 | 传递性不可达 | 唯一桥 execution_engine 自身零生产实例化（M7-04/05 双册同判） |
| TDM 判据面 | built | 节点+边+algo_note+activation 齐备（yaml:2536-2559 实读） |

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | selector 增评分输入（分算法桶累积→选型权重回写） | 接线 0.5-1 天，与 ex_sor 装配批（F55/B2）同批动 session 装配层 | P1 |
| 2 | ex_sor 全族生产装配缺位（本环节父域病） | 归 F55 接线裁定（M7-05 B2：接线 or design-frozen 显式声明） | P1 |
| 3 | RL 执行远期候选（A 股 T+1/涨跌停/拆单限制需改造） | 挂晨审不立项（tdm-growth-blueprint:175 既有裁定） | P2 |

## 五、自审闸三态
**挖干可施工**（三零件 file:line+边实测+断链双源同判；缺口 1 处置明确=selector 评分输入）。

## 六、复跑命令
```bash
grep -n "execution_quality\|quality_scorer" src/zephyr/ex_sor/core/algo_execution_selector.py   # 零命中=断链复证
sed -n '2536,2559p' config/trading_decision_map.yaml                  # TDM-E-L4-14 节点全文
sed -n '5351,5352p' config/trading_decision_map.yaml                  # 两边
grep -n "G4" docs/_working/2026-09-09-tdm-growth-blueprint.md | head -3   # G4 增长批出处
wc -l src/zephyr/ex_sor/services/execution_quality_scorer.py          # 532
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更
- `1dd6c70c74`（09-28 全流通·T袋落地）：`algo_execution_selector.py`（+55 行）新增 `QualityPriorProvider` Protocol+`quality_prior` 形参+`FEEDBACK_GAIN=0.20` 选型回写公式；`execution_quality_scorer.py`（+45 行）新增 `ScorerBackedQualityPrior` 评分侧适配器；trading_decision_map.yaml 同批 16 行——**L4-14→L4-06 执行反馈环最后一米已接（码面）**。
- `config/trading_decision_map.yaml` 另有 3 commit（`fa9ae36533` F62 注记／`8b098e31eb` ig_equity_edge 退役／`e21ebc03ec` F34 L9 消费接线）——本卷引用边无语义变化。

### 缺口清单状态修订
- 缺口 1（selector 增评分输入）：**已施工翻面**——QualityPriorProvider／ScorerBackedQualityPrior／FEEDBACK_GAIN 三件在码（1dd6c70c74）；生产装配仍受 ex_sor 全族可达性约束（缺口 2 维持）。
- 缺口 2（ex_sor 生产装配缺位）：维持（归 F55 接线裁定，未见施工）。
- 缺口 3（RL 远期候选）：维持。

### 自审闸三态
- **挖干可施工（维持）**；标题行"断链一米未接"与 §一/§三"selector 零消费评分/未接线（码缺）"断言**已翻面**——§六复跑命令第 1 条（grep 零命中=断链复证）现会命中新增 scorer 引用，勿据零命中误判回退。
