# [A_test] module_id: SRC-TST-GWM-SECDRIFT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5
# [MODULE] tests.test_secret_registry_drift
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-020 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""C-4 secret_registry 周期核对回归测试（2026-09-16 裁定#287）。

覆盖：required=true 失守 critical / registry↔.env 双向漂移 / era 钥登记与可解析性 /
钥值指纹 rotation 告警 / reconciler 工厂 trigger+action 映射 / 永不输出密钥明文。
隔离纪律：registry/era/.env 全部 tmp_path 注入，env 快照显式传参，state_dir 指向 tmp。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from zephyr.gov_audit.secret_registry_drift import (
    SECRET_DRIFT_GATE_ID,
    check_secret_registry_drift,
    make_secret_registry_drift_reconciler,
)


def _write_registry(root: Path, entries: list[dict]) -> None:
    cfg = root / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "secret_registry.yaml").write_text(
        yaml.safe_dump({"secrets": entries}, allow_unicode=True), encoding="utf-8"
    )


def _write_eras(root: Path, eras: list[dict]) -> None:
    cfg = root / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "audit_key_eras.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0.0", "transition_overlap_seconds": 0, "eras": eras}),
        encoding="utf-8",
    )


def _write_dotenv(root: Path, values: dict[str, str]) -> None:
    (root / ".env").write_text(
        "\n".join(f"{k}={v}" for k, v in values.items()) + "\n", encoding="utf-8"
    )


@pytest.fixture
def root(tmp_path) -> Path:
    return tmp_path


def _check(root: Path, env: dict[str, str] | None = None):
    return check_secret_registry_drift(root, env=env or {}, state_dir=root / ".runtime" / "secret_drift")


def _codes(report: dict) -> list[str]:
    return [f["code"] for f in report["findings"]]


class TestRequiredKeyChecks:
    def test_clean_registry_no_findings(self, root):
        _write_registry(root, [{"key": "A_KEY", "env_file": ".env", "required": True}])
        _write_dotenv(root, {"A_KEY": "val-1"})
        report = _check(root)
        assert report["status"] == "clean"
        assert report["findings"] == []
        assert report["required_total"] == 1

    def test_required_missing_is_critical(self, root):
        _write_registry(root, [{"key": "GONE_KEY", "env_file": ".env", "required": True}])
        report = _check(root)
        assert report["status"] == "critical"
        assert "required_key_missing" in _codes(report)

    def test_required_empty_value_counts_as_missing(self, root):
        _write_registry(root, [{"key": "EMPTY_KEY", "env_file": ".env", "required": True}])
        _write_dotenv(root, {"EMPTY_KEY": ""})
        assert "required_key_missing" in _codes(_check(root))

    def test_required_resolved_from_env_file_service_layout(self, root):
        _write_registry(
            root, [{"key": "DB_PASS", "env_file": "config/.env.db", "required": True}]
        )
        svc = root / "config" / ".env.db"
        svc.write_text("DB_PASS=svc-secret\n", encoding="utf-8")
        assert _check(root)["status"] == "clean"


class TestBidirectionalDrift:
    def test_env_secret_key_not_registered_warns(self, root):
        _write_registry(root, [{"key": "KNOWN_KEY", "env_file": ".env", "required": False}])
        _write_dotenv(root, {"KNOWN_KEY": "v", "ROGUE_API_KEY": "sk-123"})
        report = _check(root)
        assert "unregistered_secret_in_env" in _codes(report)
        assert report["status"] == "drift"

    def test_plain_config_key_not_flagged(self, root):
        _write_registry(root, [])
        _write_dotenv(root, {"LOG_LEVEL": "INFO"})
        assert _check(root)["status"] == "clean"

    def test_optional_registered_key_missing_not_flagged(self, root):
        """registry 有钥而 env 无：required=false 属合法缺省，不告警（optional 语义）。"""
        _write_registry(root, [{"key": "OPT_KEY", "env_file": ".env", "required": False}])
        assert _check(root)["status"] == "clean"


class TestEraLinkage:
    def test_era_env_var_must_be_registered(self, root):
        _write_registry(root, [])
        _write_eras(
            root,
            [{"id": "era-primary", "key_source": "env:ZEPHYR_AUDIT_HMAC_SECRET", "strength": "strong", "valid_from": "2026-01-01T00:00:00+00:00", "valid_to": None}],
        )
        _write_dotenv(root, {"ZEPHYR_AUDIT_HMAC_SECRET": "realkey"})
        codes = _codes(_check(root))
        assert "era_key_not_in_registry" in codes

    def test_active_era_key_unresolvable_critical(self, root):
        _write_registry(root, [{"key": "ZEPHYR_AUDIT_HMAC_SECRET", "env_file": ".env", "required": True}])
        _write_eras(
            root,
            [{"id": "era-primary", "key_source": "env:ZEPHYR_AUDIT_HMAC_SECRET", "strength": "strong", "valid_from": "2026-01-01T00:00:00+00:00", "valid_to": None}],
        )
        report = _check(root)
        assert "era_active_key_unresolvable" in _codes(report)
        assert report["status"] == "critical"

    def test_closed_default_era_with_env_key_no_warning(self, root):
        _write_registry(root, [{"key": "ZEPHYR_AUDIT_HMAC_SECRET", "env_file": ".env", "required": True}])
        _write_dotenv(root, {"ZEPHYR_AUDIT_HMAC_SECRET": "realkey"})
        _write_eras(
            root,
            [
                {"id": "era-default", "key_source": "builtin:default", "strength": "weak", "valid_from": "1970-01-01T00:00:00+00:00", "valid_to": "2026-09-16T07:05:02+00:00"},
                {"id": "era-primary", "key_source": "env:ZEPHYR_AUDIT_HMAC_SECRET", "strength": "strong", "valid_from": "2026-09-16T07:05:02+00:00", "valid_to": None},
            ],
        )
        report = _check(root)
        assert "default_era_active_with_env_key" not in _codes(report)
        assert report["status"] == "clean"
        assert report["fingerprints"]["ZEPHYR_AUDIT_HMAC_SECRET"]


class TestFingerprintRotationWatch:
    def test_rotation_since_last_check_warns(self, root):
        _write_registry(root, [{"key": "K", "env_file": ".env", "required": True}])
        _write_eras(
            root,
            [{"id": "era-primary", "key_source": "env:K", "strength": "strong", "valid_from": "2026-01-01T00:00:00+00:00", "valid_to": None}],
        )
        state = root / ".runtime" / "secret_drift"
        r1 = check_secret_registry_drift(root, env={"K": "old-value"}, state_dir=state)
        assert r1["status"] == "clean"  # 首次记账不告警
        r2 = check_secret_registry_drift(root, env={"K": "new-value"}, state_dir=state)
        assert "key_value_rotated_since_last_check" in _codes(r2)
        # 同值复跑不重复告警（状态已更新）
        r3 = check_secret_registry_drift(root, env={"K": "new-value"}, state_dir=state)
        assert "key_value_rotated_since_last_check" not in _codes(r3)
        stored = json.loads((state / "key_fingerprints.json").read_text(encoding="utf-8"))
        assert stored["K"]


class TestRegistryUnavailable:
    def test_missing_registry_critical(self, root):
        report = _check(root)
        assert report["status"] == "critical"
        assert "registry_missing" in _codes(report)

    def test_malformed_registry_critical(self, root):
        cfg = root / "config"
        cfg.mkdir(parents=True)
        (cfg / "secret_registry.yaml").write_text("::: not yaml [", encoding="utf-8")
        report = _check(root)
        assert "registry_malformed" in _codes(report)


class TestNoSecretMaterialLeak:
    def test_report_never_contains_secret_value(self, root):
        secret_value = "SUPER-SECRET-VALUE-abc123"
        _write_registry(root, [{"key": "ZEPHYR_AUDIT_HMAC_SECRET", "env_file": ".env", "required": True}])
        _write_dotenv(root, {"ZEPHYR_AUDIT_HMAC_SECRET": secret_value, "ROGUE_TOKEN": secret_value})
        _write_eras(
            root,
            [{"id": "era-primary", "key_source": "env:ZEPHYR_AUDIT_HMAC_SECRET", "strength": "strong", "valid_from": "2026-01-01T00:00:00+00:00", "valid_to": None}],
        )
        report = _check(root)
        serialized = json.dumps(report, ensure_ascii=False)
        assert secret_value not in serialized
        # 指纹形态允许（sha256[:12]）
        assert len(report["fingerprints"]["ZEPHYR_AUDIT_HMAC_SECRET"]) == 12


class TestReconcilerFactory:
    def _spec(self, root: Path):
        class _GW:
            project_root = root

        return make_secret_registry_drift_reconciler(_GW())

    def test_spec_shape(self, root):
        spec = self._spec(root)
        assert spec.gate_id == SECRET_DRIFT_GATE_ID
        assert spec.trigger(["any/file.py"]) is True  # 恒真：.env gitignored 按文件触发永不命中
        assert spec.priority == 216
        assert set(spec.file_ops) == {"read", "write"}

    def test_reconcile_clean(self, root):
        _write_registry(root, [])
        result = self._spec(root).reconcile([], "sess-x")
        assert result.action == "clean"
        assert result.gate_id == SECRET_DRIFT_GATE_ID

    def test_reconcile_required_missing_critical_warn(self, root):
        _write_registry(root, [{"key": "GONE", "env_file": ".env", "required": True}])
        result = self._spec(root).reconcile([], "sess-x")
        assert result.action == "critical_warn"
        assert "required_key_missing" in result.detail

    def test_reconcile_warn_only_drift(self, root):
        _write_registry(root, [])
        _write_dotenv(root, {"ROGUE_API_KEY": "v"})
        result = self._spec(root).reconcile([], "sess-x")
        assert result.action == "warn"
