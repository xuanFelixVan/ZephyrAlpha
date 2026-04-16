#!/usr/bin/env python3
"""测试脚本：验证检查器能正确检测已知错误样本

用途: 确保 doc_guard_pre_commit.py 的检测逻辑有效
进度: 每次审计前必须运行，失败则报错退出

用法:
  python tests/test_faulty_samples.py
  python tests/test_faulty_samples.py --verbose
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPT_DIR = PROJECT_ROOT / "scripts"
SAMPLES_DIR = Path(__file__).parent / "faulty_samples"


class FaultySamplesTester:
    """已知错误样本库测试器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.passed = 0
        self.failed = 0

    def run_tests(self) -> bool:
        """运行所有样本测试"""
        print("=" * 70)
        print("测试：已知错误样本库")
        print("=" * 70)

        # Test 1: 双YAML样本
        if self._test_double_yaml_sample():
            self.passed += 1
        else:
            self.failed += 1

        # Test 2: doc_guard脚本基本功能
        if self._test_guard_script_basic():
            self.passed += 1
        else:
            self.failed += 1

        # 打印总结
        print("\n" + "=" * 70)
        print(f"测试结果: {self.passed}通过 | {self.failed}失败")
        print("=" * 70)

        return self.failed == 0

    def _test_double_yaml_sample(self) -> bool:
        """Test 1: 验证双YAML样本能被正确检测"""
        print("\n✓ 测试 1: 双YAML样本检测")
        print("  ├─ 样本文件: tests/faulty_samples/double-yaml-sample.md")

        # 直接导入检查器并测试样本文件
        import sys
        sys.path.insert(0, str(SCRIPT_DIR))
        from doc_guard_pre_commit import DocGuardChecker

        sample_file = SAMPLES_DIR / "double-yaml-sample.md"
        checker = DocGuardChecker(docs_root=SAMPLES_DIR)

        # 检查样本文件
        result = checker.check_double_yaml(sample_file)

        if result is not None:
            print(f"  ├─ ✅ 检测到双YAML问题")
            print(f"  ├─ 详情: {result['detail']}")
            if self.verbose:
                print(f"  ├─ 类型: {result['type']}")
                print(f"  ├─ 行号: {result['line']}")
            return True
        else:
            print(f"  ├─ ❌ 未能检测到双YAML问题")
            if self.verbose:
                # 调试模式：打印文件内容摘要
                print(f"  ├─ 文件大小: {sample_file.stat().st_size} 字节")
            return False

    def _test_guard_script_basic(self) -> bool:
        """Test 2: 验证guard脚本基本功能"""
        print("\n✓ 测试 2: doc_guard脚本基本功能")

        script_path = SCRIPT_DIR / "doc_guard_pre_commit.py"

        # 运行帮助命令
        result = subprocess.run(
            ["python", str(script_path), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode == 0 and "--scan-double-yaml" in result.stdout:
            print(f"  ├─ ✅ 脚本功能正常")
            return True
        else:
            print(f"  ├─ ❌ 脚本功能异常")
            print(f"  ├─ 返回码: {result.returncode}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="测试：已知错误样本库",
        epilog="用途: 保证检查脚本的可靠性。每次大规模审计前必须运行此测试。"
    )
    parser.add_argument("--verbose", action="store_true",
                        help="启用详细模式")

    args = parser.parse_args()

    tester = FaultySamplesTester(verbose=args.verbose)
    success = tester.run_tests()

    if not success:
        print("\n❌ 致命错误：样本测试失败!")
        print("   这意味着检查脚本可能无可靠，不应继续进行大规模审计。")
        print("   请修复脚本后重试。")
        sys.exit(1)
    else:
        print("\n✅ 所有样本测试通过!")
        print("   检查脚本已验证可靠，可以进行审计。")
        sys.exit(0)


if __name__ == "__main__":
    main()
