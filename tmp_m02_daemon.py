"""检测真正的常驻服务（permanent system）特征"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

_STARTUP_RE = re.compile(r"^#\s*\[STARTUP\]\s*(\S+)", re.MULTILINE)
_TTL_RE = re.compile(r"^#\s*\[TTL\]\s*(\S+)", re.MULTILINE)

# 常驻服务特征模式
DAEMON_PATTERNS = [
    r"\bwhile\s+True\s*:",  # while True 循环
    r"\basyncio\.run\s*\(",  # asyncio 入口
    r"\bsignal\.signal\s*\(",  # 信号处理（守护进程）
    r"\bdaemon\s*=\s*True",  # 守护线程
    r"\bAPScheduler",  # APScheduler
    r"\bschedule\.every",  # schedule 库
    r"\bthreading\.Thread\s*\([^)]*daemon",  # 守护线程
    r"\bTimer\s*\(",  # threading.Timer
    r"\bBackgroundScheduler",  # APScheduler Background
    r"\bBlockingScheduler",  # APScheduler Blocking
    r"\bloop\.run_forever",  # asyncio 事件循环
    r"\basyncio\.get_event_loop",  # asyncio 事件循环
    r"\bcrontab",  # cron
    r"\bsubprocess\.Popen\s*\([^)]*daemon",  # 守护子进程
]
DAEMON_RE = re.compile("|".join(DAEMON_PATTERNS))

EXCLUDE = {".git", ".aidrafts", "__pycache__", "node_modules", ".venv", "venv", "build", "dist", "_archive", "tests"}

# 扫描 src/zephyr/ 和 scripts/governance/
scan_dirs = [
    REPO_ROOT / "src" / "zephyr",
    REPO_ROOT / "scripts" / "governance",
]

print("=== 含常驻服务特征的 manual+permanent 文件 ===")
real_daemon_violations = []
for scan_dir in scan_dirs:
    if not scan_dir.exists():
        continue
    for fp in scan_dir.rglob("*.py"):
        if any(ex in fp.parts for ex in EXCLUDE):
            continue
        try:
            source = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        sm = _STARTUP_RE.search(source)
        tm = _TTL_RE.search(source)
        if not sm or not tm:
            continue
        startup = sm.group(1).strip()
        ttl = tm.group(1).strip()
        if startup.lower() != "manual" or ttl.lower() != "permanent":
            continue
        # 检查是否含常驻特征
        if DAEMON_RE.search(source):
            try:
                rel = str(fp.relative_to(REPO_ROOT)).replace("\\", "/")
            except ValueError:
                rel = str(fp)
            # 找出匹配的特征
            matched = []
            for pat in DAEMON_PATTERNS:
                if re.search(pat, source):
                    matched.append(pat[:30])
            real_daemon_violations.append((rel, matched))

print(f"真正的常驻服务违规数: {len(real_daemon_violations)}")
for rel, matched in real_daemon_violations:
    print(f"  {rel}")
    print(f"    特征: {matched[:3]}")
