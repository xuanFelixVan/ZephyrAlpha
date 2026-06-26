# 向内收原则固化 + 全项目多真源/触发方式违反排查与修复

> **⚠️ 架构裁定已落地（2026-06-26）**：CircadianScheduler 的定时调度机制已废除——register_task/start/stop/save_state 均改为 no-op，_loop 已删除。
> 本文档中关于"废定时轨"的规划描述为历史记录，代码层面的 no-op 改造已完成。文中引用的旧规则（如 circadian_scheduler.register_task、circadian.running）仅作历史参考。

## Context(为什么做这个改动)

起因:与另一 AI 讨论 doc_type 治理时,发现"自动同步"概念本身是错的——同步=复制=又造真源=必漂移。正确做法是 B/C/D 代码**直接读词表动态加载**,不复制不同步。这引出两个问题:

1. **现实问题**:doc_type 的"4 真源、仅 1 处动态加载"不是孤例,是系统性疾病。已排查确认:24 个词表中 **9 个有 .py 硬编码副本共 23 处**,3 个 sync 脚本制造多真源,14 处时间触发、~25 处手工触发违反,6 簇可合并重复实现。
2. **逻辑问题**:用户"向内收"三原则(①能现成不创造优先扩展不同步 ②永久功能必事件驱动全自动禁时间触发禁手工触发 ③第一性原理质疑元问题该删该合并)目前**没有统辖性铁律固化**,散落在 trae_057/053/054 和 project_memory 里,新进 AI 无可机器执行的判定标准,导致同类问题反复发生(如 doc_type 之前没门禁挡住硬编码)。

**范围界定**:另一个 AI 正在处理 doc_type 的"点"状工作([doc_type_governance_plan.md](file:///d:/ZephyrAlpha/docs/_working/doc_type_governance_plan.md)),本 plan 做"面"——固化三原则 + 全项目排查修复,与 doc_type 工作互补。本 plan 不碰 doc_type 那个 AI 正在改的 triage.py / audit_directory_integrity.py(批1 词表修复时会避开 doc_type,留给那个 AI)。

**决策(已与用户确认)**:①新建 trae_060 固化三原则;②修法 trae_053 废定时轨改"事件轨+CI兜底";③按严重度分4批词表优先;④门禁本轮建 warn-only 起步。

---

## 第一部分:规则固化(判定标准,先立)

### 1.1 新建 trae_060 向内收原则

**文件**:[docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)(新建)

对齐 [trae_057](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_057_ai_consumer_first.yaml) 的 YAML 结构(rule_id/version/layer/module_id/depends_on/tags/stability/safety_level/ai_autonomy/aliases/severity/scope/domain/rule_form/triggers/sections/references/enforcement/metadata/provenance)。`stability: frozen`、`ai_autonomy: immutable_core`(顶层原则)、`severity: critical`、`version: 1.0.0`、`module_id: TRAE-060`、`aliases: [INWARD-001, INWARD-CONSOLIDATION, 向内收, SSC-EVT-001]`。

`depends_on`:TRAE-057(AI消费优先,§2依据)、TRAE-053(修法后事件轨,§3施工)、TRAE-054(depgraph访问)、TRAE-042/043(YAML格式+双真源)、PROJECT_MEMORY(YAML唯一真源铁律+MOD-INF-030)。

**6 个 section**:
- §1 原则声明:三原则完整表述 + 落地目标(唯一真源/唯一责任/自动维护/新AI不漂移)
- §2 唯一真源与直接消费(对应①):三种引用区分——(a)合法值集合直接读词表 values (b)值属性入词表字段 (c)业务分支标 `# RENAME_REVIEW`;禁止硬编码/同步复制;引用正例范式 [check_frontmatter_metadata.py:63-68](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L63) + [generate_derived_files.py:85-107](file:///d:/ZephyrAlpha/scripts/governance/generators/generate_derived_files.py#L85)
- §3 事件驱动全自动(对应②):禁 CircadianScheduler/cron/Timer/sleep-loop/periodic/进程内调度器;CI `.github/workflows schedule` 作批量兜底**允许**(非进程内Timer/不占运行时/可被push增量取代);例外清单:退避重试/锁轮询/启动等待=同步原语不算时间触发;一次性运维/诊断/迁移脚本允许 manual
- §4 第一性原理元问题审查(对应③):动手前必问"该不该存在/能否删除/能否合并";治本优先;列已排查6簇重复待合并
- §5 禁止清单(汇总,含已排查违反清单作 evidence)
- §6 与既有铁律关系(统辖 trae_057/053/054,声明 DDL-as-Code 协议待建作 §5 SQL CHECK 例外出口)

每个 rule section 含 `original_rules`/`conditions`/`prohibitions`,不写散文(对齐 trae_057 风格)。`enforcement.executors` 指向 GATE-VOCAB 脚本 + apply_depgraph + audit_registration。`provenance` 记 2026-06-26 Owner 裁定。

**索引登记**:追加 [docs/01_policies_and_standards/rules/_index.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/_index.yaml) 末尾(对齐 trae_057 条目格式),`total_rules` 当前值+1(执行时核对)。

### 1.2 修法 trae_053 废定时轨

**文件**:[docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml)(修法)

当前是 `frozen`/`immutable_core`,STEP2(约行48)强制"定时轨在 boot_cron_jobs.py 注册 circadian_scheduler.register_task",prohibitions(约行52-57)把"实现定时轨但不注册到 circadian_scheduler"列为禁止。这与三原则②、project_memory(MOD-INF-030 废除 CircadianScheduler)、红蓝对抗已迁移事件驱动**三者直接矛盾**。修法前所有 CircadianScheduler 调用方都"合规"(按旧规则),修法后才构成违反——**本修法是批3触发方式修复的前置**。

**修法 diff**:
- STEP2:删 `🕐定时在boot_cron_jobs.py注册(circadian_scheduler.register_task)`,改"⚡事件轨在 boot_hooks.py 注册;批量兜底走 CI schedule(非进程内Timer);CircadianScheduler 已废止禁止注册"
- STEP3:删 `circadian.running=true` 验证,改"触发事件后 check hooks 执行→⚡通过;CI workflow_run 历史有成功记录→CI兜底通过"
- prohibitions:删"实现定时轨但不注册到 circadian_scheduler";新增"新建/使用 CircadianScheduler 或任何进程内定时调度器""实现定时轨注册到 circadian_scheduler(系统已废止)"
- references.modules:删 `circadian_scheduler.py`
- 顶层 `version: 1.0.0`→`2.0.0`(废止定时轨=不兼容变更),追加 `metadata.change_history` v2.0.0 条目

**变更流程**(frozen 规则,对照 GitCommitGateway):
1. 经 GitCommitGateway 串行化提交(env `ZEPHYR_COMMIT_GATEWAY=1`,message 标 `[GW:<session_id>]`)
2. version 升 2.0.0 + change_history 追加
3. 同步 project_rules.md(若引用 RULE-FIFTEEN)与 onboarding_detail.md 对照表
4. 提交前跑 GATE-RULE-FM + GATE-SSOT + GATE-COMMIT-GW
5. 修法 commit 与批3修复 commit **分开**,修法先行

### 1.3 新建 GATE-VOCAB 门禁(warn-only 起步)

**脚本**:[scripts/governance/d3_metadata/check_vocab_hardcode.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_vocab_hardcode.py)(新建,对齐 check_frontmatter_metadata.py 位置)

头部 [MODULE]/[BLUEPRINT] 十四字段标记(对齐 trae_054),`[STARTUP] manual`、`[ERROR_CONTRACT] EXIT_PASS=0/EXIT_FINDINGS=1/EXIT_ERROR=2`。

**检测逻辑**(AST 扫描 src/ 与 scripts/ 下 .py):
- 启发式1:变量名匹配 `VALID_*_VALUES/STATUSES/TYPES/LEVELS` 且赋值为列表/集合/frozenset 字面量 → 疑似词表硬编码
- 启发式2:变量名匹配 `*_MAP/*_SUFFIX_MAP` 且赋值为字典字面量 → 疑似值属性硬编码(应入词表字段)
- 启发式3:`class \w+(Enum)` 且非业务枚举白名单 → 疑似词表硬编码
- "是否动态加载"判定:同文件有 `yaml.safe_load(...)` 且变量引用该调用→合规,否则→违规
- **DDL 例外**:`sqlite_schema.py`/`depgraph_schema.py` 的 SQL `CHECK(... IN (...))` 无法动态化,入 `_DDL_AS_CODE_EXEMPT` 白名单排除(走待建的 DDL-as-Code 协议)
- **业务枚举白名单**:OrderSide/OrderType/OrderStatus 等交易业务枚举豁免(非规则数据)

**模式**:`--warn-only`(默认,print 违规清单 exit 0)/ `--ci`(未来 hard block exit 1)。复用 canonical:`_shared/yaml_utils`、`_shared/walk`、`_shared/constants`(执行时核对现有模块名)。

**挂载**:追加 [.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) `repos[local].hooks` 末尾(GATE-GENERATE 之后),对齐 GATE-15 写法:
```yaml
- id: gate-vocab-hardcode
  name: "GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）"
  entry: python scripts/governance/d3_metadata/check_vocab_hardcode.py
  args: ["--warn-only"]
  language: system
  files: "^(src/|scripts/).*\\.py$"
```

**升级路径**:Phase A warn-only(当前)→ 存量23处清零+连续30天零新增 → Phase B 改 `--ci` hard block。

---

## 第二部分:4 批存量修复任务卡

每批:施工步骤(含 file:line 清单)+ 验证命令 + 回滚。每批完成后连续 2 次零问题方可进下一批(对齐 project_memory 域拆分复查铁律)。

### 批1:词表硬编码修复(9 词表 23 处,与 doc_type 工作避开)

**正例范式(复用)**:[generate_derived_files.py:85-107](file:///d:/ZephyrAlpha/scripts/governance/generators/generate_derived_files.py#L85) 的 `VOCAB_FIELD_MAP` + `_load_vocab_values()` 是通用动态加载范式,推广到其余词表;[check_frontmatter_metadata.py:63-68](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L63) `_load_ttl_values` 单词表范式;[validate_blueprint_placement.py:74-90](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_blueprint_placement.py#L74) layer 动态读 `dir_prefix` 范式。

| 词表 | 副本位置 | 类型 | 修复方向 |
|---|---|---|---|
| ttl | [validate_document_ttl.py:67](file:///d:/ZephyrAlpha/scripts/governance/d8_doc_sync/validate_document_ttl.py#L67) `VALID_TTL_VALUES`(6值,**且过期**接受4个已删值) | a集合 | 删硬编码,改 `_load_ttl_values` 读 [ttl_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) |
| status | [validate_ssot.py:16](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_ssot.py#L16) `VALID_DOCUMENT_STATUSES`(4值,**漂移**含废弃approved/superseded) | a集合 | 改动态加载 status_vocabulary |
| doc_type | [triage.py:73](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L73) `VALID_DOC_TYPES`;triage.py:283-287 业务分支 | a+c | **留给另一个AI**(doc_type工作),本批避开 |
| layer | [triage.py:102](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L102) `VALID_LAYERS`;[validate_layer_consistency.py:63](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_layer_consistency.py#L63) `LAYER_DIR_MAP`(**漂移**pf_core重复+非词表键);[sync_registry_from_blueprints.py:74](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py#L74) 同样漂移;[batch_create_index_md.py:295](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/batch_create_index_md.py#L295) `MODULE_LAYER_MAP` | a+b | layer 词表补 `dir_prefix` 字段(已有 validate_blueprint_placement 范式);3处 MAP 删,改读字段 |
| category | [schemas.py:78](file:///d:/ZephyrAlpha/src/zephyr/shared/schema/schemas.py#L78) `KeCategory(Enum)` + [integration/shared/schema/schemas.py:78](file:///d:/ZephyrAlpha/src/zephyr/integration/shared/schema/schemas.py#L78) **重复Enum**;[knowledge_base_server.py:77](file:///d:/ZephyrAlpha/src/zephyr/integration/mcp/knowledge_base_server.py#L77) + [infrastructure/knowledge_base_server.py:81](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/knowledge_base_server.py#L81) **重复frozenset**;[triage.py:291](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L291) 业务分支 | a+a+a+c | 4处副本收敛为1处动态加载(先确认src侧是否有canonical);业务分支标 RENAME_REVIEW |
| safety_level | [scaffold.py:442](file:///d:/ZephyrAlpha/scripts/scaffold.py#L442) 集合;[diagnose_depgraph.py:335](file:///d:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L335) `SAFETY_ORDER`;[detect_causal_conflicts.py:272](file:///d:/ZephyrAlpha/scripts/governance/detect_causal_conflicts.py#L272) `safety_order`;[sqlite_schema.py:101](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py#L101) SQL CHECK | a+b+b+DDL | scaffold改动态加载;序映射入词表字段;SQL CHECK 走 DDL-as-Code 例外 |
| stability | [scaffold.py:440](file:///d:/ZephyrAlpha/scripts/scaffold.py#L440) 集合;[diagnose_depgraph.py:334](file:///d:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L334) `STABILITY_ORDER` | a+b | scaffold改动态加载;序入词表字段 |
| ai_autonomy | [scaffold.py:444](file:///d:/ZephyrAlpha/scripts/scaffold.py#L444) 集合;[generate_project_depgraph.py:3290](file:///d:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py#L3290) derive分支 | a+c | scaffold改动态加载;derive分支标 RENAME_REVIEW |
| classification | [sqlite_schema.py:105](file:///d:/ZephyrAlpha/src/zephyr/governance/sqlite_schema.py#L105) SQL CHECK | DDL | 走 DDL-as-Code 例外 |

**验证**:`python scripts/governance/d3_metadata/check_vocab_hardcode.py` → 9词表副本数应从23降至 doc_type 那2处(留给另一个AI);GATE-15 仍绿;`pytest tests/governance/` 全绿。
**回滚**:每词表独立 commit(GitCommitGateway),失败回退上一词表。

### 批2:sync 多真源修复(3 个)

| 脚本 | 问题 | 修复 |
|---|---|---|
| [sync_registry_from_blueprints.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py) | 把 frontmatter 1份真源复制成 blueprint_registry.yaml + module_registry.yaml 2份,且 module_registry.yaml.construction_plan.status 被 sync_blueprint_status 当真源读,催生 [validate_ssot_construction_progress.py:19-22](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_ssot_construction_progress.py#L19) 三向校验 | 保留 frontmatter 唯一真源;只派生**1份**注册表(或合并两份);删除三向校验,改"frontmatter→单一派生缓存"单向 |
| [sync_blueprint_status.py](file:///d:/ZephyrAlpha/scripts/governance/sync_blueprint_status.py) | 读派生副本(module_registry.yaml:118-121)当真源;把 blueprint.status 写入 module_registry.yaml(192/203)+blueprint.md(75-108)两个canonical位;:50连字符路径bug | 直读 frontmatter;只写回 frontmatter(真源);修路径bug |
| [sync_blueprint_code_index.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/syncers/sync_blueprint_code_index.py) | `BLUEPRINT_MODULE_MAP`(75-353).py硬编码常量复制19模块映射 | 删 MAP,改从 blueprint.md frontmatter + 磁盘扫描动态派生 |

**附带**:7处引用不存在的 `module-registry.yaml`(连字符,实际下划线)——[sync_blueprint_status.py:50](file:///d:/ZephyrAlpha/scripts/governance/sync_blueprint_status.py#L50) 等,修路径bug。
**验证**:`GATE-SSOT` 三向校验删除后仍绿;`pytest tests/governance/test_gct_*` 全绿;grep `module-registry.yaml`(连字符)零命中。
**回滚**:每脚本独立 commit。

### 批3:触发方式修复(14 时间触发 + ~25 手工触发,需 trae_053 修法先行)

**前置**:1.2 trae_053 修法必须先合并,否则 CircadianScheduler 调用方"合规"。

**时间触发 14 处**:
- CircadianScheduler 系统:[circadian_scheduler.py](file:///d:/ZephyrAlpha/src/zephyr/trading/circadian_scheduler.py)(定义+11自注册)、[boot_cron_jobs.py](file:///d:/ZephyrAlpha/src/zephyr/trading/boot_cron_jobs.py)(16任务)、[lifecycle_manager.py](file:///d:/ZephyrAlpha/src/zephyr/trading/lifecycle_manager.py)(8任务)、[f5_boot_integration.py](file:///d:/ZephyrAlpha/src/zephyr/governance/f5_boot_integration.py)(2任务)、[auto_runtime_core.py](file:///d:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py)(调用链)——逐任务判定:迁事件轨(push/状态变更 hook)或迁 CI schedule 兜底;CircadianScheduler 类标记 deprecated
- [drift_cron_scheduler.py:48](file:///d:/ZephyrAlpha/src/zephyr/behavioral_audit/drift_cron_scheduler.py#L48) sleep-loop → file_change 事件
- [ops/scheduler.py](file:///d:/ZephyrAlpha/src/zephyr/ops/scheduler.py) FeedbackLoopScheduler → 事件
- [ide_health_service.py:212](file:///d:/ZephyrAlpha/scripts/ide_health_service.py#L212) daemon poll → 事件/CI
- [governance_watchdog.py:141](file:///d:/ZephyrAlpha/scripts/governance/governance_watchdog.py#L141) daemon → 事件
- [vms_cron_monitor.py:108](file:///d:/ZephyrAlpha/scripts/governance/vms_cron_monitor.py#L108) daemon+cron → 事件
- [auto_fix_cron.py:108](file:///d:/ZephyrAlpha/scripts/governance/ops/auto_fix_cron.py#L108) cron → 事件
- [dedup-watch.yml:4](file:///d:/ZephyrAlpha/.github/workflows/dedup-watch.yml#L4) schedule cron → **保留为CI兜底(允许)** 或改 paths 触发
- [red-blue-validator.yml:75](file:///d:/ZephyrAlpha/.github/workflows/red-blue-validator.yml#L75) 死 schedule 条件 → 删除残留

**手工触发 ~25 处**(永久治理功能仅 manual):[sync_yaml_to_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/sync_yaml_to_depgraph.py)、[auto_sync_all_registries.py](file:///d:/ZephyrAlpha/scripts/governance/auto_sync_all_registries.py)、[diagnose_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py)(post_sync_standard命令)等——挂 rules/*.yaml 变更事件 或 入 pre-commit/CI。一次性迁移脚本(dm*/migrate*/rename*)不计入。

**验证**:grep `CircadianScheduler|register_task|circadian_scheduler` 在 src/ 活跃代码零命中(除 deprecated 标记);grep `schedule:` 在 .github/workflows 仅兜底job;`pytest tests/infrastructure/test_drift_*` 全绿。
**回滚**:每脚本独立 commit;CircadianScheduler 迁移按任务粒度逐个迁,失败回退单个任务。

### 批4:可合并重复实现收敛(6 簇)

| 簇 | canonical | 散落处 | 修复 |
|---|---|---|---|
| atomic_write | [manage_baseline.py:87](file:///d:/ZephyrAlpha/scripts/governance/meta/manage_baseline.py#L87) `_atomic_write` + [src/shared/io/file_utils.py:68](file:///d:/ZephyrAlpha/src/zephyr/shared/io/file_utils.py#L68) | scripts/ 13处 + src/ 9处(含 src 侧 forensic/metadata 双份) | scripts 收敛 manage_baseline._atomic_write;src 收敛 shared/io/file_utils.atomic_write;删双份 |
| load_yaml | [_shared/yaml_utils.py:30](file:///d:/ZephyrAlpha/scripts/governance/_shared/yaml_utils.py#L30) `load_yaml` | 17处未复用(auto_sync/score_architecture/sync_yaml_to_depgraph等) | 统一 `from _shared.yaml_utils import load_yaml` |
| parse_frontmatter | [_shared/frontmatter.py:24](file:///d:/ZephyrAlpha/scripts/governance/_shared/frontmatter.py#L24) `parse_frontmatter` | 9处未复用 | 统一 import |
| apply_depgraph WAL | (新建 `_connect_wal` helper) | [apply_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py) 同文件 PRAGMA WAL+busy_timeout 重复10次 | 抽 helper,10处收敛 |
| scan_secret_leak | manage_baseline._atomic_write | [scan_secret_leak.py:153-167+205-214](file:///d:/ZephyrAlpha/scripts/governance/d6_security/scan_secret_leak.py#L153) 同文件双份内联 | 复用 `_atomic_write`(JSON非JSONL格式差异保留,写入步骤复用) |
| src forensic/metadata | (二选一canonical) | [governance/forensic.py:360](file:///d:/ZephyrAlpha/src/zephyr/governance/forensic.py#L360)+[infrastructure/rollback/forensic.py:360](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/rollback/forensic.py#L360);metadata同 | 确认 canonical,删副本 |

**验证**:`pytest tests/governance/test_all_scripts.py` + `test_security_scripts.py` 全绿;GATE-SQ 绿。
**回滚**:每簇独立 commit。

---

## 执行顺序与依赖

```
1.1 新建trae_060 ─┐
1.2 修法trae_053 ─┼─→ 1.3 GATE-VOCAB(warn-only) ─→ 批1词表 ─→ 批2sync ─→ 批3触发 ─→ 批4合并
                  │                                              ↑
                  └──────────────────────────────────────────────┘
                    trae_053修法是批3前置(修法前circadian"合规")
```

1.1/1.2 可并行(独立规则文件);1.3 依赖 1.1(GATE-VOCAB 法源是 trae_060 §2)。批1-4 串行,每批连续2次零问题方进下一批。批3 依赖 1.2 合并。

**本轮 plan 覆盖**:1.1+1.2+1.3(规则固化,立即执行)+ 批1(词表,与doc_type互补)。批2/3/4 各自独立任务卡,分后续轮次执行(每轮开工前重读本 plan 对应批次)。若用户要求本轮全做,则按顺序串行推进,不跳批次。

---

## 验证(端到端)

1. **规则固化验证**:
   - `python scripts/governance/d3_metadata/check_frontmatter_metadata.py`(GATE-15)校验 trae_060/trae_053 frontmatter 合法
   - `python scripts/governance/d5_architecture/validators/validate_rule_frontmatter.py`(GATE-RULE-FM)校验规则格式
   - `python scripts/governance/d5_architecture/validators/validate_ssot.py`(GATE-SSOT)校验一致性
   - grep `trae_060` 在 _index.yaml 已登记;total_rules 已+1
2. **GATE-VOCAB 验证**:
   - `python scripts/governance/d3_metadata/check_vocab_hardcode.py` → warn-only 打印已知23处,exit 0
   - `pre-commit run gate-vocab-hardcode --all-files` → 不阻断
3. **批1验证**:
   - `check_vocab_hardcode.py` 副本数从23降至2(doc_type留给另一AI)
   - `pytest tests/governance/` 全绿
   - GATE-15 仍绿
4. **回归**:每批后跑 `GATE-SSOT` + `GATE-RULE-FM` + 相关域测试,连续2次零问题

## 回滚

- 规则文件:每文件独立 commit(GitCommitGateway),失败 `git revert <commit>`
- trae_053 修法:保留 v1.0.0 历史,回滚即恢复 version 1.0.0 + 删 change_history v2.0.0 条目
- GATE-VOCAB:`.pre-commit-config.yaml` 删 hook 即停用;脚本删除
- 批1-4:每批每项独立 commit,失败回退上一项
- 全程通过 GitCommitGateway(env `ZEPHYR_COMMIT_GATEWAY=1`,message 标 `[GW:<session_id>]`),改 depgraph.db 前先 `git commit` 备份(trae_054 STEP0)
