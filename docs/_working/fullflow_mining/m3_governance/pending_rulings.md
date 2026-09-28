---
ttl: task_bound
volume: pending_rulings
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-m3-pending-rulings-20260926
---

# m3_governance · 待裁清单（车道 W4-B 补七案，编号 W4B-G1…W4B-G7）

> 铁律：**本车道不自赋裁定号、不写"Owner 已裁"**；W4B-Gn 是本车道内部流水，非 `ruling_registry.yaml` 裁定号。
> 案源=本目录三册：`05_f100_adversarial_validation.md`、`06_f103_clone_guard_code_dedup.md`、`07_rollback_recovery_infra.md`（第三格刻意不挂环号，判"待挖"，见其 §六）。
> 门位口径依宪法 §5：production 流转／注册表净删／flag 出厂翻转／资金破坏＝Owner（high）。

| # | 问题 | 已试路径（实测） | 选项 | 建议 | 门位属性 |
|---|---|---|---|---|---|
| W4B-G1 | 红蓝对抗**不在 `gate_registry.yaml`**（grep `adversarial\|red.blue` = 0 命中），但门件真实存在两份实现（`feedback_loop/gates/adversarial_validation.py`、`gov_enforcement/rule_enforcement/gate_engine/adversarial_validation.py`，同 module_id=MOD-GATE_ENGINE）→ 该环节在机读门禁体系里**无名**，F98 侧无法索引 | 见 `05_f100` 册 §二"真源与注册表"向；外部接线实测 6 处（boot_hooks:755、lifecycle_manager:4、gov_audit/cli:154、audit_admission_controller:73、feedback_loop/gates:138、gate_engine:2） | a＝gate_registry 增 `GATE-RED-BLUE`（含 own_scope 字段，机生勿手改）；b＝显式登记"属运行时/post-commit 门，不进 pre-commit"并给"门件↔gate_registry 覆盖差"加漂移尺；c＝维持无名 | **b 先行＋a 缓**：先把"哪些门件无机读身份"量出来（漂移尺），再决定逐条注册；直接 a 会绕过 own_scope 机生纪律 | 治理门（medium）；gate_registry=热册，本车道不改 |
| W4B-G2 | 红蓝**两层开关真源不清**：`config/flags.yaml:86 enabled: true`＋`:88 auto_game_day: true`，但实跑还须 env `ZEPHYR_RED_BLUE_AUTO_ENABLED=1`（`commit_trigger.py:31/84/169` 明写"否则只 log + 清队列（fail-closed）"），仓内**无该 env 的出厂置位证据** → "auto_game_day 已开"可能是纯账面 | 读 flags.yaml :83-92；读 commit_trigger 三段；主仓 `data/red_blue/trigger_queue/` **确有队列文件**（生产者真发生，故不得称"零触发"）；boot_hooks:752 注释自述关态行为 | a＝"是否实跑"收归 flags 单真源、env 仅临时覆盖；b＝env 保留但在部署册/SECRETS 登记出厂值＋关态留 L6 审计；c＝判"未验证"长期挂账 | **a＋关态审计**（与 m4 车道 W4B-M4-3 同型病灶，建议并案裁一次通则："运行时闸门不得存在无声旁路"） | 治理门（medium）；**若改 flags 出厂值＝flag 翻转 → Owner（high）** |
| W4B-G3 | 红蓝**同一功能三条模块路径并存**：真身 `src/zephyr/security/adversarial_validation/`；`config/blueprint_routing.yaml:714` 指 `src/zephyr/autonomy_perm/red_blue_validator/**`；`scripts/construction/_e2e_deep.py:59` 写 `zephyr.shared._cross_layer.red_blue_validator` | 三处 grep 命中实测（`05_f100` 册病灶 4）；未做件级比对 | a＝三路径归一并 `generate_project_depgraph.py --force` 重建；b＝只登记"别名/历史路径"注记；c＝判 autonomy_perm 侧为独立退役件出清单 | **b 先行**（遵更正 5"只登记不改动"；改名牵 RENAME-DEPGRAPH-SYNC 与翻译册，须专袋） | 治理门（medium）；**若走改名/删除 → Owner（high）** |
| W4B-G4 | **静态计数三源自相矛盾**（红蓝两册）：ROOR REG-RB-001 `entry_count: 53` 而同条目 description 写"**24 个**红白对抗攻击场景"；原始行计数式实测得 55/46（≠53/44）；总册 :175 又写"53+44" | `sed -n '538,556p' docs/registry_of_registries.yaml`；`grep -c "id:" _scenario_registry.yaml`=55、`_constitution_registry.yaml`=46（本车道**不认这把尺为权威**，仅证口径不齐） | a＝计数只留字段、删散文数字，字段由 loader/生成器回写；b＝定义统一计数规则（如按 scenario_id 顶层键）并三处同批刷新；c＝只登记矛盾 | **a＋b 同批**（违宪法 §9.5 与 §4.3"文档矛盾=事故"；ROOR=热册，交总筹单点写） | 纯口径刷新（low）；但 ROOR 变更必经总筹单点（并发纪律） |
| W4B-G5 | **宪法引用的 API 在盘上不存在**：`AGENTS.md` §1 补充铁律写"写前预查 `clone_guard.check_before_write`，合理重复走 `resolve_finding`"，实测两函数名在 `src/`+`scripts/` **零定义零调用**；实现侧真实语义=事后 `CloneGuardOrchestrator.check(staged_files)`（`orchestrator.py:316`）＋配置内静态 acknowledged 对（:168/:275） | 两条命令互证（`06_f103` 册 §七第 2 条）；读 orchestrator 全公共面（check/audit/compare/…） | a＝改宪法措辞为实测口径（"commit 前经 capability_overlap_gate 复检；合理重复登记进 `clone_guard.yml` acknowledged 对"）；b＝补 `check_before_write()`/`resolve_finding()` 薄封装使引用可解析；c＝加"宪法符号引用可解析性"尺（防复发） | **a＋c**（b 为一句引用造两个 API，违 §4.1 全资产净零；c 是治本——宪法是唯一必读，其指针必须可机械解析） | 治理门（medium）；**改宪法文本＝热文件，总筹／Owner 落地** |
| W4B-G6 | **同一枚 GATE-DEDUP 四处自述互斥**：`.pre-commit-config.yaml:1001`="阶段1 stages:[manual]，不阻断常规 commit"；`gate_registry.yaml:566 always_run: false`；`rule_enforcement/gate_dedup.yaml`=`auto: true`＋`on_failure: "reject"`；`code_dedup/exit_codes.py:47`="ERROR → 阻断 commit" → 提交面到底阻不阻断无单一真源（克隆守卫因此在提交面**是 warn/manual 级**，而宪法称"extract 级克隆无逃生"） | 三源逐行读（`06_f103` 册 §七第 3 条）；实测 `capability_overlap_gate` 在 commit 真调 orchestrator（:262/:270/:337）；`create_guard.py:96` 记 overlap 门为 warn-only | a＝以 hook＋gate_registry 为运行真源，规则 YAML 改标 `stage: manual`；b＝直接把门升为硬阻断（阶段2）；c＝先取一次"extract 级克隆被真拦"样本再定 | **c→a**（未证"无逃生"是否由 create_guard 兜住前就升硬阻断，会连坐无辜提交；B4 教训：`always_run`/own_scope 字段机生勿手改） | 治理门（medium）；**门禁强度变更（b）＝Owner（high，production 侧风险）** |
| W4B-G7 | **回滚恢复格本车道判"待挖"未挂认领锚**：该格（infrastructure/rollback，总册标 built/P1）目录本体实测 55 个 .py，但六向缺 3 向（下游消费／自动化触发注册名／门禁是否真跑）；另见三对同名异体嫌疑（`budget_tracker`↔`rollback_budget`、`contract`↔`contracts`、`rollback_integration`↔`rollback_boot_integration`）与"55 件 vs 常识规模不匹配"的规模问题 | `ls` 全量清单（`07_rollback_recovery_infra.md` §三）；三源交叉未完成（`grep` import 反查与注册表侧未跑，属限量取证）；未跑任何 DB 写 | a＝派下一取证窗补三向（该册 §六 已写最小观测量）；b＝现在就开簿挂锚（＝假 covered，本车道拒绝）；c＝判该格为"未生效"并降 built→partial 回写总册 | **a，并采 c 作回写口径**；三对同名异体在 §七第 5 条零消费实测后再按 w5_1 判据②出**退役判据清单**（不删不改名） | 治理门（medium，回写总册）；**注册表净删＝Owner（high）** |

## 复核命令

```bash
grep -n -i "adversarial\|red.blue" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | wc -l
sed -n '560,572p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
grep -rn "check_before_write\|resolve_finding" --include=*.py src/ scripts/ | wc -l
ls src/zephyr/infrastructure/rollback/*.py | wc -l
```
