# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §
# [MODULE] scripts.commit_queue
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；zephyr.shared.infra.process_pool.is_pid_alive（僵尸 PID 检测真源唯一）
# [CONSUMERS] 全部 AI session（提交入队唯一入口）；B 段 Serializer 落盘执行体（专用 worktree 真落盘）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 单写者（serializer.lease 唯一持有者排空）；纯 FIFO（qid 单调序，无优先级插队）；快照入袋即安全（blob 落盘即完成）；死信不卡队；同键 (session_id,path) pending 内仅留最新；C1 同会话短窗合批仅同 session+同 worktree-root（文件集并集不变，absorbed qid 不落状态目录）；永不改主工作区文件
# [MODIFY-GUARD] 66 号备忘 §6 协议/schema 真源；08 号文 §4.2 Phase 0；CLI 子命令面（enqueue/status/drain）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功（含 drain 拿不到 lease 跳过）; exit 1=参数/IO 错误（含 requeue 取回失败）; exit 2=入队轻检拒绝(DENIED)
# [TESTS] tests/governance/test_commit_queue.py; tests/governance/test_enqueue_preflight.py
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
  dead/         死信（含 dead_reason/dead_at；永不自动清理，66 号 §8；
                人工 dead-archive 归档除外——mv 非删，RB2）
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
      [--priority N] [--queue-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py status [--session S] [--queue-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py drain [--queue-root DIR] [--max-items N]
  python scripts/commit_queue.py requeue <qid> [--worktree-root DIR] [--no-bootstrap]
  python scripts/commit_queue.py cleanup [--done-ttl-days N]
  python scripts/commit_queue.py dead-archive [--days N] [--no-verify-landed] [--execute] [--json]
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
description: 提交队列串行化 MVP（enqueue/status/drain/requeue/cleanup/dead-archive/health + 入队自举排空 + 死信 + compaction + 级联标记 + done/ TTL 清理 + 死信积压告警 + C1 同会话短窗自动合批）
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
from collections.abc import Callable
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

_DONE_TTL_DAYS_DEFAULT = (
    7.0  # 66 号 §12 Q3 已闭环：done 保留 7 天 TTL；dead 永不自动清理（人工 dead-archive 归档除外，RB2：mv 非删）
)

# ---------------------------------------------------------------------------
# B5 attempts 计数+退避（st-commitspeed-tbl-20260924 止血，B4 排队键 docstring 登记
# 的残留风险本件落地）：毒药件（反复落地失败退回 pending）保留原 created_at 居队首，
# 每轮自举白耗一次 landing+终止整轮（实测 09-24 主区 HEAD 零推进 52 分钟即该形态）。
# 调度面三件：①重试退回 pending 前 attempts+1 持久化在项文件；②attempts≥
# _ATTEMPTS_BACKOFF_THRESHOLD 在 _pick_head 排序键加惩罚（延迟可拾取，复用
# (created_at,qid) 排序）；③attempts≥_ATTEMPTS_DEAD_THRESHOLD 拾取即死信
# （dead_reason=attempts_exhausted 附末次失败原因，三分类随末次原因走——env 失败
# 仍归 env 可 requeue）。不改门禁判据/退出码语义；只动队列调度面。
# 开关：env _ATTEMPTS_BACKOFF_ENV（默认 ON；"0"/"false"=关闭回退现行为）。登记锚=
# config/flags.yaml `commit_queue_attempts_backoff`（本脚本零 yaml 依赖，代码只读 env）。
# ---------------------------------------------------------------------------
_ATTEMPTS_FIELD = "attempts"  # 项 JSON 字段：累计落地失败退回次数（终态留档可追溯）
_ATTEMPTS_BACKOFF_THRESHOLD = 3  # attempts≥3 排队键退避（惩罚单调递增）
_ATTEMPTS_DEAD_THRESHOLD = 5  # attempts≥5 拾取即死信（不再白耗 landing）
_ATTEMPTS_BACKOFF_PENALTY_SECONDS = 900.0  # 退避惩罚步长 15min/超限次
_ATTEMPTS_BACKOFF_ENV = "ZEPHYR_CQ_ATTEMPTS_BACKOFF"  # 覆盖位（先例：QUEUE_ENV_VAR）

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
    "快照自洽见证",
    "TRACKED-DRIFT-READONLY",
    "网关落盘失败",
    # QCure M3.3 标记表补族（st-qcure-20260925）：落地侧已产生但三分类归 other 的盲区——
    # 死因族真源与处方映射见 _DEAD_PRESCRIPTIONS（同 commit 原子补齐，勿只改一处）。
    "三向合并失败",  # 注册表三向合并 fail-closed（commit_queue_landing 注册表合并口）
    "身份键重复",  # 注册表身份键碰撞（module_id/step_id 类）
    "基底不可知",  # BASE-UNKNOWN：base_head/base_blob 缺失无法判定快进
    "BASE-UNKNOWN",
    "快照未真应用",
    "冲突标记",  # 快照含未解决合并冲突标记（入队口 M2.2 预扫同源判据）
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
# C1 同会话短窗自动合批（st-commitspeed-tbl-20260924 提速战役 T11/C1；A4 阶梯 S7
# 「批均规模 ≥3」的前置编排档）：同一会话 <20 分钟窗口内的后续入队件并入已有
# pending 件（文件集取并集，零内容改动、纯队列编排），判据口径=件数/日 158→<60、
# 文件中位/件 1→>5。
# 红线：合批只对「同 session_id + 同 worktree-root」生效（跨会话绝不合并；历史项
# 无 worktree_root 键=不可证同根→不并）；门禁判据/阈值零变化；B4 created_at 排队
# 键不破（合并件保持前件 created_at=先来先服务）。
# 机制复用（勿造第二套）：吸收痕迹记 meta.supersedes——与 compaction 同一名册，语义
# 统一为「本件吸收/覆盖的提交序列号全集」，compaction 的传递累积链路原样复用；另记
# meta.absorbed 明细（qid/时刻/文件数/message 尾注）+ meta.merged_count 供审计。
# 资格闸（全部命中才合并，宁不并不错并）：同 session + 同 worktree_root +
# created_at 距今 ≤ _DEBOUNCE_WINDOW_SECONDS + 目标无 stale 标记 + 目标
# attempts=0（B5 失败退回件不吸收，不拖新内容陪葬）+ 任一侧无 depends_on（显式
# 依赖链是调用方编排）+ lane 相同（interactive/machine 不混）+ task_id 相同（死信
# 打标归属不串）+ base_head 相同（None==None 可；基底不同则重校验/注册表合并口径
# 不一致）+ 合并后条目数 ≤ _MAX_BATCH_FILES（R2 大批硬顶不因合批而破；machine
# 车道与 allow_oversize_batch 豁免与 enqueue 主口径一致）。
# 并发安全：rename 原子认领（target → *.merging-<pid>-<tid>，后缀不匹配 q-*.json
# glob，drain/compaction/status 恒不可见）→ 独占期内重验资格 → 并集回写 → 摘除
# claim；认领失败（已被 drain 取走/并发竞争）＝放弃合并走正常新建（宁不并不丢件）；
# 回写失败恢复原位（claim 原字节 O_EXCL 重建兜底）——absorbed qid 永不落任何状态
# 目录（它是消耗的序列号，不是队列项）。
# 开关：env _C1_DEBOUNCE_ENV（默认 ON；"0"/"false"=关闭回退现行为）。登记锚=
# config/flags.yaml `commit_queue_c1_debounce`（B5 同款：本脚本零 yaml 依赖，
# 代码只读 env）。
# ---------------------------------------------------------------------------
_DEBOUNCE_WINDOW_SECONDS = 1200.0  # 20 分钟短窗（T11/C1 任务口径）
_C1_DEBOUNCE_ENV = "ZEPHYR_CQ_C1_DEBOUNCE"  # 覆盖位（先例：_ATTEMPTS_BACKOFF_ENV）
_ABSORBED_MESSAGE_TAIL_CHARS = 500  # absorbed 明细 message 尾注截断（项文件体积卫生）


@dataclass(frozen=True)
class _C1Incoming:
    """C1 合批来件束（NO-LONG-PARAM-LIST/§5.150 合规：合并判据与载荷单一参数对象）。"""

    session_id: str
    worktree_root: str  # 已归一化（_normalize_worktree_root）
    base_head: str | None
    incoming_meta: dict  # 来件 meta_extra（lane/task_id 判据取自此）
    allow_oversize: bool
    now_ts: float
    qid: str  # 为来件分配的 qid（吸收成功=被消耗的序列号，不落任何状态目录）
    entries: list[dict]  # blob 条目（files+deletes 通道合一）
    message: str

    @property
    def entries_count(self) -> int:
        return len(self.entries)


def _c1_debounce_enabled() -> bool:
    """C1 合批总开关：env 覆盖位缺省 ON（"0"/"false"/"off"/"no"=关闭回退现行为）。"""
    raw = os.environ.get(_C1_DEBOUNCE_ENV, "").strip().lower()
    return raw not in ("0", "false", "off", "no")


def _normalize_worktree_root(value: str | os.PathLike | None) -> str:
    """worktree-root 归一化（normpath+normcase）：盘符大小写/斜杠方向差异不拆同根。"""
    return os.path.normcase(os.path.normpath(str(value or "")))


def _c1_target_meta_ok(meta: dict, incoming: _C1Incoming) -> bool:
    """目标 meta 资格子闸（§5.158 复杂度合规拆分）：stale/depends_on/worktree/lane/task_id。"""
    if meta.get("stale"):
        return False  # 级联失效件命运未定（重校验/死信候选），不吸收新内容
    if meta.get("depends_on"):
        return False  # 目标在显式依赖链上——吸收会拖新文件陪绑前置项
    if _normalize_worktree_root(meta.get("worktree_root")) != incoming.worktree_root:
        return False  # 跨 worktree 不合并（红线）；历史项无此键=不可证同根→不并
    if _item_lane({"meta": meta}) != _item_lane({"meta": incoming.incoming_meta}):
        return False  # 车道不混（interactive/machine 调度优先语义不被合并改写）
    if _item_priority({"meta": meta}) != _item_priority({"meta": incoming.incoming_meta}):
        return False  # Rx-5：优先级不混（出队主键不被合并改写，同 lane 判据；缺省 0 两侧恒等）
    return meta.get("task_id") == incoming.incoming_meta.get("task_id")  # 死信打标归属不串


def _is_c1_merge_target(item: dict, incoming: _C1Incoming) -> bool:
    """C1 合批目标资格闸（扫描与认领后重验共用同一判据——禁两套判据）。"""
    if item.get("session_id") != incoming.session_id:
        return False  # 跨会话绝不合并（红线）
    if not _c1_target_meta_ok(item.get("meta") or {}, incoming):
        return False
    if _item_attempts(item):
        return False  # B5 失败退回件不吸收——不拖新内容陪葬
    if (item.get("base_head") or None) != (incoming.base_head or None):
        return False  # 基底不同：重校验/注册表三向合并口径不一致，不并
    created = item.get("created_at")
    if not created:
        return False
    try:
        age = incoming.now_ts - datetime.fromisoformat(str(created)).timestamp()
    except (TypeError, ValueError):
        return False
    if age > _DEBOUNCE_WINDOW_SECONDS:
        return False  # 短窗外（创建于 >20 分钟前）不合
    combined = len(item.get("files") or []) + incoming.entries_count
    if combined > _MAX_BATCH_FILES and not (incoming.allow_oversize or _item_lane(item) == "machine"):
        return False  # R2 大批硬顶不因合批而破
    return True


def _c1_apply_absorb(item: dict, incoming: _C1Incoming) -> None:
    """把来件并集写入目标项内存体（调用方负责原子写回；同路径后件胜）。"""
    meta = item.setdefault("meta", {})
    by_path = {f.get("path"): f for f in item.get("files") or []}
    for entry in incoming.entries:
        by_path[entry["path"]] = entry  # 同路径后件胜（快照=完整内容最终态，66 号 §4 裁定 2）
    item["files"] = list(by_path.values())
    meta["supersedes"] = list(dict.fromkeys((meta.get("supersedes") or []) + [incoming.qid]))
    meta["absorbed"] = list(meta.get("absorbed") or []) + [
        {
            "qid": incoming.qid,
            "at": _now_iso(),
            "files": len(incoming.entries),
            "message": (incoming.message or "")[:_ABSORBED_MESSAGE_TAIL_CHARS],
        }
    ]
    meta["merged_count"] = len(meta["absorbed"])
    item["message"] = f"{item.get('message') or ''}\n\n[C1合批+{incoming.qid}] {incoming.message}"


def _c1_finalize_claim(claim: Path, target_path: Path, written: bool) -> None:
    """认领收尾：成功摘除 claim；失败恢复原位（claim 原字节 O_EXCL 重建兜底）。"""
    if written:
        try:
            claim.unlink()
        except OSError:
            pass  # 残留 claim 名不匹配 q-*.json glob，无害留痕（下轮 cleanup 可查）
        return
    try:
        os.rename(claim, target_path)
        return
    except OSError:
        pass  # 双失败兜底：从 claim 原字节重建原位（内容不丢——blob 在袋+原文在 claim）
    try:
        _create_item_excl(target_path, claim.read_bytes())
        claim.unlink()
    except OSError:
        logger.error("[c1] 合并回滚失败，原项滞留 claim 名暂不可见需人工: %s", claim.name)


def _try_c1_absorb(root: Path, incoming: _C1Incoming) -> dict | None:
    """扫描 pending 找 C1 合批目标并吸收；无目标/竞争失败返回 None（调用方走正常新建）。

    返回合并后的目标项 dict（已写回 pending）；调用方据此以 absorbed qid 出回执。
    """
    pending_dir = root / "pending"
    target_path: Path | None = None
    for candidate in sorted(pending_dir.glob("q-*.json")):  # qid 序≈同会话到达序：取最老合格件
        try:
            item = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # 写入窗口或损坏——跳过不碰（同 _compact_pending 读者容错口径）
        # 矿③ 双读：影子 stale 件同旧位口径不具合批资格（_c1_target_meta_ok 读 meta.stale）
        item = _merge_stale_view(candidate, item)
        if _is_c1_merge_target(item, incoming):
            target_path = candidate
            break
    if target_path is None:
        return None
    # rename 原子认领：独占期内 target 对 drain/compaction/status 不可见
    # （claim 后缀不匹配 q-*.json glob）；认领失败=已被取走/竞争——放弃合并走正常新建。
    claim = target_path.with_name(target_path.name + f".merging-{os.getpid()}-{threading.get_ident()}")
    try:
        os.rename(target_path, claim)
    except OSError:
        return None
    written = False
    result: dict | None = None
    try:
        item: dict | None = None
        try:
            item = json.loads(claim.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            item = None  # 认领后读取失败（异常损坏）——恢复原位，走正常新建
        # 独占期内重验资格（读-认领窗口内状态可能被级联标记/B5 退回改写——同判据复用）
        if item is not None and _is_c1_merge_target(item, incoming):
            _c1_apply_absorb(item, incoming)
            _atomic_write(target_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
            written = True
            result = item
    finally:
        _c1_finalize_claim(claim, target_path, written)
    return result


# ---------------------------------------------------------------------------
# enqueue（快照入袋即返回——防内容丢失的核心语义，66 号 §6.1「快照即落袋」）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnqueueOptions:
    """enqueue 可选参数束（NO-LONG-PARAM-LIST 合规收口，§5.150：>7 参数反模式）。

    base_head : 入队时观察到的目标分支 HEAD（A 段不主动取 git，由调用方显式传入；
        B 段落盘接通后用于 §6.4 逐文件快进/冲突判定）。
    base_blobs : 逐路径基底 blob sha（仓内相对路径 → base_head 树上的 git blob sha；
        新增件值为 None 或键缺席）。F-AUDIT-QUEUE-04 治本：`enqueue_item` 保持零 git
        依赖（§6.1 刻意出入 #3 不破），git 取数由调用方经
        `commit_queue_landing.resolve_base_blobs` 完成后经此入参落袋——此前 base_blob
        全仓无填充点，§6.4 陈旧基底重校验（_revalidate_stale_base）恒走
        `if not base_blob: continue`＝结构空转。
    depends_on : meta.depends_on 预留字段（A 段只做 schema 预留，不实现级联逻辑）。
    deletes : 删除路径列表（B 段新增，66 号 §6.1 action=delete 语义细化）：已跟踪但
        盘上缺失的文件经此通道入袋，落盘时从 dev 树删除；与 files 共享同键 compaction。
    meta_extra : 附加 meta 键值（并入队列项 meta）。
    allow_oversize_batch : 超大批逃生旗（R2，meta 留痕）：确属原子大批（如整目录
        归档迁移）时由调用方显式给出——旗是必需品不是装饰（q-0007「gate+自家测试
        同批合法」先例）。
    worktree_root : 入队来源工作区根（C1 合批判据键，meta.worktree_root 落袋）。
        C1 同会话短窗合批只对「同 session + 同 worktree_root」生效（红线：跨会话/
        跨 worktree 绝不合并）；None=不做合批（gateway 直调等历史调用方行为不变）。
    preflight_root : 声明式预检根（波 1B 包 1.7 防绕过，st-zc9-lane-r1）：显式声明
        且为 git 工作区（.git 实存）时，直调 enqueue_item 也必经与裸 CLI 同一道权威
        入队预检（run_enqueue_preflight 锁外只读；blocking→QueueReject）——直调旁路
        投注定死信件在入队口快败。None=不扫（tmp 隔离测试与 API 直调零变更，向后兼容）。
    enqueue_preflight : "skip"=唯一合法逃生位（调用方声明已在上游自跑预检，landing
        reroute 通道用）；其余值按未声明处理。skip 必须与 preflight_root 同给才生效面。
    """

    base_head: str | None = None
    base_blobs: dict | None = None
    depends_on: list[str] | None = None
    deletes: list[str] | None = None
    meta_extra: dict | None = None
    allow_oversize_batch: bool = False
    worktree_root: str | None = None
    preflight_root: str | None = None
    enqueue_preflight: str | None = None


# 登记三族内联判定的适用扩展名（CREATE-GUARD 新文件面 ∪ TRANSLATION-COVERAGE .py 面
# ∪ TTL-METADATA frontmatter 面的并集）——袋内无一命中时判定可零 git 面跳过（快路径）。
_REGISTRATION_GATE_EXTENSIONS = (".py", ".yaml", ".md", ".sh", ".ps1", ".mmd", ".json")


def _run_registration_gate(
    project_root: Path,
    files: list[str],
    session_id: str,
    message: str,
    *,
    audit_event: str,
) -> tuple[list[str], list[str], dict]:
    """登记三族内联判定入口（C-1/C-2 同一真源；调用方=enqueue_item 与 requeue_dead_item）。

    - project_root：判据的落地面=「声明的工作区」——enqueue_item 用 opts.worktree_root
      （缺省回退 cwd，覆盖 E-3 直接 import enqueue_item 的裸调用方，mapbuild 四件实证
      其 meta 裸无 options）；requeue 用重建快照来源工作区。判据读的是该盘面（入队
      语义下盘上内容=快照内容，git_commit.py 797-799 既有论证）；root 无 .git（tmp
      隔离测试/非仓目录）⇒ 无 HEAD 面可仿真，整体跳过（fail-open，与
      run_enqueue_preflight 在非仓目录的 degraded 同口径）。
    - 差量级：只跑登记三族（CREATE-GUARD/TTL-METADATA/TRANSLATION-COVERAGE），非
      36s 全门重放；袋内扩展名全不在族面时零 git 面直接放行。
    - 队列层零 git/零 governance 顶层依赖（66 号 §6.1 刻意出入 #3 同款）：延迟 import，
      设施任何故障在 run_registration_inline_checks 内降级为空 findings（「预检非新
      权威」不变——权威执行仍在落地锁内）。
    """
    if not (project_root / ".git").exists():
        return [], [], {}
    family_paths = [p for p in files if str(p).endswith(_REGISTRATION_GATE_EXTENSIONS) and not p.startswith("tests/")]
    if not family_paths:
        return [], [], {}

    from zephyr.gov_enforcement.rule_bridge.commit_preflight import (  # noqa: PLC0415
        run_registration_inline_checks,
    )

    # 袋内路径=仓相对；预检查件的输入口径=绝对路径清单（_rel_of 统一转回仓相对，
    # 与 CLI 面 run_enqueue_preflight 收到的绝对清单同构）。
    absolute_paths = [str(project_root / p) for p in family_paths]
    return run_registration_inline_checks(
        project_root,
        absolute_paths,
        session_id,
        commit_message=message,
        audit_event=audit_event,
    )


def _run_declared_preflight(
    session_id: str, message: str, files: list[tuple[str, bytes]], opts: EnqueueOptions
) -> None:
    """声明式防绕过（波 1B 包 1.7，st-zc9-lane-r1）：preflight_root 显式声明且为 git
    工作区（.git 实存）时，直调 enqueue_item 与裸 CLI 走同一道权威入队预检。

    判据（tests/governance/test_enqueue_preflight_bypass_canary 四尺）：
    - 未声明 preflight_root / 根非 git 工作区 ⇒ 不扫（tmp 隔离测试与 API 直调零变更）；
    - enqueue_preflight="skip" =唯一合法逃生位（调用方声明已在上游自跑预检）；
    - blocking ⇒ QueueReject（逐门禁处方随报错），袋不落 pending——直调旁路投注定
      死信件在入队口快败，无处可绕（enqueue_item / requeue / 裸 CLI 三通道同闸）。
    预检本体零写副作用（ruff 只读+gate 锁外只读；设施故障 fail-open 与 CLI 口径同源）。
    """
    if (opts.enqueue_preflight or "").strip().lower() == "skip":
        return
    declared = opts.preflight_root
    if not declared:
        return
    root_path = Path(declared)
    if not (root_path / ".git").exists():
        return  # 非 git 工作区不扫（与 CLI 面 run_enqueue_preflight 预检根判据同口径）
    from scripts.governance.enqueue_preflight import run_enqueue_preflight  # noqa: PLC0415

    prescription = run_enqueue_preflight(
        root_path,
        [p for p, _ in files],
        session_id,
        message or "",
    )
    if prescription:
        raise QueueReject(prescription)


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
    options : 可选参数束（base_head/depends_on/deletes/meta_extra/worktree_root），
        见 EnqueueOptions。

    返回：落袋的队列项 dict（含 qid）。C1 合批发生时返回合并后的目标项（qid=前件），
        附 absorbed={qid, files}（被吸收提交的序列号与文件数；该 qid 不落任何状态目录）。
    异常：QueueReject（轻检拒绝，fail-closed 报错非静默）。

    并发安全（66 号 §6.1 v0.4.0 结论）：多会话同时 enqueue 各自 {qid}.json 独立文件，
    无共享写状态；同会话内经进程内 session 锁串行（seq 递增 + compaction 在同一
    关键段），跨进程同会话由 O_EXCL 碰撞重试兜底唯一性。
    """
    opts = options or EnqueueOptions()
    base_head = opts.base_head
    base_blobs = opts.base_blobs or {}
    depends_on = opts.depends_on
    deletes = opts.deletes
    meta_extra = opts.meta_extra
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    _validate_session_id(session_id)
    msg = _validate_message(message)
    if not files and not deletes:
        raise QueueReject("空文件清单拒绝入队")
    # 波 1B 包 1.7 声明式防绕过：直调通道与裸 CLI 同一道权威预检（先于 C-1 内联判定，
    # 被拦件连 pending 都不进——见 _run_declared_preflight 判据四尺）。
    _run_declared_preflight(session_id, msg, files, opts)
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

    # C-1 登记三族内联强制（chain_fullflow mine_door_registration_completion §3.7-(ii)/§8）：
    # 第四裸入口（直接 import enqueue_item 的脚本化入队，E-3 mapbuild 四件 audit 零记录
    # 实证）在此结构性补口——任何调用方都无法绕过本点。判据落地面=声明工作区（缺省
    # cwd）；设施故障 fail-open（degraded 留 meta，不产生拒绝）。拒绝文案含逐门禁处方；
    # 放行证据随袋（registration_gate 摘要 + preflight_face 面貌快照，E-4 TOCTOU 比对
    # 素材），放行面不写文件审计（防锁外高频 jsonl 写放大）。
    _pf_root = Path(opts.worktree_root) if opts.worktree_root else Path.cwd()
    _pf_findings, _pf_degraded, _pf_face = _run_registration_gate(
        _pf_root, [p for p, _ in files], session_id, msg, audit_event="enqueue_api"
    )
    if _pf_findings:
        raise QueueReject(
            "登记三族入队预检拦截（C-1：直接调用 enqueue_item 与 CLI 正门同判据，"
            "注定死信的单子在入队口快败）——逐门禁处方：\n" + "\n".join(_pf_findings)
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
                "base_blob": base_blobs.get(norm),  # B 段填充接通（QUEUE-04）：调用方经
                # resolve_base_blobs 取 base_head 树上的 git blob sha 入袋；None=该路径在
                # 基底不存在（新增件）。id 空间与 _pool_head_reader 的 rev-parse 同口径。
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
                "base_blob": base_blobs.get(norm),  # 删除项同样记基底 blob（§6.4 重校验可比）
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
        # C1 合批去抖（同会话短窗并入 pending 前件；跨会话/跨 worktree 永不并）：
        # 放在 compaction 之后——同路径覆盖语义已由 compaction 处理，合批只吃
        # 互斥路径（重叠路径经 compaction 缩减后并入，文件集并集不变）。显式
        # depends_on 来件不并（调用方编排优先）。
        if _c1_debounce_enabled() and opts.worktree_root and not depends_on:
            cand_seq = _read_seq(root, session_id) + 1
            incoming = _C1Incoming(
                session_id=session_id,
                worktree_root=_normalize_worktree_root(opts.worktree_root),
                base_head=base_head,
                incoming_meta=dict(meta_extra or {}),
                allow_oversize=opts.allow_oversize_batch,
                now_ts=datetime.now().astimezone().timestamp(),
                qid=_make_qid(session_id, cand_seq),
                entries=blob_entries,
                message=msg,
            )
            merged = _try_c1_absorb(root, incoming)
            if merged is not None:
                _write_seq(root, session_id, cand_seq)
                logger.info(
                    "[enqueue] qid=%s C1合批并入 %s（files=%d，同会话短窗）",
                    incoming.qid,
                    merged["qid"],
                    len(blob_entries),
                )
                return {**merged, "absorbed": {"qid": incoming.qid, "files": len(blob_entries)}}
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
                    # Rx-5：队列优先级（int，缺省 0，越大越先出队；显式落 0=新件自描述，
                    # 读侧 _item_priority get 缺省兼容无键旧件）
                    "priority": _normalize_priority((meta_extra or {}).get("priority")),
                    "depends_on": list(depends_on or []),  # P1 级联标记依据（66 号 §6.4）
                    "supersedes": removed,  # compaction 覆盖全链（传递累积，审计可追溯）
                    # C1 合批判据键：同会话+同 worktree_root 才允许短窗并入（红线）；
                    # 不传=不做合批（历史调用方行为不变）
                    **({"worktree_root": _normalize_worktree_root(opts.worktree_root)} if opts.worktree_root else {}),
                    # C-1 放行证据随袋（registration_gate 摘要；done/dead 永留可答
                    # 「这袋过没过预检」—— witness doc §2.10「剥除名单不进 done/」教训）；
                    # preflight_face=E-4 TOCTOU 死信出口漂移比对素材
                    **(
                        {
                            "registration_gate": {
                                "ran": True,
                                "findings": 0,
                                "degraded": list(_pf_degraded),
                                "at": _now_iso(),
                            }
                        }
                        if _pf_degraded or _pf_face
                        else {}
                    ),
                    **({"preflight_face": dict(_pf_face)} if _pf_face else {}),
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
                # 矿③ 双读：影子存在则合并 stale 视图（一版过渡，见 _merge_stale_view）
                return _merge_stale_view(path, json.loads(path.read_text(encoding="utf-8")))
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
# stale 影子指令（矿③ MVP，st-qmine-20260925）：pending 袋 append-only 化。
# 级联 stale 不再原地改写袋 JSON（唯一 lease 外可写面=幽灵写手族根因，D4 四补丁
# 皆为堵它的症状治疗），改 O_EXCL 原子写旁路指令 pending/.stale/<qid>.json，
# 读取侧 _read_item 双读合并（一版过渡）。注：.stale 为点前缀子目录、内文件随
# qid 命名——pending 全部消费方恒以非递归 glob("q-*.json") 扫描，影子目录天然
# 不进队首扫描/四态计数/health 视野（白名单口径，勿成 hold_* 式暗仓）。
# ---------------------------------------------------------------------------


def _stale_shadow_path(root: Path, qid: str) -> Path:
    """stale 影子指令路径：pending/.stale/<qid>.json（旁路目录，非四态）。"""
    return root / "pending" / ".stale" / f"{qid}.json"


def _write_stale_shadow(root: Path, qid: str, stale_by: str, trigger: str) -> bool:
    """O_EXCL 原子写影子指令；已存在返回 False（保留首个触发源，同旧 meta.stale 不重标口径）。"""
    try:
        path = _stale_shadow_path(root, qid)
        path.parent.mkdir(parents=True, exist_ok=True)
        _create_item_excl(
            path,
            json.dumps(
                {"qid": qid, "stale": True, "stale_by": stale_by, "stale_at": _now_iso(), "trigger": trigger},
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8"),
        )
    except FileExistsError:
        return False
    return True


def _read_stale_shadow(root: Path, qid: str) -> dict | None:
    """读影子指令；缺失/损坏一律 None（读者容错：影子丢只损失 stale 视图，不伤袋体）。"""
    try:
        return json.loads(_stale_shadow_path(root, qid).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _cleanup_stale_shadow(root: Path, qid: str) -> bool:
    """随迁清理影子（done/dead 转移点/requeue 调用）；fail-open，返回是否确有删除。"""
    try:
        _stale_shadow_path(root, qid).unlink()
    except OSError:
        return False
    return True


def _sweep_orphan_stale_shadows(root: Path) -> int:
    """孤儿影子清扫（drain 波首、lease 单写者内）：qid 已不在 pending 的影子删除。

    兜底不经本仓清理面的出口（pool 车道死信路径/崩溃窗残留）——影子只为 pending
    件存在，件走影随迁（done/dead 转移点清理）是常态路径，此处只清残留防暗仓。
    """
    shadow_dir = root / "pending" / ".stale"
    if not shadow_dir.is_dir():
        return 0
    swept: list[str] = []
    for shadow in sorted(shadow_dir.glob("*.json")):
        if (root / "pending" / shadow.name).exists():
            continue  # 袋仍在 pending——影子有效
        # 红队终轮 P1：终态核对必须含 dead/（_recover_processing_orphans 认 done+dead
        # 双终态）——工线程在清扫二扫窗内认领并快速死信（毒药件 fast-fail）时，仅查
        # done 会把已终态 qid 误判孤儿清影→二次重跑违反"已确认终态不重跑"。
        if (root / "done" / shadow.name).exists() or (root / "dead" / shadow.name).exists():
            continue  # 已达终态——非孤儿
        if _cleanup_stale_shadow(root, shadow.stem):
            swept.append(shadow.stem)
    if swept:
        logger.info("[queue] 清扫孤儿 stale 影子 %d 个: %s", len(swept), swept)
    return len(swept)


def _merge_stale_view(path: Path, item: dict) -> dict:
    """双读一版过渡：影子存在 ⇒ 把 stale 指令并进 meta 视图（内存合并，不改袋体）。

    袋内 meta.stale 旧位（历史袋）与影子新位并存，任一命中即 stale——兼容窗口内
    旧袋照常工作。合并只作用调用方持有的内存副本：落账（done/dead）时随袋持久化
    属预期（stale_by 审计溯源同旧口径）；重试退回路径若带回 pending 亦无害（清理
    点 meta+影子双清，视图自愈）。root 取 path.parent.parent（pending/processing
    两态通用，影子只在 pending 有）。
    """
    meta = item.setdefault("meta", {})
    if meta.get("stale"):
        return item  # 袋旧位已标——视图一致，省一次影子 IO
    shadow = _read_stale_shadow(path.parent.parent, str(item.get("qid") or path.stem))
    if shadow:
        meta["stale"] = True
        meta.setdefault("stale_by", shadow.get("stale_by", ""))
        meta.setdefault("stale_at", shadow.get("stale_at", ""))
    return item


# ---------------------------------------------------------------------------
# 依赖级联标记（66 号 §6.4 + 08 号文 §4.3 P1，2026-08-29 落地；矿③ MVP 改影子）
# ---------------------------------------------------------------------------


def _mark_cascade_stale(root: Path, landed_item: dict) -> list[str]:
    """项 X 成功落盘后的级联标记：扫描 pending 剩余项，命中的写 stale 影子指令，返回命中 qid 列表。

    命中条件（66 号 §6.4「级联标记」）：
    - meta.depends_on 含 X.qid（显式依赖前置项）；或
    - base_head 与 X.base_head 相同且均非空（base_head 经由 X——同基底入队，
      X 落盘后目标分支 HEAD 已越过该基底，Y 的基底过龄）。

    stale 项不立即处置——排到队首时经 _revalidate_stale_base 重校验基底：
    仍适用→清标放行，不适用→降死信候选（dead_reason=cascade_stale）。
    矿③ MVP：袋 JSON **零改写**（append-only 不变量）——命中只 O_EXCL 写影子
    pending/.stale/<qid>.json；影子已存在（袋旧位或旁路）=已标，不重标——保留
    首个触发源（stale_by 审计首因）。读窗收窄语义保留（D4 第一层）：项已被认领
    （rename→processing）则影子也不写——写了对已认领件不可见，徒增孤儿等清扫。
    F1 飞行窗（redblu_robust.md §五）与影子并存裁定（考古合并 2026-09-26）：标记
    介质以影子为准，F1 的认领 rename 飞行窗保护逻辑原样保留——影子写入后延时二扫，
    目的侧（processing/done）落定 ⇒ 刚写的影子失去作用对象，就地清理（防 stale
    视图错标已认领件；影子写不产 pending 幽灵，故 F1 的「幽灵 unlink」形态转化为
    「影子 cleanup」，延时让渡与双查口径不变）。
    口部随迁清理落账项自身影子（pool 车道 done 出口不经本仓 drain 面，在此覆盖）。
    仅 lease 持有者（单写者）调用；仅作用 pending（done/dead 是终态不触碰）。
    """
    landed_qid = str(landed_item.get("qid", ""))
    _cleanup_stale_shadow(root, landed_qid)
    landed_base = landed_item.get("base_head")
    marked: list[str] = []
    for candidate in sorted((root / "pending").glob("q-*.json")):
        try:
            item = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # 写入窗口或损坏——跳过不碰（读者容错，同 _compact_pending 口径）
        qid = str(item.get("qid") or candidate.stem)
        meta = item.get("meta") or {}
        if meta.get("stale") or _stale_shadow_path(root, qid).exists():
            continue  # 已标（袋旧位/影子）——不重标，保留首个触发源
        depends_hit = landed_qid in (meta.get("depends_on") or [])
        base_hit = bool(landed_base) and bool(item.get("base_head")) and item["base_head"] == landed_base
        if not (depends_hit or base_hit):
            continue
        if not candidate.exists():
            continue  # 读窗内已被认领/移除——不再是 pending，stale 标记无从谈起（D4/F1 收窄）
        if not _write_stale_shadow(root, qid, landed_qid, "depends_on" if depends_hit else "base_head"):
            continue  # 影子已被并发写入（首个触发源胜出）——不计命中
        # F1 飞行窗二扫（保护逻辑保留，介质改影子）：影子写入瞬间认领 rename 可能恰在
        # 飞行中——源侧已 rename 走、目的侧尚未可见（Windows 杀软/索引器加宽可见性滞后），
        # 立即双查皆 False ⇒ 影子错标已认领件（拾取侧双读会注入 stale 视图）。先等飞行窗
        # 落定再做存在性二扫：清扫点的一次性确定性让渡，非周期轮询。
        time.sleep(0.05)  # noqa: m10-time-trigger  M10豁免: 清扫窗口对飞行中 rename 的确定性让渡（一次性延时二扫），非周期轮询
        if (root / "processing" / candidate.name).exists() or (root / "done" / candidate.name).exists():
            # 写后瞬间清理：同名已在认领/终态 ⇒ 本影子已无作用对象（读窗收窄同源语义），
            # 当场撤除防 stale 视图错标（孤儿等波首清扫兜底之外的即时口径）
            _cleanup_stale_shadow(root, qid)
            continue
        marked.append(qid)
    return marked


def _note_rebased_registry(item: dict, paths: list[str]) -> None:
    """re-base 放行留痕：把漂移并被交合并仲裁的注册表路径写进 item.meta.rebased_registry。

    拆出主函数为守复杂度上限（宪法复杂度≤15）。留痕是硬要求——"漂移被接管"不得静默，
    否则审计侧无法区分"基底本就对齐"与"基底漂移但交给合并器"两种放行。
    meta 缺失或非 dict（历史项/损坏项）时新建，不覆写既有键以外的内容。
    """
    meta = item.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        item["meta"] = meta
    meta["rebased_registry"] = paths
    logger.info(
        "[queue] qid=%s 基底漂移交条目级三向合并仲裁（re-base 不退袋）: %s",
        item.get("qid", "?"),
        paths,
    )


def _revalidate_stale_base(
    item: dict, head_reader, mergeable_pred: Callable[[str], bool] | None = None
) -> tuple[bool, list[str]]:
    """stale 项基底重校验（66 号 §6.4）：base_blob vs 当前 HEAD 逐文件比对。

    返回 (仍适用, 不适用路径清单)。判定口径：
    - base_blob 为空的条目跳过（A 段无基底信息，无法判定→放行口径）；
    - base_blob 非空而 head_reader 缺失 → fail-closed 判不适用（无法确认仍适用即
      降死信候选，人工经 requeue 基于当前工作区重建快照取回，66 号 §6.4 死信闭环）；
    - head_reader: callable(仓内相对路径) -> 当前 HEAD 该路径 blob 标识（与 base_blob
      同 id 空间），路径不在 HEAD 返回 None；比对不一致即不适用。
    队列层保持零 git 依赖（66 号 §6.1 刻意出入 #3）——HEAD 读取能力由调用方注入。

    mergeable_pred（可选形参， callable(仓内相对路径) -> bool）：注册表族 base_blob
    **确已比对出与 HEAD 不一致**且谓词判真时，不再在队列层判 cascade_stale 退袋，改交
    本仓落地模块的条目级三向合并仲裁（W2 2026-09-22 上线；真冲突仍由合并器死信并携带
    双方条目全文，绝不静默放行）。放行路径经 `_note_rebased_registry` 留痕。
    两条边界：
    ① 缺省 None ⇒ 判定与历史**逐字节一致**（drain 直连口等既有调用方口径不变）；
    ② head_reader 缺失时对**非 mergeable** 路径保险丝照旧判不适用；对 mergeable 路径
       交落地侧条目级合并仲裁——该仲裁在基底不可知时自会 raise 死信（安全不降级），
       队列层抢先判死只会把可救的袋变成人工重投（2026-09-27 裁定，见下方代码注释）。
    """
    mismatched: list[str] = []
    rebased: list[str] = []
    for f in item.get("files") or []:
        base_blob = f.get("base_blob")
        if not base_blob:
            continue
        path = f.get("path", "?")
        if head_reader is None:
            # 语义分叉裁定（2026-09-27）：本形参落地时红证 D 与边界②相互冲突——证尺要求
            # "mergeable + reader 缺失"交合并，代码却一律判死。裁定取证尺，理由是一条
            # 方向性判据：注册表族"基底是否仍等于 HEAD"本来就不是队列层的仲裁点，落地侧
            # _merge_registry_file 在 base_head 与 base_blob 皆不可知时 raise RuntimeError
            # 死信回人工（commit_queue_landing.py:1769，判据取向=绝不猜基底）。在此判死
            # 不增加任何安全，只把一只本可被条目级合并救活的袋子变成人工重投（09-27 实测
            # 该形态当日误杀 33 只）。非 mergeable 路径没有这个下游仲裁者，保险丝照旧。
            if mergeable_pred is not None and mergeable_pred(path):
                rebased.append(path)
                continue
            mismatched.append(f"{path}(head_reader 缺失无法重校验)")
            continue
        if head_reader(path) == base_blob:
            continue
        if mergeable_pred is not None and mergeable_pred(path):
            rebased.append(path)
            continue
        mismatched.append(path)
    if rebased:
        _note_rebased_registry(item, rebased)
    return (not mismatched, mismatched)


_MACHINE_LANE_STARVATION_SEC = 1800.0  # machine 单饿死上限 30min（P1-D 护栏）
_HEAD_SCAN_BOUND = 400  # B4 队首选择扫描界（FIFO 须见到全部在途项才能定"最老"；
# 原 64 是"字典序==到达序"谬误下的防御上界——改按 created_at 后 64 会把第 65 位起
# 的最老件永久看不见，等于把饿死藏回排序里。400 覆盖实测峰值 56 件约 7 倍余量。）


def _attempts_backoff_enabled() -> bool:
    """B5 退避总开关：env 覆盖位缺省 ON（"0"/"false"/"off"/"no"=关闭回退现行为）。"""
    raw = os.environ.get(_ATTEMPTS_BACKOFF_ENV, "").strip().lower()
    return raw not in ("0", "false", "off", "no")


def _item_attempts(item: dict | None) -> int:
    """读项的 attempts 计数；缺失/不可解析一律 0（历史项/损坏项不惩罚）。"""
    try:
        return int((item or {}).get(_ATTEMPTS_FIELD, 0) or 0)
    except (TypeError, ValueError):
        return 0


def _backoff_penalty_seconds(item: dict | None) -> float:
    """B5 排队键惩罚：attempts≥阈值 → (attempts-阈值+1)×步长 秒（单调递增）。

    调用方（_pick_head._rank）把惩罚加在 **max(原时刻, now)** 上=未来时刻，延迟可
    拾取（等效挪队尾）；正常件（attempts<3/缺字段/None）与开关关闭恒 0 零影响。
    """
    if not _attempts_backoff_enabled():
        return 0.0
    attempts = _item_attempts(item)
    if attempts < _ATTEMPTS_BACKOFF_THRESHOLD:
        return 0.0
    return (attempts - _ATTEMPTS_BACKOFF_THRESHOLD + 1) * _ATTEMPTS_BACKOFF_PENALTY_SECONDS


def _bump_retry_attempts(processing_path: Path, item: dict, reason: str = "") -> int:
    """重试退回 pending 前 attempts+1 持久化在该 qid 的状态文件（项 JSON 本体）。

    附 last_failure（截断 500 字符）/last_retry_at 留痕；持久化失败吞掉不阻断退回
    （计数丢失仅损失一轮退避精度，物品绝不因此丢——宁漏不误）。
    """
    item[_ATTEMPTS_FIELD] = _item_attempts(item) + 1
    if reason:
        item["last_failure"] = str(reason)[:500]
    item["last_retry_at"] = _now_iso()
    try:
        _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
    except OSError:
        logger.warning("[drain] qid=%s attempts 计数持久化失败（退回照常，宁漏不误）", item.get("qid"))
    return item[_ATTEMPTS_FIELD]


def _attempts_exhausted_reason(item: dict) -> str:
    """attempts 耗尽死因串：注明 attempts 耗尽+末次失败原因（三分类随末次原因走）。"""
    attempts = _item_attempts(item)
    return (
        f"attempts_exhausted: 落地失败退回 {attempts} 次耗尽（B5 退避止血，拾取即死信不再白耗 landing）"
        f": {item.get('last_failure', '')}"
    )


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


def _normalize_priority(raw: object) -> int:
    """Rx-5：priority 归一（int 原样含负数；bool/非 int/缺省 → 0）。读写两侧同判据。

    bool 是 int 子类必须显式排除（True 归 1 会悄悄插队）；旧件/外来值（字符串、
    null）一律兜底 0=不改变 FCFS 相对序。
    """
    if isinstance(raw, bool) or not isinstance(raw, int):
        return 0
    return raw


def _item_priority(item: dict | None) -> int:
    """Rx-5 队列优先级读取：meta.priority（int，缺省 0，越大越先出队）。

    旧件兼容：q-*.json 无 priority 键 → 0（get 缺省），与改造前 FCFS 相对序逐字节一致。
    """
    return _normalize_priority(((item or {}).get("meta") or {}).get("priority"))


def _pick_head(heads: list) -> tuple:
    """B4 排队键 + Rx-5 优先级：(-priority, interactive 先于 machine, created_at FCFS, qid 破平)。

    返回 (path, lane)。Rx-5（2026-09-29）：priority 为全局主键——高优 machine 可先于
    缺省 interactive（车道优先降为同优先级内次键）；同优先级内严格保持 B4 语义
    （interactive 全在 machine 前、created_at 先来先服务、qid 仅破平）。
    其余语义零变更：B5 退避未来时刻惩罚、读取失败 mtime 退化、machine 防饿死提前放行
    （仍取**最老到达**的 machine 件，与 priority 无关）。

    为什么必须改（实测，st-commitspeed-tbl-20260924 提交等待调查 R5）：入参 heads 由调用方
    按 qid 字典序预排，而 qid 形如 `q-<日期>-<session_id>-<序号>` ⇒ 全局排序主键其实是
    **会话名字母序**而非到达顺序。实测 24h 内 1081 对先后关系里 **56% 倒挂**（后到先走），
    最老件等 5.9 小时、而字母序在前的反复失败会话可持续独占队首
    （09-24 14:29-15:21 主区 HEAD 零推进 52 分钟即该形态）。
    残留风险（B5 已止血，st-commitspeed-tbl-20260924）：环境失败回退 pending 的件
    原保留原 created_at 恒居队首——现 attempts 计数+退避已落地：重试退回前
    attempts+1（_bump_retry_attempts），attempts≥3 排序键加惩罚（
    _backoff_penalty_seconds，延迟可拾取），attempts≥5 拾取即死信（drain attempts
    耗尽分支）——毒药队首最多白耗 _ATTEMPTS_DEAD_THRESHOLD 次即让位/入墓。
    """
    from datetime import datetime

    now_ts = datetime.now().astimezone().timestamp()

    def _rank(path: Path) -> tuple:
        """(-priority, lane_key, 到达时刻, qid, path) 排序键；lane_key 0=interactive/1=machine
        （升序即 interactive 在前）；时刻不可解析时退化文件 mtime。"""
        item = _read_item(path)
        lane = _item_lane(item)
        prio = _item_priority(item)
        raw = (item or {}).get("created_at")
        ts = None
        if raw:
            try:
                ts = datetime.fromisoformat(str(raw)).timestamp()
            except (TypeError, ValueError):
                ts = None
        if ts is None:
            try:
                ts = path.stat().st_mtime
            except OSError:
                ts = now_ts
        # B5 退避（st-commitspeed-tbl-20260924）：attempts≥阈值 → 有效时刻=max(原时刻,
        # now)+惩罚=**未来时刻**（延迟可拾取，等效挪队尾）。必须锚定 now 而非原时刻加
        # 偏移——固定偏移压不过年龄差（实测毒药件比新件老 24h，+15min 偏移仍居队首），
        # 未来时刻才能保证让位所有正常件；多毒药件之间按惩罚单调（轻者先行）。
        penalty = _backoff_penalty_seconds(item)
        if penalty:
            ts = max(ts, now_ts) + penalty
        return -prio, (1 if lane == "machine" else 0), ts, str(path.name), path

    ranked = [_rank(h) for h in heads[:_HEAD_SCAN_BOUND]]
    ordered = sorted(ranked, key=lambda r: (r[0], r[1], r[2], r[3]))
    machine = [r for r in ranked if r[1] == 1]
    oldest_machine = min(machine, key=lambda r: (r[2], r[3])) if machine else None
    if oldest_machine and (now_ts - oldest_machine[2]) > _MACHINE_LANE_STARVATION_SEC:
        return oldest_machine[4], "machine"
    if ordered:
        return ordered[0][4], ("machine" if ordered[0][1] == 1 else "interactive")
    return None, "machine"


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
    B5 attempts 退避（st-commitspeed-tbl-20260924）：环境失败退回前 attempts+1 持久化；
    attempts≥5 的项拾取即死信（dead_reason=attempts_exhausted），毒药队首有限让位。

    landing : callable(item: dict, queue_root: Path) -> LandingResult；None=默认桩
        （仅标记 done 不真提交，B 段接专用 worktree 真落盘）。
    head_reader : callable(仓内相对路径) -> 当前 HEAD 该路径 blob 标识 | None；
        P1 级联 stale 项基底重校验用（_revalidate_stale_base）；None=仅 base_blob
        全空的项可重校验通过（A 段口径），base_blob 非空项 fail-closed 降死信候选。
    done_ttl_days : done/ TTL 天数（默认 7 天，66 号 §12 Q3）；排空收尾在 lease 内
        自动清理超龄 done 项；None=本轮不清理。dead/ 永不清理不变量不受影响
        （人工 dead-archive 归档除外——mv 非删，RB2）。
    异常语义：landing 抛 Exception → 单项失败死信；BaseException 不捕获向上传播
        （模拟进程崩溃，当前项留 processing 等孤儿回收）。
    """
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    if head_reader is None:
        # 半接线治本（2026-09-27 实证）：head_reader 形参只有池路径 _pool_process_item 注入，
        # try_bootstrap_drain（签名里连该形参都没有）/_cmd_drain/reconciler 经 landing 转发
        # 这三条生产道一律 None ⇒ _revalidate_stale_base 走 fail-closed 分支，**不经落地**
        # 就把被标 stale 的在途袋判死（文案指纹 "(head_reader 缺失无法重校验)"）。此处按
        # duck-typing 从 landing 自带读口补齐：一处必经点覆盖全部排空入口，不改调用点签名、
        # 不引循环 import；无读口时保持 None 交下游 fail-closed（判据不放松）。
        _hr_getter = getattr(landing, "head_reader", None)
        if callable(_hr_getter):
            head_reader = _hr_getter()
    landing_fn = landing if landing is not None else default_landing_stub
    stats = {
        "skipped": False,
        "recovered": 0,
        "done": 0,
        "dead": 0,
        "processed_qids": [],
        "stale_cleared": 0,  # P1 级联：stale 重校验仍适用清标放行数
        "cascade_marked": 0,  # P1 级联：成功落盘后续项被标 stale 数
        "successors_rebuilt": 0,  # 死信摘除后继重建（波 1B 1.7b）：与死者同路径其后各袋标 stale 数
        "done_cleaned": 0,  # done/ TTL 清理移除数
    }

    with SerializerLease(root, timeout=lease_timeout) as lease:
        stats["recovered"] = len(_recover_orphans(root))
        # 矿③ 孤儿影子兜底清扫（在孤儿回收之后——回收回 pending 的件影子仍有效）
        stats["orphan_shadows_swept"] = _sweep_orphan_stale_shadows(root)
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
            # B5 attempts 耗尽（st-commitspeed-tbl-20260924 止血）：attempts≥死信阈值的
            # 毒药件拾取即死信，不再白耗一次 landing——队首让位，后续件同轮照常落地。
            # dead_reason 注明 attempts 耗尽并附末次失败原因（classify_dead_reason 随
            # 末次原因三分类：env 失败耗尽仍归 env 可 requeue，物品不被冤枉）。
            if _attempts_backoff_enabled() and _item_attempts(item) >= _ATTEMPTS_DEAD_THRESHOLD:
                item["dead_at"] = _now_iso()
                item["dead_reason"] = _attempts_exhausted_reason(item)
                # 波 1B 1.7b/c：毒药摘除走死信封印唯一出口（归属五件套+复发熔断+
                # 后继重建），与通用死信出口同口径——B5 出口 M3.3 脱节残留面治本。
                stats["successors_rebuilt"] += len(_seal_dead_letter(root, item))
                _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                os.replace(processing_path, root / "dead" / head.name)
                _cleanup_stale_shadow(root, qid)  # 矿③ 影随迁：袋进 dead，影子指令随迁清理
                stats["dead"] += 1
                logger.warning(
                    "[drain] qid=%s attempts=%d 耗尽，拾取即死信（队首止血）: %s",
                    qid,
                    _item_attempts(item),
                    item["dead_reason"],
                )
                _notify_task_board_dead_letter(item)  # 死信标签联动同口径（宁漏不误）
                stats["processed_qids"].append(qid)
                processed += 1
                continue
            result: LandingResult | None = None
            if (item.get("meta") or {}).get("stale"):
                # P1 级联（66 号 §6.4）：stale 项重校验基底——仍适用清标放行走正常
                # landing；不适用直接降死信候选（dead_reason=cascade_stale），不消耗 landing
                still_ok, mismatched = _revalidate_stale_base(item, head_reader)
                if still_ok:
                    meta = item["meta"]
                    meta.pop("stale", None)
                    meta["stale_cleared_at"] = _now_iso()  # stale_by 保留作审计溯源
                    _cleanup_stale_shadow(root, qid)  # 矿③ 清标放行=影子双清（meta 视图+旁路指令）
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
                    # B5（st-commitspeed-tbl-20260924）：退回前 attempts+1 持久化——
                    # 毒药件不再无限保留队首资格（≥3 惩罚退避、≥5 拾取死信）。
                    if _attempts_backoff_enabled():
                        _bump_retry_attempts(processing_path, item, f"{type(exc).__name__}: {exc}")
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
                _cleanup_stale_shadow(root, qid)  # 矿③ 影随迁：袋进 done，影子指令随迁清理
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
                # E-4 TOCTOU 死信出口增信（chain_fullflow §3.7-(iii)）：登记面貌快照随袋
                # 者（meta.preflight_face）与当前 HEAD 面貌比对，漂移=预检基础在入队后
                # 过期——「不是你的内容错，是注册表面貌变了」一跳点明（观测级增信，
                # 不改死信裁决；「预检非新权威」在册原则不动）。
                _annotate_preflight_face_drift(item)
                # 波 1B 1.7b/c：死信封印唯一出口——归属五件套（M3.3 处方+责任会话，
                # E-4 注解先行写入的增强处方 setdefault 不覆写）+ 同签名复发熔断 +
                # 后继重建（失败袋摘除后，其后同路径各袋按新组合重校验前进）。
                stats["successors_rebuilt"] += len(_seal_dead_letter(root, item))
                _atomic_write(processing_path, json.dumps(item, ensure_ascii=False, indent=2).encode("utf-8"))
                os.replace(processing_path, root / "dead" / head.name)
                _cleanup_stale_shadow(root, qid)  # 矿③ 影随迁：袋进 dead，影子指令随迁清理
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
            "successors_rebuilt": 0,
            "done_cleaned": 0,
        }


# ---------------------------------------------------------------------------
# 死信封印（波 1B 包 1.7b/c / R-L+R-M，st-zc9-lane-r1 2026-09-29）：归属签名 +
# 同签名复发熔断 + 根因工序单 + 摘除后继重建——四件事一体，唯一封袋出口。
# 判据出处 docs/_working/total_command_closeout/10_wave_plan.md:55-56；对标
# review_ext_ci_and_mergequeue.md 3-1（Google Build Cop：死信是"当天必须有人中断
# 工作去修的活信号"）。2026-09-29 实测死信 900+ 无归属难处置=本机制运维价值实证。
# ---------------------------------------------------------------------------

#: 同签名复发熔断阈值：第 3 封即熔断升级根因工序单（10_wave_plan R-M 判据）
_RECURRENCE_FUSE_LIMIT = 3


def _dead_signature(item: dict) -> str:
    """归因签名 = f"{死因族}:{死因头部特征}"——同根因必同签名，异根因必异签名。

    头部特征取 dead_reason 首个冒号前的 gate/机制标识（CREATE-GUARD/COMMIT_SCOPE/
    attempts_exhausted…）；族=classify_dead_reason 三分类现读（禁抄常量防漂移）。
    空死因回退 "other:NOREASON"（熔断永不因缺死因而静默失效）。
    """
    reason = str(item.get("dead_reason") or "")
    family = classify_dead_reason(reason)
    head = reason.split(":", 1)[0].strip() if reason else ""
    return f"{family}:{head or 'NOREASON'}"


def _seal_dead_letter_attribution(item: dict) -> None:
    """封袋归属五件套（原地变更，幂等）：owner_session / first_dead_at /
    dead_letter_family / dead_signature / prescription。

    - owner_session=袋 session_id（责任会话一跳可达；既有值不覆写）；
    - first_dead_at 首死时跨链继承：meta.requeue_lineage.first_dead_at_prev 优先于
      本次 dead_at（重投后的新袋再死，首死时不得回退到重投时刻）；
    - prescription 既有值不覆写（E-4 注解面先行写入的增强处方保留）。
    """
    reason = str(item.get("dead_reason") or "")
    item["owner_session"] = item.get("owner_session") or item.get("session_id") or ""
    if not item.get("first_dead_at"):
        lineage = (item.get("meta") or {}).get("requeue_lineage") or {}
        item["first_dead_at"] = lineage.get("first_dead_at_prev") or item.get("dead_at") or ""
    item.setdefault("dead_letter_family", classify_dead_reason(reason))
    item.setdefault("dead_signature", _dead_signature(item))
    item.setdefault("prescription", dead_letter_prescription(reason))


def _recurrence_state_path(root: Path) -> Path:
    """同签名复发表落点：dead/_recurrence_state.json（下划线前缀不入 q-*.json 名册面）。"""
    return root / "dead" / "_recurrence_state.json"


def _bump_recurrence(root: Path, signature: str, *, owner: str, first_dead_at: str) -> dict:
    """同签名复发计数 +1 并持久化；返回该签名条目 {count, first_dead_at, owner_sessions}。

    首封定基（first_dead_at 取首封，此后不覆写）；owner_sessions 逐封去重累积。
    状态文件缺失/损坏按零起算（红队 P2 口径：熔断语义不因脏数据崩溃——计数丢失只
    损失一次熔断时机，绝不误伤）。调用方负责 _ensure_dirs。
    """
    path = _recurrence_state_path(root)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            state = {}
    except (OSError, ValueError):
        state = {}
    signatures = state.get("signatures")
    if not isinstance(signatures, dict):
        signatures = {}
    entry = signatures.get(signature)
    if not isinstance(entry, dict):
        entry = {}
    try:
        count = int(entry.get("count") or 0) + 1
    except (TypeError, ValueError):
        count = 1
    owners = [o for o in (entry.get("owner_sessions") or []) if o]
    if owner and owner not in owners:
        owners.append(owner)
    new_entry = {
        "count": count,
        "first_dead_at": entry.get("first_dead_at") or first_dead_at or "",
        "owner_sessions": owners,
    }
    signatures[signature] = new_entry
    _atomic_write(path, json.dumps({"signatures": signatures}, ensure_ascii=False, indent=2).encode("utf-8"))
    return new_entry


def _iter_eviction_successors(root: Path, dead_qid: str, dead_paths: set):
    """产出（qid, candidate 路径）——排死者之后且与其共享路径的 pending 袋。

    判据细分独立成生成器（主函数保复杂度合规，COMPLEXITY-GUARD 治本）：qid 字典序
    严格大于死者（predecessor 与死者自身绝不牵连）；路径交集非空（无组合关系保守不
    牵连）；读窗内仍在 pending（已被认领/移除跳过，D4 收窄同款）。解析失败跳过不碰。
    """
    for candidate in sorted((root / "pending").glob("q-*.json")):
        try:
            successor = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # 写入窗口或损坏——跳过不碰（读者容错，同 _mark_cascade_stale 口径）
        qid = str(successor.get("qid") or candidate.stem)
        if qid <= dead_qid:
            continue  # 死者自身与其 predecessor 绝不牵连（只重建其后各袋）
        bag_paths = {f.get("path") for f in (successor.get("files") or []) if isinstance(f, dict) and f.get("path")}
        if not (bag_paths & dead_paths) or not candidate.exists():
            continue  # 无组合关系不牵连；读窗内已被认领/移除不再标
        yield qid, candidate


def _rebuild_successors_after_eviction(root: Path, dead_item: dict) -> list[str]:
    """摘除后继重建（R-L）：与死者共享路径的**其后各袋**写 stale 影子，按新组合继续前进。

    「其后」= qid 字典序严格大于死者（车道内 FIFO 序=clid 序，与 drain 队首排序同一
    真源）；「按新组合」= 与死者至少共享一个文件路径（同路径叠写才受摘除影响，保守
    判据不扩大动作面——无组合关系与前序各袋绝不牵连）。标记介质=stale 影子指令
    （矿③ append-only：袋 JSON 零改写），拾取时经 _revalidate_stale_base 重校验基底：
    仍适用清标放行并落 meta.stale_cleared_at，不适用降死信候选（判据式非处决式）。
    影子已存在（前序摘除/级联已标）=不重标（保留首因）。返回本扇标记的 qid 清单
    （drain stats.successors_rebuilt 消费；monkeypatch 位）。
    """
    dead_qid = str(dead_item.get("qid") or "")
    if not dead_qid:
        return []
    dead_paths = {f.get("path") for f in (dead_item.get("files") or []) if isinstance(f, dict) and f.get("path")}
    if not dead_paths:
        return []
    marked: list[str] = []
    for qid, _candidate in _iter_eviction_successors(root, dead_qid, dead_paths):
        if not _write_stale_shadow(root, qid, dead_qid, "eviction"):
            continue  # 已标（前序摘除/级联首因胜出）
        marked.append(qid)
    return marked


def _seal_dead_letter(queue_root: str | os.PathLike, item: dict) -> list[str]:
    """死信封印唯一出口：归属签名 + 同签名复发熔断 + 根因工序单 + 后继重建。

    drain 两条死信支线（B5 毒药拾取即死信 / landing 失败死信）与直调封袋者共用本
    出口，杜绝同形死信两套口径（B5 出口 M3.3 脱节残留面 bd8ba4d85a7 自述的治本）：
    ① 归属五件套（_seal_dead_letter_attribution）——新死信当场可查属主与归因签名；
    ② 同签名第 _RECURRENCE_FUSE_LIMIT 封 ⇒ recurrence_fused=true + 根因工序单落
       dead/_root_cause/<签名slug>.json（含属主集合与首死时）；requeue 面拒盲重投；
    ③ _rebuild_successors_after_eviction 后继重建（失败袋摘除后其链不停摆）。
    袋体落盘由调用方负责（drain 死信出口已有 _atomic_write+rename 链）；本函数只做
    item 原地封印 + 旁路状态（复发表/工序单/影子）。返回后继重建标记的 qid 清单。
    """
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    _seal_dead_letter_attribution(item)
    signature = str(item.get("dead_signature") or "")
    entry = _bump_recurrence(
        root,
        signature,
        owner=str(item.get("owner_session") or ""),
        first_dead_at=str(item.get("first_dead_at") or ""),
    )
    count = int(entry.get("count") or 0)
    item["recurrence_count"] = count
    if count >= _RECURRENCE_FUSE_LIMIT:
        item["recurrence_fused"] = True
        ticket_rel = f"dead/_root_cause/{_signature_slug(signature)}.json"
        item["root_cause_ticket"] = ticket_rel
        ticket_path = root / ticket_rel
        ticket_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(
            ticket_path,
            json.dumps(
                {
                    "root_cause_required": True,
                    "signature": signature,
                    "first_dead_at": entry.get("first_dead_at") or item.get("first_dead_at") or "",
                    "owner_sessions": entry.get("owner_sessions") or [],
                    "sample_qid": item.get("qid", ""),
                    "created_at": _now_iso(),
                },
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8"),
        )
        logger.warning(
            "[dead] qid=%s 同签名 %s 复发 %d 次熔断，根因工序单: %s",
            item.get("qid", "?"),
            signature,
            count,
            ticket_path,
        )
    return _rebuild_successors_after_eviction(root, item)


def _signature_slug(signature: str) -> str:
    """签名→安全文件名 slug（冒号转下划线；空值回退 unsigned，永不产空路径段）。"""
    slug = "".join(ch if (ch.isalnum() or ch in "-_.") else "_" for ch in signature).strip("._") or "unsigned"
    return slug[:120]


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


# 重投熔断阈值（QCure M1.3，st-qcure-20260925）：新袋 meta.requeue_count=旧袋+1，
# 计数 ≥3 拒绝重投（连败链非重复重试可解）——--force 显式旗可越（meta.requeue_forced 留痕）。
_REQUEUE_CIRCUIT_LIMIT = 3


def _retry_meta_prev(meta: dict, key: str) -> int:
    """meta 重试计数宽容读（矿② lineage 用；历史袋缺失/坏值按 0——同 requeue_count 红队 P2 口径）。"""
    try:
        return int(meta.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def requeue_dead_item(
    qid: str,
    *,
    queue_root: str | os.PathLike | None = None,
    worktree_root: str | os.PathLike | None = None,
    session_id: str | None = None,
    message: str | None = None,
    base_head: str | None = None,
    base_blobs: dict | None = None,
    from_bag: bool = False,
    force: bool = False,
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

    QCure M1.3（st-qcure-20260925）三补：①base_blobs 基底补全（此前恒 None ⇒ 级联
    重校验空转）；②死信袋 envelope 继承进新袋（requeue 是 envelope 唯一丢失点）；
    ③重投熔断（requeue_count ≥3 拒绝，--force 显式越过留痕）。
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
    old_meta = old_item.get("meta") or {}
    # 波 1B 1.7c 复发熔断（st-zc9-lane-r1）：同签名死信已 _RECURRENCE_FUSE_LIMIT 次
    # ⇒ 盲 requeue 拒绝（修根因前不再烧 landing）；根因工序单随 details 一跳可达；
    # --force 显式旗留痕越过（meta.requeue_forced 留痕）。先于 requeue_count 熔断。
    if old_item.get("recurrence_fused") and not force:
        raise RequeueError(
            f"复发熔断：{qid} 同签名死信已 {old_item.get('recurrence_count', _RECURRENCE_FUSE_LIMIT)} 次，"
            "盲重投拒绝——按根因工序单修因后再取回（确需越过的用 --force，留痕）",
            details={
                "root_cause_ticket": old_item.get("root_cause_ticket") or "",
                "dead_signature": old_item.get("dead_signature") or "",
            },
        )
    # M1.3-③ 重投熔断：新袋计数=旧袋+1，≥_REQUEUE_CIRCUIT_LIMIT 拒绝并给死因处方
    # （连败链说明重复重试不可解）；--force 显式旗可越（meta.requeue_forced=true 留痕）。
    try:
        requeue_count = int(old_meta.get("requeue_count") or 0)
    except (TypeError, ValueError):
        requeue_count = 0  # 手改 JSON 坏值按零起算（红队 P2）——熔断语义不因脏数据崩溃
    new_count = requeue_count + 1
    if new_count >= _REQUEUE_CIRCUIT_LIMIT and not force:
        dead_reason = old_item.get("dead_reason", "")
        raise RequeueError(
            f"重投熔断：{qid} 已重投 {requeue_count} 次，第 {new_count} 次拒绝"
            f"（≥{_REQUEUE_CIRCUIT_LIMIT} 连败非重复重试可解）\n"
            f"  死因: {dead_reason}\n"
            f"  死因处方: {dead_letter_prescription(dead_reason)}\n"
            f"  确需越过的用 --force（meta.requeue_forced=true 留痕）"
        )
    # M1.3-② envelope 继承：死信袋 meta.envelope（兼容读旧位顶层 envelope）带进新袋。
    envelope = old_meta.get("envelope") or old_item.get("envelope") or None
    # 矿③ 影子随迁：原 qid 残留 stale 影子（崩溃窗/pool 死信出口残留）并入新袋——
    # 不丢 stale 语义（新袋拾取时照走基底重校验），影子本体随旧袋终态清理（见取回留痕后）。
    stale_shadow = _read_stale_shadow(root, qid)

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

    # 红队 P1-2（QCure M2.2 闭环）：requeue 车道直读字节不经 _read_files_from_worktree
    # ⇒ 冲突标记快照会经 requeue 原样重入袋。此处与入队口同源补扫（复用同一检测器，
    # 禁第二判据）；from-bag 与 worktree 两分支的 payload 都过这道闸。
    from scripts.governance.enqueue_preflight import scan_conflict_markers  # noqa: PLC0415

    for _rq_path, _rq_content in payload:
        _rq_violation = scan_conflict_markers(_rq_path, _rq_content, max_bytes=_MAX_BLOB_BYTES)
        if _rq_violation:
            raise RequeueError(
                "重投快照含未解决合并冲突标记（与入队口同源预扫）——回会话 worktree 解决合并后再重投",
                details={"path": _rq_path, "violation": _rq_violation},
            )

    # 波 1B 包 1.7 声明式防绕过（st-zc9-lane-r1）：requeue 与入队口同一道权威预检
    # ——worktree_root 声明且为 git 工作区（.git 实存）时必跑 run_enqueue_preflight
    # （锁外只读）；blocking ⇒ QueueReject，注定死信的重投在重投口快败（先于 C-2
    # 内联判定，被拦件不落 pending、原死信项留 dead/ 不动）。
    if worktree_root and (Path(worktree_root) / ".git").exists():
        from scripts.governance.enqueue_preflight import run_enqueue_preflight  # noqa: PLC0415

        _pf_prescription = run_enqueue_preflight(
            Path(worktree_root),
            [p for p, _ in payload],
            session_id or old_item.get("session_id", ""),
            message or old_item.get("message", ""),
        )
        if _pf_prescription:
            raise QueueReject(_pf_prescription)

    # C-2（chain_fullflow mine_door_registration_completion §3.7-(i)/§8）：requeue 重建
    # 快照通道挂登记三族内联判定——E-2 实锤 q-…-st-cmd-…-0083（meta 含 requeued_from）
    # 死于落地三族，此前 requeue 全程零预检。同一真源入口（_run_registration_gate），
    # 轻量差量级非 36s 全门重放；audit_event="requeue"（拦截写 preflight_events.jsonl，
    # E-2 的 B 级证据由此可升 A：投袋看 audit）。已知限界（登记不遮掩）：--from-bag
    # 原袋重建时判据读的是工作区盘面——盘上缺该文件即被检查器按缺失跳过（fail-open
    # 口径，不阻断原袋取回）；盘面≠袋字节的残余窗由落地权威链兜底。
    _rq_findings, _rq_deg, _rq_face = _run_registration_gate(
        wt,
        [p for p, _ in payload],
        session_id or old_item.get("session_id", ""),
        message or old_item.get("message", ""),
        audit_event="requeue",
    )
    if _rq_findings:
        raise RequeueError(
            "重投预检拦截（C-2：requeue 与入队口同判据，注定再死信的重投在重投口快败）"
            "——逐门禁处方：\n" + "\n".join(_rq_findings),
            details={"requeued_from": qid, "degraded": list(_rq_deg)},
        )

    # M1.3-① 基底补全（作业簿 producer_enqueue 矿#4）：此前 requeue 恒不填 base_blobs
    # ⇒ 新袋 base_blob 全 None ⇒ 级联重校验 _revalidate_stale_base 结构空转、注册表
    # 合并 fail-closed 死信面未闭合。口径与 _cmd_enqueue 同源（resolve_base_head/
    # resolve_base_blobs）；非 git 目录（tmp 隔离测试）取不到→None/全 None，行为与
    # 修复前一致。
    # ATK-2 治本（st-ff-snapself-20260926，案卷 lane_stale_channel_repro S2 复现背书，
    # E 队 T-4 原案）：--from-bag 的内容真源=原袋，基底必须同步取**原袋基底**而非
    # 重投时刻的工作区 HEAD（主区形态=当下 dev 尖）——否则旧袋字节相对"比它还新"的
    # 声称基底被洗成本包改动，diff(base,dev) 恒空、快进判定结构性失明，陈旧覆盖直落
    # 吃非注册表热件。取回后陈旧覆盖在快进判定现红（死信闭环＝同步后重建快照重投）。
    # 非 from_bag（工作区重建快照）口径零变更：基底仍=重建工作区自己的 HEAD。
    if base_blobs is None:
        from scripts.governance.commit_queue_landing import (  # noqa: PLC0415
            resolve_base_blobs,
            resolve_base_head,
        )

        if from_bag and base_head is None:
            base_head = old_item.get("base_head") or None
        if base_head is None:
            base_head = resolve_base_head(wt)
        base_blobs = resolve_base_blobs(wt, base_head, [p for p, _ in payload] + list(deletes))

    task_id = old_meta.get("task_id")
    new_item = enqueue_item(
        session_id or old_item.get("session_id", ""),
        message or old_item.get("message", ""),
        payload,
        queue_root=root,
        options=EnqueueOptions(
            base_head=base_head,
            base_blobs=base_blobs,
            deletes=deletes or None,
            # requeue 豁免大批硬顶（R2）：死信重试是既定决策的延续，尺寸判定在原入队时
            # 已做出——若此处拒绝，超大死信将永远无法重入队（死锁）。
            allow_oversize_batch=True,
            meta_extra={
                "requeued_from": qid,
                # M1.3-③ 熔断计数随袋累计（dead→requeue 链一跳可见）
                "requeue_count": new_count,
                # 矿②（st-qmine-20260925）requeue_lineage 纯审计留痕：袋寿命计数
                # （attempts/env_retry/snapshot_retry）重置语义**保持不变**——继承即事故
                # （attempts≥5 继承→新袋拾取即死信变砖；env_retry≥3 继承→处方永远无法
                # 执行），只堵"静默清零"：上一袋计数随 lineage 可溯。零消费方零副作用面。
                "requeue_lineage": {
                    "attempts_prev": _item_attempts(old_item),
                    "env_retry_prev": _retry_meta_prev(old_meta, "env_retry"),
                    "snapshot_retry_prev": _retry_meta_prev(old_meta, "snapshot_retry"),
                    # 波 1B 1.7c：首死时跨链继承（新袋再死 first_dead_at 不回退到重投时刻）
                    "first_dead_at_prev": old_item.get("first_dead_at") or "",
                    "requeued_at": _now_iso(),
                },
                **({"task_id": task_id} if task_id else {}),
                # M1.3-② envelope 继承（bag_storage 作业簿⑤③：requeue 是唯一丢失点）
                **({"envelope": envelope} if envelope else {}),
                # 矿③ 影子指令合并：残留 stale 语义带进新袋（不丢——拾取时重校验基底）
                **(
                    {
                        "stale": True,
                        "stale_by": stale_shadow.get("stale_by", ""),
                        "stale_at": stale_shadow.get("stale_at", ""),
                    }
                    if stale_shadow
                    else {}
                ),
                # M1.3-③ --force 越权留痕
                **({"requeue_forced": True} if force else {}),
            },
        ),
    )
    # 取回留痕：原死信项追加 requeued 标注（dead/ 永不清理——只标注不删除）
    old_item["requeued"] = {"new_qid": new_item["qid"], "at": _now_iso()}
    _atomic_write(dead_path, json.dumps(old_item, ensure_ascii=False, indent=2).encode("utf-8"))
    _cleanup_stale_shadow(root, qid)  # 矿③ 影随迁：原袋终态留痕完成，残留影子清理（语义已并入新袋）
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
# dead/ 官方归档通道（RB2 治本，设计真源 docs/_working/root_cure_campaign/
# RB2_dead_archive.md）。66 号 §8 本义="死信回退给人，永不**自动**清理"——人工通道
# 此前从未建成，"人"退化为带外一次性手工 mv（2026-09-29 04:13 先例：结果正确、
# 程序违规：无裁定/无 manifest/操作者不入册）。本节把"有人在做对的事"收编为"系统
# 只允许做对的事"：归档=同卷 os.replace mv 非删（原子、可逆、本命令永久无删除域，
# 删除须 Owner 门位另走裁定），blob 引用由 blob_gc B 类转 D 类依然保全，与"永不
# 自动清理"不变量正交（cleanup_done 等自动通道依旧零触碰 dead/）。
# ---------------------------------------------------------------------------


class DeadArchiveError(RuntimeError):
    """dead-archive 前置拒绝（租约存活等）——整体拒绝非逐件，CLI 映射 exit 1。"""


def _dev_head_landed_checker_factory(repo_root: Path | None = None) -> Callable[[str, str], bool]:
    """默认落地判据工厂：dev HEAD 树存在性（modify=在树；delete=取反判已消失）。

    惰性建 dev 全树路径集合（一次 ``git ls-tree -r dev --name-only``，全量死信×数千
    路径只扫一次树）；非 git 目录/dev 不可得 → 树集为空 ⇒ 全判未落（fail-closed：
    判不了落地就不归档，宁留勿丢）。测试经 landed_checker 注入（设计 §3.2），零 git。
    """
    root = repo_root if repo_root is not None else _REPO_ROOT
    tree: set[str] | None = None

    def _checker(path: str, action: str) -> bool:
        nonlocal tree
        if tree is None:
            import subprocess

            try:
                proc = subprocess.run(
                    ["git", "-C", str(root), "ls-tree", "-r", "--name-only", _TARGET_BRANCH, "--"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=True,
                )
                tree = set(proc.stdout.splitlines())
            except Exception:  # noqa: BLE001 — git 不可用=判据不可得，fail-closed 全留
                tree = set()
        if action == "delete":
            return path not in tree  # delete 取反语义：dev 已无=已落地删除
        return path in tree

    return _checker


def _spot_check_dev_blob(path: str, blob_sha256: str | None) -> str:
    """落地增信抽验（只读）：dev 上该路径 blob 的 sha256 与袋记录比对。

    返回 identical（逐字节全等=强证据）/ evolved（演进件：树在但字节已演进，仍判
    已落地——设计 §2.1 口径）/ unknown（无 sha 记录或 git 不可得，不计入样本）。
    """
    if not blob_sha256:
        return "unknown"
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(_REPO_ROOT), "show", f"{_TARGET_BRANCH}:{path}"],
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return "unknown"
        return "identical" if hashlib.sha256(proc.stdout).hexdigest() == blob_sha256 else "evolved"
    except Exception:  # noqa: BLE001 — 增信面故障静默（树存在性才是裁决判据）
        return "unknown"


def dead_archive_letters(
    queue_root: str | os.PathLike | None = None,
    *,
    days: float = 7.0,
    verify_landed: bool = True,
    execute: bool = False,
    now: datetime | None = None,
    landed_checker: Callable[[str, str], bool] | None = None,
) -> dict:
    """dead/ 官方归档（RB2）：全落+超龄死信整体 mv 进根级 dead_archive_<日>/ 袋+manifest。

    三闸全过才归档，任一不过留原位并计数：
      ①年龄：dead_at 距今 ≥ days 天（缺失/解析失败回退 mtime，cleanup_done 同法）；
      ②revival 互斥：requeued.new_qid 后继在 pending/processing 在途 → 留（重投竞态
        输家的内容可能正被后继袋携带，归档会制造双源）；done 终态后继不拦；
      ③落地校验（默认开）：逐 files[].path 判 dev HEAD（modify=在树；delete=已消失，
        取反语义）；有未落路径 → 留并附 dead_letter_prescription 处方（M3.3 复用）。
        --no-verify-landed 显式关闭须留 verify=off 痕（已取代型批量归档先例复用）。

    安全五条（设计 §3.4）：①mv 非删可逆，命令永久无删除域；②verify 默认开、delete
    取反；③租约存活整体拒绝（非逐件）+后继在途逐件跳过；④manifest.jsonl 逐件留痕
    （还原=按 manifest 反向 mv）；⑤pending/processing/hold_*/blobs/ 零触碰。
    默认 dry-run 零写，execute=True 才动盘（同构 blob_gc"默认 dry-run、显式才动盘"）。

    袋位置=队列根级 dead_archive_<yyyymmdd>/（设计伪码 archive_* 为笔误，按 §3.3
    "零新消费方"意图对齐真源消费者：coordination_state_board retired_dirs 与 blob_gc
    D 类引用集均按根级 dead_archive* 前缀识别；且 state board 的 dead/ 计数用 rglob，
    袋放 dead/ 之下会污染死信积压读数。与今晨先例 dead_archive_final/ 同约定）。

    返回 {"archived": [qid...], "kept": {young, revival_in_flight, unlanded},
    "skipped_corrupt": n, "prescriptions": [...], "bag": str, "dry_run": bool,
    "verify": "on"|"off", "spot_check": {...}|None}（spot_check=默认判据下的落地
    增信抽验聚合，仅前 10 封过闸袋的首件参与）。
    """
    root = resolve_queue_root(queue_root)
    # 不 _ensure_dirs：dry-run 必须零盘面变化（含不凭空创建四态目录）；execute 只建归档袋。
    snap = _lease_snapshot(root)
    if snap.get("present") and snap.get("alive"):
        raise DeadArchiveError(
            f"serializer 租约存活（pid={snap.get('holder_pid')}），拒绝并行维护操作——等排空结束再跑 dead-archive"
        )
    ref = now or datetime.now().astimezone()
    cutoff = ref.timestamp() - days * 86400
    checker = landed_checker or _dev_head_landed_checker_factory()
    verify = "on" if verify_landed else "off"
    bag = root / f"dead_archive_{ref:%Y%m%d}"
    archived: list[str] = []
    kept: dict[str, int] = {"young": 0, "revival_in_flight": 0, "unlanded": 0}
    skipped_corrupt = 0
    prescriptions: list[dict] = []
    spot_check: dict[str, int] | None = (
        {"checked": 0, "identical": 0, "evolved": 0} if (verify_landed and landed_checker is None) else None
    )

    for entry in sorted((root / "dead").glob("q-*.json")):
        try:
            item = json.loads(entry.read_text(encoding="utf-8"))
            if not isinstance(item, dict):
                raise ValueError("envelope 非字典")
        except (OSError, ValueError):
            skipped_corrupt += 1  # 坏 JSON 计数不中断（人工先例口径）
            continue
        # ① 年龄门槛：dead_at 基准，缺失/解析失败回退 mtime
        ts: float | None = None
        dead_at = item.get("dead_at")
        if dead_at:
            try:
                ts = datetime.fromisoformat(str(dead_at)).timestamp()
            except (TypeError, ValueError):
                ts = None
        if ts is None:
            try:
                ts = entry.stat().st_mtime
            except OSError:
                kept["young"] += 1
                continue
        if ts >= cutoff:
            kept["young"] += 1  # 未达年龄门槛（dead_at 距今 < days 天）——留
            continue
        # ② revival 互斥：重投后继在途（pending/processing）不归档
        rq = (item.get("requeued") or {}).get("new_qid")
        if rq and ((root / "pending" / f"{rq}.json").exists() or (root / "processing" / f"{rq}.json").exists()):
            kept["revival_in_flight"] += 1
            continue
        files = item.get("files") or []
        # ③ 落地校验（默认开）：modify=dev 在树；delete=dev 已无（取反判）
        if verify_landed:
            unlanded = [f.get("path", "") for f in files if not checker(f.get("path", ""), f.get("action", "modify"))]
            if unlanded:
                kept["unlanded"] += 1
                reason = str(item.get("dead_reason") or "")
                prescriptions.append(
                    {
                        "qid": item.get("qid", entry.stem),
                        "dead_reason": reason[:120],
                        "unlanded_paths": unlanded[:10],
                        "prescription": dead_letter_prescription(reason),
                    }
                )
                continue
            if spot_check is not None and files and spot_check["checked"] < 10:
                f0 = files[0]
                verdict = _spot_check_dev_blob(f0.get("path", ""), f0.get("blob_sha256"))
                if verdict != "unknown":
                    spot_check["checked"] += 1
                    spot_check[verdict] += 1
        if execute:
            bag.mkdir(parents=True, exist_ok=True)
            _retry_transient(lambda: os.replace(entry, bag / entry.name))  # 同卷原子 mv，可逆
            manifest = {
                "qid": item.get("qid", entry.stem),
                "archived_at": _now_iso(),
                "dead_at": dead_at,
                "dead_reason_head": str(item.get("dead_reason") or "")[:120],
                "n_files": len(files),
                "verify": verify,
                "tool": "commit_queue.dead-archive",
            }
            with open(bag / "manifest.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        archived.append(entry.stem)
    if archived:
        logger.info(
            "[dead-archive] %s %d 封 -> %s（verify=%s days=%s）",
            "归档" if execute else "dry-run 计划归档",
            len(archived),
            bag,
            verify,
            days,
        )
    return {
        "archived": archived,
        "kept": kept,
        "skipped_corrupt": skipped_corrupt,
        "prescriptions": prescriptions,
        "bag": str(bag),
        "dry_run": not execute,
        "verify": verify,
        "spot_check": spot_check,
    }


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
    # B4 口径一致性：队首快照必须与 _pick_head 同判据（旧实现直接取字典序首件＝
    # 报出来的"队首是谁/已等多久"在跨会话场景下是错的，会把真正在办的项说成别的）
    head_path, _head_lane = _pick_head(heads)
    if head_path is None:
        return None
    try:
        item = json.loads(head_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"qid": head_path.stem, "_corrupt": True}
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


def _pending_position_map(root: Path) -> dict:
    """B4 位次表：qid → 前面还有几项，判据与 _pick_head 完全一致（Rx-5 同键）。

    旧实现用"字典序枚举下标"当位次，跨会话时报的是**会话名排名**不是到达排名——
    与队首选择改 FIFO 后会出现"位次说排第 3、实际最后一个走"的自相矛盾，故必须同源。
    Rx-5：与 _pick_head 同一排序键 (-priority, interactive 先于 machine, created_at, qid)；
    machine 防饿死例外（拾取序可提前）不计入位次，同改造前口径。
    """
    from datetime import datetime

    try:
        entries = sorted((root / "pending").glob("q-*.json"))
    except OSError:
        return {}
    now_ts = datetime.now().astimezone().timestamp()
    parsed: list[tuple] = []
    for e in entries:
        item = _read_item(e)
        raw = (item or {}).get("created_at")
        ts = None
        if raw:
            try:
                ts = datetime.fromisoformat(str(raw)).timestamp()
            except (TypeError, ValueError):
                ts = None
        if ts is None:
            try:
                ts = e.stat().st_mtime
            except OSError:
                ts = now_ts
        lane = _item_lane(item)
        parsed.append((e.stem, ts, 1 if lane == "machine" else 0, _item_priority(item)))
    ordered = sorted(parsed, key=lambda p: (-p[3], p[2], p[1], p[0]))
    return {p[0]: i for i, p in enumerate(ordered)}


def queue_status(queue_root: str | os.PathLike | None = None, *, session_id: str | None = None) -> dict:
    """队列状态总览；--session 过滤该会话各 qid 的 pending/processing/done/dead 状态。"""
    root = resolve_queue_root(queue_root)
    _ensure_dirs(root)
    counts: dict[str, int] = {}
    items: list[dict] = []
    # B4 位次表与队首选择同源计算（一次遍历，pending 量级实测 <60，成本可忽略）
    pos_map = _pending_position_map(root)
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
                # B4 位次感：与 _pick_head 同源判据（旧口径＝字典序枚举下标，跨会话报的是
                # 会话名排名而非到达排名，会与队首选择自相矛盾）
                record["position_ahead"] = pos_map.get(entry.stem, entry_idx)
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


# 死因处方映射（QCure M3.3，st-qcure-20260925）：dead_reason 特征串→一键修复指引。
# 首条命中即返回（具体特征优先于分类兜底）；未命中按 env/item/other 三分类给兜底处方。
# 新增死因族 MUST 同 commit 原子补三处：本表 + _DEAD_REASON_*_MARKERS 标记表 + 测试。
_DEAD_PRESCRIPTIONS: tuple[tuple[str, str], ...] = (
    (
        "CREATE-GUARD",
        "新建 .py/.yaml 未登记 creation_token：python scripts/governance/d3_metadata/"
        "batch_creation_tokens.py 登记 token 后重投",
    ),
    ("PROTECTED-PATHS", "触碰保护区路径：改投白名单路径或走 Owner 裁定通道后重投"),
    ("COMMIT_SCOPE", "跨域连坐误判：核实文件归属后用 git_commit.py --allow-multi-domain（留痕）重投"),
    ("三向合并失败", "注册表三向合并冲突：人工比对 基底/dev/快照 三方后手工合并登记，再重投"),
    ("身份键重复", "注册表身份键碰撞：修正 module_id/step_id 等身份键后重投"),
    ("基底不可知", "BASE-UNKNOWN：--base-head 显式传基底（或先对齐工作区与 dev）后重投"),
    ("BASE-UNKNOWN", "BASE-UNKNOWN：--base-head 显式传基底（或先对齐工作区与 dev）后重投"),
    ("快照未真应用", "快照未真应用：核对 worktree 文件实际内容与快照差异后重投"),
    ("冲突标记", "快照含未解决合并冲突标记：回会话 worktree 解决合并后重新入队，勿直接重投"),
    ("cascade_stale", "级联基底失效：前置项已落盘，重投前先按当前 dev 重取基底（--base-head）"),
    (
        "快照自洽见证",
        "stale-carry：袋内该路径字节恰等其自身基底（这不是你的改动）——同步工作区至 dev 后"
        "只重新入队真实改动的文件（勿把未动路径列入 --files；确需回写请显式新建一袋写明理由）",
    ),
    (
        "env_retry",
        "环境失败重试耗尽：排除环境故障（daemon 纪元/worktree/锁）后重投；纪元陈旧重启 ZephyrAlpha_BeltDaemon 自愈",
    ),
    ("session_id", "会话标识非法：修正袋 session_id（[A-Za-z0-9._-] ≤64）后重投"),
)
_DEAD_PRESCRIPTION_FALLBACK = {
    "env": "环境性失败（物品无辜）：直接 requeue 重投即可（瞬态环境争用类，requeue 即愈）",
    "item": "门禁物品性失败：按 dead_reason 中 gate 标识修复物品本身后重投",
    "other": "未归类死因：人工排查（python scripts/commit_queue.py health 看死因分类聚合）",
}


def dead_letter_prescription(reason: str) -> str:
    """死因→一键修复处方（M3.3）：特征串精确命中优先，未命中按三分类兜底。"""
    reason = reason or ""
    for marker, prescription in _DEAD_PRESCRIPTIONS:
        if marker in reason:
            return prescription
    return _DEAD_PRESCRIPTION_FALLBACK.get(classify_dead_reason(reason), _DEAD_PRESCRIPTION_FALLBACK["other"])


def _annotate_preflight_face_drift(item: dict, *, repo_root: Path | None = None) -> None:
    """E-4 TOCTOU 死信出口增信（观测级，非裁决——「预检非新权威」在册原则不变）。

    袋 meta.preflight_face（enqueue_item 登记三族判定时采的注册表面貌快照）与当前
    HEAD 面貌逐册比对：不一致 ⇒ 预检基础在入队后漂移（E-4 实锤形态：同会话预检
    passed 的袋仍死于 CREATE-GUARD）。只做三件事：meta 增 preflight_face_drift 明细、
    处方补「直接重投」指引、warning 留痕。任何故障静默跳过（观测面 fail-open，绝不
    影响死信本体落册）；未随快照的袋（历史件/跳过判定件）零开销直接返回。
    做不到的已登记（lane_q_notes）：不按漂移改判死因/不阻断落地——那会让预检升格为
    权威，须 Owner 门位。
    """
    face = (item.get("meta") or {}).get("preflight_face")
    if not isinstance(face, dict) or not face:
        return
    try:
        from scripts.governance.commit_queue_landing import (  # noqa: PLC0415
            resolve_base_blobs,
            resolve_base_head,
        )

        wt = repo_root if repo_root is not None else _REPO_ROOT
        current = resolve_base_blobs(wt, resolve_base_head(wt), list(face.keys()))
    except Exception as exc:  # noqa: BLE001 — 观测面故障静默（死信本体照常落册）
        logger.debug("[drain] E-4 面貌比对跳过（git 面不可用）: %s", exc)
        return
    drifted = {
        rel: {"preflight": pre_sha, "current": current.get(rel)}
        for rel, pre_sha in face.items()
        if pre_sha != current.get(rel)
    }
    if not drifted:
        return
    item["preflight_face_drift"] = drifted
    item["prescription"] = (
        f"{item.get('prescription') or ''}"
        "；另：入队预检后注册表面貌已漂移（E-4 TOCTOU 窗）——若内容未变可直接重投，"
        "预检将按新面貌重判"
    ).strip()
    logger.warning("[drain] qid=%s 预检注册表面漂移（E-4 增信）: %s", item.get("qid", "?"), sorted(drifted))


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
    # M2.2 冲突标记字节预扫（QCure st-qcure-20260925）：实现真源在
    # scripts/governance/enqueue_preflight.py，本处薄调用（延迟 import 与本文件既有
    # scripts.governance.* 引用同款防循环/直跑口径）。
    from scripts.governance.enqueue_preflight import (  # noqa: PLC0415
        CONFLICT_MARKER_REJECT_PRESCRIPTION,
        scan_conflict_markers,
    )

    out: list[tuple[str, bytes]] = []
    for rel in relpaths:
        norm = _validate_relpath(rel)  # 轻检前置：CLI 读盘前就拦穿越（不读越界文件）
        abs_path = worktree_root / norm
        try:
            content = abs_path.read_bytes()
        except OSError as exc:
            raise QueueReject(f"文件读取失败: {norm}（{exc}）") from exc
        # blob 落袋前字节预扫：历史 50 笔死因在入队口快败（零垃圾 blob，无条件扫描
        # 不依赖 merge 状态触发——pre-commit check-merge-conflict 教训）
        hit = scan_conflict_markers(norm, content, max_bytes=_MAX_BLOB_BYTES)
        if hit:
            raise QueueReject(f"{CONFLICT_MARKER_REJECT_PRESCRIPTION}\n  {hit}")
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
        # M1.1 入队预检挂线（QCure st-qcure-20260925）：三裸入口零预检补口（此前唯一有
        # 预检的是交互正门 GC:847-855）。在冲突扫之后、enqueue_item 落袋之前锁外只读
        # 执行；v1 skip 集={SESSION-REQUIRED, CLAIM-REQUIRED}（假红风暴防线，作业簿
        # 矿#2，真源=enqueue_preflight.ENQUEUE_SKIP_GATES）；blocking→QueueReject
        # exit 2+逐门禁处方；预检设施异常→模块内 warn+放行（degraded fail-open），
        # 绝不因预检故障堵入队。
        from scripts.governance.enqueue_preflight import run_enqueue_preflight  # noqa: PLC0415

        pf_prescription = run_enqueue_preflight(worktree_root, [p for p, _ in files], args.session, message or "")
        if pf_prescription:
            raise QueueReject(pf_prescription)
        depends_on = [d.strip() for d in (args.depends_on or "").split(",") if d.strip()]
        base_head = args.base_head
        from scripts.governance.commit_queue_landing import (  # noqa: PLC0415
            resolve_base_blobs,
            resolve_base_head,
        )

        if base_head is None:
            # B 段接通（F-AUDIT-QUEUE-04，2026-09-24）：裸 CLI 与交互正门同口径自取
            # 基底——此前只有 --base-head 显式传入才有，缺省即 None（两套入口不一致）。
            # 非 git 目录（tmp 隔离测试）取不到→None，行为与修复前逐字节一致。
            from scripts.governance.commit_queue_landing import (  # noqa: PLC0415
                resolve_base_blobs,
                resolve_base_head,
            )

            base_head = resolve_base_head(worktree_root)
        # W17 治本（案卷 mine_snapshot_selfconsistency_witness W17）：base_blobs 必须对
        # **生效基底**恒取——此前躲在 `if base_head is None` 分支里，于是显式传 --base-head
        # 反而把见证层素材置空，而死信 cascade_stale 的官方处方原文就教人这么传。
        # 现与 requeue 侧同源；非 git 目录返全 None＝逐字节旧行为。
        base_blobs = resolve_base_blobs(worktree_root, base_head, [p for p, _ in files])
        item = enqueue_item(
            args.session,
            message or "",
            files,
            queue_root=args.queue_root,
            options=EnqueueOptions(
                base_head=base_head,
                base_blobs=base_blobs,
                depends_on=depends_on or None,
                # Rx-5：出队优先级（int，缺省 0，越大越先出队）经 meta_extra 入袋——
                # 与 C1 合批判据同源（_c1_target_meta_ok 优先级不混，防止合并改写调度主键）
                meta_extra={"priority": args.priority},
                # C1 合批判据键透传（同会话+同 worktree-root 短窗自动并；跨会话/跨
                # worktree 永不并——红线）。归一化在 enqueue_item 内做。
                worktree_root=str(worktree_root),
            ),
        )
    except QueueReject as exc:
        # fail-closed：报错非静默（66 号 §11 #3：畸形项全拦且报错非静默）
        print(f"DENIED: {exc}", file=sys.stderr)
        return 2
    absorbed = item.get("absorbed")
    print(f"ENQUEUED: {item['qid']} (files={len(item['files'])}, supersedes={item['meta']['supersedes']})")
    if absorbed:
        # C1 同会话短窗自动合批回执：absorbed qid 已并入上件（其序列号已消耗、不落队列）
        print(f"C1-MERGED: {absorbed['qid']}({absorbed['files']} files) -> {item['qid']}（同会话短窗自动合批）")
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
        base_head = args.base_head
        if base_head is None and args.worktree_root:
            # requeue 也必须带基底：死信重投是恢复通道，若再投 base_head=None 的袋，
            # 注册表项会撞上 _merge_registry_file 的 fail-closed（QUEUE-04 收紧后）。
            from scripts.governance.commit_queue_landing import (  # noqa: PLC0415
                resolve_base_head,
            )

            base_head = resolve_base_head(args.worktree_root)
        result = requeue_dead_item(
            args.qid,
            queue_root=args.queue_root,
            worktree_root=args.worktree_root,
            session_id=args.session,
            message=message,
            base_head=base_head,
            from_bag=args.from_bag,
            force=args.force,
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


def _cmd_dead_archive(args: argparse.Namespace) -> int:
    try:
        result = dead_archive_letters(
            args.queue_root,
            days=args.days,
            verify_landed=not args.no_verify_landed,
            execute=args.execute,
        )
    except DeadArchiveError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    kept = result["kept"]
    print(
        f"DEAD-ARCHIVE: archived={len(result['archived'])} "
        f"kept={sum(kept.values()) + result['skipped_corrupt']} "
        f"(young={kept['young']}/unlanded={kept['unlanded']}/revival_in_flight={kept['revival_in_flight']}"
        f"/skipped_corrupt={result['skipped_corrupt']}) days={args.days:g} verify={result['verify']} "
        f"execute={args.execute} bag={result['bag']}"
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for p in result["prescriptions"][:10]:  # 人读面只列前 10 封处方（全量走 --json）
            paths = ",".join(p["unlanded_paths"][:3])
            print(f"  PRESCRIPTION {p['qid']}: {p['prescription']}（未落路径如 {paths}）")
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
    p_enq.add_argument(
        "--priority",
        type=int,
        default=0,
        help="Rx-5 出队优先级（int，缺省 0，越大越先出队；负数=低于缺省；同优先级保持到达序 FCFS）",
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
    p_rq.add_argument(
        "--force",
        action="store_true",
        help="越过重投熔断（requeue_count≥3 连败拒绝）显式越权——meta.requeue_forced=true 留痕",
    )
    p_rq.add_argument("--no-bootstrap", action="store_true", help="重入队后不尝试自举排空")
    p_rq.set_defaults(func=_cmd_requeue)

    p_cl = sub.add_parser("cleanup", help=f"done/ TTL 清理（默认 {_DONE_TTL_DAYS_DEFAULT:.0f} 天；dead/ 永不清理）")
    p_cl.add_argument("--done-ttl-days", type=float, default=_DONE_TTL_DAYS_DEFAULT, help="done/ 保留天数")
    p_cl.set_defaults(func=_cmd_cleanup)

    p_da = sub.add_parser(
        "dead-archive",
        help="dead/ 官方归档（RB2：mv 非删可逆；默认 dry-run 零写，--execute 才动盘；落地校验默认开）",
    )
    p_da.add_argument("--days", type=float, default=7.0, help="年龄门槛天数（dead_at 基准，解析失败回退 mtime）")
    p_da.add_argument(
        "--no-verify-landed",
        action="store_true",
        help="显式关闭落地校验（已取代型批量归档先例复用；输出留 verify=off 痕）",
    )
    p_da.add_argument("--execute", action="store_true", help="动盘归档（缺省=dry-run 只打印计划零盘面变化）")
    p_da.add_argument("--json", action="store_true", help="机器可读输出（archived 清单/kept 分布/未落处方）")
    p_da.set_defaults(func=_cmd_dead_archive)

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
