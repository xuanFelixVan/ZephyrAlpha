---
ttl: task_bound
title: 终局分诊矿道 M4 工作单——数据库数据/回测考试/全流通策略工厂 57 卡六态判定与处方
session: st-finaldel-m4-20260929
---

# 分诊矿道 M4 工作单（2026-09-29）

> 审计基线：任务卡清单=`C:\Users\fanzi\Desktop\未完成任务施工清单_2026-09-29.md`（审计窗 03:30）。
> 本工单全部判定以 **HEAD（31c38c5205 起，多袋在飞落地后自动前移）+ 实时只读探针** 为准；工作树 470 处修改=多会话在飞，不作判据。
> 六态=READY / DONE_BY_SIBLING / SUPERSEDED / CONFLICT_INFLIGHT(defer) / OWNER_GATE / BLOCKED。

## 〇、CH 存活探测（本工单实测，全部只读）

| 探针 | 结果 | 结论 |
|---|---|---|
| `ch_reader.count('c1_market.sector_constituent')` | **95124 行，ok** | **CH 存活**（2026-09-29 实时） |
| `c1_market.edb_data` | 0 行 | 维持（iFind 配额退役，替代源 macro_data 在案） |
| `c1_market.etf_benchmark` | **2370 行** | **已恢复**（审计窗时为 0；zc9-lane-d 域成果已现身） |
| `c1_market.account_nav_daily` | 1 行 | 近空维持（known_data_gaps `account_nav_daily_writer_zero_caller` 已登记） |
| `kline_sector_intraday max(trade_date)` | **2026-09-29 10:04(+08)** | 板块分钟 K **已恢复且新鲜** |
| `technical_indicator max(trade_date)` | **2026-09-29** | tilib 供数新鲜（晨检生效） |
| 历史证据 | `.runtime/tmp/ch_probe/ch_probe_20260928T204411Z.jsonl`：`ch_reader.count_strict(strict)` outcome=ok | **W-180 strict 通道 09-28 已实弹跑通** |

**CH 实弹批四件逐项判定**（C45 族）：

| 件 | 判定 | 说明 |
|---|---|---|
| etf_benchmark stub 重写#19 | 数据腿已被在途域复活（表 2370 行）；stub 代码件在 `src/zephyr/data/config/tasks.yaml`+`akshare_provider.py` | 余=代码复核可做；EC3 台账 L105 明示"换源域归 zc9-lane-d 在途，禁开腿禁代修"→**defer 归属域** |
| realtime 换腾讯源#20 | 纯代码件可做（src/zephyr/data 换源逻辑）；实弹切换=Owner | **OWNER_GATE（实弹）** |
| intake_ledger_recon rebuild | `scripts/backtest/intake_ledger_recon.py` 已在 HEAD；rebuild=执行面写回执 | **OWNER_GATE（实弹）**，DATA-OPS 三步验证材料可先登记 |
| apply_market_tables_ddl --apply | 脚本已在 HEAD；`--apply`=DDL 生产变更 | **OWNER_GATE（DDL 四类门位）**；DDL 文件审查/对齐可做 |

## 一、数据库数据（❌11 + 🔶7）

| 卡 | 态 | HEAD 复验证据 | 处方 |
|---|---|---|---|
| C11 blob 归档 | BLOCKED | blob_gc.py 在 HEAD；blobs 面持续涨（审计 23217 块） | 时序前置=C02 死信终局处置先行（防归档袋不可 from-bag 取回）；`blob_gc.py` 先 dry-run 复核孤儿面；`--archive`=破坏性数据操作走 RULE-DATA-OPS 三步验证，不实弹 |
| C51 板块分钟 K 断供 | **DONE_BY_SIBLING** | 本工单实时探针：max(trade_date)=**2026-09-29 10:04**，供数已恢复且新鲜 | 台账回填：ec3_water_health_ledger 补"09-29 复测已恢复"一行（新读数以本表为准） |
| C53 空表三件 | **SUPERSEDED**（前提已变） | fresh 读数：etb→实为 `edb_data`=0（在案）；`etf_benchmark`=**2370 行已恢复**；`account_nav_daily`=1 行（known_data_gaps 已登记） | 复核面已完成（台账 §④ 复测+本工单 fresh 读数）；余腿=account_nav_daily 接线/edb 替代源=数据道+Owner，不再按"三件全空"施工 |
| C122 股权穿透数据面 | READY（重） | ec1 台账 §5.3/L117-118 在 HEAD：node_company/node_person v1 空表待 B/C/D 层 uscc 富化；济川控股双实体 | 按 ledger §5.3 消歧桥+变体合并施工；涉数据管线写=RULE-DATA-OPS 三步验证材料先行；富化源到位前禁空跑 |
| C125 压缩收益工单更正 | **DONE_BY_SIBLING（本车道）** | HEAD L108 原"140～150GiB 属现实区间"已核实仍旧 | 已施工：更正为终局自纠实测 **≈5.5GiB**（留 L61975 出处）；袋 q-20260929-st-finaldel-m4-20260929-0002 |
| C134 W-180 CH 严格读接口族 | **READY** | HEAD ch_reader.py 仅 query/count/query_table（fail-silent 旧契约实证）；**字节已定位**：①`.aidrafts/st-final-build-20260926/src/zephyr/data/ch_reader.py`（含 count_strict）②死袋捞回件 `.runtime/tmp/qcloseout_20260928/salvage/q-20260927-st-final-build-20260926-0012/756e41f3…`（同族严格读通道卷）③实弹证据=ch_probe jsonl（09-28 count_strict ok） | 转正处方：lane 版 vs HEAD diff→补单测（strict 抛错契约）→正门/队列落库；180.3 空壳表 strict 复测已在 HEAD（wave3/empty_tables_recheck.md），码落库后全套转绿 |
| C156 QMine 登记册数据卫生 | READY（分两段） | workbook 在 HEAD | 先开消费方审计专包（docs，AI 可做）；字段改名 486 条+ruling 枚举立法的数据合法化=RULE-DATA-OPS 批量面，另批 |
| C241 G-E.1 分钟 K 持久化设计 | READY | ext_01 方案在 HEAD | 出设计文档（token 先行）；DDL 只呈批=OWNER_GATE 分离呈报 |
| C242 G-E.2 不落库采样 | BLOCKED | — | 随 G-C 主体后排产 |
| C378 F123 schema 迁移立册 | READY | 13_f123 卷在 HEAD；`migration_registry.yaml`（REG-MIGRATION-001）已在 HEAD | 新立 db schema 迁移登记册（四字段+33 件 apply_*_ddl.py 纳入+净零声明）；token 先行；与 C379（13 条 pending 退役=Owner）分轨 |
| C467 镜像帽上界 | CONFLICT_INFLIGHT | `Get-MirrorPurgeCap` 在 HEAD backup.ps1:204；**该文件 MM=他会话在飞** | defer 等在飞袋落地后重验 `git status scripts/backup/backup.ps1` 再做（>5000 判帽不可用→additive+WARN，带红样） |
| C116 W-178 板块宇宙 | OWNER_GATE | w178_sector_universe_strict.md 在 HEAD：729=601(880 段)+128(881 段)；concept_board 375 与 sector_constituent 467 零重合；strict 复测 DONE（gap 262→134） | 真源裁定呈 Owner（880 段主轴口径落册）；gap134 补齐=生产表写=Owner 批后数据道执行 |
| C182 EC3-tilib 晨检 | **DONE_BY_SIBLING** | 本工单探针：technical_indicator max=2026-09-29 | 晨检首跑效果已验证（供数新鲜）；台账补一行读数即可 |
| C305 T4 假绿灯交叉尺 | READY | archiver.py:330 实证 fail-open 仍在：`if not ch_rows: log.warning(...); return True` | 修空样本 fail-open（改 False/跳过判据）+rows_written vs 目标表行数交叉尺；与 C57 同族（verify_partition 优先）；`scripts/ch/archiver.py` 单文件 |
| C324 L4 三把尺 | OWNER_GATE | EV-02~06 施工令未签（C78：裁定册 0 命中判未批） | 等 Owner 签发施工令后随 EV 族施工 |
| C344 DU-11 部分写入 | OWNER_GATE（余量） | known_data_gaps.yaml 在 HEAD；治本件在 `.worktrees/st-zmaster2-20260926` | 治本码件移植=READY 子项（车道→主区 diff 后队列）；补 4 日期 8225 票·日=数据操作门位（三步验证），不实弹 |
| C439 sector_constituent 滞后 | OWNER_GATE | strict 卷在 HEAD（880 段 467 vs 601） | 补 134=生产表写（Owner）；降级观察轴+两套口径真源=Owner 裁定 |
| C530 EC3 六项移交核查 | BLOCKED（余量） | 六项终态已在 HEAD（①绿②红③红④三0⑤黄⑥绿） | 剩余两项数据源修复（I7-28/I7-29）=数据道带宽，非本车道 |

## 二、回测考试（❌10 + 🔶9）

| 卡 | 态 | HEAD 复验证据 | 处方 |
|---|---|---|---|
| C33 139 新题首考 | READY（重算） | exam_loop 全 10 文件在 HEAD（writeback/reexam_scheduler/exam_plan 等） | exam_loop 出首批 139 题结论；禁放宽判据；writeback.py 唯一回填口；长算任务挂低峰窗 |
| C34 旧 283 复考 | READY（重算） | 同上基建在 HEAD | 批量复考 insufficient/fail 集；结果一律 writeback 回填；与 C33 同袋排产 |
| C57 红五簇 priority 撞号 | READY | **病灶原样实证**：HEAD 五 GateSpec——REFERENCE-INTEGRITY=70 / GATE-VOCAB=80 / PERM-TRIGGER=82 / COMPLEXITY-GUARD=92 / DEPGRAPH-ENFORCEMENT=113；archiver.py:330 空样本假绿同在 | 重编号 5 个 gate .py（撞号对方=registry 面）+verify_partition 空样本改严；**涉 gate_registry 热册→专用道施工**（热册 defer）；与 C35 同袋 |
| C216 16 例测试红 | BLOCKED | tests/backtest **无** reexam*/closed_book* 测试件在 HEAD——前提过时 | 归属=reexam_strategy_lane（C77 接管）：先落 harness+test+prereg 三件，再修 haircut_sharpe_harvey_liu 源码/T0_BATCH_KIND/mock |
| C236 G-C.4 lead-lag | BLOCKED | — | 观察轨 P2，随 G-C 主体后排产 |
| C237 G-D.1 resonance prereg | CONFLICT_INFLIGHT | `config/search_space_prereg.yaml` **MM=他会话在飞**（同族配置面） | defer 等在飞袋落地；新建 chart_resonance_prereg.yaml（token 三件套）+冻结后 diff==0 |
| C238 G-D.2 逐格统计引擎 | READY（大） | regime_validation/exam_cost_gate.py 在 HEAD 为邻接基座 | 按 ext_01 G-D.2 规格新建（vectorbt 逐格 stats 同构口径；样本/夏普/c*/DSR 四件套） |
| C239 G-D.3 多重检验 | READY（大） | 17 册判据面在 HEAD | 随 G-D.2 同批立 StepM/SPA+分半窗+滚动重考（事件触发）；判据真源指针已由本车道落 17 册 §十一 |
| C288 C2 晋级率 | BLOCKED | — | 2027-03 死线排产，不紧急 |
| C452 wave2.4 三号文 | READY | 盘面+HEAD 均无 quant_methodology 07/08/12 | 从死信袋/车道反查 blob 捞回重投（blob 内容寻址袋=22 件消失案同法）；与 C02 死信新规分批兼容 |
| C107 F57 Fill 写者 | READY（大） | HEAD grep 无 fill_writer/FillFact 生产写者；wiring_A_fill_writer.md 在 HEAD | 按案件册接通单一写者（半场收口）；写面=生产链，红蓝先行 |
| C118 GPU L2 | READY（大） | gpu_rewrite 目录在 HEAD；L1 向量化已落 | L2 批量 GPU 立项排产（波 12 前置 W-173）；L3 条件触发挂起 |
| C132 红蓝两轮连零 | **READY**（CH 已复活） | 本工单探针实证 CH alive；前次归因=CH 停机 | 补跑回归轮 2（governance/trading 两目录）；91_progress 记两轮连零（裁定#416 口径） |
| C199 文件群7 五件 | **DONE_BY_SIBLING（主料）** | `scripts/backtest/hypothesis_precheck.py`+`hypothesis_translator.py` 已在 HEAD | 余量=dead 袋 blobs 清单反查缺件收尾（预计零星）；按袋对账一次即闭环 |
| C205 做T 271 批 | BLOCKED | log 尾实证停跑：batch **52/271**，elapsed 30379s | 查停跑根因（reaper/进程/日志）→断点续跑或重排窗口；长算+带宽任务 |
| C215 du881 案卷 | **DONE_BY_SIBLING** | 本车道复核期间 st-nightsweep 落地 **2d34f7b2dc**（[E21 du881 落库] 案卷两件数据证据+casefile 引用修正），merge-base 实证已在 HEAD 祖先；此前 staged 删除态已被该干净重投取代 | 无余量；早期 staged 删除痕迹=同案在飞过程态，勿再处置 |
| C233 G-C.1 跨周期数据层 | READY（大） | chart_condition_package.py 在 HEAD | merge_asof backward PIT 实现+14 处前视注入位逐个接红证尺 |
| C250 17 册判据回填 | **DONE_BY_SIBLING（指针选项，本车道）** | 17 册原无 G-D 判据节 | 已施工：新增 §十一 判据真源指针=10_wave_plan 10.G-D 行；引擎落地后余量=回填判据表 |
| C251 dossier academic 采纳 | BLOCKED | — | 随 G-D 施工同批（DSR 有效试验数+滚动重考）落 |

## 三、全流通策略工厂（❌13 + 🔶7）

| 卡 | 态 | HEAD 复验证据 | 处方 |
|---|---|---|---|
| C43 M1 封矿第一批 | READY（大） | 00_workorders/91_progress 在 HEAD；案卷无执行 | F125/F127/F128/F130 逐环"接线或退役"二选一；退役环=Owner 门；先 F125 lineage 接线 |
| C46 二期战役序列 | READY（大，整体未开工） | **代码面 0 开工实证**：saga/九态/cleaning_engine 全仓 HEAD grep 空；00_workorders §四列全（F42/F43/F45/F46-F47/F53/F02/F04/F115/F74/F73/F75/F92/F30/F05-F06） | 按排序逐项施工：F53 Saga 编排+九态桥起步；F04 残项守裁 3 冻结口径；F05-F06 空壳表登记前置=known_data_gaps 补登可先行 |
| C75 CNS-01~14 接线 | READY（大） | CNS_wiring_accounting 在 HEAD 实证：L3 生产可达=**0**、净减少=**0**；MAC-001~016 仍全 candidate | 按 CNS-01 起步（≥20 指标接入 indicator_reader 消费链）+三链转绿（一次成功快照+面板非空+IC 证据） |
| C123 前端中译两分支 | **DONE_BY_SIBLING（本车道）** | HEAD chainmap-cluster.js:615 仅 official/verified 两分支实证 | 已施工：补 akshare_top10/ig_equity_edge 两分支（标签口径=ec1 台账 §2/§5.4）；node --check 过；袋 q-…-0001 |
| C230 G-B.1 趋势线升级 | READY（大） | trendline 基座族在 HEAD（signal_ashare） | 按 ext_01 G-B.1（多触点+通道+衰减；RANSAC 弃用，trendln/pytrendline 口径） |
| C231 G-B.2 形态库 | READY（大） | unified_pattern_engine 目标位在 HEAD 族内 | ~15 形态族：每族枢轴序列+几何容差+落库+最少触发数统计 |
| C232 G-B.3 A股事件轴 | READY（大） | `src/zephyr/signal_ashare/limit_up/` 7 件在 HEAD=基座 | 封板/炸板/busted/缠论显式化；Jiang & Li 2026 证据可引 |
| C234 G-C.2 摆动结构 | READY（大） | chanlun_structure.py 在 HEAD | LH/HL 双峰检测复用 chanlun 分型（禁造第二套极值算法） |
| C235 G-C.3 共振定义器 | BLOCKED | — | 依赖 F17，随后按 ext_01 G-C.3 施工 |
| C252 dossier github 采纳 | READY（轻） | dossier_github_ecosystem.md 在 HEAD §八 | 随 F13/F21 施工引 §五/§四 选型（merge_asof/vectorbt/不引 pandas-ta）；纯登记可先行 |
| C380 B-9 骨架勘误 | **DONE_BY_SIBLING（本车道）** | HEAD B-9 行"新增"与 REG-MIGRATION-001 册面（已在 HEAD，13 条 pending）相反实证 | 已施工：B-9 行补勘误注；袋 q-…-0002 |
| C383 F123-F132 四态缺口 | READY（轻） | 11_f129_ml_train_line.md 在 HEAD | 把 F124/F129/F131/F126 缺口清单并入二期排程（F129 PROD 覆盖面/F126 与 F125 对账同尺两侧读） |
| C400 接线普查清单落地 | BLOCKED | `wiring_gap_inventory_20260927.md` **HEAD/盘面/queue pending/stash_notice 四处皆无** | 字节需先从 blob/死信捞回（与 C40 袋同源对账）；捞回即转 READY |
| C74 G-A.3 条件胞 | READY（大） | chart_condition_package/consumer+chart_pattern_registry 在 HEAD；G-A.2 已落 | 条件胞物化+条件轴挂载证据（每信号独立条件格，按预注册卡） |
| C106 缺口定档 122→132 | READY（大） | 96_final_report_wave2 在 HEAD | W6-M 判据收紧收尾+44 无簿环节逐格认领/开簿 |
| C191 P2 缺口立卡 | BLOCKED | — | 排产台账续排（INDEX 三态表序） |
| C227 G-A.1 盘点表重出 | READY | wave10 audit 卷在 HEAD | 按 154 件实测口径重出逐件输出契约（禁再引 62）；盘点生成器随码袋落 HEAD |
| C253 dossier institution 采纳 | BLOCKED | — | 随 G-B.2/G-D 施工同批（接线优先/TradingView 枢轴口径/镜像测试三纪律） |
| C357 integ4 余项 | READY（分项） | LEDGER_three_piece 在 HEAD | 勿重启整池：wiring generator/DU-11 治本/成本对照/L04-L09 接线按各自条目处方逐项落 |
| C376 F26 E7 前哨 | READY（混合） | **paper_outpost.py 不在 HEAD**（git grep 仅 docs/注册表命中——册有码无，虚登记嫌疑） | 先核 capability 册路径与码位（落码时对齐），补事件接线（schedule/事件 kind 点名）+首跑留台账；首跑=运行面另窗 |

## 四、自开工成果（4 张，全部入队）

| 卡 | 文件 | 袋号 | 验证 |
|---|---|---|---|
| C123 | `src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-cluster.js` | q-20260929-st-finaldel-m4-20260929-0001 | node --check 过 |
| C125 | `docs/_working/disk_reorg_campaign/a6_remaining_work_order.md` | q-20260929-st-finaldel-m4-20260929-0002 | 纯文档 |
| C380 | `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md` | q-…-0002 | 纯文档 |
| C250 | `docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` | q-…-0002 | 纯文档（指针选项） |

流程留痕：会话注册 `session_worktree_start(allow_workspace_drift=True)`（主区 338 件多会话在飞，直连提交被他会话 staged 外来件 MUTABLE-CONST 阻断一次，按宪法 §2.6 改道 `--enqueue` 队列=结构性免疫连坐）；4 目标文件改前均 `lock_files.py acquire`。
**本工单文件自身**：因他会话 staged 的 capability_canonical_file_registry.yaml 为陈旧快照（相对 HEAD 缺 7 条），batch_creation_tokens.py 写前自检 fail-safe 拒写（防跨会话静默删条目）→ token 登记与本文件提交 **defer**；正解=该注册表基底按手册 §4 增量补 7 条后重跑 batch 工具（归属=staged 该册的在途会话/维护班，禁本道代修）。

## 五、OWNER_GATE 登记（呈报，不执行）

1. **CH 实弹批**（C45 族）：realtime 换源#20 实弹切换、intake_ledger_recon rebuild 执行、`apply_market_tables_ddl --apply`——工程面已备、**CH 现已存活**，等 Owner 批+DATA-OPS 三步验证材料；etf_benchmark#19 数据腿已复活（2370 行），余代码复核归 zc9-lane-d 域。
2. **W-178 板块宇宙真源裁定+gap134 补齐**（C116/C439）：strict 复测已 DONE（HEAD 卷面 601/128/375 零重合事实在案），真源落册与补 134 生产表写=Owner。
3. **T1 定稿**（C69 前置核验）：handover_verdict 已于 09-29 04:20 重生成且 manifest=3700/dead=0 全 pass（计数前置已被消化）；93 册"2 阴格同窗旧引擎对拍"证据件仍缺（半天级机械真跑可做=READY-heavy）；**定稿拍板=Owner**。
4. **C344 补 4 日期**（8225 票·日）与 **C120 空壳表逐表选型**：数据操作门位。
5. **C324/C78 EV-02~06 施工令**：等 Owner 签发。
6. C43 退役环 / C378 邻接 C379（REG-MIGRATION-001 13 条 pending 净删）——注册表净删面。

## 六、尾部统计

六态判定（57 卡 = 数据库 18 + 回测 19 + 工厂 20）：

| 态 | 数据库 | 回测 | 工厂 | 小计 |
|---|---|---|---|---|
| READY | 6（C122/C134/C156/C241/C378/C305） | 10（C33/C34/C57/C238/C239/C452/C107/C118/C132/C233） | 14（C43/C46/C75/C230/C231/C232/C234/C252/C383/C74/C106/C227/C357/C376） | **30** |
| DONE_BY_SIBLING | 3（C51/C182=本道实时探针核销；C125=本道施工） | 3（C199=他道吸收主料；C250=本道施工指针选项；C215=st-nightsweep 2d34f7b2dc 落地） | 2（C123/C380=本道施工） | **8**（本车道施工/核销 6 + 他道吸收 2） |
| SUPERSEDED | 1（C53，前提"三件全空"已变） | 0 | 0 | **1** |
| CONFLICT_INFLIGHT | 1（C467，backup.ps1 MM 在飞） | 1（C237 search_space_prereg MM 在飞） | 0 | **2** |
| OWNER_GATE | 4（C116/C324/C344/C439） | 0 | 0 | **4** |
| BLOCKED | 3（C11/C242/C530） | 5（C216/C236/C288/C205/C251） | 4（C235/C400/C191/C253） | **12** |

合计核对：30+8+1+2+4+12 = **57 卡全量覆盖，无遗漏**。

READY 分列：
- **纯代码/文档可做**（无需实弹）：C134（字节已定位转正）、C378、C156（审计段）、C241、C57（涉热册专用道）、C305、C452、C238、C239、C107、C118、C233、C43、C46、C75、C230/C231/C232/C234、C252、C383、C74、C106、C227、C357、C376、C132（CH 已复活，复跑即做）。
- **需实弹/数据面待验证**（材料可备、执行=门位）：CH 实弹批四件、C122（富化源）、C344 补数、C439 补 134、C116 真源落册、T1 同窗对拍（半天真跑）。

---
*生成：st-finaldel-m4-20260929，2026-09-29。复核命令全部可复跑（本文表内读数=实时探针原值）；队列袋可用 `python scripts/commit_queue.py status --session st-finaldel-m4-20260929` 追踪。*
