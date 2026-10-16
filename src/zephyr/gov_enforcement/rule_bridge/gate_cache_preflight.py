# [BLUEPRINT] MOD-GOV_GATE_CACHE_PREFLIGHT | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.rule_bridge.gate_cache_preflight
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] stdlib（hashlib/json/os/time）；zephyr.shared.infra.process_pool（无）
# [CONSUMERS] git_commit_gateway（P2⑦ 预跑采信）；commit_gate_registry.check_all（P2⑧ 缓存查/存）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 白名单=实测命中台（gate_execution_stats 24h 窗；2026-10-15 扩容批 15→31，逐台输入面审计）且输入面=own staged∪own_scope∪manifest∪门实现的纯内容/AST 扫描门；只缓存 passed=True（降级态与失败一律不缓存——fail-open 不被缓存放大）；P2⑧ 键=gate_id×own_scope×own 内容哈希(inputs_sha)×spec_sha(门实现面内容哈希)×manifest 输入哈希×flags mtime——禁含 HEAD_sha 与共享暂存树指纹（T7/B2）；P2⑦ 预跑指纹仍含 write-tree/HEAD（锁内重验采信语义不变）；TTL 10min；两 flag（gate_result_cache/gate_preflight）出厂默认 OFF，启用属 Owner 窗口（宪章 B-007）；本模块 flag_enabled 亦承载 gate_chain_parallel（P1-1 并行链，出厂 OFF）读取
# [MODIFY-GUARD] 2026-09-10 提交通道性能优化方案 §2.2-A3 / §2.3 方案A / §2.6 分级清单（等价性红线：信号型永不缓存/预跑；指纹含 gate 输入清单 sha）；2026-09-25 T7/B2（st-commitspeed-tbl-20260924）：P2⑧ 键去全局态改内容哈希（红证=他人推进 HEAD/暂存他件即全失效为 87 命中/24h 病根），白名单改实测 top15（依据 gate_execution_stats）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 指纹/缓存设施任何异常=回退全量现算（fail-safe to current behavior，调用方无感知）
# [TESTS] tests/git/test_gate_cache_preflight.py; tests/git/test_gate_cache_key_isolation.py
# [TTL] permanent
"""gate_cache_preflight — P2⑧ 门禁结果持久缓存 + P2⑦ 锁外预跑指纹采信的共享基座。

T7/B2 缓存键改内容哈希（st-commitspeed-tbl-20260924，A4 阶梯 S2）
------------------------------------------------------------------
**病根（红证在案，tests/git/test_gate_cache_key_isolation.py）**：旧 P2⑧ 键含
``staged_tree_sha``（``git write-tree``，对共享 index 逐字节敏感）与
``head_sha``——并发场里任何人暂存任何文件、任何人推进 HEAD，都会作废所有人的
全部缓存条目 ⇒ 实测 24h 仅 87 命中（白名单 14 台只覆盖 6.1% 门禁分钟）。

**新键**（``GateResultCache._path``）＝「门实际读什么」定键：

========================================  =======================================
字段                                      失效语义
========================================  =======================================
``gate_id``                               换门即换键空间
``own_scope_hash``                        同文件换 claim 范围不误命中
``own_content_sha``（inputs_sha）         本件 staged blob sha 合集——own 内容
                                          变化一字节即 miss（投毒逆命题）
``spec_sha``                              门实现面内容哈希（commit_gates/*.py
                                          全集）——门源码一字节篡改即 miss
``manifest_inputs_sha``                   GATE_INPUT_MANIFEST 声明的注册表/配置
                                          文件工作树字节——注册表字节篡改即 miss
``flags_mtime``                           config/flags.yaml 变更全失效
========================================  =======================================

**禁含 HEAD 与共享暂存树状态**：键不再含 ``head_sha``/``staged_tree_sha``。
等价性论证：白名单准入判据（机械可查，A3 矩阵逐台核过）＝判定输入面 ⊆
own staged 内容 ∪ own_scope 集合 ∪ manifest 声明文件 ∪ 门实现本身——全局态
从不在输入面，键收敛到输入面＝等价而非放松。故信号型（RECONCILER-HEALTH/
GIT-CALL-BUDGET 等读并发态势者）、head_dependent 门（CREATE-GUARD 等）、
注册表读取未声明 manifest 者、CloneGuard 引擎依赖门（CAPABILITY-OVERLAP，
有 degraded 语义）、lane_verify_async 全图门（GATE-DOMAIN-FK 等）一律不准入。

**与包9 不可变树视图（flags.git_operations.immutable_tree，出厂 OFF）的协同**：
own-tree ON 时门禁链跑 ``CommitTreeView`` 替身，门读到的集合=本件不可变树，
own_tree_sha（此处以 own_content_sha 承载=树内本件文件内容哈希集）天然稳定 ⇒
命中面成立；OFF 时门读共享暂存区，但白名单门的判定输入仍只有本件 staged 文件
字节（own_scope 已 claim 隔离），键按 inputs_sha 仍可命中——读集哈希不含共享
树状态，是他人的暂存/提交活动进不了键，而不是键假装看不见本件内容。
两 flag 正交：缓存启停只归 P2⑧ ``gate_result_cache``，本批不改任何出厂 flag。

**白名单准入（实测，禁拍脑袋）**：``CONTENT_SCAN_CACHE_WHITELIST``＝
``.runtime/audit/gate_execution_stats.jsonl`` 24h 窗（114 链次，2026-09-25 量取）
实测 top15 命中台：(a) 实证复用面（preflight_reused/cache_hit>0）10 台；
(b) 实证耗时面（total_ms 最高且准入判据全绿）新进 5 台（BLUEPRINT-HEADER
1781s、CH-BATCH-SIZE 872s、BLUEPRINT-FORMAT 725s、FILE-COPY 136s、
NO-HARDCODED-URL 124s）。原 NO-LONG-PARAM-LIST/NO-GOD-CLASS/
NO-HIGH-COMPLEXITY 三台 24h 零触发零消费且不在 in_process_gate_registry 名册
⇒ 退役（净零）。

等价性设计（其余逐条落实）：
- **own-scope 组合**：own_scope_set_hash 进 key（同文件换 claim 范围不误命中）。
- **降级态**：准入 gate 均为无外部引擎依赖的纯扫描器，不存在降级路径；仍仅缓存
  passed=True（双保险）。
- **P2⑦ 不变**：``compute_fingerprint``/``Fingerprint`` 仍含 write-tree 树指纹
  与 HEAD_sha——那是锁外预跑+锁内 F′==F 重验的采信语义（git_commit_gateway
  专用），与本缓存键正交，本批未动其公式与调用面。

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/rule_bridge/gate_cache_preflight.yaml
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from zephyr.shared.utils.time_utils import now_utc  # RULE-SCHEMA-TZ：时间 SSoT（src 禁裸 time.time()）

#: P2⑧/P2⑦ 共享白名单＝实测命中台（依据：.runtime/audit/gate_execution_stats.jsonl
#: 24h 窗；准入判据见模块 docstring"白名单准入"节——判定输入面 ⊆ own staged∪own_scope
#: ∪manifest∪门实现，A3 矩阵逐台核过：head_dependent=false 或 HEAD 宽松单调
#: （added-lines 增量口径，先例=原 15 台中 8 台）、非信号型、非 CloneGuard 引擎依赖、
#: 非 lane 全图门、非 HEAD 严格面（条目集比对类））。
#:
#: 实证复用面（24h preflight_reused/cache_hit 计数，2026-09-25 量取）：ENCODING-SAFETY、
#: DATETIME-NOW-FORBIDDEN、NO-DOMAIN-NAME-ZH-DIRECT-ACCESS、NO-BARE-SQL、
#: NO-UPWARD-IMPORT、NO-IMPORT-SIDE-EFFECT、UNDEFINED-NAME、RELATIVE-PATH-LITERAL
#: （各 84 次）、UNSAFE-DICT-SPREAD、ASYNCIO-RUN-IN-CONTEXT（各 53 次）。
#: 实证耗时面（24h total_ms top，准入判据全绿）：BLUEPRINT-HEADER 1781s、
#: CH-BATCH-SIZE 872s、BLUEPRINT-FORMAT 725s、FILE-COPY 136s、NO-HARDCODED-URL
#: 124s。退役：NO-LONG-PARAM-LIST/NO-GOD-CLASS/NO-HIGH-COMPLEXITY（24h 零触发
#: 零消费且不在名册——死条目）。
#:
#: 扩容批（st-diskp0-20261015 总包 Z1 队 st-perfz1-20261015，24h 窗 75 链次
#: 2026-10-15 量取，逐台输入面审计后准入 16 台→总数 31）：
#: GIT-CALL-BUDGET 1960s、MUTABLE-CONST-WITHOUT-FINAL 1158s、CH-VERSION-COL 485s、
#: PERMANENT-SYSTEM-TRIGGER 740s、NO-SECRET-HARDCODE 578s、TDM-MOUNT-COVERAGE 468s、
#: NO-BARE-GETENV 379s、BLUEPRINT-NODE-ID-HARDCODE 372s、SSOT-REDEFINITION 345s、
#: DERIVATION-ANNOTATION 316s、TRANSLATION-COVERAGE 322s、OPEN-WITHOUT-WITH 313s、
#: FUNCTION-DUP、GATE-ERRCODE-CONSISTENCY、BARE-SUBPROCESS、ZEPHYR-ENV-DIRECT-ACCESS
#: ——全部 staged 面/注册表读取已声明 manifest（无注册表输入者清单留空）。
#: 驳回（登记在案，附理由）：REGISTRY-MASS-DELETION（HEAD 条目集严格面——HEAD 增
#: 条目场景缓存 pass=假绿，恰是本门存在意义的反面）；TEST-SOURCE-CONSISTENCY
#: （判定含 src 源码树存在性检查，非 manifest 可枚举）；DOC-HEADER-SUITE（子台
#: DOC-REF-BROKEN 探测全仓树链接目标）；REAL-KEY-REFERENCE-SCAN/FMS-HYGIENE/
#: COMPLEXITY-GUARD（_read_head_file 内容豁免面，无既有先例覆盖该类，保守不准入）；
#: DEPGRAPH-ENFORCEMENT（判定读 PG depgraph 库=全局可变态）；GATE-VOCAB（判定经
#: scripts/ checker，spec_sha 扫描根未覆盖+词表 glob 集不可枚举）。
CONTENT_SCAN_CACHE_WHITELIST: frozenset[str] = frozenset(
    {
        # ── 实证复用面（24h preflight_reused/cache_hit，2026-09-25）───────
        "ENCODING-SAFETY",
        "DATETIME-NOW-FORBIDDEN",
        "NO-DOMAIN-NAME-ZH-DIRECT-ACCESS",
        "NO-BARE-SQL",
        "NO-UPWARD-IMPORT",
        "NO-IMPORT-SIDE-EFFECT",
        "UNDEFINED-NAME",
        "RELATIVE-PATH-LITERAL",
        "UNSAFE-DICT-SPREAD",
        "ASYNCIO-RUN-IN-CONTEXT",
        # ── 实证耗时面（24h total_ms top，准入判据全绿，2026-09-25）──────
        "BLUEPRINT-HEADER",  # 1781s：蓝图头扫描（blueprint_amodule_consistency_gate._header_union_check）
        "CH-BATCH-SIZE",  # 872s：CH 批大小纯算规则
        "BLUEPRINT-FORMAT",  # 725s：[BLUEPRINT] 头格式正则
        "FILE-COPY",  # 136s：own 化后 extract 克隆薄封装（检测器异常 fail-open 不入缓存——只存 passed=True）
        "NO-HARDCODED-URL",  # 124s：URL 字面量正则
        # ── 扩容批（2026-10-15，24h 窗 75 链次，输入面逐台审计）─────────
        "GIT-CALL-BUDGET",  # 1960s：AST 检 added 行 git 调用反模式（added-lines 宽松单调，先例 8/15）
        "MUTABLE-CONST-WITHOUT-FINAL",  # 1158s：AST 纯扫描（零注册表输入）
        "PERMANENT-SYSTEM-TRIGGER",  # 740s：AST+头部 TTL 标扫描（零注册表输入）
        "NO-SECRET-HARDCODE",  # 578s：正则纯扫描（registry 仅注释提及，无实际读取）
        "CH-VERSION-COL",  # 485s：diff --cached 面扫描
        "TDM-MOUNT-COVERAGE",  # 468s：config/*_map.yaml own 面+豁免册已声明 manifest
        "NO-BARE-GETENV",  # 379s：AST 纯扫描
        "BLUEPRINT-NODE-ID-HARDCODE",  # 372s：检测器脚本已声明 manifest（spec_sha 不覆盖 scripts/ 面）
        "SSOT-REDEFINITION",  # 345s：REGISTRY_YAML 已声明 manifest
        "TRANSLATION-COVERAGE",  # 322s：module_translation_registry 已声明 manifest
        "DERIVATION-ANNOTATION",  # 316s：AST 纯扫描
        "OPEN-WITHOUT-WITH",  # 313s：AST 纯扫描
        "FUNCTION-DUP",  # own 集 AST 跨件判重（own_split 原语台）
        "GATE-ERRCODE-CONSISTENCY",  # error_code_registry.yaml 已声明 manifest
        "BARE-SUBPROCESS",  # AST 纯扫描
        "ZEPHYR-ENV-DIRECT-ACCESS",  # AST 纯扫描
    }
)

#: 门级输入清单（T7/B2 判失红测的机制面）：gate_id → 该门判定所读、且不在
#: own staged 集合内的注册表/配置/检测器脚本文件（仓库相对 posix 路径）。清单内
#: 文件的工作树字节哈希进键 ⇒ 注册表/脚本字节篡改一字节即 miss。
#: 原批 15 台全部为纯 staged 扫描器（无注册表输入）⇒ 清单空置；扩容批
#: （2026-10-15）注册表读取类门按白名单准入判据机械前置逐台声明如下；
#: 未声明者不准入。
GATE_INPUT_MANIFEST: dict[str, tuple[str, ...]] = {
    "SSOT-REDEFINITION": ("docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",),
    "TRANSLATION-COVERAGE": ("docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml",),
    "GATE-ERRCODE-CONSISTENCY": ("architecture_model/contracts/error_code_registry.yaml",),
    "TDM-MOUNT-COVERAGE": ("config/tdm_mount_exemption_registry.yaml",),
    # 检测逻辑 SSoT 在 scripts/ 面（spec_sha 扫描根=src/.../commit_gates 不覆盖），
    # 检测器脚本字节进键防"脚本改了缓存不失效"。
    "BLUEPRINT-NODE-ID-HARDCODE": ("scripts/governance/d3_metadata/check_doc_node_id_hardcode.py",),
}

_CACHE_DIR = ".runtime/gate_cache"
_TTL_SECONDS = 600.0  # 方案 §2.2-A3：TTL 10min

#: 门实现面（spec_sha 的扫描根）：全部门实现+共享 helper 所在包目录。
#: 门源码一字节篡改 ⇒ spec_sha 变 ⇒ 全缓存判失（内容哈希语义自证）。
_GATE_SPEC_DIR = Path("src") / "zephyr" / "gov_enforcement" / "commit_gates"

_RESULT_FLAG = "gate_result_cache"
_PREFLIGHT_FLAG = "gate_preflight"


def flag_enabled(flag_name: str) -> bool:
    """flag 读取唯一点（fail-closed OFF；与 _commit_queue_serializer_enabled 同款语义）。"""
    try:
        from zephyr.shared.foundation.flags import (  # noqa: PLC0415
            ensure_global_flags_loaded,
            global_flag_registry,
        )

        ensure_global_flags_loaded()
        return global_flag_registry.is_enabled(flag_name, default=False)
    except Exception:  # noqa: BLE001 — 设施异常 fail-closed OFF
        return False


def result_cache_enabled() -> bool:
    return flag_enabled(_RESULT_FLAG)


def preflight_enabled() -> bool:
    return flag_enabled(_PREFLIGHT_FLAG)


@dataclass(frozen=True)
class Fingerprint:
    """P2⑦ 预跑采信指纹（方案 §2.3 F 四元组的本实现收敛形态）——公式未动。

    staged_tree_sha=git write-tree（index 逐字节敏感）；head_sha=diff 基线；
    flags_mtime=配置变更失效。仅服务 git_commit_gateway 的"锁外预跑+锁内
    F′==F 重验采信"路径（T7/B2 未触碰）；P2⑧ 持久缓存键已与本指纹解耦
    （键见 ``GateResultCache._path``——全局态不得进键）。
    """

    staged_tree_sha: str
    head_sha: str
    flags_mtime: float

    def matches(self, other: Fingerprint) -> bool:
        return (
            self.staged_tree_sha == other.staged_tree_sha
            and self.head_sha == other.head_sha
            and self.flags_mtime == other.flags_mtime
        )


def compute_fingerprint(gateway) -> Fingerprint | None:
    """计算当前 staged 树/HEAD 指纹（P2⑦ 专用）；任何 git 异常返回 None。"""
    try:
        tree = gateway.run_git(["git", "write-tree"])
        if tree.returncode != 0:
            return None
        head = gateway.run_git(["git", "rev-parse", "HEAD"])
        if head.returncode != 0:
            return None
        return Fingerprint(
            staged_tree_sha=tree.stdout.strip(),
            head_sha=head.stdout.strip(),
            flags_mtime=_flags_mtime(gateway),
        )
    except Exception:  # noqa: BLE001 — 指纹失败=回退全量现算（绝不阻断）
        return None


def _flags_mtime(gateway) -> float:
    """config/flags.yaml mtime（读不到=0.0，确定性退化）。"""
    try:
        return os.path.getmtime(Path(gateway.project_root) / "config" / "flags.yaml")
    except OSError:
        return 0.0


def _own_content_hash(gateway, files: list[str]) -> str | None:
    """own 文件的 staged blob sha 合集哈希（T7/B2 键的 inputs_sha 分量）。

    一次 ``git ls-files -s -z`` 批量取全部 own 文件的 index blob sha（N 文件
    1 次 spawn，替代逐文件 N 次），排序后合集哈希。own 内容一字节变化 ⇒ 本值
    变化 ⇒ miss。任何异常返回 None ⇒ 缓存整体不可用（fail-safe 回退全量现算，
    绝不阻断）。
    """
    try:
        uniq = sorted({str(x).replace("\\", "/") for x in files})
        if not uniq:
            return hashlib.sha256(b"").hexdigest()
        r = gateway.run_git(["git", "ls-files", "-s", "-z", "--", *uniq])
        if r.returncode != 0:
            return None
        sha_by_path: dict[str, str] = {}
        for entry in r.stdout.split("\0"):
            if not entry:
                continue
            meta, _, path = entry.partition("\t")  # 形态: mode blob_sha stage\tpath
            parts = meta.split()
            if len(parts) >= 2 and path not in sha_by_path:  # 同路径多 stage 取首
                sha_by_path[path] = parts[1]
        specs = [sha_by_path.get(f, "") for f in uniq]
        return hashlib.sha256("\n".join(specs).encode("utf-8", "replace")).hexdigest()
    except Exception:  # noqa: BLE001 — fail-safe 回退现算
        return None


def _spec_sha(gateway) -> str | None:
    """门实现面内容哈希（T7/B2 键的 spec_sha 分量）。

    对 ``src/zephyr/gov_enforcement/commit_gates/**.py`` 逐文件取（相对路径,
    字节）排序后合集哈希——门源码/共享 helper 一字节篡改 ⇒ 下次必 miss
    （内容哈希语义自证）。实测 122 文件 ~17ms/链（替代旧键的 write-tree+
    rev-parse 两次 git spawn）。扫描异常返回 None ⇒ 缓存整体不可用（fail-safe）。
    """
    try:
        root = Path(gateway.project_root) / _GATE_SPEC_DIR
        h = hashlib.sha256()
        if root.is_dir():
            for p in sorted(root.rglob("*.py")):
                h.update(p.relative_to(root).as_posix().encode("utf-8", "replace"))
                h.update(p.read_bytes())
        return h.hexdigest()
    except Exception:  # noqa: BLE001 — fail-safe 回退现算
        return None


def _manifest_inputs_sha(gateway, gate_id: str) -> str | None:
    """GATE_INPUT_MANIFEST 声明文件的工作树字节合集哈希（注册表判失分量）。

    注册表/配置文件门从工作树磁盘读（非 index），故按文件字节哈希；文件缺失
    以确定性标记参与哈希（删除也是篡改）。异常返回 None ⇒ 缓存整体不可用。
    """
    try:
        declared = GATE_INPUT_MANIFEST.get(gate_id, ())
        if not declared:
            return hashlib.sha256(b"").hexdigest()
        root = Path(gateway.project_root)
        h = hashlib.sha256()
        for rel in sorted({str(x).replace("\\", "/") for x in declared}):
            h.update(rel.encode("utf-8", "replace"))
            try:
                h.update((root / rel).read_bytes())
            except OSError:
                h.update(b"<missing>")
        return h.hexdigest()
    except Exception:  # noqa: BLE001 — fail-safe 回退现算
        return None


def own_scope_hash(gateway, files: list[str]) -> str:
    """own_scope 集合指纹（files∪session held_files；与 _diff_helpers._build_own_scope 同源语义）。"""
    try:
        from zephyr.gov_enforcement.commit_gates._diff_helpers import _build_own_scope

        scope = _build_own_scope(gateway, files)
    except Exception:  # noqa: BLE001 — own_scope 不可得=退化用 files 本身
        scope = list(files)
    return hashlib.sha256("\n".join(sorted(scope)).encode("utf-8", "replace")).hexdigest()


class GateResultCache:
    """P2⑧ 持久结果缓存（.runtime/gate_cache/，TTL 10min，只存 passed=True）。

    T7/B2 键＝「门实际读什么」：gate_id × own_scope × own 内容(inputs_sha) ×
    spec_sha × manifest 输入哈希 × flags_mtime。禁含 HEAD 与共享暂存树状态
    （旧键两项全局量是 87 命中/24h 的结构性病根，红证在判别测试）。
    """

    def __init__(self, gateway, files: list[str]) -> None:
        self._gateway = gateway
        self._own_content_sha = _own_content_hash(gateway, files)
        self._spec_sha = _spec_sha(gateway)
        self._flags_mtime = _flags_mtime(gateway)
        root = Path(gateway.project_root) / _CACHE_DIR
        self._dir: Path | None = root if self._own_content_sha is not None and self._spec_sha is not None else None

    @property
    def usable(self) -> bool:
        return self._dir is not None

    def _path(self, gate_id: str, own_scope: str) -> Path:
        # T7/B2（st-commitspeed-tbl-20260924）：键=门判定输入面的内容哈希。
        # 旧键 staged_tree_sha/head_sha 两全局量——write-tree 对共享 index 逐字节
        # 敏感、HEAD 任何人可推 ⇒ 他人一切活动作废我的缓存（87 命中/24h 病根）。
        # 等价性：白名单门全是纯 staged 扫描器（A3 矩阵逐台核过），判定输入=
        # own staged 内容∪own_scope 集合∪manifest 声明文件∪门实现本身——键收敛
        # 到输入面=等价而非放松。包9 immutable_tree ON 时本件文件集=不可变树，
        # inputs_sha 天然稳定；OFF 时退化按 inputs_sha 仍命中（读集哈希不含共享
        # 树状态）。
        manifest_sha = _manifest_inputs_sha(self._gateway, gate_id)
        if manifest_sha is None:
            # 逐门清单不可得=该门缓存条目不可信：落不可能命中的键位
            # （lookup 恒 None、store 写入永不命中位）——不污染其它门条目。
            manifest_sha = "unavailable"
        key = hashlib.sha256(
            f"{gate_id}\x1e{own_scope}\x1e{self._own_content_sha}\x1e"
            f"{self._spec_sha}\x1e{manifest_sha}\x1e{self._flags_mtime}".encode()
        ).hexdigest()
        return self._dir / f"{key}.json"  # type: ignore[union-attr]

    def lookup(self, gate_id: str, own_scope: str) -> str | None:
        """命中返回缓存 detail（passed=True）；未命中/过期/异常返回 None。"""
        if not self.usable:
            return None
        p = self._path(gate_id, own_scope)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if now_utc().timestamp() - float(data["ts"]) > _TTL_SECONDS:
                return None
            return str(data["detail"])
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def store(self, gate_id: str, own_scope: str, detail: str) -> None:
        if not self.usable:
            return
        p = self._path(gate_id, own_scope)
        try:
            self._dir.mkdir(parents=True, exist_ok=True)  # type: ignore[union-attr]
            p.write_text(
                json.dumps(
                    {"gate_id": gate_id, "detail": detail, "ts": now_utc().timestamp()},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass  # 缓存写失败永不影响主链路
