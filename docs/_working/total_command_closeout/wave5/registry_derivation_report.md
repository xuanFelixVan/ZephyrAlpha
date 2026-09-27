---
ttl: task_bound
completes_when: "本报告的派生口径判定被后继班按同一命令复算且结论一致"
---

# W-52 / W-53（族 5，波 5.1）——ROOR/域册派生计数机生化 案卷

> 施工车道：`D:\ZephyrAlpha\.aidrafts\st-final-build-20260926`（分支 `session/st-final-build-20260926`，HEAD `ffc3ce5f49`）
> 本案卷只出「待落地补丁文本」。`docs/01_policies_and_standards/**` 与 `docs/registry_of_registries.yaml`（热册）
> **本包一处未写**；派生回填全部在 `.runtime/tmp/` 的临时副本上完成。

## 0. 头部四字段

- **turn_budget**：子代理 150 轮硬上限；本包实际用量 ≈ 60 次工具调用（第 8 次内落第一版骨架，符合落盘纪律）。
- **verified**（全部本机实测，命令原文见 §1/§3/§4；读数时刻 2026-09-27 03:xx，车道工作树）：
  1. ROOR `REG-STATE-VOCAB-001` 声明 `entry_count: 29`，目标册 `vocabularies` 实际 **63**（差 **34**）；
     旧口径下 CR-007 对此条只报 `UNSPECIFIED`（"未登记计数口径"），漂移被静默吞掉。
  2. 全 ROOR 范围：按各自口径实测后 **19 行** `entry_count` 与在册数字不符（§1.1 表）。
  3. ROOR `summary` 段 7 个派生标量中 **4 个漂移**：`total_registries` 76→实测 77、
     `by_tier.tier_2` 34→35、`by_status.active` 66→67、`by_medium.ok` 74→75。
  4. ROOR 散文（各条 `description`）里写死的 `N 条/N 套/N 个` 共 **53 处**与同条 `entry_count` 不符
     （含 `REG-STATE-VOCAB-001` 的 "28 套（10/12/5/1）"，真值 63）。
  5. `functional_domain_registry.yaml` 94 条 entries 中 **10 条** ssot_path↔covers 错配：
     4 条 `PATH_MISSING` + 1 条 `PATH_UNDECLARED` + 5 条 `COVERS_UNFOUND`（§1.2 逐条）。
  6. 三个改造件全部扩既有生成器/校验器，**未新建生产脚本**；新落盘件 = 1 个 canary 测试 + 本波 2 个案卷文件。
  7. 幂等：派生回填在临时副本上复跑 **字节全等**（§3）；`generate_registry_master_index.py` 连跑两次
     载荷全等（`idempotent payload: True`）。
  8. 红证：`tests/governance/test_registry_derivation_canary.py` **19 条全绿**；同批既有
     `test_registry_entry_counts.py` 8 条不退化（合计 27 passed，§4）。
  9. 复杂度：新增 13 个函数用门禁自家 `_cyclomatic_complexity` 复算，最高 12（阈值 >15 硬拦，未调阈值）。
- **assumed**（未由本包定论，落地前须总包/域主复核）：
  1. §1.2 中 4 条 `PATH_MISSING` 的"应指向哪个真源"属域归属裁定（如 `src/zephyr/governance/persistence/`
     与 `D_INFRA_RUNTIME` 是否同域），本包只给实测存在性与候选，不代裁。
  2. `COVERS_UNFOUND` 的 5 条里 `D_DATA/data_source_integrator`（CLS/EastMoney）判为**命名形态差**
     （源码实为 `cls_provider.py`/`eastmoney_news_provider.py`），非能力缺失——本包未放宽尺，如实呈报。
  3. `check_registry_consistency.py` 是否被某条 gate 直接执法：本包在 `.pre-commit-config.yaml`/
     `gate_registry.yaml`/`src/zephyr/gov_enforcement` 三处 grep 该脚本名 **零命中**，据此判定"新红点不会今晚连坐他人"；
     若总包另有注册面（如 reconciler 侧），请按注册面复核一次。
  4. 主区工作树 `state_vocabulary_registry.yaml` 呈 `29 条` 的过期副本且在主区 index 里为 `D`(staged delete)+`??`(untracked)
     双身态——本包按 dev/lane HEAD blob（63 条）取真值，双身态归因未追（不在本包作用域）。
- **input_set_disjoint_with**：
  - 只写车道内 `scripts/governance/**`（3 个既有文件）、`tests/governance/test_registry_derivation_canary.py`、
    `docs/_working/total_command_closeout/wave5/{registry_derivation_report.md,registration_needs.yaml}`。
  - 未碰 `docs/01_policies_and_standards/**`、`docs/registry_of_registries.yaml`、`wave1b/**`、`wave2/**`、`wave3/**`、
    `wave9/**`、`wave10/**`、`wave11/**`、`scripts/gov_enforcement/**`、`scripts/commit_queue.py`、`scripts/git_commit.py`；
    未写 `data/`；无任何 git add/commit/enqueue；无删除动作；PG/CH 未触（本包零 DB 访问）。
- **evidence_ref.cmd**：§1.1 / §1.2 / §1.3（现读三处）、§3（幂等两条命令）、§4（红证 pytest 命令 + 生产侧红绿对照）、§5（每条补丁的复算命令）。

## 1. 现读：三处账实不符的真值

### 1.1 ROOR `entry_count` vs 目标册实际条目

命令原文（车道根执行）：

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src \
  python scripts/governance/d3_metadata/check_registry_consistency.py --warn-only
```

改造前实测输出（节选，21 项 FAIL）：

```
STALE: REG-SCRIPT-001 ROOR=991 实测=1037（scripts 数组条目数（generate_manifest.py 全树再生））
STALE: REG-SCRIPT-002 ROOR=434 实测=450（scripts 数组条目数（governance 子集，__manifest__ 块提取））
...
UNSPECIFIED: REG-STATE-VOCAB-001 未登记计数口径——新表必须补 ENTRY_SPECS/ENTRY_MANUAL
...
  CR-007: entry_count 实测对账（ROOR）... FAIL (21 项)
```

要点：`REG-STATE-VOCAB-001` 明明在 ROOR 本条已写 `counting_rule: vocabularies 数组条目数`，
但因为代码侧手工表 `ENTRY_SPECS` 没抄这一行，CR-007 判 `UNSPECIFIED` 而不是 `STALE`——
**"口径手工表"本身就是第二真源**，29 vs 63 的 34 条漂移正是被这个判定吞掉的。

改造后（口径三级解析：ENTRY_SPECS 覆写 → ROOR 本条 counting_rule 派生 → 无口径）逐行复算，
共 **19 行** `entry_count` 与在册数字不符（含 STATE-VOCAB），全部由 `count_by_spec` 现算：

| registry_id | 行号（ROOR） | 在册 | 实测派生 |
|---|---|---|---|
| REG-SCRIPT-001 | L45 | 991 | 1037 |
| REG-SCRIPT-002 | L55 | 434 | 516 |
| REG-RESCHED-001 | L138 | 74 | 81 |
| REG-CATALOG-001 | L154 | 55 | 58 |
| **REG-STATE-VOCAB-001** | **L257** | **29** | **63** |
| REG-DOC-001 | L276 | 256 | 294 |
| REG-GATE-CAT-001 | L286 | 169 | 181 |
| REG-INFRA-001 | L296 | 16 | 17 |
| REG-FUNC-DOMAIN-001 | L366 | 83 | 94 |
| REG-ARCH-ISSUE-001 | L428 | 761 | 805 |
| REG-CAPCAN-001 | L441 | 378 | 388 |
| REG-GEN-001 | L455 | 5520 | 11641 |
| REG-ARCH-001 | L524 | 75 | 74 |
| REG-TECHNICAL-INDICATOR-001 | L642 | 102 | 143 |
| REG-PAT-001 | L653 | 297 | 287 |
| REG-DATAFLOW-001 | L674 | 342 | 294 |
| REG-DAL-001 | L717 | 27 | 32 |
| REG-BTB-001 | L738 | 137 | 142 |
| REG-ATH-001 | L827 | 38 | 49 |

> 读数注：`REG-SCRIPT-002` 在本包会话内两次读数不同（450→516），因 02:46 有 reconciler 重生了
> `scripts/governance/script_manifest.yaml`（实测该文件 `scripts` 长度=516，mtime 2026-09-27 02:46）。
> 这不是尺的抖动，是**派生值随真源实时变化**——恰好证明在册的 434 才是假的。
> `REG-METAQ-001` 仍 `UNSPECIFIED`：其 `counting_rule` 写的是"meta_question 主表行数（快照头部 row_count 字段）"，
> 非"某数组条目数"形态，解析器**不猜**（保守返回 None），须显式登记口径。

### 1.2 `functional_domain_registry.yaml` 的 ssot_path ↔ covers 错配清单

命令原文：

```bash
PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src \
python -c "import sys; sys.path.insert(0,'scripts/governance/d3_metadata'); \
import check_registry_consistency as crc; [print(r) for r in crc.verify_domain_ssot(check_covers=True)]"
```

册内 entries 实际 94 条（ROOR 在册 83 → 已在 §1.1 表内）。错配 **10 条**：

| # | domain/subdomain | 判定 | 在册 ssot_path | 实测 |
|---|---|---|---|---|
| 1 | D_AUTONOMY_PERM/budget_enforcement | PATH_MISSING | `src/zephyr/autonomy_perm/` | 全仓无此包（`grep -rl autonomy_perm src/zephyr` 只命中域名引用，无实体目录） |
| 2 | D_AUTONOMY_PERM/escalation | PATH_MISSING | `src/zephyr/autonomy_perm/` | 同上 |
| 3 | D_INFRA_RUNTIME/persistence | PATH_MISSING | `src/zephyr/data/persistence/` | 不存在；同名唯一目录 = `src/zephyr/governance/persistence/` |
| 4 | D_SHARED/shared_services | PATH_MISSING | `src/zephyr/shared/shared_services/` | 不存在；`src/zephyr/shared/` 存在但无该子包 |
| 5 | D_TEST/test_domain_placeholder | PATH_UNDECLARED | `(depgraph domains.ssot_path 为空)` | 括注非路径（自述占位） |
| 6 | D_GOV_DRIFT/drift_detection | COVERS_UNFOUND | `src/zephyr/gov_drift/` | covers 声称 `CanaryController`/`CascadeDetector`，两词全仓 0 命中 |
| 7 | D_AUTONOMY_CORE/agent_communication | COVERS_UNFOUND | `src/zephyr/autonomy_core/` | 声称 `A2AMessage`/`ConflictDetector`/`Arbitrator`，实体在 `src/zephyr/infrastructure/a2a_protocol/` |
| 8 | D_SECURITY_LLM/llm_defense | COVERS_UNFOUND | （ssot_path 存在） | 声称 `HITL`，命中面在 `src/zephyr/integration`、`src/zephyr/intelligence`，非 llm_defense |
| 9 | D_INTEGRATION_GATEWAY/mcp_servers | COVERS_UNFOUND | `src/zephyr/integration/mcp/` | 声称 `KnowledgeBaseServer`，全仓 0 命中 |
| 10 | D_DATA/data_source_integrator | COVERS_UNFOUND | `src/zephyr/data/` | 声称 `CLS`/`EastMoney`；源码以 `implementations/cls_provider.py`、`eastmoney_news_provider.py` 存在（命名形态差，非能力缺失） |

独立复核（防尺自证）：`grep -rlw <符号> src/zephyr scripts --include=*.py` 对 8 个符号逐个跑，
`CanaryController/CascadeDetector/A2AMessage/ConflictDetector/KnowledgeBaseServer/HITL/EastMoney` 在**各自声称的 ssot_path 内**均 0 命中。

### 1.3 散文里被写死的派生标量

命令原文：

```bash
grep -rn "total_gates" docs --include=*.md --include=*.yaml | head -20
grep -c "counting_rule:" docs/registry_of_registries.yaml   # 38
grep -c "entry_count:"   docs/registry_of_registries.yaml   # 76
grep -c "registry_id:"   docs/registry_of_registries.yaml   # 77
```

实测结论（三档）：

1. **机生字段侧健康**：`gate_registry.yaml total_gates: 181` ↔ `gates` 实测 181 ✅；
   `in_process_gate_registry.yaml total_gates: 103` ↔ 实测 103 ✅（这两册有生成器，不漂）。
   规则册里 8 处 `total_gates` 命中全是"以 gate_registry.yaml 的 total_gates 为准"的**引用式**写法（合规）。
2. **ROOR summary 段**：派生标量 7 个中 4 个漂（§0 verified 3），`--refresh-summary` 有再生器、**无对账器**，
   本包补 CR-007c 那把尺。
3. **ROOR description 散文**：**53 处**硬编码 `N 条/N 套/N 个` 与同条 `entry_count` 不符。复算命令：

```bash
python - <<'PY'
import yaml, re
r = yaml.safe_load(open('docs/registry_of_registries.yaml', encoding='utf-8'))
pat = re.compile(r'(\d+)\s*(条|套|个)')
hits = [(x['registry_id'], m[0]+m[1], x.get('entry_count'))
        for t in r.get('tiers', []) for x in (t.get('registries') or [])
        for m in pat.findall(str(x.get('description') or ''))
        if x.get('entry_count') is not None and int(m[0]) != x['entry_count']]
print(len(hits)); [print(h) for h in hits[:10]]
PY
```

样本（前 10）：`REG-GATE-001 '43个' vs 91`、`REG-SCRIPT-001 '755个' vs 991`、`REG-EMBED-001 '4个' vs 5`、
`REG-CATALOG-001 '16个' vs 55`、`REG-STD-001 '13条' vs 14`、`REG-CROSS-001 '16个' vs 15`、
`REG-CROSS-002 '19条' vs 132`、`REG-STATE-VOCAB-001 '28套' vs 29`、`REG-DIR-001 '88个' vs 87`、`REG-DOC-001 '153个' vs 256`。

本包只把 `REG-STATE-VOCAB-001` 一条的散文改法写成补丁（§5.3），其余 52 处属总包/域主的批量文本手术，
逐条代改会撞别人在途的册面写作，故列为**待裁清单**而非本包代修。

## 2. 改生成器：派生改机生（三处全是扩既有件，零新建生产脚本）

| 件（车道内） | 角色 | 本包扩了什么 |
|---|---|---|
| `scripts/governance/_shared/registry_entry_count.py` | 计数单一真源（`generate_registry_master_index` + `validate_registry_master_index` + `refresh_master_entries` 三家共消费） | 新增 `parse_counting_rule()`（口径文本→(kind,key)，解析不出返回 None 不猜）、`declared_count_spec()`、`count_by_spec()`（+`_walk_key`/`_sum_lists`）；`count_primary_registry_entries(data, stem, counting_rule="")` 声明口径优先、手工键白名单降为兜底；`primary_count_entry_key()` 同步随声明走 |
| `scripts/governance/d3_metadata/check_registry_consistency.py` | registry 校验器（CR-001~007b） | ①CR-007 口径三级解析 `_spec_for_roor_entry()`：ENTRY_SPECS 覆写 → **ROOR 本条 counting_rule 派生** → 无口径；②`_undeterminable_verdict()` 区分"物理文件缺失"与"口径键面不符"，防谎报 MISSING；③回填改读 row['rule']，不再只依赖手工表；④新增 **CR-007c** `verify_roor_summary()`（summary 7 派生标量 ↔ tiers 实测）；⑤新增 **CR-008** `verify_domain_ssot()`（域册 ssot_path 存在性；`--check-domain-covers` 另核 covers 符号能否在真源内以词边界命中）；⑥`_actual_entry_count()` 取数下沉到 `count_by_spec`（消灭与本模块重复的第二套数数逻辑） |
| `scripts/governance/generators/generate_registry_master_index.py` | ROOR 侧总索引生成器 | 新增 `_roor_counting_rules()`（physical_path→counting_rule，口径真源就是 ROOR 本条），`scan_catalogs/extract_registry_info` 带上口径 → 主索引 `entry_count` 不再对 10 张册恒报 0 |

为什么不新建：三处病灶（ROOR 计数、summary 标量、主索引计数）的真源与执法面都已在 `check_registry_consistency.py` +
`registry_entry_count.py` 这一对里（`ENTRY_SPECS`/`count_primary_registry_entries` 就是既有口径入口）；
新建并行尺 = 宪法 §9.5 反向违规 + 第二真源。净零：本包生产侧 `.py` 净新增 **0 个文件**，只增函数；
手工表 `ENTRY_SPECS` 由"唯一入口"降级为"覆写层"（其条目一条未删）。

生成器不 import 主区包：新增代码零 `zephyr.*` 导入（车道内跑必带 `PYTHONPATH=…/src` 自证，见各节命令）。

## 3. 幂等证明（复跑零 diff）

命令原文（不写生产册：ROOR 先复制到 `.runtime/tmp/`，对副本手术）：

```bash
PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src python - <<'PY'
import shutil, sys
from pathlib import Path
sys.path.insert(0, 'scripts/governance/d3_metadata')
import check_registry_consistency as crc
src = Path('docs/registry_of_registries.yaml'); cp = Path('.runtime/tmp/w5_roor_after.yaml')
shutil.copyfile(src, cp)
crc.apply_roor_entry_count_updates(crc.verify_entry_counts(cp), cp)
crc.apply_roor_summary_update(cp)
b = cp.read_bytes()                                    # 第二次跑
crc.apply_roor_entry_count_updates(crc.verify_entry_counts(cp), cp)
crc.apply_roor_summary_update(cp)
print('IDEMPOTENT:', b == cp.read_bytes())
PY
```

实测输出：

```
STALE rows: 19
summary: REFRESHED total_registries=76
after re-verify: Counter({'MATCH': 64, 'MANUAL': 11, 'NO_COUNT': 1, 'UNSPECIFIED': 1})
summary after refresh: ['MATCH', 'MATCH', 'MATCH', 'MATCH', 'MATCH', 'MATCH', 'MATCH']
IDEMPOTENT(second run byte-identical): True
```

主索引生成器侧（写临时输出，不碰 docs/01）：

```bash
python scripts/governance/generators/generate_registry_master_index.py --output .runtime/tmp/w5_mi_a.yaml
python scripts/governance/generators/generate_registry_master_index.py --output .runtime/tmp/w5_mi_b.yaml
```

实测：`已生成 61 张登记表索引` ×2、`idempotent payload: True`；与在册主索引比，
`entry_count` 变化 **18 行**，其中 **10 行原为 0**（手工键白名单数不出来的册，如
`REG-BTB-001 0→142`、`PS-REG-021 0→11641`、`REG-PAT-001 0→287`）；`CFG-IN-PROCESS-GATE-REGISTRY-001 113→103`
与 gate 册自述 `total_gates: 103` 对齐（旧值 113 是启发式误数）。

## 4. 反事实红证（R-5：新尺自带红证）

命令原文：

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src \
  python -m pytest tests/governance/test_registry_derivation_canary.py tests/governance/test_registry_entry_counts.py -q
```

实测输出：

```
collected 27 items
tests\governance\test_registry_derivation_canary.py ...................  [ 70%]
tests\governance\test_registry_entry_counts.py ........                  [100%]
============================= 27 passed in 3.45s ==============================
```

逐尺红绿对照（19 条 canary，每条都是"删一行/改一个数⇒必红；一致数据⇒必绿"）：

| 尺 | 绿证 | 红证（人为破坏） | 测试函数 |
|---|---|---|---|
| CR-007 口径派生 | 空 ENTRY_SPECS 也能从 ROOR `counting_rule` 数出 5→MATCH | 真源册删一行词表⇒`STALE (5→4)`；在册数字手改成 29⇒`STALE` | `test_cr007_derives_from_counting_rule_green` / `test_cr007_red_when_one_entry_deleted` / `test_cr007_red_when_declared_number_tampered` |
| CR-007 回填 | — | 复跑 `apply` 返回 `[]` 且字节不变（幂等即"不二次改"） | `test_cr007_backfill_idempotent` |
| CR-007c summary | 7 字段全 MATCH | tiers 删一条目⇒`total_registries/by_tier/by_status/by_medium` 四标量同红（3→2） | `test_summary_green_when_consistent` / `test_summary_red_when_one_entry_deleted` / `test_summary_computation_is_stable` |
| CR-008 ssot_path | 真源存在⇒零行 | 路径指向不存在位置⇒`PATH_MISSING`；括注占位⇒`PATH_UNDECLARED` | `test_domain_ssot_green` / `test_domain_ssot_red_when_path_missing` / `test_domain_ssot_red_on_placeholder_path` |
| CR-008 covers | 括号内类名在真源内⇒零行 | 类改名⇒`COVERS_UNFOUND`；散文标签 `(L1 Trae/L2 Local/L3 API)`⇒**不许哭狼**（红证逼出的两个真 bug 之一） | `test_domain_ssot_red_when_covered_symbol_moved` / `test_domain_ssot_does_not_cry_wolf_on_prose_tokens` |
| 口径解析器 | 4 种文本形态各归其 kind | 不可解析文本（"…主表行数（快照头部 row_count 字段）"、空串）⇒`None`（不猜） | `test_parse_counting_rule`（6 参数化） |
| 主索引计数 | 册内自述/ROOR 传入口径各数出 5 | 删一行⇒4；口径键面不符⇒0（交对账侧报 UNSPECIFIED） | `test_master_index_count_follows_declared_key` |

两条红证**改掉了尺本身**（不是改判据放水）：
1. 子串匹配让 `CanaryController` 命中源码里的 `CanaryControllerV2` ⇒ 改词边界 `\b…\b`；
2. 括号内散文标签被当类名 ⇒ 只认「以 `/`、`,` 分隔后仍是纯标识」的片段。
生产侧读数因此变化：CR-008 行数 11→**10**（消掉 `runtime_core`/`rollback` 两条假红，新增 `llm_defense/HITL` 一条真红）。

## 5. 待落地补丁文本（交总包；本包未写这两处）

### 5.1 `docs/registry_of_registries.yaml`——19 行 entry_count

为什么：数字是派生量，真源是各目标册的条目数组长度（ROOR 本条 `counting_rule` 已写明口径）；
在册值全部是手写快照，最严重一条差 34（STATE-VOCAB）、最大一条差 6121（REG-GEN-001）。

机械落地（推荐路径，比手抄更不易错）：

```bash
python scripts/governance/d3_metadata/check_registry_consistency.py --update-entry-counts --refresh-summary
```

逐条 diff（行号为 3ea37c1467 ROOR blob 内位置，落地以 registry_id 定位为准）：

```diff
# REG-STATE-VOCAB-001  @L257（本包主治）
-        entry_count: 29
+        entry_count: 63
# REG-SCRIPT-001  @L45
-        entry_count: 991
+        entry_count: 1037
# REG-SCRIPT-002  @L55
-        entry_count: 434
+        entry_count: 516
# REG-RESCHED-001  @L138
-        entry_count: 74
+        entry_count: 81
# REG-CATALOG-001  @L154
-        entry_count: 55
+        entry_count: 58
# REG-DOC-001  @L276
-        entry_count: 256
+        entry_count: 294
# REG-GATE-CAT-001  @L286
-        entry_count: 169
+        entry_count: 181
# REG-INFRA-001  @L296
-        entry_count: 16
+        entry_count: 17
# REG-FUNC-DOMAIN-001  @L366
-        entry_count: 83
+        entry_count: 94
# REG-ARCH-ISSUE-001  @L428（保留行尾注释）
-        entry_count: 761  # 2026-08-11 更新：含 35 项 proposed 议题（……）
+        entry_count: 805  # 2026-08-11 更新：含 35 项 proposed 议题（……）
# REG-CAPCAN-001  @L441
-        entry_count: 378
+        entry_count: 388
# REG-GEN-001  @L455
-        entry_count: 5520
+        entry_count: 11641
# REG-ARCH-001  @L524
-        entry_count: 75
+        entry_count: 74
# REG-TECHNICAL-INDICATOR-001  @L642
-        entry_count: 102
+        entry_count: 143
# REG-PAT-001  @L653
-        entry_count: 297
+        entry_count: 287
# REG-DATAFLOW-001  @L674
-        entry_count: 342
+        entry_count: 294
# REG-DAL-001  @L717
-        entry_count: 27
+        entry_count: 32
# REG-BTB-001  @L738
-        entry_count: 137
+        entry_count: 142
# REG-ATH-001  @L827
-        entry_count: 38
+        entry_count: 49
```

复算命令：`python scripts/governance/d3_metadata/check_registry_consistency.py --warn-only`（CR-007 应报 `FAIL (1 项)`，
即 `REG-METAQ-001` 无机械口径，见 §5.5）。

### 5.2 同册 summary 段——4 个派生标量

为什么：`total_registries`/`by_tier`/`by_status`/`by_medium` 全由 `tiers` 实测派生（`compute_roor_summary`），
在册值比最新 tiers 少 1 张表（新增表登记时未复跑 `--refresh-summary`）。

```diff
 summary:
   total_tiers: 3
-  total_registries: 76
+  total_registries: 77
   by_tier:
     tier_0: 12
     tier_1: 30
-    tier_2: 34
+    tier_2: 35
   by_status:
-    active: 66
+    active: 67
     archived: 2
     deprecated: 1
     draft: 7
   by_medium:
     database: 2
-    ok: 74
+    ok: 75
   broken: 0
```

复算命令：落地后 `--warn-only` 的 `CR-007c` 行应为 `PASS`；或
`python -c "import sys;sys.path.insert(0,'scripts/governance/d3_metadata');import check_registry_consistency as c;print(c.verify_roor_summary())"`。

### 5.3 同册 `REG-STATE-VOCAB-001` 的 description——去掉写死的 28/10/12/5/1

为什么：散文写死分轴计数（10+12+5+1=28）与条目数组（63）双头记账必漂（宪法 §4.3/§9.5）。
实测该册 `axis` 字段值域有两套写法并存（中文轴名 宏观10/情绪13/预测5/个股1 与缩写轴名
m.regime12/e.cycle9/m-to-e2/e-to-e7 1/f.plan3/f.trans2/s.anchored1/s.category2/s.strength1/risk fsm1），
合并口径为 宏观 22 / 情绪 25 / 预测 10 / 个股 5 / risk fsm 1 = 63。**建议改成字段引用而不写数**：

```diff
-        description: 28 套封闭状态/情绪词表逐套登记（四轴：宏观 regime 10/情绪周期 12/预测预案 5/个股行为 1 合并条）——官方词表本体=zephyr.shared.vocab.market_state（SH-VOCAB-001），撞名冲突 C1/C2/C5/C6/C9/C11 注记（DLOOP-V2-STATE-VOCAB-UNIFICATION W2）
+        description: 封闭状态/情绪词表逐套登记（套数以本条 entry_count 字段为准，勿在散文写死；分轴见各条 axis 字段）——官方词表本体=zephyr.shared.vocab.market_state（SH-VOCAB-001），撞名冲突 C1/C2/C5/C6/C9/C11 注记（DLOOP-V2-STATE-VOCAB-UNIFICATION W2）
```

复算命令：`python -c "import yaml;print(len(yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml',encoding='utf-8'))['vocabularies']))"` → 63。

### 5.4 `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`——10 条错配

为什么：`ssot_path` 是模块归属/depgraph 的真源指针，`covers` 是域能力承诺；二者与代码面脱钩即"说它管、它不在"。
分两类：**A 类=可确定候选真源**（给出 diff，仍需域主点头）；**B 类=须裁定**（不存在唯一候选，本包不代裁路径归属）。

A 类（#7 agent_communication：covers 声称的 3 个符号实体在 a2a_protocol）：

```diff
   - domain: D_AUTONOMY_CORE
     subdomain: agent_communication
-    ssot_path: src/zephyr/autonomy_core/
+    ssot_path: src/zephyr/infrastructure/a2a_protocol/   # 实测 A2AMessage=a2a_schemas.py / ConflictDetector=layer3_coordination/conflict_detector.py；落地前请核 ssot_path 唯一性（是否已被其他条目占用）
```

A 类（#10 data_source_integrator：covers 用厂商名，源码是 Provider 模块名——改 covers 文案比改路径更贴真源）：

```diff
   - domain: D_DATA
     subdomain: data_source_integrator
     covers:
-      - 多源自动下载编排(miniQMT/AKShare/Tushare/Baostock/CLS/EastMoney/TDX/TickFlow/RSS)
+      - 多源自动下载编排(miniQMT/AKShare/Tushare/Baostock/CLS/EastMoney/TDX/TickFlow/RSS —— 符号名以实现模块为准：implementations/cls_provider.py、implementations/eastmoney_news_provider.py 等；本条为命名形态差，非能力缺失)
```

B 类（#1–#5 路径不存在/占位；#6/#9 声称符号全仓 0 命中；#8 符号命中在他域）——**逐条须裁定，本包不给臆测路径**：

| # | 条目 | 实测事实 | 待裁问题 |
|---|---|---|---|
| 1–2 | D_AUTONOMY_PERM/budget_enforcement、/escalation | `src/zephyr/autonomy_perm/` 不存在；仓内 `autonomy_perm` 仅作为域名字符串出现（`governance/agent_spec/rbac_bridge.py` 等） | 该域整块无实体：是真未落地还是路径写错？RBAC 实现在 `src/zephyr/security/access_control/`，是否指此？ |
| 3 | D_INFRA_RUNTIME/persistence | `src/zephyr/data/persistence/` 不存在；同名唯一目录 `src/zephyr/governance/persistence/` | 治理域目录能否作 D_INFRA_RUNTIME 子域真源（跨域指向会破"域=目录"口径）？ |
| 4 | D_SHARED/shared_services | `src/zephyr/shared/shared_services/` 不存在；`src/zephyr/shared/` 下无同名子包 | 条目退役（注册表净删=high 门位）还是补实体？ |
| 5 | D_TEST/test_domain_placeholder | `ssot_path` 写成括注 `(depgraph domains.ssot_path 为空)` | 占位是否保留？保留则需显式豁免登记，不允许静默绿 |
| 6 | D_GOV_DRIFT/drift_detection | `CanaryController`/`CascadeDetector` 全仓 0 命中（`src/zephyr/gov_drift/` 存在） | covers 承诺未建能力——删声称还是列 backlog？ |
| 8 | D_SECURITY_LLM/llm_defense | `HITL` 命中在 `src/zephyr/integration/pipeline_orchestrator.py`、`src/zephyr/intelligence/*`，非 llm_defense | 是跨域声称还是 covers 文案误挂？ |
| 9 | D_INTEGRATION_GATEWAY/mcp_servers | `KnowledgeBaseServer` 全仓 0 命中（`src/zephyr/integration/mcp/` 存在） | 该 server 是否已退役/更名？ |

复算命令：§1.2 的命令原文（10 条应为 0 条）。

### 5.5 两条"口径文本"补齐（ROOR 侧，非本包可写）

```diff
 # REG-METAQ-001（CR-007 唯一残留 UNSPECIFIED）
       - registry_id: REG-METAQ-001
         physical_path: docs/_working/chain_piling_campaign/snapshots/registry_latest.yaml
-        counting_rule: meta_question 主表行数（快照头部 row_count 字段）
+        counting_rule: row_count 字段值      # 或按快照实际数组键名改写；现文本非"某数组条目数"形态，解析器不猜故报 UNSPECIFIED
```

另：ROOR 77 条里仅 38 条带 `counting_rule`。带齐 `counting_rule` 后，`ENTRY_SPECS` 手工表可逐步退役（净零面）；
本包未动 ROOR 也未删代码表条目，退役节奏交总包。

### 5.6 机生册再生（非 diff，跑命令即可）

```bash
python scripts/governance/generators/generate_registry_master_index.py   # 重写 registry_master_index.yaml（18 行 entry_count 变化，10 行由 0 变实数）
```

本包**未跑写生产版**（只 `--output .runtime/tmp/…` 验证）；落地由总包在同批带上该册。

## 6. registration_needs

见同目录 `registration_needs.yaml`（新建件逐件：file/kind/建议 capability/翻译 name-zh+plain-zh/depgraph/是否需 ALGO-NOTE-SYNC 同批）。

## 7. 施工流水、副发现与未竟项

**流水**：现读 §1（CR-007 前后两跑 + 域册原型测量）→ 改 §2（三件）→ 幂等 §3 → 红证 §4（19 条，其中 2 条逼出尺自身缺陷并修正）→ 补丁文本 §5 → registration_needs → 静态面复核。

**静态面复核**（命令原文，均车道内）：

```bash
python -m ruff check --output-format concise scripts/governance/_shared/registry_entry_count.py \
  scripts/governance/d3_metadata/check_registry_consistency.py \
  scripts/governance/generators/generate_registry_master_index.py \
  tests/governance/test_registry_derivation_canary.py
python -c "import ast; from zephyr.gov_enforcement.commit_gates.high_complexity_gate import _cyclomatic_complexity as cc; ..."
```

实测：ruff 剩 **4 条全部为改前既有**（`git show HEAD:` 副本同判 4 条 BLE001/I001，行号平移），
本包新增行 **0 违规**（唯一新引入的 BLE001 已按房规补 `# noqa: BLE001 + 原因`）；
新增 13 个函数 `_cyclomatic_complexity` 复算最高 **12**（阈值 >15，未调阈值）；
新函数与既有类无重名（ARCH-034 面：本包未新增 class）。

**副发现（只呈报，不在本包处置）**：

1. `check_registry_consistency.py` 在有 finding 且 `scripts/governance/reports/` 目录不存在的新工作树里会
   `FileNotFoundError` 崩在最后写 `findings.jsonl` 一步（判据本身已跑完、结论已打印）。车道内实测复现：
   `FileNotFoundError: ... scripts\governance\reports\findings.jsonl`。修法一行（`mkdir parents=True`），
   但落在本包"只改派生"范围外，未动。
2. `config/.env.clickhouse` 在车道内不存在 ⇒ 该脚本每次跑都打 `CH 配置文件不存在` 警告（本包零 CH 读，未触）。
3. `REG-STATE-VOCAB-001` 目标册的 `axis` 值域两套写法并存（§5.3），是词表册自身的结构问题，不在本包尺面。
4. `registry_entry_count.py` 与 `generate_registry_master_index.py`、`check_registry_consistency.py` 三者代码头
   `module_id` 同为 `MOD-INF-005`——跨文件复用同一 module_id，是否合规由总包按 depgraph 面判。

**未竟项**：

- 52 处 ROOR 散文写死计数（§1.3）只出了复算命令，未逐条出 diff。
- `ENTRY_SPECS` 退役（把 38→77 条 counting_rule 补齐后删手工表）为后续件，本包只做"降级为覆写层"。
- CR-008b（covers 符号核对）默认关（`--check-domain-covers`），因为它要扫源码子树；
  若要进 CI 常态执法面，需总包按 perf 分级登记（本包不自扩执法面）。
