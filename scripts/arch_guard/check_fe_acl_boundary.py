"""
check_fe_acl_boundary.py — 前端 ACL 边界检查 (INV-006) [桩文件]

INV-006: 前后端唯一接触点——前端只能通过 L08 api_gateway 访问后端。
status: stub — 需 L08 API Gateway 完整实现后激活。

激活条件：
  1. L08 API Gateway 有可检测的路由层代码
  2. 前端代码（React/Next.js）有明确的 API 调用点
  3. 可通过 import / API call 路径检测到绕过的直接调用
"""
import sys


def main() -> int:
    print("⏭ INV-006 前端 ACL 边界检查 —— [桩文件] 跳过")
    print("   激活条件：L08 API Gateway 完整实现。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
