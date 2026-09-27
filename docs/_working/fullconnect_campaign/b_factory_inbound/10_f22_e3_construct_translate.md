---
ttl: task_bound
title: F22 E3 构造与翻译（159 桥/190 翻译 MVP/人工件族）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F22 · E3 构造与翻译

> 挖矿基册=01_strategy_factory/10_f22_e3_construct_translate.md（SF-A）。本卷=独立复核+09-26 增量（manifest 5→8 行+新缺陷）。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | E2 过审集（CH precheck_passed=13 条维持）；translator SQL=`verdict='precheck_passed' AND birth_channel IN ('D','B') ORDER BY prechecked_at DESC LIMIT {n}`（hypothesis_translator.py:58-60）；construct=C/C2 过审+expression 列（factory_intake_pipeline auto_construct） |
| 下游 | scripts/backtest/translated/ **85 个 c4_*.py（其中 c4_fact_* 仍 6 件，09-27 复测）**+两引擎；translated_manifest.csv **8 行**（09-15 班 5+**09-26 10:29 班 3**）｜constructed_manifest.csv 1 行维持；E4 侧 c4_batch_screen/f06_e4_wfa_exam 消费 |
| 自动触发 | 无常驻；translator 自带 E0 问闸（check_gate lane_translate_c3 local :148-149）；construct 需人工起跑 |
| 真源注册表 | MOD-BT-159=:15949,35395／190=:8928,15984,31846,35458（grep 实证）；图 9 FAC-E3 partial+algo_note_extra（159 桥/190/construct/194/193/Kronos 尾注全录）；tests 两套在盘（translator/template）+graph_enrich 两套 |
| 门禁质量尺 | 公式化子集边界；不可翻如实 translatable=false 入阴性禁硬翻；DSL 白名单+非退化 sanity；creation_token 批登记；翻译台账只追加；出生证携带 |
| 运行状态 | 绿（两轨本体）/**红（推进面+占坑）**。09-26 翻译班真实触发（对 B 三条 pass）但 **Ollama 断供致 3 行 llm_error:ConnectionError 阴性占坑**；过审 13 条真实入 E3 考卷件=4（translated 3 件 D+constructed 1 件 C，按 exam_file 实测） |

## 二、子模块三级枚举
1. **代码面**：factor_strategy_template.py 262 行（159 桥 generate_strategy_file）｜hypothesis_translator.py（load_translated_ids :122-129 **幂等按 manifest 全部 candidate_id 集跳过**、fetch_translation_seeds :58-60、run_translate :131-、_negative 阴性档 :192-228）｜auto_construct（pipeline:171-245）｜graph_enrich_staging.py+ingest.py（193，消费线未闭合）。
2. **注册表/文档面**：path_ownership_map 双锚点；FAC-E3（store_refs 空段、algo_note_extra 七件套）；QuantCode-Bench 实证作验收集依据；docs/03_modules 无独立蓝图目录。
3. **数据面**：translated_manifest 8 行明细（09-27 逐行读）：B×1 dsl 阴性+D×3 translatable=true 带考卷件+D×1 dup_expression 阴性+**B×3 llm_error 阴性（09-26）**；constructed 1 行（c4_fact_4b200528）；c4_deferrals.csv 321 行（C4 批量翻译批阴性档）。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**（159/190/人工件三轨 built 有实战；幂等推进器缺）。
- **骨架勘误**：①基册"E2 过审 13 条仅 6 条入 E3（translated 5+constructed 1）"**口径失真**：translated 5 行中 2 行为阴性（B dsl+D dup）不带考卷件——按考卷件实收=**4/13**（3 翻译+1 构造）；滞留数实为 9 条而非 7 条（本卷按 exam_file 重算）。②基册"余 7 条滞留（3 条 B pass 永久错过）"已被 09-26 部分翻案又入新坑：3 条 B pass 09-26 被翻译班取中，但 llm_error 入阴性档后被幂等全集跳过锁死（新缺陷，见缺口②）。③FAC-E3 尾注"MOD-BT-195 登记跳过（网络不可达）"与 07_f19 卷勘误同源，归并处理。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 【P0 维持】过审→E3 无幂等全量推进器 | 双 manifest 对账：13 pass vs 4 考卷件；translator=LIMIT-N 快照语义 | 施工：统一排产器（passed 幂等对照双 manifest 差集→按轨分发）1-1.5 天；消化 9 条滞留 | P0 |
| 2 | 【P1 新】llm_error 阴性行占坑死锁 | translated_manifest 0926 三行 refusal=llm_error:ConnectionError+load_translated_ids :122-129 全集跳过 | 施工：幂等跳过排除 refusal 前缀 llm_error 的行（或重试队列）；Ollama 恢复后重翻 3 条 | P1 |
| 3 | 人工件与机生件同目录混放（E4 通配混考风险） | translated/ 79 命名件+6 c4_fact_* 无目录区分 | 待裁：动 E4 引用须 SF-B 对账；机生件挪 fact/ 子目录或 manifest 加 origin 列 | P2 |
| 4 | 双 manifest schema 分立（11 列 vs 5 列） | 两 csv 表头 09-27 实测 | 施工：统一 schema v2 或加 track 列；1 天 | P2 |
| 5 | 阴性档利用率未复盘 | refusal_reason 分布未聚类 | 施工：0.5 天复盘→表达式空间扩展方向 | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核有增量：滞留口径勘误 7→9（按考卷件）；新增 llm_error 占坑缺陷（09-26 实证）；两轨本体无退化（85/6 件复测一致）。

## 六、复跑命令
```bash
ls scripts/backtest/translated/c4_*.py | wc -l; ls scripts/backtest/translated/c4_fact_*.py | wc -l   # 85 / 6
python -c "import csv;[print(r['candidate_id'],r['birth_channel'],r['translatable'],r['refusal_reason'],r['exam_file']) for r in csv.DictReader(open('data/strategy_intake/translated_manifest.csv',encoding='utf-8-sig'))]"
python scripts/backtest/hypothesis_translator.py translate --seeds 1 --dry-run   # 需 Ollama 存活
python -m pytest tests/backtest/test_hypothesis_translator.py tests/backtest/test_factor_strategy_template.py -q
```
