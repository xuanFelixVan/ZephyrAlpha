---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F22 E3 构造与翻译（公式轨桥/假说轨翻译 MVP）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-159+190（+041..075 人工件族）
map_node: FAC-E3
---

# F22 · E3 构造与翻译

## 一、环节定义与边界
一句话：把过审想法变成 E4 可考的标准件——三轨：①公式轨桥（159 factor_strategy_template：DSL 表达式→考卷件机械翻译，c4_fact_*.py）②假说轨 C3 翻译 MVP（190 hypothesis_translator：D/B 过审假说→本地 LLM 结构化翻译为因子表达式，公式化子集，不可翻如实入阴性档）③人工翻译件族（C4 人工版 35 条验收集=模板定型基准，c4_<md5>_<name>.py）。
上游供料=E2 过审集（CH precheck_passed）+进货台账 expression 列；下游消费=scripts/backtest/translated/ 考卷件→E4 考试咽喉（F23，SF-B）+translated_manifest/constructed_manifest 双台账。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | auto_construct（factory_intake_pipeline.py:171-245）：C/C2 过审+expression 列→validate_expr（白名单+特征+元数）→159 桥 generate_strategy_file；hypothesis_translator（:57-61）：SQL 取 `verdict='precheck_passed' AND birth_channel IN ('D','B') ORDER BY prechecked_at DESC LIMIT {n}` |
| 下游消费 | scripts/backtest/translated/ 实测 **85 个 c4_*.py**（含 6 个 c4_fact_*.py 机生件）+_c4_engine/_valuation_engine 两引擎；translated_manifest.csv 5 行（09-15 03:45 班：1 B+4 D）/constructed_manifest.csv 1 行（09-15 03:39，C 渠道 FACT-********）；E4 侧 c4_batch_screen/f06_e4_wfa_exam 消费 |
| 自动化触发 | 无常驻（manual；construct 子命令=E2→E3 自动流转件但需人工起跑）；E0 问闸接线实证（190 头注：local 轻档） |
| 真源与注册表 | MOD-BT-159:15949/190:8928,15984 在 path_ownership_map；tests 两套在盘（test_factor_strategy_template/test_hypothesis_translator）；图9 FAC-E3 build_status=partial；QuantCode-Bench 实证（单轮通过率 70-76%/pass@5 43%）写进 INVARIANTS 作验收集+重试环依据；159 桥实跑验证=c4_fact_e831084c（图9 记录） |
| 门禁与质量尺 | 公式化子集边界（NL→任意代码不在此轨防幻觉）；不可公式化如实 translatable=false 入阴性台账禁硬翻（190 INVARIANTS）；DSL 白名单校验+非退化 sanity；生成件入 translated/ 前必过 creation_token 登记（construct 侧 batch_creation_tokens.py 子过程，:225-233）；翻译台账只追加；出生证原样携带+翻译行为记 birth_source 尾注 |
| 当前运行状态 | **绿（两轨本体）/红（推进面）**。最近真实出货=2026-09-15（ translated 班 5 件+constructed 1 件，同日双班）；09-15 后零新件——**E2 过审 13 条中 7 条未构造**（含 09-16 批 3 条 B pass，晚于 09-15 翻译班永久错过） |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 公式轨桥 generate_strategy_file（MOD-BT-159） | scripts/backtest/factor_strategy_template.py（262 行） | built（6 件 c4_fact_*.py 实证） |
| 假说轨翻译 hypothesis_translator（MOD-BT-190：prompt/解析/校验/阴性档/台账） | scripts/backtest/hypothesis_translator.py（约 300 行） | built（5 行台账实证，含 translatable 判定） |
| E2→E3 自动流转 auto_construct（C/C2） | factory_intake_pipeline.py:171-245 | built（幂等：manifest 已登记跳过） |
| 人工翻译验收集族（C4 人工版 35 条基准） | scripts/backtest/translated/c4_*（85 件存量=35 人工标准答案+44 件 C4 批量翻译批+6 件 c4_fact_* 机生） | built（模板定型基准） |
| graph_enrich_staging（MOD-BT-193，图谱增补 P0，挂 E3 名下） | scripts/backtest/graph_enrich_staging.py | built（tests 在盘；消费线未闭合→F18 册堵点④） |
| D/B 过审全量幂等推进器 | — | **missing**（translator LIMIT-N 人工语义，非幂等全量消费） |
| NL→任意代码全量翻译（C3 翻译第二期） | — | missing（190 头注自认"后续立项"） |

## 四、堵点与病灶
1. **【P0】过审 13 条仅 6 条入 E3**：现象=translated 5（1B+4D）+constructed 1（C）=6/13；余 7 条滞留（3 条 B pass 在 09-16 批、D 4 条未选入、C/C2 部分无 expression 或未轮到）；根因=①translator 是人工 LIMIT-N 快照语义（prechecked_at DESC 取最近 N，非幂等游标）②translator 与 construct 各管一轨无统一"过审→排产"队列③无过审滞留看板；修法=统一排产器：`SELECT candidate_id FROM passed` 幂等对照双 manifest 差集→按轨分发（有 expression 走 159 桥、D/B 假说走 190）；1-1.5 天；本车道可修（把 auto_construct 的幂等模式推广到假说轨即可）。
2. **阴性档利用率**：translated_manifest 5 行里 translatable=false 的阴性记录比例与 refusal_reason 分布未复盘——表达式空间（7 特征×白名单算子）对 D 车道产业链假说覆盖面天然窄（事件窗/多腿不可翻），预期阴性率高；修法=按 refusal_reason 聚类决定表达式空间扩展方向（特征族扩展清单）；0.5 天复盘。
3. **人工件与机生件同目录混放**：translated/ 下 79 件命名件与 6 件 c4_fact_* 机生件无目录级区分（仅前缀 fact_），E4 批测侧若按目录通配会混考；修法=机生件挪 translated/fact/ 子目录或 manifest 加 origin 列；0.5 天；**待裁**（动 E4 侧引用需 SF-B 对账）。
4. **E3 双 manifest 分立**：translated_manifest（11 列含 mechanism）与 constructed_manifest（5 列）schema 不齐，race/对账面要同时读两表；修法=统一 manifest schema（v2 迁移）或机生件并入 translated_manifest 加 track 列；1 天；P2。

## 五、提速与合并机会
- 159 桥与 190 共享 DSL 校验（190 复用 155 FEATURES+白名单）——真源已收敛；190 解析器与 E2 parse_reply 同构但语义不同（保留分立）。
- 排产器若建成，construct 子命令可并入其中（单命令"过审→考卷件"全轨化），E3 入口从两个 CLI 收敛为一个。

## 六、自审闸三态
- **三态结论：partial**（159/190/人工件三轨 built 有实战；幂等推进器缺致 7/13 滞留）。
- **差什么才算 built**：①统一排产器上线并消化现存 7 条滞留（双 manifest 对账零差集）；②机生/人工件区分口径裁定落地；③（第二期 NL→代码立项与否=Owner 门位，非 built 门槛——图9 已声明分期）。

## 七、复核命令
```bash
ls scripts/backtest/translated/c4_*.py | wc -l        # 85
ls scripts/backtest/translated/c4_fact_*.py | wc -l   # 6（159 桥产出）
python -c "import csv;[print(f,list(csv.DictReader(open('data/strategy_intake/'+f,encoding='utf-8-sig')))) for f in ['translated_manifest.csv','constructed_manifest.csv']]"
python scripts/backtest/hypothesis_translator.py translate --seeds 1 --dry-run   # 翻译演练（需 Ollama）
python -m pytest tests/backtest/test_hypothesis_translator.py tests/backtest/test_factor_strategy_template.py -q
```
