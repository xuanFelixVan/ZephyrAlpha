# tests/governance/commit_gates conftest —— 测试目录已因 GOV-DOC-018 约定文档持有
# __init__.py（包化），pytest prepend 模式下同目录模块不再自动可导；
# 此处显式注入测试目录，恢复 gate_test_helpers 的 `import gate_test_helpers` 直导。
import sys
from pathlib import Path

_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
