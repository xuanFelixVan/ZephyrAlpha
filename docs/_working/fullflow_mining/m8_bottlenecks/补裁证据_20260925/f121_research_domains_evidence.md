---
ttl: task_bound
session: st-ailayer-fullflow-frxc
date: 2026-09-25
---

# M8 补裁证据 · F121 研究性三域+研究域（design 态裁前证据，只列证据与选项，不裁）

> 挖矿会话 st-ailayer-fullflow-frxc ｜ 2026-09-25 ｜ 只读挖矿+本目录零 commit。
> 待裁命题：src/zephyr/{digital_twin,cross_asset,execution_simulation,research}/ 四包——M0 册原判"设计态无运行证据，建议挂起不入车道"（00_skeleton_fullflow.md:159 待裁项 22/23），总筹初步口径"研究域不编入"（orchestration §四 M0 行）；S0 总册 F121 行维持"design/M0 待裁"。本册把四包逐包实测摊开，供终裁。
> 关键新证据：四包**不是同质的设计空壳**——execution_simulation 已真消费在产线上，research 七件是已登记 D_FACTOR 的 production 成熟件，cross_asset 才是纯空壳。

## 一、逐包实测（盘面×域册×全仓消费机扫三源交叉，2026-09-25）
| 包 | 盘面 | 域册登记 | 外部消费方 | 实态 |
|---|---|---|---|---|
| cross_asset | 7 .py **全是 __init__ 空壳**（零实模块） | D_CROSS_ASSET（域册 :1280，stability: plastic） | **零**（全仓 grep 唯二命中=risk/cross_asset 异名路径+注释，假阳性） | **纯登记空壳** |
| digital_twin | 8 .py＝7 壳+1 实件 market_twin_simulator.py（maturity=production，MOD-DT-001） | D_DIGITAL_TWIN（:1344，lifecycle=design_only 治本注记） | **零** | 有件无消费 |
| execution_simulation | 8 .py＝7 壳+1 实件 almgren_chriss_impact_model.py（production，MOD-EXSIM-001） | D_EXEC_SIM（:1360，design_only 注记） | **2 处真生产消费**：backtest/core/matching_engine.py + backtest/implementations/vectorized_engine.py | **已在 M2 回测链上跑** |
| research | 14 .py 实件：7 件 factor 族（auto_feature_discoverer/gp_strategy_discovery/factor_vote_mining/factor_model_co_evaluator/llm_evolutionary_search/strategy_iteration_upgrader 全 production）+evidence/ 4 件（testing）+sell_news_event_study（design）+factor_mining_pipeline（testing） | **跨三域登记**：D_FACTOR×7、D_KNOWLEDGE×4、D_RESEARCH×1（域册 :1717，SSOT=MOD-RES-001，covers=事件研究/假设验证/研究资产管理） | **零生产消费**（唯一命中=scripts/construction/_e2e_deep.py 施工自查脚本） | 成熟件零接线 |

- 补充实测：四包 TDM module_ref 挂接=零（trading_decision_map.yaml grep 零命中）；capability_cards/ 零卡片；research 包零 __main__ CLI 入口。

## 二、同域重复簇证据（宪法 §4.2 内收判据 w5_1 直接受理面）
1. **research 7 件 D_FACTOR vs F17 车道 C**：车道 C=scripts/backtest/mcts_expression_search.py+gplearn 轨+AlphaGen 选型（M0 F17 行），research=gp_strategy_discovery（GP 轨）+llm_evolutionary_search（LLM 进化轨）+factor_vote_mining/auto_feature_discoverer——**同域两套挖掘件互不引用**（factory 五脚本 grep zephyr.research 零命中），符合"同真源可派生→必并"评审条件。
2. **evidence/ 链 vs F92 原问题账本+F35 一问一考**：hypothesis_registry（假设注册）/evidence_chain（证据链）与 governance/meta_question（PG 三表入库闸/一问一考）语义重叠——两组均零/低运行（F92 entry_count=0 空转，M4 在案）。
3. **cross_asset 空壳**：零触发零消费→w5_1"零触发零消费→退役"字面命中，Owner 净删门位候选。

## 三、"挂起不入车道"方证据（M0/总筹原判的支持面）
1. 四包中三包（cross_asset 全壳、digital_twin 零消费、research 零生产消费）无运行证据——M0 判词"设计态无运行证据"在 2026-09-17 立场成立。
2. 四包均无 TDM 挂轴、无 capability 卡、无调度登记——按总册 §四 环节四要素（入口/出口/自动化/真源）全数不及格。
3. 车道分配成本：挖矿波已收卷，为空壳包开新车道违背分工册"已挖干车道引用不重挖"的预算纪律。

## 四、"编入/收编处置"方证据（终裁不能忽略的新事实）
1. **execution_simulation 不能按"挂起"处置**——almgren_chriss 已被 M2 回测撮合引擎实消费（matching_engine/vectorized_engine），它事实上已在 F65 环节链上；继续标"挂起待裁"＝登记面撒谎（域册 lifecycle=design_only 与生产消费矛盾）。
2. **research 7 件是 D_FACTOR 域登记的 production 件**——处置权在 F17（SF 组）车道评审而非"挂起"；若不并，则须按 w5_1 记录"跨域不同对象→不并"理由，两套挖掘件并存需成文依据。
3. **域册/模块册登记面齐全**（4 域+37 行）——"编入"的登记成本≈0，缺的只是车道归属与消费接线判定；全删则 37 行登记+4 域册条目要一并净删（Owner 门位动作量反而更大）。
4. 决策骨架报告（F120 同源）§2"骨稳肉动"框架下，"事件研究/假设验证"属血肉自动养范畴——F121 处置与 F120 裁定有联动（若骨架收编结案，research 归属应随产线工段轴走 SF 组）。

## 五、裁定选项（并排陈列，本组不裁）
- **选项 A·维持挂起**（M0 原判）：四包不入 12 组车道，登记面冻结；execution_simulation 的 M2 消费以"个别文件借用"口径在 M2 册记一笔。风险：域册 design_only 标注与生产消费的矛盾持续发酵；research 与车道 C 重复簇无主。
- **选项 B·拆包处置（证据指向的最小正确解）**：execution_simulation→随 F65 归 M2 引用（登记互引，域册 lifecycle 改 built）；research→交 SF 组与 F17 做同域合并评审（必并/不并逐件裁）；digital_twin→评审"留件收编 vs 净删"（1 实件零消费）；cross_asset→走 w5_1 退役候选（Owner 净删门位）。
- **选项 C·整体编入新车道**：为四包开"研究域车道"补挖。成本最高，与挖矿波收卷现状冲突，除非 Owner 另有研究路线意图。

## 六、复核命令（10 分钟）
```bash
# 1. 空壳率复现（cross_asset 应 7/7 全 __init__；execution_simulation 应 7 壳+1 实件）
find src/zephyr/cross_asset src/zephyr/execution_simulation -name "*.py" | sed 's|.*/||' | sort | uniq -c | sort -rn | head -4
# 2. execution_simulation 真消费复现（应 2 文件）
grep -rln "almgren_chriss" src/zephyr/backtest --include="*.py"
# 3. research 零生产消费复现（应仅 construction 自查脚本）
grep -rln "zephyr\.research\|zephyr research" src scripts --include="*.py" | grep -v "src/zephyr/research"
# 4. 域册三域登记复现
grep -n "D_CROSS_ASSET\|D_DIGITAL_TWIN\|D_EXEC_SIM\|D_RESEARCH" docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml | head -4
# 5. research 跨域登记复现（应 D_FACTOR×7/D_KNOWLEDGE×4/D_RESEARCH×1）
python -c "
import yaml
d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml',encoding='utf-8'))
rows=[e for e in d['entries'] if 'src/zephyr/research/' in str(e.get('module_path',''))]
from collections import Counter; print(Counter(e['domain_id'] for e in rows))"
# 6. TDM 零挂轴复现（应无输出）
grep -n "digital_twin\|cross_asset\|execution_simulation\|zephyr.research" config/trading_decision_map.yaml | head -3
```
