# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.alerter
# [DOMAIN] D_DATA
# [DEPENDENCIES] logging(标准库); pathlib; urllib.request(标准库,飞书webhook); smtplib(标准库,邮件); email.mime(标准库,邮件); zephyr.shared.security.secrets
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 失败汇总文件写到 failures/ 目录; 告警级别 INFO/WARN/ERROR/CRITICAL; 不抛异常(所有错误log后吞掉); ERROR/CRITICAL触达飞书webhook+SMTP邮件(未配置则静默跳过)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] notify失败->log+不抛异常; check_*返回bool不抛异常; 通道发送失败->log后吞掉不影响主流程
# [TESTS] tests/zephyr/data/test_alerter.py
# [A_module] module_id=MOD-GOV-alerter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性）。

告警触发条件（蓝图 §6.5）：
- 任务 DEAD（重试耗尽）-> 立即告警
- 单日失败率 > 5% -> 汇总告警
- 某数据源连续 3 天失败 -> 升级告警

告警方式：
- 日志（logging，输出到 logs/integrator.log）
- 失败汇总文件（failures/{date}_{task_id}.json）
- 飞书 webhook（ZEPHYR_FEISHU_WEBHOOK，未配置则静默跳过）—— audit 8.3 #ARCH-DATA-PIPELINE-001
- SMTP 邮件（ZEPHYR_SMTP_*，未配置则静默跳过）—— audit 8.3 #ARCH-DATA-PIPELINE-001

设计要点：
- 所有方法不抛异常（告警失败不应影响主流程）
- 失败汇总文件用 JSON 格式，便于 CLI 读取和重跑
- 线程安全（threading.Lock 保护文件写入）
- ERROR/CRITICAL 告警在 failure file 实际写入后触达 IM/邮件通道（与 300s
  冷却对齐，防 crash-restart 循环刷屏）
- 通道密钥走 .env（禁止入库），见 .env.example ZEPHYR_FEISHU_WEBHOOK / ZEPHYR_SMTP_*
"""

from __future__ import annotations

import datetime
import json
import logging
import smtplib
import threading
import urllib.error
import urllib.request
from email.header import Header
from email.mime.text import MIMEText
from pathlib import Path
from typing import Final, Optional

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.security.secrets import get_secret_or_default
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

_DEFAULT_FAILURES_DIR = REPO_ROOT / "data" / "failures"

# 同一 task_id 失败文件的最小间隔（秒）：防止 crash-restart 循环刷出海量 failure 文件
_FAILURE_COOLDOWN_SEC: Final[int] = 300

# 告警级别
LEVEL_INFO: Final[str] = "INFO"
LEVEL_WARN: Final[str] = "WARN"
LEVEL_ERROR: Final[str] = "ERROR"
LEVEL_CRITICAL: Final[str] = "CRITICAL"

# --- 告警通道配置（audit 8.3，#ARCH-DATA-PIPELINE-001，2026-07-23）---
# 密钥走 .env（禁止入库）；未配置的通道静默跳过。
_FEISHU_WEBHOOK_ENV: Final[str] = "ZEPHYR_FEISHU_WEBHOOK"
_SMTP_HOST_ENV: Final[str] = "ZEPHYR_SMTP_HOST"
_SMTP_PORT_ENV: Final[str] = "ZEPHYR_SMTP_PORT"
_SMTP_USER_ENV: Final[str] = "ZEPHYR_SMTP_USER"
_SMTP_PASSWORD_ENV: Final[str] = "ZEPHYR_SMTP_PASSWORD"
_ALERT_RECIPIENT_ENV: Final[str] = "ZEPHYR_ALERT_RECIPIENT"  # 告警收件人邮箱
_ALERT_SENDER_ENV: Final[str] = "ZEPHYR_ALERT_SENDER"  # 发件人邮箱（默认同 SMTP_USER）
_ALERT_TIMEOUT_ENV: Final[str] = "ZEPHYR_ALERT_TIMEOUT"  # 网络/SMTP 超时秒数

_DEFAULT_ALERT_TIMEOUT: Final[int] = 5  # webhook/SMTP 超时秒数（防阻塞调度线程）
# 触达通道的最低告警级别（含）——仅 ERROR/CRITICAL 触达人，WARN/INFO 仅写日志
_CHANNEL_THRESHOLD_LEVELS: Final[tuple[str, ...]] = (LEVEL_ERROR, LEVEL_CRITICAL)
# SMTP EHLO 本地主机名（必须 ASCII）——smtplib 默认用 socket.gethostname()，
# Windows 中文主机名（如"范清风"）含非 ASCII 字符会导致 EHLO 命令 UnicodeEncodeError，
# 邮件静默发送失败（B2 告警通道验证发现，#ARCH-CH-023，2026-07-25）。
_SMTP_LOCAL_HOSTNAME: Final[str] = "zephyr.alert.local"


class Alerter:
    """告警管理器。

    用法：
        alerter = Alerter()
        alerter.notify("kline_daily_incremental", "连接超时", level=LEVEL_ERROR)
        if alerter.check_daily_failure_rate(total=100, failed=10):
            # 失败率 10% > 5%，已告警
            pass
    """

    def __init__(self, failures_dir: str | Path | None = None):
        """初始化告警器。

        Args:
            failures_dir: 失败汇总文件目录。None 用默认 data/failures/。
        """
        self._failures_dir = Path(failures_dir) if failures_dir else _DEFAULT_FAILURES_DIR
        self._lock = threading.Lock()
        # 失败去重：task_id -> 上次写 failure 文件的 UTC 时间戳（秒）
        self._last_failure_ts: dict[str, float] = {}

    def notify(
        self,
        task_id: str,
        error: str,
        level: str = LEVEL_ERROR,
        source: str | None = None,
        extra: dict | None = None,
    ) -> bool:
        """发送告警：写日志 + 写失败汇总文件 + 触达 IM/邮件通道。

        Args:
            task_id: 任务标识
            error: 错误信息
            level: 告警级别 INFO/WARN/ERROR/CRITICAL
            source: 数据源（可选）
            extra: 附加信息（可选）

        Returns:
            是否成功写入失败汇总文件（通道发送不影响返回值，失败仅 log）。
        """
        # 1. 写日志
        msg = f"[{level}] task={task_id} source={source or 'N/A'} error={error}"
        if level == LEVEL_CRITICAL:
            log.critical(msg)
        elif level == LEVEL_ERROR:
            log.error(msg)
        elif level == LEVEL_WARN:
            log.warning(msg)
        else:
            log.info(msg)

        # 2. 写失败汇总文件（ERROR 及以上），同一 task_id 冷却期内只写一次
        if level in (LEVEL_ERROR, LEVEL_CRITICAL):
            written = self._write_failure_file(task_id, error, level, source, extra)
            # 3. 触达通道（飞书 webhook / SMTP 邮件）——仅在 failure file 实际
            #    写入后发送，与 300s 冷却对齐，防 crash-restart 循环刷屏。
            #    通道未配置或发送失败均不影响返回值（告警失败不应影响主流程）。
            if written:
                self.notify_channels(task_id, error, level, source, extra)
            return written
        return True

    def _write_failure_file(
        self,
        task_id: str,
        error: str,
        level: str,
        source: str | None,
        extra: dict | None,
    ) -> bool:
        """写失败汇总文件到 failures/ 目录。

        文件名格式：{date}_{task_id}_{timestamp}.json
        同一 task_id 在 _FAILURE_COOLDOWN_SEC 秒内重复失败只写第一个文件，
        防止 crash-restart 循环刷出海量 failure 文件（2026-07-13 曾 40 分钟刷出 3000+ 文件）。
        """
        now = now_utc()
        now_ts = now.timestamp()

        with self._lock:
            last_ts = self._last_failure_ts.get(task_id, 0.0)
            if now_ts - last_ts < _FAILURE_COOLDOWN_SEC:
                log.debug("失败汇总跳过（冷却期内）: task=%s", task_id)
                return False
            self._last_failure_ts[task_id] = now_ts

        date_str = now.strftime("%Y%m%d")
        ts_str = now.strftime("%H%M%S")
        filename = f"{date_str}_{task_id}_{ts_str}.json"

        record = {
            "task_id": task_id,
            "source": source,
            "error": error,
            "level": level,
            "timestamp": now.isoformat(timespec="seconds"),
            "extra": extra or {},
        }

        try:
            self._failures_dir.mkdir(parents=True, exist_ok=True)
            filepath = self._failures_dir / filename
            with self._lock:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
            log.info("失败汇总已写入: %s", filepath)
            return True
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("写失败汇总文件异常: %s", e)
            return False

    # ============== 告警触达通道（audit 8.3，#ARCH-DATA-PIPELINE-001）==============
    # 密钥走 .env（禁止入库）；未配置的通道静默跳过；发送失败 log 后吞掉。

    def notify_channels(
        self,
        task_id: str,
        error: str,
        level: str,
        source: str | None,
        extra: dict | None,
    ) -> None:
        """将告警分发到已配置的触达通道（飞书 webhook / SMTP 邮件）。

        通道未配置时静默跳过；网络异常 log 后吞掉（不抛异常）。
        仅在 failure file 实际写入后由 notify() 调用（与 300s 冷却对齐）。
        """
        if level not in _CHANNEL_THRESHOLD_LEVELS:
            return  # WARN/INFO 不触达人
        text = self.format_alert_text(task_id, error, level, source, extra)
        self.send_feishu_webhook(text)
        self.send_email_smtp(task_id, level, text)

    def _notify_channels(
        self,
        task_id: str,
        error: str,
        level: str,
        source: str | None,
        extra: dict | None,
    ) -> None:
        """[已废弃] 使用 notify_channels；本方法为向后兼容的瘦封装。"""
        return self.notify_channels(task_id, error, level, source, extra)

    @staticmethod
    def format_alert_text(
        task_id: str,
        error: str,
        level: str,
        source: str | None,
        extra: dict | None,
    ) -> str:
        """格式化告警正文（飞书/邮件通用）。"""
        now = now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")
        lines = [
            "[ZephyrAlpha 告警]",
            f"级别: {level}",
            f"任务: {task_id}",
            f"数据源: {source or 'N/A'}",
            f"错误: {error}",
            f"时间: {now}",
        ]
        if extra:
            lines.append(f"附加: {json.dumps(extra, ensure_ascii=False)}")
        return "\n".join(lines)

    @staticmethod
    def _format_alert_text(
        task_id: str,
        error: str,
        level: str,
        source: str | None,
        extra: dict | None,
    ) -> str:
        """[已废弃] 使用 format_alert_text；本方法为向后兼容的瘦封装。"""
        return Alerter.format_alert_text(task_id, error, level, source, extra)

    def send_feishu_webhook(self, text: str) -> bool:
        """发送飞书机器人 webhook（未配置则跳过，发送失败 log 后吞掉）。

        飞书自定义机器人 API: POST {webhook_url}
        Body: {"msg_type": "text", "content": {"text": "<message>"}}
        """
        webhook = get_secret_or_default(_FEISHU_WEBHOOK_ENV, "")
        if not webhook:
            return False  # 未配置，静默跳过
        timeout = self.alert_timeout()
        payload = json.dumps(
            {"msg_type": "text", "content": {"text": text}},
            ensure_ascii=False,
        ).encode("utf-8")
        req = urllib.request.Request(
            webhook,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status != 200:
                    log.warning("飞书 webhook 响应非 200: %s", resp.status)
                    return False
            log.info("飞书 webhook 告警已发送")
            return True
        except Exception as e:  # noqa: BLE001 — 告警通道失败不应影响主流程
            log.error("飞书 webhook 发送异常: %s", e)
            return False

    def _send_feishu_webhook(self, text: str) -> bool:
        """[已废弃] 使用 send_feishu_webhook；本方法为向后兼容的瘦封装。"""
        return self.send_feishu_webhook(text)

    def send_email_smtp(self, task_id: str, level: str, body: str) -> bool:
        """发送 SMTP 告警邮件（未配置则跳过，发送失败 log 后吞掉）。

        配置项（均走 .env）：
          ZEPHYR_SMTP_HOST / PORT / USER / PASSWORD
          ZEPHYR_ALERT_RECIPIENT（收件人）/ ZEPHYR_ALERT_SENDER（发件人，默认=USER）
        """
        host = get_secret_or_default(_SMTP_HOST_ENV, "")
        if not host:
            return False  # 未配置，静默跳过
        user = get_secret_or_default(_SMTP_USER_ENV, "")
        password = get_secret_or_default(_SMTP_PASSWORD_ENV, "")
        recipient = get_secret_or_default(_ALERT_RECIPIENT_ENV, "")
        if not user or not recipient:
            log.warning("SMTP 已配置 host 但缺 user/recipient，跳过邮件告警")
            return False
        sender = get_secret_or_default(_ALERT_SENDER_ENV, user)
        port = int(get_secret_or_default(_SMTP_PORT_ENV, "587"))
        timeout = self.alert_timeout()
        subject = f"[ZephyrAlpha 告警] {level} - {task_id}"
        msg = MIMEText(body, "plain", "utf-8")
        # Subject 含中文，须 RFC 2047 编码（=?utf-8?b?...?=），否则 msg.as_string()
        # 产生非 ASCII 头，smtp.data() 的 ASCII 编码会失败（B2 验证发现，#ARCH-CH-023）。
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = sender
        msg["To"] = recipient
        try:
            # local_hostname 必须显式传 ASCII 值：smtplib 默认用 socket.gethostname()，
            # Windows 中文主机名会导致 EHLO 命令 UnicodeEncodeError（B2 验证发现，#ARCH-CH-023）。
            with smtplib.SMTP(host, port, local_hostname=_SMTP_LOCAL_HOSTNAME, timeout=timeout) as smtp:
                smtp.starttls()
                if password:
                    smtp.login(user, password)
                smtp.sendmail(sender, [recipient], msg.as_string())
            log.info("SMTP 告警邮件已发送 -> %s", recipient)
            return True
        except Exception as e:  # noqa: BLE001 — 告警通道失败不应影响主流程
            log.error("SMTP 邮件发送异常: %s", e)
            return False

    def _send_email_smtp(self, task_id: str, level: str, body: str) -> bool:
        """[已废弃] 使用 send_email_smtp；本方法为向后兼容的瘦封装。"""
        return self.send_email_smtp(task_id, level, body)

    @staticmethod
    def alert_timeout() -> int:
        """读取告警网络超时配置（env 可覆盖，默认 5s）。"""
        try:
            return int(get_secret_or_default(_ALERT_TIMEOUT_ENV, str(_DEFAULT_ALERT_TIMEOUT)))
        except ValueError:
            return _DEFAULT_ALERT_TIMEOUT

    @staticmethod
    def _alert_timeout() -> int:
        """[已废弃] 使用 alert_timeout；本方法为向后兼容的瘦封装。"""
        return Alerter.alert_timeout()

    # ============== 告警条件检查 ==============

    def check_daily_failure_rate(self, total: int, failed: int) -> bool:
        """检查单日失败率是否超阈值（>5%）。

        Args:
            total: 当日总任务数
            failed: 当日失败任务数

        Returns:
            True 表示失败率超阈值，已告警。
        """
        if total <= 0:
            return False
        rate = failed / total
        if rate > 0.05:
            self.notify(
                "_daily_summary",
                f"单日失败率 {rate:.1%} ({failed}/{total}) 超过 5% 阈值",
                level=LEVEL_WARN,
            )
            return True
        return False

    def check_consecutive_failures(
        self,
        task_id: str,
        failure_days: int,
        threshold: int = 3,
    ) -> bool:
        """检查连续失败天数是否超阈值（默认3天）。

        Args:
            task_id: 任务标识
            failure_days: 已连续失败天数
            threshold: 阈值（默认3）

        Returns:
            True 表示连续失败超阈值，已告警。
        """
        if failure_days >= threshold:
            self.notify(
                task_id,
                f"连续 {failure_days} 天失败（阈值 {threshold}），需人工介入",
                level=LEVEL_CRITICAL,
            )
            return True
        return False

    # ============== 查询 ==============

    def list_failure_files(self, date: str | None = None) -> list[Path]:
        """列出失败汇总文件。

        Args:
            date: 过滤日期（YYYYMMDD），None 列全部

        Returns:
            文件路径列表（按文件名排序）。
        """
        if not self._failures_dir.exists():
            return []
        files = sorted(self._failures_dir.glob("*.json"))
        if date:
            files = [f for f in files if f.name.startswith(date)]
        return files

    def read_failure_file(self, filepath: str | Path) -> dict | None:
        """读取失败汇总文件。"""
        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("读取失败汇总文件异常: %s", e)
            return None
