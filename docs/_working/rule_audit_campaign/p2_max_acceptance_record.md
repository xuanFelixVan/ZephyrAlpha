---
ttl: task_bound
completes_when: P14 终局报告
session: st-maxexec-20260920
issue: MAXEXEC-P2
---

# P2 分包验收记录——W1-G WP17 / #351+#357 终验 / W1 遗留小件

验收人=Max 验收手（st-maxexec-20260920，裁定#371 授权全权复验）。输入=任务书三件+判决书
`2026-09-19-max-dayshift-rulings.md`（#340..#360）+施工 commit 亲验。证据等级自标：`[亲验]`=本班现场命令取证；
`[转报]`=采信 commit/判决书在案证据未复跑（均注明核验方式）。

## 件 1｜W1-G WP17 验收（施工 commit `e0e115a93e`）

### 验收点① 施工面与裁定#359/#341 处方一致性 [亲验]

`git show e0e115a93e --stat` 亲验：7 文件（adversarial_validation 5 + tests 2），与裁定#359 处方逐项对上：

| #359 处方 | 施工实证（diff 亲验） |
|---|---|
| 分桶：入参/工具异常与攻击拦下分桶，error 桶绝不计入 blocked | `models.py` DefenseResult 增 `error` 字段；`defense_runner.py` `evaluate_gate` 改三态 `(blocked, source, tool_error)`；引擎缺失/评估异常/入参异常统一 `tool_error` 桶且 blocked 恒 False；`validator.py` 映射 `ResultClass.TEST_ERROR`、不写 bypass 台账；W3-T2 `fail_closed→BLOCKED` 旧分支（`return True, "fail_closed"`）在删除行中可见=废除 |
| 区分度自检：应拦/应放行结果必须不同 | `validator.py` `run_discrimination_self_check()` 三腿（应拦 canary-ok/应放行 no_vector/应报错 canary-raise）走 `run_defense` 公共链路，互异判定；`cli.py` run 接自检，`errors>0 或自检不过 → sys.exit(1)`，输出增 `errors`/`self_check` 字段；`RedBlueReport.error_count()` 只增方法不动字段契约 |

与 #341 的关系（澄清）：#341（55 台 pre-commit 零执行权）当时裁定=**E 上交 Owner、"禁止在 Owner 裁决前动主链路"**
（判决书 §一）。e0e115a93e 文件面**不含** gateway/.pre-commit-config/gate_registry（stat 亲验）——未触 #341
主链路，合规。55 台执行权（方案②网关 staged 跑 pre-commit）由 W1-D2（`aca8c71fad`，Owner 批方案②、
flag `gate_precommit_run` 出厂 ON）独立落地。任务书将 WP17 表述为"给 55 台门禁补执行权"与 commit 实际
施工面（对抗校验器通道内的真实 gate 评估能力）存在映射偏差——按任务书"以 commit 实际改动为准"执行，
本验收对 WP17 实际面全验、对 #341 通道（W1-D2）做红证 cross-check（见红证节）。

### 验收点② 计数复核（施工前后对照）

| 口径 | 数值 | 等级 |
|---|---|---|
| 判决书 #341 基线 gate_registry | 169 = pre-commit 55 + commit-gate 113 + manual 1 | [转报]判决书亲验数 |
| W1-D2 重跑注册表后（`git show aca8c71fad:<registry>` 解析） | 169 条 55/113/1 不变；另加 `enforcement_channel` 字段（55 pre-commit/113 commit-gate/1 manual） | [亲验] |
| HEAD 现状 | total_gates 字段 169、实 entry 169：55/113/1；enforcement_channel 同上+in-process 1 | [亲验]yaml 解析 |
| 工作区现状 | **170** = 169 + 1 条 `COMMIT-CRITICAL-SECTION-LOCK`（source: commit-gateway，裁定#347/#372 实名登记补册，**未提交在途件**，git diff HEAD 亲验 +13 行）——他会话/后续 rules 批 WIP，owner 责任制不代处置，仅记录 | [亲验] |
| WP17 场景计数 | 注册表声明 total_scenarios 54（scenario_id 条目 53）；CLI 实跑 total=52；修后 18 真实评估 + 34 error 桶 = 52（34=场景引用不存在 gate_id 显式入桶，旧代码全洗成假 BLOCKED） | [亲验]实跑+读册 |

**55 台计数结论**：施工前后 55→55 不变（W1-D2 加字段零计数漂移）；工作区 +1 为在途补册非本批管辖。

### 验收点③ 裁量披露：裁决代理"补 Task description 参数"是否合规

- Task 对象=`zephyr.gov_enforcement.rule_enforcement.task_types.Task`（pydantic）。亲验
  `Task.model_fields['description'].is_required()=True`、default=PydanticUndefined——**description 是
  必填字段**，缺它构造 Task 必抛 ValidationError。
- 修前腿机理实证 [亲验]：按修前代码原样构造 Task（无 description，其余参数照抄旧 try_real_gate）→
  `ValidationError: description Field required` 实测复现。叠加 diff 亲验（老代码宽 except 吞异常 →
  `return True, "fail_closed"` → 计入 BLOCKED），"52/52 全 blocked、blocked_rate 恒 1.0 假绿"恒真链条完整闭环。
- **结论=合规、非越权**：不补 description 则 52 场景全数 error 桶、工具零真实评估，#359 处方①的分布与
  处方②的自检应拦腿都无从产生——该参数是执行权落地的**必要件**；治本主体（分桶+自检）独立于该参数成立。
  施工在 commit message 以"配套（披露）"显式申报，非隐藏裁量。短描述（"Adversarial probe <sid>"）规避
  GOV-TASK-001 长描述结构词告警，用词合规。
- 任务书口径澄清：任务书要求对照".pre-commit-config.yaml 相关 entry 的 Task description 语义（pre-commit
  框架 Task 对象 description 参数）"——**pre-commit 框架无 Task 对象**；.pre-commit-config.yaml 69 个 entry
  的 `description:` 是 hook 人类可读元数据，与 Task 构造参数无语义关联。Task description 权威语义真源=
  task_types.py pydantic 模型（上文亲验）。

### 红证：抽 3 台门禁实测执行权生效（违规红/合规绿双向）[亲验]

经 pre-commit 框架端到端跑（`pre-commit run <id> --files <样本>`，即 #341 方案②/55 台执行权载体通道；
退出码为 pre-commit 自身退出码）：

| 门禁 | 违规样本（.runtime/tmp/p2_redtest/） | 合规样本 |
|---|---|---|
| gate-detect-git-dangerous | `git_bad.py`（ABS-27 hard-reset 危险命令字面量，payload 见样本原件）→ **Failed / exit 1**，报 1 finding | `git_ok.py`（安全 git 查询命令）→ **Passed / exit 0** |
| gate-detect-shell-dangerous | `shell_bad.py`（ABS-38 根目录递归删除命令字面量，payload 见样本原件）→ **Failed / exit 1**，报 2 findings | `shell_ok.py`（`shutil.rmtree(tmp_path)`）→ **Passed / exit 0** |
| gate-frontmatter | `fm_bad.md`（ttl 非法值）→ **Failed / exit 1**，报 invalid ttl | `fm_ok.md`（ttl: task_bound）→ **Passed / exit 0** |

三台六腿全部正确判别。WP17 通道修后状态同步复现 [亲验]：`python -m zephyr.security.adversarial_validation run`
→ `total=52 blocked=18 bypassed=0 errors=34 blocked_rate=0.3462 self_check=PASS` **EXIT=1**，与 commit 红证
逐位一致（修前 52 blocked/EXIT 0 为 [转报] commit 红证，机理已亲验闭环，未重跑修前二进制）。

### 结论：**通过**

## 件 2｜#351/#357 红证终验（签字级复核，不重跑重型红证）

### 裁定#351 装载器 fail-closed（施工 commit `0cc6e87618` [final3][W1-D1]）

- 处方对照（判决书 §三#351）：fail-closed（任一门装载失败→提交阻断并报 gate_id+错误）+ 装载数≠名册数
  硬告警；对照组=commit_gate_registry.check_all 单门异常即 fail-closed。施工 commit message 在案且与处方
  一致（含分层契约：名册缺失=warn 留痕的恢复变更，名册损坏/为空/装载失败/对账不一致=fail-closed）。
- 红证链完整性：三腿在案——①断一门（HELD-OVERLAP import-halted）→构造阻断 ②全健康→放行 113/113
  ③tmp 名册副本删条目（112≠113）→对账硬告警抛错。证据脚本 `.runtime/tmp/red_evidence_w1d1.py` **现存**
  ，头注释与三腿声称一致（子进程独立、victim=HELD-OVERLAP、tmp 副本不碰真册）[亲验读文件]。
- 代码现状 [亲验]：`gate_auto_registrar.py` [INVARIANTS]/[ERROR_CONTRACT] fail-closed 自述+实现
  （GateAutoRegistrationError 于名册不可读/非 dict/为空/装载失败/对账不一致抛出）。
- 健康腿亲验复现：`python -m zephyr.gov_enforcement.rule_bridge.gate_auto_registrar` →
  `Registered 113 gates, 0 failures`，EXIT=0。
- commit 归属 [亲验]：3 文件=registrar 主体+reconciliation_registry（消费方适配+附带 ruff 收敛，commit
  message 已披露）+测试；无越界文件。
- 回归声明（558 passed+1 xfailed）[转报]commit 在案，未复跑。
- **签字级结论：通过**（双向证据在案：断门必拦/健康放行；机理+脚本+健康腿复现三重吻合）。

### 裁定#357 check_index_integrity 判据重造（施工 commit `b5bc9f820f` [final3][W1-B2]）

- 处方对照（判决书 §四#357）：①相对本文件路径解析 ②sibling 扩 .py/.json ③frontmatter/版本史排除；
  同族 validate_cross_references `file:///` 纳入校验（锚点剥除沿用 7877077bf7 语义）。三处方+同族修全部
  在 commit 内（message 与 stat 亲验）。
- 红证链完整性：fixture 双向在案——修前 TOTAL=5（跨目录 `../B/target.py` 误报红、helper.py/data.json
  误报红、版本史+frontmatter 误计红、真断链被 `_archive/` 同名 basename 遮蔽=漏报）→ 修后 TOTAL=2（真断链
  `zz_absent.md` 照红 INDEX_ENTRY_MISSING、archive 盘存照报 FILE_NOT_IN_INDEX、其余全绿），**5→2 计数变化
  达成处方"同改动必须引起计数变化"硬性验收**。fixture `.runtime/tmp/index_fixture/` **现存**且结构与声称
  一致（docs/A/index.md+helper.py+data.json+note_frontmatter.md+_archive/zz_absent.md+docs/B/target.py）
  [亲验列目录]。主区计数 547→588、DIM-10 51→55 如实报含上涨来源（精确解析揭出同名遮蔽+真断链揭出）
  [转报]commit 在案。
- 代码现状 [亲验]：`check_index_integrity.py` `_SIBLING_EXTENSIONS` 含 .py/.json（:62）、
  `_strip_non_index_content`（:72）、处方①相对路径+弃递归 basename（:145-147 带裁定#357 注释）；
  `validate_cross_references.py` `file:///` 不再跳过（:696-697 带裁定注释）、`_resolve_ref` 无盘符形态按
  仓库根解析（:648-652）。
- commit 归属 [亲验]：3 文件=两检测器+echo-guard.yml（CloneGuard 豁免登记，commit message 已披露）；无越界。
- **签字级结论：通过**（改前红/改后绿双向+计数变化+漏报揭出四要件齐备）。

## 件 3｜W1 三批遗留小件

### #342 B②（FORBIDDEN_PREFIXES=() 静默全放 → fail-closed）：**已落在案，核验通过**

- 落点=W1-D2（`aca8c71fad`）：`scripts/governance/d5_architecture/checkers/check_src_no_data.py`
  `_load_forbidden_prefixes` 契约文件 FileNotFoundError → RuntimeError 报错退出（:62-83 带
  "fail-closed（裁定#342 B② 翻转，2026-09-19）"注释）[亲验代码现状]。
- W1-D2 红证 [转报]commit 在案：临时改名契约→报错非放行→还原；`src/zephyr/data` 样本修前放行 exit 0/
  修后拦截 exit 1。记录完毕，无需再施工。
- 附带核实 [亲验]：#342 主体（3 entry 补 --ci）——.pre-commit-config.yaml 现状多处 `args: ["--ci"]` 在册
  （:237/:274/:291/:307/:383）；W1-D2 实测判词"均无 --ci"前提已过时（疑对 gate_registry entry 字段核验），
  以机制验证替代并在 commit message 披露——程序合规（判据事实修正+披露，非静默改判）。

### #342 B①（前缀真源扩 `src/zephyr/data/`）：归 P6/Owner，不属本批

一句记录：未落地；W1-D2 停手理由=`src/zephyr/data/` 实为 MOD-L00-001 合法注册模块（145 tracked 代码文件），
字面执行=冻结整个数据域提交；替代建议（拦非 .py 数据扩展名/登记豁免面）已随 W8-3 签字册
（`73e02d98fd`）送 Owner 复裁。

## 依据与证据等级汇总

- 裁定依据：#359（判决书 §四，WP17 维持立项+两件处方）、#341（§一，E 上交+禁动主链路）、#351（§三，
  C 加牙概括授权）、#357（§四，B 判据重造）、#342（§一，E 上交+两处 B 修随批）、#371（Owner 2026-09-20
  授权 st-maxexec-20260920 全权复验，commit `2a5711961a`）。
- 施工 commit：WP17=`e0e115a93e`、#351=`0cc6e87618`、#357=`b5bc9f820f`、#341/#342/#354=`aca8c71fad`。
- 证据等级：件 1 红证/计数/裁量披露=**[亲验]**（修前二进制不重跑=机理亲验闭环，已标转报）；件 2=代码
  现状+证据工件+健康腿**[亲验]**，红证双向本体=[转报]commit 在案（任务书明示不重跑）；件 3 B②=代码
  现状**[亲验]**+红证[转报]在案。

## 施工披露（本批自身）

- 本批新建本记录（CREATE-GUARD token 同批登记，prefix=docs/_working/rule_audit_campaign，
  capability=rule_audit_campaign）；样本与探针均在 `.runtime/tmp/p2_redtest/`（临时区合规）。
- token 注册表 `capability_canonical_file_registry.yaml` 提交时同批吸收同会话（st-maxexec-20260920）
  兄弟批已 staged 的 28 行 factory 族 token 登记（WT==INDEX 前进条目、created_by 同名，git diff 三分法
  亲验）——按共享暂存区现状随批落地并在 commit message 披露；如兄弟批后续提交报 no-change 属预期。
- 活体证据补记：本记录首次入队（q-20260920-st-maxexec-20260920-0013）被 GATE-PRECOMMIT-RUN 通道的
  gate-detect-git-dangerous/gate-detect-shell-dangerous 拦截——红证表格原引用了违规样本的命令字面量，
  被两台门禁按真违规判红（dead_reason 在案）。**本记录的提交过程本身即 #341 方案②执行权生效的第七腿
  实证**；修正=表格改语义描述（样本原件保留在 .runtime/tmp/p2_redtest/），非豁免、非绕过。
