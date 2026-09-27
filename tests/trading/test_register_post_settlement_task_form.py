# [A_test] module_id: MOD-SCRIPT-register_post_settlement_task | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SCRIPT-register_post_settlement_task | docs/03_modules/ | §test
# [MODULE] tests.trading.test_register_post_settlement_task_form
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [TTL] permanent
"""PostSettlement 注册脚本形态静态断言（zc-lane-k-20260927，F76 S1 活雷防复发）。

病根（bc76efe3bf 回退事故）：action 块被回退成裸 ``python.exe`` 直挂 -Execute、
shell 重定向 token（``>> log 2>&1``）当 -Argument——python 把它们当位置参数吞掉，
argparse exit 2，Owner 批准的 15:30 结算自动化自注册起一次都没跑成。
修复形态（8f0e5feba9 回植，a0446129e3 逆转回退）= conhost --headless + cmd /c
真重定向。

本测试只做文件形态静态断言（零 schtasks 写操作——重注册=Owner 门），
守"未来重注册安全"：任何把 action 块退回坏形态的改动（含提交连坐吸收）
在此红。守卫语义锚=M5 04 册 §三.5 注册脚本↔live 漂移横断病。
"""

from __future__ import annotations

from pathlib import Path

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "register_post_settlement_task.ps1"


@pytest.fixture(scope="module")
def script_text() -> str:
    assert _SCRIPT_PATH.exists(), f"注册脚本缺失: {_SCRIPT_PATH}"
    return _SCRIPT_PATH.read_text(encoding="utf-8")


class TestActionBlockGoodForm:
    """action 块必须保持 conhost + cmd /c 真重定向修复形态。"""

    def test_landmine_python_direct_execute_absent(self, script_text: str) -> None:
        """坏形态活雷断言：python.exe 不得直挂 -Execute（bc76efe3bf 回退形态）。

        裸 python 直挂 + 重定向 token 当 -Argument = argparse exit 2 假语法，
        自动化静默空转——本断言是 S1 活雷的长期地雷探测器。
        """
        assert "New-ScheduledTaskAction -Execute $pythonExe" not in script_text, (
            "注册脚本 action 块退回坏形态：python.exe 直挂 -Execute "
            "（重定向 token 会被 python 当位置参数吞掉，argparse exit 2，"
            "结算自动化静默不跑——bc76efe3bf 回退事故复燃）"
        )

    def test_conhost_headless_wrapper_present(self, script_text: str) -> None:
        """修复形态①：conhost --headless 包裹（15:30 运行无窗口）。"""
        assert "New-ScheduledTaskAction -Execute $conhost" in script_text
        assert "--headless" in script_text

    def test_cmd_c_real_redirection_present(self, script_text: str) -> None:
        """修复形态②：cmd /c 内做真重定向（>> log 2>&1 是 shell 语义非 python 参数）。"""
        assert "/c cd /d" in script_text
        assert ">> " in script_text
        assert "2>&1" in script_text
        # python 以 -u 无缓冲经 cmd 内引号路径调用（真执行体在 cmd 行内）
        assert '" -u "' in script_text


class TestRegistrationSafetySemantics:
    """重注册安全语义：in-place 更新不 unregister + 触发器口径不漂移。"""

    def test_in_place_update_without_unregister(self, script_text: str) -> None:
        """已存在任务走 Set-ScheduledTask 原位更新（M5 in-place Set 铁律）。"""
        assert "Set-ScheduledTask" in script_text
        assert "Register-ScheduledTask" in script_text
        assert "Unregister-ScheduledTask" not in script_text

    def test_weekday_1530_trigger_unchanged(self, script_text: str) -> None:
        """触发器=工作日 15:30（结算硬时点，口径漂移即与下游对账错位）。"""
        assert '-At "15:30"' in script_text
        assert "Monday,Tuesday,Wednesday,Thursday,Friday" in script_text

    def test_settlement_overlap_and_hang_guards(self, script_text: str) -> None:
        """MultipleInstances IgnoreNew（结算不重叠）+ ExecutionTimeLimit（挂死被 OS 杀）。"""
        assert "IgnoreNew" in script_text
        assert "ExecutionTimeLimit" in script_text

    def test_script_is_pure_ascii(self, script_text: str) -> None:
        """PowerShell 5.1 无 BOM 按 GBK 解码（宪法 §9.7）：.ps1 必须纯 ASCII。"""
        non_ascii = [f"U+{ord(ch):04X}" for ch in script_text if ord(ch) > 127]
        assert not non_ascii, f"脚本含非 ASCII 字符: {non_ascii[:5]}"
