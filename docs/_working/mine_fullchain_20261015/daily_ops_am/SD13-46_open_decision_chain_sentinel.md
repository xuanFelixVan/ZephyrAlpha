---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-46
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-46 盘初决策链哨兵（09:40 只读巡检）

## 1. 定义

每日 09:40（盘初 10 分钟）Windows 计划任务 ZephyrAlpha_DecisionChainSentinel 拉起治理域哨兵脚本 v10（14 测绿）：盘初核对 L0-L4 决策链健康并告警（只读）。已查处缺陷：无交易日闸实锤（decision_chain_sentinel.py 零 is_trading_day 引用）——国庆假 10-01..07 每日 09:40 照触发=假日空跑在案，加闸归哨兵车道小修（2026-10-05 排查发现）；last_at 时区口径与 09:40 CST 不吻合待复判（降🔨）。决策问题：09:40 决策链健康巡检跑了吗？红项告警送达谁？

地图在册态：wiring=partial、build=partial、downstream_action=alert_only。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | L0-L4 决策链健康读数（只读巡检目标族） | `scripts/governance/decision_chain_sentinel.py`（v10，14 测绿在册） |
| 输出面 | 健康巡检告警（红项送达面）；资源册实测样本 1 条（peak 0.117GB） | `config/trading_day_cycle_map.yaml#D13-46` evidence；`scripts/tasks/register/register_decision_chain_sentinel_task.ps1:69` |
| SSOT 真源 | 图13 节点契约（行 3603-3666）+ 注册声明面 | `config/trading_day_cycle_map.yaml#D13-46`；`docs/_working/map_build/fig13_daycycle/05_盘中资金流与决策层.md` |
| 代码模块 | 哨兵脚本+计划任务注册（MOD-GOV） | `scripts/governance/decision_chain_sentinel.py`；`scripts/tasks/register/register_decision_chain_sentinel_task.ps1` |
| 门禁约束 | 只读=无 RULE-DATA-OPS 破坏性面；无交易日闸=假日空跑（浪费+告警噪音）；last_at 时区口径未定（RULE-SCHEMA-TZ 精神 applicable） | `config/trading_day_cycle_map.yaml#D13-46` evidence（零 is_trading_day 引用+假日空跑在案） |
| 自动化触发 | mechanism=B_windows_task，每日 09:40；trigger_facts last_run=2026-10-08T09:40:01；schtasks 双证 | `config/trading_day_cycle_map.yaml#D13-46` cadence_zh/trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 巡检目标族（决策链）在册且只读 |
| 输出面 | warn | 告警主体在但「红项送达谁」无答主（consumers=[] 机生零消费在册） |
| SSOT 真源 | pass | 节点契约+注册声明面完整 |
| 代码模块 | pass | 脚本+注册器实存（14 测绿） |
| 门禁约束 | warn | 假日空跑在案（缺 is_trading_day 闸）+last_at 时区口径待复判 |
| 自动化触发 | pass | 每日 09:40 last_run 在窗 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点；本格是 B 段「partial 但小修可升级」代表（地图注：加闸归哨兵车道小修）。
- gap_refs 空；consumers=[]（零消费在册）。
- 建议：①哨兵加 is_trading_day 闸（小修，地图已点名归哨兵车道）；②last_at 时区口径复判后回写；③告警送达面（红项→谁）补登记，消灭「检出无主」同族问题（与 D13-03 检出即蒸发同谱系）。
