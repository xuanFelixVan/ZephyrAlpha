---
ttl: task_bound
volume: 30_f58_execution_cost_feedback
session: st-ailayer-final-20260924
creation_token: fullflow-m7-backfill-f58-20260926
---

# 30 · F58 执行成本反馈（执行质量评分→选型回写）

> 补挖波 20260926｜只读取证，零交易路径。真源口径=`00_skeleton/00_全环节总册.md:103`（F58：执行质量评分→选型回写，G4 增长批闭环；上游 F57、下游 F55/F28；真源=`src/zephyr/ex_sor/services/execution_quality_scorer.py`；状态 **partial**，TDM-E-L4-14）。
> 差集声明：`05_ex_sor.md` 挖的是 F55 路由族整体（结论=真身 27 件在库、生产装配缺位 B2）；本册只挖 **F58 这一个闭环**——总册把它标 partial 却未记"partial 在哪一段"，本册定位到具体三处断点。

## 一、环节定义与边界

F58 = 把"这一单执行得好不好"量化成分数，回写给 F55 的算法选型器，使下一单选到更优算法（G4 增长闭环的回路腿）。四段链条：
`F57 对账产物（成交/成本事实）` → `SlippageAnalyzer / TransactionCostOptimizer`（指标）→ `ExecutionQualityScorer`（四维加权评分+verdict）→ `algo_execution_selector`（选型权重回写）。

实测：**四段全部零装配**。评分器本体合格（见 §三），但两端接口都是纸面声明。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | 契约输入=四指标 `slippage_bps / duration_s / cost_bps / impact_bps`，或经 `score_from_results` 收 `SlippageAnalyzer.SlippageResult` + `TransactionCostOptimizer.TransactionCostResult`（`execution_quality_scorer.py:41-44` 可消费上游自述，方法 :326 `score` / :423 `score_from_results`）。**实际生产无喂数方**（§三 3.4） |
| 下游消费 | 头注 :5 `[CONSUMERS] MOD-EX-CORE(执行质量报告); MOD-XS-011(算法选择器反馈环)` ⇒ 实测两方皆零引用：`ExecutionQualityScorer\|SlippageAnalyzer\|TransactionCostOptimizer` 全仓 **158 命中仅分布在 7 个文件**＝3 个自身件＋`services/__init__.py`（包级 re-export 8 命中）＋3 个 test 件（127 命中）；src/scripts 中**无任何调用方**（复跑命令 §七-1） |
| 自动化触发 | 零。`[STARTUP] manual`（:6）；无计划任务、无事件订阅。**注意反例对照**：`SlippageAnalyzer`/`TransactionCostOptimizer` 与 selector 均无自触发，而 ex_sor 族唯一被生产 import 的入口=`src/zephyr/ex_core/execution_engine.py:65-66/:358/:407/:411`（只 import `algo_trading_engine`+`market_context_provider`，**不含 selector 也不含 services**）⇒ 与 05 册 B2"唯一桥 execution_engine"完全自洽，本波独立复现该边 |
| 真源与注册表 | 件真源=`src/zephyr/ex_sor/services/execution_quality_scorer.py`（532 行，MOD-XS-018）；算法推导图=`docs/03_modules/_domain_ex_sor/algo_flow/execution_quality_scorer.yaml`（:49 外迁声明）；错误码/运营面经 `architecture_model/contracts/error_code_registry.yaml` 族登记（MOD-XS-018 三异常 QualityScorerError/InvalidWeightsError/InsufficientMetricsError，:13）；TDM 卡=TDM-E-L4-14 |
| 门禁与质量尺 | 尺：四维∈[0,1]、权重和=1.0、overall=Σ(score×weight)、verdict `good≥0.8 / acceptable≥0.5 / poor<0.5`（:8 INVARIANTS，实现 :501 `_verdict`）；阈值=bps 标尺 price 50/cost 30/impact 20、time 300s（:32-39 文档 + `QualityBenchmarkProvider/DefaultBenchmarkProvider` :69-70 可注入）；fail-closed：权重和≠1 抛 `InvalidWeightsError`（`__post_init__` :195）、指标不足抛 `InsufficientMetricsError`（:111/:197） |
| 当前运行状态 | **红（环节级）**，且**绿（件级）**：件有 532 行实现＋专属测试；环节闭环无任何一段在运行。总册 `partial` 判定**方向正确但低估**——按四要素判据（入口触发器/出口真源/自动化/真源唯一，总册 §四）实测为"入口 0、出口 0、自动化 0、真源唯一性 1" |

## 三、子模块清单（三源交叉：ls + grep + 注册表）

| # | 子件 | 入口 | 状态 |
|---|---|---|---|
| 3.1 | `ExecutionQualityScorer` 四维评分本体 | 532 行，`score` :326、`_score_dimension` :468、`_calc_overall` :488 | 绿（件级） |
| 3.2 | `QualityWeights`/`QualityDimension`/`ExecutionDimensionScore`/`ExecutionQualityResult` 值对象 | :168 `weight_for`、:227 `score_for`、:243-268 四个 threshold 属性 | 绿 |
| 3.3 | `SlippageAnalyzer`（572 行，EXT-001）/ `TransactionCostOptimizer`（715 行，EXT-003） | `services/slippage_analyzer.py`、`services/transaction_cost_optimizer.py`；二者头注 :5 各写 `[CONSUMERS] MOD-XS-018(ExecutionQualityScorer…)` | **红：声明的消费方（评分器）不 import 它们，只鸭子接收其产物**；两器自身同样生产零调用方 |
| 3.4 | 历史追踪 | `self._history: list` :312、`_history.append` :411、`get_history` :517、`average_score` :524、`clear_history` :531 | **红：进程内 list，无持久化**（本波核心发现 F2，见 §四） |
| 3.5 | 选型回写目标 `algo_execution_selector`（677 行，MOD-XS-011） | 头注 :5 `[CONSUMERS] MOD-XS-005…; D-EX-CORE(OMS,算法推荐入口)`、:8 INVARIANTS"选择可审计/评分归一[0,1]/选最高分算法" | **红：selector 的"评分"来自其内置流动性/大单规则，不读 F58 产出的历史分**（selector 文件内无任何 services 层 import，§七-2） |
| 3.6 | 包级 re-export `services/__init__.py` | :27-:99 | 绿（但它是三件套唯一"被引用"处＝账面引用，非数据流） |

## 四、堵点与病灶

- **F1【P1】反馈环两端声明互指、无人装配（"环"=两个空头指针）**。评分器说消费者是 XS-011；XS-011 的评分逻辑不读它；两者都不在 `execution_engine` 的 import 列表里。根因＝05 册 B2（ex_sor 族生产装配缺位）的**下游腿**，不是新病灶而是同一病灶的第二段。修法＝随 SOR 接线批一起做，单做 F58 无意义（上游无成交事实）。工作量＝并入 05-B2 批（该批已挂待裁）。本车道可修＝否（须与 05-B2 同裁）。
- **F2【P0·本波新证】"历史追踪"是进程内 list ⇒ 环即使接线也闭不上**。`_history` 随进程退出即蒸发（:312/:411），而模拟盘/实盘都是**一日一进程**（PaperSession 09:25 起、15:30 结算另一进程，20/10 册实测）⇒ 跨日选型学习恒为 0 样本。修法＝评分结果落库为 TCA 事实表（下游真源候选=`c1_market.execution_report`，与 10 册 D2 同一张表，可复用不新建）＋选型器读历史窗口；**禁为 F58 新立一张表**（内收判据，见 §五）。工作量＝1-2 天。本车道可修＝部分（代码可写，落库表选型须裁 M7-BF-8）。
- **F3【P1】上游 F57 事实为零 ⇒ 反馈环无源**。F58 声明上游=F57（总册 :103），而 F57 系统侧 Fill 输入结构性恒空（10 册 D1）＋三方核对未接（20 册 B1）⇒ 就算 F1/F2 都修，喂进来的仍是 0 笔。⇒ **修复次序必须是 D1→B1→F1→F2**，本波把这条依赖链写死，防止施工班从 F58 起手做出"第三个零样本假绿"。
- **F4【P2·判据健康度】阈值口径与"零样本"未区分**：`_verdict` 在 0 输入时经 `average_score` 路径会给出什么，本册**未跑测试去实测**（避免为取证执行交易域代码路径，且 tests 已有覆盖），登记待挖（§六）。

## 五、内收与合并机会（w5_1）

1. `SlippageAnalyzer` + `TransactionCostOptimizer` + `ExecutionQualityScorer` 三件 1,819 行同做"一笔成交的成本度量"，且前两者的唯一"消费方"就是第三者 ⇒ 同域重复簇→**收敛为单一成本度量入口**（评分器收原始字段即可，两器的容差/口径须先 diff 对齐，禁静默合并阈值）。
2. 落库真源候选唯一化：F58 结果与 10 册 D2 的 ExecutionReport 是**同一事实的两个视角**（成交执行 vs 执行质量），按"同真源可派生→必并"，禁止为 F58 新建第三表（新表须声明替代关系，宪法 §4.1）。
3. 不并：`TransactionCostOptimizer` 的"拆单成本最优解搜索"（面向未来单）与评分器（面向过去单）跨语义不同对象，合并时须保留各自函数边界。

## 六、自审闸三态

**挖干（环节级红判三向齐：调用方穷尽 grep、import 边实测、件内实现行号）**，**待挖 1 项**＝F4 零样本 verdict 行为未实测（刻意不做，取证不跑交易域路径）；另 §五-2 的表行数实证待总筹只读取数（与 10/20 册同一待取项合并登记）。

## 七、复核命令

```bash
# 1) 三件套生产零调用方（期望：仅 7 文件——3 自身 + services/__init__ + 3 tests）
grep -rc "ExecutionQualityScorer\|SlippageAnalyzer\|TransactionCostOptimizer" --include=*.py src scripts tests
# 2) 选型器不读评分器（期望：selector 文件内 services 层 import = 0）
grep -n "services\|QualityScorer\|_history" src/zephyr/ex_sor/core/algo_execution_selector.py
# 3) 历史只在内存
sed -n '305,322p;405,415p;511,532p' src/zephyr/ex_sor/services/execution_quality_scorer.py
# 4) ex_sor 被生产 import 的全部边（期望：仅 execution_engine 的两符号）
grep -rn "from zephyr.ex_sor" src scripts --include=*.py | grep -v "^src/zephyr/ex_sor"
# 5) 环节卡与阈值尺
sed -n '1,16p' src/zephyr/ex_sor/services/execution_quality_scorer.py
grep -n "TDM-E-L4-14" docs/02_enterprise_architecture/10_trading_map/*.md
```

## 八、回写总册建议

`:103` F58 状态维持 **partial**（判定不变），备注列补三句实测："三件套生产零调用方（唯一被引用处=包级 re-export）；历史评分为进程内 list 无持久化⇒跨日学习恒 0；上游 F57 事实为零（10 册 D1）⇒修复次序 D1→F57-B1→F58"。
