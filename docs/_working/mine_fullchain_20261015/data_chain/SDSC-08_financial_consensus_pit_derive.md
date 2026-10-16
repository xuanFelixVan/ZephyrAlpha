---
ttl: task_bound
---
# SDSC-08 财务 / 一致预期派生（PIT 双守卫）

> 挖矿工程：全链路图12 数据供给链 S3 衍生段 2/4｜真源=config/data_supply_chain_map.yaml#DSC-08｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：财务/一致预期派生（PIT 双守卫），node_type=stage，build_status=partial，verified_scope=structure，行级状态=分面（financial 腿 ✅ / consensus 腿 ✅——两腿 2026-10-07 改判后均 ✅）。
- 职责一句话：两条 internal 腿——financial_derived_build（deps=三大报表）与 consensus_daily_build（deps=研报明细+交易日历）；PIT 铁律在派生侧有第二道守卫（1970 哨兵+publish_date<=trade_date 零 embargo）。预期链曾断（09-25 定账）、已复活（IN1-27① 改判）。
- 决策问句（图原文）：派生层滞后是派生自己的锅，还是上游的锅？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 两条入边：DSC-06（三大报表/研报就绪）+DSC-03（research_report→consensus_daily_build 上游边）；上游 research_report 本批 max=2026-10-14 鲜 | config/data_supply_chain_map.yaml edges DSC-06→08+DSC-03→08；本批 CH 直查 |
| 输出面 | c3_fundamental.financial_derived/consensus_daily→DSC-HA 出图；消费=TDM DS-232+factor/fundamentals.py:24+factor/expectations.py:19+factor_registry 277/12394/12433；本批复跑：consensus_daily max(trade_date)=2026-10-15（与上游严格相等判据持续过）、financial_derived max(announce_date)=2026-09-02（announce 驱动型，三季报季未启动） | config/data_supply_chain_map.yaml#DSC-08 data_refs/consumers；本批 CH 直查 |
| SSOT 真源 | internal 任务真源=tasks.yaml（consensus_daily_build/financial_derived_build）；语义层=图12 DSC-08（含 IN1-27① 改判记录）；PIT 判据=1970 哨兵+publish_date<=trade_date | src/zephyr/data/config/tasks.yaml；config/data_supply_chain_map.yaml#DSC-08 note_zh |
| 代码模块 | module_id=MOD-L04-001，module_ref=src/zephyr/data/implementations/consensus_daily_compute.py；执行体两 compute 核实存；financial_parser.py 为 path_ghost（不在产数路径，图已改挂真身） | src/zephyr/data/implementations/consensus_daily_compute.py；src/zephyr/data/implementations/financial_derived_compute.py（本批 ls） |
| 门禁约束 | PIT 双守卫；RULE-SCHEMA-TZ（DateTime64(3)+显式时区）；两入口幂等条件同为窗口 DELETE+INSERT（dual_entry residual：人工重跑与档期重跑台账不可分） | config/data_supply_chain_map.yaml#DSC-08 fallback；AGENTS.md §1 RULE-SCHEMA-TZ |
| 自动化触发 | wired_cron：两 build 任务按档期派工（deps=advisory）；修复提交 baee3850fde（09-27）后多次 SUCCESS（#197111/#207524/#199983/#205178 台账实读在案） | config/data_supply_chain_map.yaml#DSC-08 facets/trigger_facts（as_of 2026-10-07，alive） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | warn | 上游研报链今日鲜（max=10-14）；但 research_report_detail_incremental 慢性超时残病在册（单跑 4.6~7h+ 撞 6h stale-reap 闸，10-02 仍 STALE，处方 IN1-27 归数据班）——上游一断 consensus 腿即再停 |
| 输出面 | pass | consensus 腿严格相等判据今日仍过（10-15）；financial 腿 max=09-02 属 announce 驱动节奏（10 月中三季报未开闸），非断供证据，判 pass 带注记 |
| SSOT 真源 | pass | 图改判记录（09-25 定账→10-07 复活）双段留档；tasks.yaml 任务在册 |
| 代码模块 | pass | 两 compute 核实存；path_ghost（financial_parser）已在图修正 |
| 门禁约束 | pass | PIT 双守卫+时区铁律在册；dual_entry residual 已知并有台账面缓解（task_runs 可查 SUCCESS） |
| 自动化触发 | warn | build 任务节拍闭合（期望 7/观测 2，国庆窗折算）；上游慢性超时=触发链最脆弱一环未治 |

## 4. 缺口与建议

1. 【warn 最优先】research_report_detail_incremental 慢性超时（本图最有价值待查线索，与 DSC-17 coverage 收缩交叉）：处方 IN1-27 在案（vmap12_intake，归数据班），建议升 P1 派工——它同时威胁 DSC-08 consensus 腿与 DSC-17 互验样本量。
2. 【warn 观察】financial_derived 43 天无新 announce（09-02 后）：建议在 DSC-13 供给哨兵给该表加"三季报季窗口期望"（10 月下应现增量），防真停更被节奏差异掩盖。
3. 【正向证据】预期重建链复活判据（consensus max==上游 research max 严格相等）本批复跑持续成立，退役留痕节点 DSC-GAP-CONSENSUSCHAIN 状态维持。
