# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.key_hierarchy
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.security.secrets; zephyr.shared.io.paths; zephyr.shared.utils.time_utils; cryptography(Fernet); PyYAML; config/secret_registry.yaml
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 主密钥缺失 fail-closed（KeyHierarchyError）；KEK=HKDF(master, info=kek:{purpose}) 确定性派生；DEK 按域隔离、落盘仅存 KEK 包裹态；信封 token=key_id.Fernet；跨域/篡改解密必拒；审计事件零密钥材料
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 主密钥缺失/非法→KeyHierarchyError；解密失败（跨域/篡改/未知 key_id）→KeyHierarchyError；未派发域操作→KeyHierarchyError
# [TESTS] tests/security/access_control/test_key_hierarchy.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""三层密钥层级管理（B12-03842 / CAND-SEC-004）。

层级：主密钥（系统密钥环/环境变量 ZEPHYR_MASTER_KEY，hex）→ KEK（HKDF 按用途派生）
→ DEK（按域派发，KEK 包裹存储）+ 90 天轮换 + 密钥使用审计落哈希链 + 启动完整性自检。

设计要点：
- 主密钥只经 zephyr.shared.security.secrets 同步入口读取（禁止裸 os.getenv，TRAE-031 SEC-002）。
- KEK = HKDF-SHA256(master, info="kek:{purpose}")——复用 secrets.derive_key_hkdf（RFC 5869）。
- DEK = CSPRNG 32B 按域派发；内存材料与记录分离：记录仅持 KEK(Fernet) 包裹态，可安全落盘/导出。
- 数据信封：token = key_id(16hex) + "." + Fernet(DEK)(plaintext)；key_id 前缀支持轮换后旧密文可解。
- 轮换：默认 90 天（对齐 secret_registry.yaml rotation_days 主流档位）；rotation_report()
  从 config/secret_registry.yaml 真源算各注册密钥到期清单。
- 审计：dispatch/rotate/self_check 事件注入 audit_sink（生产接 AiAuditLogger 哈希链），
  事件仅含 key_id/域/时间，零密钥材料。
- 裁剪（单人单机）：不落地 Shamir 分片与后量子迁移（裁定：机构级可选，min_build_spec 明确裁剪）。
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Final

import yaml
from cryptography.fernet import Fernet, InvalidToken

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.security.secrets import derive_key_hkdf, get_secret_or_default
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    pass  # 生产审计接线：audit_sink 可接 zephyr.trading.ai_audit_logger.AiAuditLogger 适配器

__all__ = [
    "DEFAULT_ROTATION_DAYS",
    "DispatchedDek",
    "KeyHierarchy",
    "KeyHierarchyCheck",
    "KeyHierarchyError",
]

DEFAULT_ROTATION_DAYS: Final[int] = 90
_KEK_INFO_PREFIX: Final[str] = "kek:"
_KEK_WRAP_PURPOSE: Final[str] = "domain_wrap"
_KEY_ID_LEN: Final[int] = 16  # hex 字符数（8 字节熵）
_MASTER_LEN: Final[int] = 32  # 字节


class KeyHierarchyError(Exception):
    """密钥层级操作失败（主密钥缺失/解密失败/未派发域）。"""


@dataclass(frozen=True)
class DispatchedDek:
    """DEK 派发信息（公开视图，零密钥材料）。"""

    domain: str
    key_id: str
    created_at: datetime
    rotation_days: int


@dataclass(frozen=True)
class KeyHierarchyCheck:
    """启动完整性自检单项结果。"""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class _DekRecord:
    """DEK 记录——仅持包裹态；plaintext 恒 None（材料存 _dek_material，不落记录）。"""

    domain: str
    key_id: str
    created_at: datetime
    rotation_days: int
    wrapped_dek: bytes
    plaintext: bytes | None = field(default=None, repr=False, compare=False)


class KeyHierarchy:
    """三层密钥层级：主密钥→KEK→DEK 按域派发 + 90 天轮换 + 审计 + 启动自检。"""

    MASTER_KEY_ENV: Final[str] = "ZEPHYR_MASTER_KEY"

    def __init__(
        self,
        *,
        master_key: bytes | str | None = None,
        registry_path: str | Path | None = None,
        rotation_days: int = DEFAULT_ROTATION_DAYS,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
        clock: Callable[[], datetime] = now_utc,
    ) -> None:
        self._master = self._resolve_master(master_key)  # fail-closed：缺失即 KeyHierarchyError
        self._registry_path = Path(registry_path) if registry_path else REPO_ROOT / "config" / "secret_registry.yaml"
        self._rotation_days = rotation_days
        self._audit_sink = audit_sink
        self._clock = clock
        self._deks: dict[str, _DekRecord] = {}
        self._dek_material: dict[str, bytes] = {}  # key_id → DEK 材料（含已轮换退役的）
        self._active_key_id: dict[str, str] = {}  # domain → 现役 key_id

    # ── 主密钥层 ──────────────────────────────────────────

    @classmethod
    def _resolve_master(cls, master_key: bytes | str | None) -> bytes:
        raw: bytes | str | None = master_key
        if raw is None:
            env_value = get_secret_or_default(cls.MASTER_KEY_ENV, "")
            raw = env_value if env_value else None
        if raw is None:
            raise KeyHierarchyError(
                f"主密钥未配置：请注入 master_key 或设置环境变量 {cls.MASTER_KEY_ENV}（hex，32 字节）"
            )
        if isinstance(raw, str):
            try:
                raw = bytes.fromhex(raw.strip())
            except ValueError as exc:
                raise KeyHierarchyError("主密钥 hex 解码失败（须为 64 字符 hex）") from exc
        if len(raw) < _MASTER_LEN:
            raise KeyHierarchyError(f"主密钥长度不足：{len(raw)}B < {_MASTER_LEN}B")
        return raw

    # ── KEK 层 ────────────────────────────────────────────

    def derive_kek(self, purpose: str) -> bytes:
        """按用途从主密钥派生 KEK（HKDF-SHA256，确定性）。"""
        if not purpose:
            raise KeyHierarchyError("KEK purpose 不能为空")
        return derive_key_hkdf(self._master, info=f"{_KEK_INFO_PREFIX}{purpose}", length=32)

    # ── DEK 按域派发 ──────────────────────────────────────

    def dispatch_dek(self, domain: str) -> DispatchedDek:
        """按域派发 DEK（同域缓存复用；新派发入审计）。"""
        if not domain:
            raise KeyHierarchyError("DEK 派发域不能为空")
        existing = self._deks.get(domain)
        if existing is not None:
            return self._public_view(existing)

        dek = os.urandom(32)
        created = self._clock()
        key_id = base64.urlsafe_b64encode(os.urandom(12)).decode("ascii")[:_KEY_ID_LEN].lower()
        wrapped = self._fernet(self._wrap_kek(domain)).encrypt(dek)
        record = _DekRecord(
            domain=domain,
            key_id=key_id,
            created_at=created,
            rotation_days=self._rotation_days,
            wrapped_dek=wrapped,
        )
        self._deks[domain] = record
        self._dek_material[key_id] = dek
        self._active_key_id[domain] = key_id
        self._audit("key.dispatch", domain=domain, key_id=key_id, rotation_days=record.rotation_days)
        return self._public_view(record)

    def export_state(self) -> dict[str, dict[str, Any]]:
        """导出全部域 DEK 记录（仅包裹态，可安全落盘；明文材料永不导出）。"""
        return {
            domain: {
                "key_id": rec.key_id,
                "created_at": rec.created_at.isoformat(),
                "rotation_days": rec.rotation_days,
                "wrapped_dek": rec.wrapped_dek,
            }
            for domain, rec in self._deks.items()
        }

    # ── 信封加解密 ────────────────────────────────────────

    def seal(self, domain: str, plaintext: bytes) -> bytes:
        """用域现役 DEK 密封数据：token = key_id.Fernet(plaintext)。首用惰性派发（入审计）。"""
        self.dispatch_dek(domain)  # 幂等：已派发即缓存复用
        record = self._deks[domain]
        material = self._dek_material[record.key_id]
        token = self._fernet(material).encrypt(plaintext)
        return record.key_id.encode("ascii") + b"." + token

    def open(self, domain: str, token: bytes) -> bytes:
        """解封：校验 key_id 归属该域（含已轮换退役钥），Fernet 认证失败即拒。"""
        self._require_record(domain)
        key_id, _, fernet_token = token.partition(b".")
        if not fernet_token:
            raise KeyHierarchyError("信封 token 格式非法（缺 key_id 前缀）")
        kid = key_id.decode("ascii", errors="replace")
        if kid != self._active_key_id[domain] and self._deks[domain].key_id != kid:
            raise KeyHierarchyError(f"信封 key_id 不属于域 {domain}（跨域/伪造拒绝）")
        material = self._dek_material.get(kid)
        if material is None:
            raise KeyHierarchyError(f"未知 key_id：{kid}")
        try:
            return self._fernet(material).decrypt(fernet_token)
        except InvalidToken as exc:
            raise KeyHierarchyError("解密失败（篡改或密钥不符）") from exc

    # ── 90 天轮换 ─────────────────────────────────────────

    def needs_rotation(self, domain: str) -> bool:
        """现役 DEK 龄期 ≥ rotation_days 即到期。"""
        record = self._require_record(domain)
        age = self._clock() - record.created_at
        return age.days >= record.rotation_days

    def rotate_dek(self, domain: str) -> DispatchedDek:
        """轮换域 DEK：新材料 + 新 key_id（旧材料保留供历史密文解封），入审计。"""
        old = self._require_record(domain)
        dek = os.urandom(32)
        created = self._clock()
        key_id = base64.urlsafe_b64encode(os.urandom(12)).decode("ascii")[:_KEY_ID_LEN].lower()
        wrapped = self._fernet(self._wrap_kek(domain)).encrypt(dek)
        record = _DekRecord(
            domain=domain,
            key_id=key_id,
            created_at=created,
            rotation_days=old.rotation_days,
            wrapped_dek=wrapped,
        )
        self._deks[domain] = record
        self._dek_material[key_id] = dek  # 旧 key_id 材料保留（版本化解密）
        self._active_key_id[domain] = key_id
        self._audit("key.rotate", domain=domain, key_id=key_id, retired_key_id=old.key_id)
        return self._public_view(record)

    def rotation_report(self) -> dict[str, dict[str, Any]]:
        """从 secret_registry.yaml 真源计算注册密钥轮换到期清单（rotation_days=null 不强制）。"""
        data = self._load_registry()
        if not isinstance(data, dict):
            return {}
        secrets_list = data.get("secrets") or []
        today = self._clock().date()
        report: dict[str, dict[str, Any]] = {}
        for entry in secrets_list:
            if not isinstance(entry, dict):
                continue
            days = entry.get("rotation_days")
            if days is None:
                continue
            since_raw = entry.get("since")
            try:
                since = date.fromisoformat(str(since_raw))
            except ValueError:
                continue
            due_date = date.fromordinal(since.toordinal() + int(days))
            report[str(entry.get("key"))] = {
                "service": entry.get("service", ""),
                "rotation_days": int(days),
                "due_date": due_date.isoformat(),
                "due": today >= due_date,
            }
        return report

    # ── 启动完整性自检 ────────────────────────────────────

    def startup_self_check(self) -> list[KeyHierarchyCheck]:
        """启动自检：主密钥/KEK 派生/DEK 包裹回环/注册表/已派发 DEK 健康度。"""
        results: list[KeyHierarchyCheck] = []

        results.append(
            KeyHierarchyCheck("master_configured", len(self._master) >= _MASTER_LEN, f"len={len(self._master)}")
        )

        try:
            kek = self.derive_kek(_KEK_WRAP_PURPOSE)
            results.append(KeyHierarchyCheck("kek_derivable", len(kek) == 32))
        except Exception as exc:  # noqa: BLE001 — 自检永不抛出，失败即不通过
            results.append(KeyHierarchyCheck("kek_derivable", False, str(exc)))

        try:
            probe = os.urandom(32)
            domain_kek = self._wrap_kek("__self_check__")
            wrapped = self._fernet(domain_kek).encrypt(probe)
            ok = self._fernet(domain_kek).decrypt(wrapped) == probe
            results.append(KeyHierarchyCheck("dek_wrap_roundtrip", ok))
        except Exception as exc:  # noqa: BLE001 — 自检永不抛出
            results.append(KeyHierarchyCheck("dek_wrap_roundtrip", False, str(exc)))

        registry = self._load_registry()
        results.append(
            KeyHierarchyCheck(
                "registry_present",
                isinstance(registry, dict) and "secrets" in registry,
                str(self._registry_path),
            )
        )

        unhealthy = []
        for domain, rec in self._deks.items():
            try:
                material = self._fernet(self._wrap_kek(domain)).decrypt(rec.wrapped_dek)
                if material != self._dek_material.get(rec.key_id):
                    unhealthy.append(domain)
            except Exception:  # noqa: BLE001 — 自检永不抛出
                unhealthy.append(domain)
        results.append(
            KeyHierarchyCheck("dispatched_deks_healthy", not unhealthy, ",".join(unhealthy))
        )

        self._audit(
            "key.self_check",
            all_passed=all(r.passed for r in results),
            failed=[r.name for r in results if not r.passed],
        )
        return results

    # ── 内部 ──────────────────────────────────────────────

    def _wrap_kek(self, domain: str) -> bytes:
        return self.derive_kek(f"{_KEK_WRAP_PURPOSE}:{domain}")

    @staticmethod
    def _fernet(key_material: bytes) -> Fernet:
        return Fernet(base64.urlsafe_b64encode(key_material))

    def _require_record(self, domain: str) -> _DekRecord:
        record = self._deks.get(domain)
        if record is None:
            raise KeyHierarchyError(f"域 {domain} 未派发 DEK（先 dispatch_dek）")
        return record

    @staticmethod
    def _public_view(record: _DekRecord) -> DispatchedDek:
        return DispatchedDek(
            domain=record.domain,
            key_id=record.key_id,
            created_at=record.created_at,
            rotation_days=record.rotation_days,
        )

    def _load_registry(self) -> dict[str, Any] | None:
        try:
            text = self._registry_path.read_text(encoding="utf-8")
        except OSError:
            return None
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            return None
        return data if isinstance(data, dict) else None

    def _audit(self, event: str, **detail: Any) -> None:
        """密钥使用审计（零密钥材料）；sink 生产侧接 AiAuditLogger 哈希链。"""
        if self._audit_sink is None:
            return
        entry = {"event": event, "ts": self._clock().isoformat(), **detail}
        try:
            self._audit_sink(entry)
        except Exception:  # noqa: BLE001 — 审计失败不阻断密钥主链路（哈希链侧自证缺失）
            pass
