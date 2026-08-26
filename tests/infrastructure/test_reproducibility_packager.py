# [BLUEPRINT] MOD-INF-081 | docs/03_modules/_domain_infrastructure_operations/reproducibility_packager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-081 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_reproducibility_packager
# [TESTS] src/zephyr/infrastructure/system_telemetry/reproducibility_packager.py
"""MOD-INF-081 单元测试：reproducibility_packager 实验可复现打包器。

蓝图验收（B1-00401/CAND-INFRATEL-001，C2）：
代码 commit+参数+数据快照指针+依赖锁 → 可回放包（manifest.json+sha256 校验）+
打包/校验/回放指针解析三接口 + 确定性（同输入同 digest）+ 非法输入 Fail-Closed。
包目录用 tmp_path 注入，时钟注入，不触网。
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.reproducibility_packager",
    reason="reproducibility_packager not importable",
)

from zephyr.infrastructure.system_telemetry.reproducibility_packager import (  # noqa: E402
    PackageManifest,
    ReproPackagerError,
    ReproducibilityPackager,
    manifest_digest,
)

_T0 = datetime.datetime(2026, 8, 25, 21, 0, 0)
_T1 = datetime.datetime(2026, 8, 25, 22, 0, 0)

_KW = {
    "code_commit": "abc1234",
    "params": {"lr": 0.01, "epochs": 10},
    "data_snapshot_ref": "snap://2026-08-25/features_v3",
    "dep_lock_hash": "deadbeef" * 8,
}


def _packager(tmp_path, clock=_T0) -> ReproducibilityPackager:
    return ReproducibilityPackager(root=tmp_path / "repro", clock=lambda: clock)


# ──────────────────────────────────────────────────────────────────────────────
# 打包（build_package）
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildPackage:
    def test_build_ok_returns_manifest(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        manifest = pkg.build_package("exp-001", **_KW)
        assert isinstance(manifest, PackageManifest)
        assert manifest.exp_id == "exp-001"
        assert manifest.code_commit == "abc1234"
        assert manifest.params == {"lr": 0.01, "epochs": 10}
        assert manifest.data_snapshot_ref == _KW["data_snapshot_ref"]
        assert manifest.dep_lock_hash == _KW["dep_lock_hash"]
        assert manifest.created_at == _T0

    def test_build_writes_manifest_json(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        pkg.build_package("exp-001", **_KW)
        path = tmp_path / "repro" / "exp-001" / "manifest.json"
        assert path.is_file()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["exp_id"] == "exp-001"
        assert payload["sha256"] == manifest_digest(
            PackageManifest(exp_id="exp-001", created_at=_T0, **_KW)
        )

    def test_digest_deterministic_same_input(self, tmp_path) -> None:
        p1 = _packager(tmp_path / "a")
        p2 = _packager(tmp_path / "b")
        m1 = p1.build_package("exp-001", **_KW)
        m2 = p2.build_package("exp-001", **_KW)
        assert manifest_digest(m1) == manifest_digest(m2)

    def test_digest_differs_with_clock(self, tmp_path) -> None:
        m1 = _packager(tmp_path / "a", clock=_T0).build_package("exp-001", **_KW)
        m2 = _packager(tmp_path / "b", clock=_T1).build_package("exp-001", **_KW)
        assert manifest_digest(m1) != manifest_digest(m2)

    def test_digest_params_order_invariant(self, tmp_path) -> None:
        kw2 = {**_KW, "params": {"epochs": 10, "lr": 0.01}}
        m1 = _packager(tmp_path / "a").build_package("exp-001", **_KW)
        m2 = _packager(tmp_path / "b").build_package("exp-001", **kw2)
        assert manifest_digest(m1) == manifest_digest(m2)

    def test_build_empty_exp_id_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).build_package("", **_KW)

    def test_build_empty_code_commit_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).build_package("exp-001", **{**_KW, "code_commit": ""})

    def test_build_empty_snapshot_ref_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).build_package(
                "exp-001", **{**_KW, "data_snapshot_ref": ""}
            )

    def test_build_empty_dep_lock_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).build_package("exp-001", **{**_KW, "dep_lock_hash": ""})

    def test_build_non_dict_params_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).build_package("exp-001", **{**_KW, "params": [1, 2]})

    def test_build_unserializable_params_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).build_package(
                "exp-001", **{**_KW, "params": {"bad": object()}}
            )

    def test_default_root(self) -> None:
        pkg = ReproducibilityPackager(clock=lambda: _T0)
        assert pkg.root == Path(".runtime/repro_packages")

    def test_empty_root_raises(self) -> None:
        with pytest.raises(ReproPackagerError):
            ReproducibilityPackager(root="", clock=lambda: _T0)


# ──────────────────────────────────────────────────────────────────────────────
# 校验（verify_package）
# ──────────────────────────────────────────────────────────────────────────────


class TestVerifyPackage:
    def test_verify_ok(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        pkg.build_package("exp-001", **_KW)
        assert pkg.verify_package("exp-001") is True

    def test_verify_tampered_returns_false(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        pkg.build_package("exp-001", **_KW)
        path = tmp_path / "repro" / "exp-001" / "manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["params"] = {"lr": 999}  # 篡改参数
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        assert pkg.verify_package("exp-001") is False

    def test_verify_unknown_exp_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).verify_package("ghost")

    def test_verify_malformed_json_raises(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        pkg.build_package("exp-001", **_KW)
        path = tmp_path / "repro" / "exp-001" / "manifest.json"
        path.write_text("{not-json", encoding="utf-8")
        with pytest.raises(ReproPackagerError):
            pkg.verify_package("exp-001")

    def test_verify_missing_field_raises(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        pkg.build_package("exp-001", **_KW)
        path = tmp_path / "repro" / "exp-001" / "manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        del payload["dep_lock_hash"]
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(ReproPackagerError):
            pkg.verify_package("exp-001")


# ──────────────────────────────────────────────────────────────────────────────
# 回放指针（resolve_replay_pointer）
# ──────────────────────────────────────────────────────────────────────────────


class TestResolveReplayPointer:
    def test_pointer_format(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        manifest = pkg.build_package("exp-001", **_KW)
        pointer = pkg.resolve_replay_pointer("exp-001")
        assert pointer == f"repro://exp-001@sha256:{manifest_digest(manifest)}"

    def test_pointer_deterministic(self, tmp_path) -> None:
        p1 = _packager(tmp_path / "a")
        p2 = _packager(tmp_path / "b")
        p1.build_package("exp-001", **_KW)
        p2.build_package("exp-001", **_KW)
        assert p1.resolve_replay_pointer("exp-001") == p2.resolve_replay_pointer("exp-001")

    def test_pointer_unknown_exp_raises(self, tmp_path) -> None:
        with pytest.raises(ReproPackagerError):
            _packager(tmp_path).resolve_replay_pointer("ghost")

    def test_pointer_tampered_raises(self, tmp_path) -> None:
        pkg = _packager(tmp_path)
        pkg.build_package("exp-001", **_KW)
        path = tmp_path / "repro" / "exp-001" / "manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["code_commit"] = "evil000"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        with pytest.raises(ReproPackagerError):
            pkg.resolve_replay_pointer("exp-001")
