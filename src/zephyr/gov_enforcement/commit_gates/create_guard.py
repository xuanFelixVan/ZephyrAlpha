# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.create_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec), zephyr.governance.capability_lookup (REGISTRY_YAML, CapabilityLookup)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增 .py 文件无 creation_token 时阻断 commit（passed=False）；tests/ 豁免（测试非能力真源，真源：commit_gate_registry.is_test_exempt）；非 rules/ 新增 .yaml 无 creation_token 亦硬阻断（扩展 CREATE-GUARD 到 .yaml，防造第二配置真源，.yaml 是 YAML->DB 单向同步真源）；rules/ .yaml 不走 token 检查（已有命名检查 L232-278）；YAML 不可达时 fail-closed 阻断（registry 故障是环境异常，禁止放行以防删 registry 绕过 token 检查）；git diff 失败亦 fail-closed；token 匹配按相对路径精确比对（路径归一化为正斜杠）；rules/ 新增(A)+rename(R) .yaml 两类命名违规硬阻断（ARCH-037 DIM-5 commit-time 强制：①非trae命名 ②单段name，--no-verify 绕不过）；token 检测通过后追加 check_capability_duplicates 调用（ARCH-031 门禁缺口治本：L3 pre-commit hook 被 --no-verify 绕过->L2 create_guard 追加 basename 碰撞检测，含未注册 basename 碰撞 _check_unregistered_basename_collision，收窄 governance/ 前缀+排除 _archive/，CapabilityLookup 不可用时 fail-open 不阻断）；新建 .py 文件头部 30 行内 MUST 含 14 字段标注（ARCH-031 14字段治本：# [FIELD] value 格式，BLUEPRINT/MODULE/DOMAIN/DEPENDENCIES/CONSUMERS/STARTUP/MATURITY/INVARIANTS/MODIFY-GUARD/STABILITY/SAFETY/AI_AUTONOMY/ERROR_CONTRACT/TESTS，缺字段硬阻断）；codegen 文件豁免（含 BEGIN CODEGEN/BEGIN CODGEN 标记，字段由模板注入）；__init__.py 最低 3 字段（BLUEPRINT/MODULE/DOMAIN，包标记可省 CONSUMERS 等）；14字段规范真源在 AGENTS.md + governance/__init__.py docstring；governance/ 根禁止新增 .py 文件（ARCH-031 防复发2026-07-02：治本后仅保留 6 个高风险核心模块，2026-07-17 shim 消除 commit 213be2b5a3 删除 base/merkle_hourly/performance_attribution_report 后降至 6，新模块 MUST 放入子目录，path.count("/")==3 匹配 src/zephyr/governance/<name>.py 硬阻断）；新建 .py/.yaml 资产（非 tests/，own-scope=本提交文件面）token 条目缺 merge_evaluation 字段→warn+审计不阻断（裁定#375 内收判据门禁化首期 warn-only——硬阻断会把存量 token 全打红，留过渡窗由季度审计评估升级）；own 化 2026-09-23(st-gslim P2)：staged_new 获取后即按本 session 拆分，外来 staged warn+审计不阻断(_split_own_foreign；governance 根 R-rename 反绕过检测保持全暂存)；波13·包13.1（2026-09-26）新建 .py 查功能关键词：对每个新建 .py 取查询面（文件名 stem+模块 docstring 首段+顶层类/函数名）切探针，逐探针调既有 CapabilityLookup.find()，命中>0（canonical 指向本文件或同批新建者除外）⇒硬阻断，逃生标记 '# create-guard-not-dup: <一句话理由>' 按文件豁免，命中=0 ⇒ 放行且由 find() 既有审计通道 .runtime/lookup_audit/<sid>.jsonl 的 result_count=0 行做漂移日志（不新建日志文件）；find 故障 fail-closed；取代 L827-848 fail-open basename 尺的判重角色（后者降为冗余后备）与 capability_overlap_gate stage-1 文件名词元启发式（见其 docstring 注释）；同批 CLASS-UNIQUENESS git grep 批量化为每批一次 -E alternation 调用+Python 侧按类名归因（非 ASCII 类名回退逐名查询，判据与逐名版全等，100+样本重放见 docs/_working/three_piece_infra/piece1_gate/CASE.md）；裁定#456（2026-09-30）判重腿两档化：探针命中字段∈{capability_id,aliases,canonical_file}（标识符级）维持硬拦，仅命中 description（散文面）降为 warn（logger.warning+审计 .runtime/gate_audit/create_guard_keyword_dup_warn.jsonl，不阻断；处方=逃生标记或 python -m zephyr.library.lookup 正查），逃生标记/判死阈值语义零改动；S4-C（2026-09-30，手术簿 s4_c_p90_cache.md）进程级 lookup 单例：_build_capability_lookup 失效键=registry(normcase+mtime_ns+size)∪双根扫描概要(scan_root_summary)，未变复用常驻实例/变即重建，env ZEPHYR_CG_LOOKUP_SINGLETON=0 一键回退每次新构造，warm_capability_lookup_async 判重链后后台预热（daemon，异常全吞），判定语义零变化（检索面/#456 两档/fail-closed 出口不动，monkeypatch 注入缝保留）；S4-B（2026-09-30，手术簿 s4_b_token_sim.md）判重二阶段 token 相似度影子采集：触发面收敛=仅 #456 散文级 warn 命中条目，结构证据=新建 .py 与命中条目 canonical_file 的 AST 标识符有序序列（_TOKEN_SIM_TRUNC 截断护栏）经 _tokenize 切词后 diff_utils.similarity_ratio（stdlib 零新依赖），canonical 侧 (normcase,mtime_ns,size) 键缓存（失败不缓存），audit-only 只落 .runtime/gate_audit/create_guard_token_sim_shadow.jsonl（fail-open），would_block 恒 False/threshold 恒 None——不改任何判定，相似度分布一周后 Owner 门位定档
# [MODIFY-GUARD] gate_id="CREATE-GUARD"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML 读取/解析异常降级为 fail-closed 阻断（passed=False，detail 含修复指引：恢复 registry / 修正 YAML 语法）；git diff 异常降级为 fail-closed 阻断；对标 directory_contract_gate.py fail-closed 设计
# [TESTS] tests/governance/commit_gates/test_create_guard.py; tests/gov_enforcement/test_create_guard_lookup_singleton.py; tests/gov_enforcement/test_create_guard_token_sim_shadow.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本；裁定#375：新建资产 token 缺 merge_evaluation 字段 warn+审计不阻断，首期 warn-only）

检测 staged 新增 .py 文件与非 rules/ .yaml 文件是否在 capability_canonical_file_registry.yaml 的
creation_tokens 字段登记。无 token 的 .py / .yaml 文件 -> 硬阻断，提示"无 creation_token，
禁止造第二真源（trae_060 §2）"。有 token 的 .py / .yaml 文件 -> 放行。

.yaml token 扩展（2026-07-01，trae_060 §2 向内收治本）
-------------------------------------------------------
病根：.yaml 是配置真源（YAML->DB 单向同步硬约束），第二份 .yaml 配置真源
的危害比 .py 更隐蔽（同步漂移会污染 9 个 readonly DB 表）。rules/ 目录已有
命名检查（L232-278），但非 rules/ .yaml 无任何 commit-time 检测，--no-verify
绕过 pre-commit hooks 后可造第二配置真源。
治本：扩展现有 create_guard 检测范围到非 rules/ .yaml（不新增门禁，规避自指
递归——同 reconciler 审查标记检测先例）。新增 .yaml 文件无 creation_token
-> 硬阻断，复用 .py 的 token 索引（同一 registered_files 集合）。

裁定#375 内收判据门禁化（2026-09-20，立项判据从 SOP 义务升级为机器门禁）
----------------------------------------------------------------------
宪法 §4 "全资产净零" 内收判据铁律（同真源可派生→必并｜零触发零消费→退役｜
同域重复簇→收敛唯一｜跨域不同对象→不并）+ audit_prompts v5 §3.6 已把
"立项时必须做合并评估"定为审计义务——但义务只在事后审计兜底，立项时无机器强制。

治本：token 登记面（capability_canonical_file_registry.yaml creation_tokens
条目）加可选字段 ``merge_evaluation:``（值=四判据结论一句话）。真源=token
条目本身（不建新册——全资产净零）。本 gate 检测：新建 .py/.yaml 资产
（非 tests/，own-scope=本提交文件面）的 token 条目缺该字段 -> warn+审计
（.runtime/gate_audit/create_guard_merge_evaluation.jsonl），**不阻断**。

设计权衡（首期 warn-only）：
1. **不硬阻断**：存量 token 条目全部无此字段，硬阻断=全量打红（把存量债判给
   无辜提交人，违反 own-scope 问责原则）。留过渡窗，登记为待季度审计升级评估。
2. **登记通道**：``batch_creation_tokens.py --merge-evaluation <一句话>`` 登记
   时携带；存量条目事后手工补字段即消除 warn。
3. **扩展现有 gate 而非新 gate**：复用已加载的 registry 与 own-scope 过滤面
   （净零申报：无新册无新规则文件，行为变更登记进 gate_registry.yaml）。

元问题3治本扩展（2026-06-30，AD-GOV-001 收敛约束技术强制）
------------------------------------------------------------
扩展检测范围：若 commit 包含 ``src/zephyr/governance/audit/reconciliation_registry.py``，
用 AST 对比 staged 与 HEAD 版本的 ``make_*_reconciler`` 函数集，新增函数需在
def 前 5 行内添加 ``# trae_060-reviewed: <审查结论>`` 标记，否则硬阻断。

病根：AD-GOV-001 约束"新增 reconciler 前 MUST 过 trae_060 §4 元问题审查"是
君子协定，无技术强制，新 AI 可直接造新 reconciler 绕过审查。
递归陷阱：若新增门禁强制此审查，门禁本身也是"新增"，需过 §4 审查，无限递归。
治本：扩展已有 create_guard 检测范围（不新增门禁，规避自指递归）。

ARCH-037 治本扩展（2026-07-01，DIM-5 commit-time 强制）
-------------------------------------------------------
扩展检测范围：若 commit 含 ``docs/01_policies_and_standards/rules/`` 下新增(A)
或 rename(R) 的 ``.yaml`` 文件，检测两类命名违规 -> 硬阻断：
  ① 非 trae 命名（不匹配 trae_NNN_ 前缀，如 foo.yaml）——红蓝漏洞1修复
  ② 单段 name（匹配 trae_NNN_ 但 name 段无下划线，如 trae_999_test.yaml）

病根：DIM-5 检测能力已就位（validate_rule_frontmatter.py pre-commit hook），但
``git commit --no-verify`` 绕过所有 pre-commit hooks，DIM-5 沦为君子协定，无技术
强制。治本：扩展已有 create_guard（GitCommitGateway 注册 gate，``--no-verify``
绕不过），复用 DIM-5 正则逻辑（commit-time 强制层，DIM-5 真源仍在
validate_rule_frontmatter.py，两处正则保持一致）。

rename 检测（红蓝漏洞2修复）：--diff-filter=R 取新文件名检测，防 rename+--no-verify
绕过（rename 不是新增，--diff-filter=A 漏检）。

同 line 23-32 reconciler 审查标记检测先例：扩展现有 gate 检测范围（不新增门禁，
规避自指递归 + AD-GOV-001 收敛约束）。

病根（"造第二真源"根因）
-------------------------
AI 新建 .py 文件时可能复制已有实现（违反 trae_060 §2 唯一真源原则）。现有缓解
（GATE-SSOT module_path 冲突检测 + GATE-SSOT-SINGLESOURCE 文件名检测 +
capability_overlap_gate warn-only）均在 commit 时检测，此时文件已写完——
检测滞后于创建。本 gate 治本：强制 AI 在创建新 .py 文件前先在
creation_tokens 字段登记 token（声明创建意图 + 关联 capability），
未登记则 commit 硬阻断。token 登记是"创建前"动作（先登记再写文件），
把检测点从"commit 时"前移到"创建前"。

设计权衡
--------
1. **硬阻断而非 warn-only**：capability_overlap_gate 是 warn-only（文件名 token
   匹配是启发式，可能误报）；本 gate 用精确路径比对（creation_tokens[].file 与
   staged 新增文件路径精确匹配），无误报风险，故硬阻断。
2. **tests/ 豁免**：测试文件不是能力真源（不提供 canonical 实现），对标
   capability_overlap_gate 的 tests/ 豁免设计。真源已收敛到
   ``commit_gate_registry.is_test_exempt``（治本2，消除两 gate 实现不一致——
   create_guard 先归一再比对、capability_overlap_gate 未归一化导致 Windows latent bug）。
   包含 tests/ 会要求每个测试文件登记 token，过度 disruptive 且无 SSoT 收益。
3. **fail-closed（YAML 不可达，治本1 2026-06-30）**：YAML 缺失/解析失败/非 dict
   时阻断——registry 故障是环境异常，fail-open 会被"删 registry 绕过 token 检查"
   利用（红蓝攻击向量）。对标 directory_contract_gate.py fail-closed 设计。
   配套治本1②：registry 入 validate_rules_integrity.RULES_MANIFEST，防裸 commit 删 registry
   （C 层 MISSING+critical 阻断，防 DoS）。YAML 可达但文件无 token 时才走 token 硬阻断。
4. **priority=60**：在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行
   ——先过搭便车/claim 检查（session 级约束），再过 creation_token 检查（文件级
   约束），最后 warn-only 提示。

裁定#216 Tier1 P1 重构（2026-07-15，Extract Method）
----------------------------------------------------
原 _check 闭包 475 行 McCabe=101（11 个独立检测块串联，P1 gate-closure multi-check 模式）。
治本：Extract Method 提取为 9 个模块级 helper（均 McCabe≤15），_check 简化为
~30 行 pipeline（McCabe≈14）。行为等价契约：每个 helper 返回 (True, "")=放行/继续，
(False, msg)=硬阻断。关键行为保持：
  - governance/ 根检测用 UNFILTERED new_py_files（commit_files_rel 过滤前）
  - 两处 early return（过滤前/过滤后均空时 return True）
  - field_header 内部 `if not new_py_files: return True, ""`（无 .py 时跳过 trae_047 读取）

creation_tokens 字段结构（capability_canonical_file_registry.yaml 顶层字段）::

    creation_tokens:
      - file: "src/zephyr/gov_enforcement/commit_gates/create_guard.py"
        token: "auto-create-guard-20260630"
        created_by: "session-trae-redteam-deadly-5"
        capability: "create_guard"

Usage::

    from zephyr.gov_enforcement.commit_gates.create_guard import make_create_guard

    registry.register(make_create_guard())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/c/create_guard.yaml
"""

from __future__ import annotations

import ast
import json
import logging
import os
import re
import threading
import time
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml

from zephyr.gov_enforcement.commit_gates._capability_registry_io import (
    _PARSE_CACHE as _SHARED_PARSE_CACHE,  # noqa: F401 — 别名再导出（历史引用兼容）
)
from zephyr.gov_enforcement.commit_gates._capability_registry_io import (
    cache_key_of,
    parse_capability_registry_cached,
    reset_parse_cache,
)
from zephyr.gov_enforcement.commit_gates._diff_helpers import _split_own_foreign
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt
from zephyr.governance.rule_patterns import RULE_NAME_RE
from zephyr.shared.utils.diff_utils import similarity_ratio
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["make_create_guard"]

# === 裁定#216 Tier1 P1 Extract Method 重构（2026-07-15） ===
# 模块级常量（原 _check 闭包内局部常量，提取为模块级以消除重复定义）
_RECONCILER_REGISTRY_REL = "src/zephyr/governance/audit/reconciliation_registry.py"
_TRAEO60_MARKER = "trae_060-reviewed"
_RULES_DIR_PREFIX = "docs/01_policies_and_standards/rules/"
_GOVERNANCE_ROOT_PREFIX = "src/zephyr/governance/"
_ALIAS_MARKER = "class-name-alias"
_OTHER_FORMAT_EXTENSIONS = (".md", ".sh", ".ps1", ".mmd", ".json")

# === 波13·包13.1 CREATE-GUARD 查功能关键词（2026-09-26） ===
# 逃生标记确切字面量（声明"确非重复"才放行，按文件豁免；spec 真源=本常量+案卷）：
#     # create-guard-not-dup: <一句话理由>
# （行首 #、冒号后必须跟非空理由；作用域=仅该新建 .py 自身；grep 面=git grep -rn "create-guard-not-dup"）
_KEYWORD_DUP_MARKER = "create-guard-not-dup"
_KEYWORD_DUP_MARKER_RE = re.compile(rf"^#\s*{re.escape(_KEYWORD_DUP_MARKER)}:\s*(\S.*)$", re.MULTILINE)
# 每文件探针上限（查询面=stem+docstring 首段+顶层类/函数名；上限防大 docstring 爆炸——
# 每次 find() 均落一条 lookup_audit 且有图书馆查重探针，实测 find 首轮开销不可忽略）
_MAX_KEYWORD_PROBES = 8
# === S4-B 判重二阶段 token 相似度影子采集（2026-09-30，手术簿 s4_b_token_sim.md） ===
# 影子账本（audit-only，零判据变化；相似度分布攒一周后 Owner 门位定档）
_TOKEN_SIM_SHADOW_AUDIT_REL = (".runtime", "gate_audit", "create_guard_token_sim_shadow.jsonl")
# 大文件护栏：AST 标识符有序序列截断常量（矩阵 9——超限截断后仍可比，不崩不扫全文）
_TOKEN_SIM_TRUNC = 10_000
# canonical 侧 token 串进程内缓存：键=(normcase 路径, mtime_ns, size)（同款键型见 :734）
_CANON_TOKEN_SIM_CACHE: dict[tuple[str, int, int], str] = {}
_CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]{3,}")
_ASCII_DOC_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")
# bigram 词对噪声门：docstring 通用词不成"功能关键词"（仅作用于④bigram 探针，
# 不作用于 stem/标识符探针——后者本身即功能语义面）
_BIGRAM_STOPWORDS = frozenset(
    {
        "this",
        "that",
        "with",
        "from",
        "these",
        "those",
        "will",
        "would",
        "could",
        "have",
        "has",
        "had",
        "been",
        "being",
        "into",
        "over",
        "under",
        "about",
        "above",
        "they",
        "them",
        "their",
        "there",
        "then",
        "than",
        "when",
        "where",
        "which",
        "what",
        "while",
        "because",
        "should",
        "must",
        "not",
        "only",
        "such",
        "also",
        "each",
        "other",
        "others",
        "either",
        "neither",
        "every",
    }
)

# === B1 registry 撕裂读重试（2026-09-16） ===
# 病根：并发会话写 capability registry 时存在瞬态撕裂读（读半个写入窗口），
# yaml.safe_load 单次失败即 fail-closed 会把"设施瞬态故障"误报成"违规阻断"。
_REGISTRY_PARSE_RETRIES = 3
# T8 簇1 共册解析（st-commitspeed-pkg8-20260925）：缓存下沉共享模块 _capability_registry_io
# （六台同读 2.7MB 册收敛一次 yaml.safe_load；键含 normcase 路径+mtime_ns+size，写后失效）。
# 本名保留为共享缓存同一容器的别名——历史测试/外部引用兼容，删名前先 grep 消费方。
_REGISTRY_CACHE: dict = _SHARED_PARSE_CACHE
_REGISTRY_RETRY_INTERVAL_S = 0.3
# 解析失败审计路径（相对 project_root；.runtime/audit/ 是既有审计 jsonl 约定区）
_PARSE_FAIL_AUDIT_REL = (".runtime", "audit", "create_guard_parse_fail.jsonl")

# === 裁定#375 内收判据门禁化（2026-09-20） ===
# merge_evaluation = token 条目上的合并评估声明字段（四判据结论一句话）；
# 缺失审计路径（相对 project_root；.runtime/gate_audit/ 是 gate 家族审计约定区，
# 对标 _diff_helpers._audit_foreign_staged）
_MERGE_EVAL_FIELD = "merge_evaluation"
_MERGE_EVAL_AUDIT_REL = (".runtime", "gate_audit", "create_guard_merge_evaluation.jsonl")

# 判重腿散文级 warn 审计路径（裁定#456 两档化；同族通道对标 _MERGE_EVAL_AUDIT_REL）
_KEYWORD_DUP_WARN_AUDIT_REL = (".runtime", "gate_audit", "create_guard_keyword_dup_warn.jsonl")


def _read_registry_text(registry_path) -> str:
    """读取 registry 文本（读取单点收敛——测试 monkeypatch 目标）。

    独立成单点的目的：撕裂读重试计数与"先坏后好"模拟都只需 patch 本函数，
    不触碰磁盘真源（测试隔离铁律）。
    """
    return registry_path.read_text(encoding="utf-8")


def _audit_registry_parse_fail(project_root, registry_path, reason: str) -> None:
    """registry 解析失败审计（jsonl append 到 .runtime/audit/create_guard_parse_fail.jsonl）。

    - 时间戳用 now_utc（RULE-SCHEMA-TZ：禁 datetime.now()/time.time()）。
    - reason 截前 200 字（防长 traceback 撑爆审计文件）。
    - 写失败 fail-open：审计是观测件，故障不阻断主流程（只 warning）。
    """
    try:
        audit_path = project_root.joinpath(*_PARSE_FAIL_AUDIT_REL)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": now_utc().isoformat(),
            "event": "registry_parse_fail",
            "path": str(registry_path),
            "reason": str(reason)[:200],
        }
        with audit_path.open("a", encoding="utf-8") as _f:
            _f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as _e:  # noqa: BLE001 — 审计写失败 fail-open
        logger.warning("CREATE-GUARD: registry 解析失败审计写入失败: %s", _e, exc_info=True)


def _compute_commit_files_rel(gateway, files: list[str]) -> set[str]:
    """计算 commit 文件相对路径集合（reconciler 检测 + token 检测复用）。"""
    commit_files_rel: set[str] = set()
    for f in files:
        try:
            rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
            commit_files_rel.add(rel)
        except (ValueError, OSError):
            continue
    return commit_files_rel


def _extract_make_reconcilers(tree) -> set[str]:
    """从 AST 提取 make_*_reconciler 函数名集合。"""
    if tree is None:
        return set()
    return {
        n.name
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name.startswith("make_") and n.name.endswith("_reconciler")
    }


def _find_unmarked_reconcilers(staged_tree, staged_src: str, new_reconcilers: set[str]) -> list[str]:
    """在 staged AST 中查找未标记 trae_060 的新增 reconciler 函数名。

    检查 def 行前 5 行（含 decorator/注释区）是否有 '# trae_060-reviewed' 标记。
    """
    staged_lines = staged_src.splitlines()
    unmarked = []
    for n in ast.walk(staged_tree):
        if not (isinstance(n, ast.FunctionDef) and n.name in new_reconcilers):
            continue
        has_marker = False
        for i in range(max(0, n.lineno - 6), n.lineno - 1):
            if _TRAEO60_MARKER in staged_lines[i]:
                has_marker = True
                break
        if not has_marker:
            unmarked.append(n.name)
    return unmarked


def _resolve_main_branch_ref(gateway) -> str:
    """解析主分支名（worktree 模式下 HEAD 可能过时，需对比主分支）。

    依次尝试 dev / main / master，返回第一个存在的分支名。
    全部不存在时返回 "HEAD"（回退到原行为）。
    """
    for _branch in ("dev", "main", "master"):
        try:
            _r = gateway.run_git(["git", "rev-parse", "--verify", f"refs/heads/{_branch}"])
            if _r is not None and _r.returncode == 0:
                return _branch
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            continue
    return "HEAD"


def _check_reconciler_marker(gateway, commit_files_rel: set[str]) -> tuple[bool, str]:
    """元问题3治本：新增 make_*_reconciler 需 trae_060 §4 审查标记。

    放在最前：reconciliation_registry.py 是已存在文件，不在 new_py_files 里，
    若等 new_py_files 过滤后检测，会被 "not new_py_files: return True" 提前返回跳过。

    worktree 模式修复（#ARCH-CREATE-GUARD-STALE-HEAD-001）：
    worktree HEAD 可能过时（并发 session 已 merge 新 reconciler 到 dev），
    用 HEAD 对比会把并发 session 的 reconciler 误判为"新增"。
    治本：对比主分支（dev/main/master）而非 worktree HEAD，
    使已 merge 到主分支的 reconciler 不被误判为新增。
    """
    if _RECONCILER_REGISTRY_REL not in commit_files_rel:
        return True, ""

    # 主分支 ref（worktree 模式下比 HEAD 更新，避免误判并发 session 的 reconciler）
    _main_ref = _resolve_main_branch_ref(gateway)

    try:
        staged_res = gateway.run_git(["git", "show", f":{_RECONCILER_REGISTRY_REL}"])
        head_res = gateway.run_git(["git", "show", f"{_main_ref}:{_RECONCILER_REGISTRY_REL}"])
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        staged_res = head_res = None  # fail-open：git 故障时不阻断（避免误伤正常 commit）

    if staged_res is None or staged_res.returncode != 0:
        return True, ""

    staged_src = staged_res.stdout
    head_src = head_res.stdout if (head_res is not None and head_res.returncode == 0) else ""
    try:
        staged_tree = ast.parse(staged_src)
        head_tree = ast.parse(head_src) if head_src else None
    except SyntaxError:
        return True, ""  # 语法错误由其他 gate 检测，此处 fail-open

    staged_makes = _extract_make_reconcilers(staged_tree)
    head_makes = _extract_make_reconcilers(head_tree)
    new_reconcilers = staged_makes - head_makes
    if not new_reconcilers:
        return True, ""

    unmarked = _find_unmarked_reconcilers(staged_tree, staged_src, new_reconcilers)

    if unmarked:
        return False, (
            f"新增 reconciler 未过 trae_060 §4 元问题审查: {sorted(unmarked)}. "
            f"AD-GOV-001 收敛约束：新增 make_*_reconciler 前 MUST 过 trae_060 §4 审查"
            f"（该存在/能否合并进已有/治本），并在函数定义前添加 "
            f"'# {_TRAEO60_MARKER}: <审查结论>' 标记。"
            f"修复：在 reconciliation_registry.py 新增 make_*_reconciler 函数定义前"
            f"添加注释 '# {_TRAEO60_MARKER}: <审查结论>'，或合并进已有 reconciler。"
        )
    return True, ""


def _get_staged_new_files(gateway) -> tuple[list[str] | None, str]:
    """获取 staged 新增文件列表（--diff-filter=A）。

    Returns:
        (staged_new, "") 成功； (None, detail) fail-closed 阻断。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            return None, (
                f"CREATE-GUARD fail-closed: git diff 失败(rc={diff_result.returncode})，"
                f"无法确定 staged 新增文件。禁止放行——检测器失效时漏放未登记 .py。"
                f"修复：检查 git 状态（git status）确认仓库可用后重试。"
            )
        return diff_result.stdout.strip().splitlines(), ""
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None, (
            f"CREATE-GUARD fail-closed: git diff 异常({type(e).__name__}: {e})，"
            f"无法确定 staged 新增文件。禁止放行——检测器失效时漏放未登记 .py。"
            f"修复：检查 git 仓库状态后重试。"
        )


def _collect_renamed_rule_files(gateway, commit_files_rel: set[str]) -> list[str]:
    """收集 rules/ 下 rename(R) 的 .yaml 文件（检测 rename 后的新文件名）。

    fail-open：git diff 故障不阻断（新增检测已覆盖主要场景）。
    """
    renamed: list[str] = []
    try:
        rename_result = gateway.run_git(["git", "diff", "--cached", "--name-status", "--diff-filter=R"])
        if rename_result.returncode == 0:
            for line in rename_result.stdout.strip().splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    new_path = parts[-1].replace("\\", "/")
                    if (
                        new_path.startswith(_RULES_DIR_PREFIX)
                        and new_path.endswith(".yaml")
                        and new_path in commit_files_rel
                    ):
                        renamed.append(new_path)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass  # fail-open：rename 检测故障不阻断
    return renamed


def _check_rule_yaml_naming(gateway, staged_new: list[str], commit_files_rel: set[str]) -> tuple[bool, str]:
    """ARCH-037 治本：rules/ .yaml 命名格式硬阻断（非 trae 命名 / 单段 name）。

    放在 new_py_files 过滤前：若 commit 只含 .yaml 无 .py，new_py_files 为空
    会提前 return True 跳过本检测，故须在 return 前完成 .yaml 命名检测。
    """
    new_rule_files: list[str] = []
    for f in staged_new:
        f_norm = f.replace("\\", "/")
        if f_norm.startswith(_RULES_DIR_PREFIX) and f_norm.endswith(".yaml") and f_norm in commit_files_rel:
            new_rule_files.append(f_norm)

    renamed_rule_files = _collect_renamed_rule_files(gateway, commit_files_rel)

    bad_rule_names = []
    for f in new_rule_files + renamed_rule_files:
        basename = f.rsplit("/", 1)[-1]
        m = RULE_NAME_RE.match(basename)
        if not m:
            # ① 非 trae 命名（不匹配 trae_\d+_<xxx>.yaml）
            bad_rule_names.append((f, basename, "非trae命名"))
        elif "_" not in m.group(1):
            # ② 单段 name（匹配 trae_NNN_ 但缺主题前缀）
            bad_rule_names.append((f, m.group(1), "单段name缺主题前缀"))
    if bad_rule_names:
        detail = "; ".join(f"{f}（{reason}='{seg}'）" for f, seg, reason in bad_rule_names)
        return False, (
            f"rules/ .yaml 文件命名违规(ARCH-037 DIM-5硬阻断): {detail}. "
            f"命名约定: trae_NNN_<主题>_<描述>.yaml（见 trae_028 GOV-DOC-003）。"
            f"--no-verify 绕不过本检测（create_guard 是 GitCommitGateway 注册 gate，非 pre-commit hook）。"
            f"修复：用 `python scripts/scaffold.py rule <主题_描述>` 创建（RULE-TWO 强制入口），"
            f"或手工重命名为 trae_NNN_<主题>_<描述>.yaml。"
        )
    return True, ""


def _filter_new_py_and_yaml(staged_new: list[str]) -> tuple[list[str], list[str]]:
    """过滤 staged 新增文件为 (new_py_files, new_yaml_files)。

    - new_py_files: .py 文件，排除 tests/ 豁免（真源：commit_gate_registry.is_test_exempt）
    - new_yaml_files: .yaml 文件，排除 tests/ 豁免，排除 rules/ 目录（rules/ 已有命名检查）
    """
    new_py_files = [f.replace("\\", "/") for f in staged_new if f.endswith(".py") and not is_test_exempt(f)]
    new_yaml_files = [
        f.replace("\\", "/")
        for f in staged_new
        if f.endswith(".yaml") and not is_test_exempt(f) and not f.replace("\\", "/").startswith(_RULES_DIR_PREFIX)
    ]
    return new_py_files, new_yaml_files


def _filter_new_other_formats(staged_new: list[str]) -> list[str]:
    """过滤 .md/.sh/.ps1/.mmd/.json 格式（阶段 2，ARCH-TTL-DOC-001 全 7 格式覆盖）。"""
    return [
        f.replace("\\", "/")
        for f in staged_new
        if any(f.endswith(ext) for ext in _OTHER_FORMAT_EXTENSIONS) and not is_test_exempt(f)
    ]


def _check_governance_root(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-031 防复发：禁止 governance/ 根新增/rename .py 文件。

    NOTE: 使用 UNFILTERED new_py_files（commit_files_rel 过滤前），因为 rename
    检测 MUST 在 early return 前完成。
    """
    _gov_root_new = [f for f in new_py_files if f.startswith(_GOVERNANCE_ROOT_PREFIX) and f.count("/") == 3]
    if _gov_root_new:
        return False, (
            f"ARCH-031 防复发: 禁止在 governance/ 根新增 .py 文件: {_gov_root_new}. "
            f"governance/ 根仅保留高风险核心模块（以磁盘现有文件为准，"
            f"当前为 __init__/capability_lookup/depgraph_schema/evidence_pack/"
            f"integrity/rule_patterns；清单随治本进化，不在此硬编码完整列表避免过期）。"
            f"新模块 MUST 放入对应功能子目录（如 audit/ persistence/ 等）。"
            f"修复：将文件移动到 src/zephyr/governance/<subdir>/ 下。"
        )
    # 检测②: rename(R) .py 到 governance/ 根（防 git mv 绕过 --diff-filter=A 漏检）
    try:
        _rename_result = gateway.run_git(["git", "diff", "--cached", "--name-status", "--diff-filter=R"])
        if _rename_result.returncode == 0:
            _gov_root_renamed = []
            for line in _rename_result.stdout.strip().splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    _new_path = parts[2].replace("\\", "/")
                    if (
                        _new_path.startswith(_GOVERNANCE_ROOT_PREFIX)
                        and _new_path.count("/") == 3
                        and _new_path.endswith(".py")
                    ):
                        _gov_root_renamed.append(_new_path)
            if _gov_root_renamed:
                return False, (
                    f"ARCH-031 防复发: 禁止 rename 到 governance/ 根 .py 文件: "
                    f"{_gov_root_renamed}. 新模块 MUST 放入对应功能子目录。"
                    f"修复：将文件移动到 src/zephyr/governance/<subdir>/ 下。"
                )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "CREATE-GUARD: ARCH-031 rename 检测 git diff 失败: %s",
            e,
            exc_info=True,
        )
        # fail-open: git diff 失败不阻断 rename 检测（下游 gate 仍检测新增文件）
    return True, ""


def _chunk_class_names(names: list[str], max_pattern_len: int = 6000) -> list[list[str]]:
    """把类名列表切成若干批，使 alternation 正则长度 ≤max_pattern_len。

    Windows CreateProcess 命令行硬上限 32767 字符——一次 commit 千级 class 时单条
    alternation 会爆；切批后仍是"每批一次 grep"（成本 O(批数) ≪ O(类名数)）。
    各批名字互斥，归因结果直接合并，判据与逐名版全等。
    """
    chunks: list[list[str]] = []
    cur: list[str] = []
    cur_len = len("^class ()\\b")
    for n in names:
        if cur and cur_len + len(n) + 1 > max_pattern_len:
            chunks.append(cur)
            cur, cur_len = [], len("^class ()\\b")
        cur.append(n)
        cur_len += len(n) + 1
    if cur:
        chunks.append(cur)
    return chunks


def _attribute_class_grep_lines(grep_stdout: str, names: list[str]) -> dict[str, list[str]]:
    """把 `git grep -n -E "^class (A|B|...)\\b"` 的行级输出归因回类名→文件清单（纯函数）。

    波13·包13.1 L527 批量化：原版对每个类名各跑一次全树 `git grep -l`（成本源），
    批量为每批一次 `-n` alternation 调用后，本函数按行内容用与 grep 等价的
    `^class NAME\b` 逐名归因，产出与逐名 `-l` 全等的 {类名: [文件…]}（文件顺序=
    git grep 的树序分组，逐名去重）。行格式 `path:lineno:content` 按前两个冒号切分。
    """
    compiled = {n: re.compile(r"^class " + re.escape(n) + r"\b") for n in names}
    result: dict[str, list[str]] = {n: [] for n in names}
    for line in grep_stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        path = parts[0].replace("\\", "/")
        content = parts[2]
        for name, pat in compiled.items():
            if pat.search(content):
                files = result[name]
                if not files or files[-1] != path:
                    files.append(path)
    return result


def _check_class_uniqueness(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-034 P3 遗留2治本：类名跨模块唯一性检测。

    豁免：class 定义前3行内有 '# class-name-alias: <理由>' 标记（合法 re-export 场景）。
    fail-closed：git grep 故障（异常）时阻断（防漏放同名 class）。
    波13·包13.1 L527 成本面批量化：ASCII 类名一批一次 `git grep -n -E
    "^(class (A|B|C))\\b"`（原为每新文件每 class 一次全树 grep，实测 1519 次/19186s
    的成本源），行级输出经 `_attribute_class_grep_lines` 按类名归因；非 ASCII 类名
    回退逐名 `git grep -l`（POSIX \\b 与 Python \\b 对非 ASCII 语义可能分叉，回退
    保证判据与逐名版全等）。违规组装顺序与消息格式与逐名版一致；
    等价性由 100+ 真实样本重放自证（CASE 见 three_piece_infra/piece1_gate/CASE.md）。
    """
    file_classes: list[tuple[str, list[str]]] = []
    all_names: list[str] = []
    for _py_file in new_py_files:
        _abs_path = str(gateway.project_root / _py_file)
        try:
            with open(_abs_path, encoding="utf-8") as _f:
                _src = _f.read()
            _tree = ast.parse(_src)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            continue  # 语法错误由其他 gate 检测，此处 fail-open
        _lines = _src.splitlines()
        _names: list[str] = []
        for _node in ast.walk(_tree):
            if not isinstance(_node, ast.ClassDef):
                continue
            # 检查豁免标记（def 行前3行内）
            _has_marker = False
            for _i in range(max(0, _node.lineno - 4), _node.lineno - 1):
                if _i < len(_lines) and _ALIAS_MARKER in _lines[_i]:
                    _has_marker = True
                    break
            if _has_marker:
                continue
            _names.append(_node.name)
        if _names:
            file_classes.append((_py_file, _names))
            all_names.extend(_names)
    if not all_names:
        return True, ""

    name_files: dict[str, list[str]] = {}
    ascii_names = [n for n in dict.fromkeys(all_names) if n.isascii()]
    non_ascii_names = [n for n in dict.fromkeys(all_names) if not n.isascii()]

    # 批量路径：每批一次 -n alternation grep（批切防命令行上限；ARCH-034 遗留3治本：
    # 故障 fail-closed 语义不变）
    if ascii_names:
        for _chunk in _chunk_class_names(ascii_names):
            _pattern = "^class (" + "|".join(_chunk) + ")\\b"
            try:
                _grep_res = gateway.run_git(["git", "grep", "-n", "-E", _pattern, "--", "src/zephyr/"])
                if _grep_res.returncode == 0:
                    name_files.update(_attribute_class_grep_lines(_grep_res.stdout, _chunk))
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                _shown = ", ".join(_chunk[:5]) + ("..." if len(_chunk) > 5 else "")
                return False, (
                    f"CREATE-GUARD CLASS-UNIQUENESS fail-closed: git grep 异常"
                    f"({type(e).__name__}: {e})，无法检测 class '{_shown}' 跨模块冲突。"
                    f"禁止放行——检测器失效时漏放同名 class（AI 开发幻觉温床）。"
                    f"修复：检查 git 状态（git status）确认仓库可用后重试。"
                )

    # 回退路径：非 ASCII 类名逐名 -l（与原实现同命令同语义）
    for _node_name in non_ascii_names:
        try:
            _grep_res = gateway.run_git(["git", "grep", "-l", f"^class {_node_name}\\b", "--", "src/zephyr/"])
            if _grep_res.returncode == 0:
                name_files[_node_name] = [
                    f.replace("\\", "/") for f in _grep_res.stdout.strip().splitlines() if f.strip()
                ]
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False, (
                f"CREATE-GUARD CLASS-UNIQUENESS fail-closed: git grep 异常"
                f"({type(e).__name__}: {e})，无法检测 class '{_node_name}' 跨模块冲突。"
                f"禁止放行——检测器失效时漏放同名 class（AI 开发幻觉温床）。"
                f"修复：检查 git 状态（git status）确认仓库可用后重试。"
            )

    # 违规组装（文件序→类名序；existing 排除自身——与逐名版逐字一致）
    _class_violations = []
    for _py_file, _names in file_classes:
        for _node_name in _names:
            _existing = [f for f in name_files.get(_node_name, []) if f != _py_file]
            if _existing:
                _class_violations.append((_py_file, _node_name, _existing))
    if _class_violations:
        _detail = "; ".join(f"{f} 定义 class {name} 与已有 {existing} 同名" for f, name, existing in _class_violations)
        return False, (
            f"类名跨模块冲突(ARCH-034 CLASS-UNIQUENESS): {_detail}. "
            f"同名不同义是 AI 开发幻觉温床（后导入覆盖前导入，不报错）。"
            f"修复：①改名区分（如 Managed* 前缀）②若是合法 re-export，"
            f"在 class 定义前加 '# class-name-alias: <理由>' 标记豁免。"
        )
    return True, ""


def _load_capability_registry(gateway) -> tuple[dict | None, str]:
    """加载 capability registry（fail-closed）。返回 (data, error_detail)。

    B1 撕裂读重试（2026-09-16）：并发写窗口存在瞬态撕裂读，yaml.safe_load 包
    3 次重试（0.3s 退避）。重试耗尽仍 fail-closed（不变量不动——防删 registry
    绕过 token 检查），但消息区分「设施故障（非违规）」并落审计留痕。

    裁定#480 手术③同型治本（时序倒置）：registry 盘面读取先经 anchor_main_root
    锚主仓根——serializer 落地链（专用 worktree reset 到 dev 基底）与 session
    worktree 内，project_root 盘面是基底/陈旧版，会话入队前在主区登记的
    creation_token 不在 worktree 盘面上 → "登记完即可提交"被破坏成"须先行批"
    （q-...-0013 死信同族）。主区盘面才是登记完成的即时真源（与
    approval_resolver._registry_path #ARCH-324 先例同款锚定）；主区不可达时
    逐级回退 project_root 盘面 → REGISTRY_YAML，行为面只宽不窄。
    """
    from zephyr.governance.capability_lookup import REGISTRY_YAML
    from zephyr.shared.io.paths import anchor_main_root

    _rel_parts = (
        "docs",
        "01_policies_and_standards",
        "_registry",
        "catalogs",
        "capability_canonical_file_registry.yaml",
    )
    _registry_yaml = anchor_main_root(Path(gateway.project_root)).joinpath(*_rel_parts)
    if not _registry_yaml.exists():
        _registry_yaml = Path(gateway.project_root).joinpath(*_rel_parts)  # 旧路径（worktree 自带册时兼容）
    if not _registry_yaml.exists():
        _registry_yaml = REGISTRY_YAML  # 回退到全局真源

    if not _registry_yaml.exists():
        return None, (
            f"CREATE-GUARD fail-closed: capability registry 不可达（文件缺失: {_registry_yaml}）。"
            f"禁止放行——防删 registry 绕过 creation_token 检查。"
            f"修复：git checkout HEAD -- {_registry_yaml} 恢复 registry 后重试。"
        )

    # T8 簇1 共册解析（st-commitspeed-pkg8-20260925）：读入+解析下沉共享缓存
    # （ssot_redefinition/capability_overlap 同读此册，全链一次 yaml.safe_load）。
    # 键=normcase 路径+mtime_ns+size，写后失效；解析失败不缓存。判据零变化。
    data, parse_err = parse_capability_registry_cached(_registry_yaml, reader=_read_registry_text)
    if parse_err is None and data is not None:
        return data, ""

    # B1 撕裂读重试（语义保留）：首次解析失败后最多再试 _REGISTRY_PARSE_RETRIES-1 次
    # （总尝试次数与原版 3 次一致），0.3s 退避；失败不缓存，重试真读。
    parsed = False
    last_err: Exception | None = parse_err
    for _attempt in range(_REGISTRY_PARSE_RETRIES - 1):
        try:
            data = yaml.safe_load(_read_registry_text(_registry_yaml))
            parsed = True
            break
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            last_err = e
            if _attempt < _REGISTRY_PARSE_RETRIES - 2:
                time.sleep(_REGISTRY_RETRY_INTERVAL_S)  # noqa: m10-time-trigger — 注册表撕裂读失败重试的指数退避等待，错误恢复路径非周期轮询
    if parsed and data is not None:
        try:
            reset_parse_cache(cache_key_of(_registry_yaml), data=data)
        except OSError:
            logger.debug("registry 缓存回填 stat 失败（下次调用重解析）", exc_info=True)
        return data, ""
    if not parsed:
        _audit_registry_parse_fail(gateway.project_root, _registry_yaml, f"{type(last_err).__name__}: {last_err}")
        return None, (
            f"CREATE-GUARD fail-closed: capability registry 解析失败"
            f"（{_REGISTRY_PARSE_RETRIES} 次重试后仍失败，{type(last_err).__name__}: {last_err}）。"
            f"设施故障（注册表解析失败，非违规——请稍后重试或检查并发写）。"
            f"禁止放行——registry 是 creation_token 真源，"
            f"设施故障=检测器失效。修复：修正 {_registry_yaml} 的 YAML 语法，"
            f"或等待并发写完成后重试。"
        )

    if not isinstance(data, dict):
        return None, (
            f"CREATE-GUARD fail-closed: registry YAML 顶层非 dict（结构异常）。"
            f"禁止放行——结构异常=检测器失效。修复：检查 {_registry_yaml} 顶层结构后重试。"
        )
    return data, ""


def _collect_registered_files(data: dict) -> set[str]:
    """构建 creation_tokens 文件索引（相对路径集合，归一化为正斜杠）。"""
    tokens = data.get("creation_tokens", []) or []
    registered_files: set[str] = set()
    if isinstance(tokens, list):
        for entry in tokens:
            if not isinstance(entry, dict):
                continue
            token_file = entry.get("file", "")
            if isinstance(token_file, str) and token_file:
                registered_files.add(token_file.replace("\\", "/"))
    return registered_files


def _collect_token_entries(data: dict) -> dict[str, dict]:
    """构建 creation_tokens 条目索引 file→entry（#375 merge_evaluation 检查用）。"""
    entries: dict[str, dict] = {}
    for entry in data.get("creation_tokens", []) or []:
        if not isinstance(entry, dict):
            continue
        token_file = entry.get("file", "")
        if isinstance(token_file, str) and token_file:
            entries[token_file.replace("\\", "/")] = entry
    return entries


def _audit_merge_evaluation_missing(gateway, session_id: str | None, missing_files: list[str]) -> None:
    """merge_evaluation 缺失审计（jsonl append 到 .runtime/gate_audit/；fail-open）。

    - 时间戳用 now_utc（RULE-SCHEMA-TZ：禁 datetime.now()/time.time()）。
    - 落 gateway.project_root（tmp git repo 测试场景不触碰生产 .runtime/）。
    """
    try:
        audit_path = gateway.project_root.joinpath(*_MERGE_EVAL_AUDIT_REL)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": now_utc().isoformat(),
            "gate": "CREATE-GUARD",
            "event": "merge_evaluation_missing",
            "session_id": session_id or "?",
            "missing_count": len(missing_files),
            "missing_files": missing_files[:50],
        }
        with audit_path.open("a", encoding="utf-8") as _f:
            _f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as _e:  # noqa: BLE001 — 审计写失败 fail-open（warn-only 契约）
        logger.warning("CREATE-GUARD: merge_evaluation 审计写入失败: %s", _e, exc_info=True)


def _audit_keyword_dup_warn(
    gateway, session_id: str | None, warn_violations: list[tuple[str, str, str, list[str]]]
) -> None:
    """判重腿散文级命中 warn 审计（裁定#456 两档化；jsonl append 到 .runtime/gate_audit/；fail-open）。

    - 沿用本文件既有审计通道惯例（对标 _audit_merge_evaluation_missing /
      _diff_helpers._audit_foreign_staged）；find() 既有 lookup_audit 通道照旧自动
      落每次探针查询行，本 jsonl 只补"warn 判定"记录，不新建日志体系。
    - 时间戳用 now_utc（RULE-SCHEMA-TZ）；落 gateway.project_root（tmp 测试仓不触碰生产 .runtime/）。
    """
    try:
        audit_path = gateway.project_root.joinpath(*_KEYWORD_DUP_WARN_AUDIT_REL)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": now_utc().isoformat(),
            "gate": "CREATE-GUARD",
            "event": "keyword_dup_description_warn",
            "ruling": "456",
            "session_id": session_id or "?",
            "warn_count": len(warn_violations),
            "violations": [
                {"file": rel, "capability_id": cap_id, "canonical": canon, "hit_tokens": tokens[:8]}
                for rel, cap_id, canon, tokens in warn_violations[:50]
            ],
        }
        with audit_path.open("a", encoding="utf-8") as _f:
            _f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as _e:  # noqa: BLE001 — 审计写失败 fail-open（warn-only 契约）
        logger.warning("CREATE-GUARD: 判重 warn 审计写入失败: %s", _e, exc_info=True)


def _ast_identifier_sequence(tree: ast.Module) -> str:
    """AST 标识符有序序列（S4-B 结构证据面，手术簿 s4_b_token_sim.md §3.2）。

    收集面=类/函数名+Name.id+Attribute.attr+arg.arg（ast.walk 序）——只看标识符
    不看字面量/注释，改名同构体保留词素结构即高相似。数量截断 _TOKEN_SIM_TRUNC
    （矩阵 9 大文件护栏：截断后仍可比，不崩不扫全文）。
    """
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
        elif isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        if len(names) >= _TOKEN_SIM_TRUNC:
            break
    return " ".join(names[:_TOKEN_SIM_TRUNC])


def _comparable_token_string(ident_seq: str) -> str:
    """标识符序列 → 可比较 token 串（复用 _tokenize 切词——既有设施只调用不复制）。"""
    from zephyr.governance.capability_lookup import CapabilityLookup

    ascii_tokens, cjk_str = CapabilityLookup._tokenize(ident_seq)
    parts = ascii_tokens + ([cjk_str] if cjk_str else [])
    return " ".join(parts)


def _source_token_string(src: str) -> str | None:
    """源码 → 可比较 token 串；语法错误 → None（矩阵 6 fail-open 面）。"""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    return _comparable_token_string(_ast_identifier_sequence(tree))


def _canonical_token_string(project_root, canon_rel: str) -> str | None:
    """canonical 侧可比较 token 串（进程内 (normcase 路径, mtime_ns, size) 键缓存，§3.4）。

    键型与 :734 registry 解析缓存同款（写后失效）；读不到/语法错误 → None 且不入
    缓存（对标 :734「解析失败不缓存」——并发写窗口下次应重试，负结果不钉死）。
    """
    abs_path = Path(project_root) / canon_rel
    try:
        st = abs_path.stat()
    except OSError:
        return None
    key = (os.path.normcase(str(abs_path)), st.st_mtime_ns, st.st_size)
    cached = _CANON_TOKEN_SIM_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        src = abs_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    token_string = _source_token_string(src)
    if token_string is not None:
        _CANON_TOKEN_SIM_CACHE[key] = token_string
    return token_string


def _audit_token_sim_shadow(
    gateway,
    session_id: str | None,
    new_py_files: list[str],
    warn_violations: list[tuple[str, str, str, list[str]]],
) -> None:
    """S4-B 判重二阶段 token 相似度影子采集（audit-only，手术簿 s4_b_token_sim.md）。

    - 触发面收敛：只对 #456 散文级 warn 命中条目触发（调用点=warn 出口），
      标识符级硬拦路径零触碰（矩阵 1）。
    - 结构证据=（新建 .py 的 AST 标识符有序序列）vs（命中条目 canonical_file 的
      同款序列）经 _tokenize 切词后的 ``diff_utils.similarity_ratio``（stdlib
      difflib，零新依赖；jscpd 滑窗思路的零依赖近似）。
    - **影子模式不改任何判定**：结果只落
      ``.runtime/gate_audit/create_guard_token_sim_shadow.jsonl``（fail-open），
      ``would_block`` 恒 False、``threshold`` 恒 None——相似度分布攒满一周后由
      Owner 门位定硬拦阈值（禁止拍脑袋阈值直接上硬拦，对标 gate_cache_preflight
      「实测准入」纪律；R-B2 重放锚锁死影子先行）。
    - canonical 读不到/语法错误 → event=token_sim_skipped（fail-open 维持现状
      warn，不新增放水也不新增拦）；新建文件语法错误在上游 :1146 已豁免（矩阵 6）。
    - 时间戳 now_utc（RULE-SCHEMA-TZ）；落 gateway.project_root（tmp 测试仓不触碰
      生产 .runtime）；独立账本不回写 #456 warn 账本（风险 4）。
    """
    if not warn_violations:
        return
    try:
        new_tokens: dict[str, str | None] = {}

        def _new_token(rel: str) -> str | None:
            if rel not in new_tokens:
                try:
                    src = (Path(gateway.project_root) / rel).read_text(encoding="utf-8", errors="replace")
                except OSError:
                    new_tokens[rel] = None
                else:
                    new_tokens[rel] = _source_token_string(src)
            return new_tokens[rel]

        records: list[dict] = []
        for rel, cap_id, canon, _tokens in warn_violations[:50]:
            record = {
                "timestamp": now_utc().isoformat(),
                "gate": "CREATE-GUARD",
                "event": "token_sim_shadow",
                "mode": "shadow",
                "ruling": "456",
                "session_id": session_id or "?",
                "file": rel,
                "capability_id": cap_id,
                "canonical": canon,
            }
            new_tok = _new_token(rel)
            canon_tok = _canonical_token_string(gateway.project_root, canon) if canon else None
            if new_tok is None or canon_tok is None:
                record["event"] = "token_sim_skipped"
                record["reason"] = "new_file_unparseable" if new_tok is None else "canonical_unreadable"
                records.append(record)
                continue
            record["similarity"] = round(similarity_ratio(new_tok, canon_tok), 4)
            record["would_block"] = False  # 影子期永不判死（R-B2 锚锁死）
            record["threshold"] = None  # 阈值未标定——Owner 影子期满定档
            records.append(record)
        audit_path = Path(gateway.project_root).joinpath(*_TOKEN_SIM_SHADOW_AUDIT_REL)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_path.open("a", encoding="utf-8") as _f:
            for record in records:
                _f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as _e:  # noqa: BLE001 — 影子采集 fail-open（audit-only 契约）
        logger.warning("CREATE-GUARD: token 相似度影子采集失败（fail-open）: %s", _e, exc_info=True)


def _warn_merge_evaluation(
    gateway,
    session_id: str | None,
    data: dict,
    new_py_files: list[str],
    new_yaml_files: list[str],
) -> None:
    """裁定#375：新建资产 token 条目缺 merge_evaluation → warn+审计（首期不阻断）。

    - 检测面=own-scope（调用方已按本提交文件面过滤的 new_py/new_yaml，非 tests/）；
      无 token 条目的文件由 _check_creation_token 硬阻断管，此处不重复报。
    - 首期 warn-only：存量 token 无此字段，硬阻断=全量误伤；季度审计评估升级。
    """
    new_asset_files = [*new_py_files, *new_yaml_files]
    if not new_asset_files:
        return
    entries = _collect_token_entries(data)
    missing: list[str] = []
    for f in new_asset_files:
        entry = entries.get(f)
        if entry is None:
            continue  # 无 token 条目由 _check_creation_token 硬阻断管，不重复报
        val = entry.get(_MERGE_EVAL_FIELD)
        if not (isinstance(val, str) and val.strip()):
            missing.append(f)
    if not missing:
        return
    shown = ", ".join(missing[:5]) + ("..." if len(missing) > 5 else "")
    logger.warning(
        "CREATE-GUARD warn(裁定#375 内收判据): %d 个新建资产 token 条目缺 %s 字段: %s. "
        "四判据(同真源可派生->必并|零触发零消费->退役|同域重复簇->收敛唯一|跨域不同对象->不并)"
        "要求立项时做合并评估并留一句话结论. 修复: 在 capability_canonical_file_registry.yaml "
        '对应 creation_tokens 条目补 %s: "<结论一句话>"'
        "(或 batch_creation_tokens.py --merge-evaluation 登记时携带). "
        "首期 warn-only, 季度审计评估升级.",
        len(missing),
        _MERGE_EVAL_FIELD,
        shown,
        _MERGE_EVAL_FIELD,
    )
    _audit_merge_evaluation_missing(gateway, session_id, missing)


def _no_token_detail(unregistered: list[str], file_kind: str) -> str:
    """creation_token 缺失阻断消息（.py/.yaml/其他格式共用模板）。"""
    return (
        f"无 creation_token，禁止造第二真源（trae_060 §2）: {unregistered}. "
        f"commit 新建 {file_kind} 文件前 MUST 在 capability_canonical_file_registry.yaml "
        f"的 creation_tokens 字段登记 token（声明创建意图 + 关联 capability）。"
        f'格式: - file: "<相对路径>"  token: "auto-xxx"  '
        f'created_by: "session-xxx"  capability: "xxx"'
    )


def _check_creation_token(
    gateway,
    new_py_files: list[str],
    new_yaml_files: list[str],
    new_other_files: list[str] | None = None,
    registry_data: dict | None = None,
) -> tuple[bool, str]:
    """检测新增 .py/.yaml 文件是否登记了 creation_token（trae_060 §2 唯一真源）。

    fail-closed：YAML 不可达时阻断（防删 registry 绕过 token 检查）。
    P-2 修复：registry 路径随 gateway.project_root 解析（支持 worktree 路径）。
    #375：registry_data 传入时跳过加载（调用方单次加载共用——40k 行 YAML
    重试解析昂贵，token 硬阻断与 merge_evaluation warn 不双载）。
    """
    if registry_data is None:
        registry_data, detail = _load_capability_registry(gateway)
        if registry_data is None:
            return False, detail
    data = registry_data
    registered_files = _collect_registered_files(data)

    # 检测新增 .py 文件是否登记了 creation_token
    unregistered = [f for f in new_py_files if f not in registered_files]
    if unregistered:
        return False, _no_token_detail(unregistered, ".py")
    # 检测新增非 rules/ .yaml 文件是否登记了 creation_token
    unregistered_yaml = [f for f in new_yaml_files if f not in registered_files]
    if unregistered_yaml:
        return False, _no_token_detail(unregistered_yaml, ".yaml")
    # 阶段 2 治本（ARCH-TTL-DOC-001）：检测新增 .md/.sh/.ps1/.mmd/.json 文件
    if new_other_files:
        unregistered_other = [f for f in new_other_files if f not in registered_files]
        if unregistered_other:
            return False, _no_token_detail(unregistered_other, ".md/.sh/.ps1/.mmd/.json")
    return True, ""


def _check_field_header(gateway, new_py_files: list[str]) -> tuple[bool, str]:
    """ARCH-031 治本：字段头部完整性检测（14 字段 / __init__.py 最低 3 字段）。

    豁免：codegen 文件（BEGIN CODEGEN 标记）。真源：trae_047 field_specs。
    fail-closed：真源读取失败时阻断。无 new_py_files 时直接放行。
    """
    if not new_py_files:
        return True, ""

    _TRAE_047_YAML = gateway.project_root / "docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml"
    # F-5 修复续：trae_047 路径回退到全局 REPO_ROOT（对标 P-2 capability registry 回退模式）
    if not _TRAE_047_YAML.exists():
        from zephyr.shared.io.paths import REPO_ROOT

        _TRAE_047_YAML = REPO_ROOT / "docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml"
    try:
        _rule_data = yaml.safe_load(_TRAE_047_YAML.read_text(encoding="utf-8"))
        _field_specs = _rule_data["sections"]["gov_eng_002"]["field_specs"]
        _REQUIRED_FIELDS = _field_specs["a_full"]["required"]
        _INIT_MIN_FIELDS = _field_specs["init_min"]
    except Exception as _e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return False, (
            f"字段头部规范真源读取失败（trae_047.yaml field_specs）: {_e}. "
            f"修复：检查 {_TRAE_047_YAML} 是否存在且 field_specs 结构完整。"
        )

    for _py_file in new_py_files:
        _abs_path = gateway.project_root / _py_file
        if not _abs_path.exists():
            continue
        try:
            _head = "\n".join(_abs_path.read_text(encoding="utf-8", errors="replace").split("\n")[:30])
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug(
                "CREATE-GUARD: 读取文件头失败 file=%s: %s",
                _py_file,
                e,
                exc_info=True,
            )
            continue  # 读取失败由其他 gate 检测，此处 fail-open

        # codegen 文件豁免（自动生成，字段由模板注入，手写会被覆盖）
        if "BEGIN CODEGEN" in _head or "BEGIN CODGEN" in _head:
            continue

        # __init__.py 只要求 3 字段（包标记，CONSUMERS 等可省）
        _is_init = _py_file.endswith("__init__.py")
        _required = _INIT_MIN_FIELDS if _is_init else _REQUIRED_FIELDS

        _missing = [_field for _field in _required if not re.search(rf"#\s*\[{re.escape(_field)}\]", _head)]

        if _missing:
            return False, (
                f"字段头部不完整（ARCH-031）: {_py_file} 缺失字段: {_missing}. "
                f"修复：在文件头部添加 '# [FIELD] value' 标注（共{len(_required)}字段: "
                f"{'/'.join(_required)}）。"
                + (f" __init__.py 最低要求: {'/'.join(_INIT_MIN_FIELDS)}" if _is_init else "")
            )
    return True, ""


# === S4-C CREATE-GUARD p90 缓存尾治本（2026-09-30，手术簿 s4_c_p90_cache.md） ===
# 病根：有新建 .py 的 commit 每次 _build_capability_lookup() 全量构造（实测 ~86-109s/
# 实例），CREATE-GUARD 门级 p90=55.3s 且 reused=0（head_dependent 被排除出 P2⑧
# 白名单=结构性，gate_cache_preflight.py:44-47）。治本=判定语义零变化，只动构造时机
# 与失效粒度：进程级单例+失效键（registry mtime_ns+size ∪ 双根扫描概要）+分片扫描
# （capability_lookup.scan_disk_headers 片缓存）+空闲期后台预热。
# 一键回退：env ZEPHYR_CG_LOOKUP_SINGLETON=0 → 每次新构造（现行为）。
_LOOKUP_SINGLETON_ENV = "ZEPHYR_CG_LOOKUP_SINGLETON"
# {"entry": (失效键, lookup 实例)}——单键槽（最新实例即全部语义），测试经 fixture 清零
_LOOKUP_SINGLETON_CACHE: dict[str, tuple[tuple, Any]] = {}
# 预热线程与 commit 线程同抢构造的收敛锁（双线程同抢只建一次——手术簿 §3.3）
_LOOKUP_LOCK = threading.Lock()


def _lookup_invalidation_key() -> tuple | None:
    """进程级 lookup 单例失效键（S4-C §3.1）。

    键 =（registry yaml normcase 路径, mtime_ns, size）∪（双根扫描概要序列：
    每根 (normcase 路径, .py 文件数, max mtime_ns)）——registry 是判重真源面，
    扫描概要是 basename/头部派生面，两面任一变化都必须重建（陈旧册=漏拦第二真源）。

    返回 None=失效判定设施自身异常（stat/概要失败）→ 调用方不缓存不复用，
    回退现行为每次新构造（fail-safe 对齐 gate_cache_preflight [ERROR_CONTRACT]）。
    """
    try:
        from zephyr.governance.capability_lookup import REGISTRY_YAML, SCAN_ROOTS, scan_root_summary

        reg = Path(REGISTRY_YAML)
        st = reg.stat()
        summaries: list[tuple[str, int, int]] = []
        for root in SCAN_ROOTS:
            root_p = Path(root)
            if not root_p.exists():
                continue
            summary = scan_root_summary(root_p)
            if summary is None:
                return None
            summaries.append((os.path.normcase(str(root_p)), summary[0], summary[1]))
        return (os.path.normcase(str(reg)), st.st_mtime_ns, st.st_size, tuple(summaries))
    except Exception:  # noqa: BLE001 — fail-safe：失效判定设施异常=回退现行为（手术簿 §3.4）
        return None


def _build_capability_lookup():
    """CapabilityLookup 构造缝（唯一构造点，供 basename 碰撞与查功能关键词共享）。

    S4-C 进程级单例（2026-09-30）：失效键（_lookup_invalidation_key）未变 → 复用
    常驻实例（gateway / commit_belt_daemon / 队列 serializer 均常驻进程，跨 commit
    复用成立，0.2s 档）；键变（registry 写入/扫描根概要漂移）→ 重建。判定语义
    零变化——检索面、#456 两档判据、fail-closed 出口全部不动，动的只是构造时机。

    - 一键回退：env ``ZEPHYR_CG_LOOKUP_SINGLETON=0`` → 每次新构造（现行为）。
    - 失效键不可得（None）→ 不缓存（每次新构造，fail-safe 不带病复用）。
    - 双线程同抢构造经 _LOOKUP_LOCK 收敛为单次（预热线程与 commit 竞争不双建）。
    - 实测本仓构造一次 ~86-109s（磁盘头部扫描+派生，另有首次 find 的 removed
      派生 ~15s）——本缝仍是测试注入缝：测试可 monkeypatch 本函数注入小型
      lookup（禁在测试里跑全库扫描）。
    """
    from zephyr.governance.capability_lookup import CapabilityLookup

    if os.environ.get(_LOOKUP_SINGLETON_ENV, "") == "0":
        return CapabilityLookup()
    key = _lookup_invalidation_key()
    if key is not None:
        entry = _LOOKUP_SINGLETON_CACHE.get("entry")
        if entry is not None and entry[0] == key:
            return entry[1]
    with _LOOKUP_LOCK:
        if key is not None:
            entry = _LOOKUP_SINGLETON_CACHE.get("entry")
            if entry is not None and entry[0] == key:
                return entry[1]
        instance = CapabilityLookup()
        if key is not None:
            _LOOKUP_SINGLETON_CACHE["entry"] = (key, instance)
        return instance


def warm_capability_lookup_async() -> None:
    """空闲期后台预热/刷新 lookup 单例（S4-C §3.3：把构造尾从提交关键路径搬走）。

    判重链完成后 fire-and-forget：键未变→_build_capability_lookup 命中缓存即返回
    （线程毫秒级自灭）；键已陈旧→后台重建，为本进程下一次 commit 备好热实例。
    - daemon 线程不阻塞进程退出；任何异常全吞（预热是优化，绝不影响判定路径）。
    - spawn 后全局态变化（测试拆装/他线程改册）→ 键不匹配即放弃本轮，下次触发重验
      ——防测试线程用已还原的全局态误建生产实例。
    - 与 commit 线程抢构造经 _LOOKUP_LOCK 收敛为单次（手术簿 §5 矩阵 8/9）。
    - kill-switch（ZEPHYR_CG_LOOKUP_SINGLETON=0）下不预热。
    """
    if os.environ.get(_LOOKUP_SINGLETON_ENV, "") == "0":
        return
    key_at_spawn = _lookup_invalidation_key()
    if key_at_spawn is None:
        return

    def _warm() -> None:
        try:
            key = _lookup_invalidation_key()
            if key is None or key != key_at_spawn:
                return
            _build_capability_lookup()
        except Exception:  # noqa: BLE001 — 预热失败静默（fail-safe：下次触发重验）
            logger.debug("CREATE-GUARD lookup 预热失败（下次触发重验）", exc_info=True)

    threading.Thread(target=_warm, name="create-guard-lookup-warmup", daemon=True).start()


def _check_basename_collision(gateway, new_py_files: list[str], lookup=None) -> tuple[bool, str]:
    """ARCH-031 门禁缺口治本：磁盘 basename 碰撞检测（GATE-SSOT L2）。

    fail-open：CapabilityLookup 不可用时 warning 并跳过。
    波13·包13.1：lookup 传入时复用共享实例（判重尺角色已被
    _check_capability_keyword_overlap 取代，本检测降为冗余后备，行为数值不动）。
    """
    if not new_py_files:
        return True, ""
    try:
        from zephyr.governance.capability_lookup import (
            CAPABILITY_DUPLICATE_FIX_HINT,
            CapabilityLookup,
        )

        _lookup = lookup if lookup is not None else CapabilityLookup()
        _new_py_tuples = [(str(gateway.project_root / f), f) for f in new_py_files]
        _dups = _lookup.check_capability_duplicates(_new_py_tuples)
        if _dups:
            _details = "; ".join(f"{d.rel_path}: {d.detail}" for d in _dups)
            return False, (f"能力重复/basename碰撞(GATE-SSOT L2): {_details}. {CAPABILITY_DUPLICATE_FIX_HINT}")
    except Exception as _e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("CREATE-GUARD: capability_lookup 不可用，跳过 basename 碰撞检测: %s", _e, exc_info=True)
    return True, ""


def _keyword_identifier_words(name: str) -> list[str]:
    """标识符切词（snake/camel/kebab/数字段），返回小写字母词（长度≥2，去纯数字）。

    真源探针构造的唯一切词点——stem 与顶层类/函数名共用。数字段（如日期戳）是
    测试唯一名惯例不是功能语义，剔除；<2 字词（如 a/b）是噪声剔除。
    """
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[_\-\s]+", " ", name)
    return [w.lower() for w in s.split() if len(w) >= 2 and w.isalpha()]


def _build_keyword_probes(rel_path: str, tree: ast.Module) -> list[str]:
    """构建一个新建 .py 的关键词查询面探针列表（波13·包13.1）。

    查询面 = 文件名 stem + 模块 docstring 首段 + 顶层 class/function 名，切成探针：
      ① stem 与②每个顶层类/函数名 → 切词后 ≥2 词 AND 查询（单词查询=过宽子串噪声，弃）；
      ③ docstring 首段 CJK 连续段（≥3 字，find() 的 ≥_CJK_MIN_SUBSTRING 滑窗语义面）；
      ④ docstring 首段相邻 ASCII 词对（bigram，两词 AND，防单词全命中）。
    上限 _MAX_KEYWORD_PROBES（排序即优先级：stem > 类名 > 函数名 > CJK > bigram）。
    只调既有 CapabilityLookup.find() 判重，禁在本函数外另起匹配器（§2.1 收编令）。
    """
    probes: list[str] = []
    seen: set[str] = set()

    def _add(query: str) -> None:
        query = query.strip().lower()
        if len(query) < 3 or query in seen:
            return
        # 纯 ASCII 探针必须 ≥2 词：单词查询走 find() 的精确子串分支（实测 find("gate")
        # 命中 181/388——单 ASCII 词=全库噪声，不成"功能关键词"）；CJK 探针 ≥3 字
        # 由 find() 滑窗语义（_CJK_MIN_SUBSTRING=3）保证窄度，单词可放行。
        if query.isascii() and len(query.split()) < 2:
            return
        seen.add(query)
        probes.append(query)

    stem = rel_path.rsplit("/", 1)[-1]
    if stem.endswith(".py"):
        stem = stem[:-3]
    _add(" ".join(_keyword_identifier_words(stem)))
    classes: list[str] = []
    functions: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
    for name in classes + functions:
        _add(" ".join(_keyword_identifier_words(name)))
    doc = ast.get_docstring(tree) or ""
    first_para = re.split(r"\n[ \t]*\r?\n", doc, maxsplit=1)[0]
    for run in _CJK_RUN_RE.findall(first_para):
        _add(run)
    ascii_words = [
        w.lower() for w in _ASCII_DOC_WORD_RE.findall(first_para) if len(w) >= 4 and w.lower() not in _BIGRAM_STOPWORDS
    ]
    for prev, nxt in pairwise(ascii_words):
        if len(probes) >= _MAX_KEYWORD_PROBES:
            break
        _add(f"{prev} {nxt}")
    return probes[:_MAX_KEYWORD_PROBES]


def _probe_hits_identifier_fields(lookup, probe: str, entry: dict) -> bool:
    """判定单条探针命中是否标识符级（capability_id/aliases/canonical_file 直击，裁定#456）。

    find() 把五字段拼成单一 haystack 检索，返回条目不标注命中字段——本函数在
    create_guard 侧用条目自身字段本地复检收窄：标识符三字段拼接面按 find() 同款
    匹配语义（精确子串 OR _tokenize/_token_match token 包含，两者皆为
    CapabilityLookup 既有静态件，只调用不改动 capability_lookup.py）复检：
    - 标识符面命中 ⇒ 标识符级（维持硬拦）；
    - 否则该命中只能来自 description/module_id（散文/派生面）⇒ 散文级（warn）。
    lookup 无静态件（异构测试桩）时保守判标识符级——维持 #456 前硬拦原行为，
    禁止因分类能力缺失而放水（fail-closed 对齐本检测哲学）。
    """
    ident_parts = [str(entry.get("capability_id", "") or "")]
    ident_parts.extend(str(a) for a in (entry.get("aliases") or []) if a)
    ident_parts.append(str(entry.get("canonical_file", "") or ""))
    ident_haystack = " ".join(ident_parts).lower()
    if not ident_haystack.strip():
        return False
    if probe.lower() in ident_haystack:
        return True
    try:
        ascii_tokens, cjk_str = lookup._tokenize(probe)
        return lookup._token_match(ascii_tokens, cjk_str, ident_haystack)
    except AttributeError:
        return True


def _scan_file_for_keyword_dupes(
    lookup, rel: str, src: str, batch_paths: set[str], session_id: str | None
) -> tuple[list[tuple[str, str, str, list[str]]], list[tuple[str, str, str, list[str]]]]:
    """单文件面：探针→find()→命中归并+两档分流（裁定#456）。

    返回 (硬拦条目, warn条目) 双列表；条目形状同前 (rel, cap_id, canonical, 命中探针词)。
    - 标识符级：该 capability 的命中探针中任一条直击 capability_id/aliases/canonical_file
      ⇒ 硬拦（判死阈值与 #456 前全等）；
    - 散文级：全部命中探针仅落在 description/module_id ⇒ warn 列（不阻断）。
    命中过滤：canonical 指向该文件自身或同批新建文件 ⇒ 自引用/同批登记，非重复信号。
    逃生标记命中 ⇒ 该文件整体豁免（双空列表）。语法错误 ⇒ 豁免（由其他 gate 检测）。
    """
    if _KEYWORD_DUP_MARKER_RE.search(src):
        return [], []
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return [], []
    hits: dict[str, dict] = {}
    hit_tokens: dict[str, list[str]] = {}
    ident_tokens: dict[str, list[str]] = {}
    for probe in _build_keyword_probes(rel, tree):
        for entry in lookup.find(probe, session_id=session_id):
            cap_id = str(entry.get("capability_id", "") or "")
            canon = str(entry.get("canonical_file", "") or "").replace("\\", "/")
            if not cap_id or not canon:
                continue
            if canon == rel or canon in batch_paths:
                continue
            hits.setdefault(cap_id, entry)
            hit_tokens.setdefault(cap_id, []).append(probe)
            if _probe_hits_identifier_fields(lookup, probe, entry):
                ident_tokens.setdefault(cap_id, []).append(probe)
    hard: list[tuple[str, str, str, list[str]]] = []
    warn: list[tuple[str, str, str, list[str]]] = []
    for cap_id, entry in hits.items():
        item = (
            rel,
            cap_id,
            str(entry.get("canonical_file", "") or ""),
            sorted(set(hit_tokens[cap_id])),
        )
        (hard if ident_tokens.get(cap_id) else warn).append(item)
    return hard, warn


def _check_capability_keyword_overlap(
    gateway,
    new_py_files: list[str],
    session_id: str | None = None,
    lookup=None,
    lookup_error: str = "",
) -> tuple[bool, str]:
    """波13·包13.1：新建 .py 查功能关键词（Owner 授权：从查文件名升级到查功能关键词）。

    对每个新建 .py：构建查询面探针（_build_keyword_probes），逐探针调用既有
    ``CapabilityLookup.find()``（检索面=capability_id+description+canonical_file+
    module_id+aliases，capability_lookup.py L924-930；禁重写匹配器）。
    - 裁定#456 两档化：命中按字段分级（_probe_hits_identifier_fields 本地复检，
      复用 find() 同款 _tokenize/_token_match 静态件，不改 capability_lookup.py）——
      命中字段∈{capability_id, aliases, canonical_file}（标识符级）⇒ 硬阻断，消息
      逐条给出 capability_id / canonical（派生面，canonical_override=其优先级 1
      真源）/ 命中探针词 / 逃生标记确切字面量 ``# create-guard-not-dup: <一句话理由>``
      （带非空理由即按文件豁免本检测）；仅命中 description（散文面）⇒ 降为 warn：
      logger.warning（含处方：逃生标记或 python -m zephyr.library.lookup 正查）+
      _audit_keyword_dup_warn 落账（.runtime/gate_audit/create_guard_keyword_dup_warn.jsonl，
      fail-open），不阻断。硬拦与 warn 并存时硬拦优先短路（warn 留待阻断解除后的
      下轮提交再浮出）。逃生标记豁免与判死阈值对标识符命中的行为零改动。
    - 命中=0 ⇒ 放行；漂移日志=find() 既有审计 .runtime/lookup_audit/<sid>.jsonl
      的 result_count=0 行（不新建日志文件）。
    - fail-closed：lookup 构造失败/find 异常 ⇒ 阻断（检测器失效禁止放行，对标 token
      检查 fail-closed 哲学）；语法错误文件 fail-open（由其他 gate 检测）。
    - lookup 由调用方（_run_file_registration_checks）经 _build_capability_lookup
      单例共享——本仓实测一次构造 ~86s，禁止双载。
    - 取代申报（#ARCH-310 §4）：本检测取代 _check_basename_collision（fail-open
      basename 尺）的判重角色与 capability_overlap_gate stage-1 文件名词元启发式；
      两者降为冗余后备/禁用态，本道不删不改其数值。
    """
    if not new_py_files:
        return True, ""
    if lookup is None:
        return False, (
            f"CREATE-GUARD 查功能关键词 fail-closed: CapabilityLookup 构造失败"
            f"（{lookup_error or '未提供且构造未执行'}），无法判定新建 .py 是否与在册能力重复。"
            f"禁止放行——检测器失效时漏放第二真源。"
            f"修复：确认 capability registry 可达后重试。"
        )
    hard_violations: list[tuple[str, str, str, list[str]]] = []
    warn_violations: list[tuple[str, str, str, list[str]]] = []
    try:
        batch_paths = set(new_py_files)
        for rel in new_py_files:
            abs_path = gateway.project_root / rel
            if not abs_path.exists():
                continue
            try:
                src = abs_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue  # 读不到由下游检测面兜底，此处不造新判据
            _hard, _warn = _scan_file_for_keyword_dupes(lookup, rel, src, batch_paths, session_id)
            hard_violations.extend(_hard)
            warn_violations.extend(_warn)
    except Exception as _e:  # noqa: BLE001 — fail-closed：检测器失效禁止放行
        return False, (
            f"CREATE-GUARD 查功能关键词 fail-closed: CapabilityLookup 异常"
            f"({type(_e).__name__}: {_e})，无法判定新建 .py 是否与在册能力重复。"
            f"禁止放行——检测器失效时漏放第二真源。"
            f"修复：确认 capability registry 可达后重试。"
        )
    if hard_violations:
        _lines = "; ".join(
            f"{rel} → capability_id={cap_id} | canonical_override={canon} | 命中词={tokens}"
            for rel, cap_id, canon, tokens in hard_violations
        )
        return False, (
            f"新建 .py 查功能关键词命中在册能力（波13·包13.1，判为第二真源）: {_lines}. "
            f"查询面=文件名 stem+模块 docstring 首段+顶层类/函数名，检索器=CapabilityLookup.find()"
            f"（既有真源，禁另起匹配器）。"
            f"修复：优先扩展上述 canonical 文件而非新建（RULE-CAPABILITY-LOOKUP / trae_060 §2）。"
            f"若确非重复，在该 .py 内任意注释行写逃生标记（冒号后必须跟一句话理由，逐字格式）: "
            f"# create-guard-not-dup: <一句话理由>"
            f"（例: '# create-guard-not-dup: 本模块只做 X 域只读展示，非 Y 能力的第二实现'；"
            f"可 grep 审计: git grep -rn '{_KEYWORD_DUP_MARKER}'）。"
            f"零命中漂移日志=find() 既有审计 .runtime/lookup_audit/<session_id>.jsonl 的 result_count=0 行，不新建日志。"
            f"裁定#456 两档化：本条为标识符级命中（capability_id/aliases/canonical_file），维持硬拦；"
            f"仅命中 description 散文面者降为 warn 不阻断。"
        )
    if warn_violations:
        _warn_lines = "; ".join(
            f"{rel} → capability_id={cap_id} | canonical_override={canon} | 命中词={tokens}"
            for rel, cap_id, canon, tokens in warn_violations
        )
        logger.warning(
            "CREATE-GUARD warn(裁定#456 判重腿两档化): 新建 .py 探针仅命中在册能力 description 散文面"
            "（非 capability_id/aliases/canonical_file 标识符级），降为警告不阻断: %s. "
            "处方二选一：①确非重复→在该 .py 内任意注释行写逃生标记（逐字格式）"
            "# create-guard-not-dup: <一句话理由>；②或先 python -m zephyr.library.lookup <关键词> 正查"
            "在册能力，优先扩展 canonical 文件而非新建（RULE-CAPABILITY-LOOKUP）. "
            "warn 记录已落账 .runtime/gate_audit/create_guard_keyword_dup_warn.jsonl"
            "（find() 探针查询照旧落 .runtime/lookup_audit/<session_id>.jsonl）.",
            _warn_lines,
        )
        _audit_keyword_dup_warn(gateway, session_id, warn_violations)
        # S4-B 二阶段影子采集（audit-only）：散文级 warn 面加 token 相似度结构证据，
        # 只落影子账本不改判定（would_block 恒 False，阈值 Owner 影子期满定档）。
        _audit_token_sim_shadow(gateway, session_id, new_py_files, warn_violations)
    return True, ""


def _filter_to_commit_files(
    new_py_files: list[str],
    new_yaml_files: list[str],
    new_other_files: list[str],
    commit_files_rel: set[str],
) -> tuple[list[str], list[str], list[str]]:
    """治本 2026-06-30：只检测 commit 文件中的新增文件（gateway 选择性提交）。"""
    return (
        [f for f in new_py_files if f in commit_files_rel],
        [f for f in new_yaml_files if f in commit_files_rel],
        [f for f in new_other_files if f in commit_files_rel],
    )


def _run_file_registration_checks(
    gateway,
    new_py_files: list[str],
    new_yaml_files: list[str],
    new_other_files: list[str],
    session_id: str | None = None,
) -> tuple[bool, str]:
    """文件登记类检测链：creation_token → #375 merge_evaluation warn → 字段头部 → basename 碰撞。

    registry 单次加载供 token 硬阻断与 #375 warn 共用（40k 行 YAML 重试解析昂贵，
    不双载；撕读重试计数语义不变——仍是一次 _load_capability_registry 调用）。
    """
    data, detail = _load_capability_registry(gateway)
    if data is None:
        return False, detail

    # creation_token 检测（trae_060 §2 唯一真源）——阶段 2：覆盖全 7 格式
    passed, detail = _check_creation_token(gateway, new_py_files, new_yaml_files, new_other_files, registry_data=data)
    if not passed:
        return False, detail

    # 裁定#375 内收判据门禁化：新建资产 token 缺 merge_evaluation → warn+审计
    # （首期不阻断——own-scope 已由调用方过滤到本提交文件面）
    _warn_merge_evaluation(gateway, session_id, data, new_py_files, new_yaml_files)

    # ARCH-031：字段头部完整性检测
    passed, detail = _check_field_header(gateway, new_py_files)
    if not passed:
        return False, detail

    # ARCH-031：basename 碰撞检测 + 波13·包13.1 查功能关键词（链尾追加，既有各步
    # 先后语义不动）。CapabilityLookup 经 _build_capability_lookup 单次构造共享
    # （实测 ~86s/实例，禁双载）；构造失败时 basename 保持 fail-open 原语义
    # （内部再构造→同败→warning 跳过），关键词检测 fail-closed（检测器失效禁放行）。
    _lookup = None
    _lookup_err = ""
    if new_py_files:
        try:
            _lookup = _build_capability_lookup()
        except Exception as _e:  # noqa: BLE001 — 交由两检测各自按其 fail 语义处置
            _lookup_err = f"{type(_e).__name__}: {_e}"
    passed, detail = _check_basename_collision(gateway, new_py_files, lookup=_lookup)
    if not passed:
        return False, detail
    passed, detail = _check_capability_keyword_overlap(
        gateway, new_py_files, session_id=session_id, lookup=_lookup, lookup_error=_lookup_err
    )
    # S4-C 预热：判重链完成后空闲期后台预热/刷新单例（daemon，异常全吞，不影响
    # 本链判定）——为本进程下一次 commit 把 ~86-109s 构造尾从关键路径搬走。
    warm_capability_lookup_async()
    return passed, detail


def make_create_guard() -> GateSpec:
    """构造新建 .py 文件 creation_token 阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="CREATE-GUARD", priority=60)。
        priority=60——在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行。

    裁定#216 Tier1 P1 重构（2026-07-15）：原 _check 闭包 475 行 McCabe=101，
    Extract Method 提取为 9 个模块级 helper，_check 简化为 pipeline McCabe≈14。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        commit_files_rel = _compute_commit_files_rel(gateway, files)

        # 元问题3治本：新增 make_*_reconciler 需 trae_060 §4 审查标记
        passed, detail = _check_reconciler_marker(gateway, commit_files_rel)
        if not passed:
            return False, detail

        # 获取 staged 新增文件（fail-closed）
        staged_new, detail = _get_staged_new_files(gateway)
        if staged_new is None:
            return False, detail

        # ARCH-037：rules/ .yaml 命名格式硬阻断（须在 own 拆分前：rename 检测面在
        # git R 清单，且内部已按 commit_files_rel 过滤=own 语义，不依赖 staged_new）
        passed, detail = _check_rule_yaml_naming(gateway, staged_new, commit_files_rel)
        if not passed:
            return False, detail

        # own 化（st-gslim-20260923 P2）：登记链只对本 session 新增文件，外来 warn+审计不阻断
        # （§3.1 他会话在途违规不代修；骑乘本体由 FOREIGN-CHANGE-DETECTION 全暂存台负责。
        # 不设早退：下游 ARCH-031 governance 根 R-rename 检测直读 git 清单，空 staged_new
        # 时也必须执行（rename 绕过 --diff-filter=A 的反绕过面）；空清单由其后既有守卫放行）
        staged_new = _split_own_foreign(gateway, staged_new, files, kwargs.get("session_id"), gate_name="CREATE-GUARD")[
            0
        ]

        # 过滤 .py / .yaml + 豁免 tests/（真源：commit_gate_registry.is_test_exempt）
        new_py_files, new_yaml_files = _filter_new_py_and_yaml(staged_new)
        new_other_files = _filter_new_other_formats(staged_new)

        # ARCH-031 防复发：governance/ 根检测 MUST 用 UNFILTERED new_py_files
        passed, detail = _check_governance_root(gateway, new_py_files)
        if not passed:
            return False, detail

        if not new_py_files and not new_yaml_files and not new_other_files:
            return True, ""

        # 治本 2026-06-30：只检测 commit 文件中的新增 .py（gateway 选择性提交）
        new_py_files, new_yaml_files, new_other_files = _filter_to_commit_files(
            new_py_files, new_yaml_files, new_other_files, commit_files_rel
        )

        if not new_py_files and not new_yaml_files and not new_other_files:
            return True, ""

        # ARCH-034：类名跨模块唯一性检测
        passed, detail = _check_class_uniqueness(gateway, new_py_files)
        if not passed:
            return False, detail

        # 文件登记类检测链（creation_token / #375 merge_evaluation warn / 字段头部 / basename 碰撞
        # / 波13·包13.1 查功能关键词——链尾追加，不改既有各步先后语义）
        return _run_file_registration_checks(
            gateway, new_py_files, new_yaml_files, new_other_files, kwargs.get("session_id")
        )

    return GateSpec(gate_id="CREATE-GUARD", check=_check, priority=60)
