---
ttl: task_bound
volume: wiring_N_header_compliance
session: st-ailayer-final-20260924
creation_token: w6n-header-compliance-20260926
---

# W6-N 施工记录：本役六件新建 .py 的头部合规补齐

工作面=`.worktrees/st-ailayer-final-20260924`；零提交、零入队、零 `git add`（本册与六件均只落盘）。
铁线：不为过关伪造字段值；判据真源先读后改；禁改函数体与判据。

## 一、判据真源（读过的，不是猜的）

| 台 | 判据要点 | 真源文件 |
|----|---------|---------|
| DOC-HEADER-SUITE | 七子判据聚合：BLUEPRINT-FORMAT / BLUEPRINT-HEADER / MODULE-ID-CONSISTENCY / TTL-METADATA / FILE-PLACEMENT-TTL / EXEMPT-ZONE-FM / DOC-REF-BROKEN | `src/zephyr/gov_enforcement/commit_gates/blueprint_format_gate.py`（`_DOC_HEADER_SUITE_SUBS` 行 191-199） |
| TTL-METADATA | 经 subprocess 调 GATE-15；`.py` 走 `parse_py_header`（扫前 200 行 `# [FIELD] value`），有头部则 `ttl` 必填且值须在词表内 | `scripts/governance/d3_metadata/check_frontmatter_metadata.py`（`_FIELD_RULES` 行 100-112）；值域=`docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml`（`permanent`/`task_bound`） |
| FILE-PLACEMENT-TTL | 永久区=directory_zones.permanent.paths（仅 `docs/01|02|03|08`、`docs/_archive`、`architecture_model`）；`scripts/`、`src/` 非永久区 → 无 PROMOTION_BLOCKED；区-值配对从同册动态取 | `docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml` 行 88-99 |
| CREATE-GUARD | 新建 .py 头部**前 30 行内** MUST 齐 15 字段（a_full.required），`__init__.py` 最低 3 字段（BLUEPRINT/MODULE/DOMAIN）；creation_token 真源=capability 册 `creation_tokens` | `src/zephyr/gov_enforcement/commit_gates/create_guard.py`（`_check_field_header` 行 753-811）；字段清单真源=`docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml` `sections.gov_eng_002.field_specs` |
| STARTUP 值域 | `[STARTUP]` 合法值只有 `auto_start / event_driven / imported / manual / scheduled_task`；`scheduled` 已列 deprecated_values | `docs/01_policies_and_standards/_registry/vocabularies/startup_vocabulary.yaml`（values 行 47-66、deprecated 行 68-71）；实测报红台=`scripts/governance/d3_metadata/check_vocab_hardcode.py` |
| PERM-TRIGGER / MANUAL-ONLY | 判据=AST 时间触发（while True/time.sleep/schedule/APScheduler）或 manual 触发（argparse/input/`__main__`+sys.argv）且无事件订阅；`[STARTUP]` 文案不参与判定 | `.../perm_trigger_gate.py`、`.../manual_only_permanent_gate.py`；合法豁免通道=`noqa_exempt_registry.yaml` 的 `m11-perm-manual-legitimate`（reason_required、min 10 字、格式 `#  noqa: m11-perm-manual-legitimate␣␣M11豁免: <理由>`） |
| ALGO-FLOW-LINK | 只校验**已存在**的 `# [ALGO_FLOW] external:` 锚（锚指向 yaml 须实存且图可达）；不要求新建件必须有锚 | `.../algo_flow_link_gate.py`（INVARIANTS 行 9-25）；本役 roster 态=`enabled: false`（`in_process_gate_registry.yaml` 行 353-356，Owner B 方案临时禁用） |
| MODULE-ID-CONSISTENCY | 跨文件碰撞只对**声明了 `[A_*] module_id=` 的新增文件**生效；`[BLUEPRINT]` 仅校验格式（MOD-/SH- 双轨） | `.../module_id_consistency_gate.py`（`_check_cross_file_collision` 行 193-240）；格式真源=`scripts/governance/d3_metadata/validate_module_id_naming.py::is_valid_module_id` |

## 二、逐件改动（每行取值都给了确证出处）

### 1. `scripts/governance/fullflow/__init__.py`
新增 3 行：
- `# [BLUEPRINT] MOD-GOV_SCRIPTS`——确证：同目录族 23 件兄弟件用同一裸 id 形态（`grep -c '^# \[BLUEPRINT\] MOD-GOV_SCRIPTS' scripts/`）；`path_ownership_map.yaml` 行 570/612/9747 把 `scripts/governance/...` 的 `owner_blueprint` 记为 MOD-GOV_SCRIPTS（含 `scripts/governance/git_hooks/__init__.py`，与本件同为包标记件）；格式过 `is_valid_module_id`。
- `# [DOMAIN] D_GOV_SCRIPTS`——确证：`functional_domain_registry.yaml` 行 66 在册；同目录兄弟件（`check_frontmatter_metadata.py`/`apply_depgraph.py`/`run_fulltree_gate_audit.py`）均用该值。
- `# [STARTUP] imported`——确证：包 `__init__` 属被动导入，词表合法值。
原有 `[MODULE]`/`[TTL] permanent` 未动。`__init__.py` 最低 3 字段（BLUEPRINT/MODULE/DOMAIN）现已齐。

### 2. `scripts/governance/fullflow/generate_fullflow_crosscheck.py`（本役实测死因件）
新增 5 行：
- `# [TTL] permanent`——**原死因**：落地链报 `TTL-METADATA 阻断: missing required field 'ttl'`。取值确证：同区常驻生成器件（`scripts/ai_layer/gen_obj_r_s3_threshold_census.py` 等）用 `permanent`，且本件=常驻尺（非一次性产物）；FILE-PLACEMENT-TTL 侧 `scripts/` 不在永久区清单，`permanent` 与区不冲突。
- `# [BLUEPRINT] MOD-GOV_SCRIPTS`、`# [DOMAIN] D_GOV_SCRIPTS`——同第 1 件的确证链。
- `# [ERROR_CONTRACT] ...`——逐条从代码抄实：真源缺文件→内部 `ReadFailure` 被采集层转 `status=unavailable`+`measured=null`（行 171/553/559）；无 `.git`/git 不可跑/toplevel≠本仓根→`HeadTracking(status="unavailable", reason=...)` 不抛（行 321-340）；退出码 0=正常产出或 `--stdout`，`--check` 下产物缺失或与再生成字节不一致→1（行 1318-1325）。
- `# [TESTS] tests/governance/fullflow/test_fullflow_crosscheck_generator.py`——该测试件盘上实存（已 `-e` 验）。
新增 1 处行尾标：`if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 对账尺=车道/总筹按需手跑 CLI，非常驻自动任务，零事件订阅`——本件含 `argparse.ArgumentParser`（行 848+）且无事件订阅，属 MANUAL-ONLY-PERMANENT 的 AST 命中面；m11 通道在 `noqa_exempt_registry.yaml` 在册，形态（两空格分隔+`M11豁免:` 理由≥10 字）按 `_M11_NOQA_PATTERN` 实测匹配，同目录兄弟件（`gen_search_veins.py` 等 11 件）同形态在用。
**未动函数体一字**（判据/逻辑零改）。

### 3. `scripts/ai_layer/gen_obj_r_s3_threshold_census.py`
- 15 字段本已齐全（头行 1-20 全在 30 行窗内），`[TTL] permanent`、`[BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md` 未改——该 blueprint 文件实存且首行 `module_id: MOD-INF-037`（真源自证）。
- 唯一改动=main 守卫行尾加 `m11-perm-manual-legitimate`（同上第 2 件判据链，理由写本件实际用途：普查生成器按需手跑）。

### 4. `scripts/ai_layer/run_ai_l1_scan_tick.py`
- `# [STARTUP] scheduled` → `# [STARTUP] scheduled_task`：`scheduled` 是 `startup_vocabulary.yaml` 的 **deprecated_values**，`check_vocab_hardcode.py --ci` 实测报 WARN（本役六件里唯一该台命中）；改值不是为过关——`scheduled_task` 的定义（OS 级调度器托管 one-shot 守护、进程外托管、执行完即退）与本件真实形态逐字吻合（宿主=`scripts/register_ai_l1_scan_task.ps1`，盘上实存；本件代码零定时器零 sleep）。改成 `manual` 反而会低报真实触发面=伪造。
- 其余头行未动；`m11` 豁免行（原第 68 行）本件作者已写，未重复添加。

### 5. `src/zephyr/ai_layer/switch_engine/tombstone_ttl_proposer.py`
- 15 字段齐（头行 1-26 在窗内）；`[BLUEPRINT] MOD-INF-037 | .../registry_governance/blueprint.md | §l6_switch_engine` 未改——同目录 `switch_engine/` 6 件兄弟件全部同一 id+path 配对（族内唯一形态）。
- 唯一改动=main 守卫行尾加 `m11-perm-manual-legitimate`（本件含 `argparse`（行 358）+ 无事件订阅；理由写"月度体检窗人工 CLI 点火、只出提案不执行"，与其 `[INVARIANTS]` 零删除 API 一致）。

### 6. `src/zephyr/shared/lifecycle/registry_state_vocab.py`
- `# [BLUEPRINT] MOD-BT-188 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §lifecycle_fsm_vocab` → `# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md`。确证链三条：①同目录族 10 件兄弟里 8 件用该 id+path 对（`daemon_registry/health/health_discovery/healthcheck_service/hooks/lazy_loader/longevity_monitor/resource_optimization_models/ttl_cleanup_engine`），该 blueprint 文件实存且首行 `module_id: MOD-INF-016`；②`path_ownership_map.yaml` 把 `src/zephyr/shared/lifecycle/*` 的 `owner_blueprint` 记为 MOD-INF-016（行 7968/41596/42135/44193/45103/50458/53734/54077）；③原值 MOD-BT-188 的唯一在册归属是 `src/zephyr/strategy_pipeline/lifecycle_fsm.py`（行 8914/31825）及其测试，与 `shared/lifecycle` 无涉，而它当时所配的 path 实为 MOD-INF-037 的蓝图。此项是**按确证改回族归属**，非新造 id。
- `[TTL] permanent` 从第 32 行上移到第 4 行（并删原重复行）：CREATE-GUARD 的字段窗只扫**前 30 行**，原布局 `[TESTS]` 落在 29-31、`[TTL]` 落在 32 → 15 字段判不全。值本身未改（常驻词表对齐层）。
- `[DOMAIN] D_GOVERNANCE` 保留：在册（`functional_domain_registry.yaml` 行 130 等），且本件服务对象确实是注册表 lifecycle_status 写入边界；同目录多数兄弟件用 `D_SHARED`，属"路径域 vs 职能域"分层，本窗不改判。

## 三、故意省略的（宁缺不造）

1. **`[BLUEPRINT]` 的 path+§ 两段**（fullflow 两件只写裸 id）：`MOD-GOV_SCRIPTS` 在 `docs/03_modules/**` 里**没有任何蓝图文档以 `module_id:` 声明它**（`grep -rn "module_id: MOD-GOV_SCRIPTS" docs/` 零命中）；兄弟件虽各配 path，但所配 `docs/03_modules/_domain_governance/blueprint.md` 声明的是 `MOD-GOVERNANCE`——照抄=复制别人错配。BLUEPRINT-FORMAT 只校验 id 格式、不要求 path，故省略整段后缀不触门。
2. **`[A_module]` 八元组**：一件都不加。MODULE-ID-CONSISTENCY 的碰撞判定只对声明了 `[A_*] module_id=` 的新增件生效，加了等于把零风险面变有；且本族无该形态先例。
3. **`[ALGO_FLOW]` 锚**：一件都不加。ALGO-FLOW-LINK 判据只核"已存在锚"的 yaml 实存与图可达，无锚=不参与；新建 yaml 镜像册属净零增长门位（须申报替代条目），不在本窗。
4. **函数体一字未改**：因此下列四项**仍是本袋落地风险**（见第五节），本窗只把"头部/元数据"面清干净。
5. **`m11` 之外的 noqa**（`bare-subprocess`、`class-name-alias`）没有顺手加：这两处的真实修复面在函数体/类命名，用 noqa 遮=为过关而伪。

## 四、自验（真跑，进程内门禁）

- 自验器：`.runtime/tmp/w6n_gate_harness.py`（临时件，不入库）。从 `gate_auto_registrar.auto_register_gates(CommitGateRegistry(), Path('.').resolve())` 起装载 96 台 in-process 门，对六件清单逐台调 `spec.check(gateway, files)`；桩 gateway 把六件**模拟为全新增 staged（A 态、整文件皆 added 行）**，未碰真 index（零 `git add`）。运行前自证 `zephyr.__file__` 落在本 worktree（实测=`.worktrees/st-ailayer-final-20260924/src/zephyr/__init__.py`）。
- 头部族结果（六件全绿）：DOC-HEADER-SUITE（含 TTL-METADATA / FILE-PLACEMENT-TTL / EXEMPT-ZONE-FM / DOC-REF-BROKEN / BLUEPRINT-FORMAT / BLUEPRINT-HEADER / MODULE-ID-CONSISTENCY）、GATE-DOMAIN-FK、TRANSLATION-COVERAGE、NOQA-VALIDATION、ID-UNIQUENESS、REFERENCE-INTEGRITY、ENCODING-SAFETY、R5-DIGIT-SUFFIX、DIRECTORY-CONTRACT、SYNTAX-VALIDATION、TEST-SOURCE-CONSISTENCY。
- 独立真源直跑：`check_frontmatter_metadata.py --strict-doctype <六件>` → `OK: Frontmatter validation passed (6 files checked)` rc=0；`check_vocab_hardcode.py --files <六件> --ci` → `OK: No vocabulary hardcode issues found` rc=0（改 `[STARTUP]` 前为 FOUND:1）。
- 尺族回归：`python -m pytest tests/governance/d3_metadata -p no:cacheprovider -c py.ini -q --timeout=300` → 201 passed，零回归。
- `python -m ruff check <六件>` → 仅剩 1 条 `F541`（`generate_fullflow_crosscheck.py` 行 1333 `print(f"counts: " + ...)`，属他道在途新代码区，本窗禁改函数体→未动，转总筹）；`Invalid # noqa directive` 4 条 warning 是本仓自定义 m11 码的既有形态（11 个兄弟件同态），非 error。

## 五、本役仍可能撞的门（供总筹预判，全部非头部面）

| 台 | 命中件 | 性质 | 处方（本窗无权做） |
|----|-------|------|-------------------|
| DEPGRAPH-ENFORCEMENT[NEW-FILE-DEPGRAPH-ENFORCEMENT] | 六件全部 | depgraph nodes 无记录 | `python scripts/governance/apply_depgraph.py --add-design-node <file> <module_id> <domain_id> --granularity file`（module_id 用本册第二节的确证值，勿另造）或施工毕 `generate_project_depgraph.py --force` |
| ORPHAN-MODULE | `registry_state_vocab.py` | src/ 新增件零 import（其 `[CONSUMERS]` 自陈"待接线一行"）；该门无 noqa 通道，只豁免入口件 | 同袋带上 `strategy_pipeline/promotion_advisory` 的接线，或本件随接线批一起落 |
| SSOT-REDEFINITION | `gen_obj_r_s3_threshold_census.py` | 自造 `REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]`，canonical=`src/zephyr/shared/io/paths.py` | 改 import 走 canonical（函数体/顶层赋值改动，超本窗授权） |
| CREATE-GUARD（CLASS-UNIQUENESS） | `gen_obj_r_s3_threshold_census.py` | `class Finding` 与 4 处同名 | 改名或按判据加 `# class-name-alias: <理由>`；理由须说明"合法 re-export"，本件不是 re-export，故不代填 |
| COMPLEXITY-GUARD[NO-HIGH-COMPLEXITY] | `generate_fullflow_crosscheck.py` | `collect_claims`/`build_coverage`/`build_payload` 圈复杂度 24/18/21 >15 | 拆分函数（禁改逻辑面，须作者车道自修） |
| BARE-SUBPROCESS | `generate_fullflow_crosscheck.py` | 裸 `subprocess.run` | 改 `run_subprocess_hidden`，或按判据补 `# noqa: bare-subprocess  <reason>`（须写明为何不需 CREATE_NO_WINDOW） |
| COMMIT-SCOPE | 六件混袋 | 判出 2 域：`D_GOV_SCRIPTS`（fullflow 两件）+ `D_GOVERNANCE`（其余四件） | 拆两袋（fullflow / ai_layer），或 `git_commit.py --allow-multi-domain` 留痕 |
| STATE-VOCAB-REGISTRY | — | 首轮 harness 曾报 `NameError: name 'registered' is not defined`（判定体自身崩），末轮未复现；该件正被 W 他道改 | 落地前由他道修台；勿随袋代修 |
| SESSION-REQUIRED / PERMANENT-SYSTEM-TRIGGER / MANUAL-ONLY | — | 前者=自验器未传 session_id 的桩态（真提交链必传，非风险）；后两台当前 `enabled: false`（Owner B 方案）| 若恢复启用，m11 豁免行已按在册形态预置 |

## 六、复核命令

```
cd D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:$PATH"
# 1) 头部 15 字段 + 30 行窗（CREATE-GUARD 口径复算）+ AST
python -c "import re,yaml,pathlib;r=pathlib.Path('.');fs=yaml.safe_load((r/'docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml').read_text(encoding='utf-8'))['sections']['gov_eng_002']['field_specs'];req=fs['a_full']['required'];init=fs['init_min'];\nimport sys;\n[print(f, [x for x in (init if f.endswith('__init__.py') else req) if not re.search(rf'#\s*\[{re.escape(x)}\]', chr(10).join((r/f).read_text(encoding='utf-8',errors='replace').split(chr(10))[:30]))]) for f in sys.argv[1:]]" scripts/governance/fullflow/__init__.py scripts/governance/fullflow/generate_fullflow_crosscheck.py scripts/ai_layer/gen_obj_r_s3_threshold_census.py scripts/ai_layer/run_ai_l1_scan_tick.py src/zephyr/ai_layer/switch_engine/tombstone_ttl_proposer.py src/zephyr/shared/lifecycle/registry_state_vocab.py
# 2) TTL 真源 + 词表真源
python scripts/governance/d3_metadata/check_frontmatter_metadata.py --strict-doctype <六件>
python scripts/governance/d3_metadata/check_vocab_hardcode.py --files <六件> --ci
# 3) 进程内全门禁（96 台，六件模拟为新增 staged）
PYTHONPATH="$PWD/src" python D:/ZephyrAlpha/.runtime/tmp/w6n_gate_harness.py
# 4) 尺族回归 + lint
PYTHONPATH="$PWD/src" python -m pytest tests/governance/d3_metadata -p no:cacheprovider -c py.ini -q --timeout=300
python -m ruff check <六件>
```

## 七、三态结论

- **已达成**：六件头部面合规（15 字段齐且在 30 行窗内；ttl 值合法且与放置区不冲突；STARTUP 值从 deprecated 迁到在册合法值；[BLUEPRINT] id 全部走确证链，无一处自造；m11 豁免按在册形态预置）。DOC-HEADER-SUITE 七判据 + GATE-DOMAIN-FK + 词表面 + 尺族 201 测试全绿，零回归。
- **未达成（超窗，如实报）**：六件仍有 6 台非头部面门禁可拦（DEPGRAPH 登记、ORPHAN 接线、SSOT 重定义、类名唯一、复杂度、裸 subprocess），其中四项须改函数体——本窗明令禁改，交作者车道/总筹。
- **hazards**：`generate_fullflow_crosscheck.py` 本窗期间被外来写两次整档重写（879→1290→1349 行，mtime 03:51/03:5x，Edit 工具两次报 "file changed since your last read"），我的头行与 main 守卫 noqa 目前仍在；落地前须再跑一遍第六节命令 1)、2) 复核，勿以本册时点为终态。
- **index 弹（本窗最大雷，落地必读）**：六件在工作树 index 里是 `AM` 态——**index blob 仍是补头前的旧字节**（实测 `git show :scripts/governance/fullflow/generate_fullflow_crosscheck.py` 内 `[TTL]` 命中 0；`:src/zephyr/shared/lifecycle/registry_state_vocab.py` 首行仍是 `MOD-BT-188`；`:scripts/ai_layer/run_ai_l1_scan_tick.py` 第 7 行仍是 `scheduled`）。内容型门禁读 index 不读盘面，故**本窗零 `git add` 是刻意的**（按任务书"零提交零入队零 git add"），但落地车道若不重新 `git add` 这六路径，TTL-METADATA 会照旧报 `missing required field 'ttl'`——修了盘上却死于旧 blob。复核：`git diff --cached --name-only` 与盘面逐件比 sha。

