---
ttl: task_bound
session: st-ailayer-fullflow-sc
creation_token: m5sc-order-daemon-wiring-20260925
---

# M5 补挖分册 05：F82 order_daemon 未接线取证——六断点清单

> 总册 F82（P0 断链点"order_daemon 建成未接线"）专项取证。主波 02 册 §六/04 册 S4 一句话结论（"全仓无生产 spawn 点"）的展开与完链。
> 证据：order_daemon.py（360 行）全读+全仓 grep（src/scripts/config/tests）+盘面实测，2026-09-25。只读挖矿。

## 一、设计链路（什么该发生）
```
L4/L2 胜者落库（库内=INTAKE_E2_HANDOFF 链；库外=verdict='win' 直达）
  └─emit→ evolution_winner_due → SchedulingJournal
          (.runtime/ai_scheduling/pending_events.jsonl，先落盘后消费)
  └─事件触发→ OrderDaemon.process_once()（零定时器零轮询，宪法 §9.3）
       ├─ 单例锁（belt 同款 PID+TTL600s+僵尸检测）+last_read_offset 断点续读
       ├─ build_task_order：胜者证据包→任务书附录 A schema v0（DESIGN §2.1 逐字段）
       ├─ 必填机检缺→held_incomplete+堵点本（禁静默）；criteria_hash 缺/错→拒派（L4 §2.3①）
       └─ sink 落库 → ai_scheduling.ai_work_order（PG 独立 schema，七态状态机）
  └─→ router 三证据分流（R1 作用域/R2 风险/R3 自指；骨架级→Owner 门位）
  └─→ dispatcher 两问打分+四读数配额+E0 拉式问闸 → order_dispatch_due → 施工队
  └─回执线→ work_order_shadow_ready(L6)/closed_due(L7)/dead(L2 回传)
```

## 二、六断点清单（逐段取证；✅=已备件，❌=断点）
| # | 断点 | 证据 | 定性 |
|---|------|------|------|
| B1 | **胜者侧零 emit**：`evolution_winner_due` 全仓唯一出现=KIND 定义+注释（scheduling_events.py:38/84），**零生产 emit 调用方**；上游本体的胜者落库件（SF 车道 E9 归因 F28）自身未闭环（总册红叉位） | grep 全 src/scripts/config | ❌ 结构断（最上游） |
| B2 | **journal 零生产实例**：`SchedulingJournal(` 仅 tests 两处（test_scheduling_events.py:27/conftest.py:28）；`.runtime/ai_scheduling/` 目录不存在 | grep+ls 实测 | ❌ 生产态零实例 |
| B3 | **守护零 spawn**：order_daemon.py 无 `__main__`；无 register 脚本、无计划任务、无任何生产调用 `OrderDaemon(`/`process_once`（仅包导出 __init__.py:38-43+测试） | grep+主波 01 册 49 任务全表反查 | ❌ 主波已录，本册完链 |
| B4 | **sink 缺省 dry-run**：`OrderDaemon.__init__` sink=None 缺省"只回执不落库"（order_daemon.py:257）；**工单持久化 sink writer 全仓无实现**；表结构真源在（apply_ai_layer_scheduling_ddl.py:87 `ai_work_order`，PG ai_scheduling schema，幂等 DDL+--verify），**部署 opt-in 未核**（DEPENDENCIES=get_depgraph_pg_connection） | 源读+grep | ❌ 半断（DDL 在/无 writer/未部署） |
| B5 | **下游挂接预留**：router/dispatcher/maturity 三件**已建成**（头注+测试全：三证据机检/两问打分/四读数/E0 问闸/T0 门闸），但 [CONSUMERS] 全部写"order_daemon 挂接"——挂接动作本身未发生；施工队侧（fresh worktree 会话自动派工）无消费实现 | router.py/dispatcher.py/maturity.py 头注 | ❌ 件齐线缺 |
| B6 | **回执线设计态**：work_order_shadow_ready/closed_due/dead 三 kind 消费方="L6/L7 卡实施时 register_handler"（scheduling_events.py:241-242 缺省消费体抛 no_consumer_yet 留队——缺消费者≠丢事件，语义安全） | 源读 | ❌ 按设计预留（非病） |

**已备件清单（✅，接线时零改造可用）**：policy 真源 `config/schedule_gate_policy.yaml`（9382B 在盘，maturity.py:64 fail-closed loader）；设计真源 `docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md`（§2.1 映射表/§2.4/§2.5/§2.7 全锁）；kill switch 探针复用 intake_events.probe_kill_switch（fail-closed）；毒丸 MAX_ATTEMPTS=3 留档；堵点本 `.runtime/audit/bottleneck_ledger.jsonl` append 件（append_bottleneck）。测试面：tests/ai_layer/scheduling/ 五件套全绿在册（order_daemon/events/router/dispatcher/ddl）。

## 三、接线工单序列（建议施工序，自上游向下游）
1. **W-B1（依赖外部）**：SF 车道 E9 归因件落地时，在胜者落库点 `journal.emit("evolution_winner_due", payload)`（payload 白名单见 scheduling_events.py PAYLOAD_REQUIRED_KEYS）。库外 win 直达路径同期补。**前置依赖 F27/F28 闭环，非本车道可单独完成**。
2. **W-B4a**：`apply_ai_layer_scheduling_ddl.py --verify`（只核不部署）确认表结构四件套；Owner 门位批部署（PG schema=生产流转）。
3. **W-B4b**：sink writer 小件（order_daemon sink 参数注入 PG writer，幂等键=order_id 全局唯一约束已在 DDL）。
4. **W-B3（待裁后）**：守护拉起形态二选一——
   - **选项 a（belt 同款，荐）**：注册探活式计划任务（PT5M：journal pending>0 且锁空闲→拉起一次性 `process_once` 进程；keep-list 登记）。这**不是给守护加 cron**，是 belt 已裁先例的机械复用：任务只做探测与拉起，消费体零轮询。
   - **选项 b（纯事件沿）**：胜者 emit 进程内联消费（emit 后直接 spawn process_once），无第二进程——要求 emit 方与消费方同机同仓（现状成立），但跨进程场景（E9 在他会话）需文件锁兜底，belt 单例锁已备。
   - 两选项均合规 §9.3（无 cron 驱动消费本体）；裁决点=是否接受"探活任务"这一形态。
5. **W-B5**：order_dispatch_due 消费挂接（dispatcher 入口接线）+施工队拉起件——依赖 W-B1~B4 全通，属 AI 层车道 L5 卡后续批次。
6. **B6 不动**：按设计等 L6/L7 卡。

## 四、六向台账（现状态）
- **上游输入**：应当=胜者落库事件；实际=零（B1）。
- **下游消费**：应当=sink→PG→router/dispatcher→施工队；实际=零消费（B4/B5），dry-run 回执仅测试可达。
- **自动化触发**：零——判据=**保持不存在**（主波 05 册 #11 行口径维持；接线前"不响=预期"）。
- **真源与注册表**：DESIGN.md（契约锁）；config/schedule_gate_policy.yaml（尺子）；apply_ai_layer_scheduling_ddl.py（表结构）；scheduling_events.py 头注（八 kind 契约）；MOD-INF-037 蓝图。
- **门禁与质量尺**：宪法 §9.3（零定时器）；INVARIANTS 全带（单例锁/断点续读/必填机检/criteria_hash 拒派/自我放大闸）；KillSwitch fail-closed；毒丸留档；owner_gate 骨架级必经 Owner（#374 门位族）。
- **当前运行状态：黄（预期内缺位）**。非静默失败——journal 从未有过事件，守护从未被期待在跑；风险在"有人以为它在守"（S4 原判词，维持）。

## 五、自审闸三态
**挖干可施工**：六断点逐条 file:line+grep 双源取证；已备件/缺件清单闭合；接线工单序列六步含依赖与门位标注。附待裁一项：W-B3 拉起形态 a/b（探活任务 vs 进程内联）需 Owner 裁——因涉 §9.3"探活任务"形态的先例边界（belt 先例存在但未明文覆盖 journal 类事件源）。
