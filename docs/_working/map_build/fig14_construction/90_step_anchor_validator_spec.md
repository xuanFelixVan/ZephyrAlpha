---
ttl: task_bound
completes_when: validate_construction_steps.py + generate_construction_steps.py + construction_steps_gate 子台 + config/construction_workflow_map.yaml 四件同批落地并跑红绿两轮后，本件退役为图14 施工档案
title: 图14 步骤锚校验器·施工规格（90_step_anchor_validator_spec，块B）
owner: st-mapbuild-20260924
---

# 90 步骤锚校验器施工规格（块B）

> **为什么必须先有它**：本图域的四道门第④门当前**不过**（实证见 `00_skeleton.md` §0 门④）——17 个施工环节里只有 6 个有可跑机验锚，政策明文给出的锚里有 **9 条"文档说有实则没有"**（R-01~R-09）。普查判定原文="每步 gate 命令已是脚本，但 SOP verifiability=manual → 先立步骤锚校验器再机生成图"（`docs/_working/map_census/00_panorama_map_census_v1.md:58`）。**校验器是这张图从"不可建"变"可建"的唯一路径**，不是图的附属品。
> **写给谁**：波3 施工会话，照本规格逐节做即可落地；本件不含实现代码，只含契约。
> **形态母版**：图 9 四件套（`config/strategy_production_map.yaml` + `validate_strategy_production_map.py` + `strategy_factory_map_gate.py` + `test_strategy_factory_map_gate.py`），全部坐标实测在盘。

## §1 校验对象与真源（先做净零调研，再谈挂哪）

**硬约束**：优先扩既有面，不造新册（AGENTS §4.1 全资产净零 / §4.2 内收判据"同真源可派生→必并"；宪章 §8.2.4 机生优先）。以下五个候选面全部实测过，逐个给取舍结论：

| 候选 | 实测证据 | 判定 |
|---|---|---|
| **A. battle_map 的 `step_id` 轴**（PG 三表 battle_map_steps/anchors/edges） | `scripts/governance/apply_battle_map.py:172-356` 环节 CRUD 实存；但值域宿主 `battle_map_domain_policy.yaml:45-` 的 `flow_stage_allowed_domains` 键全是**交易阶段**（stock_selection/buy_flow/position_management/plan…），BM-INV-004 按该闭集判域漂移、BM-INV-007 要求业务域必须有作战锚点 | **拒**：施工步骤挂进去必被 BM-INV-004 判红或逼"新增施工 flow_stage"，即污染交易作战图语义（跨域不同对象→不并）。**但借其结构**：step_id + anchors + edges 三件套是本项目已有的"步骤轴"范式，本图沿用它（只是轴前缀换 `D14-*`） |
| **B. `in_process_gate_registry.yaml`** | `:41 total_gates: 99`；条目 schema=`gate_id/module_path/factory_function/source/enabled`（:34-39），无 step 概念；`MAP-ALIGNMENT` 条目在 `:301-307` 带 files_trigger | **只做交叉校验目标**（CV-06 用它判"引用的 gate 是否在册"），不当步骤宿主——宿主错了会让 gate 册承担双语义，违背"文件名即责任" |
| **C. `rule_catalog_registry.yaml`** | 本 policy 在 `:2007-2021` 只有一行**文档级**条目，且 `section_count: 0`；条目字段无步骤粒度 | **拒作宿主 / 用作被更新方**：粒度差两个数量级；施工期由总包把 `section_count` 由生成器填（骨架收口 §X-2） |
| **D. 新建 `step_anchor_registry.yaml` 挂 ROOR** | 75 个 catalogs 实测无任何步骤册（`ls docs/01_policies_and_standards/_registry/catalogs/`；`grep -l step_id` 命中五册均非施工宿主） | **备选**（§11 净零声明里说明代价：+1 册 +1 ROOR 行 +1 双真源风险）。仅当方案 E 被 Owner 否定时启用 |
| **E. 政策 MD 自身的结构化段（选定）** | 政策 17/17 个 Step 段已具备统一 7 字段（实测 `**何时触发**/**前置条件**/**操作摘要**/**引用真源**/**通过判据**/**不通过处置**/**产出物**` 覆盖率 100%；9/17 段有 ```` ```powershell ```` 命令块）；政策 L77-79 自述定位="只编排：步骤序列+触发条件+执行命令+通过判据+失败处置""**每一步指向真源规则文件路径**" | **选 E**：真源**仍是政策 MD 一份文件**（零新册，净零成立）；锚块内嵌在段尾，抽取即得图；图=派生件（宪章 §8.2.4）；与政策"编排层不重复规则内容"的定位同构 |

**选定方案的净零论证**：不新增注册表、不新增 gate 台（进聚合 `subs`）、不新增枚举词表（`verifiable` 复用 `verifiability_vocabulary.yaml:30-36` 三值，`build_status` 复用图 9 的 `built/partial/pending` 三值，实测 `validate_strategy_production_map.py:42`）。新增的只有 3 个代码件（校验器/生成器/gate 子台）+ 1 个图 YAML，**声明替代**：① 替代政策 §4 手工 Checklist 的"13 项/16 行"散文计数（R-12）→ 改由 `counts:` 字段生成；② 替代附录 A.13 与 §2.3 矩阵的手工维护（CV-11 机器比对）；③ 替代 alignment_checklist §3 里"施工 SOP 有没有对齐面"这一空缺。

## §2 步骤锚块规范（写进政策 MD 每个 Step 段末尾）

### 2.1 锚块定界与位置

* 位置：紧跟在每个 `### Step …` 段的**最后一行**之后、`---` 分隔线之前。
* 定界（HTML 注释，避免与 DCR/FK 扫描器对 `#` 行首的误判；共识件 §2 明令"行首 `#` 不要写成 `[DOMAIN]` 形态注释"）：

```
<!-- D14-STEP-ANCHOR-BEGIN -->
（一段 yaml）
<!-- D14-STEP-ANCHOR-END -->
```

* 一个 Step 段**恰好一个**锚块；无锚块=CV-04 判红（政策未改完前允许 `--allow-missing-anchor <step_id>` 降级为 warn，名单必须显式写在图 YAML 的 `pending_anchors:` 里，防"忘了就绿"）。
* 锚块**不复制政策散文**（INV-1，见 CV-12）：只允许出现 id / 路径 / gate_id / 枚举 / ≤120 字的一句话摘要。

### 2.2 字段集（必填 ✔ / 选填 ○）

| 字段 | 必填 | 语义与判定 |
|---|---|---|
| `step_id` ✔ | 格式 `D14-\d{2}`，全图唯一，与骨架 §1 表逐一对应（骨架=契约，改号须总包回写） |
| `policy_step` ✔ | 政策原文 Step 名（如 `"Step 3.5"`），用于 CV-04 与 `^### Step` 集合闭合 |
| `policy_anchor` ✔ | 符号锚，格式 `<相对路径>#<标题 slug>`；**禁行号锚**（出现 `L\d+` 形态=CV-07 error；依据 R-13：政策 7 处行号锚实测 7/7 全偏） |
| `segment` ✔ | 枚举：`前置\|判定\|设计登记\|施工\|验收\|文档转正\|落地收尾`（骨架 §2.1 五段口径的细分，值集在图 YAML `layers:` 声明） |
| `role` ✔ | 枚举 `internal\|handoff`。`handoff`=机制真源属图11，只许引用（骨架门③硬边界 1） |
| `handoff_to` ○(role=handoff 时✔) | 值形如 `D11-S02`/`D11-C05`，正则 `D11-[SCD]\d{2}` |
| `order` ✔ | 整数，全图唯一；主序边方向由 order 定（CV-10 用） |
| `conditional` ✔ | bool。政策 L196/L333 类"仅新建模块/仅前端触发"→ true，并填 `trigger_when` 一句话 |
| `executable` ✔(role=internal) | 可执行真相源路径清单（.py），CV-05 判磁盘实存 + "可执行"的机械定义 |
| `gates` ○ | in-process/pre-commit gate_id 清单，CV-06 判在册 |
| `docs` ○ | `{path, symbol}` 清单，CV-07 判路径实存 + symbol 可 grep 命中 |
| `verifiable` ✔ | 枚举 `automated\|inspection\|manual`，**动态加载** `_registry/vocabularies/verifiability_vocabulary.yaml`（禁硬编码字典，AGENTS §9.9） |
| `build_status` ✔ | 枚举 `built\|partial\|pending`（与图 9 同值集） |
| `produces` ✔ | ≤120 字，一句话产出物 |
| `rollback_to` ✔(可空数组) | 政策原文回边目标 step_id 清单（骨架 §2.2 B1~B15 逐条翻译） |
| `max_rounds_ref` ○ | 仅自环环节用，指向常量（例：Step 5 → `zephyr.governance.persistence.task_repo:CIRCULAR_ACCEPTANCE_ROUNDS`，实测 `task_repo.py:667`） |
| `evidence` ✔(build_status=built 时✔) | 实查证据行（日期 + 命令 + 观察值），把骨架 §5 状态纪律"✅ 必附实查"变成机读面 |
| `red_findings` ○ | 本环节红条目号（R-01…R-16），供施工期跟踪闭环 |

### 2.3 两个样板（一条 internal+automated，一条 handoff）

```yaml
# D14-STEP-ANCHOR-BEGIN
step_id: D14-07
policy_step: "Step 3"
policy_anchor: "docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-3-全图全库对齐"
segment: 设计登记
role: internal
order: 7
conditional: false
executable:
  - scripts/governance/sync_panorama_module.py
  - scripts/governance/d5_architecture/generators/align_all.py
gates:
  - MAP-ALIGNMENT
docs:
  - {path: docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml, symbol: panorama_alignment}
  - {path: docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md, symbol: 第一层：全景图对齐}
verifiable: automated
build_status: built
produces: 全图全库对齐通过报告
rollback_to: [D14-06]
evidence:
  - "2026-09-24 sync_panorama_module.py --all 与 align_all.py 实测在盘；MAP-ALIGNMENT 在 in_process_gate_registry.yaml:301 在册"
# D14-STEP-ANCHOR-END
```

```yaml
# D14-STEP-ANCHOR-BEGIN
step_id: D14-15
policy_step: "Step 10"
policy_anchor: "docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-10-gitcommitgateway-落地"
segment: 落地收尾
role: handoff
handoff_to: [D11-C01, D11-C03, D11-C04, D11-C05, D11-C06, D11-C07, D11-C08, D11-C13]
order: 15
conditional: false
executable: []
gates: []
docs:
  - {path: docs/01_policies_and_standards/rules/trae_075_stash_lifecycle.yaml, symbol: }
verifiable: automated
build_status: built
produces: commit hash
rollback_to: [D14-11]
red_findings: [R-03, R-06, R-12, R-14]
evidence:
  - "2026-09-24 机制真源归图11（fig11_delivery/00_skeleton.md 门③E1=政策 L99 自标不重复引用）；本政策给出的 scripts/git_commit_gateway.py 实测不存在"
# D14-STEP-ANCHOR-END
```

> 注意 handoff 样板 `executable/gates` 恒空——机制锚由图11 持有，本图重复登记即造第二真源（CV-14 机验）。

## §3 图 YAML schema（`config/construction_workflow_map.yaml`，生成器产物）

顶层键（REQUIRED_TOP，CV-01）：`schema_version, map_id, name_zh, layers, nodes, edges, feedback_loops, laws, boundary, counts`
（与图 9 `validate_strategy_production_map.py:36-37` 差异：`products` → 本图无"产品清单"语义，代之以 `counts`；`layers`=§2.1 七段；`laws` 必填见 CV-15）

```
schema_version: '0.1'
map_id: construction_workflow_map
name_zh: AI 施工升级流图
generated_by: scripts/governance/d5_architecture/generators/generate_construction_steps.py
derived_from: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md   # 单向派生，禁手编
laws:                       # 全图铁律（CV-15 非空）
  - 图只存 step_id 与引用，禁复制政策正文（INV-1；政策 L77-79 编排层定位的图侧同构）
  - 每个环节必须有可执行真相源或已登记 gate 作锚，否则判 verifiable=manual 并计入红账
  - 落地收尾机制属交付流水线（图11），本图只挂 handoff 引用，禁重复登记
boundary:                   # 逐字引用，不得意译（CV-15 校验引用串在源文件中可命中）
  - "GOMAP out_of_scope：提交门禁体系——门禁是每模块配套,非运行时流水线节点（config/governance_operations_map.yaml）"
  - "不含数据运维流（政策 §5.2 + data_ops_policy 另必读）"
  - "轴区分：本图 step_id=D14-* ；作战地图 step_id=BM-*（交易 flow_stage，域闭集）"
layers: [前置, 判定, 设计登记, 施工, 验收, 文档转正, 落地收尾]
nodes: [...]                # 生成器从锚块抽，17 条
edges:                      # 主序边（order 递增）
  - [D14-01, D14-02]
  - ...
feedback_loops:             # 全部回边在此显式声明（CV-10），逐条对应骨架 §2.2 B1~B15
  - {from: D14-09, to: D14-02, note: "B8 算法缺失回补文档"}
  - {from: D14-11, to: D14-09, note: "B10 FAIL 回施工"}
  - {from: D14-12, to: D14-09, note: "B11 文档代码漂移回施工"}
  - {from: D14-13, to: D14-12, note: "B12 对齐失败回文档"}
  - {from: D14-15, to: D14-11, note: "B13 网关拒绝回长清单审查"}
  - {from: D14-07, to: D14-06, note: "B5 domain 不一致回登记"}
pending_anchors: []         # 未补锚环节的显式白名单（非空即 warn 计数，禁静默）
counts:
  total_steps: 17           # 必须 == len(nodes)（CV-13）
  automated: 6              # 由 nodes 现算
  inspection: 6
  manual: 5
```

**禁手编声明**：`nodes:` 由生成器覆盖写；人工改图=下次生成即被冲（同 `alignment_checklist.md:88` GOMAP 的"骨架机生，禁手工编辑"口径）。人只改政策 MD 的锚块。

## §4 校验项逐条（CV-01…CV-16，照图 9 十项风格）

实现约束：校验逻辑唯一真源 = 新校验器模块的 `validate_structure(data) -> list[str]` + `check_anchors(policy_text, data) -> tuple[list[str], list[str]]`（两个入参故两函数；gate 与 align_all 与 CLI **三方同源动态 import，禁复制**，先例=`strategy_factory_map_gate.py:129`、`decision_map_gate.py` 头 DEPENDENCIES）。

| # | 校验项 | 级别 | 判定式（可直译成代码） | 本仓实测会命中它的样本 |
|---|---|---|---|---|
| CV-01 | 顶层必填键齐全 | error | 遍历 REQUIRED_TOP，缺键即 error 并提前返回（照 `validate_strategy_production_map.py:55-58`） | — |
| CV-02 | 节点必填字段齐全且非空 | error | 对 `nodes[]` 逐字段 `if f not in n or n[f] in (None,"")` | — |
| CV-03 | step_id 唯一 + 前缀合法 | error | `re.fullmatch(r"D14-\d{2}")`；`len(ids)!=len(set(ids))` | — |
| CV-04 | 环节覆盖率 100%（政策↔图双向闭合，**无孤儿节点/无未图化环节**） | error | 解析政策 `^### Step` 得集合 P（带锚块的），图 nodes 得集合 G，`P != G` 即 error 并列出差集 | 当前政策无锚块 ⇒ 全 17 条欠账（正是校验器要逼出来的活）；`policy_step` 缺 Step 3.5 之类漏项直接现形 |
| CV-05 | 可执行锚磁盘实存且"可执行" | error | `Path(p).exists()` + `p.endswith('.py')` + 文件内含 `argparse\|add_parser\|def main` 之一 | R-01（ide_health_service.py 不存在）、R-03（两个路径错）、R-06（CLI 子命令不存在 ⇒ 需把 executable 指到函数所在文件并加 `symbol:`，否则判 error） |
| CV-06 | gate 锚已在 gate 册登记 | error | gate_id ∈ {in_process_gate_registry.yaml ∪ gate_registry.yaml 的 `- gate_id:` 值集}；近似名（编辑距离≤2）命中他名 ⇒ warn 点名"实名是 X" | R-14（SECRET-HARDCODE→NO-SECRET-HARDCODE）、R-07 类跨册不齐 |
| CV-07 | 文档/规则锚路径实存 + 符号锚命中；**禁行号锚** | error | `exists(path)` + symbol 非空时 `grep` 命中；`re.search(r"\bL\d{2,}\b", policy_anchor)` ⇒ error | R-13（7 处行号锚全偏）、R-09（trae_002 §rule_eight 锚不存在）、R-11（12 处 design_memos 路径） |
| CV-08 | 真源不得是"已废弃/已归档"件却支撑 automated | error | 目标 MD 的 frontmatter `status` ∈ {deprecated} 或路径含 `_archive/`、`/archive/` ⇒ 该锚只能计 `inspection/manual`，否则 error | R-10（AI_review_instructions 已 deprecated）、R-11（design_memos 49 件归档） |
| CV-09 | 枚举合法（值集动态加载） | error | `verifiable ∈ verifiability_vocabulary.values`；`build_status ∈ {built,partial,pending}`；`segment ∈ layers`；`role ∈ {internal,handoff}`。**禁**在校验器里写死中文枚举字典（AGENTS §9.9 i18n 三层 loader） | — |
| CV-10 | 边/回边合法：自环拒绝或须带常量引用；反向边必须显式声明 | error | `a==b` ⇒ 无 `max_rounds_ref` 即 error；`order[a] > order[b]` 且 `(a,b) not in feedback_loops` ⇒ error；重复边 error；边引用不存在节点 error（照 `:110-128`） | 政策 L443 循环验收（需 max_rounds_ref）；骨架 B1~B15 全部为反向边，漏声明即红 |
| CV-11 | §2.3 关系矩阵与 Step 段一一对应 | error | 解析政策 `## 2.3` 表首列 Step 名集合，与 `^### Step` 集合比对，差集非空即 error | **当前必红一次**：矩阵缺 Step 3.5 行 + 多"Step 1 前置"行（R-15）⇒ 施工期须补矩阵行或政策加豁免注记 |
| CV-12 | INV-1 反复制（图里不得抄政策正文） | error | 节点任一字符串字段 `len>120` ⇒ error；对政策正文做 40 字滑窗，命中 ≥1 个窗口的字段 ⇒ error（豁免：`evidence[]`/`boundary[]` 逐字引用段，须在 YAML 里标 `verbatim: true`） | 图 9 的 `decision_question>120 字` 先例（`:90-91`） |
| CV-13 | 计数不落地在散文 | error | `counts.total_steps == len(nodes)`；`counts.automated+inspection+manual == len(nodes)`；图 YAML 顶层禁出现"15 步/13 项"类写死数字（正则 `(\d+)\s*步` 出现在非注释行即 error） | R-12（政策六处计数漂移 ⇒ 施工期改字段时必被此条逼一次） |
| CV-14 | handoff 边界（防本图吞图11） | error | `role=handoff` ⇒ `executable==[] and gates==[] and handoff_to != []`；`handoff_to` 每项匹配 `D11-[SCD]\d{2}` 且**在图11 骨架 §1 表内可命中**（读 `docs/_working/map_build/fig11_delivery/00_skeleton.md` 的 `D11-` 串集合）；`role=internal` ⇒ `handoff_to` 必须为空 | 骨架门③硬边界 1 的机验形态（D14-01/14/15/16/17 五节点） |
| CV-15 | laws/boundary 非空 + boundary 逐字引用可回源 | error | `if not data.get("laws")` ⇒ error（照 `:60-61`）；boundary 每条若含"（<路径>）"，须在该路径文件中命中引号内原文，未命中即 error | O3（GOMAP out_of_scope 原文，`config/governance_operations_map.yaml:17-19`） |
| CV-16 | 状态自洽（把"✅ 必附实查"钉成机验） | error | `verifiable=automated` ⇒ `executable∪gates` 至少一条通过 CV-05/06；`build_status=built` ⇒ `evidence[]` 非空且每条以 `YYYY-MM-DD` 开头 | R-05（module-id-registry.json 幽灵：Step 2 若标 automated+built 但锚判失败即红）、R-08、R-04 |

告警面（不阻断，只计数并打印）：CV-06 近似名、`pending_anchors` 非空、CV-08 归档件被引为 `inspection`、图11 骨架文件暂不可读时 CV-14 的跨图引用检查。

## §5 CLI 契约（照抄 `validate_strategy_production_map.py:170-201`）

```
python scripts/governance/d5_architecture/validators/validate_construction_steps.py \
    --steps config/construction_workflow_map.yaml \
    [--policy docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md] \
    [--anchors-only] [--skip-live] [--json]
```

* `--steps`（必填语义，默认值同 DEFAULT_MAP 常量）= 图 YAML 路径；`--policy` 默认政策现路径，允许显式指向 fixture（对抗测试用）。
* **exit 语义逐字照搬**：`0`=PASS（打印 `PASS: 步骤锚校验通过（steps=17 automated=6 …）`）；`1`=结构违规（stderr 逐条 `ERROR:` + `FAILED: N 个结构违规`）；`2`=文件不存在/YAML 解析失败/顶层非对象。
* 文件头 `[ERROR_CONTRACT]` 必须写 `SystemExit(1)=结构违规; SystemExit(2)=文件/解析失败`（15 字段头，`trae_047 §A_full`，先例见校验器 :17）。
* `--skip-live`=跳过磁盘实存类检查（CV-05/06/07/08），仅跑结构；gate 走这条（提交时不做全仓 stat，同 FACTORY-MAP 把仓储存在性排除在 gate 外的口径，见其头 INVARIANTS）。
* `--json`=机器可读输出，供 `align_all.py` 第十节内联复用（不 subprocess 自调）。
* 依赖红线：只读（禁写任何文件，先例=校验器头 INVARIANTS "台账只读（本工具禁写）"）；路径以仓库根解析，**禁 CWD 漂移**（`check_stores(data, root)` 已为此扩了 root 参数，照抄其签名形态）。

## §6 生成器契约（`generate_construction_steps.py`）

1. 扫政策 MD → 抽 `D14-STEP-ANCHOR-BEGIN/END` 块 → 覆写图 YAML 的 `nodes/counts`，`edges` 由 `order` 生成主序、`feedback_loops` 由 `rollback_to` 生成；**`laws/boundary/pending_anchors` 为人工语义层，生成器保留不覆盖**（照 GOMAP 的 `effective_from` 保留策略，`alignment_checklist.md:88`）。
2. **禁 `datetime.now()`/`time.time()`**（RULE-SCHEMA-TZ 硬规则 10）；时间戳如需，经 `--as-of` 注入，且比对时忽略该字段（GOMAP 校验"忽略 generated_at/counts"先例）。
3. 生成器自身是新 .py 模块 ⇒ 施工同批必须：`add_module_translation.py` 登记大白话简介（TRANSLATION-COVERAGE gate 拦）、creation_token（CREATE-GUARD）、`apply_depgraph --add-design-node`（RULE-DEPGRAPH 先登记后施工）。
4. 未补锚环节进 `pending_anchors[]` 而非报错退出——生成器要能在半成品状态下可跑（防施工期一次性大爆炸 diff）。

## §7 与 gate 的接法（**不建独立 gate**）

* 共识件 §5④ 明令"st-gslim P4 已把六张图门并入聚合台"。动作=在 `src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py:295-302` 的 `subs` 列表追加**一行**：
  `("CONSTRUCTION-STEPS", "construction_steps_gate", "_check")`
* 新文件 `src/zephyr/gov_enforcement/commit_gates/construction_steps_gate.py` 只暴露 `_check(gateway, files, **kwargs) -> tuple[bool, str]`，形态逐条照 `strategy_factory_map_gate.py:114-139`：
  1. `_TRIGGER_FILES_NORMCASE` = {`config/construction_workflow_map.yaml`, 政策 MD 路径, 校验器路径, 生成器路径}；未触发 ⇒ `return True, "skip: ..."`；
  2. 校验逻辑动态 import `validate_structure`（`sys.path.insert(0, _VALIDATORS_DIR)`，先例注释"懒加载防 zephyr↔scripts 成环"）；**禁复制校验代码**；
  3. 图 YAML 解析失败 / 校验器不可达 ⇒ **fail-closed 阻断**（真源损坏必须先修）；
  4. 结构违规 error>0 ⇒ 阻断；告警面只呈报不阻断。
* 注册面：`in_process_gate_registry.yaml` 的 `MAP-ALIGNMENT` 条目（`:301-307`）`files_trigger` 追加本图触发面。**不新增 gate_id、不动 `total_gates`** ⇒ 净零满足（新增一台会违反 AGENTS §4.1）。
* gate 文件需 15 字段头（共识件说 14 字段头标注；实测 `trae_047:48 §A_full` 是 15 字段清单，两者不一致——**以 trae_047 为准并记 R-18 交总包核**，别照抄共识件的"14"）。
* own-scope：内容扫描型 gate 默认 own-diff 作用域；本校验器是结构校验型，走 `gate_registry.yaml` 的 `own_scope` 机生字段登记（AGENTS §3.2/§3.3：新 gate 必须 own-scope 或登记全仓扫描理由）。

## §8 挂轴（第⑤件，施工期由总包落）

| 面 | 动作 | 坐标 |
|---|---|---|
| `alignment_checklist.md` §3 | 加"AI 施工升级流图（图 14）"行：真源=`config/construction_workflow_map.yaml`、对齐 key=`step_id（D14-*）`、规则=CV-01~16、时机=commit 前（触发式）/align_all 第十节、工具=本校验器 + MAP-ALIGNMENT 子台 CONSTRUCTION-STEPS、处置=error>0 阻断 | 照 `:87`（图 9 行）与 `:88`（图 10 行）形态 |
| `alignment_checklist.md` §6 | 加时机矩阵一行 | `:189` 形态 |
| `align_all.py` | 新增**第十节**（照抄第八节 `:581-612` 形态：内联 import 校验器 + 传仓库根 + 硬>0 计入 exit 1） | `scripts/governance/d5_architecture/generators/align_all.py:581` |
| 宪章 §8.3 导航 | 纵轴图目录动态来自 §3，无需改宪章 | `system_charter.md:217-233` |

## §9 红证用例（**判通过前必须逐条证明能红**——AGENTS/共识件 §5"自写校验脚本必须先证明自己能红"）

每个用例=一份临时图 YAML/政策 fixture（pytest `tmp_path`，禁写生产路径，AGENTS §9.6），断言 `validate_structure`/`check_anchors` 返回**指定 error 串**且 CLI `exit==1`（解析类断 `exit==2`）：

| # | 红证 | 构造 | 期望触发 | 对应实测事故 |
|---|---|---|---|---|
| RC-01 | 伪造环节（图里有、政策里没有） | nodes 加 `D14-99`，policy 无对应锚块 | CV-04 error 列出差集 | 防"图长毛" |
| RC-02 | 漏图化环节（政策有 Step，图无节点） | 删掉 `D14-05` 节点 | CV-04 error | R-15（矩阵漏 Step 3.5）同族 |
| RC-03 | 断链 gate 引用 | `gates: [NOT-A-GATE]` | CV-06 error | — |
| RC-04 | 近似实名 gate | `gates: [SECRET-HARDCODE]` | CV-06 warn 点名 `NO-SECRET-HARDCODE` | R-14 实测 |
| RC-05 | 幽灵可执行锚 | `executable: [scripts/ide_health_service.py]` | CV-05 error + CV-16 连带 | R-01 原样 |
| RC-06 | 不存在的 CLI 子命令当锚 | 锚指向 `session_worktree.py` 却缺 `symbol` | CV-05 error（"可执行"判定不含函数锚时要求 CLI 面可发现） | R-06 原样 |
| RC-07 | 断链文档路径 | `docs: [{path: docs/02_.../design_memos/65_git_safety_governance.md}]` | CV-07 error + CV-08（已归档）error | R-11 原样 |
| RC-08 | 行号锚 | `policy_anchor: "...policy.md#step-2 L279"` | CV-07 error | R-13 原样 |
| RC-09 | 用 deprecated 件支撑 automated | `verifiable: automated` + docs 指向 `status=deprecated` 的 AI_review_instructions | CV-08 error | R-10 原样 |
| RC-10 | 越域吞图11 | `role: handoff` 且 `gates: [HELD-OVERLAP]`，或 `handoff_to: [D11-Z99]` | CV-14 error | 骨架门③ |
| RC-11 | 反向边未声明 | edges 加 `[D14-13, D14-06]` 不写 feedback_loops | CV-10 error | B5/B8/B10/B11/B13 |
| RC-12 | 自环未带常量 | edges 加 `[D14-10, D14-10]` 无 `max_rounds_ref` | CV-10 error | B9 |
| RC-13 | 把政策正文抄进节点 | `produces:` 填政策 L470 一整段（>120 字，含 ≥40 字连续重合） | CV-12 error | INV-1；政策 L77 编排层定位 |
| RC-14 | 散文计数漂移 | `counts.total_steps: 15` 而 nodes 17 条；或顶层写"端到端 15 步" | CV-13 error | R-12 |
| RC-15 | 枚举非法 | `verifiable: yes` | CV-09 error（且断言校验器未硬编码词表：改 fixture 词表须生效） | AGENTS §9.9 |
| RC-16 | 无证据的 built | `build_status: built`、`evidence: []` | CV-16 error | 骨架 §5 状态纪律 |
| RC-17 | YAML 损坏 / 顶层非对象 / 文件缺失 | 截断 YAML；写成 list；指向不存在路径 | CLI `exit 2`；gate 侧 **fail-closed 阻断** | 图 9 头 INVARIANTS 同款 |
| RC-18 | laws 或 boundary 清空 | `laws: []` | CV-15 + CV-01 error | 图 9 `:60-61` |
| RC-19 | 矩阵一致性回归 | fixture 政策删掉 Step 3.5 矩阵行 | CV-11 error | R-15 |
| RC-20 | gate 聚合残缺 | 把 `construction_steps_gate` 模块临时改名/不可 import | 聚合台 `subs` 分支 ⇒ `[CONSTRUCTION-STEPS] 子检查不可加载` 并阻断（`panorama_alignment_gate.py:310-312` 已实现该 fail-closed 语义，测试须验证到） | 防"台在但子台被吃" |

绿证要求：全部红证跑完后，用**真实图 YAML** 跑一次，允许的唯一剩余红=政策尚未补的锚块（走 `pending_anchors` warn 白名单），并在收尾报告写"当前 automated X / inspection Y / manual Z"（数字读 `counts`，禁手写）。

## §10 施工批次 DoD（波3 排产参考，每批可独立提交）

| 批 | 内容 | DoD（可判） |
|---|---|---|
| P1 | 政策 MD 补 17 个锚块（不改政策散文语义，仅追加锚块；改动属 01 域 policy 文件，需申请：本车道无写权） | 生成器能跑出 17 节点；`--anchors-only` exit 0 |
| P2 | 生成器 + 图 YAML 首版 + 校验器（结构面 CV-01~04/09/12/13/15） | 校验器对首版图 exit 0；RC-01/02/13/14/15/18 全红 |
| P3 | 校验器锚面（CV-05~08/16）+ 对抗测试全量 | RC-03~09/16 全红；真图上允许的红条目**逐条对应骨架 R 号**并留表 |
| P4 | 轴面（CV-10/11/14）+ CV-11 政策矩阵补行 | RC-10/11/12/19 全红 |
| P5 | gate 子台接入 `subs` + registry `files_trigger` + `test_construction_steps_gate.py` | RC-20 红；触发面外 skip 放行；提交不连坐 |
| P6 | align_all 第十节 + alignment_checklist §3/§6 挂轴 | align_all exit 0；第九/十节并存不冲突 |
| P7 | 政策真源纠偏（R-01~R-16 逐条闭环或降级标注） | 每条红要么锚已修、要么 `verifiable` 降为 manual 且在图里可见；禁"删政策句子让校验变绿"（那是把真源改没而非改对） |

## §11 净零与内收声明（AGENTS §4.1 要求新增须声明替代/合并）

* **未新增注册表**（选方案 E）、**未新增 gate 台**（进 `MAP-ALIGNMENT` subs）、**未新增枚举词表**（复用 verifiability + 图 9 build_status）。
* 新增 4 件（2 py + 1 gate 子台 py + 1 图 YAML + 1 测试）声明替代：政策 §4 手工 Checklist（16 行散文勾选 → `counts` 机生）、政策 §2.3 矩阵手工维护 → CV-11 机校、`rule_catalog_registry.section_count: 0` → 生成器填。
* 与图11 的重复面**已按内收判据"跨域不同对象→不并"处理**（handoff 引用而非合并建图），证据=政策 L99/L101 原文 + 图11 骨架 §0/§3 双向认领。
* 触发率观察期：本图 gate 与 GOMAP 同款（`alignment_checklist.md:88` "免独立校验器/免 gate，触发率实证后再议"）——建议本台先随聚合台跑一季，若 CV 违规零触发则考虑降为 align_all-only。

## §12 未决与需裁定（校验器**不能**自己解决的部分）

1. **Step 1 / Step 6 结构性不可机验**：政策 L184/L465 明令"审查结论在对话内给出，禁止创建报告文件"。要么裁定允许 `.runtime/sessions/<sid>/` 留痕件（不入 git），要么接受这两环节永久 `manual`。**规格不擅自定，图里先标 manual 并挂 `red_findings`**。
2. **R-08 词表模块缺失**（`zephyr.shared.vocab.market_state` 不存在而两册文档称"已建成"）：Step 5 的锚在补出该模块前不得标 automated。
3. **域宽矛盾（骨架 R-16）**：`scope: global` vs 正文"仅 07 域"——影响本图节点是否覆盖图12/图16 车道，须先裁后建。
4. **图11 引用表未定稿**：CV-14 跨图引用集合目前从 `fig11_delivery/00_skeleton.md` 文本扫 `D11-[SCD]\d{2}` 得到——图11 骨架一旦改编号即假红。施工期需总包裁决是否升级为"图11 也机生一张环节清单"（若升级，本条改为读清单文件，避免文本耦合）。
5. **政策是否愿当宿主**：方案 E 要求政策 MD 接受锚块（政策文件不在本车道写域，且 policy 是 `ttl: permanent` 规则件）。若 Owner 否决内嵌，退方案 D（新册），代价=+1 册 +1 ROOR 行 +双真源同步义务（此时**必须**同批把校验器改判"册为真源、政策为引用"，否则政策与册漂移无人知）。

## 总包收口请求（本件诉求，共享面禁本车道直写）

| # | 诉求 | 面 |
|---|---|---|
| V-1 | §12-3 域宽裁定（scope: global vs 仅 07 域）先落，否则节点数与 handoff 清单都定不下来 | 政策 frontmatter / 裁定册 |
| V-2 | 施工期写域申请：政策 MD（P1 批补 17 锚块）与 `docs/01_policies_and_standards/_registry/catalogs/*` 均在本车道禁写清单外，须总包代落或显式授权 | policy + catalogs |
| V-3 | `panorama_alignment_gate.py` `subs` 加一行 + `in_process_gate_registry.yaml` MAP-ALIGNMENT `files_trigger` 追加触发面（不新增 gate_id、不动 `total_gates`） | src + 册 |
| V-4 | `alignment_checklist.md` §3 图14 行（key=`step_id(D14-*)`）+ §6 时机矩阵行 + `align_all.py` 第十节 | docs + scripts |
| V-5 | token：`validate_construction_steps.py`/`generate_construction_steps.py`/`construction_steps_gate.py`/`config/construction_workflow_map.yaml`/`tests/governance/commit_gates/test_construction_steps_gate.py` 五件 + 本车道 2 份 MD | creation_tokens |
| V-6 | 施工期新 .py 三件的模块大白话简介登记（`add_module_translation.py`）与 depgraph 设计态登记（`apply_depgraph --add-design-node`）须同批 | module_translation + depgraph |
| V-7 | R-01~R-16 + R-18（gate 头字段 14 vs 15 口径不一）交总包统一排产纠偏；本图校验器上线后这些会**持续判红**，属预期行为不是噪声，勿为变绿而删政策句 | 多面 |
| V-8 | 与图11/图16 车道的会签：handoff 引用表（D14→D11）与"治理立法流是否被本图 Step 1.8/Step 6 覆盖"两问需在波2 收口 | 跨车道 |

**自审裁定**：干（本件为规格件，六向台账要求适用面=作业簿；规格自身已含真源调研六证：A 候选面逐个实测、B 字段集与既有 schema 对齐、C 母版坐标逐行引、D 红证 20 条、E 施工批次 DoD、F 未决项不擅裁）。
