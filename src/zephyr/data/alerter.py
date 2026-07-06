# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.alerter
# [DOMAIN] D_DATA
# [DEPENDENCIES] logging(标准库); pathlib
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 失败汇总文件写到 failures/ 目录; 告警级别 INFO/WARN/ERROR/CRITICAL; 不抛异常(所有错误log后吞掉)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] notify失败→log+不抛异常; check_*返回bool不抛异常
# [TESTS] tests/zephyr/data/test_alerter.py
# [A_module] module_id=MOD-L00-004-alerter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性）。

告警触发条件（蓝图 §6.5）：
- 任务 DEAD（重试耗尽）→ 立即告警
- 单日失败率 > 5% → 汇总告警
- 某数据源连续 3 天失败 → 升级告警
- iFind 月度配额 -4318 → 立即告警并暂停该源所有任务

告警方式：
- 日志（logging，输出到 logs/integrator.log）
- 失败汇总文件（failures/{date}_{task_id}.json）
- 钉钉/邮件（阶段3+ 扩展点，当前 NotImplementedError）

设计要点：
- 所有方法不抛异常（告警失败不应影响主流程）
- 失败汇总文件用 JSON 格式，便于 CLI 读取和重跑
- 线程安全（threading.Lock 保护文件写入）
"""
from __future__ import annotations

from typing import Final
import datetime
import json
import logging
import threading
from pathlib import Path
from typing import Optional

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

_DEFAULT_FAILURES_DIR = REPO_ROOT / "data" / "failures"

# 告警级别
LEVEL_INFO: Final[str] = "INFO"
LEVEL_WARN: Final[str] = "WARN"
LEVEL_ERROR: Final[str] = "ERROR"
LEVEL_CRITICAL: Final[str] = "CRITICAL"


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

    def notify(
        self,
        task_id: str,
        error: str,
        level: str = LEVEL_ERROR,
        source: str | None = None,
        extra: dict | None = None,
    ) -> bool:
        """发送告警：写日志 + 写失败汇总文件。

        Args:
            task_id: 任务标识
            error: 错误信息
            level: 告警级别 INFO/WARN/ERROR/CRITICAL
            source: 数据源（可选）
            extra: 附加信息（可选）

        Returns:
            是否成功写入失败汇总文件。
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

        # 2. 写失败汇总文件（ERROR 及以上）
        if level in (LEVEL_ERROR, LEVEL_CRITICAL):
            return self._write_failure_file(task_id, error, level, source, extra)
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
        """
        now = now_utc()
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
        except Exception as e:
            log.error("写失败汇总文件异常: %s", e)
            return False

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

    def check_quota_exhausted(
        self,
        source: str,
        error_code: str,
    ) -> bool:
        """检查 iFind 月度配额耗尽（-4318/-4309）。

        Args:
            source: 数据源
            error_code: 错误码

        Returns:
            True 表示配额耗尽，已告警。
        """
        quota_codes = {"-4318", "-4309"}
        if source == "ifind" and error_code in quota_codes:
            self.notify(
                "_quota_monitor",
                f"iFind 月度配额耗尽 (error_code={error_code})，暂停该源所有任务",
                level=LEVEL_CRITICAL,
                source=source,
                extra={"action": "pause_source", "error_code": error_code},
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
        except Exception as e:
            log.error("读取失败汇总文件异常: %s", e)
            return None
