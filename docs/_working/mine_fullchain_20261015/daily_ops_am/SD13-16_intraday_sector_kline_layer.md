---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-16
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-16 盘中板块分钟K线层（tdx 通道已退役——撮合收敛 D13-48）

## 1. 定义

原盘中每 5 分钟独立执行器池 `intraday_sector`（tdx/mootdx 直连）产板块指数分钟K；**2026-10-04 B1 三退役批正式退役**（五 tdx 任务 disabled+计划任务注销）——盘中实时板块K通道已死，产能收敛至 D13-48 盘后撮合（15:40 等权链式聚合，段外 C）。决策问题：板块分钟K独立池在产吗？断供几个交易日？

地图在册态：wiring=unwired_slot_hollow（我段 4 个之一）、build=partial、red_reason=broken_supply；终局注记：tdx 通道永久断供+任务退役（known_data_gaps verification_20261004 B1 批）。tdm_refs=TDM-E-L2-04。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | tdx/tqcenter（通达信插件 880xxx 板块指数分钟K）——**源头停供风险被 Owner 2026-10-05 指示点名，退役即对该风险的处置** | `config/trading_day_cycle_map.yaml#D13-16` evidence（源头风险+终局注记） |
| 输出面 | 盘中实时板块K=0；替代产能=D13-48 盘后等权撮合（盘中实时性诉求改盘后承接） | `config/trading_day_cycle_map.yaml#D13-16` note_zh；`config/trading_day_cycle_map.yaml#D13-48`（段外承接格） |
| SSOT 真源 | 图13 节点契约（行 1302-1380）+ known_data_gaps B1 批 | `config/trading_day_cycle_map.yaml#D13-16`；`config/data_supply_chain_map.yaml:280`（同槽图12 侧） |
| 代码模块 | 槽壳仍在册（intraday_sector 执行器+5 任务 disabled） | `src/zephyr/data/config/schedule.yaml:50-54`（槽+独立执行器声明实核） |
| 门禁约束 | 退役批=Owner 指示经正式通道（2026-10-05）；freshness_severity 极端形态：断供不在断供哨兵名单⇒无级可言（A2 缺位极端形态在册） | `config/trading_day_cycle_map.yaml#D13-16` evidence/freshness_severity_zh |
| 自动化触发 | mechanism=A_apscheduler 名义盘中每 5 分钟；30d count=230（退役前历史）；in_catchup_universe=true 但通道死=补跑无意义 | `config/trading_day_cycle_map.yaml#D13-16` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | fail | tdx 通道永久断供（退役终局在册） |
| 输出面 | fail | 盘中实时板块K产能=0（替代在盘后 D13-48） |
| SSOT 真源 | pass | 退役终局/源头风险/承接格三段契约完整 |
| 代码模块 | warn | 槽壳+5 任务仍挂 schedule.yaml（disabled），退役清理不彻底 |
| 门禁约束 | pass | 退役经 Owner 通道在册；哨兵盲区已显式登记 |
| 自动化触发 | warn | 槽壳名义节拍在而实产 0；30d 230 拍系退役前遗留读数 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**unwired_slot_hollow 5 个之一**；freshness_severity 缺口（A2/C4）极端形态代表格。
- gap_refs 在册：benchmark:A2、benchmark:C4（同 D13-14 族）。
- 建议：①退役收尾：disabled 任务与空执行器池择机摘除（或明确保留为墓碑并注记）；②板块K实时性若日后重启，先裁 tqcenter 停供风险的对冲源，不再裸押单一插件；③A2 分级接线后本格应显式标「退役格」而非空心格。
