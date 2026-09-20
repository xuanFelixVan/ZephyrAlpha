---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---
# W1b 生成器与注册表先例挖矿（module_translation_registry 重复键核实 + layer 字段先例套路）

- 战役：st-vocabconsol-20260918 / 环节：W1（三路侦察之 W1b）
- 实测时间：2026-09-18 04:40–05:05（HEAD=`08d3fa97dc`，Python 3.12.8 系统 python）
- 被测真源：`docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`
  （HEAD 版 61505 行 / 3188538 B / `version: 1.8.3` / `last_updated: 2026-08-18`；
  **实测期间工作区副本被并发会话推进**：7090→7093 条目，`git status` 显示 M）
- 上位骨架：`docs/_working/2026-09-18_vocab_consolidation_campaign/00_skeleton.md` §2 W4「疑似病灶：loader 重复键吞条目待 W1 核实」

## 0. 结论速览（先给判定，证据在后）

| 疑点 | 判定 | 一句话根因 |
|------|------|-----------|
| 「8053 行 vs 唯一 7199 = YAML 重复键吞条目」 | **不成立（口径错配）** | 8063 条 `module_path:` 行里 **973 条属另一顶层段落 `algo_submodules`**（翻译 loader 不读），与 `entries` 段 7090 条混在一起数了 |
| 字面 YAML 重复映射键（safe_load 静默覆盖） | **零命中** | 自定义 Strict 构造器全文件扫描：`literal duplicate mapping keys = 0`，没有任何键在 safe_load 下被静默丢弃 |
| 同 `module_path` 的重复条目 | **成立，但只有 30 组（非 854）** | `entries` 列表内 30 个 module_path 各出现 2 次：早期 auto-extract 占位条目 + 2026-08-23 人工 curated 批次重复登记 |
| 「被吞」的真实机制 | **成立（在 loader 层，不在 YAML 层）** | `_load_from_yaml()` 把 7090 条列表折叠成 `{module_path: …}` dict，**后写覆盖前写** → 30 条陈旧占位条目在消费侧不可见；账实差 7090 vs 7060（HEAD 口径，工作区并发态 7093 vs 7063） |
| 生成器是否幂等 | **部分幂等，且有字段吞噬副作用** | `add_module_translation.py` 是文本级 upsert（命中→**整块替换**为固定 7 字段），单条重写幂等；但 ①只替换首个命中块（存量重复无法靠它自愈）②会把条目上的非规范字段（`module_id`/`build_status`/`domain`）**一并抹掉** |
| 唯一键声明是否生效 | **未生效** | `unique_key: [module_path]` 的唯一消费方只用它反查"id 键名"，从不判唯一性 → 重复条目复发无拦截 |
| 官方写手是否 CAS | **否（宪法级发现）** | `add_module_translation.py` L320 裸 `write_text` 写热文件，未走 `safe_write_text`——违反 AGENTS 硬规则 13，且疑为本次重复带的成因（详见 §3） |
| `layer` 字段能不能直接加 | **有词表撞车风险，须先裁定** | 受控词表 `layer_vocabulary.yaml` v2.0.0 已占用 `layer` 名（4 值 `L0_infrastructure/L1_foundation/L2_domain/L3_application`），且运行时真源是 depgraph `domains.layer_id`（DB CHECK + 双 trigger），骨架 W4a 拟用的 `governance/business/ai/infrastructure` 四值是**另一套语义** |
| 空 domain 条目 | **2115 条（清单已落盘）** | `''` 2089 + `null` 19 + 键缺失（用 `domain:` 而非 `domain_id:`）7；其中 tests/ 占 1690 条（80%） |

## 1. 重复键实测（口径先对齐，再谈病灶）

### 1.1 行数账（HEAD 版）

```
grep -c "module_path:"   = 8064   ← 含 entry_schema 的 "  module_path: str" 1 行
grep -c "^- module_path:" = 8063   ← 真条目行（顶格列表项）
```

8063 按段落拆分（`yaml.safe_load` 实测，非行数估算）：

| 顶层段落 | 起始行 | 含 module_path 的列表项 | 段内唯一 module_path | 是否被 loader 读取 |
|---------|-------|------------------------|---------------------|-------------------|
| `entries:` | L33 | **7090** | 7060 | ✅ 唯一被读段 |
| `battle_map_steps:` | L50347 | 0（键=`step_id`） | — | ❌ |
| `battle_map_cross_cutting:` | L54807 | 0（键=`category`） | — | ❌ |
| `algo_submodules:` | L55666 | **973** | 401 | ❌（设计如此，由 `algo_flow_translation_sync.py` 派生重建） |

对账：7090 + 973 + 1(entry_schema) = **8064** ✅
唯一集：`entries` 唯一 7060 ∪ `algo_submodules` 唯一 401（交集 252）= **7209**（≈任务给的"唯一 7199"，差值即并发会话新增）

> **要点**：所谓"8053 vs 7199 差 854 条被吞"是**跨段混算**产物。真实病灶只有 `entries` 段内 **30 组二重键**。
> 附带发现：`algo_submodules` 段自身 973 项只覆盖 401 个 module_path（一图多节点派生件），
> 该段是**生成物**（`scripts/governance/_shared/algo_flow_translation_sync.py`，
> INVARIANTS 明写"mtr algo_submodules 段整体派生重建"+"禁整文件重序列化"），与 `entries` 人工段同处一文件，是"行数口径易被误读"的结构性原因。

### 1.2 字面重复键扫描（决定"吞条目"是否发生在 YAML 层）

自定义 Strict 构造器遍历整个文件的 MappingNode，比较同一节点内键重复：

```
literal duplicate mapping keys in whole file: 0
```

→ **safe_load 在本文件没有任何静默覆盖**：`entries` 是**列表**，重复 `module_path` 是"列表里两个 dict"，不是"一个 dict 里两个同名键"，
YAML 规范下合法、PyYAML 不报错也不丢项。所以"重复键吞条目"若成立，只可能发生在**下游按 module_path 建 dict 的消费方**——事实正是如此（§2）。

### 1.3 30 组重复的定性 = 同一路径两段（非随机脏重复）

| 特征 | 实测 |
|------|------|
| 组数 | 30（每组恰好 2 条，无三重） |
| 两条是否字节相同 | **0 组相同**，30 组字段级冲突 |
| `domain_id` 是否一致 | **30/30 一致**（不存在域错标分歧） |
| 早期条目（占位） | 24/30 的 `desc_zh` 为空；`name_zh` 呈 `X模块` / `X（x.py）` 自动抽取形态；源自 `ab168e55c8` 2026-08-01「模块翻译注册表双语真源扩容」批量 auto-extract |
| 后期条目（curated） | 30/30 有实质 `desc_zh`+`plain_zh`；集中在**同一连续批次** L41934–L42680，源自 `06fedb8d9a` 2026-08-23「长城任务批1登记合并——module_translation plain_zh +20」（该 commit 475 行改 / 330 行删，属大批量重写） |
| 谁在消费侧胜出 | **curated 胜出**（列表位次靠后 → dict 后写覆盖）→ 当前**显示层无 bug**，但真源里躺着 30 条陈旧影子条目 |

样例（同路径两段，域相同、内容代次不同）：

```
src/zephyr/ex_core/order_splitter.py
  L3581(占位) name_zh=订单拆分器     desc_zh=订单拆分器（order_splitter.py）
  L42277(人工) name_zh=拆单器         desc_zh=TWAP/VWAP拆单（无Level-2依赖，日线/分钟线历史量能曲线权重注入），整手对齐+Decimal守恒
src/zephyr/compliance/async_intercept_queue.py
  L1848(占位) name_zh=异步intercept队列 desc_zh=异步intercept队列模块
  L42004(人工) name_zh=异步拦截队列     desc_zh=SecurityGateway同步拦截延迟的异步化升级(GAP-L10-001)+内容缓存
```

30 组全清单（含 HEAD 锚定的占位行/curated 行行号）见本文**附录 B**（不另落临时件，避免并发风暴误删）。
分布前缀：`sell_decision/core` 9 / `position/core` 7 / `ex_core` 5 / `signal_ashare` 6 / `frontend/implementations` 2 / `compliance` 1。

> **历史先例**：同类病灶已被治过一次——`8a806fff59` 2026-08-01
> 「fix(candidate-pool): **翻译真源去重52脏重复**+harvest脚本幂等治本」。
> 即"翻译真源重复条目"是**复发型**问题（大批量重写批次不带去重前置），W4 治本须带**常驻去重校验**，不能只做一次性清理。

## 2. loader 解析方式（`scripts/governance/_shared/module_translation_loader.py`）

| 维度 | 实测 |
|------|------|
| 解析方式 | `yaml.safe_load(_REGISTRY_YAML.read_text(encoding="utf-8"))` —— **整文件一次性解析**，非逐行正则 |
| 读取范围 | 仅 `data.get("entries", [])`；`algo_submodules` / `battle_map_*` 段**不读** |
| 键归一 | `str(path).replace("\\","/")`（Windows 反斜杠兼容） |
| 输出结构 | `{module_path: {name_zh, name_en, desc_zh, desc_en, plain_zh}}` —— **字段白名单硬编码 5 个**，条目上的其他字段（`domain_id`/`module_id`/`build_status`/未来的 `layer`）**一律不可见** |
| 重复键行为 | 列表→dict 折叠，**后写覆盖前写**（Python dict 语义），无冲突检测、无告警 → 这就是"吞条目"的真实落点：7090 条声明 → **7063 个可见键**（HEAD 版 7060） |
| 降级 | 任何异常 `except Exception: return {}`（**静默空表**，调用方自行回退 docstring） |
| 缓存 | 模块级 `_PATH_CACHE` + `_PATH_CACHE_MTIME`（`st-commitspeed-20260916` P0-B 治本：Serializer 长进程 mtime 变化即重载，避免 drain 后续项误判 TRANSLATION-COVERAGE 死信） |
| 消费方（import 本 loader，共 10 件） | `scripts/governance/align_battle_map.py`、`apply_depgraph.py`、`d3_metadata/add_module_translation.py`、`d5_architecture/generators/{align_panoramas, generate_battle_map_diagram, generate_candidate_module_report, generate_domain_doc, generate_module_algorithm_overview}.py`、`src/zephyr/governance/audit/translation_coverage_reconciler.py`、`src/zephyr/gov_enforcement/commit_gates/translation_coverage_gate.py` |
| 测试 | 头注自称 `tests/test_module_translation_loader.py (规划中)`——**该测试文件实际不存在**（全库 grep 仅 `tests/governance/rule_bridge/test_commit_pipeline_redblue.py` 间接引用）。loader 是 10 个消费方的公共入口却零直测，W4 改 loader 属**无安全网施工** |

**给 W4 的硬约束**：想让 `layer` 被下游看见，必须同时扩 loader 的字段白名单（否则加了 YAML 字段=死字段）；
更治本的方向是把白名单改成"透传 + 已知字段缺省"，避免每加一个字段都要改 loader。

## 3. 写入侧是否幂等（`scripts/governance/d3_metadata/add_module_translation.py`）

真实路径确认：`scripts/governance/d3_metadata/add_module_translation.py`（380 行；**非** `scripts/add_module_translation.py`）。

| 环节 | 实现（行号） | 幂等性判定 |
|------|-------------|-----------|
| 段落切分 | `_split_entries_section()` L156–200：定位列 0 `entries:` 行 → 再定位下一个顶层键（`battle_map_steps:`）作 tail；新增落 entries 列表尾，**绝不追加文件尾** | 治本件（L161 注释记 2026-08-02 首版误追加文件尾损坏真源、git checkout 回滚的事故） |
| 块切分 | `re.split(r"\n(?=- module_path:)")` L227；首条目特殊处理 L216–220（注释记首版漏匹配致追加重复的 bug） | ✅ |
| upsert 命中 | L230–234：遍历 blocks，首个 `_normalize_path(m.group(1)) == norm_path` 即 `blocks[i] = new_block` 后 **return** | ⚠️ **只替换首个命中** → 存量 30 组重复无法靠本工具自愈；且**替换后另一条仍在**（若有人对重复路径再跑一次，只收敛一份） |
| 块格式 | `_format_entry_block()` L138–153：**固定 7 行**（module_path/domain_id/name_zh/name_en/desc_zh/desc_en/plain_zh），5 个文本字段强制双引号转义 | ❌ **字段吞噬器**：条目上的 `module_id`(47 条) / `build_status`(42 条) / `domain`(7 条) 一旦经本工具更新即被抹除 → 任何未来新增字段（含 `layer`）必须同步进 `_format_entry_block`，否则"跑一次补标就掉一次字段" |
| 写入前校验 | `_validate_plain()` L121–135：`plain_zh` 非空 + CJK ≥ 阈值 + 拒 `is_generic_plain_zh`/`is_generic_plain_suffix` 模板 | ✅ 治本（拒模板化简介） |
| 写后自校 | L328–334：重新 `safe_load` 确认命中路径存在，否则 `EXIT_IO` | ✅（但**只验存在性，不验唯一性** → 重复条目照样通过） |
| 并发安全 | **裸 `REGISTRY_YAML.write_text(new_text)`（L318–322）——未走 `safe_write_text` CAS**；仅事后 `_invalidate_loader_cache()` L267（✅ 缓存失效已内建） | ❌ **违宪件**：AGENTS 硬规则 13「热文件（注册表）写入必用 `safe_write_text`（CAS 防并发覆盖），禁裸 Edit/Write」。本表正被多会话实时写（§7 漂移实录），"读原文→改→整写回"没有 base 校验 = **陈旧快照覆写**通道；对照同域两件均已 CAS 治本（`harvest_candidates_from_drafts.append_to_file` 2026-08-23 接入、`algo_flow_translation_sync` 走 `safe_write_text`），本工具是**漏网第三件**。疑即 L41934–L42680 curated 重复带的成因（基于陈旧 base 整写回，旧占位条目被"复活"） |
| 唯一键声明 | YAML 头 `unique_key: [module_path]`（L25–26）。全库唯一消费方 = `scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py::_expected_id_keys()` L147–153，**只用它解析"该列表的 id 键名叫什么"**，从不判定唯一性 | ❌ **无任何去重校验**——这是重复条目能复发两次（`8a806fff59` 去重 52 → 今又 30）的制度性缺口；W4 治本应把 `unique_key` 语义升级为"实测唯一"（机生于 gate/reconciler，非新造声明） |

其他写入者（同文件多写手，是字段形态异质与重复的根源）：

| 写手 | 写入形态 | 幂等/风险 |
|------|---------|----------|
| `scripts/governance/harvest_candidates_from_drafts.py` | 文本 `append_to_file()` L400+（CAS），键=`module_path` 直接塞候选 ID `CAND-HARVEST-xxxx`；幂等靠 `existing_translation_keys()` L276–294（**仅对 `CAND-HARVEST-` 前缀去重**） | 当前 registry 内 `CAND-HARVEST` 条目 = 0（已被清），但该函数的去重域是自设前缀，不覆盖普通路径条目 |
| `scripts/governance/_shared/algo_flow_translation_sync.py` | `algo_submodules` 段整体派生重建 + 段级文本替换保人工段字节；注册表写走 `safe_write_text` CAS | 明确"禁整文件重序列化"（历史事故：整文件 safe_load→safe_dump 把 entries 人工注释/格式全冲掉） |
| `scripts/governance/oneoff/fix_module_translation_zh.py` / `_fix_remaining_en.py` | 逐行正则改写 `name_zh` 等字段 | 一次性件，改写不新增条目 |
| `scripts/governance/d5_architecture/generators/generate_domain_doc.py`、`align_battle_map.py`、`align_panoramas.py` | 读 `entries` 的 `domain_id` 做域分组/锚定（**绕开 loader 直读 YAML**，因为 loader 不暴露 domain_id） | 加字段时这批直读者也在连坐面内 |

条目字段形态异质实测（HEAD）：

| key 形态 | 条数 | 来源判定 |
|---------|-----|---------|
| 规范 7 字段 | 6994 | `add_module_translation.py` |
| +`module_id` | 47 | 他批手写/脚本回填 |
| +`build_status`（全为 `dormant`） | 42 | alt_data 休眠标记批 |
| 只有 `domain`+`module_path`+`name_zh`+`plain_zh`（**无 `domain_id`**） | 7 | `schemas/categories/market/*.py` 数据模式件，字段名写成了 `domain` |

## 4. 给注册表加一个新字段的先例套路（"改哪几件"）

### 4.1 先例甲（同表加字段，最直接对标）——`plain_zh`

| commit | 日期 | 触面 |
|--------|------|------|
| `b883925867` feat(doc-gen): plain_zh module translation SSoT | 2026-08-01 | 7 文件：注册表 YAML(+41) / loader(+20) / `generate_domain_doc.py`(−385/+，删硬编码字典改读真源) / 3 个 gate 顺修 + 1 份域文档 |
| `d5d9523bfe` feat(gov): TRANSLATION-COVERAGE 四层防御 | 2026-08-02 | 11 文件：`add_module_translation.py`(新 369) / `translation_coverage_gate.py`(新 280) / `translation_coverage_reconciler.py`(新 341) / `capability_canonical_file_registry.yaml`(+69) / `in_process_gate_registry.yaml`(+9) / `apply_depgraph.py`(+36) / `git_commit_gateway.py`(+4) / 3 个测试 |

即：**字段落地 = 真源 YAML + loader 白名单 + 写入工具 + 生成器消费 + 门禁 + 后台对账 + 能力登记 + 测试**，两轮 commit、合计约 14 件。

### 4.2 先例乙（近一月，字段=派生标记 + 一致性守卫）——`mount_route`

`16fa829c88` 2026-09-16（`strategy_registry.yaml` 加 `mount_route` 显式路由），7 文件：
①注册表 YAML 加字段（6 条显式值）②消费方 `scripts/backtest/auto_mount.py` 改"显式优先+兜底白名单"③**新增守卫** `tests/governance/test_mount_route_consistency.py`（幽灵值/未挂图/格律法/兜底白名单四道）④消费方测试 `test_auto_mount.py` ⑤对齐红蓝测试 ⑥SOP-C §6 真源指针改注。

### 4.3 先例丙（字段口径收口 = 纯生成器批）——`applicable_series`

`6005c324f8` 2026-09-15：`chart_pattern_registry.yaml` 287/287 全量收口，**只动 1 个文件**（注册表 YAML），
裁定语义写在生成器 `--annotate-series` 的子命令注释里，并留一条铁律「**生成器产出口径禁手填**」；
顺带治本"生成器幂等判别式 bug：末条目 block 吞文件尾注释致裸 `in` 判断误跳"。
→ 与 §9.5「静态清单禁手工维护」同轨：**backfill 类改动应只碰 YAML，但必须由带 `--annotate-*` 模式的常驻生成器产出**。

### 4.4 套路归纳：加 `layer` 需要动的清单（必做 6 件 + 建议/连坐 2 件）

| # | 件 | 必做理由 | 先例锚 |
|---|----|---------|--------|
| 1 | `module_translation_registry.yaml`：`entry_schema` 加 `layer: str` + `version` 升 + `last_updated` | 真源声明 | `b883925867` |
| 2 | 词表件：复用 `docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml`（v2.0.0，4 值）或**另起名**；若新建 `domain_layer_mapping.yaml` 须声明与 depgraph `domains.layer_id` 的 SSOT 方向 | **撞车点**，见 §6 | `trae_062_ssot_classification` |
| 3 | `module_translation_loader.py`：`_load_from_yaml` 字段白名单加 `layer`（否则死字段） | §2 | `b883925867`(+20) |
| 4 | `add_module_translation.py`：`_format_entry_block` 加 `layer` 行 + CLI 参数（否则一次 upsert 即抹字段，见 §3） | 字段吞噬器 | `d5d9523bfe` |
| 5 | 派生/backfill 生成器：`layer` = f(`domain_id`) 机生，禁手填；缺 `domain_id` 的 2115 条只能留空/待补标 | §9.5 红线 | `6005c324f8` |
| 6 | 一致性守卫测试：`tests/governance/test_layer_field_consistency.py`（值域合法 / 与 `domains.layer_id` 对账 / 无 domain 不得有 layer） | 复发防御 | `16fa829c88` 的 `test_mount_route_consistency.py` |
| 7 | （可选但建议）`unique_key` 唯一性校验落地：把 `module_path` 唯一性从"声明"变成 gate/reconciler 实测，顺手清掉 30 组存量 | 复发病灶 | `8a806fff59`（52 脏重复去重先例） |
| 8 | （连坐）`registry_master_index.yaml` 的 `entry_count: 7073` 已实数漂移（HEAD 实际 7090）；`battle_map_alignment_gate.py` 把本表列为叙事真源、`translation_coverage_gate/reconciler` 走 loader → 若改 loader 结构须同批跑其测试 | 账实一致 | — |

> 注意一件**假绿**：`scripts/governance/d1_structure/validate_config_integrity.py` L9 的 entry_count 对账
> 读的是 `registry-master-index.yaml`（**连字符，文件不存在**），真实文件叫 `registry_master_index.yaml`（下划线）；
> 且其计数分支只认 `models/rules/states` 键，**不认 `entries`** → 该对账对本表结构性失效。修它=独立小件，别指望它兜底。

## 5. `candidate_module_registry.yaml` 与翻译注册表的域字段关系

| 维度 | `candidate_module_registry.yaml` | `module_translation_registry.yaml` |
|------|----------------------------------|-----------------------------------|
| 唯一键 | `unique_key: [id]`（`CAND-*` / 设计态卡片 ID） | `unique_key: [module_path]`（真实文件路径） |
| 条目数 / 版本 | 623 条 / `version: 1.1.3` | HEAD 7090 条 / `version: 1.8.3` |
| 域字段名 | **`domain`**（62 个不同值，无一条为空） | **`domain_id`**（2115 条为空） |
| 是否已有层字段 | **有 `sub_layer`**（值域被污染：多数填的是目录前缀如 `src/zephyr/signal_ashare/`，另有 20 条填 `L0`，36 条空） | 无 |
| 语义 | 设计态"候选模块"池（未落地/待评估） | 落地态每个 .py 的中英翻译 + 域归属 |

判定：**不是第二真源**（键空间不相交：候选 ID vs 文件路径；且当前 registry 内 `CAND-HARVEST` 条目 0，说明 harvest 不再向翻译表镜像）。
但有两处**口径隐患**须在 W4 一并处置：
1. **字段名分叉**：同一"域"概念在两个注册表里叫 `domain` / `domain_id`，且翻译表内自身有 7 条用 `domain`（`schemas/*.py`）→ 任何"按域派生 layer"的脚本若只认 `domain_id` 会**静默漏 7 条**；只认 `domain` 会反向漏 7083 条。
2. **`sub_layer` 是既有半废层字段**：值域混装（目录前缀 / `L0` / 空），若再引入 `layer`，同域内会出现两个层语义字段。建议裁定：`layer`（受控 4 值）为机生派生，`sub_layer` 标 deprecated 或由 `layer` 取代（净零增长，§4.1 规范预算）。
3. 值域交叉实测：candidate 62 个 `domain` 有 **5 个**不在翻译表出现；翻译表 66 个 `domain_id` 有 **9 个**不在 candidate 出现（`D_GOV_SCRIPTS`/`D_GOV_CODE_QUALITY`/`D_GOV_OPS_RESILIENCE`/`D_GOV_REPAIR`/`D_GOV`/`D_INFRA`/`D_CROSS_ASSET`/`D_FBL_DIAGNOSERS`/`D_PLAN_ENGINE`）→ 与 W1a 的"词表三源差集"同源问题，`domain_id` 词表收敛是补标的前置。

## 6. `layer` 落点必须先裁定的撞车（W4a 风险）

现有事实链（全部实查）：

- `docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml`
  `schema_version: 2.0.0`、`total_values: 4`、`values = L0_infrastructure / L1_foundation / L2_domain / L3_application`，
  文件头自述「**运行时真源：`src/zephyr/governance/depgraph_schema.py` 的 DB trigger；本词表：人类可读视图**」，
  v2.0.0 变更史明写「14 层概念彻底清除——重写为 4 值，与 depgraph `domains` 表 `layer_id` 字段 DB trigger 对齐」。
- `src/zephyr/governance/depgraph_schema.py` L428–1153：`domains.layer_id` 有 CHECK + `chk_domains_layer_id_insert/update` 双 trigger，
  非法值直接 `RAISE(ABORT)`（合法值同上 4 值 + NULL）。
- **域→层的既有官方通道**：`scripts/governance/apply_depgraph.py --update-domain-layer <domain_id> <layer_id>`
  （`SQL_SELECT_DOMAIN_LAYER` / `SQL_UPDATE_DOMAIN_LAYER`，L480–481 / `cmd_update_domain_layer` L4796），
  以及 `--insert-domain D-NEW "名" 业务 L2_domain <path>`（域登记时即带层）。
- `functional_domain_registry.yaml` 里 25 个域的层只在**注释**中出现：
  `# 治本(2026-07-19): 从 DB 反向补 YAML 真源 (layer_id=…)` + `# sync 的 ON CONFLICT 不写这些列…此处仅作文档`
  → 即 **域层真源在 DB（架构数据），YAML 侧刻意不落字段**（RULE-SSOT：架构数据 apply_*.py 直写 DB）。
- 已退役的 `docs/03_modules/module-registry.yaml` 曾在 `registry_consistency_contract.yaml` 声明
  `ssoT_for: [module_id, name, **layer**, functional_domain, …]`（status: retired，G2 收口=幽灵登记）。

→ 冲突点：骨架 W4a 计划新建 `_registry/vocabularies/domain_layer_mapping.yaml`，
受控值 `governance/business/ai/infrastructure`（四层归组）——**与既有受控词表 `layer` 的 4 值同名不同义**。
若直接给翻译条目加 `layer` 字段填新四值，将同时违反：词表唯一真源（`layer` 已注册）+ DB CHECK 语义 + RULE-SSOT 方向。

三条候选路（W2 裁定素材，本文档不下结论）：
- **甲（推荐倾向，改动最小）**：模块层**不落 YAML**，消费侧按 `module_path → domain_id →（depgraph domains.layer_id）` 两跳派生，
  YAML 零新增字段；配套只需在 loader 侧加"域→层"读取（复用 `apply_depgraph` 的 SQL 通道）。
- **乙**：字段改名 `module_layer_group`（或 `arch_layer_group`），值=`governance/business/ai/infrastructure` 新词表，
  与 `layer_vocabulary` 正名并存，并在两份词表头注互指"另一套语义"，防后人混用。
- **丙**：沿用 `layer` 名，但值域强制 = `layer_vocabulary` 的 4 值（L0..L3），由 domain→layer 从 DB 机生镜像，
  YAML 头声明"派生件，禁手填，与 DB 不一致以 DB 为准"（对齐 `layer_vocabulary` 自身的"人类可读视图"定位）。

## 7. 补标工单输入：空 domain 条目统计（清单已落盘）

- 清单：`docs/_working/2026-09-18_vocab_consolidation_campaign/w1_mining/no_domain_list.csv`
  —— **2115 行**，每行一个 `module_path`（正斜杠归一、已去重、字典序）。
  口径：`domain_id` 键缺失 / 值为 `null` / 值为空串（`''` 2089 + `null` 19 + 键缺失 7 = 2115）。
  **锚定 HEAD blob（`git show HEAD:<path>`）产出口径**，与 04:54 工作区副本逐条相同，可安全作为工单输入。
- **并发漂移实录**（本表正被他会话实时写入，落盘件请一律锚 HEAD 复算）：
  实测 04:44→04:58 条目 7090(HEAD) → 7092 → 7093；工作区此刻另多出 **3 条空 domain 新条目**
  （`src/zephyr/strategy_factory/owner_band_t/{data_loader,engine,exam}.py`），未计入本 2115。
  另：本清单**曾被批量重写风暴吞掉一次**（04:56 落盘、04:57 目录内消失，非 stash——`.runtime/workspace_alerts/stash_notice.json` 最新记录停在 09-17），
  已重落并锚 HEAD；此现象与 `16fa829c88` commit message 自曝的「夜间批量重写风暴吞未提交编辑」同型 → **W1 挖矿产出须当轮即走网关提交**，别留在工作区。

| 维度 | 分布 |
|------|------|
| 根目录 | `tests/` **1690**（80%）· `src/` 189 · `scripts/` 126 · `docs/` 56 · `config/` 34 · `architecture_model/` 11 · `schemas/` 7 · `data/` 2 |
| 后缀 | `.py` 1978 · **`.yaml` 137**（注册表里混登了配置/模式件，非 .py 模块） |
| 磁盘存在性 | 2081 条文件真实存在；**34 条磁盘无对应文件**（幽灵条目，含 `tests/context/*`、`tests/audit/audit_core/test_audit_api_lifecycle.py` 等已删测试与 `src/zephyr/infrastructure/model_capability_exam/__init__.py`） |

路径前缀 top15（2 段聚合；`src/` 取 3 段）：

| 前缀 | 条数 | 前缀 | 条数 |
|------|-----|------|-----|
| `tests/feedback` | 108 | `docs/01_policies_and_standards` | 54 |
| `tests/infrastructure` | 105 | `tests/context` | 51 |
| `tests/audit` | 100 | `tests/a2a` | 48 |
| `tests/trading` | 89 | `src/zephyr/infrastructure` | 42 |
| `tests/federated_learning` | 80 | `tests/agent_rbac` | 42 |
| `scripts/governance` | 71 | `tests/utils` | 40 |
| `tests/autonomy` | 71 | 其余 | 1091（共 166 个前缀，长尾） |
| `tests/skill` | 62 | | |
| `tests/llm_security` | 61 | | |

`src/zephyr/*` 子域分布（189 条）：infrastructure 42 · shared 32 · security 21 · governance 16 · integration 11 · data 8 · signal_fundamental 8 · gov_enforcement 6 · intelligence 6 · trading 6 · 其余 33。

**给 W4c 补标的三条判读**（决定工作量真实分布）：
1. **先分层处置，别一锅端 2115**：1690 条在 `tests/`——按 AGENTS 现有纪律 tests 目录本就豁免部分登记（TRANSLATION-COVERAGE 侧），
   若裁定"测试件不需要域"，真实补标面从 2115 骤降到 **~425**（src+scripts+docs+config+architecture_model+schemas+data）。
2. **34 条幽灵条目**应走"条目退役/清偿"而非补标（补标会固化死引用），建议与去重 30 组并入**同一次真源体检批**。
3. **137 条 `.yaml` 条目**是"配置/模式件也进翻译表"的口径问题：层派生对配置件语义不成立，需单独裁定（或改键为 `file_category`）。

## 8. 本环节新增的骨架外条目（须回写 `00_skeleton.md` §2）

- W1b-N1 翻译真源 **30 组二重键 + 34 幽灵条目 + 137 非 .py 条目** → 建议新增中类「W4e 真源体检/去重清偿批」（复发型，先例 `8a806fff59`）。
- W1b-N2 `unique_key` 声明无校验器落地 → 归 W4（或 W3c 常驻差集脚本）承担"键唯一性实测"。
- W1b-N3 `layer` 词表撞车 + DB/YAML 方向 → 归 W2 裁定（三选一）。
- W1b-N4 loader 零直测 + 字段白名单封闭 → 归 W4b（施工前置安全网）。
- W1b-N5 `validate_config_integrity.py` L9 连字符/`entries` 双重假绿 → 独立小件，建议挂 W6 循环检查或另立清偿单。
- W1b-N6 **`add_module_translation.py` 裸 `write_text` 写热文件（无 CAS）** → 违反 AGENTS 硬规则 13；
  W4b 施工若要跑数千次写入，**必须先把该写手接 `safe_write_text`**（同 `algo_flow_translation_sync` 模式），否则补标批本身就是新的覆写风险源。建议独立清偿单（非本战役连根，但 W4 的前置依赖）。
- W1b-N7 loader `except Exception: return {}` 静默空表 + 零直测 → 大规模补标期间任何一次解析失败都会表现为"全库缺翻译"，
  经 TRANSLATION-COVERAGE gate 放大成批量误拦/误 warn。建议 W4b 加 fail-loud 分支（区分"文件缺失"与"解析异常"）+ `tests/governance/test_module_translation_loader.py`。

## 附录 A 复核命令（全只读）

```bash
python --version    # 3.12.8（系统 python，非 3.10）

# 行数与段落账
grep -c "module_path:"   docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -c "^- module_path:" docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
grep -n "^entries:\|^battle_map_steps:\|^battle_map_cross_cutting:\|^algo_submodules:" \
    docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml

# 条目数 / 唯一数 / 重复组 / 字面重复键扫描 / 空 domain 清单
python - <<'PY'
import yaml, collections, subprocess
BS=chr(92); p='docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml'
src=subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8').stdout
d=yaml.safe_load(src); e=d['entries']
c=collections.Counter(str(x['module_path']).replace(BS,'/') for x in e)
print(len(e), len(c), sum(1 for v in c.values() if v>1), len(d['algo_submodules']))
def empty(x):
    v=x.get('domain_id'); return 'domain_id' not in x or v is None or (isinstance(v,str) and not v.strip())
print(sum(1 for x in e if empty(x)))
# 字面重复映射键（应=0）
hits=[]
class S(yaml.SafeLoader): pass
def cm(l,n,deep=False):
    s=set()
    for kn,_ in n.value:
        k=l.construct_object(kn,deep=True)
        if k in s: hits.append((kn.start_mark.line+1,k))
        s.add(k)
    return yaml.SafeLoader.construct_mapping(l,n,deep)
S.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, cm)
yaml.load(src, Loader=S); print('literal dup keys:', len(hits))
PY
```

关键 commit 指针：`ab168e55c8`（占位批量）· `06fedb8d9a`（curated 批量，重复来源）·
`8a806fff59`（52 脏重复去重先例）· `b883925867`+`d5d9523bfe`（plain_zh 加字段两轮）·
`16fa829c88`（mount_route 加字段+守卫）· `6005c324f8`（applicable_series 生成器收口）。

## 附录 B　30 组重复 module_path 全清单（HEAD 锚定行号，按占位行升序）

| # | module_path | 占位条目行 | curated 条目行 |
|---|-------------|-----------|---------------|
| 1 | `src/zephyr/compliance/async_intercept_queue.py` | L1848 | L42004 |
| 2 | `src/zephyr/ex_core/live_simulation_switcher.py` | L3567 | L42284 |
| 3 | `src/zephyr/ex_core/order_splitter.py` | L3581 | L42277 |
| 4 | `src/zephyr/ex_core/services/live_portfolio.py` | L3609 | L42298 |
| 5 | `src/zephyr/frontend/implementations/default_approval_gateway.py` | L6453 | L42025 |
| 6 | `src/zephyr/frontend/implementations/default_notification_manager.py` | L6460 | L42032 |
| 7 | `src/zephyr/signal_ashare/cross_market_conduction_sensor.py` | L9917 | L41955 |
| 8 | `src/zephyr/signal_ashare/ml_forecast/regime_change_detector.py` | L9924 | L41941 |
| 9 | `src/zephyr/signal_ashare/adjustment_cycle_tracker.py` | L9931 | L41962 |
| 10 | `src/zephyr/signal_ashare/market_lifecycle_phase.py` | L9938 | L41969 |
| 11 | `src/zephyr/sell_decision/core/scaling_out_architect.py` | L11834 | L42221 |
| 12 | `src/zephyr/ex_core/miniqmt_channel_manager.py` | L12303 | L42270 |
| 13 | `src/zephyr/position/core/position_behavior_classifier.py` | L13908 | L42193 |
| 14 | `src/zephyr/sell_decision/core/strategy_specific_stop_framework.py` | L14224 | L42207 |
| 15 | `src/zephyr/sell_decision/core/sell_strategy_ab_tester.py` | L15171 | L42242 |
| 16 | `src/zephyr/sell_decision/core/sell_signal_scorer.py` | L15255 | L42200 |
| 17 | `src/zephyr/position/core/cross_strategy_position_merger.py` | L17189 | L42172 |
| 18 | `src/zephyr/sell_decision/core/t_trade_coordinator.py` | L20810 | L42228 |
| 19 | `src/zephyr/ex_core/performance_monitor.py` | L21090 | L42680 |
| 20 | `src/zephyr/signal_ashare/market_state_sensor.py` | L23010 | L41934 |
| 21 | `src/zephyr/ex_core/pre_execution_checker.py` | L23227 | L41997 |
| 22 | `src/zephyr/sell_decision/core/sell_signal_accuracy_monitor.py` | L24628 | L42235 |
| 23 | `src/zephyr/sell_decision/core/exit_scenario_planner.py` | L27862 | L42214 |
| 24 | `src/zephyr/position/core/position_time_budget.py` | L28858 | L42186 |
| 25 | `src/zephyr/position/core/correlation_regime_monitor.py` | L30428 | L42158 |
| 26 | `src/zephyr/position/core/covariance_estimator.py` | L33265 | L42151 |
| 27 | `src/zephyr/sell_decision/core/sell_execution_quality_tracker.py` | L34238 | L42249 |
| 28 | `src/zephyr/position/core/intraday_position_constraint.py` | L34546 | L42179 |
| 29 | `src/zephyr/signal_ashare/ml_forecast/next_day_8state_forecast.py` | L34686 | L41948 |
| 30 | `src/zephyr/position/core/position_risk_budget_allocator.py` | L34806 | L42165 |

> curated 侧全部落在 **L41934–L42680 连续带**（单批次插入，commit `06fedb8d9a` 2026-08-23）；
> 占位侧散布 L1848–L34806（auto-extract 扩容批 `ab168e55c8` 2026-08-01 及后续）。
> **去重方向明确**：删占位留 curated（curated 30/30 有实质 `desc_zh`，占位 24/30 `desc_zh` 为空）。
> 删后 `entries` 由 7090 项收敛为 7060 项 = loader 可见键数 7060 → **声明/可见差归零**。
