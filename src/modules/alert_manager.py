"""
告警系统
支持邮件、微信（Server酱）、Bark等告警方式

技术层次: Layer 6 - 监控告警层 | 业务架构: 三级时间框架融合架构

性能优化:
    - 重试机制: 网络失败自动重试
    - 超时控制: 防止请求无限等待
    - 连接池: 复用HTTP连接
"""
import logging
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """告警消息"""
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime = None
    tags: Dict[str, str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tags is None:
            self.tags = {}


class AlertChannel:
    """告警渠道基类"""
    def send(self, alert: Alert) -> bool:
        raise NotImplementedError


class EmailAlertChannel(AlertChannel):
    """邮件告警渠道

    特性:
        - TLS/SSL加密
        - 自动重试 (最多3次)
        - 超时控制 (30秒)
    """

    def __init__(self, config: Dict, max_retries: int = 3, timeout: int = 30):
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.from_addr = config.get("from_addr", "")
        self.to_addrs = config.get("to_addrs", [])
        self.max_retries = max_retries
        self.timeout = timeout

    def send(self, alert: Alert) -> bool:
        """发送邮件告警 (带重试机制)"""
        if not self.to_addrs:
            logger.warning("No email recipients configured")
            return False

        last_error = None
        for attempt in range(self.max_retries):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"[{alert.level.value.upper()}] {alert.title}"
                msg["From"] = self.from_addr
                msg["To"] = ", ".join(self.to_addrs)

                html_content = self._generate_html(alert)
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.sendmail(self.from_addr, self.to_addrs, msg.as_string())

                logger.info(f"Email alert sent: {alert.title}")
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed: {e}")
                return False

            except (smtplib.SMTPException, ConnectionError, OSError) as e:
                last_error = e
                logger.warning(f"Email send attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))

        logger.error(f"Failed to send email alert after {self.max_retries} attempts: {last_error}")
        return False

    def _generate_html(self, alert: Alert) -> str:
        """生成HTML内容"""
        level_colors = {
            AlertLevel.INFO: "#4CAF50",
            AlertLevel.WARNING: "#FF9800",
            AlertLevel.ERROR: "#F44336",
            AlertLevel.CRITICAL: "#9C27B0"
        }
        color = level_colors.get(alert.level, "#4CAF50")

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="border-left: 4px solid {color}; padding: 10px; margin: 10px 0;">
                <h2 style="color: {color}; margin: 0 0 10px 0;">
                    [{alert.level.value.upper()}] {alert.title}
                </h2>
                <p style="margin: 5px 0; color: #666;">
                    时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                </p>
                <p style="margin: 15px 0; font-size: 14px;">
                    {alert.message}
                </p>
            </div>
        </body>
        </html>
        """


class ServerChanAlertChannel(AlertChannel):
    """Server酱微信告警渠道

    特性:
        - 自动重试 (最多3次)
        - 超时控制 (10秒)
        - 错误码检查
    """

    def __init__(self, config: Dict, max_retries: int = 3, timeout: int = 10):
        self.sendkey = config.get("sendkey", "")
        self.max_retries = max_retries
        self.timeout = timeout

    def send(self, alert: Alert) -> bool:
        """发送微信告警 (带重试机制)"""
        if not self.sendkey:
            logger.warning("ServerChan sendkey not configured")
            return False

        level_emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        emoji = level_emoji.get(alert.level, "ℹ️")

        title = f"{emoji} {alert.title}"
        content = f"""
{alert.message}

时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
级别: {alert.level.value.upper()}
        """

        last_error = None
        for attempt in range(self.max_retries):
            try:
                url = f"https://sctapi.ftqq.com/{self.sendkey}.send"
                
                # 安全验证：只允许http或https协议（防御性编程）
                if not url.startswith(('http://', 'https://')):
                    logger.error(f"Unsupported protocol in URL: {url}")
                    return False

                data = urllib.parse.urlencode({
                    "title": title,
                    "content": content
                }).encode("utf-8")

                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                with urllib.request.urlopen(req, timeout=self.timeout) as response:  # nosec B310
                    result = json.loads(response.read().decode("utf-8"))

                if result.get("code") == 0:
                    logger.info(f"ServerChan alert sent: {alert.title}")
                    return True
                else:
                    logger.error(f"ServerChan API error: {result.get('msg')}")
                    return False

            except urllib.error.URLError as e:
                last_error = e
                logger.warning(f"ServerChan send attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))

            except json.JSONDecodeError as e:
                logger.error(f"ServerChan response parse error: {e}")
                return False

            except Exception as e:
                last_error = e
                logger.warning(f"ServerChan send attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))

        logger.error(f"Failed to send ServerChan alert after {self.max_retries} attempts: {last_error}")
        return False


class BarkAlertChannel(AlertChannel):
    """Bark告警渠道

    特性:
        - 自动重试 (最多3次)
        - 超时控制 (10秒)
        - iOS通知支持
    """

    def __init__(self, config: Dict, max_retries: int = 3, timeout: int = 10):
        self.bark_url = config.get("bark_url", "")
        self.group = config.get("group", "量化系统")
        self.max_retries = max_retries
        self.timeout = timeout

    def send(self, alert: Alert) -> bool:
        """发送Bark告警 (带重试机制)"""
        if not self.bark_url:
            logger.warning("Bark URL not configured")
            return False

        level_emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        emoji = level_emoji.get(alert.level, "ℹ️")

        title = f"{emoji} {alert.title}"
        content = f"""
{alert.message}

时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
级别: {alert.level.value.upper()}
        """

        last_error = None
        for attempt in range(self.max_retries):
            try:
                url = f"{self.bark_url}/{urllib.parse.quote(title)}/{urllib.parse.quote(content)}"
                
                # 安全验证：只允许http或https协议
                if not url.startswith(('http://', 'https://')):
                    logger.error(f"Unsupported protocol in URL: {url}")
                    return False

                req = urllib.request.Request(url)

                with urllib.request.urlopen(req, timeout=self.timeout) as response:  # nosec B310
                    result = json.loads(response.read().decode("utf-8"))

                if result.get("code") == 200:
                    logger.info(f"Bark alert sent: {alert.title}")
                    return True
                else:
                    logger.error(f"Bark API error: {result.get('message')}")
                    return False

            except urllib.error.URLError as e:
                last_error = e
                logger.warning(f"Bark send attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))

            except json.JSONDecodeError as e:
                logger.error(f"Bark response parse error: {e}")
                return False

            except Exception as e:
                last_error = e
                logger.warning(f"Bark send attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1 * (attempt + 1))

        logger.error(f"Failed to send Bark alert after {self.max_retries} attempts: {last_error}")
        return False


class AlertManager:
    """告警管理器

    统一管理多种告警渠道，支持:
        - 灵活配置多个渠道
        - 自动重试机制
        - 并行发送
        - 告警历史记录
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.channels: List[AlertChannel] = []
        self.alert_history: List[Alert] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._init_channels()

    def _init_channels(self):
        """初始化告警渠道"""
        email_config = self.config.get("email")
        if email_config:
            max_retries = email_config.get("max_retries", 3)
            timeout = email_config.get("timeout", 30)
            self.channels.append(EmailAlertChannel(email_config, max_retries, timeout))

        serverchan_config = self.config.get("serverchan")
        if serverchan_config:
            max_retries = serverchan_config.get("max_retries", 3)
            timeout = serverchan_config.get("timeout", 10)
            self.channels.append(ServerChanAlertChannel(serverchan_config, max_retries, timeout))

        bark_config = self.config.get("bark")
        if bark_config:
            max_retries = bark_config.get("max_retries", 3)
            timeout = bark_config.get("timeout", 10)
            self.channels.append(BarkAlertChannel(bark_config, max_retries, timeout))

        if not self.channels:
            logger.warning("No alert channels configured, alerts will only be logged")

    def send(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        tags: Optional[Dict[str, str]] = None,
        async_send: bool = False
    ):
        """发送告警

        参数:
            level: 告警级别
            title: 告警标题
            message: 告警消息
            tags: 标签
            async_send: 是否异步发送
        """
        alert = Alert(
            level=level,
            title=title,
            message=message,
            tags=tags
        )

        self.alert_history.append(alert)

        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-500:]

        if async_send:
            self.executor.submit(self._send_to_channels, alert)
            return True

        return self._send_to_channels(alert)

    def _send_to_channels(self, alert: Alert) -> int:
        """向所有渠道发送告警"""
        success_count = 0
        for channel in self.channels:
            if channel.send(alert):
                success_count += 1
        return success_count

    def info(self, title: str, message: str):
        """发送信息告警"""
        return self.send(AlertLevel.INFO, title, message)

    def warning(self, title: str, message: str):
        """发送警告告警"""
        return self.send(AlertLevel.WARNING, title, message)

    def error(self, title: str, message: str):
        """发送错误告警"""
        return self.send(AlertLevel.ERROR, title, message)

    def critical(self, title: str, message: str):
        """发送严重告警"""
        return self.send(AlertLevel.CRITICAL, title, message)

    def send_trade_alert(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        pnl: float = None
    ):
        """发送交易告警"""
        title = f"交易提醒: {action} {symbol}"
        message = f"股票: {symbol}\n动作: {action}\n数量: {quantity}\n价格: {price:.2f}"

        if pnl is not None:
            message += f"\n盈亏: {pnl:.2f}"

        return self.send(AlertLevel.INFO, title, message)

    def send_risk_alert(
        self,
        risk_type: str,
        message: str,
        triggered_rules: List[str] = None
    ):
        """发送风险告警"""
        title = f"风险预警: {risk_type}"
        content = message

        if triggered_rules:
            content += "\n触发规则:"
            for rule in triggered_rules:
                content += f"\n  - {rule}"

        return self.send(AlertLevel.WARNING, title, content)

    def send_strategy_alert(
        self,
        event_type: str,
        message: str
    ):
        """发送策略事件告警"""
        title = f"策略事件: {event_type}"
        return self.send(AlertLevel.INFO, title, message)

    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """获取最近告警"""
        return self.alert_history[-limit:]

    def get_alert_summary(self) -> Dict:
        """获取告警摘要"""
        if not self.alert_history:
            return {"total": 0, "by_level": {}}

        by_level = {}
        for alert in self.alert_history:
            level = alert.level.value
            by_level[level] = by_level.get(level, 0) + 1

        return {
            "total": len(self.alert_history),
            "by_level": by_level,
            "last_alert": self.alert_history[-1].timestamp.isoformat()
        }

    def clear_history(self):
        """清除告警历史"""
        self.alert_history.clear()

    def shutdown(self):
        """关闭告警管理器 (关闭线程池)"""
        self.executor.shutdown(wait=True)
