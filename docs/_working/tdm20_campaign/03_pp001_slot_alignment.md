---
ttl: task_bound
completes_when: 随 tdm20 战役归档（周五 E2E 集成窗消费后）
title: PP-001 排班表对齐——档位补齐+四层判定表契约对照（W3，st-tdm20-20260923）
owner: st-tdm20-20260923
session: st-tdm20-20260923
date: 2026-09-23
---

# PP-001 排班表对齐（W3）

> 总包令：PP-001 每个在图节点补档位（plan_engine 四层判定表现状 0/2/3/4 行→按图补齐该有的行；不日转，日转=集成窗）。
> 纪律裁定（台账 D-6）：判定/结算分离铁律优先于补行——**本班不向判定台账写入任何非实跑产出的行**；"该有的行"以契约对照表+缺口读数交付，真补行=周五集成窗日转实跑产出。

## §1 档位补齐（activation）

- 机械映射：盘前→premarket｜盘中→intraday｜盘后→postmarket｜持续→continuous（D32 门禁包枚举）。
- 覆盖：**138 存量节点中 110 已有档位→72 缺档全部补齐（含本班新增 44 节点）→现全图 182/182 节点带档位**。
- 刻意覆盖保留 2 处：TDM-P-P3-02/TDM-P-P3-03（point=盘中，activation=on_demand）——金字塔加仓=条件触发非定时档，属设计语义非漏填。
- 全绿校验：R15 治理字段枚举 0 error（run_checks fails=0）。

## §2 四层判定表契约对照（节点↔表↔档位）

四表 DDL 真源=schemas/categories/judgment/（DDL-as-Code）；写侧=plan_engine/judgment_ledger.py（MOD-PLAN-026，判定/结算分离）；编排=daily_loop_master_switch（MOD-PLAN-033）16 段。

| 判定表 | 生产节点（图） | 消费节点（图） | 档位 | 实测行数（2026-09-23 05:0x） | 缺口读数 |
|---|---|---|---|---|---|
| judgment_intraday_market_state | TDM-E-L1-AGG（市场状态判定）→ 本班新增 TDM-E-L9-V2 快照 | TDM-E-L2-05 水温响应 / TDM-X-S1-04 退潮信号 | intraday | 12 | L1-AGG→V2→L2-05 的 T-1 快照消费链已上图画，**实跑回填=集成窗** |
| judgment_next_day_forecast | TDM-E-L0-04（明日情绪盘中滚动预测） | TDM-E-L0-01 计划生成（T-1 输入） | intraday 产出→盘前消费 | 4 | 同上 |
| judgment_daily_plan | TDM-E-L0-01（计划生成，playbook scenarios） | TDM-E-L4 买卖点与执行 | premarket | 7 | playbook trigger 可测量性=考试链（E1）前置 |
| judgment_plan_verification | close_verify/settler 结算回填（TDM-E-L0-03 收盘复盘） | TDM-F-C3-01 多维归因引擎 | postmarket | 8 | 验证环闭环依赖结算实跑，禁预填 |

注：总包令所引"0/2/3/4 行"为派发时点读数；上表为本次实测（夜跑恢复后自然增长）。行数本身**不是**缺口指标——缺口=上表"实跑回填=集成窗"各行：图上契约已立，台账行待日转产出。

## §3 排班挂点（现有，不动）

- 日循环入口：`daily_loop_master_switch.run_daily_loop(phase ∈ {premarket, intraday, postmarket, full})`，full=16 段（data_readiness→…→decision）。
- 调度槽：scheduler 特殊槽 `dloop_post`（交易日 16:45 自动圈）；总闸=`data/runtime/daily_loop_master.disabled` 存在即停。
- PP-001 消费：`pf_alloc.allocation_inputs.load_pp001_plan` 读 sleeves（base_weights 先验）；`framework_plans.yaml` 记 source_sha256_12（本班 TDM 变更后由生成器重刷，权重零变化）。
- **本班零调度器改动**（不日转）：无 tasks.yaml 变更、无计划任务变更、无 disabled 翻转。

## §4 能力反查面补注册（secmine 盲区修复）

- capability_canonical_file_registry.yaml 新增 2 条（CAS 原子写）：
  - `sector_signal_family`：aliases=sector/板块/行业轮动/rotation/RRG/虹吸/龙头…（16 模块族，canonical=signal_ashare/sector/sector_analyzer.py）
  - `sector_data_surface`：aliases=板块数据/板块行情/板块快照/sector_ranking/板块资金流…（c1_market.sector_* 表族，canonical=data/sector_ranking_engine.py）
- 修复前实测（secmine §10 D9，2026-09-22）：sector/行业轮动/板块轮动/emotion_index/ETF/轮动/行业 七关键词反查全空。
- 修复后：sector/板块/行业轮动/rotation/板块数据 全部命中（emotion_index/ETF 属情绪线与 ETF 资产族，**不在本班写域**，留证移交）。

## §5 遗留与移交

1. emotion_index/ETF 反查关键词补编：归情绪线/ETF 资产 owner 线（本班只修板块面，不越域）。
2. 四判定表实跑回填：周五 E2E 集成窗按上表契约逐行接电（dloop_post 槽恢复后自然产出）。
3. plan_engine 判定表行数读数建议纳入骨架健康读数（generate_skeleton_health.py 消费面，本班不动）。
