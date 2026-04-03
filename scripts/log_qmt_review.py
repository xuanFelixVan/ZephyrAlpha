#!/usr/bin/env python3
"""
QMT数据接口评审日志记录脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitoring_logger import MonitoringLogger, ReviewLog
from datetime import datetime

def log_qmt_review():
    """记录QMT数据接口评审日志"""
    
    logger = MonitoringLogger()
    
    review_log = ReviewLog(
        review_id="REVIEW_QMT_DATA_001",
        start_time="2026-04-02T02:30:00Z",
        end_time="2026-04-02T03:00:00Z",
        file_path="docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md",
        agent_name="spec-approver",
        operation="review_technical_spec",
        tools_used=[
            "run_all_assessments.py",
            "technical_feasibility_assessor.py",
            "risk_analyzer.py",
            "implementation_complexity_calculator.py"
        ],
        tool_execution_times={
            "run_all_assessments.py": 0.55,
            "technical_feasibility_assessor.py": 0.18,
            "risk_analyzer.py": 0.18,
            "implementation_complexity_calculator.py": 0.19
        },
        results={
            "technical_feasibility_score": 18.3,
            "risk_score": 1.7,
            "implementation_complexity_score": 53.0,
            "overall_score": 54.5,
            "review_conclusion": "有条件批准",
            "p0_risks": 0,
            "p1_risks": 1,
            "p2_risks": 0,
            "p3_risks": 7,
            "architecture_compliance": 100.0,
            "interface_completeness": 93.0,
            "data_model_rationality": 93.0,
            "test_strategy_completeness": 88.0
        },
        success=True
    )
    
    logger.log_review(review_log)
    
    print(f"评审日志已记录:")
    print(f"  评审ID: {review_log.review_id}")
    print(f"  评审时长: {review_log.duration_seconds:.1f}秒")
    print(f"  综合评分: {review_log.results['overall_score']}/100")
    print(f"  评审结论: {review_log.results['review_conclusion']}")
    print(f"  日志文件: data/monitoring/review_logs.jsonl")

if __name__ == "__main__":
    log_qmt_review()
