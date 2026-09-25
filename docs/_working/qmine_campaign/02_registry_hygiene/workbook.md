---
ttl: task_bound
title: QMine M2 登记册存量数据卫生普查作业簿
session: st-qmine-20260925
---

# QMine M2 — 登记册存量数据卫生普查（workbook）

- 范围：`docs/01_policies_and_standards/_registry/catalogs/` 全部 76 个 YAML（含 architecture_issue_registry.yaml，其在 catalogs 目录内）；排除 `_archive/`、`index.md`、4 个 `.bak/.tmp` 垃圾文件。
- 方法：Python 3.12 `yaml.safe_load` 全量解析 + 各册头部 `unique_key`/`entry_schema` 注释对照；精确重复=全字段 JSON 等值；冲突=身份键同值不同内容；枚举=受控字段值 vs schema 注释清单；漂移=同义字段名变体（difflib≥0.75 + schema 归属判定）。只读调查，未改任何册、未动 git/队列。
- 日期：2026-09-25 ｜ 关联：QCure 排雷结论（capability 3 族已去重、107 沉积、9 条 decided）

## 六向台账

### ① 规则面
- 适用：RULE-REGISTRY（ROOR 发现）、RULE-SSOT（规则=YAML）、RULE-GIT-SAFE（改前 claim）、宪法 §4.1 全资产净零（修复批须净删申报）。
- gate 缺口：RULING-REFERENCE 只校验"引用有登记"，不校验 `status` 枚举值 → `decided/void` 入库零拦截。建议作为修复批的伴生 gate 增强（另行立项，本批不做）。
- 枚举"真源"实为各册头部 `entry_schema` 行内 `#` 注释，机器不可读——这是枚举违规与误报反复出现的结构性病根（详见长尾 L1）。

### ② 真源面
- 复合 unique_key 册（terminology_glossary `(category,en)`、functional_domain `(domain,subdomain)`、derived_identifier `(derived_type,derived_field)`）初判 27 组"冲突"经复合键复核**全部为普查脚本单键分组假阳，实际 0 冲突**。
- `fail_open_register`（1776 条）为生成器产出（generate_fail_open_register.py），手工卫生不适用——重跑生成器即自愈。

### ③ 代码面
- `infrastructure_registry.yaml` 含 0x08 字节（L229，`G:\backup` 被写成 `G:\x08ackup`）→ **整册 yaml.safe_load 失败**，一切 YAML 消费方静默拿不到该册。HIGH。
- CapabilityLookup 消费 `creation_tokens`/`capabilities`；本轮实测 (file|token) 精确重复=0（QCure 直连去重已验证干净）。

### ④ 流程面
- 前例：裁定#411（翻译册 6 组重复行 dedupe）、裁定#412（克隆对退役，保留被引多者）——本战役修复批沿用同款"登记裁定+同 commit 原子"路径。

### ⑤ 风险面
- 精确重复全仓=0：册内无冗余行可净删，净零申报负担≈0。
- 最大风险=architecture_issue 严重度失控（12 种写法 170 条）+ strategy `status=candidate` 139 条（生命周期语义挂错字段）+ 2 册 YAML 损坏。

### ⑥ 数据面（重点：全册普查表）

汇总：**76 册（含 2 册解析损坏）｜条目承载册≈70｜总条目≈30,047（含 fail_open 生成 1776）｜精确重复 0｜真冲突 3 组｜枚举违规 381 条｜字段漂移 4 族 486 条｜YAML 损坏 2**

有发现之册（其余 ~40 册零发现，身份键均唯一）：

| 册 | 容器/条目 | 身份键 | 精确重复 | 真冲突 | 枚举违规 | 备注 |
|---|---|---|---|---|---|---|
| architecture_issue_registry | entries 804 | issue_id | 0 | 0 | **211**（severity 越枚举 170：P1×73/P2×50/P0×18/P1中×9/P3×7/P0高×4/P0紧急×3/P1严重×2/medium/P2低/P0阻断/P4低各1；status 越枚举 15：implemented×6/fixed×5/adjudicated×2/overruled_by_user/confirmed；status 缺失 26）| 合法基线=severity P0致命/P1高/P2中/P3低；status open/decided/proposed/deprecated/superseded+遗留 resolved/in_progress。漂移 adjudication(796)~final_adjudication(19) |
| ruling_registry | entries 231 | ruling_id | 0 | 0 | **11**（decided×9=裁定#403/404/405/406/407/409/411/412/413，L5497-5705 区；void×2=#265/#408 墓碑）| 线索"9 条 #405-411 区"修正为：9 条 decided 实际跨 #403-#413；另发现 2 条 void 墓碑（枚举四值 active/superseded/deprecated/draft 均不含）。category 自由化（治理/数据治理等 ~20 种 vs 注释 4 值）=schema 注释过期，非数据错 |
| strategy_registry | strategies 161 | strategy_id | 0 | 0 | **139**（status=candidate；schema status=active/deprecated/retired，candidate 属 lifecycle_status 枚举）| 生命周期语义挂错字段，方向需 Owner 定 |
| candidate_module_registry | entries 623 | id | 0 | **1**（CAND-GOVTEST-005 ×2：promoted 版 2026-08-20 与 candidate 版 2026-09-02，ID 复用）| 9（priority=P3，schema=P0/P1/P2）| 漂移 created(457) vs schema created_at(116)——多数派偏离 schema |
| capability_canonical_file_registry | capabilities 388 + creation_tokens 10999 | capability_id / (file,token) | 0 | 0 | 0 | **(file|token) 精确重复=0（QCure 3 族已清，验证通过）**；107 文件多 token（共 217 token，token 均互异=合法多能力沉积，无冗余）；6 个 alias token 跨条目碰撞（CAND-SIG-012×3、ARCH-053、ARCH-056、non_gw_commit_detector、ARCH-TOOL-HEALTH-V1-Phase-4、ARCH-CONSUMERS-ACCURACY-002）；103 capability 无 canonical 字段=v1.1.0 运行时派生设计内；apply_depgraph.py 单文件挂 21 capability |
| module_translation_registry | entries 7800 | module_path | 0 | **2**（ledger_identity.py ×2、ledger_schema.py ×2，同模块两版翻译并存）| 0 | 漂移 domain(7) vs domain_id(7791)，7 条均为 schemas/categories/market/ 旧条目 |
| risk_limit_registry | risk_limits 117 | risk_limit_id | 0 | 0 | 3（status=promoted，枚举无此值）| 漂移 limit_id(3) vs risk_limit_id(117)；algorithm_status pending_definition=合法（共享词表第 4 值） |
| alert_threshold_registry | thresholds 49 | threshold_id | 0 | 0 | 8（category=ai_intake×4、trading×4 未入 schema 枚举 11 值）| 修 schema（补 2 值）非修数据 |
| infrastructure_registry | — | — | — | — | — | **YAML 损坏：L229 0x08 字节，整册不可解析** |
| _index.yaml | — | — | — | — | — | **损坏：markdown 表格冒充 YAML**（L5 `|` 被当块标量）；与 index.md 双索引并存 |
| dataflow_graph_registry | datasets 75 + jobs 74 双容器 | dataset_id / job_id | 0 | 0 | 0 | unique_key 声明为双键 `datasets.dataset_id/jobs.job_id`，普查脚本需双容器处理（已复核无重复） |
| fail_open_register | 生成 1776（dict 桶） | file:line | — | — | — | 生成器产出，重跑自愈，不入手工卫生 |
| panorama_exempt_list | 175 | module_id 标量清单 | 0 | 0 | 0 | — |
| algorithm_status 系 15 册（chart 287/factor 175/field_dict 262/tech 143/seat 16/macro 16/event 14/regime 13/portfolio 11/model 8/exp 11/bench 9/cost 6/exec 7/univ 7）| 合计 ~950 | 各自 id | 0 | 0 | 0 | 普查器首报 ~960"违规"全部为注释粘连格式假阳（`quantized已量化/pending_backtest待回测`），人工比对共享词表后**全部合法** |

## 缺陷清单

| # | 缺陷 | 量 | 级 | 修复路径 |
|---|---|---|---|---|
| D1 | infrastructure_registry.yaml 0x08 字节，整册不可解析 | 1 字节 | HIGH | 纯机械直连批（单字节替换 b→backup 的 b），改前 claim |
| D2 | _index.yaml markdown 冒充 YAML | 1 册 | MED | 人工定性：改名 .md 或转 YAML（涉重命名→RENAME-DEPGRAPH-SYNC 义务） |
| D3 | architecture_issue severity 越枚举 | 170 | MED | 精确映射 141 条纯机械（P0→P0致命/P1→P1高/P2→P2中/P3→P3低）；变体 29 条需映射表裁定 |
| D4 | architecture_issue status 越枚举 15 + 缺失 26 | 41 | MED | 裁定后机械补值（implemented/fixed→resolved 或新增枚举） |
| D5 | strategy status=candidate 挂错字段 | 139 | MED | Owner 定向：迁 lifecycle_status 还是扩 status 枚举 |
| D6 | ruling decided×9 + void×2 越枚举 | 11 | MED | 立法路径：扩枚举（decided/void）或迁移（decided→active）；墓碑语义建议立法保留 void |
| D7 | candidate CAND-GOVTEST-005 ID 复用 | 1 组 | MED | 人工：后登记者重编号（裁定#412 先例：保留先占，改新条目 ID） |
| D8 | module_translation 同路径双翻译 | 2 组 | LOW | 人工择优合并（裁定#411 先例） |
| D9 | candidate priority=P3 越枚举 | 9 | LOW | 裁定扩枚举或降级 P2 |
| D10 | alert_threshold category 新值未入枚举 | 8 | LOW | 修 schema 注释（补 ai_intake/trading） |
| D11 | 字段漂移：created→created_at 457 / domain→domain_id 7 / limit_id→risk_limit_id 3 / adjudication→final_adjudication 19 | 486 | LOW | 字段改名纯机械（归一到 schema 名） |
| D12 | alias token 跨条目碰撞 6 个 | 6 | LOW | 人工消解：改名或合并 capability |
| D13 | catalogs 目录 .bak/.tmp 垃圾 4 件 | 4 | LOW | 清理（项目卫生同类） |

## 卫生方案草案（自动修复器设计）

**能机械修（修前逐条 diff 预览、修后进程外复核，宪法 §1.13）**：D1（1 字节）、D3 前半（141 条精确映射）、D11（486 条字段归一）≈ **608 处纯机械**。
**一条裁定即可批量机械**：D3 后半 29 + D4 41 + D5 139 + D6 11 + D9 9 + D10 8 ≈ **237 处**。合计 **≈845 处可机械修复**。
**必须人工**：D2 定性、D7 重编号、D8 择优、D12 消解、107 沉积抽检（非修复）、21-capability 拆分评估。

落地批设计：
1. **批 0（直连优先批）**：D1 单字节——HIGH 且零语义风险，直连 GitCommitGateway：改前 `lock_files.py acquire docs/.../infrastructure_registry.yaml st-qmine-20260925` → `git_commit.py --session st-qmine-20260925 --files <该册>`。锁忙则 `--enqueue` 入队，不空转。
2. **批 1..N（每册一批，禁跨册混批）**：D3/D4/D11 按"一册一 commit"，`--files` 清单精确到册；commit message 携带净删申报：`[NET-DEL] 新增 0 规则/0 gate/0 册；字段归一迁移 N 条（旧写法并入 schema 名）；枚举迁移 M 条（变体并入 schema 枚举，映射表见裁定#NNN）`——满足宪法 §4.1 替代声明要求。
3. **裁定前置**：D3 映射表/D5 方向/D6 立法各登记一条裁定（RULE-RULING：先 ruling_registry 同 commit 原子），再跑批。
4. **安全网**：修复器只写 `safe_write_text`（CAS）；每批后 `git log -1 --name-only` 核实归属；修前快照各册至 `.runtime/sessions/<sid>/staging/` 便于回滚。
5. **gate 伴生建议（不在本批）**：RULING-REFERENCE 增加枚举校验；schema 枚举机器化（entry_schema 注释→结构化 enum 块）立项。

## 自审闸三态

- **通过（双脚本/人工复核可证）**：精确重复全仓=0；capability (file|token) 精确重复=0（QCure 结论复验一致）；107 多 token 文件=合法沉积（217 token 均互异非空，无一同 token 冗余）；复合键 27 组假阳已人工复核排除；ruling 越枚举 11 条（含对线索 #405-411 区间的修正：实际 #403-#413）。
- **存疑（方向待 Owner）**：D5 strategy 139 条修复方向；D6 decided/void 立法 vs 迁移；D3 变体 29 条映射逐条人判；D10 属"修 schema 不修数据"的定性。
- **不通过/未覆盖**：schema 枚举为自由注释，假阳/假阴不可能 100% 消灭（已对 ~960 条 algorithm_status 假阳逐册人工排除，但无机器保证）；fail_open_register 等 4 册 dict/生成器结构未逐条普查；`_archive/` 与 data/capability_cards/ 未在本次范围。

## 长尾

- L1（病根级）：entry_schema 枚举机器化——注释枚举是全部枚举违规/误报的共同上游。
- L2：apply_depgraph.py 单文件挂 21 capability，是 token 碰撞与查找歧义的放大器。
- L3：rule_ai_perception_index 86 条三字段（module_id/rule_id/rule_file）无 entry_schema 声明。
- L4：_index.yaml 与 index.md 双索引并存（且前者损坏）。
- L5：catalogs 目录 82 项 vs 76 册——数量表述以字段计数为准，勿写死（宪法 §4.3）。
- L6：architecture_issue 26 条 status 整字段缺失，提示历史批次写入未过 schema 校验。
