"""
TTL Cleanup Engine — 派生文件 7 天 TTL 清理引擎 (M-20)
职责：
  - 扫描 capacity_metrics / error_budget / token_budget_usage 过期数据
  - 清理前 PRAGMA wal_checkpoint(TRUNCATE)（关联盲点 #62）
  - 清理 .audit_cache/ 临时文件

触发方式：
  - 定时任务（cron/调度器）
  - WAL checkpoint 前自动清理
"""
import os
import shutil
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Optional


class TTLCleanupEngine:
    """
    TTL 派生文件清理引擎 (M-20)
    """

    DEFAULT_TTL_DAYS = 7
    AUDIT_CACHE_DIR = ".audit_cache"

    def __init__(self, db_path: Optional[str] = None, ttl_days: int = DEFAULT_TTL_DAYS):
        self.db_path = db_path or self._default_db_path()
        self.ttl_days = ttl_days

    def _default_db_path(self) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "capacity.db"
        )

    def cleanup_database(self) -> dict:
        result = {"capacity_metrics": 0, "token_budget_usage": 0, "error_budget": 0}

        try:
            conn = sqlite3.connect(self.db_path)

            # WAL checkpoint before cleanup (#62)
            try:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except sqlite3.OperationalError:
                pass

            cutoff = f"datetime('now', '-{self.ttl_days} days')"

            cur = conn.execute(f"DELETE FROM capacity_metrics WHERE ts < {cutoff}")
            result["capacity_metrics"] = cur.rowcount

            cur = conn.execute(f"DELETE FROM token_budget_usage WHERE ts < {cutoff}")
            result["token_budget_usage"] = cur.rowcount

            conn.commit()
            conn.execute("PRAGMA optimize")
            conn.close()
        except Exception:
            pass

        return result

    def cleanup_audit_cache(self, project_root: Optional[str] = None) -> int:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        cache_dir = os.path.join(project_root, self.AUDIT_CACHE_DIR)
        if not os.path.exists(cache_dir):
            return 0

        cutoff_time = datetime.now() - timedelta(days=self.ttl_days)
        removed = 0

        for root, dirs, files in os.walk(cache_dir):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if mtime < cutoff_time:
                        os.remove(fpath)
                        removed += 1
                except OSError:
                    pass

            # Remove empty dirs
            for d in list(dirs):
                dpath = os.path.join(root, d)
                try:
                    if not os.listdir(dpath):
                        os.rmdir(dpath)
                except OSError:
                    pass

        return removed

    def run(self, project_root: Optional[str] = None) -> dict:
        db_result = self.cleanup_database()
        cache_removed = self.cleanup_audit_cache(project_root)
        return {
            "database_cleanup": db_result,
            "audit_cache_removed": cache_removed,
            "ttl_days": self.ttl_days,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


_engine: Optional[TTLCleanupEngine] = None


def get_cleanup_engine(ttl_days: int = 7) -> TTLCleanupEngine:
    global _engine
    if _engine is None:
        _engine = TTLCleanupEngine(ttl_days=ttl_days)
    return _engine
