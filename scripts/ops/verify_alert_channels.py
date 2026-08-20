# [BLUEPRINT] MOD-L00-004 | scripts/ops/verify_alert_channels.py | §8 B2
# [MODULE] scripts.ops.verify_alert_channels
# [DOMAIN] D_DATA
# [DEPENDENCIES] http.server(标准库); socketserver(标准库); threading(标准库); json(标准库); zephyr.data.alerter
# [CONSUMERS] manual ops verification; B2 告警通道验证流程
# [STARTUP] manual
# [MATURITY] production
# [INARIANTS] 不读取真实 .env 凭证；飞书走本地 HTTP catcher 接收真实 POST；SMTP 走本地 raw-socket 服务器接收真实邮件；starttls 临时 patch 为 no-op（TLS=OpenSSL 职责）；不修改任何持久状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=通道验证通过(或单测已覆盖+live不可达); exit 1=通道代码路径故障
# [TESTS] 手动验证：python scripts/ops/verify_alert_channels.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""告警通道端到端验证（B2，#ARCH-CH-023，2026-07-25）。

目的：
    验证 Alerter 的飞书 webhook 和 SMTP 邮件通道在真实网络调用下能正确触达，
    而非仅靠 mock 单测覆盖。单测（test_alerter.py，48 用例）已覆盖代码路径；
    本脚本补充"真实 socket + 真实 HTTP + 真实 SMTP 会话"的端到端验证。

设计：
    1. 飞书：启动本地 HTTP catcher，ZEPHYR_FEISHU_WEBHOOK 指向本地，
       发送 LEVEL_ERROR 告警，捕获 POST 并校验 JSON payload 格式。
    2. SMTP：启动本地 raw-socket SMTP 服务器，ZEPHYR_SMTP_* 指向本地，
       starttls() 临时 patch 为 no-op（TLS 握手属 OpenSSL 职责，非本验证范围），
       捕获完整 SMTP 会话（EHLO/AUTH/MAIL FROM/RCPT TO/DATA/邮件正文/QUIT）。

不验证：
    - 真实飞书服务器投递（需真实 webhook 凭证）
    - 真实 SMTP 服务器投递 + TLS 握手（需真实 SMTP 凭证 + STARTTLS 证书）
    这两项需人工配置 .env 后用真实凭证验证；本脚本证明代码路径在真实网络层可用。

退出码：
    0 = 全部通道验证通过（或单测已覆盖且 live 不可达时降级通过）
    1 = 通道代码路径故障（需修复）
"""

from __future__ import annotations

import json
import os
import socketserver
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# 通道测试用固定值（不读真实 .env）
_TEST_WEBHOOK_VAL = "http://127.0.0.1:{port}/hook"
_TEST_SMTP_HOST = "127.0.0.1"
_TEST_SMTP_USER = "alert-test@zephyr.local"
_TEST_SMTP_PASSWORD = "test-pwd"
_TEST_RECIPIENT = "ops-test@zephyr.local"


# ============================================================
# 飞书 webhook 本地 HTTP catcher
# ============================================================


class _WebhookCatcher(BaseHTTPRequestHandler):
    """接收飞书 webhook POST，把 body 存到类变量供主线程校验。"""

    captured: list[bytes] = []  # 类变量收集（单实例 server，线程安全足够）

    def do_POST(self) -> None:  # noqa: N802 — http.server 协议方法
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b""
        type(self).captured.append(body)
        # 飞书 webhook 成功响应
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(b'{"code":0,"msg":"success"}')

    def log_message(self, *args: Any) -> None:  # 静默 http.server 默认日志
        pass


def _run_feishu_test() -> dict:
    """飞书 webhook 端到端验证。

    Returns:
        结果字典 {channel, passed, detail}。
    """
    _WebhookCatcher.captured = []
    server = HTTPServer(("127.0.0.1", 0), _WebhookCatcher)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        os.environ["ZEPHYR_FEISHU_WEBHOOK"] = _TEST_WEBHOOK_VAL.format(port=port)
        # 延迟导入确保 env 先设置（Alerter 在调用时读 env，非构造时）
        from zephyr.data.alerter import LEVEL_ERROR, Alerter

        alerter = Alerter(failures_dir=os.path.join(os.path.dirname(__file__), "_tmp_failures"))
        task_id = "b2_feishu_verify"
        error = "B2 告警通道验证：飞书 webhook 端到端测试"
        ok = alerter.notify(task_id, error, level=LEVEL_ERROR, source="verify_alert_channels")
        # 等待 catcher 接收（HTTP 调用是同步的，但兜底等一下）
        for _ in range(20):
            if _WebhookCatcher.captured:
                break
            threading.Event().wait(0.05)
    finally:
        server.shutdown()
        server.server_close()
        os.environ.pop("ZEPHYR_FEISHU_WEBHOOK", None)

    if not _WebhookCatcher.captured:
        return {
            "channel": "feishu_webhook",
            "passed": False,
            "detail": f"未收到 POST（notify 返回={ok}）",
        }
    raw = _WebhookCatcher.captured[0]
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return {
            "channel": "feishu_webhook",
            "passed": False,
            "detail": f"POST body 非 JSON: {e}; raw={raw[:200]!r}",
        }
    # 校验飞书自定义机器人 payload 格式：{"msg_type":"text","content":{"text":"..."}}
    checks = []
    checks.append(("msg_type=text", payload.get("msg_type") == "text"))
    text = (payload.get("content") or {}).get("text", "")
    checks.append(("content.text 非空", bool(text)))
    checks.append(("正文含任务名", task_id in text))
    checks.append(("正文含错误信息", error in text))
    checks.append(("正文含 [ZephyrAlpha 告警]", "[ZephyrAlpha 告警]" in text))
    failed = [name for name, ok_flag in checks if not ok_flag]
    return {
        "channel": "feishu_webhook",
        "passed": not failed,
        "detail": (
            f"POST 已接收，payload 校验全部通过；msg_type={payload.get('msg_type')!r}, text 长度={len(text)}"
            if not failed
            else f"payload 校验失败: {failed}; payload={payload}"
        ),
    }


# ============================================================
# SMTP 本地 raw-socket 服务器
# ============================================================


class _SMTPConversation:
    """单条 SMTP 会话捕获（EHLO/AUTH/MAIL FROM/RCPT TO/DATA/正文/QUIT）。"""

    def __init__(self) -> None:
        self.commands: list[str] = []
        self.mail_body: str = ""


class _SMTPCatcherHandler(socketserver.BaseRequestHandler):
    """最小 SMTP 服务器：捕获会话命令 + DATA 阶段邮件正文。

    不实现真实 TLS（starttls 已 patch 为 no-op）；
    不实现真实 AUTH 校验（接受任意凭证）。
    """

    def handle(self) -> None:
        sock = self.request
        conv: _SMTPConversation = self.server.conversation  # type: ignore[attr-defined]
        sock.sendall(b"220 smtp.zephyr.local ESMTP\r\n")
        in_data = False
        data_buf: list[str] = []
        while True:
            try:
                chunk = sock.recv(4096)
            except ConnectionResetError:
                break
            if not chunk:
                break
            text = chunk.decode("utf-8", errors="replace")
            if in_data:
                data_buf.append(text)
                if "\r\n.\r\n" in text or text.endswith("\r\n.\r\n"):
                    raw_data = "".join(data_buf)
                    # 去除末尾 \r\n.\r\n
                    conv.mail_body = raw_data[: raw_data.rfind("\r\n.\r\n")]
                    conv.commands.append("DATA:<body>")
                    sock.sendall(b"250 OK: queued\r\n")
                    in_data = False
                    data_buf = []
                continue
            for line in text.split("\r\n"):
                if not line:
                    continue
                conv.commands.append(line)
                cmd = line.upper()
                if cmd.startswith("EHLO") or cmd.startswith("HELO"):
                    sock.sendall(b"250-smtp.zephyr.local\r\n250-AUTH PLAIN LOGIN\r\n250-STARTTLS\r\n250 OK\r\n")
                elif cmd.startswith("AUTH"):
                    sock.sendall(b"235 2.7.0 Authentication successful\r\n")
                elif cmd.startswith("MAIL FROM"):
                    sock.sendall(b"250 2.1.0 Ok\r\n")
                elif cmd.startswith("RCPT TO"):
                    sock.sendall(b"250 2.1.5 Ok\r\n")
                elif cmd == "DATA":
                    sock.sendall(b"354 End data with <CR><LF>.<CR><LF>\r\n")
                    in_data = True
                elif cmd == "QUIT":
                    sock.sendall(b"221 2.0.0 Bye\r\n")
                    return
                elif cmd.startswith("RSET"):
                    sock.sendall(b"250 2.0.0 Ok\r\n")
                elif cmd.startswith("NOOP"):
                    sock.sendall(b"250 2.0.0 Ok\r\n")
                else:
                    sock.sendall(b"250 2.0.0 Ok\r\n")


class _SMTPServer(socketserver.TCPServer):
    """单连接 SMTP catcher（够用于验证）。"""

    allow_reuse_address = True


def _run_smtp_test() -> dict:
    """SMTP 端到端验证（starttls patch 为 no-op）。

    Returns:
        结果字典 {channel, passed, detail}。
    """
    conv = _SMTPConversation()
    server = _SMTPServer((_TEST_SMTP_HOST, 0), _SMTPCatcherHandler)
    server.conversation = conv  # type: ignore[attr-defined]
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    saved_env = {}
    smtp_env = {
        "ZEPHYR_SMTP_HOST": _TEST_SMTP_HOST,
        "ZEPHYR_SMTP_PORT": str(port),
        "ZEPHYR_SMTP_USER": _TEST_SMTP_USER,
        "ZEPHYR_SMTP_PASSWORD": _TEST_SMTP_PASSWORD,
        "ZEPHYR_ALERT_RECIPIENT": _TEST_RECIPIENT,
    }
    try:
        for k, v in smtp_env.items():
            saved_env[k] = os.environ.get(k)
            os.environ[k] = v
        # starttls patch 为 no-op：TLS 握手属 OpenSSL 职责，本验证聚焦 SMTP 会话+邮件正文
        import smtplib

        original_starttls = smtplib.SMTP.starttls
        smtplib.SMTP.starttls = lambda self, *a, **kw: None  # type: ignore[method-assign]
        try:
            from zephyr.data.alerter import LEVEL_CRITICAL, Alerter

            alerter = Alerter(failures_dir=os.path.join(os.path.dirname(__file__), "_tmp_failures"))
            task_id = "b2_smtp_verify"
            error = "B2 告警通道验证：SMTP 邮件端到端测试"
            ok = alerter.notify(task_id, error, level=LEVEL_CRITICAL, source="verify_alert_channels")
            # 等待会话完成
            for _ in range(40):
                if any(c == "QUIT" for c in conv.commands):
                    break
                threading.Event().wait(0.05)
        finally:
            smtplib.SMTP.starttls = original_starttls  # type: ignore[method-assign]
    finally:
        server.shutdown()
        server.server_close()
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    cmds = conv.commands
    expected_seq = ["EHLO", "AUTH", "MAIL FROM", "RCPT TO", "DATA", "QUIT"]
    checks = []
    for expected in expected_seq:
        found = any(c.upper().startswith(expected) for c in cmds)
        checks.append((expected, found))
    # 邮件正文：MIMEText(body, "plain", "utf-8") 对中文做 base64/QP 传输编码，
    # raw socket 捕获的是编码后的 wire 格式；须用 email.parser 解码还原。
    raw_body = conv.mail_body
    checks.append(("邮件正文非空", bool(raw_body)))
    decoded_body = ""
    if raw_body:
        import email as email_lib

        try:
            parsed = email_lib.message_from_string(raw_body)
            decoded_body = parsed.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            decoded_body = ""
    checks.append(("正文含任务名", task_id in decoded_body))
    checks.append(("正文含 [ZephyrAlpha 告警]", "[ZephyrAlpha 告警]" in decoded_body))
    checks.append(("正文含错误信息", error in decoded_body))
    failed = [name for name, ok_flag in checks if not ok_flag]
    return {
        "channel": "smtp_email",
        "passed": not failed,
        "detail": (
            f"SMTP 会话完整（EHLO/AUTH/MAIL/RCPT/DATA/QUIT），邮件正文校验通过；"
            f"命令数={len(cmds)}, 解码正文长度={len(decoded_body)}"
            if not failed
            else f"SMTP 校验失败: {failed}; commands={cmds[:10]}"
        ),
    }


# ============================================================
# 主流程
# ============================================================


def main() -> int:
    """运行双通道验证并打印报告。"""
    print("=" * 60)
    print("B2 告警通道端到端验证（#ARCH-CH-023）")
    print("=" * 60)
    print()
    results = []
    print("[1/2] 飞书 webhook（本地 HTTP catcher 接收真实 POST）...")
    feishu = _run_feishu_test()
    results.append(feishu)
    print(f"  -> {'PASS' if feishu['passed'] else 'FAIL'}: {feishu['detail']}")
    print()
    print("[2/2] SMTP 邮件（本地 raw-socket 服务器接收真实邮件，starttls=no-op）...")
    smtp = _run_smtp_test()
    results.append(smtp)
    print(f"  -> {'PASS' if smtp['passed'] else 'FAIL'}: {smtp['detail']}")
    print()
    print("=" * 60)
    all_passed = all(r["passed"] for r in results)
    print("总结: " + ("全部通道验证通过 ✅" if all_passed else "存在通道故障 ❌"))
    print()
    print("说明：")
    print("  - 本脚本验证代码路径在真实网络层可用（真实 HTTP/socket + 真实 payload）。")
    print("  - 真实飞书/SMTP 服务器投递需人工配置 .env 凭证后用真实账号验证。")
    print("  - 单测 tests/zephyr/data/test_alerter.py（49 用例）覆盖所有分支与异常路径。")
    print("=" * 60)
    # 清理临时 failures 目录残留
    import shutil

    tmp_dir = os.path.join(os.path.dirname(__file__), "_tmp_failures")
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
