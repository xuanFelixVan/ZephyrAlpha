---
created: 2026-09-28
ttl: task_bound
volume: 05_f100_adversarial_validation
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-f100-redblue-book-20260926
---

# 05 · F100 红蓝对抗（adversarial_validation：53 场景 + 44 条款 + 事件驱动触发）

> 车道 W4-B｜worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`｜零提交零入队｜只读取证。
> 派单=`00_skeleton/92_coverage_triage_20260926.md` §三（F100 判"真缺簿·全六向缺"）。
> 本册状态：**六向齐证**（每向给 file:line 或注册表行号），§一 挂 F100 认领锚。核心发现=**该门不在 gate_registry**（提交面零注册条目）＋**自动实跑受环境变量 fail-closed**（§四病灶 1/2）＋**ROOR 场景数与描述自相矛盾**（§四病灶 3）。

## 一、环节定义与边界

总册口径（`00_skeleton/00_全环节总册.md:175`）：F100 红蓝对抗｜攻击场景 53 + 宪法条款 44｜上游 —（总册未填）｜下游 F98（GateEngine 运行时门禁）｜真源=`src/zephyr/security/adversarial_validation/`｜总册标 built、P2、G4（K 段治理门禁）。

本册覆盖 F100
> 实证面=该包 28 个 .py（ls 实测，§三）＋两册 canonical 注册表（REG-RB-001/002）＋三处外部接线（boot_hooks / git_commit_gateway / gov_audit）。

总册"上游 —"判错：实测上游=F98 门禁达标事件（`boot_hooks.py:752` 注释"门禁达标时跑 TIER_1 对抗"）＋ commit 暂存区（`commit_trigger.detect_formal_files` :90）。属"上游/下游写反"型骨架笔误，回写建议见 §六末。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | ①**待验目标=正式化文件**：`commit_trigger.py:90 detect_formal_files(files)` 从 commit 暂存清单里挑"正式件"；②**场景真源**=`_scenario_registry.yaml`（53 条，ROOR REG-RB-001 :538-546 记 `maintenance: auto（red_blue_validator 场景加载器）`）；③**条款真源**=`_constitution_registry.yaml`（44 条，ROOR REG-RB-002 :548-556，`maintenance: auto（ConstitutionEngine 绕过学习）`，字段 article_id/derived_from/defense_action/applicable_gates）；④**AI 生成攻击面**=`ai_attack_generator.py`（自述 [CONSUMERS] :5 = game_day_runner/cold_start，即"蓝军自己长攻击"）；⑤开关输入=`config/flags.yaml:85-92`（见"当前运行状态"向） |
| 下游消费 | ①**运行时生命周期**：`src/zephyr/trading/lifecycle_manager.py:4` [DEPENDENCIES] 明列 `zephyr.security.adversarial_validation.game_day_runner`——AutoRuntime 核心直接消费；②**审计准入**：`src/zephyr/gov_audit/audit_admission_controller.py:73 "red-blue-validator": "zephyr.security.adversarial_validation"`（把红蓝器注册为审计准入的可信件）；`src/zephyr/gov_audit/cli.py:4` 与 `:154 from ...validator import RedBlueValidator`（审计 CLI 真调）；③**门禁引擎侧**：`src/zephyr/feedback_loop/gates/adversarial_validation.py:138` import 本包＋`src/zephyr/gov_enforcement/rule_enforcement/gate_engine/adversarial_validation.py:2`（module_id=MOD-GATE_ENGINE）；④**MCP 工具面**：`config/tool_inventory.yaml:1033-1038 - tool_id: mcp:red_blue_validator / entry_path: mcp://red_blue_validator`，包内 `mcp_endpoints.py` 承载；⑤**绕过学习回写**：`bypass_recorder.py`（[CONSUMERS] :5 = validator/convergence_checker/escalation-engine）→ 写回 `_constitution_registry.yaml`（ROOR 记为 auto 维护方）；⑥**蓝图路由**：`config/blueprint_routing.yaml:714 - "src/zephyr/autonomy_perm/red_blue_validator/**"`——**注意**：路由表指向的是另一条历史路径 `autonomy_perm/red_blue_validator`，与本包并存（病灶 4） |
| 自动化触发 | **事件驱动，非 cron**（符合宪法 §9.3"reconciler 必事件触发"）：①常驻消费线程=`src/zephyr/trading/boot_hooks.py:755-757 from ...commit_trigger import RedBlueTriggerConsumer` → `RedBlueTriggerConsumer().start()`（注释 :748-750 原文"红蓝对抗提交触发消费线程 (MOD-INF-030 事件驱动)：daemon 线程轮询 data/red_blue/trigger_queue/，门禁达标时跑 TIER_1 对抗。就位+门禁激活：始终启动；ZEPHYR_RED_BLUE_AUTO_ENABLED!=1 时只 log 不实跑"）；②队列真源=`data/red_blue/trigger_queue/`，接口见 `commit_trigger.py:188 queue_dir` / `:197 drain_queue` / `:221 process_one` / `:256 _on_trigger_queued(event)`；3**GameDay 排程**=`game_day_scheduler.py`（`GameDayScheduler`/`ScheduleConflictError`，:74 注释"事件入口真源=同包 commit_trigger.py"，:38 锚定 REPO_ROOT 修 CWD 相对路径 bug）→ 由 `game_day_runner.py` 执行；④旁路桥=`validator_event_bridge.py`，在 boot_hooks 中以 **`"F30 validator_event_bridge"`** 注册名挂接（`boot_hooks.py:222`）；⑤**无 Windows 计划任务**（本包不注册 schtasks，触发全在进程内事件/线程）。 |
| 真源与注册表 | ROOR 两条：**REG-RB-001 攻击场景注册表**（`docs/registry_of_registries.yaml:538-546`，physical_path=`src/.../_scenario_registry.yaml`，format yaml，maintenance auto，entry_count **53**，status active）＋ **REG-RB-002 Constitution 条款注册表**（:548-556，entry_count **44**）。其它真源：`config/flags.yaml:85 red_blue_validator`（主开关册）、`config/tool_inventory.yaml:1033`（MCP 工具册）、蓝图 `docs/03_modules/_cross_layer/gate_engine/blueprint.md §adversarial_validation`（由 `feedback_loop/gates/adversarial_validation.py:1` 与 `gate_engine/adversarial_validation.py:1` 双指）、MOD-INF-030（boot_hooks 注释口径）、MOD 挖矿真源 `scripts/construction/_e2e_deep.py:59 ("MOD-INF-030", "zephyr.shared._cross_layer.red_blue_validator", [])`。⚠ **`gate_registry.yaml` 零条 adversarial/red-blue 条目**（实测 grep 无命中）→ 本环节无机读门禁注册面（病灶 1） |
| 门禁与质量尺 | 拦什么：**不是拦 commit**，而是"门禁达标后跑对抗、对抗结论回写条款册"（`boot_hooks.py:750` 口径）。实际存在的自锁三件：`circuit_breaker.py`（熔断）、`blast_radius.py`（爆炸半径，[CONSUMERS] validator/injection_engine）、`constitution_guard.py`（条款守卫，validator/convergence_checker 消费）；收敛判据=`convergence_checker.py`；兜底清场=`cleanup.py`；冷启=`cold_start.py`；常驻监控=`async_monitor.py`（[CONSUMERS] cli/mcp_endpoints）。测试面（[TESTS] 锚在）：`tests/safety/test_commit_trigger.py`、`tests/governance/rule_enforcement/gate_engine/test_adversarial_validation_gate.py`（实测两文件在盘）。**是否真跑（关键）**：`commit_trigger.py:31` 原文"ZEPHYR_RED_BLUE_AUTO_ENABLED=1 时才实跑，否则只 log + 清队列（**fail-closed**）"——该 env 是否被置 1 **本车道未取到生产设置证据** → 自动实跑面判"未验证"，**不称装饰**（消费者线程确实被 boot 起来，队列确实有货，见下一向），亦**不称在跑** |
| 当前运行状态 | **黄**（四态拆解）：①**接线=绿**：主仓 `data/red_blue/trigger_queue/` 有真实队列文件（实测 `ls` 得 `1785751827_d07f930e.json`、`1785751862_7816ea42.json`、`1785756189_b0749323.json`）→ 生产者侧真发生；②**开关=黄**：`config/flags.yaml:86 enabled: true`、`:88 auto_game_day: true`、`:89 ai_attack_generation: true`、`:90 tier_6_advanced: true`、`:91 blind_test_mode: false`、`:92 constitution_auto_approve: false`（→ 条款自动批准**关**，符合"不自我加冕"）；③**实跑=未验证**：env `ZEPHYR_RED_BLUE_AUTO_ENABLED` 置位无证据；④**worktree 面≠生产面**：本 worktree 无 `data/red_blue/`（runtime 产物不随 git 走），据 worktree 判"零触发"＝假红，已在病灶 5 立防呆。可复跑命令见 §七第 1/2/3 条 |

## 三、子模块清单（`ls` 全量 28 件 + `grep` [CONSUMERS] 交叉 + 注册表交叉）

**3.1 编排与入口（5）**：`__init__.py`（re-export 面，:159/:136 登记 commit_trigger/game_day_scheduler）｜`__main__.py`（[CONSUMERS] :5 "End users; CI/CD"）｜`cli.py`（:4 [DEPENDENCIES] 全串 validator/scenario_loader/models/game_day_runner/game_day_scheduler/convergence_checker/cold_start）｜`mcp_endpoints.py`｜`validator.py`（RedBlueValidator，被 gov_audit/cli.py:154 直调）

**3.2 对抗执行（6）**：`game_day_runner.py`（被 lifecycle_manager 消费）｜`game_day_scheduler.py`（GameDayScheduler/ScheduleConflictError）｜`defense_runner.py`｜`injection_engine.py`｜`ai_attack_generator.py`｜`cold_start.py`

**3.3 触发与事件（4）**：`commit_trigger.py`（RedBlueTriggerConsumer，队列消费＋fail-closed）｜`validator_event_bridge.py`（boot_hooks 注册名 F30）｜`async_monitor.py`｜`steady_state.py`

**3.4 宪法与学习（4）**：`constitution_engine.py`（:5 [CONSUMERS] constitution_guard/bypass_recorder）｜`constitution_guard.py`｜`bypass_recorder.py`（绕过→条款回写）｜`convergence_checker.py`

**3.5 安全自锁（5）**：`circuit_breaker.py`｜`blast_radius.py`｜`cleanup.py`｜`attack_registry.py`（:5 "见蓝图 §4 接口契约"）｜`scenario_loader.py`

**3.6 数据与模型（4）**：`models.py`｜`_scenario_registry.yaml`（53 条，ROOR REG-RB-001）｜`_constitution_registry.yaml`（44 条，ROOR REG-RB-002）｜`__pycache__`

**3.7 三源交叉结论**：ls 28 件全覆盖；grep [CONSUMERS] 锚为**包内自述**（属"设计声明"级证据，非调用实证）；实证调用来自包外 6 处（boot_hooks:755、lifecycle_manager:4、gov_audit/cli:154、audit_admission_controller:73、feedback_loop/gates:138、gate_engine/adversarial_validation:2）。**残余未证件**：`steady_state.py`、`attack_registry.py`、`mcp_endpoints.py` 的**包外**调用方未反查（限量取证），故 §三 判"清单穷尽／逐件消费面半穷尽"。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | **该门在 `gate_registry.yaml` 零注册**（grep adversarial/red_blue 无命中），而 `MOD-GATE_ENGINE` 蓝图侧确有 `gate_engine/adversarial_validation.py` 一份门件 | 双通道并存：门件走 rule_enforcement 的**规则 YAML 面**，不进 gate_registry 的**pre-commit 机读面**；ROOR 亦无对应登记 | 二案（待裁，不并）：①在 gate_registry 增一条 `GATE-RED-BLUE` 并声明 `own_scope`；②显式登记"红蓝不进 pre-commit，属 post-commit/运行时门"，并加一条"门件 ↔ gate_registry 覆盖差"漂移检测 | 1（①）/0.5（②） | 否（gate_registry=热册且 commit_gates 在途禁触） |
| 2 | 自动实跑被 env `ZEPHYR_RED_BLUE_AUTO_ENABLED` fail-closed（`commit_trigger.py:31/84/169`），而 flags.yaml 已 `enabled: true`＋`auto_game_day: true` | 两层开关（flags 与 env）语义重叠、真源方向不清；env 未在任何仓内文件里置 1（RULE-SECRETS 面 env 属外部注入） | 把"是否实跑"收归 flags 单真源，env 仅作临时覆盖；或在 `SECRETS.md`/部署脚本登记该 env 的出厂值 | 0.5 | 否（flags.yaml 是本车道禁触热件，§指挥册一之4） |
| 3 | **计数三源自相矛盾**：ROOR REG-RB-001 `entry_count: 53`，同条目 description 却写"**24 个**红白对抗攻击场景"；本车道实测 `grep -c "id:" _scenario_registry.yaml`=55、`_constitution_registry.yaml`=46（≠ROOR 的 53/44） | 违反宪法 §9.5"静态清单禁手工维护"：计数写进散文＋计数与条目双写；`grep -c "id:"` 口径本身也含嵌套 id（非权威尺） | 以生成器口径重算（ROOR 自述 maintenance=auto 者应由加载器回写条目数）；把 53/44 只留在字段、删除散文中的"24 个"；本册**不改 ROOR**，只登记 | 0.3 | 否（ROOR=热册，总筹单点写） |
| 4 | 同功能两条模块路径并存：`config/blueprint_routing.yaml:714` 指 `src/zephyr/autonomy_perm/red_blue_validator/**`，实测真身在 `src/zephyr/security/adversarial_validation/`；`scripts/construction/_e2e_deep.py:59` 又写第三种路径 `zephyr.shared._cross_layer.red_blue_validator` | 历史改名/搬迁后路由表与 e2e 清单未同步（同病灶型：F103 的路径漂移） | 三处路径归一 + `generate_project_depgraph.py --force` 重建（宪法 §9.10） | 0.5 | 可（出清单，不改） |
| 5 | **判态防呆**：worktree 无 `data/red_blue/` ⇒ 若在 worktree 里跑状态探针会得到"零触发"假红 | 并行 worktree 只带 git 面，不带 runtime 面（本车道实测发生） | 本环节所有 runtime 判据 MUST 在主仓 `D:/ZephyrAlpha` 取；已写入 §七命令注释 | 0 | 已修（本册内） |

## 五、内收与合并机会（四判据）

- **同真源可派生→必并**：场景数/条款数（53/44）应从两册 YAML 派生，须从 ROOR description 散文与 `entry_count` 字段的双写中收敛为**仅字段**（病灶 3）。
- **零触发零消费→退役**：`steady_state.py`/`attack_registry.py`/`mcp_endpoints.py` 的包外消费未证（§3.7）→ 先反查再判；`ai_attack_generator` 的 `tier_6_advanced`、`blind_test_mode=false` 关闭面若长期为 false，按"零触发"出退役候选（**只登记不删**，注册表净删=Owner 门位）。
- **同域重复簇→收敛唯一**：三套"红蓝"命名并存（`security/adversarial_validation`、`autonomy_perm/red_blue_validator`、`shared._cross_layer.red_blue_validator`）＋门件两份（`feedback_loop/gates/adversarial_validation.py` 与 `gov_enforcement/rule_enforcement/gate_engine/adversarial_validation.py`，同一 module_id MOD-GATE_ENGINE 两处实现）→ 同域同对象，**收敛唯一**。
- **跨域不同对象→不并**：本包与 F103 `clone_guard` 的"对抗/审计"不同对象（防克隆 vs 防绕过）；与 `tests/federated_learning/test_fl_adversarial_validation.py` 所指联邦学习对抗（同名异域）**不并**。

## 六、自审闸三态

**判：挖干可施工**（六向齐证；每向有 file:line 或 ROOR 行号）。

但以下三项**不随本册升格为已闭**，是 F100 从"partial"到"built"的真差值：

1. **自动实跑证据缺**——最小观测量：`ZEPHYR_RED_BLUE_AUTO_ENABLED` 的置位处（部署脚本/PS1/secrets 白名单）＋一条 `RedBlueTriggerConsumer` 实跑并产出对抗结论的记录（队列文件被 drain 的日志）。二者皆无则本环节按宪法四要素只能判"半通"。
2. **gate 注册面缺**（病灶 1）——在 gate_registry 或"运行时门"清单中有名之前，F100 不能被 F98 一侧的消费链索引到。
3. **§3.7 三件包外消费未反查**。

**待裁（已写入 `m3_governance/pending_rulings.md`）**：病灶 1（门注册二案）、病灶 2（双层开关真源归一，涉 flags 热件）、病灶 4（三路径归一）。

**回写总册建议**（不自行改总册）：`00_全环节总册.md:175` ①上游列"—"改为"F98 门禁达标事件 + commit 暂存区"；②`built` 改 **`partial`**，备注"自动实跑 env fail-closed 且置位无证据；未进 gate_registry"；③场景/条款数以 ROOR 字段为准（勿抄散文"24 个"）。

## 七、复核命令

> ⚠ 第 2/3 条 MUST 在**主仓** `D:/ZephyrAlpha` 执行（worktree 无 runtime 面，见病灶 5）。

```bash
# 1) 六向锚点一次读全（flags 两层开关 + 事件触发 + fail-closed 原文）
sed -n '85,92p' config/flags.yaml
sed -n '748,760p' src/zephyr/trading/boot_hooks.py
sed -n '28,34p;80,92p;165,172p' src/zephyr/security/adversarial_validation/commit_trigger.py

# 2) 运行态（主仓）：队列是否真有货 + env 是否置位
ls -la data/red_blue/trigger_queue/ | head ; python -c "import os;print(repr(os.environ.get('ZEPHYR_RED_BLUE_AUTO_ENABLED')))"

# 3) 门注册面缺失自证（预期=零命中）+ ROOR 两条登记
grep -n -i "adversarial\|red.blue" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | wc -l
sed -n '538,556p' docs/registry_of_registries.yaml

# 4) 计数三源对照（53/44 vs 散文"24 个" vs grep 原始行数）
grep -c "id:" src/zephyr/security/adversarial_validation/_scenario_registry.yaml
grep -c "id:" src/zephyr/security/adversarial_validation/_constitution_registry.yaml
grep -rn "24 个红白\|24 个红" docs/registry_of_registries.yaml

# 5) 路径归一待办自证（三处同功能异路径）
grep -rn "autonomy_perm/red_blue_validator\|_cross_layer.red_blue_validator\|security.adversarial_validation" --include=*.py --include=*.yaml src/ config/ scripts/ | wc -l

# 6) 测试面
python -m pytest tests/safety/test_commit_trigger.py tests/governance/rule_enforcement/gate_engine/test_adversarial_validation_gate.py -q -o cache_dir=.runtime/tmp/pytest_cache_w4b
```
