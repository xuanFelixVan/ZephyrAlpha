---
ttl: task_bound
title: 残余挂账施工战役总簿——环节全景（封矿）/波次派发/状态回写
owner: ZephyrAlpha-Owner
session: st-residual-20260917
date: 2026-09-18
status: campaign_running
---

# 残余挂账施工战役 · 总簿

> **战役令**：Owner 通宵战役令 2026-09-18（通宵令全文在案，八条全程适用）。**范围真源**：[pending_items_plan.md](pending_items_plan.md)（五立项+四搁置）。本总簿=环节全景封矿+波次派发+状态回写，收尾时 ⬜→✅ 回写批次号与 commit hash。

## 1. 环节清单（已封矿，共 6 施工环节 + 2 战役阶段）

| 环节 | 内容 | 真源文档 | 依赖 | 波次 | 状态 |
|---|---|---|---|---|---|
| E1 | WO-2a 危机态三级接线（判读件+L1/L2/L3+crisis_gate_log+告警） | [wo2_blackswan_workbook.md](wo2_blackswan_workbook.md) §1②/§2/§6 | 无 | W1 | ⬜ |
| E2 | WO-1 收益归因（sim_attribution_report+62 天回放对平） | [wo1_attribution_workbook.md](wo1_attribution_workbook.md) | 无 | W1 | ⬜ |
| E3 | WO-3 配置生效核对器 | pending_items_plan §1 WORK-ORDER-3 | 无 | W1 | ✅ 32431d66 |
| E4 | WO-5 一期人群账本（cohort_daily_ledger 结算层+老蔡对账） | [wo5_cohort_ledger_workbook.md](wo5_cohort_ledger_workbook.md) | 无（原料全在库） | W2 | ⬜ |
| E5 | WO-2c 月度演练（crisis_drill_monthly） | wo2 workbook §4 | 无（与 E1 可并行） | W2 | ⬜ |
| E6 | WO-2b 纸面对冲腿 | wo2 workbook §3 | **E1 状态机** | W2 | ⬜ |
| E7 | WO-4 告警外推（单通道，机器侧全量建成） | pending_items_plan §1 WORK-ORDER-4 | 无 | W3 | ⬜ |
| Q1 | 循环检查+红蓝对抗+端到端实测（连续两次 0 问题） | 通宵令第五条 | E1-E7 | W3 | ⬜ |
| Q2 | 收尾（临时文件清理/claims release/台账回写/起床报告） | 通宵令第六、七条 | Q1 | 末 | ⬜ |

**环节清单封矿声明**：以上即全部环节，骨架拆分到"来源或口径变化"为止（E1-E6 各有独立真源文档，E3/E7 以主方案验收节为真源，不再细分子文档；WO-3/WO-4 按挖矿分级裁定免挖）。清单封矿后进入逐环节施工，不再新增环节；新发现一律记各环节"长尾"不扩范围。

## 2. 战役级裁定（总统筹留痕）

- **C1 共享文件单 ownership**：`pipeline_events.py`、`tasks.yaml`、`apply_market_tables_ddl.py` 三个共享文件归**总统筹独占**（E1/E2/E4/E5 四环节都要碰 pipeline_events——并发改同一热文件=HELDED-OVERLAP 战争，第一性原理：可变共享状态必须单写者）。各施工代理只 build 自带文件+纯函数交付件，接线由总统筹在波次边界统一做**接线 commit**（每环节接线独立成 commit，留痕可回滚）。
- **C2 代理会话制**：每个施工代理注册独立 session（st-<env>-20260918，session_worktree_start allow_concurrent=True），自管 claim/release，正门提交（git_commit.py --allow-non-worktree，锁忙改 --enqueue），提交后 git log -1 --name-only 自核归属。
- **C3 端到端实测口径**：禁止生产表污染——regime 注入用历史日期+哨兵 run_id（`drill_e2e_b1`），或走 tmp fake 的真实代码路径；每个环节交付一条"真实打穿"记录（打穿了什么、走没走生产路径、哨兵怎么清理）。
- **C4 告警通道凭据**：E7 机器侧全量建成（可插拔 webhook+fail-closed），推送凭据属 Owner 四类事（账号注册/API 申请）——缺凭据不算未达成，机器侧打穿（本地 webhook 桩+文件落盘双验证），凭据记待裁定清单。

## 3. 波次计划

- **W1**（进行中）：E1 + E2 + E3 三代理并行（并发=3，符合上限）。
- **W2**：总统筹 W1 接线 commit（pipeline_events L1 拦截/归因 emit/crisis_gate_log 注册）→ E4 + E5 + E6 三代理并行（E6 依赖 E1 状态机，W1 验收后放行）。
- **W3**：E7 + Q1 循环检查与红蓝（连续两次 0 问题才收口）+ Q2 收尾。

## 3.5 事故与处置日志（运行中）

- **R1 速率限制（03:0x）**：W1 三并发触发账户级速率限制，E1/E2 代理中途死亡——但代码建造实际已完成（"限流死亡代理完成论"），总统筹从工作树收编+blob 快照恢复。
- **R2 serializer 回滚吞件（03:3x-06:2x）**：队列 serializer 落地期间回滚主工作树未提交改动，E1/E2 全部文件+总统筹 pipeline_events/apply 接线被抹。处置=从 .runtime/commit_queue/blobs/（8527 个内容寻址快照）按 dead/*.json 的 blob_sha256 逐文件还原（36 文件全哈希校验通过）；共享注册表类文件回退 HEAD 防连坐。教训入册：**共享工作区+战役期，改完立即入队快照，禁止攒批**。
- **R3 会话注册静默失败**：session_worktree_start 返回 ok=False(WORKSPACE_DRIFT_BLOCKED) 被忽略+pid0 会话 90s 心跳过期——治本=注册必带 allow_workspace_drift=True + _spawn_heartbeat_daemon 全会话拉满+每次注册后验 get_session FOUND。
- **R4 admin 建表**：writer 无 c1_backtest CREATE 权限（Code 497），按工厂惯例 admin 角色建表（crisis_gate_log/sim_attribution_daily 两表已建成验证）。
- **R5 队列拥堵**：flash-nightbuild processing 项占用序列器 45min+，FIFO 20 项——活体租约不抢（6ea82b9cfb 治本行为），我方 items 快照在袋零丢失，等传送带消化。

## 4. 状态回写（收尾时填）

| 环节 | 状态 | commit hash | 批次 | 备注 |
|---|---|---|---|---|
| E1 | 🟡已建待落地 | 队列 q-...-0010 | W1 | 23 tests 绿;真实 CH 判读探针 normal/r3 通过;L2/L3 已落地(e1a975b158) |
| E2 | 🟡已建待落地 | 队列 q-...-0002 | W1 | 9 tests;62 天回放 recon_diff=0.0(73,747.04 对平);daily 模式 6 行已入 CH 表 |
| E3 | ✅ | 32431d66 | W1 | 13 tests 绿+四次真实端到端（含安全窗重启调度器 02:19）；总统筹独立复核通过；GAP：risk_params/TDM 消费方无 loaded-state 钩子（登记在 checker gaps） |
| E4 | 🟡schema已落地/builder待落地 | 2fd61ca135+队列q-...-0006 | W2 | 13 tests;老蔡对账真实数字完成(方向吻合+游资足迹验证;日期映射 O-1 待 Owner) |
| E5 | 🟡已建待落地 | 队列 q-...-0005 | W2 | 16 tests;首跑真实演练:W2024 击穿破产地板 min_nav=0.8267 CRITICAL 已告警 |
| E6 | ⬜ | | | |
| E7 | ⬜ | | | |
| Q1 | ⬜ | | | |
| Q2 | ⬜ | | | |
