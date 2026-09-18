# [BLUEPRINT] MOD-RESCHED-APPLY | docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md | §4-P2-b
# [MODULE] scripts.governance.apply_resource_plan
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml; scripts/governance/generators/generate_resource_profile_registry.py（三源解析/
#   触发器抽取/漂移检测/schtasks 探针——函数级 import 复用，禁克隆解析）;
#   src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py（三查+C-8 受闸验，
#   getattr 鸭子类型——P2-a 未合入时自动降级跑现有三查并在报告注明）; zephyr.shared.io.file_utils（CAS 写）
# [CONSUMERS] 主会话 P3 全局重排班（本工具是唯一合法写回通道）; tests/scripts/test_apply_resource_plan.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] R-A：工具产 patch 不产表——时间窗只写时间真源（schedule.yaml 槽位 cron 行 /
#   register_*.ps1 触发器构造行），注册表 window_expr 永不被本工具直接改写（表是 [GENERATED]）；
#   exclusive_group 的 §2.1 生产者=人，其真源位置就是表内人审字段（生成器不刷新它），故它是
#   本工具唯一允许的表内 patch 目标，且改后经再生复验（合并保全体制下磁盘值即生效值）；
#   写回前必过闸：patch→tmp 沙箱真源→沙箱再生→闸三查(+C-8)→新增 block=0 才允许 --apply；
#   旧值全量存档先于任何生产写（--rollback 一键逐字节还原，apply 后复验失败自动回滚）；
#   文本级精准替换：未命中的字节零改动（注释/键序/缩进/引号风格/行尾约定全保真），ps1 保持纯 ASCII；
#   方案定位失败即整单拒绝（无部分落地）；沙箱与生产文件物理隔离（自检/测试零生产写）
# [MODIFY-GUARD] cron 语义口径=注册表标准 cron（0=周日）；写回 schedule.yaml 必须经
#   standard→APScheduler（0=周一）反向平移，与生成器 _aps_dow_to_standard 成对，改一处必改两处
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 方案缺失/YAML 重复键/未知 task_id/不可物化窗/seed 实体改窗=退出码 2 且零生产写；
#   真源或生成器不可读、沙箱再生失败、CAS 冲突=退出码 4（已写文件自动回滚）；闸阻断=退出码 2
# [TESTS] tests/scripts/test_apply_resource_plan.py
# [A_module] module_id=MOD-RESCHED-APPLY | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 排班方案
#   fields: .runtime/sessions/<sid>/staging/resource_plan.yaml（{task_id: {new_window_cron|new_hour/
#     new_minute/new_dow/new_times, new_exclusive_group?, rationale_zh}}）
#   code: load_plan
# - id: I2
#   name: 时间真源与画像表
#   fields: schedule.yaml 槽位 / register_*.ps1 触发器 / 生成器 §3.C 种子 / 注册表
#   code: locate_all
# 层: 算法
# - id: A1
#   name_zh: ① 方案→真源归属定位
#   name_en: locate_all
#   intro: 生成器各源实体 → schedule_slot / ps1_task / drill_schedule / plan_doc_seed 四类归属
#     + 可改性判定（drill 源经 getattr 探测，P4-α 车道缺席时行为不变）
#   desc: 复用 parse_ps1_entities/parse_schedule_slots/manual_entities/parse_drill_entities/
#         collect_ps1_task_claims（task→真源映射单源，禁第二套命名规则）
#   inputs: I1, I2
#   outputs: Located 清单 + locate_all.truth_rels（沙箱须带走的机器真源集）
# - id: A2
#   name_zh: ② 文本级精准 patch
#   name_en: build_patches
#   intro: cron 行 / 触发器构造行 / exclusive_group 三类行级替换，未命中字节零改动
#   desc: 每处 patch 立即用生成器自己的抽取函数复验（ps1 走 _extract_trigger_exprs、槽位走
#         parse_schedule_slots(scratch)），重抽结果≠方案预期即拒绝——"改的行就是真源读的那行"
#         的机器证明
#   inputs: A1
#   outputs: Patch 清单 + unified diff
# - id: A3
#   name_zh: ③ 受闸验（沙箱）
#   name_en: build_sandbox + regen_sandbox + gate_findings
#   intro: patch 落 tmp 沙箱真源→沙箱再生→闸三查+漂移查(+C-8)→新增 block=0 才放行 --apply
#   desc: 沙箱=从 root 复制生成器/闸/真源/词表源，子进程跑再生（--skip-schtasks 保 hermetic）；
#         同时做物化校验（方案意图须在再生后的表里如实出现）
#   inputs: A2
#   outputs: gate findings + materialization problems
# - id: A4
#   name_zh: ④ 存档 + 落地 + 复验
#   name_en: run_plan(apply) + archive_originals + write_production + restore_archive
#   intro: 旧值全量入 .runtime/sessions/<sid>/archive/plan_<ts>/→CAS 写生产→子进程再生+重渲视图
#   desc: 落地后复验（真源↔表 0 漂移 + 0 新增 block + 物化成功），失败自动逐字节回滚；
#         --rollback 按 manifest 还原
#   inputs: A3
#   outputs: 真源/表/视图三处一致
# - id: A5
#   name_zh: ⑤ 三角对账
#   name_en: triangle_report
#   intro: 表 ↔ 真源重抽 ↔ schtasks 实测 三方 window/在册一致性 summary
#   desc: 复用生成器 detect_registry_drift + query_schtasks + collect_ps1_task_claims（只读探针，
#         非 Windows/无权限降级为探针健康码，不静默）
#   inputs: A2, I2
#   outputs: triangle 段
# 层: 输出
# - id: O1
#   name_zh: 受闸 diff 与对账报告
#   name_en: plan report json
#   intro: --report-json 机器可读全链证据（定位命中/patch 行数/闸 findings/三角对账/存档路径）
#   downstream: P3 重排班前后对比报告；主会话 gateway 提交说明
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A2 --> A5
# A4 --> O1
# A5 --> O1
"""apply_resource_plan — 排班方案 → 时间真源受闸写回一竿子（MOD-RESCHED-APPLY，v2 方案 P2-b）。

Owner 目标②（AI 重排班并更新模块）的执行机构。裁定 R-A：排班写回走真源不走表——
`config/resource_profile_registry.yaml` 是 [GENERATED] 静态清单（手工增删=红线），所以
"改排班"在机器层面只能是"改 schedule.yaml 的 cron 行 / 改 register_*.ps1 的触发器构造行"，
表由再生跟上。本工具产 patch，不产表。

一竿子五步（任一环节失败=整单拒绝，绝不部分落地）：

1. **定位**：方案里每个 task_id 归到四类真源之一——``schedule_slot``（schedule.yaml 槽位，
   时间真源=其 ``cron:`` 行，APScheduler dow 语义）/ ``ps1_task``（某个 register_*.ps1，
   时间真源=其触发器构造行）/ ``drill_schedule``（第 4 真源源，窗档由 frequency 结构量归一
   而来，无 cron 行可改）/ ``plan_doc_seed``（生成器 §3.C 种子，**无机器时间真源**）；后两类
   改窗即拒（先按 P4 收编成前两类再排班）。映射复用生成器自己的解析函数，不另立第二套。
2. **产 patch**：文本级精准替换（保注释/键序/缩进/引号风格/行尾约定；ps1 保持纯 ASCII）。
   每处 patch 立刻用生成器自己的抽取函数复验（ps1 走 ``_extract_trigger_exprs``、槽位走
   ``parse_schedule_slots(scratch)``）：重抽 ≠ 方案预期，说明"改的行不是真源读的那行"，拒。
   方案窗档另须自身能被 croniter 展开——闸的求和臂对坏 cron 是"跳过该实体"，若不在这里拦，
   越界 cron 会伪装成"该班永不触发"把既存冲突误判为消解。
   cron 口径：方案里的 cron 是**注册表口径（标准 cron，0=周日）**；写回 schedule.yaml 时自动
   反向平移成 APScheduler 口径（0=周一），与生成器的归一函数成对。
3. **受闸验**：patch 应用到 tmp 沙箱真源 → 沙箱跑再生 → 闸三查（互斥组交叠/内存天花板/E0 交易
   窗）+ 漂移查 +（P2-a 已合入时）C-8 同 pool 同窗并发查 → 要求"本次引入的 block=0"（现盘既存
   block 另列 pre_existing，不拿别人的账拦这一次）。
4. **存档 + 落地 + 复验**：旧值全量入 ``.runtime/sessions/<sid>/archive/plan_<ts>/``（原文件 +
   逐文件 unified diff + manifest）→ CAS/safe_write_text 写生产真源 → 子进程调再生 + 重渲周历
   视图 → 落地后复验；复验失败自动回滚。
5. **三角对账**：表 ↔ 真源重抽 ↔ schtasks 实测 三方一致性 summary（复用生成器
   ``detect_registry_drift``/``query_schtasks``；探针不可用时降级为健康码，不静默）。

确定性三条（P2-b 真实 dry-run 实测换来的，改代码前先读）：

- **评估瞬间按日取整**：闸以 ``now`` 起算 28 天地平线，未取整时两次相隔 21 秒的 dry-run
  会因末端某刻进出展开集而报出不同 block 集合（实测 23 处差异），判定与幂等指纹一起变成
  "看几点跑"。故 ``now = pin_eval_now(...)``，真实时刻只留在 ``ts_utc`` 与存档目录名里。
- **非生产 root 强制不外呼**：``tri_skip = skip_schtasks or root != REPO_ROOT``——自测跑在
  tmp 副本上时 schtasks 反映的是本机生产的在册态，探它等于把无关状态写进报告。
- **清单按文本排序**：pre_existing/new/resolved 三张 block 表输出前排序，人和指纹都别看运气。

用法::

    # 默认 dry-run：只产 patch 与报告，零生产写
    python scripts/governance/apply_resource_plan.py --plan <path> --report-json
    python scripts/governance/apply_resource_plan.py --plan <path> --map          # 真源命中全表
    python scripts/governance/apply_resource_plan.py --plan <path> --apply --session <sid>
    python scripts/governance/apply_resource_plan.py --rollback .runtime/sessions/<sid>/archive/plan_<ts>

退出码：0=OK（dry-run 通过 / apply 落地并复验成功）；2=方案非法或闸阻断（零生产写）；
3=命令行参数错误；4=环境/子进程/CAS 异常（已写文件自动回滚）。
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import inspect
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

if str(Path(__file__).resolve().parents[2] / "src") not in sys.path:  # 匿名 bootstrap，REPO_ROOT 归 canonical（SSOT）
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

logger = logging.getLogger(__name__)

__all__ = [
    "main", "run_plan", "load_plan", "locate_all", "build_patches",
    "build_sandbox", "regen_sandbox", "gate_findings", "materialization_problems",
    "triangle_report", "archive_originals", "restore_archive", "stable_hash", "cron_ok",
    "pin_eval_now",
    "PlanError", "EnvError", "Located", "Patch", "TimeSpec",
]

# --- 路径真源（全部经 root 拼接；root 可注入 = 测试在沙箱里跑同一份代码）----------------
SCHEDULE_REL = "src/zephyr/data/config/schedule.yaml"
REGISTRY_REL = "config/resource_profile_registry.yaml"
VIEW_REL = "src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js"
GENERATOR_REL = "scripts/governance/generators/generate_resource_profile_registry.py"
VIEW_GENERATOR_REL = "scripts/governance/generators/generate_resource_week_view.py"
GATE_REL = "src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py"
EXECUTOR_VOCAB_REL = "src/zephyr/data/scheduler.py"
AUDIT_POOL_REL = "src/zephyr/gov_audit/resource_aware_pool.py"
SANDBOX_COPY_RELPATHS = (SCHEDULE_REL, EXECUTOR_VOCAB_REL, AUDIT_POOL_REL, REGISTRY_REL)

DEFAULT_SID = os.environ.get("ZEPHYR_SESSION_ID") or "p2b-apply-resource-plan"
PLAN_STAGING_REL = "staging"
PLAN_DEFAULT_NAME = "resource_plan.yaml"

EXIT_OK = 0
EXIT_REFUSED = 2
EXIT_USAGE = 3
EXIT_ENV = 4

KIND_SLOT = "schedule_slot"
KIND_PS1 = "ps1_task"
KIND_SEED = "plan_doc_seed"
# 第 4 真源源（P4-α/L-5：drill_schedule.yaml）——存在与否由生成器是否有 parse_drill_entities
# 决定（鸭子类型探测）；它的窗档是 frequency/day_of_month 结构量而非 cron 行，故不可写回。
KIND_DRILL = "drill_schedule"

TIME_FIELDS = ("new_window_cron", "new_hour", "new_minute", "new_dow", "new_times")
_GROUP_FIELD = "new_exclusive_group"
_ITEM_FIELDS = frozenset((*TIME_FIELDS, _GROUP_FIELD, "rationale_zh"))
_META_FIELDS = frozenset({"plan_id", "session", "title", "notes_zh", "items", "plan", "rationale_zh"})

_DOW_NAMES = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
_RE_HHMM = re.compile(r"^(\d{1,2}):(\d{2})$")
_RE_CRON_LINE = re.compile(r"^(?P<indent> {4})cron:\s*(?P<value>.*?)(?P<tail>\s+#.*)?$")
_RE_PS_WEEKLY = re.compile(r"-Weekly(?:\s+-DaysOfWeek\s+([\w,]+))?\s+-At\s+[\"']?(\d{1,2}:\d{2})[\"']?")
_RE_PS_DAILY = re.compile(r"-Daily\s+-At\s+[\"']?(\d{1,2}:\d{2})[\"']?")
_RE_PS_TIMES = re.compile(r"-Times\s+@\(([^)]*)\)")
_RE_PS_ANYNAME = re.compile(r"ZephyrAlpha[-_][A-Za-z0-9_]+")
# 闸 finding 文本尾部的代表瞬间（Finding.render 以全角括号附注）——幂等指纹里须抹平
_RE_AT_TAIL = re.compile(r"[（(]\s*at=[^)）]*[)）]")

# 每次落地除被 patch 的真源外还须底档的衍生件：再生会重写注册表、视图生成器会重写 rw-data.js，
# 回滚若只还原真源就留下"真源旧 + 表新"的半吊子态。视图在裸检可能尚不存在 → 允许缺席存档。
ALWAYS_ARCHIVED = (REGISTRY_REL, VIEW_REL)
ARCHIVE_OPTIONAL = frozenset({VIEW_REL})


class PlanError(Exception):
    """方案层拒绝（非法方案/不可物化/定位失败）→ 退出码 2，零生产写。"""


class EnvError(Exception):
    """环境层失败（依赖缺失/再生失败/CAS 冲突）→ 退出码 4。"""


# ---------------------------------------------------------------------------
# 兄弟模块装载与文本 IO
# ---------------------------------------------------------------------------
def load_sibling(rel: str, modname: str, root: Path):
    """按 root 相对路径装载模块（root 可注入；与闸装载生成器同一范式）。"""
    path = Path(root) / rel
    if not path.exists():
        raise EnvError(f"依赖模块缺失: {path}")
    spec = importlib.util.spec_from_file_location(modname, path)
    if spec is None or spec.loader is None:
        raise EnvError(f"模块装载失败: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001 — 兄弟模块破损（如 P2-a 在途）按环境失败处理
        raise EnvError(f"依赖模块装载异常 {path}: {str(exc)[:200]}") from exc
    return mod


def read_text(path: Path) -> tuple[str, str]:
    """读文件 → (LF 化文本, 原行尾约定)。行尾约定必须随行保存，否则回滚做不到逐字节还原。"""
    raw = Path(path).read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return raw.decode("utf-8").replace("\r\n", "\n"), newline


def write_text(path: Path, text: str, newline: str = "\n", expected_base_sha256: str | None = None) -> str:
    """CAS 文本写（热文件纪律：safe_write_text），行尾按原约定落盘 → 写后 sha256。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    res = safe_write_text(path, text, expected_base_sha256=expected_base_sha256, newline=newline)
    return str(res.after_sha256)


def sha256_bytes(data: bytes) -> str:
    """sha256_bytes implementation."""
    return hashlib.sha256(data).hexdigest()


def _utc_ts() -> str:
    """_utc_ts implementation."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# ① 方案解析（重复键硬拦：YAML 默认后者覆盖前者，排班方案里=悄悄丢掉一整条改窗）
# ---------------------------------------------------------------------------
class _DupKeyLoader(yaml.SafeLoader):
    """同层重复键即抛的 SafeLoader。"""

    def construct_mapping(self, node, deep: bool = False):  # noqa: FBT001, FBT002
        """construct_mapping implementation."""
        seen: list = []
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise PlanError(
                    f"方案 YAML 第 {key_node.start_mark.line + 1} 行重复键 {key!r}——"
                    "safe_load 会静默丢弃先出现的条目，排班方案不允许"
                )
            seen.append(key)
        return super().construct_mapping(node, deep=deep)


def load_plan(path: Path) -> tuple[dict, dict]:
    """方案文件 → (meta, {task_id: item})；裸映射与 ``items:``/``plan:`` 两种写法都收。"""
    p = Path(path)
    if not p.exists():
        raise PlanError(f"方案文件不存在: {p}")
    try:
        data = yaml.load(p.read_text(encoding="utf-8"), Loader=_DupKeyLoader)  # noqa: S506
    except PlanError:
        raise
    except yaml.YAMLError as exc:
        raise PlanError(f"方案 YAML 解析失败: {exc}") from exc
    if not isinstance(data, dict) or not data:
        raise PlanError("方案为空或不是映射")
    items = data.get("items") if isinstance(data.get("items"), dict) else (
        data.get("plan") if isinstance(data.get("plan"), dict) else None
    )
    if items is None:
        items = {k: v for k, v in data.items() if k not in _META_FIELDS}
        meta = {k: v for k, v in data.items() if k in _META_FIELDS}
        if not items:
            raise PlanError("方案里没有任何 task_id 条目（也没有 items: 段）")
    else:
        meta = {k: v for k, v in data.items() if k not in ("items", "plan")}
    if not items:
        raise PlanError("方案 items 为空")
    return meta, items


# ---------------------------------------------------------------------------
# cron / 时刻 helper（注册表口径=标准 cron，0=周日）
# ---------------------------------------------------------------------------
def cron_bands(expr: object) -> list[str] | None:
    """cron 文本 → 5/6 段 bands（段数非法返回 None）。"""
    if expr is None:
        return None
    parts = str(expr).split()
    return parts if len(parts) in (5, 6) else None


def band_sig(tok: object) -> str:
    """单个 cron 段的语义指纹：区间平展、前导零归一（'00'≡'0'，'1-5'≡'1,2,3,4,5'）。"""
    s = str(tok).strip()
    if s in ("*", "?"):
        return "*"
    if "/" in s:
        base, step = s.split("/", 1)
        return f"{band_sig(base)}/{step.strip()}"
    if "-" in s:
        lo, hi = s.split("-", 1)
        if not (lo.strip().isdigit() and hi.strip().isdigit()):
            return s
        lo_i, hi_i = int(lo), int(hi)
        vals = set(range(lo_i, hi_i + 1)) if hi_i >= lo_i else set(range(lo_i, 7)) | set(range(0, hi_i + 1))
        return ",".join(str(v) for v in sorted(vals))
    if s.isdigit():
        return str(int(s))
    return s


def expr_sig(window_expr: object) -> frozenset[str]:
    """window_expr（可 '|'-多段）→ 语义指纹集（供"方案预期 vs 真源重抽"比对）。"""
    if not window_expr:
        return frozenset()
    out: set[str] = set()
    for seg in str(window_expr).split("|"):
        seg = seg.strip()
        if not seg:
            continue
        bands = cron_bands(seg)
        out.add("<unparsable>" if bands is None else " ".join(band_sig(b) for b in bands))
    return frozenset(out)


def single_int(tok: object) -> int | None:
    """single_int implementation."""
    s = str(tok).strip()
    return int(s) if s.isdigit() else None


def hhmm(tok: object) -> tuple[int, int] | None:
    """hhmm implementation."""
    m = _RE_HHMM.match(str(tok).strip())
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    return (h, mi) if h <= 23 and mi <= 59 else None


def fmt_hh(h: int, mi: int, pad_hour: bool) -> str:
    """fmt_hh implementation."""
    return f"{h:02d}:{mi:02d}" if pad_hour else f"{h}:{mi:02d}"


def _compress_dow(vals: list[int]) -> str:
    """连续段压缩为区间（与生成器 _aps_dow_to_standard 同规则，保证往返一致）。"""
    if not vals:
        return "*"
    runs: list[str] = []
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[j + 1] == vals[j] + 1:
            j += 1
        runs.append(str(vals[i]) if j == i else f"{vals[i]}-{vals[j]}")
        i = j + 1
    return ",".join(runs)


def expand_dow_field(field_text: object) -> list[int] | None | bool:
    """标准 cron dow 段 → 升序日序号；``*`` → None；不可平展（步长/日名）→ False。"""
    f = str(field_text).strip()
    if f in ("*", "?"):
        return None
    out: set[int] = set()
    for part in f.split(","):
        part = part.strip()
        if not part or "/" in part:
            return False
        if "-" in part:
            lo, hi = part.split("-", 1)
            if not (lo.strip().isdigit() and hi.strip().isdigit()):
                return False
            lo_i, hi_i = int(lo), int(hi)
            out.update({d % 7 for d in range(lo_i, hi_i + 1)} if hi_i >= lo_i
                       else set(range(lo_i, 7)) | set(range(0, hi_i + 1)))
        elif part.isdigit():
            out.add(int(part) % 7)
        else:
            return False
    return sorted(out)


def standard_dow_to_aps(field_text: object) -> str:
    """标准 cron dow（0=周日）→ APScheduler dow（0=周一）：逐元素 −1 mod 7 后重压缩。

    与生成器 ``_aps_dow_to_standard``（真源→表侧 +1）成对；往返不对称由沙箱再生复验兜住。
    """
    f = str(field_text).strip()
    vals = expand_dow_field(f)
    if vals is None:
        return "*"
    if vals is False:
        return f  # 不可平展：原样透传，让复验判死（不在这里悄悄写坏真源）
    return _compress_dow([(d - 1) % 7 for d in vals])


def dow_to_ps_names(field_text: object) -> list[str] | None | bool:
    """标准 cron dow → PowerShell DaysOfWeek 名列表（``*`` → []=每日；不可平展 → False）。"""
    vals = expand_dow_field(field_text)
    if vals is None:
        return []
    if vals is False:
        return False
    return [_DOW_NAMES[d] for d in vals]


def norm_dow_field(raw: object) -> str:
    """方案 new_dow → 标准 cron dow 段（接受 ``*``、int、list[int]、list[日名]、区间文本）。"""
    if raw is None:
        return "*"
    if isinstance(raw, (int,)) or (isinstance(raw, str) and raw.strip() in ("*", "?")):
        if isinstance(raw, int):
            vals = [raw % 7]
        else:
            return "*"
    else:
        seq = raw if isinstance(raw, (list, tuple)) else [raw]
        vals = []
        for x in seq:
            if isinstance(x, str) and not (x.strip().isdigit() or set("-,").intersection(x)):
                hit = [i for i, n in enumerate(_DOW_NAMES) if n.lower() == x.strip().lower()]
                if not hit:
                    raise PlanError(f"new_dow 日名 {x!r} 不认识（须 Sunday..Saturday 或 0-6，0=周日）")
                vals.append(hit[0])
            elif str(x).strip().isdigit():
                vals.append(int(str(x).strip()) % 7)
            else:
                exp = expand_dow_field(str(x))
                if exp is False or not exp:
                    raise PlanError(f"new_dow 段 {x!r} 不可平展（须 0-6 数字/区间/日名，0=周日）")
                vals.extend(exp)
    vals = sorted(set(vals))
    if vals == [0, 1, 2, 3, 4, 5, 6]:
        return "*"
    return _compress_dow(vals)


@dataclass
class TimeSpec:
    """方案条目里一条时间改动的中间表示（cron 一律注册表口径）。"""

    mode: str  # "cron" | "hmd" | "times"
    cron: str | None = None
    dom: str = "*"
    month: str = "*"
    second: str | None = None
    hour: int | None = None
    minute: int | None = None
    dow: str = "*"
    times: list[str] | None = None

    def describe(self) -> str:
        """describe implementation."""
        if self.mode == "times":
            return f"new_times={self.times}"
        if self.mode == "cron":
            return f"new_window_cron={self.cron}"
        return f"new_hour={self.hour} new_minute={self.minute} new_dow={self.dow!r}"

    def requested_exprs(self) -> list[str]:
        """方案预期的注册表窗档（ps1/slot 目标各自的物化形态）。"""
        if self.mode == "times":
            return [f"{hhmm(t)[1]} {hhmm(t)[0]} * * *" for t in (self.times or [])]  # type: ignore[misc]
        if self.mode == "cron" and self.cron:
            return [self.cron]
        return [f"{self.minute} {self.hour} {self.dom} {self.month} {self.dow}"]


def cron_ok(expr: str) -> bool | None:
    """cron 语义合法性（True/False；croniter 不可用时 None=无从判定）。

    为什么工具必须自己判：闸的求和臂对坏 cron 是**跳过该实体**（`_budget_rows` 口径），
    于是 "0 99 * * *" 这类越界窗会被当成"永不触发"→ 既存冲突"被消解"→ 受闸验放行。
    宁拦不漏：方案里的每一条窗档必须能被闸真正展开，才谈得上被它保护。
    """
    try:
        from croniter import croniter
    except ImportError:  # pragma: no cover — croniter 是闸/生成器共同硬依赖
        return None
    bands = cron_bands(expr)
    if bands is None:
        return False
    probe = " ".join(bands[1:]) if len(bands) == 6 else expr  # 6 段剥秒段，与 gate.expand_windows 同口径
    try:
        return bool(croniter.is_valid(probe))
    except Exception:  # noqa: BLE001 — 判定器自身异常=无从判定，交复验兜
        return None


def resolve_time_spec(item: dict, current_expr: str | None, what: str = "") -> TimeSpec | None:
    """方案条目 → TimeSpec（未给的段沿用现值；不可物化即拒）。无时间字段返回 None。"""
    keys = [k for k in TIME_FIELDS if k in item]
    if not keys:
        return None
    if "new_window_cron" in item and len(keys) > 1:
        raise PlanError(f"{what}new_window_cron 与 new_hour/new_minute/new_dow/new_times 互斥"
                        "（前者是全量重写，混填会让'哪个说了算'变成隐式规则）")
    if "new_times" in item and set(keys) != {"new_times"}:
        raise PlanError(f"{what}new_times 只允许单独出现（它是多触发点清单的全量重写）")

    if "new_times" in item:
        raw = item["new_times"]
        if not isinstance(raw, (list, tuple)) or not raw:
            raise PlanError(f"{what}new_times 必须是非空列表")
        times: list[tuple[int, int]] = []
        for t in raw:
            hm = hhmm(t)
            if hm is None:
                raise PlanError(f"{what}new_times 元素 {t!r} 不是 HH:MM")
            times.append(hm)
        uniq = sorted({(h, m) for h, m in times})
        spec = TimeSpec(mode="times", times=[f"{h:02d}:{m:02d}" for h, m in uniq])
        _check_crons(spec, what)
        return spec

    if "new_window_cron" in item:
        bands = cron_bands(item["new_window_cron"])
        if bands is None:
            raise PlanError(f"{what}new_window_cron 段数非法（须 5 或 6 段，"
                            f"实得 {str(item['new_window_cron']).split()!r}）")
        if len(bands) == 6:
            second, mi, h, dom, month, dow = bands
        else:
            second, (mi, h, dom, month, dow) = None, bands
        if str(dow).strip() == "7":
            dow = "0"  # 标准 cron 7≡0=周日；生成器往返产出 0，此处先归一免生歧义
            bands[-1] = "0"
        for name, tok in zip(("minute", "hour", "dom", "month", "dow"), (mi, h, dom, month, dow), strict=True):
            if not str(tok).strip():
                raise PlanError(f"{what}cron 的 {name} 段为空")
        spec = TimeSpec(mode="cron", cron=" ".join(bands), dom=dom, month=month, second=second, dow=dow)
        spec.minute = single_int(mi)
        spec.hour = single_int(h)
        _check_crons(spec, what)
        return spec

    cur = cron_bands(current_expr)
    if cur is None:
        raise PlanError(f"{what}现值不是可解析 cron（{current_expr!r}），只能用 new_window_cron 全量重写")
    b = cur[-5:]
    spec = TimeSpec(mode="hmd", second=cur[-6] if len(cur) == 6 else None, dom=b[2], month=b[3], dow=b[4])
    spec.minute = int(item["new_minute"]) if "new_minute" in item else _require_int(b[0], "minute", current_expr, what)
    spec.hour = int(item["new_hour"]) if "new_hour" in item else _require_int(b[1], "hour", current_expr, what)
    if "new_dow" in item:
        spec.dow = norm_dow_field(item["new_dow"])
    if not 0 <= spec.minute <= 59:  # type: ignore[misc]
        raise PlanError(f"{what}new_minute={spec.minute} 越界（0-59）")
    if not 0 <= spec.hour <= 23:  # type: ignore[misc]
        raise PlanError(f"{what}new_hour={spec.hour} 越界（0-23）")
    _check_crons(spec, what)
    return spec


def _check_crons(spec: TimeSpec, what: str) -> None:
    """方案预期的每条窗档必须真能被 croniter 展开（见 `cron_ok` 的宁拦不漏理由）。"""
    for expr in spec.requested_exprs():
        if cron_ok(expr) is False:
            raise PlanError(f"{what}窗档 {expr!r} 不是合法 cron（croniter 判不可展开）——"
                            "越界/拼错的 cron 在闸的求和臂里是「跳过该实体」，会被误读成"
                            "「该班永不触发」，从而把既存冲突当成被消解而放行")


def _require_int(tok: str, band: str, current_expr: object, what: str) -> int:
    """_require_int implementation."""
    v = single_int(tok)
    if v is None:
        raise PlanError(f"{what}现值 {current_expr!r} 的 {band} 段={tok!r} 不是单值，"
                        "无法只改另一段——请给 new_window_cron 全量重写")
    return v


def strip_ps1_comments(text: str) -> str:
    """ps1 → 去注释正文（与生成器 ``_iter_ps1_code`` 同口径：只在登记语境匹配）。"""
    return "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith("#"))


# ---------------------------------------------------------------------------
# ①′ 定位：task_id → 真源归属（复用生成器三源解析，映射单源）
# ---------------------------------------------------------------------------
@dataclass
class Located:
    task_id: str
    kind: str
    truth_rel: str
    slot: str | None = None
    ps1_task_name: str | None = None
    window_type: str | None = None
    window_expr: str | None = None
    status: str | None = None
    pool: str | None = None
    resource_class: str | None = None
    exclusive_group: list[str] = field(default_factory=list)
    patchable_window: bool = True
    why_not: str = ""
    pending_expr: str | None = None  # patch 后由生成器抽取函数复验得到的窗档


def locate_all(gen, root: Path) -> dict[str, Located]:
    """生成器各源实体 → {task_id: Located}（全量覆盖，含不可改窗的 seed/drill/event）。"""
    out: dict[str, Located] = {}
    ps1_ents, w_ps1 = gen.parse_ps1_entities()
    slot_ents, w_slot = gen.parse_schedule_slots()
    seeds = gen.manual_entities()
    claims = gen.collect_ps1_task_claims()  # {ZephyrAlpha_X: sch_x}
    name_by_tid = {tid: name for name, tid in claims.items()}
    warnings: list[str] = [str(x) for x in list(w_ps1) + list(w_slot)]

    def _common(e: dict) -> dict:
        """_common implementation."""
        return dict(
            window_type=e.get("window_type"), window_expr=e.get("window_expr"),
            status=e.get("status"), pool=e.get("pool"), resource_class=e.get("resource_class"),
            exclusive_group=[str(x) for x in (e.get("exclusive_group") or [])],
        )

    for e in slot_ents:
        tid = str(e["task_id"])
        out[tid] = Located(
            task_id=tid, kind=KIND_SLOT,
            truth_rel=str(e.get("schedule_truth_source") or SCHEDULE_REL),
            slot=tid[len("data_slot_"):] if tid.startswith("data_slot_") else tid,
            **_common(e),
        )
    for e in ps1_ents:
        tid = str(e["task_id"])
        loc = Located(
            task_id=tid, kind=KIND_PS1,
            truth_rel=str(e.get("schedule_truth_source") or ""),
            ps1_task_name=name_by_tid.get(tid),
            **_common(e),
        )
        if not e.get("window_expr"):
            loc.patchable_window = False
            loc.why_not = (
                "该计划任务的真源触发器是 -AtLogOn/-Once（常驻或补跑型），ps1 里没有可改的时刻"
                "字面量；要排窗须先把触发器改写成定时触发（另批施工）——本工具不凭空造触发器"
            )
        out[tid] = loc
    # 第 4 真源源（P4-α/L-5）：鸭子类型探测——该车道在飞，函数缺席时本工具行为不变。
    parse_drill = getattr(gen, "parse_drill_entities", None)
    drill_ents: list[dict] = []
    if callable(parse_drill):
        try:
            drill_ents, w_drill = parse_drill()
            warnings += [str(x) for x in (w_drill or [])]
        except Exception as exc:  # noqa: BLE001 — 兄弟车道探针异常不得炸定位链（如实留痕）
            warnings.append(f"drill_source_probe_failed: {str(exc)[:160]}")
    for e in drill_ents:
        tid = str(e["task_id"])
        out[tid] = Located(
            task_id=tid, kind=KIND_DRILL,
            truth_rel=str(e.get("schedule_truth_source") or ""),
            **_common(e), patchable_window=False,
            why_not=(
                f"实体来自第 4 真源源 {e.get('schedule_truth_source')}（window_type={e.get('window_type')}）："
                "其窗档由 frequency/day_of_month/months 结构量归一而来，真源里没有可改写的 cron 行；"
                "本工具改它=伪造派生值（下次再生即被真源冲掉）。要给演练排窗须先在 drill_schedule.yaml "
                "侧扩窗语义（P4/L-5 后续批），不在此越权"
            ),
        )
    for e in seeds:
        tid = str(e["task_id"])
        out[tid] = Located(
            task_id=tid, kind=KIND_SEED,
            truth_rel=str(e.get("schedule_truth_source") or ""),
            **_common(e), patchable_window=False,
            why_not=(
                f"实体类型={tid.split('_')[0]}*（window_type={e.get('window_type')}）：时间真源是生成器 "
                "§3.C 种子/方案文档而非机器可读 cron，无窗可改；须先按 v2 方案 P4（L-5/L-8）收编成 "
                "schedule.yaml 槽位或 register_*.ps1 触发器，才能被排班工具写回"
            ),
        )
    locate_all.warnings = warnings  # type: ignore[attr-defined]
    # 沙箱还须带走的"额外机器真源"：仅生成器再生时会读的解析型源（.ps1 由 build_sandbox
    # 整批复制；§3.C 种子的真源指针是文档/代码，生成器不去读它，拖进沙箱只是噪音）。
    locate_all.truth_rels = frozenset(  # type: ignore[attr-defined]
        v.truth_rel for v in out.values() if v.kind in (KIND_SLOT, KIND_DRILL) and v.truth_rel
    )
    return out


# ---------------------------------------------------------------------------
# ② patch 构造（行级精准替换 + 生成器自己的抽取函数复验）
# ---------------------------------------------------------------------------
@dataclass
class Patch:
    rel_path: str
    kind: str  # slot_cron | ps1_trigger | registry_group
    task_id: str
    line_no: int
    old_line: str
    new_line: str
    old_value: str
    new_value: str
    rationale_zh: str
    noop: bool = False
    note: str = ""


def find_slot_cron_line(lines: list[str], slot: str) -> int:
    """schedule.yaml 里定位槽位的 cron 行（槽位块=缩进 ≥4 的字段行；注释/兄弟键即止）。"""
    key_re = re.compile(rf"^  {re.escape(slot)}:\s*(#.*)?$")
    start = next((i for i, ln in enumerate(lines) if key_re.match(ln)), None)
    if start is None:
        raise PlanError(f"schedule.yaml 里找不到槽位 {slot!r} 的键行（槽位改名须同步定位器）")
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if not ln.strip():
            continue
        if not ln.startswith("    "):
            break  # 缩进不足 4 → 出了本槽位块（下一槽位键 / 顶层键 / 顶格注释）
        m = _RE_CRON_LINE.match(ln)
        if m:
            return j
    raise PlanError(f"槽位 {slot!r} 块内没有 cron: 行（该槽位非 cron 触发，或结构变更须同步本定位器）")


def patch_slot_cron(text: str, slot: str, aps_cron: str) -> tuple[str, int, str, str]:
    """替换槽位 cron 值（保留缩进/引号风格/行内注释）。返回 (新文本, 行号, 旧行, 新行)。"""
    lines = text.split("\n")
    idx = find_slot_cron_line(lines, slot)
    old_line = lines[idx]
    m = _RE_CRON_LINE.match(old_line)
    assert m is not None
    old_val = m.group("value").strip()
    quote = '"' if old_val[:1] in ('"', "'") and old_val[-1:] == old_val[:1] else ""
    inner = old_val[1:-1] if quote else old_val
    new_cron = _pad_bands_like_truth(aps_cron, inner)
    new_line = f'{m.group("indent")}cron: {quote}{new_cron}{quote}{m.group("tail") or ""}'
    lines[idx] = new_line
    return "\n".join(lines), idx + 1, old_line, new_line


def _pad_bands_like_truth(cron: str, truth_inner: str) -> str:
    """逐段沿用真源的补零风格（只补"方案确实改到且真源该段本是 0X"的段）。

    旧口径按首段判补零、却只补小时段，两处失真：真源分钟段 "00" 的补零保不住，而
    "00 2 * * 1" 只改分钟时会被顺手改成 "30 02 …"——没改的段也动了字节，破 R-A 的
    "未命中零改动"。故补零判定必须**逐段**做。
    """
    nb = cron.split()
    ob = str(truth_inner).split()
    for i in range(min(len(nb), len(ob))):
        if re.fullmatch(r"0\d", ob[i]) and nb[i].isdigit() and len(nb[i]) == 1:
            nb[i] = nb[i].zfill(2)
    return " ".join(nb)


def ps1_trigger_line_indices(code_lines: list[str], task_name: str) -> list[int]:
    """归属判定：哪些触发器构造行属于 task_name（多任务共文件时的定锤逻辑）。

    与生成器 ``_extract_trigger_exprs`` 的分段口径同源（任务名向前回看/后向截止），但这里
    定位的是**行**：候选行=含 -Weekly/-Daily/-Times@ 且带字面时刻；归属=该行最近一个在其
    之前的任务名，前面没有则归给最近一个在其之后的任务名。
    """
    name_lines = [i for i, ln in enumerate(code_lines) if _RE_PS_ANYNAME.search(ln)]
    cands = [i for i, ln in enumerate(code_lines)
             if _RE_PS_WEEKLY.search(ln) or _RE_PS_DAILY.search(ln) or _RE_PS_TIMES.search(ln)]
    owners: dict[int, str] = {}
    for i in cands:
        prev = [n for n in name_lines if n < i]
        nxt = [n for n in name_lines if n > i]
        pick = prev[-1] if prev else (nxt[0] if nxt else None)
        owners[i] = code_lines[pick] if pick is not None else ""
    mine = [i for i in cands if task_name in owners[i] or (not name_lines and task_name in code_lines[i])]
    return mine


def patch_ps1_trigger(text: str, task_name: str, spec: TimeSpec) -> tuple[str, int, str, str]:
    """改 ps1 触发器构造行（Daily↔Weekly 形态随 dow 约束自动切换）。返回 (新文本,行号,旧行,新行)。"""
    lines = text.split("\n")
    code_idx = [i for i, ln in enumerate(lines) if not ln.strip().startswith("#")]
    code_lines = [lines[i] for i in code_idx]
    mine = ps1_trigger_line_indices(code_lines, task_name)
    if not mine:
        raise PlanError(
            f"{task_name}: 在本 ps1 里定位不到带字面时刻的触发器构造行"
            "（-AtLogOn/-Once 常驻型，或触发器写法已变更须同步本工具）"
        )
    times_lines = [i for i in mine if _RE_PS_TIMES.search(code_lines[i])]
    if len(mine) > 1 and not times_lines:
        raise PlanError(
            f"{task_name}: 命中 {len(mine)} 条触发器构造行且无法唯一判定目标"
            "（多任务共文件或一次多段触发，须人工拆方案）"
        )
    idx = times_lines[0] if (spec.mode == "times" and times_lines) else mine[0]
    line = code_lines[idx]

    if spec.mode == "times":
        m_times = _RE_PS_TIMES.search(line)
        if m_times is None:
            raise PlanError(f"{task_name}: new_times 只能改写 -Times @(...) 形态的触发器")
        q = '"' if '"' in m_times.group(1) else ("'" if "'" in m_times.group(1) else '"')
        frag = "-Times @(" + ", ".join(f"{q}{t}{q}" for t in spec.times) + ")"
        new_line = line[: m_times.start()] + frag + line[m_times.end():]
    else:
        if _RE_PS_TIMES.search(line):
            old_pts = len(re.findall(r"\d{1,2}:\d{2}", _RE_PS_TIMES.search(line).group(1)))  # type: ignore[union-attr]
            raise PlanError(
                f"{task_name}: 真源是 -Times @(...) 多触发点清单（{old_pts} 个点），单点改写会"
                "静默丢弃其余触发点；请给 new_times 完整清单"
            )
        m_weekly = _RE_PS_WEEKLY.search(line)
        m_daily = _RE_PS_DAILY.search(line)
        anchor = m_weekly or m_daily
        if anchor is None:
            raise PlanError(f"{task_name}: 定位到的行里没有可改写的 -Weekly/-Daily 触发器（写法变更）")
        dow_field = spec.dow
        dow_names = dow_to_ps_names(dow_field)
        if dow_names is False:
            raise PlanError(f"{task_name}: new_dow={dow_field!r} 不可平展为 DaysOfWeek 清单")
        if spec.mode == "cron":
            b = cron_bands(spec.cron)[-5:]  # type: ignore[index]
            for band_name, tok in (("dom", b[2]), ("month", b[3])):
                if tok != "*":
                    raise PlanError(
                        f"{task_name}: ps1 触发器只能表达 Daily/Weekly 单一时刻，cron 的 {band_name} "
                        f"段={tok!r} 不可物化（月度型须改挂 schedule.yaml 槽位）"
                    )
            if single_int(b[0]) is None or single_int(b[1]) is None:
                raise PlanError(
                    f"{task_name}: cron 分/时段={b[0]!r}/{b[1]!r} 不是单一时刻，"
                    "无法物化成 ps1 触发器（多时刻须给 new_times）"
                )
            hour, minute = int(b[1]), int(b[0])
        else:
            hour, minute = spec.hour, spec.minute  # type: ignore[assignment]
            if spec.dom != "*" or spec.month != "*":
                raise PlanError(f"{task_name}: ps1 触发器无法表达 {spec.dom}/{spec.month} 日期段")
        lit = anchor.group(anchor.lastindex) if anchor.lastindex else None
        pad_hour = bool(lit) and len(str(lit).split(":")[0]) == 2 and str(lit).startswith("0")
        quoted = '"' in anchor.group(0) or "'" in anchor.group(0)
        at = fmt_hh(int(hour), int(minute), pad_hour=pad_hour)
        at_txt = f'"{at}"' if quoted else at
        frag = f"-Weekly -DaysOfWeek {','.join(dow_names)} -At {at_txt}" if dow_names else f"-Daily -At {at_txt}"
        new_line = line[: anchor.start()] + frag + line[anchor.end():]

    if not new_line.isascii():
        raise PlanError(f"{task_name}: 改写后的 ps1 行含非 ASCII——PowerShell 5.1 无 BOM 按 GBK "
                        "解码中文会造出假语法错误（宪法 §9.7）")
    lines[code_idx[idx]] = new_line
    return "\n".join(lines), code_idx[idx] + 1, line, new_line


def entity_block_span(lines: list[str], task_id: str) -> tuple[int, int]:
    """注册表 entities 里定位 `- task_id: X` 块的 [start, end)。"""
    start = next((i for i, ln in enumerate(lines) if re.match(rf"^- task_id: {re.escape(task_id)}\s*$", ln)), None)
    if start is None:
        raise PlanError(f"注册表 entities 里找不到实体 {task_id!r}（条目由生成器产出，先查再生）")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("- ") and not lines[j].startswith("-  "):
            end = j
            break
    return start, end


def patch_registry_group(text: str, task_id: str, groups: list[str]) -> tuple[str, int, str, str]:
    """改注册表实体的 exclusive_group（§2.1 生产者=人 的人审字段，再生合并保全）。"""
    lines = text.split("\n")
    start, end = entity_block_span(lines, task_id)
    for i in range(start, end):
        m = re.match(r"^  exclusive_group:\s*(?P<val>.*?)\s*$", lines[i])
        if not m:
            continue
        old_block = [lines[i]]
        j = i + 1
        if m.group("val") == "":
            while j < end and lines[j].startswith("  - "):
                old_block.append(lines[j])
                j += 1
        new_block = ["  exclusive_group: []"] if not groups else (
            ["  exclusive_group:"] + [f"  - {g}" for g in groups]
        )
        lines[i:j] = new_block
        return "\n".join(lines), i + 1, "\n".join(old_block), "\n".join(new_block)
    raise PlanError(f"实体 {task_id!r} 块内没有 exclusive_group 字段（18 字段 schema 变更须同步本工具）")


def unified_diff(rel: str, old_text: str, new_text: str) -> str:
    """unified_diff implementation."""
    return "".join(difflib.unified_diff(
        old_text.splitlines(keepends=True), new_text.splitlines(keepends=True),
        fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm="\n",
    ))


# ---------------------------------------------------------------------------
# ②′ 方案 → patch 清单（含生成器复验）
# ---------------------------------------------------------------------------
def build_patches(gen, root: Path, located: dict[str, Located], items: dict,
                  scratch: Path) -> tuple[list[Patch], dict[str, str]]:
    """把方案条目变成逐文件 patch + 逐文件改后全文。

    每处 patch 用生成器自己的抽取函数复验，不符即拒。改后全文按 task_id 序在同一份
    ``texts`` 上链式累积后直接返回——不留第二条"重放"代码路径，避免两处推导分叉。
    """
    root = Path(root).resolve()  # 绝对化：见 run_plan docstring（relative_to 口径）
    scratch.mkdir(parents=True, exist_ok=True)
    texts: dict[str, tuple[str, str]] = {}  # rel → (text, newline)
    patches: list[Patch] = []
    groups_vocab = set(gen.GROUPS)

    def _text(rel: str) -> tuple[str, str]:
        """_text implementation."""
        if rel not in texts:
            try:
                texts[rel] = read_text(root / rel)
            except (OSError, UnicodeDecodeError) as exc:
                raise EnvError(f"真源不可读 {rel}: {exc}") from exc
        return texts[rel]

    for tid in sorted(items):
        item = items[tid] or {}
        loc = located.get(tid)
        if loc is None:
            raise PlanError(f"未知 task_id {tid!r}：不在生成器各源真源（ps1/schedule.yaml/drill/§3.C 种子）里")
        if not isinstance(item, dict):
            raise PlanError(f"条目 {tid} 必须是映射")
        unknown = set(item) - _ITEM_FIELDS
        if unknown:
            raise PlanError(f"条目 {tid} 含未知字段 {sorted(unknown)}（可用={sorted(_ITEM_FIELDS)}）——"
                            "拼错的字段会被静默忽略，排班不允许")
        rationale = str(item.get("rationale_zh") or "").strip()
        if not rationale:
            raise PlanError(f"条目 {tid} 缺 rationale_zh（R-E：排班权归 AI+闸，但每条改动必须留人可复核理由）")
        time_keys = [k for k in TIME_FIELDS if k in item]
        if not time_keys and _GROUP_FIELD not in item:
            raise PlanError(f"条目 {tid} 既无时间字段也无 {_GROUP_FIELD}——空改动")

        # ── A. 时间窗改动：只写时间真源（R-A 硬线）
        if time_keys:
            if not loc.patchable_window:
                raise PlanError(f"条目 {tid} 改窗被拒：{loc.why_not}")
            spec = resolve_time_spec(item, loc.window_expr, what=f"{tid}: ")
            assert spec is not None
            if loc.kind == KIND_SLOT:
                if spec.mode == "times":
                    raise PlanError(f"{tid}: new_times 只适用于 ps1 的 -Times @(...) 多触发点清单；"
                                    "schedule.yaml 槽位是单一 cron 表达式，改窗请用 new_window_cron")
                rel = _norm(loc.truth_rel if str(loc.truth_rel).endswith((".yaml", ".yml")) else SCHEDULE_REL)
                text, nl = _text(rel)
                lines = text.split("\n")
                if loc.slot is None:
                    raise PlanError(f"{tid}: 槽位名推断失败")
                idx = find_slot_cron_line(lines, loc.slot)
                cur_val = re.sub(r"^['\"]|['\"]$", "", (_RE_CRON_LINE.match(lines[idx]).group("value").strip()))  # type: ignore[union-attr]
                cur_bands = cron_bands(cur_val)
                if cur_bands is None:
                    raise PlanError(f"{tid}: 现值 cron 不可解析（{cur_val!r}）")
                if len(cur_bands) == 6 and spec.mode != "cron":
                    raise PlanError(f"{tid}: 现值是 6 段 cron（含秒段），增量改会静默丢秒段——"
                                    "请给 6 段 new_window_cron")
                if len(cur_bands) == 6 and spec.second is None:
                    raise PlanError(f"{tid}: 6 段 cron 必须显式给秒段")
                if len(cur_bands) == 5 and spec.second is not None:
                    raise PlanError(f"{tid}: 现值是 5 段 cron，方案给了秒段（会把槽位升成 6 段，"
                                    "须显式确认，本工具拒绝隐式改形态）")
                aps = _slot_aps_cron(spec)
                new_text, line_no, old_line, new_line = patch_slot_cron(text, loc.slot, aps)
                # 复验：把改后的整份 schedule.yaml 交给生成器自己的抽取函数重抽
                tmp = scratch / f"schedule_{_utc_ts()}_{len(patches)}.yaml"
                tmp.write_text(new_text, encoding="utf-8", newline="\n")
                try:
                    ents, warns = gen.parse_schedule_slots(tmp)
                finally:
                    tmp.unlink(missing_ok=True)
                got = {str(e["task_id"]): e for e in ents}
                pend = got.get(tid)
                if pend is None:
                    raise PlanError(f"{tid}: 改后重抽槽位消失（键名/缩进被破坏）")
                want_std = _requested_std(spec)
                if expr_sig(pend.get("window_expr")) != expr_sig(want_std):
                    raise PlanError(
                        f"{tid}: 真源改写未被生成器物化成预期窗（重抽={pend.get('window_expr')!r} "
                        f"预期={want_std!r}）——定位到了不是真源读的那行"
                    )
                if warns:
                    raise PlanError(f"{tid}: 改后 schedule.yaml 触发抽取告警：{warns}")
                texts[rel] = (new_text, nl)
                loc.pending_expr = str(pend.get("window_expr"))
                patches.append(Patch(
                    rel_path=rel, kind="slot_cron", task_id=tid, line_no=line_no,
                    old_line=old_line, new_line=new_line,
                    old_value=str(loc.window_expr), new_value=loc.pending_expr,
                    rationale_zh=rationale, noop=(old_line == new_line),
                    note=f"槽位 {loc.slot}（APScheduler dow 口径写回）",
                ))
            else:  # KIND_PS1
                rel = _norm(loc.truth_rel)
                text, nl = _text(rel)
                new_text, line_no, old_line, new_line = patch_ps1_trigger(text, loc.ps1_task_name or "", spec)
                pend_exprs = gen._extract_trigger_exprs(strip_ps1_comments(new_text), loc.ps1_task_name or "")
                want = expr_sig(_requested_std(spec))
                if not pend_exprs:
                    raise PlanError(f"{tid}: 改后 ps1 触发器重抽为空（写法不再被生成器识别）")
                got_sig = expr_sig("|".join(pend_exprs))
                if spec.mode == "times":
                    if got_sig != expr_sig("|".join(spec.requested_exprs())):
                        raise PlanError(f"{tid}: -Times 清单重抽 {pend_exprs} ≠ 方案 {spec.times}")
                elif got_sig != want:
                    raise PlanError(
                        f"{tid}: 真源改写未被生成器物化成预期窗（重抽={pend_exprs} 预期={sorted(want)}）"
                        "——定位到了不是真源读的那行"
                    )
                texts[rel] = (new_text, nl)
                loc.pending_expr = "|".join(pend_exprs)
                patches.append(Patch(
                    rel_path=rel, kind="ps1_trigger", task_id=tid, line_no=line_no,
                    old_line=old_line, new_line=new_line,
                    old_value=str(loc.window_expr), new_value=loc.pending_expr,
                    rationale_zh=rationale, noop=(old_line == new_line),
                    note=f"计划任务 {loc.ps1_task_name}",
                ))

        # ── B. 互斥组改动：人审字段，真源位置就是表内该字段
        if _GROUP_FIELD in item:
            raw = item[_GROUP_FIELD]
            if not isinstance(raw, (list, tuple)) or any(not isinstance(x, str) for x in raw):
                raise PlanError(f"{tid}: {_GROUP_FIELD} 必须是字符串列表（组名枚举收口在表头 groups:）")
            new_groups = [str(x) for x in raw]
            bad = [g for g in new_groups if g not in groups_vocab]
            if bad:
                raise PlanError(
                    f"{tid}: 未知互斥组 {bad}——合法组={sorted(groups_vocab)}；"
                    "新组名须先在生成器 GROUPS 登记（代码批），排班工具不开加组子的口子"
                )
            rel = _norm(REGISTRY_REL)
            text, nl = _text(rel)
            new_text, line_no, old_line, new_line = patch_registry_group(text, tid, new_groups)
            texts[rel] = (new_text, nl)
            patches.append(Patch(
                rel_path=rel, kind="registry_group", task_id=tid, line_no=line_no,
                old_line=old_line, new_line=new_line,
                old_value=",".join(loc.exclusive_group), new_value=",".join(new_groups),
                rationale_zh=rationale, noop=(old_line == new_line),
                note="人审字段（§2.1 生产者=人；再生合并保全）",
            ))
    return patches, {rel: text for rel, (text, _nl) in texts.items()}


def _requested_std(spec: TimeSpec) -> str:
    """方案预期窗档（**注册表口径=标准 cron，0=周日**）的规范文本，用于与生成器重抽比对。

    这里刻意不做任何 dow 平移：生成器两侧（ps1 触发器抽取 / schedule.yaml 的
    ``_aps_dow_to_standard``）产出的 window_expr 都是标准口径，方案口径也定义为标准口径，
    两侧同口径才能直接比指纹。APS 口径只存在于写回真源那一步（``_slot_aps_cron``），
    生成器随后又平移回来——往返是否闭合，正是本函数与沙箱再生复验要证的事。
    """
    if spec.mode == "times":
        return "|".join(spec.requested_exprs())
    if spec.mode == "cron" and spec.cron:
        bands = cron_bands(spec.cron)
        if bands is not None:
            return " ".join(bands[-5:])  # 生成器物化时丢秒段，比对同口径丢秒段
    return " ".join([str(spec.minute), str(spec.hour), spec.dom, spec.month, spec.dow])


def _norm(rel: str) -> str:
    """_norm implementation."""
    return str(rel).replace("\\", "/")


# ---------------------------------------------------------------------------
# ③ 沙箱与受闸验
# ---------------------------------------------------------------------------
def build_sandbox(root: Path, sandbox: Path, patched: dict[str, str],
                  extra_rels: tuple[str, ...] | frozenset[str] = ()) -> Path:
    """从 root 复制真源/生成器/闸/词表源 → sandbox，再把 patch 后的文本覆盖进去。

    ``extra_rels``：locate_all 发现的额外机器真源（如第 4 源 drill_schedule.yaml）。沙箱
    再生必须看到与生产同一 populations 的源，否则生成器会把沙箱里看不见的实体判成
    ``orphaned_source``（=沙箱闸验的人口与生产不同口径，差分失效）。
    """
    root, sandbox = Path(root), Path(sandbox)
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True)
    for rel in (*SANDBOX_COPY_RELPATHS, *sorted(set(extra_rels) - set(SANDBOX_COPY_RELPATHS))):
        src = root / rel
        if not src.exists():
            if rel in SANDBOX_COPY_RELPATHS:
                raise EnvError(f"沙箱依赖缺失: {src}")
            continue  # 额外源本就随实体有无（drill 缺席时生成器自己会告警，不在此造像）
        dst = sandbox / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    for rel in (GENERATOR_REL, GATE_REL):
        src = root / rel
        if not src.exists():
            raise EnvError(f"沙箱依赖缺失: {src}")
        dst = sandbox / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    view_src = root / VIEW_GENERATOR_REL  # 可选：沙箱内的闸验用不到，留着只为 --keep-sandbox 可复盘
    if view_src.exists():
        vdst = sandbox / VIEW_GENERATOR_REL
        vdst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(view_src, vdst)
    scripts = sandbox / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    found = sorted((root / "scripts").glob("register_*.ps1"))
    if not found:
        raise EnvError(f"{root / 'scripts'} 下无 register_*.ps1（生成器 I1 真源源缺席）")
    for ps1 in found:
        shutil.copy2(ps1, scripts / ps1.name)
    for rel, text in patched.items():
        dst = sandbox / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8", newline="")
    return sandbox


def regen_sandbox(sandbox: Path, skip_schtasks: bool = True) -> Path:
    """沙箱跑再生（子进程；PYTHONPATH 指回真仓 src 以解析 zephyr.shared.io）。"""
    out = sandbox / REGISTRY_REL
    env = dict(os.environ)
    pp = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = pp if not env.get("PYTHONPATH") else pp + os.pathsep + env["PYTHONPATH"]
    cmd = [sys.executable, str(sandbox / GENERATOR_REL), "--output", str(out)]
    if skip_schtasks:
        cmd.append("--skip-schtasks")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, timeout=600)
    except Exception as exc:  # noqa: BLE001
        raise EnvError(f"沙箱再生进程失败: {str(exc)[:200]}") from exc
    if r.returncode != 0:
        raise EnvError(f"沙箱再生退出码 {r.returncode}: tail(out)={r.stdout[-400:]!r} tail(err)={r.stderr[-400:]!r}")
    return out


def gate_findings(gate, entities: list[dict], repo_root: Path, now: datetime,
                 focus: set[str] | None = None) -> dict:
    """闸三查 + 漂移查（repo_root 口径真源）+ C-8（P2-a 就绪才跑，否则报告注明降级）。

    findings 以**结构记录**返回（rendered/severity/code/ids）而不只是文本：判定"本次是否
    新账"要按 (臂, reason_code, 涉及实体) 比对，而 C-8 的文本里带代表刻 ``at=``——同一条存量
    冲突改前/改后可能落在不同瞬间，拿全文比会把别人的账算到这一次头上（反之亦然）。

    漂移查的 repo_root 决定"拿哪套真源对哪张表"：沙箱验=沙箱真源对沙箱再生表，
    基线=未打补丁的沙箱再生表（见 run_plan；现盘表按构造是滞后的，直接拿它当基线=混口径）。

    ``focus``：P2-a 给 C-8 的 own-scope 归因集（宪法 §3 "存量债不连坐本提交"）。按真实签名
    投递——兄弟代理在途改签名是常态，参数不存在就降级并留痕，不炸整条验收链路。
    """
    def _sig_names(fn) -> set[str]:
        """_sig_names implementation."""
        try:
            return set(inspect.signature(fn).parameters)
        except (TypeError, ValueError):  # noqa: PERF203 — builtin/部分装饰器不可省
            return set()

    notes: list[str] = []

    def _run(name: str, *a, focus_arg: set[str] | None = None, repo_root_arg: Path | None = None):
        """_run implementation."""
        fn = getattr(gate, name, None)
        if fn is None:
            return {"error": f"check_absent: {name}"}
        kw: dict = {}
        names = _sig_names(fn)
        if focus_arg is not None:
            if "focus" in names:
                kw["focus"] = focus_arg
            else:
                notes.append(f"{name}: 签名无 focus 参数——本轮 C-8 归因降级为全量判定+基线差分")
        if repo_root_arg is not None:
            if "repo_root" in names:
                kw["repo_root"] = Path(repo_root_arg)
            else:
                notes.append(f"{name}: 签名无 repo_root 参数——漂移查按闸自身 REPO_ROOT 口径")
        try:
            fs = list(fn(*a, **kw))
        except Exception as exc:  # noqa: BLE001 — 单检查臂异常不得炸整条验收链路（显式记账）
            return [{"rendered": f"<check_error> {name}: {str(exc)[:180]}", "severity": "block",
                     "code": f"<check_error:{name}>", "ids": [f"<{name}>"]}]
        out = []
        for f in fs:
            render = getattr(f, "render", None)
            out.append({
                "rendered": render() if callable(render) else str(f),
                "severity": str(getattr(f, "severity", "?")),
                "code": str(getattr(f, "reason_code", "?")),
                "ids": sorted(str(x) for x in (getattr(f, "task_ids", None) or [])),
            })
        return out

    c8_available = hasattr(gate, "check_pool_concurrency")
    out: dict = {
        "check_overlap_group": _run("check_overlap_group", entities, now),
        "check_mem_ceiling": _run("check_mem_ceiling", entities, now),
        "check_e0_trading": _run("check_e0_trading", entities, now),
        "check_truth_drift": _run("check_truth_drift", entities, repo_root_arg=repo_root),
        "c8_available": c8_available,
    }
    out["check_pool_concurrency"] = (
        _run("check_pool_concurrency", entities, now, focus_arg=focus) if c8_available else []
    )
    if not c8_available:
        out["c8_note"] = ("P2-a 的 check_pool_concurrency（v2 方案 C-8 同 pool 同窗并发/同刻不同组）"
                          "未就绪——本轮只跑三查+漂移查，同刻跨组冲突可能漏检")
    if notes:
        out["arm_notes"] = notes
    return out


def block_records(findings: dict) -> list[dict]:
    """block 级 findings（检查臂异常/缺席也按阻断构造——宁拦不漏）。

    只看 ``check_*`` 臂：gate_findings 还挂 c8_available/c8_note/arm_notes（list[str]）等
    说明性键，把它们当 finding 字典取 .get 会在"某臂签名降级、恰好写了 arm_notes"时炸掉
    整条验收链——那是工具的账，不是闸的账。
    """
    out: list[dict] = []
    for arm, items in findings.items():
        if not str(arm).startswith("check_"):
            continue
        if isinstance(items, dict):  # 检查臂缺席：闸改了这个函数名≠这条检查不用做
            out.append({"arm": arm, "rendered": str(items.get("error", "check_arm_absent")),
                        "severity": "block", "code": "<check_arm_absent>", "ids": [f"<{arm}>"]})
            continue
        if not isinstance(items, list):
            continue
        for f in items:
            if isinstance(f, dict) and (f.get("severity") == "block"
                                        or str(f.get("code", "")).startswith("<check_error")):
                out.append({**f, "arm": arm})
    return out


def block_keys(bl: list[dict]) -> set[tuple]:
    """结构键集（臂, reason_code, 涉及实体）——改前后差分的比对单位。"""
    return {(b["arm"], b["code"], tuple(b["ids"])) for b in bl}


def block_lines(findings: dict) -> list[str]:
    """人读/文本口径的 block 清单（判定用 block_records+block_keys，这里只是出口）。"""
    return [f"{b['arm']}: {b['rendered']}" for b in block_records(findings)]


def materialization_problems(entities: list[dict], located: dict[str, Located], items: dict, patches: list[Patch]) -> list[str]:
    """方案意图必须在再生后的表里如实出现（时间值不搬家；被合并保全遮蔽/被解析吞=没落地）。"""
    problems: list[str] = []
    by_tid = {str(e.get("task_id")): e for e in entities if isinstance(e, dict)}
    for tid in sorted(items):
        ent = by_tid.get(tid)
        if ent is None:
            problems.append(f"{tid}: 再生后实体消失")
            continue
        loc = located[tid]
        if loc.pending_expr is not None:
            if expr_sig(ent.get("window_expr")) != expr_sig(loc.pending_expr):
                problems.append(
                    f"{tid}: 表内 window_expr={ent.get('window_expr')!r} ≠ 真源重抽="
                    f"{loc.pending_expr!r}（再生未物化）"
                )
        if _GROUP_FIELD in items[tid]:
            want = sorted(str(x) for x in items[tid][_GROUP_FIELD])
            got = sorted(str(x) for x in (ent.get("exclusive_group") or []))
            if want != got:
                problems.append(
                    f"{tid}: 表内 exclusive_group={got} ≠ 方案={want}（人审字段未生效——"
                    "再生在 patch 之前跑过或被别的写者覆盖）"
                )
    return problems


# ---------------------------------------------------------------------------
# ④ 三角对账：表 ↔ 真源重抽 ↔ schtasks 实测
# ---------------------------------------------------------------------------
def triangle_report(gen, registry_path: Path, root: Path, tids: list[str],
                    skip_schtasks: bool = False) -> dict:
    """三方一致性 summary（只读探针；schtasks 不可用降级为健康码，不静默）。"""
    data = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8")) or {}
    table = list(data.get("entities") or [])
    table_by = {str(e.get("task_id")): e for e in table if isinstance(e, dict)}
    ps1_ents, _w1 = gen.parse_ps1_entities()
    slot_ents, _w2 = gen.parse_schedule_slots()
    seeds = gen.manual_entities()
    parse_drill = getattr(gen, "parse_drill_entities", None)
    drill_ents: list[dict] = []
    if callable(parse_drill):
        try:
            drill_ents = list(parse_drill()[0])
        except Exception:  # noqa: BLE001 — 探针性缺源：拿不到就不据此判幽灵（如实留痕在 warnings）
            drill_ents = []
    # 三方对账的"真源重抽"角必须与生成器的合并口径同源：四源齐（ps1+槽位+drill+§3.C 种子），
    # 少一源就会把该源实体全报成 ghost_on_disk/表有真源无——那是探针自己的账，不是排班的账。
    fresh_by = {str(e["task_id"]): e for e in list(ps1_ents) + list(slot_ents) + list(drill_ents) + list(seeds)}
    drifts = gen.detect_registry_drift(table, list(fresh_by.values()))
    claims = gen.collect_ps1_task_claims()
    name_by_tid: dict[str, str] = {}
    for name, tid in claims.items():
        name_by_tid.setdefault(str(tid), name)

    live: dict[str, list[str]] = {}
    probe: list[str] = []
    probed = False
    if skip_schtasks:
        probe = ["schtasks_probe_skipped（--skip-schtasks：本轮不判第 5 真源源，仅表↔真源两角）"]
    else:
        try:
            live, probe = gen.query_schtasks()
            probed = True
        except Exception as exc:  # noqa: BLE001 — 探针任何异常都降级成健康码
            probe = [f"schtasks_probe_exception: {str(exc)[:160]}"]

    rows = []
    for tid in sorted(set(tids)):
        ent = table_by.get(tid, {})
        fr = fresh_by.get(tid, {})
        task_name = name_by_tid.get(tid)
        status = sorted(live.get(task_name) or []) if task_name else []
        if not task_name:
            os_state = ["<in_process_or_manual_no_os_task>"]
        elif status:
            os_state = status
        elif probed:
            os_state = ["<not_registered>"]  # 探针可用而查无此任务=真差集
        else:
            os_state = ["<not_probed>"]  # 没看=不能下结论
        t_expr = ent.get("window_expr")
        f_expr = fr.get("window_expr")
        if tid not in fresh_by:
            verdict = "表有真源无"  # 幽灵实体：表里挂着而三源都不认
        elif not f_expr:
            verdict = "不适用"  # 无机器 cron 可比（种子/常驻/事件型）
        else:
            verdict = "一致" if expr_sig(t_expr) == expr_sig(f_expr) else "漂移"
        rows.append({
            "task_id": tid,
            "table_window_expr": t_expr,
            "truth_window_expr": f_expr if f_expr else "<无机器时间真源>",
            "truth_source": ent.get("schedule_truth_source") or fr.get("schedule_truth_source"),
            "os_task_name": task_name,
            "schtasks_status": os_state,
            "table_vs_truth": verdict,
            "table_status": ent.get("status"),
        })
    counted = [r for r in rows if r["os_task_name"]]
    return {
        "rows": rows,
        "whole_table_drift": drifts,
        "schtasks_probe_problems": probe,
        "summary": {
            "changed_or_queried_tasks": len(rows),
            "truth_aligned": sum(1 for r in rows if r["table_vs_truth"] == "一致"),
            "truth_drifted": sum(1 for r in rows if r["table_vs_truth"] in ("漂移", "表有真源无")),
            "no_machine_truth": sum(1 for r in rows if r["table_vs_truth"] == "不适用"),
            "os_registered": sum(1 for r in counted if not str(r["schtasks_status"][0]).startswith("<")),
            "os_absent_or_disabled": sum(1 for r in counted
                                         if str(r["schtasks_status"][0]) in {"<not_registered>"}
                                         or "disabled" in str(r["schtasks_status"]).lower()),
            "os_not_probed": sum(1 for r in counted if str(r["schtasks_status"][0]) == "<not_probed>"),
            "os_probe_available": probed,
        },
    }


# ---------------------------------------------------------------------------
# ⑤ 存档 / 落地 / 回滚
# ---------------------------------------------------------------------------
def archive_originals(archive_dir: Path, root: Path, rels: list[str], meta: dict) -> Path:
    """旧值全量存档（原文件逐字节 + manifest），先于任何生产写。"""
    ad = Path(archive_dir)
    (ad / "orig").mkdir(parents=True, exist_ok=True)
    (ad / "diff").mkdir(parents=True, exist_ok=True)
    files = []
    for rel in sorted(set(rels)):
        src = Path(root) / rel
        if not src.exists():
            if _norm(rel) in ARCHIVE_OPTIONAL:
                # 视图产物在裸检可能从未渲染过：记"事前不存在"，回滚据此删除本次新建件
                files.append({"rel_path": _norm(rel), "sha256": None, "bytes": 0, "absent": True})
                continue
            raise EnvError(f"待改真源不存在，拒绝在无底档的情况下写回: {src}")
        raw = src.read_bytes()
        dst = ad / "orig" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(raw)
        files.append({
            "rel_path": _norm(rel),
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
        })
    (ad / "manifest.json").write_text(json.dumps({**meta, "files": files}, ensure_ascii=False, indent=1),
                                      encoding="utf-8", newline="\n")
    return ad


def restore_archive(root: Path, archive_dir: Path) -> dict:
    """按 manifest 逐字节还原（原子替换 + 还原后校验；不做部分还原）。"""
    ad = Path(archive_dir)
    man_path = ad / "manifest.json"
    if not man_path.exists():
        raise EnvError(f"存档缺 manifest: {man_path}")
    man = json.loads(man_path.read_text(encoding="utf-8"))
    restored = []
    for f in man.get("files") or []:
        rel = f["rel_path"]
        dst = Path(root) / rel
        if f.get("absent"):
            # 事前不存在=本次落地新建的衍生件（视图）：还原到"不存在"才算逐字节可逆
            if dst.exists():
                aside = ad / "removed_by_rollback" / rel
                aside.parent.mkdir(parents=True, exist_ok=True)
                os.replace(str(dst), str(aside))
                restored.append({"rel_path": rel, "removed_as_created_by_apply": True,
                                 "before_sha256": sha256_bytes(aside.read_bytes())})
            else:
                restored.append({"rel_path": rel, "unchanged_absent": True})
            continue
        src = ad / "orig" / rel
        if not src.exists():
            raise EnvError(f"存档缺原文件，拒绝部分还原: {src}")
        raw = src.read_bytes()
        if f.get("sha256") and sha256_bytes(raw) != f["sha256"]:
            raise EnvError(f"存档自身指纹不符（底档被改动，拒绝据此回滚）: {src}")
        was = dst.read_bytes() if dst.exists() else None
        tmp = dst.parent / f".{dst.name}.p2b_rollback.tmp"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(raw)
        os.replace(str(tmp), str(dst))
        if dst.read_bytes() != raw:
            raise EnvError(f"回滚后校验失败: {dst}")
        restored.append({
            "rel_path": rel,
            "restored_sha256": sha256_bytes(raw),
            "before_sha256": sha256_bytes(was) if was is not None else None,
            "byte_identical_to_pre_apply": sha256_bytes(raw) == f.get("sha256"),
        })
    return {"archive_dir": _norm(ad), "plan_id": man.get("plan_id"), "restored": restored}


def write_production(root: Path, patched: dict[str, str], bases: dict[str, str]) -> list[dict]:
    """CAS 写生产文件（校验基准=受闸验时读到的内容，磁盘被他人推进即拒）。"""
    written = []
    for rel, text in patched.items():
        p = Path(root) / rel
        old_text, newline = read_text(p)
        base = content_sha256(old_text)
        if bases.get(rel) is not None and bases[rel] != base:
            raise EnvError(f"CAS 冲突：{rel} 在受闸验后被他人推进（期望 {bases[rel][:12]}，现盘 {base[:12]}）")
        after = write_text(p, text, newline=newline, expected_base_sha256=base)
        written.append({"rel_path": _norm(rel), "after_sha256": after})
    return written


def run_child(root: Path, rel: str, extra: list[str] | None = None) -> dict:
    """子进程调生产再生/视图渲染（落地后全链跟上）。"""
    cmd = [sys.executable, str(Path(root) / rel)] + list(extra or [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900, cwd=str(root))
    except Exception as exc:  # noqa: BLE001
        return {"script": _norm(rel), "rc": -1, "stdout": "", "stderr": str(exc)[:400]}
    return {"script": _norm(rel), "rc": r.returncode,
            "stdout": (r.stdout or "")[-600:], "stderr": (r.stderr or "")[-600:]}


# ---------------------------------------------------------------------------
# 编排：run_plan
# ---------------------------------------------------------------------------
def default_plan_path(root: Path, sid: str) -> Path:
    """default_plan_path implementation."""
    return Path(root) / ".runtime/sessions" / sid / PLAN_STAGING_REL / PLAN_DEFAULT_NAME


def pin_eval_now(t: datetime) -> datetime:
    """把闸窗档的评估瞬间钉到「上海墙钟当日 00:00」（返回 aware UTC）。

    为什么必须取整：闸的 expand_windows 以 ``now`` 起算 ``HORIZON_DAYS`` 天地平线，不取整时
    同一方案相隔几十秒的两次 dry-run 会因"地平线末端那一刻进不进展开集"而报出**不同的
    block 集合**（P2-b 真实 dry-run 实测：run1/run2 差异 23 处，全部来自此，与方案无关），
    幂等指纹等于自设 flaky，判定本身也变成"看运气几点跑"。取整到日首与 cron 墙钟网格对齐
    （上海 00:00 是整刻），并把今天已发生的时刻一并纳入判定——只会更保守，不会漏账。
    """
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        local = t.astimezone(ZoneInfo("Asia/Shanghai"))
        return local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    except Exception:  # noqa: BLE001 — 无 tzdata 时退回 UTC 日首（仍确定，只是网格偏 8h）
        return t.replace(hour=0, minute=0, second=0, microsecond=0)


def stable_hash(report: dict) -> str:
    """幂等指纹：剔除时间/路径等易变字段后对报告取 sha（同方案两次 dry-run 必须同值）。"""
    def _scrub(o):
        """_scrub implementation."""
        if isinstance(o, dict):
            return {k: _scrub(v) for k, v in o.items()
                    if k not in {"ts_utc", "elapsed_s", "sandbox", "archive_dir", "generated_at",
                                 "regen_stdout", "view_rc", "now_utc", "at", "restored", "written",
                                 "report_path", "sid", "session", "children", "plan_path"}
                    and not str(k).endswith("_at")}
        if isinstance(o, list):
            return [_scrub(v) for v in o]
        if isinstance(o, str):
            # finding 文本尾部的「（at=…）」是闸按当前时刻展开窗档挑的代表瞬间，
            # 与方案无关——两次 dry-run 跨分钟就会变，留着幂等指纹等于自设 flaky。
            return _RE_AT_TAIL.sub("（at=<scrubbed>）", o.replace("\\", "/"))
        return o
    return hashlib.sha256(json.dumps(_scrub(report), ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def run_plan(
    *,
    root: Path,
    plan_path: Path,
    session: str = DEFAULT_SID,
    apply: bool = False,
    sandbox_dir: Path | None = None,
    skip_schtasks: bool = False,
    now: datetime | None = None,
    keep_sandbox: bool = False,
) -> tuple[dict, int]:
    """一竿子：定位→产 patch→沙箱受闸验→（--apply）存档+落地+再生+重渲+复验。返回 (报告, 退出码)。

    root 必须是仓根（可为相对，内部即 resolve）：生成器用 relative_to(绝对 REPO_ROOT) 记
    schedule_truth_source，相对 root 会让逐 patch 复验直接抛 ValueError。
    """
    t0 = datetime.now(timezone.utc)
    root = Path(root).resolve()
    # 闸窗档评估瞬间按日取整（见 pin_eval_now）：真实运行时刻只留在 ts_utc/存档目录名里。
    now = pin_eval_now(now or t0)
    base_extra_rels: frozenset[str] = frozenset()

    def _stub(plan_id: str) -> dict:
        """_stub implementation."""
        return {
            "tool": "scripts/governance/apply_resource_plan.py",
            "plan_id": plan_id, "plan_path": _norm(plan_path), "session": session,
            "mode": "apply" if apply else "dry-run",
            "ts_utc": t0.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "items": [], "patches": [], "refusals": [],
        }

    # ── ⓪ 前置件（任一件不可用=契约出口码，绝不冒 traceback：ERROR_CONTRACT）
    try:
        gen = load_sibling(GENERATOR_REL, "p2b_gen", root)
        gate = load_sibling(GATE_REL, "p2b_gate", root)
    except EnvError as exc:
        rep = _stub(Path(plan_path).stem)
        rep["env_error"] = f"依赖模块不可装载: {exc}"
        rep["verdict"] = "env_fail"
        rep["report_sha256"] = stable_hash(rep)
        return rep, EXIT_ENV
    try:
        meta, items = load_plan(plan_path)
    except PlanError as exc:
        rep = _stub(Path(plan_path).stem)
        rep["refusals"].append({"stage": "load_plan", "reason": str(exc)})
        rep["verdict"] = "refused"
        rep["block_reasons"] = [str(exc)]
        rep["apply_note"] = "方案未通过装载校验——零生产写"
        rep["report_sha256"] = stable_hash(rep)
        return rep, EXIT_REFUSED
    try:
        located = locate_all(gen, root)
    except EnvError as exc:
        rep = _stub(str(meta.get("plan_id") or Path(plan_path).stem))
        rep["env_error"] = f"真源定位失败（生成器抽取臂异常）: {exc}"
        rep["verdict"] = "env_fail"
        rep["report_sha256"] = stable_hash(rep)
        return rep, EXIT_ENV
    base_extra_rels = frozenset(getattr(locate_all, "truth_rels", frozenset()))

    coverage = {
        "total_entities": len(located),
        "by_kind": {k: sum(1 for v in located.values() if v.kind == k)
                    for k in (KIND_SLOT, KIND_PS1, KIND_SEED, KIND_DRILL)},
        "window_patchable": sum(1 for v in located.values() if v.patchable_window),
        "extraction_warnings": list(getattr(locate_all, "warnings", [])),
    }
    report: dict = {
        "tool": "scripts/governance/apply_resource_plan.py",
        "plan_id": str(meta.get("plan_id") or Path(plan_path).stem),
        "plan_path": _norm(plan_path),
        "session": session,
        "mode": "apply" if apply else "dry-run",
        "ts_utc": t0.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "horizon_note": ("闸窗档地平线沿用 gate.HORIZON_DAYS（28 天）；评估瞬间按上海墙钟日首取整"
                         "（见 pin_eval_now）→ 同日重跑同方案报告逐字节可复现，跨日差异=地平线整体"
                         "前移一天，属真值变化而非工具抖动"),
        "eval_now_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "locate_coverage": coverage,
        "items": [],
        "patches": [],
        "refusals": [],
    }

    ad: Path | None = None

    def _finish(rep: dict, rc: int, *, drop_sandbox: bool = False) -> tuple[dict, int]:
        """所有出口的唯一收口：算幂等指纹 + 清临时真源 + 落地模式下把报告并入存档目录。"""
        shutil.rmtree(preverify, ignore_errors=True)
        if drop_sandbox and not keep_sandbox:
            shutil.rmtree(sandbox, ignore_errors=True)
        rep["report_sha256"] = stable_hash(rep)
        if ad is not None and ad.exists():
            try:
                (ad / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n",
                                                encoding="utf-8", newline="\n")
            except OSError as exc:  # 报告落档失败不得掩盖主链结论
                rep["report_archive_error"] = str(exc)[:200]
        return rep, rc

    # ── ① 定位命中表（先于 patch：让"哪几个真源文件会被碰"在最早处可见）
    for tid in sorted(items):
        loc = located.get(tid)
        report["items"].append({
            "task_id": tid,
            "located": None if loc is None else {
                "kind": loc.kind, "truth_source": loc.truth_rel, "slot": loc.slot,
                "ps1_task_name": loc.ps1_task_name, "window_type": loc.window_type,
                "current_window_expr": loc.window_expr, "status": loc.status,
                "pool": loc.pool, "exclusive_group": loc.exclusive_group,
                "patchable_window": loc.patchable_window, "why_not": loc.why_not,
            },
        })

    sandbox = Path(sandbox_dir) if sandbox_dir else root / ".runtime/tmp/apply_resource_plan_sandbox"
    # 逐 patch 复验的临时真源必须落在 root 之内：生成器 parse_schedule_slots 用
    # relative_to(自身 REPO_ROOT) 记 schedule_truth_source，落在 root 外会直接抛 ValueError。
    preverify = root / ".runtime/tmp/apply_resource_plan_preverify"

    # 「无 OS 副作用」判据：显式 --skip-schtasks，或 root 非生产仓（自测跑在 tmp 副本上，
    # 此时 schtasks 反映的是生产机的在册态，与本副本无关，探它只会污染幂等指纹）。
    tri_skip = bool(skip_schtasks) or Path(root).resolve() != REPO_ROOT

    # ── ② patch（含逐处复验）
    try:
        patches, patched_all = build_patches(gen, root, located, items, preverify)
    except PlanError as exc:
        report["refusals"].append({"stage": "build_patches", "reason": str(exc)})
        report["verdict"] = "refused"
        report["block_reasons"] = [str(exc)]
        report["apply_note"] = "方案未通过定位/patch 校验——零生产写（沙箱未建）"
        return _finish(report, EXIT_REFUSED)
    except EnvError as exc:
        report["env_error"] = f"真源/生成器不可读，无法产 patch: {exc}"
        report["verdict"] = "env_fail"
        return _finish(report, EXIT_ENV)

    bases: dict[str, str] = {}
    current: dict[str, str] = {}
    patched: dict[str, str] = {}
    noop_files: list[str] = []
    for rel in sorted(patched_all):
        text, _nl = read_text(root / rel)
        bases[rel] = content_sha256(text)
        current[rel] = text
        if patched_all[rel] == text:
            noop_files.append(rel)  # 已是目标态：不入写集，生产文件零字节改动
        else:
            patched[rel] = patched_all[rel]
    report["patches"] = [
        {"task_id": p.task_id, "kind": p.kind, "rel_path": p.rel_path, "line_no": p.line_no,
         "old_value": p.old_value, "new_value": p.new_value, "noop": p.noop,
         "note": p.note, "rationale_zh": p.rationale_zh,
         "diff_lines": len(unified_diff(p.rel_path, p.old_line, p.new_line).splitlines())}
        for p in patches
    ]
    report["files_touched"] = sorted(patched)
    report["noop_files"] = noop_files
    report["diff_preview"] = {rel: unified_diff(rel, current[rel], patched[rel]) for rel in sorted(patched)}
    report["diff_stats"] = {rel: _diff_stats(v) for rel, v in report["diff_preview"].items()}

    # ── ③ 受闸验（沙箱）：改后沙箱 vs 未改沙箱，两边同口径再生+同 focus 归因
    touched = {str(t) for t in items}
    try:
        build_sandbox(root, sandbox, patched, base_extra_rels)
        sb_reg = regen_sandbox(sandbox, skip_schtasks=tri_skip)
        sb_data = yaml.safe_load(sb_reg.read_text(encoding="utf-8")) or {}
        sb_ents = list(sb_data.get("entities") or [])
        findings = gate_findings(gate, sb_ents, sandbox, now, focus=touched)
    except PlanError as exc:
        report["refusals"].append({"stage": "sandbox_verify", "reason": str(exc)})
        report["verdict"] = "refused"
        return _finish(report, EXIT_REFUSED)
    except EnvError as exc:
        report["env_error"] = str(exc)
        report["verdict"] = "env_fail"
        return _finish(report, EXIT_ENV)

    # 基线：同沙箱机制、真源不打补丁再生一次。为什么不用现盘注册表当基线——现盘表按构造
    # 滞后于真源（谁改了真源没再生，账就记在别人头上），拿它差分等于把两件事混成一件。
    base_sandbox = sandbox.parent / (sandbox.name + "_baseline")
    try:
        build_sandbox(root, base_sandbox, {}, base_extra_rels)
        base_reg = regen_sandbox(base_sandbox, skip_schtasks=tri_skip)
        base_ents = list((yaml.safe_load(base_reg.read_text(encoding="utf-8")) or {}).get("entities") or [])
        baseline = gate_findings(gate, base_ents, base_sandbox, now, focus=touched)
    except PlanError as exc:
        report["refusals"].append({"stage": "baseline_verify", "reason": str(exc)})
        report["verdict"] = "refused"
        return _finish(report, EXIT_REFUSED)
    except EnvError as exc:
        report["env_error"] = f"基线沙箱失败（无从判定「本次新账」，宁拦不漏）: {exc}"
        report["verdict"] = "env_fail"
        return _finish(report, EXIT_ENV)
    finally:
        if not keep_sandbox:
            shutil.rmtree(base_sandbox, ignore_errors=True)

    pre_keys = block_keys(block_records(baseline))
    post_keys = block_keys(block_records(findings))
    new_blocks = [f"{b['arm']}: {b['rendered']}" for b in block_records(findings)
                  if (b["arm"], b["code"], tuple(b["ids"])) not in pre_keys]
    # 反向账同样重要：P3 全局重排要的判据是"这一挪有没有清掉一条既存冲突"（如周六 14:00
    # c4_exam/f06_grid 同刻开工），只报新账会把减账看成白干。
    blocks_resolved = sorted(f"{b['arm']}: {b['rendered']}" for b in block_records(baseline)
                             if (b["arm"], b["code"], tuple(b["ids"])) not in post_keys)
    problems = materialization_problems(sb_ents, located, items, patches)
    report["gate"] = {
        "focus_tasks": sorted(touched),
        "findings_after_patch": findings,
        "baseline_entities": len(base_ents),
        "pre_existing_blocks": sorted(f"{b['arm']}: {b['rendered']}" for b in block_records(baseline)),
        "new_blocks": sorted(new_blocks),
        "blocks_resolved": sorted(blocks_resolved),
        "materialization_problems": problems,
        "c8_available": findings["c8_available"],
        **({"c8_note": findings["c8_note"]} if "c8_note" in findings else {}),
        **({"arm_notes": findings["arm_notes"]} if "arm_notes" in findings else {}),
    }
    report["sandbox_registry"] = {"entities": len(sb_ents), "total_entities_field": sb_data.get("total_entities"),
                                  "baseline_entities": len(base_ents),
                                  "entity_delta_vs_baseline": len(sb_ents) - len(base_ents)}

    # ── ⑤ 三角对账（dry-run 侧=沙箱"改后预期"：真源重抽也须走沙箱副本，否则拿旧生产真源
    #       对改后表，报出来的全是假漂移）
    try:
        gen_sb = load_sibling(GENERATOR_REL, "p2b_gen_sandbox_root", sandbox)
    except EnvError:
        gen_sb = gen
    report["triangle"] = triangle_report(
        gen_sb, sb_reg, sandbox,
        [p.task_id for p in patches if not p.noop] or sorted(items),
        skip_schtasks=tri_skip,
    )
    report["triangle"]["os_reconcile_note"] = (
        "schtasks 角仍反映**当前系统在册态**：改 ps1 触发器只改文本真源，须以管理员重跑对应 "
        "register_*.ps1 才落到 Windows 计划任务（本工具不代跑，越权且需管理员令牌）；"
        "data_slot_* 是进程内 APScheduler 作业，本就无 OS 任务角。"
    )

    if new_blocks or problems:
        report["verdict"] = "blocked"
        report["block_reasons"] = new_blocks + problems
        report["apply_note"] = "受闸验未过——零生产写（沙箱之外未动任何文件）"
        return _finish(report, EXIT_REFUSED)
    report["verdict"] = "pass"

    # ── ④ 落地（仅 --apply）
    if not apply:
        report["apply_note"] = "dry-run：patch 与报告已产出，生产文件零改动"
        return _finish(report, EXIT_OK)

    ad = Path(root) / ".runtime/sessions" / session / "archive" / f"plan_{_utc_ts()}"
    plan_meta = {
        "plan_id": report["plan_id"], "session": session, "ts_utc": report["ts_utc"],
        "plan_sha256": sha256_bytes(Path(plan_path).read_bytes()),
        "mode": "apply", "report_sha256_pending": True, "files": [],
    }
    written: list[dict] = []
    view_existed_before = (Path(root) / VIEW_REL).exists()
    try:
        archive_originals(ad, root, sorted(set(patched) | set(ALWAYS_ARCHIVED)), plan_meta)
        (ad / "plan.yaml").write_text(Path(plan_path).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        for rel in sorted(patched):
            dp = ad / "diff" / (rel.replace("/", "__") + ".diff")
            dp.parent.mkdir(parents=True, exist_ok=True)
            dp.write_text(report["diff_preview"][rel], encoding="utf-8", newline="\n")
        written = write_production(root, patched, bases)
        regen = run_child(root, GENERATOR_REL, extra=["--skip-schtasks"] if tri_skip else [])
        view = _render_view(root)
        # 落地后复验（现盘真源→现盘表→视图→闸）：任一子进程失败=复验失败，绝不"写了再说"
        post_new: list[str] = []
        if regen["rc"] == 0:
            fresh_disk = _disk_entities(root)
            post = gate_findings(gate, fresh_disk, root, now, focus=touched)
            post_new = sorted(f"{b['arm']}: {b['rendered']}" for b in block_records(post)
                            if (b["arm"], b["code"], tuple(b["ids"])) not in pre_keys)
            problems2 = materialization_problems(fresh_disk, located, items, patches)
            # 再生只保证"表跟真源一致"，还得反过来确认一致的不是别处的旧真源
            if triangle_report(gen, root / REGISTRY_REL, root, sorted(items),
                               skip_schtasks=True)["summary"]["truth_drifted"]:
                problems2.append("post_apply_drift: 落地后表↔真源仍有漂移条目")
        else:
            fresh_disk = None
            problems2 = [f"regen_failed: rc={regen['rc']} {regen['stderr'][:200]}"]
        if view["rc"] != 0:
            detail = f"rc={view['rc']} {(view['stderr'] or view['stdout'])[:200]}"
            if view_existed_before:
                problems2.append(f"view_render_failed: {detail}")
            else:
                report["view_note"] = (
                    f"视图产物事前不存在且本次渲染未成功（{detail}）——不构成「表↔视图不一致」，"
                    "但生产落地前应确保视图链可用"
                )
        report["children"] = {"regen": regen, "view": view}
        report["written"] = written
        report["post_apply"] = {"new_blocks": post_new, "materialization_problems": problems2,
                                "entities_after_regen": None if fresh_disk is None else len(fresh_disk)}
        report["triangle_after_apply"] = triangle_report(
            gen, root / REGISTRY_REL, root, sorted(items), skip_schtasks=tri_skip)
        if post_new or problems2:
            rb = restore_archive(root, ad)
            reroll = run_child(root, GENERATOR_REL, extra=["--skip-schtasks"] if tri_skip else [])
            report["verdict"] = "rolled_back"
            report["block_reasons"] = post_new + problems2
            report["rollback"] = rb
            report["children"]["regen_after_rollback"] = reroll
            report["apply_note"] = "落地后复验失败——已按存档逐字节还原（含表与视图）"
            return _finish(report, EXIT_REFUSED, drop_sandbox=True)
        report["apply_note"] = "已落地：真源+表+视图三处一致，复验 0 新增 block"
    except EnvError as exc:
        report["env_error"] = str(exc)
        report["written_before_failure"] = written
        if not written:
            report["verdict"] = "env_fail_before_write"
            report["apply_note"] = "环境失败发生在写盘之前——生产文件零改动，无需回滚"
            return _finish(report, EXIT_ENV, drop_sandbox=True)
        try:
            report["rollback"] = restore_archive(root, ad)
            report["children"] = {"regen_after_rollback": run_child(
                root, GENERATOR_REL, extra=["--skip-schtasks"] if skip_schtasks else [])}
            report["verdict"] = "rolled_back"
        except Exception as exc2:  # noqa: BLE001 — 回滚失败必须比原错误更显眼
            report["verdict"] = "apply_failed_no_rollback"
            report["rollback_error"] = str(exc2)[:200]
        return _finish(report, EXIT_ENV, drop_sandbox=True)
    report["archive_dir"] = _norm(ad)
    return _finish(report, EXIT_OK, drop_sandbox=True)


def _render_view(root: Path) -> dict:
    """子进程重渲周历视图（表→视图；视图缺席/脚本不可用时如实记失败，不静默）。"""
    view_script = Path(root) / VIEW_GENERATOR_REL
    if not view_script.exists():
        return {"script": _norm(view_script), "rc": -1, "stdout": "", "stderr": "view generator absent"}
    cmd = [sys.executable, str(view_script),
           "--registry", str(Path(root) / REGISTRY_REL),
           "--output", str(Path(root) / VIEW_REL)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900, cwd=str(root))
    except Exception as exc:  # noqa: BLE001
        return {"script": _norm(view_script), "rc": -1, "stdout": "", "stderr": str(exc)[:300]}
    return {"script": _norm(view_script), "rc": r.returncode, "stdout": (r.stdout or "")[-600:],
            "stderr": (r.stderr or "")[-600:]}


def _disk_entities(root: Path) -> list[dict]:
    """_disk_entities implementation."""
    p = Path(root) / REGISTRY_REL
    if not p.exists():
        raise EnvError(f"注册表不存在: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return list(data.get("entities") or [])


def _slot_aps_cron(spec: TimeSpec) -> str:
    """TimeSpec（标准 cron 口径）→ 写回 schedule.yaml 的 APScheduler 口径（0=周一）。

    只平移 dow（末段），其余段原样落回真源；与生成器 ``_aps_dow_to_standard`` 成对，
    闭合与否由 build_patches 的"改后重抽==方案预期"复验与沙箱再生共同证。
    """
    if spec.mode == "times":
        raise PlanError("new_times 只适用于 ps1 -Times 清单（schedule.yaml 槽位单一 cron）")
    if spec.mode == "cron" and spec.cron:
        b = list(cron_bands(spec.cron))
        b[-1] = standard_dow_to_aps(b[-1])
        return " ".join(b)
    return " ".join([str(spec.minute), str(spec.hour), spec.dom, spec.month, standard_dow_to_aps(spec.dow)])


def _diff_stats(diff_text: str) -> dict:
    """_diff_stats implementation."""
    add = sum(1 for ln in diff_text.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    rem = sum(1 for ln in diff_text.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    return {"added_lines": add, "removed_lines": rem, "hunks": sum(1 for ln in diff_text.splitlines()
                                                                   if ln.startswith("@@"))}


def render_map(located: dict[str, Located]) -> str:
    """task→真源命中全表（人读；--map 出口）。"""
    lines = [f"{'task_id':40s} {'kind':15s} {'window_expr':30s} {'truth_source'}"]
    for tid in sorted(located):
        loc = located[tid]
        lines.append(f"{tid:40s} {loc.kind:15s} {str(loc.window_expr)[:30]:30s} {loc.truth_rel}"
                     + ("" if loc.patchable_window else "   [改窗不可: " + loc.why_not.split("；")[0][:40] + "]"))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_argparser() -> argparse.ArgumentParser:
    """_build_argparser implementation."""
    p = argparse.ArgumentParser(
        prog="apply_resource_plan.py",
        description="排班方案→时间真源受闸写回一竿子（MOD-RESCHED-APPLY，v2 方案 P2-b；R-A：产 patch 不产表）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python scripts/governance/apply_resource_plan.py --plan <path>            # 默认 dry-run\n"
            "  python scripts/governance/apply_resource_plan.py --plan <path> --report-json --map\n"
            "  python scripts/governance/apply_resource_plan.py --plan <path> --apply --session <sid>\n"
            "  python scripts/governance/apply_resource_plan.py --rollback <archive_dir>\n"
        ),
    )
    p.add_argument("--plan", type=str, default=None, help=f"排班方案 YAML（缺省 .runtime/sessions/<sid>/staging/{PLAN_DEFAULT_NAME}）")
    p.add_argument("--session", type=str, default=DEFAULT_SID, help=f"会话号（存档目录锚点，缺省 {DEFAULT_SID}）")
    p.add_argument("--dry-run", action="store_true", help="只产 patch 与报告（默认即 dry-run，旗标为显式表达）")
    p.add_argument("--apply", action="store_true", help="把 patch 落生产真源 + 调再生 + 重渲视图 + 复验（复验失败自动回滚）")
    p.add_argument("--rollback", type=str, default=None, metavar="ARCHIVE_DIR", help="按存档 manifest 逐字节还原（含表与视图）")
    p.add_argument("--report-json", nargs="?", const="-", default=None, metavar="PATH",
                   help="机器可读报告：不给值=打印 stdout，给路径=写该文件；--apply 时另存一份进存档目录 report.json")
    p.add_argument("--map", action="store_true", dest="show_map", help="打印 task→真源命中全表（人读）")
    p.add_argument("--root", type=str, default=str(REPO_ROOT), help="仓根（测试/沙箱注入用，缺省=真实仓根）")
    p.add_argument("--sandbox", type=str, default=None, help="沙箱目录（缺省 <root>/.runtime/tmp/apply_resource_plan_sandbox）")
    p.add_argument("--keep-sandbox", action="store_true", help="保留沙箱现场（排障）")
    p.add_argument("--skip-schtasks", action="store_true", help="跳过 C-15 schtasks 实测探针（离线/非 Windows/测试）")
    p.add_argument("--list-tasks", action="store_true", help="仅打印 task→真源命中表后退出")
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = _build_argparser().parse_args(argv)
    root = Path(args.root).resolve()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    try:
        gen = load_sibling(GENERATOR_REL, "p2b_gen_cli", root)
    except EnvError as exc:
        print(f"ENV-FAIL: {exc}")
        return EXIT_ENV
    if args.rollback:
        try:
            res = restore_archive(root, Path(args.rollback))
        except (EnvError, OSError, json.JSONDecodeError) as exc:
            print(f"ROLLBACK-FAIL: {exc}")
            return EXIT_ENV
        print(json.dumps(res, ensure_ascii=False, indent=1))
        print("ROLLBACK-OK: 按存档逐字节还原完成（表/视图如需刷新，再跑一次生成器与视图生成器）")
        return EXIT_OK
    if bool(args.apply) and args.dry_run:
        print("USAGE: --apply 与 --dry-run 互斥")
        return EXIT_USAGE
    plan = Path(args.plan) if args.plan else default_plan_path(root, args.session)
    try:
        located = locate_all(gen, root)
    except EnvError as exc:
        print(f"ENV-FAIL: {exc}")
        return EXIT_ENV
    if args.list_tasks:
        print(render_map(located))
        return EXIT_OK
    if args.show_map:
        print(render_map(located))
    try:
        report, rc = run_plan(
            root=root, plan_path=plan, session=args.session, apply=bool(args.apply),
            sandbox_dir=Path(args.sandbox) if args.sandbox else None,
            skip_schtasks=bool(args.skip_schtasks), keep_sandbox=bool(args.keep_sandbox),
        )
    except (PlanError, EnvError) as exc:  # 编排层漏网=编排 bug，仍按契约出口码落，不冒 traceback
        print(f"{'REFUSE' if isinstance(exc, PlanError) else 'ENV-FAIL'}: {exc}")
        return EXIT_REFUSED if isinstance(exc, PlanError) else EXIT_ENV
    json_stdout = args.report_json == "-"
    out = json.dumps(report, ensure_ascii=False, indent=1)
    if args.report_json and not json_stdout:
        p = Path(args.report_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out + "\n", encoding="utf-8", newline="\n")
        print(f"REPORT: {p}")
    if json_stdout:
        print(out)
    else:
        _print_human(report, located)
    return rc


def _print_human(report: dict, located: dict[str, Located]) -> None:
    """_print_human implementation."""
    print(f"PLAN {report.get('plan_id')} mode={report.get('mode')} verdict={report.get('verdict', '-')}")
    for it in report.get("items", []):
        loc = it["located"]
        if loc is None:
            print(f"  - {it['task_id']}: 未命中")
            continue
        print(f"  - {it['task_id']} → {loc['kind']} @ {loc['truth_source']}"
              + (f"（{loc['ps1_task_name']}）" if loc["kind"] == KIND_PS1 else "")
              + (f" 槽位={loc['slot']}" if loc["kind"] == KIND_SLOT else ""))
    for p in report.get("patches", []):
        print(f"  patch {p['kind']} {p['rel_path']}:{p['line_no']} {p['old_value']!r} → {p['new_value']!r}"
              + ("（已是目标态，noop）" if p["noop"] else ""))
    for rel, st in (report.get("diff_stats") or {}).items():
        print(f"  diff {rel}: +{st['added_lines']} -{st['removed_lines']} hunks={st['hunks']}")
    g = report.get("gate") or {}
    if g:
        print(f"  闸：新增 block={len(g.get('new_blocks', []))} 基线既存 block={len(g.get('pre_existing_blocks', []))} "
              f"本方案消解={len(g.get('blocks_resolved', []))} "
              f"C-8 就绪={g.get('c8_available')} 物化问题={len(g.get('materialization_problems', []))}")
        for b in (g.get("blocks_resolved") or [])[:3]:
            print(f"    RESOLVED {b[:200]}")
        for b in (g.get("new_blocks") or [])[:6]:
            print(f"    BLOCK {b[:200]}")
        for b in (g.get("materialization_problems") or [])[:6]:
            print(f"    MATERIALIZE {b[:200]}")
    t = report.get("triangle") or {}
    for r in t.get("rows", []):
        print(f"  三角 {r['task_id']}: 表={r['table_window_expr']!r} 真源={r['truth_window_expr']!r} "
              f"{r['table_vs_truth']} schtasks={r['schtasks_status']}")
    for s in report.get("refusals", []):
        print(f"  REFUSE[{s['stage']}]: {s['reason']}")
    if report.get("env_error"):
        print(f"  ENV-FAIL: {report['env_error']}")
    if report.get("report_sha256"):
        print(f"  report_sha256={report['report_sha256'][:16]}")
    if report.get("archive_dir"):
        print(f"  archive={report['archive_dir']}")


if __name__ == "__main__":
    raise SystemExit(main())
