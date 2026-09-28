---
ttl: task_bound
title: L09 案卷 F86 — AI 六族管线（ai_layer 九子包：落地已翻绿，部署缺半，触发缺全）
session: zc-l09-20260927
---

# F86 AI 六族管线（J 段 A1，骨架态=partial/P1）

## 一、六向台账（2026-09-27 实证，相对 M4 盘面有重大翻绿）

| 向 | 实测证据 |
|---|---|
| 上游输入 | `config/ai_source_registry.yaml`+`config/evolution_schedule_seeds.yaml`（本日双实存）；L1-L7/OBJ DESIGN 11 本（docs/_working/ai_layer_vision/） |
| 下游消费 | api_server AI 路由已落（:4914 switch_engine.approval_router；:5132-5153 scheduling dispatcher/seed_writer——M4 时为"补丁蒸发"，现已随大单落地）；施工排产（evolution_schedule_seeds→I7 生成器） |
| 自动化触发 | 自动常驻仅"两处半"（redline 三 gate 提交链内+runtime 拦截器解释器级[本机未引导，见 F88]+perceive 内监挂既有事件源）；order_daemon 零 spawn；外扫宿主 `register_ai_l1_scan_task.ps1` 本日仍不存在（缺③未解） |
| 真源与注册表 | capability 卡 10 张（ai_perceive_l1…obj_t_tools，44 卡总量内）；DDL 脚本族 `scripts/ai_layer/` 9 件实存（apply_ai_heritage/intake/layer_scheduling/model_library_ddl+gen_* 五件） |
| 门禁与质量尺 | redline 三 gate enabled:true（in_process_gate_registry.yaml:710/716/722，09-26 st-ddup 翻回注记"245/678 件批已落 HEAD（30505c93f6）"）；tests/ai_layer 690 passed 基线（M4 09-25 实测，本日未重跑） |
| 当前运行状态 | **黄→部分翻绿**：缺①落地已解（HEAD 62 件=盘面全量，零 staged/untracked）；缺②部署半解（ai_scheduling 已建，ai_compare/ai_tools 仍缺）；缺③触发未解（三阀仍关） |

## 二、子模块三级枚举（九子包逐目录实扫，61 .py+根 __init__=62，与任务书数字逐一相符）

| 子包 | .py 数 | 内件（三级：包/件/角色） |
|---|---|---|
| comparator(L4) | 11 | experiment_store/executor/fairness/too_good/compare_events/policy+考场适配器×4（venue_c4/replay/dual_run/tool_bench，fail-closed 拒考） |
| redline(OBJ_S) | 10 | negative_list/negative_list_gates/session_env_guard/drop_gate/no_delete_manifest/dashboard_pipeline/sev_router/freedom_weekly_report/annual_review |
| heritage(L7) | 7 | priors/store/heritage_events/forget/closure_check/policy |
| scheduling(L5) | 7 | router/maturity/dispatcher/order_daemon/seed_writer/scheduling_events |
| cleaning(L3) | 6 | policy/spec_store/local_prefill/washer/auditor（washer=全包唯一 LSG 合规调用示范点） |
| intake(L2) | 6 | gate/card_store/dedup/intake_events/kpi（生食库 PG ai_intake 13 表，禁产线 import 红线句） |
| switch_engine(L6) | 5 | tombstone_manager/approval_router/revert_drill/rollout_tiers（底层状态机真身在 intelligence/switch_engine/） |
| tools(OBJ_T) | 5 | inventory_generator/usage_stats/scoring/suite |
| perceive(L1) | 4 | source_registry/search_orders/translator（内监；**外扫节拍宿主未建**） |
| OBJ_M/OBJ_R | — | config 三件（model_intel_sources/model_scoring_policy/dual_run_criteria）；OBJ_R S3 提案蒸发件待重铸（收口册03 OR-WO-S3） |

## 三、接线四态独立复核

- **HEAD 落地=已翻绿（本日勘误核心）**：`git ls-tree -r HEAD src/zephyr/ai_layer`=62 件、九包全量；`git status --porcelain` 零残留。落地载体=commit `30505c93f6`（678 件 v6 emergency 通道，Owner 批准 B 方案）——M4 收口册02"缺①（8 族 untracked+接线批蒸发）"**已解除**。
- **PG 部署=半解**：本日 information_schema 实扫 ai% = ai_heritage(9 表)/ai_intake(13)/ai_intake_test_smoke×2(各12, 残留)/ai_layer_model(3)/ai_scheduling(1)。
  - `ai_scheduling.ai_work_order` **已存在**（M4 记"不存在"，且真名=ai_scheduling 非"ai_layer_scheduling"）——勘误；0 行。
  - `ai_compare`、`ai_tools` **仍不存在**（缺②剩余两条 --deploy 待 Owner high 门）。
  - ai_heritage 9 表/ai_layer_model.model_registry+model_price_history/ai_intake.ai_cleaning_spec 本日复核**全 0 行**（库空转维持）。
- **触发=未解（缺③）**：order_daemon 零 spawn+ai_work_order 0 行；translator.py 本日 grep 零 priors/heritage 命中（L1-WO-9 先验接口未接）；L1 外扫宿主 ps1 不存在（L1-WO-7 未施工）；L7 DESIGN 状态翻转未裁（夜报 #10）。
- **投影面=已接线**：api_server approval_router/scheduling 路由代码在 HEAD（M4 时蒸发件已重铸落地）。

## 骨架勘误

1. 骨架"partial（M4：DDL 未部署等）"须拆分：**落地缺已解（62 件全落 HEAD）、部署缺半解（3 缺 1：ai_compare/ai_tools 仍缺，ai_scheduling 已建）、触发缺未解**。
2. ai_scheduling schema 真名勘误：M4 分册01/收口册02 记"ai_layer_scheduling 未部署"，本日实存 schema 名=`ai_scheduling`（1 表）。
3. api_server 四路由行号漂移：M4 记 4423/4497/4513/4534，本日实锚 4914/5132-5153（路由已落，行号随大单移动）。
4. redline 三 gate 曾被停用、09-26 翻回 enabled:true（册内注记 W4 看守项）——F87/F86 联动面已恢复。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | ai_compare/ai_tools 两 schema 未部署 | `experiment_store --deploy`+`usage_stats --deploy`，Owner high 门（收口册02 缺②③条/XC-WO-4） | P1 |
| 2 | 进化主循环三阀全关（外扫宿主未建/常驻零 spawn/heritage 回流 0 行） | L1-WO-7/L7-WO-ST/order_daemon 启动登记，全 Owner 门（收口册03 依赖主链） | P1 |
| 3 | ai_intake_test_smoke×2 残留 schema | RULE-DATA-OPS 三步验证后 DROP（Owner） | P2 |
| 4 | heritage/model/cleaning_spec 三库 0 行空转 | 随首单闭环回填种子（非独立施工） | P2 |
| 5 | 35 施工单中 4 件蒸发重铸单（L5-C9/OM-C7/L6-S6/OR-S3） | 收口册03 只列不施工，随批重铸 | P2 |

## 五、自审闸三态

**挖干可施工（九包 62 件穷举+git/PG/api_server 三面独立复核）✅；待裁（缺②部署与缺③触发的 Owner 门位时序，收口册02 §五建议缺①已解后三缺并行批）；本日未重跑 690 测试基线（登记为沿用 M4 09-25 实测）。**

## 六、复跑命令

```bash
git ls-tree -r HEAD --name-only src/zephyr/ai_layer | wc -l          # 62
git status --porcelain src/zephyr/ai_layer | wc -l                   # 0
for d in comparator redline heritage scheduling cleaning intake switch_engine tools perceive; do echo "$d $(ls src/zephyr/ai_layer/$d/*.py | wc -l)"; done
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(read_only=True); cur=c.cursor(); cur.execute(\"SELECT table_schema,count(*) FROM information_schema.tables WHERE table_schema LIKE 'ai%' GROUP BY 1\"); print(cur.fetchall()); c.close()"
ls scripts/register_ai_l1_scan_task.ps1                              # 不存在=缺③在
grep -n "priors\|heritage" src/zephyr/ai_layer/perceive/translator.py | wc -l  # 0=L1-WO-9 未接
```
