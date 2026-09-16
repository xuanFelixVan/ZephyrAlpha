# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.integrity
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.agent_signer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分期验证(2026-09-16)禁 try-all——era 范围外的钥验过视为失配；强分期钥不可解析 fail-loud 判 mismatch；lost 分期计 known_loss 不判 compromised；显式传 hmac_key 保持单钥语义
# [MODIFY-GUARD] era 语义变更须同步 config/audit_key_eras.yaml 头注三硬规则+tests/governance/audit/test_key_era_verification.py（含红蓝攻击用例）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/audit/test_key_era_verification.py; tests/audit/audit_core/test_audit_integrity.py; tests/audit/audit_core/test_audit_adversarial.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit-trail.integrity — MOD-INF-020 · 密码学完整性验证器
===========================================================
蓝图 §5 · 哈希链验证 + HMAC验证 + Agent签名验证 + Merkle树聚合 (§2.2)

算法
----
  - 链式验证: 逐条验证 prev_entry_hash == SHA-256(上一条事件)
  - HMAC 验证: 验证 HMAC-SHA256 系统级签名
  - Ed25519 验证: 验证 Agent 私钥签名
  - Merkle 树聚合: 按批次(batch_id)构建 Merkle 树，产出 merkle_root
  - 批量验证: 一次性验证整个 event log 的完整性
  - 报告: 返回被篡改/中断的 entry_id 列表

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event_log_path 参数
#   fields: 参数 event_log_path（无注解）
#   code: integrity.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: hmac_key 参数
#   fields: 参数 hmac_key（无注解）
#   code: integrity.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MerkleAggregator
#   name_en: MerkleAggregator
#   intro: Merkle 树构建器——蓝图 §2.2 cryptographic_integrity.merkle_aggrega…
#   desc: Merkle 树构建器——蓝图 §2.2 cryptographic_integrity.merkle_aggregation。 将一批审计事件的 entry_hash 作为叶子…；公共方法（定义序）: build…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② IntegrityVerifier
#   name_en: IntegrityVerifier
#   intro: class IntegrityVerifier 源码 L140-L368
#   desc: 公共方法（定义序）: event_log_path, hmac_key, verify_chain, verify_single；源码 L140-L368
#   inputs: event_log_path hmac_key
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: MerkleAggregator, IntegrityVerifier
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import AUDIT_DATA_DIR, REPO_ROOT  # 路径真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.io.serialization import dumps

_logger = logging.getLogger(__name__)

# ── 密钥分期（key era）注册表——2026-09-16 密钥政策裁定配套基建 ──
# 背景：审计链 HMAC 历经三个密钥时代（公开默认钥期 / 2026-05 遗失密钥期 / 真钥期），
# 单钥验证器无法分期定性（遗失段=26,909 条"永久不可验证"被误报为失配；换真钥后
# 默认钥段 8.7 万条又将整体误报）。分期语义：
#   1. 按记录时间戳定位分期（覆盖 ts 的分期中 valid_from 最新者生效），只用该分期
#      的钥验证——禁 try-all（公开默认钥若可验任意分期=伪造通道，红蓝攻击用例钉死）。
#   2. transition_overlap_seconds：边界后过渡窗内追加接受上一分期钥（长驻写方
#      滚动重启期旧代码进程仍持旧钥）——窗内旧钥通过按 weak 计。
#   3. key_source=lost 分期 → known_loss（不判 compromised）；强分期钥不可解析
#      → mismatch fail-loud（禁静默降级为弱）。
# 显式传 hmac_key 参数时保持单钥语义（测试 SSoT，本文件既有契约不变）。
_ERA_REGISTRY_ENV = "ZEPHYR_AUDIT_KEY_ERAS"  # 测试/多仓隔离覆盖位（tests/conftest.py autouse）
_ERA_REGISTRY_PATH = REPO_ROOT / "config" / "audit_key_eras.yaml"
_DEFAULT_PUBLIC_HMAC_KEY = b"zephyr-audit-hmac-default-key"  # 与 writer._resolve_hmac_key 兜底同值（SSoT 注记：值变更须双侧同步）


@dataclass(frozen=True)
class _KeyEra:
    """一个密钥分期——注册表条目的强类型投影（解析失败 fail-loud，见 _load_key_eras）。"""

    id: str
    key_source: str  # builtin:default | env:<VAR> | lost
    strength: str  # strong | weak | none
    valid_from: datetime | None  # None=未激活（不覆盖任何时间戳）
    valid_to: datetime | None  # None=至今
    note: str = ""

    def covers(self, ts: datetime) -> bool:
        if self.valid_from is None:
            return False
        if ts < self.valid_from:
            return False
        return self.valid_to is None or ts < self.valid_to

    def resolve_key(self) -> bytes | None:
        if self.key_source == "builtin:default":
            return _DEFAULT_PUBLIC_HMAC_KEY
        if self.key_source.startswith("env:"):
            value = os.environ.get(self.key_source[4:], "")
            return value.encode("utf-8") if value else None
        return None  # lost


def _parse_iso_utc(value: str) -> datetime:
    """ISO 时间戳解析——naive 视为 UTC（writer 恒写 aware；防御历史杂散值）。"""
    ts = datetime.fromisoformat(value)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def _load_key_eras() -> tuple[list[_KeyEra], int] | None:
    """加载密钥分期注册表。

    - 注册表缺失 → None（调用方回退单钥语义——未部署分期基建的环境行为不变）
    - 注册表存在但结构/语义非法 → ValueError fail-loud（错误分期定性比拒绝验证更危险）
    - 返回 (eras, transition_overlap_seconds)；不做模块级缓存（verify 非热路径，
      免缓存换取测试 env 覆盖即时生效）
    """
    env_path = os.environ.get(_ERA_REGISTRY_ENV, "")
    path = Path(env_path) if env_path else _ERA_REGISTRY_PATH
    if not path.exists():
        return None
    import yaml  # 惰性加载：integrity 被 import 的面远大于用 yaml 的面

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("eras"), list):
        # 路径等敏感值走日志 details，不进异常消息文本（MSG-EXPOSURE，5.99.20）
        _logger.error("audit key era registry malformed (expect mapping with eras list): %s", path)
        raise ValueError("audit key era registry malformed (expect mapping with eras list; registry path in log)")
    overlap = int(data.get("transition_overlap_seconds", 0) or 0)
    eras: list[_KeyEra] = []
    for raw in data["eras"]:
        if not isinstance(raw, dict):
            raise ValueError(f"audit key era entry must be mapping: {raw!r}")
        key_source = str(raw.get("key_source", ""))
        if not (key_source == "builtin:default" or key_source == "lost" or key_source.startswith("env:")):
            raise ValueError(f"audit key era '{raw.get('id')}' unknown key_source: {key_source}")
        vf = raw.get("valid_from")
        vt = raw.get("valid_to")
        eras.append(
            _KeyEra(
                id=str(raw.get("id", "")),
                key_source=key_source,
                strength=str(raw.get("strength", "weak")),
                valid_from=_parse_iso_utc(str(vf)) if vf else None,
                valid_to=_parse_iso_utc(str(vt)) if vt else None,
                note=str(raw.get("note", "")),
            )
        )
    return eras, overlap


class MerkleAggregator:
    """Merkle 树构建器——蓝图 §2.2 cryptographic_integrity.merkle_aggregation。

    将一批审计事件的 entry_hash 作为叶子节点，构建 Merkle 树并返回 root。
    使用 SHA-256 作为哈希函数，每对兄弟节点拼接后哈希。

    使用方式:
        aggregator = MerkleAggregator()
        root = aggregator.build(entry_hashes)
    """

    @staticmethod
    def build(leaves: list[str]) -> str:
        """构建 Merkle 树——返回根哈希。

        Args:
            leaves: entry_hash 列表（叶子节点）

        Returns:
            merkle_root 的十六进制字符串。空列表返回空字符串。
        """
        if not leaves:
            return ""

        hashes = [bytes.fromhex(h) for h in leaves if h]

        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])

            next_level: list[bytes] = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_level.append(hashlib.sha256(combined).digest())
            hashes = next_level

        return hashes[0].hex() if hashes else ""

    @staticmethod
    def verify(leaves: list[str], claimed_root: str) -> bool:
        """验证 Merkle root 是否匹配。

        Args:
            leaves: 叶子节点的 entry_hash 列表
            claimed_root: 声称的 Merkle root

        Returns:
            True 如果重建的 root 与 claimed_root 一致
        """
        actual_root = MerkleAggregator.build(leaves)
        return hmac.compare_digest(actual_root.encode(), claimed_root.encode())


class IntegrityVerifier:
    def __init__(
        self,
        event_log_path: Path | str | None = None,
        hmac_key: str | None = None,
    ) -> None:
        # 治本（裁定#6 路径SSoT）：默认路径必须为绝对路径（项目硬约束"禁止相对路径"），
        # 真源为 zephyr.shared.io.paths.AUDIT_DATA_DIR。
        if event_log_path is None:
            self._event_log_path = AUDIT_DATA_DIR / "events.jsonl"
        else:
            self._event_log_path = Path(event_log_path)
        # 5.62.2 治本：未显式传 hmac_key（None）时经 SecretProvider 统一密钥源解析
        # （与 writer.py 签名方同一密钥源 ZEPHYR_AUDIT_HMAC_SECRET），禁止裸 os.environ。
        # 显式传 "" 表示禁用 HMAC（测试 SSoT：_hmac_key 应为 b""）。
        hmac_key_was_none = hmac_key is None  # 分期模式判定须用原始参数（解析会覆盖 None）
        if hmac_key is None:
            from zephyr.gov_audit.writer import resolve_audit_hmac_secret

            hmac_key = resolve_audit_hmac_secret()
        if not hmac_key:
            _logger.warning("ZEPHYR_AUDIT_HMAC_SECRET 未设置，HMAC 验证明确降级为跳过（不验证签名）")
        self._hmac_key = hmac_key.encode("utf-8") if hmac_key else b""
        # 密钥分期模式（2026-09-16）：仅自动解析（hmac_key=None）且注册表存在时启用；
        # 显式传钥=单钥语义（测试 SSoT，既有契约零变化）。注册表结构非法则 fail-loud。
        self._era_cfg = _load_key_eras() if hmac_key_was_none else None

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    # event_log_path property 已删除（2026-09-16 st-auditkey）：全仓零消费方实证
    # （tests 中的 .event_log_path 均为 AuditWriter 实例），且与 writer.py:431 构成
    # extract 级 100% 克隆（CloneGuard CAPABILITY-OVERLAP 硬阻断）——按门禁建议
    # 合并去重：路径经构造参数注入，无公共读取需求。
    @property
    def hmac_key(self):
        """只读：hmac_key（Stage 4 公共化）。"""
        return self._hmac_key

    @hmac_key.setter
    def hmac_key(self, value):
        """写入：hmac_key（Stage 4 公共化）。"""
        self._hmac_key = value

    def verify_chain(self) -> dict[str, Any]:
        if not self._event_log_path.exists():
            return {"status": "no_data", "events_checked": 0, "issues": []}

        issues: list[str] = []
        # 密钥分期计数（era 模式专用；单钥模式保持 None=不出现在语义里）
        era_summary: dict[str, int] | None = (
            {"strong": 0, "weak": 0, "known_loss": 0, "mismatch": 0} if self._era_cfg else None
        )
        # 治本（裁定#10 双契约并存）：首条事件的 prev 字段接受 "" 或 "0"*64 两种约定。
        # - writer 生产约定: prev_hash="0"*64 + HMAC(entry_hash)
        # - legacy 单元约定: prev_entry_hash="" + HMAC(canonical(event \ {entry_hash, hmac_signature}))
        # 两者安全等价：攻击者无 key 无法伪造任一形式；创世值不承载完整性保证
        #   （真正的保护来自后续事件的哈希链接）。
        prev_hash = ""
        genesis_seen = False
        event_count = 0

        with open(self._event_log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event_count += 1
                event = json.loads(line)

                stored_prev = event.get("prev_entry_hash", event.get("prev_hash", ""))
                if not genesis_seen:
                    # 创世哨兵：首条事件允许 "" 或 "0"*64 两种约定
                    if stored_prev not in ("", "0" * 64):
                        issues.append(
                            f"event #{event_count}: genesis prev_hash must be '' or '0'*64, got={stored_prev[:16]}..."
                        )
                    genesis_seen = True
                elif stored_prev != prev_hash:
                    issues.append(
                        f"event #{event_count}: prev_entry_hash mismatch "
                        f"(expected={prev_hash[:16]}..., got={stored_prev[:16]}...)"
                    )

                verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
                event_str = dumps(verify_event, ensure_ascii=False, sort_keys=True)
                prev_hash = hashlib.sha256(event_str.encode("utf-8")).hexdigest()

                # 治本（AI-AUDIT12 审计链自一致性）：校验 stored entry_hash == 内容重算哈希。
                # 原实现仅做链式 prev 链接 + HMAC-over-entry_hash：篡改"最后一条"事件内容
                # （保留 entry_hash/hmac_signature 不变）时，无后续事件暴露断链，HMAC 也只
                # 证明 entry_hash 未被替换而非内容未被篡改——末事件篡改不可检测。
                # canonical 口径（全部既有测试契约实测并存）：
                # - production 事件（writer 写入，标记=prev_hash 字段存在）：payload 含 prev_hash
                # - legacy 事件：两种历史变体并存（含/不含 prev_entry_hash），任一匹配即通过
                #   （SHA-256 抗原像，接受两个确定性 canonical 不削弱篡改检测）。
                is_production_format = "prev_hash" in event
                stored_entry_hash = event.get("entry_hash", "")
                if is_production_format and not stored_entry_hash:
                    issues.append(f"event #{event_count}: production event missing entry_hash (possible strip tamper)")
                if stored_entry_hash:
                    entry_candidates = [verify_event]
                    if not is_production_format and "prev_entry_hash" in verify_event:
                        entry_candidates.append({k: v for k, v in verify_event.items() if k != "prev_entry_hash"})
                    if not any(
                        hmac.compare_digest(
                            hashlib.sha256(dumps(c, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
                            stored_entry_hash,
                        )
                        for c in entry_candidates
                    ):
                        issues.append(f"event #{event_count}: entry_hash mismatch (content tampered or hash stripped)")
                if is_production_format and self._hmac_key and not event.get("hmac_signature", ""):
                    issues.append(
                        f"event #{event_count}: production event missing hmac_signature (possible strip tamper)"
                    )

                if self._era_cfg and era_summary is not None:
                    # 分期模式（2026-09-16）：按记录时间戳选分期钥验证，四类计数
                    # （strong/weak/known_loss/mismatch）——known_loss 不判 compromised。
                    stored_hmac = event.get("hmac_signature", "")
                    if stored_hmac:
                        verdict = self._verify_hmac_era(event)
                        era_summary[verdict] += 1
                        if verdict == "mismatch":
                            issues.append(f"event #{event_count}: HMAC signature mismatch (era-scoped)")
                elif self._hmac_key:
                    stored_hmac = event.get("hmac_signature", "")
                    if stored_hmac and not self._hmac_matches(event):
                        issues.append(f"event #{event_count}: HMAC signature mismatch")

                stored_agent_sig = event.get("signature", "")
                if stored_agent_sig:
                    entry_hash = event.get("entry_hash", "")
                    if entry_hash:
                        v = self._verify_agent_signature_inline(event, stored_agent_sig)
                        if v is False:
                            issues.append(f"event #{event_count}: Agent signature invalid")

        status = "valid" if not issues else "compromised"
        return {
            "status": status,
            "events_checked": event_count,
            "issues": issues,
            # 密钥分期四类计数（era 模式；单钥模式恒 None）——weak/known_loss 是历史
            # 事实的诚实呈现，不构成 compromised；mismatch 才是。
            "hmac_era_summary": era_summary,
        }

    def _hmac_matches(self, event: dict[str, Any]) -> bool:
        r"""验证 HMAC 签名（单钥语义）——治本（裁定#10 双契约并存）：两种安全等价签名约定。

        1. writer 生产约定: HMAC-SHA256(key, entry_hash 字符串)
        2. legacy 单元约定: HMAC-SHA256(key, canonical(event \ {entry_hash, hmac_signature}))

        攻击者无 key 无法伪造任一形式；任一形式通过即视为验证通过。
        """
        return self._hmac_matches_with_key(event, self._hmac_key)

    @staticmethod
    def _hmac_matches_with_key(event: dict[str, Any], key: bytes) -> bool:
        r"""三分期通用的多约定 HMAC 验证（era 模式与单钥模式共用）。

        约定③（canonical 含 entry_hash、不含 hmac_signature）为 2026-05 代
        audit_trail writer 遗留口径（git 考古实证：签 名=HMAC(key, json.dumps(
        event_data 含 entry_hash, sort_keys=True))）——遗失密钥段若他日寻回旧钥，
        该口径即恢复可验。三约定均为确定性 canonical，接受三者不削弱篡改检测
        （无钥仍不可伪造任一形式）。
        """
        stored_hmac = event.get("hmac_signature", "")
        if not stored_hmac:
            return True  # 无签名=无可验（缺签名问题由 verify_chain 缺失检查独立报告）
        if not key:
            return False  # 有签名而无钥=不可验证，按不通过处理（fail-closed）
        # 约定①：HMAC over entry_hash 字符串
        entry_hash_str = event.get("entry_hash", "")
        if entry_hash_str:
            expected_over_hash = hmac.new(key, entry_hash_str.encode("utf-8"), hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected_over_hash, stored_hmac):
                return True
        # 约定②：HMAC over canonical(event \ {entry_hash, hmac_signature})
        verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
        canonical_str = dumps(verify_event, ensure_ascii=False, sort_keys=True)
        expected_over_event = hmac.new(key, canonical_str.encode("utf-8"), hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected_over_event, stored_hmac):
            return True
        # 约定③（May 代）：HMAC over canonical(event \ {hmac_signature})——含 entry_hash
        may_canonical = dumps(
            {k: v for k, v in event.items() if k != "hmac_signature"}, ensure_ascii=False, sort_keys=True
        )
        expected_may = hmac.new(key, may_canonical.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_may, stored_hmac)

    # ── 密钥分期验证（2026-09-16 密钥政策裁定配套）──────────────────────────

    def _select_era(self, ts: datetime) -> _KeyEra | None:
        """覆盖 ts 的分期中 valid_from 最新者生效（内嵌分期如 lost-in-default 由此让位）。"""
        covering = [era for era in self._era_cfg[0] if era.covers(ts)]
        return max(covering, key=lambda e: e.valid_from) if covering else None

    def _previous_era(self, era: _KeyEra) -> _KeyEra | None:
        """valid_from 早于 era 的分期中最新者（过渡窗旧钥来源）。"""
        if era.valid_from is None:
            return None
        priors = [
            e
            for e in self._era_cfg[0]
            if e.valid_from is not None and e.valid_from < era.valid_from
        ]
        return max(priors, key=lambda e: e.valid_from) if priors else None

    def _era_candidate_keys(self, era: _KeyEra, ts: datetime | None) -> list[tuple[bytes, str]]:
        """生效分期钥 + 过渡窗内上一分期钥——仅此二者（禁 try-all）。

        强分期 env 缺失返回 []（调用方落 mismatch fail-loud，禁静默降级弱）。
        """
        key = era.resolve_key()
        candidates: list[tuple[bytes, str]] = []
        if key:
            candidates.append((key, era.strength))
        overlap = self._era_cfg[1]
        prev = self._previous_era(era)
        if overlap > 0 and prev is not None and era.valid_from is not None and ts is not None:
            within_overlap = (ts - era.valid_from).total_seconds() <= overlap
            prev_key = prev.resolve_key() if within_overlap else None
            if prev_key:
                candidates.append((prev_key, prev.strength))
        return candidates

    def _verify_hmac_era(self, event: dict[str, Any]) -> str:
        """分期定密验证——返回 strong / weak / known_loss / mismatch 四类之一。

        硬规则（config/audit_key_eras.yaml 头注同源）：
        - 只用生效分期的钥（+过渡窗内上一分期的钥）——禁 try-all；
        - 强分期钥不可解析 → mismatch（fail-loud，禁静默降级弱）；
        - lost 分期 → known_loss（非 compromised）。
        """
        try:
            ts = _parse_iso_utc(str(event.get("timestamp", "")))
        except (ValueError, TypeError):
            ts = None  # 无时间戳=无法定位分期，回退单钥口径防御
        era = self._select_era(ts) if ts is not None else None
        if era is None:
            if self._hmac_key and self._hmac_matches(event):
                return "weak" if self._hmac_key == _DEFAULT_PUBLIC_HMAC_KEY else "strong"
            return "mismatch"

        for cand_key, cand_strength in self._era_candidate_keys(era, ts):
            if self._hmac_matches_with_key(event, cand_key):
                return "strong" if cand_strength == "strong" else "weak"
        if era.key_source == "lost":
            return "known_loss"
        return "mismatch"

    def verify_single(self, event_index: int) -> dict[str, Any]:
        if not self._event_log_path.exists():
            return {"status": "no_data", "valid": False}

        with open(self._event_log_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i == event_index - 1:
                    event = json.loads(line.strip())
                    # 5.37.13 修复：统一哈希逻辑——排除 entry_hash 和 hmac_signature，
                    # 与 verify_chain() 保持一致，避免两种验证方法结果矛盾。
                    verify_event = {k: v for k, v in event.items() if k not in ("entry_hash", "hmac_signature")}
                    calc_hash = hashlib.sha256(
                        dumps(verify_event, ensure_ascii=False, sort_keys=True).encode("utf-8")
                    ).hexdigest()
                    # 治本（AI-AUDIT12 审计链自一致性）：valid 不再恒 True——stored entry_hash
                    # 存在时必须与内容重算哈希一致（canonical 口径同 verify_chain：production
                    # 含 prev_hash；legacy 含/不含 prev_entry_hash 两变体任一匹配）；否则视为
                    # 内容篡改 valid=False。
                    stored_entry_hash = event.get("entry_hash", "")
                    is_production_format = "prev_hash" in event
                    entry_hash_valid = True
                    if stored_entry_hash:
                        single_candidates = [verify_event]
                        if not is_production_format and "prev_entry_hash" in verify_event:
                            single_candidates.append({k: v for k, v in verify_event.items() if k != "prev_entry_hash"})
                        entry_hash_valid = any(
                            hmac.compare_digest(
                                hashlib.sha256(
                                    dumps(c, ensure_ascii=False, sort_keys=True).encode("utf-8")
                                ).hexdigest(),
                                stored_entry_hash,
                            )
                            for c in single_candidates
                        )
                    result: dict[str, Any] = {
                        "status": "found",
                        "event_index": event_index,
                        "valid": entry_hash_valid,
                        "chain_hash": calc_hash,
                    }
                    if not entry_hash_valid:
                        result["issue"] = "entry_hash mismatch (content tampered or hash stripped)"
                    if self._hmac_key:
                        stored_hmac = event.get("hmac_signature", "")
                        if stored_hmac:
                            # 修复：HMAC 验证 entry_hash 字符串，与 writer.py 写入方一致。
                            entry_hash_str = event.get("entry_hash", "")
                            expected_hmac = hmac.new(
                                self._hmac_key,
                                entry_hash_str.encode("utf-8"),
                                hashlib.sha256,
                            ).hexdigest()
                            result["hmac_valid"] = hmac.compare_digest(expected_hmac, stored_hmac)
                        elif is_production_format:
                            # 治本（AI-AUDIT12）：production 事件必有 hmac_signature（writer
                            # 恒签名）——缺失即剥离篡改，显式判 invalid（原静默跳过）。
                            result["hmac_valid"] = False
                            result["valid"] = False
                            result.setdefault("issue", "production event missing hmac_signature")
                    return result
        return {"status": "not_found", "valid": False}

    def _verify_agent_signature_inline(self, event: dict[str, Any], signature_hex: str) -> bool | None:
        try:
            from zephyr.gov_audit.agent_signer import AgentSigner

            entry_hash = event.get("entry_hash", "")
            if not entry_hash:
                return None
            public_key_hex = event.get("metadata", {}).get("agent_public_key", "")
            if not public_key_hex:
                return None
            return AgentSigner.verify(event, public_key_hex, signature_hex)
        except ImportError:
            return None
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False
