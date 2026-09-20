---
ttl: task_bound
title: 通宵 Flash 班·问题范围锁定与待 Max 裁定清单
---

# 通宵班回执（2026-09-19 04:00–07:30，Flash 执行）

> 本文件的定位是**范围锁定**，不是结论签收。Owner 睡前指令：能机械判的全做、简单语义 Flash 裁、复杂的留 Max；
> 不与在途施工队冲突；`docs/_working/` 既有内容一律未动（本文件是新建立件）。
> **证据等级**：`[亲验]`=本班亲自跑出的命令+输出；`[转报]`=读码或读产物推断；`[推断]`=口径推定未复测。

## 一、一句话总览

18/19 张机械检查卡已证红可用（双向），全仓违规范围已量化锁定；**最大发现不是文件脏，而是裁判体系有两处结构性失明**——
55 台 pre-commit 门禁在全部合法提交通道上零执行权，以及门禁装载器自身 fail-open 可静默丢门禁。
6 项裁判缺陷已治本落地（3 笔 commit），并顺带证伪了 5 个"看着吓人"的数字。

## 二、卡片可用性与全仓基线（实测）

| 卡 | 检出面 | 基线 | 判定 |
|---|---|---|---|
| C-01 表头 | `verify_header_completeness.py` | 缺栏 4241 / 无头 315（工具按设计跳过＝盲区） | 可用 `[亲验]` |
| C-02 frontmatter | `check_frontmatter_metadata.py --all-files` | 18 hard-block | 可用（**18 全在 ignore 区，跟踪面债务=0**） |
| C-03 词表硬编码 | `check_vocab_hardcode.py --ci` | 5 | 可用 |
| C-04 命名 | `check_naming_convention.py --scan` | 涉事文件 636 → 去重 203 组；warn 1788 | 可用 |
| C-05 编码 | `check_encoding.py --dir` | 抽 3 目录 FAIL 0 | 可用但**对 GBK 源文件失明** |
| C-06 目录容量 | `audit_directory_scalability.py` | 0 err + 2 warn | 可用 |
| C-07 索引 | `check_index_integrity.py` | 1263（MEDIUM 752 / LOW 511，LOW 被 `[:20]` 截断，真值 4966） | 可用但**95% 是假信号** |
| C-08 目录契约 | `check_directory_contract.py` | 9 error | 可用（**9/9 untracked+ignored，跟踪面=0**） |
| C-09a 临时件 | `detect_temp_files.py` | 770 | **修复前不可采信**（相对口径条件恒绿） |
| C-09b 残留 | `detect_residual_files.py` | 0 | 可用（`--warn-only` 下恒 exit 0，须读行数） |
| C-09c 孤儿 py | `detect_orphan_py.py` | 330,615（真孤儿 0） | **已修**（见 §三） |
| C-10 错误码 | pytest 一致性 | 1 违规 `ZA-INF-RT-ADM` | 可用 |
| C-11 五图对齐 | `align_all.py --no-report` | exit 1：硬 19 / 软 698 | 可用（19 硬全在图10 派生册过期） |
| C-12 depgraph | `diagnose_depgraph.py` | orphan_nodes=512 | 可用（**512 严重高估**） |
| C-13 岛模块 | 四步判据抽 15 | **真岛 1 件** | 可用但高噪 |
| C-14 克隆 | `clone_guard_audit.py` | findings 4，健康分 D，3505 文件 | 可用 |
| C-15 fail-open | `generate_fail_open_register.py --check` | 盘上 1595 vs 现算 1610 = DRIFT | 可用（**分母是 token 级不可当规模**） |
| C-16 登记三连带 | `audit_registration.py --full` | 58（24 孤儿模块+27 孤儿脚本+2 孤儿门+1 僵尸引用+4 路径不符） | 可用 |
| C-17 无主路径 | 现场 `git ls-files`×22 域锚点 | 差集 67 → 真无主 52 → 净欠账 37 | 可用 |
| C-18 纯陈述 | `check_pure_assertion.py --full-scan` | 117 | 可用 |

## 三、已治本落地（3 笔 commit，全在 dev）

| commit | 内容 | 亲验证据 |
|---|---|---|
| `bdc21c8811` | 孤儿检测豁免 `.aidrafts`/`.worktrees` + 摘 `--fix` + 扫描入参口径收进 `_shared/walk.py` 单一真源 | 主仓孤儿数 330,615 → 真值 0（原为会话工作树副本被误判） |
| `3a67233f41` | `detect_threading_lock` / `detect_vague_terms` 接入新口径 | 见下行统一实测 |
| `0406b66fce` | `detect_ruins_references` 接入新口径 | 同上 |

**修后统一直测**（本班亲自跑）：4 台检测器 `--scan-dir` 传**绝对路径**与**相对路径**输出**逐字同数**（例：`detect_shell_true` 两种口径均 `Scanned 2 Python files, 1 findings`，exit 1）。修前同一样本相对口径报 `0 findings / exit 0`＝**条件恒绿**。 `[亲验]`

一处施工队遗留须知晓：工棚 `.worktrees/AI-NIGHT-CF1-001` 有 8 个文件的**未提交陈旧副本**（落后 dev），**不可整批回灌**（会回退他人后续落地）。补丁已双份备份至 `.runtime/tmp/cf1/backup/`，功能等价性已用实测口径证明，建议直接丢弃。

## 四、P0 结构性发现（交 Max/Owner，本班未动）

### P0-1｜55 台 pre-commit 门禁在全部合法提交通道上零执行权 `[亲验]`
- 名册实测：`gate_registry.yaml` 169 条 = 113 `commit-gate`（in-process）+ **55 `pre-commit`** + 1 manual。
- `in_process_gate_registry.yaml` 113 条与前者 113 条**全等**，与那 55 条**交集 = 0**。
- 三条合法通道全部 `git commit --no-verify`：`git_commit_gateway.py:3115/3117`、`session_worktree.py:3857`、`commit_queue_landing.py`；全仓 grep **无任何** `pre-commit run` 调用点。
- 后果：`GATE-ARCH`、`GATE-NAMING`、`GATE-SSOT-CODE`、`GATE-17`、`GATE-TRIPLE-ALIGN` 等 55 台**只有走裸 `git commit`（违宪路径）才会咬**。越守规矩的 AI 越免检。
- **A2 腿独立取证的加固**（它不知道本条已立案，另路撞出同一结论，故置信度提升）：因为网关自身以 `--no-verify` 出仓，`rules/` 的第二层防线 `check_protected_paths.py --staged` **在网关通道上根本不执行**，受保护路径的唯一实拦只剩 Layer-1 `PROTECTED-PATHS`（它读 commit message 里的 `[ARCH-APPROVAL]` 标记）——**即"受保护"的实际强度＝有没有人诚实写那个标记，而不是有没有第二道校验**。 `[亲验×2，双路独立]`
- 处方二选一：①把 55 台观测语义并入 in-process 注册表；②网关落地前跑 `pre-commit run --hook-stage pre-commit --all-files` 的 staged 口径。并给 `gate_registry` 加 `enforcement_channel` 字段防再生。

### P0-2｜门禁装载器 fail-open，可静默丢门禁 `[亲验]`
`gate_auto_registrar.py` L121-170：in-process 门禁 import/factory/register 失败仅进 failures 列表 + `logger.warning`，提交照常走；**装载数 ≠ 名册数无人报警**（名册 113，实装 <113 静默）。对照组好设计：`commit_gate_registry.check_all` 单 gate 异常即 fail-closed。

### P0-3｜3 台门禁"仅 `--ci` 才阻断"而注册表 entry 没带 `--ci`＝双重保险丝全断 `[亲验]`
`GATE-SRC-NO-DATA`(`check_src_no_data.py:124-135`)、`GATE-VMS-SSOT`(`:236-238`)、`GATE-BP-PLACE`(`:271-276`)。修法是一行注册表数据，但**翻转阻断属"flag 出厂翻转"门位 → Owner**。
附：`check_src_no_data` 前缀真源只有 `src/data/`，`src/zephyr/data/` 逃逸在门禁标题宣称范围外；契约文件缺失时 `FORBIDDEN_PREFIXES=()` 静默全放，注释自称"fail-closed 例外"实为 fail-open。

### P0-4｜跨卡共因：检查器扫磁盘工作树，而 `.gitignore` 是白名单模型
"扫得到但提交不了"的面结构性恒红。加 `--tracked-only` 口径（或对生成区/`_working` 统一 zone 豁免真源）可一次归零 C-02/C-07/C-08/C-09a 的假红。这是**一条裁定治四张卡**的杠杆点。

### P0-5｜观测面永久失明的存量门禁 9 台 `[亲验]`
`check_generator_no_realtime_time`、`check_no_commit_derived`、`check_src_no_data`、`check_vms_ssot`、`check_no_tests_unit`、`verify_dedup`（+`check_protected_paths` 半合理、2 台事件型可接受）——观测面只有 staged 且**无全树能力**，历史存量对它永久不可见。

### P0-6｜`check_encoding.py` 对 GBK/不可解码源文件失明 `[亲验]`
`check_file_encoding` 里 `except UnicodeDecodeError: pass` → 真·非 UTF-8 的 .py 恒绿（对 mojibake 标记有牙、对退化类失明）。处方：`.py/.md/.yaml` 不可解码即报 INJ-007 FAIL。**收紧会点亮存量红 → 属门位**。

### P0-7｜`git_commit_gateway` 两处兜底在坏场景自动放行 `[亲验行号]`
L1717-1748 SSoT 兜底门禁在 `capability_lookup` import/init 失败时 `return (True, …)`；L2362/3396 `_GlobalCommitLock` 不可用 → fail-open 继续 commit；L3584 幻影签名"带引号的路径跳过"。LSG `gateway.py:123/307/327/343/364` 的 `FAIL_OPEN_LAYERS={l6,l7}` 硬编码默认放行、无配置可关。

## 五、被证伪的"吓人数字"（**这些不该动**，动了就是与规则对赌）

| 表面数字 | 真相 | 依据 |
|---|---|---|
| C-01 缺栏 4241 | 缺的不是"15 栏"而是 5 个 YAML 锚栏（stability 4031/ai_autonomy 3981/safety_level 3405/blueprint_id 3404/module_id 3316）；`ttl` 缺口实测 **0**；**77.6%（3293 件）集中在 `docs/03_modules/**/algo_flow/*.yaml`**，而 trae_047 自陈 B_yaml 适用面不含 `architecture_view` → 是工具全量套栏对规则分型适用的**外溢** | `[亲验]` |
| C-04 命名 636 | 语义是"涉事文件数"非违规数，去重 203 组；其中 **606 件是 algo_flow 镜像卡的必然结果** → 白名单加 `algo_flow` 一项即 636→27（属 Owner 白名单门位） | `[亲验]` |
| C-07 索引 1263 | **717 条（95%）是工具缺陷**：`extract_index_entries` 未剥 `#锚点`，且量集中在一个 gitignored 生成区 | `[亲验]` |
| C-09a 临时件 770 | **100% 是工具缓存**（767 `__pycache__` + 3 根缓存），真垃圾 0；且它连缓存都没数全（767 vs 实存 810 vs 含隐藏区 3014）——`EXCLUDE_DIRS` 把 `data`/`models` 当任意层级名剪枝 | `[亲验]` |
| C-02 18 / C-08 9 | 全在 gitignored 或 untracked 面 → **正常跟踪面上债务为 0**，改动会被 ignore 吞掉，零收益 | `[亲验]` |
| C-12 孤儿 512 | 抽 15 个实核仅 **1 个真岛**；6 个是 depgraph 缺边假孤儿、2 个由 config 动态挂载、3 个设计性一次性 CLI、1 ghost | `[亲验]` |
| C-15 fail_open 1595/1610 | 分母是 token/行级（含 29% 注释与 doc）；AST 扫 `fail_open` 标识符节点 = **0** → 该数**不可当"真吞点规模"** 引用 | `[亲验]` |
| 普查曾报 "63 声明 fail-open / 103 未声明" | **不可复现**：`gate_registry.yaml` 根本没有退化方向字段，169 条 description 提及 fail-open/fail-closed = 0 → 该普查数字作废 | `[亲验]` |

同时须反向警惕：**修好工具后红数会变大，那不是变坏**（orphan 330,615→真值；temp 相对口径 0→477；`detect_temp_files` 补模式后 770→810+/3014）。

## 六、真欠账（晨班可立即接手）

| # | 项 | 件数 | 性质 | 谁能做 |
|---|---|---|---|---|
| T-1 | 真垃圾待删：CAS 原子写残留 `.yaml_<rand>.tmp` **86.6 MB**（`_registry/catalogs` 40 / `scripts*` 5 / `config` 1，全 gitignored、0 被跟踪）+ 1 个 0 字节残壳 `tests/signal_ashare/test_sector_strength_aggregator.py` | 47 | 删除 | **Owner 门位**（本班一件未删） |
| T-2 | `TEMP_FILE_PATTERNS` 缺 `\.tmp$`/`^_probe_`/`^commit_msg`/`^pytest_` 四类 → 上述真垃圾今晚全漏检 | 1 文件 | 裁判加牙 | Max 裁定后 Flash 施工 |
| T-3 | ALGO_FLOW 卡 5 栏 join-fill：2993 件可从上卡自带 `source_of_truth` 机械 join（抽样 400/400 目标存在、400/400 有该键），但**缺一个 join 生成器**（现有三件 backfill 均不覆盖） | 2993 | 需新造工具 | **先裁定"补头"还是"卡随上游豁免"**，再谈造器 |
| T-4 | 227 件卡的上游是被 trae_047 明文豁免的 `__init__.py` → 卡要求继承其锚值 vs 上游被豁免，**规则自相矛盾** | 227 | 立法冲突 | Max |
| T-5 | tests 同名 12 组 24 件改名（逐组建议名+引用面已实测：保 SUT 目录匹配侧、不匹配侧加子系统前缀）；其中 2 组是同 SUT 近重复测试→转 dedup，1 组随 T-1 删除自动消解 | 12 | `git mv`+depgraph 重建 | Flash 可做，须同步 `generate_project_depgraph.py --force` |
| T-6 | C-16 登记债 58（24 孤儿模块+27 孤儿脚本+2 孤儿门+1 僵尸引用+4 路径不符） | 58 | 机械补登为主 | Flash（③档语义除外） |
| T-7 | C-10 真漂移：`src/zephyr/infra_runtime/runtime_admission.py:89` 定义的 `ZA-INF-RT-ADM` 未登记进 `error_code_registry.yaml`，两文件在 HEAD 均 clean＝**已提交的真漂移** | 1 | 机械补登 | Flash（热文件须 CAS） |
| T-8 | C-11 图10 gomap 派生册过期（19 硬漂移，抽验 6 文件磁盘 clean）→ 重跑 `generate_governance_map.py` | 19 | 派生重建 | 晨班（写被跟踪派生册，宜错峰） |
| T-9 | C-15 fail_open_register 盘上过期的 1595→1610 → 主仓重跑生成器 | 1 | 派生重建 | 晨班 |
| T-10 | 唯一真岛 `src/zephyr/alt_data/cohort_daily_ledger.py`（域 D_ALT_DATA）：生产 import=0、无 boot_hook、无 task/config 接线，`__init__.py` 里只是 `__all__` 惰性模块名字符串 → **运行时死代码岛** | 1 | salvage/退役 | **Owner 删除门位** |
| T-11 | 无主路径净欠账 37 条（`strategy_factory/` 17、`strategy_pipeline/` 11、`ai_layer/` 7、`tools/desktop/` 2）；另 15 条（`infra_runtime` 9+`infra_ops` 6）实为**第2章锚点表↔registry 投影漂移**，补锚即收编 | 37+15 | 归属 | Max 定归属，Owner 追认 |
| T-12 | C-18 文档过渡语 117 条（大量 `candidate_modules/*.md` 与蓝图文） | 117 | 机械删过渡文本 | Flash |

## 七、在途施工队交叉面（避让登记）

- 开工时活跃 claim 18 件（`st-ramp-wp1b` 4、`st-bizmine-inda/-indb/-indc/-tick/-tickm/-pb/-pat` 等），全程未碰其文件。
- 本班另处置：主区曾存在 **168 条陈旧暂存条目（90 条 INDEX<HEAD＝回退炸弹）**，已按 Owner 授权用 `git reset --pathspec-from-file` 复位 167 条（主动排除 2 条在途件），**169/169 工作区字节+SHA256 与复位前快照全等，零内容丢失**。剩 2 条回退炸弹仍归在途会话。
- 唯一炸点机理：`git_commit_gateway.py:3071` 检测 MERGE_HEAD → git 禁合并期 partial commit → 强制全量 commit 收编全部 staged；该处只 `logger.warning` **不阻断**。日常提交则被 `_unstage_non_target_files` 自愈。

## 八、A2 腿（规则条文施工）回执并入

### 落地两笔（总控亲自复核在 dev）
| commit | 内容 | 实测复跑效果 |
|---|---|---|
| `40bfe9a7c8` | 施工 SOP `construction_workflow_policy.md` 3 处 `diagnose_depgraph.py` 旧路径重指现址 | 断链 58→56、distinct 46→45 |
| `3450edb560` | 施工图模板 `check_blueprint_compliance.py` 重指 `d3_metadata/` 现址 | 断链 56→55、distinct→44 |

真源证据＝`git log --follow --name-status` 判 `R100`（100% 纯移动、唯一后继），属机械可定值。总控复测：`scripts/governance/diagnose_depgraph.py` 旧串在 tracked 面还剩 20 个文件，其中 **18 处正好包含在 A2 已备好的 29 条重指 patch 内**（属 `rules/` 冻结面），另 2 处是 `data/reports/dm018/dm020` 历史战报——**该豁免不该修**（同 §8 归档面问题）。 `[亲验]`

### A2 停手停对了（重要）
`rules/` 面 29 条同类重指**做成成品但未落地**，堵因不是门禁红信而是**我自己立的 D-14 冻结**（`rules/` 全域冻结到 WP9 判案完成）＋`architecture_issue_registry.yaml` 里无本战役议题，借无关 ISSUE_ID 等于伪造审批指向。成品双份留存并已抢救：
`docs/_working/rule_audit_campaign/a2_handoff/`（`rules_m1_repoint.patch` 19KB，16 文件 42+/42−，`git apply --check` 通过；附 `rules_repoint_rows.json`+`genpatch.py` 可重生；`A2_M5_prescriptions.md` 21 条二值化处方）。
**原位置在 `.runtime/sessions/<sid>/staging/`，24h TTL 会吃掉——已复制到 git 跟踪区。** `[亲验]`

### A2 对普查数字的现场更正（案卷引用件已被 TTL 蒸发，全部现场重算）
| 项 | 曾报 | 实测 |
|---|---|---|
| M1 执行体路径写错 | 9 条 | **41 条/19 份**（①可重指 29 条/16 份、②归档件 5 条、③真删无后继 7 条）+ 裸文件名 12 条（唯一可解析，非缺陷） |
| M2 `paired_gate_id` 对不上两册 | 案卷闸0 804 | **只 1 条**（TRAE-079）——两册实测 169/113 且 `in_process ⊂ gate_registry`，故"对不上两册"≡"不在 gate_registry" |
| M3 无 `executors` | 21 | **21 份**（15 空列表 + 6 缺字段） |
| M4 风险档落 default | 1401/1404 | **86/86 份不可补**：`risk_tier_registry.yaml` 真键是 `domain_tiers` 18 条（**不是 `entries`**，按 `entries` 取会得 0，案卷口径顺带更正），域清单无 `TRAE`，catalog 86 条 trae 行根本没有 domain 字段 |
| M5 闸2 词表命中 | 32 | **34 命中但真规范位仅 21（38% 误报）**：名词位/"AI 建议止损"、防御条款自引用（trae_042 禁词表含"建议/尽量"）、术语定义位 |

### A2 新增待裁项（原报告 §四/§六 之外）
- **`check_blueprint_compliance.py` 缺 sys.path 引导**：裸 `python <路径>` 必 `ModuleNotFoundError: No module named '_shared'`（同 `diagnose_depgraph.py` 有 bootstrap 就能裸跑）→ **改对路径必要但不充分**，属 C 加牙。 `[亲验]`
- **`check_ssot_uniqueness.py` 参数面与模板不符**：模板写 `--blueprint <module_id>`，实存脚本只有 `--warn-only`+位置参数 → 改路径不改参数命令仍崩，改参数＝立法，A2 按"禁猜"未动。 `[亲验]`
- **施工 SOP 里 `python scripts/git_commit_gateway.py`（L29/L610）该路径全史从未存在**，合法后继二义（`scripts/git_commit.py` CLI vs `gov_enforcement/rule_bridge/git_commit_gateway.py` 模块）→ 需定"官方提交入口"的写法。 `[亲验]`
- **归档面免断链普查**：`agent_constitution_legacy_v1.md:522` 引用已迁移模块，归档自称"零内容丢失"，改它＝改历史 → 建议登记豁免面。 `[亲验]`
- **`TRAE-079` 判 D4 无效**：`COMMIT-CRITICAL-SECTION-LOCK` 两册零候选、全仓 grep 只命中条文自身与本战役文档＝从未存在 → 这条"有牙"是假的，弱模型会以为它拦过。 `[亲验]`

### 派单纠错（供后续腿照抄）
我给 A2/A7 的任务书里写的入队姿势 `git_commit.py ... --base-head $(git rev-parse dev)` 是**错的**——本版 `git_commit.py` 无 `--base-head` 参数，带上会 exit≠0。A2 去掉该旗标后成功。（`--base-head` 属 `commit_queue.py enqueue` 的参数，我记串了。） `[亲验]`

## 八B、A7 腿（文档面清扫）回执并入 —— **本腿最大的价值是否掉了我的处方**

### 落地三笔（总控逐笔复核在 dev，0 死信、0 逃生旗）
| commit | 内容 | 实测 |
|---|---|---|
| `7877077bf7` | `check_index_integrity.py` 新增 `_strip_anchor`，链接剥 `#锚点` 后再判存在 | 主区同磁盘快照改前/改后：**1263→547（−716）**，MEDIUM 752→36。715/752 来自单个 gitignored 生成区文件的 807 条锚点链接。双向红证：植锚点链接修前误报、修后不报；植真悬空**仍能红**（无误绿） |
| `864618bc7a` | 30 条 `file:///D:/ZephyrAlpha/...` 绝对针 → 28 条改相对 + 2 条按证据去链接保行文 | `audit_broken_links.py --ci --check-new` 本批 5 文件 rc=0"无断链"；`check_pure_assertion --ci` rc=0 |
| `e9fb06c2d4` | 5 行改指已核实唯一真址（`knowledge_article_registry.yaml`→`_archive/`、2 处裸名→唯一路径） | 每条改前 `git ls-files` 断言唯一；改前后 dev 零第三方漂移（blob 全等） |

### 它按证据否决了我派下去的 5 条处方（我复核后认账）
| 我派单写的 | 真相（总控亲验） |
|---|---|
| **K3「`docker-compose.yaml` 拼写变体 → 改指根目录 `docker-compose.yml`」** | **我的处方是错的。** `docs/03_modules/index.md:107` 原文是 `> **豁免**：docker-compose.yml / docker-compose.yaml（Docker 外部约定）`——**两种拼写并列正是这句话的语义**，"改成 yml"等于自己造 bug |
| **K4「真删/从未存在条目删行 6-9 条」** | 13 条逐条取证后**全部不该删**：7 条指向 gitignored 但**盘上真实存在**的派生导航件（`326952a276` 一次性把 100 个派生文档移出跟踪）／2 条是 frontmatter `summary:` 与版本史表格里的**变更日志文本**（删＝毁审计轨迹）／2 条是"待施工"设计意图声明／2 条属内容缺陷该改写不该删。**照我那份清单删行会把退役历史和"待施工"声明一起清掉** |
| 裸名链接 78 条可机械补 | 其中 **52 条是 `blueprint.md` 泛称**（"每个模块都有 blueprint.md"），根本不是链接；真需消歧只 5 个名字 |
| `_registry/index.md:23 _index.yaml` 加路径 | 它在文件数构成叙述里（"64 登记表 YAML + `_index.yaml` + `index.md` + `_archive/`"），作用域已被上下文限定，加路径反而破坏口径 |
| glob 占位 4 条 | `*_vocabulary.yaml`/`trae_*.yaml`/`{module}/blueprint.md` 是模式说明，"缺文件"判定对它们无意义 |

### 新立 P0（总控已独立复测坐实）
**P0-8｜`generate_missing_index_md.py` 在任何 session worktree 里恒绿。** 真源 `scripts/governance/d1_structure/generate_missing_index_md.py:294` 用 `dirpath.parts` 判"是否隐藏目录"，而 parts 是**绝对路径**分段——仓库检出在 `.worktrees/` 下时**每个目录都带 `.` 段**，于是全被 skip。总控复测：工棚内同工具同参数输出 `OK: 扫描 0 个目录，全部已含 index.md`，主区则是 `[DRY-RUN] 将处理 1002 个 index.md`。**这条通道正是提交队列 serializer 用的通道**——任何在 worktree 里跑它的班次都会拿"全绿"收工。 `[亲验]`

**P0-9｜`check_index_integrity.py` 不能当施工验收证据**（比 §五 那条"95% 假信号"更深）：判据是"条目 basename ∈ 该 index 目录**递归**子树内的 md/yaml 集"，造成 ①跨目录正确链接全误报（含 6 条指向 `.py/.json` 的——`get_sibling_files` 只收 md/yaml，永远红）②**真断链漏报**（`knowledge_article_registry.yaml` 改名后该门一声不吭，因为 `_archive/` 里同名文件被递归命中）③把 frontmatter 与版本史正文当索引清单。铁证：**A7 改了 35 行真内容，该门计数 517→517 纹丝不动**。同族盲区另证：`validate_cross_references.py:642` 对 `file:///` 直接 `continue` → 那 30 条绝对针**改前根本不在任何交叉引用校验覆盖内**。 `[亲验]`

### 数字口径纠正（同一个欠账，两个都对的数）
| 口径 | 数 | 谁给的 |
|---|---|---|
| 工具自带口径（含未跟踪/被忽略目录，如 `docs/_working/投资账本截图/`；≥1 件） | **1002** | A7 主区 dry-run |
| tracked ∧ 内容件≥2 ∧ 无 `index.md` | **344** | 总控自建口径亲验（A3 曾报 345，属同口径漂移） |
| 其中临时区 `docs/_working`（本不该有 index 义务） | 108 | 同上 |
| **永久区真欠账**（`03_modules` 215 + `01` 11 + `02` 7） | **≈233** | 同上 |

⇒ **本报告 §六 T-3 里"345"与本节"1002"都必须带口径才能引用**；不带口径的净增规模差 3 倍，决策依据不成立。这正是宪法 §9.5「静态清单禁手工维护」与 §4.3「计数用字段不写死在散文」的同一个病。

### A7 剩余登记（未做，非被堵）
- 同类绝对针还剩 **26 条在 `docs/03_modules/**/blueprint.md`**（blueprint frontmatter 是 `blueprint_registry` 同步真源，改面性质不同）+ 1 条在 v1 归档宪法（archive 宜原样保留）+ 2 条在 `docs/_working`（禁区）。`[亲验]`
- `.tmp` 残留实测已漂到 **137 件 / 82.7 MB**（A3 曾报 46 件/86.6MB，dev 在动）。位置集中在 `.runtime/tmp/**`（宪法钦定临时区）。
- 5 条多命中裸名待消歧（`noqa_exempt_registry.yaml`/`strategy_registry.yaml`/`model_registry.yaml`/`compliance_report_registry.yaml`/`README.md`），清单 `.runtime/tmp/a7/a7_bare.json`。
- `blueprint_registry.yaml` 在 `docs/03_modules/index.md:91` 仍被标为 **"SSoT"** 但双盘均不存在（`.gitignore:574`、`03df6215e8` 退库）——A7 只去了链接，"该行该指生成器 / 该删 / 派生件是否配称 SSoT"待 Max 判。



## 九、本班未做成 / 须认的账

1. **A2、A7 均已回并入库（见 §八、§八B）**。七路全部交回：A1a/A1b/A2/A3/A5/A7/CF1；A4 的架构域由 A1b 的 C-11..C-18 覆盖，未另立腿。
2. C-13 只抽了 15 个候选（512 个未穷尽），C-17 的 `strategy_factory`/`strategy_pipeline` 全量清单落在 `.runtime/tmp/redlab_a1b/c17_unowned.txt`。
3. C-05/C-18 未做按域细分（A3 派单只含 T1–T4）。
4. DEPENDENCIES/CONSUMERS 能否 100% 由 depgraph 反查**未实测** → T-3/T-6 的"②档"定级偏保守。
5. A5 有 5 台"有测试但零负向断言"的门禁（`apply_decisiongraph`、`collect_write_audit_4663`、`extract_decisiongraph`、`run_silent_failure_regression`、`session_worktree_cli`）**未能逐台实弹红证**——真红需写被跟踪派生册或造 worktree，撞只读硬约束，标 `[推断-不可测]`。
6. GATE-ARCH 19 子项、GATE-INTEGRITY 子进程面未逐台开牙验（时间盒）。
7. 计数漂移：`check_index_integrity` 1264→1263、orphan 313,763→322,189 属并发会话在途写入，非本班会话造成（本班样本全在 `.runtime`，两卡源码均显式 skip 该区）。
8. 一次工具链误伤登记：红样经 bash heredoc 两次被本仓 echo-guard 拦截/改写（`\\` 被吞成 `\`），改用 python 写入才可靠——审计/施工管道对该守卫的误伤需要预案。
9. 注入面扫描：全部读取面命中 5 处诱导字样，**均为防御规范自身的样本串**（`audit_prompts_20_ai.md:63` 抗注入条款本体 + LSG/蓝图判定表），无一处指向执行腿。 `[亲验]`
