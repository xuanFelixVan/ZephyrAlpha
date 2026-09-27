---
ttl: task_bound
title: "F131 nlp 文本情报处理线（新闻打分/情绪聚合/研究评级）复飞案卷"
session: st-c7-mine-20260927
---

# F131 nlp 文本情报处理线（C 段，P2，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-08 行——"`nlp`（7 py：news/sentiment）→ F131（P2，C 段，文本情报处理线）"；同文件 :73 新增序亦记 "F131 nlp(P2/C)" ⇒ 本级取 **P2**。
> **口径勘误**：机采台账 `.runtime/tmp/st-c7-m1-inbox/six_direction_ledger.yaml` 的 `environments.F131.priority` 值为 **P1**，与骨架册面 P2 不一致。本卷以骨架为真源、按 P2 立卷，并把该不一致登记为 M1 采集器缺陷（§四 缺 5）。
> **主结论（黄）**：本包是 12 环节中**唯一经"三跳传递链"被日班排程真正驱动**的一件（非直接 import），故判**半接线**：6 实体件里 3 件在产、3 件测试可达。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/nlp/`（7 .py 在 HEAD，§六 P1）：`nlp_inference.py`、`sentiment_aggregator.py`、`sentiment_pipeline.py`、`research_rating.py`、`news_dual_tagger.py`、`news_impact_grader.py` + `__init__.py`。无 api/services/… 空骨架层（结构最紧的一件）。 |
| 在册态 | `module_translation_registry.yaml` 命中 **9**、`candidate_module_registry.yaml` 命中 **13**（本包同 F132 为候选册命中>翻译册命中的两件之一）；`architecture_model/contracts/error_code_registry.yaml` 有本包错误码条目（§六 R3）。上游需求在册：`src/zephyr/data/config/known_data_gaps.yaml:455-462`（news_sentiment 接线史与"已接线"闭合证据两处 文件:行号）。 |
| 消费者 | **生产 import=8 条 / 5 文件（AST 实测，§六 W1）**：`scripts/ml/eval_sentiment.py:54`、`scripts/ml/run_sentiment_batch.py:55` → `nlp_inference`；`run_sentiment_batch.py:61` → `sentiment_aggregator`；`scripts/ml/run_research_rating_batch.py:47` → `research_rating`；`src/zephyr/intelligence/news_llm_scorer.py:57/85` → `nlp_inference`；`src/zephyr/ml_train/implementations/sentiment_sft_trainer.py:130/433` → `nlp_inference`。**TYPE_CHECKING 装饰腿 1 条**：`src/zephyr/intelligence/news_sentiment_analyzer.py:53  from zephyr.nlp.nlp_inference import SentimentResult`（在 `if TYPE_CHECKING:` 块内，运行时零依赖，§六 C2）。测试 import=6 文件。 |
| 测试 | 6 文件：`tests/nlp/test_nlp_inference.py:25`、`test_sentiment_aggregator.py:28`、`test_research_rating.py:16`、`test_news_dual_tagger.py:33`、`test_news_impact_grader.py:31`、`test_sentiment_pipeline.py:25/26`。⇒ 6/6 实体件均有测试（覆盖齐），但其中 `news_dual_tagger`/`news_impact_grader`/`sentiment_pipeline` 三件**仅测试可达**。 |
| 自动化触发 | **有一条真链，但为三跳传递**（本卷最重要的机制更正）：`schedule.yaml:205-208` 槽位 `nightly_sentiment`（描述"日频接线，当日窗口+近 7 日缺口补跑，ReplacingMergeTree 幂等"）→ `scripts/data/run_nightly_sentiment.py:41-42` 调 `compute_nightly_sentiment(persist=True)`（`known_data_gaps.yaml:462` 以两处 文件:行号 记其已接线并自 2026-09-18 复核）→ `src/zephyr/intelligence/nightly_sentiment_window.py` 引 `news_llm_scorer` → `news_llm_scorer.py:57/85` import `zephyr.nlp.nlp_inference`。⇒ 排程确实驱动本包核心件，但**`data/scheduler.py` 并不直接 import 本包**（§六 A1 实测 scheduler.py/schedule.yaml/config 内 `zephyr.nlp` 零命中）。其余入口为人工 CLI：`config/resource_profile_registry.yaml:953  - task_id: manual_run_sentiment_batch`（名字即标 manual）。 |
| 真源方向 | 文本情报的落库真源=CH 侧情绪/新闻表族（`compute_nightly_sentiment` 写ReplacingMergeTree，见 §一 上游行）；规则数据侧真源= `src/zephyr/data/config/known_data_gaps.yaml` 对该链路的需求登记；架构数据=depgraph。本包自身**不持真源**，是纯处理层 ⇒ 方向清晰，无第二真源风险（与 F128/F130 的"真源未定"形成对照，本项为本卷少数全绿向）。 |
| 门禁与质量尺 | 无本包专属 gate（§六 G1）。质量面靠 `eval_sentiment.py` 的评估产物 + `known_data_gaps.yaml` 的缺口登记（人工/会话维护）双向兜，无自动效果尺。 |
| 当前运行状态 | **黄（半接线）**：`nlp_inference` 有日频传递链 + 3 条人工 CLI 入口；`sentiment_aggregator`/`research_rating` 有人工 CLI 入口；余三件测试可达。 |

## 二、子模块三级枚举

1. **推理族（在产，含排程腿）**：`nlp_inference.py`
   - 二级=LLM 推理封装（情绪打分/评级产出）
   - 三级=四个消费出口：日频排程（经 `news_llm_scorer`）、SFT 训练侧（`sentiment_sft_trainer.py:130/433`）、评估 CLI（`eval_sentiment.py:54`）、批跑 CLI（`run_sentiment_batch.py:55`）；另有 1 条 TYPE_CHECKING 装饰出口（`news_sentiment_analyzer.py:53`）
2. **聚合族（人工 CLI 在产）**：`sentiment_aggregator.py`（← `run_sentiment_batch.py:61`）→ 三级=多源情绪归并口径（其与 CH 侧 `nightly_sentiment` 窗口的去重关系见 `candidate_module_registry.yaml` 内"场内对账: 读侧三层去重已建（collect_news/run_sentiment_batch/run_research_rating_batch），引擎级修复无"一条，:20147 evidence 字段）
3. **评级族（人工 CLI 在产）**：`research_rating.py`（← `run_research_rating_batch.py:47`）
4. ** tagging 族（测试可达）**：`news_dual_tagger.py`（双标签）、`news_impact_grader.py`（影响分级）→ 三级=两者名义上是新闻入库前置，实测生产链路（`collect_news` 侧）未 import 之 ⇒ 标签能力当前不落生产（§四 缺 2）
5. **管线族（测试可达）**：`sentiment_pipeline.py` → 三级=与 `sentiment_aggregator.py` 的职责边界未声明（两件并存且仅后者在产）⇒ **同域重复簇候选**，按根宪法 §4.2 须核"同真源可派生→必并"（§四 缺 3）

## 三、接线四态独立复核

**判定=半接线**。判据链：

1. **直接 import 面**：PROD 8 条 / 5 文件（AST，§六 W1）⇒ 本包不是 F125/F127/F128/F130 那种零引用装饰，属**真被消费**。
2. **TYPE_CHECKING 专项（逐条测）**：`news_sentiment_analyzer.py:53` 的 `nlp_inference` 导入在 `if TYPE_CHECKING:` 块内（该块上文 :50 即 `ZephyrBaseError = Exception  # type: ignore` 的兜底分支）⇒ 该件"看起来消费 nlp"是**假象**，运行时零依赖，不得计入消费面；这也是 M1 台账把 `NewsItemInput` 之类 symbol 报成消费时的同类风险面（§六 C3 复核口径）。
3. **传递触发 vs 直接触发的区分（本卷核心纪律）**：M1 dir6 对 F131 报 `covered_wide=true` 且 chain 写 "`src/zephyr/data/scheduler.py <== schedule.yaml schedules(31 slots) 驱动`" —— 本卷实测**该机制描述不成立**：`git grep "zephyr.nlp" HEAD -- src/zephyr/data/scheduler.py src/zephyr/data/config/schedule.yaml` 零命中（§六 A1）。但**结论方向侥幸不差**：真链路确实源自 `schedule.yaml:205` 的槽位，只是经三跳（run_nightly_sentiment → compute_nightly_sentiment → nightly_sentiment_window → news_llm_scorer → nlp_inference）。⇒ 记为"覆盖为真、机制为伪"，两件事必须分开写，否则下一个人会去 scheduler 里找一条根本不存在的边。
4. **零触发件判据**：`news_dual_tagger`/`news_impact_grader`/`sentiment_pipeline` 三件 PROD import=0 且无计划任务、无 config 反射 ⇒ 装饰（不是半接线的一部分，而是包内的装饰子集）。
5. **人工 CLI 的合宪性**：`eval_sentiment.py`/`run_sentiment_batch.py`/`run_research_rating_batch.py` 属按需人工（`resource_profile_registry.yaml:953` 显式命名 `manual_`），本卷**不**把"非自动"当缺陷，只把"无排程但被叙事当作自动化能力"记为缺口（§四 缺 4）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | `news_sentiment_analyzer.py` 仅类型期依赖 nlp，运行时不消费 ⇒ 分析器与推理件的关系是纸面的 | 施工：定该件真实职责（若应调 nlp 推理则补运行时腿；若只做窗口聚合则删该 import 消歧），改后跑自家测试 | P2 |
| 2 | `news_dual_tagger`/`news_impact_grader` 零生产消费 ⇒ 新闻标签/分级能力不落生产 | 施工：接 `collect_news` 侧或明确退役（根宪法 §4.2 零触发零消费→退役）；接入须红样先行 | P2 |
| 3 | `sentiment_pipeline` vs `sentiment_aggregator` 职责边界未声明，同域重复簇候选 | 挂起：读毕两件的输入/输出口径后由总筹判合并方向；本卷不自行判并 | P2 |
| 4 | 三件的人工 CLI 叙事与"F131 文本情报处理线"的自动化期待不符；且三跳传递链任一跳断（`known_data_gaps.yaml` 曾记"写入器全仓零生产调用方"）即整链失效，**链上无健康探针** | 施工：在 `nlp_inference` 的调用侧加一次产出计数探针（事件写 `.runtime/sessions/<sid>/staging/`，禁直写 `.runtime` 根，根宪法 §9.4），使断链可当日可见 | P1 |
| 5 | M1 机采 priority 字段（P1）与骨架册面（P2）不一致 | 施工：M1 采集器改为从骨架册派生 priority 而非另算，避免两套数 | P2 |
| 6 | 无质量尺：LLM 打分漂移/失败率无自动判据（§六 G1） | 挂起：与 F88（LSG）质量面交叉，避免两把尺 | P2 |

## 五、自审闸三态

**未干。** 已可复算：PROD 8 条精确到 文件:行号、TC 装饰腿单列、三跳传递链逐跳给锚（schedule.yaml:205 → run_nightly_sentiment.py:41-42 → nightly_sentiment_window → news_llm_scorer:57/85）、M1 机制性错误的证伪、6/6 测试覆盖与 3 件零消费的并存事实、priority 口径不一致的登记。未干原因：①`nlp_inference.py` 的实现体未读（模型选择、LSG 是否为其调用路径、失败降级面）——而这直接决定 §六 缺 6"是否有 LLM 质量尺"的答案，也决定本包 LLM 调用是否合规经过 LSG（根宪法 §9.2 红线，**本卷未验证，不可推断为合规**）；②三跳链的本日实际产出未取（需读 CH 侧 `nightly_sentiment` 表当日行数，凭据未走 secrets 通道）；③缺 3 的重复簇判定需读两件实现。**特别标注**：缺 ①中"是否经 LSG"是本卷留给他人的最高优先未闭项，任何接手者在核完前不得称 F131 已干。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1 件数（期望 7）
git ls-tree -r --name-only HEAD src/zephyr/nlp | wc -l
# W1 三态分类（期望 PROD=8 / TC=1）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.nlp','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    if p.startswith('src/zephyr/nlp/'): continue
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.nlp'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else 'PROD')
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# A1 直接排程边不存在之证伪（期望零命中）
git grep -n "zephyr\.nlp" HEAD -- src/zephyr/data/scheduler.py src/zephyr/data/config/schedule.yaml config/
# A2 三跳链逐跳锚点
sed -n '203,210p' src/zephyr/data/config/schedule.yaml
sed -n '38,45p' scripts/data/run_nightly_sentiment.py
git grep -n "news_llm_scorer\|NewsLlmScorer" HEAD -- src/zephyr/intelligence/nightly_sentiment_window.py | head -4
# A3 人工入口在册名
grep -n "manual_run_sentiment_batch" config/resource_profile_registry.yaml | head -3
# C2 TC 装饰腿定位
sed -n '50,56p' src/zephyr/intelligence/news_sentiment_analyzer.py
# T1 测试面（期望 6）
git grep -l "zephyr\.nlp" HEAD -- 'tests/*'
# R1/R2/R3 在册三层
grep -c "zephyr[./]nlp" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -c "zephyr[./]nlp" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "zephyr.nlp" architecture_model/contracts/error_code_registry.yaml | head -3
# G1/未闭项 起手（LLM 调用是否经 LSG，本卷未做）
grep -n "gateway\|LSG\|ollama\|openai\|httpx\|requests" src/zephyr/nlp/nlp_inference.py | head -10
```
