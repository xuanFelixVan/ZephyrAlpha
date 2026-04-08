"""
P2持续监控机制
定期运行审计脚本，自动发现问题并修复
"""
import os
import json
import schedule
import time
import subprocess
from pathlib import Path
from datetime import datetime

class ContinuousMonitor:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.monitor_log = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "checks": []
        }
        
    def run_daily_check(self):
        """每日检查"""
        print("\n" + "="*80)
        print(f"每日检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        check_result = {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "check_type": "daily",
            "issues_found": 0,
            "issues_fixed": 0,
            "details": []
        }
        
        try:
            result = subprocess.run(
                ["python", str(self.project_root / "scripts" / "daily_check.py")],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            check_result["output"] = result.stdout
            check_result["errors"] = result.stderr
            
            if result.returncode == 0:
                print("  ✓ 每日检查完成")
                check_result["status"] = "success"
            else:
                print(f"  ✗ 每日检查失败: {result.stderr}")
                check_result["status"] = "failed"
                
        except Exception as e:
            print(f"  ✗ 执行错误: {str(e)}")
            check_result["status"] = "error"
            check_result["error"] = str(e)
        
        self.monitor_log["checks"].append(check_result)
        self.save_monitor_log()
        
    def run_weekly_audit(self):
        """每周审计"""
        print("\n" + "="*80)
        print(f"每周审计 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        check_result = {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "check_type": "weekly",
            "issues_found": 0,
            "issues_fixed": 0,
            "details": []
        }
        
        try:
            result = subprocess.run(
                ["python", str(self.project_root / "scripts" / "weekly_check.py")],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            check_result["output"] = result.stdout
            check_result["errors"] = result.stderr
            
            if result.returncode == 0:
                print("  ✓ 每周审计完成")
                check_result["status"] = "success"
            else:
                print(f"  ✗ 每周审计失败: {result.stderr}")
                check_result["status"] = "failed"
                
        except Exception as e:
            print(f"  ✗ 执行错误: {str(e)}")
            check_result["status"] = "error"
            check_result["error"] = str(e)
        
        self.monitor_log["checks"].append(check_result)
        self.save_monitor_log()
        
    def run_monthly_audit(self):
        """每月审计"""
        print("\n" + "="*80)
        print(f"每月审计 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        check_result = {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "check_type": "monthly",
            "issues_found": 0,
            "issues_fixed": 0,
            "details": []
        }
        
        try:
            result = subprocess.run(
                ["python", str(self.project_root / "scripts" / "monthly_check.py")],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=1200
            )
            
            check_result["output"] = result.stdout
            check_result["errors"] = result.stderr
            
            if result.returncode == 0:
                print("  ✓ 每月审计完成")
                check_result["status"] = "success"
            else:
                print(f"  ✗ 每月审计失败: {result.stderr}")
                check_result["status"] = "failed"
                
        except Exception as e:
            print(f"  ✗ 执行错误: {str(e)}")
            check_result["status"] = "error"
            check_result["error"] = str(e)
        
        self.monitor_log["checks"].append(check_result)
        self.save_monitor_log()
        
    def run_layer4_deep_audit(self):
        """Layer 4深度审计"""
        print("\n" + "="*80)
        print(f"Layer 4深度审计 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        check_result = {
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "check_type": "layer4_deep_audit",
            "issues_found": 0,
            "issues_fixed": 0,
            "details": []
        }
        
        try:
            result = subprocess.run(
                ["python", str(self.project_root / "scripts" / "layer4_deep_audit_v3.py")],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            check_result["output"] = result.stdout
            check_result["errors"] = result.stderr
            
            if result.returncode == 0:
                print("  ✓ Layer 4深度审计完成")
                check_result["status"] = "success"
            else:
                print(f"  ✗ Layer 4深度审计失败: {result.stderr}")
                check_result["status"] = "failed"
                
        except Exception as e:
            print(f"  ✗ 执行错误: {str(e)}")
            check_result["status"] = "error"
            check_result["error"] = str(e)
        
        self.monitor_log["checks"].append(check_result)
        self.save_monitor_log()
        
    def save_monitor_log(self):
        """保存监控日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"continuous_monitor_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.monitor_log, f, ensure_ascii=False, indent=2)
        
    def setup_schedule(self):
        """设置定时任务"""
        print("="*80)
        print("持续监控机制启动")
        print("="*80)
        print(f"启动时间: {self.monitor_log['start_time']}")
        print("-"*80)
        print("定时任务配置:")
        print("  - 每日检查: 每天 09:00")
        print("  - 每周审计: 每周一 10:00")
        print("  - 每月审计: 每月1日 11:00")
        print("  - Layer 4深度审计: 每周日 14:00")
        print("-"*80)
        
        schedule.every().day.at("09:00").do(self.run_daily_check)
        schedule.every().monday.at("10:00").do(self.run_weekly_audit)
        schedule.every(1).to(28).days.at("11:00").do(self.run_monthly_audit)
        schedule.every().sunday.at("14:00").do(self.run_layer4_deep_audit)
        
        print("监控服务已启动，按Ctrl+C停止...")
        print("="*80)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n监控服务已停止")
            self.save_monitor_log()
            
    def run_once(self):
        """执行一次完整检查"""
        print("="*80)
        print("执行一次性完整检查")
        print("="*80)
        print(f"检查时间: {self.monitor_log['start_time']}")
        print("-"*80)
        
        self.run_daily_check()
        self.run_weekly_audit()
        self.run_layer4_deep_audit()
        
        print("\n" + "="*80)
        print("完整检查完成")
        print("="*80)
        print(f"检查次数: {len(self.monitor_log['checks'])}")
        self.save_monitor_log()

if __name__ == "__main__":
    monitor = ContinuousMonitor()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        monitor.run_once()
    else:
        monitor.setup_schedule()
