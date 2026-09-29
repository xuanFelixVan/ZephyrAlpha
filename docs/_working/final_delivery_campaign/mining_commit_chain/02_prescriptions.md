---
ttl: task_bound
title: "提交链治本深挖 R2——可施工级处方卷（改哪/怎么测/怎么收/怎么退）"
session: st-finaldel-m1-20260929
---

# 02 处方卷（每条含：施工点、测试、验收判据、回滚、风险、预估收益）

> 前置：现状证据见同目录 01 卷。所有处方遵守：不删门禁（只前置/合批/降频/diff 化）、判据零放松、own-scope 归因语义不动（`gateway:3579-3645`）、热文件写 `safe_write_text`、提交走 `scripts/git_commit.py` 队列正门。
> 收益均为 02 卷写作时点实测外推，落地后以 R2 复测（重跑 csx_deep_01..09 对照 R1）为准。

## Rx-1（P0）enqueue 侧 ruff/format 预清——首过率 9%→70%+ 的主刀

- **病灶**：入队预检（`scripts/commit_queue.py:893` 引 `zephyr.gov_enforcement.rule_bridge.commit_preflight`，in-process gate 面）不含 ruff/ruff-format；这两台只在落地侧 pre-commit 通道跑（`.pre-commit-config.yaml` 序 10/11）。账本实证：通道阻断 hook 谱前两名 ruff-format 37 + ruff 36（占全史 46%）。每死一次=整轮 landing 白烧（gates 相位 mean 448-593s）+ requeue 重排。
- **施工点**：
  1. `scripts/governance/enqueue_preflight.py` 新增步骤 `ruff_preclean(entries)`：对本批 `.py` 清单跑 `python -m ruff check --no-cache --quiet <files>` 与 `python -m ruff format --check <files>`（subprocess，超时 60s，失败=阻断级 finding，输出截 800 字附修复命令）；非 .py 批零开销跳过。
  2. `scripts/git_commit.py` 直连路径对称补同一步（在 `gateway.commit` 之前，读 `:622 _probe_commit_lock_busy` 同层）；复用 20260922"落地通道整文件 ruff 预清"（`git_commit.py:603` 注释所指旧函数）如有残体则收编勿造第二套（CLONEGUARD 预查 `clone_guard.check_before_write`）。
  3. 开关：env `ZEPHYR_ENQUEUE_RUFF_PRECLEAN`（缺省 ON，"0"=回退现行为，B5/C1 同款零 yaml 依赖）；登记锚 `config/flags.yaml` 新键 `enqueue_ruff_preclean`（净零声明：合并 decisions_log 19:5x"人工两连"纪律为机械闸，不新增判据——ruff 判据真源仍是 `.pre-commit-config.yaml` 同一配置）。
- **测试**：红证=HEAD 旧字节上"含 ruff 违规的 .py 批 enqueue 成功"2 例绿；新码上同批 enqueue 被拒且 message 含 `ruff` 修复指引；非 .py 批不触发；env=0 时回退绿。
- **验收判据**：7 天窗内 `event=precommit_channel_blocked` 中 ruff/ruff-format 计数 <5/天（现 36-37/累积）；通道 rc=0 率（首过率）>70%；夜间 done 等待 p50 <20min。
- **回滚**：env 一键 OFF；或 flags 键 enabled:false。零数据迁移。
- **风险**：ruff 版本漂移导致入队/落地判据不一致——两处同用 `python -m ruff`+同一 `pyproject.toml` 配置，同进程环境解析；预检误拒的代价=入队时秒级反馈（远小于落地 10 分钟 round-trip）。
- **预估收益**：消除 40-60 死循环 landing/天 × 2-10min ≈ **200-400min/天**，并直接压夜间等待 p50（当前 107min 的第一大成分）。

## Rx-2（P0）锁等待插桩+gates 相位三分——R2 定案前置（半天，纯加法）

- **病灶**：`_GlobalCommitLock.__enter__`（`gateway:548-612`）轮询拿锁，等待时长**零落账**；唯一记录=超时 GatewayError 文本（`:2607-2610`→`:2639-2643`）。landing 侧 gates 相位把锁等待+门禁链+precommit+git commit 四合一（`commit_queue_landing.py:2811`），deep_dive_r1"未解释 123s"无法定案到段。
- **施工点**：
  1. `_GlobalCommitLock.__enter__` 成功路径加 `self.waited_ms = (time.monotonic() - t0)*1000`（t0=进入时刻；超时路径 `waited_ms`=timeout 值随异常带出）。
  2. `gateway.commit()` 在 `with _GlobalCommitLock(...)`（`:2592`）成功进入后读 `lock.waited_ms`，随 `_append_commit_anomaly_jsonl` 落一行 `{event:"lock_wait", session_id, waited_ms, timeout_s}`（复用现有 anomaly 通道，不新增账本文件——净零）；超时路径在 `:2643` 同格式落账。
  3. landing 侧在 gates 相位旁加记 `gates_inner_ms`（锁后重入 gateway 前后取差即可，`commit_queue_landing.py:2761/2797` 调用点已有 `_gates_t0`），使 gates=gates_inner+lock_wait 可对账。
- **测试**：pytest 桩锁注入 1.5s 延迟 → 断言 waited_ms≥1500 且 jsonl 行存在；超时路径断言 anomaly 行 event=lock_wait 且 acquired=false。账本断言用 `tmp_path` fixture（测试隔离红线）。
- **验收判据**：24h 内 lock_wait 行覆盖率=100% 提交尝试；能用账本直接回答"夜间 gates 相位均值中锁等待占比"（R2 定案判据：占比 <10% 则 123s 案闭卷归通道重试，>30% 则启动 Rx-6 提级）。
- **回滚**：env `ZEPHYR_LOCK_WAIT_LEDGER=0`（缺省 ON）。
- **预估收益**：不省秒数，但它是 Rx-6 是否立项、以及"夜战排队 107min 归因"的唯一判据来源——**没有它，后续所有优化不可验收**（A1 同款逻辑）。

## Rx-3（P1）own 面确定性 hook 加 `fail_fast: true`——红路径 88-100s→10-15s

- **病灶**：Phase-A 首败短路只覆盖非慢尾集且**同一次调用内先跑完全部快段才停**（`gateway:3549-3550` 按 chunk break，实为"段末短路"）；`pre_commit run` 本身无全局 fail_fast，注释明示原因=会以 foreign 失败掩蔽 own 失败（`gateway:3495`）。
- **关键安全论证（为何对 4 台 hook 开 fail_fast 不破坏归因）**：通道跑在 own-scope 临时索引+`--files own`（`gateway:3401-3418`），ruff/ruff-format/check-merge-conflict-marker/detect-private-key-local 四台是纯本批文件扫描器，**结构上不存在 foreign 失败**——它们红了=必然 own 违规，提前停链不存在"掩蔽 own"问题。全仓自扫描型 hook（慢尾 20 台）**不加**，保 own/foreign 归因。
- **施工点**：`.pre-commit-config.yaml` 仅给 `ruff`、`ruff-format`（序 10/11）、`check-merge-conflict-marker`、`detect-private-key-local`（序 1/2）四台 hook 块加一行 `fail_fast: true`。配置序不动（廉价前置的配置化重排与 T10"先取证再排序"纪律一致，本轮不做）。
- **测试**：钉子测试解析 `.pre-commit-config.yaml` 断言=恰 4 台含 fail_fast 且其余 65 台无；红证=构造 ruff 违规批实测通道 rc=1 且耗时 <20s（旧码 >60s）。
- **验收判据**：`precommit_channel_stats.jsonl` 中 rc!=0 行的 total_ms p50 从 88-100s 降至 <20s；own 阻断消息（`_precommit_decide_failure`）hook 字段非空率不降。
- **回滚**：revert 4 行 yaml（无状态）。
- **预估收益**：每次红路径省 70-90s × 20-60 红/天 ≈ **30-90min/天**，且工人提前释放直接压队尾等待。

## Rx-4（P1）Phase-B 收窄为"慢尾续跑"——绿路径 91→54 台次（-40%）

- **病灶**：Phase-A 绿后 Phase-B **全量重跑 57 台**（`gateway:3509` `_precommit_execute(env, chunks)` 无 SKIP）⇒ 快段 34 台一链跑两遍；样例实测 Phase-A 单段 44s，绿路径双调用固定地板 ~80-90s。
- **施工点**：`gateway:_precommit_run_scoped` 在 `:3509` 改为：Phase-A 绿（fa_rc==0 且非 infra）时调 `self._precommit_execute(env, chunks, skip_hooks=",".join(_PRECOMMIT_SLOW_TAIL_HOOKS 的补集))`——即 Phase-B SKIP=快段已验台（实现为 `_precommit_execute` 增加可选参 `extra_skip: str`，并入 env SKIP）；归因面合并：`_precommit_decide_failure` 收到 `fa_output + "\n" + output`（Phase-A 输出本就已在返回值链上，`:3496-3508` 现短路路径已复用同归因器）。变异重跑语义不变（仍整段重跑一次）。
- **测试**：判别 3 例=①Phase-A 红短路不动（现测保绿）；②Phase-A 绿→Phase-B env SKIP 含快段 id 且慢尾 id 不在 SKIP；③快段绿+慢尾红→own 阻断归因含慢尾 hook id（合并输出生效）。
- **验收判据**：rc=0 行的 `total_ms − fast_subset_ms`（=Phase-B 增量）p50 下降 ≥30%；阻断归因 hook 覆盖面不缩（对照 7 天窗 hooks 字段集合）。
- **回滚**：env `ZEPHYR_PRECOMMIT_PHASEB_FULL=1` 一键回全量 Phase-B；代码路径 flag 门住。
- **风险**：SKIP 不存在的 id 无害（`gateway:386` 既定语义）；变异侦测的 before/after 比对面随收窄缩小——变异只可能由已跑 hook 产生，语义自洽。
- **预估收益**：绿路径每件省 ~25-40s × 全量件数（日 ~80-190）≈ **50-120min/天**。

## Rx-5（P1）队列 priority 字段+本战役插队权（Owner 已授权）

- **病灶**：`_pick_head._rank`（`scripts/commit_queue.py:1678-1701`）排序键=(ts, qid, lane, path)，车道只有 interactive>machine+machine 1800s 防饿（`:1706`）；item 实测键集无 priority（01 卷快照表）。Owner 已批本战役提交插队，但机制不存在。
- **施工点**：
  1. item `meta.priority: int`（缺省 0；enqueue 入参 `--priority` 透传，`scripts/git_commit.py` `_enqueue_mode` 加同名参数，白名单 0-9）。
  2. `_rank` 键改 `(-priority, ts, qid, lane, path)`——**同优先级内 FCFS 严格保持**（B4 语义不破）；`_head_snapshot`/`position_ahead`（`:2390-2436`）同源改（B4 同判据纪律）。
  3. 开关：env `ZEPHYR_CQ_PRIORITY`（缺省 ON；"0"=排序键忽略 priority 全员等价 0）。C1 合批资格闸加"priority 相同才可并"一条（`:721 _c1_target_meta_ok` 处，防高优先件被低优先件吸收稀释）。
- **测试**：优先件插队（新 priority=5 件排在老 priority=0 件前）；同优先级保持 created_at 序（B4 专项测试不回归）；position_ahead 与 _pick_head 同源一致；C1 跨 priority 不并。
- **验收判据**：战役件（priority≥5）入队→开落 ≤1 个 landing 周期；非战役件倒挂率不升（B4 判据 <5% 保持）。
- **回滚**：env OFF=全字段归零（存量 priority 字段留存无害，缺省 0）；或战役会话停传 `--priority`。
- **预估收益**：战役车道等待 p50 107min→≤10min；不提速全局（机械插队，零判据变化）。

## Rx-6（P2，条件立项）precommit 通道出主锁——P2⑦ 同构：锁外预跑+锁内指纹采信

- **前置**：Rx-2 数据若证锁等待占 gates 相位 >30%，或主区直连并发窗再次出现 >3min 零推进（B1 原判据），本条提级 P1。
- **病灶**：直连路径通道 88-100s 全额计入主仓全局锁持有（01 卷 §二残留3）；`gate_preflight`（flags.yaml:104-107，production）已验证"锁外预跑+锁内指纹采信"模式可行，但只覆盖白名单 L2 门，未覆盖 precommit 通道。
- **施工点**：`gateway.commit()` 在 `:2553-2590` preflight 块旁增平行块（flag `gate_precommit_preflight` 出厂 OFF）：锁外先跑 `_run_precommit_channel`（临时索引+own 面天然隔离，无需防他会话 staged 漂移）；指纹 F=(HEAD sha, own blob sha 合集, flags mtime)——**必须含 head_sha**（慢尾全仓 hook 读 HEAD）；拿锁后重算 F′，相等才采信（跳过锁内通道），不等/预跑异常/预跑即阻断→锁内现行全量重跑（正确性永不依赖预跑，P2⑦ 同款安全边界）。阻断语义归锁内段（CAND-GATEMEC-004 口径不变：预跑红=放弃采信走锁内重跑给现行阻断）。
- **测试**：判别 3 例=F′==F 采信（锁内通道被跳、结果一致）；F′≠F（锁外推进 HEAD）丢弃采信锁内重跑；预跑异常降级。
- **验收判据**：主仓锁平均持有时间 −60s 以上（lock_wait 账本 p50 下降）；重放 20 件红件对照=同一批红件锁外仍判红（#341 执行权不丢，B1 判据③原文）。
- **回滚**：flag OFF（预跑代码保留，零行为差异）。
- **风险**：预跑与锁内窗口 HEAD 漂移→指纹必含 head_sha 兜住；通道双跑的固定地板成本在 F′≠F 时发生（实测频率由 lock_wait 账本先证）。
- **预估收益**：主区直连/merge 每件锁持有 −88-100s；并发直连吞吐近似线性受益。队列工路径不受益（私锁），无需改。

## Rx-7（P2，需 Owner）慢尾全仓 hook 触发面收窄（ERRCODE 现状处置）

- **现状**：GATE-ERRCODE-CONSISTENCY（统一册 `:1137` 条，own_scope=false，居 15 台 SHARED_INDEX 名单）in-process 侧 P50 7047ms（05_gate_audit C5 全表第 1）；precommit 侧 `gate-errcode-consistency`（配置序 34，files=`src/zephyr/**.py|errcode 注册表`）居慢尾清单（`gateway:395`）⇒ 每个含 src .py 的提交 Phase-B 必跑全仓 pytest 对账。
- **处方**（两档，均不动判据本体）：
  - 档1（登记 `files_trigger` 已有字段）：precommit 侧 hook `files:` 收窄为 `^(src/zephyr/.*\.py|architecture_model/contracts/error_code_registry\.yaml)$` 中含 errcode 特征的子集不可行（任何 .py 都可能新增 errcode）——改走**own-diff 预过滤器**：hook entry 前置 3 秒预检（own diff 无 `ERR-|error_code|raise ` 特征→直接 pass），作为独立 local hook 排在原 hook 前。审计 C5 的"仅 errcode 注册表或映射文件变更时跑"对 in-process 侧可行（L2 门挂 files_trigger，`gate_registry.yaml` 字段已在、触发机制走 check_all 前置短路）。
  - 档2（保守）：维持现状，仅 Rx-4 收窄后慢尾只在 Phase-B 跑一次，成本已减半；R2 复测后再议。
- **验收判据**：in-process 侧 GATE-ERRCODE-CONSISTENCY 触发次数/天下降 ≥70% 且 24h 窗零漏拦（errcode 类 block 事件计数不降）；重放 100 笔 verdict 全等（判据面变化 MUST 走重放）。
- **回滚**：触发面还原（files_trigger 一值/删预过滤 hook）。
- **同簇**：RECONCILER-HEALTH(3687ms)、CH-VERSION-COL(3344ms)、TAG-VOCAB(2172ms)、SCHEMA-FILE-EXISTS(1906ms) 同法（05_gate_audit C5 表既有处方，Owner 09-23 已批 A-E 五包，属执行欠账非新提案）。

## Rx-8（P2，Owner 门位）regen_scope 翻转 main_only——证据见 03 卷

一句话：消费点 `scripts/governance/git_hooks/post_commit_regen_yaml.py:310-311` 已就位（main_only=worktree 语境只记账不 spawn，记账 P-3 先行已落），翻转=flags.yaml 一值；但 worktree regen 的锁/账/产物根已钉主区（P3 批），提速收益有限，按 03 卷裁定节奏走。

## 施工优先序（建议）

1. **Rx-1（先修）**：唯一同时压"首过率 9%"与"夜战 107min"两大主症状的单刀；纯加法、env 回滚、账本可验收。
2. **Rx-2（同批）**：半天纯装表，为 Rx-6 立项与 R2 定案供数；A1 教训=没有账就没有验收。
3. **Rx-3+Rx-4（第二批，同文件族）**：通道固定地板与红路径成本；注意 gateway 同文件在飞批串行纪律（快照 §五），与在飞批错峰投递。
4. **Rx-5（随战役需要）**：Owner 已授权，机械插队，半天级。
5. **Rx-6/Rx-7/Rx-8**：等 Rx-2 数据或 R2 复测后按判据立项，防"未取证先动刀"（T10 学费条款）。
