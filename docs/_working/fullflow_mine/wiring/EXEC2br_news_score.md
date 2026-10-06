---
ttl: task_bound
title: "新闻评分链诊断报告r"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# 新闻评分链诊断报告（EXEC-2b-r 重派收口）

## 1. 结论速览

- **根因（已定案，非新发）**：`c3_fundamental.news_sentiment_score` 唯一写入口是
  `scripts/governance/meta_question/wo_a2legs/backfill_news_sentiment.py` 一次性回填件
  （硬编码 `CUT=2025-09-09`、task_bound 冻结）。**表建成即无日更生产者**，
  2025-09-10 起断供 13 个月。排除项：非任务 disabled、非接口字段漂移、非路径变更、
  非 LLM 通道故障。
- **机制判定**：规则法词典打分（`RuleBasedSentimentScorer`，反转短语先扣+ST 词边界
  +正负词典），LLM 仅为可选注入扩展口（`nlp_inference`），**存量与增量均不依赖 LLM
  通道**——不触发"LLM 则只诊不修"分支。口径指纹 `rule-a0e3f2b6d3` 与存量 7.7M 行
  逐字节一致（前手探针核实，本手抽验 caliber_version 一致）。
- **处置**：属"根因可当日修"分支，且前手 EXEC-2b（超时阵亡）已把修复件全部落盘，
  本手 2b-r 完成验证、合规补登记与提交落地。

## 2. 修复件清单（本批提交，commit 见 §5）

| 文件 | 角色 |
|------|------|
| `src/zephyr/intelligence/news_score_daily.py` | 日更+区间回补唯一生产者（新） |
| `src/zephyr/data/scheduler.py` | `nightly_news_score` 槽接线（惰性导入+总闸实查+异常降级 alerter） |
| `src/zephyr/data/config/schedule.yaml` | 08:50 日频 cron 注册（全周 7 天，空新闻日零成本） |
| `tests/intelligence/test_news_score_daily.py` | 单测 5 例（reader/client/store 全注入，tmp_path 隔离） |
| `docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml` | 大白话简介登记（本手补，TRANSLATION-COVERAGE 合规） |

生产者要点：只读 `fund_news_data`（FINAL 去重）零改写母表；经在册 Scorer 打分落 CH
（ReplacingMergeTree 同键 `(caliber_version,news_id,publish_time)` 幂等）；断点续传
ProgressStore（task_id=news_sentiment_score_daily/backfill）；服务总闸
`data/runtime/news_score_daily.disabled`（存在=停用，每次触发实查即时生效）。

## 3. 验证读数（2026-10-04，CH 只读复核）

- **断供窗已闭环**：2025-09-10 ~ 2026-09-24 逐月原料(`fund_news_data` FINAL)-评分
  对齐 **13/13 月 100.0%**（稀疏月系原料本身薄，非评分缺口；前手已做全缺口回填而非
  仅 7 天）。缺口窗合计 197,094 行。
- **链路存活**：表总量 7,947,739 行（断供时 7,733,898），`max(publish_time)=
  2026-10-04 04:34+08`；近 7 日逐日 932~3558 行（scored_at=2026-10-03T21:08~21:12Z）。
- **幂等复核**：本手重跑 `--backfill --start 2026-10-01 --end 2026-10-01` →
  `ok=true, skipped=1, rows=0`（ProgressStore 判日已完成，零重复）。
- **测试**：`pytest tests/intelligence/test_news_score_daily.py` 5/5 过（3.0s）；
  改后 `zephyr.data.scheduler` 可加载。
- **未复跑项**：调度器进程若常驻，`schedule.yaml` 热加载行为未验——次日 08:50
  首跑为准，失败走 alerter ERROR 告警（fail-visible），不静默。

## 4. 残留与移交（工单级）

1. **【P1 工单】capability_canonical_file_registry 账本迁移缺口 → CREATE-GUARD 挡提交**：
   本手 6 文件提交四连试被 CREATE-GUARD 硬拦，根因定位为**投影账本（PG ledger
   REG-CAPCAN-001，rev 13）不含 news_score_daily.py 的 creation_token**——该 token
   在 HEAD（`git show HEAD:<registry>` 可见，token=`news-score-daily-news-score-daily-20261003`，
   created_by=st-datasop-20260930，capability=news_score_daily，含 merge_evaluation），
   但账本迁移时未导入，PG 渲染（--render PG wins）合法地把它从册面洗掉了。
   处置中已发生的册面事故与本手修复：盘面曾被他手压陈旧快照（相对 HEAD 缺 10 条），
   本手条目级并集合并误吞尾部 `di_seam_exemptions` 顶层键区段，**已走正规通道修复**：
   `registry_projection_generator.py --render --session st-datasop-20260930`
   （PG wins，rev13，`--check` 零漂移，顶层键在位），干净渲染版已 `git add` 压回索引，
   全部 claim 已 `--release-only` 释放（6/6）。
   **接手工单处方**：走 02号文§3.1 意图 API 重登记后重打——
   `zephyr.governance.registry_ledger.api.register(registry_id="REG-CAPCAN-001",
   family_key=<照 baseline._iter_scan_entries 扫描派生>, payload={HEAD 原条目 5 字段
   原文照抄}, reason=..., session_id="st-datasop-20260930")` →
   `registry_projection_generator.py --render` → CREATE-GUARD 即过 →
   按 §5 原命令重提交。禁再手工改册面（投影指纹门会拦）。
2. **RULE-DEPGRAPH 设计节点**：`apply_depgraph.py --add-design-node` 未见本件登记，
   移交下岗按施工收尾补登。
3. **LLM 轨扩展**：逐条分表若切 LLM 打分须 Owner 门位+口径评审（模块头 INVARIANTS
   在案）；现行 `nightly_sentiment_llm` 对照期仅作用于 `news_sentiment_window`，
   与本表无涉。
4. **运营注记**：调度器 08:50 首跑从工作树导入本件（不依赖 commit 落地）——
   数据链当前已存活；提交阻塞不影响日更，但拖久会有"工作树被清理即断供"的暴露面，
   建议工单 1 次日内收口。

## 5. 提交与 lever 留痕（终态：提交未落地，工单移交）

- 6 文件提交走 `scripts/git_commit.py --session st-datasop-20260930`（消息文件
  `.runtime/tmp/exec2br_msg.txt`，含根因/验证/lever 三段），**终态=未落地**：
  依次被 COMMIT-SCOPE 跨域（→`--allow-multi-domain` 过）、Ruff Format（→格式化后
  过，5 测试复绿）、CREATE-GUARD（token 账本缺口，硬拦无逃生，见 §4.1 工单）拦停；
  CLAIM_REQUIRED_VIOLATION 亦出现过（lock_files 与网关 claim 册异源，`--allow-overlap`
  可越，已留痕）。全部 lever：`--adopt-prior-work`/`--skip-preflight`/
  `--allow-non-worktree`/`--no-auto-enqueue`/`--allow-multi-domain`/`--allow-overlap`/
  `ZEPHYR_PRECOMMIT_DEBT_RATCHET=0`。
- **现场保全**：索引中 capability_canonical_file_registry.yaml=干净 PG 渲染版
  （非本手坏合并版）；6 文件改动全部留工作树+索引，claim 已全释放；消息文件保留
  （`.runtime/tmp/exec2br_msg.txt`，网关提示可直接重跑同一命令）。
- 备注：网关直连在 9 会话并发下 >55s（会话册扫描+门自注册扫描），短超时直连会被
  SIGTERM 杀在落地前——本手改后台长窗执行；**提交落地后必须 `git log -1 --name-only`
  复核真实归属**（暂存区可能吸收他会话内容，宪法 §2.5）。
- 本报告留盘移交，不单独提交（投影册战争区）。

## 6. 复现命令（交接用）

```bash
# 日更（调度同款）
python -m zephyr.intelligence.news_score_daily --daily
# 任意区间回补（断点续传；--redo 强制重灌，同键幂等）
python -m zephyr.intelligence.news_score_daily --backfill --start 2025-09-10 --end 2026-10-03
# 停服开关
#   建文件 data/runtime/news_score_daily.disabled 即停，删除即恢复
```
