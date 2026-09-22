# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] scripts.governance.commit_queue_landing
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；scripts.commit_queue（队列协议/LandingResult）；scripts.session_worktree（环境三件套备置真源 _provision_worktree_env，延迟 import）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway（全门禁落盘执行体）；zephyr.security.access_control.session_concurrency（主仓 session registry）
# [CONSUMERS] 全部 AI session（drain_queue(landing=...) 真落盘注入点）；zephyr.gov_enforcement.rule_bridge.git_commit_gateway._commit_auto（flag ON 时 reroute 目标，延迟 import）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 永不改主工作区脏文件（66 号 §9.7 受控放松 2026-08-23：只写专用 worktree + 对象库 + dev ref CAS；landing 后主工作区受限收敛——仅当文件与旧 HEAD 逐字节一致才快进写入新内容，脏/缺失/删除冲突一律跳过留痕，零 WIP 丢失风险）；单写者（仅 Serializer lease 持有者经 drain 调用）；幂等不双落（done/landed_id + is-ancestor + 标记 grep 三重判定）；门禁一套不裁（GitCommitGateway 全门禁链零适配，worktree 形态 100 门禁天然生效）；CAS 冲突/基底冲突→死信不卡队；**瞬态环境失败（git index.lock 争用 / Windows 句柄占用致 reset --hard unlink 失败 / 全局提交锁 LOCK_TIMEOUT；特征串真源=_TRANSIENT_GIT_MARKERS）→ 抛 LandingEnvironmentError 让项退回 pending，绝不死信**；主工作区收敛 fail-open（landing 已成功，收敛异常仅留痕不改变结果）；worktree 环境备置（ensure_worktree 两出口经 scripts.session_worktree._provision_worktree_env 从主仓取 PG+CH 配置——门禁/reconciler 在 worktree 内与主区等价，不再 fail-open；备置失败仅 warning 不阻断落盘）
# [MODIFY-GUARD] 66 号备忘 §6.3 MVP 形态 + §8 幂等算法 + §9 边界；08 号文 §4.2 步骤 3/5；[GW:{sid}:{qid}] 标记格式（POST-COMMIT-GUARD / REFERENCE-TRANSACTION-GUARD 消费方）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] __call__ 永不抛普通 Exception（落盘失败→LandingResult(ok=False, reason) 进死信）；cq.LandingEnvironmentError 按设计向上逃逸（drain 捕获后项退回 pending + 终止本轮）；BaseException 向上传播（模拟进程崩溃语义，项留 processing 等回收）
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

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

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
_GIT_TIMEOUT_SECONDS = _get_threshold("git_operations.commit_queue_git_timeout_seconds", 120)  # 治本(AI-20 P0③): 从SSoT读取；与 worktree_pool.run_git 同款
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
_TRANSIENT_GIT_MARKERS = (
    "index.lock",
    "unable to create",
    "unable to unlink",
    "permission denied",
    "being used by another process",
    "the process cannot access the file",
)


def _is_transient_git_error(exc: BaseException | str) -> bool:
    """git 失败是否属瞬态环境类（锁争用/句柄占用）——是则项退回 pending，绝不死信。"""
    text = str(exc).lower()
    return any(marker in text for marker in _TRANSIENT_GIT_MARKERS)


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


def _split_registry_entries(text: str) -> tuple[dict[str | None, _RegistryFamily], str | None]:
    """YAML 文本 → {顶层 list 键: 族切分}（yaml.compose 节点行号法，原文块零重排）。

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
            hard_bound = (
                min(item_nodes[i + 1].start_mark.line, end_bound) if i + 1 < len(item_nodes) else end_bound
            )
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
                    identity=_merge_entry_identity(data),
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

    import 走 flat 路径（HEAD 既存真源）；registry_family/ 重组位落地前
    IMPORT-INTEGRITY 只认 HEAD 可解析面（0060 死因），重组后由 Lane A 批统一切换。
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


def _scalar_family_keys(fam_map: dict[str | None, _RegistryFamily]) -> set[str | None]:
    """纯标量族集合（全部条目均非 dict——schema 元数据 list 特征，如 unique_key: [id]）。

    gate 的身份语义对非 dict 条目本就跳过（fail-open 不计入身份集）；合并器同构：
    这类族不参与条目合并，passthrough 保留 ours 原样（Lane B THD-ALERT-007
    q-0001 死信实证：顶层 unique_key 元数据 list 被误判条目族致增量件死信）。
    """
    out: set[str | None] = set()
    for k, fam in fam_map.items():
        if fam.blocks and all(b.identity is None and not isinstance(b.data, dict) for b in fam.blocks):
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
) -> tuple[dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]], str | None]:
    """族内条目按身份键建索引；身份判不了/同侧键重复 → 死信方向错误串。"""
    idx: dict[str, tuple[str | None, _RegistryFamily, _RegistryEntryBlock]] = {}
    for fam_key, family in fam_map.items():
        for block in family.blocks:
            if block.identity is None:
                return {}, "存在身份判不了的条目（非 dict/首字段非标量）——合并语义不可证，死信回人工"
            if block.identity in idx:
                return {}, f"同侧身份键重复: {block.identity}——身份不唯一，死信回人工"
            idx[block.identity] = (fam_key, family, block)
    return idx, None


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
        cached = family_append_pos.get(t_fam_key)
        if cached is None:
            cached = target.blocks[-1].end + 1 if target.blocks else target.head_line + 1
        family_append_pos[t_fam_key] = cached + 1
        text = t_block.text if t_block.text.endswith("\n") else t_block.text + "\n"
        if key in base_idx:
            # base 有+ours 无+theirs 有 → 采纳，除 ours 侧合法退役
            # （判据=条目引用路径盘上与 HEAD 双不存在；判定异常=不可证 → 采纳恢复）
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
) -> str | None:
    """渲染自检（fail-closed 兜底）：结果必须可解析且身份集 == 预期（保留∪插入）。"""
    import yaml  # noqa: PLC0415

    try:
        yaml.safe_load(merged)
    except Exception as exc:  # noqa: BLE001
        return f"{rel_path}: 合并渲染自检失败（结果不可解析）: {exc}"
    got, err = _split_registry_entries(merged)
    if err:
        return f"{rel_path}: 合并渲染自检失败（重切分异常）: {err}"
    got_keys: set[str] = set()
    for fam in got.values():
        for block in fam.blocks:
            if block.identity is not None:
                got_keys.add(block.identity)
    if got_keys != (kept_keys | inserted_keys):
        return (
            f"{rel_path}: 合并渲染自检失败（身份集漂移）预期 {len(kept_keys | inserted_keys)} 条 "
            f"实际 {len(got_keys)} 条——死信回人工"
        )
    return None


def _split_all_sides(
    ours_text: str, theirs_text: str, base_text: str | None, rel_path: str
) -> tuple[
    dict[str | None, _RegistryFamily] | None,
    dict[str | None, _RegistryFamily] | None,
    dict[str | None, _RegistryFamily] | None,
    str | None,
]:
    """三侧文本各自条目族切分；任一侧解析失败 → (None, None, None, 错误串)。"""
    ours_families, err = _split_registry_entries(ours_text)
    if err:
        return None, None, None, f"{rel_path}: ours 侧 {err}"
    theirs_families, err = _split_registry_entries(theirs_text)
    if err:
        return None, None, None, f"{rel_path}: theirs(快照) 侧 {err}"
    base_families: dict[str | None, _RegistryFamily] = {}
    if base_text is not None:
        base_families, err = _split_registry_entries(base_text)
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
]:
    """三侧条目索引构建；任一侧身份判不了/键重复 → 错误串。"""
    ours_idx, err = _index_family_blocks(ours_families)
    if err:
        return None, None, None, f"{rel_path}: ours {err}"
    theirs_idx, err = _index_family_blocks(theirs_families)
    if err:
        return None, None, None, f"{rel_path}: theirs(快照) {err}"
    base_idx, err = _index_family_blocks(base_families)
    if err:
        return None, None, None, f"{rel_path}: base {err}"
    return ours_idx, theirs_idx, base_idx, None


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
    ours_families, theirs_families, base_families, err = _split_all_sides(ours_text, theirs_text, base_text, rel_path)
    if err:
        return None, err

    passthrough, err = _split_passthrough_and_drift(ours_families, theirs_families, base_families, rel_path)
    if err:
        return None, err
    for fam_map in (ours_families, theirs_families, base_families):
        for k in passthrough:
            fam_map.pop(k, None)

    ours_idx, theirs_idx, base_idx, err = _index_all_sides(ours_families, theirs_families, base_families, rel_path)
    if err:
        return None, err

    kept_splices, kept_keys, err = _plan_kept_splices(ours_idx, theirs_idx, base_idx, rel_path)
    if err:
        return None, err
    ins_splices, inserted_keys, err = _plan_insert_splices(
        theirs_idx, ours_idx, base_idx, ours_families, rel_path, retired_check
    )
    if err:
        return None, err

    # 应用 splice（start 降序；同位置的多个插入按登记顺序生效）
    splices = kept_splices + ins_splices
    lines = ours_text.splitlines(keepends=True)
    for start, end_excl, text in sorted(splices, key=lambda s: (s[0], s[1]), reverse=True):
        lines[start:end_excl] = [text] if text else []
    merged = "".join(lines)

    err = _render_selfcheck(merged, kept_keys, inserted_keys, rel_path)
    if err:
        return None, err
    return merged, ""


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
        """
        self._git_wt("reset", "--hard", f"refs/heads/{self.target_branch}")
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

    # ------------------------------------------------------------------
    # 幂等判定（66 号 §8：is-ancestor / done 记录 + 标记 grep 三重）
    # ------------------------------------------------------------------
    def _already_landed(self, item: dict) -> str | None:
        """返回已落盘 commit sha（未落盘返回 None）——重放不双落的核心。"""
        landed = item.get("landed_id") or ""
        # noop 哨兵剥前缀：快照与该 HEAD 一致的幂等空转项按已落盘跳过（防重放循环），
        # is-ancestor 用 @ 后真实 sha 判定。
        if landed.startswith(_NOOP_LANDED_PREFIX):
            landed = landed[len(_NOOP_LANDED_PREFIX):]
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

    def _conflict_reason(self, item: dict, current_dev: str) -> str | None:
        """base_head 基底冲突判定；无 base_head（A 段兼容项）→ None（快进应用）。

        W2（2026-09-22 注册表事故治本）：注册表族文件（is_registry_mergeable）不做
        path 级死信——同路径漂移交由落地侧条目级三向合并消化（同键内容异才死信）；
        此处若照旧死信，合并器永远无执行机会。非注册表路径维持逐文件快进判定零变更。
        """
        base = item.get("base_head")
        if not base or base == current_dev:
            return None
        if self._git_repo("cat-file", "-e", base, check=False).returncode != 0:
            return f"冲突判定失败：base_head 无效（{base}）——死信回退人工（66 号 §6.4）"
        paths = self._item_paths(item)
        mergeable = {p for p in paths if is_registry_mergeable(p)}
        overlap = self._changed_paths_between(base, current_dev) & (paths - mergeable)
        if overlap:
            return (
                f"冲突：入队基底 {base[:12]} 之后 dev 已推进且触及同路径 {sorted(overlap)}"
                f"——逐文件快进判定失败，死信回退属主会话（66 号 §6.4/§9.1）"
            )
        return None

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

    def _registry_entry_retired(self, entry: object) -> bool:
        """ours 侧合法退役判定（W2 规则 b 例外项）：条目引用路径盘上与 HEAD 双不存在。

        判据真源=DISPATCH_v1 Lane A 卡片 W2「该条目文件路径盘上与 HEAD 双不存在」；
        条目无路径候选 / 任一路径存活 → 非合法退役（采纳恢复，宁可多救不可漏救——
        被救回的多余条目由属主会话按正规删除通道二次移除，方向安全）。
        """
        paths = _extract_entry_paths(entry)
        if not paths:
            return False
        head = self._dev_head()
        for p in paths:
            if (self.repo_root / p).exists():
                return False
            r = self._git_repo("cat-file", "-e", f"{head}:{p}", check=False)
            if r.returncode == 0:
                return False
        return True

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
            return theirs_bytes  # dev 侧无此文件（新增落地）→ 无合并语义
        if ours_text == theirs_text:
            return None  # 快照与 dev 一致 → 零合并零提交（幂等 noop）
        base_sha = item.get("base_head") or ""
        if not base_sha or self._git_repo("cat-file", "-e", base_sha, check=False).returncode != 0:
            parent = self._git_repo("rev-parse", "--verify", f"{old_dev}^", check=False)
            base_sha = parent.stdout.strip() if parent.returncode == 0 else ""
        base_text = self._read_blob_text_opt(base_sha, rel) if base_sha else None
        merged, conflict = three_way_merge_registry_yaml(
            base_text,
            ours_text,
            theirs_text,
            rel_path=rel,
            retired_check=self._registry_entry_retired,
        )
        if conflict:
            raise RuntimeError(f"[landing] 注册表三向合并失败（死信回退人工）: {conflict}")
        if merged == ours_text:
            return None  # 合并未给 dev 带来任何变化（快照侧新增全被退役判定吸收等）
        return merged.encode("utf-8")

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
            if is_registry_mergeable(rel):
                # W2 治本（2026-09-22 注册表事故）：注册表族不做整文件覆盖——
                # fb5a7821d 陈旧快照 blob 一写抹掉 103 条已提交身份的病灶在此封死。
                content = self._merge_registry_file(item, rel, content, old_dev)
                if content is None:
                    continue  # 合并结果与 dev 一致 → noop，不写盘不进提交清单

            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_bytes(content)
            wt_files.append(str(abs_path))
        return wt_files

    # ------------------------------------------------------------------
    # dev CAS 推进（66 号 §6.3 修正 4：带上期望旧值，单写者免费保险）
    # ------------------------------------------------------------------
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
                type(exc).__name__, exc, exc_info=True,
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

    def _refresh_integrity_baseline_main_repo(self, item: dict) -> str:
        """落地成功后在主仓补跑 integrity 基线注册（fail-open，返回空=成功）。

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

        try:
            self.ensure_worktree()
            gateway = self._get_gateway()
        except cq.LandingEnvironmentError:
            raise
        except Exception as exc:  # noqa: BLE001 — 环境失败≠物品失败：转专类供 drain 终止整轮不死信（2026-09-10 死信事故治本）
            raise cq.LandingEnvironmentError(
                f"landing 环境不可用（repo_root={self.repo_root}）: {type(exc).__name__}: {exc}"
            ) from exc
        marker = queue_marker(session_id, qid)

        for attempt in range(1, self._max_cas_retries + 1):
            # 2) 同步 + 基底冲突判定
            try:
                self._sync_worktree()
            except cq.LandingEnvironmentError:
                raise
            except RuntimeError as exc:
                # 瞬态 git 环境失败（索引锁争用 / Windows 句柄占用）≠ 物品失败——高并发期
                # 他会话 commit 持主仓/worktree 索引锁是常态（2026-09-10 二阶死信：
                # worktree 修复后 26 项死于 reset --hard 撞锁）；同族还有 Windows 下
                # 外部进程开着文件句柄导致 reset --hard unlink 失败（2026-09-16
                # q-…-0018 实证："unable to unlink old '…business_data_categories.yaml':
                # Invalid argument"）。转环境专类 → 项退回 pending、整轮终止等下次自举，
                # 绝不死信（特征串单一真源=_TRANSIENT_GIT_MARKERS）。
                if _is_transient_git_error(exc):
                    raise cq.LandingEnvironmentError(f"git 瞬态环境失败，项退回 pending 等下次自举: {exc}") from exc
                raise
            old_dev = self._dev_head()
            reason = self._conflict_reason(item, old_dev)
            if reason:
                return cq.LandingResult(ok=False, reason=reason)

            # 3) claim（净树基线）→ 快照应用 → 全门禁 commit → 释放 claim
            wt_files = [str(self.worktree_path / p) for p in sorted(self._item_paths(item))]
            claimed = gateway.claim_files(session_id, wt_files) if wt_files else []
            try:
                commit_files = self._apply_snapshot(item, queue_root, old_dev)
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
                            "[landing] qid=%s pathspec 丢 staging 自愈：重放 apply+prestage 后重试 commit", qid,
                        )
                        commit_files = self._apply_snapshot(item, queue_root, old_dev)
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
                raise cq.LandingEnvironmentError(
                    f"全局提交锁争用（等待 {self._lock_wait_seconds:g}s 仍未得），项退回 pending 等下次自举: "
                    f"{(result.message or '')[:400]}"
                )

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
                    return cq.LandingResult(
                        ok=True, landed_id=f"{_NOOP_LANDED_PREFIX}{old_dev}"
                    )
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
            try:
                reg_note = self._refresh_integrity_baseline_main_repo(item)
                if reg_note:
                    logger.warning("[landing] qid=%s 主仓基线注册失败（non-blocking）: %s", qid, reg_note)
            except Exception as exc:  # noqa: BLE001 — 注册 fail-open
                logger.warning("[landing] qid=%s 主仓基线注册异常（non-blocking）: %s", qid, exc)
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
    payload, deletes, skipped_protected = split_auto_commit_snapshot(
        existing, str(gateway.project_root)
    )
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
            meta_extra={"rerouted_from": "_commit_auto", "lane": "machine"},  # 审计可追溯（改道来源标记；P1-D 车道让路交互提交）
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
