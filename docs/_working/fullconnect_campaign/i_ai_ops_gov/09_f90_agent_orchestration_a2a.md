---
ttl: task_bound
title: L09 案卷 F90 — Agent 编排与 A2A（orchestrator/autonomy_core 59 技能/MCP 13 server/管线编排）
session: zc-l09-20260927
---

# F90 Agent 编排与 A2A（J 段 A5，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | config/blueprint_routing.yaml（30 条路由，本日 grep 计数=30，与骨架口径一致）；M1-M11 管线编排（pipeline_orchestrator.py 实存） |
| 下游消费 | 全链 Agent 面（编排为横切底板）；skills 消费=autonomy_core/skills/ 59 .py+skill-registry.yaml |
| 自动化触发 | autonomy_core 带 __main__.py（可宿主）；触发路由=trigger_router.py；探针时无 autonomy_core 实例在跑（按需宿主态） |
| 真源与注册表 | src/zephyr/orchestrator/（agent_orchestrator.py 等 20+ 条目）；src/zephyr/autonomy_core/（30+ 条目）；src/zephyr/integration/mcp/ 13 只 *_server.py |
| 门禁与质量尺 | autonomy_boundary_gate.py/non_ai_boundary_guard.py/per_agent_gate.py/self_evolution_fidelity_gate.py（边界门四件实扫）；kill_switch_orchestrator.py+killswitch_response_levels.py（与 F61 KillSwitch 协同） |
| 当前运行状态 | **绿（件面）**：三包全量在盘+技能注册表+13 MCP server；宿主按需拉起（P2 支线态，无生产常驻需求证据） |

## 二、子模块三级枚举

1. `src/zephyr/orchestrator/`：agent_orchestrator.py/layered_command_chain.py/task_queue.py/rollback_manager.py/hallucination_detector.py/global_state_aggregator.py/file_task_mapper.py/deferred_queue.py+core/contracts/execution/fault_tolerance/governance/lifecycle/quality/resilience 八子目录+两 skill（agent_coordination/task_orchestration）。
2. `src/zephyr/autonomy_core/`：__main__ 宿主/trigger_router/phase_planner/spec_engine/prompt_registry/autonomy_level_registry/skill_rbac_registry/skill_attention/skill_breakage_checker/skill_cache_provider/all_skill_modules/file_autoregister/ide_watcher/agentic_drift_guard/drift_semantic_reviewer/ai_ops_autonomy_card/embedding_provider_adapter/progressive_disclosure_injector/agent_observability+agents/context/integration/module_factory/skills 子目录；skills/ 内 **59 .py+skill-registry.yaml+_skill_cache/_durable_state 持久面**。
3. `src/zephyr/integration/mcp/`：13 server（blueprint_search/doc_guard/gate_engine+base/_base 等本日 ls 计数）+client_discovery/audit_logger/error_codes；`pipeline_orchestrator.py`+`config/blueprint_routing.yaml`（30 路由）=M1-M11 管线编排面（F122 交叉，不重挖）。

## 三、接线四态独立复核

- **A2A/MCP=已接线**：13 server+client_discovery 双向面在盘；GATE-MCP 在册（wiring_gap §1.6 门清单内）。
- **技能面=已接线（59 技能+注册表+缓存持久化）**：骨架"skills 60+"与实扫 59 差 1（口径=含 registry yaml 则 60+；勘误记数漂移）。
- **宿主=按需态**：autonomy_core __main__ 可独立宿主，探针无实例——P2 支线无生产常驻义务，判"设计内按需"非缺口。
- **边界门=四件在位**：non_ai_boundary/autonomy_boundary/per_agent/fidelity 与 F88 LSG、F61 KillSwitch 构成三层协同（引用级，不重判）。

## 骨架勘误

1. 技能计数：骨架"skills 60+"/本日实扫 59 .py——计数口径差 1（.py 数 vs 含注册表条目数），按宪法 §4.3 应以注册表条目字段为准，登记待字段化。
2. 其余无勘误：MCP 13 server、路由 30 条均与实扫一致。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 59 技能的 RBAC/缓存一致性无机检（skill_rbac_registry vs skill-registry.yaml 双账） | 抽查对账或入 F81 health 面 | P2 |
| 2 | GATE-MCP 在"疑似判据失效 43 门"名单（wiring_gap §1.6，无配对测试） | 随 43 门红样采集批处置 | P2 |
| 3 | autonomy_core 宿主化场景未登记（何时该拉起） | 登记触发场景进资源册或声明 manual-only | P2 |

## 五、自审闸三态

**挖干（三包目录级穷举+计数双核）✅；无待裁；待挖（技能逐件深挖与 A2A 协议面——P2 支线，本卷有意不展开，登记即可）。**

## 六、复跑命令

```bash
ls src/zephyr/autonomy_core/skills/*.py | wc -l       # 59
ls src/zephyr/integration/mcp/*_server.py | wc -l     # 13
grep -c "route_id\|- id:" config/blueprint_routing.yaml  # 30
ls src/zephyr/orchestrator/ | head -8
```
