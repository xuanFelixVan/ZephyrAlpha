---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F29 工厂进货台账与出生证——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F29 · 工厂进货台账与出生证

> 组 SF·策略工厂供给链 B 后半册 7/7。上游 F14-F22（全工厂进货/预审/构造面），下游=全工厂（任何环节回溯"这策略哪来的"唯一凭证）。
> 环节真源：M0 总册 F29 行（状态 partial）；data/strategy_intake/ 台账族+CH 三台账。

## 一、环节定义与边界

一句话：候选想法/翻译件/考卷件的 manifest 台账族——每件货带出生证（渠道+批次+原文指针/表达式/考卷路径），从 E1 进货到 E4 判定全链可溯。
边界：本环节=台账**体系**本身（出生证字段链完整性），不含各环节业务逻辑；台账只增铁律在此立法（c4_batch_screen/C2 原行零触碰先例）。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | 六车道 csv（lane_b/c/c2/g/chain/three_high）+聚宽盘点（raw_manifest）+F06 网格批次 manifest（grid_*/manifest.csv 21 批次实测）+翻译件清单（translated_manifest/constructed_manifest） |
| 下游消费 | E2（台账幂等消费）、E4（--auto-only 发现未考件）、E6（注册表 evidence run 指针+doc_ref）、E8（birth_channel 赛马计分板 race_scoreboard）、Owner 审计（inventory 盘点） |
| 自动化触发 | 无统一触发——台账族由各车道/各环节写侧追加（写时即证）；factory_intake_pipeline construct 子命令逐行追加 constructed_manifest（追加即 flush，factory_intake_pipeline.py:240-242） |
| 真源与注册表 | csv 族=data/strategy_intake/（2026-09-25 实测行数见下表）；CH 族=c1_backtest.hypothesis_precheck（candidate_id+birth_channel 出生证主档）/c1_backtest.strategy_screen（strategy_id+source_file+run_id+screen_batch）；注册表=registry entry 内 doc_ref/code_path/evidence |
| 门禁与质量尺 | 台账只增不改（C4 结果以新 screen_batch 追加、C2 原行零触碰）；md5_12 内容指纹防重；考卷件入 translated/ 前必须过 creation_token 登记+编译自检（factor_strategy_template.py:13）；幂等键四键（batch,sid,verdict,source_file） |
| 当前运行状态 | **绿（台账活）+黄（出生证断链两处）**。实测：raw_manifest=597、screen_c2=597、c4_deferrals=321、three_high=40、lane_c=16、lane_chain=10、lane_c2=8、translated_manifest=5、lane_b=4、f06_survivors=1、**constructed_manifest=1**、**lane_g_candidates=0（仅表头）**、lane_g_seen_urls=5 |

## 三、子模块清单（台账族逐一+出生证字段链）

| 台账 | 出生证字段 | 行数(09-25) | 状态 |
|------|-----------|-------------|------|
| raw_manifest.csv | seq/year/orig_name/md5_12/normalized_rel | 597 | built（车道 A 盘点批） |
| screen_c2.csv | C2 粗筛批次判定 | 597 | built |
| c4_deferrals.csv | 挂起原因枚举（deferred_*_gap 族） | 321 | built |
| three_high_candidates.csv | candidate_id+三高支柱分（车道 D） | 40 | built |
| lane_c_candidates.csv / lane_c2_ / lane_chain_ / lane_b_ | candidate_id+birth_channel+expression | 16/8/10/4 | built |
| lane_g_candidates.csv | candidate_id+birth_source(url 指针) | **0** | **台账在、货为零**（seen_urls=5 说明胃侧处理过 5 url、0 条假说过审出库——车道 G 进货断供，归 SF-A F20 处置） |
| translated_manifest.csv | 翻译件清单（MOD-BT-190 假说轨） | 5 | built |
| constructed_manifest.csv | candidate_id/birth_channel/strategy_id(FACT-hash8)/exam_file/constructed_at | **1** | **断链①**：translated/ 下 c4_fact_*.py 实有 6 件（4b200528/4228020a/4db4c41e/4f749668/e293e217/e831084c），manifest 仅 1 行——5 件考卷件绕过 auto_construct 产出（早期手工/模板期产物），E4 成绩可查但 E3 出生证缺行 |
| f06_survivors.csv | recipe_id/birth_batch/values_json/exam_archive | 1 | built（F06 车道出生证最完整样本：配方参数+考试档案路径+dedup 指针全带） |
| grid_*/manifest.csv | 批次 manifest（MOD-BT-196 落盘） | 21 批次 | built |
| c1_backtest.hypothesis_precheck | candidate_id/birth_channel/verdict | CH | built（E2 出生证主档，race 计分板数据源） |
| c1_backtest.strategy_screen | strategy_id/source_file/run_id/screen_batch/num_trials | 1341 | built（E4 出生证主档） |
| strategy_registry.yaml | entry 内 doc_ref/code_path/evidence | 162 | built（字段完整度参差见堵点 3） |

## 四、堵点与病灶

1. **constructed_manifest 缺 5 行**（现象/根因=c4_fact_* 6 件 vs manifest 1 行，早期件先于 auto_construct 上线产出；修法=补登 5 行（exam_file/constructed_at 回溯自 git 提交史）或裁定"冻结批前件豁免"；工作量=S；本车道可修=是，须裁定登记防台账改史争议——补登=追加行非改行，符合只增铁律）。
2. **车道 G 零出货**（lane_g_candidates=0 行——进货环节无货，台账面无断链，断在供货侧；归 SF-A F20，此处仅登记台账证据）。
3. **注册表出生证参差**：162 条 entry 的 evidence/doc_ref 字段完整度不一（模板批 vs 早期手工批）；修法=注册表净扫一次性补齐（E6 域施工，非台账结构问题）；工作量=M。
4. **strategy_id 三命名系并存**：CAND-<md5_12>（翻译件）/FACT-<hash8>（公式轨）/STR-<模板>（注册表）——同件跨台账靠 candidate_id↔strategy_id 映射行维系；constructed_manifest 断链即映射断链（堵点 1 的因）。建议注册表 entry 补 candidate_id 反查列（登记级）。

## 五、提速与合并机会

- 台账族 13+csv 无统一清单器（本册三为手工盘点）——凡"条目列表+计数"清单必须生成器产出（运维红线 §9.5）：建议一个小型 inventory 生成器扫 data/strategy_intake/*.csv 行数+最新 mtime（S 级），替代手工盘点防漂移。
- race 计分板（cmd_race）已聚合 E2 漏斗，可扩读 constructed/screen 行数成为全链出生证仪表（复用不新建）。

## 六、自审闸三态

**挖干可施工**。台账族双源盘点齐（ls+wc 实测+脚本写侧交叉）；断链两处（constructed 缺行/registry 参差）有根因+修法；车道 G 零货归邻册。补登 5 行与命名系统一=待裁两小案随册呈总筹。

## 七、复核命令（10 分钟）

```bash
wc -l data/strategy_intake/*.csv | sort -rn | head -14      # 台账族行数
ls scripts/backtest/translated/c4_fact_*.py | wc -l         # 6 件 vs manifest 1 行
head -2 data/strategy_intake/constructed_manifest.csv
head -2 data/strategy_intake/f06_survivors.csv              # 出生证最完整样本
python scripts/backtest/factory_intake_pipeline.py race     # E2 漏斗按车道聚合
```
