import os
import shutil
import time
from datetime import datetime, timedelta
import re

# 配置
AUDIT_DIR = r"d:\ZephyrAlpha\docs\09_AUDIT"
STATE_DIR = os.path.join(AUDIT_DIR, "STATE")
REPORTS_DIR = os.path.join(AUDIT_DIR, "REPORTS")

# TTL 配置 (天)
TTL_CONFIG = {
    "DAILY": 30,
    "OVERNIGHT": 14,
    "SCAN_REPORTS": 90,
    "DEFAULT": 90
}

# 二级目录结构
REPORTS_SUBDIRS = ["GOVERNANCE", "QUALITY", "COMPLIANCE", "INCIDENT", "PERIODIC", "ARCHIVE"]
STATE_SUBDIRS = ["DAILY", "OVERNIGHT", "MILESTONE"]

def get_file_age_days(file_path):
    return (time.time() - os.path.getmtime(file_path)) / (24 * 3600)

def ensure_subdirs(base_dir, subdirs):
    for subdir in subdirs:
        path = os.path.join(base_dir, subdir)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")

def classify_and_cleanup_state():
    print("Starting STATE/ cleanup and classification...")
    ensure_subdirs(STATE_DIR, STATE_SUBDIRS)

    for item in os.listdir(STATE_DIR):
        item_path = os.path.join(STATE_DIR, item)
        if os.path.isdir(item_path) and item in STATE_SUBDIRS:
            continue

        if os.path.isfile(item_path):
            age = get_file_age_days(item_path)

            # 1. 分类
            target_subdir = None
            ttl = TTL_CONFIG["DEFAULT"]

            if "overnight" in item.lower():
                target_subdir = "OVERNIGHT"
                ttl = TTL_CONFIG["OVERNIGHT"]
            elif item in ("INDEX_HEALTH_ORPHAN_LATEST.json", "index-health-orphan-latest.md",
                          "SENTINEL_L1_SCAN_LATEST.json", "SENTINEL_L1_SCAN_LATEST.md"):
                # LATEST 文件：覆盖写入模式，永不过期、永不移动
                ttl = 9999
            elif re.search(r"INDEX_HEALTH_ORPHAN_\d{8}", item) or re.search(r"index-health-orphan-\d{8}", item):
                target_subdir = "DAILY"
                ttl = TTL_CONFIG["DAILY"]
            elif "milestone" in item.lower() or "baseline" in item.lower():
                target_subdir = "MILESTONE"
                ttl = 9999 # 永久保留

            # 2. 清理或移动
            if age > ttl and ttl != 9999:
                print(f"Deleting expired STATE file: {item} (Age: {age:.1f} days, TTL: {ttl} days)")
                os.remove(item_path)
            elif target_subdir:
                dest_path = os.path.join(STATE_DIR, target_subdir, item)
                print(f"Moving STATE file: {item} -> {target_subdir}")
                shutil.move(item_path, dest_path)

def classify_and_cleanup_reports():
    print("Starting REPORTS/ cleanup and classification...")
    ensure_subdirs(REPORTS_DIR, REPORTS_SUBDIRS)

    for item in os.listdir(REPORTS_DIR):
        item_path = os.path.join(REPORTS_DIR, item)
        if os.path.isdir(item_path) and item in REPORTS_SUBDIRS:
            continue

        if os.path.isfile(item_path):
            age = get_file_age_days(item_path)

            # 1. 分类
            target_subdir = "ARCHIVE"

            if "sentinel" in item.lower():
                target_subdir = "GOVERNANCE"
            elif any(k in item.lower() for k in ["quality", "link", "duplicate", "structure"]):
                target_subdir = "QUALITY"
            elif any(k in item.lower() for k in ["compliance", "naming", "metadata"]):
                target_subdir = "COMPLIANCE"
            elif any(k in item.lower() for k in ["fix", "encoding", "incident"]):
                target_subdir = "INCIDENT"
            elif any(k in item.lower() for k in ["weekly", "monthly", "quarterly", "annual"]):
                target_subdir = "PERIODIC"

            # 2. 移动
            dest_path = os.path.join(REPORTS_DIR, target_subdir, item)
            print(f"Moving REPORT file: {item} -> {target_subdir}")
            shutil.move(item_path, dest_path)

def cleanup_session_logs():
    """清理 SESSION_LOGS/ 下超过 30 天 TTL 的 Session Log。
    注意：删除前先检查文件是否含关键决策，提醒操作者手动升级后再删。
    """
    session_logs_dir = os.path.join(STATE_DIR, "SESSION_LOGS")
    if not os.path.exists(session_logs_dir):
        return

    print("Checking SESSION_LOGS/ for expired files (TTL: 30 days)...")
    ttl = 30
    expired = []

    for item in os.listdir(session_logs_dir):
        item_path = os.path.join(session_logs_dir, item)
        if not os.path.isfile(item_path):
            continue
        age = get_file_age_days(item_path)
        if age > ttl:
            expired.append((item, item_path, age))

    if not expired:
        print("SESSION_LOGS/: No expired files found.")
        return

    print(f"\nFound {len(expired)} expired Session Log(s):")
    for name, path, age in expired:
        print(f"  - {name} (Age: {age:.1f} days)")

    print("\nACTION REQUIRED: Before deleting, check '## 关键决策' in each file.")
    print("If critical decisions exist, upgrade them to TECH_DECISION_RECORDS.md or lessons-learned-register.md first.")
    print("To delete, run this script with --force-session-logs flag.")


if __name__ == "__main__":
    import sys
    classify_and_cleanup_state()
    classify_and_cleanup_reports()
    cleanup_session_logs()
    print("Cleanup and classification complete.")
