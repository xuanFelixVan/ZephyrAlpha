---
ttl: task_bound
title: Max 日班判决书——夜裁-01..24 逐条裁定（裁定#340..#360）
session: st-maxday-20260919
---

# Max 日班判决书（2026-09-19）· 夜裁-01..24 逐条裁定

> **程序依据**：`rule_disposition_policy.md`（六道闸×六类归宿；三铁律含 0.3 红证双向）。
> **输入**：交接令 `2026-09-19-overnight-handover-max-shift.md` §五 + 证据真源 `2026-09-19-overnight-scope-lock-report.md` + 主方案 D-1..D-18。
> **编号**：正式裁定号 #340..#360（现值 max=#339 已 grep 亲验；"夜裁-NN"仅为交接临时号，全部映射到正式号）。
> **证据等级**：本文件自标 `[亲验]`=本班现场命令取证；`[夜验]`=夜班亲验且本班抽查关键面吻合；`[转报]`=仅采信未复测（不作唯一判决依据时才允许）。
> **净零申报**（宪法 §4.1）：本批裁定无一新增门禁册条目、无一新增规则文件；全部处置落在既有检查器参数面/判据面/登记同步面。

## 〇、开工自证（并发与回退炸弹处置记录）

1. 心跳：45 个 pid 文件全部 >4.7h 陈旧（最年轻 AI-NIGHT-A2/A7 ≈4.8h）→ 开工时无活跃会话。`lock_files.py list` = CLEAN。队列 0 pending / 0 processing（done 1065 / dead 1030）。
2. **回退炸弹复测**：三分法（HEAD/INDEX/工作区 git-hash-object 逐条比对）发现 **19 条 INDEX 陈旧且工作区==HEAD**（复位=内容中性）+ 37 条前进/在途条目。19 条已按夜班同手法 `git reset --pathspec-from-file` 复位（复位前逐条断言 WT==HEAD，双向红证成立）；37 条在途件原样保留（含 bizmine_chain_mining、a2_handoff 等他人 staged 新件）。pathspec 清单留 `.runtime/tmp/dayshift_reset_20260919.txt`。
3. 案卷 1404 份仍在 `.runtime/sessions/st-ruledisp-20260918/staging/dossiers/`（TTL 未吃）；`redlab_a1b/` 仍在。
4. 本班未碰 `docs/_working/` 既有条目（本文件与裁定登记为新增）；未碰 `st-ramp-wp1b` 在途持有的 `rollback_verifier.py`。

## 一、第一梯队（裁定#340..#345）

### 裁定#340｜D-10 更新：T0 可用卡 6 → 18/19 张
夜班把可证红卡从 6 张扩到 18/19（真源=scope-lock §二表，本文件不复数）。**更新 D-10**：T0 机械波可用卡以该表为准；唯一前置=口径批（#345/#350/#352）先落，否则弱模型在假信号上空转。D-10 原"只用 6 台卡"限制解除。[夜验+本班采纳]

### 裁定#341（夜裁-01）｜55 台 pre-commit 门禁零执行权 → **E 上交**
**亲验**：gate_registry 169=pre-commit 55+commit-gate 113+manual 1；in_process 册 113 与 commit-gate 全等、与 pre-commit 交集 0；`git_commit_gateway.py:3115/3117` 与 `scripts/governance/commit_queue_landing.py:38` 均 `--no-verify`；全仓 grep 无任何 `pre-commit run` 调用点（仅注释提及）。
**上交包**：证据如上；建议=**方案②**网关落地前对 staged 面跑 `pre-commit run`（吞吐成本限于改动面），**备选方案③**并入 #354 周期审计波（55 台转夜间全树审计，零提交延迟）；两案都应给 gate_registry 加 `enforcement_channel` 字段防再生。**不裁的后果**：GATE-ARCH/GATE-NAMING/GATE-SSOT-CODE 等 55 台只咬裸提交违规者，守规会话永久免检；`check_protected_paths --staged` 第二层在网关通道同样不执行，受保护路径实拦只剩 message 标记层。**禁止在 Owner 裁决前动主链路。**

### 裁定#342（夜裁-02）｜3 条 entry 补 `--ci` → **E 上交**（flag 出厂翻转门位）
**亲验**：三台 entry 均无 `--ci`；`check_src_no_data.py` 尾部 `if args.ci: return EXIT_FINDINGS / return EXIT_PASS` ＝带违规仍放行，双重保险丝全断属实。
**上交包**：建议=批准三条 entry 各补 `--ci`（一行注册表数据×3）；同批附带两处 B 修（前置随批）：①前缀真源扩 `src/zephyr/data/`（现只拦 `src/data/`，逃逸在宣称范围外）；②契约文件缺失时 `FORBIDDEN_PREFIXES=()` 静默全放改 fail-closed。**不裁的后果**：三台继续只打印不拦。

### 裁定#343（夜裁-03）｜删除打包 → **E 上交（删除）+ F 挂起（真岛翻案）**
- **①`.tmp` 打包**：现值 **148 件 / ≈86MB**（本班 `find -name "*.tmp"` 排除 .git/.worktrees [亲验]；较夜班 137/82.7MB 漂移=dev 在动）。含 CAS 原子写残留**隐藏点文件** `.capability_canonical_file_registry.yaml_<rand>.tmp`（catalogs 下抽验 5 枚 [亲验]）→ 删除脚本必须含隐藏文件。**上交 Owner 批准删除**；批后由 Flash 先 `--dry-run` 出精确清单（排除 `.worktrees/**` 他人工棚）再执行。
- **②"唯一真岛" cohort_daily_ledger.py → 翻案，F 挂起**：夜班定性被本班实证推翻——WORK-ORDER-5（投资者行为日账本）三笔 commit 在案：`1603be4cd4` 立项（五人群×粒度×三期）、`fac109d7a2` 数据线对账、`0a276ca249` 接口镜像条款 [亲验 git log --grep]。该模块是**在册立项待接线**，非死代码。**处置：挂起（F）挂 WORK-ORDER-5 接线里程碑，T-10 撤案，禁止删除**；若立项废弃须先走正式退役裁定。
- **③0 字节残壳** `tests/signal_ashare/test_sector_strength_aggregator.py`：0 字节属实 [亲验 ls]，并入①打包。
**不批①的后果**：86MB 继续占盘且 TEMP 模式缺口（#345b）修复后每晚都把它们数一遍。

### 裁定#344（夜裁-04）｜N-16 白名单加 `algo_flow` → **B 修正，D-14 后落地**
**亲验**：`skip_dirs_docs` 真源在 `rules/trae_028_doc_structure_naming.yaml:1165` §n16_config（代码动态加载、YAML 即生效、硬编码仅 fail-open 回退）。真源在 rules/ → **受 D-14 冻结约束，落地排 WP9 判案后与 #346 批同批**。语义=扫描面修正非豁免实质违规（algo_flow 镜像卡 doc_type=architecture_view 本就不在 trae_047 B_yaml 适用面，与 #349 互为支撑）。预期 C-04 636→27。夜班标【Owner】不采：白名单扩一项不属宪法 §5 四类门位，且证据 100% 机械（606 件全在名为 algo_flow 的目录）。

### 裁定#345（夜裁-05+14）｜口径双裁定 → **B 修正 + C 加牙（同批施工）**
- **(a) `--tracked-only` 口径**：四卡执行器（C-02 frontmatter / C-07 索引 / C-08 目录契约 / C-09a 临时件）加 opt-in 旗标，**不翻默认**；T0 卡与审计工作流 v4 引用一律带口径。依据 [亲验]：`.gitignore:262` `/*` 白名单模型 → "扫得到但提交不了"面结构性恒红（C-02 18/C-08 9 全在 ignore 区，跟踪面债务 0）。
- **(b) `TEMP_FILE_PATTERNS` 补 4 类**（`\.tmp$`、`^_probe_`、`^commit_msg`、`^pytest_`）：加牙但红数**以 tracked 口径计**（与 (a) 联动），不采 810+/3014 全盘面数为施工验收基线。
- **净零申报**：检测器参数面+模式清单，无新门禁。红证：补模式后对已知 `.tmp` 样本红、撤样绿 [夜验配方复跑]。

## 二、第二梯队：规则面（裁定#346..#350）

### 裁定#346（夜裁-06/07/08）｜rules/ 面三批处置框架
- **29 条重指（16 份 42+/42−）→ B**：成品四件已在 git 跟踪区、`git apply --check` 本班复验 PASS [亲验]。**落地时点=WP9 判案后**（D-14 不重开）；ISSUE_ID **新立本战役议题**（architecture_issue_registry 加条目，禁借无关 ID——夜班拒伪造正确，追认）。
- **5 条 `_archive/` 当现役 → F 挂起→WP9 逐条判**：改指向=替架构决定"工具还要不要"，须 salvage 证据（WP8 v2 出）。ide_health 族（trae_053）有 2026-08-28 僵尸清除记录，预判 D3。
- **7 条真删无后继 → 预判 D3**：`f57016319e`（retire 3 task_bound scripts）等退库 commit 本班 git log 亲验在案；同走 v2 salvage→WP9 终判。
- **流程缺陷上报（Owner 知悉）**：工具退库/归档时无"grep rules/ 引用面"义务 → 条文悬空数月无人知（本案 12 条即实证）。治本=退役 SOP 补一步引用面清扫（并入既有 SOP 步骤，非新规则，§4.1 合规）。
- **闸0/闸1 采数口径更正**：A2 实测 M1=41 条/19 份（①29/②5/③7）+裸名 12 条非缺陷；M2 悬空配对**只 1 条**（TRAE-079，见 #347）。

### 裁定#347（夜裁-09）｜TRAE-079 → **B 身份修正（推翻 D4 预判）**
**亲验**：`COMMIT-CRITICAL-SECTION-LOCK` 两册零命中、全仓仅 trae_079 条文自身——夜班"从未存在"在**册名层面**成立。**但** `git_commit_gateway.py:2360-2366` 的 `_GlobalCommitLock` 临界区机制**实存**（含 `_audit_commit_lock_fallback` 审计兜底，日志自标 TRAE-079）→ 机制层面"从未存在"不成立，**D4 不适用**。
**处方**（闸0：对不上→先建映射，不改规则）：优先把现存临界区锁机制按实名登记进 gate_registry（source: commit-gate，指向 gateway 内实现）；若册内 schema 不适配（锁非检查型 gate），则改 trae_079 §enforcement 的 executors 指向实存机制名并保留 code_embedded 类型。**流程缺陷上报保留**：册外身份游离数月无人发现＝"登记环节不校验强制体存在性"的又一实证。该锁的 fail-open 姿态争议归 #353①。

### 裁定#348（夜裁-10）｜规则面风险档 → **维持 D-7 两轴派生，"TRAE 归哪个域"消解**
**亲验**：risk_tier_registry 真键 `domain_tiers`=18 域、无 TRAE、无 `entries` 键（按 entries 取得 0 属实）。**裁定**：不给 86 份补 domain、不加 TRAE 域条目——按 D-7，案卷生成器直接读 `safety_level`+`ai_autonomy` 两轴派生风险档；案卷口径 bug（entries→domain_tiers）随 v2 采集器修正。3 条 None-domain 不阻断。**验收红证**：v2 重跑后"退化方向可判分母"从 0 变 >0。

### 裁定#349（夜裁-11+12）｜ALGO_FLOW 分型豁免 → **B 适用面修正（227+2993 件均不计违规）**
**亲验**：trae_047:44/:140 B_yaml 适用面=`gate, registry, contract(yaml), config, data`；抽卡 `docs/03_modules/_domain_alt_data/algo_flow/_extensions__init__.yaml` 为 `doc_type: architecture_view` 且自带 `source_of_truth`——**卡不在规则自陈适用面内**。
- **(a) 2993 件 5 栏**：无补栏义务 → 卡判据按 rule 分型适用面过滤（C-01/C-04 套栏外溢修正）。**不造 join 生成器**（为非义务造工具=负资产）。T-3 撤案。
- **(b) 227 件继承矛盾**：上游是被 `gov_eng_002_exempt`（trae_047:109-115）豁免的 `__init__.py`（抽卡上游即 `src/.../_extensions/__init__.py` [亲验]）→ **豁免随链传播**，继承义务对豁免上游失效；改的是卡判据，不是 227 个文件。T-4 撤案。
- 两判合计消解 C-01 77.6% 假红主体。**不修 trae_047 豁免面**（豁免本身有 AST 事实依据）。

### 裁定#350（夜裁-13）｜闸2 词表判据收窄 → **B 修正（M5 处方照准）**
[夜验+本班复核处方件在案 55 行]。判据改法：只在 `conditions[].check|pass|fail`、`actions[].step(type=mandatory|forbidden)`、`invariants[].description` 位匹配情态词；同句含"禁止/不得/MUST NOT/名词后缀（产出/输出/记录）"豁免——消解 13 处误报（名词位/防御条款自引用/术语定义位）。**21 处真规范位的逐条二值化处方**（A2_M5_prescriptions.md）属 rules/ 面 → 与 #346 批同落（WP9 后）。工具侧（词表判据）不属 rules/，**Flash 可立即施工**。

## 三、第三梯队：裁判失明面（裁定#351..#356）

### 裁定#351（夜裁-15）｜装载器 fail-open → **C 加牙（Max 权限内，依概括授权）**
**亲验**：`gate_auto_registrar.py` docstring 自述"失败不抛异常（fail-open）"，import/factory/register 失败仅进 failures+logger.warning，装载数≠名册数无报警。
**处方**：改 fail-closed（任一门装载失败→提交阻断并报 gate_id+错误）+ 装载数≠名册数硬告警（并入 fail_open_register 台账族）。对照组=commit_gate_registry.check_all 单门异常即 fail-closed（仓内既判好设计）。**授权依据**：Owner 2026-09-18"一律取治本"概括授权 + D-2/D-18 改门禁执行链同族先例。**部署前置**：113 台全量 import 健康预检（防一台坏=全仓冻结）。红证双向：断一门 import→必拦；健康→放行。
**我可能错在哪**：可用性代价真实（一台坏=全员冻结）；逃生通道=emergency_commit（宪法 §9.8 钦定锁/注册表不可用时可用）。若 Owner 认为此收紧应回门位，可否决本条（影响仅 #351，不连坐）。

### 裁定#352（夜裁-16）｜check_encoding GBK 失明 → **C 加牙（推翻"属门位"预判，新证据）**
**亲验**：`check_encoding.py` 五处 `except UnicodeDecodeError` 吞掉；**全仓 tracked 面 .py/.md/.yaml 不可 UTF-8 解码存量=0**（本班全量扫描）→ 夜班"收紧会点亮存量红"前提**不成立** → 无剩余 Owner 权衡，Max 可裁。
**处方**：tracked 面源文件不可解码即 FAIL（口径与 #345a 一致）。红证双向：造 GBK 样本→红；撤→绿。**不翻既有 mojibake 检查行为**。

### 裁定#353（夜裁-17）｜网关兜底 → **三拆：E 上交① + B 修正②③**
**亲验**：`:1717-1748` SSoT 兜底 capability_lookup 不可用→`return(True,…)`（注释自认 fail-open）；`:2362` _GlobalCommitLock 不可用→fail-open 继续提交（trae_079 bypass_allowed:true+落审计的明文承载）；`:3584` 幻影签名 `not line.startswith('A"')` 跳过带引号路径（中文路径 git 必加引号→逃逸）；LSG `gateway.py:123` `FAIL_OPEN_LAYERS={l6_observability,l7_validation}` 硬编码。
- **① SSoT 兜底 + 全局锁 fail-open → E 上交**：门禁自身 high 档应然 fail-closed，但锁的 fail-open 有 trae_079 条文明文承载＝**程序法与条文的闸3 冲突**，须 Owner 定夺（建议 fail-closed+emergency 通道；不裁后果＝坏场景静默放行，锁失效正是回退炸弹机理的一环）。Owner 裁后同批改 trae_079 §enforcement（WP9 后 rules 批）。
- **② LSG 配置化 → B**：FAIL_OPEN_LAYERS 抽到配置，**默认值维持现状（零翻转）**，给 Owner 可关手柄。
- **③ 引号路径解析 → B**：解析 git 带引号形式（含转义还原），中文路径幻影不再逃逸。红证：造中文路径 AD 幻影→修前漏/修后红。

### 裁定#354（夜裁-18）｜观测面 9 台 → **C 加牙（审计模式，不动提交面）**
**亲验**（抽查 check_src_no_data）：`files=get_staged_files(); if not files: return EXIT_PASS`＝staged-only 属实。**但提交面 own-scope/staged 是宪法 §3.1 立法设计（防连坐），不是缺陷**——夜班"永久失明"定性只在"无周期全树审计面"意义上成立。
**处方**：9 台加 `--full-tree` 审计模式+周期任务（并入既有审计任务族；审计扫描非 reconciler，不违 §9.3 事件触发律）。**该基建即 #341 方案③的载体**：Owner 若选③，55 台 pre-commit 门禁同车夜间运行。净零申报：检测器参数面，无新册条目。

### 裁定#355（夜裁-19）｜generate_missing_index_md worktree 恒绿 → **B 修正（最高优先级机械件）**
**亲验**：`:294` `any(p.startswith(".") for p in dirpath.parts)`——parts 是绝对路径分段，`.worktrees/` 下检出时**每个目录**的 parts 都含 `.worktrees` 段→全 skip→"扫描 0 个目录"假绿。**提交队列 serializer 正跑此通道**＝假验收源头。
**处方**：判隐藏目录改用相对扫描根的 parts（`dirpath.relative_to(root_dir).parts`）。红证：worktree 内跑修前 0/修后>0（夜班已给主区 1002 vs 工棚 0 双向，施工时复跑）。

### 裁定#356（夜裁-20）｜缺 index.md 净增 → **口径定案+生成器施工令**
**本班复算**（tracked∧内容件≥2∧无 index.md）：总数 **346**（夜班 344 属漂移）；`docs/_working` 临时区 **110**（豁免——TTL 区无索引义务）；永久区 236−`_archive` 3＝**真欠账 233**（03_modules 215+01 11+02 7）[亲验]。
**裁定**：①三口径并存合法但**引用必带口径**（宪法 §4.3）；②施工对象=233，由 generate_missing_index_md.py 批量产（宪法 §9.5 禁手工维护），**先修 #355**，按域分批一批一提交；③index.md 属派生导航件，不占 §4.1 规范预算。工具口径 1002 不作施工依据。

## 四、第四梯队（裁定#357..#360）

### 裁定#357（夜裁-21）｜check_index_integrity 判据重造 → **B 修正**
[夜验]：A7 改 35 行真内容门计数 517→517 纹丝不动＝不能当验收证据的铁证；`get_sibling_files` 只收 md/yaml→指 .py/.json 的链接永远红；递归 basename 命中→跨目录正确链接全误报、`_archive/` 同名真断链漏报。
**处方**：①链接解析改"相对本文件路径"；②sibling 集扩 .py/.json；③frontmatter/版本史正文排除出索引清单判定。同族 `validate_cross_references.py:642` 对 `file:///` 直接 continue 一并修（绝对针纳入校验，锚点剥除沿用 `7877077bf7` 语义）。**红证双向**：跨目录正确链接不再红；真断链仍红；同改动必须引起计数变化（否则重造失败）。

### 裁定#358（夜裁-22）｜blueprint_registry"SSoT"行 → **维持 D-11 既裁，按 WP11 处方执行（B）**
无新决策：D-11 已裁"故意退库禁恢复"；WP11 五点处方全套执行（index.md:91 改"派生件+生成器"表述去链接、_registry/catalogs/index.md:49 删行、四处"SSoT"表述改"frontmatter→生成器"链、不动历史 changelog、收尾删 audit_prompts 过期括号）。Flash 施工；`capability_canonical_file_registry.yaml` 热件走 CAS 单独批。

### 裁定#359（夜裁-23）｜WP17 未施工 → **维持立项，排本班后第一优先**
D-18 已立法（恒真＝第三种假绿）不重开。修法照主方案 WP17：入参/工具异常与攻击拦下**分桶**（前者 error 桶绝不计入 blocked）+ 区分度自检（应拦场景与应放行场景结果必须不同）。Max 亲自处方+验收，Flash 施工。

### 裁定#360（夜裁-24）｜归档面豁免+提交入口写法 → **B 修正×2**
**亲验**：construction SOP L29 `scripts/git_commit_gateway.py` 与 L610 `python scripts/git_commit_gateway.py`（该 CLI 路径全史从未存在）；legacy v1 宪法、data/reports/dm018/dm020 历史战报属归档/审计轨迹面。
- **(a) 归档/历史面免断链豁免**：`agent_constitution_legacy_v1.md`、`data/reports/dm018/dm020`、`_archive/**` 登记进断链检测器豁免面（改归=改历史，禁修正文）。落点=D4 路径检测器 exempt 配置（非 rules/）。
- **(b) SOP 提交入口写法定案**：L29/L610 统一改 `python scripts/git_commit.py`（CLI 正门，宪法 §2.1/§7 钦定）；模块引用保持 `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（L32 已正确）。SOP 属可写路径，Flash 施工，替换文本逐字给出。

## 五、Owner 上交清单（E 类汇总——等人在门位，本班未执行）

| # | 事项 | 建议 | 不裁的后果 | 证据 |
|---|---|---|---|---|
| #341 | 55 台 pre-commit 执行权 | 方案②网关 staged 跑 / 方案③周期审计波（#354 基建） | 守规会话永久免检 55 台；受保护路径第二层不执行 | [亲验] §一 |
| #342 | 3 entry 补 --ci | 批准（+两处附带 B 修随批） | 三台只打印不拦 | [亲验] §一 |
| #343①③ | .tmp 148件/86MB+0字节壳删除 | 批准（dry-run 先行、含隐藏点文件、排除 .worktrees） | 86MB 占盘+模式补齐后每晚重数 | [亲验] §一 |
| #353① | SSoT 兜底+全局锁 fail-open 收紧 | fail-closed+emergency 通道；条文与程序法冲突需定夺 | 坏场景静默放行（回退炸弹机理一环） | [亲验] §三 |

**破坏性动作单独列表**：仅 #343①③（删除）；其余裁定无删除/净增/阻断翻转。#351/#352 属收紧但依概括授权+存量 0 实证落在 Max 权限内，已在各自条目声明"我可能错在哪"与否决路径。

## 六、执行清单（Flash 施工序，按依赖排序）

| 批 | 裁定 | 内容 | 前置 |
|---|---|---|---|
| A0 | #355 | generate_missing_index_md 相对路径修复（serializer 通道止血） | 无——**第一件** |
| A1 | WP8 | 案卷 v2 重跑：D-6 收窄判据 + #348 两轴 + #350 词表判据 + #349 分型过滤（都在采集器/判据层，不触 rules/） | A0 |
| B | #345(a)(b)、#352、#357 | 口径批：tracked-only 旗标+TEMP 模式+编码收紧+索引判据重造（+validate_cross_references file:///） | 无 |
| C | #358、#360、#353②③ | 引用面：WP11 处方、SOP 入口+归档豁免、LSG 配置化+引号解析 | 无 |
| D | #351、#354 | 门禁面：装载器 fail-closed（113 台预检先行）、full-tree 审计模式+周期任务 | B/C 无冲突即可并行 |
| E | #356 | index.md 233 件生成（分域分批） | A0 落地 |
| F | WP9 判案（Max）→ #344+#346+#350(21条)+#347+#353①条文侧 | rules/ 统一批：新立 ISSUE_ID+ARCH-APPROVAL | A1 完成 |
| G | #359 | WP17 对抗校验器分桶 | Max 处方先行 |

派单姿势照抄交接令 W4 三条（--base-head 归属/入队正形/claim 必在主仓 cwd）。

## 七、复查清单与复核命令

1. 回退炸弹：`git diff --cached --name-only` 逐条三分比对应无"WT==HEAD 且 INDEX≠HEAD"残留（本班已清 19，工具=pathspec 复位+hash-object 三分法）。
2. #344/#346 落地后：`python scripts/governance/d3_metadata/check_naming_convention.py --scan` 涉事数 636→≈27；`git apply --check rules_m1_repoint.patch` 于落地批前复验。
3. #345/#352 红证：造 `.tmp`/GBK 样本→红→撤→绿，双向贴命令与退出码。
4. #348 验收：v2 案卷"退化方向可判分母">0。
5. #355 红证：worktree 内修前"扫描 0 目录"/修后>0。
6. #356 口径：`git ls-files | <分域统计>` 复算 233。
7. 全部施工批提交后：`git log -1 --name-only` 核实归属（宪法 §2.5）。

## 八、本班认的账

1. `.tmp` 148 件中含 `.worktrees` 排除口径；Owner 批后 dry-run 清单须再排除他会话工棚内文件（本班计数已排除，删除时同样）。
2. #347 的两个落地方向（登记 vs 改条文）留施工时按册内 schema 可行性择一——本班未逐字段验 gate_registry 条目 schema 对锁型机制的适配性。
3. #354 周期任务的调度载体（计划任务 vs 现有审计任务族挂载点）未选型，施工时按 ROOR 查注册表后定。
4. M5 的 21 条条文处方、A2 的 M1 三类清单均未逐条复核原文（采信夜班 [亲验] + 本班件在案复验）；WP9 判案时逐条过。
5. 夜裁-13 的"38% 误报"分母 34 未复测（处方件抽验一致；词表收紧后的实测数以施工批红证为准）。
