# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] scripts.governance.commit_queue_landing
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；scripts.commit_queue（队列协议/LandingResult）；scripts.session_worktree（环境三件套备置真源 _provision_worktree_env，延迟 import）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway（全门禁落盘执行体）；zephyr.security.access_control.session_concurrency（主仓 session registry）
# [CONSUMERS] 全部 AI session（drain_queue(landing=...) 真落盘注入点）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway._commit_auto（flag ON 时 reroute 目标，延迟 import）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 永不改主工作区脏文件（66 号 §9.7 受控放松 2026-08-23：只写专用 worktree + 对象库 + dev ref CAS；landing 后主工作区受限收敛——仅当文件与旧 HEAD 逐字节一致才快进写入新内容，脏/缺失/删除冲突一律跳过留痕，零 WIP 丢失风险）；单写者（仅 Serializer lease 持有者经 drain 调用）；幂等不双落（done/landed_id + is-ancestor + 标记 grep 三重判定）；门禁一套不裁（GitCommitGateway 全门禁链零适配，worktree 形态 100 门禁天然生效）；CAS 冲突/基底冲突→死信不卡队；**瞬态环境失败（git index.lock 争用 / Windows 句柄占用致 reset --hard unlink 失败 / 全局提交锁 LOCK_TIMEOUT；特征串真源=_TRANSIENT_GIT_MARKERS）→ 抛 LandingEnvironmentError 让项退回 pending，绝不死信**；**热册三连（FOREIGN-CHANGE/HELD-OVERLAP/HOT-FILE-BASE-FRESHNESS 集中打 module_translation/capability_canonical 两热册，结构性并发非物品违规）→ 抛 HotRegistryContentionError 同走退 pending+B5 attempts 退避通道，绝不死信回人工（A3 任务1 st-circ-a3-20260930）**；主工作区收敛 fail-open（landing 已成功，收敛异常仅留痕不改变结果）；worktree 环境备置（ensure_worktree 两出口经 scripts.session_worktree._provision_worktree_env 从主仓取 PG+CH 配置——门禁/reconciler 在 worktree 内与主区等价，不再 fail-open；备置失败仅 warning 不阻断落盘）；**k=4 通道池（st-k4-20260923）：投机并行验证+串行落地——drain_queue_pool 池级单 lease+单心跳线程，k 工各配独立 worktree/分支/gateway（_GlobalCommitLock 按 project_root 键控→门禁段真并行），路径锁同路径项门禁段前串行化（防跨 session claim 冲突+整文件互踩），dev ref CAS 唯一串行落地点，冲突→_pool_cas_replay 落地段重放不重跑门禁（注册表同册=条目级三向合并重放吸收零丢失；无重叠=commit-tree re-parent；非注册表同路径=死信零覆盖）；k=1（thresholds commit_queue_landing_pool_workers）=legacy 逐字节降级**；env 名册/import 同源（gateway roster_root=主仓根，三选一之③，q-0006/q-0007 死信治本）；快照写后读回自验（M5.1 rsync -c 语义：write_bytes 即读回 sha256 比对，注册表族基准=三向合并后字节、普通文件=袋内 blob_sha256，delete/noop 豁免）；gate 装载失败新鲜子进程判别（M5.2：fresh 同败=确定性册坏即死信，fresh 通过=daemon 纪元陈旧退 pending，配 env_retry 上限）；改道入队前锁外预检（M1.2：blocking 返回 COMMIT_FAILED 拒不降级直提，预检设施异常才放行+审计）
# [MODIFY-GUARD] 66 号备忘 §6.3 MVP 形态 + §8 幂等算法 + §9 边界；08 号文 §4.2 步骤 3/5；[GW:{sid}:{qid}] 标记格式（POST-COMMIT-GUARD / REFERENCE-TRANSACTION-GUARD 消费方）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] __call__ 永不抛普通 Exception（落盘失败→LandingResult(ok=False, reason) 进死信）；cq.LandingEnvironmentError 按设计向上逃逸（drain 捕获后项退回 pending + 终止本轮），但带 per-item 计数（item meta env_retry/snapshot_retry，持久化进项 JSON），同类失败≥3 次升级死信带处方防活锁（M5.1/M5.2，st-qcure-20260925）；SnapshotVerifyError=快照写后读回自验失败的专类（继承 LandingEnvironmentError）；BaseException 向上传播（模拟进程崩溃语义，项留 processing 等回收）
# [TESTS] tests/governance/test_commit_queue_integration.py; tests/governance/test_commit_queue_landing.py
# [A_module] module_id=MOD-GOV-047 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""commit_queue_landing.py — 提交队列 B 段：专用 worktree 真落盘 + _commit_auto 改道预备

真源
----
- 66 号备忘 §6.3（Serializer 主循环 MVP 形态：专用 worktree + 现有 gateway 全门禁零适配）、
  §6.4（逐文件快进冲突判定/死信）、§8（is-ancestor 幂等判定）、§9.7（永不改主工作区文件）。
- 08 号文 §4.2 步骤 3（专用 worktree 落盘）/步骤 5（_commit_auto 改道入队）+ §5 ⑪
  （无双写者终态——改道经 feature flag 门控灰度，启用=Owner 窗口批准，宪章 B-007）。

落盘流水线（每项一次，仅 Serializer lease 持有者经 drain_queue(landing=...) 调用）
--------------------------------------------------------------------------------
1. 幂等短路：done/ 已记 landed_id 且 is-ancestor 命中 → 直接复用；否则按
   `[GW:{sid}:{qid}]` 标记 grep dev 历史，命中 → 复用已落 commit（不重跑）。
2. 专用 worktree 同步：`reset --hard refs/heads/dev` + `clean -fd`（66 号 §6.3 伪代码
   的 merge --ff-only + clean + reset 三步由 reset --hard <ref> 一步收敛——语义等效且
   能自愈 POST-COMMIT-GUARD reset / 孤儿 commit 等分支漂移；§11 #6 不变量：每项处理前
   worktree HEAD == dev HEAD 且工作区 clean）。
3. 基底冲突判定（66 号 §6.4 逐文件快进）：item.base_head 与当前 dev 不一致时，
   diff base..dev 触及本项路径 → 冲突 → 死信（不静默覆盖他人推进）。
4. 快照应用前 claim（worktree 路径、净树基线为空 → FOREIGN-CHANGE 放行），blob 落成
   真实文件（delete action 删文件），经 GitCommitGateway.commit() 全门禁链零适配提交
   （--no-verify + pathspec 限定，message 附 `[GW:{sid}:{qid}]` 标记，网关再补
   `[GW:{sid}]` 尾标——两个 shell guard 均为 `[GW:` 子串匹配，零适配兼容）。
5. CAS 推进 dev：`git update-ref refs/heads/dev <new> <old>`（单写者免费保险，
   66 号 §6.3 修正 4；git 2.48.1 实证对已 checkout 的 dev 亦可用）。CAS 失败 =
   有队列外写入者插队 → diff old..new_dev 触及本项路径 → 冲突死信；否则重同步重试
   （上限 _MAX_CAS_RETRIES 次，耗尽 → 死信留人工）。

标记格式说明（B 段裁定）
------------------------
66 号 §8/§2.4 模板写作 `[GW:{sid}:q-{qid}]`；qid 自身即 `q-{date}-{sid}-{seq}` 完整形式
（66 号 §6.1），故模板中 `{qid}` 占位代入完整 qid 后 `q-` 前缀恰出现一次——本实现
`queue_marker(sid, qid) == f"[GW:{sid}:{qid}]"`，与模板意图逐字符一致
（如 [GW:sess-a:q-20260821-sess-a-0001]）。两 guard 的识别均为 `[GW:` 子串/grep，
sess- 前缀解析位不受影响（post_commit_guard sed `sess-[^]:}]*` 在冒号前截断）。

worktree 位置与门禁诚实记录
---------------------------
专用 worktree 落 `<queue_root>/worktree`（生产即 .runtime/commit_queue/worktree，
08 号文 §4.2 步骤 3 任务口径；66 号原文 .aidrafts/serializer/ 的替代位——.runtime
整体 gitignored，queue 同目录共命运）。由此带来两个已核实的门禁交互：

- WORKTREE-REQUIRED（priority=44）：其「在 worktree 内」判定基于进程 cwd 是否落在
  .aidrafts//.worktrees/ 下（worktree_manager.get_current_worktree），.runtime 路径
  不命中。落盘 commit 传 allow_non_worktree=True——gate 自有逃生参数，不修改不放宽
  任何判定；其防护意图（防共享 index 搭便车）由专用 worktree 的独立 checkout+index
  结构性满足，且每个队列 commit 带 [GW:{sid}:{qid}] 标记留痕（65 号 2026-08-13
  用户裁定反转口径：逃生通道 AI 可默认使用 + GW 标记留痕）。
- FORGED-GW-MARKER（priority=29）：commit_message 含 [GW: 且 sid 在其自建的
  worktree 级 registry 查无 → 需 ZEPHYR_COMMIT_GATEWAY=1 env 逃生。落盘在调
  gateway.commit() 期间置该 env（try/finally 恢复）——语义如实（确为网关内部调用），
  与 run_git 每次 subprocess 置同款 env 一致。

_commit_auto 改道（flag 门控灰度，B-007 合规核心）
--------------------------------------------------
``reroute_auto_commit_to_queue`` 是 flag ON 时 _commit_auto 的改道目标（git_commit_gateway
内一处改动，66 号 §7）：快照读盘 → enqueue_item（base_head=dev HEAD 落袋，删除文件走
deletes 通道）→ 自举排空尝试（best-effort）→ 返回 CommitResult(OK, QUEUED:{qid})。
flag OFF（默认 ALWAYS_OFF）时 _commit_auto 现状直提不变——OFF 期 reconciler 直提照旧，
这不是双写者终态而是门控灰度（08 号文 §5 ⑪ 的灰度语义化）；**flag 启用属 Owner 窗口
（宪章 B-007 production 行为变更），启用后单写者不变量生效**——dev 只经 Serializer
通道落盘，可用 ``assert_single_writer_dev_history`` 机械验证。

fail-safe 降级（08 号文 §4.2 步骤 5 任务口径）：改道通道任何异常（设施 import 失败/
快照读盘失败/入队异常含 QueueReject）由 _commit_auto 捕获 → logging.warning 留痕 +
降级现行直提——队列异常不阻塞 reconciler 工作流。降级非静默：①warning 日志；
②降级 commit 仅带 [GW:{sid}:auto] 无队列标记，``assert_single_writer_dev_history``
会机械点名为违例（Owner 对账可见）；③降级窗口是瞬态双写者形态，队列设施修复后即
恢复单写者。人工 commit() 完整路径永不入队——人工提交是 Serializer 外唯一合法写者
（05 号裁定语义）。

flag OFF 灰度期已知过渡语义（如实记录，非缺陷）：队列落盘触发的 post-commit reconciler
链在 serializer worktree 上跑，其 auto-commit 直提落在 serializer 分支、下次 reset
--hard 时被遗弃（派生文件由后续 reconcile 重生成）；flag ON 后这些 auto-commit 改道
入队，经 Serializer 落 dev 完成闭环。
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import scripts.commit_queue as cq
from scripts.governance._shared.thresholds import get as _get_threshold  # 治本(AI-20 P0③ 2026-09-05): 阈值SSoT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_SERIALIZER_BRANCH = "serializer/commit-queue"  # 专用 worktree 检出的分支（随每项 reset 到 dev）
_WORKTREE_DIR_NAME = "worktree"  # <queue_root>/worktree——任务口径专用目录（08 号文 §4.2 步骤 3）
_NOOP_LANDED_PREFIX = "noop@"  # no-op 落地哨兵（2026-09-16）：快照与 HEAD 逐字节一致（幂等空转）
# 时 landed_id 记为 "noop@<old_dev>"——裸记 old_dev 会错位成他会话提交（q-20260916-0004 实证：
# done 指向 st-redfix 的 commit，排查者误以为内容已随其落库）。_already_landed 剥前缀后判 is-ancestor。
_MAX_CAS_RETRIES = 6  # dev CAS 冲突重试上限（66 号 §8：重放产生同内容 commit，CAS 保护不分叉）
# 上限 3→6（2026-09-16 q-20260916-st-consrep-20260916-0013 死信实证）：8 会话并发期
# 单轮落地 ~70s，3 次重试全被队列外写入者插队耗尽 → 无辜物品死信回退人工。CAS 重放
# 幂等（同内容 commit），提高上限不产生分叉，只是把"人工 requeue"换成"自动重同步"。
_GIT_TIMEOUT_SECONDS = _get_threshold(
    "git_operations.commit_queue_git_timeout_seconds", 120
)  # 治本(AI-20 P0③): 从SSoT读取；与 worktree_pool.run_git 同款
# 全局提交锁等待（2026-09-16 q-…-0009/0010/0011 死信实证）：gateway 缺省 60s 在并发
# 提交期必然撞锁（另一会话正 commit），而锁争用是**瞬态**——排队等待即可落地，死信是
# 假失败。落地侧把等待放宽到 300s（队列本就异步、无交互延迟预算），并把仍超时归为
# 环境失败（项退回 pending，绝不死信）。刻意用普通常量而非新增 thresholds 注册键：
# 这是队列落地内部实现细节，不是可调业务阈值（避免注册表膨胀）。
_LANDING_LOCK_WAIT_SECONDS = 300.0
_MAIN_WS_SYNC_AUDIT_NAME = (
    "main_workspace_sync.jsonl"  # <queue_root>/ 下——主工作区收敛跳过/异常留痕（66 号 §9.7 受控放松 2026-08-23）
)

# 队列标记正则：[GW:{sid}:{qid}]——sid 字符集 [A-Za-z0-9._-]（入队校验保证无冒号/右括号）
_QUEUE_MARKER_RE = re.compile(r"\[GW:[^\]:\s]+:q-[^\]\s]+\]")
# 提交归属提取（存量兜底判定用）：直提形态 [GW:sid] 与队列形态 [GW:sid:q-xxx] 都要认，
# 故不能用上面的 _QUEUE_MARKER_RE（它强制 :q- 段，只用于假落地防线的标记核验）。
_GW_OWNER_RE = re.compile(r"\[GW:([^:\]\s]+)")

# 派生计数标量 → 集合段（按册名）——**手工点名层**。与 GATE-21 selfcheck 的 pairs 同一份
# 口径——检测器（判红）与落地侧自愈（改对）必须同源，否则"检测说 174、修补写 180"会变成
# 新漂移源；两处一致性由 tests/governance/test_commit_queue_base_head.py 的口径同源尺断言。
# 生效全集 = 自动发现（SKIP-6，discover_derived_total_pairs）⊕ 本表（同名手工覆盖），
# 统一经 all_derived_total_pairs() 消费；本表保留为覆盖层=净零（不删任何既有条目）。
_MANUAL_DERIVED_TOTAL_PAIRS: dict[str, dict[str, str]] = {
    "gate_registry.yaml": {"total_gates": "gates"},
    "rule_catalog_registry.yaml": {"total_files": "files"},
    # 2026-09-27 st-chief6-20260927 补：in_process 门禁名册漏在册 ⇒ 该册标量走不了队列（两投皆
    # merged==ours→noop→记 done 而盘上零变化，同型先例 FMS 38168467d1"条目+计数同批"落盘仍 103）。
    "in_process_gate_registry.yaml": {"total_gates": "gates"},
}


def _git_blob_sha(data: bytes) -> str:
    """内容字节 → git blob id（与 base_blob / _pool_head_reader 同一 id 空间）。

    三套哈希口径不可互换（bytes-sha ≠ git-blob-sha ≠ content_sha256）；此处必须用
    git 那一套才能与 ls-tree 输出直接比对。
    """
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


# 网关 env 标记（FORGED-GW-MARKER env 逃生语义=确为网关内部调用；与 run_git 同款）
_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"
# Serializer 可信 git 调用 env（66 号 §4 裁定 7 plumbing 白名单 + worktree_pool fast-path 先例）
_SERIALIZER_MODE_ENV = "ZEPHYR_SERIALIZER_MODE"
_GIT_GUARD_FAST_PATH_ENV = "ZEPHYR_GIT_GUARD_FAST_PATH"

# 瞬态 git 环境失败特征串（大小写不敏感匹配）：全部是"外部进程/OS 一时占着文件"，
# 与队列项内容无关——重放即可落地，死信是假失败。
#   index.lock / Unable to create —— 他会话 commit 持索引锁（2026-09-10 二阶死信：26 项）
#   unable to unlink / Permission denied / being used by another process /
#   The process cannot access the file —— Windows 句柄占用（2026-09-16
#   q-20260916-st-consrep-20260916-0018 死信实证：reset --hard 撞
#   "unable to unlink old 'docs/.../business_data_categories.yaml': Invalid argument"，
#   一个只含 13 个 consensus 文件的合法批次被误判物品失败）。
# 刻意不收 "Invalid argument" 裸串：它太宽（真 bug 也报这个），只收 git 的 unlink/占用
# 原话——句柄一释放重放就过，与 index.lock 同款语义。
#   timeout after —— git 子进程墙钟超时被强杀（_run_git 超时分支原话 "… -> timeout
#   after Ns (killed)"）：慢盘/杀毒扫描类瞬态慢，重放即愈（2026-09-30 批 LANDING-
#   TIMEOUT 死因实证）。与 LOCK_TIMEOUT 同款"等待即愈"语义。
#   winerror 233 / 管道的另一端 / no process on the other end —— Windows 命名管道
#   对端瞬断（OSError [WinError 233] 管道的另一端上无任何进程；存量死信 77 封、
#   7 天单项最大伪命中实证）：git/子进程通信管道一时无人接听，重放即愈。中英双
#   形态都收（中文 Windows 报中文、英文环境报英文原话）。
_TRANSIENT_GIT_MARKERS = (
    "index.lock",
    "unable to create",
    "unable to unlink",
    "permission denied",
    "being used by another process",
    "the process cannot access the file",
    "timeout after",
    "winerror 233",
    "管道的另一端",
    "no process on the other end",
)


def _is_transient_git_error(exc: BaseException | str) -> bool:
    """git 失败是否属瞬态环境类（锁争用/句柄占用/管道瞬断/墙钟超时）——是则项退回 pending，绝不死信。"""
    text = str(exc).lower()
    return any(marker in text for marker in _TRANSIENT_GIT_MARKERS)


# 瞬态 gate 检查器环境失败特征串：gate 的外部检查器子进程**无法执行**（如
# check_frontmatter_metadata.py 在 worktree 内起不来——环境问题非物品违规）时，
# ttl_gate 等以 "…execution failed: …" 报 COMMIT_FAILED。frontmatter 本身没被判过，
# 死信是假失败——归环境类退 pending 配 env_retry 计数闸（≤3 次防活锁；2026-09-30
# 批 TTL-METADATA execution failed 死因实证）。真 frontmatter 违规报 "FAIL: …" 原话
# 不落此表，门禁死信语义零放松。
_TRANSIENT_GATE_ENV_MARKERS = ("execution failed",)


def _is_transient_env_failure(exc: BaseException | str) -> bool:
    """落地失败是否瞬态环境类：git 瞬态（_is_transient_git_error）∪ 检查器无法执行。

    drain 泛化异常出口、pool 泛化异常出口与 COMMIT_FAILED 结果出口统一消费本判据
    ——特征串单一真源（_is_transient_git_error 判据思路同款，两表合一消费口）。
    """
    text = str(exc).lower()
    return _is_transient_git_error(text) or any(m in text for m in _TRANSIENT_GATE_ENV_MARKERS)


# ── 热册三连自动改道（A3 任务1，st-circ-a3-20260930，深挖矿处方）─────────────────
# 病根：FOREIGN-CHANGE(42)/HOT-FILE-BASE-FRESHNESS(31)/HELD-OVERLAP(13) 三类阻断
# 集中打 module_translation_registry.yaml 与 capability_canonical_file_registry.yaml
# 两册——多会话并发期对同一热册 claim/落盘互踩是**结构性并发**，不是物品违规；
# 死信回人工是假失败（等持册会话落地后重投即自愈，注册表族落地本就三向合并吸收）。
# 治本：landing 侧识别这三类阻断 → 抛 HotRegistryContentionError（LandingEnvironmentError
# 子类）→ drain/pool 既有 env 通道退回 pending + B5 attempts 退避（≥3 次 15min/次惩罚、
# ≥5 次拾取死信防活锁——终态死因归 env 类可 requeue，处方可行动）。零新增计数器
# （内收原则：退避/升级全部复用队列 B5 既有机制）。
_CONTENTION_BLOCK_STATUSES: Final = frozenset({"FOREIGN_CHANGE_VIOLATION", "HELD_OVERLAP_VIOLATION"})
_CONTENTION_BLOCK_GATE_MARKERS: Final = ("HOT-FILE-BASE-FRESHNESS",)


def is_hot_registry_contention_block(status_name: str, message: str) -> bool:
    """网关落盘失败是否属热册并发类（FOREIGN-CHANGE/HELD-OVERLAP 专用 status 或
    COMMIT_FAILED 消息带 HOT-FILE-BASE-FRESHNESS 门禁标记）。

    仅落地侧消费：worktree 路径 claim 基线为空，FOREIGN-CHANGE 命中=共享暂存区/
    热册互踩的结构性并发，不是袋内容违规；HELD-OVERLAP 命中=他会话正持册（等让位）；
    HOT-FILE-BASE-FRESHNESS 命中=基底被他会话推进（重同步+三向合并即自愈）。
    """
    if status_name in _CONTENTION_BLOCK_STATUSES:
        return True
    return status_name == "COMMIT_FAILED" and any(m in message for m in _CONTENTION_BLOCK_GATE_MARKERS)


class HotRegistryContentionError(cq.LandingEnvironmentError):
    """热册并发阻断专类（A3 任务1）——项退回 pending 退避重投，绝不死信回人工。

    继承 LandingEnvironmentError：drain/pool 既有 env 分支按「环境失败≠物品失败」
    退 pending + attempts+1（B5 退避）+ 终止本轮等下次自举。``retried_key="contention"``
    供 pool 环境分支识别「免烧 env_retry 计数」——热册并发不消耗环境失败预算，
    其终态由队列 B5 attempts≥5 拾取死信兜底（死因随末次失败文本归 env 类可 requeue）。
    """

    retried_key = "contention"


# ---------------------------------------------------------------------------
# 注册表族落地三向合并（W2 治本，2026-09-22 注册表事故）
# ---------------------------------------------------------------------------
# 病根：_apply_snapshot 对快照文件 write_bytes() 整文件覆盖——sim-launch 15:17 的
# fb5a7821d 用 01:35 基底快照落地，一个 blob 写回抹掉 103 条已提交身份。逐文件快进
# 冲突判定（_conflict_reason）只在 base_head 有效且 diff 触及同路径时兜底，无 base_head
# 的旧格式项/跨 list 族代数抵消全部漏网。
# 治本：注册表族文件（_REGISTRY_CATALOGS_PREFIX 且 .yaml）落地时改**条目级三向合并**
# ——base=快照基底（item.base_head，缺省 old_dev 父提交）、ours=当前 dev、theirs=快照
# 内容；条目身份复用 registry_mass_deletion_gate.entry_identity_key（每条首个标量字段），
# 落地侧与门禁侧同一份身份定义。合并规则（DISPATCH_v1 Lane A 卡片 W2）：
#   base 有+ours 无+theirs 有 → 采纳（ours 侧合法退役除外——条目引用路径盘上与 HEAD
#                               双不存在）；base 有+ours 有+theirs 无 → 保留 ours（快照
#                               侧删除不镇压现役）；base 无+theirs 有 → 插入；同键内容
#                               异（三方各自改）→ 死信带双方条目全文。
# 非注册表文件维持整文件语义零变更；合并在落地器内做，enqueue 侧快照格式零改动
# （向后兼容，旧队列项直接受益）。

_REGISTRY_CATALOGS_PREFIX = "docs/01_policies_and_standards/_registry/catalogs/"
# 合并死信详情里单侧条目 dump 的截断上限（防 reason 超 2000 字符截断丢双侧原文）
_MERGE_CONFLICT_DUMP_CHARS = 800

# SKIP-6 自动发现结果进程内缓存（None=未扫描；landing 长驻进程只扫一次）
_DISCOVERED_PAIRS_CACHE: dict[str, dict[str, str]] | None = None


def discover_derived_total_pairs(catalogs_dir: Path | str | None = None) -> dict[str, dict[str, str]]:
    """SKIP-6 自动发现器（2026-09-28）：扫描注册表目录，收编派生计数配对册。

    病根：_MANUAL_DERIVED_TOTAL_PAIRS 是手工点名表——每出现一只新的 total_ 册就要
    记得"再点一次名"，漏点=该册标量走不了队列（q-0006/FMS 38168467d1 同型假成功），
    结构性复发点。现口径：扫描 catalogs/*.yaml，凡 `total_<x>:` 顶层**整数**标量与
    同名顶层 `<x>:` 集合段共存、且**当前自洽**（声明值==段实际长度）的册即收编。

    三重保守面（发现器只做收编，绝不发明配对）：
    ① "曾经自洽"是收编前提——语义凑巧/故意不等长的册（total 统计口径≠段长）永远
       不会同时满足同名+整数+等长三条件，不会被误配后在落地时刷毁语义值；
    ② 解析失败/非映射册/无配对册一律跳过留痕（_index.yaml 等 markdown 混写件），
       单册失败绝不拖垮发现器；
    ③ 手工点名表保留为覆盖层：all_derived_total_pairs() 同名手工赢，发现集只做增量
       （净零——不删任何既有条目）。
    """
    import yaml  # noqa: PLC0415 — landing 模块保持 stdlib 顶层 import（与 gate lazy 风格一致）

    base = (
        Path(catalogs_dir)
        if catalogs_dir is not None
        else Path(__file__).resolve().parents[2] / _REGISTRY_CATALOGS_PREFIX
    )
    out: dict[str, dict[str, str]] = {}
    if not base.is_dir():
        logger.warning("[landing] 派生标量发现器：目录不存在 %s（退手工点名表）", base)
        return out
    for p in sorted(base.glob("*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 — 单册解析失败不拖垮发现器
            logger.info("[landing] 派生标量发现器跳过不可解析册 %s: %s", p.name, exc)
            continue
        if not isinstance(data, dict):
            continue
        pairs: dict[str, str] = {}
        for key, val in data.items():
            ks = key if isinstance(key, str) else str(key)
            if not ks.startswith("total_") or isinstance(val, bool) or not isinstance(val, int):
                continue
            section_key = ks[len("total_") :]
            section = data.get(section_key)
            if isinstance(section, (list, dict)) and val == len(section):
                pairs[ks] = section_key
        if pairs:
            out[p.name] = pairs
    return out


def all_derived_total_pairs() -> dict[str, dict[str, str]]:
    """生效配对全集 = SKIP-6 自动发现 ⊕ 手工点名层（同名手工覆盖）。

    检测（GATE-21 自洽台）/落地自愈（_heal_derived_totals）/落地前自证读回
    （_noop_absorption_verdict）三者唯一同源消费口——任何一方单独另配一张表
    都会重演"检测说 174、修补写 180"的漂移。发现器故障 fail-open 退手工表
    （自愈覆盖面收窄，绝不阻断落地）。结果进程内缓存一次。
    """
    global _DISCOVERED_PAIRS_CACHE
    if _DISCOVERED_PAIRS_CACHE is None:
        try:
            _DISCOVERED_PAIRS_CACHE = discover_derived_total_pairs()
        except Exception as exc:  # noqa: BLE001 — fail-open：发现器故障不阻断落地
            logger.warning("[landing] 派生标量自动发现失败（退手工点名表）: %s", exc)
            _DISCOVERED_PAIRS_CACHE = {}
    return {**_DISCOVERED_PAIRS_CACHE, **_MANUAL_DERIVED_TOTAL_PAIRS}


def is_registry_mergeable(rel: str) -> bool:
    """仓内相对路径是否命中注册表族（W2 三向合并作用域；与 gate 的
    REGISTRY-MASS-DELETION 触发目录同源语义，按前缀族判定不逐文件枚举）。"""
    norm = rel.replace("\\", "/")
    return norm.startswith(_REGISTRY_CATALOGS_PREFIX) and norm.endswith(".yaml")


@dataclass
class _RegistryFamily:
    """一个顶层 list 族的切分结果（头行号 + 条目块）。"""

    head_line: int  # 族键行（0-based；顶层 list 文件为 0）
    blocks: list[_RegistryEntryBlock]


@dataclass
class _RegistryEntryBlock:
    """单条目在原文中的行区间与语义对象。"""

    identity: str | None  # gate 同款身份键（None=判不了，合并器 fail-closed 死信）
    data: object  # 条目 yaml 语义对象（dict）
    start: int  # 起始行（0-based，含）
    end: int  # 结束行（0-based，含）
    text: str  # 原文块（keepends，含行尾）


def _split_registry_entries(
    text: str, identity_fn: object | None = None
) -> tuple[dict[str | None, _RegistryFamily], str | None]:
    """YAML 文本 → {顶层 list 键: 族切分}（yaml.compose 节点行号法，原文块零重排）。

    Args:
        identity_fn: 可选 ``(family_key, entry_data) -> str | None``——夜班手术二a
            （st-nightfix-20260923）族身份作用域化钩子；None=默认复合键
            （_merge_entry_identity）。渲染自检必须与切分用同一 fn，否则身份集
            比对必假漂移。

    Returns:
        (families, error)；解析失败/结构非 mapping+list 组合时 error 非 None。
    """
    import yaml  # noqa: PLC0415 — landing 模块保持 stdlib 顶层 import（与 gate lazy 风格一致）

    try:
        node = yaml.compose(text)
    except Exception as exc:  # noqa: BLE001 — 解析失败由调用方死信
        return {}, f"yaml.compose 解析失败: {exc}"
    if node is None:
        return {}, None  # 空文件 = 无族无条目
    lines = text.splitlines(keepends=True)
    families: dict[str | None, _RegistryFamily] = {}
    seq_nodes: list[tuple[str | None, object, int, int]] = []
    node_cls = type(node).__name__  # 鸭子判定用类型名（不顶层 import yaml.SequenceNode）
    if node_cls == "SequenceNode":
        seq_nodes.append((None, node, 0, len(lines)))
    elif node_cls == "MappingNode":
        pairs = node.value
        for i, (key_node, value_node) in enumerate(pairs):
            if type(value_node).__name__ == "SequenceNode":
                # 族右边界 = 下一兄弟键行（族末条目 end_mark 会指到该键，须截尾——
                # smoke8 实测：末条目块吞进 `others:` 行致 safe_load 失败）；末族=文件尾
                next_bound = pairs[i + 1][0].start_mark.line if i + 1 < len(pairs) else len(lines)
                seq_nodes.append((str(key_node.value), value_node, key_node.start_mark.line, next_bound))
    # ScalarNode / 空文档 → 无族（无条目可合并，调用方走 ours/theirs 一致性短路或 noop）
    for list_key, seq, head_line, end_bound in seq_nodes:
        blocks: list[_RegistryEntryBlock] = []
        item_nodes = list(seq.value)
        for i, item_node in enumerate(item_nodes):
            start = item_node.start_mark.line
            # PyYAML end_mark 指向节点结束后的位置——block 条目下恰是**下一条目的
            # start**（实测 end_mark.line == next.start_mark.line），故同族内用
            # 「下一 start-1」截尾最可靠；族末条目受族右边界约束。
            hard_bound = min(item_nodes[i + 1].start_mark.line, end_bound) if i + 1 < len(item_nodes) else end_bound
            end = max(min(item_node.end_mark.line, hard_bound - 1, len(lines) - 1), start)
            block_text = "".join(lines[start : end + 1])
            try:
                data = yaml.safe_load(block_text)
            except Exception as exc:  # noqa: BLE001
                return {}, f"条目块解析失败（{list_key} 第 {start + 1} 行）: {exc}"
            if isinstance(data, list) and len(data) == 1:
                # 块文本以 `- ` 开头（带原缩进），单独解析产出单元素 list——解包回条目本体
                data = data[0]
            blocks.append(
                _RegistryEntryBlock(
                    identity=(_merge_entry_identity(data) if identity_fn is None else identity_fn(list_key, data)),
                    data=data,
                    start=start,
                    end=end,
                    text=block_text,
                )
            )
        families[list_key] = _RegistryFamily(head_line=head_line, blocks=blocks)
    return families, None


def _is_seq_node(node: object) -> bool:
    """（保留兼容名）yaml 序列节点判定——已由 _split_registry_entries 内联类型名分支取代。"""
    return type(node).__name__ == "SequenceNode" and isinstance(getattr(node, "value", None), list)


def _entry_identity(data: object) -> str | None:
    """条目身份（gate 同款真源委托；import 失败等异常 → None → 合并器死信方向）。

    池化批（st-k4）反方案：registry_family/ 迁移延后另案，import 维持根路径原位
    （Lane A 批预设动作；旧 flat 路径模块同批退役，FOLDER-CAPACITY 121>120 解堵）。
    """
    try:
        from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (  # noqa: PLC0415
            entry_identity_key,
        )

        return entry_identity_key(data)
    except Exception:  # noqa: BLE001 — 判不了按 None（fail-closed 死信，不静默合并）
        return None


def _merge_entry_identity(data: object) -> str | None:
    """合并器复合身份键（W2 热修，q-20260923-st-gateaudit-20260922-0078 实战）：
    gate 单键 + token 并入。

    实战缺陷：gate 首标量字段单键（creation_tokens 族=file）在「同文件合法持多条
    token」（blueprint 双 capability/night-gw 新旧并存，HEAD 41 文件此形态）下同侧
    键重复 → 误死信。修法（热修令）：键升级为 ``首标量|token=值`` 复合——首字段=file
    时即 (file, token)，与 batch_creation_tokens._entry_keys_of_text 的 B22 立法
    身份同构；无 token 字段的注册表（ruling_id 单键）自动退化为 gate 单键，通用性
    零破坏。复合键下同键重复=同 file 同 token 两条（真非法）→ 死信判据保留。

    刻意不改 gate 的 entry_identity_key（其身份集语义与既有测试断言绑死单键格式；
    本函数为合并器本地扩展——复合键是单键的细化不是分叉：单键判「存在」者复合键
    必判「存在」，合并器消失检测更严方向安全）。
    """
    base = _entry_identity(data)
    if base is None or not isinstance(data, dict):
        return base
    token = data.get("token")
    if isinstance(token, (str, int, float)) and token is not None:
        return f"{base}|token={token}"
    return base


# 夜班手术二a（st-nightfix-20260923，Lane 0b 授权）：module_translation_registry
# 族身份作用域化。实测缺陷：该册 entries/algo_submodules 两族合法持同 module_path
# 多条（HEAD 7196/968 条实测 194 个 module_path 多条形态），默认首标量单键一进
# 合并即"同侧身份键重复"死信——翻译册落地结构性死锁，逼出直连绕行
# （a0562e88f2 批A 同款死两次实证）。真键取条目内判别字段（dispatch ②a：
# "module_path+条目内 term 级"；entries 族无 term 字段，实测判别=name 级）。
_TRANSLATION_REGISTRY_SUFFIX = "module_translation_registry.yaml"


def _translation_family_identity(family_key: str | None, data: object) -> str | None:
    """翻译册族真键：entries=(module_path,name_zh,name_en)，algo_submodules=(module_path,node_id)。

    其余族（unique_key 元数据/battle_map_steps/battle_map_cross_cutting）→ 默认复合键
    （不越权造键）；module_path 缺失/非标量 → 退默认复合键（判不了不硬造）；
    非 dict → None（死信方向）。
    """
    if not isinstance(data, dict):
        return None
    base = _merge_entry_identity(data)
    if family_key not in ("entries", "algo_submodules"):
        return base
    mp = data.get("module_path")
    if not isinstance(mp, str) or not mp:
        return base
    if family_key == "algo_submodules":
        node = data.get("node_id")
        return f"{base}|mp={mp}|node={node}" if node else base
    nz = data.get("name_zh")
    ne = data.get("name_en")
    if not (nz or ne):
        return base
    return f"{base}|mp={mp}|name={nz}|{ne}"


_DECL_KEY_PREFIX = "decl|"  # 声明键命名空间前缀（与默认复合键空间隔离，混轨不撞键）


def _decl_fields(raw: object) -> tuple[str, ...] | None:
    """声明字段清单归一：全为非空 str 才有效；空/含非 str → None（该声明退化）。"""
    if not isinstance(raw, list) or not raw:
        return None
    if not all(isinstance(f, str) and f for f in raw):
        return None
    return tuple(raw)


def _unique_key_decl(text: str) -> dict[str | None, tuple[str, ...]] | None:
    """册头 ``unique_key`` 声明解析并归一（L1 文件自声明=SSOT，QMine A1 件③）。

    支持两形态（实测 36/71 册自声明）：``[field,...]``=全册默认键（functional_domain
    [domain,subdomain]/terminology [category,en] 形态）；``{family: [field,...]}``=
    按族键（data_asset_registry 形态）。返回 {None: 默认键, 族名: 族键}；无声明/
    解析失败/字段清单退化 → None（调用方退现状，不引入新死法）。
    """
    import yaml  # noqa: PLC0415 — 与合并内核同款惰性 import

    try:
        doc = yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — 解析失败退现状
        return None
    if not isinstance(doc, dict):
        return None
    raw = doc.get("unique_key")
    if isinstance(raw, list):
        fields = _decl_fields(raw)
        return {None: fields} if fields else None
    if isinstance(raw, dict):
        decl: dict[str | None, tuple[str, ...]] = {}
        for fam, fields_raw in raw.items():
            fields = _decl_fields(fields_raw)
            if fields:
                decl[str(fam)] = fields
        return decl or None
    return None


def _safe_load_doc(text: str) -> dict | None:
    """yaml.safe_load 失败/非 dict → None（调用方退现状，解析死信交既有 _split 通道）。"""
    import yaml  # noqa: PLC0415

    try:
        d = yaml.safe_load(text)
    except Exception:  # noqa: BLE001
        return None
    return d if isinstance(d, dict) else None


def _entries_carry_declared_fields(entries: object, fields: tuple[str, ...]) -> bool:
    """族内 dict 条目是否全数携带声明标量字段（L1 逐族适用性校验）。

    族缺位（None/非 list）=该侧无此族 → 空真；族内无 dict 条目（纯标量元数据族）
    → 空真（passthrough 通道处理，与身份键无关）。
    """
    if not isinstance(entries, list):
        return True
    dict_entries = [e for e in entries if isinstance(e, dict)]
    return all(all(isinstance(e.get(f), (str, int, float, bool)) for f in fields) for e in dict_entries)


def _declared_family_plan(
    ours_text: str, theirs_text: str | None, base_text: str | None
) -> dict[str, tuple[str, ...]] | None:
    """声明驱动逐族适用性计划（QMine A1 件③）。三防线，不引入新死法：

    ① 三侧声明必须齐备且一致：theirs/base 任一侧声明缺失或不等 → None 整体退现状
       （防声明跨合并窗口漂移导致跨侧身份错配）；
    ② 逐族校验：**三侧**该族 dict 条目须全数携带声明标量字段，任一侧不满足 → 该族
       不进计划（退默认复合键，防单侧缺字段条目混轨→跨侧身份错配）；
    ③ 计划为空 → None（退现状）。
    """
    decl = _unique_key_decl(ours_text)
    if decl is None:
        return None
    ours_doc = _safe_load_doc(ours_text)
    if ours_doc is None:
        return None
    side_docs = [ours_doc]
    for t in (theirs_text, base_text):
        if t is None:
            continue
        if _unique_key_decl(t) != decl:
            return None
        other = _safe_load_doc(t)
        if other is None:
            return None
        side_docs.append(other)
    plan: dict[str, tuple[str, ...]] = {}
    for fam, entries in ours_doc.items():
        fields = decl.get(str(fam)) or decl.get(None)
        if not fields or not isinstance(entries, list):
            continue
        if all(_entries_carry_declared_fields(d.get(str(fam)), fields) for d in side_docs):
            plan[str(fam)] = fields
    return plan or None


def _declared_identity_from_plan(plan: dict[str, tuple[str, ...]]):
    """声明驱动族身份函数（闭包工厂）：声明字段值拼接 + token 复合后缀。

    键格式 ``decl|f1=v1|f2=v2[|token=t]``。token 后缀沿用 _merge_entry_identity 的
    复合细化——声明字段替换其首标量分量、token 分量保留：capability_canonical_file
    同 file 多 token 合法并存形态不被声明键错杀（q-0078 复形回归保护）。声明字段
    缺失/非标量的条目（防御兜底，plan 已三侧验证）→ 退默认复合键，绝不判 None
    引入新死法。
    """

    def _identity(family_key: str | None, data: object) -> str | None:
        fields = plan.get(family_key)
        if fields and isinstance(data, dict):
            parts: list[str] = []
            for f in fields:
                v = data.get(f)
                if not isinstance(v, (str, int, float, bool)):
                    parts = []
                    break
                parts.append(f"{f}={v}")
            if parts:
                key = _DECL_KEY_PREFIX + "|".join(parts)
                token = data.get("token")
                if isinstance(token, (str, int, float)) and token is not None:
                    key += f"|token={token}"
                return key
        return _merge_entry_identity(data)

    return _identity


def _family_identity_fn(
    rel_path: str,
    ours_text: str | None = None,
    theirs_text: str | None = None,
    base_text: str | None = None,
):
    """按文件路由族身份函数：翻译册→族真键；有 unique_key 声明且三侧校验齐备 →
    声明驱动（L1 SSOT——functional_domain/terminology 类被单键错杀的册由此治愈）；
    其余/声明不可用 → 默认复合键（零漂移退现状）。"""
    if rel_path.replace("\\\\", "/").endswith(_TRANSLATION_REGISTRY_SUFFIX):
        return _translation_family_identity
    if ours_text is not None:
        plan = _declared_family_plan(ours_text, theirs_text, base_text)
        if plan:
            return _declared_identity_from_plan(plan)
    return None


def _extract_entry_paths(data: object) -> list[str]:
    """条目内路径候选：递归收集「含 ``/``」或「带文件后缀」的字符串值（URL/绝对路径排除）。

    合法退役判据（W2/W3 同款）的原料——登记表惯例路径字段名不一
    （path/module_path/file/target…），按值形态机械提取不靠字段名白名单。
    后缀规则兜住单文件名（如 ``retired_doc.md``——无斜杠但显然是文件）。
    """
    out: list[str] = []

    def _walk(node: object) -> None:
        """_walk implementation."""
        if isinstance(node, str):
            norm = node.replace("\\", "/").strip()
            if norm.startswith(("/", "http://", "https://")):
                return
            if "/" in norm or Path(norm).suffix:
                out.append(norm)
        elif isinstance(node, dict):
            for v in node.values():
                _walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                _walk(v)

    _walk(data)
    return out


def _first_field_value_is_non_scalar(data: object) -> bool:
    """dict 条目首字段值是否非标量（QMine A1 件②：流式 list 元数据块的 dict 形态特征）。"""
    if not isinstance(data, dict) or not data:
        return False
    return not isinstance(next(iter(data.values())), (str, int, float, bool))


def _scalar_family_keys(fam_map: dict[str | None, _RegistryFamily]) -> set[str | None]:
    """passthrough 族集合：纯标量族 + 首字段非标量的 dict 形态元数据族（剔出合并空间）。

    两类形态同判（QMine A1 件②，工作簿 §4.1 L3 扩面）：
    - 族内全块非 dict——schema 元数据 list 特征（unique_key: [id]；Lane B
      THD-ALERT-007 q-0001 死信实证）；
    - 族内全块为 dict 且身份判不了且首字段值非标量——流式 list 的块文本含族键前缀
      （``tags: [a, b]`` 单行 → 每块 safe_load 出 ``{"tags": [...]}``），HEAD 6 册
      14 块活雷实测（fail_open scan_roots×2 / ai_autonomy tags×7 / chain
      related_arch×2 / compliance、feature_adjudication、registry_of_logs 各 1），
      任一落地触册即死「身份判不了」。
    共同点：条目级身份不可证（gate 对非 dict 跳过/首字段非标量判不了）→ 合并语义
    不成立 → passthrough 保留 ours 原样零结构漂移（与 drift 检查同向 fail-closed）。
    混合形态族（标量块与常规条目并存）不在此列，维持既有死信方向，不放宽。
    """
    out: set[str | None] = set()
    for k, fam in fam_map.items():
        if fam.blocks and (
            all(b.identity is None and not isinstance(b.data, dict) for b in fam.blocks)
            or all(
                b.identity is None and isinstance(b.data, dict) and _first_field_value_is_non_scalar(b.data)
                for b in fam.blocks
            )
        ):
            out.add(k)
    return out


def _split_passthrough_and_drift(
    ours_families: dict[str | None, _RegistryFamily],
    theirs_families: dict[str | None, _RegistryFamily],
    base_families: dict[str | None, _RegistryFamily],
    rel_path: str,
) -> tuple[set[str | None], str | None]:
    """纯标量族 passthrough 判定 + 结构漂移 fail-closed 检查。

    ours/theirs 双方该族均全标量 → 剔出合并空间（保留 ours 原样）；base 有该族且含
    结构化条目而 ours/theirs 标量化 → 结构漂移死信（防静默丢 base 条目）；base 无该
    文件（新增落地前置态）→ 不约束。theirs/base 出现 ours 没有的顶层 list 族 → 结构级
    重写非条目级编辑，死信回人工。
    """
    ours_scalar = _scalar_family_keys(ours_families)
    theirs_scalar = _scalar_family_keys(theirs_families)
    base_scalar = _scalar_family_keys(base_families)
    passthrough: set[str | None] = set()
    for k in ours_scalar & theirs_scalar:
        if base_families and k in base_families and k not in base_scalar:
            return set(), f"{rel_path}: 族 {k} 在 base 侧有结构化条目而 ours/theirs 为纯标量——结构漂移，死信回人工"
        passthrough.add(k)
    for side, fam in (("theirs(快照)", theirs_families), ("base", base_families)):
        drift = [k for k in fam if k not in ours_families]
        if drift:
            return set(), f"{rel_path}: {side} 存在 ours 缺失的顶层 list 族 {drift}——结构漂移，死信回人工"
    return passthrough, None


def _index_family_blocks(
    fam_map: dict[str | None, _RegistryFamily],
) -> tuple[dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]], str | None, int]:
    """族内条目按身份键建索引；身份判不了/同键真冲突 → 死信方向错误串。

    侧内判等去重（QMine A1 件①，st-qmine-20260925，工作簿 §4.2「重复的语义学」）：
    同键同侧两条先判等——``data`` 全等（yaml.safe_load 对象判等，覆盖字节级相同与
    仅重序列化的语义同；死信袋回放实测 33% 死亡属此形态，token 双发窗口样本 69%）
    → 真重复，静默去重保留首条并计数，不再白白陪死；``data`` 不等 → 同键异容=
    仓库态缺陷，死信且 detail 升级为结构化双条 dump（落地器无权择优，处方=对账器）。
    去重只做**侧内**、绝不跨侧：跨侧同键由既有三向规则处理（base 仲裁），静默吞
    任一侧才是吞条目（CRDT MV-register 双值并存待裁决语义）。

    Returns:
        (idx, error, dedup_count)；dedup_count=本侧静默去重条数（审计日志出口）。
    """
    idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]] = {}
    dedup_count = 0
    for fam_key, family in fam_map.items():
        for block in family.blocks:
            if block.identity is None:
                return {}, "存在身份判不了的条目（非 dict/首字段非标量）——合并语义不可证，死信回人工", 0
            dup = idx.get(block.identity)
            if dup is not None:
                if dup[2].data == block.data:
                    dedup_count += 1  # 真重复（字节同/token 双发/重序列化）——保留首条
                    continue
                return (
                    {},
                    (
                        f"同侧身份键重复且内容冲突（同键异容，仓库态缺陷）: {block.identity}"
                        f"——死信回人工；处方: 跑 registry 去重对账器核对存量，勿手拼 YAML\n"
                        f"--- 在册先条 (first) ---\n{_yaml_dump_short(dup[2].data, _MERGE_CONFLICT_DUMP_CHARS)}\n"
                        f"--- 重复后条 (dup) ---\n{_yaml_dump_short(block.data, _MERGE_CONFLICT_DUMP_CHARS)}"
                    ),
                    0,
                )
            idx[block.identity] = (fam_key, family, block)
    return idx, None, dedup_count


def _yaml_dump_short(data: object, limit: int) -> str:
    """条目数据 YAML 渲染（冲突报告用，截断到 limit 字符）。"""
    import yaml  # noqa: PLC0415

    return yaml.safe_dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)[:limit]


def _merge_conflict_msg(
    rel_path: str, key: str, ours_block: _RegistryEntryBlock, theirs_block: _RegistryEntryBlock, cause: str
) -> str:
    """同键条目内容冲突报告（双侧渲染截断）。"""
    return (
        f"{rel_path}: 同键条目内容冲突: {key}（{cause}）\n"
        f"--- ours (dev) ---\n{_yaml_dump_short(ours_block.data, _MERGE_CONFLICT_DUMP_CHARS)}\n"
        f"--- theirs (快照) ---\n{_yaml_dump_short(theirs_block.data, _MERGE_CONFLICT_DUMP_CHARS)}"
    )


def _plan_kept_splices(
    ours_idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]],
    theirs_idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]],
    base_idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]],
    rel_path: str,
) -> tuple[list[tuple[int, int, str]], set[str], str | None]:
    """ours 侧既有条目遍历：kept 收集 + theirs 改 ours 没动的采纳 splice + 同键内容异冲突。"""
    splices: list[tuple[int, int, str]] = []
    kept: set[str] = set()
    for key, (_fk, family, block) in ours_idx.items():
        kept.add(key)
        if key not in theirs_idx:
            continue  # base 有+ours 有+theirs 无 → 保留 ours（快照侧删除不镇压现役）；ours 独有新增同理
        _, _, t_block = theirs_idx[key]
        base_block = base_idx[key][2] if key in base_idx else None
        if t_block.data == block.data:
            continue  # 双方一致，保留 ours 原文块（零字节漂移）
        if base_block is not None and base_block.data == t_block.data:
            continue  # theirs 没动（==base）、ours 改了 → 保留 ours
        if base_block is not None and base_block.data == block.data:
            # theirs 改了、ours 没动（==base）→ 采纳 theirs
            splices.append((block.start, block.end + 1, t_block.text))
            continue
        # 剩余=三方都在且 ours/theirs 相对 base 各自修改，或双侧新增内容异 → 同键内容异死信
        cause = "三方各自修改" if base_block is not None else "双侧各自新增且内容异"
        return [], set(), _merge_conflict_msg(rel_path, key, block, t_block, cause)
    return splices, kept, None


def _plan_insert_splices(
    theirs_idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]],
    ours_idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]],
    base_idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]],
    ours_families: dict[str | None, _RegistryFamily],
    rel_path: str,
    retired_check: object | None,
) -> tuple[list[tuple[int, int, str]], set[str], str | None]:
    """theirs 独有条目遍历：族尾追加 splice（base 有+ours 无=采纳恢复，尊重 ours 合法退役）。"""
    splices: list[tuple[int, int, str]] = []
    inserted: set[str] = set()
    family_append_pos: dict[str | None, int] = {}
    for key, (t_fam_key, _, t_block) in theirs_idx.items():
        if key in ours_idx:
            continue
        target = ours_families.get(t_fam_key)
        if target is None:
            return [], set(), f"{rel_path}: 条目 {key} 的目标族在 ours 缺失——结构漂移，死信回人工"
        # 夜班手术二a 拼接修（st-nightfix-20260923）：同族多条插入共享**同一**族尾
        # 坐标——splices 按 start 降序应用，同位插入逆序落刀=正序成品，无需伪递增。
        # 旧 ``cached+1`` 把第 2+ 条插到族尾之后的原文行上（末族场景即越过
        # di_seam_exemptions 居末键）→ 渲染自检"结果不可解析"死信
        # （q-20260923-st-wm1-mineC-20260923-0003 与 st-ibt-remedy-a 批A 双实证）。
        if t_fam_key not in family_append_pos:
            family_append_pos[t_fam_key] = target.blocks[-1].end + 1 if target.blocks else target.head_line + 1
        cached = family_append_pos[t_fam_key]
        text = t_block.text if t_block.text.endswith("\n") else t_block.text + "\n"
        if key in base_idx:
            # base 有+ours 无+theirs 有 → 采纳，除 ours 侧合法退役
            # （判据=条目引用路径盘上与 HEAD 双不存在；判定异常=不可证 → 采纳恢复）
            # ATK-1 加侧闸（快照自洽见证的条目级形态，st-ff-snapself-20260926，案卷
            # lane_stale_channel_repro ATK-1）：theirs 条目与其基底逐内容相同＝袋侧
            # 纯陈旧携带（本包对该条目零意图）——不得复活 dev 已落地的删除（旧口径
            # "宁可多救不可漏救"对陈旧袋把删除语义清零，加侧无任何闸）。theirs 确实
            # 改过该条目（内容≠base）则维持 W2 采纳恢复语义（合并语义不回归；确需
            # 原样恢复已删条目=同步工作区后重投，该条目相对新基底成为真实新增）。
            if base_idx[key][2].data == t_block.data:
                logger.warning(
                    "[landing] %s 条目 %s 袋内内容恰等其基底携带（这不是你的改动）——拒绝复活 dev 已落地的删除",
                    rel_path,
                    key,
                )
                continue
            if retired_check is not None:
                try:
                    if retired_check(t_block.data):
                        continue  # 合法退役，尊重 ours 的删除
                except Exception as exc:  # noqa: BLE001
                    logger.warning("[landing] retired_check 异常（按不可证退役处理，采纳恢复条目）: %s", exc)
            inserted.add(key)
            splices.append((cached, cached, text))
        else:
            # base 无+theirs 有（ours 无）→ 插入
            inserted.add(key)
            splices.append((cached, cached, text))
    return splices, inserted, None


def _render_selfcheck(
    merged: str,
    kept_keys: set[str],
    inserted_keys: set[str],
    rel_path: str,
    identity_fn: object | None = None,
) -> str | None:
    """渲染自检（fail-closed 兜底）：结果必须可解析且身份集 == 预期（保留∪插入）。"""
    import yaml  # noqa: PLC0415

    try:
        yaml.safe_load(merged)
    except Exception as exc:  # noqa: BLE001
        return f"{rel_path}: 合并渲染自检失败（结果不可解析）: {exc}"
    got, err = _split_registry_entries(merged, identity_fn)
    if err:
        return f"{rel_path}: 合并渲染自检失败（重切分异常）: {err}"
    # 预期集=去重后恒等集（QMine A1 件①配套）：重切分经同一 _index_family_blocks——
    # 侧内真重复（data 全等）在成品里合法共存（ours 原样保留），身份集按去重后口径
    # 比对；同键异容真冲突在重切分即报错（防拼接产物引入身份不唯一）。passthrough
    # 族（元数据标量/流式 dict 形态）先剔出，与主合并管线同序——身份判不了是这些族
    # 的合法常态，不是自检失败。
    for k in _scalar_family_keys(got):
        got.pop(k, None)
    got_idx, err2, _deduped = _index_family_blocks(got)
    if err2:
        return f"{rel_path}: 合并渲染自检失败（重切分索引异常）: {err2}"
    got_keys: set[str] = set(got_idx)
    if got_keys != (kept_keys | inserted_keys):
        return (
            f"{rel_path}: 合并渲染自检失败（身份集漂移）预期 {len(kept_keys | inserted_keys)} 条 "
            f"实际 {len(got_keys)} 条——死信回人工"
        )
    return None


def _split_all_sides(
    ours_text: str,
    theirs_text: str,
    base_text: str | None,
    rel_path: str,
    identity_fn: object | None = None,
) -> tuple[
    dict[str | None, _RegistryFamily] | None,
    dict[str | None, _RegistryFamily] | None,
    dict[str | None, _RegistryFamily] | None,
    str | None,
]:
    """三侧文本各自条目族切分；任一侧解析失败 → (None, None, None, 错误串)。"""
    ours_families, err = _split_registry_entries(ours_text, identity_fn)
    if err:
        return None, None, None, f"{rel_path}: ours 侧 {err}"
    theirs_families, err = _split_registry_entries(theirs_text, identity_fn)
    if err:
        return None, None, None, f"{rel_path}: theirs(快照) 侧 {err}"
    base_families: dict[str | None, _RegistryFamily] = {}
    if base_text is not None:
        base_families, err = _split_registry_entries(base_text, identity_fn)
        if err:
            return None, None, None, f"{rel_path}: base 侧 {err}"
    return ours_families, theirs_families, base_families, None


def _index_all_sides(
    ours_families: dict[str | None, _RegistryFamily],
    theirs_families: dict[str | None, _RegistryFamily],
    base_families: dict[str | None, _RegistryFamily],
    rel_path: str,
) -> tuple[
    dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]] | None,
    dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]] | None,
    dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]] | None,
    str | None,
    int,
]:
    """三侧条目索引构建；任一侧身份判不了/同键真冲突 → 错误串；带侧内去重计数。"""
    total_dedup = 0
    ours_idx, err, n = _index_family_blocks(ours_families)
    if err:
        return None, None, None, f"{rel_path}: ours {err}", 0
    total_dedup += n
    theirs_idx, err, n = _index_family_blocks(theirs_families)
    if err:
        return None, None, None, f"{rel_path}: theirs(快照) {err}", 0
    total_dedup += n
    base_idx, err, n = _index_family_blocks(base_families)
    if err:
        return None, None, None, f"{rel_path}: base {err}", 0
    total_dedup += n
    return ours_idx, theirs_idx, base_idx, None, total_dedup


def three_way_merge_registry_yaml(
    base_text: str | None,
    ours_text: str,
    theirs_text: str,
    *,
    rel_path: str,
    retired_check: object | None = None,
) -> tuple[str | None, str]:
    """注册表族文件条目级三向合并（W2 治本核心，纯函数零 IO）。

    Args:
        base_text: 快照基底版本（item.base_head 或 old_dev 父提交；None=该文件 base 侧不存在）。
        ours_text: 当前 dev 版本。
        theirs_text: 快照内容（入队时的整文件快照）。
        rel_path: 仓内相对路径（死信详情/自检报告用）。
        retired_check: callable(entry_dict) -> bool——ours 侧合法退役判定
            （条目引用路径盘上与 HEAD 双不存在）；None=一律不认退役（纯文本层测试用）。

    Returns:
        (merged_text, "") 合并成功；(None, conflict_reason) 冲突/结构漂移/解析失败
        ——调用方落地死信回人工，绝不静默整文件覆盖。
    """
    identity_fn = _family_identity_fn(rel_path, ours_text, theirs_text, base_text)
    ours_families, theirs_families, base_families, err = _split_all_sides(
        ours_text, theirs_text, base_text, rel_path, identity_fn
    )
    if err:
        return None, err

    passthrough, err = _split_passthrough_and_drift(ours_families, theirs_families, base_families, rel_path)
    if err:
        return None, err
    for fam_map in (ours_families, theirs_families, base_families):
        for k in passthrough:
            fam_map.pop(k, None)

    ours_idx, theirs_idx, base_idx, err, deduped = _index_all_sides(
        ours_families, theirs_families, base_families, rel_path
    )
    if err:
        return None, err
    if deduped:
        # 审计计数出口（工作簿 §⑤：去重静默化须留计数）——landing 日志可回放
        logger.info("[landing] %s 三向合并侧内去重 %d 条（data 全等真重复，保留首条）", rel_path, deduped)

    kept_splices, kept_keys, err = _plan_kept_splices(ours_idx, theirs_idx, base_idx, rel_path)
    if err:
        return None, err
    ins_splices, inserted_keys, err = _plan_insert_splices(
        theirs_idx, ours_idx, base_idx, ours_families, rel_path, retired_check
    )
    if err:
        return None, err

    # 应用 splice（start 降序；同位多条插入按规划序号**降序**落刀——后规划的先插、
    # 先规划的压在其上，成品保持 theirs 规划正序。stable reverse 平局保原序会反序，
    # 夜班手术二a 测试 test_multi_insert_order_preserved 钉住）
    splices = kept_splices + ins_splices
    lines = ours_text.splitlines(keepends=True)
    for start, end_excl, text, _seq in sorted(
        ((s, e, t, k) for k, (s, e, t) in enumerate(splices)),
        key=lambda x: (x[0], x[1], x[3]),
        reverse=True,
    ):
        lines[start:end_excl] = [text] if text else []
    merged = "".join(lines)

    err = _render_selfcheck(merged, kept_keys, inserted_keys, rel_path, identity_fn)
    if err:
        return None, err
    return merged, ""


_MISSING = object()  # 头部键判等的"键不存在"哨兵（None 是合法 YAML 值，不可复用）


def _noop_absorption_verdict(
    rel: str, base_text: str | None, ours_text: str, theirs_text: str
) -> tuple[str | None, str]:
    """落地前自证读回（防 done 零变化，2026-09-28）：合并零变化必须有合法解释。

    病根（q-0006 名册标量袋实证）：合并器对标量/头部行恒取 ours（防陈旧快照吃热册
    头部的正确设计），袋内增量凡走不进条目合并通道就**静默蒸发**，落地器却记 done
    ——假成功。本判别在 merged == ours 的必经返回点分流三态：

    - 合法 noop（返回 (None, 审计注)）：袋内预期增量全有解——条目已被 dev 吸收
      （他袋已落）、陈旧携带（theirs==base，非本袋意图）、ours 侧合法退役吸收、
      头部标量在派生配对覆盖内且 dev 已自洽（自愈已处理）；
    - 内容被吞（返回 (吞没报告, "")）：预期增量（base→theirs 真差异）既未被 dev
      携带又无合法解释——拒绝记 done，死信人工核查；
    - 判别不能（解析/切分/身份异常）→ 同样拒绝（fail-closed：证明不了的零变化
      不算自证通过）。

    纯函数零 IO；与主合并共用同一套切分/索引/身份函数（同输入必同判定）。
    """
    try:
        return _noop_absorption_verdict_inner(rel, base_text, ours_text, theirs_text)
    except Exception as exc:  # noqa: BLE001 — 判别器自身异常=证明不了，绝不放行也不裸抛
        return f"{rel}: 自证读回判别器异常（{type(exc).__name__}: {exc}）——零变化无法自证，拒绝记 done", ""


def _entry_level_absorption(ours_idx: dict, theirs_idx: dict, base_idx: dict) -> tuple[list[str], list[str]]:
    """条目级核对：theirs 相对 base 的真差异，逐键核对去向（吸收有解/被吞）。

    Returns:
        (absorbed 审计注列表, swallowed 吞没键列表)。
    """
    absorbed: list[str] = []
    swallowed: list[str] = []
    for key, (_t_fam, _fam, t_block) in theirs_idx.items():
        ours_block = ours_idx.get(key)
        base_block = base_idx.get(key)
        if ours_block is None:
            if base_block is None:
                # base 无+theirs 有（ours 无）：合并器必插（渲染自检也拦），零变化=被吞。
                # 今日到不了这里（防御面）——到得了即说明合并器换了实现，正是要抓的回归。
                swallowed.append(str(key))
            elif base_block[2].data == t_block.data:
                absorbed.append(f"{key}(陈旧携带，非本袋意图)")  # ATK-1 加侧闸语义
            else:
                absorbed.append(f"{key}(ours 侧合法退役吸收)")  # 退役吸收必须仍通行
            continue
        if base_block is None:
            absorbed.append(f"{key}(dev 已有，他袋已落)")  # 袋内新增但 dev HEAD 已存在
            continue
        if base_block[2].data == t_block.data:
            continue  # 袋未触碰该条目（ours 自行演化）——无意图即无吞没
        if ours_block[2].data == t_block.data:
            absorbed.append(f"{key}(改动已被 dev 吸收)")
            continue
        # theirs 真改、ours 也非 base（或 ours==base 却未采纳）——本应采纳或冲突死信，
        # 零变化=被吞（防御面：现行合并器两条路都到不了这里）
        swallowed.append(str(key))
    return absorbed, swallowed


def _header_key_verdict(
    k: object,
    ours_families: dict,
    theirs_doc: dict,
    ours_doc: dict,
    base_doc: dict | None,
    covered: dict[str, str],
) -> tuple[str | None, str | None]:
    """单个头部键的 absorb/swallow 判定（结构族键交条目级核对，此处恒不判）。

    Returns:
        (absorbed 注, swallowed 报告)；键无袋侧意图时 (None, None)。
    """
    ks = k if isinstance(k, str) else str(k)
    if k in ours_families:  # 结构族键已由条目级核对覆盖（ours_families 已剔直通族）
        return None, None
    t_val = theirs_doc.get(k, _MISSING)
    b_val = base_doc.get(k, _MISSING) if base_doc is not None else t_val  # 基底不可知⇒不推断头部意图
    if b_val == t_val:
        return None, None  # 袋未改此键——无意图即无吞没
    o_val = ours_doc.get(k, _MISSING)
    if o_val == t_val:
        return f"{ks}(头部已被 dev 吸收)", None
    section = covered.get(ks)
    ours_section = ours_doc.get(section, _MISSING) if section else _MISSING
    if section and isinstance(o_val, int) and isinstance(ours_section, (list, dict)) and o_val == len(ours_section):
        return f"{ks}(自愈覆盖内，dev 已自洽)", None  # 自愈按段长重算，袋侧计值被权威值取代
    return None, f"{ks}（base {_short(b_val)} → theirs {_short(t_val)}，dev {_short(o_val)}）"


def _header_level_absorption(
    rel: str,
    families: tuple[dict, dict, dict],
    texts: tuple[str | None, str, str],
    absorbed: list[str],
) -> tuple[list[str], str | None]:
    """头部级核对：非结构族键（标量/直通族/缺失键）base→theirs 真差异逐键核对。

    直通族先剔出结构空间（主合并同序）；ours 有结构族的键交条目级核对，此处跳过。

    Args:
        families: (ours, theirs, base) 三侧族切分（可变，直通族会被就地剔除）。
        texts: (base_text, ours_text, theirs_text)——base 可为 None（基底无此文件）。
        absorbed: 条目级审计注的累加器（头部吸收注原地追加）。

    Returns:
        (header_swallowed 报告列表, err)；err 非 None=判别不能（fail-closed）。
    """
    ours_families, theirs_families, base_families = families
    base_text, ours_text, theirs_text = texts
    passthrough, perr = _split_passthrough_and_drift(ours_families, theirs_families, base_families, rel)
    if perr:
        return [], perr
    for fam_map in families:  # 直通族剔出结构空间（主合并同序）
        for pt_key in passthrough:
            fam_map.pop(pt_key, None)
    covered = all_derived_total_pairs().get(rel.rsplit("/", 1)[-1]) or {}
    theirs_doc = _safe_load_doc(theirs_text) or {}
    ours_doc = _safe_load_doc(ours_text) or {}
    base_doc = (_safe_load_doc(base_text) or {}) if base_text is not None else None
    header_keys: set[object] = set(theirs_doc)
    if base_doc is not None:
        header_keys |= set(base_doc)
    header_swallowed: list[str] = []
    for k in header_keys:
        head_absorb, head_swallow = _header_key_verdict(k, ours_families, theirs_doc, ours_doc, base_doc, covered)
        if head_absorb:
            absorbed.append(head_absorb)
        if head_swallow:
            header_swallowed.append(head_swallow)
    return header_swallowed, None


def _noop_absorption_verdict_inner(
    rel: str, base_text: str | None, ours_text: str, theirs_text: str
) -> tuple[str | None, str]:
    """_noop_absorption_verdict 本体（异常交外壳统一 fail-closed）。"""
    identity_fn = _family_identity_fn(rel, ours_text, theirs_text, base_text)
    ours_families, theirs_families, base_families, err = _split_all_sides(
        ours_text, theirs_text, base_text, rel, identity_fn
    )
    if err:
        return f"{rel}: 自证读回无法判别（ours 侧 {err}）", ""
    passthrough, perr = _split_passthrough_and_drift(ours_families, theirs_families, base_families, rel)
    if perr:
        return f"{rel}: 自证读回无法判别（{perr}）", ""
    for fam_map in (ours_families, theirs_families, base_families):  # 直通族剔出结构空间（主合并同序）
        for k in passthrough:
            fam_map.pop(k, None)
    ours_idx, theirs_idx, base_idx, err, _dedup = _index_all_sides(ours_families, theirs_families, base_families, rel)
    if err:
        return f"{rel}: 自证读回无法判别（{err}）", ""
    absorbed, swallowed = _entry_level_absorption(ours_idx, theirs_idx, base_idx)
    header_swallowed, herr = _header_level_absorption(
        rel,
        (ours_families, theirs_families, base_families),
        (base_text, ours_text, theirs_text),
        absorbed,
    )
    if herr:
        return f"{rel}: 自证读回无法判别（{herr}）", ""

    if swallowed or header_swallowed:
        detail = "；".join([f"条目 {s}" for s in swallowed] + header_swallowed)
        report = (
            f"{rel}: 落地前自证读回失败——合并结果与 dev 零变化，但袋内预期增量未被携带（内容被合并器吞没）: {detail}"
        )
        return report, ""
    note = "；".join(absorbed) if absorbed else "袋与 dev 语义等价（零增量）"
    return None, note


def _short(val: object) -> str:
    """判别报告里的值摘要（防超长 dump 撑爆死信 reason；_MISSING 显式记 缺失）。"""
    if val is _MISSING:
        return "缺失"
    text = repr(val)
    return text if len(text) <= 60 else text[:57] + "..."


class CasConflict(RuntimeError):
    """dev ref CAS 推进失败（old 期望值失配——队列外写入者插队）。"""


class SnapshotVerifyError(cq.LandingEnvironmentError):
    """快照写后读回自验失败（M5.1，st-qcure-20260925，治 29 笔 SNAPSHOT-NOT-APPLIED）。

    write_bytes 落盘后立即读回 sha256 比对不符＝落地器物化被静默丢失（rsync
    --checksum 语义）。继承 LandingEnvironmentError：drain/pool 按环境失败退
    pending 重放自愈（首两跳多为句柄占用类瞬态）；``dead_result`` 非 None ＝
    snapshot_retry 计数耗尽，调用方转死信带处方，不再无限重放。
    ``retried_key`` 类属性供 pool 环境分支识别「已过计数闸」，免二次累加。
    """

    retried_key = "snapshot_retry"

    def __init__(self, message: str, *, dead_result: cq.LandingResult | None = None) -> None:
        super().__init__(message)
        self.dead_result = dead_result


class MergeSwallowVerifyError(SnapshotVerifyError):
    """落地前自证读回失败（防 done 零变化，2026-09-28，q-0006 名册标量袋假成功治本）。

    合并结果与 dev 零变化、但袋内预期增量（条目行/头部键）既未被 dev 携带又无合法
    解释（他袋已落/陈旧携带/合法退役/自愈覆盖）＝内容被合并器吞没——拒绝记 done。
    判 SnapshotVerifyError 同族（继承）；吞没是**确定性**故障，重放无益，故构造时
    恒携 ``dead_result``（调用方见之即死信带处方，不烧 snapshot_retry 计数）。
    """

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            dead_result=cq.LandingResult(
                ok=False,
                reason=(
                    f"{message}。处方: 内容被合并器吞没，人工核查——①核对增量是否已由他袋落地"
                    f"（dev 已含则同步工作区后重投即吸收）；②确属合并器吞没勿重投原袋，"
                    f"报值班排查合并器并改走 git_commit.py 直提；③头部标量被吞=该配对未入"
                    f"自愈覆盖（可补 _MANUAL_DERIVED_TOTAL_PAIRS 点名或核查自动发现器）"
                ),
            ),
        )


# M5.1/M5.2 重试升级阈值：同一 item 同类环境失败达 3 次=确定性故障，升级死信带处方，
# 不再退 pending（防「HEAD 册真坏→每轮首项 abort→全队无限 pending」活锁，gate_chain
# 作业簿 §3.1）。阈值刻意用普通常量：落地器内部防线参数，非可调业务阈值。
_RETRY_META_MAX = 3


def _bump_item_retry(item: dict, queue_root: Path | str, key: str) -> int:
    """item meta 重试计数自增并持久化（M5.1 snapshot_retry / M5.2 env_retry 单一真源）。

    计数必须跨 drain 轮存活——drain 的 env 分支只 rename 回 pending 不重写 JSON，
    故此处就地改写 processing/ 下的项文件（单写者 lease 内无并发写者，_atomic_write
    原子替换）。项文件定位失败（畸形 qid / 测试直调无队列盘面）fail-open：仅内存
    计数，至少同进程内连续轮次仍可累计升级。
    """
    meta = item.setdefault("meta", {})
    try:
        n = int(meta.get(key) or 0) + 1
    except (TypeError, ValueError):
        n = 1
    meta[key] = n
    qid = str(item.get("qid") or "")
    if qid:
        try:
            p = Path(queue_root) / "processing" / f"{qid}.json"
            if p.exists():
                cq._atomic_write(p, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
        except (OSError, TypeError, ValueError) as exc:
            logger.warning("[landing] %s 计数持久化失败（fail-open，仅内存计数）: %s", key, exc)
    return n


def _retry_dead_result(key: str, prescription: str, detail: str) -> cq.LandingResult:
    """重试耗尽死信回执：处方必须可行动（人工/属主一眼知道下一步）。"""
    return cq.LandingResult(
        ok=False,
        reason=f"{detail}（{key}={_RETRY_META_MAX} 次耗尽，升级死信）处方: {prescription}",
    )


def _is_gate_auto_registration_error(exc: BaseException) -> bool:
    """GateAutoRegistrationError 判定（M5.2 分流前置；惰性 import——导入设施本身
    不可用时按类型名兜底匹配，防误分流回泛化 env 分支）。"""
    try:
        from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import (  # noqa: PLC0415
            GateAutoRegistrationError,
        )

        return isinstance(exc, GateAutoRegistrationError)
    except Exception:  # noqa: BLE001 — 设施不可用按名兜底（fail-open 到同名判定）
        return type(exc).__name__ == "GateAutoRegistrationError"


def queue_marker(session_id: str, qid: str) -> str:
    """生成队列 commit 标记 [GW:{sid}:{qid}]（唯一真源——落盘与幂等 grep 共用）。"""
    return f"[GW:{session_id}:{qid}]"


def _trusted_git_env() -> dict:
    """Serializer 内部 git 调用 env：plumbing 白名单 + git_guard fast-path（可信调用方）。"""
    env = dict(os.environ)
    env[_SERIALIZER_MODE_ENV] = "1"  # 66 号 §4 裁定 7：Serializer 专用 worktree 内 plumbing 不拦
    env[_GIT_GUARD_FAST_PATH_ENV] = "1"  # worktree_pool 同款（GIT-BUDGET-INV-003）
    return env


def _run_git(repo_or_wt: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """落地 git 执行（统一 utf-8/隐藏窗口/超时；stderr 进异常消息，报错非静默）。

    治本（2026-08-23 假死修复）：stdout/stderr 不走 PIPE 改落临时文件——Windows 下
    git 衍生的孙进程（worktree/hook 链上的 sh.exe 等）继承管道写句柄且可能活得
    比 git 久，PIPE 模式 communicate() 等 EOF 永不返回（C 级阻塞，pytest-timeout
    thread 法杀不动；subprocess.run 超时 kill 直子后的二次 communicate 同样堵死
    在 EOF 等待上）。临时文件读取不依赖句柄继承链，wait() 只等直子退出，kill 后
    无需二次 communicate，根除此类管道 join 假死。
    """
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200
        )

    out_fd, out_path = tempfile.mkstemp(prefix="zcq_git_out_", suffix=".log")
    err_fd, err_path = tempfile.mkstemp(prefix="zcq_git_err_", suffix=".log")
    proc: subprocess.Popen | None = None
    try:
        with os.fdopen(out_fd, "wb") as out_f, os.fdopen(err_fd, "wb") as err_f:
            proc = subprocess.Popen(
                ["git", *args],
                cwd=str(repo_or_wt),
                stdin=subprocess.DEVNULL,
                stdout=out_f,
                stderr=err_f,
                creationflags=creationflags,
                env=_trusted_git_env(),
            )
            try:
                proc.wait(timeout=_GIT_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                # Popen 级墙钟强杀——输出在文件不在管道，kill 直子即返，
                # 绝无 PIPE 模式的 kill 后 EOF 等待
                proc.kill()
                proc.wait(timeout=10)
                raise RuntimeError(f"git {' '.join(args)} -> timeout after {_GIT_TIMEOUT_SECONDS}s (killed)") from None
        stdout = Path(out_path).read_bytes().decode("utf-8", errors="replace")
        stderr = Path(err_path).read_bytes().decode("utf-8", errors="replace")
    finally:
        for p in (out_path, err_path):
            try:
                os.unlink(p)
            except OSError:  # 孙进程仍持有句柄时 Windows 禁删——留 %TEMP% 由系统清理
                pass
    r = subprocess.CompletedProcess(["git", *args], proc.returncode, stdout, stderr)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} -> rc={r.returncode}: {(r.stderr or r.stdout).strip()[:400]}")
    return r


# ── A2 装表：单件落地分段计时（st-commitspeed-tbl-20260924，提交等待调查 A2）──────────
# 背景：队列单件实测 p50≈597s，而已装表的门禁链只占 110-133s——其余数百秒在既有账面上
# 无任何归属，故无人能判定该优化哪一段（＝调查 R6 无法收口的直接原因）。
# 本段只测不判：不改任何门禁判据、不改任何控制流；计时器按方法 def 位挂载，
# 因此 CAS 重试段与双分支等全部调用路径自动覆盖，无需拆函数（拆名即丢
# COMPLEXITY-GUARD 存量豁免，q-20260923-st-k4-20260923-0002 死信实证）。
_PHASE_ACC: Final = "_phase_ms"
_PHASE_FILE: Final = "landing_phase_stats.jsonl"


def _worker_tag(landing: object) -> str:
    """从序列化分支名反推工号（WorktreeLanding 无 worker_id 属性位）。

    k=4 池此前所有账本都不按工归因——这正是"三路工熄火 9 小时"看不见的原因。
    """
    branch = str(getattr(landing, "serializer_branch", "") or "")
    return "w" + branch.rsplit("-w", 1)[-1] if "-w" in branch else "single"


def _record_phase(landing: object, name: str, ms: float) -> None:
    """同段多次进入（CAS 重试/双分支）累加而非覆盖。"""
    bucket = getattr(landing, _PHASE_ACC, None)
    if bucket is None:
        bucket = {}
        setattr(landing, _PHASE_ACC, bucket)
    bucket[name] = round(float(bucket.get(name, 0.0)) + ms, 1)


def _timed_phase(name: str) -> Callable[..., Callable[..., object]]:
    """按方法定义位挂分段计时上下文（装饰器形态＝零控制流改动）。"""

    def deco(fn: Callable[..., object]) -> Callable[..., object]:
        @functools.wraps(fn)
        def inner(self: object, *args: object, **kwargs: object) -> object:
            t0 = time.monotonic()
            try:
                return fn(self, *args, **kwargs)
            finally:
                _record_phase(self, name, (time.monotonic() - t0) * 1000)

        return inner

    return deco


def _emit_landing_phase_stat(landing: object, item: dict, total_ms: float) -> None:
    """一行一单件：分段耗时 + 未归属残差（residual_ms 即下一轮装表的靶子）。

    账本随本工 worktree 落盘（与 gate_execution_stats 同根语义＝池各工天然分账）。
    可观测性永不阻断主链路：任何写入异常静默吞掉。
    """
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        bucket = dict(getattr(landing, _PHASE_ACC, None) or {})
        setattr(landing, _PHASE_ACC, {})
        anchor = getattr(landing, "worktree_path", None) or getattr(landing, "repo_root", None)
        audit_dir = Path(str(anchor)) / ".runtime" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        accounted = round(sum(bucket.values()), 1)
        record = {
            "timestamp": now_utc().isoformat(),
            "event": "landing_phase_run",
            "qid": item.get("qid", "?"),
            "session_id": item.get("session_id", ""),
            "worker": _worker_tag(landing),
            "files_count": len(item.get("files") or []),
            "total_ms": round(total_ms, 1),
            "phases": bucket,
            "accounted_ms": accounted,
            "residual_ms": round(total_ms - accounted, 1),
        }
        with open(audit_dir / _PHASE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (OSError, TypeError, ValueError):
        pass


_POOL_WAVE_LOG: Final = "pool_wave.log"


def _pool_wave_log(root: Path, line: str) -> None:
    """A3 装表：工线程出口原因落**文件**（队列根下 pool_wave.log）。

    必落文件而非 logger 的原因（实测取证）：belt 守护只 getLogger、不装任何 handler，
    其 logger.error 全走 lastResort→stderr→被丢弃——所以"三路工为何不再认领"在盘上
    至今零证据（调查 R6 判 UNPROVABLE 的直接原因）。只记不判：不改任何认领/中止语义。
    """
    try:
        with open(Path(root) / _POOL_WAVE_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%dT%H:%M:%S%z ") + line + "\n")
    except OSError:
        pass


class WorktreeLanding:
    """Serializer 落盘执行体：队列项 → 专用 worktree → GitCommitGateway 全门禁 → CAS 推进 dev。

    用法（drain_queue landing 注入点，A 段协议）::

        landing = WorktreeLanding(repo_root=Path("."), queue_root=cq.resolve_queue_root())
        cq.drain_queue(queue_root, landing=landing)

    线程/进程安全：单写者不变量由 Serializer lease 保证（drain_queue 内只有 lease
    持有者会调到本类）；本类自身不加锁。同一实例跨项复用（gateway/worktree 惰性一次初始化）。

    参数
    ----
    repo_root : 主仓根（update-ref/rev-parse 等 ref 操作的锚点；永不写其工作区文件）。
    queue_root : 队列根（默认 commit_queue.resolve_queue_root()——仓级共享协调设施）。
    worktree_path : 专用 worktree 路径（默认 <queue_root>/worktree）。
    target_branch : 落盘目标分支（默认 dev，66 号 §9.5 v0.1 单目标）。
    registry : 主仓根 SessionRegistry（SESSION-REQUIRED/CLAIM-REQUIRED 判定真源；
        默认按 repo_root 构造——生产者会话注册处）。
    gateway : 测试注入位（默认惰性构造 GitCommitGateway(project_root=worktree)）。
    max_cas_retries : dev CAS 冲突重试上限（默认 _MAX_CAS_RETRIES=6；耗尽=死信回退人工）。
    lock_wait_seconds : 透传 gateway.commit(lock_wait_timeout=...) 的全局锁等待秒数
        （默认 _LANDING_LOCK_WAIT_SECONDS=300；测试可注入小值免等）。
    pool_mode : k=4 通道池工模式（st-k4-20260923 施工令③）。True 时 CAS 冲突走
        「落地段重放不重跑门禁」（_replay_commit_without_gates）；False=现行
        整段重试（重同步+重跑门禁）零行为变化。
    """

    def __init__(
        self,
        repo_root: str | os.PathLike,
        *,
        queue_root: str | os.PathLike | None = None,
        worktree_path: str | os.PathLike | None = None,
        target_branch: str = cq._TARGET_BRANCH,
        serializer_branch: str = _SERIALIZER_BRANCH,
        registry=None,
        gateway=None,
        max_cas_retries: int = _MAX_CAS_RETRIES,
        lock_wait_seconds: float = _LANDING_LOCK_WAIT_SECONDS,
        pool_mode: bool = False,
    ) -> None:
        """__init__ implementation."""
        self.repo_root = Path(repo_root).resolve()
        self.queue_root = cq.resolve_queue_root(queue_root)
        self.worktree_path = (
            Path(worktree_path).resolve() if worktree_path else (self.queue_root / _WORKTREE_DIR_NAME).resolve()
        )
        self.target_branch = target_branch
        self.serializer_branch = serializer_branch
        self._registry = registry
        self._gateway = gateway
        self._max_cas_retries = max_cas_retries
        self._lock_wait_seconds = lock_wait_seconds
        self._pool_mode = pool_mode

    # ------------------------------------------------------------------
    # git 便捷封装
    # ------------------------------------------------------------------
    def _git_repo(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """_git_repo implementation."""
        return _run_git(self.repo_root, list(args), check=check)

    def _git_wt(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """_git_wt implementation.

        fail-closed（2026-08-29 主仓打穿事故治本）：专用 worktree 目录在但 .git 链接
        丢失时，git 以 cwd 向上查找会命中主仓 .git——reset --hard/clean 直接打穿主工作区
        （当日 reflog 实证 6 次成对 reset）。执行前硬校验：.git 链接存在 且
        rev-parse --show-toplevel 解析回自身，否则 RuntimeError（宁停勿伤）。
        """
        git_link = self.worktree_path / ".git"
        if not git_link.exists():
            raise RuntimeError(
                f"[landing] 专用 worktree .git 链接丢失，拒绝执行（防 walk-up 打穿主仓）: {self.worktree_path}"
            )
        r = _run_git(self.worktree_path, ["rev-parse", "--show-toplevel"], check=True)
        top = os.path.normcase(str(Path(r.stdout.strip()).resolve()))
        if top != os.path.normcase(str(self.worktree_path)):
            raise RuntimeError(
                f"[landing] 专用 worktree toplevel 漂移（{top} != {self.worktree_path}），拒绝执行（防打穿主仓）"
            )
        return _run_git(self.worktree_path, list(args), check=check)

    def _dev_head(self) -> str:
        """_dev_head implementation."""
        return self._git_repo("rev-parse", f"refs/heads/{self.target_branch}").stdout.strip()

    def head_reader(self):
        """stale 基底重校验的 HEAD blob 读口（公开口，供各排空通道注入；薄封装 _pool_head_reader，
        不另写第二份读口实现）。"""
        return _pool_head_reader(self)

    # ------------------------------------------------------------------
    # 专用 worktree 生命周期（66 号 §6.3 MVP 形态）
    # ------------------------------------------------------------------
    def _provision_env(self, wt: Path) -> None:
        """专用 worktree 环境备置（委托 session_worktree 真源，不复制实现）。

        病根（2026-09-16 fail-open 实证）：队列落盘在 worktree 内跑 pre-commit 门禁 +
        post-commit reconciler，进程 REPO_ROOT 解析到 `.runtime/commit_queue/worktree`，
        而该处从未备置 config/.env.postgres / config/.env.clickhouse →
        DEPGRAPH-PRE-REGISTRATION 抛 FileNotFoundError、CH 依赖 reconciler 记
        "CH 配置文件不存在 …（CH 连接将失败）"（reconcile_execution_log 自 2026-09-12
        起多条）。队列是提交正门（宪法 §2），正门上的 enforcement 必须与主区等价。
        备置失败永不阻断落盘（与 session_worktree create 同口径）：全量降级 warning。
        """
        try:
            from scripts.session_worktree import _provision_worktree_env  # noqa: PLC0415

            warns = [n for n in _provision_worktree_env(wt, source_root=self.repo_root) if n.startswith("WARN")]
            if warns:
                logger.warning("[landing] 专用 worktree 环境备置降级: %s", "; ".join(warns))
        except Exception as exc:  # noqa: BLE001
            logger.warning("[landing] 专用 worktree 环境备置异常（不阻断落盘）: %s", exc)

    @_timed_phase("worktree")
    def ensure_worktree(self) -> Path:
        """确保专用 worktree 就位（幂等；仅 Serializer 调用，单写者无竞态）。

        状态机：已注册且目录在 → 复用；注册残留但目录丢失 → prune 后重建；
        目录在但未注册（上次半成品）→ 物理删除该专用目录后重建；
        分支已存在（历史遗留）→ 不 -b 直接检出复用。

        两条出口（复用/新建）都过 _provision_env：新建路径缺配置是必然，复用路径
        补置是为了配置在主区被轮换（换 PG 密码/CH 迁移）后 worktree 跟上。
        """
        wt = self.worktree_path
        r = self._git_repo("worktree", "list", "--porcelain")
        registered = False
        target_norm = os.path.normcase(str(wt))
        for line in r.stdout.splitlines():
            if line.startswith("worktree ") and os.path.normcase(line.split(" ", 1)[1].strip()) == target_norm:
                registered = True
                break
        # .git 链接存在性=复用前提（2026-08-29 事故：目录在而链接丢失 → git walk-up 打穿主仓）
        git_link_ok = wt.is_dir() and (wt / ".git").exists()
        if registered and git_link_ok:
            self._provision_env(wt)
            return wt  # 就位，复用
        if registered and not git_link_ok:
            logger.warning("[landing] 专用 worktree 注册残留但目录/.git 链接丢失，prune+清残骸后重建: %s", wt)
            self._git_repo("worktree", "prune")
            if wt.exists():
                # 残留检出树（无 .git 链接的 stale checkout）——物理清除后重建
                from zephyr.shared.io.file_utils import safe_rmtree  # noqa: PLC0415

                safe_rmtree(wt, allowed_prefix=self.queue_root, ignore_errors=True)
        elif wt.exists() and not registered:
            # 半成品残骸（上次 worktree add 中断）——仅限本专用路径，物理清掉重建
            # （CAND-GOVSEC-001①：safe_rmtree 硬断言——resolve 后须严格落在
            # queue_root 内 + 拒绝 reparse point，拦截 rmtree 越界/junction 穿透）
            logger.warning("[landing] 专用 worktree 半成品残骸，清除后重建: %s", wt)
            from zephyr.shared.io.file_utils import safe_rmtree  # noqa: PLC0415

            safe_rmtree(wt, allowed_prefix=self.queue_root, ignore_errors=True)
            self._git_repo("worktree", "prune")
        wt.parent.mkdir(parents=True, exist_ok=True)
        branch_exists = (
            self._git_repo(
                "rev-parse", "--verify", "--quiet", f"refs/heads/{self.serializer_branch}", check=False
            ).returncode
            == 0
        )
        if branch_exists:
            self._git_repo("worktree", "add", str(wt), self.serializer_branch)
        else:
            self._git_repo("worktree", "add", str(wt), "-b", self.serializer_branch, f"refs/heads/{self.target_branch}")
        self._provision_env(wt)
        logger.info("[landing] 专用 worktree 就位: %s (branch=%s)", wt, self.serializer_branch)
        return wt

    def _verify_wt_integrity_post(self, phase: str) -> None:
        """EV-02 执行后复核（15 号文处方残余落地，2026-09-30 F 组夜班）。

        _git_wt 执行前硬校验关"入口门"；本复核关 TOCTOU 窗：git 调用在飞时 .git
        链接被外力摘除/竞态破坏（2026-08-29 打穿事故形态的剩余通道）。危险命令
        （reset --hard / clean -fd）执行后立即复测链接存在+toplevel 仍解析回自身，
        不一致即 RuntimeError 中止本轮（走既有死信/环境分类链路）——宁停勿伤。
        主仓 untracked 计数快照比对本实现不含：并发会话常态改写主区 untracked 数
        （假阳性不可用），该观测面归 EV-01 黑匣子 5 分钟快照专职（内收不重复建）。
        """
        git_link = self.worktree_path / ".git"
        if not git_link.exists():
            logger.critical(
                "[landing][EV-02] %s 执行后复核：worktree .git 链接丢失（TOCTOU 窗命中，中止防打穿主仓）: %s",
                phase,
                self.worktree_path,
            )
            raise RuntimeError(f"[landing][EV-02] {phase} 执行后复核：.git 链接丢失，中止（防打穿主仓）")
        r = _run_git(self.worktree_path, ["rev-parse", "--show-toplevel"], check=False)
        top = os.path.normcase(str(Path(r.stdout.strip()).resolve())) if r.returncode == 0 and r.stdout.strip() else ""
        if r.returncode != 0 or top != os.path.normcase(str(self.worktree_path)):
            logger.critical(
                "[landing][EV-02] %s 执行后复核：toplevel 漂移/不可解析（rc=%s, top=%r，中止防打穿主仓）",
                phase,
                r.returncode,
                top,
            )
            raise RuntimeError(f"[landing][EV-02] {phase} 执行后复核：toplevel 漂移（rc={r.returncode}），中止")

    @_timed_phase("sync")
    def _sync_worktree(self) -> None:
        """每项处理前同步：serializer 分支 reset --hard 到 dev HEAD + clean -fd。

        66 号 §11 #6 不变量（每项处理前 worktree HEAD == dev HEAD 且 clean）的机械实现；
        同时自愈 POST-COMMIT-GUARD reset / 上次崩溃孤儿 commit 等分支漂移。

        clean 容错（2026-09-14 死信饥饿治本，12+ 条死信实证）：worktree 里的
        data/databases/governance.db 是落盘门禁链的写副本（project_root=worktree），
        其 SQLite journal 是毫秒级瞬态（曾因 *.db-journal 未入 .gitignore SQLite 段
        成为 clean 目标——同批已补）：clean 遍历到它时可能刚消失（rc=128 Cannot
        lstat）或正被锁（rc=1 failed to remove）。处置：失败重试一次（让瞬态过去），
        仍失败降级 warning 继续——落盘 commit 是 pathspec 限定（仅本项文件），worktree
        残留 untracked 不可能混入提交，§11 #6 的防陈旧内容泄漏目的由 reset --hard +
        pathspec 双保险保持。reset --hard 失败仍然致命（真异常，照旧走死信/环境分类）。

        EV-02（15 号文）：两条危险命令执行后各做一次 worktree 完整性复核
        （_verify_wt_integrity_post），关 _git_wt 前置校验与命令在飞之间的 TOCTOU 窗。
        """
        self._git_wt("reset", "--hard", f"refs/heads/{self.target_branch}")
        self._verify_wt_integrity_post("reset --hard")
        try:
            self._git_wt("clean", "-fd")
        except RuntimeError as exc:
            logger.warning("[landing] clean -fd 首次失败（worktree journal 瞬态竞态）: %s —— 0.5s 后重试", exc)
            time.sleep(0.5)
            try:
                self._git_wt("clean", "-fd")
            except RuntimeError as exc2:
                logger.warning(
                    "[landing] clean -fd 重试仍失败，降级继续（pathspec 限定提交不受 worktree 残留影响）: %s",
                    exc2,
                )
        self._verify_wt_integrity_post("clean -fd")

    # ------------------------------------------------------------------
    # 幂等判定（66 号 §8：is-ancestor / done 记录 + 标记 grep 三重）
    # ------------------------------------------------------------------
    def _already_landed(self, item: dict) -> str | None:
        """返回已落盘 commit sha（未落盘返回 None）——重放不双落的核心。"""
        landed = item.get("landed_id") or ""
        # noop 哨兵剥前缀：快照与该 HEAD 一致的幂等空转项按已落盘跳过（防重放循环），
        # is-ancestor 用 @ 后真实 sha 判定。
        if landed.startswith(_NOOP_LANDED_PREFIX):
            landed = landed[len(_NOOP_LANDED_PREFIX) :]
        if landed:
            r = self._git_repo("merge-base", "--is-ancestor", landed, f"refs/heads/{self.target_branch}", check=False)
            if r.returncode == 0:
                return landed  # done/ 记录 + is-ancestor 双证（66 号 §8 原文判定）
        marker = queue_marker(item.get("session_id", ""), item.get("qid", ""))
        r = self._git_repo(
            "log", "-1", "--format=%H", "-F", f"--grep={marker}", f"refs/heads/{self.target_branch}", check=False
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()[0]  # 标记在史：崩溃发生在 update-ref 之后的重放
        return None

    # ------------------------------------------------------------------
    # 冲突判定（66 号 §6.4：逐文件快进；语义冲突一律死信回退给人，§9.1）
    # ------------------------------------------------------------------
    def _item_paths(self, item: dict) -> set[str]:
        """_item_paths implementation."""
        return {f.get("path", "") for f in (item.get("files") or []) if f.get("path")}

    def _changed_paths_between(self, from_sha: str, to_sha: str) -> set[str]:
        """_changed_paths_between implementation."""
        r = self._git_repo("diff", "--name-only", from_sha, to_sha)
        return {line.strip() for line in r.stdout.splitlines() if line.strip()}

    @_timed_phase("conflict")
    def _conflict_reason(self, item: dict, current_dev: str) -> str | None:
        """base_head 基底冲突判定（66 号 §6.4 逐文件快进）；无基底见下方两分支。

        W2（2026-09-22 注册表事故治本）：注册表族文件（is_registry_mergeable）不做
        path 级死信——同路径漂移交由落地侧条目级三向合并消化（同键内容异才死信）；
        此处若照旧死信，合并器永远无执行机会。非注册表路径维持逐文件快进判定零变更。

        F-AUDITFIX-STALE-01（2026-09-24 晚，q-…-st-commitspeed-tbl-…-0005 实证）：
        基底＝快照真源（入队工作区自己的 HEAD），不是「当时看到的 dev 尖」。取 dev 尖
        时陈旧工作区记到的基底**比自己的字节还新** ⇒ diff(base, dev) 恒空 ⇒ 快进判定
        结构性失明（那件就是把在册的 4442b1b4f6 修复整文件覆掉的袋：它带 base_head，
        值是入队时的 dev 尖 e500df6dfe，而快照来自早于该修复的工作区）。
        dev 侧推进一律以 merge-base 为界度量：会话分支上有自有未并入提交时，
        直接 diff(base, dev) 会把"dev 从没改过、只是我没跟上"判成冲突（假红）。
        """
        base = item.get("base_head")
        paths = self._item_paths(item)
        mergeable = {p for p in paths if is_registry_mergeable(p)}
        if not base:
            # 存量项兜底（F-AUDIT-QUEUE-04 残面）：装表之前入袋的项仍无 base_head，
            # 光修正门救不了在飞的存量袋 ⇒ 用时间基底替代（见 _legacy_base_drift_reason）。
            # 刻意不按"缺基底即拒"收紧：实证今晚吃人的袋**有**基底、只是口径错（已由
            # resolve_base_head 取真源治掉），而按缺失收紧会打死按契约直投的存量通道。
            return self._legacy_base_drift_reason(item, current_dev)
        if base == current_dev:
            return None
        if self._git_repo("cat-file", "-t", base, check=False).stdout.strip() != "commit":
            # 红队 P2：`-e` 认 blob/tree/tag，非 commit 值会让 merge-base 失败后再抛
            # 异常——把"受控死信"变成崩栈。类型判一次，异常形态一律回死信通道。
            return f"冲突判定失败：base_head 非可判 commit（{str(base)[:12]}）——死信回退人工（66 号 §6.4）"
        anchor = self._merge_base(base, current_dev) or base
        overlap = self._changed_paths_between(anchor, current_dev) & (paths - mergeable)
        if not overlap:
            return None
        real = sorted(overlap - self._noop_overwrite_paths(item, overlap, current_dev))
        if real and self._drift_all_same_session(item, anchor, current_dev, real):
            logger.info(
                "[landing] qid=%s 同路径漂移 %s 全部由本会话此前落地构成 ⇒ 同包迭代非互踩，放行",
                item.get("qid"),
                real,
            )
            return None
        if real:
            return (
                f"冲突：快照基底 {base[:12]}（与 dev 的共同祖先 {anchor[:12]}）之后 dev 已推进"
                f"且触及同路径 {real}——逐文件快进判定失败，死信回退属主会话"
                f"（66 号 §6.4/§9.1；解法＝同步工作区后重新入队）"
            )
        return None

    def _noop_overwrite_paths(self, item: dict, paths: set[str], current_dev: str) -> set[str]:
        """快照字节与 dev 现字节同 git blob id 的路径＝覆盖是无操作，可安全快进。

        同会话连投多袋是常态（前袋已把内容送上 dev、后袋基底早于前袋）：路径重叠而
        字节一致。不短接则每次自投都吃死信（系统性假红）；短接只放"字节完全一致"这一
        种可证的无害形态。口径＝git blob sha 三套哈希不可互换（此处只认 git 那一套）。
        """
        dev_blobs = resolve_base_blobs(self.repo_root, current_dev, sorted(paths))
        git_blob_of: dict[str, str | None] = {}
        for entry in item.get("files") or []:
            rel = entry.get("path") or ""
            if rel not in paths or str(entry.get("action") or "modify") != "modify":
                continue
            ref = entry.get("blob_ref") or ""
            if not ref:
                continue
            try:
                data = (Path(self.queue_root) / ref).read_bytes()
            except OSError:
                continue  # 读不到袋内字节 ⇒ 不短接（保守判冲突）
            git_blob_of[rel] = _git_blob_sha(data)
        return {rel for rel, sha in git_blob_of.items() if sha is not None and dev_blobs.get(rel) == sha}

    def _witness_stale_carry(self, item: dict, queue_root: Path | str, current_dev: str) -> cq.LandingResult | None:
        """快照自洽见证消费端（ATK-3 判据层补面，st-ff-snapself-20260926）。

        活性护栏实测（tests/governance/test_commit_queue_snapshot_selfconsistency.py
        L 组）：等值即拒（不看 dev 现态、整袋按携带档死信）会误杀正常并行——同会话
        同步后连投与多文件正常改动都会被自家前袋/单枚携带拖死。故判据收紧到
        stale-path 级：部分命中=剥除危险携带路径后其余照常落地（meta 留痕+日志
        点名）；全部命中=袋内已无任何属于本包的改动，拒落整袋死信回属主并点名
        "这不是你的改动"。注册表族与 delete 项不经此通道（条目级合并语义零变更，
        其携带不复活闸在 _plan_insert_splices 以同一见证判据落地）。
        """
        dangerous, safe = assert_snapshot_selfconsistent(
            item, queue_root=queue_root, repo_root=self.repo_root, current_dev=current_dev
        )
        if safe:
            logger.info(
                "[landing] qid=%s 快照自洽见证：%s 为安全携带（袋==基底==dev，写=noop），不拦",
                item.get("qid"),
                safe,
            )
        if not dangerous:
            return None
        hit = set(dangerous)
        keep = [f for f in (item.get("files") or []) if f.get("path") not in hit]
        meta = item.get("meta")
        if not isinstance(meta, dict):
            meta = item["meta"] = {}
        meta["witness_stale_carry"] = sorted(hit)
        if keep:
            item["files"] = keep
            logger.warning(
                "[landing] qid=%s 快照自洽见证剥除陈旧携带路径 %s（袋字节恰等其自身基底——"
                "这不是你的改动，且 dev 已推进）；其余文件照常落地",
                item.get("qid"),
                sorted(hit),
            )
            return None
        return cq.LandingResult(
            ok=False,
            reason=(
                f"快照自洽见证（stale-carry）：袋内路径 {sorted(hit)} 字节恰等其自身基底"
                f"（本包没改它=纯陈旧携带）且 dev 已在这些路径上推进——落地必回退在册内容，"
                f"这不是你的改动，拒落回属主（66 号 §6.4；解法=同步工作区后只重新入队"
                f"真实改动的文件）"
            ),
        )

    def _heal_derived_totals(self, rel: str, merged: str) -> str:
        """条目合并后重算"声明计数"标量——派生值不得靠"某人恰好直提"才对。

        病形（④ 号任务实证，2026-09-24）：本合并器对标量/头部行恒取 ours（dev 侧），
        那是防热册头部被陈旧快照吃掉的正确设计，副作用是**计数标量永远进不来**：
        gate_registry 的 total_gates 被 052c2817f4 直提成 180 后又被陈旧袋压回 174，
        rule_catalog 的 total_files 停在 274 而实际 292 条。逐册直提＝把结构缺陷转嫁给
        "谁的基底恰好最新"，不成立。现口径：条目合并完成后按段实际长度就地重算，
        于是任何一只碰这两册的袋都会把标量修正，无需任何人去直提。

        行级改写（不用正则）：只认"顶层『键: 整数』"，且原样保留该行行尾（CRLF 仓里
        把一行改成 LF＝制造混合行尾）。红队 P1 补硬：顶层同键**必须恰好一行**——YAML
        重复顶层键时 safe_load 取最后一个而我改第一个，会把"改错行"伪装成自愈成功，
        且让 GATE-21 永红并振荡；段不是集合/标量不是整数/计数已一致/形态不认识 ⇒
        一律不动（自愈是附加收益，绝不因此把可落地的袋变成死信，解析失败只 log 不抛）。
        """
        pairs = all_derived_total_pairs().get(rel.rsplit("/", 1)[-1])
        if not pairs:
            return merged
        try:
            import yaml  # noqa: PLC0415

            data = yaml.safe_load(merged)
        except Exception as exc:  # noqa: BLE001 — 解析不了就交给 GATE-21 判红，此处不改
            logger.warning("[landing] 派生标量自愈跳过（YAML 不可解析）%s: %s", rel, exc)
            return merged
        if not isinstance(data, dict):
            return merged
        out = merged
        lf = chr(10)
        cr = chr(13)
        for scalar, section in pairs.items():
            declared = data.get(scalar)
            actual = data.get(section)
            if not isinstance(actual, (list, dict)) or not isinstance(declared, int):
                continue
            if declared == len(actual):
                continue
            prefix = scalar + ":"
            lines = out.split(lf)
            bodies = [ln[:-1] if ln.endswith(cr) else ln for ln in lines]
            idxs = [i for i, b in enumerate(bodies) if b.startswith(prefix) and b == b.lstrip()]
            if len(idxs) != 1:
                logger.warning(
                    "[landing] 派生标量不改写 %s: %s（顶层同键行 %d 个，须恰好 1——"
                    "重复键/缺位交 GATE-21 判红，禁在这里猜哪行是真）",
                    rel,
                    scalar,
                    len(idxs),
                )
                continue
            i = idxs[0]
            tail_cr = lines[i].endswith(cr)
            lines[i] = f"{scalar}: {len(actual)}" + (cr if tail_cr else "")
            out = lf.join(lines)
            logger.info(
                "[landing] 派生标量自愈 %s: %s %d → %d（按段 %s 实际长度重算）",
                rel,
                scalar,
                declared,
                len(actual),
                section,
            )
        return out

    def _drift_all_same_session(self, item: dict, anchor: str, current_dev: str, paths: list[str]) -> bool:
        """漂移提交是否**全部**归属本会话（同会话连投多袋是常态，不得系统性假死信）。

        红队 B5：工作区停在分叉点、同会话先后两袋改同一文件——按纯字节判定第二袋必红，
        而它吃的正是本会话自己的前一次落地，不是他人内容。判据用 `[GW:sid]` 归属：
        任一提交无标记或归属他会话 ⇒ 不豁免（保守判红）。
        """
        sid = str(item.get("session_id") or "")
        if not sid:
            return False
        r = self._git_repo("log", "--format=%H%x09%s", f"{anchor}..{current_dev}", "--", *paths, check=False)
        if r.returncode != 0:
            return False
        rows = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        if not rows:
            return False  # 拿不到漂移提交清单 ⇒ 不豁免
        for row in rows:
            _sha, sep, subj = row.partition(chr(9))
            if not sep:
                return False
            m = _GW_OWNER_RE.search(subj)
            if not m or m.group(1) != sid:
                return False
        return True

    def _merge_base(self, base: str, other: str) -> str | None:
        """两 commit 的共同祖先；不可判（浅克隆/对象缺失）→ None，调用方退回 base。"""
        r = self._git_repo("merge-base", base, other, check=False)
        if r.returncode != 0:
            return None
        return (r.stdout or "").strip() or None

    def _legacy_base_drift_reason(self, item: dict, current_dev: str) -> str | None:
        """无 base_head 的存量项：以「袋创建时间 + GW 归属」替代时间基底做快进判定。

        判据=dev 上本袋 `created_at` 之后触及本袋路径的提交里，是否存在**别的会话**的
        GW 落地。有 ⇒ 本袋快照必是陈旧字节，快进＝整覆盖他人已落地内容 ⇒ 冲突死信；
        没有 ⇒ 快进放行。拿不到时间/无法归属（早期无标记提交）⇒ 保守放行——
        本函数是存量过渡兜底，不是新主路，宁可漏判也不误杀无辜袋。
        刻意不猜 base（不重演 old_dev^ 那类兜底），只在证据确实存在时判红。

        S-12（2026-09-24 本包治本，被 815312f93d 陈旧快照覆回后又读实时分支尖）：
        判定点位必须用调用方传入的 `current_dev`——CAS 每轮重试重取 dev 点位，用实时
        `refs/heads/dev` 会让"判定点位"与"实到点位"错位（第 2 轮起判的是别处的历史）。
        """
        created = str(item.get("created_at") or "")[:19].replace("T", " ")
        sid = str(item.get("session_id") or "")
        paths = sorted(self._item_paths(item))
        if not created or not sid or not paths:
            return None
        r = self._git_repo(
            "log",
            f"--since={created}",
            "--format=%H%x09%s",
            current_dev,
            "--",
            *paths,
            check=False,
        )
        if r.returncode != 0:
            return None
        offenders: list[str] = []
        for row in (r.stdout or "").splitlines():
            sha, sep, subj = row.partition("\t")
            if not sep:
                continue
            m = _GW_OWNER_RE.search(subj)
            owner = m.group(1) if m else ""
            if owner and owner != sid:
                offenders.append(f"{sha.strip()[:12]}←{owner}")
        if not offenders:
            return None
        return (
            f"冲突：历史项无 base_head，时间基底判定 dev 在本袋创建（{created}）之后由"
            f"他会话落过同路径 {len(offenders)} 笔（{offenders[:3]}）——快进必整覆盖他人"
            f"已落地内容，死信回属主 requeue 取新基底（F-AUDIT-QUEUE-04 存量兜底）"
        )

    # ------------------------------------------------------------------
    # 快照应用（blob → 真实文件；delete action 删文件）
    # 注册表族文件走条目级三向合并（W2），非注册表维持整文件覆盖零变更
    # ------------------------------------------------------------------
    def _read_blob_text_opt(self, sha: str, rel: str) -> str | None:
        """读取 <sha>:<rel> 文本；对象/路径不存在返回 None（三向合并缺侧语义）。

        刻意走 _git_repo（临时文件输出）而非 _read_blob_bytes 的
        run_subprocess_hidden——后者在部分环境对 stdout 做 CRLF 变换（实测
        tmp 仓 cat-file 返回 'hi\\r\\n'），字节漂移会污染合并器输入。
        """
        r = self._git_repo("cat-file", "blob", f"{sha}:{rel}", check=False)
        if r.returncode != 0:
            return None
        return r.stdout  # _run_git 的 stdout 已按 utf-8 解码（str）

    def _bag_payload_paths(self, item: dict) -> frozenset[str]:
        """本袋 payload 路径集合（分隔符归一 /，与 _extract_entry_paths 同口径）。"""
        out: set[str] = set()
        for f in item.get("files") or []:
            p = str(f.get("path") or "").replace("\\", "/").strip()
            if p:
                out.add(p)
        return frozenset(out)

    def _registry_entry_retired(self, entry: object, bag_paths: frozenset[str] = frozenset()) -> bool:
        """ours 侧合法退役判定（W2 规则 b 例外项）：条目引用路径盘上与 HEAD 双不存在。

        判据真源=DISPATCH_v1 Lane A 卡片 W2「该条目文件路径盘上与 HEAD 双不存在」；
        条目无路径候选 / 任一路径存活 → 非合法退役（采纳恢复，宁可多救不可漏救——
        被救回的多余条目由属主会话按正规删除通道二次移除，方向安全）。
        雷三豁免（st-c9-mfix，f43 两代死信同签名）：引用路径 ∈ 本袋 payload → 必非
        退役——该文件正随本袋落地，合并瞬间 HEAD 与主区盘上自然都还没有它，旧判据
        把「同袋自洽新增」误读成「合法退役」静默吞条目。豁免只放宽本袋自洽场景；
        袋外引用缺失的既有退役语义原样保留（真实退役吸收必须仍通行）。
        """
        paths = _extract_entry_paths(entry)
        if not paths:
            return False
        head = self._dev_head()
        for p in paths:
            if p in bag_paths:
                return False
            if (self.repo_root / p).exists():
                return False
            r = self._git_repo("cat-file", "-e", f"{head}:{p}", check=False)
            if r.returncode == 0:
                return False
        return True

    def _entry_base_blob(self, item: dict, rel: str) -> str | None:
        """袋内该路径记录的基底 git blob sha（无记录→None，调用方 fail-closed）。"""
        for f in item.get("files") or []:
            if f.get("path") == rel:
                return f.get("base_blob") or None
        return None

    def _base_had_path(self, item: dict, rel: str) -> bool:
        """袋内基底是否**有正证据**包含该路径（不可知一律按"没有"，不误杀新增件）。"""
        base_sha = str(item.get("base_head") or "")
        if base_sha and self._git_repo("cat-file", "-e", f"{base_sha}:{rel}", check=False).returncode == 0:
            return True
        return bool(self._entry_base_blob(item, rel))

    def _merge_registry_file(self, item: dict, rel: str, theirs_bytes: bytes, old_dev: str) -> bytes | None:
        """注册表族单文件三向合并（W2）；冲突/结构漂移抛 RuntimeError → 死信回人工。

        Returns:
            合并后的字节；None = 合并结果与 dev 现状逐字节一致（快照条目内容已被
            dev 全包含，无新内容可落）——调用方按 noop 跳过该文件（否则空提交
            NOTHING_TO_COMMIT 会撞假落地防线死循环）。
        """
        theirs_text = theirs_bytes.decode("utf-8", errors="replace")
        ours_text = self._read_blob_text_opt(old_dev, rel)
        if ours_text is None:
            # P0 补齐（红队 A1）：dev 侧无此文件≠"无合并语义"——若本袋**基底**里有它，
            # 那是 dev 在基底之后删了它；直接写回＝陈旧袋复活已删件，且绕过全部冲突判定。
            if self._base_had_path(item, rel):
                raise RuntimeError(
                    f"[landing] 注册表族 {rel} 在本袋基底存在而 dev 已删——拒绝用陈旧快照"
                    f"整文件写回（确需恢复请显式新建一袋并写明理由）"
                )
            return theirs_bytes  # 基底也无此文件＝真·新增件落地，无合并语义
        if ours_text == theirs_text:
            return None  # 快照与 dev 一致 → 零合并零提交（幂等 noop）
        base_sha = item.get("base_head") or ""
        base_text: str | None = None
        if base_sha and self._git_repo("cat-file", "-e", base_sha, check=False).returncode == 0:
            base_text = self._read_blob_text_opt(base_sha, rel)
        else:
            # F-AUDIT-QUEUE-04（2026-09-24 治本）：缺 base_head 时**不再兜底 old_dev^**。
            # 旧兜底把「陈旧快照不含该条目」读成「theirs 侧主动删除」并忠实执行——
            # 09-22 fb5a7821d 与 09-24 通宵 11 起热册「0 增 N 删」的同一真通道。
            # 现口径：退而求其次用袋内逐路径 base_blob（与 _pool_head_reader 同为 git
            # blob id 空间，直接 cat-file）；两样都没有 ⇒ fail-closed 死信，绝不猜基底。
            # 注：base_blob 键缺失与值 null 在 JSON 里不可区分（历史项都写 null），故
            # 本分支一律按「基底不可知」处理，不把 null 误读成「基底无此文件＝新增件」
            # ——那会让合并器把 ours-only 条目判成 theirs 新增而复活已删条目。
            base_blob = self._entry_base_blob(item, rel)
            if not base_blob:
                raise RuntimeError(
                    f"[landing] 注册表项基底不可知（base_head 与 base_blob 皆无）——"
                    f"拒绝以 {old_dev[:12]}^ 猜基底做合并（09-24 热册被吃病根）。"
                    f"修复通道：python scripts/commit_queue.py requeue <qid> "
                    f"--worktree-root <会话工作区>（重投即带新基底，66 号 §6.4 死信闭环）"
                )
            r = self._git_repo("cat-file", "blob", base_blob, check=False)
            if r.returncode != 0:
                raise RuntimeError(f"[landing] base_blob 对象不可读（{base_blob[:12]}）——死信回退人工")
            base_text = r.stdout
        bag_paths = self._bag_payload_paths(item)
        merged, conflict = three_way_merge_registry_yaml(
            base_text,
            ours_text,
            theirs_text,
            rel_path=rel,
            retired_check=lambda entry: self._registry_entry_retired(entry, bag_paths),
        )
        if conflict:
            raise RuntimeError(f"[landing] 注册表三向合并失败（死信回退人工）: {conflict}")
        merged = self._heal_derived_totals(rel, merged)
        if merged == ours_text:
            # 落地前自证读回（防 done 零变化，2026-09-28，q-0006 假成功治本）：零变化
            # 必须有合法解释——吸收有解（他袋已落/陈旧携带/合法退役/自愈覆盖）→ 合法
            # noop 带审计注；判不了或判为吞没 → 拒绝记 done（确定性故障，死信不烧重试）。
            swallow, note = _noop_absorption_verdict(rel, base_text, ours_text, theirs_text)
            if swallow is not None:
                raise MergeSwallowVerifyError(swallow)
            meta = item.get("meta")
            if not isinstance(meta, dict):
                meta = {}
                item["meta"] = meta
            prev = str(meta.get("noop_audit") or "")
            meta["noop_audit"] = f"{prev}; {rel}: {note}" if prev else f"{rel}: {note}"
            logger.info("[landing] %s 合并零变化自证通过（合法 noop 吸收）: %s", rel, note)
            return None
        return merged.encode("utf-8")

    @_timed_phase("snapshot")
    def _apply_snapshot(self, item: dict, queue_root: Path, old_dev: str) -> list[str]:
        """把队列项快照落成 worktree 真实文件，返回 worktree 内绝对路径列表（commit pathspec 用）。"""
        wt_files: list[str] = []
        for entry in item.get("files") or []:
            rel = entry.get("path", "")
            if not rel:
                continue
            # 红队对称补齐（#ARCH-310，2026-09-12）：入队侧 _read_files_from_worktree
            # 已用 _validate_relpath 拦穿越/绝对路径/.git/密钥路径；落地侧同口径——
            # 畸形项（手改 JSON/未来非 CLI 写入方）在此死信而非越界写盘。
            try:
                rel = cq._validate_relpath(rel)
            except cq.QueueReject as exc:
                raise RuntimeError(f"快照路径校验拒绝: {rel}（{exc}）") from exc
            abs_path = self.worktree_path / rel
            if entry.get("action") == "delete":
                try:
                    os.remove(abs_path)
                except FileNotFoundError:
                    pass  # 幂等：已删不报错
                wt_files.append(str(abs_path))
                continue
            blob_ref = entry.get("blob_ref") or ""
            blob_path = queue_root / blob_ref
            try:
                content = blob_path.read_bytes()
            except OSError as exc:
                raise RuntimeError(f"blob 读取失败: {rel}（{blob_ref}，{exc}）") from exc
            merged = False
            if is_registry_mergeable(rel):
                # W2 治本（2026-09-22 注册表事故）：注册表族不做整文件覆盖——
                # fb5a7821d 陈旧快照 blob 一写抹掉 103 条已提交身份的病灶在此封死。
                content = self._merge_registry_file(item, rel, content, old_dev)
                if content is None:
                    continue  # 合并结果与 dev 一致 → noop，不写盘不进提交清单
                merged = True

            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_bytes(content)
            # M5.1 写后读回自验（rsync --checksum 语义，st-qcure-20260925）：落地器
            # 物化静默丢失（句柄占用半写/杀软隔离/盘面回滚）在此显形，不再等到 gate
            # 链之后以 NOTHING_TO_COMMIT 假落地死。期望值分流：注册表族 content 已被
            # 三向合并重写（_merge_registry_file 返回合并后字节），袋内 blob_sha256
            # 不再是落地基准 → 用合并后 in-memory 字节；普通文件用袋内 blob_sha256
            # （与 enqueue 落袋/--from-bag 自校验同哈希，兼验 blob 袋本身完好），缺失
            # 时退回写盘字节。delete 项无写盘、合并 noop 项不落盘，均天然豁免。
            expect_sha = (
                hashlib.sha256(content).hexdigest()
                if merged
                else (str(entry.get("blob_sha256") or "") or hashlib.sha256(content).hexdigest())
            )
            readback = abs_path.read_bytes()
            readback_sha = hashlib.sha256(readback).hexdigest()
            if readback_sha != expect_sha:
                n = _bump_item_retry(item, queue_root, "snapshot_retry")
                detail = (
                    f"快照写后读回不符（物化静默丢失）: {rel} 期望 sha256={expect_sha[:12]} 实得={readback_sha[:12]}"
                )
                if n >= _RETRY_META_MAX:
                    raise SnapshotVerifyError(
                        detail,
                        dead_result=_retry_dead_result(
                            "snapshot_retry",
                            "落地器物化静默丢失，快照已固化在袋 blob，请 "
                            "python scripts/commit_queue.py requeue <qid> 或报总包 st-qcure-20260925",
                            detail,
                        ),
                    )
                raise SnapshotVerifyError(f"{detail}——退 pending 重放自愈（第 {n}/{_RETRY_META_MAX} 次）")
            wt_files.append(str(abs_path))
        return wt_files

    # ------------------------------------------------------------------
    # dev CAS 推进（66 号 §6.3 修正 4：带上期望旧值，单写者免费保险）
    # ------------------------------------------------------------------
    @_timed_phase("prestage")
    def _prestage_snapshot(self, item: dict, commit_files: list[str]) -> None:
        """快照预暂存：把快照文件 add/rm 进 index（gate 链 staged-diff 完整性前置）。

        delete 项用 git rm --cached --ignore-unmatch（幂等，对齐
        GitCommitGateway._add_and_remove_normal_files 语义）；existing 用
        git add --pathspec-from-file（Windows 长路径安全）。失败抛 RuntimeError
        → 落地器转 COMMIT_FAILED 死信（不静默放行，gate 依赖 staged diff）。
        """
        dels: list[str] = []
        adds: list[str] = []
        for entry in item.get("files") or []:
            rel = entry.get("path", "")
            if not rel:
                continue
            if entry.get("action") == "delete":
                dels.append(rel)
            else:
                adds.append(rel)
        if adds:
            # Mode A 治本（st-commitspeed-20260916 晚，st-dbgap-fix/st-tickdrain 死信
            # 实证）：scripts/data/* 等 gitignored 路径混入快照，git add rc=1 整项死，
            # RuntimeError 截断后 AI 读不到病灶。前置 check-ignore 精确点名+可行动指引。
            chk = self._git_wt("check-ignore", "--no-index", "--", *adds, check=False)
            if chk.returncode == 0 and chk.stdout.strip():
                ignored = [x for x in chk.stdout.strip().splitlines() if x.strip()]
                raise RuntimeError(
                    "prestage 拒绝：以下快照路径被 .gitignore 忽略（再生产物区，禁入 git）：\n"
                    + "\n".join(f"  - {x}" for x in ignored[:10])
                    + "\n修复：①把文件移到非忽略目录（如 scripts/data/ 下代码应移 scripts/）后重新入队；"
                    "②或确认该路径应入库，修 .gitignore 精确豁免（对齐 sz_open_data 先例）后重新入队"
                )
            pathspec = self.worktree_path / ".git_prestage_add_paths.txt"
            pathspec.write_text("\n".join(adds) + "\n", encoding="utf-8")
            try:
                res = self._git_wt("add", f"--pathspec-from-file={pathspec}")
                if res.returncode != 0:
                    raise RuntimeError(f"prestage git add failed: {res.stderr.strip()[:200]}")
            finally:
                try:
                    pathspec.unlink()
                except OSError:
                    pass
        if dels:
            pathspec = self.worktree_path / ".git_prestage_rm_paths.txt"
            pathspec.write_text("\n".join(dels) + "\n", encoding="utf-8")
            try:
                res = self._git_wt("rm", "--cached", "--ignore-unmatch", f"--pathspec-from-file={pathspec}")
                if res.returncode != 0:
                    raise RuntimeError(f"prestage git rm failed: {res.stderr.strip()[:200]}")
            finally:
                try:
                    pathspec.unlink()
                except OSError:
                    pass
        logger.info(
            "[landing] 快照预暂存完成 adds=%d dels=%d（staged-diff 依赖型 gate 前置）",
            len(adds),
            len(dels),
        )

    @_timed_phase("cas")
    def _advance_dev(self, old_sha: str, new_sha: str) -> None:
        """`git update-ref refs/heads/<dev> <new> <old>` CAS；失败抛 CasConflict。

        git 2.48.1 实证：对已 checkout 的 dev 亦可用（plumbing update-ref 不做
        branch -f 的 checkout 保护）。共享 index 不被触碰（66 号 §9.7 保留）；
        主工作区文件由 ``_converge_main_workspace`` 受限收敛（仅快进干净文件），
        脏文件陈旧由「会话 worktree 独立工作区 + 死信重新入队」机制覆盖。

        双锁统一（2026-09-16 晚 Owner 开工令，st-commitspeed-20260916）：
        CAS 前获取 _GlobalCommitLock——消灭直连路径（git_commit.py 持全局锁
        [gate→stage→commit]）与队列 CAS 的 dev ref 竞态窗口（W4 孤魂提交
        301a6ee82a 实证：两把互斥锁互不排他→61 秒 gate 窗口内 dev 被抢先）。
        锁窗口极短（仅 update-ref 调用，<1s）；fail-open：锁不可得时退化为
        原裸 CAS（CAS 自身仍原子，全局锁是防线加固非正确性前提）。
        """
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: PLC0415
            _GlobalCommitLock,
        )

        _lock = None
        try:
            _lock = _GlobalCommitLock(
                self.repo_root,
                timeout=30.0,  # 短窗：直连提交临界区最长 ~5min，30s 探测够用
            )
            _lock.__enter__()
        except Exception as exc:  # noqa: BLE001 — 锁不可得=裸 CAS 降级（fail-open 加固）
            # 异常类型必须进正文：本行曾把 str 传给 _GlobalCommitLock（其契约是 Path，
            # 内部 strip_session_worktree 取 .parts）→ AttributeError 被 "锁不可得" 的
            # 措辞读成锁竞争，加固自落地起静默失效数小时（#ARCH-327）。
            logger.warning(
                "[landing] 双锁统一：全局锁未取到（%s: %s），退化为裸 CAS",
                type(exc).__name__,
                exc,
                exc_info=True,
            )
            _lock = None
        try:
            r = self._git_repo("update-ref", f"refs/heads/{self.target_branch}", new_sha, old_sha, check=False)
        finally:
            if _lock is not None:
                try:
                    _lock.__exit__(None, None, None)
                except Exception:  # noqa: BLE001
                    pass
        if r.returncode != 0:
            raise CasConflict(f"dev CAS 推进失败（期望 {old_sha[:12]}）: {(r.stderr or r.stdout).strip()[:300]}")

    # ------------------------------------------------------------------
    # 主工作区受限收敛（2026-08-23 裁定：66 号 §9.7 受控放松）
    # ------------------------------------------------------------------
    # 病根：landing 只 update-ref 推进 dev，主工作区文件停在旧内容——共享工作区
    # 会话读到陈旧字节，是陈旧快照覆写事故的温床（2026-08-23 实证）。
    # 放松边界：永不改主工作区的**脏**文件——仅当工作区文件与 old_sha 逐字节
    # 一致（无任何 WIP）才写入 new_sha 内容（纯快进，零丢失）；脏/缺失/删除
    # 冲突一律跳过并留痕 .runtime/commit_queue/main_workspace_sync.jsonl。
    # 幂等：重放时文件已等于 new_sha → already_synced 跳过。fail-open：
    # 收敛是 landing 成功后的补强，异常仅留痕不改变 LandingResult。

    def _worktree_matches(self, sha: str, rel: str) -> bool:
        """主工作区文件与 <sha>:<rel> 是否一致（git diff --quiet 语义，属性过滤器生效）。

        rc=0 → 一致；rc=1 → 有差异（含工作区缺失=删除态差异）；rc>1 → 错误抛异常。
        """
        r = self._git_repo("diff", "--quiet", sha, "--", rel, check=False)
        if r.returncode == 0:
            return True
        if r.returncode == 1:
            return False
        raise RuntimeError(
            f"git diff --quiet {sha[:12]} -- {rel} -> rc={r.returncode}: {(r.stderr or '').strip()[:200]}"
        )

    def _read_blob_bytes(self, sha: str, rel: str) -> bytes:
        """读取 <sha>:<rel> 的原始 blob 字节（bytes 模式，二进制安全）。"""
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

        r = run_subprocess_hidden(
            ["git", "cat-file", "blob", f"{sha}:{rel}"],
            cwd=str(self.repo_root),
            text=False,
            timeout=_GIT_TIMEOUT_SECONDS,
            env=_trusted_git_env(),
        )
        if r.returncode != 0:
            raise RuntimeError(f"cat-file blob {sha[:12]}:{rel} -> rc={r.returncode}")
        return r.stdout

    def _tree_has_path(self, sha: str, rel: str) -> bool:
        """<sha> 树中是否含 <rel>（cat-file -e 语义；对象异常按「无」处理——保守方向=跳过快进）。"""
        r = self._git_repo("cat-file", "-e", f"{sha}:{rel}", check=False)
        return r.returncode == 0

    def _converge_one(self, rel: str, old_sha: str, new_sha: str, is_delete: bool) -> str:
        """单文件收敛，返回动作 token（already_*/fast_forwarded/deleted/skipped_*）。"""
        target = self.repo_root / rel
        if self._worktree_matches(new_sha, rel):
            return "already_deleted" if is_delete else "already_synced"
        if not self._worktree_matches(old_sha, rel):
            if is_delete and not target.exists():
                return "already_deleted"  # 删除项 + 工作区已缺失：语义已达成
            return "skipped_missing" if not target.exists() else "skipped_dirty"
        # 未跟踪 WIP 补盲：git diff 对 untracked 不可见——「old_sha 无此路径 + 盘上
        # 有同名未跟踪文件」会被上方误判为双方一致。此时快进写入会覆写他人 WIP，
        # 违反零丢失铁律 → 按脏处理跳过（66 号 §9.7 放松边界以逐字节一致为前提，
        # untracked 文件对 old_sha 而言不是「一致」是「凭空多出」）。
        if not is_delete and target.exists() and not self._tree_has_path(old_sha, rel):
            return "skipped_dirty"
        # 干净（== old_sha）：快进
        if is_delete:
            try:
                os.remove(target)
            except FileNotFoundError:
                return "already_deleted"
            return "deleted"
        data = self._read_blob_bytes(new_sha, rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".converge_tmp")
        tmp.write_bytes(data)
        os.replace(tmp, target)  # 原子替换，并发读者不见半成品
        return "fast_forwarded"

    def _index_matches(self, sha: str, rel: str) -> bool:
        """主工作区 INDEX 与 <sha>:<rel> 是否一致（--cached diff 语义；rc>1 抛错）。"""
        r = self._git_repo("diff", "--quiet", "--cached", sha, "--", rel, check=False)
        if r.returncode in (0, 1):
            return r.returncode == 0
        raise RuntimeError(f"diff --cached {sha[:12]}:{rel} -> rc={r.returncode}")

    def _index_convergence_mode(self) -> str:
        """RB1 双开关（2026-09-29 治本战役）：off=完全关 / live=实做清 index / 缺省=shadow。

        shadow 只判不动（决策进审计流），观察期后由 data/runtime/main_index_convergence.live
        翻实做；data/runtime/main_index_convergence.off 一票关停（回退=v1 行为）。
        """
        runtime_dir = self.repo_root / "data" / "runtime"
        if (runtime_dir / "main_index_convergence.off").exists():
            return "off"
        if (runtime_dir / "main_index_convergence.live").exists():
            return "live"
        return "shadow"

    def _converge_index_one(self, rel: str, old_sha: str, new_sha: str, wt_action: str) -> str:
        """RB1 条件式 index 收敛臂：清「纯落地残影」、保「他意 staged WIP」（零丢失）。

        前提=工作树已等于 dev 新 blob（wt_action 为落地成功态），此时 index 只可能：
          ==new → already（无残影）；==old → 纯残影（session staged 旧版后工作树演进），
          restore --staged --source=<new_sha> 清之（显式 source，不依赖主区 HEAD 分支位）；
          异于两者 → 他会话有意 staged 的 WIP → skip_staged_wip（禁碰）。
        执行前工作树复验关竞态窗；off/shadow 模式只判不动（shadow 记 would_* 进审计）。
        """
        mode = self._index_convergence_mode()
        if mode == "off":
            return "index_off"
        if wt_action in ("skipped_dirty", "skipped_missing", "error"):
            return "index_skip_dirty_wt"
        if not self._worktree_matches(new_sha, rel):
            return "index_skip_dirty_wt"
        if self._index_matches(new_sha, rel):
            return "index_already"
        if not self._index_matches(old_sha, rel):
            return "index_skip_staged_wip"
        if mode != "live":
            return "index_shadow_clear"
        r = self._git_repo("restore", "--staged", "--source", new_sha, "--", rel, check=False)
        if r.returncode != 0:
            return "index_error"
        return "index_cleared"

    @_timed_phase("converge")
    def _converge_main_workspace(self, item: dict, old_sha: str, new_sha: str) -> None:
        """landing 后主工作区受限收敛：干净文件快进 / 脏文件跳过留痕（fail-open）。"""
        qid = item.get("qid", "?")
        counts: dict[str, int] = {}
        audit_records: list[dict] = []
        for entry in item.get("files") or []:
            rel = entry.get("path", "")
            if not rel:
                continue
            try:
                action = self._converge_one(rel, old_sha, new_sha, entry.get("action") == "delete")
            except Exception as exc:  # noqa: BLE001 — 收敛 fail-open（landing 已成功）
                action = "error"
                logger.warning("[landing] 主工作区收敛异常 qid=%s %s: %s", qid, rel, exc)
            counts[action] = counts.get(action, 0) + 1
            if os.environ.get("RB1_DEBUG"):
                print(
                    f"RB1DBG qid={qid} old={old_sha[:10]} new={new_sha[:10]} dev_tip={self._git_repo('rev-parse', 'dev').stdout.strip()[:10] if False else '?'} path={rel}"
                )
            try:
                # RB1 条件式 index 收敛臂（2026-09-29 治本战役）：清纯落地残影/保他意 staged，
                # off/shadow 双开关缺省 shadow 只判不动；fail-open 同款（index 异常不回滚 landing）
                idx_action = self._converge_index_one(rel, old_sha, new_sha, action)
            except Exception as exc:  # noqa: BLE001 — 同上 fail-open
                idx_action = "index_error"
                logger.warning("[landing] index 收敛异常 qid=%s %s: %s", qid, rel, exc)
            counts[idx_action] = counts.get(idx_action, 0) + 1
            if idx_action not in ("index_already", "index_off", "index_skip_dirty_wt"):
                audit_records.append(
                    {
                        "ts": time.time(),
                        "qid": qid,
                        "path": rel,
                        "action": idx_action,
                        "old": old_sha[:12],
                        "new": new_sha[:12],
                    }
                )
            if action in ("skipped_dirty", "skipped_missing", "error"):
                audit_records.append(
                    {
                        "ts": time.time(),
                        "qid": qid,
                        "path": rel,
                        "action": action,
                        "old": old_sha[:12],
                        "new": new_sha[:12],
                    }
                )
        if audit_records:
            try:
                audit_path = self.queue_root / _MAIN_WS_SYNC_AUDIT_NAME
                audit_path.parent.mkdir(parents=True, exist_ok=True)
                with audit_path.open("a", encoding="utf-8") as fh:
                    for rec in audit_records:
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            except OSError as exc:
                logger.warning("[landing] 主工作区收敛审计写入失败（non-blocking）: %s", exc)
            logger.warning(
                "[landing] qid=%s 主工作区收敛存在跳过项（留痕 %d 条）: %s",
                qid,
                len(audit_records),
                counts,
            )
        else:
            logger.info("[landing] qid=%s 主工作区收敛完成: %s", qid, counts)

    # ------------------------------------------------------------------
    # 网关（惰性构造一次，跨项复用）
    # ------------------------------------------------------------------
    _RULES_PREFIXES_FOR_BASELINE = (
        "architecture_model/contracts/",
        "src/zephyr/shared/contracts/",
        "docs/01_policies_and_standards/rules/",
        "scripts/governance/_shared/thresholds.yaml",
        "scripts/governance/meta/",
        "scripts/governance/quickstart.md",
        "scripts/governance/quality_standard.md",
        "AGENTS.md",
    )

    def _integrity_baseline_mode(self) -> str:
        """integrity 基线面旗读取（战役 B0/M1·P3；fail-closed=snapshot=现行为）。

        与 validate_rules_integrity._baseline_mode 同优先级；读取本体在
        zephyr.gov_enforcement.derived_dirty_ledger（唯一点）。设施异常回 snapshot
        ⇒ 退回旧同步 spawn 通道，绝不因配置读不到而改变判定。
        """
        try:
            from zephyr.gov_enforcement.derived_dirty_ledger import read_integrity_baseline_mode

            return read_integrity_baseline_mode(self.repo_root)
        except Exception:  # noqa: BLE001 — 设施异常回现状
            return "snapshot"

    def _record_integrity_refresh_intent(self, item: dict, qid: str) -> None:
        """把"该刷一次完整性审计快照"的意图落册（战役 B0/M1·P3）：不 spawn、不等待、不改工作区。

        head 态下校验参考面=当前 HEAD（validate_rules_integrity check head 模式），
        DB 退出判定链 ⇒ 本记录纯观测（审计快照批量刷新的事件源，消费端=事件触发，
        宪法运维红线第 3 条）；去抖键=head_sha（N 件 → 1 刷）。
        """
        from zephyr.gov_enforcement.derived_dirty_ledger import append_intent

        touched = sorted(p for p in self._item_paths(item) if p.startswith(self._RULES_PREFIXES_FOR_BASELINE))
        append_intent(
            self.repo_root,
            {
                "qid": qid,
                "session_id": item.get("session_id", ""),
                "head_sha": self._dev_head(),
                "rules_touched": touched,  # 仅观测标签：head 态刷新与是否触碰规则册无关
                "reason": "queue_landed",
            },
        )

    @_timed_phase("baseline")
    def _refresh_integrity_baseline_main_repo(self, item: dict) -> str:
        """落地成功后在主仓补跑 integrity 基线注册（fail-open，返回空=成功）。

        【snapshot 回滚态专用】战役 B0/M1·P3：head 态下 B1/B2 调用点改走
        _record_integrity_refresh_intent，本方法仅在 flag
        integrity_baseline_mode.mode == "snapshot"（出厂态）被调用；
        真删待"零消费"观察一个发布周期后按净零条款退役。

        与直提路径 GATE-INTEGRITY-AUDIT reconciler 完全对齐：该 reconciler trigger
        always-True（每次 commit 无条件注册），本方法同样不设前缀过滤——任何队列
        落地后都刷新主仓基线（幂等，fail-open 留痕）。ZEPHYR_RECONCILER_MODE=1 是
        该脚本自带的防手动重注册门禁，此处为网关内部等价通道（landing 即网关延长
        的落盘臂）。
        """
        script = self.repo_root / "scripts" / "governance" / "meta" / "validate_rules_integrity.py"
        if not script.is_file():
            return f"integrity register script missing: {script}"
        env = {**os.environ, "ZEPHYR_RECONCILER_MODE": "1"}
        try:
            r = subprocess.run(
                [sys.executable, str(script), "--register"],
                cwd=str(self.repo_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return "register timeout(180s)"
        if r.returncode != 0:
            return f"rc={r.returncode}: {(r.stderr or r.stdout).strip()[:200]}"
        return ""

    def _get_gateway(self):
        """_get_gateway implementation."""
        if self._gateway is None:
            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
            from zephyr.security.access_control.session_concurrency import SessionRegistry

            if self._registry is None:
                # registry MUST 锚主仓根（生产者会话注册处；session_worktree.py:6011 同款
                # 模式——worktree  rooting 的 gateway + 主仓 rooting 的 registry）
                self._registry = SessionRegistry(self.repo_root)
            # roster_root=主仓根（st-k4-20260923 施工令⑥ env 名册/import 同源治本）：
            # 名册（原读 worktree=provision 时点 HEAD 态）与 importlib（进程 sys.path
            # →主区盘）分裂时，主区缺 gate 模块即必炸 ModuleNotFoundError（q-0006/q-0007
            # 双死信实证，机理归档=registry_incident_20260922/overnight_decisions_20260923.md
            # 三选一之③「名册读主区盘与 import 同源」）。都从主区盘后，名册+代码同盘
            # 同态，原子批窗口内外自洽。
            self._gateway = GitCommitGateway(
                project_root=self.worktree_path, registry=self._registry, roster_root=self.repo_root
            )
        return self._gateway

    # ------------------------------------------------------------------
    # 环境失败重试闸（M5.2 活锁治理，st-qcure-20260925）
    # ------------------------------------------------------------------
    def _env_pending_or_dead(
        self,
        item: dict,
        queue_root: Path,
        message: str,
        *,
        cause: BaseException | None = None,
        prescription: str = "环境类失败重试耗尽——排除 worktree/磁盘/锁环境故障后 requeue 重投",
    ) -> cq.LandingResult | cq.LandingEnvironmentError:
        """env 失败统一出口：计数 + 耗尽升级死信，未耗尽抛带标记的 LandingEnvironmentError。

        返回 LandingResult（计数耗尽）→ 调用方直接 return（死信带处方）；
        返回 LandingEnvironmentError（未耗尽）→ 调用方 raise（drain/pool 退 pending）。
        异常实例带 ``retried_key="env_retry"`` 标记，pool 环境分支凭此免二次计数。
        计数存 item JSON meta（跨 drain 轮存活，幂等可重放）。
        """
        n = _bump_item_retry(item, queue_root, "env_retry")
        if n >= _RETRY_META_MAX:
            return _retry_dead_result("env_retry", prescription, message)
        err = cq.LandingEnvironmentError(f"{message}（env_retry={n}/{_RETRY_META_MAX}）")
        err.retried_key = "env_retry"
        if cause is not None:
            err.__cause__ = cause
        return err

    def _gate_registration_env_outcome(
        self, item: dict, queue_root: Path, exc: Exception
    ) -> cq.LandingResult | cq.LandingEnvironmentError:
        """GateAutoRegistrationError 专判（M5.2）：新鲜子进程重跑 auto_register_gates 定真凶。

        - 子进程同败 → 确定性代码/册缺陷（daemon 重启救不了，fresh import 用的就是
          盘上代码＝重启后将加载的同款）→ 立即死信带修册处方；
        - 子进程成功 → 本进程陈旧纪元/瞬态 IO → 走 env 退 pending（计数升级防活锁），
          处方=重启 ZephyrAlpha_BeltDaemon 后自愈；
        - probe 自身未完成（OSError/超时，红队 P1-4）→ 不算确定性失败，同走 env 退
          pending 计数——冷缓存/杀软致首跑 >120s 的瞬态不得错杀成死信。
        """
        fresh_state, fresh_detail = self._probe_fresh_gate_registration()
        if fresh_state == "fail":
            return cq.LandingResult(
                ok=False,
                reason=(
                    "gate 册条目坏，fresh import 亦败（M5.2 确定性判别），修册后重投: "
                    f"{exc}｜fresh 子进程: {fresh_detail}"
                ),
            )
        return self._env_pending_or_dead(
            item,
            queue_root,
            f"landing 环境不可用: gate 装载失败但 fresh 子进程通过（本进程纪元陈旧/瞬态 IO）: {exc}",
            cause=exc,
            prescription="daemon 纪元陈旧，重启 ZephyrAlpha_BeltDaemon 后自愈",
        )

    def _probe_fresh_gate_registration(self, timeout: float = 120.0) -> tuple[str, str]:
        """新鲜子进程重跑 auto_register_gates（M5.2 纪元判别真源）。

        同解释器全新 import——子进程 sys.modules 无本进程的陈旧纪元，加载的是盘上
        代码。roster_root=self.repo_root（与 _get_gateway 同源：名册读主区盘与
        import 同盘同态，q-0006/q-0007 治本口径）。
        返回 (状态, 详情)：状态三态——"pass"=通过；"fail"=子进程跑完且注册失败
        （确定性缺陷）；"unreachable"=probe 自身未完成（OSError/超时，红队 P1-4，
        按环境瞬态处理而非确定性死信）。
        """
        probe = (
            "import sys\n"
            "from pathlib import Path\n"
            "from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry\n"
            "from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates\n"
            f"auto_register_gates(CommitGateRegistry(), Path({str(self.repo_root)!r}))\n"
        )
        try:
            r = subprocess.run(
                [sys.executable, "-c", probe],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return "unreachable", f"probe 未完成: {type(exc).__name__}: {exc}"
        if r.returncode == 0:
            return "pass", ""
        return "fail", f"rc={r.returncode}: {(r.stderr or r.stdout).strip()[:400]}"

    # ------------------------------------------------------------------
    # 落盘主入口（drain_queue landing 协议：fn(item, queue_root) -> LandingResult）
    # ------------------------------------------------------------------
    def __call__(self, item: dict, queue_root: Path) -> cq.LandingResult:
        """__call__ implementation.

        pool_mode 的路径锁在本函数**调用方**（_pool_process_item）获取/释放——本函数
        名与函数体必须保持 HEAD 存量形态（COMPLEXITY-GUARD 存量豁免按函数名绑定，
        拆名即丢豁免，q-20260923-st-k4-20260923-0002 死信实证）。
        """
        qid = item.get("qid", "?")
        session_id = item.get("session_id", "")

        # M3.2 sid 断言封路（st-qcure-20260925 核实结论）：本函数以单局部变量把
        # session_id 贯通 claim_files/commit/release_files/queue_marker（结构性一致，
        # requeue 重建亦从 sid 重生成新 qid，二者同源不失联）；唯一断裂面＝畸形项
        # sid 缺失/非法（手改 JSON/历史旧格式）。CAPABILITY-LOOKUP 审计 store 按 sid
        # 寻址，sid 断裂＝读空册冤杀——进幂等/门禁链前机械拒绝，死信带处方。
        try:
            cq._validate_session_id(session_id)
        except cq.QueueReject as exc:
            return cq.LandingResult(
                ok=False,
                reason=(
                    "队列项 session_id 非法（landing 全链按 sid 寻址会话审计 store，"
                    f"断裂=读空册冤杀）: {exc}；处方: requeue 重建（--session 指定正确会话）"
                ),
            )

        # 1) 幂等短路（崩溃重放不双落，66 号 §8）
        landed = self._already_landed(item)
        if landed:
            logger.info("[landing] qid=%s 已落盘（%s），幂等跳过", qid, landed[:12])
            # 崩溃 Completion：若崩溃发生在 update-ref 之后、主工作区收敛之前，
            # 重放走到这里——补跑收敛（幂等，已同步文件 already_synced 短路）。
            try:
                parent = self._git_repo("rev-parse", f"{landed}^", check=False)
                if parent.returncode == 0:
                    self._converge_main_workspace(item, parent.stdout.strip(), landed)
            except Exception as exc:  # noqa: BLE001 — 收敛 fail-open
                logger.warning("[landing] qid=%s 重放收敛异常（non-blocking）: %s", qid, exc)
            return cq.LandingResult(ok=True, landed_id=landed)

        try:
            self.ensure_worktree()
            gateway = self._get_gateway()
        except cq.LandingEnvironmentError as exc:
            outcome = self._env_pending_or_dead(item, queue_root, str(exc))
            if isinstance(outcome, cq.LandingResult):
                return outcome
            raise outcome from exc
        except Exception as exc:  # noqa: BLE001 — 环境失败≠物品失败：转专类供 drain 终止整轮不死信（2026-09-10 死信事故治本）
            if _is_gate_auto_registration_error(exc):
                # M5.2（st-qcure-20260925）：gate 装载失败先做新鲜判别再定退 pending
                # 还是死信——env abort 无计数时 HEAD 册真坏＝全队无限 pending 活锁。
                outcome = self._gate_registration_env_outcome(item, queue_root, exc)
                if isinstance(outcome, cq.LandingResult):
                    return outcome
                raise outcome from exc
            outcome = self._env_pending_or_dead(
                item,
                queue_root,
                f"landing 环境不可用（repo_root={self.repo_root}）: {type(exc).__name__}: {exc}",
                cause=exc,
            )
            if isinstance(outcome, cq.LandingResult):
                return outcome
            raise outcome from exc
        marker = queue_marker(session_id, qid)

        for attempt in range(1, self._max_cas_retries + 1):
            # 2) 同步 + 基底冲突判定
            try:
                self._sync_worktree()
            except cq.LandingEnvironmentError as exc:
                outcome = self._env_pending_or_dead(item, queue_root, str(exc))
                if isinstance(outcome, cq.LandingResult):
                    return outcome
                raise outcome from exc
            except (RuntimeError, OSError) as exc:
                # 瞬态 git 环境失败（索引锁争用 / Windows 句柄占用 / 命名管道对端瞬断
                # [WinError 233]）≠ 物品失败——高并发期他会话 commit 持主仓/worktree
                # 索引锁是常态（2026-09-10 二阶死信：worktree 修复后 26 项死于
                # reset --hard 撞锁）；同族还有 Windows 下外部进程开着文件句柄导致
                # reset --hard unlink 失败（2026-09-16 q-…-0018 实证："unable to unlink
                # old '…business_data_categories.yaml': Invalid argument"）与管道对端
                # 瞬断（OSError WinError 233，st-circ-a1-20260930 收编——OSError 非
                # RuntimeError，捕获面随之加宽）。转环境专类 → 项退回 pending、整轮
                # 终止等下次自举，绝不死信（特征串单一真源=_TRANSIENT_GIT_MARKERS）。
                if _is_transient_git_error(exc):
                    outcome = self._env_pending_or_dead(
                        item, queue_root, f"git 瞬态环境失败，项退回 pending 等下次自举: {exc}", cause=exc
                    )
                    if isinstance(outcome, cq.LandingResult):
                        return outcome
                    raise outcome from exc
                raise
            old_dev = self._dev_head()
            reason = self._conflict_reason(item, old_dev)
            if reason:
                return cq.LandingResult(ok=False, reason=reason)
            # 快照自洽见证层（ATK-3 补面，st-ff-snapself-20260926）：快进判定之后、
            # claim/快照应用之前——判定分工清晰（他包漂移归快进判定，陈旧携带归见证），
            # 先于 claim 免无谓占锁。部分命中=stale-path 级剥除，全袋命中=拒落死信点名。
            stale_verdict = self._witness_stale_carry(item, queue_root, old_dev)
            if stale_verdict is not None:
                return stale_verdict

            # 3) claim（净树基线）→ 快照应用 → 全门禁 commit → 释放 claim
            wt_files = [str(self.worktree_path / p) for p in sorted(self._item_paths(item))]
            claimed = gateway.claim_files(session_id, wt_files) if wt_files else []
            try:
                try:
                    commit_files = self._apply_snapshot(item, queue_root, old_dev)
                except SnapshotVerifyError as exc:
                    # M5.1 计数耗尽 → 死信回执（finally 仍释放 claim）；未耗尽 → 按环境
                    # 失败逃逸，drain/pool 退 pending 重放自愈。
                    if exc.dead_result is not None:
                        return exc.dead_result
                    raise
                # 快照预暂存（ALGO-NOTE-SYNC 等暂存依赖型 gate 前置）：gate 设计前提
                # =「必须在暂存集冻结后运行」（diff=git diff --cached），而 gateway.commit
                # 的 gate 链跑在自身 add 之前——快照只写工作区不进 index 时 gate 读到
                # 空/陈旧 diff，把内容合规的落地误判为未同步（q-0013/0014 死信实证）。
                # 预暂存后 gate 读到完整 staged diff；gateway.commit 内 add 幂等无副作用。
                self._prestage_snapshot(item, commit_files)
                if not commit_files:
                    # 全部文件为合并 noop（W2：合并结果与 dev 一致）——幂等空转，
                    # 记 noop landed_id 防重放（与 NOTHING_TO_COMMIT 同款哨兵）
                    logger.info("[landing] qid=%s 快照合并后零变化（noop）", qid)
                    return cq.LandingResult(ok=True, landed_id=f"{_NOOP_LANDED_PREFIX}{old_dev}")
                full_message = f"{item.get('message', '')}\n\n{marker}"
                # FORGED-GW-MARKER env 逃生（确为网关内部调用，与 run_git 同款 env）；
                # allow_non_worktree 见模块 docstring「门禁诚实记录」（不修改不放宽任何门禁判定）
                prev_env = os.environ.get(_GATEWAY_ENV)
                os.environ[_GATEWAY_ENV] = "1"
                _gates_t0 = time.monotonic()  # M5 矿①：gates 相位计时锚（单点累加在下方 finally）
                try:
                    result = gateway.commit(
                        session_id,
                        commit_files,
                        full_message,
                        allow_non_worktree=True,
                        # B2（#ARCH-310，2026-09-12）：落地快照与 worktree 同步之间存在
                        # 窗口，同族 reconciler 波次会重写自身衍生文件（script-manifest 等
                        # ——q-0001 死信实证），快照内容本身受 CAS 保护，容忍窗口漂移。
                        allow_tracked_drift=True,
                        # B3（#ARCH-310，2026-09-12）：队列项=入队者已圈定的单任务文件集
                        # （gate+自家测试是同一任务的合法组成——q-0007 死信实证），域拆分
                        # 责任在入队侧，落地不再二次执法；gateway 自动追加 multi-domain 标记留痕。
                        allow_multi_domain=True,
                        # B3b（#ARCH-310，2026-09-12）：永久区新文件（注册表/登记表）经队
                        # 列入队时，入队者的显式 --files 清单即 PROMOTION gate 要求的准入
                        # 意思表示（q-0015 死信实证：REG-RISK-TIER-001 被拦）；allow_promote
                        # 落地留痕审计不变。
                        allow_promote=True,
                        # 锁等待放宽（2026-09-16 q-…-0009/0010/0011 死信实证）：并发
                        # 提交期撞全局锁是瞬态，排队等待即可落地，gateway 缺省 60s 太短。
                        lock_wait_timeout=self._lock_wait_seconds,
                    )
                    # Mode B 自愈（st-commitspeed-20260916 晚，st-resched-fix/st-auditfix
                    # pathspec 死信实证）：新文件在 prestage 已 staged，但 gateway commit
                    # 报 "did not match any file(s) known to git"=index 中 staging 丢失
                    # （微因待观测——已加诊断）。自愈：重放 apply+prestage 一次后重试
                    # commit；仍败→死信带 git status 诊断（下次必可归因）。
                    if (
                        result.status.name == "COMMIT_FAILED"
                        and "did not match" in (result.message or "")
                        and "pathspec" in (result.message or "")
                    ):
                        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: PLC0415
                            CommitResult,
                        )

                        logger.warning(
                            "[landing] qid=%s pathspec 丢 staging 自愈：重放 apply+prestage 后重试 commit",
                            qid,
                        )
                        try:
                            commit_files = self._apply_snapshot(item, queue_root, old_dev)
                        except SnapshotVerifyError as exc:
                            if exc.dead_result is not None:
                                return exc.dead_result
                            raise
                        self._prestage_snapshot(item, commit_files)
                        _diag = self._git_wt("status", "--porcelain", "--", *self._item_paths(item))
                        result = gateway.commit(
                            session_id,
                            commit_files,
                            full_message,
                            allow_non_worktree=True,
                            allow_tracked_drift=True,
                            allow_multi_domain=True,
                            allow_promote=True,
                            lock_wait_timeout=self._lock_wait_seconds,
                        )
                        if result.status.name == "COMMIT_FAILED" and "did not match" in (result.message or ""):
                            result = CommitResult(
                                status=result.status,
                                message=(
                                    f"{result.message[:1200]}\n"
                                    f"[诊断] 自愈重试仍败——worktree status（本项文件）:\n{_diag.stdout[:600]}"
                                ),
                            )
                finally:
                    # gates 相位单点（QMine A1 件④，观测面 M5 矿①方案）：env 守卫 finally
                    # 处累加——主路径与 Mode B 重试两次 commit 全覆盖；刻意不拆函数
                    # （拆名即丢 COMPLEXITY-GUARD 存量豁免）。
                    _record_phase(self, "gates", (time.monotonic() - _gates_t0) * 1000)
                    if prev_env is None:
                        os.environ.pop(_GATEWAY_ENV, None)
                    else:
                        os.environ[_GATEWAY_ENV] = prev_env
            finally:
                if claimed:
                    gateway.release_files(session_id, claimed)

            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitStatus

            # 锁超时=瞬态环境失败，不是物品失败（2026-09-16 q-…-0009/0010/0011 死信实证：
            # 三项内容合法，仅因他会话正持全局提交锁而被判死信）。与 index.lock 同款语义
            # → 转环境专类：claim 已在上面 finally 释放，项退回 pending、终止本轮等下次
            # 自举，绝不死信（宪法「真实物品不被环境事故拖进坟墓」）。
            if result.status is CommitStatus.LOCK_TIMEOUT:
                outcome = self._env_pending_or_dead(
                    item,
                    queue_root,
                    f"全局提交锁争用（等待 {self._lock_wait_seconds:g}s 仍未得），项退回 pending 等下次自举: "
                    f"{(result.message or '')[:400]}",
                )
                if isinstance(outcome, cq.LandingResult):
                    return outcome
                raise outcome

            if result.status is not CommitStatus.OK:
                # 门禁阻断/git 失败 → 死信（不卡队，66 号 §4 裁定 4）；NOTHING_TO_COMMIT
                # 语义=快照与 HEAD 已一致（幂等空转）→ 视为落盘成功但无新 commit
                if result.status is CommitStatus.NOTHING_TO_COMMIT:
                    # 假落地防线（2026-09-15 q-20260915-0003 事故）：NOTHING_TO_COMMIT
                    # 只有当 item 全部 blob 与 old_dev 同路径内容一致时才是真幂等重放；
                    # 任一 blob 缺失/内容不符 = 快照应用被静默丢失，必须死信可见化，
                    # 禁止伪装 ok（该事故把真实变更落地失败记成了 landed_id=旧 HEAD）。
                    mismatched: list[str] = []
                    for entry in item.get("files") or []:
                        rel = entry.get("path", "")
                        want_sha = entry.get("blob_sha256")
                        if entry.get("action") == "delete":
                            if self._tree_has_path(old_dev, rel):
                                mismatched.append(rel)
                            continue
                        if not want_sha or not self._tree_has_path(old_dev, rel):
                            mismatched.append(rel)
                            continue
                        try:
                            have = self._read_blob_bytes(old_dev, rel)
                        except Exception:  # noqa: BLE001 — 读不到按缺失计
                            mismatched.append(rel)
                            continue
                        if hashlib.sha256(have).hexdigest() != want_sha:
                            mismatched.append(rel)
                    if mismatched:
                        return cq.LandingResult(
                            ok=False,
                            reason=(
                                "NOTHING_TO_COMMIT 但快照未真应用 "
                                f"(blob 与 old_dev 不符: {sorted(mismatched)[:5]})——"
                                "应用静默丢失，死信回退重新入队"
                                "（2026-09-15 q-0003 假落地事故防线）"
                            ),
                        )
                    return cq.LandingResult(ok=True, landed_id=f"{_NOOP_LANDED_PREFIX}{old_dev}")
                # 热册三连自动改道（A3 任务1，st-circ-a3-20260930）：FOREIGN-CHANGE/
                # HELD-OVERLAP/HOT-FILE-BASE-FRESHNESS 集中打两热册
                # （module_translation_registry/capability_canonical_file_registry）——
                # 结构性并发非物品违规，死信回人工是假失败。抛专类走 env 通道：项退
                # pending + B5 attempts 退避（≥3 次 15min/次惩罚、≥5 次拾取死信防活锁），
                # 等持册会话落地后重投即自愈（注册表族落地三向合并吸收增量）。
                if is_hot_registry_contention_block(result.status.name, result.message or ""):
                    raise HotRegistryContentionError(
                        f"热册并发阻断（{result.status.value}），项退回 pending 退避重投（结构性并发非物品违规）: "
                        f"{(result.message or '')[:400]}。处方: 等下次自举自动重投即自愈；若 attempts≥5 反复耗尽，"
                        f"与持册会话协调提交窗口后 requeue 重投"
                    )
                # 瞬态环境失败伪装成 COMMIT_FAILED 的截收（st-circ-a1-20260930，两类
                # 实证死因）：①LANDING-TIMEOUT——git 墙钟超时经 gateway 报 COMMIT_
                # FAILED 且消息带 "timeout after"；②TTL-METADATA "execution failed"
                # ——check_frontmatter_metadata.py 检查器子进程在 worktree 内起不来
                # （环境故障，frontmatter 根本没被判过）。两者都是环境失败不是物品
                # 违规：转 env 通道退 pending 配 env_retry 计数闸（≤3 防活锁），绝不
                # 死信（判据单一真源=_is_transient_env_failure）。
                if result.status is CommitStatus.COMMIT_FAILED and _is_transient_env_failure(result.message or ""):
                    outcome = self._env_pending_or_dead(
                        item,
                        queue_root,
                        f"瞬态环境失败伪装 COMMIT_FAILED，项退回 pending 等下次自举: {(result.message or '')[:400]}",
                    )
                    if isinstance(outcome, cq.LandingResult):
                        return outcome
                    raise outcome
                return cq.LandingResult(
                    ok=False,
                    # P0-3（#ARCH-310，2026-09-12）：400→2000——门禁阻断详情（多文件
                    # file:line 违规清单）400 字符常被截断，AI requeue 时读不到病灶。
                    reason=f"网关落盘失败（{result.status.value}）: {result.message[:2000]}",
                )

            # 4) CAS 推进 dev；失败=队列外写入者插队 → 同路径冲突死信 / 否则重试
            try:
                self._advance_dev(old_dev, result.commit_hash)
            except CasConflict:
                if not self._pool_mode:
                    new_dev = self._dev_head()
                    overlap = self._changed_paths_between(old_dev, new_dev) & self._item_paths(item)
                    if overlap:
                        return cq.LandingResult(
                            ok=False,
                            reason=(
                                f"冲突：dev CAS 竞态——{old_dev[:12]}..{new_dev[:12]} 间同路径 "
                                f"{sorted(overlap)} 被队列外写入者推进（66 号 §6.4，死信回退人工）"
                            ),
                        )
                    logger.warning(
                        "[landing] qid=%s CAS 竞态（无同路径冲突），重同步重试 %d/%d",
                        qid,
                        attempt,
                        self._max_cas_retries,
                    )
                    continue
                # ── 池化串行落地点（st-k4-20260923 施工令③）──────────────────
                # 冲突=重放一次落地段，不重跑门禁：门禁已在 result.commit_hash 的
                # 内容上全链通过，重放只做注册表重合并+树重建+commit-tree（见
                # _pool_cas_replay/_replay_commit_without_gates）。
                return self._pool_cas_replay(item, queue_root, old_dev, result.commit_hash, qid)
            logger.info("[landing] qid=%s 落盘完成 commit=%s", qid, result.commit_hash[:12])
            # 5) 主工作区受限收敛（干净文件快进/脏跳过留痕；fail-open 不改变落盘结果）
            try:
                self._converge_main_workspace(item, old_dev, result.commit_hash)
            except Exception as exc:  # noqa: BLE001 — 收敛 fail-open
                logger.warning("[landing] qid=%s 主工作区收敛异常（non-blocking）: %s", qid, exc)
            # 6) 规则类文件落地后主仓完整性基线刷新（#ARCH-310 认证战役 P1 F1 治本，
            #    2026-09-12）：gateway 直提路径的 post-commit reconciler 在主仓跑
            #    validate_rules_integrity --register；队列落地路径的同一 reconciler 跑
            #    在 serializer worktree 内——基线写进 worktree 副本，主仓基线恒 stale
            #    → TAMPERED 误报（宪法替换 c964c376c0 实证）。此处按 ritual 同款
            #    触发口径（_RULES_PREFIXES 命中）在主仓补跑一次注册；fail-open 留痕。
            # 6·P3（2026-09-24）：head 态=校验参考面读当前 HEAD，刷新义务消失 ⇒ 只记意图
            #    （不 spawn、不等待，旧路 timeout=180 白等面归零）；snapshot=出厂回滚态同步 spawn 原样。
            try:
                if self._integrity_baseline_mode() == "snapshot":
                    reg_note = self._refresh_integrity_baseline_main_repo(item)
                    if reg_note:
                        logger.warning("[landing] qid=%s 主仓基线注册失败（non-blocking）: %s", qid, reg_note)
                else:
                    self._record_integrity_refresh_intent(item, qid)
            except Exception as exc:  # noqa: BLE001 — 基线刷新/意图记录 fail-open（意图丢了也有兜底对账）
                logger.warning("[landing] qid=%s 基线刷新/意图记录异常（non-blocking）: %s", qid, exc)
            return cq.LandingResult(ok=True, landed_id=result.commit_hash)

        return cq.LandingResult(
            ok=False,
            reason=f"dev CAS 冲突重试耗尽（{self._max_cas_retries} 次）——死信回退人工",
        )

    # ------------------------------------------------------------------
    # 池化串行落地点（st-k4-20260923 施工令③：冲突=重放落地段，不重跑门禁）
    # ------------------------------------------------------------------
    def _pool_cas_replay(
        self,
        item: dict,
        queue_root: Path,
        base_dev: str,
        commit_sha: str,
        qid: str,
    ) -> cq.LandingResult:
        """CAS 推进 + 冲突重放循环（pool_mode 专用；替换 legacy 的整段重试）。

        - CAS 成功 → 主工作区收敛 + 主仓基线注册（与 legacy 步骤 5/6 同款）→ ok。
        - CAS 冲突 → 拆分重叠路径：非注册表同路径=死信回人工（零覆盖铁律，66 号
          §6.4）；注册表同册（或无重叠）→ _replay_commit_without_gates 重放落地段
          （同册不同条目由条目级三向合并吸收=零丢失），循环重试至成功/耗尽。
        - 重放后快照被 dev 全包含 → noop 哨兵（同 NOTHING_TO_COMMIT 口径）。
        """
        for attempt in range(1, self._max_cas_retries + 1):
            try:
                self._advance_dev(base_dev, commit_sha)
            except CasConflict:
                new_dev = self._dev_head()
                overlap = self._changed_paths_between(base_dev, new_dev) & self._item_paths(item)
                nonmergeable = overlap - {p for p in overlap if is_registry_mergeable(p)}
                if nonmergeable:
                    return cq.LandingResult(
                        ok=False,
                        reason=(
                            f"冲突：dev CAS 竞态（池化）——{base_dev[:12]}..{new_dev[:12]} 间同路径 "
                            f"{sorted(nonmergeable)} 被并发落地工推进（66 号 §6.4，死信回退人工）"
                        ),
                    )
                try:
                    replay = self._replay_commit_without_gates(item, queue_root, commit_sha, base_dev, new_dev)
                except cq.LandingEnvironmentError as exc:
                    # 红队 R2-P1-1（QCure st-qcure-20260925）：快照自验专类
                    # （SnapshotVerifyError←LandingEnvironmentError）不得被下方
                    # RuntimeError 兜底吞成死信——重放支与主支同享"首两跳退 pending
                    # 自愈 +3 次升级"闸，交还外层 env 处理（计数+退 pending）。
                    # 红队 R3-P2-1：耗尽态（已携 dead_result=精确快照处方）直接采信，
                    # 防止转 env 分支后无 retried_key 再计 env_retry、处方失真为笼统 env。
                    dead_result = getattr(exc, "dead_result", None)
                    if dead_result is not None:
                        return dead_result
                    raise
                except RuntimeError as exc:
                    return cq.LandingResult(ok=False, reason=f"冲突重放失败（死信回退人工）: {exc}")
                if replay is None:
                    logger.info("[landing] qid=%s 池化重放后零内容（noop@%s）", qid, new_dev[:12])
                    return cq.LandingResult(ok=True, landed_id=f"{_NOOP_LANDED_PREFIX}{new_dev}")
                base_dev, commit_sha = new_dev, replay
                logger.warning(
                    "[landing] qid=%s 池化 CAS 竞态，落地段重放（不重跑门禁）%d/%d commit=%s",
                    qid,
                    attempt,
                    self._max_cas_retries,
                    replay[:12],
                )
                continue
            logger.info("[landing] qid=%s 池化落盘完成 commit=%s", qid, commit_sha[:12])
            try:
                self._converge_main_workspace(item, base_dev, commit_sha)
            except Exception as exc:  # noqa: BLE001 — 收敛 fail-open（landing 已成功）
                logger.warning("[landing] qid=%s 主工作区收敛异常（non-blocking）: %s", qid, exc)
            try:
                if self._integrity_baseline_mode() == "snapshot":
                    reg_note = self._refresh_integrity_baseline_main_repo(item)
                    if reg_note:
                        logger.warning("[landing] qid=%s 主仓基线注册失败（non-blocking）: %s", qid, reg_note)
                else:
                    self._record_integrity_refresh_intent(item, qid)
            except Exception as exc:  # noqa: BLE001 — 基线刷新/意图记录 fail-open
                logger.warning("[landing] qid=%s 基线刷新/意图记录异常（non-blocking）: %s", qid, exc)
            return cq.LandingResult(ok=True, landed_id=commit_sha)
        return cq.LandingResult(
            ok=False,
            reason=f"dev CAS 冲突重试耗尽（{self._max_cas_retries} 次，池化重放）——死信回退人工",
        )

    def _replay_commit_without_gates(
        self,
        item: dict,
        queue_root: Path,
        prev_commit: str,
        base_dev: str,
        new_dev: str,
    ) -> str | None:
        """重放落地段（不重跑门禁）——门禁已在 prev_commit 内容上全链通过。

        ①他会话未触及本项注册表路径 → 树零变化，直接 re-parent prev_commit
          （commit-tree，同 message 逐字节保真——幂等 grep 与单写者断言依赖标记）；
        ②触及同册 → _apply_snapshot 对新 dev 重三向合并（他会话条目进合并基线，
          合并冲突/结构漂移抛 RuntimeError → 死信，绝不静默覆盖）+ read-tree 新 dev
          + prestage + write-tree 重建树 + commit-tree；
        ③重放后零内容（快照被 dev 全包含）→ None（调用方 noop 收口）。
        非注册表路径与新 dev 无交集由调用方判定（_pool_cas_replay 的 nonmergeable
        分流），blob 原样有效。plumbing（read-tree/write-tree/commit-tree）经
        ZEPHYR_SERIALIZER_MODE=1 白名单放行（scripts/git_guard.py PLUMBING 白名单），
        不触发 hook/门禁——门禁语义已由内容判据保全。
        """
        mergeable_paths = {p for p in self._item_paths(item) if is_registry_mergeable(p)}
        drifted = self._changed_paths_between(base_dev, new_dev)
        need_remerge = bool(mergeable_paths & drifted)
        # P0 治本（红队 2026-09-24 A2，生产实证 9de51e673f）：prev_commit 的树是
        # 「base_dev + 本袋 files」的**全量快照**，袋里没有的路径在树里仍是 base_dev 的旧
        # 字节。只要 base_dev..new_dev 之间存在任何漂移（哪怕与本袋路径零交集），re-parent
        # 就等于把期间他人落地的一切整树回退——mapbuild 那只只带 2 件的袋就是这样把本包
        # 4 件在册文件回退掉的。旧判据只看"注册表路径是否重叠"，看不见这条。
        if not drifted:
            r = self._git_repo("rev-parse", f"{prev_commit}^{{tree}}")
            tree = r.stdout.strip()
            return self._commit_tree_same_message(prev_commit, new_dev, tree)
        commit_files = self._apply_snapshot(item, queue_root, new_dev)
        if not commit_files:
            return None  # 重合并后全被 dev 吸收 → noop
        self._git_wt("read-tree", f"refs/heads/{self.target_branch}")  # 纯 index 置换，不触工作区
        self._prestage_snapshot(item, commit_files)
        tree = self._git_wt("write-tree").stdout.strip()
        return self._commit_tree_same_message(prev_commit, new_dev, tree)

    def _commit_tree_same_message(self, prev_commit: str, parent: str, tree: str) -> str:
        """commit-tree 造重放 commit（message 取原 commit %B 原文，-F 文件透传保真）。"""
        r = self._git_repo("log", "-1", "--format=%B", prev_commit)
        fd, msg_path = tempfile.mkstemp(prefix="zcq_replay_msg_", suffix=".txt")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                fh.write(r.stdout)
            r2 = self._git_repo("commit-tree", tree, "-p", parent, "-F", msg_path)
        finally:
            try:
                os.unlink(msg_path)
            except OSError:
                pass
        return r2.stdout.strip()


# ---------------------------------------------------------------------------
# k=4 通道池（st-k4-20260923 施工令：投机并行验证+串行落地）
# ---------------------------------------------------------------------------

# 池工 worktree 目录（<queue_root>/worktrees/w{i}）与分支（每工一支，互不干扰）。
# 刻意不落 .aidrafts_pool/：该池 lease 语义是「move 到 .aidrafts/{sid}+分支改名」，
# 面向长生命周期 session；且 .aidrafts/ 直接子目录会被 _sweep_stale_worktrees 按
# session 语义清扫（worktree_pool.py docstring 显式警告）。落地工棚是常驻专用位
# （<queue_root> 同 .runtime gitignored 共命运），复用 WorktreeLanding 既有
# ensure/_sync/provision 生命周期即「既有池机制」的落地形态——池激活零 worktree
# add 成本（首次创建后跨激活复用，优于 prefetch-per-activation）。
_POOL_WORKTREES_DIR = "worktrees"
_POOL_WORKER_HEARTBEAT_INTERVAL_S = 60.0  # 池级单心跳间隔（TTL 300s 的 1/5 富余）
# 同册不同条目 CAS 竞态重放时，注册表条目级三向合并吃掉同册冲突（施工令红蓝①
# 「4 路并发落地同册不同条目→全部成功零丢失」的落地机制）；非注册表同路径仍死信
# （66 号 §6.4 语义冲突回人工，零覆盖铁律不变）。


def resolve_pool_workers() -> int:
    """k 值读取（施工令⑦配置面）：thresholds SSoT `commit_queue_landing_pool_workers`。

    默认 4；显式配 1 = 降级开关（逐字节回退单传送带现行为）。非法/缺失回退默认。
    """
    try:
        k = int(_get_threshold("git_operations.commit_queue_landing_pool_workers", 4))
    except Exception:  # noqa: BLE001 — 配置面故障回退默认（可用性优先）
        return 4
    return k if k >= 1 else 1


def worker_worktree_path(queue_root: Path, worker_id: int) -> Path:
    """第 i 工的专用 worktree 路径（<queue_root>/worktrees/w{i}）。"""
    return (queue_root / _POOL_WORKTREES_DIR / f"w{worker_id}").resolve()


def worker_serializer_branch(worker_id: int) -> str:
    """第 i 工的专用分支（每工一支——并发 reset/commit 互不踩）。"""
    return f"serializer/commit-queue-w{worker_id}"


def make_worker_landing(
    repo_root: str | os.PathLike,
    queue_root: str | os.PathLike,
    worker_id: int,
    **kwargs: object,
) -> WorktreeLanding:
    """构造第 i 工落地执行体（独立 worktree+独立分支+pool_mode）。"""
    return WorktreeLanding(
        repo_root,
        queue_root=queue_root,
        worktree_path=worker_worktree_path(Path(queue_root), worker_id),
        serializer_branch=worker_serializer_branch(worker_id),
        pool_mode=True,
        **kwargs,  # type: ignore[arg-type] — 透传测试注入位（gateway/registry/lock_wait_seconds 等）
    )


# 同路径项池内串行化（路径级互斥）：池化后两个不同会话的队列项若同文件并行进
# 门禁段，会撞 claim 互斥（跨 session claim 冲突→CLAIM-REQUIRED 死信）与整文件
# 快照互踩——单传送带时代靠串行天然免疫的病灶。治法=工在进门禁段前按全局序取
# 本项全部路径锁（同路径项串行化，后工重同步到新 dev=基底冲突/合并判定照常生效）；
# 锁持者死亡（BaseException）经 finally 必释放。池级 lease 保证单进程排空，
# 进程内 threading.Lock 即完备。
_PATH_LOCK_GUARD = threading.Lock()
_PATH_LOCKS: dict[str, threading.Lock] = {}
_PATH_LOCK_TIMEOUT_S = 600.0  # 同路径在途工最长持锁预算（超时=环境失败退回 pending，绝不死信）


def _item_path_locks(paths: set[str]) -> list[threading.Lock]:
    """按全局序获取本项全部路径互斥锁（全局序防死锁）。超时抛 LandingEnvironmentError。"""
    deadline = time.monotonic() + _PATH_LOCK_TIMEOUT_S
    acquired: list[threading.Lock] = []
    try:
        for p in sorted(paths):
            with _PATH_LOCK_GUARD:
                lock = _PATH_LOCKS.setdefault(os.path.normcase(p), threading.Lock())
            remaining = max(0.1, deadline - time.monotonic())
            if not lock.acquire(timeout=remaining):
                raise cq.LandingEnvironmentError(f"路径锁等待超时（同路径项在途持锁）: {p}")
            acquired.append(lock)
        return acquired
    except BaseException:
        for lk in acquired:
            try:
                lk.release()
            except Exception:  # noqa: BLE001 — 释放兜底
                pass
        raise


def _release_path_locks(locks: list[threading.Lock]) -> None:
    """释放本项路径锁（逐把兜底，绝不因单把失败泄漏其余）。"""
    for lk in locks:
        try:
            lk.release()
        except Exception:  # noqa: BLE001
            pass


def _pool_heartbeat_loop(lease: cq.SerializerLease, stop: threading.Event) -> None:
    """池级单心跳（施工令④）：四工共享一个「池活体」心跳线程，杜绝四倍心跳病。

    逐项 renew 会随工数放大（4 工 × 每项一次=四倍心跳病）；独立线程按固定间隔
    续租，活体持有者 acquired_at 恒新鲜，TTL 永不对在工池触发。
    """
    while not stop.wait(_POOL_WORKER_HEARTBEAT_INTERVAL_S):
        try:
            lease.renew()
        except Exception:  # noqa: BLE001 — 续租失败不致命（活体感知分支兜底防抢），下轮再试
            logger.warning("[pool] 池级心跳续租失败（下轮重试）", exc_info=True)


def _pool_claim_item(root: Path) -> Path | None:
    """按队列 FIFO+车道优先认领一项（原子 rename pending→processing = 互斥点）。

    复用 _pick_head 车道语义（interactive 先落/machine 让路/30min 防饿死）；
    FileNotFoundError=被其他工抢先 → 重扫下一队首（原子 rename 即互斥锁，
    无需额外锁）；PermissionError=enqueue 写入窗瞬态 → 重扫。有界重扫防活锁。
    返回 processing 路径；队空/持续占用 → None（工收工）。
    """
    for _ in range(8):
        heads = sorted((root / "pending").glob("q-*.json"))
        if not heads:
            return None
        head, _lane = cq._pick_head(heads)
        if head is None:
            return None
        # D4 终止性复查·第二层：done/ 已有同名＝已落地件的幽灵（_mark_cascade_stale 回写复活
        # 或其他时序残留）——弃置续扫，不二次落地（判据：done 恒等于件数）
        if (root / "done" / head.name).exists():
            try:
                head.unlink()
            except (FileNotFoundError, PermissionError):
                pass
            continue
        processing_path = root / "processing" / head.name
        try:
            os.rename(head, processing_path)
        except FileNotFoundError:
            continue  # 他工已抢——重扫
        except PermissionError:
            continue  # enqueue 写入窗——重扫（同 drain_queue 竞态口径，不冤枉慢写入者）
        except FileExistsError:
            # processing 同名＝幽灵/竞态窗残留（D3 在工层兜底续跑，此处顺手清源防复发）
            try:
                head.unlink()
            except (FileNotFoundError, PermissionError):
                pass
            continue
        # 认领后终止性复查：rename 成功后 done/ 出现同名（同窗另一时序）⇒ 本副本亦幽灵——弃置
        if (root / "done" / head.name).exists():
            try:
                processing_path.unlink()
            except (FileNotFoundError, PermissionError):
                pass
            continue
        # F1 第二道保险（redblu_robust.md §五）：_mark_cascade_stale 延时二扫后仍可能有一线
        # 写回幽灵漏网（回写与认领 rename 的极窄交错）——rename 落定后 pending 同名再现
        # 即清扫竞态残留，unlink 之（本工持 processing 真身为准），防第三手再认领同件。
        residue = root / "pending" / head.name
        if residue.exists():
            try:
                residue.unlink(missing_ok=True)
            except (FileNotFoundError, PermissionError):
                pass
        return processing_path
    return None


def _selfcheck_now_iso() -> str:
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

    return now_utc().isoformat()


def _bootstrap_worktree_link_selfcheck(repo_root: str | os.PathLike) -> dict:
    """EV-04 serializer 启动自检：扫描会话 worktree 的 .git 链接完整性（只告警不阻断）。

    15 号文 EV-04 处方后半（2026-09-30 F 组夜班落地）：2026-08-29 打穿事故的形态之一
    是 worktree 目录在而 .git 链接丢失——landing 对自身专用 worktree 已有 _git_wt
    前置校验+ensure_worktree 重建，本自检覆盖其余会话 worktree（.worktrees/*）：
    每个含 .git 指针文件（gitfile，内容 gitdir: <path>）的目录，解析目标存在性；
    断链=登记 warning+审计 jsonl（.runtime/gate_audit/），不删不改不阻断（只观测，
    修复归各会话/归档流程）。返回统计供测试断言。
    """
    root = Path(repo_root)
    wt_base = root / ".worktrees"
    stats: dict = {"scanned": 0, "broken": [], "audit_path": None}
    if not wt_base.is_dir():
        return stats
    for child in sorted(wt_base.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        git_link = child / ".git"
        if not git_link.exists() or git_link.is_dir():
            continue  # 纯目录/主仓形态（.git 目录）不在本自检语义内
        stats["scanned"] += 1
        try:
            content = git_link.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            content = ""
        if content.startswith("gitdir:"):
            target = content.split(":", 1)[1].strip()
            target_path = Path(target)
            if not target_path.is_absolute():
                target_path = child / target_path
            if target_path.exists():
                continue
        stats["broken"].append(str(child))
    if stats["broken"]:
        logger.warning(
            "[landing][EV-04] 启动自检：%d 个会话 worktree .git 链接断链: %s", len(stats["broken"]), stats["broken"]
        )
        try:
            audit_dir = root / ".runtime" / "gate_audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_path = audit_dir / "worktree_link_selfcheck.jsonl"
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {"ts": _selfcheck_now_iso(), "scanned": stats["scanned"], "broken": stats["broken"]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            stats["audit_path"] = str(audit_path)
        except OSError as exc:  # noqa: BLE001 — 审计面降级不阻断
            logger.warning("[landing][EV-04] 自检审计写盘失败（不阻断）: %s", exc)
    return stats


def drain_queue_pool(
    queue_root: str | os.PathLike | None = None,
    *,
    repo_root: str | os.PathLike | None = None,
    workers: int | None = None,
    max_items: int | None = None,
    lease_timeout: float = cq._LEASE_TIMEOUT_SECONDS,
) -> dict:
    """k 工并发排空（st-k4-20260923：投机并行验证+串行落地）。

    - 池级 lease：整池一把 SerializerLease（与单传送带同文件同语义，互斥旧路径），
      独立心跳线程续租（单心跳，非四倍）。
    - 每波起 k 个工线程：各自 FIFO 认领互斥项（原子 rename）→ 独立 worktree 走
      完整门禁链（昂贵段并行——每工独立 GitCommitGateway，其 _GlobalCommitLock 按
      project_root=本工 worktree 键控，工间零锁竞争）→ dev ref CAS 串行落地点。
    - CAS 冲突：注册表族同册竞态由条目级三向合并重放吸收（零丢失）；非注册表
      同路径死信回人工（零覆盖，66 号 §6.4）；无路径冲突 → commit-tree 重放落地段
      不重跑门禁（施工令③）。
    - k<=1：逐字节降级回 cq.drain_queue 现行为（施工令⑦降级开关）。
    - 工线程死亡（BaseException）：其项留 processing，下一波 _recover_orphans
      回收重入队=工棚级复活；其余工与本波不受影响。
    """
    root = cq.resolve_queue_root(queue_root)
    repo = Path(repo_root) if repo_root else cq._REPO_ROOT
    # EV-04（15 号文）：serializer 启动自检会话 worktree .git 链接完整性（只告警不阻断）
    _bootstrap_worktree_link_selfcheck(repo)
    k = max(1, int(workers) if workers is not None else resolve_pool_workers())
    if k <= 1:
        # 降级开关：与现行为逐字节一致（不进任何池化代码路径）
        landing = WorktreeLanding(repo_root=repo, queue_root=root)
        return cq.drain_queue(root, landing=landing, max_items=max_items)

    cq._ensure_dirs(root)
    stats = {
        "skipped": False,
        "pool_workers": k,
        "recovered": 0,
        "done": 0,
        "dead": 0,
        "processed_qids": [],
        "stale_cleared": 0,
        "cascade_marked": 0,
        # 死信摘除后继重建计数（波 1B 1.7b 口径，2026-10-03 挖矿治本）：与
        # cq.drain_queue 的 stats 同键同义——池化四死信出口接 _seal_dead_letter
        # 后，后继重建扇出量对账面可见（此前池化死信不封印 ⇒ 此键恒缺席）。
        "successors_rebuilt": 0,
        "done_cleaned": 0,
        # D1 §4.2：已落地件的内存级联索引 [(qid, base_head)]（落地序）。落账时锁内
        # append（纯内存，不触 pending 盘）；波末 _run_pool_wave 统一交
        # cq.mark_cascade_stale_batch 一次消费（每波一遍 O(N)，替代逐落地 O(N²) 扇出）。
        "landed_index": [],
    }
    with cq.SerializerLease(root, timeout=lease_timeout) as lease:
        stats["recovered"] = len(cq._recover_orphans(root))
        stop_heartbeat = threading.Event()
        hb = threading.Thread(
            target=_pool_heartbeat_loop,
            args=(lease, stop_heartbeat),
            daemon=True,
            name="commit-queue-pool-heartbeat",
        )
        hb.start()
        try:
            budget = max_items
            while budget is None or budget > 0:
                wave_done = _run_pool_wave(root, repo, k, budget, stats)
                if wave_done == 0:
                    break
                if budget is not None:
                    budget -= wave_done
            stats["done_cleaned"] = len(cq.cleanup_done(root, ttl_days=cq._DONE_TTL_DAYS_DEFAULT)["removed"])
        finally:
            stop_heartbeat.set()
            hb.join(timeout=5.0)
    try:
        cq.emit_dead_backlog_alert(root)
    except Exception as exc:  # noqa: BLE001 — 旁路可观测性（与 drain_queue 收尾同口径）
        logger.warning("[pool] 死信积压告警异常（忽略）: %s", exc)
    try:
        cq.check_dead_burst(root)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[pool] 死信爆发告警异常（忽略）: %s", exc)
    return stats


# D3 工线程连错上限：同一工连续 err_streak 次异常才允许收工（防"每项必抛"退化成活锁）。
# 取 20 = 认领有界重扫 8 轮的 2.5 倍余量，且远小于实测队深峰值 83——保证暂时性异常自愈续跑，
# 系统性异常仍能收工，交波尾 _recover_orphans 兜底（绝不静默把整波永久占住）。
_WORKER_ERR_STREAK = 20


def _run_pool_wave(root: Path, repo: Path, k: int, budget: int | None, stats: dict) -> int:
    """一波 k 工并发（工收工即退出，全队收工即波终）。返回本波处理项数。

    波首孤儿回收=工棚级复活（上波死亡工遗留的 processing 项重入 pending）；
    环境失败（LandingEnvironmentError）置共享 env_aborted → 终止本波与外层排空
    （项退回 pending 绝不死信，与 drain_queue 同语义）。
    """
    stats_lock = threading.Lock()
    # 平台互斥补丁（总集成验收 st-circ-integ-20261001，2026-10-01）：Windows 实测
    # 并发同源 os.rename 300 轮 297 次「双方均成功」（本机 NTFS/MoveFileEx 语义，
    # 微基准在案）——「原子 rename 即互斥」在此平台不成立，双工可同领同一 pending 件
    # （in-process 可见面）→ 双落地。claimed 集=进程内认领去重第二道闸（rename 后
    # stats_lock 内查重，先到者加工、后到者让位；env 失败/read 失败退回 pending 时
    # 出册允许合法重领；集随波生命周期，跨波新 set 无残留）。
    shared: dict = {"processed": 0, "env_aborted": False, "budget_left": budget, "claimed": set()}
    cq._recover_orphans(root)  # 波首回收（上一波死亡工的遗孤）

    def _worker(worker_id: int) -> None:
        landing = make_worker_landing(repo, root, worker_id)

        def _reserve_slot() -> bool:
            """预扣一个处理名额：环境健康且预算有余才继续（领取失败由调用方归还）。"""
            with stats_lock:
                if shared["env_aborted"]:
                    return False
                if shared["budget_left"] is not None and shared["budget_left"] <= 0:
                    return False
                shared["budget_left"] = shared["budget_left"] - 1 if shared["budget_left"] is not None else None
                return True

        # D3（st-commitspeed-tbl-20260924）：工线程**不得早退**。
        # 一波 wave 只在全部线程返回后才结束；而外层只在"本波处理数>0"时起下一波。
        # 因此任何单工异常退出都会让余下的 straggler 把这一波无限开着——新波永不开，
        # 死亡工永不得重生（09-24 实测：三路工 06:2x 后停止认领，w2 单工把同一波开到 17 点，
        # 排空速率 18 件/时 → 2-4 件/时，积压 83 件；并发度恰为 1.000 的直接机理）。
        # 治法=认领/处理任一抛错都记档后继续循环；同因连错 _WORKER_ERR_STREAK 次才收工，
        # 防"每项必抛"变成活锁（收工后由波尾 join→下一波 _recover_orphans 兜底）。
        err_streak = 0
        while _reserve_slot():
            try:
                processing_path = _pool_claim_item(root)
            except Exception as exc:  # noqa: BLE001 — 早退即全队停摆，必须就地吞下并记账
                err_streak += 1
                _pool_wave_log(
                    root,
                    f"w{worker_id} claim_raised {type(exc).__name__}: {exc} streak={err_streak}"
                    f"{' GIVEUP' if err_streak >= _WORKER_ERR_STREAK else ''}",
                )
                if err_streak >= _WORKER_ERR_STREAK:
                    return
                continue
            if processing_path is None:
                with stats_lock:
                    if shared["budget_left"] is not None:
                        shared["budget_left"] += 1  # 未消费预扣预算归还
                # A3 装表：出口三选其一必须留痕——"认领 8 轮全被撞空"与"队空"是两种病，
                # 处方互斥（前者=认领竞态治本，后者=无事可干属正常收工）。
                _pool_wave_log(root, f"w{worker_id} exit=claim_none")
                return
            # 平台互斥补丁第二道闸（见 shared["claimed"] 注记）：Windows 双工同领去重
            # ——先到者登记认领并施工，后到者让位（同路径同字节件，peer 持有施工权）。
            with stats_lock:
                _dup_claim = processing_path.name in shared["claimed"]
                if not _dup_claim:
                    shared["claimed"].add(processing_path.name)
            if _dup_claim:
                _pool_wave_log(root, f"w{worker_id} claim_dup_windows_race {processing_path.stem}（让位 peer）")
                with stats_lock:
                    if shared["budget_left"] is not None:
                        shared["budget_left"] += 1  # 未消费预扣预算归还
                continue
            try:
                _pool_process_item(landing, root, processing_path, stats, stats_lock, shared)
            except Exception as exc:  # noqa: BLE001 — 同上：处理段异常不得杀工
                err_streak += 1
                _pool_wave_log(
                    root,
                    f"w{worker_id} process_raised {processing_path.stem} "
                    f"{type(exc).__name__}: {exc} streak={err_streak}"
                    f"{' GIVEUP' if err_streak >= _WORKER_ERR_STREAK else ''}",
                )
                if err_streak >= _WORKER_ERR_STREAK:
                    return
                continue
            err_streak = 0
        # A3 装表：走到这里＝名额预扣失败（环境终止旗或预算耗尽），与 claim_none 分流
        _pool_wave_log(
            root,
            f"w{worker_id} exit=no_slot env_aborted={shared['env_aborted']} budget_left={shared['budget_left']}",
        )

    threads = [
        threading.Thread(target=_worker, args=(i,), daemon=True, name=f"commit-queue-pool-w{i}") for i in range(k)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # D1 §4.3：波末一次性批量化级联标记（每波一遍 O(N)；单一 batch 实现与串传送带
    # 共用，禁新旧两版分叉）。本波内已被消费的命中已由 _pool_process_item 的索引
    # 命中记账补计，两段合计与逐件即时标记口径全等（§5 差分矩阵机械检验）。
    marked = cq.mark_cascade_stale_batch(root, stats.get("landed_index") or [])
    if marked:
        stats["cascade_marked"] += len(marked)
        logger.info("[pool] 波末批级联标记 stale %d 件: %s", len(marked), marked)
    return shared["processed"]


def _stale_revalidate_counted(item: dict, head_reader) -> tuple[bool, list[str]]:
    """stale 基底重校验的环境失败统一转 env 专类（QMine A1 件④，逃逸口封堵）。

    head_reader 的 git 读（_git_repo）在锁争用/句柄占用等瞬态下抛 RuntimeError——
    原样上抛会绕过 _pool_process_item 的 LandingEnvironmentError 计数分支（M3 线
    移交实测 38 笔环境失败逃逸），项滞留 processing 无限重放。此处统一转专类：
    调用方既有 env 分支计数 + 耗尽升级死信，与 landing 内部环境失败同闸同语义。

    注册表族 re-base 不死袋（卷宗 §10 Tier-2 条目 6，2026-09-27 治本）：注入
    mergeable_pred=is_registry_mergeable——该族 base_blob 漂移交本模块条目级三向
    合并仲裁（W2 2026-09-22 上线，真冲突仍死信带双方条目全文），不再在队列层判
    cascade_stale 退袋；非 mergeable 路径判定逐字节不变。放行路径留痕
    item.meta.rebased_registry（审计可见）。
    """
    try:
        return cq._revalidate_stale_base(item, head_reader, mergeable_pred=is_registry_mergeable)
    except cq.LandingEnvironmentError:
        raise
    except Exception as exc:  # noqa: BLE001 — git/OS 瞬态统一转环境专类
        raise cq.LandingEnvironmentError(
            f"stale 基底重校验环境失败（已收进 env_retry 计数闸）: {type(exc).__name__}: {exc}"
        ) from exc


@dataclass
class _PoolLedger:
    """pool 记账三元组打包（stats/stats_lock/shared）——helper 形参 ≤7（NO-LONG-PARAM-LIST，
    q-20261001-st-circ-a1-20260930-0001 死信治本：8 参被门禁拦）。"""

    stats: dict
    lock: threading.Lock
    shared: dict


def _emit_dead_letter_ledger(root: Path, qid: str, item: dict, reason: str) -> None:
    """死信→堵点本桥接（2026-10-01 提交链治本·C8）。

    落地侧死因（Popen TypeError / CLAIM_REQUIRED / 幽灵闸 / 路径锁超时）此前只落
    dead/ 袋 JSON——账本 .runtime/audit/commit_block_events.jsonl 零捕获（26 袋
    Popen 大屠杀账本缺席实证），维护班报表（commit_perf_report）因此看不见最大
    死因谱。纯追加审计；任何 IO 异常静默吞掉（观测设施不阻断死信主链）。
    """
    try:
        from datetime import datetime, timezone  # noqa: PLC0415

        audit_path = root.parent / "audit" / "commit_block_events.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": item.get("session_id") or "",
            "event": "queue_landing_dead",
            "gate_id": "QUEUE-LANDING",
            "qid": qid,
            "files_count": len(item.get("files") or []),
            "dead_reason": str(reason)[:200],
            "requeue_count": (item.get("meta") or {}).get("requeue_count", 0),
        }
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计失败静默，主链（死信落盘）不受影响
        pass


# 池化封印进程内互斥锁（2026-10-03 死信挖矿治本）：_bump_recurrence 对
# dead/_recurrence_state.json 是「读-改-写」，k 工并发裸奔会丢更新（同签名计数
# 少加 ⇒ 熔断延迟）。串行通道单线程天然安全；池化四出口经 _pool_seal_dead_letter
# 共享助手在锁内串行调用。跨进程互斥由 SerializerLease 承担（池与串行同 lease）。
_POOL_SEAL_LOCK = threading.Lock()


def _pool_seal_dead_letter(root: Path, item: dict) -> list[str]:
    """池化死信封印共享出口（波 1B 1.7b/c 口径对齐，2026-10-03 死信挖矿治本）。

    复用 cq._seal_dead_letter 唯一真源（归属五件套 + 同签名复发熔断 + 根因工序单
    + 后继重建），绝不复制实现（双实现漂移禁令）。池化两点适配：
    - 进程内互斥：见 _POOL_SEAL_LOCK 注释；
    - best-effort 降级：封印是治理附加面（死信袋必落 dead/ 不依赖封印成败），
      任何异常只 warning + 降级做纯内存归属五件套注入（cq._seal_dead_letter_
      attribution，无 IO 不会失败在盘上——归属仍可查，只是复发计数/工序单缺席），
      与 _notify_task_board_dead_letter「宁漏不误」同哲学。返回后继重建标记的
      qid 清单（消费方计入 stats.successors_rebuilt）。
    """
    try:
        with _POOL_SEAL_LOCK:
            return cq._seal_dead_letter(root, item)
    except Exception as exc:  # noqa: BLE001 — 封印失败不阻断死信主链（治理附加面）
        logger.warning(
            "[pool] qid=%s 死信封印失败（best-effort 降级：仅归属五件套，无复发计数/工序单）: %s",
            item.get("qid", "?"),
            exc,
        )
        try:
            cq._seal_dead_letter_attribution(item)
        except Exception as exc2:  # noqa: BLE001 — 纯内存注入最后的兜底也不许炸死信路径
            logger.warning(
                "[pool] qid=%s 归属五件套降级注入失败（袋落 dead/ 无封印字段）: %s", item.get("qid", "?"), exc2
            )
        return []


def _pool_env_failure_exit(
    root: Path,
    processing_path: Path,
    item: dict,
    qid: str,
    exc: BaseException,
    ledger: _PoolLedger,
) -> None:
    """pool 环境失败统一出口（st-circ-a1-20260930 自 LandingEnvironmentError 分支提取）：
    计数（env_retry，retried_key 已标记者免烧）→ 耗尽升级死信防活锁 → 未耗尽退回
    pending + 置共享终止旗终止本波。两个消费口：landing 专类逃逸（原分支）与
    泛化异常的瞬态截收（_is_transient_env_failure 命中）——同闸同语义零分叉。
    """
    dead: cq.LandingResult | None = None
    if not getattr(exc, "retried_key", ""):
        n = _bump_item_retry(item, root, "env_retry")
        if n >= _RETRY_META_MAX:
            dead = _retry_dead_result(
                "env_retry",
                "环境类失败重试耗尽——排除环境故障后 requeue 重投",
                f"landing 环境失败: {exc}",
            )
    if dead is not None:
        # 死信封印（2026-10-03 挖矿治本）：dead_reason 先落定（签名派生依赖），
        # 封印在锁外完成（item 由认领 rename 独占，互斥不依赖池级锁；锁内只留
        # 落盘+纯内存记账，D1「停世界窗口归零」口径不变）。
        item["dead_at"] = cq._now_iso()
        item["dead_reason"] = dead.reason
        _rebuilt = _pool_seal_dead_letter(root, item)
        with ledger.lock:
            cq._atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
            os.replace(processing_path, root / "dead" / processing_path.name)
            ledger.stats["dead"] += 1
            ledger.stats["successors_rebuilt"] += len(_rebuilt)
            ledger.stats["processed_qids"].append(qid)
            ledger.shared["processed"] += 1
        logger.error("[pool] qid=%s 环境失败重试耗尽，升级死信（防活锁）: %s", qid, dead.reason)
        return
    # B5（st-commitspeed-tbl-20260924）：退回前 attempts+1 持久化（≥3 惩罚
    # 退避、≥5 拾取死信，毒药件不再无限占队首）。
    if cq._attempts_backoff_enabled():
        cq._bump_retry_attempts(processing_path, item, f"{type(exc).__name__}: {exc}")
    try:
        cq._retry_transient(lambda: os.rename(processing_path, root / "pending" / processing_path.name))
    except OSError:
        logger.error("[pool] qid=%s 环境失败退回 pending 失败，留 processing 等波首回收", qid)
    with ledger.lock:
        ledger.shared["env_aborted"] = True
        if ledger.shared["budget_left"] is not None:
            ledger.shared["budget_left"] += 1
        ledger.shared.get("claimed", set()).discard(processing_path.name)  # 退回 pending=可合法重领
    logger.error("[pool] landing 环境失败，终止本波（项退回 pending，不死信）: %s", exc)


def _pool_process_item(
    landing: WorktreeLanding,
    root: Path,
    processing_path: Path,
    stats: dict,
    stats_lock: threading.Lock,
    shared: dict,
) -> None:
    """单工单项：stale 重校验 → landing → done/dead 落账（drain_queue 单项语义的
    线程安全移植；D1 后锁内仅纯内存记账+索引 append，终态迁移/级联批标记/死信
    通知全部出锁——processing_path 的独占由认领 rename（_pool_claim_item 原子
    rename 即互斥点）保证，不依赖池级锁）。

    D1 §4.4 认领判定与跨波兜底语义（§8 风险1 残余，显式在案）：基底越界判定入参=
    「盘上 stale 旗 ∪ stats["landed_index"] 内存命中」，**任何 base 已被本波越过的
    件，绝不允许未经重校验就落 dev**。批标记在波末才写盘 ⇒ 进程若死于波末 flush
    前，未消费的 stale 旗不落盘：本波内由内存 index 兜住；跨波由下一波
    `_recover_orphans` 回收 + 盘面影子重扫（上波已 flush 的影子仍在 pending/.stale/，
    拾取侧 _read_item 双读注入）覆盖——旗「只在内存」的丢失面以波为界，与串传送带
    的排空粒度一致。
    """
    item = cq._read_item(processing_path)
    if item is None:
        # 读取持续失败：放回 pending 下波再试（不冤枉慢写入者，不见死信）
        try:
            os.rename(processing_path, root / "pending" / processing_path.name)
        except OSError:
            pass
        with stats_lock:
            if shared["budget_left"] is not None:
                shared["budget_left"] += 1
            shared.get("claimed", set()).discard(processing_path.name)  # 退回 pending=可合法重领
        return
    qid = item.get("qid", processing_path.stem)
    # 幽灵会话存活闸·池工拾取点（裁定#459 延伸，st-circ-a1-20260930）：belt daemon
    # 生产主通道（bootstrap_drain_with_landing→drain_queue_pool）认领即判活——死会话
    # 袋不再烧工线程的 worktree 同步+全门禁段，直落 dead/（ghost_session，归 env 类
    # 处方可 requeue；CLI 手动 requeue 不受闸限）；判定不了 fail-open 放行。
    _ghost_sid = str(item.get("session_id") or "")
    if cq._session_ghost_dead(_ghost_sid, runtime_root=root.parent):
        cq._mark_ghost_dead_fields(item, _ghost_sid)
        # 死信封印唯一出口（2026-10-03 挖矿治本）：与串行 ghost 出口
        # （commit_queue.py drain 拾取点）同链——归属五件套+复发熔断+后继重建，
        # 不再手写 prescription/owner_session 两字段（治理面脱节的病根）。
        _rebuilt = _pool_seal_dead_letter(root, item)
        with stats_lock:
            cq._atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
            os.replace(processing_path, root / "dead" / processing_path.name)
            stats["dead"] += 1
            stats["successors_rebuilt"] += len(_rebuilt)
            stats["processed_qids"].append(qid)
            shared["processed"] += 1
            shared.get("claimed", set()).discard(processing_path.name)  # 终态=认领权释放
        logger.warning("[pool] qid=%s 属主会话已死（幽灵），拾取存活闸拒绝落地，直落 dead/", qid)
        cq._notify_task_board_dead_letter(item)
        return
    _item_t0 = time.monotonic()
    # B5 attempts 耗尽（st-commitspeed-tbl-20260924 止血，与 drain_queue 同语义）：
    # attempts≥死信阈值的毒药件拾取即死信，不再白耗一次 landing——队首让位。
    # dead_reason 注明 attempts 耗尽并附末次失败原因（三分类随末次原因走）。
    if cq._attempts_backoff_enabled() and cq._item_attempts(item) >= cq._ATTEMPTS_DEAD_THRESHOLD:
        item["dead_at"] = cq._now_iso()
        item["dead_reason"] = cq._attempts_exhausted_reason(item)
        # 死信封印唯一出口（2026-10-03 挖矿治本）：与串行 B5 出口同链（归属
        # 五件套+复发熔断+后继重建），替代红队 R2-P1-2 的手写处方补丁——处方/
        # 属主由封印统一注入，k=4 生产形态与单工口径全等。
        _rebuilt = _pool_seal_dead_letter(root, item)
        cq._atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
        os.replace(processing_path, root / "dead" / processing_path.name)
        with stats_lock:
            stats["dead"] += 1
            stats["successors_rebuilt"] += len(_rebuilt)
            stats["processed_qids"].append(qid)
            shared["processed"] += 1
            shared.get("claimed", set()).discard(processing_path.name)  # 终态=认领权释放
        logger.warning(
            "[pool] qid=%s attempts=%d 耗尽，拾取即死信（队首止血）: %s",
            qid,
            cq._item_attempts(item),
            item["dead_reason"],
        )
        cq._notify_task_board_dead_letter(item)
        return
    result: cq.LandingResult | None = None
    # M3 移交逃逸口封堵（QMine A1 件④，st-qmine-20260925）：stale 重校验的 git 读
    # 原在本 try 之外——锁争用/句柄占用类瞬态环境失败直接逃逸 env_retry 计数闸
    # （38 笔实测），项滞留 processing 无限重放。整段收进下方 try：环境失败经
    # _stale_revalidate_counted 转 LandingEnvironmentError 走既有 env 分支
    # （计数+耗尽升级死信），与 landing 内部环境失败同闸同语义。
    path_locks: list[threading.Lock] = []
    # D1 §4.4：认领时刻基底判定入参 =「盘上 stale 旗 ∪ 本波内存 landed_index 命中」。
    # 批标记延至波末写盘，盘旗对「同基底件已落盘之后才被认领」的件不再及时——内存
    # 索引补位（不变式：任何 base 已被本波越过的件，绝不允许未经重校验就落 dev）。
    idx_source = (
        None if (item.get("meta") or {}).get("stale") else cq._cascade_index_hit(item, stats.get("landed_index"))
    )
    try:
        if (item.get("meta") or {}).get("stale") or idx_source is not None:
            if idx_source is not None:
                # 内存索引命中补 stale 视图（字段口径与 _merge_stale_view 影子注入一致：
                # stale_by=落地序首因，审计溯源不因标记介质延迟写盘而丢；stale_at=此刻
                # 墙钟，视图字段，白名单级易变位）。
                meta = item.setdefault("meta", {})
                meta["stale"] = True
                meta.setdefault("stale_by", idx_source)
                meta.setdefault("stale_at", cq._now_iso())
            still_ok, mismatched = _stale_revalidate_counted(item, _pool_head_reader(landing))
            if still_ok:
                meta = item["meta"]
                meta.pop("stale", None)
                meta["stale_cleared_at"] = cq._now_iso()
                with stats_lock:
                    stats["stale_cleared"] += 1
            else:
                result = cq.LandingResult(
                    ok=False,
                    reason=(f"cascade_stale: 基底重校验不适用 {mismatched}（stale_by={item['meta'].get('stale_by')}）"),
                )
        if result is None:
            # 路径锁在调用方取/放（不改 __call__ 函数名——复杂度存量豁免按名绑定）：
            # 同路径项门禁段前串行化，锁覆盖幂等短路+应用+门禁+CAS 全程；持锁工死亡
            # （BaseException）经 finally 必释放。
            path_locks = _item_path_locks(landing._item_paths(item))
            result = landing(item, root)
    except cq.LandingEnvironmentError as exc:
        # 环境失败≠物品失败：当前项退回 pending、置共享终止旗（其余工收工不新增
        # 失败面）、本波结束——与 drain_queue「终止整轮」同语义。
        # M5.2 活锁治理：landing 内抛点已过计数闸（retried_key 标记）不重复计数；
        # landing 外抛点（路径锁超时等）就地补计数，同一 item 达上限升级死信，
        # 不再无限退 pending。
        _pool_env_failure_exit(root, processing_path, item, qid, exc, _PoolLedger(stats, stats_lock, shared))
        return
    except Exception as exc:  # noqa: BLE001 — 单项失败→死信不卡队；瞬态环境类先截收
        if _is_transient_env_failure(exc):
            # 瞬态环境失败逃逸截收（st-circ-a1-20260930）：WinError233 管道瞬断类
            # OSError 等不经 landing 内部判据点直达此处——旧径直落 "landing 异常"
            # 死信（77 封实证假失败）。按 env 分支同语义退 pending 计数防活锁。
            _pool_env_failure_exit(root, processing_path, item, qid, exc, _PoolLedger(stats, stats_lock, shared))
            return
        result = cq.LandingResult(ok=False, reason=f"landing 异常: {type(exc).__name__}: {exc}")
    finally:
        _release_path_locks(path_locks)
        # A2 装表：本 finally 覆盖成功/死信/环境失败三条出口（env 分支 return
        # 也走 finally），单件账不因失败路径漏记——失败件恰恰最该有账。
        _emit_landing_phase_stat(landing, item, (time.monotonic() - _item_t0) * 1000)

    # D1 §4.1/§4.5：终态迁移与死信通知全部出锁——processing_path 由认领 rename 独占
    # （_pool_claim_item 原子 rename 即互斥），不需要池级锁保护；顺序保持「先写带
    # landed_at/dead_at 的件，再 rename 到终态目录」（幂等重放依赖此原顺序）。
    # 锁内只留纯内存记账（微秒级），停世界窗口归零。
    if result.ok:
        item["landed_at"] = cq._now_iso()
        item["landed_id"] = result.landed_id
        cq._atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
        os.replace(processing_path, root / "done" / processing_path.name)
    else:
        item["dead_at"] = cq._now_iso()
        item["dead_reason"] = result.reason
        _emit_dead_letter_ledger(root, qid, item, result.reason)
        # 死信封印唯一出口（2026-10-03 挖矿治本）：与串行通用死信出口同链
        # （审计桥接先行、封印随后、再落盘——顺序对齐 cq.drain_queue 死信支）。
        _rebuilt = _pool_seal_dead_letter(root, item)
        cq._atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
        os.replace(processing_path, root / "dead" / processing_path.name)
    with stats_lock:
        if result.ok:
            stats["done"] += 1
            # D1 §4.2：落地序内存级联索引（波末 batch 消费；锁内 append 纯内存）。
            stats["landed_index"].append((qid, item.get("base_head")))
        else:
            stats["dead"] += 1
            stats["successors_rebuilt"] += len(_rebuilt)
        if idx_source is not None:
            # D1 计数语义保持：索引命中=旧实现「落地临界区内即时标记」的口径。波末
            # batch 只补计「仍留 pending」的命中；本波内已被后续认领消费的命中在此
            # 补计（含死信支——旧口径命中件死信同样先计标记），两段合计与旧口径全等。
            stats["cascade_marked"] += 1
        stats["processed_qids"].append(qid)
        shared["processed"] += 1
        shared.get("claimed", set()).discard(processing_path.name)  # 终态=认领权释放
    if not result.ok:
        logger.warning("[pool] qid=%s 进死信: %s", qid, result.reason)
        # D1 §4.5：task_board 死信联动出锁（旁路可观测性，失败不阻断排空，宁漏不误）。
        cq._notify_task_board_dead_letter(item)
    _item_dur = time.monotonic() - _item_t0
    if _item_dur > cq._SLOW_ITEM_LEDGER_SECONDS:
        cq._ledger_slow_item(root, qid, item.get("session_id"), round(_item_dur, 1))


def _pool_head_reader(landing: WorktreeLanding):
    """stale 重校验 head_reader 注入（drain_queue 的 P1 依赖级联协议对齐）：
    读当前 dev 该路径 blob sha；路径缺失返回 None。"""

    def _read(rel: str) -> str | None:
        r = landing._git_repo("rev-parse", f"refs/heads/{landing.target_branch}:{rel}", check=False)
        return r.stdout.strip() if r.returncode == 0 else None

    return _read


# ---------------------------------------------------------------------------
# 入队基底取数（F-AUDIT-QUEUE-04 治本，2026-09-24）
# ---------------------------------------------------------------------------

_LSTREE_CHUNK = 50  # Windows 命令行长度上限 ⇒ ls-tree pathspec 分块


def resolve_base_head(repo_root: Path | str) -> str | None:
    """入队基底 = 快照真源 commit（该工作区自己的 HEAD）——66 号 §6.4 快进判定的锚点。

    F-AUDITFIX-STALE-01（2026-09-24 晚）：原口径取「入队时刻看到的 refs/heads/dev 尖」，
    而快照字节来自这个工作区的树。两者不是一回事——工作区落后 dev 时取到的基底**比字节
    还新**，于是 diff(base, dev) 恒空、快进判定结构性失明，陈旧字节照样整覆盖他人已落地
    内容（正门装表后依然存在的通道，与今晚 815312f93d 吃掉在册修复同一病类）。
    现取 HEAD＝字节真源；工作区与 dev 对齐时两者同值＝零行为变化，落后时才能判红。


    病根：此前只有 machine 车道（``reroute_auto_commit_to_queue``）取基底，交互正门
    ``git_commit.py --enqueue`` 与裸 CLI ``commit_queue.py enqueue`` 均不传 ⇒ 生产袋
    全量 ``base_head=None`` ⇒ ``_conflict_reason`` 在 ``if not base`` 处先于注册表/
    非注册表分流即早退 None ⇒ 在库注释承诺的「非注册表文件维持逐文件快进判定」在
    生产形态下不成立，后落地快照可整文件覆盖他包已落地内容。

    取不到（非 git 目录/分支不存在）→ None：保持 tmp 隔离测试可跑，不因此拒绝入队
    （落地侧对 None 的处理见 ``_merge_registry_file`` 的 fail-closed 收紧）。
    """
    r = _run_git(Path(repo_root), ["rev-parse", "HEAD"], check=False)
    sha = (r.stdout or "").strip()
    return sha or None if r.returncode == 0 else None


def resolve_base_blobs(repo_root: Path | str, base_head: str | None, paths: list[str]) -> dict[str, str | None]:
    """逐路径取 base_head 树上的 git blob sha —— ``EnqueueOptions.base_blobs`` 填充器。

    此前 ``base_blob`` 全仓无填充点（``enqueue_item`` 两处硬编码 None），§6.4 陈旧基底
    重校验 ``_revalidate_stale_base`` 对每条恒走 ``if not base_blob: continue``＝结构
    空转。id 空间与 ``_pool_head_reader`` 的 ``rev-parse refs/heads/dev:<rel>`` 同为
    git blob sha（三套哈希口径不可互换——此处只认这一套）。

    单条 ``git ls-tree <base> -- <路径…>`` 覆盖一批（ARCH-GIT-CALL-BUDGET 批量化强制，
    禁逐文件子进程）；树上不存在（新增件）→ None。
    """
    uniq = [p for p in dict.fromkeys(paths) if p]
    if not base_head:
        return {p: None for p in uniq}
    found: dict[str, str] = {}
    for i in range(0, len(uniq), _LSTREE_CHUNK):
        chunk = uniq[i : i + _LSTREE_CHUNK]
        r = _run_git(Path(repo_root), ["ls-tree", base_head, "--", *chunk], check=False)
        if r.returncode != 0:
            continue  # 该块取不到 ⇒ 块内全 None（宁可少记基底，不猜）
        for line in (r.stdout or "").splitlines():
            meta, sep, path = line.partition("\t")
            parts = meta.split()
            if sep and len(parts) == 3 and parts[1] == "blob":
                found[path] = parts[2]
    return {p: found.get(p) for p in uniq}


def _stale_carry_candidate_blobs(item: dict, queue_root: Path | str) -> dict[str, str]:
    """见证前段（assert_snapshot_selfconsistent 拆件，COMPLEXITY-GUARD 处方）：收集
    「非注册表 modify 且袋字节 git-blob==其 base_blob」的路径。

    不判面（保守放行，与主函数 docstring 口径同源）：delete 项/注册表族/base_blob
    缺失（历史项未填、真新增件）/blob_ref 缺失/袋内字节读不到——拿不到证据不动手。
    """
    candidates: dict[str, str] = {}
    root = Path(queue_root)
    for entry in item.get("files") or []:
        rel = entry.get("path") or ""
        base_blob = entry.get("base_blob")
        if not rel or not base_blob or str(entry.get("action") or "modify") != "modify":
            continue
        if is_registry_mergeable(rel):
            continue
        ref = entry.get("blob_ref") or ""
        if not ref:
            continue
        try:
            data = (root / ref).read_bytes()
        except OSError:
            continue
        if _git_blob_sha(data) == base_blob:
            candidates[rel] = str(base_blob)
    return candidates


def assert_snapshot_selfconsistent(
    item: dict,
    *,
    queue_root: Path | str,
    repo_root: Path | str,
    current_dev: str,
) -> tuple[list[str], list[str]]:
    """快照自洽见证：袋字节 × 袋自身基底树（案卷 lane_stale_channel_repro ATK-3 判据层补层）。

    既有四机制（逐文件快进/基底重校验/注册表合并器/同会话豁免）的判据集恒为
    「dev 移动 × 袋路径集」，没有任何一层比较「袋内 blob 字节 vs 袋记录的
    base_blob」——「盘/袋字节陈旧而 dev 未被判到移动」遂成自由通道：同会话豁免
    盲区里陈旧携带回退自家前袋在册内容（ATK-3 形态），from-bag 错误基底把旧字节
    洗成"本包改动"吃非注册表热件（ATK-2 形态，其基底口径已在 requeue_dead_item
    同批治掉）。本函数把这层比较升为独立见证，消费端=WorktreeLanding._witness_stale_carry。

    口径：
    - 仅非注册表 modify 条目——注册表族维持条目级三向合并语义不回归，其同判据的
      加侧闸（陈旧携带条目不得复活 dev 已落地的删除，ATK-1）在 _plan_insert_splices；
    - 袋字节 git blob id == 条目 base_blob（resolve_base_blobs 填充的基底树 blob，
      同 id 空间，_git_blob_sha 唯一换算点）⇒ 本包没改该路径＝纯陈旧携带；
    - 两档输出（活性护栏实测等值即杀误伤正常并行，消费端只拒危险档）：
        dangerous: 携带且 dev 现字节≠袋字节 ⇒ 落地必回退在册内容，拒落对象；
        safe:      携带且 dev 现字节==袋字节 ⇒ 写=无操作，仅审计不拦；
    - base_blob 缺失（历史项未填/真新增件）一律不判——见证只比有底可证的条目；
      袋内 blob 字节读不到同样不判（拿不到证据不动手，与保守放行口径同源）。
    """
    candidates = _stale_carry_candidate_blobs(item, queue_root)
    if not candidates:
        return [], []
    dev_blobs = resolve_base_blobs(repo_root, current_dev, sorted(candidates))
    dangerous = sorted(rel for rel, sha in candidates.items() if dev_blobs.get(rel) != sha)
    safe = sorted(rel for rel, sha in candidates.items() if dev_blobs.get(rel) == sha)
    return dangerous, safe


# ---------------------------------------------------------------------------
# _commit_auto 改道（66 号 §7 一处改动；flag 门控，默认 OFF——启用=Owner 窗口批准）
# ---------------------------------------------------------------------------


def bootstrap_drain_with_landing(*, queue_root=None, repo_root=None) -> dict:
    """入队后自举排空（66 号 §8：无常驻进程，拿不到 lease 放弃等下次）。

    best-effort：任何失败仅 log 不抛出——队列项已入袋即安全，排空失败等下次自举。
    测试 monkeypatch 本函数以隔离真实落盘。
    k>1（thresholds `commit_queue_landing_pool_workers`，默认 4）→ 池化排空
    （st-k4-20260923）；k=1 → 单传送带现行为逐字节不变。
    """
    try:
        root = cq.resolve_queue_root(queue_root)
        repo: Path | None
        if repo_root:
            repo = Path(repo_root)
        else:
            # 与 try_bootstrap_drain 同款锚定口径：默认布局 <repo>/.runtime/commit_queue
            # 才可判归属仓；自定义队列根（测试隔离 tmp 等）保持 legacy 桩语义。
            repo = root.parents[1] if root.parent.name == ".runtime" else None
        if (
            repo is not None
            and (repo / "scripts" / "governance" / "commit_queue_landing.py").is_file()
            and resolve_pool_workers() > 1
        ):
            try:
                return drain_queue_pool(queue_root=root, repo_root=repo, workers=resolve_pool_workers())
            except cq.LeaseUnavailable as exc:
                logger.info("[reroute] %s —— 池/Serializer 在跑，放弃等下次自举", exc)
                return {
                    "skipped": True,
                    "reason": "lease_unavailable",
                    "done": 0,
                    "dead": 0,
                    "recovered": 0,
                    "processed_qids": [],
                    "stale_cleared": 0,
                    "cascade_marked": 0,
                    "done_cleaned": 0,
                }
        landing = WorktreeLanding(repo_root=repo if repo is not None else cq._REPO_ROOT, queue_root=root)
        return cq.try_bootstrap_drain(root, landing=landing)
    except Exception as exc:  # noqa: BLE001 — 自举失败绝不阻断改道返回（入袋即安全）
        logger.warning("[reroute] 自举排空失败（队列项安全在袋，等下次自举）: %s", exc)
        return {"skipped": True, "reason": f"bootstrap_error: {exc}"}


def split_auto_commit_snapshot(
    existing: list[str], project_root: str | os.PathLike
) -> tuple[list[tuple[str, bytes]], list[str], list[str]]:
    """auto-commit 快照文件切分：保护路径剔除（不入队）+ payload/deletes 构建。

    返回 (payload, deletes, skipped_protected)。保护清单真源=check_protected_paths
    .PROTECTED_PATTERNS（经 check_path 复用，零复制——见 reroute 内注释）。
    单独成函数供回归测试（Owner 裁定 2026-09-11 选 A 的复发性死信治本）。
    """
    from scripts.governance.d6_security.check_protected_paths import check_path

    payload: list[tuple[str, bytes]] = []
    deletes: list[str] = []
    skipped_protected: list[str] = []
    for f in existing:
        rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
        if check_path(rel):
            skipped_protected.append(rel)
            continue
        if os.path.isfile(f):
            try:
                payload.append((rel, Path(f).read_bytes()))
            except OSError as exc:
                # fail-safe：读盘异常向上传播 → gateway 降级直提（transient 占用可自愈）
                raise RuntimeError(f"reroute 快照读盘失败: {rel}（{exc}）") from exc
        else:
            deletes.append(rel)  # 已跟踪但盘上缺失 = 删除
    return payload, deletes, skipped_protected


def reroute_auto_commit_to_queue(gateway, session_id: str, files: list[str], message: str):
    """flag ON 时 _commit_auto 的改道目标：快照入袋即返回（66 号 §7 + 08 号文 §4.2 步骤 5）。

    语义对齐 _commit_auto 现状：
    - 文件解析复用 gateway._resolve_auto_commit_files（存在或已跟踪）——已跟踪但盘上
      缺失的文件 = 删除，经 enqueue_item(options=EnqueueOptions(deletes=...)) 通道入袋
      （action=delete）。
    - base_head=当前 dev HEAD 落袋（出队端逐文件快进冲突判定的锚点，66 号 §6.4）。
    - 返回 CommitResult(OK, commit_hash="QUEUED:{qid}")——对 reconciler 呈现「入袋即
      完成」（66 号 §4 裁定 1：会话提交 = 快照入队即返回），QUEUED: 前缀如实暴露
      异步落盘语义（对标 BatchedAutoCommitter 的 BUFFERED 合成回执先例）。

    fail-safe（08 号文 §4.2 步骤 5 任务口径）：快照读盘失败/入队异常（含 QueueReject）
    一律向上传播，由 gateway._commit_auto 捕获后 logging.warning + 降级现行直提——
    队列异常不阻塞 reconciler 工作流。本函数自身不吞异常；唯一正常提前返回是
    NOTHING_TO_COMMIT（无可提交文件，与直提路径同判）。
    """
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

    existing = gateway._resolve_auto_commit_files(files)
    if not existing:
        return CommitResult(
            status=CommitStatus.NOTHING_TO_COMMIT,
            message="no existing or tracked files to auto-commit",
        )
    # 自动同步保护路径过滤（Owner 裁定 2026-09-11 选 A，复发性死信治本，st-perf-plan-20260910）：
    # 保护文件（architecture_model/** 等）混入 reconciler 批次时，落盘必被 PROTECTED-PATHS
    # 门禁拦截且**整批陪葬**成死信——改为入队前剔除不碰，漂移留工作区归属主手动处理；
    # 门禁语义零改动（manual 直提路径照旧全量拦截），队列侧永不再产生此类死信。
    payload, deletes, skipped_protected = split_auto_commit_snapshot(existing, str(gateway.project_root))
    if skipped_protected:
        logger.warning(
            "[reroute] 自动同步保护路径过滤: 跳过 %d 项不入队（漂移留工作区归属主处理）: %s",
            len(skipped_protected),
            skipped_protected[:5],
        )
        if not payload and not deletes:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message=f"all {len(skipped_protected)} files protected-skipped: {skipped_protected[:5]}",
            )
    # M1.2（st-qcure-20260925）：改道前锁外预检——注定被门禁拦死的批次在入队前改判，
    # 不再依赖入队后落地死信暴露。与并行施工线 A（git_commit.py --enqueue）同参：
    # audit_event="enqueue"、skip={SESSION-REQUIRED, CLAIM-REQUIRED}（入队语义无
    # 会话流程/claim 前移，文件传绝对路径对齐 _rel_of 判定面）。
    # blocking → 返回 COMMIT_FAILED + 处方。刻意**返回值而非抛异常**：本函数异常会被
    # gateway._commit_auto 的 fail-safe 捕获降级直提（GW:3911）——那等于把死信批改道
    # 回直提老路绕开队列单写者；COMMIT_FAILED 回执让 reconciler 如实记失败零降级。
    pf_files = [str(Path(str(gateway.project_root)) / rel) for rel in ([p for p, _ in payload] + list(deletes or []))]
    try:
        from zephyr.gov_enforcement.rule_bridge.commit_preflight import run_preflight

        pf = run_preflight(
            gateway,
            pf_files,
            session_id,
            skip_gate_ids={"SESSION-REQUIRED", "CLAIM-REQUIRED"},
            audit_event="enqueue",
            commit_message=message,
        )
    except Exception as exc:  # noqa: BLE001 — 预检设施异常=放行入队（落地侧锁内权威链兜底，既有口径）+审计
        logger.warning("[reroute] preflight 设施异常，降级放行入队（锁内权威链兜底）: %s", exc, exc_info=True)
        try:
            from zephyr.gov_enforcement.rule_bridge.commit_preflight import _write_audit

            _write_audit(
                gateway,
                {
                    "session_id": session_id,
                    "event": "degraded_pass",
                    "path": "enqueue",
                    "error": f"{type(exc).__name__}: {exc}"[:300],
                    "files_count": len(pf_files),
                },
            )
        except Exception:  # noqa: BLE001 — 审计是旁路可观测性，失败不阻断改道
            pass
    else:
        if pf.blocking:
            return CommitResult(
                status=CommitStatus.COMMIT_FAILED,
                message=(
                    "reroute 预检拦截（注定死信批，不降级直提不空转入队——M1.2）:\n"
                    + pf.render_report(session_id)
                    + "\n处方: 逐项修复预检违规后重新触发；确属合法逃生请走 git_commit.py "
                    "对应旗标显式声明后重提"
                ),
            )
        if pf.degraded:
            logger.info("[reroute] preflight degraded（不阻断）: %s", pf.degraded)
    base_head = resolve_base_head(gateway.project_root)  # 同源真口径（勿再各写一条 rev-parse）
    base_blobs = resolve_base_blobs(
        gateway.project_root,
        base_head,
        [p for p, _ in payload] + list(deletes or []),
    )
    # QueueReject 等入队异常向上传播 → gateway fail-safe 降级直提（warning 留痕）
    # 签名对齐 A 段定稿：可选参数束走 options=EnqueueOptions（NO-LONG-PARAM-LIST 收口）
    item = cq.enqueue_item(
        session_id,
        message,
        payload,
        options=cq.EnqueueOptions(
            base_head=base_head,
            base_blobs=base_blobs,
            deletes=deletes or None,
            meta_extra={
                "rerouted_from": "_commit_auto",
                "lane": "machine",
            },  # 审计可追溯（改道来源标记；P1-D 车道让路交互提交）
        ),
    )
    bootstrap_drain_with_landing(repo_root=gateway.project_root)
    qid = item["qid"]
    logger.info(
        "[reroute] _commit_auto 改道入队: qid=%s session=%s files=%d deletes=%d",
        qid,
        session_id,
        len(payload),
        len(deletes),
    )
    return CommitResult(
        status=CommitStatus.OK,
        message=f"rerouted to commit queue: {qid}（快照入袋即完成，Serializer 异步落盘）",
        commit_hash=f"QUEUED:{qid}",
    )


# ---------------------------------------------------------------------------
# 单写者不变量断言（Owner 启用 flag 后的机械验证工具；66 号 §5 关键不变量①）
# ---------------------------------------------------------------------------


def assert_single_writer_dev_history(
    repo_root: str | os.PathLike,
    *,
    since: str | None = None,
    target_branch: str = cq._TARGET_BRANCH,
) -> list[dict]:
    """断言 dev 历史只经 Serializer 通道落盘（全部 commit 带 [GW:{sid}:{qid}] 队列标记）。

    参数
    ----
    since : 起始 sha（不含）——flag 启用时刻的 dev HEAD；None=全历史。
        Owner 验证用法：``assert_single_writer_dev_history(repo, since=<flag_on_sha>) == []``。

    返回违例 commit 列表（{sha, subject}；空列表=不变量成立）。
    merge commit（2+ parents）豁免——与两个 shell guard 的豁免口径一致
    （merge 由 merge gate 专管，非 Serializer 直提面）。
    """
    rev = f"refs/heads/{target_branch}"
    if since:
        rev = f"{since}..{rev}"
    # %B 多行——用 \x1e 记录分隔 + \x00 字段分隔（逐行 split 会把 body 切散）
    r = _run_git(
        Path(repo_root),
        ["log", "--format=%x1e%H%x00%P%x00%B", rev],
        check=True,
    )
    violations: list[dict] = []
    for record in r.stdout.split("\x1e"):
        record = record.strip("\r\n")
        if not record:
            continue
        parts = record.split("\x00")
        if len(parts) < 3:
            continue
        sha, parents, body = parts[0], parts[1], parts[2]
        if len(parents.split()) >= 2:
            continue  # merge commit 豁免（guard 同款口径）
        if not _QUEUE_MARKER_RE.search(body):
            violations.append({"sha": sha, "subject": body.splitlines()[0] if body else ""})
    return violations
