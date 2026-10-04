---
ttl: task_bound
session: st-f5-mountdata-20261003
date: 2026-10-03
title: F5 四字段数据装配终报（四件 YAML 产出 + T1-T5 机械对账）
completes_when: 总筹升级生成器消费本批四件并随上户口批落地后转归档
---

# F5 四字段数据装配终报

> 车道：机械数据装配（格式转换+机械对账，零判定）· sid=st-f5-mountdata-20261003 · 2026-10-03。
> 冷启动：Python 3.12.8 ✓ / `setup_dev_env.py --check` ✓（usercustomize 在岗）/ `lock_files.py cleanup` CLEAN / reaper 存活（last_run=2026-10-03 21:57:33，写操作前提满足）。
> 红线执行：六源输入全部纯读零改写；零 `git commit` 零 `git add`（落地归总筹）；五件产出写前逐件 `lock_files.py acquire` 全成功；只新建文件、零既有文件改写。

## §1 产出清单（docs/_working/commitmap_cure/，YAML，UTF-8 无 BOM）

| 文件 | 内容 | 行数 |
|------|------|------|
| f5_purpose_tags.yaml | labels 节 12 条（第 1-11 条逐字抄 00_design_basis.md §1 冻结表；第 12 条摘 01_review_adjudications.md §1#2 批准原文）+ gates 节 182 台 {label_name, node_id, source_row} | 788 |
| f5_casebooks_mount.yaml | nodes 节 28 环节 → casebooks（逐字取 F4 §1 矩阵，raw=原胞 + 按「；」切分指针列表）+ unmounted_note 节 G01/G02 显式不挂注记 | 184 |
| f5_trigger_facts.yaml | 182 台 {trigger_count, zero_trigger_candidate, evidence}；trigger_count=「近30天触发」列（F3 README 明文主指标）；零触发布尔以 f3_zero_trigger_candidates.csv 为准 | 739 |
| f5_consumers_agg.yaml | 182 台 {consumer_count, top_consumers(≤5), detail_source}；计数取明细行数（与主表消费者数列逐台相等）；top5=明细文件序前 5（production 恒在前，文件序即生产优先）；INV-1 只存指针 | 1621 |
| f5_report.md | 本终报 | — |

四件 YAML 回读校验全过（yaml.safe_load 零错、无 BOM、写后进程外核实）。

## §2 T1-T5 机械对账

### T1 三张 gate 键表两两相等 —— ✅ 平

| 键表 | 集合 |
|------|------|
| 产出 1 gates 节（源=A 类型=gate 行） | 182 |
| 产出 3 facts 节（源=f3_trigger_evidence.csv） | 182 |
| 产出 4 aggregates 节（源=f3_consumer_detail.csv） | 182 |

两两相等 ✅（写前对输入集、写后对产出 YAML 回读各验一遍，均平）。A 门禁集与 B 主表集合亦逐台相等。

### T2 产出集 vs E 两册并集 —— 幽灵 0 / 孤儿 3

E 两册今日字段实值（勿背数，读 total_gates）：in_process_gate_registry.yaml=**105**、gate_registry.yaml=**182**；并集 **185**、两册交集 **102**。

- 幽灵（产出集有、E∪ 无）：**0 台** ✅
- 孤儿（E∪ 有、产出集无）：**3 台**，均 in_process 册独有：`CONSTITUTION-LINE-LIMIT` / `REAL-KEY-REFERENCE-SCAN` / `TASK-ORDER-DOCS-LOCK`
- 附机械事实：F3 主表 182 台与 shell 册 182 台**逐台相等**（B==shell 集合全等）；in_process 册 105 台中 102 台与 shell 重叠。

### T3 A 行数与 E 计数口径差异（只引原句，勿自算新口径）

机械实数对照：A=**204 数据行**（182 gate + registry 10 + daemon 6 + script 6）；E raw 条目 105+182=287、去重并集 185；F3 主表=182。口径真源原句：

> 02_audit_workpaper.md L9：「输入：F2 标签 204 机制（含活性8套/手续5道/守护5件）、F3 触发证据 182 台、F4 病历挂载 28 环节。」

> 02_audit_workpaper.md L30-31：「列语义待核：主表“近30天触发”列与 README Top5（TRANSLATION-COVERAGE 2.2万）口径差一个数量级——疑为拦截数 vs 执行数两列，对审第 0 步先统一口径（F3 README 已有逐列定义，按它对齐）。」

> 00_design_basis.md §1 使用规则：「每个图11 机制节点恰好一个主标签；多义模块按挂点拆（一岗多流程=多挂点，见 §4）。」

> 00_skeleton.md D11-C05 行：「≈99（gate 数勿背，读 total_gates 字段）」——骨架所记 99 为估数，本车道以今日字段实值 105/182 为准。

差值归口径：A 比 F3 多 22=非门禁机制 22 台（活性8+手续5+工具4+守护5，02 底稿 L9 原句口径）；E∪ 比 F3 多 3=T2 孤儿三台；E raw 和 287≠并集 185=两册重叠 102 所致。本产出按任务书取「每台门禁」=182 台，非门禁 22 台未入 gates 节（是否入图=总筹判定面）。

### T4 F4 §1 矩阵完备性复算 —— ✅ 平（28 行、五本各 ≥1）

- §1 矩阵 **28 行** ✅；28 个环节 id 与 00_skeleton.md §1 的 28 id 集合**双向零差** ✅；A 的 D11环节 列取值 ⊆ 骨架 28 id ✅。
- 五本覆盖复算（口径=「册码#」在矩阵原胞中出现即计，含「+」连接的复合单元）：

| 病历本 | 覆盖环节数（本测 §1） | F4 §4 自报 |
|--------|------|------|
| AP 堵点本 | 19 | 14 |
| DCS 死因案例册 | 14 | 13 |
| MEM 记忆教训索引 | 28 | 30 |
| RV1 审查卷一 | 8 | （两卷）14 |
| RV2 审查卷二 | 6 | （两卷）14 |
| SV 抢救台账 | 8 | 9 |
| RV1∪RV2 两卷并集 | 11 | 14 |

全部 ≥1 ✅ **T4 完备性通过**。本测数与 F4 §4 自报数的差异列入 §3 异常清单（§1=任务书指定唯一真源，本产出按 §1 逐字；差异只列不平，禁修源）。

### T5 12 条标签 —— ✅ 平

无重名 ✅；每条带一句话 ✅；gates 节所用标签 ∈ labels 节 ✅（11/12 条被 182 台门禁引用：⑧63/⑨40/④34/⑤14/⑦9/②6/③6/⑩3/①3/⑪2/⑥2，与 02 底稿 §1 交叉表合计列逐格一致）。第 12 条「别把钥匙留在门口」0 台挂载=预期态（见 §3-6）。

## §3 异常与观察清单（只列不平，禁自行修源）

1. **T2 孤儿 3 台**：CONSTITUTION-LINE-LIMIT / REAL-KEY-REFERENCE-SCAN / TASK-ORDER-DOCS-LOCK 在 in_process 册而 F3 主表未收。对照 02 底稿 L41「注册册割裂实证（两册零交集+四台高频门双册无登记）」——本测两册 id 交集=102，与该句表述口径未对齐，原文引录存档，不裁定。
2. **F4 §4 自报覆盖数与 §1 矩阵复算不平**（T4 表）：DCS 13vs14 / AP 14vs19 / SV 9vs8 / 两卷 14vs11 / MEM 30vs28。§1 为任务书指定 casebooks 唯一真源，产出按 §1；§0/§2/§4 与 §1 的内部差异归 F4 车道与总筹复核。
3. **A 非门禁机制 22 台**（registry 10 / daemon 6 / script 6）不在产出 1 gates 节（任务书 gates 节=每台门禁）；四件产出的 gate 键表故为 182。22 台机制是否进图=总筹判定面。
4. **trigger_count 映射口径**：F3 README「触发口径」节明文主指标=「近30天触发」（五项结构化证据之和）；02 底稿 L30 对该列有「拦截数 vs 执行数数量级差」疑云并已裁定「按 F3 README 对齐」。本产出按 README 主指标列直抄，映射已写入 YAML source_map 供总筹换列重算。
5. **零触发候选 10 台**已按名单打 zero_trigger_candidate=true；其中含 02 底稿已注记的灰区台（GATE-ARCH 合并门内层预期静默 / ISSUE-RESOLVED-INTEGRITY 已 deprecated / COMMIT-CRITICAL-SECTION-LOCK 裁定「健康静默不入退役名单」）——布尔为名单机械直抄，处置判定权在总筹。
6. **第 12 标签 0 台挂载**：符合 01_review_adjudications.md §1#2「≈10+ 台可机械圈出改挂」的改挂未执行态，属总筹后续判定面，非本车道缺漏。
7. **门禁拦截/异常**：全程零门拦截零异常。CREATE-GUARD token 未落册（F1-F4 同模式）：五件 slug 已备好纯 ASCII 名 `commitmap_cure_f5_purpose_tags` / `commitmap_cure_f5_casebooks_mount` / `commitmap_cure_f5_trigger_facts` / `commitmap_cure_f5_consumers_agg` / `commitmap_cure_f5_report`，随 chief 落地批同批原子登记。
8. 过程小事故（零损失）：一次 heredoc 落脚本因终止符未被 Git Bash 识别而空跑（已知学费项），改用 Write 工具落脚本后一次通过；临时脚本按红线走 `.runtime/tmp/f5_mountdata_20261003/`（24h TTL 自清）。
9. **盘面异常（外部行为，非本车道）**：写后 `git status` 实测四件 YAML 态=`A `（已进暂存区）、f5_report.md=`??`（未跟踪）。本车道全程零 `git add` 零 `git commit`（铁律 1），暂存入区系外部自动保护机制或他会话 watcher（"写即add"防蒸发配方的既有盘面行为）。另 `f3_trigger_evidence_readme.md` 显示 `MM`，本车道对其纯读零写，该态为他会话在途改动。两项均如实呈报，未对抗未清理。

## §4 交接注记（chief 消费点）

- 四件 YAML 结构：顶层 `source_map` 节记录逐字段映射规则（含行号约定：source_row=f2_label_candidates.csv 文件行号，表头=1）；生成器可直接消费。
- 降级直改登记原因：机械装配新产出文件、无既有文件改写、随 chief 批落地（F1-F4 同模式）。
- claim 状态：五件已 acquire（sid=st-f5-mountdata-20261003，TTL 30 分钟自过期）；本车道零 commit 零 add；四件 YAML 被「写即add」外部保护自动入暂存区（见 §3-9），落地归总筹。

[no-lookup: 纯数据装配无新业务代码，任务书已含全部真源指针]

本车道未做任何判定，全部判定权归总筹。
