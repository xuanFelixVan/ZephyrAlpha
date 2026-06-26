# 向内收原则——剩余 Phase 1 任务执行计划

> **⚠️ 架构裁定已落地（2026-06-26）**：CircadianScheduler 的定时调度机制已废除——register_task/start/stop/save_state 均改为 no-op，_loop 已删除。
> 本文档中关于"废定时轨"的任务描述为规划记录，代码层面的 no-op 改造已完成。文中引用的旧规则（如 circadian_scheduler.register_task、circadian.running）仅作历史参考。

## Summary

本 plan 是 [inward_consolidation_principle_and_ssot_audit.md](file:///d:/ZephyrAlpha/.trae/documents/inward_consolidation_principle_and_ssot_audit.md) 的续接，聚焦该 plan 中**尚未完成**的 4 个任务：1.2 修法 trae_053、1.3 新建 GATE-VOCAB 门禁、批1 词表硬编码修复、端到端验证。

**已完成**：1.1 新建 trae_060（282 行，6 section，frozen/immutable_core）+ _index.yaml 登记（total_rules=58，L0_critical=19）。

**本轮范围**：1.2 + 1.3 + 批1（P0/P1 非 archive 文件）+ 验证。批2/批3/批4 与 sync_yaml_to_depgraph 大规模重构列为后续轮次。

---

## Current State Analysis

### 已核实的关键发现（基于 3 个 Explore agent 的全项目扫描）

**词表硬编码问题（按严重度）**：

| 优先级 | 文件 | 行号 | 问题 | 本轮处理 |
|--------|------|------|------|----------|
| P0 | validate_document_ttl.py | 67 | `VALID_TTL_VALUES` 含 4 个废弃值（7d/30d/periodic_review_90d/session），校验器接受废弃 TTL | **修** |
| P0 | validate_document_ttl.py | 215 | `ttl_thresholds` 硬编码 3 个废弃值阈值 | **修** |
| P1 | triage.py | 98-115 | `VALID_LAYERS` 硬编码 16 值，与同文件 `VALID_DOC_TYPES`（已动态加载）自相矛盾 | **修** |
| P2 | finding_state_machine.py | 72-83 | ImportError 回退分支硬编码 10 个 Finding 状态 | 后续 |
| P2 | migrate_clean_build_status.py:17 + apply_depgraph.py:610 | — | build_status/design_maturity 双处真源（需先建词表） | 后续 |
| P3 | generate_missing_index_md.py:78-81 | — | TTL 字面量硬编码 | 后续 |
| P3 | detect_permanent_file_deletion.py:105-121 | — | "permanent" 字面量 4 处 | 后续 |
| P3 | collection_schemas.py:60-126 | — | ai_autonomy_level 命名与词表冲突 | 后续 |
| — | validate_ssot_status.py:39-52 | _archive | 已归档，10 个错误值 | 不修（archive） |
| — | check_frontmatter_metadata.py:67（旧版） | _archive | 已归档 | 不修（archive） |

**正例范式（修复参照）**：
- [check_frontmatter_metadata.py:63-68](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L63) `_load_ttl_values()` — `yaml.safe_load` + `{v["value"] for v in data.get("values", [])}`
- [triage.py:86-96](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py#L86) `VALID_DOC_TYPES` — 同文件内已有动态加载正例（另一个 AI 改的 doc_type）

**trae_053 当前状态**：version=1.0.0（但 change_history 最新是 1.2.0，已存在不一致），STEP2 强制 circadian_scheduler.register_task，与三原则②、MOD-INF-030 废除 CircadianScheduler 直接矛盾。

**GATE-VOCAB 状态**：脚本不存在，pre-commit 未挂载。

---

## Proposed Changes

### 任务3（1.2）：修法 trae_053 废定时轨

**文件**：[docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml)

**精确 diff（基于已核实行号）**：

1. **第 3 行** `version: 1.0.0` → `version: 2.0.0`

2. **第 48 行** STEP2，当前：
   ```
   step: STEP2实现→🕐定时在boot_cron_jobs.py注册(circadian_scheduler.register_task)；⚡事件在boot_hooks.py注册(hook_registry.register或event_bus.subscribe)；🕐+⚡双轨两条都要
   ```
   改为：
   ```
   step: STEP2实现→⚡事件轨在 boot_hooks.py 注册(hook_registry.register 或 event_bus.subscribe)；批量兜底走 CI schedule(.github/workflows，非进程内Timer)；CircadianScheduler 已废止，禁止注册任何任务到 circadian_scheduler
   ```

3. **第 50 行** STEP3，当前：
   ```
   step: STEP3验证→python scripts/ide_health_service.py --status→circadian.running=true+tasks_registered正确计数→🕐通过；触发事件后check对应hooks执行→⚡通过
   ```
   改为：
   ```
   step: STEP3验证→触发事件后 check 对应 hooks 执行→⚡事件轨通过；CI workflow_run 历史有成功记录→CI兜底通过；grep 确认无 circadian_scheduler.register_task 调用→废止验证通过
   ```

4. **第 30 行** conditions 第一条 pass 字段，当前：
   ```
   pass: 通过两轨分类+实现验证(🕐定时/⚡事件/🕐+⚡双轨)
   ```
   改为：
   ```
   pass: 通过分类+实现验证(⚡事件轨/CI批量兜底)
   ```

5. **第 33-34 行** conditions 第二条（全项目扫描归属），当前：
   ```
   check: 全项目扫描(去重/孤儿/临时文件/审计保留)
   pass: 归属🕐定时轨
   fail: 挂在事件驱动上(每次文件变更扫全项目=拖死)
   ```
   改为：
   ```
   check: 全项目扫描(去重/孤儿/临时文件/审计保留)
   pass: 归属 CI schedule 批量兜底(.github/workflows schedule)
   fail: 挂在进程内事件驱动上(每次文件变更扫全项目=拖死)或进程内定时器(已废止)
   ```

6. **第 56 行** prohibitions，删除：
   ```
   - 实现定时轨但不注册到circadian_scheduler(代码写好了但没人跑)
   ```
   替换为新增 2 条：
   ```
   - 新建或使用 CircadianScheduler 及任何进程内定时调度器(已废止，违反 trae_060 §3)
   - 向 circadian_scheduler.register_task 注册任何任务(系统已废止)
   ```

7. **第 65 行** references.modules，删除：
   ```
   - src/zephyr/trading/circadian_scheduler.py
   ```

8. **change_history**（第 79 行 `change_history:` 之后、`- version: '1.2.0'` 之前）插入：
   ```yaml
   - version: '2.0.0'
     date: '2026-06-26'
     change: '废除定时轨(🕐)：CircadianScheduler 已废止(MOD-INF-030)；双轨判定改为"事件轨+CI批量兜底"；STEP2/STEP3/conditions/prohibitions 同步更新；references.modules 删 circadian_scheduler.py；对齐 trae_060 §3 事件驱动全自动'
   ```

**变更流程**（frozen/immutable_core 规则）：
- 经 GitCommitGateway 提交（env `ZEPHYR_COMMIT_GATEWAY=1`，message 标 `[GW:<session_id>]`）
- 提交前跑 GATE-RULE-FM + GATE-SSOT
- 修法 commit 与批3修复 commit **分开**

---

### 任务4（1.3）：新建 GATE-VOCAB 门禁脚本

**新建文件**：[scripts/governance/d3_metadata/check_vocab_hardcode.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_vocab_hardcode.py)

**头部标记**（十四字段，对齐 trae_054 + check_frontmatter_metadata.py 范式）：
```
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_vocab_hardcode.py | §gate-vocab
# [MODULE] governance.d3_metadata.check_vocab_hardcode
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] _shared.constants; _shared.walk
# [CONSUMERS] pre-commit GATE-VOCAB; manual audit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] AST 扫描检测词表合法值硬编码；warn-only 起步(exit 0)；DDL 例外白名单；业务枚举白名单
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无违规或 warn-only）；EXIT_FINDINGS=1（--ci 模式有违规）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：全量扫描 exit 0；已知违规文件被检出
```

**检测逻辑**（AST 扫描 src/ 与 scripts/ 下 .py，排除 _archive/）：

1. **启发式1**：变量名匹配 `VALID_*_VALUES|VALID_*_STATUSES|VALID_*_TYPES|VALID_*_LEVELS|VALID_*_LAYERS|VALID_*_TTL` 且赋值为 list/set/frozenset 字面量 → 疑似词表硬编码
2. **启发式2**：变量名匹配 `*_MAP|*_SUFFIX_MAP|*_THRESHOLDS` 且赋值为 dict 字面量且键为字符串 → 疑似值属性硬编码
3. **"是否动态加载"判定**：同文件 AST 中有 `yaml.safe_load(...)` 调用，且该变量在赋值时引用了该调用的结果 → 合规；否则 → 违规
4. **DDL 例外白名单**：`sqlite_schema.py`、`depgraph_schema.py`、`audit_post_sync_commands.py` 的 SQL `CHECK(... IN (...))` 无法 yaml.safe_load，排除
5. **业务枚举白名单**：`OrderSide`、`OrderType`、`OrderStatus`、`TradeDirection` 等交易业务枚举豁免（非规则数据，是运行时业务实体）
6. **archive 排除**：`_archive/` 路径下的文件不扫描

**输出格式**：
```
WARN: src/zephyr/governance/triage.py:98 VALID_LAYERS 硬编码词表合法值(应从 layer_vocabulary.yaml 动态加载)
WARN: scripts/governance/d8_doc_sync/validate_document_ttl.py:67 VALID_TTL_VALUES 硬编码词表合法值(应从 ttl_vocabulary.yaml 动态加载)
```

**模式**：
- `--warn-only`（默认）：print 违规清单，exit 0
- `--ci`：print 违规清单，有违规则 exit 1（未来 hard block，本轮不启用）

**复用 canonical**（执行时核对现有模块）：
- `_shared.constants`（EXIT_PASS/EXIT_FINDINGS/EXIT_ERROR）
- `_shared.walk`（iter_files）
- 路径设置用 `next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists())` 范式（对齐 check_frontmatter_metadata.py:44-47）

**挂载 pre-commit**：追加 [.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) 在 GATE-GENERATE 之后：
```yaml
- id: gate-vocab-hardcode
  name: "GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）"
  entry: python scripts/governance/d3_metadata/check_vocab_hardcode.py
  args: ["--warn-only"]
  language: system
  files: ^(src|scripts)/.*\.py$
  exclude: ^scripts/_archive/
  pass_filenames: false
```

---

### 任务5：批1 词表硬编码修复（P0 + P1，非 archive）

#### 5.1 修复 validate_document_ttl.py（P0，最严重）

**文件**：[scripts/governance/d8_doc_sync/validate_document_ttl.py](file:///d:/ZephyrAlpha/scripts/governance/d8_doc_sync/validate_document_ttl.py)

**问题**：第 67 行 `VALID_TTL_VALUES = {"permanent", "periodic_review_90d", "30d", "7d", "session", "task_bound"}` 含 4 个废弃值，校验器会接受废弃 TTL。第 215 行 `ttl_thresholds` 也硬编码废弃值。

**修复**：
1. 删除第 67 行硬编码集合
2. 新增 `_load_ttl_values()` 函数（参照 [check_frontmatter_metadata.py:63-68](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L63) 范式）：
   ```python
   _TTL_VOCAB_PATH = (
       _REPO_ROOT / "docs" / "01_policies_and_standards"
       / "_registry" / "vocabularies" / "ttl_vocabulary.yaml"
   )

   def _load_ttl_values() -> set[str]:
       """从 ttl_vocabulary.yaml 加载合法 ttl 值集合（v2.0.0 仅 permanent/task_bound）。"""
       import yaml
       data = yaml.safe_load(_TTL_VOCAB_PATH.read_text(encoding="utf-8"))
       return {v["value"] for v in data.get("values", [])}

   VALID_TTL_VALUES = _load_ttl_values()
   ```
3. 第 215 行 `ttl_thresholds = {"7d": 7, "30d": 30, "periodic_review_90d": 90}` —— v2.0.0 已废除此阈值机制（二元判定无阈值），删除此行及相关逻辑（执行时核对第 210-260 行的 ttl_thresholds 消费逻辑，若已无消费方则整块删；若有消费方则改为空字典或移除）
4. 第 253 行 `if ttl == "permanent":` —— 保留（业务分支，标 `# RENAME_REVIEW` 注释，属 trae_060 §2 第三种引用）
5. 第 308 行 `choices=sorted(VALID_TTL_VALUES)` —— 自动跟随动态加载，无需改

**验证**：修复后运行 `python scripts/governance/d8_doc_sync/validate_document_ttl.py` 确认不再接受废弃值。

#### 5.2 修复 triage.py 的 VALID_LAYERS（P1）

**文件**：[src/zephyr/governance/triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py)

**问题**：第 98-115 行 `VALID_LAYERS` 硬编码 16 个 layer 值，与同文件第 86-96 行 `VALID_DOC_TYPES`（已动态加载）自相矛盾。第 73-74 行注释写着"禁止在此硬编码值名"但仍硬编码了。

**修复**：参照同文件 `VALID_DOC_TYPES` 范式（第 75-96 行），在第 96 行后新增：
```python
_LAYER_VOCAB_PATH = (
    _PROJECT_ROOT / "docs" / "01_policies_and_standards"
    / "_registry" / "vocabularies" / "layer_vocabulary.yaml"
)

def _load_layer_values() -> list[str]:
    """从 layer_vocabulary.yaml 加载活跃 layer 值列表。"""
    data = yaml.safe_load(_LAYER_VOCAB_PATH.read_text(encoding="utf-8"))
    return [v["value"] for v in data.get("values", [])]

VALID_LAYERS: list[str] = _load_layer_values()
```
删除第 98-115 行的硬编码列表。

**不碰**：`VALID_DOC_TYPES`（第 86-96 行，另一个 AI 正在处理的 doc_type 范围）。

**验证**：`python -c "from zephyr.governance.triage import VALID_LAYERS; print(VALID_LAYERS)"` 确认动态加载。

---

### 任务6：端到端验证

**验证命令序列**（连续 2 次零问题）：

1. **GATE-VOCAB**（新建脚本）：
   ```
   python scripts/governance/d3_metadata/check_vocab_hardcode.py --warn-only
   ```
   预期：validate_document_ttl.py 和 triage.py 不再出现在违规清单（已修复）；finding_state_machine.py 等后续项仍 warn（可接受）

2. **GATE-15**（ttl 校验）：
   ```
   python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files
   ```
   预期：exit 0

3. **GATE-RULE-FM**（规则 frontmatter）：
   ```
   python scripts/governance/d3_metadata/validate_rule_frontmatter.py
   ```
   预期：exit 0（trae_053 v2.0.0 + trae_060 v1.0.0 均通过）

4. **GATE-SSOT**：
   ```
   python scripts/governance/d3_metadata/validate_ssot.py
   ```
   预期：exit 0 或仅 warn（执行时核对脚本是否存在与实际行为）

5. **pytest 相关测试**：
   ```
   python -m pytest tests/unit/test_vocab_sync_chain.py -v
   ```
   预期：VALID_LAYERS 子集断言通过

6. **trae_053 修法验证**：
   ```
   python scripts/governance/d3_metadata/validate_rule_frontmatter.py
   ```
   确认 trae_053 v2.0.0 通过校验

---

## Assumptions & Decisions

1. **批1 范围聚焦 P0+P1**：validate_document_ttl.py（含废弃值，最严重）+ triage.py（有同文件正例可参照）。P2/P3 列后续，因为 finding_state_machine.py 需确认词表归属、build_status/design_maturity 需先建词表。

2. **archive 文件不修**：validate_ssot_status.py、check_frontmatter_metadata.py 旧版在 `_archive/`，已归档不维护。GATE-VOCAB 脚本会排除 `_archive/`。

3. **triage.py 只改 VALID_LAYERS 不碰 VALID_DOC_TYPES**：另一个 AI 正在处理 doc_type，避免冲突。VALID_LAYERS 修复参照同文件已有范式，风险低。

4. **GATE-VOCAB warn-only 起步**：避免一上线就阻断现有提交。待批1-批4 修复完成后，再切换 `--ci` 硬阻断。

5. **trae_053 version 直接升 2.0.0**：当前顶层 version=1.0.0 但 change_history 最新是 1.2.0（已存在不一致）。废除定时轨是不兼容变更，统一升到 2.0.0 并追加 change_history 条目，顺带修复版本不一致。

6. **DDL 例外**：sqlite_schema.py 等的 SQL CHECK 枚举无法 yaml.safe_load，走待建的 DDL-as-Code 协议（trae_060 §5 已声明），本轮 GATE-VOCAB 白名单排除。

7. **sync_yaml_to_depgraph.py 本轮不碰**：19 个 sync 函数的大规模重构是批2 范围，需单独评估"DB 作为只读缓存"的架构定位是否合理（project_memory 已声明"DB 规则表为只读缓存"），本轮不展开。

8. **CircadianScheduler/FeedbackLoopScheduler 本轮不碰**：批3 范围，依赖 trae_053 修法先行。本轮只修规则文本，不动运行时代码。

---

## 执行顺序（依赖图）

```
任务3（trae_053 修法）──┐
                       ├──→ 任务6（验证）
任务4（GATE-VOCAB 脚本）─┤
                       │
任务5.1（validate_document_ttl.py）─┤
任务5.2（triage.py VALID_LAYERS）───┘
```

- 任务3、任务4 可并行（互不依赖）
- 任务5 依赖任务4（验证命令需要 GATE-VOCAB 脚本存在）
- 任务6 依赖全部完成

**建议串行执行**：3 → 4 → 5.1 → 5.2 → 6（降低上下文切换成本）

---

## 后续轮次（本轮不做，仅记录）

- **批2 sync 多真源**：sync_yaml_to_depgraph.py 19 个 sync 函数评估"DB 只读缓存"架构定位；同名 state_synchronizer.py/blueprint_code_sync.py 物理重复收敛
- **批3 触发方式**：CircadianScheduler（circadian_scheduler.py）+ FeedbackLoopScheduler（ops/scheduler.py）+ boot_cron_jobs.py 迁移事件驱动；依赖 trae_053 修法先行
- **批4 重复实现收敛**：6 簇重复实现合并
- **P2/P3 词表硬编码**：finding_state_machine.py 回退分支、build_status/design_maturity 入词表、TTL 字面量、ai_autonomy_level 命名统一
