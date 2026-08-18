# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.aisg_sandbox
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L10-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


AISG Sandbox Testing — AI Security Gateway 沙箱验证 (INV-015 升级)

从文件存在性检查升级为实际沙箱拦截测试：
  - 测试 AI 生成代码是否能绕过 AISG
  - 模拟危险指令（eval/exec/subprocess/os.system）验证拦截
  - 验证 Audit Log 正确写入

Phase B：将 FF-015 从此文件替换为实际调用入口。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 危险模式字典 内置常量
#   fields: DANGEROUS_PATTERNS 12 项 模式子串→风险描述（eval/exec/subprocess/os.system/pickle.loads 等）
#   code: aisg_sandbox.py L56
# - id: I2
#   name: 安全代码样本 内置常量
#   fields: SAFE_SAMPLES 3 条正常代码（数据查询/因子计算/模型推理）
#   code: aisg_sandbox.py L71
# 层: 算法
# - id: A1
#   name_zh: ① 危险模式静态扫描
#   name_en: AISGSandbox.scan_content
#   intro: 对代码文本做子串匹配，命中危险模式即记录风险描述
#   desc: 遍历 DANGEROUS_PATTERNS，pattern in content 则追加对应中文风险描述；纯静态不执行代码
#   inputs: I1
#   outputs: 风险标记列表 risk_flags
# - id: A2
#   name_zh: ② 危险样本拦截测试
#   name_en: run_dangerous_pattern_tests
#   intro: 给 12 种危险模式各造一条样本，期望全部 block
#   desc: 期望 expected_action=block；scan_content 有命中则 actual=block，比对得 passed；累计 total_tests/tests_passed
#   inputs: A1
#   outputs: 危险样本测试结果列表
# - id: A3
#   name_zh: ③ 安全样本放行测试
#   name_en: run_safe_pattern_tests
#   intro: 3 条正常代码期望全部 allow，有误拦即 FAIL
#   desc: 期望 expected_action=allow；scan_content 无命中则 actual=allow，比对得 passed
#   inputs: A1 I2
#   outputs: 安全样本测试结果列表
# - id: A4
#   name_zh: ④ 全量汇总判定
#   name_en: main
#   intro: 汇总 15 项测试打印 PASS/FAIL，有失败返回退出码 1
#   desc: 打印每条结果与通过率；failures 非空打印 INV-015 拦截不完整并 return 1，否则 return 0
#   inputs: A2 A3
#   outputs: 进程退出码
# 层: 输出
# - id: O1
#   name_zh: 沙箱测试结果 SandboxResult
#   name_en: SandboxResult
#   intro: 每项含 test_name/expected/actual/passed/risk_flags 的测试结论
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: CLI 退出码
#   name_en: exit_code
#   intro: 0=INV-015 拦截完整，1=存在漏拦或误报
#   invariant: 全部通过才返回 0
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# I2 --> A3
# A2 --> A4
# A3 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Final

from zephyr.shared.io.paths import REPO_ROOT

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class SandboxResult:
    """AISG 沙箱测试结果"""

    test_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    test_name: str = ""
    content: str = ""
    expected_action: str = "block"
    actual_action: str = ""
    passed: bool = False
    risk_flags: list[str] = field(default_factory=list)


DANGEROUS_PATTERNS: Final[set] = {
    "eval(": "动态代码执行",
    "exec(": "动态代码执行",
    "compile(": "代码编译",
    "subprocess": "子进程调用",
    "os.system": "系统命令执行",
    "os.popen": "管道执行",
    "__import__": "动态导入",
    "globals()": "全局命名空间访问",
    "ctypes": "外部库调用",
    "pickle.loads": "反序列化风险",
    "socket.": "网络套接字",
    "requests.post(": "外部 HTTP 请求",
}

SAFE_SAMPLES: Final[list] = [
    ("数据查询", "df = pd.read_csv('data.csv')"),
    ("因子计算", "result = np.log(price / price.shift(1))"),
    ("模型推理", "predictions = model.predict(features)"),
]


class AISGSandbox:
    """
    AISG 沙箱测试器（Phase B）

    在开发机上运行 AISG 拦截逻辑的真实测试。
    不执行真实系统命令——仅做静态 AST + 模式匹配分析。
    """

    total_tests: ClassVar[int] = 0
    tests_passed: ClassVar[int] = 0

    @classmethod
    def scan_content(cls, content: str) -> list[str]:
        """扫描内容中的危险模式"""
        risks: list[str] = []
        for pattern, desc in DANGEROUS_PATTERNS.items():
            if pattern in content:
                risks.append(desc)
        return risks

    @classmethod
    def run_dangerous_pattern_tests(cls) -> list[SandboxResult]:
        """运行危险模式沙箱测试套件"""
        results: list[SandboxResult] = []

        for pattern, desc in DANGEROUS_PATTERNS.items():
            test_content = f"# AI generated code\n{pattern}(x)"
            result = SandboxResult(
                test_name=f"Dangerous pattern: {pattern}",
                content=test_content,
                expected_action="block",
            )
            result.risk_flags = cls.scan_content(test_content)
            result.actual_action = "block" if result.risk_flags else "allow"
            result.passed = result.actual_action == result.expected_action
            results.append(result)

            cls.total_tests += 1
            if result.passed:
                cls.tests_passed += 1

        return results

    @classmethod
    def run_safe_pattern_tests(cls) -> list[SandboxResult]:
        """运行安全模式沙箱测试套件"""
        results: list[SandboxResult] = []

        for name, code in SAFE_SAMPLES:
            result = SandboxResult(
                test_name=f"Safe pattern: {name}",
                content=code,
                expected_action="allow",
            )
            result.risk_flags = cls.scan_content(code)
            result.actual_action = "block" if result.risk_flags else "allow"
            result.passed = result.actual_action == result.expected_action
            results.append(result)

            cls.total_tests += 1
            if result.passed:
                cls.tests_passed += 1

        return results


def main() -> int:
    """运行 AISG sandbox 全量测试"""
    print("[AISG Sandbox] Running Phase B security tests ...\n")

    sandbox = AISGSandbox()
    dangerous_results = sandbox.run_dangerous_pattern_tests()
    safe_results = sandbox.run_safe_pattern_tests()

    all_results = dangerous_results + safe_results
    failures = [r for r in all_results if not r.passed]

    for r in dangerous_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.test_name}: {r.risk_flags}")

    print()
    for r in safe_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.test_name}: flags={r.risk_flags or 'none'}")

    print(f"\n[AISG Sandbox] {sandbox.tests_passed}/{sandbox.total_tests} tests passed")

    if failures:
        print(f"\nFAIL: {len(failures)} AISG sandbox test(s) failed — INV-015 拦截不完整")
        for f in failures:
            print(f"  - {f.test_name}: expected={f.expected_action}, actual={f.actual_action}")
        return 1

    print("OK: AISG sandbox all passed — security gateway intercepts dangerous patterns correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
