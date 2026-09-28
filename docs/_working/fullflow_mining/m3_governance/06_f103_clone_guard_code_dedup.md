---
created: 2026-09-28
ttl: task_bound
volume: 06_f103_clone_guard_code_dedup
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-f103-cloneguard-book-20260926
---

# 06 · F103 代码质量与克隆守卫（clone_guard 编排层 + code_dedup 引擎层）

> 车道 W4-B｜worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`｜零提交零入队｜只读取证＋写本簿，不改生产代码。
> 派单=`00_skeleton/92_coverage_triage_20260926.md` §三（F103 判"真缺簿·全六向缺"）＋§四第 4 条。
> 本册状态：**六向齐证**（§二 每向都有 file:line 或注册表行号），§一 挂 F103 认领锚。核心发现=**宪法宣称的 API 在盘上不存在**＋**同一枚 GATE-DEDUP 三处真源互斥**（§四病灶 1/2）。

## 一、环节定义与边界

总册口径（`00_skeleton/00_全环节总册.md:178`）：F103 代码质量与克隆守卫｜code_dedup + extract 级克隆无逃生｜上游 F98（GateEngine 运行时门禁）｜下游=施工｜真源=`src/zephyr/gov_code_quality/`、`clone_guard/`｜总册标 built、P2、G7。

本册覆盖 F103
> 机生对账尺认领锚，机生对账尺认领锚，判据=本行 F 号字面出现；实证面为下列两包，缺一即本行应撤锚）。

实测真源修正：总册写的 `clone_guard/` 是**裸相对名**，盘上唯一路径=`src/zephyr/clone_guard/`（9 件，编排层）；`src/zephyr/gov_code_quality/` 下只有一层子包 `code_dedup/`（60 件，引擎层）。二者是**同域双层**（编排 vs 引擎），非重复簇。边界：`capability_overlap_gate`（commit 侧消费方）、`create_guard`（新建文件守卫）不属本册，只作下游消费证据引用。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | ①staged 文件清单：`CloneGuardOrchestrator.check(staged_files)` `src/zephyr/clone_guard/orchestrator.py:316`——唯一 pre-commit 侧入口，入参即 git 暂存区 .py 清单（由 `capability_overlap_gate.py:337 _run_clone_guard_check(all_staged_py)` 供给）；②配置真源 `clone_guard.yml`（仓根）：`pre_commit.timeout_sec: 30`、`fail_on: extract`（注释原文"extract=3+副本硬阻断(必须合并), review=2副本警告"）→ 宪法"extract 级克隆无逃生"的**机生对应物就是这行**；③已确认重复对（acknowledged pairs）由 `orchestrator.py:168 _load_acknowledged_pairs(raw)` 从配置读入，`:275 _suppress_acknowledged()` 在聚合后剔除；④`code_dedup` 侧输入=git diff 增量文件（`src/zephyr/gov_enforcement/rule_enforcement/gate_dedup.yaml` check `DD-CHK-INCREMENTAL` params `scan_mode: incremental`） |
| 下游消费 | ①commit 门禁：`capability_overlap_gate.py:262/270/337`（import `CloneGuardOrchestrator` 并在 commit 时跑）；②**跨域复用（非门禁）**：`src/zephyr/risk/core/crowding_response_engine.py:55 from zephyr.clone_guard.strategy_fingerprint import dtw_distance`，注释 :38 明写"DTW 唯一真源 = clone_guard"——策略拥挤度引擎借用克隆指纹算法，说明 strategy_fingerprint 已外溢成通用件；③MCP 面：`src/zephyr/clone_guard/__init__.py:5 [CONSUMERS]` 声明 `config/mcp.json (servers.clone_guard)`，`mcp_server.py` 在盘；④审计产物消费：`orchestrator.py:529 _persist_audit_result` → `.runtime/clone_guard_audit/audit_<ts>.json`（`scripts/clone_guard_audit.py:26` 注释："不入 git"），`:581 load_latest_audit()` 供 MCP 只读回查；⑤`code_dedup` 声明的消费方=`integration_hub.py:40 {"name": "GATE-DEDUP", "type": "pre-commit"}` |
| 自动化触发 | 三条独立通道，注册名各异：①**pre-commit hook**：`.pre-commit-config.yaml:1004 - id: gate-dedup`（entry `python scripts/pre_commit/verify_dedup.py`，:1001 注释"阶段1（当前）：stages:[manual]——手动 `pre-commit run gate-dedup` 可用，不阻断常规 commit"）；②**GateEngine 事件式**：`gate_dedup.yaml` 描述"每次 GateEngine.evaluate("GATE-DEDUP") 触发时"＋`auto: true`/`on_failure: reject`（与①互斥，见 §四病灶 2）；③**手动审计脚本**：`scripts/clone_guard_audit.py:22 "手动：python scripts/clone_guard_audit.py"`；④**warn-only commit 侧**：`capability_overlap_gate` 经 `create_guard.py:96` 口径="warn-only"。**无计划任务/常驻 daemon 证据**（L2 周期审计仅在 `clone_guard.yml` 注释中作为分层设想出现，未见注册名） |
| 真源与注册表 | ①配置真源=`clone_guard.yml`（自述 :2 "真源: docs/03_modules/_cross_layer/clone_guard/blueprint.md §6"）；②门禁注册表条目=`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml:560-572`（gate_id GATE-DEDUP、`files_trigger: ^src/zephyr/.*\.py$`、`always_run: false`、`status: active`、`enforcement_channel: pre-commit`，**无 own_scope 字段**——该字段在本册实测的 GATE-DEDUP 块内缺席，而同文件 :636/:648/:659 其它门有，说明此门未走 own-diff 作用域声明）；③规则真源=`gate_dedup.yaml`（module_id MOD-GATE_ENGINE，rule_ids TRAE-002）；④ROOR 反查=`docs/registry_of_registries.yaml` grep `clone|dedup` **查无条目**（本包无机读注册表条目，只有 gate_registry 一条）；⑤模块蓝图=`docs/03_modules/_cross_layer/clone_guard/blueprint.md`（由 `scripts/clone_guard_audit.py:1/10` 的 [BLUEPRINT]/[MODIFY-GUARD] 锚指向）；⑥审计台账=`.runtime/clone_guard_audit/`（派生，不入 git） |
| 门禁与质量尺 | 拦谁：`gate-dedup`（AST 级函数粒度重复）＋ `capability_overlap_gate`（编排层聚合结论）＋ `create_guard`（新建件能力重叠，硬阻断）。**是否真跑（本册实测）**：GATE-DEDUP 处于 **manual 阶段、不阻断 commit**（`.pre-commit-config.yaml:1001`＋`gate_registry.yaml:566 always_run: false` 两源同判）→ 按判据口径，提交面它**当前不是有效拦截器**；但其自检件在跑：`self_scanner.py`、`exit_codes.py:45-49` 五态（PASS/WARN/ERROR/TOOL-ERROR/DEGRADED）定义齐备、`pre_apply_integrity_gate.py`、`success_validator.py`、`false_negative_auditor.py` 在盘。质量尺本身有"防尺失效"设计（`risk_mitigator.py:57/61/74` 把"pre-commit 未部署 / 门禁不执行 / Git Hook 损坏"列为 R06/R10/R23 在册风险）——**承认病灶在册，未修**。 |
| 当前运行状态 | **黄偏红**。黄：编排层与引擎层在盘、消费方接线在（capability_overlap_gate 真 import 真调）、配置有硬阻断语义（`fail_on: extract`）。红：①宪法宣称的两个 API 不存在（§四病灶 1）；②GATE-DEDUP 提交面不阻断（manual），而 `code_dedup/exit_codes.py:47` 与 `gate_dedup.yaml on_failure: reject` 均宣称"FAIL 阻断 commit"→ **账面宣称与真源口径相反**；③真源路径书写漂移（§四病灶 3）。可复跑命令见 §七第 1/2 条（第 1 条为最小判别实验：manual 门在普通 commit 下确应不触发）。 |

## 三、子模块清单（`ls` + `grep` + 注册表三源交叉）

**3.1 `src/zephyr/clone_guard/`（9 件，编排层，ls 实测）**：`__init__.py`（[CONSUMERS] 声明 :5）｜`orchestrator.py`（真源主体：check :316 / audit :400 / compare :454、三层引擎构建 :228/:243/:260、acknowledged 抑制 :168/:275、健康分 :495、重构计划 :517、持久化 :529、并发/串行引擎 :635/:696、总降级处置 :715）｜`aggregator.py`｜`config.py`｜`strategy_fingerprint.py`（DTW 唯一真源）｜`mcp_server.py`｜`engines/`（6 适配器：`ast_grep_adapter` `echo_guard_adapter` `mcrit_adapter` `redup_adapter` `relate_adapter` `vendetect_adapter`）｜`rules/`（4 条 ast-grep 规则：`no-bare-except` `no-broad-except` `no-duplicate-try-except` `no-pass-in-except`）

**3.2 `src/zephyr/gov_code_quality/`（2 件）**：`__init__.py`｜`code_dedup/`（下）

**3.3 `src/zephyr/gov_code_quality/code_dedup/`（60 件，引擎层，ls 实测全量，按职责聚类）**

- 检测与比对（12）：`ast_comparator` `signature_matcher` `symbol_index` `micro_clone_detector` `diff_detector` `function_discovery` `path_index_validator` `cross_boundary_detector` `stale_shared_detector` `dead_module_detector` `thematic_clusterer` `behavioral_sampler`
- 安全重构与修复（11）：`atomic_fixer` `auto_fixer` `extraction_safety` `file_creator` `shared_evolver` `shared_lifecycle_manager` `risk_mitigator` `canary_manager` `canary_register` `shadow_trust_validator` `shadow_verifier`
- 审计与判据（10）：`verifier` `fifteen_dimension_auditor` `false_negative_auditor` `simplicity_auditor` `decision_auditor` `contract_consistency_checker` `behavioral_trust_checker` `success_validator` `policy_tree_validator` `pre_apply_integrity_gate`
- 运行保障（10）：`cache_manager` `degradation` `doom_loop_guard` `observation_window_guard` `monoculture_guard` `health_monitor` `exit_codes` `integration_hub` `integrations` `code_analyzer_runner`
- 治理与台账（9）：`grandfather_manager` `annotations` `debt_projector` `prioritizer` `report` `ssot_registrar` `recovery_manifest_writer` `self_scanner` `sensitivity_sweeper`
- 入口与仿真（5）：`cli` `code_simulator` `mock_duplicate_generator` `phase_executor` `config`｜另 `trackers/`（子目录）

**3.4 三源交叉结论**：`ls` 给 69 件全量（9+60 归并）；`grep` 给外部消费方 5 处（capability_overlap_gate / reconciler_health_gate:230 / crowding_response_engine:55 / clone_guard_audit.py / externalize_algo_flow.py:243 归类映射）；注册表侧仅 `gate_registry.yaml:560` 一条 + `gate_dedup.yaml` 一份规则。**交叉缺口**：`code_dedup/` 60 件中仅 `cli` `exit_codes` `integrations` `integration_hub` `risk_mitigator` 5 件有跨文件引用证据，其余 55 件的消费方为**未证**（见 §六）。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | **宪法宣称的 API 不存在**：`AGENTS.md` §1 补充铁律 "RULE-CLONEGUARD：写前预查 `clone_guard.check_before_write`，合理重复走 `resolve_finding` 标 acknowledged"。实测 `grep -rn "def check_before_write\|def resolve_finding" --include=*.py src/` = **0 命中**；`grep -rn "check_before_write\|resolve_finding" src/ scripts/`（去本包）= **0 命中** | 宪法按"设计意图"立法，实现侧走的是**另一套语义**：事后 `check(staged_files)`（orchestrator.py:316）＋配置内静态 acknowledged 对（:168/:275）。"写前预查"这一时间点在实现里不存在；"resolve_finding"这一动作被降级为**改配置文件**而非 API 调用 | 二选一（**须治理裁定，本车道不自裁**）：①改宪法措辞为实测口径（"commit 前经 capability_overlap_gate 复检，合理重复登记进 `clone_guard.yml` acknowledged 对"）；②补 `check_before_write()`/`resolve_finding()` 薄封装 API 并让宪法引用可解析。倾向①（零新增资产，符合 §4 全资产净零） | 0.2（①）/1（②） | 否（改宪法=热文件＋判据文本，Owner/总筹面） |
| 2 | **同一枚 GATE-DEDUP 三源互斥**：`.pre-commit-config.yaml:1001`＝"阶段1 stages:[manual]，不阻断常规 commit"；`gate_registry.yaml:566`＝`always_run: false`；而 `rule_enforcement/gate_dedup.yaml`＝`auto: true` + `on_failure: "reject"` + "每次 GateEngine.evaluate 触发"；`code_dedup/exit_codes.py:47`＝"ERROR → GATE-DEDUP FAIL 阻断commit" | 规则 YAML（设计意图）与 hook 注册面（实际执行）分头演进，无一致性尺；`integration_hub.py:40` 又独立声明一份"GATE-DEDUP type=pre-commit" | 以 hook+gate_registry 两源为**运行真源**，把 `gate_dedup.yaml` 的 `auto/on_failure` 改成与阶段一致的字段（或加 `stage: manual` 显式标注）；同时给 `validate_rules_integrity.py` 加一条"gate 的 auto/on_failure 与 gate_registry.always_run/stages 互斥检测" | 1 | 否（改 gate 属 commit_gates 在途热件，§一第 4 条禁触） |
| 3 | 真源路径书写漂移：`.pre-commit-config.yaml:998` 注释"真源：scripts/pre_commit/verify_dedup.py → **zephyr.governance.code_dedup.cli** verify"，盘上实际包是 **`zephyr.gov_code_quality.code_dedup`**（`grep` 命中路径自证）；`code_dedup/integrations.py:49` 又写 `scripts/pre-commit/verify_dedup.py`（连字符目录，盘上只有 `pre_commit`） | 包迁移（governance→gov_code_quality）后注释/自述未同步 | 全仓 `grep "governance.code_dedup\|scripts/pre-commit/"` 一次性改注释；无行为变更 | 0.2 | 部分（改注释即改生产文件，本车道不改，登记待接线） |
| 4 | 60 件引擎层中 55 件消费方未证 → 存在"能力堆叠而无人调用"的高风险面（该包自述 R06/R10/R23 三条"门禁不执行"风险在册未修，`risk_mitigator.py:57/61/74`） | 无跨件消费反查尺 | 下一窗跑 §七第 4 条命令得零消费清单，按 w5_1"零触发零消费→退役"**只登记不删**（注册表净删=Owner 门位） | 0.5 | 可（判据清单） |
| 5 | `capability_overlap_gate` 是 warn-only（`create_guard.py:96` 明写"硬阻断而非 warn-only：capability_overlap_gate 是 warn-only"）→ 宪法"extract 级克隆无逃生"在提交面实际由谁兜住？候选=`create_guard`（硬阻断）＋`clone_guard.yml fail_on: extract`（但该门 manual） | 逃生口径落在 create_guard（新建件重叠），存量件的 extract 级克隆仍可能过 | 取一次真实拒绝样本（`.runtime` 审计或 git log 中 gate 拦截记录）验证"无逃生"是否成立；无样本=判"未验证" | 0.5 | 可 |

## 五、内收与合并机会（四判据）

- **同真源可派生→必并**：三处对 GATE-DEDUP 的自述（`.pre-commit-config.yaml` / `gate_registry.yaml` / `gate_dedup.yaml` / `integration_hub.py:40`，共 4 处）都是同一枚门的派生视图 → 应由 `gate_registry.yaml` 单向派生，其余改为引用（**必并**）。
- **零触发零消费→退役**：§四病灶 4 的候选清单（待 §七第 4 条实测）；另 `mock_duplicate_generator.py`（自称"造重复样本"）若仅测试消费则属测试夹具，应移出生产包（登记，不改名）。
- **同域重复簇→收敛唯一**：包内三对同名异体候选 `shadow_verifier`↔`shadow_trust_validator`、`canary_manager`↔`canary_register`、`verifier`↔`success_validator`↔`pre_apply_integrity_gate`（三件同职"验"）→ 待消费面实测后定；`integrations.py`↔`integration_hub.py` 一对亦同。
- **跨域不同对象→不并**：`clone_guard`（代码克隆）与 `strategy_fingerprint` 被 `crowding_response_engine`（策略拥挤度）借用＝同件不同业务对象，**不并**（并即绑死交易域）；`code_dedup` 与 `capability_overlap_gate`（能力面重叠，语义=文档/注册表重叠）不并。

## 六、自审闸三态

**判：挖干可施工**（就 F103 六向而言）——六向每向有 file:line 或注册表行号实证；§三 清单为 ls 全量＋grep 消费方＋注册表单源交叉。

**保留意见（不得当成已闭）**：①`code_dedup/` 60 件中 55 件的**逐件**消费方未反查（本车道限量取证：每结论≤3 命令）→ 若后续要宣称"整个 F103 面挖干"，缺这一条；②`docs/03_modules/_cross_layer/clone_guard/blueprint.md` 未读（蓝图↔实现一致性未核）；③L2/L3 引擎（mcrit/redup/relate/vendetect）是否真在 pre-commit 加载未跑通实测（`_build_l2_engines` :243 / `_build_l3_engines` :260 在盘，实际是否启用取决于 `clone_guard.yml` 未读段落）。

**待裁（已写进本目录 `pending_rulings.md`）**：病灶 1 的修法方向①/②（涉宪法文本）、病灶 2 的门禁阶段口径（涉 gate 在途热件）。

**回写总册建议**：`00_全环节总册.md:178` 由 `built` 改 **`built（提交面 warn-only/manual，GATE-DEDUP 不阻断，宪法引用 API 不存在）`**，备注列指向本册 §四 1/2。

## 七、复核命令

```bash
# 1) 最小判别实验：GATE-DEDUP 是否真在普通 commit 阻断（预期=manual，不触发）
pre-commit run gate-dedup --all-files ; sed -n '996,1015p' .pre-commit-config.yaml

# 2) 宪法 API 不存在（本册核心发现，两条命令互证）
grep -rn "check_before_write\|resolve_finding" --include=*.py src/ scripts/ | wc -l
grep -n "def check\b\|def audit\|def compare\|_load_acknowledged_pairs\|_suppress_acknowledged" src/zephyr/clone_guard/orchestrator.py

# 3) GATE-DEDUP 三源互斥逐源读
sed -n '560,572p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
sed -n '1,40p' src/zephyr/gov_enforcement/rule_enforcement/gate_dedup.yaml
sed -n '40,50p' src/zephyr/gov_code_quality/code_dedup/exit_codes.py

# 4) 60 件引擎层消费方反查（交下一窗出零消费退役候选清单）
for f in $(ls src/zephyr/gov_code_quality/code_dedup/*.py | xargs -n1 basename | sed 's/\.py$//'); do printf "%s " $f; grep -rln "code_dedup.$f\|from .$f import" --include=*.py src/ scripts/ tests/ | grep -v "code_dedup/$f.py" | wc -l; done

# 5) 真源路径漂移复核
grep -rn "governance.code_dedup\|scripts/pre-commit/" --include=*.py --include=*.yaml src/ scripts/ .pre-commit-config.yaml | head
```
