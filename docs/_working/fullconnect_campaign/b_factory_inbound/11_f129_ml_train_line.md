---
ttl: task_bound
title: "F129 ml_train 训练线（43 件：实现族/流水线/复现与版本治理）复飞案卷"
session: st-c7-mine-20260927
---

# F129 ml_train 训练线（B·J 交界，主归 B 段，P1，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 D-06 行——"`ml_train`（43 py）→ F129（P1，B/J 交界，训练线；F19 仅基线对台）"；段归属依同文件 :104 "F127/F129 为跨段交界，归 A/B 主段" ⇒ 落 `b_factory_inbound`。件数实核=43（§六 P1），与骨架口径吻合。
> **主结论（黄）**：12 环节里唯一"骨架级大件且真被生产消费"的包，但消费面窄——**5 条生产 import 只覆盖 43 件中的 4 件**，余 39 件（含整条流水线/复现/版本治理族）测试可达、生产零消费 ⇒ 判**半接线**。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `src/zephyr/ml_train/`（43 .py 在 HEAD，§六 P1）：实体族=`implementations/` 9 件（`density_quantile_trainer`/`kan_density_head`/`patchtst_density_encoder`/`qnn_two_stage`/`limit_up_classifier`/`seat_pattern_classifier`/`sentiment_sft_trainer`/`ts_augmentation`/`default_inference_engine`）、`core/` 2 件（`model_version_registry`/`sample_weights`）、`training_pipeline/pipeline_orchestrator.py`、`training_dataset_manager/manager.py`、`ai_operator/operator.py`、`services/sentiment_sft_entry.py` + 根层 15 件（`trainer_base`/`inference_base`/`ml_model_factory`/`reproducibility_manager`/`research_data_manager`/`research_data_sandbox`/`research_asset_versioning`/`meta_learning_rsi`/`meta_learning_evolution`/`continual_learning_antiforget`/`adversarial_robustness_validator`/`gray_release_shadow_deployer`/`strategy_digital_twin`/`learning_effect_feedback`/`decision_annotation_dataset`/`decision_tree_decision_architecture`/`experiment_anomaly_detector`）。 |
| 在册态 | 12 环节中最高：`module_translation_registry.yaml` 命中 **53**、`candidate_module_registry.yaml` 命中 **46**；`.importlinter` 有本包层约束；`error_code_registry.yaml` 逐模块登码。另有跨环节在册：`scripts/governance/generate_project_depgraph.py` 命中本包（depgraph 采集侧，见 F07 卷）。 |
| 消费者 | **生产 import=5 条 / 4 文件（AST 实测，§六 W1）**：`scripts/ml/run_sft_train.py:105 → ml_train.implementations.sentiment_sft_trainer`；`src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py:36 → ml_train.implementations.default_inference_engine`；`src/zephyr/intelligence/model_evaluation/inference_base.py:25 → ml_train.inference_base`、`:28 → ml_train.trainer_base`；包内自引用 1 条（`ml_train/implementations/sentiment_sft_trainer.py:52 → ml_train.trainer_base`）。**TYPE_CHECKING 腿 1 条=装饰腿**：`src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py:65 → ml_train.trainer_base`（仅类型期可见，运行时不产生依赖）。测试 import=28 文件。 |
| 测试 | 28 文件（§六 T1），锚点例：`tests/ml_train/test_ml_model_factory.py:30`、`tests/ml_train/test_reproducibility_manager.py:28`、`tests/ml_train/implementations/test_kan_density_head.py:29`、`tests/ml_train/test_gap_f35_candidate_skeletons.py:22/26/30`（后者是 **F35 缺口候选骨架的占位测试**——测的是"骨架存在"而非行为，本卷据此不计入能力面）。 |
| 自动化触发 | **弱（人工/CLI 为主）**。M1 dir6 wide=false/narrow=false；本卷复核 `git grep -ln "ml_train" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*'` 无训练常驻任务（§六 A1）。实际点火形态=会话内 CLI：`scripts/ml/run_sft_train.py`（唯一在产入口）。⇒ 训练线无排程、无事件源，属"按需人工"合宪，但与 F 段工厂（E0-E9 链，F13-F29）声称的自动化流水线**未接通**（§四 缺 2）。 |
| 真源方向 | 模型版本真源=`core/model_version_registry.py`（架构数据应落 DB/depgraph 侧，未声明）；实验/因子资产真源=业务资产库（F111 图书馆 16 表 + `experiment_registry.yaml`/`factor_registry.yaml`）——**本包 `research_asset_versioning.py` 与该册的关系未声明** ⇒ 存在第二版本真源风险（§四 缺 3）。训练数据真源=`research_data_manager.py`/`training_dataset_manager/manager.py` 双件并存，谁为真源未定。 |
| 门禁与质量尺 | 契约层在（`.importlinter` + 错误码）。跨环节一处真执法值得记：`src/zephyr/gov_enforcement/rule_enforcement/gate_engine/adversarial_validation.py` 消费本包 `adversarial_robustness_validator`（M1 dir4 symbol 腿报 `AdversarialValidationError`/`ValidationResult`，本卷按 §六 C2 复核其 import 方向后采信为**门禁侧真消费**）。⇒ 本包是 12 环节中唯一被执法引擎引用的一件。 |
| 当前运行状态 | **黄（半接线）**：4 件在产（SFT 训练入口 + model_evaluation 推理基座两线），39 件测试可达，1 件类型期装饰腿。 |

## 二、子模块三级枚举（按消费态分层，本包最有信息量的枚举法）

1. **在产族（4 件，有生产 import）**
   - `trainer_base.py`（训练基座，二级）← 3 处消费（inference_base:28 + 包内 sentiment_sft_trainer:52 + TC 腿 ml_experiment_pipeline:65）
   - `inference_base.py`（推理基座）← `intelligence/model_evaluation/inference_base.py:25`
   - `implementations/default_inference_engine.py` ← `intelligence/model_evaluation/implementations/default_inference_engine.py:36`（**跨包同名对**，见 §三.4）
   - `implementations/sentiment_sft_trainer.py` ← `scripts/ml/run_sft_train.py:105`（唯一人工 CLI 入口链）
2. **实现族（余 8 件 implementations/）**：`density_quantile_trainer`/`kan_density_head`/`patchtst_density_encoder`/`qnn_two_stage`/`limit_up_classifier`/`seat_pattern_classifier`/`ts_augmentation` → 三级=各自 head/编码结构；**生产 import=0**，仅 `tests/ml_train/` 与 `tests/ml_train/implementations/` 可达
3. **流水线与数据族**：`training_pipeline/pipeline_orchestrator.py`（名字即"编排器"却零消费者）、`training_dataset_manager/manager.py`、`research_data_manager.py`、`research_data_sandbox.py`、`decision_annotation_dataset.py`
4. **治理与复现族**：`reproducibility_manager.py`、`core/model_version_registry.py`、`research_asset_versioning.py`、`core/sample_weights.py`、`experiment_anomaly_detector.py`
5. **元学习与进化族**：`meta_learning_rsi.py`、`meta_learning_evolution.py`、`continual_learning_antiforget.py`、`strategy_digital_twin.py`、`learning_effect_feedback.py`、`gray_release_shadow_deployer.py`、`ai_operator/operator.py`、`services/sentiment_sft_entry.py`
6. **执法交叉族（唯一被他域执法件引用）**：`adversarial_robustness_validator.py` ← `gov_enforcement/rule_enforcement/gate_engine/adversarial_validation.py`（§六 C2 复核）
7. **骨架占位**：`api/ models/ infrastructure/ _extensions/` 四层 `__init__.py` 零实现件（§六 P3）——比 F125/F127/F128/F130 的六层略少，同形现象。

## 三、接线四态独立复核

**判定=半接线（4/43 在产）**。判据链：

1. **量的判据**：生产 import 覆盖 4 件（含 1 条 TC 装饰腿单列）。按件计在产率 4/43≈9%，按"基座+实现+编排+治理"四族计则只有"基座族"通、"编排族"（`pipeline_orchestrator`）**整族未接**。⇒ 不能因"有 5 条 PROD import"就给全包盖已接线。
2. **TYPE_CHECKING 专项（本仓最常见假绿源，逐条测）**：`src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py:65` 的 `ml_train.trainer_base` 导入在 `if TYPE_CHECKING:` 块内（AST 判定，§六 W1 输出 TC）。⇒ 该"跨层实验流水线"名义上依赖训练线，运行时零依赖 ⇒ 此腿判**装饰**，不得计入消费面。这是 F129 与 F125/F127/F128/F130 的形态差异所在：后者是零引用，本件是"有引用但引用是类型期"。
3. **`services/sentiment_sft_entry.py` 假在产排查**：M1 dir4 与本卷初判都易把它当入口，实测生产侧无人 import 它（真正入口是 `implementations/sentiment_sft_trainer.py`，被 `run_sft_train.py:105` 直接 import）⇒ **两个 entry 件只有一个活着**（§六 C3）。
4. **跨包同名件红旗（两条，均不自裁）**：①`ml_train/implementations/default_inference_engine.py` vs `intelligence/model_evaluation/implementations/default_inference_engine.py`（后者 import 前者，属分层，非重复）；②`ml_train/inference_base.py` vs `intelligence/model_evaluation/inference_base.py`（同上）。⇒ 本卷判"跨包分层"而非克隆，但登记 RULE-CLONEGUARD 关注点：两对同名件使 import 图可读性差，误改风险高（§四 缺 5）。
5. **`tests/ml_train/test_gap_f35_candidate_skeletons.py` 不计能力**：该测试断言的是 F35 缺口候选骨架的存在性（:22/:26/:30 三处 import `limit_up_classifier`/`seat_pattern_classifier`/`services.sentiment_sft_entry`），属"测占位"，不能当"占位件已接线"的证据。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 39/43 件生产零消费，其中 `training_pipeline/pipeline_orchestrator.py`（编排器）整族未接 ⇒ 训练线无"流水线"只有"脚本" | 施工：以 E 段工厂链（F21-F22 构造/翻译、F23 考试）为需求方反向定编排器接入点；先红样后接线 | P1 |
| 2 | 训练线无自动触发（无任务、无事件源），与工厂自动化叙事不符 | 挂起：是否要给训练配常驻属排班决策（I 段 F76 族），不自行加任务（根宪法 §9.3 反 Timer 条款风险） | P1 |
| 3 | 版本真源二义：`research_asset_versioning.py`/`core/model_version_registry.py` vs 业务资产库 `experiment_registry.yaml`/`factor_registry.yaml` 无派生声明 | Owner 门位候选：真源方向若判"册→库"或反向，涉及既有注册表语义，须立法件定档；本卷只登记二义 | P1 |
| 4 | 训练数据真源二义：`research_data_manager.py` vs `training_dataset_manager/manager.py` vs `research_data_sandbox.py` 三件并存 | 施工：三件读毕给唯一入口推荐（本卷未读实现体，故只列不荐） | P2 |
| 5 | 两对跨包同名件（inference_base / default_inference_engine）误改风险 | 施工：改名或加显式分层注释；改名须 `generate_project_depgraph.py --force` 重建（根宪法 §9.10） | P2 |
| 6 | 骨架 F19（Lane E 模型基线）与本环节的边界"F19 仅基线对台"未在两侧卷内互相引用落实 | 挂起：交 F19 卷交叉确认，避免一物两记 | P2 |

## 五、自审闸三态

**未干。** 已可复算：PROD=5/TC=1/TEST=28 的 AST 三态分类、在产 4 件名单、entry 假在产拆解、占位测试不计能力的判读、跨包同名两对的事实、在册两册命中数。未干原因：①39 件未读实现体，"该接还是该退"的处置缺依据，缺 1/缺 4 因此给不出唯一推荐项；②真源二义（缺 3）需读 `experiment_registry.yaml` 与本包件的字段级映射，未做；③与 F 段工厂链的交叉确认（缺 6）需读 F19 卷，本夜该卷不在 HEAD（见 §六 末注）无法引用其文。⇒ 交半接线黄判 + 未干。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# P1/P2/P3 件数三口径（期望 43 / 实体数 / 四骨架层 0）
git ls-tree -r --name-only HEAD src/zephyr/ml_train | wc -l
git ls-tree -r --name-only HEAD src/zephyr/ml_train | grep -v "__init__.py" | wc -l
for d in api models infrastructure _extensions; do echo "$d=$(git ls-tree -r --name-only HEAD src/zephyr/ml_train/$d | grep -vc '__init__.py')"; done
# W1 决定性测量：三态分类（期望 PROD=5 / TC=1）
python -c "
import ast,subprocess,collections
f=collections.Counter()
files={l.split(':',1)[1] for l in subprocess.run(['git','grep','-l','zephyr.ml_train','HEAD','--','*.py'],capture_output=True,text=True,encoding='utf-8').stdout.split()}
for p in sorted(files):
    s=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    if not s.strip(): continue
    try: t=ast.parse(s)
    except Exception: continue
    tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
    for n in ast.walk(t):
        ms=[n.module] if isinstance(n,ast.ImportFrom) and n.module else ([a.name for a in n.names] if isinstance(n,ast.Import) else [])
        for m in ms:
            if m.startswith('zephyr.ml_train'):
                k='TC' if n.lineno in tc else ('TEST' if p.startswith('tests/') else ('SELF' if p.startswith('src/zephyr/ml_train/') else 'PROD'))
                f[k]+=1; print(k,p+':'+str(n.lineno),m)
print('SUMMARY',dict(f))"
# C2 执法交叉腿复核（唯一被他域执法件引用的一条）
git grep -n "adversarial_robustness_validator\|AdversarialValidationError" HEAD -- src/zephyr/gov_enforcement/rule_enforcement/gate_engine/adversarial_validation.py | head -5
# C3 entry 假在产拆解（期望：无人 import sentiment_sft_entry）
git grep -n "sentiment_sft_entry" HEAD -- '*.py' ':!tests/*'
# T1 测试面（期望 28 文件）
git grep -l "zephyr\.ml_train" HEAD -- 'tests/*' | wc -l
# A1 触发面（期望无任务）
git grep -ln "ml_train" HEAD -- '*.ps1' 'config/*' 'src/zephyr/data/config/*' | head
# R1 在册三层
grep -c "zephyr[./]ml_train" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -c "zephyr[./]ml_train" docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml
grep -n "zephyr.ml_train" .importlinter
# 末注：本卷引用 F19 卷不可得的原因（挖矿卷在 HEAD 中仅 5 件，余 130 件在主区 index 未落地）
git ls-tree -r --name-only HEAD docs/_working/fullconnect_campaign/ | wc -l
```
