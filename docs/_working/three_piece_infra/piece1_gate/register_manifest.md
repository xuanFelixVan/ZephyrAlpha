---
ttl: task_bound
completes_when: 总筹已按本清单完成 token/翻译/depgraph 合批登记
---

# 包 13.1 待登记清单（register_manifest） — 乙道 st-p1-gate

> 热册唯一写手制：以下条目由总筹一次性合批登记，本道不碰热册。
> 净零口径：新增门禁台数=0（全部落在既有 CREATE-GUARD 的 check 管线内，未新增 GateSpec，未翻任何 enabled 旗）。

## 新建 .py（需 creation_token + 大白话简介 + depgraph 节点）

tests/ 下文件 CREATE-GUARD 已豁免 token、TRANSLATION-COVERAGE 亦按既有约定不要求登记；此处仍列全，由总筹裁量。

| file | capability_id 建议 | merge_evaluation（净零对价） | domain | plain_zh（≥8 字大白话） |
|---|---|---|---|---|
| tests/gov_enforcement/test_create_guard_keyword_overlap_canary.py | piece1_gate_keyword_canary_rulers | 无同类红证件：现有 test_create_guard.py 覆盖 token/字段头/reconciler 面，不覆盖"查功能关键词"与批量化归因判据全等，属新增判据配套尺非重复件（同真源可派生→否；跨域不同对象→不并） | D_GOV_ENFORCEMENT | CREATE-GUARD 查功能关键词的红证测试，四条能红判据各一条，含批量查重判据全等复算 |
| tests/gov_enforcement/create_guard_batch_replay.py | piece1_gate_batch_replay_harness | 非并入 create_guard 生产件（测试取证件，生产代码不含重放框架）；与既有 scripts/ 下一次性取证脚本零重叠（同类无） | D_GOV_ENFORCEMENT | 把类名查重的逐条老做法和批量新做法跑同一批真实样本，逐字节比对结论是否完全一致并留存证据文件 |

## 新建 .json（证据件，非能力真源）

| file | capability_id 建议 | merge_evaluation | domain | plain_zh |
|---|---|---|---|---|
| tests/gov_enforcement/create_guard_batch_replay_evidence.json | — | 由 create_guard_batch_replay.py 产出，非手工维护清单（静态清单禁手工维护铁律）；每次重放覆盖 | D_GOV_ENFORCEMENT | 批量类名查重的等价性证据包，含样本清单、两边结论原文、原始 grep 输出与耗时 |

## 新建 .md（docs/_working 案卷，ttl: task_bound）

| file | capability_id 建议 | merge_evaluation | domain | plain_zh |
|---|---|---|---|---|
| docs/_working/three_piece_infra/piece1_gate/CASE.md | — | 任务绑定案卷（ttl: task_bound），波 13 落 HEAD 后由总筹并回骨架册族 15，不与 00 册重复（设计真源在 00 册 §3 包13.1，本案卷只记施工证据与红证） | D_GOV_ENFORCEMENT | 包 13.1 的案卷 |
| docs/_working/three_piece_infra/piece1_gate/register_manifest.md | — | 本清单，登记后即退役（任务绑定） | D_GOV_ENFORCEMENT | 待登记清单 |

## 既有件改动登记（无需新 token，但行为变更需 gate_registry 侧注记）

- `src/zephyr/gov_enforcement/commit_gates/create_guard.py`（已存在 token）：
  - 新增 `_check_capability_keyword_overlap` / `_scan_file_for_keyword_dupes` / `_build_keyword_probes`
    / `_keyword_identifier_words` / `_build_capability_lookup`（构造缝）。
  - `_check_class_uniqueness` 批量化：N 个 class → 每批一次 `git grep -n -E`（+ `_chunk_class_names`
    / `_attribute_class_grep_lines`），非 ASCII 类名回退逐名查询。
  - `_check_basename_collision` 增 `lookup=` 入参（共享单次构造，实测 ~86s/次，禁双载）。
  - 净零对价：本项检测**取代** L827-848 fail-open basename 碰撞的判重角色（降为冗余后备，未删）
    与 `capability_overlap_gate._check_py_overlap` stage-1 文件名词元启发式（注释标注，未翻旗）。
  - 逃生标记：`# create-guard-not-dup: <一句话理由>`。
- `src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py`：
  `_check_py_overlap` docstring 增"被 CREATE-GUARD 取代"注释（纯注释，零行为变更，enabled 旗不动）。

## ALGO-NOTE-SYNC 待办（转总筹合批）

碰实现码同批需同步 TDM `algo_note_zh` + algo_flow desc：
`docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/create_guard.yaml`
需补 stage「查功能关键词」（探针构造 → CapabilityLookup.find → 命中即红 + 逃生标记）
与 stage「类名唯一性批量化」（一次 git grep -n -E + 归因纯函数）。
