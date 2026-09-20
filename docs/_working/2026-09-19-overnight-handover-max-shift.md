---
ttl: task_bound
title: 通宵班交接令（Flash 夜班 → Max 日班）
---

# 交接令 · 2026-09-19 通宵班 → Max 日班

> **真源分工**（防双真源，本文件不复述证据表）：
> - 证据与全量基线 = `D:\ZephyrAlpha\docs\_working\2026-09-19-overnight-scope-lock-report.md`（§一–§九）
> - 施工纪律与裁定 D-1～D-18 = `D:\ZephyrAlpha\docs\_working\2026-09-18-rule-audit-master-construction-plan.md`
> - 程序法（六道闸×六类归宿） = `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\review_sop\rule_disposition_policy.md`
> - 审计工作流 v4（22 域 + 18 张 T0 卡） = `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\audit_prompts_20_ai.md`
> - 身份键地基修复细节 = `D:\ZephyrAlpha\docs\_working\2026-09-18-gate-identity-root-fix-plan.md`
> - A2 未放行成品 = `D:\ZephyrAlpha\docs\_working\rule_audit_campaign\a2_handoff\`
> - 案卷 1404 份 = `D:\ZephyrAlpha\.runtime\sessions\st-ruledisp-20260918\staging\dossiers\`（**24h TTL，先抢救再动**）

## 一、前因（为什么要做这一整摊）

Owner 的目标链条是：**让便宜模型（Flash）去执行全仓"打扫卫生+审计+治本修复"**，把项目里每一个多余零件清出去。
但传导链上有个大坑：**人写规则 → 裁判（门禁）执行 → 便宜模型照裁判结论改文件 → 总控照结论收口**。
裁判错一次，会被 22 域 × 每轮 × 弱模型**无怀疑地、且是"绿着"地**放大。所以 Owner 定的序是：
**先审"规则与裁判本身"，再开机械波改文件**。

因此本战役有两个面，不要混：
- **面 A＝审判规则与裁判**（本夜班主攻）＝六道闸×六类归宿，产出是"哪些规则该维持/修正/加牙/减重/上交/挂起"。
- **面 B＝打扫卫生**（v4 审计工作流）＝22 域 × 18 张 T0 卡，产出是"哪些文件不合规、哪些零件是多余的"。

**夜班核心结论：面 B 的多数"吓人数字"是假的，面 A 的裁判体系有两处结构性失明。**
所以在面 A 修好之前开面 B 的规模化施工，就是在与规则对赌。

## 二、前夜已定且**不得重开**的裁定（Owner 已拍）

| 编号 | 内容 | 状态 |
|---|---|---|
| D-1 | 身份键走 B′（三面一致性在 commit 时强制），不走 A | 已裁 |
| D-6 | 案卷判据收窄（曾报 962/948 作废） | 已裁 |
| D-7 | 规则面风险档＝两轴推导（`safety_level`→退化方向、`ai_autonomy`→人机门位） | 已裁 |
| D-8 | 记忆文档 A/B 抄 ARCH-310 R3 方法，**必须有 C 组阳性对照** | 已裁 |
| D-9（更正后） | `AGENTS.md` ↔ `agent_constitution_l0.md` 是**分叉双真源**（42 行真差异），真源＝`AGENTS.md` | 已裁 |
| D-10 | T0 波只用已证红卡片 | **本夜班已把可用卡从 6 张扩到 18/19 张，此裁定需更新** |
| D-13 | Flash 写权限＝只能改"有唯一可读字段真源、值可机械确定"的项 | 已裁 |
| D-14 | `rules/` 全域冻结到 WP9 判案完成 | **夜班按此自行停手，见 §五-2** |
| D-15 | 主区具名 + `--enqueue` 是正门（三前置） | 已裁 |
| D-18 | 对抗校验器恒真＝第三种假绿；红证必须双向；立 WP17 | 已立法 `0315d5555d`，**WP17 未施工** |

## 三、夜班已落地（8 笔 commit，全部经 `git merge-base --is-ancestor` 复核在 dev）

| commit | 内容 | 实测效果 |
|---|---|---|
| `bdc21c8811` | `detect_orphan_py` 豁免 `.aidrafts`/`.worktrees` + 摘 `--fix`；扫描入参口径收进 `_shared/walk.py` 单一真源 | 孤儿 330,615 → 真值 0 |
| `3a67233f41` | `detect_threading_lock` / `detect_vague_terms` 接入新口径 | 相对/绝对口径同数 |
| `0406b66fce` | `detect_ruins_references` 接入新口径 | 同上 |
| `40bfe9a7c8` | 施工 SOP `construction_workflow_policy.md` 3 处 `diagnose_depgraph.py` 重指现址 | 断链 58→56 |
| `3450edb560` | 施工图模板 `check_blueprint_compliance.py` 重指 `d3_metadata/` | 断链 56→55 |
| `7877077bf7` | `check_index_integrity.py` 新增 `_strip_anchor` 剥链接锚点 | 主区 1263→547（−716）；双向红证成立 |
| `864618bc7a` | 30 条 `file:///` 绝对针 → 28 改相对 + 2 去链接保行文 | `audit_broken_links --check-new` rc=0 |
| `e9fb06c2d4` | 5 行改指已核实唯一真址 | 逐条 `git ls-files` 唯一性断言 |

**统一根因**：CF1 那三笔与 P0-8 是**同一个病**——绝对/相对路径语义没归一。修一处能带一片。

## 四、夜班**主动否决**的动作（不要重做，除非有新证据）

1. `gate_registry` 里"133 条无同名 pre-commit hook"＝**误报**（按 `source` 分：pre-commit 55 / commit-gate 113 / manual 1，in-process 本就不该有 hook）→ 真漂移只 2 条。
2. `rule_catalog_registry.yaml` 214 条空 `rule_form`／107 条空 `status`＝**合规非欠账**（机生册忠实反映源文档 frontmatter 无该键；重跑生成器一个都填不上）。
3. C-01 的 4241、C-04 的 636、C-07 的 1263、C-09a 的 770、C-02 的 18、C-08 的 9、C-12 的 512、C-15 的 1610 ＝**全部或大部分是口径/投影假信号**，逐条见报告 §五。
4. **`docker-compose.yaml` 不是拼写变体**：`docs/03_modules/index.md:107` 是"两种拼写都豁免"的正文，改它＝造 bug（我派单写错，A7 挡下）。
5. **13 条"真删悬空行"一条都不该删**：7 条指 gitignored 但盘上存在的派生件、2 条是 frontmatter/版本史正文、2 条"待施工"声明、2 条该改写不该删。
6. 52 条 `blueprint.md` 裸名＝泛称不是链接；4 条 glob＝模式说明；`_registry/index.md:23` 的 `_index.yaml`＝文件数叙述。
7. 普查曾报"63 声明 fail-open / 103 未声明"＝**不可复现**（`gate_registry.yaml` 根本没有退化方向字段），该数作废。

## 五、待裁清单（**夜裁-01 … 夜裁-24**）

> 分三档：**【Owner】**＝人在门位（宪法 §5：production 流转/注册表净删/flag 出厂翻转/资金破坏）；
> **【Max】**＝下一个对话里由 Max 判案；**【Max→Flash】**＝Max 定了方向后 Flash 可直接施工。

### 第一梯队：不定这条，后面全悬

**夜裁-01【Owner】｜55 台 pre-commit 门禁在所有合法提交通道上零执行权（P0-1）**
- **这是什么**：名册 169 条＝113 `commit-gate` + **55 `pre-commit`** + 1 manual。`in_process_gate_registry.yaml` 那 113 条与前者的 113 条全等、与这 55 条**交集为 0**。而三条合法通道全部 `git commit --no-verify`（`D:\ZephyrAlpha\src\zephyr\gov_enforcement\rule_bridge\git_commit_gateway.py:3115,3117`、`D:\ZephyrAlpha\scripts\session_worktree.py:3857`、`D:\ZephyrAlpha\src\zephyr\gov_enforcement\rule_bridge\commit_queue_landing.py`），全仓 grep **找不到一处** `pre-commit run`。
- **为什么要你点头**：修它要么把 55 台并进 in-process 注册表（＝一次净增 55 条门禁语义，触 §4.1 规范预算），要么在网关落地前加跑 `pre-commit run --all-files` 的 staged 口径（＝改提交主链路、影响所有人吞吐）。两条都不是机械活。
- **不点会怎样**：`GATE-ARCH`/`GATE-NAMING`/`GATE-SSOT-CODE`/`GATE-TRIPLE-ALIGN` 等 55 台继续**只在有人违规裸提交时才咬**。越守规矩的 AI 越免检。
- **附带加固**（A2 独立撞出，双路同结论）：正因网关 `--no-verify`，`check_protected_paths.py --staged` 这第二层**根本不执行**，受保护路径唯一实拦只剩读 message 标记的 Layer-1 ⇒ **"受保护"的实际强度＝有没有人诚实写 `[ARCH-APPROVAL]`**。

**夜裁-02【Owner】｜3 条门禁 entry 补 `--ci`（P0-3）**
- `GATE-SRC-NO-DATA`(`check_src_no_data.py:124-135`)、`GATE-VMS-SSOT`(`check_vms_ssot.py:236-238`)、`GATE-BP-PLACE`(`validate_blueprint_placement.py:271-276`) 三台"仅 `--ci` 才阻断"，而注册表 entry 恰好没带 `--ci`＝**双重保险丝全断**。修法是一行注册表数据，但**翻转阻断属"flag 出厂翻转"门位**。
- 不点：这三台继续只打印不拦。附带：`check_src_no_data` 前缀真源只有 `src/data/`，`src/zephyr/data/` 逃逸在其宣称范围外；契约文件缺失时 `FORBIDDEN_PREFIXES=()` 静默全放，注释自称"fail-closed 例外"实为 fail-open。

**夜裁-03【Owner】｜删除类一次性打包（本夜班一件未删）**
- ① `.tmp` 残留 **137 件 / 82.7 MB**（A3 时测 46 件/86.6MB，dev 在动），集中在 `D:\ZephyrAlpha\.runtime\tmp\**`；其中 CAS 原子写残留 `.yaml_<rand>.tmp` 落在 `_registry/catalogs`(40)、`scripts*`(5)、`config`(1)，全 gitignored、0 被跟踪。
- ② 唯一**真岛** `D:\ZephyrAlpha\src\zephyr\alt_data\cohort_daily_ledger.py`（域 D_ALT_DATA）：生产 import=0、无 boot_hook、无 task/config 接线，`__init__.py` 里只是 `__all__` 惰性模块名字符串＝运行时死代码。
- ③ 0 字节残壳 `D:\ZephyrAlpha\tests\signal_ashare\test_sector_strength_aggregator.py`（09-13 `git rm` 后留盘）。
- 不点：继续占 82MB 且 `TEMP_FILE_PATTERNS` 缺 4 类模式导致今晚真垃圾**全部漏检**（见夜裁-13）。

**夜裁-04【Owner】｜N-16 白名单加 `algo_flow`（消 609）**
- C-04 阻断 636 去重后 203 组，其中 **606 件是 `docs/03_modules/**/algo_flow/` 镜像卡的必然结果**（实测 100% 位于名为 `algo_flow` 的目录）。加一项白名单即 636→27。
- 真源：`D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\`（trae_028 §n16_config.`skip_dirs_docs`，代码动态加载、改 YAML 即生效）。
- 不点：22 域每轮都要在 636 里挑 27 件真活，白噪音淹掉真问题。

**夜裁-05【Owner+Max】｜`--tracked-only` 扫描口径（一条裁定治四张卡，P0-4）**
- 病根：D1/D3 检查器一律扫**磁盘工作树**，而本仓 `.gitignore` 用 `/*` + 显式反选的**白名单模型** ⇒ 结构性"扫得到但提交不了" ⇒ C-02（18 全在 ignore 区，跟踪面债务 **0**）/C-07/C-08（9/9 untracked）/C-09a **同时恒红**。
- 加 `--tracked-only` 口径可一次归零这四张卡的假红。不点：每张卡都要各自解释一遍"为什么绿不了"。

### 第二梯队：规则面（WP9 判案相关）

**夜裁-06【Max】｜`rules/` 面 29 条重指放行**——成品已备好双份：`D:\ZephyrAlpha\docs\_working\rule_audit_campaign\a2_handoff\rules_m1_repoint.patch`（16 文件 42+/42−，`git apply --check` 通过；附 `rules_repoint_rows.json` + `genpatch.py` 可重生）。夜班按 D-14 自行停手，且 `architecture_issue_registry.yaml` 内**无本战役议题**，借无关 ISSUE_ID＝伪造审批指向。要你先判：WP9 提前 or 先补合法 ISSUE_ID。不点：16 份条文继续把 AI 指向不存在的文件（夜班已现场验证按旧路径跑必崩）。

**夜裁-07【Max】｜②类 5 条把 `_archive/` 件当现役**（trae_032 `assign_module_id.py`、trae_034/035、trae_055 `audit_domain_nodes.py`）——这不是搬家是退役，改指向＝替 Owner 决定"这工具还要"。
**夜裁-08【Max】｜③类 7 条引用"真被删且无后继"**（trae_036 `validate_phase_transition.py`→`f57016319e`；trae_044 `score_architecture.py`→`c441a1fca5`；trae_053 `ide_health_service.py`/`ide_health_daemon.py`→`6fe7e96dfc` 2026-08-28 僵尸系统裁定清除；trae_083）→ 按程序法走 **D3/D4**（选 D4 须同时上报"登记环节不校验强制体存在性"这条流程缺陷）。
**夜裁-09【Max】｜`TRAE-079` 判 D4 还是 C 加牙**——其 `paired_gate_id: COMMIT-CRITICAL-SECTION-LOCK` 两册零候选、全仓 grep 只命中条文自身与本战役文档＝**从未存在**。不判：这条"有牙"是假的，弱模型会以为它拦过。
**夜裁-10【Max】｜M4 结构性风险档（86/86 份补不了）**——`D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\risk_tier_registry.yaml` 真键是 `domain_tiers` 18 条（**不是 `entries`**，按 `entries` 取得 0；案卷口径需更正），域清单无 `TRAE`；86 份规则 `domain`＝'TRAE'×83 + None×3；`rule_catalog_registry.yaml` 的 86 条 trae 行**根本没有 domain 字段**；`functional_domain_registry` 里 D_GOVERNANCE/D_GOV_DOCS/D_GOV_RULE/D_GOV_SCRIPTS 多候选 ⇒ 唯一读出失败。要定"TRAE 条文归哪个域"。不点：风险档恒落 default low → 闸4"退化方向应然"永远失明（曾报 1401/1404 的真根因，不是漏填）。
**夜裁-11【Max】｜T-4 规则自相矛盾 227 件**——ALGO_FLOW 卡要求继承上游锚值，但上游是被 `trae_047` `gov_eng_002_exempt` **明文豁免的 `__init__.py`**。判"卡随上游豁免" or 改豁免面；不可代填。
**夜裁-12【Max→Owner】｜T-3 ALGO_FLOW 5 栏方向**：2993 件卡自带 `source_of_truth` 可机械 join（抽样 400/400 目标存在、400/400 有该键），但**现有三件 backfill 工具均不覆盖**、需新造 join 生成器。先裁"补头"还是"卡随 rule 分型豁免"（trae_047 自陈 B_yaml 适用面＝gate/registry/contract/config/data，这些卡 `doc_type: architecture_view` 不在其内）。
**夜裁-13【Max→Flash】｜闸2 判据本身要改**：曾报 32、实测命中 34 但**真规范位只 21＝38% 误报**（名词位"AI 建议止损"、防御条款自引用 trae_042 禁词表本身含"建议/尽量"、术语定义位）。处方全文 `D:\ZephyrAlpha\docs\_working\rule_audit_campaign\a2_handoff\A2_M5_prescriptions.md`。不点：T0 机械波会把 13 处假违规当真活去做。
**夜裁-14【Max】｜`TEMP_FILE_PATTERNS` 补 4 类模式**（`\.tmp$`、`^_probe_`、`^commit_msg`、`^pytest_`）——这是"加牙"，**且补完后红数会从 770 跳向 810+/3014**，要一并决定是否同批改卡片口径为 tracked-only。

### 第三梯队：裁判失明面

**夜裁-15【Max】｜`gate_auto_registrar.py:121-170` 装载器 fail-open（P0-2）**——in-process 门禁 import/factory/register 失败只进 failures + `logger.warning`，提交照走；**装载数≠名册数无人报警**。对照组可抄：`commit_gate_registry.check_all` 单 gate 异常即 fail-closed。
**夜裁-16【Max】｜`check_encoding.py` 对 GBK/不可解码源文件恒绿（P0-6）**——`check_file_encoding` 里 `except UnicodeDecodeError: pass`。**收紧会点亮存量红**，属门位，故夜班未动。
**夜裁-17【Max】｜网关三处兜底在坏场景自动放行（P0-7）**——`git_commit_gateway.py:1717-1748` SSoT 兜底在 `capability_lookup` 不可用时 `return (True,…)`；`:2362,3396` `_GlobalCommitLock` 不可用→fail-open 继续 commit；`:3584` 幻影签名"带引号的路径跳过"。另 LSG `gateway.py:123,307,327,343,364` 的 `FAIL_OPEN_LAYERS={l6_observability,l7_validation}` **硬编码默认放行、无配置可关**。
**夜裁-18【Max】｜观测面永久失明的存量门禁 9 台（P0-5）**——`check_generator_no_realtime_time`、`check_no_commit_derived`、`check_src_no_data`、`check_vms_ssot`、`check_no_tests_unit`、`verify_dedup`（+`check_protected_paths` 半合理、2 台事件型可接受）＝观测面只有 staged 且**无全树能力**，历史存量对它永久不可见。
**夜裁-19【Max】｜`generate_missing_index_md.py` 在 worktree 恒绿（P0-8，夜班亲测坐实）**——`:294` 用 `dirpath.parts` 判隐藏目录，parts 是绝对路径分段 ⇒ 检出在 `.worktrees/` 下时**每个目录都带 `.` 段全被 skip**。工棚内输出 `OK: 扫描 0 个目录，全部已含 index.md`，主区同工具 `将处理 1002 个`。**提交队列 serializer 正跑在这条通道上**。修它＝当场暴露净增欠账，故与夜裁-20 联动判。
**夜裁-20【Max】｜缺 `index.md` 净增规模（**必须带口径**）**——工具口径 1002（含未跟踪/被忽略如 `docs/_working/投资账本截图/`、≥1 件）；tracked∧≥2 件＝**344**；其中临时区 `docs/_working` 108；**永久区真欠账 ≈233**（`03_modules` 215 + `01` 11 + `02` 7）。批哪个数、建不建，取决于你认哪个口径。

### 第四梯队：其余在册待办

**夜裁-21【Max】｜`check_index_integrity.py` 判据要重造（P0-9）**——递归 basename 判据致：①跨目录正确链接全误报（含 6 条指 `.py/.json`，`get_sibling_files` 只收 md/yaml → **永远红**）②真断链漏报（`knowledge_article_registry.yaml` 改名进 `_archive/` 后该门一声不吭）③把 frontmatter 与版本史正文当索引清单。铁证：**A7 改 35 行真内容，门计数 517→517 纹丝不动 ⇒ 它不能当验收证据**。同族：`validate_cross_references.py:642` 对 `file:///` 直接 `continue`。
**夜裁-22【Max】｜`blueprint_registry.yaml` 的"SSoT"行怎么处置**——`docs/03_modules/index.md:91` 仍称其为 SSoT，但双盘均不存在（`.gitignore:574`、`03df6215e8` 派生退库）。选项：指生成器 `sync_registry_from_blueprints.py` / 删行 / 承认"派生件不配称 SSoT"并改写措辞。
**夜裁-23【Max】｜WP17 未施工**——对抗校验器恒真（`blocked_rate` 恒 1.0、零区分度）修法，处方三条已在本战役 ledger；D-18 已立法（`0315d5555d`）但修复未做。
**夜裁-24【Max】｜归档面免断链普查**——`agent_constitution_legacy_v1.md:522` 引用已迁移模块（后继在 `infrastructure/pipeline/`）；`data/reports/dm018/dm020` 历史战报里的旧路径。归档自称"零内容丢失"、历史战报属审计轨迹，**改它＝改历史**。建议登记"归档/历史面免断链普查"豁免面。另需定：施工 SOP 里 `python scripts/git_commit_gateway.py`（同文件 L29/L610）该路径全史从未存在，合法后继二义（`scripts/git_commit.py` CLI vs 模块路径）→ 官方提交入口写法。

## 六、后续工作清单（施工序，Max 裁定后照此派 Flash）

**W1｜身份键地基（WP1，Max 主导，Flash 打下手）**
- `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_verifier.py` 静默空转（读 `gate["result"]` 而活库 `gates` 真列是 `gate_run_id/gate_id/passed/details/artifact_path/session_id/task_id/created_at`）——**注意：此件现由 `st-ramp-wp1b` 在途持有，勿碰**，夜班实测其 index 比 HEAD 大 +6218 字节＝前进中工作。
- 三套命名空间：YAML 册 169（`ALGO-FLOW-LINK` 族）／`governance.db` 的 `gates`+`gate_runs`（`G0:CP-*`、`G7:OPS-*`、`G_TRAE_nnn:DM-nnnnnn` 族，与 YAML 册**交集 0**）／`reconcile_execution_log` 63 身份（交集仅 3）。后果＝"这条规则近 90 天触发几次"算不出来 → 宪法 §4.2 季度退役审计**结构上跑不起来**。
- `gate_decisions` 0 行的真根因＝**零调用者**（不是 INSERT 坏；`gate_persistence.py` 写的是 `data/drift_audit/drift_events.db`，列名匹配，该"必失败"论断已被施工队证伪并划掉）。

**W2｜WP8→WP9 判案链**：案卷 v1 有 1404 份（**先查 staging TTL 是否还在**），WP8 需按 D-6 收窄判据重出 v2，再走六道闸判案（六档序）。

**W3｜T0 机械波正式开**：卡片可用性已从 6 张扩到 **18/19 张**（唯一不可用＝修前的 `detect_orphan_py`），故 **D-10 需更新**。开波前先落夜裁-04/05/13/14 的口径，否则弱模型会在假信号上空转。

**W4｜派单必须照抄的三条姿势纠错**（夜班实测）
1. `git_commit.py` **没有** `--base-head`（属 `commit_queue.py enqueue`）；带上直接 `unrecognized arguments` → exit≠0。
2. 正确入队形：`cd /d/ZephyrAlpha && python scripts/commit_queue.py --queue-root .runtime/commit_queue enqueue --session <sid> --files-file <清单> --message-file <件> --worktree-root <wt> --base-head $(git rev-parse dev)`
3. `lock_files.py acquire` **必须在主仓 cwd** 跑；在 worktree 里跑 claim 会落进 worktree 私有 `.ailocks/registry.json` → 落地侧 `CLAIM_REQUIRED_VIOLATION` 死信。

**W5｜worktree 收尾（WP15 第 1 件，仍欠）**：`st-ruledisp-20260918`、`st-auditdoc-v4-20260918`、`AI-NIGHT-CF1-001` 三个待拆。
- CF1 工棚那 8 个文件的**未提交陈旧副本不可整批回灌**（落后 dev，会回退他人后续落地）；补丁已备份 `D:\ZephyrAlpha\.runtime\tmp\cf1\backup\`，功能等价性已用实测口径证明，建议直接丢弃。
- 收尾三连：①按 cmdline 精确核 PID 后 terminate 自己的 heartbeat_daemon ②`SessionRegistry(仓根).unregister(sid)`（真路径 `zephyr.security.access_control.session_concurrency`）③再 abort；OPS-GUARD 禁 in-process 删 `.worktrees/**` 属正确姿态，勿加 `--force-skip-checks`。

**W6｜记忆文档 A/B 班（还没开）**：按 D-8 抄 ARCH-310 R3 双基准法，**必须有 C 组阳性对照、n≥3**；盘点面 `C:\Users\fanzi\.qoder-cn\memory\`（user+project 两级）、`.claude\`、`.cursor\`、`D:\ZephyrAlpha\.trae\rules\project_rules.md`（520 行）与 `D:\ZephyrAlpha\AGENTS.md`（140 行）**常驻注入重叠率无人测过＝§2.2 双份承载嫌疑**。硬线：简化版效果必须 ≥ 原版。

## 七、并发与避让（日班开工前重测，勿背夜班数）

- 夜班开工时活跃 claim 18 件、心跳 <30min 仅 `st-bizmine-pb`；全程未碰他人文件、未与施工队发生一次冲突。
- **另处置**：主区曾存在 168 条陈旧暂存条目（90 条 INDEX<HEAD＝回退炸弹），已按 Owner 授权 `git reset --pathspec-from-file` 复位 167 条（主动排除 2 条在途件），**169/169 工作区字节+SHA256 与复位前快照全等、零内容丢失**；剩 2 条仍归在途会话。
- **唯一炸点机理**：`git_commit_gateway.py:3071` 检测 MERGE_HEAD → git 禁合并期 partial commit → 强制全量 commit 收编全部 staged；该处只 `logger.warning` **不阻断**。日常提交由 `_unstage_non_target_files` 自愈。⇒ **施工队每次合并收尾前，自己那批之外的陈旧暂存条目都是风险**；日班开工先重跑一次"回退炸弹"检测（脚本口径见报告 §七）。
- 开工三连实测命令：`python scripts/lock_files.py list`、`ls .runtime/locks/heartbeat_*.pid`、`python scripts/commit_queue.py status`。

## 八、夜班认的账（不确定处，别当结论用）

1. C-13 只抽 15 个候选（512 未穷尽）；C-17 全量清单在 `.runtime/tmp/redlab_a1b/c17_unowned.txt`（**TTL 面，先抢救**）。
2. C-05/C-18 未做按域细分（A3 派单只含 T1–T4）。
3. DEPENDENCIES/CONSUMERS 能否 100% 由 depgraph 反查**未实测** → ②档定级偏保守（若可反查则 795 中约 51+32 件可升①）。
4. A5 有 5 台"有测试但零负向断言"的门禁**未能逐台实弹红证**（真红需写被跟踪派生册或造 worktree，撞只读硬约束）→ 标 `[推断-不可测]`。GATE-ARCH 19 子项、GATE-INTEGRITY 子进程面未逐台开牙验。
5. 计数漂移（1264→1263、orphan 313,763→322,189、`.tmp` 46→137 件）均归因并发会话在途写入＋dev 前进，夜班样本全在 `.runtime`（各卡源码显式 skip 该区），未取到具体肇事会话。
6. 一次注入面登记：夜班运行中出现过注入他会话 worktree 的 `AGENTS.md` 与 `MEMORY.md` 变更通知，一律按数据处置、未据此改变任何动作；全部读取面扫诱导字样命中 5 处，**均为防御规范自身的样本串**（`audit_prompts_20_ai.md:63` 抗注入条款本体 + LSG/蓝图判定表），无一处指向执行腿。
7. 工具链误伤待办：红样经 bash heredoc 两次被本仓 echo-guard 拦截/改写（`\\` 被吞成 `\`），改用 python 写入才可靠——**审计/施工管道对该守卫的误伤需要预案**。
8. **`rules_enforcement_census.json` 等三件普查件已被 `.runtime/sessions/*/staging/` 的 24h TTL 吃掉**，A2 只能全仓重算（重算结果与曾报数差数倍，见夜裁-10/13）。⇒ 教训：取证/成品落地后必须立即复制到 git 跟踪区或随 commit 入库。
