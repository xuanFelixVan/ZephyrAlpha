---
ttl: task_bound
volume: wiring_E_state_vocab
session: st-ailayer-final-20260924
creation_token: fullflow-w3e-state-vocab-ontology-20260926
---

# W3-E 车道施工记录 · 状态词表本体补建（GATE-VOCAB 家族四处悬空收口）

> 依据：94 波2 裁定册 §四（**补建本体使声明为真，不删悬空登记**）＋ §一 P-7（**不选词表对齐方向**，
> 本车道只建登记真源）；缺口清单来自 `01_state_vocabulary_lane.md` §四 堵点 1/2。
> 词表内容一律取自已裁定档（裁定#398 五①＋#399 四 / `docs/_working/vocab_legislation/01_official_state_vocabulary.md`
> ＋ `02_state_vocabulary_mapping_register.md`）——**本车道零新造状态值、零改分段语义**。

## 一、四处悬空的收口状态（逐处实测）

| # | 病灶（开单实测） | 收口后 | 复核证据 |
|---|---|---|---|
| ① | `catalogs/state_vocabulary_registry.yaml` 不存在而 ROOR 指向它 | **已建**（34 套逐套登记＋4 官方本体值锁定＋3 撞名消解＋5 缺口如实披露） | `test_central_registry_file_exists`；`_load_registry()` error="" |
| ② | `src/zephyr/shared/vocab/` 包不存在而 capability 册/翻译册各登记 2 件 | **已建**（`__init__.py`＋`market_state.py`，与已登记路径/ token 逐字一致） | capability 册 :44070/:44075 与翻译册 :55926/:55934 的 `module_path` 现已实存 |
| ③ | 门只按 `zephyr.shared.vocab.market_state.MacroRegime` 类名后缀匹配＝拦错对象 | **加值级锁定**：官方本体类除类名在册外，类内每个全大写取值必须逐值在 `canonical_values` | `_collect_value_locks`＋`_scan_py_files_for_findings`；红测乙 |
| ④ | 声明的 `tests/gov_enforcement/test_state_vocab_registry_gate.py` 不存在 | **已建**：19 例全绿，含两枚必红测 | `pytest tests/gov_enforcement/test_state_vocab_registry_gate.py` |

附带收口（①的成因）：门在"册缺失/损坏"路径原为 fail-open（`return True, ""`）→ 结构性恒绿；
现该路径返回 `(False, detail)` 并写审计痕。**warn→block 的出厂翻转未做**（属 Owner 门位，
`STATE_VOCAB_GATE_MODE` 仍为 "warn"，测试 `test_shipped_mode_is_warn_not_flipped` 钉住）。

## 二、门现在的判据读的是册还是常数（回答回执问句）

- **读册**：`_load_registry(project_root)` 从
  `docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml` 递归取字符串
  （登记面）＋解析 `official_ontology.classes[].canonical_values`（值面）。代码里**不留任何词表常数**；
  `market_state.py` 是官方常量的代码镜像，其对账由测试 `test_ontology_values_match_registry_value_by_value`
  逐值钉（任一侧单边改值＝测试红），门本身不读 `market_state.py`。
- 册读不到＝判据不可用＝报红（不放行）。

## 三、两枚红测结论

| 红测 | 断言 | 结论 |
|---|---|---|
| 甲 册缺失→报红 | 无册/坏 YAML/顶层非映射 → `passed is False`＋`.runtime/gate_audit/state_vocab_registry.jsonl` 留 `__registry_unavailable__` 痕 | **成立**（`TestRedARegistryUnreadableIsRed` 5 例绿；反证：改前该路径 return True） |
| 乙 值不在册→拦 | 官方本体类新增第 7 个取值（夹具 RECHARGING）→ block 模式 `passed is False`；warn 模式放行但 detail＋审计痕必在 | **成立**（`TestRedBValueNotInRegistryIsBlocked` 5 例绿；含 noqa 逃生与"存量类不做值锁定"两条反向测） |

全套 `tests/gov_enforcement + tests/shared/lifecycle` = 76 passed（无连坐回归）。

补充核验（总筹落地前的机器面）：`ruff check src/zephyr/shared/vocab tests/gov_enforcement/test_state_vocab_registry_gate.py
src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py` → All checks passed
（其中 SIM114 是我重构 `_count_upper_assignments` 时新引入又已消除的，HEAD 版本该文件本就 clean）；
`pytest tests/gov_enforcement/test_state_vocab_registry_gate.py` → **exit=0**（19 dots/19 tests，py.ini 抑制了汇总行，以退出码为准）。
本车道**零 git add/零 commit/零入队**（92 册 §一.2），四件新产物停在 untracked、两件修改停在工作区面。

## 四、门禁车道红线：对 HEAD 全量 dry 扫的存量误伤计数

扫描面：`git ls-tree -r HEAD` 中 `src/**.py`＋`scripts/**.py`（候选 4800，实扫 4772，tests/ 按门自身豁免），
外加本车道两份新落盘 .py；判据＝改后门的真实判据（own-scope 不适用，故为全仓上限口径）。

**TOTAL_FINDINGS=67 / 涉及 66 文件**，分解：

| 类别 | 条数 | 定性（禁"为让门绿放宽判据"） | 处方（本车道不代修） |
|---|---|---|---|
| A 类"状态词表类未登记" | 66 | **既有判据的真实命中，非本车道新增**：门过去因病灶①恒绿，从未报过；册一旦在场它们本来就该报。属**登记面欠账**（各线自家状态枚举从未走过 W2 收编），不是代码缺陷、也不是我造的红 | 独立施工袋：符号扫描生成器逐套补登（本册 `gap_disclosures.VOCAB-GAP-5` 已挂此义务）；短期各线自加 `# noqa 标记（STATE-VOCAB-REGISTRY） <原因>`；**warn 模式下 67 条对现网提交零阻断**（只留痕），故不构成连坐 |
| B 类"官方词表类取值未登记" | 1 | **本车道新判据造成的唯一命中**，定性＝**真缺陷**：`src/zephyr/gov_drift/detector_core/regime_detector.py:38` 的 `class MacroRegime(str,Enum)` 取值 EXPANSION/STAGFLATION/TIGHTENING/CRISIS，是"宏观政策周期四态"，**撞官方本体类名而语义异轴**（正是立法件 §3-C1 与映射册 M5/M6/M7"MarketRegime 三胞胎"要治的病；旧门因类名后缀匹配对它完全失明＝病灶③实证） | 该线改名（如 `MacroPolicyRegime`）或类体加 noqa 豁免留痕；gov_drift 非本车道禁触件但改名牵 depgraph/消费者面，属另一施工袋，本车道不代修 |
| 合计 | 67 | 其中"是缺陷"=1，"是登记面欠账"=66，**"是我为了让门绿而放宽"=0**（未放宽任何判据：值锁定只作用于 4 个官方本体类，存量类零值锁定，已由反向测钉住） | — |

A 类按域分布（供总筹派单）：feedback_loop 18 / governance 11 / shared 5 / position 5 / infrastructure 5 /
signal_ashare 4 / security 4 / gov_drift 4 / risk 3 / ex_core 2 / ml_train 1 / plan_engine 1 /
sell_decision 1 / simulation 1 / infra_ops 1 / gov_enforcement 1。
**禁触清单核对**：ex_core 2 条只报不修；`data/**`、`pf_alloc/*`、`intelligence/comparator/**` 零命中；
本车道新件自扫 0 命中（`test_ontology_classes_pass_the_gate_themselves`）。

## 五、GATE-VOCAB 另两条 entry 的回归实测（改后是否仍绿）

- `scripts/governance/d3_metadata/check_vocab_hardcode.py --ci` → **exit 0**（noqa 95 < 基线 193）
- `scripts/governance/d3_metadata/generate_derived_files.py --check` → **exit 0**（派生文件与 vocabulary YAML 全一致）
⇒ 新建包/新册未撞 GATE-VOCAB 的脚本腿。

## 六、待登项（车道禁触热册，请总筹在窗口内单点落地）

```yaml
# 1) docs/registry_of_registries.yaml —— REG-STATE-VOCAB-001 就地改 3 字段（其余不动）
registry_id: REG-STATE-VOCAB-001
physical_path: docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml   # 现已实存，status: active 名副其实
entry_count: 34            # 派生标量：本册 vocabularies 数组实测长度（禁散文写死，宪法 §4.3）
counting_rule: vocabularies 数组条目数（官方本体 4 类另列 official_ontology.classes，不计入存量套数）
description: >-
  封闭状态/情绪词表逐套登记（实测 m.* 14 / e.* 10 / f.* 5 / s.* 4）——官方词表本体
  =zephyr.shared.vocab.market_state（SH-VOCAB-001，现已实存）；撞名消解已裁 C1/C2/C11 三案，
  C5/C6/C9 无立法实物（见册内 gap_disclosures.VOCAB-GAP-2，勿再按旧描述引用）

# 2) capability_canonical_file_registry.yaml —— 三条 file 行已实存（:44070/:44075 与
#    catalogs 行），车道未动；仅需总筹复核 token 与本次落盘字节一致：
#    state-vocab-market-state-20260921 / state-vocab-init-20260921 / state-vocab-registry-20260921

# 3) module_translation_registry.yaml —— 两条 module_path 行已实存（:55926/:55934），
#    plain_zh 文案与本车道实现一致，无需新增；若测试件也须登记大白话，请总筹按 tests/ 惯例判定

# 4) depgraph（RULE-DEPGRAPH，总筹登记设计节点/产物）
need_register:
  - artifact: src/zephyr/shared/vocab/market_state.py
    produces: 官方状态词表常量本体
  - artifact: src/zephyr/shared/vocab/__init__.py
    produces: 官方词表包入口
  - artifact: docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml
    produced_by: 首版=人工普查实物锚点版（映射册 §H-3 口径）；后续=符号扫描生成器（待建，见 VOCAB-GAP-5）
  - consumer: src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py
    consumes: state_vocabulary_registry.yaml（改判据：册缺失=报红；官方本体值级锁定）

# 5) 派生册须重生成（车道禁触，只报不修）
regenerate:
  - file: docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml
    why: 门内 fail-open 站点行号/条数变了（原 6 条含"注册表不存在 fail-open"字样行，现为报红）
    cmd: python scripts/governance/d7_code/generate_fail_open_register.py
  - file: gate_registry.yaml / in_process_gate_registry.yaml
    why: 若把 STATE-VOCAB-REGISTRY 描述里"注册表缺失 fail-open 跳过"同步为"报红"，须同批改文案

# 6) 待接线（本车道刻意不做，避免越权/越界）
pending_wiring:
  - ALGO_FLOW yaml（docs/03_modules/_domain_shared/algo_flow/…market_state.yaml）＋ market_state.py 头部
    external: 锚——锚指向文件不存在会被 ALGO-FLOW-LINK 硬拦，故本件暂不带锚（生成器产出后回挂）
  - 各线消费方改用 `from zephyr.shared.vocab import …`（立法件 §1.1 第 2 条）——迁移随各线自然迭代，
    本车道零行为变更（沿用 W2 口径）
  - F75 词表对齐方向（P-7 不选方向）＝另一施工袋，与本件无耦合
```

## 七、跨域不并的边界句（防后来者顺手合并）

- `src/zephyr/shared/vocab/market_state.py` 与 `src/zephyr/shared/vocab/__init__.py` 头注：
  本方=大盘状态/情绪官方本体；`shared/lifecycle/registry_state_vocab` 方=策略生命周期拼写对齐——跨域不同对象→不并。
- `src/zephyr/shared/lifecycle/registry_state_vocab.py` 头注 [INVARIANTS] 末已回写同一条边界（含 94 §四 出处）。
- 中央登记册 `boundary_statement` 字段同步声明。

## 八、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version   # 3.12.8
# 1 四处悬空全部转实存（预期四行都列得出文件）
ls -l docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml \
      src/zephyr/shared/vocab/__init__.py src/zephyr/shared/vocab/market_state.py \
      tests/gov_enforcement/test_state_vocab_registry_gate.py
# 2 两枚红测＋声明为真三面（预期 19 passed）
PYTHONPATH=src python -m pytest tests/gov_enforcement/test_state_vocab_registry_gate.py -p no:cacheprovider -c py.ini -q --timeout=300
# 3 无连坐回归（预期 76 passed）
PYTHONPATH=src python -m pytest tests/gov_enforcement tests/shared/lifecycle -p no:cacheprovider -c py.ini -q --timeout=300
# 4 GATE-VOCAB 另两腿仍绿（预期各 exit 0）
PYTHONPATH=src python scripts/governance/d3_metadata/check_vocab_hardcode.py --ci | tail -3
PYTHONPATH=src python scripts/governance/d3_metadata/generate_derived_files.py --check | tail -3
# 5 存量误伤 dry 扫（预期 TOTAL_FINDINGS=67，其中"取值未登记"=1）
PYTHONPATH=src python .runtime/tmp/w3e_dry_scan.py | tee .runtime/tmp/w3e_dry_scan_out.txt | grep -E "TOTAL_FINDINGS|取值未登记"
# 6 词表面规模（实测 47 条目=46 个 *.yaml + 1 份非 yaml 索引；01 车道册"47 个 yaml"口径差 1）
ls docs/01_policies_and_standards/_registry/vocabularies | wc -l
```

## 九、三态结论

**完工**（本车道范围内）：四处悬空全部收口，判据读册不读常数，两枚红测成立，存量误伤 67 条已逐类定性、
零放宽判据、零阻断现网（warn 未翻）。
**待登（非缺陷）**：§六 六组待登项由总筹单点落地（ROOR 计数与描述、token 复核、depgraph、派生册重生成、ALGO_FLOW 锚）。
**待裁（不阻塞）**：①A 类 66 条登记面欠账的补登方式（生成器 vs 各线 noqa）——属施工安排；
②B 类 gov_drift `MacroRegime` 撞名件的改名裁量（该线归属）；③F75/P-7 词表对齐方向仍按 94 §一 P-7 不选。
本车道未自赋任何裁定号、未写 Owner 署名。
