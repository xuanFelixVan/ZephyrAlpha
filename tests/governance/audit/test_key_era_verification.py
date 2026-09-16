# [A_test] module_id: SRC-TST-KEYERA | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5
# [MODULE] tests.test_key_era_verification
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] 攻击用例红蓝钉死：era 范围外的钥验过=失配（禁 try-all）
# [MODIFY-GUARD] era 语义变更须同步 src/zephyr/gov_audit/integrity.py + config/audit_key_eras.yaml
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-020 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""密钥分期（key era）验证语义测试（2026-09-16 密钥政策裁定配套）。

四类判定（strong / weak / known_loss / mismatch）+ 三条硬规则：
  1. era 范围外的钥验过=失配（try-all 禁止——红蓝攻击用例钉死）
  2. 强分期 env 缺失 fail-loud 判 mismatch（禁静默降级弱）
  3. lost 分期 known_loss 不判 compromised

隔离：tests/conftest.py autouse 把 ZEPHYR_AUDIT_KEY_ERAS 指向不存在路径；
本套件 fixture 内重设 env 指向 tmp 注册表（后执行者生效）。
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from zephyr.gov_audit.integrity import IntegrityVerifier
from zephyr.gov_audit.writer import AuditWriter
from zephyr.shared.io.serialization import dumps as z_dumps

_DEFAULT_KEY = b"zephyr-audit-hmac-default-key"


@pytest.fixture
def era_env(tmp_path, monkeypatch):
    """注册表工厂：写入 tmp yaml 并接管 ZEPHYR_AUDIT_KEY_ERAS（覆盖 conftest 隔离值）。"""

    def _install(eras: list[dict], overlap: int = 0) -> Path:
        path = tmp_path / "audit_key_eras.yaml"
        path.write_text(
            yaml.safe_dump(
                {"schema_version": "1.0.0", "transition_overlap_seconds": overlap, "eras": eras},
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("ZEPHYR_AUDIT_KEY_ERAS", str(path))
        return path

    return _install


def _write_events(data_dir: Path, key: str, n: int, agent: str) -> None:
    w = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key=key)
    for i in range(n):
        w.write({"event_type": "generic", "agent_id": agent, "seq": i})


def _timestamps(path: Path) -> list[datetime]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(datetime.fromisoformat(json.loads(line)["timestamp"]))
    return out


def _boundary(ts_a: datetime, ts_b: datetime) -> str:
    """两时间戳中点=era 边界（避开 covers() 的 >= 语义歧义）。"""
    mid = ts_a + (ts_b - ts_a) / 2
    return mid.astimezone(timezone.utc).isoformat()


def _era(id_, key_source, strength, valid_from, valid_to=None):
    return {
        "id": id_,
        "key_source": key_source,
        "strength": strength,
        "valid_from": valid_from,
        "valid_to": valid_to,
    }


class TestEraClassification:
    def test_three_era_strong_known_loss_classification(self, tmp_path, era_env, monkeypatch):
        """三段链：强钥段 strong / 遗失段 known_loss——status 仍 valid（known_loss 非 compromised）。"""
        monkeypatch.setenv("ZEPHYR_TEST_ERA_KEY_A", "secret-era-a")
        monkeypatch.setenv("ZEPHYR_TEST_ERA_KEY_C", "secret-era-c")
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"

        import time as _time

        _write_events(data_dir, "secret-era-a", 2, "era-a")
        _time.sleep(0.005)  # 分段间时间戳严格分离（防负载下时钟碰撞致边界歧义）
        _write_events(data_dir, "secret-era-b-now-lost", 2, "era-b")
        _time.sleep(0.005)
        _write_events(data_dir, "secret-era-c", 2, "era-c")

        ts = _timestamps(log)
        era_env(
            [
                _era("era-a", "env:ZEPHYR_TEST_ERA_KEY_A", "strong", "1970-01-01T00:00:00+00:00", _boundary(ts[1], ts[2])),
                _era("era-b", "lost", "none", _boundary(ts[1], ts[2]), _boundary(ts[3], ts[4])),
                _era("era-c", "env:ZEPHYR_TEST_ERA_KEY_C", "strong", _boundary(ts[3], ts[4])),
            ]
        )
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"] == {"strong": 4, "weak": 0, "known_loss": 2, "mismatch": 0}
        assert report["status"] == "valid", report["issues"][:3]

    def test_weak_era_builtin_default(self, tmp_path, era_env):
        """公开默认钥签名段 → weak 计数（诚实呈现弱保护，不判 compromised）。"""
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, _DEFAULT_KEY.decode(), 3, "default-era")
        era_env([_era("era-default", "builtin:default", "weak", "1970-01-01T00:00:00+00:00")])
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"]["weak"] == 3
        assert report["status"] == "valid"

    def test_strong_era_fail_loud_when_env_missing(self, tmp_path, era_env):
        """强分期 env 缺失 → mismatch（禁静默降级为弱/默认）——换钥后删 .env 即刻暴露。"""
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, "some-secret", 2, "strong-era")  # env 未设该变量
        era_env([_era("era-x", "env:ZEPHYR_TEST_ERA_KEY_UNSET_XYZ", "strong", "1970-01-01T00:00:00+00:00")])
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"]["mismatch"] == 2
        assert report["status"] == "compromised"


class TestEraScopingSecurity:
    def test_forged_signature_with_out_of_era_key_rejected(self, tmp_path, era_env, monkeypatch):
        """红蓝攻击用例：强分期记录被 era 外的钥（含公开默认钥）重签 → 必须失配。

        try-all 实现会在此用例上放行（默认钥可验）——era 范围围栏是安全底线。
        """
        monkeypatch.setenv("ZEPHYR_TEST_ERA_KEY_A", "secret-era-a")
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, "secret-era-a", 3, "era-a")

        lines = log.read_text(encoding="utf-8").splitlines()
        rec = json.loads(lines[-1])
        forged = hmac.new(_DEFAULT_KEY, rec["entry_hash"].encode("utf-8"), hashlib.sha256).hexdigest()
        rec["hmac_signature"] = forged
        lines[-1] = json.dumps(rec, ensure_ascii=False)
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")

        era_env([_era("era-a", "env:ZEPHYR_TEST_ERA_KEY_A", "strong", "1970-01-01T00:00:00+00:00")])
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"]["mismatch"] == 1
        assert report["status"] == "compromised"

    def test_transition_overlap_bounded(self, tmp_path, era_env, monkeypatch):
        """过渡窗语义：边界后 overlap 秒内接受上一分期钥（weak）；窗外同钥=失配。"""
        import time as _time

        monkeypatch.setenv("ZEPHYR_TEST_ERA_NEW", "secret-new")
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, _DEFAULT_KEY.decode(), 2, "old-default")  # 旧钥段
        _time.sleep(0.005)  # 保证第 3 条时间戳严格晚于前两条（防负载下时钟碰撞闪失）
        _write_events(data_dir, _DEFAULT_KEY.decode(), 1, "old-default")  # 边界后旧钥记录

        ts = _timestamps(log)
        boundary = _boundary(ts[1], ts[2])  # 严格中点：ts[0]/ts[1] 归旧分期，ts[2] 归新分期
        era_env(
            [
                _era("era-old", "builtin:default", "weak", "1970-01-01T00:00:00+00:00", boundary),
                _era("era-new", "env:ZEPHYR_TEST_ERA_NEW", "strong", boundary),
            ],
            overlap=86400 * 365,  # 365 天窗内：旧钥记录按 weak 接受
        )
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"] == {"strong": 0, "weak": 3, "known_loss": 0, "mismatch": 0}
        assert report["status"] == "valid"

        era_env(
            [
                _era("era-old", "builtin:default", "weak", "1970-01-01T00:00:00+00:00", boundary),
                _era("era-new", "env:ZEPHYR_TEST_ERA_NEW", "strong", boundary),
            ],
            overlap=0,  # 窗关闭：边界后旧钥签名即刻失配（边界前旧段仍 weak 合法）
        )
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"]["weak"] == 2  # 边界前的旧段记录
        assert report["hmac_era_summary"]["mismatch"] == 1  # 边界上的记录（ts==valid_from 归新分期）
        assert report["status"] == "compromised"


class TestLegacyCompat:
    def test_explicit_key_bypasses_era(self, tmp_path, era_env):
        """显式传 hmac_key=单钥语义（既有 60 处调用面契约零变化）。"""
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, "secret-a", 2, "a")
        _write_events(data_dir, "secret-b", 2, "b")
        ts = _timestamps(log)
        era_env(
            [
                _era("era-a", "builtin:default", "weak", "1970-01-01T00:00:00+00:00", _boundary(ts[1], ts[2])),
                _era("era-b", "lost", "none", _boundary(ts[1], ts[2])),
            ]
        )
        report = IntegrityVerifier(event_log_path=log, hmac_key="secret-a").verify_chain()
        assert report["hmac_era_summary"] is None  # 单钥模式不出分期计数
        assert report["status"] == "compromised"  # secret-b 段在单钥口径下失配（既有行为）

    def test_registry_missing_legacy_single_key(self, tmp_path, monkeypatch):
        """注册表缺失 → 回退单钥语义（未部署分期基建的环境行为不变）。

        同时摘除 ZEPHYR_AUDIT_HMAC_SECRET 模拟部署前环境——本仓 .env 已部署真钥
        （裁定#267），包导入即注入 os.environ，不摘除则单钥解析出真钥致默认钥事件失配。
        生产面不受此影响：仓内 config/audit_key_eras.yaml 存在，自动模式恒走 era 分期。
        """
        monkeypatch.setenv("ZEPHYR_AUDIT_KEY_ERAS", str(tmp_path / "_nonexistent.yaml"))
        monkeypatch.delenv("ZEPHYR_AUDIT_HMAC_SECRET", raising=False)
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, _DEFAULT_KEY.decode(), 2, "default")
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"] is None
        assert report["status"] == "valid"

    def test_malformed_registry_fail_loud(self, tmp_path, era_env):
        """注册表结构非法 → ValueError（错误分期定性比拒绝验证更危险）。"""
        path = tmp_path / "bad.yaml"
        path.write_text('{"eras": [{"id": "x", "key_source": "file:/etc/shadow"}]}', encoding="utf-8")
        import os

        os.environ["ZEPHYR_AUDIT_KEY_ERAS"] = str(path)
        try:
            with pytest.raises(ValueError, match="unknown key_source"):
                IntegrityVerifier(event_log_path=tmp_path / "nope.jsonl")
        finally:
            os.environ.pop("ZEPHYR_AUDIT_KEY_ERAS", None)


class TestMayConventionCompat:
    def test_may_era_convention_accepted(self, tmp_path, era_env, monkeypatch):
        """约定③（2026-05 代：HMAC over canonical 含 entry_hash）可验——旧钥寻回即恢复。"""
        key = "recovered-may-secret"
        monkeypatch.setenv("ZEPHYR_TEST_ERA_MAY", key)
        data_dir = tmp_path / "chain"
        data_dir.mkdir()
        log = data_dir / "events.jsonl"
        _write_events(data_dir, "throwaway", 1, "x")

        lines = log.read_text(encoding="utf-8").splitlines()
        rec = json.loads(lines[0])
        payload = {k: v for k, v in rec.items() if k != "hmac_signature"}
        rec["hmac_signature"] = hmac.new(
            key.encode(), z_dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"), hashlib.sha256
        ).hexdigest()
        lines[0] = json.dumps(rec, ensure_ascii=False)
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")

        era_env([_era("era-may", "env:ZEPHYR_TEST_ERA_MAY", "strong", "1970-01-01T00:00:00+00:00")])
        report = IntegrityVerifier(event_log_path=log).verify_chain()
        assert report["hmac_era_summary"]["strong"] == 1
        assert report["status"] == "valid"
