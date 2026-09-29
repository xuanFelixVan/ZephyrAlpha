---
ttl: task_bound
title: F98 GateEngine 运行时门禁——挖干案卷
session: zc-l10-20260927
updated: 2026-09-29
---

# F98 · GateEngine 运行时门禁（91 canonical+GatePipeline+MAD 准入）

> 总册行（00_全环节总册.md:173）：built｜上游 规则｜下游 全链｜P1｜G2
> 第一证据源：fullflow_mining/m3_governance/03_registry_families.md＋wiring_gap_inventory_20260927.md §1.6＋src/zephyr/gov_enforcement/rule_enforcement/

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 规则面：docs/01_policies_and_standards/rules/ 86 trae_*.yaml（F101）＋rule_enforcement/ 内 45 个 g_trae_*.yaml 门定义（本日 ls 计数：g_trae_003..059 缺 13/14/15/19/55-58 号段） |
| 下游消费 | 全链提交面（commit_gates 114 模块）＋运行时面（in_process 册 102 门）＋admission 准入面 |
| 自动化触发 | commit/merge 事件经 GitCommitGateway；in_process 门经 gate_auto_registrar YAML 驱动注册；名册机生=generate_gate_registry.py post-commit reconciler GATE-GATE-REGISTRY-SYNC（M3 03 分册 §二） |
| 真源与注册表 | canonical 名册=src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml（**本日 grep gate_id: = 91，与总册一致**，MOD-GATE_ENGINE，last_updated 2026-09-18）；门总册=catalogs/gate_registry.yaml（total_gates 180，auto 机生 2026-09-24T07:29:34Z，M3 03 实测）（已过时，见刷新批注——T14 regen 后现 183）；in_process 册=102/102 自洽（现 104/104） |
| 门禁与质量尺 | 门禁的门禁=invariants/（en_001 循环依赖/en_002 执法验证器/en_003 契约兼容/en_process_lifecycle_gateway/post_doc_review_check/zero_residue_check，7 .py 本日计数）＋gate_integrity_guard.py＋gate_health.py |
| 当前运行状态 | **built（黄）**：引擎与名册在产，但名册三账漂移 114/102/180（M3 03 §四）＋机判面 43 门疑似判据失效（§1.6/本卷 §三） |

## 二、子模块三级枚举（rule_enforcement/ 五子包，本日 wc/ls 实测）

1. **gate_engine/（9 .py，2891 行）**：gate_engine.py（1820 行，class GateEngine:1427，evaluate:1573）｜gate_pipeline.py（172 行，统一 GateResult+AND/OR/NOT 组合+并行 beta+from_engine_step 工厂桥接旧版）｜gate_context.py（185）｜gate_override.py（130）｜gate_simulator.py（91）｜gate_health.py（108）｜gate_integrity_guard.py（132）｜adversarial_validation.py（205）｜__init__（48）。gate_types.py（包根）=GateViolation:42/GateResult:52/GateEngineError:77。
2. **invariants/（7 .py）**：en_001_circular_dependency＋yaml｜en_002_enforcement_validator＋yaml｜en_003_contract_compatibility＋yaml｜en_process_lifecycle_gateway｜post_doc_review_check｜zero_residue_check。
3. **rule_engine/（5 .py，466 行）**：rule_engine.py（263，RuleLoader:79）｜rule_canary_manager.py（76）｜rule_shadow_runner.py（58）｜rule_debt_auditor.py（43）｜__init__（26）。
4. **admission/（MAD 准入，5 yaml）**：mad_001_architecture_necessity（"新模块创建前的架构必要性质询"，SSoT 指本卷 _registry.yaml）｜mad_002_phase_relevance｜mad_003_dependency_compliance｜mad_004_interface_definability｜mad_005_dependency_graph_template。
5. **task/（1 .py+3 yaml）**：__init__＋g0_entry.yaml＋g0_orc_gate_engine.yaml＋g7_orc_gate_engine.yaml。
6. **包根门定义面**：45 个 g_trae_*.yaml＋g1-g9 业务门 yaml＋_registry.yaml(91)＋_template.yaml＋gate_dedup/zero_residue/observability_baseline 等 yaml＋约 30 个独立 .py 门模块（quality_gate/secrets_guard/cbac_matrix/triple_alignment 等）。

## 三、接线四态独立复核

- 总册判 **built**：引擎面成立（GateEngine/GatePipeline/invariants/MAD 全实存在产）；但**接线质量面本日独立复核发现四态分化**，机判产物复跑（.runtime/tmp/mine_dossiers_20260926/census_raw.json）：
  **169 门四态 = 真执法(初判) 104 ＋ 疑似判据失效(无配对测试) 43 ＋ 装饰(装载通道缺失) 19 ＋ 装饰(enabled=false仍claim active) 3**。
- 与清单 §1.6 散文口径（43 疑似/装饰 9/半接线 2）差异说明：43 一致；"装饰/悬空 9"是 19+3=22 装饰中的**点名子集**（停用链 4＋悬空 4），两口径分组镜头不同、非矛盾——引用须注明出处。
- **骨架勘误/补强**：宪法 17 条映射中 RULE-SSOT/RULE-DATA-OPS/RULE-SCHEMA-TZ/RULE-RULING 四条执法件落"疑似判据失效/半接线"（GATE-SSOT-CODE、check_tick_duplication、GATE-GEN-NO-REALTIME-TIME、RULING-REFERENCE 零配对红证）——built 判定对这四条成立度打折，建议总册 F98 行状态注记补"（43 门疑似失效在案）"。

### built 缺口施工最小集建议
1. 43 疑似门逐门"配对测试补齐/合并/降档/diff 化"三分处置（Owner 令已定调：不判可删）。
2. 三口径名册（模块 114/in_process 102/总册 180）对账生成器化（M3 03 G1 修法：generate_gate_registry.py 扩展三口径 diff 段）。
3. own_scope 67 条字段缺失补机生缺省值（M3 03 G2，S 工作量）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | 43 门疑似判据失效（装载√无配对测试，含 4 条宪法执法件） | Owner 令三分处置+逐门配对红证 | P0 |
| G2 | 停用虚报 3（名册 claim active 但 manifest enabled=false：ALGO-FLOW-LINK/CAPABILITY-OVERLAP/PERMANENT-SYSTEM-TRIGGER+MANUAL-ONLY） | 名册三账对账生成器化+虚报修正 | P0 |
| G3 | 悬空 4（COMMIT-CRITICAL-SECTION-LOCK/GATE-ZR/GATE-DRIFT/GATE-ERRCODE 无钩子无启动器） | 挂载或退役二选一，禁悬空 | P1 |
| G4 | 半接线 2（GATE-ERRCODE 单脚本顺带调；VOCAB-CHAIN 两面等价性未证） | 等价性红证补齐 | P1 |
| G5 | in_process total_gates 字段 102≠103 实数 | 机生字段修正（禁手改散文计数） | P2 |

## 五、自审闸三态

**引擎与名册结构=挖干可施工**（五子包逐文件 wc 实证+91 canonical 复算一致）；**43 门处置与三账收敛=待裁**（Owner 令门位）；**机判口径差异=待裁**（19+3 vs 9 分组镜头需 Owner 认定统一口径）。

## 六、复跑命令

```bash
grep -c "gate_id:" src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml   # 91
wc -l src/zephyr/gov_enforcement/rule_enforcement/gate_engine/*.py | tail -1    # 2891
python -c "import json;raw=json.load(open('.runtime/tmp/mine_dossiers_20260926/census_raw.json',encoding='utf-8'));from collections import Counter;print(len(raw['gates']),Counter(r['state0'] for r in raw['gates']))"
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml',encoding='utf-8'));print(d['total_gates'],len(d['gates']))"
ls src/zephyr/gov_enforcement/rule_enforcement/admission/                       # MAD 5 yaml
```

## 八、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更（gate 治理面 9/28-29 大改，本卷为主战场，四件治本落地）
- `81d85b9a77`（09-29 SW15 墓碑治本）：generate_gate_registry 三源合并改墓碑胜出（extract_commit_gates 每文件首 gate_id 遮蔽墓碑=假 active 借 post-commit 重生的病根修复）；统一册 15 台 active→deprecated+redirect_to（RULING-REFERENCE/RENAME-DEPGRAPH-SYNC/七簇吸收台）；**悬空镜头 16→1**（残 1=裁定 #347 _GlobalCommitLock 机制实名，镜头不可见非真悬空）；22 台全部定性=P4 吸收台退役登记（Owner 09-23 全批 E 既批）；回归测试 test_manual_tombstones_override_disk_shadowed_entries（红 15 违例→绿）。
- `76fd3f1788`（09-29 T14 三件套）：**对账生成器 reconcile_gate_rosters.py（404 行）落库**——卷尾附记"三账对账生成器化"（G2 修法）兑现；own_scope 机生面补全（非空 114→168）；统一册重生成 182→183 台 identity 零丢失。
- `98ce6370c5`（09-29 红五簇撞号修复·实为六簇）：commit_gates 六簇同 priority 撞号（70/79/80/82/92/113——每簇=被吸收薄工厂与 union 吸收面同号，任一面重装载即 GateRegistrationError 整链 fail-closed）迁 152-157 空带；修后 134 passed+in_process 104 台装载零撞号——**装载面 fail-closed 风险解除**。
- `ea0b362d0c`（W-135 密钥门触发面改型）+`1042b6d9e2`（N-3 五台超宽门 files_trigger 按门内真域收窄）：in_process 名册触发面收敛。

### HEAD 现状复测（2026-09-29）
- 三账：gate_registry total_gates=**183**｜_registry.yaml gate_id=**91**（不变）｜in_process **104/104**——卷面"180"与附记"生成器 182≠盘面 181 在飞漂移"均**已过时**（T14 regen 收敛）。

### 缺口清单状态修订
- G1（43 门疑似判据失效）：未见逐门处置证据，维持待裁。
- G2（停用虚报+三账对账生成器化）：**大半翻面**——对账生成器已落（reconcile_gate_rosters.py）+墓碑胜出机制+虚报面收敛（15 台 deprecated）。
- G3（悬空）：**翻面**——悬空镜头 16→1（残 1 非真悬空）。
- G4（半接线 2）：维持；G5（102≠103）：附记已记"可销"，维持销账。
- 新增已闭：六簇撞号装载风险（挖矿时点未立案，09-29 施工闭合）。

### 自审闸三态
- **引擎与名册结构=挖干可施工（维持）**；"43 门处置与三账收敛=待裁"**部分翻面**——三账收敛面已有生成器+墓碑+撞号修复三件落地，43 门逐门处置仍待 Owner；卷尾附记悬空 16 项清单**已过时**（现 1，见上）。

## 七、卷尾附记：三账对账首跑实录（2026-09-27，zc-lane-v-20260927；只读报告，不修册）

M3 03 G1 修法落地：`generate_gate_registry.py` 扩 `three_account_diff()` + `--diff` 只读对账段
（净零：并入既有生成器，替代人工周审计动作，不新增脚本不新增门；generate() 编排段字节兼容，
对账不写任何册）。**口径声明**：本附记三账=统一册 active ↔ in_process enabled ↔ pre-commit hooks，
与卷面 §一/§三 的"模块 114/册 102/总册 180"条目数口径**不同对象，引用禁混用**。

当日实测（会话 zc-lane-v-20260927，`--diff` 全量输出存 `.runtime/tmp/lane_v_diff_report_20260927.txt`）：

| 账 | 口径 | 数 |
|---|---|---|
| 账1 | gate_registry.yaml status=active | 169 |
| 账2 | in_process_gate_registry.yaml enabled=true | 100 |
| 账3 | .pre-commit-config.yaml GATE-* hooks | 55 |
| 三账交集 | 三账一致面 | **0** |

- 判定 **RED**（差集非空）。账3−账1=0（钩子面是账1 真子集）；账3−账2=55（GATE-* 命名族与账2 裸名族无交集，命名轨道分裂即三账交集=0 的根因）。
- **虚报镜头（缺口 G2 对位）4 项**：ALGO-FLOW-LINK / CAPABILITY-OVERLAP / GATE-VOCAB / PERMANENT-SYSTEM-TRIGGER（账1 active 但账2 enabled=false；较卷面 §四 G2 的 3 项多出 GATE-VOCAB）。
- **悬空镜头（缺口 G3 对位）16 项**（账1 有名但账2/账3 均无挂载）：ARCH-REFERENCE, BLUEPRINT-AMODULE-CROSS-CHECK, COMMIT-CRITICAL-SECTION-LOCK, DECISION-MAP, DEPGRAPH-WRITE-PATH, FACTORY-MAP, FRONTEND-MAP, GATE-BATTLE-MAP-ALIGNMENT, INDUSTRY-CHAIN-MAP, MANUAL-ONLY-PERMANENT, NEW-FILE-DEPGRAPH-ENFORCEMENT, NO-GOD-CLASS, NO-LONG-PARAM-LIST, RENAME-DEPGRAPH-SYNC, RULING-REFERENCE, VOCAB-CHAIN——多为 P4 合并的旧台锚点（部分 MANUAL_GATES 已标 deprecated 仍滞留 active 面，如 RULING-REFERENCE/VOCAB-CHAIN，疑 commit_gates 源文件 [MODIFY-GUARD] 头 gate_id 残留旧名被三源合并再登记）。
- **字段自洽**：gate_registry 181/181 OK；in_process 104/104 OK（卷面 §四 G5 记的 102≠103 已被他会话收敛，G5 可销）。注意：生成器现生 182 ≠ 盘面 181（他会话在飞漂移，只记不修）。
- 修册归名册 owner 域；本附记仅为对账机检留痕。复跑：`python scripts/governance/generators/generate_gate_registry.py --diff`（红=exit 1）。
