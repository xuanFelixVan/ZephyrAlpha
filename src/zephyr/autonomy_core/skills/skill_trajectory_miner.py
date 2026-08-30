# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_trajectory_miner
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.file_utils; zephyr.shared.io.paths
# [CONSUMERS] tests/skill/test_skill_trajectory_miner.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 空输入优雅降级（empty_input，不抛异常不落盘）；仅 status ∈ {supported, verified, completed} 的记录入矿；草稿一律 unverified_draft 态且只落 output_dir（默认 .runtime/skill_drafts/），禁写生产 skills/ 目录与 skill-registry.yaml；候选草稿与退役指纹相似度 >0.90 拒绝生成并记录拒绝理由；退役指纹库/假设落盘损坏 fail-fast 不静默兜底；落盘原子写（tmp+os.replace）
# [MODIFY-GUARD] tests/skill/test_skill_trajectory_miner.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SkillTrajectoryMinerError(ZA-AC-0008)——契约违反（空陈述/非法记录类型/草稿不存在）与落盘损坏 fail-fast
# [TESTS] tests/skill/test_skill_trajectory_miner.py
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""轨迹挖掘器（Skill Trajectory Miner）——技能库自动生成路径 MVP 第一段（11号文 §4.4 P2-1）。

职责：研究轨迹/已验证假设 → 聚类归纳 → 技能草稿（SKILL.md 渐进披露三级格式）。
MVP 边界（11号文 §3.2 自动生成路径的第一段，后续段复用既有设施不新建）：
    轨迹挖掘→技能草稿（本件）→ skill_sandbox 沙箱测试（复用）→ backtest 回测
    验证门（复用）→ 人工门 → skill_constructor 式入库（复用）。本件只产"未验证"
    草稿落 .runtime/skill_drafts/（易失区，人工门禁卫），不落生产库。

输入契约（TrajectoryRecord）：record_id / statement / status / tags / steps /
regime / source。真源输入 = HypothesisRegistry 落盘 data/research/evidence/
hypotheses.json 中 status=supported 的假设（load_supported_hypotheses 加载；
磁盘实测该数据尚未积累时返回空表，mine([]) 优雅降级）。

SKILL.md 渐进披露三级格式（设计参数真源 11号文 §3.2）：
    Discovery（~100-200 tokens）name+description+triggers+outputs——检索级；
    Activation（<5000 tokens）instructions+constraints——命中加载级；
    Execution（不计入上下文）references+scripts——执行按需级。

退役指纹库（11号文 §3.2：相似度 >90% 拒绝重注册，防已淘汰能力换皮复活）：
    MVP 实现 = 规范化文本 SHA-256 指纹 + 字符 bigram Jaccard 相似度；
    指纹 JSON 落盘（默认 .runtime/skill_drafts/retired_fingerprints.json——
    MVP 落点，≥1 年保留期的正式落点待裁定后迁 data/ 持久区）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 轨迹/假设记录序列（内存契约）或 supported 假设落盘
#   fields: TrajectoryRecord(record_id/statement/status/tags/steps/regime/source)
#   code: mine(records) / load_supported_hypotheses(store_dir)
# - id: I2
#   name: 退役指纹库 retired_fingerprints.json（构造时加载）
#   fields: fingerprints[](fingerprint_id/name/text/bigrams/retired_at/reason)
#   code: RetiredFingerprintStore._load（损坏 fail-fast ZA-AC-0008）
# 层: 算法
# - id: A1
#   name_zh: ① 契约校验+适格过滤
#   name_en: validate + filter
#   desc: 空陈述/非法记录类型即 ZA-AC-0008；仅 ELIGIBLE_STATUSES 入矿，其余跳过
#   inputs: I1
#   outputs: 适格记录序列
# - id: A2
#   name_zh: ② 贪心聚类
#   name_en: _cluster
#   desc: 逐条与既有簇质心算 bigram Jaccard，≥0.25 入簇否则开新簇
#   inputs: A1
#   outputs: 簇列表
# - id: A3
#   name_zh: ③ 簇归纳草稿+指纹查重门
#   name_en: _induce_draft + fingerprint gate
#   desc: 公共标签→condition/triggers；steps 保序去重→action/instructions；首条陈述→effect/outputs；候选文本查退役指纹库，>0.90 拒生成记 rejected
#   inputs: A2 + I2
#   outputs: SkillDraft 或 rejection
# - id: A4
#   name_zh: ④ 原子落盘
#   name_en: _write_draft + _write_manifest
#   desc: 草稿 SKILL.md（三级格式+unverified_draft 标注）与 manifest.json 经 atomic_write 落 output_dir
#   inputs: A3
#   outputs: 落盘文件
# 层: 输出
# - id: O1
#   name_zh: 挖掘结果视图
#   name_en: mine 返回值
#   downstream: tests/skill/test_skill_trajectory_miner.py；人工门（消费 .runtime/skill_drafts/manifest.json）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# I2 --> A3
# A3 --> A4
# A4 --> O1

依据: 11号文 §3.2/§4.4 P2-1 + aiarch 清单 2.7（MOD-INF-059）
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.file_utils import atomic_write
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "ACTIVATION_TOKEN_BUDGET",
    "CLUSTER_SIMILARITY_THRESHOLD",
    "DEFAULT_FINGERPRINT_PATH",
    "DEFAULT_OUTPUT_DIR",
    "DISCOVERY_TOKEN_BUDGET",
    "DRAFT_STATUS",
    "SIMILARITY_THRESHOLD",
    "RetiredFingerprintStore",
    "SkillTrajectoryMiner",
    "SkillTrajectoryMinerError",
    "TrajectoryRecord",
    "estimate_tokens",
    "validate_skill_md",
]

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约（ZA-AC-0008）
# ============================================================================


class SkillTrajectoryMinerError(ZephyrBaseError):
    """ZA-AC-0008: 轨迹挖掘器基础错误（契约违反/落盘损坏 fail-fast）。"""

    error_code = "ZA-AC-0008"


# ============================================================================
# 2. 常量
# ============================================================================

#: 中国标准时间（无夏令时）——落盘时间戳统一口径（同 research.evidence 族）
CST: Final = timezone(timedelta(hours=8))

#: 默认草稿输出根（.runtime 易失区——人工门禁卫，不落生产库；理由见模块 docstring）
DEFAULT_OUTPUT_DIR: Final[Path] = REPO_ROOT / ".runtime" / "skill_drafts"
#: 默认退役指纹库落盘（MVP 落点；≥1 年保留期的正式落点待裁定后迁 data/ 持久区）
DEFAULT_FINGERPRINT_PATH: Final[Path] = DEFAULT_OUTPUT_DIR / "retired_fingerprints.json"
#: supported 假设真源落盘（HypothesisRegistry，GP0 已 production）
DEFAULT_HYPOTHESIS_STORE_DIR: Final[Path] = REPO_ROOT / "data" / "research" / "evidence"

SCHEMA_VERSION: Final = "1.0.0"
DRAFT_STATUS: Final = "unverified_draft"

#: 退役指纹拒绝阈值（11号文 §3.2：相似度 >90% 拒绝注册）
SIMILARITY_THRESHOLD: Final = 0.90
#: 聚类阈值（字符 bigram Jaccard；短文本经验值，同族记录实测 ~0.7、异族 ~0.05）
CLUSTER_SIMILARITY_THRESHOLD: Final = 0.25
#: 渐进披露 token 预算（11号文 §3.2：Discovery ~100-200 / Activation <5000）
DISCOVERY_TOKEN_BUDGET: Final = 200
ACTIVATION_TOKEN_BUDGET: Final = 5000

#: 入矿适格状态（hypothesis: supported；trajectory: verified/completed）
ELIGIBLE_STATUSES: Final = frozenset({"supported", "verified", "completed"})

_CJK_RE: Final = re.compile(r"[一-鿿㐀-䶿豈-﫿]")
_LATIN_WORD_RE: Final = re.compile(r"[A-Za-z0-9_]+")
_WS_RE: Final = re.compile(r"\s+")
_NON_TEXT_RE: Final = re.compile(r"[^0-9A-Za-z一-鿿㐀-䶿豈-﫿]+")
_SLUG_RE: Final = re.compile(r"[^a-z0-9-]+")


def _now_iso() -> str:
    return datetime.now(CST).isoformat()


def estimate_tokens(text: str) -> int:
    """中英混合 token 粗估：CJK 字符 1 字≈1 token，拉丁词按词计。"""
    cjk = len(_CJK_RE.findall(text))
    latin = len(_LATIN_WORD_RE.findall(_CJK_RE.sub(" ", text)))
    return cjk + latin


def _normalize(text: str) -> str:
    """指纹/相似度用规范化：小写、去标点、折叠空白。"""
    return _WS_RE.sub(" ", _NON_TEXT_RE.sub(" ", text.lower())).strip()


def _bigrams(text: str) -> frozenset[str]:
    """字符 bigram 集（中英通吃的文本相似度 MVP 底座）。"""
    compact = _normalize(text).replace(" ", "")
    if len(compact) < 2:
        return frozenset({compact}) if compact else frozenset()
    return frozenset(compact[i : i + 2] for i in range(len(compact) - 1))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _fingerprint_of(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()[:16]


# ============================================================================
# 3. 输入契约
# ============================================================================


@dataclass(frozen=True)
class TrajectoryRecord:
    """轨迹/假设记录（输入契约——真实数据待积累，见模块 docstring）。

    Attributes:
        record_id: 记录 ID（假设 HYP-%04d 或轨迹 ID）。
        statement: 陈述/结论（必填非空白）。
        status: 生命周期状态；仅 ELIGIBLE_STATUSES 入矿。
        tags: 主题标签（聚类与 triggers 归纳原料）。
        steps: 验证过程步骤（instructions 归纳原料）。
        regime: 市场制度（可选；簇内一致时进 triggers）。
        source: 来源标识（hypothesis/trajectory 等，追溯用）。
    """

    record_id: str
    statement: str
    status: str = "supported"
    tags: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    regime: str = ""
    source: str = "hypothesis"


# ============================================================================
# 4. 退役指纹库
# ============================================================================


class RetiredFingerprintStore:
    """退役指纹库（MVP：JSON 落盘 + bigram Jaccard 相似度查重）。

    Args:
        path: 指纹库 JSON 路径；损坏 fail-fast（ZA-AC-0008），不存在按空库引导。
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return  # fresh boot：空库
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            entries = payload["fingerprints"]
            if not isinstance(entries, list):
                raise TypeError("fingerprints 非列表")
        except SkillTrajectoryMinerError:
            raise
        except Exception as exc:  # JSONDecodeError/KeyError/TypeError
            raise SkillTrajectoryMinerError(
                f"退役指纹库落盘损坏，fail-fast（不静默兜底为空库）: {self._path}",
                details={"path": str(self._path), "cause": repr(exc)},
            ) from exc
        self._entries = [dict(e) for e in entries]

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": SCHEMA_VERSION, "fingerprints": self._entries}
        atomic_write(self._path, json.dumps(payload, ensure_ascii=False, indent=2))

    def add(self, *, name: str, text: str, reason: str = "", retired_at: str | None = None) -> dict[str, Any]:
        """归档一条退役指纹（同 fingerprint_id 幂等更新理由）。"""
        entry = {
            "fingerprint_id": _fingerprint_of(text),
            "name": name,
            "text": _normalize(text),
            "bigrams": sorted(_bigrams(text)),
            "retired_at": retired_at or _now_iso(),
            "reason": reason,
        }
        self._entries = [e for e in self._entries if e["fingerprint_id"] != entry["fingerprint_id"]]
        self._entries.append(entry)
        self._save()
        log.info("退役指纹归档 %s（%s）", entry["fingerprint_id"], name)
        return entry

    def find_similar(self, text: str, threshold: float = SIMILARITY_THRESHOLD) -> tuple[dict[str, Any], float] | None:
        """查重：返回 (最相似指纹条目, 相似度)；相似度 > threshold 才命中。"""
        cand = _bigrams(text)
        best: tuple[dict[str, Any], float] | None = None
        for entry in self._entries:
            sim = _jaccard(cand, frozenset(entry["bigrams"]))
            if sim > threshold and (best is None or sim > best[1]):
                best = (entry, sim)
        return best

    def entries(self) -> list[dict[str, Any]]:
        return [dict(e) for e in self._entries]


# ============================================================================
# 5. SKILL.md 三级格式校验
# ============================================================================


def _split_level_sections(content: str) -> dict[str, str]:
    """按 `## ` 节切分（key=节标题首词，如 Discovery/Activation/Execution）。"""
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in content.split("\n"):
        m = re.match(r"^##\s+(\S+)", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def validate_skill_md(
    content: str,
    *,
    discovery_budget: int = DISCOVERY_TOKEN_BUDGET,
    activation_budget: int = ACTIVATION_TOKEN_BUDGET,
) -> dict[str, Any]:
    """SKILL.md 渐进披露三级格式校验（11号文 §3.2 格式与 token 预算）。"""
    issues: list[str] = []
    fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm:
        issues.append("frontmatter 缺失")
    else:
        if "name:" not in fm.group(1):
            issues.append("frontmatter 缺 name")
        if "status:" not in fm.group(1):
            issues.append("frontmatter 缺 status")

    sections = _split_level_sections(content)
    for level in ("Discovery", "Activation", "Execution"):
        if level not in sections:
            issues.append(f"缺 {level} 节（三级渐进披露格式不全）")

    tokens: dict[str, int] = {}
    if "Discovery" in sections:
        tokens["discovery"] = estimate_tokens(sections["Discovery"])
        if tokens["discovery"] > discovery_budget:
            issues.append(
                f"Discovery 超 token 预算: {tokens['discovery']} > {discovery_budget}"
            )
    if "Activation" in sections:
        tokens["activation"] = estimate_tokens(sections["Activation"])
        if tokens["activation"] > activation_budget:
            issues.append(
                f"Activation 超 token 预算: {tokens['activation']} > {activation_budget}"
            )
    return {"valid": not issues, "issues": issues, "tokens": tokens}


# ============================================================================
# 6. 轨迹挖掘器
# ============================================================================


class SkillTrajectoryMiner:
    """轨迹挖掘器——研究轨迹/已验证假设 → 聚类归纳 → SKILL.md 草稿（未验证态）。

    Args:
        output_dir: 草稿输出目录；None → .runtime/skill_drafts/。
        fingerprint_store_path: 退役指纹库路径；None → output 默认位。
        similarity_threshold: 退役指纹拒绝阈值（默认 0.90，11号文 §3.2）。
        cluster_threshold: 聚类相似度阈值（默认 0.25）。
    """

    def __init__(
        self,
        output_dir: Path | str | None = None,
        fingerprint_store_path: Path | str | None = None,
        *,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        cluster_threshold: float = CLUSTER_SIMILARITY_THRESHOLD,
    ) -> None:
        self._output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
        self._fingerprint_store = RetiredFingerprintStore(
            fingerprint_store_path if fingerprint_store_path is not None else DEFAULT_FINGERPRINT_PATH
        )
        self._similarity_threshold = similarity_threshold
        self._cluster_threshold = cluster_threshold

    # ── 属性 ──────────────────────────────────────────────────────────────

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    @property
    def fingerprint_store(self) -> RetiredFingerprintStore:
        return self._fingerprint_store

    # ── 真源加载 ──────────────────────────────────────────────────────────

    def load_supported_hypotheses(self, store_dir: Path | str | None = None) -> list[TrajectoryRecord]:
        """加载 HypothesisRegistry 落盘中 status=supported 的假设为输入记录。

        数据尚未积累（hypotheses.json 不存在）时返回空表——优雅降级，不抛异常；
        落盘损坏 fail-fast（ZA-AC-0008，不静默兜底）。
        """
        store = Path(store_dir) if store_dir is not None else DEFAULT_HYPOTHESIS_STORE_DIR
        path = store / "hypotheses.json"
        if not path.exists():
            log.info("supported 假设落盘不存在（数据待积累），按空输入降级: %s", path)
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows = payload["hypotheses"]
        except Exception as exc:
            raise SkillTrajectoryMinerError(
                f"supported 假设落盘损坏，fail-fast: {path}",
                details={"path": str(path), "cause": repr(exc)},
            ) from exc
        records: list[TrajectoryRecord] = []
        for row in rows:
            if row.get("status") != "supported":
                continue
            notes = str(row.get("notes", ""))
            steps = tuple(s.strip() for s in re.split(r"[\n；;]", notes) if s.strip())
            records.append(
                TrajectoryRecord(
                    record_id=str(row.get("hypothesis_id", "")),
                    statement=str(row.get("statement", "")),
                    status="supported",
                    tags=tuple(str(t) for t in row.get("tags", [])),
                    steps=steps,
                    source="hypothesis",
                )
            )
        return records

    # ── 主流程 ────────────────────────────────────────────────────────────

    def mine(self, records: list[TrajectoryRecord] | tuple[TrajectoryRecord, ...]) -> dict[str, Any]:
        """挖掘主入口：契约校验 → 适格过滤 → 聚类 → 归纳+查重 → 落盘。

        空输入/全量不适格 → {"status": "empty_input", ...} 优雅降级（不落盘）。
        """
        eligible: list[TrajectoryRecord] = []
        for r in records:
            if not isinstance(r, TrajectoryRecord):
                raise SkillTrajectoryMinerError(
                    f"非法记录类型（契约要求 TrajectoryRecord）: {type(r).__name__}",
                    details={"type": type(r).__name__},
                )
            if not r.statement or not r.statement.strip():
                raise SkillTrajectoryMinerError(
                    f"轨迹/假设记录陈述为空——契约违反（statement 必填非空白）: {r.record_id}",
                    details={"record_id": r.record_id},
                )
            if r.status in ELIGIBLE_STATUSES:
                eligible.append(r)

        if not eligible:
            return {"status": "empty_input", "clusters": 0, "drafts": [], "rejected": []}

        clusters = self._cluster(eligible)
        drafts: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        for cluster in clusters:
            draft = self._induce_draft(cluster)
            hit = self._fingerprint_store.find_similar(
                draft["canonical_text"], self._similarity_threshold
            )
            if hit is not None:
                entry, sim = hit
                rejected.append(
                    {
                        "name": draft["name"],
                        "fingerprint_id": entry["fingerprint_id"],
                        "similarity": round(sim, 4),
                        "reason": (
                            f"与退役指纹 {entry['fingerprint_id']}（{entry['name']}）"
                            f"相似度 {sim:.2%} > {self._similarity_threshold:.0%}——"
                            "退役能力换皮复活拒绝重注册（11号文 §3.2 退役指纹规则）"
                        ),
                        "source_records": draft["source_records"],
                    }
                )
                log.info("草稿 %s 命中退役指纹 %s（%.2f），拒绝生成", draft["name"], entry["fingerprint_id"], sim)
                continue
            rel_path = self._write_draft(draft)
            drafts.append(
                {
                    "draft_id": draft["draft_id"],
                    "name": draft["name"],
                    "path": rel_path,
                    "fingerprint": draft["fingerprint"],
                    "source_records": draft["source_records"],
                    "status": DRAFT_STATUS,
                    "canonical_text": draft["canonical_text"],
                }
            )

        self._write_manifest(drafts, rejected)
        return {
            "status": "mined",
            "clusters": len(clusters),
            "drafts": drafts,
            "rejected": rejected,
        }

    def retire_draft(self, draft_id: str, *, reason: str = "") -> dict[str, Any]:
        """草稿退役：指纹归档入退役指纹库（后续同能力重挖掘将被 >90% 门拒绝）。"""
        manifest = self._load_manifest()
        for d in manifest.get("drafts", []):
            if d["draft_id"] == draft_id:
                return self._fingerprint_store.add(
                    name=d["name"], text=d["canonical_text"], reason=reason
                )
        raise SkillTrajectoryMinerError(
            f"草稿不存在（无法退役）: {draft_id}",
            details={"draft_id": draft_id, "manifest": str(self._output_dir / "manifest.json")},
        )

    # ── 聚类与归纳 ────────────────────────────────────────────────────────

    @staticmethod
    def _record_text(r: TrajectoryRecord) -> str:
        return " ".join([r.statement, " ".join(r.tags), " ".join(r.steps), r.regime])

    def _cluster(self, records: list[TrajectoryRecord]) -> list[dict[str, Any]]:
        """贪心单遍聚类：与簇质心 bigram Jaccard ≥ 阈值入簇，否则开新簇。"""
        clusters: list[dict[str, Any]] = []
        for r in records:
            grams = _bigrams(self._record_text(r))
            best_sim, best_cluster = 0.0, None
            for c in clusters:
                sim = _jaccard(grams, c["centroid"])
                if sim > best_sim:
                    best_sim, best_cluster = sim, c
            if best_cluster is not None and best_sim >= self._cluster_threshold:
                best_cluster["records"].append(r)
                best_cluster["centroid"] |= grams
            else:
                clusters.append({"records": [r], "centroid": grams})
        return clusters

    def _induce_draft(self, cluster: dict[str, Any]) -> dict[str, Any]:
        """簇 → 技能三元组（condition/triggers，action/instructions，effect/outputs）草稿。"""
        records: list[TrajectoryRecord] = cluster["records"]
        tag_sets = [set(r.tags) for r in records]
        common_tags = sorted(set.intersection(*tag_sets)) if all(tag_sets) else []
        regimes = {r.regime for r in records if r.regime}
        regime = regimes.pop() if len(regimes) == 1 else ""
        steps = list(dict.fromkeys(s for r in records for s in r.steps))  # 保序去重
        statements = [r.statement.strip() for r in records]

        canonical_text = " ".join(
            [" ".join(common_tags), " ".join(statements), " ".join(steps), regime]
        )
        fingerprint = _fingerprint_of(canonical_text)
        draft_id = f"SKILL-DRAFT-{fingerprint[:8].upper()}"
        name = self._draft_name(common_tags, fingerprint)
        description = f"从 {len(records)} 条已验证研究记录归纳：{statements[0][:80]}"
        triggers = [*common_tags, *([f"regime:{regime}"] if regime else [])]
        return {
            "draft_id": draft_id,
            "name": name,
            "description": description,
            "triggers": triggers,
            "outputs": statements[:3],
            "instructions": steps,
            "source_records": [f"{r.source}:{r.record_id}" for r in records],
            "fingerprint": fingerprint,
            "canonical_text": canonical_text,
        }

    @staticmethod
    def _draft_name(common_tags: list[str], fingerprint: str) -> str:
        if common_tags:
            base = _SLUG_RE.sub("-", "-".join(common_tags[:3]).lower()).strip("-")
            return f"{base}-pattern"
        return f"mined-pattern-{fingerprint[:6]}"

    # ── 落盘 ──────────────────────────────────────────────────────────────

    def _write_draft(self, draft: dict[str, Any]) -> str:
        draft_dir = self._output_dir / draft["draft_id"]
        draft_dir.mkdir(parents=True, exist_ok=True)
        content = self._render_skill_md(draft)
        atomic_write(draft_dir / "SKILL.md", content)
        return f"{draft['draft_id']}/SKILL.md"

    def _render_skill_md(self, draft: dict[str, Any]) -> str:
        instructions = (
            "\n".join(f"{i}. {s}" for i, s in enumerate(draft["instructions"], 1))
            if draft["instructions"]
            else "1. _待人工门补全执行步骤（验证过程未记录 steps）_"
        )
        triggers = ", ".join(draft["triggers"]) if draft["triggers"] else "_待人工门补全_"
        outputs = "\n".join(f"- {o}" for o in draft["outputs"])
        references = "\n".join(f"- {src}" for src in draft["source_records"])
        constraints = "\n".join(
            f"- {c}"
            for c in (
                "本草稿为未验证态（unverified_draft），禁止生产加载",
                "入库前必须依次通过：skill_sandbox 沙箱测试 → backtest 回测验证门 → 人工门（11号文 §3.2）",
                "验证通过前不得接入交易链路（金融安全硬边界）",
            )
        )
        return f"""---
skill_id: {draft['draft_id']}
name: {draft['name']}
description: {draft['description']}
status: {DRAFT_STATUS}
generated_by: skill_trajectory_miner
generated_at: {_now_iso()}
version: 0.1.0
---

# {draft['name']}

> ⚠️ 未验证草稿——禁止生产加载。入库须过沙箱测试→回测验证门→人工门（11号文 §3.2/§4.4）。

## Discovery
<!-- L1 检索级（~100-200 tokens）：name + description + triggers + outputs -->
- description: {draft['description']}
- triggers: {triggers}
- outputs:
{outputs}

## Activation
<!-- L2 命中加载级（<5000 tokens）：instructions + constraints -->
### Instructions
{instructions}

### Constraints
{constraints}

## Execution
<!-- L3 执行级（按需读取，不计入上下文）：references + scripts -->
### References
{references}

### Scripts
- _待人工门补全_

---
_由 SkillTrajectoryMiner 归纳生成；来源记录：{', '.join(draft['source_records'])}_
"""

    def _write_manifest(self, drafts: list[dict[str, Any]], rejected: list[dict[str, Any]]) -> None:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "similarity_threshold": self._similarity_threshold,
            "drafts": drafts,
            "rejected": rejected,
        }
        atomic_write(
            self._output_dir / "manifest.json",
            json.dumps(payload, ensure_ascii=False, indent=2),
        )

    def _load_manifest(self) -> dict[str, Any]:
        path = self._output_dir / "manifest.json"
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SkillTrajectoryMinerError(
                f"草稿 manifest 落盘损坏，fail-fast: {path}",
                details={"path": str(path), "cause": repr(exc)},
            ) from exc
