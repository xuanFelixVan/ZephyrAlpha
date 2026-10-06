---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e0_compute —— E0 算力调度（SPM 18 节点）

- 真源: `config/strategy_production_map.yaml` nodes L68 起（行号=SPM:L*）；族=layer_id E0。
- 职责: 重算力任务的开闸裁判与算力经济（trade_calendar 当闸、事件触发禁定时器、白天轻任务/夜批重任务）。
- 计数: 18 = 1 stage(partial) + 17 mechanism（built 15 / partial 1 / pending 2）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E0 | 算力调度心跳（stage） | partial | MOD-BT-151 | SPM:L69 |
| FAC-E0-M-001 | 算力调度闸门 | built | MOD-BT-151 | SPM:L451 |
| FAC-E0-M-002 | 批次窗口预检（Batch Window Preflight） | **pending** | MOD-BT-226 | SPM:L471 |
| FAC-E0-M-003 | GPU Core（回测 GPU 薄核） | **pending** | MOD-BT-233 | SPM:L482 |
| FAC-E0-M-004 | 资源优化引擎——GPU 监控/进程池化/自愈 | built | MOD-RESOURCE_OPTIMIZATION_ENGINE | SPM:L493 |
| FAC-E0-M-005 | 系统大脑三层运行时（节律调度与工厂夜批同机竞争算力） | built | MOD-INF-035 | SPM:L505 |
| FAC-E0-M-006 | 排班冲突检测闸（互斥组/内存天花板/E0 三查） | built | MOD-RESCHED-GATE | SPM:L517 |
| FAC-E0-M-007 | 资源画像注册表+生成器（排班真源） | built | MOD-RESCHED-PROFILE | SPM:L541 |
| FAC-E0-M-008 | 资源实测采样器 | built | MOD-RESCHED-SAMPLER | SPM:L559 |
| FAC-E0-M-009 | 排班冲突告警桥 | built | MOD-RESCHED-ALERT | SPM:L581 |
| FAC-E0-M-010 | 资源调度器 | built | dir:_domain_infrastructure_runtime/resource_scheduler | SPM:L601 |
| FAC-E0-M-011 | NSSM+5 进程架构与 Supervisor（工厂夜批宿主） | built | MOD-INF-066 | SPM:L613 |
| FAC-E0-M-012 | SLI/SLO+Token Budget——算力容量守护 | built | MOD-INF-001 | SPM:L625 |
| FAC-E0-M-013 | GPU 上岗热交换模型（两档显存画像） | built | MOD-INF-069 | SPM:L637 |
| FAC-E0-M-014 | GPU 资源管理 | built | dir:_domain_data_eng/gpu_resource_manager | SPM:L649 |
| FAC-E0-M-015 | 交易日历（E0 闸门数据源） | built | code:src/zephyr/data/trading_calendar.py | SPM:L661 |
| FAC-MAP-M-001 | 策略工厂图结构校验器（FACTORY-MAP 本图守卫） | built | MOD-BT-080 | SPM:L4879 |
| FAC-MAP-M-002 | 本图对抗测试件 | built | MOD-BT-081 | SPM:L4893 |

注：FAC-MAP-M-001/002 是全图守卫件，物理挂在 E0 名下（这正是"骨架 16 vs 实查 17+2 图守卫"口径分歧的来源之一，见 00 §5 C1）。

## 2. 接线现状与缺口判定

- 已接线（built 15）：闸门语义（classify_window+gate_decision 四枚理由码、日历缺失 fail-closed、收盘缓冲 15:30）= FAC-E0 algo_note 自述（SPM:L69-90 区）；排班族（M-006~M-009）+ 画像注册表（M-007）构成排班真源闭环。
- 缺口 1：FAC-E0-M-002 批次窗口预检 pending（MOD-BT-226）——预检器未落地，重批次开跑前的窗口复核缺位。
- 缺口 2：FAC-E0-M-003 GPU Core pending（MOD-BT-233）——**状态张力**：#ARCH-366/W-173 已有 gpu_core 张量核冒烟实测（0.53s/格口径，经 H9 §3.4 引用），build_status 疑滞后（00 §5 C4）。本车道不改图，留图侧复核。
- 可考性：E0 是考卷的前置闸而非考卷内容——现行考卷已消费"E0 问闸+GPU 独占+vram.concurrency=1"语义（H9 §3.3 第 4 条）。骨架可考，无需新考卷。

## 3. 修复建议（一句话）

M-002 批次窗口预检按 MOD-BT-226 设计补落地；M-003 由图侧把 #ARCH-366 实测进度回写 build_status（改图属他队域，本车道只登记）。

## 4. 交叉验证

- chief B1 ENV-17（策略生产闭环 E0-E9）计数一致（341/built315/12/14，`docs/_working/chief_fullchain_20261006/01_skeleton_environments.md` §1 表）。
- H9 §3.3/§3.4：E0 问闸在 prereg 治理中为不变项；GPU 口径出处与 M-003 pending 的张力=00 §5 C4。
- map_census 00_panorama：FACTORY-MAP gate142（census §1 表）与 FAC-MAP-M-001 守卫节点对应关系为本车道补充挖矿（census 未记录节点级守卫）。
