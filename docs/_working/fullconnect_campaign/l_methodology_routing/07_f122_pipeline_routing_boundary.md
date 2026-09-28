---
ttl: task_bound
title: L12 案卷 F122 — 管线路由 M1-M11（partial：两物正交+命名冲突+M5 补挖波新认领面）
session: zc-l12-20260927
---

# F122 管线路由 M1-M11（M 段横切 X7，骨架态=partial/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | M0 待裁项 24（"待裁：M4（Agent 编排）或 M5（调度）边界"原文，`00_skeleton_fullflow.md:161`）；总筹初步口径"M4M5 互引"（orchestration :35）；代码级边界真源=AUDIT-08（pipeline_orchestrator.py :19-24 + ct_pipe_routing.py :23-24） |
| 下游消费 | 唯一生产消费方=src/zephyr/trading/auto_runtime_core.py（:65/:1103 PipelineOrchestrator 挂 TaskQueue dispatch handler，300s 轮询；:1119 BlueprintWatcher 另挂）——运行宿主=F71 AutoRuntime Core，**既非 M4 也非 M5** |
| 自动化触发 | 编排侧=进程内 300s 轮询（非计划任务，宿主不活=整链 idle）；选读路由侧=零计划任务/零 DataScheduler 槽/零 cron，纯同步查表（M5 补挖波 §3·5 实测） |
| 真源与注册表 | config/blueprint_routing.yaml（30 routes，module_id=MOD-INF-002，[DOMAIN] D_INFRA_RUNTIME，Human-Gated"路由映射变更=关键架构变更" :15）｜src/zephyr/integration/pipeline_orchestrator.py（MOD-INF-009，D_INTEGRATION，production）｜capability 卡 data/capability_cards/pipeline_orchestrator.yaml（MOD-INF-035，requires_human=true） |
| 门禁与质量尺 | blueprint_routing 变更=Human-Gated；M10 豁免注记在 orchestrator 头（periodic_profile while+sleep 四要素完整，ARCH-BENCH-LEAK-001）；MODIFY-GUARD=no structural changes without owner approval |
| 当前运行状态 | **partial（边界之争未裁+命名冲突未消）**：两物本正交、30 路由在册、编排件 production；但"M4/M5 边界"待裁+CT-Pipe M1-M11 与挖矿车道 M1-M8 同名异义未消歧 |

## 二、子模块三级枚举（两正交物 → 属性 → 登记面）

1. **选读路由侧** config/blueprint_routing.yaml（828 行，R001-R030，priority 1-100）：scope（pre_change/post_change/always）+safety（L/M/H）+fallback（keyword_count_then_priority，min_keyword_hits=1）+agent_hints（enabled=false，Phase_3 设计态未启）；消费方=integration/mcp/blueprint_search_server.py（:84 ROUTING_YAML_PATH、错误契约 ZA-BPS-0001 fail-soft）+pipeline_roadmap.py :505-509（MOD-CONTEXT_ENGINE config_consume ✅）
2. **运行态编排侧** pipeline_orchestrator.py + infrastructure/pipeline/ 件族：pipeline_lock/preemption_manager（priority_cutoff="P2"）/models（retry_max≤3、wait_before_retry_s=300、periodic_profile_interval_s=3600）/circuit_breaker_manager/dead_letter_queue/backpressure_manager/cost_tracker/model_router/routing_plugins/pipeline_agent_bridge/pipeline_roadmap/ct_pipe_routing；调度宿主=auto_runtime_core :1096-1116（_BootSubsystemRegistrar→set_dispatch_handler→start_polling 300s）
3. **登记面**：TDM/strategy_production_map grep "pipeline_orchestrator|blueprint_routing|管线路由"=**零命中**（本日复现）——M1-M11 管线不在任何业务图挂轴；capability 卡挂 F91 能力反查族（M4 资产名下）；域册双域 D_INFRA_RUNTIME（路由表）+D_INTEGRATION（编排器）；M5 补挖波读出 **4 条 Backlog 调度依赖**（pipeline_roadmap.py :511-550：反馈重路由/编排-分派闭环/锁等待转延迟队列/容量准入预算扣减）

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| blueprint_routing.yaml | **已接线（选读面 built）** | 30 routes 本日复现；MCP 消费方在册；Human-Gated 属性在头注 |
| pipeline_orchestrator.py | **码成宿主缺位（半接线）** | 件 production+测试在册（CONSUMERS 自声明）；宿主 auto_runtime_core 今日是否在跑=F71 域态（M5 补挖波："今日宿主不活＝整链 idle"） |
| M4 认领 | **零认领（维持）** | m4_ai_layer/ 四册+接续收口_20260925/ 三册 grep 零命中（本日复现） |
| M5 认领 | **已认领（新事实）** | m5_scheduling/90_backfill_wave.md（立册 09-25 23:4x）§3·5 补挖管线路由调度属性，给出 R1 建议方案 a："选读面（priority/scope/fallback）归 M4、分派面（触发/锁/抢占/重试/容量）归 M5，交叉轴=pipeline_roadmap Dependency 表" |

### M0 待裁内容原样转录（`00_skeleton_fullflow.md:161`）

> | 24 | 管线路由 M1-M11 | config/blueprint_routing.yaml 30 条+pipeline_orchestrator | 待裁：M4（Agent 编排）或 M5（调度）边界 |

总筹初步口径（orchestration :35）："管线路由 M4M5 互引"。

**影响面**：①命名冲突未消——pipeline_orchestrator 的 M1-M11 是 AI 编码管线段（A 区 M1-M5 生产/B 区 M6-M11 审计），与挖矿车道 M1-M8 同名异义；总册 F122 行下游写"Agent 编排"本身即被字面牵引；②4 条 Backlog 调度依赖无主（反馈重路由/编排-分派闭环/延迟队列/容量准入）；③30 路由 Human-Gated 语义（变更=架构变更）无 risk_tier 行（high 域语义、tier 册未登记）。

## 骨架勘误

1. **"双方零认领"已失效**：09-25 补裁证据册 §四.1 判"M4/M5 两册零认领——边界之争是骨架期纸面问题"；同日 23:4x 落盘的 M5 补挖波 §3·5 **已实际认领并给出归属细则建议（R1·方案 a）**——M4 至今仍零认领，"边界之争"已单向变成"M5 主张 vs M4 沉默"。本卷按最新盘面改判：M5=已认领（附待裁 R1），M4=零认领。
2. 总册 F122 行下游"Agent 编排"与 M0 互引裁语并存，且未录入 AUDIT-08 正交边界——两物一行的写法本身在制造"M4/M5 二选一"伪命题；建议 F122 行拆注"选读路由表+CT-PIPE 编排两正交物"。
3. 域册 domain 字段：blueprint_routing.yaml 实际以头注 `[DOMAIN] D_INFRA_RUNTIME` 声明（yaml 键内无 domain_id 字段，程序化读取须取头注）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | M5 R1 归属细则待裁（a 二分/M5 整收+M4 消费方/维持互引不落判据；补挖波建议 a） | Owner 裁；裁语须同步写进总册 F122 行+M4/M5 册各一行+消歧命名（CT-Pipe M1-M11 禁与车道 M1-M8 裸并置） | P1 |
| 2 | 宿主活性（AutoRuntime Core 不跑则编排链 idle） | 归 F71 启动链处置，本环节挂互引 | P1 |
| 3 | 4 条 Backlog 调度依赖（反馈重路由/分派闭环/延迟队列/容量准入） | 随 R1 裁决归车道立卡；容量准入涉 Kill Switch 前置=门位候选 | P2 |
| 4 | 30 路由 Human-Gated 无 risk_tier 行 | 无论 R1 何解，随裁登记 risk_tier（high 语义） | P2 |
| 5 | agent_hints Phase_3 设计态未启 | 保持 disabled，升 Phase_3 时走 Human-Gated 通道 | P2 |

## 五、自审闸三态

**挖干（两物正交+登记面+认领态）**：30 路由/域册双域/消费方/零挂轴全部本日复现 ✅ M0 待裁 24 原文转录零改字 ✅；**待裁**：R1 归属细则（Owner）；宿主启动（F71 车道）；risk_tier 登记（随裁）。

## 六、复跑命令

```bash
python -c "import yaml;d=yaml.safe_load(open('config/blueprint_routing.yaml',encoding='utf-8'));print(len(d['routes']),d['module_id'])"  # 30 MOD-INF-002
sed -n '19,24p' src/zephyr/integration/pipeline_orchestrator.py       # AUDIT-08 正交自声明
grep -rn "PipelineOrchestrator" src/zephyr/trading/auto_runtime_core.py | head -3
grep -rln "管线路由\|pipeline_orchestrator\|blueprint_routing" docs/_working/fullflow_mining/m4_ai_layer/  # 应无输出
grep -c "管线路由" config/trading_decision_map.yaml config/strategy_production_map.yaml  # 0 0
grep -n "capability_id\|requires_human" data/capability_cards/pipeline_orchestrator.yaml | head -2
sed -n '126,159p' docs/_working/fullflow_mining/m5_scheduling/90_backfill_wave.md  # §3·5 M5 认领面
```
