---
ttl: task_bound
session: st-regsolo-20261010
landing_note: 本件由终清波三 st-fclean3-20261012 依统筹批复 M2 闸①代落，正文零改动，仅补 docs/_working 必需的 ttl frontmatter（原文无 frontmatter）；origin sha 见 wave3/26_件 §一
---

# T3 热册盘点 lane（session=st-regsolo-20261010，分析车道 T3）

状态：完结版。数据来源=实跑 `baseline.p0_physical_paths(Path('D:/ZephyrAlpha'))`、`load_roor_index`、PG 只读 SQL（`DatabaseService().get_depgraph_conn(read_only=True)`）、盘面文件头部直读、parse_gate/gate_registry/mass_deletion/reconciler 源码与登记册比对。主仓零写入。

## 结论（≤8 条）

1. 七册物化路径全部机械解析成功，ROOR 交叉核对零漂移（7/7 registry_id 与 maintenance=pg_ledger 全对上）；其中 REG-ERRCODE-001 在 `architecture_model/contracts/`（不在 catalogs/ 目录），扩面时路径常量须按实跑值写。
2. 七册盘面【零 GENERATED 标记、零 frontmatter】；唯一自带生成器痕迹的是 rule_catalog_registry.yaml（头部 `generated_at`/`generated_by: scripts/governance/d3_metadata/generate_rule_catalog.py`、`maintenance: auto`），加标文案可分两档：真投影册（CAPCAN/module_translation/rule_catalog）与 PG 登记册（arch_issue/errcode/candidate/ruling）。
3. parse_gate 现 watch 面仅 2 册：CAPCAN（capability_registry 全量档）+ data_asset（非 P0）；**七册中只有 CAPCAN 被看**。profile 断言分叉点=`_structural_issues` 的 `if profile == "capability_registry"`（di_seam_exemptions 末位+creation_tokens list 只适用 CAPCAN），六册走 basic 档（parse+根键唯一）零新代码分支即可扩。
4. 投影状态文件（v2 map）已武装 2 册：CAPCAN（rev=130，2026-10-09）与 module_translation（rev=9，2026-10-08）；但 module_translation **已武装却未被 gate 看**——tamper 判别只在 watched 文件上触发，故它现在的手改拦不住，只差 `_WATCH_FILES` 加一行即闭环。
5. PG 侧七册全部有已发布快照（registry_snapshot 最新版：CAPCAN v132/14819 条、MODULE-TRANSLATION v10/8759、DOC v7/302、ARCH-ISSUE v7/815、ERRCODE v4/800、CAND v5/623、RULING v9/302）——render 首打的 PG 数据面齐备，无需先补账。
6. registry_catalog 表的 unique_key_fields 列七册全 NULL（盘面 YAML 头声明未回填库列；CAPCAN 盘面 L1-6 有 `unique_key:` 声明）——扩面若依赖库列声明需先跑一次 import/reconcile 回填，仅做 parse+tamper 执法则不阻塞。
7. FRONT_DOOR 执法形态：无独立 commit gate（gate_registry 查无 front 条目）；=标记行内嵌 `regenerate && git diff --exit-code` 命令 + `library_regen_reconciler.py:183` 事件触发再生（"前门双投再生"）。七册加标照抄此形态即可：标记行（含重生成命令）+ 投影册由 registry_projection_generator 接管再生。
8. 武装顺序建议：module_translation（只加 watch）→ rule_catalog（生成器语义最贴）→ arch_issue/ruling/candidate → errcode（有 GATE-ERRCODE 双向对账门共存，结构门与对账门互补不冲突）；每册先 `--check` 验零漂移再 `--render` 首打写状态文件。

## 七册盘点总表

| registry_id | 物理路径（实跑） | 行数 | GENERATED现状 | parse_gate现状 | 状态文件武装 | PG快照版本 | PG entry_count | catalog.unique_key_fields |
|---|---|---|---|---|---|---|---|---|
| REG-CAPCAN-001 | docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | 66043 | 无标记无frontmatter（首行=`unique_key:`声明） | watched=capability_registry 档 | 是（v2 map，rev=130，2026-10-09T14:22Z） | 132 | 14819 | NULL（盘面有声明） |
| REG-MODULE-TRANSLATION-001 | docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | 68162 | 无标记无frontmatter（头部标量含 registry_id） | 未 watch | 是（rev=9，2026-10-08T13:00Z） | 10 | 8759 | NULL |
| REG-DOC-001 | docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml | 4997 | 无标记；有 `generated_at: '2026-10-04T12:10:38Z'`+`generated_by: .../generate_rule_catalog.py`+`maintenance: auto` | 未 watch | 否 | 7 | 302 | NULL |
| REG-ARCH-ISSUE-001 | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | 10278 | 无标记；`# [A_config]` 注释锚 | 未 watch | 否 | 7 | 815 | NULL |
| REG-ERRCODE-001 | architecture_model/contracts/error_code_registry.yaml | 3921 | 无标记；`# --- 治理锚定 ---` 注释块 | 未 watch | 否 | 4 | 800 | NULL |
| REG-CAND-001 | docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml | 21343 | 无标记；`# [A_config]` 注释锚 | 未 watch | 否 | 5 | 623 | NULL |
| REG-RULING-001 | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | 4714 | 无标记；`# [A_config]` 注释锚 | 未 watch | 否 | 9 | 302 | NULL |

ROOR 交叉核对（`load_roor_index` 实跑）：7/7 registry_id 匹配、maintenance 全=`pg_ledger`（CAPCAN/module_translation/candidate/ruling 带注释 "2026-10-04 cutover：文件=YAML 只读投影，条目写路径唯一入口=意图 API registry_ledger.api"）。注意 PG catalog 表内 maintenance 值滞后（CAPCAN='semi-auto(...)'、其余='manual'），与 ROOR 的 pg_ledger 漂移——非本 lane 阻塞项，呈报备查。

## GENERATED 标记范本原文（docs/library/FRONT_DOOR.md 逐字）

frontmatter（L1-5）：

```yaml
---
ttl: permanent
doc_type: index
generated_by: scripts/governance/generators/generate_front_door.py
---
```

标记行（L7，逐字）：

```
<!-- GENERATED FILE — regenerate: python scripts/governance/generators/generate_front_door.py && git diff --exit-code；手改必被覆盖 -->
```

配套维护教义（L49-52 逐字要点）：

- "本页由 generate_front_door.py 从 ROOR/registry_master_index/INDEX.md/根宪法 §7 派生，禁手改。"
- "发现本页与真源不一致 = 立即 regenerate；仍不一致 = 真源有病，修真源而非本页。"
- 生成闭环支柱（L47）："生成物必过 `regenerate && diff --exit-code`"。

门钩/重生成：

- 无独立 commit gate 挂 FRONT_DOOR（gate_registry.yaml grep "front" 零命中）。
- 事件触发再生钩=`src/zephyr/library/library_regen_reconciler.py:183`：`run_subprocess_hidden(["python", "scripts/governance/generators/generate_front_door.py"], cwd=project_root, timeout=120)`，日志"前门双投再生 rc=0"（符合 §9.3 事件触发红线，非 cron）。
- 七册对应物=投影通道 `python scripts/governance/registry_projection/registry_projection_generator.py --render`（CLI 参数实查：`--check` 零写判漂移 / `--render` 四象限全自动处置 PG wins / `--snapshot-file` / `--registry-id` 缺省 REG-CAPCAN-001 / `--physical-path` 缺省 capability 册 / `--project-root` / `--session`）——**已支持逐册传参，六册首打无需改生成器**。

## 扩面方案建议（profile 分档+武装顺序）

### profile 分档

- `_WATCH_FILES: dict[str, str]`（registry_yaml_parse_gate.py:95）现两档：`capability_registry`（parse+根键唯一+di_seam_exemptions 末位+creation_tokens list）、`data_asset_registry`（parse+根键唯一）。
- 断言分叉点=`_structural_issues()` 内 `if profile == "capability_registry"`——capability 专断言不会误伤他册；六册直接复用 data_asset 档（或更名 `registry_basic`，语义更准，改名需同步 :353 的 watched 组装与档名字符串，二选一）。
- `_projection_tamper_issue()`（:121）与档名无关，对一切 watched 文件生效：状态文件 v2 map 按 `registry_path` 匹配本册→`content_sha256(staged) != state.content_sha256` 即阻断；未武装/别册/状态损坏一律 fail-open。→ **watch+武装=手改必拦；生成器 render 后 staged==state=必过**（判别真源=本地状态文件，零 PG 依赖）。
- A-12 token 滞后判别（:214，`_head_token_lag_issue`）在 `profile == "capability_registry"` 分支内才调用——扩面后六册自动不触发（它们无 creation_tokens），行为面干净。
- 建议扩面 watch 表（basic 档全部六册；CAPCAN 保持原档不动）：

```python
_WATCH_FILES = {
    "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml": "capability_registry",
    "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml": "data_asset_registry",
    "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml": "data_asset_registry",  # 或 registry_basic
    "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml": "data_asset_registry",
    "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml": "data_asset_registry",
    "architecture_model/contracts/error_code_registry.yaml": "data_asset_registry",
    "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml": "data_asset_registry",
    "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml": "data_asset_registry",
}
```

### 武装顺序（render 首打，六册中前 1 册已武装）

0. 前置闸：每册先跑 `registry_projection_generator.py --registry-id <rid> --physical-path <path> --check` 验零漂移（PG↔YAML 同步才允许 render；否则 PG-wins 首打会吞掉 YAML 侧未同步手改）。PG 快照七册齐备（上表），账面无缺。
1. **module_translation**：已武装（状态文件有条目）→ 只加 `_WATCH_FILES` 一行即闭环，零新武装，第一刀最便宜。
2. **rule_catalog**：`--registry-id REG-DOC-001 --physical-path docs/.../rule_catalog_registry.yaml --render` 首打；册头本有 generated_by/generated_at/maintenance: auto，与 GENERATED 语义零冲突。
3. **arch_issue / ruling / candidate**：同命令逐册首打（maintenance=pg_ledger 已声明 PG 为真源，render 即把该声明兑现）；ruling 册注意与 RULE-RULING"裁定#NNN 同 commit 原子"共存——经意图 API 写 PG 后重打投影再同 commit 提交，教义不冲突。
4. **errcode**（architecture_model/contracts/）：与 GATE-ERRCODE（pre-commit 双向对账，files_trigger 含本册）共存：GATE-ERRCODE 管"条目↔代码一致"，parse gate 管"结构+tamper"，正交互补；但它是七册中唯一不在 catalogs/ 目录的，路径常量照实跑值。
5. 每册武装落地后：状态文件条目出现该册 `registry_path` 键（=武装完成判据），随后任何非生成器 diff 立即被 tamper 拦。
6. 配套（施工车道执行，本 lane 仅提示）：加标文案建议按"投影册/登记册"两档套 FRONT_DOOR L7 模板，重生成命令分别指 registry_projection_generator --render（5 册投影）与各自生成器/意图 API（ruling/candidate/arch_issue 为 API 登记+render）；热文件写入必走 safe_write_text（§1.13）；改 parse_gate.py 本身先 claim。

## 手改一行会被什么拦——现状 vs 扩面后矩阵

| 册 | 手改一行：现状拦截面 | 扩面后拦截面 |
|---|---|---|
| CAPCAN | 结构坏（解析炸/双根键/exemptions 键序/ct 非 list）→ REGISTRY-YAML-PARSE 档断言拦；任意字节手改 → tamper 指纹拦；删 token → A-12 滞后拦；净删超阈 → REGISTRY-MASS-DELETION | 不变（已是全量档） |
| module_translation | 结构坏/手改内容 → **无人拦**（已武装但未被 gate 看）；净删 → MASS-DELETION；提交时 BLOOD-FLESH（files_trigger 含本册，gate_registry:1334）仅顺带 | tamper 指纹拦任意手改 + parse/根键唯一拦结构坏 |
| rule_catalog | 手改 → 无人拦（但下次 generate_rule_catalog 再生即覆盖）；净删 → MASS-DELETION | tamper 拦 + 结构断言拦；GENERATED 标记+再生闭环兑现 |
| arch_issue | 手改 → 无人拦；净删 → MASS-DELETION | 同上 |
| ruling | 手改 → 无人拦（RULE-RULING 只是流程纪律无门禁面）；净删 → MASS-DELETION | 同上 |
| candidate | 手改 → 无人拦；净删 → MASS-DELETION | 同上 |
| errcode | 条目与代码不一致 → GATE-ERRCODE 双向对账拦；纯结构坏/注释手改 → 无人拦 | GATE-ERRCODE 保留 + tamper 拦任意手改 + 结构断言拦 |

MASS-DELETION 覆盖依据：registry_mass_deletion_gate.py:38 "staged 命中 _REGISTRY_DIR_MARKER（登记表目录）或 _WATCH_FILES"——catalogs/ 目录级兜底，contracts/error_code 需核对其 _WATCH_FILES 是否显式含（本 lane 未展开，非阻塞）。

## 证据

1. `src/zephyr/governance/registry_ledger/baseline.py:102` P0_REGISTRY_IDS 七元组；:113 `p0_physical_paths`（ROOR∪ catalogs/+contracts/ 目录机械枚举∪头部 registry_id 扫描）；:152 `load_roor_index`（first-wins，返回 {path: {registry_id, maintenance}}）。实跑输出=上表路径列（零 KeyError）。
2. `src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py`：:95 `_WATCH_FILES` 两册两档；:104 `_TEACH`；:118 `_PROJECTION_STATE_REL=.runtime/projection/registry_projection_state.json`；:121 `_projection_tamper_issue`（v2 map registry_path 匹配→staged sha≠state sha 阻断；未武装 fail-open；阻断文案内嵌 `registry_projection_generator.py --render`）；:182-243 A-12 token 滞后判别（白名单 `[allow-mass-deletion:reason≥10字]`，仅 capability 档调用）；:285 `_structural_issues`（档分叉 :314）；:328 gate 构造（gate_id=REGISTRY-YAML-PARSE，priority=54，own-scope 经 `_build_own_scope`）。
3. `.runtime/projection/registry_projection_state.json`：version=2，registries 键=capability 册（rev=130，2026-10-09T14:22:36Z，entry_counts 含 creation_tokens=14422）与 module_translation 册（rev=9，2026-10-08T13:00:58Z，四族 8759 条）。
4. PG 只读 SQL 实跑（DatabaseService().get_depgraph_conn(read_only=True)）：registry_snapshot 七册最新版=v132/14819、v10/8759、v7/302、v7/815、v4/800、v5/623、v9/302（含 content_sha256 全有值）；registry_catalog 七册 physical_path 全匹配实跑路径、unique_key_fields 全 NULL、maintenance=CAPCAN 'semi-auto(...)' 其余 'manual'。
5. 七册头部 1-10 行实读：全部无 `<!-- GENERATED FILE -->` 标记、无 `---` frontmatter；rule_catalog 册头含 `generated_at/generated_by/maintenance: auto`；CAPCAN 册首行即 `unique_key:` 逐族声明（capabilities: [capability_id]、creation_tokens: [file, token]）。
6. `docs/library/FRONT_DOOR.md` L1-7（frontmatter+GENERATED 标记逐字）、L47/L49-52（生成闭环教义）；`src/zephyr/library/library_regen_reconciler.py:181-189`（事件触发再生钩）；`scripts/governance/generators/generate_front_door.py`（"GENERATED FILE" 标记唯一产出点）。
7. `scripts/governance/registry_projection/registry_projection_generator.py:56-62`：CLI 已有 `--check/--render/--snapshot-file/--registry-id/--physical-path/--project-root/--session`，缺省册=CAPCAN——六册首打零生成器改造。
8. `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`：:354 GATE-ERRCODE files_trigger=`^(src/zephyr/.*\.py|architecture_model/contracts/error_code_registry\.yaml)$`（active）；:1328-1340 BLOOD-FLESH files_trigger 含 module_translation 册（active, own_scope=true）；"front" 零命中（FRONT_DOOR 无 commit gate）。
