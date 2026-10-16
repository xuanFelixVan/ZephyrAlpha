---
ttl: task_bound
---
# SDSC-04 ClickHouse 写入通道（两条二级降级）

> 挖矿工程：全链路图12 数据供给链 S2 入库段 1/3｜真源=config/data_supply_chain_map.yaml#DSC-04｜挖矿时点=2026-10-15
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：ClickHouse 写入通道（两条二级降级），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。
- 职责一句话：读/DDL 链 TCP(9000)→HTTP(8123)、批量写链 HTTP(8123)→本地 TSV 落盘——批量写从不过 TCP；写失败经 save_fallback 落 data/local_fallback/ 并由回灌器补写。骨架"三级降级"是两条链串成一条的记忆残留（图已正名）。
- 决策问句（图原文）：写不进去时数据落在哪里、什么时候回灌、回灌排空过没有？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 三条 data_flow 入边（DSC-01/02/03）+一条 control 回灌边（DSC-FB replay_batch）；全仓写路径唯一正门=DatabaseService（禁裸 duckdb/裸 CH 连接） | config/data_supply_chain_map.yaml edges；AGENTS.md §7 DatabaseService 行；src/zephyr/infrastructure/database_service.py |
| 输出面 | 40 表全集经其写通道（pass-through）；本批复跑 kline_daily FINAL max=2026-10-15=写通道产出见证；降级产物=data/local_fallback/<table>/ TSV+_manifest.jsonl（回灌成功即 unlink） | config/data_supply_chain_map.yaml#DSC-04 store_refs；本批 ls data/local_fallback/（现仅 _quarantine_20261001..1014 隔离区=回灌尝试留痕，无未排空 TSV 顶层面） |
| SSOT 真源 | 写通道行为真源=ch_writer.py 模块契约（三态 WriteDisposition 禁把本地持久化伪装成 CH 已提交）；图 DSC-04 节点块 | src/zephyr/data/ch_writer.py；config/data_supply_chain_map.yaml#DSC-04 note_zh |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/ch_writer.py；四执行体 ch_writer/local_replay/quality_gate/cleaning_rule_engine 全实存 | src/zephyr/data/ch_writer.py；src/zephyr/data/local_replay.py；src/zephyr/data/quality_gate.py；src/zephyr/data/cleaning_rule_engine.py（本批 ls） |
| 门禁约束 | 静默失败即假绿（冷却期内直接返回空串=调用方须自行降级）；RULE-SECRETS（连接配置走 secrets）；RULE-DATA-OPS 约束其后的破坏性操作 | config/data_supply_chain_map.yaml#DSC-04 fallback residual；AGENTS.md §1 RULE-SECRETS/RULE-DATA-OPS |
| 自动化触发 | wired_import（随采集进程，无独立档期）；回灌守护线程=_start_local_replay（scheduler.py:1128-1165，启动即检+30min 周期+超阈值追平 replay_catchup）；quarantine 隔离区 10-01~10-14 连日生成=回灌在动 | src/zephyr/data/scheduler.py:1128-1165（图 FB 节点 evidence 同锚）；data/local_fallback/_quarantine_*/（本批 ls 8+ 日目录） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 三采集边+回灌边在册；采集三段今日全在产（S1 三本子文档交叉证） |
| 输出面 | pass | 主表今日新鲜（FINAL 直查）；fallback 袋顶层面无未排空 TSV；quarantine 连日=降级路径活着且有毒丸隔离 |
| SSOT 真源 | pass | 写契约三态明文+图节点一致；"三级降级"记忆残留已在图正名 |
| 代码模块 | pass | 四执行体实存 |
| 门禁约束 | warn | 两条 residual 在册未消：TCP→HTTP 冷却期空串契约（调用方自行降级）、local_fallback 路径曾 3h 零日志（现 500 次限频告警）——均有缓解但非根治 |
| 自动化触发 | warn | 写随采集在跑；但回灌排空测量腿未接（DSC-GAP-REPLAY：samples 落点 worktree 不可见、排空与否无读据）——触发面"真的排干净了"不可机械证明 |

## 4. 缺口与建议

1. 【warn 持续→P1 建议】回灌排空测量腿（DSC-GAP-REPLAY，挂 DSC-04/05/FB 三边）：建议给 replay_batch 成功排空写一行 manifest 消账记录（file+ts+rows），让"排空过没有"从目录侧可读——这是 S2 段最值钱的一根测量腿。
2. 【warn 观察】quarantine 隔离区只进不出（10-01 起连日目录）：建议加"隔离区 TTL 复审"读数（毒丸文件是否已被上游修复版替代），防隔离区变成第二积压袋。
3. 【正向证据】dynamic_local_replay unregistered_running 的登记侧滞后仍在册（resource_profile_registry planned/dynamic），但守护线程实跑+隔离区连日留痕已构成"在岗"旁证链。
