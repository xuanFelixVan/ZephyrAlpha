# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] scripts.governance.commit_queue_landing
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；scripts.commit_queue（队列协议/LandingResult）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway（全门禁落盘执行体）；zephyr.security.access_control.session_concurrency（主仓 session registry）
# [CONSUMERS] 全部 AI session（drain_queue(landing=...) 真落盘注入点）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway._commit_auto（flag ON 时 reroute 目标，延迟 import）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 永不改主工作区脏文件（66 号 §9.7 受控放松 2026-08-23：只写专用 worktree + 对象库 + dev ref CAS；landing 后主工作区受限收敛——仅当文件与旧 HEAD 逐字节一致才快进写入新内容，脏/缺失/删除冲突一律跳过留痕，零 WIP 丢失风险）；单写者（仅 Serializer lease 持有者经 drain 调用）；幂等不双落（done/landed_id + is-ancestor + 标记 grep 三重判定）；门禁一套不裁（GitCommitGateway 全门禁链零适配，worktree 形态 100 门禁天然生效）；CAS 冲突/基底冲突→死信不卡队；主工作区收敛 fail-open（landing 已成功，收敛异常仅留痕不改变结果）
# [MODIFY-GUARD] 66 号备忘 §6.3 MVP 形态 + §8 幂等算法 + §9 边界；08 号文 §4.2 步骤 3/5；[GW:{sid}:{qid}] 标记格式（POST-COMMIT-GUARD / REFERENCE-TRANSACTION-GUARD 消费方）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] __call__ 永不抛普通 Exception（落盘失败→LandingResult(ok=False, reason) 进死信）；BaseException 向上传播（模拟进程崩溃语义，项留 processing 等回收）
# [TESTS] tests/governance/test_commit_queue_integration.py
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

import json
import logging
import os
import re
import subprocess
import time
from pathlib import Path

import scripts.commit_queue as cq

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_SERIALIZER_BRANCH = "serializer/commit-queue"  # 专用 worktree 检出的分支（随每项 reset 到 dev）
_WORKTREE_DIR_NAME = "worktree"  # <queue_root>/worktree——任务口径专用目录（08 号文 §4.2 步骤 3）
_MAX_CAS_RETRIES = 3  # dev CAS 冲突重试上限（66 号 §8：重放产生同内容 commit，CAS 保护不分叉）
_GIT_TIMEOUT_SECONDS = 120  # 与 worktree_pool.run_git 同款
_MAIN_WS_SYNC_AUDIT_NAME = "main_workspace_sync.jsonl"  # <queue_root>/ 下——主工作区收敛跳过/异常留痕（66 号 §9.7 受控放松 2026-08-23）

# 队列标记正则：[GW:{sid}:{qid}]——sid 字符集 [A-Za-z0-9._-]（入队校验保证无冒号/右括号）
_QUEUE_MARKER_RE = re.compile(r"\[GW:[^\]:\s]+:q-[^\]\s]+\]")

# 网关 env 标记（FORGED-GW-MARKER env 逃生语义=确为网关内部调用；与 run_git 同款）
_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"
# Serializer 可信 git 调用 env（66 号 §4 裁定 7 plumbing 白名单 + worktree_pool fast-path 先例）
_SERIALIZER_MODE_ENV = "ZEPHYR_SERIALIZER_MODE"
_GIT_GUARD_FAST_PATH_ENV = "ZEPHYR_GIT_GUARD_FAST_PATH"


class CasConflict(RuntimeError):
    """dev ref CAS 推进失败（old 期望值失配——队列外写入者插队）。"""


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
    """落地 git 执行（统一 utf-8/隐藏窗口/超时；stderr 进异常消息，报错非静默）。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    r = run_subprocess_hidden(
        ["git", *args],
        cwd=str(repo_or_wt),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=_GIT_TIMEOUT_SECONDS,
        env=_trusted_git_env(),
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} -> rc={r.returncode}: {(r.stderr or r.stdout).strip()[:400]}")
    return r


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
    ) -> None:
        """__init__ implementation."""
        self.repo_root = Path(repo_root).resolve()
        self.queue_root = cq.resolve_queue_root(queue_root)
        self.worktree_path = Path(worktree_path).resolve() if worktree_path else (self.queue_root / _WORKTREE_DIR_NAME).resolve()
        self.target_branch = target_branch
        self.serializer_branch = serializer_branch
        self._registry = registry
        self._gateway = gateway
        self._max_cas_retries = max_cas_retries

    # ------------------------------------------------------------------
    # git 便捷封装
    # ------------------------------------------------------------------
    def _git_repo(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """_git_repo implementation."""
        return _run_git(self.repo_root, list(args), check=check)

    def _git_wt(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        """_git_wt implementation."""
        return _run_git(self.worktree_path, list(args), check=check)

    def _dev_head(self) -> str:
        """_dev_head implementation."""
        return self._git_repo("rev-parse", f"refs/heads/{self.target_branch}").stdout.strip()

    # ------------------------------------------------------------------
    # 专用 worktree 生命周期（66 号 §6.3 MVP 形态）
    # ------------------------------------------------------------------
    def ensure_worktree(self) -> Path:
        """确保专用 worktree 就位（幂等；仅 Serializer 调用，单写者无竞态）。

        状态机：已注册且目录在 → 复用；注册残留但目录丢失 → prune 后重建；
        目录在但未注册（上次半成品）→ 物理删除该专用目录后重建；
        分支已存在（历史遗留）→ 不 -b 直接检出复用。
        """
        wt = self.worktree_path
        r = self._git_repo("worktree", "list", "--porcelain")
        registered = False
        target_norm = os.path.normcase(str(wt))
        for line in r.stdout.splitlines():
            if line.startswith("worktree ") and os.path.normcase(line.split(" ", 1)[1].strip()) == target_norm:
                registered = True
                break
        if registered and wt.is_dir():
            return wt  # 就位，复用
        if registered and not wt.is_dir():
            logger.warning("[landing] 专用 worktree 注册残留但目录丢失，prune 后重建: %s", wt)
            self._git_repo("worktree", "prune")
        elif wt.exists() and not registered:
            # 半成品残骸（上次 worktree add 中断）——仅限本专用路径，物理清掉重建
            # （CAND-GOVSEC-001①：safe_rmtree 硬断言——resolve 后须严格落在
            # queue_root 内 + 拒绝 reparse point，拦截 rmtree 越界/junction 穿透）
            logger.warning("[landing] 专用 worktree 半成品残骸，清除后重建: %s", wt)
            from zephyr.shared.io.file_utils import safe_rmtree  # noqa: PLC0415

            safe_rmtree(wt, allowed_prefix=self.queue_root, ignore_errors=True)
            self._git_repo("worktree", "prune")
        wt.parent.mkdir(parents=True, exist_ok=True)
        branch_exists = self._git_repo(
            "rev-parse", "--verify", "--quiet", f"refs/heads/{self.serializer_branch}", check=False
        ).returncode == 0
        if branch_exists:
            self._git_repo("worktree", "add", str(wt), self.serializer_branch)
        else:
            self._git_repo(
                "worktree", "add", str(wt), "-b", self.serializer_branch, f"refs/heads/{self.target_branch}"
            )
        logger.info("[landing] 专用 worktree 就位: %s (branch=%s)", wt, self.serializer_branch)
        return wt

    def _sync_worktree(self) -> None:
        """每项处理前同步：serializer 分支 reset --hard 到 dev HEAD + clean -fd。

        66 号 §11 #6 不变量（每项处理前 worktree HEAD == dev HEAD 且 clean）的机械实现；
        同时自愈 POST-COMMIT-GUARD reset / 上次崩溃孤儿 commit 等分支漂移。
        """
        self._git_wt("reset", "--hard", f"refs/heads/{self.target_branch}")
        self._git_wt("clean", "-fd")

    # ------------------------------------------------------------------
    # 幂等判定（66 号 §8：is-ancestor / done 记录 + 标记 grep 三重）
    # ------------------------------------------------------------------
    def _already_landed(self, item: dict) -> str | None:
        """返回已落盘 commit sha（未落盘返回 None）——重放不双落的核心。"""
        landed = item.get("landed_id") or ""
        if landed:
            r = self._git_repo(
                "merge-base", "--is-ancestor", landed, f"refs/heads/{self.target_branch}", check=False
            )
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

    def _conflict_reason(self, item: dict, current_dev: str) -> str | None:
        """base_head 基底冲突判定；无 base_head（A 段兼容项）→ None（快进应用）。"""
        base = item.get("base_head")
        if not base or base == current_dev:
            return None
        if self._git_repo("cat-file", "-e", base, check=False).returncode != 0:
            return f"冲突判定失败：base_head 无效（{base}）——死信回退人工（66 号 §6.4）"
        overlap = self._changed_paths_between(base, current_dev) & self._item_paths(item)
        if overlap:
            return (
                f"冲突：入队基底 {base[:12]} 之后 dev 已推进且触及同路径 {sorted(overlap)}"
                f"——逐文件快进判定失败，死信回退属主会话（66 号 §6.4/§9.1）"
            )
        return None

    # ------------------------------------------------------------------
    # 快照应用（blob → 真实文件；delete action 删文件）
    # ------------------------------------------------------------------
    def _apply_snapshot(self, item: dict, queue_root: Path) -> list[str]:
        """把队列项快照落成 worktree 真实文件，返回 worktree 内绝对路径列表（commit pathspec 用）。"""
        wt_files: list[str] = []
        for entry in item.get("files") or []:
            rel = entry.get("path", "")
            if not rel:
                continue
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
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_bytes(content)
            wt_files.append(str(abs_path))
        return wt_files

    # ------------------------------------------------------------------
    # dev CAS 推进（66 号 §6.3 修正 4：带上期望旧值，单写者免费保险）
    # ------------------------------------------------------------------
    def _advance_dev(self, old_sha: str, new_sha: str) -> None:
        """`git update-ref refs/heads/<dev> <new> <old>` CAS；失败抛 CasConflict。

        git 2.48.1 实证：对已 checkout 的 dev 亦可用（plumbing update-ref 不做
        branch -f 的 checkout 保护）。共享 index 不被触碰（66 号 §9.7 保留）；
        主工作区文件由 ``_converge_main_workspace`` 受限收敛（仅快进干净文件），
        脏文件陈旧由「会话 worktree 独立工作区 + 死信重新入队」机制覆盖。
        """
        r = self._git_repo(
            "update-ref", f"refs/heads/{self.target_branch}", new_sha, old_sha, check=False
        )
        if r.returncode != 0:
            raise CasConflict(
                f"dev CAS 推进失败（期望 {old_sha[:12]}）: {(r.stderr or r.stdout).strip()[:300]}"
            )

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
                action = self._converge_one(
                    rel, old_sha, new_sha, entry.get("action") == "delete"
                )
            except Exception as exc:  # noqa: BLE001 — 收敛 fail-open（landing 已成功）
                action = "error"
                logger.warning("[landing] 主工作区收敛异常 qid=%s %s: %s", qid, rel, exc)
            counts[action] = counts.get(action, 0) + 1
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
                qid, len(audit_records), counts,
            )
        else:
            logger.info("[landing] qid=%s 主工作区收敛完成: %s", qid, counts)

    # ------------------------------------------------------------------
    # 网关（惰性构造一次，跨项复用）
    # ------------------------------------------------------------------
    def _get_gateway(self):
        """_get_gateway implementation."""
        if self._gateway is None:
            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
            from zephyr.security.access_control.session_concurrency import SessionRegistry

            if self._registry is None:
                # registry MUST 锚主仓根（生产者会话注册处；session_worktree.py:6011 同款
                # 模式——worktree  rooting 的 gateway + 主仓 rooting 的 registry）
                self._registry = SessionRegistry(self.repo_root)
            self._gateway = GitCommitGateway(project_root=self.worktree_path, registry=self._registry)
        return self._gateway

    # ------------------------------------------------------------------
    # 落盘主入口（drain_queue landing 协议：fn(item, queue_root) -> LandingResult）
    # ------------------------------------------------------------------
    def __call__(self, item: dict, queue_root: Path) -> cq.LandingResult:
        """__call__ implementation."""
        qid = item.get("qid", "?")
        session_id = item.get("session_id", "")
        queue_root = Path(queue_root)

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

        self.ensure_worktree()
        gateway = self._get_gateway()
        marker = queue_marker(session_id, qid)

        for attempt in range(1, self._max_cas_retries + 1):
            # 2) 同步 + 基底冲突判定
            self._sync_worktree()
            old_dev = self._dev_head()
            reason = self._conflict_reason(item, old_dev)
            if reason:
                return cq.LandingResult(ok=False, reason=reason)

            # 3) claim（净树基线）→ 快照应用 → 全门禁 commit → 释放 claim
            wt_files = [str(self.worktree_path / p) for p in sorted(self._item_paths(item))]
            claimed = gateway.claim_files(session_id, wt_files) if wt_files else []
            try:
                commit_files = self._apply_snapshot(item, queue_root)
                if not commit_files:
                    return cq.LandingResult(ok=False, reason="空快照项（无文件可落）")
                full_message = f"{item.get('message', '')}\n\n{marker}"
                # FORGED-GW-MARKER env 逃生（确为网关内部调用，与 run_git 同款 env）；
                # allow_non_worktree 见模块 docstring「门禁诚实记录」（不修改不放宽任何门禁判定）
                prev_env = os.environ.get(_GATEWAY_ENV)
                os.environ[_GATEWAY_ENV] = "1"
                try:
                    result = gateway.commit(
                        session_id,
                        commit_files,
                        full_message,
                        allow_non_worktree=True,
                    )
                finally:
                    if prev_env is None:
                        os.environ.pop(_GATEWAY_ENV, None)
                    else:
                        os.environ[_GATEWAY_ENV] = prev_env
            finally:
                if claimed:
                    gateway.release_files(session_id, claimed)

            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitStatus

            if result.status is not CommitStatus.OK:
                # 门禁阻断/git 失败 → 死信（不卡队，66 号 §4 裁定 4）；NOTHING_TO_COMMIT
                # 语义=快照与 HEAD 已一致（幂等空转）→ 视为落盘成功但无新 commit
                if result.status is CommitStatus.NOTHING_TO_COMMIT:
                    return cq.LandingResult(ok=True, landed_id=old_dev)
                return cq.LandingResult(
                    ok=False,
                    reason=f"网关落盘失败（{result.status.value}）: {result.message[:400]}",
                )

            # 4) CAS 推进 dev；失败=队列外写入者插队 → 同路径冲突死信 / 否则重试
            try:
                self._advance_dev(old_dev, result.commit_hash)
            except CasConflict:
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
                    qid, attempt, self._max_cas_retries,
                )
                continue
            logger.info("[landing] qid=%s 落盘完成 commit=%s", qid, result.commit_hash[:12])
            # 5) 主工作区受限收敛（干净文件快进/脏跳过留痕；fail-open 不改变落盘结果）
            try:
                self._converge_main_workspace(item, old_dev, result.commit_hash)
            except Exception as exc:  # noqa: BLE001 — 收敛 fail-open
                logger.warning("[landing] qid=%s 主工作区收敛异常（non-blocking）: %s", qid, exc)
            return cq.LandingResult(ok=True, landed_id=result.commit_hash)

        return cq.LandingResult(
            ok=False,
            reason=f"dev CAS 冲突重试耗尽（{self._max_cas_retries} 次）——死信回退人工",
        )


# ---------------------------------------------------------------------------
# _commit_auto 改道（66 号 §7 一处改动；flag 门控，默认 OFF——启用=Owner 窗口批准）
# ---------------------------------------------------------------------------


def bootstrap_drain_with_landing(*, queue_root=None, repo_root=None) -> dict:
    """入队后自举排空（66 号 §8：无常驻进程，拿不到 lease 放弃等下次）。

    best-effort：任何失败仅 log 不抛出——队列项已入袋即安全，排空失败等下次自举。
    测试 monkeypatch 本函数以隔离真实落盘。
    """
    try:
        root = cq.resolve_queue_root(queue_root)
        landing = WorktreeLanding(
            repo_root=Path(repo_root) if repo_root else cq._REPO_ROOT,
            queue_root=root,
        )
        return cq.try_bootstrap_drain(root, landing=landing)
    except Exception as exc:  # noqa: BLE001 — 自举失败绝不阻断改道返回（入袋即安全）
        logger.warning("[reroute] 自举排空失败（队列项安全在袋，等下次自举）: %s", exc)
        return {"skipped": True, "reason": f"bootstrap_error: {exc}"}


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
    payload: list[tuple[str, bytes]] = []
    deletes: list[str] = []
    for f in existing:
        rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
        if os.path.isfile(f):
            try:
                payload.append((rel, Path(f).read_bytes()))
            except OSError as exc:
                # fail-safe：读盘异常向上传播 → gateway 降级直提（transient 占用可自愈）
                raise RuntimeError(f"reroute 快照读盘失败: {rel}（{exc}）") from exc
        else:
            deletes.append(rel)  # 已跟踪但盘上缺失 = 删除
    head_r = gateway.run_git(["git", "rev-parse", f"refs/heads/{cq._TARGET_BRANCH}"])
    base_head = head_r.stdout.strip() if head_r.returncode == 0 else None
    # QueueReject 等入队异常向上传播 → gateway fail-safe 降级直提（warning 留痕）
    # 签名对齐 A 段定稿：可选参数束走 options=EnqueueOptions（NO-LONG-PARAM-LIST 收口）
    item = cq.enqueue_item(
        session_id,
        message,
        payload,
        options=cq.EnqueueOptions(
            base_head=base_head,
            deletes=deletes or None,
            meta_extra={"rerouted_from": "_commit_auto"},  # 审计可追溯（改道来源标记）
        ),
    )
    bootstrap_drain_with_landing(repo_root=gateway.project_root)
    qid = item["qid"]
    logger.info("[reroute] _commit_auto 改道入队: qid=%s session=%s files=%d deletes=%d",
                qid, session_id, len(payload), len(deletes))
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
