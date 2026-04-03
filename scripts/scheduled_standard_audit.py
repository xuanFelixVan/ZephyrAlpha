#!/usr/bin/env python3
"""
标准审计脚本
功能: 每月执行，检查文档分类、命名规范、索引完整性
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from document_auditor import DocumentAuditor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/standard_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_standard_audit():
    """执行标准审计"""
    try:
        logger.info("开始标准审计...")
        
        auditor = DocumentAuditor(project_root='.')
        results = auditor.run_full_audit()
        
        timestamp = datetime.now().strftime('%Y%m%d')
        output_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/monthly_{timestamp}.json'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"标准审计完成，报告已保存到: {output_file}")
        
        generate_summary_report(results, timestamp)
        
        return 0
        
    except Exception as e:
        logger.error(f"标准审计失败: {str(e)}")
        return 1

def generate_summary_report(results, timestamp):
    """生成审计摘要报告"""
    summary_file = f'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/monthly_summary_{timestamp}.md'
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# 月度文档审计摘要报告\n\n")
        f.write(f"**审计时间**: {results['summary']['scan_time']}\n\n")
        f.write(f"## 审计概要\n\n")
        f.write(f"- 扫描文件数: {results['summary']['scanned_files']}\n")
        f.write(f"- 问题总数: {results['summary']['total_issues']}\n\n")
        
        if results['summary']['issues_by_severity']:
            f.write(f"## 问题分布\n\n")
            for severity, count in results['summary']['issues_by_severity'].items():
                f.write(f"- {severity}: {count}个\n")
        
        if results['summary']['issues_by_type']:
            f.write(f"\n## 问题类型\n\n")
            for issue_type, count in results['summary']['issues_by_type'].items():
                f.write(f"- {issue_type}: {count}个\n")

if __name__ == '__main__':
    sys.exit(run_standard_audit())
