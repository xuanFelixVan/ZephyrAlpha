---
ttl: task_bound
title: L12 案卷 F121 — 研究性三域+研究域（design 态：M0 待裁挂起原文转录+四包实态复核）
session: zc-l12-20260927
---

# F121 研究性三域+研究域（M 段横切 X5/X6，骨架态=design/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | M0 骨架 76 环节册待裁项 22/23（原文见三·转录节）；总筹初步口径"研究域不编入"（orchestration :35）；补裁证据册 2026-09-25（四包逐包实测） |
| 下游消费 | 待裁（总册 F121 行下游列="待裁"）；唯一既成消费边=execution_simulation→M2 回测链（见三·表） |
| 自动化触发 | 零——四包零 TDM 挂轴、零 capability 卡（本日 ls grep 复现）、零调度登记、research 零 __main__ CLI |
| 真源与注册表 | 四包代码：src/zephyr/{cross_asset,digital_twin,execution_simulation,research}/；登记面：域册 D_CROSS_ASSET(:1280)/D_DIGITAL_TWIN(:1344)/D_EXEC_SIM(:1360)/D_RESEARCH(:1717)+模块册 37 行（D_FACTOR×7/D_KNOWLEDGE×4/D_RESEARCH×1） |
| 门禁与质量尺 | 宪法 §4.2 内收判据 w5_1（同真源可派生→必并/零触发零消费→退役）直接受理面；净删=Owner 门位 |
| 当前运行状态 | **design（挂起中，但挂起判据已被新事实击穿一角）**：cross_asset 纯空壳/digital_twin 有件零消费/research 成熟件零生产接线/execution_simulation **已被 M2 真消费且消费面扩大 2→3 文件**（本日 grep 复现，见勘误 1） |

## 二、子模块三级枚举（包 → 文件 → 登记面）

1. `cross_asset/`（7 .py 全 __init__，零实模块）：纯登记空壳；域册 D_CROSS_ASSET（stability: plastic）；外部消费零（全仓 grep 唯二命中=异名路径+注释假阳性）
2. `digital_twin/`（8 .py=7 壳+1 实件）：market_twin_simulator.py（maturity=production，MOD-DT-001）；域册 D_DIGITAL_TWIN（lifecycle=design_only 治本注记）；消费零
3. `execution_simulation/`（8 .py=7 壳+1 实件）：almgren_chriss_impact_model.py（production，MOD-EXSIM-001）；域册 D_EXEC_SIM（design_only 注记）；**消费 3 文件**：backtest/core/matching_engine.py + implementations/vectorized_engine.py + core/cost_model_calibration.py（本日实扫）
4. `research/`（14 .py=2 __init__+12 实件）：根层 8 实件（auto_feature_discoverer/gp_strategy_discovery/llm_evolutionary_search/factor_vote_mining/factor_model_co_evaluator/strategy_iteration_upgrader＝factor 族 production 6 件＋factor_mining_pipeline(testing)＋sell_news_event_study(design)）＋evidence/ 4 实件（batch_entry/evidence_chain/hypothesis_registry/iteration_guide，testing）；域册跨三域 D_FACTOR×7/D_KNOWLEDGE×4/D_RESEARCH×1；外部消费仅 scripts/construction/_e2e_deep.py（施工自查）
5. 两图登记面：TDM/strategy_production_map grep 四包关键词=**零命中**（本日复现）——管"研究三域"不在任何业务图挂轴

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| cross_asset | **空壳（退役候选）** | 7/7 __init__ 本日复现；w5_1"零触发零消费→退役"字面命中，Owner 净删门位候选 |
| digital_twin | **建成未接线** | 1 实件 production 级零消费；"留件收编 vs 净删"待评审 |
| execution_simulation | **已接线（登记面谎报 design）** | M2 撮合/向量化引擎真消费；域册 lifecycle=design_only 与生产消费矛盾持续 |
| research | **建成未接线（重复簇无主）** | 7 件 D_FACTOR production 与 F17 车道 C（mcts_expression_search/gplearn/AlphaGen 选型）同域两套挖掘件互不引用；evidence/ 链与 F92 原问题账本（entry_count=0 空转）+F35 一问一考语义重叠 |

### M0 待裁内容原样转录（禁改字，`00_skeleton_fullflow.md` 扩展项表 :159-160）

> | 22 | 研究性三域（数字孪生/跨资产/执行仿真） | src/zephyr/{digital_twin,cross_asset,execution_simulation}/ | 待裁：设计态无运行证据，建议挂起不入车道 |
> | 23 | 研究域 research | src/zephyr/research/（事件研究/假设注册） | 待裁：或 M2 扩 |

总筹初步口径（`00_orchestration.md:35` M0 行原文摘录）："3 项待裁已由总筹裁掉（**研究域不编入**/管线路由 M4M5 互引）"。

**影响面**（挂起状态若延续）：
1. 域册登记面撒谎持续发酵——D_EXEC_SIM design_only 标注 vs 3 文件生产消费（本卷新增第 3 消费方证据），M2 册若只按 2 文件记"个别文件借用"则又一处漂移；
2. research 与 F17 车道 C 同域重复簇继续无主——w5_1"必并"评审条件已满足却无受理车道；若不并须成文"跨域不同对象→不并"依据，当前零成文；
3. cross_asset 空壳占 4 域册条目+37 模块册行中的无效面，净删动作量随拖延与登记增长同向放大；
4. F120 骨架若走"收编结案"（联动项），research"事件研究/假设验证"应随产线工段轴归 SF 组——F121 与 F120 裁定联动，单裁 F121 可能返工。

## 骨架勘误

1. **消费面扩大**：09-25 补裁证据册记 almgren_chriss 消费=2 文件；本日复现=**3 文件**（新增 backtest/core/cost_model_calibration.py）——"挂起=无运行证据"的判据进一步失守。
2. **件数口径修正**：证据册"research 14 .py 实件"实为 14 .py 含 2 __init__＝**12 实件**（7 factor 族+4 evidence+1 事件研究；factor_mining_pipeline 计入 factor 族则 8+4）。
3. **裁定状态登记张力**：总筹称待裁"已裁掉（研究域不编入）"，但总册 F121 行与今日清单 §1.4 均仍标"M0 待裁挂起"且 ruling_registry 无对应裁定号（本日 grep 零命中）——"已裁"仅存在于 orchestration 一行字，无登记落点；本卷按纪律维持总册/清单口径（design 待裁挂起）并将该张力列为待裁前置事实。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | F121 终裁缺位（维持挂起/拆包处置/整体编入三选项，09-25 证据册 §五并排，本卷不裁；证据指向最小正确解=拆包） | Owner 裁；裁时联动 F120 选项 | P1（裁前 execution_simulation 登记面持续撒谎） |
| 2 | D_EXEC_SIM（及 D_DIGITAL_TWIN）lifecycle=design_only 与实态矛盾 | 裁后随包处置同步改注（execution_simulation→随 F65 归 M2 引用、lifecycle 改 built） | P1 |
| 3 | cross_asset 空壳退役候选 | w5_1 退役评审→Owner 净删门位（连 4 域册/37 行登记一并处置） | P2 |
| 4 | research↔F17 车道 C 同域合并评审 | 交 SF 组逐件裁必并/不并；不并须成文依据 | P2 |
| 5 | "已裁研究域不编入"无裁定号 | 补 ruling_registry 登记或撤回"已裁"措辞（二选一，消口径张力） | P2 |

## 五、自审闸三态

**挖干（四包实态+待裁原文）**：包/文件/登记三级枚举本日全复现 ✅ M0 待裁 22/23 原文转录零改字 ✅；**待裁**：F121 终裁路径（Owner）；research 合并评审（SF 组）；cross_asset 净删（Owner 门位）。

## 六、复跑命令

```bash
for p in cross_asset digital_twin execution_simulation research; do echo "$p: $(find src/zephyr/$p -name '*.py' | wc -l) py / $(find src/zephyr/$p -name '__init__.py' | wc -l) init"; done
grep -rln "almgren_chriss" src/zephyr/backtest --include="*.py"        # =3 文件
grep -rln "zephyr\.research" src scripts --include="*.py" | grep -v "src/zephyr/research"  # 仅 construction 自查
grep -cn "digital_twin\|cross_asset\|execution_simulation\|zephyr\.research" config/trading_decision_map.yaml config/strategy_production_map.yaml  # =0 0
sed -n '159,160p' docs/_working/fullflow_mining/00_skeleton_fullflow.md  # 待裁 22/23 原文
ls data/capability_cards/ | grep -i "twin\|cross_asset\|research"       # 应无输出
```
