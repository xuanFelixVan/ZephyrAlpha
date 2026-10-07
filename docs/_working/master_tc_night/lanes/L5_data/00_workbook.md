---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# L5 数据库车道作业簿（st-mastertc-l5，2026-10-07 夜战）

> 总包：master_tc_night（00_orchestration.md §三硬纪律+§四模板）｜卡：C11 C122 C156 C241 C242 C378 C324 C120 C121 C299
> 冷启动：PATH=Python312 ✓｜lock cleanup ✓（回收死锁 2+worker 遗物 1）｜reaper 存活 ✓（后经 C324 现算化，`source=live` 实测）
> 提交：合并单袋走 `git_commit.py --enqueue --allow-non-worktree --allow-multi-domain`（夜战多车道并发，serialize 窗口实测 ~14 分钟/次；共册 stomP 三次实测在案，幂等复插处方见 C156⑤）

---

## C11 blob 归档（qmine 复核轮）——GREEN

- ①处方：dry-run 复核孤儿面 + `--archive` 前 1 小批（只归档确认零引用块）；报告追加 04_blobs_gc/workbook.md。
- ②现状实证：dry-run（03:43）在盘 23408｜A live 2929/B dead_only 8384/C2 done 921/C1 混 483/D archive_only 3493/**Z 孤儿 5354（1.92GB）**/mixed 1844；候选（Z∧mtime>7d）4408/1.27GB；幻影 0。
- ③上游：blob_gc.py 四态扫描（矿簿 §1⑥ 口径）；L3 死信处置（引用时序）。
- ④下游：qmine 04_blobs_gc/workbook.md §5（已 safe_write CAS 追加）；后续分批 GC。
- ⑤冲突面：L3 车道 concurrent——候选集构造上排除 dead/ 引用（B 类零触碰）+二次重扫+内容寻址自愈，无冲突。
- ⑥残余：~4365 个 7d 候选未动，留 L3 死信清账后分批。
- 自审闸 **GREEN**｜施工：`--archive --grace-days 14` → **moved=43**/14.7MB，竞态跳过 0，dst 已在 0；进程外核实 blobs 23410→23367、blobs_archive/ 43 块+manifest 逐行审计；宽限 14d=收窄出最保守首袋（卡面"前 1 小批"字面满足）。

## C122 uscc 富化消歧桥——GREEN（真跑批 WAIT）

- ①处方：读 EC1 台账 §5.3；最小消歧桥=设计+代码骨架+单测（mock DB）；涉新 DDL=Owner 门只落设计；真数据富化跑批 WAIT。
- ②现状：node_person/node_company v1 空表（A 层 akshare 无 uscc）；设计真源=altdata_line/02 §4.1（公司主键=uscc）+§7（同名合并错误=假边=假信号）。
- ③上游：edge_holding 股东名称面；EC1 chainmap_equity_graph 消费契约。
- ④下游：富化跑批（另批，提案→施写分离）；ChainMap 前端富化展示。
- ⑤冲突面：无（新模块+只读）。
- ⑥残余：人物概率消歧实现（B 层富化批）；提案持久表=新 DDL=Owner 门（骨架 INVARIANTS 明确不触发）。
- 自审闸 **GREEN（骨架）/WAIT（跑批）**｜施工：`src/zephyr/governance/data_governance/entity_graph_uscc_bridge.py`（只读提案器：normalize→uscc 直键 1.0/name_norm 唯一 0.9/ambiguous 附候选/unresolved 四态；人物三证据立法骨架 NotReady）+ `tests/.../test_entity_graph_uscc_bridge.py` **7/7 绿**（mock cursor 零真实 PG）；token+翻译+depgraph(16408442) 齐。

## C156 登记册数据卫生——GREEN（立法批；数据合法化另批）

- ①处方：普查 status 值域；立法=册面枚举+越界值逐一列出；数据合法化只做"纯改名映射表"文档+校验脚本，**不批量改 486 条**。
- ②现状普查（YAML 解析条目级）：status 六值现势=active 284→285/draft 1/superseded 4/**decided 13/void 2**；D11 字段漂移=**486 整**（created×457/domain×7/limit_id×3/final_adjudication×19）——行级 grep 漏嵌套 limit_id 的教训在案（校验器为准）。
- ③上游：qmine 02_registry_hygiene 矿簿 D6/D11。
- ④下游：RULING-REFERENCE gate 增强（另行立项）；改名合法化批（§映射档交接处方）。
- ⑤冲突面：ruling_registry/capability 册/module_translation 册=他会话高频写窗——改前 acquire 全过（ruling 回收 L10 过期 claim）；**capability 册被并发排水 stomP 三次**（22 条 HEAD 缺口反复压盘），处方=幂等 backfill（append-only CAS）+token 幂等复插，三次全量复核 OK。
- ⑥残余：486 条改名=另批（映射档 §4 留四条理由：共册撞写窗/体量大须 RULE-DATA-OPS 三步验证独立批/校验器已就绪/零硬消费无抢跑收益）。
- 自审闸 **GREEN**｜施工：①册头铁律#4 四值→**六值立法**（decided=裁定已成立的时点性变体/void=编号墓碑承载铁律#2）+entry_schema 行同步+越界 15 条（decided 13+#265/#408 void）册面逐一列出，数据零改；②映射档 c156_field_rename_mapping.md（486 条四族+消费方审计+另批处方）；③校验器 `scripts/governance/check_registry_field_legality.py`+单测 **5/5 绿**（exit 0/1/2 契约；立法后越界=0 实测）。

## C241 G-E.1 分钟K持久化设计——GREEN（呈批稿）

- ①处方：按 ext_01 G-E.1 规格出设计文档（DDL 呈批不执行），落 final_review_chartlib/。
- ②现状实证（**前提更正**）：卡面"无 minute 表"系 `LIKE '%minute%'` 测量伪影——库内 `kline_1min/5min/15min/30min/60min` 在册且满覆盖：**kline_1min 14.86 亿行/37.3GB/5858 标的/2021-09→2026-09-30 fresh**（local_intraday 12.98 亿+bdpan 1.89 亿）；年增 ≈3 亿行/7.5GB。
- ③上游：裁定#413④（xtdata=分钟考试唯一指派源）；ext_01 波10 规格。
- ④下游：G-D.1 prereg 分钟周期轴解禁；Owner 呈批清单（TTL 择一+C 路冻结件）。
- ⑤冲突面：无（CH 只读）。
- ⑥残余：B 路写库器模块（另批门位）；G-E.2 实现（WAIT 随 G-C）。
- 自审闸 **GREEN**｜施工：`ext_05_minute_k_persistence_design.md`——A 路（复用 kline_1min，零 DDL，推荐）/B 路（xtdata 增量腿 data_source='xtdata'，ReplacingMergeTree 去重共存，零 DDL）/C 路（新表 kline_stock_minute DDL 呈批稿冻结，触发条件=口径结构性冲突）；TTL 三案呈批（现状分钟族零 TTL）；sector_intraday 分工=板块级 vs 个股级天然不重叠。

## C242 G-E.2 分钟临时替代路径——GREEN（接口草案，实现 WAIT）

- ①处方：随 G-C 主体；本夜只出接口草案小节并入 C241 文档，标 WAIT。
- ②现状：miniQMT 模拟盘在运行（实盘通道已退役）；A 路既有表可直接供数。
- ③上游：G-C.3 共振条件对（消费签名）。
- ④下游：G-C 离线回测采样验证（样本窗 ≤3 个月）。
- ⑤冲突面：无。
- ⑥残余：实现批随 G-C 主体。
- 自审闸 **GREEN（草案）/WAIT（实现）**｜施工：ext_05 §7 `MinuteSampleFeed` 接口草案（load_window 92 天窗断言/assert_readonly 零写自检；输出只落 `.runtime/tmp/`）。

## C378 schema 迁移登记册立项——GREEN（净零销账：册已在，验证补齐）

- ①处方：立新册 schema_migration_registry.yaml（token 先行，四字段），纳入 33 件 apply_*ddl 清单，净零声明入册头。
- ②现状实证：**REG-SCHEMA-MIG-001（schema_migrations.yaml）已于 2026-10-01 由 st-ffchief wave4-G 落地**（F123 P0 新号）——册头自带正名声明（与 migration_registry.yaml 模块迁移册正交）+merge_evaluation 净零声明+34 脚本基线清单+PG tracking 表+runner 三件套；applied_history 实证 batch-20261001T073645Z 已应用。
- ③上游：F123 处方；C379 裁定（migration_registry=模块迁移册）。
- ④下游：今后 DDL 一律走版本化迁移通道。
- ⑤冲突面：无（只读复核）。
- ⑥残余：无（卡面"33 件"实测 34=机械扫描为准，与册内 baseline_script_count=34 一致）。
- 自审闸 **GREEN（净零销账）**｜施工：按册头 algorithm 复算指纹 `sha256:decfa003...26f6` **match=True**（34 文件逐一哈希）；不立新册——立新册=同域重复簇违裁定#375，本卡"纳入清单"义务已被 baseline_manifest 承载。

## C324 reaper status 现算化——GREEN

- ①处方：`_print_status` 读 `_STATUS_FILE` 改现算（保留文件回退），补单测（tmp_path）。
- ②现状：原实现纯读 last_run.json（快照可能停更=护栏瞎掉，reap docstring 2026-09-26 事故在案）。
- ③上游：L4 三把尺（EV-03 supply_conservation 已在；本卡=第二把）。
- ④下游：RULE-GUARDIAN 冷启动日检（输出加 `source=live/scan_mode=live_dryrun` 标注行，向后兼容追加）。
- ⑤冲突面：process_reaper.py 无他会话在途。
- ⑥残余：第三把尺另卡。
- 自审闸 **GREEN**｜施工：`_compute_live_report()`（走 `_reap_cycle(True)` 只读现算，**绕开 reap() finally 的 _write_status**——保护"上次真跑"快照不被 dry-run 覆盖，失败回退文件）；单测 `tests/trading/test_process_reaper_status.py` **5/5 绿**（live/回退/never_run/corrupt/errors 五态）；实弹 `--status` 输出 source=live 实测。

## C120 空壳表选型复核——GREEN（登记面）

- ①处方：6 张已入 known_data_gaps；逐表复核覆盖，缺的补登（登记不删）；裁定面（建腿/退役）已由 #311/#328+D1 批覆盖销账。
- ②现状实证：wave3 empty_tables_recheck（09-26 探针 13 vacuum+1 has_data）逐表对账——12 张在册（6 张 *_empty_table_no_leg+l2_tick/edb_data/account_nav_daily/reconciliation_differences/index_valuation_daily_v2 各有专条），**缺 1 张=realtime_snapshot**（10-07 复测仍 0 行）已补登 `realtime_snapshot_empty_table_no_leg`（gaps 74→75）；观测注记：etf_benchmark 09-26 空→10-07 实测 2,373 行（建腿自愈，无需登记）。
- ③上游：#311/#328 退役条件通道；F06 卷。
- ④下游：Owner 逐表批（建腿/退役）；quality_sentinel。
- ⑤冲突面：known_data_gaps.yaml acquire 后 CAS 写。
- ⑥残余：裁定面=Owner 保留（#311/#328 通道执行另批）。
- 自审闸 **GREEN**｜施工：safe_write CAS 追加一条（克隆 6 张先例 schema，root_cause 注明补登链路）。

## C121 hfq 血缘版本列 DDL——**WAIT-OWNER**（呈批稿，只文档）

- ①处方：Owner 窗未开 → 出 DDL 呈批稿落 workbook。
- ②现状实证（10-07 system.columns 只读）：hfq 族现势 3 张——kline_daily_hfq **有** lineage_version（UInt16 DEFAULT 1）+data_source/ingest_ts；**kline_weekly_hfq/kline_monthly_hfq 无**（引擎均 ReplacingMergeTree，sorting_key=(symbol, trade_date)，**无版本参数**）。X-58：读写侧已在（recalc_hfq.py CANON_LINEAGE_VERSION=100+HAS_LINEAGE_COL 探针），缺的是族级版本列。
- ③上游：wo004 recalc_hfq 落地腿；X-58 改判。
- ④下游：weekly/monthly 重算提升通道（F123 无关）。
- ⑤冲突面：DDL=四类门位，本夜禁执行（总纲 §三.7）。
- ⑥残余：Owner 批窗后执行+回填+验证。
- 自审闸 **WAIT-OWNER**｜呈批稿（随本 workbook 落 HEAD）：

```sql
-- 【DDL 呈批稿 · 不执行 · WAIT-OWNER】C121：hfq 族级血缘版本列补齐（X-58/⚑-5⑤）
-- 动机：weekly/monthly 缺 lineage_version ⇒ recalc_hfq 提升腿的"版本判赢"语义在两表失配，
--       旧口径行（厂商 back/陈旧快照）可静默覆盖裁定口径行（卡面"旧行可静默覆盖"病灶）。
-- 对齐 daily_hfq 既有列型（UInt16 DEFAULT 1；CANON 口径行写入时显式 =100）：
ALTER TABLE c1_market.kline_weekly_hfq  ADD COLUMN IF NOT EXISTS lineage_version UInt16 DEFAULT 1 COMMENT '血缘版本：1=默认厂商口径, 100=裁定口径(recalc_hfq CANON)';
-- noqa: bare-sql 呈批稿只呈批不执行(DDL四类门位 Owner 呈批件)
ALTER TABLE c1_market.kline_monthly_hfq ADD COLUMN IF NOT EXISTS lineage_version UInt16 DEFAULT 1 COMMENT '血缘版本：1=默认厂商口径, 100=裁定口径(recalc_hfq CANON)';
-- noqa: bare-sql 呈批稿只呈批不执行(DDL四类门位 Owner 呈批件)
-- 回滚注记：ALTER TABLE ... DROP COLUMN lineage_version（补列即回滚点；DEFAULT 列零数据迁移，可逆）。
-- noqa: bare-sql 呈批稿只呈批不执行(DDL四类门位 Owner 呈批件)
-- 决策点（Owner 择一，随批呈报）：
--  A. 只补列（本稿）：写侧显式版本判读，FINAL 语义仍按插入序——够 recalc_hfq 现行 SQL（LEFT ANTI JOIN 按 >=100 判）；
--  B. 引擎升 ReplacingMergeTree(lineage_version)：FINAL 版本判赢治本，但属引擎变更（ATOMIC RENAME 重建表，窗内停写）——建议二批。
```

## C299 R5 三处真源收敛——GREEN（方案文档+挂账行更新；配置移交调度域）

- ①处方：按已知分歧（consensus dow=2-6 vs schedule 1-5）出对齐方案+更新 9f32c9011b④ 挂账行，真源=schedule（trades 日历为主）；不改生产配置。
- ②现状实证：三处共用 dual_source_guard 判据（W-36/X-40 在册）；schedule.yaml 槽位 cron dow 语义两代不一致（daily_kline/eod_reconciliation `0-4` vs consensus_crosscheck `1-5`——至少一种在调度器语义下错位）；reconciliation_differences 两库皆空在册（known_data_gaps 双病灶条）。
- ③上游：9f32c9011b④（B15 挂账 +reconciliation_differences）；R-015。
- ④下游：recon_runner/consensus_crosscheck/score 宿主取数窗施工批；调度域移交项。
- ⑤冲突面：known_data_gaps.yaml 本车道已 claim（C120 同册连写，CAS 双写成功）。
- ⑥残余：配置改动（cron 语义统一）→调度域移交（本档 §4）；消费窗改造施工批另落。
- 自审闸 **GREEN**｜施工：`c299_r5_truth_alignment.md`（三步方案：判据走 trade_calendar/班面语义统一/5 交易日无假绿验收）+挂账行更新（resolution_plan 补 C299 入口+last_updated=2026-10-07，CAS）。**裁定理由**：真源=trades 日历——cron dow 是"何时跑"的投影，拿投影当"哪日该有数"的本体=SSOT 倒挂；scheduler.py:196 `weekday()>=5` 桥已在场，收敛=让消费窗走同一桥。

---

## OPEN_QUESTIONS

1. C121 决策点 A/B（只补列 vs 引擎升版本判赢）——Owner 批窗定。
2. schedule.yaml cron dow 语义（0=周日标准 vs 本仓 0=周一实态）需调度域实测裁定——移交在案。
3. capability 册并发 stomP 已三次：建议共册写方统一走"幂等 backfill+复插"处方，或 Owner 门收窄夜战窗并发写者数（登记非裁定）。

## CONFLICT_LEDGER

| 时点 | 冲突 | 处置 |
|---|---|---|
| 04:0x | git_commit 首投 WORKTREE-REQUIRED+CREATE-GUARD（c156 映射档 token 缺） | session_worktree_start(allow_workspace_drift) 注册+token 补登 |
| 04:19/04:33/05:0x | capability 册 22 条 HEAD 缺口反复压盘（并发排水 stomP×3） | 幂等 backfill（append-only CAS）+5 token 复插，全量复核 OK |
| 04:33 | --enqueue 首投被 SESSION-REQUIRED+CREATE-GUARD 拦（bag 未入队） | 前两项修复后改合并单袋重投 |

## DONE_SUMMARY

10 卡：GREEN 8（C11/C122/C156/C241/C242/C378/C324/C120）+ GREEN 含 WAIT 子项 2（C122 跑批/C242 实现）+ WAIT-OWNER 1（C121，并入上计）——卡面全挖干，六向台账齐；测试 17/17 绿（5+7+5）；CH 全程只读；DDL 零执行（呈批稿 2 件：G-E.1 C 路冻结件+C121）；DROP 零；生产配置零改。
