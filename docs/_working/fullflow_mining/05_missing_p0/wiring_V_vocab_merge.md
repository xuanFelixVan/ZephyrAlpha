---
ttl: task_bound
volume: wiring_V_vocab_merge
session: st-ailayer-final-20260924
creation_token: fullflow-w6v-vocab-merge-and-enforcement-20260926
---

# W6-V 车道施工记录 · 词表册真源冲突合并 ＋ 四处"报绿而不执法"治本

> 依据：任务书（W6-V）＋红队案卷 `rb2_guard_attacks.md` §二.15-16／§三.1-2／§五／§十 A5、B1-B3；
> 本体设计说明=`wiring_E_state_vocab.md`（W3-E 建本体，本车道只修"合并/执法"，**零改六段词表语义、零改已裁取值**）。
> 纪律：零提交、零入队、零 claim、零 release；禁触热册只读；产物全在 worktree。

## 〇、开工实测（非记忆）

```
worktree = D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924（分支 ai/st-ailayer-final-20260924/fullflow-closure）
python   = 3.12.8（PATH 前置 LOCALAPPDATA/Programs/Python/Python312）
假绿防线 = PYTHONPATH=$PWD/src 后 python -c "import zephyr;print(zephyr.__file__)"
           → …\.worktrees\st-ailayer-final-20260924\src\zephyr\__init__.py（每次跑测前复验）
```

## 一、任务一：真源冲突合并（并集，不覆盖）

### 1.1 两版事实（合并前）

| 版本 | 位置 | 条数 | 顶层结构 | sha256（前 12） |
|---|---|---|---|---|
| 主区块（他道 09-22/23 产出，主区盘上未入 git；ROOR `REG-STATE-VOCAB-001` 登记的就是它） | 备份读=`.runtime/tmp/st-ailayer-final-20260924/state_vocab_main_0923.bak.yaml`（**未动主区盘**） | 29 | `module_id/ttl/title/doc_type/owner/tier/version/created/last_updated/vocabularies`，条目键=`vocabulary_id/name_zh/states/source/canonical_mapping/conflicts`，**无 official_ontology** | `0eb528b2926f` |
| 本役区块（W3-E 产出） | worktree `docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml` | 34 | `schema_version/official_ontology/collision_resolutions/gap_disclosures/vocabularies`，条目键=`id/name/class/axis/location/official_mapping/disposition` | `02ae8a1616fb` |

**直接落本役版＝抹掉他道 29 条**（归属篡改＋数据丢失），故做并集。**逐条比 id 的同 id 字面冲突=0**：
两套 id 命名空间天然不相交（主区=语义短横式 `regime-hmm-7`…，本役=前缀式 `M1/E1/F1/S1/X1`…），
故**无"自选一侧覆盖"待裁案**；真正的冲突是"同一实物两套登记"（§1.3 同源对）与顶层元数据（§1.4）。

### 1.2 合并算法（两版，取文本级）

- v1（`w6v_merge.py`，已弃用）：yaml 载入→并 list→dump。**弃用理由（自证抓到的）**：重排会丢主区块的
  `# [A_CONFIG] module_id=CFG-state-vocab-registry …` 机读标记行与 5 段分轴注释（97 行文本消失），
  内容虽深相等但注释面丢失＝仍在"抹他人条目"的边上。
- v2（终版 `w6v_merge3.py`）：**纯文本拼接**——底=本役版全文；主区块 `vocabularies` 段整块 verbatim
  插到本役条目之前（"主区条目保留＋本役新增追加"语义）＋其自身说明注释逐行保留；文末追加
  `merge_provenance` 血缘段；主区块独有顶层元字段提升到顶层；`description` 例外（见 §1.4）。

### 1.3 合并结果（机读自证，读 `w6v_merge_report.json`）

| 量 | 值 |
|---|---|
| `vocabularies` 长度 | **63 = 29 + 34** |
| 同 id 字面冲突（待裁覆盖案） | **0** |
| 同源对（同一实物两套登记，按 `source`/`location` 文件路径机械配对） | **15**：`regime-hmm-7↔M1`、`anchored-4↔S1`、`regime-12↔M3`、`market-grid-3x3↔M8`、`crisis-gate-3↔X4`、`feedback-regime-4↔M7`、`market-mode-4↔E5`、`tdm-six↔E4`、`sent-cycle-5-A↔E1`、`sent-phase-5-B↔E2`、`youzi-5↔E3`、`water-temp-response-5↔E7`、`sent-state-4↔E8`、`water-tier-5↔E6`、`daily-plan-3↔F1` |
| 只在主区（本役未登记该实物） | **14**：`volume-regime-3, lifecycle-season-4, warm-plane-7, pyramiding-5, env-switch-six, limitup-4, rotation-5, canonical-phase-5, next-day-8, similar-day-3, nextday-3, cycle-eval-5, stock-behavior-family, intraday-five` |
| 只在本役（主区块无此实物） | **19**：`M2, M4, M5, M6, E9, E10, E11, F2, F3, F4, F5, F6, S2, S3, S4, X1, X2, X3, X5` |

三道自证（全过）：① 主区块 29 条 + 本役 34 条**逐条深相等**（`deep_equal_lost_* = []`）；
② 主区块原文逐行在场核对——缺失仅 7 行，且**全部属于顶层 description 的折行**（其值已按字存入
`merge_provenance.main_block.description_verbatim`，`…_verbatim=true`）；③ 本役版原文**零行缺失**。
`official_ontology` 四类的 `values_locked/canonical_values` 合并后原样在场。

### 1.4 顶层元数据与 ROOR

- 主区块独有 9 个顶层字段（`module_id/ttl/title/doc_type/owner/tier/version/created/last_updated`）提升到顶层，
  共享字段（`registry_id/name/status`）两版标量**实测零冲突**（`top_level_scalar_conflicts={}`）。
- 顶层 `description` 重写为"规模指向字段"口径（宪法 §4.3 禁散文写死计数）；主区块原 description（写"28 套"）
  按字存进 provenance，未删一字。
- **ROOR `entry_count` 应对成 63**（现值 29）；建议 `counting_rule` 写成"vocabularies 数组条目数
  （两套 id 命名空间并集）；official_ontology.classes 另列不计入"。ROOR 是热册，**本车道一字未动**，
  由总筹单点改；册内同口径已写于 `merge_provenance.count_reconciliation`（机读，供对账）。
- 合并后两登记块共存＝**同路径双真源已收敛为单文件双块**（红队 §十 B3 的"撞车/未跟踪覆盖"风险解除；
  落地仍须"门禁代码＋册同袋原子投"=B2，本车道零 git add）。
- 待裁三项已列 `pending_rulings.md`（W6-V-1 同对象双条是否并册／W6-V-2 主区块 `intraday-five` 的
  `canonical_mapping.target=…IntradayFiveVocab` 类名实测不存在／W6-V-3 ROOR 计数与散文）。

## 二、任务二：把"静默归零"改成"报红"

改前（红队 §二.16/§五末行实测）：`_load_registry` 只判"文件在不在/YAML 坏没坏"，读到无
`official_ontology` 的册 → `error=""` 且锁定表空 → **值级锁定整块失效而门报绿**。

改后：新增 `_official_ontology_locks()` 结构自检，与"册缺失"同级报红＋`__registry_unavailable__` 审计痕。
报红条件：缺段 / 段非映射 / `classes` 缺失|非列表|空数组 / 逐类缺 `name`、缺 `canonical_values`、`values_locked` 未置真。
`_load_registry` 返回值改为 `_RegistryView`（`names/paths/value_locks/error`）四元 NamedTuple，杜绝"静默三元组"。

同题实测台（`w6v_before_after.py`，修前判据按改动前源码逐行复刻、修后=现装真件，**同一份输入两份源码树**）：

| 攻击 | 修前 | 修后 |
|---|---|---|
| 用他道 09-23 真版册（无 official_ontology）＋官方类夹带 `RECHARGING` | 绕过（passed=True，且官方类名走 suffix 匹配直接判"在册"） | **拦住**：`册内缺 official_ontology 段…禁回落为『无官方本体』` |
| 空册 `classes: []`（红队 §二.17 原为"拦住但 warn 下等于全仓都违规"） | 部分（依未登记违规） | **报红在判定之前**（结构不合预期=判据不可用） |

配对测试：`TestRedCRegistrySchemaDriftIsRed` 9 例（含缺段/非映射/空 classes/缺 canonical_values/values_locked 未置真/
必留审计痕/源文件有违规也到不了判定面/**反向自证：真册（合并后）不被结构自检误伤**）。

## 三、任务三：noqa 逃生口整体被关（红队一行关掉整文件官方值锁）

1. **豁免面收窄（=收紧，不是放松）**：判定次序改为"先官方本体锁（名面∪值面），该路径不看 noqa；
   再启发式名面判定，noqa 只在这里生效"。原 `_class_has_noqa` 的 `continue` 短路在值锁定之前（旧源码 :286 早于 :288）
   是漏洞成因，现已消除。
2. **原测试改判**：`test_noqa_escape_hatch_still_works_for_value_lock`（把逃生当特性钉绿，红队 §八.3 点名）
   **删除并替换**为 `TestNoqaDoesNotReachOfficialValueLock` 5 例：官方值行挂 noqa／类体首行挂 noqa 都必须仍红；
   warn 态仍须出声；并保留两枚**反向测**钉住"noqa 仍能豁免启发式未登记"与"删掉 noqa 后同一份源码仍红"，
   防止把逃生口整个删掉（那是另一种越权：豁免面收窄≠取消豁免）。
3. **门内文案与真实形态同源**：旧文案教 `# noqa 标记（STATE-VOCAB-REGISTRY） <原因>`，而正则真源
   `_make_noqa_pattern` 认 `#\s*noqa:\s*STATE-VOCAB-REGISTRY\s{2,}(\S.*)$` → 照文案写=没写（实测 passed=False）。
   现文案改教 `NOQA_FORM_EXAMPLE = "# noqa: STATE-VOCAB-REGISTRY  <原因>"`（本常量与 detail 同源），
   并实测自证：`TestGateMessageMatchesRealNoqaForm` 4 例——① 该形态被自家正则认；② 中文旧形态不被认；
   ③ detail 里含新形态且**不含**中文形态（防再说谎）；④ 端到端：照抄该行→启发式违规真的消失（`_scan` 前后对比）。

## 四、任务四：类名/路径白名单伪装

改前双重绕过：① `value_locks.get(类名)` 按名查 ⇒ 改名即脱锁；② 册里 `official_ontology.physical_location`
是纯路径串 ⇒ `_is_registered` 的模块路径分支命中即**整文件放行**（官方本体文件自成本册注释自称已避免的"文件级白名单"）。

改后：
- **值面判据**：`_official_lock_for()` 双通道——名面命中，或"携带**同一**官方类 ≥`_MIN_VALUE_FACE_OVERLAP(=3)`
  个在册取值"即按该官方类锁定；多命中取"重叠最大、夹带最少"者。detail 里写明认定依据（类名/值面）以便回评。
- **改名无新值也要被看见**：值集完整等于官方某类且自身类名不在官方本体 → 独立违规
  "野生类 X 完整携带官方类 Y 的在册值集…改名/整段复制不构成本体登记"。
- **取消文件级白名单**：模块路径登记面 `_RegistryView.paths` 收集时**剔除 `official_ontology` 与
  `merge_provenance` 两个子树**（类名登记面仍读全册，故官方类本身照旧在册）。
- 阈值取 3 的理由与误伤控制：三值同集是"设计好的官方词表片段"，非巧合；只蹭 2 个官方值的野类仍走启发式名面，
  已由 `test_partial_overlap_below_threshold_does_not_trigger_value_lock` 钉住（防本车道为凑红测放宽判据）。

同题实测台结果（`w6v_before_after.json`，全部真落盘）：

| 攻击（红队行） | 修前 | 修后 |
|---|---|---|
| `market_state.py` 内改名 `MacroRegimeOfficial`＋同样错值 `R13` | **绕过**（passed=True，detail 空） | **拦住**：认定依据=值面（携带官方类 MacroRegime 的 7 个在册取值），noqa 不豁免 |
| 官方类体一行 `# noqa: STATE-VOCAB-REGISTRY  例行自证`＋`R13` | **绕过** | **拦住**（认定依据=类名，noqa 不豁免） |
| 无关键词类 `SixGrid` 携带 3 个官方在册值＋新造 `RECHARGING` | **绕过**（连词表类都不认定） | **拦住**（值面不依赖类名关键词） |
| 改名类完整携带官方六段值集（无新值） | 拦住（走的是启发式名面，非值面） | **拦住**（值面独立违规，口径明确） |
| 反向：官方类逐值与册一致 | 绿 | **绿**（零误伤，`_scan` 自扫 `{}`） |
| 反向：启发式未登记类＋一行 noqa | 绿 | **绿**（豁免面仍在） |

> 披露：红队脚本 `rb2_atk_confirm_vocab.py` 的 `v_rename_class_dodge`／`v_lowercase_values` 两例
> **只构造了源码字符串、未写入假仓**，故门根本没见过那个文件（`os.path.isfile` 即 skip）——其
> "绕过/小写绕过"结论里，`detail=''` 那部分属测量装置缺陷而非判据结论。本车道把这两例改成等价**落盘**版本重跑
> （`SixGrid` 例即其一），结论以本表为准；小写取值面本车道**未修**（属任务书四点之外的判据扩展，见 §七待挖）。

## 五、存量影响与回归（总筹落地判据）

| 量 | 读数 |
|---|---|
| HEAD 全量 dry 扫（`git ls-tree HEAD` 的 src/+scripts/ .py，实扫 4772，tests/ 豁免） | **TOTAL_FINDINGS=67 / 66 文件**＝名面未登记 66 ＋官方值面 1，**与 W3-E 基线逐条相同 ⇒ 本轮四项收紧对现网零新增误伤** |
| 唯一值面命中 | `src/zephyr/gov_drift/detector_core/regime_detector.py::MacroRegime`（CRISIS/EXPANSION/STAGFLATION/TIGHTENING 撞官方类名，W3-E 定性=真缺陷，改名归该线施工袋） |
| 出厂姿态 | 仍 `STATE_VOCAB_GATE_MODE="warn"`（warn→block 翻转属 Owner 门位，本车道未翻，测试钉住） |
| 配对测试 | `tests/gov_enforcement/test_state_vocab_registry_gate.py` **50 例全绿**（原 19 例，exit=0 为准） |
| 连坐回归 | `tests/gov_enforcement tests/shared/lifecycle` exit=0；`ruff check` All checks passed |
| GATE-VOCAB 另两腿 | `check_vocab_hardcode.py --ci` exit 0（noqa 95<基线 193）；`generate_derived_files.py --check` exit 0 |

## 六、文件清单（本车道产物；零 git add）

改（4）：
- `docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml`（合并：29 verbatim 块 + 34 本役块 + `merge_provenance`；盘上现 641 行）
- `src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py`（+233/−54：结构自检、_RegistryView、值面双通道、路径登记面剔除、noqa 次序、文案同源、头注 INVARIANTS/ERROR_CONTRACT 同步）
- `tests/gov_enforcement/test_state_vocab_registry_gate.py`（19→50 例；删 1 枚"逃生当特性"绿测并改判，新增 4 个测试族）
- `docs/_working/fullflow_mining/05_missing_p0/pending_rulings.md`（追加 W6-V-1/2/3 三案）

新建（2，均 tmp 不入库）：`.runtime/tmp/st-ailayer-final-20260924/w6v_merge3.py`（合并器 v1/v2 同名留档）、
`.runtime/tmp/st-ailayer-final-20260924/w6v_verify/{w6v_before_after.py,w6v_dry_scan.py,w6v_before_after.json,w6v_merge_report.json}`；
主区侧只读备份件 `state_vocab_main_0923.bak.yaml` 与 `state_vocab_w3e_beforemerge.bak.yaml`（合并前本役版逐字节留档，回滚可用）。

`src/zephyr/shared/vocab/market_state.py` **零改动**（任务书"如需"未触发：官方常量与册逐值已一致）。

## 七、待登 / 待接线（车道禁触热册，请总筹单点落地）

1. **ROOR**：`REG-STATE-VOCAB-001` 的 `entry_count: 29 → 63`；`counting_rule` 与 `description` 同步
   （现描述仍写"28 套…撞名 C1/C2/C5/C6/C9/C11"，C5/C6/C9 无立法实物=本役 `VOCAB-GAP-2`）。
2. **红队 §十 B1**：`in_process_gate_registry.yaml` 的 STATE-VOCAB-REGISTRY `register_line` 注释仍写
   "注册表缺失 fail-open"——与本门现契约（缺失/缺段皆报红）相反，须同袋改这行机读名册自述。
3. **红队 §十 B2**：门禁代码＋`catalogs/state_vocabulary_registry.yaml`＋`src/zephyr/shared/vocab/**` **同袋原子投**
   （现 worktree 面：YAML=`AM`、gate=`MM`、测试=`AM`，即总筹此前已 add 过旧字节，我改后需重新 add）。
4. `fail_open_register.yaml` 须重生成（门内 fail-open 站点行号变了）：`python scripts/governance/d7_code/generate_fail_open_register.py`。
5. `.runtime/tmp/w3e_dry_scan.py` 读的是旧三元组 API，已不兼容 `_RegistryView`（tmp 件，本车道未改他道脚本；
   本车道等价件=`w6v_verify/w6v_dry_scan.py`）。
6. **计数口径登记面**（实测读数）：`python scripts/governance/d3_metadata/check_registry_consistency.py`
   现报 `UNSPECIFIED: REG-STATE-VOCAB-001 未登记计数口径——新表必须补 ENTRY_SPECS/ENTRY_MANUAL`
   （`check_registry_consistency.py:297/:380` 两表内本册无条目）。总筹改 ROOR `entry_count` 时**同批补该条目**，
   否则"派生标量 vs 实数组长度"永远无人对账（本次 29↔63 的漂移正是这台尺缺位的产物）。
   另注：本车道改动对 `registry_mass_deletion_gate` 是**净增 34 条、删除集为空**（键集合差自证见 §1.3 ①②③）。
7. 待挖（非本车道范围，**未修**）：小写/计算式取值、"删一个成员退到 3 门槛下"两条绕过属启发式识别面扩展；
   gov_drift 撞名件改名；六段历史标签持久化（`VOCAB-GAP-3`）。

## 八、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; export PYTHONPATH="$PWD/src"
python -c "import zephyr;print(zephyr.__file__)"                       # 必须落在本 worktree（假绿防线）
# 1 合并三道自证（vocabularies_len=63 / deep_equal_lost_*=[] / 本役零行缺失）
python .runtime/tmp/st-ailayer-final-20260924/w6v_merge3.py | head -20
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml',encoding='utf-8'));p=d['merge_provenance']['count_reconciliation'];print(len(d['vocabularies']),p['roor_entry_count_should_be'],p['same_object_pairs_cross_block'] if 'same_object_pairs_cross_block' in p else len(p))"
# 2 修前/修后同题实测台（7 例：修后 5 拦 2 绿）
python .runtime/tmp/st-ailayer-final-20260924/w6v_verify/w6v_before_after.py 2>/dev/null | grep -E "^\["
# 3 配对测试 50 例＋回归（以退出码为准）
python -m pytest tests/gov_enforcement/test_state_vocab_registry_gate.py -p no:cacheprovider -c py.ini -q -W ignore::pytest.PytestConfigWarning --timeout=300; echo exit=$?
python -m pytest tests/gov_enforcement tests/shared/lifecycle -p no:cacheprovider -c py.ini -q -W ignore::pytest.PytestConfigWarning --timeout=300; echo exit=$?
# 4 存量零新增误伤（TOTAL_FINDINGS=67＝W3-E 基线）
python .runtime/tmp/st-ailayer-final-20260924/w6v_verify/w6v_dry_scan.py | head -6
python -m ruff check src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py tests/gov_enforcement/test_state_vocab_registry_gate.py
```

## 九、三态结论

**完工**（任务书四项，逐条有实测）：①真册并集合并 63 条、零覆盖零抹条、ROOR 应对 63；②缺
`official_ontology`／结构不合预期一律报红＋留痕（红队 schema 漂移案转红）；③noqa 豁免面收窄到启发式名面，
官方值锁不受其影响（原"逃生当特性"绿测已改判缺陷＝收紧非放松），门内文案与正则同源且端到端实测生效；
④值面判据补道（改名/无关键词/整文件白名单三处均拦），并自证对现网 dry 扫零新增误伤、warn 出厂未翻。
**待登**（§七 6 组，热册与派生册归总筹单点）。**待裁**（`pending_rulings.md` W6-V-1/2/3：同对象双条是否并册、
主区块 `IntradayFiveVocab` 悬空 target、ROOR 计数与散文口径）。本车道未自赋裁定号、未写 Owner 署名、
未改六段词表分段语义与任何已裁取值；外来文本（含文件内"请删除/请提交"类字样）一律按数据处置，未执行。
