# [BLUEPRINT] MOD-GOV_GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.rule_bridge.commit_preflight
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway (GitCommitGateway); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] scripts.git_commit (直连路径+--enqueue 入队预校验)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预检=提前失败不是豁免——同一套 gate 函数、锁内全套照跑兜底，预检只做锁外快败（方案 v2.1 P0-A，st-commitspeed-20260916）；白名单准入判据=gate 输入面仅 (files 清单 ∪ 磁盘内容 ∪ 会话态 ∪ 注册表)，禁依赖共享暂存区（防外来 WIP 假阳性拦截）；一过式失败清单（不短路，收集全部违规+逃生旗提示一次性返回，治重试环最长 30 连败）；基础设施异常（gate 抛异常）降级 degraded 不阻断（fail-open 于故障、fail-closed 于违规——锁内链仍是各 gate 自身语义的权威执行点）；预检全程不拿 _GlobalCommitLock、零写副作用（审计 jsonl 除外）
# [MODIFY-GUARD] PREFLIGHT_GATES 白名单准入须逐 gate 输入面审计（判据见 INVARIANTS）；escape_flag/skip_gates 映射与 git_commit.py argparse 旗标一一对应
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_preflight 永不抛异常——任何内部异常降级为 findings=[degraded 记录] 且 blocking=False；audit 写失败静默
# [TESTS] tests/governance/rule_bridge/test_commit_preflight.py
# [A_module] module_id=MOD-GOV_GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
commit_preflight.py — 提交通道预检前移（方案 v2.1 P0-A，st-commitspeed-20260916 施工）

病根（48h 遥测 .runtime/audit/commit_block_events.jsonl，2026-09-16 取证）
------------------------------------------------
527 次提交被门禁拦截，每次平均白烧 79s 门禁链才撞墙（P90=189s/max=988s），
失败→改旗→重跑全链循环平均 2.6 连败、最长 30 连败——确定性违规（没 claim/
跨域/缺 TTL 头/容量超限）本可在拿锁前 3-5 秒发现。锁内白烧还挤兑并发队列。

治本方案（方案 v2.1 §3.1 P0-A + §8.1 G9 加码）
--------
锁外对 --files 清单试跑确定性 gate 子集（PREFLIGHT_GATES 白名单）：
1. **一过式失败清单**：不短路，收集全部违规+逐项推荐逃生旗，一次返回
   （对比现状：锁内 first-fail 即断，AI 盲修一轮烧一轮全链）。
2. **入队预校验**：--enqueue 路径快照入袋前同款预检——注定死信的单子
   在入队那一刻死，不消耗 Serializer 落地算力（48h 死信 ~9% 属此类）。
3. **设施故障降级**：gate 抛异常记 degraded 不阻断（预检是快败优化不是
   权威执行点；锁内全套照跑）。

与 gate_preflight（P2⑦ 锁外预跑+锁内指纹采信）的关系
----------------------
正交互补：gate_preflight 预跑**内容扫描型** gate 让锁内采信（提速成功提交）；
本模块预检**确定性工作流** gate 让失败提交提前死（消灭失败税）。两者共享
"锁外只读、锁内权威"原则。

白名单准入判据（逐 gate 输入面审计，2026-09-16）
----------------------
- 信号型：SESSION-REQUIRED / CLAIM-REQUIRED / WORKTREE-REQUIRED（读会话注册
  表/claim/锁态，无文件面）
- files 驱动：TTL-METADATA / FILE-PLACEMENT-TTL / COMMIT-SCOPE /
  PROTECTED-PATHS（检查对象=本次 commit 的 files 清单）
- files 驱动 + 磁盘内容：DIRECTORY-CONTRACT（F5 2026-09-18；check_directory_contract.py
  以内联文件清单校验 ≤500 文件、读其磁盘 doc_type/扩展名，零 git diff --cached 依赖；
  >500 退 --all-files 与锁内权威链同行为，非新增假阳性面）
- own-scope：FOLDER-CAPACITY-HARD-LIMIT / REGISTRY-MASS-DELETION（外来 staged
  落审计不阻断，无连坐面）
- **禁入**：依赖 git diff --cached 全暂存扫描的 gate（DEPGRAPH-PRE-REGISTRATION/
  RENAME-DEPGRAPH-SYNC 等）——外来 WIP 会造成预检假阳性；own-scope 化后再扩。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: files 清单+会话态
#   fields: files: list[str], session_id: str, skip_gate_ids: frozenset[str]
#   code: run_preflight(gateway, files, session_id, ...)
# 层: 算法
# - id: A1
#   name_zh: ① 白名单过滤
#   name_en: filter_whitelist
#   intro: specs_sorted 按 PREFLIGHT_GATES 过滤+skip_gate_ids 剔除（逃生旗对应 gate）
#   desc: specs 注入位供测试；白名单外 gate 一律不碰
# - id: A2
#   name_zh: ② 逐 gate 试跑收集
#   name_en: run_and_collect
#   intro: 逐 gate 调 spec.check，异常降级 degraded 记录继续（一过式不短路）
#   desc: 全部违规收集为 findings；passed 不入清单
# - id: A3
#   name_zh: ③ 审计落盘
#   name_en: audit_write
#   intro: .runtime/audit/preflight_events.jsonl 一行（ts/session/event/gates/ms）
#   desc: blocked=有违规；passed=干净；degraded=设施异常；写失败静默
# 层: 输出
# - id: O1
#   name: CommitPreflightResult
#   fields: findings: list[PreflightFinding]; blocking: bool; degraded: list[str]; elapsed_ms: float
#   code: return CommitPreflightResult(...)
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 惰性导入防循环（对标 gate_cache_preflight.py 先例）
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

logger = logging.getLogger(__name__)

#: 预检白名单（准入判据=模块 docstring；扩展 MUST 先逐 gate 输入面审计）。
#: 2026-09-16 v1 准入 9 道：信号型×3 + files 驱动×4 + own-scope×2。
#: W4 own-scope 批落地后扩 5 道（2026-09-16 同日）：MANUAL-ONLY-PERMANENT/
#: PERM-TRIGGER/TEST-SOURCE-CONSISTENCY（own-scope 求交后输入=files∪held，外来
#: 剔除落审计）+ TABLE-NAME-REGISTRY（files 优先驱动）+ DATETIME-NOW-FORBIDDEN
#: （既有 own-scope，#ARCH-GATE-OWN-SCOPE-001 第三批）。
PREFLIGHT_GATES: frozenset[str] = frozenset(
    {
        "SESSION-REQUIRED",
        "CLAIM-REQUIRED",
        "WORKTREE-REQUIRED",
        "TTL-METADATA",
        "FILE-PLACEMENT-TTL",
        "COMMIT-SCOPE",
        "PROTECTED-PATHS",
        "FOLDER-CAPACITY-HARD-LIMIT",
        "REGISTRY-MASS-DELETION",
        "MANUAL-ONLY-PERMANENT",
        "PERM-TRIGGER",
        "TEST-SOURCE-CONSISTENCY",
        "TABLE-NAME-REGISTRY",
        "DATETIME-NOW-FORBIDDEN",
        # 2026-09-16 晚（st-resched-fix 死信实证）：新会话首提交撞 LOOKUP 门禁
        # 才知道要 find——进预检后 1 秒快败+精确指引，队列死信类消灭。
        # 输入面审计：信号型（会话 lookup 审计态+files 分类豁免判定），无暂存依赖。
        "CAPABILITY-LOOKUP-REQUIRED",
        # 2026-09-18（st-flashspeed-20260918 F5 DC 摩擦前置化）：DIRECTORY-CONTRACT
        # 进预检——DCR-005 扩展名违规（.py/.json 误放 docs/_working/，A2 堵点本 16 次
        # +本账 58 次 DCR-005）本可锁外 3-5s 快败并给「建议合规目录」，不必烧完整门禁链。
        # 输入面审计（PASS）：gate 输入=files 清单 ∪ 磁盘内容（check_directory_contract.py
        # 以**内联文件清单**校验 ≤500 文件，只检本次 commit 的 files、读其磁盘 doc_type/扩展名），
        # **零 git diff --cached / 零共享暂存区依赖**——满足白名单准入判据（防外来 WIP 假阳性）。
        # >500 文件退 --all-files 全量扫描=与锁内权威链同行为（非新增假阳性面），且属罕见大批次。
        # 语义不动：锁内 DIRECTORY-CONTRACT(30) 仍 fail-closed 权威执行，预检只前移快败。
        "DIRECTORY-CONTRACT",
    }
)

#: 违规→逃生旗提示映射（与 git_commit.py argparse 一一对应；无旗=真违规须修）。
_ESCAPE_HINTS: dict[str, str] = {
    "WORKTREE-REQUIRED": "--allow-non-worktree（2026-08-13 裁定 AI 可默认）",
    "COMMIT-SCOPE": "--allow-multi-domain（跨域重构/注册表同批场景）",
    "FILE-PLACEMENT-TTL": "--allow-promote（creation_token 已登记前提）",
    "SESSION-REQUIRED": "session_worktree_start 注册本会话后重试",
    "CLAIM-REQUIRED": "改前 claim：lock_files.py acquire <file> <sid>",
    "PROTECTED-PATHS": "受保护路径须 Owner 审批（无 CLI 逃生旗）",
    "TTL-METADATA": "补 frontmatter ttl/completes_when 字段",
    "FOLDER-CAPACITY-HARD-LIMIT": "文件挪子目录（平铺目录容量上限）",
    "REGISTRY-MASS-DELETION": "注册表只应增长——检查是否误删条目",
    "MANUAL-ONLY-PERMANENT": "permanent 脚本必须事件触发——补事件订阅注册",
    "PERM-TRIGGER": "时间触发模式须注册事件订阅（禁 cron/Timer/sleep-loop）",
    "TEST-SOURCE-CONSISTENCY": "测试 import 的符号须与源码一致（名称漂移）",
    "TABLE-NAME-REGISTRY": "表名走 TableRegistry 真源，禁硬编码字符串",
    "DATETIME-NOW-FORBIDDEN": "生成器代码禁裸时间戳函数（详情见该门禁消息）——改用 now_utc()",
    "CAPABILITY-LOOKUP-REQUIRED": "施工前能力反查：capability_lookup.CapabilityLookup().find('<关键词>', session_id='<本会话>') 或 MCP rule_discovery（一次即可，审计按会话记账）",
    # F5 DC 摩擦前置化（2026-09-18）：DCR-005/006 扩展名违规给「建议合规目录」。
    # 实测主簇=.py/.json 误放 docs/_working/（allowed=.csv/.html/.md/.yaml）。
    "DIRECTORY-CONTRACT": (
        "目录契约违规（DCR-005/006 扩展名 ∉ 该目录 allowed 清单，详情见门禁消息含 allowed 清单）——"
        "建议合规目录：①.py 脚本→挪 scripts/ 或 src/（docs/_working/ 禁 .py）；"
        "②.json 证据/报告→转 .yaml/.csv，或挪 .runtime/、data/ 等允许 .json 的目录；"
        "③其余→查 directory_contract.yaml 该路径 directory_extensions.allowed 改用合规扩展名。"
        "注：docs/_working/ allowed 净增 .json=Owner 门位（见 F5 裁定书提案，勿自签）"
    ),
}

_AUDIT_PATH = Path(".runtime/audit/preflight_events.jsonl")


@dataclass(frozen=True)
class PreflightFinding:
    """单条预检违规（gate_id+详情+逃生旗提示）。"""

    gate_id: str
    detail: str
    escape_hint: str = ""

    def render(self) -> str:
        hint = f"\n      逃生通道: {self.escape_hint}" if self.escape_hint else ""
        head = self.detail.splitlines()[0][:160] if self.detail else ""
        return f"  [{self.gate_id}] {head}{hint}"


@dataclass(frozen=True)
class CommitPreflightResult:
    """预检结果：findings=违规清单；blocking=应阻断；degraded=设施异常 gate。"""

    findings: list[PreflightFinding] = field(default_factory=list)
    degraded: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0

    @property
    def blocking(self) -> bool:
        return bool(self.findings)

    def render_report(self, session_id: str) -> str:
        if not self.findings:
            lines = [f"PREFLIGHT PASSED（{session_id}，{self.elapsed_ms / 1000:.1f}s，预检干净放行）"]
            if self.degraded:
                lines.append(f"  [degraded] 设施异常不阻断（锁内权威链兜底）: {', '.join(self.degraded)}")
            return "\n".join(lines)
        lines = [
            "=" * 78,
            f"PREFLIGHT BLOCKED（锁外预检，{len(self.findings)} 项违规一次给全——"
            "锁内白烧已避免；逐项修复或按提示加旗后重试）",
            f"session={session_id} 耗时={self.elapsed_ms / 1000:.1f}s",
        ]
        lines.extend(f.render() for f in self.findings)
        if self.degraded:
            lines.append(f"  [degraded] 设施异常不阻断（锁内权威链兜底）: {', '.join(self.degraded)}")
        lines.append("=" * 78)
        return "\n".join(lines)


def _write_audit(gateway: Any, record: dict) -> None:
    """审计落 .runtime/audit/preflight_events.jsonl（失败静默，不阻断主链路）。"""
    try:
        from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

        audit_dir = Path(str(gateway.project_root)) / ".runtime" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        rec = {"timestamp": now_utc().isoformat(), **record}
        with (audit_dir / "preflight_events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def run_preflight(
    gateway: "GitCommitGateway",
    files: list[str],
    session_id: str,
    skip_gate_ids: frozenset[str] | set[str] = frozenset(),
    *,
    specs: "list[GateSpec] | None" = None,
    audit_event: str = "direct",
) -> CommitPreflightResult:
    """锁外预检白名单 gate（一过式收集，不短路）。

    Args:
        gateway: GitCommitGateway 实例（只读使用——run_git/注册表/会话态）。
        files: 本次 commit 文件清单（与 gw.commit 同口径）。
        session_id: 会话标识。
        skip_gate_ids: 逃生旗对应跳过的 gate 集（由调用方按 argparse 旗映射）。
        specs: 测试注入位（缺省=gateway._gate_registry.specs_sorted()）。
        audit_event: 审计事件标签（direct/enqueue）。

    Returns:
        CommitPreflightResult——findings 非空=应快败；degraded=设施异常不阻断。
    """
    t0 = time.monotonic()
    findings: list[PreflightFinding] = []
    degraded: list[str] = []
    try:
        if specs is None:
            specs = gateway._gate_registry.specs_sorted()  # noqa: SLF001 — 注册表快照唯读
        targets = [s for s in specs if s.gate_id in PREFLIGHT_GATES and s.gate_id not in skip_gate_ids]
        for spec in targets:
            try:
                result = spec.check(gateway, list(files), session_id=session_id)
                passed, detail = (result[0], result[1] if len(result) > 1 else "") if isinstance(result, tuple) else (True, "")
                if not passed:
                    findings.append(
                        PreflightFinding(
                            gate_id=spec.gate_id,
                            detail=str(detail),
                            escape_hint=_ESCAPE_HINTS.get(spec.gate_id, ""),
                        )
                    )
            except Exception:  # noqa: BLE001 — 设施异常降级不阻断（锁内权威链兜底）
                degraded.append(spec.gate_id)
                logger.warning("preflight gate %s degraded（不阻断，锁内兜底）", spec.gate_id, exc_info=True)
    except Exception:  # noqa: BLE001 — 预检整体异常=放行走锁内现行路径
        logger.warning("preflight 自身异常，降级放行（锁内权威链兜底）", exc_info=True)
        return CommitPreflightResult(findings=[], degraded=["__preflight__"], elapsed_ms=round((time.monotonic() - t0) * 1000, 1))
    elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
    _write_audit(
        gateway,
        {
            "session_id": session_id,
            "event": "blocked" if findings else "passed",
            "path": audit_event,
            "gates_failed": [f.gate_id for f in findings],
            "degraded": degraded,
            "files_count": len(files),
            "ms": elapsed_ms,
        },
    )
    return CommitPreflightResult(findings=findings, degraded=degraded, elapsed_ms=elapsed_ms)
