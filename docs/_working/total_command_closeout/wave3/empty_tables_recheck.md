---
ttl: task_bound
completes_when: 三态复测表落盘 + strict 分箱结论出 + known_data_gaps.yaml 纯追加且删除集为空断言通过
---

# W-34 空壳表 strict 复测案卷（波 3.0/3.5 · 内收：扩既有严格读家族，不新建第二套尺）

- **turn_budget**: 150（本包实耗 ≈20 次工具调用；骨架在第 8 次调用落盘；单块调研 ≤6 次；后期只落盘）
- **evidence_ref.cmd**:
  - 复测：`cd D:/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src && set -a && . /d/ZephyrAlpha/config/.env.clickhouse && set +a && python scripts/governance/wave3/recheck_empty_tables.py --apply-gaps`
  - 机读产物：`docs/_working/total_command_closeout/wave3/empty_tables_recheck.tsv` / `.json`（本包临时输出，声明为机生禁手改）
  - 进程外核实：`python -c "import yaml;d=yaml.safe_load(open('src/zephyr/data/config/known_data_gaps.yaml',encoding='utf-8'));print(len(d['gaps']))"` → **74**
- **input_set_disjoint_with**: `docs/_working/total_command_closeout/wave11/**`（兄弟包在用，本包零读写）；
  本包写面仅三处＝本案卷、`scripts/governance/wave3/recheck_empty_tables.py`、
  `src/zephyr/data/config/known_data_gaps.yaml`（纯追加）＋上述两个机读产物。
- **verified / assumed 分列**：见 §一（9 条现读）与 §二（4 条假设，其中 3 条已被本包实测判定）。

## 一、verified（现读取得，均可复算）

| # | 事实 | 出处（文件:行号） |
|---|---|---|
| V1 | 在册结论"W-34 空壳表 9–10 张：逐表建采集腿 vs 登记 known_data_gaps"，态 ⬜ | `docs/_working/total_command_closeout/00_master_skeleton.md:82` |
| V2 | `count()` 契约＝"查询失败返回 0"，失败态与真 0 行不可分，W-180.1 禁判据类计数裸用 | `src/zephyr/data/ch_reader.py:131`（docstring 起） |
| V3 | 严格通道已在场：`query_rows()` 失败必抛、`count_strict()` 失败/形状异常必抛且真 0 行＝确证空表 | `src/zephyr/data/ch_reader.py:239`、`:251` |
| V4 | 传输层：TCP 9000 主、HTTP 8123 次；`last_transport()` 供"实际成功路径"观测 | `src/zephyr/data/ch_writer.py:5`、`:77-78`、`:521` |
| V5 | 波 3.0 令＝"空壳表清单用 strict 通道复测重出（防 `count()` 返回 0 造假空壳），逐表给 strict 读数/传输路径/时间戳三列，禁照抄旧数" | `docs/_working/total_command_closeout/10_wave_plan.md:80`（3.0）、`:85`（3.5 三分补登记） |
| V6 | "曾被判空壳"的表全集＝骨架病灶 B「已知 4 张 + 并集去重后另有 10 张」＝**14 张**（现读复原） | `docs/_working/chain_fullflow_closeout/business_pipeline_skeleton.md:147-152` |
| V7 | 另一套旧数"空壳表 9 张"但点名 8 张（6 未登记 + `suspend` + `etf_benchmark`） | `docs/_working/chain_fullflow_closeout/mine_pipe_blockage_substages.md:121` |
| V8 | 第三套旧数＝G 窗口实读点名 12 张中 11 张 count()=0，唯一非 0 是 `suspend`（36 行，max trade_date 2026-09-23）；三处张数不一致已记为 N9 | `docs/_working/total_command_closeout/dossier_G_business_chain.md:116-141`、`:313`（N9）、`:339` |
| V9 | 旧读数面本身是 fail-silent 双源：`ch_writer.query()` 异常时 `return ""`（骨架落库读数用它） | `docs/_working/total_command_closeout/dossier_G_business_chain.md:312`（N8） |
| V10 | 跨库名称探测会静默返回 0（N6）⇒ 本包在册探测一律带 `database=` 库限 | `docs/_working/total_command_closeout/dossier_G_business_chain.md:310`（N6） |
| V11 | 空壳处置早有条件批文 #311/#328，W-34 改判为执行任务（非"请 Owner 新批"） | `docs/_working/total_command_closeout/02_field_corrections_and_new_cases.md:93`（X-53） |

## 二、assumed → 本包判定结果

| # | 原假设 | 判定 |
|---|---|---|
| A1 | "W-34 空壳清单可能是 `count()` fail-silent 造出的假空壳" | **本表集合内不成立**：14 张在册点名表全部走 strict（`count_strict`）复测，13 张确证 0 行、1 张有数据（`suspend`=36），**0 张读失败** ⇒ 无一张是"把查询失败读成空表"的产物（§四） |
| A2 | CH 本窗口可达 | **成立**：可达性哨兵 `SELECT count() FROM system.tables WHERE database='c1_market'` 经 **tcp:9000** 通过，全部 14 张读数传输路径＝`tcp:9000`，单表耗时 13.3–19.4ms（产物 ts=2026-09-26T18:03:35.642+00:00 起） |
| A3 | 14 张表全部仍存在于 `system.tables` | **成立**：带库限在册探测 14/14 命中 ⇒ `table_missing_in_ch` 子因 0 次 |
| A4 | gap 条目字段格式 | **已现读**并照抄：`known_data_gaps.yaml:74-90`（edb_data empty_table 范式）、`:805-815`（sector_fund_flow_empty 用 `start_date: ""` 先例）、`:1404-1417`（最新条目含 `impact`/`evidence` 字段） |

## 三、复测器与内收声明

- 件：`scripts/governance/wave3/recheck_empty_tables.py`（新建，纯普查编排）。
- 读数面**零新增**：只调 `zephyr.data.ch_reader.count_strict()` / `query_rows()`（W-180.1 严格通道）与
  `ch_writer.last_transport()`；字段口径（ts_utc / sql / transport / elapsed / rows）对齐
  `scripts/governance/data_supply/ch_probe.py:1-40` 既有探针规范；`scripts/governance/data_supply/strict_truth_reader.py`
  的"失败必抛、禁把 0/''当证据"契约在本件逐字沿用。
- **内收账（净零）**：仓内 grep `empty_table|shell_table|空壳|count_strict` 后确认**无既有"空壳表普查器"**
  （仅有 `src/zephyr/gov_enforcement/commit_gates/empty_handler_gate.py`＝提交门 handler 尺，异对象不同域，不并）。
  本件不新增阈值／不新增 gate／不新增 flag／不新增配置册；替代的旧件＝波 3 之前各班**手写一次性 CH 探测脚本**
  （散落于 `.runtime/tmp/dossierG/ch_recheck*.py`，见 `dossier_G_business_chain.md:310`），收敛为"严格通道 + 本普查编排"单一路径。
- 三态常量互斥：`vacuum_confirmed` / `has_data` / `read_failed`；代码层硬保证
  "表不在册"与"传输/形状异常"都进 `read_failed`（子因 `table_missing_in_ch` / `strict_read_error` / `ch_unreachable`），
  **读失败绝不追加 gap**（`--apply-gaps` 候选集＝仅 `verdict==vacuum_confirmed`）。

## 四、分箱结论（strict 现读，禁照抄旧数；下表读数/判定＝写入 gap 条目的那次运行 `ts=2026-09-26T18:03:35.642+00:00`，盘上产物 `empty_tables_recheck.tsv/json` 系复跑运行 `ts=2026-09-26T18:06:37.892+00:00`——**判定与行数逐行同值，仅耗时/时间戳随运行漂移**）

| 表（c1_market.*） | 旧数（点名来源） | strict 行数 | 传输 | 耗时(ms) | 判定 | 差异解释 |
|---|---|---:|---|---:|---|---|
| suspend | 0（骨架 `:147` 已知 4 张；blockage `:121` 亦列入 9 张） | **36** | tcp:9000 | 18.3 | **①假空壳（翻案）** | 翻案原因＝**时点过期**，非读数通道污染：G 窗口早于本包也已读到 36（`dossier_G:137`，max trade_date 2026-09-23）⇒ 骨架快照时该表确为 0，其后有腿进数。旧数出自 `count()`／`ch_writer.query()` fail-silent 面（V9），但本例失败态未参与，**不得指认为假空壳=通道污染** |
| account_nav_daily | 0（骨架 `:147`） | 0 | tcp:9000 | 13.3 | ②真空确证 | 通道无关，strict 复现；**未登记** ⇒ 本次补登记 |
| etf_benchmark | 0（骨架 `:147`；blockage `:121`） | 0 | tcp:9000 | 16.0 | ②真空确证 | 复现；补登记 |
| l2_tick | 0（骨架 `:147`） | 0 | tcp:9000 | 19.4 | ②真空确证 | **已在册**（`known_data_gaps.yaml:209-216` `l2_tick_permission_required`，permission_required/accepted）⇒ 不动 |
| edb_data | 0（骨架 `:150`） | 0 | tcp:9000 | 17.6 | ②真空确证 | **已在册**（`known_data_gaps.yaml:74-90` `edb_data_ifind_quota_exhausted`）⇒ 不动 |
| realtime_snapshot | 0（骨架 `:150`） | 0 | tcp:9000 | 13.6 | ②真空确证 | 复现；补登记（骨架注"落库断"属归因待判，本包不代裁） |
| index_valuation_daily_v2 | 0（骨架 `:150`） | 0 | tcp:9000 | 16.7 | ②真空确证 | 复现；补登记 |
| ipo_schedule | 0（骨架 `:150`；blockage `:121`） | 0 | tcp:9000 | 17.9 | ②真空确证 | 复现；补登记 |
| margin_target_adjustment | 0（骨架 `:150`；blockage `:121`） | 0 | tcp:9000 | 18.1 | ②真空确证 | 复现；补登记 |
| market_index_meta | 0（骨架 `:150`；blockage `:121`） | 0 | tcp:9000 | 17.2 | ②真空确证 | 复现；补登记 |
| msci_adjustment | 0（骨架 `:150`；blockage `:121`） | 0 | tcp:9000 | 16.9 | ②真空确证 | 复现；补登记 |
| reconciliation_differences | 0（骨架 `:150`） | 0 | tcp:9000 | 14.5 | ②真空确证 | 复现；补登记（"真源在 governance.db"是 W-36 三源收敛议题，与本格"表空"不互斥，本包不裁） |
| stock_candidate_pool | 0（骨架 `:150`；blockage `:121`） | 0 | tcp:9000 | 16.2 | ②真空确证 | 复现；补登记 |
| stock_valuation | 0（骨架 `:150`；blockage `:121`） | 0 | tcp:9000 | 19.4 | ②真空确证 | 复现；补登记（G 已证全库唯一在 c1_market，`dossier_G:137`） |

**分箱计数**：① 假空壳翻案 **1 张**（`suspend`）｜② 真空确证 **13 张**｜③ 读失败 **0 张**（CH 经 tcp:9000 全程可达）。

**三套旧数的量纲裁决（本包 strict 唯一口径）**：骨架"10 张"＝病灶 B 的**扩面子集**（14 张全集减去已知 4 张）；
blockage"9 张"＝**文字张数与其点名 8 张不符**（`dossier_G:313` N9 已记）；G 窗口"12 张点名 11 空"＝只覆盖 12 张子集。
⇒ 并集 14 张中 strict 确证 **13 张真空**，三套旧数都是子集口径、非同一分母，本包不作"谁错"判，只立"13/14 现值"唯一口径。

**关键翻案点回话（A1）**：fail-silent 污染风险**在机制上真实存在**（V2/V9 契约可证），但**在本表集合上未发生**——
13 张真空全部被 strict 复现，无一张从"读失败"被洗成"真空"。W-34 的病不是假空壳，而是**张数分母三套并存 + `suspend` 旧快照过期**。

## 五、known_data_gaps 纯追加与不变量

- 追加前 **63** 条 → 追加后 **74** 条（**+11**）；追加候选＝13 张确证真空，其中 2 张已在册（`edb_data`、`l2_tick`）被跳过。
- 脚本内置断言（`append_gaps()`，`--apply-gaps` 路径必经，违背即 `GapAppendInvariantError` 且不落盘）：
  ①`yaml.safe_load` 前后各解析一次；②既有 id 键集合差 **删除集＝`[]`**；③条目数 `after ≥ before + len(added)`；
  ④**逐条深比对**：每条既有 entry 追加后 dict 完全相等（`mutated_existing＝[]`）；⑤写盘文本零 CRLF（`newline='\n'`）。
- 机生回报原文：`{"before_count": 63, "after_count": 74, "added_ids": [account_nav_daily / etf_benchmark / realtime_snapshot / index_valuation_daily_v2 / ipo_schedule / margin_target_adjustment / market_index_meta / msci_adjustment / reconciliation_differences / stock_candidate_pool / stock_valuation]_strict_recheck_empty, "skipped_already_registered": ["c1_market.edb_data", "c1_market.l2_tick"], "deletion_set": [], "mutated_existing": []}`
- 幂等复跑证据（同命令二次执行）：`{"before_count": 74, "after_count": 74, "added_ids": [], "skipped_already_registered": [13 张确证真空表全列], "deletion_set": [], "mutated_existing": []}`
  ⇒ 追加通道按 `table` 与 `id` 双查重，重复跑不产生第二条同表 gap，也不改动任何既有条目。
- 插入点＝gaps 列表尾、文件顶层键 `last_updated:` 之前（`_gap_list_tail_offset()`），既有字节零改动；新条目字段顺序照
  `known_data_gaps.yaml:74-90` 范式（`id/table/gap_type/start_date/end_date/date_column/detection_threshold/status/root_cause/impact/evidence/resolution_plan/created/last_updated`），`status: open`（**未裁**：建腿 vs 退役仍是待处置，本包不代 Owner 裁定、不自赋裁定号）。
- `date_column` 非手写：由 `system.columns` 带库限现读（如 `ipo_schedule→ipo_date`、`market_index_meta→valid_from`、
  `realtime_snapshot→snapshot_time`、`msci_adjustment→announcement_date`），无日期列者取 `""`（照 `:808-812` 先例）。
- 归属澄清：本包追加前，该文件在本车道 index 已有**兄弟会话遗留**的暂存改动（`git diff --cached --stat` ＝5 insertions/4 deletions，
  不含任何 `id:`/`status:` 行）；与 HEAD 深比对出的 2 条差异（`dividend_plan_miniqmt_retired`、`tick_data_2026_0917_gap`）
  **全部早于本包写入**（本包首次尝试因路径 bug 在 read_text 处即失败，未写盘）。本包净贡献＝纯追加 11 条。
- 条目 `created/last_updated` 值＝`2026-09-26` 系 **UTC 日期**（`datetime.now(timezone.utc)`，本地 09-27）；证据串内已带 `ts_utc` 原值，勿按本地日期判漂移。

## 六、遗留义务（本包写面受限，未做但须交接）

1. CREATE-GUARD `creation_token` 登记、`add_module_translation.py` 大白话简介登记、`apply_depgraph.py --add-design-node`
   ——三者写面均在 `docs/01_policies_and_standards/**`／注册表内，本包被限定"只准写三处"，故**未执行**，随波 3 落地袋补。
2. `suspend` 从 W-34 空壳清单剔除、13 张现值回填 `business_pipeline_skeleton.md`（该件非本案卷，本包未改）。
3. 复测器目前**零消费者**（一次性普查件，由本案卷引用）；若要长期化，须并入 `scripts/governance/data_supply/` 家族并补测试。
4. 本包临时机读产物落 `docs/_working/total_command_closeout/wave3/empty_tables_recheck.{tsv,json}`（声明为产物非交付册）；
   首次运行的两个错路径产物已 `mv` 至 `.runtime/tmp/w3recheck/mispath_first_run.{tsv,json}`（未删除任何文件）。

## 七、硬禁自证（本包零违例）

未跑 git add/commit/enqueue；未改 `docs/01_policies_and_standards/**`；未动阈值/断言/skip/xfail 与
`search_space_prereg.yaml`/`exam_scale_cost_gate.yaml`/`flags.yaml`；对 CH **只读**（语句仅 `SELECT`，走 `query_strict` 只读白名单）；
未重启 VM、未动 CH 数据/元数据文件、未 kill 进程、未删除文件；未跑 `test_ops_guard_red_team.py`；未写 `data/` 生产目录；
CH 连接参数经 `config/.env.clickhouse`（主区真源）以环境变量注入，未在案卷/代码落任何凭据值（本机仅打印 host:port 用于可达性说明）。

> 复算器本体的落地状态（09-27 06:0x）：`scripts/governance/wave3/recheck_empty_tables.py` **今晚不入库**——TABLE-NAME-REGISTRY 拦它 14 处硬编码候选表名（该门的处方＝走 `TableRegistry.table(category_id)` 真源）。
> 本班不伪造合规（不把表名换成看似 registry 的字符串常量应付门），处方留给接管者：把候选清单从 `src/zephyr/data/config/known_data_gaps.yaml` 读入（那已是这些表的空壳状态真源，符合内收），表名一律经 `TableRegistry`；改完与本册同袋重投。读数本身不受影响：本册 14 件三态与 1 件翻案为实测，复跑命令在件头 usage 内。
