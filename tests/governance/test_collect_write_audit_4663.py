# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.governance.test_collect_write_audit_4663
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.collect_write_audit_4663
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 4663 解析纯函数正确性：热目录命中/非热目录过滤/写删 op 判定/字段缺失降级
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
"""test_collect_write_audit_4663.py — SACL 4663 采集器解析层单测（#ARCH-279 裁定B3）。

只测纯函数 parse_4663_inserts（不触碰 Security 日志——读日志需管理员，
CI/测试环境无此前置）；win32evtlog 交互路径由 Owner 实机验证。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.governance.collect_write_audit_4663 import parse_4663_inserts  # noqa: E402

_ROOT = Path("D:/ZephyrAlpha")


def _inserts(object_name: str, access_mask: str = "0x2", object_type: str = "File") -> list[str]:
    """4663 实测 13 槽位布局（2026-08-27 Windows 11 dump 实证）。"""
    return [
        "S-1-5-18",  # 0 SubjectSid
        "fanzi",  # 1 SubjectUser
        "DESKTOP",  # 2 SubjectDomain
        "0x27adb",  # 3 LogonId
        "Security",  # 4 ObjectServer
        object_type,  # 5 ObjectType
        object_name,  # 6 ObjectName
        "0x15c",  # 7 HandleId
        "%%1537\n\n\t\t\t\t",  # 8 Accesses 列表占位
        access_mask,  # 9 AccessMask (hex)
        "0xdb0",  # 10 ProcessId (hex) = 3504
        "C:\\Windows\\System32\\notepad.exe",  # 11 ProcessName
        "S:AI",  # 12 ResourceAttributes
    ]


class TestParse4663:
    def test_hot_path_write_hit(self) -> None:
        """热目录写（WriteData 0x2）→ 命中，op=write，归因四要素齐备。"""
        rec = parse_4663_inserts(
            _inserts("D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\factor_registry.yaml"),
            _ROOT,
        )
        assert rec is not None
        assert rec["op"] == "write"
        assert rec["path"] == "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml"
        assert rec["sacl"]["user"] == "DESKTOP\\fanzi"
        assert rec["sacl"]["process_id"] == 0xDB0
        assert rec["sacl"]["process_name"].endswith("notepad.exe")

    def test_hot_path_delete_op(self) -> None:
        """DELETE 位（0x10000）→ op=delete。"""
        rec = parse_4663_inserts(
            _inserts("D:\\ZephyrAlpha\\.runtime\\quarantine\\drift_x\\a.md", "0x10000"),
            _ROOT,
        )
        assert rec is not None and rec["op"] == "delete"

    def test_design_memos_prefix(self) -> None:
        rec = parse_4663_inserts(
            _inserts(
                "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\07_trading_decision_architecture\\design_memos\\94_x.md"
            ),
            _ROOT,
        )
        assert rec is not None and rec["path"].startswith("docs/02_enterprise_architecture")

    def test_non_hot_path_filtered(self) -> None:
        """非热目录（src/ 等）→ None（审计量纪律：只收热目录集）。"""
        rec = parse_4663_inserts(_inserts("D:\\ZephyrAlpha\\src\\zephyr\\x.py"), _ROOT)
        assert rec is None

    def test_non_file_object_filtered(self) -> None:
        rec = parse_4663_inserts(_inserts("D:\\ZephyrAlpha\\docs\\x", object_type="Key"), _ROOT)
        assert rec is None

    def test_short_inserts_degrade(self) -> None:
        assert parse_4663_inserts(["only-one"], _ROOT) is None

    def test_bad_access_mask_degrade_to_access(self) -> None:
        rec = parse_4663_inserts(_inserts("D:\\ZephyrAlpha\\.runtime\\quarantine\\q\\a.md", "zz"), _ROOT)
        assert rec is not None and rec["op"] == "access"
