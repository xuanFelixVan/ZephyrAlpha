---
ttl: task_bound
---
# SDSC-06 幂等写与判重（引擎语义 + 全字段判重正门）

> 挖矿工程：全链路图12 数据供给链 S2 入库段 3/3｜真源=config/data_supply_chain_map.yaml#DSC-06｜挖矿时点=2026-10-15
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：幂等写与判重（引擎语义+全字段判重正门），node_type=stage，build_status=partial，verified_scope=structure。
- 职责一句话：幂等由调用方决定（ReplacingMergeTree 直接 INSERT / MergeTree 写前 DELETE）；判重口径是破坏性操作的准入闸——真重复定义=全字段相同，禁 count()-uniqExact(排序键)（2026-07-16 tick 21 个月误删事故的治本件）。判重唯一正门=check_tick_duplication.py（RULE-DATA-OPS）。
- 决策问句（图原文）：这批行是引擎合并造成的读数差，还是真重复？能不能据此删？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 两条 data_flow 入边（DSC-04 写入后口径生效/DSC-05 tick 引擎幂等）+两条反馈边（DSC-18 合并效果回判/DSC-19 自愈腿保读判口径可用） | config/data_supply_chain_map.yaml edges DSC-04→06/DSC-05→06/DSC-18→06(feedback)/DSC-19→06(gap 边注) |
| 输出面 | 判重报告=stdout/人工案卷（无落库台账=审计缺口在册）；判重结论是 DSC-16 修复/删数动作的准入前提；pass-through 全部入库幂等声明 | config/data_supply_chain_map.yaml#DSC-06 store_refs（"无（案卷不入库＝审计缺口）"原文） |
| SSOT 真源 | RULE-DATA-OPS（判重只走 check_tick_duplication 正门，禁聚合数判重）+图 laws（ReplacingMergeTree 判真必 FINAL 且双版并报） | AGENTS.md §1 RULE-DATA-OPS；config/data_supply_chain_map.yaml laws |
| 代码模块 | module_id=MOD-GOV_DQ，module_ref=scripts/governance/data_quality/check_tick_duplication.py；执行体该脚本+ch_reader.py 实存 | scripts/governance/data_quality/check_tick_duplication.py；src/zephyr/data/ch_reader.py（本批 ls） |
| 门禁约束 | 破坏性 DB 操作三步验证（必要/真实/可逆）；FINAL 双版并报；ch_reader 自动注 FINAL/DatabaseService 原生连接不注=同一 SQL 两通道结果可不同（residual 在册） | AGENTS.md §1 RULE-DATA-OPS；config/data_supply_chain_map.yaml#DSC-06 fallback |
| 自动化触发 | wired_import+ad-hoc CLI（manual，无节拍）；引擎侧幂等随写路径自动生效（无独立触发面） | config/data_supply_chain_map.yaml#DSC-06 wiring_status/trigger_facts（insufficient_window） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 写入/引擎/反馈四边在册，被检对象（tick_data 等）今日在产 |
| 输出面 | warn | 报告不入库=审计缺口持续；判重结论的消费方（修复/删数）全靠人工案卷串联 |
| SSOT 真源 | pass | 正门唯一性双锚（宪法 RULE-DATA-OPS+图 laws）；误删事故治本件口径未松动 |
| 代码模块 | pass | 正门脚本实存，且 fail-visible 修复已落地：_query_rows_or_raise（FIX 2026-10-07 DSC-06②，失败必抛点名 leg，禁当 0 行处理）——DSC-GAP-DUPGUARD 的 Code 42 恒抛被吞缺陷已闭合（本批实读脚本 185-198 行 docstring 原文） |
| 门禁约束 | pass | 聚合对照腿修复后两态结构可分（查询失败≠0 行）；三步验证+FINAL 纪律在册 |
| 自动化触发 | warn | 正门仍为 ad-hoc CLI 无节拍：修复后无一次运行留痕可查（trigger_facts insufficient_window 延续），"修好了"与"在用"之间缺一段运行证据 |

## 4. 缺口与建议

1. 【已闭合，建议留痕归档】DSC-GAP-DUPGUARD（判重器聚合对照腿不可用/半假绿+硬编码主区路径）：fail-visible FIX 2026-10-07 已落地（脚本内注释原文锚定）；建议图侧把该 gap 节点转退役留痕（同 MACRO/CONSENSUSCHAIN 先例），硬编码主区 src 的 sys.path 注入是否同步修掉需一次复核。
2. 【warn 持续】判重报告不入库：建议把每次运行的 JSON 摘要落 data/failures/ 同构目录（dup_check 案卷族），让破坏性操作准入闸有翻得了的账（审计缺口原文即此）。
3. 【warn 持续】两通道 FINAL 语义差（ch_reader 自动注/原生连接不注）：建议在 DatabaseService 文档面加一行红字，防修复人员拿原生连接读数下删除结论。
