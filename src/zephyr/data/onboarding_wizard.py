# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.onboarding_wizard
# [DOMAIN] D_DATA
# [DEPENDENCIES] 候选册 docs/_working/altdata_line/10_data_source_candidates.yaml(读写尾插);
#   DS 册 architecture_model/data/data_sources_registry.yaml(读写); tasks/schedule=src/zephyr/data/config/;
#   品类册 docs/03_modules/_cross_layer/database/business_data_categories.yaml(读写尾插);
#   schemas/categories/+implementations/(只读探测); table_registry.validate_tasks_yaml(复用);
#   zephyr.shared.io.file_utils(safe_write_text); zephyr.shared.utils.time_utils(now_utc); stdlib
# [CONSUMERS] 数据上架会话（人工驱动 CLI：python -m zephyr.data.onboarding_wizard start|resume|confirm|status）;
#   无调度器/计划任务消费（宪法 §9.3：本件纯人工步进，禁止自动轮询注册）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯编排壳：十环零散件全复用既有真源与脚本（apply_*_ddl/validate_tasks_yaml/两册一表），不新造接数逻辑;
#   人工环只产出待办与指令绝不代做（报批/三闸/首跑/验收三查=人）；机器环只做文件登记（CAS 尾插保注释）与脚本调用，本件零业务库连接;
#   O2 硬校验：tasks 登记时 fallback_sources 键必在（显式置空带 fallback_note）——DATA-TASK-COMPLETENESS 退役后登记时替代闸;
#   O3 硬校验：disabled 任务必带 disabled_reason；爬虫源默认否决（SOP §2，向导内不放行）;
#   O4 毕业联动：candidates 翻转 promoted+DS 册 DS-* 条目两册一次先后落盘；状态断点续跑 state.json+checklist 落 data/runtime/onboarding/;
#   dry-run 全链打印零落盘；不注册计划任务无 cron/Timer/sleep-loop；真实接入动作（注册/首跑/连库）不属本件（F02 任务书禁区）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OnboardingWizardError：请求非法（source_id/cand_id 空、crawler、槽位违规）或册文件损坏（fail-closed 不静默）;
#   机器环执行失败=该环 failed 暂停不抛（断点续跑语义）；CLI 参数错=argparse 退出码 2
# [TESTS] tests/data/test_onboarding_wizard.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=experimental | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: 纯编排壳不二造真源——_load_yaml_doc 仅为本件读册的私有工具函数（非通用 yaml 加载器），
# 全部能力面（DDL 部署/任务校验/两册登记）均复用既有 canonical 件（scripts/ch/apply_*_ddl.py、
# zephyr.data.table_registry.validate_tasks_yaml、候选册/DS 册/品类册本体），零新接数逻辑、零第二真源；
# capability 反查审计 .runtime/lookup_audit/st-c9-f02 空命中在案
"""onboarding_wizard — F02 数据源上架十环编排器（SOP 工段③断链的单入口向导，纯编排壳）.

施工处方：docs/_working/fullconnect_campaign/a_data_foundation/02_f02_source_onboarding_lifecycle.md
（缺口 O1：候选→毕业→DS 册→provider→DDL→品类→tasks.yaml→槽位→首跑→哨兵腿十环全靠会话人肉串接，
st-emomine 批 a9818b2ef2 为实证）；流程真源=data_ops_sop/data_source_onboarding_sop.md v1.1.0。

定位：把 SOP 十环编成显式状态机。每环=一步：机器环（有既有脚本/册登记可执行）直接执行或落盘；
人工环（报批/三闸/首跑/验收三查）产出下一步指令与所需人工件清单并暂停，人工完成后
confirm 回执或人工件落盘后 resume 自动检出。状态逐环落 state.json，断点续跑；
checklist.md 逐环追加留痕。dry-run 全链打印不落盘。

# [ALGO_FLOW]
输入: OnboardingRequest(source_id/cand_id/table/provider/task_id/schedule_slot/candidate_entry/
      fallback_sources|fallback_note) + 五册文件（候选/DS/tasks/schedule/品类）+ schemas/implementations 探测
前置检查: source_id 非空；acquire_mode≠crawler（SOP §2 默认否决）；槽位 ∈ schedule.yaml；
      机器环前置环已闭环（毕业环未过→DS 册环拒绝执行）
执行: 十环线性状态机，逐环 check→(已达标?done):(kind? machine→executor / manual→instruction+暂停)，
      逐环 safe_write_text 持久化 state.json + 追加 checklist.md；resume 从首个未闭环环继续；
      confirm 只对 manual_wait 的人工环生效
输出: WizardReport(逐环 status/detail/instruction + stopped_at 下一动作)；侧效应=两册一表登记件+
      state/checklist 落盘（dry-run 时全部免掉，只打印）
降级: 册文件缺文档/键→OnboardingWizardError（不静默）；DDL 子进程失败→该环 failed；
      validate_tasks_yaml 警告=记录不阻断（WARN 语义与 table_registry 一致）
不变量: 人工环绝不代做；机器环绝不连业务库；十环顺序固定不自创环；两册联动（O4）同批先后落；
      O2/O3 在登记生成时硬校验，不带 fallback/disabled_reason 的条目永不落 tasks.yaml
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

import yaml

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "ACCEPTANCE_RING",
    "CANDIDATE_RING",
    "DS_REGISTRY_RING",
    "OnboardingRequest",
    "OnboardingWizard",
    "OnboardingWizardError",
    "RingRecord",
    "RingStatus",
    "WizardDeps",
    "WizardReport",
    "main",
]

# ========== 常量（真源路径，禁凭记忆散落） ==========

CANDIDATES_REGISTRY = Path("docs/_working/altdata_line/10_data_source_candidates.yaml")
DS_REGISTRY = Path("architecture_model/data/data_sources_registry.yaml")
TASKS_CONFIG = Path("src/zephyr/data/config/tasks.yaml")
SCHEDULE_CONFIG = Path("src/zephyr/data/config/schedule.yaml")
CATEGORY_REGISTRY = Path("docs/03_modules/_cross_layer/database/business_data_categories.yaml")
IMPLEMENTATIONS_DIR = Path("src/zephyr/data/implementations")
SCHEMAS_DIR = Path("schemas/categories")
DEFAULT_STATE_DIR = Path("data/runtime/onboarding")

SOP_REF = "docs/01_policies_and_standards/sop/data_ops_sop/data_source_onboarding_sop.md"
_BLUEPRINT_ANCHOR = "MOD-L00-001  # onboarding_wizard 编排登记"

_ALLOWED_ACQUIRE_MODES = ("api_free", "api_register", "download", "manual", "paid_api")
_ALLOWED_CAND_STATUS = ("candidate", "approved", "registering", "integrated", "promoted", "rejected")
_GRADUATED_STATUSES = ("integrated", "promoted")
_SCORE_KEYS = ("availability", "signal", "fit", "maintenance")

RING_CANDIDATE = "candidate"
RING_GRADUATION = "graduation"
RING_DS_REGISTRY = "ds_registry"
RING_PROVIDER = "provider"
RING_DDL = "ddl"
RING_CATEGORY = "category"
RING_TASK = "task_register"
RING_SLOT = "schedule_slot"
RING_FIRST_RUN = "first_run"
RING_ACCEPTANCE = "acceptance"

CANDIDATE_RING = RING_CANDIDATE
DS_REGISTRY_RING = RING_DS_REGISTRY
ACCEPTANCE_RING = RING_ACCEPTANCE

# ========== 错误与数据契约 ==========


class OnboardingWizardError(ValueError):
    """向导请求非法或册文件损坏（fail-closed，不静默；定位信息进 details 不进消息文本）。"""

    def __init__(self, msg: str, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


class RingStatus:
    """环状态字面量集合（JSON 友好，不用 Enum 以保 state.json 可读）。"""

    PENDING = "pending"
    DONE = "done"
    MANUAL_WAIT = "manual_wait"
    FAILED = "failed"


@dataclass
class OnboardingRequest:
    """一次上架编排的输入面。人工件（报批结论/三闸/首跑/验收）不在此代填。"""

    source_id: str  # 目标 DS-* 编号（如 DS-CAND-011 毕业后的 DS-HYPERLIQUID）
    cand_id: str = ""  # 候选编号（如 DS-CAND-011；空=免候选环，直接从 DS 册环起）
    table: str = ""  # 全限定表名 db.table（如 c1_crypto.perp_snapshot_daily）
    schema_domain: str = ""  # schemas/categories/ 子目录（market/fundamental/crypto/...）
    provider: str = ""  # runtime_id（implementations/<provider>_provider.py）
    task_id: str = ""
    schedule_slot: str = ""
    date_col: str = ""  # PIT 锚列（SOP §4）
    capability: str = ""
    description: str = ""
    fallback_sources: list[str] = field(default_factory=list)  # O2：备源清单
    fallback_note: str = ""  # O2：显式置空时的原因（与 fallback_sources 二选一必有一）
    disabled: bool = False  # 登记 disabled 任务时必须配 disabled_reason（O3）
    disabled_reason: str = ""
    candidate_entry: dict[str, Any] | None = None  # R1 机器登记载荷（None=人工挖矿待办）
    consumer: str = ""  # §9 默认消费端注记（验收环指令引用）
    ddl_command: list[str] = field(default_factory=list)  # 缺省派生 apply_*_ddl.py

    def validate(self) -> None:
        if not self.source_id or not self.source_id.startswith("DS-"):
            raise OnboardingWizardError(f"source_id 必须为 DS-* 编号，得到: {self.source_id!r}")
        if self.candidate_entry is not None:
            mode = str(self.candidate_entry.get("acquire_mode", ""))
            if mode == "crawler":
                raise OnboardingWizardError("acquire_mode=crawler 默认否决（SOP §2），需专项裁定走 Owner 通道")
            if mode not in _ALLOWED_ACQUIRE_MODES:
                raise OnboardingWizardError(f"acquire_mode 非法: {mode!r}，合法值 {_ALLOWED_ACQUIRE_MODES}")
        if self.disabled and not self.disabled_reason:
            raise OnboardingWizardError("O3 硬校验：disabled 任务必须带 disabled_reason（SOP §7）")
        if self.candidate_entry is not None and self.cand_id:
            entry_id = str(self.candidate_entry.get("cand_id", ""))
            if entry_id and entry_id != self.cand_id:
                raise OnboardingWizardError(f"cand_id 不一致: request={self.cand_id} entry={entry_id}")

    def derived_ddl_command(self) -> list[str]:
        if self.ddl_command:
            return list(self.ddl_command)
        if not self.table:
            return []
        table_name = self.table.split(".", 1)[1]
        return [sys.executable, f"scripts/ch/apply_{table_name}_ddl.py"]


@dataclass
class RingRecord:
    """单环状态（state.json rings 段的值对象）。"""

    ring_id: str
    status: str = RingStatus.PENDING
    detail: str = ""
    instruction: str = ""
    confirmed_note: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WizardReport:
    """一次 start/resume/confirm 运行的输出面。"""

    source_id: str
    dry_run: bool = False
    stopped_at: str = ""
    next_action: str = ""
    rings: list[RingRecord] = field(default_factory=list)

    def render(self) -> str:
        lines = [f"[onboarding] {self.source_id} dry_run={self.dry_run}"]
        for rec in self.rings:
            mark = {RingStatus.DONE: "x", RingStatus.MANUAL_WAIT: "!", RingStatus.FAILED: "✗"}.get(rec.status, " ")
            head = f"  [{mark}] {rec.ring_id:<14} {rec.status:<11} {rec.detail}"
            lines.append(head.rstrip())
            if rec.status == RingStatus.MANUAL_WAIT and rec.instruction:
                lines.append(f"        待办: {rec.instruction}")
        if self.stopped_at:
            lines.append(f"  停于: {self.stopped_at} — {self.next_action}")
        return "\n".join(lines)


@dataclass
class WizardDeps:
    """可注入依赖（测试全 mock 的接缝；生产用默认值）。"""

    repo_root: Path
    state_dir: Path = DEFAULT_STATE_DIR
    run_command: Callable[[list[str]], tuple[int, str]] | None = None
    session: str = "onboarding-wizard"
    confirm_mode: bool = False  # 内部：confirm 通道放行标记

    def resolve(self, rel: Path) -> Path:
        return self.repo_root / rel

    def default_run_command(self, cmd: list[str]) -> tuple[int, str]:
        proc = run_subprocess_hidden(  # noqa: S603 — 命令白名单来自 request.ddl_command/派生，人工显式发起
            cmd, cwd=str(self.repo_root), capture_output=True, text=True, timeout=600, check=False
        )
        return proc.returncode, (proc.stdout + proc.stderr)[-2000:]


# ========== YAML 读写（保注释的文本外科手术） ==========


def _load_yaml_doc(path: Path, key: str) -> dict[str, Any]:
    """加载含 frontmatter 的多文档 YAML，取含 key 的映射文档（顶层 list 文档包装为 {"__list__": [...]}）。"""
    if not path.exists():
        raise OnboardingWizardError("真源文件不存在（路径见 details）", details={"path": str(path)})
    for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")):
        if isinstance(doc, dict) and key in doc:
            return doc
        if isinstance(doc, list) and key == "__list__":
            return {"__list__": doc}
    raise OnboardingWizardError(
        "真源册中未找到含期望键的文档段（册文件损坏？路径与键见 details）",
        details={"path": str(path), "key": key},
    )


def _dump_doc(frontmatter: str | None, doc: dict[str, Any]) -> str:
    body = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100)
    return (frontmatter + body) if frontmatter else body


def _find_list_entry(entries: list[dict[str, Any]] | None, id_key: str, id_val: str) -> dict[str, Any] | None:
    for entry in entries or []:
        if isinstance(entry, dict) and str(entry.get(id_key, "")) == id_val:
            return entry
    return None


def _append_text_block(path: Path, block: str) -> None:
    """册表尾插（列表节均为末键，尾插不破坏既有注释；CAS 走 safe_write_text）。"""
    current = path.read_text(encoding="utf-8")
    if not current.endswith("\n"):
        current += "\n"
    safe_write_text(path, current + block, repo_root=None)


def _flip_candidate_status(path: Path, cand_id: str, new_status: str) -> bool:
    """在候选册内精准翻转指定 cand_id 的 status 行（块内正则，不动他条目）。"""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(cand_id:\s*" + re.escape(cand_id) + r"\n(?:    .*\n)*?    status:\s*)(\S+)", re.MULTILINE)
    matched = pattern.search(text)
    if not matched:
        return False
    updated = text[: matched.start(2)] + new_status + text[matched.end(2) :]
    safe_write_text(path, updated, repo_root=None)
    return True


def _yaml_block(entry: dict[str, Any], indent: str = "  ") -> str:
    """条目 dict → YAML 块文本（首键带 - 前缀，后续键对齐）。"""
    dumped = yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
    lines = dumped.rstrip("\n").split("\n")
    out = [f"{indent}- " + lines[0]]
    for line in lines[1:]:
        out.append((indent + "  " + line) if line.strip() else "")
    return "\n".join(out).rstrip() + "\n"


# ========== 十环定义（O1 处方顺序，禁自创环） ==========


class OnboardingStateStore:
    """状态持久化面：state.json 断点续跑载体 + checklist.md 逐环留痕（safe_write_text CAS）。"""

    def __init__(self, deps: WizardDeps) -> None:
        self.deps = deps

    def source_dir(self, source_id: str) -> Path:
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", source_id)
        return self.deps.resolve(self.deps.state_dir) / safe_id

    def state_path(self, source_id: str) -> Path:
        return self.source_dir(source_id) / "state.json"

    def checklist_path(self, source_id: str) -> Path:
        return self.source_dir(source_id) / "checklist.md"

    def load(self, source_id: str, wizard: OnboardingWizard) -> dict[str, Any] | None:
        path = self.state_path(source_id)
        if not path.exists():
            return None
        state = json.loads(path.read_text(encoding="utf-8"))
        req = OnboardingRequest(**state["request"])
        wizard.request = req
        return state

    def persist(self, state: dict[str, Any]) -> None:
        state["updated_at"] = now_utc().isoformat()
        path = self.state_path(state["source_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        result = safe_write_text(path, json.dumps(state, ensure_ascii=False, indent=2), repo_root=None)
        if not result.written:
            raise OnboardingWizardError("state.json 写入未落地（路径见 details）", details={"path": result.path})

    def append_checklist(self, source_id: str, rec: RingRecord) -> None:
        path = self.checklist_path(source_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else f"# 上架 checklist — {source_id}\n\n"
        line = f"- [{now_utc().isoformat()}] {rec.ring_id}: {rec.status} — {rec.detail}\n"
        if rec.instruction:
            line += f"  待办: {rec.instruction}\n"
        safe_write_text(path, existing + line, repo_root=None)


class RegistryProbe:
    """真源只读探测面：五册三目录的存在性/登记态查询（本件零业务库连接，全部文件面）。"""

    def __init__(self, deps: WizardDeps) -> None:
        self.deps = deps

    def category_hit(self, req: OnboardingRequest) -> dict[str, Any] | None:
        if not req.table:
            return None
        doc = _load_yaml_doc(self.deps.resolve(CATEGORY_REGISTRY), "__list__")
        entries = doc["__list__"]
        db, table = req.table.split(".", 1)
        return next((e for e in entries if e.get("database") == db and e.get("table") == table), None)

    def slot_names(self) -> dict[str, Any]:
        doc = _load_yaml_doc(self.deps.resolve(SCHEDULE_CONFIG), "schedules")
        return doc["schedules"]

    def runner(self) -> Callable[[list[str]], tuple[int, str]]:
        return self.deps.run_command or self.deps.default_run_command

    def cand_entry(self, cand_id: str) -> dict[str, Any] | None:
        doc = _load_yaml_doc(self.deps.resolve(CANDIDATES_REGISTRY), "candidates")
        return _find_list_entry(doc["candidates"], "cand_id", cand_id)

    def ds_entry(self, source_id: str) -> dict[str, Any] | None:
        doc = _load_yaml_doc(self.deps.resolve(DS_REGISTRY), "data_sources")
        return _find_list_entry(doc["data_sources"], "id", source_id)

    def task_entry(self, task_id: str) -> dict[str, Any] | None:
        doc = _load_yaml_doc(self.deps.resolve(TASKS_CONFIG), "tasks")
        return _find_list_entry(doc["tasks"], "task_id", task_id)

    def provider_path(self, req: OnboardingRequest) -> Path:
        return self.deps.resolve(IMPLEMENTATIONS_DIR / f"{req.provider}_provider.py")

    def schema_path(self, req: OnboardingRequest) -> Path:
        if not req.table or not req.schema_domain:
            return Path()
        table_name = req.table.split(".", 1)[1]
        return self.deps.resolve(SCHEMAS_DIR / req.schema_domain / f"{table_name}.py")

    def task_o2o3_errors(self, entry: dict[str, Any]) -> list[str]:
        """O2/O3 硬校验（登记时拦截，非 commit gate）。"""
        errors: list[str] = []
        if "fallback_sources" not in entry:
            errors.append("O2: fallback_sources 键缺失（显式置空也须落键并注明显式置空原因）")
        if entry.get("disabled") and not entry.get("disabled_reason"):
            errors.append("O3: disabled 任务缺 disabled_reason（SOP §7）")
        return errors


class RingOps:
    """十环处理面：逐环 check（工件已达标？）/exec（机器环执行）/instr（人工环待办指令）。

    经 RegistryProbe 探测与 WizardDeps 执行，不持有状态（state 由 wizard 层管理）。
    """

    def __init__(self, wizard: OnboardingWizard) -> None:
        self.w = wizard
        self.probe = RegistryProbe(wizard.deps)

    def check_candidate(self, req: OnboardingRequest) -> tuple[bool, str]:
        if not req.cand_id:
            return True, "免候选环（cand_id 为空，修复/直登场景）"
        entry = self.probe.cand_entry(req.cand_id)
        if entry:
            return True, f"候选 {req.cand_id} 已登记 status={entry.get('status')}"
        return False, f"候选 {req.cand_id} 未登记"

    def exec_candidate(self, req: OnboardingRequest) -> tuple[str, str, str]:
        if req.candidate_entry is None:
            return (
                RingStatus.MANUAL_WAIT,
                "",
                "人工环待办（SOP §2）：对该中类做全网三重扫描挖矿（生产者/获取方式/因子文献），"
                f"按 §3 字段模板填写条目；爬虫默认否决。产出后经 start --candidate-entry 或直接编辑 "
                f"{CANDIDATES_REGISTRY} 登记后 resume。",
            )
        entry = dict(req.candidate_entry)
        cand_id = str(entry.get("cand_id", ""))
        if not cand_id:
            return RingStatus.FAILED, "candidate_entry 缺 cand_id", ""
        if self.probe.cand_entry(cand_id) is not None:
            return RingStatus.DONE, f"候选 {cand_id} 已存在（幂等跳过）", ""
        missing = [
            k for k in ("name", "vendor", "acquire_mode", "cost", "score", "target_table", "status") if k not in entry
        ]
        if missing:
            return RingStatus.FAILED, f"candidate_entry 缺必填键: {missing}", ""
        if entry.get("status") not in _ALLOWED_CAND_STATUS:
            return RingStatus.FAILED, f"status 非法: {entry.get('status')!r}", ""
        score = entry.get("score") or {}
        bad = [k for k in _SCORE_KEYS if not isinstance(score.get(k), int) or score[k] < 0]
        if bad:
            return RingStatus.FAILED, f"四格评分缺失/非法: {bad}", ""
        path = self.w.deps.resolve(CANDIDATES_REGISTRY)
        _append_text_block(path, _yaml_block(entry))
        return RingStatus.DONE, f"候选 {cand_id} 已尾插登记（status={entry['status']}）", ""

    def check_graduation(self, req: OnboardingRequest) -> tuple[bool, str]:
        if not req.cand_id:
            return True, "免毕业环（无候选）"
        entry = self.probe.cand_entry(req.cand_id)
        if entry and str(entry.get("status")) in _GRADUATED_STATUSES:
            return True, f"候选 {req.cand_id} 已毕业（status={entry['status']}）"
        return False, "候选尚未毕业（integrated/promoted）"

    def instr_graduation(self, req: OnboardingRequest) -> str:
        entry = self.probe.cand_entry(req.cand_id) if req.cand_id else None
        mode = str((entry or {}).get("acquire_mode", ""))
        score = (entry or {}).get("score") or {}
        passed = all(isinstance(score.get(k), int) and score[k] >= 3 for k in _SCORE_KEYS)
        route = (
            "免费+四格≥3 → 直接推进"
            if mode == "api_free" and passed
            else "api_register → 打包报 Owner 批量注册"
            if mode == "api_register"
            else "paid → 标价报 Owner 审"
        )
        return (
            f"人工环待办（SOP §3 报批）：路由建议={route}；Owner 批准并落实注册后执行 "
            f"confirm --source-id {req.source_id} --ring graduation --note '<批复留痕>'"
        )

    def check_ds_registry(self, req: OnboardingRequest) -> tuple[bool, str]:
        if self.probe.ds_entry(req.source_id):
            return True, f"DS 条目 {req.source_id} 已在册"
        return False, f"DS 条目 {req.source_id} 缺席（两册联动待落）"

    def exec_ds_registry(self, req: OnboardingRequest, state: dict[str, Any]) -> tuple[str, str, str]:
        if state["rings"][RING_GRADUATION]["status"] != RingStatus.DONE:
            return RingStatus.FAILED, "毕业环未闭环，拒绝 DS 册登记（O4 联动前置）", ""
        if self.probe.ds_entry(req.source_id):
            return RingStatus.DONE, f"DS 条目 {req.source_id} 已存在（幂等跳过）", ""
        cand = self.probe.cand_entry(req.cand_id) if req.cand_id else None
        entry: dict[str, Any] = {
            "id": req.source_id,
            "module_id": _BLUEPRINT_ANCHOR,
            "runtime_id": req.provider or (req.source_id[len("DS-") :].lower() or "unknown"),
            "name": (cand or {}).get("name", req.source_id),
            "vendor": (cand or {}).get("vendor", ""),
            "category": "alt_data",
            "status": "active",
            "coverage": (cand or {}).get("coverage", ""),
            "target_table": req.table or (cand or {}).get("target_table", ""),
            "operation_manual": f"src/zephyr/data/implementations/{req.provider or 'todo'}_provider.py",
            "onboarding": f"onboarding_wizard 编排骨架条目（{now_utc().isoformat()} by {self.w.deps.session}）；"
            "毕业复核义务：补齐 interface_types/policy/探活腿等字段（DS-CAND-011 范式）",
        }
        _append_text_block(self.w.deps.resolve(DS_REGISTRY), _yaml_block(entry))
        if req.cand_id:
            _flip_candidate_status(self.w.deps.resolve(CANDIDATES_REGISTRY), req.cand_id, "promoted")
        return RingStatus.DONE, f"DS 条目已登记+候选翻转 promoted（O4 两册联动，{req.source_id}）", ""

    def check_provider(self, req: OnboardingRequest) -> tuple[bool, str]:
        if not req.provider:
            return True, "免 provider 环（未指定）"
        if self.probe.provider_path(req).exists():
            return True, f"provider 文件在位: {req.provider}_provider.py"
        return False, "provider 未落地"

    def instr_provider(self, req: OnboardingRequest) -> str:
        return (
            "人工环待办（SOP §6）：src/zephyr/data/implementations/ 新增 "
            f"{req.provider}_provider.py，接口经 capability 三闸（capability_validator/"
            "capability_semantic_gate/capability_symbol_gate）；fallback_sources 必填（哪怕显式置空+原因）。"
            "完成后 resume 自动检出。"
        )

    def check_ddl(self, req: OnboardingRequest, state: dict[str, Any]) -> tuple[bool, str]:
        marker = state.get("ring_outputs", {}).get("ddl_applied")
        if marker:
            return True, f"DDL 已部署（{marker}）"
        return False, "DDL 未部署"

    def exec_ddl(self, req: OnboardingRequest, state: dict[str, Any]) -> tuple[str, str, str]:
        schema_path = self.probe.schema_path(req)
        if not str(schema_path):
            return RingStatus.FAILED, "request 缺 table/schema_domain，无法定位 DDL 设计件", ""
        if not schema_path.exists():
            return (
                RingStatus.MANUAL_WAIT,
                "",
                f"人工环待办（SOP §4-§5 字段/表设计）：创建 {schema_path.relative_to(self.w.deps.repo_root)}——"
                "PIT 锚时间列+三件套（data_source/quality_flag/ingest_ts DateTime64(3,'UTC')）+频率枚举固定；"
                "庁前缀路由+ReplacingMergeTree 月分区默认。完成后 resume 自动执行部署。",
            )
        cmd = req.derived_ddl_command()
        if not cmd:
            return RingStatus.FAILED, "无法派生 DDL 命令", ""
        rc, output = self.probe.runner()(cmd)
        if rc != 0:
            return RingStatus.FAILED, f"DDL 脚本失败 rc={rc}: {cmd[-1]} — {output[-300:]}", ""
        ts = now_utc().isoformat()
        state.setdefault("ring_outputs", {})["ddl_applied"] = ts
        return RingStatus.DONE, f"DDL 部署完成（脚本自带 verify 引擎校验）: {cmd[-1]}", ""

    def check_category(self, req: OnboardingRequest) -> tuple[bool, str]:
        hit = self.probe.category_hit(req)
        if hit:
            return True, f"品类已在册: {hit.get('category_id')}"
        return False, "品类未登记"

    def exec_category(self, req: OnboardingRequest) -> tuple[str, str, str]:
        hit = self.probe.category_hit(req)
        if hit:
            return RingStatus.DONE, f"品类已在册（幂等跳过）: {hit.get('category_id')}", ""
        if not req.table:
            return RingStatus.FAILED, "request 缺 table，无法登记品类", ""
        db, table = req.table.split(".", 1)
        schema_rel = str(SCHEMAS_DIR / req.schema_domain / f"{table}.py") if req.schema_domain else None
        entry = {
            "category_id": table,
            "name": req.description or table,
            "engine": "clickhouse",
            "database": db,
            "table": table,
            "schema_file": schema_rel,
            "data_type": "待补",
            "lifecycle": "hot_90d",
            "sla_level": "L3",
            "enabled": True,
            "hard_constraint": None,
            "calc_mode": "none",
            "frequency": "待补",
            "data_source": [req.provider] if req.provider else ["internal"],
            "blueprint": None,
            "onboarding_note": f"onboarding_wizard 编排骨架（{now_utc().isoformat()}）；data_type/frequency 复核义务",
        }
        path = self.w.deps.resolve(CATEGORY_REGISTRY)
        _append_text_block(path, _yaml_block(entry, indent=""))
        return RingStatus.DONE, f"品类骨架条目已尾插: {req.table}", ""

    def build_task_entry(self, req: OnboardingRequest) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "task_id": req.task_id,
            "table": req.table,
            "source": req.provider,
            "schedule": req.schedule_slot,
            "incremental": True,
            "date_col": req.date_col,
            "dependencies": [],
            "capability": req.capability,
            "fallback_sources": list(req.fallback_sources),
            "extra": {"description": req.description or f"onboarding_wizard 编排登记（{req.source_id}）"},
        }
        if req.fallback_note:
            entry["extra"]["fallback_note"] = req.fallback_note
        if req.disabled:
            entry["disabled"] = True
            entry["disabled_reason"] = req.disabled_reason
        return entry

    def check_task(self, req: OnboardingRequest) -> tuple[bool, str]:
        entry = self.probe.task_entry(req.task_id)
        if not entry:
            return False, "任务未登记"
        errors = self.probe.task_o2o3_errors(entry)
        if errors:
            return False, "；".join(errors)
        return True, f"任务已登记且过 O2/O3 校验: {req.task_id}"

    def exec_task(self, req: OnboardingRequest, state: dict[str, Any]) -> tuple[str, str, str]:
        existing = self.probe.task_entry(req.task_id)
        if existing:
            errors = self.probe.task_o2o3_errors(existing)
            return (
                (RingStatus.FAILED, "；".join(errors), "")
                if errors
                else (
                    RingStatus.DONE,
                    f"任务已存在且过 O2/O3（幂等跳过）: {req.task_id}",
                    "",
                )
            )
        if not req.task_id or not req.table:
            return RingStatus.FAILED, "request 缺 task_id/table", ""
        if not req.fallback_sources and not req.fallback_note:
            return (
                RingStatus.FAILED,
                "O2 登记时拦截：fallback_sources 必填（单源无备=停更即断供；显式置空须给 fallback_note 原因）",
                "",
            )
        entry = self.build_task_entry(req)
        path = self.w.deps.resolve(TASKS_CONFIG)
        _append_text_block(path, _yaml_block(entry))
        warnings = self.validate_tasks()
        detail = f"任务条目已尾插: {req.task_id}"
        if warnings:
            state.setdefault("ring_outputs", {})["task_warnings"] = warnings
            detail += f"（validate_tasks_yaml WARN {len(warnings)} 条，已录 state）"
        return RingStatus.DONE, detail, ""

    def validate_tasks(self) -> list[str]:
        try:
            from zephyr.data.table_registry import get_registry  # noqa: PLC0415 — 懒加载避免重链

            doc = _load_yaml_doc(self.w.deps.resolve(TASKS_CONFIG), "tasks")
            return list(get_registry().validate_tasks_yaml(doc["tasks"]))
        except Exception as exc:  # noqa: BLE001 — 校验器不可用不阻断编排，记录即走
            return [f"validate_tasks_yaml 不可用: {exc}"]

    def check_slot(self, req: OnboardingRequest) -> tuple[bool, str]:
        if not req.schedule_slot:
            return True, "免槽位环（未指定）"
        if req.schedule_slot in self.probe.slot_names():
            warn = "（⚠ daily_event 有断供前科：验收环必须探活，SOP §7）" if req.schedule_slot == "daily_event" else ""
            return True, f"槽位合法: {req.schedule_slot}{warn}"
        return False, f"槽位 {req.schedule_slot} 不在 schedule.yaml"

    def instr_first_run(self, req: OnboardingRequest) -> str:
        return (
            "人工环待办（SOP §8.1-8.3）：首跑全量回填（分块+progress_store 断点续传，缺口登记 known_data_gaps）→ "
            "对账（行数 vs 源端口径+抽样字段比对）→ 质量闸（quality_gate→integrity_checker→cross_source_validator）"
            "→ 失败必须留痕 failures/{date}_{task}.json。完成后 "
            f"confirm --source-id {req.source_id} --ring first_run --note '<首跑结论>'"
        )

    def instr_acceptance(self, req: OnboardingRequest) -> str:
        slot_warn = (
            "该任务挂 daily_event 槽（断供前科），探活腿为强制项。" if req.schedule_slot == "daily_event" else ""
        )
        consumer = req.consumer or "（§9 路由表选默认消费端）"
        return (
            "人工环待办（SOP §8.4+§9 接通验收三查，缺一不算通）："
            "①表有数且 max(date) 新鲜；②调度器日志/心跳可见真实执行记录；③目标消费者实际查得到数。"
            f"另须：supply_sentinel 探活腿登记{slot_warn}；消费者登记≥1（{consumer}）；巡检/停更阈值生效。"
            f"全部过后 confirm --source-id {req.source_id} --ring acceptance --note '<三查结论>'"
        )


class OnboardingWizard:
    """十环状态机。start=新上架；resume=断点续跑；confirm=人工环回执；status/checklist=只读。"""

    RINGS: tuple[tuple[str, str, str], ...] = (
        (RING_CANDIDATE, "候选登记", "SOP §1-§3"),
        (RING_GRADUATION, "毕业报批", "SOP §3"),
        (RING_DS_REGISTRY, "DS 册登记", "SOP §3 毕业流程+O4 两册联动"),
        (RING_PROVIDER, "Provider 接入", "SOP §6"),
        (RING_DDL, "建表 DDL", "SOP §4-§5"),
        (RING_CATEGORY, "品类登记", "SOP §5.4"),
        (RING_TASK, "任务登记", "SOP §7+O2/O3"),
        (RING_SLOT, "槽位核验", "SOP §7 调度槽位"),
        (RING_FIRST_RUN, "首跑回填", "SOP §8.1-8.3"),
        (RING_ACCEPTANCE, "验收三查+哨兵腿", "SOP §8.4-§9"),
    )
    MANUAL_RINGS: frozenset[str] = frozenset({RING_GRADUATION, RING_PROVIDER, RING_FIRST_RUN, RING_ACCEPTANCE})

    def __init__(self, deps: WizardDeps, request: OnboardingRequest | None = None) -> None:
        self.deps = deps
        self.request = request
        self.store = OnboardingStateStore(deps)
        self.ops = RingOps(self)

    # ---- 状态机主循环 ----

    def start(self, dry_run: bool = False) -> WizardReport:
        if self.request is None:
            raise OnboardingWizardError("start 需要 request")
        self.request.validate()
        source_id = self.request.source_id
        if self.store.state_path(source_id).exists() and not dry_run:
            raise OnboardingWizardError(f"{source_id} 已有在途 state（走 resume，勿重复 start）")
        state = self._new_state(source_id)
        return self._run(state, dry_run=dry_run)

    def resume(self, source_id: str, dry_run: bool = False) -> WizardReport:
        state = self.store.load(source_id, self)
        if state is None:
            raise OnboardingWizardError(f"{source_id} 无在途 state（走 start）")
        return self._run(state, dry_run=dry_run)

    def confirm(self, source_id: str, ring_id: str, note: str) -> WizardReport:
        state = self.store.load(source_id, self)
        if state is None:
            raise OnboardingWizardError(f"{source_id} 无在途 state")
        if ring_id not in self.MANUAL_RINGS:
            raise OnboardingWizardError(f"{ring_id} 非人工环，禁止 confirm 代签")
        rec = state["rings"][ring_id]
        if rec["status"] != RingStatus.MANUAL_WAIT:
            raise OnboardingWizardError(f"{ring_id} 状态={rec['status']}，仅 manual_wait 可 confirm")
        rec.update(
            status=RingStatus.DONE, detail=f"人工回执: {note}", confirmed_note=note, updated_at=now_utc().isoformat()
        )
        self.store.persist(state)
        self.store.append_checklist(source_id, RingRecord(**rec))
        return self._report(state, stopped_at="", next_action="resume 续跑下一环")

    def status(self, source_id: str) -> WizardReport:
        state = self.store.load(source_id, self)
        if state is None:
            raise OnboardingWizardError(f"{source_id} 无在途 state")
        return self._report(state, stopped_at="", next_action="")

    def checklist(self, source_id: str) -> str:
        path = self.store.checklist_path(source_id)
        if not path.exists():
            raise OnboardingWizardError(f"{source_id} 无 checklist")
        return path.read_text(encoding="utf-8")

    def _new_state(self, source_id: str) -> dict[str, Any]:
        rings = {ring_id: RingRecord(ring_id=ring_id).to_dict() for ring_id, _, _ in self.RINGS}
        return {
            "source_id": source_id,
            "session": self.deps.session,
            "created_at": now_utc().isoformat(),
            "updated_at": "",
            "sop_ref": SOP_REF,
            "request": asdict(self.request),
            "rings": rings,
            "ring_outputs": {},
        }

    def _run(self, state: dict[str, Any], dry_run: bool) -> WizardReport:
        req = OnboardingRequest(**state["request"])
        stopped_at, next_action = "", ""
        for ring_id, title, sop in self.RINGS:
            rec = state["rings"][ring_id]
            if rec["status"] == RingStatus.DONE:
                continue
            ok, detail = self._check_ring(ring_id, req, state)
            if ok:
                rec.update(status=RingStatus.DONE, detail=detail, updated_at=now_utc().isoformat())
                if not dry_run:
                    self.store.persist(state)
                    self.store.append_checklist(state["source_id"], RingRecord(**rec))
                continue
            if dry_run:
                kind = "人工" if ring_id in self.MANUAL_RINGS else "机器"
                rec["detail"] = f"[dry-run 计划] {kind}环 {title}（{sop}）: {detail}"
                continue
            if ring_id in self.MANUAL_RINGS:
                instruction = self._manual_instruction(ring_id, req)
                rec.update(
                    status=RingStatus.MANUAL_WAIT,
                    detail=detail,
                    instruction=instruction,
                    updated_at=now_utc().isoformat(),
                )
                self.store.persist(state)
                self.store.append_checklist(state["source_id"], RingRecord(**rec))
                stopped_at, next_action = ring_id, instruction
                break
            status, edetail, einstruction = self._exec_ring(ring_id, req, state)
            rec.update(status=status, detail=edetail, instruction=einstruction, updated_at=now_utc().isoformat())
            self.store.persist(state)
            self.store.append_checklist(state["source_id"], RingRecord(**rec))
            if status != RingStatus.DONE:
                stopped_at = ring_id
                next_action = einstruction or f"机器环 {ring_id} 失败：修复后 resume 重试"
                break
        if dry_run:
            report = self._report(state, stopped_at="", next_action="dry-run：全链已打印，零落盘")
            report.dry_run = True
            return report
        if not stopped_at:
            next_action = "十环全部闭环"
        return self._report(state, stopped_at=stopped_at, next_action=next_action)

    def _check_ring(self, ring_id: str, req: OnboardingRequest, state: dict[str, Any]) -> tuple[bool, str]:
        dispatch: dict[str, Callable[[], tuple[bool, str]]] = {
            RING_CANDIDATE: lambda: self.ops.check_candidate(req),
            RING_GRADUATION: lambda: self.ops.check_graduation(req),
            RING_DS_REGISTRY: lambda: self.ops.check_ds_registry(req),
            RING_PROVIDER: lambda: self.ops.check_provider(req),
            RING_DDL: lambda: self.ops.check_ddl(req, state),
            RING_CATEGORY: lambda: self.ops.check_category(req),
            RING_TASK: lambda: self.ops.check_task(req),
            RING_SLOT: lambda: self.ops.check_slot(req),
            RING_FIRST_RUN: lambda: (False, "首跑未回执"),
            RING_ACCEPTANCE: lambda: (False, "验收未回执"),
        }
        return dispatch[ring_id]()

    def _exec_ring(self, ring_id: str, req: OnboardingRequest, state: dict[str, Any]) -> tuple[str, str, str]:
        dispatch: dict[str, Callable[[], tuple[str, str, str]]] = {
            RING_CANDIDATE: lambda: self.ops.exec_candidate(req),
            RING_DS_REGISTRY: lambda: self.ops.exec_ds_registry(req, state),
            RING_DDL: lambda: self.ops.exec_ddl(req, state),
            RING_CATEGORY: lambda: self.ops.exec_category(req),
            RING_TASK: lambda: self.ops.exec_task(req, state),
        }
        if ring_id not in dispatch:
            return RingStatus.FAILED, f"{ring_id} 非机器环", ""
        return dispatch[ring_id]()

    def _manual_instruction(self, ring_id: str, req: OnboardingRequest) -> str:
        if ring_id == RING_GRADUATION:
            return self.ops.instr_graduation(req)
        if ring_id == RING_PROVIDER:
            return self.ops.instr_provider(req)
        if ring_id == RING_FIRST_RUN:
            return self.ops.instr_first_run(req)
        return self.ops.instr_acceptance(req)

    def _report(self, state: dict[str, Any], stopped_at: str, next_action: str) -> WizardReport:
        rings = [RingRecord(**state["rings"][rid]) for rid, _, _ in self.RINGS]
        return WizardReport(
            source_id=state["source_id"],
            dry_run=False,
            stopped_at=stopped_at,
            next_action=next_action,
            rings=rings,
        )


# ========== CLI（人工步进入口，无守护无轮询） ==========


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.data.onboarding_wizard", description="F02 数据源上架十环向导"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="新上架：从候选环起跑")
    p_start.add_argument("--source-id", required=True)
    p_start.add_argument("--cand-id", default="")
    p_start.add_argument("--table", default="")
    p_start.add_argument("--schema-domain", default="")
    p_start.add_argument("--provider", default="")
    p_start.add_argument("--task-id", default="")
    p_start.add_argument("--schedule-slot", default="")
    p_start.add_argument("--date-col", default="")
    p_start.add_argument("--capability", default="")
    p_start.add_argument("--description", default="")
    p_start.add_argument("--fallback-sources", nargs="*", default=[])
    p_start.add_argument("--fallback-note", default="")
    p_start.add_argument("--consumer", default="")
    p_start.add_argument("--dry-run", action="store_true")

    p_resume = sub.add_parser("resume", help="断点续跑")
    p_resume.add_argument("--source-id", required=True)
    p_resume.add_argument("--dry-run", action="store_true")

    p_confirm = sub.add_parser("confirm", help="人工环回执")
    p_confirm.add_argument("--source-id", required=True)
    p_confirm.add_argument("--ring", required=True)
    p_confirm.add_argument("--note", required=True)

    p_status = sub.add_parser("status", help="查看十环状态")
    p_status.add_argument("--source-id", required=True)

    p_checklist = sub.add_parser("checklist", help="打印 checklist 留痕")
    p_checklist.add_argument("--source-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    deps = WizardDeps(repo_root=Path.cwd())
    wizard = OnboardingWizard(deps)
    try:
        if args.command == "start":
            request = OnboardingRequest(
                source_id=args.source_id,
                cand_id=args.cand_id,
                table=args.table,
                schema_domain=args.schema_domain,
                provider=args.provider,
                task_id=args.task_id,
                schedule_slot=args.schedule_slot,
                date_col=args.date_col,
                capability=args.capability,
                description=args.description,
                fallback_sources=list(args.fallback_sources),
                fallback_note=args.fallback_note,
                consumer=args.consumer,
            )
            wizard.request = request
            report = wizard.start(dry_run=args.dry_run)
        elif args.command == "resume":
            report = wizard.resume(args.source_id, dry_run=args.dry_run)
        elif args.command == "confirm":
            report = wizard.confirm(args.source_id, args.ring, args.note)
        elif args.command == "status":
            report = wizard.status(args.source_id)
        else:
            print(wizard.checklist(args.source_id))
            return 0
    except OnboardingWizardError as exc:
        print(f"[onboarding-wizard] 错误: {exc}", file=sys.stderr)
        return 1
    print(report.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
