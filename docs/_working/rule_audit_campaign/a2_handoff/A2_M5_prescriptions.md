---
ttl: task_bound
completes_when: rules 批 48acb99c46 已落地，本件仅存历史证据
---
# A2 腿 · M5 闸2 不可二值判定条文的处方（只处方，未自改；条文面属 rules/，D-14 冻结）

实测 raw 命中 34 处（曾报 32）；其中真规范位 21、词表误报 13。
处方逐条：

- **trae_018_behavior_code_prohibition.yaml:46** `classification_system.actions[0].step`
  「REC推荐做法(建议遵守但不强制)」=术语定义位，非判据；二值化处方：把「不强制」改为机器可读字段 `blocking: false` + 写明「违反仅记 audit，不阻断」，删掉自然语言「建议」。
- **trae_021_behavior_other_prohibition.yaml:454** `abs_51.conditions[0].check`
  「AI建议止损/调仓/加仓」里的「建议」是名词（产出物），不是模糊量词——本条属词表误报；处方：词表只匹配情态位（建议/应/宜 + 动词），名词位排除。
- **trae_021_behavior_other_prohibition.yaml:455** `abs_51.conditions[0].pass`
  处方：把「建议附带置信区间和回测数据」改成二值判据「输出 MUST 含 `confidence=` 与 `backtest_ref=` 两字段，缺一即 FAIL」。
- **trae_021_behavior_other_prohibition.yaml:459** `abs_51.actions[0].step`
  与 :455 同判据双承载→处方：D1 合并为一处真源，另一处改指针（判据=字段存在性检查）。
- **trae_021_behavior_other_prohibition.yaml:516** `ps_std_003_purpose_scope.actions[9].step`
  处方：「推荐做法：建议遵守但不强制」→ 落成 `severity: advisory` 字段 + 一句人判条款（谁判/看什么证据），删模糊语。
- **trae_021_behavior_other_prohibition.yaml:1020** `ps_std_003_consumer_registry.actions[1].step`
  处方：「Tier 2 消费者变更建议同步更新」→「Tier 2 消费者变更 MUST 同 commit 更新 .pre-commit-config/CI 两处，缺失由 GATE-<既有对齐门> 阻断」。
- **trae_024_methodology_diagnosis.yaml:216** `mth_007.conditions[0].pass`
  「经过四问检查(埋雷/容量/对标/建议)」—「建议」是四问之一（名词）→ 词表误报；处方：四问改名「结论/推荐项」以消歧。
- **trae_024_methodology_diagnosis.yaml:226** `mth_007.actions[3].step`
  处方：「最终建议(带推理)」→「MUST 产出 `recommendation` + `evidence_refs>=1` 两字段，脚本查字段非空」。
- **trae_024_methodology_diagnosis.yaml:228** `mth_007.actions[4].step`
  处方：把「返工=四问执行不彻底」改为可查判据「后续 3 个 session 内出现 `rework_of=<本决策id>` 记录 → 记 MTH-007 不合格」。
- **trae_024_methodology_diagnosis.yaml:416** `general_principles.prohibitions[2]`
  「只说不能、不给覆盖建议」→ 处方：禁止位改判据「forbid 输出 MUST 同段含 `override_path=`，否则 FAIL」。
- **trae_025_methodology_decision.yaml:68** `mth_007.actions[0].step`
  与 trae_024:226 同一判据跨文件承载 → 处方：D1 合并（保留 trae_024 为真源，本处改指针）。
- **trae_025_methodology_decision.yaml:109** `mth_009.prohibitions[4]`
  禁止跳过四问（含「最终建议」名词）→ 词表误报；无需改写，处方=词表加名词豁免。
- **trae_031_security_key_access.yaml:590** `sec_004_compliance_baseline.content.baselines[1].requirement`
  「多数场景建议≤180天定期复审」=真模糊位。处方：拆两行——高敏密钥 `rotate_days<=180`（硬，脚本可比对）/ 低敏 `<=365`（warn），删「多数场景」。
- **trae_032_module_lifecycle.yaml:65** `mod_001.actions[4].step`
  「输出否决建议」是产出物名词→误报；处方：改「输出 `veto_candidates[]`」并绑定生成器。
- **trae_034_task_card_standard.yaml:839** `task_001_split_dependency.branches[1].condition`
  「下游建议等上游完成」=真模糊位。处方：改为「下游卡 status MUST=blocked 直到上游 status=done（由 task_repo 状态机判定）」。
- **trae_041_meta_rule_classification.yaml:686** `ps_std_012_violation_response.actions[0].step`
  「向Owner提出系统性改进建议」是流程产出名词→误报；处方：加 `ruling_request_id` 字段使其可查。
- **trae_042_meta_rule_standard.yaml:112** `ps_std_002_prohibitions.prohibitions[4]`
  本条正是「禁止使用模糊词汇（尽量/建议/最好）」的防御条款本体——命中词=被禁词自引用，属词表误报。处方：词表加「同句含 禁止/不得/MUST NOT」豁免。
- **trae_042_meta_rule_standard.yaml:254** `std_009_emergency.actions[0].step`
  「记录问题和建议修复方案」→处方：「Session Log MUST 含 `proposed_fix=` 非空，缺字段 FAIL（现有 session log schema 校验可挂）」。
- **trae_042_meta_rule_standard.yaml:978** `ps_std_002_chapter_details.prohibitions[2]`
  同 :112（自引用误报），处方同上；且 :112/:978 双承载→D1 合并。
- **trae_047_engineering_file_header.yaml:79** `gov_eng_003.conditions[0].pass`
  「顶层包名无碰撞，建议≤200顶层包」→处方：拆成「无碰撞=硬阻断（scaffold 查重 exit1）」+「≤200=warn 并计入 architecture_health_dashboard M 指标」。
- **trae_047_engineering_file_header.yaml:352** `gov_eng_003_namespace_baseline.items[2].details`
  与 :79 同判据三处承载（YAML+代码常量+文档）→处方：D1 收敛为代码常量真源，文档改派生指针。
- **trae_083_design_intent_source_discipline.yaml:74** `design_intent_source.actions[7].step`
  「必要时查 depgraph 补结构状态」=真模糊位。处方：改为触发条件「当 design 文档与 depgraph 字段差集非空时 MUST 查 depgraph（判据=diff 命令 exit code）」。

## 误报 13 处的共同成因（交 Max 定词表改法）
词表按「字符串含词」判，未区分（a）名词位（建议=产出物）、（b）防御条款自引用（禁止使用『建议/尽量』）、（c）术语定义位、（d）change_history/示例/摘要位。
可机械收紧的处方：只在 `conditions[].check|pass|fail`、`actions[].step(type=mandatory|forbidden)`、`invariants[].description` 位匹配，且同句含「禁止/不得/MUST NOT/名词后缀（产出/输出/记录）」者豁免。

## M1 待裁清单（rules/ 面，未施工）
见 rules_m1_repoint.patch（①类 29 条可直接 git apply）+ 本文件下方 ②③ 段