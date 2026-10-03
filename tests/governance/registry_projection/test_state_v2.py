# [A_test] module_id: MOD-GOV_registry_projection_state | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.registry_projection.test_state_v2
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""PD-1 v2 状态文件：多册 map 键控读写/upsert 保他册/v1 兼容读+首写迁移/损坏降级。"""

from __future__ import annotations

import json

import pytest

from zephyr.governance.registry_projection.state import (
    ProjectionState,
    load_all,
    load_state,
    save_state,
    state_path,
)

PATH_A = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
PATH_B = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"


def _state(path: str, sha: str, revision: int = 7) -> ProjectionState:
    return ProjectionState(
        content_sha256=sha, ledger_revision=revision, registry_path=path, entry_counts={"entries": 3}, generated_at="t"
    )


def test_v2_multi_registry_roundtrip(tmp_path):
    save_state(tmp_path, _state(PATH_A, "sha-a"))
    save_state(tmp_path, _state(PATH_B, "sha-b", revision=9))

    all_entries = load_all(tmp_path)
    assert set(all_entries) == {PATH_A, PATH_B}

    a = load_state(tmp_path, registry_path=PATH_A)
    b = load_state(tmp_path, registry_path=PATH_B)
    assert a is not None and a.content_sha256 == "sha-a"
    assert b is not None and b.ledger_revision == 9

    # 缺省参：多册→None（v1 单条语义不再成立），单册→唯一条目
    assert load_state(tmp_path) is None
    only = load_state(tmp_path, registry_path=PATH_A)
    assert only is not None and only.registry_path == PATH_A


def test_v2_upsert_preserves_other_registry(tmp_path):
    save_state(tmp_path, _state(PATH_A, "sha-a1"))
    save_state(tmp_path, _state(PATH_B, "sha-b"))
    save_state(tmp_path, _state(PATH_A, "sha-a2", revision=8))

    all_entries = load_all(tmp_path)
    assert all_entries[PATH_A].content_sha256 == "sha-a2"
    assert all_entries[PATH_A].ledger_revision == 8
    assert all_entries[PATH_B].content_sha256 == "sha-b"  # 他册条目不被覆盖


def test_v1_legacy_read_and_first_write_migrates(tmp_path):
    legacy = _state(PATH_A, "sha-legacy").to_dict()
    path = state_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")

    all_entries = load_all(tmp_path)
    assert set(all_entries) == {PATH_A}
    assert load_state(tmp_path) is not None  # v1 唯一条目兼容语义

    save_state(tmp_path, _state(PATH_B, "sha-b"))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("version") == 2 and set(data.get("registries", {})) == {PATH_A, PATH_B}


def test_corrupt_entries_degrade_open(tmp_path):
    path = state_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not-json", encoding="utf-8")
    assert load_all(tmp_path) == {}
    assert load_state(tmp_path, registry_path=PATH_A) is None

    payload = {
        "version": 2,
        "registries": {PATH_A: _state(PATH_A, "sha-a").to_dict(), PATH_B: {"broken": True}},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    all_entries = load_all(tmp_path)
    assert set(all_entries) == {PATH_A}  # 单条损坏只跳该册


def test_save_rejects_empty_registry_path(tmp_path):
    with pytest.raises(ValueError):
        save_state(tmp_path, _state("", "sha-x"))


def test_path_canonicalization(tmp_path):
    save_state(tmp_path, _state(PATH_A, "sha-a"))
    assert load_state(tmp_path, registry_path=f"./{PATH_A}") is not None
    assert load_state(tmp_path, registry_path=PATH_A.replace("/", "\\")) is not None
