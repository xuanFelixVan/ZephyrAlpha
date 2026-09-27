---
ttl: task_bound
title: "F126 字段字典（REG-FLD-001，8280 行 schema v2.0）复飞案卷"
session: st-c7-mine-20260927
---

# F126 字段字典（A/K 交界，主归 A 段，P1，骨架态=unmined(new id)）

> 立卷依据：`00_skeleton_verified.md` §二 B-7 行——"REG-FLD-001 字段字典（8280 行，schema v2.0）→ F126（P1，A/K 交界，schema 治理面）"。
> 骨架给的行数与 schema 版本号经本卷实核**逐字吻合**（8280 行 / `schema_version: 2.0` 族注释），故本环节身份确认无歧义。

## 一、六向台账（2026-09-27 实证，基准=HEAD 3b4b1f86a1）

| 向 | 实测证据 |
|---|---|
| 实现件 | `docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml`（实存且在 HEAD：`git cat-file -e HEAD:` 通过；`wc -l`=8280；`fields` 映射长度=**262**，§六 M2 实算）。册头 :1 十四字段标注：`module_id=REG-FLD-001 | layer=config | stability=stable | safety=L | ai_autonomy=human_gated`。 |
| 上游输入 | **手工维护**（ROOR `registry_of_registries.yaml:680` 段 `maintenance: manual`）；无生成器写它——`git grep -ln "field_dictionary" HEAD -- 'scripts/governance/generators/*'` 仅 `generate_registry_master_index.py:142` 在总索引枚举里点名（读侧）。schema v2.0 升级史在册头 :3-:10（2026-08-15，为 546 条因子/策略入库前的结构预扩，含"既有条目为默认值/空值占位，禁止视为已填写内容"自警）。 |
| 下游消费 | 四条真读腿（均非自述、逐条 file:line）：①`scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py:95` 声明 `"field_dictionary.yaml": ["fields"]`，:234 `_field_dictionary_keys()`、:245 实读、:253 解析失败即记 violation（**fail-closed 方向**）、:292 用于 inputs 闭包检查；②`scripts/governance/d5_architecture/checkers/check_registry_code_fingerprint.py:92` 同键声明；③`scripts/governance/d5_architecture/generators/align_all.py:128` import `check_field_dictionary_fk`，:537/:553 两处调用（对齐单入口内腿）；④`scripts/governance/d8_doc_sync/agents_cheatsheet_drift_reconciler.py:113` 三元组 `("field_dictionary", "REG-FLD-001", "field_dictionary.yaml")` 绑名分/号/路径。执法侧上卷=`src/zephyr/gov_enforcement/commit_gates/registry_code_anchor_gate.py:82` 把 `"field_dictionary.yaml"` 列入受检册名清单。M1 台账 dir4 只采到 `check_registry_code_anchor.py` 一腿 ⇒ 本卷实测**宽于**机采面（机采漏 3 腿，已进 §四 缺 4）。 |
| 测试 | `git grep -l "field_dictionary" HEAD -- 'tests/*'` = 4 件：`tests/industry_graph/test_field_dictionary_alignment.py`、`tests/governance/test_registry_alignment_layer2.py`、`tests/governance/commit_gates/test_registry_code_anchor_gate.py`、`tests/scripts/governance/d8_doc_sync/test_agents_cheatsheet_drift_reconciler.py`。注意其中一件是 **industry_graph 侧**字典（`industry_graph_field_dictionary.yaml`）的同名命中，须按 §六 T2 分册复核归属。 |
| 自动化触发 | 随提交链触发：`registry_code_anchor_gate` 为 in-process/提交门一侧，读它的是锚点校验器；对账类由 `align_all.py`（根宪法 §8 对齐单入口）与 `agents_cheatsheet_drift_reconciler` 驱动。无独立计划任务（§六 A1 期望零命中）。 |
| 真源与注册表 | 在册=ROOR `:680` `- registry_id: REG-FLD-001` / `name: 字段字典登记表` / `format: yaml` / `maintenance: manual`。真源方向：规则数据=YAML（RULE-SSOT），故字段级 schema 语义以本册为准；库内实际列以 DB 为准 ⇒ 两者**无自动对账尺**（§四 缺 1，与 F123 缺 4 同批）。 |
| 门禁与质量尺 | 尺在（`check_registry_code_anchor.py` 系 + `check_registry_code_fingerprint.py`），且解析失败记 violation 而非静默跳过；但尺的覆盖面=结构键与锚点，**不覆盖 262 条目的内容完成度**。册头 :7 自证："既有条目为默认值/空值占位，禁止视为已填写内容" ⇒ 内容完成度是本环节未量化的主面（§四 缺 2）。 |
| 当前运行状态 | **在产（读侧四腿通、写侧手工、执法侧在册）**。 |

## 二、子模块三级枚举

1. **册结构层**（一级：field_dictionary.yaml）
   - 二级=顶层：`module_id` / `ttl` / `schema_version` / `registry_id` / `name` / `name_zh` / `description` / `owner` / `fields`（§六 M2 实读键序）
   - 二级=`fields` 262 条；三级=条目级 v2.0 新增维度（册头 :6-:8 逐条点名）：`entry_role`（保留值 `reference`）、`applies_to`、`tags`、`algorithm_status`（本库固定 `not_computed`/`not_applicable` 族）、`evidence`（空=未回测）
   - 三级=**本库裁剪声明**（:9）：裁掉 `primary_timeframe`/`applicable_timeframes`/`regime_valid`/`regime_invalid`/`direction` 五维中的 timeframe×2、regime×2、direction——裁剪理由="数据字段定义无周期/环境/方向语义"。⇒ v2.0 的九维里本册只用四共有的+一固定，这是"为别的库设计、被本库裁剪"的借用结构（§四 缺 3）。
2. **对偶册层**
   - `industry_graph_field_dictionary.yaml`（同 catalogs 目录并存）——同为"字段字典"，主键结构经 §六 D2 比对；两者关系（同真源可派生／异对象异域）决定根宪法 §4.2 的必并或保留判定，本卷仅登记并存事实不下合并结论。
3. **校验器层**（scripts/governance/d5_architecture/）
   - 二级=checkers：`check_registry_code_anchor.py`（键声明 :95 + 读取 :245 + inputs 闭包 :292）、`check_registry_code_fingerprint.py`（:92）
   - 三级=三者共同入口 `align_all.py`（:128/:537/:553）；执法上卷 `registry_code_anchor_gate.py:82`；名实绑定 `agents_cheatsheet_drift_reconciler.py:113`
4. **消费语义层**：字段字典与 TDM/depgraph 的关系（字段→表→模块链的字段端点），本环节处于 F111 图书馆交叉轴与 F123 schema 通道之间，是"交界"定号的实际含义。

## 三、接线四态独立复核

- **判定=已接线（读侧）／空转（写侧无尺）**。读侧四腿逐条 file:line 实核且含执法上卷，非注释级引用——特别排除两类假绿：①`generate_registry_master_index.py:142` 只是在注释里列举册名（`:142` 行文本为 `# data_asset/dataflow_graph/.../field_dictionary/strategy）。`），**不计为消费者**；②ROOR 与总索引里的名字出现属"提到即算"形态，本卷按正向声明位（键声明 + 实读函数）重算。
- **fail 方向实测**：解析失败路径（:253）追加 violation ⇒ 该腿 **fail-closed**；此判据对本环节成立，与仓内常见的"解析失败即静默归零"形态不同（该差异是本卷值得留档的正向样本）。
- **装饰性排查**：`check_field_dictionary_fk` 经 `align_all.py:128` **运行时真实 import**，非 `if TYPE_CHECKING:` 内导入（AST 判定脚本见 §六 W1）；且 :537/:553 有实际调用点，故不是"装了不调"的装饰态。
- **零消费者检验**：与同批 F125/F127/F128/F130 四件"生产面零 import"的形态**不同**——本环节有跨包真实读取，故不得套用同批结论。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 8280 行册面对 262 条字段与 DB/CH 实际列的一致性无机检：无一把尺读两侧比对（改表不写字典不可见） | 施工：与 F123 缺 1（schema 迁移登记）同批设计，复用 DatabaseService 读侧（根宪法 §9.1），禁裸 duckdb | P1 |
| 2 | v2.0 新维度的"空占位禁判为已填"只有册头散文自警，无机检：`evidence`/`applies_to`/`tags` 完成度当前不可测 | 施工：补完成度尺（按字段维度的非空计数，输出用派生标量字段而非散文计数，根宪法 §4.3） | P1 |
| 3 | 与 `industry_graph_field_dictionary.yaml` 的双册并存未定内收态（同域重复簇 or 异域不同对象） | 挂起：须两册主键集合做差后再判，属注册表处置面（若走向净删即根宪法 §5 high 域 → Owner） | P1 |
| 4 | M1 机采台账 dir4 对本环节漏采 3 条消费腿（只报 `check_registry_code_anchor.py`）⇒ 以机采面判覆盖会系统性低估 | 施工：M1 采集器补"键声明 + 函数级实读 + 名分路径三元组"三种消费形态，随下一 census 轮 | P2 |
| 5 | `maintenance: manual` 的 8280 行清单册与根宪法 §9.5"静态清单禁手工维护"存在张力 | 挂起：是否强制生成器化属制度判定，交治理侧；本卷只登记张力不自行改判 | P2 |

## 五、自审闸三态

**未干。** 穷尽度自评：六向台账与接线四态已实核到 file:line 级并主动剔除了两类"提到即算"假绿，这部分可信。未干的原因有三，均不可在本夜闭：①262 条字段的**内容面**（每条定义是否与其真实列语义相符）一条未读——按骨架"每环节挖干"口径，schema 治理环节的主体物就是条目内容，跳过内容不能称干；②缺 1 的比对尺不存在，故"字典是否漂移"当前不可测，测量手段本身是先决条件；③缺 3 的双册关系未做键集合差，判不了内收态。本卷价值=把 F126 从"零证据"推进到"身份确认 + 读侧四腿确证 + 三把缺尺点名"，后续接手者可用 §六 直接续测。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
# M1 在 HEAD + 行数（期望 8280）
git cat-file -e HEAD:docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml && echo INHEAD
wc -l docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml
# M2 条目数（期望 262）与顶层键序
python -c "import yaml,io;d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml',encoding='utf-8'));print(list(d)[:9]);print('n_fields',len(d['fields']))"
# C1 四条真读腿
git grep -n "field_dictionary" HEAD -- 'scripts/governance/d5_architecture/*' 'src/zephyr/gov_enforcement/commit_gates/registry_code_anchor_gate.py' 'scripts/governance/d8_doc_sync/*' ':!tests/*'
# C2 排除噪声（期望只见注释行，据此不计消费者）
git grep -n "field_dictionary" HEAD -- 'scripts/governance/generators/generate_registry_master_index.py'
# W1 装载腿是否 TYPE_CHECKING（期望 RUNTIME）
python -c "
import ast,io
f='scripts/governance/d5_architecture/generators/align_all.py'
t=ast.parse(io.open(f,encoding='utf-8').read())
tc={n.lineno for i in ast.walk(t) if isinstance(i,ast.If) and 'TYPE_CHECKING' in ast.dump(i.test) for n in ast.walk(i) if isinstance(n,(ast.Import,ast.ImportFrom))}
for n in ast.walk(t):
    if isinstance(n,ast.ImportFrom) and any('field_dictionary' in (a.name or '') for a in n.names): print(n.lineno,'TC' if n.lineno in tc else 'RUNTIME')"
# T1/T2 测试面（分册归属复核）
git grep -l "field_dictionary" HEAD -- 'tests/*'
git grep -ln "industry_graph_field_dictionary" HEAD -- 'tests/*'
# D1/D2 双册并存与主键形态差
wc -l docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml
python -c "import yaml,io;a=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml',encoding='utf-8'));b=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml',encoding='utf-8'));print('A_top',list(a)[:6]);print('B_top',list(b)[:6])"
# A1 无独立计划任务（期望零命中）
git grep -ln "field_dictionary" HEAD -- '*.ps1' 'config/*' | head
# R1 在册态（maintenance=manual）
grep -n -A5 "REG-FLD-001" docs/registry_of_registries.yaml | head -8
```
