# [BLUEPRINT] MOD-GOV_SERVE_DOCS
# [MODULE] scripts.serve_docs
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] 人工查看派生架构文档（域文档/项目树/HTML）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_SERVE_DOCS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  本地文档HTTP服务按需启动,非cron/daemon常驻服务
"""本地文档服务：按需重生成派生架构文档 + 启动 HTTP 服务器浏览。

治本（#ARCH-GOV-BUDGET-001 / I-GOV-1，2026-08-05）：
派生产物（域文档、项目树）已从 git 离库，源真源（depgraph DB + 生成器代码）已跟踪。
本脚本提供"按需生成 + 本地浏览"工作流，替代原"派生产物入 git + reconciler auto-commit"的
非收敛循环模式。

用法：
    python scripts/serve_docs.py              # 重生成全部派生文档 + 启动 HTTP 服务
    python scripts/serve_docs.py --no-regen   # 仅启动 HTTP 服务（不重生成）
    python scripts/serve_docs.py --regen-only # 仅重生成，不启动服务

HTTP 服务监听 127.0.0.1:8765，服务仓库根目录。浏览器访问：
    http://127.0.0.1:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/README.md
    http://127.0.0.1:8765/docs/02_enterprise_architecture/01_global_architecture_diagram/

[MODULE] scripts.serve_docs
[INVARIANTS] 不修改 git index；生成器幂等（多次跑无副作用）；HTTP 服务仅监听 127.0.0.1
[CONSUMERS] 人工查看派生架构文档（域文档/项目树/HTML）
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 生成器失败 → 打印错误继续（不阻断 HTTP 服务）；端口占用 → 提示换端口
[TESTS] 手工验证
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

import argparse
import http.server
import socketserver
import subprocess
import sys
import threading

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
PORT = 8765
GENERATORS = [
    # (描述, 命令)
    ("path_tree（项目树 zh/en）",
     [sys.executable, "scripts/governance/d5_architecture/generators/generate_path_tree.py"]),
    ("domain_doc --all（72 域文档 + HTML）",
     [sys.executable, "scripts/governance/d5_architecture/generators/generate_domain_doc.py", "--all"]),
]


def regenerate_derived_docs() -> int:
    """按需重生成派生架构文档。返回失败计数。"""
    failures = 0
    for desc, cmd in GENERATORS:
        print(f"  → 重生成 {desc} ...", flush=True)
        r = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,  # noqa: bare-subprocess  本地文档HTTP服务按需生成,非线上治理代码
                           encoding="utf-8", errors="replace", timeout=300)
        if r.returncode != 0:
            failures += 1
            print(f"    ❌ 失败: {r.stderr.strip()[:300]}", flush=True)
        else:
            # 打印生成器最后一行成功信息
            last_line = (r.stdout or "").strip().splitlines()[-1] if r.stdout else "ok"
            print(f"    ✅ {last_line}", flush=True)
    return failures


def serve_http(port: int) -> None:
    """启动本地 HTTP 服务，服务仓库根目录。"""
    handler = http.server.SimpleHTTPRequestHandler
    # 静态服务器无 Cache-Control，浏览器启发式缓存会让用户看到旧版 HTML。
    # 加 no-cache 头强制重验证（与 zoomable_html.py 一致）。
    class NoCacheHandler(handler):
        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-cache, must-revalidate")
            super().end_headers()

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    print(f"\n🌐 HTTP 服务启动: http://127.0.0.1:{port}/", flush=True)
    print(f"   服务根目录: {REPO_ROOT}", flush=True)
    print(f"   浏览器入口:", flush=True)
    print(f"   - 域文档: http://127.0.0.1:{port}/docs/02_enterprise_architecture/02_domain_architecture_docs/README.md", flush=True)
    print(f"   - 全局图: http://127.0.0.1:{port}/docs/02_enterprise_architecture/01_global_architecture_diagram/", flush=True)
    print(f"\n   Ctrl+C 停止服务。\n", flush=True)

    with ReusableTCPServer(("127.0.0.1", port), NoCacheHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止。", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="派生架构文档按需生成 + 本地 HTTP 浏览（治本 #ARCH-GOV-BUDGET-001 / I-GOV-1）"
    )
    parser.add_argument("--no-regen", action="store_true", help="不重生成，仅启动 HTTP 服务")
    parser.add_argument("--regen-only", action="store_true", help="仅重生成，不启动 HTTP 服务")
    parser.add_argument("--port", type=int, default=PORT, help=f"HTTP 服务端口（默认 {PORT}）")
    args = parser.parse_args()

    if not args.no_regen:
        print("=== 重生成派生架构文档（治本 #ARCH-GOV-BUDGET-001：派生产物离库，按需生成）===", flush=True)
        failures = regenerate_derived_docs()
        if failures:
            print(f"\n⚠️  {failures} 个生成器失败，但继续启动 HTTP 服务（已生成的文档仍可查看）", flush=True)
        else:
            print("\n✅ 全部生成器成功", flush=True)

    if not args.regen_only:
        serve_http(args.port)

    return 0


if __name__ == "__main__":
    sys.exit(main())
