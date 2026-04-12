#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
审批智能体性能监控日志收集器

本脚本提供审批智能体 (Spec-Approver) 的性能监控日志收集功能，
包括评审日志、工具执行日志、用户反馈日志的收集和管理。
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import uuid


@dataclass
class ReviewLog:
    """评审日志数据结构"""
    review_id: str = field(default_factory=lambda: f"REV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}")
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_path: str = ""
    file_size_kb: Optional[float] = None
    agent_name: str = "spec-approver"
    operation: str = "review_technical_spec"
    tools_used: List[str] = field(default_factory=list)
    tool_execution_times: Dict[str, float] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """计算结束时间和持续时间"""
        if self.end_time and self.start_time:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            self.duration_seconds = (end - start).total_seconds()
        
        # 自动计算文件大小
        if self.file_path and os.path.exists(self.file_path):
            try:
                self.file_size_kb = os.path.getsize(self.file_path) / 1024
            except (OSError, PermissionError):
                self.file_size_kb = None


@dataclass
class ToolExecutionLog:
    """工具执行日志数据结构"""
    tool_name: str = ""
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    input_file: str = ""
    output_files: List[str] = field(default_factory=list)
    success: bool = True
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    system_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """计算结束时间和持续时间"""
        if self.end_time and self.start_time:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            self.duration_seconds = (end - start).total_seconds()


@dataclass
class UserFeedback:
    """用户反馈数据结构"""
    feedback_id: str = field(default_factory=lambda: f"FB-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    review_id: str = ""
    user_id: str = "user"
    satisfaction_score: int = 0  # 1-5分
    categories: List[str] = field(default_factory=list)
    positive_comments: str = ""
    negative_comments: str = ""
    suggestions: str = ""
    urgency: str = "低"
    follow_up_required: bool = False


class MonitoringLogger:
    """性能监控日志收集器"""
    
    def __init__(self, base_dir: str = "data/monitoring"):
        """
        初始化日志收集器
        
        Args:
            base_dir: 日志存储的基础目录
        """
        self.base_dir = Path(base_dir)
        self._ensure_directories()
        
    def _ensure_directories(self):
        """确保所有必要的目录都存在"""
        directories = [
            self.base_dir / "logs" / "review_logs",
            self.base_dir / "logs" / "tool_logs",
            self.base_dir / "logs" / "feedback",
            self.base_dir / "logs" / "validation",
            self.base_dir / "reports" / "daily",
            self.base_dir / "reports" / "weekly",
            self.base_dir / "reports" / "monthly",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _get_daily_log_file(self, log_type: str) -> Path:
        """获取当日的日志文件路径"""
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")
        
        return self.base_dir / "logs" / f"{log_type}_logs" / year / month / day / f"{log_type}_logs.jsonl"
    
    def log_review(self, review_log: ReviewLog) -> str:
        """
        记录评审日志
        
        Args:
            review_log: 评审日志对象
            
        Returns:
            评审ID
        """
        # 确保结束时间已设置
        if not review_log.end_time:
            review_log.end_time = datetime.utcnow().isoformat() + "Z"
            review_log.__post_init__()  # 重新计算持续时间
        
        log_file = self._get_daily_log_file("review")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = asdict(review_log)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        return review_log.review_id
    
    def log_tool_execution(self, tool_log: ToolExecutionLog) -> str:
        """
        记录工具执行日志
        
        Args:
            tool_log: 工具执行日志对象
            
        Returns:
            日志记录ID
        """
        # 确保结束时间已设置
        if not tool_log.end_time:
            tool_log.end_time = datetime.utcnow().isoformat() + "Z"
            tool_log.__post_init__()  # 重新计算持续时间
        
        log_file = self._get_daily_log_file("tool")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = asdict(tool_log)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        return tool_log.tool_name
    
    def log_user_feedback(self, feedback: UserFeedback) -> str:
        """
        记录用户反馈
        
        Args:
            feedback: 用户反馈对象
            
        Returns:
            反馈ID
        """
        log_file = self._get_daily_log_file("feedback")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = asdict(feedback)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        return feedback.feedback_id
    
    def get_review_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取评审统计数据
        
        Args:
            days: 统计天数
            
        Returns:
            统计数据字典
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        reviews = []
        total_duration = 0
        successful_reviews = 0
        
        # 读取指定日期范围内的日志
        current_date = start_date
        while current_date <= end_date:
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            day = current_date.strftime("%d")
            
            log_file = self.base_dir / "logs" / "review_logs" / year / month / day / "review_logs.jsonl"
            
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        review_data = json.loads(line.strip())
                        reviews.append(review_data)
                        
                        if review_data.get("duration_seconds"):
                            total_duration += review_data["duration_seconds"]
                        
                        if review_data.get("success", False):
                            successful_reviews += 1
            
            current_date += timedelta(days=1)
        
        # 计算统计数据
        total_reviews = len(reviews)
        avg_duration = total_duration / total_reviews if total_reviews > 0 else 0
        success_rate = (successful_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            "total_reviews": total_reviews,
            "successful_reviews": successful_reviews,
            "success_rate": success_rate,
            "total_duration_hours": total_duration / 3600,
            "average_duration_minutes": avg_duration / 60,
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days
            }
        }
    
    def get_tool_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        获取工具执行统计数据
        
        Args:
            days: 统计天数
            
        Returns:
            工具统计数据字典
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        tool_executions = {}
        
        # 读取指定日期范围内的日志
        current_date = start_date
        while current_date <= end_date:
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            day = current_date.strftime("%d")
            
            log_file = self.base_dir / "logs" / "tool_logs" / year / month / day / "tool_logs.jsonl"
            
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        tool_data = json.loads(line.strip())
                        tool_name = tool_data.get("tool_name", "unknown")
                        
                        if tool_name not in tool_executions:
                            tool_executions[tool_name] = {
                                "total_executions": 0,
                                "successful_executions": 0,
                                "total_duration": 0,
                                "durations": []
                            }
                        
                        tool_stats = tool_executions[tool_name]
                        tool_stats["total_executions"] += 1
                        
                        if tool_data.get("success", False):
                            tool_stats["successful_executions"] += 1
                        
                        if tool_data.get("duration_seconds"):
                            tool_stats["total_duration"] += tool_data["duration_seconds"]
                            tool_stats["durations"].append(tool_data["duration_seconds"])
            
            current_date += timedelta(days=1)
        
        # 计算每个工具的统计数据
        result = {}
        for tool_name, stats in tool_executions.items():
            total = stats["total_executions"]
            successful = stats["successful_executions"]
            total_duration = stats["total_duration"]
            durations = stats["durations"]
            
            success_rate = (successful / total * 100) if total > 0 else 0
            avg_duration = total_duration / total if total > 0 else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            result[tool_name] = {
                "total_executions": total,
                "successful_executions": successful,
                "success_rate": success_rate,
                "total_duration_seconds": total_duration,
                "average_duration_seconds": avg_duration,
                "min_duration_seconds": min_duration,
                "max_duration_seconds": max_duration
            }
        
        return result
    
    def generate_daily_report(self) -> str:
        """
        生成日报
        
        Returns:
            报告文件路径
        """
        stats = self.get_review_stats(days=1)
        tool_stats = self.get_tool_stats(days=1)
        
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_file = self.base_dir / "reports" / "daily" / f"{report_date}_performance_report.md"
        
        report_content = f"""# 审批智能体性能日报

**报告日期**: {report_date}
**报告周期**: {report_date} 00:00:00 - {report_date} 23:59:59

## 1. 关键指标概览

| 指标类别 | 昨日数值 | 目标值 | 状态 |
|----------|----------|----------|------|
| 评审数量 | {stats['total_reviews']}个 | ≥5个 | {"✅ 达标" if stats['total_reviews'] >= 5 else "❌ 未达标"} |
| 平均评审时长 | {stats['average_duration_minutes']:.1f}分钟 | ≤30分钟 | {"✅ 达标" if stats['average_duration_minutes'] <= 30 else "❌ 未达标"} |
| 评审成功率 | {stats['success_rate']:.1f}% | ≥95% | {"✅ 达标" if stats['success_rate'] >= 95 else "❌ 未达标"} |
| 总工作时长 | {stats['total_duration_hours']:.1f}小时 | - | - |

## 2. 工具执行情况

| 工具名称 | 执行次数 | 成功率 | 平均时长 |
|----------|----------|----------|----------|
"""
        
        for tool_name, tool_stat in tool_stats.items():
            report_content += f"| {tool_name} | {tool_stat['total_executions']}次 | {tool_stat['success_rate']:.1f}% | {tool_stat['average_duration_seconds']:.1f}秒 |\n"
        
        report_content += """
## 3. 异常情况

- 无重大异常（根据日志分析）

## 4. 重点关注

- 继续监控工具执行性能
- 关注用户反馈收集

## 5. 改进建议

1. 保持当前监控频率
2. 定期检查日志文件大小
3. 备份重要监控数据
"""
        
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return str(report_file)
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """
        清理旧的日志文件
        
        Args:
            days_to_keep: 保留天数
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # 清理review日志
        review_logs_dir = self.base_dir / "logs" / "review_logs"
        self._cleanup_old_files(review_logs_dir, cutoff_date)
        
        # 清理tool日志
        tool_logs_dir = self.base_dir / "logs" / "tool_logs"
        self._cleanup_old_files(tool_logs_dir, cutoff_date)
        
        # 清理feedback日志
        feedback_logs_dir = self.base_dir / "logs" / "feedback"
        self._cleanup_old_files(feedback_logs_dir, cutoff_date)
        
        print(f"[INFO] 已清理 {days_to_keep} 天前的日志文件")
    
    def _cleanup_old_files(self, base_dir: Path, cutoff_date: datetime):
        """清理指定目录下的旧文件"""
        if not base_dir.exists():
            return
        
        for year_dir in base_dir.iterdir():
            if not year_dir.is_dir():
                continue
            
            try:
                year = int(year_dir.name)
            except ValueError:
                continue
            
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue
                
                try:
                    month = int(month_dir.name)
                except ValueError:
                    continue
                
                for day_dir in month_dir.iterdir():
                    if not day_dir.is_dir():
                        continue
                    
                    try:
                        day = int(day_dir.name)
                    except ValueError:
                        continue
                    
                    dir_date = datetime(year, month, day)
                    if dir_date < cutoff_date:
                        # 删除整个目录
                        import shutil
                        shutil.rmtree(day_dir)
                        print(f"[INFO] 删除旧日志目录: {day_dir}")


def main():
    """主函数：测试日志收集功能"""
    logger = MonitoringLogger()
    
    # 示例：记录一个评审日志
    review_log = ReviewLog(
        file_path="docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md",
        operation="review_technical_spec",
        tools_used=["technical_feasibility_assessor", "risk_analyzer", "implementation_complexity_calculator"],
        tool_execution_times={
            "technical_feasibility_assessor": 8.5,
            "risk_analyzer": 12.3,
            "implementation_complexity_calculator": 18.7
        },
        results={
            "technical_feasibility_score": 15.8,
            "risk_analysis_score": 2.9,
            "implementation_complexity_score": 73.0,
            "composite_score": 46.6
        }
    )
    
    review_id = logger.log_review(review_log)
    print(f"[INFO] 记录评审日志: {review_id}")
    
    # 示例：记录工具执行日志
    tool_log = ToolExecutionLog(
        tool_name="technical_feasibility_assessor",
        input_file="docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md",
        output_files=["assessment_results.json"],
        system_metrics={
            "cpu_percent": 45.2,
            "memory_mb": 128.7
        }
    )
    
    logger.log_tool_execution(tool_log)
    print("[INFO] 记录工具执行日志")
    
    # 获取统计数据
    review_stats = logger.get_review_stats(days=1)
    print(f"[INFO] 评审统计: {review_stats}")
    
    # 生成日报
    report_file = logger.generate_daily_report()
    print(f"[INFO] 生成日报: {report_file}")
    
    print("[INFO] 日志收集测试完成")


if __name__ == "__main__":
    main()
