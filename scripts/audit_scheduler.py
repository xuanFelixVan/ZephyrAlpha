#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
自动化审计调度系统
支持定时执行每周、每月、每季度审计
"""

import os
import sys
import json
import schedule
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class AuditScheduler:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs" / "audit"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.weekly_script = self.scripts_dir / "weekly_audit_optimized.py"
        self.monthly_script = self.scripts_dir / "monthly_audit.py"
        self.quarterly_script = self.scripts_dir / "quarterly_audit.py"
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        log_file = self.logs_dir / f"audit_scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def run_weekly_audit(self):
        self.log("开始执行每周审计...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(self.weekly_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                self.log("每周审计执行成功", "SUCCESS")
                self.log(result.stdout)
            else:
                self.log(f"每周审计执行失败: {result.stderr}", "ERROR")
        except Exception as e:
            self.log(f"每周审计执行异常: {str(e)}", "ERROR")
    
    def run_monthly_audit(self):
        self.log("开始执行每月审计...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(self.monthly_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                self.log("每月审计执行成功", "SUCCESS")
                self.log(result.stdout)
            else:
                self.log(f"每月审计执行失败: {result.stderr}", "ERROR")
        except Exception as e:
            self.log(f"每月审计执行异常: {str(e)}", "ERROR")
    
    def run_quarterly_audit(self):
        self.log("开始执行每季度审计...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(self.quarterly_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                self.log("每季度审计执行成功", "SUCCESS")
                self.log(result.stdout)
            else:
                self.log(f"每季度审计执行失败: {result.stderr}", "ERROR")
        except Exception as e:
            self.log(f"每季度审计执行异常: {str(e)}", "ERROR")
    
    def setup_schedule(self):
        schedule.every().monday.at("09:00").do(self.run_weekly_audit)
        
        schedule.every(1).month.at("10:00").do(self.run_monthly_audit)
        
        schedule.every(3).months.at("14:00").do(self.run_quarterly_audit)
        
        self.log("审计调度系统已启动")
        self.log("每周审计: 每周一 09:00")
        self.log("每月审计: 每月1日 10:00")
        self.log("每季度审计: 每季度首月1日 14:00")
    
    def run(self):
        self.setup_schedule()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                self.log("审计调度系统已停止", "INFO")
                break
            except Exception as e:
                self.log(f"调度系统异常: {str(e)}", "ERROR")
                time.sleep(60)

if __name__ == "__main__":
    scheduler = AuditScheduler()
    scheduler.run()
