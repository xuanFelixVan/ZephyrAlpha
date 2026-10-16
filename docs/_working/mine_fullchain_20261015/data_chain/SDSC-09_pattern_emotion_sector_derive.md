---
ttl: task_bound
---
# SDSC-09 形态 / 情绪 / 板块状态衍生

> 挖矿工程：全链路图12 数据供给链 S3 衍生段 3/4｜真源=config/data_supply_chain_map.yaml#DSC-09｜挖矿时点=2026-10-15（含当日只读复跑）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：形态/情绪/板块状态衍生，node_type=stage，build_status=partial，verified_scope=structure，行级状态=分面（pattern ✅ / emotion ✅ / daban 🟡 / sector 🔴）。
- 职责一句话：两类触发面并存——tasks.yaml 档期（形态/情绪/打板族 internal 任务）+scheduler 硬编码特殊槽（sector_close_final/sector_pre_open，产物在 tasks.yaml 之外）；renko/point_figure/kagi 真身是信号域纯函数算法叶（不落库）。
- 决策问句（图原文）：板块状态这张表该不该有 T 日截面？派生全集能不能只靠 tasks.yaml 枚举？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-06→DSC-09（行情/打板就绪→派生）；原料=盘后行情+板块快照 | config/data_supply_chain_map.yaml edges DSC-06→09 |
| 输出面 | c1_market.market_pattern_event/emotion_index/sector_state/sector_preference/daban_board_event→DSC-HA（L1/L2 传感器+plan_engine 供料）；本批复跑：emotion_index max=2026-10-15、market_pattern_event max=2026-10-14、daban_board_event max=2026-10-12（滞后）、sector_state close_final=10-14/pre_open=10-09（倒挂未销）、sector_preference 7 行（近空转） | config/data_supply_chain_map.yaml#DSC-09 data_refs；本批 CH 直查 |
| SSOT 真源 | 特殊槽真源=scheduler._run_special_schedule 硬编码白名单（以 tasks.yaml 为唯一枚举源的生成器会结构性漏掉这条腿——图 machine 层如实分列）；语义层=图12 DSC-09 | src/zephyr/data/scheduler.py（special 白名单）；config/data_supply_chain_map.yaml#DSC-09 machine.slots（两槽 task_count=0/special_dispatch=true） |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/implementations/internal_compute_provider.py（板块状态 pipeline 蓝图号畸形改挂代表路径）；执行体 sector_state_pipeline.py/series_transform.py 实存；renko path_ghost 已改挂真身 | src/zephyr/data/implementations/internal_compute_provider.py；src/zephyr/data/sector_state_pipeline.py；src/zephyr/signal_ashare/strategy_signal/series_transform.py（本批 ls） |
| 门禁约束 | 检测≠修复（downstream_action=detect_only）；产物一致性无校验（pre_open 只能复制已存在 close_final 的定义约束无机械检查）；禁自造 MOD 号（登记收口请求纪律） | config/data_supply_chain_map.yaml#DSC-09 fallback/gaps；AGENTS.md §8 路径禁凭记忆 |
| 自动化触发 | wired_special_branch：sector_close_final/sector_pre_open 两槽特殊分派（dispatched_slots 在册）；形态/情绪/打板走档期；两特殊槽 task_runs 零行=计数腿未接（insufficient_window） | config/data_supply_chain_map.yaml#DSC-09 machine+trigger_facts |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 行情原料今日鲜（DSC-01/02 交叉证），衍生供料成立 |
| 输出面 | warn | emotion/pattern 两腿今日鲜；daban 滞后 3 日（10-12）、sector_state pre_open 停 10-09 vs close_final 10-14（倒挂缺陷复现且扩大）、sector_preference 7 行近空转——四腿两鲜两滞 |
| SSOT 真源 | warn | 特殊槽硬编码白名单=结构性枚举盲区（图已如实登记）；sector_state_pipeline.py 蓝图号畸形（含空格非 MOD-* 形态）收口请求仍在途 |
| 代码模块 | pass | 三执行体实存；renko/point_figure/kagi 路径幽灵已在图改挂 series_transform 真身 |
| 门禁约束 | warn | 产物一致性（pre_open<=close_final）无校验器：倒挂 09-25 曾消、本批复跑又现且滞后扩大=缺陷未销的机械复现 |
| 自动化触发 | warn | 特殊分派在机（close_final 隔日有产）；但两特殊槽计数腿未接+今日 10-15 close_final 未落（复跑时点 21:33）=当日档期执行存疑 |

## 4. 缺口与建议

1. 【warn 复发】sector_state pre_open/close_final 倒挂：定义约束（pre_open 复制 close_final）缺机械校验，建议加一条 T 日截面断言进 DSC-13 哨兵（检出不修、但把倒挂从人工复跑变成日检红）。
2. 【warn 持续】sector_preference 供料端近空转（全表 7 行）：丁线 owner_gate 消费在等；建议查其上游任务的 symbols 范围与 disabled 态，判定是"有意最小供料"还是"静默缩水"。
3. 【warn 结构】tasks.yaml 唯一枚举源漏特殊槽腿：图的 machine 层已用 slots+scheduler_dispatch 双面互证兜住；建议把特殊槽白名单从硬编码迁到声明式配置（与 schedule.yaml 同源），一次消掉枚举盲区。
4. 【正向证据】形态/情绪两腿（market_pattern_event/emotion_index）本批全鲜，daban 腿从 09-22 停更恢复到 10-12（滞后收窄中但未闭合）。
