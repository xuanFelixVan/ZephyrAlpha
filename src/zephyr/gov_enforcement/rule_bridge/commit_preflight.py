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
import os
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
        # ── D1 预检扩容（st-commitchain-20260922，Owner R1；0921 死信杀手榜前三家族）──
        # 输入面审计（PASS）：RULING-REFERENCE(74)/ARCH-REFERENCE(75) 经 _reference_helpers.
        # collect_new_refs_by_file 读 files 磁盘内容 ∪ HEAD registry（git show）——零暂存依赖。
        # 死信实证：taskcards 0032（引用了裁定#392 的 D 后缀悬空号——后缀未登记即悬空）+ code-doc 20 连败主因，秒级可挡在队外。
        "RULING-REFERENCE",
        "ARCH-REFERENCE",
        # 输入面审计（PASS）：EXEMPT-ZONE-FM(87) _check 直接遍历 files 参数逐文件读磁盘
        # frontmatter（os.path.isfile + rel 路径）——零暂存依赖。死信实证：0921×11+0922 当日。
        "EXEMPT-ZONE-FM",
        # CREATE-GUARD / NO-BARE-SQL 为 staged-diff 依赖型（diff --cached --diff-filter=A /
        # _get_added_lines），不直接准入——经下方 _INLINE_PREFLIGHT_CHECKS 内联适配层
        # （磁盘 vs HEAD 等价判定）进预检；TRANSLATION-COVERAGE 适配面大，挂起待复测。
    }
)

# 内联适配层注册表（st-commitchain-20260922）：(gate_id, check(gateway, files, **kw))。
# 设计铁律：检测核心=复用 gate 模块既有函数/正则（不造第二检测器，全资产净零 §4.1）；
# 适配只做「输入面等价替换」（磁盘 vs HEAD 的增行/新文件判定 ≈ 落地时 staged diff，
# 因入队语义下磁盘内容=快照内容，git_commit.py:797-799 已论证）；预检只快败不豁免，
# 锁内权威链照跑（本模块 INVARIANTS）。
_INLINE_PREFLIGHT_CHECKS: list[tuple] = []


def _head_tracked_relset(gateway: GitCommitGateway) -> set[str]:
    """HEAD 已跟踪相对路径集（单次 ls-tree，新文件判定的唯一 git 面——非共享暂存区）。"""
    out = gateway.run_git(["git", "ls-tree", "-r", "HEAD", "--name-only"])
    if getattr(out, "returncode", 1) != 0:
        raise RuntimeError((getattr(out, "stderr", "") or "ls-tree failed")[:200])
    return {ln.strip() for ln in (out.stdout or "").splitlines() if ln.strip()}


def _rel_of(gateway: GitCommitGateway, f: str) -> str:
    """入队/直连两面统一的仓内相对 posix 路径（绝对反斜杠 CLI 清单 → 仓相对）。

    P2-3/P2-4（红队 0922）：normpath 消 `..` 段；越仓路径返回空串（调用方跳过——
    git 本就拒收仓外路径，预检不读仓外文件）。
    """
    root = Path(str(gateway.project_root))
    p = Path(os.path.normpath(f))
    try:
        rel = p.relative_to(root)
    except ValueError:
        try:
            rel = Path(f).relative_to(root)
        except ValueError:
            return ""
    if any(part == ".." for part in rel.parts):
        return ""
    return rel.as_posix()


def _head_line_set(gateway: GitCommitGateway, rel: str) -> list[str]:
    """HEAD 版本行集（新文件=空集）；git 异常按空集处理（预检 fail-open，锁内兜底）。"""
    try:
        out = gateway.run_git(["git", "show", f"HEAD:{rel}"])
        if getattr(out, "returncode", 1) != 0:
            return []
        return (
            (out.stdout or b"").decode("utf-8", errors="replace").splitlines()
            if isinstance(out.stdout, (bytes, bytearray))
            else str(out.stdout or "").splitlines()
        )
    except Exception:  # noqa: BLE001 — 预检快败优化不因单文件 HEAD 读取失败而炸
        return []


def _check_inline_create_guard(gateway: GitCommitGateway, files: list[str], **kwargs: object) -> tuple[bool, str]:
    """CREATE-GUARD 入队面等价判定（D1，0921 死信 32 次+0091 磨 116 分钟的病灶前移）。

    新文件判定=files ∖ HEAD ls-tree（*.py / 非 rules *.y*ml / .md/.sh/.ps1/.mmd/.json，
    tests/ 豁免同锁内口径）；检测核心**原样复用** create_guard._check_creation_token +
    _check_field_header（不造第二检测器）。磁盘内容=快照内容（入队语义），与落地侧
    staged-diff 判定等价。
    """
    from zephyr.gov_enforcement.commit_gates.create_guard import (  # noqa: PLC0415
        _check_creation_token,
        _check_field_header,
    )
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import is_test_exempt  # noqa: PLC0415

    tracked = {os.path.normcase(t) for t in _head_tracked_relset(gateway)}
    root = Path(str(gateway.project_root))
    new_py: list[str] = []
    new_yaml: list[str] = []
    new_other: list[str] = []
    for f in files:
        rel = _rel_of(gateway, f)
        if not rel:
            continue
        # P2-2（红队 0922）：Windows 盘大小写不敏感——normcase 后比对防假红
        if os.path.normcase(rel) in tracked or is_test_exempt(rel):
            continue
        if not (root / rel).is_file():
            continue  # delete/缺失路径与 token 无关（deletes 通道另行处理）
        # 契约注记：_check_creation_token/_check_field_header 的路径口径=仓相对 posix
        # （锁内侧来源 git diff --name-only 即 rel）——绝对路径会永远对不上注册表索引。
        if rel.endswith(".py"):
            new_py.append(rel)
        elif rel.endswith(".yaml") and not rel.startswith(
            "docs/01_policies_and_standards/rules/"
        ):  # P2-5：对齐锁内口径（.yaml only）
            new_yaml.append(rel)
        elif rel.endswith((".md", ".sh", ".ps1", ".mmd", ".json")):
            new_other.append(rel)
    if not (new_py or new_yaml or new_other):
        return True, ""
    passed, detail = _check_creation_token(gateway, new_py, new_yaml, new_other)
    if not passed:
        return False, detail
    return _check_field_header(gateway, new_py)


def _check_inline_no_bare_sql(gateway: GitCommitGateway, files: list[str], **kwargs: object) -> tuple[bool, str]:
    """NO-BARE-SQL 入队面等价判定（D1，0921 死信 15 次）。

    增行=磁盘 vs HEAD 的 difflib opcode（精确 added 行）；SQL 识别正则**原样复用**
    bare_sql_gate._SQL_PATTERN；豁免口径（tests/、_archive、scripts/ch/）与锁内一致。
    """
    import difflib  # noqa: PLC0415

    from zephyr.gov_enforcement.commit_gates.bare_sql_gate import _SQL_PATTERN  # noqa: PLC0415
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import is_test_exempt  # noqa: PLC0415

    root = Path(str(gateway.project_root))
    violations: list[str] = []
    for f in files:
        rel = _rel_of(gateway, f)
        if not rel:
            continue
        norm = rel.replace("\\", "/")
        if not norm.endswith(".py") or is_test_exempt(norm):
            continue
        if "_archive" in norm or norm.startswith("scripts/ch/"):
            continue
        # 注意：tracked 文件不跳过——改动的 tracked 文件其"新增行"同样要检
        # （锁内 _get_added_lines 对 modify 同样提取增行；此处 difflib 等价）。
        p = root / rel
        if not p.is_file():
            continue
        disk_lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        head_lines = _head_line_set(gateway, rel)
        if len(disk_lines) > 20000:
            continue  # P1-2（红队 0922：10 万行实测 63s）超长文件跳过快段，锁内权威链兜底
        sm = difflib.SequenceMatcher(a=head_lines, b=disk_lines)  # 默认 autojunk 启发式防二次方退化
        added: list[str] = []
        for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
            if tag in ("insert", "replace"):
                added.extend(disk_lines[j1:j2])
        for line in added:
            if _SQL_PATTERN.search(line):
                violations.append(f"{norm}: {line.strip()[:120]}")
                break  # 每文件报首条（锁内权威链给全量，预检只定快败）
    if violations:
        return False, (
            "NO-BARE-SQL 预检（入队面等价判定）：新增行含裸 SQL 字面量（§5.160.2 SQL 集中化）\n  "
            + "\n  ".join(violations[:5])
        )
    return True, ""


_INLINE_PREFLIGHT_CHECKS.extend(
    [
        ("CREATE-GUARD", _check_inline_create_guard),
        ("NO-BARE-SQL", _check_inline_no_bare_sql),
    ]
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
    "REGISTRY-MASS-DELETION": (
        "注册表只应增长——检查是否误删条目；确属合法净删（去重/退役/账实修正）"
        "在 commit message 加标记 [allow-mass-deletion:<理由≥10字>]（预检已可读 message，随批永久留痕）"
    ),
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
    # ── D1 新增逃生旗提示（st-commitchain-20260922）──
    "RULING-REFERENCE": (
        "ruling_registry.yaml 补登对应 裁定#NNN 条目（同 commit 原子，RULE-RULING）"
        "或修正/移除引用；带字母后缀（#392-D）同样必须登记"
    ),
    "ARCH-REFERENCE": "architecture_issue_registry.yaml 补登 #ARCH-NNN 条目或修正引用（登记册禁凭空造册）",
    "EXEMPT-ZONE-FM": "豁免区文件（docs/_working 等）frontmatter 只带 ttl 禁 doc_type——按 gate 消息修正头",
    "CREATE-GUARD": (
        "新建资产先登记 token：python scripts/governance/d3_metadata/batch_creation_tokens.py "
        "--prefix <目录> --created-by <本会话> --capability <能力名>（.py 另需 14 字段头；token 批与内容同批或先行落地）"
    ),
    "NO-BARE-SQL": "SQL 提取到模块级常量或 TableRegistry/专用集中化文件；存量伪新增加行尾 # noqa: bare-sql <reason≥10字>",
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


def _write_audit(gateway: GitCommitGateway, record: dict) -> None:
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
    gateway: GitCommitGateway,
    files: list[str],
    session_id: str,
    skip_gate_ids: frozenset[str] | set[str] = frozenset(),
    *,
    specs: list[GateSpec] | None = None,
    audit_event: str = "direct",
    commit_message: str = "",
) -> CommitPreflightResult:
    """锁外预检白名单 gate（一过式收集，不短路）。

    Args:
        gateway: GitCommitGateway 实例（只读使用——run_git/注册表/会话态）。
        files: 本次 commit 文件清单（与 gw.commit 同口径）。
        session_id: 会话标识。
        skip_gate_ids: 逃生旗对应跳过的 gate 集（由调用方按 argparse 旗映射）。
        specs: 测试注入位（缺省=gateway._gate_registry.specs_sorted()）。
        audit_event: 审计事件标签（direct/enqueue）。
        commit_message: 本次提交信息（缺省空串）。标记豁免型 gate（如
            REGISTRY-MASS-DELETION 的 [allow-mass-deletion:]）以此为输入面——
            2026-09-18 治本：此前预检不传 message，带合法逃生标记的批次被预检
            假红硬拦，而锁内权威链/落地侧会放行（预检与权威判据错位）。

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
                result = spec.check(gateway, list(files), session_id=session_id, commit_message=commit_message)
                passed, detail = (
                    (result[0], result[1] if len(result) > 1 else "") if isinstance(result, tuple) else (True, "")
                )
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
        # D1 内联适配层（staged-diff 依赖型 T0 门禁的入队面等价判定；失败语义与 specs 同款）
        for gate_id, fn in _INLINE_PREFLIGHT_CHECKS:
            if gate_id in skip_gate_ids:
                continue
            try:
                passed, detail = fn(gateway, list(files), session_id=session_id, commit_message=commit_message)
                if not passed:
                    findings.append(
                        PreflightFinding(
                            gate_id=gate_id, detail=str(detail), escape_hint=_ESCAPE_HINTS.get(gate_id, "")
                        )
                    )
            except Exception:  # noqa: BLE001 — 设施异常降级不阻断（锁内权威链兜底）
                degraded.append(gate_id)
                logger.warning("preflight inline gate %s degraded（不阻断，锁内兜底）", gate_id, exc_info=True)
    except Exception:  # noqa: BLE001 — 预检整体异常=放行走锁内现行路径
        logger.warning("preflight 自身异常，降级放行（锁内权威链兜底）", exc_info=True)
        return CommitPreflightResult(
            findings=[], degraded=["__preflight__"], elapsed_ms=round((time.monotonic() - t0) * 1000, 1)
        )
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
