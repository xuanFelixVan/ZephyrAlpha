# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §
# [MODULE] scripts.commit_queue
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；zephyr.shared.infra.process_pool.is_pid_alive（僵尸 PID 检测真源唯一）
# [CONSUMERS] 全部 AI session（提交入队唯一入口）；B 段 Serializer 落盘执行体（专用 worktree 真落盘）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 单写者（serializer.lease 唯一持有者排空）；纯 FIFO（qid 单调序，无优先级插队）；快照入袋即安全（blob 落盘即完成）；死信不卡队；同键 (session_id,path) pending 内仅留最新；永不改主工作区文件
# [MODIFY-GUARD] 66 号备忘 §6 协议/schema 真源；08 号文 §4.2 Phase 0；CLI 子命令面（enqueue/status/drain）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功（含 drain 拿不到 lease 跳过）; exit 1=参数/IO 错误（含 requeue 取回失败）; exit 2=入队轻检拒绝(DENIED)
# [TESTS] tests/governance/test_commit_queue.py
# [A_module] module_id=MOD-GOV-046 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 AI/CI 按需调用的 CLI 协调工具（入队自举排空，无常驻进程），与 lock_files.py/task_board.py 同类
"""commit_queue.py — 提交队列串行化 MVP（A 段：队列协议 + CLI + Serializer 自举排空 + 死信 + compaction）

真源
----
- 66 号备忘 §6（入队 schema / compaction / Serializer 主循环 / 冲突判定）、§8（入队自举
  排空形态 + lease 算法 + 幂等恢复）、§9（不做什么：单写者/纯 FIFO/死信回退给人/永不改
  主工作区）、§10（MVP 验收口径）、§11（红队测试清单）。
- 08 号文 §4.2 Phase 0 步骤 0/1/2/4（A 段范围）；步骤 3（专用 worktree 真落盘）与步骤 5
  （_commit_auto 改道）属 B 段，不在本文件。

核心语义（66 号 §4 裁定 1/2）
------------------------------
- 会话提交 = 快照入队即返回：文件**完整内容**（非 diff）按内容寻址落 blobs/（sha256 命名
  天然去重），队列项 JSON 落 pending/（O_EXCL 原子创建）——快照入袋即完成，工作区后续
  被 restore/清空不影响本项。
- 落盘由单写者 Serializer 按 FIFO（qid 单调序）完成；本 A 段落盘为**接口桩**
  （landing callable 注入点，默认实现仅标记 done 不真提交）——队列语义（零丢失/FIFO/
  死信/compaction）本段钉死，真 git 落盘 B 段接专用 worktree + GitCommitGateway 全门禁。

与 66 号 §6.1 schema 的刻意出入（回执报备）
------------------------------------------
1. 队列项用 JSON（{qid}.json）而非 YAML——stdlib 零依赖 + 原子写简单；字段集与 66 号
   §6.1 对齐（qid/session_id/created_at/branch/base_head/files[{path,blob_sha256,
   blob_ref,base_blob,action}]/message/meta{depends_on,supersedes}）。
2. message 内联于队列项 JSON（66 号为 message_file 指针）——A 段落盘为桩无消费方，
   B 段接通时可落 message_file；CLI 保留 --message-file 读入（PowerShell 中文编码教训，
   66 号 §6.3 修正 3）。
3. base_head/base_blob A 段不主动取 git（零 git 依赖，测试可全 tmp 隔离）——CLI 提供
   --base-head 显式传入；B 段落盘接通时由 enqueue 增强或 drain 端填充。
4. lease 文件落 .runtime/commit_queue/serializer.lease（任务指定，与队列同目录共命运）；
   66 号 §8 原文为 .ailocks/commit_serializer.lock——语义同款（O_EXCL+TTL+僵尸 PID）。

目录协议（运行时创建；.runtime/ 已整体 gitignore）
--------------------------------------------------
.runtime/commit_queue/
  pending/      待处理队列项（q-*.json，O_EXCL 原子创建）
  processing/   Serializer 取走处理中（原子 rename 进入；崩溃留孤儿，下次自举回收）
  done/         已落盘（含 landed_at/landed_id）
  dead/         死信（含 dead_reason/dead_at；永不自动清理，66 号 §8）
  blobs/        内容寻址快照（sha256 命名，tmp+os.replace 原子写）
  {session_id}.seq  会话内单调序号（qid 组成部分；唯一性最终由 O_EXCL 保证）
  serializer.lease  Serializer 租约（TTL=300s + 僵尸 PID 检测）

入队轻检（66 号 §6.5 + §11 #3 红队口径，全部 fail-closed 报错非静默）
--------------------------------------------------------------------
- 路径穿越：.. 段 / 绝对路径（盘符、UNC、/ 开头）/ ~ 开头 / 反斜杠 / NUL
- .git 路径：首段为 .git 一律拒绝
- 密钥路径：常见密钥文件名黑名单（.env*/*.pem/*.key/*.pfx/id_rsa* 等，66 号 §6.5 pathspec 白名单）
- 超大 blob：单文件 > 10MB 拒绝（66 号 §6.1 大小约束，§12 Q3 已闭环：超限走人工）
- 空 message：strip 后为空拒绝

故障与恢复（66 号 §8）
----------------------
- Serializer 无常驻进程：enqueue/status/drain 成功写队后尝试拿 lease 排空，拿不到就放弃
  等下次自举；崩溃则下一个入队者/任意 status 调用续排空。
- drain 中途崩溃 → processing/ 孤儿项：下次拿 lease 后先原子回收重入 pending 续跑——
  不得双落（done/ 按 qid 唯一）不得丢失（每项终有 pending/processing/done/dead 其一）。
  A 段默认 landing 桩无副作用天然幂等；B 段真落盘时幂等判定（git merge-base
  --is-ancestor / done/ 记录，66 号 §8）在 landing 实现内完成。
- landing 抛普通 Exception = 单项处理失败 → 死信（不卡队，后续项继续）；
  BaseException（KeyboardInterrupt/SystemExit 等，含测试崩溃注入）不捕获向上传播——
  当前项留 processing 等回收，模拟真实进程崩溃语义。

CLI
---
  python scripts/commit_queue.py enqueue --session S --files a.py,b.py --message "msg"
      [--message-file F] [--worktree-root DIR] [--base-head SHA] [--depends-on qid1,qid2]
      [--queue-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py status [--session S] [--queue-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py drain [--queue-root DIR] [--max-items N]
  python scripts/commit_queue.py requeue <qid> [--worktree-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py cleanup [--done-ttl-days N]
  python scripts/commit_queue.py health [--no-alert]

B 段接口预留点（2026-08-21 B 段已接通）
--------------------------------------
- landing callable：drain_queue(queue_root, landing=fn)，fn(item: dict, queue_root: Path)
  -> LandingResult(ok, reason, landed_id)。**B 段真落盘实现已落
  scripts/governance/commit_queue_landing.py（MOD-GOV-047）**：专用 worktree
  （<queue_root>/worktree）+ GitCommitGateway 全门禁零适配 + `[GW:{sid}:{qid}]` 标记
  （POST-COMMIT-GUARD / REFERENCE-TRANSACTION-GUARD `[GW:` 子串匹配兼容）+
  is-ancestor/标记 grep 幂等 + dev update-ref CAS 推进。
- flag 接入：config/flags.yaml `commit_queue_serializer`（出厂默认 enabled:false=
  ALWAYS_OFF）。【2026-08-22 Owner 裁定翻开，当前 enabled:true，已运行 8 天】；
  ON 时 _commit_auto 改道 enqueue（git_commit_gateway 内一处改动，66 号 §7）。
- task_board 联动（P1 已落地 2026-08-28）：死信时若队列项 meta.task_id 存在，
  经 _notify_task_board_dead_letter → scripts.task_board.tag_dead_letter 把
  {qid, reason, owner, tagged_at} 写入 task_board metadata_json.deadletter
  （66 号 §6.4，无需改表）；任务不存在/已完成/板不可达仅记日志不阻断排空。
- P1 队列联动三件套（2026-08-29 已落地，08 号文 §4.3 ↔ 66 号 §10 P1 行）：
  ①级联标记——项 X 成功落盘后扫描 pending，meta.depends_on 含 X.qid 或 base_head
  与 X 相同（base_head 经由 X）的后续项标 stale；stale 项排到队首时重校验基底
  （base_blob vs 当前 HEAD，head_reader 注入比对），仍适用→清标放行，不适用→
  降死信候选（dead_reason=cascade_stale，不消耗 landing）；
  ②死信重新入队 CLI——requeue 从 dead/ 取回，基于当前工作区文件内容重建快照
  重新入队（新 qid 排 FIFO 队尾，原死信项留 dead/ 追加 requeued 标注留痕，
  task_board 死信标签同步标注 requeued 不解除）；
  ③done/ TTL 清理——默认 7 天可配置，drain 收尾在 lease 内自动执行；
  dead/ 永不自动清理不变量不变（66 号 §8）。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 提交队列串行化 MVP（enqueue/status/drain/requeue/cleanup/health + 入队自举排空 + 死信 + compaction + 级联标记 + done/ TTL 清理 + 死信积压告警）
dimensions:
- D1
priority: P0
timeout_seconds: 120
warn_only: false
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# --- sys.path 引导（CLI 独立运行时 src 不在 sys.path；pytest 下已由项目配置提供）---
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
# repo 根同样入 path（2026-09-11 修正 53fa0b431a 残留）：scripts/ 是常规包，直跑场景
# （sys.path[0]=scripts/，repo 根不在 path）下 `from scripts.X import` 需要根在 path，
# 且必须位于 pywin32.pth 注入的 site-packages/win32 之前——该目录含裸 `scripts` 命名
# 空间部分，会遮蔽本仓真实包（详见 _purge_poisoned_scripts_package）。
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# 僵尸 PID 检测真源唯一（红蓝对抗归一，禁止内联复制——process_pool.py docstring 原话）
from zephyr.shared.infra.process_pool import is_pid_alive  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量（真源逐条注释）
# ---------------------------------------------------------------------------
QUEUE_ENV_VAR = "ZEPHYR_COMMIT_QUEUE_DIR"  # 测试/多仓隔离覆盖位（先例：ZEPHYR_TASK_BOARD_DB）
_QUEUE_DIR_DEFAULT = ".runtime/commit_queue"  # 66 号 §2.4 #13 / 08 号文 §2.4 E
_STATES = ("pending", "processing", "done", "dead")  # 四态目录（66 号 §5 架构图）

_LEASE_FILE = "serializer.lease"  # 独立文件锁，不共用网关 _GlobalCommitLock（任务口径）
_LEASE_TTL_SECONDS = 300  # 66 号 §8：Serializer 排空一批通常 <30s，5 分钟足够
_LEASE_TIMEOUT_SECONDS = 5.0  # 66 号 §8：自举模式不等待——拿不到就放弃
_LEASE_POLL_INTERVAL = 0.1  # 与 _GlobalCommitLock._POLL_INTERVAL 同款
# R2 大批硬顶（st-commitchain-20260922，数据驱动）：done 项文件数 p50=3、p90=110
# （0921 workclean 111 文件巨批实测磨 116 分钟死在终点 CREATE-GUARD）——交互车道
# 单批超限拒绝+拆批指引，失败早暴露不互相拖累；machine 车道与显式逃生旗豁免。
_MAX_BATCH_FILES = 40
# D7 单项墙钟挂账阈值：单项 landing 超此秒数写堵点本（kind=slow_item）——大注册表批
# 从无声变有账（环节2 E4；遥测口径：单项均值 79s/P90 189s，300s=显著越界）。
_SLOW_ITEM_LEDGER_SECONDS = 300

_MAX_BLOB_BYTES = 10 * 1024 * 1024  # 66 号 §6.1 大小约束（§12 Q3 已闭环：单 blob 上限 10MB，超限拒绝走人工）
_TARGET_BRANCH = "dev"  # 66 号 §9.5：v0.1 仅 dev 主干单目标（不支持跨分支队列）
_SEQ_PAD = 4  # 66 号 §6.1：seq:04d 零填充——qid 字典序 == 数值序，保 FIFO 排序机械性

_READ_RETRY_TIMES = 20  # drain 读 pending 项容忍写入窗口：重试次数（见 _read_item 注释）
_READ_RETRY_INTERVAL = 0.05  # 重试间隔 50ms × 20 = 1s 上限

_DONE_TTL_DAYS_DEFAULT = 7.0  # 66 号 §12 Q3 已闭环：done 保留 7 天 TTL；dead 永不自动清理

# ---------------------------------------------------------------------------
# F2 前置②（2026-09-18 st-flashspeed，判据书 F2「前置（机读）」行）：跨域热文件
# 单通道闸——域映射配置在案。S18-R3 签署后 k=4 分区通道的 drain 按域取队 MUST 咨
# 询本路由：不变量=任一通道键任一时间点活跃 lease≤1（机读判据「lease 双写者窗口
# =0」的落地基础）；热文件（注册表族/ROOR/AGENTS.md/standards.yaml）强制单一热
# 通道跨域串行，杜绝多通道并发写注册表的 CAS 风暴。k=1 现状 drain 不咨询本路由
# ——纯函数零行为变化，「闸在案」=配置+不变量+测试三件齐；主体通道池待 Owner 签。
# ---------------------------------------------------------------------------
HOT_CHANNEL_KEY = "hot"  # 热文件单一热通道（判据书 F2 前置：注册表/ROOR/AGENTS.md/standards.yaml）
MIXED_CHANNEL_KEY = "shared"  # 跨域混合项兜底单通道（防跨域项撕裂多通道产生额外竞态面）
_HOT_PATH_MARKERS = (
    "docs/01_policies_and_standards/_registry/",  # 注册表族（capability/module/rule catalogs 等）
    "docs/registry_of_registries.yaml",  # ROOR（注册表发现唯一真源）
    "AGENTS.md",  # 宪法 L0
    "standards.yaml",  # 标准真源
)


def channel_key_for_files(files: list[str]) -> str:
    """队列项文件清单 → 通道路由键（F2 k=4 域映射配置；判据「同域冲突率不升」基础）。

    规则（优先级降序）：
    1. 含热文件（_HOT_PATH_MARKERS 任一命中）→ HOT_CHANNEL_KEY（单一热通道跨域串行）；
    2. 全部文件同域 → 域键（src/zephyr/<域> 三级；其余=顶级目录）；
    3. 跨域混合 → MIXED_CHANNEL_KEY（兜底单通道）。
    不变量：同域同文件的双队列项必得同键（=同通道串行）——「同域同文件双通道并发」
    压测的并发安全前提；lease O_EXCL 在通道内物化单写者。
    """
    norm = [str(f).replace("\\", "/") for f in files]
    if any(marker in f for f in norm for marker in _HOT_PATH_MARKERS):
        return HOT_CHANNEL_KEY
    domains: set[str] = set()
    for f in norm:
        parts = [p for p in f.split("/") if p]
        if not parts:
            domains.add("/")
        elif parts[0] == "src" and len(parts) > 2:
            domains.add("/".join(parts[:3]))  # src/zephyr/<域>
        else:
            domains.add(parts[0])
    if len(domains) == 1:
        return domains.pop()
    return MIXED_CHANNEL_KEY


# 死信积压告警（2026-09-11 死信率告警最小落地，st-perf-plan-20260910）：
# 阈值唯一真源=alert_threshold_registry.yaml（REG-ATH-001）THD-ALERT-003（积压项数）
# /THD-ALERT-004（告警冷却窗口）；告警通道=task_board 专 task 死信标签（66 号 §6.4 同款）。
_DEADLETTER_WATCH_TASK_ID = "T-QUEUE-DEADLETTER"  # 告警挂载点固定 task id（幂等自建）
_HEALTH_ALERT_STATE_FILE = "health_alert_state.json"  # 冷却状态（队列根下，共命运）

# 死因三分类标记（与 .runtime/tmp/commit_queue_dead_triage_20260910.md 口径一致）：
# env=环境性失败（物品无辜，可 requeue）；item=门禁/冲突物品性失败（gate 语义正常）。
_DEAD_REASON_ENV_MARKERS = (
    "pytest_50136",
    "pytest_19944",
    "rev-parse --show-toplevel",
    "index.lock",
    "Unable to create",
    "Author identity unknown",
    "LandingEnvironmentError",
    "瞬态锁争用",
    # LOCK_TIMEOUT 归 env（2026-09-16 q-…-0009/0010/0011 实证）：内容合法，仅因他会话
    # 正持全局提交锁而死信——瞬态争用，requeue 即愈。classify_dead_reason 先查 env 标记，
    # 故 "网关落盘失败（LOCK_TIMEOUT）" 这类混合串也会正确归 env（落地侧现已转
    # LandingEnvironmentError 让项退回 pending，此标记只兜历史/直连路径的死信）。
    "LOCK_TIMEOUT",
    # Windows 文件句柄占用同归 env（2026-09-16 q-…-0018 实证：reset --hard 撞
    # "unable to unlink old '…business_data_categories.yaml': Invalid argument"，
    # 13 文件合法批次被误判物品失败）。落地侧特征串真源=
    # commit_queue_landing._TRANSIENT_GIT_MARKERS（现已转 LandingEnvironmentError），
    # 此处只兜历史/直连路径；刻意不收裸 "Invalid argument"（太宽，真 bug 也报它）。
    "unable to unlink",
    "Permission denied",
    "being used by another process",
    "The process cannot access the file",
    "瞬态环境失败",
    # env 盲区补盲（st-commitchain-20260922，0921/0922 死信 18 项落 other 实证）：
    # Windows 中文形态 PermissionError 与 WinError 码不在原标记表，物品无辜却被
    # 归 other 无人 requeue——逐串补齐（0921 WinError5×9 + WinError206 文件名过长×2）。
    "拒绝访问",
    "WinError 5",
    "WinError 206",
    "文件名或扩展名太长",
)
_DEAD_REASON_ITEM_MARKERS = (
    "PROTECTED-PATHS",
    "CAS 竞态",
    "CAS 冲突",
    "快进判定失败",
    "SESSION-REQUIRED",
    "CLAIM_REQUIRED",
    "COMMIT_SCOPE",
    "cascade_stale",
    "基底重校验",
    "TRACKED-DRIFT-READONLY",
    "网关落盘失败",
)

# session_id 字符白名单：session_id 进入 qid 与 seq 文件名，必须防路径注入
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

# qid 格式白名单：requeue 的 qid 入参直接拼 dead/ 文件路径，必须防路径穿越
# （对齐 _make_qid：q-{date:%Y%m%d}-{session_id}-{seq:04d}，碰撞重试 seq 可超 4 位）
_QID_RE = re.compile(r"^q-\d{8}-[A-Za-z0-9._-]{1,64}-\d{4,}$")

# 密钥文件名黑名单（66 号 §6.5 pathspec 白名单：禁止 .git/密钥路径入队）
_SECRET_NAME_RE = re.compile(
    r"^(\.env(\..*)?|.*\.(pem|key|pfx|p12|keystore|jks)|id_rsa.*|id_ed25519.*|credentials(\..*)?)$",
    re.IGNORECASE,
)


class QueueReject(ValueError):
    """入队轻检拒绝（fail-closed：报错非静默，CLI 映射 exit 2 DENIED）。"""


class LeaseUnavailable(RuntimeError):
    """Serializer lease 被活体持有（自举模式：放弃等下次，非错误）。"""


class RequeueError(RuntimeError):
    """死信取回重入队失败（qid 不在 dead/、qid 非法、工作区文件缺失等——CLI 映射 exit 1）。

    details : 结构化敏感面（MSG-EXPOSURE §5.99.20 口径：路径/凭证等进 details，
        消息文本只留人类可读摘要——5.99.20 治本落地的异常契约补全）。
    """

    def __init__(self, msg: str, details: dict | None = None) -> None:
        super().__init__(msg)
        self.details = details or {}


class LandingEnvironmentError(RuntimeError):
    """landing 运行环境不可用（2026-09-10 死信事故治本）。

    与"物品失败"严格区分：landing 自身的 repo/worktree 不可用（如 rev-parse
    rc=128）= 环境失败 → drain 终止整轮、当前项退回 pending、**绝不死信**；
    物品失败（CAS 冲突/门禁阻断/快照损坏）= 死信不卡队（66 号 §4 裁定 4）。

    事故背景：pytest 污染进程（repo_root=已删除临时仓）自举 drain 真实队列，
    851 项真实物品被环境失败误标死信（dead_reason 全带 pytest_50136 路径）。
    """


@dataclass
class LandingResult:
    """landing callable 返回协议（B 段真落盘实现的契约）。

    ok=False → 项进 dead/ 附 reason；landed_id 预留 B 段回填 commit hash。
    """

    ok: bool
    reason: str = ""
    landed_id: str = ""


# landing callable 类型：fn(队列项 dict, queue_root) -> LandingResult
# B 段接专用 worktree 真落盘（08 号文 §4.2 步骤 3，GitCommitGateway 全门禁零适配）。


def default_landing_stub(item: dict, queue_root: Path) -> LandingResult:
    """A 段默认落盘桩：仅标记 done 不真提交。

    队列语义（零丢失/FIFO/死信）本段钉死；真 git 落盘 B 段接专用 worktree
    （.aidrafts/serializer/）+ GitCommitGateway 全门禁链（66 号 §6.3 MVP 形态）。
    """
    logger.info("[landing-stub] qid=%s 仅标记 done（B 段接专用 worktree 真落盘）", item.get("qid"))
    return LandingResult(ok=True, landed_id=f"stub:{item.get('qid', '')}")


# ---------------------------------------------------------------------------
# 路径与基础工具
# ---------------------------------------------------------------------------


def resolve_queue_root(queue_root: str | os.PathLike | None = None) -> Path:
    """队列根解析序：显式参数 > 环境变量 > 仓库默认 .runtime/commit_queue。

    默认锚 __file__ 派生的仓库根（scripts/ 上一级）——与 task_board 锚主仓同理，
    本队列是跨 worktree 协调设施，MUST 全会话共享同一目录。
    P0-C 测试隔离治本（st-commitspeed-20260916，2026-09-16）：pytest 运行态下
    禁止回退生产根——历史 735 条死信系测试无 queue_root 落生产队列所致
    （dead_reason 含 .runtime/tmp/pytest_* 路径，已隔离转运 .runtime/quarantine/
    dead_test_pollution_20260916/）。测试 MUST 显式传 queue_root 或设
    ZEPHYR_COMMIT_QUEUE_DIR；确需测默认解析本体的用例 monkeypatch PYTEST_CURRENT_TEST。
    """
    if queue_root is not None:
        return Path(queue_root)
    env = os.environ.get(QUEUE_ENV_VAR)
    if env:
        return Path(env)
    if os.environ.get("PYTEST_CURRENT_TEST"):
        raise RuntimeError(
            "P0-C 测试隔离：pytest 运行态禁止解析到生产队列根——"
            "测试 MUST 显式传 queue_root=tmp_path/... 或 setenv "
            f"{QUEUE_ENV_VAR}（历史 735 条测试污染死信治本）"
        )
    return _REPO_ROOT / _QUEUE_DIR_DEFAULT


def _ensure_dirs(queue_root: Path) -> None:
    """运行时创建队列目录协议（pending/processing/done/dead/blobs）。"""
    for d in (*_STATES, "blobs"):
        (queue_root / d).mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: bytes) -> None:
    """tmp + flush/fsync + os.replace 原子写（RULE-ONE 同款模式，对标 lock_files.py）。"""
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}-{threading.get_ident()}")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _retry_transient(fn, times: int = 5, interval: float = 0.02):
    """Windows 瞬态文件占用（PermissionError）重试。

    竞态真源：enqueue 的 O_EXCL 创建后单 write 窗口内文件被持有句柄，并发 drain 的
    rename/compaction 的 replace 撞上即 WinError 32（PermissionError）。窗口极短
    （毫秒级），短暂重试即可收敛；FileNotFoundError 属语义性消失（对方已完成移动/
    删除），由调用方按语义处理，不在此重试。
    """
    for attempt in range(times):
        try:
            return fn()
        except PermissionError:
            if attempt == times - 1:
                raise
            threading.Event().wait(interval * (attempt + 1))
    return None  # pragma: no cover - 防御性（循环必 return 或 raise）


def _now_iso() -> str:
    """本地时区 ISO8601 秒级（66 号 §6.1 示例：2026-08-12T21:30:00+08:00）。"""
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# 入队轻检（66 号 §6.5 + §11 #3 红队口径——畸形项全拦，报错非静默）
# ---------------------------------------------------------------------------


def _validate_session_id(session_id: str) -> None:
    if not session_id or not _SESSION_ID_RE.match(session_id):
        raise QueueReject(
            f"非法 session_id: {session_id!r}（白名单 [A-Za-z0-9._-] 且 ≤64 字符；"
            f"session_id 进入 qid/seq 文件名，必须防路径注入）"
        )


def _validate_relpath(path: str) -> str:
    """仓内相对路径校验，返回归一化正斜杠形式。

    红队向量（66 号 §11 #3）：路径穿越（../、绝对路径、~）/.git 路径/密钥路径。
    """
    if not path or not path.strip():
        raise QueueReject("空路径拒绝入队")
    if "\x00" in path:
        raise QueueReject(f"路径含 NUL 字符: {path!r}")
    if "\\" in path:
        raise QueueReject(f"路径必须正斜杠（拒绝反斜杠）: {path!r}")
    if path.startswith("~"):
        raise QueueReject(f"路径穿越（~ 开头）: {path!r}")
    if path.startswith("/") or path.startswith("//"):
        raise QueueReject(f"绝对路径（/ 或 UNC 开头）拒绝: {path!r}")
    if re.match(r"^[A-Za-z]:", path):
        raise QueueReject(f"绝对路径（盘符）拒绝: {path!r}")
    parts = path.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise QueueReject(f"路径穿越（含空段/./..）拒绝: {path!r}")
    if parts[0] == ".git":
        raise QueueReject(f".git 路径禁止入队（66 号 §6.5 pathspec 白名单）: {path!r}")
    if _SECRET_NAME_RE.match(parts[-1]):
        raise QueueReject(f"密钥路径禁止入队（66 号 §6.5 pathspec 白名单）: {path!r}")
    return path


def _validate_message(message: str) -> str:
    msg = (message or "").strip()
    if not msg:
        raise QueueReject("空 message 拒绝入队（66 号 §11 #3 红队口径）")
    return msg


def _validate_blob_size(path: str, content: bytes) -> None:
    if len(content) > _MAX_BLOB_BYTES:
        raise QueueReject(
            f"超大 blob 拒绝入队: {path} = {len(content)} 字节 > 上限 {_MAX_BLOB_BYTES}"
            f"（66 号 §6.1：单 blob 10MB 上限，超限走人工）"
        )


# ---------------------------------------------------------------------------
# blob 内容寻址存储（66 号 §6.1 v0.4.0：tmp 写入 + os.replace；sha 命名天然去重）
# ---------------------------------------------------------------------------


def _store_blob(queue_root: Path, content: bytes) -> str:
    sha = hashlib.sha256(content).hexdigest()
    blob_path = queue_root / "blobs" / sha
    if not blob_path.exists():  # 内容寻址天然去重——同内容不重复存储
        _atomic_write(blob_path, content)
    return sha


# ---------------------------------------------------------------------------
# qid / seq（66 号 §6.1 v0.4.0：q-{date}-{session_id}-{seq:04d}，O_EXCL 原子创建，
# 碰撞重试 seq+1；seq 文件是 hint，唯一性最终由 O_EXCL 保证）
# ---------------------------------------------------------------------------

# 同进程内每会话 enqueue 串行点（66 号 §6.2：compaction 序列需在 session seq 锁内完成）；
# 跨进程同会话并发由 pending O_EXCL + 原子 rename 兜底（竞态分析见 enqueue_item docstring）。
_session_locks: dict[str, threading.Lock] = {}
_session_locks_guard = threading.Lock()


def _get_session_lock(session_id: str) -> threading.Lock:
    with _session_locks_guard:
        lock = _session_locks.get(session_id)
        if lock is None:
            lock = threading.Lock()
            _session_locks[session_id] = lock
        return lock


def _read_seq(queue_root: Path, session_id: str) -> int:
    seq_file = queue_root / f"{session_id}.seq"
    try:
        return int(seq_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def _write_seq(queue_root: Path, session_id: str, seq: int) -> None:
    _atomic_write(queue_root / f"{session_id}.seq", f"{seq}\n".encode())


def _make_qid(session_id: str, seq: int) -> str:
    date = datetime.now().strftime("%Y%m%d")
    return f"q-{date}-{session_id}-{seq:0{_SEQ_PAD}d}"


def _create_item_excl(path: Path, payload: bytes) -> None:
    """os.open(O_CREAT|O_EXCL) 原子创建队列项（66 号 §6.1 v0.4.0 文件创建原子性）。"""
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------
# compaction（66 号 §6.2：键=(session_id,path)，pending 内同键仅留最新，整体覆盖）
# ---------------------------------------------------------------------------


def _compact_pending(queue_root: Path, session_id: str, new_paths: set[str]) -> list[str]:
    """同键覆盖：移除 pending 中被新项覆盖的同会话旧项/旧条目，返回 supersedes 链。

    调用时机：新项落盘**之前**（会话锁内）——故无需排除新项自身。
    语义（66 号 §6.2 + §4 裁定 2）：快照是完整内容非增量补丁，替换=最终态正确；
    仅作用 pending（done/dead/processing 不参与）；跨会话同文件不覆盖（键不同）。
    supersedes 传递累积：被整体移除项自身的 supersedes 并入返回值——覆盖全链可追溯
    （如 v3 覆盖 v2、v2 曾覆盖 v1 → v3.supersedes=[q2,q1]），供死信回溯/审计。
    竞态安全：与 drain 并发时——drain 用原子 rename 取项，本函数对已不在 pending 的项
    收到 FileNotFoundError 即跳过（说明已被 drain 取走，不参与 pending compaction，
    语义正确）；部分覆盖写回走 tmp+os.replace 原子替换，读者（drain）只见完整旧版或
    完整新版；Windows 瞬态占用（enqueue 写入窗口）经 _retry_transient 收敛。
    """
    superseded: list[str] = []
    pending_dir = queue_root / "pending"
    for candidate in sorted(pending_dir.glob("q-*.json")):
        try:
            item = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # 写入窗口或损坏——跳过不碰（读者容错，见 _read_item）
        if item.get("session_id") != session_id:
            continue  # 跨会话同文件不产生覆盖（键不同，66 号 §6.2）
        files = item.get("files") or []
        overlapped = [f for f in files if f.get("path") in new_paths]
        if not overlapped:
            continue
        remaining = [f for f in files if f.get("path") not in new_paths]
        old_qid = item.get("qid", candidate.stem)
        if not remaining:
            # 整体覆盖：旧项所有 path 均被新项包含 → 移除旧项（其内容必然已被
            # 新快照包含，66 号 §4 裁定 2 审查论证）；supersedes 关系记在新项 meta。
            try:
                _retry_transient(lambda: os.remove(candidate))
                superseded.append(old_qid)
                # 传递累积：被移除项自身覆盖过的更旧项一并入链（审计可追溯）
                superseded.extend(item.get("meta", {}).get("supersedes") or [])
            except (FileNotFoundError, PermissionError):
                pass  # 已被 drain 并发取走/正在其操作窗口——正确语义，跳过
        else:
            # 部分覆盖：旧项缩减为未被覆盖的 path 集合，原子写回。
            # 不记 compacted_by=<新qid>——本函数在新项落盘前调用，新 qid 此时尚未分配；
            # 只留「被部分覆盖」事实与时间戳（整体覆盖链在新项 meta.supersedes 全量记录）。
            item["files"] = remaining
            item.setdefault("meta", {})["compacted_partial"] = True
            item["meta"]["compacted_at"] = _now_iso()
            try:
                _retry_transient(
                    lambda: _atomic_write(candidate, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                )
            except (FileNotFoundError, PermissionError):
                pass  # 同上：并发取走即跳过
    # 保序去重（直接前驱在前）
    seen: set[str] = set()
    out: list[str] = []
    for q in superseded:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out


# ---------------------------------------------------------------------------
# enqueue（快照入袋即返回——防内容丢失的核心语义，66 号 §6.1「快照即落袋」）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnqueueOptions:
    """enqueue 可选参数束（NO-LONG-PARAM-LIST 合规收口，§5.150：>7 参数反模式）。

    base_head : 入队时观察到的目标分支 HEAD（A 段不主动取 git，由调用方显式传入；
        B 段落盘接通后用于 §6.4 逐文件快进/冲突判定）。
    depends_on : meta.depends_on 预留字段（A 段只做 schema 预留，不实现级联逻辑）。
    deletes : 删除路径列表（B 段新增，66 号 §6.1 action=delete 语义细化）：已跟踪但
        盘上缺失的文件经此通道入袋，落盘时从 dev 树删除；与 files 共享同键 compaction。
    meta_extra : 附加 meta 键值（并入队列项 meta）。
    allow_oversize_batch : 超大批逃生旗（R2，meta 留痕）：确属原子大批（如整目录
        归档迁移）时由调用方显式给出——旗是必需品不是装饰（q-0007「gate+自家测试
        同批合法」先例）。
    """

    base_head: str | None = None
    depends_on: list[str] | None = None
    deletes: list[str] | None = None
    meta_extra: dict | None = None
    allow_oversize_batch: bool = False


def enqueue_item(
    session_id: str,
    message: str,
    files: list[tuple[str, bytes]],
    *,
    queue_root: str | os.PathLike | None = None,
    options: EnqueueOptions | None = None,
) -> dict:
    """入队核心（API 层；CLI 层负责从 worktree 读文件内容后调本函数）。

    参数
    ----
    files : list[(仓内相对路径, 完整内容 bytes)]——完整快照非 diff（66 号 §4 裁定 2）。
    options : 可选参数束（base_head/depends_on/deletes/meta_extra），见 EnqueueOptions。

    返回：落袋的队列项 dict（含 qid）。
    异常：QueueReject（轻检拒绝，fail-closed 报错非静默）。

    并发安全（66 号 §6.1 v0.4.0 结论）：多会话同时 enqueue 各自 {qid}.json 独立文件，
    无共享写状态；同会话内经进程内 session 锁串行（seq 递增 + compaction 在同一
    关键段），跨进程同会话由 O_EXCL 碰撞重试兜底唯一性。
    """
    opts = options or EnqueueOptions()
    base_head = opts.base_head
    depends_on = opts.depends_on
    deletes = opts.deletes
    meta_extra = opts.meta_extra
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    _validate_session_id(session_id)
    msg = _validate_message(message)
    if not files and not deletes:
        raise QueueReject("空文件清单拒绝入队")
    # R2 大批硬顶（st-commitchain-20260922）：交互车道单批 >_MAX_BATCH_FILES 拒绝。
    # 数据实证：0921 workclean 0091=111 文件磨 116 分钟死在终点 CREATE-GUARD；
    # done 项文件数 p50=3。machine 车道（reconciler 派生自动批）与显式逃生旗豁免。
    total_entries = len(files) + len(deletes or [])
    lane = (meta_extra or {}).get("lane")
    if total_entries > _MAX_BATCH_FILES and not opts.allow_oversize_batch and lane != "machine":
        raise QueueReject(
            f"单批 {total_entries} 文件超上限 {_MAX_BATCH_FILES}（R2 大批硬顶）："
            f"请拆分为多个语义批次入队（失败早暴露不互相拖累）；"
            f"确属原子大批用 --allow-oversize-batch / EnqueueOptions(allow_oversize_batch=True)（meta 留痕）"
        )

    # 1) 轻检 + blob 落袋（先于队列项创建——blob 入袋即内容不丢）
    blob_entries: list[dict] = []
    seen_paths: set[str] = set()
    for path, content in files:
        norm = _validate_relpath(path)
        if norm in seen_paths:
            raise QueueReject(f"同一入队项内路径重复: {norm}")
        seen_paths.add(norm)
        _validate_blob_size(norm, content)
        sha = _store_blob(root, content)
        blob_entries.append(
            {
                "path": norm,
                "blob_sha256": sha,
                "blob_ref": f"blobs/{sha}",
                "base_blob": None,  # A 段预留（B 段：git rev-parse HEAD:{path} 填充，66 号 §6.1 v0.4.0）
                "action": "modify",  # add/modify 统一 modify；delete 经 deletes 通道（B 段细化）
            }
        )
    # B 段 deletes 通道（66 号 §6.1 action=delete）：已跟踪但盘上缺失的删除项，
    # 无 blob 落袋；同键 compaction 与 files 共享 seen_paths（覆盖语义一致）。
    for path in deletes or []:
        norm = _validate_relpath(path)
        if norm in seen_paths:
            raise QueueReject(f"同一入队项内路径重复: {norm}")
        seen_paths.add(norm)
        blob_entries.append(
            {
                "path": norm,
                "blob_sha256": None,
                "blob_ref": None,
                "base_blob": None,
                "action": "delete",
            }
        )

    # 2) 会话内串行段：compaction → seq 分配 → O_EXCL 落 pending（同一会话锁内完成，
    #    66 号 §6.2「compaction 序列需在 session seq 锁内完成」）。
    #    顺序为何是「先 compact 后落新项」而非「先落后 compact+回填」：
    #    2026-08-21 竞态测试实证——先落后回填形态下，drain 把新项 rename 取走后，
    #    supersedes 回填的 os.replace 对不存在目标**静默重建** pending 文件，
    #    同快照同 qid 二次落盘（v17 双落实例）。改为 compact 收集 supersedes 链后
    #    随新项一次落盘，零回填零重建窗口。空窗代价：compact 删旧项与新项落盘间
    #    该键短暂无 pending——blob 已入袋不丢内容，drain 空窗仅视为队列空（无害）。
    lock = _get_session_lock(session_id)
    with lock:
        removed = _compact_pending(root, session_id, seen_paths)
        seq = _read_seq(root, session_id)
        payload_item: dict = {}
        qid = ""
        for _attempt in range(1000):  # O_EXCL 碰撞重试（66 号 §6.1：极端碰撞 seq+1 重试）
            seq += 1
            qid = _make_qid(session_id, seq)
            payload_item = {
                "qid": qid,
                "session_id": session_id,
                "created_at": _now_iso(),
                "branch": _TARGET_BRANCH,
                "base_head": base_head,
                "message": msg,
                "files": blob_entries,
                "meta": {
                    "depends_on": list(depends_on or []),  # P1 级联标记依据（66 号 §6.4）
                    "supersedes": removed,  # compaction 覆盖全链（传递累积，审计可追溯）
                    **(meta_extra or {}),
                },
            }
            payload = json.dumps(payload_item, ensure_ascii=False, indent=2).encode("utf-8")
            try:
                _create_item_excl(root / "pending" / f"{qid}.json", payload)
                break
            except FileExistsError:
                continue  # qid 碰撞（并发同 seq hint）→ seq+1 重试
        else:  # pragma: no cover - 理论不可达（1000 次碰撞）
            # MSG-EXPOSURE 口径：session_id 属敏感标识不入错误消息文本
            raise RuntimeError("qid 分配失败（1000 次碰撞），请清理队列后重试")
        _write_seq(root, session_id, seq)

    logger.info("[enqueue] qid=%s session=%s files=%d supersedes=%s", qid, session_id, len(blob_entries), removed)
    return payload_item


# ---------------------------------------------------------------------------
# Serializer lease（复用 _GlobalCommitLock 同款语义：O_EXCL + TTL + 僵尸 PID 检测；
# 独立文件锁 .runtime/commit_queue/serializer.lease，不共用网关锁——任务口径）
# ---------------------------------------------------------------------------


class SerializerLease:
    """Serializer 租约（66 号 §8 v0.4.0 lease 算法）。

    - 获取：os.open(O_CREAT|O_EXCL) 原子创建；与 _GlobalCommitLock 同款。
    - TTL=300s：持有者崩溃后租约自动过期可回收。
    - 僵尸 PID 检测：持有进程 PID 已死亡立即清理（零窗口期，is_pid_alive 真源唯一）。
    - 超时 5s：自举模式不等待——拿不到抛 LeaseUnavailable，调用方放弃等下次自举。
    - 释放：os.remove。
    """

    def __init__(
        self,
        queue_root: Path,
        timeout: float = _LEASE_TIMEOUT_SECONDS,
        ttl: float = _LEASE_TTL_SECONDS,
        poll_interval: float = _LEASE_POLL_INTERVAL,
    ) -> None:
        self._lease_file = queue_root / _LEASE_FILE
        self._timeout = timeout
        self._ttl = ttl
        self._poll_interval = poll_interval
        self._acquired = False

    def __enter__(self) -> SerializerLease:
        deadline = time.monotonic() + self._timeout
        # do-while 等价结构（expired 后置判定）——保证 timeout=0 也至少尝试一次获取，
        # 与 66 号 §8"拿不到就放弃"语义一致；不用 while True（PERM-TRIGGER 口径：
        # 本文件是事件触发自举，非时间轮询常驻，循环有界）。
        expired = False
        while not expired:
            try:
                fd = os.open(str(self._lease_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(
                        fd,
                        json.dumps({"pid": os.getpid(), "acquired_at": time.time()}, ensure_ascii=False).encode(
                            "utf-8"
                        ),
                    )
                finally:
                    os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                try:
                    data = json.loads(self._lease_file.read_text(encoding="utf-8"))
                    acquired_at = data.get("acquired_at", 0)
                    if not isinstance(acquired_at, (int, float)):
                        acquired_at = 0
                    holder_pid = data.get("pid")
                    if holder_pid is not None and not is_pid_alive(int(holder_pid)):
                        # 僵尸租约：持有者进程已死亡，立即清理（零窗口期）
                        logger.warning("SerializerLease: 持有进程 PID %s 已死亡，清理僵尸租约", holder_pid)
                        try:
                            os.remove(self._lease_file)
                        except OSError:
                            pass
                        continue
                    if time.time() - acquired_at > self._ttl:
                        if holder_pid is None:
                            # 无 PID 可校验存活（旧格式/损坏租约）：保留 TTL 回收语义
                            logger.warning("SerializerLease: 租约超 TTL(%ss) 且无持有者 PID，回收", self._ttl)
                            try:
                                os.remove(self._lease_file)
                            except OSError:
                                pass
                            continue
                        # 持有进程仍存活（死亡持有者已被上面 dead-PID 分支即时回收）=
                        # 慢项在途（如 reconciler 超时 180s 级拖长单项墙钟），绝不可抢。
                        # 病根（2026-09-17 q-…-0013 等 11 条 pathspec did-not-match 死信）：
                        # 抢租约 → 两个 drain 并发跑同一 serializer worktree → thief 的
                        # _sync_worktree(reset --hard + clean -fd) 删掉 victim 已 materialize
                        # 未 commit 的 untracked 新文件 → victim 提交期网关 step3a os.path.isfile
                        # 判 False → git rm --cached 反把它撤暂存 → commit pathspec 不匹配死信
                        # （tracked 文件被 reset 回 HEAD 仍在盘故 pathspec 仍匹配，只有新文件死
                        # =死信特征）。活体持有者由 renew() 心跳保鲜 acquired_at，正常不触发 TTL；
                        # 触发=单项超 TTL 的慢项，等待至 timeout 放弃（自举语义：拿不到等下次）。
                        logger.warning(
                            "SerializerLease: 租约超 TTL(%ss) 但持有 PID=%s 仍存活——判定慢项在途，"
                            "不抢租约（防 worktree 竞态毁未提交新文件），等待至超时放弃",
                            self._ttl,
                            holder_pid,
                        )
                except (OSError, ValueError, TypeError):
                    logger.warning("SerializerLease: 租约文件损坏，清理后重试")
                    try:
                        os.remove(self._lease_file)
                    except OSError:
                        pass
                    continue
                expired = time.monotonic() >= deadline
                if not expired:
                    threading.Event().wait(self._poll_interval)
        raise LeaseUnavailable(f"Serializer lease 被活体持有（timeout {self._timeout}s）: {self._lease_file}") from None

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            try:
                os.remove(self._lease_file)
            except OSError:
                pass
            self._acquired = False
        return False

    def renew(self) -> bool:
        """心跳续租：把 acquired_at 刷新为当前时间，活体持有者保鲜防 TTL 误判过期。

        病根（2026-09-17 11 条 pathspec did-not-match 死信根因）：原租约 acquired_at 只在
        获取时写一次、全程不续；drain 处理慢项（reconciler 超时 180s 级）墙钟超 TTL(300s)
        后并发自举 drain 判其过期抢租约 → 双 drain 同跑一个 serializer worktree → thief 的
        _sync_worktree(reset --hard + clean -fd) 删掉 victim 已 materialize 未 commit 的
        untracked 新文件 → 提交期 pathspec 不匹配死信。续租让活体持有者 acquired_at 始终
        新鲜，TTL 永不对工作中 drain 触发（与 __enter__ 的活体感知不抢租约互为双保险）。

        防易主误覆盖：覆盖前校验租约 pid 仍是本进程（被合法回收/易主则放弃续租并标记
        未持有，绝不 clobber 新持有者）。原子写（tmp + os.replace）防半写损坏。
        fail-open：OSError 不抛进排空主循环（返回 False，调用方继续——续租失败不致命，
        活体感知分支已兜底防抢）。返回 True=续租成功。
        """
        if not self._acquired:
            return False
        try:
            cur = json.loads(self._lease_file.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            logger.warning("SerializerLease: 续租读取租约失败（租约丢失/损坏），放弃续租")
            self._acquired = False
            return False
        if cur.get("pid") != os.getpid():
            logger.warning(
                "SerializerLease: 续租发现租约已易主（pid=%s != 本进程 %s），放弃续租",
                cur.get("pid"),
                os.getpid(),
            )
            self._acquired = False
            return False
        _now = time.time()
        payload = json.dumps({"pid": os.getpid(), "acquired_at": _now, "renewed_at": _now}, ensure_ascii=False).encode(
            "utf-8"
        )
        tmp = self._lease_file.with_name(f"{self._lease_file.name}.renew-{os.getpid()}")
        try:
            with open(tmp, "wb") as fh:
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, self._lease_file)
            return True
        except OSError as exc:
            logger.warning("SerializerLease: 续租写入失败（不阻断排空）: %s", exc)
            try:
                os.remove(tmp)
            except OSError:
                pass
            return False


# ---------------------------------------------------------------------------
# drain（Serializer 主循环，66 号 §6.3：FIFO 取项 → processing → 落盘 → done/dead）
# ---------------------------------------------------------------------------


def _notify_task_board_dead_letter(item: dict) -> None:
    """死信 → task_board 打标联动（66 号 §6.4，P1 2026-08-28 落地）。

    队列项 meta.task_id 存在时，经 scripts.task_board.tag_dead_letter 把
    {qid, reason, owner, tagged_at} 写入该任务 metadata_json.deadletter；
    任务不存在/已完成（rc=2）或 metadata 损坏（rc=1）仅记日志跳过；
    板不可达等异常吞掉不阻断排空（死信已落 dead/，联动是可观测性增强，宁漏不误）。
    task_id 注入通道：enqueue 时 EnqueueOptions.meta_extra={"task_id": "T-xxx"}。
    """
    task_id = (item.get("meta") or {}).get("task_id")
    if not task_id:
        return
    try:
        from scripts import task_board as tb

        conn = tb._connect(tb._resolve_board_db())
        try:
            rc = tb.tag_dead_letter(
                conn,
                task_id,
                qid=item.get("qid", ""),
                reason=item.get("dead_reason", ""),
                owner=item.get("session_id", ""),
                actor="commit_queue",
            )
        finally:
            conn.close()
        if rc == 0:
            logger.info("[drain] task_board 死信打标: task=%s qid=%s", task_id, item.get("qid"))
        else:
            logger.info("[drain] task_board 打标跳过: task=%s rc=%s（任务不存在/已完成/metadata 损坏）", task_id, rc)
    except Exception as exc:  # noqa: BLE001 — 联动失败不阻断排空
        logger.warning("[drain] task_board 死信联动失败（忽略，死信已落 dead/）: %s", exc)


def _read_item(path: Path) -> dict | None:
    """读队列项 JSON，容忍 enqueue 写入窗口（O_EXCL 创建后单 write 的极短半写窗口）。

    重试 _READ_RETRY_TIMES × 50ms ≈ 1s；仍失败返回 None（本轮跳过留 pending，永不因
    读取竞态进死信；真损坏项留待人工，66 号 §8 队列腐败口径：append-only + fsck 校验）。
    """
    for _ in range(_READ_RETRY_TIMES):
        try:
            if path.stat().st_size > 0:
                return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        threading.Event().wait(_READ_RETRY_INTERVAL)
    logger.error("[drain] 队列项读取失败（疑似损坏，留待人工）: %s", path)
    return None


def _recover_orphans(queue_root: Path) -> list[str]:
    """processing/ 孤儿回收（66 号 §8：崩溃后下次自举从 processing 续跑——重入 pending）。

    仅 lease 持有者调用（单写者不变量）。原子 rename 回 pending/；done/dead 同名文件
    已存在则直接删除孤儿（幂等重放保护：已确认终态的不重跑，防双落）。
    """
    recovered: list[str] = []
    processing_dir = queue_root / "processing"
    for orphan in sorted(processing_dir.glob("q-*.json")):
        qid = orphan.stem
        if (queue_root / "done" / orphan.name).exists() or (queue_root / "dead" / orphan.name).exists():
            # 已有终态（崩溃发生在 rename 之后？防御性）→ 删孤儿防双落
            try:
                os.remove(orphan)
            except OSError:
                pass
            logger.warning("[drain] 孤儿项 %s 已有终态，删除防双落", qid)
            continue
        try:
            os.rename(orphan, queue_root / "pending" / orphan.name)
            recovered.append(qid)
        except OSError as exc:
            logger.error("[drain] 孤儿回收失败 %s: %s", qid, exc)
    if recovered:
        logger.info("[drain] 回收 processing 孤儿 %d 项重入 pending: %s", len(recovered), recovered)
    return recovered


# ---------------------------------------------------------------------------
# 依赖级联标记（66 号 §6.4 + 08 号文 §4.3 P1，2026-08-29 落地）
# ---------------------------------------------------------------------------


def _mark_cascade_stale(root: Path, landed_item: dict) -> list[str]:
    """项 X 成功落盘后的级联标记：扫描 pending 剩余项，命中的标 stale，返回命中 qid 列表。

    命中条件（66 号 §6.4「级联标记」）：
    - meta.depends_on 含 X.qid（显式依赖前置项）；或
    - base_head 与 X.base_head 相同且均非空（base_head 经由 X——同基底入队，
      X 落盘后目标分支 HEAD 已越过该基底，Y 的基底过龄）。

    stale 项不立即处置——排到队首时经 _revalidate_stale_base 重校验基底：
    仍适用→清标放行，不适用→降死信候选（dead_reason=cascade_stale）。
    仅 lease 持有者（单写者）调用；仅作用 pending（done/dead 是终态不触碰）；
    并发 compaction 移除（FileNotFoundError）/写入窗口瞬态占用（PermissionError）
    容错跳过。已标 stale 的项不重复标——保留首个触发源（stale_by 审计首因）。
    """
    landed_qid = landed_item.get("qid", "")
    landed_base = landed_item.get("base_head")
    marked: list[str] = []
    for candidate in sorted((root / "pending").glob("q-*.json")):
        try:
            item = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # 写入窗口或损坏——跳过不碰（读者容错，同 _compact_pending 口径）
        meta = item.setdefault("meta", {})
        if meta.get("stale"):
            continue
        depends_hit = landed_qid in (meta.get("depends_on") or [])
        base_hit = bool(landed_base) and bool(item.get("base_head")) and item["base_head"] == landed_base
        if not (depends_hit or base_hit):
            continue
        meta["stale"] = True
        meta["stale_by"] = landed_qid
        meta["stale_at"] = _now_iso()
        try:
            _retry_transient(
                lambda: _atomic_write(candidate, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
            )
            marked.append(item.get("qid", candidate.stem))
        except (FileNotFoundError, PermissionError):
            pass  # 并发 compaction 移除/写入窗口——跳过（同 _compact_pending 竞态口径）
    return marked


def _revalidate_stale_base(item: dict, head_reader) -> tuple[bool, list[str]]:
    """stale 项基底重校验（66 号 §6.4）：base_blob vs 当前 HEAD 逐文件比对。

    返回 (仍适用, 不适用路径清单)。判定口径：
    - base_blob 为空的条目跳过（A 段无基底信息，无法判定→放行口径）；
    - base_blob 非空而 head_reader 缺失 → fail-closed 判不适用（无法确认仍适用即
      降死信候选，人工经 requeue 基于当前工作区重建快照取回，66 号 §6.4 死信闭环）；
    - head_reader: callable(仓内相对路径) -> 当前 HEAD 该路径 blob 标识（与 base_blob
      同 id 空间），路径不在 HEAD 返回 None；比对不一致即不适用。
    队列层保持零 git 依赖（66 号 §6.1 刻意出入 #3）——HEAD 读取能力由调用方注入。
    """
    mismatched: list[str] = []
    for f in item.get("files") or []:
        base_blob = f.get("base_blob")
        if not base_blob:
            continue
        path = f.get("path", "?")
        if head_reader is None:
            mismatched.append(f"{path}(head_reader 缺失无法重校验)")
            continue
        if head_reader(path) != base_blob:
            mismatched.append(path)
    return (not mismatched, mismatched)


_MACHINE_LANE_STARVATION_SEC = 1800.0  # machine 单饿死上限 30min（P1-D 护栏）


def _item_lane(item: dict | None) -> str:
    """P1-D 车道判定（方案 v2.1 §3.6）：machine=reconciler 派生自动批；缺省 interactive。

    判定真源=meta.lane 显式标记；兼容历史项：meta.interactive=="true"→interactive、
    meta.rerouted_from=="_commit_auto"→machine、其余缺省 interactive（历史交互项）。
    """
    meta = (item or {}).get("meta") or {}
    lane = meta.get("lane")
    if lane in ("interactive", "machine"):
        return lane
    if meta.get("rerouted_from") == "_commit_auto":
        return "machine"
    return "interactive"


def _pick_head(heads: list) -> tuple:
    """P1-D 车道优先选队首：interactive 先落、machine 让路；30min 防饿死兜底。

    返回 (path, lane)。interactive 项存在 → qid 序取首个 interactive；无
    interactive → qid 序取首个 machine（队空时 machine 自然落地）。最老 machine
    等待超 _MACHINE_LANE_STARVATION_SEC → 提前放行（防持续交互流量饿死）。
    项读取失败按 interactive 保守处理（不降级跳过——FIFO 不跳项铁律）。
    """
    from datetime import datetime

    oldest_machine_age = 0.0
    now = datetime.now().astimezone()
    first_interactive = None
    first_machine = None
    for h in heads[:64]:  # 有界扫描（pending 通常 <10，64=防御上界）
        item = _read_item(h)
        if _item_lane(item) == "machine":
            if first_machine is None:
                first_machine = h
            if item and item.get("created_at"):
                try:
                    age = (now - datetime.fromisoformat(item["created_at"])).total_seconds()
                    oldest_machine_age = max(oldest_machine_age, age)
                except (ValueError, TypeError):
                    pass
        elif first_interactive is None:
            first_interactive = h
    if oldest_machine_age > _MACHINE_LANE_STARVATION_SEC and first_machine is not None:
        return first_machine, "machine"
    if first_interactive is not None:
        return first_interactive, "interactive"
    return first_machine, "machine"


def drain_queue(
    queue_root: str | os.PathLike | None = None,
    *,
    landing=None,
    max_items: int | None = None,
    lease_timeout: float = _LEASE_TIMEOUT_SECONDS,
    head_reader=None,
    done_ttl_days: float | None = _DONE_TTL_DAYS_DEFAULT,
) -> dict:
    """Serializer 排空（单写者主循环）。

    流程（66 号 §6.3 + §8）：拿 lease → 回收 processing 孤儿 → FIFO（qid 单调序）取
    pending 队首 → 原子 rename processing → landing → done/（附 landed_at/landed_id）
    或 dead/（附 dead_reason/dead_at，不卡队后续继续）→ 排空释放 lease。

    landing : callable(item: dict, queue_root: Path) -> LandingResult；None=默认桩
        （仅标记 done 不真提交，B 段接专用 worktree 真落盘）。
    head_reader : callable(仓内相对路径) -> 当前 HEAD 该路径 blob 标识 | None；
        P1 级联 stale 项基底重校验用（_revalidate_stale_base）；None=仅 base_blob
        全空的项可重校验通过（A 段口径），base_blob 非空项 fail-closed 降死信候选。
    done_ttl_days : done/ TTL 天数（默认 7 天，66 号 §12 Q3）；排空收尾在 lease 内
        自动清理超龄 done 项；None=本轮不清理。dead/ 永不清理不变量不受影响。
    异常语义：landing 抛 Exception → 单项失败死信；BaseException 不捕获向上传播
        （模拟进程崩溃，当前项留 processing 等孤儿回收）。
    """
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    landing_fn = landing if landing is not None else default_landing_stub
    stats = {
        "skipped": False,
        "recovered": 0,
        "done": 0,
        "dead": 0,
        "processed_qids": [],
        "stale_cleared": 0,  # P1 级联：stale 重校验仍适用清标放行数
        "cascade_marked": 0,  # P1 级联：成功落盘后续项被标 stale 数
        "done_cleaned": 0,  # done/ TTL 清理移除数
    }

    with SerializerLease(root, timeout=lease_timeout) as lease:
        stats["recovered"] = len(_recover_orphans(root))
        processed = 0
        # 排空即退出（66 号 §6.3）：heads 为空 break；循环上界=max_items——有界批处理，
        # 非 while True 时间轮询（PERM-TRIGGER 口径：事件触发自举，无常驻）。
        while max_items is None or processed < max_items:
            # 逐项心跳续租（2026-09-18 st-flashspeed-20260918 死信治本）：慢项在途
            # （reconciler ~180s）会撑破 _LEASE_TTL_SECONDS(300s) 单批预算，若租约
            # acquired_at 不刷新，并发自举 drain 会判租约超期并抢锁——两个 drain 争用
            # 同一 serializer worktree，抢锁方 _sync_worktree 的 clean -fd 删掉受害方
            # 已物化未提交的 untracked 新文件（tracked 文件 reset 后仍在，故只有新文件
            # 死信=pathspec did not match 取证签名）。每处理一项刷新租约，令"活着且在
            # 干活"的持有者永不被 TTL 误抢（配合 __enter__ 的存活感知 TTL 分支双保险）。
            if not lease.renew():
                # D7（st-commitchain-20260922，环节2 E3）：renew 返回 False=租约丢失/
                # 易主（仅 corrupt 清理分支可达的理论双写窗）——立即终止本轮，当前项
                # 留 processing 等孤儿回收；绝不带着失效租约继续碰共享 worktree。
                logger.critical("[drain] 租约续期失败（易主/丢失），本轮立即终止：当前项留 processing 等孤儿回收")
                break
            pending_dir = root / "pending"
            heads = sorted(pending_dir.glob("q-*.json"))  # qid 字典序 == 车道内 FIFO 序
            if not heads:
                break  # 排空即退出（66 号 §6.3）
            # P1-D 车道优先（方案 v2.1 §3.6，st-commitspeed-20260916）：interactive
            # 先落（AI 交互提交延迟敏感）、machine 让路（reconciler 派生批延迟不
            # 敏感）；车道内维持 qid 单调 FIFO；30min 防饿死兜底。纯 FIFO 不变量
            # 修订=车道化 FIFO（裁定留档本 commit message）。
            head, lane = _pick_head(heads)
            if head is None:
                break
            if lane == "machine":
                stats.setdefault("machine_lane_landed", 0)
                stats["machine_lane_landed"] = stats.get("machine_lane_landed", 0) + 1
            processing_path = root / "processing" / head.name
            try:
                # 原子取项：pending → processing；PermissionError=enqueue 写入窗口瞬态占用，
                # 重试收敛（保 FIFO 不跳项——取不到队首本轮结束，下轮自举再来）
                _retry_transient(lambda: os.rename(head, processing_path))
            except FileNotFoundError:
                continue  # 被并发 compaction 移除——取下一队首（竞态安全，66 号 §6.2）
            except PermissionError:
                logger.info("[drain] 队首 %s 持续被占用（写入者慢），本轮结束等下次自举", head.name)
                break
            item = _read_item(processing_path)
            if item is None:
                # 读取持续失败：放回 pending 下轮再试（不冤枉慢写入者，不见死信）
                try:
                    os.rename(processing_path, head)
                except OSError:
                    pass
                break
            qid = item.get("qid", head.stem)
            _item_t0 = time.monotonic()  # D7 单项墙钟挂账（环节2 E4）
            result: LandingResult | None = None
            if (item.get("meta") or {}).get("stale"):
                # P1 级联（66 号 §6.4）：stale 项重校验基底——仍适用清标放行走正常
                # landing；不适用直接降死信候选（dead_reason=cascade_stale），不消耗 landing
                still_ok, mismatched = _revalidate_stale_base(item, head_reader)
                if still_ok:
                    meta = item["meta"]
                    meta.pop("stale", None)
                    meta["stale_cleared_at"] = _now_iso()  # stale_by 保留作审计溯源
                    stats["stale_cleared"] += 1
                    logger.info("[drain] qid=%s stale 重校验仍适用，清标放行（stale_by=%s）", qid, meta.get("stale_by"))
                else:
                    result = LandingResult(
                        ok=False,
                        reason=(
                            f"cascade_stale: 基底重校验不适用 {mismatched}（stale_by={item['meta'].get('stale_by')}）"
                        ),
                    )
            if result is None:
                try:
                    result = landing_fn(item, root)
                except LandingEnvironmentError as exc:
                    # 环境失败 ≠ 物品失败（2026-09-10 死信事故治本）：landing 自身
                    # repo/worktree 不可用时，本轮所有项都必然同样失败——当前项退回
                    # pending、终止整轮、绝不死信（真实物品不被环境事故拖进坟墓）。
                    try:
                        _retry_transient(lambda: os.rename(processing_path, head))
                    except OSError:
                        logger.error("[drain] qid=%s 环境失败退回 pending 失败，留 processing 等孤儿回收", qid)
                    logger.error(
                        "[drain] landing 环境失败，终止本轮排空（当前项退回 pending，不死信）: %s",
                        exc,
                    )
                    break
                except Exception as exc:  # noqa: BLE001 — 单项失败 → 死信不卡队（66 号 §4 裁定 4）
                    result = LandingResult(ok=False, reason=f"landing 异常: {type(exc).__name__}: {exc}")
            if result.ok:
                item["landed_at"] = _now_iso()
                item["landed_id"] = result.landed_id
                _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                os.replace(processing_path, root / "done" / head.name)
                stats["done"] += 1
                # 依赖级联标记（66 号 §6.4，P1 2026-08-29 落地）：X 成功落盘后扫描
                # pending，meta.depends_on 含 X.qid 或 base_head 经由 X 的后续项标 stale
                marked = _mark_cascade_stale(root, item)
                if marked:
                    stats["cascade_marked"] += len(marked)
                    logger.info("[drain] qid=%s 落盘，级联标记 stale: %s", qid, marked)
            else:
                # 死信：附原因移 dead/，队列继续前进（DLQ 语义不堵队，66 号 §6.4）
                item["dead_at"] = _now_iso()
                item["dead_reason"] = result.reason
                _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                os.replace(processing_path, root / "dead" / head.name)
                stats["dead"] += 1
                logger.warning("[drain] qid=%s 进死信: %s", qid, result.reason)
                _notify_task_board_dead_letter(item)  # 66 号 §6.4 task_board 死信标签联动（P1 已落地）
            _item_dur = time.monotonic() - _item_t0
            if _item_dur > _SLOW_ITEM_LEDGER_SECONDS:
                _ledger_slow_item(root, qid, item.get("session_id"), round(_item_dur, 1))
            stats["processed_qids"].append(qid)
            processed += 1
        if done_ttl_days is not None:
            # done/ TTL 清理（66 号 §12 Q3：done 7 天 / dead 永不清理）；lease 内单写者安全
            stats["done_cleaned"] = len(cleanup_done(root, ttl_days=done_ttl_days)["removed"])
    # 死信积压告警（2026-09-11：drain 收尾事件触发，lease 外执行——task_board IO 不占
    # 单写者窗口；内部全量 fail-open，绝不影响排空结果）
    try:
        emit_dead_backlog_alert(root)
    except Exception as exc:  # noqa: BLE001 — 告警是旁路可观测性，双重保险吞异常
        logger.warning("[health] 死信积压告警异常（忽略）: %s", exc)
    try:
        check_dead_burst(root)  # D6 死信爆发升级告警（Owner 0922：285 死/日应当天拉铃）
    except Exception as exc:  # noqa: BLE001 — 同上，旁路可观测性
        logger.warning("[health] 死信爆发告警异常（忽略）: %s", exc)
    return stats


def try_bootstrap_drain(queue_root: str | os.PathLike | None = None, *, landing=None) -> dict:
    """入队自举排空（66 号 §8：无常驻进程——写队后尝试拿 lease，拿不到就放弃等下次）。"""
    if landing is None:
        # B3（#ARCH-310，2026-09-12）：自举排空默认接真落地——默认桩=标记 done 不真
        # 提交，对真实队列是"假 done 丢内容"footgun（q-0004 实证：文档项被标 done 但
        # dev 无 commit）。仅在可安全锚定仓根的默认队列布局（<repo>/.runtime/commit_queue）
        # 下启用：自定义队列根（测试隔离 tmp 等）无法判定归属仓，保持桩行为（项留
        # pending 不丢失）。延迟 import 防循环（B 段 landing 反向 import 本模块）；
        # 装载失败退回桩（fail-open：入队主流程不受影响）。
        try:
            _qroot = resolve_queue_root(queue_root)
            _repo: Path | None = _qroot.parents[1] if _qroot.parent.name == ".runtime" else None
            if _repo is not None and (_repo / "scripts" / "governance" / "commit_queue_landing.py").is_file():
                _repo_root_str = str(_repo)
                if _repo_root_str not in sys.path:
                    sys.path.insert(0, _repo_root_str)
                _purge_poisoned_scripts_package()
                from scripts.governance.commit_queue_landing import WorktreeLanding  # noqa: PLC0415

                landing = WorktreeLanding(repo_root=_repo, queue_root=_qroot)
        except Exception:  # noqa: BLE001 — 排空是 best-effort，装载失败不阻断入队
            logger.warning("[bootstrap] 真落地装载失败，本次退回默认桩（项留 pending 不丢）", exc_info=True)
            landing = None
    try:
        return drain_queue(queue_root, landing=landing)
    except LeaseUnavailable as exc:
        logger.info("[bootstrap] %s —— 另一 Serializer 在跑，放弃等下次自举", exc)
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


# ---------------------------------------------------------------------------
# requeue（死信取回重入队，66 号 §6.4 死信闭环 + 08 号文 §4.3 P1，2026-08-29 落地）
# ---------------------------------------------------------------------------


def _notify_task_board_requeued(old_item: dict, new_qid: str) -> None:
    """requeue → task_board 死信标签标注联动（66 号 §6.4）。

    原死信项 meta.task_id 存在时，经 scripts.task_board.tag_requeued 把
    {old_qid, new_qid, requeued_at} 写入 metadata_json.deadletter.requeued——
    死信标签不解除（死信事实留痕），重复取回以最新为准。
    与 _notify_task_board_dead_letter 同口径：联动失败仅记日志不阻断（宁漏不误，
    重入队已完成是主流程）。
    """
    task_id = (old_item.get("meta") or {}).get("task_id")
    if not task_id:
        return
    try:
        from scripts import task_board as tb

        conn = tb._connect(tb._resolve_board_db())
        try:
            rc = tb.tag_requeued(
                conn,
                task_id,
                old_qid=old_item.get("qid", ""),
                new_qid=new_qid,
                actor="commit_queue",
            )
        finally:
            conn.close()
        if rc == 0:
            logger.info("[requeue] task_board 死信标签标注 requeued: task=%s qid=%s", task_id, old_item.get("qid"))
        else:
            logger.info(
                "[requeue] task_board 标注跳过: task=%s rc=%s（任务不存在/已完成/metadata 损坏/无死信标签）",
                task_id,
                rc,
            )
    except Exception as exc:  # noqa: BLE001 — 联动失败不阻断重入队主流程
        logger.warning("[requeue] task_board 联动失败（忽略，重入队已完成）: %s", exc)


def requeue_dead_item(
    qid: str,
    *,
    queue_root: str | os.PathLike | None = None,
    worktree_root: str | os.PathLike | None = None,
    session_id: str | None = None,
    message: str | None = None,
    base_head: str | None = None,
    from_bag: bool = False,
) -> dict:
    """死信取回重入队（66 号 §6.4 死信闭环 + 08 号文 §4.3 P1）。

    qid 口径（裁定留痕）：**新 qid，不复用原 qid**——原死信项留 dead/ 永不清理
    （66 号 §8 不变量），同 qid 再入 pending 会与留痕项撞名破坏四态唯一；
    新 qid 排 FIFO 队尾，meta.requeued_from=原 qid + 原死信项追加
    requeued={new_qid, at} 标注，双向可追溯。

    快照重建（66 号 §6.4 死信闭环原文口径）：基于**当前工作区**文件内容重新入队——
    每会话有独立 worktree，重入队快照基于本会话 worktree 状态，一次重试即可通过
    快进判定。action=delete 条目走 deletes 通道（无 blob）；modify 条目工作区文件
    缺失/不可读 → RequeueError（人工判定该文件是否还应提交，不静默造空快照）。

    task_board 联动：原项 meta.task_id 存在 → metadata_json.deadletter 标注
    requeued（标签不解除，死信事实留痕）。

    返回 {"old_qid", "new_qid", "item"}；异常 RequeueError（CLI 映射 exit 1）/
    QueueReject（新项入队轻检拒绝，CLI 映射 exit 2）。
    """
    if not qid or not _QID_RE.match(qid):
        raise RequeueError(f"非法 qid（白名单 q-YYYYMMDD-<session>-<seq>，防路径穿越）: {qid!r}")
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    dead_path = root / "dead" / f"{qid}.json"
    if not dead_path.exists():
        raise RequeueError(f"qid 不在 dead/（仅死信项可取回重入队）: {qid}")
    try:
        old_item = json.loads(dead_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RequeueError(f"死信项读取失败: {qid}（{exc}）") from exc

    wt = Path(worktree_root) if worktree_root else Path.cwd()
    payload: list[tuple[str, bytes]] = []
    deletes: list[str] = []
    # D7 透明化（st-commitchain-20260922，环节9 E1 勘误保守落地）：
    # 默认仍=当前工作区内容（修-重试工作流依赖此语义：改完 requeue 带新内容），
    # 但 MUST 显式告知「快照≠死信原快照」；--from_bag 则从 dead/ 项 blob 袋直读
    # 原始内容（sha256 自校验，工作区漂移免疫）。
    if from_bag:
        logger.info("[requeue] from_bag=原袋重建（内容寻址 sha256 自校验，工作区漂移免疫）")
    else:
        logger.info(
            "[requeue] 快照来源=当前工作区 %s（非死信原快照；改-重试工作流预期行为，需原内容加 --from-bag）", wt
        )
    for f in old_item.get("files") or []:
        path = f.get("path")
        if not path:
            continue
        if f.get("action") == "delete":
            deletes.append(path)
            continue
        if from_bag and f.get("blob_ref"):
            try:
                content = (root / f["blob_ref"]).read_bytes()
            except OSError as exc:
                raise RequeueError(
                    "原袋 blob 读取失败（路径见 details）",
                    details={"path": path, "cause": str(exc)},
                ) from exc
            sha = hashlib.sha256(content).hexdigest()
            if sha != f.get("blob_sha256"):
                raise RequeueError(
                    "原袋 blob 校验失败：内容寻址 sha256 不符（详见 details）",
                    details={"path": path},
                )
            payload.append((path, content))
            continue
        try:
            payload.append((path, (wt / path).read_bytes()))
        except OSError as exc:
            # MSG-EXPOSURE §5.99.20 口径：消息只留摘要，路径走 details 结构化字段
            raise RequeueError(
                "工作区文件缺失/不可读，无法重建快照（路径见 details）——若该文件应删除请人工处理",
                details={"path": path, "cause": str(exc), "hint": "from_bag=True 可取死信原快照"},
            ) from exc
    if not payload and not deletes:
        raise RequeueError(f"死信项无文件条目可取回: {qid}")

    task_id = (old_item.get("meta") or {}).get("task_id")
    new_item = enqueue_item(
        session_id or old_item.get("session_id", ""),
        message or old_item.get("message", ""),
        payload,
        queue_root=root,
        options=EnqueueOptions(
            base_head=base_head,
            deletes=deletes or None,
            # requeue 豁免大批硬顶（R2）：死信重试是既定决策的延续，尺寸判定在原入队时
            # 已做出——若此处拒绝，超大死信将永远无法重入队（死锁）。
            allow_oversize_batch=True,
            meta_extra={"requeued_from": qid, **({"task_id": task_id} if task_id else {})},
        ),
    )
    # 取回留痕：原死信项追加 requeued 标注（dead/ 永不清理——只标注不删除）
    old_item["requeued"] = {"new_qid": new_item["qid"], "at": _now_iso()}
    _atomic_write(dead_path, json.dumps(old_item, ensure_ascii=False, indent=2).encode("utf-8"))
    _notify_task_board_requeued(old_item, new_item["qid"])
    logger.info("[requeue] %s -> %s（基于当前工作区重建快照，新 qid 排 FIFO 队尾）", qid, new_item["qid"])
    return {"old_qid": qid, "new_qid": new_item["qid"], "item": new_item}


# ---------------------------------------------------------------------------
# done/ TTL 清理（66 号 §12 Q3 已闭环：done 7 天 TTL / dead 永不自动清理）
# ---------------------------------------------------------------------------


def cleanup_done(
    queue_root: str | os.PathLike | None = None,
    *,
    ttl_days: float = _DONE_TTL_DAYS_DEFAULT,
    now: datetime | None = None,
) -> dict:
    """done/ TTL 清理：超龄 done 项删除，返回 {"removed": [qid...], "kept": n}。

    年龄基准 landed_at（落盘时刻），缺失/解析失败回退文件 mtime。
    **dead/ 永不触碰**（66 号 §8 队列腐败口径：死信回退给人，永不自动清理——
    不变量由 TestDoneTtlCleanup 专测钉死）；pending/processing 不触碰；
    blobs/ 内容寻址共享存储不在本清理范围（多队列项可共享同一 blob）。
    drain 排空收尾自动调用（lease 内单写者安全）；CLI cleanup 子命令可手动触发。
    """
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    ref = now or datetime.now().astimezone()
    cutoff = ref.timestamp() - ttl_days * 86400
    removed: list[str] = []
    kept = 0
    for entry in sorted((root / "done").glob("q-*.json")):
        ts: float | None = None
        try:
            item = json.loads(entry.read_text(encoding="utf-8"))
            landed_at = item.get("landed_at")
            if landed_at:
                ts = datetime.fromisoformat(landed_at).timestamp()
        except (OSError, ValueError):
            ts = None
        if ts is None:
            try:
                ts = entry.stat().st_mtime
            except OSError:
                kept += 1
                continue
        if ts < cutoff:
            try:
                _retry_transient(lambda: os.remove(entry))
                removed.append(entry.stem)
            except (FileNotFoundError, PermissionError):
                pass  # 并发读取窗口瞬态占用——留待下轮清理
        else:
            kept += 1
    if removed:
        logger.info("[cleanup] done/ TTL(%s 天) 清理 %d 项: %s", ttl_days, len(removed), removed)
    return {"removed": removed, "kept": kept}


# ---------------------------------------------------------------------------
# status（66 号 §6.6 落盘确认接口：会话 push/声明完成前 MUST 先确认队列项全部 done）
# ---------------------------------------------------------------------------


def _ledger_slow_item(root: Path, qid: str, session_id: str | None, seconds: float) -> None:
    """单项墙钟超阈挂账（D7 环节2 E4：大注册表批磨时从无声变有账；daemon 堵点本同文件）。

    写 root.parent/audit/bottleneck_ledger.jsonl（kind=slow_item）；旁路可观测性
    fail-open：写失败仅记日志绝不阻断排空。
    """
    try:
        ledger = root.parent / "audit" / "bottleneck_ledger.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {"ts": time.time(), "kind": "slow_item", "qid": qid, "session_id": session_id, "seconds": seconds},
            ensure_ascii=False,
        )
        with open(ledger, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        logger.warning("[drain] 单项墙钟超阈挂账: qid=%s seconds=%.1fs", qid, seconds)
    except OSError as exc:  # noqa: BLE001 — 旁路可观测性写失败不阻断排空
        logger.warning("[drain] 堵点本写入失败（忽略）: %s", exc)


def _lease_snapshot(root: Path) -> dict:
    """serializer.lease 只读快照（R5：等待方可见「谁在持有、磨了多久」）。

    0921 实测痛点：租约被持时 queue_status 不读租约，processing=0 显「队列健康」，
    等待会话被迫 cat 租约+Get-CimInstance 反推——本快照把这段考古变成一眼可见。
    """
    lease_path = root / _LEASE_FILE
    if not lease_path.exists():
        return {"present": False}
    try:
        data = json.loads(lease_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"present": False, "corrupt": True}
    if not isinstance(data, dict):  # P2-1（红队 0922）：合法 JSON 非字典（list/int）不崩 status
        return {"present": False, "corrupt": True}
    pid = data.get("pid")
    now = time.time()
    acquired_at = data.get("acquired_at") if isinstance(data.get("acquired_at"), (int, float)) else 0.0
    renewed_at = data.get("renewed_at") if isinstance(data.get("renewed_at"), (int, float)) else acquired_at
    alive = False
    if pid is not None:
        try:
            alive = is_pid_alive(int(pid))
        except (TypeError, ValueError):
            alive = False
    return {
        "present": True,
        "holder_pid": pid,
        "alive": alive,
        "acquired_age_s": round(now - acquired_at, 1) if acquired_at else None,
        "renewed_age_s": round(now - renewed_at, 1) if renewed_at else None,
        "over_ttl": bool(acquired_at and now - acquired_at > _LEASE_TTL_SECONDS),
        # 语义注记：alive=True=活体持有（F9 绝不可抢，正在磨）；alive=False=僵尸残留
        # （下个竞争者进 __enter__ 即回收）。renewed_age_s 巨大而 alive=True=大项在途
        # （renew 逐项刷新，项内必然陈旧——设计使然非异常）。
        "state": "drain-active" if alive else "stale",
    }


def _head_snapshot(root: Path) -> dict | None:
    """队首 pending 项快照（R5：位置感——队首是谁、多少文件、已等多久）。"""
    try:
        heads = sorted((root / "pending").glob("q-*.json"))
    except OSError:
        return None
    if not heads:
        return None
    try:
        item = json.loads(heads[0].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"qid": heads[0].stem, "_corrupt": True}
    created = item.get("created_at")
    waiting_s = None
    if created:
        try:
            waiting_s = round(time.time() - datetime.fromisoformat(created).timestamp(), 1)
        except (ValueError, TypeError):
            waiting_s = None
    return {
        "qid": item.get("qid", heads[0].stem),
        "session_id": item.get("session_id"),
        "files": len(item.get("files") or []),
        "created_at": created,
        "waiting_s": waiting_s,
    }


def _daemon_snapshot(root: Path) -> dict:
    """belt daemon 在线探测（环节3 E6：守护失联可观测——补位消费者死=排空纯靠内联自举）。"""
    lock_path = root / "belt_daemon.lock"
    if not lock_path.exists():
        return {
            "online": False,
            "note": "belt daemon 离线（手动启动形态、无计划任务重拉）：排空依赖 enqueue/status/requeue 内联自举",
        }
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        online = isinstance(data, dict) and is_pid_alive(int(data.get("pid")))
    except (OSError, ValueError, TypeError, AttributeError):
        online = False
    return {"online": online}


def queue_status(queue_root: str | os.PathLike | None = None, *, session_id: str | None = None) -> dict:
    """队列状态总览；--session 过滤该会话各 qid 的 pending/processing/done/dead 状态。"""
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    counts: dict[str, int] = {}
    items: list[dict] = []
    for state in _STATES:
        state_dir = root / state
        entries = sorted(state_dir.glob("q-*.json"))
        counts[state] = 0
        for entry_idx, entry in enumerate(entries):
            try:
                item = json.loads(entry.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                item = {"qid": entry.stem, "session_id": None, "_corrupt": True}
            if session_id is not None and item.get("session_id") != session_id:
                continue
            counts[state] += 1
            record = {
                "qid": item.get("qid", entry.stem),
                "session_id": item.get("session_id"),
                "state": state,
                "created_at": item.get("created_at"),
            }
            if state == "dead":
                record["dead_reason"] = item.get("dead_reason")
            if state == "done":
                record["landed_id"] = item.get("landed_id")
            if state == "pending":
                # R5 位置感：前面还有几项（FIFO 序=qid 字典序，与 drain :1134 同口径）
                record["position_ahead"] = entry_idx
            items.append(record)
    return {
        "queue_root": str(root),
        "counts": counts,
        "total": sum(counts.values()),
        "items": items,
        "lease": _lease_snapshot(root),
        "head": _head_snapshot(root),
        "daemon": _daemon_snapshot(root),
    }


# ---------------------------------------------------------------------------
# 队列健康快照 + 死信积压告警（2026-09-11 死信率告警最小落地）
# 背景：884 项死信积压 8 天无人发现（.runtime/tmp/commit_queue_dead_triage_20260910.md
# §下一步 3/4）——每项 task_id 联动只覆盖带 task_id 的项，auto 同步项（无 task_id）
# 是可见性盲区。本节补两块：只读健康快照（聚合口径复用该 triage）+ 积压超阈告警。
# ---------------------------------------------------------------------------


def classify_dead_reason(reason: str) -> str:
    """死因三分类：env（环境性，物品无辜可 requeue）/ item（门禁物品性，gate 语义正常）/ other。"""
    reason = reason or ""
    if any(m in reason for m in _DEAD_REASON_ENV_MARKERS):
        return "env"
    if any(m in reason for m in _DEAD_REASON_ITEM_MARKERS):
        return "item"
    return "other"


def queue_health(queue_root: str | os.PathLike | None = None) -> dict:
    """队列健康快照（只读，不触发排空——与 status 的自举排空语义刻意区分）。

    聚合：四态计数 + dead 死因分类 + 最老 pending/processing 项龄（小时，积压监控
    关键指标）+ blobs 数。供 CLI ``health`` 子命令与死信积压告警共用。
    """
    root = resolve_queue_root(queue_root)
    counts: dict[str, int] = {s: 0 for s in _STATES}
    dead_categories: dict[str, int] = {}
    dead_per_session: dict[str, int] = {}  # D6：单会话死亡计数（连败链可观测，环节6 E7）
    oldest_pending_created: str | None = None
    oldest_processing_created: str | None = None
    for state in _STATES:
        for entry in sorted((root / state).glob("q-*.json")):
            counts[state] += 1
            if state not in ("pending", "processing", "dead"):
                continue
            try:
                item = json.loads(entry.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            created = item.get("created_at")
            if not created:
                continue
            if state == "dead":
                cat = classify_dead_reason(item.get("dead_reason", ""))
                dead_categories[cat] = dead_categories.get(cat, 0) + 1
                sid = item.get("session_id") or "?"
                dead_per_session[sid] = dead_per_session.get(sid, 0) + 1
            elif state == "pending" and (oldest_pending_created is None or created < oldest_pending_created):
                oldest_pending_created = created
            elif state == "processing" and (oldest_processing_created is None or created < oldest_processing_created):
                oldest_processing_created = created
    now = datetime.now().astimezone()
    ages: dict[str, float] = {}
    for key, created in (
        ("oldest_pending_hours", oldest_pending_created),
        ("oldest_processing_hours", oldest_processing_created),
    ):
        if created:
            try:
                ages[key] = round((now - datetime.fromisoformat(created)).total_seconds() / 3600, 2)
            except ValueError:
                ages[key] = -1.0  # 解析失败如实标注（负值=未知，不当 0 冒充新鲜）
    return {
        "queue_root": str(root),
        "counts": counts,
        "dead_total": counts["dead"],
        "dead_categories": dead_categories,
        # D6 死信爆发两维度聚合（与 check_dead_burst 同口径；Owner 0922 诉求可观测半边）
        "max_session_death_chain": max(dead_per_session.values()) if dead_per_session else 0,
        "per_session_top": sorted(dead_per_session.items(), key=lambda kv: -kv[1])[:3],
        **ages,
        "blobs": len(list((root / "blobs").glob("*"))),
        "generated_at": _now_iso(),
    }


def emit_dead_backlog_alert(
    queue_root: str | os.PathLike | None = None,
    *,
    health: dict | None = None,
    registry_path=None,
    now: datetime | None = None,
) -> dict:
    """死信积压超阈告警（drain 收尾事件触发，无常驻轮询）。

    判定：dead_total ≥ THD-ALERT-003（REG-ATH-001，fail-closed 统读）且距上次告警
    ≥ THD-ALERT-004 冷却窗口 → task_board 专 task（T-QUEUE-DEADLETTER，幂等自建）
    打 deadletter 标签（66 号 §6.4 既有通道，list --label deadletter 可查）。

    可观测性链路 fail-open：阈值加载失败/板不可达/状态写失败一律记日志返回 skipped，
    **绝不阻断排空**（宁漏不误，对标 task_board 联动口径）；REG-ATH-001 的 fail-closed
    约束针对核心业务阈值消费（错阈值=错行为），本函数是旁路可观测性，语义分级处理。
    """
    root = resolve_queue_root(queue_root)
    snap = health or queue_health(root)
    result: dict = {"fired": False, "action": "skipped"}
    dead_total = snap.get("dead_total", 0)
    if dead_total <= 0:
        return result
    try:
        from zephyr.shared.alerts.threshold_loader import AlertThresholdConfigError, load_alert_thresholds

        thresholds = load_alert_thresholds(
            {"THD-ALERT-003": "dead_backlog", "THD-ALERT-004": "cooldown_seconds"},
            registry_path=registry_path,
            cast="int",
        )
    except Exception as exc:  # noqa: BLE001 — 阈值不可读=告警链路降级（fail-open，见 docstring）
        logger.warning("[health] 死信积压阈值加载失败，告警跳过（REG-ATH-001 不可达）: %s", exc)
        result["action"] = "threshold_unavailable"
        return result
    if dead_total < thresholds["dead_backlog"]:
        result["action"] = "below_threshold"
        return result
    state_file = root / _HEALTH_ALERT_STATE_FILE
    ref = now or datetime.now().astimezone()
    try:
        last = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}
        last_at = datetime.fromisoformat(last.get("last_alert_at")) if last.get("last_alert_at") else None
        if last_at is not None and (ref - last_at).total_seconds() < thresholds["cooldown_seconds"]:
            result["action"] = "cooldown"
            return result
    except (OSError, ValueError):
        pass  # 状态损坏=视作无冷却历史，放行本次告警
    # task_board 联动（专 task 幂等自建 + deadletter 标签；板不可达仅记日志）
    try:
        from scripts import task_board as tb

        conn = tb._connect(tb._resolve_board_db())
        try:
            if tb._get_task(conn, _DEADLETTER_WATCH_TASK_ID) is None:
                tb.ensure_task(
                    conn,
                    _DEADLETTER_WATCH_TASK_ID,
                    title="提交队列死信积压告警（自动维护勿关闭）",
                    description=(
                        "commit_queue 死信积压超阈挂载点（66 号 §6.4 通道）：dead/ 积压 ≥ "
                        "REG-ATH-001 THD-ALERT-003 时经 tag_dead_letter 打标；处置入口 "
                        "python scripts/commit_queue.py health。"
                    ),
                    actor="commit_queue",
                )
            newest_dead = ""
            try:
                newest = sorted((root / "dead").glob("q-*.json"))[-1]
                newest_dead = newest.stem
            except (OSError, IndexError):
                pass
            reason = (
                f"dead_backlog={dead_total} ≥ threshold={thresholds['dead_backlog']}; "
                f"categories={snap.get('dead_categories')}; "
                f"oldest_pending_hours={snap.get('oldest_pending_hours')}"
            )
            rc = tb.tag_dead_letter(
                conn,
                _DEADLETTER_WATCH_TASK_ID,
                qid=newest_dead or "backlog",
                reason=reason,
                owner="commit_queue",
                actor="commit_queue",
            )
        finally:
            conn.close()
        if rc != 0:
            logger.warning("[health] 死信积压告警打标跳过: rc=%s（任务已完成/metadata 损坏）", rc)
            result["action"] = f"tag_skipped_rc{rc}"
            return result
    except Exception as exc:  # noqa: BLE001 — 板不可达不阻断排空（宁漏不误）
        logger.warning("[health] 死信积压告警 task_board 联动失败（忽略）: %s", exc)
        result["action"] = "board_unreachable"
        return result
    try:
        # P2-6（红队 0922）：合并写——整文件覆盖会踩掉 check_dead_burst 的日期键
        _atomic_write(
            state_file,
            json.dumps(
                {
                    **(last if isinstance(last, dict) else {}),
                    "last_alert_at": ref.isoformat(),
                    "dead_total": dead_total,
                },
                ensure_ascii=False,
            ).encode("utf-8"),
        )
    except OSError as exc:
        logger.warning("[health] 告警冷却状态写入失败（下次可能重复告警）: %s", exc)
    logger.warning("[health] 死信积压告警触发: %s", reason)
    result.update({"fired": True, "action": "alerted", "reason": reason})
    return result


def _dead_burst_aggregate(root: Path, today: str) -> tuple[int, dict[str, int]]:
    """当日死信聚合：返回 (当日新增总数, 各会话当日死亡计数)——只读 dead/。"""
    day_total = 0
    per_session: dict[str, int] = {}
    for entry in sorted((root / "dead").glob("q-*.json")):
        try:
            item = json.loads(entry.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not (item.get("dead_at") or "").startswith(today):
            continue
        day_total += 1
        sid = item.get("session_id") or "?"
        per_session[sid] = per_session.get(sid, 0) + 1
    return day_total, per_session


def _dead_burst_load_thresholds(registry_path=None) -> dict | None:
    """THD-ALERT-005/006 fail-closed 统读；非法/不可读返回 None（fail-open 跳过）。"""
    try:
        from zephyr.shared.alerts.threshold_loader import load_alert_thresholds

        th = load_alert_thresholds(
            {"THD-ALERT-005": "daily_dead_burst", "THD-ALERT-006": "session_dead_chain"},
            registry_path=registry_path,
            cast="int",
        )
    except Exception as exc:  # noqa: BLE001 — 阈值不可读=链路降级（fail-open）
        logger.warning("[health] 死信爆发阈值加载失败，跳过（REG-ATH-001 不可达）: %s", exc)
        return None
    if th["daily_dead_burst"] <= 0 or th["session_dead_chain"] <= 0:
        # P2-7（红队 0922）：value 0 = 配置手误地雷（0 死信也会 fire）——按配置错误跳过
        logger.warning("[health] 死信爆发阈值非法（<=0），跳过（REG-ATH-001 条目需修正）")
        return None
    return th


def _dead_burst_write_ledger(
    root: Path, today: str, day_total: int, top_session: str, top_count: int, types: list[str]
) -> None:
    """堵点本 alert 行（daemon 离线时本路径是唯一记账人；写失败仅记日志）。"""
    ledger = root.parent / "audit" / "bottleneck_ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "ts": time.time(),
                    "kind": "alert",
                    "type": "dead_burst",
                    "date": today,
                    "day_total": day_total,
                    "top_session": top_session,
                    "top_count": top_count,
                    "types": types,
                },
                ensure_ascii=False,
            )
            + chr(10)
        )


def _dead_burst_tag_task_board(root: Path, today: str, reason: str) -> None:
    """task_board T-QUEUE-DEADLETTER 打标（幂等自建；板不可达仅记日志不阻断）。"""
    from scripts import task_board as tb

    conn = tb._connect(tb._resolve_board_db())
    try:
        if tb._get_task(conn, _DEADLETTER_WATCH_TASK_ID) is None:
            tb.ensure_task(
                conn,
                _DEADLETTER_WATCH_TASK_ID,
                title="提交队列死信积压告警（自动维护勿关闭）",
                description="commit_queue 死信爆发/积压统一挂载点（66 号 §6.4 通道）。处置入口：python scripts/commit_queue.py health",
                actor="commit_queue",
            )
        rc = tb.tag_dead_letter(
            conn,
            _DEADLETTER_WATCH_TASK_ID,
            qid=f"burst-{today}",
            reason=reason,
            owner="commit_queue",
            actor="commit_queue",
        )
        if rc != 0:
            logger.warning("[health] 死信爆发打标跳过: rc=%s", rc)
    finally:
        conn.close()


def _dead_burst_pending_types(state_file: Path, today: str, triggered: list[str]) -> tuple[dict, list[str]]:
    """日期键每日一声：读冷却状态，返回 (state, 今日尚未触发过的类型)。"""
    try:
        state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}
    except (OSError, ValueError):
        state = {}
    burst_state = state.get("dead_burst") or {}
    done_types = set(burst_state.get("types") or []) if burst_state.get("date") == today else set()
    return state, [t for t in triggered if t not in done_types]


def check_dead_burst(
    queue_root: str | os.PathLike | None = None,
    *,
    registry_path=None,
    now: datetime | None = None,
) -> dict:
    """死信爆发升级告警（D6=Owner 2026-09-22 显式诉求：285 死/日应当天拉铃而非事后考古）。

    两维度（阈值真源=REG-ATH-001，fail-closed 统读）：THD-ALERT-005 单日死信增量 ≥50；
    THD-ALERT-006 单会话当日死亡 ≥10（requeue 连败链的当日代理口径）。
    防轰炸=日期键每日一声（每类型每天最多一次，跨天自动失效）；通道=堵点本 alert 行
    + task_board 打标。drain 收尾事件触发（lease 外）；fail-open 不阻断排空。
    """
    root = resolve_queue_root(queue_root)
    ref = now or datetime.now().astimezone()
    today = ref.date().isoformat()
    day_total, per_session = _dead_burst_aggregate(root, today)
    th = _dead_burst_load_thresholds(registry_path)
    if th is None:
        return {"fired": False, "action": "threshold_unavailable", "day_total": day_total}
    top_session, top_count = max(per_session.items(), key=lambda kv: kv[1]) if per_session else ("", 0)
    triggered: list[str] = []
    if day_total >= th["daily_dead_burst"]:
        triggered.append("daily_burst")
    if top_count >= th["session_dead_chain"]:
        triggered.append("session_chain")
    if not triggered:
        return {"fired": False, "action": "below_threshold", "day_total": day_total, "top_session": top_session}
    state_file = root / _HEALTH_ALERT_STATE_FILE
    state, pending_types = _dead_burst_pending_types(state_file, today, triggered)
    if not pending_types:
        return {"fired": False, "action": "already_alerted_today", "day_total": day_total}
    reason = (
        f"dead_burst date={today} types={pending_types}: day_total={day_total}"
        f" (>= {th['daily_dead_burst']}) top_session={top_session}({top_count}"
        f" >= {th['session_dead_chain']})"
    )
    try:
        _dead_burst_write_ledger(root, today, day_total, top_session, top_count, pending_types)
    except OSError as exc:  # noqa: BLE001
        logger.warning("[health] 死信爆发堵点本写入失败（忽略）: %s", exc)
    try:
        _dead_burst_tag_task_board(root, today, reason)
    except Exception as exc:  # noqa: BLE001 — 板不可达不阻断排空
        logger.warning("[health] 死信爆发 task_board 联动失败（忽略）: %s", exc)
    try:
        _atomic_write(
            state_file,
            json.dumps(
                {**state, "dead_burst": {"date": today, "types": sorted(set(triggered))}},
                ensure_ascii=False,
            ).encode("utf-8"),
        )
    except OSError as exc:
        logger.warning("[health] 死信爆发冷却状态写入失败（明日可能重复告警）: %s", exc)
    logger.warning("[health] 死信爆发升级告警触发: %s", reason)
    return {"fired": True, "action": "alerted", "types": pending_types, "day_total": day_total, "reason": reason}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read_files_from_worktree(worktree_root: Path, relpaths: list[str]) -> list[tuple[str, bytes]]:
    """CLI 层：从工作区读文件完整内容（66 号 §6.1 v0.4.0：读工作区文件非 git index，
    因工作区是 AI 编辑的最终态）。

    B 段衔接点：读取前 MUST 先 lock_files.py acquire（66 号 §6.1 v0.4.0 编辑期锁协议
    衔接）——A 段未集成（严格限界），由会话纪律层保证；快照落袋本身保数据不丢。
    """
    out: list[tuple[str, bytes]] = []
    for rel in relpaths:
        norm = _validate_relpath(rel)  # 轻检前置：CLI 读盘前就拦穿越（不读越界文件）
        abs_path = worktree_root / norm
        try:
            content = abs_path.read_bytes()
        except OSError as exc:
            raise QueueReject(f"文件读取失败: {norm}（{exc}）") from exc
        out.append((norm, content))
    return out


def _cmd_enqueue(args: argparse.Namespace) -> int:
    worktree_root = Path(args.worktree_root) if args.worktree_root else Path.cwd()
    message = args.message
    if args.message_file:
        try:
            # --message-file：UTF-8 读入（PowerShell 管道传中文必毁编码教训，66 号 §6.3 修正 3）
            message = Path(args.message_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: message-file 读取失败: {exc}", file=sys.stderr)
            return 1
    files_arg = [f.strip() for f in (args.files or "").split(",") if f.strip()]
    if args.files_file:
        try:
            # --files-file：一行一路径（UTF-8）；逗号分隔无法承载含逗号文件名（2026-09-13 C4 数据批发现）
            for line in Path(args.files_file).read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    files_arg.append(line)
        except OSError as exc:
            print(f"ERROR: files-file 读取失败: {exc}", file=sys.stderr)
            return 1
    if not files_arg:
        print("DENIED: 空文件清单拒绝入队（--files 必填）", file=sys.stderr)
        return 2
    try:
        files = _read_files_from_worktree(worktree_root, files_arg)
        depends_on = [d.strip() for d in (args.depends_on or "").split(",") if d.strip()]
        item = enqueue_item(
            args.session,
            message or "",
            files,
            queue_root=args.queue_root,
            options=EnqueueOptions(base_head=args.base_head, depends_on=depends_on or None),
        )
    except QueueReject as exc:
        # fail-closed：报错非静默（66 号 §11 #3：畸形项全拦且报错非静默）
        print(f"DENIED: {exc}", file=sys.stderr)
        return 2
    print(f"ENQUEUED: {item['qid']} (files={len(item['files'])}, supersedes={item['meta']['supersedes']})")
    if not args.no_bootstrap:
        result = try_bootstrap_drain(args.queue_root)  # 入队自举排空（66 号 §8）
        if not result.get("skipped"):
            print(f"DRAIN: done={result['done']} dead={result['dead']} recovered={result['recovered']}")
        else:
            print("DRAIN: skipped（另一 Serializer 持 lease，等下次自举）")
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    if not args.no_bootstrap:
        try_bootstrap_drain(args.queue_root)  # 66 号 §6.6：status 调用本身触发一次排空尝试
    report = queue_status(args.queue_root, session_id=args.session)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _purge_poisoned_scripts_package() -> None:
    """清除 sys.modules 中被外来同名命名空间包占据的 `scripts` 族缓存（毒缓存防护）。

    病根（2026-09-11 直跑 drain 实证）：pywin32 的 .pth 把 site-packages/win32 注入
    sys.path，其 scripts/ 子目录可被裸 `import scripts` 解析为**命名空间包**；直跑时
    main() 首选 `from scripts.ops_guard import ...`（此时 repo 根已在 path，正常解析真包，
    不触发）——但任何早于真包解析的 `import scripts`（外来工具链/PYTHONPATH 异常态）
    一旦命中 win32 命名空间，sys.modules['scripts'] 即被缓存，**事后补插 sys.path 无法
    翻转**（submodule 搜索走已缓存 __path__，scripts.governance 永久不可达 → CLI drain
    ModuleNotFoundError）。按 __path__ 是否含本仓 scripts/ 判定毒缓存，命中则整族清除
    （下一条 import 语句按已修正的 sys.path 重新解析真包）。
    """
    import sys as _sys

    _scripts_dir = str(Path(__file__).resolve().parent)
    _pkg = _sys.modules.get("scripts")
    if _pkg is not None and _scripts_dir not in (getattr(_pkg, "__path__", None) or ()):
        for _name in [n for n in list(_sys.modules) if n == "scripts" or n.startswith("scripts.")]:
            del _sys.modules[_name]


def _cmd_drain(args: argparse.Namespace) -> int:
    # 2026-09-10 治本（死信事故排查第二处缺口）：CLI drain MUST 接真 landing——
    # A 段默认桩=标记 done 不真提交，对真实队列是"假 done 丢内容"footgun；
    # B 段真落地在 bootstrap_drain_with_landing，但 CLI drain 一直没回接。
    # 延迟 import 防循环；直跑场景（sys.path[0]=scripts/）补 repo 根防 scripts.governance 不可达。
    import sys as _sys

    _repo_root_str = str(Path(__file__).resolve().parents[1])
    if _repo_root_str not in _sys.path:
        _sys.path.insert(0, _repo_root_str)
    _purge_poisoned_scripts_package()
    from scripts.governance.commit_queue_landing import WorktreeLanding  # noqa: PLC0415

    landing = WorktreeLanding(repo_root=_REPO_ROOT, queue_root=args.queue_root)
    try:
        result = drain_queue(
            args.queue_root, landing=landing, max_items=args.max_items, done_ttl_days=args.done_ttl_days
        )
    except LeaseUnavailable as exc:
        # 显式 drain 拿不到 lease = 另一 Serializer 在排空——正常路径非错误（66 号 §8）
        print(f"SKIPPED: {exc}")
        return 0
    print(
        f"DRAIN: done={result['done']} dead={result['dead']} "
        f"recovered={result['recovered']} qids={result['processed_qids']} "
        f"stale_cleared={result['stale_cleared']} cascade_marked={result['cascade_marked']} "
        f"done_cleaned={result['done_cleaned']}"
    )
    return 0


def _cmd_requeue(args: argparse.Namespace) -> int:
    message = args.message
    if args.message_file:
        try:
            # --message-file：UTF-8 读入（与 enqueue 同款，66 号 §6.3 修正 3）
            message = Path(args.message_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: message-file 读取失败: {exc}", file=sys.stderr)
            return 1
    try:
        result = requeue_dead_item(
            args.qid,
            queue_root=args.queue_root,
            worktree_root=args.worktree_root,
            session_id=args.session,
            message=message,
            base_head=args.base_head,
            from_bag=args.from_bag,
        )
    except RequeueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except QueueReject as exc:
        # 新项入队轻检拒绝——fail-closed 报错非静默（与 enqueue 同口径）
        print(f"DENIED: {exc}", file=sys.stderr)
        return 2
    src = "死信原快照" if args.from_bag else "当前工作区"
    print(f"REQUEUED: {result['old_qid']} -> {result['new_qid']}（快照来源={src}，新 qid 排 FIFO 队尾）")
    if not args.no_bootstrap:
        drain_result = try_bootstrap_drain(args.queue_root)  # 重入队自举排空（66 号 §8）
        if not drain_result.get("skipped"):
            print(
                f"DRAIN: done={drain_result['done']} dead={drain_result['dead']} recovered={drain_result['recovered']}"
            )
        else:
            print("DRAIN: skipped（另一 Serializer 持 lease，等下次自举）")
    return 0


def _cmd_cleanup(args: argparse.Namespace) -> int:
    result = cleanup_done(args.queue_root, ttl_days=args.done_ttl_days)
    print(f"CLEANUP: removed={len(result['removed'])} kept={result['kept']}（done/ 超 TTL 项已清理；dead/ 永不清理）")
    return 0


def _cmd_health(args: argparse.Namespace) -> int:
    snap = queue_health(args.queue_root)
    print(json.dumps(snap, ensure_ascii=False, indent=2))
    if args.no_alert:
        return 0
    alert = emit_dead_backlog_alert(args.queue_root, health=snap)
    print(f"ALERT: {json.dumps(alert, ensure_ascii=False)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # CAND-GOVSEC-001 ② 翻硬拦（批5b，2026-08-26）：观测期零误伤，队列 CLI（含
    # drain 排空路径）in-process 删除护栏转正硬拦。landing 侧 safe_rmtree 硬断言
    # 授权通道直通，裸删除命中保护区即拦。失败静默降级，不阻断队列主链路。
    try:
        try:
            from scripts.ops_guard import install_inprocess_enforcement
        except ImportError:  # python scripts/commit_queue.py 直跑：sys.path[0]=scripts/
            from ops_guard import install_inprocess_enforcement
        install_inprocess_enforcement()
    except Exception:  # noqa: BLE001 — 护栏装配失败永不阻断队列主链路
        pass

    parser = argparse.ArgumentParser(
        prog="commit_queue.py",
        description="提交队列串行化 MVP（66 号 §6 协议）：enqueue/status/drain",
    )
    parser.add_argument(
        "--queue-root", default=None, help=f"队列根（默认 {_QUEUE_DIR_DEFAULT}；环境变量 {QUEUE_ENV_VAR} 可覆盖）"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_enq = sub.add_parser("enqueue", help="快照入队即返回（入袋即完成）")
    p_enq.add_argument("--session", required=True, help="生产者会话 ID（[A-Za-z0-9._-] ≤64）")
    p_enq.add_argument("--files", required=False, help="仓内相对路径逗号分隔（正斜杠）")
    p_enq.add_argument(
        "--files-file",
        default=None,
        help="文件清单文件（UTF-8，一行一路径；文件名含逗号时用，与 --files 二选一同时给出则合并）",
    )
    p_enq.add_argument("--message", default=None, help="commit message（内联）")
    p_enq.add_argument("--message-file", default=None, help="commit message 文件（UTF-8，中文推荐）")
    p_enq.add_argument("--worktree-root", default=None, help="工作区根（默认 cwd）")
    p_enq.add_argument("--base-head", default=None, help="入队时目标分支 HEAD（A 段显式传入，B 段自动取）")
    p_enq.add_argument(
        "--depends-on",
        default=None,
        help="依赖的前置 qid 逗号分隔（P1 起 drain 级联标记生效：前置项落盘后本项标 stale 重校验基底，66 号 §6.4）",
    )
    p_enq.add_argument("--no-bootstrap", action="store_true", help="入队后不尝试自举排空")
    p_enq.set_defaults(func=_cmd_enqueue)

    p_st = sub.add_parser("status", help="队列状态（触发一次排空尝试）")
    p_st.add_argument("--session", default=None, help="按会话过滤")
    p_st.add_argument("--no-bootstrap", action="store_true", help="不触发排空尝试")
    p_st.set_defaults(func=_cmd_status)

    p_dr = sub.add_parser("drain", help="显式排空（拿不到 lease 则跳过 exit 0）")
    p_dr.add_argument("--max-items", type=int, default=None, help="本轮最多处理项数")
    p_dr.add_argument(
        "--done-ttl-days",
        type=float,
        default=_DONE_TTL_DAYS_DEFAULT,
        help=f"done/ TTL 天数（默认 {_DONE_TTL_DAYS_DEFAULT:.0f}；dead/ 永不清理）",
    )
    p_dr.set_defaults(func=_cmd_drain)

    p_rq = sub.add_parser("requeue", help="死信取回重入队（66 号 §6.4：基于当前工作区重建快照，新 qid 排 FIFO 队尾）")
    p_rq.add_argument("qid", help="dead/ 中的死信项 qid")
    p_rq.add_argument("--worktree-root", default=None, help="工作区根（默认 cwd）——快照重建内容来源")
    p_rq.add_argument(
        "--from-bag",
        action="store_true",
        help="从死信原快照（blob 袋 sha256 自校验）取回而非当前工作区——工作区漂移免疫",
    )
    p_rq.add_argument("--session", default=None, help="新项会话 ID（默认沿用原死信项 session_id）")
    p_rq.add_argument("--message", default=None, help="commit message（默认沿用原死信项 message）")
    p_rq.add_argument("--message-file", default=None, help="commit message 文件（UTF-8，中文推荐）")
    p_rq.add_argument("--base-head", default=None, help="新项 base_head（默认 None，由调用方/B 段填充）")
    p_rq.add_argument("--no-bootstrap", action="store_true", help="重入队后不尝试自举排空")
    p_rq.set_defaults(func=_cmd_requeue)

    p_cl = sub.add_parser("cleanup", help=f"done/ TTL 清理（默认 {_DONE_TTL_DAYS_DEFAULT:.0f} 天；dead/ 永不清理）")
    p_cl.add_argument("--done-ttl-days", type=float, default=_DONE_TTL_DAYS_DEFAULT, help="done/ 保留天数")
    p_cl.set_defaults(func=_cmd_cleanup)

    p_hl = sub.add_parser(
        "health",
        help="队列健康快照（只读不排空：四态计数/死因分类/最老项龄；死信积压告警同源聚合）",
    )
    p_hl.add_argument("--no-alert", action="store_true", help="只打印快照，不执行积压告警判定")
    p_hl.set_defaults(func=_cmd_health)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
