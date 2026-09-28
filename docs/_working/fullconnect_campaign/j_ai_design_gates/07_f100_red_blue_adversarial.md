---
ttl: task_bound
title: F100 红蓝对抗——挖干案卷
session: zc-l10-20260927
---

# F100 · 红蓝对抗（攻击场景 53+宪法条款 44）

> 总册行（00_全环节总册.md:175）：built｜上游 —｜下游 F98｜P2｜G4
> 第一证据源：fullflow_mining/m3_governance/01_runtime_guards.md＋src/zephyr/security/adversarial_validation/

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 攻击场景册 _scenario_registry.yaml（MOD-INF-030）＋宪法条款册 _constitution_registry.yaml＋red_team_corpus.yaml（M3 01 §二引用） |
| 下游消费 | F98 门禁面（validator_event_bridge.py→门事件；commit_trigger.py→提交触发）＋game_day 演练产出 |
| 自动化触发 | game_day_scheduler.py＋async_monitor.py＋commit_trigger.py（事件/演练触发）；cold_start.py 自举 |
| 真源与注册表 | _scenario_registry.yaml：**本日 grep "  - scenario_id:" = 53（与总册一致）；册头字段 total_scenarios: 54（漂移）**；_constitution_registry.yaml：**本日 grep "  - article_id:" = 44（与总册一致）；册头字段 total_articles: 34（漂移）**——两册 last_updated 2026-06-26/2026-05-08 |
| 门禁与质量尺 | validator.py＋convergence_checker.py（收敛判据）＋circuit_breaker.py＋blast_radius.py（爆炸半径）＋bypass_recorder.py（绕过留痕） |
| 当前运行状态 | built（册+引擎件全在；蓝军 ai_attack_generator+injection_engine 在产） |

## 二、子模块三级枚举（本日 ls 实测，25 .py+2 册）

1. **场景与攻击面（红军）**：ai_attack_generator.py｜injection_engine.py｜attack_registry.py｜scenario_loader.py｜_scenario_registry.yaml（53 场景，RB-SCEN-001..，tier L1..，severity critical..，target_module llm-security 等）。
2. **防御与判据（蓝军）**：defense_runner.py｜validator.py｜constitution_engine.py｜constitution_guard.py｜_constitution_registry.yaml（44 条 CONST-001..）｜steady_state.py｜convergence_checker.py。
3. **演练编排**：game_day_runner.py｜game_day_scheduler.py｜async_monitor.py｜commit_trigger.py｜cold_start.py｜cleanup.py。
4. **风控与留痕**：circuit_breaker.py｜blast_radius.py｜bypass_recorder.py｜models.py｜validator_event_bridge.py（与门事件桥）｜mcp_endpoints.py｜cli.py｜__main__.py。
5. **关联测试面**：tests/agent_rbac/test_redteam_adversarial.py、test_adversarial_resilience.py、test_adversarial_agent_rbac.py、test_rbac_adversarial.py、tests/a2a/test_a2a_red_team.py（本日 find 实证；无 tests/adversarial_validation 专树）。

## 三、接线四态独立复核

- 总册判 **built**：成立（册/引擎/编排/风控四层全实存，场景 53+条款 44 复算与总册一致）。
- **骨架勘误（数册内漂移，非骨架错）**：两册头部的机生计数字段与实体数不符——total_scenarios: 54 vs 实体 53；total_articles: 34 vs 实体 44。宪法 §4.3"计数用字段不写死"要求字段可复算：字段失修=文档矛盾级隐患，须生成器重算字段（禁手工改数）。
- 下游接线：validator_event_bridge/commit_trigger 提供与 F98/提交链的挂点（模块级实证）；运行频度（game_day 实际点火记录）本卷未挖，归 Owner 演练排程。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | 两册计数字段漂移（54≠53、34≠44） | loader 装载时校验字段=实体数（fail-closed）+生成器重算 | P1 |
| G2 | 册 last_updated 陈旧（05-08/06-26，4 个月未更） | 场景/条款增补排程（对齐宪法 44 条演进） | P2 |
| G3 | 无专树测试（tests/adversarial_validation 缺位） | 关键件（validator/constitution_engine）配对测试 | P2 |
| G4 | 演练运行记录/战果台账未在本卷实证 | 归 Owner 演练排程面，挂起待裁 | P2 |

## 五、自审闸三态

**册与引擎=挖干可施工**（53/44 复算一致+25 件逐层实证）；**计数字段修正=本车道禁改（既有文件），登记待施工**；**演练频度=挂起**。

## 六、复跑命令

```bash
grep -c "  - scenario_id:" src/zephyr/security/adversarial_validation/_scenario_registry.yaml  # 53
grep -c "  - article_id:" src/zephyr/security/adversarial_validation/_constitution_registry.yaml # 44
grep -n "total_scenarios\|total_articles" src/zephyr/security/adversarial_validation/_*.yaml    # 漂移字段
ls src/zephyr/security/adversarial_validation/ | wc -l                                          # 包容量
```
