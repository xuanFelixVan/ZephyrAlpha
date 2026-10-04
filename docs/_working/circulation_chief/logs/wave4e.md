---
ttl: task_bound
session: st-ffchief-20261001
date: 2026-10-01
status: done
---

# wave4-E 车道日志（内收原则专项：空壳处置+触发面卫生+债登记）

> 会话=st-ffchief-20261001｜车道=wave4-E｜日期=2026-10-01
> 输入=W3-3 挖矿（skeleton/J_ai_layer/F130、F87）+ gate_auto_registrar 触发面实证
> 自裁授权=Owner 总包令（堵死→登记跳过，禁提问禁停）

## 冷启动

- Python 3.12.8 PATH 修正 + usercustomize 在岗 + `ZephyrAlpha_ProcessReaper` 就绪（scanned=25 killed=0）——写操作前提在岗。
- 6 目标文件 lock_files.py claim 全成后动刀。

## 任务1a F130 ml_serve 空壳退役——已退役登记·零动作收口

- **复核**：7 件全空壳 `__init__.py` 成立（`__all__=[]` 零实码）；全仓 import 级消费=0
  （仅 4 处非 import 名字引用：domain_fk_gate 域名映射、externalize_algo_flow 路径映射、
  阈值普查同名异义注释、test_l11_ml_platform 陈旧头注——该 test 实际 importorskip
  `zephyr.ml_train.inference_base`，对 ml_serve 零依赖）。
- **关键发现**：W3-3 档漏见根包已有 2026-09-29 SW5 墓碑
  （st-nightsweep-sw5-20260929 依 fullconnect 案卷判"纯装饰，退役标记"，
  successor=F129 ml_train）——退役语义**已登记在案**。
- **处置裁定**：不重复退役动作。retire_module.py（MLC-003 七步）不适用：
  `--status MOD-ML_SERVE` = `{}`（生命周期册无此模块状态条目）且 `--execute` 须 Owner
  裁定号（RULE-RULING），总包令不构成裁定号。物理删除禁（V1 宁留勿删）。
  子包 6 件已有 DORMANT(STR-01) 标记，不重复铺 DEPRECATED（净零：同语义标记不成簇）。
- **落点**：F130.md 追加处置注记。

## 任务1b F87 redline 零消费——**证据过时，不退役**

- **复核翻案**：`ai_secret_exposure` 现有外部消费方 2 件（均惰性 import）：
  - `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:2863`（worktree 链路）
  - `src/zephyr/shared/security/secrets.py:227`（密钥面）
  另 redline/ 自部 11 件 + tests/ai_layer/redline/ 12 件自测试。
- **处置裁定**：零消费前提失效，"零触发零消费→退役"不适用——**不退役**；
  与 GateEngine 门族"同域收敛 vs 跨域不并"（§4 判据 4）属语义裁定，升级 Owner 门位，
  wave4-E 不代裁。
- **落点**：F87.md 追加处置注记。

## 任务2 门禁触发面卫生——5 台修正，真源→生成器→对账全链闭环

**真源链**：`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`
（files_trigger 真源）→ `scripts/governance/generators/generate_gate_registry.py`
（拉通进机生册 gate_registry.yaml）→ `scripts/governance/generate_gate_face_reconciliation.py`
（触发面对账报表）。匹配语义=四路 OR（目录前缀/精确/fnmatch/子串），fnmatch `*` 跨斜杠。

- **死触发清理 1 台**：REFERENCE-INTEGRITY 删 `docs/*.py|*.txt|*.yml` 三模式
  （git ls-files 实测 docs/ 全树三扩展名嵌套命中=0，永不触发）；
  `docs/*.json` 有嵌套命中 2 件=**活模式保留**（任务书"4 台"与实证 3 死的差异在此，
  实证优先）。触发面 8617 件不变（死模式零贡献坐实）。
- **超宽收窄 4 台**：COMPLEXITY-GUARD / FILE-COPY / FUNCTION-DUP / UNSAFE-DICT-SPREAD
  `["*.py"]` → `["src/*.py", "scripts/*.py", "schemas/*.py", "sitecustomize.py"]`
  （业务四径正向模式=排除面等价物；无排除字段语法故走正向）。全仓 .py 9169 件中
  tests/ 3975 件噪音出清，触发面 5194 件业务面（对账报表实测：
  src 3795+scripts 1162+schemas 236+根 sitecustomize 1）。
- **写入合规**：真源册经 `safe_write_text` CAS+进程外核实（6 行等量替换、零净删；
  注册表族删行守卫 0.81%>0.5% 拦截一次，按守卫文档外科通道显式 `allow_mass_edit=True`
  放行，审计留痕）。
- **重生成+验证**：generate_gate_registry.py 重出 181 门；diff 精确=5 台 files_trigger
  +generated_at，零漂移；`--diff` 三账对账 total_gates 自洽（181/181、104/104）；
  face_reconciliation 报表重出，5 台新触发面实测数字入表。
- **既存红项（非本车道引入，留审计）**：三账悬空 4 项
  （COMMIT-CRITICAL-SECTION-LOCK / GATE-DETECT-GIT-DANGEROUS /
  GATE-DETECT-PERMANENT-DELETION / GATE-DETECT-SHELL-DANGEROUS——账1 有名账2/3 无挂载）。

## 任务3 GOV-DOC-018 scripts/ 平铺债登记（只登记，不动结构）

- **实测**：`scripts/` 直系子文件 **148** 件（任务书口径 143——当日姊妹车道又落件，
  漂移 +5 在案）> error 线 120（trae_028 §GOV-DOC-018：warn 60/error 120）。
  构成：.ps1×69、.py×47、其他（AGENTS.md/2 yaml/vbs/1 tmp 残渣）。
- **拆簇建议**（Owner 级重构，测算 81 件可迁，scripts/ 顶层可降至 ~67）：
  1. `register_*.ps1`×32 → `scripts/tasks/register/`（计划任务登记器一族，最大簇）
  2. `run_*`×11 + `start_*`×6 → `scripts/tasks/runners/`（运行器/启动器）
  3. `check_/verify_/scan_/find_/list_*`×17 → `scripts/diagnostics/`（诊断审计一次性件）
  4. `git_*/commit_*/lock_files/session_worktree/git_guard/pre_commit/post_checkout_guard`×10
     → `scripts/git_tools/`（git 安全族）
  5. `fix_*`×5、`backfill_*`×3 → 各归 ops/data 簇
  - 迁移注意：计划任务注册器 cmdline 引用、script-manifest.yaml、
    `scripts/governance/` 根禁新增 .py 铁律不因拆簇放松；每簇迁移动须 ROOR 路径核实。

## 卫生发现（登记不动）

- `scripts/commit_queue.py.tmp.18376.0486a91925ee`：atomic-write 残渣（untracked），
  某次 commit_queue.py 写入被中断所留——建议 Owner 批准后物理清除（tmp 残渣非资产，
  不属 V1 宁留勿删对象）。
- `tests/model/test_l11_ml_platform.py:3` 头注 `[MODULE] zephyr.ml_serve.serving_orchestrator`
  陈旧（实际 import `zephyr.ml_train.inference_base`）——头注漂移，归测试域顺手修。
- GATE-DOMAIN-FK 亦为 `["*.py"]` 超宽（任务书"至少四台"之外的第五台）——未动，
  留 Owner 判其是否需要同等收窄。

## 交付与提交

- 改动清单（本笔入袋 8 件）：in_process_gate_registry.yaml、gate_registry.yaml（机生）、
  gate_face_reconciliation.{md,yaml}（机生）、F130.md、F87.md、wave4e.md（本文件）、
  **capability_canonical_file_registry.yaml（同袋原子）**。
- **capability 册入袋裁定（终）**：首判"不入袋"（避他会话净删），被 CREATE-GUARD
  锁外预检两连拦翻案——门读模拟提交后状态（temp-index 只装本笔 --files，册不在袋=
  退回 HEAD 版无 token），"同袋原子登记"是门禁设计要求非可选项（lane-f62 先例同）。
  袋内承继内容核验：448 插入=今日各车道 token 增量（W3-3 挖矿批 14:56 登记的
  skeleton 全档 campaign-mining-doc-* + 本车道 wave4e token 等）；17 删除=map_family
  3 token（**实件已物理消失**，死条目一致性清理，matrix 车道 13eaba13ca 先例
  "本队非删方，工作区字节承继"同型）+f82 路径迁移修正行。注册表净删 Owner 门位
  判定：删的是指向已不存在文件的死 token，属内收判据"零对象→退役"，不构成争议净删。
- token 登记通道：本车道 wave4e token 循 batch_creation_tokens 硬化通道
  （insert_block CAS）落盘；skeleton 7 档 token 由 W3-3 挖矿车道 14:56 并发登记
  （竞速双赢，幂等不冲突）。
- 提交：git_commit.py --session st-ffchief-20261001 --files <上列 8 件> --allow-non-worktree
  --enqueue；qid 以队列回执为准。
