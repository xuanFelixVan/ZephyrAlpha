---
ttl: task_bound
title: F29 工厂进货台账与出生证——L03 接线矿道案卷（台账只增铁律的出生证链）
session: zc-l03-20260927
---

# F29 · 工厂进货台账与出生证

> 挖矿基册=01_strategy_factory/b2_f29_factory_ledger_birth_cert.md（SF-B 工厂台账册）。本卷=09-27 全族逐行复测+出生证缺行收敛实证（5→2）。

## 一、六向台账
| 向 | 实证锚点（09-27 逐 csv 实测） |
|----|------|
| 上游 | 六车道+盘点+翻译/构造 manifest。data/strategy_intake/ 数据行数（csv.DictReader 口径）：raw_manifest=597/screen_c2=597/c4_deferrals=321/**three_high=60（基册 40，+20）**/lane_c=16/lane_chain=10/lane_c2=8/**translated=8（基册 5，+3=09-26 班）**/lane_b=4/lane_g_seen_urls=5/**lane_g_candidates=0（维持零货）**/constructed=1/f06_survivors=1 |
| 下游 | E2（CH 幂等消费）/E4（--auto-only 发现未考件）/E6（evidence run 指针）/E8（birth_channel 赛马）/Owner 审计；race 计分板本日实跑：D 过审 8+B 过审 4+C 过审 1=**13 维持** |
| 自动触发 | 无统一触发维持（写时即证）；factory_intake_pipeline construct 追加即 flush；translated +3 行为 hypothesis_translator 09-26 班产物（3 行 llm_error 阴性占坑=L02 卷缺陷②实证） |
| 真源注册表 | CH 双主档=c1_backtest.hypothesis_precheck（E2 出生证）/c1_backtest.strategy_screen（E4 出生证，total=1351/uniq=574 本日实跑）；strategy_registry 162 键（doc_ref/code_path/evidence 完整度参差维持）；图无独立 F29 节点（跨切面环节，总册 F29 行 partial） |
| 门禁质量尺 | 台账只增不改；md5_12 指纹；幂等四键；creation_token+编译自检前置（factor_strategy_template.py:13 维持） |
| 运行状态 | **绿（台账活）+出生证断链收敛中**。**c4_fact_* 6 件中 4 件已补得 manifest 行**：4228020a/4f749668/4db4c41e=translated 09-26 班 D×3 考卷行、4b200528=constructed 原行——**缺行 5→2（e293e217/e831084c，两件均 bothwin 及格在账）**；lane_g 零货维持（归 L02 F20）；m2 册 tmp 污染已清（scripts/backtest 0 tmp 本日 ls） |

## 二、子模块三级枚举
1. **代码面**：factory_intake_pipeline.py（construct/race/inspect 子命令；_CONSTRUCT_LANES=("C","C2") BP-1 维持；_e2_passed_by_channel fail-silent BP-2 维持——两文件与 HEAD 一致无在途改动）；hypothesis_translator.py（LIMIT-N+llm_error 占坑，L02 域）；strategy_screen_query.py（出生证查询面）。
2. **注册表/文档面**：b2_f29 基册（台账族立法册）；strategy_registry.yaml（candidate_id 反查列建议维持登记级）；m2_backtest_sim/02_backtest.md 2.9 批次筛选/工厂管线族交联；无统一 inventory 生成器维持（运维红线 §9.5 欠账）。
3. **数据面**：13+csv 台账族全活（行数见表）；translated_manifest 8 行明细本日逐行读：B×1 dsl+D×3 考卷+D×1 dup+B×3 llm_error——阴性/占坑 5 行 vs 考卷行 3 行；constructed 1 行（FACT-32e5c744→c4_fact_4b200528，2026-09-15）。

## 三、接线四态独立复核
- 总册 partial → **维持 partial**，无态变。
- **骨架勘误**：①基册"constructed 缺 5 行"按 09-27 口径更新为"**缺 2 件**"（translated 09-26 班 3 行自带 exam_file 指针，客观上为 3 件 fact 件补了出生证链——虽走翻译轨非构造轨，映射 candidate_id↔strategy_id 已通）；②three_high 40→60（+20 条新进货，车道 D 在产）；③translated 5→8（+3 全阴性占坑，考卷产能实际 +0）。
- L02 交叉：转化率 4/13 维持；出生证缺行数与 L02"4/13 按考卷件实收"口径自洽（4 考卷件=3 翻译+1 构造）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | fact 件缺出生证 2 件（e293e217/e831084c 已及格） | manifest 对账本日 | 补登 2 行（追加非改行，符合只增）或裁定豁免；S | **P0**（原 P1 因及格在账升格） |
| 2 | translated 3 行 llm_error 占坑死锁 | 0926 三行+load_translated_ids 全集跳过 | L02 缺口②同案：幂等跳过排除 llm_error 前缀+Ollama 恢复重翻 | P1 |
| 3 | 车道 G 零货 | lane_g_candidates=0 维持 | 归 L02 F20，本卷仅登记台账证据 | P1（邻域） |
| 4 | 注册表出生证参差+反查列缺 | 162 键字段巡检未做 | E6 域净扫；candidate_id 列登记级 | P2 |
| 5 | 台账族无生成器清单器 | 本卷手工盘点第 3 次 | 小型 inventory 生成器（§9.5 红线）；S | P2 |
| 6 | strategy_id 三命名系并存 | CAND-/FACT-/STR- | 命名统一待裁维持 | P2（待裁） |

## 五、自审闸三态
**挖干可施工（复核维持+断链收敛实证）**。台账族 13+csv 全活双源核对；出生证缺行 5→2 有逐行证据；车道 D 进货 +20 为全链少有的增量绿点；补登 2 行待裁随册呈总筹。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python - <<'EOF'
import csv,glob,os
for f in sorted(glob.glob('data/strategy_intake/*.csv')):
    print(len(list(csv.DictReader(open(f,encoding='utf-8-sig')))), os.path.basename(f))
EOF
ls scripts/backtest/translated/c4_fact_*.py | wc -l        # 6
for f in e293e217 e831084c; do grep -c "$f" data/strategy_intake/*.csv | grep -v ":0" ; done  # 仅 screen 台账有、manifest 无
python scripts/backtest/factory_intake_pipeline.py race    # 13 过审维持
python scripts/backtest/strategy_screen_query.py summary   # 1351/574
```
