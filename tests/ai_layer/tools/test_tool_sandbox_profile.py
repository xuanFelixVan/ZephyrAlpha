# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools
# [MODULE] tests.ai_layer.tools.test_tool_sandbox_profile
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] config/tool_sandbox_profile.yaml（只读真源）; PyYAML（safe_load）
# [CONSUMERS] pytest tests/ai_layer/tools/test_tool_sandbox_profile.py；OBJ_T C5 验收「密钥零发放有测试+试用工具默认禁用」落点
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 生产 YAML 只读不写（测试禁写生产路径铁律）；断言全部钉 OBJ_T DESIGN §4.2/§4.3
#              预注册口径——default_enabled=false（试用默认禁用）、密钥零发放、禁写清单覆盖五
#              生产路径根、注入 probe 必跑、转正四判据名単冻结；改动即红
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §4.2/§4.3
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；profile 缺段→KeyError 红（fail-closed，禁静默默认）
# [TESTS] tests/ai_layer/tools/test_tool_sandbox_profile.py
# [TTL] permanent
"""test_tool_sandbox_profile — OBJ_T C5 验收：沙箱 profile 四闸结构钉值（默认禁用/零密钥/禁写清单/probe 必跑）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import yaml

REPO: Final = Path(__file__).resolve().parents[3]
PROFILE_PATH: Final = REPO / "config" / "tool_sandbox_profile.yaml"


def _load_profile() -> dict[str, Any]:
    with PROFILE_PATH.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    assert isinstance(doc, dict) and isinstance(doc.get("sandbox"), dict), "profile 缺 sandbox 段（fail-closed）"
    return doc["sandbox"]


def test_trial_tools_disabled_by_default() -> None:
    """试用工具会话内默认禁用、显式申请制（DESIGN §4.2）。"""
    assert _load_profile()["default_enabled"] is False


def test_zero_secret_issuance() -> None:
    """密钥零发放：issuance/secrets_py_read 双 forbidden（RULE-SECRETS；C5 验收项）。"""
    secrets = _load_profile()["secrets"]
    assert secrets["issuance"] == "forbidden"
    assert secrets["secrets_py_read"] == "forbidden"


def test_forbidden_write_paths_cover_production_roots() -> None:
    """禁写清单覆盖五生产路径根（config/src/scripts/tests/data）。"""
    forbidden = set(_load_profile()["isolation"]["forbidden_write_paths"])
    for root in ("config/", "src/", "scripts/", "tests/", "data/"):
        assert root in forbidden, f"禁写清单缺生产路径根: {root}"
    assert _load_profile()["isolation"]["production_db_access"] == "forbidden"


def test_injection_probe_required_and_network_boundaries() -> None:
    """注入 probe 必跑（C5 验收项）；网络=出网允许但实盘域与生产 DB 禁触。"""
    sandbox = _load_profile()
    assert sandbox["injection_review"]["injection_probe_required"] is True
    assert sandbox["injection_review"]["tool_description_trust"] == "untrusted"
    assert sandbox["network"]["outbound"] == "allowed"
    assert "live_trading_domain" in sandbox["network"]["forbidden_targets"]
    assert "production_database" in sandbox["network"]["forbidden_targets"]


def test_trial_window_and_promotion_criteria_frozen() -> None:
    """试用窗口常数与转正四判据名单冻结（DESIGN §4.2/§4.3 预注册口径）。"""
    trial = _load_profile()["trial"]
    assert trial["status_word"] == "trial"
    assert trial["max_days"] == 14
    assert trial["min_tasks"] == 3
    assert _load_profile()["promotion_criteria"] == [
        "safety_review_cleared",
        "benchmark_noninferior",
        "resource_profile_registered",
        "pitfall_written_back",
    ]
    assert _load_profile()["fail_close"] == "tombstone"
