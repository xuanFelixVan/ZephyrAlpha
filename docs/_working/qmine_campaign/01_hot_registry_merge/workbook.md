---
ttl: task_bound
title: QMine作业簿·热册三向合并器治本（同侧键重复+身份判不了死因族）
session: st-qmine-20260925
---
# 热册三向合并器治本 作业簿

## 1 环节定义与边界
对象=commit_queue_landing.py 注册表条目级三向合并内核：`_split_registry_entries`(LAND:247-313) → `_split_passthrough_and_drift`(LAND:443-468) → `_index_family_blocks`(LAND:471-483，**死因判定点**) → `_plan_kept_splices`/`_plan_insert_splices`(LAND:504-575) → `_render_selfcheck`(LAND:578-605)；身份键链=`_entry_identity`(LAND:316-333 委托 gate)→`_merge_entry_identity`(LAND:336-357 token 复合)→`_translation_family_identity`(LAND:369-391 夜班手术二a)→`_family_identity_fn`(LAND:394-398 文件路由)。死因袋=.runtime/commit_queue/dead/ 65 笔（同侧键重复 29 + 身份判不了 36，2026-09-22~25）。边界：不含 enqueue 装袋/门禁链/CAS（QCure 已挖外层，见 landing_materialize 与 cas_converge 工作簿）；本包只挖合并器内核与身份键语义。

## 2 六向台账
### ①上游输入
- 三侧文本：ours=old_dev、theirs=袋内快照 blob、base=base_head/袋内 base_blob（`three_way_merge_registry_yaml` LAND:659-722；`_merge_registry_file` LAND:1456+）。快照 blob 由 enqueue 侧冻结，死信袋 7 笔 theirs blob 已被清理（BLOB_MISSING 实测）——上游输入有损。
- 作用域=docs/01_policies_and_standards/_registry/catalogs/*.yaml（`is_registry_mergeable` LAND:222-226），git ls-files 实测 71 个 yaml。
### ②下游消费
- 合并产物→_apply_snapshot 写盘(LAND:1549-1559)→prestage→gateway；冲突→RuntimeError→dead/ 死信（reason 原样入库，含双侧 800 字符 dump `_MERGE_CONFLICT_DUMP_CHARS` LAND:218）。消费方之二=渲染自检（重切分必须用同一 identity_fn，LAND:720）。
### ③机制现状
- 身份键现行=「每条首个标量字段 + token 复合」三段拼装，**完全不理会册文件自带的 `unique_key:` 声明**（实测 36/71 册自声明了 unique_key，含 dict 形态按族分键的 data_asset_registry——合并器零读取，已查无任何消费代码）。
- 同侧判重策略=硬死信（`_index_family_blocks` LAND:480-481 见键重复即整体放弃整文件合并）；歧义（首字段非标量）同判死信（LAND:479）。
- passthrough 现行=`_scalar_family_keys`(LAND:429-440) 只救「全条目非 dict」的族（unique_key 元数据 str/list 族）；**dict 形态元数据族（`{scan_roots: [...]}`）不在内**——实测 HEAD 6 册共 14 个此类块，触一即死。
- 业界参照：git ort 三方合并只在双侧各自改同内容才冲突（https://git-scm.com/docs/git-merge ）；PostgreSQL INSERT ON CONFLICT 显式冲突目标=声明式唯一键+可编程动作（https://www.postgresql.org/docs/current/sql-insert.html ）；CRDT MV-register 并发写保双值待裁决而非弃写（Shapiro et al. 2011，https://crdt.tech/resources.html ）——三者同向：冲突面最小化+冲突显式化，恰是本内核缺的。
### ④代码面
- 死因判定：`_index_all_sides`(LAND:635-656) 三侧各跑 `_index_family_blocks`，side 前缀 ours/theirs(快照)/base 进 reason。
- 判等素材已在块上：`_RegistryEntryBlock.text`(原文字节)与 `.data`(语义对象)并存（LAND:237-245），同键判「data 相等/字节相等」零新依赖。
- 测试基座=tests/governance/test_commit_queue_landing_nightfix.py（三向合并/族键/多插顺序 L59-161）+test_commit_queue_landing.py(70 例)；跑法 `python -m pytest tests/governance/test_commit_queue_landing_nightfix.py -x`。
### ⑤运维面
- 死因字符串无结构化字段（side/key 混在散文里），classify_dead_reason 归 other（QCure 长尾已登记）；去重类死因若静默化，需新增审计计数出口（gate_execution_stats.jsonl 或 phase note）。
- daemon 吃启动纪元代码（cas_converge ④）——合并器改动须 daemon 重启生效，施工排期要含纪元换血窗口。
### ⑥失败态与数据面（实测）
- **同侧键重复 29 笔逐一回放取证**（dev 历史按 created_at 取 ours，袋 blob 取 theirs，用现行代码+现行身份键重放）：
  - 可复现 15 对：字节级相同 2｜语义相同仅字节异（YAML 重序列化）3｜**真冲突 11**（判等口径：block.text== / block.data==）。
  - 不可复现 14：theirs blob 被清 7｜ours 侧重复已被后续落地自然治愈 6｜reason 解析失败 1。
  - dev 历史窗口扫描（09-23T18:00~09-25）另捕获 3 个曾带重复的 dev 提交：3826755f(3 对 token 重复:2 DATA+1 BYTE)、42bdec7b(1 对 BYTE)、5ff195e9(9 对 capability_id:5 BYTE+4 CONFLICT)——**同侧重复在 dev 上真实存在过且被后续落地治愈**。
- **身份判不了 36 笔**：大头=历史代码纪元误杀（unique_key 元数据族在 passthrough 诞生前、module_path 单键在夜班手术二a 前——现行代码重放不复现）；**现行仍会死**的形态=「首字段非标量的 dict 块」：`{scan_roots: [src/zephyr, scripts]}`(fail_open×2)、`{tags: [...]}`(ai_autonomy×7)、`{related_arch: [TDMAP-001,...]}`(chain×2)、compliance/feature_adjudication/registry_of_logs 各 1——HEAD 实测 6 册 14 块，任一落地触册即死。panorama_exempt_list 175 块纯标量已 passthrough 安全。
- **HEAD 在册活雷（同键真冲突，触册即死）**：registry_master_index `registry_id=REG-DATAFLOW-001`×2（data_asset 与 dataflow_graph 两个不同注册表撞号）；candidate_module `id=CAND-GOVTEST-005`×2（两个不同候选撞号）；其余 4 册（functional_domain×10 族、terminology×15 族、derived_identifier、directory）为**键粒度错杀**（真键含第二字段，现单键误判重复）。
- 3 册 HEAD 上块级解析直接失败（anchor/alias 跨块不可解）：risk_tier_registry（`&high_human_gate`/`*high_human_gate` 6 处）、infrastructure_registry、_index.yaml——任何落地触册必死「解析失败」。

## 3 缺陷与矿脉清单
1. **【本矿主体】身份键规范缺位**：gate 单键语义被三段热修补丁（token 复合+翻译册族键）追赶，36 册自带 unique_key 声明无人消费；functional_domain/terminology/derived_identifier 类键错杀=声明与合并键脱节的直接事故面。
2. **同侧重复一律死信无判等分层**：字节/语义相同（实测占回可复现对的 33%；token 双发窗口样本 69%）与真冲突（67%）同罪，前者可静默去重。
3. **dict 形态元数据族 passthrough 缺口**：`_scalar_family_keys` 只认非 dict，6 册 14 块活雷。
4. **anchor/alias 册不可合并**：3 册块级解析失败，无降级通道（要么整册 passthrough 留痕要么全文档解析）。
5. **撞号数据缺陷无对账器**：REG-DATAFLOW-001/CAND-GOVTEST-005 撞号在册，无工具发现「同键不同容」存量；每个触册落地项反复付死信成本。
6. theirs blob 可被清理而死信仍引用（取证不可回放，7 笔实证）——blob 生命周期与死信生命周期脱钩（QCure M5.4 长尾相关，此处补审计维度）。

## 4 治本方案草案
### 4.1 身份键规范（三层，声明优先）
- **L1 文件自声明=SSOT**：读顶层 `unique_key` 元数据族（已有 36 册），支持两种形态：`[field,...]`=全册默认键；`{family_key: [field,...]}`=按族键（data_asset 已是此形态）。合并器身份=「声明字段值 tuple 拼接」；声明缺失的族退 L2。配套：unique_key 声明本身归 generator 产出+校验（静态清单禁手工维护铁律 §9.5），新增对账断言「声明键在册内确无语义重复」。
- **L2 判别兜底**：无声明的族维持现行「首标量|token=」复合（零破坏）；9 个热册补声明——ruling_registry[ruling_id]✓已有、candidate[id]✓已有、in_process_gate[gate_id]✓已有、registry_master_index 缺（补[registry_id]）、rule_catalog 缺（补 files 族键）、fail_open 缺（补 gate_id 或整册元数据化）、battle_map_steps 需 generator 立法（step_id 单键已被 8 笔死信证伪，真键=step_id+name_en 或 generator 侧改号规则）。
- **L3 元数据 passthrough 扩面**：`_scalar_family_keys` 判据扩为「族内全块非 dict」或「族内全块为 dict 且首字段值非标量」→ 剔出合并空间保留 ours（灭 6 册 14 块活雷，零结构漂移风险——与现 drift 检查 LAND:461-467 同向保留 fail-closed）。
### 4.2 重复的语义学（回答硬问题④的判据）
- 同键同侧两条：`data 相等`（yaml.safe_load 对象判等，覆盖字节异/语义同）→ **真重复，静默去重保留第一条+审计计数**；`data 不等` → **语义冲突=仓库态缺陷，死信**，reason 升级为结构化三段（rel/side/key+双条 dump，现 dump 机制保留）并附处方「跑 registry 去重对账器，勿手拼 YAML」。
- 跨侧同键不在此列：ours/theirs 同键由既有三向规则处理（base 仲裁 LAND:519-529），语义=CRDT MV-register 的「双值并存待裁决」，静默吞任一侧才是吞条目——去重只做**侧内**、绝不跨侧，即可消除「静默吞条目」风险；渲染自检预期集=去重后恒等集（LAND:600 判等式不变，喂入集合改去重后）。
- upsert 语义不做：落地器无权择优（PG ON CONFLICT 的 DO UPDATE 需要业务规则），择优=对账器+人门位的事。
### 4.3 去重器插入点（两件套，回答硬问题④）
- **落地时侧内去重**（内联，小改）：`_index_family_blocks` 键重复分支改「判等→等则跳过带计数/异则死信」，约 +20 行；自检预期集同步。只解决「真重复白白陪死」。
- **独立对账器**（真治本，事件触发）：新增 `scripts/governance/registry_dedup_audit.py --scan/--heal-equal`：全册扫描同键分组、判等三态报告；`--heal-equal` 仅去重语义全等条目（数据面净删，Owner 门）；「同键异容」只报告不修（撞号 ID 重分配=裁定件）。触发挂 landing 死信钩（禁 cron，符合 §9.3）。落地侧去重治不了存量撞号——REG-DATAFLOW-001/CAND-GOVTEST-005 每次触册照死，必须对账器一次治愈。
### 4.4 anchor/alias 册
块级解析失败但整文档 yaml.safe_load 可解析的册 → 整册 passthrough+审计留痕（宁可不合并不可假合并）；risk_tier 的 alias 链即此通道。
### 4.5 参照锚点
git ort「双侧同改才冲突」(https://git-scm.com/docs/git-merge)；PG ON CONFLICT 声明冲突目标+显式动作 (https://www.postgresql.org/docs/current/sql-insert.html)；CRDT MV-register 冲突保双值 (https://crdt.tech/resources.html)；RFC 7386 Merge Patch 仅对象级合并不涉身份 (https://www.rfc-editor.org/rfc/rfc7386)。

## 5 自审闸三态裁定
**施工（分两批）**——批1 落地侧（4.1 L1-L3+4.2/4.3 内联去重，纯增量、fail-closed 方向不变、有 nightfix 测试基座）；批2 数据侧（对账器+2 撞号 heal 属注册表净删=Owner 门，随批1 落地后开单）。

## 6 长尾清单
- theirs blob 清理与死信引用完整性脱钩（7 笔不可回放）→ blob 退役通道须留死信期 TTL（归 M5.4）。
- battle_map_steps 真键规范=generator 侧立法（非 landing 能定）。
- 合并器复合键与 gate entry_identity_key 长期分叉（LAND:347 刻意不分叉 gate）——声明驱动后宜择机统一真源。
- created_at 与落地尝试时刻存在漂移，死信回放取证窗口不精确（本包 6 笔靠 dev 窗口扫描补证）。
- classify_dead_reason 补同键重复/身份判不了/解析失败三类标记（与 QCure observability 长尾合并执行）。
- 5ff195e9 类「dev 历史上曾存在重复后被治愈」的写入路径审计（谁写进去的：直连提交绕过队列疑似，未深挖）。
