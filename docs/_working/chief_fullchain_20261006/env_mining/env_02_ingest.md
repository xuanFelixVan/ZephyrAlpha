---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_02_ingest.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-02 入库 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/data_supply_chain_map.yaml segments[S2_ingest]；血肉卷=docs/_working/map_build/fig12_datachain/02_入库单通道与幂等判重.md
- **职责一句话**：CH 两条二级降级写通道 + 实时 WAL + 幂等判重（共用 local_fallback 汇聚）
- **节点清单（6）**：DSC-04 写入通道两条二级降级(built)｜DSC-05 实时 WAL 落盘排空(built)｜DSC-FB local_fallback 汇聚(built)｜DSC-06 幂等写与判重(partial)｜DSC-GAP-DUPGUARD 判重器聚合对照腿(pending)｜DSC-GAP-REPLAY 回灌排空不可证(pending)
- **状态分布**：built=3 / partial=1 / pending=2（与 counts.segment_S2_ingest=6 合）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 全网/外部 | 判定 |
|---|---|---|---|
| ①上游 | 边：DSC-01/02/03→DSC-04（normalized rows→写通道）、DSC-02→DSC-05（tick 段落 WAL）、DSC-04/05→DSC-FB 双降级入边。写手真身：src/zephyr/data/ch_writer.py（TCP 冷却 15s :101/:176/:207、HTTP 冷却 15s :233、批量写从不过 TCP）、wal_writer.py（:69-72 容量 2GB/70% warning/90% critical 背压、:163 拒收语义、:283 backlog gauge） | — | signal |
| ②下游 | replay_batch/local_replay 消费方 grep=src/zephyr/data/{ch_writer,wal_writer,scheduler,local_replay}.py 四件（回灌闭环在数据域内自洽）；redundant_source/wal_codec 包级 re-export；图内 consumers=40 表全集 pass-through＋ch_tick_replay/cost_model_calibration（读侧）。local_fallback 在产实证：data/local_fallback/ 存 _quarantine_20261001、_quarantine_20261003 两区及多表 TSV | — | signal |
| ③算法机制 | 降级算法=TCP(9000)→HTTP(8123)→本地 TSV 落盘+manifest（store_refs data/local_fallback/_manifest.jsonl，成功 unlink）；级联自愈=HTTP 连续 5 次 5xx 双单例作废（图 fallback）；幂等=调用方决定（ReplacingMergeTree 直 INSERT / MergeTree 写前 DELETE），判真值须 FINAL；90% 背压=add() 直接拒收非软减速 | ClickHouse 官方+Altinity+ObsessionDB（2026-10 检索）：ReplacingMergeTree 去重是后台合并的 eventual 行为、判真值须 FINAL 或 OPTIMIZE；OPTIMIZE FINAL 定位=维护工具非查询策略、按分区跑控成本——与本仓"读侧 FINAL/归档 FINAL/物理去重三防线"设计互证 | signal |
| ④后端代码 | src/：ch_writer.py、wal_writer.py、buffered_writer.py（攒批写 32 任务同形不同物）、local_replay.py、ch_reader.py（自动注 FINAL）。scripts/：scripts/governance/data_quality/check_tick_duplication.py。tests/：tests/data/data/test_ch_reader_strict.py、tests/data/db/test_clickhouse_conn_unify.py；ch_writer/wal_writer 专项 test 未命中＝测试面偏读侧（登记） | — | signal |
| ⑤前端呈现（只登记不施工） | src/zephyr/frontend/dashboard/api_server.py:2057 有 storage_tiering Tier 对齐注释（冷层迁表登记位，"表名→tier"空 dict）；无 local_fallback/写通道独立面板命中 | — | noise（登记：写侧前端呈现近乎零，与"无位置"判词一致） |
| ⑥数据字段 | **本批最大新证（图 as_of 10-04 之后的推进）**：DSC-GAP-DUPGUARD 的 Code 42 缺陷已修——check_tick_duplication.py:127-129 带 `FIX 2026-10-05` 注记（14 平铺列撞 Nullable 聚合 ≤8 上限→tuple 单参包装，:175 落地），聚合对照腿恢复。但第二缺陷仍在：:47 `_SRC_DIR = r"d:\ZephyrAlpha\src"` 硬编码主区（worktree 判重不同源）未修。判重报告仍 stdout/人工案卷无落库台账（审计缺口维持） | — | signal（gap 半闭合，登记滞后） |

## §2 挖干自评

- **三扫收敛?** 收敛。三轮后新发现仅 DUPGUARD 修复现状一处（属登记滞后非新病灶）；其余与图判词一一互证。
- **未挖长尾清单**：(a) quality_gate.py/cleaning_rule_engine.py 两执行体的规则明细（map 列为 DSC-04 machine 执行体，本批只核存在未核规则覆盖面）；(b) buffered_writer 32 攒批任务的逐任务名单；(c) ch_writer/quality_gate 的 tests 专项缺口的补齐必要性评估。
- **🌑不可得清点**：①回灌是否真排空过（GAP-REPLAY 测量腿未接，samples 落点 .runtime/logs/resource_samples/ 本 worktree 不可见）；②manifest 今日行数（读 F:/ manifest 属 ENV-04 面，此处不重复）。

## §3 挖后自审闸三态裁定

**施工（一项小收尾）＋ 挂起排期（两项）＋ 已建成面封矿**

- **施工**：DUPGUARD 剩余半腿——check_tick_duplication.py:47 硬编码 `d:\ZephyrAlpha\src` 改为脚本相对解析（同 :51-55 _GOV_DIR 的写法），消灭 worktree 判重不同源；并把"已修聚合腿"回写 DSC-GAP-DUPGUARD 档案（改后该 gap 应退役）。终局量尺：判重正门全自动化后删数据准入闸无人审也成立＝有位置。
- **挂起排期①**：GAP-REPLAY 回灌测量腿——解锁条件=resource_profile_registry 的 dynamic 样本落点迁入 worktree 可见面或接 metrics 台账；解锁前禁写"已排空"散文。
- **挂起排期②**：判重报告落库台账（审计缺口）——解锁条件=DUPGUARD 修复验收同批设计存储位（涉新表=DDL Owner 窗口）。
- 封矿理由：DSC-04/05/FB 三节点 production/structure 证据齐、trigger_facts alive，降级+WAL+汇聚一套两用途设计已是终局形态。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：S2 六节点字段+edges 降级边（map:724-2575, 3524-3551） | signal | 两链二级降级/90% 背压/汇聚并置（WB12-26）判词全录 |
| 2 | 代码轮：ch_writer/wal_writer/local_replay/check_tick_duplication 行号级核验 | signal | 15s 双冷却、0.9 阈值、拒收语义在码；**DUPGUARD 聚合腿 2026-10-05 已修（tuple 包装）＋硬编码主区未修**＝本批最值钱发现 |
| 3 | 消费方轮：replay_batch 调用面 + local_fallback 目录 ls + tests 面 | signal | 回灌闭环四文件互调；quarantine 双区实证；测试面偏读侧登记 |
| 4 | 外搜轮：ClickHouse 去重/OPTIMIZE 官方与 Altinity 口径 | signal | FINAL 判真值+OPTIMIZE=维护工具，与本仓三防线互证（DSC-18 定位获得外部支持） |
