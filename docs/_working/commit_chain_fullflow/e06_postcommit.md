---
created: 2026-09-30
ttl: task_bound
title: 提交链路全流通·E6 post-commit 链（挖矿）
session: M3
---

# E6 — post-commit 钩链（lfs → YAML regen → guard → Qoder[已封存]）+ 友邻钩（post-checkout / reference-transaction）

> 挖矿代理 M3 ｜ 2026-09-30 盘面实测行号。钩子安装位 `.git/hooks/`（git_commit 恒 `--no-verify`，pre-commit 被跳但 **post-commit 不被跳**——guard 治本前提，:12-14 of guard）。
> 真源：`.git/hooks/post-commit`（22 行）、`scripts/governance/git_hooks/post_commit_guard.sh`（276 行）、`scripts/governance/git_hooks/post_commit_regen_yaml.py`（358 行）、`scripts/governance/git_hooks/reference_transaction_guard.sh`（280 行）、`.git/hooks/post-checkout`（20 行）。本日 git status 全部 clean 无占用。

## §0 自审闸三态

| 段 | 状态 | 依据 |
|---|---|---|
| post-commit 四段 + guard 全分支 + regen 触发器 | 【挖干】 | 六向齐，钩子源文件与真源脚本本日逐行核实 |
| reference-transaction guard（M3/T6 改后态） | 【挖干】 | :133-135 非 dev 早退 + 零子进程根发现 + 5并1 均在盘验证 |
| post-checkout 链 | 【挖干】（post_checkout_guard.py 本体 174 行只记接口） | guard 本体深挖归 E2/会话面，非提交耗时关键路径 |
| Qoder tracker | 【不可挖】→ 已退役 | 2026-09-30 Owner 批注释封存（post-commit:19-21、post-checkout:8-19），零观测零消费方 |
| regen 扇出本体 reconcile_generators.py 深挖 | 【不可挖】→ E8 | 属 E8 reconciler/auto-commit 环节；本文记触发外壳与耗时账 |

## §1 组件全清单

### 1.1 `.git/hooks/post-commit`（四段，git commit 进程返回前**同步**跑完）

| 段 | 锚点 file:line | 功能 | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|---|
| ① git-lfs | .git/hooks/post-commit:2-3 | LFS 探测 `git lfs post-commit` | 每次 commit | <0.3s 量级 UNKNOWN（B0_1 A2） | 自动，静默 |
| ② YAML regen 触发器 | :9-11 → post_commit_regen_yaml.py | 检测本笔是否改生成器 YAML 输入源→detached spawn `reconcile_stale` | 每次 commit（python 冷启动含内） | **同步段 0.1-1s**（ZEPHYR_SKIP_REGENERATE=1 冷启实测，b0_readme 表）；扇出本体 detached 不在关键路径 | ERROR_CONTRACT：任何异常静默 exit 0（regen:10-14） |
| ③ POST-COMMIT-GUARD | :16-18 → post_commit_guard.sh（sourced） | 非 GW commit 检测与自动 `reset --soft HEAD~1` | 每次 commit | 未单列计时（B0_1 A4：17 处 git/shell 为静态上界 UNKNOWN）；合法路径主体=2 次 git log + 1 次 rev-parse + 1 次注册表 grep | 阻断式（reset+exit 1） |
| ④ Qoder tracker | :19-21 **已注释封存**（2026-09-30·Owner批，gate_survival_adjudication §6/§9.5） | 外部 IDE 记账，每笔拉起 Electron | —（退役） | 曾为 UNKNOWN 残差候选（B0_1 A5） | 已退役，注释块可还原 |

### 1.2 `post_commit_regen_yaml.py`（段②真源）

| 组件 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|
| 本笔 YAML 清单 | :169-188（`git diff --name-only --diff-filter=AMR HEAD~1 HEAD`，timeout 15s；首笔无 HEAD~1→空不触发） | 每次 | 1 git 子进程 | 静默失败 |
| 输入源匹配 | :191-207（`yaml.safe_load` generator_registry 全册，只认 `yaml:` 前缀 input_sources） | 命中 YAML 才继续 | 2 次 yaml.safe_load（inputs+outputs，B0_1 A3 计两处 :115/:134 旧锚） | 精确+前缀匹配 :269-272 |
| 产物循环阻断 | :210-229、:263-268（committed 命中 output_globs → 跳过，防产物→输入→产物死循环） | 每次 | 同上一次 load | #3 治本 |
| 意图账（M2/P-3） | :148-157、:297-304（`.runtime/derived_dirty/ledger.jsonl` append-only，逃生/锁占/main_only 只抑制执行不抑制记账） | 命中输入源即落账 | ~0ms（append） | C4 静默丢弃治本 |
| 逃生通道 | :307-308（`ZEPHYR_SKIP_REGENERATE=1`） | 批量提交 | 0 | 记账已完成才放行 |
| scope 旗 | :131-145（读 flags `git_operations.regen_scope`，缺省 any_worktree；main_only=worktree 只记账不 spawn） | worktree 语境 | 1 次 flags 读 | **现值 any_worktree（config/flags.yaml:48 出厂态）**；翻转=Owner 门位 |
| TTL 去重锁 | :119-122（lockfile TTL 60s）、:232-240（判活）、:243-253（写 PID） | spawn 前 | ~0ms | 60s 内后续 commit 跳过 spawn |
| 尾事件收敛 | :160-166、:315-317（锁活跃→`_mark_pending_rerun`）；消费端 reconcile_generators.py:802（跑完异步补一轮 stale 检查，禁定时器） | 锁活跃时 | ~0ms | 75% 静默丢的收口补丁（已落盘） |
| 主区钉根 | :84-113（`_resolve_main_root`：worktree .git 指针剥 `/worktrees/` 段）、:111-117（锁/账/日志/编排器全钉主区） | 模块加载时 | 0 | R2c"每工一把锁"+C5 负收益治本 |
| detached spawn | :320-348（CREATE_NO_WINDOW，`cwd=_MAIN_ROOT`，日志 `.runtime/logs/post_commit_regen_yaml_*.log`，不等待） | 全检查通过 | 同步成本仅到 Popen | 永不阻断 commit |

扇出本体耗时账（detached，b0_readme 表）：CPU 总秒 **97.3 / 122.5 / 234.3**（mean/med/max），墙钟 **37 / 11 / 131**s；单生成器 CPU·s 均值 domain_doc 78.7｜governance_map 19.1｜path_tree 17.5｜battle_map 10.8｜decision_diagram 7.1；并发度=`_MAX_WORKERS=4`（reconcile_generators.py:73、:525、:555 ThreadPoolExecutor）。4 工落地同窗爆发即 4×97 CPU·s 争用面（B0_3 M2 动机）。

### 1.3 `post_commit_guard.sh`（段③真源，276 行）

| 组件 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|
| 取 message | :51（`git log -1 --format=%B`） | 每次 | 1 git 子进程 | — |
| `[GW:` 检测与 sid 提取 | :54、:62（广义标识符 `[GW:<A-Za-z0-9_][..]*`，多标记全量 `sort -u`） | 每次 | shell 内置+grep/sed 管道 | P1-1 治本（原 sess- 前缀对现行会话命名全盲→提取恒空→伪造畅通，红蓝 v3 S1.9 实弹） |
| 文档性提及放行 | :65-67 | 解析不出标识符 | 0 | 保守放行防误杀散文 `[GW: 标记]` |
| worktree 感知根 | :70-76（`rev-parse --git-common-dir`→注册表路径） | 有 GW 标记才走 | 1 git 子进程 | — |
| fail-open | :79-81（注册表不存在→放行） | 注册表缺失 | 0 | 不因环境问题阻断所有 commit |
| 会话键校验 | :114-115（grep 会话键正则，剔容器名 sessions）、:117-123（逐标记 `-x -F` 整字相等） | 有 GW 标记 | 2 grep | 红队加固 st-ff-rb-gov-20260918：字段名/路径片段不再当通行证（原整文子串匹配，`[GW:pid]` 万能通行） |
| warn-only 分支 | :134-218（GW env=1 且 sid 未注册）：阈值计数 :144-148（缺省 3/86400s 同 session，env 可覆盖）、7 天报告清理 :162（事件触发非时间触发）、逐报告 4 grep :164-181、超阈值升级 reset :185-201、未超 warn+审计 :203-218 | 逃生通道 commit | 最坏遍历全 reports 目录（24h 窗内 N 份 ×4 grep） | ARCH-TOOL-HEALTH-V1 Phase 5（原 per-session 24h≥3 结构性失效：max=2 永达不了 3） |
| 伪造分支 | :221-237（无 GW env → `git reset --soft HEAD~1` + 审计 jsonl） | 伪造标记 | 2-3 git 子进程 | 阻断 |
| merge 豁免 | :245-253（2+ parents 主判定 + `^merge[( :]` 兜底） | merge commit | 1-2 git 子进程 | #ARCH-MERGE-PATH-GAP-001①（原 `^merge ` 误杀 conventional） |
| non-GW 分支 | :255-275（reset --soft + 审计） | 裸 commit | 2-3 git 子进程 | 阻断，修改保留 staging |

**17 处 git/shell 调用**（静态上界，grep 实数）：git log ×3（:51/:245/:250）+ rev-parse ×2 类（:70/:194/:213/:231/:266）+ reset --soft ×3（:199/:236/:273）+ grep/sed/find 若干。

### 1.4 `.git/hooks/post-checkout`（20 行）与 `reference-transaction`

| 钩 | 锚点 | 功能 | 触发时机 | 耗时账 |
|---|---|---|---|---|
| post-checkout ①lfs | post-checkout:2-3 | LFS | 每次 checkout（含落地器 `reset --hard` 每件触发，B0_1 A6） | 未测 UNKNOWN |
| post-checkout ②guard | :7 → scripts/post_checkout_guard.py | 事后检测 checkout 覆盖他会话锁定文件，仅警告不阻断 | 同上 | 未测 UNKNOWN |
| post-checkout ③Qoder | :8-19 已封存 | — | —（退役） | — |
| reference-transaction | .git/hooks/reference-transaction:5-7 → reference_transaction_guard.sh | 堵 commit-tree/update-ref plumbing 绕过（porcelain 才触发 pre/post-commit，plumbing 零钩） | **每次 ref 事务 prepared**（含非 dev 分支/stash/tags） | **dev 前进 1.25s/次（n=3）、非 dev 0.39s、真回退 0.44s**（b0_readme 表；原 5 git 子进程已并 1） |

ref-tx guard 关键锚点：state 早退 :74-76；零子进程根发现（PWD 上行走查 .git，M3/T6）:78-100；CRLF 剥离 :119-125；**非 dev 早退 :133-135**（M3/T6 已做）；deletion 跳过 :138-140；假 creation 堵漏（update-ref 不带 old 恒报全零→先探 ref 真值）:155-163；单调用取数（merge-base 判定+父数+正文合 1 次 `git log`）:177-191；会话键校验（与 guard 孪生，改一必同步另一）:202-238；Z-F8 归属观测腿（在册 sid 但网关未在场→warn_only 落审计）:232-237；GW env/emergency 审计放行 :247-253；BLOCK exit 1（prepared 回滚整个事务）:257-276。

## §2 六向台账

- **上游触发源**：①git commit 进程（E5 :4071，`--no-verify` 不豁免 post-commit）；ref-tx=一切 ref 事务（E5 commit、E5 内 guard 的 reset --soft、E7 `_advance_dev` update-ref、emergency_commit）。
- **下游消费方**：guard 审计 jsonl→commit_gw_audit reconciler；regen 意图账→reconcile_generators 尾事件补跑（:802）；ref-tx 审计→归属观测（Z-F8）；reset --soft→回 staging 由 AI 重新走正门。
- **输入面**：HEAD 新 commit message、`.runtime/session_registry.json`（会话键真源，indent=2 美化写格式被 :114 grep 依赖——布局漂移即退化 warn-only，:99-102 有失效语义登记）、`.runtime/reconcile_reports/post_commit_guard_*.json`（warn 计数真源）、generator_registry.yaml、flags.yaml。
- **输出面**：exit 0 放行 / exit 1+reset（guard、ref-tx prepared）；`.runtime/reconcile_reports/*.json`；`.runtime/derived_dirty/{ledger.jsonl,pending_rerun}`；`.runtime/logs/post_commit_regen_yaml_*.log`；`.runtime/locks/reconcile_stale.pid`。
- **真源锚**：§1 各 file:line；孪生段纪律=guard :114-123 ↔ ref-tx :214-223（注释互相点名，改一 MUST 同步另一）。
- **耗时账**：合法笔全链同步成本≈lfs(<0.3 UNKNOWN)+regen 同步段(0.1-1s)+guard(UNKNOWN，主体 2-4 git 子进程)+ref-tx(1.25s，仅 dev 前进时)；计入 E5 单条 commit 墙钟 112s med 内。异常笔加 reset 2-3 子进程+审计写。

## §3 缺陷与已修

| # | 缺陷（实弹证据） | 治本 | 锚点 |
|---|---|---|---|
| 1 | sid 提取只认 sess- 前缀→现行命名全盲→guard reset 从未触发 | 广义标识符+多标记全量校验 | guard :56-62（c224e15d63） |
| 2 | 注册表整文子串匹配：字段名当通行证（`[GW:pid]` 恒过）、嫁祸在活他人 sid | 只认会话键+`-x -F` 整字 | guard :87-123；ref-tx :193-223 |
| 3 | `update-ref <ref> <new>` 不带 old 恒报全零→"跳过 creation"成万能豁免，Phase 4 想堵的绕过从未被查过 | old 全零先探 ref 真值 | ref-tx :142-163（A1-5 实弹） |
| 4 | 文档性提及 `[GW: 标记` 被首版收紧误拦死（正门被打自纠） | 解析不出标识符→保守放行 | guard :65-67；ref-tx :203-209 |
| 5 | C4：60s TTL 去重**静默**丢弃合格触发——942 commit→81 命中→仅 20 份日志≈75% 丢且零留痕（b0_readme.md:28） | M2 意图账（先记账后抑制）+pending_rerun 尾事件收敛 | regen :124-166、:297-317 |
| 6 | C5：worktree 语境再生产物被 `check_no_commit_derived` 禁入 git、又被下件 `reset --hard` 抹掉=纯负收益 | 主区钉根（锁/账/日志/编排器 cwd 全钉主区） | regen :84-117、:341 |
| 7 | merge conventional subject 被误 reset（bm-fill 首版实证） | 2+ parents 主判定+前缀放宽 | guard :241-253 |
| 8 | per-session 24h≥3 阈值结构性失效（max=2 永达不了） | per-hour→改同 session 24h 窗计数+7 天报告事件触发清理 | guard :137-162 |
| 9 | Qoder tracker 每笔拉 Electron、零观测零消费 | 2026-09-30 Owner 批注释封存 | post-commit:19-21、post-checkout:8-19 |
| 10 | ref-tx 5 git 子进程/次（dev 前进 1.25s） | M3/T6：非 dev 早退+零子进程根发现+5并1 | ref-tx :78-100、:133-135、:177-191 |

**残余攻面（如实登记，勿宣称"标记不可伪造"）**：guard :104-113 / ref-tx :198-201 孪生登记——冒充**任一在活的他人会话键**仍落地不回滚（判据是 sid∈会话键，非 sid==本笔归属；归属信息只在网关进程内）。治本=提交时凭据载体（HMAC 尾签），跨车道设计，已登记交总包裁定；Z-F8 归属观测腿（ref-tx :232-237）已先落 warn_only 留痕。

## §4 待办移交

1. **A6 regen 事件化**（骨架 §三 A 段，st-gate-rationalize 认领）：翻转 `git_operations.regen_scope: any_worktree→main_only`（Owner 门位，flags.yaml:48；M2 外壳已备好 main_only 分支 regen:131-145/311-312），消灭锁内同步段与 4×97 CPU·s 同窗争用。本挖矿确认外壳分支/意图账/尾收敛三件已就绪，只剩旗翻转+实弹观察。
2. **hook 通道出锁**（骨架 §三 B 段"最后一并"）：post-commit 全链在 `_GlobalCommitLock` 持有窗内同步执行（git commit 进程返回前），lfs/guard/regen 同步段均为锁内可见成本；B0_1 A4 计时缺口（guard UNKNOWN）建议并入 A2 分段装表后回填。
3. **post-checkout 链计时缺口**：每件落地 `_sync_worktree` reset --hard 触发一次（B0_1 A6 UNKNOWN），移交 E7/E9 装表时顺带补测。
4. 移交 E8：regen 扇出本体（reconcile_generators.py:73/:525/:555、reconcile_stale :734、reconcile_async :628）与再生锁 drop-not-queue（C3 洞：锁按 _REPO_ROOT 键控跨工不去重——M2 钉根后编排骨架已单点，锁本体语义待 E8 复核）。
