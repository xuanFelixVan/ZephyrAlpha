# [A_test] module_id: MOD-GOV-047-TEST-FEMAP-R2-VERSIONING | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.d5_architecture.test_check_frontend_map_r2_versioning
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; check_frontend_map（sys.path 动态加载——判据单一真源）
# [CONSUMERS] pytest 自动发现
# [INVARIANTS] R2 升级红蓝（R4 st-govjudge-20261010）：无标条目 module_id 缺 manifest=fail；
#   criteria_version=v1 存量=warn 不重审（G4-5）；auto_scanned 豁免不变；真仓 fail=0 不回退
# [TTL] permanent
"""check_frontend_map R2 升级版本化对抗测试（R4 frontend 半件）。

G4-5 判据版本化语义锁：新判据（R2 warn→fail）适用新考生（无 criteria_version 标注条目），
存量（criteria_version: v1）标注口径不重审保持 warn，升级路径=逐页复核转正后摘标。
判据真源=check_frontend_map._check_feature（gate 只做阻塞封装，禁复制）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_CHECKERS_DIR = Path(__file__).resolve().parents[4] / "scripts" / "governance" / "d5_architecture" / "generators"
if str(_CHECKERS_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECKERS_DIR))

import check_frontend_map as cfm  # noqa: E402


def _check_one(entry: dict, mf_ids: set[str]) -> tuple[list[str], list[str]]:
    fails: list[str] = []
    warns: list[str] = []
    cfm._check_feature(entry, mf_ids, warns, fails)
    return fails, warns


_MF_IDS = {"mod-real"}


def _entry(**over) -> dict:
    base = {
        "id": "F-TEST-X",
        "module_id": "mod-missing",
        "file": "features/x/x.js",
        "backend_ref": "module:mod-real",
        "status": "active",
    }
    base.update(over)
    return base


def test_r2_new_entry_module_missing_is_fail() -> None:
    """无标注条目（现行口径）：module_id 缺 manifest ⇒ R2 升 fail（阻塞面）。"""
    fails, warns = _check_one(_entry(), _MF_IDS)
    assert any(x.startswith("R2 F-TEST-X") for x in fails), fails
    assert not any(x.startswith("R2") for x in warns)


def test_r2_legacy_v1_entry_stays_warn() -> None:
    """criteria_version=v1 存量条目：同病灶保持 warn 不重审（G4-5），且注记在案。"""
    fails, warns = _check_one(_entry(criteria_version="v1"), _MF_IDS)
    assert not fails
    assert any(x.startswith("R2 F-TEST-X") and "criteria_version=v1" in x for x in warns), warns


def test_r2_auto_scanned_exempt_unchanged() -> None:
    """auto_scanned 豁免不变：无 module_id 缺 manifest 告警（原语义零回归）。"""
    fails, warns = _check_one(_entry(auto_scanned=True), _MF_IDS)
    assert not fails and not any(x.startswith("R2") for x in warns)


def test_real_repo_fail_stays_zero() -> None:
    """真仓 fail=0 不回退（存量已全量 v1 标注；蓝案钉扎——新违例进真仓即红）。"""
    fails, warns, total = cfm.run_checks()
    assert total > 0
    assert fails == [], f"真仓出现 R2 升级后 fail（存量标注漏标或新违例）: {fails[:5]}"
