---
ttl: task_bound
volume: 01_state_vocabulary_lane
session: st-ailayer-final-20260924
creation_token: fullflow-p0-state-vocab-lane-20260926
---

# 01 · 状态词表与状态机登记治理环节（P0，二验成立）

> 成立来源＝对账表 **B-12（REG-STATE-VOCAB-001）＋ A-1（TDM `state_matrix` 段）＋ B-15 之 REG-SM-001（`src/zephyr/shared/_state_machine_registry.yaml`）**，三行同真源可派生→按宪法 §4.2 并为**一个**新环节，不拆三环。
> 二验结论：**F01–F122 无此环节**；本环节持有一道**真实在拦的 pre-commit 门禁**＋47 份词表数据＋一份 Owner 批准的状态矩阵，却**登记面三重断链**（ROOR 指向文件不存在／门声明的测试文件不存在／环节无 F 位）。

## 一、环节定义与边界

- **做什么**：①为全仓"状态/阶段/市况/情绪/模式"枚举提供**中央登记真源**（state_vocabulary_registry.yaml，制度名"词表 SSOT 制度 W3 执行门"）；②立法并维护业务侧封闭词表（`_registry/vocabularies/*.yaml` 47 份＋TDM `state_matrix` 六段相位）；③在提交面拦截未登记的新状态枚举类；④登记跨模块状态机（`_state_machine_registry.yaml`）与词表的对应关系。
- **不做什么**：不做单个 FSM 的业务语义（那是 F53/F60/F75/F36 各环自家状态机）；不改词表内容判据（六段温度已裁，见 §五）。
- **边界冲突（已识别）**：与 F38（六传感器→7 态）、F75（生命周期五态/注册表八态）、F53/F60（订单/回撤状态机）是"**登记面 vs 业务面**"关系——各环持有状态语义，本环节持"有没有登记、拼写是否唯一、下游是否同步"的治理真源。F75 姊妹册（`../03_promotion_ab/04_lifecycle_fsm.md` §四）实测的"三套词表并存、production 越界写入注册表"**正是本环节缺位的事故产物**（那里 3.6 行"词表对齐层缺位"＝本环节的缺位）。

## 二、六向台账

| 向 | 内容与实测证据 |
|---|---|
| 上游输入 | ①各模块新定义的状态枚举类（AST 扫描入面：类名含 state/phase/regime/emotion/mode 且类体 ≥3 个全大写字面量赋值，实测 gate 自述 docstring :24-31）；②TDM `state_matrix` 段（`config/trading_decision_map.yaml:5556`，本册实测 47 行，Owner 批准真源——引 `../00_skeleton/90_crosscheck_link_census.md:40` 与 F 册消费面）；③立法件 `docs/_working/vocab_legislation/01_official_state_vocabulary.md`＋`02_state_vocabulary_mapping_register.md`（两件均在盘） |
| 下游消费 | 实测读 `_registry/vocabularies/` 的代码/脚本 8 件：`src/zephyr/autonomy_core/module_factory/knowledge_classifier.py`、`src/zephyr/governance/audit/reconciliation_registry.py`、`src/zephyr/governance/depgraph_schema.py`、`src/zephyr/governance/persistence/decisiongraph_schema.py`、`src/zephyr/gov_enforcement/commit_gates/file_placement_ttl_gate.py`、`src/zephyr/gov_enforcement/rule_enforcement/g2_triage.yaml`、`_registry.yaml`、`src/zephyr/integration/mcp/gate_engine_server.py`；TDM `state_matrix` 消费实测 5 件：`trading/decision_map.py`、`strategy_pipeline/daily_decision_orchestrator.py`、`signal_ashare/core/environment_switch.py`、`pf_alloc/allocation_inputs.py`、`scripts/backtest/auto_mount.py` |
| 自动化触发 | ①**提交事件**：`STATE-VOCAB-REGISTRY`（`in_process_gate_registry.yaml:646`＋`gate_registry.yaml:1311`，entry=`in-process (GitCommitGateway)`，`own_scope: true`，`status: active`）；②`GATE-VOCAB`（`gate_registry.yaml:185`，status=active，source=pre-commit，entry 两条：`scripts/governance/d3_metadata/check_vocab_hardcode.py --ci`（55,338 字节在盘）＋`generate_derived_files.py --check`（26,408 字节在盘））；`files_trigger` 覆盖 `^(src/zephyr/.*\.py|scripts/.*\.py|docs/01_policies_and_standards/_registry/vocabularies/.*\.yaml)$`。**无 cron/Timer**（合宪法 §9.3 事件触发）。 |
| 真源与注册表 | ROOR `REG-STATE-VOCAB-001` @`docs/registry_of_registries.yaml:252`（name=状态词表中央登记表、maintenance=manual、entry_count=29、status=**active**、描述称"官方词表本体=zephyr.shared.vocab.market_state（SH-VOCAB-001）"）；门自身的制度真源＝`docs/_working/daily_loop_campaign/03_self_ruling_vocab_ssot.md`（在盘）；数据真源＝`_registry/vocabularies/`（47 个 yaml，实测）；状态机登记真源＝`src/zephyr/shared/_state_machine_registry.yaml`（实测在盘）。**F 体系真源＝无**（F 册 `grep 词表`/`vocabulary`＝0 命中） |
| 门禁与质量尺 | `GATE-VOCAB`（硬编码检测＋派生文件一致性）＋`STATE-VOCAB-REGISTRY`（AST 登记查）。**尺子质量实测有硬伤**：gate 的 `[ERROR_CONTRACT]` 自述"check 永不抛异常——AST/IO/yaml 异常**降级为 fail-open**（passed=True）"，而它要查的登记文件 `catalogs/state_vocabulary_registry.yaml` **实测不存在**（FILE-MISSING）→ IO 异常路径恒被触发 → **该门在当前仓态下结构性 fail-open（恒绿）**；同时 `[TESTS]` 声明的 `tests/gov_enforcement/test_state_vocab_registry_gate.py` **实测不存在** → 无配对测试可证伪（按 Owner 明令"恒绿无配对测试＝疑似判据失效"） |
| 当前运行状态 | **红**（三处实测：①ROOR 宣称 active 的物理文件不存在；②ROOR 宣称的"词表本体包"`src/zephyr/shared/vocab` 不存在（最接近件只有 `signal_ashare/market_state_sensor.py`）；③拦截门因①恒 fail-open 且无测试）。环节面＝F 册无位（黄→红由上述断链定级）。复跑命令见 §七 |

## 三、子模块清单（ls＋grep＋注册表交叉实测，非凭记忆）

| # | 子件 | 实测锚点 | 状态 |
|---|---|---|---|
| 3.1 | 词表登记观察门（AST 扫 staged .py） | `src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py`（in-process，由 `gate_auto_registrar` 驱动） | 红（目标登记文件缺失→fail-open；声明测试缺失） |
| 3.2 | 词表硬编码门禁（.py 侧） | `scripts/governance/d3_metadata/check_vocab_hardcode.py`（55,338 B）＋ `gate_registry.yaml:185` | 黄（在跑，判据与 3.1 是否重叠未逐条比对） |
| 3.3 | 派生文件一致性检查 | `scripts/governance/d3_metadata/generate_derived_files.py --check`（26,408 B） | 黄 |
| 3.4 | 业务封闭词表数据面 47 套 | `docs/01_policies_and_standards/_registry/vocabularies/*_vocabulary.yaml`（实测 47 件，含 `contract_status`、`decision_layer`、`decision_edge_type`、`category`、`classification`、`compliance_tags` 等） | 绿（数据在盘，消费方 8 件实测） |
| 3.5 | 状态机中央登记 | `src/zephyr/shared/_state_machine_registry.yaml`（ROOR `REG-SM-001` @`:557`） | 黄（登记与 3.1 门是否互查未证） |
| 3.6 | 六段相位/TDM 状态矩阵视图 | TDM `state_matrix` @`config/trading_decision_map.yaml:5556`（47 行）＋消费 5 件 | 黄（消费在跑，无 F 位，无登记关系） |
| 3.7 | 词表立法件与映射登记册 | `docs/_working/vocab_legislation/01_official_state_vocabulary.md`、`02_state_vocabulary_mapping_register.md` | 绿（两件在盘；r4 归属两版相反属技术收敛待办，**非门位**） |
| 3.8 | 中央登记本体文件 | `docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml` | **不存在（本环节核心病灶）** |

## 四、堵点与病灶

| # | 现象（实测） | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | 登记真源文件 `state_vocabulary_registry.yaml` 不存在，ROOR 却登记 status=active | 门先建、册未产（W3 执行门上线时登记册未初始化），无 ROOR 悬空校验 | 生成器扫全仓状态枚举类出初版登记册（条目数与 3.4/3.5 交叉对账）→ ROOR 保持 active 才名副其实 | 1 施工袋 | 否（本车道禁新建 .py） |
| 2 | 门因文件缺失恒 fail-open，且声明的测试文件不在盘 | `ERROR_CONTRACT` 设计成"IO 异常=放行"＋无配对测试 | ①补登记册后让路径存在；②补 `tests/gov_enforcement/test_state_vocab_registry_gate.py` 钉"未登记类必产生 warn 留痕"与"文件缺失时须报红而非放行"两条 | 1 施工袋（同批） | 否 |
| 3 | 环节在 F 体系无位 → 派单不覆盖、六向无人认领 | 122 集合不完备（本战役结论） | 在 F 册新增一行（建议段 K，占位编号待总筹定），真源字段挂 ROOR+47 词表+TDM 段 | 文档改动（总筹落地） | 否（F 册是他棒真源册） |
| 4 | 三套/四套状态词表并存（F75 姊妹册实测 production↔live 越界、shelved 无值、decayed 死态） | 本环节缺位导致各环自造词表、无对齐层 | 由本环节提供"注册表词表↔FSM 词表"映射件；**方向须治理裁定**（F75 册已列两选一，不在此重裁） | 1–2 施工袋 | 否（待裁） |
| 5 | `state_matrix`（Owner 批准真源）与 3.4 词表 47 套之间的"谁派生谁"未登记 | 双真源并存、无派生声明 | 机生派生图：TDM 段 → 词表条目逐条对应；禁散文复述计数（宪法 §4.3） | 小 | 否 |

## 五、内收与合并机会（w5_1 四判据逐条）

1. **同真源可派生→必并**：B-12＋A-1（state_matrix）＋B-15 的 REG-SM-001 三行并入本 1 环（本册即合并结论）；F 册若已新增这三行会造三条假环节。
2. **同域重复簇→收敛唯一**：`GATE-VOCAB`（脚本链）与 `STATE-VOCAB-REGISTRY`（in-process）判据重叠面须做一次合并审计——**但门禁处置只能"合并/降档/diff 化"，夜间不执行退役**（既有 Owner 明令档），故本车道只登记该机会，不提删除。
3. **跨域不同对象→不并**：F53/F60/F75 各环**业务状态语义**不迁入本环节；本环节只做登记与查名；F88 LSG（LLM 防御）无关。
4. **零触发零消费→退役**：本环节零适用——有触发（pre-commit）有消费（8 件实测）→ **不退役，必须建**。
5. 与既有环节的挂接义务：F38/F75/F53/F60/F36 各册应在真源字段反向引用本环节新行（否则又是登记面欠账）。

## 六、自审闸三态

**挖干可施工**——六向均有 file:line 或可复跑命令实测输出；三处"红"为断链实证而非推测。
可派下一波的施工范围（不在本车道做）：①生成中央登记册 ②补配对测试并改 fail-open→报红 ③F 册新增环节行（占位编号交总筹）④派生图机生。
**待挖**：3.2 与 3.1 判据重叠的条目级比对（未做）；ROOR 悬空路径全仓普查（属另一施工袋，见对账表 V-5）。
**待裁**（已写 `pending_rulings.md`，本车道不自赋裁定号）：词表对齐方向（F75 册 §五 堵点 1 的两选一）；`GATE-VOCAB`×`STATE-VOCAB-REGISTRY` 合并方案（涉门禁处置＝Owner 门位）。

## 七、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version   # 3.12.8
# 1 环节无位：F 册零命中（预期 0 / 0）
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
grep -c "词表" $S; grep -c "vocabulary" $S
# 2 门禁真实在拦（预期两条 gate_id 命中，status: active）
GR=docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
grep -n "gate_id: GATE-VOCAB" -A9 $GR | cut -c1-140
grep -n "gate_id: STATE-VOCAB-REGISTRY" -A10 $GR | cut -c1-120
grep -n "STATE-VOCAB-REGISTRY" docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml | head -3
# 3 三重断链（预期全部 NOT-EXIST / No such file）
ls docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml 2>&1 | tail -1
ls -d src/zephyr/shared/vocab 2>&1 | tail -1
ls tests/gov_enforcement/test_state_vocab_registry_gate.py 2>&1 | tail -1
sed -n '11,14p' src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py | cut -c1-150   # fail-open 契约＋TESTS 声明
# 4 数据面规模（预期 47）与消费方（预期 8 件）
ls docs/01_policies_and_standards/_registry/vocabularies/ | wc -l
grep -rln "vocabularies/" src/zephyr scripts | grep -v __pycache__ | head -8
# 5 TDM 状态矩阵与消费（预期 47 行 / 5 件）
awk '/^state_matrix:/{f=1;next} /^[a-z_]*:/{f=0} f' config/trading_decision_map.yaml | grep -c ":"
grep -rln "state_matrix\|portfolio_plan" src/zephyr scripts | grep -v __pycache__ | head -8
# 6 状态机登记册在盘
grep -n "registry_id: REG-SM-001" -A5 docs/registry_of_registries.yaml | cut -c1-130
ls -l src/zephyr/shared/_state_machine_registry.yaml
```
