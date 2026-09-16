---
ttl: task_bound
completes_when: consensus_daily_repaired 双轨重建落库并验收后归档
---

# 交接包：consensus_daily_repaired 双轨重建（2026-09-16，st-expectation-20260915 → 下一班）

> 本文件=一键复制交接包的落盘副本。新对话直接执行文末"执行指令"。

## 项目背景浓缩

ZephyrAlpha=A 股量化项目。本主线=研报+一致预期消费端（C1 派生层/C1.5 夜间调度/C2 因子评估/C3 超预期事件/C4 PDF 历史修复/C5 信号融合）。核心事实：

1. **源污染**：research_report（DS-228，14.7 万行）的 EPS 预测槽位 fy0/fy1/fy2=东财源站"当前快照"语义，历史区间无 PIT（§9.1 三路实证）→ consensus_daily（DS-229，678 万行）历史快照=今天预期回放，值类因子（EXP-01/02/03/05）全阻塞。
2. **修复数据已就位**：C4 历史修复批从研报 PDF 原文提取"发布时点预测"（真历史原件），表 pdf_forecast_extracted 现有 **19.2 万行 / 55,440 份研报（2017-2021 五年，93.6%）**，其中 high 置信 39,101 行（表格路径，抽核 20/20 全对）。扫尾中（余 ~5,000 份多为永久无预测行报告）。
3. **本任务**：从 pdf_forecast_extracted 按 consensus 口径重聚合出 **consensus_daily_repaired 新表**，与污染的 consensus_daily **物理隔离双轨并存**，验收后交 Owner 切换。值类因子随之解锁。

## 必看文件（真源，按序读）

- D:/ZephyrAlpha/AGENTS.md —— L0 宪法（冷启动序列 §0 必做：PATH 3.12.8/reaper/worktree/claim/ROOR）
- D:/ZephyrAlpha/docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md —— §8 预注册/§9 污染档案/§9.3 处置（Owner 裁 A）/§9.3.4 裁定#253
- D:/ZephyrAlpha/docs/_working/2026-09-14-c4-history-repair-plan.md —— **重建方案真源**（§L48/L64-65：双轨隔离禁改历史；§5 病菌寻路；§6 验收标准=锚点准确率≥90%+抽核 30 份+Owner 门位）
- D:/ZephyrAlpha/docs/_working/2026-09-15-c4-acceptance-interim.md —— 阶段验收+抽核首批 15 份台账
- D:/ZephyrAlpha/docs/_working/reports/2026-09-16-c4-audit-batch2.md —— 抽核第二批 5 份+本班事件留痕（双进程/队列 landed_id/stash 吞改动）
- D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml —— 裁定#253（EXP-04/06 放行，尾部条目）

## 工作文件（代码，全部实证存在）

- D:/ZephyrAlpha/scripts/ch/build_consensus_daily.py —— **现 consensus_daily 构建器 CLI（重建逻辑的口径母本：90 自然日窗/publish_date≤trade_date/评级映射/fy 选择）**
- D:/ZephyrAlpha/src/zephyr/data/implementations/consensus_daily_compute.py —— 现构建核心（MOD 实现层）
- D:/ZephyrAlpha/scripts/ch/apply_consensus_daily_ddl.py —— 现表 DDL 部署（新表照此先例）
- D:/ZephyrAlpha/schemas/categories/fundamental/consensus_daily.py —— 现表 schema 真源（新表 schema 照此+provenance 列）
- D:/ZephyrAlpha/schemas/categories/fundamental/pdf_forecast_extracted.py —— 提取表 schema（重建的数据源）
- D:/ZephyrAlpha/scripts/ch/apply_pdf_forecast_extracted_ddl.py —— 提取表 DDL 部署先例
- D:/ZephyrAlpha/src/zephyr/data/c4_history_repair.py —— 提取链核心（下载/文字层守卫/两级提取）
- D:/ZephyrAlpha/scripts/ch/c4_extract_batch.py —— 全量批 CLI（督导器看护中，**勿动进程**）
- D:/ZephyrAlpha/src/zephyr/factor/expectations.py —— 六 EXP 因子（重建后值类复评的消费方）
- D:/ZephyrAlpha/scripts/backtest/eval_exp_expectations.py —— 评估器（--factor exp02/04/06；重估需扩 repaired 源）
- D:/ZephyrAlpha/src/zephyr/data/consensus_crosscheck.py —— 23:30 双向对账（可扩展对 repaired 表）
- D:/ZephyrAlpha/src/zephyr/data/config/tasks.yaml —— consensus_daily_build @ L592-603（现管线登记形态）
- D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml —— DS-228@L9690/DS-229@L9772（新表须登记 DS-23x）
- D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml —— FCT-EXP-001~006 @ L12379-12612
- D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml —— EXP-FACTOR-EVAL-001/002/003 @ L597+

## 环境事实（实测，省时间）

- 系统 python 3.12.8：`export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"` + `PYTHONPATH=D:/ZephyrAlpha/src`
- 提交：`python scripts/git_commit.py --session <sid> --files <逗号清单> --message-file <utf8文件> --allow-non-worktree --enqueue`（队列正门，入袋即安全；直连会被他会话 staged 全仓扫描 gate 连坐）；landed_id 幂等空转现记 `noop@<sha>` 哨兵（ec366cfaa7）
- 会话：SessionRegistry.register(pid=0) 后**每 15 分钟内须 heartbeat**（否则被 reaper 收割触发 SESSION-REQUIRED）；lock_files.py acquire/release-all
- 热文件写：safe_write_text 必带 expected_base_sha256=content_sha256(原文)；registry 尾部追加用锚点断言唯一
- 新建 .py：14 字段头+add_module_translation.py 登记+depgraph --add-design-node+creation_token（走 scripts/governance/d3_metadata/batch_creation_tokens.py 库，勿裸写）
- 新建 .md 于 docs/_working：仅 reports/ 等子目录可行（平铺 139 份顶格 FOLDER-CAPACITY 硬拦）+frontmatter ttl: task_bound+completes_when+creation_token
- pytest：`-o cache_dir="$TEMP/pytest_zc"`（.runtime/tmp 缓存被 ACL 锁）
- 量纲：kline_daily.volume=手；stock_indicator.circ_mv=万元；换手推导=volume(手)×100÷(circ_mv(万元)×1e4÷close)
- CH：一律 ch_reader；ReplacingMergeTree 读 FINAL；长结果集按月分块+日期白名单
- C4 批在跑：勿动 c4_* 进程；若机器重启过，`python .runtime/tmp/c4_supervisor.py` 重启（已登 reaper 白名单）
- PDF 缓存已迁 F 盘：data/c4_pdf_cache → F:\zephyr_c4_pdf_cache（junction，D 盘勿回迁）

## 执行指令（按序）

1. 冷启动宪法 §0 全序；读本文档+方案文档 §L48/§L64-65/§6。
2. **抽核滚动**（欠 10 份，每夜 5 份）：从 pdf_forecast_extracted 生产行 cityHash64 序抽 5 份（排除已抽 20 份的 report_id），fitz 渲染预测表页目视核对，台账续记本文件同目录。
3. **新表 schema**：schemas/categories/fundamental/consensus_daily_repaired.py（照 consensus_daily.py+provenance 列：source_method/source_report_ids 样本数）+DDL 部署脚本（照 apply_consensus_daily_ddl.py 先例）——物理隔离，禁触碰 DS-229。
4. **重建 builder**：scripts/ch/build_consensus_daily_repaired.py——口径对齐现 builder（90 自然日窗、publish_date≤trade_date、评级 7/5/3/2/1 映射、fy1=≥当年最小预测年），数据源换 pdf_forecast_extracted **high-only**（mid 留档不入聚合、low 排除——抽核实证 high 20/20 全对）；2026-07 起段可叠加 analyst_forecast 干净源（双源合流，标注来源列）。
5. **对照验收**：①repaired vs 现 consensus_daily 在 2026-07~09 双源重叠段秩相关（应高）；②对 600519 等锚点股画 repaired 历史曲线 vs 污染曲线（应显著不同且符合"预期随财报事件阶梯变化"常识）；③抽 10 份研报人肉对照窗口聚合值。
6. **登记**：DS-23x（data_asset_registry，标 dual_track=true/switch_gate=Owner）+capability+business_data_categories+module_translation；exp 侧 doc_ref 回填。
7. **复评解锁**：eval_exp_expectations.py 扩 --source repaired（或参数化表名），EXP-01/03/05 + EXP-02 复核跑 ④⑤⑥，归档 EXP-FACTOR-EVAL-004+；EXP-04 复评（裁定#253 预留旋钮）。
8. **收尾**：正门提交（--enqueue）；workbuddy/auto-memory 交底；2022-2026 段（8.6 万份）夜窗接续为独立后续任务。
