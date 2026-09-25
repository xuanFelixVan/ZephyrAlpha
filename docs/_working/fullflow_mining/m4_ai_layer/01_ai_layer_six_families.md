---
ttl: task_bound
title: M4 分册01 — ai_layer 六族（实为 8+1 族）入口与状态
lane: m4_ai_layer
session: st-commitspeed-tbl-20260924
date: 2026-09-25
status: mined
---

# 01 — ai_layer 六族状态册（src/zephyr/ai_layer/ 全族穷尽）

## 一、环节定义与边界

AI 层（自我进化引擎）工程落点：`src/zephyr/ai_layer/` 按"七段一常数"（L1-L7+OBJ_M/R/S/T）组织为 **9 个子包**（任务书所称"六族"实为盘面 8 族+intake 首批族）。总骨架真源=`docs/_working/ai_layer_vision/README.md`（v2.0 active）。上游=capability/LSG/meta_question（分册 02/03/04）；下游=施工排产（scheduling 种子→生成器 I7）、仪表盘投影（api_server 四路由）、redline 三 gate（提交链消费）。

## 二、六向台账

| 向 | 实测证据 |
|---|---|
| 上游输入 | L1 源注册表 `config/ai_source_registry.yaml`；政策族 config×16（veins/cleaning/comparison/heritage/schedule_gate/obj_s_degradation/switch_criteria/tool_exam 等，全部在 staged v4 清单） |
| 下游消费 | `scripts/governance/d5_architecture/generators/`（I7 生成器消费 evolution_schedule_seeds）；`src/zephyr/frontend/dashboard/api_server.py:4423/4497/4513/4534` 四只读路由消费 perceive/scheduling 投影 |
| 自动化触发 | **全族零 cron/零 Timer/零 sleep-loop**（perceive/__init__ 事件纪律句 + order_daemon 头"零定时器零轮询"）；唯一事件源=SchedulingJournal 尾随；月检=人工点火 CLI |
| 真源与注册表 | 各族 DESIGN.md（docs/_working/ai_layer_vision/L*/DESIGN.md）；capability 卡 10 张（ai_perceive_l1…obj_t_tools）；DDL=scripts/ai_layer/apply_*_ddl.py |
| 门禁与质量尺 | redline 三 gate（149/150/151，见分册01§四）；tests/ai_layer/ 61 个测试文件——**本夜实测 `pytest tests/ai_layer -q` = 690 passed / 0 failed / 0 skipped（49.14s，2026-09-25 凌晨主区）** |
| 当前运行状态 | **黄**：代码与测试网全绿（690 passed 实测），但 63 件未落 HEAD；PG 侧 ai_compare/ai_tools 两 schema 未部署 |

## 三、子模块清单（逐族，两源交叉验证：ls+capability 卡+PG）

### 1. perceive（L1 感知）— 入口 `src/zephyr/ai_layer/perceive/`
- `source_registry.py` 源注册表装载（config/ai_source_registry.yaml）｜`search_orders.py` 定向搜索任务单（SearchOrderJournal）｜`translator.py` 内监翻译器（五既有探测器事件信号）
- 状态：**代码就绪、外扫节拍宿主锁定**——外扫节拍宿主=施工项 7，受 T3 双前置约束（Owner 追认+裁定登记）未解锁；月检生成器 `scripts/ai_layer/gen_ai_layer_monthly_checkup.py`（STARTUP manual，人工点火，产出 checkups/YYYY-MM.md+json 双轨）
- 实测：`python -m import` OK；monthly_checkup 头部 `[STARTUP] manual`

### 2. intake（L2 收集）— 唯一已落 HEAD 的族
- `gate.py/card_store.py/dedup.py/intake_events.py/kpi.py` 五件；生食库=PG `ai_intake` schema（13 表），产线代码禁 import（__init__ 红线句）
- 状态：**绿（唯一 HEAD 落地族+有真数据）**。commit 84007a1d6a（intake 族第 3 批落地）；PG 实测：ai_intake_card=6 行、ai_intake_ref_snapshot=3595 行、source_quota=12、kpi_weekly=4
- ⚠️ 病灶：PG 残留 `ai_intake_test_smoke`、`ai_intake_test_smoke2` 两 smoke 测试 schema（测试隔离违规残留，待清洗）

### 3. cleaning（L3 清洗）
- `policy/spec_store/local_prefill/washer/auditor` 五件；外部 fetched 代码零执行（E0-E6）；**全部 LLM 调用经 LSG**（washer.py 是全包唯一 GATE-20 命中件，合规挂网关）
- 状态：代码就绪 staged；PG `ai_intake.ai_cleaning_spec`=0 行（规格卡库空转，无生产清洗流量）

### 4. comparator（L4 对比）
- `experiment_store/executor/fairness/too_good/compare_events` + 考场适配器×4（venue_c4/replay/dual_run/tool_bench，fail-closed 拒考）
- 状态：代码就绪 staged；**PG `ai_compare` schema 不存在**（DDL 内嵌模块 CLI `--schema ai_compare --verify`，"施工批 PG 只读"零生产部署）；考场零真流量

### 5. scheduling（L5 排产）
- `router/maturity/dispatcher/order_daemon/seed_writer/scheduling_events` 六件；排班只写种子 `config/evolution_schedule_seeds.yaml`（禁直改 resource_profile_registry）
- `order_daemon.py`：**事件驱动型"常驻"件但当前无常驻实例**——设计=消费 SchedulingJournal（单例锁 PID+TTL 600s+僵尸检测，belt 同款），胜者落库 emit `evolution_winner_due` 触发 process_once；零定时器。实测无该守护进程在跑（无启动登记）
- PG `ai_layer_scheduling` DDL 脚本在（apply_ai_layer_scheduling_ddl.py，ai_work_order 表），schema 未见于 information_schema（未部署或并入他 schema——实测 `ai%` 枚举无此名）

### 6. switch_engine（L6 切换，AI 层侧）
- `tombstone_manager/approval_router/revert_drill/rollout_tiers` 治理四件；底层状态机真身在 `src/zephyr/intelligence/switch_engine/`（switch_engine.py/switch_registry.py/shadow_runner.py/criteria.py 四件全在）
- 状态：代码就绪 staged；墓碑制（退役不删，git tag+status=tombstone）；复活恒 route=shadow_recheck

### 7. heritage（L7 传承）
- `priors/store/heritage_events/forget/closure_check` 五件；D-L7-02：PG `ai_heritage` schema 全读写经 DatabaseService/depgraph 通道
- 状态：**DDL 已部署（9 表实存）但零数据**——ai_heritage_entry/l1_prior/kpi 实测全 0 行。回流闭环关键边建成未通水

### 8. redline（OBJ_S 红线与自由域）— **ModuleNotFoundError 之谜：真身存在**
- 九件全在 `src/zephyr/ai_layer/redline/`：negative_list（NL-1..6 编号层）/negative_list_gates（三 gate 工厂）/session_env_guard/drop_gate/no_delete_manifest/dashboard_pipeline/sev_router/freedom_weekly_report/annual_review
- **实测（2026-09-25 凌晨，Python 3.12.8 主区）**：10 模块 import 全 OK（zephyr.ai_layer.redline + 9 子模块逐一 importlib 验证零异常）。昨晚所报 ModuleNotFoundError 判定为**环境性误报**：redline 九件时间戳 Sep 25 00:30（当晚重写盘面），误报窗口应为蒸发/删除事态期间的 worktree 视角缺件；主区现行盘面无恙
- 三 gate 挂载实证：`in_process_gate_registry.yaml:707-725` REAL-KEY-REFERENCE-SCAN(149)/TASK-ORDER-DOCS-LOCK(150)/CONSTITUTION-LINE-LIMIT(151)，enabled: true，own-diff 作用域，模块路径 zephyr.ai_layer.redline.negative_list_gates

### 9. tools（OBJ_T）与 intake 之外的常量线
- `inventory_generator/usage_stats/scoring/suite` 四件；organ 词表与 OBJ_T DESIGN 同源
- 状态：staged；PG `ai_tools` schema 未部署（usage_stats 自述"本班零生产 DDL 部署"，--deploy 待 Owner 点火）

### OBJ_M/OBJ_R（模型线/规则线）
- OBJ_M：config 三件（model_intel_sources/model_scoring_policy/dual_run_criteria）已在 v4 清单；PG `ai_layer_model` 3 表实存但 model_registry/model_price_history=0 行
- OBJ_R：S3 提案骨架（76 常量：31 纳入/45 排除留痕）在 staging obj_r_s3_proposal.md，施工归 gov 车道

## 四、常驻自动 vs 手动触发判定（本册核心问题）

| 组件 | 触发形态 | 实证 |
|---|---|---|
| redline 三 gate | **自动（提交链内）** | in_process_gate_registry enabled:true，每次 commit 经网关触发 |
| runtime LLM 拦截器 | **自动（解释器级）** | sitecustomize.py 启动引导，ZEPHYR_RUNTIME_GATE=0 才关 |
| perceive 内监 | **自动（事件挂载）** | 零定时器，全部挂既有探测器事件源 |
| perceive 外扫节拍 | **锁定（手动）** | T3 双前置未解锁，施工项 7 未点火 |
| monthly checkup | **手动 CLI** | [STARTUP] manual，高模型维护班人工开会话执行（降级路线） |
| order_daemon | **事件驱动·无常驻实例** | 设计常驻但无启动登记/无进程；胜者事件当前零产 |
| heritage 回流 | **手动登记制** | 表 0 行，零自动写入方 |
| comparator 考场 | **手动 CLI** | experiment_store CLI --verify/--deploy，零部署零流量 |
| intake 入库闸 | **事件/调用触发** | 有 6 行真数据=曾通水；无常驻 |
| DDL 部署类（apply_*） | **手动一次性** | 幂等脚本，人为执行 |

**结论：AI 层当前"自动常驻"的只有两处半——redline 三 gate（提交链内）、runtime LLM 拦截器（解释器级）、perceive 内监（挂既有事件源）。进化主循环（外扫→收集→清洗→对比→排产→切换→传承）全链为"件就绪、阀未开"的手动/锁定态。**

## 五、堵点与病灶

1. **63 件 staged 未落 HEAD**（含 8/9 族全部代码）：现象=git ls-tree HEAD 仅 intake 族 9 件｜根因=ailayer 战役 187 件 v4 批 enqueue 后撞主区删除事态停手（LEDGER_final.md [20:4x]）｜修法=队列畅通后按 landing_files_v4.txt 逐件对账 commit｜工作量=1 批次｜**非本车道可修**（M4 只读红线）
2. **ai_compare/ai_tools 两 schema 未部署**：现象=information_schema 无记录｜根因=施工批 PG 只读纪律，--deploy 等 Owner 点火｜修法=Owner 门位批准后跑 `python -m zephyr.ai_layer.comparator.experiment_store --deploy` 与 usage_stats --deploy｜属本车道建议项（施工须申请）
3. **heritage 9 表零数据**：回流闭环未通水，L1 先验/L5 祖先分支消费面全饿｜修法=首个真实工单闭环后回填种子数据
4. **ai_intake_test_smoke/schema 残留**：测试隔离违规残留两 schema｜修法=RULE-DATA-OPS 三步验证后 DROP（破坏性操作走 Owner 门）
5. **矿脉三挂点缺位**：P1_final_report 宣称"depgraph 尾+align_all 尾 vein 再生钩子三件 staged"，实测 `scripts/governance/generate_project_depgraph.py` 与 `align_all.py`（d5_architecture/generators/）均无 gen_search_veins 引用——挂点件未在当前盘面（可能在 v4 批外或随事态丢失），月检 vein_coverage 段将恒显"产物缺失"注记

## 六、自审闸三态

**待挖→挖干可施工（代码面）/待裁（落地与部署面）**：
- 六向台账每向有 file:line 或可复跑命令输出 ✅
- 子模块 9 族 48 .py 逐一 ls+capability 卡交叉验证 ✅
- 三态结论：**代码完备性=挖干可施工；HEAD 落地+PG 部署+常驻点火=待裁**（队列畅通广播属总筹/Owner；PG DDL 部署属 high 门位）

## 七、复核命令

```bash
ls src/zephyr/ai_layer/                                    # 9 子包
python -c "import zephyr.ai_layer.redline.sev_router"       # redline 真身
git ls-tree -r HEAD --name-only src/zephyr/ai_layer | wc -l # HEAD=9
git status --porcelain src/zephyr/ai_layer | grep -c "^A"   # staged=63
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(read_only=True); cur=c.cursor(); cur.execute(\"SELECT table_schema,count(*) FROM information_schema.tables WHERE table_schema LIKE 'ai%' GROUP BY 1\"); print(cur.fetchall()); c.close()"
sed -n '707,725p' docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml
```
